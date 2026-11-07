from snapshot_io import read_snapshot, write_snapshot
"""Offline, auditable training-prospect screen over the broad local extract."""
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import pyarrow.parquet as pq
from build_inventory import body, clean, geography, identity_keys, relevance, requirements, safe_url, TOOLS, signals, canonical_company
from build_evidence import locate
from build_boston_market import region

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/training-market'
DOMAIN=re.compile(r'pharma|biotech|biopharm|life[- ]scien|clinical research|contract research organi',re.I)
ENTRY=re.compile(r'\b(?:entry[- ]level|early[- ]career|new[- ]grad(?:uate)?|junior|graduate trainee)\b',re.I)
INTERN=re.compile(r'\b(?:intern(?:ship)?|co[- ]?op|apprentice(?:ship)?)\b',re.I)
SENIOR=re.compile(r'\b(?:senior|sr\.?|principal|staff|lead|manager|director|head|vp|vice president|chief)\b',re.I)
YEARS=re.compile(r'\b(\d{1,2})(?:\s*(?:-|–|to)\s*(\d{1,2}))?\s*(\+)?\s*(?:years?|yrs?)\b',re.I)


def experience(text):
    """Only years attached to experience, with age/tenure/benefit exclusions."""
    text=clean(text)
    start=re.search(r'qualifications|requirements|what you.{0,15}(?:bring|need)|education.{0,25}experience',text,re.I)
    if start:text=text[start.start():]
    stop=re.search(r'equal opportunity|employee benefits|compensation range',text,re.I)
    if stop:text=text[:stop.start()]
    result=[]
    for m in YEARS.finditer(text):
        before=text[max(0,m.start()-70):m.start()]
        after=text[m.end():m.end()+100]
        if re.match(r'\s*(?:of age|old\b|or older|of company|in business)',after,re.I):continue
        if re.search(r'\b(?:founded|established|for over|for more than|company has|history of)\b',before,re.I):continue
        tail=re.split(r'[.;!?]',after,maxsplit=1)[0]
        direct_after=bool(re.search(r'\bexperience\b',tail[:80],re.I))
        direct_before=bool(re.search(r'\bexperience\s*(?:of|:|is|at least|minimum|a minimum of|for)?\s*$',before,re.I))
        if not (direct_after or direct_before):continue
        lo,hi=int(m[1]),int(m[2] or m[1])
        if not 0<=lo<=hi<=40:continue
        result.append({'minimum':lo,'maximum_mentioned':hi,'open_ended':bool(m[3]),
                       'evidence':text[max(0,m.start()-55):min(len(text),m.end()+100)]})
    return result


def career(title, exp):
    # These are screening buckets, not verified eligibility or employee headcounts.
    if INTERN.search(title):return 'Internship / student pathway'
    if SENIOR.search(title):return 'Senior / supervisory title'
    if ENTRY.search(title):return 'Explicit early-career title'
    if not exp:return 'Experience unclear'
    if all(x['minimum']<=3 and x['maximum_mentioned']<=3 for x in exp):return '0–3-year experience signal; review required'
    if any(x['minimum']<=3 for x in exp):return 'Mixed experience alternatives; review required'
    return '4+ years experience signal'


def employer_key(row):
    # Deliberately avoid fuzzy corporate-family merging or grouping on industry codes.
    return re.sub(r'\s+',' ',(row.get('company_name') or '').strip()).casefold() or f"unknown:{row['id']}"


def domain_basis(row):
    if DOMAIN.search((row.get('company_name') or '')+' '+(row.get('company_description') or '')):
        return 'Employer-text signal'
    if any(re.match(r'^(3254|541714)',row.get(k) or '') for k in ['naics_code','company_naics_code']):
        return 'Industry-code signal (unvalidated)'
    return 'Posting-text signal only'


