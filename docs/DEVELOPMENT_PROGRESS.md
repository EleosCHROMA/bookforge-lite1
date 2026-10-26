# BookForge development handoff

Updated: October 25, 2026 (America/Los_Angeles).

## Current state

**V4 development: IN PROGRESS. V3 engineering milestone: COMPLETE.
Publication: NOT APPROVED.**

Current working branch: `development/v4-review-tracking`. Resume this branch,
not a fresh branch from v3. The latest verified v3 parent is
`2beb40d9cdf6f9aad13beb40d732f4aef2f5b4c4`.

The v4 visual-instruction checkpoint adds six computed vector diagrams, one in
each worked lesson, plus extracted-glyph margin preflight and a one-command v4
candidate builder. Both interiors remain 64 pages, answers start on page 45, and
all 12 guided solutions remain at the back. Local checks: 15 v4 + 116 v3 + 21 v2
tests. Changed lessons in both themes were visually inspected. Actual numeric
axis spacing, net face area/topology and alternating inside margins have
regression tests. See `bookforge_v4/README.md` for setup and remaining scope.

The user explicitly authorized starting v4 in the current live session and wants
to work toward 2 a.m. Pacific. Scheduled sessions must resume the latest verified
v4 checkpoint without overwriting live work. Next: add student model-based activities. V4 is not complete.

### Second v4 checkpoint: review tracking

Verified parent: `f3f3159ab0378374c98a4008ba66f7a775cab48a` on
`development/v4-lesson-diagrams`. The commit containing this paragraph completes
the source-bound review packet and candidate integration. It adds 174 review
items covering all practice/repair/guided content, concepts, worked examples and
diagrams. All 174 remain PENDING; zero approvals were generated. Changed sources
invalidate prior evidence; diagrams and paired examples are bound together.
The reviewer packet includes answer text and must stay outside student PDFs.
Tests: 21 v4 + 116 v3 + 21 v2 pass. PDF content is unchanged from the visually
inspected first v4 checkpoint; both candidate builds still pass all structural,
answer-key and glyph-geometry checks. Next: make the guided questions explicitly
use the visual models and improve diagram usability without adding repetitive
computation. Preserve v3 and main.

## Preserved v3 baseline

The preserved v3 baseline is `development/complete-chapter-lessons`. The v3 engineering release
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

## Original v4 starting plan (now underway)

1. Fetch the branch above, check for other contributors' changes, inspect repo
   instructions, and rerun the candidate/test baseline as needed.
2. Resume the current v4 development branch noted above; it already starts from the verified v3 commit.
3. Prioritize actual teaching representations: put fraction models, coordinate
   diagrams, geometry nets, and statistical plots beside the relevant lessons.
   Existing standalone visual modules can be reused after review; do not merely
   add more repetitive computation or silently claim full CCSS coverage.
4. Strengthen print geometry checks and exercise/lesson review tracking. Keep
   automated numerical checks separate from editorial attestations.
5. Preserve answers at the back, both themes, native page numbers, matching covers,
   no publication, and the $0 budget. Update this record after every meaningful
   verified milestone so live and scheduled sessions can resume consistently.
