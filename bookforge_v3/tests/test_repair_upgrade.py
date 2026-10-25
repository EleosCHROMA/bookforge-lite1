import json
import unittest
from bookforge_v3.pipeline import ROOT,validate_project
from bookforge_v3.build_repair_draft import create
from bookforge_v3.repair_upgrade import audit,upgrade,CASES
from bookforge_v3.quality import analyze

class RepairUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.original=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
    def test_repaired_draft(self):
        book=create(self.original)
        self.assertEqual(sum(len(c["problems"]) for c in book["chapters"]),132)
        self.assertEqual(sum(len(c["repair_tickets"]) for c in book["chapters"]),11)
        self.assertEqual(audit(book)["checked"],5)
        validate_project(book)
        quality=analyze(book)
        self.assertTrue(quality["ready_for_build"],quality["errors"])
        self.assertFalse(quality["ready_for_publication"])
    def test_source_not_mutated(self):
        create(self.original)
        self.assertEqual(sum(len(c["repair_tickets"]) for c in self.original["chapters"]),6)
    def test_tampered_answer_fails(self):
        book=create(self.original)
        book["chapters"][1]["repair_tickets"][-1]["answer"]="25 dollars"
        with self.assertRaisesRegex(ValueError,"Incorrect repair-ticket solution"):
            audit(book)
        self.assertFalse(analyze(book)["ready_for_build"])
    def test_repeated_upgrade_fails(self):
        book=create(self.original)
        with self.assertRaises(ValueError):upgrade(book)
    def test_bank_size_and_location(self):
        book=create(self.original)
        self.assertEqual(len(CASES),5)
        self.assertEqual([len(c["repair_tickets"]) for c in book["chapters"]],[2,2,2,2,2,2])
