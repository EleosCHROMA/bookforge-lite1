import json
import unittest
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_132 import create
from bookforge_v3.review_queue import review_queue

class EditorialInventoryTests(unittest.TestCase):
    def test_expanded_draft_has_explicit_pending_exercises(self):
        base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        draft=create(base)
        result=review_queue(draft)
        self.assertEqual(result["total_problems"],132)
        self.assertEqual(result["numeric_check_records"],93)
        self.assertEqual(len(result["fraction_bank_problem_ids"]),12)
        self.assertEqual(result["unverified_count"],0)
        self.assertEqual(result["human_review_required_count"],132)
        self.assertTrue(any(q["id"].startswith("context_") for q in result["human_review_required_exercises"]))
    def test_reference_draft_unverified_count(self):
        base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        result=review_queue(base)
        self.assertEqual(result["total_problems"],36)
        self.assertEqual(result["unverified_count"],0)
        self.assertEqual(result["human_review_required_count"],36)
