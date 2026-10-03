---
id: FIX-ERP2-M30
module_id: M30
module_code: ADM
module_name: Platform Administration & Configuration
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P0
wave: W1
---

# M30 — Platform Administration & Configuration
### Category K · Code `ADM` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M30 |
| **Module code** | `ADM` |
| **Category** | K — Platform & Technology |
| **Status** | Existing (re-scoped in v2.1 — master data governance moved to **M64**; locale, country pack and translation moved to **M65**) |
| **Priority** | **P0** — one of the three modules built first |
| **Delivery wave** | W1 (Months 1–4) |
| **Business owner** | Chief Technology Officer |
| **System owner** | Platform Squad |
| **Delivery layers** | L1 Odoo `base` company and configuration · L2 OCA `operating-unit`, `server-tools` · L4 Grafana, Prometheus, Loki · L5 custom org structure, configuration, feature flags and operations console |
| **Custom modules** | `cd_entity_config`, `cd_feature_flag`, `cd_platform_ops`, `cd_job_registry` |
| **Requirement range** | FR-ADM-001 … FR-ADM-040 |
| **Requirement count** | **40** *(measured — exceeds the 035 range allocated in `05-01` §1.3; extension into the 036–050 headroom)* |
| **Effort estimate** | **19 person-weeks** *(measured — supersedes the 15 PW estimate in `02-02`)* |
| **Depends on** | M28 Integration (event outbox, health telemetry) · M29 Identity (administrator authorisation) |
| **Depended on by** | **All 66 other modules and all 12 portals** |

---

## 2. Purpose

M30 is **how the platform is run and how the business shape is expressed in it**.

Two responsibilities that look unrelated live here for a reason. The first is the
**organisation structure** — the legal entity, the 51+ branches, the dispatch zones, the cost
centres, the business lines and the working calendars that every other module carries on every
record. The second is **platform operation** — configuration, feature flags, environments,
scheduled jobs, health, archival and announcements.

They belong together because they answer the same question: *how does this system get changed
without changing its code?* A new branch opens; that is configuration. A pricing threshold
moves; that is configuration. A new capability is switched on for one branch before all 51;
that is a feature flag. NFR-027 requires no-code configuration for workflows, forms, thresholds
and rules, and NFR-028 requires customisation without modifying core product code. M30 is where
those two requirements are honoured.

The category overview draws the boundary against M64 precisely: **M30 keeps the platform
running; M64 keeps the data trustworthy.** A branch code created without approval is an M64
failure, not an M30 one.

### Why It Exists

**Because the Company is opening branches.** The 1000FiX Station programme is a stated growth
initiative. Today standing up a branch means weeks of coordination. The target is **under one
day**, and that is only possible if a branch is a configuration object rather than a project.

**Because every record in the estate carries dimensional context.** `02-01` §8 requires
`company_id`, `country_id`, `operating_unit_id`, `zone_id`, `cost_center_id`,
`business_line_id`, `currency_id` and `lang` on every record. Those dimensions must be defined
once, by one module, or they diverge.

**Because production must be changed safely.** OPS-02 forbids hand-editing configuration in
production. OPS-06 requires that any new capability can be disabled without a deployment. Both
require a configuration and feature-flag system that exists from day one, not one retrofitted
after the first bad release.

**Because silent failure is a defect.** OPS-05 states it plainly: every scheduled job reports
success, failure and duration. In a 67-module estate running hundreds of jobs, a job that fails
quietly corrupts data for weeks before anyone notices.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §2 | M30 owns "organisation structure, users, environments, feature flags, jobs, health console, archival, announcements" |
| `_CATEGORY_OVERVIEW.md` §5 | The M30/M64 split: technical configuration versus business master data governance. "M30 keeps the platform running. M64 keeps the data trustworthy" |
| `_CATEGORY_OVERVIEW.md` §6 | M30 owns organisation structure — entity, branch, zone, cost centre; **M65 adds the country dimension**; M30 owns observability and platform health with M28 integration health |
| `_CATEGORY_OVERVIEW.md` §7 promise 5 | "Every module inherits multi-branch, multi-entity and multi-currency context from the platform" — M30 with M65 |
| `_CATEGORY_OVERVIEW.md` §9 | **Time to stand up a new branch < 1 day**; configuration changes made without a code release > 95% |
| `02-01` §8 | The full dimensional model — eight dimensions carried on every record and their enforcing mechanism |
| `05-02` §M30 | 17 allocated entities, of which **5 move to M64 and M65** under the v2.1 re-scope |
| `05-05` §11 BRU-ADM-01, BRU-ADM-02 | Master data changes above significance require approval; production configuration changes must trace to an approved change record |
| `05-06` NFR-027, NFR-028 | No-code configuration for workflows, forms, thresholds and rules; customisation without modifying core code |
| `05-06` NFR-006, NFR-007, NFR-030, NFR-049, NFR-051, NFR-052 | Uptime, RPO/RTO, backup retention, maintenance window, DR drills, backup verification |
| `05-06` OPS-01 … OPS-08 | The eight operability standards this module implements |
| `05-06` NFR-058 | 200 branches without configuration redesign |
| `05-06` §11 | The environment ladder: local, dev, staging, training, prod, dr |
| `02-05` §9 | Development environment and practice, secrets, promotion, dependency management |

---

## 3. Scope Boundary

