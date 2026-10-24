# -*- coding: utf-8 -*-
"""
groupbook — category guide books, the portal suite guide book, and the
library master index.

A category guide book answers a different question from a module guide book:
not *what does this component do* but *why are these components grouped,
where do the seams between them run, and what breaks if one of them is late*.
"""

import os
import re
from collections import OrderedDict, Counter, defaultdict

from docx import Document
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH

import theme as T
import docxkit as K
import render as R
import mdparse as MD
import exhibits as X
import exhibits_group as XG
import narrative as N
from guidebook import _sanitise, _short


REVENUE_STREAMS = [
    (
        1,
        "Authorised brand warranty service",
        "M09 Warranty, Protection Plans & Claims",
        "C",
    ),
    (
        2,
        "Out-of-warranty paid repair",
        "M01 Service Request · M31 Workshop & Depot Repair",
        "A",
    ),
    (3, "AMC / RAMC maintenance contracts", "M08 Contract Lifecycle Management", "C"),
    (
        4,
        "Warranty extension & protection products",
        "M09 Warranty, Protection Plans & Claims",
        "C",
    ),
    (
        5,
        "Spare parts & accessories",
        "M15 Spare Parts & Inventory · M38 E-Commerce",
        "E",
    ),
    (6, "Corporate managed IT services", "M05 Remote Support & Managed Services", "A"),
    (
        7,
        "Equipment rental / Equipment-as-a-Service",
        "M13 Rental & Equipment-as-a-Service",
        "D",
    ),
    (8, "Data recovery", "M06 Data Services & Secure Data Handling", "A"),
    (
        9,
        "Data backup & archival subscriptions",
        "M06 Data Services · M39 Subscription",
        "A",
    ),
    (10, "Refurbished device resale", "M14 Trade-In, Refurbishment & Resale", "D"),
    (11, "Trade-in / exchange margin", "M14 Trade-In, Refurbishment & Resale", "D"),
    (
        12,
        "E-waste recycling & material recovery",
        "M18 E-Waste, Recycling & Circular Economy",
        "D",
    ),
    (
        13,
        "Marketplace commission & settlement",
        "M12 Marketplace & Seller Ecosystem",
        "C",
    ),
    (
        14,
        "Advertising, boost & lead placement",
        "M12 Marketplace · M35 Marketing & Campaigns",
        "C",
    ),
]


