"""BookForge v2 dual-theme, multi-chapter PDF assembly."""
import argparse
import json
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter
from generate import W,H,MARGIN,fonts,wrapped,header_footer
from fullbook import validate_book, ticket_page, answer_page
from premium import opener as premium_opener, worksheet as premium_worksheet
from layout import worksheet_batches, section_page_count
from answer_layout import answer_batches

ANSWERS_PER_PAGE = 9

ROOT=Path(__file__).resolve().parent
CONFIG=json.loads((ROOT/'config/themes.json').read_text(encoding='utf-8'))
THEMES=CONFIG['themes']
WHITE=HexColor('#FFFFFF')

def gear(c,x,y,r,color):
    c.saveState();c.setFillColor(color)
    for i in range(8):
        c.saveState();c.translate(x,y);c.rotate(i*45);c.roundRect(-r*.14,r*.72,r*.28,r*.52,2,fill=1,stroke=0);c.restoreState()
    c.circle(x,y,r*.86,fill=1,stroke=0)
    c.setFillColor(WHITE);c.circle(x,y,r*.35,fill=1,stroke=0)
    c.restoreState()

def playful_opener(c,d,page):
    orange=HexColor('#F16B32');navy=HexColor('#17335A');teal=HexColor('#21A9A4')
    header_footer(c,d,page,orange)
    c.setFillColor(HexColor('#FFF3E6'));c.roundRect(MARGIN,H-293,W-2*MARGIN,207,19,fill=1,stroke=0)
    c.setFillColor(orange);c.roundRect(MARGIN+12,H-163,W-2*MARGIN-24,61,15,fill=1,stroke=0)
    gear(c,W-MARGIN-38,H-132,18,HexColor('#FFCB68'))
    c.setFillColor(WHITE);c.setFont('BFBold',11);c.drawString(MARGIN+26,H-124,f"CHAPTER {d['chapter_number']:02d}  •  THE LEARNING GARAGE")
    wrapped(c,d['chapter_title'],MARGIN+26,H-146,W-2*MARGIN-108,'BFBold',18,23,WHITE,bottom=H-169,max_lines=2)
    c.setFillColor(navy);c.setFont('BFBold',14);c.drawString(MARGIN+24,H-193,'Welcome to the workshop!')
    wrapped(c,d['introduction'],MARGIN+24,H-215,W-2*MARGIN-48,size=9.2,leading=15,color=navy,bottom=H-279,max_lines=4)
    c.setFillColor(teal);c.roundRect(MARGIN,H-352,W-2*MARGIN,37,15,fill=1,stroke=0)
    c.setFillColor(WHITE);c.setFont('BFBold',13);c.drawString(MARGIN+20,H-339,'YOUR MISSION: LEARNING OBJECTIVES')
    y=H-387
    for i,objective in enumerate(d['objectives']):
        c.setFillColor(HexColor('#F4FAFB'));c.roundRect(MARGIN,y-38,W-2*MARGIN,49,11,fill=1,stroke=0)
        c.setFillColor(teal);c.circle(MARGIN+24,y-13,12,fill=1,stroke=0)
        c.setFillColor(WHITE);c.setFont('BFBold',9);c.drawCentredString(MARGIN+24,y-16,str(i+1))
        wrapped(c,objective,MARGIN+48,y-8,W-2*MARGIN-66,size=9,leading=14,color=navy,bottom=y-36,max_lines=2)
        y-=59
    c.setFillColor(orange);c.setFont('BFBold',10);c.drawString(MARGIN,H-720,'INSPECT  •  THINK  •  REPAIR  •  LEARN')
    gear(c,W-MARGIN-22,H-710,10,teal)
    c.showPage()

