"""Insert optional visual-learning pages directly before the answer-key section."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from pypdf import PdfReader,PdfWriter
from .visual_lessons import generate

def insert_visual_lessons(interior, output, font_dir=None):
    book=PdfReader(str(interior))
    boundaries=[i for i,page in enumerate(book.pages)
                if 'MASTER MECHANIC GUIDE' in (page.extract_text() or '')]
    if not boundaries:
        raise ValueError('No answer-key boundary in interior PDF')
    first=boundaries[0]
    with TemporaryDirectory() as temp:
        visuals=PdfReader(str(generate(Path(temp)/'visuals.pdf',font_dir)))
        writer=PdfWriter()
        for page in book.pages[:first]:writer.add_page(page)
        for page in visuals.pages:writer.add_page(page)
        for page in book.pages[first:]:writer.add_page(page)
        dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('wb') as f:writer.write(f)
        return {'output':str(dest),'pages':len(writer.pages),
                'visual_pages':len(visuals.pages),
                'answer_key_starts_at':first+len(visuals.pages)+1}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('interior')
    p.add_argument('--output',required=True)
    p.add_argument('--font-dir')
    a=p.parse_args()
    print(json.dumps(insert_visual_lessons(a.interior,a.output,a.font_dir),indent=2))
