const fs = require('node:fs'), assert = require('node:assert/strict'), path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const bundle = JSON.parse(read('outputs/us-employer-inventory/web/dashboard-data.js').replace(/^window.PHARMA_DATA = /, '').trim().replace(/;$/, '').replaceAll('<\\/', '</'));
for (const [page, file, key] of [['outlook','outlook-data.json','benchmarks'],['skills','skills-data.json','employer_analysis']]) {
  const source = read(page+'.qmd'), rendered = read('_site/'+page+'.html');
  assert.deepEqual(JSON.parse(read('outputs/us-employer-inventory/web/'+file)), bundle[key]);
  assert.equal(read('outputs/us-employer-inventory/web/'+file), read('_site/outputs/us-employer-inventory/web/'+file));
  assert.match(source, /```\{ojs\}/);
  assert.match(rendered, /quarto-ojs-runtime.js/);
  assert.match(rendered, /interpretFromScriptTags/);
  assert.doesNotMatch(source, /```\{=html\}|explorer-scripts/);
  assert.doesNotMatch(rendered, /<script src="scripts\/dashboard.js"/);
}
// Independent row-level reconciliation for each published skill scope.
for (const [key, scope] of Object.entries(bundle.employer_analysis.scopes)) {
  const jobs = bundle.jobs.filter(j => key === 'us' || (key === 'analytics' ? j.analytics_relevant : j.data_signals.length));
  assert.equal(scope.records, jobs.length);
  for (const skill of scope.skills) {
    const matches = jobs.filter(j => j.skills.includes(skill.name));
    assert.equal(skill.records, matches.length);
    assert.equal(skill.denominator, jobs.length);
    assert.equal(skill.companies, new Set(matches.map(j => j.company)).size);
    assert.deepEqual(skill.sources.map(s => s.id).sort(), matches.map(j => j.id).sort());
  }
}
console.log('OJS_OK: focused attachment parity, native compiled pages, and independent skill/source denominators');
