/* Build the Microsoft Word edition of the 1000FiX ERP Employee User Guide.
   Sources (all static data files, no dynamic evaluation):
     _catalog_rich.json   - live navigation payload incl. screen names/types,
                            portals, journeys, personas (extracted separately
                            via the documented node -e one-liners)
     _guide_knowledge.js  - authored narrative (areas + 67 modules)
     user-guide/images/   - the 89 screenshots captured from the prototype
   Output: user-guide/1000FiX_ERP_User_Guide.docx
   Run:  node _build_guide_docx.js   (from the marketing folder) */
'use strict';
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, PageNumber, NumberFormat, AlignmentType,
  HeadingLevel, WidthType, BorderStyle, ShadingType, TableLayoutType,
  SectionType, TableOfContents, LevelFormat, VerticalMergeType,
} = require('docx');

const DIR = __dirname;
const IMG = path.join(DIR, 'user-guide', 'images');
const OUT = path.join(DIR, 'user-guide', '1000FiX_ERP_User_Guide.docx');
const KNW = require('./_guide_knowledge.js');
const CAT = JSON.parse(fs.readFileSync(path.join(DIR, '_catalog_rich.json'), 'utf8'));

/* ------------------------------------------------------------------ data */
const AREAS = CAT.areas;
const MODS = {};
AREAS.forEach((a) => a.mods.forEach((m) => { MODS[m.mid] = m; }));
const typeName = { g: 'Grid / list', f: 'Form', r: 'Report', c: 'Console', d: 'Dashboard', x: '360 view' };
const tot = { screens: 0, reports: 0, forms: 0, funcs: 0, mods: 0 };
AREAS.forEach((a) => a.mods.forEach((m) => {
  tot.mods += 1;
  m.groups.forEach((g) => { tot.screens += g.screens.length; });
  tot.reports += (m.reports || []).length;
  tot.forms += (m.forms || []).length;
  tot.funcs += (m.freg && m.freg.src) || 0;
}));

/* ---------------------------------------------------------------- style */
const PAL = {
  bg: '162235',
  cover: { titleColor: 'FFFFFF', subtitleColor: 'B0B8C0', metaColor: '90989F', footerColor: '687078', accent: '37DCF2' },
  primary: '0E2A33', text: '1A1A1A', secondary: '5A6B73',
  accent: '1B6B7A', surface: 'EDF3F5', innerLine: 'C8DDE2',
  warnBorder: '9A6A1F', warnFill: 'FBF5E8', gainBorder: '2A7A65', gainFill: 'EDF5F2',
};
const F = { body: 'Calibri', mono: 'Consolas', bn: 'Nirmala UI' };
const NB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };

const hasBn = (s) => /[\u0980-\u09FF]/.test(String(s));
const fontFor = (s, mono) => {
  if (mono) return { ascii: F.mono, eastAsia: F.mono, cs: F.mono };
  if (hasBn(s)) return { ascii: F.bn, eastAsia: F.bn, cs: F.bn };
  return { ascii: F.body, eastAsia: F.body, cs: F.body };
};
const run = (text, o = {}) => new TextRun({
  text: String(text == null ? '' : text),
  bold: o.bold || false, italics: o.italics || false,
  size: o.size || 22, color: o.color || PAL.text,
  font: o.font || fontFor(text, o.mono),
});

const para = (text, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { line: o.line || 312, before: o.before || 0, after: o.after == null ? 120 : o.after },
  keepNext: o.keepNext || false,
  indent: o.indent,
  children: (o.runs || [run(text, o)]),
});

let figN = 0;
function figure(fileName, caption, opts = {}) {
  /* boundary-checked image resolution: basename only, must stay inside IMG */
  const safeName = path.basename(fileName);
  const p = path.resolve(IMG, safeName);
  if (p !== path.join(IMG, safeName) || !p.startsWith(IMG + path.sep)) throw new Error('bad image path: ' + fileName);
  if (!fs.existsSync(p)) { console.warn('MISSING IMAGE ' + safeName); return []; }
  const buf = fs.readFileSync(p);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const maxW = opts.maxW || 560, maxH = opts.maxH || 780;
  const scale = Math.min(maxW / w, maxH / h, 1);
  const dw = Math.round(w * scale), dh = Math.round(h * scale);
  figN += 1;
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true,
      spacing: { before: 160, after: 60, line: 240 },
      children: [new ImageRun({ data: buf, transformation: { width: dw, height: dh }, type: 'png',
        altText: { title: 'Figure ' + figN, description: caption, name: safeName } })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200, line: 260 },
      children: [run('Figure ' + figN + ' \u2014 ', { size: 18, color: PAL.secondary, bold: true }),
        run(caption, { size: 18, color: PAL.secondary })],
    }),
  ];
}

function callout(leadBold, rest, kind = 'info') {
  const border = kind === 'warn' ? PAL.warnBorder : (kind === 'gain' ? PAL.gainBorder : PAL.accent);
  const fill = kind === 'warn' ? PAL.warnFill : (kind === 'gain' ? PAL.gainFill : PAL.surface);
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: { top: NB, bottom: NB, right: NB, insideHorizontal: NB, insideVertical: NB,
      left: { style: BorderStyle.SINGLE, size: 18, color: border } },
    rows: [new TableRow({ children: [new TableCell({
      shading: { type: ShadingType.CLEAR, fill },
      margins: { top: 100, bottom: 100, left: 180, right: 160 },
      children: [para('', { after: 0, align: AlignmentType.LEFT, runs: [
        run(leadBold ? leadBold + ' ' : '', { bold: true, size: 21, color: PAL.primary }),
        run(rest, { size: 21 }),
      ] })],
    })] })],
  });
}

const cellMargins = { top: 60, bottom: 60, left: 120, right: 120 };
function th(text, widthPct) {
  return new TableCell({
    shading: { type: ShadingType.CLEAR, fill: PAL.accent },
    margins: cellMargins, width: widthPct ? { size: widthPct, type: WidthType.PERCENTAGE } : undefined,
    children: [para('', { after: 0, align: AlignmentType.LEFT, runs: [run(text, { bold: true, size: 18, color: 'FFFFFF' })] })],
  });
}
function td(content, o = {}) {
  const runs = Array.isArray(content) ? content : [run(content, { size: o.size || 18, bold: o.bold, mono: o.mono, color: o.color })];
  return new TableCell({
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill } : undefined,
    margins: cellMargins, width: o.widthPct ? { size: o.widthPct, type: WidthType.PERCENTAGE } : undefined,
    verticalMerge: o.vMerge,
    children: [para('', { after: 0, align: AlignmentType.LEFT, runs })],
  });
}
function tbl(caption, headers, rows, o = {}) {
  const out = [];
  if (caption) out.push(para('', {
    keepNext: true, before: 120, after: 60, align: AlignmentType.LEFT,
    runs: [run(caption, { bold: true, size: 20, color: PAL.primary })],
  }));
  out.push(new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: PAL.accent },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: PAL.accent },
      left: NB, right: NB,
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: PAL.innerLine },
      insideVertical: NB,
    },
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => th(h, o.widths && o.widths[i])) }),
      ...rows,
    ],
  }));
  out.push(para('', { after: 60, runs: [] }));
  return out;
}
const zebra = (i) => (i % 2 === 1 ? PAL.surface : undefined);

