# Website review gates
- [x] G1: Independent design assessment with desktop/mobile rendered evidence.
  MANUAL: Inspect Assessment A captures and findings.
- [x] G2: Browser interactions and detector findings with reproducible evidence.
  MANUAL: Inspect Assessment B results after Assessment A completes.
- [x] G3: Live SEO metadata and discovery checks, with unavailable metrics explicit.
  CHECK: python outputs/review-2026-11-07/seo_probe.py
  EXPECT: SEO_PROBE_OK
- [x] G4: Synthesize priorities, limitations and verification criteria; review only, no UI changes.
  MANUAL: Reconcile report claims to captured evidence.

G3 evidence: PowerShell, repo root, Python probe exited 0 after approved network retry; SEO_PROBE_OK, 11 HTTP-200 pages and 11 sitemap URLs. SEO field/traffic metrics unavailable and explicitly excluded.

G1/G2/G4 evidence: independent Assessment A completed before B findings were read. Reports, screenshot inspection and browser-results saved; seven-page local browser coverage and live SEO coverage explicitly separated. Skill-bubble execution unavailable and disclosed; no deployment or field-CWV claims. Final synthesis in outputs/review-2026-11-07/REVIEW.md.
