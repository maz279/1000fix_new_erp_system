---
id: OP-006
title: Release Notes Standard and Wave Note Set
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Office with Content Design
author: Content Design with Programme Office and Platform Engineering
reviewers: [Content Design Lead, Chief Technology Officer, Programme Manager, Support Lead, L&D Lead, Change Lead, Localisation Lead, QA Lead]
approver: Programme Manager
content_class: C
purpose: >
  Fixes what a release note contains, who receives which version of it, when it is issued and what
  makes a change "action required" rather than informational — and sets out the note for each of
  the nine waves. Nine waves of change land in a live system used by 800+ staff and eleven
  external populations; a user who cannot see what changed concludes the system broke, raises a
  ticket, and stops trusting the next change.
traces_to: [06-01, M30, M66, SP-031, OP-001, OP-002, OP-011, TR-024, CM-005, CM-009, CG-006, HC-016, AP-011]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md — nine waves, scope and months
    verified: 2026-08-20
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md §3 — standard, normal and emergency change definitions
    verified: 2026-08-20
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md §3 — content pinned to the release that consumes it
    verified: 2026-08-20
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md — release-triggered refresher training
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-008 zero-downtime deployment standard; OPS-01 deployments automated, repeatable and reversible; OPS-06 feature flags
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# OP-006 — Release Notes Standard and Wave Note Set

> **A release note is the difference between "they improved it" and "it broke".** The change is
> the same; only the note decides which one the user experiences.

---

## 1. Purpose

Over 36 months this programme deploys nine waves, 67 modules and 12 portals into a system that
people are using while it changes underneath them. `OPS-01` makes every deployment automated and
reversible and `NFR-008` makes zero downtime the standard — which means **most changes arrive with
no visible signal at all**. A user who was not told is not neutral; they are confused, and confusion
routes to the service desk.

**What stops without this file:**

| Absent | Consequence |
|---|---|
| A standard | Every squad writes notes in its own format, at its own length, at its own time. Users stop reading them within two waves |
| Audience segmentation | A technician receives 40 lines about warehouse valuation and stops opening the note that also contains the one line that affects their shift |
| An "action required" rule | Changes that need the user to do something look identical to changes that do not |
| A training trigger | [`TR-024`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) has no reliable signal for when a refresher is needed |
| A wave note set | Each of the nine launches is improvised in the week it happens, which is the week nobody has time |
| A record of what shipped when | [`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) cannot pin content to a release; screenshots and instructions drift silently out of date |

---

## 2. Scope

**In scope:** the release note standard (structure, tone, length, taxonomy); audience
segmentation; release types and their notice periods; the "action required" definition; the
distribution model; the wave-level note set for W1–W9; hotfix and emergency-change notes;
deprecation and removal notices; and the measurement of whether notes are read and understood.

**Out of scope:**

| Situation | Owned by |
|---|---|
| The change process, CAB, approval and rollback | [`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) |
| Mobile store release mechanics, staged rollout, forced upgrade | [`OP-011`](OP-011_Runbook_Portal_and_Mobile_App_Operations.md) |
| Planned-maintenance notices and windows | [`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) |
| Training content built from a release | `TR-024` |
| Wave launch campaigns and the change story | [`CM-005`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md), [`CM-001`](../16_Change_Management_and_Comms/CM-001_Programme_Narrative_and_Change_Story.md) |
| API deprecation notices to integration partners | [`AP-011`](../15_Integration_and_Developer_Content/AP-011_Integration_Change_Deprecation_and_Notice_Content.md) |
| Content re-pinning triggered by a release | `CG-006` §3 |
| Help-centre article updates | [`HC-016`](../09_Help_Centre_and_Self_Service/HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| Squad leads and release managers | Produce the note that ships with their release |
| Content Design | Edit notes to the standard before publication |
| Support Lead | Anticipate contact volume and prepare macros ([`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md)) |
| L&D | Trigger refreshers from `Action required` items (`TR-024`) |
| Change Lead | Align wave notes with the launch kit (`CM-005`) |
| Branch managers and champions | Brief their site on what changed |
| Account managers | Tell corporate clients what changed in their portal |
| Auditors | Trace a production change to an approved change record and a published note |

