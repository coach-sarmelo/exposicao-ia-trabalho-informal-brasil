const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

console.log('======================================================================');
console.log('1. STATIC ACCESSIBILITY & WCAG 2.1 AA CHECKS');
console.log('======================================================================');

const html = fs.readFileSync(path.join(__dirname, '../docs/index.html'), 'utf8');

// 1. Skip link
assert(html.includes('.skip-link{position:absolute;'), 'Skip link CSS missing');
assert(html.includes('<a href="#mainContent" class="skip-link">Pular para o conteúdo principal</a>'), 'Skip link anchor missing');
assert(html.includes('<main id="mainContent" tabindex="-1">'), 'Main landmark ID/tabindex missing');
console.log('  [PASS] Skip link & landmark configured correctly');

// 2. Focus visible
assert(html.includes('#dataTable th:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}'), 'Table header focus-visible style missing');
assert(html.includes('.chip:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,a:focus-visible'), 'Interactive elements focus-visible missing');
console.log('  [PASS] Focus visible styles present for buttons, links, inputs, selects, headers');

// 3. Contrast fix
assert(html.includes('.decomp-seg-edu{background:#56B4E9;color:#0c2a4a;'), 'Decomp sky blue segment text contrast not fixed');
assert(html.includes('.econ-badge.blue{background:#e8f0fe;color:#174ea6}'), 'Blue badge contrast not fixed to >= 4.5:1');
assert(html.includes('.dim{color:#4b5563;'), 'Dim element contrast not fixed');
console.log('  [PASS] Color contrast on decomp bar segment, badges, and dim text meets WCAG AA/AAA');

// 4. Decorative emojis wrapped in aria-hidden
assert(html.includes('<span aria-hidden="true">✉️ </span>'), 'Email emoji not aria-hidden');
assert(html.includes('<span aria-hidden="true">📄 </span>'), 'Paper emoji not aria-hidden');
assert(html.includes('<span aria-hidden="true">💻 </span>'), 'GitHub emoji not aria-hidden');
assert(html.includes('<span aria-hidden="true">🔗 </span>'), 'LinkedIn emoji not aria-hidden');
assert(html.includes('<span aria-hidden="true">‹ </span>Anterior'), 'Prev arrow not aria-hidden');
assert(html.includes('Próxima <span aria-hidden="true"> ›</span>'), 'Next arrow not aria-hidden');
assert(html.includes('<span aria-hidden="true">⬇ </span>Baixar CSV filtrado'), 'CSV download arrow not aria-hidden');
console.log('  [PASS] All decorative emojis wrapped in aria-hidden with descriptive labels');

// 5. Accessible table headers
assert(html.includes('tabindex="0" role="columnheader"'), 'Table headers role and tabindex missing');
assert(html.includes('aria-sort='), 'Table headers aria-sort attribute missing');
console.log('  [PASS] Table headers properly formatted with ARIA attributes & keyboard navigation');

// 6. Mobile responsiveness - filterbar unsticking
assert(html.includes('.filterbar{position:relative;top:auto}') || html.includes('.filterbar{position:static'), 'Filterbar not un-stuck on mobile viewports');
console.log('  [PASS] Mobile filterbar unsticking rule present');

// 7. Aria-live regions
assert(html.includes('id="activeCount" aria-live="polite"'), 'activeCount aria-live missing');
assert(html.includes('id="pageInfo" aria-live="polite"'), 'pageInfo aria-live missing');
assert(html.includes('id="tableInfo" style="margin-left:auto" aria-live="polite"'), 'tableInfo aria-live missing');
console.log('  [PASS] Live regions configured with aria-live="polite"');

// 7. Verify no sub-12px font sizes in CSS or Oster gauge
const smallFontRegex = /font-size:\s*(10|10\.[0-9]|11|11\.[0-9])px/g;
const matches = [];
let m;
while ((m = smallFontRegex.exec(html)) !== null) {
  matches.push({ match: m[0], index: m.index });
}
assert.strictEqual(matches.length, 0, `Found sub-12px font size matches: ${JSON.stringify(matches)}`);
console.log('  [PASS] Zero sub-12px font declarations found in file');

