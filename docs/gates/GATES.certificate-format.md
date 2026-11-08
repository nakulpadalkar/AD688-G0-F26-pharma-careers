# Certificate website integration

- [x] G1: Certificate page describes agreed non-credit, self-paced semester format and four courses totaling 14 weeks; brochure facts remain separate.
  MANUAL: Inspect source and rendered page against approved syllabus and both brochures.
- [x] G2: Full static build and existing link/evidence verification pass.
  CHECK: quarto render
  EXPECT: METRICS_OK
  CHECK: python scripts/verify_site.py
  EXPECT: PARQUET_SITE_OK
- [x] G3: Desktop and mobile certificate rendering have no horizontal overflow and curriculum and learning-format navigation works without a server.
  MANUAL: Bundled headless Chromium file-URL inspection and screenshots at 1440 and 390 pixels.
- [x] G4: Review diff and record AAR with evidence and publication status.
  CHECK: git diff --check
  EXPECT: exit 0

## Verified evidence

- G1: Inspected both supplied PDF texts and flyer rendering; compared all four course topics and 3 + 4 + 4 + 3 pacing to the updated syllabus. Brochure-specific tuition, start dates, faculty, contact information, and badges were excluded. Current program status stays proposed.
- G2: PowerShell, repository root: quarto render exited 0, rendered all 11 pages, and emitted METRICS_OK. python scripts/verify_site.py exited 0 with EVIDENCE_OK (466 local links and anchors) and PARQUET_SITE_OK.
- G3: node C:/Users/nakulpadalkar/.codex/skills/playwright/scripts/run-browser.cjs D:/Repositories/AD688-G0-F26-pharma-careers/docs/certificate-browser.cjs exited 0 with CERTIFICATE_BROWSER_OK. Four curriculum rows, curriculum/format anchors, and no horizontal overflow at 1440 and 390 pixels. Reviewed desktop and full mobile screenshots in outputs/certificate/qa. No server started. Impeccable detector returned an empty findings array.
- G4: Reviewed source and generated diffs. Full render regenerated the shared CSS hash and page references. Existing market pre-render also reordered two tied degree labels (14 each) with unchanged counts and regenerated matching bundles. git diff --check exited 0. Recorded AAR in LESSONS.md. No commit, push, PR, or publication performed.

Final: 4 met, 0 unmet, 0 abandoned.
