/* one-shot: verify mega menu closes on navigation (fresh Chrome, CDP) */
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
  await sleep(300);
  await send('Page.navigate', { url: 'http://localhost:8471/app.html#/home' });
  await sleep(1200);

  const flag = await expr('(function(){ return !!window.__fxOverlayClose; })()');
  const test = await expr(`(async function(){
    var out = {};
    document.querySelector('.nav-area').click();
    await new Promise(r => setTimeout(r, 300));
    var mg = document.getElementById('megamenu');
    out.openAfterClick = !!(mg && mg.classList.contains('open'));
    out.links = mg ? mg.querySelectorAll('a').length : 0;
    var chip = document.querySelector('#megamenu a.mega-chip');
    out.chip = chip ? chip.textContent.trim().slice(0, 30) : null;
    if (chip) chip.click();
    await new Promise(r => setTimeout(r, 600));
    mg = document.getElementById('megamenu');
    out.stillOpenAfterNav = !!(mg && mg.classList.contains('open'));
    out.hash = location.hash;
    out.h1 = (document.querySelector('#page h1') || {}).textContent || '';
    return out;
  })()`);
  console.log('fixLoaded=' + flag, JSON.stringify(test));
  ws.close(); process.exit(0);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
