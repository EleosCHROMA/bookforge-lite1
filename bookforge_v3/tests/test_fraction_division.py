import json
import unittest
from fractions import Fraction
from bookforge_v3.fraction_division import make_exercises, PAIRS
from bookforge_v3.fraction_enrichment import enrich
from bookforge_v3.pipeline import ROOT, validate_project
from bookforge_v3.quality import analyze

class FractionDivisionTests(unittest.TestCase):
    def setUp(self):
        self.project=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
    def test_exact_answers(self):
        qs=make_exercises()
        self.assertEqual(len(qs),12)
        self.assertEqual(qs[0]["answer"],"1 1/2")
        for (a,b), q in zip(PAIRS,qs):
            answer=Fraction(q["exact_numerator"],q["exact_denominator"])
            self.assertEqual(answer,Fraction(a)/Fraction(b))
    def test_enriched_project(self):
        result=enrich(self.project)
        self.assertEqual(sum(len(c["problems"]) for c in result["chapters"]),48)
        self.assertEqual(len(result["chapters"][0]["repair_tickets"]),2)
        self.assertFalse(analyze(result)["ready_for_publication"])
        validate_project(result)
        self.assertEqual(len(self.project["chapters"][0]["problems"]),6)
    def test_no_repeated_insertion(self):
        with self.assertRaises(ValueError):
            enrich(enrich(self.project))
    def test_candidate_standards_are_not_verified(self):
        from bookforge_v3.standards_audit import report
        result=report(enrich(self.project))
        self.assertEqual(result["standards_verified_in_metadata"],0)
        self.assertIn("6.NS.1",result["standards_without_verified_exercises"])