function h1(text, opts = {}) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, pageBreakBefore: opts.pageBreakBefore !== false,
    spacing: { before: 360, after: 180, line: 380, lineRule: 'atLeast' },
    children: [run(text, { bold: true, size: 32, color: PAL.primary })],
  });
}
function h2(text, opts = {}) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, pageBreakBefore: !!opts.pageBreakBefore,
    spacing: { before: 300, after: 140, line: 340, lineRule: 'atLeast' },
    children: [run(text, { bold: true, size: 28, color: PAL.primary })],
  });
}
function h3(text, opts = {}) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3, pageBreakBefore: opts.pageBreakBefore !== false,
    spacing: { before: 240, after: 120, line: 312 },
    children: [run(text, { bold: true, size: 24, color: PAL.primary })],
  });
}
const label = (text) => para('', {
  keepNext: true, before: 160, after: 60, align: AlignmentType.LEFT,
  runs: [run(text, { bold: true, size: 21, color: PAL.accent })],
});
const bullets = (items) => items.map((t) => new Paragraph({
  bullet: { level: 0 }, spacing: { line: 312, after: 80 },
  children: Array.isArray(t) ? t : [run(t)],
}));
const steps = (ref, items) => items.map((t) => new Paragraph({
  numbering: { reference: ref, level: 0 }, spacing: { line: 312, after: 80 },
  children: Array.isArray(t) ? t : [run(t)],
}));

const numberingConfig = [];
function registerList(ref) {
  numberingConfig.push({
    reference: ref,
    levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 620, hanging: 360 } } } }],
  });
}

/* ------------------------------------------------------------ cover (R1) */
function calcCoverSpacing(p) {
  const SAFETY = 1200;
  const usable = 16838 - SAFETY;
  const titleH = p.titleLineCount * (p.titlePt * 23 + 200);
  const subH = p.hasSubtitle ? (12 * 23 + 600) : 0;
  const engH = p.hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaH = p.metaLineCount * (10 * 23 + 100);
  const content = titleH + subH + engH + metaH + p.fixedHeight + 3 * 300;
  const remaining = Math.max(usable - content, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(remaining * 0.45), rawBottom = Math.floor(remaining * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  return { topSpacing, bottomSpacing };
}
function buildCoverR1() {
  const P = PAL.cover;
  const padL = 1200, padR = 800;
  const titleLines = ['1000 FiX ERP', 'Employee User Guide']; /* English title, semantic split */
  const titlePt = 40;
  const metaLines = [
    'Edition 2.0 \u00b7 28 September 2026',
    tot.mods + ' modules \u00b7 12 areas \u00b7 ' + tot.screens + ' screens \u00b7 12 portals',
    tot.reports + ' built-in reports \u00b7 ' + tot.forms + ' forms \u00b7 ' + tot.funcs.toLocaleString('en-US') + ' registered functions',
    'Hotline 16743 \u00b7 ISO 9001:2015 Certified',
  ];
  const sp = calcCoverSpacing({ titleLineCount: titleLines.length, titlePt, hasSubtitle: true,
    hasEnglishLabel: true, metaLineCount: metaLines.length, fixedHeight: 400 });
  const accentLeft = { style: BorderStyle.SINGLE, size: 8, color: P.accent, space: 12 };
  const children = [];
  children.push(new Paragraph({ spacing: { before: sp.topSpacing } }));
  children.push(new Paragraph({
    indent: { left: padL, right: padR }, spacing: { after: 500 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: P.accent, space: 8 } },
    children: [new TextRun({ text: '1000 FIX SERVICES LTD'.split('').join('  '), size: 18, color: P.accent,
      font: { ascii: F.body, eastAsia: F.body }, characterSpacing: 40 })],
  }));
  titleLines.forEach((line, i) => children.push(new Paragraph({
    indent: { left: padL },
    spacing: { after: i < titleLines.length - 1 ? 100 : 300, line: Math.ceil(titlePt * 23), lineRule: 'atLeast' },
    children: [new TextRun({ text: line, size: titlePt * 2, bold: true, color: P.titleColor,
      font: { ascii: F.body, eastAsia: F.body } })],
  })));
  children.push(new Paragraph({
    indent: { left: padL, right: padR }, spacing: { after: 800, line: 320, lineRule: 'atLeast' },
    children: [new TextRun({ text: 'Everything you need to work in the system: how the ERP is organised, how to use every area module by module, and the business knowledge behind each screen \u2014 written for every employee, from branch counter to boardroom.',
      size: 24, color: P.subtitleColor, font: { ascii: F.body, eastAsia: F.body } })],
  }));
  metaLines.forEach((line) => children.push(new Paragraph({
    indent: { left: padL + 200 }, spacing: { after: 80 },
    border: { left: accentLeft },
    children: [new TextRun({ text: line, size: 24, color: P.metaColor, font: { ascii: F.body, eastAsia: F.body } })],
  })));
  children.push(new Paragraph({ spacing: { before: sp.bottomSpacing } }));
  children.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: P.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      new TextRun({ text: '1000 FiX Services Limited \u00b7 Internal use', size: 16, color: P.footerColor, font: { ascii: F.body } }),
      new TextRun({ text: '                                                                ', size: 16, color: P.footerColor, font: { ascii: F.body } }),
      new TextRun({ text: 'Edition 2.0 \u00b7 September 2026', size: 16, color: P.footerColor, font: { ascii: F.body } }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: 'exact' },
      children: [new TableCell({ shading: { type: ShadingType.CLEAR, fill: PAL.bg }, borders: noBorders, children })],
    })],
  })];
}

