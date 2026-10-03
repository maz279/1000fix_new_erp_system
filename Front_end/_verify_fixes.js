/* one-shot: verify iteration-3 fixes live — generic breadcrumb, plain report links,
   Tell-ME keyboard navigation, mobile 390px rail collapse/overlay (CDP) */
'use strict';
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let ws, msgId = 0; const pending = new Map();
  const send = (method, params) => new Promise((res, rej) => {
    const id = ++msgId; pending.set(id, { res, rej });
    ws.send(JSON.stringify({ id, method, params: params || {} }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error('timeout ' + method)); } }, 15000);
  });
  const expr = async js => (await send('Runtime.evaluate', { expression: js, returnByValue: true, awaitPromise: true })).result.value;
  const nav = async url => { await send('Page.navigate', { url }); await sleep(1300); };

  let page = null;
  for (let i = 0; i < 40 && !page; i++) {
    try { page = (await (await fetch('http://127.0.0.1:9333/json')).json()).find(t => t.type === 'page'); } catch (e) { /* boot */ }
    if (!page) await sleep(300);
  }
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
  };
  await send('Page.enable');
  await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await sleep(300);

  const BASE = 'http://localhost:8471';
  const out = {};

  /* 1. generic record page → breadcrumb anchors at a live screen, no 404 */
  await nav(BASE + '/app.html#/record/generic/SO-99914');
  out.generic = await expr(`(function(){
    var bc = document.querySelector('.crumbs a');
    return {
      href: bc ? bc.getAttribute('href') : null,
      h1: (document.querySelector('#page h1') || {}).textContent || '',
      is404: /404/i.test((document.querySelector('#page h1') || {}).textContent || '')
    };
  })()`);

  /* 2. report viewer first column is plain text, not a record link */
  await nav(BASE + '/app.html#/report/M51/0');
  out.reportPlain = await expr(`(function(){
    var t = document.querySelector('.fx-card .fx-table');
    return { idChips: t ? t.querySelectorAll('a.id-chip').length : -1, rows: t ? t.querySelectorAll('tbody tr').length : 0 };
  })()`);

  /* 3. Tell-ME keyboard navigation: type, ArrowDown, Enter follows the active item */
  await nav(BASE + '/app.html#/home');
  out.tellme = await expr(`(async function(){
    var i = document.getElementById('tellme');
    i.value = 'VAT'; i.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 250));
    var kd = function(k){ i.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true })); };
    kd('ArrowDown'); kd('ArrowDown');
    var act = document.querySelector('#tm-results .tm-item.active');
    var want = act ? act.dataset.href : null;
    kd('Enter');
    await new Promise(r => setTimeout(r, 500));
    return { activeFound: !!act, wanted: want, landed: location.hash, followed: !!want && want === location.hash };
  })()`);

  /* 4. mobile 390px: closed rail adds no hscroll; toggle opens overlay; nav click closes it */
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: false });
  for (let k = 0; k < 20; k++) { if (await expr('window.innerWidth') === 390) break; await sleep(100); }
  out.viewport = await expr('window.innerWidth');
  await nav(BASE + '/app.html#/home');
  out.mobile = await expr(`(async function(){
    var o = {};
    o.closedHscroll = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    document.getElementById('btn-navtoggle').click();
    await new Promise(r => setTimeout(r, 300));
    var sh = document.getElementById('fx-shell');
    var nv = document.getElementById('leftnav');
    o.openClass = sh.classList.contains('nav-open');
    var r = nv.getBoundingClientRect();
    o.overlayVisible = r.width > 100 && r.left === 0;
    o.openHscroll = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    var mod = nv.querySelector('.nav-mod'); if (mod) mod.click();
    await new Promise(r2 => setTimeout(r2, 500));
    o.closedAfterNav = !document.getElementById('fx-shell').classList.contains('nav-open');
    o.hashAfterNav = location.hash;
    return o;
  })()`);
  await send('Emulation.clearDeviceMetricsOverride');

  console.log(JSON.stringify(out, null, 1));
  ws.close(); process.exit(0);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
