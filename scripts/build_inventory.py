"""Build an auditable US pharmaceutical data-careers inventory from private read-only extracts."""
import json,re,hashlib,html
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode,unquote
from build_evidence import locate,FOREIGN,CONFLICT,STATES
from artifact_io import TASK, write_data
import pyarrow.parquet as pq
import pyarrow as pa
ROOT=Path(__file__).resolve().parents[1]
EMPLOYERS={'AbbVie':r'\babbvie\b','Iovance Biotherapeutics':r'\biovance\b','Amgen':r'\bamgen\b','AstraZeneca':r'\bastra\s?zeneca\b','Takeda':r'\btakeda\b','Gilead Sciences':r'\bgilead\b','Regeneron':r'\bregeneron\b','Pfizer':r'\bpfizer\b','Novartis':r'\bnovartis\b','Sanofi':r'\bsanofi\b','Neurocrine Biosciences':r'\bneurocrine\b','Otsuka':r'\botsuka\b','Teva':r'\bteva\b','Vertex Pharmaceuticals':r'\bvertex\b','IQVIA':r'\biqvia\b'}
SIGNALS={'IQVIA':r'\biqvia\b','Symphony':r'\bsymphony(?: health)?\b','MMIT':r'\bmmit\b','Claims data':r'\b(?:claims?[- ](?:data|based|analytic)|(?:medical|pharmacy|healthcare|patient|prescription) claims?)\b','Patient-level data':r'\bpatient[-\s]+level\b|\blongitudinal (?:patient|prescription|healthcare)\b','LAAD / APLD / Xponent':r'\b(?:LAAD|APLD|Xponent)\b'}
TOOLS={'SQL':r'\bSQL\b','Python':r'\bPython\b','R':r'\bR\b(?=\s*[,/)]|\s+(?:programming|and Python|and SAS))','Power BI':r'\bPower\s*BI\b','Tableau':r'\bTableau\b','Excel':r'\bExcel\b','SAS':r'\bSAS\b'}
ROLE=r'analyst|analytics|data\b|insight|forecast|business intelligence|decision scien'
COMMERCIAL=r'commercial|market access|payer|patient services|field (?:planning|force|analytic)|marketing|sales (?:analytic|data)|business analytics|business intelligence|customer insights|forecast'
EXCLUDED=r'financ|account(?:ing|ant|s payable|s receivable)|tax\b|payroll|cyber|security|quality control|\bQC\b|manufactur|supply (?:chain|planning)|procurement|regulatory|clinical|safety|biostat|pharmacom|bioanaly|drug discover|genetic|bioinformat|medical writ|chemistry|research scientist|laboratory|\blab\b|human resources|\bHR\b|corporate affairs|receivables|R&D Study|Process Sciences|cell and gene therapy|medical director|therapeutic strategy|business development|client success|agency partnerships|global account management|director, sales|account manager'
def clean(value):
 s=html.unescape(str(value or ''));s=re.sub(r'<[^>]+>',' ',s);return re.sub(r'\s+',' ',s).strip()
def body(r):
 a=clean(r.get('html_description_text'));return a if len(a)>=200 else clean(r.get('description'))
def canonical_company(r):
 name=r.get('company_name','');url=r.get('apply_url','') or ''
 if re.search(r'gilead community|otsuka (?:icu|brano)',name,re.I):return None
 for c,p in EMPLOYERS.items():
  if re.search(p,name,re.I):
   if c=='Vertex Pharmaceuticals' and not ('pharma' in name.lower() or re.search(r'(?:vrtx|vertexpharma|vertexcareers)',url,re.I)):return None
   return c
 return None
def safe_url(value):
 u=urlsplit(value or '')
 if u.scheme not in ['http','https'] or not u.netloc or u.username or u.password:return ''
 allowed={'gh_jid','jobid','job_id','reqid','requisitionid','id','site_number'}
 query=urlencode([(k,v) for k,v in parse_qsl(u.query) if k.lower() in allowed])
 return urlunsplit((u.scheme,u.netloc,u.path,query,u.fragment if u.fragment.isdigit() else ''))
def geography(r):
 country=(r.get('countryiso') or '').upper().strip();loc=r.get('location_text') or ''
 if CONFLICT.search(loc):return False,'conflicting_location'
 bucket,_=locate(r)
 if bucket=='explicit_non_us':return False,'explicit_non_us'
 if country in ['US','USA']:return True,'country_field'
 if bucket in ['mapped_state','us_unallocated']:return True,'location_text'
 if re.search(r'\bUnited States\b|\bUSA\b',loc,re.I):return True,'location_text'
 path=unquote(urlsplit(r.get('apply_url') or '').path)
 m=re.search(r'/job/([^/]+)/',path,re.I)
 if m:
  segment=m[1]
  if canonical_company(r)=='Regeneron' and segment.upper() in ['TARRYTOWN','SLEEPY-HOLLOW']:
   return True,'employer_location_reference'
  if re.search(r'(?:^|-)US(?:A)?(?:-|$)|United-States',segment,re.I):return True,'ATS_location_segment'
 return False,'unresolved_us_location'
