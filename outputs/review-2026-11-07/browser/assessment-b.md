# Assessment B: detector and browser evidence

Scope: original local rendered markup detector; subsequent local rendered-site browser checks after parent cleanup began. This is not a live deployment verification. Live browser navigation failed with ERR_NAME_NOT_RESOLVED; escalated retry was aborted while awaiting approval. No local server was started. No browser overlay injected because it requires a prohibited local listener.

## Browser evidence
- Seven pages loaded from file URLs, tested at 1440x1000 and 390x844. All seven document scroll widths equaled their viewport widths. Wide table descendants stayed within scrolling containers; do not report these as page overflow.
- Jobs: default 9,493 postings, 12 rendered cards; analytics filter 1,127; impossible search displays informative empty state; pagination advances to page 2 of 792.
- Geography: selecting share and keyboard Enter on Massachusetts updates detail to Massachusetts / 8.1%.
- US market: county layer plus Massachusetts region yields 14 counties plus placeholder; first county Barnstable renders 84.6%, interval 80.8–88.4%, FIPS25001, year2024 and strong quality.
- All seven tested pages have zero Parquet links.
- Skills hover and keyboard could NOT be exercised: local file CORS blocks Quarto ES modules and Observable runtime; sandbox DNS also prevents external dependencies. These errors are limitations of this test environment, not proven production defects. Source code does wire click, focus and mouseenter to selected skill and updates aria-pressed.
- Browser runtime errors were file-module CORS, failed external DNS and an Observable initialization error following module failure. Do not attribute them to deployed website.

## Detector evidence
Deterministic scan ran against original _site/index.html, jobs.html, skills.html, geography.html, us-market.html, before parent cleanup. Findings are heuristic, not verified accessibility failures. Low-contrast token comparisons need actual rendered foreground/background verification; a pale token intended as background must not be counted as low contrast text. Design-pattern warnings need context judgement and preservation of user-requested blue/white/pink identity.

Total detector findings: 43

{
  "low-contrast": 4,
  "hero-eyebrow-chip": 1,
  "tiny-text": 11,
  "undersized-ui-text": 7,
  "overused-font": 5,
  "dark-glow": 5,
  "kicker-above-heading": 7,
  "border-accent-on-rounded": 3
}
