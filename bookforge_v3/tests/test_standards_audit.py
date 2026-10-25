import json
import unittest
from bookforge_v3.pipeline import ROOT
from bookforge_v3.standards_audit import report, STANDARDS

class StandardsAuditTests(unittest.TestCase):
    def setUp(self):
        self.project=json.loads((ROOT/'data/mistake_mechanics_six_chapters.json').read_text(encoding='utf-8'))
    def test_unreviewed_is_not_coverage(self):
        r=report(self.project)
        self.assertEqual(r['standards_verified_in_metadata'],0)
        self.assertIn('6.NS.1', r['standards_without_verified_exercises'])
        self.assertEqual(len(STANDARDS),29)
    def test_candidate_tags_do_not_count(self):
        self.project['chapters'][0]['problems'][0]['verified_standards']=['6.NS.3']
        self.assertEqual(report(self.project)['standards_verified_in_metadata'],0)
    def test_editor_verified_tag_counts(self):
        problem=self.project['chapters'][0]['problems'][0]
        problem['verified_standards']=['6.NS.3']
        problem['standard_reviewed']=True
        self.assertEqual(report(self.project)['standards_with_verified_exercises'], ['6.NS.3'])
    def test_invalid_tag_flag(self):
        problem=self.project['chapters'][0]['problems'][0]
        problem['verified_standards']=['6.BAD.999']
        problem['standard_reviewed']=True
        self.assertIn('c1p1',report(self.project)['invalid_or_unreviewed_standard_tags'])
    def test_duplicate_prompt(self):
        self.project['chapters'][1]['problems'][0]['prompt']='12.4 + 8.75'
        self.assertIn(('c1p1','c2p1'),report(self.project)['duplicate_prompt_pairs'])
