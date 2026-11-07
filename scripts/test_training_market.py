from snapshot_io import read_snapshot, write_snapshot
"""Negative controls and reconciliation for the local employer prospect screen."""
import json
from pathlib import Path
from collections import Counter
from build_training_market import experience, career, domain_basis, employer_key, summarize, refine_candidates

assert experience('Applicants must be 18 years or older.')==[]
assert experience('Our company has over 20 years of experience in pharma.')==[]
assert experience('Qualifications: 2 years of SQL experience.')[0]['minimum']==2
assert experience('Requirements: 0-3 years of relevant experience.')[0]['maximum_mentioned']==3
assert experience('Applicants need 2 to 3 years of work experience.')[0]['maximum_mentioned']==3
assert career('Data Analyst',experience('2 years of SQL experience'))=='0–3-year experience signal; review required'
assert career('Data Analyst',experience('Bachelor: 5 years of experience. Master: 2 years of experience.'))=='Mixed experience alternatives; review required'
assert career('Senior Data Analyst',experience('2 years of experience'))=='Senior / supervisory title'
assert career('Data Engineer Intern',experience('18 years or older'))=='Internship / student pathway'
assert career('Data Analyst',[])=='Experience unclear'
assert career('Junior Data Analyst',[])=='Explicit early-career title'
assert domain_basis({'company_name':'Biotech Labs'})=='Employer-text signal'
assert domain_basis({'company_name':'Example','naics_code':'325412'})=='Industry-code signal (unvalidated)'
assert domain_basis({'company_name':'Example'})=='Posting-text signal only'
assert employer_key({'company_name':' Example  Inc ','id':'1'})==employer_key({'company_name':'example inc','id':'2'})
assert employer_key({'company_name':'Example Inc','id':'1'})!=employer_key({'company_name':'Example LLC','id':'2'})

base={'company':'Example','title':'Data Analyst','url':'https://example.com/job/Hyderabad---TS---IN/Analyst-123','us':True,'analytics':True,'analytics_basis':'pharma_data_science_or_informatics_title','commercial_fit':False,'location':'Hyderabad Ts, Indiana','domain_basis':'Posting-text signal only'}
assert not refine_candidates([dict(base)])[0]['us']
assert refine_candidates([{**base,'url':'https://example.com/job/US-Indianapolis-IN/Analyst-123','location':'Indianapolis, Indiana'}])[0]['us']
assert not refine_candidates([{**base,'title':'Data Entry Pharmacy Technician'}])[0]['analytics']

OUT=Path(__file__).resolve().parents[1]/'outputs/training-market'
if (OUT/'web/summary.parquet').exists():
    summary=read_snapshot((OUT/'web/summary.parquet'))
    jobs=read_snapshot((OUT/'processed/postings.parquet'))
    us=[j for j in jobs if j['us']]
    analytics=[j for j in us if j['analytics']]
    assert summarize(jobs)==summary['combined']
    assert summarize(us)==summary['us']
    assert sum(j['raw_records'] for j in jobs)==summary['receipt']['candidate_records']
    assert len(jobs)+summary['source_rows_collapsed']==summary['receipt']['candidate_records']
    assert len(us)+summary['non_us_or_unresolved']==len(jobs)
    assert sum(summary['us']['career'].values())==len(analytics)
    assert sum(summary['posted_months'].values())+sum(summary['pull_months_undated'].values())==len(analytics)
    assert sum(summary['states'].values())==len(analytics)
    assert all(not j['us'] for j in jobs if j['geography_basis']=='Cross-record country conflict')
    assert len({j['id'] for j in jobs})==len(jobs)
    assert len(read_snapshot(OUT/'web/analytics-postings.parquet'))==len(analytics)
    employers=read_snapshot(OUT/'web/employer-prospects.parquet')
    assert len(employers)==summary['analytics_employer_labels']
    assert sum(int(r['analytics']) for r in employers)+summary['analytics_unknown_employer_postings']==len(analytics)
    assert summary['receipt']['transaction_read_only'] is True
    print('TRAINING_MARKET_OK: age/tenure exclusions, career controls, duplicates, geography, date series, employer and export reconciliation')
else:
    print('TRAINING_UNIT_OK: screening controls passed; full data reconciliation awaits extraction')
