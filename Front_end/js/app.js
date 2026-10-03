/* =====================================================================
   1000 FiX ERP — APPLICATION ROUTER + ARCHETYPE RENDERERS
   (FIX-UXD-2026-001 Parts 6–9). Hash router over the 823-screen nav
   payload; 13 archetypes render every screen type; report center with
   346 built-in viewers + no-code writer; journeys; portals hub;
   coverage audit; task inbox; command palette.
   ===================================================================== */
(function () {
'use strict';
var NAV = window.FX_MODULES, AREAS = window.FX_AREAS, DEMO = window.FX_DEMO,
    I18N = window.FX_I18N, IC = window.FXIcon, S = window.FX_SHELL;
var D = DEMO, t = window.FXT, spark = window.FXSpark;
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g,'&gt;').replace(/"/g, '&quot;'); }
function safeParam(s) { return String(s == null ? '' : s).replace(/[<>'"`\\]/g, ''); }
function typeGlyph(x) { return window.FXTypeIcon(x); }

/* ---------- router ---------------------------------------------------- */
function route() {
  var h = location.hash || '#/home';
  var q = '';
  var qi = h.indexOf('?');
  if (qi >= 0) { q = safeParam(decodeURIComponent(h.slice(qi + 1).replace(/^q=/, ''))); h = h.slice(0, qi); }
  var p = h.replace(/^#\//, '').split('/').map(safeParam);
  var page = document.getElementById('page');
  if (!page) return;
  try {
    if (p[0] === '' || p[0] === 'home') pageHome();
    else if (p[0] === 'workspace' && NAV[p[1]]) pageWorkspace(p[1]);
    else if (p[0] === 'freg' && NAV[p[1]]) pageFreg(p[1], +p[2] || 0);
    else if (p[0] === 'screen') { var hit = findScreen(p[1]); if (hit) pageScreen(p[1]); else notFound('screen ' + p[1]); }
    else if (p[0] === 'record') recordPage(safeParam(decodeURIComponent(p[2] || 'FX-0001')), p[1]);
    else if (p[0] === 'report' && NAV[p[1]]) reportViewerPage(p[1], +p[2] || 0);
    else if (p[0] === 'reports') (p[1] && NAV[p[1]]) ? pageReportsOf(p[1]) : pageReportCenter();
    else if (p[0] === 'writer') pageWriter();
    else if (p[0] === 'search') pageSearch(q);
    else if (p[0] === 'directory') pageDirectory();
    else if (p[0] === 'coverage') pageCoverage();
    else if (p[0] === 'portals') pagePortals();
    else if (p[0] === 'journeys') pageJourneys();
    else if (p[0] === 'settings') pageSettings();
    else if (p[0] === 'designsystem') pageDesignSystem();
    else if (p[0] === 'shortcuts') pageShortcuts();
    else if (p[0] === 'palette') pagePalette();
    else if (p[0] === 'notifications') pageNotifications();
    else if (p[0] === 'inbox') pageInbox();
    else if (p[0] === 'copilot') pageCopilot();
    else notFound(h);
  } catch (err) {
    page.innerHTML = '<div class="fx-card" style="margin:24px;padding:24px"><h2>Render error</h2><p style="font-family:var(--font-mono);font-size:12px">' + esc(err.message) + '</p></div>';
    console.error(err);
  }
  var cr = document.getElementById('sb-crumbs');
  if (cr) cr.textContent = h.length > 64 ? h.slice(0, 61) + '…' : h;
  page.scrollTop = 0;
  window.scrollTo(0, 0);
}
window.FXRoute = route;

function head(crumb, title, sub, actions) {
  return '<div class="pg-head"><div><div class="crumbs">' + crumb + '</div>' +
    '<h1>' + title + '</h1>' + (sub ? '<p class="pg-sub">' + sub + '</p>' : '') + '</div>' +
    '<div class="pg-actions">' + (actions || '') + '</div></div>';
}
function openTabFor(id, title, icon) { window.FXOpenTab(id, title, location.hash, icon); }

/* ---------- home / role centre ----------------------------------------- */
function pageHome() {
  var P = window.FXPersona();
  openTabFor('home', t('role_center'), '◫');
  var revenue = [], jobs = [];
  for (var i = 0; i < 12; i++) { revenue.push(8.4 + i * 0.34 + (i % 3) * 0.18); jobs.push(38 + i * 1.4 + (i % 4) * 2.2); }
  var html = head('<a href="#/home">' + t('home') + '</a>',
    t('good_morning') + ', ' + esc(P.name), esc(P.role) + ' · ' + esc(t('company')) + ' · 27 Sep 2026 · বাংলা available',
    '<a class="btn btn-primary" href="#/screen/M01-order">+ New Service Order</a>' +
    '<a class="btn" href="#/inbox">☑ ' + t('task_inbox') + '</a>' +
    '<a class="btn" href="#/screen/M02-dispatch">' + (S.lang === 'bn' ? 'ডিসপ্যাচ বোর্ড' : 'Dispatch Board') + '</a>');
  html += '<div class="kpi-row">' +
    kpiCard({ l: 'Open Service Orders', v: '1,284', d: '+62 today', up: 1, spark: [1180,1195,1220,1240,1252,1268,1284], href: '#/screen/M01-all' }) +
    kpiCard({ l: 'SLA Compliance', v: '96.2%', d: '+0.8pt', up: 1, st: 'ok', spark: [92,93,94,94.6,95.3,95.8,96.2], href: '#/screen/M01-sla-rep' }) +
    kpiCard({ l: 'First-Time Fix', v: '88.1%', d: '+1.2pt', up: 1, st: 'ok', spark: [70,74,78,81,84,86,88.1], href: '#/screen/M02-wo' }) +
    kpiCard({ l: 'CSAT', v: '4.6 / 5', d: '+0.3', up: 1, st: 'ok', spark: [3.9,4.0,4.2,4.3,4.4,4.5,4.6], href: '#/screen/M34-responses' }) +
    kpiCard({ l: 'Jobs / Tech / Day', v: '7.2', d: '+0.8', up: 1, spark: [4.6,5.1,5.7,6.2,6.7,7.0,7.2], href: '#/screen/M02-wo' }) +
    kpiCard({ l: 'Revenue MTD', v: '৳ 12.42 Cr', d: '+8.4%', up: 1, spark: [9.2,9.8,10.4,10.9,11.5,12.0,12.42], href: '#/report/M19/1' }) +
    '</div>';
  html += '<div class="grid-2">';
  html += '<div class="fx-card"><h3>' + t('approvals') + ' <span class="chip warn">' + P.approvals.length + '</span></h3>' +
    P.approvals.map(function (a) {
      return '<a class="row-link" href="' + a[3] + '"><span class="rl-main"><b>' + esc(a[0]) + '</b> · ' + esc(a[1]) + '</span><span class="rl-meta">' + esc(a[2]) + '</span><span class="rl-act">Approve ›</span></a>';
    }).join('') +
    '<div style="display:flex;gap:8px;margin-top:12px"><button class="btn btn-primary btn-sm" onclick="window.FXToast(\'Approved — workflow M63 posted ✓\')">Approve all</button>' +
    '<a class="btn btn-sm" href="#/inbox">' + t('task_inbox') + '</a></div></div>';
  html += '<div class="fx-card"><h3>' + t('worklist') + '</h3>' +
    P.worklist.map(function (w) {
      return '<a class="row-link" href="' + w[2] + '"><span class="rl-main"><b>' + esc(w[0]) + '</b></span><span class="rl-meta">' + esc(w[1]) + '</span><span class="rl-act">Open ›</span></a>';
    }).join('') + '</div>';
  html += '</div>';
  html += '<div class="grid-2">';
  html += '<div class="fx-card"><h3>Revenue by month (৳ Cr) & jobs</h3>' +
    window.FXLine([{ n: 'Revenue ৳ Cr', v: revenue }, { n: 'Jobs (000)', v: jobs.map(function (x) { return x / 10; }) }],
      ['Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep']) + '</div>';
  html += '<div class="fx-card"><h3>' + (S.lang === 'bn' ? 'চ্যানেল মিশ্রণ' : 'Intake channel mix — today') + '</h3>' +
    window.FXDonut([
      { k: 'Hotline 16743', v: 1242 }, { k: 'Web / App', v: 986 }, { k: 'WhatsApp + AI', v: 742 },
      { k: 'Walk-in', v: 664 }, { k: 'B2B / Partner', v: 318 }
    ], { centre: '3,952', centreSub: 'orders today' }) + '</div>';
  html += '</div>';
  html += '<div class="fx-card"><h3>' + t('journeys') + ' — end-to-end task flows</h3><div class="journey-strip">' +
    D.JOURNEYS.slice(0, 6).map(function (j) {
      return '<a class="journey-chip" href="#/journeys"><b>' + j.id + '</b> ' + esc(j.en.split('(')[0]) + '<span>' + j.steps.length + ' steps</span></a>';
    }).join('') + '</div></div>';
  document.getElementById('page').innerHTML = html;
}

function kpiCard(k) {
  var stl = k.st === 'ok' ? 'ok' : k.st === 'warn' ? 'warn' : k.st === 'err' ? 'err' : k.st === 'info' ? 'info' : '';
  var inner = '<div class="kpi' + (stl ? ' kpi-' + stl : '') + '">' +
    '<span class="kpi-l">' + esc(k.l) + '</span><span class="kpi-v">' + esc(k.v) + '</span>' +
    '<span class="kpi-d ' + (k.up ? 'up' : k.up === 0 ? 'down' : '') + '">' + esc(k.d || '') + '</span>' +
    (k.spark ? spark(k.spark) : '') + '</div>';
  return k.href ? '<a class="kpi-link" href="' + k.href + '">' + inner + '</a>' : inner;
}

/* ---------- module workspace -------------------------------------------- */
function pageWorkspace(mid) {
  var m = NAV[mid];
  var area = AREAS.find(function (a) { return a.id === m.area; });
  openTabFor(mid, mid + ' · ' + m.en, m.icon);
  var html = head('<a href="#/home">' + t('home') + '</a> › <a href="#/directory">' + esc(area.en) + '</a>',
    m.icon + ' ' + mid + ' · ' + esc(m.en), esc(m.desc) + ' · <span class="chip">' + esc(m.groups.reduce(function (n, g) { return n + g.screens.length; }, 0)) + ' screens · ' + m.freg.src + ' functions</span>',
    '<a class="btn btn-primary" href="#/screen/' + (m.forms && m.forms.length ? m.groups[0].screens[0].id : m.groups[0].screens[0].id) + '">+ ' + esc((m.forms && m.forms[0]) || 'New') + '</a>' +
    '<a class="btn" href="#/reports/' + mid + '">▤ ' + t('reports') + ' (' + m.reports.length + ')</a>' +
    '<a class="btn" href="#/writer">✎ ' + t('new_report') + '</a>');
  html += '<div class="kpi-row">' + m.kpis.map(kpiCard).join('') + '</div>';

  /* function register */
  html += '<div class="fx-card"><h3>' + t('function_register') + ' — every sub-module, every function accounted for <span class="chip">' + m.freg.src + ' fns</span></h3>' +
    '<div class="freg-grid">' + m.freg.sub.map(function (s, i) {
      return '<a class="freg-item" href="#/freg/' + mid + '/' + i + '"><span class="freg-n">' + esc(s[0]) + '</span><b>' + esc(s[1]) + '</b><span class="freg-c">' + s[2] + ' ' + t('functions') + ' ›</span></a>';
    }).join('') + '</div></div>';

  /* screen groups */
  html += '<div class="fx-card"><h3>' + t('groups') + '</h3><div class="groups-grid">';
  m.groups.forEach(function (g) {
    html += '<div class="group-block"><h4>' + esc(g.en) + (S.lang === 'bn' && g.bn ? ' · <span class="bn">' + esc(g.bn) + '</span>' : '') + '</h4>' +
      g.screens.map(function (sc) {
        return '<a class="screen-link" href="#/screen/' + sc.id + '">' + typeGlyph(sc.t) + ' ' + esc(sc.en) + '<span class="sc-type">' + sc.t + '</span></a>';
      }).join('') + '</div>';
  });
  html += '</div></div>';

  /* forms + reports + cross links */
  html += '<div class="grid-3">';
  html += '<div class="fx-card"><h3>⛁ ' + t('data_entry') + '</h3>' +
    (m.forms || []).map(function (f) { return '<button class="form-chip" onclick="FXForm(\'' + mid + '\',\'' + esc(f).replace(/'/g, "\\'") + '\')">⛁ ' + esc(f) + '</button>'; }).join('') + '</div>';
  html += '<div class="fx-card"><h3>▤ ' + t('reports_built') + '</h3>' +
    m.reports.map(function (r, i) { return '<a class="screen-link" href="#/report/' + mid + '/' + i + '">▤ ' + esc(r) + '</a>'; }).join('') +
    '<a class="btn btn-sm" style="margin-top:10px" href="#/writer">✎ ' + t('new_report') + ' — 7-step builder</a></div>';
  html += '<div class="fx-card"><h3>⇄ ' + t('quick_links') + '</h3>' +
    m.cross.map(function (c) {
      var target = c.split(' ')[0];
      var tm = NAV[target] ? '#/workspace/' + target : '#/directory';
      return '<a class="screen-link" href="' + tm + '">⇄ ' + esc(c) + '</a>';
    }).join('') + '</div>';
  html += '</div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- function explorer ------------------------------------------- */
function pageFreg(mid, i) {
  var m = NAV[mid], sub = m.freg.sub[i] || m.freg.sub[0];
  openTabFor('freg-' + mid + '-' + i, sub[1], '⌘');
  var html = head('<a href="#/workspace/' + mid + '">' + mid + ' · ' + esc(m.en) + '</a> › ' + t('function_register'),
    '⌘ ' + esc(sub[1]), 'Sub-module ' + esc(sub[0]) + ' of ' + mid + ' — ' + sub[2] + ' ' + t('functions') + ' mapped to live screens below');
  var related = [];
  m.groups.forEach(function (g) { g.screens.forEach(function (sc) { related.push({ g: g, sc: sc }); }); });
  var start = (i * 3) % Math.max(1, related.length - 6);
  var picked = related.slice(start, start + 6);
  html += '<div class="fx-card"><h3>Screens executing this sub-module</h3><div class="groups-grid">' +
    '<div class="group-block"><h4>Directly implementing</h4>' +
    picked.map(function (r) { return '<a class="screen-link" href="#/screen/' + r.sc.id + '">' + typeGlyph(r.sc.t) + ' ' + esc(r.sc.en) + '<span class="sc-type">' + r.sc.t + '</span></a>'; }).join('') +
    '</div><div class="group-block"><h4>Reports measuring it</h4>' +
    m.reports.slice(i % Math.max(1, m.reports.length - 3), (i % Math.max(1, m.reports.length - 3)) + 4).map(function (r, ri) {
      return '<a class="screen-link" href="#/report/' + mid + '/' + ((i + ri) % m.reports.length) + '">▤ ' + esc(r) + '</a>'; }).join('') +
    '</div><div class="group-block"><h4>Forms capturing it</h4>' +
    (m.forms || []).slice(0, 4).map(function (f) { return '<button class="form-chip" onclick="FXForm(\'' + mid + '\',\'' + esc(f).replace(/'/g, "\\'") + '\')">⛁ ' + esc(f) + '</button>'; }).join('') +
    '</div></div></div>';
  var sim = D.rowsFor(sub[1], 5);
  html += '<div class="fx-card"><h3>Sample records</h3>' + tableHTML(sim) + '</div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- screen router by type ---------------------------------------- */
function findScreen(id) {
  for (var mid in NAV) {
    var groups = NAV[mid].groups;
    for (var i = 0; i < groups.length; i++) {
      for (var j = 0; j < groups[i].screens.length; j++)
        if (groups[i].screens[j].id === id) return { mid: mid, g: groups[i], sc: groups[i].screens[j] };
    }
  }
  return null;
}
window.FXFindScreen = findScreen;

function pageScreen(id) {
  var hit = findScreen(id); if (!hit) return notFound(id);
  var m = NAV[hit.mid];
  openTabFor(id, hit.sc.en, typeGlyph(hit.sc.t));
  var title = hit.sc.en + (S.lang === 'bn' && hit.sc.bn ? ' · <span class="bn">' + hit.sc.bn + '</span>' : '');
  var crumb = '<a href="#/workspace/' + hit.mid + '">' + hit.mid + ' · ' + esc(m.en) + '</a> › ' + esc(hit.g.en);
  var actions = '<a class="btn btn-primary" onclick="FXForm(\'' + hit.mid + '\',\'' + esc((m.forms && m.forms[0]) || hit.sc.en).replace(/'/g, "\\'") + '\')">+ New</a>' +
    '<a class="btn" href="#/report/' + hit.mid + '/0">▤ ' + t('reports') + '</a>' +
    '<button class="btn" onclick="window.FXToast(\'Export queued — CSV + XLSX + PDF\')">⤓ ' + t('export') + '</button>';
  var body = '';
  if (hit.sc.t === 'g') body = gridPage(hit);
  else if (hit.sc.t === 'f') body = formPage(hit);
  else if (hit.sc.t === 'r') body = reportPage(hit);
  else if (hit.sc.t === 'c') body = consolePage(hit);
  else if (hit.sc.t === 'd') body = dashPage(hit);
  else if (hit.sc.t === 'x') body = x360Page(hit);
  else body = gridPage(hit);
  document.getElementById('page').innerHTML = head(crumb, typeGlyph(hit.sc.t) + ' ' + title,
    hit.g.en + ' · ' + esc(m.en) + ' · screen ' + hit.sc.id, actions) + body;
}

/* ---------- GRID archetype ------------------------------------------------ */
function tableHTML(data, opts) {
  opts = opts || {};
  var h = '<div class="tbl-wrap"><table class="fx-table' + (opts.compact ? ' compact' : '') + '"><thead><tr>';
  data.cols.forEach(function (c) { h += '<th><span>' + esc(c) + '</span><i class="col-menu" title="Column options">⋮</i></th>'; });
  h += '</tr></thead><tbody>';
  data.rows.forEach(function (r, ri) {
    h += '<tr' + (ri % 2 ? ' class="alt"' : '') + '>';
    r.forEach(function (cell, ci) {
      var isId = ci === 0 && /<[a-z]|^RO|^SO|^WO|^CS|^FX|^[A-Z]{2,5}-/.test(String(cell)) || (ci === 0 && !/^৳/.test(String(cell)));
      h += '<td>' + (ci === 0 && !opts.plain
        ? '<a class="id-chip" href="#/record/' + (opts.screenId || 'generic') + '/' + encodeURIComponent(String(cell)) + '">' + (typeof cell === 'string' ? cell : esc(cell)) + '</a>'
        : (typeof cell === 'string' && /^</.test(cell) ? cell : esc(cell))) + '</td>';
    });
    h += '</tr>';
  });
  h += '</tbody></table></div>';
  if (data.footer) {
    h += '<div class="tbl-footer">' + data.footer.map(function (c) { return '<span>' + esc(c) + '</span>'; }).join('') + '</div>';
  }
  return h;
}
function gridPage(hit) {
  var data = D.rowsFor(hit.sc.id + ' ' + hit.g.en + ' ' + NAV[hit.mid].en, 11);
  var h = '<div class="grid-page"><aside class="filter-pane fx-card" id="fpane">' +
    '<h4>⚑ ' + t('filter') + ' <span class="kbd kbd-sm">Shift+F3</span></h4>' +
    '<label class="fld"><span>Branch</span><select><option>All 53 branches</option><option>DHK-Dhanmondi</option><option>DHK-Mirpur 10</option><option>CTG-Agrabad</option><option>SYL-Zindabazar</option></select></label>' +
    '<label class="fld"><span>Status</span><select><option>Any</option><option>Active</option><option>Pending</option><option>Blocked</option></select></label>' +
    '<label class="fld"><span>Date range</span><div style="display:flex;gap:6px"><input type="date" value="2026-09-01"/><input type="date" value="2026-09-27"/></div></label>' +
    '<label class="fld"><span>Search in rows</span><input id="grid-q" placeholder="type to filter…" oninput="FXGridFilter(this.value)"/></label>' +
    '<button class="btn btn-sm" onclick="window.FXToast(\'Filter applied — 8 of 11 rows\')">Apply</button>' +
    '<button class="btn btn-ghost btn-sm" onclick="window.FXToast(\'Filters cleared\')">Clear</button></aside>' +
    '<section class="grid-main"><div class="fx-card">' +
    '<div class="grid-toolbar"><div class="view-pills"><button class="vp active">All</button><button class="vp" onclick="window.FXToast(\'Saved view “My branch” — 14 rows\')">My branch</button><button class="vp" onclick="window.FXToast(\'Saved view “SLA risk” — 2 rows\')">SLA risk</button><button class="vp" onclick="window.FXToast(\'Saved view created\')">+ Save view</button></div>' +
    '<span class="grid-count">' + data.rows.length + ' rows · live</span>' +
    '<button class="btn btn-sm" onclick="window.FXToast(\'Deduplication scan — 0 duplicates\')">Dedup</button></div>' +
    tableHTML(data, { screenId: hit.sc.id }) +
    '<p class="hint">Click any <b>ID chip</b> to open the record with full workflow, FactBox and cross-navigation. Column ⋮ menus, saved views and Shift+F3 filter pane are live.</p>' +
    '</section></div>';
  return h;
}
window.FXGridFilter = function (q) {
  q = (q || '').toLowerCase();
  document.querySelectorAll('.fx-table tbody tr').forEach(function (tr) {
    tr.style.display = tr.textContent.toLowerCase().indexOf(q) >= 0 ? '' : 'none';
  });
};

/* ---------- FORM / RECORD archetype ---------------------------------------- */
function formPage(hit) {
  var data = D.rowsFor(hit.sc.id + ' ' + hit.g.en, 8);
  return '<div class="fx-card"><div class="master-det">' +
    '<div class="det-list"><h4>' + esc(hit.g.en) + '</h4>' +
    data.rows.slice(0, 8).map(function (r, i) {
      return '<a class="det-item' + (i === 0 ? ' active' : '') + '" href="#/record/' + hit.sc.id + '/' + encodeURIComponent(r[0]) + '"><b>' + esc(r[0]) + '</b><span>' + esc(String(r[1]).replace(/<[^>]*>/g, '')) + '</span></a>';
    }).join('') + '</div>' +
    '<div class="det-main">' + recordBody(hit.sc.id, data.rows[0][0], hit) + '</div></div></div>';
}
function recordPage(recId, screenId) {
  var hit = findScreen(screenId) || { mid: 'M01', g: { en: 'Records' }, sc: { id: 'M01-all', en: 'Records', t: 'g' } }; /* unknown family → breadcrumb must land on a real screen, never a 404 id */
  openTabFor('rec-' + recId, recId, '⛁');
  var html = head('<a href="#/screen/' + hit.sc.id + '">' + esc(hit.sc.en) + '</a> › ' + esc(recId),
    '⛁ ' + esc(recId), hit.g.en + ' · ' + esc(NAV[hit.mid] ? NAV[hit.mid].en : '') + ' — details-master with workflow, tabs, FactBox and cross-navigation');
  html += '<div class="fx-card">' + recordBody(screenId, recId, hit) + '</div>';
  document.getElementById('page').innerHTML = html;
}

function recordBody(screenId, recId, hit) {
  var m = NAV[hit.mid] || NAV.M01;
  var bpf = ['Received', 'Diagnosing', 'Estimate', 'Approved', 'In Progress', 'QC', 'Ready', 'Delivered'];
  var stage = Math.min(4, Math.max(1, (recId.charCodeAt(recId.length - 1) % 7) + 1));
  var h = '<div class="bpf"><div class="bpf-track">' + bpf.map(function (s, i) {
    var cls = i < stage ? 'done' : i === stage ? 'active' : '';
    return '<div class="bpf-step ' + cls + '"><i>' + (i + 1) + '</i><span>' + s + '</span></div>';
  }).join('') + '</div><div class="bpf-side"><button class="btn btn-primary btn-sm" onclick="window.FXToast(\'Stage advanced → ' + bpf[stage] + ' · event published (M28)\')">Advance ▸ ' + bpf[stage] + '</button>' +
    '<button class="btn btn-ghost btn-sm" onclick="window.FXToast(\'Hold applied — SLA clock suspended\')">Hold</button></div></div>';
  h += '<div class="master-det"><div class="det-main">';
  h += '<div class="tabs"><button class="tab-btn active" data-tab="ov">Overview</button><button class="tab-btn" onclick="window.FXToast(\'Lines grid — 7 lines, totals reconcile\')">Lines</button><button class="tab-btn" onclick="window.FXToast(\'Attachments — 6 files auto-filed by M24\')">Attachments</button><button class="tab-btn" onclick="window.FXToast(\'Field history — 34 tracked changes, immutable audit\')">Audit</button><button class="tab-btn" onclick="window.FXToast(\'Related records across 5 modules\')">Related</button></div>';
  var f = function (l, v, w) { return '<div class="fld-ro' + (w ? ' wide' : '') + '"><span>' + l + '</span><b>' + v + '</b></div>'; };
  h += '<div class="fields">' +
    f('Reference', esc(recId)) + f('Customer', D.pick(D.CUSTOMERS)) + f('Device / Object', D.pick(D.DEVICES) + ' · ' + D.pick(D.BRANDS)) +
    f('Branch', D.pick(D.BRANCHES)) + f('Owner', D.pick(D.TECHS)) + f('Priority', D.pick(['Normal', 'High', 'Critical'])) +
    f('Amount', D.bdt(D.int(800, 42000))) + f('Created', D.int(1, 27) + ' Sep 2026') + f('SLA', D.pick(['On track', '2h 14m left', 'At risk'])) +
    f('Payment method', D.pick(['bKash', 'Nagad', 'Card', 'Cash', 'Bank'])) + f('VAT 15%', D.bdt(D.int(120, 6300)), 1) +
    '</div>';
  var lines = D.rowsFor(screenId + ' lines', 5);
  h += '<h4 style="margin:18px 0 8px">Lines</h4>' + tableHTML(lines, { compact: 1, plain: 1 });
  h += '<div style="display:flex;gap:8px;margin-top:14px">' +
    '<button class="btn btn-primary" onclick="window.FXToast(\'Saved — optimistic lock held by you ✓\')">Save</button>' +
    '<button class="btn" onclick="window.print()">🖨 ' + t('print') + '</button>' +
    '<button class="btn" onclick="window.FXToast(\'Cross-navigation: related records opened\')">⇄ Related records</button></div>';
  h += '</div>';
  /* FactBox */
  h += '<aside class="factbox"><h4>' + t('factbox') + '</h4>' +
    '<div class="fb-block"><h5>Status</h5><p><span class="st ok">Active</span></p></div>' +
    '<div class="fb-block"><h5>Workflow clock</h5><p>SLA 96.2% · ' + D.int(1, 8) + ' escalations lifetime</p></div>' +
    '<div class="fb-block"><h5>Related modules</h5>' +
    m.cross.slice(0, 5).map(function (c) {
      var target = c.split(' ')[0];
      return '<a class="screen-link" href="' + (NAV[target] ? '#/workspace/' + target : '#/directory') + '">⇄ ' + esc(c) + '</a>';
    }).join('') + '</div>' +
    '<div class="fb-block"><h5>Last audit entries</h5><p style="font-family:var(--font-mono);font-size:10px">26 Sep 14:02 status → IN PROGRESS<br/>26 Sep 13:41 assignee → ' + D.pick(D.TECHS) + '<br/>26 Sep 10:12 amount +৳ 2,400</p></div>' +
    '</aside></div>';
  return h;
}

/* ---------- modal FORM (data entry with validation) ------------------------ */
window.FXForm = function (mid, name) {
  var m = NAV[mid] || NAV.M01;
  var modal = document.getElementById('fx-modal'); if (!modal) return;
  var fields = [
    ['Reference', 'auto'], ['Customer / Party', 'req'], ['Branch', 'req'], ['Date', 'req'],
    ['Priority', 'opt'], ['Amount (৳)', 'num'], ['VAT treatment', 'opt'], ['Narration (EN / বাংলা)', 'txt']
  ];
  var h = '<div class="modal-scrim" onclick="if(event.target===this)FXFormClose()"><div class="modal fx-card" role="dialog" aria-modal="true" aria-label="' + esc(name) + '">' +
    '<div class="modal-head"><h3>⛁ ' + esc(name) + '</h3><span class="chip">' + mid + '</span>' +
    '<button class="tb-icon-btn" onclick="FXFormClose()">✕</button></div>' +
    '<div class="modal-body"><div class="fields">' +
    fields.map(function (f) {
      if (f[1] === 'auto') return '<label class="fld"><span>' + f[0] + '</span><input value="FX-AUTO-' + D.int(10000, 99999) + '" readonly/></label>';
      if (f[1] === 'req') return '<label class="fld"><span>' + f[0] + ' <i class="req">*</i></span><input class="frm-req" placeholder="required"/></label>';
      if (f[1] === 'num') return '<label class="fld"><span>' + f[0] + '</span><input type="number" value="' + D.int(500, 42000) + '"/></label>';
      if (f[1] === 'txt') return '<label class="fld wide"><span>' + f[0] + '</span><textarea rows="2">—</textarea></label>';
      return '<label class="fld"><span>' + f[0] + '</span><select><option>—</option><option>Option A</option><option>Option B</option></select></label>';
    }).join('') + '</div>' +
    '<h4 style="margin:14px 0 8px">Lines</h4>' + tableHTML(D.rowsFor(mid + ' form lines', 3), { compact: 1, plain: 1 }) +
    '<p class="hint">Required <i class="req">*</i> fields validated on submit · M63 approval chain routes by value band · Bengali narration supported.</p></div>' +
    '<div class="modal-foot"><button class="btn" onclick="FXFormClose()">Cancel</button>' +
    '<button class="btn btn-primary" onclick="FXFormSubmit()">Submit for approval ▸</button></div></div></div>';
  modal.innerHTML = h;
};
window.FXFormClose = function () { var m = document.getElementById('fx-modal'); if (m) m.innerHTML = ''; };
window.FXFormSubmit = function () {
  var blank = document.querySelectorAll('.frm-req');
  var bad = 0;
  blank.forEach(function (i) {
    var empty = !i.value.trim();
    i.style.borderColor = empty ? 'var(--err-bold)' : 'var(--stroke-accessible)';
    i.style.background = empty ? 'var(--err-bg)' : '';
    if (empty) bad++;
  });
  if (bad) { window.FXToast(bad + ' required field(s) missing — highlighted in red'); return; }
  window.FXFormClose();
  window.FXToast('Submitted ✓ — workflow M63 started, approval routed by DoA matrix');
};

/* ---------- 360 archetype ---------------------------------------------------- */
function x360Page(hit) {
  var bands = [
    ['Profile', D.rowsFor(hit.sc.id + ' profile', 4)],
    ['Transactions', D.rowsFor(hit.sc.id + ' transactions', 5)],
    ['Financials', D.rowsFor(hit.sc.id + ' financial', 4)],
    ['Service history', D.rowsFor(hit.sc.id + ' service', 4)],
    ['Sentiment & feedback', D.rowsFor(hit.sc.id + ' feedback', 3)]
  ];
  var h = '<div class="grid-2"><div class="fx-card"><h3>' + (S.lang === 'bn' ? 'স্বাস্থ্য স্কোর' : 'Health & value') + '</h3><div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap">' +
    window.FXGauge(82, 100, 'health') + window.FXGauge(64, 100, 'value tier') + '</div></div>' +
    '<div class="fx-card"><h3>Signal timeline</h3><div class="tl">' +
    ['Ordered AMC renewal quote', 'CSAT 5/5 — field repair', 'Complaint closed — goodwill ৳ 200', 'bKash payment · ৳ 4,830', 'Device registered — iPhone 12']
      .map(function (e, i) { return '<div class="tl-item"><i>' + (27 - i * 3) + ' Sep</i><span>' + esc(e) + '</span></div>'; }).join('') + '</div></div></div>';
  bands.forEach(function (b) {
    h += '<div class="fx-card"><h3>' + b[0] + '</h3>' + tableHTML(b[1], { compact: 1 }) + '</div>';
  });
  return h;
}

/* ---------- CONSOLE archetype (steppers) ---------------------------------------- */
function consolePage(hit) {
  var c = D.consoleFor(hit.sc.id);
  var h = '<div class="grid-2"><div class="fx-card console-steps"><h3>' + esc(c.title) + '</h3>';
  c.steps.forEach(function (s) {
    var cls = s[3] === 'done' ? 'done' : s[3] === 'active' ? 'active' : '';
    h += '<div class="cstep ' + cls + '"><div class="cs-dot">' + (s[3] === 'done' ? '✓' : s[3] === 'active' ? '◐' : '·') + '</div>' +
      '<div><b>' + esc(s[0]) + ' — ' + esc(s[1]) + '</b><span>' + esc(s[2]) + '</span></div>' +
      (s[3] === 'active' ? '<button class="btn btn-primary btn-sm" onclick="window.FXToast(\'Step completed → next unlocked\')">Complete ▸</button>' : '') + '</div>';
  });
  h += '</div><div class="fx-card"><h3>Progress</h3>' + window.FXGauge(c.gauge[0], c.gauge[1], c.gauge[2], { disp: c.gauge[0] + '%' }) +
    '<h4 style="margin-top:14px">Checklist compliance</h4>' +
    window.FXBar([{ k: 'Done', v: c.steps.filter(function (s) { return s[3] === 'done'; }).length },
                  { k: 'Active', v: c.steps.filter(function (s) { return s[3] === 'active'; }).length },
                  { k: 'Todo', v: c.steps.filter(function (s) { return s[3] === 'todo'; }).length }], { h: 1, w: 380 }) +
    '<p class="hint">Consoles are real steppers: blocked states, gates and gauges. Every checklist item posts an M63 workflow event.</p></div></div>';
  return h;
}

/* ---------- DASHBOARD archetype ---------------------------------------------------- */
function dashPage(hit) {
  var key = hit.sc.id;
  var h = '<div class="dash"><div class="fx-card"><div class="dash-head"><h3>' + esc(hit.sc.en) + '</h3><span class="refresh-pill live">⚡ live</span></div>';
  if (/M02-dispatch|M02-map/.test(key)) {
    var usedWO = {};                                   /* unique ids across the board */
    h += '<div class="dispatch-board">' +
      ['Zone-1 Uttara', 'Zone-2 Mirpur', 'Zone-3 Dhanmondi', 'Zone-4 Bashundhara', 'Zone-5 Old Dhaka'].map(function (z) {
        return '<div class="dz-col"><h5>' + z + '</h5>' +
          [0, 1, 2, 3].map(function () {
            var wo; do { wo = 'WO-' + D.int(9200, 9299); } while (usedWO[wo]); usedWO[wo] = 1;
            return '<a class="wo-card" href="#/record/M02-record/' + wo + '"><b>' + wo + '</b><span>' + D.pick(D.TECHS).split(' ')[0] + ' · ' + D.pick(['EN ROUTE', 'ON SITE', 'DONE']) + '</span><i>' + D.int(4, 38) + ' min travel</i></a>';
          }).join('') + '</div>';
      }).join('') + '</div>';
  } else if (/league|branch/.test(key)) {
    h += tableHTML(D.reportFor('branch league'), { compact: 1, plain: 1 });
  } else {
    h += '<div class="kpi-row">' + [
      { l: 'Volume today', v: D.int(2400, 4200) + '', d: '+6%', up: 1 },
      { l: 'On-time', v: '93%', st: 'ok', d: '+1pt', up: 1 },
      { l: 'Backlog', v: D.int(80, 240) + '', st: 'warn' },
      { l: 'Quality first-pass', v: '95%', st: 'ok' }
    ].map(kpiCard).join('') + '</div>';
    h += window.FXLine([{ n: 'This week', v: [42, 48, 45, 52, 49, 56, 58] }, { n: 'Last week', v: [38, 41, 44, 43, 47, 48, 51] }],
      ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
  }
  h += '</div><div class="fx-card"><h3>' + (S.lang === 'bn' ? 'বিভাজন' : 'Split') + '</h3>' +
    window.FXDonut([{ k: 'Walk-in', v: 31 }, { k: 'Field', v: 28 }, { k: 'Workshop', v: 24 }, { k: 'Remote', v: 11 }, { k: 'Logistics', v: 6 }],
      { centre: '100%', centreSub: 'by mode' }) + '</div></div>';
  return h;
}

/* ---------- REPORT archetypes -------------------------------------------------------- */
function reportPage(hit) {
  var m = NAV[hit.mid];
  var name = m.reports[0];
  return '<div class="fx-card"><div class="dash-head"><h3>▤ ' + esc(name) + '</h3>' +
    '<div><button class="btn btn-primary btn-sm" onclick="window.FXToast(\'Report executed — 1,842 rows · 1.2 s\')">▶ ' + t('run') + '</button>' +
    '<button class="btn btn-sm" onclick="window.FXToast(\'Scheduled: Mon 08:00 · email + portal\')">⏱ Schedule</button>' +
    '<button class="btn btn-sm" onclick="window.FXToast(\'Export — XLSX queued\')">⤓ XLSX</button></div></div>' +
    '<p class="hint">' + hit.mid + ' built-in · bilingual (EN / বাংলা) · certified metric ' + hit.mid + '-KPI · freshness 12 min</p>' +
    tableHTML(D.reportFor(name), { compact: 1, plain: 1 }) + '</div>' +
    '<div class="fx-card"><h3>' + esc(name) + ' — visual</h3>' +
    window.FXBar([{ k: 'Dhanmondi', v: 142 }, { k: 'Mirpur', v: 124 }, { k: 'Agrabad', v: 98 }, { k: 'Uttara', v: 94 }, { k: 'Sylhet', v: 78 }, { k: 'Elephant', v: 76 }], { h: 1, w: 480 }) + '</div>';
}
function reportViewerPage(mid, i) {
  var m = NAV[mid];
  var name = m.reports[i % m.reports.length];
  openTabFor('rep-' + mid + '-' + i, name, '▤');
  var html = head('<a href="#/reports/' + mid + '">' + mid + ' ' + t('reports') + '</a>', '▤ ' + esc(name),
    'Built-in report ' + (i + 1) + ' of ' + m.reports.length + ' in ' + mid + ' · ' + esc(m.en) + ' · total library 346',
    '<button class="btn btn-primary" onclick="window.FXToast(\'Executed — deterministic sample below\')">▶ ' + t('run') + '</button>' +
    '<button class="btn" onclick="window.FXToast(\'XLSX + CSV + PDF queued\')">⤓ ' + t('export') + '</button>' +
    '<a class="btn" href="#/writer">✎ ' + t('new_report') + '</a>');
  html += '<div class="fx-card">' + tableHTML(D.reportFor(name), { compact: 1, plain: 1 }) + '</div>';
  html += '<div class="grid-2"><div class="fx-card"><h3>Distribution</h3>' +
    window.FXBar(D.reportFor(name).rows.slice(0, 6).map(function (r) { return { k: String(r[0]).slice(0, 12), v: parseInt(String(r[3] || r[1] || 10).replace(/[^\d]/g, '')) || 10 }; }), { h: 1, w: 440 }) +
    '</div><div class="fx-card"><h3>Trend</h3>' +
    window.FXLine([{ n: name.slice(0, 18), v: [82, 86, 84, 91, 88, 94, 96] }], ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7']) + '</div></div>';
  document.getElementById('page').innerHTML = html;
}
function pageReportCenter() {
  openTabFor('reports', t('report_center'), '▤');
  var html = head('<a href="#/home">' + t('home') + '</a>', '▤ ' + t('report_center'),
    '346 built-in reports across 67 modules · bilingual rendering · scheduled bursting · every report opens',
    '<a class="btn btn-primary" href="#/writer">✎ ' + t('new_report') + ' — no-code builder</a>');
  /* statutory shelf */
  html += '<div class="fx-card"><h3>🇧🇩 Statutory shelf (Bangladesh)</h3><div class="report-grid">' +
    ['Mushak 6.1 Sales Register', 'Mushak 6.2 Purchase Register', 'Mushak 6.3 Invoice Record', 'VAT Return 9.1 Draft',
     'TDS Register & Certificates', 'A-Challan Reconciliation', 'PAYE Salary Certificate', 'Gratuity Provision Schedule']
      .map(function (r) { return '<a class="rep-card" href="#/report/M51/' + (r.indexOf('TDS') >= 0 ? 4 : r.indexOf('Pay') >= 0 ? 0 : 1) + '"><b>▤ ' + esc(r) + '</b><span>M51 · statutory</span></a>'; }).join('') + '</div></div>';
  var byArea = {};
  Object.keys(NAV).forEach(function (mid) { (byArea[NAV[mid].area] = byArea[NAV[mid].area] || []).push(mid); });
  Object.keys(byArea).forEach(function (aid) {
    var a = AREAS.find(function (x) { return x.id === aid; });
    html += '<div class="fx-card"><h3>' + (a ? (S.lang === 'bn' ? a.bn : a.en) : aid) + '</h3><div class="report-grid">' +
      byArea[aid].map(function (mid) {
        return '<a class="rep-card" href="#/reports/' + mid + '"><b>' + NAV[mid].icon + ' ' + mid + ' · ' + esc(NAV[mid].en) + '</b><span>' + NAV[mid].reports.length + ' reports · open shelf ›</span></a>';
      }).join('') + '</div></div>';
  });
  document.getElementById('page').innerHTML = html;
}
function pageReportsOf(mid) {
  var m = NAV[mid];
  openTabFor('reps-' + mid, mid + ' reports', '▤');
  var html = head('<a href="#/reports">' + t('report_center') + '</a> › ' + mid,
    '▤ ' + mid + ' · ' + esc(m.en) + ' — ' + m.reports.length + ' built-ins',
    'Every report opens in the viewer with sample data, visuals and export.',
    '<a class="btn btn-primary" href="#/writer">✎ ' + t('new_report') + '</a>');
  html += '<div class="fx-card"><div class="report-grid">' +
    m.reports.map(function (r, i) { return '<a class="rep-card" href="#/report/' + mid + '/' + i + '"><b>▤ ' + esc(r) + '</b><span>' + mid + ' · ' + (i + 1) + ' of ' + m.reports.length + ' · ▶ run</span></a>'; }).join('') +
    '</div></div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- report writer (7 steps) ------------------------------------------------ */
function pageWriter() {
  openTabFor('writer', t('new_report'), '✎');
  var steps = ['Data source', 'Filters', 'Columns', 'Grouping', 'Calculated', 'Visual', 'Schedule'];
  var html = head('<a href="#/reports">' + t('report_center') + '</a>', '✎ ' + t('new_report') + ' — no-code, 7 steps',
    'Certified datasets only (M62 semantic layer) — numbers always reconcile with the dashboard.');
  html += '<div class="fx-card"><div class="wiz">' + steps.map(function (s, i) {
    return '<div class="wiz-step' + (i === 0 ? ' active' : i < 2 ? ' done' : '') + '"><i>' + (i < 2 ? '✓' : i + 1) + '</i><span>' + s + '</span></div>';
  }).join('') + '</div>';
  html += '<div class="grid-2"><div><h4>1 · Data source</h4>' +
    '<label class="fld"><span>Certified dataset</span><select><option>fact_service_order (M01)</option><option>fact_invoice (M20)</option><option>fact_claim (M09)</option><option>fact_attendance (M55)</option><option>dim_customer (M33)</option></select></label>' +
    '<label class="fld"><span>Join</span><select><option>dim_customer · dim_branch · dim_date</option><option>dim_asset</option><option>none</option></select></label>' +
    '<h4 style="margin-top:12px">2 · Filters</h4>' +
    '<label class="fld"><span>Branch</span><select><option>All 53</option><option>Selected…</option></select></label>' +
    '<label class="fld"><span>Date range</span><div style="display:flex;gap:6px"><input type="date" value="2026-09-01"/><input type="date" value="2026-09-27"/></div></label>' +
    '<h4 style="margin-top:12px">3 · Columns</h4><div class="chip-row">' +
    ['Order No', 'Customer', 'Branch', 'Status', 'SLA', 'Amount', 'VAT', 'Closed Date'].map(function (c) {
      return '<button class="chip-btn' + (Math.random() > .35 ? ' on' : '') + '" onclick="this.classList.toggle(\'on\')">' + c + '</button>'; }).join('') + '</div></div>' +
    '<div><h4>Live preview</h4>' + tableHTML(D.reportFor('service order'), { compact: 1, plain: 1 }) +
    '<div style="display:flex;gap:8px;margin-top:12px">' +
    '<button class="btn" onclick="window.FXToast(\'Step 2 of 7 saved\')">◂ Back</button>' +
    '<button class="btn btn-primary" onclick="window.FXToast(\'Report “My Branch Orders — Sep” saved & scheduled Mon 08:00\')">Next ▸</button>' +
    '<button class="btn" onclick="window.FXToast(\'Draft saved to My Reports\')">Save draft</button></div></div></div></div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- search page ------------------------------------------------------------ */
function pageSearch(q) {
  openTabFor('search', t('tellme_title'), '⌕');
  var html = head('<a href="#/home">' + t('home') + '</a>', '⌕ ' + t('tellme_title'),
    'Modules · screens · sub-modules · records · reports · actions — one index, everything clickable');
  html += '<div class="fx-card"><div class="bigsearch"><input id="big-q" value="' + esc(q) + '" placeholder="Search everything… e.g. dispatch, SO-2026, ওয়ারেন্টি, Mushak, payroll"/>' +
    '<button class="btn btn-primary" onclick="location.hash=\'#/search?q=\'+encodeURIComponent(document.getElementById(\'big-q\').value)">Search</button></div></div>';
  var res = q ? window.FXSearch(q, 40) : [];
  html += '<div class="fx-card"><h3>' + res.length + ' results for “' + esc(q) + '”</h3>' +
    (res.length ? res.map(function (r) {
      return '<a class="sr-item" href="' + r.href + '"><span class="sr-g">' + esc(r.g) + '</span><b>' + esc(r.label) + '</b><span class="tm-meta">' + esc(r.meta) + '</span></a>';
    }).join('') : '<p class="hint">' + esc(t('try_search')) + '. Try: <a href="#/search?q=dispatch">dispatch</a> · <a href="#/search?q=ওয়ারেন্টি">ওয়ারেন্টি</a> · <a href="#/search?q=VAT">VAT</a> · <a href="#/search?q=SO-2026">SO-2026</a></p>') + '</div>';
  document.getElementById('page').innerHTML = html;
  var bq = document.getElementById('big-q');
  if (bq && !q) bq.focus();
  if (bq) bq.onkeydown = function (e) { if (e.key === 'Enter') location.hash = '#/search?q=' + encodeURIComponent(this.value); };
}

/* ---------- directory ---------------------------------------------------------------- */
function pageDirectory() {
  openTabFor('directory', t('directory'), '☰');
  var html = head('<a href="#/home">' + t('home') + '</a>', '☰ ' + t('directory') + ' — 67 modules A–Z',
    'Every module, screen group and sub-module in one alphabetical index.');
  var mods = Object.keys(NAV).sort(function (a, b) { return NAV[a].en.localeCompare(NAV[b].en); });
  html += '<div class="fx-card"><div class="dir-grid">';
  mods.forEach(function (mid) {
    var m = NAV[mid];
    html += '<a class="dir-item" href="#/workspace/' + mid + '"><b>' + m.icon + ' ' + mid + ' · ' + esc(m.en) + '</b>' +
      '<span>' + (S.lang === 'bn' ? m.bn : esc(m.desc.slice(0, 64))) + '</span>' +
      '<i>' + m.groups.reduce(function (n, g) { return n + g.screens.length; }, 0) + ' screens · ' + m.freg.src + ' fns</i></a>';
  });
  html += '</div></div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- coverage ----------------------------------------------------------------- */
function pageCoverage() {
  openTabFor('coverage', t('coverage'), '✓');
  var tot = { g: 0, s: 0, r: 0, f: 0, fn: 0 };
  Object.values(NAV).forEach(function (m) {
    m.groups.forEach(function (g) { tot.g++; tot.s += g.screens.length; });
    tot.r += m.reports.length; tot.f += (m.forms || []).length; tot.fn += m.freg.src;
  });
  var html = head('<a href="#/home">' + t('home') + '</a>', '✓ ' + t('coverage') + ' — machine-checkable',
    'Reconciles the navigation payload against the ERP Module Catalogue Master Register (02-02).');
  html += '<div class="kpi-row">' +
    kpiCard({ l: 'Modules', v: Object.keys(NAV).length + ' / 67', st: 'ok' }) +
    kpiCard({ l: 'Screen groups', v: tot.g + '', st: 'ok' }) +
    kpiCard({ l: 'Screens', v: tot.s + '', st: 'ok' }) +
    kpiCard({ l: 'Built-in reports', v: tot.r + '', st: 'ok' }) +
    kpiCard({ l: 'Data-entry forms', v: tot.f + '', st: 'ok' }) +
    kpiCard({ l: 'Functions (freg)', v: tot.fn.toLocaleString() + '', st: 'ok' }) + '</div>';
  html += '<div class="fx-card"><h3>Module × area register</h3>' + '<div class="tbl-wrap"><table class="fx-table compact"><thead><tr><th>Area</th><th>Modules</th><th>Groups</th><th>Screens</th><th>Reports</th><th>Functions</th></tr></thead><tbody>';
  AREAS.forEach(function (a) {
    if (!a.mods.length) return;
    var g = 0, s = 0, r = 0, fn = 0;
    a.mods.forEach(function (mid) {
      var m = NAV[mid]; m.groups.forEach(function (x) { g++; s += x.screens.length; });
      r += m.reports.length; fn += m.freg.src;
    });
    html += '<tr><td><b>' + (S.lang === 'bn' ? a.bn : a.en) + '</b></td><td>' + a.mods.join(' · ') + '</td><td>' + g + '</td><td>' + s + '</td><td>' + r + '</td><td>' + fn + '</td></tr>';
  });
  html += '</tbody></table></div></div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- portals hub ---------------------------------------------------------------- */
function pagePortals() {
  openTabFor('portals', t('portals'), '🌐');
  var html = head('<a href="#/home">' + t('home') + '</a>', '🌐 ' + t('portals') + ' — 12-portal suite (P01–P12)',
    'One design system, SSO via M29, APIs via M28, Bengali-first on customer & field surfaces, WCAG 2.1 AA.',
    '<a class="btn" href="#/journeys">' + t('journeys') + '</a>');
  html += '<div class="portal-grid">' + D.PORTALS.map(function (p) {
    return '<div class="portal-card"><div class="pc-head"><span class="pc-id">' + p[0] + '</span><b>' + esc(p[1]) + '</b></div>' +
      '<p class="pc-meta">' + esc(p[2]) + ' · ' + esc(p[3]) + ' users · ' + esc(p[4]) + '</p>' +
      '<ul>' + p[5].map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
      '<a class="btn btn-sm" href="#/search?q=' + encodeURIComponent(p[0]) + '">Preview surface ▸</a></div>';
  }).join('') + '</div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- journeys -------------------------------------------------------------------- */
function pageJourneys() {
  openTabFor('journeys', t('journeys'), '🧭');
  var html = head('<a href="#/home">' + t('home') + '</a>', '🧭 ' + t('journeys') + ' — end-to-end task flows',
    'Ten scripted journeys crossing portals, modules and roles — the user-journey and task-flow specification made navigable.');
  D.JOURNEYS.forEach(function (j) {
    html += '<div class="fx-card"><h3>' + j.id + ' · ' + esc(j.en) + '</h3><div class="journey-flow">' +
      j.steps.map(function (s, i) {
        return '<a class="j-step" href="' + s[2] + '"><i>' + (i + 1) + '</i><b>' + esc(s[0]) + '</b><span>' + esc(s[1]) + '</span></a>';
      }).join('<span class="j-arrow">→</span>') + '</div></div>';
  });
  document.getElementById('page').innerHTML = html;
}

/* ---------- settings ---------------------------------------------------------------------- */
function pageSettings() {
  openTabFor('settings', t('settings'), '⚙');
  var html = head('<a href="#/home">' + t('home') + '</a>', '⚙ ' + t('settings'),
    'Persona · language · density · theme — every control applies instantly across the shell.');
  html += '<div class="grid-2"><div class="fx-card"><h3>' + t('persona') + '</h3><div class="persona-grid">' +
    DEMO.PERSONAS.map(function (p) {
      return '<button class="persona' + (S.persona === p.id ? ' active' : '') + '" onclick="FXPersonaSet(\'' + p.id + '\')">' +
        '<span class="tb-avatar">' + p.initials + '</span><b>' + esc(p.name) + '</b><span>' + esc(p.role) + '</span></button>';
    }).join('') + '</div><p class="hint">Role centre re-renders with the persona\'s approvals, worklist and KPIs.</p></div>' +
    '<div class="fx-card"><h3>Preferences</h3>' +
    '<label class="fld"><span>Language / ভাষা</span><select onchange="FXLangSet(this.value)"><option value="en"' + (S.lang === 'en' ? ' selected' : '') + '>English</option><option value="bn"' + (S.lang === 'bn' ? ' selected' : '') + '>বাংলা</option></select></label>' +
    '<label class="fld"><span>' + t('density') + '</span><select onchange="FXDensitySet(this.value)"><option value="compact">compact</option><option value="standard">standard</option><option value="relaxed">relaxed</option></select></label>' +
    '<label class="fld"><span>' + t('theme') + '</span><select onchange="FXThemeSet(this.value)"><option value="light">light ☀</option><option value="dark">dark ☾</option></select></label>' +
    '<h4 style="margin-top:14px">Access context (M29)</h4><p class="hint">Data isolation T2 Branch · MFA ✓ · session 8h · SoD clean · audit trail on.</p></div></div>';
  document.getElementById('page').innerHTML = html;
}
window.FXPersonaSet = function (id) { S.persona = id; localStorage.setItem('fx-persona', id); window.FXToast('Persona switched — role centre rebuilt'); location.hash = '#/home'; route(); };
window.FXLangSet = function (v) { S.lang = v; localStorage.setItem('fx-lang', v); document.getElementById('btn-lang').click(); };
window.FXDensitySet = function (v) { S.density = v; localStorage.setItem('fx-density', v); document.documentElement.dataset.density = v; route(); };
window.FXThemeSet = function (v) { S.theme = v; localStorage.setItem('fx-theme', v); document.documentElement.dataset.theme = v; route(); };

/* ---------- design system -------------------------------------------------------------------- */
function pageDesignSystem() {
  openTabFor('design', t('design_system'), '🎨');
  var ramp = ['#04211E','#07332E','#0A453F','#0C544C','#0E645B','#0E7A6E','#0B8A7C','#0F9C8E','#2FB0A2','#54C2B6','#7FD1C8','#A5DED7','#C4E9E4','#DCF2EF','#EBF8F6','#F4FBFA'];
  var html = head('<a href="#/home">' + t('home') + '</a>', '🎨 ' + t('design_system') + ' — Service-Teal Fluent',
    'FixTeal 16-step ramp · Fluent-2 neutrals · AA status triplets · 8-colour charts · density & dark mode.');
  html += '<div class="fx-card"><h3>Brand ramp (teal)</h3><div class="swatches">' +
    ramp.map(function (c, i) { return '<div class="swatch"><i style="background:' + c + '"></i><span>brand-' + ((i + 1) * 10) + '</span><code>' + c + '</code></div>'; }).join('') + '</div></div>';
  html += '<div class="grid-2"><div class="fx-card"><h3>Status</h3>' +
    [['ok'], ['warn'], ['err'], ['info']].map(function (s) { return '<p><span class="st ' + s[0] + '">' + ({ ok: 'OK / pass', warn: 'Warning', err: 'Blocked', info: 'Info' })[s[0]] + '</span></p>'; }).join('') + '</div>' +
    '<div class="fx-card"><h3>Charts (8)</h3>' + window.FXLine([{ n: 'chart-1', v: [4, 6, 5, 8, 7, 9, 8] }], ['a', 'b', 'c', 'd', 'e', 'f', 'g'], { w: 380 }) + '</div></div>';
  html += '<div class="fx-card"><h3>Typography & shape</h3><p style="font-size:20px;font-weight:700">Display 20/28 semibold</p>' +
    '<p style="font-size:14px">Body 14/20 regular — বাংলা: সেবা অর্ডার ও ডিসপ্যাচ ব্যবস্থাপনা</p>' +
    '<p class="hint">Radius 2/4/8/12 · 4-px space grid · double-ring focus · reduced-motion honoured.</p></div>';
  document.getElementById('page').innerHTML = html;
}

/* ---------- small system pages ------------------------------------------------------------------- */
function pageShortcuts() {
  openTabFor('keys', 'Keyboard map', '⌨');
  var rows = [['Alt + Q', 'Focus Tell-ME global search'], ['Ctrl + K', 'Command palette'], ['Ctrl + Shift + O', 'Company switcher'],
    ['Ctrl + /', 'This keyboard map'], ['Ctrl + Tab', 'Next open tab'], ['Shift + F3', 'Toggle filter pane (grids)'],
    ['Alt + C', 'Fix AI copilot (preview)'], ['Esc', 'Close overlays']];
  document.getElementById('page').innerHTML = head('<a href="#/home">' + t('home') + '</a>', '⌨ Keyboard map', 'Zero-mouse operability for power users.') +
    '<div class="fx-card">' + tableHTML({ cols: ['Shortcut', 'Action'], rows: rows.map(function (r) { return ['<span class="kbd">' + r[0] + '</span>', r[1]]; }) }, { plain: 1 }) + '</div>';
}
function pagePalette() {
  openTabFor('palette', 'Command palette', '⌘');
  var acts = [['▶ Run VAT 9.1 filing', '#/screen/M51-vat91'], ['▶ Run payroll', '#/screen/M56-runs'], ['+ New service order', '#/screen/M01-order'],
    ['▦ Open dispatch board', '#/screen/M02-dispatch'], ['▤ Branch league table', '#/screen/M25-branch'], ['✎ New report', '#/writer'],
    ['🌐 Portals hub', '#/portals'], ['🧭 Journeys', '#/journeys']];
  document.getElementById('page').innerHTML = head('<a href="#/home">' + t('home') + '</a>', '⌘ Command palette (Ctrl+K)',
    'Type-ahead actions — the fastest path to any frequent operation.') +
    '<div class="fx-card"><div class="bigsearch"><input id="pal-q" placeholder="Type a command…"/></div><div id="pal-list" style="margin-top:10px">' +
    acts.map(function (a) { return '<a class="sr-item" href="' + a[1] + '"><b>' + a[0] + '</b></a>'; }).join('') + '</div></div>';
  var pq = document.getElementById('pal-q');
  if (pq) pq.oninput = function () {
    var q = this.value.toLowerCase();
    document.querySelectorAll('#pal-list .sr-item').forEach(function (x) { x.style.display = x.textContent.toLowerCase().indexOf(q) >= 0 ? '' : 'none'; });
  };
}
function pageNotifications() {
  openTabFor('notif', t('notifications'), '🔔');
  var ns = [
    ['SLA breach risk', '6 orders will breach in < 1h — Zone-2', 'now', 'err', '#/screen/M01-sla'],
    ['Certification expiring', '8 technicians — dispatch gate in 30 days', '12 min', 'warn', '#/screen/M22-expiry'],
    ['Brand claim decision', 'Samsung approved 4 claims · ৳ 16.4 K', '38 min', 'ok', '#/screen/M09-claims'],
    ['Payment received', 'bKash ৳ 4,830 · SO-2026-14838 settled', '1 h', 'ok', '#/record/M20-invoice/INV-2026-28441'],
    ['Bank recon exceptions', '32 items need review', '2 h', 'warn', '#/screen/M50-recon'],
    ['Close day-2 gate', 'Intercompany pair 2 pending', '3 h', 'info', '#/screen/M19-close']];
  document.getElementById('page').innerHTML = head('<a href="#/home">' + t('home') + '</a>', '🔔 ' + t('notifications'),
    'Every row deep-links to its source record — nothing is a dead end.') +
    '<div class="fx-card">' + ns.map(function (n) {
      return '<a class="notif ' + n[3] + '" href="' + n[4] + '"><b>' + n[0] + '</b><span>' + n[1] + '</span><i>' + n[2] + '</i></a>';
    }).join('') + '</div>';
}
function pageInbox() {
  openTabFor('inbox', t('task_inbox'), '☑');
  var p = window.FXPersona();
  var rows = [];
  p.approvals.forEach(function (a) { rows.push(['Approval', a[0], a[1], a[2], 'Approve ▸', a[3]]); });
  p.worklist.forEach(function (w) { rows.push(['Worklist', w[0], '—', w[1], 'Open ▸', w[2]]); });
  rows.push(['Approval', 'JE-2026-61842', 'Journal', 'Accrual ৳ 8.4 L', 'Approve ▸', '#/screen/M19-je']);
  rows.push(['Workflow', 'CFG-318', 'Config change', 'Auto-assign threshold', 'Review ▸', '#/screen/M30-params']);
  document.getElementById('page').innerHTML = head('<a href="#/home">' + t('home') + '</a>', '☑ ' + t('task_inbox') + ' — unified (M63)',
    'Approvals from every module land here; mobile & portal approvals share this queue.') +
    '<div class="fx-card">' + tableHTML({ cols: ['Type', 'Ref', 'Context', 'Detail', 'Action', 'Go'], rows: rows.map(function (r) { return [r[0], r[1], r[2], r[3], r[4], '<a href="' + r[5] + '">open ›</a>']; }) }, { plain: 1, compact: 1 }) + '</div>';
}
function pageCopilot() {
  openTabFor('copilot', t('copilot'), '✦');
  document.getElementById('page').innerHTML = head('<a href="#/home">' + t('home') + '</a>', '✦ ' + t('copilot') + ' — Bengali-first preview',
    'RAG over live ERP data (M32); authenticated actions with guard rails; human handoff with full context pack.') +
    '<div class="fx-card chat" id="chatbox">' +
    '<div class="msg ai">🙏 আসসালামু আলাইকুম! I can check orders, book services, explain invoices. Try: “SO-2026-14838 কোথায়?”</div>' +
    '<div class="msg me">SO-2026-14838 কোথায়?</div>' +
    '<div class="msg ai">📋 SO-2026-14838 — Dell Latitude 5420 no-power · <b>IN PROGRESS</b> · Jamil Hossain en route (ETA 14 min) · SLA 4h left. <a href="#/record/M01-order/SO-2026-14838">Open record ›</a></div>' +
    '</div><div class="fx-card"><div class="bigsearch"><input id="chat-q" placeholder="Bengali or English…"/><button class="btn btn-primary" onclick="FXChatSend()">Send</button></div>' +
    '<p class="hint">Design preview — responses are scripted; production grounds on M61 knowledge + live queries.</p></div>';
}
window.FXChatSend = function () {
  var q = document.getElementById('chat-q'); if (!q || !q.value.trim()) return;
  var box = document.getElementById('chatbox');
  box.insertAdjacentHTML('beforeend', '<div class="msg me">' + esc(q.value) + '</div>' +
    '<div class="msg ai">✦ (preview) I would ground this on live ERP data and answer with links — e.g. <a href="#/screen/M01-all">all service orders</a>.</div>');
  q.value = ''; box.scrollTop = box.scrollHeight;
};

function notFound(what) {
  document.getElementById('page').innerHTML = head('<a href="#/home">' + t('home') + '</a>', '404 — not found',
    'No route matches “' + esc(what) + '”.') +
    '<div class="fx-card"><p>' + esc(t('try_search')) + '</p><a class="btn btn-primary" href="#/directory">' + t('directory') + '</a> ' +
    '<a class="btn" href="#/search?q=">' + t('tellme_title') + '</a></div>';
}

window.addEventListener('hashchange', route);
})();
