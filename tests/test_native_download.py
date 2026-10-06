"""Exercise the actual Windows PowerShell helper against small release fixtures."""
# SPDX-License-Identifier: MIT
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which('powershell.exe') if os.name == 'nt' else None


@unittest.skipUnless(POWERSHELL, 'Windows PowerShell required')
class NativeDownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='stremiobox-native-test-')
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'output with spaces'
        self.output.mkdir()
        blocks = [b'first raw ISO part\x00', b'second raw ISO part\xff']
        image = b''.join(blocks)
        self.data = {'schema': 1, 'project': 'StremioBox', 'release': 'fixture',
                     'image': self.spec('fixture.iso', image), 'parts': []}
        for i, block in enumerate(blocks, 1):
            part = self.spec(f'fixture.iso.{i:03}', block)
            part['url'] = ('https://github.com/zubSero/StremioBox/releases/download/'
                           'fixture/' + part['name'])
            self.data['parts'].append(part)
            (self.output / part['name']).write_bytes(block)
        self.image = image
        self.manifest = Path(self.temp.name) / 'manifest.json'

    @staticmethod
    def spec(name, content):
        return {'name': name, 'bytes': len(content),
                'sha256': hashlib.sha256(content).hexdigest()}

    def run_helper(self, offline=True):
        self.manifest.write_text(json.dumps(self.data), encoding='utf-8')
        args = [POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                str(ROOT / 'tools/download.ps1'), '-Manifest', str(self.manifest),
                '-OutputDirectory', str(self.output)]
        if offline:
            args.append('-Offline')
        return subprocess.run(args, capture_output=True, timeout=30)

    def assert_failed_cleanly(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse((self.output / 'fixture.iso').exists())
        self.assertEqual(list(self.output.glob('*.partial')), [])

    def test_assemble_and_reuse(self):
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.output / 'fixture.iso').read_bytes(), self.image)
        for part in self.data['parts']:
            (self.output / part['name']).unlink()
        self.assertEqual(self.run_helper().returncode, 0)

    def test_existing_output_preserved(self):
        path = self.output / 'fixture.iso'
        path.write_bytes(b'unrelated user data')
        self.assertNotEqual(self.run_helper().returncode, 0)
        self.assertEqual(path.read_bytes(), b'unrelated user data')

    def test_corrupt_part_rejected_before_download(self):
        first = self.output / self.data['parts'][0]['name']
        first.unlink()
        second = self.output / self.data['parts'][1]['name']
        second.write_bytes(b'wrong')
        result = self.run_helper(offline=False)
        self.assert_failed_cleanly(result)
        self.assertNotIn(b'Downloading:', result.stdout)
        self.assertEqual(second.read_bytes(), b'wrong')

    def test_missing_offline_part(self):
        (self.output / self.data['parts'][1]['name']).unlink()
        self.assert_failed_cleanly(self.run_helper())

    def test_wrong_final_hash_cleans_temporary(self):
        self.data['image']['sha256'] = '0' * 64
        self.assert_failed_cleanly(self.run_helper())

    def test_path_traversal_rejected(self):
        self.data['image']['name'] = '../escape.iso'
        self.assert_failed_cleanly(self.run_helper())
        self.assertFalse((self.output.parent / 'escape.iso').exists())

    def test_foreign_url_rejected(self):
        self.data['parts'][0]['url'] = 'https://example.com/fixture.iso.001'
        self.assert_failed_cleanly(self.run_helper())

    def test_non_integer_size_rejected(self):
        self.data['parts'][0]['bytes'] = float(self.data['parts'][0]['bytes'])
        self.assert_failed_cleanly(self.run_helper())