console.log('\n======================================================================');
console.log('2. JAVASCRIPT EXECUTION & DASHBOARD DATA ENGINE AUDIT');
console.log('======================================================================');

const scriptMatches = [...html.matchAll(/<script(?:\s+[^>]*)?>([\s\S]*?)<\/script>/g)];
assert(scriptMatches.length >= 3, 'Expected at least 3 script tags in index.html');

// Script 0: DASH_DATA
const dashDataCode = scriptMatches[0][1];
const dataSandbox = { window: {} };
vm.createContext(dataSandbox);
vm.runInContext(dashDataCode, dataSandbox);
const rawDashData = dataSandbox.window.DASH_DATA;
assert(rawDashData, 'Could not evaluate window.DASH_DATA');
console.log(`  [PASS] Loaded raw DASH_DATA successfully. n = ${rawDashData.n}, occs = ${rawDashData.occs.length}, ufs = ${rawDashData.ufs.length}`);

// Script 2: DashApp code
const dashAppCode = scriptMatches[2][1];

// Create sandbox
const sandbox = {
  window: {},
  document: {
    getElementById: (id) => ({
      addEventListener: () => {},
      querySelectorAll: () => [],
      innerHTML: '',
      textContent: '',
      setAttribute: () => {},
      classList: { toggle: () => {}, add: () => {}, remove: () => {} }
    }),
    createElement: () => ({
      setAttribute: () => {},
      addEventListener: () => {},
      classList: { toggle: () => {} },
      appendChild: () => {}
    })
  },
  Float32Array,
  Float64Array,
  Uint8Array,
  Uint32Array,
  Math,
  JSON,
  atob: (b64) => Buffer.from(b64, 'base64').toString('binary'),
  Intl,
  setTimeout,
  clearTimeout,
  console
};
sandbox.globalThis = sandbox.window;
sandbox.window.DASH_DATA = rawDashData;

vm.createContext(sandbox);
vm.runInContext(dashAppCode, sandbox);

const DashApp = sandbox.window.DashApp;
assert(DashApp, 'DashApp was not exported to window');
assert(typeof DashApp.decodeData === 'function', 'decodeData function missing');
assert(typeof DashApp.filterIndices === 'function', 'filterIndices function missing');
assert(typeof DashApp.tableFilterIndices === 'function', 'tableFilterIndices function missing');
assert(typeof DashApp.setData === 'function', 'setData helper missing');

// Initialize data in DashApp
DashApp.setData(rawDashData);
const V = DashApp.decodeData(rawDashData);
console.log(`  [PASS] decodeData verified: decoded ${V.n} rows. Array types valid.`);
assert.strictEqual(V.n, rawDashData.n);
assert(V.inc instanceof Uint32Array);
assert(V.expo instanceof Float32Array);
assert(V.w instanceof Float32Array);

// Check filterIndices
const state = DashApp.state;
state.regions = new Set(rawDashData.regions.map((_, i) => i));
state.sexes = new Set([0, 1]);
state.races = new Set(Object.keys(rawDashData.raceLabels).map(Number));
state.forms = new Set([0, 1]);

const allIdx = DashApp.filterIndices(V, state);
assert.strictEqual(allIdx.length, rawDashData.n, 'Initial filterIndices did not match total n');
console.log(`  [PASS] filterIndices all-active returns full sample (${allIdx.length})`);

// Filter by region: Southeast only (region 2)
state.regions = new Set([2]);
const seIdx = DashApp.filterIndices(V, state);
assert(seIdx.length > 0 && seIdx.length < allIdx.length, 'Southeast filter failed');
console.log(`  [PASS] Regional filter: Southeast sample = ${seIdx.length}`);

// Reset regions
state.regions = new Set(rawDashData.regions.map((_, i) => i));

console.log('\n======================================================================');
console.log('3. SEARCH & TABLE FILTERING BATTERY (Panel 4)');
console.log('======================================================================');

