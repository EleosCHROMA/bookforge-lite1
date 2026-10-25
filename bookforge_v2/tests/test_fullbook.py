import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from fullbook import generate_book, validate_book
SAMPLE = Path(__file__).resolve().parents[1] / 'sample' / 'chapter_full.json'
class FullBookTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(SAMPLE.read_text(encoding='utf-8'))
    def test_valid(self):
        self.assertIs(validate_book(self.data), self.data)
    def test_missing_answer(self):
        del self.data['answers']['p2']
        with self.assertRaisesRegex(ValueError, 'answers must match'):
            validate_book(self.data)
    def test_duplicate_ticket_id(self):
        self.data['repair_tickets'][1]['id'] = 'p1'
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate_book(self.data)
    def test_four_pages_answers_last_and_fonts(self):
        with tempfile.TemporaryDirectory() as td:
            pdf = PdfReader(str(generate_book(self.data, Path(td)/'book.pdf')))
            self.assertEqual(len(pdf.pages), 4)
            self.assertIn('REPAIR TICKETS', pdf.pages[2].extract_text())
            self.assertIn('MASTER MECHANIC GUIDE', pdf.pages[3].extract_text())
            self.assertNotIn('MASTER MECHANIC GUIDE', pdf.pages[1].extract_text())
            for page in pdf.pages:
                self.assertEqual(tuple(map(float,page.mediabox[2:])), (612.,792.))
                for ref in page['/Resources']['/Font'].get_object().values():
                    obj=ref.get_object()
                    self.assertNotEqual(str(obj.get('/BaseFont')), '/Helvetica')
                    desc=obj.get('/FontDescriptor')
                    self.assertIsNotNone(desc)
                    self.assertTrue(any(k in desc.get_object() for k in ('/FontFile','/FontFile2','/FontFile3')))
if __name__ == '__main__': unittest.main()
