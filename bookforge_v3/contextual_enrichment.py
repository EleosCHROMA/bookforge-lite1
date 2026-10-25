"""Original contextual math questions with instructor worked-solution notes.

These are draft instructional examples. Correctness checks are separate from
pedagogical review and standards certification.
"""
from copy import deepcopy
from fractions import Fraction

CONTEXTUAL = (
 (1,"word_problem","A repair shop has 3/4 liter of coolant. Each refill uses 1/8 liter. How many complete refills can it make?","6","3/4 divided by 1/8 = 3/4 x 8/1 = 6.","6.NS.1"),
 (1,"error_analysis","A technician claims 2/3 divided by 1/3 equals 2/9. Explain the error and find the correct quotient.","2","Instead of multiplying the fractions, multiply 2/3 by the reciprocal 3/1 to get 2.","6.NS.1"),
 (2,"word_problem","A shop sells 3 identical filters for $27. What would 7 filters cost at the same rate?","$63","The unit price is $27 divided by 3 = $9. Multiply $9 by 7 = $63.","6.RP.3"),
 (2,"explanation","A sale reduces a $80 inspection by 25%. What is the final price? Explain both steps.","$60","25% of $80 is $20. Subtract the discount: $80 - $20 = $60.","6.RP.3"),
 (3,"word_problem","A technician earns $18 per hour. Write the total earnings for h hours, then evaluate when h = 4.","18h; $72 when h = 4","The variable expression is 18h. Substituting h = 4 gives 18 x 4 = 72.","6.EE.6"),
 (3,"explanation","A lift can safely hold at most 2,000 pounds. Write an inequality for vehicle weight w and explain whether 2,000 is allowed.","w <= 2000; yes","At most includes the boundary: w <= 2000. Equality means 2,000 pounds is permitted.","6.EE.8"),
 (4,"modeling","A car is parked at (-3, 2). It moves 5 units right. What are its new coordinates?","(2, 2)","Increase the x-coordinate by 5: -3 + 5 = 2. The y-coordinate remains 2.","6.NS.8"),
 (4,"explanation","Which value is colder, -6 degrees or -2 degrees? Explain using a number line.","-6 degrees","-6 is farther left on the number line than -2, so -6 is smaller.","6.NS.7"),
 (5,"word_problem","A storage crate is 2.5 feet long, 1.5 feet wide, and 2 feet tall. Find its volume.","7.5 cubic feet","Multiply length x width x height: 2.5 x 1.5 x 2 = 7.5 cubic feet.","6.G.2"),
 (5,"error_analysis","A mechanic finds triangle area using base 10 and height 6 and reports 60 square inches. Diagnose and correct.","30 square inches","Area of a triangle is half the base times the height: 1/2 x 10 x 6 = 30.","6.G.1"),
 (6,"word_problem","Five repair jobs took 10, 15, 15, 20, and 25 minutes. What is their mean time?","17 minutes","Add times to obtain 85, then divide by 5 jobs: 85 / 5 = 17 minutes.","6.SP.3"),
 (6,"explanation","A dot plot has 1 dot at 2, 3 dots at 3, and 2 dots at 4. What is the mode and why?","3","The mode is 3 because it occurs three times, more often than 2 or 4.","6.SP.4"),
)

def enrich_context(project):
    """Return a new draft with 12 contextual tasks and worked answers."""
    book=deepcopy(project)
    if len(book.get("chapters", []))!=6:
        raise ValueError("Expected exactly six existing chapters")
    existing={p["id"] for ch in book["chapters"] for p in ch["problems"]}
    for chapter_number,kind,prompt,answer,steps,standard in CONTEXTUAL:
        chapter=book["chapters"][chapter_number-1]
        if chapter.get("chapter_number")!=chapter_number:
            raise ValueError("Chapters must be sequential")
        item_id=f"context_{chapter_number}_{sum(1 for x in CONTEXTUAL if x[0]==chapter_number and CONTEXTUAL.index(x)<=CONTEXTUAL.index((chapter_number,kind,prompt,answer,steps,standard))):02d}"
        if item_id in existing:raise ValueError("Contextual content already added")
        existing.add(item_id)
        chapter["problems"].append({
            "id":item_id,"kind":kind,"prompt":prompt,
            "hint":"Explain your reasoning and show each step.",
            "candidate_standards":[standard],"standard_reviewed":False,
        })
        chapter["answers"][item_id]=f"{answer}. {steps}"
    book["editorial_review"]={}
    book["content_status"]="draft_requires_editorial_review"
    return book
