"""Place guided lessons after their chapter openers; restamp visible page numbers."""
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter
from .lesson_pages import render, validate_lessons, W, H, M

def chapter_boundaries(project, total_pages, first_answer):
    starts, position = {}, 0
    for chapter in project["chapters"]:
        number = chapter["chapter_number"]
        if number in starts: raise ValueError("Duplicate chapter number")
        starts[number] = position
        position += 2 + ceil(len(chapter["problems"]) / 6)
    if position != first_answer or first_answer >= total_pages:
        raise ValueError("Chapter body-page count does not match answer-key boundary")
    return starts

def overlay_page_number(page, number, theme):
    """Opaque visual overlay. Old hidden numbers may remain text-extractable."""
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(W,H))
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(W-M-31,12,45,34,fill=1,stroke=0)
    c.setFillColor(HexColor("#F16B32" if theme=="playful-illustrated" else "#286E9C"))
    c.circle(W-M-9,28,11,fill=1,stroke=0)
    c.setFillColor(HexColor("#FFFFFF"));c.setFont("LessonBold",8)
    c.drawCentredString(W-M-9,25,str(number));c.save();stream.seek(0)
    stamp = PdfReader(stream).pages[0]
    mapping = stamp["/Resources"]["/Font"].get_object()
    embedded = next((v for v in mapping.values()
                     if "DejaVuSans" in str(v.get_object().get("/BaseFont",""))),None)
    if embedded is None: raise RuntimeError("Page numbering font is not embedded")
    for key,ref in list(mapping.items()):
        if str(ref.get_object().get("/BaseFont"))=="/Helvetica":
            mapping[key]=embedded
    page.merge_page(stamp)
    return page

def insert_by_chapter(interior, project, lesson_data, output, theme="clean-premium", font_dir=None):
    validate_lessons(lesson_data)
    reader=PdfReader(str(interior))
    keys=[i for i,p in enumerate(reader.pages)
          if "MASTER MECHANIC GUIDE" in (p.extract_text() or "")]
    if not keys: raise ValueError("Answer-key section not found")
    boundary=keys[0]
    starts=chapter_boundaries(project,len(reader.pages),boundary)
    assigned={}
    for lesson in lesson_data["lessons"]:
        number=lesson.get("chapter_number")
        if type(number) is not int or number not in starts:
            raise ValueError("Each guided lesson requires a valid chapter_number")
        assigned.setdefault(number,[]).append(lesson)
    with TemporaryDirectory() as temp:
        inserts={}
        for number,items in assigned.items():
            lesson_pdf=render({"lessons":items},Path(temp)/f"{number}.pdf",theme,font_dir)
            inserts[starts[number]+1]=list(PdfReader(str(lesson_pdf)).pages)
        pages=[]
        for i,page in enumerate(reader.pages):
            pages.extend(inserts.get(i,[]))
            pages.append(page)
        writer=PdfWriter()
        for i,page in enumerate(pages,1):
            writer.add_page(overlay_page_number(page,i,theme))
        target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("wb") as fh:writer.write(fh)
    return {"output":str(target),"pages":len(pages),
            "lesson_pages":sum(map(len,inserts.values())),
            "answer_key_page":boundary+sum(map(len,inserts.values()))+1,
            "placed_by_chapter":{str(num):len(items) for num,items in assigned.items()},
            "page_numbering":"visual overlay; old numbers remain text-extractable"}
