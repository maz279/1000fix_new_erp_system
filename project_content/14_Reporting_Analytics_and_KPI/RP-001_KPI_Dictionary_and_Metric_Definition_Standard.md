---
id: RP-001
title: KPI Dictionary and Metric Definition Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead with Enterprise Architecture
author: BI Lead with Enterprise Architecture and the module business owners
reviewers: [CTO, CFO, CCO, Operations Director, Quality Manager, HR Manager, Solution Architect, Programme Manager, Localisation Lead]
approver: CTO with CFO
content_class: D
purpose: >
  The single definition of every metric this programme measures — formula, numerator, denominator,
  inclusions, exclusions, grain, source, owner, baseline and target — and the rules that keep it
  single. One hundred and twenty-three citations across sixty-eight written content files already
  point at this file, which makes it the most depended-upon artefact in the register; and until it
  exists, "first-time fix rate" means whatever the person quoting it believes it means, a branch
  league table can be contested rather than acted on, and no coverage or benefit figure in the
  programme can be defended.
traces_to: [00-07 H2-04, 06-02, 06-02 §1, 06-02 §2, 06-02 §6, M25, M62, M62 §9, P06, 04-00 P06, 05-04, 05-04 §5, CG-004, CG-012, VB-008, RP-002, RP-003, RP-004, RP-005, RP-006, RP-007, RP-011, RP-012, RP-015, RP-016, BN-003, TS-005, TS-012, TS-014, HC-008, TR-011]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: RP-001_KPI_Dictionary_and_Metric_Definition_Standard_BN.md
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2 KPI Register — 95 identifiers KPI-001…KPI-095 with baseline, W4 and W8 targets and a source module; §1 business objectives BO-01…BO-18; §6 Benefit Tracking Discipline — "every KPI's baseline is measured and signed off before the relevant wave begins; a KPI without a baseline cannot claim a benefit"
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md §3 H2-04 — 22 KPI identifiers used by two or more modules, with the per-identifier claim table; and the note that Category H's KPI-212…KPI-305 collide with nothing
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M62_Data_Platform_Warehouse_and_Governance.md §9 BRU-DAT-01…BRU-DAT-12 — a business metric has exactly one definition held in the metric registry; change only through version-controlled review; consumers notified before a change takes effect; no retirement while a consumer remains; certification status displayed wherever the metric appears; every fact model declares its grain; every dataset and metric has a named business owner and a named technical steward
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-01 (no business metric is defined in a dashboard; every metric comes from M25's semantic layer), PRU-P06-07 (every metric's definition, owner and source available on the view without leaving it), PRU-P06-08 (every aggregate decomposable to its constituent records)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/_CATEGORY_E_AUDIT_REPORT.md finding A-02 — "KPI register exhausted. 06-02 §2.6 stops at KPI-049 and contains no identifiers" for the modules that followed
    verified: 2026-08-20
    class: P1
  - source: Enumeration of 1000fix_ERP_Module/03_Modules/**/M*.md and P*.md, 2026-08-20 — 250 distinct KPI- identifiers used, 247 defined in a module §15 table row, against 95 registered in 06-02
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# KPI Dictionary and Metric Definition Standard

| Item | Value |
|---|---|
| Register held here | Every metric the programme measures, reports or targets |
| Identifier space | `KPI-nnn`, programme-wide, allocated **only** here (§4.3) |
| System of record | `M62` metric registry — **this file is its content**, §2 |
| Consumers | `RP-002`…`RP-016`, all 12 portals, 28 SOPs, 18 `TR` packs, `TS` coverage reporting |
| Inbound citations | **123 across 68 written content files** — the most depended-upon file in the register |
| Wave | W1 · `P0` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), with the
> **metric definition table** that `CG-009` §3 requires of every `RP` file. All six sections retained
> in order; §4 is subdivided because a dictionary, an identifier standard and a reconciliation of 250
> identifiers do not fit one undifferentiated section.

---

## 1. Purpose

`P06` commits management to taking **100% of decisions on live data** rather than compiled
spreadsheets, and to cutting manual management reporting effort by **90%**. `06-02` sets 95 KPIs, 18
business objectives and a benefit case of **BDT 876 lac a year** at base case. `M62` `BRU-DAT-01`
states, as a hard rule, that *a business metric has exactly one definition and no consumer computes
its own variant*.

**None of those commitments can be met by a system. They are met by a document, and this is it.**

