# Pharma career site acceptance gates

- [x] G1: Traceable METEOR aggregates, geography exclusions, official benchmarks and job source dates; no invented placement outcomes.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
  EVIDENCE: PowerShell, repository root, exit 0. Counts reconcile; 11 geography controls; 51 map entries; 85 local links/anchors; bundled files match snapshots.
- [x] G2: Dashboard controls, job examples and work scenarios operate with the checked snapshots.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK
  EVIDENCE: PowerShell, repository root, exit 0. Minimal DOM fixture checks 2/13 examples, search/empty state, levels, three map measures, keyboard selection/reset and three scenarios. Syntax check also exits 0. Not browser layout validation.
- [x] G3: Existing Quarto site renders without executing data infrastructure or starting a server.
  CHECK: quarto render
  EXPECT: Output created
  EVIDENCE: PowerShell, repository root, exit 0. Three pages rendered; pre-render bundles snapshots only.
- [x] G4: Review generated pages/assets and record limitations and AAR.
  MANUAL: Source, generated HTML, responsive CSS, data provenance and verification receipt reviewed. Browser file URL blocked by policy; no server authorized, so visual/mobile QA is explicitly unverified. See docs/verification.md and LESSONS.md.

Final state: 4 met, 0 unmet, 0 abandoned within the stated verification scope. Browser visual QA is not claimed. No deployment performed.
