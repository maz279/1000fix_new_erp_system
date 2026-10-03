/* =====================================================================
   1000 FiX ERP — INTERACTIVE BROWSER AUDIT (connects to a running
   headless Chrome on --remote-debugging-port=9333; launch it first).
     A. landing page — links, anchors, বাংলা toggle
     B. login page — credential + TOTP flow, one-click demo button
     C. app crawl  — BFS over EVERY link (click-equivalent), mega menus,
                     Tell-ME search, form-modal validation, tab rail,
                     toggles, per-route h1/render assertions
     D. screenshots of key views → ./_shots/*.png
   Run:  node _audit_click.js   (needs http://localhost:8471 + Chrome 9333)
   ===================================================================== */
'use strict';
const fs = require('fs');
const path = require('path');

const PORT = 9333;
const BASE = 'http://localhost:8471';
const SHOTS = path.join(__dirname, '_shots');
fs.mkdirSync(SHOTS, { recursive: true });

const errors = [];
let curRoute = '(boot)';

/* ---------- tiny CDP client (Node ≥21 global WebSocket) ------------- */
let ws, msgId = 0;
const pending = new Map();
const handlers = [];
function send(method, params) {
  return new Promise((res, rej) => {
    const id = ++msgId;
    pending.set(id, { res, rej });
    ws.send(JSON.stringify({ id, method, params: params || {} }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error('CDP timeout ' + method)); } }, 20000);
  });
}
function on(fn) { handlers.push(fn); }
async function expr(js) {
  const r = await send('Runtime.evaluate', { expression: js, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails.exception || {}).slice(0, 200));
  return r.result && r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function boot() {
  let page = null;
  for (let i = 0; i < 60 && !page; i++) {
    try {
      const targets = await fetch(`http://127.0.0.1:${PORT}/json`).then(r => r.json());
      page = targets.find(t => t.type === 'page');
    } catch (e) { /* chrome not up yet */ }
    if (!page) await sleep(300);
  }
  if (!page) throw new Error('no CDP page target on port ' + PORT);
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.rej(new Error(m.error.message)) : p.res(m.result);
    } else handlers.forEach(h => h(m));
  };
  on(m => {
    if (m.method === 'Runtime.exceptionThrown')
      errors.push({ route: curRoute, text: 'EXC ' + ((m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description) || m.params.exceptionDetails.text || '').slice(0, 220) });
    if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error')
      errors.push({ route: curRoute, text: 'CON ' + m.params.args.map(a => a.value || a.description || '').join(' ').slice(0, 220) });
  });
  await send('Runtime.enable'); await send('Page.enable'); await send('Log.enable');
  /* python http.server sends no cache-control — Chrome heuristically caches JS and serves stale code across edits */
  await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  try { await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false }); }
  catch (e) { /* window-size flag already set; optional */ }
}

async function goto(url) {
  const loaded = new Promise(res => { const h = m => { if (m.method === 'Page.loadEventFired') { handlers.splice(handlers.indexOf(h), 1); res(); } }; handlers.push(h); });
  await send('Page.navigate', { url });
  await Promise.race([loaded, sleep(6000)]);
  await sleep(150);
}
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(SHOTS, name + '.png'), Buffer.from(r.data, 'base64'));
}
async function goRoute(hash) {
  curRoute = hash;
  await expr(`location.hash = ${JSON.stringify(hash)}; 0`);
  await sleep(40);
}
function pageProbe() {
  return expr(`(function(){
    var p = document.getElementById('page');
    return { html: p ? p.innerHTML.length : 0, h1: p ? (p.querySelector('h1')||{}).textContent||'' : '' };
  })()`);
}