def playful_worksheet(c,d,page):
    navy=HexColor('#17335A');orange=HexColor('#F16B32');teal=HexColor('#21A9A4')
    accents=['#F16B32','#8D68D7','#21A9A4','#E65D87','#428BC8','#33A66C']
    header_footer(c,d,page,orange)
    c.setFillColor(orange);c.roundRect(MARGIN,H-112,W-2*MARGIN,55,16,fill=1,stroke=0)
    c.setFillColor(WHITE);c.setFont('BFBold',17);c.drawString(MARGIN+22,H-80,'GUIDED PRACTICE')
    c.setFont('BFRegular',9);c.drawString(MARGIN+22,H-99,'Complete each problem. Show your repair work below.')
    gap=14;cw=(W-2*MARGIN-gap)/2;cardh=183;top0=H-129
    for i,q in enumerate(d['problems']):
        x=MARGIN+(i%2)*(cw+gap);top=top0-(i//2)*(cardh+11);bottom=top-cardh
        color=HexColor(accents[i%len(accents)])
        c.setFillColor(WHITE);c.setStrokeColor(color);c.setLineWidth(1.2)
        c.roundRect(x,bottom,cw,cardh,15,fill=1,stroke=1)
        c.setFillColor(color);c.circle(x+24,top-25,15,fill=1,stroke=0)
        c.setFillColor(WHITE);c.setFont('BFBold',12);c.drawCentredString(x+24,top-29,str(i+1+d.get('_practice_offset', 0)))
        wrapped(c,q['prompt'],x+46,top-22,cw-58,'BFBold',8.5,12,navy,bottom=top-85,max_lines=5)
        if q.get('hint'):
            wrapped(c,q['hint'],x+15,top-94,cw-30,size=7.3,leading=10,color=navy,bottom=top-121,max_lines=2)
        c.setStrokeColor(color);c.setDash(2,3);c.roundRect(x+14,bottom+13,cw-28,55,8,fill=0,stroke=1);c.setDash()
        c.setFillColor(color);c.setFont('BFBold',7);c.drawString(x+23,bottom+53,'WORK AREA')
        gear(c,x+cw-25,bottom+29,8,color)
    c.showPage()

def render_section(ch,path,theme,section,page_start):
    c=canvas.Canvas(str(path),pagesize=(W,H));c.setTitle(f"{ch['series']} — {theme}")
    if section=='body':
        if theme=='clean-premium': premium_opener(c,ch,page_start)
        else: playful_opener(c,ch,page_start)
        for n, batch in enumerate(worksheet_batches(ch['problems'])):
            part = dict(ch, problems=batch, _practice_offset=6*n)
            if theme=='clean-premium': premium_worksheet(c,part,page_start+1+n)
            else: playful_worksheet(c,part,page_start+1+n)
        ticket_page(c,ch,page_start+section_page_count(ch)-1,theme)
    else:
        for index, (start, batch) in enumerate(answer_batches(ch)):
            is_last = start + len(batch) >= len(ch['problems'])
            section_data = dict(ch, problems=batch,
                                answers={p['id']: ch['answers'][p['id']] for p in batch},
                                repair_tickets=ch['repair_tickets'] if is_last else [],
                                _answer_offset=start)
            answer_page(c, section_data, page_start + index, theme)
    c.save()

def generate(data,output,theme=None):
    theme=theme or data.get('theme',CONFIG['default_theme'])
    if theme not in THEMES:raise ValueError(f'Unknown theme: {theme}')
    chapters=data.get('chapters') if 'chapters' in data else [data]
    if not isinstance(chapters,list) or not chapters:raise ValueError('chapters must be a nonempty list')
    for chapter in chapters:validate_book(chapter)
    fonts();writer=PdfWriter()
    with tempfile.TemporaryDirectory() as tmp:
        total_body_pages = sum(section_page_count(ch) for ch in chapters)
        body_page = 1
        answer_page_number = total_body_pages + 1
        for section in ('body','answers'):
            for i,ch in enumerate(chapters):
                p=Path(tmp)/f'{section}-{i}.pdf'
                start_page = body_page if section == 'body' else answer_page_number
                render_section(ch,p,theme,section,start_page)
                rendered_pages = PdfReader(str(p)).pages
                for page in rendered_pages:
                    writer.add_page(page)
                if section == 'body': body_page += len(rendered_pages)
                else: answer_page_number += len(rendered_pages)
    # ReportLab initializes /F1 as Helvetica even when it prints no glyphs.
    # Point that default font resource to our embedded regular face.
    for page in writer.pages:
        resources = page['/Resources'].get_object()
        font_ref = resources.get('/Font')
        if not font_ref:
            continue
        font_map = font_ref.get_object()
        regular = next((obj for obj in font_map.values()
                        if 'DejaVuSans' in str(obj.get_object().get('/BaseFont', ''))
                        and 'Bold' not in str(obj.get_object().get('/BaseFont', ''))), None)
        if regular is None:
            continue
        for font_name, font_obj in list(font_map.items()):
            if str(font_obj.get_object().get('/BaseFont', '')) == '/Helvetica':
                font_map[font_name] = regular
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('wb') as f:writer.write(f)
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',default='bookforge_themed.pdf');p.add_argument('--theme',choices=list(THEMES));args=p.parse_args()
    print(generate(json.loads(Path(args.input).read_text(encoding='utf-8')),args.output,args.theme))