The failure mode is specific and it is already visible in the repository. Audit `00-07` H2-04 found
22 KPI identifiers used by more than one module. Enumeration for this file found something larger:
**250 distinct KPI identifiers in use against 95 registered**, because the register was exhausted and
module authors — correctly unwilling to leave a metric unnamed — allocated locally. §4.2 sets out the
full position.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| One definition per metric | `KPI-004` first-time fix rate is quoted by `M01`, `M02` and `M31`. Three teams improving three definitions produce three trends and one argument |
| An owned identifier space | 196 identifiers exist outside any register. A dashboard citing `KPI-207` cannot be traced to an owner, a formula or a target |
| Baselines | 44 of the 95 registered KPIs have no measured baseline, and `06-02` §6 states that a KPI without a baseline **cannot claim a benefit**. `RP-015` carries the remediation; this file carries the requirement |
| Grain and exclusions | "SLA compliance 96%" — of what population, over what period, excluding what? Two honest analysts produce different numbers from the same warehouse |
| Definitions on the view | `PRU-P06-07` requires a metric's definition, owner and source to be available **on the view**. There is nothing to display |

---

## 2. Scope

**In scope.** The metric definition schema; the `KPI-nnn` identifier standard and its allocation
rules; the reconciliation of the 250-identifier module space against the 95-identifier programme
register; definition rules; grain, inclusion, exclusion and null-handling conventions; the
restatement and versioning policy; ownership; and the dictionary itself.

**Out of scope — and the first boundary is the one that matters most.**

| Out of scope | Owned by | The boundary |
|---|---|---|
| **The metric registry as a system** — storage, version control, consumer notification, certification flags | **`M62`** (`BRU-DAT-01`…`05`) | `M62` specifies *the mechanism that holds one definition per metric*. **This file is the definitions.** The module repository says what the system must do; content says what must be written for it to work (Master Index §0) |
| Certified datasets, fields, joins, grain bindings, row-level security | `RP-006` | A metric is computed *from* a dataset. `RP-006` describes the dataset; this file describes the metric |
| Which report or dashboard shows a metric | `RP-002`, `RP-003`, `RP-004`, `RP-005` | A metric appears in many places and is defined once |
| How a metric is drawn | `RP-007` | Chart type, colour, axis and unit rendering |
| Baseline measurement and evidence | `RP-015` | This file states that every metric needs a baseline; `RP-015` establishes them and holds the evidence |
| Thresholds that raise an alert | `RP-012` | A target is a commitment; a threshold is an operational trigger. They are frequently different numbers |
| Data-quality measures on master data | `RP-016` | `RP-016` measures the *data*; this file measures the *business* |
| Terminology and the Bengali term for a metric | `CG-004`, `BN-003` | This file binds each metric to its approved term; it does not create terms |
| Content-effectiveness metrics | `CG-014` | A separate metric family with a separate owner, deliberately not merged |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **BI Lead** (accountable) | The authority for every metric in the semantic layer |
| **Enterprise Architecture** | The `KPI-nnn` identifier space and its allocation |
| **Module business owners** | The definition of the metric they are accountable for |
| **Executives and branch managers** | Knowing what a number on a dashboard means before acting on it |
| **BI analysts and engineers** | Implementing `M62` metric definitions without interpreting |
| **QA** (`TS-005`, `TS-012`, `TS-014`) | `SL-26` requires analytics outcomes recomputed independently — against this |
| **`RP-015`** | The list of metrics that require a baseline |
| **Localisation** | The Bengali name and definition of every metric a branch manager reads |

---

## 4. Content

### 4.1 The metric definition schema

**Every metric carries all eighteen fields. A metric missing any of them is not defined and may not
be published** (`KD-01`).

| # | Field | Content | Why it is mandatory |
|---:|---|---|---|
| 1 | `id` | `KPI-nnn`, allocated per §4.3 | Traceability |
| 2 | `name_en` | The approved English name, from `CG-004` | One name per metric |
| 3 | `name_bn` | The approved Bengali name, from `BN-003` | Branch managers read the dashboard in Bengali |
| 4 | `question` | The business question it answers, in one sentence | A metric nobody can state the purpose of is a metric nobody should act on |
| 5 | `formula` | The arithmetic, stated symbolically | Removes interpretation |
| 6 | `numerator` | Population and filter, precisely | The commonest source of divergence |
| 7 | `denominator` | Population and filter, precisely | The second commonest |
| 8 | `inclusions` | What deliberately counts | Makes a judgement explicit |
| 9 | `exclusions` | What deliberately does not | **The single most valuable field**; §4.5 |
| 10 | `grain` | The lowest level at which it is valid | `BRU-DAT-08`; prevents invalid aggregation |
| 11 | `unit` | %, count, BDT, days, hours, ratio, score | Prevents a rate being summed |
| 12 | `direction` | Higher is better / lower is better / target band | A league table cannot rank without it |
| 13 | `source` | The `RP-006` certified dataset and its fields | `PRU-P06-02` |
| 14 | `business_owner` | Named function accountable for the number | `BRU-DAT-09` |
| 15 | `technical_steward` | Named function accountable for the computation | `BRU-DAT-09` |
| 16 | `baseline` | Value, date and basis, or **`NOT MEASURED`** | `06-02` §6; `RP-015` |
| 17 | `targets` | W4 and W8 targets from `06-02`, and any interim | The commitment |
| 18 | `certification` | `Certified` · `Provisional` · `Deprecated` | `BRU-DAT-05` requires it displayed wherever the metric appears |

