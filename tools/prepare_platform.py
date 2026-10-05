#!/usr/bin/env python3
"""Validate a pinned Android checkout and optionally apply the public overlay."""
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP_SHA256 = '3a9f86646ba18f4f11073dfbb01e10b1d4019e78d89ba58ec3de79f36f6cfc8c'


def sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open('rb') as src:
        for data in iter(lambda: src.read(4 * 1024 * 1024), b''):
            checksum.update(data)
    return checksum.hexdigest()


def git(directory: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(directory), *args], text=True).strip()


def within(root: Path, relative: str) -> Path:
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()) or target == root.resolve():
        raise ValueError(f'Unsafe relative path: {relative}')
    return target


def prepare(source: Path, apk: Path, apply: bool = False, public_root: Path = ROOT,
            expected_app_hash: str = APP_SHA256) -> None:
    source = source.resolve()
    if not (source / 'build/envsetup.sh').is_file():
        raise ValueError('Source is not an Android checkout with build/envsetup.sh')
    lock = json.loads((public_root / 'platform/input-lock.json').read_text(encoding='utf-8'))
    manifest_path = public_root / 'platform/manifest.xml'
    if sha256(manifest_path) != lock['manifest_sha256']:
        raise ValueError('Pinned manifest hash mismatch')
    projects = ET.fromstring(manifest_path.read_bytes()).findall('project')
    if len(projects) != lock['manifest_project_count']:
        raise ValueError('Pinned manifest project count mismatch')
    revisions = {}
    for project in projects:
        path = project.get('path') or project.get('name')
        if not path or path in revisions:
            raise ValueError('Manifest has an invalid or duplicate project path')
        revisions[path] = project.get('revision')
        directory = within(source, path)
        if not directory.is_dir() or git(directory, 'rev-parse', 'HEAD') != revisions[path]:
            raise ValueError(f'Project revision mismatch: {path}')
    if not apk.is_file() or sha256(apk) != expected_app_hash:
        raise ValueError('Stremio APK does not match the original signed app input')
    destination = within(source, 'device/local/nuc10_tv')
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Product destination already exists; use a fresh locked checkout')
    steps = []
    checked = set()
    for port in lock['source_ports']:
        if port['repository'] not in revisions:
            raise ValueError('Patch project is absent from the locked manifest')
        directory = within(source, port['repository'])
        patch = within(public_root, port['patch'])
        if sha256(patch) != port['sha256']:
            raise ValueError(f'Patch checksum mismatch: {patch.name}')
        if directory not in checked:
            if git(directory, 'status', '--porcelain', '--untracked-files=all'):
                raise ValueError(f'Patch project has local changes: {port["repository"]}')
            checked.add(directory)
        steps.append((directory, patch))
        print(f'{"Apply" if apply else "Plan"}: {patch.name} -> {port["repository"]}', flush=True)
    if not apply:
        print('Pinned revisions, hashes and app input verified. Use --apply to prepare this checkout.')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    applied = []
    try:
        with tempfile.TemporaryDirectory(prefix='.stremiobox-', dir=destination.parent) as staging:
            product = Path(staging) / 'product'
            shutil.copytree(public_root / 'platform/product', product)
            shutil.copyfile(apk, product / 'stremiobox/stremio.apk')
            if sha256(product / 'stremiobox/stremio.apk') != expected_app_hash:
                raise ValueError('App input changed during preparation')
            for directory, patch in steps:
                subprocess.run(['git', '-C', str(directory), 'apply', '--check', str(patch)], check=True)
                subprocess.run(['git', '-C', str(directory), 'apply', str(patch)], check=True)
                applied.append((directory, patch))
            if destination.exists() or destination.is_symlink():
                raise FileExistsError('Product destination appeared during preparation')
            os.rename(product, destination)
    except BaseException:
        for directory, patch in reversed(applied):
            subprocess.run(['git', '-C', str(directory), 'apply', '-R', str(patch)], check=True)
        raise
    print('Overlay prepared. No build, host package installation or device writes performed.')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--stremio-apk', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        prepare(args.source, args.stremio_apk, args.apply)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f'Preparation failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
