# BookForge development handoff

Updated: October 25, 2026 (America/Los_Angeles).

## Current state

**V3 engineering milestone: COMPLETE. Publication: NOT APPROVED.**

Continue from `development/complete-chapter-lessons`. The v3 engineering release
commit is the commit containing this record; resolve its exact SHA with
`git log -1 -- docs/DEVELOPMENT_PROGRESS.md`. Its verified remote parent is
`43ebb4d0d80dd9e980f328da68da4d72d4c682cc` on
`development/verify-guided-solutions`. Do not restart from the older `version-3`
branch, which lacks the completed fixes. Main remains untouched.

User authorized development branches, verified commits and pushes to
EleosCHROMA/bookforge-lite1, a $0 budget, and v4 work in the next daily session.
Do not merge main, spend money, or publish to KDP without explicit approval.

## V3 engineering acceptance evidence

- One command: `python -m bookforge_v3.candidate --output NEW_DIRECTORY`.
- Both Clean Premium and Playful Illustrated: 64 pages; answers start at page 45.
- Six chapter-local worked lessons, 132 practice questions, 12 repair tickets,
  and 12 guided questions with matching back-of-book solutions.
- 116 v3 tests pass; 21 v2 tests pass. V2 tests run from `bookforge_v2`.
- Both assembled interiors pass font/trim preflight and manuscript audits.
  Each audit checks all 12 guided solutions against source text.
- Each matching cover is generated from the actual interior page count and
  passes paired preflight. Handoffs hash manuscript, lessons, cover config,
  interior, and cover; file paths are relative to the candidate root.
- Visually inspected both complete interiors using rendered contact sheets,
  inspected new lesson/answer pages at larger scale, corrected wrapped example
  heading spacing, and inspected both final covers. The final 128 interior page
  renders match the reviewed corrected build. This was model-assisted visual
  inspection, not independent human editorial approval.
- Candidate creation preserves existing directories and does not write a success
  summary when its manuscript audit fails.
- Added a manually triggered candidate workflow. It was NOT dispatched remotely;
  the results above are local verification, not a claim of a passing Actions run.
- Exact candidate artifacts were packaged separately for review. Regenerate
  through the command above if those bytes are unavailable.

## What engineering completion does not certify

No human attestations or individual exercise reviews were invented. All 132
practice questions still require documented independent editorial review. New
lesson explanations and solutions need substantive review as well. KDP Previewer,
metadata/rights/barcode verification and print proof remain open. The cover is a
draft and the interiors retain draft notices. The content is not certified as a
comprehensive Grade 6 standards workbook. No KDP upload was performed.

## Next daily session: v4

1. Fetch the branch above, check for other contributors' changes, inspect repo
   instructions, and rerun the candidate/test baseline as needed.
2. Create a v4 development branch from the latest verified v3 commit.
3. Prioritize actual teaching representations: put fraction models, coordinate
   diagrams, geometry nets, and statistical plots beside the relevant lessons.
   Existing standalone visual modules can be reused after review; do not merely
   add more repetitive computation or silently claim full CCSS coverage.
4. Strengthen print geometry checks and exercise/lesson review tracking. Keep
   automated numerical checks separate from editorial attestations.
5. Preserve answers at the back, both themes, native page numbers, matching covers,
   no publication, and the $0 budget. Update this record after every meaningful
   verified milestone so live and scheduled sessions can resume consistently.
