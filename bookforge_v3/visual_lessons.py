"""Vector mini-lessons: fractions, inequalities and a statistical dot plot."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter

W,H=letter
INK=HexColor('#183354'); BLUE=HexColor('#3489C8')
TEAL=HexColor('#159D98'); ORANGE=HexColor('#F46D36')

def fonts(font_dir=None):
    roots=([Path(font_dir)] if font_dir else [])+[Path('/usr/share/fonts/truetype/dejavu'),Path('C:/Windows/Fonts'),Path.home()/'AppData/Local/Microsoft/Windows/Fonts']
    for root in roots:
        a,b=root/'DejaVuSans.ttf',root/'DejaVuSans-Bold.ttf'
        if a.exists() and b.exists():
            pdfmetrics.registerFont(TTFont('BFVisual',str(a)))
            pdfmetrics.registerFont(TTFont('BFVisualBold',str(b)))
            return
    raise FileNotFoundError('DejaVu Sans regular and bold fonts missing')

def label(c,x,y,words,size=10,bold=False,color=INK):
    c.setFillColor(color);c.setFont('BFVisualBold' if bold else 'BFVisual',size)
    c.drawString(x,y,str(words))

def base(c,title,subtitle,page,color):
    c.setStrokeColor(color);c.setLineWidth(2);c.line(42,H-36,W-42,H-36)
    label(c,43,H-28,'MISTAKE MECHANICS / VISUAL LEARNING LAB',8,True,color)
    c.setFillColor(HexColor('#F4F8FC'));c.roundRect(42,H-139,W-84,85,13,fill=1,stroke=0)
    label(c,60,H-91,title,18,True);label(c,60,H-120,subtitle,9)
    label(c,43,25,'Illustrated practice • Draft for instructional review',8)
    label(c,W-81,25,page,9,True,color)

def segments(c,x,y,shade,fill):
    width=480/4
    for i in range(4):
        c.setFillColor(fill if i<shade else HexColor('#FFFFFF'))
        c.setStrokeColor(INK);c.setLineWidth(1)
        c.rect(x+i*width,y,width,44,stroke=1,fill=1)

def page_fractions(c):
    base(c,'Fraction Division: How Many Fit?','Compare one-half-sized groups with three-fourths.',1,ORANGE)
    label(c,55,610,'Example: 3/4 ÷ 1/2',16,True)
    label(c,55,580,'Shade three fourths of a whole.',10)
    segments(c,61,521,3,HexColor('#FFB682'))
    c.setStrokeColor(BLUE);c.setLineWidth(3);c.line(61,514,301,514);c.line(301,514,421,514)
    label(c,74,480,'One full group of 1/2',10,True,BLUE)
    label(c,312,452,'Half a group',10,True,BLUE)
    label(c,55,404,'3/4 contains one and one-half groups of size 1/2.',10)
    label(c,55,368,'3/4 ÷ 1/2 = 3/4 × 2/1 = 3/2 = 1 1/2',13,True,TEAL)
    label(c,55,307,'TRY: How many 1/4-liter bottles can you fill with 3/4 liter?',10,True)
    segments(c,61,226,3,HexColor('#B2E6E2'))
    label(c,55,177,'Explain your model:',10,True)
    for y in (150,122,94):c.setStrokeColor(HexColor('#B7C9D5'));c.line(55,y,548,y)
    c.showPage()

def page_inequalities(c):
    base(c,'Inequalities: Solution Detective','See solutions on the number line.',2,BLUE)
    label(c,55,610,'Example: x > -2',16,True)
    label(c,55,577,'A thermometer reading must be greater than -2 degrees.',10)
    x0,step,y=86,44,484
    c.setStrokeColor(INK);c.setLineWidth(2);c.line(x0,y,x0+10*step,y)
    for n in range(-5,6):
        x=x0+(n+5)*step;c.line(x,y-7,x,y+7);label(c,x-8,y-25,n,9)
    pivot=x0+3*step;c.setStrokeColor(ORANGE);c.setLineWidth(5);c.line(pivot+10,y,x0+10*step,y)
    c.setFillColor(HexColor('#FFFFFF'));c.circle(pivot,y,8,stroke=1,fill=1)
    label(c,55,414,'Open circle: -2 is excluded. Arrow right: greater values.',10,True)
    label(c,55,376,'TRY: Graph x ≤ 3. Use a filled circle because 3 is included.',11,True,TEAL)
    c.setStrokeColor(INK);c.setLineWidth(1.5);c.line(x0,287,x0+10*step,287)
    for n in range(-5,6):
        x=x0+(n+5)*step;c.line(x,280,x,294);label(c,x-8,261,n,9)
    label(c,55,199,'Explain your choice:',10,True)
    for yy in (167,130,93):c.setStrokeColor(HexColor('#B7C9D5'));c.line(55,yy,548,yy)
    c.showPage()

def page_statistics(c):
    base(c,'Statistics: Dot Plot Detective','Interpret grouped garage repair-time data.',3,TEAL)
    data=(2,3,3,4,4,4,5)
    label(c,55,610,'Tire inspection times, in minutes',12,True)
    label(c,55,580,'Data: 2, 3, 3, 4, 4, 4, 5',10)
    c.setStrokeColor(INK);c.line(90,420,522,420)
    for n in range(2,6):
        x=132+(n-2)*99;c.line(x,412,x,428);label(c,x-4,392,n,10)
        for i in range(data.count(n)):
            c.setFillColor(TEAL);c.circle(x,443+i*27,9,stroke=0,fill=1)
    label(c,55,334,'Mode: 4 minutes (three appearances).',10,True)
    label(c,55,300,'Median: 4 minutes (middle of seven values).',10)
    label(c,55,266,'Range: 5 - 2 = 3 minutes.',10)
    label(c,55,210,'TRY: Find the mean of the seven inspection times.',10,True)
    for yy in (168,132,96):c.setStrokeColor(HexColor('#B7C9D5'));c.line(55,yy,548,yy)
    c.showPage()

def generate(output,font_dir=None):
    fonts(font_dir);output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(output),pagesize=(W,H))
    for fn in (page_fractions,page_inequalities,page_statistics):fn(c)
    c.save()
    reader=PdfReader(str(output));writer=PdfWriter()
    for page in reader.pages:
        resources=page['/Resources']['/Font'].get_object()
        embedded=next((v for v in resources.values() if 'DejaVuSans' in str(v.get_object().get('/BaseFont','')) and 'Bold' not in str(v.get_object().get('/BaseFont',''))),None)
        if embedded is None:raise RuntimeError('Embedded regular font missing')
        for k,v in list(resources.items()):
            if str(v.get_object().get('/BaseFont'))=='/Helvetica':resources[k]=embedded
        writer.add_page(page)
    with output.open('wb') as stream:writer.write(stream)
    return output

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--font-dir')
    args=p.parse_args();print(generate(args.output,args.font_dir))
