// Executes the actual dashboard against a minimal DOM fixture. This checks logic,
// event wiring and generated content, not browser layout or browser API fidelity.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),pages=['index','geography','outlook','jobs','skills','work'],html=pages.map(name=>fs.readFileSync(path.join(root,'_site',name+'.html'),'utf8')).join('\n');
const elements=new Map(),paths=[],picks=[],tabs=[];
class Element{
 constructor(id,dataset={}){this.id=id;this.dataset=dataset;this.events={};this.attrs={};this.value='';this.textContent='';this.content='';this.title={textContent:''};this.classes=new Set();this.classList={toggle:(k,v)=>v?this.classes.add(k):this.classes.delete(k)};}
 set innerHTML(value){this.content=value;this.writes=(this.writes||0)+1;if(this.id==='map'){for(const m of value.matchAll(/data-state="([A-Z]{2})"/g))paths.push(new Element('',{state:m[1]}));}if(this.id==='state-ranking'){for(const m of value.matchAll(/data-pick="([A-Z]{2})"/g))picks.push(new Element('',{pick:m[1]}));}}
 get innerHTML(){return this.content;}
 contains(target){return target.owner===this.id;}
 addEventListener(name,fn){this.events[name]=fn;}
 setAttribute(k,v){this.attrs[k]=v;}
 querySelector(s){assert.equal(s,'title');return this.title;}
 fire(name,event={}){assert.ok(this.events[name],`No handler: ${this.id}:${name}`);this.events[name](event);}
}
for(const m of html.matchAll(/\bid="([^"]+)"/g))elements.set(m[1],new Element(m[1]));
for(const m of html.matchAll(/data-scenario="(\d+)"/g))tabs.push(new Element('',{scenario:m[1]}));
const get=id=>{assert.ok(elements.has(id),`Missing rendered DOM id: ${id}`);return elements.get(id);};
get('job-relevance').value='all';get('job-signal').value='all';get('map-measure').value='records';get('job-level').value='all';
const document={getElementById:get,querySelectorAll:selector=>{if(selector==='path[data-state]'||selector==='[data-state]')return paths;if(selector==='[data-pick]')return picks;if(selector==='[data-scenario]')return tabs;throw Error(`Unsupported selector ${selector}`);}};
const context=vm.createContext({window:{},document});
vm.runInContext(fs.readFileSync(path.join(root,'outputs/us-employer-inventory/web/dashboard-data.js'),'utf8'),context);
vm.runInContext(fs.readFileSync(path.join(root,'scripts/dashboard.js'),'utf8'),context);
const countCards=()=>[...get('job-cards').innerHTML.matchAll(/class="job-card"/g)].length;
const inventory=context.window.PHARMA_DATA.inventory,jobsData=context.window.PHARMA_DATA.jobs;
assert.equal(paths.length,51);assert.equal(countCards(),Math.min(12,jobsData.length));
assert.match(get('raw-coverage').textContent,/18,443 local records/);assert.match(get('raw-coverage').textContent,/4,549 Azure records/);assert.ok(jobsData.length>6);assert.ok(get('employer-count').textContent.startsWith(jobsData.length+' matching'));
assert.equal(get('job-employer').value,'__all__');
assert.ok(!elements.has('job-store'));
assert.match(get('employer-summary').innerHTML,/Teva/);
assert.equal(jobsData.length,9493);
get('job-next').fire('click');
for(const [value,total] of [['analytics',1127],['other',8366],['all',9493]]){
 get('job-relevance').value=value;get('job-relevance').fire('change');
 assert.ok(get('employer-count').textContent.startsWith(total+' matching'));
 assert.match(get('job-page').textContent,/Page 1 of/);
}
// Global combinations filter postings immediately with all employers selected.
get('job-level').value='Manager';get('job-signal').value='Claims data';get('job-signal').fire('change');
const combined=jobsData.filter(j=>j.level==='Manager'&&j.data_signals.includes('Claims data'));
assert.ok(combined.length>0);assert.equal(countCards(),Math.min(12,combined.length));assert.ok(get('employer-count').textContent.startsWith(combined.length+' matching'));
get('job-employer').value='__all__';get('job-employer').fire('change');assert.equal(countCards(),Math.min(12,combined.length));
get('job-relevance').value='analytics';get('job-relevance').fire('change');
const analyticsCombined=combined.filter(j=>j.analytics_relevant);
assert.equal(countCards(),Math.min(12,analyticsCombined.length));assert.ok(get('employer-count').textContent.startsWith(analyticsCombined.length+' matching'));
get('job-relevance').value='all';
get('job-level').value='all';get('job-signal').value='all';get('job-signal').fire('change');
// Traverse every employer's entire pagination and verify no record is omitted or repeated.
const seen=new Set();let pulled=0;
for(const company of inventory.companies){
 get('job-employer').value=company.company;get('job-employer').fire('change');let found=0;
 for(let p=0;p<Math.max(1,Math.ceil(company.jobs/12));p++){
  const ids=[...get('job-cards').innerHTML.matchAll(/data-posting-id="([^"]+)"/g)].map(x=>x[1]);
  pulled += [...get('job-cards').innerHTML.matchAll(/class="job-pull-date"/g)].length;
  for(const id of ids){assert.ok(!seen.has(id));seen.add(id);assert.equal(jobsData.find(j=>j.id===id).company,company.company);}
  assert.doesNotMatch(get('job-cards').innerHTML,/Not detected|No equivalent-experience phrase detected|No tracked dataset\/vendor terms detected|<dt>/);
  found+=ids.length;if(!get('job-next').disabled)get('job-next').fire('click');
 }
 assert.equal(found,company.jobs);
}
assert.equal(seen.size,jobsData.length);assert.equal(pulled,5071);
get('job-employer').value='AbbVie';get('job-employer').fire('change');assert.equal(countCards(),12);assert.match(get('job-cards').innerHTML,/\d{4}-\d{2}-\d{2}|First recorded:/);get('job-next').fire('click');assert.match(get('job-page').textContent,/Page 2/);get('job-prev').fire('click');assert.match(get('job-page').textContent,/Page 1/);
get('job-search').value='NOT_A_REAL_SKILL';get('job-search').fire('input');assert.equal(countCards(),0);assert.match(get('employer-count').textContent,/0 matching US postings/);
get('job-search').value='';get('job-search').fire('input');get('job-employer').value='';get('job-employer').fire('change');assert.equal(countCards(),Math.min(12,jobsData.length));assert.equal(get('job-employer').value,'__all__');
assert.match(get('map-legend').innerHTML,/1\u201310/);assert.match(get('map-legend').innerHTML,/11\u201330/);assert.match(get('map-legend').innerHTML,/31\u201360/);
const ca=paths.find(p=>p.dataset.state==='CA');ca.fire('click');assert.equal(get('state-count').textContent,'120');assert.match(get('map-selection').textContent,/18.3%/);assert.equal(ca.attrs['aria-pressed'],'true');
get('map-measure').value='share';get('map-measure').fire('change');assert.equal(get('state-count').textContent,'18.3%');
get('map-measure').value='texts';get('map-measure').fire('change');assert.equal(get('state-count').textContent,'100');
const il=paths.find(p=>p.dataset.state==='IL');let prevented=false;il.fire('keydown',{key:'Enter',preventDefault(){prevented=true;}});assert.ok(prevented);assert.equal(get('state-name').textContent,'Illinois');
get('reset-state').fire('click');assert.equal(get('state-name').textContent,'United States');assert.equal(get('state-count').textContent,'654');
for(let i=0;i<3;i++){tabs[i].fire('click');assert.equal(tabs[i].attrs['aria-pressed'],'true');assert.match(get('scenario').innerHTML,/portfolio artifact/);}
assert.match(get('scenario').innerHTML,/territories/);
// Smoke-test each real rendered page with absent elements returning null.
for (const page of [...pages,'about','eda_pharma']) {
 paths.length=0;picks.length=0;tabs.length=0;
 const pageHtml=fs.readFileSync(path.join(root,'_site',page+'.html'),'utf8'),local=new Map();
 for(const m of pageHtml.matchAll(/\bid="([^"]+)"/g))local.set(m[1],new Element(m[1]));
 for(const m of pageHtml.matchAll(/data-scenario="(\d+)"/g))tabs.push(new Element('',{scenario:m[1]}));
 for(const [id,value] of Object.entries({'map-measure':'records','job-relevance':'all','job-level':'all','job-signal':'all'}))if(local.has(id))local.get(id).value=value;
 const isolated=vm.createContext({window:{},document:{getElementById:id=>local.get(id)||null,querySelectorAll:document.querySelectorAll}});
 vm.runInContext(fs.readFileSync(path.join(root,'outputs/us-employer-inventory/web/dashboard-data.js'),'utf8'),isolated);
 vm.runInContext(fs.readFileSync(path.join(root,'scripts/dashboard.js'),'utf8'),isolated);
 const expected={index:'home-inventory-metric',geography:'state-table',jobs:'job-cards',work:'scenario'}[page];
 if(expected)assert.ok(local.get(expected).innerHTML.length>(page==='index'?50:100),`${page} did not initialize`);
 if(page==='index')assert.ok(!local.has('map')&&!local.has('job-cards'),'Home still contains long explorers');
}
console.log('INTERACTIONS_OK: 8 independent pages; complete US inventory; all employers/pagination; independent global relevance + level + data combinations; employer isolation, search + empty state, levels, 3 map measures, keyboard selection/reset, 3 scenarios');
