"""Generate a configurable KDP paperback cover draft from the actual interior."""
import argparse
import json
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PT=72.0
BLEED=0.125
STOCK={"premium-color":0.002347,"standard-color":0.002252,
       "bw-white":0.002252,"bw-cream":0.0025}
THEMES={
 "clean-premium":{"dark":"#14354A","accent":"#188B9F","light":"#EDF6F8","accent2":"#92D2D9"},
 "playful-illustrated":{"dark":"#143656","accent":"#EE7044","light":"#FFF3E6","accent2":"#49B5AC"},
}

def font_setup():
    for root in (Path("/usr/share/fonts/truetype/dejavu"),Path("C:/Windows/Fonts"),
                 Path.home()/"AppData/Local/Microsoft/Windows/Fonts"):
        normal,bold=root/"DejaVuSans.ttf",root/"DejaVuSans-Bold.ttf"
        if normal.exists() and bold.exists():
            for name,file in (("BFV3Cover",normal),("BFV3CoverBold",bold)):
                if name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont(name,str(file)))
            return
    raise FileNotFoundError("DejaVu Sans regular and bold fonts required")

def interior_info(path,trim=(8.5,11)):
    reader=PdfReader(str(path))
    if reader.is_encrypted:raise ValueError("Encrypted interior unsupported")
    pages=len(reader.pages)
    if not 24<=pages<=828:raise ValueError("Paperback page count must be 24..828")
    for i,page in enumerate(reader.pages,1):
        size=float(page.mediabox.width)/PT,float(page.mediabox.height)/PT
        if any(abs(a-b)>.01 for a,b in zip(size,trim)):
            raise ValueError(f"Page {i} has trim {size}, expected {trim}")
    return pages

def geometry(pages,stock="premium-color",trim=(8.5,11)):
    if stock not in STOCK:raise ValueError("Unknown paper stock")
    if not 24<=pages<=828:raise ValueError("Invalid page count")
    spine=pages*STOCK[stock]
    return {"pages":pages,"stock":stock,"trim_width_in":trim[0],
            "trim_height_in":trim[1],"spine_in":spine,
            "cover_width_in":2*trim[0]+spine+2*BLEED,
            "cover_height_in":trim[1]+2*BLEED,"spine_text_allowed":pages>=80}

def artwork_dimensions(path,width_inches,height_inches):
    with Image.open(path) as img:width,height=img.size
    factor=max(width_inches*300/width,height_inches*300/height)
    effective=300/factor
    return {"pixels":[width,height],"effective_ppi_at_cover_fit":round(effective,1),
            "meets_300_ppi":effective>=300}

def crop_art(c,path,x,y,w,h):
    with Image.open(path) as img:iw,ih=img.size
    factor=max(w/iw,h/ih)
    sw,sh=iw*factor,ih*factor
    c.saveState()
    clip=c.beginPath();clip.rect(x,y,w,h)
    c.clipPath(clip,stroke=0,fill=0)
    c.drawImage(ImageReader(str(path)),x+(w-sw)/2,y+(h-sh)/2,sw,sh,mask="auto")
    c.restoreState()

