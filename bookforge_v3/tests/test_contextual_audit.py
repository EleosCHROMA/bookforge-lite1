import json
import unittest
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_132 import create
from bookforge_v3.contextual_audit import verify, _expected
from bookforge_v3.quality import analyze

class ContextualAnswerAuditTests(unittest.TestCase):
    def setUp(self):
        base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        self.project=create(base)
    def test_all_twelve_recomputed(self):
        self.assertEqual(verify(self.project)["checked"],12)
        self.assertEqual(len(_expected()),12)
        report=analyze(self.project)
        self.assertTrue(report["ready_for_build"],report["errors"])
        self.assertEqual(report["statistics"]["contextual_checks"],12)
        self.assertEqual(report["statistics"]["math_checks_remaining"],0)
        self.assertFalse(report["ready_for_publication"])
    def test_money_is_not_scientific_notation(self):
        self.assertEqual(_expected()["context_2_02"], "$60")
        self.assertEqual(_expected()["context_5_01"], "7.5 cubic feet")
    def test_tampered_answer_blocked(self):
        self.project["chapters"][1]["answers"]["context_2_02"]="$80. A faulty calculation."
        with self.assertRaisesRegex(ValueError,"computed answer mismatch"):
            verify(self.project)
        self.assertFalse(analyze(self.project)["ready_for_build"])
    def test_tampered_explanation_blocked(self):
        self.project["chapters"][0]["answers"]["context_1_01"]="6. A completely different explanation."
        with self.assertRaisesRegex(ValueError,"explanation changed"):
            verify(self.project)
    def test_partial_bank_blocked(self):
        ch=self.project["chapters"][0]
        ch["problems"]=[p for p in ch["problems"] if p["id"]!="context_1_01"]
        ch["answers"].pop("context_1_01")
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            verify(self.project)
    def test_standalone_fraction_bank_unaffected(self):
        base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        self.assertEqual(verify(base)["checked"],0)
