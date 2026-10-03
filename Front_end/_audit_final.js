/* =====================================================================
   1000 FiX ERP — SUPPLEMENTARY FINAL AUDIT (iteration 3).
   Covers what the 8,716-route click crawl could not:
     A. ASSETS      — browser-side Network capture: every subresource
                      (css/js/img/url()) must load with status < 400
     B. DEEP-LINKS  — direct cold loads of every archetype hash
     C. HISTORY     — back/forward restores route + content
     D. OVERFLOW    — no horizontal scroll at 1600×900 on key routes
     E. MOBILE      — 390×844: no overflow; 3 screenshots
     F. FOCUS       — keyboard focus ring visible on first control
   Run:  node _audit_final.js   (needs server :8471 + Chrome CDP :9333)
   ===================================================================== */
'use strict';
const fs = require('fs');
const path = require('path');

const PORT = 9333;
const BASE = 'http://localhost:8471';
const SHOTS = path.join(__dirname, '_shots');
fs.mkdirSync(SHOTS, { recursive: true });

const errors = [];
const report = [];
let curPhase = '(boot)';

/* ---------- tiny CDP client ------------------------------------------ */
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

/* network capture — filled by CDP events, read-only for the audit */
const netStatus = new Map();   /* url -> http status */
const netFailed = [];          /* {url, text} */

async function boot() {
  let page = null;
  for (let i = 0; i < 60 && !page; i++) {
    try {
      const targets = await fetch('http://127.0.0.1:9333/json').then(r => r.json());
      page = targets.find(t => t.type === 'page');
    } catch (e) { /* chrome not up yet */ }
    if (!page) await sleep(300);
  }
  if (!page) throw new Error('no CDP page target on port 9333');
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
    if (m.method === 'Network.responseReceived')
      netStatus.set(m.params.response.url, m.params.response.status);
    if (m.method === 'Network.loadingFailed')
      netFailed.push({ url: m.params.requestId, text: m.params.errorText });
    if (m.method === 'Runtime.exceptionThrown')
      errors.push({ phase: curPhase, text: 'EXC ' + ((m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description) || m.params.exceptionDetails.text || '').slice(0, 220) });
    if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error')
      errors.push({ phase: curPhase, text: 'CON ' + m.params.args.map(a => a.value || a.description || '').join(' ').slice(0, 220) });
  });
  await send('Runtime.enable'); await send('Page.enable'); await send('Network.enable');
  /* python http.server sends no cache-control — Chrome heuristically caches JS and serves stale code across edits */
  await send('Network.setCacheDisabled', { cacheDisabled: true });
}
async function goto(url) {
  const loaded = new Promise(res => { const h = m => { if (m.method === 'Page.loadEventFired') { handlers.splice(handlers.indexOf(h), 1); res(); } }; handlers.push(h); });
  /* a hash-only jump is a same-document navigation — no reload, so CSS/JS edits never
     load; a changing ?_cb on the path (before the hash) forces a cold document each time */
  const hi = url.indexOf('#');
  const path = hi >= 0 ? url.slice(0, hi) : url;
  const hash = hi >= 0 ? url.slice(hi) : '';
  await send('Page.navigate', { url: path + (path.indexOf('?') >= 0 ? '&' : '?') + '_cb=' + Date.now() + hash });
  await Promise.race([loaded, sleep(6000)]);
  await sleep(150);
}
async function shot(name) {
  await sleep(80);
  const b = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(SHOTS, name), Buffer.from(b.data, 'base64'));
}
async function setViewport(w, h, mobile) {
  /* mobile:true makes Chrome fit-scale the emulated viewport to the window (390 → 583 observed);
     DSF 2 without the mobile flag gives an exact CSS viewport, which is what the layout check needs */
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: mobile ? 2 : 1, mobile: false });
  for (let i = 0; i < 20; i++) {           /* confirm the override actually applied */
    const iw = await expr('window.innerWidth');
    if (iw === w) return;
    await sleep(100);
  }
  throw new Error('viewport override failed: wanted ' + w + ', got ' + (await expr('window.innerWidth')));
}
async function clearViewport() {
  try { await send('Emulation.clearDeviceMetricsOverride'); } catch (e) { /* ignore */ }
}

