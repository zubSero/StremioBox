# SPDX-License-Identifier: MIT
import copy
import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import download


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output = Path(self.directory.name)
        self.payloads = [b'first raw image piece\x00', b'second raw image piece\xff']
        combined = b''.join(self.payloads)
        self.manifest = {
            'schema': 1, 'project': 'StremioBox', 'release': 'test',
            'image': {'name': 'test.iso', 'bytes': len(combined), 'sha256': hashlib.sha256(combined).hexdigest()},
            'parts': [{'name': f'test.iso.{i:03d}', 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                       'url': f'https://github.com/zubSero/StremioBox/releases/download/test/test.iso.{i:03d}'}
                      for i, data in enumerate(self.payloads, 1)]}

    def responses(self, request, **kwargs):
        index = int(request.full_url[-3:]) - 1
        return io.BytesIO(self.payloads[index])

    def local_parts(self):
        for part, data in zip(self.manifest['parts'], self.payloads):
            (self.output / part['name']).write_bytes(data)

    def assert_no_partial(self):
        self.assertEqual(list(self.output.glob('*.partial')), [])

    def test_download_assembles_verified_image_and_reuses_it(self):
        with patch.object(download.urllib.request, 'urlopen', side_effect=self.responses) as request:
            path = download.obtain(self.manifest, self.output)
            self.assertEqual(path.read_bytes(), b''.join(self.payloads))
            self.assertEqual(request.call_count, 2)
        with patch.object(download.urllib.request, 'urlopen') as request:
            self.assertEqual(download.obtain(self.manifest, self.output), path)
            request.assert_not_called()
        self.assert_no_partial()

    def test_offline_assembly(self):
        self.local_parts()
        with patch.object(download.urllib.request, 'urlopen') as request:
            self.assertEqual(download.obtain(self.manifest, self.output, offline=True).read_bytes(), b''.join(self.payloads))
            request.assert_not_called()

    def test_corrupt_download_never_publishes_a_part_or_image(self):
        with patch.object(download.urllib.request, 'urlopen', return_value=io.BytesIO(b'corrupt')):
            with self.assertRaises(ValueError):
                download.obtain(self.manifest, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_existing_unrelated_image_is_preserved_before_transfer(self):
        destination = self.output / 'test.iso'
        destination.write_bytes(b'important existing file')
        with patch.object(download.urllib.request, 'urlopen') as request:
            with self.assertRaises(FileExistsError):
                download.obtain(self.manifest, self.output)
            request.assert_not_called()
        self.assertEqual(destination.read_bytes(), b'important existing file')

    def test_corrupt_existing_part_is_preserved_and_rejected(self):
        part = self.output / self.manifest['parts'][1]['name']
        part.write_bytes(b'existing unrelated part')
        with patch.object(download.urllib.request, 'urlopen') as request:
            with self.assertRaises(FileExistsError):
                download.obtain(self.manifest, self.output)
            request.assert_not_called()
        self.assertEqual(part.read_bytes(), b'existing unrelated part')

    def test_final_hash_is_checked_even_when_all_part_hashes_match(self):
        self.local_parts()
        self.manifest['image']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            download.obtain(self.manifest, self.output, offline=True)
        self.assertFalse((self.output / 'test.iso').exists())
        self.assert_no_partial()

    def test_interrupted_transfer_removes_only_its_temporary_file(self):
        class Broken(io.BytesIO):
            def read(self, *args):
                raise OSError('transfer interrupted')
        sentinel = self.output / 'keep.txt'
        sentinel.write_text('keep')
        with patch.object(download.urllib.request, 'urlopen', return_value=Broken()):
            with self.assertRaises(OSError):
                download.obtain(self.manifest, self.output)
        self.assertEqual(sentinel.read_text(), 'keep')
        self.assert_no_partial()

    def test_destination_created_during_download_is_preserved(self):
        destination = self.output / 'test.iso'
        original = download.commit_verified
        def racing_commit(temporary, target):
            if target == destination:
                target.write_bytes(b'created by someone else')
            return original(temporary, target)
        with patch.object(download.urllib.request, 'urlopen', side_effect=self.responses), patch.object(download, 'commit_verified', side_effect=racing_commit):
            with self.assertRaises(FileExistsError):
                download.obtain(self.manifest, self.output)
        self.assertEqual(destination.read_bytes(), b'created by someone else')
        self.assert_no_partial()

    def test_unsafe_filename_and_foreign_url_are_rejected(self):
        for mutation in ('path', 'url'):
            manifest = copy.deepcopy(self.manifest)
            if mutation == 'path':
                manifest['image']['name'] = '../escape.iso'
            else:
                manifest['parts'][0]['url'] = 'https://example.com/unknown'
            with self.assertRaises(ValueError):
                download.validate_manifest(manifest)


if __name__ == '__main__':
    unittest.main()
