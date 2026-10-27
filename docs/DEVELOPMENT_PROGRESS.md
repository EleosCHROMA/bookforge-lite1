# BookForge development handoff

Updated: late-night October 25-26, 2026 (America/Los_Angeles).

## Current state

**V4 development: IN PROGRESS. V3 engineering milestone: COMPLETE.
Publication: NOT APPROVED.**

Current working branch: `development/v4-pricing-handoff`. Resume this branch,
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


### Third v4 checkpoint: model-based guided activities

Verified parent: `93f6de4853ea184be2b758f5605e12be52821678` on
`development/v4-review-tracking`. The commit containing this section updates
six guided tasks to use the model representations, revises the strict/inclusive
boundary comparison, and updates their back-of-book explanations. Each lesson's
first writing box is now 72 points high; the second stays 48 points. Diagram
placement is measured against the remaining example-card space. Both interiors
remain 64 pages and pass the manuscript, exact-solution, font/trim, paired-cover,
and actual-glyph margin checks. All six changed lessons plus the guided answer
page were visually inspected in each theme. Local tests: 23 v4 + 116 v3 + 21 v2
(all passing). No real reviews were supplied; 174 content items remain PENDING.
The new v4 Actions workflow is manual only and has not been run remotely.

The daily automation must resume this branch (or a newer verified descendant).
Two additional finite overnight runs were configured for 12:15 and 1:15 a.m.
Pacific on October 26, with instructions to save progress and stop by 2 a.m.
They are scheduled sessions, not a claim of continuous execution. Fetch latest
remote heads before edits; avoid overwriting live or other scheduled work.

Next meaningful work: improve diagram usability and extend geometry preflight to
vector bounds where reliable; audit and improve shallow statistics instruction
and real visual tasks. Keep source-bound review evidence, both themes, answer
privacy, no spending, no changes to main and no KDP publication. V4 remains
IN_PROGRESS and the workbook is not independently editorially approved.

### Fourth v4 checkpoint: artwork preflight and footer repair

Parent: `2ef89e1cd01fdfdafce0469fd9163ceac524ee4d` on
`development/v4-model-practice`. The commit containing this section extends print
preflight to conservative vector bounds including half-stroke width, filled
shapes, placed image bounds, and minimum 300 effective PPI. The actual scan found
the page-number badge circles entered the bottom margin by one point. Their
radius was reduced from 11 to 10 points, preserving number alignment while
bringing their fill to the 18-point boundary. The new report is named
`print-geometry.json` and covers text plus artwork.

Verified: 28 v4 + 116 v3 + 21 v2 tests pass (165 total). Both 64-page candidates
pass all checks; 823 clean-theme and 2,307 playful-theme vector objects were
checked, with zero raster images. Render comparison confirms all content above
the footer is unchanged on all 128 pages. Both repaired footer styles were
visually inspected. No reviews were invented; 174 items remain pending.

Next run: resume this branch or a newer verified descendant. Priority candidates
are improving substantive statistics lessons, checking diagram/text collisions,
or making reviewer packets easier to inspect. Do not weaken the new checks to
make drafts pass. Conservative artwork bounds do not interpret clipping or
transparency; rotated/sheared image PPI and physical proofs need manual review.
V4 remains IN_PROGRESS. Main and the v3 baseline are preserved.

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

## Overnight review-date validation checkpoint

Parent: 30e04a08ce96d2a2dead094b0493bbef7e797b08. Branch:
`development/v4-review-dates`. Review attestations with future timestamps now
remain INVALID rather than being accepted as completed reviews. Regression
coverage includes year-2999 timestamps alongside malformed and timezone-free
dates. All 28 v4 tests pass. PDF rendering/content is unchanged, so no new PDF
inspection is claimed. No approvals generated. Next: substantive statistics
instruction or reviewer usability; v4 remains in progress.

## Reviewer browser checkpoint

Parent: f97c652dc5e34c54db5aaa7b1122a42fea1b4e09. Branch:
`development/v4-review-browser`. Candidate builds now include an offline searchable
editorial-review.html with prompts, solutions, fingerprints and current statuses.
All source strings are HTML-escaped; no approval actions or external network
requests are included. The reviewer page is hashed in each handoff.
29 v4 tests pass including full candidate integration and hostile-markup escaping.
Student PDF generation is unchanged; no new PDF visual inspection is claimed.
Next: substantive statistics instruction. V4 remains in progress.

## Statistical spread checkpoint

Parent: 2108b18a96da060f3569dec7004d66e78dda023e. Added explicit MAD
instruction and a guided distance-from-mean task with a complete back-of-book
solution. The diagram model independently computes MAD = 22/5 for the repair
data, while the lesson explains 4.4 minutes. Both 64-page candidates pass all
structural, glyph/artwork, and guided-solution checks; 29 v4 tests pass. Both
revised lesson pages were rendered and visually inspected. All 174 reviews
remain pending. Full completion is blocked on real editorial/print review;
no human approvals may be fabricated. V4 remains a development candidate.

## Candidate package integrity verification

