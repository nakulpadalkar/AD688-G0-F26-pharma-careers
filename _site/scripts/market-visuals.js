/* Offline, accessible visual exploration of saved public evidence. */
(() => {
  const D=window.MARKET_VISUALS, root=document.querySelector('.market-visuals');
  if(!D||!root)return;
  const $=id=>document.getElementById(id), num=n=>Number(n).toLocaleString('en-US'), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const boston=document.body.dataset.market==='boston', current=boston?D.boston.local:D.us.inventory;
  const colors=['#e4edfc','#bad1ef','#7eace0','#467fc4','#235eb5','#102c60'];
  let selectedState=null,selectedCounty=null;
  const stateNames=new Map(); D.counties.forEach(c=>{if(c.state_name)stateNames.set(c.geoid.slice(0,2),c.state_name);});
  const cards=boston?[[num(D.boston.context.boston_member_companies_2026+D.boston.context.cambridge_member_companies_2026),'Boston / Cambridge members','Life-sciences companies · 2026'],[num(D.boston.shortlist_employees),'MA employees in 20 firms','Selected major employers · 2026'],[num(current.commercial),'Local commercial-fit postings','Historical inventory · core + suburbs']]:[[num(D.us.census_total.FIRM),'Manufacturing employer firms','Census SUSB · 2022'],[num(D.us.bands.slice(3).reduce((s,r)=>s+r.FIRM,0)),'Firms in 500+ enterprises','Enterprise size, not site size'],[num(current.commercial),'Commercial-fit US postings','Historical inventory · selected employers']];
  $('market-kpis').innerHTML=cards.map(([n,l,c])=>`<div class="market-kpi"><strong>${n}</strong><span>${l}</span><small>${c}</small></div>`).join('');
  $('county-region').innerHTML+=[...stateNames].sort((a,b)=>a[1].localeCompare(b[1])).map(([c,n])=>`<option value="${c}">${esc(n)}</option>`).join('');
  if(boston){$('market-layer').value='county';$('county-region').value='25';}
  function legend(labels, shades=colors){$('market-legend').innerHTML=labels.map((l,i)=>`<span><i style="background:${shades[i]}"></i>${esc(l)}</span>`).join('');}
  function bar(label,v,max,annotation=''){
    return `<div class="market-bar"><span>${esc(label)}${annotation?`<br><small>${esc(annotation)}</small>`:''}</span><div class="market-bar-track"><div class="market-bar-fill" style="width:${max?100*v/max:0}%"></div></div><b>${num(v)}</b></div>`;
  }
  function stateDetail(code){
    selectedState=code;const r=D.us.states.find(s=>s.state===code),key=$('market-measure').value;
    document.querySelectorAll('#market-map path').forEach(p=>p.classList.toggle('selected',p.dataset.state===code));
    $('market-detail').innerHTML=r?`<p class="eyebrow">STATE POSTING EVIDENCE</p><h3>${esc(r.name)}</h3><strong>${num(r[key])}</strong><p>${esc($('market-measure').selectedOptions[0].text)}<br>${num(r.employers)} employers in the saved records</p><p>${num(r.missing_posted_date)} records lack a posting date. Zero means no matches in this inventory.</p>`:'<p class="eyebrow">STATE POSTING EVIDENCE</p><h3>Choose a state</h3><p>Click or focus a state to compare historical posting evidence. Counts are affected by employer and collection coverage.</p>';
  }
  function countyDetail(geoid){
    selectedCounty=geoid;const r=D.counties.find(c=>c.geoid===geoid);
    document.querySelectorAll('#market-map path').forEach(p=>p.classList.toggle('selected',p.dataset.county===geoid));
    $('county-pick').value=geoid||'';
    $('market-detail').innerHTML=r?`<p class="eyebrow">COUNTY WORKFORCE CONTEXT</p><h3>${esc(r.name)}<br><small>${esc(r.state_name||stateNames.get(r.geoid.slice(0,2)))}</small></h3><strong>${r.value===null?'No estimate':r.value.toFixed(1)+'%'}</strong><p>Adults ages 25–54 employed · ${D.county_meta.year}</p><p>${r.lower!==null&&r.upper!==null?`Source interval: ${r.lower.toFixed(1)}–${r.upper.toFixed(1)}%<br>`:''}Quality: ${esc(r.quality||'not provided')}<br>Status: ${esc(r.status.replaceAll('_',' '))}<br>County FIPS: ${r.geoid}</p><p>This measures the resident population, not pharma employment or learner eligibility.</p>`:'<p class="eyebrow">COUNTY WORKFORCE CONTEXT</p><h3>Choose a county</h3><p>Select a county on the map or in the dropdown to inspect its employment estimate, confidence bounds and quality.</p><p>Higher employment does not establish higher demand for this certificate.</p>';
  }
  function drawMap(){
    const county=$('market-layer').value==='county';
    $('state-measure-label').hidden=county;$('county-region-label').hidden=!county;$('county-pick-label').hidden=!county;
    if(!county){
      $('market-map').innerHTML=D.state_svg;
      const key=$('market-measure').value,rows=D.us.states.filter(r=>r.state!=='Unallocated'),max=Math.max(...rows.map(r=>r[key]));
      document.querySelectorAll('#market-map path').forEach(p=>{
        const r=rows.find(r=>r.state===p.dataset.state);if(!r)return;
        const v=r[key],index=v===0?0:Math.min(5,1+Math.floor(v/max*4));p.style.fill=v===0?'#edf2f7':colors[index];
        p.setAttribute('aria-label',`${r.name}: ${v} ${$('market-measure').selectedOptions[0].text}`);p.querySelector('title').textContent=p.getAttribute('aria-label');
        p.addEventListener('click',()=>stateDetail(r.state));p.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();stateDetail(r.state);}});
      });
      legend(['0','>0–<25% of max','25–<50%','50–<75%','75–<100%','Maximum'],['#edf2f7',...colors.slice(1)]);
      $('map-vintage').textContent='Saved US posting inventory';
      $('market-map-note').textContent=`Relative color scale; maximum is ${num(max)} records. Exact counts appear on selection. County layer uses a different population and scale.`;
      const u=D.us.states.find(s=>s.state==='Unallocated');$('market-coverage').textContent=`${num(u[key])} of ${num(D.us.inventory[key])} records in this measure are state-unallocated and excluded from shading. US totals retain them.`;
      stateDetail(selectedState);
    }else{
      const region=$('county-region').value,rows=D.counties.filter(c=>region==='all'||c.geoid.startsWith(region));
      let box='0 0 800 380';if(region!=='all'&&rows.length){const x=Math.min(...rows.map(r=>r.bbox[0])),y=Math.min(...rows.map(r=>r.bbox[1])),right=Math.max(...rows.map(r=>r.bbox[2])),bottom=Math.max(...rows.map(r=>r.bbox[3])),pad=Math.max(right-x,bottom-y)*.06;box=`${x-pad} ${y-pad} ${right-x+2*pad} ${bottom-y+2*pad}`;}
      const defs=colors.map((c,i)=>`<pattern id="county-hatch-${i}" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="${c}"/><path d="M-1,1L1,-1 M0,5L5,0 M4,6L6,4" stroke="#102c60" stroke-width=".6"/></pattern>`).join('');
      const markup=rows.map(r=>{const i=r.value===null?null:[50,60,70,80,90].filter(v=>r.value>=v).length,fill=i===null?'#e1e4e9':r.status==='low_quality'?`url(#county-hatch-${i})`:colors[i];return `<path data-county="${r.geoid}" d="${r.path}" fill="${fill}" fill-rule="evenodd"><title>${esc(r.name)}: ${r.value===null?'No usable estimate':r.value.toFixed(1)+'%'}; ${esc(r.quality||r.status)}</title></path>`;}).join('');
      $('market-map').innerHTML=`<svg viewBox="${box}" role="img" aria-label="County share of adults ages 25 to 54 employed"><defs>${defs}</defs>${markup}</svg>`;
      $('county-pick').innerHTML='<option value="">Select a county</option>'+[...rows].sort((a,b)=>(a.state_name+a.name).localeCompare(b.state_name+b.name)).map(r=>`<option value="${r.geoid}">${esc(r.name)}, ${esc(r.state_name||stateNames.get(r.geoid.slice(0,2)))}</option>`).join('');
      document.querySelectorAll('#market-map [data-county]').forEach(p=>p.addEventListener('click',()=>countyDetail(p.dataset.county)));
      legend(['<50%','50–<60%','60–<70%','70–<80%','80–<90%','90–100%','No usable value'],[...colors,'#e1e4e9']);
      $('map-vintage').textContent=`Urban Institute · ${D.county_meta.year}`;
      $('market-map-note').textContent=`2025 Census boundaries; exact county FIPS joins. ${region==='all'?'Alaska and Hawaii are inset.':'Region zoom changes the geographic scale.'} Hatched shapes have marginal or weak source quality.`;
      const usable=rows.filter(r=>r.value!==null).length,low=rows.filter(r=>r.status==='low_quality').length;
      $('market-coverage').textContent=`${num(usable)} of ${num(rows.length)} displayed county boundaries have a usable estimate; ${num(low)} are lower quality. Nationally, ${D.county_meta.unmatched_geoids.length} source codes have no matching boundary and ${D.county_meta.excluded_territories.length} territory observations are excluded. Observation year is not the download date.`;
      countyDetail(rows.some(r=>r.geoid===selectedCounty)?selectedCounty:null);
    }
  }
  function sizes(){
    const workforce=$('size-measure').value==='workforce';let rows;
    if(boston){rows=['2,000+','500–1,999','Under 500'].map(b=>({label:b,value:D.boston.employers.filter(e=>e.size_band===b).reduce((s,e)=>s+(workforce?e.ma_employees:1),0)}));$('size-heading').textContent='20 employers, by MA workforce';$('size-note').textContent='Selected major employers · 2026 MassBio. MA workforce is not worldwide headcount or potential training seats. The shortlist is not the regional size distribution.';}
    else{rows=D.us.bands.map(b=>({label:b.band,value:b[workforce?'EMPL':'FIRM']}));$('size-note').textContent='Census SUSB 2022 · NAICS 3254. Size bands use whole-enterprise employment; workforce bars count only manufacturing establishments in this industry. R&D-only and service firms are outside this denominator.';}
    const max=Math.max(...rows.map(r=>r.value));$('size-chart').innerHTML=rows.map(r=>bar(r.label,r.value,max)).join('');
  }
  function employers(){
    const key=$('employer-measure').value;
    let rows=boston?D.boston.employers.map(e=>({name:e.company,value:e[key==='headcount'?'ma_employees':'local_'+key],covered:key==='headcount'||e.inventory_covered})):D.us.employers.map(e=>({name:e.company,value:e[key],covered:true}));
    rows.sort((a,b)=>(b.value||0)-(a.value||0)||a.name.localeCompare(b.name));const max=Math.max(...rows.map(r=>r.value||0));
    $('employer-chart').innerHTML=rows.map(r=>r.covered?bar(r.name,r.value,max):`<div class="market-bar"><span>${esc(r.name)}</span><small>Outside inventory</small><b>—</b></div>`).join('');
    $('employer-note').textContent=key==='headcount'?'Massachusetts employees, 2026 MassBio. AstraZeneca/Alexion is combined. Headcount does not establish eligible learners.':boston?'Core + declared outreach suburbs. Dash = employer absent from inventory; zero = no matching local record. AstraZeneca posting coverage excludes a separate Alexion match.':'Selected employers only. More postings can reflect collection coverage, not greater hiring or training demand. US company headcounts are not inferred from postings.';
  }
  if(boston){$('employer-measure').insertAdjacentHTML('afterbegin','<option value="headcount">Massachusetts workforce</option>');$('employer-measure').value='headcount';}
  $('fit-chart').innerHTML=[['All saved postings',current.postings],['Broad analytics',current.analytics],['Commercial-data fit',current.commercial]].map(([l,v])=>bar(l,v,current.postings)).join('');
  $('fit-note').textContent=`${boston?'Boston core + outreach suburbs':'Selected US employer inventory'}. Nested rule-screened posting subsets, not a learner conversion funnel. Commercial fit is evidence for task alignment, not proof of eligibility or sponsorship.`;
  ['market-layer','market-measure','county-region'].forEach(id=>$(id).addEventListener('change',drawMap));
  $('county-pick').addEventListener('change',()=>countyDetail($('county-pick').value));
  $('size-measure').addEventListener('change',sizes);$('employer-measure').addEventListener('change',employers);
  sizes();employers();drawMap();
})();
