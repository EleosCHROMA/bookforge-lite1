"""Separate automated answer checks from mandatory editorial reviews."""
import argparse
import json
from pathlib import Path
from .foundation_audit import CASES as FOUNDATION

def review_queue(project):
    decimal_ids={x["problem_id"] for x in project.get("math_checks",[])}
    questions=[(ch,p) for ch in project.get("chapters",[]) for p in ch.get("problems",[])]
    fraction_ids={p["id"] for ch,p in questions if p.get("id","").startswith("fraction_division_")}
    contextual_ids={p["id"] for ch,p in questions if p.get("id","").startswith("context_")}
    foundation_ids={p["id"] for ch,p in questions if p.get("id") in FOUNDATION}
    checks=decimal_ids|fraction_ids|contextual_ids|foundation_ids
    pending_numeric=[]
    human_review=[]
    approvals=project.get("individual_exercise_reviews",{})
    if not isinstance(approvals,dict):approvals={}
    for chapter,p in questions:
        item={"id":p["id"],"chapter":chapter["chapter_number"],
              "kind":p.get("kind","unclassified"),"prompt":p["prompt"]}
        if p["id"] not in checks:
            pending_numeric.append(item)
        approval=approvals.get(p["id"])
        if not isinstance(approval,dict) or not str(approval.get("reviewer","")).strip():
            human_review.append(item)
    repairs=[{"chapter":c["chapter_number"],"ticket_id":t["id"]}
             for c in project.get("chapters",[]) for t in c.get("repair_tickets",[])]
    return {"total_problems":len(questions),
            "numeric_check_records":len(decimal_ids),
            "fraction_bank_problem_ids":sorted(fraction_ids),
            "contextual_check_problem_ids":sorted(contextual_ids),
            "foundation_check_problem_ids":sorted(foundation_ids),
            "unverified_count":len(pending_numeric),
            "unverified_exercises":pending_numeric,
            "human_review_required_count":len(human_review),
            "human_review_required_exercises":human_review,
            "repair_tickets_for_editorial_review":repairs,
            "note":"Automated answers are computational checks, NOT independently approved instructional content. Human editorial review remains required."}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("project",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=review_queue(json.loads(a.project.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(f"Unchecked answers: {result['unverified_count']}; pending human review: {result['human_review_required_count']} / {result['total_problems']}")
