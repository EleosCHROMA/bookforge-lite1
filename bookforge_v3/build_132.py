"""Build a 132-exercise draft with fraction division and contextual reasoning."""
import argparse
import json
from pathlib import Path
from .build_120 import create as build_120
from .contextual_enrichment import enrich_context

def create(base):
    return enrich_context(build_120(base))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("input",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    book=create(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(book,indent=2)+"\n",encoding="utf-8")
    print(f"Created {sum(len(ch['problems']) for ch in book['chapters'])} exercises.")
