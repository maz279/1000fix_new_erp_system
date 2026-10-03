# -*- coding: utf-8 -*-
"""
masterbook — GB-000, the master index and orientation volume for the library.

This is the one document a new SPSL joiner is given first. It explains the
estate, the library, how to navigate both, and what is known to be unsettled.
"""
import os
import re
from collections import OrderedDict, Counter, defaultdict

from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH

import theme as T
import docxkit as K
import render as R
import mdparse as MD
import exhibits as X
import exhibits_group as XG
import narrative as N
from groupbook import GroupBookBase, REVENUE_STREAMS
from guidebook import _short


COMPANY = [
    ("Legal name", "1000FiX Services Limited"),
    ("Founded", "29 August 2017"),
    ("Position", "Bangladesh's largest after-sales service provider, and the "
                 "country's only ISO 9001:2015 certified IT service provider"),
    ("Network", "51+ service centres across all eight administrative divisions"),
    ("People", "500+ employees, including 200–400 field technicians"),
    ("Customers", "250,000+ per month"),
    ("Brand partnerships", "17+ authorised warranty service agreements"),
    ("Hotline", "16743"),
    ("Head office", "586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, "
                    "Mirpur, Dhaka-1216"),
]

LAYER_TABLE = [
    ("L1", "Odoo 19 Community Edition", "The standard product.", "$0"),
    ("L2", "OCA community modules", "140+ modules across 18 repositories.", "$0"),
    ("L3", "Free third-party Odoo modules", "Selected, reviewed, pinned.", "$0"),
    ("L4", "Standalone open-source systems",
     "24 systems integrated alongside the ERP.", "$0"),
    ("L5", "Custom development",
     "Odoo modules, services and applications built for 1000FiX.",
     "Development cost"),
    ("L6", "Commercial components",
     "Four, used only where no viable open source exists.", "$0–36K / 3 years"),
]

ONBOARDING = [
    ("Day 1", "GB-000 (this volume), Parts One and Two",
     "The estate, the library, and how to find anything in it."),
    ("Day 2", "The category guide book for the area you will work in",
     "Why those components are grouped and where the seams run."),
    ("Day 3–5", "The component guide books for your first two components — "
                "Parts One and Two of each",
     "Purpose, boundary, benchmark, and the full requirement inventory."),
    ("Week 2", "Parts Three and Four of the same component guide books",
     "Lifecycle, rules, data ownership, interfaces and permissions — the "
     "material you will actually build or test against."),
    ("Week 3", "GB-000 Part Five, and §18 of every component you touch",
     "What is unsettled, who owns the decision, and by when."),
    ("Month 2", "The category guide books either side of yours",
     "Almost every defect that reaches production crosses a category boundary."),
]

AUDIT_CONTEXT = [
    ("00-06", "Documentation Audit Report",
     "5 critical, 6 high, 9 medium and 4 low findings, including two factual "
     "errors with legal consequence."),
    ("00-07", "Category H Audit and Repository Integrity Report",
     "Identifier-space violations and repository completeness understated by "
     "44 module specifications."),
    ("AUDIT-001", "Content and Repository Integrity Audit",
     "18 findings raised on 15 August 2026, of which 9 remained open at the "
     "time this library was generated."),
]


