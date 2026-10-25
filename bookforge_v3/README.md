# BookForge v3 — complete six-chapter workbook assembly

The v3 pipeline builds on the existing v2 renderer. It supports two themes, sequential chapters, repair tickets, answer keys at the end and PDF preflight.

Run from repository root:

```powershell
py -m pip install -r bookforge_v2/requirements.txt
py bookforge_v3/pipeline.py bookforge_v3/data/mistake_mechanics_six_chapters.json --theme clean-premium --output clean.pdf
py bookforge_v3/pipeline.py bookforge_v3/data/mistake_mechanics_six_chapters.json --theme playful-illustrated --output playful.pdf
py -m unittest discover -s bookforge_v3/tests -v
```

Install DejaVu Sans regular and bold according to the v2 README. Dataset exercises are curated examples adapted from the original workbook, **not a complete transcription** and **not independently curriculum-audited**. Publishing is not automated.

## Content QA and release gate

Audit without generating a PDF:

```powershell
py bookforge_v3/pipeline.py bookforge_v3/data/mistake_mechanics_six_chapters.json --audit-only
```

To require editorial sign-offs before producing a release candidate:

```powershell
py bookforge_v3/pipeline.py bookforge_v3/data/mistake_mechanics_six_chapters.json --require-editorial-signoff --output reviewed.pdf
```

The demonstration has 36 exercises; only 21 have independent arithmetic checks. Remaining questions need other forms of review. Sign-off fields (`mathematics`, `pedagogy`, `proofreading`, `print_preview`) are for real human/editor confirmation, not for automated approval. Passing PDF preflight alone is insufficient for KDP publication.

## October 2026 layout hardening

The v3 branch now uses measured answer-key rows rather than fixed 9-question chunks. Long explanations paginate earlier, preserve the original problem numbers, and reserve space for repair-ticket solutions. Answers that cannot fit on one page produce explicit errors instead of silent text clipping.

Run the regression suites:
```powershell
cd bookforge_v2
py -m unittest discover -s tests -v
cd ..
py -m unittest discover -s bookforge_v3/tests -v
```

Verified locally: 21 v2 tests + 18 v3 tests; original six-chapter sample renders as 24 pages in each theme. Synthetic long-answer stress inputs render as 30 pages in each theme. The stress inputs are **not publishable educational content**.


## 108-exercise draft generator

From repository root:

```powershell
py -m bookforge_v3.expand_workbook bookforge_v3/data/mistake_mechanics_six_chapters.json --output expanded108.json
py bookforge_v3/pipeline.py expanded108.json --theme playful-illustrated --output expanded-playful.pdf
py bookforge_v3/pipeline.py expanded108.json --theme clean-premium --output expanded-clean.pdf
py bookforge_v3/kdp_preflight.py expanded-playful.pdf
```

The expanded draft has **108 exercises / 6 chapters** (72 new generated draft exercises), yielding **42 US Letter no-bleed pages** in either theme. The quality report has **93 arithmetic check records**, not 93 independently reviewed educational solutions. Source examples and generated drafts have not been curriculum-audited. Page numbers continue across worksheet pages; single repair tickets get more workspace.

Current KDP preflight checks PDF trim-size dimensions, minimum/maximum paperback page counts, and font embedding; it reports required gutter and outside margins based on page count. It does **not** inspect actual glyph geometry, illustration DPI, text safe areas or cover dimensions. KDP Previewer and substantive editorial review remain mandatory before publication. See https://kdp.amazon.com/en_US/help/topic/G201857950 .

Local verification: 21 v2 tests + 24 v3 tests passed. A GitHub Actions workflow also runs these tests and generates sample PDFs; confirm its run status in Actions rather than assuming it passed.
