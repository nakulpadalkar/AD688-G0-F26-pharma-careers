"""Check the static market page in Edge through file URLs; no server."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/us-market/qa'
OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 960})
    page.goto((ROOT/'_site/us-market.html').as_uri())
    expect(page.locator('#sponsor-result')).to_contain_text('40 expected certificate starters')
    for key, value in [('accounts', '20'), ('rate', '10'), ('seats', '5'), ('fee', '1000')]:
        page.locator('#sponsor-' + key).fill(value)
    expect(page.locator('#sponsor-result')).to_contain_text('10 expected certificate starters')
    expect(page.locator('#sponsor-result')).to_contain_text('$10,000')
    page.locator('#sponsor-accounts').fill('101')
    expect(page.locator('#sponsor-result')).to_contain_text('Enter valid')
    page.locator('#sponsor-accounts').fill('0')
    expect(page.locator('#sponsor-result')).to_contain_text('0 expected certificate starters')
    for key, value in [('accounts', '50'), ('rate', '10'), ('seats', '8'), ('fee', '0')]:
        page.locator('#sponsor-' + key).fill(value)
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(OUT/'desktop.png'), full_page=True)
    page.screenshot(path=str(OUT/'desktop-top.png'))
    page.set_viewport_size({'width': 390, 'height': 844})
    page.screenshot(path=str(OUT/'mobile.png'), full_page=True)
    page.screenshot(path=str(OUT/'mobile-top.png'))
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Mobile overflow'
    assert page.locator('a[href="outputs/us-market/web/employers.csv"]').count() == 1
    browser.close()
print('US_BROWSER_OK: calculator defaults, changes, invalid and zero inputs; mobile width')
