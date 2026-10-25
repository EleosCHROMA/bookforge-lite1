# BookForge v2 Release Gates

Status: **local release candidate, GitHub source integration incomplete**.

## Verified locally (October 24, 2026 Pacific)
- Both Clean Premium and Playful Illustrated workbook styles.
- Chapter opener, paginated worksheets, repair tickets and answer keys at the back.
- Multi-chapter assembly, 36-problem stress test in both themes.
- Fixed answer numbering on subsequent answer pages.
- US Letter preflight with embedded-font verification.
- 21 local Python unit tests passing.
- Generated and visually inspected a 12-page stress-test PDF.

## Must finish before v3
1. Commit **all** tested source modules and tests to `version-2`.
2. Perform fresh checkout, install dependencies and rerun tests.
3. Recreate representative PDFs from only tracked repository files.
4. Inspect pages for clipping, spacing and formula display.
5. Validate publication-specific specifications separately for each KDP product.

## Publishing caveats
- These tests are engineering checks, not a factual math-editorial audit.
- KDP uploading and publishing are **not automated**.
- Do not merge into `main` until the complete implementation passes from a fresh checkout.
