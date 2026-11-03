"""Derive display statistics from saved evidence, never from HTML literals."""
from collections import Counter
from copy import deepcopy
from datetime import date
import hashlib
import json
import re


def derive_inventory(jobs, raw, previous):
    result = deepcopy(previous)
    result.update(
        job_count=len(jobs),
        source_counts=dict(Counter(r['store'] for r in raw)),
        analytics_relevant_jobs=sum(bool(j['analytics_relevant']) for j in jobs),
        other_us_jobs=sum(not j['analytics_relevant'] for j in jobs),
        undated_jobs=sum(not j['posted_on'] for j in jobs),
        data_signal_jobs=sum(bool(j['data_signals']) for j in jobs),
        data_signals=dict(Counter(s for j in jobs for s in j['data_signals'])),
        education=dict(Counter(d for j in jobs for d in j['requirements']['degrees_mentioned'])),
        degree_not_detected=sum(not j['requirements']['degrees_mentioned'] for j in jobs),
        equivalent_experience_language=sum(j['requirements']['equivalent_experience_language'] for j in jobs),
        relevance_counts=dict(Counter(j['relevance_basis'] for j in jobs)),
        date_basis_counts=dict(Counter(j['date_basis'] for j in jobs)),
    )
    for company in result['companies']:
        rows = [j for j in jobs if j['company'] == company['company']]
        company.update(jobs=len(rows), local_jobs=sum('local' in j['stores'] for j in rows),
                       azure_jobs=sum('azure' in j['stores'] for j in rows),
                       both_jobs=sum(len(j['stores']) == 2 for j in rows))
        company['raw_records'] = dict(Counter(r['store'] for r in raw if r['canonical_employer'] == company['company']))
    assert sum(c['jobs'] for c in result['companies']) == len(jobs), 'Unknown employer in saved jobs'
    result['employers_with_jobs'] = sum(c['jobs'] > 0 for c in result['companies'])
    result['experience_by_level'] = {
        level: dict(Counter(y for j in jobs if j['level'] == level for y in j['requirements']['experience_year_mentions']))
        for level in sorted({j['level'] for j in jobs})
    }
    result['raw_date_basis_counts'] = {
        store: dict(Counter(r['date_basis'] for r in raw if r['store'] == store))
        for store in result['source_counts']
    }
    return result


def derive_metrics(bundle, course_count):
    meteor, benchmark, inventory = (bundle[k] for k in ('meteor', 'benchmarks', 'inventory'))
    industry = benchmark['industry']
    start, end = map(int, re.findall(r'\d{4}', benchmark['projection_period']))
    base, projected = industry[f'employment_{start}'], industry[f'employment_{end}']
    assert base > 0 and end > start
    growth = (projected / base - 1) * 100
    annual = ((projected / base) ** (1 / (end - start)) - 1) * 100
    mapped = sum(s['records'] for s in meteor['geography']['states'])
    total = sum(m['records'] for m in meteor['monthly'])
    assert total == meteor['counts']['commercial_candidates'] == sum(meteor['geography']['buckets'].values())
    assert mapped == meteor['geography']['mapped_records']
    assert len(bundle['historical']) == meteor['counts']['reviewed_examples']
    values = {f'meteor_{k}': f'{v:,}' for k, v in meteor['counts'].items()}
    values.update(
        meteor_commercial_candidates=f'{total:,}', mapped_records=f'{mapped:,}',
        mapped_share=f'{mapped / total * 100:.1f}' if total else '0.0',
        reviewed_examples=str(len(bundle['historical'])),
        blank_country=f"{sum(r['records'] for r in meteor['country_codes'] if r['code'] == '(blank)'):,}",
        naics_valid=f"{meteor['classification']['naics_4_6_digit']:,}",
        naics_pharma=f"{meteor['classification']['naics_3254_prefix']:,}",
        employers_searched=str(len(inventory['companies'])),
        employers_with_jobs=str(inventory['employers_with_jobs']), job_count=f"{inventory['job_count']:,}",
        raw_records=f"{sum(inventory['source_counts'].values()):,}",
        industry_base=f'{base:,}', industry_projected=f'{projected:,}',
        industry_growth=f'{growth:.1f}', industry_annual_growth=f'{annual:.1f}',
        projection_start=str(start), projection_end=str(end),
        projection_period=benchmark['projection_period'], wage_year=str(benchmark['wage_year']),
        industry_naics=industry['naics'], industry_matrix=industry['bls_matrix_code'],
        course_count=str(course_count),
        review_date=date.fromisoformat(meteor['as_of']).strftime('%B %d, %Y').replace(' 0', ' '),
        inventory_date=inventory['checked_at_utc'][:10],
        meteor_window=meteor['window'],
    )
    months = sorted(m['month'] for m in meteor['monthly'])
    values['meteor_months'] = '–'.join(date.fromisoformat(m + '-01').strftime('%b %Y') for m in (months[0], months[-1]))
    for store, count in inventory['source_counts'].items():
        dates = inventory['raw_date_basis_counts'][store]
        posted = dates.get('source_reported_posted_at', 0)
        values.update({f'{store}_records': f'{count:,}', f'{store}_posted': f'{posted:,}', f'{store}_undated': f'{count-posted:,}'})
    source_hash = hashlib.sha256(json.dumps({k: bundle[k] for k in ('meteor', 'benchmarks', 'inventory', 'jobs', 'historical', 'current')}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return {'source_sha256': source_hash, 'method': 'Counts from saved records; BLS industry growth = endpoint ratio minus one; CAGR = ratio to reciprocal years minus one. Occupational forecasts and wages are published source inputs.',
            'industry': {'employment_base': base, 'employment_projected': projected, 'growth_percent': growth, 'annual_growth_percent': annual},
            'values': values}
