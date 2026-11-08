import json,urllib.request,urllib.error,time
from pathlib import Path
from html.parser import HTMLParser
BASE='https://nakulpadalkar.github.io/AD688-G0-F26-pharma-careers/'
OUT=Path(__file__).parent
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.h1=[];self.title='';self.active=None;self.schemas=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
  if tag=='link':self.links.append(a)
  if tag in ['h1','title']:self.active=tag
  if tag=='script' and a.get('type')=='application/ld+json':self.schemas.append(True)
 def handle_data(self,s):
  if self.active=='title':self.title+=s
  if self.active=='h1':self.h1.append(s.strip())
 def handle_endtag(self,tag):
  if tag==self.active:self.active=None
pages=['index','jobs','skills','geography','outlook','boston-market','training-market','us-market','work','about','eda_pharma']
rows=[]
for page in pages:
 url=BASE+page+'.html'
 try:
  with urllib.request.urlopen(url,timeout=30) as r:html=r.read().decode('utf-8');status=r.status
  (OUT/(page+'-live.html')).write_text(html,encoding='utf-8')
  p=Parser();p.feed(html)
  rows.append(dict(page=page,status=status,title=p.title,description=p.meta.get('description'),robots=p.meta.get('robots'),canonical=[x.get('href') for x in p.links if x.get('rel')=='canonical'],h1=p.h1,schema_count=len(p.schemas),og=[x for x in p.meta if x.startswith('og:')],bytes=len(html.encode()),parquet_links=('.parquet"' in html)))
 except Exception as e:rows.append(dict(page=page,error=str(e)))
 time.sleep(1)
discovery=[]
for url in ['https://nakulpadalkar.github.io/robots.txt',BASE+'sitemap.xml',BASE+'robots.txt']:
 try:
  with urllib.request.urlopen(url,timeout=30) as r:discovery.append(dict(url=url,status=r.status,body=r.read().decode('utf-8')[:15000]))
 except Exception as e:discovery.append(dict(url=url,error=str(e)))
(OUT/'seo-evidence.json').write_text(json.dumps(dict(pages=rows,discovery=discovery),indent=2),encoding='utf-8')
assert all(x.get('status')==200 for x in rows),rows
print('SEO_PROBE_OK',json.dumps(rows))