Two further fields are carried where they apply: `contributors` (modules that influence the metric
without owning it, §4.4) and `restated_from` (§4.7).

### 4.2 The identifier space — reconciled

This is the reconciliation the register created this file to perform. **Every figure below is
enumerated from the filesystem on 2026-08-20, not taken from what any document says about itself.**

| Position | Count |
|---|---:|
| Registered in `06-02` §2 (`KPI-001`…`KPI-095`) | **95** |
| Distinct `KPI-` identifiers used anywhere in the 79 module and portal specifications | **250** |
| Defined in a module `§15` KPI table row | 247 |
| **Used in a module but not registered in `06-02`** | **196** — a contiguous block `KPI-110`…`KPI-305` |
| **Registered in `06-02` but used by no module** | **41** |
| Both registered and module-used | 54 |
| Unallocated gap | `KPI-096`…`KPI-109` — **14 identifiers, used nowhere** |

#### Why 196 identifiers sit outside the register — and it is not author indiscipline

The Category E module audit already recorded the cause as its finding **A-02, High**: *"KPI register
exhausted. `06-02` §2.6 stops at KPI-049 and contains no identifiers"* for the modules written
afterwards. Faced with a metric that needed a name and a register with no room, module authors
allocated locally and said so. `M19` even carries a register note stating which of its identifiers
are *"the canonical identifiers allocated in `06-02`"*, distinguishing them from local ones.

**The defect is in the register, not in the modules.** `06-02` §2 stopped at 95 while the
architecture grew from 30 modules to 67. §4.3 fixes the space; `O-01` escalates the reconciliation.

#### The "22 collisions" re-diagnosed

`00-07` H2-04 lists 22 identifiers used by two or more modules, with `KPI-050` claimed by nine and
`KPI-004` and `KPI-049` by eight each. **Extraction of how each is actually used changes the
diagnosis materially.**

| Category | Count | What it is |
|---|---:|---|
| **Contribution references** | the large majority | A module citing a metric it *influences* but does not own — "supports `KPI-050` (close ≤ 3 days)", "contributes to the ≤ 3-day close". `KPI-050` is registered to `M19`; `M15`, `M49`, `M51` and `M29` reference it as contributors. **This is correct behaviour and the dictionary should record it, not prohibit it** |
| **Ownership annotations** | 8 of the 10 name variants | The same name with a parenthetical: *"(workshop contribution)"*, *"(M15 measures; M43 is the primary lever)"*, *"(instrumented here; see register note)"*, *"(jointly with M19)"*. These are measurement-ownership notes, not competing definitions |
| **Consistent restatement** | 3 identifiers | The same name, baseline and both targets restated identically in more than one module |
| **Genuine defects** | **2** | Below |

**The two genuine defects:**

| Identifier | Defect | Severity |
|---|---|---|
| **`KPI-018`** | `06-02` registers it as *"Logistics on-time collection/delivery"* — **one identifier for a combined metric**. `M03` splits it into **two separate rows, "On-time collection" and "On-time delivery"**, under the same identifier. One identifier, two metrics, in one module | **Must be split into two identifiers.** A combined figure hides which half is failing, and collection and delivery have different owners and different causes |
| **`KPI-013`** | `M02` calls it *"Automatic assignment rate"*; `M26` calls it *"Automatic dispatch assignment rate"*; `06-02` calls it *"Automatic assignment rate"* | Naming inconsistency only. **`06-02`'s name governs** (`KD-04`) |

> **This re-diagnosis is reported, not used to close H2-04.** H2-04's extraction was mechanically
> correct; its interpretation over-counted. The finding should be **restated** rather than closed,
> because the underlying problem it pointed at — an unowned identifier space — is real and larger
> than the finding described. `O-01`.

### 4.3 Identifier allocation standard

| # | Rule |
|---|---|
| **KD-02** | `KPI-nnn` is a **programme-wide** space, allocated **only in this file**. A module may not allocate a `KPI-nnn`; it requests one |
| **KD-03** | Identifiers are permanent and never reused. A retired metric is marked `Deprecated`, never recycled (`CP-02` applied to metrics) |
| **KD-04** | Where a module name and `06-02` disagree, **`06-02`'s name governs** until this dictionary supersedes it, and this dictionary then governs |
| **KD-05** | **One metric, one identifier.** An identifier covering two metrics is split, and both halves are new identifiers with the original marked `Deprecated` and cross-referenced |
| **KD-06** | A module citing a metric it does not own records itself as a **`contributor`**, not as a second definition (§4.4) |

