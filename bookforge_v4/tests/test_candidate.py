import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
from bookforge_v4.candidate import build


class VisualCandidateTests(unittest.TestCase):
    def test_both_styles_keep_complete_answer_keys_and_pass_geometry(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'candidate'
            result=build(output)
            self.assertEqual(result['version'],4)
            self.assertEqual(result['development_status'],'AWAITING_EXTERNAL_REVIEW')
            self.assertFalse(result['ready_for_publication'])
            self.assertEqual(result['visual_models'],6)
            self.assertEqual(result['editorial_items'],174)
            self.assertEqual(result['editorial_status_counts']['PENDING'],174)
            self.assertEqual(json.loads((output/'review-attestations.json').read_text()),{})
            for theme,report in result['themes'].items():
                self.assertEqual(report['pages'],64)
                self.assertEqual(report['answer_key_page'],45)
                self.assertEqual(report['guided_solutions_checked'],12)
                self.assertTrue(report['text_geometry_passed'])
                self.assertGreater(report['glyphs_checked'],20000)
                pdf=PdfReader(output/theme/'interior.pdf')
                self.assertIn('GUIDED LESSON SOLUTIONS',pdf.pages[-1].extract_text())
                self.assertIn('4x3',pdf.pages[31].extract_text())
                self.assertNotIn('DRAFT', ' '.join(page.extract_text() or '' for page in pdf.pages).upper())
                cover=PdfReader(output/theme/'cover.pdf')
                self.assertNotIn('DRAFT', ' '.join(page.extract_text() or '' for page in cover.pages).upper())

    def test_geometry_failure_removes_v3_success_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'candidate'
            with patch('bookforge_v4.candidate.geometry_audit',return_value={'ok':False}):
                with self.assertRaisesRegex(ValueError,'geometry preflight failed'):
                    build(output)
            self.assertFalse((output/'candidate-summary.json').exists())
