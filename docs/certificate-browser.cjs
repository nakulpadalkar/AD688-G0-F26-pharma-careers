const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
module.exports = async ({page}) => {
 const root = 'D:/Repositories/AD688-G0-F26-pharma-careers';
 const out = path.join(root, 'outputs/certificate/qa');
 fs.mkdirSync(out, {recursive:true});
 await page.setViewportSize({width:1440,height:1000});
 await page.goto(pathToFileURL(path.join(root,'_site/about.html')).href);
 await page.locator('.certificate-page').waitFor();
 await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
 for (const width of [1440,390]) {
   await page.setViewportSize({width,height:900});
   if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)) throw Error('Overflow at '+width);
   const rows = await page.locator('.certificate-page tbody tr').count();
   if(rows!==4) throw Error('Expected four course rows');
   await page.getByRole('link',{name:'Explore the curriculum',exact:true}).click();
   if (!page.url().endsWith('#curriculum')) throw Error('Curriculum anchor');
   await page.getByRole('link',{name:'How self-paced study works',exact:true}).click();
   if (!page.url().endsWith('#learning-format')) throw Error('Format anchor');
   await page.evaluate(()=>window.scrollTo(0,0));
   await page.screenshot({path:path.join(out,width===390?'mobile.png':'desktop-top.png'),fullPage:width===390});
 }
 console.log('CERTIFICATE_BROWSER_OK: four course rows; desktop/mobile widths; curriculum and format anchors');
};
