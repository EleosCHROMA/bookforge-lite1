import json
import tempfile
import unittest
from pathlib import Path
from reportlab.pdfgen import canvas
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,DictionaryObject
from bookforge_v3.release_manifest import manifest,sha256

class ReleaseManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name)
        self.book=root/"interior.pdf";self.cover=root/"cover.pdf";self.project=root/"project.json"
        c=canvas.Canvas(str(self.book),pagesize=(612,792))
        for _ in range(60):c.showPage()
        c.save()
        c=canvas.Canvas(str(self.cover),pagesize=((17.25+60*.002347)*72,11.25*72))
        c.showPage();c.save()
        pdf=PdfReader(str(self.cover));writer=PdfWriter()
        for page in pdf.pages:
            page["/Resources"][NameObject("/Font")]=DictionaryObject()
            writer.add_page(page)
        with self.cover.open("wb") as f:writer.write(f)
        self.project.write_text(json.dumps({"chapters":[{"problems":[{"id":"p1"}]}]}))
    def tearDown(self):self.temp.cleanup()
    def test_matching_cover_still_blocks_publication(self):
        r=manifest(self.project,self.book,self.cover)
        self.assertTrue(r["ready_for_structural_review"],r["paired_preflight"])
        self.assertFalse(r["ready_for_publication"])
        self.assertEqual(r["exercise_count"],1)
        self.assertTrue(any("editorial approval" in b for b in r["blockers"]))
    def test_stale_cover_dimensions_fail(self):
        c=canvas.Canvas(str(self.cover),pagesize=(17.25*72,11.25*72))
        c.showPage();c.save()
        self.assertFalse(manifest(self.project,self.book,self.cover)["ready_for_structural_review"])
    def test_fingerprint_changes(self):
        previous=sha256(self.project)
        self.project.write_text('{"chapters":[]}')
        self.assertNotEqual(previous,sha256(self.project))
    def test_paper_mismatch_blocked(self):
        config=self.project.parent/"config.json"
        config.write_text(json.dumps({"paper_stock":"bw-white"}))
        result=manifest(self.project,self.book,self.cover,cover_config=config)
        self.assertTrue(any("stock differs" in x for x in result["blockers"]))
