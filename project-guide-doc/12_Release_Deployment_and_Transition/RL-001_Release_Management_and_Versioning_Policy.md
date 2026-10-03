---
id: RL-001
title: Release Management and Versioning Policy
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Release Manager
approver: Chief Technology Officer, endorsed by the ERP Steering Committee
standards_basis: >
  ITIL 4 — Release Management (service management practice) and Deployment Management (technical
  management practice), adopted as two practices and not one · ISO/IEC 20000-1:2018 + Amd 1:2024
  §8.5.1 change control and §8.5.3 release and deployment · Semantic Versioning 2.0.0 and the OCA
  addon scheme, both adopted by citation from BE-003 §8 · ISO 9001:2015 §8.6 release of products
  and services · DORA / Google Cloud State of DevOps four key metrics, with the 2025 additions of
  rework rate and reliability
traces_to: >
  PGD-000 RL-001 row (◐ OP-006) · OP-006 §4.1 release types, §4.7 wave note set, DT-01 ·
  SP-031 §3 change classes, §5.3, §5.4, §7 · SP-004 A-90, A-91 · BE-003 §8, §9, GW-31…GW-41 ·
  06-01 §5 delivery method · RFP §12.6 · M66 §4 (CAB rejection) · M30 (W1 change records)
depends_on: >
  BE-003 (issued) · SP-031 (content, issued) · OP-006 (content, issued) · GV-003 (issued) ·
  GV-009 (issued) · QA-010 (issued) · PE-002, PE-004, PE-008, PE-009 (ISSUED 2026-08-19,
  concurrently with this document) · SV-001, SV-002, SV-003 (ISSUED 2026-08-19) ·
  SV-004, SV-005 (ISSUED 2026-08-19, fifth estate movement of this session) ·
  SV-006 Problem & Major Incident Management (ABSENT ◐) ·
  M30 / M66 change-record systems (specified, not built)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-18 23:27 (+06)
rule_prefix: RMP — verified unused across all 777 markdown files of the workspace, re-verified at audit 2026-08-19 02:10 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RL-001 — Release Management and Versioning Policy

### Category 12 · Code `RL` · Rule space `RMP` · ITIL 4 · ISO/IEC 20000-1:2018 + Amd 1:2024 §8.5 · SemVer 2.0.0

---

> **`PGD-000` states the gap this document fills:** *"`OP-006` defines the release-note **standard
> and wave note set**. The release process that produces them is undefined."*
>
> That is exactly right, and it understates the position by one degree. `OP-006` describes eight
> release types. `SP-031` describes three change classes. `BE-003` describes five tag forms.
> **No document maps any of these three sets onto either of the others**, and no document states
> when a release may not happen at all. This policy supplies the mapping and the calendar.

---

## 1. Purpose

This policy states **how software becomes available to the people who use it**: what a release is,
what kinds there are, who may authorise each kind, how often they happen, what version number they
carry, and — the part nothing in the estate currently answers — **the dates on which a release must
not happen**.

It exists because a 1000FiX release is not a deployment to a website. It is a change to the system
of record for 250,000+ customers a month, 500+ employees and 51+ branches, and it touches a
statutory VAT sequence, a payroll run and a set of contractual SLAs. A release that lands on the
wrong day does not inconvenience users; it lands inside a month-end close, or inside a cutover
freeze, or three days before a wave gate whose evidence it has just invalidated.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **release / deployment decoupling** — the organising decision of this category (§3) |
| 2 | The **release taxonomy**: eight release types reconciled to three change classes (§4) |
| 3 | **Release trains and cadence**, per wave and inside a wave (§5) |
| 4 | **Versioning policy** — the business meaning of the schemes `BE-003` §8 defines mechanically (§6) |
| 5 | **Freeze windows** — eight classes, derived rather than asserted (§7) |
| 6 | **Authority** — who approves which release type, and who may waive a freeze (§8) |
| 7 | The **hotfix and emergency path** at the governance layer, and a correction to `BE-003` §9 (§9) |
| 8 | **Release notes** — adopted from `OP-006` by citation, with the two rules `OP-006` cannot set (§10) |
| 9 | **Deprecation and removal** of live capability (§11) |
| 10 | **Measurement** — the DORA set, and an honest statement of what can be measured today (§12) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Moving artefacts into an environment; pre-flight, verification, abort | `RL-002` | ITIL 4 separates deployment from release, and so does this category. §3 states the seam |
| Readiness assessment before a go-live | `RL-003` | A release policy says *how* to release; readiness says *whether* to |
| Which branches receive a release in which order | `RL-004` | Site sequencing is a rollout problem |
| Branch model, commit form, tag mechanics, merge rules | `BE-003` §3–§9 | Adopted here by citation; **never restated** (`MST-01` pattern) |
| Pipeline stages, runners, promotion automation | `PE-004` | Issued 2026-08-19. §12.3 states what its **implementation** status costs |
| Environment classes, sizing, provisioning | `PE-002` | Issued 2026-08-19 — twelve environments |
| Incident and request handling, problem management | `SP-031` §5.1, §5.2, §5.5 | This policy uses only §5.3 and §5.4 |
| Release **note wording**, audience extracts, language | `OP-006` | Adopted whole. §10 adds only the two rules a content standard cannot set |
| Defect thresholds that block a gate | `QA-010` §5 | Consumed, not restated |
| Per-change post-implementation review | `M66` `CD-163` / `SP-031` §8 | Distinct from `RL-005`. §4.5 disambiguates |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Release Manager | The whole document. This is the role's charter |
| Change Manager and the CAB | §4, §8, §9 — what class a release falls in and who approves it |
| Engineering Lead and squads | §5 cadence, §6 versioning, §7 when they may not ship |
| Financial Controller and CFO | §7.3, §7.4, §7.5 — the finance, payroll and statutory freezes and why they bind |
| Data Migration Lead | §7.6 — the cutover freeze, and how `CUT-01` is satisfied by a date rather than a hope |
| Support Lead | §7.7 — why no feature ships into a wave during that wave's hypercare |
| PMO | §7.8 — the gate evidence freeze; §12 for the gate report's release metrics |
| Steering Committee | §8.3 — the two decisions reserved to it |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / practice | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ITIL 4 — Release Management** | Service management practice: make new and changed services and features available for use | §3 adopts the practice boundary as the category's organising principle; §4 and §5 are its taxonomy and cadence | **None.** The ITIL 4 restructure that split release from deployment is adopted deliberately, not inherited |
| **ITIL 4 — Deployment Management** | Technical management practice: move new or changed components to live environments | Named and delegated to `RL-002` in full | The split is the point of §3 |
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | **§8.5.1** change control · **§8.5.3** release and deployment management | §4 classifies changes; §8 records authority; §9 provides the documented emergency route; §10 records what is released and when | Amd 1:2024 (published February 2024) adds climate-action wording to clauses 4.1/4.2 and **changes nothing in §8.5**. Cited for currency, per `PG-M4` |
| **ISO 9001:2015** | §8.6 release of products and services | §8.4 requires traceability from every production release to the authorising person, matching `BE-003` `GW-34`'s signed tags | None |
| **Semantic Versioning 2.0.0** | `MAJOR.MINOR.PATCH` | Adopted **by citation** from `BE-003` §8.1. §6.2 supplies the business meaning of a MAJOR bump, which SemVer does not | SemVer defines the mechanics of a public API's version. It says nothing about *user-visible* change, which is what a release policy must govern. §6.2 bridges the two |
| **OCA addon versioning** | `{odoo_series}.{major}.{minor}.{patch}` | Adopted by citation from `BE-003` `GW-31` | Odoo's own update mechanism reads the manifest version; the scheme is not negotiable |
| **DORA four key metrics** | Deployment frequency · lead time for changes · change failure rate · failed-deployment recovery time | §12.1 adopts all four, plus the 2025 report's **rework rate** | **Departure:** none of the four can be measured until `PE-004` and `PE-008` exist. §12.3 states the position rather than publishing an unmeasurable target |

