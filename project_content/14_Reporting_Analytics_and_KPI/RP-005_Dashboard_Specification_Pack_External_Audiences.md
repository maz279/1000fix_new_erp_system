---
id: RP-005
title: Dashboard Specification Pack — External Audiences
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead with Security
author: BI Lead with Security Lead, Account Management and Marketplace Operations
reviewers: [CTO, Chief Data Officer, Security Lead, CCO delegate, Account Manager representatives, Marketplace Operations Officer, Legal Counsel]
approver: CTO with Chief Data Officer
content_class: D
purpose: >
  The scoped analytics shown to corporate clients, brand partners, marketplace sellers and referral
  partners on their own portals — what each audience may see, at what grain, and what they must never
  see. Every other dashboard file in this category risks a wrong decision if it is wrong. This one
  risks a data breach: a seller who can see another seller's payout, or a corporate client who can
  read another client's estate, is a notifiable event under the Personal Data Protection Act 2026, not
  a reporting defect.
traces_to: [P04, P07, P08, P12, P06, 04-00, 05-04, 05-04 §8, 05-02 §10, 05-06 §6.3, M25, M62, M62 §9, RP-001, RP-002, RP-006, RP-007, RP-013, RP-014, TS-011, TS-017, LG-002, EO-001, UI-014, UI-017, UI-018, UI-022]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-14 — "No external party has P06 access; external analytics are served by P04, P07 and P08"; PRU-P06-03 row-level security derived from M29 applied to every dataset and tested as a security control; PRU-P06-04 column-level restrictions enforced by exclusion from the dataset, not by hiding in a view; PRU-P06-16 an embedded panel carries the host session's identity and scope
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §8 External Party Access Rules EA-01…EA-12; §1.7 R36 250,000+/month, R37 500–2,000, R38 1,000–3,000
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M62_Data_Platform_Warehouse_and_Governance.md §9 BRU-DAT-11 (S3-classified personal data excluded from the analytical estate by default; inclusion requires named, approved, time-limited authorisation), BRU-DAT-12 (analytical row-level security mirrors the user's ERP scope and is enforced in the query engine, not the presentation tool)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P04 Reporting "scoped analytics on their own estate — volume, cost, downtime, TAT, top-failing assets — with export"; P07 Performance own scorecard; P08 Performance "1000FiX service performance on their brand — volume, TAT, first-time fix, rework, CSAT, failure patterns by model"; P12 Performance leads, conversion, revenue attributed, ranking
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Dashboard Specification Pack — External Audiences

| Item | Value |
|---|---|
| Portals | `P04` Corporate · `P07` Marketplace Seller · `P08` Brand Partner · `P12` Partner & Referral |
| Populations | 500–2,000 corporate users · 500–2,000 sellers · 17+ brands · 100–500 partners |
| **`P06` access** | **None** — `PRU-P06-14` |
| Views specified | **11** across four portals (§4.3) |
| Enforcement layer | **Query engine**, not the presentation tool — `BRU-DAT-12` |
| Wave | W4 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` metric-table addition applied per view in §4.3. All six sections retained in order.

---

## 1. Purpose

`04-00` promises each external audience a view of their own performance: a corporate client sees their
estate, a brand sees 1000FiX's performance on their brand, a seller sees their scorecard, a partner
sees their conversions. Each of those is a competitive-sensitivity boundary as much as a permission
boundary, and **17+ brand partners are frequently competitors with each other.**

The register states the consequence precisely: *"scope errors here are data breaches, not reporting
defects."* Since the Personal Data Protection Act 2026 came into force, that is literal — `NFR-094`
requires notification of the National Data Management Authority for a breach likely to cause
significant damage, with exposure to **BDT 50 lakh** registered as risk `RSK-032`.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| A specified view per audience | Each portal team designs analytics from what the API returns, and the API returns more than the audience may see |
| An explicit denial list | Scope is defined by what was remembered, not by what was decided. §4.4 is the more important half of this file |
| Enforcement-layer discipline | `BRU-DAT-12` requires row-level security in the query engine. A filter applied in the presentation tool is bypassed by an export, a bookmark or an API call |
| Aggregation floors | A brand with a single-unit model in one district can identify the customer from a "top-failing assets" chart. **Scoping alone does not prevent re-identification** |
| Competitive isolation | Brand A must not infer Brand B's volumes from a market-share denominator |

---

## 2. Scope

**In scope.** The eleven external analytic views across `P04`, `P07`, `P08` and `P12`: metric
selection, grain, aggregation floors, the explicit denial list, enforcement rules, export limits, and
the isolation rules between audiences.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Metric definitions | `RP-001` — external metrics use the `KPI-400`…`KPI-449` range (`RP-001` §4.3) |
| Certified datasets and their RLS bindings | **`RP-006`** — this file states the scope rule; `RP-006` binds it to a dataset |
| Chart rendering | `RP-007` |
| Internal dashboards | `RP-003`, `RP-004` |
| Export marking and watermarking | **`RP-014`** |
| Scheduled delivery to external parties | `RP-013` |
| Portal labels and microcopy | `UI-014`, `UI-017`, `UI-018`, `UI-022` |
| The systematic proof that scope holds | **`TS-017`** — Block E derives `EA-01`…`EA-12` cases; this file supplies the design those cases test |
| Experiential proof by real external users | `TS-011` `UA-39` |
| Terms governing what a party may do with data | `LG-002` and the four external agreements |
| Onboarding into the portal | `EO-001` and the ecosystem kits |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **BI Lead** (accountable with Security) | The build specification |
| **Security Lead and Chief Data Officer** | The scope and re-identification controls |
| **Account Management** | What a corporate client is entitled to see |
| **Marketplace Operations** | What a seller sees of themselves and of the market |
| **Brand partner managers** | What each of 17+ brands sees, and what they cannot infer |
| **QA** (`TS-011`, `TS-017`) | The design the scope tests are written against |
| **Legal Counsel** | The disclosure boundary each agreement must support |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **ED-01** | **No external party has `P06` access** (`PRU-P06-14`). External analytics are served inside `P04`, `P07`, `P08` and `P12` |
| **ED-02** | **Row-level security is enforced in the query engine, never in the presentation tool** (`BRU-DAT-12`, `PRU-P06-03`). A filter that a URL parameter, a bookmark, an export or an API call can bypass is not a control |
| **ED-03** | **Column-level restriction is enforced by exclusion from the dataset**, never by hiding in a view (`PRU-P06-04`). The field is absent from the payload |
| **ED-04** | **An external party sees only records where they are a named party** (`EA-01`), and **never** cost, margin, internal notes or another party's data (`EA-02`) |
| **ED-05** | **Every view carries an explicit denial list** (§4.4). A view specified only by what it shows is a view whose boundary was never decided |
| **ED-06** | **Aggregation floor: no external view displays a figure derived from fewer than five underlying records** where a smaller count could identify a customer, a technician or a competitor's transaction. Below the floor the cell reads *"too few to report"* |
| **ED-07** | **No market-share, peer-average or ranked-against-others measure** is shown to any external party, in any form, unless the comparator set is at least ten parties and the party cannot deduce a member. A brand must not infer another brand's volume from a denominator |
| **ED-08** | **No `S3` field reaches the analytical estate** (`BRU-DAT-11`, `05-02` §10); `S2` fields appear only where the audience is the data subject or its named controller |
| **ED-09** | **Seller access to customer data expires** the defined period after job completion (`BRU-ECM-05`, `EA-04`), and **the analytic view expires with it** — a historical chart is not an exemption |
| **ED-10** | **Every external export is logged** with user, view, row count and timestamp (`PRU-P06-11`), and above the configured row threshold requires justification (`AUT-P06-07`, `EA-12`) |
| **ED-11** | **MFA is required for any external analytic view carrying financial detail** (`EA-09`) |
| **ED-12** | **Every metric on an external view carries the same definition as its internal counterpart** (`RP-001`). A separately defined "client-facing TAT" is how two numbers for one reality come to exist |
| **ED-13** | Every view states its **freshness** (`PRU-P06-06`); an external party acting on stale data will attribute the staleness to us |
| **ED-14** | **Drill never widens access** (`PRU-P06-09`), and an external drill terminates at the party's own record — never at a system-wide list |
| **ED-15** | Every view is specified for the **audience's own language**: `P07` sellers and `P12` partners are Bengali-first populations, `P04` and `P08` are English (§4.6) |

### 4.2 The four audiences and their isolation model

| Audience | Portal | `05-04` role | Sees | Isolation risk |
|---|---|---|---|---|
| **Corporate client** | `P04` | `R37` | Their own asset estate and service history | Another client's estate; their own users' cross-department data (`EA-03`) |
| **Marketplace seller** | `P07` | `R38` | Their own jobs, earnings, scorecard | Another seller's earnings or rating; **customer data past expiry** (`ED-09`) |
| **Brand partner** | `P08` | `R38` | 1000FiX performance on **their** brand | **Another brand's volumes, failure rates or claim outcomes — including by inference** |
| **Referral partner** | `P12` | `R38` | Their own leads, conversions, commission | Another partner's pipeline; the customer's identity beyond what conversion requires |

> **`05-04` §1.7 collapses vendor, seller, brand, courier, referral and recycling partners into a
> single `R38`.** That is a real problem for this file: the permission engine cannot express "a brand
> sees brand data" and "a seller sees seller data" as one role's rules. `TS-011` `O-06` and `TS-017`
> `O-03` both record it; here it means **the scope rules in §4.3 cannot be implemented as role rules
> and must be dataset-level policies** (`ED-02`). `O-01`.

### 4.3 The eleven views

---

#### `P04` Corporate — four views, `R37`, 500–2,000 users

| View | Question | Grain | Key metrics |
|---|---|---|---|
| **X1 Estate performance** | *How is my estate performing?* | Asset, site, department, month | Volume, TAT, downtime, first-time fix, top-failing assets |
| **X2 Service and SLA** | *Are you meeting the SLA I pay for?* | Request; month | SLA attainment, breaches, **service credits earned** (`BRU-CTR-08`) |
| **X3 Cost and consumption** | *What am I spending, and against what entitlement?* | Site, department, cost centre, month | Spend, entitlement consumed and remaining, out-of-scope billed |
| **X4 Compliance evidence** | *Can I prove disposal and destruction happened?* | Asset, certificate | Destruction certificates (`DT-034`), disposal certificates (`DT-035`) |

**Scope.** Own company only (`EA-03`), further scoped by the user's role **within** that company —
a requester sees their own site, a finance user sees all sites' billing, an admin sees all. **The
within-company scoping is the part most likely to be missed**, because "own company" feels like a
complete answer.

**`X2` carries contractual consequence.** Service credits derive from measured SLA breach, and
`AUDIT-013` LG-01 records that `DT-031` maps nine `MD-028` fields that do not exist. **A credit figure
shown to a client on a view they can export is a commitment** — `RP-001` `KD-18` flags the metric as
contractual, and `O-04` records the dependency.

---

#### `P07` Marketplace Seller — three views, `R38`, 500–2,000 sellers, **Bengali**

| View | Question | Grain | Key metrics |
|---|---|---|---|
| **X5 My performance** | *How am I doing, and what happens if I keep doing it?* | Job, month | Acceptance rate, on-time rate, rating breakdown, rework, disputes — **with the threshold consequences stated** (`BRU-ECM-04`) |
| **X6 My earnings** | *What have I earned, and what is held?* | Job, payout run | Earnings, commission and fees, held amounts **with the reason**, payout history |
| **X7 My market opportunity** | *What work is available to me?* | Category, area | Broadcast volume **in my categories and areas only** — no seller-level comparison |

**`X5` is the highest-consequence external view in the pack.** `BRU-ECM-04` reduces visibility
automatically below a threshold and suspends below a lower one. **A seller whose livelihood depends on
a score must be able to see the score, its components and the threshold** — otherwise the automated
consequence is unexplainable, and `AUDIT-013`'s work on the seller agreement makes that a contractual
exposure as well as a fairness one.

**`X7` is where `ED-07` bites hardest.** "What work is available" is legitimate; "how many other
sellers bid" is a market-structure disclosure. The view shows volume in the seller's own categories
and **no count of competitors**.

---

#### `P08` Brand Partner — three views, `R38`, 17+ organisations, English

| View | Question | Grain | Key metrics |
|---|---|---|---|
| **X8 Service performance on my brand** | *How well is 1000FiX servicing my products?* | Model, month, region | Volume, TAT, first-time fix, rework, CSAT — **their brand only** (`EA-05`) |
| **X9 Failure patterns** | *Which of my models are failing, and how?* | Model, fault code (`MD-024`), month | Failure rate by model, fault distribution, repeat-fault rate |
| **X10 Claims and reconciliation** | *What have I approved, paid and disputed?* | Claim, remittance, month | Claim volume, approval rate, decision time, reimbursement ageing, unmatched remittances |

**`X9` is the re-identification risk in this pack.** A brand with low volumes in one district can
reach a single customer through model × fault × region × month. **`ED-06`'s five-record floor is
mandatory on `X9`**, and region is the coarsest available geography — `MD-006` division, never
upazila.

**`ED-07` applies absolutely on `P08`.** A brand may not see its failure rate expressed against an
all-brand average, because with 17+ brands and known market shares the average is close to
invertible. **Their own trend over time is the only comparator offered.**

---

#### `P12` Referral Partner — one view, `R38`, 100–500 partners

| View | Question | Grain | Key metrics |
|---|---|---|---|
| **X11 My referrals and commission** | *What have I referred, what converted, what am I owed?* | Lead, conversion, statement period | Leads submitted, conversion rate, revenue attributed, commission earned and paid, ranking **band** only |

**Ranking is shown as a band, not a position.** `04-00` `P12` lists "ranking" as a capability;
`ED-07` prohibits a ranked-against-others measure below ten parties, and a numeric position in a
100–500 partner set discloses more than it motivates. **A band — top quartile, second quartile —
carries the incentive without the disclosure.** Recorded as a deliberate narrowing of the `04-00`
capability, `O-05`.

### 4.4 The denial list — what no external view shows

`ED-05` requires this to be explicit. It applies to all eleven views.

| Never shown to any external party | Why |
|---|---|
| **Cost, unit cost, margin** on anything | `EA-02`; `05-04` §5 restricts these fields to eleven internal roles |
| **Internal notes** | `EA-02`; `05-04` §5 — *"never exposed to any external portal"* |
| **Another party's records, in any aggregate** | `EA-01`, `ED-07` |
| **Peer averages, market share, competitor counts** | `ED-07` — inferable |
| **Named technicians** | A brand or client naming a technician creates a labour-relations exposure and adds nothing to their decision |
| **Named customers**, except where the external party is the customer's own controller (`P04` for its own employees' requests) | `05-02` §10 `S2`; PDPA minimisation |
| **Any `S3` field** | `BRU-DAT-11`, `ED-08` |
| **Other portals' data** — a seller does not see vendor data | `EA-01`; and `R38` collapsing makes this the rule the engine must enforce (`O-01`) |
| **Our own internal KPIs** — `KPI-004` network first-time fix, `KPI-050` close cycle | Not the party's data; commercially sensitive |
| **Customer contact details past the seller expiry period** | `BRU-ECM-05`, `EA-04`, `ED-09` |
| **Forward-looking internal forecasts** | A forecast shown externally becomes a commitment |
| **Cells below the five-record floor** | `ED-06` — replaced with *"too few to report"* |

### 4.5 Enforcement — where each control lives

| Control | Layer | Verified in |
|---|---|---|
| Row-level scope | **Query engine** (`BRU-DAT-12`) | `TS-017` Block A, E; `TS-011` `UA-39` |
| Column exclusion | **Dataset definition** (`PRU-P06-04`, `ED-03`) | `TS-017` Block C |
| Aggregation floor | **Dataset or metric definition** — not the chart | `TS-017`; `O-03` records that no test currently covers it |
| Comparator prohibition | **Metric definition** (`RP-001`) | `RP-006` dataset design |
| Export logging and threshold | Platform (`PRU-P06-11`, `AUT-P06-07`) | `TS-017` Block E `EA-12` |
| Seller data expiry | `M12` business rule (`BRU-ECM-05`) | `TS-007` `UAT-R38-P07-007` |
| MFA on financial views | `M29` (`EA-09`) | `TS-017` Block E |
| Freshness display | `P06`/portal (`PRU-P06-06`) | `TS-011` |

**Nothing in this table is enforced by the dashboard.** That is the point of `ED-02` and `ED-03`, and
it is why this file is owned jointly by BI and Security.

### 4.6 Language

| Portal | Audience language | Basis |
|---|---|---|
| `P07` Seller | **Bengali-first** | 500–2,000 Bangladeshi engineers and shops; `PS-03`; `TS-011` executes the seller block in Bengali |
| `P12` Partner | **Bengali or English** | Mixed population |
| `P04` Corporate | English | Corporate and government staff; `CG-010` §3.3 — *"contractual and technical documents English"* |
| `P08` Brand | English | 17+ partner organisations contracting in English |

**This file is English-only** (`CG-010` §3.2 allocates 5 bilingual `RP` files and this is not one).
The Bengali obligation for `P07` and `P12` view labels sits in `UI-017` and `UI-022`, and the metric
names in `RP-001` `name_bn`. Recorded so the obligation is not lost by being out of scope here.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | Every scope rule here is implemented as a dataset RLS binding (`ED-02`) |
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | Metric definitions, the `KPI-400`–`449` external range, and `KD-18` contractual flags |
| [`RP-007`](RP-007_Chart_Label_and_Visualisation_Standard.md) | Rendering, and the *"too few to report"* treatment of a floored cell |
| [`RP-014`](RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) | Marking on every external export (`ED-10`) |
| [`RP-013`](RP-013_Scheduled_Report_and_Subscription_Catalogue.md) | Scheduled delivery under per-recipient scope (`PRU-P06-10`) |
| `05-04` §8 `EA-01`…`EA-12` | The external access rules this file designs to |
| `05-02` §10 | `S0`–`S3` classification (`ED-08`) |
| `M62` §9 `BRU-DAT-11`, `BRU-DAT-12` | Exclusion of `S3`, and query-engine enforcement |
| `P06` §9 `PRU-P06-03`, `-04`, `-09`, `-11`, `-14`, `-16` | The governing portal rules |
| `TS-011`, `TS-017` | Where the scope is proved, experientially and systematically |
| `LG-002` and the four external agreements | The disclosure each audience has agreed to |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave; and on any change to an external agreement |
| Trigger for out-of-cycle review | A new external audience; a new metric on an external view; a change to `EA-*`; a re-identification concern raised; an aggregation-floor breach found |
| Owner | BI Lead with Security Lead; Chief Data Officer approves |
| Data file | `RP-005_External_View_Scope.csv` — 11 views × metric × scope rule × denial list |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`05-04` §1.7 collapses six external audiences into `R38`**, so a brand, a seller, a vendor and a partner share one role. `EA-04`, `EA-05`, `EA-06` and `EA-07` are audience-specific rules on a single role, which the permission engine cannot express as role rules. **The scope rules in §4.3 must therefore be dataset-level policies, and that design decision has not been taken.** `TS-011` `O-06` and `TS-017` `O-03` record the same gap | Enterprise Architecture with `M29` owner | **W4 — before `RP-006` binds the datasets** |
| **O-02** | **`ED-07`'s comparator prohibition narrows two `04-00` capabilities.** `P08` lists brand performance without stating a comparator, and `P12` lists "ranking". This file offers own-trend-only and a quartile band. **Both are deliberate reductions of a published capability** and need the CCO's agreement, because brands and partners may have been told otherwise | CCO delegate with Chief Data Officer | **W4** |
| **O-03** | **No test covers the aggregation floor.** `ED-06` is the only control against re-identification on `X9`, and `TS-017`'s derivation covers roles, tiers, fields and `EA-*` rules — **not statistical disclosure.** A view that passes every scope test can still identify a customer through model × fault × region × month | Security Lead with QA Lead | **W4 — a `TS-017` block addition is needed** |
| **O-04** | **`X2` shows service credits and `AUDIT-013` LG-01 records that `DT-031` maps nine non-existent `MD-028` fields.** A credit figure a client can export is a commitment computed on an undefined field. `RP-001` `O-08` records the contractual-metric register gap | Legal Counsel with CFO | **W4 — blocked by LG-01** |
| **O-05** | **`P12` `X11` ranking is shown as a band, not a position** (§4.3), which is this file's decision rather than an agreed one. `04-00` `P12` lists "ranking" as a capability and `KPI` targets 200+ active referral partners | CCO delegate | W4 |
| **O-06** | **The four external agreements do not exist** — seller, vendor, brand and partner. `TS-011` `O-05` records it. **A view showing a party their own performance data is a disclosure the agreement should authorise**, and Category 10 holds none of the four | Legal Counsel | **W4 for `P08`; W7 for `P07` and `P12`** |
| **O-07** | **`ED-09` requires the analytic view to expire with the seller's data access, and no mechanism is specified.** `BRU-ECM-05` expires access to customer contact data; whether a completed job's analytics also expire — and what a seller's historical earnings view shows after expiry — is undecided | Marketplace Operations with Chief Data Officer | W7 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` metric-table addition applied per view
- [x] **`PRU-P06-14` stated first — no external party has `P06` access**
- [x] Fifteen rules stated, led by query-engine enforcement and dataset-level column exclusion
- [x] Eleven views specified across four portals with question, grain and metrics
- [x] **An explicit denial list covering all eleven views — the more important half of the file (`ED-05`)**
- [x] **An aggregation floor and a comparator prohibition specified, because scoping alone does not prevent re-identification or competitive inference**
- [x] The `R38` collapse identified as making role-level enforcement impossible, with the dataset-policy consequence stated
- [x] Enforcement table placing every control in a layer, and none of them in the dashboard
- [x] Two deliberate narrowings of published `04-00` capabilities flagged for CCO agreement rather than made silently
- [x] Language position stated for all four audiences, with the Bengali obligation located in `UI-017`/`UI-022`
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `R38` collapse — outstanding; blocks dataset binding**
- [ ] **`O-03` no test covers statistical disclosure — outstanding; `ED-06` is unverified**
- [ ] **`O-06` four external agreements absent — outstanding**
- [ ] Named approvers recorded — **pending CTO and Chief Data Officer**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
