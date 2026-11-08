# Taste cleanup gates
Kind: educational career-evidence dashboard. Voice: plain, specific, source-grounded. Preserve blue/white/pink, Quarto, all counts and population distinctions.
- [x] G1: Replace generic headline with concrete purpose and working task links; retain the circular hero per user correction, simplify directory and improve text size.
  MANUAL: Inspect rebuilt desktop/mobile captures.
- [x] G2: Preserve data and interactions; provide meaningful H1s and descriptions on the five missing pages.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
- [x] G3: Render all 11 pages and inspect via one-shot Playwright; document any blocked visual checks.
  CHECK: quarto render
  EXPECT: Output created

Evidence: PowerShell/repo root; quarto render exit 0 for 11 pages; verify_site exit 0 with 457 links and snapshot/count parity. One-shot Playwright exit 0, 1440px and 390px screenshots inspected, document widths equal viewports; circular hero confirmed at desktop. PAGE_METADATA_OK for five pages. Taste copy lint: 0 FAIL, 1 WARN for real evidence-derived statistics retained by design. Full Taste server-dependent gate not run under no-server rule.
