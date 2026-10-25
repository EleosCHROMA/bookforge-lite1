import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from generate import generate, validate

SAMPLE = Path(__file__).resolve().parents[1] / 'sample' / 'chapter.json'

class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(SAMPLE.read_text(encoding='utf-8'))

    def test_valid_sample(self):
        self.assertIs(validate(self.data), self.data)

    def test_missing_required_field(self):
        del self.data['chapter_title']
        with self.assertRaisesRegex(ValueError, 'chapter_title'):
            validate(self.data)

    def test_duplicate_ids(self):
        self.data['problems'][1]['id'] = 'p1'
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate(self.data)

    def test_too_many_problems(self):
        self.data['problems'] *= 2
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_two_pages_and_embedded_fonts(self):
        with tempfile.TemporaryDirectory() as d:
            path = generate(self.data, Path(d)/'out.pdf')
            pdf = PdfReader(str(path))
            self.assertEqual(len(pdf.pages), 2)
            for page in pdf.pages:
                self.assertEqual(tuple(float(v) for v in page.mediabox[2:]), (612, 792))
                font_resources = page['/Resources']['/Font'].get_object()
                for fontref in font_resources.values():
                    font = fontref.get_object()
                    self.assertNotEqual(font.get('/BaseFont'), '/Helvetica')
                    descriptor = font.get('/FontDescriptor')
                    self.assertIsNotNone(descriptor)
                    self.assertTrue(any(k in descriptor.get_object() for k in ('/FontFile', '/FontFile2', '/FontFile3')))
            self.assertIn('Decimal Diagnostics', pdf.pages[0].extract_text())
            self.assertIn('WORK AREA', pdf.pages[1].extract_text())

if __name__ == '__main__':
    unittest.main()
