import json
import unittest
from bookforge_v3.math_audit import audit, evaluate
from bookforge_v3.pipeline import ROOT

class ArithmeticTests(unittest.TestCase):
    def test_fractional_arithmetic(self):
        self.assertEqual(str(evaluate("9.36/0.3")),"31.2")
    def test_reject_unsafe_input(self):
        with self.assertRaises(ValueError): evaluate('__import__("os").system("whoami")')
    def test_checked_21_examples(self):
        project=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        report=audit(project)
        self.assertEqual(report["checked"],21)
        self.assertEqual(report["total"],36)
    def test_wrong_answer_detected(self):
        project=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        project["math_checks"][0]["expected"]="1000"
        with self.assertRaises(ValueError): audit(project)
