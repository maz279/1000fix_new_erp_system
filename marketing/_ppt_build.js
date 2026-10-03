/* 1000 FiX ERP — System Overview deck (pptxgenjs, LAYOUT_WIDE)
   Run: NODE_PATH=$(npm root -g) node _ppt_build.js  */
'use strict';
const path = require('path');
const pptxgen = require('pptxgenjs');

const IMG = n => path.join(__dirname, '_ppt_imgs', n + '.png');

/* palette — Service-Teal brand of the ERP */
const C = {
  bgLight: 'FFFFFF', bgDark: '0B3B36',
  primary: '0E7A6E', primaryDark: '0A5A50', wash: 'EAF4F2', tint: '9FC9C2',
  accent: 'B45309', text: '17211F', muted: '5B6B68', lightText: 'F2F7F6', lightMuted: 'A9C4BF',
  white: 'FFFFFF'
};
const FONT = 'Segoe UI';
const W = 13.33, H = 7.5, M = 0.5;

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.author = '1000 FiX Services Ltd.';
pres.title = '1000 FiX ERP — System Overview & Employee Tour';

const bu = () => ({ code: '2013', indent: 12 });
const shadow = () => ({ type: 'outer', color: '0B3B36', blur: 7, offset: 2, angle: 45, opacity: 0.18 });

function pageChrome(s, n, dark) { /* slide number + footer, no bars */
  s.addText([{ text: '1000 FiX ERP \u00b7 System Overview', options: {} }], {
    x: M, y: H - 0.38, w: 4.5, h: 0.28, fontSize: 10.5, fontFace: FONT,
    color: dark ? C.lightMuted : C.muted, margin: 0 });
  s.addText(String(n), { x: W - 0.9, y: H - 0.38, w: 0.4, h: 0.28, fontSize: 10.5,
    fontFace: FONT, color: dark ? C.lightMuted : C.muted, align: 'right', margin: 0 });
}
function h1(s, kicker, title, dark) {
  s.addText(kicker.toUpperCase(), { x: M, y: 0.42, w: W - 2 * M, h: 0.3, fontSize: 12.5,
    fontFace: FONT, bold: true, charSpacing: 3, color: dark ? C.tint : C.primary, margin: 0 });
  s.addText(title, { x: M, y: 0.72, w: W - 2 * M, h: 0.62, fontSize: 30, fontFace: FONT,
    bold: true, color: dark ? C.white : C.text, margin: 0 });
}
/* motif: screenshot in a rounded wash card + caption */
function shot(s, img, x, y, w, h, caption, dark) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x - 0.08, y: y - 0.08, w: w + 0.16, h: h + 0.16,
    fill: { color: dark ? C.primaryDark : C.wash }, rectRadius: 0.09, line: { type: 'none' } });
  s.addImage({ path: IMG(img), x, y, w, h, sizing: { type: 'cover', w, h }, shadow: shadow() });
  if (caption) s.addText(caption, { x, y: y + h + 0.1, w, h: 0.3, fontSize: 12,
    fontFace: FONT, color: dark ? C.lightMuted : C.muted, margin: 0 });
}
function stat(s, x, y, w, num, label, dark, acc) {
  s.addText(num, { x, y, w, h: 0.95, fontSize: 60, fontFace: FONT, bold: true,
    color: acc ? C.accent : (dark ? C.white : C.primary), margin: 0 });
  s.addText(label, { x, y: y + 0.98, w, h: 0.55, fontSize: 14, fontFace: FONT,
    color: dark ? C.lightMuted : C.muted, margin: 0 });
}
function chip(s, x, y, w, txt) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.34, fill: { color: C.wash },
    rectRadius: 0.17, line: { type: 'none' } });
  s.addText(txt, { x, y: y + 0.015, w, h: 0.31, fontSize: 11.5, fontFace: FONT, bold: true,
    color: C.primaryDark, align: 'center', margin: 0 });
}
function bulletList(s, items, x, y, w, h, opts) {
  s.addText(items.map((t, i) => ({ text: t,
    options: { bullet: bu(), breakLine: i < items.length - 1 } })), Object.assign({
    x, y, w, h, fontSize: 15, fontFace: FONT, color: C.text, paraSpaceAfter: 9, margin: 0, valign: 'top'
  }, opts || {}));
}

let pageNo = 0;
function newSlide(dark) { const s = pres.addSlide(); pageNo++; s.background = { color: dark ? C.bgDark : C.bgLight }; pageChrome(s, pageNo, dark); return s; }

