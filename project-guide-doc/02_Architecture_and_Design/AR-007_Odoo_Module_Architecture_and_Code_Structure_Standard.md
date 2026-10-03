---
id: AR-007
title: Odoo Module Architecture & Code Structure Standard
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Solution Architect
approver: Chief Architect
standards_basis: Odoo 19.0 module conventions · OCA Development Guidelines · AS-01…AS-15 · DM-01…DM-15
traces_to: >
  PGD-000 AR-007 · AS-05 (extend, never fork) · 02-05 §9 · Technology Stack Specification §8.3 (L5-01…L5-10) ·
  risk TR-04 · AR-001 QAS-11
depends_on: AR-001 · AR-003 · BE-005 (CD register)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-007 — Odoo Module Architecture & Code Structure Standard

### Category 02 · Code `AR` · Odoo 19.0 conventions · OCA Development Guidelines

---

## 1. Purpose

`02-05` §9 asserts the single most important upgrade-safety rule in the programme:

> *"Extensions are separate modules, not modifications to core."*

It asserts it in a table cell, with no standard beneath it and no mechanism above it. **One `_inherit`
done wrong makes the Odoo 20 upgrade a rewrite** across 232 custom modules and 140+ OCA modules
(risk `TR-04`, `AR-001` QAS-11). Over 36 months with a changing team, a rule enforced by intention
alone will be broken, and it will be broken quietly.

This document is the standard: the mandatory anatomy of a `cd_*` module, the inheritance rules that
keep upgrades survivable, and — the part that makes it real — **the CI check that fails a build when
the rule is violated**.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The mandatory directory anatomy of a `cd_*` Odoo module |
| 2 | The manifest standard and dependency declaration rules |
| 3 | **The inheritance decision tree** and the four extension mechanisms, in order of preference |
| 4 | The OCA consumption rule and the fork register |
| 5 | Naming, model, field and method conventions |
| 6 | Security artefact requirements — record rules, field permissions, groups |
| 7 | View, data, wizard and controller rules |
| 8 | Test structure and coverage requirements |
| 9 | The module definition-of-done, and the CI gates that enforce it |
| 10 | Migration script conventions for forward-only, zero-downtime deployment |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| What a module *does* | `AR-003` per-module SDD | Anatomy vs behaviour |
| Repository layout above the module (monorepo, subtrees, submodules) | `BE-004` | This standard governs the inside of a module |
| Language style — formatting, line length, docstrings | `BE-002` Coding Standards | Style vs structure |
| Git workflow, branching, PR template | `BE-003` | |
| CD identifier allocation | `BE-005` | This standard *consumes* the register |
| Next.js and Flutter application structure | `BE-004`, `UX-001` | Odoo-specific |
| CI pipeline stages and infrastructure | `PE-004` | §11 states the *checks*; `PE-004` builds the pipeline |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every Odoo developer** | Read before creating a module. This is not optional reading |
| Code reviewers | The objective standard `BE-002` currently lacks |
| Solution Architect | The fork register (§5.4) and the deviation approval path |
| Implementation vendor | The acceptance standard their deliverables are measured against |
| Platform engineers | §11's checks are the gates `PE-004` must implement |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **Odoo 19.0 module conventions** | Directory structure, manifest keys, model API, inheritance mechanisms | **Departure:** the `fix.`/`fix_`/`cd_` prefix scheme (AS-04) is a 1000FiX addition. Rationale: at 232 custom modules alongside 23 Odoo core and 140+ OCA modules, being able to tell at a glance which layer a model belongs to is worth the convention |
| **OCA Development Guidelines** | Manifest completeness, module naming, security file placement, test layout | Adopted, except OCA's `oca_` naming (ours is `cd_`) and OCA's module-per-feature granularity, where we group by CD allocation |
| AS-01…AS-15 (`02-01` §10, `05-06` §12) | Every standard is realised by a rule in §4–§10 and a check in §11 | AS-05 is the load-bearing one and is given §5 in full |
| DM-01…DM-15 (`05-02` §1) | Model, field, state, sequence and event conventions | Full |
| L5-01…L5-10 (Technology Stack Specification §8.3) | Deliverable completeness — README, runbook, OpenAPI, tests, translation | Full |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §3, §9 | OCA repositories in use; v19 migration status; the extension rule this standard enforces |
| `.../02-01_*.md` §10 | AS-01…AS-15 |
| `.../05-02_*.md` §1, §11 | DM-01…DM-15; index and partition design |
| `../../primary-doc/…Technology_Stack_Specification.md` §5, §8.2, §8.3, §18.2 | OCA repository list; the 248-item CD register; L5 standards; the CI stage list |
| Ibid. §23 `TR-04` | *"OCA modules forked rather than extended, making every future upgrade manual"* — the risk this standard exists to control |