**The allocated ranges.** The space is bounded so that a reader can tell from the number what kind of
metric it is, and so that exhaustion cannot recur silently.

| Range | Allocation | Status |
|---|---|---|
| `KPI-001` … `KPI-095` | **Programme KPIs** — the `06-02` register, board-visible, benefit-bearing | In force |
| `KPI-096` … `KPI-109` | **Reserved** for programme KPIs added by Steering decision | 14 free |
| `KPI-110` … `KPI-305` | **Module operational metrics**, already in use across the 67 modules — to be ratified into this dictionary in module order | **196 in use, unregistered — `O-01`** |
| `KPI-306` … `KPI-399` | **Reserved** for module metrics | 94 free |
| `KPI-400` … `KPI-449` | **External-audience metrics** (`RP-005`) | Free |
| `KPI-450` … `KPI-499` | **Data-quality metrics** (`RP-016`) | Free |
| `KPI-500` +| **Reserved**; allocation requires an Enterprise Architecture decision | Free |

**Content-effectiveness metrics keep their own space.** `CG-014` measures help deflection, training
pass rates and translation defect density. Those are not `KPI-nnn` and are not merged here — a
deliberate `CP-01` boundary, recorded so a later author does not fold them in and inflate the board
register.

### 4.4 Ownership — one owner, many contributors

`BRU-DAT-09` requires a named business owner **and** a named technical steward for every metric. This
file adds a third role that the module set already uses informally and that the dictionary formalises:

| Role | Accountable for | One per metric? |
|---|---|---|
| **Business owner** | The number being *right for the business*, and the target being met | **Yes** |
| **Technical steward** | The computation being *right against this definition* | **Yes** |
| **Contributor** | A module or function that materially influences the metric without owning it | **No — many** |

**Why contributors are recorded rather than prohibited.** `KPI-043` part availability is measured by
`M15` and is primarily driven by `M43` demand planning; `M15` says so in its own text. Prohibiting
the cross-reference would either hide the causal chain or force a duplicate metric. **Recording it
means improvement work can be aimed at the lever rather than the meter.**

### 4.5 Definition rules

| # | Rule |
|---|---|
| **KD-01** | **All eighteen schema fields, or the metric is not published** (§4.1) |
| **KD-07** | **A metric states its exclusions explicitly, and an empty exclusions field is a positive assertion** that nothing is excluded — not an omission |
| **KD-08** | Every metric declares its **grain**, and aggregation above the grain is defined or prohibited (`BRU-DAT-08`) |
| **KD-09** | **A rate is never summed and never averaged across unequal populations.** Re-aggregation recomputes the numerator and denominator |
| **KD-10** | **Null is not zero.** Every metric states whether a missing value is excluded from the denominator or counted as a failure. This single decision moves most operational percentages by several points |
| **KD-11** | Every metric states its **period basis** — calendar month, fiscal month (July–June year, `MD-041`), rolling 30 days, shift, wave — and its **timezone** is Asia/Dhaka on a UTC store (`AS-11`) |
| **KD-12** | A **currency** metric states its currency and, where multi-currency, the conversion rate basis (`MD-039`) |
| **KD-13** | A metric with a **statutory** definition takes it from the instrument, not from convenience, and cites it with a verification date (`CG-012`) |
| **KD-14** | A metric whose value depends on a `MD` code set names the code set and the version. **A metric defined on `MD-024` fault codes changes meaning when the taxonomy changes** |
| **KD-15** | **No metric is defined in a dashboard, a report or a query** (`PRU-P06-01`, `AUT-P06-08`). A dashboard containing an inline calculation is rejected at review |
| **KD-16** | Every metric is **decomposable to its constituent records** (`PRU-P06-08`). A metric that cannot be drilled cannot be trusted or disputed |
| **KD-17** | Every metric displays its **definition, owner, source and certification status** on the view (`PRU-P06-07`, `BRU-DAT-05`) |
| **KD-18** | A metric used in a **contractual or incentive** context — service credits (`DT-031`), technician incentive (`BRU-HRM-03`), seller score (`BRU-ECM-04`), commission — is flagged `contractual` and may not change without the contract owner's approval |
| **KD-19** | Every metric names the **`RP-006` certified dataset** it is computed from. A metric with no certified source is `Provisional` at best (`PRU-P06-02`) |
| **KD-20** | A metric with **no measured baseline** is published with its baseline field reading `NOT MEASURED` and **may not be used to claim a benefit** (`06-02` §6; `RP-015`) |
| **KD-21** | Bengali names and definitions are **authored by the Localisation Lead**, not translated by an analyst (`CG-010`; `BN-003`) |
| **KD-22** | A metric is `Certified` only when its definition, dataset, baseline, owner and steward are all in place. **Everything else is `Provisional` and labelled as such on every view** |
| **KD-23** | **Changing a definition is a restatement event** (§4.7), never a silent edit (`BRU-DAT-02`) |
| **KD-24** | Coverage of this dictionary is **counted and reported** — metrics defined ÷ metrics in use — with the enumeration date (`CP-11`) |

