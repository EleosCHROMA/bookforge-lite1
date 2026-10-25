import json
import unittest
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_132 import create
from bookforge_v3.release_gate import evaluate

class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        self.draft=create(base)
    def test_draft_not_releasable(self):
        outcome=evaluate(self.draft)
        self.assertFalse(outcome["ready_for_release"])
        self.assertEqual(outcome["exercise_reviews_required"],132)
        self.assertTrue(any("human attestation" in x for x in outcome["blockers"]))
        self.assertTrue(any("No final interior PDF" in x for x in outcome["blockers"]))
    def test_cover_is_required_for_release(self):
        result=evaluate(self.draft)
        self.assertIn("No matching cover PDF provided",result["blockers"])
        self.assertIsNone(result["cover_preflight"])
    def test_full_curriculum_claim_must_be_supported(self):
        outcome=evaluate(self.draft,require_full_curriculum=True)
        self.assertTrue(any("Comprehensive Grade 6" in x for x in outcome["blockers"]))
    def test_unknown_approval_is_not_sufficient(self):
        self.draft["release_approvals"]={"mathematics":True,"pedagogy":True,
            "proofreading":True,"print_preview":True}
        result=evaluate(self.draft)
        self.assertTrue(any("Missing human attestation" in x for x in result["blockers"]))