/* -------------------------------------------------------- front matter */
function frontMatter() {
  const out = [];
  out.push(new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 480, after: 300, line: 400, lineRule: 'atLeast' },
    children: [run('About this guide', { bold: true, size: 32, color: PAL.primary })],
  }));
  out.push(para('This is the Microsoft Word edition of the 1000 FiX ERP Employee User Guide. It carries the same content as the interactive HTML edition and the print PDF: every part, every one of the ' + tot.mods + ' modules, every screenshot. Word format makes it easy to annotate, excerpt for training, and share sections by email.', { after: 200 }));

  out.push(...tbl('Document control', ['Field', 'Value'], [
    new TableRow({ cantSplit: true, children: [td('Edition', { bold: true, widthPct: 24 }), td('2.0 (Word edition)')] }),
    new TableRow({ cantSplit: true, children: [td('Issued', { bold: true }), td('28 September 2026')] }),
    new TableRow({ cantSplit: true, children: [td('Subject', { bold: true }), td('1000 FiX ERP \u2014 the complete employee user guide')] }),
    new TableRow({ cantSplit: true, children: [td('Coverage', { bold: true }), td([run(tot.mods + ' modules \u00b7 12 areas \u00b7 ' + tot.screens + ' screens \u00b7 ' + tot.reports + ' built-in reports \u00b7 ' + tot.forms + ' data-entry forms \u00b7 ' + tot.funcs.toLocaleString('en-US') + ' registered functions \u00b7 12 portals \u00b7 10 end-to-end journeys \u2014 all counts machine-verified against the live navigation data', { size: 18 })])] }),
    new TableRow({ cantSplit: true, children: [td('Audience', { bold: true }), td('Every employee \u2014 branch counter to boardroom; bilingual UI (English + Bangla)')] }),
    new TableRow({ cantSplit: true, children: [td('Companions', { bold: true }), td([run('Interactive HTML (index.html, works offline) \u00b7 print PDF companion (218 pages). Deep process detail per module lives in the ERP Guide Book Library \u2014 see Part 9.', { size: 18 })])] }),
    new TableRow({ cantSplit: true, children: [td('Classification', { bold: true }), td('Internal use \u00b7 1000 FiX Services Limited \u00b7 Hotline 16743 \u00b7 ISO 9001:2015 Certified')] }),
  ], { widths: [24, 76] }));

  out.push(...tbl('How the guide is organised', ['Part', 'What it holds'], [
    new TableRow({ cantSplit: true, children: [td('0 \u00b7 Welcome', { bold: true }), td('What the ERP is, the one idea behind it, and how to read this guide.')] }),
    new TableRow({ cantSplit: true, children: [td('1 \u00b7 Getting started', { bold: true }), td('Login and TOTP, the screen you will live in, the mega menu, Tell-ME search, personalisation, mobile use, keyboard shortcuts.')] }),
    new TableRow({ cantSplit: true, children: [td('2 \u00b7 Core skills', { bold: true }), td('Grids and views, records and the process bar, forms, reports, the 7-step report writer, dashboards / consoles / 360 views, search and coverage.')] }),
    new TableRow({ cantSplit: true, children: [td('3 \u00b7 Map of the system', { bold: true }), td('One table that orients you across all eleven business areas.')] }),
    new TableRow({ cantSplit: true, children: [td('4 \u00b7 Module by module', { bold: true }), td('All ' + tot.mods + ' modules across 11 areas \u2014 each with purpose, live screenshot, step-by-step usage, business knowledge, employee benefit, and generated reference tables (screens, reports, forms, function register).')] }),
    new TableRow({ cantSplit: true, children: [td('5 \u00b7 Portals', { bold: true }), td('The 12 audience portals \u2014 who each serves, at what scale, with which features.')] }),
    new TableRow({ cantSplit: true, children: [td('6 \u00b7 Journeys', { bold: true }), td('Ten end-to-end journeys \u2014 64 steps mapped to their owners and screens.')] }),
    new TableRow({ cantSplit: true, children: [td('7 \u00b7 Personas', { bold: true }), td('Four sample personas and their role-based home pages.')] }),
    new TableRow({ cantSplit: true, children: [td('8 \u00b7 Glossary & FAQ', { bold: true }), td('Twenty working terms (AMC to WO) and six frequently asked questions.')] }),
    new TableRow({ cantSplit: true, children: [td('9 \u00b7 Reference', { bold: true }), td('Where to go for more \u2014 including the Word Guide Book Library \u2014 and the research sources behind the business knowledge.')] }),
  ], { widths: [24, 76] }));

  out.push(label('Conventions used in this guide'));
  out.push(...bullets([
    [run('Module ids ', {}), run('M01\u2026M67', { mono: true, size: 20 }), run(' are stable and searchable \u2014 type the id in Tell-ME and press Enter to land on that workspace.')],
    [run('Screen ids and in-app routes appear in a ', {}), run('monospace face', { mono: true, size: 20 }), run(' (for example '), run('#/coverage', { mono: true, size: 20 }), run('). Keyboard combinations are written Alt+Q, Ctrl+K.')],
    [run('Callout boxes flag the things worth remembering: '), run('teal', { bold: true, color: PAL.accent }), run(' for guidance, '), run('green', { bold: true, color: PAL.gainBorder }), run(' for what you personally gain, '), run('amber', { bold: true, color: PAL.warnBorder }), run(' for warnings.')],
    [run('Every table under a module in Part 4 is generated from the system\u2019s own navigation data \u2014 what you read here is exactly what exists in the app, and the '), run('#/coverage', { mono: true, size: 20 }), run(' screen verifies it.')],
  ]));
  out.push(para('Screenshots were captured from the live interactive prototype; counts and screen lists were extracted directly from the navigation payload, so they cannot drift from the shipped system.', { before: 120 }));
  return out;
}

/* ------------------------------------------------------------- parts 0-2 */
function part0() {
  const out = [];
  out.push(h1('Part 0 \u00b7 Welcome', { pageBreakBefore: false }));
  out.push(para('The 1000 FiX ERP is one connected system for the whole company: every service order, part, invoice, technician hour and customer conversation lives in one place. This guide shows you how to work in it \u2014 and why each part exists.', { after: 160 }));
  out.push(callout('The one idea that explains everything:', 'in the ERP, nothing is typed twice. The hotline agent creates an order; the technician, the workshop, the parts counter, the cashier, the accountant and the manager all work on that same order \u2014 each from their own screen. When you do your step well, everyone downstream inherits it.'));
  out.push(label('What the ERP covers'));
  out.push(...tbl(null, ['Dimension', 'Fact', 'What it means'], [
    new TableRow({ cantSplit: true, children: [td('Scale', { bold: true }), td(tot.mods + ' modules \u00b7 12 areas'), td([run(tot.screens + ' screens, ' + tot.reports + ' built-in reports, ' + tot.forms + ' data-entry forms and ' + tot.funcs.toLocaleString('en-US') + ' registered functions \u2014 from first phone call to VAT return, across all branches.', { size: 18 })])] }),
    new TableRow({ cantSplit: true, children: [td('Everyone', { bold: true }), td('12 portals'), td('Customers, technicians, corporates, vendors and partners each get their own door into the same system (see Part 5).')] }),
    new TableRow({ cantSplit: true, children: [td('Bilingual', { bold: true }), td([run('English + ', { size: 18 }), run('\u09ac\u09be\u0982\u09b2\u09be', { size: 18 })]), td('Every screen switches language instantly from the top bar. The customer chatbot speaks Bangla too.')] }),
    new TableRow({ cantSplit: true, children: [td('Built on proof', { bold: true }), td('ISO 9001:2015 aligned'), td('Processes, quality gates and audit trails in the system are the same ones our certificate is audited against.')] }),
  ], { widths: [16, 24, 60] }));
  out.push(label('How to use this guide'));
  registerList('p0-usage');
  out.push(...steps('p0-usage', [
    'New employee? Read Parts 1\u20132 (getting started + core skills). That is enough to be useful on day one.',
    'Working in a specific department? Jump to your area in Part 4 \u2014 each module page shows what it does, the steps you perform, the business logic behind them, and tables of its screens, reports and forms.',
    'Need a word? The glossary in Part 8 explains every term used at 1000 FiX \u2014 from AMC to VAT to FTTR.',
  ]));
  out.push(para('', { runs: [run('The system itself is the best teacher: the ', {}), run('#/coverage', { mono: true, size: 20 }), run(' screen shows every module and screen, and ', {}), run('Tell-ME', { bold: true }), run(' search (press ', {}), run('Alt+Q', { bold: true }), run(') finds any screen, report or record by name \u2014 in English or Bangla.')] }));
  out.push(callout('Safety note:', 'everything you do in the ERP is attributed to your login and kept in an audit trail. If you make a mistake, tell your supervisor \u2014 corrections are normal and traceable; hiding mistakes is not.', 'warn'));
  out.push(label('One system behind every door'));
  out.push(...figure('s-landing.png', 'What customers see (public site and app) is powered by the same ERP you work in \u2014 their booking becomes your service order.', { maxH: 700 }));
  return out;
}

