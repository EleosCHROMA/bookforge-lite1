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

## Grade 6 standards and question mix audit

Run after generating the 108-question JSON draft:

```powershell
py -m bookforge_v3.curriculum_report expanded108.json --output curriculum-review.json
```

The audit tracks 29 Grade 6 CCSS standard codes, detects duplicate question text, and identifies missing exercise-type labels. **Chapter candidate standards are not proof of coverage.** Only an individually reviewed question carrying `verified_standards` and `standard_reviewed: true` contributes to verified alignment. Reference: https://www.thecorestandards.org/Math/Content/6/ .

The current 108-question draft is arithmetic-heavy. Before publication, add varied error-analysis tasks, visual representations, explanations, fraction division, equations and inequalities, coordinate geometry, and statistical displays where needed. Avoid presenting the book as comprehensive Grade 6 standards coverage until independently audited.


## New draft: fraction division (6.NS.1)

The optional enrichment adds 12 exact fraction-division computations and one repair ticket to the first chapter. It updates that chapter title to *Number Operations: Decimals & Fractions* and retains the other five chapters.

```powershell
py -m bookforge_v3.build_120 bookforge_v3/data/mistake_mechanics_six_chapters.json --output draft120.json
py bookforge_v3/pipeline.py draft120.json --theme playful-illustrated --output draft120-playful.pdf
py bookforge_v3/pipeline.py draft120.json --theme clean-premium --output draft120-clean.pdf
py -m unittest discover -s bookforge_v3/tests -v
```

The enriched draft has 120 exercises. Of these, 93 have decimal arithmetic records and another 12 have separate exact-fraction verification, leaving 15 with no independent numeric check. This does **not** certify standards alignment or lesson quality. Question metadata only identifies 6.NS.1 as a *candidate*; human review remains required. The bank is calculation-heavy and still needs fraction models and contextual word problems.

## Visual mini-lessons (fraction bars, inequalities and statistics)

Generate 3 print-sharp pages with DejaVu Sans embedded:

```powershell
py -m bookforge_v3.visual_lessons --output visual-lessons.pdf
```

Insert them into any existing BookForge workbook immediately **before the Master Mechanic Guide**:

```powershell
py -m bookforge_v3.visual_book draft120-playful.pdf --output draft120-with-visuals.pdf
```

The output has three additional pages: a fraction bar showing `3/4 ÷ 1/2 = 1 1/2`, a number line for `x > -2`, and a dot plot of inspection times `2,3,3,4,4,4,5`. Each includes a student task. These are vector-drawn, not AI-generated math labels.

The insertion tool refuses to run if it cannot locate the answer-key section, preventing silent placement of lessons behind the answers. **This is draft teaching material** and still requires editorial review. It currently supplements, rather than replacing, the predominantly computation-based question bank.

## Contextual enrichment: 132-exercise draft

The optional enrichment adds 12 instructor-authored **draft** questions (two per chapter) with explanation-style answer entries. Topics include decimal/fraction interpretation, ratios and discounts, equations and inequalities, coordinate moves, geometry in realistic shop settings, and statistical interpretation.

```powershell
py -m bookforge_v3.build_132 bookforge_v3/data/mistake_mechanics_six_chapters.json --output draft132.json
py bookforge_v3/pipeline.py draft132.json --theme playful-illustrated --output draft132-playful.pdf
py bookforge_v3/pipeline.py draft132.json --theme clean-premium --output draft132-clean.pdf
py -m unittest discover -s bookforge_v3/tests -v
```

**Important:** The contextual prompts and explanations are human-authored draft content, not independently verified answers. All 132 tasks require review for learning progression, clarity, standards alignment, and suitability for print. The earlier 93 decimal arithmetic checks and 12 exact fraction-bank checks remain separate. Do not automatically mark `standard_reviewed` or editorial approvals true.


## Configurable guided lessons

Use `bookforge_v3/data/guided_lessons.json` as a template. Each lesson has:
- `title`, `concept`
- `examples`: one or two worked examples with a `problem` and 1–3 `steps`
- `guided`: one or two prompts with writing space

Example commands (run from repository root):

```powershell
py -m bookforge_v3.build_guided bookforge_v3/data/mistake_mechanics_six_chapters.json --lessons bookforge_v3/data/guided_lessons.json --theme playful-illustrated --output guided-playful.pdf
py -m bookforge_v3.build_guided bookforge_v3/data/mistake_mechanics_six_chapters.json --lessons bookforge_v3/data/guided_lessons.json --theme clean-premium --output guided-clean.pdf
```

The three supplemental pages are inserted **before the first answer-key page**, not alongside the answer keys. This initial milestone is a reusable lesson supplement, not yet automatic placement immediately after each chapter opener. The renderer refuses oversized lesson text and uses embedded DejaVu Sans for print-safe, editable text. Generated sample lessons remain draft instructional material, not approved curriculum.
