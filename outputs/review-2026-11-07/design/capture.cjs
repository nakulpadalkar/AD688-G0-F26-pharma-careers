const fs=require('fs'); const path=require('path');
module.exports=async({page})=>{
 const out='D:/Repositories/AD688-G0-F26-pharma-careers/outputs/review-2026-11-07/design';
 const base='https://nakulpadalkar.github.io/AD688-G0-F26-pharma-careers/';
 const records=[];
 for(const width of [1440,390]){
 await page.setViewportSize({width,height:1000});
 for(const name of ['index','jobs','skills','training-market','us-market']){
 const resp=await page.goto(base+(name==='index'?'':name+'.html'),{waitUntil:'networkidle'});
 await page.screenshot({path:path.join(out,name+'-'+width+'.png'),fullPage:false});
 records.push({name,width,status:resp.status(),title:await page.title(),text:(await page.locator('body').innerText()).slice(0,18000)});
 }
 }
 fs.writeFileSync(path.join(out,'pages.json'),JSON.stringify(records,null,2));
 console.log('DESIGN_CAPTURE_OK');
};
