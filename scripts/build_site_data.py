"""Bundle checked snapshots and project cached US geography; no network or database."""
import json, math, re
from collections import Counter
from pathlib import Path
from artifact_io import read_data, write_data, TASK
from site_metrics import derive_inventory, derive_metrics
ROOT=Path(__file__).resolve().parents[1]
def read(name): return read_data(name)
def project(lon,lat,code):
    if code=='AK':
        if lon>0: lon-=360
        return 55+(lon+180)*3.2, 345-(lat-50)*3.2
    if code=='HI': return 235+(lon+161)*8, 342-(lat-18)*8
    p1,p2,p0=map(math.radians,[29.5,45.5,37.5]); p=math.radians(lat)
    n=(math.sin(p1)+math.sin(p2))/2; C=math.cos(p1)**2+2*n*math.sin(p1)
    rho=math.sqrt(C-2*n*math.sin(p))/n; r0=math.sqrt(C-2*n*math.sin(p0))/n
    t=n*math.radians(lon+96)
    return 400+rho*math.sin(t)*700,190-(r0-rho*math.cos(t))*700

def map_svg(topo):
    scale=topo['transform']['scale']; shift=topo['transform']['translate']; arcs=[]
    for arc in topo['arcs']:
        x=y=0; coords=[]
        for dx,dy in arc:
            x+=dx;y+=dy;coords.append((x*scale[0]+shift[0],y*scale[1]+shift[1]))
        arcs.append(coords)
    parts=['<svg viewBox="0 0 800 380" role="group" aria-label="US historical commercial candidate choropleth">']
    for g in topo['objects']['subunits']['geometries']:
        code=g['id']; polys=[g['arcs']] if g['type']=='Polygon' else g['arcs']; path=[]
        for poly in polys:
            for ring in poly:
                points=[]
                for a in ring:
                    segment=arcs[a] if a>=0 else list(reversed(arcs[~a]))
                    points.extend(segment if not points else segment[1:])
                coords=[project(x,y,code) for x,y in points]
                path.append('M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in coords)+'Z')
        parts.append(f'<path data-state="{code}" d="{"".join(path)}" tabindex="0" role="button" aria-label="{code}" fill="#edf2fa"><title>{code}</title></path>')
    parts.append('<text class="inset-label" x="95" y="370">ALASKA (INSET)</text><text class="inset-label" x="225" y="370">HAWAII (INSET)</text></svg>')
    return ''.join(parts)

def employer_analysis(jobs):
    scopes={}
    for name, selected in [('us',jobs), ('analytics',[j for j in jobs if j['analytics_relevant']]), ('data',[j for j in jobs if j['data_signals']])]:
        skills=[]
        for skill in sorted({s for j in selected for s in j['skills']}):
            matches=[j for j in selected if skill in j['skills']]
            skills.append({'name':skill,'records':len(matches),'denominator':len(selected),'companies':len({j['company'] for j in matches}),'sources':[{'company':j['company'],'id':j['id'],'url':j['url'],'evidence':'Detected in stored role text; required/preferred status not classified.'} for j in matches]})
        scopes[name]={'records':len(selected),'companies':len({j['company'] for j in selected}),'skills':sorted(skills,key=lambda s:(-s['records'],s['name']))}
    return {'method':'One mention per combined posting identity. Historical database evidence; keywords do not establish mandatory requirements or market prevalence.', 'scopes':scopes}

def build():
    (TASK/'web').mkdir(parents=True,exist_ok=True)
    bundle={'meteor':read('meteor.json'),'benchmarks':read('benchmarks.json'),'current':read('current-jobs.json'),'historical':read('reviewed-examples.json'),'map':map_svg(read('usa_110m.json'))}
    bundle['jobs']=read('database-jobs.json')
    bundle['inventory']=derive_inventory(bundle['jobs'], read('all-employer-records'), read('inventory-summary'))
    write_data('inventory-summary', bundle['inventory'])
    courses=len(re.findall(r'^\| \d+\.', (ROOT/'about.qmd').read_text(encoding='utf-8'), re.M))
    bundle['metrics']=derive_metrics(bundle, courses)
    write_data('site-metrics', bundle['metrics'])
    # JSON is a YAML subset; Quarto resolves these variables during rendering.
    (ROOT/'_variables.yml').write_text(json.dumps(bundle['metrics']['values'], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    b=bundle['benchmarks']
    benchmark_rows=[f"| Occupation | SOC | {b['wage_year']} median annual wage | {b['projection_period']} growth | Average annual projected openings |", '|---|---|---:|---:|---:|']
    benchmark_rows += [f"| [{o['name']}]({o['url']}) | {o['soc']} | ${o['median']:,} | {o['growth']}% | {o['openings']:,} |" for o in b['occupations']]
    (TASK/'web/benchmark-table.md').write_text('\n'.join(benchmark_rows)+'\n',encoding='utf-8')
    write_data('us-jobs',bundle['jobs'])
    bundle['employer_analysis']=employer_analysis(bundle['jobs'])
    write_data('employer-analysis',bundle['employer_analysis'])
    # Focused attachments for native OJS pages; do not load the full jobs bundle.
    for filename, payload in [('outlook-data.json', bundle['benchmarks']), ('skills-data.json', bundle['employer_analysis'])]:
        (TASK/'web'/filename).write_text(json.dumps(payload, ensure_ascii=False)+'\n', encoding='utf-8')
    summary=bundle['inventory']
    rows=['| Employer | Combined US postings | Local | Azure | In both |','|---|---:|---:|---:|---:|']
    rows += [f"| {c['company']} | {c['jobs']} | {c['local_jobs']} | {c['azure_jobs']} | {c['both_jobs']} |" for c in summary['companies']]
    rows += ['', 'Local + Azure − in both = combined postings. Counts include historical and undated records; they are not current vacancy counts. Zero means no eligible records in this extract, not no jobs at that employer.']
    (TASK/'web/inventory-table.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    (TASK/'web/inventory-metric.html').write_text(f"<strong>{summary['employers_with_jobs']}</strong><p>employers with US postings</p><small>{summary['job_count']} combined posting identities</small>",encoding='utf-8')
    dest=TASK/'web/dashboard-data.js';dest.write_text('window.PHARMA_DATA = '+json.dumps(bundle,ensure_ascii=False).replace('</','<\\/')+';\n',encoding='utf-8')
    findings=[f"All US roles are included by default; **{summary['analytics_relevant_jobs']:,}** pass the optional analytics screen and **{summary['other_us_jobs']:,}** do not. A failed rule match is not proof that a role contains no analytical work.", '', f"The snapshot contains **{summary['job_count']} US posting identities across {summary['employers_with_jobs']} employers with matches**, from {summary['source_counts']['local']:,} local and {summary['source_counts']['azure']:,} Azure employer-name-matched rows.", '', f"**{summary['data_signal_jobs']} / {summary['job_count']} ({summary['data_signal_jobs']/summary['job_count']:.1%})** mention a tracked vendor, product or dataset. These mentions connect analytical work to specific data sources. They include required and preferred skills; dataset terms also contribute to the optional analytics-relevance classification.", '', f"{summary['undated_jobs']} postings lack a source-reported date; the display uses a separately labeled database-creation proxy where available.", '', '| Degree term detected | Posting identities |', '|---|---:|']
    findings += [f'| {k} | {v} |' for k,v in summary['education'].items()]
    findings += ['',f"Categories overlap. No degree term was detected in {summary['degree_not_detected']} postings; {summary['equivalent_experience_language']} contain equivalent-experience language. These categories describe the wording of advertisements; eligibility depends on the full qualification requirements.", '', '| Career level from title | Postings | Frequent year expressions (posting counts) |', '|---|---:|---|']
    for level,counts in summary['experience_by_level'].items():
        terms=', '.join(f'{k} years ({v})' for k,v in sorted(counts.items(),key=lambda kv:-kv[1])[:6])
        findings.append(f"| {level} | {sum(j['level']==level for j in bundle['jobs'])} | {terms} |")
    findings += ['', 'Year expressions are not verified minimum requirements; several may occur in one posting for different degree alternatives or specialist experience.']
    findings += ['', '### Analytics-relevance classification', '', '| Classification reason (not an exclusion) | Posting identities |', '|---|---:|']
    findings += [f"| {k.replace('_', ' ')} | {v} |" for k,v in summary['relevance_counts'].items()]
    findings += ['', 'The inventory spans pharmaceutical data careers beyond commercial analytics. Clinical, scientific and operational specialties can require additional training beyond the proposed certificate.']
    (TASK/'web/inventory-findings.md').write_text('\n'.join(findings)+'\n',encoding='utf-8')
    d=bundle['meteor']; total=d['geography']['mapped_records']
    rows=['| Geographic bucket | Records |','|---|---:|']
    rows += [f'| {k.replace("_", " ")} | {v:,} |' for k,v in d['geography']['buckets'].items()]
    rows += ['', '### State evidence table', '', '| State | Records | Share of mapped | Distinct employer/text pairs |', '|---|---:|---:|---:|']
    rows += [f'| {s["name"]} | {s["records"]} | {s["records"]/total*100:.1f}% | {s["distinct_employer_text_hashes"]} |' for s in d['geography']['states']]
    rows += ['', '### Collection activity over time', '', 'Monthly counts describe the historical collection, not employment growth. Changes in source coverage and ingestion can dominate the series. The series therefore describes collection activity.', '', '```{=html}', '<div class="monthly-chart" aria-label="Monthly historical candidate records; exact values in the following table">']
    peak=max(m['records'] for m in d['monthly'])
    rows += [f'<div style="height:{m["records"]/peak*100:.2f}%" title="{m["month"]}: {m["records"]}"></div>' for m in d['monthly']]
    rows += ['</div>', '```', '', '| Month | Screened records |', '|---|---:|']
    rows += [f'| {m["month"]} | {m["records"]} |' for m in d['monthly']]
    (TASK/'web/evidence-tables.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print('BUNDLE_OK')
if __name__=='__main__': build()
