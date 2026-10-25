"""Strict human-approval release gate for KDP candidate PDFs.

This does not approve, upload or publish anything. It requires explicit reviewer
attestations instead of trusting automatically generated editorial booleans.
"""
import argparse
import json
from pathlib import Path
from .quality import analyze, REQUIRED_REVIEWS
from .kdp_preflight import audit_pdf

def evaluate(project,pdf_path=None,require_full_curriculum=False):
    qa=analyze(project)
    blockers=list(qa["errors"])
    approvals=project.get("release_approvals",{})
    if not isinstance(approvals,dict):
        blockers.append("release_approvals must be an object")
        approvals={}
    for role in REQUIRED_REVIEWS:
        entry=approvals.get(role)
        if not isinstance(entry,dict) or not all(
            isinstance(entry.get(k),str) and entry[k].strip()
            for k in ("reviewer","reviewed_at","notes")
        ):
            blockers.append(f"Missing human attestation: {role}")
    standard=qa.get("standards_audit",{})
    if require_full_curriculum and standard.get("standards_verified_in_metadata",0)<standard.get("standards_total",29):
        blockers.append("Comprehensive Grade 6 claim is not supported by reviewed standards metadata")
    if qa["statistics"].get("math_checks_remaining",0):
        blockers.append(f'{qa["statistics"]["math_checks_remaining"]} exercise answers lack automatic numeric checks and need documented individual review')
    individual=project.get("individual_exercise_reviews",{})
    if not isinstance(individual,dict): individual={}
    uncovered={p.get("id") for ch in project.get("chapters",[]) for p in ch.get("problems",[])}
    unreviewed=[p for p in sorted(uncovered) if not isinstance(individual.get(p),dict)
         or not isinstance(individual[p].get("reviewer"),str)
         or not individual[p]["reviewer"].strip()]
    if unreviewed:
        blockers.append(f"{len(unreviewed)} exercises lack documented individual reviews")
    if pdf_path is None:
        blockers.append("No final interior PDF supplied for print preflight")
        preflight=None
    else:
        preflight=audit_pdf(pdf_path)
        blockers.extend(preflight["errors"])
    return {"ready_for_release":not blockers,
            "blockers":blockers,"exercise_reviews_required":len(unreviewed),
            "print_preflight":preflight,
            "warning":"Approval metadata represents editor attestations and is not automatically verified against reviewer identity or PDF content."}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("project",type=Path)
    p.add_argument("--pdf",type=Path)
    p.add_argument("--full-curriculum",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=evaluate(json.loads(args.project.read_text(encoding="utf-8")),args.pdf,args.full_curriculum)
    doc=json.dumps(result,indent=2)+"\n"
    if args.output:args.output.write_text(doc,encoding="utf-8")
    print(doc)
    raise SystemExit(0 if result["ready_for_release"] else 1)
