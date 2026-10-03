# Guide Book Library — generator

The 92 Word volumes in this library are generated, not hand-written. This
folder holds the pipeline that produced them, so that the library can be
regenerated at each wave gate and after any change to a source specification.

## What it needs

* Python 3.12
* `python-docx`, `matplotlib`, `numpy`, `pillow`
* Calibri and Consolas (present on any Windows installation)

```
pip install python-docx matplotlib numpy pillow
```

## Regenerating the library

```
python build_library.py --clean --jobs 10
```

Roughly seven minutes on ten workers. Useful switches:

| Switch | Effect |
|---|---|
| `--only M01,P02,CAT-G` | Rebuild named volumes only |
| `--skip-modules` / `--skip-categories` / `--skip-master` | Partial rebuilds |
| `--out DIR` | Write somewhere other than the library folder |
| `--jobs N` | Parallel workers |

## Auditing the output

```
python audit.py
```

Checks coverage, A4 geometry, typography, navigation fields, header and
footer content, image integrity, table geometry, heading structure, text
hygiene, and content fidelity against the parsed source specifications.
`last_audit.json` is the audit that accompanied Edition 1.0: 92 documents,
zero findings at any severity.

## Where the source comes from

`catalogue.py` reads every `M*.md` and `P*.md` under
`1000fix_ERP_Module/03_Modules/`, plus the eleven `_CATEGORY_OVERVIEW.md`
files. Nothing else is read, and nothing is cached between runs — every
quantity in every volume is counted from the source files at generation time,
under register rule **RG-06**.

## Module map

| File | Responsibility |
|---|---|
| `theme.py` | The design system: type scale, palette, category accents, geometry |
| `docxkit.py` | Low-level WordprocessingML beyond what python-docx exposes |
| `mdparse.py` | Block and inline parser for the house markdown dialect |
| `spec.py` | The analytical model of one specification — every §1–§19 fact |
| `catalogue.py` | Discovery and the programme-wide cross-reference index |
| `exhibits.py` | Component-level exhibits |
| `exhibits_group.py` | Category, suite and estate-level exhibits |
| `render.py` | The typographic layer: tables, callouts, panels, captions |
| `narrative.py` | The authored guide-book framing text |
| `findings.py` | Ten integrity checks run against the source specifications |
| `guidebook.py` | Assembles one component volume |
| `groupbook.py` | Assembles a category or suite volume |
| `masterbook.py` | Assembles GB-000 |
| `build_library.py` | Orchestrator |
| `audit.py` | Post-generation inspection of the produced Word files |

## One thing worth knowing

Calibri fails to rasterise at certain point sizes when matplotlib renders below
about 240 dpi — glyphs vanish entirely and only ligatures survive. `theme.DPI`
is set to 300, which is verified free of dropout across 5–26 pt. Do not lower
it without re-running that check.

---

*1000FiX Services Limited · CONFIDENTIAL — Internal Use Only*
