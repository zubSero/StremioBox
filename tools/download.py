#!/usr/bin/env python3
"""Download, verify and assemble a StremioBox release using only the stdlib."""
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BLOCK = 4 * 1024 * 1024


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(BLOCK), b''):
            result.update(block)
    return result.hexdigest()


def matches(path: Path, spec: dict) -> bool:
    return (not path.is_symlink() and path.is_file()
            and path.stat().st_size == spec['bytes']
            and digest(path) == spec['sha256'])


def validate_manifest(data: dict) -> None:
    if data.get('schema') != 1 or data.get('project') != 'StremioBox':
        raise ValueError('Unsupported release manifest')
    release = data.get('release', '')
    if not isinstance(release, str) or not re.fullmatch(r'[a-zA-Z0-9._-]+', release):
        raise ValueError('Invalid release name')
    image = data.get('image', {})
    parts = data.get('parts', [])
    if not isinstance(parts, list) or not 1 <= len(parts) <= 100:
        raise ValueError('Invalid part list')
    for spec in [image, *parts]:
        name = spec.get('name', '')
        if not isinstance(name, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]*', name):
            raise ValueError('Invalid asset filename')
        if type(spec.get('bytes')) is not int or spec['bytes'] <= 0:
            raise ValueError('Invalid asset size')
        if not re.fullmatch(r'[0-9a-f]{64}', spec.get('sha256', '')):
            raise ValueError('Invalid SHA-256')
    if not image['name'].endswith('.iso'):
        raise ValueError('Expected an ISO image')
    base = f'https://github.com/zubSero/StremioBox/releases/download/{release}/'
    for index, part in enumerate(parts, 1):
        if part['name'] != image['name'] + f'.{index:03d}':
            raise ValueError('Parts must be consecutive raw ISO pieces')
        if part.get('url') != base + part['name']:
            raise ValueError('Unexpected release download URL')
        if part['bytes'] >= 2 * 1024**3:
            raise ValueError('Release part exceeds GitHub asset limit')
    if sum(p['bytes'] for p in parts) != image['bytes']:
        raise ValueError('Part sizes do not match the final image')


def commit_verified(temporary: Path, destination: Path) -> None:
    """Publish without replacing an existing destination, including a race."""
    try:
        os.link(temporary, destination)
    except FileExistsError:
        raise
    except OSError:
        # FAT/exFAT may not support hard links. Exclusive creation still protects
        # existing files; clean only the output created by this invocation.
        created = False
        try:
            with destination.open('xb') as dst:
                created = True
                with temporary.open('rb') as src:
                    shutil.copyfileobj(src, dst, BLOCK)
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise


def fetch(part: dict, output: Path, offline: bool = False) -> Path:
    target = output / part['name']
    if target.exists() or target.is_symlink():
        if matches(target, part):
            print('Verified existing part:', target.name, flush=True)
            return target
        raise FileExistsError(f'Existing part is invalid; move it aside first: {target}')
    if offline:
        raise FileNotFoundError(f'Offline part is missing: {target}')
    request = urllib.request.Request(part['url'], headers={'User-Agent': 'StremioBox-download/1'})
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output, suffix='.partial', delete=False) as dst:
            temporary = Path(dst.name)
            checksum = hashlib.sha256()
            count = 0
            next_progress = 128 * 1024 * 1024
            print('Downloading:', target.name, flush=True)
            with urllib.request.urlopen(request, timeout=60) as response:
                while block := response.read(BLOCK):
                    count += len(block)
                    if count > part['bytes']:
                        raise ValueError(f'Oversized download: {target.name}')
                    checksum.update(block)
                    dst.write(block)
                    if count >= next_progress:
                        print(f'  {count / part["bytes"]:.0%}', flush=True)
                        next_progress += 128 * 1024 * 1024
        if count != part['bytes'] or checksum.hexdigest() != part['sha256']:
            raise ValueError(f'Download checksum/size mismatch: {target.name}')
        commit_verified(temporary, target)
        print('Verified downloaded part:', target.name, flush=True)
        return target
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def obtain(data: dict, output: Path, offline: bool = False) -> Path:
    validate_manifest(data)
    output.mkdir(parents=True, exist_ok=True)
    image = data['image']
    destination = output / image['name']
    if destination.exists() or destination.is_symlink():
        if matches(destination, image):
            print('Verified existing ISO:', destination, flush=True)
            return destination
        raise FileExistsError(f'Existing ISO is different; move it aside first: {destination}')
    # Preflight all existing parts before downloading any missing one.
    missing = 0
    for part in data['parts']:
        path = output / part['name']
        if path.exists() or path.is_symlink():
            if not matches(path, part):
                raise FileExistsError(f'Existing part is invalid; move it aside first: {path}')
        else:
            missing += part['bytes']
    if shutil.disk_usage(output).free < missing + image['bytes']:
        raise OSError('Insufficient space for missing parts and the assembled ISO')
    paths = [fetch(p, output, offline) for p in data['parts']]
    temporary = None
    try:
        print('Assembling and verifying the ISO...', flush=True)
        with tempfile.NamedTemporaryFile(dir=output, suffix='.partial', delete=False) as dst:
            temporary = Path(dst.name)
            checksum = hashlib.sha256()
            total = 0
            for path in paths:
                with path.open('rb') as src:
                    while block := src.read(BLOCK):
                        dst.write(block)
                        checksum.update(block)
                        total += len(block)
        if total != image['bytes'] or checksum.hexdigest() != image['sha256']:
            raise ValueError('Final ISO checksum/size mismatch; no image published')
        commit_verified(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print('ISO verified:', destination, flush=True)
    print('SHA-256:', image['sha256'], flush=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'releases/r6.json')
    parser.add_argument('--output', type=Path, default=Path('downloads'))
    parser.add_argument('--offline', action='store_true', help='Assemble only already-downloaded parts')
    args = parser.parse_args()
    try:
        obtain(json.loads(args.manifest.read_text(encoding='utf-8')), args.output, args.offline)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
