import copy
import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.lesson_pages import validate_lessons
from bookforge_v3.guided_answers import render_answers
from bookforge_v3.native_book import assemble
from bookforge_v3.manuscript_audit import audit

ROOT = Path(__file__).resolve().parents[1]

class GuidedAnswersTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT/'data/guided_lessons.json').read_text())

    def test_missing_mismatched_and_empty_solutions(self):
        for answers in ([], [''], ['valid', '']):
            spec = copy.deepcopy(self.spec)
            spec['lessons'][0]['guided_answers'] = answers
            with self.assertRaises(ValueError):
                validate_lessons(spec)
        del self.spec['lessons'][0]['guided_answers']
        with tempfile.TemporaryDirectory() as tmp:
            lessons = Path(tmp)/'lessons.json'
            lessons.write_text(json.dumps(self.spec))
            with self.assertRaisesRegex(ValueError, 'requires guided_answers'):
                assemble(ROOT/'data/mistake_mechanics_six_chapters.json', lessons, Path(tmp)/'bad.pdf')

    def test_solutions_paginate_and_number_without_losing_answers(self):
        spec = {'lessons': [copy.deepcopy(self.spec['lessons'][0]) for _ in range(12)]}
        for n, lesson in enumerate(spec['lessons'], 1):
            lesson['chapter_number'] = n
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'answers.pdf'
            render_answers(spec, path, 'clean-premium', 50)
            pdf = PdfReader(path)
            self.assertGreater(len(pdf.pages), 1)
            text = '\n'.join(page.extract_text() for page in pdf.pages)
            for n in range(1, 13):
                self.assertIn(f'Lesson {n}:', text)
            for n, page in enumerate(pdf.pages, 50):
                self.assertEqual(page.extract_text().strip().splitlines()[-1], str(n))

    def test_answers_only_at_back_of_workbook(self):
        with tempfile.TemporaryDirectory() as tmp:
            for theme in ('clean-premium', 'playful-illustrated'):
                result = assemble(ROOT/'data/mistake_mechanics_six_chapters.json', ROOT/'data/guided_lessons.json', Path(tmp)/(theme+'.pdf'), theme)
                project = json.loads((ROOT/'data/mistake_mechanics_six_chapters.json').read_text())
                self.assertTrue(audit(result['output'], project)['ok'])
                pdf = PdfReader(result['output'])
                student = '\n'.join(p.extract_text() for p in pdf.pages[:result['answer_key_page']-1])
                solutions = pdf.pages[-1].extract_text()
                for lesson in self.spec['lessons']:
                    for answer in lesson['guided_answers']:
                        normalized = ' '.join(answer.split())
                        self.assertIn(normalized, ' '.join(solutions.split()))
                        self.assertNotIn(normalized, ' '.join(student.split()))
