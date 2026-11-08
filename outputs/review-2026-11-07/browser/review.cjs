const fs=require('fs'),path=require('path');
module.exports=async({page})=>{
const out=path.join(process.cwd(),'outputs/review-2026-11-07/browser');const base='file:///D:/Repositories/AD688-G0-F26-pharma-careers/_site/';const results={pages:[],interactions:[],errors:[]};
page.on('pageerror',e=>results.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')results.errors.push(m.text())});
const save=()=>fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify(results,null,2));
for(const name of ['index','jobs','skills','geography','us-market','boston-market','training-market']){
 await page.setViewportSize({width:1440,height:1000});let response=await page.goto(base+(name+'.html'),{waitUntil:'networkidle',timeout:60000});
 let data={name,status:response?.status(),url:page.url(),desktop:await page.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth,headings:[...document.querySelectorAll('h1,h2')].map(e=>e.textContent.trim()),parquetLinks:[...document.querySelectorAll('a[href]')].filter(e=>e.href.includes('.parquet')).map(e=>e.href)}))};
 await page.screenshot({path:path.join(out,name+'-desktop.png'),fullPage:false});
 if(name==='jobs'){
  results.interactions.push({type:'jobs default',text:await page.locator('#job-count').innerText(),cards:await page.locator('.job-card').count()});
  await page.locator('#job-relevance').selectOption('analytics');results.interactions.push({type:'jobs analytics',text:await page.locator('#job-count').innerText()});
  await page.locator('#job-search').fill('zzzz-no-match-review');results.interactions.push({type:'jobs empty',text:await page.locator('#job-cards').innerText()});
  await page.locator('#job-search').fill('');await page.locator('#job-relevance').selectOption('all');
  await page.locator('#job-next').click();results.interactions.push({type:'jobs next',text:await page.locator('#job-page').innerText()});
 }
 if(name==='skills' && await page.locator('.ojs-bubble').count()){
  await page.locator('.ojs-bubble').first().waitFor();let bubbles=page.locator('.ojs-bubble');
  await bubbles.nth(1).hover();await page.waitForTimeout(200);results.interactions.push({type:'skill hover',skill:await bubbles.nth(1).getAttribute('data-skill'),text:await page.locator('#selected-skill-summary').innerText()});
  await bubbles.nth(2).focus();await page.waitForTimeout(200);results.interactions.push({type:'skill keyboard focus',skill:await bubbles.nth(2).getAttribute('data-skill'),text:await page.locator('#selected-skill-summary').innerText(),pressed:await bubbles.nth(2).getAttribute('aria-pressed')});
  let selects=page.locator('select');data.selects=await selects.evaluateAll(es=>es.map(e=>({options:[...e.options].map(o=>({label:o.label,value:o.value}))})));
  let compare=selects.filter({has:page.locator('option', {hasText:'Share of scope (%)'})});await compare.selectOption({label:'Share of scope (%)'});await page.waitForTimeout(200);results.interactions.push({type:'skill share geometry',bubbles:await bubbles.evaluateAll(es=>es.slice(0,4).map(e=>({skill:e.dataset.skill,inline:e.getAttribute('style'),disc:e.querySelector('.bubble-disc').getBoundingClientRect().width,text:e.innerText}))) });
 }
 if(name==='geography'){
  await page.locator('#map-measure').selectOption('share');let state=page.locator('#map [data-state="MA"]');await state.focus();await state.press('Enter');results.interactions.push({type:'geography keyboard',text:await page.locator('#state-name').innerText(),count:await page.locator('#state-count').innerText()});
 }
 if(name==='us-market'){
  await page.locator('#market-layer').selectOption('county');await page.locator('#county-region').selectOption({label:'Massachusetts'});data.countyOptions=await page.locator('#county-pick option').count();await page.locator('#county-pick').selectOption({index:1});results.interactions.push({type:'county selection',text:await page.locator('#market-detail').innerText()});
 }
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(200);data.mobile=await page.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('main *')].filter(e=>{let r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+2||r.left< -2)}).slice(0,12).map(e=>({tag:e.tagName,id:e.id,class:e.className,width:e.getBoundingClientRect().width}))}));await page.screenshot({path:path.join(out,name+'-mobile.png'),fullPage:false});results.pages.push(data);save();
}
save();console.log('BROWSER_REVIEW_COMPLETE');
};
