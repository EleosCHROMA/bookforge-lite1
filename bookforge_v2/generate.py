"""BookForge v2: deterministic two-page educational worksheet PDF generator."""
import argparse
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter

W, H = letter
MARGIN = 42
NAVY = HexColor('#202B43')
ORANGE = HexColor('#F36B21')
BLUE = HexColor('#168DCC')
GREEN = HexColor('#129C68')
INK = HexColor('#263044')
MUTED = HexColor('#526078')
PALE = HexColor('#F7F9FC')


def fonts(font_dir=None):
    roots = [Path(font_dir)] if font_dir else []
    roots += [Path(__file__).parent / 'fonts', Path('/usr/share/fonts/truetype/dejavu'), Path('C:/Windows/Fonts')]
    for root in roots:
        normal = next((root / n for n in ('DejaVuSans.ttf', 'dejavusans.ttf') if (root / n).exists()), None)
        bold = next((root / n for n in ('DejaVuSans-Bold.ttf', 'dejavusans-bold.ttf') if (root / n).exists()), None)
        if normal and bold:
            pdfmetrics.registerFont(TTFont('BFRegular', str(normal)))
            pdfmetrics.registerFont(TTFont('BFBold', str(bold)))
            return
    raise FileNotFoundError('DejaVu Sans fonts missing. Place DejaVuSans.ttf and DejaVuSans-Bold.ttf in v2/fonts/ or pass --font-dir.')


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Root must be an object')
    for key in ('series', 'grade', 'chapter_number', 'chapter_title', 'introduction', 'objectives', 'problems'):
        if key not in data:
            raise ValueError(f'Missing required field: {key}')
    for key in ('series', 'grade', 'chapter_title', 'introduction'):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f'{key} must be nonempty text')
    if not isinstance(data['chapter_number'], int) or not 1 <= data['chapter_number'] <= 99:
        raise ValueError('chapter_number must be an integer 1..99')
    if not isinstance(data['objectives'], list) or not 1 <= len(data['objectives']) <= 5 or not all(isinstance(x, str) and x.strip() for x in data['objectives']):
        raise ValueError('objectives must contain 1..5 nonempty strings')
    if not isinstance(data['problems'], list) or not 1 <= len(data['problems']) <= 60:
        raise ValueError('problems must contain 1..60 entries')
    ids = set()
    for i, p in enumerate(data['problems'], 1):
        if not isinstance(p, dict) or not isinstance(p.get('id'), str) or not p['id'].strip() or not isinstance(p.get('prompt'), str) or not p['prompt'].strip():
            raise ValueError(f'problem {i} needs nonempty id and prompt')
        if p['id'] in ids:
            raise ValueError('duplicate problem id')
        ids.add(p['id'])
        if 'hint' in p and not isinstance(p['hint'], str):
            raise ValueError('hint must be text')
    return data


def wrapped(c, text, x, top, width, font='BFRegular', size=10, leading=15, color=INK, bottom=42, max_lines=None):
    lines = simpleSplit(text, font, size, width)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f'Text overflows allotted {max_lines} lines: {text[:65]}')
    if top - len(lines)*leading < bottom:
        raise ValueError(f'Text exceeds page safe area: {text[:65]}')
    c.setFillColor(color)
    c.setFont(font, size)
    for line in lines:
        c.drawString(x, top, line)
        top -= leading
    return top


def header_footer(c, data, page, color):
    c.setStrokeColor(color)
    c.setLineWidth(1.4)
    c.line(MARGIN, H-34, W-MARGIN, H-34)
    c.setFont('BFBold', 7)
    c.setFillColor(color)
    c.drawString(MARGIN, H-26, f"CHAPTER {data['chapter_number']}  •  {data['chapter_title'].upper()}"[:85])
    c.setFillColor(MUTED)
    c.setFont('BFRegular', 7)
    c.drawRightString(W-MARGIN, H-26, f"{data['series'].upper()}  •  {data['grade'].upper()}")
    c.setFont('BFRegular', 8)
    c.drawString(MARGIN, 25, f"{data['series']}  •  {data['grade']}")
    c.setFillColor(color)
    c.circle(W-MARGIN-9, 28, 11, fill=1, stroke=0)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('BFBold', 8)
    c.drawCentredString(W-MARGIN-9, 25, str(page))


