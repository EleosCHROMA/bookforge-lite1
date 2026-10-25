"""Check paper size and embedded fonts in BookForge interior PDFs."""
import argparse
from pathlib import Path
from pypdf import PdfReader

LETTER = (612, 792)

def check_pdf(filename):
    pdf = PdfReader(str(filename))
    issues = []
    if not pdf.pages:
        issues.append("PDF contains no pages")
    for num, page in enumerate(pdf.pages, 1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        if abs(width - LETTER[0]) > .1 or abs(height - LETTER[1]) > .1:
            issues.append(f"Page {num}: expected US Letter, found {width} x {height} pt")
        resources = page.get("/Resources")
        font_refs = resources.get_object().get("/Font", {}) if resources else {}
        for font in font_refs.get_object().values():
            obj = font.get_object()
            descriptor = obj.get("/FontDescriptor")
            if not descriptor:
                issues.append(f"Page {num}: font {obj.get('/BaseFont')} lacks font descriptor")
                continue
            desc = descriptor.get_object()
            if not any(key in desc for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                issues.append(f"Page {num}: font {obj.get('/BaseFont')} is not embedded")
    return {"pages": len(pdf.pages), "issues": issues, "ok": not issues}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pdf")
    args = p.parse_args()
    result = check_pdf(Path(args.pdf))
    print(f"Pages: {result['pages']} | {'PASS' if result['ok'] else 'FAIL'}")
    for issue in result["issues"]:
        print("-", issue)
    raise SystemExit(0 if result["ok"] else 1)
