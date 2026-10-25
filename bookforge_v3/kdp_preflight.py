"""KDP paperback interior structural preflight; not a KDP Previewer substitute."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader

GUTTER_RULES=((150,.375),(300,.5),(500,.625),(700,.75),(828,.875))
TRIM_SIZES={'letter':(8.5,11),'6x9':(6,9),'8x10':(8,10)}

def audit_pdf(path, *, trim='letter', bleed=False):
    if trim not in TRIM_SIZES:
        raise ValueError('Unknown trim')
    pdf=PdfReader(str(path))
    count=len(pdf.pages)
    errors=[]
    if not 24 <= count <= 828:
        errors.append(f'Invalid paperback interior page count: {count}')
    gutter=next((value for cap,value in GUTTER_RULES if count<=cap),.875)
    outside=.375 if bleed else .25
    a,b=TRIM_SIZES[trim]
    expected=(a+(.125 if bleed else 0),b+(.25 if bleed else 0))
    for i,page in enumerate(pdf.pages,1):
        w,h=float(page.mediabox.width)/72,float(page.mediabox.height)/72
        if abs(w-expected[0])>.002 or abs(h-expected[1])>.002:
            errors.append(f'Page {i}: incorrect size {w:.3f} x {h:.3f} inches')
        resources=page.get('/Resources')
        fonts=resources.get_object().get('/Font',{}) if resources else {}
        fonts=fonts.get_object() if hasattr(fonts,'get_object') else fonts
        for font in fonts.values():
            obj=font.get_object()
            desc=obj.get('/FontDescriptor')
            details=desc.get_object() if desc else {}
            if not any(x in details for x in ('/FontFile','/FontFile2','/FontFile3')):
                errors.append(f'Page {i}: unembedded font {obj.get("/BaseFont")}')
    return {'ok':not errors,'pages':count,'trim':trim,'bleed':bleed,
            'required_inside_margin_in':gutter,'required_outside_margin_in':outside,
            'expected_pdf_size_in':list(expected),'errors':errors,
            'warnings':['Automated checks do not verify glyph placement, margins, artwork bleed, image DPI, or educational correctness; use KDP Previewer.']}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('pdf',type=Path)
    p.add_argument('--trim',choices=TRIM_SIZES,default='letter')
    p.add_argument('--bleed',action='store_true')
    args=p.parse_args()
    result=audit_pdf(args.pdf,trim=args.trim,bleed=args.bleed)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['ok'] else 1)