### 4.6 Worked definitions

Eight metrics are defined in full here as the pattern every other definition follows. They were
chosen because each one exposes a different definitional trap. The remaining metrics are carried in
the accompanying data file (§6).

---

**`KPI-004` — First-time fix rate**

| Field | Value |
|---|---|
| `name_en` / `name_bn` | First-time fix rate / *(Localisation Lead — `O-05`)* |
| `question` | What proportion of jobs were resolved on the first visit or first workshop pass, with no return? |
| `formula` | `jobs_fixed_first_attempt ÷ jobs_completed` |
| `numerator` | Completed service orders whose resolution was achieved without a second visit, a second workshop pass, or a reopen inside the repair-warranty period |
| `denominator` | Service orders reaching `Completed` in the period |
| `inclusions` | Paid, warranty, AMC and marketplace-delivered jobs |
| `exclusions` | Jobs cancelled before diagnosis; jobs held for customer-declined estimates; jobs where the part was unavailable **and the customer chose to wait** — *a parts-wait is not a fix failure* |
| `grain` | Service order |
| `unit` / `direction` | % / higher is better |
| `source` | `RP-006` `ds_service_order_fact` |
| `business_owner` / `technical_steward` | Operations Director (`R05`) / BI Lead |
| `baseline` | **70%**, measured, `06-02` §2.1 |
| `targets` | W4 82% · W8 88% |
| `contributors` | `M02` field execution · `M31` workshop execution · `M15` parts availability · `M22` certification currency |
| `certification` | `Provisional` until the exclusions are ratified by the Operations Director |

> **The trap.** `M01`, `M02` and `M31` all quote this metric, and `M31` annotates it *"(workshop
> contribution)"*. Without the exclusion list above, a workshop measuring itself on the same
> identifier will legitimately exclude field-only failure modes and report a higher number. **One
> definition, three contributors, one owner.**

---

**`KPI-018` → `KPI-096` and `KPI-097` — the split**

`06-02` registers `KPI-018` as *"Logistics on-time collection/delivery"*. `M03` uses it for two
distinct metrics. Under `KD-05` it is split:

| New | Name | Owner | Why separate |
|---|---|---|---|
| **`KPI-096`** | Logistics on-time **collection** | Logistics Coordinator (`R15`) | Collection failure is a scheduling and access problem |
| **`KPI-097`** | Logistics on-time **delivery** | Logistics Coordinator (`R15`) | Delivery failure is a routing and recipient-availability problem |
| `KPI-018` | *Deprecated* — retained, never reused (`KD-03`) | — | Cross-referenced to both halves |

The combined figure remains reportable as a derived measure, stated as such. `06-02` §2.2's target of
90% at W4 and 93% at W8 applies to **both halves independently** until the Operations Director sets
separate targets — recorded as an assumption, `O-03`.

---

**`KPI-050` — Month-end close cycle**

| Field | Value |
|---|---|
| `question` | How many working days after period end does the close complete? |
| `formula` | `close_completion_date − period_end_date`, in **working days** (`MD-041` holiday calendar) |
| `numerator` / `denominator` | n/a — a duration, not a ratio |
| `inclusions` | All entities and all business lines consolidated (`06-02` §5 criterion 3) |
| `exclusions` | Adjusting entries raised by external audit after close |
| `grain` | Fiscal period × entity |
| `unit` / `direction` | Working days / lower is better |
| `business_owner` / `technical_steward` | CFO (`R03`) / Finance Manager (`R26`) |
| `baseline` | **15–20 days** — *a range, not a measurement*; `RP-015` must resolve it (`TS-009` `O-07`) |
| `targets` | W4 5 days · W8 ≤ 3 days |
| `contributors` | `M15` inventory valuation · `M49` depreciation · `M50` bank reconciliation · `M51` tax positions · `M52` accruals |
| `certification` | `Provisional` — the baseline is a range |

> **The trap.** Nine module files reference `KPI-050`; **exactly one owns it.** The other eight are
> contributors, and `00-07` H2-04 counted them as collisions. The dictionary records all nine
> correctly and the ambiguity disappears.

---

**`KPI-006` — SLA compliance**