> **The rule:** M30 owns **the shape of the organisation and the operation of the platform**.
> It does not own the *governance* of business data (M64), the *jurisdiction* (M65), or the
> *process* by which IT work gets done (M66).

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Legal entity register and company configuration *(the entity object; M65 adds its country dimension)* |
| 2 | **Branch register** — the 51+ operating units with capability, hours, contact, geography and status |
| 3 | Branch provisioning: the single action that stands up a new branch end to end |
| 4 | Dispatch zone definition and geographic coverage |
| 5 | Cost centre hierarchy |
| 6 | Business line register |
| 7 | Working calendars, shifts, public holidays and branch-specific opening hours |
| 8 | The dimensional model: guaranteeing every record carries entity, branch, zone, cost centre, business line and currency |
| 9 | User administration as an operational function *(identity and permission remain M29's)* |
| 10 | **Configuration parameter registry** — every threshold, limit, toggle and setting, with type, owner and scope |
| 11 | Configuration versioning, change history and rollback |
| 12 | **Configuration promotion** through the environment ladder, never hand-edited in production |
| 13 | **Feature flags** with targeting by entity, branch, role, user and percentage rollout |
| 14 | Kill-switch capability: disabling any new capability without a deployment |
| 15 | Environment registry: local, dev, staging, training, prod, dr — with purpose, data policy and refresh cadence |
| 16 | **Scheduled job registry** — every cron and background job with owner, schedule, expected duration and SLA |
| 17 | Job execution monitoring: success, failure, duration, overlap detection and alerting |
| 18 | Background queue and worker health |
| 19 | **Platform health console** — the single operational view of the estate |
| 20 | Observability configuration: metrics, logs, traces, dashboards and alert routing |
| 21 | Alert registry with a mandatory runbook link per alert |
| 22 | Capacity monitoring and growth review |
| 23 | **Archival and data lifecycle**: archive policy, execution, retrieval and storage tiering |
| 24 | Backup configuration, verification and restore testing |
| 25 | Disaster recovery configuration, failover procedure and drill execution |
| 26 | Planned maintenance windows and change freeze periods |
| 27 | **System announcements** and operational communication to internal users |
| 28 | Deployment and release coordination support: version registry, rollback readiness |
| 29 | Licence register for open-source and commercial components |
| 30 | Platform runbook registry, ensuring every module ships one (NFR-091) |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Master data ownership, stewardship workflow, data quality rules** | **M64** MDM | The defining boundary of §5 in the category overview. M30 lets you create a branch code; M64 decides who may, through what approval, and whether the value is any good |
| **Business-rule parameters and thresholds** | **M64** stores, **M63** executes | M30 holds *technical* configuration — a timeout, a batch size, a feature flag. A discount ceiling or an approval threshold is business master data |
| **Country pack, locale pack, translation, currency rules, statutory calendars** | **M65** | M30 defines the entity; M65 defines what it means to operate in a jurisdiction |
| Identity, authentication, roles, permissions, record rules, audit | **M29** | M30 administers users operationally; M29 decides what they may do |
| API gateway, event bus, connectors, integration health *detail* | **M28** | M30's health console *displays* integration health; M28 produces and owns it |
| Workflow, approval routing, business-rule execution | **M63** | — |
| **IT incident, problem, change and request processes** | **M66** ITSM | M30 provides the health console and the change *record*; M66 runs the change *process*. A platform alert becomes an M66 incident |
| Company IT assets, laptops, phones, employee software licences | **M66** | M30 holds the licence register for *platform components*; M66 holds it for *employee software* |
| Data warehouse, pipelines, analytical modelling | **M62** | — |
| Business dashboards and reporting | **M25** | M30's console is operational, not analytical |
| HR organisation chart, reporting lines, positions | **M21** | The branch is an operating unit; the team inside it is HR's |
| Branch premises, fit-out, utilities, physical infrastructure | **M47** Facility | M30 creates the branch record; M47 builds the branch |
| Branch opening as a **project** with phases, budget and milestones | **M67** PPM | M30 provisions in a day; M67 manages the six-week project around it |
| Financial chart of accounts and fiscal configuration | **M19** / **M65** | — |
| Document retention schedule and legal hold | **M24** | M30 executes archival technically; M24 sets the policy |

### 3.3 Shared Concepts

| Concept | M30's Role | Owning Module |
|---|---|---|
| Legal entity | **Owns** the object; M65 owns its country pack and jurisdiction attributes | M30 / M65 |
| Branch / operating unit | **Owns** | M30 |
| Zone | **Owns** the definition; M02 owns dispatch behaviour within it | M30 / M02 |
| Cost centre | **Owns** the hierarchy; M54 owns budget and cost accounting against it | M30 / M54 |
| Configuration parameter | **Owns** technical parameters; M64 owns business parameters | M30 / M64 |
| Feature flag | **Owns** | M30 |
| Scheduled job | **Owns** the registry and monitoring; the module owns the job's logic | M30 / module |
| Platform health | **Owns** the console; M28 owns integration health, M29 owns security signals | M30 / M28 / M29 |
| Archive | **Owns** execution; M24 owns retention policy | M30 / M24 |
| Change record | **Owns** the configuration change trail; M66 owns the ITIL change process | M30 / M66 |
| Environment | **Owns** | M30 |
| Announcement | **Owns** internal operational communication; M27 owns customer communication | M30 / M27 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP enterprise structure (company code, plant, storage location, profit centre)** | The organisational skeleton defined once and carried on every document | **The dimensional model as a platform guarantee rather than a per-module convention** (`02-01` §8, AS-03). Every record carries entity and operating unit, verified in CI | SAP's enterprise-structure configuration depth and its irreversibility. Ours is editable with an audit trail |
| **Oracle Fusion enterprise structures / Dynamics 365 legal entities and operating units** | Legal entity, business unit, department hierarchies with security integration | The separation of **legal entity** (a fiscal and statutory concept) from **operating unit** (an operational one) — which is what makes 51 branches inside one legal entity work cleanly, and what makes a second legal entity additive | — |
| **OCA `operating-unit`** | Multi-branch isolation on the Odoo substrate | Adopted as the L2 foundation for operating-unit scoping across all modules | — |
| **Feature-flag practice (LaunchDarkly, OpenFeature, Datadog Feature Flags)** | Targeted rollout by segment, percentage rollout, kill switch, flag-to-telemetry correlation | **Kill switch as a first-class operational capability (OPS-06)** and targeting by entity, branch, role and percentage. Also adopted: **correlating a flag with telemetry**, so "did enabling this slow anything down" is answerable | Experimentation and A/B statistical machinery; the business need is safe rollout, not experimentation |
| **Platform engineering / internal developer platform practice** | Self-service golden paths; configuration as a product; a service catalogue | **Branch provisioning as a golden path** — one action, not a checklist. This is what turns "weeks" into "under a day" | A full Backstage-style developer portal; M28's developer portal covers the API surface and that is sufficient |
| **OpenTelemetry + Prometheus + Grafana (CNCF baseline)** | Vendor-neutral metrics, logs and traces feeding one operational view | The **single health console** with alert-to-runbook linkage (OPS-03). An alert without an action is noise, and noise is why real alerts get missed | Vendor-specific observability agents; cardinality discipline is enforced (see M28 T-14) |
| **SRE practice — error budgets, capacity review, blameless operations** | Availability targets treated as budgets; capacity reviewed ahead of need | **Capacity reviewed monthly against growth with scaling decided ahead of the need (OPS-08)**, and availability measured against NFR-006 (99.9% business hours) and NFR-045 (99.7% 24×7) | Formal error-budget-driven release gating; disproportionate for a team of this size, and revisitable |
| **Configuration-as-code / GitOps** | Versioned configuration promoted through environments, never edited in place | **OPS-02 implemented literally**: production configuration is promoted, and direct production edits are blocked rather than discouraged | Full GitOps for business configuration; business users must be able to change a threshold without a pull request. The line is drawn at technical versus business parameters — which is exactly the M30/M64 boundary |

**Design position.** Four deliberate differences.

First, **a branch is a configuration object, not a project**. The category KPI is under one day
to stand up a branch, against weeks today. That is achievable only if creating a branch
provisions its operating unit, stock location, cash drawer, queue, working calendar, zone
membership, user groups, printer profile and portal visibility in **one governed action**.
Anything less and the checklist reappears, with the omissions that come with it. M67 still
manages the *branch opening project* — premises, fit-out, staffing — but the *system* side is
one action.

Second, **technical configuration and business parameters are deliberately separated**. Most
ERP programmes put every setting in one place, and then either data stewards get administrator
rights or administrators approve business thresholds. Neither is acceptable. A timeout, a batch
size and a feature flag are M30's; a discount ceiling, an approval threshold and a warranty
period are M64's, under stewardship. The test is: *would getting this wrong break the system,
or break the business?*

Third, **configuration changes are promoted, not made**. OPS-02 is enforced technically: the
production configuration API rejects direct writes for versioned parameters, accepting only a
promotion from a lower environment with an approved change record (BRU-ADM-02). This is
inconvenient in an emergency, so an explicit, loud, time-boxed emergency path exists rather
than a quiet exception.

Fourth, **the health console is operational, not analytical, and it is one console**. Six
modules could each build a dashboard. The category defines a single view — platform, jobs,
integrations, security signals and capacity in one place — because the person on call at 2am
must not have to know which module owns the symptom.

---

## 5. Functional Areas & Features

### 5.1 Organisation Structure

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ADM-001 | Legal entity register | Maintain legal entities with registration details, fiscal configuration and status; **the country dimension and its pack are supplied by M65** | **P0** | L1/L5 |
| FR-ADM-002 | **Branch register** | Maintain the 51+ branches as operating units with code, name, address, geography, contact, capabilities, service lines offered, opening hours, status and parent entity | **P0** | L2/L5 |
| FR-ADM-003 | **Single-action branch provisioning** | Stand up a new branch in one governed action, creating its operating unit, stock location, cash drawer, queue configuration, working calendar, zone membership, user groups, printer and device profile, and portal visibility | **P0** | L5 |
| FR-ADM-004 | Branch capability profile | Record which services, device categories and repair levels a branch can perform, so that intake, dispatch and booking respect it | **P0** | L5 |
| FR-ADM-005 | Zone definition | Define dispatch zones with geographic boundaries, branch membership and coverage rules | **P0** | L5 |
| FR-ADM-006 | Cost centre hierarchy | Maintain a cost centre hierarchy with owners, mapped to entities and branches | **P0** | L1/L5 |
| FR-ADM-007 | Business line register | Maintain the nine business lines from `02-01` §9 as a reporting and attribution dimension | **P0** | L5 |
| FR-ADM-008 | Working calendars | Maintain working calendars, shift patterns, branch-specific opening hours and public holidays, including moon-dependent dates supplied by M65 | **P0** | L1/L5 |
| FR-ADM-009 | **Dimensional guarantee** | Ensure every record in every module carries `company_id`, `operating_unit_id` and, where applicable, `zone_id`, `cost_center_id`, `business_line_id` and `currency_id`; verify in CI (AS-03) | **P0** | L5 |
| FR-ADM-010 | Branch lifecycle | Open, suspend, relocate, merge and close a branch, with data continuity, historical reporting integrity and reassignment of open work | P1 | L5 |
| FR-ADM-011 | Organisation change history | Retain the full history of organisational structure so that historical reporting reflects the structure in force at the time | P1 | L5 |
| FR-ADM-012 | User administration | Provide the operational administration surface for users — creation, branch assignment, deactivation — **delegating every identity and permission decision to M29** | **P0** | L5 |

### 5.2 Configuration Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ADM-013 | **Configuration registry** | Maintain a registry of every technical configuration parameter with key, type, default, current value, scope (global/entity/branch), owning module, description and business impact | **P0** | L5 |
| FR-ADM-014 | Scoped configuration | Resolve a parameter by scope precedence — branch overrides entity overrides global — with the effective value and its source visible | **P0** | L5 |
| FR-ADM-015 | Configuration versioning | Version every configuration change with actor, timestamp, previous value, reason and change record reference | **P0** | L5 |
| FR-ADM-016 | **Promotion, not editing** | Promote configuration through the environment ladder; **reject a direct write to a versioned production parameter** unless it arrives as an approved promotion (OPS-02, BRU-ADM-02) | **P0** | L5 |
| FR-ADM-017 | Emergency configuration change | Provide an explicit, loud, time-boxed emergency path with immediate multi-party notification and mandatory retrospective change record | **P0** | L5 |
| FR-ADM-018 | Configuration rollback | Roll back any configuration change to a prior version in one action, with the same audit trail | **P0** | L5 |
| FR-ADM-019 | Configuration validation | Validate a parameter against its type, range and dependency constraints before it takes effect, and reject an invalid value at the point of change | **P0** | L5 |
| FR-ADM-020 | Configuration comparison | Compare configuration between environments and report divergence | P1 | L5 |
| FR-ADM-021 | Licence register | Maintain the register of open-source and commercial component licences with obligations and review dates (`02-05` §4) | P2 | L5 |

### 5.3 Feature Flags & Release Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ADM-022 | **Feature flag registry** | Maintain flags with key, description, owning module, state, targeting rules, creation date and planned removal date | **P0** | L5 |
| FR-ADM-023 | Targeted rollout | Target a flag by entity, branch, role, named user or percentage of users, and change targeting without a deployment | **P0** | L5 |
| FR-ADM-024 | **Kill switch** | Disable any flagged capability estate-wide in one action, taking effect within 60 seconds, without a deployment (OPS-06) | **P0** | L5 |
| FR-ADM-025 | Flag evaluation service | Provide a low-latency evaluation service that every module and portal calls, with a safe default when the service is unreachable | **P0** | L5 |
| FR-ADM-026 | Flag telemetry correlation | Record which flag state applied to a request, so performance and error rates can be attributed to a flag | P1 | L5 |
| FR-ADM-027 | Stale flag management | Report flags past their planned removal date and flags with unchanged state beyond a threshold, to prevent permanent accumulation | P2 | L5 |
| FR-ADM-028 | Change freeze | Declare and enforce change freeze periods during which promotions and non-emergency flag changes are blocked | P1 | L5 |

### 5.4 Environments, Jobs & Background Processing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ADM-029 | Environment registry | Maintain the environment ladder — local, dev, staging, training, prod, dr — with purpose, data policy, refresh cadence and access | **P0** | L5 |
| FR-ADM-030 | Environment refresh | Refresh a non-production environment from production **with masking applied and verified by M29 before release** (NFR-071, BRU-SEC-08) | **P0** | L5 |
| FR-ADM-031 | **Scheduled job registry** | Register every scheduled and background job with owner, schedule, expected duration, SLA, dependencies and failure impact | **P0** | L5 |
| FR-ADM-032 | **Job execution monitoring** | Record success, failure and duration for every run; alert on failure, on overrun beyond expected duration, and on a missed run; **silent failure is a defect** (OPS-05) | **P0** | L5 |
| FR-ADM-033 | Job control | Enable, disable, reschedule, trigger manually and prevent overlapping execution of any registered job | **P0** | L5 |
| FR-ADM-034 | Queue and worker health | Monitor background queue depth, worker availability and processing latency, with alerting and scaling signals | **P0** | L4/L5 |

### 5.5 Health, Observability & Operations

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ADM-035 | **Platform health console** | Present one operational view: application and database health, job status, queue depth, **integration health from M28**, security signals from M29, capacity and active incidents | **P0** | L4/L5 |
| FR-ADM-036 | Alert registry and routing | Maintain every alert with severity, threshold, routing and a **mandatory runbook link**; remove alerts that have no action (OPS-03) | **P0** | L5 |
| FR-ADM-037 | Capacity monitoring | Monitor utilisation against growth, review monthly, and signal scaling decisions ahead of need (OPS-08, NFR-009) | P1 | L4/L5 |
| FR-ADM-038 | Runbook registry | Hold an operational runbook for every module and every alert, and block a module's release without one (NFR-091) | **P0** | L5 |

### 5.6 Data Lifecycle, Continuity & Communication

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ADM-039 | **Archival, backup and continuity** | Execute archive policies by object and age with retrieval on demand and storage tiering; configure and verify backups — daily 30-day, weekly 1-year, monthly 7-year (NFR-030) with **automated weekly restore testing** (NFR-052); maintain the DR configuration and failover procedure to RPO ≤ 15 min and RTO ≤ 2 h (NFR-007), exercised in **twice-yearly drills** (NFR-051); and schedule planned maintenance outside 08:00–23:00 BST, capped at 4 hours per month and announced 72 hours ahead (NFR-049) | **P0** | L5 |
| FR-ADM-040 | **System announcements** | Publish operational announcements to internal users — planned maintenance, degraded service, release notes, policy changes — targeted by role, branch or entity, in Bengali and English, with acknowledgement tracking where required | P1 | L5 |

> **Note on grouping.** FR-ADM-039 aggregates archival, backup, disaster recovery and
> maintenance windows into one requirement because they are a single operational discipline
> with a single owner and a common evidence set. Each sub-obligation is separately testable and
> appears individually in §17.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Dimensional enforcement in CI** | A model without `company_id` and `operating_unit_id` fails the model-registry check and the build (AS-03). This is what makes promise 5 real rather than aspirational |
| T-02 | **Configuration resolution performance** | Parameter resolution is cached with invalidation on change; effective-value lookup ≤ 2 ms. Configuration read on a hot path must never be a database round trip |
| T-03 | **Production write rejection** | The configuration service rejects direct writes to versioned production parameters at the API layer, not by convention. The emergency path is a distinct, audited, notifying endpoint |
| T-04 | **Feature flag evaluation latency and safety** | Flag evaluation ≤ 1 ms from local cache; on cache miss and service unavailability, the flag returns its **safe default** rather than failing the request |
| T-05 | **Kill-switch propagation** | A kill switch takes effect estate-wide within 60 seconds through cache invalidation, not at next restart |
| T-06 | **Branch provisioning atomicity** | Branch provisioning is transactional across every dependent object; a partial provision is impossible. Failure rolls back completely and reports which step failed |
| T-07 | **Organisational history** | Structure changes are effective-dated and never destructive, so a report for a past period reflects the structure in force then |
| T-08 | **Job overlap prevention** | Every registered job takes a distributed lock; a run cannot start while its predecessor is running unless explicitly declared concurrent-safe |
| T-09 | **Missed-run detection** | The scheduler detects a run that did not start, not merely one that failed. A job silently not running is the most common and least visible operational failure |
| T-10 | **Observability cardinality discipline** | Metrics are dimensioned by entity, branch, module and job — never by customer, order or device id |
| T-11 | **Alert-runbook integrity** | An alert cannot be registered without a runbook link; a runbook link that 404s fails the weekly check |
| T-12 | **Masked refresh gate** | A non-production environment cannot be released for use until M29 confirms masking verification passed (NFR-086c) |
| T-13 | **Archive retrievability** | Archived data is retrievable within 10 seconds for the current statutory window and within 24 hours beyond it, and archival never breaks referential integrity |
| T-14 | **Zero-downtime configuration** | Configuration and flag changes take effect without restart, and no configuration change requires a deployment (NFR-008, OPS-06) |
| T-15 | **Scale envelope** | 200 branches without configuration redesign (NFR-058); 10 legal entities across 5 countries (NFR-059); ~800 registered jobs at Wave 8 |
| T-16 | **No business logic** | M30 evaluates configuration and flags; it never interprets business meaning. Verified by dependency analysis |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M30 |
|---|---|---|
| **Branch manager** | A new branch takes weeks of coordination and something is always missed | Branch stood up in under a day, complete, with nothing forgotten |
| **Operations director** | Cannot see which branches are configured for which services | One register: every branch, its capabilities, its hours, its zone |
| **IT administrator** | Edits production settings by hand and hopes; finds out a job failed when a report is wrong | Promotes versioned configuration; every job monitored with failure, overrun and missed-run alerts |
| **CTO** | No single view of platform state | One health console covering application, jobs, integrations, security and capacity |
| **Developer / release manager** | A bad release means an emergency deployment | The capability is flagged off in 60 seconds without a deployment |
| **Finance** | Cost centre structure lives in a spreadsheet and diverges from the system | One hierarchy, used by every module and by M54 budgeting |
| **All staff** | Learn about maintenance when the system is down | Announcements 72 hours ahead, targeted, in Bengali and English |
| **Auditor** | Cannot establish what the configuration was at a past date | Versioned configuration with effective dates and change records |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Branch opening speed** | Single-action provisioning of every system dependency | **From weeks to under one day** — the category KPI. With the 1000FiX Station expansion programme active, this converts directly into revenue-earning days per branch opened |
| **Change without code release** | Business-relevant settings, thresholds and toggles configurable rather than coded | **> 95% of configuration changes without a code release** (with M64). Each avoided release is days of development, testing and deployment risk |
| **Release risk reduction** | Kill switch disables any new capability in 60 seconds | Turns a bad release from an emergency deployment into a toggle. This is what makes weekly delivery safe across 67 modules |
| **Silent failure elimination** | Every job monitored for failure, overrun **and missed run** | A nightly job that stops running is discovered in minutes rather than in the month-end reconciliation. Protects the KPI-050 three-day close and every downstream data dependency |
| **Incident response time** | One health console with alert-to-runbook linkage | The on-call engineer does not need to know which module owns the symptom. Directly supports NFR-006 (99.9% business-hours uptime) |
| **Continuity assurance** | Verified backups weekly, DR drills twice yearly, RPO ≤ 15 min, RTO ≤ 2 h | A backup that has never been restored is a hope, not a control. This is the difference between a bad day and an existential event |
| **Capacity cost control** | Monthly capacity review with scaling ahead of need | Avoids both the outage of under-provisioning and the waste of over-provisioning across the **$450–5,800/month** infrastructure progression |
| **Expansion readiness** | Entity and dimensional model designed for multi-entity from Wave 1 | Retrofitting multi-entity into a live single-entity system typically costs **3–5×** what designing for it costs — the explicit category risk. Supports **BO-18** |
| **Audit position** | Versioned configuration traceable to approved change records | Supports **BO-10 (zero compliance findings)** and removes a standard audit weakness |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Operational discipline** | OPS-01 to OPS-08 encoded in a system rather than in a handbook. Standards that are enforced are followed |
| **Reduced key-person risk** | Runbooks are mandatory and registered; the platform can be operated by someone other than the person who built it |
| **ISO 9001 and 27001 evidence** | Change control, configuration management, backup verification and business continuity are explicit clauses in both |
| **Blameless operations culture** | Monitoring that catches problems early, and kill switches that make recovery cheap, change how teams behave about risk |
| **Institutional memory of structure** | Effective-dated organisational history means a question about last year's branch structure has an answer |
| **Licence compliance** | The obligations of AGPL, LGPL, BSL and Sustainable Use components are registered and reviewed annually rather than discovered in diligence |
| **Foundation for M64, M65, M66 and M67** | All four extend structures M30 defines. Getting the dimensional model right in Wave 1 is what makes them additive rather than disruptive |

---

## 8. Lifecycle & State Models

### 8.1 Branch Lifecycle

```
        ┌──────────────┐
        │   PLANNED    │  ◄── created by an M67 branch-opening project
        └──────┬───────┘
               │ **single-action provisioning** (FR-ADM-003):
               │ operating unit · stock location · cash drawer · queue ·
               │ calendar · zone · user groups · printers · portal visibility
        ┌──────▼───────┐
        │ PROVISIONED  │  configured but not trading
        └──────┬───────┘
               │ staff assigned, opening stock counted, go-live approved
        ┌──────▼───────┐
        │    ACTIVE    │◄──────────────┐
        └──┬───┬───┬───┘               │
           │   │   │ capability change │ resumed
           │   │   └───────────────────┤
           │   │                       │
           │   │ temporary closure     │
           │   ▼                       │
           │ ┌────────────┐            │
           │ │ SUSPENDED  │────────────┘
           │ │ no new     │
           │ │ intake;    │
           │ │ open work  │
           │ │ continues  │
           │ └────────────┘
           │
           │ relocation or merge
           ▼
        ┌──────────────┐
        │  RELOCATING  │  address and geography change;
        │  / MERGING   │  open work and stock transferred
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │    ACTIVE    │  (at the new location or absorbed into the target)
        └──────────────┘

        ┌──────────────┐
        │    CLOSED    │  ◄── from Active or Suspended:
        └──────────────┘      open work reassigned · stock transferred ·
                              cash reconciled · staff reassigned ·
                              **history retained; the branch is never deleted**
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Planned | Branch-opening project initiated (M67) or direct request | Operations Director |
| Planned | Provisioned | Provisioning action completes atomically across every dependency | IT Administrator |
| Provisioned | Active | Staff assigned, opening stock counted (M15), go-live approved | Operations Director |
| Active | Suspended | Temporary closure approved; no new intake accepted; open work continues | Operations Director |
| Suspended | Active | Resumption approved | Operations Director |
| Active | Relocating / Merging | Change approved; open work and stock transfer planned | Operations Director + CTO |
| Active / Suspended | Closed | Open work reassigned, stock transferred, cash reconciled, staff reassigned | Operations Director + CFO |
| Closed | (never) Deleted | Historical reporting integrity requires retention | — |

### 8.2 Configuration Change Lifecycle

```
   PROPOSED ──► validated against type, range and dependencies (FR-ADM-019)
       │        ✖ invalid ──► REJECTED with the reason
       ▼
   APPROVED ──► change record raised; approver recorded (BRU-ADM-02)
       │
       ▼
   PROMOTED to dev ──► verified
       │
       ▼
   PROMOTED to staging ──► verified
       │
       │  ✖ change freeze active ──► HELD (FR-ADM-028)
       ▼
   PROMOTED to production ──► effective immediately, no restart (T-14)
       │
       ├──► adverse effect observed ──► ROLLED BACK (FR-ADM-018)
       │                                 one action, same audit trail
       ▼
   ACTIVE ──► versioned; prior value retained; effective-dated


   EMERGENCY PATH (FR-ADM-017)
   ───────────────────────────
   EMERGENCY CHANGE ──► applied directly to production
       │                 multi-party notification immediately
       │                 time-boxed
       ▼
   RETROSPECTIVE CHANGE RECORD ──► mandatory within 24 h
       │                            ✖ not filed ──► escalate to CTO;
       │                                            change auto-reverted
       ▼
   REGULARISED ──► promoted through the ladder to match
```

### 8.3 Scheduled Job Run

```
   SCHEDULED ──► due
       │
       ├──► predecessor still running ──► SKIPPED (overlap prevented, T-08)
       │                                   └► alert if repeated
       │
       ├──► did not start ──► **MISSED** (T-09) ──► alert immediately
       │
       ▼
   RUNNING ──► duration tracked against expected
       │
       ├──► exceeds expected duration ──► OVERRUNNING ──► alert
       │
       ├──► error ──► FAILED ──► alert with runbook link ──► retry per policy
       │                          └► repeated failure ──► M66 incident
       ▼
   COMPLETED ──► success, duration and record count logged (OPS-05)
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-ADM-01 | Master data changes above the defined significance require approval before taking effect *(the rule remains; **execution transfers to M64** under the v2.1 re-scope)* | **H** | CTO |
| BRU-ADM-02 | **Configuration changes in production must be traceable to an approved change record** | **H** | CTO |
| BRU-ADM-03 | Production configuration is promoted through the environment ladder, never hand-edited (OPS-02) | **H** | CTO |
| BRU-ADM-04 | An emergency configuration change notifies multiple parties immediately, is time-boxed, and requires a retrospective change record within 24 hours or is automatically reverted | **H** | CTO |
| BRU-ADM-05 | Every record in every module carries `company_id` and `operating_unit_id` (AS-03) | **H** | CTO |
| BRU-ADM-06 | A branch is provisioned atomically; a partial provision is rolled back completely | **H** | CTO |
| BRU-ADM-07 | A branch is never deleted; closure retains history | **H** | CTO |
| BRU-ADM-08 | Organisational structure changes are effective-dated; historical reporting reflects the structure in force at the time | **C** | CFO / CTO |
| BRU-ADM-09 | Every new capability is behind a feature flag and can be disabled without a deployment (OPS-06) | **H** | CTO |
| BRU-ADM-10 | A feature flag returns its safe default when the evaluation service is unavailable; it never fails the request | **H** | CTO |
| BRU-ADM-11 | Every scheduled job is registered with an owner, an expected duration and a failure impact; an unregistered job cannot run in production | **H** | CTO |
| BRU-ADM-12 | Every job reports success, failure and duration; **silent failure is a defect** (OPS-05) | **H** | CTO |
| BRU-ADM-13 | A job cannot overlap its own previous run unless declared concurrent-safe | **H** | CTO |
| BRU-ADM-14 | Every alert has a runbook entry; an alert without an action is removed (OPS-03) | **H** | CTO |
| BRU-ADM-15 | Every module ships an operational runbook; a module without one cannot be released (NFR-091) | **H** | CTO |
| BRU-ADM-16 | A non-production environment cannot be released for use until M29 confirms masking verification passed | **H** | CTO |
| BRU-ADM-17 | Backups are restore-tested weekly; an unverified backup is treated as no backup (NFR-052) | **H** | CTO |
| BRU-ADM-18 | Disaster recovery is exercised twice yearly with documented results (NFR-051) | **H** | CTO |
| BRU-ADM-19 | Planned maintenance occurs outside 08:00–23:00 BST, is capped at 4 hours per month, and is announced 72 hours ahead (NFR-049) | **H** | CTO |
| BRU-ADM-20 | Archived data remains retrievable and never breaks referential integrity | **H** | CTO |
| BRU-ADM-21 | Data is soft-deleted only; hard deletion requires an approved, logged procedure (DI-08) | **H** | CTO |
| BRU-ADM-22 | During a declared change freeze, promotions and non-emergency flag changes are blocked | **H** | CTO |
| BRU-ADM-23 | M30 holds technical configuration only; business thresholds and parameters belong to M64 | **C** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

Derived from the 17 entities allocated to M30 in `05-02` §M30, **less the five that move to M64
and M65** under the v2.1 re-scope, plus entities this specification adds.

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.entity` | `fix_entity` | Legal entity | code, name, registration_no, tax_ids, base_currency, fiscal_year_start, country_id *(M65)*, country_pack_id *(M65)*, status, parent_entity_id |
| `fix.branch` | `fix_branch` | **The operating unit** | code, name, entity_id, operating_unit_id, address, geo_point, contact, capabilities, service_lines, opening_hours, calendar_id, zone_ids, status, opened_on, closed_on, parent_branch_id |
| `fix.zone` | `fix_zone` | Dispatch zone | code, name, entity_id, boundary_geojson, branch_ids, coverage_rules, active |
| `fix.cost.center` | `fix_cost_center` | Cost centre hierarchy | code, name, parent_id, entity_id, branch_id, owner_user_id, active, effective_from |
| `fix.business.line` | `fix_business_line` | The nine business lines | code, name, description, revenue_model, owning_role, active |
| `fix.working.calendar` | `fix_working_calendar` | Calendars and shifts | code, name, entity_id, branch_id, shift_patterns, weekly_hours, holiday_set_ref *(M65)*, timezone |
| `fix.org.change` | `fix_org_change` | Effective-dated structure history | object_type, object_id, change_type, previous_state, new_state, effective_from, approved_by, reason |
| `fix.config.parameter` | `fix_config_parameter` | **Technical configuration registry** | key, type, default_value, description, scope_level, owning_module, business_impact, validation_rule, is_versioned, requires_approval |
| `fix.config.value` | `fix_config_value` | Scoped effective values | parameter_id, scope_level (global/entity/branch), scope_id, value, environment, effective_from, effective_to |
| `fix.config.version` | `fix_config_version` | Change history and rollback | parameter_id, scope_id, version, previous_value, new_value, changed_by, changed_at, reason, change_record_ref, promoted_from_env, emergency, rolled_back_at |
| `fix.feature.flag` | `fix_feature_flag` | Flag registry | key, description, owning_module, state, safe_default, targeting_rules_json, created_at, planned_removal_date, last_changed_by, kill_switched_at |
| `fix.feature.flag.evaluation` | `fix_feature_flag_evaluation` | Telemetry correlation | flag_key, request_correlation_id, resolved_state, targeting_reason, evaluated_at |
| `fix.environment` | `fix_environment` | The environment ladder | code (local/dev/staging/training/prod/dr), purpose, data_policy, refresh_cadence, last_refreshed_at, masking_verified_at, access_roles |
| `fix.change.freeze` | `fix_change_freeze` | Freeze periods | name, from, to, scope, reason, declared_by, exceptions_allowed |
| `fix.scheduled.job` | `fix_scheduled_job` | **Job registry** | code, name, owning_module, schedule_cron, expected_duration_sec, sla_sec, concurrent_safe, dependencies, failure_impact, owner_user_id, runbook_ref, enabled |
| `fix.job.run` | `fix_job_run` | Execution record | job_id, scheduled_for, started_at, completed_at, duration_sec, state (completed/failed/missed/skipped/overrunning), record_count, error_detail, alerted |
| `fix.platform.alert` | `fix_platform_alert` | Alert registry | code, name, source, severity, threshold_expression, routing, **runbook_ref (mandatory)**, active, last_fired_at, fire_count_30d |
| `fix.runbook` | `fix_runbook` | Operational runbooks | scope (module/alert/procedure), reference, title, document_id, owner_user_id, last_reviewed_at, next_review_due |
| `fix.capacity.metric` | `fix_capacity_metric` | Capacity tracking | resource, dimension, measured_at, current_value, headroom_pct, growth_rate, projected_exhaustion, review_note |
| `fix.archive.policy` | `fix_archive_policy` | Archival configuration | model, criteria, age_threshold, target_tier, retrieval_sla, retention_class_ref *(M24)*, active |
| `fix.archive.run` | `fix_archive_run` | Archival execution | policy_id, run_at, records_archived, bytes, target_location, verified, error_detail |
| `fix.backup.verification` | `fix_backup_verification` | Restore testing | backup_ref, backup_type, taken_at, restore_tested_at, restore_duration_sec, result, tested_by |
| `fix.dr.drill` | `fix_dr_drill` | DR exercise record | drill_date, scope, rpo_achieved_min, rto_achieved_min, issues_found, actions, signed_off_by |
| `fix.maintenance.window` | `fix_maintenance_window` | Planned maintenance | scheduled_from, scheduled_to, scope, impact, announced_at, announcement_id, actual_from, actual_to, overran |
| `fix.system.announcement` | `fix_system_announcement` | Internal communication | title_bn, title_en, body_bn, body_en, severity, target_roles, target_branches, target_entities, publish_from, publish_to, acknowledgement_required, acknowledged_count |
| `fix.component.licence` | `fix_component_licence` | Licence register | component, version, licence, obligation_summary, compliance_note, reviewed_at, next_review_due |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.country.pack`, `fix.locale.pack`, holiday sets, currency rules | **M65** | Read; **moved out of M30 in v2.1** |
| `fix.master.data.domain`, `fix.mdm.change.request` | **M64** | Read; **moved out of M30 in v2.1** |
| `fix.identity`, `fix.role`, masking verification | M29 | Read; user administration delegates every access decision |
| `fix.integration.health`, `fix.integration.config` | M28 | Read for the health console |
| `fix.security.event`, `fix.security.incident` | M29 | Read for the health console |
| `fix.it.major.incident`, `fix.it.change` (ITIL process) | M66 | Platform alerts raise incidents; change records reference M66's process |
| `fix.document`, retention class, legal hold | M24 | Read before archival or purge |
| `fix.budget`, cost-centre budgets | M54 | Referenced, not owned |
| `fix.project` (branch opening) | M67 | Read; a branch-opening project triggers provisioning |
| Vault secret references | Platform infrastructure | Managed here, resolved by M28 and M29 |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-ADM-01 | Branch provisioning requested | Create the operating unit, stock location, cash drawer, queue configuration, working calendar, zone membership, user groups, printer profile and portal visibility — atomically | **Roll back completely**; report the failing step |
| AUT-ADM-02 | Branch status changes to Closed | Reassign open work, initiate stock transfer, require cash reconciliation, notify affected modules; retain all history | Block closure until open items are cleared |
| AUT-ADM-03 | Model deployed without `company_id` or `operating_unit_id` | Fail the build with the offending model named (AS-03) | **Hard block in CI** |
| AUT-ADM-04 | Configuration change proposed | Validate type, range and dependencies; route for approval where the parameter requires it | Reject invalid values with the reason |
| AUT-ADM-05 | Direct write attempted on a versioned production parameter | Reject and point to the promotion path | **Hard block**; security event raised |
| AUT-ADM-06 | Emergency configuration change applied | Notify CTO, IT Administrator and the module owner immediately; start the 24-hour retrospective clock | Escalate |
| AUT-ADM-07 | Emergency change record not filed within 24 hours | **Revert the change automatically**; escalate to CTO | Hard revert |
| AUT-ADM-08 | Configuration promoted to production | Apply without restart; invalidate caches; record the version and the change record reference | Roll back; alert |
| AUT-ADM-09 | Kill switch activated | Propagate estate-wide within 60 seconds; notify the module owner and the CTO | Escalate; force cache invalidation |
| AUT-ADM-10 | Flag past its planned removal date | Report to the owning module team monthly; escalate at 90 days overdue | Report only |
| AUT-ADM-11 | Change freeze declared | Block promotions and non-emergency flag changes; notify all module teams | Hard block |
| AUT-ADM-12 | Scheduled job completes | Log success, duration and record count; compare against expected duration | — |
| AUT-ADM-13 | **Scheduled job fails** | Alert with the runbook link; retry per policy; raise an M66 incident on repeated failure | Escalate to the job owner and CTO |
| AUT-ADM-14 | **Scheduled job does not start when due** | Alert immediately as a missed run — distinct from a failure | Escalate |
| AUT-ADM-15 | Job exceeds its expected duration | Alert as overrunning; provide the option to terminate | Alert only |
| AUT-ADM-16 | Job attempts to start while its predecessor runs | Skip the run and log; alert if skipping repeats | — |
| AUT-ADM-17 | Queue depth or worker health breaches threshold | Alert; signal scaling where automatic scaling applies | Escalate |
| AUT-ADM-18 | Non-production refresh requested | Copy, apply masking, **request M29 verification**, release only on confirmation | Block release; alert |
| AUT-ADM-19 | Weekly | Execute an automated restore test against a recent backup and record the result (NFR-052) | Alert as a **critical** failure |
| AUT-ADM-20 | Twice yearly | Schedule and run the DR drill; record RPO and RTO achieved and issues found (NFR-051) | Escalate to CTO and CEO |
| AUT-ADM-21 | Maintenance window scheduled | Publish the announcement 72 hours ahead in Bengali and English, targeted by role and branch | Block the window until announced |
| AUT-ADM-22 | Archive policy due | Execute archival, verify retrievability, tier the storage, record the run | Alert; retain data in place |
| AUT-ADM-23 | Monthly | Produce the capacity review with utilisation, growth rate and projected exhaustion (OPS-08) | Report only |
| AUT-ADM-24 | Alert registered without a runbook link, or a runbook link fails its weekly check | Block registration; flag the broken link for the owner | Hard block on registration |
| AUT-ADM-25 | Module release attempted without a runbook | Block the release (NFR-091) | **Hard block** |

---

## 12. Interfaces

### 12.1 Upstream — M30 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M29 Identity** | Administrator authorisation; masking verification for environment refresh; security signals for the health console | REST + events |
| **M28 Integration** | Integration health, event platform telemetry, gateway metrics | Events + REST |
| **M65 Localisation** | Country packs, locale packs, holiday sets, currency rules, fiscal calendars | REST |
| **M64 MDM** | Business master data and parameters — referenced, not owned | REST |
| M66 ITSM | Change process records that a configuration change references | REST |
| M67 PPM | Branch-opening projects that trigger provisioning | Events |
| M24 Documents | Retention class and legal hold before archival | REST |
| M54 FP&A | Cost-centre budget context | REST |
| Infrastructure (Prometheus, Loki, Tempo, K3s) | Metrics, logs, traces, cluster state | Scrape / query |

### 12.2 Downstream — M30 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **Every module (all 66)** | Entity, branch, zone, cost centre, business line and calendar context; configuration parameters; feature flag evaluation | REST + framework |
| **All 12 portals** | Branch directory, opening hours, capabilities, announcements, feature flags | REST |
| **M29 Identity** | Organisation structure as the record-rule dimensions | REST |
| **M28 Integration** | Entity and environment context; scheduled-job registry for batch exchange; vault references | REST |
| M02 Field Service | Zones, branch capabilities, working calendars | REST |
| M15 Inventory | Branch stock locations created at provisioning | Events |
| M04 Branch Operations | Queue and cash-drawer configuration created at provisioning | Events |
| M19 / M54 | Entity, cost centre and business line as posting and reporting dimensions | REST |
| M66 ITSM | Platform alerts and job failures raising IT incidents | Events |
| M25 BI / M62 | Organisation dimensions for reporting; platform telemetry | Warehouse extract |
| M67 PPM | Branch provisioning completion as a project milestone | Events |
| Portal platform (CON-03) | Branch and coverage data | Events (`05-03` §3.1) |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `branch.provisioned` | branch, entity, zone, capabilities, dependent objects created | **All modules**, portal, M67 |
| `branch.activated` | branch, opened on, service lines | M01, M02, M04, M15, portal |
| `branch.suspended` | branch, reason, effective from | M01, M02, M04, portal |
| `branch.closed` | branch, closed on, work reassigned to, stock transferred to | All modules, portal |
| `branch.capability_changed` | branch, capabilities added, removed | M01, M02, M36, portal |
| `entity.created` | entity, country, base currency, fiscal year | M19, M29, M65 |
| `zone.changed` | zone, boundary, branch membership | M02, M03 |
| `cost_center.changed` | cost centre, parent, owner, effective from | M19, M54 |
| `config.changed` | parameter, scope, previous value, new value, actor, change record | Owning module, M66 |
| `config.emergency_change` | parameter, value, actor, notification recipients | CTO, M66, M29 |
| `config.rolled_back` | parameter, from version, to version, actor, reason | Owning module, M66 |
| `feature_flag.changed` | flag, previous state, new state, targeting, actor | Owning module, M25 |
| `feature_flag.kill_switched` | flag, actor, reason, propagation time | Owning module, CTO, M66 |
| `job.failed` | job, run, error, duration, owner, runbook | **M66**, owning module |
| `job.missed` | job, scheduled for, owner, failure impact | **M66**, owning module |
| `job.overran` | job, run, expected duration, actual duration | Owning module |
| `platform.alert_fired` | alert, severity, source, runbook | **M66**, on-call |
| `environment.refreshed` | environment, source, masking verified, released at | M29, all teams |
| `backup.verification_failed` | backup, type, failure reason | **CTO**, M66 |
| `dr.drill_completed` | drill, RPO achieved, RTO achieved, issues | CTO, CEO, M23 |
| `maintenance.scheduled` | window, scope, impact, announcement | All users, M27, M66 |
| `announcement.published` | announcement, targeting, acknowledgement required | All users |
| `archive.completed` | policy, records archived, target tier | M24, M62 |
| `capacity.threshold_breached` | resource, headroom, projected exhaustion | CTO, M66 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-ADM-01 | **Prometheus / Loki / Tempo / Grafana** | Inbound | Metrics, logs, traces and dashboards feeding the health console |
| INT-ADM-02 | **K3s / Docker orchestration** | Bidirectional | Cluster state, worker health, scaling signals |
| INT-ADM-03 | **PostgreSQL / PgBouncer** | Inbound | Database health, connection pool, replication lag |
| INT-ADM-04 | Backup and object storage (MinIO) | Bidirectional | Backup execution, verification restore, archive tiering |
| INT-ADM-05 | **HashiCorp Vault** | Bidirectional | Secret registry and rotation scheduling *(M29 owns key policy; M30 owns the operational registry)* |
| INT-ADM-06 | CI/CD pipeline | Bidirectional | Deployment records, configuration promotion, build gates |
| INT-ADM-07 | Alerting channels (email, SMS, WhatsApp, on-call rotation) | Outbound | Alert routing — delivered through M27's channels |
| INT-ADM-08 | Cloud provider APIs | Bidirectional | Infrastructure capacity, cost and scaling |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/admin/branches` | GET/POST | Branch register and provisioning | P03, portal, all modules |
| `/api/v1/admin/branches/{id}/provision` | POST | **Single-action branch provisioning** | P03 |
| `/api/v1/admin/branches/{id}/status` | POST | Suspend, resume, relocate or close | P03 |
| `/api/v1/branches` | GET | Public branch directory with capabilities and hours | **Portal (CON-03)**, P01 |
| `/api/v1/admin/entities` | GET/POST | Legal entity register | P03, M19, M65 |
| `/api/v1/admin/zones` | GET/POST | Zone definition and coverage | P03, M02, M03 |
| `/api/v1/admin/cost-centers` | GET/POST | Cost centre hierarchy | P03, M19, M54 |
| `/api/v1/admin/calendars` | GET | Working calendars and holidays | All modules |
| `/api/v1/config/{key}` | GET | **Resolve a parameter's effective value for a scope** | All modules |
| `/api/v1/admin/config` | GET/POST | Configuration registry and change proposal | P03 |
| `/api/v1/admin/config/promote` | POST | Promote configuration between environments | P03, CI/CD |
| `/api/v1/admin/config/{id}/rollback` | POST | Roll back to a prior version | P03 |
| `/api/v1/admin/config/emergency` | POST | Emergency change (loud, time-boxed, notifying) | P03 |
| `/api/v1/flags/evaluate` | POST | **Evaluate flags for a context — called on every request path that needs one** | All modules, all portals |
| `/api/v1/admin/flags` | GET/POST | Flag registry and targeting | P03 |
| `/api/v1/admin/flags/{key}/kill` | POST | **Kill switch** | P03 |
| `/api/v1/admin/jobs` | GET/POST | Scheduled job registry | P03, all modules |
| `/api/v1/admin/jobs/{id}/run` | POST | Trigger manually | P03 |
| `/api/v1/admin/jobs/runs` | GET | Execution history with state and duration | P03, M66 |
| `/api/v1/admin/health` | GET | **The platform health console feed** | P03, P06 |
| `/api/v1/admin/alerts` | GET/POST | Alert registry with runbook links | P03 |
| `/api/v1/admin/environments` | GET | Environment ladder and refresh state | P03 |
| `/api/v1/admin/environments/{id}/refresh` | POST | Masked refresh (gated on M29 verification) | P03 |
| `/api/v1/admin/announcements` | GET/POST | System announcements | P03, all portals |
| `/api/v1/admin/capacity` | GET | Capacity and growth projection | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | All; sole approver of emergency changes, change freezes and DR sign-off |
| R33 IT / System Administrator | C R U D A | All operational functions: provisioning, promotion, flags, jobs, environments, archival |
| R05 Operations Director | C R U A | Branch lifecycle, zones, capabilities, calendars; approves branch opening and closure |
| R06 Branch Manager | R U | **Own branch** configuration within a bounded set: opening hours, contact, local announcements |
| R03 Chief Financial Officer | R A | Entity, cost centre and business line structure; approves branch closure |
| R26 Finance Manager | R | Cost centre and business line structure |
| R30 HR Manager | R | Branch register and working calendars for workforce planning |
| R32 Quality Manager / ISO Coordinator | R | Backup verification, DR drills, runbook currency, change control evidence |
| R01 Chief Executive Officer | R | Platform health summary, capacity, continuity posture |
| All internal users | R | Announcements targeted to them; branch directory |

**Configuration authority.** Technical parameters are changed only by R33 and R02. **Business
thresholds are not configurable here at all** — they belong to M64 under stewardship
(BRU-ADM-23). This is the practical expression of the M30/M64 boundary and it prevents an
administrator from changing a discount ceiling.

**Field-level restrictions.** Vault references, infrastructure endpoints and credential
metadata are visible only to R02 and R33. Capacity cost figures are visible to R02, R03 and R01.

**Segregation of duties.**
- The proposer of a configuration change cannot be its sole approver where the parameter requires approval.
- The person who applies an emergency change cannot be the person who files and approves its retrospective record.
- A branch manager cannot provision, suspend or close their own branch.
- Backup verification results cannot be marked passed by the person who performed the restore test alone.
- Archival execution and retention-policy definition are separate (M30 executes, M24 defines).

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Platform health console** | CTO, IT Administrator, on-call | Real time | Application and database health, job status, queue depth, **integration health (M28)**, security signals (M29), capacity, active incidents |
| **Scheduled job board** | IT Administrator, module owners | Real time | Every job: last run, state, duration against expected, failures, **missed runs**, next due |
| Branch register and readiness | Operations Director, CEO | Real time | Every branch: status, capabilities, hours, zone, provisioning completeness |
| **Branch provisioning performance** | Operations Director, CTO | Per opening | Time from request to active — **against the < 1 day target** |
| Configuration change log | CTO, Internal Audit, M66 | Weekly | Every change with actor, approver, change record, environment path; emergency changes highlighted |
| **Configuration change without code release** | CTO | Monthly | Share of changes achieved by configuration rather than deployment — **target > 95%** (with M64) |
| Feature flag register | CTO, module owners | Monthly | Live flags, targeting, stale flags past removal date, kill-switch events |
| Environment status | CTO, all teams | Weekly | Refresh dates, masking verification, configuration divergence between environments |
| **Backup and continuity assurance** | CTO, CFO, Quality Manager | Weekly / per drill | Backup success, **restore test results**, RPO/RTO achieved in drills, issues and actions |
| Capacity and growth | CTO, CFO | Monthly | Utilisation, growth rate, projected exhaustion, scaling recommendations, infrastructure cost |
| Alert quality | CTO, IT Administrator | Monthly | Alerts fired, actioned, ignored; alerts without runbooks; noisy alerts proposed for removal |
| Runbook currency | CTO, Quality Manager | Quarterly | Modules and alerts with runbooks; overdue reviews |
| Maintenance and availability | CTO, Operations Director | Monthly | Planned windows used against the 4-hour cap; unplanned downtime; availability against NFR-006 and NFR-045 |
| Archival and storage | CTO, CFO | Quarterly | Data archived by policy, storage tier distribution, retrieval requests, cost |
| Licence compliance | CTO, Legal | Annually | Component licences, obligations, compliance status, review dates |
| Announcement reach | CTO, HR Director | Monthly | Announcements published, targeting, acknowledgement rates |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **Time to stand up a new branch** | weeks | < 2 days | **< 1 day** |
| — | **Configuration changes made without a code release** *(shared with M64)* | unmeasured | 85% | **> 95%** |
| — | Time to stand up a new legal entity *(shared with M65)* | not possible | — | **< 10 days** |
| — | Scheduled job failures detected within 5 minutes | unknown | 98% | **100%** |
| — | **Missed job runs undetected** | unknown | **Zero** | **Zero** |
| — | Alerts with a current runbook link | 0% | **100%** | **100%** |
| — | Modules released without a runbook | unknown | **Zero** | **Zero** |
| — | Direct production configuration edits | unmeasured | **Zero** | **Zero** |
| — | Emergency changes regularised within 24 hours | n/a | 95% | **100%** |
| — | Kill-switch propagation time | n/a | < 90 s | **< 60 s** |
| — | **Backup restore tests passed** | unmeasured | **100%** | **100%** |
| — | DR drills completed on schedule with RPO ≤ 15 min and RTO ≤ 2 h | never | **2 per year** | **2 per year** |
| — | System uptime, business hours (09:00–22:00 BST) | unmeasured | 99.8% | **≥ 99.9%** (NFR-006) |
| — | Planned maintenance within the 4 h/month cap and announced 72 h ahead | unmeasured | 100% | **100%** |
| — | Models missing entity or operating-unit dimensions | unknown | **Zero** | **Zero** |
| — | Feature flags past their planned removal date | n/a | < 10% | **< 5%** |
| — | Capacity reviews completed monthly | 0% | **100%** | **100%** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §9 names **time to stand up a new branch (< 1 day)**
> and **configuration changes without a code release (> 95%)** as the category KPIs owned by M30
> / M30–M64. **Neither has a canonical `KPI-0nn` identifier** — `06-02` §2.6 ends at KPI-049
> with no platform section. Allocation for all seventeen metrics is an audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `base` — company, configuration parameters, cron substrate | 18% |
| L2 | **OCA `operating-unit`** (multi-branch isolation), OCA `server-tools` (technical utilities, configuration helpers) | 20% |
| L4 | **Prometheus, Loki, Tempo, Grafana**, K3s, MinIO, Vault operational surfaces | 18% |
| L5 | `cd_entity_config`, `cd_feature_flag`, `cd_platform_ops`, `cd_job_registry` | 44% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 1 of 4 identifiers below are claimed by another module: **CD-159** also claimed by M19, M45. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-133 | `cd_entity_config` — entity, branch, zone, cost centre, business line, working calendar, **single-action branch provisioning**, effective-dated organisational history, dimensional enforcement | Odoo module | 7 PW |
| CD-135 | `cd_feature_flag` — flag registry, targeting, evaluation service, **kill switch**, telemetry correlation, stale-flag management, change freeze | Odoo module + service | 3 PW |
| CD-138 | `cd_platform_ops` — configuration registry, versioning, promotion and rollback, emergency path, **health console**, alert and runbook registry, capacity, archival, backup verification, DR drills, maintenance windows, announcements, licence register | Odoo module + frontend | 7 PW |
| **CD-159** | `cd_job_registry` — scheduled job registry, execution monitoring with failure, overrun and **missed-run detection**, overlap prevention, queue and worker health | Odoo module | 2 PW |

> CD-133, CD-135 and CD-138 retain their `02-05` §5.2 allocation. **CD-134 `cd_mdm` moves to
> M64**; **CD-136 `cd_locale_pack` and CD-137 `cd_country_pack` move to M65** under the v2.1
> re-scope. CD-159 is claimed from the extension block for modules M31–M67. **All CD IDs remain
> provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M28 Integration** | Event outbox for structure and configuration events; health telemetry into the console. Also W1 |
| **M29 Identity** | Administrator authorisation; masking verification gating environment refresh. Also W1 |
| Infrastructure: Prometheus, Grafana, Loki, K3s, MinIO, Vault | Provisioned before the console can display anything |
| **M64 MDM (W2)** | Business master data governance. **M30 ships in W1 holding both technical and business parameters; business parameters and their stewardship transfer to M64 in W2.** The transfer must be planned, not discovered |
| **M65 Localisation (W9)** | Country and locale packs. **Until W9, Bangladesh holiday sets, currency and locale are configured directly in M30 and migrate to M65 at W9.** The `fix.entity` country attributes are stubbed from W1 |
| M24 Documents (W3) | Retention class and legal hold before archival executes; archival is not enabled before W3 |
| M66 ITSM (W6) | The ITIL change process that configuration change records reference. **Until W6, the change record is held in M30 itself** |
| M67 PPM (W7) | Branch-opening projects; branch provisioning works standalone before then |

> **Three deferred hand-offs.** M30 ships in W1 holding capabilities that later transfer to M64
> (W2), M66 (W6) and M65 (W9). Each is a planned migration of ownership, not a re-build, and
> each is listed above. **Failing to plan them is how a platform-admin module becomes a
> permanent dumping ground** — the exact outcome the v2.1 re-scope exists to prevent.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Branch list | 51+ branches | `fix.branch` | W1, surveyed and authored |
| Legal entity details | 1 entity | `fix.entity` | W1 |
| Cost centre structure | Held in finance spreadsheets | `fix.cost.center` | W1, authored with Finance |
| Zone definitions | Informal, in dispatch practice | `fix.zone` | W1, **authored** — no formal zones exist today |
| Working calendars and holidays | Manual | `fix.working.calendar` | W1, authored; holiday sets move to M65 at W9 |
| Existing scheduled jobs | Legacy cron, undocumented | `fix.scheduled.job` | W1, surveyed and registered |
| Configuration | Held in code and configuration files | `fix.config.parameter` | W1, **extracted and registered** |
| Runbooks | None exist | `fix.runbook` | W1 onward, **authored per module as each is built** |

> **Position.** M30 migrates almost nothing and authors almost everything. Two tasks are larger
> than they appear: **surveying every scheduled job in the legacy estate** (an unregistered job
> that stops running is invisible), and **extracting hard-coded configuration** into the
> registry, which is the precondition for the > 95% no-code-change KPI.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A new branch is provisioned end to end in under one day, with every dependent object created | Three real branch openings measured |
| AC-02 | Branch provisioning is atomic; an induced failure at any step rolls back completely | Fault-injection test at each provisioning step |
| AC-03 | No model reaches production without `company_id` and `operating_unit_id` | CI model-registry check plus a full-schema assertion |
| AC-04 | A direct write to a versioned production configuration parameter is rejected | Negative test on the API and the UI |
| AC-05 | An emergency change notifies multiple parties within one minute and auto-reverts if unregularised within 24 hours | Scripted scenario with a deliberate non-filing |
| AC-06 | Any configuration change can be rolled back in one action with a complete audit trail | Rollback test |
| AC-07 | A kill switch disables a capability estate-wide within 60 seconds without a deployment | Timed test across all application nodes and portals |
| AC-08 | Feature flag evaluation returns the safe default when the evaluation service is unavailable, and never fails the request | Induced-outage test |
| AC-09 | Every scheduled job is registered; an unregistered job cannot run in production | Negative test plus a full job-inventory reconciliation |
| AC-10 | A job failure alerts within 5 minutes with a working runbook link | Fault-injection across a sample of jobs |
| AC-11 | **A job that does not start when due is detected and alerted as a missed run** | Scheduler-suppression test |
| AC-12 | A job cannot overlap its own previous run unless declared concurrent-safe | Concurrency test |
| AC-13 | Every registered alert has a runbook link, and a broken link is detected weekly | Registry assertion plus link-check results |
| AC-14 | No module is released without an operational runbook | Release-gate evidence across all modules built to date |
| AC-15 | A non-production environment cannot be released until M29 confirms masking verification | Negative test |
| AC-16 | Weekly automated restore tests execute and pass | Twelve weeks of verification records |
| AC-17 | DR drills are executed twice yearly and achieve RPO ≤ 15 minutes and RTO ≤ 2 hours | Two drill reports with measured results |
| AC-18 | Planned maintenance occurs outside 08:00–23:00 BST, within 4 hours per month, announced 72 hours ahead | Twelve months of window records |
| AC-19 | Archived data is retrievable within the stated SLA and referential integrity is preserved | Retrieval test on archived records with dependencies |
| AC-20 | Effective-dated organisational history produces correct reporting for a past period after a structure change | Scripted scenario spanning a branch reorganisation |
| AC-21 | Business thresholds cannot be changed in M30; the attempt directs the user to M64 | Negative test (from W2) |
| AC-22 | Configuration resolution adds ≤ 2 ms and flag evaluation ≤ 1 ms at p95 | Performance test on a hot path |
| AC-23 | Announcements render correctly in Bengali and English and target by role, branch and entity | Translation and targeting test (AS-12) |
| AC-24 | CTO and Operations Director sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 24 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **What is the definitive branch list, and what capability profile does each branch have?** "51+" is not a specification, and provisioning cannot be designed against an approximate number. | Operations Director | W1 minus 2 months |
| Q-02 | **Do formal dispatch zones exist today, or must they be authored?** The migration table assumes authored. If they exist informally in dispatchers' heads, extracting them is a discovery exercise on the W1 critical path. | Operations Director / Dispatch Manager | W1 minus 1 month |
| Q-03 | What is the cost centre structure, and does it match how Finance actually reports today? | CFO / Finance Manager | W1 build |
| Q-04 | **Which configuration parameters are technical (M30) and which are business (M64)?** The boundary is clear in principle and will be contested in practice for perhaps 50–100 parameters. A classification pass is needed before the W2 hand-off. | CTO / business owners | **W2 minus 1 month** |
| Q-05 | Is there an on-call rotation, and who is on it? A health console with no one watching it is a dashboard, not a control. | CTO / IT Administrator | W1 build |
| Q-06 | What is the branch-manager configuration boundary — which settings may a branch manager change for their own branch without approval? | Operations Director / CTO | W1 build |
| Q-07 | Where is the DR environment hosted, and does the split-residency architecture (NFR-086) require a second resident DR store? This interacts directly with M29 Q-05. | CTO / CFO | W1 build |
| Q-08 | Is the 4-hour monthly maintenance cap realistic for a 67-module estate under active development, and what happens when a wave cutover needs longer? | CTO / Operations Director | W2 |
| Q-09 | Who owns the licence register review, and what is the escalation when a component's licence terms change (for example Redpanda's BSL conversion)? | CTO / Legal | W3 |
| Q-10 | **When exactly does business-parameter ownership transfer to M64**, and who runs the migration? Deferring this decision is how M30 becomes a permanent dumping ground. | CTO | **W2 planning** |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2, §5 (**the M30/M64 boundary**), §6 (boundary map), §7 promise 5,
§9 (category KPIs), §11 (multi-country retrofit risk) ·
`M28_Integration_API_and_Event_Platform.md` (integration health, event outbox, batch jobs) ·
`M29_Identity_Access_and_Information_Security.md` (authorisation, masking verification) ·
`M64_Master_Data_Management_and_Configuration.md` (**business master data and parameters**) ·
`M65_Multi_Entity_Multi_Country_and_Localisation.md` (**country packs, locale, currency, holidays**) ·
`M66_Internal_IT_Service_Management.md` (incident, problem and change processes) ·
`M67_Project_Program_and_Portfolio_Management.md` (branch-opening projects) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §8 (**the dimensional model**),
§9 (business lines), §10 (AS-03) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §4 (L4 systems), §5.2 (CD-133…138),
§8 (infrastructure sizing and cost), §9 (environments, secrets, promotion) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md`
NFR-006, NFR-007, NFR-008, NFR-009, NFR-027, NFR-028, NFR-030, NFR-049, NFR-051, NFR-052,
NFR-058, NFR-059, NFR-071, NFR-091; **OPS-01…OPS-08**; DI-08; AS-03, AS-12 ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` §11 (BRU-ADM-01, BRU-ADM-02) ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §M30 (17 entities, 5 reallocated) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §3.5

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Service Infrastructure (1000FiX Station expansion),
§Multiple Service Centers · `ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md`
(multi-location and configuration requirements)

**External benchmark**
SAP enterprise structure — company code, plant, profit centre as the dimensional skeleton ·
Oracle Fusion enterprise structures and Dynamics 365 legal entities / operating units ·
OCA `operating-unit` — multi-branch isolation on Odoo ·
[Feature flags unified with observability — Datadog](https://www.datadoghq.com/about/latest-news/press-releases/datadog-launches-feature-flags/) ·
[OpenFeature observability specification — flag evaluation telemetry](https://openfeature.dev/specification/appendix-d/) ·
[Platform engineering and internal developer platform practice — 2025 stack survey](https://newsletter.pragmaticengineer.com/p/the-pragmatic-engineer-2025-survey-part-3) ·
[Building a cost-effective observability platform with OpenTelemetry — CNCF](https://www.cncf.io/blog/2025/12/16/how-to-build-a-cost-effective-observability-platform-with-opentelemetry/) ·
[Observability platform selection criteria 2026](https://www.augmentcode.com/tools/best-observability-platforms) ·
Google SRE practice — capacity review, blameless operations, runbook discipline

---

*Module M30 · Category K · 1000FiX ERP System v2.0 · CONFIDENTIAL*
