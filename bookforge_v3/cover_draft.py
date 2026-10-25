"""KDP paperback cover geometry and vector-draft generator.

The cover is a prototype. Verify in KDP's cover calculator and Print Previewer.
"""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter

SPINE_PER_PAGE={"premium-color":0.002347,"standard-color":0.002252,
                "bw-white":0.002252,"bw-cream":0.0025}
STYLES={"clean-premium":("#173753","#27859B","#F5F7F8"),
        "playful-illustrated":("#163558","#F4773D","#FFF8E9")}
PT=72

def geometry(pages,trim=(8.5,11),paper="premium-color"):
    if type(pages) is not int or not 24<=pages<=828:
        raise ValueError("Paperback page count must be 24..828")
    if paper not in SPINE_PER_PAGE:
        raise ValueError("Unknown paper type")
    if not (isinstance(trim,(list,tuple)) and len(trim)==2 and all(isinstance(x,(int,float)) and x>0 for x in trim)):
        raise ValueError("Invalid trim")
    spine=pages*SPINE_PER_PAGE[paper]
    return {"spine_in":spine,"width_in":2*trim[0]+spine+0.25,
            "height_in":trim[1]+0.25,"spine_text_allowed":pages>79}

def _fonts(folder=None):
    roots=([Path(folder)] if folder else [])+[Path("/usr/share/fonts/truetype/dejavu"),
           Path("C:/Windows/Fonts"),Path.home()/"AppData/Local/Microsoft/Windows/Fonts"]
    for root in roots:
        regular,bold=root/"DejaVuSans.ttf",root/"DejaVuSans-Bold.ttf"
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("CovRegular",str(regular)))
            pdfmetrics.registerFont(TTFont("CovBold",str(bold)))
            return
    raise FileNotFoundError("DejaVu Sans fonts not found")

def draft(output,pages=60,theme="playful-illustrated",title="MISTAKE MECHANICS",
          subtitle="GRADE 6 MATH",paper="premium-color",font_dir=None):
    if theme not in STYLES:raise ValueError("Unknown theme")
    if any(not isinstance(x,str) or not x.strip() for x in (title,subtitle)):
        raise ValueError("Title and subtitle required")
    config=geometry(pages,paper=paper);_fonts(font_dir)
    dark,accent,pale=map(HexColor,STYLES[theme])
    W,H=config["width_in"]*PT,config["height_in"]*PT
    right=0.125*PT+8.5*PT+config["spine_in"]*PT
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(path),pagesize=(W,H))
    c.setTitle(title+" (COVER DRAFT)")
    c.setFillColor(pale);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(dark);c.rect(right,0,W-right,H,fill=1,stroke=0)
    c.setFillColor(accent);c.roundRect(right+46,H-216,520,120,18,fill=1,stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    size=30
    while pdfmetrics.stringWidth(title,"CovBold",size)>495 and size>12:size-=1
    c.setFont("CovBold",size);c.drawString(right+59,H-146,title)
    c.setFont("CovBold",17);c.drawString(right+59,H-188,subtitle)
    c.setFont("CovBold",22);c.drawString(right+58,H-306,"FIND THE ERROR.")
    c.drawString(right+58,H-340,"FIX THE MATH.")
    c.setFont("CovRegular",14)
    for i,line in enumerate(("Repair tickets  |  Guided lessons",
                             "Visual models  |  Step-by-step practice",
                             "Answers collected at the back")):
        c.drawString(right+58,H-420-30*i,line)
    c.setFillColor(accent)
    for x,y,r in ((420,220,62),(515,138,42),(430,102,22)):
        c.circle(right+x,y,r,fill=1,stroke=0)
    c.setFillColor(dark);c.roundRect(65,H-215,502,130,17,fill=1,stroke=0)
    c.setFillColor(HexColor("#FFFFFF"));c.setFont("CovBold",22)
    c.drawString(88,H-136,"INSPECT. THINK. REPAIR.")
    c.setFont("CovRegular",12)
    c.drawString(88,H-175,"A hands-on math workshop for curious students.")
    c.setFillColor(dark);c.setFont("CovBold",17)
    c.drawString(85,H-283,"Inside the learning garage")
    c.setFont("CovRegular",12)
    for i,line in enumerate(("Six chapters of Grade 6 skill-building",
                             "Visual lessons and mistake-diagnosis tasks",
                             "Organized answer keys at the end")):
        c.drawString(88,H-324-35*i,line)
    # Intentionally blank for auto-placed KDP barcode on back cover.
    c.setFillColor(HexColor("#FFFFFF"));c.roundRect(8.5*PT-175,49,152,90,4,fill=1,stroke=0)
    c.showPage();c.save()
    reader=PdfReader(str(path));writer=PdfWriter()
    page=reader.pages[0];fm=page["/Resources"]["/Font"].get_object()
    regular=next((x for x in fm.values() if "DejaVuSans" in str(x.get_object().get("/BaseFont",""))
                  and "Bold" not in str(x.get_object().get("/BaseFont",""))),None)
    if regular is None:raise RuntimeError("Embedded cover font not found")
    for key,ref in list(fm.items()):
        if str(ref.get_object().get("/BaseFont",""))=="/Helvetica":fm[key]=regular
    writer.add_page(page)
    with path.open("wb") as out:writer.write(out)
    return config

if __name__=="__main__":
    import argparse
    import json
    p=argparse.ArgumentParser(description="Generate a KDP paperback cover draft")
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--pages",type=int,default=60)
    p.add_argument("--theme",choices=tuple(STYLES),default="playful-illustrated")
    p.add_argument("--paper",choices=tuple(SPINE_PER_PAGE),default="premium-color")
    p.add_argument("--title",default="MISTAKE MECHANICS")
    p.add_argument("--subtitle",default="GRADE 6 MATH")
    opts=p.parse_args()
    print(json.dumps(draft(opts.output,opts.pages,opts.theme,opts.title,opts.subtitle,opts.paper),indent=2))
