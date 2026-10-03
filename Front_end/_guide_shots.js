/* capture guide screenshots: 67 module workspaces + shell/skill screens (CDP) */
'use strict';
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, '..', 'marketing', 'user-guide', 'images');
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let ws, msgId = 0; const pending = new Map();
  const send = (method, params) => new Promise((res, rej) => {
    const id = ++msgId; pending.set(id, { res, rej });
    ws.send(JSON.stringify({ id, method, params: params || {} }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error('timeout ' + method)); } }, 20000);
  });
  const expr = async js => (await send('Runtime.evaluate', { expression: js, returnByValue: true, awaitPromise: true })).result.value;

  let page = null;
  for (let i = 0; i < 50 && !page; i++) {
    try { page = (await (await fetch('http://127.0.0.1:9333/json')).json()).find(t => t.type === 'page'); } catch (e) { /* boot */ }
    if (!page) await sleep(300);
  }
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
  };
  await send('Page.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1.5, mobile: false });
  for (let k = 0; k < 20; k++) { if (await expr('window.innerWidth') === 1440) break; await sleep(100); }

  const BASE = 'http://localhost:8471';
  async function shot(name, full) {
    await sleep(250);
    const b = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: !!full });
    fs.writeFileSync(path.join(OUT, name + '.png'), Buffer.from(b.data, 'base64'));
  }
  async function go(url, wait) {
    await send('Page.navigate', { url });
    await sleep(wait || 1400);
  }

  /* ---- special screens ---- */
  await go(BASE + '/index.html', 1600); await shot('s-landing', true);
  await go(BASE + '/login.html'); await shot('s-login');
  await go(BASE + '/app.html?_cb=' + Date.now() + '#/home', 1800); await shot('s-home', true);
  await expr(`document.querySelectorAll('.nav-area')[0].click(); 0`); await sleep(500); await shot('s-megamenu', true);
  await expr(`(function(){var b=document.querySelectorAll('.nav-area')[0];if(b)b.click();return 0;})()`); await sleep(300);
  const i = await expr(`(function(){var q=document.getElementById('tellme');q.value='VAT';q.dispatchEvent(new Event('input'));return 1;})()`);
  await sleep(600); await shot('s-tellme', false);
  await expr(`(function(){var b=document.getElementById('tm-results');if(b)b.classList.remove('open');var q=document.getElementById('tellme');q.value='';q.blur();return 0;})()`);
  await go(BASE + '/app.html#/screen/M01-all'); await shot('s-grid', true);
  await go(BASE + '/app.html#/record/M01-order/SO-2026-14838'); await shot('s-record', true);
  await go(BASE + '/app.html#/screen/M02-dispatch'); await shot('s-dispatch', true);
  await go(BASE + '/app.html#/screen/M19-close'); await shot('s-console', true);
  await go(BASE + '/app.html#/report/M51/0'); await shot('s-report', true);
  await go(BASE + '/app.html#/writer'); await shot('s-writer', true);
  await go(BASE + '/app.html#/reports'); await shot('s-reportcenter', true);
  await go(BASE + '/app.html#/portals'); await shot('s-portals', true);
  await go(BASE + '/app.html#/journeys'); await shot('s-journeys', true);
  await go(BASE + '/app.html#/directory'); await shot('s-directory', true);
  await go(BASE + '/app.html#/coverage'); await shot('s-coverage', true);
  await go(BASE + '/app.html#/search?q=warranty'); await shot('s-search', true);
  await go(BASE + '/app.html#/freg/M01/0'); await shot('s-freg', true);
  await expr(`document.getElementById('btn-theme').click(); 0`); await sleep(400);
  await go(BASE + '/app.html#/home'); await shot('s-dark', true);
  await expr(`document.getElementById('btn-theme').click(); 0`); await sleep(300);
  await expr(`document.getElementById('btn-lang').click(); 0`); await sleep(600);
  await shot('s-bengali', true);
  await expr(`document.getElementById('btn-lang').click(); 0`); await sleep(400);
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: false });
  for (let k = 0; k < 20; k++) { if (await expr('window.innerWidth') === 390) break; await sleep(100); }
  await go(BASE + '/app.html#/home', 1600); await shot('s-mobile-home', true);
  await expr(`document.getElementById('btn-navtoggle').click(); 0`); await sleep(500); await shot('s-mobile-nav', false);
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1.5, mobile: false });

  /* ---- 67 module workspaces ---- */
  const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'marketing', '_catalog.json'), 'utf8'));
  let n = 0;
  for (const area of catalog) for (const m of area.mods) {
    await go(BASE + '/app.html#/workspace/' + m.mid, 1200);
    await shot('w-' + m.mid, true);
    n++;
  }
  console.log('CAPTURED specials+workspaces=' + n);
  ws.close(); process.exit(0);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
