"""Structural audit of the finished BookForge PDF (not editorial certification)."""
import argparse
import json
import re
from pathlib import Path
from pypdf import PdfReader

HEADER="MASTER MECHANIC GUIDE"
CHAPTER=re.compile(r"CHAPTER\s+(\d+)\s*[•|:–-]",re.I)
ANSWER=re.compile(r"^\s*(\d+)\.\s+\S",re.M)

def audit(pdf_path,project=None,expected_lessons=None,lesson_data=None):
    pdf=PdfReader(str(pdf_path))
    texts=[p.extract_text(extraction_mode="plain") or "" for p in pdf.pages]
    if not texts:
        return {"ok":False,"pages":0,"errors":["Empty PDF"],"warnings":[]}
    errors=[];warnings=[];locations={}
    summaries=[]
    for i,text in enumerate(texts,1):
        chapter=CHAPTER.search(text)
        summaries.append({"page":i,"chapter":int(chapter.group(1)) if chapter else None,
                          "answer":HEADER in text})
        if len(text.strip())<60:
            warnings.append(f"Page {i}: limited extractable text; inspect visually")
        if "REPAIR TICKET SOLUTIONS" in text and HEADER not in text:
            errors.append(f"Page {i}: repair solutions outside answer keys")
    index=next((i for i,t in enumerate(texts) if HEADER in t),None)
    if index is None:
        errors.append("Missing back-of-book answer keys")
        index=len(texts)
    if any(HEADER not in text for text in texts[index:]):
        errors.append("Non-answer page follows answer-key boundary")
    for i,text in enumerate(texts[:index],1):
        if "PRACTICE ANSWERS" in text:
            errors.append(f"Page {i}: answer list appears on student page")
    for title in expected_lessons or []:
        found=[i+1 for i,text in enumerate(texts[:index]) if title in text]
        locations[title]=found
        if len(found)!=1:
            errors.append(f"Guided lesson {title!r} appears {len(found)} times before answers")
    guided_checked = 0
    if lesson_data is not None:
        from .lesson_pages import validate_lessons
        validate_lessons(lesson_data)
        normalize = lambda text: " ".join(text.split())
        student_text = normalize("\n".join(texts[:index]))
        answer_text = normalize("\n".join(texts[index:]))
        for lesson in lesson_data["lessons"]:
            title = lesson["title"]
            expected_answers = lesson.get("guided_answers")
            if expected_answers is None:
                errors.append(f"Guided lesson {title!r}: missing source solutions")
                continue
            heading = normalize(f"Lesson {lesson['chapter_number']}: {title}")
            if answer_text.count(heading) != 1:
                errors.append(f"Guided lesson {title!r}: expected exactly one solution heading")
                continue
            start = answer_text.index(heading) + len(heading)
            following = re.search(r"Lesson \d+: ", answer_text[start:])
            end = start + following.start() if following else len(answer_text)
            block = answer_text[start:end]
            previous = -1
            for number, answer in enumerate(expected_answers, 1):
                normalized = normalize(answer)
                entry = f"{number}. {normalized}"
                position = block.find(entry)
                if position < 0 or position <= previous:
                    errors.append(f"Guided lesson {title!r}: missing or reordered solution {number}")
                else:
                    guided_checked += 1
                previous = position
                if normalized in student_text:
                    errors.append(f"Guided lesson {title!r}: student pages reveal solution {number}")
    if project is not None:
        for chapter in project.get("chapters",[]):
            number=chapter["chapter_number"]
            answers=[i for i,s in enumerate(summaries) if s["chapter"]==number and s["answer"]]
            if not answers:
                errors.append(f"Chapter {number}: missing answer page")
                continue
            content="\n".join(texts[i] for i in answers)
            numbers=[int(x) for x in ANSWER.findall(content)]
            expected=list(range(1,len(chapter["problems"])+1))
            if numbers!=expected:
                errors.append(f"Chapter {number}: answer numbers do not match {len(expected)} exercises (found {len(numbers)})")
            student_text=" ".join(texts[i] for i,summary in enumerate(summaries[:index]) if summary["chapter"]==number)
            student_text=" ".join(student_text.split())
            for ticket in chapter.get("repair_tickets",[]):
                diagnosis=" ".join(str(ticket.get("diagnosis","")).split())
                if diagnosis and diagnosis in student_text:
                    errors.append(f"Chapter {number}: student repair ticket reveals the supplied diagnosis")
                key=str(ticket.get("id",""))
                if not re.search(r"(?<![\w.])"+re.escape(key)+r"(?=\s|\.|$)",content):
                    errors.append(f"Chapter {number}: no back-of-book solution ID for repair ticket {key}")
            if not any(s["chapter"]==number for s in summaries[:index]):
                errors.append(f"Chapter {number}: missing student pages")
        ordered=[s["chapter"] for s in summaries[index:] if s["answer"] and s["chapter"] is not None]
        if ordered!=sorted(ordered):
            errors.append("Answer-key chapters out of order")
    return {"ok":not errors,"pages":len(texts),"answer_key_starts_at":index+1,
            "student_pages":index,"answer_pages":len(texts)-index,
            "errors":errors,"warnings":warnings,"lesson_locations":locations,
            "guided_solutions_checked":guided_checked,
            "status":"STRUCTURAL CHECK ONLY — human visual and editorial review required"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--pdf",required=True,type=Path)
    p.add_argument("--project",type=Path)
    p.add_argument("--lessons",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    project=json.loads(a.project.read_text(encoding="utf-8")) if a.project else None
    lesson_data=json.loads(a.lessons.read_text(encoding="utf-8")) if a.lessons else None
    titles=[x["title"] for x in lesson_data["lessons"]] if lesson_data else None
    result=audit(a.pdf,project,titles,lesson_data)
    output=json.dumps(result,indent=2)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(output,encoding="utf-8")
    print(output)
    raise SystemExit(0 if result["ok"] else 1)
