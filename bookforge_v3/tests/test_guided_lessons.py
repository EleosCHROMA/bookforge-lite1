import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.lesson_pages import render,validate_lessons
from bookforge_v3.pipeline import ROOT
from bookforge_v3.build_guided import create

LESSONS=ROOT/'data/guided_lessons.json'
PROJECT=ROOT/'data/mistake_mechanics_six_chapters.json'

class GuidedLessonTests(unittest.TestCase):
    def test_three_pages_both_themes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for theme in ('clean-premium','playful-illustrated'):
                pdf=PdfReader(str(render(json.loads(LESSONS.read_text()),Path(tmp)/(theme+'.pdf'),theme)))
                self.assertEqual(len(pdf.pages),3)
                self.assertIn('Fraction Division',pdf.pages[0].extract_text())
                for page in pdf.pages:
                    for ref in page['/Resources']['/Font'].get_object().values():
                        descriptor=ref.get_object().get('/FontDescriptor')
                        self.assertIsNotNone(descriptor)
                        self.assertTrue(any(k in descriptor.get_object() for k in ('/FontFile','/FontFile2','/FontFile3')))
    def test_overflow_fails(self):
        data=json.loads(LESSONS.read_text())
        data['lessons'][0]['title']='OVERFLOW '*75
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):render(data,Path(tmp)/'bad.pdf')
    def test_bad_structure_fails(self):
        with self.assertRaises(ValueError):validate_lessons({'lessons':[{'title':'x'}]})
    def test_workbook_answers_stay_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=create(PROJECT,LESSONS,Path(tmp)/'book.pdf','clean-premium')
            self.assertEqual(result['pages'],27)
            self.assertEqual(result['answer_key_page'],22)
            pdf=PdfReader(str(result['output']))
            self.assertIn('MASTER MECHANIC GUIDE',pdf.pages[-1].extract_text())
            self.assertIn('Fraction Division',pdf.pages[1].extract_text())
            self.assertIn('Statistics: Read the Repair Times',pdf.pages[18].extract_text())
