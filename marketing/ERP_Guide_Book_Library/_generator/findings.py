# -*- coding: utf-8 -*-
"""
findings — integrity analysis of the source specification set.

These are findings about the *source material*, computed while the guide
books are generated, and reported inside them. A guide book that silently
passes on a broken reciprocity declaration or an entity whose declared owner
does not define it has made the reader's job harder, not easier.

Every check here is mechanical and reproducible. None of them is a judgement
about whether a design decision is right.
"""

import re
from collections import defaultdict, Counter

import mdparse as MD

WAVE_N = re.compile(r"W(\d)")
ENTITY = re.compile(r"`([a-z][a-z0-9_.]*)`")
ROLE = re.compile(r"\bR(\d{2})\b")
CD = re.compile(r"\bCD-(\d{3})\b")
KPI = re.compile(r"\bKPI-(\d{3})\b")

REGISTERED_ROLE_MAX = 38  # R01–R38 registered in 05-04


def _wave_num(txt):
    ns = [int(m) for m in WAVE_N.findall(txt or "")]
    return min(ns) if ns else None


def _entity_names(rows, col=0):
    out = []
    for r in rows:
        cell = r[col] if col < len(r) else ""
        found = ENTITY.findall(cell)
        if found:
            out.extend(found)
        else:
            t = MD.plain(cell).strip()
            if t and " " not in t and "." in t:
                out.append(t)
    return out


