"""Reproducible 132-exercise manuscript with five extra repair tickets."""
import argparse
import json
from pathlib import Path
from .build_132 import create as create_132
from .repair_upgrade import upgrade,audit

def create(base):
    result=upgrade(create_132(base))
    audit(result)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    original=json.loads(a.input.read_text(encoding="utf-8"))
    book=create(original)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(book,indent=2)+"\n",encoding="utf-8")
    print(f"Created {sum(len(c['problems']) for c in book['chapters'])} exercises and {sum(len(c['repair_tickets']) for c in book['chapters'])} repair tickets")
