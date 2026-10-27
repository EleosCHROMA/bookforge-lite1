"""Back-of-book guided solutions with measured pagination."""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from .lesson_pages import fonts, validate_lessons, PALETTES, W, H, M


def render_answers(spec, output, theme, first_page, footer_notice='DRAFT - Educational and typesetting review required'):
    validate_lessons(spec)
    fonts()
    primary, _, _, ink = PALETTES[theme]
    c = canvas.Canvas(str(output), pagesize=(W, H))
    number = first_page

    def header():
        c.setFillColor(HexColor(primary))
        c.setFont('LessonBold', 14)
        c.drawString(M, H - 48, 'MASTER MECHANIC GUIDE')
        c.setFont('LessonBold', 11)
        c.drawString(M, H - 70, 'GUIDED LESSON SOLUTIONS')
        return H - 104

    def finish():
        c.setFillColor(HexColor(ink))
        c.setFont('LessonRegular', 7)
        if footer_notice:
            c.drawString(M, 29, footer_notice)
        c.drawRightString(W - M, 29, str(number))
        c.showPage()

    y = header()
    for lesson in sorted(spec['lessons'], key=lambda item: item['chapter_number']):
        answers = lesson.get('guided_answers')
        if answers is None:
            raise ValueError('Missing guided_answers')
        title = f"Lesson {lesson['chapter_number']}: {lesson['title']}"
        title_lines = simpleSplit(title, 'LessonBold', 10, W - 2*M)
        rows = [simpleSplit(f'{i}. {answer}', 'LessonRegular', 10, W - 2*M)
                for i, answer in enumerate(answers, 1)]
        height = len(title_lines)*15 + sum(len(row)*15 + 10 for row in rows) + 18
        if height > H - 104 - 60:
            raise ValueError('Guided solution exceeds one page')
        if y - height < 60:
            finish()
            number += 1
            y = header()
        c.setFillColor(HexColor(ink))
        for font, lines in [('LessonBold', title_lines)] + [('LessonRegular', row) for row in rows]:
            c.setFont(font, 10)
            for line in lines:
                c.drawString(M, y, line)
                y -= 15
            y -= 10
        y -= 8
    finish()
    c.save()
