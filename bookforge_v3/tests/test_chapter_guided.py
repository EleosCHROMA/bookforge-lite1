import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_guided import create
from bookforge_v3.chapter_guided import chapter_boundaries

PROJECT=ROOT/'data/mistake_mechanics_six_chapters.json'
LESSONS=ROOT/'data/guided_lessons.json'

class ChapterPlacementTests(unittest.TestCase):
    def test_insertions_and_answer_key_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'book.pdf'
            result=create(PROJECT,LESSONS,output,'playful-illustrated')
            reader=PdfReader(result['output'])
            self.assertEqual(result['pages'],27)
            self.assertEqual(result['answer_key_page'],22)
            self.assertIn('Fraction Division',reader.pages[1].extract_text())
            self.assertIn('Inequalities',reader.pages[8].extract_text())
            self.assertIn('Statistics:',reader.pages[18].extract_text())
            self.assertIn('MASTER MECHANIC GUIDE',reader.pages[21].extract_text())
            self.assertTrue(result['kdp_preflight']['ok'])
    def test_corrupt_boundary_is_rejected(self):
        project=json.loads(PROJECT.read_text(encoding='utf-8'))
        with self.assertRaises(ValueError):
            chapter_boundaries(project,24,17)
    def test_all_pages_pass_font_preflight(self):
        with tempfile.TemporaryDirectory() as folder:
            result=create(PROJECT,LESSONS,Path(folder)/'book.pdf','clean-premium')
            self.assertTrue(result['kdp_preflight']['ok'])
            self.assertEqual(len(PdfReader(result['output']).pages),27)
