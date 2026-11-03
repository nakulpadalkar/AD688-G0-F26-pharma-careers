"""Exercise the rendered OJS pages in Edge without a server or listening port.
Run: uv run --with playwright python -X utf8 scripts/test_ojs_browser.py
Only requests for the test origin are fulfilled from _site; other requests use
normal networking (Quarto's bundled runtime may load Observable libraries).
"""
import json
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
OUT = ROOT / 'artifacts/ojs-migration'
OUT.mkdir(parents=True, exist_ok=True)
scopes = json.loads((SITE/'outputs/us-employer-inventory/web/skills-data.json').read_text(encoding='utf-8'))['scopes']
benchmarks = json.loads((SITE/'outputs/us-employer-inventory/web/outlook-data.json').read_text(encoding='utf-8'))

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width':1280,'height':1000})
    errors = []
    page.on('pageerror', lambda err: errors.append(str(err)))
    def asset(route):
        target = (SITE/unquote(urlparse(route.request.url).path).lstrip('/')).resolve()
        if not target.is_relative_to(SITE) or not target.is_file():
            route.fulfill(status=404)
            return
        route.fulfill(path=str(target), content_type='text/javascript' if target.suffix == '.js' else mimetypes.guess_type(target)[0] or 'application/octet-stream')
    page.route('https://pharma.test/**', asset)
    def clean():
        assert not errors, errors
        assert page.locator('.observablehq--error').count() == 0
    def load(name):
        page.goto('https://pharma.test/'+name+'.html')
        expect(page.locator('.analytics-chart svg')).to_have_count(1, timeout=30000)
        clean()
    def mobile(name):
        page.set_viewport_size({'width':390,'height':844})
        page.evaluate('window.scrollTo(0, 0)')
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT/(name+'-mobile.png')), full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (name, page.evaluate("[...document.querySelectorAll('select, input, form, .panel')].filter(e => e.getBoundingClientRect().right > innerWidth).map(e => [e.tagName,e.className,e.getBoundingClientRect().right])"))
        assert page.locator('.analytics-chart').evaluate('(el) => el.scrollWidth > el.clientWidth'), 'Chart must be pannable on mobile'
        page.screenshot(path=str(OUT/(name+'-mobile.png')), full_page=True)
        clean()
        page.set_viewport_size({'width':1280,'height':1000})
    load('outlook')
    table = page.locator('.analytics-table table')
    expect(table.locator('tbody tr')).to_have_count(len(benchmarks['occupations']))
    for label, key in [('Median annual wage ($)','median'),('Annual projected openings','openings'),('Projected growth (%)','growth')]:
        page.get_by_label('Compare', exact=True).select_option(label=label)
        expect(page.locator('#growth-chart svg')).to_contain_text(label)
        best=max(benchmarks['occupations'],key=lambda d:d[key])
        expect(table.locator('tbody tr').first).to_contain_text(best['name'])
    # Native table heading sorting changes visible row order.
    table.get_by_text('Occupation',exact=True).click()
    expect(table.locator('tbody tr').first).to_contain_text(sorted(d['name'] for d in benchmarks['occupations'])[0])
    checks=page.locator('.analytics-controls input[type=checkbox]')
    for index in range(checks.count()):
        checks.nth(index).uncheck()
    expect(page.locator('#growth-chart')).to_contain_text('Select at least one occupation')
    page.wait_for_function("document.querySelector('.analytics-table form').value.length === 0")
    checks.nth(0).check()
    expect(table.locator('tbody tr')).to_have_count(1)
    for index in range(checks.count()):
        checks.nth(index).check()
    page.screenshot(path=str(OUT/'outlook-desktop.png'),full_page=True)
    mobile('outlook')
    load('skills')
    scope_control=page.get_by_label('Evidence scope',exact=True)
    search=page.get_by_label('Find a skill',exact=True)
    metric=page.get_by_label('Compare',exact=True)
    skill_control=page.get_by_label('Skill',exact=True)
    employer_control=page.get_by_label('Source employer',exact=True)
    skill_table=page.locator('.analytics-table').first.locator('table')
    evidence=page.locator('.analytics-evidence')
    for key,label in [('us','All US postings'),('analytics','Analytics-relevant US postings'),('data','Postings mentioning tracked data products / datasets')]:
        scope_control.select_option(label=label)
        scope=scopes[key]
        expect(page.locator('.analytics-controls')).to_contain_text(f"{scope['records']:,} US postings")
        expect(skill_table.locator('tbody tr')).to_have_count(len(scope['skills']))
        search.fill('sQl')
        expected=[s for s in scope['skills'] if 'sql' in s['name'].lower()]
        expect(skill_table.locator('tbody tr')).to_have_count(len(expected))
        if expected:
            skill=expected[0]
            expect(evidence).to_contain_text(f"{skill['records']:,} postings")
            expect(evidence).to_contain_text(f"{100*skill['records']/scope['records']:.1f}%")
            company=skill['sources'][0]['company']
            employer_control.select_option(label=company)
            expected_sources=[s for s in skill['sources'] if s['company']==company]
            expect(evidence).to_contain_text(f"Showing {len(expected_sources):,} source records")
            # Read the input's data value to verify all records, beyond visible rows.
            actual=evidence.locator('form').last.evaluate('(el) => el.value')
            assert {s['id'] for s in actual} == {s['id'] for s in expected_sources}
        search.fill('NO_MATCH_9274')
        expect(page.locator('#skills-chart')).to_contain_text('No skills match')
        page.wait_for_function("document.querySelector('.analytics-table form').value.length === 0")
        expect(evidence).to_contain_text('No skill selected')
        search.fill('')
    scope_control.select_option(label='All US postings')
    for label, axis in [('Share of scope (%)','Share of selected scope (%)'),('Employers','Employers'),('Posting mentions','Posting mentions')]:
        metric.select_option(label=label)
        expect(page.locator('#skills-chart svg')).to_contain_text(axis)
    skill_control.select_option(label='SQL')
    expect(evidence).to_contain_text('SQL appears')
    # Selection is persistent while focusing a source link; no hover DOM rebuild.
    link=evidence.get_by_role('link',name='Employer posting').first
    link.focus()
    page.locator('#skills-chart svg').hover()
    expect(link).to_be_focused()
    skill_table.get_by_text('Skill / data signal',exact=True).click()
    expect(skill_table.locator('tbody tr').first).to_contain_text(sorted(s['name'] for s in scopes['us']['skills'])[0])
    page.screenshot(path=str(OUT/'skills-desktop.png'),full_page=True)
    mobile('skills')
    clean()
    browser.close()
print('OJS_BROWSER_OK: 2 pages; 3 measures each; 3 skill scopes; sorting, source parity, empty/recovery states, focus, desktop and 390px mobile; no runtime errors; no server')
