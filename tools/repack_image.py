#!/usr/bin/env python3
"""Apply a declared set of file changes to a verified ISO's system image.

Every change names its path, the expected SHA-256 before (or "absent") and the
input file with its expected SHA-256 after. All other system entries must keep
their contents, mode, ownership, extended attributes and symlink targets.

Linux root, erofs-utils, e2fsprogs and xorriso required. This repacks an
existing platform; it does not compile Android.
"""
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from repack_home import inventory, run, sha


def load_spec(path, base):
    spec = json.loads(path.read_text(encoding='utf-8'))
    changes = []
    for change in spec['changes']:
        source = (base / change['input']).resolve()
        assert sha(source) == change['sha256'], 'Input hash mismatch: ' + change['input']
        assert change['path'].startswith('system/') and '..' not in change['path'].split('/')
        changes.append(dict(change, source=source))
    return spec, changes


def apply(mount, before, changes):
    for change in changes:
        target = mount / change['path']
        assert target.parent.resolve().is_relative_to(mount.resolve()), change['path']
        assert not target.is_symlink(), change['path']
        previous = before.get(change['path'])
        if change['before'] == 'absent':
            assert previous is None, change['path'] + ' already exists'
            template = before[change['label_from']]
            shutil.copyfile(change['source'], target)
            os.chown(target, template['uid'], template['gid'])
            os.chmod(target, int(change['mode'], 8))
            for key, value in template['xattrs'].items():
                os.setxattr(target, key, bytes.fromhex(value), follow_symlinks=False)
        else:
            assert previous and previous['kind'] == 'file', change['path']
            assert previous['sha256'] == change['before'], change['path'] + ' base hash mismatch'
            shutil.copyfile(change['source'], target)


def check_delta(before, after, changes):
    paths = {change['path'] for change in changes}
    changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
    assert changed == paths, sorted(changed ^ paths)
    for change in changes:
        new = after[change['path']]
        assert new['sha256'] == change['sha256'], change['path']
        if change['before'] != 'absent':
            for key in ('mode', 'uid', 'gid', 'xattrs', 'kind'):
                assert before[change['path']][key] == new[key], (change['path'], key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-iso', type=Path, required=True)
    parser.add_argument('--base-record', type=Path, required=True)
    parser.add_argument('--changes', type=Path, required=True, help='JSON change specification')
    parser.add_argument('--inputs', type=Path, required=True, help='Directory holding the change inputs')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if os.name != 'posix' or os.geteuid() != 0:
        parser.error('Run on a Linux build host as root, with loop-mount support')
    if args.output.exists():
        parser.error('Output already exists; never overwrite a released image')
    spec, changes = load_spec(args.changes, args.inputs)
    record = json.loads(args.base_record.read_text(encoding='utf-8'))
    expected_iso = record['files'][args.base_iso.name]
    assert args.base_iso.stat().st_size == expected_iso['bytes']
    assert sha(args.base_iso) == expected_iso['sha256'], 'Base ISO hash mismatch'
    assert shutil.disk_usage(tempfile.gettempdir()).free > 24 * 1024**3
    assert shutil.disk_usage(args.output.parent).free > 4 * 1024**3
    with tempfile.TemporaryDirectory(prefix='stremiobox-repack-') as temporary:
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
            print('Inventorying every system entry before the change...', flush=True)
            before = inventory(mount)
            run('umount', mount)
            mounted = False
            run('mount', '-o', 'loop,rw', inner, mount)
            mounted = True
            apply(mount, before, changes)
            after = inventory(mount)
            check_delta(before, after, changes)
            print(f'Verified: {len(changes)} declared entries changed; every other entry preserved.', flush=True)
            os.sync()
            run('umount', mount)
            mounted = False
            run('/usr/sbin/e2fsck', '-f', '-n', inner)
            new_outer = work / 'system.efs'
            print('Compressing the system image...', flush=True)
            run('mkfs.erofs', '-zlz4hc,9', '--all-root', new_outer, container)
            run('fsck.erofs', new_outer)
            # Verify the compressed result's actual file inventory.
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
            boot = run('xorriso', '-indev', new_iso, '-report_el_torito', 'plain', '-report_system_area', 'plain')
            assert all(value in boot for value in ('BIOS', 'UEFI', 'GPT'))
            files = {}
            for name in ('kernel', 'initrd.img', 'ramdisk-recovery.img', 'system.efs'):
                extracted = work / ('verified-' + name)
                run('xorriso', '-osirrox', 'on', '-indev', new_iso, '-extract', '/' + name, extracted)
                expected = sha(new_outer) if name == 'system.efs' else record['files'][name]['sha256']
                assert sha(extracted) == expected, name
                files[name] = {'bytes': extracted.stat().st_size, 'sha256': expected}
            with args.output.open('xb') as dst, new_iso.open('rb') as src:
                shutil.copyfileobj(src, dst, 4 * 1024**2)
            assert sha(args.output) == sha(new_iso)
            files[args.output.name] = {'bytes': args.output.stat().st_size, 'sha256': sha(args.output)}
            result = dict(record)
            result.update(revision=spec['revision'], base_revision=record['revision'],
                          base_iso_sha256=expected_iso['sha256'], files=files,
                          state='Offline image and complete declared delta verified; runtime tests recorded separately',
                          derivation=spec['derivation'])
            result['packaged_metadata'] = dict(record['packaged_metadata'], inner_system_image_sha256=sha(inner))
            delta = {'base_revision': record['revision'], 'revision': spec['revision'],
                     'changes': [{'path': c['path'], 'reason': c['reason'],
                                  'before': before.get(c['path'], 'absent'), 'after': after[c['path']]}
                                 for c in changes],
                     'unchanged_entries': len(before) - sum(c['before'] != 'absent' for c in changes),
                     'all_other_file_contents_modes_ownership_xattrs_symlinks_preserved': True,
                     'kernel_initrd_recovery_preserved': True, 'uefi_bios_gpt_preserved': True}
            args.output.with_name('image-verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            args.output.with_name('image-delta.json').write_text(json.dumps(delta, indent=2) + '\n', encoding='utf-8')
            print('Verified image:', args.output.name, files[args.output.name], flush=True)
        finally:
            if mounted:
                run('umount', mount)
    print('Temporary image workspace released.', flush=True)


if __name__ == '__main__':
    main()
