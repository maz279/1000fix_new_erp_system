/* meta-audit over CDP: recompute claimed counts from the live payload, diff the
   i18n catalogues, find t() keys missing from EN, and check area/module integrity.
   All analysis runs inside Chrome (Runtime.evaluate) — no Node-side eval. */
'use strict';
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let ws, msgId = 0; const pending = new Map();
  const send = (method, params) => new Promise((res, rej) => {
    const id = ++msgId; pending.set(id, { res, rej });
    ws.send(JSON.stringify({ id, method, params: params || {} }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error('timeout ' + method)); } }, 15000);
  });
  const expr = async js => {
    const r = await send('Runtime.evaluate', { expression: js, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) return { __exc: (r.exceptionDetails.exception || {}).description || r.exceptionDetails.text };
    return r.result.value;
  };

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
  await send('Page.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Page.navigate', { url: 'http://localhost:8471/app.html?_cb=' + Date.now() + '#/coverage' });
  await sleep(1600);

  const out = await expr(`(function(){
    var AREAS = window.FX_AREAS || [], NAV = window.FX_MODULES || {};
    var mods = Object.keys(NAV);
    var r = { mods: mods.length, areas: AREAS.length, groups: 0, screens: 0, reports: 0,
              forms: 0, subs: 0, funcs: 0, dupes: [], orphans: [], noArea: [], fregDelta: [], srcTotal: 0 };
    var ids = {};
    mods.forEach(function (mid) {
      var m = NAV[mid];
      (m.groups || []).forEach(function (g) {
        r.groups++;
        (g.screens || []).forEach(function (sc) {
          r.screens++;
          if (ids[sc.id]) r.dupes.push(sc.id); ids[sc.id] = 1;
        });
      });
      r.reports += (m.reports || []).length;
      r.forms += (m.forms || []).length;
      r.srcTotal += (m.freg && m.freg.src) || 0;
      (m.freg && m.freg.sub || []).forEach(function (fr) { r.subs++; r.funcs += (fr[2] || 0); });
      var subSum = (m.freg && m.freg.sub || []).reduce(function (n, fr) { return n + (fr[2] || 0); }, 0);
      if (m.freg && subSum !== m.freg.src) r.fregDelta.push({ mid: mid, src: m.freg.src, subSum: subSum });
    });
    AREAS.forEach(function (a) {
      (a.mods || []).forEach(function (mid) { if (!NAV[mid]) r.orphans.push(a.id + ':' + mid); });
    });
    mods.forEach(function (mid) {
      if (!AREAS.some(function (a) { return (a.mods || []).indexOf(mid) >= 0; })) r.noArea.push(mid);
    });
    var cat = window.FX_I18N || null;
    r.i18nExposed = !!cat;
    if (cat && cat.en && cat.bn) {
      var ek = Object.keys(cat.en), bk = Object.keys(cat.bn);
      r.enKeys = ek.length; r.bnKeys = bk.length;
      var bnSet = {}; bk.forEach(function (k) { bnSet[k] = 1; });
      r.enOnly = ek.filter(function (k) { return !bnSet[k]; });
      r.bnOnly = bk.filter(function (k) { return !cat.en[k]; });
    }
    var cov = (document.querySelector('#page h1') || {}).textContent || '';
    r.coverageH1 = cov.slice(0, 60);
    var covText = (document.getElementById('page') || {}).innerText || '';
    r.coverageMentions = ['823', '346', '266', '5,100', '67'].filter(function (n) { return covText.indexOf(n) >= 0; });
    return r;
  })()`);

  console.log(JSON.stringify(out, null, 1));
  ws.close(); process.exit(0);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