/* ============ 1 · TITLE (dark) ============ */
(() => {
  const s = newSlide(true);
  s.addText('1000 FiX SERVICES LTD. \u00b7 INTERNAL', { x: M, y: 0.75, w: 8, h: 0.32,
    fontSize: 13, fontFace: FONT, bold: true, charSpacing: 4, color: C.tint, margin: 0 });
  s.addText('The 1000 FiX ERP', { x: M, y: 1.85, w: 11, h: 1.05, fontSize: 64, fontFace: FONT,
    bold: true, color: C.white, margin: 0 });
  s.addText('One connected system for every order, part, invoice, technician hour\nand customer conversation \u2014 a tour for every employee.', {
    x: M, y: 3.0, w: 9.4, h: 0.95, fontSize: 19, fontFace: FONT, color: C.lightText, margin: 0 });
  const stats = [['67', 'modules'], ['823', 'screens'], ['346', 'reports'], ['12', 'portals'], ['5,100', 'functions']];
  stats.forEach((st, i) => {
    s.addText(st[0], { x: M + i * 2.35, y: 4.45, w: 2.1, h: 0.8, fontSize: 44, fontFace: FONT, bold: true, color: i === 0 ? C.tint : C.white, margin: 0 });
    s.addText(st[1], { x: M + i * 2.35, y: 5.3, w: 2.1, h: 0.35, fontSize: 13.5, fontFace: FONT, color: C.lightMuted, margin: 0 });
  });
  s.addText('Edition 2.0 \u00b7 September 2026 \u00b7 Hotline 16743 \u00b7 ISO 9001:2015 Certified', {
    x: M, y: 6.35, w: 9, h: 0.35, fontSize: 13, fontFace: FONT, color: C.lightMuted, margin: 0 });
  s.addNotes('Welcome. This deck is the 20-minute companion to the full Employee User Guide. Audience: every employee, no ERP background assumed.');
})();

/* ============ 2 · THE ONE IDEA ============ */
(() => {
  const s = newSlide();
  h1(s, 'Why it matters', 'One idea explains the whole system');
  s.addText('\u201CNothing is typed twice.\u201D', { x: M, y: 1.75, w: 7.2, h: 1.0, fontSize: 44,
    fontFace: FONT, bold: true, color: C.primary, margin: 0 });
  s.addText('The hotline agent creates an order. The technician, the workshop, the parts counter, the cashier, the accountant and the manager all work on that same order \u2014 each from their own screen. Do your step well and everyone downstream inherits it.', {
    x: M, y: 2.95, w: 7.0, h: 1.6, fontSize: 17, fontFace: FONT, color: C.text, margin: 0 });
  bulletList(s, [
    'Every customer touchpoint \u2014 hotline 16743, web, app, branch counter \u2014 lands in the same system',
    'Every module reads and writes one shared record, so numbers agree everywhere',
    'Your work is visible, attributable and auditable \u2014 that is what ISO-grade service means'],
    M, 4.75, 7.0, 1.9);
  shot(s, 's-landing-half', 8.1, 1.7, 4.7, 3.92, 'What customers see is powered by the same ERP you work in');
  s.addNotes('Anchor slide. If listeners remember one thing: one order object flows through every role. Screenshots: public landing page.');
})();

