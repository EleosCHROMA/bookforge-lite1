"""Single-pass chapter assembly with native page numbers, no number overlays."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from .pipeline import validate_project, V2_ROOT
from .quality import analyze
from .lesson_pages import render, validate_lessons
from .guided_answers import render_answers
from .kdp_preflight import audit_pdf

def assemble(project_path, lessons_path, output_path, theme="clean-premium"):
    project=validate_project(json.loads(Path(project_path).read_text(encoding="utf-8")))
    qa=analyze(project)
    if not qa["ready_for_build"]:
        raise ValueError("Content QA failed: "+"; ".join(qa["errors"]))
    spec=validate_lessons(json.loads(Path(lessons_path).read_text(encoding="utf-8")))
    if theme not in ("clean-premium","playful-illustrated"):
        raise ValueError("Unknown theme")
    if str(V2_ROOT) not in sys.path:sys.path.insert(0,str(V2_ROOT))
    from themes import (fonts,playful_opener,playful_worksheet,premium_opener,
        premium_worksheet,ticket_page,render_section,worksheet_batches,W,H)
    chapters=project["chapters"]
    numbers={x["chapter_number"] for x in chapters}
    by_chapter={}
    for lesson in spec["lessons"]:
        number=lesson.get("chapter_number")
        if type(number) is not int or number not in numbers:
            raise ValueError("Each lesson needs a valid chapter_number")
        by_chapter.setdefault(number,[]).append(lesson)
    if any("guided_answers" not in lesson for lesson in spec["lessons"]):
        raise ValueError("Native workbook requires guided_answers for every lesson")
    fonts()
    dest=Path(output_path);dest.parent.mkdir(parents=True,exist_ok=True)
    pages=[];number=1
    with TemporaryDirectory() as t:
        root=Path(t)
        for chapter in chapters:
            chno=chapter["chapter_number"]
            p=root/f"opener-{chno}.pdf"
            c=canvas.Canvas(str(p),pagesize=(W,H))
            (premium_opener if theme=="clean-premium" else playful_opener)(c,chapter,number)
            c.save();pages.extend(PdfReader(str(p)).pages);number+=1
            assigned=by_chapter.get(chno,[])
            if assigned:
                p=root/f"lesson-{chno}.pdf"
                render({"lessons":assigned},p,theme,page_numbers=list(range(number,number+len(assigned))))
                pages.extend(PdfReader(str(p)).pages);number+=len(assigned)
            p=root/f"practice-{chno}.pdf"
            c=canvas.Canvas(str(p),pagesize=(W,H))
            for i,group in enumerate(worksheet_batches(chapter["problems"])):
                subset=dict(chapter,problems=group,_practice_offset=i*6)
                (premium_worksheet if theme=="clean-premium" else playful_worksheet)(c,subset,number)
                number+=1
            ticket_page(c,chapter,number,theme);number+=1
            c.save();pages.extend(PdfReader(str(p)).pages)
        first_answer=number
        for chapter in chapters:
            p=root/f"answers-{chapter['chapter_number']}.pdf"
            render_section(chapter,p,theme,"answers",number)
            group=PdfReader(str(p)).pages
            pages.extend(group);number+=len(group)
        p=root/"guided-answers.pdf"
        render_answers(spec,p,theme,number)
        group=PdfReader(str(p)).pages
        pages.extend(group);number+=len(group)
        writer=PdfWriter()
        for page in pages:writer.add_page(page)
        for page in writer.pages:
            resources=page.get("/Resources")
            fonts_ref=resources.get_object().get("/Font") if resources else None
            if not fonts_ref:continue
            fontmap=fonts_ref.get_object()
            embedded=next((ref for ref in fontmap.values()
                if "DejaVuSans" in str(ref.get_object().get("/BaseFont",""))
                and "Bold" not in str(ref.get_object().get("/BaseFont",""))),None)
            if embedded is not None:
                for key,ref in list(fontmap.items()):
                    if str(ref.get_object().get("/BaseFont",""))=="/Helvetica":fontmap[key]=embedded
        with dest.open("wb") as f:writer.write(f)
    audit=audit_pdf(dest)
    if not audit["ok"]:
        dest.unlink(missing_ok=True)
        raise ValueError("KDP preflight failed: "+"; ".join(audit["errors"]))
    return {"output":str(dest),"pages":number-1,"answer_key_page":first_answer,
            "lessons":sum(len(x) for x in by_chapter.values()),"theme":theme,
            "qa":qa["statistics"]}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("project",type=Path)
    p.add_argument("--lessons",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--theme",choices=("clean-premium","playful-illustrated"),default="clean-premium")
    a=p.parse_args()
    print(json.dumps(assemble(a.project,a.lessons,a.output,a.theme),indent=2))