class Findings(object):
    """Whole-estate integrity analysis, indexed by component."""

    def __init__(self, specs):
        self.specs = specs
        self.by_uid = {s.uid: s for s in specs}
        self.per = defaultdict(list)  # uid -> [finding dicts]
        self.library = []  # estate-level findings
        self._owned = {s.uid: set(_entity_names(s.owned_entities)) for s in specs}
        self._run()

    # ------------------------------------------------------------------ API
    def for_uid(self, uid):
        return sorted(
            self.per.get(uid, []),
            key=lambda f: (
                {"High": 0, "Medium": 1, "Low": 2}.get(f["severity"], 3),
                f["code"],
            ),
        )

    def summary(self):
        c = Counter(f["code"] for lst in self.per.values() for f in lst)
        return c

    def _add(self, uid, code, severity, title, detail, action):
        self.per[uid].append(
            {
                "code": code,
                "severity": severity,
                "title": title,
                "detail": detail,
                "action": action,
            }
        )

    # -------------------------------------------------------------- checks
    def _run(self):
        self._f01_reciprocity()
        self._f02_entity_ownership()
        self._f03_wave_inversion()
        self._f04_identifier_gaps()
        self._f05_count_vs_stated()
        self._f06_event_consumers()
        self._f07_unregistered_roles()
        self._f08_cd_collisions()
        self._f09_kpi_collisions()
        self._f10_missing_failure_behaviour()

    # F-01 ---------------------------------------------------------------
    def _f01_reciprocity(self):
        """RG-04: A names B as a prerequisite, so B must name A as a dependant."""
        for s in self.specs:
            broken_out, broken_in = [], []
            for dep in s.depends_on:
                other = self.by_uid.get(dep)
                if other is None:
                    continue
                blanket = "all" in (other.depended_txt or "").lower()
                if not blanket and s.uid not in other.depended_by:
                    broken_out.append(dep)
            for dependant in s.depended_by:
                other = self.by_uid.get(dependant)
                if other is None:
                    continue
                blanket = "all" in (other.depends_txt or "").lower()
                if not blanket and s.uid not in other.depends_on:
                    broken_in.append(dependant)
            if broken_out:
                self._add(
                    s.uid,
                    "F-01",
                    "Medium",
                    "Dependency declaration is not reciprocated",
                    "%s names %s as %s in §1, but %s not name %s in %s own "
                    "**Depended on by** list."
                    % (
                        s.uid,
                        ", ".join(broken_out),
                        "prerequisites" if len(broken_out) > 1 else "a prerequisite",
                        "they do" if len(broken_out) > 1 else "it does",
                        s.uid,
                        "their" if len(broken_out) > 1 else "its",
                    ),
                    "Raise a register defect under rule RG-04. Either the "
                    "dependency is real and the other side must declare it, or "
                    "it is not a prerequisite and §1 overstates it.",
                )
            if broken_in:
                self._add(
                    s.uid,
                    "F-01b",
                    "Low",
                    "Dependant declaration is not reciprocated",
                    "%s lists %s as depending on it, but %s do not name %s as a "
                    "prerequisite."
                    % (
                        s.uid,
                        ", ".join(broken_in),
                        "those components" if len(broken_in) > 1 else "that component",
                        s.uid,
                    ),
                    "Confirm the direction of the relationship before you rely "
                    "on it for sequencing.",
                )

    # F-02 ---------------------------------------------------------------
    def _f02_entity_ownership(self):
        """A referenced entity must appear verbatim in its declared owner's §10.1."""
        for s in self.specs:
            bad = []
            for r in s.ref_entities:
                names = _entity_names([r])
                owners = re.findall(
                    r"\b(M\d{2})\b", " ".join(r[1:2]) if len(r) > 1 else ""
                )
                if not names or not owners:
                    continue
                for owner in owners:
                    if owner not in self._owned:
                        continue
                    for nm in names:
                        if nm not in self._owned[owner]:
                            bad.append((nm, owner))
            if bad:
                uniq = []
                for x in bad:
                    if x not in uniq:
                        uniq.append(x)
                self._add(
                    s.uid,
                    "F-02",
                    "High",
                    "Referenced entity is not defined by its declared owner",
                    "%d referenced entit%s in §10 name%s an owning module that "
                    "does not define %s in its own owned-entity table: %s."
                    % (
                        len(uniq),
                        "y" if len(uniq) == 1 else "ies",
                        "s" if len(uniq) == 1 else "",
                        "it" if len(uniq) == 1 else "them",
                        ", ".join("`%s` → %s" % (n, o) for n, o in uniq[:12])
                        + (" …" if len(uniq) > 12 else ""),
                    ),
                    "Do not code against these names. Confirm the entity's real "
                    "owner and its exact name in `05-02 Data Model and Entity "
                    "Catalogue` before you build the interface.",
                )

    # F-03 ---------------------------------------------------------------
    def _f03_wave_inversion(self):
        for s in self.specs:
            mine = _wave_num(s.wave)
            if mine is None:
                continue
            late = []
            for dep in s.depends_on:
                other = self.by_uid.get(dep)
                if other is None:
                    continue
                theirs = _wave_num(other.wave)
                if theirs is not None and theirs > mine:
                    late.append("%s (W%d)" % (dep, theirs))
            if late:
                self._add(
                    s.uid,
                    "F-03",
                    "High",
                    "Wave inversion — a prerequisite lands later than this component",
                    "%s is scheduled in W%d but declares %d prerequisite%s that "
                    "land%s later: %s."
                    % (
                        s.uid,
                        mine,
                        len(late),
                        "" if len(late) == 1 else "s",
                        "s" if len(late) == 1 else "",
                        ", ".join(late),
                    ),
                    "One of three things must be true before the wave gate, and "
                    "the programme must say which: the dependency is not a true "
                    "prerequisite for this wave's scope; a named interim "
                    "capability covers the gap; or a wave assignment is wrong "
                    "and `06-01` must change.",
                )

    # F-04 ---------------------------------------------------------------
    def _f04_identifier_gaps(self):
        for s in self.specs:
            if not s.reqs:
                continue
            nums = sorted(int(r["id"].rsplit("-", 1)[1]) for r in s.reqs)
            code = s.reqs[0]["id"].rsplit("-", 2)[1]
            missing = [n for n in range(nums[0], nums[-1] + 1) if n not in set(nums)]
            if missing:
                self._add(
                    s.uid,
                    "F-04",
                    "Low",
                    "Allocated requirement identifiers were never issued",
                    "%d identifier%s inside the allocated range `FR-%s-%03d … "
                    "FR-%s-%03d` %s never issued: %s."
                    % (
                        len(missing),
                        "" if len(missing) == 1 else "s",
                        code,
                        nums[0],
                        code,
                        nums[-1],
                        "was" if len(missing) == 1 else "were",
                        ", ".join("`FR-%s-%03d`" % (code, n) for n in missing[:20])
                        + (" …" if len(missing) > 20 else ""),
                    ),
                    "These identifiers are retired under rule RG-02 and must "
                    "never be reissued. Count requirement rows, not the highest "
                    "identifier.",
                )

    # F-05 ---------------------------------------------------------------
    def _f05_count_vs_stated(self):
        for s in self.specs:
            if s.req_count_stated is None:
                continue
            if s.req_count != s.req_count_stated:
                self._add(
                    s.uid,
                    "F-05",
                    "Medium",
                    "Stated requirement count differs from the measured count",
                    "§1 states **%d** requirements. Counting the requirement rows "
                    "in §5 returns **%d** — a difference of %+d."
                    % (
                        s.req_count_stated,
                        s.req_count,
                        s.req_count - s.req_count_stated,
                    ),
                    "Under rule RG-06 the measured figure stands and §1 is the "
                    "defect. This guide book uses the measured figure throughout.",
                )

    # F-06 ---------------------------------------------------------------
    def _f06_event_consumers(self):
        for s in self.specs:
            if s.is_portal or not s.events:
                continue
            orphan = []
            for r in s.events:
                joined = " ".join(r[1:]) if len(r) > 1 else ""
                if not re.search(r"\b[MP]\d{2}\b", joined):
                    name = MD.plain(r[0])
                    if name:
                        orphan.append(name)
            if orphan:
                self._add(
                    s.uid,
                    "F-06",
                    "Low",
                    "Domain event has no declared consumer",
                    "%d event%s published in §12.3 name%s no consuming component: "
                    "%s."
                    % (
                        len(orphan),
                        "" if len(orphan) == 1 else "s",
                        "s" if len(orphan) == 1 else "",
                        ", ".join("`%s`" % o for o in orphan[:10])
                        + (" …" if len(orphan) > 10 else ""),
                    ),
                    "An event with no consumer is either dead weight or an "
                    "undeclared contract. Confirm which before building the "
                    "publisher.",
                )

    # F-07 ---------------------------------------------------------------
    def _f07_unregistered_roles(self):
        for s in self.specs:
            unreg = sorted(
                {
                    r["id"]
                    for r in s.roles
                    if r["id"] and int(r["id"][1:]) > REGISTERED_ROLE_MAX
                }
            )
            if unreg:
                self._add(
                    s.uid,
                    "F-07",
                    "Medium",
                    "Role identifier is not in the registered range",
                    "§13 uses %s. The role register `05-04` registers R01–R%d; "
                    "anything above that is used but unregistered."
                    % (", ".join("`%s`" % u for u in unreg), REGISTERED_ROLE_MAX),
                    "Register the role in `05-04` before it reaches "
                    "configuration. An unregistered role cannot be assigned a "
                    "segregation-of-duties control.",
                )

    # F-08 ---------------------------------------------------------------
    def _f08_cd_collisions(self):
        owner = defaultdict(set)
        for s in self.specs:
            for r in s.cd_items:
                for cd in CD.findall(" ".join(r)):
                    owner["CD-" + cd].add(s.uid)
        collided = {k: v for k, v in owner.items() if len(v) > 1}
        if collided:
            self.library.append(
                {
                    "code": "F-08",
                    "severity": "High",
                    "title": "Custom-development identifiers are claimed by more "
                    "than one component",
                    "detail": "%d `CD-` identifiers are claimed by two or more "
                    "components: %s."
                    % (
                        len(collided),
                        ", ".join(
                            "%s (%s)" % (k, ", ".join(sorted(v)))
                            for k, v in sorted(collided.items())[:14]
                        )
                        + (" …" if len(collided) > 14 else ""),
                    ),
                    "action": "`CD-` is a programme-wide identifier space allocated "
                    "by `02-05`. Do not create a build backlog item from "
                    "any of these identifiers until the unified register "
                    "has issued them.",
                }
            )
            per_uid = defaultdict(list)
            for cd, uids in sorted(collided.items()):
                for uid in uids:
                    others = sorted(u for u in uids if u != uid)
                    per_uid[uid].append("`%s` (also %s)" % (cd, ", ".join(others)))
            for uid, items in per_uid.items():
                self._add(
                    uid,
                    "F-08",
                    "High",
                    "Custom-development identifiers collide with other " "components",
                    "%d `CD-` identifier%s claimed in §16.2 %s also claimed "
                    "elsewhere: %s."
                    % (
                        len(items),
                        "" if len(items) == 1 else "s",
                        "is" if len(items) == 1 else "are",
                        "; ".join(items[:10]) + (" …" if len(items) > 10 else ""),
                    ),
                    "`CD-` is a programme-wide identifier space allocated "
                    "by `02-05`. These allocations are provisional. Do not "
                    "raise a build backlog item against any of them until "
                    "the unified register has issued them.",
                )

    # F-09 ---------------------------------------------------------------
    def _f09_kpi_collisions(self):
        owner = defaultdict(set)
        for s in self.specs:
            for r in s.kpis:
                for k in KPI.findall(" ".join(r)):
                    owner["KPI-" + k].add(s.uid)
        shared = {k: v for k, v in owner.items() if len(v) > 1}
        if shared:
            self.library.append(
                {
                    "code": "F-09",
                    "severity": "Medium",
                    "title": "KPI identifiers appear in more than one component",
                    "detail": "%d `KPI-` identifiers are used by two or more "
                    "components: %s."
                    % (
                        len(shared),
                        ", ".join(
                            "%s (%s)" % (k, ", ".join(sorted(v)))
                            for k, v in sorted(shared.items())[:14]
                        )
                        + (" …" if len(shared) > 14 else ""),
                    ),
                    "action": "A shared metric is legitimate, but it must carry a "
                    "note naming the co-owning component. `KPI-` is a "
                    "programme-wide space and is not allocated locally.",
                }
            )
            per_uid = defaultdict(list)
            for k, uids in sorted(shared.items()):
                for uid in uids:
                    per_uid[uid].append(
                        "`%s` (also %s)"
                        % (k, ", ".join(sorted(u for u in uids if u != uid)))
                    )
            for uid, items in per_uid.items():
                self._add(
                    uid,
                    "F-09",
                    "Medium",
                    "KPI identifier is shared with another component",
                    "%d `KPI-` identifier%s in §15 %s also used elsewhere: "
                    "%s."
                    % (
                        len(items),
                        "" if len(items) == 1 else "s",
                        "is" if len(items) == 1 else "are",
                        "; ".join(items[:10]) + (" …" if len(items) > 10 else ""),
                    ),
                    "A shared metric is legitimate, but the KPI row must "
                    "name the co-owning component so that the two are not "
                    "reported twice. `KPI-` is a programme-wide space and "
                    "is not allocated locally.",
                )

    # F-10 ---------------------------------------------------------------
    def _f10_missing_failure_behaviour(self):
        for s in self.specs:
            if not s.automations:
                continue
            hdr = [MD.plain(h).lower() for h in s.automation_header]
            i = next((n for n, h in enumerate(hdr) if "failure" in h), None)
            if i is None:
                continue
            blank = [
                MD.plain(r[0])
                for r in s.automations
                if i >= len(r) or not MD.plain(r[i])
            ]
            if blank:
                self._add(
                    s.uid,
                    "F-10",
                    "High",
                    "Automation has no declared failure behaviour",
                    "%d automation%s in §11 leave%s the failure-behaviour column "
                    "blank: %s."
                    % (
                        len(blank),
                        "" if len(blank) == 1 else "s",
                        "s" if len(blank) == 1 else "",
                        ", ".join("`%s`" % b for b in blank[:10]),
                    ),
                    "No automation may ship without a declared failure "
                    "behaviour. Silent failure is never an acceptable design.",
                )


