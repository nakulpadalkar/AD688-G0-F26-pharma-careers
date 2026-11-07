from snapshot_io import read_snapshot, write_snapshot
"""Offline visual bundle; exact FIPS joins and explicit observation quality."""
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from artifact_io import read_data
from build_site_data import map_svg, project

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/market-visuals'
TERRITORIES={'60','66','69','72','78'}

def value(row):
    if row.get('in_universe') is False: return None,'outside_universe'
    try: v=float(row.get('share_employed'))
    except (ValueError,TypeError): return None,'missing'
    if not math.isfinite(v) or not 0<=v<=1: return None,'missing'
    quality=str(row.get('share_employed_quality') or '').lower()
    return v*100,'low_quality' if quality in {'weak','marginal','2','3'} else 'available'

def path_for(feature):
    geometry=feature['geometry'];state=feature['geoid'][:2]
    code={'02':'AK','15':'HI'}.get(state,'US')
    polygons=[geometry['coordinates']] if geometry['type']=='Polygon' else geometry['coordinates']
    paths=[];all_points=[]
    for poly in polygons:
        for ring in poly:
            points=[]
            for lon,lat,*_ in ring:
                xy=tuple(round(c,2) for c in project(lon,lat,code))
                if not points or points[-1]!=xy:points.append(xy)
            if len(points)>2:
                paths.append('M'+'L'.join(f'{x},{y}' for x,y in points)+'Z');all_points+=points
    return ''.join(paths),[min(p[0] for p in all_points),min(p[1] for p in all_points),max(p[0] for p in all_points),max(p[1] for p in all_points)]

def build():
    source=read_snapshot((OUT/'data/urban-counties.parquet'))
    boundaries=read_snapshot((OUT/'data/county-boundaries.parquet'))
    rows={r['geoid']:r for r in source['rows']};assert len(rows)==len(source['rows'])
    counties=[];boundary_ids=set()
    for feature in boundaries:
        g=feature['geoid']
        if g[:2] in TERRITORIES:continue
        boundary_ids.add(g);r=rows.get(g,{})
        percent,status=value(r);path,bbox=path_for(feature)
        bounds=[]
        for key in ['share_employed_lb','share_employed_ub']:
            try:v=float(r.get(key));bounds.append(v*100 if math.isfinite(v) and 0<=v<=1 else None)
            except (ValueError,TypeError):bounds.append(None)
        counties.append({'geoid':g,'name':r.get('name',feature['name']),'state_name':r.get('state_name',''),
                         'value':percent,'status':status,'quality':r.get('share_employed_quality'),
                         'lower':bounds[0],'upper':bounds[1],'path':path,'bbox':bbox})
    meta={k:v for k,v in source.items() if k not in ['rows','coverage_by_year']}
    meta.update(mapped=sum(c['value'] is not None for c in counties),boundary_count=len(counties),
                unmatched=sorted(set(rows)-boundary_ids-TERRITORIES),
                unmatched_geoids=[g for g in rows if g not in boundary_ids and g[:2] not in TERRITORIES],
                excluded_territories=[g for g in rows if g[:2] in TERRITORIES],
                statuses=dict(Counter(c['status'] for c in counties)))
    meta.pop('unmatched')
    us=read_snapshot((ROOT/'outputs/us-market/web/summary.parquet'))
    boston=read_snapshot((ROOT/'outputs/boston-market/web/market-summary.parquet'))
    payload={'us':us,'boston':boston,'county_meta':meta,'counties':counties,'state_svg':map_svg(read_data('usa_110m.json'))}
    web=OUT/'web';web.mkdir(parents=True,exist_ok=True)
    # Headings in a raw details block can close the surrounding Quarto section.
    # Bold subheads keep the evidence inside one accessible disclosure.
    for label,path in [('us','outputs/us-market/web/evidence.qmd'),('boston','outputs/boston-market/web/evidence.qmd')]:
        evidence=(ROOT/path).read_text(encoding='utf-8')
        (web/f'{label}-evidence.qmd').write_text(re.sub(r'^#+ (.+)$',r'**\1**',evidence,flags=re.M),encoding='utf-8')
    (web/'visual-data.js').write_text('window.MARKET_VISUALS = '+json.dumps(payload,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+';\n',encoding='utf-8')
    keys=['geoid','name','state_name','value','status','quality','lower','upper']
    write_snapshot(web/'county-employment.parquet',[{k:r.get(k) for k in keys} for r in counties])
    receipt={'county':meta,'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'data/urban-counties.parquet',OUT/'data/county-boundaries.parquet',ROOT/'outputs/us-market/web/summary.parquet',ROOT/'outputs/boston-market/web/market-summary.parquet']}}
    write_snapshot(web/'provenance.parquet',receipt)
    print('MARKET_VISUALS_BUILT',json.dumps({k:meta[k] for k in ['year','mapped','boundary_count','statuses','unmatched_geoids']}))

if __name__=='__main__':build()
