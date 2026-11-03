/* All displayed data comes from the versioned snapshot bundled at build time. */
(() => {
'use strict';
const D=window.PHARMA_DATA, $=id=>document.getElementById(id);
if(!D) return;
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number=n=>Number(n).toLocaleString('en-US');
const money=n=>'$'+number(n);
if ($('home-inventory-metric')) $('home-inventory-metric').innerHTML=`<strong>${D.inventory.employers_with_jobs}</strong><p>employers with US postings</p><small>${D.inventory.job_count} combined posting identities</small>`;
if ($('map')) {
const states=D.meteor.geography.states, mapped=D.meteor.geography.mapped_records;
let selected=null;
$('map').innerHTML=D.map;
const colors=['#edf2fa','#d2e3fc','#97bdf0','#4e8bd6','#1e5197'];
function measure(s){return $('map-measure').value==='share'?s.records/mapped*100:$('map-measure').value==='texts'?s.distinct_employer_text_hashes:s.records;}
function label(v){return $('map-measure').value==='share'?v.toFixed(1)+'%':number(v);}
function selectState(code){selected=code;const s=states.find(x=>x.code===code);$('state-name').textContent=s?s.name:'United States';$('state-count').textContent=s?label(measure(s)):number(mapped);$('state-description').textContent=s?`${s.records} observed records \u00b7 ${s.distinct_employer_text_hashes} distinct employer/text pairs`:'State-mapped historical records';$('map-selection').textContent=s?`${s.name}: ${s.records} records (${(s.records/mapped*100).toFixed(1)}% of mapped records), ${s.distinct_employer_text_hashes} distinct employer/text pairs. Historical location-text inference, not current openings.`:'Historical records by state.';document.querySelectorAll('[data-state]').forEach(p=>{p.classList.toggle('selected',p.dataset.state===code);p.setAttribute('aria-pressed',String(p.dataset.state===code));});}
function drawMap(){const share=$('map-measure').value==='share', cuts=share?[0,1,5,10]:[0,10,30,60];document.querySelectorAll('path[data-state]').forEach(p=>{const s=states.find(x=>x.code===p.dataset.state),v=measure(s);const i=v===0?0:v<=cuts[1]?1:v<=cuts[2]?2:v<=cuts[3]?3:4;p.setAttribute('fill',colors[i]);const text=`${s.name}: ${label(v)} ${share?'of mapped records':$('map-measure').value==='texts'?'distinct employer/text pairs':'historical records'}`;p.setAttribute('aria-label',text);p.querySelector('title').textContent=text;});const labels=share?['No assigned records','>0\u20131%','>1\u20135%','>5\u201310%','>10%']:['No assigned records','1\u201310','11\u201330','31\u201360','61+'];$('map-legend').innerHTML=labels.map((l,i)=>`<span><i class="swatch" style="background:${colors[i]}"></i>${l}</span>`).join('');selectState(selected);}
$('map-measure').addEventListener('change',drawMap);
document.querySelectorAll('path[data-state]').forEach(p=>{p.addEventListener('click',()=>selectState(p.dataset.state));p.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectState(p.dataset.state);}});});
$('reset-state').addEventListener('click',()=>selectState(null));
$('state-ranking').innerHTML=[...states].sort((a,b)=>b.records-a.records).slice(0,5).map(s=>`<div class="rank-row"><button type="button" data-pick="${s.code}">${s.name}</button><strong>${s.records}</strong></div>`).join('');
document.querySelectorAll('[data-pick]').forEach(b=>b.addEventListener('click',()=>selectState(b.dataset.pick)));
$('geo-coverage').textContent=`${number(mapped)} of ${number(D.meteor.counts.commercial_candidates)} screened records mapped (${(mapped/D.meteor.counts.commercial_candidates*100).toFixed(1)}%). Location-text inference; not verified US vacancy counts.`;
$('state-table').innerHTML='<table><caption>Historical candidate records by inferred state</caption><thead><tr><th>State</th><th>Records</th><th>Share of mapped</th><th>Distinct employer/text pairs</th></tr></thead><tbody>'+states.map(s=>`<tr><td>${s.name}</td><td>${s.records}</td><td>${(s.records/mapped*100).toFixed(1)}%</td><td>${s.distinct_employer_text_hashes}</td></tr>`).join('')+'</tbody></table>';
$('geo-exclusions').innerHTML='<p>All 1,353 candidates reconcile to these mutually exclusive geographic buckets:</p><ul>'+Object.entries(D.meteor.geography.buckets).map(([k,v])=>`<li>${escape(k.replaceAll('_',' '))}: ${number(v)}</li>`).join('')+'</ul><p>Repeated employer/text pairs are not confirmed duplicate vacancies; the same pair can appear in more than one state. Remote records are not assigned to every state.</p>';
drawMap();
}
if ($('benchmark-cards')) $('benchmark-cards').innerHTML=D.benchmarks.occupations.map(b=>`<article class="benchmark-card"><span class="tiny">SOC ${b.soc} \u00b7 NATIONAL PROXY</span><h3>${b.name}</h3><strong class="benchmark-growth">+${b.growth}%</strong><span class="tiny"> &nbsp; projected, 2025\u20132035</span><div class="growth-track" aria-hidden="true"><span style="width:${b.growth/35*100}%"></span></div><div class="benchmark-facts"><div><strong>${money(b.median)}</strong><small>May 2025 median annual wage</small></div><div><strong>${number(b.openings)}</strong><small>Projected annual openings</small></div></div><p class="tiny">Openings include replacement needs; they are not currently advertised jobs.</p><a href="${b.url}" target="_blank" rel="noopener">BLS source \u2197</a> &nbsp; <a href="${b.onet}" target="_blank" rel="noopener">O*NET occupation \u2197</a></article>`).join('');
if ($('job-cards')) {
const usJobs=D.jobs, companies=D.inventory.companies, pageSize=12;
$('raw-coverage').textContent=`Raw employer-name matches: ${number(D.inventory.source_counts.local)} local records + ${number(D.inventory.source_counts.azure)} Azure records. After employer identity, cross-store deduplication, US-location and relevance checks: ${D.inventory.job_count} eligible posting identities. Source totals include overlaps and excluded records.`;
let page=1;
function jobFactTags(job){
 const tags=[
  ...(job.requirements.degrees_mentioned.length?[['Degree mention',job.requirements.degrees_mentioned.join(', ')]]:[]),
  ...(job.requirements.experience_year_mentions.length?[['Experience',`${job.requirements.experience_year_mentions.join(', ')} years`]]:[]),
  ...(job.requirements.equivalent_experience_language?[['Degree alternative','Equivalent experience mentioned']]:[]),
  ...job.data_signals.map(value=>['Data',value])
 ];
 return tags.length?`<ul class="job-fact-tags" aria-label="Detected text mentions">${tags.map(([label,value])=>`<li><span class="tag-label">${escape(label)}:</span> ${escape(value)}</li>`).join('')}</ul>`:'';
}
function renderJobs(){
 const company=$('job-employer').value||'__all__',q=$('job-search').value.trim().toLowerCase(),lev=$('job-level').value,signal=$('job-signal').value,store=$('job-store').value;
 const matching=usJobs.filter(j=>(lev==='all'||j.level===lev)&&(signal==='all'||(signal==='any'?j.data_signals.length>0:j.data_signals.includes(signal)))&&(store==='all'||(store==='both'?j.stores.length===2:j.stores.includes(store)))&&[j.title,j.location,...j.skills,...j.requirements.degrees_mentioned].join(' ').toLowerCase().includes(q));
 const counts=[...companies].sort((a,b)=>a.company.localeCompare(b.company)).map(c=>{const rows=matching.filter(j=>j.company===c.company);return {...c,matching:rows.length,local:rows.filter(j=>j.stores.includes('local')).length,azure:rows.filter(j=>j.stores.includes('azure')).length,both:rows.filter(j=>j.stores.length===2).length};});
 $('employer-count').textContent=`${matching.length} matching US postings \u00b7 ${counts.filter(c=>c.matching>0).length} employers with matches \u00b7 ${companies.length} employers searched`;
 $('job-employer').innerHTML=`<option value="__all__">All employers (${matching.length})</option>`+counts.map(c=>`<option value="${escape(c.company)}">${escape(c.company)} (${c.matching})</option>`).join('');
 $('job-employer').value=company;
 $('employer-summary').innerHTML='<table><caption>Employer counts for the selected filter combination</caption><thead><tr><th>Employer</th><th>Combined</th><th>Local</th><th>Azure</th><th>In both</th></tr></thead><tbody>'+counts.map(c=>`<tr><th scope="row">${escape(c.company)}</th><td>${c.matching}</td><td>${c.local}</td><td>${c.azure}</td><td>${c.both}</td></tr>`).join('')+'</tbody></table>';
 $('job-pagination').hidden=!company;
 const c=counts.find(c=>c.company===company);
 $('employer-detail').textContent=c?`${c.company}: ${c.matching} matching of ${c.jobs} eligible postings \u00b7 ${c.local} local \u00b7 ${c.azure} Azure \u00b7 ${c.both} in both (counted once).`:'All employers: showing postings matching the selected combination.';
 const jobs=matching.filter(j=>company==='__all__'||j.company===company).sort((a,b)=>(b.display_on||'').localeCompare(a.display_on||'')||a.title.localeCompare(b.title));
 const pages=Math.max(1,Math.ceil(jobs.length/pageSize));page=Math.min(page,pages);
 $('job-count').textContent=`${jobs.length} matching postings for ${company==='__all__'?'all employers':company}. Historical database evidence; not live-rechecked.`;
 $('job-page').textContent=`Page ${page} of ${pages}`;$('job-prev').disabled=page===1;$('job-next').disabled=page===pages;
 $('job-cards').innerHTML=jobs.length?jobs.slice((page-1)*pageSize,page*pageSize).map(j=>`<article class="job-card" data-posting-id="${escape(j.id)}"><div class="job-company">${escape(j.company)}</div><h3>${escape(j.title)}</h3><p class="job-meta">${escape(j.location)} \u00b7 ${escape(j.level)} \u00b7 ${j.date_basis==='source_reported_posted_at'?escape(j.display_on||'Date unavailable'):j.date_basis==='database_created_at_proxy'?`First recorded: ${escape(j.display_on||'Unknown')}`:'Date unavailable'}</p><p class="tiny">${escape(j.stores.join(' + '))} \u00b7 ${j.source_records} source records combined<br>US evidence: ${escape(j.geography_basis.replaceAll('_',' '))}</p>${jobFactTags(j)}<p class="tiny">Qualification mentions may describe degree alternatives or different types of experience. ${escape(j.status)}.</p><div class="chips">${j.skills.map(x=>`<span>${escape(x)}</span>`).join('')}</div></article>`).join(''):'<p class="empty-state">No eligible postings match this employer and these filters. A zero reflects stored evidence and screening, not an absence of employment opportunities.</p>';
}
['job-employer','job-level','job-signal','job-store'].forEach(id=>$(id).addEventListener('change',()=>{page=1;renderJobs();}));
$('job-search').addEventListener('input',()=>{page=1;renderJobs();});
$('job-prev').addEventListener('click',()=>{if(page>1){page--;renderJobs();}});
$('job-next').addEventListener('click',()=>{page++;renderJobs();});renderJobs();
}
if ($('skill-bars')) {
let selectedSkillKey=null;
function showSkill(index){
 const scope=D.employer_analysis.scopes[$('skill-scope').value],s=scope.skills[index];
 if(!s) return;
 const key=$('skill-scope').value+':'+index;
 if(key===selectedSkillKey) return;
 selectedSkillKey=key;
 const companies=[...new Set(s.sources.map(x=>x.company))].sort();
 $('skill-detail').innerHTML=`<p class="eyebrow">SKILL EVIDENCE</p><h3>${escape(s.name)}</h3><div class="skill-detail-metrics"><div><strong>${number(s.records)}</strong><span>posting identities</span></div><div><strong>${number(s.companies)}</strong><span>company labels</span></div></div><p><strong>${(s.records/s.denominator*100).toFixed(1)}%</strong> of ${number(s.denominator)} postings in this scope mention this skill.</p><p class="tiny">Companies: ${companies.map(escape).join(', ')}.</p><details><summary>Inspect stored source examples</summary><ul>${s.sources.slice(0,5).map(x=>`<li>${x.url?`<a href="${escape(x.url)}" target="_blank" rel="noopener">${escape(x.company)} \u2197</a>`:escape(x.company)} \u00b7 ${escape(x.id)}</li>`).join('')}</ul><a href="jobs.html">Explore all matching roles \u2192</a></details><p class="tiny">Historical posting evidence. Required and preferred mentions are not classified separately.</p>`;
 $('skill-bars').dataset.activeSkill=String(index);
 document.querySelectorAll('[data-skill-index]').forEach(button=>button.setAttribute('aria-pressed',String(Number(button.dataset.skillIndex)===index)));
 $('skill-status').textContent=`${s.name}: ${s.records} postings, ${s.companies} companies, ${(s.records/s.denominator*100).toFixed(1)} percent of selected postings.`;
}
function renderSkills(){
 const scope=D.employer_analysis.scopes[$('skill-scope').value],peak=Math.max(1,...scope.skills.map(s=>s.records));
 $('skill-summary').textContent=`${scope.records} US data and analytics postings across ${scope.companies} companies. Each skill counts once per posting; required and preferred mentions are combined.`;
 $('skill-bars').innerHTML=scope.skills.map((s,i)=>`<button type="button" class="skill-bubble" aria-controls="skill-detail" aria-describedby="skill-hint" aria-pressed="false" data-skill-index="${i}" style="--bubble-size:${(188*Math.sqrt(s.records/peak)).toFixed(2)}px" aria-label="${escape(s.name)}: ${s.records} posting identities, ${s.companies} companies, ${(s.records/s.denominator*100).toFixed(1)} percent. Show evidence."><span>${escape(s.name)}</span><strong>${s.records}</strong></button>`).join('');
 selectedSkillKey=null;
 showSkill(0);
}
function inspectSkill(event){
 // Moving across a bubble's child text must not rebuild or collapse its evidence.
 // Hover must not replace source links while a keyboard user is reading them.
 if(event.type==='mouseover' && document.activeElement && $('skill-detail').contains(document.activeElement)) return;
 const button=event.target.closest('[data-skill-index]');
 if(button)showSkill(Number(button.dataset.skillIndex));
}
['mouseover','focusin','click'].forEach(event=>$('skill-bars').addEventListener(event,inspectSkill));
$('skill-scope').addEventListener('change',renderSkills);renderSkills();
}
if ($('scenario')) {
const scenarios=[
{title:'Why did prescriptions drop this week?',role:'Data operations / stewardship',question:'A fall in reported prescriptions can reflect lower demand or a change in pharmacy coverage. The distinction matters because each explanation calls for a different response.',steps:['The analyst compares incoming prescription counts, reporting dates and pharmacy coverage with the previous delivery.','SQL checks identify missing feeds and duplicate records. An exception log connects each issue to its source.','A comparison restricted to consistent coverage separates changes in the data from changes in observed activity.','The release recommendation explains which patterns remain after those checks and which require further investigation.'],output:'A reconciliation query, quality-rule log, data glossary and release recommendation.',link:'Related responsibilities: AbbVie data operations. Curriculum connection: Courses 1–2 and capstone.'},
{title:'Where does the patient journey slow down?',role:'Market access analytics',question:'Longer time to therapy may reflect delays at a particular stage, differences in patient groups or incomplete follow-up. A common cohort definition makes those explanations easier to separate.',steps:['The analysis defines a cohort, observation window and consistent start and end events.','Linked patient-support, claims and formulary records reveal gaps in coverage and missing timestamps.','Time-to-therapy comparisons account for incomplete follow-up and differences in patient characteristics.','The findings identify stages for operational investigation while preserving uncertainty about the cause of the differences.'],output:'A cohort specification, linkage-quality report, time-to-event analysis and decision brief.',link:'Related responsibilities: Sobi and AbbVie payer analytics. Curriculum connection: Courses 1–3 and capstone.'},
{title:'Which territories need a closer look?',role:'Commercial insights / field analytics',question:'Differences in treatment-center activity can reflect territory opportunity, reporting delays or source coverage. A useful scorecard separates those factors before comparing performance.',steps:['A shared business question establishes the population and denominator for comparison.','Authorized or synthetic CRM, patient-support, specialty-pharmacy and claims records provide complementary measures.','The scorecard distinguishes activity, access and patient flow, with adjustments for coverage and reporting delays.','Sensitivity checks show which comparisons persist under different assumptions and support a focused recommendation.'],output:'A documented data model, BI scorecard and executive recommendation with a measurement plan.',link:'Related responsibilities: Iovance commercial analytics. Curriculum connection: Courses 2–4.'}
];
function showScenario(i){const s=scenarios[i];$('scenario').innerHTML=`<div><p class="eyebrow">ILLUSTRATIVE WORK BRIEF / ${escape(s.role)}</p><h3>${s.title}</h3><p>${s.question}</p><div class="deliverable"><strong>Illustrative portfolio artifact</strong><br>${s.output}</div><p class="tiny" style="margin-top:16px">${s.link}</p></div><div><h3>How the analysis develops</h3><ol>${s.steps.map(x=>`<li>${x}</li>`).join('')}</ol><p class="tiny">These scenarios illustrate analytical relationships; they are not reported employer projects.</p></div>`;document.querySelectorAll('[data-scenario]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.scenario)===i)));}
document.querySelectorAll('[data-scenario]').forEach(b=>b.addEventListener('click',()=>showScenario(Number(b.dataset.scenario))));showScenario(0);
}
})();