function part1() {
  const out = [];
  out.push(h1('Part 1 \u00b7 Getting started'));
  out.push(h2('1.1 Log in'));
  out.push(...figure('s-login.png', 'The login page \u2014 your email, password, and a 6-digit TOTP code from your authenticator app.'));
  registerList('p1-login');
  out.push(...steps('p1-login', [
    'Open the ERP address in any modern browser \u2014 desktop or phone, the shell adapts.',
    'Enter your work email and password. First-time users receive credentials from IT (module M66).',
    'Type the 6-digit code from your authenticator app \u2014 the box auto-advances digit by digit.',
    'You land on your Role Centre \u2014 a home page assembled for your job.',
  ]));
  out.push(callout('Never share your login.', 'Accounts are personal, MFA-protected, and every action is logged to you (module M29). Colleagues who need access get their own account \u2014 ask IT.', 'warn'));

  out.push(h2('1.2 The screen you will live in'));
  out.push(...figure('s-home.png', 'The Role Centre: KPI cards, charts, approvals and your worklist \u2014 everything on this page is clickable.'));
  out.push(...tbl('The shell, element by element', ['Element', 'What it does'], [
    new TableRow({ cantSplit: true, children: [td([run('Tell-ME search', { bold: true, size: 18 }), run(' (top centre)', { size: 18 })]), td('Searches every screen, module, report and record. Press Alt+Q, type 2\u20133 letters, pick with the arrow keys, open with Enter.')] }),
    new TableRow({ cantSplit: true, children: [td([run('Left navigation', { bold: true, size: 18 })]), td('Every module grouped into 12 areas. Expand an area in the rail, or click it once to open its mega menu.')] }),
    new TableRow({ cantSplit: true, children: [td([run('Tab strip', { bold: true, size: 18 }), run(' (under the top bar)', { size: 18 })]), td('Like browser tabs: every screen you open gets a tab (up to 12). Your session restores on next login.')] }),
    new TableRow({ cantSplit: true, children: [td([run('Breadcrumbs', { bold: true, size: 18 }), run(' (status bar)', { size: 18 })]), td('Always shows where you are; every step is a link back.')] }),
    new TableRow({ cantSplit: true, children: [td([run('Top-right buttons', { bold: true, size: 18 })]), td([run('Language (EN / ', { size: 18 }), run('\u09ac\u09be\u0982\u09b2\u09be', { size: 18 }), run('), density, dark mode, notifications, company, Fix AI copilot, your profile.', { size: 18 })])] }),
    new TableRow({ cantSplit: true, children: [td([run('Status bar', { bold: true, size: 18 }), run(' (bottom)', { size: 18 })]), td('Environment, session, keyboard hints.')] }),
  ], { widths: [30, 70] }));

  out.push(h2('1.3 The mega menu \u2014 one click to any screen'));
  out.push(...figure('s-megamenu.png', 'Click an area in the left nav \u2014 every screen group in the area opens as a catalogue. Chips at the top jump straight to module workspaces.'));
  registerList('p1-mega');
  out.push(...steps('p1-mega', [
    'Click an area (for example Service Operations) in the left navigation.',
    'The mega menu lists every module\u2019s screen groups \u2014 click any screen to open it.',
    'The menu closes automatically when you navigate; click outside to dismiss it without choosing.',
  ]));

  out.push(h2('1.4 Tell-ME \u2014 finding anything in seconds'));
  out.push(...figure('s-tellme.png', 'Typing \u201cVAT\u201d \u2014 results grouped into Pages, Modules, Reports and Records, with keyboard selection.'));
  out.push(callout('Try it now:', 'Alt+Q, type dispatch, press the down arrow twice, then Enter. You are on the dispatch board. This one habit replaces most navigation.'));

  out.push(h2('1.5 Make the system yours'));
  out.push(...bullets([
    [run('Language', { bold: true }), run(' \u2014 the Bangla/EN button switches the shell instantly; modules and screens carry Bangla names too.')],
    [run('Density', { bold: true }), run(' \u2014 compact / standard / relaxed changes table row height (cashiers love compact).')],
    [run('Dark mode', { bold: true }), run(' \u2014 remembered per device; charts are tuned for both themes.')],
    [run('Phone use', { bold: true }), run(' \u2014 on a small screen the left rail collapses; the menu button opens it as an overlay that closes when you navigate.')],
  ]));
  out.push(...figure('s-dark.png', 'Dark mode \u2014 same data, easier on night-shift eyes.'));
  out.push(...figure('s-bengali.png', 'The full shell in Bangla \u2014 one button, no reload.'));
  out.push(...figure('s-mobile-home.png', 'The Role Centre on a phone (390 px) \u2014 same data, stacked layout, wide tables swipe inside the page.', { maxW: 300 }));
  out.push(...figure('s-mobile-nav.png', 'The menu button opens navigation as an overlay on phones; it closes automatically when you pick a module.', { maxW: 300 }));

  out.push(h2('1.6 Keyboard shortcuts worth memorising'));
  out.push(...tbl(null, ['Shortcut', 'Action'], [
    new TableRow({ cantSplit: true, children: [td([run('Alt+Q', { mono: true, bold: true, size: 18 })]), td('Focus Tell-ME search')] }),
    new TableRow({ cantSplit: true, children: [td([run('Ctrl+K', { mono: true, bold: true, size: 18 })]), td('Command palette \u2014 jump to any screen')] }),
    new TableRow({ cantSplit: true, children: [td([run('Alt+C', { mono: true, bold: true, size: 18 })]), td('Fix AI copilot')] }),
    new TableRow({ cantSplit: true, children: [td([run('Ctrl+Shift+O', { mono: true, bold: true, size: 18 })]), td('Switch company / entity')] }),
  ], { widths: [28, 72] }));
  out.push(para('', { runs: [run('The full list lives on the ', {}), run('#/shortcuts', { mono: true, size: 20 }), run(' screen in the app.', {})] }));
  return out;
}