### 2.3 Audit findings this document addresses

| Finding | How |
|---|---|
| `PGD-000` `AR-007` — *"`02-05` §9 asserts the rule with no standard that enforces it"* | §5 is the standard; §11 is the enforcement |
| `TR-04` OCA fork risk | §5.4 fork register + `FF-03` CI check + wave-gate review |
| `TR-12` Outbox applied unevenly | §7.4 emission rule + `FF-04` coverage check |
| `H-03` Two incompatible CD registers, 48 colliding identifiers | §3.2 makes the manifest cite an **issued** CD identifier; a provisional one fails the build |

---

## 3. Module Anatomy

### 3.1 The mandatory directory structure

Every `cd_*` module has this shape. Directories that do not apply are omitted; **directories that
apply may not be renamed, and files may not be placed outside them.**

```
cd_<name>/
├── __init__.py
├── __manifest__.py              ← §3.2
├── README.md                    ← L5-01, mandatory
├── runbook.md                   ← L5-01 / DoD-11, mandatory
├── openapi.yaml                 ← L5-01 / DoD-06, mandatory where the module exposes an API
│
├── models/                      ← ALL business logic (AS-09)
│   ├── __init__.py
│   └── <aggregate>.py           ← one file per aggregate root + its owned entities
│
├── services/                    ← pure computation, no ORM writes, unit-testable in isolation
│   └── <concern>.py             ← e.g. sla_calculator.py, rework_detector.py
│
├── wizards/                     ← transient models; orchestration only, never rules
├── controllers/                 ← HTTP marshalling only; ZERO business logic (AS-09)
├── views/                       ← XML; no <field> computation, no domain logic in attrs
├── reports/                     ← QWeb templates; Bengali-capable (TR-07)
├── data/                        ← noupdate="1" master data, sequences, cron definitions
├── demo/                        ← demo data, never loaded in production
│
├── security/
│   ├── ir.model.access.csv      ← mandatory for every model
│   ├── <module>_groups.xml
│   ├── <module>_record_rules.xml  ← T0–T5 isolation (AR-001 §8.2)
│   └── <module>_field_rules.xml   ← field-level permissions (CD-130)
│
├── i18n/
│   ├── <module>.pot
│   └── bn_BD.po                 ← 100% before acceptance (AS-12, DoD-08)
│
├── migrations/                  ← §10; forward-only
│   └── 19.0.<x.y.z>/
│       ├── pre-migrate.py
│       └── post-migrate.py
│
├── static/
│   ├── description/index.html   ← module card
│   └── src/                     ← OWL 2 components only where genuinely needed
│
└── tests/
    ├── __init__.py
    ├── test_<aggregate>.py      ← state machine + happy path
    ├── test_rules.py            ← one NEGATIVE test per H-class business rule (DoD-04)
    ├── test_security.py         ← one negative test per role (DoD-07)
    ├── test_events.py           ← outbox emission coverage (DoD-05)
    └── test_api.py              ← contract tests where an API exists
```

**Three placements that are commonly got wrong and are therefore stated explicitly:**

| Placement | Rule |
|---|---|
| `services/` | Exists so that computation (SLA maths, scoring, rework detection) is unit-testable **without a database**. Anything in `services/` that writes through the ORM is misplaced |
| `controllers/` | Marshals request → calls a model method → marshals response. **A validation in a controller is a rule that binds API callers and not UI users**, which is the defect DoD-04 exists to catch |
| `data/` vs `demo/` | `data/` loads in every environment including production. `demo/` never loads in production. Putting test fixtures in `data/` is how a production database acquires a customer called "Test Customer" |

### 3.2 The manifest standard

