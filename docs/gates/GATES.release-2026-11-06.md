# Release verification: 2026-11-06

- [x] G1: All branches fetched and recent source updates reviewed.
  MANUAL: Inspect remote refs, status, stashes and changed build inputs.
- [x] G2: Eleven pages build and evidence, frontend and browser checks pass.
  MANUAL: Run reviewed offline data checks, Quarto render, JS checks and headless browser tests without a server.
- [x] G3: Targeted commits preserve source and generated outputs; temporary artifacts removed and private data excluded.
  MANUAL: Inspect staged paths and diff checks.
- [x] G4: Main pushed, remote matches HEAD, working tree and stash list empty.
  MANUAL: Fetch after push and verify Git state.

Evidence: PowerShell, repository root. Fetched all remotes; main current before commits; gh-pages is generated publication output. No stashes, symlinks or root HTML duplicates. Stopped the repository preview and waited for exit before clearing .quarto. Quarto rendered 11 pages. Inventory, metrics, Boston, US and training-market checks passed; 485 local links resolved; mocked runner checks passed without DB calls. JS syntax, dashboard, OJS parity and all three Edge headless desktop/mobile browser suites exited 0. No local server started. Temporary QA screenshots removed after successful tests.

AAR: Expected complete update preservation and a clean verified push. Actual build and all checks passed. Prior preview/cache lessons prevented competing renders; the new market pages required additional checks beyond the previous release suite. Continue deriving release checks from current page and script inventory. No new rule or skill change needed; existing lessons cover this pattern.

G3 evidence: separate visual-restoration, market-source and generated-site commits created. Source whitespace and staged-path checks passed; generated Quarto whitespace retained. Private raw, processed and enrichment datasets remain ignored. All remaining untracked deliverables are preserved in verification records.

G4 evidence: push through c73403a succeeded; verification fetch confirmed HEAD equals origin/main, and status --porcelain and stash list returned no entries. Four gates met, zero unmet or abandoned. Final receipt commit is verified again after push.
