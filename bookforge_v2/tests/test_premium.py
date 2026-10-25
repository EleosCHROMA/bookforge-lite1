import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from premium import generate
BASE=Path(__file__).resolve().parents[1]
class PremiumTests(unittest.TestCase):
    def setUp(self):self.data=json.loads((BASE/'sample/chapter_full.json').read_text())
    def test_single_chapter(self):
        with tempfile.TemporaryDirectory() as d:
            pdf=generate(self.data,Path(d)/'a.pdf');self.assertEqual(len(PdfReader(str(pdf)).pages),4)
    def test_multi_chapter_answers_at_end(self):
        d2=json.loads(json.dumps(self.data));d2['chapter_number']=2;d2['chapter_title']='Rates and Ratios'
        with tempfile.TemporaryDirectory() as d:
            r=PdfReader(str(generate({'chapters':[self.data,d2]},Path(d)/'b.pdf')))
            self.assertEqual(len(r.pages),8)
            self.assertIn('MASTER MECHANIC',r.pages[6].extract_text())
            self.assertNotIn('MASTER MECHANIC',r.pages[5].extract_text())
    def test_invalid_rejected(self):
        self.data['answers'].pop('p1')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):generate(self.data,Path(d)/'bad.pdf')
if __name__=='__main__':unittest.main()
