# Visual employer markets

The US and Boston pages share `scripts/market-visuals.js`, `styles/market-visuals.css` and `_includes/market-visuals.html`. Maps and charts use saved snapshots; no live database, browser library CDN, API key or server is required to view them. Tables remain inside evidence disclosures. Sponsorship calculations remain separate from observed measures.

## Azure county source

`scripts/fetch_urban_counties.py --env-file <private-path>` is an explicit refresh, never a render hook. It enforces an Azure hostname, TLS, a read-only repeatable-read transaction, timeouts and row caps. It reads only the active public Urban release, headline county file 11 / all / All, and 2025 Census county boundaries at 5m. It selects the latest year with nonmissing employment observations, not the newest empty year. The export contains no credentials, connection endpoints, student data or job descriptions.

The current snapshot has 3,144 Urban observations for 2024. After excluding territories, 3,144 Census county boundaries are displayed: 2,609 have usable values, 535 do not; 2,026 usable estimates have marginal/weak quality. No nonterritory source FIPS is unmatched. Observation and extraction dates are separate. The source release, immutable Git commit, source Parquet URL and hash, license, confidence bounds and quality strings are retained in `data/urban-counties.parquet`.

Urban's `share_employed` is a 0–1 share of adults ages 25–54 employed, displayed as percent. No other `share_*` variable is scaled by analogy. False universe and missing/out-of-range values remain null; zero remains zero. All quality labels remain visible; marginal/weak estimates are hatched. County employment is general population context, not pharmaceutical employment, posting allocation or a training demand measure.

Attribution: Urban Institute, Mobility Metrics for the Upward Mobility Framework, ODC-BY 1.0. Definitions: https://ui-research.github.io/mobility-from-poverty-dictionary/variable_details/share_employed.html . Boundaries: US Census Bureau, 2025 cartographic boundaries, 1:5m; read from the existing Azure Census reference table. FIPS joins are exact; historic boundaries are never silently reassigned.

## Build and verification

`python scripts/build_market_visuals.py` produces projected paths, the offline data bundle, Parquet download and provenance receipt. Quarto invokes it after the US/Boston data builders. Run it once before the first render if generated includes are absent, because Quarto resolves include paths before pre-render hooks. County geometry is projected to the same Albers mainland and separate Alaska/Hawaii insets as the existing state map; regional zoom changes scale. The map does not compare geographic area with record volume.

`python scripts/test_market_visuals.py` checks exact joins, quality/missing/zero cases, source hashes and snapshot parity. Run it after rendering finishes, not while pre-render builders are replacing its hashed inputs. `uv run --with playwright python scripts/test_market_visuals_browser.py` checks maps, selectors, metric changes, missing estimates, disclosures and mobile width through file URLs without a server. Existing US/Boston browser tests verify sponsorship calculator behavior.

County shapes are selectable by mouse, while the labeled county dropdown supplies equivalent keyboard access. State paths support Enter/Space. Numeric bar labels and the expandable source tables accompany every visual. Keep a complementary detail panel as a `div role="complementary"`; Quarto treats a literal `aside` as margin content. Evidence subheads are generated as bold paragraphs so section headings do not close the disclosure prematurely.
