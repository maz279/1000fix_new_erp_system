# -*- coding: utf-8 -*-
"""
spec — the analytical model of one module or portal specification.

Reads a source specification, parses it, and derives every fact the guide
book needs: requirement inventory by area / priority / delivery layer,
business-rule classification, entity ownership, automation register,
interface surface, role matrix, KPI set, delivery layer allocation,
custom-development backlog, dependency graph edges and state models.

Everything here is *measured from the source file*, never restated from a
register — the same "count, do not consult" discipline the programme's own
rule RG-06 imposes.
"""

import os
import re
from collections import OrderedDict, Counter

import mdparse as MD

RE_FR = re.compile(r"\bFR-([A-Z0-9]{2,5})-(\d{3})\b")
RE_BRU = re.compile(r"\bBRU-([A-Z0-9]{2,5})-(\d{2,3})\b")
RE_AUT = re.compile(r"\bAUT-([A-Z0-9]{2,5})-(\d{2,3})\b")
RE_MOD = re.compile(r"\bM(\d{2})\b")
RE_POR = re.compile(r"\bP(\d{2})\b")
RE_ROLE = re.compile(r"\bR(\d{2})\b")
RE_LAYER = re.compile(r"\bL([1-6])\b")
RE_PRI = re.compile(r"\bP([0-3])\b")
RE_WAVE = re.compile(r"\bW([1-9])\b")
RE_PCT = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")
RE_PW = re.compile(r"(\d+(?:\.\d+)?)\s*(?:PW|person[- ]weeks?)", re.I)


def _norm(s):
    return MD.plain(s).strip()


