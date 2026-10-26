import json
import unittest
from pathlib import Path
from bookforge_v3.build_repair_draft import create
from bookforge_v3.standards_audit import report, STANDARDS, ALLOWED_KINDS
from bookforge_v4.content_metadata import annotate

class MetadataTests(unittest.TestCase):
    def test_all_exercises_labeled_without_inventing_reviews(self):
        root=Path(__file__).resolve().parents[2]
        base=create(json.loads((root/'bookforge_v3/data/mistake_mechanics_six_chapters.json').read_text()))
        original=json.dumps(base,sort_keys=True)
        result=annotate(base)
        self.assertEqual(json.dumps(base,sort_keys=True),original)
        self.assertEqual(report(result)['exercises_missing_kind'],[])
        self.assertEqual(report(result)['standards_verified_in_metadata'],0)
        for chapter in result['chapters']:
            for p in chapter['problems']:
                self.assertIn(p['kind'],ALLOWED_KINDS)
                self.assertTrue(set(p['candidate_standards'])<=set(STANDARDS))
                self.assertFalse(p.get('standard_reviewed',False))
                self.assertEqual(p['alignment_proposal']['status'],'PROPOSED_NOT_VERIFIED')