class MasterIndex(GroupBookBase):

    def __init__(self, specs, index, groups, outdir, exdir, structure,
                 audit_rows=None, findings=None):
        GroupBookBase.__init__(self, outdir, exdir)
        self.specs = specs
        self.index = index
        self.groups = groups
        self.structure = structure
        self.audit_rows = audit_rows or []
        self.findings = findings
        self.accent = T.NAVY
        self.doc_id = "GB-000"
        self.exdir = os.path.join(exdir, "_GB000")
        self.modules = [s for s in specs if not s.is_portal]
        self.portals = [s for s in specs if s.is_portal]

    # ------------------------------------------------------------ aggregates
    def totals(self):
        return OrderedDict([
            ("Guide books", len(self.specs) + 12 + 1),
            ("Modules", len(self.modules)),
            ("Portals", len(self.portals)),
            ("Module categories", 11),
            ("Functional requirements", sum(s.req_count for s in self.specs)),
            ("Build effort · PW",
             int(round(sum(s.effort_pw or 0 for s in self.specs)))),
            ("Business rules", sum(len(s.rules) for s in self.specs)),
            ("Owned entities", sum(len(s.owned_entities) for s in self.specs)),
            ("Domain events", sum(len(s.events) for s in self.specs)),
            ("Automations", sum(len(s.automations) for s in self.specs)),
            ("External links", sum(len(s.externals) for s in self.specs)),
            ("Open questions", sum(len(s.questions) for s in self.specs)),
        ])

    def category_coupling(self):
        cats = T.CATEGORY_ORDER + ["P"]
        idxmap = {c: i for i, c in enumerate(cats)}
        m = [[0] * len(cats) for _ in cats]
        for s in self.specs:
            src = "P" if s.is_portal else s.category
            for dep in set(s.depends_on + s.iface_up):
                meta = self.index.get(dep)
                if not meta:
                    continue
                dst = "P" if meta["is_portal"] else meta["category"]
                if src in idxmap and dst in idxmap:
                    m[idxmap[src]][idxmap[dst]] += 1
        return m, cats

    def wave_load(self):
        counts, effort = Counter(), defaultdict(float)
        for s in self.specs:
            ws = re.findall(r"W\d", s.wave or "")
            if not ws:
                continue
            share = (s.effort_pw or 0) / float(len(ws))
            for w in ws:
                counts[w] += 1
                effort[w] += share
        return counts, dict(effort)

    # -------------------------------------------------------------- exhibits
    def build_exhibits(self):
        os.makedirs(self.exdir, exist_ok=True)
        p = lambda n: os.path.join(self.exdir, "GB000_%s.png" % n)
        E = self.exhibits

        E["totals"] = X.scorecard(
            p("totals"), self.totals(), T.NAVY,
            "The 1000FiX ERP estate, measured",
            "Counted from all %d component specifications on %s"
            % (len(self.specs), T.ISSUE_DATE))

        E["treemap"] = XG.estate_treemap(
            p("treemap"),
            OrderedDict([(c, sum(s.req_count for s in self.groups.get(c, [])))
                         for c in T.CATEGORY_ORDER + ["P"]]),
            "Where the requirement mass sits",
            "Block area is proportional to measured functional requirements")

        E["library"] = XG.library_map(
            p("library"),
            OrderedDict([(c, [s.uid for s in self.groups.get(c, [])])
                         for c in T.CATEGORY_ORDER + ["P"]]),
            "The guide book library",
            "One guide book per component, plus one per category and one for "
            "the portal suite")

        m, cats = self.category_coupling()
        E["coupling"] = XG.estate_heatmap(
            p("coupling"), m, cats, cats,
            "How the categories are coupled",
            "Declared prerequisites and consumed interfaces, counted")

        wc, we = self.wave_load()
        E["waveload"] = XG.estate_wave_load(
            p("waveload"), wc, we,
            "Programme load, wave by wave",
            "Build effort in person-weeks, with the number of components "
            "landing in each wave")

        pri = Counter()
        for s in self.specs:
            pri.update(s.pri_mix)
        E["priority"] = X.priority_mix(
            p("priority"), pri, max(sum(pri.values()), 1),
            "Requirement priority across the whole estate",
            "How much of the programme is genuinely negotiable")

        acc = defaultdict(float)
        for s in self.specs:
            w = float(s.req_count) or 1.0
            for L, v in s.layer_alloc.items():
                acc[L] += (v.get("pct") or 0.0) * w
        tot = sum(acc.values()) or 1.0
        lm = OrderedDict((L, 100.0 * acc[L] / tot)
                         for L in ["L1", "L2", "L3", "L4", "L5", "L6"] if acc.get(L))
        E["layers"] = XG.stack_bar(
            p("layers"), list(lm.keys()), list(lm.values()),
            "Where the whole build comes from",
            "Requirement-weighted delivery layer mix across all %d components"
            % len(self.specs),
            colours=[T.LAYER_COLOUR[k] for k in lm.keys()], value_fmt="%.0f%%")

        E["revenue"] = XG.revenue_streams(
            p("revenue"), REVENUE_STREAMS,
            "The fourteen revenue streams and the modules that run them",
            "The reason the module count moved from eleven to sixty-seven")

        rm = Counter()
        for s in self.specs:
            rm.update(s.rule_mix)
        E["rules"] = X.rule_classes(
            p("rules"), rm, max(sum(rm.values()), 1),
            "How the estate enforces its rules",
            "%d business and portal rules, classified" % sum(rm.values()))
        return self

    # ----------------------------------------------------------------- build
    def build(self):
        self.build_exhibits()
        self.doc = self._new_document(
            title="1000FiX ERP Guide Book Library — Master Index",
            subject="%s · Master index and orientation volume" % T.PROGRAMME,
            keywords="1000FiX, ERP, guide book library, master index, SPSL, "
                     "Odoo 19, after-sales service, Bangladesh",
            comments="GB-000 master index, %s." % T.EDITION,
            category_str="Library master index")

        self._cover(
            big="GB-000", code="",
            name="ERP Guide Book Library",
            kind_line="Master Index and Orientation Volume",
            strip_text="%d MODULES  ·  %d PORTALS  ·  11 CATEGORIES  ·  "
                       "%d GUIDE BOOKS"
                       % (len(self.modules), len(self.portals),
                          len(self.specs) + 12),
            one_liner="Every module and every portal of the 1000FiX ERP, written "
                      "up as a working guide book, indexed here. Start with this "
                      "volume; it will tell you which of the other %d to open."
                      % (len(self.specs) + 11),
            facts=[("Guide books", len(self.specs) + 12),
                   ("Modules", len(self.modules)),
                   ("Portals", len(self.portals)),
                   ("Requirements", sum(s.req_count for s in self.specs)),
                   ("Build effort", "%d person-weeks"
                    % int(round(sum(s.effort_pw or 0 for s in self.specs)))),
                   ("Programme", "36 months · 9 waves")])

        sec = self.doc.add_section()
        K.setup_section(sec)
        K.restart_page_numbering(sec, 1)
        self._header_footer(sec, "%s  ·  %s" % (T.PROGRAMME, T.LIBRARY),
                            "GB-000", "Master Index", self.doc_id)

        self._control()
        self._how()
        self._contents()
        self._part_one()
        self._part_two()
        self._part_three()
        self._part_four()
        self._part_five()
        self._annexes()

        if not os.path.isdir(self.outdir):
            os.makedirs(self.outdir, exist_ok=True)
        path = os.path.join(self.outdir,
                            "GB-000_ERP_Guide_Book_Library_Master_Index.docx")
        self.doc.save(path)
        return path

    # -------------------------------------------------------------- sections
    def _control(self):
        doc = self.doc
        R.h_section(doc, None, "Document control", self.accent,
                    kicker="About this volume")
        R.body(doc,
               "This is the master index of the 1000FiX ERP Guide Book Library. The "
               "library restates the programme's approved module and portal "
               "specifications as working guide books for SPSL staff: one volume for "
               "every module, one for every portal, one for every category, one for "
               "the portal suite as a whole, and this one to hold them together.")
        R.definition_rows(doc, [
            ("Volume", "GB-000 — Master Index and Orientation"),
            ("Library", "%s · %s" % (T.LIBRARY, T.PROGRAMME)),
            ("Volumes", "%d component guide books · 11 category guide books · "
                        "1 portal suite guide book · 1 master index"
                        % len(self.specs)),
            ("Edition", "%s, issued %s" % (T.EDITION, T.ISSUE_DATE)),
            ("Audience", "All SPSL staff working on the 1000FiX ERP programme, "
                         "and named 1000FiX programme staff"),
            ("Classification", T.CLASSIFICATION),
            ("Document owner", "SPSL ERP Programme Documentation Office"),
            ("Source", "`1000fix_ERP_Module/03_Modules/` — the approved 19-section "
                       "module and portal specifications, plus the eleven "
                       "`_CATEGORY_OVERVIEW.md` documents"),
            ("Counting rule applied",
             "Register rule **RG-06** — *count, do not consult*. Every quantity in "
             "the library was counted directly from the specification files at the "
             "time of generation."),
            ("Review cycle", "At each wave gate, and on any change to a source "
                             "specification"),
        ], accent=self.accent)
        R.callout(doc,
                  "This library is a **restatement**, not a replacement. Where a "
                  "guide book and its source specification disagree, the "
                  "specification wins and the guide book is the defect. Where the "
                  "specification and a register disagree on a count, the measured "
                  "figure wins under RG-06 and the register is the defect. Annex F "
                  "lists the differences found while this edition was generated.",
                  kind="rule", accent=T.PLUM, title="AUTHORITY")

    def _how(self):
        doc = self.doc
        R.h_section(doc, None, "How the library works", self.accent,
                    page_break=True, kicker="Orientation")
        R.body(doc,
               "The library has three levels. Each answers a different question, and "
               "each is a complete document in its own right — you never have to read "
               "up or down a level to make sense of the one you are in.")
        R.table(doc, ["Level", "Volume", "Answers", "How many"],
                [["Library", "`GB-000` Master index (this volume)",
                  "What is the estate, what is in the library, where do I start?", "1"],
                 ["Grouping", "`GB-CAT-A` … `GB-CAT-K` category guide books, "
                              "`GB-PORTALS` suite guide book",
                  "Why are these components grouped, where do the seams run, what "
                  "does the grouping cost?", "12"],
                 ["Component", "`GB-M01` … `GB-M67`, `GB-P01` … `GB-P12`",
                  "What does this component do, how does it behave, who uses it, "
                  "how is it built?", str(len(self.specs))]],
                accent=self.accent, first_col_bold=True,
                caption="The three levels of the library")

        R.h_sub(doc, "Where the files live", self.accent)
        R.body(doc,
               "The folder structure mirrors the three levels. Module guide books are "
               "grouped by category; portal guide books sit together in their own "
               "folder, because a portal is not a module and grouping it with one "
               "would repeat the classification error the v2.0 architecture "
               "corrected.")
        R.code_panel(doc, self.structure, title="Library folder structure",
                     accent=self.accent)

        R.h_sub(doc, "Naming", self.accent)
        R.table(doc, ["Pattern", "Meaning", "Example"],
                [["`GB-000_…`", "The master index — this volume",
                  "`GB-000_ERP_Guide_Book_Library_Master_Index.docx`"],
                 ["`CAT-<letter>_…_Category_Guide_Book.docx`",
                  "A category guide book",
                  "`CAT-G_Finance_and_Treasury_Category_Guide_Book.docx`"],
                 ["`PORTALS_…_Suite_Guide_Book.docx`",
                  "The portal suite guide book",
                  "`PORTALS_Portal_and_Application_Suite_Guide_Book.docx`"],
                 ["`M<nn>_…_Guide_Book.docx`", "A module guide book",
                  "`M09_Warranty_Protection_Plans_and_Claims_Guide_Book.docx`"],
                 ["`P<nn>_…_Guide_Book.docx`", "A portal guide book",
                  "`P02_Technician_Mobile_Application_Guide_Book.docx`"]],
                accent=self.accent, first_col_bold=True)

        R.h_sub(doc, "Every component guide book has the same shape", self.accent)
        rows = []
        for n in range(1, 20):
            f = N.SECTION_FRAME.get(n)
            if not f:
                continue
            rows.append(["§%d" % n, f["m"][0], f["p"][0],
                         "Part %d" % f["part"]])
        R.table(doc, ["Section", "In a module guide book", "In a portal guide book",
                      "Part"], rows, accent=self.accent, compact=True,
                caption="The 19-section house structure, identical across all "
                        "%d component guide books" % len(self.specs))

        R.h_sub(doc, "Conventions", self.accent)
        R.table(doc, ["Kind", "Code", "Meaning"],
                [[a, b, c] for a, b, c in N.CONVENTIONS], accent=self.accent)
        R.table(doc, ["Panel", "What it means"],
                [[a, b] for a, b in N.CALLOUT_LEGEND], accent=self.accent)

    # ------------------------------------------------------------- Part One
    def _part_one(self):
        doc = self.doc
        R.part_opener(doc, "Part One", "The business and the estate",
                      "Who 1000FiX is, what the ERP has to run, and the shape of "
                      "the system that runs it.", self.accent)

        R.h_section(doc, "1.", "The company", self.accent, page_break=True)
        R.definition_rows(doc, COMPANY, accent=self.accent, label_mm=44)

        R.h_section(doc, "2.", "Why sixty-seven modules", self.accent)
        R.body(doc,
               "1000FiX has committed, across its business plan, its Service App "
               "scope of work and its portal roadmap, to operating **fourteen "
               "distinct revenue streams**. The originally approved ERP covered "
               "eleven modules and could run five of them. This estate defines the "
               "system that can run all fourteen, benchmarked against SAP S/4HANA "
               "Service, Oracle Fusion Cloud, Microsoft Dynamics 365, IFS Cloud, "
               "Odoo 19 and the specialist after-sales platforms used in comparable "
               "markets.")
        R.exhibit(doc, self.exhibits.get("revenue"),
                  "The fourteen revenue streams and their owning modules",
                  accent=self.accent)

        R.h_section(doc, "3.", "The estate, measured", self.accent,
                    page_break=True)
        R.exhibit(doc, self.exhibits.get("totals"),
                  "Every dimension of the estate, counted from the specifications",
                  accent=self.accent)
        R.exhibit(doc, self.exhibits.get("treemap"),
                  "Where the requirement mass sits, by category",
                  accent=self.accent)
        R.exhibit(doc, self.exhibits.get("priority"),
                  "Priority mix across the whole estate", accent=self.accent)

        R.h_section(doc, "4.", "The six delivery layers", self.accent,
                    page_break=True)
        R.body(doc,
               "Every requirement in the estate is allocated to one of six delivery "
               "layers. The allocation is the programme's cost model: what comes "
               "from the product and the community costs nothing to licence, and "
               "what is custom has to be built, tested and maintained.")
        R.table(doc, ["Layer", "What it is", "Detail", "Licence cost"],
                [list(r) for r in LAYER_TABLE], accent=self.accent,
                caption="The six delivery layers")
        R.exhibit(doc, self.exhibits.get("layers"),
                  "The measured layer mix across all components",
                  accent=self.accent)
        R.callout(doc,
                  "**Software licence cost for the ERP core is $0.** Layers L1 to L4 "
                  "are open source. Only L6 carries a licence line, and only where no "
                  "viable open-source component exists.",
                  kind="good", accent=T.GREEN, title="COST POSITION")

        R.h_section(doc, "5.", "How the rules are enforced", self.accent)
        R.exhibit(doc, self.exhibits.get("rules"),
                  "Rule enforcement classes across the estate", accent=self.accent)

    # ------------------------------------------------------------- Part Two
    def _part_two(self):
        doc = self.doc
        R.part_opener(doc, "Part Two", "The library",
                      "Every guide book in the library, what it covers, and where "
                      "to find it.", self.accent)
        R.exhibit(doc, self.exhibits.get("library"),
                  "The library at a glance — every component guide book, grouped "
                  "by category", accent=self.accent)

        for letter in T.CATEGORY_ORDER:
            group = self.groups.get(letter, [])
            if not group:
                continue
            acc = T.cat_colour(letter)
            R.h_section(doc, "Category %s" % letter, T.cat_name(letter), acc,
                        page_break=True, kicker="Guide books")
            R.kpi_strip(doc, [
                (len(group), "modules"),
                (sum(s.req_count for s in group), "requirements"),
                (int(round(sum(s.effort_pw or 0 for s in group))), "person-weeks"),
                (sum(len(s.rules) for s in group), "rules"),
                (sum(len(s.owned_entities) for s in group), "entities"),
            ], accent=acc)
            R.table(doc,
                    ["Guide book", "Module", "Code", "In one sentence", "Pri", "Wave"],
                    [["GB-%s" % s.uid, s.name, s.code,
                      _short(s.one_liner(), 130), s.priority, s.wave or "—"]
                     for s in group],
                    align=["left", "left", "left", "left", "center", "center"],
                    accent=acc, compact=True,
                    caption="Category %s — %d module guide books"
                            % (letter, len(group)))

        acc = T.cat_colour("P")
        R.h_section(doc, "Portals", "Portal & Application Suite", acc,
                    page_break=True, kicker="Guide books")
        R.body(doc,
               "The ERP is the system of record. Portals and applications are "
               "surfaces onto it. No portal holds authoritative state, no portal "
               "implements a business rule, every portal authenticates through M29 "
               "and calls through the M28 gateway, and every portal is measured.")
        R.kpi_strip(doc, [
            (len(self.portals), "portals"),
            (sum(s.req_count for s in self.portals), "requirements"),
            (int(round(sum(s.effort_pw or 0 for s in self.portals))), "person-weeks"),
            (sum(len(s.rules) for s in self.portals), "portal rules"),
        ], accent=acc)
        R.table(doc,
                ["Guide book", "Portal", "Code", "In one sentence", "Pri", "Wave"],
                [["GB-%s" % s.uid, s.name, s.code, _short(s.one_liner(), 130),
                  s.priority, s.wave or "—"] for s in self.portals],
                align=["left", "left", "left", "left", "center", "center"],
                accent=acc, compact=True,
                caption="The twelve portal and application guide books")

    # ----------------------------------------------------------- Part Three
    def _part_three(self):
        doc = self.doc
        R.part_opener(doc, "Part Three", "How the estate hangs together",
                      "Coupling between categories, the shared kernel every "
                      "component depends on, and the components that would hurt "
                      "most if they were late.", self.accent)
        R.exhibit(doc, self.exhibits.get("coupling"),
                  "Category-to-category coupling, counted from declared "
                  "prerequisites and consumed interfaces", accent=self.accent)

        R.h_section(doc, None, "The most depended-upon components", self.accent,
                    page_break=True)
        R.body(doc,
               "Counted from every declared prerequisite and consumed interface "
               "across the estate. If one of these slips, the slip propagates. They "
               "are the components to staff first and to protect hardest.")
        dep = Counter()
        for s in self.specs:
            for d in set(s.depends_on + s.iface_up):
                dep[d] += 1
        rows = []
        for uid, n in dep.most_common(24):
            meta = self.index.get(uid)
            if not meta:
                continue
            rows.append([uid, meta["name"],
                         "%s · %s" % (meta["category"], meta["cat_name"]),
                         meta["priority"], meta["wave"] or "—", str(n)])
        R.table(doc, ["Component", "Name", "Category", "Pri", "Wave",
                      "Depended on by"], rows,
                align=["left", "left", "left", "center", "center", "right"],
                accent=self.accent, compact=True,
                caption="The estate's critical path, by declared dependency count")

        R.h_section(doc, None, "The components with the most open questions",
                    self.accent, page_break=True)
        q = sorted(self.specs, key=lambda s: len(s.questions), reverse=True)[:20]
        R.table(doc, ["Component", "Name", "Wave", "Open questions",
                      "Acceptance criteria"],
                [[s.uid, s.name, s.wave or "—", str(len(s.questions)),
                  str(len(s.acceptance))] for s in q],
                align=["left", "left", "center", "right", "right"],
                accent=self.accent, compact=True,
                caption="Where the design is least settled")

    # ------------------------------------------------------------ Part Four
    def _part_four(self):
        doc = self.doc
        R.part_opener(doc, "Part Four", "Delivering it",
                      "Nine waves across 36 months, and what has to happen in "
                      "each.", self.accent)
        R.exhibit(doc, self.exhibits.get("waveload"),
                  "Programme load by wave", accent=self.accent)

        R.h_section(doc, None, "What lands in each wave", self.accent,
                    page_break=True)
        for w, (a, b) in X.WAVE_MONTHS.items():
            comp = [s for s in self.specs if w in re.findall(r"W\d", s.wave or "")]
            if not comp:
                continue
            R.h_sub(doc, "%s — months %d to %d" % (w, a, b), self.accent)
            R.table(doc, ["Component", "Name", "Category", "Pri", "Reqs", "PW"],
                    [[s.uid, s.name,
                      "P" if s.is_portal else s.category, s.priority,
                      str(s.req_count), str(int(s.effort_pw or 0))]
                     for s in sorted(comp, key=lambda x: (x.priority, x.uid))],
                    align=["left", "left", "center", "center", "right", "right"],
                    accent=self.accent, compact=True)

    # ------------------------------------------------------------ Part Five
    def _part_five(self):
        doc = self.doc
        R.part_opener(doc, "Part Five", "Governance, currency and honesty",
                      "What is known to be unsettled, how figures in this library "
                      "were derived, and what to do when you find something wrong.",
                      self.accent)

        R.h_section(doc, None, "Onboarding path", self.accent, page_break=True)
        R.body(doc,
               "A new SPSL joiner should be able to hold a useful conversation about "
               "their part of the estate within a week, and to build or test against "
               "it within three. This is the path that gets there.")
        R.table(doc, ["When", "Read", "What you will be able to do"],
                [list(r) for r in ONBOARDING], accent=self.accent,
                first_col_bold=True, caption="Onboarding curriculum")

        R.h_section(doc, None, "Reading paths by role", self.accent)
        R.table(doc, ["If you are…", "Read, in this order", "Because"],
                [[a, b, c] for a, b, c in N.READING_PATHS],
                accent=self.accent, first_col_bold=True)

        R.h_section(doc, None, "The status of the source material", self.accent,
                    page_break=True)
        R.callout(doc,
                  "**The source specification set is DRAFT FOR APPROVAL.** Nothing in "
                  "this library is authorised for build until the ERP Steering "
                  "Committee approves the programme charter. Read the guide books; "
                  "do not treat a requirement identifier in them as a build "
                  "instruction until the gate is passed.",
                  kind="warning", accent=T.GOLD, title="STATUS")
        R.body(doc,
               "Three audits were run against the source documentation in August "
               "2026. Their findings are not hidden from this library — several of "
               "them are reproduced inside the component guide books as audit panels, "
               "because a reader who does not know a figure is disputed will use it "
               "as though it were settled.")
        R.table(doc, ["Audit", "Title", "What it found"],
                [list(r) for r in AUDIT_CONTEXT], accent=self.accent,
                first_col_bold=True)

        R.h_section(doc, None, "How to raise a defect", self.accent)
        R.table(doc, ["What you have found", "Where it goes", "Who decides"],
                [["A guide book does not match its source specification",
                  "Documentation defect against that guide book's `GB-` identifier",
                  "SPSL Programme Documentation Office"],
                 ["A specification is wrong",
                  "Specification change request against the source file",
                  "The component's business owner, with the Steering Committee "
                  "where scope moves"],
                 ["A boundary is claimed twice, or by nobody",
                  "Boundary defect — rule RG-04 requires both sides to agree",
                  "Solution architecture, then both business owners"],
                 ["A count in a register disagrees with the measured figure",
                  "Register defect — under RG-06 the measured figure wins",
                  "The allocating authority for that register"],
                 ["An open question has actually been answered",
                  "Decision record, before the answer is lost",
                  "The owner named against that question"]],
                accent=self.accent)

    # -------------------------------------------------------------- annexes
    def _annexes(self):
        doc = self.doc
        R.part_opener(doc, "Annexes", "Registers",
                      "The complete registers, measured from the specifications.",
                      self.accent)

        R.h_section(doc, "Annex A", "Complete module register", self.accent,
                    page_break=True, kicker="Reference")
        R.table(doc,
                ["ID", "Module", "Code", "Cat", "Pri", "Wave", "Reqs", "PW",
                 "Rules", "Ents"],
                [[s.uid, s.name, s.code, s.category, s.priority, s.wave or "—",
                  str(s.req_count), str(int(s.effort_pw or 0)), str(len(s.rules)),
                  str(len(s.owned_entities))]
                 for s in sorted(self.modules, key=lambda x: x.uid)],
                align=["left", "left", "left", "center", "center", "center",
                       "right", "right", "right", "right"],
                accent=self.accent, compact=True,
                caption="All %d modules, measured" % len(self.modules))

        R.h_section(doc, "Annex B", "Complete portal register", self.accent,
                    page_break=True, kicker="Reference")
        R.table(doc,
                ["ID", "Portal", "Code", "Pri", "Wave", "Reqs", "PW", "Rules",
                 "Modules read"],
                [[s.uid, s.name, s.code, s.priority, s.wave or "—",
                  str(s.req_count), str(int(s.effort_pw or 0)), str(len(s.rules)),
                  str(len(s.upstream))]
                 for s in sorted(self.portals, key=lambda x: x.uid)],
                align=["left", "left", "left", "center", "center", "right",
                       "right", "right", "right"],
                accent=self.accent, compact=True,
                caption="All %d portals and applications, measured"
                        % len(self.portals))

        R.h_section(doc, "Annex C", "Category register", self.accent,
                    page_break=True, kicker="Reference")
        rows = []
        for c in T.CATEGORY_ORDER + ["P"]:
            g = self.groups.get(c, [])
            if not g:
                continue
            rows.append([c, T.cat_name(c), str(len(g)),
                         str(sum(s.req_count for s in g)),
                         str(int(round(sum(s.effort_pw or 0 for s in g)))),
                         str(sum(len(s.rules) for s in g)),
                         str(sum(len(s.owned_entities) for s in g)),
                         str(sum(len(s.questions) for s in g))])
        rows.append(["", "**Total**", str(len(self.specs)),
                     str(sum(s.req_count for s in self.specs)),
                     str(int(round(sum(s.effort_pw or 0 for s in self.specs)))),
                     str(sum(len(s.rules) for s in self.specs)),
                     str(sum(len(s.owned_entities) for s in self.specs)),
                     str(sum(len(s.questions) for s in self.specs))])
        R.table(doc, ["Cat", "Name", "Components", "Reqs", "PW", "Rules",
                      "Entities", "Open Qs"], rows,
                align=["center", "left", "right", "right", "right", "right",
                       "right", "right"],
                accent=self.accent,
                caption="Every category, measured")

        R.h_section(doc, "Annex D", "Revenue stream map", self.accent,
                    page_break=True, kicker="Reference")
        R.table(doc, ["#", "Revenue stream", "Owning module(s)"],
                [[str(n), name, owner] for n, name, owner, _c in REVENUE_STREAMS],
                align=["center", "left", "left"], accent=self.accent,
                caption="The fourteen revenue streams the estate exists to run")

        R.h_section(doc, "Annex E", "Glossary", self.accent, page_break=True,
                    kicker="Reference")
        R.table(doc, ["Term", "Meaning"],
                [[a, b] for a, b in N.HOUSE_GLOSSARY], accent=self.accent)

        R.h_section(doc, "Annex F", "Measured against the register", self.accent,
                    page_break=True, kicker="Assurance")
        R.body(doc,
               "Every quantity in this library was counted from the specification "
               "files. Where the count differs from a figure published in a "
               "programme register, both are stated below rather than one being "
               "silently preferred. Under rule RG-06 the measured figure is the "
               "authoritative one and the register is what needs correcting.")
        if self.audit_rows:
            R.table(doc, ["Measure", "Register figure", "Measured", "Difference",
                          "Note"], self.audit_rows, accent=self.accent,
                    caption="Differences found while generating this edition")
        else:
            R.body(doc, "No differences were recorded for this edition.")

        self._annex_findings()

    # ------------------------------------------------------- findings register
    CHECK_NAMES = OrderedDict([
        ("F-01", ("Dependency declaration is not reciprocated", "Medium",
                  "RG-04 — a prerequisite must be declared on both sides")),
        ("F-01b", ("Dependant declaration is not reciprocated", "Low",
                   "RG-04, reverse direction")),
        ("F-02", ("Referenced entity is not defined by its declared owner", "High",
                  "One entity, one owner — `05-02`")),
        ("F-03", ("Wave inversion — a prerequisite lands later", "High",
                  "Wave check, house template §16.3")),
        ("F-04", ("Allocated requirement identifiers were never issued", "Low",
                  "RG-02 — retired, never reissued")),
        ("F-05", ("Stated requirement count differs from the measured count",
                  "Medium", "RG-06 — count, do not consult")),
        ("F-06", ("Domain event has no declared consumer", "Low",
                  "Contract symmetry, house template §12.3")),
        ("F-07", ("Role identifier is not in the registered range", "Medium",
                  "`05-04` registers R01–R38")),
        ("F-08", ("Custom-development identifiers collide", "High",
                  "`CD-` is allocated programme-wide by `02-05`")),
        ("F-09", ("KPI identifiers appear in more than one component", "Medium",
                  "`KPI-` is a programme-wide space")),
        ("F-10", ("Automation has no declared failure behaviour", "High",
                  "House template §11")),
    ])

    def _annex_findings(self):
        doc = self.doc
        f = self.findings
        R.h_section(doc, "Annex G", "Integrity findings register", self.accent,
                    page_break=True, kicker="Assurance")
        R.body(doc,
               "Ten mechanical integrity checks were run across all %d component "
               "specifications while this edition was generated — eleven finding "
               "references, because the reciprocity check reports each direction "
               "separately. Every finding is reproduced in the affected "
               "component's own guide book at Annex E; this register is the "
               "estate-wide roll-up. These are defects in the **source "
               "specifications and their registers**, not in the guide books."
               % len(self.specs))

        if f is None:
            R.body(doc, "No findings analysis was supplied for this edition.")
            return

        counts = f.summary()
        affected = len(f.per)
        R.kpi_strip(doc, [
            (sum(counts.values()), "findings raised"),
            (affected, "components affected"),
            (len(self.specs) - affected, "components clean"),
            (len({c.rstrip("b") for c in self.CHECK_NAMES}), "checks run"),
        ], accent=self.accent)

        R.h_sub(doc, "Findings by check", self.accent)
        rows = []
        for code, (title, sev, rule) in self.CHECK_NAMES.items():
            n = counts.get(code, 0)
            comps = sorted(uid for uid, lst in f.per.items()
                           if any(x["code"] == code for x in lst))
            rows.append([code, title, sev, str(n),
                         (", ".join(comps[:26]) + (" …" if len(comps) > 26 else ""))
                         if comps else "— none —"])
        R.table(doc, ["Ref", "Finding", "Severity", "Count", "Components affected"],
                rows, align=["left", "left", "center", "right", "left"],
                accent=self.accent, first_col_bold=True, compact=True,
                caption="Integrity findings across the estate")

        R.h_sub(doc, "What each check enforces", self.accent)
        R.table(doc, ["Ref", "Rule it enforces"],
                [[c, r] for c, (_t, _s, r) in self.CHECK_NAMES.items()],
                accent=self.accent, first_col_bold=True, compact=True)

        if f.library:
            R.h_sub(doc, "Estate-level findings", self.accent)
            for item in f.library:
                R.callout(doc,
                          "**%s.** %s\n" % (item["title"], item["detail"]),
                          kind="audit" if item["severity"] != "High" else "risk",
                          accent=T.OCHRE if item["severity"] != "High" else T.RED,
                          title="%s · %s" % (item["code"], item["severity"].upper()))
                R.body(doc, "**Action.** " + item["action"])

        R.h_sub(doc, "Components with the most findings", self.accent)
        ranked = sorted(f.per.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:25]
        R.table(doc, ["Component", "Name", "Findings", "High", "Medium", "Low"],
                [[uid,
                  self.index.get(uid, {}).get("name", "—"),
                  str(len(lst)),
                  str(sum(1 for x in lst if x["severity"] == "High")),
                  str(sum(1 for x in lst if x["severity"] == "Medium")),
                  str(sum(1 for x in lst if x["severity"] == "Low"))]
                 for uid, lst in ranked],
                align=["left", "left", "right", "right", "right", "right"],
                accent=self.accent, compact=True,
                caption="Where the source material needs attention first")

        R.callout(doc,
                  "None of these findings stops the library being used. Every one "
                  "of them stops a specific line of a specific specification being "
                  "built from without a decision first. They are listed component "
                  "by component in each guide book's Annex E precisely so that the "
                  "decision is taken by the person who needs it, at the moment "
                  "they need it.",
                  kind="note", accent=self.accent, title="HOW TO USE THIS REGISTER")
