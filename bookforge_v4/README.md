# BookForge v4 - visual instruction (in progress)

Start from the verified v3 engineering candidate. This branch adds six computed,
vector-drawn teaching models inside the existing chapter-local lessons:

| Chapter | Worked model |
| --- | --- |
| 1 | Fraction bar: how many half-sized groups fit in three fourths |
| 2 | Double number line linking filters to cost |
| 3 | Inclusive inequality boundary and leftward solution arrow |
| 4 | Horizontal movement and reflection on a coordinate grid |
| 5 | Six-face rectangular-prism net, surface area, and volume |
| 6 | Dot plot of the repair times used in the worked example |

The diagrams contain editable, embedded-font text and vector shapes. Their
numeric labels come from validated inputs; they are not generated images.
The paired instructional explanations still require independent review.

Build both styles from the repository root:

```powershell
py -m pip install -r bookforge_v4/requirements.txt
py -m bookforge_v4.candidate --output v4-candidate
py -m unittest discover -s bookforge_v4/tests -q
```

Install DejaVu Sans regular/bold as required by v3. Use a new output directory.
The 64-page interiors retain answers at page 45, all 12 guided solutions at the
back, and covers matched to the actual page count. `diagram-models.json` records
computed model values. Per-theme `text-geometry.json` reports inspect extracted
PDF glyph bounds against the configured no-bleed margins, including alternating
inside margins. This does not check vector strokes, images, contrast, or physical
print results. Existing font/trim/manuscript/cover checks remain in use.

A v4 geometry failure removes the earlier v3 success summary. The final summary
identifies version 4 and explicitly keeps development status `IN_PROGRESS`.
No human approvals are generated and nothing is published.

## Current verified checkpoint

15 v4 tests, 116 v3 tests and 21 v2 tests pass locally. Tests cover exact model
results, common-denominator grouping, inequality inclusivity, invalid inputs,
embedded fonts, actual number-line tick spacing and six non-overlapping net
faces, alternating glyph margins, full candidate builds, and failure reporting.
Both styles' six changed lessons have been visually inspected at larger scale.
The v3 baseline's unchanged practice/answer pages remain intact.

## Remaining v4 work

- Add meaningful model-based student tasks, rather than worked diagrams alone.
- Bind review records to exact exercise, repair, lesson and diagram source hashes
  so changing content invalidates old review evidence.
- Expand geometry checking to vector/diagram bounds and text collisions where
  reliable; retain human visual review.
- Improve statistical representations and any shallow curriculum areas without
  claiming comprehensive Grade 6 alignment.
- Continue substantive editorial review and keep publication approval separate.

## Source-bound editorial review packet

The candidate now writes `editorial-review-items.json` with prompts, answers,
context and source hashes for **174 items**: 132 practice questions, 12 repair
tickets, 12 guided tasks, six lesson concepts, six worked examples and six
paired diagrams. This packet contains answers and belongs with reviewer
materials, not student pages.

`review-attestations.json` starts as `{}`. A real reviewer may supply records
keyed by item ID. Each record requires `reviewer`, timezone-aware `reviewed_at`,
`notes`, `content_sha256`, and `decision` (`approve` or `reject`). The fingerprint
must match the current source. Changing a diagram also invalidates its paired
worked-example review. Review results distinguish PENDING, INVALID, STALE,
REJECTED and APPROVED. Reviewer identity/expertise are not authenticated by this
local tool; matching metadata is not publication approval.

To reuse reviewer-supplied evidence during a fresh candidate build:

```powershell
py -m bookforge_v4.candidate --output NEW_DIRECTORY --reviews actual-reviews.json
```

To check existing evidence against regenerated current sources:

```powershell
py -m bookforge_v4.review_packet --project v4-candidate/manuscript.json --lessons v4-candidate/lessons.json --reviews actual-reviews.json --output review-status.json
```

The review command exits nonzero while anything is unapproved. The candidate
builder still produces a development review package with pending items; it never
changes `ready_for_publication` to true. The lesson, diagram and review source
files are included in each exact-file handoff's fingerprints.

Additional verification: six review-tracking tests cover missing evidence,
changed answers, changed diagram/example pairings, incomplete metadata,
timezone-free dates, rejected decisions, orphaned IDs, and packet tampering.
Total local checkpoint: 21 v4, 116 v3 and 21 v2 tests pass.

## Model-based guided practice checkpoint

Each chapter's first guided task now asks students to use the corresponding
representation: fraction grouping, a double number line, inequality boundaries,
coordinate movement, a prism net, or a dot plot. Matching explanations are kept
at the back. The first writing box is 72 points high, giving one inch for a
sketch or explanation; the second stays 48 points high. The measured layout
rejects oversized writing-box requests and protects diagram/text separation.
Both themes stay at 64 pages, with answers starting on page 45.

Current local validation: **23 v4 + 116 v3 + 21 v2 tests pass**. All changed lesson
pages and guided answer pages were visually inspected in both styles. Actual
writing-box dimensions and their bottom bounds are regression-tested. The
manually triggered `v4-candidate.yml` workflow was added but not dispatched.
V4 is still in progress; this is a saved development checkpoint.


## Artwork bounds and placed-image preflight

`print-geometry.json` now supersedes `text-geometry.json`. Alongside glyph
margins, it measures conservative vector bounds (including half the stroke
width), filled shapes, placed images, and effective image PPI (minimum 300).
Clipped/translucent paths and rotated/sheared images still need visual review.
It does not detect arbitrary text/art collisions or certify physical printing.

The first real artwork scan caught the footer badge circles extending one point
inside the bottom margin. Their radii are now 10 rather than 11 points, leaving
the text unchanged and meeting the configured boundary. Both full manuscripts
pass: 823 clean and 2,307 playful vector objects checked; no raster images.
Current local total: **28 v4 + 116 v3 + 21 v2 = 165 passing tests**.


Recheck a saved package with `python -m bookforge_v4.verify_package DIRECTORY`.
This detects missing/changed files and unsafe inventory paths against both
handoffs. The manifests are unsigned; matching hashes do not prove editorial
review or publication approval.


Run `python -m bookforge_v4.readiness DIRECTORY --output readiness.json` to
recheck integrity, content QA, manuscript answers, print geometry and paired
covers together. A zero exit means engineering checks passed, not publication
approval. The report separately lists outstanding editorial and print work.


The candidate includes `model-editorial-review.json`: fixed findings for all
174 inspected source items, separate from human review status. Source changes
make findings stale; they do not trigger automatic model reapproval. All 132
exercise kinds and proposed standard codes are present. Proposals are not
verified alignment and the book is not certified comprehensive Grade6 coverage.
