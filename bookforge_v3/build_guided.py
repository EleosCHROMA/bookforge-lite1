"""Build a workbook with editable guided lessons before the answer keys."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from .pipeline import build
from .lesson_pages import validate_lessons
from .native_book import assemble
from .kdp_preflight import audit_pdf

def create(project,lessons,output,theme='clean-premium',font_dir=None):
    # font_dir retained for compatibility; renderer searches known system locations.
    if font_dir is not None:
        raise ValueError("Custom font_dir is not yet supported by the native assembler")
    result=assemble(project,lessons,output,theme)
    result['kdp_preflight']=audit_pdf(output)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('project',type=Path)
    p.add_argument('--lessons',type=Path,required=True)
    p.add_argument('--theme',choices=['clean-premium','playful-illustrated'],default='clean-premium')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(create(a.project,a.lessons,a.output,a.theme),indent=2))
