import json
import sys
import tempfile
import unittest
from pathlib import Path
from reportlab.pdfgen import canvas
from pypdf import PdfReader
from bookforge_v3.pipeline import ROOT, V2_ROOT

sys.path.insert(0,str(V2_ROOT))
from themes import fonts, ticket_page

class NoDiagnosisSpoilersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fonts()
    def test_student_ticket_prompts_without_revealing_diagnosis(self):
        project=json.loads((ROOT/"data/mistake_mechanics_six_chapters.json").read_text(encoding="utf-8"))
        chapter=project["chapters"][0]
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"ticket.pdf"
            c=canvas.Canvas(str(path),pagesize=(612,792))
            ticket_page(c,chapter,3,"playful-illustrated")
            c.save()
            text=PdfReader(str(path)).pages[0].extract_text()
        self.assertIn("YOUR DIAGNOSIS",text)
        self.assertIn("What went wrong?",text)
        self.assertNotIn(chapter["repair_tickets"][0]["diagnosis"],text)
        self.assertIn(chapter["repair_tickets"][0]["faulty_work"],text)