function part2() {
  const out = [];
  out.push(h1('Part 2 \u00b7 Core skills (used in every module)'));
  out.push(h2('2.1 Working with lists (grids)'));
  out.push(...figure('s-grid.png', 'All Service Orders \u2014 filter pane at left, saved views above, row links open the full record.'));
  registerList('p2-grid');
  out.push(...steps('p2-grid', [
    [run('Filter pane', { bold: true }), run(' (left): pick values \u2014 filters combine and show as chips above the grid.')],
    [run('Saved views', { bold: true }), run(': use your team\u2019s shared views (for example \u201cSLA at risk\u201d) or save your own \u2014 they persist per user.')],
    [run('Column menus', { bold: true }), run(' (the header menu on each column): sort, hide and show columns.')],
    [run('Open anything', { bold: true }), run(': the first column of every grid is a link to the full record.')],
    [run('Export', { bold: true }), run(' any grid to XLSX / CSV \u2014 no screenshot-reporting needed.')],
  ]));
  out.push(h2('2.2 Working with a record \u2014 the process bar'));
  out.push(...figure('s-record.png', 'A service order record: the 8-step process bar across the top, tabs for lines and documents, FactBox at the right.'));
  out.push(para('Most records carry a business process flow \u2014 the horizontal stepper showing the document\u2019s life. For a service order: Received \u2192 Diagnosing \u2192 Estimate \u2192 Approved \u2192 In Progress \u2192 QC \u2192 Ready \u2192 Delivered.'));
  registerList('p2-record');
  out.push(...steps('p2-record', [
    'Open a record from any grid or search result.',
    'Advance the stage by clicking the next step \u2014 the system may require fields (for example diagnosis notes) before allowing it.',
    'The FactBox (right) shows related facts: customer, device, warranty, history \u2014 no navigation needed.',
    'Tabs across the record hold Lines, Documents and the Audit history (who changed what, when).',
  ]));
  out.push(h2('2.3 Filling forms \u2014 and why validation is your friend'));
  out.push(para('Data-entry forms (' + tot.forms + ' of them) share one behaviour: required fields are checked before save, and invalid values are flagged immediately in red. This is deliberate \u2014 a correct form once beats ten corrections downstream (an invoice with a wrong BIN costs an hour at the bank).'));
  out.push(h2('2.4 Running reports'));
  out.push(...figure('s-report.png', 'A built-in report \u2014 parameters and Run button, data table, distribution and trend charts, export options.'));
  registerList('p2-report');
  out.push(...steps('p2-report', [
    [run('Open the ', {}), run('Report Center', { bold: true }), run(' (', {}), run('#/reports', { mono: true, size: 20 }), run(') \u2014 ' + tot.reports + ' built-ins browsable by module \u2014 or find one by name in Tell-ME.', {})],
    'Set parameters (branch, period), press Run.',
    'Export XLSX / CSV / PDF, or Schedule it (for example every Monday 08:00 to your inbox).',
  ]));
  out.push(h2('2.5 Creating your own report \u2014 the 7-step writer'));
  out.push(...figure('s-writer.png', 'The no-code report writer: pick a dataset, filter, choose columns, watch the live preview, save and schedule.'));
  out.push(para('When no built-in answers your question, the Report Writer wizard builds one in minutes \u2014 no SQL, no IT ticket. Your saved reports appear in the Report Center next to the built-ins and can be shared with your team.'));
  out.push(h2('2.6 Dashboards, consoles and 360\u00b0 views'));
  out.push(...tbl(null, ['Surface', 'What it is'], [
    new TableRow({ cantSplit: true, children: [td('Dashboard', { bold: true }), td('Live charts and KPIs for monitoring (for example the Order Operations Board). Every tile drills into records.')] }),
    new TableRow({ cantSplit: true, children: [td('Console', { bold: true }), td('A guided checklist screen for periodic work \u2014 for example period-end close: every task with status, owner and sign-off.')] }),
    new TableRow({ cantSplit: true, children: [td('360\u00b0 view', { bold: true }), td('One subject (customer, device, supplier) with everything about it \u2014 profile, transactions, history \u2014 on one screen.')] }),
  ], { widths: [22, 78] }));
  out.push(...figure('s-dispatch.png', 'The M02 Dispatch Board \u2014 a live dashboard: columns are service zones, cards are today\u2019s work orders.'));
  out.push(...figure('s-console.png', 'The Month-End Close console (M19) \u2014 month-end as a tracked checklist instead of a memory test.'));
  out.push(h2('2.7 Search, Directory and Coverage'));
  out.push(...figure('s-search.png', 'The search page behind Tell-ME \u2014 grouped results across screens, modules, reports and records, in both languages.'));
  out.push(...bullets([
    [run('Search page', { bold: true }), run(' (', {}), run('#/search', { mono: true, size: 20 }), run(') \u2014 the full-power search behind Tell-ME: screens, modules, reports and sample records, in both languages.', {})],
    [run('A\u2013Z Directory', { bold: true }), run(' (', {}), run('#/directory', { mono: true, size: 20 }), run(') \u2014 every module and screen in one alphabetical list.', {})],
    [run('Coverage', { bold: true }), run(' (', {}), run('#/coverage', { mono: true, size: 20 }), run(') \u2014 the machine-checked map of the whole ERP: every module\u2019s screens, reports, forms and functions. Use it to discover what exists before asking for anything new.', {})],
  ]));
  out.push(...figure('s-directory.png', 'The A\u2013Z Directory \u2014 every module at a glance.'));
  out.push(...figure('s-coverage.png', 'The Coverage screen \u2014 proof that every module\u2019s numbers are real and checkable.'));
  out.push(h2('2.8 The Report Center'));
  out.push(...figure('s-reportcenter.png', 'The Report Center \u2014 ' + tot.reports + ' built-in reports browsable by module, plus your own saved reports from the writer.'));
  return out;
}

/* --------------------------------------------------------------- part 3 */
function part3() {
  const out = [];
  out.push(h1('Part 3 \u00b7 The map of the system'));
  out.push(para('Before the module detail, hold the whole picture: eleven business areas (plus Home) carry the ' + tot.mods + ' modules. The same structure you see here is the left navigation in the app \u2014 learn the map once, navigate forever.', { after: 160 }));
  const rows = [];
  AREAS.forEach((a, ai) => {
    if (!a.mods.length) return;
    const k = KNW.AREAS[a.id] || {};
    const screens = a.mods.reduce((n, m) => n + m.groups.reduce((n2, g) => n2 + g.screens.length, 0), 0);
    const reports = a.mods.reduce((n, m) => n + (m.reports || []).length, 0);
    const funcs = a.mods.reduce((n, m) => n + ((m.freg && m.freg.src) || 0), 0);
    rows.push(new TableRow({ cantSplit: true, children: [
      td([run(a.id + ' \u00b7 ' + a.en, { bold: true, size: 18 }), run('  (' + a.bn + ')', { size: 16, color: PAL.secondary })], { widthPct: 22, fill: zebra(ai) }),
      td(k.intro || '', { size: 17, fill: zebra(ai) }),
      td([run(a.mods.length + ' modules', { bold: true, size: 17 }), run(' ' + a.mods.map((m) => m.mid).join(' '), { size: 15, color: PAL.secondary })], { widthPct: 18, fill: zebra(ai) }),
      td([run(screens + ' screens', { size: 17 }), run(' \u00b7 ' + reports + ' reports', { size: 17 }), run(' \u00b7 ' + funcs + ' functions', { size: 17 })], { widthPct: 18, fill: zebra(ai) }),
    ] }));
  });
  out.push(...tbl('Eleven areas, ' + tot.mods + ' modules', ['Area', 'What it covers', 'Modules', 'Key numbers'], rows, { widths: [22, 42, 18, 18] }));
  out.push(callout('Reading the module pages:', 'every module id (M01\u2013M67) is searchable in Tell-ME \u2014 type the id and press Enter to land on its workspace. The ids are stable; screens may evolve, ids do not.'));
  return out;
}

