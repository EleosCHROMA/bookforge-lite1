"""Clean premium theme and multi-chapter assembly for BookForge v2."""
import argparse
import json
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter
from generate import W,H,MARGIN,fonts,wrapped,header_footer
from fullbook import validate_book, ticket_page, answer_page

NAVY=HexColor('#24304A'); TEAL=HexColor('#1C9C9A'); LIGHT=HexColor('#EAF7F5'); INK=HexColor('#263044'); WHITE=HexColor('#FFFFFF'); BORDER=HexColor('#DCE6E9'); MUTED=HexColor('#64748B')
COLORS=['#E77B57','#258FAE','#8B70C5','#31A18A','#C86D95','#3C9A9A']

def accent(d):
    return HexColor(COLORS[(d['chapter_number']-1)%len(COLORS)])

def pill(c,x,y,w,h,color):
    c.setFillColor(color);c.roundRect(x,y,w,h,h/2,stroke=0,fill=1)

def title(c,txt,x,y,width,size=21,color=NAVY):
    return wrapped(c,txt,x,y,width,'BFBold',size,size*1.4,color,bottom=y-100,max_lines=3)

def opener(c,d,p):
    a=accent(d);header_footer(c,d,p,a)
    pill(c,MARGIN,H-108,150,25,LIGHT)
    c.setFillColor(a);c.setFont('BFBold',9);c.drawString(MARGIN+13,H-99,'THE LEARNING GARAGE')
    c.setFillColor(a);c.roundRect(MARGIN,H-265,W-2*MARGIN,132,18,fill=1,stroke=0)
    c.setFillColor(WHITE);c.setFont('BFBold',12);c.drawString(MARGIN+22,H-164,f"CHAPTER {d['chapter_number']:02}")
    title(c,d['chapter_title'],MARGIN+22,H-201,W-2*MARGIN-44,23,WHITE)
    c.setFillColor(NAVY);c.setFont('BFBold',14);c.drawString(MARGIN,H-307,'What you will learn')
    wrapped(c,d['introduction'],MARGIN,H-335,W-2*MARGIN,size=10,leading=17,bottom=H-422,max_lines=5)
    c.setFillColor(LIGHT);c.roundRect(MARGIN,H-670,W-2*MARGIN,225,15,fill=1,stroke=0)
    c.setFillColor(NAVY);c.setFont('BFBold',12);c.drawString(MARGIN+20,H-475,'YOUR LEARNING CHECKLIST')
    y=H-505
    for i,obj in enumerate(d['objectives']):
        c.setStrokeColor(a);c.setLineWidth(1.2);c.roundRect(MARGIN+20,y-3,13,13,4,stroke=1,fill=0)
        y=wrapped(c,obj,MARGIN+47,y+7,W-2*MARGIN-67,size=9,leading=14,bottom=H-658,max_lines=2)-20
    c.showPage()

def worksheet(c,d,p):
    a=accent(d);header_footer(c,d,p,a)
    c.setFillColor(NAVY);c.setFont('BFBold',17);c.drawString(MARGIN,H-82,'Practice & progress')
    wrapped(c,'Solve each problem. Use the space below to show your thinking.',MARGIN,H-105,W-2*MARGIN,size=9,color=MUTED,bottom=H-130)
    gap=14;cw=(W-2*MARGIN-gap)/2;cardh=182;top0=H-137
    for i,q in enumerate(d['problems']):
        x=MARGIN+(i%2)*(cw+gap);top=top0-(i//2)*(cardh+12);bottom=top-cardh
        c.setFillColor(WHITE);c.setStrokeColor(BORDER);c.setLineWidth(1);c.roundRect(x,bottom,cw,cardh,12,fill=1,stroke=1)
        pill(c,x+13,top-36,32,24,a)
        c.setFillColor(WHITE);c.setFont('BFBold',9);c.drawCentredString(x+29,top-28,f"{i+1+d.get('_practice_offset', 0):02}")
        wrapped(c,q['prompt'],x+14,top-54,cw-28,'BFBold',9.1,13,INK,bottom=top-104,max_lines=4)
        if q.get('hint'):
            wrapped(c,q['hint'],x+14,top-107,cw-28,size=7.2,leading=10,color=MUTED,bottom=top-130,max_lines=2)
        c.setStrokeColor(HexColor('#B7CED2'));c.setDash(2,3)
        c.roundRect(x+13,bottom+13,cw-26,46,7,fill=0,stroke=1);c.setDash()
        c.setFillColor(MUTED);c.setFont('BFBold',6);c.drawString(x+23,bottom+47,'YOUR WORKSPACE')
    c.showPage()

def make_pdf(data,path,section='all',start=1):
    fonts();c=canvas.Canvas(str(path),pagesize=(W,H));c.setTitle('BookForge — Clean Premium Workbook')
    if section in ('all','body'):
        opener(c,data,start);worksheet(c,data,start+1);ticket_page(c,data)
    if section in ('all','answers'):
        answer_page(c,data)
    c.save()

def generate(data,output):
    chapters=data.get('chapters') if isinstance(data,dict) and 'chapters' in data else [data]
    if not isinstance(chapters,list) or not chapters:raise ValueError('chapters must be nonempty list')
    for ch in chapters:validate_book(ch)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    writer=PdfWriter()
    with tempfile.TemporaryDirectory() as temp:
        for section in ('body','answers'):
            for i,ch in enumerate(chapters):
                p=Path(temp)/f'{section}_{i}.pdf';make_pdf(ch,p,section)
                reader=PdfReader(str(p))
                for page in reader.pages:
                    fdict=page['/Resources']['/Font'].get_object()
                    for key,ref in list(fdict.items()):
                        if ref.get_object().get('/BaseFont')=='/Helvetica':del fdict[key]
                    writer.add_page(page)
    with output.open('wb') as f:writer.write(f)
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input');parser.add_argument('--output',default='premium_workbook.pdf');args=parser.parse_args()
    print(generate(json.loads(Path(args.input).read_text(encoding='utf8')),args.output))
