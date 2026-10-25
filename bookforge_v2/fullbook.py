"""BookForge v2 extension: chapter opener, worksheet, repair tickets and back-of-book answers."""
import argparse
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter
from generate import W, H, MARGIN, NAVY, ORANGE, BLUE, GREEN, MUTED, INK, fonts, validate, chapter_page, worksheet_page, header_footer, wrapped

WHITE = HexColor('#FFFFFF')
PALE = HexColor('#F4F8FB')

def validate_book(data):
    validate(data)
    tickets = data.get('repair_tickets')
    if not isinstance(tickets, list) or not 1 <= len(tickets) <= 2:
        raise ValueError('repair_tickets must contain 1 or 2 tickets')
    seen = {p['id'] for p in data['problems']}
    for i, ticket in enumerate(tickets):
        if not isinstance(ticket, dict):
            raise ValueError(f'ticket {i+1} must be an object')
        for key in ('id', 'topic', 'faulty_work', 'diagnosis', 'instruction', 'answer'):
            if not isinstance(ticket.get(key), str) or not ticket[key].strip():
                raise ValueError(f'ticket {i+1} missing {key}')
        if ticket['id'] in seen:
            raise ValueError('duplicate exercise ID')
        seen.add(ticket['id'])
    answers = data.get('answers')
    if not isinstance(answers, dict):
        raise ValueError('answers must be an object')
    problem_ids = {p['id'] for p in data['problems']}
    if set(answers) != problem_ids:
        raise ValueError('answers must match all problem IDs exactly')
    if not all(isinstance(a, str) and a.strip() for a in answers.values()):
        raise ValueError('answers must contain nonempty text')
    return data


def ticket_page(c, data, page_number=3, theme='clean-premium'):
    from themes import THEMES
    palette = THEMES[theme]['palette']
    accent = HexColor(palette['accent'])
    primary = HexColor(palette['primary'])
    header_footer(c, data, page_number, accent)
    c.setFillColor(accent)
    c.roundRect(MARGIN, H-86, 270, 31, 14, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('BFBold', 12)
    c.drawString(MARGIN+14, H-76, '03   REPAIR TICKETS')
    wrapped(c, 'Inspect the mistake, explain the failure, then make your repair.', MARGIN, H-112, W-2*MARGIN, size=9)
    top = H-145
    for i, t in enumerate(data['repair_tickets']):
        h = 420 if len(data['repair_tickets']) == 1 else 250
        bottom = top-h
        if bottom < 52:
            raise ValueError('repair tickets overflow page')
        c.setStrokeColor(accent)
        c.setLineWidth(1)
        c.roundRect(MARGIN, bottom, W-2*MARGIN, h, 9, fill=0, stroke=1)
        c.setFillColor(primary)
        c.roundRect(MARGIN, top-34, W-2*MARGIN, 34, 8, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont('BFBold', 10)
        c.drawString(MARGIN+12, top-22, f"REPAIR TICKET {t['id']}")
        c.setFont('BFRegular', 7)
        c.drawRightString(W-MARGIN-12, top-22, t['topic'][:47].upper())
        for label, text_value, y, bg in [
            ('FAULTY WORK', t['faulty_work'], top-53, HexColor('#FFF5E8')),
            ('DIAGNOSIS', t['diagnosis'], top-101, HexColor('#F3F6FB')),
            ('YOUR REPAIR', t['instruction'], top-149, HexColor('#EDF9F3')),
        ]:
            c.setFillColor(bg)
            c.rect(MARGIN+1, y-33, W-2*MARGIN-2, 43, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.setFont('BFBold', 8)
            c.drawString(MARGIN+11, y, label)
            wrapped(c, text_value, MARGIN+118, y, W-2*MARGIN-132, size=8.2, leading=11, bottom=y-30, max_lines=3)
        c.setStrokeColor(accent)
        c.setDash(2, 3)
        c.roundRect(MARGIN+15, bottom+14, W-2*MARGIN-30, max(41, h-204), 5, stroke=1, fill=0)
        c.setDash()
        top = bottom-20
    c.showPage()


def answer_page(c, data, page_number=4, theme="clean-premium"):
    header_footer(c, data, page_number, NAVY)
    c.setFillColor(NAVY)
    c.roundRect(MARGIN, H-130, W-2*MARGIN, 70, 10, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('BFBold', 19)
    c.drawString(MARGIN+18, H-101, 'MASTER MECHANIC GUIDE')
    c.setFont('BFRegular', 9)
    c.drawString(MARGIN+18, H-120, 'Answer keys & repair solutions — collected at the back')
    y = H-161
    c.setFillColor(ORANGE)
    c.setFont('BFBold', 12)
    c.drawString(MARGIN, y, 'PRACTICE ANSWERS')
    y -= 22
    for i, p in enumerate(data['problems']):
        a = data['answers'][p['id']]
        lines = __import__('reportlab').lib.utils.simpleSplit(a, 'BFRegular', 9, W-2*MARGIN-65)
        rowh = max(33, 15*len(lines)+18)
        if y-rowh < 100:
            raise ValueError('answer key overflow; shorten answers or split into more pages')
        if i % 2 == 0:
            c.setFillColor(HexColor('#FFF0E5'))
            c.roundRect(MARGIN, y-rowh, W-2*MARGIN, rowh, 4, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.setFont('BFBold', 9)
        c.drawString(MARGIN+10, y-18, f"{i+1+data.get('_answer_offset', 0)}.")
        wrapped(c, a, MARGIN+43, y-17, W-2*MARGIN-60, size=9, leading=15, bottom=y-rowh+1)
        y -= rowh+4
    if data['repair_tickets']:
        y -= 15
        if y < 85:
            raise ValueError('repair answer section overflow')
        c.setFillColor(GREEN)
        c.setFont('BFBold', 12)
        c.drawString(MARGIN, y, 'REPAIR TICKET SOLUTIONS')
        y -= 23
    for t in data['repair_tickets']:
        if y < 64:
            raise ValueError('repair answers overflow')
        c.setFillColor(GREEN)
        c.setFont('BFBold', 9)
        c.drawString(MARGIN+4, y, t['id'])
        y = wrapped(c, t['answer'], MARGIN+77, y, W-2*MARGIN-89, size=8.5, leading=13, bottom=54, max_lines=3)-17
    c.showPage()


def generate_book(data, output, font_dir=None):
    validate_book(data)
    fonts(font_dir)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=(W,H))
    c.setTitle(f"{data['series']} — {data['chapter_title']} (v2 sample)")
    chapter_page(c, data)
    worksheet_page(c, data)
    ticket_page(c, data)
    answer_page(c, data)
    c.save()
    reader = PdfReader(str(output))
    writer = PdfWriter()
    for page in reader.pages:
        fdict = page['/Resources']['/Font'].get_object()
        for key, ref in list(fdict.items()):
            if str(ref.get_object().get('/BaseFont')) == '/Helvetica':
                del fdict[key]
        writer.add_page(page)
    with output.open('wb') as f:
        writer.write(f)
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--output', default='bookforge_v2_sample.pdf')
    parser.add_argument('--font-dir')
    args = parser.parse_args()
    print(generate_book(json.loads(Path(args.input).read_text(encoding='utf-8')), args.output, args.font_dir))