def refine_candidates(rows):
    """Apply review controls to saved evidence; never upgrade unknown geography."""
    references=read_snapshot((ROOT/'outputs/boston-market/data/employers.parquet'))
    normalize=lambda name: re.sub(r'[^a-z0-9]','',name.lower())
    names={normalize(e['company']) for e in references}
    names.update(normalize(e.get('inventory_company') or '') for e in references)
    names.discard('')
    for row in rows:
        if canonical_company({'company_name':row['company'],'apply_url':row['url']}) or normalize(row['company']) in names:
            row['domain_basis']='Named employer reference'
        path=urlsplit(row['url']).path
        foreign=re.search(r'(?:^|[-/])(ISR|IND|GBR|CAN|DEU|FRA|IRL|CHN|JPN|AUS|CHE|SWE|DNK|ESP|ITA|POL|NLD|SGP|NZL|MEX|BRA)(?:[-/]|$)',path)
        corrupt_city=re.search(r'\b(?:Hyderabad|Karnataka|Bangalore|Bengaluru|Gurgaon|Gurugram|Mumbai|Maharashtra|Chennai|Tamil Nadu|Telangana|Pune|Noida|New Delhi|Ahmedabad)\b',row['location']+' '+path,re.I)
        if (foreign or corrupt_city) and row['us']:
            row['us']=False;row['geography_basis']='Country conflict with recruiting URL'
        # Product or claims mentions alone do not establish an analytical job.
        title=row['title']
        excluded=re.search(r'data[- ]entry|pharmacy technician|habi[l]?itation specialist|health services specialist|finance|financial|treasury|payroll|receivables|tax analyst|accounting',title,re.I)
        analytical_title=re.search(r'analyst|analytics|data\b|statistic|informatic|forecast|insight|machine learning|artificial intelligence|\bAI\b|epidemiolog|\bHEOR\b|real.world (?:evidence|research)',title,re.I)
        if row['analytics'] and (excluded or not analytical_title):
            row['analytics']=False;row['commercial_fit']=False
            row['analytics_basis']='Broader match withheld: title needs role-level review'
    return rows


def summarize(rows):
    return {'postings':len(rows),'employer_labels':len({r['employer_key'] for r in rows if not r['employer_key'].startswith('unknown:')}),
            'analytics':sum(r['analytics'] for r in rows),'undated':sum(not r['posted_on'] for r in rows),
            'career':dict(Counter(r['career'] for r in rows if r['analytics'])),
            'domain_basis':dict(Counter(r['domain_basis'] for r in rows)),
            'freshness':dict(Counter(r['freshness'] for r in rows))}


def write_table_snapshot(path, rows, fields):
    write_snapshot(path, [{k:r.get(k) for k in fields} for r in rows])


