import copy
import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.pipeline import ROOT, V2_ROOT, build
import sys
sys.path.insert(0, str(V2_ROOT))
from generate import fonts
from answer_layout import answer_batches, answer_row_height

def sample():
    return json.loads((ROOT / 'data/mistake_mechanics_six_chapters.json').read_text(encoding='utf-8'))

class AdaptiveAnswerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fonts()

    def test_existing_book_keeps_24_pages(self):
        chapter = sample()['chapters'][0]
        self.assertEqual([len(batch) for _, batch in answer_batches(chapter)], [6])

    def test_long_answers_split_early(self):
        chapter = copy.deepcopy(sample()['chapters'][0])
        for p in chapter['problems']:
            chapter['answers'][p['id']] = 'Detailed explanation: ' + ('Carefully align each decimal position and verify the operation. ' * 9)
        batches = answer_batches(chapter)
        self.assertGreater(len(batches), 1)
        self.assertEqual(sum(len(items) for _, items in batches), 6)
        for _, items in batches:
            self.assertLessEqual(sum(answer_row_height(chapter['answers'][p['id']]) for p in items), 380)

    def test_overlong_answer_rejected(self):
        chapter = copy.deepcopy(sample()['chapters'][0])
        chapter['answers']['c1p1'] = 'overlong ' * 600
        with self.assertRaisesRegex(ValueError, 'too long for one page'):
            answer_batches(chapter)

    def test_full_book_uses_multiple_answer_pages(self):
        project = sample()
        for chapter in project['chapters']:
            for p in chapter['problems']:
                chapter['answers'][p['id']] += ' Explanation: ' + ('Check each operation carefully. ' * 12)
        project['math_checks'] = []
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'input.json'
            source.write_text(json.dumps(project), encoding='utf-8')
            result = build(source, Path(temp) / 'out.pdf', theme='clean-premium')
            self.assertGreater(result['pages'], 24)
            self.assertTrue(result['pages'] <= 42)
            pdf = PdfReader(result['output'])
            self.assertIn('MASTER MECHANIC GUIDE', pdf.pages[-1].extract_text())