| Field | Value |
|---|---|
| `question` | What proportion of jobs met the SLA that applied to them? |
| `formula` | `jobs_within_sla ÷ jobs_with_an_sla` |
| `numerator` | Jobs whose measured elapsed time, **net of approved holds**, was within the `MD-028` target for their priority and service type |
| `denominator` | Jobs with an SLA assigned at creation |
| `inclusions` | All delivery modes; Privilege-uplifted SLAs at their uplifted target (`BRU-SRM-10`) |
| `exclusions` | Jobs on an approved hold for the duration of the hold only (`BRU-SRM-15`); jobs with no SLA assigned — **and the count of those is reported alongside, because an unassigned SLA is a defect, not an exemption** |
| `grain` | Service order |
| `unit` / `direction` | % / higher is better |
| `business_owner` | Operations Director (`R05`) |
| `baseline` | **`NOT MEASURED`** (`06-02` §2.1 reads "unmeasured") |
| `targets` | W4 92% · W8 96% |
| `certification` | **`Provisional` — no baseline** (`KD-20`); **may not claim a benefit** |
| `contractual` | **Yes** — service credits under `DT-031` derive from measured SLA breach (`BRU-CTR-08`). `KD-18` applies |

> **The trap.** The hold exclusion is worth several points, and it is also the most gameable rule in
> the dictionary: an SLA that can be paused by an unapproved hold reason is an SLA that always
> passes. `BRU-SRM-15` requires an approved hold reason; **the dictionary requires the count of holds
> to be published beside the compliance figure.**

---

**`KPI-016` — Technician app daily active usage**

| Field | Value |
|---|---|
| `question` | What proportion of technicians who were rostered on used the app that day? |
| `formula` | `distinct_technicians_with_a_state_changing_action ÷ technicians_rostered_on_shift` |
| `numerator` | Technicians who performed at least one state-changing action, **including actions performed offline and synced later** (`DI-04`) |
| `denominator` | Technicians rostered on shift that day (`MD-042`) |
| `exclusions` | Technicians on leave or off-shift |
| `grain` | Technician × day |
| `baseline` | 0% — measured, the app does not exist |
| `targets` | W4 92% · W8 **> 95%** |
| `business_owner` | Technical Director |
| `certification` | `Certified` |

> **The trap, and it is the most important one in this file.** A technician who opens the app, reads
> a job and works from a paper notebook counts as active if the numerator is "logged in". **The
> numerator is a state-changing action for that reason.** `TS-015` `N-09` records that the paper
> notebook is invisible to every measure the programme has; this definition is the closest the
> metric layer can get, and it is still not proof. Stated so the metric is not over-trusted.

---

**`KPI-037` — Claims submitted within 72 hours**

| Field | Value |
|---|---|
| `formula` | `claims_submitted_within_72h ÷ claims_eligible_for_submission` |
| `numerator` | Claims transmitted to the brand within 72 hours of the warranty work order closing |
| `denominator` | Claims auto-created under `BRU-WTY-02` from a closed warranty work order |
| `exclusions` | Claims blocked by incomplete evidence **for the period the block is open** — *and the blocked count is published beside it*, because `BRU-WTY-01` blocks are the actual cause of leakage |
| `grain` | Claim |
| `baseline` | **~50% at 30–90 days** — a qualitative baseline; `RP-015` must restate it |
| `targets` | W4 92% · W8 95% |
| `business_owner` | Finance Director |
| `certification` | `Provisional` |

---

**`KPI-092` — Bengali translation completeness**

| Field | Value |
|---|---|
| `formula` | `strings_translated_and_linguistically_signed_off ÷ user_facing_strings_in_scope` |
| `numerator` | Strings with an approved Bengali value **and** in-context linguistic sign-off (`BN-018`) |
| `denominator` | All user-facing strings in the release scope (`UI-001` key inventory) |
| `exclusions` | Developer-facing strings, log messages, internal admin labels |
| `grain` | String × release × portal |
| `baseline` | 0% |
| `targets` | **100%** — `AS-12` and `G1-08` admit no lower figure |
| `business_owner` | Localisation Lead |
| `certification` | `Provisional` — **`AUDIT-012` BN-01 records a counted 44% on the `common.*` namespace against a claimed completeness**, so the denominator is itself disputed |

> **The trap.** This metric is **registered in `06-02` and used by no module** — one of the 41.
> That is not an orphan: it is a **programme-measured** metric with no single owning module, and
> §4.8 declares that class rather than deleting it.

---

**`KPI-085` — System uptime (business hours)**