def build():
    receipt=json.loads((OUT/'receipt.json').read_text())
    now=datetime.fromisoformat(receipt['completed_at_utc'])
    rows=[];parent=[];keys={};raw_ids={};raw_geo=Counter();raw_status=Counter()
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def join(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    source=OUT/'raw/local-candidates.parquet'
    with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==receipt['raw_sha256']
    for batch in pq.ParquetFile(source).iter_batches(batch_size=2000):
        for raw in batch.to_pylist():
            key=employer_key(raw);text=body(raw)
            # Prefer original qualifications; enriched summaries are identified fallback evidence.
            exp=experience(text)
            evidence_source='Original posting text'
            if not text and raw.get('requirements_summary'):
                exp=experience(raw['requirements_summary']);evidence_source='Enriched requirements summary'
            analytics,reason=relevance(raw.get('title') or '',text)
            exp_bucket=career(raw.get('title') or '',exp)
            us,geo=geography(raw);state_bucket,state=locate(raw)
            raw_geo[geo]+=1;raw_status[raw.get('enrichment_status') or 'missing']+=1
            fresh='Availability unknown'
            if raw.get('alive')=='False':fresh='Last check reported unavailable'
            elif raw.get('alive')=='True' and raw.get('alive_checked_at') and raw.get('alive_valid_until'):
                try:
                    if datetime.fromisoformat(raw['alive_valid_until'])>=now:fresh='Live check within stored validity'
                    else:fresh='Live check expired'
                except ValueError:pass
            record={'id':raw['id'],'employer_key':key,'company':clean(raw.get('company_name')) or 'Unknown employer',
                    'title':clean(raw.get('title')),'location':clean(raw.get('location_text')),'us':us,'geography_basis':geo,
                    'explicit_non_us':geo=='explicit_non_us','state':state or '',
                    'domain_basis':domain_basis(raw),'analytics':analytics,'analytics_basis':reason,'commercial_fit':analytics and reason in {'commercial_analytics_title','commercial_data_duties','data_product_in_business_role','data_product_or_dataset_in_role'},'career':exp_bucket,
                    'experience_evidence':exp,'qualification_source':evidence_source,
                    'degrees':requirements(text or raw.get('requirements_summary') or '')['degrees_mentioned'],
                    'skills':[k for k,p in TOOLS.items() if re.search(p,text,re.I)]+signals(text),
                    'posted_on':(raw.get('posted_at') or '')[:10],'pulled_on':(raw.get('created_at') or '')[:10],
                    'freshness':fresh,'url':safe_url(raw.get('apply_url')),'staffing':raw.get('is_staffing_agency')=='True',
                    'duplicate_of':raw.get('duplicate_of_id'),'raw_records':1,'enrichment_status':raw.get('enrichment_status') or 'missing'}
            i=len(rows);parent.append(i);rows.append(record);raw_ids[raw['id']]=i
            for identity in identity_keys(raw,key):
                # A shared careers homepage is not a requisition identity.
                if identity[1]=='url':
                    url=urlsplit(safe_url(raw.get('apply_url')))
                    if not re.search(r'\d',url.path+url.query):continue
                if identity in keys:join(i,keys[identity])
                else:keys[identity]=i
        if len(rows)%20000==0:print(json.dumps({'processed_candidate_rows':len(rows)}),flush=True)
    assert len(rows)==receipt['candidate_records']
    for i,row in enumerate(rows):
        other=raw_ids.get(row['duplicate_of'])
        if other is not None and rows[other]['employer_key']==row['employer_key']:join(i,other)
    groups=defaultdict(list)
    for i in range(len(rows)):groups[find(i)].append(rows[i])
    combined=[]
    for group in groups.values():
        # Choose an actual record; do not synthesize qualifications across advertisements.
        r=dict(max(group,key=lambda x:(x['us'],len(x['experience_evidence']),bool(x['posted_on']),int(x['id']))))
        r['raw_records']=len(group)
        conflict=any(x['us'] for x in group) and any(x['explicit_non_us'] for x in group)
        r['us']=any(x['us'] for x in group) and not conflict
        if conflict:r['geography_basis']='Cross-record country conflict'
        states={x['state'] for x in group if x['state']}
        r['state']=next(iter(states)) if len(states)==1 else ''
        r['posted_on']=max((x['posted_on'] for x in group if x['posted_on']),default='')
        r['pulled_on']=min((x['pulled_on'] for x in group if x['pulled_on']),default='')
        # Conflicting freshness observations do not establish a current vacancy.
        if len({x['freshness'] for x in group})>1:r['freshness']='Availability unknown'
        combined.append(r)
    publish(combined,receipt,dict(raw_geo),dict(raw_status))


def publish(combined,receipt,raw_geo,raw_status):
    combined=refine_candidates(combined)
    raw_count=sum(r['raw_records'] for r in combined)
    snapshot_date=datetime.fromisoformat(receipt['completed_at_utc']).date()
    recent_from=(snapshot_date-timedelta(days=120)).isoformat()
    for r in combined:
        r['posted_last_120_days']=bool(r['posted_on'] and recent_from<=r['posted_on']<=snapshot_date.isoformat())
        r['posting_date_future']=bool(r['posted_on'] and r['posted_on']>snapshot_date.isoformat())
    us=[r for r in combined if r['us']];analytics=[r for r in us if r['analytics']]
    employer_rows=[]
    early={'Explicit early-career title','0–3-year experience signal; review required'}
    by_company=defaultdict(list)
    for r in us:by_company[r['employer_key']].append(r)
    for company_key,company in sorted(by_company.items()):
        if company_key.startswith('unknown:'):continue
        a=[r for r in company if r['analytics']]
        if not a:continue
        candidates=[r for r in a if r['career'] in early]
        employer_rows.append({'company':company[0]['company'],'us_postings':len(company),'analytics':len(a),
                             'early_career_review':len(candidates),'commercial_analytics':sum(r['commercial_fit'] for r in a),'recent_analytics':sum(r['posted_last_120_days'] for r in a),'recent_early_review':sum(r['posted_last_120_days'] for r in candidates),'early_commercial_review':sum(r['commercial_fit'] for r in candidates),'recent_early_commercial_review':sum(r['commercial_fit'] and r['posted_last_120_days'] for r in candidates),'internships':sum(r['career']=='Internship / student pathway' for r in a),
                             'unclear_experience':sum(r['career']=='Experience unclear' for r in a),
                             'domain_evidence':'; '.join(sorted({r['domain_basis'] for r in a})),
                             'staffing_flag':any(r['staffing'] for r in company),
                             'states':', '.join(sorted({r['state'] for r in a if r['state']})),
                             'skills':'; '.join(f'{s} ({n})' for s,n in Counter(s for r in candidates for s in set(r['skills'])).most_common(8)),
                             'missing_posted_date':sum(not r['posted_on'] for r in a),
                             'latest_posted':max((r['posted_on'] for r in a),default=''),
                             'latest_pull_proxy':max((r['pulled_on'] for r in a),default=''),
                             'live_check_in_validity':sum(r['freshness']=='Live check within stored validity' for r in a),
                             'example_url':next((r['url'] for r in candidates if r['url']),a[0]['url'])})
    employer_rows.sort(key=lambda r:(-r['recent_early_commercial_review'],-r['recent_early_review'],-r['early_commercial_review'],-r['early_career_review'],-r['analytics'],r['company']))
    result={'receipt':receipt,'raw_geography':dict(raw_geo),'raw_enrichment_status':dict(raw_status),
            'recent_posted_from':recent_from,
            'recent_analytics':sum(r['posted_last_120_days'] for r in analytics),
            'future_posting_dates':sum(r['posting_date_future'] for r in analytics),
            'regional_analytics':dict(Counter(region({'location':r['location'],'country':'US'}) for r in analytics)),
            'analytics_commercial_fit':sum(r['commercial_fit'] for r in analytics),
            'early_commercial_review':sum(r['commercial_fit'] and r['career'] in early for r in analytics),
            'combined':summarize(combined),'us':summarize(us),'non_us_or_unresolved':len(combined)-len(us),
            'source_rows_collapsed':raw_count-len(combined),'analytics_employer_labels':len(employer_rows),'analytics_unknown_employer_postings':sum(r['employer_key'].startswith('unknown:') for r in analytics),
            'states':dict(Counter(r['state'] or 'US state unresolved' for r in analytics)),
            'posted_months':dict(sorted(Counter(r['posted_on'][:7] for r in analytics if r['posted_on']).items())),
            'pull_months_undated':dict(sorted(Counter(r['pulled_on'][:7] or 'Unknown' for r in analytics if not r['posted_on']).items()))}
    web=OUT/'web';web.mkdir(parents=True,exist_ok=True)
    write_snapshot(web/'summary.parquet',result)
    (OUT/'processed').mkdir(exist_ok=True)
    # Sanitized posting evidence is reproducible locally; only focused Parquet datasets are published.
    write_snapshot(OUT/'processed/postings.parquet',combined)
    write_table_snapshot(web/'employer-prospects.parquet',employer_rows,list(employer_rows[0]) if employer_rows else ['company'])
    example_fields=['id','company','title','location','state','domain_basis','commercial_fit','career','experience_mentions','degrees','skills','posted_on','posted_last_120_days','posting_date_future','pulled_on','freshness','url','raw_records']
    export=[]
    for r in analytics:
        export.append({**r,'experience_mentions':r['experience_evidence']})
    write_table_snapshot(web/'analytics-postings.parquet',export,example_fields)
    def esc(value):return html.escape(str(value)).replace('|','&#124;').replace('\n',' ')
    lines=[f"Snapshot extracted **{receipt['completed_at_utc'][:10]} UTC** from local PostgreSQL. All available dates were scanned, including missing posting dates.", '',
           '| Processing stage | Records |','|---|---:|',
           f"| Entire local posting table, all industries | {receipt['database_records']:,} |",
           f"| Broad pharma / biotech / life-sciences candidate records | {raw_count:,} |",
           f"| Combined candidate posting identities | {len(combined):,} |",
           f"| US-evidenced identities | {len(us):,} |",
           f"| Non-US, unresolved or conflicting country | {len(combined)-len(us):,} |",
           f"| US analytics-rule matches | {len(analytics):,} |",
           f"| Employer labels with US analytics matches | {len(employer_rows):,} |",
           f"| US commercial-data rule matches | {result['analytics_commercial_fit']:,} |",
           f"| Commercial-data matches with early-career review signals | {result['early_commercial_review']:,} |",'',
           'These counts cover matching records across employers, not a census of pharmaceutical companies. A posting can mention a pharmaceutical client while its employer belongs to another industry. Employer-text and industry-code signals are screening evidence, not independent industry verification.', '',
           f"Of the US analytics matches, **{result['recent_analytics']:,}** have source posting dates within 120 days of extraction; **{sum(not r['posted_on'] for r in analytics):,}** have no posting date and remain included. **{result['future_posting_dates']:,}** have dates later than extraction and are excluded from the recent-date measure. Dates do not verify that a role is still open.", '', '## Career-stage evidence', '', '| Analytics posting bucket | Identities |','|---|---:|']
    lines += [f'| {esc(k)} | {v:,} |' for k,v in result['us']['career'].items()]
    lines += ['', 'The 0–3-year bucket identifies advertisements for review; it does not establish eligibility. Degree alternatives, specialist requirements and postgraduate study can change suitability. Internships are separate from employee-upskilling prospects. Missing experience evidence stays unknown. Age requirements such as “18 years or older” are excluded.', '',
              '## Employer outreach shortlist', '', 'Ranked first by early-career commercial-data candidates with posting dates in the last 120 days, then other recent early-career signals and historical evidence. Commercial fit uses the existing commercial title/duty/data-product rules; other analytics roles can require a different curriculum. This table prioritizes named employer references and employer-text signals. Stored staffing flags are shown in the download for review; they are not verified exclusions. Other candidates remain in the download for review. Counts are historical demand signals, not training seats or verified vacancies.', '',
              '| Employer | US analytics | Early-career review | Commercial early-career | Student pathways | Unclear experience | Skills in early-career candidates |', '|---|---:|---:|---:|---:|---:|---|']
    shortlist=[r for r in employer_rows if any(b in r['domain_evidence'] for b in ('Named employer reference','Employer-text signal')) and r['early_career_review']]
    lines += [f"| {esc(r['company'])} | {r['analytics']:,} | {r['early_career_review']:,} | {r['early_commercial_review']:,} | {r['internships']:,} | {r['unclear_experience']:,} | {esc(r['skills'])} |" for r in shortlist[:40]]
    lines += ['', '## Inspect candidate advertisements', '', 'Examples below have a named employer reference or employer-text signal and an early-career review classification. Source URLs are stored evidence; this analysis did not recheck employer websites.', '', '| Employer / role | Career evidence | Degree mentions | Date basis | Source |', '|---|---|---|---|---|']
    examples=[];seen=set()
    for r in sorted(analytics,key=lambda r:(r['career']!='Explicit early-career title',r['company'],r['title'])):
        if r['career'] not in early or r['domain_basis'] not in ('Named employer reference','Employer-text signal') or r['company'].casefold() in seen:continue
        seen.add(r['company'].casefold());examples.append(r)
        if len(examples)==12:break
    for r in examples:
        date_label='Posted '+r['posted_on'] if r['posted_on'] else f'<span class="job-pull-date">Pulled {esc(r["pulled_on"] or "unknown")}</span>'
        evidence='; '.join(e['evidence'] for e in r['experience_evidence'][:2]) or r['career']
        lines.append(f"| {esc(r['company'])}: {esc(r['title'])} | {esc(evidence)} | {esc(', '.join(r['degrees']) or 'Not detected')} | {date_label} | "+(f"[Source]({r['url']})" if r['url'] else 'No stored URL')+' |')
    lines += ['', '## Geography and collection dates', '', '| State evidence | US analytics identities |', '|---|---:|']
    lines += [f'| {esc(k)} | {v:,} |' for k,v in sorted(result['states'].items(),key=lambda x:-x[1])]
    lines += ['', '<details>', '<summary>Expand monthly posting and pull-date evidence</summary>', '', '### Source-reported posting months', '', 'This series measures records in the collection, not hiring growth. Missing posting dates are never substituted into this series.', '', '| Month | Analytics identities |', '|---|---:|']
    lines += [f'| {esc(k)} | {v:,} |' for k,v in result['posted_months'].items()]
    lines += ['', '### Pull months for records without posting dates', '', '| Database-created month (proxy) | Analytics identities |', '|---|---:|']
    lines += [f'| {esc(k)} | {v:,} |' for k,v in result['pull_months_undated'].items()]
    lines += ['', '</details>', '', '## Availability evidence', '', '| Stored status at extraction | US candidate identities |', '|---|---:|']
    lines += [f'| {esc(k)} | {v:,} |' for k,v in result['us']['freshness'].items()]
    lines += ['', '## Screening and reconciliation', '', '| Domain signal | All combined candidates |', '|---|---:|']
    lines += [f'| {esc(k)} | {v:,} |' for k,v in result['combined']['domain_basis'].items()]
    lines += ['', '### Raw candidate enrichment coverage', '', '| Stored enrichment status | Source records |', '|---|---:|']
    lines += [f'| {esc(k)} | {v:,} |' for k,v in result['raw_enrichment_status'].items()]
    lines += ['', 'Enrichment status describes pipeline processing, not independently verified correctness.', '', f"Combined {raw_count:,} source rows into {len(combined):,} posting identities using source IDs, normalized requisition URLs and same-employer database duplicate links. This prospect screen requires an analytical title; duty-only matches, pharmacy data-entry and non-analytical support titles are withheld for manual review; explicit foreign recruiting-country codes override contradictory US evidence. Named employer references use the existing reviewed inventory and MassBio shortlist. Employer names are whitespace/case normalized only; subsidiaries, spelling variants and unnamed employers may remain separate. A shared title alone does not join advertisements. Conflicting US/non-US evidence is withheld from the US subset.", '',
              'Industry-code enrichments are unvalidated and do not establish company membership. Original descriptions drive analytics and skill screening; enriched qualification summaries are used only when original text is absent. This is a reproducible rules-based screen; individual matches require review before outreach or eligibility decisions.', '',
              '[Download all employer prospects](outputs/training-market/web/employer-prospects.parquet) · [Download US analytics posting evidence](outputs/training-market/web/analytics-postings.parquet) · [Saved calculations and extraction receipt](outputs/training-market/web/summary.parquet)']
    (web/'evidence.qmd').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'TRAINING_BUILD_OK':True,'raw':raw_count,'combined':len(combined),'us':len(us),'analytics':len(analytics),'analytics_employer_labels':len(employer_rows),'analytics_unknown_employer_postings':sum(r['employer_key'].startswith('unknown:') for r in analytics),'career':result['us']['career']}),flush=True)


if __name__=='__main__':
    import sys
    if '--refresh-derived' in sys.argv:
        saved=read_snapshot((OUT/'web/summary.parquet'))
        combined=read_snapshot((OUT/'processed/postings.parquet'))
        publish(combined,saved['receipt'],saved['raw_geography'],saved['raw_enrichment_status'])
    else:build()
