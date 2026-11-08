const fs=require('fs');
module.exports=async({page})=>{
const out='D:/Repositories/AD688-G0-F26-pharma-careers/outputs/review-2026-11-07';
const result=[];
for(const width of [1440,390]){
 await page.setViewportSize({width,height:900});
 await page.goto('file:///D:/Repositories/AD688-G0-F26-pharma-careers/_site/index.html');
 await page.screenshot({path:out+'/clean-home-'+width+'.png',fullPage:true});
 result.push(await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,h1:document.querySelector('h1').innerText,hero:document.querySelector('.hero').getBoundingClientRect().toJSON()})));
}
fs.writeFileSync(out+'/cleanup-browser.json',JSON.stringify(result,null,2));
console.log('CLEANUP_BROWSER_OK',JSON.stringify(result));
};
