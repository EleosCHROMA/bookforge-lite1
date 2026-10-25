import tempfile
import unittest
from pathlib import Path
from reportlab.pdfgen import canvas
from bookforge_v3.manuscript_audit import audit

class ManuscriptAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/"book.pdf"
        self.project={"chapters":[{"chapter_number":1,"chapter_title":"Math",
            "problems":[{"id":"p1"}],
            "repair_tickets":[{"id":"1.1","diagnosis":"Forgot to regroup"}]}]}
        self.make_pdf()
    def tearDown(self):self.temp.cleanup()
    def make_pdf(self,student_extra="",answer_extra=""):
        c=canvas.Canvas(str(self.path))
        for content in (
            "CHAPTER 1 - MATH\nGUIDED PRACTICE\nFAULTY WORK\n"+student_extra,
            "CHAPTER 1 - MATH\nMASTER MECHANIC GUIDE\nPRACTICE ANSWERS\n1. 42\nREPAIR TICKET SOLUTIONS\n1.1 Correct\n"+answer_extra):
            for i,line in enumerate(content.split("\n")):c.drawString(50,700-20*i,line)
            c.showPage()
        c.save()
    def test_valid_book(self):
        self.assertTrue(audit(self.path,self.project)["ok"])
    def test_missing_answer_detected(self):
        self.project["chapters"][0]["problems"].append({"id":"p2"})
        self.assertFalse(audit(self.path,self.project)["ok"])
    def test_missing_ticket_solution_detected(self):
        self.project["chapters"][0]["repair_tickets"].append({"id":"1.2"})
        self.assertFalse(audit(self.path,self.project)["ok"])
    def test_lesson_missing_detected(self):
        self.assertFalse(audit(self.path,self.project,["Fraction Division"])["ok"])
    def test_answer_leak_detected(self):
        self.make_pdf(student_extra="PRACTICE ANSWERS")
        self.assertFalse(audit(self.path,self.project)["ok"])
    def test_revealed_diagnosis_detected(self):
        self.make_pdf(student_extra="Forgot to regroup")
        result=audit(self.path,self.project)
        self.assertFalse(result["ok"])
        self.assertTrue(any("reveals" in x for x in result["errors"]))