---

## 4. Content

### 4.1 Release types and notice periods

| Type | Definition (`SP-031` §3) | Note required | Notice period | Approver |
|---|---|:--:|---|---|
| **Configuration change** | Pre-approved standard change; no code | Only if user-visible | Same day | Domain owner |
| **Weekly release** | Routine fixes and small changes | ✔ | Published on release day | Release manager |
| **Sprint release** | Feature-bearing, every 2–3 weeks | ✔ | 3 working days ahead for `Action required` items | Release manager + Content Design |
| **Wave release** | A delivery wave going live | ✔ **wave note set** (§4.7) | 10 working days ahead | Programme Manager |
| **Hotfix** | Fix to a live defect, out of cycle | ✔ short form | At deployment | Change manager |
| **Emergency change** | Restores or protects service | ✔ short form, retrospective | Within 1 working day of the change | Incident Commander, reviewed in 2 working days |
| **Mobile app release** | Store-distributed (`OP-011`) | ✔ | Per staged-rollout schedule | Mobile lead |
| **Removal / deprecation** | A capability is withdrawn | ✔ **deprecation notice** | **30 calendar days** minimum | Programme Manager |

### 4.2 The note structure

Every note, at every level, uses these sections in this order. Sections with nothing in them are
**omitted, not left empty** — an empty "Fixed" heading trains people to skim.

