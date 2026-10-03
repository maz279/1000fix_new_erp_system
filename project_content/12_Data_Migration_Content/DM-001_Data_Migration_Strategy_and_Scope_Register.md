---
id: DM-001
title: Data Migration Strategy and Scope Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead
author: Data Migration with Enterprise Architecture and MDM
reviewers: [CTO, CFO, Chief Commercial Officer, HR Director, Master Data Owner, QA Lead, Legal Counsel, Programme Content Lead]
approver: CTO with CFO
content_class: E
purpose: >
  Declares, for every one of the 67 modules, what data moves into the ERP, what is archived, what
  is authored new, what is established by physical count, what is deliberately left behind and what
  must be destroyed rather than carried — with the cut-off date, historical depth and reason for
  each decision. Migration scope decided late is migration scope decided expensively, and this
  register is also the content counterpart of the planned `06-03_Data_Migration_Strategy.md`, which
  does not exist.
traces_to: [06-03, 05-02, M01, M06, M15, M17, M19, M20, M21, M24, M33, M45, M49, M50, M56, M58, M64, 06-01, 06-02, MD-048, DM-002, DM-003, DM-011, DM-013, DM-014]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §12 — Data Migration Sources (11 source domains with volumes, targets and waves) and Migration Standards MIG-01…MIG-07
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/ — §16.4 Data Migration extracted from all 67 module specifications by enumeration on 2026-08-18; every disposition in §4.2 is derived from those sections, not asserted
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §11.6 — migration requirements MIG-001…MIG-015, §6.1 current system landscape, §6.5 legacy decommission commitment
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 — RSK-014 migration quality below usable threshold; ASM-03 existing customer and device data exportable at ≥ 80% quality; DEP-05 legacy data extracted, profiled and cleansed
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 §Gates — G1-05 customer and device data migrated and reconciled; G2-06 inventory accuracy ≥ 95% at migrated locations; G3-08 financial history reconciled to the trial balance
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Act 2026 (Bangladesh), enacted from the Personal Data Protection Ordinance 2025 — explicit, specific and revocable consent; transparency notice obligation; enforcement mechanisms activating around 13 May 2027
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# DM-001 — Data Migration Strategy and Scope Register

> **Read this before any other `DM` file.** Every mapping workbook, load template, quality rule and
> reconciliation report in Category 12 operates *inside* the scope this file declares. A workbook
> that maps a dataset this register places out of scope is wasted effort; a dataset this register
> omits is a cutover surprise.
>
> **Identifier note (`CG-005` §3.3).** Throughout Category 12, `DM-001`…`DM-014` are **content**
> identifiers. The two-digit `05-02` `DM-01`…`DM-15` are **modelling standards** and are always
> written with their document prefix.
>
> **Second identifier note.** Two `MIG` spaces exist and are not the same register. `05-02` §12
> `MIG-01`…`MIG-07` are the **migration standards**; the BRD §11.6.2 `MIG-001`…`MIG-015` are the
> **migration requirements**. This file qualifies every citation of both. See open item `O-07`.

---

## 1. Purpose

The 1000FiX estate has **no system integration at all**. The BRD §6.1 records the position
plainly: a WordPress site, two unconnected order-tracking portals, a standalone accounting tool,
paper forms, sign-in books, an Excel payroll, and manual spreadsheets holding service orders,
inventory, customer data, contracts and HR. **System integration score: zero.**

Migration into a 67-module ERP from that estate is not a technical exercise with a business
component. It is a **business exercise with a technical component**, and the largest single
decision in it is not *how* data moves but *whether it moves at all*.

Four modules refuse migration outright and require a physical count instead. `M15` §16.4 states the
reasoning in one sentence that governs this entire category:

> *"The spreadsheets are 75% accurate; loading them guarantees that inventory accuracy never
> recovers, because every subsequent variance is contaminated by an unknown opening error."*

`M49` §16.4 and `M50` §16.4 take the same position for fixed assets and cash, citing `M15`
explicitly. `M45` §16.4 extends it to test equipment and calibration. **Four independent modules
reached the same conclusion, which makes it a programme position, not a module preference.**

**Consequence of absence (`CP-03`).** Without this register:

| What happens | Why |
|---|---|
| Mapping workbooks are built for datasets that were never in scope | Nobody declared the boundary |
| A dataset nobody mapped is discovered at cutover | `05-02` §12 lists eleven source domains; the 67 module `§16.4` sections list **far more** |
| "Migrate everything" becomes the default | It is the only decision available when no decision was recorded |
| Physical counts are scheduled as data tasks and under-resourced | 51+ branches, van stock, 8,000–20,000 fixed assets and cash at every location, inside a cutover window |
| Personal data moves without a lawful basis | `M33` §16.4 rule 2 and BRD `MIG-015` both require one; neither names who confirms it |
| Historical records are loaded into operational tables | And then contaminate SLA, rework, ageing and KPI computation forever |

---

## 2. Scope

