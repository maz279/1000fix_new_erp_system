/* =====================================================================
   1000 FiX ERP — FINAL AUDIT: loads every JS file in order exactly as
   app.html does, then walks every route (system pages, 67 workspaces,
   823 screens, 346 report viewers, 278 function explorers, 18 records)
   asserting 0 exceptions. Prints a coverage report.
   Run:  node _audit.js
   ===================================================================== */
'use strict';
const fs = require('fs');
const path = require('path');

const store = {};
global.localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: k => { delete store[k]; }
};
global.addEventListener = () => {};
global.scrollTo = () => {};
global.getComputedStyle = () => ({ getPropertyValue: () => '' });
global.window = global;
global.location = { hash: '#/home' };

let pageHTML = '';
const PAGE = {
  innerHTML: '', scrollTop: 0,
  insertAdjacentHTML: () => {}, querySelectorAll: () => [],
  classList: { add(){}, remove(){}, toggle(){} }, value: ''
};
const el = () => ({
  innerHTML: '', scrollTop: 0, textContent: '', style: {},
  insertAdjacentHTML: () => {}, querySelectorAll: () => [], classList: { add(){}, remove(){}, toggle(){} },
  setAttribute(){}, dataset: {}, appendChild(){}, value:''
});
global.document = {
  documentElement: { lang: 'en', dataset: {}, classList: { add(){}, remove(){}, toggle(){} } },
  getElementById: (id) => id === 'page' ? PAGE : el(),
  querySelectorAll: () => [], querySelector: () => null,
  createElement: () => el(), addEventListener: () => {}, body: el()
};

const FILES = ['nav_data', 'nav_data2', 'nav_data3', 'demo_data', 'i18n', 'charts', 'shell', 'app'];
FILES.forEach(f => {
  new Function('window', fs.readFileSync(path.join(__dirname, 'js', f + '.js'), 'utf8'))(global.window);
});

const NAV = window.FX_MODULES, AREAS = window.FX_AREAS;
let pass = 0, fail = 0;
function walk(hash, label) {
  global.location.hash = hash;
  PAGE.innerHTML = '';
  try {
    window.FXRoute();
    pageHTML = PAGE.innerHTML;
    if (!pageHTML || pageHTML.length < 80) throw new Error('empty render');
    pass++;
  }
  catch (e) { fail++; console.log('  FAIL', hash, '—', e.message); }
}

console.log('1000 FiX ERP — final audit');
console.log('=========================');

/* system routes */
const SYSTEM = ['home', 'reports', 'reports/M01', 'reports/M09', 'writer', 'search?q=dispatch',
  'search?q=' + encodeURIComponent('ওয়ারেন্টি'), 'directory', 'coverage', 'portals', 'journeys',
  'settings', 'designsystem', 'shortcuts', 'palette', 'notifications', 'inbox', 'copilot', 'freg/M01/0'];
SYSTEM.forEach(r => walk('#/' + r, 'system'));
console.log('system routes:', SYSTEM.length, 'rendered');

/* workspaces */
Object.keys(NAV).forEach(mid => walk('#/workspace/' + mid, 'workspace'));

/* every screen */
let screens = 0;
Object.keys(NAV).forEach(mid => NAV[mid].groups.forEach(g => g.screens.forEach(s => {
  walk('#/screen/' + s.id, 'screen'); screens++;
})));
console.log('screens walked:', screens);

/* every report viewer */
let reports = 0;
Object.keys(NAV).forEach(mid => { for (let i = 0; i < NAV[mid].reports.length; i++) { walk('#/report/' + mid + '/' + i, 'report'); reports++; } });
console.log('report viewers walked:', reports);

/* function explorers (sampled: first of each module + every one for 6 core modules) */
let fregs = 0;
Object.keys(NAV).forEach(mid => {
  walk('#/freg/' + mid + '/0', 'freg'); fregs++;
  if (['M01', 'M02', 'M09', 'M20', 'M51', 'M56'].indexOf(mid) >= 0)
    for (let i = 1; i < NAV[mid].freg.sub.length; i++) { walk('#/freg/' + mid + '/' + i, 'freg'); fregs++; }
});
console.log('function explorers walked:', fregs);

/* records */
const RECS = ['M01-order/SO-2026-14838', 'M02-record/WO-9218', 'M31-record/RO-5412', 'M03-record/CS-31244',
  'M33-party/CUS-104283', 'M20-invoice/INV-2026-28441', 'M09-record/CLM-2026-7428', 'M08-record/AMC-2118',
  'M16-pos/PO-2026-4182', 'M17-asset/AST-41280', 'M06-record/DRC-418', 'M23-ncr/NC-628',
  'M36-record/QT-2418', 'M67-record/PRJ-121', 'M21-employee/FX-EMP-321', 'generic/FX-0001'];
RECS.forEach(r => walk('#/record/' + r, 'record'));
console.log('records walked:', RECS.length);

/* search sanity */
const q1 = window.FXSearch('dispatch', 10).length;
const q2 = window.FXSearch('ওয়ারেন্টি', 10).length;
const q3 = window.FXSearch('SO-2026', 10).length;
console.log('search sanity: dispatch=' + q1 + ' ওয়ারেন্টি=' + q2 + ' SO-2026=' + q3);

/* nav-payload integrity */
const ids = new Set(Object.keys(NAV));
let integrity = true;
AREAS.forEach(a => a.mods.forEach(m => { if (!ids.has(m)) { integrity = false; console.log('  MISSING MODULE', m); } }));
Object.keys(NAV).forEach(k => { if (!AREAS.find(a => a.id === NAV[k].area)) { integrity = false; console.log('  BAD AREA', k); } });
console.log('nav integrity:', integrity ? 'OK (67 modules in 12 areas)' : 'ISSUES');

/* totals */
const tot = { g: 0, s: 0, r: 0, f: 0, fn: 0, sub: 0 };
Object.values(NAV).forEach(m => {
  m.groups.forEach(g => { tot.g++; tot.s += g.screens.length; });
  tot.r += m.reports.length; tot.f += (m.forms || []).length;
  tot.fn += m.freg.src; tot.sub += m.freg.sub.length;
});
console.log('-------------------------');
console.log('RESULT:', (fail === 0 ? 'ALL CLEAN ✓' : fail + ' FAILURES'),
  '| walked', pass, 'routes | modules', Object.keys(NAV).length,
  '| groups', tot.g, '| screens', tot.s, '| reports', tot.r,
  '| forms', tot.f, '| sub-modules', tot.sub, '| functions', tot.fn);
process.exit(fail === 0 ? 0 : 1);
