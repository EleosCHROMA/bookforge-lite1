import json
import unittest
from bookforge_v3.pipeline import ROOT
from bookforge_v3.expand_workbook import expand
from bookforge_v3.fraction_enrichment import enrich
from bookforge_v3.fraction_audit import audit_fraction_bank
from bookforge_v3.quality import analyze

class FractionAuditTests(unittest.TestCase):
    def setUp(self):
        base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        self.draft=enrich(expand(base))
    def test_120_draft(self):
        self.assertEqual(sum(len(c["problems"]) for c in self.draft["chapters"]),120)
        self.assertEqual(audit_fraction_bank(self.draft)["checked"],12)
        report=analyze(self.draft)
        self.assertTrue(report["ready_for_build"],report["errors"])
        self.assertEqual(report["statistics"]["fraction_checks"],12)
        self.assertEqual(report["statistics"]["math_checks"],93)
        self.assertEqual(report["statistics"]["math_checks_remaining"],15)
    def test_corrupt_fraction_answer_rejected(self):
        self.draft["chapters"][0]["answers"]["fraction_division_01"]="3/8"
        with self.assertRaisesRegex(ValueError,"mismatch"):
            audit_fraction_bank(self.draft)
        self.assertFalse(analyze(self.draft)["ready_for_build"])
    def test_missing_fraction_problem_rejected(self):
        self.draft["chapters"][0]["problems"]=[p for p in self.draft["chapters"][0]["problems"]
            if p["id"]!="fraction_division_01"]
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            audit_fraction_bank(self.draft)
    def test_original_without_bank(self):
        self.draft["chapters"][0]["problems"]=[p for p in self.draft["chapters"][0]["problems"]
            if not p["id"].startswith("fraction_division_")]
        self.assertEqual(audit_fraction_bank(self.draft)["checked"],0)