| Field | Value |
|---|---|
| `formula` | `available_minutes ÷ scheduled_minutes` within 09:00–22:00 BST |
| `exclusions` | Announced maintenance inside `NFR-049`'s permitted window; **degradation short of unavailability is reported separately** |
| `grain` | Service × day |
| `baseline` | ≥ 99.9% *(target restated as baseline in `06-02` §2.10 — see `O-04`)* |
| `targets` | ≥ 99.9% |
| `business_owner` | CTO |
| `certification` | `Provisional` |

> **The trap.** `06-02` §2.10 gives several platform KPIs a "target" and no baseline column, and
> `KPI-085`'s baseline reads as the target. **A metric whose baseline equals its target cannot show
> improvement and cannot fail**, which makes it unusable for benefit tracking. `O-04`.

### 4.7 Restatement and versioning

A definition change is a **restatement event**, because it changes history.

| # | Rule |
|---|---|
| **KD-25** | Every definition carries a version. A change increments it and records `restated_from` |
| **KD-26** | **Every registered consumer is notified before the change takes effect** (`BRU-DAT-03`) |
| **KD-27** | The change states whether history is **recomputed** on the new basis or **broken** at a stated date. Both are acceptable; silence is not |
| **KD-28** | A restated metric is **labelled on every view for one full reporting cycle** |
| **KD-29** | A metric cannot be retired while a registered consumer remains (`BRU-DAT-04`) |
| **KD-30** | A `contractual` metric (`KD-18`) requires the contract owner's approval before restatement, because service credits and incentives already paid were computed on the old basis |

### 4.8 Metrics with no owning module — a declared class

41 registered KPIs are used by no module specification. **They are not errors.** They divide into
three classes, declared here so a future reader does not delete them or invent owners:

| Class | Examples | Owner |
|---|---|---|
| **Programme-measured** — measured centrally, no single module computes them | `KPI-092` translation completeness, `KPI-094` manual reports remaining, `KPI-095` overall automation | Programme / PMO |
| **Portal-measured** — belong to a portal, not a module | `KPI-020` CSAT, `KPI-021` NPS, `KPI-022` online booking rate | Portal owner |
| **Cross-functional outcome** — the result of many modules with no single computation site | `KPI-030`…`KPI-036` commercial outcomes, `KPI-061`…`KPI-068` people and quality | The `06-02` §1 objective owner |

**Each of the 41 is assigned an owner in the data file.** A registered metric with no owner is the
condition that lets a board target go unmeasured for a year, and `06-02` §6 already prohibits it.

### 4.9 Coverage

`KD-24` requires coverage counted. The position on **2026-08-20**:

| Measure | Value |
|---|---|
| Metrics in use across the module and portal set | **250** |
| Metrics registered in `06-02` | 95 |
| **Metrics fully defined to the §4.1 eighteen-field schema** | **8** *(this file, §4.6)* |
| Metrics with a schema-complete definition in the data file | **0 — outstanding** |
| Metrics with a measured baseline | 51 of 95 registered; unknown for the 196 |
| Metrics that may claim a benefit today (`KD-20`) | **51 of 250 — 20%** |

