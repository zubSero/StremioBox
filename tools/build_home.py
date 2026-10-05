#!/usr/bin/env python3
"""Build and sign Home with an installed Android SDK and a private user key."""
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def version_key(path: Path) -> tuple:
    return tuple(int(n) for n in re.findall(r'\d+', path.name))


def run(*args: str | Path) -> None:
    command = [str(arg) for arg in args]
    # The SDK's d8/apksigner Windows entry points are batch files. Their paths
    # and arguments are fixed local inputs; no password is placed on the CLI.
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, default=os.environ.get('ANDROID_SDK_ROOT'))
    parser.add_argument('--build-tools', help='SDK Build Tools version, otherwise highest installed')
    parser.add_argument('--keystore', type=Path, required=True)
    parser.add_argument('--alias', required=True)
    parser.add_argument('--output', type=Path, default=Path('out/StremioBoxHome.apk'))
    args = parser.parse_args()
    if args.sdk is None or not args.sdk.is_dir():
        parser.error('Supply an installed Android SDK with --sdk or ANDROID_SDK_ROOT')
    if not args.keystore.is_file() or 'STREMIOBOX_KEY_PASSWORD' not in os.environ:
        parser.error('Supply your keystore and set STREMIOBOX_KEY_PASSWORD privately')
    if args.output.exists():
        parser.error('Output already exists; choose another path')
    sdk = args.sdk.resolve()
    jar = sdk / 'platforms/android-35/android.jar'
    choices = sorted((sdk / 'build-tools').glob('*'), key=version_key)
    build = sdk / 'build-tools' / args.build_tools if args.build_tools else choices[-1] if choices else None
    if not jar.is_file() or build is None or not build.is_dir():
        parser.error('Install SDK platform 35 and Build Tools')
    windows = os.name == 'nt'
    def sdk_tool(name: str) -> Path:
        extension = '.bat' if windows and name in ('d8', 'apksigner') else '.exe' if windows else ''
        path = build / (name + extension)
        if not path.is_file():
            parser.error(f'Missing SDK tool: {path}')
        return path
    java_home = os.environ.get('JAVA_HOME')
    javac = Path(java_home) / 'bin' / ('javac.exe' if windows else 'javac') if java_home else shutil.which('javac')
    if not javac:
        parser.error('Install a JDK and set JAVA_HOME or add javac to PATH')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='stremiobox-home-') as temporary:
        work = Path(temporary)
        for part in ('res/drawable', 'assets', 'classes', 'dex'):
            (work / part).mkdir(parents=True)
        shutil.copyfile(ROOT / 'docs/assets/logo.png', work / 'res/drawable/logo.png')
        shutil.copyfile(ROOT / 'docs/assets/tv-wallpaper.png', work / 'assets/tv-wallpaper.png')
        run(sdk_tool('aapt2'), 'compile', '--dir', work / 'res', '-o', work / 'resources.zip')
        run(sdk_tool('aapt2'), 'link', '-o', work / 'resources.apk', '--manifest',
            ROOT / 'launcher/AndroidManifest.xml', '-I', jar, '-A', work / 'assets', work / 'resources.zip')
        run(javac, '--release', '8', '-classpath', jar, '-d', work / 'classes',
            *sorted((ROOT / 'launcher/src').rglob('*.java')))
        run(sdk_tool('d8'), '--min-api', '26', '--lib', jar, '--output', work / 'dex',
            *sorted((work / 'classes').rglob('*.class')))
        with zipfile.ZipFile(work / 'resources.apk') as resources, zipfile.ZipFile(work / 'unsigned.apk', 'w', zipfile.ZIP_STORED) as apk:
            for name in resources.namelist():
                apk.writestr(name, resources.read(name))
            apk.write(work / 'dex/classes.dex', 'classes.dex')
        run(sdk_tool('zipalign'), '-p', '4', work / 'unsigned.apk', work / 'aligned.apk')
        signed = work / 'signed.apk'
        run(sdk_tool('apksigner'), 'sign', '--ks', args.keystore.resolve(), '--ks-key-alias', args.alias,
            '--ks-pass', 'env:STREMIOBOX_KEY_PASSWORD', '--key-pass', 'env:STREMIOBOX_KEY_PASSWORD',
            '--out', signed, work / 'aligned.apk')
        run(sdk_tool('apksigner'), 'verify', '--verbose', signed)
        # Copy exclusively only after signature verification succeeds.
        with args.output.open('xb') as dst, signed.open('rb') as src:
            shutil.copyfileobj(src, dst)
    print('Built and signature-verified:', args.output)
    print('Your own signing key creates a fork; it cannot update the original r5 prebuilt in place.')


if __name__ == '__main__':
    main()