/* ============ 3 · BY THE NUMBERS ============ */
(() => {
  const s = newSlide();
  h1(s, 'Scope', 'The system by the numbers');
  stat(s, M, 1.8, 3.6, '67', 'modules across 11 business areas', false, true);
  stat(s, 4.6, 1.8, 3.6, '823', 'screens \u2014 grids, records, consoles, dashboards');
  stat(s, 8.7, 1.8, 3.6, '346', 'built-in reports, plus a no-code report writer');
  stat(s, M, 3.9, 3.6, '266', 'data-entry forms with live validation');
  stat(s, 4.6, 3.9, 3.6, '5,100', 'registered functions in 600 sub-modules');
  stat(s, 8.7, 3.9, 3.6, '12', 'portals for every audience \u2014 customer to vendor');
  s.addText('Source: 1000 FiX ERP coverage screen (#/coverage) \u2014 machine-verified against the live navigation data, September 2026.', {
    x: M, y: 6.15, w: 12.3, h: 0.4, fontSize: 11.5, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('All figures are machine-checked by the system itself on the Coverage screen \u2014 not marketing numbers.');
})();

/* ============ 4 · THE MAP (chart) ============ */
(() => {
  const s = newSlide();
  h1(s, 'Orientation', 'Eleven areas carry the whole company');
  const areas = [
    ['A02 Service Operations', 7], ['A03 Customer Experience', 7], ['A04 Commercial & Revenue', 9],
    ['A05 Circular Economy', 3], ['A06 Supply Chain', 6], ['A07 Assets & Facilities', 5],
    ['A08 Finance & Treasury', 8], ['A09 People & Workforce', 7], ['A10 Quality & Governance', 4],
    ['A11 Insights & Intelligence', 4], ['A12 Platform & Technology', 7]
  ];
  s.addChart(pres.charts.BAR, [{
    name: 'Modules', labels: areas.map(a => a[0]), values: areas.map(a => a[1])
  }], {
    x: M, y: 1.55, w: 7.6, h: 5.0, barDir: 'bar',
    chartColors: [C.primary], chartArea: { fill: { color: C.bgLight } },
    catAxisLabelColor: C.text, catAxisLabelFontSize: 11.5, catAxisLabelFontFace: FONT,
    valAxisLabelColor: C.muted, valAxisLabelFontSize: 11, valAxisLabelFontFace: FONT,
    valAxisMaxVal: 10, valGridLine: { color: 'E2E8F0', size: 0.5 }, catGridLine: { style: 'none' },
    showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: C.primaryDark, dataLabelFontSize: 11.5,
    showLegend: false, showTitle: false
  });
  s.addText('The same eleven groups are the left navigation in the app \u2014 learn the map once, navigate forever.', {
    x: 8.5, y: 1.8, w: 4.3, h: 1.1, fontSize: 16, fontFace: FONT, color: C.text, margin: 0 });
  shot(s, 's-directory-half', 8.5, 3.15, 4.3, 3.58, 'The A\u2013Z Directory (#/directory) lists every module');
  s.addText('Source: system navigation data (12 areas incl. Home role centre).', {
    x: M, y: 6.6, w: 9, h: 0.3, fontSize: 11, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('Left nav = this map. Note the balance: operations and finance are the biggest areas.');
})();

/* ============ 5 · GETTING STARTED ============ */
(() => {
  const s = newSlide();
  h1(s, 'Getting started', 'Log in with your own identity');
  const steps = [
    ['1', 'Open the ERP in any browser \u2014 desktop or phone'],
    ['2', 'Work email + password (issued by IT, module M66)'],
    ['3', '6-digit TOTP code \u2014 the box auto-advances'],
    ['4', 'You land on your Role Centre, built for your job']
  ];
  steps.forEach((st, i) => {
    const y = 1.75 + i * 1.06;
    s.addShape(pres.shapes.OVAL, { x: M, y, w: 0.52, h: 0.52, fill: { color: C.primary }, line: { type: 'none' } });
    s.addText(st[0], { x: M, y: y - 0.017, w: 0.52, h: 0.55, fontSize: 20, fontFace: FONT, bold: true, color: C.white, align: 'center', margin: 0 });
    s.addText(st[1], { x: 1.28, y: y + 0.035, w: 5.9, h: 0.5, fontSize: 16.5, fontFace: FONT, color: C.text, margin: 0 });
  });
  s.addText('Never share your login \u2014 every action is attributed to you (M29) and kept in the audit trail.', {
    x: M, y: 6.05, w: 6.6, h: 0.7, fontSize: 13.5, fontFace: FONT, italic: true, color: C.accent, margin: 0 });
  shot(s, 's-login-wide', 8.0, 1.7, 4.8, 3.0, 'Login \u2014 email, password, TOTP');
  s.addNotes('MFA is mandatory; accounts are personal. Corrections are normal, hiding mistakes is not.');
})();

/* ============ 6 · SHELL TOUR ============ */
(() => {
  const s = newSlide();
  h1(s, 'Getting started', 'The screen you\u2019ll live in');
  shot(s, 's-home-wide', M, 1.6, 8.0, 5.0, 'The Role Centre (#/home) \u2014 KPIs, approvals and your worklist; everything is clickable');
  const feats = [
    ['Tell-ME search', 'Alt+Q \u2014 finds any screen, report or record'],
    ['Tab strip', 'browser-style tabs, session restored on login'],
    ['Breadcrumbs', 'you always know where you are'],
    ['Top-right', 'language, density, dark mode, copilot, profile']
  ];
  feats.forEach((f, i) => {
    const y = 1.7 + i * 1.22;
    s.addText(f[0], { x: 8.9, y, w: 4.0, h: 0.32, fontSize: 15.5, fontFace: FONT, bold: true, color: C.primaryDark, margin: 0 });
    s.addText(f[1], { x: 8.9, y: y + 0.33, w: 4.0, h: 0.6, fontSize: 13, fontFace: FONT, color: C.muted, margin: 0 });
  });
  s.addNotes('Demo tip: click a KPI, open the mega menu, switch language live.');
})();

/* ============ 7 · MEGA MENU + TELL-ME ============ */
(() => {
  const s = newSlide();
  h1(s, 'Getting started', 'Two ways to reach anything');
  shot(s, 's-megamenu-half', M, 1.65, 5.85, 4.88, 'Click an area \u2014 the mega menu catalogues every screen');
  shot(s, 's-tellme-half', 6.98, 1.65, 5.85, 4.88, 'Tell-ME \u2014 \u201CVAT\u201D grouped into pages, modules, reports, records');
  s.addText('Keyboard: Alt+Q \u2192 type \u2192 \u2193/\u2191 \u2192 Enter follows the highlighted result.', {
    x: M, y: 6.75, w: 12.3, h: 0.35, fontSize: 13.5, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('The mega menu shows structure; Tell-ME is the shortcut habit. Both work in Bangla.');
})();

/* ============ 8 · PERSONAL ============ */
(() => {
  const s = newSlide();
  h1(s, 'Getting started', 'Make the system yours');
  shot(s, 's-dark-half', M, 1.65, 3.95, 3.29, 'Dark mode');
  shot(s, 's-bengali-half', 4.69, 1.65, 3.95, 3.29, '\u09AC\u09BE\u0982\u09B2\u09BE \u2014 one button');
  s.addImage({ path: IMG('s-mobile-home-tall'), x: 9.35, y: 1.65, w: 2.1, h: 4.35, sizing: { type: 'contain', w: 2.1, h: 4.35 } });
  s.addText('On phones', { x: 9.35, y: 6.1, w: 2.1, h: 0.3, fontSize: 12, fontFace: FONT, color: C.muted, align: 'center', margin: 0 });
  bulletList(s, [
    'Language switches instantly \u2014 EN / \u09AC\u09BE\u0982\u09B2\u09BE across the whole shell',
    'Density: compact for cash desks, relaxed for reading',
    'Dark mode remembered per device; charts tuned for both themes',
    'On a phone the rail collapses to an overlay that closes on navigation'],
    M, 5.35, 8.3, 1.6, { fontSize: 13.5 });
  s.addNotes('Personalisation is per user and per device \u2014 no admin needed.');
})();

/* ============ 9 · SKILL: GRIDS ============ */
(() => {
  const s = newSlide();
  h1(s, 'Core skill 1 of 5', 'Work the grid \u2014 filter, view, open');
  shot(s, 's-grid-wide', 4.6, 1.6, 8.2, 5.12, 'All Service Orders \u2014 filter pane, saved views, row links into records');
  bulletList(s, [
    'Filter pane on the left \u2014 filters combine into chips',
    'Saved views: team-shared or your own, kept per user',
    'Column menu (\u22EE): sort, show, hide',
    'First column always links to the full record',
    'Export any grid to XLSX / CSV']
    , M, 1.8, 3.85, 3.4);
  s.addNotes('Grids are the default screen type (429 of them). Teach filtering once, productivity forever.');
})();

/* ============ 10 · SKILL: RECORD + BPF ============ */
(() => {
  const s = newSlide();
  h1(s, 'Core skill 2 of 5', 'Advance work on the process bar');
  const steps = ['Received', 'Diagnosing', 'Estimate', 'Approved', 'In Progress', 'QC', 'Ready', 'Delivered'];
  steps.forEach((st, i) => {
    const x = M + i * 1.51;
    s.addShape(pres.shapes.CHEVRON, { x, y: 1.62, w: 1.6, h: 0.62,
      fill: { color: i < 5 ? C.primary : C.wash }, line: { type: 'none' } });
    s.addText(st, { x: x + 0.12, y: 1.65, w: 1.36, h: 0.56, fontSize: 10.5, fontFace: FONT,
      bold: true, color: i < 5 ? C.white : C.primaryDark, align: 'center', valign: 'middle', margin: 0 });
  });
  bulletList(s, [
    'Click the next stage to advance it \u2014 required fields are enforced first',
    'The FactBox (right) carries customer, device, warranty, history',
    'Tabs hold Lines, Documents and the full audit trail',
    'Same pattern on work orders, claims, POs, contracts \u2014 learn it once'],
    M, 2.7, 7.3, 2.2);
  s.addText('The business process flow is the system\u2019s spine \u2014 it is how custody, approval and quality gates stay enforceable.', {
    x: M, y: 5.15, w: 7.3, h: 0.8, fontSize: 14, fontFace: FONT, italic: true, color: C.accent, margin: 0 });
  shot(s, 's-record-half', 8.4, 2.7, 4.32, 3.6, 'A service order \u2014 steps, tabs and the FactBox');
  s.addNotes('Walk one order across the bar live. Point at QC: nothing ships without the gate.');
})();

/* ============ 11 · SKILL: REPORTS ============ */
(() => {
  const s = newSlide();
  h1(s, 'Core skill 3 of 5', 'Run reports \u2014 or write your own');
  shot(s, 's-report-half', M, 1.65, 5.0, 3.55, 'Built-in report \u2014 parameters, run, charts, export');
  shot(s, 's-writer-half', 6.6, 1.65, 5.0, 3.55, 'The 7-step report writer \u2014 no SQL, no IT ticket');
  bulletList(s, [
    'Report Center: 346 built-ins, browsable by module',
    'Schedule any report \u2014 e.g. Monday 08:00 to your inbox',
    'Your saved reports sit beside the built-ins and can be shared'],
    M, 5.85, 12.3, 1.0, { fontSize: 13.5 });
  s.addNotes('If a number matters weekly, it should arrive \u2014 not be hunted.');
})();

/* ============ 12 · SKILL: DASHBOARDS & CONSOLES ============ */
(() => {
  const s = newSlide();
  h1(s, 'Core skills 4 & 5', 'Monitor on dashboards, close on consoles');
  shot(s, 's-dispatch-half', M, 1.65, 5.85, 4.88, 'Dispatch Board (M02) \u2014 zones as columns, cards as jobs');
  shot(s, 's-console-half', 6.98, 1.65, 5.85, 4.88, 'Month-End Close console (M19) \u2014 a tracked checklist');
  s.addNotes('Dashboards watch the now; consoles walk periodic duty. 360 views complete the trio.');
})();

/* ============ 13 · DIVIDER (dark) ============ */
(() => {
  const s = newSlide(true);
  s.addText('MODULE BY MODULE', { x: M, y: 2.1, w: 10, h: 0.4, fontSize: 14, fontFace: FONT,
    bold: true, charSpacing: 5, color: C.tint, margin: 0 });
  s.addText('Eleven areas,\nsixty-seven modules', { x: M, y: 2.6, w: 11, h: 2.2, fontSize: 54,
    fontFace: FONT, bold: true, color: C.white, margin: 0 });
  s.addText('Each area on the next eleven slides: what it covers, the modules inside it, one live screen, and why it matters to you. The full walkthrough for every module lives in the Employee User Guide.', {
    x: M, y: 5.0, w: 10.5, h: 1.0, fontSize: 16.5, fontFace: FONT, color: C.lightText, margin: 0 });
  s.addNotes('Pace: ~60 seconds per area slide. Dive deeper where the audience works.');
})();

/* ---- area slide factory ---- */
const AREAS = [
  { id: 'A02', name: 'Service Operations', bn: '\u09B8\u09BE\u09B0\u09CD\u09AD\u09BF\u09B8 \u0985\u09AA\u09BE\u09B0\u09C7\u09B6\u09A8', hero: 'w-M02',
    intro: 'The heart of 1000 FiX \u2014 receive, dispatch, repair and return every customer device.',
    mods: 'M01 Requests & Orders \u00b7 M02 Dispatch \u00b7 M31 Workshop \u00b7 M03 Logistics \u00b7 M04 Branch \u00b7 M05 Remote/MSP \u00b7 M06 Data Recovery',
    why: ['SLA, TAT and first-time-fix are the numbers this area lives or dies on', 'Signed job sheet at intake = legal proof of custody', 'Dispatch balances skill, zone and travel in one board'] },
  { id: 'A03', name: 'Customer Experience', bn: '\u0995\u09BE\u09B8\u09CD\u099F\u09AE\u09BE\u09B0 \u0985\u09AD\u09BF\u099C\u09C1\u0997\u09C1\u09B2\u09BF', hero: 'w-M27',
    intro: 'Everything customer-facing before and after the repair \u2014 including the 16743 hotline.',
    mods: 'M33 Party Master \u00b7 M07 CRM \u00b7 M10 Loyalty \u00b7 M34 CX & Complaints \u00b7 M27 Contact Centre \u00b7 M32 Bengali AI \u00b7 M35 Campaigns',
    why: ['One party, one record \u2014 duplicates destroy loyalty and warranty lookups', 'Complaints close with root cause, feeding ISO CAPA', 'The Bengali chatbot deflects routine status calls 24/7'] },
  { id: 'A04', name: 'Commercial & Revenue', bn: '\u09AC\u09BE\u09A3\u09BF\u099C\u09CD\u09AF \u0993 \u09B0\u09C7\u09AD\u09C7\u09A8\u09BF\u0989', hero: 'w-M11',
    intro: 'How services are priced, quoted, contracted and sold \u2014 catalogue to partner channel.',
    mods: 'M37 Catalogue \u00b7 M11 Pricing \u00b7 M36 Quotations \u00b7 M08 AMC \u00b7 M09 Warranty \u00b7 M39 Subscriptions \u00b7 M38 E-Commerce \u00b7 M12 Marketplace \u00b7 M40 Partners',
    why: ['Same service, same tier, same price \u2014 everywhere', 'AMC entitlements checked at intake, not by memory', 'Warranty decides who pays \u2014 claims actually get claimed'] },
  { id: 'A05', name: 'Circular Economy', bn: '\u09B8\u09BE\u09B0\u09CD\u0995\u09C1\u09B2\u09BE\u09B0 \u0985\u09B0\u09CD\u09A5\u09A8\u09C0\u09A4\u09BF', hero: 'w-M13',
    intro: 'Rental & Device-as-a-Service, certified trade-in and refurbishment, compliant e-waste recycling.',
    mods: 'M13 Rental/EaaS \u00b7 M14 Trade-In & Refurb \u00b7 M18 E-Waste',
    why: ['Fleet utilisation is the profitability dial for EaaS', 'Graded refurb stock sells with warranty tiers', 'Recycling certificates satisfy auditors and corporate donors'] },
  { id: 'A06', name: 'Supply Chain', bn: '\u09B8\u09BE\u09AA\u09CD\u09B2\u09BE\u0987 \u099A\u09C7\u0987\u09A8', hero: 'w-M15',
    intro: 'Parts and materials \u2014 inventory, procurement, suppliers, planning and import compliance.',
    mods: 'M15 Parts Inventory \u00b7 M41 Warehouse \u00b7 M16 Procurement \u00b7 M42 Suppliers \u00b7 M43 Planning \u00b7 M44 Import',
    why: ['Parts availability is the #1 driver of first-time-fix', 'Three-way match: order \u2194 receipt \u2194 invoice before payment', 'Landed cost with duty and freight rolls into part cost'] },
  { id: 'A07', name: 'Assets & Facilities', bn: '\u0985\u09CD\u09AF\u09BE\u09B8\u09C7\u099F \u0993 \u09AB\u09C7\u09B8\u09BF\u09B2\u09BF\u099F\u09BF', hero: 'w-M17',
    intro: 'The physical backbone \u2014 customer devices, test equipment, fleet, branches, IoT telemetry.',
    mods: 'M17 Device Registry \u00b7 M45 Enterprise Assets \u00b7 M46 Fleet \u00b7 M47 Facilities \u00b7 M48 IoT & Predictive',
    why: ['Any device\u2019s full history in two clicks', 'Calibration due dates never slip \u2014 QC depends on them', 'Predictive telemetry turns break-fix into planned visits'] },
  { id: 'A08', name: 'Finance & Treasury', bn: '\u09AB\u09BE\u0987\u09A8\u09BE\u09A8\u09CD\u09B8 \u0993 \u099F\u09CD\u09B0\u09C7\u099C\u09B0\u09BF', hero: 'w-M51',
    intro: 'Money \u2014 GL, invoicing with Mushak 6.3, treasury across bKash/Nagad, tax, revenue, assets, FP&A.',
    mods: 'M19 GL \u00b7 M20 AR & Invoicing \u00b7 M52 AP & Expense \u00b7 M50 Treasury \u00b7 M51 Tax (BD) \u00b7 M53 Revenue \u00b7 M49 Fixed Assets \u00b7 M54 FP&A',
    why: ['Every taxable supply carries a Mushak 6.3; monthly 9.1 assembles itself', 'Bank, bKash and Nagad reconcile daily', 'Month-end is a console checklist, not a fire drill'] },
  { id: 'A09', name: 'People & Workforce', bn: '\u09AA\u09BF\u09AA\u09C1\u09B2 \u0993 \u0993\u09AF\u09BC\u09BE\u09B0\u09CD\u0995\u09AB\u09CB\u09B0\u09CD\u09B8', hero: 'w-M56',
    intro: 'HR lifecycle, rostering, payroll with statutory deductions, performance, learning, hiring, safety.',
    mods: 'M21 Core HR \u00b7 M55 Time & Roster \u00b7 M56 Payroll \u00b7 M57 Performance \u00b7 M22 Learning \u00b7 M58 Talent \u00b7 M59 H&S',
    why: ['Rosters follow forecast workload; attendance feeds payroll untouched', 'Incentives compute from system data \u2014 jobs, CSAT, upsell', 'Expired certificates block dispatch automatically'] },
  { id: 'A10', name: 'Quality & Governance', bn: '\u0995\u09CB\u09AF\u09BC\u09BE\u09B2\u09BF\u099F\u09BF \u0993 \u0997\u09AD\u09BE\u09B0\u09CD\u09A8\u09C7\u09A8\u09CD\u09B8', hero: 'w-M23',
    intro: 'The trust layer \u2014 ISO 9001 quality system, risk, controlled documents with e-signature, knowledge.',
    mods: 'M23 Quality (ISO) \u00b7 M60 GRC \u00b7 M24 Documents & E-Sign \u00b7 M61 Knowledge',
    why: ['We are Bangladesh\u2019s only ISO 9001:2015 certified IT service provider', 'Non-conformances flow into CAPA with owners and deadlines', 'Fix knowledge lives in a library, not in senior heads'] },
  { id: 'A11', name: 'Insights & Intelligence', bn: '\u0987\u09A8\u09B8\u09BE\u0987\u099F \u0993 \u0987\u09A8\u09CD\u099F\u09C7\u09B2\u09BF\u099C\u09C7\u09A8\u09CD\u09B8', hero: 'w-M26',
    intro: 'Governed dashboards, the 14-model AI portfolio, the data platform and process automation.',
    mods: 'M25 BI \u00b7 M26 AI/ML (14 models) \u00b7 M62 Data Platform \u00b7 M63 Automation',
    why: ['One metric, one definition \u2014 dashboard arguments end', 'Dispatch, churn and demand predictions arrive with explanations', 'Robots copy; people judge \u2014 exceptions stay human'] },
  { id: 'A12', name: 'Platform & Technology', bn: '\u09AA\u09CD\u09B2\u09BE\u099F\u09AB\u09B0\u09CD\u09AE \u0993 \u099F\u09C7\u0995\u09A8\u09CB\u09B2\u099C\u09BF', hero: 'w-M29',
    intro: 'The foundation \u2014 integrations, identity & security, administration, master data, entities, IT, projects.',
    mods: 'M28 Integration/API \u00b7 M29 Identity & Security \u00b7 M30 Admin \u00b7 M64 MDM \u00b7 M65 Multi-Entity \u00b7 M66 Internal IT \u00b7 M67 Projects',
    why: ['bKash, Nagad, couriers, storefronts \u2014 one governed connection layer', 'Role-based access: everyone sees exactly their job', 'Group growth never means a new ERP'] }
];
AREAS.forEach(a => {
  const s = newSlide();
  s.addText(a.id + ' \u00b7 ' + a.name.toUpperCase(), { x: M, y: 0.42, w: 9.5, h: 0.3, fontSize: 12.5,
    fontFace: FONT, bold: true, charSpacing: 3, color: C.primary, margin: 0 });
  s.addText(a.name, { x: M, y: 0.72, w: 7.3, h: 0.62, fontSize: 30, fontFace: FONT, bold: true, color: C.text, margin: 0 });
  s.addText(a.bn, { x: M, y: 1.34, w: 7.3, h: 0.34, fontSize: 15, fontFace: FONT, color: C.muted, margin: 0 });
  s.addText(a.intro, { x: M, y: 1.86, w: 7.2, h: 0.75, fontSize: 16.5, fontFace: FONT, color: C.text, margin: 0 });
  bulletList(s, a.why, M, 2.8, 7.2, 2.0, { fontSize: 14.5 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.15, w: 7.25, h: 1.42, fill: { color: C.wash }, rectRadius: 0.09, line: { type: 'none' } });
  s.addText('MODULES', { x: M + 0.18, y: 5.28, w: 3, h: 0.26, fontSize: 10.5, fontFace: FONT, bold: true, charSpacing: 2, color: C.primaryDark, margin: 0 });
  s.addText(a.mods, { x: M + 0.18, y: 5.56, w: 6.9, h: 0.95, fontSize: 12.5, fontFace: FONT, color: C.text, margin: 0 });
  shot(s, a.hero + '-half', 8.15, 1.65, 4.65, 3.88, 'Live workspace \u2014 ' + a.hero + ' (Tell-ME \u2192 ' + a.hero + ')');
  s.addNotes('Area ' + a.id + '. Hero screenshot: ' + a.hero + ' workspace. Full module detail: Employee User Guide Part 4.');
});

/* ============ 25 · PORTALS ============ */
(() => {
  const s = newSlide();
  h1(s, 'One system, many doors', 'Twelve portals for every audience');
  shot(s, 's-portals-wide', M, 1.6, 7.3, 4.56, 'The Portals screen (#/portals) \u2014 audiences and scale');
  const P = [
    ['P01 Customer App', '250 K+/mo'], ['P02 Technician', '650 techs'], ['P03 Operations', 'floor supervisors'],
    ['P04 Corporate B2B', 'AMC clients'], ['P05 Vendor/Partner', 'suppliers'], ['P06 Analytics/BI', 'analysts'],
    ['P07 AI Assistant', 'Bengali chat'], ['P08 Finance Hub', 'accountants'], ['P09 Rider', 'pick & drop'],
    ['P10 Admin', 'platform'], ['P11 Audit/Compliance', 'auditors'], ['P12 Knowledge', 'all staff']
  ];
  P.forEach((p, i) => {
    const col = Math.floor(i / 6), row = i % 6;
    const x = 8.25 + col * 2.35, y = 1.75 + row * 0.78;
    s.addText(p[0], { x, y, w: 2.3, h: 0.3, fontSize: 12.5, fontFace: FONT, bold: true, color: C.primaryDark, margin: 0 });
    s.addText(p[1], { x, y: y + 0.3, w: 2.3, h: 0.28, fontSize: 11, fontFace: FONT, color: C.muted, margin: 0 });
  });
  s.addText('A portal is a role-scoped front door over the same data \u2014 created once, visible everywhere.', {
    x: M, y: 6.45, w: 12.3, h: 0.35, fontSize: 13.5, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('Emphasise: customer booking in P01 becomes the same service order worked in P03.');
})();

/* ============ 26 · JOURNEY ============ */
(() => {
  const s = newSlide();
  h1(s, 'How work flows', 'Booking to delivery \u2014 one journey of ten');
  const J = [
    ['Customer', 'books in the app (P01), Bengali UI, picks symptom + slot'],
    ['Party M33', 'OTP identity \u2014 golden record matched or created'],
    ['Order M01', 'service order created, device custody + job sheet'],
    ['Dispatch M02', 'best technician scored by skill, zone, travel'],
    ['Field M02/M31', 'diagnose \u2192 estimate \u2192 approve \u2192 repair \u2192 QC'],
    ['Close M20', 'invoice with Mushak 6.3, bKash/Nagad receipt, CSAT survey']
  ];
  J.forEach((st, i) => {
    const x = M + (i % 3) * 4.15, y = 1.7 + Math.floor(i / 3) * 1.72;
    s.addShape(pres.shapes.OVAL, { x, y, w: 0.46, h: 0.46, fill: { color: i === 5 ? C.accent : C.primary }, line: { type: 'none' } });
    s.addText(String(i + 1), { x, y: y - 0.015, w: 0.46, h: 0.49, fontSize: 17, fontFace: FONT, bold: true, color: C.white, align: 'center', margin: 0 });
    s.addText(st[0], { x: x + 0.62, y: y - 0.03, w: 3.4, h: 0.3, fontSize: 14.5, fontFace: FONT, bold: true, color: C.primaryDark, margin: 0 });
    s.addText(st[1], { x: x + 0.62, y: y + 0.28, w: 3.4, h: 0.85, fontSize: 12.5, fontFace: FONT, color: C.muted, margin: 0 });
  });
  s.addText('All ten journeys, interactive, at #/journeys \u2014 every step names its owner and screen.', {
    x: M, y: 5.5, w: 6.9, h: 0.7, fontSize: 13.5, fontFace: FONT, color: C.muted, margin: 0 });
  s.addText('Source: system journey register (10 journeys \u00b7 64 steps).', { x: M, y: 6.6, w: 8, h: 0.3, fontSize: 11, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('Follow the order, not the org chart \u2014 that is the systems thinking the ERP teaches.');
})();

/* ============ 27 · PERSONAS ============ */
(() => {
  const s = newSlide();
  h1(s, 'Whose screen is whose', 'Four personas, four role centres');
  const PS = [
    ['Rahim Uddin', 'CTO / Super Admin', 'platform health, access, roadmap'],
    ['Nusrat Jahan', 'Service Manager', 'dispatch board, SLA, WIP ageing'],
    ['Tanvir Ahmed', 'Accountant', 'close console, VAT 9.1, reconciliations'],
    ['Shirin Akter', 'Branch Manager', 'queue, cash, collections, CSAT']
  ];
  PS.forEach((p, i) => {
    const x = M + i * 3.12;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.8, w: 2.9, h: 3.3, fill: { color: C.wash }, rectRadius: 0.1, line: { type: 'none' } });
    s.addText(p[0].split(' ').map(w => w[0]).join(''), { x: x + 0.95, y: 2.05, w: 1.0, h: 1.0, fontSize: 30, fontFace: FONT, bold: true, color: C.white, align: 'center', valign: 'middle', fill: { color: C.primary }, margin: 0 });
    s.addText(p[0], { x: x + 0.15, y: 3.25, w: 2.6, h: 0.32, fontSize: 15.5, fontFace: FONT, bold: true, color: C.text, align: 'center', margin: 0 });
    s.addText(p[1], { x: x + 0.15, y: 3.6, w: 2.6, h: 0.3, fontSize: 12, fontFace: FONT, bold: true, color: C.primaryDark, align: 'center', margin: 0 });
    s.addText(p[2], { x: x + 0.15, y: 3.98, w: 2.6, h: 0.95, fontSize: 11.5, fontFace: FONT, color: C.muted, align: 'center', margin: 0 });
  });
  s.addText('Your home page is assembled from your role, not your name \u2014 change departments and it changes with you. Try personas on #/settings.', {
    x: M, y: 5.5, w: 12.3, h: 0.6, fontSize: 14, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('Demo: switch persona on the settings screen, watch the Role Centre rebuild.');
})();

/* ============ 28 · PROOF ============ */
(() => {
  const s = newSlide();
  h1(s, 'Built on proof', 'Verified, not assumed');
  stat(s, M, 1.8, 3.6, '8,566', 'routes crawled clean \u2014 zero dead links', false, true);
  stat(s, 4.6, 1.8, 3.6, '89/89', 'screenshots render in this deck\u2019s source guide');
  stat(s, 8.7, 1.8, 3.6, '20/20', 'cold deep-links pass with a 404 guard');
  bulletList(s, [
    'Full-browser audit: every link followed, zero console errors',
    'True 390 px mobile pass \u2014 no horizontal scroll on phones',
    'Back/forward history verified with real input clicks',
    'Counts machine-verified from live navigation data \u2014 823 screens, 346 reports, 5,100 functions'],
    M, 4.0, 7.0, 1.9);
  shot(s, 's-coverage-half', 8.15, 3.95, 4.65, 2.5, 'The Coverage screen \u2014 the system audits itself');
  s.addText('Source: audit harnesses _audit_click.js / _audit_final.js, September 2026.', {
    x: M, y: 6.6, w: 9, h: 0.3, fontSize: 11, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('The prototype behind these screenshots is itself machine-audited \u2014 quality you can show an auditor.');
})();

/* ============ 29 · FIRST WEEK ============ */
(() => {
  const s = newSlide();
  h1(s, 'Your first week', 'Five steps to productive');
  const FW = [
    ['Day 1', 'Read guide Parts 0\u20132 \u00b7 log in \u00b7 Alt+Q habit'],
    ['Day 2', 'Your area in Part 4 \u00b7 open its workspace \u00b7 learn your grids'],
    ['Day 3', 'Follow one order across the process bar, end to end'],
    ['Day 4', 'Run your team\u2019s saved views and scheduled reports'],
    ['Day 5', 'Save your first own view \u00b7 subscribe to one report']
  ];
  FW.forEach((st, i) => {
    const x = M + i * 2.52;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.3, w: 2.3, h: 2.9, fill: { color: i === 4 ? C.primary : C.wash }, rectRadius: 0.1, line: { type: 'none' }, shadow: shadow() });
    s.addText(st[0], { x: x + 0.18, y: 2.55, w: 1.95, h: 0.4, fontSize: 19, fontFace: FONT, bold: true, color: i === 4 ? C.tint : C.primaryDark, margin: 0 });
    s.addText(st[1], { x: x + 0.18, y: 3.1, w: 1.95, h: 1.9, fontSize: 12.5, fontFace: FONT, color: i === 4 ? C.white : C.text, margin: 0 });
  });
  s.addText('Help as you go: Learning (M22) assigns your onboarding path \u00b7 the IT portal (M66) takes tickets \u00b7 the Employee User Guide sits beside this deck.', {
    x: M, y: 5.7, w: 12.3, h: 0.6, fontSize: 13.5, fontFace: FONT, color: C.muted, margin: 0 });
  s.addNotes('Managers: check the Day-5 artifact \u2014 a saved view proves the habit landed.');
})();

/* ============ 30 · HELP ============ */
(() => {
  const s = newSlide();
  h1(s, 'Where to get help', 'Four doors, one company');
  const D = [
    ['In the app', '#/coverage map \u00b7 #/directory A\u2013Z \u00b7 Tell-ME search'],
    ['Employee User Guide', 'marketing/user-guide \u2014 HTML + 218-page PDF, module by module'],
    ['Learning & IT', 'M22 courses by role \u00b7 M66 IT portal for tickets'],
    ['For customers', 'Hotline 16743 \u00b7 Contact Centre M27 \u00b7 Bengali AI assistant']
  ];
  D.forEach((d, i) => {
    const y = 1.8 + i * 1.15;
    s.addText(d[0], { x: M, y, w: 3.6, h: 0.4, fontSize: 18, fontFace: FONT, bold: true, color: C.primaryDark, margin: 0 });
    s.addText(d[1], { x: 4.3, y: y + 0.02, w: 8.4, h: 0.75, fontSize: 15, fontFace: FONT, color: C.text, margin: 0 });
    if (i < 3) s.addShape(pres.shapes.LINE, { x: M, y: y + 0.92, w: 12.3, h: 0, line: { color: 'D7E2E0', width: 0.75 } });
  });
  s.addNotes('Everything above is internal; 16743 is the customer-facing hotline.');
})();

/* ============ 31 · CLOSE (dark) ============ */
(() => {
  const s = newSlide(true);
  s.addText('One team.\nOne system.\nEvery device accounted for.', { x: M, y: 2.0, w: 11.5, h: 2.6,
    fontSize: 52, fontFace: FONT, bold: true, color: C.white, margin: 0 });
  s.addText('Open the guide. Press Alt+Q. Advance the bar.', { x: M, y: 4.85, w: 9.5, h: 0.5,
    fontSize: 19, fontFace: FONT, color: C.tint, margin: 0 });
  s.addText('1000 FiX Services Limited \u00b7 Hotline 16743 \u00b7 ISO 9001:2015 Certified \u00b7 Internal use', {
    x: M, y: 6.3, w: 10, h: 0.35, fontSize: 13, fontFace: FONT, color: C.lightMuted, margin: 0 });
  s.addNotes('Close on the habit, not the software: search first, advance the bar, ask early.');
})();

pres.writeFile({ fileName: path.join(__dirname, '1000FiX_ERP_System_Overview.pptx') })
  .then(() => console.log('WROTE deck, slides=' + pageNo));