def chapter_page(c, data):
    header_footer(c, data, 1, ORANGE)
    c.setFillColor(NAVY)
    c.roundRect(MARGIN, H-255, W-2*MARGIN, 157, 12, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.setFont('BFBold', 11)
    c.drawString(MARGIN+22, H-132, 'WELCOME TO THE DIAGNOSTICS BAY!')
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('BFBold', 38)
    c.drawString(MARGIN+20, H-188, str(data['chapter_number']))
    wrapped(c, data['chapter_title'], MARGIN+88, H-178, W-2*MARGIN-110, 'BFBold', 21, 29, HexColor('#FFFFFF'), bottom=H-240, max_lines=2)
    c.setFillColor(ORANGE)
    c.setFont('BFBold', 13)
    c.drawString(MARGIN, H-298, '01   WELCOME & LEARNING GOALS')
    y = wrapped(c, data['introduction'], MARGIN, H-331, W-2*MARGIN, size=10.5, leading=17, bottom=H-430, max_lines=5)
    c.setFillColor(NAVY)
    c.roundRect(MARGIN, H-483, W-2*MARGIN, 31, 6, fill=1, stroke=0)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('BFBold', 10)
    c.drawString(MARGIN+13, H-472, 'DIAGNOSTIC LEARNING OBJECTIVES')
    y = H-514
    for n, goal in enumerate(data['objectives'], 1):
        c.setFillColor(GREEN)
        c.setFont('BFBold', 10)
        c.drawString(MARGIN+4, y, f'{n:02}')
        y = wrapped(c, goal, MARGIN+36, y, W-2*MARGIN-43, size=10, leading=16, bottom=62, max_lines=2) - 17
    if y < 62:
        raise ValueError('Objectives overflow page 1')
    c.showPage()


def worksheet_page(c, data):
    header_footer(c, data, 2, BLUE)
    c.setFillColor(BLUE)
    c.roundRect(MARGIN, H-83, 310, 29, 14, fill=1, stroke=0)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('BFBold', 12)
    c.drawString(MARGIN+14, H-74, '02   GUIDED & INDEPENDENT PRACTICE')
    wrapped(c, 'Show your work in each diagnostic area. Check answers in the back of the finished book.', MARGIN, H-106, W-2*MARGIN, size=9, bottom=H-137)
    gap = 14
    colw = (W-2*MARGIN-gap)/2
    cardh = 179
    top0 = H-145
    for idx, p in enumerate(data['problems']):
        col = idx % 2
        row = idx // 2
        x = MARGIN + col*(colw+gap)
        top = top0 - row*(cardh+13)
        bottom = top-cardh
        c.setStrokeColor(HexColor('#D8E2EE'))
        c.setLineWidth(0.9)
        c.setFillColor(HexColor('#FFFFFF'))
        c.roundRect(x, bottom, colw, cardh, 9, stroke=1, fill=1)
        c.setFillColor(BLUE)
        c.circle(x+17, top-20, 10, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('BFBold', 9)
        c.drawCentredString(x+17, top-23, str(idx+1))
        wrapped(c, p['prompt'], x+34, top-18, colw-45, 'BFBold', 9.5, 14, bottom=top-75, max_lines=4)
        if p.get('hint'):
            wrapped(c, p['hint'], x+14, top-78, colw-28, 'BFRegular', 7.5, 11, MUTED, bottom=top-104, max_lines=2)
        c.setStrokeColor(BLUE)
        c.setDash(2, 2)
        c.roundRect(x+13, bottom+14, colw-26, 64, 5, fill=0, stroke=1)
        c.setDash()
        c.setFillColor(MUTED)
        c.setFont('BFBold', 6)
        c.drawString(x+22, bottom+65, 'WORK AREA')
    c.showPage()


def generate(data, output, font_dir=None):
    validate(data)
    fonts(font_dir)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=letter, pageCompression=1)
    c.setTitle(f"{data['series']} — {data['chapter_title']} (prototype)")
    chapter_page(c, data)
    worksheet_page(c, data)
    c.save()
    # ReportLab reserves Helvetica even when never used; remove the unused
    # resource so print preflight sees embedded fonts only.
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(str(output))
    writer = PdfWriter()
    for page in reader.pages:
        resources = page['/Resources'].get_object()
        font_dict = resources['/Font'].get_object()
        for key, ref in list(font_dict.items()):
            if ref.get_object().get('/BaseFont') == '/Helvetica':
                del font_dict[key]
        writer.add_page(page)
    with output.open('wb') as fh:
        writer.write(fh)
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', help='JSON workbook chapter')
    ap.add_argument('--output', default='prototype.pdf')
    ap.add_argument('--font-dir', default=None)
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    print(generate(data, args.output, args.font_dir))


if __name__ == '__main__':
    main()