class Spec(object):
    # -------------------------------------------------------------- loading
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
        self.fm, body = MD.parse_frontmatter(raw)
        self.blocks = MD.parse_blocks(body)
        self.sections = MD.sectionise(self.blocks)
        self.by_num = {s["num"]: s for s in self.sections if s["num"] is not None}
        self.preamble = next((s for s in self.sections if s["num"] is None), None)
        self.raw = raw
        self._derive()

    def sec(self, num):
        return self.by_num.get(num, {"num": num, "title": "", "blocks": []})

    def sec_blocks(self, num):
        return self.sec(num)["blocks"]

    def sec_title(self, num):
        return self.sec(num).get("title", "")

    def subsections(self, num):
        """OrderedDict of '<n>.<m> Title' -> [blocks] for one section.

        Deterministic: the house structure numbers every sub-heading, so the
        sub-heading is a far more reliable key than sniffing table headers.
        Blocks appearing before the first '###' are filed under key ''.
        """
        out = OrderedDict()
        key = ""
        out[key] = []
        for b in self.sec_blocks(num):
            if b["t"] == "h" and b["level"] == 3:
                key = _norm(b["text"])
                out.setdefault(key, [])
            else:
                out[key].append(b)
        return out

    def sub(self, num, *needles):
        """Blocks of the first sub-section whose title matches a needle.

        A needle of the form '12.1' matches the sub-section number; any other
        needle is matched case-insensitively against the title text.
        """
        subs = self.subsections(num)
        for needle in needles:
            n = needle.lower()
            for title, blocks in subs.items():
                tl = title.lower()
                if re.match(r"^\d+\.\d+", n):
                    if tl.startswith(n):
                        return blocks
                elif n in tl:
                    return blocks
        return []

    @staticmethod
    def _first_table(blocks):
        for b in blocks:
            if b["t"] == "table":
                return b
        return None

    def sub_table(self, num, *needles):
        return self._first_table(self.sub(num, *needles))

    # ------------------------------------------------------------- identity
    def _derive(self):
        fm = self.fm
        self.is_portal = "portal_id" in fm or bool(re.match(r"^P\d\d", self.filename))
        self.uid = (
            fm.get("module_id") or fm.get("portal_id") or self.filename.split("_")[0]
        )
        self.code = (fm.get("module_code") or fm.get("portal_code") or "").strip("` ")
        self.name = (fm.get("module_name") or fm.get("portal_name") or "").strip()
        if not self.name:
            h1 = next(
                (b for b in self.blocks if b["t"] == "h" and b["level"] == 1), None
            )
            if h1:
                t = _norm(h1["text"])
                self.name = re.sub(r"^[MP]\d\d\s*[—-]\s*", "", t)
        self.category_raw = fm.get("category", "")
        m = re.match(r"^([A-K])\b", self.category_raw.strip())
        self.category = m.group(1) if m else ("P" if self.is_portal else "K")
        self.category_name = re.sub(r"^[A-K]\s*[—-]\s*", "", self.category_raw).strip()
        self.version = fm.get("version", "1.0")
        self.date = fm.get("date", "")
        self.status = fm.get("status", "DRAFT FOR APPROVAL")
        self.business_owner = fm.get("business_owner", "")
        self.system_owner = fm.get("system_owner", "")
        self.priority = fm.get("priority", "").strip() or "P2"
        self.wave = fm.get("wave", "").strip()
        self.classification = fm.get(
            "classification", "CONFIDENTIAL — Internal Use Only"
        )

        self._identity_table()
        self._scope()
        self._benchmark()
        self._requirements()
        self._technical()
        self._benefits()
        self._states()
        self._rules()
        self._entities()
        self._automations()
        self._interfaces()
        self._roles()
        self._reports()
        self._kpis()
        self._delivery()
        self._acceptance()
        self._questions()
        self._deps()

    # ------------------------------------------------------- §1  identity
    def _identity_table(self):
        self.identity = OrderedDict()
        t = MD.find_table(self.sec_blocks(1), "attribute", "value", min_hits=1)
        if t:
            for r in t["rows"]:
                if len(r) >= 2 and _norm(r[0]):
                    self.identity[_norm(r[0])] = _norm(r[1])
        get = lambda *k: next(
            (
                v
                for kk, v in self.identity.items()
                if any(x.lower() in kk.lower() for x in k)
            ),
            "",
        )
        self.effort_txt = get("Effort")
        m = RE_PW.search(self.effort_txt)
        self.effort_pw = float(m.group(1)) if m else None
        self.req_count_txt = get("Requirement count")
        m = re.search(r"(\d+)", self.req_count_txt)
        self.req_count_stated = int(m.group(1)) if m else None
        self.req_range = get("Requirement range")
        self.custom_modules = get("Custom modules")
        self.delivery_layers_txt = get("Delivery layers")
        self.status_txt = get("Status") or self.status
        if not self.business_owner:
            self.business_owner = get("Business owner")
        if not self.system_owner:
            self.system_owner = get("System owner")
        if not self.wave:
            self.wave = get("Delivery wave", "Wave")
        self.depends_txt = get("Depends on")
        self.depended_txt = get("Depended on by", "Depended on")
        self.users_txt = get("Primary users", "Users")
        self.tech_txt = get("Technology", "Platform")

    # ---------------------------------------------------------- §2 purpose
    def purpose_paragraphs(self):
        return [b for b in self.sec_blocks(2) if b["t"] == "p"]

    def one_liner(self):
        ps = self.purpose_paragraphs()
        if not ps:
            return ""
        txt = MD.plain(ps[0]["text"])
        parts = re.split(r"(?<=[.!?])\s+", txt)
        out = parts[0] if parts else txt
        if len(out) < 60 and len(parts) > 1:
            out = out + " " + parts[1]
        return out.strip()

    def evidence_rows(self):
        t = MD.find_table(
            self.sec_blocks(2), "source", "what it establishes", min_hits=1
        )
        return t["rows"] if t else []

    # ----------------------------------------------------------- §3 scope
    def _scope(self):
        self.in_scope, self.out_scope, self.shared = [], [], []
        self.in_header, self.out_header, self.shared_header = [], [], []
        for key, attr, hattr in (
            ("3.1", "in_scope", "in_header"),
            ("3.2", "out_scope", "out_header"),
            ("3.3", "shared", "shared_header"),
        ):
            t = self.sub_table(3, key)
            if t:
                setattr(self, attr, t["rows"])
                setattr(self, hattr, t["header"])
        if not self.in_scope:
            for tb in MD.tables_in(self.sec_blocks(3)):
                hdr = " | ".join(_norm(h).lower() for h in tb["header"])
                if "owned by" in hdr or "why the boundary" in hdr:
                    self.out_scope, self.out_header = tb["rows"], tb["header"]
                elif "owning" in hdr:
                    self.shared, self.shared_header = tb["rows"], tb["header"]
                elif "capability" in hdr and not self.in_scope:
                    self.in_scope, self.in_header = tb["rows"], tb["header"]

    # ------------------------------------------------------- §4 benchmark
    def _benchmark(self):
        t = MD.find_table(
            self.sec_blocks(4), "reference system", "equivalent capability", min_hits=1
        )
        self.benchmark = t["rows"] if t else []
        self.benchmark_header = t["header"] if t else []
        self.design_position = [b for b in self.sec_blocks(4) if b["t"] == "p"]

    # ---------------------------------------------------- §5 requirements
    def _requirements(self):
        self.areas = OrderedDict()  # area title -> list of req dicts
        self.reqs = []
        cur = self.name
        for b in self.sec_blocks(5):
            if b["t"] == "h" and b["level"] == 3:
                cur = re.sub(r"^\d+(\.\d+)*\s*", "", _norm(b["text"])).strip()
                self.areas.setdefault(cur, [])
            elif b["t"] == "table":
                hdr = " | ".join(_norm(h).lower() for h in b["header"])
                if "fr id" not in hdr and "fr-" not in hdr and "id" not in hdr:
                    continue
                ci_id = MD.col_index(b, "FR ID", "ID") or 0
                ci_feat = MD.col_index(b, "Feature", "Capability")
                ci_fn = MD.col_index(b, "Function", "The system shall")
                ci_pri = MD.col_index(b, "Pri", "Priority")
                ci_lay = MD.col_index(b, "Layer")
                self.areas.setdefault(cur, [])
                for r in b["rows"]:
                    rid = (
                        _norm(r[ci_id]) if ci_id is not None and ci_id < len(r) else ""
                    )
                    if not RE_FR.search(rid):
                        continue
                    pri = ""
                    if ci_pri is not None and ci_pri < len(r):
                        mp = RE_PRI.search(_norm(r[ci_pri]))
                        pri = "P" + mp.group(1) if mp else ""
                    lay = ""
                    if ci_lay is not None and ci_lay < len(r):
                        ml = RE_LAYER.search(_norm(r[ci_lay]))
                        lay = "L" + ml.group(1) if ml else ""
                    rec = {
                        "id": RE_FR.search(rid).group(0),
                        "area": cur,
                        "feature": _norm(r[ci_feat])
                        if ci_feat is not None and ci_feat < len(r)
                        else "",
                        "function": _norm(r[ci_fn])
                        if ci_fn is not None and ci_fn < len(r)
                        else "",
                        "pri": pri or self.priority,
                        "layer": lay or "L5",
                    }
                    self.areas[cur].append(rec)
                    self.reqs.append(rec)
        self.areas = OrderedDict((k, v) for k, v in self.areas.items() if v)
        self.req_count = len(self.reqs)
        self.pri_mix = Counter(r["pri"] for r in self.reqs)
        self.layer_mix = Counter(r["layer"] for r in self.reqs)
        self.area_mix = OrderedDict((k, len(v)) for k, v in self.areas.items())

    # ------------------------------------------------- §6 technical funcs
    def _technical(self):
        t = MD.find_table(
            self.sec_blocks(6), "technical function", "requirement", min_hits=1
        )
        self.tech_funcs = t["rows"] if t else []
        self.tech_header = t["header"] if t else []

    # ---------------------------------------------------- §7 benefits
    def _benefits(self):
        self.role_change, self.role_change_header = [], []
        self.quant_benefit, self.quant_header = [], []
        self.inst_benefit, self.inst_header = [], []
        for key, attr, hattr in (
            ("7.1", "role_change", "role_change_header"),
            ("7.2", "quant_benefit", "quant_header"),
            ("7.3", "inst_benefit", "inst_header"),
        ):
            t = self.sub_table(7, key)
            if t:
                setattr(self, attr, t["rows"])
                setattr(self, hattr, t["header"])
        if not self.role_change:
            for tb in MD.tables_in(self.sec_blocks(7)):
                hdr = " | ".join(_norm(h).lower() for h in tb["header"])
                if "today" in hdr:
                    self.role_change, self.role_change_header = tb["rows"], tb["header"]
                elif "why it matters" in hdr:
                    self.inst_benefit, self.inst_header = tb["rows"], tb["header"]
                elif "mechanism" in hdr or "value" in hdr:
                    self.quant_benefit, self.quant_header = tb["rows"], tb["header"]

    # ------------------------------------------------------- §8 lifecycle
    def _states(self):
        b = self.sec_blocks(8)
        self.state_models = []
        cur_title = "Lifecycle"
        for blk in b:
            if blk["t"] == "h" and blk["level"] == 3:
                cur_title = re.sub(r"^\d+(\.\d+)*\s*", "", _norm(blk["text"])).strip()
            elif blk["t"] == "code":
                self.state_models.append({"title": cur_title, "lines": blk["lines"]})
        t = MD.find_table(b, "guard", "from", "to", min_hits=2)
        self.transitions = t["rows"] if t else []
        self.transitions_header = t["header"] if t else []

    # ----------------------------------------------------------- §9 rules
    def _rules(self):
        t = MD.find_table(self.sec_blocks(9), "rule", "class", min_hits=2)
        self.rules = []
        if t:
            ci_id = MD.col_index(t, "ID") or 0
            ci_rule = MD.col_index(t, "Rule")
            ci_cls = MD.col_index(t, "Class")
            ci_own = MD.col_index(t, "Owner")
            for r in t["rows"]:
                cls = ""
                if ci_cls is not None and ci_cls < len(r):
                    mc = re.search(r"\b([HASC])\b", _norm(r[ci_cls]))
                    cls = mc.group(1) if mc else ""
                self.rules.append(
                    {
                        "id": _norm(r[ci_id]) if ci_id < len(r) else "",
                        "rule": _norm(r[ci_rule])
                        if ci_rule is not None and ci_rule < len(r)
                        else "",
                        "class": cls,
                        "owner": _norm(r[ci_own])
                        if ci_own is not None and ci_own < len(r)
                        else "",
                    }
                )
        self.rule_mix = Counter(r["class"] for r in self.rules if r["class"])

    # -------------------------------------------------------- §10 entities
    def _entities(self):
        self.owned_entities, self.ref_entities = [], []
        self.owned_header, self.ref_header = [], []
        self.client_state, self.client_state_header = [], []
        self.never_held, self.never_held_header = [], []

        t = self.sub_table(10, "10.1", "owned entit")
        if t and not self.is_portal:
            self.owned_entities, self.owned_header = t["rows"], t["header"]

        if self.is_portal:
            t1 = self.sub_table(10, "10.1", "client-side state", "permitted")
            if t1:
                self.client_state, self.client_state_header = t1["rows"], t1["header"]
            t2 = self.sub_table(10, "10.2", "never held")
            if t2:
                self.never_held, self.never_held_header = t2["rows"], t2["header"]
            t3 = self.sub_table(10, "10.3", "referenced entit")
            if t3:
                self.ref_entities, self.ref_header = t3["rows"], t3["header"]
        else:
            t3 = self.sub_table(10, "10.2", "referenced entit")
            if t3:
                self.ref_entities, self.ref_header = t3["rows"], t3["header"]

        # Fallback for any file whose sub-headings are absent.
        if not self.owned_entities and not self.is_portal:
            for tb in MD.tables_in(self.sec_blocks(10)):
                hdr = " | ".join(_norm(h).lower() for h in tb["header"])
                if "owned by" in hdr or "access pattern" in hdr:
                    if not self.ref_entities:
                        self.ref_entities, self.ref_header = tb["rows"], tb["header"]
                elif "entity" in hdr and not self.owned_entities:
                    self.owned_entities, self.owned_header = tb["rows"], tb["header"]

    # ----------------------------------------------------- §11 automations
    def _automations(self):
        t = MD.find_table(self.sec_blocks(11), "trigger", "action", min_hits=1)
        self.automations = t["rows"] if t else []
        self.automation_header = t["header"] if t else []

    # ------------------------------------------------------ §12 interfaces
    def _interfaces(self):
        """Parsed by sub-section number, which the house structure fixes.

        Modules: 12.1 consumes · 12.2 provides · 12.3 events published ·
                 12.4 external integrations · 12.5 API surface.
        Portals: 12.1 modules consumed · 12.2 writes back ·
                 12.3 events consumed · 12.4 external · 12.5 API / contract.
        """
        subs = self.subsections(12)
        titles = list(subs.keys())

        def by_num(prefix):
            for t in titles:
                if t.lower().startswith(prefix):
                    return self._first_table(subs[t])
            return None

        def pack(tbl):
            return (tbl["rows"], tbl["header"]) if tbl else ([], [])

        self.upstream, self.up_header = pack(by_num("12.1"))
        self.downstream, self.down_header = pack(by_num("12.2"))
        self.events, self.events_header = pack(by_num("12.3"))
        self.externals, self.ext_header = pack(by_num("12.4"))
        self.api, self.api_header = pack(by_num("12.5"))

        # Some files carry a sixth sub-section; fold anything API-shaped in.
        if not self.api:
            for t in titles:
                tb = self._first_table(subs[t])
                if not tb:
                    continue
                hdr = " | ".join(_norm(h).lower() for h in tb["header"])
                if "endpoint" in hdr and "method" in hdr:
                    self.api, self.api_header = tb["rows"], tb["header"]
                    break
        if not self.externals:
            for t in titles:
                tb = self._first_table(subs[t])
                if not tb:
                    continue
                hdr = " | ".join(_norm(h).lower() for h in tb["header"])
                if "int id" in hdr or ("direction" in hdr and "system" in hdr):
                    self.externals, self.ext_header = tb["rows"], tb["header"]
                    break
        self.iface_subtitles = {
            t: len(self._first_table(subs[t])["rows"])
            for t in titles
            if self._first_table(subs[t]) is not None
        }

    # ----------------------------------------------------------- §13 roles
    def _roles(self):
        t = MD.find_table(self.sec_blocks(13), "role", "access", min_hits=1)
        self.roles = []
        if t:
            ci_r = MD.col_index(t, "Role") or 0
            ci_a = MD.col_index(t, "Access")
            ci_s = MD.col_index(t, "Scope")
            for r in t["rows"]:
                nm = _norm(r[ci_r]) if ci_r < len(r) else ""
                if not nm:
                    continue
                acc = _norm(r[ci_a]) if ci_a is not None and ci_a < len(r) else ""
                self.roles.append(
                    {
                        "id": (
                            RE_ROLE.search(nm).group(0) if RE_ROLE.search(nm) else ""
                        ),
                        "name": re.sub(r"^R\d\d\s*", "", nm),
                        "access": acc,
                        "perms": set(
                            re.findall(r"[CRUDA]", acc.upper().replace("—", ""))
                        ),
                        "scope": _norm(r[ci_s])
                        if ci_s is not None and ci_s < len(r)
                        else "",
                    }
                )
        self.role_notes = [b for b in self.sec_blocks(13) if b["t"] == "p"]

    # --------------------------------------------------------- §14 reports
    def _reports(self):
        t = MD.find_table(self.sec_blocks(14), "audience", min_hits=1)
        self.reports = t["rows"] if t else []
        self.reports_header = t["header"] if t else []

    # ------------------------------------------------------------ §15 KPIs
    def _kpis(self):
        t = MD.find_table(self.sec_blocks(15), "kpi", "metric", min_hits=1)
        self.kpis = t["rows"] if t else []
        self.kpis_header = t["header"] if t else []

    # -------------------------------------------------------- §16 delivery
    def _delivery(self):
        self.layer_alloc = OrderedDict()
        self.layer_rows, self.layer_header = [], []
        self.cd_items, self.cd_header = [], []
        self.sequencing, self.seq_header = [], []
        self.migration, self.mig_header = [], []

        t = self.sub_table(16, "16.1", "layer allocation", "technology & layer")
        if t is None:
            t = MD.find_table(self.sec_blocks(16), "layer", "coverage", min_hits=2)
        if t:
            self.layer_rows, self.layer_header = t["rows"], t["header"]
            for r in t["rows"]:
                label = _norm(r[0])
                layers = ["L" + d for d in re.findall(r"L(\d)", label)]
                if not layers:
                    continue
                pct = None
                for c in r[1:]:
                    mp = RE_PCT.search(_norm(c))
                    if mp:
                        pct = float(mp.group(1))
                share = (pct / len(layers)) if pct is not None else None
                comp = _norm(r[1]) if len(r) > 1 else ""
                for L in layers:
                    cur = self.layer_alloc.setdefault(
                        L, {"component": comp, "pct": 0.0, "parts": []}
                    )
                    if share is not None:
                        cur["pct"] = (cur["pct"] or 0.0) + share
                    if comp and comp not in cur["parts"]:
                        cur["parts"].append(comp)
        # normalise: drop zero-valued placeholders, order L1..L6
        self.layer_alloc = OrderedDict(
            (k, self.layer_alloc[k])
            for k in sorted(self.layer_alloc, key=lambda x: x)
            if self.layer_alloc[k]
        )
        self.layer_total_pct = sum(
            (v.get("pct") or 0.0) for v in self.layer_alloc.values()
        )

        t = self.sub_table(16, "16.2", "custom development")
        if t:
            self.cd_items, self.cd_header = t["rows"], t["header"]
        t = self.sub_table(16, "16.3", "sequencing")
        if t:
            self.sequencing, self.seq_header = t["rows"], t["header"]
        t = self.sub_table(16, "16.4", "data migration")
        if t:
            self.migration, self.mig_header = t["rows"], t["header"]

        self.cd_effort = 0.0
        for r in self.cd_items:
            for c in r:
                m = RE_PW.search(_norm(c))
                if m:
                    self.cd_effort += float(m.group(1))
                    break

    # ------------------------------------------------------ §17 acceptance
    def _acceptance(self):
        t = MD.find_table(self.sec_blocks(17), "criterion", min_hits=1)
        self.acceptance = t["rows"] if t else []
        self.acceptance_header = t["header"] if t else []

    # ------------------------------------------------------- §18 questions
    def _questions(self):
        t = MD.find_table(self.sec_blocks(18), "question", min_hits=1)
        self.questions = t["rows"] if t else []
        self.questions_header = t["header"] if t else []

    # ------------------------------------------------------ dependency edges
    def _deps(self):
        def ids(txt, rx, pre):
            return sorted({pre + m for m in rx.findall(txt or "")})

        self.depends_on = ids(self.depends_txt, RE_MOD, "M")
        self.depended_by = ids(self.depended_txt, RE_MOD, "M")
        self.depends_on_portals = ids(self.depends_txt, RE_POR, "P")
        self.depended_by_portals = ids(self.depended_txt, RE_POR, "P")

        up = set()
        for r in self.upstream:
            up |= {"M" + m for m in RE_MOD.findall(" ".join(r))}
            up |= {"P" + m for m in RE_POR.findall(" ".join(r))}
        dn = set()
        for r in self.downstream:
            dn |= {"M" + m for m in RE_MOD.findall(" ".join(r))}
            dn |= {"P" + m for m in RE_POR.findall(" ".join(r))}
        ev = set()
        for r in self.events:
            ev |= {"M" + m for m in RE_MOD.findall(" ".join(r))}
            ev |= {"P" + m for m in RE_POR.findall(" ".join(r))}
        self.iface_up = sorted(up - {self.uid})
        self.iface_down = sorted(dn - {self.uid})
        self.event_consumers = sorted(ev - {self.uid})

        allrefs = set(RE_MOD.findall(self.raw))
        self.mentions = sorted({"M" + m for m in allrefs} - {self.uid})
        self.mentions_portals = sorted(
            {"P" + m for m in RE_POR.findall(self.raw)} - {self.uid}
        )

        self.waves = sorted({"W" + w for w in RE_WAVE.findall(self.wave or "")})

    # --------------------------------------------------------------- totals
    def scorecard(self):
        if self.is_portal:
            return OrderedDict(
                [
                    ("Functional requirements", self.req_count),
                    ("Capability areas", len(self.areas)),
                    ("Portal rules", len(self.rules)),
                    ("Automations & notifications", len(self.automations)),
                    ("Modules consumed", len(self.upstream)),
                    ("Write-back targets", len(self.downstream)),
                    ("Events subscribed", len(self.events)),
                    ("Referenced entities", len(self.ref_entities)),
                    ("Roles served", len(self.roles)),
                    ("KPIs", len(self.kpis)),
                    ("Acceptance criteria", len(self.acceptance)),
                    ("Open questions", len(self.questions)),
                ]
            )
        return OrderedDict(
            [
                ("Functional requirements", self.req_count),
                ("Functional areas", len(self.areas)),
                ("Business rules", len(self.rules)),
                ("Automations", len(self.automations)),
                ("Owned entities", len(self.owned_entities)),
                ("Referenced entities", len(self.ref_entities)),
                ("Domain events published", len(self.events)),
                ("API endpoints", len(self.api)),
                ("Roles with access", len(self.roles)),
                ("Reports & dashboards", len(self.reports)),
                ("KPIs", len(self.kpis)),
                ("Acceptance criteria", len(self.acceptance)),
            ]
        )

    def __repr__(self):
        return "<Spec %s %s reqs=%d>" % (self.uid, self.name, self.req_count)
