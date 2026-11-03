# Lessons

Written by /aar-loop after each session's After Action Review. Read this file before starting a new task in this project. Every entry should be concrete and checkable, never vague.

## 2026-11-02 -- In the saved pharma audit, countryiso is blank for 1326 of 1353 commercial candidates; retain explicit exclusions for foreign records and known corrupt locations such as Hyderabad, Indiana. Only 654 records map conservatively to states. Keep historical counts separate from dated employer application-page checks and from BLS employment projections.
- Expected: Build a modern pharma career website grounded in METEOR and official labor statistics.
- Actual: Three static Quarto pages built with traceable aggregates, two checked employer examples, thirteen historical examples and interactive choropleth. Browser file URL was blocked; static and simulated-DOM checks passed.
- Why: Source geography and classification fields are incomplete or inconsistent, and the supported browser disallows file URLs. The no-server instruction prevents local HTTP preview. Geography exclusions, source vintages and verification limits remain visible. No standing-rule fix proposed.
- tags: pharma,geography,website,evidence

## 2026-11-02 -- When moving dashboard sections into separate QMD pages, guard each JavaScript module by its own DOM container and test each rendered page independently with absent elements returning null. Keep home as a directory and verify cross-page anchors after moving sections.
- Expected: Replace the long-scrolling dashboard with focused website pages.
- Actual: Eight Quarto pages render; 274 local links and anchors and eight independent page initialization tests pass.
- Why: The original dashboard assumed all containers existed on one page. Module-level guards preserve interactions after splitting content. A transient missing Bootstrap asset on first render resolved on unchanged rerender; no standing-rule change proposed.
- tags: quarto,navigation,javascript

## 2026-11-02 -- For direct employer samples, store source_access and availability separately: Workday can expose indexed job text while the live page has no readable body, and Pfizer job URLs can redirect to search. Use application_observed only for readable pages with an observed application control; exclude indexed-only rows from the readable skills scope. Keep country and currency explicit for overseas roles supporting US teams.
- Expected: Expand direct pharma jobs and skills evidence and verify company presence in local PostgreSQL and Azure.
- Actual: Ten employers annotated, five readable application-link pages and five indexed-only sources; all ten employers found in both databases through read-only queries. Eight rendered pages, 276 links and interaction checks pass.
- Why: Indexed descriptions can outlive application deadlines or readable pages. Separate source access, status and geographic scopes prevent stale roles or overseas salaries from being presented as current US openings. No standing-rule fix proposed.
- tags: employer-sources,freshness,postgres,azure

## 2026-11-02 -- For the US employer selector, test zero job cards before selection and after clearing selection, employer-isolated results, and rejection of a non-US employer value. Derive employer counts and the US download from country=US, not from US-team wording.
- Expected: US-only job explorer showing employer counts and cards after company selection.
- Actual: Six US employers and six postings; two US skill scopes; eight-page render, 277 links and selector regressions passed.
- Why: No remaining gap. Explicit country filtering and empty-selection tests keep the employer-first interaction consistent with its download and skills denominator. No standing-rule change needed.
- tags: jobs,us-scope,employer-selector

## 2026-11-02 -- For isolated Quarto checks, copy the current artifact_io.py data dependencies under outputs/site-reference, outputs/employer-page-review/data and outputs/us-employer-inventory/curated; data/ alone no longer supplies the pre-render bundle.
- Expected: Apply the blue-white-pink palette and render the existing website.
- Actual: Palette updated; shared render twice failed moving jobs.html. An isolated eight-page build succeeded after including current Parquet dependencies.
- Why: The repository changed concurrently, including conversion of build inputs to task-scoped Parquet. Shared build failure cause was not established. Read current dependencies before isolated verification; no standing rule changes proposed.
- tags: quarto,palette,concurrent-work

## 2026-11-02 -- For skill bubbles, key detail rendering by scope and skill index. Repeated mouseover events from child text must not replace the detail DOM; ignore hover while a source link inside skill-detail holds keyboard focus. Test both cases with the existing DOM fixture.
- Expected: Widen the site to 1100px and improve readability and hover accessibility.
- Actual: Widened body and CSS caps, increased spacing and type, added selection and control semantics, and verified repeated hover and focus protection. Isolated eight-page build and 282 local links passed; browser visual QA remains unavailable.
- Why: Bubbling mouseover events rebuilt the selected details unnecessarily. A selected-key guard preserves open source details. Shared Quarto output still encounters file-move failures, so verification used an isolated build. No standing-rule changes proposed.
- tags: accessibility,hover,quarto

## 2026-11-02 -- For the full employer inventory, reconcile 18,443 local and 4,549 Azure source rows separately from deduplicated US-relevant identities. Keep posted_at and created_at separate in compressed task-scoped Parquet; label created_at fallbacks as first-recorded proxies and include null posted_at rows in complete extracts.
- Expected: Expose complete employer coverage, independent filters and auditable dates in task-scoped data files.
- Actual: 22,992 raw rows retained; 253 US-relevant identities across 12 employers; 129 source posting dates and 124 collection proxies. Inventory, interactions and 282-link checks pass.
- Why: The earlier six-job example sample was a different population from the database extracts. Name matches, store overlap, geography and relevance reduce usable identities; missing posted dates require explicit provenance. No standing-rule change proposed.
- tags: parquet,inventory,dates,postgres,azure

## 2026-11-02 -- The 253-record commercial-only screen is not the full pharmaceutical data-careers population. Keep inclusion-rule counts in inventory-summary.parquet and generated methods; test clinical data, biostatistics, operations analysts and analytical duties with technical tools separately from commercial vendor signals. Use explicit UTF-8 for source reads and writes on Windows.
- Expected: Expand evidence-based US career coverage consistently across the website.
- Actual: 1,127 posting identities across 13 employers; 874 additions; eight pages rendered, 282 links and all inventory/filter checks passed.
- Why: Commercial title and vendor requirements excluded adjacent data careers. Broader documented rules preserve US evidence and deduplication. Encoding and concurrent card-layout changes were detected by checks and reconciled. No standing-rule changes proposed.
- tags: inventory,scope,parquet,encoding

## 2026-11-02 -- For website prose revisions, edit QMD pages, shared _includes, scripts/dashboard.js and scripts/build_site_data.py together. Generated findings and scenario text otherwise restore editorial instructions on the next build. Keep build commands in repository documentation rather than public methods prose.
- Expected: Use mechanism-first prose and remove internal commentary and instructions from public pages.
- Actual: Eight pages revised and rendered; 282 links and interaction checks passed; 1,127 postings across 13 employers preserved.
- Why: Public copy is distributed across page sources, HTML includes, browser templates and Python generators. Revised those sources and verified the local render. No standing-rule changes proposed.
- tags: writing,website,generated-copy

## 2026-11-02 -- Before rendering AD688 G0, inspect existing Quarto preview processes targeting this checkout. A running jobs.qmd preview competed for root HTML and _site files. Stop that preview before a release build; if Quarto openKv then reports disk I/O error, remove only this checkout .quarto cache and render again.
- Expected: Render all eight pages in the shared checkout and preserve recent changes in main.
- Actual: Clean temporary render passed; shared render passed after stopping the repository preview and clearing .quarto. Inventory, 282 local links and dashboard checks passed.
- Why: A Quarto preview targeting jobs.qmd was running while render moved shared HTML files. The subsequent cache error disappeared after removing .quarto. No standing-rule changes proposed.
- tags: quarto,build,cleanup
