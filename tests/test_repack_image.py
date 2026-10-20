# SPDX-License-Identifier: MIT
"""Checks for the declared-delta logic used to derive a release image."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import repack_image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def entry(digest, mode=0o644):
    return {'mode': mode, 'uid': 0, 'gid': 0, 'xattrs': {'security.selinux': '00'},
            'kind': 'file', 'bytes': 1, 'sha256': digest}


class DeltaTests(unittest.TestCase):
    changes = [{'path': 'system/bin/a', 'before': 'old', 'sha256': 'new'},
               {'path': 'system/etc/b', 'before': 'absent', 'sha256': 'added'}]

    def test_declared_changes_pass(self):
        before = {'system/bin/a': entry('old'), 'system/x': entry('same')}
        after = {'system/bin/a': entry('new'), 'system/x': entry('same'), 'system/etc/b': entry('added')}
        repack_image.check_delta(before, after, self.changes)

    def test_undeclared_change_fails(self):
        before = {'system/bin/a': entry('old'), 'system/x': entry('same')}
        after = {'system/bin/a': entry('new'), 'system/x': entry('other'), 'system/etc/b': entry('added')}
        with self.assertRaises(AssertionError):
            repack_image.check_delta(before, after, self.changes)

    def test_changed_permissions_fail(self):
        before = {'system/bin/a': entry('old', 0o755)}
        after = {'system/bin/a': entry('new', 0o644), 'system/etc/b': entry('added')}
        with self.assertRaises(AssertionError):
            repack_image.check_delta(before, after, self.changes)

    def test_wrong_result_hash_fails(self):
        before = {'system/bin/a': entry('old')}
        after = {'system/bin/a': entry('wrong'), 'system/etc/b': entry('added')}
        with self.assertRaises(AssertionError):
            repack_image.check_delta(before, after, self.changes)


class SpecTests(unittest.TestCase):
    def test_repack_specs_are_consistent(self):
        specs = sorted((ROOT / 'releases').glob('r*-changes.json'))
        self.assertGreaterEqual(len(specs), 2)
        for path in specs:
            with self.subTest(path.name):
                spec = json.loads(path.read_text(encoding='utf-8'))
                delta = json.loads(path.with_name(path.name.replace('-changes', '-image-delta'))
                                   .read_text(encoding='utf-8'))
                self.assertEqual(spec['revision'], delta['revision'])
                self.assertEqual(spec['base_revision'], delta['base_revision'])
                self.assertEqual([c['path'] for c in spec['changes']], [c['path'] for c in delta['changes']])
                for declared, recorded in zip(spec['changes'], delta['changes']):
                    self.assertEqual(declared['sha256'], recorded['after']['sha256'])
                    if declared['before'] != 'absent':
                        self.assertEqual(declared['before'], recorded['before']['sha256'])

    def test_input_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            (base / 'input').write_bytes(b'data')
            spec = base / 'spec.json'
            good = hashlib.sha256(b'data').hexdigest()
            for digest, path, ok in ((good, 'system/bin/x', True), ('0' * 64, 'system/bin/x', False),
                                     (good, 'system/../etc', False), (good, 'vendor/x', False)):
                spec.write_text(json.dumps({'changes': [{'path': path, 'before': 'absent', 'input': 'input',
                                                         'sha256': digest}]}), encoding='utf-8')
                if ok:
                    repack_image.load_spec(spec, base)
                else:
                    with self.assertRaises(AssertionError):
                        repack_image.load_spec(spec, base)


if __name__ == '__main__':
    unittest.main()