```python
{
    "name": "1000FiX Service Order",
    "summary": "Service order lifecycle, SLA, diagnosis, estimate and QC",
    "version": "19.0.1.0.0",          # <odoo>.<major>.<minor>.<patch>.<build>
    "category": "1000FiX/Service Delivery",
    "author": "1000FiX Services Limited",
    "website": "https://1000fix.com",
    "license": "LGPL-3",              # §3.3
    "depends": [                       # §3.4 — declared, minimal, layered
        "base", "mail", "product",
        "fieldservice",                # OCA
        "cd_party_master",             # 1000FiX
    ],
    "data": [
        "security/cd_service_order_groups.xml",
        "security/ir.model.access.csv",
        "security/cd_service_order_record_rules.xml",
        "data/sequences.xml",
        "views/service_order_views.xml",
    ],
    "demo": ["demo/service_order_demo.xml"],
    "installable": True,
    "application": False,             # only the category anchor module is an application
    "auto_install": False,
    # ─── 1000FiX mandatory keys ────────────────────────────────────────────
    "x_cd_id": "CD-001",              # ISSUED by BE-005. A provisional id fails CI (FF-16)
    "x_module_id": "M01",             # owning module from 02-02
    "x_wave": "W1",
    "x_owner": "Service Delivery Squad",
}
```

| Key | Rule |
|---|---|
| `version` | **Five components, prefixed with the Odoo series.** `19.0.1.0.0`. The series prefix is what makes an upgrade sweep mechanical |
| `license` | Must be declared. `LGPL-3` for modules extending Odoo/OCA; see §3.3 |
| `depends` | **Minimal and declared.** Never rely on transitive availability — an indirect dependency is invisible at upgrade |
| `x_cd_id` | **Must be an identifier issued by `BE-005`.** Provisional identifiers from `02-05` §5.2 or Technology Stack Specification §8.2 fail the build until ratified |
| `application` | `False` for all but the category anchor. 232 modules each claiming to be an application makes the Apps menu unusable |

### 3.3 Licence rule

| Situation | Licence | Why |
|---|---|---|
| The module `_inherit`s an Odoo core or OCA model | **LGPL-3** | Derivative of an LGPL-3 work |
| The module is standalone with no Odoo/OCA inheritance | LGPL-3 by default | Consistency; no benefit to divergence |
| Any AGPL-3 dependency is introduced | **Architecture approval required** | AGPL-3 network-use obligations propagate. `02-05` §4 analyses this correctly; `CO-004` maintains the register |

**Automated licence scan on every dependency addition. AGPL, BSL, TSL and fair-code components
require architecture approval** (Technology Stack Specification §18.5).

### 3.4 Dependency layering

`depends` entries are declared in strict layer order, and **a lower layer may never depend on a
higher one**:

```
1. Odoo core          base, mail, product, stock, account, hr …
2. OCA                fieldservice, helpdesk, operating_unit, dms …
3. 1000FiX platform   cd_event_outbox, cd_rbac_ext, cd_entity_config, cd_party_master …
4. 1000FiX domain     cd_service_order, cd_dispatch, cd_billing_engine …
```

| Rule | Enforcement |
|---|---|
| **DL-01** A platform module (layer 3) may not depend on a domain module (layer 4) | `FF-17` |
| **DL-02** A domain module may not depend on another domain module **except** as ruled in `AR-006` §6.1 tiers | `FF-17` |
| **DL-03** No module depends on `web` for business behaviour | Review |
| **DL-04** Every `depends` entry is used. An unused dependency is removed | Static analysis |

---

## 4. Naming and Model Conventions

