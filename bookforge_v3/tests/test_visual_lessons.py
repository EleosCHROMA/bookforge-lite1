import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from bookforge_v3.visual_lessons import generate
from bookforge_v3.visual_book import insert_visual_lessons

class VisualLessonTests(unittest.TestCase):
    def test_three_embedded_font_pages(self):
        with tempfile.TemporaryDirectory() as t:
            result=PdfReader(str(generate(Path(t)/'lessons.pdf')))
            self.assertEqual(len(result.pages),3)
            self.assertIn('3/4',result.pages[0].extract_text())
            self.assertIn('x > -2',result.pages[1].extract_text())
            self.assertIn('Mode: 4',result.pages[2].extract_text())
            for page in result.pages:
                for ref in page['/Resources']['/Font'].get_object().values():
                    desc=ref.get_object().get('/FontDescriptor')
                    self.assertIsNotNone(desc)
                    self.assertTrue(any(k in desc.get_object() for k in ('/FontFile','/FontFile2','/FontFile3')))
    def test_visuals_appear_before_answers(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'src.pdf';c=canvas.Canvas(str(src))
            c.drawString(50,650,'PRACTICE WORKSHEET');c.showPage()
            c.drawString(50,650,'MASTER MECHANIC GUIDE');c.showPage();c.save()
            result=insert_visual_lessons(src,Path(t)/'book.pdf')
            pdf=PdfReader(result['output'])
            self.assertEqual(len(pdf.pages),5)
            self.assertEqual(result['answer_key_starts_at'],5)
            self.assertIn('Fraction Division',pdf.pages[1].extract_text())
            self.assertIn('MASTER MECHANIC GUIDE',pdf.pages[-1].extract_text())
    def test_missing_answer_heading_fails_safe(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'src.pdf';c=canvas.Canvas(str(src));c.drawString(50,650,'INCOMPLETE');c.save()
            with self.assertRaises(ValueError):
                insert_visual_lessons(src,Path(t)/'out.pdf')
