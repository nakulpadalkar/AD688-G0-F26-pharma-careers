"""Regression controls for inventory inclusion, provenance and public exports."""
import json
from pathlib import Path
from artifact_io import read_data,TASK
import pyarrow.parquet as pq
from build_inventory import canonical_company,geography,relevance,signals,requirements,identity_keys,safe_url
ROOT=Path(__file__).resolve().parents[1]
def row(**kw):return dict(company_name='AbbVie',countryiso='',location_text='Mettawa, Illinois',apply_url='',source='source-a',external_id='1',title='Commercial Analytics Manager',description='Use claims data to analyze brand performance.',**kw)
assert canonical_company({'company_name':'The Vertex Companies LLC','apply_url':'https://example.com'}) is None
assert canonical_company({'company_name':'Vertex','apply_url':'https://vrtx.wd501.myworkdayjobs.com/job/US/REQ-1'})=='Vertex Pharmaceuticals'
assert canonical_company({'company_name':'Gilead Community Services'}) is None
assert geography(row())[0]
assert not geography({'countryiso':'IN','location_text':'Mettawa, Illinois'})[0]
assert not geography({'location_text':'Hyderabad, Indiana','countryiso':''})[0]
assert not geography({'location_text':'Remote','countryiso':'','title':'US commercial team'})[0]
assert geography({'location_text':'Remote','countryiso':'','apply_url':'https://amgen.wd1.myworkdayjobs.com/careers/job/United-States---Remote/Analyst_R123'})[0]
assert geography({'company_name':'Regeneron','location_text':'Sleepy, Hollow','apply_url':'https://regeneron.wd1.myworkdayjobs.com/careers/job/SLEEPY-HOLLOW/Analyst_R123'})[0]
assert not geography({'company_name':'Other','location_text':'Sleepy, Hollow','apply_url':'https://other.wd1.myworkdayjobs.com/careers/job/SLEEPY-HOLLOW/Analyst_R123'})[0]
assert relevance('Commercial Analytics Manager','Build reports.')[0]
assert relevance('Data Analyst','Analyze medical claims data and MMIT formulary coverage.')[0]
assert not relevance('Senior Receivables Analyst','Analyze commercial data.')[0]
assert relevance('Clinical Data Manager','IQVIA claims data')[0]
assert relevance('Business Analyst','IQVIA is a leading global provider of data and analytics.')[0]
assert not relevance('Receptionist','IQVIA is a leading global provider of data and analytics.')[0]
assert relevance('Biostatistics Director','Design statistical studies.')[0]
assert relevance('Supply Chain Analyst','Plan demand.')[0]
assert relevance('Scientist','Perform statistical analysis using Python.')[0]
assert not relevance('Scientist','Perform laboratory assays.')[0]
assert signals('Working with IQVIA, Symphony, MMIT and claims data is preferred.')==['IQVIA','Symphony','MMIT','Claims data']
assert 'IQVIA' not in signals('IQVIA is a leading provider of data and analytics.')
assert 'Claims data' not in signals('Employee benefits include insurance benefits and claims data services.')
assert not relevance('Commercial Analytics Manager','Absolutely. Using only the text provided, here is a rewrite.')[0]
req=requirements('Qualifications: Bachelor degree and 3 years or Master degree and 2 years; equivalent experience considered.')
assert req['degrees_mentioned']==['Bachelor','Master'] and req['experience_year_mentions']==['2','3'] and req['equivalent_experience_language']
assert requirements('No education information supplied.')['degrees_mentioned']==[]
a=row();b=dict(a,external_id='2',apply_url='https://abbvie.wd1.myworkdayjobs.com/en-US/jobs/job/US/Analyst_R123-1');a['apply_url']='https://abbvie.wd1.myworkdayjobs.com/jobs/job/US/Analyst_R123'
assert set(identity_keys(a,'AbbVie')) & set(identity_keys(b,'AbbVie'))
assert not set(identity_keys(a,'AbbVie')) & set(identity_keys(a,'Amgen'))
assert 'token' not in safe_url('https://example.com/jobs/1?indeed-apply-token=secret&utm_source=a&gh_jid=23')
assert safe_url('javascript:alert(1)')==''
jobs=read_data('database-jobs');s=read_data('inventory-summary')
assert len(jobs)==s['job_count']==sum(c['jobs'] for c in s['companies'])
assert len({j['id'] for j in jobs})==len(jobs)
assert s['identity_groups']==len(jobs)+sum(v for k,v in s['exclusions'].items() if k!='unrelated_or_ambiguous_employer')
assert sum(s['source_counts'].values())==s['canonical_employer_records']+s['exclusions']['unrelated_or_ambiguous_employer']
assert all(j['country']=='US' and j['geography_basis'] and j['stores'] for j in jobs)
for c in s['companies']:
 assert c['jobs']==c['local_jobs']+c['azure_jobs']-c['both_jobs']
 assert c['jobs']==sum(j['company']==c['company'] for j in jobs)
assert all(not any(k in j for k in ['description','html_description_text','password']) for j in jobs)
assert all(safe_url(j['url'])==j['url'] for j in jobs)
assert sum(bool(j['data_signals']) for j in jobs)==s['data_signal_jobs']
raw=read_data('all-employer-records')
assert len(raw)==sum(s['source_counts'].values())
for alias in ['local','azure']:
 table=pq.read_table(TASK/f'raw/{alias}.parquet')
 assert table.num_rows==s['source_counts'][alias]
 assert 'timestamp' in str(table.schema.field('created_at').type)
 for r in table.to_pylist():
  assert r['display_date']==(r['posted_at'] or r['created_at'])
assert all(j['display_on']==(j['posted_on'] or j['first_recorded_on']) for j in jobs)
assert sum(j['date_basis']=='database_created_at_proxy' for j in jobs)==s['undated_jobs']
print('INVENTORY_TESTS_OK: geography, employer identity, negative relevance controls, signal context, source identity, safe URLs and complete count reconciliation')
