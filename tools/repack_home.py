#!/usr/bin/env python3
"""Replace only Home in a verified ISO, preserving all other system entries.

Linux root, erofs-utils, e2fsprogs and xorriso required. Temporary data is kept
in a dedicated temporary directory and mounts are released before cleanup.
This repacks an existing platform; it does not compile Android.
"""
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

HOME = 'system/product/app/StremioBoxHome/StremioBoxHome.apk'


def sha(path):
    checksum = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024**2), b''):
            checksum.update(data)
    return checksum.hexdigest()


def run(*args):
    result = subprocess.run([str(arg) for arg in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def inventory(mount):
    entries = {}
    for directory, dirs, files in os.walk(mount, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            info = path.lstat()
            entry = {'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid, 'gid': info.st_gid,
                     'xattrs': {key: os.getxattr(path, key, follow_symlinks=False).hex()
                                for key in os.listxattr(path, follow_symlinks=False)}}
            if path.is_symlink():
                entry.update(kind='symlink', target=os.readlink(path))
            elif path.is_file():
                entry.update(kind='file', bytes=info.st_size, sha256=sha(path))
            elif path.is_dir():
                entry.update(kind='dir')
            else:
                entry.update(kind='special', device=info.st_rdev)
            entries[path.relative_to(mount).as_posix()] = entry
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-iso', type=Path, required=True)
    parser.add_argument('--base-record', type=Path, required=True)
    parser.add_argument('--home-apk', type=Path, required=True)
    parser.add_argument('--home-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--revision', type=int, default=6)
    args = parser.parse_args()
    if os.name != 'posix' or os.geteuid() != 0:
        parser.error('Run on a Linux build host as root, with loop-mount support')
    if args.output.exists():
        parser.error('Output already exists; never overwrite a released image')
    record = json.loads(args.base_record.read_text(encoding='utf-8'))
    expected_iso = record['files'][args.base_iso.name]
    assert args.base_iso.stat().st_size == expected_iso['bytes']
    assert sha(args.base_iso) == expected_iso['sha256'], 'Base ISO hash mismatch'
    assert sha(args.home_apk) == args.home_sha256, 'Home APK hash mismatch'
    assert shutil.disk_usage(tempfile.gettempdir()).free > 24 * 1024**3
    assert shutil.disk_usage(args.output.parent).free > 4 * 1024**3
    with tempfile.TemporaryDirectory(prefix='stremiobox-home-repack-') as temporary:
        work = Path(temporary)
        mount = work / 'system'
        mount.mkdir()
        mounted = False
        print('Extracting the verified base system...', flush=True)
        outer = work / 'base-system.efs'
        run('xorriso', '-osirrox', 'on', '-indev', args.base_iso, '-extract', '/system.efs', outer)
        assert sha(outer) == record['files']['system.efs']['sha256']
        container = work / 'container'
        run('fsck.erofs', '--extract=' + str(container), outer)
        inner = container / 'system.img'
        assert sha(inner) == record['packaged_metadata']['inner_system_image_sha256']
        run('/usr/sbin/e2fsck', '-f', '-n', inner)
        try:
            run('mount', '-o', 'loop,ro,noload', inner, mount)
            mounted = True
            print('Inventorying every system entry before the Home change...', flush=True)
            before = inventory(mount)
            assert HOME in before and before[HOME]['kind'] == 'file'
            run('umount', mount)
            mounted = False
            run('mount', '-o', 'loop,rw', inner, mount)
            mounted = True
            target = mount / HOME
            assert not target.is_symlink() and target.resolve().is_relative_to(mount)
            shutil.copyfile(args.home_apk, target)
            after = inventory(mount)
            changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
            assert changed == {HOME}, sorted(changed)
            for key in ('mode', 'uid', 'gid', 'xattrs', 'kind'):
                assert before[HOME][key] == after[HOME][key], key
            assert after[HOME]['sha256'] == args.home_sha256
            print('Verified: only Home APK content changed; every other entry preserved.', flush=True)
            os.sync()
            run('umount', mount)
            mounted = False
            run('/usr/sbin/e2fsck', '-f', '-n', inner)
            new_outer = work / 'system.efs'
            print('Compressing the English Home system...', flush=True)
            run('mkfs.erofs', '-zlz4hc,9', '--all-root', new_outer, container)
            run('fsck.erofs', new_outer)
            # Verify the compressed result's actual file inventory, not merely
            # the uncompressed working tree or a list of expected native files.
            check = work / 'check'
            run('fsck.erofs', '--extract=' + str(check), new_outer)
            assert sha(check / 'system.img') == sha(inner)
            run('/usr/sbin/e2fsck', '-f', '-n', check / 'system.img')
            run('mount', '-o', 'loop,ro,noload', check / 'system.img', mount)
            mounted = True
            assert inventory(mount) == after, 'Compressed system inventory differs'
            run('umount', mount)
            mounted = False
            new_iso = work / args.output.name
            run('xorriso', '-indev', args.base_iso, '-outdev', new_iso, '-map', new_outer,
                '/system.efs', '-boot_image', 'any', 'replay', '-hfsplus', 'off', '-commit')
            # ISO boot structures are replayed; inspect the resulting image.
            boot = run('xorriso', '-indev', new_iso, '-report_el_torito', 'plain', '-report_system_area', 'plain')
            assert all(value in boot for value in ('BIOS', 'UEFI', 'GPT'))
            files = {}
            for name in ('kernel', 'initrd.img', 'ramdisk-recovery.img', 'system.efs'):
                extracted = work / ('verified-' + name)
                run('xorriso', '-osirrox', 'on', '-indev', new_iso, '-extract', '/' + name, extracted)
                expected = sha(new_outer) if name == 'system.efs' else record['files'][name]['sha256']
                assert sha(extracted) == expected, name
                files[name] = {'bytes': extracted.stat().st_size, 'sha256': expected}
            # Publishing is an exclusive copy: an unrelated existing image
            # cannot be replaced, including one created during this operation.
            with args.output.open('xb') as dst, new_iso.open('rb') as src:
                shutil.copyfileobj(src, dst, 4 * 1024**2)
            assert sha(args.output) == sha(new_iso)
            files[args.output.name] = {'bytes': args.output.stat().st_size, 'sha256': sha(args.output)}
            result = dict(record)
            result.update(revision=args.revision, base_revision=record['revision'],
                          base_iso_sha256=expected_iso['sha256'], files=files,
                          state='Offline image and complete Home-only delta verified; runtime tests recorded separately',
                          derivation='Verified r5 platform; only English Home 1.1 APK replaced; no platform compile',
                          home={'version': '1.1', 'version_code': 2, 'language': 'en', 'sha256': args.home_sha256})
            result['packaged_metadata'] = dict(record['packaged_metadata'], inner_system_image_sha256=sha(inner))
            delta = {'base_revision': record['revision'], 'revision': args.revision,
                     'changed_file': HOME, 'before': before[HOME], 'after': after[HOME],
                     'unchanged_entries': len(before) - 1,
                     'all_other_file_contents_modes_ownership_xattrs_symlinks_preserved': True,
                     'kernel_initrd_recovery_preserved': True, 'uefi_bios_gpt_preserved': True}
            args.output.with_name('image-verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            args.output.with_name('home-delta.json').write_text(json.dumps(delta, indent=2) + '\n', encoding='utf-8')
            print('Verified image:', args.output.name, files[args.output.name], flush=True)
        finally:
            if mounted:
                run('umount', mount)
    print('Temporary image workspace released.', flush=True)


if __name__ == '__main__':
    main()
