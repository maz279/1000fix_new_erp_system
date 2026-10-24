# -*- coding: utf-8 -*-
"""
bizbook — the business-reader module guide book.

The first edition of this library mirrored the specification: nineteen numbered
sections in specification order, a requirement register on almost every page,
and identifiers in the first column of every table. It is an accurate document
and a poor guide book. A branch manager opening it at section 5 meets
`FR-SRM-047 · P0 · L2` before meeting a sentence.

This builder inverts that. The body is written for somebody who has to run a
service centre, not build one: what the module is for, what changes for them on
the day it goes live, what it lets them do, and what happens when something goes
wrong. Every identifier, delivery layer, state guard and interface contract
still exists — in Appendix A, where the people who need them will look.

The content that cannot be derived — the narrative, the worked examples, the
day-in-the-life scenarios, the plain-English reading of each feature — lives in
`bizcontent/`, one module per file. Everything else is measured from the
specification through `spec.Spec`, exactly as before.
"""

import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

import docxkit as K
import render as R
import theme as T
import exhibits as X
import bizexhibits as BX

CONTENT_MM = T.CONTENT_W_MM


def _short(text, n=200):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def _sanitise(name):
    """File-safe module name, matching the first edition's naming exactly.

    The ampersand becomes 'and' rather than disappearing, so a rebuilt book
    lands on the same filename as the edition it replaces instead of sitting
    beside it.
    """
    s = str(name).replace("&", " and ")
    s = re.sub(r"[^A-Za-z0-9-]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


class BusinessGuideBook(object):
    """Builds one business-reader guide book for one module specification."""

    def __init__(self, sp, content, exdir, outdir, peers=None, doc_no=None):
        self.sp = sp
        self.c = content  # the authored content pack
        self.exdir = os.path.join(exdir, sp.uid)
        self.outdir = outdir
        self.peers = peers or {}
        self.accent = T.cat_colour(sp.category)
        self.pale = T.cat_pale(sp.category)
        self.doc_id = doc_no or ("GB-%s" % sp.uid)
        self.ex = {}
        self.doc = None
        self._table_n = 0

    # ------------------------------------------------------------- exhibits
    def _p(self, key):
        return os.path.join(self.exdir, "%s_%s.png" % (self.sp.uid, key))

    def build_exhibits(self):
        """Render every exhibit this guide book will reference."""
        sp, c, a = self.sp, self.c, self.accent
        os.makedirs(self.exdir, exist_ok=True)
        ex = self.ex

        def keep(key, path):
            if path:
                ex[key] = path
            return path

        keep(
            "headline",
            BX.headline(
                self._p("headline"),
                c["headline"],
                a,
                "%s at a glance" % sp.name,
                "The figures worth carrying into a meeting",
            ),
        )

        if c.get("volume"):
            keep(
                "volume",
                BX.volume_profile(
                    self._p("volume"),
                    c["volume"],
                    a,
                    c["volume_title"],
                    c["volume_sub"],
                ),
            )

        if sp.role_change:
            keep(
                "today",
                BX.today_tomorrow(
                    self._p("today"),
                    [(r[0], r[1], r[2]) for r in sp.role_change if len(r) >= 3],
                    a,
                    "What changes for each role on the day this goes live",
                    "The same people, the same work, a different day",
                ),
            )

        keep(
            "boundary",
            BX.boundary_panels(
                self._p("boundary"),
                c["does"],
                c["does_not"],
                a,
                "Where this module starts and stops",
                "The second column matters more than the first",
            ),
        )

        keep(
            "capability",
            BX.capability_map(
                self._p("capability"),
                c["areas_map"],
                a,
                "What this module lets you do",
                "%d functions, grouped into %d areas of work"
                % (sp.req_count, len(c["areas_map"])),
            ),
        )

        if c.get("journey"):
            keep(
                "journey",
                BX.journey_ribbon(
                    self._p("journey"),
                    c["journey"],
                    a,
                    c["journey_title"],
                    c["journey_sub"],
                ),
            )

        if c.get("gates"):
            keep(
                "gates",
                BX.gate_ladder(
                    self._p("gates"),
                    c["gates"],
                    a,
                    "The points a job cannot get past",
                    "Each one is a hard stop, not a warning",
                ),
            )

        for i, sc in enumerate(c.get("scenarios", []), 1):
            keep(
                "scenario%d" % i,
                BX.swimlane(
                    self._p("scenario%d" % i),
                    sc["lanes"],
                    a,
                    sc["exhibit_title"],
                    sc["exhibit_sub"],
                    columns=sc.get("columns"),
                ),
            )

        if c.get("automation_groups"):
            keep(
                "automation",
                BX.auto_ring(
                    self._p("automation"),
                    c["automation_groups"],
                    a,
                    "What the system does without being asked",
                    "%d automatic behaviours, grouped by what sets them off"
                    % sum(g[1] for g in c["automation_groups"]),
                ),
            )

        if c.get("permissions"):
            pm = c["permissions"]
            keep(
                "permissions",
                BX.who_can(
                    self._p("permissions"),
                    pm["roles"],
                    pm["actions"],
                    pm["marks"],
                    a,
                    "Who may do what",
                    pm.get("sub", "The actions people argue about most"),
                ),
            )

        if c.get("dials"):
            keep(
                "dials",
                BX.target_dials(
                    self._p("dials"),
                    c["dials"],
                    a,
                    "What good looks like",
                    "The numbers this module is judged on",
                ),
            )

        if c.get("channels"):
            keep(
                "channels",
                BX.fan_in(
                    self._p("channels"),
                    c["channels"],
                    c["channels_hub"],
                    a,
                    c["channels_title"],
                    c["channels_sub"],
                    hub_note=c.get("channels_note"),
                ),
            )

        if c.get("benefits"):
            keep(
                "benefits",
                BX.benefit_stack(
                    self._p("benefits"),
                    c["benefits"],
                    a,
                    "What this module is worth in a year",
                    "Annual value the specification attributes to this module",
                    note=c.get("benefits_note"),
                ),
            )

        # neighbour map reuses the specification-side exhibit; it is the one
        # place a business reader genuinely wants the module codes
        up = [r[0] for r in sp.upstream] if sp.upstream else []
        dn = [r[0] for r in sp.downstream] if sp.downstream else []
        if up or dn:
            keep(
                "neighbours",
                X.integration_surface(
                    self._p("neighbours"),
                    sp.uid,
                    sp.upstream,
                    sp.downstream,
                    sp.events,
                    getattr(sp, "externals", []) or [],
                    a,
                    "Who this module depends on, and who depends on it",
                    "Every arrow is a working relationship somebody has to maintain",
                ),
            )

        if c.get("kinds_columns"):
            keep(
                "kinds",
                BX.compare_columns(
                    self._p("kinds"),
                    c["kinds_columns"],
                    a,
                    c["kinds_title"],
                    c["kinds_sub"],
                ),
            )

        if c.get("area_bars"):
            keep(
                "area_bars",
                BX.scale_bars(
                    self._p("area_bars"),
                    c["area_bars"],
                    a,
                    "Where the work is concentrated",
                    "Number of distinct functions in each area of the module",
                    unit=" functions",
                ),
            )
        return self

    # ------------------------------------------------------------- document
    def _new_document(self):
        doc = Document()
        K.install_base_styles(doc)
        K.set_doc_defaults_language(doc)
        K.set_compat_and_zoom(doc)
        K.set_update_fields_on_open(doc)
        sp = self.sp
        K.set_core_properties(
            doc,
            title="%s — %s" % (sp.uid, sp.name),
            subject="%s · Module Guide Book · Category %s — %s"
            % (T.PROGRAMME, sp.category, T.cat_name(sp.category)),
            keywords="1000FiX, ERP, %s, %s, %s, guide book, SPSL, "
            "after-sales service, Bangladesh" % (sp.uid, sp.code, sp.name),
            comments="Business-reader guide book %s, %s. Written for the "
            "people who will use the module, from specification %s "
            "(version %s, %s). CONFIDENTIAL — internal use only."
            % (self.doc_id, T.EDITION, sp.filename, sp.version, sp.date),
            category_str="Category %s — %s" % (sp.category, T.cat_name(sp.category)),
        )
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
        t.columns[0].width = Mm(CONTENT_MM * 0.55)
        t.columns[1].width = Mm(CONTENT_MM * 0.45)
        c0, c1 = t.rows[0].cells
        c0.width = Mm(CONTENT_MM * 0.55)
        c1.width = Mm(CONTENT_MM * 0.45)
        p0 = c0.paragraphs[0]
        K.pfmt(p0, before=0, after=0)
        K.run(
            p0,
            "%s  ·  Module Guide Book" % T.PROGRAMME,
            size=7.5,
            colour=T.GREY,
            spacing=8,
        )
        p1 = c1.paragraphs[0]
        K.pfmt(p1, before=0, after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
        K.run(p1, "%s  " % self.sp.uid, size=7.5, bold=True, colour=self.accent)
        K.run(p1, _short(self.sp.name, 46), size=7.5, colour=T.GREY)
        for c in (c0, c1):
            K.cell_borders(c, bottom=(6, T.RULE))
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
        K.run(pb, "%s  ·  %s" % (self.doc_id, T.EDITION), size=7.0, colour=T.GREY)
        pc = c.paragraphs[0]
        K.pfmt(pc, before=0, after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
        K.run(pc, "Page ", size=7.0, colour=T.GREY)
        K.add_field(pc, " PAGE ", "1", size=7.0, bold=True, colour=T.NAVY)
        K.run(pc, " of ", size=7.0, colour=T.GREY)
        K.add_field(pc, " NUMPAGES ", "1", size=7.0, colour=T.GREY)

    # ------------------------------------------------------------------ helpers
    def _h1(self, number, title, kicker=None, page_break=False):
        """A numbered section.

        Sections flow rather than each starting a fresh page. Forcing a break
        at every heading is what left the first edition with pages carrying a
        single spilled table row and nothing else. The heading already keeps
        with the text that follows it, and the part dividers still break, so
        the book stays navigable without the holes.
        """
        if not page_break:
            R.spacer(self.doc, 12)
        R.h_section(
            self.doc, number, title, self.accent, page_break=page_break, kicker=kicker
        )

    def _lede(self, text):
        """The italic standfirst under a section heading."""
        p = self.doc.add_paragraph()
        K.pfmt(p, before=0, after=8, line=1.24)
        K.run(p, text, size=10.5, colour=T.INK_SOFT, italic=True)

    def _paras(self, blocks, size=T.SIZE_BODY):
        for b in blocks or []:
            R.body(self.doc, b, size=size, after=6)

    def _tbl(self, header, rows, align=None, caption=None, size=None, note=None):
        if not rows:
            return
        R.table(
            self.doc,
            header,
            rows,
            align=align,
            accent=self.accent,
            caption=caption,
            size=size,
            note=note,
        )

    def _exhibit(self, key, caption, source=None):
        path = self.ex.get(key)
        if not path:
            return False
        R.exhibit(self.doc, path, caption, accent=self.accent, source=source)
        return True

    def _example(self, title, text):
        R.callout(
            self.doc,
            text,
            kind="insight",
            accent=self.accent,
            title="WORKED EXAMPLE — %s" % title.upper(),
        )

    def _part(self, number, title, blurb, sections, accent=None):
        """A part divider that also says what is in the part.

        A bare divider leaves most of a page empty. Listing the sections costs
        nothing, fills the page honestly, and gives the reader a second place
        to navigate from besides the contents.
        """
        doc = self.doc
        acc = accent or self.accent
        R.part_opener(doc, number, title, blurb, acc)
        if not sections:
            return
        R.vspace(doc, 6)
        p = doc.add_paragraph()
        K.pfmt(p, before=0, after=6)
        K.run(p, "IN THIS PART", size=7.5, bold=True, colour=T.GREY, spacing=34)
        t = doc.add_table(rows=len(sections), cols=2)
        K.no_table_borders(t)
        K.table_layout_fixed(t)
        K.table_width_pct(t, 100)
        K.table_cell_margins(t, top=60, left=0, bottom=60, right=110)
        t.columns[0].width = Mm(CONTENT_MM * 0.34)
        t.columns[1].width = Mm(CONTENT_MM * 0.66)
        for i, (num, name, gist) in enumerate(sections):
            c0, c1 = t.rows[i].cells
            c0.width = Mm(CONTENT_MM * 0.34)
            c1.width = Mm(CONTENT_MM * 0.66)
            for c in (c0, c1):
                K.cell_borders(c, top=(6, T.RULE_SOFT) if i else (6, T.RULE))
            p0 = c0.paragraphs[0]
            K.pfmt(p0, before=0, after=0, line=1.16)
            K.run(p0, "%s  " % num, size=10.0, bold=True, colour=acc)
            K.run(p0, name, size=9.5, bold=True, colour=T.NAVY)
            p1 = c1.paragraphs[0]
            K.pfmt(p1, before=0, after=0, line=1.16)
            K.run(p1, gist, size=9.0, colour=T.INK_SOFT)

    # ================================================================= cover
    def cover(self):
        doc, sp, acc = self.doc, self.sp, self.accent

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
        K.run(p, T.PROGRAMME.upper(), size=8.5, bold=True, colour="7FA8CE", spacing=56)
        p = ic.add_paragraph()
        K.pfmt(p, before=0, after=0, line=0.90)
        K.run(p, sp.uid, size=52, bold=True, colour=T.WHITE)
        K.run(p, "   ", size=52, colour=T.WHITE)
        K.run(p, sp.code or "", size=15, bold=True, colour=acc)
        p = ic.add_paragraph()
        K.pfmt(p, before=6, after=0, line=1.02)
        K.run(p, sp.name, size=23, bold=True, colour=T.WHITE)
        p = ic.add_paragraph()
        K.pfmt(p, before=12, after=0)
        K.run(p, "Module Guide Book", size=12.5, colour="B9CEE4")
        p = ic.add_paragraph()
        K.pfmt(p, before=3, after=0)
        K.run(
            p,
            "Written for the people who will use it",
            size=9.5,
            colour="7FA8CE",
            italic=True,
        )
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
        K.run(
            ps,
            "CATEGORY %s   ·   %s" % (sp.category, T.cat_name(sp.category).upper()),
            size=8.5,
            bold=True,
            colour=T.WHITE,
            spacing=32,
        )

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
        K.run(p, self.c["cover_line"], size=12.0, colour=T.INK_SOFT)

        # what is inside — the strip that used to be dead white space
        p = lc.add_paragraph()
        K.pfmt(p, before=0, after=4)
        K.run(p, "WHAT IS INSIDE", size=7.0, bold=True, colour=T.GREY, spacing=30)
        inside = self.c["cover_inside"]
        it = lc.add_table(rows=len(inside), cols=1)
        K.no_table_borders(it)
        K.table_width_pct(it, 100)
        K.table_cell_margins(it, top=34, left=0, bottom=34, right=0)
        for i, (label, text) in enumerate(inside):
            cell = it.rows[i].cells[0]
            K.cell_borders(cell, top=(6, T.RULE_SOFT) if i else (6, T.RULE))
            cell.paragraphs[0]._p.getparent().remove(cell.paragraphs[0]._p)
            pp = cell.add_paragraph()
            K.pfmt(pp, before=0, after=0, line=1.16)
            K.run(pp, label + "   ", size=9.0, bold=True, colour=acc)
            K.run(pp, text, size=9.0, colour=T.INK_SOFT)

        R.vspace(lc, 16)
        R.rule_gap(lc, T.RULE, weight=6, space=0, gap_pt=2.0)
        p = lc.add_paragraph()
        K.pfmt(p, before=8, after=2)
        K.run(p, T.CLIENT, size=11.0, bold=True, colour=T.NAVY)
        p = lc.add_paragraph()
        K.pfmt(p, before=0, after=2, line=1.20)
        K.run(
            p,
            "Prepared for SPSL service, branch, workshop and support "
            "teams   ·   %s   ·   Issued %s" % (T.EDITION, T.ISSUE_DATE),
            size=8.5,
            colour=T.GREY,
        )
        p = lc.add_paragraph()
        K.pfmt(p, before=6, after=0)
        K.run(p, T.CLASSIFICATION, size=8.0, bold=True, colour=T.RED, spacing=14)
        return self

    # ====================================================== document control
    def document_control(self):
        doc, sp = self.doc, self.sp
        self._h1(None, "About this guide book", page_break=True)
        R.body(doc, self.c["about"], after=8)

        R.definition_rows(
            doc,
            [
                ("Document", "%s — %s" % (self.doc_id, sp.name)),
                (
                    "Module",
                    "%s  ·  code %s  ·  category %s, %s"
                    % (sp.uid, sp.code or "—", sp.category, T.cat_name(sp.category)),
                ),
                ("Who it is for", self.c["audience"]),
                (
                    "Who owns the module",
                    "%s on the business side; %s in engineering"
                    % (sp.business_owner or "—", sp.system_owner or "—"),
                ),
                ("Edition", "%s, issued %s" % (T.EDITION, T.ISSUE_DATE)),
                (
                    "Built from",
                    "%s, version %s, dated %s" % (sp.filename, sp.version, sp.date),
                ),
                ("Classification", T.CLASSIFICATION),
            ],
            accent=self.accent,
            label_mm=44,
        )

        R.h_sub(doc, "How this guide book is arranged", self.accent)
        R.body(doc, self.c["how_arranged"], after=7)
        self._tbl(
            ["Part", "What it covers", "Read it when"],
            self.c["parts_table"],
            caption="How this guide book is arranged",
        )

        R.callout(
            doc,
            self.c["reading_note"],
            kind="note",
            accent=self.accent,
            title="IF YOU ONLY READ ONE THING",
        )

        R.h_sub(doc, "A note on the technical appendix", self.accent)
        R.body(doc, self.c["appendix_note"], after=6)
        return self

    # =============================================================== contents
    def contents(self):
        doc = self.doc
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
        return self

    # ============================================== PART ONE — understanding
    def part_one(self):
        doc, sp, c = self.doc, self.sp, self.c
        self._part(
            "Part one",
            "Understanding this module",
            c["part1_blurb"],
            c["part1_sections"],
        )

        # --- 1. What this module is for
        self._h1("1.", "What this module is for", page_break=False)
        self._lede(c["s1_lede"])
        self._paras(c["s1_intro"])
        self._exhibit("headline", "%s in numbers" % sp.uid)
        R.h_sub(doc, "The problem it was built to solve", self.accent)
        self._paras(c["s1_problem"])
        if self.ex.get("volume"):
            self._exhibit("volume", c["volume_caption"])
        R.h_sub(doc, "What it replaces", self.accent)
        self._tbl(
            ["What happens now", "What happens instead", "Why it matters"],
            c["s1_replaces"],
            caption="What this module replaces",
        )
        R.callout(
            doc,
            c["s1_one_sentence"],
            kind="good",
            accent=self.accent,
            title="THE MODULE IN ONE SENTENCE",
        )

        # --- 2. Who uses it
        self._h1("2.", "Who uses it, and what changes for them")
        self._lede(c["s2_lede"])
        self._paras(c["s2_intro"])
        self._exhibit("today", "What changes for each role")
        self._tbl(
            ["Role", "What they use it for", "What they see first"],
            c["s2_roles"],
            caption="Who uses this module, and for what",
        )
        for role in c.get("s2_days", []):
            R.h_sub(doc, role["title"], self.accent)
            self._paras(role["text"])
        if c.get("s2_note"):
            R.callout(doc, c["s2_note"], kind="note", accent=self.accent)

        # --- 3. Boundary
        self._h1("3.", "Where this module starts and stops")
        self._lede(c["s3_lede"])
        self._paras(c["s3_intro"])
        self._exhibit("boundary", "What this module owns, and what it hands on")
        R.h_sub(doc, "Things more than one module touches", self.accent)
        R.body(doc, c["s3_shared_intro"], after=6)
        self._tbl(
            ["The thing", "Who owns it", "What this module does with it"],
            c["s3_shared"],
            caption="Shared concepts and who owns them",
        )

        # --- 4. The kinds of work it handles
        self._h1("4.", c["s4k_title"])
        self._lede(c["s4k_lede"])
        self._paras(c["s4k_intro"])
        self._exhibit("kinds", c["s4k_caption"])
        self._tbl(c["s4k_header"], c["s4k_table"], caption=c["s4k_caption"])
        if c.get("s4k_note"):
            R.callout(doc, c["s4k_note"], kind="note", accent=self.accent)

        # --- 5. The words we use
        self._h1("5.", "The words we use")
        self._lede(c["s4_lede"])
        self._paras(c.get("s4_intro"))
        self._tbl(
            ["Word", "What it means here", "Where you will meet it"],
            c["s4_glossary"],
            caption="The vocabulary of this module",
        )
        return self

    # ================================================ PART TWO — what you can do
    def part_two(self):
        doc, sp, c = self.doc, self.sp, self.c
        self._part(
            "Part two", "What you can do with it", c["part2_blurb"], c["part2_sections"]
        )

        # --- 5. Everything it lets you do
        self._h1("6.", "Everything this module lets you do", page_break=False)
        self._lede(c["s5_lede"])
        self._paras(c["s5_intro"])
        self._exhibit("capability", "The areas of work this module covers")
        if self.ex.get("channels"):
            self._exhibit("channels", c["channels_caption"])

        for i, area in enumerate(c["areas"], 1):
            R.h_sub(doc, area["title"], self.accent, number="6.%d" % i)
            self._paras(area["intro"])
            self._tbl(
                [
                    "What it is called",
                    "What it does for you",
                    "A typical use at 1000FiX",
                ],
                area["features"],
                align=["left", "left", "left"],
                caption="%s — what you can do" % area["title"],
            )
            if area.get("who"):
                R.definition_rows(doc, area["who"], accent=self.accent, label_mm=46)
            if area.get("example"):
                self._example(area["example"][0], area["example"][1])
            if area.get("mistakes"):
                R.h_minor(doc, "Where people go wrong here")
                R.bullets(doc, area["mistakes"], accent=self.accent)
            if area.get("caution"):
                R.callout(doc, area["caution"], kind="warning", accent=T.OCHRE)

        if self.ex.get("area_bars"):
            self._exhibit("area_bars", "Where the functions are concentrated")

        # --- 6. The journey of a job
        self._h1("7.", c["s6_title"])
        self._lede(c["s6_lede"])
        self._paras(c["s6_intro"])
        self._exhibit("journey", c["journey_caption"])
        self._tbl(
            ["Stage", "What it means", "Who moves it on", "What must be true first"],
            c["s6_stages"],
            caption="Every stage, and what it takes to leave it",
        )
        R.h_sub(doc, "The points a job cannot get past", self.accent)
        R.body(doc, c["s6_gates_intro"], after=6)
        self._exhibit("gates", "The hard stops, in the order a job meets them")
        if c.get("s6_wrong"):
            R.h_sub(doc, "What goes wrong at each stage", self.accent)
            R.body(doc, c["s6_wrong_intro"], after=6)
            self._tbl(
                [
                    "Stage",
                    "What commonly goes wrong here",
                    "How you will know",
                    "What to do",
                ],
                c["s6_wrong"],
                caption="Where jobs get stuck, stage by stage",
            )
        if c.get("s6_note"):
            R.callout(doc, c["s6_note"], kind="note", accent=self.accent)

        # --- 7. A day in the life
        self._h1("8.", "A day in the life")
        self._lede(c["s7_lede"])
        self._paras(c["s7_intro"])
        for i, sc in enumerate(c["scenarios"], 1):
            R.h_sub(doc, sc["title"], self.accent, number="8.%d" % i)
            self._paras(sc["narrative"])
            self._exhibit("scenario%d" % i, sc["caption"])
            if sc.get("table"):
                self._tbl(
                    ["Step", "Who does it", "What happens in the system"],
                    sc["table"],
                    caption="%s — step by step" % sc["title"],
                )
            R.callout(
                doc,
                sc["outcome"],
                kind="good",
                accent=self.accent,
                title="WHAT IT ADDS UP TO",
            )

        # --- 9. Putting it together
        self._h1("9.", "What the walkthroughs have in common")
        self._lede(c["s9t_lede"])
        self._paras(c["s9t_intro"])
        self._tbl(
            ["The pattern", "Where you saw it", "Why it matters"],
            c["s9t_table"],
            caption="The habits the module builds in",
        )
        R.callout(
            doc,
            c["s9t_close"],
            kind="good",
            accent=self.accent,
            title="THE THREAD RUNNING THROUGH ALL OF THEM",
        )
        return self

    # ============================================ PART THREE — working with it
    def part_three(self):
        doc, sp, c = self.doc, self.sp, self.c
        self._part(
            "Part three", "Working with it well", c["part3_blurb"], c["part3_sections"]
        )

        # --- 8. Rules
        self._h1("10.", "The rules the system will enforce", page_break=False)
        self._lede(c["s8_lede"])
        self._paras(c["s8_intro"])
        self._tbl(
            [
                "What you will not be able to do",
                "Why the rule exists",
                "What to do instead",
            ],
            c["s8_rules"],
            caption="The rules you will meet, in plain words",
        )
        if c.get("s8_note"):
            R.callout(doc, c["s8_note"], kind="warning", accent=T.OCHRE)

        # --- 9. Automation
        self._h1("11.", "What happens without anyone asking")
        self._lede(c["s9_lede"])
        self._paras(c["s9_intro"])
        self._exhibit("automation", "Everything the system does on its own")
        self._tbl(
            ["What the system does", "What sets it off", "Who sees it"],
            c["s9_table"],
            caption="Automatic behaviour, and who it reaches",
        )

        # --- 10. Who may do what
        self._h1("12.", "Who may do what")
        self._lede(c["s10_lede"])
        self._paras(c["s10_intro"])
        self._exhibit("permissions", "The permission grid at a glance")
        self._tbl(
            ["Role", "What the role is for", "What only this role can do"],
            c["s10_roles"],
            caption="Roles in this module",
        )
        if c.get("s10_restrictions"):
            R.h_sub(doc, "What is hidden, and from whom", self.accent)
            R.body(doc, c["s10_restrictions_intro"], after=6)
            self._tbl(
                ["What is restricted", "Who can see it", "Why"],
                c["s10_restrictions"],
                caption="Field-level restrictions and separations",
            )
        if c.get("s10_note"):
            R.callout(doc, c["s10_note"], kind="note", accent=self.accent)

        # --- 11. What you can see and measure
        self._h1("13.", "What you can see and measure")
        self._lede(c["s11_lede"])
        self._paras(c["s11_intro"])
        self._exhibit("dials", "The numbers this module is judged on")
        R.h_sub(doc, "Reports you can run", self.accent)
        self._tbl(
            ["Report", "What question it answers", "Who usually runs it"],
            c["s11_reports"],
            caption="Reports available from this module",
        )
        R.h_sub(doc, "The measures behind them", self.accent)
        self._tbl(
            ["Measure", "What it tells you", "What good looks like"],
            c["s11_kpis"],
            caption="Measures and their targets",
        )
        if c.get("s11_reading"):
            R.h_sub(doc, c["s11_reading_title"], self.accent)
            self._paras(c["s11_reading"])
            if c.get("s11_reading_table"):
                self._tbl(
                    [
                        "What you are looking at",
                        "What it is telling you",
                        "What to do about it",
                    ],
                    c["s11_reading_table"],
                    caption="Reading the board",
                )

        # --- 12. Neighbours
        self._h1("14.", "Where this module meets the others")
        self._lede(c["s12_lede"])
        self._paras(c["s12_intro"])
        self._exhibit(
            "neighbours", "Everything this module reads, and everything that reads it"
        )
        R.h_sub(doc, "What it cannot work without", self.accent)
        self._tbl(
            ["Module", "What it supplies", "What breaks without it"],
            c["s12_upstream"],
            caption="Modules this one depends on",
        )
        R.h_sub(doc, "What cannot work without it", self.accent)
        self._tbl(
            ["Module", "What it takes from here", "What breaks without it"],
            c["s12_downstream"],
            caption="Modules that depend on this one",
        )
        for rel in c.get("s12_close_up", []):
            R.h_sub(doc, rel["title"], self.accent)
            self._paras(rel["text"])
        if c.get("s12_note"):
            R.callout(doc, c["s12_note"], kind="note", accent=self.accent)

        # --- 13. When something goes wrong
        self._h1("15.", "When something goes wrong")
        self._lede(c["s13_lede"])
        self._paras(c["s13_intro"])
        self._tbl(
            ["What you are seeing", "What it usually means", "What to do"],
            c["s13_troubleshooting"],
            caption="Common problems and what to do about them",
        )
        R.h_sub(doc, "Questions people ask", self.accent)
        self._tbl(
            ["Question", "Answer"], c["s13_faq"], caption="Frequently asked questions"
        )

        # --- 14. What it is worth
        self._h1("16.", "What this module is worth")
        self._lede(c["s14_lede"])
        self._paras(c["s14_intro"])
        if self.ex.get("benefits"):
            self._exhibit("benefits", "Annual value, by where it comes from")
        self._tbl(
            ["Benefit", "How it happens", "What it is worth"],
            c["s14_benefits"],
            caption="Quantified benefits",
        )
        R.h_sub(doc, "The benefits that are not money", self.accent)
        self._tbl(
            ["Benefit", "Why it matters"],
            c["s14_soft"],
            caption="Benefits that do not appear in a budget",
        )
        R.callout(
            doc,
            c["s14_close"],
            kind="good",
            accent=self.accent,
            title="THE SHORT VERSION",
        )

        # --- 17. Learning it
        self._h1("17.", "Learning it")
        self._lede(c["s17_lede"])
        self._paras(c["s17_intro"])
        self._tbl(
            ["When", "What to do", "How long", "You will be able to"],
            c["s17_plan"],
            caption="A first fortnight with this module",
        )
        R.h_sub(doc, "How you will know you have got it", self.accent)
        R.body(doc, c["s17_check_intro"], after=6)
        R.bullets(doc, c["s17_checks"], accent=self.accent)
        if c.get("s17_note"):
            R.callout(doc, c["s17_note"], kind="note", accent=self.accent)

        # --- 18. the one page to keep
        self._h1("18.", "The one page to keep")
        self._lede(c["s15_lede"])
        R.body(
            doc,
            "Everything in this guide book that somebody actually "
            "needs in a meeting, at a counter or on a first day, on a "
            "single page. Print it if it helps.",
            after=8,
        )
        R.kpi_strip(doc, c["s15_figures"], accent=self.accent, cols=4)
        R.h_sub(doc, "What it is", self.accent)
        R.body(doc, c["s1_one_sentence"], after=7)
        R.h_sub(doc, "The stages a job passes through", self.accent)
        R.body(doc, "  →  ".join(s[0] for s in c["journey"]), after=7)
        R.h_sub(doc, "The things it will not let you do", self.accent)
        R.bullets(doc, c["s15_never"], accent=self.accent)
        R.h_sub(doc, "Where to look when something is wrong", self.accent)
        R.definition_rows(doc, c["s15_where"], accent=self.accent, label_mm=52)
        return self

    # ================================================ APPENDIX A — technical
    def appendix(self):
        doc, sp, c = self.doc, self.sp, self.c
        self._part(
            "Appendix A",
            "Technical reference",
            c["appendix_blurb"],
            c["appendix_sections"],
            accent=T.NAVY,
        )

        R.h_section(doc, "A.1", "Module register entry", T.NAVY, page_break=False)
        R.body(
            doc,
            "The permanent registry record for this module. Module IDs "
            "and module codes never change and are never reused.",
            after=6,
        )
        R.definition_rows(doc, list(sp.identity.items()), accent=T.NAVY, label_mm=44)

        R.h_section(doc, "A.2", "Requirement index", T.NAVY)
        R.body(
            doc,
            "Every function described in Part two, in identifier order, "
            "with the priority and delivery layer it will be built in. "
            "This is the list a developer estimates from and a tester "
            "writes cases against.",
            after=6,
        )
        rows = [
            [r["id"], r["feature"], r["function"], r["pri"], r["layer"]]
            for r in sorted(sp.reqs, key=lambda r: r["id"])
        ]
        R.table(
            doc,
            ["ID", "Feature", "Function", "Pri", "Layer"],
            rows,
            align=["left", "left", "left", "center", "center"],
            accent=T.NAVY,
            size=T.SIZE_TABLE_DENSE,
            caption="Complete requirement index for %s" % sp.uid,
        )

        if sp.tech_funcs:
            R.h_section(doc, "A.3", "Technical functions", T.NAVY)
            R.body(
                doc,
                "Engineering behaviours no user will see and every "
                "operator will eventually depend on.",
                after=6,
            )
            R.table(
                doc,
                sp.tech_header,
                sp.tech_funcs,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Technical functions",
            )

        if sp.rules:
            R.h_section(doc, "A.4", "Business rules as specified", T.NAVY)
            R.body(
                doc,
                "The enforced rules with their permanent identifiers "
                "and rule classes. Section 8 gives the plain-English "
                "reading; this is the contract.",
                after=6,
            )
            R.table(
                doc,
                ["ID", "Rule", "Class", "Owner"],
                [
                    [r["id"], r["rule"], r["class"], r.get("owner", "")]
                    for r in sp.rules
                ],
                align=["left", "left", "center", "left"],
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Business rule register",
            )

        if sp.transitions:
            R.h_section(doc, "A.5", "State model and transition guards", T.NAVY)
            R.body(
                doc,
                "The lifecycle as a state machine. A transition that is "
                "not in this table must not be possible in the built "
                "system.",
                after=6,
            )
            R.table(
                doc,
                sp.transitions_header,
                sp.transitions,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Transition guards",
            )

        if sp.owned_entities or sp.ref_entities:
            R.h_section(doc, "A.6", "Data entities", T.NAVY)
            if sp.owned_entities:
                R.h_sub(doc, "Owned by this module", T.NAVY)
                R.table(
                    doc,
                    sp.owned_header,
                    sp.owned_entities,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Owned entities",
                )
            if sp.ref_entities:
                R.h_sub(doc, "Referenced from elsewhere", T.NAVY)
                R.table(
                    doc,
                    sp.ref_header,
                    sp.ref_entities,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Referenced entities",
                )

        R.h_section(doc, "A.7", "Interfaces", T.NAVY)
        if sp.upstream:
            R.h_sub(doc, "Consumed", T.NAVY)
            R.table(
                doc,
                sp.up_header,
                sp.upstream,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Upstream interfaces",
            )
        if sp.downstream:
            R.h_sub(doc, "Provided", T.NAVY)
            R.table(
                doc,
                sp.down_header,
                sp.downstream,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Downstream interfaces",
            )
        if sp.events:
            R.h_sub(doc, "Domain events published", T.NAVY)
            R.table(
                doc,
                sp.events_header,
                sp.events,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Domain events",
            )
        if sp.api:
            R.h_sub(doc, "API surface", T.NAVY)
            R.table(
                doc,
                sp.api_header,
                sp.api,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="API surface",
            )

        if sp.roles:
            R.h_section(doc, "A.8", "Roles and permissions as specified", T.NAVY)
            R.body(
                doc,
                "Access is written in the house notation: C create, "
                "R read, U update, D delete, A approve.",
                after=6,
            )
            # A few roles in the specification carry no register number.
            # An em dash says so; an empty cell reads as a mistake.
            R.table(
                doc,
                ["ID", "Role", "Access", "Scope"],
                [
                    [r["id"] or "—", r["name"], r["access"], r["scope"]]
                    for r in sp.roles
                ],
                align=["left", "left", "center", "left"],
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Role permission matrix",
            )

        if sp.automations:
            R.h_section(doc, "A.9", "Automations as specified", T.NAVY)
            R.table(
                doc,
                sp.automation_header,
                sp.automations,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Automation register",
            )

        if sp.kpis or sp.reports:
            R.h_section(doc, "A.10", "Reports and measures as specified", T.NAVY)
            if sp.reports:
                R.h_sub(doc, "Reports", T.NAVY)
                R.table(
                    doc,
                    sp.reports_header,
                    sp.reports,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Report register",
                )
            if sp.kpis:
                R.h_sub(doc, "Measures", T.NAVY)
                R.table(
                    doc,
                    sp.kpis_header,
                    sp.kpis,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Measure register",
                )

        if sp.benchmark:
            R.h_section(doc, "A.11", "How this compares with the big suites", T.NAVY)
            R.body(
                doc,
                "What the equivalent capability looks like in the "
                "enterprise products this design was measured against, "
                "and what 1000FiX took from each.",
                after=6,
            )
            R.table(
                doc,
                sp.benchmark_header,
                sp.benchmark,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Benchmark basis",
            )
            for b in sp.design_position:
                R.body(doc, b["text"], after=5)

        if sp.acceptance:
            R.h_section(doc, "A.12", "Acceptance criteria", T.NAVY)
            R.body(
                doc,
                "What has to be demonstrably true before this module is "
                "accepted as delivered.",
                after=6,
            )
            R.table(
                doc,
                sp.acceptance_header,
                sp.acceptance,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Acceptance criteria",
            )

        if getattr(sp, "questions", None):
            R.h_section(doc, "A.13", "Open questions", T.NAVY)
            R.body(
                doc,
                "Decisions the specification records as still open. "
                "They are listed here so that nobody plans around an "
                "answer that has not been given.",
                after=6,
            )
            R.table(
                doc,
                sp.questions_header,
                sp.questions,
                accent=T.NAVY,
                size=T.SIZE_TABLE_DENSE,
                caption="Open questions",
            )

        if sp.layer_rows or sp.cd_items or sp.sequencing or sp.migration:
            R.h_section(doc, "A.14", "How it will be delivered", T.NAVY)
            R.body(
                doc,
                "Which parts come from the standard product, which "
                "from community modules and which have to be written; "
                "the build sequence; and what has to be migrated "
                "before go-live.",
                after=6,
            )
            if sp.layer_rows:
                R.h_sub(doc, "Layer allocation", T.NAVY)
                R.table(
                    doc,
                    sp.layer_header,
                    sp.layer_rows,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Layer allocation",
                )
            if sp.cd_items:
                R.h_sub(doc, "Custom development", T.NAVY)
                R.table(
                    doc,
                    sp.cd_header,
                    sp.cd_items,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Custom development items",
                )
            if sp.sequencing:
                R.h_sub(doc, "Build sequence", T.NAVY)
                R.table(
                    doc,
                    sp.seq_header,
                    sp.sequencing,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Build sequence",
                )
            if sp.migration:
                R.h_sub(doc, "Data migration", T.NAVY)
                R.table(
                    doc,
                    sp.mig_header,
                    sp.migration,
                    accent=T.NAVY,
                    size=T.SIZE_TABLE_DENSE,
                    caption="Data migration",
                )

        R.h_section(doc, "A.15", "Where this came from", T.NAVY)
        R.body(
            doc,
            "Every claim in this guide book traces to the specification "
            "below, and through it to the workspace documents the "
            "specification cites.",
            after=6,
        )
        R.definition_rows(
            doc,
            [
                ("Specification", sp.filename),
                ("Version", "%s, dated %s" % (sp.version, sp.date)),
                ("Status", sp.status),
                ("Functions described", str(sp.req_count)),
                ("Rules enforced", str(len(sp.rules))),
                ("Automatic behaviours", str(len(sp.automations))),
                ("Roles", str(len(sp.roles))),
                ("Reports", str(len(sp.reports))),
                ("Measures", str(len(sp.kpis))),
            ],
            accent=T.NAVY,
            label_mm=44,
            keep_together=True,
        )
        return self

    # ==================================================================== end
    def back_matter(self):
        doc, c = self.doc, self.c
        R.spacer(doc, 14)
        R.h_section(
            doc,
            "Appendix B",
            "Change control and feedback",
            self.accent,
            page_break=False,
        )
        R.body(doc, c["change_control"], after=7)
        self._tbl(
            ["What you found", "Who to tell", "What happens next"],
            c["change_table"],
            caption="How to get this guide book fixed",
        )
        R.callout(doc, c["change_note"], kind="note", accent=self.accent)
        return self

    # ================================================================== build
    def build(self):
        self.doc = self._new_document()
        self.cover()

        sec = self.doc.add_section()
        K.setup_section(sec)
        K.restart_page_numbering(sec, start=1)
        self._header_footer(sec)

        (
            self.document_control()
            .contents()
            .part_one()
            .part_two()
            .part_three()
            .appendix()
            .back_matter()
        )

        os.makedirs(self.outdir, exist_ok=True)
        name = "%s_%s_Guide_Book.docx" % (self.sp.uid, _sanitise(self.sp.name))
        path = os.path.join(self.outdir, name)
        self.doc.save(path)
        return path
