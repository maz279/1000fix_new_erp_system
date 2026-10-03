/* Build the 1000FiX ERP employee user guide (marketing/user-guide/index.html)
   from _catalog.json (live nav payload) + _guide_knowledge.js (authored narrative)
   + static part files. Run: node _build_guide.js  (from the marketing folder) */
'use strict';
const fs = require('fs');
const path = require('path');
const DIR = __dirname;
const cat = JSON.parse(fs.readFileSync(path.join(DIR, '_catalog.json'), 'utf8'));
const KNW = require('./_guide_knowledge.js');
const OUTDIR = path.join(DIR, 'user-guide');
fs.mkdirSync(OUTDIR, { recursive: true });
const OUT = path.join(OUTDIR, 'index.html');
const readPart = function (name) { return fs.readFileSync(path.join(DIR, name), 'utf8'); };

const esc = function (s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); };
const typeName = { g: 'Grid / list', f: 'Form', r: 'Report', c: 'Console', d: 'Dashboard', x: '360 view' };

function tocHtml() {
  let h = '';
  cat.areas.forEach(function (a) {
    if (!a.mods.length) return;
    h += '<details class="toc-g" open><summary><b>' + esc(a.id) + '</b> ' + esc(a.en) + '</summary><ul>';
    h += '<li><a href="#area-' + a.id + '">Area overview</a></li>';
    a.mods.forEach(function (m) { h += '<li><a href="#mod-' + m.mid + '">' + esc(m.mid + ' \u00b7 ' + m.en) + '</a></li>'; });
    h += '</ul></details>';
  });
  return h;
}

function moduleTables(m) {
  let h = '<div class="tables">';
  h += '<div class="tbl-card"><h4>Key screens (' + m.groups.reduce(function (n, g) { return n + g.screens.length; }, 0) + ')</h4><table><thead><tr><th>Group</th><th>Screen</th><th>Type</th></tr></thead><tbody>';
  m.groups.forEach(function (g) {
    g.screens.forEach(function (s, i) {
      h += '<tr>' + (i === 0 ? '<td rowspan="' + g.screens.length + '">' + esc(g.en) + '</td>' : '') +
        '<td><code>' + esc(s.id) + '</code></td><td>' + esc(typeName[s.t] || s.t) + '</td></tr>';
    });
  });
  h += '</tbody></table></div>';
  if (m.reports && m.reports.length) {
    h += '<div class="tbl-card"><h4>Built-in reports (' + m.reports.length + ')</h4><ul class="mini">' +
      m.reports.map(function (r) { return '<li>' + esc(r) + '</li>'; }).join('') + '</ul></div>';
  }
  if (m.forms && m.forms.length) {
    h += '<div class="tbl-card"><h4>Data-entry forms (' + m.forms.length + ')</h4><ul class="mini">' +
      m.forms.map(function (r) { return '<li>' + esc(r) + '</li>'; }).join('') + '</ul></div>';
  }
  if (m.freg && m.freg.sub && m.freg.sub.length) {
    h += '<div class="tbl-card"><h4>Function register \u2014 ' + m.freg.src + ' functions in ' + m.freg.sub.length + ' sub-modules</h4><table><thead><tr><th>#</th><th>Sub-module</th><th>Functions</th></tr></thead><tbody>' +
      m.freg.sub.map(function (s) { return '<tr><td>' + esc(s[0]) + '</td><td>' + esc(s[1]) + '</td><td>' + esc(s[2]) + '</td></tr>'; }).join('') +
      '</tbody></table></div>';
  }
  return h + '</div>';
}

function moduleSection(m) {
  const k = KNW.MODULES[m.mid] || {};
  let h = '<section class="module" id="mod-' + m.mid + '">';
  h += '<div class="mod-head"><span class="mod-id">' + esc(m.mid) + '</span><div><h3>' + esc(m.en) + '</h3><p class="bn">' + esc(m.bn) + '</p></div><span class="mod-count">' + m.groups.reduce(function (n, g) { return n + g.screens.length; }, 0) + ' screens \u00b7 ' + (m.reports || []).length + ' reports \u00b7 ' + (m.forms || []).length + ' forms</span></div>';
  h += '<p class="purpose">' + esc(k.p || '') + '</p>';
  h += '<figure><img loading="lazy" src="images/w-' + m.mid + '.png" alt="' + esc(m.mid + ' ' + m.en + ' workspace') + '"><figcaption>' + esc(m.mid + ' \u2014 ' + m.en + ' workspace. Open it in the app: Tell-ME \u2192 ' + m.mid + ', or the area mega menu.') + '</figcaption></figure>';
  if (k.how) {
    h += '<div class="cols"><div class="how"><h4>How you use it</h4><ol>' + k.how.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ol></div>';
    h += '<div><h4>Business knowledge</h4><p>' + esc(k.biz || '') + '</p><h4>What you gain</h4><p class="benefit">' + esc(k.b || '') + '</p></div></div>';
  }
  h += moduleTables(m);
  return h + '</section>';
}

