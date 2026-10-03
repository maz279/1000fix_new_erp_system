# -*- coding: utf-8 -*-
"""
bizcatbook — the business-reader category guide book.

A module guide book answers "what can I do with this?". A category guide book
answers a different question: "how do these seven fit together, and which one
should I be reading?". It is the document a new joiner is handed first and the
one a manager takes into a meeting about somebody else's module.

It shares the exhibit library, the palette and the page geometry with the module
books, and it is deliberately shorter — a reader who wants depth is one page
reference away from the module that has it.
"""
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

import docxkit as K
import render as R
import theme as T
import bizexhibits as BX
from bizbook import CONTENT_MM, _short, _sanitise


class CategoryGuideBook(object):
    """Builds the business-reader guide book for one whole category."""

    def __init__(self, letter, specs, content, exdir, outdir):
        self.letter = letter
        self.specs = specs                      # {uid: Spec}, in reading order
        self.c = content
        self.exdir = os.path.join(exdir, "CAT-" + letter)
        self.outdir = outdir
        self.accent = T.cat_colour(letter)
        self.name = T.cat_name(letter)
        self.doc_id = "GB-CAT-%s" % letter
        self.ex = {}
        self.doc = None

    # ------------------------------------------------------------- exhibits
    def _p(self, key):
        return os.path.join(self.exdir, "CAT%s_%s.png" % (self.letter, key))

    def build_exhibits(self):
        c, a = self.c, self.accent
        os.makedirs(self.exdir, exist_ok=True)

        def keep(key, path):
            if path:
                self.ex[key] = path

        keep("headline", BX.headline(
            self._p("headline"), c["headline"], a,
            "Category %s at a glance" % self.letter,
            "The seven modules, counted from their specifications"))

        keep("weight", BX.scale_bars(
            self._p("weight"),
            [(sp.name, sp.req_count) for sp in self.specs.values()], a,
            "How much each module contains",
            "Number of distinct functions, measured from the specifications",
            unit=" functions", label_w=38.0))

        keep("effort", BX.scale_bars(
            self._p("effort"), c["effort_bars"], a,
            "How much each module costs to build",
            "Indicative person-weeks", unit=" person-weeks", label_w=38.0))

        keep("modes", BX.journey_ribbon(
            self._p("modes"), c["modes_ribbon"], a,
            "Nine ways a customer can be served",
            "Every module in the category has to support all nine",
            per_row=3))

        keep("wave", BX.journey_ribbon(
            self._p("wave"), c["wave_ribbon"], a,
            "The order the category gets built in",
            "Six waves, and what becomes possible at each",
            per_row=3))

        keep("split", BX.compare_columns(
            self._p("split"), c["split_columns"], a,
            c["split_title"], c["split_sub"]))

        keep("dials", BX.target_dials(
            self._p("dials"), c["dials"], a,
            "What the category is judged on",
            "The four numbers that summarise seven modules"))

        keep("owns", BX.capability_map(
            self._p("owns"), c["owns_map"], a,
            "What each module owns",
            "One record type each, and no overlap", per_row=3))

        keep("risks", BX.today_tomorrow(
            self._p("risks"), c["risk_rows"], T.OCHRE,
            "What could go wrong, and what is being done about it",
            "The five risks the category carries",
            head=("Module", "What could go wrong", "What is being done")))
        return self

    # ------------------------------------------------------------- document
    def _new_document(self):
        doc = Document()
        K.install_base_styles(doc)
        K.set_doc_defaults_language(doc)
        K.set_compat_and_zoom(doc)
        K.set_update_fields_on_open(doc)
        K.set_core_properties(
            doc,
            title="Category %s — %s" % (self.letter, self.name),
            subject="%s · Category Guide Book" % T.PROGRAMME,
            keywords="1000FiX, ERP, category %s, %s, guide book, SPSL"
                     % (self.letter, self.name),
            comments="Business-reader category guide book %s, %s. "
                     "CONFIDENTIAL — internal use only."
                     % (self.doc_id, T.EDITION),
            category_str="Category %s — %s" % (self.letter, self.name))
        sec = doc.sections[0]
        K.setup_section(sec, top=0, bottom=0, left=0, right=0)
        return doc

    def _header_footer(self, sec):
        K.unlink_header_footer(sec)
        K.clear_container(sec.header)
        t = sec.header.add_table(rows=1, cols=2, width=Mm(CONTENT_MM))
        K.no_table_borders(t)
        K.table_layout_fixed(t)
        K.table_width_pct(t, 100)
        K.table_cell_margins(t, top=0, left=0, bottom=40, right=0)
        for i, w in enumerate((0.55, 0.45)):
            t.columns[i].width = Mm(CONTENT_MM * w)
            t.rows[0].cells[i].width = Mm(CONTENT_MM * w)
            K.cell_borders(t.rows[0].cells[i], bottom=(6, T.RULE))
        c0, c1 = t.rows[0].cells
        p0 = c0.paragraphs[0]
        K.pfmt(p0, before=0, after=0)
        K.run(p0, "%s  ·  Category Guide Book" % T.PROGRAMME, size=7.5,
              colour=T.GREY, spacing=8)
        p1 = c1.paragraphs[0]
        K.pfmt(p1, before=0, after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
        K.run(p1, "CATEGORY %s  " % self.letter, size=7.5, bold=True,
              colour=self.accent)
        K.run(p1, _short(self.name, 46), size=7.5, colour=T.GREY)
        hp = sec.header.add_paragraph()
        K.pfmt(hp, before=0, after=0)
        hp.paragraph_format.line_spacing = Pt(2)

        K.clear_container(sec.footer)
        f = sec.footer.add_table(rows=1, cols=3, width=Mm(CONTENT_MM))
        K.no_table_borders(f)
        K.table_layout_fixed(f)
        K.table_width_pct(f, 100)
        K.table_cell_margins(f, top=40, left=0, bottom=0, right=0)
        for i, w in enumerate((0.40, 0.28, 0.32)):
            f.columns[i].width = Mm(CONTENT_MM * w)
            f.rows[0].cells[i].width = Mm(CONTENT_MM * w)
            K.cell_borders(f.rows[0].cells[i], top=(6, T.RULE))
        a, b, c = f.rows[0].cells
        pa = a.paragraphs[0]
        K.pfmt(pa, before=0, after=0)
        K.run(pa, T.CLASSIFICATION, size=7.0, bold=True, colour=T.RED)
        pb = b.paragraphs[0]
        K.pfmt(pb, before=0, after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
        K.run(pb, "%s  ·  %s" % (self.doc_id, T.EDITION), size=7.0,
              colour=T.GREY)
        pc = c.paragraphs[0]
        K.pfmt(pc, before=0, after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
        K.run(pc, "Page ", size=7.0, colour=T.GREY)
        K.add_field(pc, " PAGE ", "1", size=7.0, bold=True, colour=T.NAVY)
        K.run(pc, " of ", size=7.0, colour=T.GREY)
        K.add_field(pc, " NUMPAGES ", "1", size=7.0, colour=T.GREY)

    # ------------------------------------------------------------- helpers
    def _h1(self, number, title, page_break=False):
        if not page_break:
            R.spacer(self.doc, 12)
        R.h_section(self.doc, number, title, self.accent,
                    page_break=page_break)

    def _lede(self, text):
        p = self.doc.add_paragraph()
        K.pfmt(p, before=0, after=8, line=1.24)
        K.run(p, text, size=10.5, colour=T.INK_SOFT, italic=True)

    def _paras(self, blocks):
        for b in blocks or []:
            R.body(self.doc, b, after=6)

    def _tbl(self, header, rows, caption=None, align=None, size=None):
        if rows:
            R.table(self.doc, header, rows, align=align, accent=self.accent,
                    caption=caption, size=size)

    def _exhibit(self, key, caption):
        if self.ex.get(key):
            R.exhibit(self.doc, self.ex[key], caption, accent=self.accent)

    # ================================================================= cover
    def cover(self):
        doc, acc, c = self.doc, self.accent, self.c
        t = doc.add_table(rows=1, cols=1)
        K.no_table_borders(t)
        K.table_width_pct(t, 100)
        K.table_cell_margins(t, top=0, left=1080, bottom=520, right=760)
        ic = t.cell(0, 0)
        K.shade(ic, T.NAVY)
        K.row_height(t.rows[0], 104, rule="atLeast")
        ic.paragraphs[0]._p.getparent().remove(ic.paragraphs[0]._p)
        R.vspace(ic, 30)

        p = ic.add_paragraph()
        K.pfmt(p, before=0, after=10)
        K.run(p, T.PROGRAMME.upper(), size=8.5, bold=True, colour="7FA8CE",
              spacing=56)
        p = ic.add_paragraph()
        K.pfmt(p, before=0, after=0, line=0.92)
        K.run(p, "CATEGORY ", size=30, bold=True, colour="7FA8CE")
        K.run(p, self.letter, size=52, bold=True, colour=T.WHITE)
        p = ic.add_paragraph()
        K.pfmt(p, before=8, after=0, line=1.02)
        K.run(p, self.name, size=23, bold=True, colour=T.WHITE)
        p = ic.add_paragraph()
        K.pfmt(p, before=12, after=0)
        K.run(p, "Category Guide Book", size=12.5, colour="B9CEE4")
        p = ic.add_paragraph()
        K.pfmt(p, before=3, after=0)
        K.run(p, "How the seven modules fit together", size=9.5,
              colour="7FA8CE", italic=True)
        R.vspace(ic, 4)
        R.rule_gap(ic, acc, weight=10, space=8, gap_pt=2.0)

        strip = doc.add_table(rows=1, cols=1)
        K.no_table_borders(strip)
        K.table_width_pct(strip, 100)
        K.table_cell_margins(strip, top=110, left=1080, bottom=110, right=760)
        sc = strip.cell(0, 0)
        K.shade(sc, acc)
        K.row_height(strip.rows[0], 13, rule="exact")
        ps = sc.paragraphs[0]
        K.pfmt(ps, before=0, after=0)
        K.run(ps, "   ·   ".join(sp.uid for sp in self.specs.values()),
              size=8.5, bold=True, colour=T.WHITE, spacing=32)

        low = doc.add_table(rows=1, cols=1)
        K.no_table_borders(low)
        K.table_width_pct(low, 100)
        K.table_cell_margins(low, top=0, left=1080, bottom=240, right=760)
        lc = low.cell(0, 0)
        K.shade(lc, T.WHITE)
        lc.paragraphs[0]._p.getparent().remove(lc.paragraphs[0]._p)
        R.vspace(lc, 14)

        p = lc.add_paragraph()
        K.pfmt(p, before=0, after=14, line=1.24)
        K.run(p, c["cover_line"], size=12.0, colour=T.INK_SOFT)

        p = lc.add_paragraph()
        K.pfmt(p, before=0, after=4)
        K.run(p, "THE SEVEN MODULES", size=7.0, bold=True, colour=T.GREY,
              spacing=30)
        it = lc.add_table(rows=len(self.specs), cols=1)
        K.no_table_borders(it)
        K.table_width_pct(it, 100)
        K.table_cell_margins(it, top=30, left=0, bottom=30, right=0)
        for i, sp in enumerate(self.specs.values()):
            cell = it.rows[i].cells[0]
            K.cell_borders(cell, top=(6, T.RULE_SOFT) if i else (6, T.RULE))
            cell.paragraphs[0]._p.getparent().remove(cell.paragraphs[0]._p)
            pp = cell.add_paragraph()
            K.pfmt(pp, before=0, after=0, line=1.14)
            K.run(pp, sp.uid + "   ", size=9.0, bold=True, colour=acc)
            K.run(pp, sp.name, size=9.0, bold=True, colour=T.NAVY)
            K.run(pp, "   " + c["cover_gists"][sp.uid], size=8.5,
                  colour=T.GREY)

        R.vspace(lc, 14)
        R.rule_gap(lc, T.RULE, weight=6, space=0, gap_pt=2.0)
        p = lc.add_paragraph()
        K.pfmt(p, before=8, after=2)
        K.run(p, T.CLIENT, size=11.0, bold=True, colour=T.NAVY)
        p = lc.add_paragraph()
        K.pfmt(p, before=0, after=2, line=1.20)
        K.run(p, "Prepared for SPSL service, branch, workshop and support "
                 "teams   ·   %s   ·   Issued %s" % (T.EDITION, T.ISSUE_DATE),
              size=8.5, colour=T.GREY)
        p = lc.add_paragraph()
        K.pfmt(p, before=6, after=0)
        K.run(p, T.CLASSIFICATION, size=8.0, bold=True, colour=T.RED,
              spacing=14)
        return self

    # =============================================================== body
    def body(self):
        doc, c = self.doc, self.c

        # ---- about
        self._h1(None, "About this guide book", page_break=True)
        R.body(doc, c["about"], after=8)
        R.definition_rows(doc, [
            ("Document", "%s — Category %s, %s"
                         % (self.doc_id, self.letter, self.name)),
            ("Modules covered", "%d  ·  %s"
                                % (len(self.specs),
                                   ", ".join(self.specs.keys()))),
            ("Who it is for", c["audience"]),
            ("Read it", c["read_when"]),
            ("Edition", "%s, issued %s" % (T.EDITION, T.ISSUE_DATE)),
            ("Classification", T.CLASSIFICATION),
        ], accent=self.accent, label_mm=44)
        R.callout(doc, c["reading_note"], kind="note", accent=self.accent,
                  title="IF YOU ONLY READ ONE THING")

        # ---- contents
        R.h_section(doc, None, "Contents", self.accent, page_break=True)
        p = doc.add_paragraph()
        K.pfmt(p, before=2, after=10)
        K.add_toc(p, levels="1-2")
        R.h_section(doc, None, "Exhibits", self.accent, page_break=True)
        p = doc.add_paragraph()
        K.pfmt(p, before=2, after=10)
        K.add_table_of_figures(p, label="Exhibit")
        R.h_section(doc, None, "Tables", self.accent, page_break=False)
        p = doc.add_paragraph()
        K.pfmt(p, before=2, after=0)
        K.add_table_of_figures(p, label="Table")

        # ---- 1
        self._h1("1.", "What this part of the company does", page_break=True)
        self._lede(c["s1_lede"])
        self._paras(c["s1_intro"])
        self._exhibit("headline", "Category %s in numbers" % self.letter)
        self._tbl(["Module", "What it owns", "When it arrives"],
                  c["s1_modules"], caption="The seven modules of Category %s"
                                           % self.letter)
        R.callout(doc, c["s1_test"], kind="good", accent=self.accent,
                  title="THE TEST FOR WHAT BELONGS HERE")

        # ---- 2
        self._h1("2.", "The seven modules, one at a time")
        self._lede(c["s2_lede"])
        self._paras(c["s2_intro"])
        self._exhibit("owns", "One record type each, with no overlap")
        for m in c["module_cards"]:
            R.h_sub(doc, m["title"], self.accent, number=m["number"])
            self._paras(m["text"])
            R.definition_rows(doc, m["facts"], accent=self.accent,
                              label_mm=46)
        self._exhibit("weight", "How much each module contains")

        # ---- 3
        self._h1("3.", "Nine ways a customer can be served")
        self._lede(c["s3_lede"])
        self._paras(c["s3_intro"])
        self._exhibit("modes", "The nine delivery modes")
        self._tbl(["Delivery mode", "Which modules carry it",
                   "What is distinctive about it"],
                  c["s3_modes"], caption="The nine service delivery modes")
        if c.get("s3_note"):
            R.callout(doc, c["s3_note"], kind="note", accent=self.accent)

        # ---- 4
        self._h1("4.", "The words the whole category shares")
        self._lede(c["s4_lede"])
        self._paras(c["s4_intro"])
        self._tbl(["Word", "What it means", "Which module owns it"],
                  c["s4_vocab"], caption="Shared vocabulary across Category %s"
                                         % self.letter)

        # ---- 5
        self._h1("5.", "Where each module stops")
        self._lede(c["s5_lede"])
        self._paras(c["s5_intro"])
        self._tbl(["Capability", "Owned by", "Used but not owned by"],
                  c["s5_boundary"], caption="Who owns what across the category")
        R.h_sub(doc, c["split_heading"], self.accent)
        self._paras(c["s5_split"])
        self._exhibit("split", "The most important boundary in the category")

        # ---- 6
        self._h1("6.", "Following one job across several modules")
        self._lede(c["s6_lede"])
        self._paras(c["s6_intro"])
        for j in c["journeys"]:
            R.h_sub(doc, j["title"], self.accent, number=j["number"])
            self._paras(j["text"])
            self._tbl(["Step", "Module", "What happens"], j["steps"],
                      caption="%s — module by module" % j["title"])

        # ---- 7
        self._h1("7.", "The order it gets built in")
        self._lede(c["s7_lede"])
        self._paras(c["s7_intro"])
        self._exhibit("wave", "The delivery sequence, wave by wave")
        self._tbl(["Wave", "What arrives", "What becomes possible"],
                  c["s7_waves"], caption="The category delivery sequence")
        self._exhibit("effort", "What each module costs to build")

        # ---- 8
        self._h1("8.", "What the category is judged on")
        self._lede(c["s8_lede"])
        self._paras(c["s8_intro"])
        self._exhibit("dials", "The four headline numbers")
        self._tbl(["Measure", "Where it is today", "Where it needs to be",
                   "Which module owns it"],
                  c["s8_kpis"], caption="Category measures and their owners")

        # ---- 9
        self._h1("9.", "What could go wrong")
        self._lede(c["s9_lede"])
        self._paras(c["s9_intro"])
        self._exhibit("risks", "The five risks the category carries")
        self._tbl(["Risk", "Why it matters", "What is being done about it"],
                  c["s9_risks"], caption="Category risks and mitigations")
        R.callout(doc, c["s9_note"], kind="warning", accent=T.OCHRE)

        # ---- 10
        self._h1("10.", "Where to read next")
        self._lede(c["s10_lede"])
        self._paras(c["s10_intro"])
        self._tbl(["If you are", "Read", "In this order"],
                  c["s10_paths"], caption="Reading paths by role")
        R.callout(doc, c["s10_close"], kind="good", accent=self.accent,
                  title="THE SHORT VERSION")
        return self

    # ================================================================== build
    def build(self):
        self.doc = self._new_document()
        self.cover()
        sec = self.doc.add_section()
        K.setup_section(sec)
        K.restart_page_numbering(sec, start=1)
        self._header_footer(sec)
        self.body()

        os.makedirs(self.outdir, exist_ok=True)
        name = "CAT-%s_%s_Category_Guide_Book.docx" % (
            self.letter, _sanitise(self.name))
        path = os.path.join(self.outdir, name)
        self.doc.save(path)
        return path