| # | Section | Rule |
|---:|---|---|
| 1 | **What this affects** | Named audiences and portals, first, before any detail. A reader must be able to stop after this line if it is not them |
| 2 | **Action required** | Only genuine actions. If empty, the note says "No action needed" explicitly — that sentence is the most-read line in any note |
| 3 | **New** | Capability that did not exist. One line each, in the user's language, with a link to guidance |
| 4 | **Changed** | Something that behaves differently. **Always states the before and the after** |
| 5 | **Fixed** | Defects users reported or noticed. References the symptom, not the code |
| 6 | **Removed** | With the date it was announced and what to use instead |
| 7 | **Known issues** | Carried from [`OP-002`](OP-002_Hypercare_Plan_and_Exit_Criteria.md) §4.6 with the workaround |
| 8 | **Where to get help** | The route from [`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) §4.3 for that audience |

**Length limits.** Weekly note: 1 screen. Sprint note: 2 screens. Wave note: 4 screens plus
per-audience extracts. A note longer than its limit is edited, not extended.

### 4.3 The "action required" definition

The most abused label in release communication. A change is **Action required** only if one of
these is true:

| # | Condition |
|---|---|
| **AR-01** | The user must do something before a date, or something they rely on stops working |
| **AR-02** | A task the user performs regularly now has different steps, a different screen, or a different result |
| **AR-03** | A number, status or label the user reads has changed meaning |
| **AR-04** | The user must install or update something (`OP-011`) |
| **AR-05** | A control, approval or authority limit affecting the user has changed |
| **AR-06** | Data the user owns must be checked or corrected |

Anything else is **New**, **Changed** or **Fixed** — informational. Marking an informational item
as `Action required` costs the label its meaning; the first squad to do it makes every later note
weaker.

**Every `Action required` item automatically:**
- triggers a `TR-024` refresher assessment within 2 working days;
- generates a macro review in `OP-003` (will support be asked about this?);
- is listed in the wave launch kit if it lands in a wave (`CM-005`);
- is repeated in the note for the **next two releases**, because people miss the first one.

### 4.4 Audience segmentation

One release produces one master note and **eight audience extracts**, generated from the same
items by tagging, never rewritten separately (`CP-01`).

| Extract | Audience | Includes items tagged | Channel |
|---|---|---|---|
| `REL-INT-OPS` | Branch, front desk, dispatch, workshop | `P03`, `M01`–`M04`, master data | In-app notice + champion briefing |
| `REL-INT-FIELD` | Technicians, riders, auditors | `P02`, `P09`, `P11`, offline, sync | **In-app only** — field staff do not read email |
| `REL-INT-FIN` | Finance, cashiers | `M19`–`M21`, tax, invoicing, payments | Email + finance forum |
| `REL-INT-SCM` | Warehouse, procurement, logistics | `M15`–`M18`, `M42` | Email |
| `REL-INT-HR` | HR, payroll | `M21`, `M22`, `M57` | Email |
| `REL-INT-ADMIN` | System administrators, `R33` | Configuration, permissions, integrations | Email + `P03` console banner |
| `REL-EXT-CUST` | Consumers | `P01` visible changes only | In-app "what's new" card |
| `REL-EXT-PARTNER` | Corporate, sellers, vendors, brands, partners | Their portal only | Portal banner + account manager for corporate |

> **`SG-01`.** An audience extract that would contain no items is **not sent**. Sending "nothing
> changed for you" every week is how a channel dies.

### 4.5 Language

[`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2 places `OP-006` among the twelve English-only `OP` files, and the note *standard* is
correctly English — it is read by squads and Content Design.

**But the extracts are not.** `REL-INT-OPS` and `REL-INT-FIELD` reach branch staff and field
technicians, who are covered by the §3.3 audience rule ("if a person outside the programme's
English-working core will read it to do their job, it is bilingual").

**Resolution applied here:**

| Artefact | Language | Owner |
|---|---|---|
| This standard and the master note | English | Programme Office |
| `REL-INT-FIN`, `REL-INT-SCM`, `REL-INT-HR`, `REL-INT-ADMIN` | English | Programme Office |
| **`REL-INT-OPS`, `REL-INT-FIELD`, `REL-EXT-CUST`, `REL-EXT-PARTNER` (seller and referral)** | **Bengali and English** | Content Design + Localisation |
| Wave launch kit built from the wave note | Bengali and English (`CM-005`) | Change Lead |

This is a **declared departure** from the file-level `bilingual: no` flag: the file is English, four
of its outputs are not. It is recorded here rather than quietly resolved, and it is raised as a
finding in the Category 17 audit because `CG-010`'s per-file model cannot express it.

### 4.6 Templates

**Weekly / sprint note**

```
RELEASE {release_id} — {date}
Affects: {audiences}                                   Downtime: none / {window}

ACTION REQUIRED
  • {who} must {action} by {date}. Why: {reason}. How: {link}
  (or) No action needed.

NEW
  • {capability} — {one line}. {link}

CHANGED
  • {thing}: was {before}, now {after}. {why_it_matters}

FIXED
  • {symptom the user saw} ({defect_ref})

KNOWN ISSUES
  • {symptom} — until {target}, {workaround} ({issue_ref})

HELP: {route from OP-001 §4.3}
```

**Hotfix / emergency note**

```
HOTFIX {release_id} — deployed {time}
What was wrong: {symptom in user language}
Who was affected: {population} between {start} and {end}
What we changed: {plain fix}
What you should do: {action or "nothing"}
Related incident: {inc_ref}   Post-incident review: {pir_link}
```

**Deprecation notice**

```
{capability} WILL BE REMOVED ON {date}  ({days} days' notice)
Why: {reason}
Use instead: {replacement} — {link}
Who this affects: {population}, approximately {count} users
What happens if you do nothing: {consequence}
Questions: {route}
```

### 4.7 The wave note set

Each wave's note is drafted **at the start of the wave**, not at its end, and updated as scope
settles. The table below fixes what each note must cover and who receives it.

| Wave | Note ID | Headline for users | Mandatory `Action required` topics | Primary extracts |
|:--:|---|---|---|---|
| **W1** | `REL-W1` | The branch and admin system replaces the old way of recording jobs | Sign-in and MFA enrolment · new service-order references · paper forms withdrawn at pilot sites · master data ownership | `REL-INT-OPS`, `REL-INT-ADMIN` |
| **W2** | `REL-W2` | Customers can book online; technicians work in the app | Technician app install and enrolment · offline rules · customer booking channel change · tracking page | `REL-INT-FIELD`, `REL-EXT-CUST`, `REL-INT-OPS` |
| **W3** | `REL-W3` | Payments, logistics and vendor ordering move into the system | Payment method changes at counter · pick-and-drop custody scanning · vendor PO acknowledgement · bank reconciliation cut-off | `REL-INT-FIN`, `REL-INT-SCM`, `REL-EXT-PARTNER` |
| **W4** | `REL-W4` | Corporate clients, brands, the contact centre and dashboards go live | Corporate approval configuration · brand claim submission through the portal · hotline call handling in-system · report migration | `REL-EXT-PARTNER`, `REL-INT-OPS`, `REL-INT-FIN` |
| **W5** | `REL-W5` | Quality auditing, deeper finance and HR | Audit app use on site · month-end close steps · payroll run steps · statutory filing changes | `REL-INT-FIN`, `REL-INT-HR`, `REL-INT-OPS` |
| **W6** | `REL-W6` | Native apps, the assistant, and internal IT support moves into the system | New app versions (forced upgrade) · assistant limits and escalation · **service desk route changes as `M66` goes live** | `REL-INT-FIELD`, `REL-INT-ADMIN`, all internal |
| **W7** | `REL-W7` | Marketplace and partner network open | Seller onboarding and standards · referral attribution rules · payout timing | `REL-EXT-PARTNER` |
| **W8** | `REL-W8` | Scale and optimisation | Mostly none — performance and capacity. Any changed threshold that users can see | `REL-INT-ADMIN` |
| **W9** | `REL-W9` | Multi-entity and cross-border | Entity selection on transactions · residency handling of sensitive fields · currency and tax behaviour | `REL-INT-FIN`, `REL-INT-ADMIN` |

> **`WN-01`.** A wave note is published **10 working days before cutover**, repeated at cutover, and
> repeated once during hypercare. Three publications of the same note is not repetition; it is how
> 800+ people across 51+ sites actually receive something.

### 4.8 Distribution and timing

| Channel | Used for | Timing |
|---|---|---|
| In-app notice ([`UI-005`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md)) | All internal extracts | On first sign-in after release |
| In-app "what's new" card (`P01`, `P02`) | Customer and field extracts | On first open after update |
| Email | Function-specific extracts | Release day, 09:00 BST |
| Champion briefing ([`CM-008`](../16_Change_Management_and_Comms/CM-008_Champion_and_Super_User_Network_Kit.md)) | Ops and field extracts | 1 working day before release |
| Portal banner | External partner extracts | Release day |
| Knowledge base (`HC-016`, `KB`) | Permanent record and searchable history | Same day |
| Release archive | Every note, permanently | Same day |

**Rule `DT-01`:** nothing user-visible ships on a **Thursday after 15:00 BST or on a Friday**, so
that a problem surfaces while the people who can fix it are working. Bangladesh's Friday–Saturday
weekend makes this a Thursday constraint, not a Friday one — the inherited industry convention is
wrong here and must not be copied.

### 4.9 Quality rules

| # | Rule |
|---|---|
| **RN-01** | Every note is written **from the user's point of view**: what they can now do, not what was built |
| **RN-02** | **No internal identifiers** in a user-facing note — no `M`-numbers, no ticket numbers except a defect reference the user quoted, no module names |
| **RN-03** | Every `Changed` item states **before and after**. "Improved the estimate screen" is not a release note |
| **RN-04** | Every `Fixed` item names **the symptom the user saw**, not the cause |
| **RN-05** | No note claims a benefit it cannot evidence ("40% faster") without a source ([`CG-012`](../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md)) |
| **RN-06** | Notes are **edited by Content Design before publication** — squads draft, Content Design publishes |
| **RN-07** | A release with **no note** cannot be deployed to production. This is a deployment gate, not a courtesy (`OPS-01` discipline extended to communication) |
| **RN-08** | A note is never retro-edited after publication; corrections are issued as a new note referencing the old one |
| **RN-09** | Every note is archived and permanently addressable; `CG-006` pins content versions to these identifiers |

### 4.10 Measurement

| Measure | Definition | Target | Source |
|---|---|---|---|
| Note coverage | Releases with a published note ÷ all production releases | **100%** | Change register vs release archive |
| Timeliness | Notes published within the §4.1 notice period | ≥ 95% | Release archive |
| Read rate | Distinct users opening the in-app notice ÷ affected population | ≥ 50% internal, ≥ 20% customer | `M30` telemetry |
| Support correlation | Tickets in 72 h referencing a change that had no `Action required` label | ≤ 5 per release | Ticket system |
| Refresher trigger | `Action required` items with a `TR-024` decision recorded | 100% | L&D log |
| Deprecation compliance | Removals with ≥ 30 days' notice | **100%** | Change register |

### 4.11 Open decisions

| # | Decision required | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|
| **OP-006-OI-01** | Confirm the bilingual split in §4.5 with the Localisation Lead, and record it in `CG-010` | Localisation Lead + Content Design | W1 | The register says English-only; four extracts are not, and neither position is authoritative |
| **OP-006-OI-02** | `RN-07` (no note, no deploy) must be added to the deployment gate in the CI/CD pipeline, or it is an aspiration | CTO | W1 | The one rule that makes the standard self-enforcing is unenforced |
| **OP-006-OI-03** | Wave note ownership: Programme Office drafts, or the squad drafts and the Programme Office edits | Programme Manager | W1 | Wave notes are written by whoever notices, late |
| **OP-006-OI-04** | Confirm `DT-01`'s Thursday cut-off against the Bangladesh working week with Operations | Operations Director | W1 | Releases land into an unstaffed weekend |
| **OP-006-OI-05** | Read-rate telemetry (§4.10) requires per-user notice tracking in `M30`; confirm it exists | Platform Engineering | W2 | Three of six measures are unmeasurable |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `SP-031` | Change types, approval and the change record every note describes |
| `06-01` | Wave scope for the wave note set |
| `TR-024` | Consumes `Action required` items as refresher triggers |
| `CM-005`, `CM-008` | Wave launch kit and champion briefing carry the note to sites |
| `OP-011` | Mobile release mechanics for app-bearing notes |
| `OP-005` | Maintenance windows referenced in notes |
| `OP-002` | Known-issue log feeds section 7 of every note |
| `CG-006` §3 | Content pinning uses release identifiers from here |
| `HC-016`, `KB` | Permanent searchable record |
| `AP-011` | External API deprecation follows its own, longer notice regime |

**Depended on by:** `TR-024` · `CM-005` · `CG-006` · `OP-003` · `HC-016` · `OP-002` (`HX-14`).

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | After each wave; the standard itself annually |
| Trigger for out-of-cycle review | Read rate below target for two consecutive months · a change causing a ticket spike with no note · any deprecation shipped with under 30 days' notice · `M66` go-live at W6 |
| Owner | Programme Office with Content Design |
| Archive retention | Permanent — release notes are the audit trail of what users were told |
| Change route | `CG-006`; the wave note set (§4.7) updates per wave without a version bump to the standard |

---

## Open Items

1. **OP-006-OI-01** — bilingual split of extracts conflicts with `CG-010` §3.2's per-file flag.
2. **OP-006-OI-02** — `RN-07` not yet a pipeline gate.
3. **OP-006-OI-03** — wave note ownership undecided.
4. **OP-006-OI-04** — Thursday release cut-off unconfirmed.
5. **OP-006-OI-05** — read-rate telemetry may not exist.
6. The wave note set (§4.7) is drafted against `06-01` scope as it stands at 2026-08-20; any wave
   re-scoping changes the note set without changing this standard.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — applies to the published notes, not to this standard; the standard requires it of them
- [x] Bengali counterpart — n/a for the standard; **four extracts require Bengali**, see §4.5 and OI-01
- [ ] Named approver recorded — Programme Manager, appointment pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — five open decisions pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ●. G4 applies to the bilingual extracts, not to this file.

---

*`OP-006` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
