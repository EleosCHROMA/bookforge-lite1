import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.native_book import assemble
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_132 import create as expand_132

BASE=ROOT/"data/mistake_mechanics_six_chapters.json"
LESSONS=ROOT/"data/guided_lessons.json"

class NativeBookTests(unittest.TestCase):
    def test_original_book_both_styles(self):
        with tempfile.TemporaryDirectory() as t:
            for theme in ("clean-premium","playful-illustrated"):
                result=assemble(BASE,LESSONS,Path(t)/(theme+".pdf"),theme)
                self.assertEqual(result["pages"],28)
                self.assertEqual(result["answer_key_page"],22)
                pdf=PdfReader(result["output"])
                self.assertIn("Fraction Division",pdf.pages[1].extract_text())
                self.assertIn("MASTER MECHANIC GUIDE",pdf.pages[21].extract_text())
                self.assertNotIn("page_numbering",result)
    def test_expanded_132_questions(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"132.json"
            base=json.loads(BASE.read_text(encoding="utf-8"))
            draft=expand_132(base)
            self.assertEqual(sum(len(x["problems"]) for x in draft["chapters"]),132)
            path.write_text(json.dumps(draft),encoding="utf-8")
            result=assemble(path,LESSONS,Path(t)/"large.pdf","clean-premium")
            self.assertGreater(result["pages"],40)
            self.assertEqual(result["answer_key_page"],42)
            reader=PdfReader(result["output"])
            self.assertIn("MASTER MECHANIC GUIDE",reader.pages[41].extract_text())
    def test_invalid_lesson_chapter_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            spec=json.loads(LESSONS.read_text(encoding="utf-8"))
            spec["lessons"][0]["chapter_number"]=100
            path=Path(t)/"lessons.json"
            path.write_text(json.dumps(spec))
            with self.assertRaises(ValueError):
                assemble(BASE,path,Path(t)/"invalid.pdf")