| # | Rule | Example | Check |
|---|---|---|---|
| **N-01** | Module directory: `cd_<snake_case>` | `cd_service_order` | `FF-02` |
| **N-02** | Model name: `fix.<domain>.<entity>` | `fix.service.order` | `FF-02` (AS-04) |
| **N-03** | Table name: `fix_<domain>_<entity>` — derived, never hand-set | `fix_service_order` | `FF-02` |
| **N-04** | Columns `snake_case`; `_id` for many2one, `_ids` for one2many/many2many | `partner_id`, `work_order_ids` | Linter |
| **N-05** | Boolean fields read as an assertion, not a question | `is_warranty`, not `warranty` | Review |
| **N-06** | Computed fields declare `compute=`, `store=` and `depends` explicitly. **A stored computed field with an incomplete `depends` is a data-integrity defect**, not a performance one | | Review + `FF-18` |
| **N-07** | Selection values are stable technical strings, never translated labels | `('awaiting_approval', 'Awaiting Approval')` | `FF-02` |
| **N-08** | Public methods: `action_*` (UI-invoked), `compute_*`, `check_*`, `_*` (private) | `action_confirm` | Linter |
| **N-09** | Every model has `_description` | | `FF-19` |
| **N-10** | Every model inherits `mail.thread` and `mail.activity.mixin` (AS-02, DM-04) | | `FF-20` |
| **N-11** | Every transactional model carries `company_id` and `operating_unit_id` (AS-03, DM-03) | | `FF-21` |
| **N-12** | Money is `fields.Monetary` with an explicit `currency_id`. **Never `Float`** (AS-10, DI-01) | | `FF-22` |
| **N-13** | Datetimes are naive UTC; presentation converts to `Asia/Dhaka` (AS-11, DM-08) | | `FF-23` |
| **N-14** | Durations stored in **minutes** as `Integer` | `duration_min` | Review |
| **N-15** | Every user-facing string wrapped for translation; `bn_BD.po` at 100% before acceptance (AS-12) | `_("…")` | `FF-24` |
| **N-16** | `ondelete` declared explicitly on every many2one. **No default** | `ondelete='restrict'` | `FF-25` |
| **N-17** | Business records are archived (`active`), never hard-deleted (DM-06, DI-08) | | Review |
| **N-18** | Residency-classified values are **never** declared as a field. A resident key is declared and the value read through CD-233 (`AR-003` DP-07) | | `FF-09` |

> **N-16 deserves a sentence of its own.** Odoo's default `ondelete` for many2one is `set null`. For
> `fix.service.order.partner_id` that would silently orphan an order when a customer record is merged
> — which happens routinely in M33's deduplication. Every many2one must state its policy deliberately.

---

## 5. The Inheritance Standard — AS-05 in Full

**This section is the reason this document is P0.**

### 5.1 The decision tree

Applied in strict order. **Each step must be shown to be impossible before moving to the next.**

```
Need to change existing behaviour?
│
├─ 1. Can CONFIGURATION do it?
│     (field visibility, view inheritance in the UI, a rule, a parameter)
│     → YES: configure. Write no code. STOP.
│
├─ 2. Can EXTENSION do it?
│     class ServiceOrder(models.Model):
│         _inherit = 'repair.order'          # extend in place
│         new_field = fields.Char()
│         def action_confirm(self):
│             res = super().action_confirm()  # ALWAYS call super
│             ...
│     → YES: extend. STOP.
│
├─ 3. Can COMPOSITION do it?
│     A new fix.* model with a many2one to the Odoo/OCA model,
│     leaving the original untouched.
│     → YES: compose. STOP.
│
└─ 4. FORK
      Requires NAMED Design Authority approval, an entry in the fork
      register (§5.4), and a divergence review at every wave gate.
      → This is the last resort, and it is a decision, not a workaround.
```

### 5.2 The three Odoo inheritance mechanisms, and when each is correct

| Mechanism | Syntax | Use when | Do not use when |
|---|---|---|---|
| **Extension** | `_inherit = 'model'` | Adding fields or behaviour to an existing model, in place | You need a *separate* table with different lifecycle |
| **Prototype** | `_name = 'new'` + `_inherit = 'old'` | You need a **new table** that starts from another model's definition | Extension would do — this copies the definition and diverges permanently |
| **Delegation** | `_inherits = {'model': 'field_id'}` | A composed record that *is-a* another record with its own table | You merely need a reference — use a plain many2one |

> **The most common and most expensive mistake:** using **prototype** inheritance where **extension**
> was wanted. Prototype creates a second table that shares no rows with the original. It is
> discovered when a report queries the original and finds none of the new records — usually in UAT,
> and usually after a hundred records exist in the wrong table.

### 5.3 Method override rules

| # | Rule | Why |
|---|---|---|
| **OV-01** | `super()` is **always** called, unless the override deliberately replaces the behaviour and an ADR records it | Not calling `super()` silently disables every other module's extension of the same method |
| **OV-02** | Overrides of `create`, `write` and `unlink` are `@api.model_create_multi` / batch-aware | A single-record override breaks bulk operations and NFR-041 (1,000 records ≤ 60 s) |
| **OV-03** | Never override a private Odoo method (`_`-prefixed) without an ADR — it is not a contract and it changes between versions | This is the primary upgrade-breakage vector after forking |
| **OV-04** | Never monkey-patch. Ever | Invisible at review, invisible at upgrade, invisible in a stack trace |
| **OV-05** | Never modify a file inside `odoo/` or an OCA subtree. **Ever** | AS-05. Enforced by `FF-03` and by CI diff against the pinned tree |
| **OV-06** | View inheritance uses `xpath` with a stable anchor, not positional indices | Positional inheritance breaks on any upstream view edit |

