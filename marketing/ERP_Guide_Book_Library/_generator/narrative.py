# -*- coding: utf-8 -*-
"""
narrative — the authored, non-derived text of the guide-book library.

Two kinds of text live here:

  * **Framing text** — the guide-book scaffolding that turns a specification
    into a teaching document: what each section is for, how to read it, who
    it is written for. Authored once, applied to all 79 guide books.

  * **Derived sentences** — short statements assembled from measured
    specification data. These are templates with slots, never assertions
    invented about a module. If the data is not there, the sentence is not
    written.
"""
import re
from collections import Counter

import mdparse as MD

# =========================================================== section framing
# What each of the 19 house sections answers, and why an SPSL reader
# should care. Keyed by section number; 'm' = module, 'p' = portal.
SECTION_FRAME = {
    1: {
        "part": 1,
        "m": ("Identity",
              "The registry entry for this module: its permanent identifier, who owns it on "
              "the business side and who owns it in engineering, when it is scheduled, how "
              "large it is, and which other modules it cannot function without. Read this "
              "first, and read nothing else in the guide book until the wave and the "
              "dependency list make sense to you.",
              "Everything in this table is governed. Module IDs and module codes are "
              "permanent under register rule RG-02 — a module may be renamed or re-scoped, "
              "but its identifier never changes and is never reused."),
        "p": ("Identity",
              "The registry entry for this portal: its permanent identifier, the population "
              "it serves, the technology it is built in, when it is scheduled, and which "
              "modules stand behind it. A portal is a surface, never a system of record — "
              "the modules named here hold the truth it displays.",
              "Portal IDs are permanent. A portal never owns business state and never "
              "implements a business rule; both belong to the module that owns the object."),
    },
    2: {
        "part": 1,
        "m": ("Purpose",
              "Why this module exists at all, written for a reader who has to explain it to "
              "someone else — a branch manager, an auditor, a new joiner. The evidence table "
              "at the end traces every claim to a workspace document, so nothing in this "
              "section rests on opinion.",
              "If you can only take one thing from this guide book into a meeting, take the "
              "first paragraph of this section."),
        "p": ("Purpose",
              "Why this portal exists, who it is for, and what changes for that population "
              "on the day it goes live. The evidence table traces every claim to a workspace "
              "document.",
              "A portal earns its place by removing work from a channel that costs more — a "
              "hotline call, a counter visit, an email thread. That is the test this section "
              "answers."),
    },
    3: {
        "part": 1,
        "m": ("Scope boundary",
              "The anti-overlap control. §3.1 states what this module does; §3.2 states what "
              "it deliberately does not do and names the module that does it instead; §3.3 "
              "names the concepts it shares with other modules and its role in each.",
              "Boundary symmetry is a governed rule (RG-04): if this module declares a "
              "capability out of scope and owned elsewhere, the owning module must claim it. "
              "A boundary that only one side agrees to is a defect, and it is the single most "
              "common cause of duplicated build effort."),
        "p": ("Scope boundary",
              "What this portal presents, what it deliberately refuses to hold, and which "
              "module owns each concept it touches. For a portal the out-of-scope list is the "
              "more important half: it is what stops a surface quietly becoming a second "
              "system of record.",
              "If a capability is not listed in §3.1, do not build it into this portal — "
              "raise it as a change against the owning module first."),
    },
    4: {
        "part": 1,
        "m": ("Benchmark basis",
              "What the equivalent capability looks like in SAP S/4HANA, Oracle Fusion Cloud, "
              "Microsoft Dynamics 365, IFS Cloud, Odoo 19 and the specialist after-sales "
              "platforms — and, for each, what 1000FiX adopted and what it rejected.",
              "The rejections matter as much as the adoptions. Where this module differs from "
              "the benchmark it is almost always for one of four reasons: Bangladesh "
              "regulatory context, cost discipline, Bengali-first interfaces, or field "
              "conditions. The design position paragraph says which."),
        "p": ("Benchmark basis",
              "How comparable portals behave in enterprise suites and in consumer products, "
              "and what this design took from each. Portals are benchmarked against consumer "
              "software as well as enterprise software, because that is what their users "
              "compare them to.",
              "Where the design departs from the enterprise benchmark, the design position "
              "paragraph states why."),
    },
    5: {
        "part": 2,
        "m": ("Functional areas and features",
              "The requirement inventory — every function the module must perform, grouped "
              "into functional areas, each with a permanent identifier, a priority and the "
              "delivery layer it will be built in. This is the section a developer estimates "
              "from and a tester writes cases against.",
              "Every requirement is written to be independently testable. A requirement you "
              "cannot write a pass/fail test for is a defect in the requirement, not in the "
              "test — raise it."),
        "p": ("Capability areas and functions",
              "The requirement inventory for the portal — every function it must perform, "
              "grouped by capability area, each with a permanent identifier, a priority and "
              "the delivery layer.",
              "Portal requirements describe what the surface does, never what the underlying "
              "rule is. Where you find a rule here rather than a presentation behaviour, it "
              "belongs in the owning module."),
    },
    6: {
        "part": 2,
        "m": ("Technical functions",
              "The engineering behaviours the module must exhibit that no user will ever see "
              "and every operator will eventually depend on: idempotency, concurrency "
              "control, the transactional outbox, the performance envelope.",
              "These are the requirements that decide whether the module survives production. "
              "They are not optional and they are not 'non-functional nice-to-haves'."),
        "p": ("Technical functions",
              "The engineering behaviours the portal must exhibit: offline capability, sync "
              "integrity, payload budgets, device envelope, accessibility conformance.",
              "For field applications these constraints are harder than the functional "
              "requirements. A feature that cannot work on a mid-range Android handset on a "
              "3G connection is not delivered."),
    },
    7: {
        "part": 2,
        "m": ("Business value",
              "What changes for each role on the day this module goes live, the quantified "
              "benefit where a baseline exists, and the institutional benefits that do not "
              "reduce to money.",
              "Where no baseline has been measured the specification says so and states no "
              "number. That is deliberate: an absolute target against an unmeasured baseline "
              "cannot be assessed as met or missed."),
        "p": ("Business value",
              "What changes for each population the portal serves, the quantified benefit "
              "where a baseline exists, and the benefits that do not reduce to money.",
              "Adoption is the benefit mechanism for every portal. A portal nobody uses "
              "delivers none of the value below, however complete its feature list."),
    },
    8: {
        "part": 3,
        "m": ("Lifecycle and state model",
              "The state machine for the objects this module owns, and the guards on every "
              "transition — who may make it and what must be true first.",
              "State models are contracts. A transition that is not in this section must not "
              "be possible in the built system, and a transition that is here must be "
              "reachable and testable."),
        "p": ("User journeys and state models",
              "The journeys this portal supports end to end, and the states a journey can be "
              "in. Portal state is presentation state; the authoritative state lives in the "
              "backing module.",
              "Where a journey can be abandoned, resumed, or completed on a different device, "
              "that behaviour is specified here rather than left to the implementation."),
    },
    9: {
        "part": 3,
        "m": ("Business rules",
              "The rules the system enforces, each classified by how it behaves when it is "
              "broken: a hard block, an override that requires approval, a soft warning, or a "
              "computed consequence.",
              "The classification is the important column. A hard block that ships as a soft "
              "warning is a control failure, and it will be found in audit rather than in "
              "testing."),
        "p": ("Portal rules",
              "The rules that constrain what this portal may do, each classified by how it "
              "behaves when it is broken.",
              "Most portal rules are prohibitions — what the surface must never hold, show, "
              "or decide. Treat them as security requirements, not as guidance."),
    },
    10: {
        "part": 3,
        "m": ("Data entities",
              "The entities this module owns and is the single authority for, and the "
              "entities it reads from other modules.",
              "One entity, one owner. If you need to write to an entity in the referenced "
              "table, you call the owning module's interface — you do not write to its "
              "table. This rule is what makes the estate maintainable."),
        "p": ("Data, caching and state",
              "What this portal may hold on the client, for how long, what it must never "
              "hold, and which module owns each entity it reads.",
              "A portal may cache for performance. It may never cache for truth. Every cached "
              "object in the permitted table names the module it can be rebuilt from."),
    },
    11: {
        "part": 3,
        "m": ("Automations",
              "Everything the system does without being asked: the trigger, the action, and — "
              "the column that matters most — what happens when the automation fails.",
              "No automation ships without a declared failure behaviour. Silent failure is "
              "the worst outcome available and it is never an acceptable design."),
        "p": ("Automations and notifications",
              "What this portal does on its own, and what it does when the thing it depends "
              "on is unavailable.",
              "Fail closed and visible. A portal that silently drops a notification has "
              "created a support call it will never be connected to."),
    },
    12: {
        "part": 4,
        "m": ("Interfaces",
              "The complete integration surface: what this module consumes, what it provides, "
              "the domain events it publishes, its external integrations and its API.",
              "Contract symmetry is governed. Every event another module declares it consumes "
              "must appear in the publishing module's event table, and every event published "
              "should have at least one declared consumer."),
        "p": ("Module interfaces",
              "Which modules this portal reads, what it writes back, which events it "
              "subscribes to, and the external services it touches.",
              "Every call goes through the M28 gateway and authenticates through M29. There "
              "is no second path, and a portal that opens one is a security finding."),
    },
    13: {
        "part": 4,
        "m": ("Roles and permissions",
              "Who can do what, at what scope, together with field-level restrictions and the "
              "combinations of duties that must never sit with one person.",
              "Segregation of duties entries are audit-visible controls. Where this section "
              "names an incompatible combination, the system enforces it — configuration "
              "cannot be allowed to undo it."),
        "p": ("Roles and permissions",
              "Which roles reach this portal, what each may do, and at what scope.",
              "Portal permissions are a projection of module permissions, never an addition "
              "to them. A portal cannot grant an access the owning module withholds."),
    },
    14: {
        "part": 5,
        "m": ("Reports and analytics",
              "The reports and dashboards this module produces, who reads them and how often.",
              "Every report here has a named audience. A report with no named audience is a "
              "maintenance liability and should be challenged before it is built."),
        "p": ("Analytics and instrumentation",
              "What this portal measures about its own use, and who reads it.",
              "Instrumentation is a functional requirement for a portal, not an afterthought. "
              "Adoption, task completion and error rate are the three that decide whether the "
              "investment paid."),
    },
    15: {
        "part": 5,
        "m": ("Key performance indicators",
              "The measures this module is accountable for, with baseline and wave targets.",
              "Where the baseline reads 'unmeasured', measuring it is itself a delivery task "
              "and it belongs in the wave that precedes the target."),
        "p": ("Key performance indicators",
              "The measures this portal is accountable for, with baseline and targets.",
              "Adoption first, then task completion, then satisfaction. A portal that scores "
              "well on satisfaction and poorly on adoption has not succeeded."),
    },
    16: {
        "part": 5,
        "m": ("Delivery",
              "How the module will actually be built: the split across the six delivery "
              "layers, the custom development backlog, what must be finished first, and what "
              "data has to be migrated.",
              "The layer allocation is the cost model. Every percentage point moved from L5 "
              "custom development into L1 or L2 is effort the programme does not have to "
              "fund, and every point moved the other way is effort it must."),
        "p": ("Delivery",
              "How the portal will be built: the technology and layer split, the custom "
              "development backlog, prerequisites and sequencing.",
              "Portals are overwhelmingly custom by design. That is a deliberate position: no "
              "ERP portal framework produces an experience that wins against the consumer "
              "software these users compare it to."),
    },
    17: {
        "part": 5,
        "m": ("Acceptance criteria",
              "What has to be demonstrably true before this module is accepted, and the "
              "evidence that will be produced for each criterion.",
              "Acceptance criteria are written before the build, not after it. If a criterion "
              "cannot be evidenced, it is not a criterion."),
        "p": ("Acceptance criteria",
              "What has to be demonstrably true before this portal is accepted, and the "
              "evidence for each.",
              "For portals, acceptance is measured on real devices and real networks, not in "
              "an emulator on the office wi-fi."),
    },
    18: {
        "part": 5,
        "m": ("Open questions",
              "What is genuinely undecided, who has to decide it, and by when.",
              "An open question with no named owner and no needed-by date is not open — it is "
              "abandoned. Treat every row here as a live action."),
        "p": ("Open questions",
              "What is genuinely undecided about this portal, who decides, and by when.",
              "Portal questions frequently turn on decisions owned by a backing module. Where "
              "that is the case, the question is answered there, not here."),
    },
    19: {
        "part": 5,
        "m": ("References",
              "The internal documents, workspace evidence and external benchmarks this "
              "specification relies on.",
              "Verify a path before you cite it. Nine module files carried references to "
              "superseded filenames until the August 2026 audit corrected them."),
        "p": ("References",
              "The internal documents, workspace evidence and external benchmarks this "
              "specification relies on.",
              "Verify a path before you cite it."),
    },
}

