"""Reusable print-safe guided-lesson pages for BookForge v3."""
from pathlib import Path
from tempfile import TemporaryDirectory
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from pypdf import PdfReader,PdfWriter

W,H,M=612,792,42
PALETTES={"clean-premium":("#286E9C","#8B72C9","#F5F8FC","#18283A"),
          "playful-illustrated":("#F16B32","#21A9A4","#FFF9EE","#17335A")}

def fonts(font_dir=None):
    roots=([Path(font_dir)] if font_dir else [])+[Path('/usr/share/fonts/truetype/dejavu'),
          Path('C:/Windows/Fonts'),Path.home()/'AppData/Local/Microsoft/Windows/Fonts']
    for root in roots:
        a,b=root/'DejaVuSans.ttf',root/'DejaVuSans-Bold.ttf'
        if a.exists() and b.exists():
            pdfmetrics.registerFont(TTFont('LessonRegular',str(a)))
            pdfmetrics.registerFont(TTFont('LessonBold',str(b)))
            return
    raise FileNotFoundError('DejaVu Sans regular/bold fonts missing')

def validate_lessons(data):
    if not isinstance(data,dict) or not isinstance(data.get('lessons'),list) or not data['lessons']:
        raise ValueError('Expected object with nonempty lessons')
    for n,lesson in enumerate(data['lessons'],1):
        if not isinstance(lesson,dict):raise ValueError(f'Lesson {n} must be object')
        if any(not isinstance(lesson.get(k),str) or not lesson[k].strip() for k in ('title','concept')):
            raise ValueError(f'Lesson {n} missing title/concept')
        examples=lesson.get('examples')
        guided=lesson.get('guided')
        if not isinstance(examples,list) or not 1<=len(examples)<=2:
            raise ValueError('Each lesson requires 1-2 worked examples')
        if not isinstance(guided,list) or not 1<=len(guided)<=2:
            raise ValueError('Each lesson requires 1-2 guided exercises')
        if any(not isinstance(g,str) or not g.strip() for g in guided):
            raise ValueError('Guided exercise must be nonempty text')
        answers=lesson.get('guided_answers')
        if answers is not None and (not isinstance(answers,list) or len(answers)!=len(guided)
                or any(not isinstance(a,str) or not a.strip() for a in answers)):
            raise ValueError('guided_answers must match guided exercises with nonempty text')
        for example in examples:
            if not isinstance(example,dict) or not isinstance(example.get('problem'),str):
                raise ValueError('Example requires a problem')
            steps=example.get('steps')
            if not isinstance(steps,list) or not 1<=len(steps)<=3 or any(not isinstance(s,str) or not s.strip() for s in steps):
                raise ValueError('Example requires 1-3 nonempty steps')
    return data

def draw(c,text,x,y,width,size=9,leading=14,bold=False,color='#18283A',limit=4):
    font='LessonBold' if bold else 'LessonRegular'
    lines=simpleSplit(text,font,size,width)
    if len(lines)>limit:raise ValueError('Lesson text overflow: '+text[:60])
    c.setFillColor(HexColor(color));c.setFont(font,size)
    for line in lines:
        c.drawString(x,y,line);y-=leading
    return y

