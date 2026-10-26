# BookForge v3 engineering candidate

Build the complete candidate from the repository root:

```powershell
py -m pip install -r bookforge_v3/requirements.txt
py -m bookforge_v3.candidate --output v3-candidate
```

Use a new output directory for every build; existing directories are preserved.
DejaVu Sans regular and bold must be installed (see the v2 setup instructions).
The command builds both themes with six chapter-local worked lessons, 132 practice
questions, 12 repair tickets, and 12 guided solutions. Each interior is 64 pages,
with answers beginning on page 45. Matching covers use the actual final page count.

The output includes manuscript and lesson source JSON, both interiors and covers,
per-theme structural audits, exact-file hashes, an editorial review queue, release
blockers, and a final `candidate-summary.json`. Hash paths inside handoff reports
are relative to the candidate root (one directory above each handoff report).
A failed build has no final summary and must not be treated as a verified candidate.

Engineering completion means the reproducible candidate builds, automated checks
pass, and rendered output has been inspected. It does **not** mean publication
approval: human editorial review, KDP Previewer, final metadata/rights, barcode
placement, and print proof remain open. The tool never uploads or publishes.
The manually triggered `v3-candidate.yml` workflow can reproduce the checks; its
remote run status must be verified separately. No workflow run is implied by a
local pass. See `docs/DEVELOPMENT_PROGRESS.md` for the current handoff and v4 queue.

The sections below document earlier milestones and smaller demonstration builds.
Their page counts and commands apply to those inputs, not the complete candidate.

---

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

## Chapter-local lessons and page numbering (latest)

Guided lesson JSON now includes a required `chapter_number` in each lesson. During assembly, `build_guided.py` inserts each lesson immediately after its matching chapter opener. The insertion routine verifies the calculated chapter body-page count against the first answer-key page and aborts rather than silently misplacing content.

After insertion, it overlays sequential visible physical page numbers. The older numbers underneath the opaque overlay may still be returned by raw PDF text extraction; this is a **visual renumbering workaround**, not a structural replacement of the old content. Future versions should number pages during initial rendering rather than stamping them afterward.

Three sample lessons are assigned to chapters 1, 3, and 6. The demonstration book contains 27 pages, and answers begin on physical page 22. Run:

```powershell
py -m bookforge_v3.build_guided bookforge_v3/data/mistake_mechanics_six_chapters.json --lessons bookforge_v3/data/guided_lessons.json --theme playful-illustrated --output chapter-guided-playful.pdf
```

Preflight checks file dimensions and embedded fonts. A separate KDP Previewer inspection and independent educational review are still required.


## Native page numbering and complete guided-book assembly

Use this **new** production-oriented path instead of overlay-based `chapter_guided.py`:

```powershell
py -m bookforge_v3.build_132 bookforge_v3/data/mistake_mechanics_six_chapters.json --output draft132.json
py -m bookforge_v3.native_book draft132.json --lessons bookforge_v3/data/guided_lessons.json --theme playful-illustrated --output playful132.pdf
py -m bookforge_v3.native_book draft132.json --lessons bookforge_v3/data/guided_lessons.json --theme clean-premium --output clean132.pdf
py -m bookforge_v3.review_queue draft132.json --output editorial-review-queue.json
```

This assembler renders openers, worksheets, repair tickets, guided lessons and answer keys in final order with **native continuous page numbers**. It does not use an opaque post-render page-number overlay, so duplicate hidden number text is avoided. Lessons are placed directly after their corresponding chapter opener. The sample lessons cover Chapters 1, 3 and 6. The earlier `build_guided.py` now calls the same native assembler.

In local tests using a 132-exercise representative data set, both themes produced 60 pages with answer keys beginning on page 42. A full clean GitHub CI run for the exact repository-generated 132-question draft remains to be confirmed.

The editorial worklist identifies exercises not covered by the two automated arithmetic check types. It does **not** imply that checked questions have passed independent pedagogical review. Keep all KDP and editorial approvals manual until those checks have been completed.


