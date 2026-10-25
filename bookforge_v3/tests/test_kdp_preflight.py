import tempfile
import unittest
from pathlib import Path
from reportlab.pdfgen import canvas
from bookforge_v3.kdp_preflight import audit_pdf
from bookforge_v3.pipeline import ROOT, build

class KDPPreflightTests(unittest.TestCase):
    def test_six_chapter_pdf(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'book.pdf'
            build(ROOT/'data/mistake_mechanics_six_chapters.json',path)
            report=audit_pdf(path)
            self.assertTrue(report['ok'],report['errors'])
            self.assertEqual(report['required_inside_margin_in'],.375)
    def test_wrong_trim_and_short_book(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'bad.pdf'
            c=canvas.Canvas(str(path),pagesize=(432,648))
            c.drawString(30,400,'short')
            c.showPage()
            c.save()
            report=audit_pdf(path)
            self.assertFalse(report['ok'])
            self.assertTrue(any('page count' in x.lower() for x in report['errors']))
            self.assertTrue(any('size' in x.lower() for x in report['errors']))
    def test_no_bleed_pdf_cannot_pass_bleed_preflight(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'book.pdf'
            build(ROOT/'data/mistake_mechanics_six_chapters.json',path)
            self.assertFalse(audit_pdf(path,bleed=True)['ok'])
    def test_gutter_rules(self):
        from bookforge_v3.kdp_preflight import GUTTER_RULES
        self.assertEqual(GUTTER_RULES[0],(150,.375))
        self.assertEqual(GUTTER_RULES[-1],(828,.875))