Parent: a7e2e1154968396219ad85988203e82792b174d0. Branch:
`development/v4-package-verification`. Run `python -m
bookforge_v4.verify_package CANDIDATE_DIRECTORY` to recheck both handoffs against
current PDF, lesson and reviewer-file bytes. Missing inventory, modified or
missing files and paths escaping the package fail verification. Handoffs remain
unsigned, so this is integrity checking, not provenance or editorial approval.
32 v4 tests pass; the actual V4_Spread_Checked package passes with 18 fingerprint
records checked. PDF generation is unchanged; no new visual review claimed.
Next: real editorial/print review and remaining usability improvements.

## Combined engineering readiness checkpoint

Parent: a2ddf67b872132556ab01dfcfb70c2645191070c. Branch:
`development/v4-readiness-audit`. A single saved-package audit now reruns byte
integrity, mathematical content checks, manuscript/solution checks, glyph and
artwork bounds, image PPI and paired-cover checks. The actual saved 64-page
candidate reports engineering_ready=true and ready_for_publication=false.
34 v4 tests pass, including a complete candidate and changed-source rejection.
The final readiness module also passed its two integration tests after adding
content QA. No PDF rendering changes were made.

Near-complete engineering candidate, not a completed published workbook: all
174 editorial items remain pending; standards tags are unreviewed and 108
exercise-kind labels are absent. Previewer/print-proof review and explicit
publication approval remain required. Preserve these open findings in future
work; do not turn computational passes into editorial attestations.

## Autonomous content review checkpoint

Parent: 8e5d30c468c07f08e3fe2edb2e2848aa7dbf0c90. All 132 exercises
now have valid exercise-kind labels and candidate standard codes in the v4
build. Existing audited contextual tags are preserved; proposed tags are never
marked reviewed. Zero standards are claimed verified. Model-assisted numeric
and clarity inspection of all 132 prompt/answer pairs is recorded with exact
content hashes in bookforge_v4/data/model_review_notes.json. Scope limitations
are explicit, particularly isolated surface-area calculations without nets and
integer-edge volume questions. This is not independent human approval.

35 v4 and 116 v3 tests pass; both 64-page candidates pass all checks. All
128 rendered pages are pixel-identical to the previously inspected statistics
build. No new visual changes are claimed. The scheduled task was updated with
the user standing instruction: checkpoints are not stopping points; proceed
until scope complete, a genuine user-action blocker, or execution limits.

RESUME NEXT: inspect the remaining 42 non-practice items listed in
model_review_notes.json (repairs, concepts, examples, guided tasks, diagrams).
Then integrate fixed model review findings into the reviewer package, treating
source-hash mismatches as stale. Improve per-item standards rationale and
partial-coverage notes. Do not regenerate model review pass labels for changed
unread source. No human approvals are recorded; publication stays blocked.

## All-source model-assisted editorial inspection complete

Parent: 0f76327a588440e15c2d1cca778506bfb186a6e2. All 174 current
review-item sources have now been inspected by the model. Fixed per-item notes
are bound to source hashes; changed items become STALE_MODEL_REVIEW and never
receive an automatic renewed pass. The candidate includes model-editorial-
review.json and hashes it in each handoff. Readiness distinguishes current
model findings from independently supplied human attestations.

36 v4 tests pass. Both rebuilt 64-page candidates pass all structural, arithmetic,
guided-solution and geometry checks. PDFs are unchanged from the visually
reviewed statistics build. All 132 exercise types are labeled and candidate
standard codes proposed; none are declared editor-verified. Remaining scope
limitations include isolated surface-area items without nets and restricted
statistical representations. Repair diagnosis1.1 is plausible, not uniquely
inferable; weight-domain context is implicit. Findings are not hidden.

Agreed model-review/metadata scope is complete for this source version. No human
approvals have been generated. Remaining external work: independent review of
findings, official KDP Previewer, print proof, metadata/rights/barcode checks,
and explicit publication approval. Continue other feasible improvements under
the standing instruction; do not ask for continue at routine checkpoints.

## V4 consolidated external-review handoff

Parent: c50eb995e3b34b3fb169b316f52bab5abd825e72. The reviewer HTML now
shows current/stale model findings beside each source and explicitly labels
human-review status separately. Candidate status is AWAITING_EXTERNAL_REVIEW.
The agreed engineering and model-assisted source-review scope is complete for
this snapshot: six visual lessons and guided activities, all132 exercise labels
and proposed standard mappings, all174 source-bound model findings, searchable
reviewer handoff, artifact integrity checks and full engineering preflight.
No comprehensive standards alignment or human approval is claimed.

Remaining publication blockers require external evidence: independent editorial
review and resolution of documented limitations, KDP Previewer inspection,
physical print-proof review, final metadata/rights/barcode checks and explicit
user publication approval. Do not manufacture a new cosmetic milestone to hide
these blockers. If reviewing new content or responding to supplied feedback,
resume here and rerun relevant checks. Student PDF content is unchanged by this
HTML/status update; no new visual PDF inspection is claimed.

## Consolidated editorial finding resolution

