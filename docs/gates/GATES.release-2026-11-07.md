# Release verification: November 7, 2026

- [x] G1: All remote branches inspected and local updates preserved.
  MANUAL: Fetch/prune, branch, status, stash and source-diff review.
- [x] G2: All eleven pages and current data/frontend/browser checks pass.
  MANUAL: Run reviewed Quarto render and Python/Node/Edge checks with saved evidence and no server.
- [x] G3: Targeted source/output commits; cleanup complete and no private data staged.
  MANUAL: Inspect staged paths, whitespace, temporary artifacts and final status.
- [x] G4: Main pushed and synchronized; Quarto Publish and Pages deployment succeed.
  MANUAL: Verify remote HEAD, empty status/stashes and Actions run results.

Evidence: PowerShell, repository root. Fetch/prune succeeded; main initially matched origin/main and gh-pages is generated publication output. No stashes, initial untracked files, symlinks or running preview. First render failed with WinError 32 replacing a Parquet temp file; full retry rendered 11 pages. Inventory, site, metrics, Boston, US, training-market, market-visual and mocked-runner tests passed; 457 local links and no dataset download links verified. Three JS syntax checks, two Node suites and four Edge headless browser suites passed. No server or database refresh was started. Generated QA artifacts and the identified failed-render temp file removed after success.

G3 evidence: source/generator and rendered-site updates committed separately. Staged paths and diff checks passed; generated trailing blank lines retained. Private ignored extracts preserved. README reflects removed download links. AAR recorded in LESSONS.md.

G4 evidence: corrected main release 413a002 pushed successfully. Quarto Publish 42439558471 and Pages deployment 42439716814 both succeeded; deployed gh-pages a599ee6743802f2b13bdddc04ae6d2360e527d43. Fetch verified synchronized main and empty status/stashes. Four gates met; zero unmet or abandoned. Final checklist-only commit uses [skip ci].

Final review correction: Quarto had copied the failed-render temporary Parquet into _site before source-temp cleanup. Removed the copied artifact in 413a002, added verify_site.py rejection of any published .tmp file, and reran site verification successfully. No temporary files remain in the site.