PARTS = {
    1: ("Part One", "Orientation",
        "What this component is, why it exists, where its boundary sits, and how it "
        "compares with the enterprise systems it was benchmarked against."),
    2: ("Part Two", "What it does",
        "The complete inventory of functions and features, the engineering behaviours "
        "beneath them, and the value the business gets in return."),
    3: ("Part Three", "How it behaves",
        "Lifecycle and state, the rules the system enforces, the data it owns, and "
        "everything it does without being asked."),
    4: ("Part Four", "How it connects",
        "The integration surface with every other module and portal in the estate, and "
        "who is permitted to do what."),
    5: ("Part Five", "How it is measured and delivered",
        "Reporting, performance indicators, the build plan across the six delivery "
        "layers, acceptance, and what remains undecided."),
}


# ============================================================ reading paths
READING_PATHS = [
    ("Business analyst / functional consultant",
     "§2 Purpose · §3 Scope boundary · §5 Functional areas · §7 Business value · §9 Business rules",
     "You are establishing what the business is buying and where the edges are."),
    ("Solution architect",
     "§1 Identity · §3 Scope boundary · §10 Data entities · §12 Interfaces · §16 Delivery",
     "You are checking ownership, contracts and the layer split before anything is committed."),
    ("Developer",
     "§5 Functional areas · §6 Technical functions · §8 Lifecycle · §10 Data entities · "
     "§11 Automations · §12 Interfaces · §16.2 Custom development",
     "You are building against identifiers. Everything you need to estimate is in these sections."),
    ("Test engineer / QA",
     "§5 Functional areas · §8 Lifecycle · §9 Business rules · §13 Roles · §17 Acceptance criteria",
     "Every requirement is independently testable; every rule has a declared enforcement class."),
    ("Implementation and data lead",
     "§10 Data entities · §16.3 Sequencing · §16.4 Data migration · §17 Acceptance criteria",
     "You are planning cutover. The migration table is the smallest and the most underestimated."),
    ("Trainer and change lead",
     "§2 Purpose · §7.1 What changes for each role · §8 Lifecycle · §13 Roles · Annex D",
     "Annex D is the one-page card to put in front of an end user."),
    ("Support and service desk",
     "§8 Lifecycle · §9 Business rules · §11 Automations · §13 Roles · Annex C Glossary",
     "Most support calls resolve to a rule that fired or a state that has not advanced."),
    ("Project manager / delivery lead",
     "§1 Identity · §7.2 Quantified benefit · §15 KPIs · §16 Delivery · §18 Open questions",
     "Wave, effort, prerequisites and unresolved decisions, in that order."),
]


