import json
import unittest
from bookforge_v3.pipeline import ROOT, validate_project
from bookforge_v3.build_132 import create
from bookforge_v3.contextual_enrichment import CONTEXTUAL, enrich_context
from bookforge_v3.quality import analyze
from bookforge_v3.standards_audit import report

class ContextualEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.base=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
    def test_twelve_contextual_tasks(self):
        draft=create(self.base)
        self.assertEqual(sum(len(c["problems"]) for c in draft["chapters"]),132)
        self.assertEqual(sum(p["id"].startswith("context_") for c in draft["chapters"] for p in c["problems"]),12)
        self.assertEqual(len({p["id"] for c in draft["chapters"] for p in c["problems"]}),132)
        self.assertEqual(len(CONTEXTUAL),12)
        validate_project(draft)
        qa=analyze(draft)
        self.assertTrue(qa["ready_for_build"],qa["errors"])
        self.assertFalse(qa["ready_for_publication"])
        self.assertEqual(qa["statistics"]["math_checks"],93)
        self.assertEqual(qa["statistics"]["fraction_checks"],12)
    def test_source_unchanged(self):
        enrich_context(self.base)
        self.assertEqual(len(self.base["chapters"][0]["problems"]),6)
    def test_no_false_standards_certification(self):
        self.assertEqual(report(create(self.base))["standards_verified_in_metadata"],0)
    def test_repeated_enrichment_rejected(self):
        data=enrich_context(self.base)
        with self.assertRaisesRegex(ValueError,"already added"):
            enrich_context(data)
    def test_chapter_balance(self):
        draft=create(self.base)
        counts=[len(c["problems"]) for c in draft["chapters"]]
        self.assertEqual(counts,[32,20,20,20,20,20])
        self.assertTrue(all(len(c["repair_tickets"])>=1 for c in draft["chapters"]))