/* ---------- A. asset integrity — real browser loads, we only listen -- */
async function phaseAssets() {
  curPhase = 'ASSETS';
  netStatus.clear(); netFailed.length = 0;
  for (const p of ['index.html', 'login.html', 'app.html']) {
    await goto(BASE + '/' + p + (p === 'app.html' ? '#/home' : ''));
    await sleep(600); /* let SPA pull its scripts */
  }
  const bad = [];
  netStatus.forEach((status, url) => {
    if (status >= 400) bad.push(url.replace(BASE + '/', '') + ' -> ' + status);
  });
  const localCount = [...netStatus.keys()].filter(u => u.startsWith(BASE)).length;
  report.push('ASSETS loaded=' + localCount + ' failed-net=' + netFailed.length + ' bad-status=' + bad.length + (bad.length ? ' [' + bad.join(', ') + ']' : ''));
  bad.forEach(b => errors.push({ phase: 'ASSETS', text: 'missing asset: ' + b }));
  netFailed.forEach(f => errors.push({ phase: 'ASSETS', text: 'loading failed: ' + f.text }));
}

/* ---------- helpers --------------------------------------------------- */
async function appReady() { /* wait until SPA rendered the route */
  for (let i = 0; i < 40; i++) {
    const n = await expr(`(document.getElementById('page') && document.getElementById('page').innerHTML.length) || 0`);
    if (n > 200) return n;
    await sleep(120);
  }
  return 0;
}
const DEEP = [
  '#/home', '#/portals', '#/journeys', '#/coverage', '#/directory', '#/reports', '#/writer',
  '#/workspace/M01', '#/workspace/M02', '#/workspace/M33',
  '#/screen/M50-accounts', '#/freg/M01/0', '#/report/M33/0', '#/report/M51/0',
  '#/record/M02-record/WO-9201', '#/screen/M19-close', '#/screen/M20-invoices',
  '#/search/service', '#/screen/M33-360', '#/settings'
];

async function phaseDeepLinks() {
  curPhase = 'DEEP-LINKS';
  let pass = 0;
  for (const h of DEEP) {
    await goto(BASE + '/app.html' + h);
    const n = await appReady();
    const hash = await expr('location.hash');
    const is404 = await expr(`(document.querySelector('#page h1') || {textContent:''}).textContent.indexOf('404') >= 0`);
    if (n > 200 && hash === h && !is404) pass++;
    else errors.push({ phase: 'DEEP-LINKS', text: h + ' rendered=' + n + ' hash=' + hash + ' is404=' + is404 });
  }
  report.push('DEEP-LINKS cold-start pass=' + pass + '/' + DEEP.length + ' (404-guard on)');
}

async function phaseHistory() {
  curPhase = 'HISTORY';
  /* Chrome hardening: programmatic location.hash changes without user activation are
     treated as history REPLACEMENTS — only real clicks push entries. Simulate a user
     with trusted Input.dispatchMouseEvent clicks on the app's own anchor links. */
  const realClick = async sel => {
    const r = await expr(`(function(){ var el = document.querySelector(${JSON.stringify(sel)}); if (!el) return null; el.scrollIntoView({block:'center'}); var b = el.getBoundingClientRect(); return JSON.stringify({ x: b.left + b.width / 2, y: b.top + b.height / 2 }); })()`);
    if (!r) throw new Error('realClick: no element ' + sel);
    const c = JSON.parse(r);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: c.x, y: c.y, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: c.x, y: c.y, button: 'left', clickCount: 1 });
    await sleep(450); await appReady();
  };
  await send('Page.navigate', { url: BASE + '/app.html#/directory' });
  await sleep(1500); await appReady();
  await realClick('a[href="#/workspace/M01"]');
  const h1a = await expr('location.hash');
  await realClick('a[href="#/screen/M01-all"]');
  const h1b = await expr('location.hash');
  await expr(`history.back()`); await sleep(400); await appReady();
  const b1 = await expr('location.hash');
  await expr(`history.back()`); await sleep(400); await appReady();
  const b2 = await expr('location.hash');
  await expr(`history.forward()`); await sleep(400); await appReady();
  const f1 = await expr('location.hash');
  await expr(`history.forward()`); await sleep(400); await appReady();
  const f2 = await expr('location.hash');
  const okBack = h1a === '#/workspace/M01' && h1b === '#/screen/M01-all' &&
    b1 === '#/workspace/M01' && b2 === '#/directory' && f1 === '#/workspace/M01' && f2 === '#/screen/M01-all';
  report.push('HISTORY clicks=' + h1a + ',' + h1b + ' back1=' + b1 + ' back2=' + b2 + ' fwd1=' + f1 + ' fwd2=' + f2 + ' ok=' + okBack);
  if (!okBack) errors.push({ phase: 'HISTORY', text: 'back/forward mismatch ' + [h1a, h1b, b1, b2, f1, f2].join('/') });
}

