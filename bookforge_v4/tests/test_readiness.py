import tempfile
import unittest
from pathlib import Path
from bookforge_v4.candidate import build
from bookforge_v4.readiness import audit

class ReadinessTests(unittest.TestCase):
    def test_saved_candidate_ready_for_engineering_but_not_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'candidate';build(root)
            report=audit(root)
            self.assertTrue(report['engineering_ready'],report['blockers'])
            self.assertFalse(report['ready_for_publication'])
            self.assertEqual(report['editorial_review']['counts']['PENDING'],174)
            (root/'lessons.json').write_text('{}')
            changed=audit(root)
            self.assertFalse(changed['engineering_ready'])
            self.assertTrue(any('changed file' in item for item in changed['blockers']))

    def test_missing_package_never_reports_ready(self):
        with tempfile.TemporaryDirectory() as tmp:self.assertFalse(audit(tmp)['engineering_ready'])
