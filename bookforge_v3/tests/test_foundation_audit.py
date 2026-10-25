import json
import unittest
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_132 import create
from bookforge_v3.foundation_audit import verify, CASES
from bookforge_v3.quality import analyze

class FoundationAuditTests(unittest.TestCase):
    def setUp(self):
        self.base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
    def test_all_original_unchecked_answers_now_calculated(self):
        result=verify(self.base)
        self.assertEqual(result["checked"],15)
        self.assertEqual(len(CASES),15)
    def test_132_draft_has_complete_automated_answer_checks(self):
        draft=create(self.base)
        stats=analyze(draft)["statistics"]
        self.assertEqual(stats["foundation_checks"],15)
        self.assertEqual(stats["math_checks_remaining"],0)
        self.assertFalse(analyze(draft)["ready_for_publication"])
    def test_corrupted_ratio_answer_fails(self):
        self.base["chapters"][1]["answers"]["c2p1"]="8:12"
        with self.assertRaisesRegex(ValueError,"mismatch"):
            verify(self.base)
        self.assertFalse(analyze(self.base)["ready_for_build"])
    def test_tampered_prompt_fails(self):
        self.base["chapters"][3]["problems"][2]["prompt"]="Different coordinates"
        with self.assertRaisesRegex(ValueError,"prompt changed"):
            verify(self.base)
    def test_missing_foundation_answer_key_fails(self):
        self.base["chapters"][5]["problems"]=[p for p in self.base["chapters"][5]["problems"] if p["id"]!="c6p3"]
        self.base["chapters"][5]["answers"].pop("c6p3")
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            verify(self.base)
