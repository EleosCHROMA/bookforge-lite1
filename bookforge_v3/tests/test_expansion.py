import json
import tempfile
import unittest
from pathlib import Path
from bookforge_v3.expand_workbook import expand
from bookforge_v3.pipeline import ROOT, build
from bookforge_v3.quality import analyze
from bookforge_v3.kdp_preflight import audit_pdf

class ExpansionTests(unittest.TestCase):
    def setUp(self):
        self.base=json.loads((ROOT/'data/mistake_mechanics_six_chapters.json').read_text(encoding='utf-8'))
    def test_expanded_math_audit(self):
        project=expand(self.base)
        self.assertEqual(sum(len(c['problems']) for c in project['chapters']),108)
        report=analyze(project)
        self.assertTrue(report['ready_for_build'],report['errors'])
        self.assertEqual(report['statistics']['math_checks'],93)
        self.assertFalse(report['ready_for_publication'])
    def test_two_themes_and_preflight(self):
        project=expand(self.base)
        with tempfile.TemporaryDirectory() as t:
            d=Path(t)
            path=d/'draft.json'
            path.write_text(json.dumps(project),encoding='utf-8')
            for theme in ('clean-premium','playful-illustrated'):
                pdf=d/(theme+'.pdf')
                result=build(path,pdf,theme)
                self.assertEqual(result['pages'],42)
                self.assertTrue(audit_pdf(pdf)['ok'])
