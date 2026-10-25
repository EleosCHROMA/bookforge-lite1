import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from pipeline import build, validate_project, ROOT
SAMPLE = ROOT / "data/mistake_mechanics_six_chapters.json"

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    def test_six_chapters(self):
        self.assertEqual(len(validate_project(self.data)["chapters"]), 6)
    def test_duplicate_chapter_numbers(self):
        self.data["chapters"][1]["chapter_number"] = 1
        with self.assertRaises(ValueError): validate_project(self.data)
    def test_missing_answer(self):
        self.data["chapters"][0]["answers"].pop("c1p1")
        with self.assertRaises(ValueError): validate_project(self.data)
    def test_unknown_theme(self):
        self.data["theme"] = "invalid"
        with self.assertRaises(ValueError): validate_project(self.data)
    def test_both_themes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for theme in ("clean-premium", "playful-illustrated"):
                result = build(SAMPLE, Path(tmp) / (theme+".pdf"), theme)
                pdf = PdfReader(result["output"])
                self.assertEqual(len(pdf.pages), 24)
                self.assertEqual(result["chapters"], 6)
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                self.assertIn("MASTER MECHANIC GUIDE", text)
                first_answer = next(i for i,p in enumerate(pdf.pages) if "MASTER MECHANIC GUIDE" in (p.extract_text() or ""))
                self.assertEqual(first_answer, 18)
