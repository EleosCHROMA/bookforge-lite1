"""Build a workbook with editable guided lessons before the answer keys."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from .pipeline import build
from .lesson_pages import attach,validate_lessons
from .kdp_preflight import audit_pdf

def create(project,lessons,output,theme='clean-premium',font_dir=None):
    data=validate_lessons(json.loads(Path(lessons).read_text(encoding='utf-8')))
    with TemporaryDirectory() as tmp:
        base=Path(tmp)/'base.pdf'
        build(project,base,theme)
        result=attach(base,data,output,theme,font_dir)
    result['kdp_preflight']=audit_pdf(output)
    if not result['kdp_preflight']['ok']:
        Path(output).unlink(missing_ok=True)
        raise RuntimeError('KDP preflight failed')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('project',type=Path)
    p.add_argument('--lessons',type=Path,required=True)
    p.add_argument('--theme',choices=['clean-premium','playful-illustrated'],default='clean-premium')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(create(a.project,a.lessons,a.output,a.theme),indent=2))
