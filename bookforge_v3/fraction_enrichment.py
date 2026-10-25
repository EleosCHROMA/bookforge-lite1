"""Create a new six-chapter draft with a fraction-division section."""
from copy import deepcopy
from .fraction_division import make_exercises

def enrich(project):
    book = deepcopy(project)
    chapters=book.get("chapters", [])
    if len(chapters)!=6 or chapters[0].get("chapter_number")!=1:
        raise ValueError("Expected six chapters beginning with chapter 1")
    chapter=chapters[0]
    ids={p["id"] for ch in chapters for p in ch["problems"]}
    new=make_exercises()
    if any(item["id"] in ids for item in new):
        raise ValueError("Fraction division was already added")
    chapter["chapter_title"]="Number Operations: Decimals & Fractions"
    chapter["objectives"]=[
        "Operate accurately with decimals.",
        "Divide fractions using models and reciprocals.",
        "Explain and correct fraction-division mistakes.",
    ]
    chapter["introduction"]="Investigate decimals and fractions at the learning garage."
    for item in new:
        chapter["problems"].append({k:v for k,v in item.items()
                                    if k not in ("answer","exact_numerator","exact_denominator")})
        chapter["answers"][item["id"]]=item["answer"]
    chapter["repair_tickets"].append({
        "id":"1.F", "topic":"Fraction division",
        "faulty_work":"3/4 divided by 1/2 = 3/8.",
        "diagnosis":"Multiplied by the divisor instead of its reciprocal.",
        "instruction":"Explain the correct steps and repair the answer.",
        "answer":"3/4 x 2/1 = 3/2 = 1 1/2.",
    })
    book["editorial_review"]={}
    book["content_status"]="draft_requires_editorial_review"
    return book