### 5.4 The OCA consumption rule and the fork register

| # | Rule |
|---|---|
| **OCA-01** | Only modules rated **Production/Stable** or **Beta with confirmed v19 migration** (or active migration commits within six months) are deployed |
| **OCA-02** | OCA modules are consumed as **subtrees at a pinned commit**. Never vendored by copy-paste, never edited in place |
| **OCA-03** | Where 1000FiX migrates an OCA module to v19, **the work is contributed upstream.** This reduces long-term maintenance and is a condition of the licence spirit (`02-05` §3) |
| **OCA-04** | A fork requires named Design Authority approval, a fork-register entry, and a stated **exit condition** — what would have to be true for the fork to be retired |
| **OCA-05** | The fork register is reviewed at **every wave gate**, with divergence measured in lines changed against upstream |

**Fork register** — the artefact that makes `TR-04` measurable rather than feared:

| Field | Content |
|---|---|
| Module | OCA repository and module name |
| Pinned upstream commit | |
| Approved by / date | Named individual, not a role alone |
| Reason | Why steps 1–3 of §5.1 were impossible |
| Divergence | Lines changed vs upstream, measured at each wave gate |
| **Exit condition** | What upstream change would allow retirement |
| Upgrade owner | Who merges upstream at the Odoo 20 slot (ADR-027) |

**Current state, counted 2026-08-18: zero forks, because no code exists.** The register opens empty
and every entry is a decision.

### 5.5 Known v19 migration exposure

`02-05` §3 records the OCA migration position. It is a live Wave 2 risk (`TR-03`), and it is where
the fork pressure will come from:

| Repository | v19 status | Exposure |
|---|---|---|
| `OCA/field-service` | ~25 of 33 migrated | **M01, M02 — the core FSM replacement.** 8 modules to migrate; 12–20 PW carried |
| `OCA/helpdesk` | ~20 of 28 | M01, M05, M27 |
| `OCA/management-system` | ~28 of 33 | M23 |
| `OCA/operating-unit` | ~12 of 15 | **All modules** — this is the multi-branch isolation mechanism |
| `OCA/hr` + `OCA/payroll` | ~40 of 50+ | M21, M22, M56 |

> **`W0-01` is a blocking pre-build activity:** assess the actual v19 gap before the Wave 1
> architecture is fixed. If `field-service` migration exceeds 20 PW (assumption `A-03`), the gap
> reclassifies to L5 and Wave 2 effort rises. **Migrating and contributing upstream is always
> preferred to forking**, because a contributed migration is maintained by the community afterwards
> and a fork is maintained by us for 36 months.

---

## 6. Security Artefacts

Every module ships all four. A module with models and no `ir.model.access.csv` **will not install**
in a correctly configured environment, and should not.

| Artefact | Rule |
|---|---|
| `ir.model.access.csv` | One row per model per applicable group. **No model without an ACL** |
| Groups XML | Groups map to registered roles `R01`…`R46`. **A group for an unregistered role fails CI** (`FF-26`) |
| Record rules XML | Realise the isolation tier (T0–T5, `AR-001` §8.2). Every transactional model declares its tier |
| Field rules XML | Field-level permissions via CD-130 for S2/S3-classified fields |

| # | Rule | Why |
|---|---|---|
| **S-01** | Every model declares its **isolation tier** in a comment at the top of the record-rule file | Makes the tier reviewable rather than inferable from a domain expression |
| **S-02** | Record rules use `operating_unit_id` for T2 via `OCA/operating-unit`, never a hand-rolled branch field | One isolation mechanism, one place to audit |
| **S-03** | **One negative test per applicable role** (DoD-07) — a user in role X **cannot** read/write what X should not | A positive-only permission test proves nothing about isolation |
| **S-04** | No `sudo()` without an inline comment stating why and what it bypasses | `sudo()` is the single most common privilege-escalation defect in Odoo code |
| **S-05** | SoD-relevant capabilities are declared so CD-132 can evaluate them at role-assignment time (ADR-021) | All 30 SOD controls, not the 12 currently registered |

---

## 7. Business Logic Rules

