# -*- coding: utf-8 -*-
"""
guidebook — assembles one module or portal guide book as a Word document.

Document architecture
    Cover · Document control · How to use this guide book · Contents ·
    Exhibits · The component in one page ·
    Part 1 Orientation           §1–§4
    Part 2 What it does          §5–§7
    Part 3 How it behaves        §8–§11
    Part 4 How it connects       §12–§13
    Part 5 Measured and delivered §14–§19
    Annex A Requirement index · Annex B Relationship register ·
    Annex C Glossary · Annex D Quick reference card ·
    Annex E Assurance and known defects · Annex F Change control
"""

import os
import re
from collections import Counter

from docx import Document
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH

import theme as T
import docxkit as K
import render as R
import mdparse as MD
import exhibits as X
import narrative as N
from findings import PASSED_CHECKS as FINDINGS_PASSED


# ------------------------------------------------------------------ helpers
def _sanitise(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def _short(text, n=200):
    t = re.sub(r"\s+", " ", MD.plain(text)).strip()
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


# ================================================================== the build
class GuideBook(object):
    def __init__(
        self,
        sp,
        catalogue,
        peers,
        exdir,
        outdir,
        doc_no=None,
        total_docs=None,
        findings=None,
    ):
        self.sp = sp
        self.cat = catalogue
        self.peers = peers
        self.exdir = os.path.join(exdir, sp.uid)
        self.outdir = outdir
        self.doc_no = doc_no
        self.total_docs = total_docs
        self.accent = T.cat_colour(sp.category)
        self.pale = T.cat_pale(sp.category)
        self.kind = "Portal" if sp.is_portal else "Module"
        self.doc_id = "GB-%s" % sp.uid
        self.title = "%s — %s" % (sp.uid, sp.name)
        self.exhibits = {}
        self.findings = findings or []
        self.doc = None

    # ------------------------------------------------------------- exhibits
    def build_exhibits(self):
        sp, acc = self.sp, self.accent
        d = self.exdir
        os.makedirs(d, exist_ok=True)
        p = lambda n: os.path.join(d, "%s_%s.png" % (sp.uid, n))
        E = self.exhibits

        E["scorecard"] = X.scorecard(
            p("scorecard"),
            sp.scorecard(),
            acc,
            "%s %s — the specification measured" % (self.kind, sp.uid),
            "Every figure counted from the source specification on issue, not restated "
            "from a register",
        )

        E["wave"] = X.wave_position(
            p("wave"),
            sp.waves,
            acc,
            "Where %s sits in the 36-month programme" % sp.uid,
            "Delivery wave %s · priority %s" % (sp.wave or "unassigned", sp.priority),
        )

        E["boundary"] = X.boundary_map(
            p("boundary"),
            len(sp.in_scope),
            sp.out_scope,
            sp.shared,
            acc,
            "Scope boundary at a glance",
            "What %s owns, what it deliberately leaves to others" % sp.uid,
        )

        E["areas"] = X.req_by_area(
            p("areas"),
            sp.area_mix,
            acc,
            "Requirements by %s area"
            % ("capability" if sp.is_portal else "functional"),
            "%d requirements across %d areas" % (sp.req_count, len(sp.areas)),
        )

        E["priority"] = X.priority_mix(
            p("priority"),
            sp.pri_mix,
            max(sp.req_count, 1),
            "Requirement priority mix",
            "How much of %s is negotiable under schedule pressure" % sp.uid,
        )

        # Three renderings, tried in order of fidelity: an arrow-parsed graph,
        # the principal path through a box diagram, then a plain inventory.
        E["state"] = X.state_flow(
            p("state"),
            sp.state_models,
            acc,
            "Lifecycle state model",
            "simplified rendering; the authoritative diagram follows",
        )
        E["state_caption"] = "Simplified from the state machine in §8."
        if not E["state"]:
            E["state"] = X.state_chain(
                p("state_chain"),
                sp.state_models,
                acc,
                "The principal path through the lifecycle",
                "main sequence only; branches and exceptions are in the diagram below",
            )
            E["state_caption"] = (
                "Principal path only. Side branches, reopen paths "
                "and terminal exceptions are shown in the "
                "authoritative diagram that follows."
            )
        if not E["state"]:
            E["state"] = X.state_inventory(
                p("states"),
                sp.state_models,
                acc,
                "States declared in the lifecycle model",
                "shown without transitions; the authoritative diagram follows",
            )
            E["state_caption"] = (
                "States only — the transitions are shown in the "
                "authoritative diagram that follows."
            )

        E["rules"] = X.rule_classes(
            p("rules"),
            sp.rule_mix,
            max(len(sp.rules), 1),
            "How the rules behave when they are broken",
            "%d rules classified by enforcement" % len(sp.rules),
        )

        E["data"] = X.data_ownership(
            p("data"),
            sp.owned_entities,
            sp.ref_entities,
            acc,
            "Data ownership and data reach",
            "One entity, one owner — everything else is read through an interface",
            owned_label=(
                "Entities this portal owns"
                if sp.is_portal
                else "Entities this module owns"
            ),
        )

        E["automation"] = X.automation_profile(
            p("automation"),
            sp.automations,
            sp.automation_header,
            acc,
            "What happens when an automation fails",
            "Declared failure behaviour across %d automations" % len(sp.automations),
        )

        E["interfaces"] = X.integration_surface(
            p("interfaces"),
            sp.uid,
            sp.upstream,
            sp.downstream,
            sp.events,
            sp.externals,
            acc,
            "Integration surface",
            "Everything %s reads, and everything that depends on it" % sp.uid,
            up_label="Modules it consumes" if sp.is_portal else "Consumes from",
            down_label="Writes back to" if sp.is_portal else "Provides to",
        )

        E["roles"] = X.role_matrix(
            p("roles"), sp.roles, acc, "Who can do what", "Role and permission matrix"
        )

        E["kpi"] = X.kpi_board(
            p("kpi"),
            sp.kpis,
            sp.kpis_header,
            acc,
            "From today's baseline to the wave target",
            "Only indicators with a measured baseline are plotted",
        )

        E["layers"] = X.layer_allocation(
            p("layers"),
            sp.layer_alloc,
            "Delivery layer allocation",
            "The cost model: standard product versus custom build",
        )

        E["peers"] = X.peer_comparison(
            p("peers"),
            self.peers,
            sp.uid,
            acc,
            "%s against the rest of Category %s" % (sp.uid, sp.category),
            "Functional requirement count, measured",
        )
        return self

    # ---------------------------------------------------------------- shell
    def _new_document(self):
        doc = Document()
        K.install_base_styles(doc)
        K.set_doc_defaults_language(doc)
        K.set_compat_and_zoom(doc)
        K.set_update_fields_on_open(doc)
        K.set_core_properties(
            doc,
            title="%s Guide Book — %s" % (self.kind, self.title),
            subject="%s · %s · Category %s — %s"
            % (T.PROGRAMME, self.kind, self.sp.category, T.cat_name(self.sp.category)),
            keywords="1000FiX, ERP, %s, %s, %s, guide book, SPSL, Odoo 19, "
            "after-sales service, Bangladesh"
            % (self.sp.uid, self.sp.code, self.sp.name),
            comments="Guide book %s, %s. Generated from specification %s "
            "(version %s, %s). CONFIDENTIAL — internal use only."
            % (self.doc_id, T.EDITION, self.sp.filename, self.sp.version, self.sp.date),
            category_str="Category %s — %s"
            % (self.sp.category, T.cat_name(self.sp.category)),
        )
        sec = doc.sections[0]
        K.setup_section(sec, top=0, bottom=0, left=0, right=0)
        return doc

    def _header_footer(self, sec):
        K.unlink_header_footer(sec)
        # ---- header
        K.clear_container(sec.header)
        t = sec.header.add_table(rows=1, cols=2, width=Mm(T.CONTENT_W_MM))
        K.no_table_borders(t)
        K.table_layout_fixed(t)
        K.table_width_pct(t, 100)
        K.table_cell_margins(t, top=0, left=0, bottom=40, right=0)
        t.columns[0].width = Mm(T.CONTENT_W_MM * 0.55)
        t.columns[1].width = Mm(T.CONTENT_W_MM * 0.45)
        c0, c1 = t.rows[0].cells
        c0.width = Mm(T.CONTENT_W_MM * 0.55)
        c1.width = Mm(T.CONTENT_W_MM * 0.45)
        p0 = c0.paragraphs[0]
        K.pfmt(p0, before=0, after=0)
        K.run(
            p0,
            "%s  ·  %s" % (T.PROGRAMME, T.LIBRARY),
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

        # ---- footer
        K.clear_container(sec.footer)
        f = sec.footer.add_table(rows=1, cols=3, width=Mm(T.CONTENT_W_MM))
        K.no_table_borders(f)
        K.table_layout_fixed(f)
        K.table_width_pct(f, 100)
        K.table_cell_margins(f, top=40, left=0, bottom=0, right=0)
        widths = (0.40, 0.28, 0.32)
        for i, w in enumerate(widths):
            f.columns[i].width = Mm(T.CONTENT_W_MM * w)
            f.rows[0].cells[i].width = Mm(T.CONTENT_W_MM * w)
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

    # ---------------------------------------------------------------- cover
    def cover(self):
        doc, sp, acc = self.doc, self.sp, self.accent

        # ---------- upper colour field
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
        K.run(p, sp.uid, size=52, bold=True, colour=T.WHITE)
        K.run(p, "   ", size=52, colour=T.WHITE)
        K.run(p, sp.code or "", size=15, bold=True, colour=acc)

        p = ic.add_paragraph()
        K.pfmt(p, before=6, after=0, line=1.02)
        K.run(p, sp.name, size=23, bold=True, colour=T.WHITE)

        p = ic.add_paragraph()
        K.pfmt(p, before=12, after=0)
        K.run(p, "%s Guide Book" % self.kind, size=12.5, colour="B9CEE4")

        R.vspace(ic, 4)
        R.rule_gap(ic, acc, weight=10, space=8, gap_pt=2.0)

        # ---------- category strip
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

        # ---------- lower field
        low = doc.add_table(rows=1, cols=1)
        K.no_table_borders(low)
        K.table_width_pct(low, 100)
        K.table_cell_margins(low, top=0, left=1080, bottom=300, right=760)
        lc = low.cell(0, 0)
        K.shade(lc, T.WHITE)
        lc.paragraphs[0]._p.getparent().remove(lc.paragraphs[0]._p)
        R.vspace(lc, 15)

        one = sp.one_liner()
        if one:
            p = lc.add_paragraph()
            K.pfmt(p, before=0, after=16, line=1.22)
            K.run(p, _short(one, 300), size=12.0, colour=T.INK_SOFT)

        facts = [
            ("Priority", sp.priority),
            ("Delivery wave", sp.wave or "—"),
            ("Requirements", str(sp.req_count)),
            ("Business owner", sp.business_owner or "—"),
            ("System owner", sp.system_owner or "—"),
            ("Effort estimate", sp.effort_txt or "—"),
        ]
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
        return self

    # ------------------------------------------------------- document control
    def document_control(self):
        doc, sp = self.doc, self.sp
        R.h_section(
            doc, None, "Document control", self.accent, kicker="About this guide book"
        )

        R.body(
            doc,
            "This guide book is the working reference for **%s %s — %s**. It is written "
            "for SPSL delivery, implementation and support staff, and it is intended to be "
            "used, annotated and argued with rather than filed. It restates the approved "
            "specification in full, adds the orientation material a reader needs to use it, "
            "and presents the measured shape of the %s as a set of exhibits."
            % (self.kind.lower(), sp.uid, sp.name, self.kind.lower()),
        )

        R.h_sub(doc, "Identity", self.accent)
        R.definition_rows(
            doc,
            [
                ("Guide book", "%s — %s Guide Book" % (self.doc_id, self.kind)),
                ("Title", self.title),
                (
                    "Component",
                    "%s %s · code `%s`" % (self.kind, sp.uid, sp.code or "—"),
                ),
                (
                    "Category",
                    "Category %s — %s" % (sp.category, T.cat_name(sp.category)),
                ),
                ("Programme", "%s · %s" % (T.PROGRAMME, T.CLIENT)),
                ("Edition", "%s, issued %s" % (T.EDITION, T.ISSUE_DATE)),
                (
                    "Audience",
                    "SPSL delivery, implementation, quality, support and training teams; "
                    "1000FiX business owners and process owners",
                ),
                ("Classification", T.CLASSIFICATION),
                ("Document owner", "SPSL ERP Programme Documentation Office"),
                ("Business owner of the component", sp.business_owner or "—"),
                ("System owner of the component", sp.system_owner or "—"),
                (
                    "Review cycle",
                    "At each wave gate, and on any change to the source specification",
                ),
            ],
            accent=self.accent,
        )

        R.h_sub(doc, "Source and provenance", self.accent)
        R.body(
            doc,
            "Nothing in Parts One to Five originates in this guide book. Every requirement, "
            "rule, entity, interface, role, indicator and delivery figure is taken from the "
            "approved specification named below. Where this guide book adds material — "
            "orientation, reading paths, exhibits, annexes — it is derived from that same "
            "source by measurement, and is marked as such.",
        )
        R.definition_rows(
            doc,
            [
                ("Source specification", "`%s`" % sp.filename),
                (
                    "Repository path",
                    "`1000fix_ERP_Module/03_Modules/%s_%s/`"
                    % (
                        sp.category,
                        T.cat_name(sp.category)
                        .replace(" ", "_")
                        .replace(",", "")
                        .replace("&", "and"),
                    ),
                ),
                ("Source version", "%s, dated %s" % (sp.version, sp.date or "—")),
                ("Source status", sp.status),
                (
                    "House structure",
                    "19-section module and portal specification structure, "
                    "`03_Modules/_MODULE_TEMPLATE.md`",
                ),
                (
                    "Counting rule applied",
                    "Register rule **RG-06** — *count, do not consult*. Every quantity in this guide "
                    "book was counted directly from the source file at the time of generation. A "
                    "figure stated in a register was not treated as evidence.",
                ),
            ],
            accent=self.accent,
        )

        R.h_sub(doc, "Revision history", self.accent)
        R.table(
            doc,
            ["Edition", "Date", "Author", "Change"],
            [
                [
                    "1.0",
                    T.ISSUE_DATE,
                    "SPSL Programme Documentation Office",
                    "First issue. Generated from specification version %s dated %s. "
                    "Full restatement of the 19-section specification with orientation "
                    "material, %d exhibits and five annexes."
                    % (
                        sp.version,
                        sp.date or "—",
                        len([v for v in self.exhibits.values() if v]),
                    ),
                ]
            ],
            accent=self.accent,
            first_col_bold=True,
        )

        R.h_sub(doc, "How to read the figures in this guide book", self.accent)
        R.callout(
            doc,
            "Counts shown here are measured from the source specification and may differ "
            "from the totals published in `02-02 Module Catalogue — Master Register`. "
            "Where they differ, this guide book states the measured figure and the "
            "register figure side by side rather than silently preferring one. The "
            "programme's own rule RG-06 makes the measured figure the authoritative one; "
            "the register is the thing that needs correcting.",
            kind="rule",
            accent=self.accent,
            title="COUNTING RULE",
        )

        R.h_sub(doc, "Related documents", self.accent)
        R.table(
            doc,
            ["Document", "What it gives you"],
            [
                [
                    "`GB-000` Library master index",
                    "The whole guide book library — 79 components, 11 categories, one portal suite — "
                    "with the reading order for a new joiner.",
                ],
                [
                    "`GB-CAT-%s` Category %s guide book" % (sp.category, sp.category),
                    "How this %s fits with the others in Category %s, the boundaries between "
                    "them, and the category's shared concepts."
                    % (self.kind.lower(), sp.category),
                ],
                [
                    "`02-02` Module Catalogue — Master Register",
                    "The authoritative register of module identity, code, category, owner, "
                    "priority and wave.",
                ],
                [
                    "`05-01` Feature and Function Register",
                    "The programme-wide allocation of `FR-` identifier ranges.",
                ],
                [
                    "`05-02` Data Model and Entity Catalogue",
                    "The programme-wide entity register and its ownership allocations.",
                ],
                [
                    "`05-04` Role, Permission and Access Matrix",
                    "The registered role set `R01`–`R38` and the segregation-of-duties controls.",
                ],
                [
                    "`05-06` Non-Functional Requirements and Standards",
                    "The `NFR-` register and the regulatory obligations this component inherits.",
                ],
                [
                    "`06-01` Implementation Roadmap and Phasing",
                    "The nine-wave delivery plan this component's wave assignment comes from.",
                ],
            ],
            accent=self.accent,
            first_col_bold=True,
        )

        R.h_sub(doc, "Confidentiality", self.accent)
        R.callout(
            doc,
            "This guide book is classified **CONFIDENTIAL — Internal Use Only**. It "
            "contains the commercial, operational and technical design of %s and of the "
            "SPSL delivery approach. It may be shared inside SPSL and with named 1000FiX "
            "programme staff. It may not be forwarded outside those groups, published, or "
            "provided to a competitor, a supplier or a brand partner without the written "
            "approval of the programme sponsor." % T.CLIENT,
            kind="risk",
            accent=T.RED,
            title="HANDLING",
        )
        return self

    # ------------------------------------------------------------- how to use
    def how_to_use(self):
        doc, sp = self.doc, self.sp
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
            "This guide book has five parts and five annexes. The parts follow the "
            "19-section house structure that every module and portal specification in the "
            "programme conforms to, so once you have read one guide book you can navigate "
            "any of the other 78 without relearning the layout. Section numbers are stable "
            "across the whole library: §9 is always business rules, §12 is always "
            "interfaces, §16 is always delivery.",
        )

        R.h_sub(doc, "Read the sections your job needs", self.accent)
        R.body(
            doc,
            "Very few readers need all nineteen sections. The paths below are the ones the "
            "programme's own roles use most; take the row that matches what you are about "
            "to do, not the row that matches your job title.",
        )
        R.table(
            doc,
            ["If you are…", "Read, in this order", "Because"],
            [[a, b, c] for a, b, c in N.READING_PATHS],
            accent=self.accent,
            first_col_bold=True,
            caption="Reading paths by role",
        )

        R.h_sub(doc, "The five parts", self.accent)
        rows = []
        for n in (1, 2, 3, 4, 5):
            label, name, blurb = N.PARTS[n]
            secs = [
                s for s in range(1, 20) if N.SECTION_FRAME.get(s, {}).get("part") == n
            ]
            rows.append(
                ["%s — %s" % (label, name), "§%d–§%d" % (min(secs), max(secs)), blurb]
            )
        R.table(
            doc,
            ["Part", "Sections", "What it covers"],
            rows,
            accent=self.accent,
            first_col_bold=True,
        )

        R.h_sub(doc, "The annexes", self.accent)
        R.table(
            doc,
            ["Annex", "Contents", "Use it when"],
            [
                [
                    "A",
                    "Requirement index — every requirement in identifier order with its "
                    "area, priority and delivery layer",
                    "You are estimating, tracing or writing test cases.",
                ],
                [
                    "B",
                    "Relationship register — every other module and portal this one "
                    "touches, and the nature of each link",
                    "You are assessing the blast radius of a change.",
                ],
                [
                    "C",
                    "Glossary — the components, codes and house terms used in this document",
                    "You have hit an abbreviation and do not want to leave the page.",
                ],
                [
                    "D",
                    "Quick reference card — the whole component on one page",
                    "You are in a meeting, in a branch, or briefing someone in five minutes.",
                ],
                [
                    "E",
                    "Assurance and known defects — what was checked when this "
                    "guide book was generated, and what the checks found wrong "
                    "in the source specification",
                    "**Before you build anything.** Read it early, not last.",
                ],
                [
                    "F",
                    "Change control and feedback",
                    "You have found something wrong. Please use it.",
                ],
            ],
            accent=self.accent,
            first_col_bold=True,
        )

        R.h_sub(doc, "Conventions", self.accent)
        R.body(
            doc,
            "The programme uses a small, fixed vocabulary. It is worth learning once: the "
            "same four priority codes, four rule classes and six delivery layers appear in "
            "every one of the 79 guide books, and in every register behind them.",
        )
        R.table(
            doc,
            ["Kind", "Code", "Meaning"],
            [[a, b, c] for a, b, c in N.CONVENTIONS],
            accent=self.accent,
            first_col_bold=False,
            caption="Programme conventions used throughout this guide book",
        )

        R.h_sub(doc, "Panels", self.accent)
        R.body(
            doc,
            "Coloured panels carry a specific meaning throughout the library. They are not "
            "decoration and they are not emphasis — each one tells you what kind of "
            "statement you are reading.",
        )
        R.table(
            doc,
            ["Panel", "What it means"],
            [[a, b] for a, b in N.CALLOUT_LEGEND],
            accent=self.accent,
            first_col_bold=True,
        )

        R.callout(
            doc,
            "**Typography.** Body text is set in Calibri 9.5 pt throughout the library, "
            "as the house standard requires. Reference tables of seven columns or more "
            "drop to 8.5 pt so that they fit the A4 text column without reflowing; that "
            "is the only permitted deviation, and it applies to tabular matter only.",
            kind="note",
            accent=self.accent,
        )
        return self

    # -------------------------------------------------------------- contents
    def contents(self):
        doc = self.doc
        R.h_section(doc, None, "Contents", self.accent, page_break=True)
        p = doc.add_paragraph()
        K.pfmt(p, before=0, after=8)
        K.run(
            p,
            "Press Ctrl+A then F9 in Word to build the contents, the exhibit list and "
            "the page numbers. Fields are set to update automatically on open.",
            size=T.SIZE_SMALL,
            italic=True,
            colour=T.GREY,
        )
        tp = doc.add_paragraph()
        K.pfmt(tp, before=0, after=0)
        K.add_toc(tp, levels="1-2")

        R.h_section(doc, None, "Exhibits", self.accent, page_break=True)
        p = doc.add_paragraph()
        K.pfmt(p, before=0, after=8)
        K.run(
            p,
            "Every exhibit in this guide book is generated from the source "
            "specification. No figure is illustrative.",
            size=T.SIZE_SMALL,
            italic=True,
            colour=T.GREY,
        )
        ep = doc.add_paragraph()
        K.pfmt(ep, before=0, after=0)
        K.add_table_of_figures(ep, "Exhibit")

        R.h_section(doc, None, "Tables", self.accent, page_break=False)
        tp2 = doc.add_paragraph()
        K.pfmt(tp2, before=4, after=0)
        K.add_table_of_figures(tp2, "Table")
        return self

    # ----------------------------------------------------------- one-pager
    def one_page(self):
        doc, sp = self.doc, self.sp
        R.h_section(
            doc,
            None,
            "%s in one page" % sp.uid,
            self.accent,
            page_break=True,
            kicker="Executive orientation",
        )

        one = sp.one_liner()
        if one:
            R.pull_quote(
                doc,
                _short(one, 400),
                self.accent,
                attribution="§2 Purpose, %s" % sp.filename,
            )

        R.exhibit(
            doc,
            self.exhibits.get("scorecard"),
            "%s measured — every dimension counted from the specification" % sp.uid,
            accent=self.accent,
            source="Source: %s §1–§18." % sp.filename,
        )

        R.h_sub(doc, "Five things to know before you read further", self.accent)
        R.numbered(doc, N.five_things(sp), accent=self.accent, after=5)

        R.h_sub(doc, "Who works in it every day", self.accent)
        daily = N.daily_roles(sp)
        ro = N.read_only_roles(sp)
        appr = N.approvers(sp)
        R.definition_rows(
            doc,
            [
                (
                    "Creates and changes records",
                    ", ".join(daily)
                    if daily
                    else "No role holds create or update access — this component is read-only to its users.",
                ),
                ("Reads only", ", ".join(ro) if ro else "—"),
                (
                    "Approves",
                    ", ".join(appr)
                    if appr
                    else "No approval authority is defined in this component.",
                ),
            ],
            accent=self.accent,
            label_mm=46,
        )

        R.h_sub(doc, "What it owns, and what it must never touch", self.accent)
        owned = N._entity_names(sp.owned_entities)[:14]
        pairs = []
        if owned:
            pairs.append(
                (
                    "Sole authority for",
                    ", ".join("`%s`" % o for o in owned)
                    + (
                        " and %d more" % (len(sp.owned_entities) - len(owned))
                        if len(sp.owned_entities) > len(owned)
                        else ""
                    ),
                )
            )
        else:
            pairs.append(
                (
                    "Sole authority for",
                    "Nothing. This %s owns no entity; everything it shows is owned "
                    "elsewhere." % self.kind.lower(),
                )
            )
        bo = N.boundary_owners(sp)
        if bo:
            pairs.append(
                (
                    "Deliberately not its job",
                    ", ".join(
                        "%s (%d capabilit%s)" % (m, n, "y" if n == 1 else "ies")
                        for m, n in bo[:8]
                    ),
                )
            )
        if sp.depends_on:
            pairs.append(("Cannot start without", ", ".join(sp.depends_on)))
        if sp.depended_by:
            pairs.append(
                (
                    "Blocks, if it is late",
                    ", ".join(sp.depended_by[:16])
                    + (" …" if len(sp.depended_by) > 16 else ""),
                )
            )
        R.definition_rows(doc, pairs, accent=self.accent, label_mm=46)

        R.exhibit(
            doc,
            self.exhibits.get("wave"),
            "Delivery position — wave %s of nine across the 36-month programme"
            % (sp.wave or "unassigned"),
            accent=self.accent,
        )
        return self

    # ================================================================= parts
    def _section_frame(self, num):
        f = N.SECTION_FRAME.get(num)
        if not f:
            return None, None, None
        key = "p" if self.sp.is_portal else "m"
        return f[key]

    def _part(self, n):
        """Part divider plus a working contents list for that part."""
        doc, sp = self.doc, self.sp
        label, name, blurb = N.PARTS[n]
        R.part_opener(doc, label, name, blurb, self.accent)

        nums = [s for s in range(1, 20) if N.SECTION_FRAME.get(s, {}).get("part") == n]
        R.eyebrow(doc, "In this part", colour=self.accent, before=14, after=4)
        rows = []
        for s in nums:
            short, intro, _tip = self._section_frame(s)
            title = sp.sec_title(s) or short or ""
            rows.append(["§%d" % s, title, _short(intro, 210)])
        R.table(
            doc,
            ["", "Section", "What it tells you"],
            rows,
            accent=self.accent,
            first_col_bold=True,
            zebra=True,
        )

        counts = self._part_counts(n)
        if counts:
            R.kpi_strip(doc, counts, accent=self.accent)
        return self

    def _part_counts(self, n):
        sp = self.sp
        return {
            1: [
                (len(sp.in_scope), "capabilities in scope"),
                (len(sp.out_scope), "explicitly out of scope"),
                (len(sp.shared), "shared concepts"),
                (len(sp.benchmark), "systems benchmarked"),
            ],
            2: [
                (sp.req_count, "requirements"),
                (len(sp.areas), "areas"),
                (len(sp.tech_funcs), "technical functions"),
                (len(sp.quant_benefit), "quantified benefits"),
            ],
            3: [
                (len(sp.state_models), "state models"),
                (len(sp.rules), "business rules"),
                (len(sp.owned_entities) + len(sp.ref_entities), "entities"),
                (len(sp.automations), "automations"),
            ],
            4: [
                (len(sp.upstream), "interfaces consumed"),
                (len(sp.downstream), "interfaces provided"),
                (len(sp.events), "domain events"),
                (len(sp.roles), "roles"),
            ],
            5: [
                (len(sp.reports), "reports"),
                (len(sp.kpis), "KPIs"),
                (len(sp.cd_items), "custom components"),
                (len(sp.acceptance), "acceptance criteria"),
            ],
        }.get(n, [])

    def _open_section(self, num, page_break=True):
        doc, sp = self.doc, self.sp
        title = sp.sec_title(num) or (self._section_frame(num)[0] or "")
        R.h_section(doc, "%d." % num, title, self.accent, page_break=page_break)
        short, intro, tip = self._section_frame(num)
        if intro:
            p = doc.add_paragraph()
            K.pfmt(p, before=2, after=6, line=1.18, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            K.run(
                p,
                "What this section tells you.  ",
                size=T.SIZE_BODY,
                bold=True,
                colour=self.accent,
            )
            R.emit_inline(p, intro, size=T.SIZE_BODY, colour=T.INK_SOFT)
        return tip

    def _close_section_tip(self, tip, kind="note"):
        if tip:
            R.callout(self.doc, tip, kind=kind, accent=self.accent)

    # --------------------------------------------------------------- part 1
    def part_one(self):
        doc, sp = self.doc, self.sp
        self._part(1)

        # ---- §1
        tip = self._open_section(1, page_break=True)
        pairs = list(sp.identity.items())
        R.definition_rows(doc, pairs, accent=self.accent, label_mm=52)
        extra = [b for b in sp.sec_blocks(1) if b["t"] in ("quote", "p")]
        R.render_blocks(doc, extra, accent=self.accent)
        R.exhibit(
            doc,
            self.exhibits.get("wave"),
            "%s in the nine-wave delivery plan" % sp.uid,
            accent=self.accent,
        )
        self._close_section_tip(tip, "rule")

        # ---- §2
        tip = self._open_section(2)
        R.render_blocks(doc, sp.sec_blocks(2), accent=self.accent)
        self._close_section_tip(tip)

        # ---- §3
        tip = self._open_section(3)
        R.exhibit(
            doc,
            self.exhibits.get("boundary"),
            "The scope boundary in numbers — in scope, out of scope, shared",
            accent=self.accent,
        )
        R.render_blocks(doc, sp.sec_blocks(3), accent=self.accent)
        self._close_section_tip(tip, "rule")

        # ---- §4
        tip = self._open_section(4)
        R.render_blocks(doc, sp.sec_blocks(4), accent=self.accent)
        self._close_section_tip(tip)
        return self

    # --------------------------------------------------------------- part 2
    def part_two(self):
        doc, sp = self.doc, self.sp
        self._part(2)

        tip = self._open_section(5, page_break=True)
        R.kpi_strip(
            doc,
            [
                (sp.req_count, "requirements"),
                (len(sp.areas), "areas"),
                (sp.pri_mix.get("P0", 0) + sp.pri_mix.get("P1", 0), "P0 + P1"),
                (
                    "%.0f%%"
                    % (100.0 * (sp.layer_mix.get("L5", 0)) / max(sp.req_count, 1)),
                    "custom-built",
                ),
            ],
            accent=self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("areas"),
            "Where the requirement mass sits",
            accent=self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("priority"),
            "How much of this component is negotiable",
            accent=self.accent,
        )
        R.render_blocks(doc, sp.sec_blocks(5), accent=self.accent)
        self._close_section_tip(tip)

        tip = self._open_section(6)
        R.render_blocks(doc, sp.sec_blocks(6), accent=self.accent)
        self._close_section_tip(tip, "warning")

        tip = self._open_section(7)
        R.render_blocks(doc, sp.sec_blocks(7), accent=self.accent)
        self._close_section_tip(tip)
        return self

    # --------------------------------------------------------------- part 3
    def part_three(self):
        doc, sp = self.doc, self.sp
        self._part(3)

        tip = self._open_section(8, page_break=True)
        if self.exhibits.get("state"):
            R.exhibit(
                doc,
                self.exhibits["state"],
                "The lifecycle, rendered — the authoritative diagram follows below",
                accent=self.accent,
                source=self.exhibits.get("state_caption", ""),
            )
        R.render_blocks(
            doc,
            sp.sec_blocks(8),
            accent=self.accent,
            code_title="State machine — as specified",
        )
        self._close_section_tip(tip, "rule")

        tip = self._open_section(9)
        if sp.rules:
            R.exhibit(
                doc,
                self.exhibits.get("rules"),
                "Enforcement profile — what the system does when a rule is broken",
                accent=self.accent,
            )
        R.render_blocks(doc, sp.sec_blocks(9), accent=self.accent)
        self._close_section_tip(tip, "rule")

        tip = self._open_section(10)
        R.exhibit(
            doc,
            self.exhibits.get("data"),
            "Data ownership and data reach",
            accent=self.accent,
        )
        R.render_blocks(doc, sp.sec_blocks(10), accent=self.accent)
        self._close_section_tip(tip, "rule")

        tip = self._open_section(11)
        if sp.automations:
            R.exhibit(
                doc,
                self.exhibits.get("automation"),
                "Declared failure behaviour across every automation",
                accent=self.accent,
            )
        R.render_blocks(doc, sp.sec_blocks(11), accent=self.accent)
        self._close_section_tip(tip, "warning")
        return self

    # --------------------------------------------------------------- part 4
    def part_four(self):
        doc, sp = self.doc, self.sp
        self._part(4)

        tip = self._open_section(12, page_break=True)
        R.kpi_strip(
            doc,
            [
                (len(sp.upstream), "consumed"),
                (len(sp.downstream), "provided"),
                (len(sp.events), "events"),
                (len(sp.externals), "external"),
                (len(sp.api), "endpoints"),
            ],
            accent=self.accent,
        )
        R.exhibit(
            doc,
            self.exhibits.get("interfaces"),
            "The integration surface",
            accent=self.accent,
        )
        R.render_blocks(doc, sp.sec_blocks(12), accent=self.accent)
        self._close_section_tip(tip, "rule")

        tip = self._open_section(13)
        R.exhibit(
            doc,
            self.exhibits.get("roles"),
            "Role and permission matrix",
            accent=self.accent,
        )
        R.render_blocks(doc, sp.sec_blocks(13), accent=self.accent)
        self._close_section_tip(tip, "risk")
        return self

    # --------------------------------------------------------------- part 5
    def part_five(self):
        doc, sp = self.doc, self.sp
        self._part(5)

        tip = self._open_section(14, page_break=True)
        R.render_blocks(doc, sp.sec_blocks(14), accent=self.accent)
        self._close_section_tip(tip)

        tip = self._open_section(15)
        if self.exhibits.get("kpi"):
            R.exhibit(
                doc,
                self.exhibits["kpi"],
                "Baseline to target, for every indicator with a measured baseline",
                accent=self.accent,
            )
        R.render_blocks(doc, sp.sec_blocks(15), accent=self.accent)
        self._close_section_tip(tip)

        tip = self._open_section(16)
        R.exhibit(
            doc,
            self.exhibits.get("layers"),
            "The delivery layer split — the programme's cost model in one bar",
            accent=self.accent,
        )
        R.render_blocks(doc, sp.sec_blocks(16), accent=self.accent)
        if self.exhibits.get("peers"):
            R.exhibit(
                doc,
                self.exhibits["peers"],
                "How %s compares with the rest of Category %s" % (sp.uid, sp.category),
                accent=self.accent,
            )
        self._close_section_tip(tip)

        tip = self._open_section(17)
        R.render_blocks(doc, sp.sec_blocks(17), accent=self.accent)
        self._close_section_tip(tip)

        tip = self._open_section(18)
        R.render_blocks(doc, sp.sec_blocks(18), accent=self.accent)
        self._close_section_tip(tip, "warning")

        tip = self._open_section(19)
        R.render_blocks(doc, sp.sec_blocks(19), accent=self.accent)
        self._close_section_tip(tip)
        return self

    # ================================================================ annexes
    def annexes(self):
        doc, sp = self.doc, self.sp
        R.part_opener(
            doc,
            "Annexes",
            "Reference material",
            "Indexes, registers and a one-page card, all derived by measurement "
            "from the specification restated in Parts One to Five.",
            self.accent,
        )

        # ---------- Annex A
        R.h_section(
            doc,
            "Annex A",
            "Requirement index",
            self.accent,
            page_break=True,
            kicker="Reference",
        )
        R.body(
            doc,
            "Every requirement in %s, in identifier order, with the area it belongs to, its "
            "priority and the delivery layer it will be built in. Use this to trace, to "
            "estimate and to write test coverage. Identifiers are permanent: a withdrawn "
            "requirement's identifier is retired, never reissued." % sp.uid,
        )
        rows = sorted(sp.reqs, key=lambda r: r["id"])
        R.table(
            doc,
            ["FR ID", "Feature", "Area", "Pri", "Layer"],
            [
                [
                    r["id"],
                    r["feature"] or r["function"][:70],
                    r["area"],
                    r["pri"],
                    r["layer"],
                ]
                for r in rows
            ],
            align=["left", "left", "left", "center", "center"],
            accent=self.accent,
            compact=True,
            caption="Requirement index — %d requirements" % len(rows),
        )

        gaps = self._identifier_gaps()
        if gaps:
            R.callout(
                doc,
                "The allocated identifier range is `%s`. Counting the rows above gives "
                "**%d requirements**, not %d. %d identifier%s inside the range %s never "
                "issued and %s retired under rule RG-02, never to be reissued: %s."
                % (
                    sp.req_range or "—",
                    len(rows),
                    gaps["span"],
                    len(gaps["missing"]),
                    "" if len(gaps["missing"]) == 1 else "s",
                    "was" if len(gaps["missing"]) == 1 else "were",
                    "is" if len(gaps["missing"]) == 1 else "are",
                    ", ".join("`%s`" % g for g in gaps["missing"][:24])
                    + (" …" if len(gaps["missing"]) > 24 else ""),
                ),
                kind="audit",
                accent=T.OCHRE,
                title="IDENTIFIER RECONCILIATION",
            )

        # ---------- Annex B
        R.h_section(
            doc,
            "Annex B",
            "Relationship register",
            self.accent,
            page_break=True,
            kicker="Reference",
        )
        R.body(
            doc,
            "Every other module and portal that %s names, and the nature of each link. Read "
            "this before you change anything: it is the blast radius. A component appearing "
            "as a *declared prerequisite* must be live before %s is useful; one appearing as "
            "a *declared dependant* will feel any change you make here."
            % (sp.uid, sp.uid),
        )
        rel = N.relationship_register(sp, self.cat)
        if rel:
            R.table(
                doc,
                ["Component", "Name", "Category", "Nature of the relationship"],
                [list(r) for r in rel],
                accent=self.accent,
                compact=True,
                caption="Relationship register — %d connected components" % len(rel),
            )
        else:
            R.body(doc, "No related components are declared.")

        # ---------- Annex C
        R.h_section(
            doc,
            "Annex C",
            "Glossary and abbreviations",
            self.accent,
            page_break=True,
            kicker="Reference",
        )
        gl = N.glossary_terms(sp, self.cat)
        if gl:
            R.h_sub(doc, "Components referenced in this guide book", self.accent)
            R.table(
                doc,
                ["Code", "Component", "Category"],
                [list(g) for g in gl],
                accent=self.accent,
                compact=True,
            )
        R.h_sub(doc, "Programme terms", self.accent)
        R.table(
            doc,
            ["Term", "Meaning"],
            [[a, b] for a, b in N.HOUSE_GLOSSARY],
            accent=self.accent,
        )

        # ---------- Annex D
        self._quick_card()

        # ---------- Annex E
        self._assurance()

        # ---------- Annex F
        R.h_section(
            doc,
            "Annex F",
            "Change control and feedback",
            self.accent,
            page_break=True,
            kicker="Governance",
        )
        R.body(
            doc,
            "This guide book restates an approved specification. It cannot be corrected in "
            "isolation: if something here is wrong, either the guide book has misrepresented "
            "the specification, or the specification itself is wrong. The two routes are "
            "different and it matters which one you take.",
        )
        R.table(
            doc,
            ["What you have found", "Where it goes", "Who decides"],
            [
                [
                    "The guide book does not match the specification — a table is missing, a "
                    "figure is wrong, an exhibit misreads the data",
                    "Documentation defect against `%s`" % self.doc_id,
                    "SPSL Programme Documentation Office",
                ],
                [
                    "The specification itself is wrong — a rule, an interface, an owner, a "
                    "boundary",
                    "Specification change request against `%s`" % sp.filename,
                    "%s, with the ERP Steering Committee where scope moves"
                    % (sp.business_owner or "the component's business owner"),
                ],
                [
                    "A boundary is claimed by two components, or by neither",
                    "Boundary defect — rule RG-04 requires both sides to agree",
                    "Solution architecture, then both business owners",
                ],
                [
                    "An identifier collides with one already allocated elsewhere",
                    "Register defect against the owning register (`05-01`, `05-02`, `05-04`, `02-05`)",
                    "The allocating authority named in §0 of the house template",
                ],
                [
                    "An open question in §18 has in fact been answered",
                    "Decision record — the answer needs recording before it is lost",
                    "The owner named against that question",
                ],
            ],
            accent=self.accent,
            first_col_bold=False,
        )
        R.callout(
            doc,
            "Raising a defect is not criticism of the author. Three separate audits in "
            "August 2026 found 19 open findings across this documentation set, including "
            "two factual errors with legal consequence, and every one of them was found "
            "by a reader rather than by the writer. Please use this annex.",
            kind="good",
            accent=T.GREEN,
            title="PLEASE DO RAISE IT",
        )
        return self

    # ------------------------------------------------------- Annex E assurance
    def _assurance(self):
        """What was checked when this guide book was generated, and what the
        checks found in the source specification."""
        doc, sp = self.doc, self.sp
        R.h_section(
            doc,
            "Annex E",
            "Assurance and known defects",
            self.accent,
            page_break=True,
            kicker="Governance",
        )
        R.body(
            doc,
            "This guide book was generated by a documented pipeline and audited "
            "mechanically before issue. This annex states what was checked, what "
            "passed, and — more usefully — what the checks found wrong in the "
            "**source specification**. Those findings are reproduced here rather "
            "than quietly passed on, because a reader who does not know a figure "
            "is disputed will use it as though it were settled.",
        )

        R.h_sub(doc, "Checks that passed", self.accent)
        R.table(
            doc,
            ["Check", "What was verified", "Result"],
            [
                [c, d, "Passed"]
                for c, d in [(name, detail) for _code, name, detail in FINDINGS_PASSED]
            ],
            accent=self.accent,
            first_col_bold=True,
            caption="Generation-time assurance checks",
        )

        items = self.findings or []
        R.h_sub(doc, "Findings against the source specification", self.accent)
        if not items:
            R.callout(
                doc,
                "No integrity defect was found in the source specification "
                "for %s. Dependency declarations reciprocate, every "
                "referenced entity is defined by its declared owner, no "
                "prerequisite lands in a later wave, no identifier collides, "
                "and the stated requirement count matches the measured one." % sp.uid,
                kind="good",
                accent=T.GREEN,
                title="CLEAN",
            )
        else:
            R.body(
                doc,
                "%d finding%s %s raised against the source specification when "
                "this edition was generated. They are defects in the "
                "specification or its registers, not in this guide book, and "
                "they are listed here so that you do not build on them "
                "unknowingly."
                % (
                    len(items),
                    "" if len(items) == 1 else "s",
                    "was" if len(items) == 1 else "were",
                ),
            )
            R.table(
                doc,
                ["Ref", "Severity", "Finding"],
                [
                    [f["code"], f["severity"], "**%s.** %s" % (f["title"], f["detail"])]
                    for f in items
                ],
                align=["left", "center", "left"],
                accent=self.accent,
                first_col_bold=True,
                caption="Integrity findings against %s" % sp.filename,
            )
            R.h_sub(doc, "What to do about each", self.accent)
            R.table(
                doc,
                ["Ref", "Action"],
                [[f["code"], f["action"]] for f in items],
                accent=self.accent,
                first_col_bold=True,
            )
            sev = Counter(f["severity"] for f in items)
            if sev.get("High"):
                R.callout(
                    doc,
                    "**%d finding%s of high severity.** A high-severity "
                    "finding means something in this specification cannot be "
                    "built as written without a decision first — an entity "
                    "whose owner does not define it, a prerequisite that "
                    "lands after the thing that needs it, or an identifier "
                    "claimed twice. Resolve these before the wave gate, not "
                    "during the build."
                    % (sev["High"], "" if sev["High"] == 1 else "s"),
                    kind="risk",
                    accent=T.RED,
                    title="ACT BEFORE BUILD",
                )

        R.h_sub(doc, "How these findings were produced", self.accent)
        R.table(
            doc,
            ["Ref", "Check", "Rule it enforces"],
            [
                [
                    "F-01",
                    "Dependency reciprocity in §1",
                    "RG-04 — boundary and dependency symmetry",
                ],
                [
                    "F-02",
                    "Referenced entities are defined by their declared owner",
                    "One entity, one owner (`05-02`)",
                ],
                [
                    "F-03",
                    "No prerequisite lands in a later wave",
                    "Wave check, house template §16.3",
                ],
                [
                    "F-04",
                    "Allocated requirement identifiers were all issued",
                    "RG-02 — a withdrawn identifier is retired, never reissued",
                ],
                [
                    "F-05",
                    "Stated requirement count equals the measured count",
                    "RG-06 — count, do not consult",
                ],
                [
                    "F-06",
                    "Every published domain event has a declared consumer",
                    "Contract symmetry, house template §12.3",
                ],
                [
                    "F-07",
                    "Role identifiers are inside the registered range",
                    "`05-04` registers R01–R38",
                ],
                [
                    "F-08",
                    "Custom-development identifiers are unique",
                    "`CD-` is allocated programme-wide by `02-05`",
                ],
                [
                    "F-09",
                    "KPI identifiers are not allocated locally",
                    "`KPI-` is a programme-wide space",
                ],
                [
                    "F-10",
                    "Every automation declares a failure behaviour",
                    "House template §11 — no blank failure column",
                ],
            ],
            accent=self.accent,
            first_col_bold=True,
            compact=True,
        )
        return self

    def _identifier_gaps(self):
        sp = self.sp
        if not sp.reqs:
            return None
        nums = sorted(int(r["id"].rsplit("-", 1)[1]) for r in sp.reqs)
        code = sp.reqs[0]["id"].rsplit("-", 2)[1]
        lo, hi = nums[0], nums[-1]
        missing = [n for n in range(lo, hi + 1) if n not in set(nums)]
        if not missing:
            return None
        return {
            "span": hi - lo + 1,
            "missing": ["FR-%s-%03d" % (code, n) for n in missing],
        }

    def _quick_card(self):
        doc, sp = self.doc, self.sp
        R.h_section(
            doc,
            "Annex D",
            "Quick reference card",
            self.accent,
            page_break=True,
            kicker="One page, for the meeting",
        )
        R.body(
            doc,
            "Everything a colleague needs to hold %s in their head. Print this page."
            % sp.uid,
        )

        R.kpi_strip(
            doc,
            [
                (sp.priority, "priority"),
                (sp.wave or "—", "wave"),
                (sp.req_count, "requirements"),
                (len(sp.rules), "rules"),
                (
                    len(sp.owned_entities)
                    if not sp.is_portal
                    else len(sp.ref_entities),
                    "entities owned" if not sp.is_portal else "entities read",
                ),
            ],
            accent=self.accent,
        )

        one = sp.one_liner()
        pairs = [
            ("In one sentence", _short(one, 320) if one else "—"),
            ("Category", "%s — %s" % (sp.category, T.cat_name(sp.category))),
            ("Code", "`%s`" % (sp.code or "—")),
            ("Business owner", sp.business_owner or "—"),
            ("System owner", sp.system_owner or "—"),
            ("Effort", sp.effort_txt or "—"),
        ]
        areas = list(sp.areas.keys())
        if areas:
            pairs.append(
                (
                    "What it does",
                    " · ".join(areas[:10]) + (" · …" if len(areas) > 10 else ""),
                )
            )
        owned = N._entity_names(sp.owned_entities)[:10]
        if owned:
            pairs.append(("What it owns", ", ".join("`%s`" % o for o in owned)))
        hard = [r for r in sp.rules if r["class"] == "H"][:5]
        if hard:
            pairs.append(
                (
                    "Rules that block outright",
                    "  ·  ".join(
                        "**%s** %s" % (r["id"], _short(r["rule"], 90)) for r in hard
                    ),
                )
            )
        st = []
        for m in sp.state_models[:1]:
            st = X.all_states(m["lines"])[:14]
        if st:
            pairs.append(
                (
                    "States in the first lifecycle model",
                    "  ·  ".join(X._case(s) for s in st),
                )
            )
        daily = N.daily_roles(sp)
        if daily:
            pairs.append(("Used daily by", ", ".join(daily[:10])))
        if sp.depends_on:
            pairs.append(("Depends on", ", ".join(sp.depends_on)))
        if sp.depended_by:
            pairs.append(
                (
                    "Depended on by",
                    ", ".join(sp.depended_by[:20])
                    + (" …" if len(sp.depended_by) > 20 else ""),
                )
            )
        if sp.kpis:
            k0 = sp.kpis[0]
            pairs.append(
                ("Headline KPI", " · ".join(MD.plain(x) for x in k0[:3] if MD.plain(x)))
            )
        if sp.questions:
            pairs.append(
                (
                    "Still undecided",
                    "%d open question%s — see §18"
                    % (len(sp.questions), "" if len(sp.questions) == 1 else "s"),
                )
            )
        R.definition_rows(doc, pairs, accent=self.accent, label_mm=44)
        return self

    # ------------------------------------------------------------------ save
    def build(self):
        self.build_exhibits()
        self.doc = self._new_document()
        self.cover()

        sec = self.doc.add_section()
        K.setup_section(sec)
        K.restart_page_numbering(sec, 1)
        self._header_footer(sec)

        self.document_control()
        self.how_to_use()
        self.contents()
        self.one_page()
        self.part_one()
        self.part_two()
        self.part_three()
        self.part_four()
        self.part_five()
        self.annexes()

        fname = "%s_%s_Guide_Book.docx" % (
            self.sp.uid,
            _sanitise(self.sp.name.replace("&", "and")),
        )
        path = os.path.join(self.outdir, fname)
        if not os.path.isdir(self.outdir):
            os.makedirs(self.outdir, exist_ok=True)
        self.doc.save(path)
        return path