/* --------------------------------------------------------------- part 4 */
function moduleSection(mid) {
  const m = MODS[mid];
  const k = KNW.MODULES[mid] || {};
  const screenCount = m.groups.reduce((n, g) => n + g.screens.length, 0);
  const out = [];
  out.push(h3(mid + ' \u00b7 ' + m.en));
  out.push(para('', { after: 40, runs: [run(m.bn, { size: 20, color: PAL.secondary }), run('   \u2014   ' + screenCount + ' screens \u00b7 ' + (m.reports || []).length + ' reports \u00b7 ' + (m.forms || []).length + ' forms' + (m.freg ? ' \u00b7 ' + m.freg.src + ' functions' : ''), { size: 18, color: PAL.secondary })] }));
  out.push(para(k.p || m.desc || '', { after: 100 }));
  out.push(...figure('w-' + mid + '.png', mid + ' \u2014 ' + m.en + ' workspace. Open it in the app: Tell-ME \u2192 ' + mid + ', or the area mega menu.'));

  if (k.how && k.how.length) {
    registerList('how-' + mid);
    out.push(label('How you use it'));
    out.push(...steps('how-' + mid, k.how));
    out.push(label('Business knowledge'));
    out.push(para(k.biz || '', { after: 100 }));
    out.push(callout('What you gain:', k.b || '', 'gain'));
  }

  /* key screens table with vertically merged group column */
  const screenRows = [];
  m.groups.forEach((g) => {
    g.screens.forEach((s, i) => {
      screenRows.push(new TableRow({ cantSplit: true, children: [
        td(g.en, { vMerge: i === 0 ? VerticalMergeType.RESTART : VerticalMergeType.CONTINUE, widthPct: 26, size: 17, bold: i === 0 }),
        td(s.en, { size: 17 }),
        td(s.id, { mono: true, size: 16, widthPct: 20 }),
        td(typeName[s.t] || s.t || '\u2014', { size: 17, widthPct: 16 }),
      ] }));
    });
  });
  out.push(...tbl('Key screens (' + screenCount + ')', ['Group', 'Screen', 'Screen id', 'Type'], screenRows, { widths: [26, 38, 20, 16] }));

  if ((m.reports || []).length) {
    out.push(...tbl('Built-in reports (' + m.reports.length + ')', ['#', 'Report'], m.reports.map((r, i) =>
      new TableRow({ cantSplit: true, children: [
        td(String(i + 1), { size: 17, widthPct: 8, fill: zebra(i), color: PAL.secondary }),
        td(r, { size: 17, fill: zebra(i) }),
      ] })), { widths: [8, 92] }));
  }
  if ((m.forms || []).length) {
    out.push(...tbl('Data-entry forms (' + m.forms.length + ')', ['#', 'Form'], m.forms.map((r, i) =>
      new TableRow({ cantSplit: true, children: [
        td(String(i + 1), { size: 17, widthPct: 8, fill: zebra(i), color: PAL.secondary }),
        td(r, { size: 17, fill: zebra(i) }),
      ] })), { widths: [8, 92] }));
  }
  if (m.freg && m.freg.sub && m.freg.sub.length) {
    out.push(...tbl('Function register \u2014 ' + m.freg.src + ' functions in ' + m.freg.sub.length + ' sub-modules', ['#', 'Sub-module', 'Functions'],
      m.freg.sub.map((s, i) => new TableRow({ cantSplit: true, children: [
        td(s[0], { size: 17, widthPct: 8, fill: zebra(i), color: PAL.secondary }),
        td(s[1], { size: 17, fill: zebra(i) }),
        td(String(s[2]), { size: 17, widthPct: 16, fill: zebra(i) }),
      ] })), { widths: [8, 76, 16] }));
  }
  return out;
}

function part4() {
  const out = [];
  out.push(h1('Part 4 \u00b7 The ' + tot.mods + ' modules, area by area'));
  out.push(para('Each area opens with its business context; each module page follows the same rhythm \u2014 what it is, a screenshot, how you use it step by step, the business knowledge behind it, what you personally gain, then the reference tables (screens, reports, forms, function register).', { after: 140 }));
  out.push(callout('Numbers note:', 'the tables under each module are generated from the system\u2019s own navigation data \u2014 what you read here is exactly what exists in the app, and the #/coverage screen verifies it.'));
  out.push(...figure('s-freg.png', 'The Function Explorer \u2014 every sub-module and function behind a module, drillable one level deeper (#/freg/M01/0 shown).'));
  AREAS.forEach((a) => {
    if (!a.mods.length) return;
    const k = KNW.AREAS[a.id] || {};
    out.push(h2(a.id + ' \u00b7 ' + a.en, { pageBreakBefore: true }));
    out.push(para('', { after: 60, runs: [run(a.bn, { size: 20, color: PAL.secondary })] }));
    out.push(para(k.intro || '', { after: 120 }));
    out.push(label('The business of this area'));
    out.push(para(k.biz || '', { after: 100 }));
    if (k.b && k.b.length) {
      out.push(label('Why it matters to you'));
      out.push(...bullets(k.b));
    }
    out.push(label('Modules in this area'));
    out.push(para('', { runs: a.mods.map((m, i) => run((i ? ' \u00b7 ' : '') + m.mid + ' ' + m.en, { size: 20 })) }));
    a.mods.forEach((m) => { out.push(...moduleSection(m.mid)); });
  });
  return out;
}

/* --------------------------------------------------------------- part 5 */
function part5() {
  const out = [];
  out.push(h1('Part 5 \u00b7 The 12 portals \u2014 every audience gets its own door'));
  out.push(para('The ERP is one system, but a customer, a technician and a vendor each need a different view of it. Portals are role-scoped front doors over the same data.', { after: 140 }));
  out.push(...tbl('The portal suite at a glance', ['Id', 'Portal', 'Audience', 'Scale'], CAT.portals.map((p, i) => new TableRow({ cantSplit: true, children: [
    td(p.id, { bold: true, size: 17, widthPct: 8, fill: zebra(i) }),
    td(p.name, { size: 17, fill: zebra(i) }),
    td(p.audience, { size: 17, fill: zebra(i), widthPct: 28 }),
    td(p.scale, { size: 17, widthPct: 18, fill: zebra(i) }),
  ] })), { widths: [8, 46, 28, 18] }));
  CAT.portals.forEach((p) => {
    out.push(para('', { keepNext: true, before: 220, after: 60, align: AlignmentType.LEFT, runs: [
      run(p.id + ' \u00b7 ' + p.name, { bold: true, size: 24, color: PAL.primary })] }));
    out.push(para('', { after: 60, runs: [
      run('Who: ', { bold: true, size: 20 }), run(p.audience + '      ', { size: 20 }),
      run('Scale: ', { bold: true, size: 20 }), run(p.scale + '      ', { size: 20 }),
      run('Stack: ', { bold: true, size: 20 }), run(p.stack, { size: 20 })] }));
    out.push(...bullets((p.features || []).map((f) => run(f, { size: 20 }))));
  });
  out.push(...figure('s-portals.png', 'The Portals screen in the app \u2014 all 12 doors with their audiences and scale.'));
  return out;
}

/* --------------------------------------------------------------- part 6 */
function part6() {
  const out = [];
  out.push(h1('Part 6 \u00b7 Ten end-to-end journeys \u2014 how work flows across modules'));
  out.push(para('A journey is real work crossing module borders. Follow these to see how your piece feeds the next person\u2019s \u2014 each step names the owner and the screen where it happens.', { after: 140 }));
  CAT.journeys.forEach((j) => {
    out.push(para('', { keepNext: true, before: 260, after: 60, align: AlignmentType.LEFT, runs: [
      run(j.id + ' \u00b7 ' + j.en, { bold: true, size: 24, color: PAL.primary })] }));
    out.push(...tbl(null, ['#', 'Step owner', 'What happens', 'Where in the system'],
      j.steps.map((s, i) => new TableRow({ cantSplit: true, children: [
        td(String(i + 1), { size: 17, widthPct: 6, fill: zebra(i), color: PAL.secondary }),
        td(s.who, { size: 17, bold: true, fill: zebra(i), widthPct: 20 }),
        td(s.what, { size: 17, fill: zebra(i) }),
        td(s.route, { mono: true, size: 15, widthPct: 24, fill: zebra(i) }),
      ] })), { widths: [6, 20, 50, 24] }));
  });
  out.push(...figure('s-journeys.png', 'All journeys, interactive, in the app (#/journeys).'));
  return out;
}