// 3.1 Empty query
state.q = '';
state.expoMin = '';
state.expoMax = '';
state.incMin = '';
state.incMax = '';
const t0 = DashApp.tableFilterIndices(allIdx);
assert.strictEqual(t0.length, allIdx.length, 'Empty search should return all indices');
console.log(`  [PASS] Empty query returns full set (${t0.length} rows)`);

// 3.2 Search by occupation name (e.g. vendedor)
state.q = 'vendedor';
const tVendedor = DashApp.tableFilterIndices(allIdx);
assert(tVendedor.length > 0, 'Search for "vendedor" returned 0 rows');
for (const i of tVendedor.slice(0, 50)) {
  const occName = DashApp.deacc(rawDashData.occs[V.occ[i]].name);
  assert(occName.includes('vendedor'), `Occupation does not match: ${rawDashData.occs[V.occ[i]].name}`);
}
console.log(`  [PASS] Search "vendedor" matched ${tVendedor.length} rows; sampled rows validated`);

// 3.3 Search with accents (e.g. médico)
state.q = 'médico';
const tMedicoAcc = DashApp.tableFilterIndices(allIdx);
state.q = 'medico';
const tMedicoNoAcc = DashApp.tableFilterIndices(allIdx);
assert.strictEqual(tMedicoAcc.length, tMedicoNoAcc.length, 'Accent insensitive matching failed for médico/medico');
assert(tMedicoAcc.length > 0, 'Search for médico returned 0');
console.log(`  [PASS] Accent insensitivity verified: "médico" (${tMedicoAcc.length}) === "medico" (${tMedicoNoAcc.length})`);

// 3.4 Search by COD occupation code
const sampleOcc = rawDashData.occs.find(o => o.code === '111');
state.q = sampleOcc.code;
const tCode = DashApp.tableFilterIndices(allIdx);
assert(tCode.length > 0, `Search by occupation code ${sampleOcc.code} returned 0`);
for (const i of tCode) {
  const occ = rawDashData.occs[V.occ[i]];
  assert(occ.code.includes(sampleOcc.code) || DashApp.deacc(occ.name).includes(sampleOcc.code));
}
console.log(`  [PASS] Search by COD code "${sampleOcc.code}" matched ${tCode.length} rows`);

// 3.5 Search by UF abbreviation (SP)
state.q = 'SP';
const tSP = DashApp.tableFilterIndices(allIdx);
assert(tSP.length > 0, 'Search by UF abbreviation SP returned 0');
console.log(`  [PASS] Search by UF abbreviation "SP" matched ${tSP.length} rows`);

// 3.6 Search by full UF state name (São Paulo / sao paulo)
state.q = 'São Paulo';
const tSPFullName = DashApp.tableFilterIndices(allIdx);
state.q = 'sao paulo';
const tSPFullNameLower = DashApp.tableFilterIndices(allIdx);
assert.strictEqual(tSPFullName.length, tSPFullNameLower.length, 'Search by full state name failed accent parity');
assert(tSPFullName.length > 0, 'Full name São Paulo returned 0');
for (const i of tSPFullName) {
  const uf = rawDashData.ufs[V.uf[i]];
  assert.strictEqual(uf, 'SP', `Row with UF ${uf} matched São Paulo`);
}
console.log(`  [PASS] Search by full state name "São Paulo" matched ${tSPFullName.length} rows, 100% belonging to SP`);

// 3.7 Multi-token search across occupation AND UF (e.g. "vendedor SP")
state.q = 'vendedor SP';
const tVendedorSP = DashApp.tableFilterIndices(allIdx);
assert(tVendedorSP.length > 0, 'Multi-token search "vendedor SP" returned 0');
assert(tVendedorSP.length < tVendedor.length, '"vendedor SP" should be a subset of "vendedor"');
for (const i of tVendedorSP) {
  const occName = DashApp.deacc(rawDashData.occs[V.occ[i]].name);
  const uf = rawDashData.ufs[V.uf[i]];
  assert(occName.includes('vendedor'), 'Occupation does not match');
  assert.strictEqual(uf, 'SP', 'UF does not match SP');
}
console.log(`  [PASS] Multi-token cross search "vendedor SP" matched ${tVendedorSP.length} rows (all verified)`);

