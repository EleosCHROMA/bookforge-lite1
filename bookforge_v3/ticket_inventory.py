"""Inventory all repair tickets without implying instructional approval."""
import argparse
import json
from pathlib import Path

REQUIRED=("id","topic","faulty_work","diagnosis","instruction","answer")

def inventory(project,expected_per_chapter=None):
    errors=[];counts={};seen=set();tickets=[]
    for chapter in project.get("chapters",[]):
        number=chapter.get("chapter_number")
        items=chapter.get("repair_tickets",[])
        if not isinstance(items,list):
            errors.append(f"Chapter {number}: repair_tickets is not a list")
            continue
        counts[str(number)]=len(items)
        if expected_per_chapter is not None and len(items)!=expected_per_chapter:
            errors.append(f"Chapter {number}: expected {expected_per_chapter} tickets, found {len(items)}")
        for ticket in items:
            if not isinstance(ticket,dict):
                errors.append(f"Chapter {number}: invalid ticket object")
                continue
            key=ticket.get("id")
            if not isinstance(key,str) or not key.strip():
                errors.append(f"Chapter {number}: missing ticket ID")
            elif key in seen:
                errors.append(f"Duplicate ticket ID: {key}")
            else:
                seen.add(key)
            for field in REQUIRED:
                val=ticket.get(field)
                if not isinstance(val,str) or not val.strip():
                    errors.append(f"Ticket {key}: missing {field}")
            if isinstance(ticket.get("faulty_work"),str) and ticket.get("faulty_work")==ticket.get("answer"):
                errors.append(f"Ticket {key}: faulty work equals corrected answer")
            tickets.append({"chapter":number,"id":key,"topic":ticket.get("topic")})
    return {"ok":not errors,"errors":errors,"tickets":tickets,
            "total_tickets":len(tickets),"counts_by_chapter":counts,
            "editorial_status":"UNREVIEWED"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("project",type=Path)
    p.add_argument("--expected-per-chapter",type=int)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=inventory(json.loads(args.project.read_text(encoding="utf-8")),args.expected_per_chapter)
    rendered=json.dumps(result,indent=2)+"\n"
    if args.output:args.output.write_text(rendered,encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if result["ok"] else 1)
