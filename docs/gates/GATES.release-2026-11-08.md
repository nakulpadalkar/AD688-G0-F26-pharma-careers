# Certificate release verification: November 8, 2026

- [x] G1: All branches and local updates reviewed; source work preserved.
  MANUAL: Fetch/prune, refs, status, stashes and content diff review.
- [x] G2: Eleven pages and existing data/frontend/browser checks pass; certificate layout and navigation verified.
  MANUAL: Reviewed Quarto/Python/Node/Edge checks, including four course rows and certificate anchors.
- [x] G3: Targeted commits separate source, generated site and evidence; temporary artifacts removed.
  MANUAL: Staged path/diff inspection, no private or temporary files.
- [ ] G4: Main synchronized and clean; publication and Pages deployment succeed.
  MANUAL: Remote HEAD, clean status/stashes and Actions results.

Evidence: PowerShell, repository root. Fetch all/prune succeeded; main initially current, gh-pages is publication output. No stashes, symlinks or running previews. Quarto rendered 11 pages. Eight Python suites, three JS syntax checks, two Node suites and four Edge browser suites passed. EVIDENCE_OK checked 466 links; snapshot/homepage count parity passed. Additional certificate browser check passed four course rows, curriculum/format anchors and 1440/390px containment; fresh screenshots visually inspected. QA screenshot trees removed after verification; no .tmp files. No local server or database refresh started.

AAR: Expected preserve the new certificate format and publish a complete verified build. All local checks passed and the proposed status, four-course count and semester pacing remained visible. No build failure or new mismatch occurred. Repeat the saved-evidence build and rendered certificate checks; existing lessons cover the pattern, with no new rule or skill changes needed.

G3 evidence: source/content and generated-site changes committed separately. Staged paths and diff checks passed; generated trailing blanks preserved. Certificate format documentation and browser harness retained; temporary QA removed and private ignored data preserved.
