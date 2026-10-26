import json
import unittest
from pathlib import Path
from bookforge_v3.build_repair_draft import create
from bookforge_v4.content_metadata import annotate
from bookforge_v4.review_packet import create as packet
from bookforge_v4.model_review import report

class ModelReviewTests(unittest.TestCase):
    def test_current_findings_and_stale_sources_remain_separate_from_approval(self):
        root=Path(__file__).resolve().parents[2]
        book=annotate(create(json.loads((root/'bookforge_v3/data/mistake_mechanics_six_chapters.json').read_text())))
        lessons=json.loads((root/'bookforge_v4/data/lessons.json').read_text())
        p=packet(book,lessons);r=report(p)
        self.assertEqual(r['current_model_reviews'],174)
        self.assertEqual(r['human_approvals_granted'],0)
        p['items'][0]['content_sha256']='changed'
        r=report(p)
        self.assertEqual(r['current_model_reviews'],173)
        self.assertEqual(r['remaining_item_ids'],[p['items'][0]['id']])