> **A note on ITIL editions.** ITIL 4 is the current framework. Training vendors have advertised an
> *"ITIL Foundation V5"* for 2026; **that claim is not verified from an AXELOS/PeopleCert primary
> source and is not relied on here.** It is registered as an `RR-005` currency item so that a
> future edition change is a decision rather than a surprise. Verified 2026-08-19.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `OP-006` §4.1 | `../../project_content/17_Operations_Support_and_Runbooks/` | **Eight release types** with notice periods and named approvers |
| `OP-006` §4.7 | ″ | The nine-wave note set `REL-W1`…`REL-W9`, published **10 working days** before cutover |
| `OP-006` `DT-01` | ″ | Nothing user-visible ships **Thursday after 15:00 BST or Friday** — a Bangladesh-specific correction of the inherited convention |
| `SP-031` §3, §5.3, §5.4, §7 | `../../project_content/06_Process_SOP_and_Workflow/06B_…/` | **Three change classes** — standard, normal, emergency — with CAB approval and a 2-business-day retrospective review |
| `SP-004` `A-90`, `A-91` | ″ `06A_Process_Architecture/` | Production configuration change requires a traceable change record and CAB; emergency change is CTO-approved |
| `BE-003` §8, §9 | `../07_Build_Engineering_and_Development_Standards/` | Three version schemes, five tag forms, `GW-31`…`GW-41`, the hotfix step sequence |
| `06-01` §5 · RFP §12.6 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/` · `../../primary-doc/` | Cadence: fortnightly to staging, monthly to production within a wave; hypercare after every wave |
| `M66` §4, `CD-163`, `AC-12` | `../../1000fix_ERP_Module/03_Modules/…M66_*.md` | The ITSM module: three change types, risk-routed approval, change calendar with collision detection, back-out, per-change post-implementation review — **and an explicit rejection of a CAB meeting cadence** |
| `M30` | ″ `…M30_Platform_Administration_and_Configuration.md` | **W1** capability: change freezes, configuration change records, working calendars |
| `OP-002` §4.3, §4.8 | `../../project_content/17_…/OP-002_*.md` | Hypercare duration per wave (4–8 weeks) and the eighteen `HX` exit criteria |
| `DM-014` §4.1, `CV-06` | `../../project_content/12_Data_Migration_Content/` | Five cutover phases; the freeze instant as an exact `Asia/Dhaka` instant |
| `MG-006` `CUT-01` | `../09_Data_Migration_and_Cutover/` | **The application must be deployed, smoke-tested and stable *before* the freeze instant** |
| `MG-005` | ″ | Rehearsal must be run against the code that will be live |
| `GV-009` `GA-03`, `GA-10` | `../00_Programme_Governance_and_Control/` | Gate evidence is dated within T−6 weeks to T−0; the gate report circulates 3 working days ahead |
| `MD-041` | `../../project_content/02_Master_Data_and_Configuration/` | The public holiday gazette, reloaded annually |

### 2.3 Audit findings and register gaps this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `RL-001` row ◐ | `PGD-000` | *"The release process that produces them is undefined."* §4, §5, §7 and §8 define it |
| `SP-031` Definition-of-Done open item | `SP-031` §DoD | *"CAB membership, cadence and quorum defined — **outstanding**."* §8.2 defines all three, and §4.6 rules on the contradiction that made it hard to define |
| `BE-003` §9 step 6 mis-citation | This document, §9.4 | `BE-003` routes emergency deployment to *"`RL-003` emergency change"*. `RL-003` is the go-live readiness assessment. The emergency change route is **`RL-001` §9** |
| `M66` §4 vs `SP-031` §3 contradiction | This document, §4.6 | Two current documents disagree on whether a CAB meets. Ruled, with the reasoning recorded |
| `MG-006` `Q-01` | `MG-006` §2.3 | *"`RL-002` is unwritten; this rule is the interface it must honour."* `RMP-25`/`RMP-26` supply the dates `CUT-01` lacked |
| No freeze calendar exists anywhere | This document, §7 | Eight freeze classes derived from the business cycles that impose them |

### 2.4 The rule space

Rules in this document carry the prefix **`RMP`**. The category code `RL` is **not** used as a rule
prefix.

> **Why not `RL`.** `RL-01` … `RL-12` is already the rule space of
> `TR-024_Release_Training_and_Refresher_Standard.md`, which uses it **36 times** for
> release-training rules. Using `RL-nn` here would have produced a silent collision across two
> files describing the same event from different sides — the defect class behind `H-03` (48
> colliding `CD` identifiers), `H2-04` (22 colliding `KPI` identifiers) and `PGD-A1-01`. `RMP` was
> tested against every `[A-Z]{2,6}-[0-9]{1,3}` token in all **754** markdown files of the workspace
> and returned **zero** matches before allocation.

---

## 3. Release and Deployment Are Two Practices

### 3.1 The decision

> **`RMP-01`. A release and a deployment are different events with different owners, different
> authority and different failure modes. This category treats them separately throughout.**

| | **Release** (`RL-001`) | **Deployment** (`RL-002`) |
|---|---|---|
| ITIL 4 classification | **Service management** practice | **Technical management** practice |
| Question answered | *What becomes available to users, and when?* | *How do the artefacts get into the environment?* |
| Unit | A named, versioned set of user-visible change | A promotion of a build to an environment |
| Owner | Release Manager | Platform Lead |
| Fails as | Users receive a change they were not prepared for | The environment ends in an inconsistent state |
| Reversal | Feature toggle, or a subsequent release | Pipeline rollback (`PE-004` §8.4 `RB-01`) |
| Approval | §8 of this document | `RL-002` §6 pre-flight and §9 abort |
| Evidence | Release note (`OP-006`), signed tag (`GW-34`) | Deployment record, smoke-test result |

### 3.2 Why this matters here rather than being theory

Three concrete consequences follow, and each is a rule.

> **`RMP-02` — a deployment may occur without a release.** Code may be promoted to production with
> its user-visible behaviour disabled. This is the only mechanism by which `MG-006` `CUT-01` can be
> satisfied: *"the application must be deployed, smoke-tested and stable **before** the freeze
> instant."* If deployment and release were the same event, `CUT-01` would require the business to
> receive new behaviour during a cutover freeze — which §7.6 forbids.

> **`RMP-03` — a release may occur without a deployment.** Enabling a toggle for a branch, a role
> or a customer segment is a **release** and requires a release note under `OP-006` §4.1, even
> though nothing was deployed. `RL-004` uses this route to bring branches live in tranches without
> one deployment per tranche.

> **`RMP-04` — the toggle register is a release artefact, not a developer convenience.** Every
> toggle gating user-visible behaviour is registered with its owner, its default, its intended
> removal release and its removal date. A toggle with no removal date becomes permanent
> configuration and is a defect. **This obligation is stated here and has no owning design
> document**: `PE-009` (Configuration & Secrets Management) is ◐ and `BE-003` does not cover
> toggles. Raised as `Q-01`.

---

## 4. The Release Taxonomy

### 4.1 The problem

Three registers of "kinds of change" exist and none references another.

| Register | Location | Members | Purpose |
|---|---|---:|---|
| Release types | `OP-006` §4.1 | **8** | Determines whether a note is required, its notice period and its approver |
| Change classes | `SP-031` §3, §5.3–§5.4 | **3** | Determines the approval route and whether CAB assessment applies |
| Tag forms | `BE-003` §8.2 | **5** | Determines what a git tag means |

Counted from the source tables at **2026-08-18 23:27 (+06)**.

A release manager holding all three has no way to answer *"this is a sprint release — does it need
CAB?"*, and the answer is not obvious: `OP-006` names the approver as *"Release manager + Content
Design"*, while `SP-004` `A-90` requires that **any** production configuration change be
CAB-approved.

### 4.2 The mapping

> **`RMP-05`. Every release carries exactly one release type, exactly one change class and, where
> it reaches production, exactly one tag form. The three are assigned together at release planning,
> never separately.**

| # | `OP-006` release type | `SP-031` change class | `BE-003` tag form | Notice | Approver (this policy) |
|:--:|---|---|---|---|---|
| 1 | **Configuration change** | **Standard** — from the pre-approved catalogue | *(none)* | Same day, only if user-visible | Domain owner |
| 2 | **Weekly release** | **Normal**, low risk | `v<n>.<m>.<p>` | Release day | Release Manager |
| 3 | **Sprint release** | **Normal** | `v<n>.<m>.<p>` | **3 working days** ahead for `Action required` items | Release Manager + Content Design |
| 4 | **Wave release** | **Normal**, high risk | `v<n>.0.0-w<n>` | **10 working days** | Programme Manager, after the `GV-009` gate |
| 5 | **Hotfix** | **Emergency** | `hotfix-<INC-ID>` | At deployment | Change Manager (§8.2) |
| 6 | **Emergency change** | **Emergency** | `hotfix-<INC-ID>` or none | Within 1 working day, retrospective | Incident Commander; retrospective CAB in **2 working days** (`SP-004` `A-91`) |
| 7 | **Mobile app release** | **Normal** | `v<n>.<m>.<p>` | Per staged-rollout schedule | Mobile Lead |
| 8 | **Removal / deprecation** | **Normal**, high risk | `v<n>.<m>.<p>` | **30 calendar days** | Programme Manager |
| — | *Release candidate to `staging`* | **Standard** | `v<n>.0.0-rc<k>` | None — not user-visible | Release Manager |

**Three things this mapping settles that were previously ambiguous:**

> **`RMP-06` — types 5 and 6 are both `Emergency` but are not the same thing.** A **hotfix** repairs
> a defect in delivered function and follows `BE-003` §9's eight steps. An **emergency change**
> restores or protects service and may involve no code at all — a rate limit, a disabled
> integration, a rolled credential. Both take the `SP-004` `A-91` authority; only the hotfix takes
> `BE-003` `GW-40`'s mandatory regression test. `OP-006` distinguishes them and `SP-031` does not;
> this table preserves the distinction because the compensating controls differ.

> **`RMP-07` — a "configuration change" is only a Standard change while it is in the catalogue.**
> `SP-031` step 23: *"deviation makes it a normal change."* The catalogue is owned by the CAB (§8.2)
> and reviewed quarterly. **A configuration change to a statutory sequence, a tax rate, an approval
> limit or a retention class is never Standard**, whatever the catalogue says — it is `RC-A` scope
> under `QA-001` §5.4 and takes the Normal route.

> **`RMP-08` — a wave release is approved by the Programme Manager *after* the wave gate, not
> before.** `GV-009` §6.3 makes the Steering Committee's gate decision the authority to release the
> **next** wave's scope. The wave release itself is authorised once the gate has passed, and §7.8's
> freeze exists so that the release cannot invalidate the evidence the gate was decided on.

### 4.3 Risk routing, and what it replaces

`M66` §4 adopts *"approval routed by risk"* and explicitly rejects a standing CAB meeting. `SP-031`
§5.3 step 16 requires CAB assessment of every normal change. Both are current, approved documents.

> **`RMP-09` — risk class determines the approval route; the CAB is the body that approves the
> highest class and owns the routing rules.** Risk class is assigned at release planning from three
> factors, and the **highest** factor wins.

| Factor | Low | Medium | **High** |
|---|---|---|---|
| **Blast radius** | One role, one branch, or a toggle at ≤ 5% | One function, or one portal | Cross-module, all sites, or an external population |
| **Reversibility** | Toggle-reversible in < 5 minutes | Reversible by redeploying the prior tag | **Irreversible, or reversible only by data repair** |
| **Regulated surface** | None | Personal data, but no statutory output | **Statutory output, `RC-A` population, or a residency-classified field** |

| Risk class | Approval route | CAB involvement |
|---|---|---|
| **Low** | Release Manager, asynchronously | Recorded; sampled quarterly |
| **Medium** | Release Manager **and** the affected domain owner | Recorded; reviewed at the weekly CAB asynchronous round |
| **High** | **CAB**, quorate (§8.2), before implementation | Assessed and approved individually. `SP-004` `A-90` applies unchanged |

> **This is not a departure from `SP-031`; it is `SP-031` §5.3 made operable at the change volume
> `M66` §4 anticipates.** `SP-031` step 16's requirement — *"the change owner does not approve their
> own change"* — holds at every class without exception (`RMP-16`).

### 4.4 The system of record for a change

| Wave | Where change records live | What is available | What is not |
|:--:|---|---|---|
| **W1 – W5** | `M30` Platform Administration | Configuration change records · **change freezes** · working calendars | **No risk routing, no change calendar with collision detection, no back-out record, no per-change review** |
| **W6 +** | `M66` `CD-163` | All of the above, plus risk-routed approval, calendar with collision detection, back-out and per-change post-implementation review | — |

> **`RMP-10` — five of the nine wave releases happen before the change-management system designed
> to govern them exists.** `M66` is a Wave 6 module (Months 23–26); `W1`…`W5` complete at Month 22.
> Until `M66` is live, §4.3's risk class, §7's freeze calendar and §8's approvals are maintained in
> the `M30` configuration change record with a **manually maintained release calendar** owned by the
> Release Manager. This is a stated interim control, not an oversight, and it is the single largest
> operational weakness of this policy. Raised as `Q-02`.

### 4.5 Three artefacts called "PIR"

Recorded here because §4.2 row 6 and `M66` `AC-12` both use the abbreviation, and they mean
different things.

| Abbreviation used in | Means | Trigger | Owner |
|---|---|---|---|
| `M66` `AC-12`, `SP-031` §8 | Post-**implementation** review **of a change** | Every emergency, failed or major change | Change Manager |
| `OP-016`, `OP-002` `HX-17` | Post-**incident** review | Every `Sev1`/`Sev2` incident | Incident Commander |
| **`RL-005`** | Post-**implementation** review **of a wave** | Every wave, after hypercare exit | PMO |

> **`RMP-11` — in this category the unqualified term "PIR" means `RL-005`'s wave review.** A change
> review is written **"change review"**; an incident review is written **"post-incident review"**.
> `RL-005` §3.2 carries the same rule from the other side.

### 4.6 The CAB contradiction, ruled

| Document | Position | Status |
|---|---|---|
| `SP-031` §3, §5.3, §7 | A Change Advisory Board assesses and approves normal changes; a non-quorate CAB does not approve | Current, approved |
| `SP-031` DoD | *"CAB membership, cadence and quorum defined — **outstanding**"* | Open |
| `M66` §4 | *"A formal Change Advisory Board meeting cadence"* is listed under **what is not adopted**: *"approval is routed by risk, and a weekly meeting would delay more than it protects at our change volume"* | Current, approved |

> **Ruling — `RL-001-D-01`.** Both are right about different things, and the word doing the damage
> is **"meeting"**. `SP-031` requires a *body* with membership, quorum and an approval record;
> `M66` rejects a *standing weekly meeting* as the only route to that body. §8.2 constitutes the CAB
> as a **named body with an asynchronous default and a convened exception**: Low and Medium changes
> are approved on the record without convening; **High-risk changes convene it**, and it must be
> quorate to approve them. This satisfies `SP-031`'s control and `M66`'s throughput objection
> simultaneously, and it discharges `SP-031`'s open Definition-of-Done item.

---

## 5. Release Trains and Cadence

### 5.1 The inherited cadence

`06-01` §5 and RFP §12.6 both state: *"Fortnightly to staging; monthly to production within a wave;
hotfixes as needed."* `BE-003` `GW-37` adds that once `release/w<n>` is cut, no new scope enters it.

### 5.2 The train calendar

> **`RMP-12`. The programme runs three trains. A change boards the earliest train it qualifies for
> and never jumps to a later one to avoid a freeze.**

| Train | Target | Cadence | Contents | Version form |
|---|---|---|---|---|
| **`T-STAGE`** | `staging` | **Fortnightly**, end of each sprint | Everything merged to `develop` | `v<n>.0.0-rc<k>` |
| **`T-PROD`** | `production` | **Monthly**, inside a wave | Fixes and low/medium-risk features from the current wave's scope | `v<n>.<m>.<p>` |
| **`T-WAVE`** | `production` | **Nine times**, at wave go-live | The wave release | `v<n>.0.0-w<n>` |

### 5.3 The release day, derived

`OP-006` `DT-01` forbids user-visible releases on **Thursday after 15:00 BST and on Friday**,
because Bangladesh's weekend is Friday–Saturday and the working week is **Sunday to Thursday**.
`DT-01` states the constraint; it does not state the release day.

> **The derivation.** `DT-01`'s purpose is that *"a problem surfaces while the people who can fix it
> are working."* A release on Thursday morning leaves **half a working day** of observation. A
> release on Wednesday leaves one day. Hypercare triage runs at 09:30 and 17:30 daily (`OP-002`
> §4.5), so one observation *day* is two triage cycles. `OP-002` `HX-04` measures `Sev1` incidents
> over **10 consecutive working days**, and `RL-002` §10 sets a 48-hour post-deployment verification
> window. Two working days of observation is therefore the smallest window in which a
> release-induced `Sev1` can be detected, triaged and either fixed or reverted before the weekend.

| # | Rule |
|---|---|
| **`RMP-13`** | **Routine production releases (`T-PROD`) are deployed Sunday, Monday or Tuesday.** Two full working days of observation remain before the weekend |
| **`RMP-14`** | A **Wednesday** release requires the Release Manager's recorded approval and a named on-call engineer for Thursday |
| **`RMP-15`** | **Thursday after 15:00 BST, Friday and Saturday are closed** to user-visible releases. Only an emergency change (§9) may cross this line, and it takes the `SP-004` `A-91` authority |
| **`RMP-16`** | The person who executes a release is never its sole approver (`SP-031` §11, `SOD-59` pattern). This holds at every risk class, including Low |
| **`RMP-17`** | A `T-WAVE` release is deployed at the time the wave's cutover runsheet (`MG-006` §5) specifies, which may be any hour. `RMP-13` does not apply to it; §7.6 governs it instead |

### 5.4 Wave releases map to waves, not sprints

Adopted unchanged from `BE-003` `GW-37`/`GW-38`. Nine waves, nine major production releases, with
patch releases inside each. Restated here **only** as a pointer, per `MST-01`.

| Wave | Release tag | Go-live month (`06-01` §8) | Wave note (`OP-006` §4.7) | Hypercare (`OP-002` §4.3) |
|:--:|---|:--:|---|:--:|
| W1 | `v1.0.0-w1` | **4** | `REL-W1` | 8 weeks |
| W2 | `v2.0.0-w2` | 8 | `REL-W2` | 6 weeks |
| W3 | `v3.0.0-w3` | 13 | `REL-W3` | 8 weeks |
| W4 | `v4.0.0-w4` | **18** — v1.0 scope complete | `REL-W4` | 6 weeks |
| W5 | `v5.0.0-w5` | 22 | `REL-W5` | 8 weeks |
| W6 | `v6.0.0-w6` | 26 | `REL-W6` | 4 weeks |
| W7 | `v7.0.0-w7` | 30 | `REL-W7` | 6 weeks |
| W8 | `v8.0.0-w8` | 34 | `REL-W8` | 4 weeks |
| W9 | `v9.0.0-w9` | 36 | `REL-W9` | 6 weeks |

---

## 6. Versioning Policy

### 6.1 The mechanical layer is `BE-003`'s

`BE-003` §8.1 defines three coexisting schemes and `GW-31`…`GW-33` govern them. **They are adopted
by citation and are not restated.** This section adds only what a git standard cannot decide.

### 6.2 What a version number promises the business

SemVer defines MAJOR as a backward-incompatible change to a **public API**. That is the right rule
for `libs/py/**`. It is the wrong rule for a branch counter clerk, who does not have an API.

> **`RMP-18`. For any artefact a person uses directly — a portal, an app, an Odoo addon with a user
> interface — the version number's user-facing meaning is defined against the *task*, not the
> interface.**

| Bump | Promise to the business | Consequence |
|---|---|---|
| **MAJOR** | *A task you perform today is performed differently, or is no longer performed here.* Retraining is required | Triggers `TR-024` refresher content, a 30-day notice if anything is removed (§11), and a `CH-002` training update |
| **MINOR** | *Something new is available. Nothing you do today changes* | Release note `New` section; no retraining |
| **PATCH** | *Something that was wrong now works* | Release note `Fixed` section referencing the symptom, not the code |

> **`RMP-19`** — a change that is MINOR under SemVer but requires retraining is released as
> **MAJOR** for the user-facing artefact. The two schemes are permitted to diverge; `GW-33` already
> forbids deriving one from the other.

### 6.3 The programme version

| # | Rule |
|---|---|
| **`RMP-20`** | The programme's overall version is `v<MAJOR>.<MINOR>.<PATCH>` with a `-w<n>` suffix at wave go-live (`BE-003` §8.1 row 3). **`MAJOR` = the wave number.** This is why nine waves produce nine MAJOR versions and why `v1.0.0-w1` is the first production release |
| **`RMP-21`** | The version in the user interface footer, in a support ticket, in a release note and on the git tag are **the same string**. A support ticket that cannot state the version is not diagnosable |
| **`RMP-22`** | An addon's OCA version and the programme version are never reconciled or cross-derived (`GW-33`). The release note carries the **programme** version; the manifest carries the OCA version |

### 6.4 The unresolved manifest question

`BE-003` records that `AR-007` §3.2 describes a **five**-component addon scheme while OCA's has
**four**; `BE-002` `BEA-10` raises it and `GW-31` implements the OCA reading pending `AR-007` v1.1.

> **This policy does not reopen it.** It records the consequence: **until `AR-007` v1.1 issues, the
> version string on an addon is authoritative and the one in `AR-007` §3.2's comment is not.**
> Carried as `Q-03`.

---

## 7. Freeze Windows

### 7.1 Why this section exists

No document in the workspace states when a release may not happen. `M30` provides a *"change
freeze"* capability at W1 and nothing populates it. `OP-006` `DT-01` gives a weekly constraint.
Everything else — month-end, payroll, statutory filing, cutover, hypercare, gate evidence, Eid — is
a freeze that everyone assumes and nobody has written.

> **`RMP-23`. A freeze is a period in which a stated class of release may not be made. It is
> declared in the change calendar, it has an owner, it has an exact start and end instant in
> `Asia/Dhaka`, and it has exactly one waiver authority.**

### 7.2 The eight freeze classes

| # | Freeze | Blocks | Window | Owner | Waiver authority |
|:--:|---|---|---|---|---|
| **`F1`** | **Weekly** | All user-visible releases | Thu 15:00 → Sun 00:00 BST, every week | Release Manager | Emergency route only (§9) |
| **`F2`** | **Finance period close** | Anything touching `M19`, `M20`, `M50`, `M52` | Last **2** working days of the period → close signed, capped **+5** working days | Financial Controller | CFO |
| **`F3`** | **Payroll** | Anything touching `M55`, `M56`, `M21` | Payroll lock → BEFTN file accepted by the bank | HR Director | CFO **and** HR Director jointly |
| **`F4`** | **Statutory filing** | Anything touching a Mushak sequence, an NBR output or a statutory register | Filing preparation start → filed and acknowledged | Financial Controller | **CFO only. Not delegable** |
| **`F5`** | **Cutover** | **All** releases to the affected scope | Wave code freeze (T−25 wd) → parallel-run exit (`DM-014` `C8`) | Data Migration Lead | CTO **with** the Programme Director (`CV-14` pattern) |
| **`F6`** | **Hypercare** | Feature releases into the wave's live scope | Wave go-live → hypercare exit (`OP-002` §4.8) | Support Lead | Programme Manager |
| **`F7`** | **Gate evidence** | All production releases in the gate's scope | T−3 working days → gate decision | PMO | Programme Director |
| **`F8`** | **Business peak** | All user-visible releases | Per the `MD-041` gazette (§7.9) | Operations Director | Operations Director |

### 7.3 `F2` — the finance period close, derived

`06-02` `G3-05` requires *"first full month-end closed within **5 days**."* `DM-014` `CV-05`
establishes that a finance position struck mid-period cannot be agreed with an external auditor.
The exposure is therefore not the close itself but the interval in which the ledger is being
adjusted and the trial balance is not yet struck.

> **Derivation.** The freeze must begin before the last posting day, because a release on the final
> posting day changes behaviour that the close will then measure. Two working days ahead is the
> smallest lead that guarantees at least one full business day of the prior behaviour is observable
> for comparison. It must end when the close is **signed**, not when the calendar says day 5 —
> `G3-05`'s five days is a *target*, and a freeze that expires on a target rather than on an event
> expires while the thing it protects is still happening. Hence **−2 working days → close signed**,
> capped at +5 working days, with any extension escalated to the CFO.

### 7.4 `F3` — payroll, derived

`06-02` `G5-01` requires *"first payroll run processed, validated and paid with **zero errors**"*
and `G5-02` requires the BEFTN file accepted **without rework**. `DM-002` `SRC-014` records the
legacy payroll as a 3-day manual cycle whose YTD balances *"must be exact."*

> **Derivation.** Payroll is the only process in the estate with a stated **zero-tolerance**
> criterion at a gate, and its failure is not recoverable by a subsequent release — an underpaid
> employee is a legal and industrial-relations event, not a defect. The freeze therefore runs to the
> **bank's acceptance of the BEFTN file**, not to the run's completion, because a rejected file
> returns the process to its start. RFP §12.6 requires **two pay cycles** of parallel running, which
> means `F3` binds twice at W5.

### 7.5 `F4` — statutory filing, and why it does not delegate

`DM-014` `T6` makes an unassertable Mushak 6.3 sequence position an **absolute** cutover fallback
trigger: *"uncorrectable statutory exposure."* `SC-008` and the VAT and SD Act 2012 set the filing
obligations; the PDPA 2026 sets the personal-data ones.

> **`RMP-24` — `F4` is the only freeze with a single named waiver authority and no delegate.** A
> statutory exposure cannot be accepted by a role acting for someone else, and the estate's own
> pattern (`CV-14`: *"a go decision taken by whoever is present at 04:00 is how a known-bad load
> reaches production"*) applies with more force here, because the counterparty is the NBR.

### 7.6 `F5` — the cutover freeze, and how `CUT-01` is satisfied

`MG-006` `CUT-01` is the interface this policy must honour:

> *"The application must be deployed, smoke-tested and stable **before** the freeze instant. A
> cutover that deploys code and migrates data in the same window has two failure modes in one clock
> and cannot attribute a defect to either."*

`CUT-01` states the requirement and asks `RL-002` for the mechanism. **It does not state a date**,
and a requirement with no date is satisfied by whatever happens.

> **Derivation of the date.** `DM-014` §4.1 fixes the cutover phases: `P0` rehearsal runs T−21 to
> T−7 **calendar** days; `P1` freeze approach begins T−3 days; the freeze instant ends `P1`.
> `MG-005` requires the rehearsal to be run against **the code that will be live**, or it has
> rehearsed something else. The wave release must therefore be in production **before `P0` begins**,
> not merely before the freeze instant. T−21 calendar days is approximately **T−15 working days**
> against a Sunday–Thursday week; that leaves `RL-002`'s 48-hour post-deployment verification plus
> at least one full business day of observation before rehearsal starts.

| # | Rule |
|---|---|
| **`RMP-25`** | The wave release is deployed to production **no later than T−15 working days** before the freeze instant, where T is the instant defined under `CV-06` |
| **`RMP-26`** | The **code freeze** for that release is **T−25 working days**, giving ten working days of release-candidate testing on `staging` |
| **`RMP-27`** | Between the wave release deployment and the parallel-run exit (`C8`), **only emergency changes** reach the affected scope. `F5` blocks everything else |
| **`RMP-28`** | The wave release is deployed **with its user-visible behaviour disabled** where a toggle exists (`RMP-02`). The *release* — the toggle being enabled — occurs at the go decision (`C7`), not at deployment |

> **`RMP-25` and `RMP-26` are the two dates `CUT-01` was missing, and they are the most consequential
> numbers in this document.** They are derived from `DM-014`'s phase model and `MG-005`'s rehearsal
> requirement, not chosen. They are offered to `MG-006` as the answer to its `Q-01`.

### 7.7 `F6` — hypercare, derived from a measurement

`OP-002` `HX-03` sets a hypercare exit criterion: *"new `S1`/`S2` defect arrival rate ≤ 1 per week
combined, sustained for 2 consecutive weeks."* `HX-06` requires support contact volume to be
*"declining week on week."*

> **Derivation.** Both criteria are **measurements of a decaying population**. A feature release into
> the same scope during hypercare injects a new defect population and a new support-contact
> population into the measurement, and neither criterion can then distinguish *"the wave is
> stabilising"* from *"the wave is stable and the new feature is not."* **The exit criteria do not
> merely become harder to meet — they become uninterpretable.** `F6` therefore blocks feature
> releases into the wave's live scope for the whole hypercare period, which is 4 to 8 weeks
> depending on the wave (`OP-002` §4.3).

| # | Rule |
|---|---|
| **`RMP-29`** | **No feature release enters a wave's live scope during that wave's hypercare.** Fixes, `RC-A` corrections and emergency changes are permitted and are counted in `HX-03` |
| **`RMP-30`** | A wave's `F6` and the **next** wave's development are concurrent by design. `F6` blocks *release*, never *build* — `GW-37` already sends new scope to `develop` |
| **`RMP-31`** | Where `HD-03` applies — a wave rolling out to branches in tranches — the `F6` window runs from the **last** tranche's go-live, matching `OP-002`'s hypercare clock. `RL-004` §7 sizes the tranches; a long tranche schedule lengthens `F6`, and that cost belongs in the rollout plan rather than in a surprise |

### 7.8 `F7` — the gate evidence freeze

`GV-009` `GA-03`: evidence must be *"dated within the gate window — T−6 weeks to T−0"*. `GA-10`: the
gate report circulates a **minimum of 3 working days** before the gate.

> **Derivation.** A production release between the moment the gate report is circulated and the
> moment the Steering Committee decides changes the system the report describes. The committee then
> decides about a system that no longer exists. The freeze is therefore exactly the circulation
> window — **T−3 working days to the decision** — and no shorter, because `GA-10` fixes the
> circulation lead time.

> **`RMP-32`** — a release inside `F7` that is nonetheless made under emergency authority
> **invalidates the affected criterion's evidence** and requires it to be re-taken before the gate,
> per `GA-03`. This is stated so the emergency route cannot be used to slip scope past a gate.

### 7.9 `F8` — business peak, and the data that does not exist

`MD-041` is the public holiday gazette, *"reloaded annually"* and version-pinned. Two Eids, Pohela
Boishakh, Victory Day and Independence Day are the largest fixed points; Eid dates move against the
Gregorian calendar and are gazetted, not computed.

| # | Rule |
|---|---|
| **`RMP-33`** | The `F8` windows for a calendar year are published in the change calendar **before 1 January** of that year, from the gazetted `MD-041` load |
| **`RMP-34`** | `F8` covers the **3 working days before and after** each gazetted public holiday of two days or more, and the whole of any period the Operations Director declares a service peak |
| **`RMP-35`** | **`F8` cannot be enforced before `MD-041` is populated.** `MD-003` records that even the branch count is class `P3` until its dataset is confirmed; the holiday gazette is in the same position. Until then `F8` is maintained by the Operations Director as a manual list. Raised as `Q-04` |

### 7.10 Freeze collision

> **`RMP-36`. Freezes compose. Where two freezes overlap, the release is blocked if **either** blocks
> it, and a waiver requires **both** waiver authorities.** There is no netting and no "senior
> authority overrides".

Worst case, stated so that it is planned for rather than discovered: **Wave 5, Month 22.** `F5`
(cutover), `F3` (payroll, two cycles), `F2` (period close) and `F4` (statutory filing) can all bind
inside the same month, because W5 delivers payroll, deep finance and statutory filing together
(`OP-002` §4.3: *"must contain one full payroll run **and** one statutory filing"*). A waiver at W5
therefore requires the CFO, the HR Director, the CTO and the Programme Director. **This is correct,
and it means W5 has effectively no release window outside its wave release.** It is raised to
`GV-005` as a scheduling risk rather than absorbed silently.

---

## 8. Authority

### 8.1 Who approves what

| Release type | Risk class | Approves | Records in |
|---|---|---|---|
| Configuration change (catalogued) | Low | Domain owner | `M30` change record |
| Configuration change (statutory, `RC-A`, limits) | **High** | **CAB**, quorate | `M30`; `GV-003` if programme-wide |
| Weekly release | Low / Medium | Release Manager + domain owner | `M30` / `M66` |
| Sprint release | Medium | Release Manager + Content Design | `M30` / `M66` |
| **Wave release** | **High** | **Programme Manager**, after the `GV-009` gate passes | `GV-003` `D-nnn` |
| Hotfix | Emergency | Change Manager, notified to the Engineering Lead | Incident record + `M30` / `M66` |
| Emergency change | Emergency | **CTO or delegate** (`SP-004` `A-91`) | Retrospective CAB within **2 working days** |
| Mobile app release | Medium | Mobile Lead | `M30` / `M66` |
| Removal / deprecation | **High** | **Programme Manager**, 30 calendar days' notice | `GV-003` `D-nnn` |

### 8.2 The Change Advisory Board, constituted

Discharging `SP-031`'s open Definition-of-Done item and implementing `RL-001-D-01`.

| Attribute | Provision |
|---|---|
| **Chair** | Change Manager |
| **Standing members** | CTO *(or Platform Lead as delegate)* · Release Manager · Head of Quality Engineering · Security Lead · Service Manager · Data Migration Lead *(until parallel-run exit of the current wave)* |
| **Summoned members** | The affected domain owner, always; the Financial Controller for any `F2`/`F3`/`F4` scope; the DPO for any personal-data scope |
| **Quorum** | **Chair + three standing members, of whom one must be the affected domain owner or their named deputy.** Below quorum the CAB does not approve (`SP-031` §6 row 16) |
| **Default mode** | **Asynchronous.** Low and Medium changes are approved on the record within 2 working days |
| **Convened mode** | **High-risk changes convene the CAB**, within 3 working days of request, or same-day for an `F5`/`F7` conflict |
| **Emergency** | The CTO approves alone (`SP-004` `A-91`); the CAB reviews retrospectively within **2 working days** and may not decline retrospectively — it records, and raises a problem record where the route was misused |
| **Standard-change catalogue** | Owned by the CAB, reviewed **quarterly**, and reviewed unconditionally after any failed standard change |
| **Record** | Every decision, every dissent and every abstention, with the member's name and role |

> **`RMP-37`** — three roles in the standing membership **do not exist in `06-01` §4's team model**:
> Change Manager, Security Lead and Service Manager. `GV-009` §5.3 already records the last two as
> unfilled with a 12–20 week hire lead. **The CAB cannot be quorate as specified until they are
> appointed**, and until then the Chair is the Release Manager and quorum is Chair + two. This is an
> interim, it is dated, and it is raised as `Q-05`.

### 8.3 Reserved to the Steering Committee

| # | Decision | Why it cannot sit lower |
|---|---|---|
| 1 | Accepting a `QA-010` `DMG-T3`/`T4`/`T7`/`T8` threshold breach at a wave release | `QA-010` §5.5 reserves it, and `DMG-T1`/`T2`/`T5` may not be accepted by **any** body |
| 2 | Approving a release that changes the **locked wave scope** | `GV-006` §6.3; the scope baseline is the Steering Committee's |

### 8.4 Traceability of authorisation

> **`RMP-38`** — every production release traces to a named authorising person, per ISO 9001:2015
> §8.6. The trace is the **signed annotated tag** (`BE-003` `GW-34`) plus the change record. An
> unsigned tag does not discharge the obligation, and `GW-36` forbids repairing one by moving it.

---

## 9. The Hotfix and Emergency Path

### 9.1 The seam with `BE-003`

`BE-003` §9 owns the **mechanics** — branch, review count, CI, tag, back-merge, regression test.
They are adopted unchanged and are not restated. This section owns the **authority and the
conditions**, which a git standard cannot set.

### 9.2 When the emergency route may be used

> **`RMP-39`. Emergency is a service condition, not a schedule preference.** Adopted verbatim from
> `SP-031` §6 row 24, because it is the rule most often broken and the wording is already correct.

| Permitted | Not permitted |
|---|---|
| Service is degraded or unavailable | A change missed the train |
| A statutory output cannot be produced | A stakeholder wants it sooner |
| Personal data is exposed or at risk | A freeze is inconvenient |
| A financial control is not operating | The next window is after a holiday |
| A safety-relevant function is failing | The change is small |

### 9.3 What emergency does and does not reduce

Adopted from `BE-003` `GW-39`: *"a hotfix reduces the approval count, never the checks."*

| Reduced | Preserved absolutely |
|---|---|
| Approvals: **one**, from any `CODEOWNERS` holder | The full CI run — **no check is skipped** (`BE-003` §9 step 4) |
| Notice period: at deployment | The regression test (`GW-40`), tracked open until merged |
| CAB: retrospective, 2 working days | The release note, short form (`OP-006` §4.1) |
| — | Segregation of duties: the author is never the sole approver (`RMP-16`) |
| — | `QA-010` `DMG-T1`/`T2`/`T5` — **an emergency release may not introduce an open `S1`** |

### 9.4 Correction to `BE-003` §9

`BE-003` §9 step 6 reads: *"Merge to `main`; tag `hotfix-<INC-ID>`; deploy under **`RL-003`**
emergency change."*

> **`RL-003` is the Go-Live Readiness Assessment & Gate Criteria document.** It has no emergency
> change route and cannot acquire one without becoming a different document. The emergency change
> route is **`RL-001` §9** for authority and **`RL-002` §8** for the deployment itself.
>
> Recorded as finding `RLA-01` in `_AUDIT/PGD-AUDIT-CAT-12`. `BE-003` v1.1 should read *"deploy
> under `RL-001` §9 emergency change, executed per `RL-002` §8."* Until it does, **this document is
> the authority and `BE-003`'s citation is the error** — stated explicitly so that a reader who
> reaches `RL-003` and finds nothing does not conclude the route is undefined.

### 9.5 The 24-hour rule

Adopted from `GW-41`: if a hotfix cannot be made safe within 24 hours it becomes a normal `fix/*`
and the incident is mitigated operationally meanwhile — through `OP-014`'s manual fallback
procedures, which exist for exactly this.

> **`RMP-40`** — a hotfix open longer than 24 hours is reported at the next CAB round regardless of
> its state. The failure mode this prevents is a hotfix branch that lives for a week and accumulates
> scope, which is a release wearing an emergency's approval count.

---

## 10. Release Notes

`OP-006` is adopted **whole**: the eight-section note structure, the `Action required` definition,
audience segmentation, bilingual rules, the templates, the nine-wave note set, distribution channels
and `WN-01`'s three publications. **None of it is restated here.**

Two rules a content standard cannot set:

| # | Rule |
|---|---|
| **`RMP-41`** | **A production release without a published note is an incomplete release, not a released change.** The note's publication is a step in `RL-002`'s go-live checklist, not a follow-up task. `GW-35` already requires notes on every production tag; this makes the omission a *release defect* rather than a documentation gap |
| **`RMP-42`** | The note's `Known issues` section is populated **from `OP-002` §4.6's known-issue log**, and where a wave is in hypercare the two must agree. A known issue appearing in one and not the other is an `RL-005` lesson, not a formatting difference |

---

## 11. Deprecation and Removal

`OP-006` §4.1 sets a **30 calendar day** minimum notice for a removal. This section states what must
happen inside those 30 days.

| Day | Action | Owner |
|:--:|---|---|
| **−30** | Deprecation notice published to every affected audience, in Bengali and English, naming the replacement | Release Manager + Content Design |
| −30 | In-product notice on the capability itself (`UI-005` message library) | Product |
| −21 | Usage measured. **If usage has not fallen, the removal is re-planned, not proceeded with** | Release Manager |
| −14 | Direct contact with any external population still using it — corporate clients, brands, sellers, vendors | Account owners |
| −7 | Final notice; support macros updated (`OP-003`) | Support Lead |
| **0** | Capability removed in a Normal, High-risk release approved by the Programme Manager | Programme Manager |
| +1 | Release note `Removed` section states the announcement date and the replacement (`OP-006` §4.2 row 6) | Release Manager |

| # | Rule |
|---|---|
| **`RMP-43`** | The 30 days start at **publication**, not at the decision |
| **`RMP-44`** | A capability with a **contractual** obligation behind it — an SLA, a corporate agreement, a marketplace seller term — cannot be removed on this route at all. It requires a `CO-003` deliverable change and a contractual notice, whose period is set by the contract and is longer. `CO-003` is ⛔; raised as `Q-06` |
| **`RMP-45`** | Removing a **legacy** capability is not a deprecation — it is a decommissioning and is governed by `RL-006` |

---

## 12. Measurement

### 12.1 The metric set

Reported at every wave gate per `GV-009` §6.2, alongside `QA-010`'s defect position.

| # | Metric | Definition | Why it is here |
|:--:|---|---|---|
| **`RMP-M1`** | **Deployment frequency** | Production deployments per week | Tests `RMP-12`'s trains — a monthly `T-PROD` that never runs means change is accumulating into the wave release |
| **`RMP-M2`** | **Lead time for changes** | Merge to `develop` → available in production | Tests `GW-37`/`GW-38` and the freeze calendar's real cost |
| **`RMP-M3`** | **Change failure rate** | Production releases requiring a hotfix, rollback or emergency change ÷ all production releases | The most direct test of whether §8's authority levels are set correctly |
| **`RMP-M4`** | **Failed-deployment recovery time** | Failure detected → service restored | Tests `RL-002`'s abort criteria and the rollback path |
| **`RMP-M5`** | **Rework rate** | Releases that reverse or repair a release made within the previous 14 days | Added from the 2025 DORA set; it catches the failure `RMP-M3` misses — a release that "succeeded" and was wrong |
| **`RMP-M6`** | **Emergency change proportion** | Emergency changes ÷ all changes | `SP-031` §8: *"the normal path is too slow; fix the process, do not normalise emergencies."* Falling is the target |
| **`RMP-M7`** | **Freeze waivers granted** | Count by freeze class and authority | A freeze waived routinely is not a freeze. Reported per class, never as a total |

### 12.2 Targets

> **`RMP-46`. No target is set for `RMP-M1` … `RMP-M5` at Wave 1.** The first four gates establish a
> **baseline**; targets are set at `G4` from measured performance. Setting a DORA target before the
> pipeline exists would publish a number derived from an industry survey rather than from this
> programme, and `GA-04`'s discipline — *a percentage carries its denominator* — applies to
> throughput metrics as much as to coverage.

| Metric | Target |
|---|---|
| `RMP-M6` emergency proportion | **< 10%** of all changes, from `G2`. This one **is** set now, because `SP-031` already ruled on it and a rising emergency rate is a process failure at any maturity |
| `RMP-M7` freeze waivers | **Zero** for `F4`. All other classes: reported, not targeted |

### 12.3 What can be measured today: none of it

> **⚠ Corrected at audit, 2026-08-19 02:10 (+06) — finding `RLA-16`.** The v1.0 issue of this table
> attributed the blockage to two **documents being absent**. Both were issued on 2026-08-19,
> concurrently with this one. **The blockage is unchanged**, because it was never the document: a
> pipeline design does not emit a deployment event and an observability design does not detect a
> failure. The table below states the real condition, which is implementation.

| Metric | Blocked by | Status |
|---|---|---|
| `RMP-M1`, `RMP-M2`, `RMP-M4` | **`PE-004` implementation** — design issued 2026-08-19, pipeline not built | No pipeline runs; deployment events are not emitted |
| `RMP-M3`, `RMP-M5` | **`PE-008` implementation** — design issued 2026-08-19, dashboards not built | Failure detection is not instrumented |
| `RMP-M6` | `SP-031` §12 records it as **untracked** | No change-record system until `M30` at W1 |
| `RMP-M7` | This document | Measurable from the first published freeze calendar |

> **`RMP-47`.** **`RMP-M7` is the only metric in this set measurable on the day this policy issues**,
> and it is therefore the one the first gate reports. The other six were named so that `PE-004`
> and `PE-008` would be specified *against a known consumer* rather than specified and then asked
> to emit something they were not designed for. **Both were issued the same day as this policy and
> neither cites `RMP-M1`…`RMP-M5` as a consumer** — the naming was too late by hours, and the
> confirmation that their telemetry covers these five metrics is now `Q-08`. This is the same failure `AR-009` found at 45× scale
> in the event estate, and naming the consumer first is the cheap fix.

---

## 13. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| `RMP-01` | Release and deployment are separate practices with separate owners | 3.1 |
| `RMP-02` | A deployment may occur without a release | 3.2 |
| `RMP-03` | A release may occur without a deployment | 3.2 |
| `RMP-04` | Every user-visible toggle is registered with a removal date | 3.2 |
| `RMP-05` | Every release carries one type, one change class and one tag form, assigned together | 4.2 |
| `RMP-06` | Hotfix and emergency change are distinct types sharing one authority | 4.2 |
| `RMP-07` | A statutory, `RC-A` or limit-bearing configuration change is never Standard | 4.2 |
| `RMP-08` | A wave release is authorised after its gate, not before | 4.2 |
| `RMP-09` | Risk class routes approval; the CAB owns the routing rules | 4.3 |
| `RMP-10` | W1–W5 releases run on `M30` records with a manual calendar; `M66` arrives at W6 | 4.4 |
| `RMP-11` | "PIR" unqualified means `RL-005`'s wave review | 4.5 |
| `RMP-12` | Three trains: `T-STAGE`, `T-PROD`, `T-WAVE` | 5.2 |
| `RMP-13` | Routine production releases deploy Sunday–Tuesday | 5.3 |
| `RMP-14` | Wednesday requires Release Manager approval and named on-call | 5.3 |
| `RMP-15` | Thursday 15:00 → Sunday is closed except by emergency | 5.3 |
| `RMP-16` | The executor is never the sole approver, at every risk class | 5.3 |
| `RMP-17` | A wave release follows the cutover runsheet's clock, not `RMP-13` | 5.3 |
| `RMP-18` | A user-facing MAJOR means the task changed, not the API | 6.2 |
| `RMP-19` | Retraining-bearing change releases as MAJOR even if SemVer says MINOR | 6.2 |
| `RMP-20` | Programme MAJOR = wave number | 6.3 |
| `RMP-21` | UI footer, ticket, note and tag carry the same version string | 6.3 |
| `RMP-22` | OCA and programme versions are never cross-derived | 6.3 |
| `RMP-23` | A freeze has an owner, exact instants and one waiver authority | 7.1 |
| `RMP-24` | `F4` statutory has a single non-delegable waiver authority | 7.5 |
| `RMP-25` | Wave release in production by **T−15 working days** before the freeze instant | 7.6 |
| `RMP-26` | Wave code freeze at **T−25 working days** | 7.6 |
| `RMP-27` | Between wave release and `C8`, only emergency changes reach the scope | 7.6 |
| `RMP-28` | The wave release deploys disabled; the release is the toggle at `C7` | 7.6 |
| `RMP-29` | No feature release into a wave's live scope during its hypercare | 7.7 |
| `RMP-30` | `F6` blocks release, never build | 7.7 |
| `RMP-31` | Tranched rollout runs `F6` from the last tranche | 7.7 |
| `RMP-32` | An emergency release inside `F7` invalidates the affected evidence | 7.8 |
| `RMP-33` | `F8` windows published before 1 January from the gazette | 7.9 |
| `RMP-34` | `F8` covers ±3 working days around multi-day public holidays | 7.9 |
| `RMP-35` | `F8` is manual until `MD-041` is populated | 7.9 |
| `RMP-36` | Freezes compose; overlapping freezes need all waiver authorities | 7.10 |
| `RMP-37` | The CAB cannot be quorate as specified until three roles are appointed | 8.2 |
| `RMP-38` | Every production release traces to a named person via a signed tag | 8.4 |
| `RMP-39` | Emergency is a service condition, not a schedule preference | 9.2 |
| `RMP-40` | A hotfix open beyond 24 hours is reported at the next CAB round | 9.5 |
| `RMP-41` | A production release without a published note is incomplete | 10 |
| `RMP-42` | Note `Known issues` reconcile with the hypercare known-issue log | 10 |
| `RMP-43` | Deprecation's 30 days start at publication | 11 |
| `RMP-44` | Contractually bound capability cannot be removed on the 30-day route | 11 |
| `RMP-45` | Removing legacy capability is `RL-006`, not deprecation | 11 |
| `RMP-46` | No DORA target before `G4`; baseline first | 12.2 |
| `RMP-47` | `RMP-M7` is the only metric measurable at issue | 12.3 |

**Forty-seven rules.** Counted from this table at 2026-08-18 23:27 (+06).

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Which document owns the **feature-toggle register** — `PE-009`, `BE-003`, or a new one? `RMP-04` creates the obligation and nothing holds it | Solution Architect | **W1** | `RMP-02`, `RMP-28`, `RL-004` tranching |
| `Q-02` | What is the interim change-calendar tool for W1–W5, before `M66`? A spreadsheet is a change calendar with no collision detection | Change Manager | **W1 minus 1 month** | `RMP-10`, all of §7 |
| `Q-03` | When does `AR-007` v1.1 issue and resolve the four-versus-five component manifest scheme? | Solution Architect | W1 | `RMP-22`, `GW-31` |
| `Q-04` | Who populates `MD-041`, and by when? `F8` is unenforceable until then | HR Director with the Master Data Owner | **Before 1 January of the first delivery year** | `RMP-33`, `RMP-35` |
| `Q-05` | When are the Change Manager, Security Lead and Service Manager appointed? | Programme Director | **W1** | `RMP-37`, CAB quorum, `GV-009` §5.3 |
| `Q-06` | Which contractual notice periods bind capability removal? `CO-003` ⛔ | Legal Counsel with the PMO | W2 | `RMP-44` |
| `Q-07` | Does `BE-003` v1.1 accept the §9.4 correction, or does it intend a different route? | Engineering Lead | **W1** | `RLA-01` closure |
| `Q-08` | Do `PE-004`'s and `PE-008`'s telemetry designs emit what `RMP-M1`…`RMP-M5` consume? Both issued without citing this policy as a consumer | Platform Lead with the Release Manager | **W1** | `RMP-47`; the gate release-metrics report |

---

## 15. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RL-001-D-01` | How to reconcile `SP-031`'s CAB with `M66`'s rejection of a CAB cadence | (a) Follow `SP-031`, weekly CAB · (b) Follow `M66`, no CAB · (c) Named body, asynchronous default, convened for High risk | **(c)** | `SP-031` needs a *body*; `M66` objects to a *meeting*. (c) satisfies both, and discharges `SP-031`'s open DoD item | The CAB has three unfilled standing seats (`RMP-37`); interim quorum applies |
| `RL-001-D-02` | Whether to set DORA targets at issue | (a) Adopt industry benchmarks · (b) Baseline for four gates, then set | **(b)** | An industry benchmark is a number about other organisations. `GA-04`'s denominator discipline applies | No throughput target until `G4`; `RMP-M6` and `RMP-M7` are set now because both are already ruled |
| `RL-001-D-03` | Where to place the wave-release deployment date relative to the freeze instant | (a) Before the freeze instant, as `CUT-01` literally says · (b) Before `P0` rehearsal begins | **(b) — T−15 working days** | `MG-005` requires rehearsal against the code that will be live. (a) permits rehearsing different code, which is what `CUT-01` exists to prevent | Wave code freeze moves to T−25 working days, lengthening the required build window by roughly five weeks |
| `RL-001-D-04` | Whether to restate `OP-006`, `SP-031` and `BE-003` content | (a) Restate, for a self-contained policy · (b) Adopt by citation | **(b)** | `MST-01`: *"a Category 12 rule is adopted by citation and never restated."* Restating creates two sources that drift | This document is unreadable without `OP-006` §4 and `BE-003` §8 to hand. That is the intended cost |
| `RL-001-D-05` | Rule prefix | (a) `RL-nn`, matching the category code · (b) A verified-unused prefix | **(b) — `RMP`** | `RL-01`…`RL-12` is `TR-024`'s rule space, used 36 times | The category code and rule prefix differ, as they do for `GV-009`'s `SG-` and `GA-` |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every `OP-006` release type maps to exactly one `SP-031` change class | §4.2 — 8 rows plus the release-candidate row |
| `AC-02` | Freeze windows are **derived** from a named business cycle, not asserted | §7.3–§7.9; each carries a derivation paragraph |
| `AC-03` | `MG-006` `CUT-01`'s missing date is supplied and traceable to `DM-014`'s phase model | `RMP-25`, `RMP-26`, `RL-001-D-03` |
| `AC-04` | `SP-031`'s open DoD item — CAB membership, cadence, quorum — is closed | §8.2 |
| `AC-05` | The `SP-031` / `M66` CAB contradiction is ruled, with reasoning | §4.6, `RL-001-D-01` |
| `AC-06` | The `BE-003` §9 mis-citation is corrected and routed to its owner | §9.4, `RLA-01`, `Q-07` |
| `AC-07` | No rule identifier collides with any existing identifier in the workspace | §2.4; `RMP` verified at zero across 754 files |
| `AC-08` | Every metric states whether it is measurable today | §12.3 — six of seven are not, and it says so |
| `AC-09` | Every open question has an owner and a needed-by date | §14 — seven questions |
| `AC-10` | Nothing owned by `OP-006`, `SP-031` or `BE-003` is restated | `RL-001-D-04`; §6.1 and §10 are pointers |

**Definition of done.** Complete when every criterion above holds, the `PGD-000` row is updated with
a fresh enumeration timestamp, and the approver has signed. **Test (d) of `PGD-000` §0.3 — an
approval record — cannot be met until `GV-001` `CC-01` completes** (`PGD-A2-25`); the ✅ this
document carries is qualified on that basis, as all 99 before it are.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `BE-003` §8, §9 | Version schemes, tag forms and hotfix mechanics adopted by citation |
| Upstream | `OP-006` | Release types, notice periods and the whole notes standard adopted |
| Upstream | `SP-031`, `SP-004` | Change classes and approval limits adopted; §8.2 completes `SP-031`'s DoD |
| Upstream | `GV-009` | `GA-03`/`GA-10` derive `F7`; `GV-009` §6.3 gates the wave release |
| Upstream | `QA-010` §5 | Defect thresholds consumed at the wave release |
| Upstream | `OP-002` §4.3, §4.8 | Hypercare durations derive `F6` |
| Upstream | `DM-014`, `MG-005`, `MG-006` | Cutover phases and the rehearsal requirement derive `F5`, `RMP-25`, `RMP-26` |
| Downstream | **`RL-002`** | Executes every release this policy authorises; owns pre-flight, verification and abort |
| Downstream | **`RL-003`** | Consumes `RMP-28`'s toggle-at-`C7` model as the release half of the go decision |
| Downstream | **`RL-004`** | Uses `RMP-03` toggle-releases to bring branch tranches live |
| Downstream | **`RL-005`** | Measures `RMP-M1`…`RMP-M7` per wave; owns the unqualified "PIR" |
| Downstream | **`RL-006`** | `RMP-45` routes legacy removal there |
| Downstream | `PE-004` (issued; unimplemented) | Must emit the deployment events `RMP-M1`, `RMP-M2` and `RMP-M4` consume |
| Downstream | `PE-008` (issued; unimplemented) | Must emit the failure signals `RMP-M3` and `RMP-M5` consume |
| Downstream | `PE-009` (issued 2026-08-19) | Candidate owner for the `RMP-04` toggle register — confirm at `Q-01` |
| Lateral | `TR-024` | Owns `RL-01`…`RL-12`, the release-**training** rule space. §2.4 |
| Lateral | `M30`, `M66` | The systems of record for change; §4.4 |
| Lateral | `CO-003` ⛔ | Contractual notice periods for `RMP-44` |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`RL-002`](RL-002_Deployment_Plan_and_Go_Live_Checklist.md) ·
[`RL-003`](RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) ·
[`RL-004`](RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) ·
[`RL-005`](RL-005_Post_Implementation_Review_Standard.md) ·
[`RL-006`](RL-006_Legacy_Decommissioning_Plan.md) ·
[`../07_Build_Engineering_and_Development_Standards/BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md`](../07_Build_Engineering_and_Development_Standards/BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md) ·
[`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md`](../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) ·
[`../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md) ·
[`../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md`](../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md)

**Workspace**
`../../project_content/17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md` ·
`../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md` ·
`../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md` ·
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` ·
`../../project_content/08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` §12.6

**External standards and sources** *(all verified 2026-08-19)*

| Source | Edition / date | Used for |
|---|---|---|
| ITIL 4 — Release Management practice | ITIL 4, current framework | §3, §4 |
| ITIL 4 — Deployment Management practice | ITIL 4 | §3; delegated to `RL-002` |
| ISO/IEC 20000-1:2018 **+ Amd 1:2024** | Amendment published February 2024 — climate action; **no change to §8.5** | §2.1, §4, §8, §10 |
| ISO 9001:2015 | §8.6 | §8.4 |
| Semantic Versioning 2.0.0 | — | §6, via `BE-003` |
| DORA / Google Cloud *State of DevOps* | **2025 edition** — four keys plus **rework rate** and the *reliability* quasi-metric; seven team profiles replace the older cluster model | §12.1 |

> **Currency note for `RR-005`.** Two items in this table need re-verification before `G1`:
> (a) whether an ITIL edition after 4 has been published by AXELOS/PeopleCert — vendor training pages
> claim a *"V5"* for 2026 and no primary source confirms it; (b) whether the *State of DevOps* 2026
> edition changes the metric set again. Both are `PG-M4` obligations, and neither changes a rule in
> this document if it moves.

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.1 | 2026-08-19 | Release Management | **Audit corrections, `PGD-AUDIT-CAT-12`.** `RLA-16` — §12.3 attributed six unmeasurable metrics to two **absent documents**; both were issued the same day and the blockage is **implementation**, not documentation. Table and `RMP-47` corrected; `Q-08` added, because neither `PE-004` nor `PE-008` cites this policy as a telemetry consumer. Status of `PE-002`/`PE-004`/`PE-008`/`PE-009`/`SV-001`–`SV-003` refreshed throughout | *Pending — `GV-001` `CC-01`* |
| 1.0 | 2026-08-19 | Release Management | Initial issue. Forty-seven `RMP` rules. Maps `OP-006`'s eight release types to `SP-031`'s three change classes for the first time; derives eight freeze windows; supplies the two dates `MG-006` `CUT-01` was missing; constitutes the CAB, discharging `SP-031`'s open DoD item; rules the `SP-031`/`M66` CAB contradiction; corrects `BE-003` §9's `RL-003` mis-citation | *Pending — `GV-001` `CC-01`* |

---

*`RL-001` · Category 12 · Rule space `RMP` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
