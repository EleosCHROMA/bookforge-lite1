"""Identify exact exercises still needing mathematical or editorial verification."""
import argparse
import json
from pathlib import Path

def review_queue(project):
    decimal_ids={x["problem_id"] for x in project.get("math_checks",[])}
    fraction_ids=set()
    for chapter in project.get("chapters",[]):
        for p in chapter.get("problems",[]):
            if p.get("id","").startswith("fraction_division_"):
                fraction_ids.add(p["id"])
    checks=decimal_ids|fraction_ids
    pending=[]
    for chapter in project.get("chapters",[]):
        for p in chapter["problems"]:
            if p["id"] not in checks:
                pending.append({"id":p["id"],
                                "chapter":chapter["chapter_number"],
                                "kind":p.get("kind","unclassified"),
                                "prompt":p["prompt"],
                                "reason":"No independent numeric/exact-fraction verification; manual reasoning review required"})
    repairs=[{"chapter":c["chapter_number"],"ticket_id":t["id"]}
             for c in project.get("chapters",[]) for t in c.get("repair_tickets",[])]
    return {"total_problems":sum(len(c["problems"]) for c in project["chapters"]),
            "numeric_check_records":len(decimal_ids),
            "fraction_bank_problem_ids":sorted(fraction_ids),
            "unverified_count":len(pending),
            "unverified_exercises":pending,
            "repair_tickets_for_editorial_review":repairs,
            "note":"Check records are not curriculum sign-off; all explanations, diagrams and repair tickets still need editorial verification."}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("project",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=review_queue(json.loads(a.project.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(f"Unverified exercises: {result['unverified_count']} / {result['total_problems']}")
