/* =====================================================================
   1000 FiX ERP — SHELL (FIX-UXD-2026-001 Part 5)
   Canonical Dynamics-365-grade chrome rendered client-side from
   FX_NAV: top bar · left nav (areas → modules + user zones) · mega menu
   per area · Tell-ME search (pages + records + actions + reports +
   function register) · right Tab Rail + tab strip · status bar.
   Zero dependencies.
   ===================================================================== */
(function () {
'use strict';
var NAV = window.FX_MODULES, AREAS = window.FX_AREAS, I18N = window.FX_I18N, DEMO = window.FX_DEMO;
var S = { tabs: [], activeTab: null, lang: localStorage.getItem('fx-lang') || 'en',
          density: localStorage.getItem('fx-density') || 'standard',
          theme: localStorage.getItem('fx-theme') || 'light',
          collapsed: false, railOpen: false, persona: localStorage.getItem('fx-persona') || 'super',
          pinned: JSON.parse(localStorage.getItem('fx-pinned') || '[]') };

function t(k) { return (I18N[S.lang] && I18N[S.lang][k]) || I18N.en[k] || k; }
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
window.FX_SHELL = S;

/* ---------- icons (inline, tiny) -------------------------------------- */
var IC = {
  menu:'<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5h12M2 8h12M2 12.5h12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
  search:'<svg width="15" height="15" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="4.4" stroke="currentColor" stroke-width="1.4"/><path d="M10.4 10.4 14 14" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
  bell:'<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 6.5a4 4 0 1 1 8 0c0 3 1 4 1 4H3s1-1 1-4Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M6.5 13a1.5 1.5 0 0 0 3 0" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
  chev:'<svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M3.2 1.6 6.6 5 3.2 8.4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  x:'<svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M1.5 1.5l7 7m0-7l-7 7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
  pin:'<svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><path d="M5 0 6 3.6 9.5 5 6 6.4 5 10 4 6.4.5 5 4 3.6Z"/></svg>',
  grid:'▦', form:'⛁', rep:'▤', con:'⌘', dash:'◫', x360:'◈', scaff:'▢'
};
function typeIcon(t) { return ({ g:IC.grid, f:IC.form, r:IC.rep, c:IC.con, d:IC.dash, x:IC.x360, s:IC.scaff })[t] || IC.grid; }
window.FXIcon = IC; window.FXTypeIcon = typeIcon;

/* ---------- render ----------------------------------------------------- */
function renderShell(root) {
  document.documentElement.lang = S.lang === 'bn' ? 'bn' : 'en';
  document.documentElement.classList.toggle('lang-bn', S.lang === 'bn');
  document.documentElement.dataset.density = S.density;
  document.documentElement.dataset.theme = S.theme;
  root.innerHTML =
    '<header class="fx-topbar" id="topbar">' + topbarHTML() + '</header>' +
    '<nav class="fx-nav" id="leftnav" aria-label="Main">' + navHTML() + '</nav>' +
    '<main class="fx-main"><div class="fx-tabstrip" id="tabstrip"></div><div class="fx-page" id="page" role="main"></div></main>' +
    '<aside class="fx-rail" id="tabrail" aria-label="Open tabs">' + railHTML() + '</aside>' +
    '<footer class="fx-statusbar">' + statusHTML() + '</footer>' +
    '<div class="toast-host" id="toasts"></div>';
  bindShell(root);
}
window.FXRenderShell = renderShell;

function persona() {
  var p = DEMO.PERSONAS.find(function (x) { return x.id === S.persona; }) || DEMO.PERSONAS[0];
  return p;
}
window.FXPersona = persona;

function topbarHTML() {
  var p = persona();
  return (
    '<button class="tb-icon-btn" id="btn-navtoggle" title="Toggle navigation" aria-label="Toggle navigation">' + IC.menu + '</button>' +
    '<div class="tb-brand"><span class="tb-logo">F</span><span style="font-weight:600;font-size:13px">1000 FiX ERP</span></div>' +
    '<div class="fx-tellme"><span class="tm-ico">' + IC.search + '</span>' +
      '<input id="tellme" type="search" placeholder="' + esc(t('search_ph')) + '" role="combobox" aria-expanded="false" aria-label="Global search"/>' +
      '<span class="tm-kbd kbd">Alt+Q</span><div class="tm-results" id="tm-results" role="listbox"></div></div>' +
    '<div class="tb-right">' +
      '<button class="tb-icon-btn" id="btn-directory" title="' + esc(t('directory')) + '">☰</button>' +
      '<button class="tb-icon-btn" id="btn-bell" title="' + esc(t('notifications')) + '">' + IC.bell + '<span id="bell-badge" style="position:absolute;transform:translate(14px,-14px);background:var(--err-bold);color:#fff;font-size:9px;border-radius:8px;padding:0 4px">5</span></button>' +
      '<button class="tb-icon-btn" id="btn-lang" title="Language / ভাষা">' + (S.lang === 'en' ? 'বাংলা' : 'EN') + '</button>' +
      '<button class="tb-icon-btn" id="btn-density" title="' + esc(t('density')) + '">◷</button>' +
      '<button class="tb-icon-btn" id="btn-theme" title="' + esc(t('theme')) + '">' + (S.theme === 'dark' ? '☀' : '☾') + '</button>' +
      '<button class="tb-company" id="btn-company" title="Ctrl+Shift+O"><span style="width:8px;height:8px;border-radius:50%;background:var(--ok-bold)"></span>' + esc(t('company')) + ' ▾</button>' +
      '<button class="tb-icon-btn" id="btn-copilot" title="' + esc(t('copilot')) + ' — ⌥C">✦</button>' +
      '<button class="tb-avatar" id="btn-avatar" title="' + esc(p.name + ' · ' + p.role) + '">' + p.initials + '</button>' +
    '</div>');
}

function navHTML() {
  var h = '<div class="nav-head"><div class="nv-search">' + IC.search +
    '<input id="nav-filter" placeholder="' + esc(t('modules')) + '…" aria-label="Filter navigation"/></div></div>';
  h += '<div class="nav-scroll" id="nav-scroll">';
  h += '<button class="nav-item" data-route="#/home">' + IC.grid + '<span class="nav-label">' + esc(t('home')) + '</span></button>';
  h += '<div class="nav-zone-title">' + esc(t('recents')) + '</div><div id="nav-recents"></div>';
  AREAS.forEach(function (a) {
    if (!a.mods.length) return;
    h += '<button class="nav-item nav-area" data-area="' + a.id + '" aria-expanded="false">' +
      '<span>' + (NAV[a.mods[0]] ? NAV[a.mods[0]].icon : '•') + '</span><span class="nav-label">' +
      (S.lang === 'bn' ? a.bn : a.en) + '</span><span class="nav-count">' + a.mods.length + '</span><span class="chev">' + IC.chev + '</span></button>';
    h += '<div class="nav-sub" data-sub="' + a.id + '">';
    a.mods.forEach(function (mid) {
      var m = NAV[mid]; if (!m) return;
      h += '<button class="nav-item nav-mod" data-route="#/workspace/' + mid + '" title="' + mid + ' · ' + esc(m.en) + '">' +
        '<span>' + m.icon + '</span><span class="nav-label">' + (S.lang === 'bn' ? m.bn : mid + ' · ' + m.en) + '</span></button>';
    });
    h += '</div>';
  });
  h += '<div class="nav-zone-title">' + esc(t('favorites')) + '</div><div id="nav-favs"></div>';
  h += '<div class="nav-zone-title">System</div>' +
    '<button class="nav-item" data-route="#/reports"><span>▤</span><span class="nav-label">' + esc(t('report_center')) + ' (346)</span></button>' +
    '<button class="nav-item" data-route="#/search"><span>⌕</span><span class="nav-label">' + esc(t('tellme_title')) + '</span></button>' +
    '<button class="nav-item" data-route="#/coverage"><span>✓</span><span class="nav-label">' + esc(t('coverage')) + '</span></button>' +
    '<button class="nav-item" data-route="#/portals"><span>🌐</span><span class="nav-label">' + esc(t('portals')) + ' (P01–P12)</span></button>' +
    '<button class="nav-item" data-route="#/journeys"><span>🧭</span><span class="nav-label">' + esc(t('journeys')) + ' (10)</span></button>' +
    '<button class="nav-item" data-route="#/settings"><span>⚙</span><span class="nav-label">' + esc(t('settings')) + '</span></button>' +
    '<button class="nav-item" data-route="#/designsystem"><span>🎨</span><span class="nav-label">' + esc(t('design_system')) + '</span></button>';
  h += '</div>';
  return h;
}

function megaHTML(area) {
  var a = AREAS.find(function (x) { return x.id === area; }); if (!a) return '';
  var h = '<div class="mega-head"><span class="mega-title">' + (S.lang === 'bn' ? a.bn : a.en) + '</span><div class="mega-actions">' +
    a.mods.map(function (mid) {
      var m = NAV[mid]; if (!m) return '';
      return '<a class="mega-chip" href="#/workspace/' + mid + '">' + m.icon + ' ' + mid + ' ' + esc(S.lang === 'bn' ? m.bn : m.en) + '</a>';
    }).join('') + '<a class="mega-chip" href="#/directory">✦ ' + esc(t('directory')) + '</a></div></div>';
  h += '<div class="mega-cols">';
  var shown = 0;
  a.mods.forEach(function (mid) {
    var m = NAV[mid]; if (!m) return;
    m.groups.forEach(function (g) {
      h += '<div class="mega-col"><h6>' + (S.lang === 'bn' && g.bn ? g.bn : g.en) + ' <i>' + mid + '</i></h6>';
      g.screens.forEach(function (sc) {
        h += '<a href="#/screen/' + sc.id + '">' + typeIcon(sc.t) + ' ' +
          (S.lang === 'bn' && sc.bn ? sc.bn : sc.en) + '<span class="sc-type">' + sc.t + '</span></a>';
      });
      h += '</div>'; shown++;
    });
  });
  h += '</div><div class="mega-foot"><span>' + a.mods.length + ' modules · ' + shown + ' screen groups · ' +
    a.mods.reduce(function (n, mid) { return n + (NAV[mid] ? NAV[mid].groups.reduce(function (x, g) { return x + g.screens.length; }, 0) : 0); }, 0) + ' screens — every link live</span></div>';
  return h;
}

function railHTML() {
  return '<div class="rail-strip" id="rail-strip"></div>' +
    '<div class="rail-panel"><div class="rp-head"><input id="rail-search" placeholder="' + esc(t('search_tabs')) + '"/>' +
    '<button class="tb-icon-btn" id="rail-close" title="' + esc(t('close')) + '">' + IC.x + '</button></div>' +
    '<div class="rp-body" id="rp-body"></div>' +
    '<div class="rp-foot"><button class="btn btn-ghost btn-sm" id="rail-session">↺ ' + esc(t('reopen_session')) + '</button></div></div>';
}

function statusHTML() {
  return '<span class="sb-env">' + esc(t('demo_note')) + '</span>' +
    '<span>' + esc(t('company')) + ' · ' + esc(t('fy')) + ' · 53 branches</span>' +
    '<span class="sb-save" id="sb-save">✓ ' + esc(t('saved')) + ' ' + new Date().toTimeString().slice(0,5) + '</span>' +
    '<span class="sb-spacer"></span>' +
    '<span id="sb-crumbs" style="font-family:var(--font-mono);font-size:10px"></span>' +
    '<button class="sb-btn" id="sb-density">' + esc(t('density')) + ': ' + esc(t(S.density)) + '</button>' +
    '<span class="kbd">Ctrl+/</span>';
}

/* ---------- tabs -------------------------------------------------------- */
function openTab(id, title, route, icon) {
  var ex = S.tabs.find(function (x) { return x.id === id; });
  if (ex) { ex.route = route; S.activeTab = id; }
  else {
    if (S.tabs.filter(function (x) { return !x.pinned; }).length >= 12) {
      var lru = S.tabs.filter(function (x) { return !x.pinned; })[0];
      if (lru) S.tabs.splice(S.tabs.indexOf(lru), 1);
    }
    S.tabs.push({ id: id, title: title, route: route, icon: icon || IC.grid, pinned: S.pinned.indexOf(id) >= 0 });
    S.activeTab = id;
  }
  paintTabs(); pushRecent(route, title);
}
window.FXOpenTab = openTab;
function closeTab(id) {
  S.tabs = S.tabs.filter(function (x) { return x.id !== id; });
  if (S.activeTab === id) S.activeTab = S.tabs.length ? S.tabs[S.tabs.length - 1].id : null;
  paintTabs();
  if (S.activeTab) location.hash = S.tabs.find(function (x) { return x.id === S.activeTab; }).route;
  else location.hash = '#/home';
}
function paintTabs() {
  var strip = document.getElementById('tabstrip');
  if (!strip) return;
  strip.innerHTML = S.tabs.map(function (tb) {
    return '<button class="tab' + (tb.id === S.activeTab ? ' active' : '') + '" data-tab="' + tb.id + '" title="' + esc(tb.title) + '">' +
      '<span>' + tb.icon + '</span><span style="max-width:150px;overflow:hidden;text-overflow:ellipsis">' + esc(tb.title) + '</span>' +
      (tb.pinned ? '<span class="pin">' + IC.pin + '</span>' : '') +
      '<span class="x" data-close="' + tb.id + '" role="button" aria-label="Close">' + IC.x + '</span></button>';
  }).join('') + '<button class="tb-icon-btn tab-overflow" id="rail-toggle" title="' + esc(t('open_tabs')) + '">⌄</button>';
  var strip2 = document.getElementById('rail-strip');
  if (strip2) strip2.innerHTML = S.tabs.map(function (tb) {
    return '<button class="rail-tab' + (tb.id === S.activeTab ? ' active' : '') + '" data-tab="' + tb.id + '" title="' + esc(tb.title) + '">' +
      '<span>' + tb.icon + '</span>' + (tb.pinned ? '<span class="pin">' + IC.pin + '</span>' : '') + '</button>';
  }).join('') + '<button class="rail-tab rail-expander" id="rail-expand" title="' + esc(t('open_tabs')) + '">⌄</button>';
  var body = document.getElementById('rp-body');
  if (body) {
    body.innerHTML = '<div class="rp-zone">' + esc(t('pinned')) + '</div>' +
      S.tabs.filter(function (x) { return x.pinned; }).map(railItem).join('') +
      '<div class="rp-zone">' + esc(t('open_tabs')) + ' (' + S.tabs.length + ')</div>' +
      S.tabs.filter(function (x) { return !x.pinned; }).map(railItem).join('');
  }
  persistSession();
}
function railItem(tb) {
  return '<button class="rp-item' + (tb.id === S.activeTab ? ' active' : '') + '" data-tab="' + tb.id + '">' + tb.icon +
    ' <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + esc(tb.title) + '</span>' +
    '<span class="rp-x" data-close="' + tb.id + '">' + IC.x + '</span></button>';
}
function persistSession() {
  try { localStorage.setItem('fx-session', JSON.stringify(S.tabs.map(function (x) { return { id: x.id, title: x.title, route: x.route, icon: x.icon, pinned: x.pinned }; }))); } catch (e) {}
}
function pushRecent(route, title) {
  try {
    var r = JSON.parse(localStorage.getItem('fx-recent') || '[]').filter(function (x) { return x.p !== route; });
    r.unshift({ p: route, t: title }); localStorage.setItem('fx-recent', JSON.stringify(r.slice(0, 12)));
  } catch (e) {}
  paintRecents();
}
function paintRecents() {
  var el = document.getElementById('nav-recents'); if (!el) return;
  var r = [];
  try { r = JSON.parse(localStorage.getItem('fx-recent') || '[]').slice(0, 4); } catch (e) {}
  el.innerHTML = r.map(function (x) { return '<button class="nav-item lvl3" data-route="' + esc(x.p) + '"><span class="nav-label">' + esc(x.t) + '</span></button>'; }).join('');
}

/* ---------- Tell-ME search ---------------------------------------------- */
function tellmeSearch(q, limit) {
  q = q.trim().toLowerCase();
  if (!q) return [];
  limit = limit || 14;
  var out = [];
  var records = DEMO.tellme;
  Object.keys(NAV).forEach(function (mid) {
    var m = NAV[mid];
    if ((mid + ' ' + m.en + ' ' + m.bn).toLowerCase().indexOf(q) >= 0)
      out.push({ g: t('pages'), label: mid + ' — ' + m.en, meta: 'module', href: '#/workspace/' + mid });
    m.groups.forEach(function (gr) {
      if ((gr.en + ' ' + (gr.bn || '')).toLowerCase().indexOf(q) >= 0)
        out.push({ g: t('pages'), label: gr.en, meta: mid + ' · ' + gr.screens.length + ' ' + t('screens'), href: '#/screen/' + gr.screens[0].id });
      gr.screens.forEach(function (sc) {
        if ((sc.id + ' ' + sc.en + ' ' + (sc.bn || '') + ' ' + gr.en).toLowerCase().indexOf(q) >= 0)
          out.push({ g: t('pages'), label: sc.en, meta: mid + ' · ' + gr.en, href: '#/screen/' + sc.id });
      });
    });
    m.freg.sub.forEach(function (s, si) {
      if (String(s[1]).toLowerCase().indexOf(q) >= 0)
        out.push({ g: t('function_register'), label: s[1], meta: mid + ' · ' + s[2] + ' ' + t('functions'), href: '#/freg/' + mid + '/' + si });
    });
    (m.forms || []).forEach(function (f) {
      if (f.toLowerCase().indexOf(q) >= 0)
        out.push({ g: t('actions'), label: f, meta: mid + ' · ⛁ ' + t('forms').toLowerCase(), href: '#/screen/' + m.groups[0].screens[0].id });
    });
    m.reports.forEach(function (r, ri) {
      if (r.toLowerCase().indexOf(q) >= 0) out.push({ g: t('reports'), label: r, meta: mid + ' · ▶ ' + t('run').toLowerCase(), href: '#/report/' + mid + '/' + ri });
    });
  });
  records.forEach(function (rec) {
    if ((rec[0] + ' ' + rec[1] + ' ' + rec[2]).toLowerCase().indexOf(q) >= 0)
      out.push({ g: t('records'), label: rec[0] + ' · ' + rec[1], meta: rec[2], href: rec[3] });
  });
  [['New Service Order', '#/screen/M01-order'], ['Dispatch Board', '#/screen/M02-dispatch'],
   ['Run Payroll', '#/screen/M56-runs'], ['File VAT 9.1', '#/screen/M51-vat91'],
   ['New Customer', '#/screen/M33-party'], ['Create Quotation', '#/screen/M36-record'],
   ['New Purchase Order', '#/screen/M16-pos'], ['Report Writer', '#/writer'],
   ['Task Inbox', '#/inbox'], ['Brand Claim', '#/screen/M09-record']
  ].forEach(function (a) { if (a[0].toLowerCase().indexOf(q) >= 0) out.push({ g: t('actions'), label: a[0], meta: 'action', href: a[1] }); });
  return out.slice(0, limit);
}
window.FXSearch = tellmeSearch;
function paintTellme(q) {
  var box = document.getElementById('tm-results'); if (!box) return;
  var res = tellmeSearch(q);
  if (!res.length) { box.classList.remove('open'); box.innerHTML = ''; return; }
  var groups = {};
  res.forEach(function (r) { (groups[r.g] = groups[r.g] || []).push(r); });
  box.innerHTML = Object.keys(groups).map(function (g) {
    return '<div class="tm-group"><h5>' + esc(g) + '</h5>' + groups[g].map(function (r) {
      return '<button class="tm-item" data-href="' + esc(r.href) + '"><span>' + esc(r.label) + '</span><span class="tm-meta">' + esc(r.meta) + '</span></button>';
    }).join('') + '</div>';
  }).join('');
  box.classList.add('open');
}

/* ---------- events ------------------------------------------------------- */
function bindId(id, ev, fn) {
  var el = document.getElementById(id);
  if (el) el[ev] = fn;
}
function bindShell(root) {
  var shell = document.getElementById('fx-shell');

  root.addEventListener('click', function (e) {
    if (e.target.closest('#rail-toggle, #rail-expand')) {
      shell2().classList.add('rail-open'); S.railOpen = true; return;
    }
    if (e.target.closest('#rail-close')) {
      shell2().classList.remove('rail-open'); S.railOpen = false; return;
    }
    var el = e.target.closest('[data-route]');
    if (el) { location.hash = el.dataset.route; return; }
    el = e.target.closest('[data-href]');
    if (el) {
      location.hash = el.dataset.href;
      var tr = document.getElementById('tm-results'); if (tr) tr.classList.remove('open');
      return;
    }
    el = e.target.closest('[data-close]');
    if (el) { e.stopPropagation(); closeTab(el.dataset.close); return; }
    el = e.target.closest('[data-tab]');
    if (el) {
      var tb = S.tabs.find(function (x) { return x.id === el.dataset.tab; });
      if (tb) { S.activeTab = tb.id; location.hash = tb.route; }
      return;
    }
    if (!e.target.closest('.fx-tellme')) { var rb = document.getElementById('tm-results'); if (rb) rb.classList.remove('open'); }
    if (!e.target.closest('.fx-mega') && !e.target.closest('.nav-area')) { var mg = document.getElementById('megamenu'); if (mg) mg.classList.remove('open'); }
  });

  /* navigation closes overlays — mega menu must not linger over the target page */
  if (!window.__fxOverlayClose) {
    window.__fxOverlayClose = 1;
    window.addEventListener('hashchange', function () {
      var mg = document.getElementById('megamenu'); if (mg) mg.classList.remove('open');
      var tr = document.getElementById('tm-results'); if (tr) tr.classList.remove('open');
      var sh = document.getElementById('fx-shell'); if (sh) sh.classList.remove('nav-open');
    });
  }

  paintTabs(); paintRecents();

  bindId('btn-navtoggle', 'onclick', function () {
    S.collapsed = !S.collapsed;
    if (window.innerWidth <= 1024) shell.classList.toggle('nav-open');
    else shell.classList.toggle('nav-collapsed');
  });
  bindId('btn-lang', 'onclick', function () {
    S.lang = S.lang === 'en' ? 'bn' : 'en'; localStorage.setItem('fx-lang', S.lang); renderShell(root); route2();
  });
  var cycleD = function () {
    S.density = { compact: 'standard', standard: 'relaxed', relaxed: 'compact' }[S.density];
    localStorage.setItem('fx-density', S.density); document.documentElement.dataset.density = S.density;
    var sb = document.getElementById('sb-density'); if (sb) sb.textContent = t('density') + ': ' + t(S.density);
  };
  bindId('btn-density', 'onclick', cycleD);
  bindId('sb-density', 'onclick', cycleD);
  bindId('btn-theme', 'onclick', function () {
    S.theme = S.theme === 'light' ? 'dark' : 'light'; localStorage.setItem('fx-theme', S.theme);
    document.documentElement.dataset.theme = S.theme;
    this.textContent = S.theme === 'dark' ? '☀' : '☾'; route2();
  });
  bindId('btn-directory', 'onclick', function () { location.hash = '#/directory'; });
  bindId('btn-bell', 'onclick', function () { location.hash = '#/notifications'; });
  bindId('btn-company', 'onclick', function () { toast('Company switcher — 1000 FiX Services Ltd. (Ctrl+Shift+O)'); });
  bindId('btn-copilot', 'onclick', function () { toast(t('copilot') + ' — Bengali draft ready (design preview)'); });
  bindId('btn-avatar', 'onclick', function () { location.hash = '#/settings'; });
  bindId('rail-session', 'onclick', function () { toast(t('reopen_session') + ' — up to 12 tabs'); });
  bindId('rail-search', 'oninput', function () {
    var q = this.value.toLowerCase();
    document.querySelectorAll('#rp-body .rp-item').forEach(function (x) {
      x.style.display = x.textContent.toLowerCase().indexOf(q) >= 0 ? '' : 'none';
    });
  });

  var tm = document.getElementById('tellme');
  if (tm) {
    tm.oninput = function () { paintTellme(this.value); };
    tm.onkeydown = function (e) {
      var box = document.getElementById('tm-results');
      var items = box ? [].slice.call(box.querySelectorAll('.tm-item')) : [];
      var cur = items.findIndex(function (x) { return x.classList.contains('active'); });
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (!items.length) return;
        e.preventDefault();
        if (cur >= 0) items[cur].classList.remove('active');
        cur = e.key === 'ArrowDown' ? (cur + 1) % items.length : (cur <= 0 ? items.length - 1 : cur - 1);
        items[cur].classList.add('active');
        items[cur].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        if (cur >= 0 && items[cur]) { location.hash = items[cur].dataset.href; tm.blur(); }
        else { location.hash = '#/search?q=' + encodeURIComponent(this.value); tm.blur(); }
      } else if (e.key === 'Escape') {
        if (box) box.classList.remove('open'); tm.blur();
      }
    };
  }
  bindId('nav-filter', 'oninput', function () {
    var q = this.value.toLowerCase();
    document.querySelectorAll('#nav-scroll .nav-mod, #nav-scroll .nav-area').forEach(function (x) {
      x.style.display = x.textContent.toLowerCase().indexOf(q) >= 0 ? '' : 'none';
    });
  });

  /* area expand + mega menu */
  document.querySelectorAll('.nav-area').forEach(function (btn) {
    btn.onclick = function (e) {
      var id = btn.dataset.area, sub = document.querySelector('[data-sub="' + id + '"]');
      var open = sub && sub.classList.toggle('open');
      btn.classList.toggle('expanded', !!open); btn.setAttribute('aria-expanded', !!open);
      var existing = document.getElementById('megamenu'); if (existing) existing.remove();
      if (!open) return;
      var mg = document.createElement('div'); mg.className = 'fx-mega'; mg.id = 'megamenu';
      mg.innerHTML = megaHTML(id);
      document.body.appendChild(mg);
      var r = btn.getBoundingClientRect();
      mg.style.left = Math.max(8, Math.min(r.left, window.innerWidth - mg.offsetWidth - 12)) + 'px';
      mg.classList.add('open');
      e.stopPropagation();
    };
  });

  /* keyboard map */
  document.addEventListener('keydown', function (e) {
    if (e.altKey && e.key.toLowerCase() === 'q') { e.preventDefault(); var q = document.getElementById('tellme'); if (q) { q.focus(); q.select(); } }
    if (e.altKey && e.key.toLowerCase() === 'c') { e.preventDefault(); location.hash = '#/copilot'; }
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'o') { e.preventDefault(); var b = document.getElementById('btn-company'); if (b) b.click(); }
    if (e.ctrlKey && e.key === '/') { e.preventDefault(); location.hash = '#/shortcuts'; }
    if (e.ctrlKey && e.key.toLowerCase() === 'k') { e.preventDefault(); location.hash = '#/palette'; }
    if (e.ctrlKey && e.key === 'Tab') {
      e.preventDefault();
      var i = S.tabs.findIndex(function (x) { return x.id === S.activeTab; });
      if (S.tabs.length) { var nx = S.tabs[(i + 1) % S.tabs.length]; S.activeTab = nx.id; location.hash = nx.route; }
    }
  });
}
function route2() { if (window.FXRoute) window.FXRoute(); }
function shell2() { return document.getElementById('fx-shell') || document.body; }

function toast(msg, undo) {
  var host = document.getElementById('toasts'); if (!host) return;
  var el = document.createElement('div'); el.className = 'toast';
  el.innerHTML = esc(msg) + (undo ? ' <button class="undo">Undo</button>' : '');
  host.appendChild(el);
  setTimeout(function () { el.remove(); }, 4200);
}
window.FXToast = toast;
window.FXT = t;
})();
