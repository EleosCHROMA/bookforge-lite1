import json
import unittest
from bookforge_v3.pipeline import ROOT
from bookforge_v3.quality import analyze

def sample():
    return json.loads((ROOT / "data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))

class QualityTests(unittest.TestCase):
    def test_sample_not_publication_ready(self):
        result = analyze(sample())
        self.assertTrue(result["ready_for_build"])
        self.assertFalse(result["ready_for_publication"])
        self.assertEqual(result["statistics"]["exercises"], 36)
        self.assertEqual(result["statistics"]["math_checks"], 21)
    def test_duplicate_id_rejected(self):
        data = sample()
        data["chapters"][1]["problems"][0]["id"] = "c1p1"
        self.assertIn("Duplicate exercise ID: c1p1", analyze(data)["errors"])
    def test_wrong_math_rejected(self):
        data = sample()
        data["math_checks"][0]["expected"] = "100000"
        self.assertFalse(analyze(data)["ready_for_build"])
    def test_long_text_warning(self):
        data = sample()
        data["chapters"][0]["problems"][0]["prompt"] = "long " * 40
        self.assertTrue(any("Long prompt" in x for x in analyze(data)["warnings"]))
    def test_editorial_review_gate(self):
        data = sample()
        data["editorial_review"] = dict.fromkeys(("mathematics", "pedagogy", "proofreading", "print_preview"), True)
        self.assertTrue(analyze(data)["ready_for_publication"])