def signals(text):
 found=[]
 for name,pattern in SIGNALS.items():
  for m in re.finditer(pattern,text,re.I):
   context=text[max(0,m.start()-90):min(len(text),m.end()+120)]
   if re.search(r'employee benefits|disability claims|insurance benefits|workers.compensation',context,re.I):continue
   if name=='IQVIA':
    if re.search(r'IQVIA (?:is|was|provides|offers|has|creates|helps)|about IQVIA|join IQVIA|at IQVIA|IQVIA careers',context,re.I):continue
    if not re.search(r'data|syndicat|claims|xponent|LAAD|APLD|MMIT|Symphony|tools|platform',context,re.I):continue
   found.append(name);break
 return found
def commercial_relevance(title,text):
 if re.search(r'Absolutely[.!].{0,30}Using only|as an AI language model|here is (?:a|the) rewritten',text,re.I):return False,'source_text_quality_review'
 if not re.search(ROLE,title,re.I):
  if re.search(r'manager|director|consultant|specialist',title,re.I) and not re.search(EXCLUDED,title,re.I) and signals(text) and re.search(r'analys[ei]|analytics|forecast|insights|data management',text,re.I):return True,'data_product_in_business_role'
  return False,'no_analytics_data_title'
 if re.search(EXCLUDED,title,re.I):return False,'outside_commercial_scope'
 if re.search(r'clinical data management|clinical trial data',text,re.I) and not re.search(COMMERCIAL,title,re.I):return False,'clinical_data_management'
 if re.search(COMMERCIAL,title,re.I):return True,'commercial_analytics_title'
 if signals(text):return True,'data_product_or_dataset_in_role'
 if re.search(r'commercial (?:data|analytics|organization|operations|team)|market access|payer (?:data|analytics)|sales data|brand (?:analytics|performance|strategy)|customer master',text,re.I):return True,'commercial_data_duties'
 return False,'no_commercial_data_evidence'

def relevance(title,text):
 # Vendor language is not a prerequisite for broader pharmaceutical data careers.
 if re.search(r'Absolutely[.!].{0,30}Using only|as an AI language model|here is (?:a|the) rewritten',text,re.I):return False,'source_text_quality_review'
 core,reason=commercial_relevance(title,text)
 if core:return core,reason
 if re.search(r'\bdata\b|analytics|business intelligence|informatics|biostatistic|statistical (?:program|scient)|bioinformatic|decision scien|machine learning|artificial intelligence|\bAI\b|\bepidemiolog|real.world (?:evidence|research)|\bHEOR\b',title,re.I):
  return True,'pharma_data_science_or_informatics_title'
 if re.search(r'analyst|forecast|insights',title,re.I) and not re.search(r'receivables|payable|tax\b|payroll|security|cyber|\bQC\b|quality control|laboratory|\blab\b',title,re.I):
  return True,'pharma_business_or_operations_analytics_title'
 if re.search(r'manager|director|scientist|engineer|specialist|consultant|programmer',title,re.I) and re.search(r'data (?:analytics|analysis|science|engineering|management|governance|integration|warehouse|platform)|statistical (?:analysis|programming)|predictive model|machine learning|business intelligence',text,re.I) and any(re.search(p,text,re.I) for n,p in TOOLS.items() if n!='Excel'):
  return True,'analytical_duties_and_technical_tool'
 return False,reason
def level(title):
 return 'Leadership' if re.search(r'director|\bdir\b|\bAD\b|head\b|vice president|\bVP\b',title,re.I) else 'Manager' if re.search(r'manager|\bmgr\b',title,re.I) else 'Analyst / specialist'
