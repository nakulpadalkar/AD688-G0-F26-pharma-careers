from snapshot_io import read_snapshot, write_snapshot
"""US market evidence: Census enterprise sizes plus saved posting identities."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from artifact_io import read_data, artifact_path
from build_boston_market import summarize, commercial
from build_evidence import locate, STATES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/us-market'
BANDS = [('Under 20', ['02','03','04','05']),
         ('20–99', ['06','07','08','09','10','11','12']),
         ('100–499', ['13','14','15','16','17']),
         ('500–999', ['18','19']), ('1,000–4,999', ['31','22','23','24']),
         ('5,000+', ['25'])]

def state(row):
    bucket, code = locate({'location_text': row['location'], 'countryiso': row['country']})
    return code if bucket == 'mapped_state' else 'Unallocated'

def compute(jobs, census):
    by_state = defaultdict(list)
    for row in jobs:
        by_state[state(row)].append(row)
    raw = {r['ENTRSIZE']: r for r in census['rows']}
    bands = [{'band': label, **{key: sum(int(raw[c][key]) for c in codes) for key in ['FIRM','ESTB','EMPL']}}
             for label, codes in BANDS]
    employers = [{'company': name, **summarize([r for r in jobs if r['company'] == name])}
                 for name in sorted({r['company'] for r in jobs})]
    employers.sort(key=lambda r: (-r['commercial'], -r['analytics'], r['company']))
    states = [{'state': code, 'name': STATES.get(code, code), **summarize(by_state[code])}
              for code in sorted(set(STATES) | {'Unallocated'})]
    states.sort(key=lambda r: (-r['commercial'], -r['analytics'], r['name']))
    return {'bands': bands, 'census_total': {k: int(raw['01'][k]) for k in ['FIRM','ESTB','EMPL']},
            'inventory': summarize(jobs), 'employers': employers, 'states': states,
            'commercial_employers': sum(r['commercial'] > 0 for r in employers)}

def build():
    census = read_snapshot((OUT/'data/census-3254.parquet'))
    jobs = read_data('database-jobs.json')
    d = compute(jobs, census)
    d['census_source'] = {k: v for k,v in census.items() if k != 'rows'}
    d['inventory_checked_at'] = read_data('inventory-summary.parquet')['checked_at_utc']
    d['input_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [OUT/'data/census-3254.parquet', artifact_path('database-jobs.json')]}
    web = OUT/'web'; web.mkdir(parents=True, exist_ok=True)
    write_snapshot(web/'summary.parquet',d)
    for name, rows, keys in [('employers',d['employers'],['company','postings','analytics','commercial','missing_posted_date']),
                             ('states',d['states'],['state','name','postings','employers','analytics','commercial','missing_posted_date']),
                             ('company-sizes',d['bands'],['band','FIRM','ESTB','EMPL'])]:
        write_snapshot(web/(name+'.parquet'),[{k:r[k] for k in keys} for r in rows])
    n=d['inventory']; total=d['census_total']
    lines=['## How many companies, and how large?', '',
           f"**{total['FIRM']:,} employer firms** operated **{total['ESTB']:,} pharmaceutical and medicine manufacturing establishments**, employing **{total['EMPL']:,} people** in those establishments in 2022. This is the Census SUSB NAICS 3254 population, not the full biopharma ecosystem or a list of qualified certificate buyers.", '',
           '| Enterprise employment band | Firms | Establishments | Industry employment |', '|---|---:|---:|---:|']
    lines += [f"| {r['band']} | {r['FIRM']:,} | {r['ESTB']:,} | {r['EMPL']:,} |" for r in d['bands']]
    large=sum(r['FIRM'] for r in d['bands'][3:]); mid=d['bands'][2]['FIRM']
    lines += ['',f"A practical account-research starting point is the **{large} firms in enterprises with 500+ employees**, followed by **{mid} in the 100–499 band**. This prioritization is a sales hypothesis, not a finding that those firms have training budgets or commercial-data teams.", '',
              f"Source: [Census 2022 SUSB detailed enterprise sizes]({census['source_url']}) ([release and definitions](https://www.census.gov/data/tables/2022/econ/susb/2022-susb-annual.html)), retrieved {census['retrieved_on']}. Census lists 2022 as its latest SUSB release at review. Counts refer to firms with paid employees; nonemployers are excluded. Enterprise size uses employment across the enterprise, while industry employment counts only establishments classified in NAICS 3254. A firm can operate multiple establishments and span industries. Do not add firm totals across industries or states. Published employment values use Census disclosure protection; the retained source rows preserve its flags.", '',
              '### Broader biopharma context', '',
              'PhRMA’s summary of the newer TEConomy report describes **nearly 1.1 million direct biopharma jobs** in 2024 across the states, DC and Puerto Rico. California, Massachusetts, New Jersey, New York, North Carolina, Pennsylvania and Texas each exceed 50,000 direct jobs. This broader industry definition includes more than manufacturing; it is not comparable to the narrower Census count, and the figures must not be added. [PhRMA / TEConomy summary](https://phrma.org/blog/the-1-74-trillion-sector-powering-america-s-economy).', '',
              'R&D-only biotechs, analytics vendors, CROs and consultancies may also buy training. The manufacturing firm count does not enumerate them. A deduplicated national count of commercially relevant buyers and eligible employees is not yet established.', '',
              '## What our US employability data says', '',
              f"The saved audit dated {d['inventory_checked_at']} contains **{n['postings']:,} US posting identities across {n['employers']} selected employers**. **{n['analytics']:,}** pass the broad analytics screen; **{n['commercial']:,}** pass the narrower commercial-fit screen across **{d['commercial_employers']} employers**. These are historical stored records, not current vacancies, annual hiring or graduate outcomes. This analysis reuses the saved local/Azure inventory; no fresh database pull was made.", '',
              '| Employer | All US postings | Analytics | Commercial fit | Missing posting date |', '|---|---:|---:|---:|---:|']
    lines += [f"| {r['company']} | {r['postings']:,} | {r['analytics']} | {r['commercial']} | {r['missing_posted_date']:,} |" for r in d['employers']]
    lines += ['', 'The table ranks observed commercial-fit evidence. It does not rank national hiring share: employers were selected in advance and collection coverage varies. Named-company US headcounts are not available in this inventory; posting volume is not a company-size measure. Use the Census size distribution for market segmentation and verify each prospect’s team size directly.', '',
              f"**{n['missing_posted_date']:,} records lack a source posting date.** Database-created dates remain collection proxies. Source-reported dates span {n['posted_min']} to {n['posted_max']}; old and undated records remain included. Distinct saved identities can still represent repeated advertisements.", '',
              '### Where to focus outreach', '',
              'The following states have the most commercial-fit records in this selected inventory. Location is the advertised work location, not necessarily headquarters or the training budget owner. Compare with the broader industry hubs above; a weak signal here can reflect poor coverage.', '',
              '| State | All postings | Analytics | Commercial fit | Employers |', '|---|---:|---:|---:|---:|']
    top=[r for r in d['states'] if r['state']!='Unallocated'][:12]
    lines += [f"| {r['name']} | {r['postings']:,} | {r['analytics']} | {r['commercial']} | {r['employers']} |" for r in top]
    u=next(r for r in d['states'] if r['state']=='Unallocated')
    lines += ['',f"**State unallocated: {u['postings']:,} postings, including {u['commercial']} commercial-fit records.** These remain in US totals but are not assigned to a state. The existing parser requires explicit state evidence; city-only, remote, ambiguous and multi-state locations may remain unallocated. State employer counts overlap and must not be summed to get national companies.", '',
              '### Curriculum fit and entry requirements', '',
              '| Skill or dataset term | Commercial-fit postings |', '|---|---:|']
    lines += [f'| {k} | {v} |' for k,v in n['commercial_skills'].items()]
    lines += ['',f"Denominator: {n['commercial']} commercial-fit identities. Terms overlap and mix requirements, preferences and duties. Commercial-fit screening partly uses data terms; these frequencies are not independent estimates of national skill prevalence.", '',
              'Degree mentions: '+', '.join(f'{k} ({v})' for k,v in n['commercial_degrees'].items())+'.', '',
              f"{n['commercial_no_degree_detected']} have no detected degree term; {n['commercial_equivalent_experience']} contain equivalent-experience wording. Neither implies open eligibility. Non-degree describes the credential; employer degree and experience requirements still apply.", '',
              'Career-level labels from titles: '+', '.join(f'{k} ({v})' for k,v in n['commercial_levels'].items())+'.', '',
              'Commercial fit reuses four saved relevance reasons: commercial analytics title, commercial-data duties, data product in a business role, or dataset/product in an analytical role. The broader analytics screen also includes clinical, scientific and operations specialties beyond this curriculum. Review duties individually before making a sales claim.', '',
              '[Employer Parquet](outputs/us-market/web/employers.parquet) · [All states Parquet](outputs/us-market/web/states.parquet) · [Company-size Parquet](outputs/us-market/web/company-sizes.parquet) · [Calculated evidence and hashes](outputs/us-market/web/summary.parquet)']
    (web/'evidence.qmd').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('US_MARKET_BUILT',total,'commercial',n['commercial'],'employers',d['commercial_employers'])

if __name__=='__main__': build()
