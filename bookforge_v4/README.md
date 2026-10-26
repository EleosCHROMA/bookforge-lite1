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