/* --------------------------------------------------------------- part 7 */
function part7() {
  const out = [];
  out.push(h1('Part 7 \u00b7 Whose screen is whose \u2014 the four sample personas'));
  out.push(para('Your Role Centre is assembled from your role, not your name \u2014 when you change departments, your home page changes with you. These four sample personas show what that looks like; try them on the #/settings screen in the app.', { after: 160 }));
  CAT.personas.forEach((p) => {
    out.push(para('', { keepNext: true, before: 260, after: 40, align: AlignmentType.LEFT, runs: [
      run(p.name + ' \u2014 ' + p.role, { bold: true, size: 24, color: PAL.primary })] }));
    out.push(para('', { after: 80, runs: [
      run('Approvals waiting: ', { bold: true, size: 20 }), run(String((p.approvals || []).length), { size: 20 }),
      run('      Worklist items: ', { bold: true, size: 20 }), run(String((p.worklist || []).length), { size: 20 })] }));
    out.push(...tbl('Approvals waiting on the Role Centre', ['Ref', 'Type', 'Detail'], (p.approvals || []).map((a, i) => new TableRow({ cantSplit: true, children: [
      td(a[0], { mono: true, size: 17, widthPct: 22, fill: zebra(i) }),
      td(a[1], { size: 17, fill: zebra(i), widthPct: 26 }),
      td(a[2], { size: 17, fill: zebra(i) }),
    ] })), { widths: [22, 26, 52] }));
    out.push(...tbl('Worklist on the Role Centre', ['Count', 'Item', 'Screen'], (p.worklist || []).map((a, i) => new TableRow({ cantSplit: true, children: [
      td(a[0], { bold: true, size: 17, widthPct: 16, fill: zebra(i) }),
      td(a[1], { size: 17, fill: zebra(i) }),
      td(a[2], { mono: true, size: 15, widthPct: 30, fill: zebra(i) }),
    ] })), { widths: [16, 54, 30] }));
  });
  return out;
}

/* --------------------------------------------------------------- part 8 */
function part8() {
  const out = [];
  out.push(h1('Part 8 \u00b7 Glossary & FAQ'));
  out.push(h2('Working vocabulary at 1000 FiX'));
  const glossary = [
    ['AMC', 'Annual Maintenance Contract \u2014 a fixed-fee yearly service agreement with defined response promises and included visits.'],
    ['BIN', 'Business Identification Number \u2014 the VAT registration number issued by NBR; required on tax invoices.'],
    ['bKash / Nagad', 'Mobile financial services \u2014 the dominant payment rails in Bangladesh; each reconciles via its own settlement file.'],
    ['CAPA', 'Corrective & Preventive Action \u2014 the ISO 9001 discipline of fixing root causes, not symptoms.'],
    ['CSAT / NPS / CES', 'Customer Satisfaction score / Net Promoter Score / Customer Effort Score \u2014 the three experience measures.'],
    ['EaaS', 'Equipment-as-a-Service \u2014 a rental/subscription model where 1000 FiX owns the device and sells uptime.'],
    ['FTTR (first-time fix)', 'Share of jobs fully resolved on the first visit \u2014 the single most important field-service KPI.'],
    ['GRN', 'Goods Received Note \u2014 warehouse confirmation of what physically arrived versus the purchase order.'],
    ['Job sheet', 'The signed intake document recording device condition and stated fault \u2014 legal proof of custody.'],
    ['Mushak 6.3', 'The mandatory VAT tax invoice/challan issued for every taxable supply under the VAT & SD Act 2012.'],
    ['Mushak 9.1', 'The monthly VAT return filed with NBR summarising output VAT against input VAT.'],
    ['NBR', 'National Board of Revenue \u2014 Bangladesh\u2019s tax authority.'],
    ['Party', 'Any person or organisation the company deals with \u2014 customer, partner, supplier, employee \u2014 one identity, many roles.'],
    ['RMA', 'Return Merchandise Authorisation \u2014 an approved return of a part or device to stock or to a supplier.'],
    ['SLA', 'Service Level Agreement \u2014 the promised response/resolution time; compliance is measured on every order.'],
    ['TAT', 'Turnaround time \u2014 total days a device is in 1000 FiX\u2019s custody, from intake to delivery.'],
    ['TOTP', 'The 6-digit time-based code from your authenticator app, used at login (multi-factor authentication).'],
    ['Three-way match', 'Procurement control: purchase order \u2194 goods receipt \u2194 supplier invoice must agree before payment.'],
    ['WIP', 'Work in process \u2014 orders currently between intake and closure; WIP ageing is watched daily.'],
    ['WO', 'Work order \u2014 the field-service document assigned to a technician (WO-xxxx ids).'],
  ];
  out.push(...tbl('Twenty terms you will hear every day', ['Term', 'Plain meaning'], glossary.map((g, i) => new TableRow({ cantSplit: true, children: [
    td(g[0], { bold: true, size: 18, widthPct: 22, fill: zebra(i) }),
    td(g[1], { size: 18, fill: zebra(i) }),
  ] })), { widths: [22, 78] }));
  out.push(h2('Frequently asked questions'));
  const faqs = [
    ['\u201cI can\u2019t see a screen my colleague sees.\u201d', 'Access is role-based (M29). Ask your manager to request the role from IT \u2014 access reviews run quarterly.'],
    ['\u201cI made a mistake on a posted document.\u201d', 'Never delete (you can\u2019t). Tell your supervisor; corrections are posted as reversal entries and the audit trail keeps both \u2014 that\u2019s normal and safe.'],
    ['\u201cThe system is slow / a page won\u2019t load.\u201d', 'Check the status bar (environment), try Ctrl+F5, then raise an IT ticket through the internal portal (M66) \u2014 its wallboard shows live platform status.'],
    ['\u201cWhere do I get training?\u201d', 'M22 Learning lists courses by device family and role; your onboarding path is assigned automatically in your first week.'],
    ['\u201cWho owns this data field?\u201d', 'Every dataset in the catalogue (M62 / M25) names its owner. The Coverage screen tells you which module a field belongs to.'],
    ['\u201cCan I use it in Bangla?\u201d', 'Yes \u2014 the Bangla button (top bar) switches the shell instantly; records keep English codes for cross-border readability, exactly like localised Dynamics deployments.'],
  ];
  faqs.forEach((q) => {
    out.push(para('', { keepNext: true, before: 160, after: 40, align: AlignmentType.LEFT, runs: [run(q[0], { bold: true, size: 22, color: PAL.primary })] }));
    out.push(para(q[1], { after: 100 }));
  });
  return out;
}

