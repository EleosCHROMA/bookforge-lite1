"""Five misconception-based repair tickets; authored draft, not editorial approval."""
from copy import deepcopy
from fractions import Fraction
from statistics import mean

CASES = {
2: {"id":"2.P","topic":"Discount diagnosis","faulty_work":"25% off an $80 inspection means the customer pays $25.","diagnosis":"The student confused the discount rate with the final price.","instruction":"Calculate the savings, then the final sale price.","answer":"25% of $80 is $20; the final price is $80 - $20 = $60."},
3: {"id":"3.I","topic":"Inequality inspection","faulty_work":"At most 2,000 pounds is written as w < 2000.","diagnosis":"A strict inequality wrongly excludes the maximum allowed weight.","instruction":"Write the correct inequality and decide whether 2,000 is allowed.","answer":"w <= 2000. Equality is allowed, so 2,000 pounds is permitted."},
4: {"id":"4.C","topic":"Coordinate reflection","faulty_work":"Reflect (2,-4) across the x-axis to get (-2,-4).","diagnosis":"The student negated x; reflecting across the x-axis negates y.","instruction":"Identify the coordinate that changes and give the correct point.","answer":"Keep x = 2; negate y = -4. Correct point: (2,4)."},
5: {"id":"5.V","topic":"Volume repair","faulty_work":"A 2 x 3 x 4 inch box has a volume of 9 cubic inches.","diagnosis":"The student added the side lengths instead of multiplying.","instruction":"Calculate the correct volume and explain the units.","answer":"V = 2 x 3 x 4 = 24 cubic inches."},
6: {"id":"6.S","topic":"Mean versus median","faulty_work":"The mean of 5, 10, and 15 is 15.","diagnosis":"The student used the largest value instead of the arithmetic mean.","instruction":"Add the values and divide by the number of observations.","answer":"(5 + 10 + 15) / 3 = 10. The mean is 10."},
}

def independently_derived_answers():
    total=Fraction(80)
    saving=total*Fraction(25,100)
    avg=int(mean([5,10,15]))
    return {
        2:f"25% of $80 is ${saving}; the final price is $80 - ${saving} = ${total-saving}.",
        3:"w <= 2000. Equality is allowed, so 2,000 pounds is permitted.",
        4:f"Keep x = 2; negate y = -4. Correct point: ({2},{-(-4)}).",
        5:f"V = 2 x 3 x 4 = {2*3*4} cubic inches.",
        6:f"(5 + 10 + 15) / 3 = {avg}. The mean is {avg}.",
    }

def upgrade(project):
    book=deepcopy(project)
    chapters=book.get("chapters",[])
    if len(chapters)!=6 or [c.get("chapter_number") for c in chapters]!=list(range(1,7)):
        raise ValueError("Expected six sequential chapters")
    for n,ticket in CASES.items():
        existing=chapters[n-1].get("repair_tickets",[])
        if len(existing)!=1:
            raise ValueError(f"Chapter {n} must have exactly one existing ticket")
        if any(t.get("id")==ticket["id"] for c in chapters for t in c.get("repair_tickets",[])):
            raise ValueError("Duplicate repair-ticket ID")
        existing.append(deepcopy(ticket))
    book["editorial_review"]={}
    book["release_approvals"]={}
    book["content_status"]="draft_requires_editorial_review"
    return book

def audit(project):
    wanted={case["id"]:n for n,case in CASES.items()}
    found={}
    for chapter in project.get("chapters",[]):
        for ticket in chapter.get("repair_tickets",[]):
            key=ticket.get("id")
            if key in wanted:
                if key in found:raise ValueError("Duplicate upgraded repair ticket")
                found[key]=(chapter.get("chapter_number"),ticket)
    if not found:return {"checked":0,"expected":len(wanted)}
    if set(found)!=set(wanted):raise ValueError("Incomplete upgraded repair-ticket bank")
    derived=independently_derived_answers()
    for key,n in wanted.items():
        chapter,ticket=found[key]
        if chapter!=n:raise ValueError("Repair-ticket chapter mismatch")
        for field in ("topic","faulty_work","diagnosis","instruction"):
            if ticket.get(field)!=CASES[n][field]:
                raise ValueError(f"Repair ticket changed: {key} ({field})")
        if ticket.get("answer")!=derived[n]:
            raise ValueError(f"Incorrect repair-ticket solution: {key}")
    return {"checked":len(found),"expected":len(wanted)}