Parent: ef42ea51403ac1c2df7d5a35816b17eb3b00204f. Resolved the two
actionable model-review findings rather than deferring them: the weight model
now represents the physical domain 0<=w<=2000 with closed endpoints and a bounded
segment; the original subtraction repair diagnosis explicitly identifies only
a possible cause and requests shown work. All changed lesson/repair sources
were re-inspected and only affected source-bound findings refreshed.
Both revised inequality pages were rendered and visually inspected. Numeric
axis spacing is tested independently of repeated numbers in paragraph text.
All 174 model findings remain separate from human attestations.

Standing work rule: use consolidated editorial/build/verification blocks, not
cosmetic commits as stopping points. Report only completed scope, genuine
user-action blockers or execution limits. Current external blockers remain
KDP account/Previewer access and physical proof review plus independent human
attestation if claimed; do not fabricate access, reviews or publication.

## User KDP visual preview review

On October26 the user reported all pages reviewed and looking good. The attached
summary visibly confirms 64 pages, 8.5x11, Premium Color/white paper, No Bleed and
Matte. Evidence and known review-package fingerprints are recorded separately
in docs/reviews/kdp-preview-2026-10-26.json. The screenshot does not prove exact
uploaded byte identity. This is a real user visual-review statement, not an
invented mathematical/editorial signoff. Physical proof and publication approval
remain ungranted. Draft notices and final metadata still need attention before
a publication file set; repeat preview after any such file changes.

## User proof preference and final-copy cleanup

The user chose to skip a physical print proof if the online preview looks good.
No physical proof was performed or approved. The previous online visual review
remains valid only for the files the user reviewed, whose uploaded hashes were not
verified. The v4 candidate removes draft notices from student lesson and guided
answer footers and the cover blurb; v3 retains its draft wording by default.
This is a new file set and requires a fresh online preview before publication.
Editorial attestations and publication approval remain separate and are not
implied by the removal of draft text. Preserve the $0 budget and do not publish.
Parent e3c31d98094f207ba25f852333fe40ae7ffd079b. Both 64-page styles and covers
were rebuilt; lesson, answer-guide and cover pages were visually inspected in
both styles. All 38 v4 and 116 v3 tests passed, including text checks against
draft wording. Automated geometry and manuscript checks passed. Candidate
readiness no longer incorrectly requires a physical proof against user wishes.

## Revised-file user feedback

Parent: 71ddbfb8d0d19cb2d4c457819087c2d5e78e84b0. After receiving the
revised v4 review package and a request to inspect it online, the user said
"Looks good, now continue automatically and tell me when complete". See
docs/reviews/final-files-user-review-2026-10-26.json for package hashes and
limits: the review tool and uploaded bytes were not confirmed. Do not treat the
statement as publication authorization or human editorial approval. The user
requested the daily schedule paused; do not claim runs continue in the background.
Remaining: final metadata and rights verification, actual KDP Previewer result
for these files if not established, and explicit publication approval. Physical
proof is declined unless the user changes their preference.

## Final online review confirmation

Parent: 662cc375c149534080ad71d16e35bb8cfd3eb226. Following the request
to confirm the revised package's online check, the user said "It passes
everything". This is recorded as the user's report of a successful final online
preview for the supplied playful package; uploaded bytes were not independently
authenticated. No independent editorial, physical proof or publication approval
is implied. Readiness can optionally accept that evidence and checks the local
interior and cover hashes against it; a changed package or absent evidence does
not inherit the pass. The report continues to require explicit publication
approval and identifies missing independent editorial attestations honestly.
All 38 v4 tests passed, including matching and stale preview evidence. Rechecking
the exact saved candidate reports engineering ready and user-reported preview
pass, while keeping publication false. `docs/v4-publishing-handoff.md` supplies
a restrained listing description and the unresolved ownership, ISBN, listing,
price and approval details. No PDF bytes were changed by this checkpoint.

## Review evidence integrity

Parent: d45b5359239641656ce2f1cf6579c511bfe21408. Package verification now
requires the diagram-model and model-review inventory entries. Readiness also
compares saved editorial and model-review reports to the current source-derived
reports, including when handoff hashes have been rewritten. This catches stale
or inconsistent review evidence; unsigned handoffs still cannot establish who
reviewed content. The publishing handoff clarifies that standards labels are
rule-generated proposals, not per-item standards verification. PDF content and
the user's reported online preview remain unchanged.
Validation: all 39 v4 tests passed; the final six focused readiness and package
tests passed, including missing inventory and inconsistent saved-review data.
The previously saved candidate still passed engineering checks with the user's
reported preview evidence. No PDF was modified or rebuilt in this checkpoint.

## Pricing handoff

Parent: af4d3841b3d74867cce0d66b5e67589cbd6b196c. The publishing handoff
now gives transparent Amazon.com royalty estimates at three price points,
using the $6.12 printing cost shown in the earlier user-provided KDP screenshot
and official paperback royalty rules checked October 26, 2026. It identifies
the assumptions and calls for verifying the current listing cost. No price
was chosen and no KDP account or listing was changed.
