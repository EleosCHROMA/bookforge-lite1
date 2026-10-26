import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.candidate import build
from bookforge_v3.release_manifest import sha256


class CandidateTests(unittest.TestCase):
    def test_complete_candidate_both_styles(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'candidate'
            result = build(folder)
            self.assertTrue(result['engineering_checks_passed'])
            self.assertFalse(result['ready_for_publication'])
            for theme, report in result['themes'].items():
                self.assertEqual(report['guided_lessons'], 6)
                self.assertEqual(report['guided_solutions_checked'], 12)
                self.assertEqual(report['pages'], 64)
                self.assertEqual(report['answer_key_page'], 45)
                self.assertTrue(report['publication_blockers'])
                pdf = PdfReader(folder/theme/'interior.pdf')
                for n, page in enumerate(pdf.pages, 1):
                    footers = []
                    page.extract_text(visitor_text=lambda text, cm, tm, font, size:
                        footers.append(text.strip()) if 15 <= tm[5] <= 40 else None)
                    self.assertIn(str(n), footers)
                handoff = json.loads((folder/theme/'handoff.json').read_text())
                for path, fingerprint in handoff['files'].items():
                    self.assertEqual(sha256(folder/path), fingerprint['sha256'])
                self.assertIn('lessons.json', handoff['files'])

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp)/'keep.txt'
            marker.write_text('keep')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                build(tmp)
            self.assertEqual(marker.read_text(), 'keep')

    def test_missing_chapter_lesson_rejected_before_creating_output(self):
        from bookforge_v3.pipeline import ROOT
        with tempfile.TemporaryDirectory() as tmp:
            spec = json.loads((ROOT/'data/production_lessons.json').read_text())
            spec['lessons'].pop()
            source = Path(tmp)/'lessons.json'
            source.write_text(json.dumps(spec))
            output = Path(tmp)/'candidate'
            with self.assertRaisesRegex(ValueError, 'every chapter'):
                build(output, source)
            self.assertFalse(output.exists())

    def test_failed_audit_never_writes_success_summary(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'candidate'
            with patch('bookforge_v3.candidate.audit', return_value={'ok': False}):
                with self.assertRaisesRegex(ValueError, 'manuscript audit failed'):
                    build(folder)
            self.assertFalse((folder/'candidate-summary.json').exists())
