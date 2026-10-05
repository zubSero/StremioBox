# SPDX-License-Identifier: MIT
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import prepare_platform


def run(directory, *args):
    return subprocess.check_output(['git', '-C', str(directory), *args], text=True).strip()


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.source = root / 'source'
        self.public = root / 'public'
        (self.source / 'build').mkdir(parents=True)
        (self.source / 'build/envsetup.sh').write_text('# fixture')
        self.project = self.source / 'frameworks/example'
        self.project.mkdir(parents=True)
        run(self.project, 'init', '-q')
        run(self.project, 'config', 'user.name', 'Fixture')
        run(self.project, 'config', 'user.email', 'fixture@example.invalid')
        run(self.project, 'config', 'core.autocrlf', 'false')
        self.file = self.project / 'value.txt'
        self.file.write_bytes(b'before\n')
        run(self.project, 'add', '.')
        run(self.project, 'commit', '-qm', 'Fixture source')
        revision = run(self.project, 'rev-parse', 'HEAD')
        self.file.write_bytes(b'after\n')
        patch = run(self.project, 'diff') + '\n'
        run(self.project, 'checkout', '--', 'value.txt')
        (self.public / 'platform/patches').mkdir(parents=True)
        (self.public / 'platform/product/stremiobox').mkdir(parents=True)
        (self.public / 'platform/product/example.mk').write_text('# fixture product')
        patch_path = self.public / 'platform/patches/0001.patch'
        patch_path.write_bytes(patch.encode())
        manifest = f'<manifest><project name="example" path="frameworks/example" revision="{revision}"/></manifest>\n'.encode()
        (self.public / 'platform/manifest.xml').write_bytes(manifest)
        self.lock = {'manifest_project_count': 1, 'manifest_sha256': hashlib.sha256(manifest).hexdigest(),
                     'source_ports': [{'repository': 'frameworks/example', 'patch': 'platform/patches/0001.patch',
                                       'sha256': hashlib.sha256(patch.encode()).hexdigest()}]}
        self.save_lock()
        self.apk = root / 'input.apk'
        self.apk.write_bytes(b'fixture app')
        self.app_hash = hashlib.sha256(self.apk.read_bytes()).hexdigest()
        self.destination = self.source / 'device/local/nuc10_tv'

    def save_lock(self):
        (self.public / 'platform/input-lock.json').write_text(json.dumps(self.lock), encoding='utf-8')

    def prepare(self, apply=False):
        prepare_platform.prepare(self.source, self.apk, apply, self.public, self.app_hash)

    def test_preview_does_not_change_checkout(self):
        self.prepare()
        self.assertEqual(self.file.read_bytes(), b'before\n')
        self.assertFalse(self.destination.exists())
        self.assertEqual(run(self.project, 'status', '--porcelain'), '')

    def test_apply_patches_and_copies_only_into_new_product(self):
        self.prepare(apply=True)
        self.assertEqual(self.file.read_bytes(), b'after\n')
        self.assertEqual((self.destination / 'stremiobox/stremio.apk').read_bytes(), b'fixture app')
        self.assertTrue((self.destination / 'example.mk').is_file())

    def test_failure_rolls_back_previous_patch(self):
        bad = self.public / 'platform/patches/0002.patch'
        bad.write_bytes(b'diff --git a/value.txt b/value.txt\n--- a/value.txt\n+++ b/value.txt\n@@ -1 +1 @@\n-not present\n+bad\n')
        self.lock['source_ports'].append({'repository': 'frameworks/example', 'patch': 'platform/patches/0002.patch',
                                         'sha256': hashlib.sha256(bad.read_bytes()).hexdigest()})
        self.save_lock()
        with self.assertRaises(subprocess.CalledProcessError):
            self.prepare(apply=True)
        self.assertEqual(self.file.read_bytes(), b'before\n')
        self.assertEqual(run(self.project, 'status', '--porcelain'), '')
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.destination.parent.glob('.stremiobox-*')), [])

    def test_dirty_checkout_is_preserved_and_rejected(self):
        self.file.write_bytes(b'my local changes\n')
        with self.assertRaises(ValueError):
            self.prepare(apply=True)
        self.assertEqual(self.file.read_bytes(), b'my local changes\n')
        self.assertFalse(self.destination.exists())

    def test_existing_product_is_preserved(self):
        self.destination.mkdir(parents=True)
        existing = self.destination / 'keep.txt'
        existing.write_text('keep')
        with self.assertRaises(FileExistsError):
            self.prepare(apply=True)
        self.assertEqual(existing.read_text(), 'keep')
        self.assertEqual(self.file.read_bytes(), b'before\n')

    def test_wrong_app_or_patch_is_rejected_before_mutation(self):
        self.apk.write_bytes(b'wrong app')
        with self.assertRaises(ValueError):
            self.prepare(apply=True)
        self.assertEqual(self.file.read_bytes(), b'before\n')
        self.apk.write_bytes(b'fixture app')
        (self.public / self.lock['source_ports'][0]['patch']).write_bytes(b'changed patch')
        with self.assertRaises(ValueError):
            self.prepare(apply=True)
        self.assertFalse(self.destination.exists())

    def test_new_project_revision_is_rejected(self):
        self.file.write_bytes(b'new source\n')
        run(self.project, 'add', '.')
        run(self.project, 'commit', '-qm', 'A different source revision')
        with self.assertRaises(ValueError):
            self.prepare(apply=True)
        self.assertFalse(self.destination.exists())


if __name__ == '__main__':
    unittest.main()