CONVENTIONS = [
    ("Priority", "P0", "Blocking. Cannot be descoped; the programme does not go live without it."),
    ("Priority", "P1", "Must have. Inside the committed scope for its wave."),
    ("Priority", "P2", "Important. Planned, and deferrable under schedule pressure."),
    ("Priority", "P3", "Desirable. Delivered if capacity allows."),
    ("Rule class", "H", "Hard block. The system refuses the action. No override exists."),
    ("Rule class", "A", "Approved override. The action is refused unless a named role approves it."),
    ("Rule class", "S", "Soft warning. The user is warned and may proceed."),
    ("Rule class", "C", "Computed. The system derives the outcome; there is nothing to override."),
    ("Delivery layer", "L1", "Odoo 19 Community Edition — standard product, zero licence cost."),
    ("Delivery layer", "L2", "OCA community modules — 140+ modules across 18 repositories."),
    ("Delivery layer", "L3", "Free third-party Odoo modules."),
    ("Delivery layer", "L4", "Standalone open-source systems integrated alongside the ERP."),
    ("Delivery layer", "L5", "Custom development — Odoo modules, services and applications built for 1000FiX."),
    ("Delivery layer", "L6", "Commercial component, used only where no viable open source exists."),
    ("Access", "C R U D A", "Create · Read · Update · Delete · Approve."),
    ("Identifier", "FR-<CODE>-nnn", "Functional requirement. Module-local, permanent, never reissued."),
    ("Identifier", "BRU-<CODE>-nn", "Business rule. Module-local."),
    ("Identifier", "AUT-<CODE>-nn", "Automation. Module-local."),
    ("Identifier", "KPI-nnn · CD-nnn · R nn · SOD-nn · NFR-nnn",
     "Programme-wide. Allocated centrally; cited here, never invented here."),
    ("Wave", "W1 … W9", "Delivery wave across the 36-month programme."),
]


