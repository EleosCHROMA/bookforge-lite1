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
                self.assertTrue(audit(result['output'], project, lesson_data=self.spec)['ok'])
                pdf = PdfReader(result['output'])
                student = '\n'.join(p.extract_text() for p in pdf.pages[:result['answer_key_page']-1])
                solutions = pdf.pages[-1].extract_text()
                for lesson in self.spec['lessons']:
                    for answer in lesson['guided_answers']:
                        normalized = ' '.join(answer.split())
                        self.assertIn(normalized, ' '.join(solutions.split()))
                        self.assertNotIn(normalized, ' '.join(student.split()))

class FinishedGuidedSolutionAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/'fixture.pdf'
        self.spec = {'lessons': [{'title': 'Test lesson', 'concept': 'Test concept',
            'chapter_number': 1, 'examples': [{'problem': '1 + 1', 'steps': ['Add to get 2.']}],
            'guided': ['Find 2 + 2.', 'Find 3 + 3.'],
            'guided_answers': ['4. Add two and two.', '6. Add three and three.']}]}

    def tearDown(self):
        self.temp.cleanup()

    def make_pdf(self, answers=None, student_extra='', repeat_heading=False):
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(self.path))
        c.drawString(42, 700, 'Test lesson')
        c.drawString(42, 680, student_extra)
        c.showPage()
        lines = ['MASTER MECHANIC GUIDE', 'GUIDED LESSON SOLUTIONS', 'Lesson 1: Test lesson']
        lines += answers if answers is not None else ['1. 4. Add two and two.', '2. 6. Add three and three.']
        if repeat_heading:
            lines.append('Lesson 1: Test lesson')
        for n, line in enumerate(lines):
            c.drawString(42, 700 - n*20, line)
        c.showPage()
        c.save()

    def test_complete_solutions_checked(self):
        self.make_pdf()
        result = audit(self.path, lesson_data=self.spec)
        self.assertTrue(result['ok'], result['errors'])
        self.assertEqual(result['guided_solutions_checked'], 2)

    def test_missing_changed_and_reordered_answers_rejected(self):
        for answers in ([], ['1. 5. Add two and two.', '2. 6. Add three and three.'],
                        ['2. 6. Add three and three.', '1. 4. Add two and two.']):
            with self.subTest(answers=answers):
                self.make_pdf(answers=answers)
                self.assertFalse(audit(self.path, lesson_data=self.spec)['ok'])

    def test_duplicate_solution_section_rejected(self):
        self.make_pdf(repeat_heading=True)
        self.assertFalse(audit(self.path, lesson_data=self.spec)['ok'])

    def test_student_solution_leak_rejected(self):
        self.make_pdf(student_extra='4. Add two and two.')
        result = audit(self.path, lesson_data=self.spec)
        self.assertTrue(any('reveal' in error for error in result['errors']))

    def test_missing_source_solutions_rejected(self):
        self.make_pdf()
        del self.spec['lessons'][0]['guided_answers']
        self.assertFalse(audit(self.path, lesson_data=self.spec)['ok'])