/* --------------------------------------------------------------- part 9 */
function part9() {
  const out = [];
  out.push(h1('Part 9 \u00b7 Reference'));
  out.push(h2('Where to go for more'));
  out.push(...bullets([
    [run('In the app: ', { bold: true }), run('#/coverage', { mono: true, size: 20 }), run(' (the machine-checked map of all ' + tot.mods + ' modules), ', {}), run('#/directory', { mono: true, size: 20 }), run(' (A\u2013Z of screens), ', {}), run('#/shortcuts', { mono: true, size: 20 }), run(' (every keyboard shortcut), ', {}), run('#/designsystem', { mono: true, size: 20 }), run(' (UI standards).', {})],
    [run('Deep-dive Word guides: ', { bold: true }), run('the ERP Guide Book Library (marketing folder) holds 92 volumes \u2014 one Microsoft Word guide book per module and per portal, one per category, a portal suite volume and a master index. Start from GB-000, the master index.', {})],
    [run('Training & certification: ', { bold: true }), run('Learning module M22.', {})],
    [run('Helpdesk: ', { bold: true }), run('internal IT portal (M66) \u00b7 customer hotline 16743 (M27).', {})],
  ]));
  out.push(...tbl('The ERP Guide Book Library \u2014 92 Word volumes', ['Level', 'Where', 'Count'], [
    new TableRow({ cantSplit: true, children: [td('Master index'), td('00_Start_Here/ (GB-000)'), td('1', { widthPct: 12 })] }),
    new TableRow({ cantSplit: true, children: [td('Category guide books'), td('01_Modules/<category>/'), td('11', { widthPct: 12 })] }),
    new TableRow({ cantSplit: true, children: [td('Module guide books'), td('01_Modules/<category>/'), td('67', { widthPct: 12 })] }),
    new TableRow({ cantSplit: true, children: [td('Portal suite guide book'), td('02_Portals_and_Applications/'), td('1', { widthPct: 12 })] }),
    new TableRow({ cantSplit: true, children: [td('Portal guide books'), td('02_Portals_and_Applications/'), td('12', { widthPct: 12 })] }),
  ], { widths: [34, 54, 12] }));
  out.push(h2('Sources consulted for the business knowledge in this guide'));
  out.push(...bullets([
    run('Company corpus \u2014 the 1000 FiX ERP Module Catalogue & Master Register, module specifications, BRD/URD documents, and the ISO 9001:2015 context of 1000 FiX Services Ltd (Bangladesh\u2019s largest and only ISO-certified IT after-sales provider; hotline 16743).', { size: 20 }),
    run('Field-service practice \u2014 first-time-fix, SLA and CSAT definitions per industry KPI guides (Salesforce field service metrics, Comarch FSM, Skedulo).', { size: 20 }),
    run('Bangladesh VAT \u2014 Mushak 6.3 tax-invoice and Mushak 9.1 monthly-return obligations under the VAT & Supplementary Duty Act 2012 (NBR requirements; practitioner summaries).', { size: 20 }),
    run('ERP guide structure \u2014 modelled on Microsoft Dynamics 365 documentation practice (get-started \u2192 navigation \u2192 module tasks) at learn.microsoft.com/dynamics365.', { size: 20 }),
  ]));
  const colophon = '1000 FiX ERP Employee User Guide \u00b7 Edition 2.0 \u00b7 28 September 2026 \u00b7 generated from the live system navigation data (' + tot.mods + ' modules, ' + tot.screens + ' screens, ' + tot.reports + ' reports, ' + tot.forms + ' forms, ' + tot.funcs.toLocaleString('en-US') + ' functions \u2014 machine-verified).';
  out.push(para('', { before: 200, runs: [run(colophon, { size: 18, color: PAL.secondary, italics: true })] }));
  out.push(para('', { runs: [run('1000 FiX Services Limited \u00b7 Hotline 16743 \u00b7 ISO 9001:2015 Certified \u00b7 Internal use', { size: 18, color: PAL.secondary, italics: true })] }));
  return out;
}

/* ------------------------------------------------------------ assemble */
registerList('p0-usage'); registerList('p1-login'); registerList('p1-mega');
registerList('p2-grid'); registerList('p2-record'); registerList('p2-report');

const bodyChildren = [
  ...part0(), ...part1(), ...part2(), ...part3(), ...part4(),
  ...part5(), ...part6(), ...part7(), ...part8(), ...part9(),
];

const pageSize = { width: 11906, height: 16838 };
const pageMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };

const bodyHeader = new Header({ children: [new Paragraph({
  alignment: AlignmentType.CENTER,
  border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: PAL.innerLine, space: 4 } },
  spacing: { after: 0, line: 240 },
  children: [run('1000 FiX ERP \u00b7 Employee User Guide \u00b7 Edition 2.0', { size: 16, color: PAL.secondary })],
}) ] });
const numFooter = () => new Footer({ children: [new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { line: 240 },
  children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: PAL.secondary, font: { ascii: F.body } })],
}) ] });

const doc = new Document({
  creator: '1000 FiX Services Ltd',
  title: '1000 FiX ERP \u2014 Employee User Guide (Edition 2.0)',
  description: 'Complete employee user guide for the 1000 FiX ERP: 67 modules, 12 areas, 12 portals, 10 journeys.',
  styles: {
    default: {
      document: {
        run: { font: { ascii: F.body, eastAsia: F.body, cs: F.body }, size: 22, color: PAL.text },
        paragraph: { spacing: { line: 312 } },
      },
      heading1: { run: { font: { ascii: F.body, eastAsia: F.body }, size: 32, bold: true, color: PAL.primary },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      heading2: { run: { font: { ascii: F.body, eastAsia: F.body }, size: 28, bold: true, color: PAL.primary },
        paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 1 } },
      heading3: { run: { font: { ascii: F.body, eastAsia: F.body }, size: 24, bold: true, color: PAL.primary },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 } },
    },
  },
  numbering: { config: numberingConfig },
  features: { updateFields: true },
  sections: [
    { /* Section 1: cover \u2014 margin 0, no footer */
      properties: { page: { size: pageSize, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildCoverR1(),
    },
    { /* Section 2: front matter \u2014 Roman numerals */
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pageSize, margin: pageMargin,
          pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
      },
      footers: { default: numFooter() },
      children: [
        ...frontMatter(),
        new Paragraph({
          alignment: AlignmentType.CENTER, pageBreakBefore: true, spacing: { before: 0, after: 360, line: 400, lineRule: 'atLeast' },
          children: [run('Table of Contents', { bold: true, size: 32, color: PAL.primary })],
        }),
        new TableOfContents('Table of Contents', { hyperlink: true, headingStyleRange: '1-3' }),
        new Paragraph({
          spacing: { before: 200 },
          children: [run('Note: this Table of Contents is generated via field codes. To ensure page-number accuracy after editing, right-click the Table of Contents and choose \u201cUpdate Field\u201d, then \u201cUpdate entire table\u201d.', { italics: true, size: 18, color: '888888' })],
        }),
      ],
    },
    { /* Section 3: body \u2014 Arabic numerals from 1 */
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pageSize, margin: pageMargin,
          pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
      },
      headers: { default: bodyHeader },
      footers: { default: numFooter() },
      children: bodyChildren,
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log('WROTE ' + OUT + ' (' + (buf.length / 1024 / 1024).toFixed(1) + ' MB)');
  console.log('figures: ' + figN + ' | modules: ' + tot.mods + ' | screens: ' + tot.screens +
    ' | reports: ' + tot.reports + ' | forms: ' + tot.forms + ' | functions: ' + tot.funcs);
}).catch((e) => { console.error(e); process.exit(1); });