### 7.1 Placement

| Logic | Lives in | Never in |
|---|---|---|
| Validation and business rules | `models/` — constraints and method guards | Views, controllers, wizards, portal code (AS-09) |
| Pure computation | `services/` | Models, where it cannot be unit-tested without a database |
| Orchestration of a user flow | `wizards/` | Controllers |
| Request marshalling | `controllers/` | Anywhere else |

### 7.2 State machines (`AR-003` DP-01)

| # | Rule |
|---|---|
| **SM-01** | One `state` Selection per aggregate root |
| **SM-02** | The transition map is a **single declared structure** on the model (AS-06) |
| **SM-03** | **All** state change flows through one `_do_transition(target)` method |
| **SM-04** | `_do_transition` checks the guard, writes the state, writes the outbox row and posts to chatter — **in one transaction** |
| **SM-05** | `record.state = 'x'` outside `_do_transition` **fails CI** (`FF-06`) |

### 7.3 Business rules

| # | Rule |
|---|---|
| **BR-01** | **H**-class rules are enforced by a `@api.constrains` constraint or a guard on the transition method — at the **model layer** |
| **BR-02** | **A**-class (approved override) rules require a `fix.approval.request` and log the override with the approver |
| **BR-03** | **S**-class (soft warning) rules use a non-blocking warning; they never silently pass |
| **BR-04** | **C**-class (computed) rules are stored computed fields with complete `depends` |
| **BR-05** | Every **H** rule has a **negative test through both UI and API** (DoD-04) |

### 7.4 Event emission (`AR-003` DP-04)

| # | Rule |
|---|---|
| **EV-01** | Every state-changing method emits its domain event through the shared `emit_event()` helper (CD-125), **in the same transaction** |
| **EV-02** | Never publish after commit. Never publish from `@api.onchange`. Never publish from a view or controller |
| **EV-03** | The event name conforms to `AR-009`'s convention — `<aggregate>.<past-tense-verb>` (ADR-017) |
| **EV-04** | The event is registered in `IN-003` before the code that emits it merges |
| **EV-05** | The module's §9 transition table and its emitted-event set must agree — a transition with no event, or an event with no transition, fails `FF-04` |

---

## 8. Views, Reports and Client Code

| # | Rule | Why |
|---|---|---|
| **V-01** | View inheritance uses `xpath` with a stable anchor | Positional inheritance breaks on upstream edits |
| **V-02** | No business logic in `attrs` beyond simple field visibility | A rule in `attrs` binds the UI only |
| **V-03** | Every list view supports **bulk actions** (`04-00` design requirement) | High-volume roles depend on them |
| **V-04** | Screen density targets **1366×768** — the most common branch hardware | `04-00` P03 design requirement |
| **V-05** | Any record reachable in **≤ 4 clicks** from any starting point (NFR-077) | |
| **V-06** | OWL 2 components only where a standard widget genuinely cannot serve. Every component is a maintenance liability at upgrade | |
| **V-07** | QWeb reports are **Bengali-verified on every supported printer at each wave gate** (`TR-07`) | A Mushak 6.3 that renders wrongly is a compliance defect |
| **V-08** | Layouts tolerate **15–30% Bengali text expansion** without truncation | `UX-007` |

---

## 9. Tests

| Level | Requirement | Gate |
|---|---|---|
| Unit | **≥ 80% of custom code; 100% of financial and tax calculation paths** (DoD-03, NFR-090-M) | CI blocks merge |
| Business rules | One **negative** test per **H**-class rule, through UI and API (DoD-04) | CI |
| Security | One **negative** test per applicable role (DoD-07) | CI |
| Events | Outbox coverage — every state transition emits (DoD-05) | CI `FF-04` |
| Contract | OpenAPI 3.1 validation; **an invalid payload posted directly to the API must be rejected** (PS-11) | CI |
| Migration | Every migration script dry-run against a **production-sized clone** | CI build verification |
| Localisation | Translation completeness **100%** | CI `FF-24` |

| # | Rule |
|---|---|
| **T-01** | Tests use `demo/` data or fixtures, never production-shaped assumptions |
| **T-02** | No test depends on another test's ordering or residue |
| **T-03** | A flaky test is a defect and is fixed or removed — never re-run until green |
| **T-04** | Concurrency behaviour declared in the SDD (`AR-003` DP-03) has a test that exercises the contention |