CALLOUT_LEGEND = [
    ("NOTE", "Context that helps you read the section correctly."),
    ("IN PRACTICE", "How this behaves on the ground, in a branch or in the field."),
    ("TAKE CARE", "A known trap. Something that is commonly got wrong."),
    ("OPEN RISK", "An unresolved exposure carried forward from the specification."),
    ("AUDIT FINDING", "A defect raised by one of the three 2026 documentation audits."),
    ("RULE", "A governed rule of the programme. Not negotiable at project level."),
    ("CONFIRMED", "A figure or a statement verified by direct measurement."),
]


# ==================================================== derived, data-backed text
def five_things(sp):
    """Headline facts, each assembled only from what the source actually states."""
    out = []
    pri_word = {"P0": "blocking — it cannot be descoped",
                "P1": "a must-have inside its wave",
                "P2": "important but deferrable under schedule pressure",
                "P3": "desirable, delivered if capacity allows"}
    pw = sp.priority if sp.priority in pri_word else "P2"
    wave = sp.wave or "an unassigned wave"
    out.append(
        "**It is %s, and it lands in %s.** %s carries %d functional requirement%s across "
        "%d %s area%s."
        % (pri_word[pw], wave, sp.uid, sp.req_count, "" if sp.req_count == 1 else "s",
           len(sp.areas), "capability" if sp.is_portal else "functional",
           "" if len(sp.areas) == 1 else "s"))

    if sp.is_portal:
        n = len(sp.ref_entities)
        out.append(
            "**It owns no data.** %s reads %d entit%s owned by other modules and writes "
            "back through %d command interface%s. Every figure it shows can be rebuilt "
            "from the module that owns it."
            % (sp.uid, n, "y" if n == 1 else "ies", len(sp.downstream),
               "" if len(sp.downstream) == 1 else "s"))
    else:
        names = _entity_names(sp.owned_entities)[:3]
        tail = (" — including %s" % ", ".join("`%s`" % n for n in names)) if names else ""
        out.append(
            "**It is the single authority for %d entit%s%s.** No other module writes to "
            "them; they are reached through this module's interface or not at all."
            % (len(sp.owned_entities),
               "y" if len(sp.owned_entities) == 1 else "ies", tail))

    hard = sp.rule_mix.get("H", 0)
    if sp.rules:
        out.append(
            "**%d of its %d rule%s %s hard block%s.** The system refuses the action "
            "outright; there is no override path and no configuration switch that removes it."
            % (hard, len(sp.rules), "" if len(sp.rules) == 1 else "s",
               "is a" if hard == 1 else "are", "" if hard == 1 else "s")
            if hard else
            "**None of its %d rule%s is a hard block.** Every rule is an approved override, "
            "a soft warning or a computed consequence — this component constrains behaviour "
            "without ever refusing an action outright."
            % (len(sp.rules), "" if len(sp.rules) == 1 else "s"))

    deps = sp.depends_on or sp.iface_up
    if deps:
        shown = deps[:5]
        rest = len(deps) - len(shown)
        listed = ", ".join(shown) + (" and %d further module%s"
                                     % (rest, "" if rest == 1 else "s")
                                     if rest else "")
        out.append(
            "**It cannot stand up on its own.** %d module%s %s named as a prerequisite — "
            "%s. Each must be live, or credibly stubbed with a defined retirement date, "
            "before this component does anything useful."
            % (len(deps), "" if len(deps) == 1 else "s",
               "is" if len(deps) == 1 else "are", listed))

    if sp.layer_alloc:
        l5 = (sp.layer_alloc.get("L5", {}).get("pct") or 0.0)
        std = sum((sp.layer_alloc.get(k, {}).get("pct") or 0.0) for k in ("L1", "L2", "L3"))
        if l5 >= 65:
            out.append(
                "**It is a build, not a configuration.** %.0f%% of the delivery is custom "
                "development (L5) against %.0f%% standard product and community modules. "
                "Plan the effort accordingly." % (l5, std))
        elif std >= 45:
            out.append(
                "**Most of it already exists.** %.0f%% comes from Odoo 19 Community, OCA "
                "modules and free third-party modules, with %.0f%% custom development. "
                "The risk here is over-customising what the product already does."
                % (std, l5))
        else:
            out.append(
                "**The build splits roughly evenly.** %.0f%% custom development against "
                "%.0f%% standard product and community modules." % (l5, std))
    return out[:5]


