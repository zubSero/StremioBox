"""Run the Linux/macOS helper against the same corruption/overwrite fixtures."""
# SPDX-License-Identifier: MIT
import shutil
import os
import subprocess
import unittest
import test_native_download as fixtures


class ShellDownloadTests(fixtures.NativeDownloadTests):
    __unittest_skip__ = os.name == 'nt' or not shutil.which('bash')
    __unittest_skip_why__ = 'Bash required'

    def run_helper(self, offline=True):
        lines = ['release ' + self.data['release']]
        for kind, spec in [('image', self.data['image']), *[('part', p) for p in self.data['parts']]]:
            lines.append(f"{kind} {spec['name']} {spec['bytes']} {spec['sha256']}")
        self.manifest.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        args = ['bash', str(fixtures.ROOT / 'tools/download.sh'), '--manifest', str(self.manifest),
                '--output', str(self.output)]
        if offline:
            args.append('--offline')
        return subprocess.run(args, capture_output=True, timeout=30)

    def test_foreign_url_rejected(self):
        # Download URLs are constructed from a validated release ID, never supplied by a manifest.
        self.data['release'] = '../../example.com'
        self.assert_failed_cleanly(self.run_helper())


if __name__ == '__main__':
    unittest.main()