def make_cover(interior,config,output,artwork=None):
    required={"title","subtitle","back_blurb","theme","paper_stock"}
    missing=sorted(required-set(config))
    if missing:raise ValueError("Missing cover metadata: "+", ".join(missing))
    for field in ("title","subtitle","back_blurb"):
        if not isinstance(config[field],str) or not config[field].strip():
            raise ValueError("Invalid "+field)
    if config["theme"] not in THEMES:raise ValueError("Unknown theme")
    trim=tuple(config.get("trim_inches",[8.5,11]))
    if trim!=(8.5,11):raise ValueError("This version supports 8.5x11 no-bleed only")
    pages=interior_info(interior,trim)
    geo=geometry(pages,config["paper_stock"],trim)
    if config.get("expected_pages") is not None and config["expected_pages"]!=pages:
        raise ValueError("Interior page count differs from metadata; update configuration")
    font_setup()
    scheme=THEMES[config["theme"]]
    dark,accent,light,alt=[HexColor(scheme[x]) for x in ("dark","accent","light","accent2")]
    tw=trim[0]*PT;spine=geo["spine_in"]*PT;bleed=BLEED*PT
    W=geo["cover_width_in"]*PT;H=geo["cover_height_in"]*PT
    front_x=bleed+tw+spine;back_x=bleed;safe=.375*PT
    art_report=None
    if artwork:
        artwork=Path(artwork)
        art_report=artwork_dimensions(artwork,3.05,3.15)
        if not art_report["meets_300_ppi"]:
            raise ValueError("Artwork below 300 effective PPI for its placement")
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
    c.setFillColor(light);c.rect(0,0,W,H,stroke=0,fill=1)
    c.setFillColor(dark);c.rect(front_x,0,tw+bleed,H,stroke=0,fill=1)
    c.setFillColor(accent);c.rect(bleed+tw,0,spine,H,stroke=0,fill=1)
    c.setFillColor(dark);c.roundRect(back_x+safe,H-180,tw-2*safe,104,16,stroke=0,fill=1)
    c.setFillColor(HexColor("#FFFFFF"));c.setFont("BFV3CoverBold",20)
    c.drawString(back_x+safe+22,H-117,"INSPECT. THINK. REPAIR.")
    c.setFont("BFV3Cover",11)
    c.drawString(back_x+safe+22,H-147,"A hands-on mathematics workshop")
    c.setFillColor(dark);c.setFont("BFV3CoverBold",16)
    c.drawString(back_x+safe,H-231,"Inside the learning garage")
    c.setFont("BFV3Cover",10.5)
    lines=simpleSplit(config["back_blurb"],"BFV3Cover",10.5,tw-2*safe)
    if len(lines)>8:raise ValueError("Back blurb too long")
    y=H-258
    for line in lines:
        c.drawString(back_x+safe,y,line);y-=17
    if y<185:raise ValueError("Back blurb enters barcode-safe region")
    barcode_x=bleed+tw-.35*PT-2*PT
    barcode_y=bleed+.35*PT
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(barcode_x,barcode_y,2*PT,1.2*PT,stroke=0,fill=1)
    c.setFillColor(accent);c.roundRect(front_x+safe,H-207,tw-2*safe,139,22,stroke=0,fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    title_size=31
    while pdfmetrics.stringWidth(config["title"],"BFV3CoverBold",title_size)>tw-2*safe-44 and title_size>=15:
        title_size-=1
    if title_size<15:raise ValueError("Title too long")
    c.setFont("BFV3CoverBold",title_size)
    c.drawCentredString(front_x+tw/2,H-130,config["title"])
    c.setFont("BFV3CoverBold",15);c.drawCentredString(front_x+tw/2,H-173,config["subtitle"])
    if artwork:
        aw=3.05*PT;ah=3.15*PT
        crop_art(c,artwork,front_x+tw/2-aw/2,222,aw,ah)
    else:
        c.setFillColor(alt)
        for cx,cy,r in ((front_x+tw*.35,340,77),(front_x+tw*.64,312,65),(front_x+tw*.54,425,44)):
            c.circle(cx,cy,r,stroke=0,fill=1)
            c.setFillColor(dark);c.circle(cx,cy,r*.42,stroke=0,fill=1);c.setFillColor(alt)
    c.setFillColor(HexColor("#FFFFFF"));c.setFont("BFV3CoverBold",19)
    c.drawCentredString(front_x+tw/2,169,"FIND THE ERROR. FIX THE MATH.")
    if config.get("author"):
        c.setFont("BFV3Cover",12);c.drawCentredString(front_x+tw/2,132,config["author"])
    # Deliberately omit spine text, even on eligible books, until manual design review.
    c.showPage();c.save()
    original=PdfReader(str(out));writer=PdfWriter()
    for page in original.pages:
        mapping=page["/Resources"]["/Font"].get_object()
        regular=next((ref for ref in mapping.values()
                      if "DejaVuSans" in str(ref.get_object().get("/BaseFont",""))
                      and "Bold" not in str(ref.get_object().get("/BaseFont",""))),None)
        if regular is None:raise RuntimeError("Embedded DejaVu font missing")
        for key,ref in list(mapping.items()):
            if str(ref.get_object().get("/BaseFont",""))=="/Helvetica":mapping[key]=regular
        writer.add_page(page)
    with out.open("wb") as stream:writer.write(stream)
    return {"draft_only":True,"interior_file":str(interior),"cover_file":str(out),
            **geo,"theme":config["theme"],"artwork":art_report,
            "barcode_reserved_in":[round(barcode_x/PT,4),round(barcode_y/PT,4),2,1.2],
            "manual_checks":["KDP Previewer","Final barcode placement","Metadata and rights","Print color proof"]}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--interior",required=True);ap.add_argument("--config",required=True)
    ap.add_argument("--output",required=True);ap.add_argument("--artwork");ap.add_argument("--report")
    a=ap.parse_args()
    result=make_cover(a.interior,json.loads(Path(a.config).read_text(encoding="utf-8")),a.output,a.artwork)
    if a.report:Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