def _entity_names(rows):
    names = []
    for r in rows:
        m = re.findall(r"`([^`]+)`", r[0] if r else "")
        if m:
            names.extend(m)
        else:
            t = MD.plain(r[0]) if r else ""
            if t:
                names.append(t)
    return names


def daily_roles(sp):
    """Roles that create or update, i.e. the people in the system every day."""
    out = []
    for r in sp.roles:
        if {"C", "U"} & r["perms"]:
            out.append(("%s %s" % (r.get("id", ""), r["name"])).strip())
    return out


def read_only_roles(sp):
    out = []
    for r in sp.roles:
        if r["perms"] and not ({"C", "U", "D"} & r["perms"]):
            out.append(("%s %s" % (r.get("id", ""), r["name"])).strip())
    return out


def approvers(sp):
    return [("%s %s" % (r.get("id", ""), r["name"])).strip()
            for r in sp.roles if "A" in r["perms"]]


def boundary_owners(sp):
    c = Counter()
    for r in sp.out_scope:
        joined = " ".join(r[1:2]) if len(r) > 1 else " ".join(r)
        for m in re.findall(r"\bM\d{2}\b", joined):
            c[m] += 1
    return c.most_common()


def relationship_register(sp, catalogue):
    """Every other component this one names, with the nature of the link."""
    rel = {}

    def mark(ids, kind):
        for i in ids:
            rel.setdefault(i, set()).add(kind)

    mark(sp.depends_on + sp.depends_on_portals, "Declared prerequisite")
    mark(sp.depended_by + sp.depended_by_portals, "Declared dependant")
    mark(sp.iface_up, "Consumed interface")
    mark(sp.iface_down, "Provided interface")
    mark(sp.event_consumers, "Event contract")
    for r in sp.ref_entities:
        joined = " ".join(r[1:2]) if len(r) > 1 else " ".join(r)
        for m in re.findall(r"\b[MP]\d{2}\b", joined):
            rel.setdefault(m, set()).add("Referenced data owner")
    for m, _n in boundary_owners(sp):
        rel.setdefault(m, set()).add("Boundary counterparty")

    rows = []
    for uid in sorted(rel):
        if uid == sp.uid:
            continue
        meta = catalogue.get(uid)
        rows.append((uid,
                     meta["name"] if meta else "—",
                     (meta["category"] + " · " + meta["cat_name"]) if meta else "—",
                     " · ".join(sorted(rel[uid]))))
    return rows


