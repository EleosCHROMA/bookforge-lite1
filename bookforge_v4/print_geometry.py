"""Check text, conservative vector bounds and image PPI for no-bleed interiors.

Clipping, transparency, visual collisions and physical printing need review.
"""
import argparse
import json
from math import isfinite
import pdfplumber
from bookforge_v3.kdp_preflight import GUTTER_RULES


def audit(path, outside_pt=18, tolerance_pt=.25, minimum_image_ppi=300):
    if not isfinite(outside_pt) or outside_pt < 18 or not 0 <= tolerance_pt <= 1:
        raise ValueError('Invalid geometry margin/tolerance')
    if not isfinite(minimum_image_ppi) or minimum_image_ppi < 300:
        raise ValueError('Image resolution threshold must be at least 300 PPI')
    errors, pages = [], []
    total_chars = 0
    total_vectors = total_images = 0
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
            artwork_violations=[]
            vector_count=0
            image_details=[]
            for kind in ('line','rect','curve','image'):
                objects=page.images if kind=='image' else getattr(page,kind+'s')
                for obj in objects:
                    if kind!='image' and not (obj.get('stroke') or obj.get('fill')):
                        continue
                    if kind=='image':
                        total_images+=1
                    else:
                        total_vectors+=1
                        vector_count+=1
                    padding=0
                    if kind!='image' and obj.get('stroke'):
                        weight=float(obj.get('linewidth') or .5)
                        if not isfinite(weight) or weight<0:
                            artwork_violations.append({'kind':kind,'reason':'Invalid stroke width'})
                            continue
                        padding=weight/2
                    box=[obj['x0']-padding,obj['top']-padding,obj['x1']+padding,obj['bottom']+padding]
                    if not all(isfinite(v) for v in box):
                        artwork_violations.append({'kind':kind,'reason':'Non-finite artwork bounds'})
                        continue
                    if (box[0]<left-tolerance_pt or box[1]<outside_pt-tolerance_pt
                            or box[2]>page.width-right+tolerance_pt or box[3]>page.height-outside_pt+tolerance_pt):
                        artwork_violations.append({'kind':kind,'box':[round(v,3) for v in box],
                                                   'reason':'Artwork enters required margin'})
                    if kind=='image':
                        pixels=obj.get('srcsize')
                        width,height=obj['x1']-obj['x0'],obj['bottom']-obj['top']
                        if not pixels or len(pixels)!=2 or min(pixels)<=0 or min(width,height)<=0:
                            artwork_violations.append({'kind':kind,'reason':'Cannot determine image PPI'})
                            continue
                        ppi=min(pixels[0]*72/width,pixels[1]*72/height)
                        image_details.append({'effective_minimum_ppi':round(ppi,2),'pixels':list(pixels)})
                        if ppi+1e-6<minimum_image_ppi:
                            artwork_violations.append({'kind':kind,'effective_minimum_ppi':round(ppi,2),
                                                       'reason':'Image resolution below threshold'})
            if artwork_violations:
                errors.append(f'Page {number}: {len(artwork_violations)} artwork preflight violations')
            if violations:
                errors.append(f'Page {number}: {len(violations)} glyphs violate safe margins')
            if not chars:
                errors.append(f'Page {number}: no extractable text; inspect blank/image page')
            pages.append({'page':number,'glyphs_checked':len(chars),'violations':len(violations),
                          'examples':violations[:12], 'vector_objects_checked':vector_count,
                          'images_checked':len(page.images),'image_details':image_details,
                          'artwork_violations':len(artwork_violations),'artwork_examples':artwork_violations[:12],
                          'required_left_pt':left,'required_right_pt':right,
                          'measured_minimum_margins_pt':dict(zip(('left','right','top','bottom'),(round(v,3) for v in bounds)))})
    if not pages:errors.append('No pages')
    return {'ok':not errors,'pages':len(pages),'glyphs_checked':total_chars,
            'vector_objects_checked':total_vectors,'images_checked':total_images,
            'minimum_image_ppi':minimum_image_ppi,'required_inside_pt':gutter_pt,'required_outside_pt':outside_pt,
            'errors':errors,'page_reports':pages,
            'limitations':['Conservative vector bounding boxes include half the stroke width; clipping and visual collisions are not interpreted.',
                           'Image PPI uses placed bounding boxes; rotated or sheared images may require manual review.',
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
