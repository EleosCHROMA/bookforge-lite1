"""Structural preflight for a matched no-bleed 8.5x11 interior and cover.

This does not constitute approval from KDP Print Previewer.
"""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader

PT=72.0
SPINE_PER_PAGE={"premium-color":0.002347,"standard-color":0.002252,
                "bw-white":0.002252,"bw-cream":0.0025}

def interior_pages(path):
    pdf=PdfReader(str(path))
    if pdf.is_encrypted:raise ValueError("Encrypted interior unsupported")
    n=len(pdf.pages)
    if not 24<=n<=828:raise ValueError("Paperback page count must be 24..828")
    for number,page in enumerate(pdf.pages,1):
        width,height=float(page.mediabox.width)/PT,float(page.mediabox.height)/PT
        if abs(width-8.5)>.01 or abs(height-11)>.01:
            raise ValueError(f"Interior page {number} is not no-bleed US Letter")
    return n

def cover_geometry(page_count,paper_stock="premium-color"):
    if paper_stock not in SPINE_PER_PAGE:raise ValueError("Unknown stock")
    if not 24<=page_count<=828:raise ValueError("Invalid page count")
    spine=page_count*SPINE_PER_PAGE[paper_stock]
    return {"pages":page_count,"stock":paper_stock,"spine_in":spine,
            "cover_width_in":17.25+spine,"cover_height_in":11.25,
            "spine_text_allowed":page_count>=80}

def paired_preflight(interior,cover,stock="premium-color"):
    pages=interior_pages(interior)
    geometry=cover_geometry(pages,stock)
    pdf=PdfReader(str(cover))
    errors=[]
    if len(pdf.pages)!=1:errors.append("Wraparound cover must contain one PDF page")
    for number,page in enumerate(pdf.pages,1):
        size=float(page.mediabox.width)/PT,float(page.mediabox.height)/PT
        expected=geometry["cover_width_in"],geometry["cover_height_in"]
        if any(abs(a-b)>.001 for a,b in zip(size,expected)):
            errors.append(f"Cover page {number} size {size} does not match {expected}")
        resources=page.get("/Resources")
        fonts=resources.get_object().get("/Font",{}) if resources else {}
        fonts=fonts.get_object() if hasattr(fonts,"get_object") else fonts
        for ref in fonts.values():
            font=ref.get_object()
            descriptor=font.get("/FontDescriptor")
            if descriptor is None or not any(k in descriptor.get_object()
                    for k in ("/FontFile","/FontFile2","/FontFile3")):
                errors.append(f"Unembedded cover font: {font.get('/BaseFont')}")
    return {"ok":not errors,"errors":errors,"interior_pages":pages,
            "spine_in":geometry["spine_in"],
            "expected_cover_size_in":[geometry["cover_width_in"],geometry["cover_height_in"]],
            "requires_manual_checks":["KDP Print Previewer","Cover text and trim safe areas",
                "Artwork rights, barcode placement, metadata match, print color proof"]}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--interior",required=True)
    p.add_argument("--cover",required=True)
    p.add_argument("--stock",default="premium-color")
    p.add_argument("--report")
    a=p.parse_args()
    report=paired_preflight(a.interior,a.cover,a.stock)
    if a.report:Path(a.report).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report["ok"] else 1)
