import json
import unittest
from copy import deepcopy
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_repair_draft import create
from bookforge_v3.ticket_inventory import inventory

class TicketInventoryTests(unittest.TestCase):
    def setUp(self):
        source=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        self.book=create(source)
    def test_twelve_tickets_two_in_each_chapter(self):
        result=inventory(self.book,expected_per_chapter=2)
        self.assertTrue(result["ok"],result["errors"])
        self.assertEqual(result["total_tickets"],12)
        self.assertEqual(list(result["counts_by_chapter"].values()),[2]*6)
        self.assertEqual(result["editorial_status"],"UNREVIEWED")
    def test_duplicate_ids_rejected(self):
        bad=deepcopy(self.book)
        bad["chapters"][1]["repair_tickets"][0]["id"]=bad["chapters"][0]["repair_tickets"][0]["id"]
        result=inventory(bad,expected_per_chapter=2)
        self.assertFalse(result["ok"])
        self.assertTrue(any("Duplicate ticket ID" in x for x in result["errors"]))
    def test_missing_solution_rejected(self):
        bad=deepcopy(self.book)
        bad["chapters"][2]["repair_tickets"][1]["answer"]=""
        self.assertFalse(inventory(bad,expected_per_chapter=2)["ok"])
    def test_different_existing_book_is_not_forced_to_two_tickets(self):
        base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        result=inventory(base)
        self.assertTrue(result["ok"],result["errors"])
        self.assertEqual(result["total_tickets"],6)
