import tempfile
import unittest
import json
from pathlib import Path
from bookforge_v4.candidate import build
from bookforge_v4.readiness import audit
from bookforge_v3.release_manifest import sha256

class ReadinessTests(unittest.TestCase):
    def test_saved_candidate_ready_for_engineering_but_not_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'candidate';build(root)
            report=audit(root)
            self.assertTrue(report['engineering_ready'],report['blockers'])
            self.assertFalse(report['ready_for_publication'])
            self.assertEqual(report['editorial_review']['counts']['PENDING'],174)
            preview=Path(tmp)/'preview.json'
            evidence={'theme':'playful-illustrated','review_type':'USER_REPORTED_FINAL_ONLINE_PREVIEW_PASS',
                      'interior_sha256':sha256(root/'playful-illustrated/interior.pdf'),
                      'cover_sha256':sha256(root/'playful-illustrated/cover.pdf')}
            preview.write_text(json.dumps(evidence))
            reviewed=audit(root,preview)
            self.assertEqual(reviewed['preview_status'],'USER_REPORTED_PASS_FOR_MATCHING_PACKAGE')
            self.assertFalse(reviewed['ready_for_publication'])
            self.assertTrue(any('publication approval' in x for x in reviewed['blockers']))
            evidence['cover_sha256']='0'*64
            preview.write_text(json.dumps(evidence))
            self.assertEqual(audit(root,preview)['preview_status'],'STALE_OR_INVALID')
            (root/'lessons.json').write_text('{}')
            changed=audit(root)
            self.assertFalse(changed['engineering_ready'])
            self.assertTrue(any('changed file' in item for item in changed['blockers']))

    def test_missing_package_never_reports_ready(self):
        with tempfile.TemporaryDirectory() as tmp:self.assertFalse(audit(tmp)['engineering_ready'])
