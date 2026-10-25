"""Export a human-readable and JSON curriculum review report.

Usage:
  python -m bookforge_v3.curriculum_report project.json --output report.json
"""
import argparse
import json
from pathlib import Path
from .standards_audit import report, STANDARDS

def build_report(project):
    result=report(project)
    chapter_counts=[]
    for ch in project.get("chapters", []):
        problems=ch.get("problems", [])
        chapter_counts.append({"chapter":ch.get("chapter_number"),"title":ch.get("chapter_title"),"exercises":len(problems),
                               "kind_labeled":sum(p.get("kind") is not None for p in problems)})
    result["chapters"]=chapter_counts
    result["unverified_standards_details"]=[
        {"code":code,"topic":STANDARDS[code]} for code in result["standards_without_verified_exercises"]
    ]
    return result

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("project",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args(argv)
    data=json.loads(args.project.read_text(encoding="utf-8"))
    result=build_report(data)
    rendered=json.dumps(result,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered,encoding="utf-8")
    print(f"Exercises: {sum(c['exercises'] for c in result['chapters'])}")
    print(f"Editor-verified grade 6 standards: {result['standards_verified_in_metadata']}/{result['standards_total']}")
    print(f"Duplicate question prompts: {len(result['duplicate_prompt_pairs'])}")
    print(f"Questions missing kind labels: {len(result['exercises_missing_kind'])}")
    print("This is metadata verification, NOT a curriculum certification.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