def requirements(text):
 start=re.search(r'qualifications|requirements|education.{0,25}experience|what you.{0,15}(?:bring|need)|about you',text,re.I)
 t=text[start.start():] if start else text
 stop=re.search(r'equal opportunity|compensation range|we offer a comprehensive|employee benefits',t,re.I)
 if stop:t=t[:stop.start()]
 degrees=[]
 for name,p in {'Bachelor':r'bachelor|baccalaureate|\bB\.?S\.?\b|\bB\.?A\.?\b','Master':r'master|\bMBA\b|\bM\.?S\.?\b','Doctorate':r'\bPh\.?D\.?\b|doctorate|doctoral','Associate':r'associate.?s degree','High school':r'high school|\bGED\b'}.items():
  if re.search(p,t,re.I):degrees.append(name)
 years=sorted(set(re.findall(r'\b(\d{1,2}\s*(?:[-–]\s*\d{1,2})?\s*\+?)\s*(?:years|yrs)\b',t,re.I)))
 years=[re.sub(r'\s+','',x).replace('–','-') for x in years if 0<int(re.match(r'\d+',x)[0])<=40]
 equivalent=bool(re.search(r'(?:equivalent|comparable).{0,65}(?:experience|combination)|(?:experience).{0,45}(?:in lieu of|instead of).{0,25}degree',t,re.I))
 return {'degrees_mentioned':degrees,'experience_year_mentions':years,'equivalent_experience_language':equivalent,'qualification_section_found':bool(start)}
def identity_keys(r,company):
 keys=[];source=(r.get('source') or '').lower();ext=str(r.get('external_id') or '')
 if ext:keys.append((company,'source',source,ext))
 url=safe_url(r.get('apply_url'));u=urlsplit(url)
 if url:
  req=re.search(r'[_/](R(?:EQ)?-?\d+)(?:-\d+)?/?$',u.path,re.I)
  if 'myworkdayjobs.com' in u.netloc and req:keys.append((company,'workday',req[1].upper()))
  else:keys.append((company,'url',(u.netloc+u.path).lower().rstrip('/')+'?'+u.query+'#'+u.fragment))
 # Exact text/title/location is used only when there is no usable source identity or URL.
 if not keys:keys=[(company,'text',clean(r.get('title')).lower(),clean(r.get('location_text')).lower(),hashlib.sha256(body(r).encode()).hexdigest())]
 return keys