(async () => {
  await boot();
  const report = [];
  const visited = new Set();
  const queue = [];

  /* ---------- A. LANDING -------------------------------------------- */
  await goto(BASE + '/index.html');
  curRoute = 'index.html';
  await sleep(450);
  const landing = await expr(`(function(){
    var links = [].map.call(document.querySelectorAll('a[href]'), a=>a.getAttribute('href'));
    var ids  = ['top','journeys','modules','portals','design'];
    return { links: links, anchorsOk: ids.every(i=>document.getElementById(i)!==null),
             areas: document.querySelectorAll('.area-card').length,
             journeys: document.querySelectorAll('.j-cell').length,
             portals: document.querySelectorAll('.p-card').length };
  })()`);
  report.push(['LANDING', 'area-cards=' + landing.areas, 'journeys=' + landing.journeys, 'portals=' + landing.portals, 'anchorsOk=' + landing.anchorsOk].join(' '));
  if (!landing.anchorsOk) errors.push({ route: 'index.html', text: 'missing landing anchor ids' });
  if (landing.areas < 11 || landing.portals < 12) errors.push({ route: 'index.html', text: 'landing cards undercount' });
  await expr(`document.querySelector('.land-lang').click(); 0`);
  const bnOK = await expr(`document.querySelector('[data-i18n=h1a]').textContent.includes('বাংলাদেশ')`);
  await expr(`document.querySelector('.land-lang').click(); 0`);
  const enBack = await expr(`(function(){
    var el = document.querySelector('[data-i18n=h1a]');
    return { heroEn: !el.textContent.includes('বাংলাদেশ'),
             anyBnLeft: !!document.querySelector('[data-orig]') };
  })()`);
  report.push(['LANDING', 'lang-toggle-bn=' + bnOK, 'lang-restore-en=' + enBack.heroEn].join(' '));
  if (bnOK && (!enBack.heroEn || enBack.anyBnLeft)) errors.push({ route: 'index.html', text: 'EN restore left Bengali text (i18n round-trip)' });
  landing.links.filter(h => h && h.startsWith('app.html#/')).forEach(h => queue.push('#/' + h.split('#/')[1]));
  await shot('01-landing');

  /* ---------- B. LOGIN ---------------------------------------------- */
  await goto(BASE + '/login.html');
  curRoute = 'login.html';
  await sleep(300);
  const login1 = await expr(`(function(){
    document.getElementById('fx-submit').click();
    return { totpShown: document.getElementById('fx-totp-row').style.display !== 'none' };
  })()`);
  await expr(`(function(){
    var ins = document.querySelectorAll('.fx-otp');
    '123456'.split('').forEach((c,i)=>ins[i].value=c);
    return 0;
  })()`);
  await expr(`document.getElementById('fx-submit').click(); 0`);
  await sleep(900);
  const loginURL = await expr('location.href');
  report.push(['LOGIN', 'totp=' + login1.totpShown, 'after-submit-url=' + loginURL.replace(BASE, '')].join(' '));
  if (!/app\.html/.test(loginURL)) errors.push({ route: 'login.html', text: 'credential flow did not reach app.html' });
  await goto(BASE + '/login.html'); await sleep(250);
  await expr(`document.querySelector('.login-demo .btn-hero').click(); 0`);
  await sleep(900);
  const demoURL = await expr('location.href');
  report.push(['LOGIN', 'one-click-demo=' + demoURL.replace(BASE, '')].join(' '));
  if (!/app\.html/.test(demoURL)) errors.push({ route: 'login.html', text: 'demo button did not navigate to app' });
  await goto(BASE + '/login.html'); await shot('02-login');
  await goto(BASE + '/app.html');
  await sleep(600);

  /* ---------- C. APP ------------------------------------------------ */
  const sysRoutes = ['#/home', '#/reports', '#/writer', '#/directory', '#/coverage',
    '#/portals', '#/journeys', '#/settings', '#/designsystem', '#/shortcuts',
    '#/palette', '#/notifications', '#/inbox', '#/copilot', '#/search?q=dispatch',
    '#/search?q=' + encodeURIComponent('ওয়ারেন্টি')];
  sysRoutes.forEach(r => queue.push(r));

  const linkSel = `[].map.call(document.querySelectorAll('#page a[href^="#/"], #page a[href^="app.html#/"]'), a=>a.getAttribute('href'))`;

  async function crawlOne(route) {
    visited.add(route);
    await goRoute(route);
    const probe = await pageProbe();
    if (probe.html < 80 || !probe.h1) {
      errors.push({ route, text: 'EMPTY/BROKEN render html=' + probe.html + ' h1="' + probe.h1 + '"' });
    }
    if (/404\s*[-—]\s*not found/i.test(probe.h1 || '')) {
      errors.push({ route, text: 'DEAD LINK — renders 404 page' });
    }
    let links = [];
    try { links = await expr(linkSel); } catch (e) { errors.push({ route, text: 'link-extract: ' + e.message }); }
    links.forEach(h => {
      if (!h) return;
      const r = h.startsWith('app.html#/') ? '#/' + h.split('#/')[1] : h;
      if (r.startsWith('#/') && !visited.has(r) && !queue.includes(r)) queue.push(r);
    });
    return probe;
  }

  /* seed: expand all nav areas, collect module + system routes */
  await goRoute('#/home');
  await expr(`(function(){ document.querySelectorAll('.nav-area').forEach(function(b){ b.click(); b.click(); }); return 0; })()`);
  const navLinks = await expr(`[].map.call(document.querySelectorAll('.nav-sub button[data-route], .nav-scroll button[data-route]'), function(b){ return b.dataset.route; })`);
  navLinks.filter(Boolean).forEach(r => { if (!visited.has(r) && !queue.includes(r)) queue.push(r); });

  /* mega menus: real clicks */
  const megaCounts = [];
  for (let i = 0; i < 12; i++) {
    const area = await expr(`(function(){
      var b = document.querySelectorAll('.nav-area')[${i}];
      if (!b) return null;
      b.click();
      var mg = document.getElementById('megamenu');
      return mg ? { links: mg.querySelectorAll('a').length, title: mg.querySelector('.mega-title').textContent } : null;
    })()`);
    if (!area) break;
    megaCounts.push(area.links);
    if (i === 1) await shot('04-megamenu');
    await expr(`document.body.click(); 0`);
  }
  report.push(['MEGA-MENUS', 'opened=' + megaCounts.length, 'links=' + megaCounts.join('/')].join(' '));
  /* 11 areas carry modules (A01 Home intentionally has none) */
  if (megaCounts.length !== 11 || megaCounts.some(n => n < 8)) errors.push({ route: 'megamenu', text: 'mega menu underfilled: ' + megaCounts.join(',') });

  /* Tell-ME search interaction (EN + বাংলা) */
  const tm = await expr(`(function(){
    var i = document.getElementById('tellme');
    i.value = 'dispatch'; i.dispatchEvent(new Event('input', {bubbles:true}));
    var box = document.getElementById('tm-results');
    var n = box.classList.contains('open') ? box.querySelectorAll('.tm-item').length : 0;
    if (n) box.querySelector('.tm-item').click();
    return { n: n };
  })()`);
  await sleep(200);
  report.push(['TELLME', 'results=' + tm.n, 'navigated=' + (await expr('location.hash'))].join(' '));
  if (!tm.n) errors.push({ route: 'tellme', text: 'no live results for "dispatch"' });
  const tmBn = await expr(`(function(){
    var i = document.getElementById('tellme');
    i.value = 'ওয়ারেন্টি'; i.dispatchEvent(new Event('input', {bubbles:true}));
    var box = document.getElementById('tm-results');
    return box.classList.contains('open') ? box.querySelectorAll('.tm-item').length : 0;
  })()`);
  report.push(['TELLME', 'bengali-results=' + tmBn].join(' '));
  if (!tmBn) errors.push({ route: 'tellme', text: 'no results for Bengali query' });
  await expr(`document.body.click(); 0`);

  /* form modal validation */
  await goRoute('#/workspace/M01');
  const form = await expr(`(async function(){
    var chips = document.querySelectorAll('.form-chip');
    if (!chips.length) return { chips: 0 };
    chips[0].click(); await new Promise(r=>setTimeout(r,80));
    var modal = document.querySelector('.modal');
    if (!modal) return { chips: chips.length, modal: 0 };
    window.FXFormSubmit();
    var redBorders = [].filter.call(document.querySelectorAll('.frm-req'), function(i){ return i.style.borderColor; }).length;
    [].forEach.call(document.querySelectorAll('.frm-req'), function(i){ i.value = 'x'; });
    window.FXFormSubmit();
    await new Promise(r=>setTimeout(r,60));
    var after = document.querySelectorAll('#fx-modal .modal').length;
    return { chips: chips.length, redOnEmpty: redBorders, closedOnValid: after === 0 };
  })()`);
  report.push(['FORM-MODAL', JSON.stringify(form)].join(' '));
  if (!form.redOnEmpty || !form.closedOnValid) errors.push({ route: 'form', text: 'validation broken ' + JSON.stringify(form) });

  /* tab rail + close a tab */
  const rail = await expr(`(function(){
    var t = document.getElementById('rail-toggle'); if (t) t.click();
    var open = document.getElementById('fx-shell').classList.contains('rail-open');
    var items = document.querySelectorAll('#rp-body .rp-item').length;
    var x = document.querySelector('.rp-x'); if (x) x.click();
    var c = document.getElementById('rail-close'); if (c) c.click();
    return { open: open, items: items };
  })()`);
  report.push(['TAB-RAIL', JSON.stringify(rail)].join(' '));
  if (!rail.open) errors.push({ route: 'rail', text: 'rail did not open' });

  /* toggles round-trip */
  const tog = await expr(`(function(){
    var o = {};
    document.getElementById('btn-theme').click();
    o.theme = document.documentElement.dataset.theme;
    document.getElementById('btn-theme').click();
    document.getElementById('btn-density').click();
    o.density = document.documentElement.dataset.density;
    document.getElementById('btn-density').click(); document.getElementById('btn-density').click();
    document.getElementById('btn-lang').click();
    o.bn = document.documentElement.classList.contains('lang-bn');
    o.navBn = (document.querySelector('.nav-mod .nav-label')||{}).textContent || '';
    document.getElementById('btn-lang').click();
    return o;
  })()`);
  report.push(['TOGGLES', JSON.stringify(tog)].join(' '));
  if (tog.theme !== 'dark' || !tog.bn) errors.push({ route: 'toggles', text: 'theme/lang toggle failed ' + JSON.stringify(tog) });

  /* screenshots of key views */
  await goRoute('#/home'); await shot('03-home');
  await goRoute('#/workspace/M01'); await shot('05-workspace-M01');
  await goRoute('#/screen/M01-all'); await shot('06-grid-M01');
  await goRoute('#/record/M01-order/SO-2026-14838'); await shot('07-record');
  await goRoute('#/screen/M02-dispatch'); await shot('08-dispatch');
  await goRoute('#/screen/M19-close'); await shot('09-console-close');
  await goRoute('#/report/M51/1'); await shot('10-report-vat');
  await goRoute('#/writer'); await shot('11-writer');
  await goRoute('#/portals'); await shot('12-portals');
  await goRoute('#/journeys'); await shot('13-journeys');
  await goRoute('#/coverage'); await shot('14-coverage');
  await expr(`document.getElementById('btn-theme').click(); 0`);
  await goRoute('#/home'); await shot('15-home-dark');
  await expr(`document.getElementById('btn-theme').click(); 0`);
  await expr(`document.getElementById('btn-lang').click(); 0`);
  await goRoute('#/screen/M01-all'); await shot('16-grid-bengali');
  await expr(`document.getElementById('btn-lang').click(); 0`);

  /* exhaustive crawl of every queued route */
  let crawled = 0;
  while (queue.length) {
    const r = queue.shift();
    if (visited.has(r)) continue;
    await crawlOne(r);
    crawled++;
  }
  report.push(['CRAWL', 'unique-routes=' + visited.size, 'crawled=' + crawled].join(' '));
  report.push(['RESULT', errors.length === 0 ? 'ALL CLEAN ✓' : errors.length + ' ISSUES', 'routes=' + visited.size, 'screenshots=16'].join(' '));

  console.log(report.join('\n'));
  if (errors.length) {
    console.log('\n--- ISSUES ---');
    errors.slice(0, 60).forEach(e => console.log(' ', e.route, '→', e.text));
    if (errors.length > 60) console.log('  … +' + (errors.length - 60) + ' more');
  }
  process.exit(errors.length === 0 ? 0 : 1);
})().catch(e => { console.error('AUDIT CRASH', e); process.exit(2); });
