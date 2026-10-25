# BookForge v2 — dual-theme workbook generator

Creates PDF educational workbooks with two themes, multi-page practice, repair tickets and answers at the back. Uses embedded DejaVu Sans fonts and ReportLab.

## Windows setup

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py themes.py sample/chapter_full.json --theme playful-illustrated --output playful.pdf
py themes.py sample/chapter_full.json --theme clean-premium --output clean.pdf
```

Place free `DejaVuSans.ttf` and `DejaVuSans-Bold.ttf` inside `fonts/` or make them available in the system font directory. Font files are not included.

`sample/chapter_full.json` is the workbook schema example. For multiple chapters, use a JSON object containing `chapters: [<chapter objects>]` and optional `theme`. Each chapter supports six or more practice problems; tested up to twelve per chapter with short answers. Layout validation raises errors for overflow rather than silently clipping. KDP publication requires separate review and preflight.

## V2 release candidate: October 24, 2026

Two selectable themes, practice pagination (6 questions per worksheet page), and answer-key pagination (9 short answers per answer page) are working locally. All answers appear after chapter bodies. Numbering continues correctly across answer pages.

Run `py preflight.py your-output.pdf` after generating a PDF. This currently checks US Letter page size and embedded font resources; it does **not** certify content accuracy, clipping-free pages, margin compliance, or KDP acceptance. Long narrative answers can still trigger a controlled overflow error and need additional pagination logic.

The standalone code ZIP is newer than the partially synced GitHub branch. Do not merge `main` until the complete source is committed and tests pass on a fresh checkout.
