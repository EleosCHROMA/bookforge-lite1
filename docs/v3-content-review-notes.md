# BookForge v3 — Second-pass content review notes (draft)

This is a **model-assisted editorial pass**, not a human-reviewed curriculum sign-off. Do not use these notes to populate `individual_exercise_reviews` or `release_approvals`.

## Checks performed

- Recomputed the 15 previously unchecked original answer types (ratios/rates, algebra, coordinates, signed numbers and medians); **15/15 match the stored answer keys** with integer medians normalized to whole-number notation.
- Existing 93 decimal, 12 exact fraction and 12 contextual checks are handled by separate verification modules. Their presence is not independent proof of educational quality.
- Reviewed the 12 contextual prompt/solution pairs for interpretation and clarity.

## Editorial findings

1. **Geometry problem units fixed**: Contextual triangle-area error analysis previously gave base = 10 and height = 6 without stating units, but the answer was in square inches. The prompt now specifies a 10-inch base and a 6-inch height.
2. **Currency-language polishing fixed**: The original awkward phrase has been replaced with “An $80 inspection is discounted by 25%”; the calculated $60 answer is unchanged.
3. **Inequality typesetting remains basic**: Some text uses `<=` rather than `≤`. In the final renderer prefer a correctly embedded Unicode symbol or typeset math if the font supports it.
4. **Worked explanations need human review**: Current step strings are author fixtures; automated exact matching only detects changed text, not incomplete reasoning or misleading pedagogy.
5. **Coverage is not certified**: Only 6 chapters and some Grade 6 topic areas are represented. Per-question Common Core tags remain candidate metadata until independently reviewed; do not advertise comprehensive standards alignment.

## Release discipline

- Keep both Clean Premium and Playful Illustrated themes.
- Ensure answers are in a back-of-book section.
- Make the cover spine width depend on the **final** interior page count. A 60-page demo cover must be recalculated if future edits change the total.
- Before KDP upload, have a real editor inspect the 132 questions, repair tickets, visuals, page layout, and official Print Previewer findings.
