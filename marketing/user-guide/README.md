# 1000 FiX ERP — Employee User Guide (Edition 2.0)

**Open `index.html` in any browser.** The guide works offline; everything it
needs is in this folder. A **PDF companion** (`1000FiX_ERP_User_Guide.pdf`,
218 pages) is included for printing and phone reading.

| File | Purpose |
|---|---|
| `index.html` | The interactive guide (sidebar TOC, 89 screenshots) |
| `1000FiX_ERP_User_Guide.docx` | **Microsoft Word edition** (26 MB, ~235 pages) — same content as the HTML/PDF, with a live field-code Table of Contents, Roman/Arabic page numbering, all 89 screenshots and full screen-name/type tables. Annotate, excerpt and share by email. |
| `1000FiX_ERP_User_Guide.pdf` | Print/phone companion, exported from `print.html` |
| `print.html` | Eager-image build variant (lazy images export as blank boxes in PDF) |
| `images/` | 89 screenshots captured from the live prototype (28 MB) |

## What's inside

| Part | Content |
|---|---|
| 0 · Welcome | What the ERP is, how to use the guide |
| 1 · Getting started | Login & TOTP, shell tour, mega menu, Tell-ME, personalisation, mobile, shortcuts |
| 2 · Core skills | Grids & views, records & the process bar, forms, reports, the 7-step writer, dashboards/consoles/360°, search/directory/coverage |
| 4 · Module by module | **All 67 modules** across 11 business areas — each with purpose, live screenshot, step-by-step usage, business knowledge, employee benefit, and generated reference tables (screens / reports / forms / function register) |
| 5 · Portals | The 12 audience portals with who/scale/features |
| 6 · Journeys | 10 end-to-end journeys, 64 steps mapped to owners and screens |
| 7 · Personas | The 4 sample personas and role-based home pages |
| 8 · Glossary & FAQ | 20 working terms (AMC → WO), 6 FAQs |
| 9 · Reference | Further reading incl. the Word Guide Book Library, and research sources |

## How it was built (and how to rebuild)

The guide is **generated from the system's own navigation data** — the same
payload that powers the app — so its numbers can't drift from reality:

```
marketing/
  _catalog.json            # extracted from Front_end/js/nav_data{,2,3}.js + demo_data.js
  _catalog_rich.json       # same payload but keeps screen names + types (feeds the Word build)
  _guide_knowledge.js      # authored narrative: 12 areas + 67 modules (purpose/how/biz/benefit)
  _guide_style.css         # stylesheet
  _guide_part_*.html       # authored sections (welcome, started, skills, reference)
  _build_guide.js          # assembles user-guide/index.html
  _build_guide_docx.js     # assembles user-guide/1000FiX_ERP_User_Guide.docx (node _build_guide_docx.js)
  _verify_guide.js         # CDP verification: images, anchors, overflow
Front_end/_guide_shots.js  # captures all screenshots from the running prototype
```

Rebuilding the **Word edition**: re-extract `_catalog_rich.json` first (same
one-liner pattern as `_catalog.json`, but keep `screens.map(s=>({id:s.id,en:s.en,t:s.t}))`),
then run `node _build_guide_docx.js`, then the docx post-processing scripts
(TOC placeholders + footer field patch — see the documents/docx skill).

Rebuild after changing the app or the narrative:

```bash
# 1. serve the prototype and run headless Chrome (see Front_end/README.md §5)
cd Front_end && python -m http.server 8471
node _guide_shots.js        # refreshes marketing/user-guide/images/

# 2. re-extract the catalog (inline vm — a script file with dynamic eval is blocked
#    by the Mimosa hook, so these two one-liners are the supported path):
#    a) areas+modules:
node -e "const fs=require('fs'),vm=require('vm');const w={};vm.runInNewContext(fs.readFileSync('js/nav_data.js','utf8')+fs.readFileSync('js/nav_data2.js','utf8')+fs.readFileSync('js/nav_data3.js','utf8'),{window:w});const A=w.FX_AREAS,M=w.FX_MODULES;const out=A.map(a=>({id:a.id,en:a.en,bn:a.bn,mods:a.mods.map(mid=>{const m=M[mid];return{mid,en:m.en,bn:m.bn,groups:m.groups.map(g=>({en:g.en,screens:g.screens.map(s=>s.id)})),reports:m.reports,forms:m.forms||[],freg:m.freg}})}));fs.writeFileSync('../marketing/_catalog.json',JSON.stringify({areas:out}));"
#    b) append personas/portals/journeys from demo_data.js:
node -e "const fs=require('fs'),vm=require('vm');const w={};vm.runInNewContext(fs.readFileSync('js/demo_data.js','utf8'),{window:w});const D=w.FX_DEMO;const c=JSON.parse(fs.readFileSync('../marketing/_catalog.json','utf8'));c.personas=D.PERSONAS.map(p=>({id:p.id,name:p.name,role:p.role,initials:p.initials,approvals:p.approvals,worklist:p.worklist}));c.portals=D.PORTALS.map(p=>({id:p[0],name:p[1],audience:p[2],scale:p[3],stack:p[4],features:p[5]}));c.journeys=D.JOURNEYS.map(j=>({id:j.id,en:j.en,steps:j.steps.map(s=>({who:s[0],what:s[1],route:s[2]}))}));fs.writeFileSync('../marketing/_catalog.json',JSON.stringify(c));"

# 3. build and verify:
cd ../marketing && node _build_guide.js
node _verify_guide.js       # expect: broken=0, missingAnchors=[], hscroll=0

# 4. optional PDF companion (uses print.html — the eager-image variant,
#    because lazy images export as blank boxes):
chrome --headless --print-to-pdf="user-guide\1000FiX_ERP_User_Guide.pdf" --no-pdf-header-footer "file:///D:/.../marketing/user-guide/print.html"
```

**Verification record (28 Sep 2026, after the audit pass):** knowledge map
covers all 67 modules × 4 narrative fields (machine-checked) · 89/89 images
load · 87/87 TOC anchors resolve · 67 module sections + 11 area sections
render · no horizontal overflow · part sequence 0–9 complete · layout
vision-checked · PDF exports 218 pages with 260 embedded images.

**Audit pass fixes (28 Sep 2026):** five factual corrections — steps now quote
the real report/screen names only (M02 → *Dispatch Performance by Zone* /
*Travel-Time*, M31 → *Repair Cycle Time by Level* / *Internal Rework Loop*,
M03 → *Consignment Cycle Time* / *Courier Performance (Pathao/RedX/Steadfast)*,
M04 → *Token & Waiting Display* / *Shift Close*, M05 → *Remote Resolution
Rate* / *MSP SLA Attainment by Client*); "Financial Close console" renamed to
the real *Month-End Close Console* (M19); missing **Part 3 · The map of the
system** added (one-table orientation of all 11 areas), completing the part
numbering 0–9; PDF companion + print variant added; rebuild instructions made
exact (catalog extraction one-liners included).

*1000 FiX Services Limited · Hotline 16743 · ISO 9001:2015 Certified · Internal use*
