import copy
import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from themes import generate
from layout import worksheet_batches, section_page_count

ROOT = Path(__file__).resolve().parents[1]

class PaginationTests(unittest.TestCase):
    def setUp(self):
        self.chapter = json.loads((ROOT/'sample/chapter_full.json').read_text(encoding='utf-8'))

    def make_chapter(self, number, count):
        chapter = copy.deepcopy(self.chapter)
        chapter['chapter_number'] = number
        chapter['problems'] = []
        chapter['answers'] = {}
        for i in range(count):
            key = f'c{number}p{i+1}'
            chapter['problems'].append({'id':key,'prompt':f'Calculate {i+1} + 2.'})
            chapter['answers'][key] = str(i+3)
        return chapter

    def test_pagination(self):
        self.assertEqual([len(x) for x in worksheet_batches(list(range(14)))],[6,6,2])
        self.assertEqual(section_page_count(self.make_chapter(1,14)),5)

    def test_twelve_problems_two_themes(self):
        with tempfile.TemporaryDirectory() as td:
            for theme in ('clean-premium','playful-illustrated'):
                p = generate(self.make_chapter(1,12),Path(td)/f'{theme}.pdf',theme)
                pages = PdfReader(str(p)).pages
                self.assertEqual(len(pages),6)
                self.assertIn('REPAIR TICKET',pages[3].extract_text())
                self.assertIn('MASTER MECHANIC',pages[4].extract_text())
                self.assertIn('MASTER MECHANIC',pages[5].extract_text())

    def test_thirty_six_questions_answer_pagination(self):
        with tempfile.TemporaryDirectory() as td:
            for theme in ('clean-premium', 'playful-illustrated'):
                pdf = PdfReader(str(generate(self.make_chapter(1,36), Path(td)/f'{theme}-long.pdf', theme)))
                # one opener, six worksheets, one repair page, four answer pages
                self.assertEqual(len(pdf.pages), 12)
                texts = [p.extract_text() for p in pdf.pages]
                self.assertIn('REPAIR TICKET', texts[7])
                for answer_text in texts[8:]:
                    self.assertIn('MASTER MECHANIC', answer_text)
                self.assertIn('28.', texts[11])
                self.assertIn('36.', texts[11])

    def test_multi_chapter_answers_last(self):
        with tempfile.TemporaryDirectory() as td:
            chapters=[self.make_chapter(1,8),self.make_chapter(2,12)]
            pdf = PdfReader(str(generate({'chapters':chapters},Path(td)/'multi.pdf')))
            self.assertEqual(len(pdf.pages),11)
            self.assertIn('MASTER MECHANIC',pdf.pages[8].extract_text())
            self.assertIn('MASTER MECHANIC',pdf.pages[9].extract_text())

if __name__ == '__main__': unittest.main()