> **T-04 is the one most often skipped and most valuable.** A reservation race, a duplicate webhook,
> or two dispatchers assigning the same technician are all reproducible in a test and all invisible
> in a single-user manual test.

---

## 10. Migrations

Zero-downtime deployment (NFR-008) constrains the *shape* of every schema change, which is why this
belongs in an architecture standard rather than an operations one.

| # | Rule |
|---|---|
| **MG-01** | Migrations are **forward-only** (OPS-07). A rollback is a documented procedure, not a `down` script |
| **MG-02** | **A release adds a column before code uses it, and removes a column only after no code references it — two releases, never one** |
| **MG-03** | Every migration is dry-run against a production-sized clone before promotion |
| **MG-04** | Data migrations are **idempotent and restartable** — a migration killed halfway must be safely re-runnable |
| **MG-05** | Long-running data migrations run **outside** the deployment window, as a background job with progress reporting |
| **MG-06** | `pre-migrate` handles renames and drops; `post-migrate` handles backfills and recomputation |
| **MG-07** | A migration that touches residency-classified data goes through CD-233. **Never a direct query** (`AR-001` LB-08) |

> **MG-02 is the whole of zero-downtime deployment in one sentence.** During a rolling deploy, old
> and new code run simultaneously. A column dropped in the same release that stops using it will be
> read by the old pods that have not yet cycled.

---

## 11. Enforcement — the CI Gates

**A standard without a mechanism is a preference.** These are the checks; `AR-012` defines them as
fitness functions and `PE-004` builds the pipeline.

| Gate | Check | Blocks merge |
|---|---|:--:|
| `FF-02` | Naming: `cd_*` module, `fix.*` model, `fix_*` table, snake_case columns (AS-04, N-01…N-03) | ✔ |
| **`FF-03`** | **No modification to any file under `odoo/` or an OCA subtree; no unregistered fork (AS-05, OV-05)** | ✔ |
| `FF-04` | Outbox coverage — every state transition emits its event (AS-08, EV-05) | ✔ |
| `FF-06` | No `state` assignment outside `_do_transition` (SM-05) | ✔ |
| `FF-09` | No residency-classified field declared outside CD-233 (N-18) | ✔ |
| `FF-16` | `x_cd_id` present and **issued by `BE-005`**, not provisional | ✔ |
| `FF-17` | Dependency layering DL-01, DL-02 | ✔ |
| `FF-18` | Stored computed fields have complete `depends` | ✔ |
| `FF-19` | Every model has `_description` | ✔ |
| `FF-20` | Every business model inherits `mail.thread` + `mail.activity.mixin` (AS-02) | ✔ |
| `FF-21` | Every transactional model has `company_id` + `operating_unit_id` (AS-03) | ✔ |
| `FF-22` | No `Float` in a money path; `Monetary` with explicit currency (AS-10) | ✔ |
| `FF-23` | Datetimes stored UTC (AS-11) | ✔ |
| `FF-24` | Translation completeness 100% (AS-12) | ✔ |
| `FF-25` | `ondelete` declared on every many2one (N-16) | ✔ |
| `FF-26` | Every security group maps to a registered role `R01`…`R46` | ✔ |
| — | Unit coverage ≥ 80%, 100% financial (DoD-03) | ✔ |
| — | SAST, dependency scan, container scan, licence scan | ✔ on high/critical |
| — | OpenAPI 3.1 validation + PS-11 portal contract test | ✔ |
| — | Migration dry-run against a production-sized clone | ✔ |

> **`FF-26` is currently unsatisfiable and must not be quietly relaxed.** `05-04` registers R01–R38;
> **R39–R46 are in use and unregistered, R60 is a duplicate of R32, and R54/R57 are undefined**. The
> check should be built in Wave 1 and the register completed to R46 in Wave 0 (`TR-13`). Building the
> check against 38 roles and widening it later means the eight unregistered roles enter production
> unchecked.

---

## 12. Module Definition of Done

Inherits `02-02` §8 (DoD-01…DoD-17) and adds the structural items this standard governs.

