"""Check extracted glyph bounding boxes against configured no-bleed margins.

This measures PDF text, not raster artwork, vector strokes, or physical printing.
"""
import argparse
import json
from math import isfinite
import pdfplumber
from bookforge_v3.kdp_preflight import GUTTER_RULES


def audit(path, outside_pt=18, tolerance_pt=.25):
    if not isfinite(outside_pt) or outside_pt < 18 or not 0 <= tolerance_pt <= 1:
        raise ValueError('Invalid geometry margin/tolerance')
    errors, pages = [], []
    total_chars = 0
    with pdfplumber.open(path) as pdf:
        count = len(pdf.pages)
        gutter_pt = next((value*72 for cap,value in GUTTER_RULES if count<=cap),63)
        for number,page in enumerate(pdf.pages,1):
            left,right = (gutter_pt,outside_pt) if number%2 else (outside_pt,gutter_pt)
            violations=[]
            bounds=[page.width,page.width,page.height,page.height]
            chars=[char for char in page.chars if char.get('text','').strip()]
            total_chars += len(chars)
            for char in chars:
                x0,x1,top,bottom=(char[key] for key in ('x0','x1','top','bottom'))
                if not all(isfinite(v) for v in (x0,x1,top,bottom)):
                    violations.append({'text':char['text'],'reason':'Non-finite glyph bounds'})
                    continue
                bounds=[min(bounds[0],x0),min(bounds[1],page.width-x1),
                        min(bounds[2],top),min(bounds[3],page.height-bottom)]
                if (x0 < left-tolerance_pt or x1 > page.width-right+tolerance_pt
                        or top < outside_pt-tolerance_pt or bottom > page.height-outside_pt+tolerance_pt):
                    violations.append({'text':char['text'],'box':[round(v,3) for v in (x0,top,x1,bottom)],
                                       'reason':'Glyph enters required margin'})
            if violations:
                errors.append(f'Page {number}: {len(violations)} glyphs violate safe margins')
            if not chars:
                errors.append(f'Page {number}: no extractable text; inspect blank/image page')
            pages.append({'page':number,'glyphs_checked':len(chars),'violations':len(violations),
                          'examples':violations[:12], 'required_left_pt':left,'required_right_pt':right,
                          'measured_minimum_margins_pt':dict(zip(('left','right','top','bottom'),(round(v,3) for v in bounds)))})
    if not pages:errors.append('No pages')
    return {'ok':not errors,'pages':len(pages),'glyphs_checked':total_chars,
            'required_inside_pt':gutter_pt,'required_outside_pt':outside_pt,
            'errors':errors,'page_reports':pages,
            'limitations':['Extracted glyph boxes only; vector strokes and images are not checked.',
                           'Does not certify KDP Previewer approval, typography, contrast, or content.']}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('pdf')
    parser.add_argument('--output')
    args=parser.parse_args()
    report=audit(args.pdf)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='page_reports'},indent=2))
    raise SystemExit(0 if report['ok'] else 1)
