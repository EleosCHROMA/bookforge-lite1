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
            names=('manuscript.json','lessons.json',f'{theme}/interior.pdf',f'{theme}/cover.pdf',f'{theme}/cover-config.json',
                   'editorial-review-items.json','review-attestations.json','editorial-review.html',
                   'diagram-models.json','model-editorial-review.json')
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

    def test_review_evidence_cannot_be_removed_from_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            path=root/'playful-illustrated/handoff.json'
            report=json.loads(path.read_text())
            del report['files']['model-editorial-review.json']
            path.write_text(json.dumps(report))
            self.assertTrue(any('missing inventory entry model-editorial-review.json' in e for e in verify(root)['errors']))

    def test_cover_configuration_must_be_bound_to_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            path=root/'playful-illustrated/handoff.json'
            report=json.loads(path.read_text())
            del report['files']['playful-illustrated/cover-config.json']
            path.write_text(json.dumps(report))
            (root/'playful-illustrated/cover-config.json').write_text('{"paper_stock":"bw-white"}')
            result=verify(root)
            self.assertFalse(result['ok'])
            self.assertTrue(any('missing inventory entry playful-illustrated/cover-config.json' in e for e in result['errors']))