| # | Criterion |
|---|---|
| ✔ | Directory anatomy conforms to §3.1 |
| ✔ | Manifest complete, `x_cd_id` **issued**, licence declared, dependencies minimal and layered |
| ✔ | README, runbook and OpenAPI present (L5-01) |
| ✔ | All 18 naming rules pass |
| ✔ | Inheritance decision tree applied; **zero unregistered forks** |
| ✔ | Four security artefacts present; negative test per role |
| ✔ | State machine via `_do_transition`; H-rules at the model layer with negative tests |
| ✔ | Outbox emission on every transition; events registered in `IN-003` |
| ✔ | Coverage ≥ 80% / 100% financial; `bn_BD.po` at 100% |
| ✔ | Migrations forward-only, dry-run against a production-sized clone |
| ✔ | Every CI gate in §11 green |

---

## 12A. Decisions Recorded

*The house-template "Decisions Recorded" section is intentionally empty here, and the heading is
retained rather than omitted.* Every decision this standard rests on is an ADR in `AR-004` — ADR-001
(Odoo CE), ADR-026 (Flutter), ADR-027 (upgrade slot) — and the standard's own rules are derived from
AS-01…AS-15, which are decisions taken in `02-01` §10 and not re-taken here. A local decision table
would restate them and then diverge.

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **When is `BE-005` issued?** `FF-16` cannot run against provisional identifiers | CTO | **W0 — blocking** | Every module manifest |
| Q-02 | **Role register completion to R46, R60 eliminated** — `FF-26` is unsatisfiable until then | CTO / `SC-004` | **W0 — blocking** | Every security artefact |
| Q-03 | `W0-01` OCA v19 gap assessment — is `field-service` closable within 12–20 PW (`A-03`)? | Implementation Partner | **W0** | Wave 2 scope; fork pressure |
| Q-04 | Does the Odoo 20 upgrade slot (ADR-027, `D-025`) change the `version` prefix rule mid-programme? | CTO | W5 | Migration directory naming |
| Q-05 | Who owns the fork register between wave gates? | Solution Architect | W1 | `TR-04` control |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The mandatory module anatomy is fully specified | §3.1 |
| AC-02 | AS-05 is expressed as a decision tree with an approval path and a register | §5.1, §5.4 |
| AC-03 | Every naming and model convention has a check | §4 — 18 rules, 14 automated |
| AC-04 | Every AS-01…AS-15 standard is realised by a rule and a gate | §4, §7, §11 |
| AC-05 | The zero-downtime migration constraint is stated as a shape rule | §10 MG-02 |
| AC-06 | Enforcement is mechanical, not advisory | §11 — 16 named fitness functions |
| AC-07 | Gates that are currently unsatisfiable are stated as such rather than silently relaxed | §11 `FF-16`, `FF-26` |

**Definition of done.** Complete when every criterion is met, `BE-005` is issued (Q-01), the role
register is completed (Q-02), and `PGD-000`'s `AR-007` row is updated with a fresh enumeration
timestamp.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` QAS-11 | The upgrade-survivability scenario this standard satisfies |
| Upstream | `AR-004` ADR-001, ADR-027 | Odoo CE, and the planned upgrade slot |
| Upstream | **`BE-005`** | CD identifiers — `FF-16` |
| Upstream | `SC-004` | Role register — `FF-26` |
| Downstream | `AR-003` §7 | Every SDD's structure viewpoint conforms to §3.1 |
| Downstream | `AR-012` | Defines §11's gates as fitness functions |
| Downstream | `BE-002`, `BE-004`, `BE-006` | Style, repository and component standards build on this |
| Downstream | `PE-004` | Implements §11 in the pipeline |
| Downstream | `QA-005` | Test automation framework realises §9 |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05` §3, §9 | OCA position and the rule this standard enforces |

---

## 16. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-003` · `./AR-004` · `./AR-009` ·
`./AR-012` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-01` §10, `02-05` §3, §4, §9 ·
`.../05_Cross_Cutting_Specifications/05-02` §1, `05-04`, `05-06` §12 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §5, §8.2, §8.3, §18.2, §18.5, §23

**External sources**

| Source | Version | Verified |
|---|---|---|
| Odoo Developer Documentation — module structure, ORM, inheritance | 19.0 | 2026-08-18 |
| OCA Development Guidelines | current | 2026-08-18 |
| Odoo 19.0 released 18 September 2025; supported to ~September 2028 | 19.0 | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Makes AS-05 mechanically enforceable via the §5.1 decision tree, the §5.4 fork register and 16 CI gates. States `FF-16` and `FF-26` as currently unsatisfiable pending `BE-005` and the role register | *Pending — Chief Architect* |

---

*`AR-007` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