function areaSection(a) {
  const k = KNW.AREAS[a.id] || {};
  let h = '<section class="area" id="area-' + a.id + '"><h2>' + esc(a.id) + ' \u2014 ' + esc(a.en) + ' <span class="bn">' + esc(a.bn) + '</span></h2>';
  h += '<p class="lead">' + esc(k.intro || '') + '</p>';
  h += '<div class="area-grid"><div><h4>The business of this area</h4><p>' + esc(k.biz || '') + '</p></div>';
  h += '<div><h4>Why it matters to you</h4><ul>' + (k.b || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div></div>';
  h += '<p class="area-mods">' + a.mods.map(function (m) { return '<a href="#mod-' + m.mid + '">' + esc(m.mid + ' ' + m.en) + '</a>'; }).join('<span class="dot"> \u00b7 </span>') + '</p>';
  a.mods.forEach(function (m) { h += moduleSection(m); });
  return h + '</section>';
}

const parts = [];
parts.push('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>');
parts.push('<meta name="viewport" content="width=device-width, initial-scale=1"/>');
parts.push('<title>1000 FiX ERP \u2014 Employee User Guide</title>');
parts.push(readPart('_guide_style.css'));
parts.push('</head><body>');
parts.push('<header class="cover"><div class="wrap">');
parts.push('<div class="kicker">1000 FiX Services Ltd. \u00b7 Internal</div>');
parts.push('<h1>1000 FiX ERP \u2014 Employee User Guide</h1>');
parts.push('<div class="sub">Everything you need to work in the system: how the ERP is organised, how to use every area module by module, and the business knowledge behind each screen \u2014 written for every employee, from branch counter to boardroom.</div>');
parts.push('<div class="meta">Edition 2.0 \u00b7 28 September 2026 \u00b7 covers 67 modules \u00b7 12 areas \u00b7 12 portals \u00b7 hotline 16743<br/>Works offline \u2014 open this file in any browser. Screenshots taken from the live interactive prototype.</div>');
parts.push('</div></header>');
parts.push('<div class="layout">');
parts.push('<nav class="toc" aria-label="Guide contents"><div class="toc-title">Contents</div>');
parts.push('<a href="#welcome">0 \u00b7 Welcome</a><a href="#started">1 \u00b7 Getting started</a><a href="#skills">2 \u00b7 Core skills</a><a href="#map">3 \u00b7 The map of the system</a>');
parts.push('<div class="toc-title">Module by module</div>');
parts.push(tocHtml());
parts.push('<a href="#portals">5 \u00b7 Portals</a><a href="#journeys">6 \u00b7 End-to-end journeys</a><a href="#personas">7 \u00b7 Whose screen is whose</a>');
parts.push('<a href="#glossary">8 \u00b7 Glossary &amp; FAQ</a><a href="#reference">9 \u00b7 Reference</a></nav>');
parts.push('<main>');
parts.push(readPart('_guide_part_welcome.html'));
parts.push(readPart('_guide_part_started.html'));
parts.push(readPart('_guide_part_skills.html'));

/* Part 3 — the map of the system (fixes part numbering and orients the reader) */
parts.push('<section id="map"><h2>Part 3 \u00b7 The map of the system</h2>');
parts.push('<p class="lead">Before the module detail, hold the whole picture: eleven business areas (plus Home) carry the 67 modules. The same structure you see here is the left navigation in the app \u2014 learn the map once, navigate forever.</p>');
parts.push('<table><thead><tr><th>Area</th><th>What it covers</th><th>Modules</th><th>Key numbers</th></tr></thead><tbody>');
cat.areas.forEach(function (a) {
  if (!a.mods.length) return;
  const screens = a.mods.reduce(function (n, m) { return n + m.groups.reduce(function (n2, g) { return n2 + g.screens.length; }, 0); }, 0);
  const reports = a.mods.reduce(function (n, m) { return n + (m.reports || []).length; }, 0);
  const funcs = a.mods.reduce(function (n, m) { return n + ((m.freg && m.freg.src) || 0); }, 0);
  parts.push('<tr><td><b>' + esc(a.id) + '</b><br/><span class="bn">' + esc(a.en) + '</span></td><td>' + esc((KNW.AREAS[a.id] || {}).intro || '') + '</td><td>' + a.mods.length + '<br/><span class="ref">' + a.mods.map(function (m) { return m.mid; }).join(' ') + '</span></td><td>' + screens + ' screens<br/>' + reports + ' reports<br/>' + funcs + ' functions</td></tr>');
});
parts.push('</tbody></table>');
parts.push('<div class="callout"><b>Reading the module pages:</b> every module id (M01\u2013M67) is searchable in Tell-ME \u2014 type the id and Enter to land on its workspace. The ids are stable; screens may evolve, ids don\u2019t.</div>');
parts.push('</section>');

parts.push('<section id="modules"><h2>Part 4 \u00b7 The 67 modules, area by area</h2><p class="lead">Each area opens with its business context; each module page follows the same rhythm \u2014 what it is, a screenshot, how you use it step by step, the business knowledge behind it, what you personally gain, then the reference tables (screens, reports, forms, function register).</p><div class="callout"><b>Numbers note:</b> the tables under each module are generated from the system\u2019s own navigation data \u2014 what you read here is exactly what exists in the app, and the <code>#/coverage</code> screen verifies it.</div>');
parts.push('<figure><img loading="lazy" src="images/s-freg.png" alt="Function explorer"><figcaption>The Function Explorer \u2014 every sub-module and function behind a module, drillable one level deeper (<code>#/freg/M01/0</code> shown).</figcaption></figure>');
cat.areas.forEach(function (a) { if (a.mods.length) parts.push(areaSection(a)); });
parts.push('</section>');

parts.push('<section id="portals"><h2>Part 5 \u00b7 The 12 portals \u2014 every audience gets its own door</h2><p class="lead">The ERP is one system, but a customer, a technician and a vendor each need a different view of it. Portals are role-scoped front doors over the same data.</p><div class="cards">');
cat.portals.forEach(function (p) {
  parts.push('<div class="card"><div class="tag">' + esc(p.id) + '</div><h4>' + esc(p.name) + '</h4><p><b>Who:</b> ' + esc(p.audience) + ' \u00b7 <b>Scale:</b> ' + esc(p.scale) + '</p><p>' + (p.features || []).slice(0, 5).map(esc).join(' \u00b7 ') + '</p></div>');
});
parts.push('</div><figure><img loading="lazy" src="images/s-portals.png" alt="Portals page"><figcaption>The Portals screen in the app \u2014 all 12 doors with their audiences and scale.</figcaption></figure></section>');

parts.push('<section id="journeys"><h2>Part 6 \u00b7 Ten end-to-end journeys \u2014 how work flows across modules</h2><p class="lead">A journey is real work crossing module borders. Follow these to see how your piece feeds the next person\u2019s \u2014 each step names the owner and the screen where it happens.</p>');
cat.journeys.forEach(function (j) {
  parts.push('<div class="card journey"><div class="tag">' + esc(j.id) + '</div><h4>' + esc(j.en) + '</h4><table class="steps-table"><thead><tr><th>Step owner</th><th>What happens</th><th>Where in the system</th></tr></thead><tbody>');
  j.steps.forEach(function (s) {
    parts.push('<tr><td>' + esc(s.who) + '</td><td>' + esc(s.what) + '</td><td><code>' + esc(s.route) + '</code></td></tr>');
  });
  parts.push('</tbody></table></div>');
});
parts.push('<figure><img loading="lazy" src="images/s-journeys.png" alt="Journeys page"><figcaption>All journeys, interactive, in the app (<code>#/journeys</code>).</figcaption></figure></section>');

parts.push('<section id="personas"><h2>Part 7 \u00b7 Whose screen is whose \u2014 the four sample personas</h2><div class="cards">');
cat.personas.forEach(function (p) {
  parts.push('<div class="card"><div class="tag">' + esc(p.role) + '</div><h4>' + esc(p.name) + '</h4><p>' + (p.approvals || []).length + ' approvals waiting \u00b7 ' + (p.worklist || []).length + ' worklist items on the Role Centre</p></div>');
});
parts.push('</div><p>Your own Role Centre is assembled from your role, not your name \u2014 when you change departments, your home page changes with you. Try personas on the <code>#/settings</code> screen in the app.</p></section>');

parts.push(readPart('_guide_part_reference.html'));
parts.push('</main></div></body></html>');

fs.writeFileSync(OUT, parts.join('\n'));
/* print variant: PDF export renders lazy images as blank boxes — emit an eager copy */
fs.writeFileSync(path.join(OUTDIR, 'print.html'), parts.join('\n').split(' loading="lazy"').join(''));
console.log('WROTE user-guide/index.html (' + (fs.statSync(OUT).size / 1024).toFixed(0) + ' KB) + print.html, image refs: ' + (parts.join('').split('images/').length - 1));