## Independent contextual checks and release blocking (October 2026)

The `contextual_audit.py` module recomputes the numeric outcomes of the 12 instructor-authored garage problems from fixed scenario inputs. It also detects changed prompts, answer prefixes, or explanatory text. These checks protect the answer-key data; they do **not** independently establish that every explanation is pedagogically correct.

The content QA report now distinguishes:
- arithmetic checks from `math_audit.py`
- exact fraction checks from `fraction_audit.py`
- 12 contextual result/fixture integrity checks from `contextual_audit.py`
- individual questions still lacking automated mathematical coverage

**Strict release gate** (expected to reject current drafts):

```powershell
py -m bookforge_v3.release_gate draft132.json --pdf final-clean-132.pdf --output release-blockers.json
```

This command exits with a nonzero status until the draft has signed editorial attestations, individually documented exercise reviews, a supplied interior PDF, and passing structural PDF preflight. Optional `--full-curriculum` also demands evidence of individually reviewed standards tags before claiming comprehensive Grade 6 coverage. Nobody should programmatically fabricate reviewer names, approvals, or review dates to bypass it.

The current draft is **not publication ready**. KDP's own Previewer, print specification checks, and substantive editorial verification remain required before upload.


## Original 15 non-decimal answers: automated verification

`foundation_audit.py` independently computes the remaining 15 seed exercises (ratios, rates, expressions, coordinate geometry, integer comparisons and medians) and rejects changed prompts or answers. `quality.py` combines 93 decimal check records + 12 exact fraction checks + 12 contextual result checks + 15 foundation checks for **132 automated answer checks on a 132-exercise draft**. This is not an independent human educational review; worked explanations, diagrams, misleading problem phrasing, standards and all individual tasks still require editorial sign-off. `review_queue.py` now reports automated-answer gaps separately from missing individual human reviews.

```powershell
py -m unittest discover -s bookforge_v3/tests -v
py -m bookforge_v3.review_queue draft132.json --output review132.json
```

## Paperback cover prototypes

KDP geometry is calculated from final page count, trim size, bleed and paper stock. At 60 pages, 8.5 × 11-inch trim, Premium Color stock, the calculated wrap cover is **17.39082 × 11.25 inches** with a 0.14082-inch spine. No spine text is permitted for this short book.

```powershell
py -m bookforge_v3.cover_draft --pages 60 --theme playful-illustrated --output playful-cover-draft.pdf
py -m bookforge_v3.cover_draft --pages 60 --theme clean-premium --output clean-cover-draft.pdf
```

These are vector cover **drafts**, not KDP-approved covers. They have a reserved back-cover barcode region and embedded fonts. Confirm the page count, selected paper type, cover dimensions, all title/author metadata, actual text safe areas, illustration/print color requirements, and barcode position with KDP's official template generator and Print Previewer before uploading. Recalculate spine after every interior page-count change. Consult: https://kdp.amazon.com/en_US/help/topic/G201953020 .

Do not automatically claim completed human reviews or bypass the manual publication gate.


## Cover pipeline paired to actual interior

New production-oriented draft tool: `cover_pipeline.py` (requires Pillow) and
`paired_cover_preflight.py`. Unlike the earlier fixed 60-page `cover_draft.py`,
this tool reads the interior PDF to determine the page count and recalculates spine
width from the chosen stock. The optional `expected_pages` metadata guards
against accidentally using an older cover configuration.

From repository root:

```powershell
py -m pip install -r bookforge_v3/requirements.txt
py -m bookforge_v3.build_132 bookforge_v3/data/mistake_mechanics_six_chapters.json --output draft132.json
py -m bookforge_v3.native_book draft132.json --lessons bookforge_v3/data/guided_lessons.json --theme playful-illustrated --output interior.pdf
py -m bookforge_v3.cover_pipeline --interior interior.pdf --config bookforge_v3/data/cover_config.json --output cover.pdf --report cover_report.json
py -m bookforge_v3.paired_cover_preflight --interior interior.pdf --cover cover.pdf --report paired.json
```