def render(data,output,theme='clean-premium',font_dir=None,page_numbers=None):
    validate_lessons(data)
    if theme not in PALETTES:raise ValueError('Invalid lesson theme')
    if page_numbers is not None and (len(page_numbers)!=len(data['lessons']) or any(type(n) is not int or n<1 for n in page_numbers)):
        raise ValueError('page_numbers must be positive integers matching lessons')
    fonts(font_dir)
    primary,accent,surface,ink=PALETTES[theme]
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(output),pagesize=(W,H))
    for i,lesson in enumerate(data['lessons'],1):
        c.setStrokeColor(HexColor(primary));c.line(M,H-33,W-M,H-33)
        draw(c,'BOOKFORGE / GUIDED LESSON',M,H-25,W-2*M,8,bold=True,color=primary)
        c.setFillColor(HexColor(surface));c.roundRect(M,618,W-2*M,112,15,stroke=0,fill=1)
        draw(c,lesson['title'],M+20,692,W-2*M-40,17,22,True,ink,2)
        draw(c,lesson['concept'],M+20,649,W-2*M-40,9,14,False,ink,2)
        c.setFillColor(HexColor(primary));c.roundRect(M,574,W-2*M,31,11,stroke=0,fill=1)
        draw(c,'LEARN BY EXAMPLE',M+14,584,W-2*M-30,11,bold=True,color='#FFFFFF')
        y=560
        for j,example in enumerate(lesson['examples'],1):
            height=155 if len(lesson['examples'])==2 else 220
            c.setFillColor(HexColor(surface));c.roundRect(M,y-height,W-2*M,height-9,12,stroke=0,fill=1)
            yy=draw(c,f'Example {j}: {example["problem"]}',M+14,y-26,W-2*M-28,10,15,True,ink,2)-9
            for idx,step in enumerate(example['steps'],1):
                yy=draw(c,f'{idx}. {step}',M+17,yy,W-2*M-34,9,14,False,ink,3)-8
            if yy<y-height+11:raise ValueError('Example exceeds card')
            y-=height+8
        y-=14
        if y<177:raise ValueError('Insufficient space for guided questions')
        draw(c,'YOUR TURN',M,y,W-2*M,12,bold=True,color=accent);y-=23
        for j,prompt in enumerate(lesson['guided'],1):
            y=draw(c,f'{j}. {prompt}',M+5,y,W-2*M-10,9,13,True,ink,2)-17
            c.setStrokeColor(HexColor(accent));c.setDash(2,3)
            c.roundRect(M+5,y-48,W-2*M-10,48,9,stroke=1,fill=0);c.setDash()
            y-=62
        if y<54:raise ValueError('Guided answers exceed safe area')
        draw(c,'DRAFT • Educational and typesetting review required',M,29,W-2*M,7,color=ink)
        draw(c,str(page_numbers[i-1] if page_numbers is not None else i),W-M-15,29,15,8,bold=True,color=primary)
        c.showPage()
    c.save()
    reader=PdfReader(str(output));writer=PdfWriter()
    for page in reader.pages:
        fontmap=page['/Resources']['/Font'].get_object()
        regular=next((v for v in fontmap.values() if 'DejaVuSans' in str(v.get_object().get('/BaseFont','')) and 'Bold' not in str(v.get_object().get('/BaseFont',''))),None)
        if regular is None:raise ValueError('Embedded regular font missing')
        for key,v in list(fontmap.items()):
            if str(v.get_object().get('/BaseFont'))=='/Helvetica':fontmap[key]=regular
        writer.add_page(page)
    with output.open('wb') as f:writer.write(f)
    return output

def attach(interior,lesson_data,output,theme='clean-premium',font_dir=None):
    """Insert guided lessons before the first answer-key page."""
    reader=PdfReader(str(interior))
    matches=[i for i,p in enumerate(reader.pages) if 'MASTER MECHANIC GUIDE' in (p.extract_text() or '')]
    if not matches:raise ValueError('No answer-key boundary')
    split=matches[0]
    with TemporaryDirectory() as temp:
        supplement=PdfReader(str(render(lesson_data,Path(temp)/'lessons.pdf',theme,font_dir)))
        writer=PdfWriter()
        for p in reader.pages[:split]:writer.add_page(p)
        for p in supplement.pages:writer.add_page(p)
        for p in reader.pages[split:]:writer.add_page(p)
        target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('wb') as f:writer.write(f)
        return {'output':str(target),'pages':len(writer.pages),'lesson_pages':len(supplement.pages),
                'answer_key_page':split+len(supplement.pages)+1}
