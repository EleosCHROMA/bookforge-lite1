# BookForge v2 — dual-theme workbook generator

This directory is the staging area for the JSON-driven workbook engine. The full tested Python prototype is available in the source bundle generated in ChatGPT; the complete implementation has **not yet been committed** to this branch.

## Implemented in the local prototype
- `clean-premium` and `playful-illustrated` themes.
- Chapter opener, practice pages, premium-colored repair tickets and answer-key pages.
- Six problems per worksheet page; supports multi-page practice.
- Multiple chapters, with answer sections collected after all chapter bodies.
- Automated validation and tests.

## Installation (after placing the source bundle here)
```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py themes.py sample/chapter_full.json --theme playful-illustrated --output playful.pdf
py themes.py sample/chapter_full.json --theme clean-premium --output clean.pdf
```

Requires free DejaVuSans.ttf and DejaVuSans-Bold.ttf in `fonts/` or in an available system fonts folder. Do not commit font files without appropriate licensing.

**Scope:** prototypes only; publishing, content accuracy verification and Amazon KDP preflight remain separate steps.
