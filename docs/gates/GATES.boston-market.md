# Boston employer market analytics gates

Scope: Add a source-backed employer market page, reproducible saved-inventory analysis, and explicit employer-sponsored training scenarios. No publication requested.

- [x] G1: Regional headcount evidence distinguishes Massachusetts from Boston and an employer shortlist from a market census.
  MANUAL: Review source dates, scopes, links, missing company counts and size bands.
  EVIDENCE: Visually checked MassBio 2026 PDF pages 11 and 37; 20 employer values sum to 40,521. Page distinguishes MA workforce, core membership, selected employers, and unknown qualified-buyer count.
- [x] G2: Recompute local employer demand from saved posting identities, with geography and commercial-fit rules, exclusions and provenance.
  CHECK: python scripts/test_boston_market.py
  EXPECT: BOSTON_MARKET_OK
  EVIDENCE: PowerShell, repository root, exit 0: BOSTON_MARKET_OK; geography positive/negative controls, source hashes, changed-input controls and population reconciliation. Reverified after final render.
- [x] G3: Integrate page into navigation and certificate page, render without a server, and verify existing metrics and links.
  CHECK: quarto render
  EXPECT: Output created
  EVIDENCE: PowerShell, repository root, exit 0: all nine pages rendered; final page-only rerender passed METRICS_OK. verify_site.py exit 0: 357 local links. test_boston_browser.py exit 0: calculator defaults/changes/invalid/zero inputs and 390px mobile width; desktop/mobile previews inspected. No server started.
- [x] G4: Review diff and record AAR with no unsupported enrollment or placement claims.
  MANUAL: Inspect final artifacts and source diff whitespace.
  EVIDENCE: Reviewed generated table and page, verified source diff --check exit 0 on task files; Quarto-generated HTML retains renderer-produced trailing whitespace in navigation. AAR appended to existing LESSONS.md; no rule changes. Concurrent changes to other pages/styles preserved. No commit, push or publication performed.

Completion: 4 met, 0 unmet, 0 abandoned.