class GroupBookBase(object):
    """Shared shell: cover, control page, headers, footers, contents."""

    kind_label = "Guide Book"

    def __init__(self, outdir, exdir):
        self.outdir = outdir
        self.exdir = exdir
        self.exhibits = {}
        self.doc = None

    # ---------------------------------------------------------------- shell
    def _new_document(self, title, subject, keywords, comments, category_str):
        doc = Document()
        K.install_base_styles(doc)
        K.set_doc_defaults_language(doc)
        K.set_compat_and_zoom(doc)
        K.set_update_fields_on_open(doc)
        K.set_core_properties(doc, title, subject, keywords, comments, category_str)
        K.setup_section(doc.sections[0], top=0, bottom=0, left=0, right=0)
        return doc

    def _header_footer(self, sec, left_text, right_id, right_text, doc_id):
        K.unlink_header_footer(sec)
        K.clear_container(sec.header)
        t = sec.header.add_table(rows=1, cols=2, width=Mm(T.CONTENT_W_MM))
        K.no_table_borders(t)
        K.table_layout_fixed(t)
        K.table_width_pct(t, 100)
        K.table_cell_margins(t, top=0, left=0, bottom=40, right=0)
        for i, w in enumerate((0.55, 0.45)):
            t.columns[i].width = Mm(T.CONTENT_W_MM * w)
            t.rows[0].cells[i].width = Mm(T.CONTENT_W_MM * w)
            K.cell_borders(t.rows[0].cells[i], bottom=(6, T.RULE))
        p0 = t.rows[0].cells[0].paragraphs[0]
        K.pfmt(p0, before=0, after=0)
        K.run(p0, left_text, size=7.5, colour=T.GREY, spacing=8)
        p1 = t.rows[0].cells[1].paragraphs[0]
        K.pfmt(p1, before=0, after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
        K.run(p1, "%s  " % right_id, size=7.5, bold=True, colour=self.accent)
        K.run(p1, _short(right_text, 48), size=7.5, colour=T.GREY)
        hp = sec.header.add_paragraph()
        K.pfmt(hp, before=0, after=0)
        hp.paragraph_format.line_spacing = Pt(2)

        K.clear_container(sec.footer)
        f = sec.footer.add_table(rows=1, cols=3, width=Mm(T.CONTENT_W_MM))
        K.no_table_borders(f)
        K.table_layout_fixed(f)
        K.table_width_pct(f, 100)
        K.table_cell_margins(f, top=40, left=0, bottom=0, right=0)
        for i, w in enumerate((0.40, 0.28, 0.32)):
            f.columns[i].width = Mm(T.CONTENT_W_MM * w)
            f.rows[0].cells[i].width = Mm(T.CONTENT_W_MM * w)
            K.cell_borders(f.rows[0].cells[i], top=(6, T.RULE))
        a, b, c = f.rows[0].cells
        pa = a.paragraphs[0]
        K.pfmt(pa, before=0, after=0)
        K.run(pa, T.CLASSIFICATION, size=7.0, bold=True, colour=T.RED)
        pb = b.paragraphs[0]
        K.pfmt(pb, before=0, after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
        K.run(pb, "%s  ·  %s" % (doc_id, T.EDITION), size=7.0, colour=T.GREY)
        pc = c.paragraphs[0]
        K.pfmt(pc, before=0, after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
        K.run(pc, "Page ", size=7.0, colour=T.GREY)
        K.add_field(pc, " PAGE ", "1", size=7.0, bold=True, colour=T.NAVY)
        K.run(pc, " of ", size=7.0, colour=T.GREY)
        K.add_field(pc, " NUMPAGES ", "1", size=7.0, colour=T.GREY)

    def _cover(self, big, code, name, kind_line, strip_text, one_liner, facts):
        doc, acc = self.doc, self.accent
        t = doc.add_table(rows=1, cols=1)
        K.no_table_borders(t)
        K.table_width_pct(t, 100)
        K.table_cell_margins(t, top=0, left=1080, bottom=560, right=760)
        ic = t.cell(0, 0)
        K.shade(ic, T.NAVY)
        K.row_height(t.rows[0], 116, rule="atLeast")
        ic.paragraphs[0]._p.getparent().remove(ic.paragraphs[0]._p)
        R.vspace(ic, 34)

        p = ic.add_paragraph()
        K.pfmt(p, before=0, after=10)
        K.run(p, T.PROGRAMME.upper(), size=8.5, bold=True, colour="7FA8CE", spacing=56)
        p = ic.add_paragraph()
        K.pfmt(p, before=0, after=0, line=0.90)
        K.run(p, big, size=46, bold=True, colour=T.WHITE)
        if code:
            K.run(p, "   ", size=46, colour=T.WHITE)
            K.run(p, code, size=15, bold=True, colour=acc)
        p = ic.add_paragraph()
        K.pfmt(p, before=6, after=0, line=1.02)
        K.run(p, name, size=23, bold=True, colour=T.WHITE)
        p = ic.add_paragraph()
        K.pfmt(p, before=12, after=0)
        K.run(p, kind_line, size=12.5, colour="B9CEE4")
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
        K.run(ps, strip_text.upper(), size=8.5, bold=True, colour=T.WHITE, spacing=32)

        low = doc.add_table(rows=1, cols=1)
        K.no_table_borders(low)
        K.table_width_pct(low, 100)
        K.table_cell_margins(low, top=0, left=1080, bottom=300, right=760)
        lc = low.cell(0, 0)
        K.shade(lc, T.WHITE)
        lc.paragraphs[0]._p.getparent().remove(lc.paragraphs[0]._p)
        R.vspace(lc, 15)
        if one_liner:
            p = lc.add_paragraph()
            K.pfmt(p, before=0, after=16, line=1.22)
            K.run(p, one_liner, size=12.0, colour=T.INK_SOFT)
        ft = lc.add_table(rows=2, cols=3)
        K.no_table_borders(ft)
        K.table_layout_fixed(ft)
        K.table_cell_margins(ft, top=60, left=0, bottom=60, right=140)
        colw = (T.PAGE_W_MM - 38 - 27) / 3.0
        for r in range(2):
            for cc in range(3):
                cell = ft.rows[r].cells[cc]
                cell.width = Mm(colw)
                K.cell_borders(cell, top=(6, T.RULE))
                k, v = facts[r * 3 + cc]
                cell.paragraphs[0]._p.getparent().remove(cell.paragraphs[0]._p)
                p1 = cell.add_paragraph()
                K.pfmt(p1, before=0, after=1)
                K.run(p1, k.upper(), size=7.0, colour=T.GREY, spacing=20)
                p2 = cell.add_paragraph()
                K.pfmt(p2, before=0, after=0)
                K.run(p2, str(v), size=10.0, bold=True, colour=T.NAVY)
        R.vspace(lc, 26)
        R.rule_gap(lc, T.RULE, weight=6, space=0, gap_pt=2.0)
        p = lc.add_paragraph()
        K.pfmt(p, before=8, after=2)
        K.run(p, T.CLIENT, size=11.0, bold=True, colour=T.NAVY)
        p = lc.add_paragraph()
        K.pfmt(p, before=0, after=2, line=1.20)
        K.run(
            p,
            "Prepared for SPSL delivery, implementation and support teams   ·   "
            "%s   ·   Issued %s" % (T.EDITION, T.ISSUE_DATE),
            size=8.5,
            colour=T.GREY,
        )
        p = lc.add_paragraph()
        K.pfmt(p, before=6, after=0)
        K.run(p, T.CLASSIFICATION, size=8.0, bold=True, colour=T.RED, spacing=14)

    def _contents(self, exhibits=True):
        doc = self.doc
        R.h_section(doc, None, "Contents", self.accent, page_break=True)
        p = doc.add_paragraph()
        K.pfmt(p, before=0, after=8)
        K.run(
            p,
            "Press Ctrl+A then F9 in Word to build the contents and the page "
            "numbers. Fields are set to update automatically on open.",
            size=T.SIZE_SMALL,
            italic=True,
            colour=T.GREY,
        )
        tp = doc.add_paragraph()
        K.pfmt(tp, before=0, after=0)
        K.add_toc(tp, levels="1-2")
        if exhibits:
            R.h_section(doc, None, "Exhibits", self.accent, page_break=False)
            ep = doc.add_paragraph()
            K.pfmt(ep, before=4, after=0)
            K.add_table_of_figures(ep, "Exhibit")
            R.h_section(doc, None, "Tables", self.accent, page_break=False)
            tp2 = doc.add_paragraph()
            K.pfmt(tp2, before=4, after=0)
            K.add_table_of_figures(tp2, "Table")


# ============================================================ CATEGORY BOOK
class CategoryBook(GroupBookBase):
    def __init__(
        self, letter, specs, index, overview_path, outdir, exdir, findings=None
    ):
        GroupBookBase.__init__(self, outdir, exdir)
        self.findings = findings
        self.letter = letter
        self.is_portal_suite = letter == "P"
        self.specs = specs
        self.index = index
        self.accent = T.cat_colour(letter)
        self.cat_name = T.cat_name(letter)
        self.doc_id = "GB-PORTALS" if self.is_portal_suite else "GB-CAT-%s" % letter
        self.overview = None
        if overview_path and os.path.isfile(overview_path):
            with open(overview_path, "r", encoding="utf-8") as fh:
                raw = fh.read()
            fm, bodytext = MD.parse_frontmatter(raw)
            self.overview_fm = fm
            self.overview = MD.parse_blocks(bodytext)
        self.exdir = os.path.join(exdir, "_" + self.doc_id)
        self.items = [
            {
                "uid": s.uid,
                "name": s.name,
                "code": s.code,
                "reqs": s.req_count,
                "effort": s.effort_pw,
                "rules": len(s.rules),
                "entities": len(s.owned_entities),
                "events": len(s.events),
                "automations": len(s.automations),
                "roles": len(s.roles),
                "kpis": len(s.kpis),
                "wave": s.wave,
                "priority": s.priority,
                "depends_on": s.depends_on,
                "one_liner": s.one_liner(),
                "business_owner": s.business_owner,
                "system_owner": s.system_owner,
                "areas": list(s.areas.keys()),
                "questions": len(s.questions),
                "acceptance": len(s.acceptance),
                "layer_alloc": s.layer_alloc,
                "in_scope": len(s.in_scope),
                "out_scope": len(s.out_scope),
                "api": len(s.api),
                "externals": len(s.externals),
            }
            for s in specs
        ]

    # ------------------------------------------------------------ aggregates
    def totals(self):
        it = self.items
        agg = OrderedDict(
            [
                ("Components", len(it)),
                ("Requirements", sum(d["reqs"] for d in it)),
                ("Build effort · PW", int(round(sum(d["effort"] or 0 for d in it)))),
                ("Business rules", sum(d["rules"] for d in it)),
                ("Owned entities", sum(d["entities"] for d in it)),
                ("Domain events", sum(d["events"] for d in it)),
                ("Automations", sum(d["automations"] for d in it)),
                ("API endpoints", sum(d["api"] for d in it)),
                ("External links", sum(d["externals"] for d in it)),
                ("KPIs", sum(d["kpis"] for d in it)),
                ("Acceptance criteria", sum(d["acceptance"] for d in it)),
                ("Open questions", sum(d["questions"] for d in it)),
            ]
        )
        return agg

    def layer_mix(self):
        acc = defaultdict(float)
        for s in self.specs:
            w = float(s.req_count) or 1.0
            for L, v in s.layer_alloc.items():
                acc[L] += (v.get("pct") or 0.0) * w
        tot = sum(acc.values()) or 1.0
        return OrderedDict(
            (L, 100.0 * acc[L] / tot)
            for L in ["L1", "L2", "L3", "L4", "L5", "L6"]
            if acc.get(L)
        )

    def priority_mix(self):
        c = Counter()
        for s in self.specs:
            c.update(s.pri_mix)
        return c

    def rule_mix(self):
        c = Counter()
        for s in self.specs:
            c.update(s.rule_mix)
        return c

    def external_reach(self):
        c = Counter()
        own = {d["uid"] for d in self.items}
        for s in self.specs:
            for uid in set(s.depends_on + s.iface_up + s.iface_down + s.depended_by):
                if uid in own:
                    continue
                meta = self.index.get(uid)
                if meta:
                    c[meta["category"]] += 1
        return c

    # ------------------------------------------------------------- exhibits
    def build_exhibits(self):
        os.makedirs(self.exdir, exist_ok=True)
        p = lambda n: os.path.join(self.exdir, "%s_%s.png" % (self.doc_id, n))
        E, acc = self.exhibits, self.accent
        label = "portal suite" if self.is_portal_suite else "category"

        E["totals"] = X.scorecard(
            p("totals"),
            self.totals(),
            acc,
            (
                "The portal suite measured"
                if self.is_portal_suite
                else "Category %s measured" % self.letter
            ),
            "Counted from the %d specification%s in this %s, not restated from "
            "a register"
            % (len(self.items), "" if len(self.items) == 1 else "s", label),
        )

        E["scale"] = XG.cat_scale(
            p("scale"),
            self.items,
            acc,
            "Relative scale of each component",
            "%d components" % len(self.items),
        )

        E["composition"] = XG.cat_composition(
            p("composition"),
            self.items,
            acc,
            "What each component actually contains",
            "Rules, owned entities, domain events and automations",
        )

        E["waves"] = XG.cat_wave_map(
            p("waves"), self.items, acc, "Delivery map — when each component lands", ""
        )

        E["matrix"] = XG.cat_dependency_matrix(
            p("matrix"),
            self.items,
            acc,
            "Internal dependencies",
            "A filled cell means the row depends on the column",
        )

        E["reach"] = XG.cat_external_reach(
            p("reach"),
            self.external_reach(),
            acc,
            "How far this %s reaches outside itself" % label,
            "Declared links to components in other categories",
        )

        pm = self.priority_mix()
        E["priority"] = X.priority_mix(
            p("priority"),
            pm,
            max(sum(pm.values()), 1),
            "Requirement priority across the %s" % label,
            "How much of this %s is negotiable" % label,
        )

        lm = self.layer_mix()
        E["layers"] = XG.stack_bar(
            p("layers"),
            list(lm.keys()),
            list(lm.values()),
            "Where the build comes from",
            "Requirement-weighted delivery layer mix across the %s" % label,
            colours=[T.LAYER_COLOUR[k] for k in lm.keys()],
            value_fmt="%.0f%%",
        )

        rm = self.rule_mix()
        E["rules"] = X.rule_classes(
            p("rules"),
            rm,
            max(sum(rm.values()), 1),
            "Rule enforcement across the %s" % label,
            "%d rules in total" % sum(rm.values()),
        )
        return self

    # ---------------------------------------------------------------- build
    def build(self):
        self.build_exhibits()
        title = (
            "Portal & Application Suite"
            if self.is_portal_suite
            else "Category %s — %s" % (self.letter, self.cat_name)
        )
        self.doc = self._new_document(
            title="%s Guide Book" % title,
            subject="%s · %s" % (T.PROGRAMME, title),
            keywords="1000FiX, ERP, category %s, %s, guide book, SPSL"
            % (self.letter, self.cat_name),
            comments="Category guide book %s, %s." % (self.doc_id, T.EDITION),
            category_str=title,
        )

        self._cover(
            big=("PORTALS" if self.is_portal_suite else "CATEGORY %s" % self.letter),
            code="",
            name=(
                "Portal & Application Suite" if self.is_portal_suite else self.cat_name
            ),
            kind_line=(
                "Suite Guide Book" if self.is_portal_suite else "Category Guide Book"
            ),
            strip_text=(
                "%d PORTALS AND APPLICATIONS  ·  P01 – P12" % len(self.items)
                if self.is_portal_suite
                else "%d MODULES  ·  %s"
                % (len(self.items), "  ·  ".join(d["uid"] for d in self.items))
            ),
            one_liner=self._cover_line(),
            facts=[
                ("Components", len(self.items)),
                ("Requirements", sum(d["reqs"] for d in self.items)),
                (
                    "Build effort",
                    "%d person-weeks"
                    % int(round(sum(d["effort"] or 0 for d in self.items))),
                ),
                ("Waves", self._wave_span()),
                ("Business rules", sum(d["rules"] for d in self.items)),
                ("Owned entities", sum(d["entities"] for d in self.items)),
            ],
        )

        sec = self.doc.add_section()
        K.setup_section(sec)
        K.restart_page_numbering(sec, 1)
        self._header_footer(
            sec,
            "%s  ·  %s" % (T.PROGRAMME, T.LIBRARY),
            ("PORTALS" if self.is_portal_suite else "CATEGORY %s" % self.letter),
            ("Portal & Application Suite" if self.is_portal_suite else self.cat_name),
            self.doc_id,
        )

        self._control()
        self._orientation()
        self._contents()
        self._at_a_glance()
        self._as_designed()
        self._components()
        self._working_together()
        self._delivery()
        self._annexes()

        fname = (
            "PORTALS_Portal_and_Application_Suite_Guide_Book.docx"
            if self.is_portal_suite
            else "CAT-%s_%s_Category_Guide_Book.docx"
            % (self.letter, _sanitise(self.cat_name.replace("&", "and")))
        )
        if not os.path.isdir(self.outdir):
            os.makedirs(self.outdir, exist_ok=True)
        path = os.path.join(self.outdir, fname)
        self.doc.save(path)
        return path

    # ------------------------------------------------------------- sections
    def _cover_line(self):
        if self.is_portal_suite:
            return (
                "Twelve surfaces onto one system of record. The ERP holds the "
                "truth; these portals and applications are how twelve different "
                "populations reach it."
            )
        return (
            "The %d modules of Category %s, why they are grouped, where the "
            "seams between them run, and what happens if one of them is late."
            % (len(self.items), self.letter)
        )

    def _wave_span(self):
        ws = sorted(
            {w for d in self.items for w in re.findall(r"W\d", d.get("wave") or "")}
        )
        return "%s – %s" % (ws[0], ws[-1]) if ws else "—"

    def _control(self):
        doc = self.doc
        label = "portal suite" if self.is_portal_suite else "category"
        R.h_section(
            doc, None, "Document control", self.accent, kicker="About this guide book"
        )
        R.body(
            doc,
            "This is the %s-level guide book. It sits above the individual "
            "component guide books and answers the questions none of them can "
            "answer on their own: why these components are grouped together, "
            "where the boundary between each pair of them runs, what they share, "
            "and what the %s as a whole costs and delivers." % (label, label),
        )
        R.definition_rows(
            doc,
            [
                (
                    "Guide book",
                    "%s — %s"
                    % (
                        self.doc_id,
                        "Portal & Application Suite Guide Book"
                        if self.is_portal_suite
                        else "Category %s Guide Book" % self.letter,
                    ),
                ),
                ("Scope", ", ".join(d["uid"] for d in self.items)),
                ("Programme", "%s · %s" % (T.PROGRAMME, T.CLIENT)),
                ("Edition", "%s, issued %s" % (T.EDITION, T.ISSUE_DATE)),
                (
                    "Audience",
                    "SPSL delivery, implementation, quality, support and "
                    "training teams; 1000FiX business and process owners",
                ),
                ("Classification", T.CLASSIFICATION),
                ("Document owner", "SPSL ERP Programme Documentation Office"),
                (
                    "Source",
                    "The %d component specifications listed above%s"
                    % (
                        len(self.items),
                        ", and the category overview `_CATEGORY_OVERVIEW.md`"
                        if self.overview
                        else "",
                    ),
                ),
                (
                    "Counting rule applied",
                    "Register rule **RG-06** — *count, do not consult*. Every quantity was "
                    "counted from the source specifications at the time of generation.",
                ),
            ],
            accent=self.accent,
        )
        R.h_sub(doc, "Component guide books in this %s" % label, self.accent)
        R.table(
            doc,
            ["Guide book", "Component", "Priority", "Wave", "Reqs"],
            [
                [
                    "GB-%s" % d["uid"],
                    d["name"],
                    d["priority"],
                    d["wave"] or "—",
                    str(d["reqs"]),
                ]
                for d in self.items
            ],
            align=["left", "left", "center", "center", "right"],
            accent=self.accent,
            caption="The component guide books this document sits above",
        )

    def _orientation(self):
        doc = self.doc
        label = "portal suite" if self.is_portal_suite else "category"
        R.h_section(
            doc,
            None,
            "How to use this guide book",
            self.accent,
            page_break=True,
            kicker="Orientation",
        )
        R.body(
            doc,
            "Read this %s guide book before you read any of the component guide "
            "books beneath it, and read it again whenever you are asked to move a "
            "capability from one component to another. Most of the expensive "
            "mistakes in an ERP programme are boundary mistakes, and boundaries "
            "are what this document is about." % label,
        )
        R.table(
            doc,
            ["If you are…", "Read", "Because"],
            [
                [
                    "New to the programme",
                    "Part One and Part Two",
                    "You need the shape of the %s before the detail of any one "
                    "component." % label,
                ],
                [
                    "Scoping or estimating",
                    "Part Two and Part Four",
                    "Scale, effort and the delivery sequence are here; the component "
                    "guide books have the line detail.",
                ],
                [
                    "Designing an interface",
                    "Part Three",
                    "Internal dependencies and the shared concepts sit in Part Three.",
                ],
                [
                    "Arguing about ownership",
                    "Part Three and the component §3",
                    "Boundary symmetry is a governed rule; both sides must agree.",
                ],
                [
                    "Planning a wave",
                    "Part Four",
                    "Sequencing, prerequisites and the wave load are here.",
                ],
                [
                    "Looking for one fact fast",
                    "The annexes",
                    "Component index, requirement index, the assurance register and the glossary.",
                ],
            ],
            accent=self.accent,
            first_col_bold=True,
        )
        R.table(
            doc,
            ["Kind", "Code", "Meaning"],
            [[a, b, c] for a, b, c in N.CONVENTIONS],
            accent=self.accent,
            caption="Programme conventions used throughout the library",
        )

    def _at_a_glance(self):
        doc = self.doc
        label = "portal suite" if self.is_portal_suite else "category"
        title = (
            "The portal suite in one page"
            if self.is_portal_suite
            else "Category %s in one page" % self.letter
        )
        R.h_section(
            doc,
            None,
            title,
            self.accent,
            page_break=True,
            kicker="Executive orientation",
        )
        R.pull_quote(doc, self._cover_line(), self.accent)
        R.exhibit(
            doc,
            self.exhibits.get("totals"),
            "Everything in this %s, counted" % label,
            accent=self.accent,
        )

        R.h_sub(doc, "The components", self.accent)
        R.table(
            doc,
            ["ID", "Component", "In one sentence", "Pri", "Wave"],
            [
                [
                    d["uid"],
                    d["name"],
                    _short(d["one_liner"], 150),
                    d["priority"],
                    d["wave"] or "—",
                ]
                for d in self.items
            ],
            align=["left", "left", "left", "center", "center"],
            accent=self.accent,
            caption="The components of this %s and what each is for" % label,
        )

        R.exhibit(
            doc,
            self.exhibits.get("scale"),
            "Relative scale — requirements and build effort side by side",
            accent=self.accent,
        )

    def _as_designed(self):
        doc = self.doc
        label, name, blurb = N.PARTS[1]
        R.part_opener(
            doc,
            "Part One",
            "The %s as designed" % ("suite" if self.is_portal_suite else "category"),
            "What belongs here and what does not, taken from the "
            "programme's own category overview.",
            self.accent,
        )
        if self.overview:
            R.render_blocks(doc, self.overview, accent=self.accent, table_max_rows=None)
        else:
            R.body(
                doc,
                "No category overview document exists for this grouping. "
                "The narrative below is derived from the component "
                "specifications alone.",
            )
        R.exhibit(
            doc,
            self.exhibits.get("priority"),
            "Requirement priority across the whole grouping",
            accent=self.accent,
        )

    def _components(self):
        doc = self.doc
        R.part_opener(
            doc,
            "Part Two",
            "The components, one by one",
            "A profile of every component in this grouping: what it is "
            "for, what it owns, what it depends on and what it is "
            "measured by. The full treatment is in each component's own "
            "guide book.",
            self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("composition"),
            "What each component actually contains",
            accent=self.accent,
        )

        for d, s in zip(self.items, self.specs):
            R.h_section(
                doc,
                d["uid"],
                d["name"],
                self.accent,
                page_break=True,
                kicker="Component profile",
            )
            R.kpi_strip(
                doc,
                [
                    (d["priority"], "priority"),
                    (d["wave"] or "—", "wave"),
                    (d["reqs"], "requirements"),
                    (int(d["effort"] or 0), "person-weeks"),
                    (d["rules"], "rules"),
                ],
                accent=self.accent,
            )
            if d["one_liner"]:
                R.body(doc, _short(d["one_liner"], 500))
            pairs = [
                ("Code", "`%s`" % (d["code"] or "—")),
                ("Business owner", d["business_owner"] or "—"),
                ("System owner", d["system_owner"] or "—"),
                ("Functional areas", " · ".join(d["areas"][:10]) or "—"),
                (
                    "Owns",
                    ", ".join("`%s`" % e for e in N._entity_names(s.owned_entities)[:8])
                    or "No entity — this component owns no data of its own",
                ),
                ("Depends on", ", ".join(d["depends_on"]) or "—"),
                ("Depended on by", ", ".join(s.depended_by[:18]) or "—"),
                ("Guide book", "`GB-%s`" % d["uid"]),
            ]
            R.definition_rows(doc, pairs, accent=self.accent, label_mm=44)

            if s.in_scope:
                R.h_sub(doc, "What it does", self.accent)
                R.table(
                    doc,
                    s.in_header or ["#", "Capability"],
                    s.in_scope,
                    accent=self.accent,
                    max_rows=24,
                    compact=True,
                )
            if s.out_scope:
                R.h_sub(doc, "What it deliberately does not do", self.accent)
                R.table(
                    doc,
                    s.out_header or ["Capability", "Owned by", "Why"],
                    s.out_scope,
                    accent=self.accent,
                    max_rows=18,
                    compact=True,
                )
            hard = [r for r in s.rules if r["class"] == "H"][:8]
            if hard:
                R.h_sub(doc, "The rules that block outright", self.accent)
                R.table(
                    doc,
                    ["ID", "Rule", "Owner"],
                    [[r["id"], r["rule"], r["owner"]] for r in hard],
                    accent=self.accent,
                    compact=True,
                )

    def _working_together(self):
        doc = self.doc
        R.part_opener(
            doc,
            "Part Three",
            "How they work together",
            "The seams. Internal dependencies, shared concepts, and "
            "everything this grouping reaches for outside itself.",
            self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("matrix"),
            "Internal dependency matrix",
            accent=self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("reach"),
            "Reach outside the grouping, by category",
            accent=self.accent,
        )

        R.h_section(doc, None, "The boundary register", self.accent, page_break=True)
        R.body(
            doc,
            "Every capability a component in this grouping declares out of scope, "
            "and the component that owns it instead. Boundary symmetry is a "
            "governed rule: the owning component must claim what is disclaimed "
            "here. Where it does not, that is a defect worth raising.",
        )
        rows = []
        for d, s in zip(self.items, self.specs):
            for r in s.out_scope:
                owner = MD.plain(r[1]) if len(r) > 1 else ""
                why = MD.plain(r[2]) if len(r) > 2 else ""
                rows.append([d["uid"], MD.plain(r[0]), owner, why])
        if rows:
            R.table(
                doc,
                [
                    "Component",
                    "Capability it does not own",
                    "Owned by",
                    "Why the boundary sits there",
                ],
                rows,
                accent=self.accent,
                compact=True,
                caption="Boundary register — %d declared boundaries" % len(rows),
            )

        R.h_section(doc, None, "Shared concepts", self.accent, page_break=True)
        srows = []
        for d, s in zip(self.items, self.specs):
            for r in s.shared:
                srows.append([d["uid"]] + [MD.plain(c) for c in r[:3]])
        if srows:
            R.table(
                doc,
                ["Component", "Concept", "Its role", "Owned by"],
                srows,
                accent=self.accent,
                compact=True,
                caption="Concepts shared with other components",
            )
        else:
            R.body(doc, "No shared concepts are declared in this grouping.")

    def _delivery(self):
        doc = self.doc
        R.part_opener(
            doc,
            "Part Four",
            "Building it",
            "The delivery sequence, the layer split that drives cost, and "
            "what has to be true before each component can start.",
            self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("waves"),
            "When each component lands",
            accent=self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("layers"),
            "Where the build comes from — the cost model",
            accent=self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("rules"),
            "Rule enforcement profile across the grouping",
            accent=self.accent,
        )

        R.h_section(
            doc, None, "Prerequisites and sequencing", self.accent, page_break=True
        )
        rows = []
        for d, s in zip(self.items, self.specs):
            for r in s.sequencing:
                rows.append(
                    [d["uid"], MD.plain(r[0]), MD.plain(r[1]) if len(r) > 1 else ""]
                )
        if rows:
            R.table(
                doc,
                ["Component", "Prerequisite", "Why"],
                rows,
                accent=self.accent,
                compact=True,
                caption="Every declared prerequisite in this grouping",
            )
        R.callout(
            doc,
            "**Wave check.** No prerequisite may land in a later wave than the "
            "component that needs it. Where the table above shows one that "
            "does, either the dependency is not a true prerequisite, an interim "
            "capability covers the gap, or a wave assignment is wrong — and the "
            "programme has to say which before the wave gate.",
            kind="warning",
            accent=T.GOLD,
        )

        R.h_section(
            doc,
            None,
            "Open questions across the grouping",
            self.accent,
            page_break=True,
        )
        qrows = []
        for d, s in zip(self.items, self.specs):
            for r in s.questions:
                qrows.append([d["uid"]] + [MD.plain(c) for c in r[:4]])
        if qrows:
            hdr = ["Component"] + [
                MD.plain(h)
                for h in (
                    self.specs[0].questions_header
                    or ["#", "Question", "Owner", "Needed by"]
                )
            ][:4]
            R.table(
                doc,
                hdr,
                qrows,
                accent=self.accent,
                compact=True,
                caption="%d open questions across %d components"
                % (len(qrows), len(self.items)),
            )
        else:
            R.body(doc, "No open questions are recorded.")

    def _annexes(self):
        doc = self.doc
        R.part_opener(
            doc,
            "Annexes",
            "Reference material",
            "Indexes and registers derived by measurement from the "
            "component specifications.",
            self.accent,
        )

        R.h_section(
            doc,
            "Annex A",
            "Component index",
            self.accent,
            page_break=True,
            kicker="Reference",
        )
        R.table(
            doc,
            ["ID", "Component", "Code", "Owner", "Pri", "Wave", "Reqs", "Rules", "PW"],
            [
                [
                    d["uid"],
                    d["name"],
                    d["code"],
                    d["business_owner"],
                    d["priority"],
                    d["wave"] or "—",
                    str(d["reqs"]),
                    str(d["rules"]),
                    str(int(d["effort"] or 0)),
                ]
                for d in self.items
            ],
            align=[
                "left",
                "left",
                "left",
                "left",
                "center",
                "center",
                "right",
                "right",
                "right",
            ],
            accent=self.accent,
            compact=True,
            caption="Every component in this grouping, measured",
        )

        R.h_section(
            doc,
            "Annex B",
            "Requirement index",
            self.accent,
            page_break=True,
            kicker="Reference",
        )
        R.body(
            doc,
            "Every requirement in the grouping, in component and " "identifier order.",
        )
        rows = []
        for s in self.specs:
            for r in sorted(s.reqs, key=lambda x: x["id"]):
                rows.append(
                    [
                        s.uid,
                        r["id"],
                        r["feature"] or r["function"][:60],
                        r["pri"],
                        r["layer"],
                    ]
                )
        R.table(
            doc,
            ["Component", "FR ID", "Feature", "Pri", "Layer"],
            rows,
            align=["left", "left", "left", "center", "center"],
            accent=self.accent,
            compact=True,
            caption="%d requirements across %d components"
            % (len(rows), len(self.items)),
        )

        R.h_section(
            doc,
            "Annex C",
            "Assurance and known defects",
            self.accent,
            page_break=True,
            kicker="Governance",
        )
        R.body(
            doc,
            "Ten mechanical integrity checks were run across the source "
            "specifications while this edition was generated. The findings that "
            "affect this grouping are consolidated below; each is repeated in "
            "the affected component's own guide book at Annex E, with the "
            "action to take. These are defects in the source specifications and "
            "their registers, not in the guide books.",
        )
        f = self.findings
        if f is None:
            R.body(doc, "No findings analysis was supplied for this edition.")
        else:
            rows = []
            for d in self.items:
                for x in f.for_uid(d["uid"]):
                    rows.append(
                        [
                            d["uid"],
                            x["code"],
                            x["severity"],
                            "**%s.** %s" % (x["title"], x["detail"]),
                        ]
                    )
            if rows:
                sev = Counter(r[2] for r in rows)
                R.kpi_strip(
                    doc,
                    [
                        (len(rows), "findings"),
                        (sev.get("High", 0), "high"),
                        (sev.get("Medium", 0), "medium"),
                        (sev.get("Low", 0), "low"),
                        (len({r[0] for r in rows}), "components affected"),
                    ],
                    accent=self.accent,
                )
                R.table(
                    doc,
                    ["Component", "Ref", "Severity", "Finding"],
                    rows,
                    align=["left", "left", "center", "left"],
                    accent=self.accent,
                    compact=True,
                    first_col_bold=True,
                    caption="Integrity findings across this grouping",
                )
                if sev.get("High"):
                    R.callout(
                        doc,
                        "**%d high-severity finding%s in this grouping.** "
                        "Each one means a specific line of a specific "
                        "specification cannot be built as written without a "
                        "decision first. Resolve them before the wave gate."
                        % (sev["High"], "" if sev["High"] == 1 else "s"),
                        kind="risk",
                        accent=T.RED,
                        title="ACT BEFORE BUILD",
                    )
            else:
                R.callout(
                    doc,
                    "No integrity defect was found in the source "
                    "specifications for this grouping.",
                    kind="good",
                    accent=T.GREEN,
                    title="CLEAN",
                )

        R.h_section(
            doc, "Annex D", "Glossary", self.accent, page_break=True, kicker="Reference"
        )
        R.table(
            doc,
            ["Term", "Meaning"],
            [[a, b] for a, b in N.HOUSE_GLOSSARY],
            accent=self.accent,
        )
