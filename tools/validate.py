#!/usr/bin/env python3
"""Check public sources, locked assets, release metadata and documentation."""
# SPDX-License-Identifier: MIT
from __future__ import annotations

import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET

from download import validate_manifest

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        for name in ('href', 'src'):
            if data.get(name):
                self.links.append(data[name])
        if data.get('id'):
            if data['id'] in self.ids:
                raise ValueError(f'Duplicate HTML id: {data["id"]}')
            self.ids.add(data['id'])
        if tag == 'img' and 'alt' not in data:
            raise ValueError('Image is missing an alt attribute')


def relative_link(file: Path, target: str, ids=None) -> None:
    parsed = urllib.parse.urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return
    local = (file.parent / urllib.parse.unquote(parsed.path)).resolve() if parsed.path else file
    if not local.is_relative_to(ROOT) or not local.exists():
        raise ValueError(f'Broken local link in {file.relative_to(ROOT)}: {target}')
    if ids is not None and not parsed.path and parsed.fragment and parsed.fragment not in ids:
        raise ValueError(f'Broken HTML anchor: {target}')


def main() -> int:
    releases = sorted(path for path in (ROOT / 'releases').glob('r*.json')
                      if re.fullmatch(r'r\d+\.json', path.name))
    if not releases:
        raise ValueError('No release manifests found')
    for path in releases:
        release = json.loads(path.read_text(encoding='utf-8'))
        validate_manifest(release)
        native = path.with_name(path.stem + '-download.txt')
        if native.exists():
            records = ['release ' + release['release']]
            for kind, spec in [('image', release['image']), *[('part', p) for p in release['parts']]]:
                records.append(f"{kind} {spec['name']} {spec['bytes']} {spec['sha256']}")
            if native.read_text(encoding='utf-8') != '\n'.join(records) + '\n':
                raise ValueError('Native shell manifest differs from the JSON release manifest')
        image = json.loads(path.with_name(path.stem + '-image-verification.json').read_text(encoding='utf-8'))
        if image['files'][release['image']['name']] != {k: release['image'][k] for k in ('bytes', 'sha256')}:
            raise ValueError('Image verification and release manifest disagree')
        if image['private_data_included'] is not False:
            raise ValueError('Release must exclude private data')
    lock = json.loads((ROOT / 'platform/input-lock.json').read_text(encoding='utf-8'))
    manifest = ROOT / 'platform/manifest.xml'
    projects = ET.fromstring(manifest.read_bytes()).findall('project')
    if len(projects) != lock['manifest_project_count']:
        raise ValueError('Source manifest project count mismatch')
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != lock['manifest_sha256']:
        raise ValueError('Source manifest hash mismatch')
    filtered = b''.join(line for line in manifest.read_bytes().splitlines(keepends=True)
                        if b'proprietary_' not in line)
    filtered_sha = hashlib.sha256(filtered).hexdigest()
    filtered_count = len(ET.fromstring(filtered).findall('project'))
    metadata = image['packaged_metadata']
    if (filtered_sha != metadata['source_manifest_sha256']
            or filtered_count != metadata['source_manifest_projects']):
        raise ValueError('Upstream-filtered source manifest does not match the image record')
    relation = json.loads((ROOT / 'releases/manifest-verification.json').read_text(encoding='utf-8'))
    if (relation['export']['sha256'] != lock['manifest_sha256']
            or relation['embedded']['sha256'] != filtered_sha
            or relation['embedded']['projects'] != filtered_count):
        raise ValueError('Manifest verification record is inconsistent')
    for project in projects:
        if not re.fullmatch('[0-9a-f]{40}', project.get('revision', '')):
            raise ValueError('Every source project must use a pinned commit')
    if len(lock['source_ports']) != 17:
        raise ValueError('Expected 17 source ports for r5')
    for entry in lock['source_ports']:
        patch = ROOT / entry['patch']
        if hashlib.sha256(patch.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Patch hash mismatch: {patch.name}')
        subprocess.run(['git', 'apply', '--numstat', str(patch)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assets = json.loads((ROOT / 'releases/source-lock.json').read_text(encoding='utf-8'))
    for name, spec in assets['files'].items():
        path = ROOT / name
        if not path.is_file() or path.stat().st_size != spec['bytes']:
            raise ValueError(f'Locked source/asset size mismatch: {name}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != spec['sha256']:
            raise ValueError(f'Locked source/asset hash mismatch: {name}')
    english = json.loads((ROOT / 'releases/r6-image-verification.json').read_text(encoding='utf-8'))
    home = ROOT / 'platform/product/stremiobox/home/StremioBoxHome.apk'
    if hashlib.sha256(home.read_bytes()).hexdigest() != english['home']['sha256']:
        raise ValueError('Current Home prebuilt differs from the r6 packaged Home')
    delta = json.loads((ROOT / 'releases/r6-home-delta.json').read_text(encoding='utf-8'))
    if (delta['changed_file'] != 'system/product/app/StremioBoxHome/StremioBoxHome.apk'
            or delta['after']['sha256'] != english['home']['sha256']):
        raise ValueError('English Home delta is inconsistent with the release')
    secret = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}')
    private = re.compile(r'[A-Z]:[\\/]Users[\\/][^\s\\/]+'
                         r'|[A-Z]:[\\/]bt' r'-debug|/mnt/c/bt' r'-debug'
                         r'|\b192\.168\.\d{1,3}\.\d{1,3}\b', re.I)
    files = [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts]
    for path in files:
        if path.suffix.lower() in ('.p12', '.jks', '.pem', '.keystore', '.iso') or re.search(r'\.iso\.\d+$', path.name):
            raise ValueError(f'Private key or disk image belongs outside Git: {path.relative_to(ROOT)}')
        if path.name in ('adbkey', 'adbkey.pub', 'key-password.txt'):
            raise ValueError('Private device/signing material detected')
        if path.suffix in ('.png', '.apk', '.zip', '.pyc'):
            continue
        content = path.read_text(encoding='utf-8')
        if secret.search(content) or private.search(content):
            raise ValueError(f'Potential private material in {path.relative_to(ROOT)}')
        if path.suffix == '.py':
            ast.parse(content, filename=str(path))
        elif path.suffix == '.json':
            json.loads(content)
        elif path.suffix == '.xml':
            ET.fromstring(content)
        elif path.suffix == '.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
                relative_link(path, target.split(' "')[0])
        elif path.suffix == '.html':
            page = Page()
            page.feed(content)
            for link in page.links:
                relative_link(path, link, page.ids)
    print(f'Validated {len(files)} public files, 17 patches, {len(projects)} pinned projects, release and local links.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(f'Validation failed: {error}', file=sys.stderr)
        raise SystemExit(1)
