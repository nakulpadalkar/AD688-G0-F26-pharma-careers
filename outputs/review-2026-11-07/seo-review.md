# SEO review — 2026-11-07

Scope: public GitHub Pages website, all 11 configured pages. Education and career-evidence publisher; not an active-vacancy board. Raw response evidence is in seo-evidence.json and *-live.html. No implementation changes made.

## Verified findings

- All 11 HTML pages returned HTTP 200. The live sitemap contains 11 URLs. All observed titles are distinct. No sampled page has a meta noindex directive. This establishes accessibility to this probe, not actual Google indexation.
- Five pages lack meta descriptions and H1 headings: Jobs, Skills, Geography, Outlook and Work. Add descriptive page-specific summaries and one visible top-level heading. Verify in rendered HTML and monitor Search Console landing-page impressions/CTR once available; description changes do not guarantee Google's chosen snippet.
- No sampled page has an explicit canonical. Configure the deployed site URL and consistent absolute self-canonicals, including the homepage preferred URL. Verify source HTML against sitemap and internal links. Missing canonical tags alone are not an indexing block.
- Boston and US market pages share the same meta description. Differentiate their geography and intent.
- No sampled page exposes Open Graph metadata or JSON-LD. Add truthful social preview metadata and eligible website/publisher metadata after ownership is established. Do not mark historical candidates as current JobPosting vacancies or imply measured placement outcomes.
- Domain-root robots.txt returns 404; this is not itself a crawl block. A project-path robots.txt does not govern the domain. The existing sitemap is the stronger immediate discovery asset.
- Homepage, Jobs, Geography and Work reference a shared 12,743,139-byte local JavaScript data file. This is uncompressed file size, not measured network transfer or a Core Web Vitals score. Split page-specific aggregates from job records and load job details when needed. Verify unchanged counts/filter outputs and compare transfer/parse work under the same mobile profile.
- Sources/methodology and explicit proposed-program/outcome limitations support credibility. Add a clearly named responsible maintainer/reviewer, review date and correction route. Do not invent institutional endorsement or graduate outcomes.

## Action sequence and verification

1. Correct browser accessibility/usability defects identified by Playwright; measure keyboard completion of core tasks.
2. Add H1s/descriptions/canonicals and differentiated market summaries. Success: each intended landing page has unique descriptive metadata and a consistent preferred URL. Recheck source HTML, not only browser DOM.
3. Split shared payloads, preserving Parquet-derived values. Success: less transfer/parse work without losing chart/filter parity. Field CWV must be checked separately after deployment.
4. Add authorship/review context and preview metadata. Success: visible factual ownership and valid previews. Monitor inquiry quality and search snippets rather than assuming ranking gains.

No Search Console, analytics, CrUX field data, ranking history, backlink audit or measured INP/LCP/CLS was available in this review. No aggregate SEO score is issued because it would imply measured coverage that is absent.

Primary references: [Google JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics), [canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), [snippets](https://developers.google.com/search/docs/appearance/snippet).