**This file is a standard with eight worked examples, not a completed dictionary.** Stating that
plainly is `CP-11`; the authoring effort is `O-02`.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `06-02` §2 | The 95 registered KPIs, their baselines and targets |
| `06-02` §1, §6 | Objectives, and the rule that a KPI without a baseline claims no benefit |
| Module `§15` KPI blocks | The 247 module-defined metrics this file must ratify |
| `M62` §9 `BRU-DAT-01`…`12` | The registry mechanism, grain rule and owner/steward requirement |
| `P06` §9 `PRU-P06-01`, `-07`, `-08` | No metric defined in a dashboard; definition on the view; decomposable |
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | The certified dataset every metric must name (`KD-19`) |
| **[`RP-015`](RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md)** | Baselines and their evidence (`KD-20`) |
| `MD-028`, `MD-041`, `MD-039`, `MD-024` | SLA targets, calendar, currency, code sets (`KD-11`…`KD-14`) |
| `CG-004`, `BN-003` | Approved English and Bengali terms (`KD-21`) |
| `05-04` §5 | Which roles may see a metric computed on restricted fields |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly, and at every wave gate before the gate pack is written |
| Trigger for out-of-cycle review | A new metric request; a `MD` code-set change; a statutory change affecting `KD-13`; a restatement; a `06-02` target change; a contractual metric change |
| Owner | BI Lead, with Enterprise Architecture for the identifier space |
| Change control | Definition changes follow §4.7. Identifier-range changes require an Enterprise Architecture decision |
| Data files | `RP-001_KPI_Dictionary.csv` — the 250 metrics against the eighteen-field schema · `RP-001_Identifier_Allocation.csv` · `RP-001_Deprecated_and_Restated.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **196 module metrics sit outside any register and `00-07` H2-04 needs restating rather than closing.** The finding described 22 collisions; enumeration finds an exhausted register (`06-02` §2 stops at 95 while the architecture reached 67 modules) and 196 locally allocated identifiers, of which the Category E audit already reported the cause as its finding A-02. **Ratifying 196 definitions is the single largest piece of work in Category 14** | Enterprise Architecture with BI Lead | **W1 — before any dashboard cites a module metric** |
| **O-02** | **This file defines 8 of 250 metrics.** The remaining 242 need the eighteen-field schema completed with their business owners — an estimated 240–360 hours of owner time across eleven functions, and it appears in no plan. `06-01` §4 already names business availability as the binding constraint | BI Lead with Programme Manager | **W1 for the 95 registered; W2–W4 for the 196** |
| **O-03** | **`KPI-018` must be split into `KPI-096` and `KPI-097`** (`KD-05`, §4.6), and separate targets set. The `06-02` targets of 90%/93% are applied to both halves as an interim assumption, which is stated but not approved | Operations Director with BI Lead | **W1** |
| **O-04** | **Several `06-02` §2.10 platform KPIs have a baseline equal to their target** — `KPI-085` at ≥ 99.9%, `KPI-086` at < 400 ms, `KPI-087` at > 99.9%. **A metric whose baseline equals its target cannot show improvement**, which makes it unusable for the benefit tracking `06-02` §6 requires. Either the baselines are pre-programme measurements that happen to meet target, or the column is a transcription of the target | BI Lead with CTO | **W1 — with `RP-015`** |
| **O-05** | **No Bengali name or definition exists for any metric.** `KD-21` requires the Localisation Lead to author them and `CG-010` §3.2 makes this file bilingual because *"KPI names reach branch managers"*. 51+ branch managers read the league table (`RP-011`) in Bengali. Bengali authoring capacity is unresourced — `TS-002` `O-06`, `TR-001` `O-05`, `AUDIT-012` BN-01 | Localisation Lead | **W1 — before `RP-004` ships with `P03` at W1** |
| **O-06** | **44 of 95 registered KPIs have no measured baseline** and `06-02` §6 states they cannot claim a benefit. The benefit case is **BDT 876 lac a year** at base case. `RP-015` is `P1`/**W0** — already overdue against its own wave — and this file cannot certify a metric without it | Programme with Finance | **W0 — overdue** |
| **O-07** | **`M62`'s metric registry is a W8 platform capability in `06-01`, and this dictionary is needed at W1.** `BRU-DAT-01`…`05` describe version control, consumer notification and certification display; until they exist, this file is the registry, maintained as content, and `KD-17`'s on-view display has no mechanism | CTO with BI Lead | **W1 — interim mechanism needed** |
| **O-08** | **`KD-18` contractual metrics have no register.** Service credits (`DT-031`), technician incentive (`BRU-HRM-03`), seller performance (`BRU-ECM-04`) and commission all derive from metrics defined here, and `AUDIT-013` LG-01 already records that `DT-031` maps nine `MD-028` fields that do not exist. **A contractual metric computed on an undefined field is a liability, not a reporting defect** | Legal Counsel with CFO and BI Lead | **W3** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` with the `CG-009` metric-definition-table addition
- [x] **The `M62` boundary stated first: `M62` is the registry mechanism, this file is its content**
- [x] Eighteen-field definition schema specified, with the reason each field is mandatory
- [x] **The identifier space enumerated from the filesystem — 250 in use, 95 registered, 196 unregistered, 41 unused, 14 free**
- [x] **`00-07` H2-04's 22 collisions re-diagnosed: contribution references, ownership annotations, and exactly two genuine defects**
- [x] The cause of the 196 traced to the Category E audit's own finding A-02, so the register is blamed rather than the authors
- [x] Identifier ranges allocated with headroom, so exhaustion cannot recur silently
- [x] Owner / steward / contributor model defined, resolving the apparent collisions
- [x] Thirty rules stated, including null-is-not-zero, rates-are-not-summed and no-metric-defined-in-a-dashboard
- [x] Eight metrics defined in full, each chosen to expose a different definitional trap
- [x] `KPI-018` split proposed under `KD-05` with the deprecated identifier retained
- [x] The 41 unused registered metrics declared as three legitimate classes rather than deleted
- [x] Restatement policy covering recomputation, consumer notification and contractual metrics
- [x] **Coverage counted and stated honestly: 8 of 250 defined; 51 of 250 may claim a benefit**
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 242 remaining definitions authored — outstanding (`O-02`); this file is the standard and eight worked examples**
- [ ] **`O-01` 196 unregistered identifiers ratified — outstanding; the largest task in Category 14**
- [ ] **`O-06` 44 baselines absent — outstanding; blocks certification and every benefit claim**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding (`O-05`)**
- [ ] Named approvers recorded — **pending CTO and CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