**In scope:** the six migration dispositions and their definitions; the disposition assigned to
every dataset named in any module's §16.4; cut-off dates and historical depth per domain; the
archive-area rule; the legacy-identifier rule; the parallel-run and reversibility position; the
lawful-basis position for personal data; the physical-count commitment; and rules `MS-01`…`MS-26`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Which legacy system each dataset physically comes from, and how it is extracted | [`DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md`](DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md) |
| The order in which entities load | [`DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md`](DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) |
| Field-level source-to-target mapping | `DM-004` … `DM-010` |
| Validation, cleansing, matching and survivorship | [`DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md`](DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) |
| The load file formats business owners fill in | [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) |
| How a load is proven correct | [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) |
| Freeze windows and branch communication | [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) |
| **Migration tooling, staging architecture, environments, ETL platform, rollback mechanics** | **`06-03_Data_Migration_Strategy.md` — which does not exist.** See `O-01` |
| Seed master-data load order (the 47 authored `MD` datasets) | [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md) |
| The privacy notice served to migrated data subjects | [`../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) — written, at `Draft`, **wave W2**. See `O-03` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Data Migration Lead** | Hold the scope boundary against "while we're at it" requests |
| **CTO** | Approve what does and does not move, and carry the decision to Steering |
| **CFO** | Approve the trial-balance basis, the count commitment and the write-off positions |
| **Business owners (per module)** | Understand what their function must supply, count, author or accept losing |
| **Branch managers (51+)** | Know that a count — not a data load — is what W2, W3 and W5 ask of them |
| **QA Lead** | Derive the migration acceptance criteria that `TS-018` signs |
| **Legal Counsel / Chief Data Officer** | See every personal-data movement in one place, with its basis stated or absent |
| **Migration analysts** | Know which of six dispositions their dataset carries before opening a workbook |

---

## 4. Content

### 4.1 The six dispositions

**Every dataset in the estate carries exactly one disposition.** The set is closed (`MS-01`). It is
derived from the language actually used across the 67 §16.4 sections, not invented for this file.

| Code | Disposition | Definition | Lands in | Typical evidence |
|:--:|---|---|---|---|
| **`M`** | **Migrate — live** | Loaded into operational tables and used by business logic on day one | The operational model | A mapping workbook (`DM-004`…`DM-010`) and a signed reconciliation |
| **`A`** | **Migrate — archive** | Loaded, retrievable, **flagged, and excluded from operational logic, SLA, ageing and KPI computation** | Archive area / warehouse | `05-02` `MIG-06`; `M01` §16.4; `M08` §16.4; `M23` §16.4 |
| **`N`** | **Author new** | No usable source exists; the dataset is created by people, not extracted | The operational model | An `MD` seed specification or a business authoring exercise |
| **`C`** | **Count / survey at cutover** | The opening position is established by a **physical count or site survey**, witnessed and signed — not by loading a record | The operational model | A count sheet, a witness signature, a variance report |
| **`L`** | **Leave** | Deliberately not migrated; retained where it is, or allowed to lapse | Nowhere in the ERP | A recorded decision naming what is being given up |
| **`P`** | **Purge** | Must be **destroyed** before go-live, not carried | Nowhere | A destruction record |

> **Why `C` is a disposition and not a project task.** If a physical count is recorded as a task in
> a delivery plan, it is estimated by the delivery team. If it is recorded as a *disposition* in a
> migration register, it is owned by the business function that must perform it and appears in the
> cutover checklist (`DM-014`). Four modules make it non-negotiable; it must be visible where scope
> is visible.

> **Why `P` exists.** `M06` §16.4: *"any customer data currently held from past recovery work must
> be audited and purged before Wave 6 go-live"*. `M58` §16.4: historical job applications are *"personal
> data with no lawful retention basis and no consent on record"* — migrating them *"imports a
> compliance problem into a new system on day one"*. Neither is a migration; both would be invisible
> if the register had only "in scope / out of scope".

### 4.2 The scope register

Derived by extracting §16.4 from all 67 module specifications on **2026-08-18** (`RG-06`, `CP-11`).
Waves shown are the waves stated by the owning module, which is the **load wave** — see §4.6 on the
distinction between load wave and build wave.

#### 4.2.1 Disposition `M` — migrate live

| Module | Dataset | Volume stated by the module | Load wave | Workbook |
|---|---|---|:--:|---|
| `M33` | Customer records, portal accounts, corporate account lists, addresses | 100,000+ customers; ~2,000 corporate; 100,000+ addresses | W1 | `DM-004` |
| `M07` | Account assignments, renewal-tracked contracts, open opportunities | ~2,000 / 5,000+ / <200 | W1 | `DM-004` |
| `M17` | Devices from the legacy order-tracking system, service history, corporate estates, warranty records, rental pool | **300,000–600,000 distinct devices** | W1–W3 | `DM-005` |
| `M01` | Branch service order spreadsheets — open and recent | ~50,000 | W1–W2 | `DM-006` |
| `M31` | Workshop WIP job cards | ~500 devices | W2 | `DM-006` |
| `M02` | Technician master; open field jobs | 200–400; ~1,000 | W2 | `DM-004`, `DM-006` |
| `M10` | Privilege members with **actual remaining term** | To be profiled | W2 | `DM-004` |
| `M37` | Service descriptions, parts rows, brand catalogues, brand/model lists — **all land in Draft** | ~1,200 / ~18,000 / ~60,000 / ~4,000 | W1–W2 | **Unassigned — see `O-05`** |
| `M15` | Brand consignment balances; open RTVs | 17+ brands; current | W2 | `DM-007` |
| `M03` | Open pick-and-drop jobs; courier partners and rate cards; rider master | ~200; 3–5; 50–150 | W3 | `DM-004`, `DM-006` |
| `M16` | Open purchase orders; supplier price lists; open RTVs | 150–400 lines; 40–120 suppliers | W3 | `DM-007` |
| `M42` | Supplier profiles, documents, price lists, framework agreements | 40–120 active; 200–400 historical | W3–W4 | `DM-004`, `DM-007` |
| `M19` | Chart of accounts (rationalised); **trial balance at cutover**; comparatives; FX history | 400–800 accounts; 1–2 years | W3 | `DM-008` |
| `M20` | Open invoices, credit notes, unapplied receipts, deposits, disputes, credit terms | 8,000–15,000 open items | W3 | `DM-008` |
| `M52` | Open vendor invoices, advances, retention, employee advances, expense claims | 800–2,000 open items | W3 | `DM-008` |
| `M50` | Bank account master and mandates; open reconciling items; cheque stock; open LCs and facilities | 12–25 accounts | W3 | `DM-008` |
| `M24` | Contract originals, statutory financial records, employee files, ISO records, brand authorisations | ~3,000–5,000 contracts; 7-year statutory set | W3–W6 | **Unassigned — see `O-04`** |
| `M63` | Delegation-of-authority matrix; approval thresholds; in-flight approvals | All limits in force | W3 | `DM-012` templates |
| `M60` | Trade licence, VAT/BIN, TIN, sector registrations; retention schedule | ~10–20 | W3 / W6 | `DM-012` templates |
| `M08` | Active AMC/RAMC contracts, corporate agreements, MSP agreements, brand authorisations | 3,000–5,000 contracts | W4 | `DM-010` |
| `M09` | Outstanding claims (evidenced only), sold extended warranties, brand rate cards, consignment part balances | ~2,000 open claims; ~400 rate lines | W4 | `DM-010` |
| `M39` | AMC/RAMC billing schedules, corporate billing arrangements, payment mandates | 3,000–5,000 | W4 | `DM-010` |
| `M53` | Revenue contracts, performance obligations, **opening deferred revenue rebuilt obligation by obligation** | All active contracts | W4 | `DM-008`, `DM-010` |
| `M51` | Tax registrations, current and prior-year statutory packs, opening input VAT credit, **Mushak 6.3 sequence position**, open withholding deposits | Per entity | W4 | `DM-008` |
| `M27` | Existing SMS templates; DND status for the customer base | 250,000+ numbers | W1 / W4 | `DM-004` |
| `M34` | Open complaint records only | To be profiled | W4 | `DM-006` |
| `M40` | Brand authorisation documents with verified expiry; brand partner contacts | 17+; 60–100 | W4 / W7 | `DM-010` |
| `M21` | Employee records, employment contracts, org structure, salary structures, bank details, **single opening service-book entry** | 500+ | W5 | `DM-009` |
| `M55` | Leave balances **agreed with each employee before cutover**; leave policy; holiday calendar | 500+ | W5 | `DM-009` |
| `M56` | **Year-to-date tax, PF and gratuity balances**; loans and advances; investment declarations | 500+ | W5 | `DM-009` |
| `M22` | Certificates where evidenced; brand certification lists | Variable | W5 | `DM-009` |
| `M23` | Open CAPAs and audit findings (confirmed open only); certificates | To be profiled | W5 | `DM-010` |
| `M46` | Vehicles, insurance policies, driver licences **verified against the physical document** | 150–400 vehicles; 200–400 drivers | W5 | `DM-005` |
| `M13` | Open rental agreements; deposits reconciled to the Finance liability | Live agreements only | W6 | `DM-010` |
| `M14` | Refurbishment WIP; refurbished stock on hand; live refurbished-unit warranties | All units held | W6 | `DM-005` |
| `M44` | Open letters of credit; in-flight consignments; NBR tariff schedule; permits | 5–20 LCs | W6 | `DM-007` |
| `M54` | **Current-year budget as an approved locked version** | All cost centres | W6 | `DM-008` |
| `M12` | Informal sub-contractor list — **as Registered, never as Approved sellers** | 50–150 | W7 | `DM-004` |
| `M67` | In-flight corporate rollouts and branch openings | Current only | W7 | `DM-012` templates |
| `M18` | Accumulated e-waste backlog; recycler relationships (certification re-verified) | All held stock | W8 | `DM-005` |
| `M28` | Existing API consumers; integration configuration; **credentials rotated on migration** | 2–4 consumers | W1 | `DM-012` templates |
| `M29` | Internal user accounts (**all credentials reset**); customer portal accounts (**forced re-authentication**) | 150–250; 250,000+ | W1 / W2 | `DM-004` |
| `M30` | Branch list, legal entity, cost centre structure, existing scheduled jobs, extracted configuration | 51+ branches; 1 entity | W1 | `MD-048` seed |
| `M64` | Code lists and business parameters extracted from code and legacy systems; cross-references | ~200 lists / ~5,000 values; ~300 parameters | W2–W3 | `MD-048` seed |
| `M65` | Bangladesh administrative geography; public holidays; exchange rates | 8 / 64 / ~495 | W1 | `MD-048` seed |
| `M05` | Corporate AMC clients with IT scope; client asset lists | To be profiled | W5 | `DM-010` |
| `M06` | Current data-recovery job cards only | Current work | W6 | `DM-006` |
| `M11` | Price points **after reconciliation to one governed set**; brand rate cards; corporate negotiated rates | ~1,200 points; ~18,000 rows; ~400 rate lines | W3 | **Unassigned — see `O-05`** |
| `M36` | Open corporate proposals; open tender register; outstanding bid bonds | ~200; ~30; ~15 | W3 | `DM-010` |
| `M48` | Historical fault and failure records from `M17` as an ML label set | 24–36 months | W8 | `DM-005` |
| `M49` | Asset classes, useful lives, methods; **opening cost and accumulated depreciation after count**; tax-book WDV | 8,000–20,000 assets | W5 | `DM-008` |
| `M45` | Calibration records **only where a certificate exists and its traceability is verifiable** | Unknown | W5 | `DM-005` |
| `M47` | Leases, licences, deposits — **from the physical documents, scanned and hashed** | 51+ sites | W7 | `DM-010` |
| `M66` | Software entitlements; IT vendor contracts | Purchase records | W6 | `DM-005` |

#### 4.2.2 Disposition `A` — migrate to archive

| Module | Dataset | Volume | Load wave | Exclusion required |
|---|---|---|:--:|---|
| `M01` | Paper service history archive; `station.1000fix.com` and `123.0.26.238` order tracking | **500,000+ historical** | W2–W6 | SLA, rework and all KPI calculations |
| `M24` | Branch paper job sheets and service records, OCR-indexed | 500,000+ *(profiling required)* | W3–W6 | Operational logic; retrieval only |
| `M08` | Historic expired contracts | Unknown | W4 | Contract base and renewal KPIs |
| `M09` | Email-based claim records; unevidenced outstanding claims | 12–24 months | W4 | Claim recovery and ageing |
| `M36` | Historical accepted AMC proposals | ~1,500 | W3–W4 | Conversion, turnaround and variance KPIs |
| `M23` | Paper ISO records — audits, reviews, NCs, CAPAs | 3 certification cycles | W5 | Quality KPI computation |
| `M20`, `M52` | Historical invoices, 2 years where recoverable | Best-effort | W3–W4 | **The operational ledger** — warehouse only |
| `M11`, `M38`, `M39`, `M40`, `M12` | Historical transactions retained for baseline only | 12–24 months | Per wave | All operational logic |
| `M50` | Historical bank statements | 1–2 years | W3–W4 | Reconciliation logic |
| `M49` | Historical disposals | 2 years | W5 | Register and depreciation |
| `M17` | Legacy service history, 24–36 months where recoverable | Best-effort | W2 | Warranty entitlement decisions |
| `M57` | Historical appraisal records | Variable | W5 *(optional)* | Performance scoring |

> **`MS-08` — the archive rule.** An archived record is **retrievable, flagged and excluded**. All
> three, or it is not archived — it is loaded. `05-02` `MIG-06` requires the flag; `M01` §16.4
> requires the exclusion; `M24` §16.4 requires classification and a retention class **on capture**,
> because *"bulk-loading unclassified scans would create exactly the unmanageable corpus M24 exists
> to prevent."*

#### 4.2.3 Disposition `N` — author new

These are the datasets with **no source at all**. They are the most commonly missed item in a
migration plan because they do not appear in any extract.

| Module | Must be authored | Lead time stated by the module |
|---|---|---|
| `M02`, `M30` | **Dispatch zones** — *"no formal zones exist today"* | Before W2 build |
| `M02` | Technician skill profiles | Before W2 |
| `M03` | Logistics zones and courier rate cards | Before W3 |
| `M16` | Spend category taxonomy, competitive thresholds, match tolerance bands | Before W3 build |
| `M41` | **Warehouse bin master (~6,000 bins at W3, ~20,000 at full build) and initial slotting** | W3, authored |
| `M44` | **HS classification for every imported part** — *"a multi-week effort requiring the agent's cooperation"* | **Before W6 build** |
| `M54` | Allocation cycles and drivers — *"current practice is largely undocumented"* | W6 minus 1 month |
| `M55` | Shift patterns and rosters | W5 |
| `M59` | **Hazard register, risk assessments and JSAs** — *"requires the HSE Officer to be in post first"* | W6, long lead |
| `M22` | **The initial competency matrix — supervisor assessment of 500+ employees** | **Well before W5** |
| `M23` | Rationalised checklist set — 30–60 branch variants become one governed set | W4 lead time |
| `M25`, `M62` | The register of every manual management pack, and the metric definitions buried in its formulas | Before W4 |
| `M63` | The register of routine operational work — **the denominator for the 85% automation target** | Before W3 |
| `M32`, `M34` | Intent taxonomy; complaint taxonomy | W4 |
| `M64` | Domain register, ~300–500 quality rules, hierarchies | W2 onward |
| `M65` | **The statutory obligation register** — *"discovered, not migrated"* | W1–W4 |
| `M66` | IT service catalogue and knowledge articles | W6 |
| `M67` | Five project templates capturing how 1000FiX actually runs a rollout | W7 |
| `M61` | **150–250 authored technical articles** covering the top 100 fault codes | W6 |
| `M29` | Roles, permission sets, SoD rules from `05-04` | W1 |
| `M28`, `M30` | Event schemas and runbooks, per module as each is built | W1 onward |
| `M26` | The existing human heuristics, encoded as declared model fallbacks | W6 |

> **`MS-11`.** A dataset with disposition `N` is **not a migration deliverable and must not appear
> in a migration plan as one.** It appears here so that its absence from the migration plan is a
> recorded decision rather than an omission. **Twenty-two such datasets are registered above**
> *(enumerated 2026-08-18)*; several carry lead times longer than the wave they serve.

#### 4.2.4 Disposition `C` — physical count or survey at cutover

**This is the single largest business commitment in the programme.**

| Module | What is counted or surveyed | Scale | Wave | Module's stated position |
|---|---|---|:--:|---|
| `M04` | Branch storage layout, counters, devices held | 51+ branches; ~5,000 devices | W1 | *"the most commonly underestimated task in Wave 1"* |
| `M15` | **Stock at every location, van stock recalled and counted, consignment balances brand-confirmed** | 10,000 SKUs × up to 51 sites; 200–400 vans; 17+ brands | **W2** | **Non-negotiable** |
| `M41` | Bin-level opening positions at WMS-enabled warehouses | ~6,000 bins | W3 | A smaller repeat of the `M15` count |
| `M50` | **Cash at every location, witnessed and signed**; bank balances **from the bank's own statement**; cheque stock | 51+ branches; 200–400 field staff; 12–25 accounts | **W3** | **Non-negotiable** |
| `M49` | **Full physical verification of the fixed-asset register** | 8,000–20,000 assets | **W5** | **Non-negotiable**; unfound assets written off with approval before cutover |
| `M45` | Physical equipment audit at every branch and workshop | 51+ sites | **W5** | **Non-negotiable** |
| `M46` | Driver licences verified against the physical licence | 200–400 drivers | W5 | Not transcribed from HR files |
| `M13` | Condition baseline for every unit on hire | All open rentals | W6 | Units without an outbound report are *baseline unknown* |
| `M14` | Every unit in stock assessed against the destruction gate | All units held | W6 | *"not negotiable"* |
| `M47` | Infrastructure and safety equipment survey at every site | 1,500–4,000 assets | W7 | Same visit as the `M45` audit — **schedule once, use twice** |
| `M66` | **IT asset physical audit across 51+ branches, workshop, warehouse and corporate office** | ~2,500 assets | W6 | *"a business commitment, not a software task"* |
| `M18` | Pre-implementation e-waste backlog, item by item through the full gate | All held stock | W8 | None may be grandfathered |

> **`MS-13`.** A `C` disposition dataset **has no mapping workbook and needs none**. What it needs is
> a count instruction, a count sheet, a witness, a variance procedure and a place in `DM-014`. Three
> of the twelve — `M45`, `M49`, `M66` — currently have none. See `O-06`.

#### 4.2.5 Disposition `L` — leave behind

Each row is a deliberate loss. **The loss is stated so that it is a decision, not a discovery.**

| Module | Not migrated | What is given up | Module's reason |
|---|---|---|---|
| `M07` | Historical win/loss | Conversion baselines | None exists in structured form |
| `M10` | Historical points balances | Member goodwill history | **No ledger has ever been kept** |
| `M13` | Historical rental history | Utilisation baseline; dispute support | No condition evidence exists |
| `M14` | Historical trade-in and resale records | Margin analysis; warranty support | No grading standard, certificates or cost records |
| `M18` | Historical disposal records | Statutory return support | No certificates, weights or custody evidence |
| `M19` | 51+ branch spreadsheets | Nothing — retained as reference documents in `M24` | Historical only |
| `M20` | Historical ageing | Ageing trend before go-live | Cannot be reconstructed from balances |
| `M25` | Historical report outputs | Comparability of old packs | *"unreproducible, being built on definitions that were never recorded"* |
| `M27` | Historical conversations | Contact-reason baseline | None exist in structured form |
| `M29` | Historical audit trail | Pre-ERP forensic capability | None exists |
| `M34` | Historical satisfaction data | CSAT baseline | None exists in structured form |
| `M35` | Historical campaign performance | Campaign benchmarks | None exists in structured form |
| `M43` | **Pre-ERP consumption records** | Forecast warm start | **Produced by a 75%-accurate process; would contaminate the demand series** |
| `M55` | Historical attendance | Attendance trend | Sign-in books are not machine-readable or reliable |
| `M56` | Historical payslips | Payslip reprint from history | Retained as documents in `M24` where they exist |
| `M57` | Historical KPI baselines | First-period incentive baseline | Accumulated, not migrated |
| `M63` | Historical approval records | Approval-behaviour baseline | No consistent trail exists |
| `M66` | Existing IT tickets | Ticket history | None recorded |
| `M67` | Historical project outcomes | On-time/on-budget baseline | No project system has existed |
| `M05` | Historical support correspondence | Case history | Client estates are discovered and onboarded, not migrated |

> **`MS-15`.** Nineteen `L` rows share one consequence: **the KPI baselines in `06-02` cannot be
> computed from history for those domains.** `RP-015` Benefits Realisation and KPI Baseline Register
> must therefore establish each of them by measurement or by declared estimate. This register is the
> evidence that the gap is structural, not an oversight in `RP-015`.

#### 4.2.6 Disposition `P` — purge before go-live

| Module | What must be destroyed | Deadline | Basis |
|---|---|---|---|
| `M06` | Customer data currently held from past recovery work, audited and purged | **Before W6 go-live** | `M06` §16.4 — *"a pre-implementation remediation task, not a migration"* |
| `M58` | Historical job applications | Before W6 | **Personal Data Protection Act 2026** — no lawful retention basis, no consent on record |
| `M28` | Every credential held in a configuration file or a developer's notes | W1 | **Rotated on migration**, on the assumption that anything held in plain text is compromised |
| `M29` | Every existing internal password | W1 | Set under an unknown policy in a system with no MFA |

### 4.3 Cut-off dates and historical depth

**`MS-16`: historical depth is a decision with a cost, taken once per domain, by a named owner.**
It is not a technical parameter. The module specifications record four of these decisions as *open
questions*, which means they are unresolved today.

| Domain | Depth | Cut-off basis | Decided by | Status |
|---|---|---|---|---|
| Service history | **Open — 3, 5 or all years** | `M01` `Q-04` | Ops Director / CTO | **Unresolved — W2 planning** |
| Financial comparatives | **Open — number of years for statutory and board reporting** | `M19` `Q-06` | CFO | **Unresolved — W3 minus 2 months** |
| Chart of accounts | **Open — rationalise before migration, or migrate as-is** | `M19` `Q-02` | CFO | **Unresolved; rationalisation strongly recommended by `M19`** |
| Complaint log | **Open — does an existing log with open cases exist** | `M34` `Q-08` | Customer Service Manager | **Unresolved — W4 minus 2 months** |
| Open AR / AP | Open items only, at cutover date | `M20`, `M52` §16.4 | CFO | Settled |
| Historical AR / AP invoices | 2 years, warehouse only, best-effort | `M20`, `M52` §16.4 | CFO | Settled |
| Purchase price history | 24 months where recoverable | `M16` §16.4 | Procurement Manager | Settled |
| Inventory consumption | 24 months where recoverable, **warehouse only** | `M15` §16.4; **excluded from `M43` forecasting** | Warehouse Manager | Settled |
| Payroll | **Year-to-date balances only** | `M56` §16.4 | HR Director + CFO | Settled |
| Employee service | **Single verified opening entry from the joining date** | `M21` §16.4 | HR Director | Settled |
| Device service history | 24–36 months where recoverable, best-effort | `M17` §16.4 | Service Ops Director | Settled |
| Bank statements | 1–2 years, warehouse only | `M50` §16.4 | CFO | Settled |
| Warranty device data | Sampled from 500,000+ records, **confidence = derived** | `M09` §16.4 | Finance Director | Settled |

> **`MS-17` — cut-off is a timestamp, not a date.** Every wave cutover declares an exact
> `Asia/Dhaka` cut-off instant (`05-02` `DM-08` stores UTC and presents `Asia/Dhaka`). A source
> record created after the cut-off instant is a **delta**, handled under `MIG-009` (BRD) incremental
> migration during the parallel run — never re-run as a full load. `DM-014` owns the instant.

### 4.4 Legacy identifiers, and why every record keeps one

`05-02` §12 `MIG-05` and BRD `MIG-010` both require it. `05-01` `FR-SRM-088` makes it a **delivered
feature**: *"Look up migrated historical service records with their original references."*

**`MS-18`.** Every migrated record — disposition `M` or `A` — carries three control values, populated
by the load and never editable afterwards: `legacy_source_system`, `legacy_record_id` and
`migration_batch_id`. `DM-012` defines their format; `DM-013` reconciles on them; `DM-004`…`DM-010`
map them.

Without them: a reconciliation cannot identify *which* rows failed, a customer quoting an old
reference cannot be served, an auditor cannot trace a balance to its source, and a re-run cannot
tell a duplicate from a new record.

### 4.5 Personal data, and the basis on which it moves

**This is the highest-consequence open item in the category.**

`M33` §16.4 states three rules and this register adopts all three verbatim as `MS-19`…`MS-21`:

1. **Profile before load.** Duplicate rate, completeness and validity are measured on the source
   before any load and reported to the CCO.
2. **No consent is inferred.** Historical customers migrate **without** consent records; consent is
   captured at their next interaction against the current notice. *"Assuming consent from prior
   dealings is not a lawful basis under the PDPA."*
3. **Sensitive fields last.** NID and TIN migrate **only after the Bangladesh-resident store is live
   and verified** (`05-06` NFR-086, NFR-086a).

What none of them settles is **the transparency notice**. BRD `MIG-015` requires that *"transparency
notice obligations [are] addressed for migrated data subjects"*, and `05-06` §PDPA `NFR-092`
requires a notice **before or during processing** stating categories, purposes, retention and the
withdrawal procedure.

**At W1, 100,000+ customers and 300,000–600,000 devices are processed into a new controller
environment.** The notice that discharges `NFR-092` for that population is
[`LG-008`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md), which
**was written on 2026-08-17 and stands at `Draft`, registered for wave W2** *(enumerated
2026-08-18)*. Two things therefore remain open, and neither is closed by the file existing:

| Open | Why it still blocks |
|---|---|
| **`LG-008` is a `W2` artefact and the first party load is `W1`** | A notice that arrives after the processing it describes does not discharge `NFR-092` |
| **The lawful basis for the migration processing itself is unconfirmed** | `LG-008` is customer-facing consent copy; it is not a legal-basis determination for a bulk controller-to-controller transfer, and `CG-013` legal escalation applies |

Recorded as `O-03` and reported to the audit.

`AUDIT-010` finding HC-01 raised the same class of question for transcript mining at W2 and remains
open. **This is the second Critical finding in the programme concerning the lawfulness of a planned
activity rather than its correctness, and it lands two waves earlier.**

### 4.6 Build wave versus load wave

The Master Index reading key defines **Wave** as *"the delivery wave that consumes it"*. The Master
Index §1 note qualifies this for exactly this category:

> *"Where a content file is needed before the wave that consumes it (master data and migration
> content almost always are), the wave shown is the **build wave**."*

**Both statements are in force and they mean different things.** For Category 12 the register wave
is the **build** wave; the module §16.4 wave is the **load** wave. They diverge by up to two waves:

| File | Register wave (build) | Load wave (per the owning module) | Gap |
|---|:--:|:--:|:--:|
| `DM-007` Inventory and parts | W1 | **W2** (`M15` §16.4, `06-01` W2) | 1 |
| `DM-008` Finance and open items | W1 | **W3** (`M19`, `M20`, `M50`, `M52` §16.4, `06-01` W3) | 2 |
| `DM-010` Contracts, warranty and claims | W2 | **W4** (`M08`, `M09` §16.4, `06-01` W4) | 2 |
| `DM-005` Device and asset | W1 | W1–W3 (`M17` §16.4) | 0–2 |

**`MS-22`.** Every Category 12 workbook states **both** waves in its §1. A workbook that states one
wave will be read as stating the load wave by a delivery planner and the build wave by a content
planner, and one of them will be wrong. Reported to the audit as a register-precision finding.

### 4.7 Reversibility, dry runs and the parallel run

| # | Position | Source |
|---|---|---|
| Every load is reversible; a dry run precedes every production load | Mandatory | `05-02` §12 `MIG-03` |
| Trial migration into `staging` with business UAT before every cutover | Mandatory | BRD `MIG-005` |
| Documented, **rehearsed** rollback plan for every cutover | Mandatory | BRD `MIG-007` |
| Database migrations forward-only, tested against a production-sized dataset, reversible by documented procedure | Mandatory | `05-06` `OPS-07` |
| **Two-week parallel run on service orders and finance before legacy decommission** | Mandatory | `05-02` §12 `MIG-07` |
| **One full parallel month-end close**, reconciled line by line and signed, before the legacy accounting system is retired | Mandatory | `M19` §16.4 |
| Migration tooling delivered to the Company, repeatable and re-runnable | Mandatory | BRD `MIG-008` |
| Non-production environments never contain unmasked residency-classified data | Mandatory | `05-06` `NFR-086c` |

> **`MS-23`.** *"Reversible"* means a **rehearsed** procedure with a measured duration, not the
> existence of a backup. A rollback whose duration is unknown cannot be inside a cutover window, and
> a fallback trigger (`DM-014`) that cannot be executed inside the window is not a trigger.

### 4.8 What the business is actually being asked for

Migration is routinely planned as a technical workstream. Across the 67 §16.4 sections, the
distribution of effort is the opposite:

| Disposition | Datasets | Who does the work |
|---|---:|---|
| `M` — migrate live | 54 | Migration team **with** the business owner supplying and confirming |
| `A` — archive | 12 | Migration team |
| `N` — author new | 22 | **The business, entirely** |
| `C` — count or survey | 12 | **The business, entirely** — 51+ sites, several times |
| `L` — leave | 20 | A decision, then nothing |
| `P` — purge | 4 | Security, Legal and the owning function |

**Thirty-four of the datasets that must exist for go-live are produced by people, not by pipelines**
— the twenty-two `N` rows and the twelve `C` rows, enumerated 2026-08-18.
`00-04` `DEP-05` names department heads as accountable for extraction, profiling and cleansing per
wave; `06-01` §Resourcing allocates **Data Owners at 20% through W1–W5**. Whether 20% of a data
owner covers a competency matrix for 500+ employees, an HS classification exercise, a hazard
register and three rounds of 51-site counting is a question this register raises and cannot answer
(`O-08`).

### 4.9 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **`MS-01`** | Six dispositions; the set is closed. Every dataset carries exactly one | **H** |
| **`MS-02`** | A dataset with no disposition in this register does not migrate. Absence is not permission | **H** |
| **`MS-03`** | A disposition is changed only by the module's business owner, recorded in `RF-006` | **H** |
| **`MS-04`** | Profiling precedes every load — completeness, validity, duplication, staleness, reported to the data owner (`05-02` `MIG-01`, BRD `MIG-002`) | **H** |
| **`MS-05`** | Cleansing happens in the source or a staging layer, **never silently during load** (`05-02` `MIG-02`, BRD `MIG-003`) | **H** |
| **`MS-06`** | Every load is reversible and preceded by a dry run (`05-02` `MIG-03`) | **H** |
| **`MS-07`** | Reconciliation counts and control totals are **signed by the business owner** before cutover (`05-02` `MIG-04`, BRD `MIG-006`) | **H** |
| **`MS-08`** | An archived record is retrievable, flagged **and** excluded from operational logic. All three | **H** |
| **`MS-09`** | No migrated record enters an `Active` or `Approved` state where the owning module requires approval (`M37`, `M12`, `M40`) | **H** |
| **`MS-10`** | Uncleansable records go to the archive area, flagged (BRD `MIG-012`); they are never dropped silently | **H** |
| **`MS-11`** | Disposition `N` datasets are authoring deliverables, not migration deliverables, and are resourced as such | **C** |
| **`MS-12`** | A physical count is witnessed and signed; the count sheet is the source record, not a spreadsheet transcription | **H** |
| **`MS-13`** | Every `C` dataset has a count instruction and a place in `DM-014` before its wave gate | **H** |
| **`MS-14`** | Variances found at count are resolved before cutover — written off with approval, or registered at approved deemed cost — never carried as unexplained | **H** |
| **`MS-15`** | Every `L` decision states what is given up, and the affected `06-02` baseline is referred to `RP-015` | **C** |
| **`MS-16`** | Historical depth is decided once per domain by a named owner and recorded here | **H** |
| **`MS-17`** | Cut-off is an exact `Asia/Dhaka` instant; post-cut-off records are deltas, never re-loads | **H** |
| **`MS-18`** | Every migrated record carries `legacy_source_system`, `legacy_record_id` and `migration_batch_id`, immutable after load | **H** |
| **`MS-19`** | Profile before load; the duplicate, completeness and validity result goes to the CCO (`M33`) | **H** |
| **`MS-20`** | **No consent is inferred.** Historical parties migrate with no consent record (`M33`) | **H** |
| **`MS-21`** | NID, TIN, passport, biometric and recovered-data fields migrate **only after** the Bangladesh-resident store is live and verified (`NFR-086`) | **H** |
| **`MS-22`** | Every Category 12 workbook states both its build wave and its load wave | **C** |
| **`MS-23`** | "Reversible" means rehearsed, with a measured duration that fits the cutover window | **H** |
| **`MS-24`** | Non-production environments never hold unmasked residency-classified data (`NFR-086c`) | **H** |
| **`MS-25`** | Every credential in scope is **rotated or reset** on migration, never carried (`M28`, `M29`) | **H** |
| **`MS-26`** | Bengali text is normalised to UTF-8 at extract, before any matching or loading (BRD `MIG-011`, `05-02` `DM-09`) | **H** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the same
> scale as `05-05` §1.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-02` §12 and §1 (`DM-01`…`DM-15`) | The eleven source domains, `MIG-01`…`MIG-07`, and the modelling standards every target must satisfy |
| `03_Modules/` §16.4 × 67 | **The entire §4.2 register is derived from these sections** |
| BRD §6.1, §6.5, §11.6 | The legacy landscape, the decommission commitment, `MIG-001`…`MIG-015` |
| `06-01` §3 | Wave content, per-wave migration statement and gate criteria |
| `06-02` §Gates | `G1-05`, `G2-06`, `G3-08` — migration is a gate criterion at three of five gates |
| `05-06` `NFR-086`/`086a`/`086b`/`086c`, `NFR-088`, `NFR-092`, `NFR-095`, `OPS-07` | Residency, retention, transparency and reversibility constraints |
| `00-04` `RSK-014`, `ASM-03`, `DEP-05` | The risk, the 80%-quality assumption, and the extraction dependency |
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md) | Seed load order; migration loads **after** the master data they reference |
| [`../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md`](../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md) | Source classes `P1`…`P4` used in this file's front matter |
| [`../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) · [`../10_Legal_Policy_and_Compliance/LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](../10_Legal_Policy_and_Compliance/LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | Written 2026-08-17, both at `Draft` and both registered **W2** — after the W1 processing they must cover (`O-03`) |

| Depended on by |
|---|
| `DM-002` … `DM-014` — every file in this category · `MD-048` load index · `TS-002` test data · `RP-015` KPI baselines · `CM-012` branch readiness · `OP-002` · every wave gate that names migration |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **At every wave boundary**, and before every cutover |
| Trigger for out-of-cycle review | A new source system discovered · a disposition change · a module §16.4 amendment · a `Q-` open question in any module being answered · a PDPA position changing |
| Owner | Data Migration Lead; dispositions owned by each module's business owner |
| Change log | `RF-006`, with the module and disposition named |
| Enforcement | `MS-01`…`MS-26`; `DM-013` reconciliation gate; `DM-014` cutover checklist; wave gates `G1-05`, `G2-06`, `G3-08` |
| Derivation | §4.2 is **regenerated by re-extracting §16.4 from all 67 modules**, never edited in isolation (`RG-06`, `CP-11`) |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`06-03_Data_Migration_Strategy.md` does not exist.** This file is its content counterpart and deliberately stops at the boundary of tooling, staging architecture, environment topology, ETL platform and rollback mechanics. **Those decisions have no owning document.** BRD `MIG-008` requires the tooling to be delivered to the Company, repeatable and re-runnable — against no specification | CTO | **W0 — before any extract is built** |
| **`O-02`** | **Four historical-depth decisions are unresolved** (§4.3): service-history depth (`M01` `Q-04`), financial comparatives (`M19` `Q-06`), chart-of-accounts rationalisation (`M19` `Q-02`), complaint-log existence (`M34` `Q-08`). Each changes volume, effort and mapping | Ops Director · CFO · Customer Service Manager | Per §4.3 |
| **`O-03`** | **The transparency notice reaches the wrong wave, and the lawful basis is still unconfirmed.** BRD `MIG-015` and `05-06` §PDPA `NFR-092` require a notice before or during processing. `LG-008` and `LG-012` **were written on 2026-08-17 and are registered at W2**; the first party load is **W1**, and neither file determines the lawful basis for a bulk migration. **100,000+ customers are processed at W1** | Legal Counsel with Chief Data Officer | **W1 — before the first party load** |
| **`O-04`** | **No mapping workbook covers `M24` document and paper-archive migration** — 500,000+ paper records at W3–W6, the largest single volume in the estate. Category 12 has fourteen registered files and none of them is it | Programme Content Lead with Quality Manager | **W3** |
| **`O-05`** | **No mapping workbook covers catalogue and pricing migration** — `M37` (~18,000 parts rows, ~1,200 service descriptions, ~60,000 OEM references, W1) and `M11` (~1,200 price points, W3). The `MD` seed specifications assume authored data; `M37` §16.4 says the data is migrated. **The seam is undeclared** | Programme Content Lead with CCO | **W1** |
| **`O-06`** | **Three `C` datasets have no count instruction and no owner**: `M45` test equipment (W5), `M49` fixed assets (W5), `M66` IT assets (W6). `M15` and `M50` counts are covered by `DM-007` and `DM-008`; these three are not | Data Migration Lead with CFO and CTO | **W5 minus 3 months** |
| **`O-07`** | **Two `MIG` identifier spaces exist** — `05-02` §12 `MIG-01`…`MIG-07` (standards) and BRD §11.6.2 `MIG-001`…`MIG-015` (requirements) — distinguishable only by digit count, exactly the failure `CG-005` §3.3 registered for `DM`. Unqualified citation will misattribute | Programme Content Lead with Enterprise Architecture | W1 |
| **`O-08`** | **Thirty-six datasets are produced by the business, not by pipelines** (§4.8), against a `06-01` allocation of **20% of a data owner's time**. The competency matrix alone covers 500+ employees. The allocation has not been tested against the workload | Programme Director with PMO | **W0 — it is a business-case item** |
| **`O-09`** | The Master Index §1 wave-month table (W1 = months 3–8) and `06-01` §3 (W1 = months 1–4) **state different months for the same waves**. Cut-off dates in §4.3 are expressed relative to waves; the two calendars must be reconciled before any date is published to 51 branches | Programme Content Lead with PMO | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; §7 Open Items added per category convention
- [x] Six dispositions defined, closed, and each derived from language actually used in the module set
- [x] **Every one of the 67 module §16.4 sections extracted and dispositioned by enumeration on 2026-08-18** (`RG-06`, `CP-11`)
- [x] Physical count established as a disposition, not a task, with all twelve instances listed
- [x] Purge established as a disposition, with all four instances listed
- [x] Every "leave behind" states what is given up and refers the baseline consequence to `RP-015`
- [x] Historical-depth decisions tabulated with four marked **unresolved** rather than assumed
- [x] Legacy-identifier rule stated and bound to `FR-SRM-088`
- [x] Personal-data position stated, with the missing transparency notice raised as `O-03` rather than assumed present
- [x] Build wave versus load wave distinction stated, with the four divergent files named
- [x] `DM` collision qualified on first use (`CG-008` `U-36`); the second `MIG` collision raised as `O-07`
- [x] Every factual claim carries a source with a verification date (`CG-012`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `06-03` absent — migration has no technical specification**
- [ ] **`O-03` transparency notice registered at W2 while processing begins at W1; lawful basis unconfirmed**
- [ ] **`O-04` / `O-05` two uncovered migration domains — register change required**
- [ ] Named approver recorded — **pending CTO with CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