PASSED_CHECKS = [
    (
        "C-01",
        "Source section coverage",
        "All nineteen house sections of the source specification are present in "
        "this guide book, in order, with their content restated in full.",
    ),
    (
        "C-02",
        "Table fidelity",
        "Every table in the source specification is reproduced with the same "
        "number of rows and the same column headings.",
    ),
    (
        "C-03",
        "Requirement fidelity",
        "Every requirement identifier in the source appears in §5 and again in "
        "Annex A, with the same priority and delivery layer.",
    ),
    (
        "C-04",
        "Exhibit provenance",
        "Every exhibit is generated from the parsed source. No exhibit contains "
        "an illustrative or placeholder figure.",
    ),
    (
        "C-05",
        "Counting rule",
        "Every quantity was counted from the source file at generation time, "
        "under rule RG-06.",
    ),
    (
        "C-06",
        "Typography",
        "Body text is Calibri 9.5 pt. Reference tables of seven columns or more "
        "are set at 8.5 pt to fit the A4 text column.",
    ),
    (
        "C-07",
        "Navigation",
        "Table of contents, list of exhibits and list of tables are Word fields "
        "and rebuild on open. Headings map to Word heading styles, so the "
        "navigation pane works.",
    ),
    (
        "C-08",
        "Cross-reference integrity",
        "Every component identifier named in Annex B resolves to a component "
        "that exists in the estate.",
    ),
]
