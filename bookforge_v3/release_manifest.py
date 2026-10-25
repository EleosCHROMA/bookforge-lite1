"""Fingerprinted handoff for matching workbook interior/cover files.

A structural pass is not permission to publish; editorial approvals and KDP
Previewer must still be handled by a real reviewer.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from .paired_cover_preflight import paired_preflight

REVIEWS=("mathematics","pedagogy","proofreading","print_preview")

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def manifest(project_file, interior, cover, stock="premium-color", cover_config=None):
    project_file,interior,cover=map(Path,(project_file,interior,cover))
    book=json.loads(project_file.read_text(encoding="utf-8"))
    if not isinstance(book,dict) or not isinstance(book.get("chapters"),list):
        raise ValueError("Project requires chapters")
    paths=[project_file,interior,cover]
    blockers=[]
    config=None
    if cover_config:
        path=Path(cover_config)
        paths.append(path)
        config=json.loads(path.read_text(encoding="utf-8"))
        if config.get("paper_stock")!=stock:
            blockers.append("Cover config stock differs from checked stock")
    try:
        matched=paired_preflight(interior,cover,stock)
    except (ValueError,OSError,TypeError,KeyError) as exc:
        matched={"ok":False,"errors":[str(exc)]}
    blockers.extend(matched["errors"])
    attestations=book.get("release_approvals",{})
    if not isinstance(attestations,dict):attestations={}
    for review in REVIEWS:
        item=attestations.get(review)
        if not isinstance(item,dict) or not all(isinstance(item.get(k),str)
             and item[k].strip() for k in ("reviewer","reviewed_at","notes")):
            blockers.append("Missing documented editorial approval: "+review)
    reviewed=book.get("individual_exercise_reviews",{})
    if not isinstance(reviewed,dict):reviewed={}
    problems=[p.get("id") for ch in book["chapters"] for p in ch.get("problems",[])]
    missing=sum(not isinstance(reviewed.get(p),dict) or
                not str(reviewed[p].get("reviewer","")).strip() for p in problems)
    if missing:blockers.append(f"{missing} exercises lack documented individual review")
    return {
       "schema_version":1,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
       "files":{str(p):{"sha256":sha256(p),"bytes":p.stat().st_size} for p in paths},
       "exercise_count":len(problems),"paired_preflight":matched,
       "metadata":{"stock":stock,"cover_config":config},
       "ready_for_structural_review":bool(matched["ok"]),
       "ready_for_publication":False,
       "blockers":blockers,
       "manual_requirements":["Verify exact files in KDP Print Previewer",
           "Complete independent editorial review and approval",
           "Confirm final metadata, rights, barcode position and print proof"],
       "warning":"Hashes bind a report to exact file bytes; they do not certify content or authorize publication."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True)
    p.add_argument("--interior",required=True)
    p.add_argument("--cover",required=True)
    p.add_argument("--stock",default="premium-color")
    p.add_argument("--config")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=manifest(a.project,a.interior,a.cover,a.stock,a.config)
    target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("Paired structural check:", "PASS" if result["ready_for_structural_review"] else "FAIL")
    print("Publication: BLOCKED pending verified editorial and KDP approval")
    raise SystemExit(0 if result["ready_for_structural_review"] else 1)
