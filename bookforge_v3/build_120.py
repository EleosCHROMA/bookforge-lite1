"""Build 120-question draft from the 108-question expansion."""
import argparse
import json
from pathlib import Path
from .expand_workbook import expand
from .fraction_enrichment import enrich

def create(base):
    return enrich(expand(base))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("input",type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    original=json.loads(args.input.read_text(encoding="utf-8"))
    expanded=create(original)
    args.output.write_text(json.dumps(expanded,indent=2)+"\n",encoding="utf-8")
    print(f"Created {sum(len(x['problems']) for x in expanded['chapters'])} exercises.")