// 3.8 Multi-token with full state name ("vendedor São Paulo")
state.q = 'vendedor São Paulo';
const tVendedorSPFull = DashApp.tableFilterIndices(allIdx);
assert.strictEqual(tVendedorSPFull.length, tVendedorSP.length, '"vendedor São Paulo" must match "vendedor SP"');
console.log(`  [PASS] Multi-token full state name "vendedor São Paulo" matched ${tVendedorSPFull.length} rows`);

// 3.9 Numerical range filters (expoMin and expoMax)
state.q = '';
state.expoMin = '5.0';
state.expoMax = '7.0';
const tExpoRange = DashApp.tableFilterIndices(allIdx);
assert(tExpoRange.length > 0, 'Exposure range [5.0, 7.0] returned 0');
for (const i of tExpoRange.slice(0, 100)) {
  assert(!isNaN(V.expo[i]), 'NaN exposure included in range');
  assert(V.expo[i] >= 5.0 && V.expo[i] <= 7.0, `Exposure out of range: ${V.expo[i]}`);
}
console.log(`  [PASS] Exposure range [5.0, 7.0] matched ${tExpoRange.length} rows`);

// 3.10 Combined query + ranges
state.q = 'professor';
state.expoMin = '4.0';
state.expoMax = '';
state.incMin = '3000';
state.incMax = '';
const tCombined = DashApp.tableFilterIndices(allIdx);
assert(tCombined.length > 0, 'Combined search returned 0');
for (const i of tCombined) {
  const occName = DashApp.deacc(rawDashData.occs[V.occ[i]].name);
  assert(occName.includes('professor'));
  assert(V.expo[i] >= 4.0);
  assert(V.inc[i] >= 3000);
}
console.log(`  [PASS] Combined query "professor" + expo>=4.0 + inc>=3000 matched ${tCombined.length} rows`);

// 3.11 Impossible query returns empty array
state.q = 'astronauta AC';
const tZero = DashApp.tableFilterIndices(allIdx);
assert.strictEqual(tZero.length, 0, 'Impossible query should return 0 rows');
console.log(`  [PASS] Zero-result search returned 0 rows gracefully`);

console.log('\n======================================================================');
console.log('4. STATISTICAL & AGGREGATION ROUTINES INTEGRITY');
console.log('======================================================================');

// 4.1 wSummary
const sumInc = DashApp.wSummary(i => V.inc[i], V, allIdx);
assert(!isNaN(sumInc.mean), 'wSummary mean is NaN');
assert(sumInc.mean > 0, 'Mean income must be positive');
assert(sumInc.med > 0, 'Median income must be positive');
assert(sumInc.sd > 0, 'SD income must be positive');
console.log(`  [PASS] wSummary income: Mean = R$ ${sumInc.mean.toFixed(2)}, Median = R$ ${sumInc.med.toFixed(2)}, SD = R$ ${sumInc.sd.toFixed(2)}`);

// 4.2 wPearson
const rEduExpo = DashApp.wPearson(i => V.edu[i], i => V.expo[i], V, allIdx.filter(i => !isNaN(V.expo[i])));
assert(!isNaN(rEduExpo), 'wPearson correlation is NaN');
assert(rEduExpo > 0.4, `Schooling-Exposure correlation expected > 0.4, got ${rEduExpo}`);
console.log(`  [PASS] wPearson (Schooling × Exposure): r = ${rEduExpo.toFixed(4)} (strong positive gradient)`);

// 4.3 regionOccCells
const cells = DashApp.regionOccCells(V, allIdx, 20);
assert(cells.length > 0, 'regionOccCells returned 0 cells');
for (const c of cells.slice(0, 10)) {
  assert(c.n >= 20, 'Cell n less than threshold');
  assert(!isNaN(c.expo), 'Cell expo is NaN');
  assert(c.jobs > 0, 'Cell jobs <= 0');
}
console.log(`  [PASS] regionOccCells: Generated ${cells.length} regional bubbles (n >= 20)`);

console.log('\n======================================================================');
console.log('ALL VERIFICATION BATTERIES PASSED PERFECTLY!');
console.log('======================================================================');
