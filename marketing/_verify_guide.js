/* verify the built user guide over file:// — images, anchors, overflow (CDP) */
'use strict';
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let ws, msgId = 0; const pending = new Map();
  const send = (method, params) => new Promise((res, rej) => {
    const id = ++msgId; pending.set(id, { res, rej });
    ws.send(JSON.stringify({ id, method, params: params || {} }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error('timeout ' + method)); } }, 20000);
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
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'file:///D:/software_project_development/software_project/Software_Project_14/1000%20fix/1000fix_new_erp_system/marketing/user-guide/index.html' });
  await sleep(3500);

  const report = await expr(`(async function(){
    /* force every lazy image to load now: flip to eager, then wait for the decoder */
    document.querySelectorAll('img[loading="lazy"]').forEach(function(i){ i.loading = 'eager'; });
    var imgs = [].slice.call(document.images);
    for (var k = 0; k < 60; k++) {
      await new Promise(function(r){ setTimeout(r, 500); });
      if (imgs.every(function(i){ return i.complete; })) break;
    }
    var broken = imgs.filter(function(i){ return !i.complete || i.naturalWidth === 0; }).map(function(i){ return i.getAttribute('src'); });
    var links = [].slice.call(document.querySelectorAll('nav.toc a[href^="#"]'));
    var missingAnchors = links.map(function(a){ return a.getAttribute('href').slice(1); })
      .filter(function(id){ return !document.getElementById(id); });
    var mods = document.querySelectorAll('section.module').length;
    var areas = document.querySelectorAll('section.area').length;
    return {
      title: document.title,
      imgs: imgs.length, broken: broken.slice(0, 10), brokenCount: broken.length,
      tocLinks: links.length, missingAnchors: missingAnchors.slice(0, 10),
      modules: mods, areas: areas,
      hscroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      bytes: document.documentElement.outerHTML.length
    };
  })()`);
  console.log(JSON.stringify(report, null, 1));

  /* screenshots for vision check: top, a module section, journeys */
  await send('Page.navigate', { url: 'file:///D:/software_project_development/software_project/Software_Project_14/1000%20fix/1000fix_new_erp_system/marketing/user-guide/index.html#welcome' });
  await sleep(1200);
  let b = await send('Page.captureScreenshot', { format: 'png' });
  require('fs').writeFileSync('user-guide/_check_top.png', Buffer.from(b.data, 'base64'));
  await expr(`document.getElementById('mod-M51').scrollIntoView(); 0`);
  await sleep(800);
  b = await send('Page.captureScreenshot', { format: 'png' });
  require('fs').writeFileSync('user-guide/_check_module.png', Buffer.from(b.data, 'base64'));
  await expr(`document.getElementById('portals').scrollIntoView(); 0`);
  await sleep(800);
  b = await send('Page.captureScreenshot', { format: 'png' });
  require('fs').writeFileSync('user-guide/_check_portals.png', Buffer.from(b.data, 'base64'));
  console.log('SHOTS saved');
  ws.close(); process.exit(0);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
