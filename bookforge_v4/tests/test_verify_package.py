import json
import tempfile
import unittest
from pathlib import Path
from bookforge_v3.release_manifest import sha256
from bookforge_v4.verify_package import verify

class PackageTests(unittest.TestCase):
    def fixture(self,root):
        for theme in ('clean-premium','playful-illustrated'):
            (root/theme).mkdir()
            names=('manuscript.json','lessons.json',f'{theme}/interior.pdf',f'{theme}/cover.pdf',
                   'editorial-review-items.json','review-attestations.json','editorial-review.html')
            files={}
            for name in names:
                path=root/name;path.write_bytes(b'fixture')
                files[name]={'bytes':path.stat().st_size,'sha256':sha256(path)}
            (root/theme/'handoff.json').write_text(json.dumps({'files':files}))

    def test_valid_then_modified_and_missing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            self.assertTrue(verify(root)['ok'])
            (root/'lessons.json').write_bytes(b'changed')
            self.assertFalse(verify(root)['ok'])
            (root/'lessons.json').unlink()
            self.assertFalse(verify(root)['ok'])

    def test_escape_path_and_missing_inventory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            path=root/'clean-premium/handoff.json'
            report=json.loads(path.read_text());report['files']['../outside']={}
            del report['files']['lessons.json'];path.write_text(json.dumps(report))
            result=verify(root)
            self.assertFalse(result['ok'])
            self.assertTrue(any('escapes' in error for error in result['errors']))

    def test_missing_handoffs_are_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:self.assertFalse(verify(tmp)['ok'])
