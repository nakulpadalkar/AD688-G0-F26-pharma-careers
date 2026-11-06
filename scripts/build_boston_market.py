"""Reproducible employer-market evidence from saved, sanitized posting identities."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from artifact_io import read_data, artifact_path
from build_evidence import locate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/boston-market'
# Deliberate sales outreach geography, not an official metropolitan boundary.
TOWNS = ['Boston', 'Cambridge', 'Watertown', 'Waltham', 'Lexington', 'Burlington',
         'Billerica', 'Bedford', 'Woburn', 'Somerville', 'Newton', 'Needham',
         'Medford', 'Framingham', 'Natick', 'Marlborough', 'Andover']
COMMERCIAL = {'commercial_analytics_title', 'commercial_data_duties',
              'data_product_in_business_role', 'data_product_or_dataset_in_role'}

def region(row):
    """Conservative state evidence first; ambiguous city-only names stay out."""
    location = row.get('location', '')
    if locate({'location_text': location, 'countryiso': row.get('country', '')}) != ('mapped_state', 'MA'):
        return 'outside_or_unresolved'
    if any(re.search(r'\b' + re.escape(t) + r'\b', location, re.I) for t in TOWNS[:2]):
        return 'Boston / Cambridge'
    if any(re.search(r'\b' + re.escape(t) + r'\b', location, re.I) for t in TOWNS[2:]):
        return 'Outreach suburbs'
    return 'Other Massachusetts'

def commercial(row):
    return bool(row.get('analytics_relevant')) and row.get('relevance_basis') in COMMERCIAL

def summarize(rows):
    analytics = [r for r in rows if r.get('analytics_relevant')]
    direct = [r for r in rows if commercial(r)]
    dates = [r['posted_on'] for r in rows if r.get('posted_on')]
    return {'postings': len(rows), 'employers': len({r['company'] for r in rows}),
            'analytics': len(analytics), 'commercial': len(direct),
            'missing_posted_date': sum(not r.get('posted_on') for r in rows),
            'posted_min': min(dates, default=None), 'posted_max': max(dates, default=None),
            'commercial_skills': dict(Counter(s for r in direct for s in set(r['skills'])).most_common()),
            'commercial_degrees': dict(Counter(s for r in direct for s in set(r['requirements']['degrees_mentioned'])).most_common()),
            'commercial_levels': dict(Counter(r['level'] for r in direct).most_common()),
            'commercial_no_degree_detected': sum(not r['requirements']['degrees_mentioned'] for r in direct),
            'commercial_equivalent_experience': sum(r['requirements']['equivalent_experience_language'] for r in direct)}

def compute(jobs, employers):
    local = [r for r in jobs if region(r) in ('Boston / Cambridge', 'Outreach suburbs')]
    ma = [r for r in jobs if region(r) != 'outside_or_unresolved']
    companies = {r['company'] for r in jobs}
    table = []
    for e in employers:
        selected = [r for r in local if r['company'] == e['inventory_company']]
        ma_rows = [r for r in ma if r['company'] == e['inventory_company']]
        size = e['ma_employees']
        table.append({**e, 'size_band': '2,000+' if size >= 2000 else '500–1,999' if size >= 500 else 'Under 500',
                      'inventory_covered': e['inventory_company'] in companies,
                      'local_postings': len(selected), 'local_analytics': sum(r['analytics_relevant'] for r in selected),
                      'local_commercial': sum(commercial(r) for r in selected), 'ma_postings': len(ma_rows)})
    return {'us': summarize(jobs), 'ma': summarize(ma), 'local': summarize(local),
            'core': summarize([r for r in local if region(r) == 'Boston / Cambridge']),
            'geography_counts': dict(Counter(region(r) for r in jobs)), 'employers': table,
            'shortlist_employees': sum(e['ma_employees'] for e in table),
            'shortlist_covered': sum(e['inventory_covered'] for e in table),
            'local_company_counts': dict(Counter(r['company'] for r in local).most_common()),
            'local_commercial_company_counts': dict(Counter(r['company'] for r in local if commercial(r)).most_common())}

def build():
    employers = json.loads((OUT/'data/employers.json').read_text(encoding='utf-8'))
    context = json.loads((OUT/'data/market-context.json').read_text(encoding='utf-8'))
    jobs = read_data('database-jobs.json')
    result = compute(jobs, employers)
    result['context'] = context
    result['inventory_checked_at'] = read_data('inventory-summary.json')['checked_at_utc']
    result['towns'] = TOWNS
    result['source_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [artifact_path('database-jobs.json'), artifact_path('inventory-summary.json'),
                                         OUT/'data/employers.json', OUT/'data/market-context.json']}
    (OUT/'web').mkdir(parents=True, exist_ok=True)
    (OUT/'web/market-summary.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    table = result['employers']
    with (OUT/'web/employer-prospects.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0])); writer.writeheader(); writer.writerows(table)
    rows = ['### Market scale', '', '| Evidence | Count | Meaning |', '|---|---:|---|',
            f"| Boston + Cambridge life-sciences members | {context['boston_member_companies_2026'] + context['cambridge_member_companies_2026']:,} | 331 Boston + 429 Cambridge; 2026 membership map |",
            f"| Massachusetts life-sciences members | {context['ma_member_companies_2026']:,} | Broad statewide prospect universe; includes the core above |",
            f"| Massachusetts biopharma workforce | {context['ma_employment_2025']:,} | All functions, 2025; down 3.1% year over year |",
            f"| Major-employer shortlist | {len(table)} | Selected by the source's largest-employer chart, not buyer qualification |",
            f"| Combined shortlist workforce | {result['shortlist_employees']:,} | Reported Massachusetts employees, 2026; not training seats |", '',
            f"Sources: [MassBio 2026 Industry Snapshot]({context['source_url']}), pp. 6, 11 and 37. Company sizes are from the member survey; Moderna uses the Boston Business Journal Book of Lists. Reviewed {context['reviewed_on']}. Workforce and shortlist dates differ, so no market-share percentage is calculated.", '',
            '### Company size and our demand evidence', '',
            'Local means Boston/Cambridge plus the explicitly listed outreach suburbs below. All posting counts are historical saved identities. A dash means the employer is outside the current inventory; zero means covered but no matching local posting was found.', '',
            '| Employer | MA employees (2026) | Local postings | Analytics | Commercial fit |', '|---|---:|---:|---:|---:|']
    for e in table:
        vals = [str(e[k]) if e['inventory_covered'] else '—' for k in ['local_postings', 'local_analytics', 'local_commercial']]
        rows.append(f"| [{e['company']}]({e['source_url']}) | {e['ma_employees']:,} | {' | '.join(vals)} |")
    rows += ['', 'AstraZeneca/Alexion workforce is combined in MassBio; our posting match covers AstraZeneca only. These are Massachusetts headcounts, not Boston office counts or worldwide employee totals.', '',
             '| MA workforce band | Shortlisted companies | Combined employees | Suggested sales approach |', '|---|---:|---:|---|']
    for band, approach in [('2,000+', 'Team cohort; commercial analytics leader plus learning and development'), ('500–1,999', 'Cross-functional cohort or shared employer cohort'), ('Under 500', 'Individual sponsorship or consortium seats')]:
        subset = [e for e in table if e['size_band'] == band]
        rows.append(f"| {band} | {len(subset)} | {sum(e['ma_employees'] for e in subset):,} | {approach} |")
    rows += ['', 'Size bands describe only this selected shortlist. They do not estimate the size distribution of all 760 core companies. Buying capacity and curriculum fit require employer conversations.', '',
             '### What the employability data supports', '',
             f"Saved inventory audit: {result['inventory_checked_at']}. Recomputed from the existing sanitized local/Azure inventory; no new database extraction or live vacancy check was performed.", '',
             '| Geography | All postings | Employers | Analytics | Commercial fit | Missing posting date |', '|---|---:|---:|---:|---:|---:|']
    for label, key in [('Selected US employer inventory', 'us'), ('Massachusetts, explicit state', 'ma'), ('Boston / Cambridge, explicit state', 'core'), ('Core + outreach suburbs', 'local')]:
        d = result[key]
        rows.append(f"| {label} | {d['postings']:,} | {d['employers']} | {d['analytics']} | {d['commercial']} | {d['missing_posted_date']} |")
    local = result['local']
    priorities = ', '.join(f'{name} ({n})' for name, n in result['local_commercial_company_counts'].items()) or 'No rule-matched records'
    rows += ['', f"**First employers to validate:** {priorities}. Parentheses show local commercial-fit posting identities, not prospective enrollments. This ranking measures observed relevance in a selected dataset; collection coverage differs across employers.", '',
             f"Only {result['shortlist_covered']} of the {len(table)} shortlisted employer names are represented in the US inventory. Missing companies remain prospect-research opportunities, not evidence of no demand.", '',
             f"Local source-reported posting dates range from {local['posted_min']} to {local['posted_max']}; {local['missing_posted_date']} local records lack a source posting date. Database-created dates remain collection proxies. All dates, including old records, are included; these counts cannot measure current openings or annual hiring.", '',
             '#### Skills and qualifications in the local commercial-fit subset', '',
             '| Skill term | Posting identities |', '|---|---:|']
    rows += [f'| {s} | {n} |' for s, n in local['commercial_skills'].items()]
    rows += ['', f"Denominator: {local['commercial']} local commercial-fit identities. Skill terms overlap and do not distinguish mandatory requirements from preferences. Commercial-fit rules partly use data terms, so this is not an independent estimate of market-wide skill prevalence.", '',
             'Degree terms: ' + ', '.join(f'{k} ({v})' for k, v in local['commercial_degrees'].items()) + '.', '',
             f"No degree term detected: {local['commercial_no_degree_detected']}; equivalent-experience wording: {local['commercial_equivalent_experience']}. Terms overlap; neither finding proves that a degree is optional. A non-degree certificate does not replace employer education or experience requirements.", '',
             'Career-level labels inferred from titles: ' + ', '.join(f'{k} ({v})' for k,v in local['commercial_levels'].items()) + '.', '',
             '#### Geography and screening rules', '',
             'Outreach area: ' + ', '.join(TOWNS) + '. This is a declared sales territory, not the official Boston metropolitan statistical area. Worcester and other Massachusetts locations appear only in the statewide row.', '',
             'State evidence uses the existing conservative parser: explicit Massachusetts or a comma-delimited MA abbreviation. City-only Cambridge, state-prefix strings such as “Ma Cambridge”, remote-only locations and conflicting multi-state locations stay outside local counts. Therefore these are conservative observed counts, not complete local hiring coverage.', '',
             'Commercial fit is the subset of analytics-relevant records with commercial analytics titles, commercial-data duties, data products in business roles, or data products/datasets in analytical roles. It reuses the saved relevance reasons, without treating all clinical, scientific or operations analytics roles as certificate matches. Review individual duties before outreach.', '',
             '[Download employer table](outputs/boston-market/web/employer-prospects.csv) · [Download calculated evidence and source hashes](outputs/boston-market/web/market-summary.json)']
    (OUT/'web/evidence.qmd').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print('BOSTON_MARKET_BUILT', json.dumps({k: result[k] for k in ['local', 'shortlist_employees', 'shortlist_covered']}))

if __name__ == '__main__':
    build()
