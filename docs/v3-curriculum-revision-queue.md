# Mistake Mechanics v3 — Curriculum revision queue

Reference: [Common Core Grade 6 overview](https://www.thecorestandards.org/Math/Content/6/introduction/) and individual standards in the same official series.

**Status:** 108-question engineering draft; not an independently audited Grade 6 book. The automated standards audit currently reports zero **editor-verified question-to-standard mappings**. This is a metadata status, **not** a claim that none of the lessons teach the standards.

## Highest-value missing or shallow areas

| Priority | Standards | Needed instructional work |
|---|---|---|
| P0 | 6.NS.1 | Dedicated dividing-fractions-by-fractions lesson, worked models, practice and misconception-based repair tickets |
| P0 | 6.NS.2, 6.NS.4 | Long division and factors/multiples/GCF/LCM with explanation tasks |
| P0 | 6.EE.5, 6.EE.8, 6.EE.9 | Solution meaning, inequalities and dependent/independent variables |
| P0 | 6.G.3, 6.G.4 | Coordinate-polygon geometry and drawn nets/surface-area representations |
| P0 | 6.SP.4, 6.SP.5 | Actual dot plots, histograms and box plots; contextual interpretation including spread |
| P1 | 6.RP.3 | Equivalent-ratio tables, conversion tasks, multi-step scenarios |
| P1 | 6.NS.5–8 | Rational-number placement and reasoning, not just absolute-value calculations |
| P1 | 6.SP.1–3 | Statistical questions, distributions and MAD with explanations |
| P1 | 6.G.2 | Rectangular-prism volume including fractional dimensions |
| P1 | 6.EE.2–4 | Writing expressions from descriptions, evaluating variables, explaining equivalence |

## Release criteria

- Review and tag **each individual exercise** with the relevant standard(s). Use `verified_standards` only after actual human review; `standard_reviewed: true` must not be set by a generator.
- Add explicit exercise kinds: `computation`, `word_problem`, `error_analysis`, `explanation`, `visual`, `modeling`.
- Include meaningful representation/visualization and explanation activities rather than simply increasing computational quantity.
- Math answers and repair-ticket rationales need independent checks. A correct numerical answer does not prove a lesson is instructionally sound.
- Keep answer keys at the back and preserve both Clean Premium and Playful Illustrated themes.
- Re-run v2/v3 tests, curriculum report, PDF preflight, and actual KDP Print Previewer before calling a book print-ready.

**Important:** The first uploaded 26-page workbook itself omitted dedicated fraction-division instruction. Preserve its design identity, but expand the actual learning scope where necessary.