Add `--artwork path/to/high_resolution_artwork.png` to use optional JPG/PNG
artwork. The generator rejects an image if the crop-to-fill size results in less
than 300 effective PPI. It also rejects unexpected page counts, unsupported
trim sizes, and incomplete cover configuration. The metadata example does not
invent an author name; if supplied, the `author` field is shown on the cover.

**Current limitations:** no-bleed 8.5 × 11-inch interior only, draft cover PDF
only, not color-managed CMYK output, no spine text, reserved blank barcode
region rather than an ISBN/barcode. The matching checker inspects dimensions
and embedded fonts but does not guarantee text/safe-zone compliance, rights,
metadata accuracy, flattening, or Print Previewer approval. The final cover
must be visually inspected using the official KDP cover calculator/template.
Never automatically publish on the strength of these automated checks alone.

KDP cover requirements: https://kdp.amazon.com/en_US/help/topic/G201953020


## Fingerprinted production handoff (latest)

Use `release_manifest.py` after building an interior and matching cover. The command computes SHA-256 hashes of the project JSON, interior PDF, cover PDF and optional cover configuration, records file sizes, and runs paired structural preflight.

```powershell
py -m bookforge_v3.release_manifest --project draft132.json --interior final-playful-132.pdf --cover matched-playful-cover.pdf --config bookforge_v3/data/cover_config.json --output production-handoff.json
```

A structural pass is not a publication approval. The manifest **always** records `ready_for_publication: false` because a local script cannot certify KDP Previewer approval, artwork rights, print proof, or truthful human editorial attestations. The strict `release_gate.py` command now also **requires a paired cover PDF** (`--cover`) and checks it against the interior page count/stock rather than checking the interior alone.

```powershell
py -m bookforge_v3.release_gate draft132.json --pdf final-playful-132.pdf --cover matched-playful-cover.pdf --output release-blockers.json
```

When any PDF or project bytes change, regenerate the manifest and redo the relevant reviews; an earlier SHA-256 fingerprint is not evidence that a later file was inspected. Test cases cover matching and stale covers, content fingerprints, and paper-stock mismatches. KDP submission remains intentionally manual.


## Misconception-focused repair tickets

`repair_upgrade.py` adds five draft mistake-analysis tickets to Chapters 2–6, complementing the six original chapter tickets plus the separately added fraction-division ticket in Chapter 1. The resulting 132-exercise manuscript has **12 repair tickets**, exactly two per chapter. The audit recomputes discount, reflection, volume and mean corrections and preserves canonical error statements. It does not certify instructional quality.

```powershell
py -m bookforge_v3.build_repair_draft bookforge_v3/data/mistake_mechanics_six_chapters.json --output repair132.json
py -m bookforge_v3.native_book repair132.json --lessons bookforge_v3/data/guided_lessons.json --theme playful-illustrated --output repair-playful.pdf
py -m bookforge_v3.native_book repair132.json --lessons bookforge_v3/data/guided_lessons.json --theme clean-premium --output repair-clean.pdf
```

The new five repair themes are percent discount confusion, the boundary in `at most` inequalities, reflection across the x-axis, multiplication versus addition in prism volume, and finding a mean. The structural renderer fits two repair tickets on one chapter page; locally tested both styles using the extended 132-question manuscript. The final *chapter-guided* production build still requires its GitHub Actions test to pass before treating it as verified. All explanations and standards tags await independent editorial review.

## Repair-ticket inventory verification

The fraction-enriched 132-exercise book contains **12 repair tickets, two in each of six chapters**: six original chapter tickets, one fraction-division ticket, and five new misconception-focused tickets. An earlier claim of 11 was incorrect; a mismatched test and CI assertion have been corrected.

Run:

```powershell
py -m bookforge_v3.build_repair_draft bookforge_v3/data/mistake_mechanics_six_chapters.json --output draft-repair.json
py -m bookforge_v3.ticket_inventory draft-repair.json --expected-per-chapter 2 --output ticket-inventory.json
```

The inventory catches duplicate IDs, missing or empty fields, and unexpectedly missing tickets. It is a **structural content check** and deliberately labels the tickets `UNREVIEWED`; it cannot certify misconception pedagogy or the quality of explanations. KDP publication remains blocked pending proper editorial review.


## Finished-PDF manuscript audit and repair-ticket privacy (latest)

**Important fix:** Earlier repair-ticket student pages printed the filled-in diagnosis, unintentionally giving away the intended misconception. The renderer now uses **YOUR DIAGNOSIS** with a neutral question in the student workbook. Correct solutions remain in the answer-key section at the back. Older generated samples still contain the outdated diagnosis text and must be regenerated.

Run this post-render audit (both styles) after generating a revised workbook:

```powershell
py -m bookforge_v3.manuscript_audit --pdf repair-playful.pdf --project draft-repair.json --lessons bookforge_v3/data/guided_lessons.json --output manuscript-playful-audit.json
py -m bookforge_v3.manuscript_audit --pdf repair-clean.pdf --project draft-repair.json --lessons bookforge_v3/data/guided_lessons.json --output manuscript-clean-audit.json
```

The audit checks chapter/answer-key order, contiguous numbered answers in each chapter, repair-ticket solution ID presence, expected guided-lesson locations, and unintended diagnosis disclosure. The older 60-page Playful Illustrated PDF produced before the fix failed the new audit with six diagnosis disclosures, one in each chapter. It otherwise passed the structural answer-key order and answer count checks.

This audit is based on PDF text extraction; it does **not** detect visual overlap, cropped vector art, accessibility issues, typos, print color problems, incorrect math reasoning, or incomplete CCSS coverage. Use image inspection and real editorial review in addition. CI now runs this audit against both re-generated 132-exercise repair-ticket workbooks.


## Complete guided-lesson answer keys

Native assembly now requires one nonempty `guided_answers` entry for every
`guided` question. All six bundled Your Turn tasks have back-of-book solutions,
appended after the chapter answer keys with native page numbers. Long solution
groups paginate together; oversized groups fail instead of clipping. Legacy
standalone lesson rendering still accepts lesson specifications without answers.

The repair-enriched 132-question build is now **61 pages** in both styles, with
answers beginning on page 42 and guided solutions on page 61. The paired cover
configuration expects 61 pages; regenerate any earlier 60-page cover. The sample
36-question native build is 28 pages.

This update also fits the two-line fraction chapter title inside the playful
banner and shortens the triangle error-analysis prompt while preserving its
measurements and units, allowing both expanded manuscripts to build. Layout
stress tests use synthetic exercise IDs so their intentionally expanded answers
are not mistaken for the canonical arithmetic fixtures.

Local validation: 107 v3 tests and 21 v2 tests; both 61-page repair manuscripts
pass structural manuscript/font/trim preflight. Rendered page contact sheets and
the changed pages were inspected in both styles. These checks do not constitute
human editorial approval or KDP Previewer approval. No publication is performed.


### Finished-PDF guided-solution integrity

When `manuscript_audit` receives `--lessons`, it now verifies the supplied
`guided_answers` in the extracted final PDF, rather than checking only that
the student lesson titles appear. Each solution section must appear once, each
numbered answer must match the source and remain in order, and source solution
text must not appear before the answer-key boundary. The report includes
`guided_solutions_checked` (six for the bundled lessons). Missing source answers
fail this check; older API callers that supply only title strings retain the
original title-presence check.

Local validation: 112 v3 tests pass, including deliberately missing, changed,
reordered, duplicated, and disclosed solution fixtures. Both regenerated
61-page repair workbooks pass the CLI audit with six guided answers checked.
This compares source text to rendered text; it does not establish mathematical
or pedagogical correctness.