def build():
 inputs=[]
 for alias in ['local','azure']:
  payload=json.loads((TASK/f'manifests/{alias}.json').read_text(encoding='utf-8'));payload['rows']=pq.read_table(TASK/f'raw/{alias}.parquet').to_pylist();inputs.append(payload)
 records=[];excluded=Counter();raw_by=defaultdict(Counter)
 for payload in inputs:
  assert payload['transaction'][0]=='on'
  for r in payload['rows']:
   company=canonical_company(r)
   if not company:excluded['unrelated_or_ambiguous_employer']+=1;continue
   r['_company']=company;r['_store']=payload['alias'];records.append(r);raw_by[company][payload['alias']]+=1
 parent=list(range(len(records)));keys={}
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,r in enumerate(records):
  for k in identity_keys(r,r['_company']):
   if k in keys:parent[root(i)]=root(keys[k])
   else:keys[k]=i
 groups=defaultdict(list)
 for i,r in enumerate(records):groups[root(i)].append(r)
 jobs=[];review=[]
 for group in groups.values():
  # Prefer local authority with the most complete original text; retain all store provenance.
  group.sort(key=lambda r:(len(body(r))>=200,r['_store']=='local',len(body(r))),reverse=True);r=group[0];company=r['_company']
  us_rows=[(x,geography(x)) for x in group if geography(x)[0]]
  text=body(r);ok,reason=relevance(r['title'],text)
  if not us_rows:excluded['us_unresolved_or_non_us']+=1;review.append({'company':company,'title':r['title'],'reason':geography(r)[1],'location':r.get('location_text'),'url':safe_url(r.get('apply_url'))});continue
  # Explicit foreign evidence conflicts are not silently overridden by another store's US label.
  if any(geography(x)[1] in ['explicit_non_us','conflicting_location'] for x in group):excluded['cross_record_geography_conflict']+=1;continue
  geo,geo_reason=us_rows[0];req=requirements(text);sig=signals(text);tool=[n for n,p in TOOLS.items() if re.search(p,text,re.I)]
  allkeys=sorted(str(k) for x in group for k in identity_keys(x,company));id='db-'+hashlib.sha256('|'.join(allkeys).encode()).hexdigest()[:16]
  urls=list(dict.fromkeys(safe_url(x.get('apply_url')) for x in group if safe_url(x.get('apply_url'))))
  dates=sorted({str(x['posted_at'])[:10] for x in group if x.get('posted_at')})
  created=sorted({str(x['created_at'])[:10] for x in group if x.get('created_at')})
  display_date=dates[-1] if dates else created[0] if created else None
  jobs.append({'id':id,'company':company,'title':r['title'],'location':geo.get('location_text') or 'US location evidenced by source','country':'US','geography_basis':geo_reason[1],'level':level(r['title']),'url':urls[0] if urls else '', 'source_urls':urls,'posted_on':dates[-1] if dates else None,'first_recorded_on':created[0] if created else None,'display_on':display_date,'date_basis':'source_reported_posted_at' if dates else 'database_created_at_proxy' if created else 'unknown','stores':sorted({x['_store'] for x in group}),'source_records':len(group),'sources':sorted({x.get('source','') for x in group}),'status':'Historical database evidence; not live-rechecked','analytics_relevant':bool(ok),'relevance_basis':reason,'data_signals':sig,'skills':tool+sig,'requirements':req,'description_available':bool(text),'text_source':'html_description_text' if len(clean(r.get('html_description_text')))>=200 else 'description','text_hash':hashlib.sha256(text.encode()).hexdigest()})
 jobs.sort(key=lambda j:(j['company'],j['posted_on'] or '',j['title']),reverse=False)
 companies=[]
 for c in EMPLOYERS:
  selected=[j for j in jobs if j['company']==c]
  companies.append({'company':c,'jobs':len(selected),'local_jobs':sum('local' in j['stores'] for j in selected),'azure_jobs':sum('azure' in j['stores'] for j in selected),'both_jobs':sum(len(j['stores'])==2 for j in selected),'raw_records':dict(raw_by[c])})
 summary={'checked_at_utc':max(x['checked_at_utc'] for x in inputs),'scope':'All available dates in met_career_match_jobposting; 15 named employers; All US-evidenced roles; analytics relevance is a selectable classification, not an inclusion condition. Historical and undated records included. No live vacancy claim.','source_counts':{x['alias']:len(x['rows']) for x in inputs},'canonical_employer_records':len(records),'identity_groups':len(groups),'exclusions':dict(excluded),'companies':companies,'job_count':len(jobs),'employers_with_jobs':sum(c['jobs']>0 for c in companies),'undated_jobs':sum(j['posted_on'] is None for j in jobs),'relevance_counts':dict(Counter(j['relevance_basis'] for j in jobs)),'data_signal_jobs':sum(bool(j['data_signals']) for j in jobs),'data_signals':dict(Counter(s for j in jobs for s in j['data_signals'])),'education':dict(Counter(d for j in jobs for d in j['requirements']['degrees_mentioned'])),'degree_not_detected':sum(not j['requirements']['degrees_mentioned'] for j in jobs),'equivalent_experience_language':sum(j['requirements']['equivalent_experience_language'] for j in jobs),'experience_by_level':{l:dict(Counter(y for j in jobs if j['level']==l for y in j['requirements']['experience_year_mentions'])) for l in ['Analyst / specialist','Manager','Leadership']},'limitations':['Rule-screened relevance, not manual validation of every role.','Same source identity or normalized requisition URL joins records; distinct identities without links may remain repeated advertisements.','Qualifications are keyword observations, not validated minimum experience or mandatory degree rules.','No detected degree is not proof that a degree is optional.','Country ambiguity is excluded and quantified; US-team wording alone is not US geography.']}
 summary['analytics_relevant_jobs']=sum(j['analytics_relevant'] for j in jobs)
 summary['other_us_jobs']=sum(not j['analytics_relevant'] for j in jobs)
 summary['date_basis_counts']=dict(Counter(j['date_basis'] for j in jobs))
 summary['raw_date_basis_counts']={p['alias']:dict(Counter('source_reported_posted_at' if r.get('posted_at') else 'database_created_at_proxy' if r.get('created_at') else 'unknown' for r in p['rows'])) for p in inputs}
 write_data('database-jobs',jobs);write_data('inventory-summary',summary)
 raw_public=[]
 for payload in inputs:
  for r in payload['rows']:
   posted=str(r['posted_at'])[:10] if r.get('posted_at') else None;created=str(r['created_at'])[:10] if r.get('created_at') else None
   raw_public.append({'store':payload['alias'],'record_id':r['id'],'company_label':r['company_name'],'canonical_employer':canonical_company(r),'title':r['title'],'location':r.get('location_text'),'country_field':r.get('countryiso'),'posted_on':posted,'first_recorded_on':created,'display_on':posted or created,'date_basis':'source_reported_posted_at' if posted else 'database_created_at_proxy' if created else 'unknown','source':r['source'],'url':safe_url(r.get('apply_url'))})
 write_data('all-employer-records',raw_public)
 (TASK/'reports').mkdir(exist_ok=True)
 pq.write_table(pa.Table.from_pylist(review),TASK/'reports/geography-review.parquet',compression='zstd')
 print(json.dumps({k:summary[k] for k in ['source_counts','identity_groups','exclusions','job_count','employers_with_jobs','undated_jobs','data_signal_jobs','education','equivalent_experience_language','companies']},ensure_ascii=True))
if __name__=='__main__':build()
