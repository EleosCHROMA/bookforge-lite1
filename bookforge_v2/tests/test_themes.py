import json,tempfile,unittest
from pathlib import Path
from pypdf import PdfReader
from themes import generate
ROOT=Path(__file__).resolve().parents[1]
class ThemeTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((ROOT/'sample/chapter_full.json').read_text(encoding='utf-8'))
 def test_both_themes(self):
  with tempfile.TemporaryDirectory() as t:
   for theme in ('clean-premium','playful-illustrated'):
    r=PdfReader(str(generate(self.data,Path(t)/(theme+'.pdf'),theme)))
    self.assertEqual(len(r.pages),4)
    self.assertIn('GUIDED PRACTICE' if theme=='playful-illustrated' else 'Practice & progress',r.pages[1].extract_text())
 def test_answers_last(self):
  d=json.loads(json.dumps(self.data));d['chapter_number']=2
  with tempfile.TemporaryDirectory() as t:
   r=PdfReader(str(generate({'chapters':[self.data,d]},Path(t)/'b.pdf','playful-illustrated')))
   self.assertEqual(len(r.pages),8)
   self.assertIn('MASTER MECHANIC',r.pages[6].extract_text())
 def test_invalid_theme(self):
  with self.assertRaises(ValueError):generate(self.data,'/tmp/no.pdf','unknown')
if __name__=='__main__':unittest.main()