def glossary_terms(sp, catalogue):
    """Module and portal codes actually used in this document, plus house terms."""
    used = sorted(set(sp.mentions + sp.mentions_portals +
                      sp.depends_on + sp.depended_by))
    rows = []
    for uid in used:
        meta = catalogue.get(uid)
        if meta:
            rows.append((uid, meta["name"],
                         "Category %s — %s" % (meta["category"], meta["cat_name"])))
    return rows


HOUSE_GLOSSARY = [
    ("AMC / RAMC", "Annual Maintenance Contract / Renewable Annual Maintenance Contract — the "
                   "recurring service agreements sold to corporate and government clients."),
    ("BDT", "Bangladeshi Taka."),
    ("BRD / URD / RFP", "Business Requirements Document · User Requirements Document · Request "
                        "for Proposal. The three primary workspace documents this specification traces to."),
    ("CAPA", "Corrective and Preventive Action — the quality response to a non-conformance."),
    ("CD-nnn", "Custom development item. Programme-wide identifier allocated by the technology "
               "stack document, not by a module."),
    ("Domain event", "An immutable statement that something happened, published by the module "
                     "that owns the object, consumed by anyone who needs to react."),
    ("Idempotency", "The property that performing the same operation twice has the same effect "
                    "as performing it once. Essential wherever a field device retries."),
    ("ISO 9001:2015", "The quality management standard 1000FiX is certified against — the only "
                      "IT service provider in Bangladesh that is."),
    ("NCR", "Non-Conformance Report."),
    ("NFR-nnn", "Non-functional requirement. Programme-wide; cited by modules, never invented "
                "by them."),
    ("OCA", "Odoo Community Association — the body that maintains the community module "
            "repositories used at delivery layer L2."),
    ("PDPA 2026", "Bangladesh Personal Data Protection Act 2026. Governs consent, transparency "
                  "notices, data residency and retention for personal data."),
    ("PW", "Person-week of build effort."),
    ("RG-01 … RG-06", "Register governance rules. RG-06 — 'count, do not consult' — requires "
                      "every figure describing repository content to be measured at the time of "
                      "writing rather than restated from a register."),
    ("SLA / OLA", "Service Level Agreement with a customer · Operational Level Agreement between "
                  "internal teams."),
    ("SOD-nn", "Segregation of duties control. Names a combination of duties one person may not hold."),
    ("Transactional outbox", "The pattern that writes a domain event in the same database "
                             "transaction as the state change it describes, so the two cannot diverge."),
    ("TAT", "Turnaround time — elapsed time from intake to the device being ready for collection."),
    ("Wave", "One of nine delivery increments across the 36-month programme."),
]