async function phaseOverflow() {
  curPhase = 'OVERFLOW';
  await setViewport(1600, 900, false);
  let pass = 0; const sample = DEEP.slice(0, 12);
  for (const h of sample) {
    await goto(BASE + '/app.html' + h); await appReady();
    const w = await expr(`document.documentElement.scrollWidth - document.documentElement.clientWidth`);
    if (w <= 1) pass++;
    else errors.push({ phase: 'OVERFLOW', text: h + ' hscroll=+' + w + 'px' });
  }
  report.push('OVERFLOW 1600px pass=' + pass + '/' + sample.length);
}

async function phaseMobile() {
  curPhase = 'MOBILE';
  await setViewport(390, 844, true);
  const applied = await expr('window.innerWidth');
  const views = [['#/home', '17-mobile-home'], ['#/screen/M50-accounts', '18-mobile-grid'], ['#/record/M02-record/WO-9201', '19-mobile-record']];
  let pass = 0;
  for (const v of views) {
    await goto(BASE + '/app.html' + v[0]); await appReady(); await sleep(400);
    const w = await expr(`document.documentElement.scrollWidth - document.documentElement.clientWidth`);
    const n = await expr(`(document.getElementById('page') && document.getElementById('page').innerHTML.length) || 0`);
    if (w <= 1 && n > 200) pass++;
    else errors.push({ phase: 'MOBILE', text: v[0] + ' hscroll=+' + w + 'px rendered=' + n });
    await shot(v[1] + '.png');
  }
  await clearViewport();
  report.push('MOBILE 390px viewport=' + applied + ' pass=' + pass + '/' + views.length + ' shots=3');
}

async function phaseFocus() {
  curPhase = 'FOCUS';
  await setViewport(1600, 900, false);
  await goto(BASE + '/login.html'); await sleep(400);
  const info = await expr(`(function(){
    var el = document.querySelector('input,button,a'); if (!el) return {err:'no control'};
    el.focus();
    var cs = getComputedStyle(el);
    return { tag: el.tagName, outline: cs.outlineStyle + ' ' + cs.outlineWidth, boxShadow: (cs.boxShadow || 'none').slice(0, 60) };
  })()`);
  const ringOK = info && !info.err && ((/solid|dashed|double/i.test(info.outline) && !/none/i.test(info.outline)) || (info.boxShadow && info.boxShadow !== 'none'));
  report.push('FOCUS control=' + (info && info.tag) + ' outline="' + (info && info.outline) + '" shadow="' + (info && info.boxShadow) + '" ring=' + !!ringOK);
  if (!ringOK) errors.push({ phase: 'FOCUS', text: 'no visible focus ring: ' + JSON.stringify(info) });
}

/* ---------- main ------------------------------------------------------ */
(async () => {
  await boot();
  await phaseAssets();
  await phaseDeepLinks();
  await phaseHistory();
  await phaseOverflow();
  await phaseMobile();
  await phaseFocus();
  console.log(report.join('\n'));
  try { ws.close(); } catch (e) { /* already gone */ }
  if (errors.length) {
    console.log('\nERRORS (' + errors.length + '):');
    errors.forEach(e => console.log(' -', e.phase, e.text.slice(0, 200)));
    process.exitCode = 1;
  } else {
    console.log('\nRESULT ALL CLEAN ✓ assets+deep+history+overflow+mobile+focus');
  }
})().catch(e => { console.error('FATAL', e); process.exit(1); });
