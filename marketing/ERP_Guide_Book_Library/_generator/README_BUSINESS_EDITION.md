# The business-reader edition

Edition 1.0 of this library mirrored the specification: nineteen sections in
specification order, a requirement register on almost every page, and
identifiers in the first column of every table. It is accurate and it is a poor
guide book — a branch manager opening it at section 5 met `FR-SRM-047 · P0 · L2`
before meeting a sentence.

This edition inverts that. The body is written for the people who will use each
module; every identifier, delivery layer, state guard and interface contract
still exists, in Appendix A, where developers and testers will look for it.

## What changed

| | Edition 1.0 | Business edition |
|---|---|---|
| Structure | 19 sections in specification order | 3 parts and an appendix, in reading order |
| Section 5 | Requirement register, `FR-xxx` first column | "What it is called / What it does for you / A typical use at 1000FiX" |
| Worked examples | none | one per functional area, with named customers and figures |
| Walkthroughs | none | five per module, following one job across everybody who touches it |
| Technical register | throughout the body | Appendix A only |
| Exhibits | 14–15 | 20 |
| Words per module | 12,500–15,000 | 19,000–28,000 |
| Short pages | 18 of 63 in M01 | 4–5 of 54–65 |

## How to build

```
python build_business.py                 # all seven modules and the category book
python build_business.py M01             # one module
python build_business.py CAT             # the category book only

powershell -ExecutionPolicy Bypass -File Update-Fields.ps1
python audit_business.py
```

`build_business.py` renders the exhibits and assembles the Word files.
`Update-Fields.ps1` opens each one in Word to compute the contents, exhibit and
table lists and to repaginate — python-docx cannot evaluate a field.
`audit_business.py` then checks geometry, typography, navigation, images,
tables, structure, hygiene and voice. All eight documents audit clean.

## Where the content lives

Anything measurable is read from the module specifications through `spec.Spec`
and is never typed by hand. Anything that has to be *written* — the narrative,
the worked examples, the walkthroughs, the plain-English reading of each feature
and each rule — lives in `bizcontent/`, one file per module plus `common.py` for
the framing text every book shares.

The split matters. If a figure changes in a specification the guide books pick
it up on the next build with nobody editing prose. If the *meaning* of something
changes, a person has to open the content pack and say so, which is correct — no
generator should be inventing the sentence that explains what a quality gate is
for.

`bizcontent/__init__.py` validates that a content pack carries every key the
builder will ask for, so a missing section fails at load with a useful message
rather than three minutes into a build.

## The files

| File | What it is |
|---|---|
| `bizbook.py` | The module guide book builder |
| `bizcatbook.py` | The category guide book builder |
| `bizexhibits.py` | Fifteen business-reader exhibit types |
| `bizcontent/` | The authored content, one file per module |
| `build_business.py` | The runner |
| `Update-Fields.ps1` | The Word pass that computes the contents lists |
| `audit_business.py` | The artefact audit |

The first-edition generator (`guidebook.py`, `groupbook.py`, `masterbook.py`,
`exhibits.py`) is untouched and still builds the rest of the library. The two
share `theme.py`, `render.py`, `docxkit.py` and `spec.py`, so a change to the
palette or the page geometry reaches both.

## Two things worth knowing

**The vertical axis of a business exhibit is measured in inches, not in an
abstract 0–100 space.** Text is drawn at a fixed point size, so a box whose
height is a fraction of the figure will not stay in proportion to the words
inside it. Working in inches means a four-line paragraph reserves exactly four
lines and the exhibit closes up to fit its content. See the geometry note at the
top of `bizexhibits.py`.

**Calibri drops glyphs in matplotlib below about 240 dpi.** Whole runs of text
vanish with no warning. `theme.DPI` is 300 and verified clean; do not lower it.

---

*1000FiX ERP System v2.0 · ERP Guide Book Library · Confidential — Internal Use Only*
