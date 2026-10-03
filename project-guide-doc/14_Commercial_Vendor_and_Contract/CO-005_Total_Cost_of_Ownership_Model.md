---
id: CO-005
title: Total Cost of Ownership Model
category: 14 — Commercial, Vendor & Contract
code: CO
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Financial Officer
approver: Board of Directors, on the recommendation of the ERP Steering Committee
standards_basis: >
  ISO 15686-5:2017 (life-cycle costing — whole-life cost method, applied to a software asset) ·
  AACE International Recommended Practice 17R-97 (cost estimate classification, classes 1–5) ·
  ISO 21502:2020 §7.9 (cost management) · PMBOK 7 (Delivery and Measurement performance domains) ·
  ISO/IEC 19770-1:2017 (IT asset management systems — the entitlement and consumption view) ·
  ISO/IEC 5230:2020 (OpenChain — the licence obligations that carry a cost) ·
  Bangladesh VAT and Supplementary Duty Act 2012 · Income Tax Act 2023 as amended by the
  Finance Act 2026
traces_to: >
  PGD-000 CO-005 · GV-008-D-03 (this document is named as the successor that must re-derive the
  non-people lines) · GV-008 Q-03 (what BD-R costs) · GV-007 §7.3 ("CO-005 must state that the TCO
  is bounded below, not bounded") · 00-06 §4 H-02 · AUDIT-001 AF-08, AF-09 · 00-07 H2-08 ·
  PGD-A1-05 · PGD-A2-09 · PGD-A2-10 · PE-002-F-04 · PE-006-F-07 · PE-006 §8.2 · PE-001 §3.4 ·
  CH-002 §7.2 TPD-14 · RFP §16.1, §16.2, §20.3.1 · D-014
depends_on: GV-007 · GV-008 · GV-004 · GV-009 · PE-001 · PE-002 · PE-006 · PE-007 · AR-013 · BE-007 · CH-002 · SC-007
verified_on: 2026-08-19
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-19 10:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CO-005 — Total Cost of Ownership Model

### Category 14 · Code `CO` · ISO 15686-5:2017 life-cycle costing · AACE 17R-97 · ISO 21502:2020 §7.9 · ISO/IEC 19770-1:2017

---

> **Local rule prefix: `TCO-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 10:05 (+06), by
> `grep -rho "TCO-[0-9]\{1,3\}" --include=*.md .` across all six repositories.
>
> **⚠ The category code `CO` is already a rule prefix elsewhere in the estate, in three unrelated
> namespaces.** `CO-01`…`CO-06` are **cost controls** in `PE-006` §8.4; `CO-01`…`CO-12` are
> **content-operating-model rules** in `project_content/00_Content_Governance_and_Standards/CG-002`,
> cited by name from at least fourteen further content files and from `GV-011` `CM-16`; and
> `CO-01`…`CO-03` are **callback-ordering rules** in `IN-006`. Enumerated at 2026-08-19 10:05 (+06):
> **30 files, 3 repositories, 108 occurrences of the two-digit form.**
>
> `CO-001`…`CO-006` — this category's document identifiers — therefore collide **by digit count**
> with all three, exactly as `MG-nn`/`MG-nnn` did in Category 09 (`MGA-04`), `CH-nn`/`CH-nnn` in
> Category 13 (`CHA-02`), and `MIG-nn`/`MIG-nnn` before both. **No document in this category uses
> `CO-nn` as a local rule prefix**, and every prefix allocated across Category 14 was verified to
> return zero workspace-wide occurrences first. Recorded as finding **`CVA-01`**.

---

## 1. Purpose

**This document exists because another document said it must.**

`GV-008` §4.3 restated the programme's cost position and carried its five non-people lines forward
from `02-05` §8 and `06-02` §3.3 **unchanged**, attaching four caveats and this ruling:

> *"All four caveats point the same way. Every non-people line was sized against `SB-2` — 30
> modules, single region, 18-month v1.0 horizon. None has been re-derived for 67 modules, split
> residency, 12 portals and 36 months. **The non-people subtotal is understated by an unknown
> amount**, and `PE-006` (capacity plan) and `CO-005` (TCO) must re-derive it."*

`GV-008-D-03` recorded why it did not do the re-derivation itself: *"Re-deriving infrastructure
requires `PE-001`–`PE-006`, none of which exists. Inventing a figure would be worse."*

**`PE-001` through `PE-008` were issued on 2026-08-19.** The precondition `GV-008-D-03` named has
been satisfied and the deferral it granted has expired. This document performs the re-derivation.

It does three further things that no document in the estate does:

| # | What | Why nobody has done it |
|:--:|---|---|
| 1 | Extends the horizon from **three years to five** | RFP §16.2.10 requires respondents to state a Year 4 and Year 5 run rate. **The Company has never computed its own.** Every internal figure stops at Year 3, which is the month the programme ends and the year the system starts costing money without a project to charge it to |
| 2 | Adds the **tax, FX and escalation** lines | Every cost figure in the estate is a pre-tax, single-point-FX, un-escalated 2026 number applied to spend that occurs between May 2027 and May 2030 |
| 3 | Adds the **internal resource cost** | `CH-002` §7.2 states it plainly: *"a training plan that shows only trainer cost understates the true figure by an order of magnitude"* — and names this document as one that *"does not contain it either"*. It does now |

> **The single most important sentence in this document.** The 1000FiX RFP was issued to the market
> on **13 August 2026** carrying a published budget envelope of **USD 690,000 – 1,150,000** (§16.1)
> and instructing respondents to perform *"an independent capacity analysis against 1,513 PW"*
> (§17.2 criterion 7). **Five days later `GV-007` superseded 1,513 PW with 3,022 PW, and six days
> later `GV-008` superseded the envelope with $1,024K–$2,608K.** Bids are due **30 October 2026**
> and the written-question deadline is **17 September 2026**. Every proposal now in preparation is
> being priced against a figure the Company's own budget baseline disowns. **This document's most
> urgent output is not a number; it is the recommendation at §9.4 that an RFP addendum be issued
> before 17 September 2026.**

### 1.1 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | The **whole-life cost** of the ERP and portal estate over five years from programme kickoff, per ISO 15686-5:2017 §5 |
| 2 | **Re-derivation** of the five non-people lines `GV-008` §4.3 carried with caveats, using `PE-001`, `PE-002`, `PE-006` and `PE-007` |
| 3 | The **three infrastructure lines** absent from every published progression: `BD-R`, `dr`, and the non-production environment estate |
| 4 | **Bangladesh VAT and withholding-tax** treatment of the implementation contract, and the cash consequence of each |
| 5 | **Foreign-exchange** basis, verified, and the effect of the verified rate on the return position |
| 6 | **Rate escalation** across a 36-month programme and a 24-month run-out |
| 7 | **Hypercare** across nine waves, and **programme management and assurance** — the two lines `GV-007` §7.3 and `GV-008-D-02` respectively excluded and declared |
| 8 | The **internal resource cost**: learner time, OJT supervisor time, super-user commitment, business-owner commitment, champion released time |
| 9 | **Two tiers** — incremental cash cost, and full economic cost — separately, because they answer different questions |
| 10 | **Unit economics** — cost per service order — and the cost controls that follow from them |
| 11 | Reconciliation against **every** cost figure the estate carries, including the live RFP envelope |
| 12 | The **restated return position** at the verified FX rate |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The **authorised budget** — tranches, drawdown, contingency, management reserve, risk budget | `GV-008` §5, §6 | A budget authorises spend against a governance structure; a TCO measures cost. Putting contingency inside a TCO double-counts it the moment `GV-008` also carries it |
| The **effort** figures the people lines rest on | `GV-007` §7.1 | This document applies rates to `GV-007`'s counted effort. It does not re-estimate effort, and where it disagrees it says so rather than re-deriving |
| **Benefits, NPV, IRR and the business case** | `BM-003` | §10 restates payback because FX moves it. The full financial case, discount rate and sensitivity analysis are `BM-003`'s, and `PGD-A2-10` is `BM-003`'s to resolve |
| **KPI baselines** that make a benefit claimable | `BM-002` | §10.1 uses `GV-008` §7.1's claimable/claimed split; it does not measure baselines |
| The **evaluation** of bid prices against this model | `CO-002` §7 | This model is the yardstick; applying it to bids is the evaluation record |
| **Contract price, payment milestones, retention and remedies** | `CO-003` | This document sizes the cost; `CO-003` makes it enforceable |
| **Procurement** of infrastructure, devices and L6 components | `CO-006` | Including learner devices, which `CH-002` §7.1 assigns to `CO-006` |
| **Open-source licence obligations** and their owners | `CO-004` | §5.5 costs the L6 commercial set; the obligations that cost nothing in cash but carry legal exposure are `CO-004`'s |
| Infrastructure **sizing** and capacity derivation | `PE-006` | This document prices `PE-006`'s shapes. Where `PE-006` gives a shape and no number, §5 supplies the number and labels its class |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Board of Directors** | The decision `D-014` requires. §9.1's reconciliation and §11's options are written for this reader |
| **Chief Financial Officer** | The owner. §5, §6 and §7 are the working; §12's rules are the control framework |
| ERP Steering Committee | §9.4's addendum recommendation, which is time-critical and theirs to instruct |
| Head of Procurement | §5.5 and §6's tax treatment shape the contract structure and the bid-evaluation basis |
| Legal Counsel | §6.1 and §6.2 — the VAT and withholding positions both need an opinion, not an assumption |
| Implementation partner *(post-award)* | §12's cost controls and §13's unit economics become contractual reporting obligations under `CO-003` |
| Internal audit / Audit Committee | The arithmetic is regenerated in place at every table, per `PG-M10`, so it can be re-performed |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 15686-5:2017** | §5 (whole-life and life-cycle cost), §6 (analysis period), Annex A | The five-year analysis period is stated and justified (§3.3); acquisition, operation, maintenance and end-of-life are the cost categories; costs are separated into **incremental cash** and **internal resource** tiers | ISO 15686-5 is written for constructed assets. **Departure:** *residual value* is treated as zero (§3.2) and *disposal* is replaced by **decommissioning and exit** (§7.4). Both are stated because the standard's asset model does not transfer cleanly to software |
| **AACE 17R-97** | Estimate classes 1–5 and their expected accuracy ranges | Every line in §7 carries an estimate class. The document's class is the class of its worst input, per `GV-007` `EM-05` | None. `GV-007` already adopted this classification; this document inherits it rather than introducing a second scheme |
| **ISO 21502:2020** | §7.9 cost management | Cost is planned, estimated with a stated method, and controlled by named rules (§12) | Budget control and drawdown are `GV-008`'s. This document supplies the cost model that `GV-008` §8 controls against |
| **ISO/IEC 19770-1:2017** | §8 operational planning; the entitlement–consumption reconciliation | §5.5 treats each L6 component as an entitlement with a consumption metric, and applies `AR-013` `L6-02`'s 5× volume test to every per-unit metric | Full conformance is an ITAM **management system**, which the Company does not have. This document conforms to the entitlement-modelling clause only, and says so rather than claiming the standard |
| **PMBOK 7** | Delivery, Measurement | Unit economics (§13), including `PE-006` §8.3's two-direction cost-per-order rule | None |
| **ISO/IEC 5230:2020** | §3.2 (identified obligations carry an owner and a cost) | §5.5 and §7.4 carry the cost consequences of the licence positions `CO-004` owns | The compliance programme itself is `CO-004` and `BE-007`. This document costs it |
| **VAT & SD Act 2012** | Imported services; input tax credit; Mushak 6.3, 6.6, 9.1 | §6.1 states both treatments and their cash consequences | **Not a tax opinion.** `TCO-Q-02` requires one before contract signature |
| **Income Tax Act 2023**, as amended by the Finance Act 2026 | Withholding on payments to residents and non-residents for technical and professional services | §6.2 states the rates and quantifies the gross-up exposure | As above. Treaty relief depends on the winning respondent's jurisdiction, which is unknown at issue |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `GV-007` §4.1, §5, §6, §7.1, §7.3 | `../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` | The counted effort position: **1,842 PW build · 648 content · 352 definition · 180 design = 3,022 PW expected**, band 2,537–3,931. And the seven excluded streams |
| `GV-008` §3.2, §4.2–§4.6, §5, §6, §7 | `../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md` | The rate basis, the people-cost translation, the restated 3-year baseline **$1,024K / $1,630K / $2,608K**, and the four caveats this document discharges |
| `PE-006` §5.2–§5.5, §8.1–§8.4 | `../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md` | `PE-006-F-07`: `02-05` §8.2 is production-only. The three excluded lines and their drivers. The connection pooler |
| `PE-002` §3.2, §5.1–§5.12, §9.1–§9.3 | `../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md` | The **twelve** environments, their classes and lifetimes, and `PE-002-F-04` — the same finding from the environment side |
| `PE-001` §3.3, §3.4, §3.5, §8.2 | `../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md` | `BD-R`'s five cost components and the ruling that **key custody and facility dominate, not volume** |
| `PE-007` §4.2, §4.4, §4.5 | `../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md` | `BKP-3` — the immutable copy outside the primary account — and the retention that sizes it |
| `AR-013` §5, §6, §6.1, §7, §7.1 | `../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md` | The build-vs-buy register with owners and review dates; the licence watch; the four L6 components; `L6-02`'s 5× volume rule |
| `BE-007` §6, §7.1, §7.2 | `../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md` | The licence policy as a machine-checked file; **MinIO archived 25 April 2026** (`BEA-16`); the Odoo "LTS" correction (`BEA-13`) |
| `CH-002` §4.6, §7.1, §7.2, §7.3 | `../13_Training_Change_and_Adoption/CH-002_Training_Plan_and_Delivery_Schedule.md` | **Learner time 308–544 PW**; OJT supervisor time 733–1,465 supervisor-days; trainer effort 380–525 trainer-days; `TPD-14`'s requirement that learner time be costed; the assignment of learner devices to `CO-006` |
| `RL-001` §6, `RL-004` `HD-03` | `../12_Release_Deployment_and_Transition/` | Hypercare is **4–8 weeks per wave** (`OP-002` §4.3/§4.8), and the clock runs from the **last** tranche |
| `SC-007` `SC-007-D-01`, §9 | `../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` | *"The mechanism is built in Wave 1 regardless of what the legal opinion says … W1 cost incurred before the answer."* This is why `BD-R` is a Year 1 line |
| `02-05` §4, §6, §7, §8.1–§8.3 | `../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` | The stack, the L6 set, the 20 build-vs-buy decisions, the production sizing and the **production-only** cost progression |
| `00-06` §4 `H-02` | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` | *"Do not present the current TCO to the Board as final."* |
| RFP §16.1, §16.2.1–§16.2.11, §16.3–§16.5, §18.1, §20.3.1 | `../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` | The **published** envelope; the pricing response structure this model must be comparable to; the payment structure; the timetable; the disclosure |
| Bangladesh Bureau of Statistics, via national press reporting of the July 2026 CPI release | External, verified **2026-08-19** | **General CPI 8.32%** (July 2026, point-to-point), food 7.16%, **non-food 9.28%** |
| Foreign-exchange market data | External, verified **2026-08-19** | **USD/BDT 122.70 on 17 August 2026**; 2026 average **122.44**; August high 123.785 on 5 August 2026 |
| PwC Worldwide Tax Summaries — Bangladesh, corporate withholding taxes | External, verified **2026-08-19** | Non-resident technical/professional services **10%** (entities) / 20% (individuals); royalties and intangibles **20%**; resident services generally **5%**; treaty relief by NBR certificate |
| VAT guidance on imported services and input rebate | External, verified **2026-08-19** | Imported services taxable at **15%**, withheld by the bank at payment; input rebate requires a valid **Mushak 6.3**; buyer accounts on **Mushak 9.1** |

### 2.3 Audit findings this document closes, and how

| Finding | Source | Severity | How this document closes or advances it |
|---|---|:--:|---|
| **`H-02`** | `00-06` §4 | High — *"the finding with the largest financial consequence in the audit"* | **Closed in specification.** `GV-008` §4.6 confirmed `H-02` and found it conservative (2.2×–3.3×). This document completes it: with the twelve lines `GV-008` does not carry, the three-year understatement against the figure the Board holds is **4.1× at the midpoint**. `H-02`'s instruction — *"do not present the current TCO to the Board as final"* — is discharged by presenting **this** TCO |
| **`GV-008-D-03`** | `GV-008` §10 | — | **Closed.** §5 re-derives all five non-people lines against `PE-001`, `PE-002`, `PE-006` and `PE-007`, which now exist |
| **`GV-008` `Q-03`** | `GV-008` §11 | — | **Closed.** §5.3 prices `BD-R` at **$22K–$66K per year**, expected $38K, from `PE-001` §3.4's five components |
| **`PE-006-F-07`** and **`PE-002-F-04`** | `PE-006` §8.2 / `PE-002` §9.1 | — | **Closed.** Both findings referred the number to this document. §5.2 supplies it: the twelve-environment, three-site multiplier is **2.17× – 3.34×** the published production-only progression |
| **`AF-09`** | `AUDIT-001` | — | **Advanced.** `GV-007` absorbed the 520–775 PW content estate and `GV-008` costed it at $114K–$310K. This document adds the **second** omission of the same class that `CH-002` §7.2 identified: 308–544 PW of learner time |
| **`AF-08`** | `AUDIT-001` | — | **Advanced.** §9.1 places all seven circulating cost figures in one table with their bases and dispositions, which is what `AF-08` asked for on the effort side |
| **`PGD-A1-05`** | `PGD-AUDIT-001` | — | **Advanced.** Guiding-document and screen-design effort are in the cost model at $229K and $86K expected |
| **`PGD-A2-09`** | `GV-008` §4.5 | — | **Not closed, deliberately.** Two upper bounds ($780K and $850K) circulate for the same baseline. Both are **superseded** by this document, so the contradiction becomes historical rather than resolved. `GV-006` must retire both under `RG-08` |
| **`PGD-A2-10`** | `GV-008` §7.2 | — | **Advanced, not closed.** §10.2 shows the FX correction moves payback independently of the annual/cumulative label problem. Resolving the label remains `BM-003`'s |
| **`CH-002` `TPD-14`** | `CH-002` §7.2 | — | **Closed.** §6.6 costs learner time, OJT supervisor time and the wider internal draw, and reports it alongside delivery cost as `TPD-14` requires |
| **`GV-007` §7.3** | `GV-007` | — | **Partly closed.** Of the seven excluded streams this document sizes **hypercare** (§6.4) and **vendor management, procurement and contract administration** (§6.5), and prices **PMO and assurance** (§6.3), which `GV-008-D-02` excluded. Four remain excluded and §7.5 says which |
| **`CVA-01`** *(raised here)* | This document | Medium | The `CO-nn` rule-prefix collision, enumerated at **108 occurrences across 30 files and 3 repositories** |
| **`CVA-02`** *(raised here)* | This document | **Critical** | The live RFP publishes a budget envelope and an effort basis that the Company's own `GV-007` and `GV-008` superseded five and six days after issue, into an open procurement. §9.4 |
| **`CVA-03`** *(raised here)* | This document | High | **No cost figure in the estate carries a tax line.** §6.1, §6.2 |
| **`CVA-04`** *(raised here)* | This document | High | `GV-008` `A1`'s FX rate of 110 is **11.5% away from the verified market rate** and has not been the market rate at any point in 2026. §6.7 |
| **`CVA-05`** *(raised here)* | This document | Medium | `PE-002` §9.1 counts `dr` twice — as line 2 and again inside *"eleven non-production environments"* — and includes `local`, a developer workstation bearing no shared infrastructure cost. The cost-bearing non-production estate is **nine environments plus `dr`**. §5.2 |
| **`CVA-06`** *(raised here)* | This document | **High** — *re-graded at audit* | **Raised, and resolved on the engineering side within the session.** `SV-005` §4.1 (issued 2026-08-19) settles the duration by summing `OP-002` §4.3's per-wave figures to **56 weeks**. **The commercial residue is larger than the original finding:** RFP §14.1 prices hypercare at four weeks per wave — **36 weeks** — so the contractual scope is understated by **20 weeks, or 56%**, and respondents are pricing against it. §6.4; joins Addendum 1 |

---

## 3. What a TCO Is, and Why This Is Not `GV-008`

### 3.1 The distinction, stated once

Two documents in this estate now carry a cost table with similar row labels. Confusing them would be
easy and would be expensive, so the boundary is stated before either number appears.

| | `GV-008` — Programme Budget & Cost Baseline | **`CO-005` — Total Cost of Ownership** |
|---|---|---|
| **Question answered** | *"How much may the programme spend, and against what authority?"* | *"What does it cost the Company to own and run this system?"* |
| **Horizon** | **3 years** — the programme | **5 years** — the asset's first life-cycle phase |
| **Boundary** | Cost **the programme incurs** | Cost **the Company incurs**, including what no project charges |
| **Contingency and reserve inside it** | **Yes** — §6. They are funding provisions | **No.** A TCO with contingency inside it is not comparable to a bid |
| **Tax** | No | **Yes** — §6.1, §6.2 |
| **Internal time** | No | **Yes**, as a separate tier — §6.6, §7.3 |
| **Years 4–5 run cost** | No | **Yes** — §7.2 |
| **Unsized lines** | **Excluded and declared** (`GV-008-D-02`), because `EM-06` says a figure without a class is not a budget line | **Included with a class label**, because a TCO that omits what it cannot price precisely is bounded below and reads as if it were bounded |
| **Authority** | Board authorises against it | Board decides `D-014` on it; `CO-002` evaluates bids against it |
| **Changes when** | Change request under `GV-003` §6 | Re-baselined at every wave gate (`TCO-09`) |

> **`CO-005-D-01` is the decision that lets the two documents coexist.** `GV-008-D-02` excluded the
> unsized PMO and assurance line under `EM-06` and recorded that the total is therefore *"bounded
> below"*. This document **includes** it, at estimate class 4, and states the reason: a budget line
> must be individually **defensible**, because someone will be authorised to spend it; a TCO line
> must be individually **honest**, and an omission is not honesty. The two documents do not disagree
> about the number. They disagree about what to do with a number you cannot yet defend to two
> significant figures, and each is right for its own purpose.

### 3.2 What ISO 15686-5 requires, and what does not transfer

ISO 15686-5:2017 is the whole-life costing standard and it is written for buildings. Four of its
elements transfer directly and two do not. Saying which is which is what `PG-06` requires.

| ISO 15686-5 element | Transfers? | Treatment here |
|---|:--:|---|
| **Analysis period**, stated and justified | ✅ | §3.3 |
| **Acquisition / construction cost** | ✅ | §7.1 lines A–D — people, escalation |
| **Operation cost** | ✅ | §7.1 lines E–H — infrastructure, APIs, licences |
| **Maintenance cost** | ✅ | §7.1 line I — support and maintenance |
| **Residual value** at the end of the analysis period | ⚠ **Departure** | Treated as **zero**. A five-year-old deployment of Odoo 19.0 — out of standard support since about September 2028, with **no extended-support path for Community Edition** (`BE-007` §7.2, verified) — has no realisable resale value, and treating the sunk build as an asset with a residual would flatter the model |
| **End-of-life / disposal cost** | ⚠ **Departure** | Replaced by **decommissioning and exit cost** — §7.4. It is not zero: `AR-013` `L6-05` requires every L6 component to have a documented exit, and data extraction under RFP §19.1(5) is real work |

### 3.3 The analysis period, and why five years

| Option | Argument for | Why it was not chosen |
|:--:|---|---|
| 3 years | Every existing figure in the estate uses it; comparability | **Wave 9 completes at Month 36.** A three-year TCO measures a system that has never run a full year in its final configuration. It is a *programme* horizon dressed as an *ownership* horizon |
| **5 years** | **Chosen.** RFP §16.2.10 already requires respondents to state Year 4 and Year 5 run rates, so the Company must be able to evaluate them. `06-02` §3.2's benefit curve runs to Year 5. Two full years of steady-state run cost become visible | — |
| 7–10 years | Closer to a true life cycle | Beyond five years the model is dominated by a platform-upgrade decision (`ADR-027`, `D-025`) that has not been taken. Estimating it would be class 5 resting on class 5 |

> **`TCO-01` — the analysis period is five years from programme kickoff, and Years 4–5 are reported
> separately from Years 1–3.** They are not blended, because Years 1–3 contain a project and Years
> 4–5 do not. Blending them hides the run rate, which is the figure that persists after everyone
> who authorised the programme has moved on.

### 3.4 The two tiers

| Tier | Definition | Who needs it |
|:--:|---|---|
| **Tier 1 — Incremental cash cost** | Money that leaves the Company's bank account and would not have left it had the programme not happened | **The Board**, for `D-014`. `CO-002`, for bid comparability. This is the figure comparable to a respondent's TCO response under RFP §16.2.9 |
| **Tier 2 — Full economic cost** | Tier 1 **plus** the internal resource cost of the people whose time the programme consumes | **The CEO**, because Tier 2 minus Tier 1 is a draw on a 500-person organisation that has never been quantified or approved. `CH-002` `TPD-14` and `GV-007` §7.5 both require it |

> **Neither tier is "the" TCO, and a document that publishes only one is making an argument rather
> than a measurement.** Tier 1 understates what the programme costs the Company. Tier 2 overstates
> what it costs in cash. Both are stated, and §7.3 states the bridge between them — the **backfill
> decision**, which is the only part of Tier 2 that can become Tier 1.

---

## 4. Method

### 4.1 The five steps

| Step | Method | Rule |
|:--:|---|---|
| 1 | Take the **effort** position from `GV-007` §7.1 — low / expected / high per work stream. Do not re-estimate | `TCO-02` |
| 2 | Apply `GV-008` §3.2's **rate classes**, unchanged, so that every difference between this document and `GV-008` is attributable to a *line*, never to a re-rating | `TCO-03` |
| 3 | **Re-derive** each non-people line from the `PE-*` documents that now exist, showing the driver and the multiplier (§5) | `TCO-04` |
| 4 | **Add** the lines no existing figure carries — tax, FX, escalation, hypercare, PMO, internal resource (§6) | `TCO-05` |
| 5 | Regenerate every total **from its own rows** at the point of writing, and show the arithmetic inline | `PG-M10` |

### 4.2 Rate basis — carried, not changed

`GV-008` `CB-01` derived the build rate from the approved case's own implied rate:
$290K–$470K ÷ 834 PW = **$348–$564 per person-week**. That basis is carried here unchanged, for the
reason `CB-01` gives: *"an increase driven by both effort and rate would be unarbitrable."*

| Rate class | $/PW | Applied to |
|---|---|---|
| **Build** | $350 – $565 | Module and portal build; hypercare; standalone services |
| **Engineering definition** | $500 – $800 | The 127 remaining guiding documents |
| **Content** | $220 – $400 | The 477-file content estate |
| **Experience design** | $350 – $600 | Screen design |
| **Internal (1000FiX staff)** | **$100 – $210** | §6.6. **Newly derived here** — see below |

> **The internal rate is the one new rate in this document, and it is derived rather than assumed.**
> A 1000FiX super-user, branch champion, workshop supervisor or accountant on a Bangladesh salary of
> **BDT 40,000 – 80,000 per month** costs BDT 9,200 – 18,400 per week; at the verified rate of
> **122.70** that is **$75 – $150 per week**, and at a conventional 1.4× employment-cost loading,
> **$105 – $210 per person-week**. Rounded to **$100 – $210**, expected **$150**. Estimate class 4:
> the loading factor is conventional and the salary band is a market inference, not a payroll
> extract. **`TCO-Q-01`: the HR Director replaces this band with the actual loaded cost per grade,
> from the `M21` payroll data, before the Board paper is issued.**

### 4.3 Estimate classes carried

| Line | Class | Why |
|---|:--:|---|
| Build people cost | **2** | 79 specifications counted; effort estimated by their specifiers (`GV-007` §4.1) |
| Content and engineering-definition people cost | **3** | Counted file inventory, estimated rate per file |
| Screen-design people cost | **5** | The screen count is *"an order-of-magnitude inference"* (`GV-007` §6.1). `UX-003` converts it |
| Infrastructure — regional | **4** | Driver counted (12 environments, 3 sites); multipliers are engineering judgement, not quotations |
| Infrastructure — `BD-R` | **4** | Five components named by `PE-001` §3.4; no facility or HSM quotation obtained |
| Third-party APIs | **3** | Volumetrics derived in `PE-006` §4; unit prices are published tariffs |
| L6 commercial | **3** | Four components, published price bands, volume from `PE-006` |
| Support and maintenance | **4** | Per-module derivation from a 30-module base |
| Hypercare | **4** | Duration range and squad size are judgement; `SV-005` will improve both |
| PMO and assurance | **4** | Conventional percentage of delivery cost |
| Tax | **3** | Statutory rates verified; the recoverable proportion is an opinion not yet obtained |
| FX | **2** | Spot and average rates verified 2026-08-19 |
| Escalation | **3** | Published CPI; contractual cap known from RFP §16.2.11 |
| Internal resource | **5** | Commitment percentages are stated policy (`06-01` §4), never validated against an establishment |

> **`TCO-06` — per `GV-007` `EM-05`, an estimate is no better than its worst input.** This document
> contains class 5 lines. **Its overall class is 5**, and it is published as class 5. Two events
> improve it materially and nothing else does: `UX-003` converting the screen inference to a count,
> and an establishment review converting §6.6's commitment percentages into named people.

---

## 5. Re-derivation of the Non-People Lines

This section discharges `GV-008-D-03`. Each of the five lines `GV-008` §4.3 carried with a caveat is
re-derived against the `PE-*` documents that now exist. **The method is to keep the published figure
as the production-only base and to derive a multiplier from a counted driver**, rather than to
substitute a new absolute figure whose provenance would be no better than the one it replaced.

### 5.1 What the published progression actually measures

`02-05` §8.2 gives a monthly infrastructure cost per wave and an annual roll-up of ~$8K (Year 1),
~$19K (Year 2) and ~$44K (Year 3) — **$71K over three years**, which `GV-008` §4.3 carried as a band
of $52K–$96K.

**Verification of the base** *(regenerated per `PG-M10`)*: Year 1 spans W1–W2 at $450–$1,200/month,
average ≈ $700 × 12 = **$8.4K** ✓ · Year 2 spans W3–W4 at $1,200–$2,400/month, average ≈ $1,500 ×
12 = **$18.0K** ✓ · Year 3 spans W5–W9 at $2,000–$5,800/month, average ≈ $3,500 × 12 = **$42.0K** ✓.
Sum **$68.4K**, consistent with the stated ~$71K. The column heading *"Cumulative Annual"* is
therefore a mislabel — the values are **annual**, not cumulative, exactly as `PGD-A2-10` found for
`06-02` §3.2's benefit curve. Two tables in the estate carry the same label defect.

**What that base covers, and what it does not:**

| Dimension | What `02-05` §8.2 covers | What the architecture requires |
|---|---|---|
| Environments | **`prod` only** | **Twelve** — `PE-002` §5 |
| Sites | **One region** | **Three** — `RGN-P`, `RGN-S` (`dr`), `BD-R` — `PE-001` §3 |
| Residency | **None** | `Z4` resident store, production **and** standby — `SC-007`, `PE-001` §3.3 |
| Backup | Not itemised | `BKP-3` immutable copy **outside the primary account**, plus egress — `PE-007` §4.4 |
| Pooler | **Absent** | Required; HA pair — `PE-006` §5.2 line 1, §5.5 |

> **`PE-006-F-07` and `PE-002-F-04` are the same finding reached independently from two directions**,
> and both referred the number to this document. It is supplied below.

### 5.2 Regional infrastructure — the environment and site multiplier

**`CVA-05` first, because it changes the count.** `PE-002` §9.1 lists three excluded lines: `BD-R`,
`dr`, and *"non-production environments — eleven of them"*. Counted from `PE-002` §5, the estate has
**twelve** environments; excluding `prod` leaves **eleven**; but `dr` is already line 2 of the same
table, and `local` is a developer workstation on Docker Compose at `172.20.0.0/16` (`PE-002` §5.1)
which bears **no shared infrastructure cost at all**. The cost-bearing non-production estate is
therefore **nine environments, plus `dr` counted once**. Referred to `PE-002` and `PE-006` for
correction; it does not change either document's conclusion, only its arithmetic.

**The nine, priced as a share of production:**

| Environment | Class (`PE-002` §3.2) | Share of `prod`, low | high | Driver |
|---|---|---:|---:|---|
| `ci` | Open | 0.05 | 0.10 | Short-lived runners; minutes, not months |
| `dev` | Open | 0.10 | 0.20 | Always on; small; synthetic data |
| `sit` | Controlled | 0.10 | 0.20 | Always on through a wave |
| `uat` | Controlled | 0.10 | 0.20 | Always on through a wave; masked data |
| `staging` | Controlled | 0.30 | 0.50 | **Parity is the point** (`PE-002` §7.1); the closest to production of the eleven |
| `training` | Controlled | 0.10 | 0.20 | Peaks at each wave's training window; 800+ learners |
| `perf` | Controlled | 0.05 | 0.15 | **Production-scale by definition** — `DoD-14` requires 1.5× expected peak — but **ephemeral per gate** (`PE-002` §9.3), so it costs its run time |
| `migration-staging` | **Production-class** | 0.08 | 0.20 | Production-volume legacy extracts; **per migration wave**, then destroyed |
| `sandbox` | Open, **externally exposed** | 0.05 | 0.15 | Small, but externally reachable, so it carries its own ingress and WAF |
| **Non-production subtotal** | | **0.93** | **1.90** | |

**Verification** *(regenerated per `PG-M10`)*: low 0.05 + 0.10 + 0.10 + 0.10 + 0.30 + 0.10 + 0.05 +
0.08 + 0.05 = **0.93** ✓ · high 0.10 + 0.20 + 0.20 + 0.20 + 0.50 + 0.20 + 0.15 + 0.20 + 0.15 =
**1.90** ✓.

**The full regional multiplier:**

| Component | Low | High | Basis |
|---|---:|---:|---|
| `prod` | 1.00 | 1.00 | The published progression |
| Nine non-production environments | 0.93 | 1.90 | Above |
| `dr` — `RGN-S` standing compute, replicated storage, replication egress, `BKP-3` | 0.25 | 0.40 | `PE-006` §5.4: *"storage- and egress-dominated; compute near zero"*; failover capacity has **zero standing cost** because it is scaled from IaC |
| Connection pooler, HA pair | 0.02 | 0.04 | `PE-006` §5.5 — two small `Z2` instances |
| **Total multiplier on the published production progression** | **2.20** | **3.34** | |

**Verification**: low 1.00 + 0.93 + 0.25 + 0.02 = **2.20** ✓ · high 1.00 + 1.90 + 0.40 + 0.04 =
**3.34** ✓. Expected multiplier = **2.75** (mid-point).

| | Low | Expected | High |
|---|---:|---:|---:|
| Published production base, 3 years | $52K | $71K | $96K |
| × multiplier | × 2.20 | × 2.75 | × 3.34 |
| **Regional infrastructure, 3 years** | **$114K** | **$195K** | **$321K** |

**Verification**: 52 × 2.20 = 114.4 → **$114K** ✓ · 71 × 2.75 = 195.25 → **$195K** ✓ ·
96 × 3.34 = 320.6 → **$321K** ✓.

> **The two mechanisms that keep this from being far worse are `PE-002` §9.3's ephemerality rules,
> and they depend entirely on `PE-003`.** `perf` at production scale and `migration-staging` at
> production volume would together carry 1.0–1.5× production if they ran permanently. They carry
> 0.13–0.35 because they are destroyed between uses. **`PE-002` `LC-02` — *"a hand-built environment
> is not an environment; it is a liability with a hostname"* — is worth roughly $60K–$110K over
> three years**, and that is the strongest cost argument for infrastructure-as-code the programme
> has.

### 5.3 `BD-R` — the Bangladesh-resident store, priced

This closes `GV-008` `Q-03`. `PE-001` §3.4 names five components and rules that **cost is dominated
by availability and key custody, not by volume**. Priced accordingly:

| Component | Annual, low | Annual, high | Basis |
|---|---:|---:|---|
| `Z4` production HA pair — 4 vCPU / 16 GB / 500 GB × 2 | $3.0K | $6.0K | Technology Stack §21.1 sizing; small compute, small storage |
| `Z4` **standby** — the same again | $3.0K | $6.0K | `SC-007-DR-1`; `PE-002` §5.12 |
| **In-country key custody** — HSM or managed KMS | **$6.0K** | **$24.0K** | `SC-006` `ES-3`. `PE-001` §3.4 calls it *"the disproportionate line"* and it is: a dedicated HSM is an order of magnitude above the compute it protects |
| Cross-border private link `RGN-P` ↔ `BD-R` | $3.6K | $12.0K | `PE-001` §8.2 — low bandwidth; **latency and availability are the constraint**, and availability is what costs |
| Facility — Tier III+ colocation, power, cooling, remote hands | $6.0K | $18.0K | `PE-001` §3.3, `SEL-01`. Tier IV preferred, which sits at the top of the band |
| **Annual total** | **$21.6K** | **$66.0K** | |

**Verification**: low 3.0 + 3.0 + 6.0 + 3.6 + 6.0 = **21.6** ✓ · high 6.0 + 6.0 + 24.0 + 12.0 +
18.0 = **66.0** ✓. Rounded: **$22K – $66K per year**, expected **$38K** *(estimate class 4)*.

**When it starts.** `SC-007-D-01` rules that *"the mechanism is built in Wave 1 regardless of what
the legal opinion says"* and accepts the consequence: *"W1 cost incurred before the answer."*
`BD-R` is therefore a **Year 1** line and recurs in every year of the analysis period.

| | Low | Expected | High |
|---|---:|---:|---:|
| **`BD-R`, 3 years** | **$66K** | **$114K** | **$198K** |
| **`BD-R`, Years 4–5** | **$44K** | **$76K** | **$132K** |

> **`BD-R` alone, over three years, is larger than the entire infrastructure line `GV-008` carries.**
> $66K–$198K against $52K–$96K. This is not a criticism of `GV-008`, which said so in a caveat and
> named this document as the place to fix it. It is the measure of how far a production-only,
> single-region figure can be from a total.
>
> **And it is not discretionary.** `AR-001` §8.2 places `Z4` in the path of **every `T5` read in the
> system**, so its availability requirement is at least that of the estate as a whole — which is why
> the standby is not optional and why the facility tier, not the data volume, sets the price.

### 5.4 Third-party API consumption

`02-05` §8.3 gives **$1,890–$5,230 per month at scale** across ten services, which `GV-008` §4.3
carried as $41K–$95K over three years.

**The ramp arithmetic behind the low bound is sound and is retained**: at $1,890/month = $22.7K/year
at full scale, with a ramp of roughly 25% / 55% / 100% of scale across Years 1–3, the three-year sum
is 22.7 × 1.80 = **$40.9K**, which is `GV-008`'s $41K. That figure is not disturbed.

**Three drivers raise the upper bound:**

| # | Driver | Effect |
|:--:|---|---|
| 1 | **`AR-013` `L6-02` requires every per-unit metric to be modelled at 5× projected volume before signing.** Six of the ten lines are per-unit: SMS, WhatsApp, Maps, traffic, identity verification, storage egress | The upper bound must reflect a volume the Company has explicitly decided to plan for |
| 2 | **Storage egress was sized against a 20 TB store.** `PE-006` §4.5 derives **~12 TB/year** of growth, so by Year 3 the store is roughly 2× the sizing assumption and by Year 5 roughly 3× | Egress and replication egress both scale with it |
| 3 | **The `dr` region adds continuous cross-failure-domain replication egress** that no published figure carries | `PE-006` §5.4: *"storage- and egress-dominated"* |

| | Low | Expected | High |
|---|---:|---:|---:|
| **Third-party APIs, 3 years** | **$41K** | **$85K** | **$150K** |
| **Third-party APIs, Years 4–5** | **$46K** | **$80K** | **$126K** |

Years 4–5 assume full scale in both years at $23K–$63K/year, with volume growth of about 10% a year
against the marketplace and MSP lines.

> **Payment gateway fees are netted against revenue in `02-05` §8.3 and are shown gross nowhere.**
> ISO 15686-5 requires costs to be stated, not netted. At marketplace scale the gateway fee is a
> direct function of gross merchandise value and belongs in `BM-003`'s margin model rather than in a
> TCO, but **it must appear somewhere and currently appears nowhere.** Raised as `TCO-Q-05`.

### 5.5 L6 commercial components

Four components, from `02-05` §6 and `AR-013` §7. `GV-008` §4.3 carried them at **$0–$36K over three
years** — a range whose zero floor comes from `00-02` principle 2 (open source by default).

| Component | Metric | Published band | Volume basis | 3-year, low | 3-year, high |
|---|---|---|---|---:|---:|
| Cloud telephony / CPaaS | Per minute + seats | $200–$600 / month | Hotline 16743, contact-centre seats (`P10`) | $7.2K | $21.6K |
| Qualified e-signature | Per envelope | $100–$400 / month | AMC, MSP, rental and **seller** agreements — the marketplace drives envelope count | $3.6K | $14.4K |
| Identity verification / KYC | **Per check, $0.30–$0.80** | — | **Marketplace seller onboarding (`M12`, `P07`) and high-value customers.** The volume driver is seller growth, which is a business-plan variable | $1.8K | $18.0K |
| Endpoint RMM agent | **Per endpoint, $2–$5 / month** | — | **`D-18` open**; decision at the W5 pilot. Client Windows/macOS estates under `M05` | $0 | $36.0K |
| **Total** | | | | **$12.6K** | **$90.0K** |

**Verification**: low 7.2 + 3.6 + 1.8 + 0 = **12.6** ✓ · high 21.6 + 14.4 + 18.0 + 36.0 = **90.0** ✓.

> **The published *"$0–$36K over three years"* is not reproducible from its own components and is
> too low at the top.** Two of the four components are **per-unit** metrics with no volume cap, and
> `AR-013` `L6-02` exists precisely because of them: *"model every per-unit metric at 5× projected
> volume before signing. The RMM agent at $2–$5 per endpoint is the one that scales dangerously."*
> A 1,000-endpoint MSP book at $3/endpoint/month is $36K **per year**, not per three years. The
> figure below is therefore restated, and `CO-006` `PPP-08` makes the volume cap a procurement
> requirement rather than a hope.

| | Low | Expected | High |
|---|---:|---:|---:|
| **L6 commercial, 3 years** | **$13K** | **$45K** | **$90K** |
| **L6 commercial, Years 4–5** | **$8K** | **$34K** | **$70K** |

**A fifth L6 component is now likely, and it is not in this table.** `BE-007` §7.1 records that
**MinIO's community edition was archived on 25 April 2026** — verified independently against public
sources on 2026-08-19 — and that TSS §7.4 assessed and **rejected** *"cloud-native object storage
only"* as a fallback on residency grounds. If the `W0` assessment selects a managed object store,
that is a **new recurring licence or service cost** and, under `AR-013` `L6-04`, requires **Design
Authority and CFO approval** because the bounded set of four is the point of the position. If it
selects **Garage** — AGPL-3, Rust, S3-compatible, actively maintained with a release on 16 April
2026 — the cash cost is zero and the **AGPL-3 obligation is inherited unchanged**, which is
`CO-004`'s to own. Neither outcome is costed here because the decision has not been taken.
`TCO-Q-06`.

### 5.6 Support and maintenance

`GV-008` §4.3 carried **$50K–$110K for Years 2–3** with the caveat *"sized against a 30-module
system."* Re-derived per module:

| Step | Working |
|:--:|---|
| 1 | The carried figure is $50K–$110K over two years for **30 modules** = $25K–$55K per year |
| 2 | Per module per year: $25K ÷ 30 = **$0.83K**; $55K ÷ 30 = **$1.83K** |
| 3 | Modules live is not 67 in every year. From `GV-004` §5.2 and `06-01`: end of Year 1 ≈ W2 complete; end of Year 2 ≈ W4–W5 complete (**v1.0 scope**, Month 18); end of Year 3 ≈ W9 complete |
| 4 | Average live module count: **Year 2 ≈ 35 · Year 3 ≈ 55 · Years 4–5 = 67** |

| Year | Live modules | Low | High |
|---|---:|---:|---:|
| Year 2 | 35 | $29K | $64K |
| Year 3 | 55 | $46K | $101K |
| **Years 2–3 total** | | **$75K** | **$165K** |
| Year 4 | 67 | $56K | $123K |
| Year 5 | 67 | $56K | $123K |

**Verification**: 35 × 0.83 = 29.1 ✓ · 35 × 1.83 = 64.1 ✓ · 55 × 0.83 = 45.7 ✓ · 55 × 1.83 =
100.7 ✓ · 29 + 46 = **75** ✓ · 64 + 101 = **165** ✓ · 67 × 0.83 = 55.6 ✓ · 67 × 1.83 = 122.6 ✓.

| | Low | Expected | High |
|---|---:|---:|---:|
| **Support and maintenance, Years 2–3** | **$75K** | **$120K** | **$165K** |
| **Support and maintenance, Years 4–5** | **$112K** | **$180K** | **$246K** |

> **This line excludes hypercare**, which `GV-007` §7.3 lists as an excluded work stream in its own
> right and which §6.4 sizes separately. The exclusion is stated because the RFP's own pricing
> structure (§16.2.8) puts hypercare *inside* support and maintenance, and a reader comparing this
> model to a bid must know that the boundary differs. `CO-002` §7.2 normalises for it.

### 5.7 Change and training delivery

`GV-008` §4.3 carried **$22K–$43K** with the caveat *"sized for `SB-2`. 800+ employees across 51+
branches, nine waves."* RFP §16.1 already restated this line to **$35K–$65K** on the 1,513 PW basis.

`CH-002` §7.1 supplies the establishment this line has to pay for, and it is not currently in any
budget: **2.8–3.5 Bengali-capable trainer FTE at the W1–W2 peak**, a 1.0 FTE Training Lead for 36
months, and 0.5–1.0 FTE of perpetual instructional design. `CH-002` marks every one of them
*"In `GV-007` §8? ✘ — Funded? ✘"*.

| | Low | Expected | High |
|---|---:|---:|---:|
| **Change and training delivery, 3 years** | **$35K** | **$52K** | **$85K** |
| **Years 4–5** — refresh, perpetual, per `CH-002` `TPD-19` | **$12K** | **$24K** | **$40K** |

> **This is the external delivery cost only.** The **learner** time it consumes — 308–544 PW —
> is Tier 2 and is at §6.6. `CH-002` `TPD-14` requires them to be reported together, and §7.3 does
> exactly that.

### 5.8 The re-derived non-people position

| # | Line | `GV-008` §4.3 carried | **Re-derived, 3 years** | Δ (expected) |
|:--:|---|---|---|---:|
| 2 | L6 commercial licensing | $0 – $36K | **$13K / $45K / $90K** | +$27K |
| 3 | Infrastructure — regional, 12 environments, 3 sites | $52K – $96K | **$114K / $195K / $321K** | +$121K |
| 3a | **`BD-R`** — *absent from every published figure* | — | **$66K / $114K / $198K** | **+$114K** |
| 4 | Third-party APIs | $41K – $95K | **$41K / $85K / $150K** | +$17K |
| 5 | Change and training delivery | $22K – $43K | **$35K / $52K / $85K** | +$20K |
| 6 | Support and maintenance, Years 2–3 | $50K – $110K | **$75K / $120K / $165K** | +$40K |
| | **Non-people subtotal, 3 years** | **$165K / $272K / $380K** | **$344K / $611K / $1,009K** | **+$339K** |

**Verification** *(regenerated from the rows per `PG-M10`)*: low 13 + 114 + 66 + 41 + 35 + 75 =
**344** ✓ · expected 45 + 195 + 114 + 85 + 52 + 120 = **611** ✓ · high 90 + 321 + 198 + 150 + 85 +
165 = **1,009** ✓. Expected delta 611 − 272 = **339** ✓.

> **`GV-008`'s caveat said the non-people subtotal was *"understated by an unknown amount"*. The
> amount is 2.2× at the expected case, and $114K of it — a third — is a single line that appears in
> no published figure at all.**

---

## 6. The Lines No Cost Figure in the Estate Carries

`GV-007` §7.3 listed seven work streams outside its estimate and instructed: *"`GV-008` must carry
an explicit allowance for them, and `CO-005` must state that the TCO is bounded below, not
bounded."* This section carries them, plus five more that no document has named.

### 6.1 Bangladesh VAT — `CVA-03`, part one

**RFP §16.2 requires all pricing "exclusive of Bangladesh VAT, with the VAT treatment stated
separately."** Every cost figure in the estate is therefore a pre-VAT figure, and **no document
carries the VAT line.** At the standard rate of **15%** on a contract of the size in §7.1, that is
between **$129K and $334K of cash** that must be funded.

**Two treatments apply, and which one applies to which part of the contract depends on the
respondent's structure — which RFP §16.2.11 explicitly contemplates being mixed** (onshore and
offshore day rates) and MQ-04 explicitly permits (*"a named local implementation partner"*).

| | **Resident supplier** | **Non-resident supplier** |
|---|---|---|
| Mechanism | Supplier charges 15% and issues **Mushak 6.3** | **Imported services** — VAT at 15% withheld by the bank at the time of payment and deposited to the Commissionerate |
| 1000FiX accounts on | **Mushak 9.1** monthly return | **Mushak 9.1** monthly return |
| Input rebate available? | **Yes**, against a valid Mushak 6.3 | **Yes**, subject to documentation |
| Evidence 1000FiX must hold | Mushak 6.3 per invoice; **Mushak 6.6** VDS certificate where VAT is deducted at source | Bank challan; treasury deposit evidence |
| Real (non-recoverable) cost | **Nil if fully rebated** | **Nil if fully rebated** |
| **Cash requirement** | **15% funded at payment**, recovered in the following return period | As left |
| Failure mode | **A missing or defective Mushak 6.3 makes the rebate unavailable and converts 15% into a real cost** | Documentation failure has the same effect |

**Three consequences, in order of importance:**

| # | Consequence | Magnitude |
|:--:|---|---|
| 1 | **A cash-funding requirement of $129K–$334K across the programme** that `GV-008` §5's drawdown schedule does not contain | Referred to `GV-008` for the drawdown, not carried as a cost here |
| 2 | **A rebate-integrity dependency on `M51`.** Input rebate requires a valid Mushak 6.3 per invoice. `M51` — the Mushak module — is the system that produces and validates them, and it is a **Wave 3** deliverable (`06-01`). **For the first three years of contract payments the rebate rests on a manual process the ERP does not yet support** | The exposure is the rebate, not the tax |
| 3 | **Apportionment risk.** Input rebate is available in proportion to taxable output. If any part of 1000FiX's output is exempt or zero-rated, a proportion of the input VAT becomes a **real** cost | **Unquantified. `TCO-Q-02`** |

| | Low | Expected | High |
|---|---:|---:|---:|
| **VAT — non-recoverable residue, 3 years** | **$0** | **$20K** | **$50K** |

Low assumes full recovery with clean documentation. High assumes roughly 15% of the VAT is lost to
apportionment or documentation failure. **The cost of carry is immaterial and is stated so rather
than padded**: at a continuously revolving one-month lag the average outstanding balance is under
$10K, and its financing cost is roughly $1K over three years.

> **`TCO-07` — the VAT line is stated separately from price in every commercial table in this
> estate, and a total that does not say whether it is VAT-inclusive is not a total.** All figures in
> §7 are **exclusive of recoverable VAT** and **include** the non-recoverable residue above.

### 6.2 Withholding tax and the gross-up question — `CVA-03`, part two

Verified 2026-08-19 against published Bangladesh withholding-tax guidance:

| Payment | Recipient | Rate |
|---|---|---:|
| Technical / professional / consultancy services | **Non-resident entity** | **10%** |
| Technical / professional / consultancy services | Non-resident individual | 20% |
| **Royalty, licence fee, payments for intangibles** | Non-resident | **20%** |
| Services generally | Resident | **5%** |

Treaty relief is available where a double-taxation agreement applies, on an **NBR certificate**
authorising payment without deduction or at a reduced rate.

**The commercial question is not the rate. It is who bears it.**

| Position | Consequence |
|---|---|
| Contract states the price is **inclusive of all taxes payable by the supplier**, and 1000FiX withholds from it | **Zero additional cost.** The vendor's net receipt falls by 10%; that is the vendor's tax, correctly borne by the vendor |
| Contract is **silent** | The vendor will, at the first payment, request a **gross-up** so that it receives the contracted sum net of withholding. A 10% withholding grossed up is **11.1%** on the affected portion |
| Contract states the price is **net of taxes** / the Company grosses up | **11.1% added to the offshore portion**, contractually, with no recourse |

**Quantified.** RFP §16.2.11 requires separate onshore and offshore day rates, so the offshore
proportion is a contract variable. At 40%–70% of contract value offshore:

| | Low | Expected | High |
|---|---:|---:|---:|
| Offshore share assumed | 40% | 55% | 70% |
| People cost base (§7.1 line A) | $859K | $1,358K | $2,228K |
| Gross-up at 11.1% of the offshore share | $38K | $83K | $173K |
| **Exposure if the contract is silent** | **$38K** | **$83K** | **$173K** |
| **Exposure if `CO-003` `SOW-42` is included** | **$0** | **$0** | **$0** |

**Verification**: 859 × 0.40 × 0.111 = 38.1 ✓ · 1,358 × 0.55 × 0.111 = 82.9 ✓ · 2,228 × 0.70 ×
0.111 = 173.1 ✓.

> **This is the cheapest finding in the document to act on and the most expensive to ignore.** One
> clause in the Statement of Work — `CO-003` `SOW-42` — removes an $83K expected exposure at zero
> cost, and it must be in the contract **before** negotiation rather than raised at the first
> invoice, when the leverage has gone. The §7.1 model carries the exposure at the expected case
> because, as at the date of issue, **the clause does not exist**.
>
> **One provision already drafted works in the Company's favour and should not be traded away.**
> RFP §19.1(3) requires the respondent's pre-existing proprietary frameworks to be licensed
> *"perpetually, irrevocably and royalty-free."* Royalty-free is not merely commercially good; it
> avoids the **20%** royalty withholding class entirely. A negotiator offered a lower headline price
> in exchange for a royalty-bearing licence should decline.

### 6.3 Programme management, assurance and PMO

`GV-008` §4.2 line 1.5: *"has never been sized by anyone"*, excluded under `GV-008-D-02`, with a
declared shape of *"conventionally 8–12% of delivery cost, roughly $110K–$270K."*

Included here under `CO-005-D-01`, at 8% of the low case, 10% of the expected and 12% of the high:

| | Low | Expected | High |
|---|---:|---:|---:|
| People cost base | $859K | $1,358K | $2,228K |
| Rate | 8% | 10% | 12% |
| **PMO, assurance and programme management** | **$69K** | **$136K** | **$267K** |

**Verification**: 859 × 0.08 = 68.7 ✓ · 1,358 × 0.10 = 135.8 ✓ · 2,228 × 0.12 = 267.4 ✓.
Reconciles with `GV-008`'s declared *"roughly $110K–$270K"* as its expected-to-high band.

**This line also funds `GV-010`'s independent assurance**, which `GV-008` §6.3 lists among the named
calls on the $60K risk budget. The overlap is noted rather than double-counted: the risk budget funds
**treatment of identified risks**; this line funds the **standing** assurance function.

### 6.4 Hypercare, nine times — `CVA-06`

`GV-007` §7.3 excluded it: *"Hypercare — four weeks after **every** wave go-live, nine times;
recurs at every wave boundary."*

**`SV-005` was issued on 2026-08-19, during this document's authoring window, and it supersedes the
estimate this section first carried.** Per `TCO-02`, the owning document's figure is taken unchanged
rather than re-derived. `SV-005` §5.5 derives **≈ 678 person-weeks across three pools**, from
`OP-002` §4.3's per-wave durations summed to **56 weeks** — not the 36 weeks that four-weeks-per-wave
implies.

| Pool (`SV-005` §5.5) | Effort | Owner | Tier here | Rate class |
|---|--:|---|:--:|---|
| **1 — Project**: ring-fenced delivery team + coordination | **288 PW** | Programme / CTO | **Tier 1** | Build |
| **2 — Support**: T1 staffing at 2× baseline | **250 PW** | Head of ITSM / CFO | **Tier 1** | Support — derived below |
| **3 — Business**: floor-walking, ride-alongs, branch clinics | **≈ 140 PW** | Operations Director | **Tier 2** — §6.6 | Internal |
| **Total** | **≈ 678 PW** | | | |

**The support rate, derived** *(the second new rate in this document, after §4.2's internal rate)*:
a Bangladesh T1/T2 support engineer at **BDT 45,000–90,000 per month** costs BDT 10,400–20,800 per
week; at the verified rate of 122.70 that is **$85–$170 per week**, and at a 1.4× employment-cost
loading, **$119–$238 per person-week**. Rounded to **$120–$240**, expected **$180**. Estimate class 4.

| Pool | PW | Low rate | Exp rate | High rate | **Low** | **Expected** | **High** |
|---|--:|--:|--:|--:|--:|--:|--:|
| 1 — Project | 288 | $350 | $458 | $565 | **$101K** | **$132K** | **$163K** |
| 2 — Support | 250 | $120 | $180 | $240 | **$30K** | **$45K** | **$60K** |
| **Tier 1 hypercare (line C)** | **538** | | | | **$131K** | **$177K** | **$223K** |

**Verification** *(regenerated per `PG-M10`)*: 288 × 350 = $100.8K ✓ · 288 × 458 = $131.9K ✓ ·
288 × 565 = $162.7K ✓ · 250 × 120 = $30.0K ✓ · 250 × 180 = $45.0K ✓ · 250 × 240 = $60.0K ✓ ·
101 + 30 = **131** ✓ · 132 + 45 = **177** ✓ · 163 + 60 = **223** ✓ · 288 + 250 = **538 PW** ✓.

> **`CVA-06` is resolved on the engineering side and sharpened on the commercial side.** `SV-005`
> settles the duration question the estate could not answer: it adopts `OP-002` §4.3's per-wave
> durations — 8, 6, 8, 6, 8, 4, 6, 4, 6 — summing to **56 weeks**, and supersedes both the flat
> "4 weeks" and the "4–8 weeks" range.
>
> **What that does to the commercial position is the finding.** RFP §14.1 prices hypercare at
> **four weeks per wave — 36 weeks**. The estate's own owning document now requires **56**.
> **The RFP understates the hypercare scope by 20 weeks, or 56%**, and respondents are pricing
> against the lower figure. This joins `CVA-02`'s list of items for **Addendum 1**, and
> `CO-003` `SOW-13` and `SOW-22` depend on it.

> **`SV-005` §5.7's own comparison uses the superseded 1,513 PW build figure**, giving hypercare as
> *"≈ 45% of build"*. Against `GV-007` §4.1's counted **1,842 PW** the correct share is
> **678 ÷ 1,842 = 36.8%**. Referred to `SV-005`; it does not change any figure in this document,
> which uses the 678 PW directly.

### 6.5 Vendor management, procurement and contract administration

`GV-007` §7.3 lists it as excluded and names its owner: **CFO**, and its documents: `CO-002`,
`CO-003`. It is the cost of running the commercial relationship — evaluation, negotiation, the
`CO-003` acceptance regime, monthly variance reporting under `GV-008` `CB-07`, the wave-gate
re-baselining under RFP `CR-02`, and the licence-obligation reviews under `CO-004`.

| Element | Basis | 3-year, low | 3-year, high |
|---|---|---:|---:|
| Evaluation and award (`CO-002`) — committee time across six RFP §17.1 stages, from 30 Oct 2026 to 16 Apr 2027 | ~6 people × ~20% × ~24 weeks | $6K | $14K |
| Contract negotiation and legal (`CO-003`) — 8 Mar to 9 Apr 2027, plus the DPA and the tax opinions | External counsel + internal | $12K | $35K |
| Contract administration, 36 months — acceptance, invoicing, retention, variance | 0.3–0.5 FTE | $14K | $32K |
| **Total** | | **$32K** | **$81K** |

**Verification**: low 6 + 12 + 14 = **32** ✓ · high 14 + 35 + 32 = **81** ✓. Expected **$56K**.

> This line is **partly Tier 1 and partly Tier 2** — external counsel is cash, internal committee
> time is not. It is carried in Tier 1 in full, conservatively, because the legal component
> dominates and because splitting a $56K line two ways adds precision the estimate does not have.

### 6.6 The internal resource cost — Tier 2

`GV-007` §7.5 is titled *"Business-side capacity — the constraint nobody has sized"* and ends:
*"That has never been put to the CEO."* `CH-002` §7.2 adds learner time and records that this
document *"does not contain it either."* Both are now sized.

**The commitments, as stated in `06-01` §4 and quantified in `GV-007` §7.5 and `CH-002` §4.6/§7.2:**

| Population | Commitment | Count | Duration | PW low | PW high |
|---|---|---:|---|---:|---:|
| **Super-users** | 30% during UAT, **10% otherwise** | 134 – 201 | 156.5 programme weeks | **2,191** | **3,287** |
| Module business owners | 20% of time | 11 category owners | 156.5 weeks | **344** | **344** |
| Branch champions | 4 h/week during rollout | 51+ branches | ~95 weeks, W1–W5 | **475** | **485** |
| Data owners | 20% during migration | ~10 domains | ~95 weeks, W1–W5 | **190** | **190** |
| **Learner time** — formal training | `CH-002` §7.2: 1,538 – 2,720 person-days | 800+ employees | Per wave | **308** | **544** |
| **OJT supervisor time** | `CH-002` §4.6: 733 – 1,465 supervisor-days | Workshop supervisors, branch and finance managers | Per wave | **147** | **293** |
| **Hypercare floor-walking** — `SV-005` §5.4 pool 3 | `OP-002` §4.4 ratios: 1 walker per 8–15 users, per branch, per cohort | Champion network + branch staff | 56 weeks across 9 waves | **120** | **160** |
| **Total internal draw** | | | | **3,775** | **5,303** |

**Verification** *(regenerated per `PG-M10`)*: low 2,191 + 344 + 475 + 190 + 308 + 147 + 120 =
**3,775** ✓ · high 3,287 + 344 + 485 + 190 + 544 + 293 + 160 = **5,303** ✓. Expected **4,539 PW**.

**Working for the super-user line**, because it is the largest and the least intuitive:
134 × 0.10 × 156.5 = 2,097 PW baseline, plus a UAT uplift of 134 × 0.20 × 3.5 = 94 PW →
**2,191 PW**. At the upper population: 201 × 0.10 × 156.5 = 3,146, plus 201 × 0.20 × 3.5 = 141 →
**3,287 PW**.

**Not added, stated separately**, following `CH-002`'s own treatment: `CH-002` `TPD-06` records
**fourteen roles covering 313–505 people with an `LS-03` obligation and no stated OJT period**. At
the five-day minimum used elsewhere that is a further **313–505 PW**. It is excluded from the total
because the obligation is unspecified rather than unfunded, and including an unspecified obligation
in a total would breach `EM-06`.

**Overlap declared, not double-counted.** `CH-002` §7.3 option C refers to *"142–180 people already
trained by `TR-023`"* as the champion network, and `CH-005` records that their time is itself
unreleased and unfunded. The 51-branch champion line above is the **released-time** commitment from
`06-01` §4; the wider 142–180 network overlaps it and is **not** added again.

| | Low | Expected | High |
|---|---:|---:|---:|
| Internal draw, person-weeks | 3,775 | 4,539 | 5,303 |
| Internal rate (§4.2) | $100 | $150 | $210 |
| **Internal resource cost, 3 years** | **$378K** | **$681K** | **$1,114K** |
| **Internal resource cost, Years 4–5** *(2–4 FTE sustainment plus perpetual refresh)* | **$21K** | **$47K** | **$87K** |

**Verification**: 3,775 × 100 = $377.5K ✓ · 4,539 × 150 = $680.9K ✓ · 5,303 × 210 = $1,113.6K ✓.

> **Read the first row of that table again.** `06-01` §4 commits 134–201 super-users at *"10%
> otherwise"* for a 36-month programme. Applied literally, that single commitment is **2,191–3,287
> person-weeks — comparable to the entire 1,842 PW build.**
>
> There are only two honest readings, and the Company must choose one:
>
> | Reading | Consequence |
> |---|---|
> | **The commitment is real** | The programme consumes 3,775–5,303 internal person-weeks — **24–34 FTE-equivalents sustained for three years**, a 5–7% draw on a 500-person organisation. `RSK-001` is rated **Critical** on exactly this and its mitigation is *"named super-users with time formally protected in their objectives."* **Not one super-user has been named** (`GV-007` §7.5) |
> | **The commitment is aspirational** | Then `CON-12` and `RSK-001`'s statement that *"UAT capacity, not developer capacity, paces the programme"* has no resourcing behind it, and every wave gate's `DoD-13` — *"UAT executed and signed by named business super-users"* — rests on people who do not have the time to do it |
>
> **This is `D-002`, and `GV-007` §7.5 is right that it cannot be taken sensibly without this
> number.** It is now available. Escalated to `GV-005` and to the CEO.

### 6.7 Foreign exchange — `CVA-04`

`GV-008` assumption `A1` records: *"`06-02` converts BDT to USD at **110**. That rate is carried
forward here for comparability and is **not verified**. … an FX move of ±10% changes the ROI by ±10%
without changing either underlying figure. `BM-003` must verify the rate and state the sensitivity."*

**Verified 2026-08-19:**

| Measure | Value | Date |
|---|---:|---|
| USD/BDT spot | **122.70** | 17 August 2026 |
| USD/BDT, 2026 average to date | **122.44** | 2026 YTD |
| USD/BDT, August 2026 high | 123.785 | 5 August 2026 |
| **Model assumption `GV-008` `A1`** | **110.00** | Carried from `06-02` |
| **Variance** | **+11.5%** | |

**Verification**: 122.70 ÷ 110.00 = 1.1155 → **+11.5%** ✓.

> **The assumption is not merely stale; 110 has not been the market rate at any point in 2026.** The
> 2026 average is 122.44 and the August range is 122.70–123.79. This is not an unlucky spot reading
> against a volatile rate — it is a rate that was already superseded when `06-02` was written.

**Which direction it cuts, stated carefully because it is easy to get backwards:**

| | Denominated in | Effect of a weaker taka |
|---|---|---|
| **Benefits** | **BDT** (all `06-02` figures are in BDT lac) | The same BDT benefit converts to **fewer USD**. USD benefit falls by **10.4%** |
| **Costs** | **USD** (RFP §16.2 requires all pricing in USD) | The same USD cost requires **more BDT**. BDT cost rises by **11.5%** |

**Verification**: 110 ÷ 122.70 = 0.8965 → benefit in USD falls **10.4%** ✓.

| Figure | At 110 | **At 122.70** | Source |
|---|---:|---:|---|
| Claimed annual benefit at steady state (876 lac) | $797K | **$714K** | `GV-008` §7.1 |
| **Claimable** benefit under `06-02` §6 (~480 lac) | $436K | **$391K** | `GV-008` §7.1 |
| Five-year cumulative benefit, base case (2,796 lac) | $2,542K | **$2,278K** | `GV-008` §7.3 |

**And a risk-allocation finding.** RFP §16.2 requires all pricing in USD and asks respondents to
state the FX assumption and *"who bears FX risk"* **only where a component is priced in BDT**.
Because the whole response is in USD, **1000FiX bears 100% of the FX risk on a 36-month programme,
in a currency that has moved 11.5% against the model's own assumption.** `CO-003` `SOW-44` proposes
a shared-risk mechanism; §11 option E prices the alternative.

### 6.8 Rate escalation

`GV-008` `CB-01` fixes rates at the approved case's implied rate — a **2026** figure. Under the RFP
§18.1 timetable, contract signature is targeted at **16 April 2027**, kickoff at **3 May 2027**, and
programme closure at **May 2030**. Not one dollar of this programme is spent in 2026.

| Input | Value | Source, verified 2026-08-19 |
|---|---|---|
| Bangladesh general CPI, July 2026, point to point | **8.32%** | BBS, via national press reporting of the release |
| Non-food CPI, July 2026 | **9.28%** | As above — and non-food is the relevant series for salaries |
| Contractual escalation cap after Month 24 | **Bangladesh CPI or 5% p.a., whichever is lower** | RFP §16.2.11 |
| Rates fixed for | **24 months** from contract | RFP §16.2.11 |

**Derivation:**

| Period | Treatment | Uplift |
|---|---|---:|
| 2026 implied rate → April 2027 contract rate | ~8 months of wage inflation at 8.3–9.3% p.a. The vendor prices its **2027** cost base, not the Company's 2026 model | **+5.5%** |
| Months 1–24 (May 2027 – Apr 2029) | Fixed by `CR-01` and §16.2.11 | 0% |
| Months 25–36 (May 2029 – May 2030) | Cap **binds at 5%** because CPI exceeds it | **+5.0%** on the residual |
| Years 4–5 run costs | +5% per year, compounding | +5%, +10.25% |

Applied to the spend profile in `GV-008` §5.2, which front-loads people cost into Months 1–24, the
weighted uplift on people cost is **+5% (low) to +11% (high), expected +7%**.

| | Low | Expected | High |
|---|---:|---:|---:|
| Base — people cost + PMO + hypercare | $1,059K | $1,671K | $2,718K |
| Escalation rate | 5% | 7% | 11% |
| **Escalation** | **$53K** | **$117K** | **$299K** |

**Verification**: base low 859 + 69 + 131 = **1,059** ✓ · expected 1,358 + 136 + 177 = **1,671** ✓ ·
high 2,228 + 267 + 223 = **2,718** ✓ · 1,059 × 0.05 = 53.0 ✓ · 1,671 × 0.07 = 117.0 ✓ ·
2,718 × 0.11 = 299.0 ✓.

> **The 5% cap is favourable to the Company and should be defended in negotiation — but it is not
> free.** With CPI at 8.32% and non-food at 9.28%, a cap of 5% transfers roughly 3–4 points a year of
> wage inflation to the vendor from Month 25. A rational vendor prices that into the **initial**
> rate, which is precisely why the +5.5% pre-contract uplift above is a real cost and not an
> accounting artefact. `CO-002` §7.4 tests for it: a bid whose rate card is at the 2026 implied rate
> has either mispriced its own cost base or intends to recover it through change requests.

---

## 7. The Consolidated Position

### 7.1 Tier 1 — incremental cash cost, Years 1–3

All figures in USD thousands. **Excludes contingency and management reserve, which are `GV-008`
§6's.** Excludes recoverable VAT; includes the non-recoverable residue.

| Line | | Low | Expected | High | Class |
|:--:|---|---:|---:|---:|:--:|
| **A** | People — delivery, 4 work streams (`GV-008` §4.2) | 859 | 1,358 | 2,228 | 2–5 |
| **B** | Programme management, assurance, PMO (§6.3) | 69 | 136 | 267 | 4 |
| **C** | Hypercare — pools 1 + 2, 538 PW (§6.4, `SV-005` §5.5) | 131 | 177 | 223 | 4 |
| **D** | Rate escalation on A + B + C (§6.8) | 53 | 117 | 299 | 3 |
| **E** | Infrastructure — regional, 12 environments (§5.2) | 114 | 195 | 321 | 4 |
| **F** | **`BD-R`** — Bangladesh-resident store (§5.3) | 66 | 114 | 198 | 4 |
| **G** | Third-party API consumption (§5.4) | 41 | 85 | 150 | 3 |
| **H** | L6 commercial components (§5.5) | 13 | 45 | 90 | 3 |
| **I** | Support and maintenance, Years 2–3 (§5.6) | 75 | 120 | 165 | 4 |
| **J** | Change and training delivery (§5.7) | 35 | 52 | 85 | 4 |
| **K** | VAT — non-recoverable residue (§6.1) | 0 | 20 | 50 | 3 |
| **L** | Withholding-tax gross-up exposure (§6.2) | 0 | 83 | 173 | 3 |
| **M** | Vendor management and contract administration (§6.5) | 32 | 56 | 81 | 4 |
| | **Tier 1, Years 1–3** | **1,488** | **2,558** | **4,330** | **5** |

**Verification** *(regenerated from the rows per `PG-M10`)*:
low 859 + 69 + 131 + 53 + 114 + 66 + 41 + 13 + 75 + 35 + 0 + 0 + 32 = **1,488** ✓ ·
expected 1,358 + 136 + 177 + 117 + 195 + 114 + 85 + 45 + 120 + 52 + 20 + 83 + 56 = **2,558** ✓ ·
high 2,228 + 267 + 223 + 299 + 321 + 198 + 150 + 90 + 165 + 85 + 50 + 173 + 81 = **4,330** ✓.

**Reconciliation to `GV-008` §4.4**, because the Board will ask why two documents six days apart
differ by $928K:

| | Low | Expected | High |
|---|---:|---:|---:|
| `GV-008` §4.4 three-year cost baseline | 1,024 | 1,630 | 2,608 |
| Non-people re-derivation (§5.8: 344/611/1,009 less 165/272/380) | +179 | +339 | +629 |
| New lines B + C + D + K + L + M | +285 | +589 | +1,093 |
| **This document, Tier 1, Years 1–3** | **1,488** | **2,558** | **4,330** |

**Verification**: 1,024 + 179 + 285 = **1,488** ✓ · 1,630 + 339 + 589 = **2,558** ✓ ·
2,608 + 629 + 1,093 = **4,330** ✓. Expected delta = **+$928K**, of which **37%** is the non-people
re-derivation `GV-008` asked for and **63%** is lines no document carried.

### 7.2 Tier 1 — Years 4 and 5

The programme has ended. There is no build, no PMO, no hypercare, no training delivery beyond
refresh, and no vendor-management overhead beyond support-contract administration. Non-production
shrinks: `perf`, `sit` and `migration-staging` are no longer needed continuously, so the regional
multiplier falls from 2.20–3.34 to **1.80–2.50**, expected 2.10, against a production run rate at
Wave 9 steady state of **$48K–$70K per year** (`02-05` §8.2: $4,000–$5,800/month).

| Line | Year 4 low | Year 4 exp | Year 4 high |
|---|---:|---:|---:|
| Infrastructure — regional, run state | 86 | 124 | 175 |
| `BD-R` | 22 | 38 | 66 |
| Third-party APIs | 23 | 40 | 63 |
| L6 commercial | 4 | 17 | 35 |
| Support and maintenance, 67 modules | 56 | 90 | 123 |
| Training refresh (`CH-002` `TPD-19`) | 6 | 12 | 20 |
| **Sub-total, before escalation** | **197** | **321** | **482** |
| Escalation (+5% Year 4, +10.25% Year 5) | | | |
| **Year 4** | **207** | **337** | **506** |
| **Year 5** | **217** | **354** | **531** |
| **Years 4–5 total** | **424** | **691** | **1,037** |

**Verification**: low 86 + 22 + 23 + 4 + 56 + 6 = **197** ✓ · expected 124 + 38 + 40 + 17 + 90 + 12
= **321** ✓ · high 175 + 66 + 63 + 35 + 123 + 20 = **482** ✓ ·
197 × 1.05 = 206.9 ✓ · 197 × 1.1025 = 217.2 ✓ · 207 + 217 = **424** ✓ ·
321 × 1.05 = 337.1 ✓ · 321 × 1.1025 = 353.9 ✓ · 337 + 354 = **691** ✓ ·
482 × 1.05 = 506.1 ✓ · 482 × 1.1025 = 531.4 ✓ · 506 + 531 = **1,037** ✓.

> **The steady-state run rate is $207K–$531K a year, expected $337K.** That is the number nobody in
> the estate has ever computed, and it is the number that persists. It is **4.7× the $71K a year**
> that `02-05` §8.2 would imply for a reader who took the published progression as a total.

### 7.3 The two tiers, five years

| | Low | Expected | High |
|---|---:|---:|---:|
| Tier 1, Years 1–3 (§7.1) | 1,488 | 2,558 | 4,330 |
| Tier 1, Years 4–5 (§7.2) | 424 | 691 | 1,037 |
| **TIER 1 — five-year incremental cash TCO** | **1,912** | **3,249** | **5,367** |
| Internal resource cost, Years 1–3 (§6.6) | 378 | 681 | 1,114 |
| Internal resource cost, Years 4–5 (§6.6) | 21 | 47 | 87 |
| **TIER 2 — five-year full economic TCO** | **2,311** | **3,977** | **6,568** |

**Verification**: 1,488 + 424 = **1,912** ✓ · 2,558 + 691 = **3,249** ✓ · 4,330 + 1,037 =
**5,367** ✓ · 1,912 + 378 + 21 = **2,311** ✓ · 3,249 + 681 + 47 = **3,977** ✓ ·
5,367 + 1,114 + 87 = **6,568** ✓.

**Three-year figures, for comparability with every existing estate figure:**

| | Low | Expected | High |
|---|---:|---:|---:|
| **Tier 1, three-year** | **$1,488K** | **$2,558K** | **$4,330K** |
| **Tier 2, three-year** | **$1,866K** | **$3,239K** | **$5,444K** |

**Verification**: 1,488 + 378 = **1,866** ✓ · 2,558 + 681 = **3,239** ✓ · 4,330 + 1,114 =
**5,444** ✓.

**The bridge between the tiers — the backfill decision.** Tier 2 minus Tier 1 is internal salaried
time already being paid for. It becomes **cash** only if the Company backfills rather than absorbs.

| Backfill policy | Cash effect | Operational effect |
|---|---|---|
| **Absorb** — no backfill | $0 | A **5–7% organisation-wide productivity draw**, concentrated in UAT and training windows. `CH-001` §8's saturation model is where this lands |
| **Backfill 30% of the draw** | **+$204K** over three years | The most likely landing point: backfill the operational roles that cannot absorb (counter staff, technicians) and absorb the managerial ones |
| Backfill in full | +$681K | Not credible for a 500-person organisation in a 10–12 month hiring market |

**Verification**: 681 × 0.30 = **$204K** ✓.

> **`TCO-08` — the backfill decision is taken explicitly, at the Board, before Wave 1.** Taken
> implicitly, it is taken by 800 individual supervisors deciding whether to release their people,
> and the answer will be no. This is the same mechanism `CH-005` records for the champion network
> and `RSK-001` rates Critical for super-users.

### 7.4 Decommissioning and exit

ISO 15686-5's disposal category, translated. Not costed as a line in §7.1 because it falls outside
the five-year period, but stated because a TCO that ignores exit is the reason exit is expensive.

| Obligation | Source | Shape |
|---|---|---|
| Every L6 component has a **documented exit** — what happens to the data and the capability | `AR-013` `L6-05` | The **qualified e-signature** provider is the hard one: it holds evidentiary records for contracts with a multi-year life, and *"what happens to the signed envelopes if we change provider"* must be answered **before** signing |
| Full data export in **open, documented formats, available at any time** | RFP §19.1(5) | A build obligation, not an exit cost — if it is built |
| **Source code, configuration and IaC delivered continuously** to a Company-controlled repository | RFP §19.1(6), MQ-08 | The single most effective exit provision in the RFP. It converts vendor exit from a recovery project into a personnel change |
| 90 days' transition assistance on termination | RFP §19.2 | Priced by the respondent; `CO-002` §7.3 scores it |
| `BD-R` exit — *"what it takes to leave, and how long the data takes to move"* | `PE-001` `SEL-05` | Must be answered **before** the facility is entered |

### 7.5 What is still not in this model

Stated so the position is not read as complete, per `GV-007` §7.3's instruction that *"`CO-005` must
state that the TCO is bounded below, not bounded."*

| Excluded | Why | Owner | Shape |
|---|---|---|---|
| **Data migration execution** beyond the `MG-*` documents | 48 sources unprofiled; unknowable until `MG-002` completes | Migration lead | Unknown. `MG-002` is the precondition |
| **Test execution** effort | `QA-001`…`QA-011` now exist; the automation ratio is decided but execution effort has not been re-derived against them | QA Lead | Material. Referred to `GV-007` for the next re-estimate |
| **Payment gateway fees**, currently netted against revenue | A function of gross merchandise value, not of the system | `BM-003` | Rises with marketplace success. `TCO-Q-05` |
| **Platform upgrade** beyond Odoo 19.0's support horizon (~Sept 2028) | `ADR-027` / `D-025` not taken; no extended-support path for CE | CTO | Falls inside Year 2–3 of ownership and is not in any budget |
| **The fifth L6 component** if the MinIO replacement is commercial | `BEA-16`; decision at `W0` | Chief Architect / CFO | `TCO-Q-06` |
| **`BD-R` capacity expansion** if the `DEP-31` legal opinion widens the residency-classified field set | RFP `OPT-12` already prices it as an option | Legal Counsel | Bounded by `OPT-12` |
| The **14 unspecified-OJT roles** at the five-day minimum | `CH-002` `TPD-06` — unspecified, not unfunded | HR Director | +313–505 PW = +$31K–$106K |
| **The device estate** — `P02` handsets for 215–430 technicians, classroom devices, rider and field-auditor devices | **`CO-006` §6 raises this as `CVA-19`.** Two of five populations have no quantity anywhere in the estate, and the regional hub count is unstated (`CVA-20`) | IT with Operations | **Material and unquantifiable today.** `CO-006` `PPP-16` and `PPP-Q-09` require a line here once the quantities exist |

> **`TCO-09` — this model is bounded below.** Seven named exclusions all point upward and none points
> down. **A reader who needs a single sentence should read the expected case as a floor with a
> credible upper half, not as a midpoint between equally likely outcomes.**

---

## 8. Sensitivity

Single-variable sensitivity on the Tier 1 five-year expected case of **$3,249K**.

| # | Variable | Movement tested | Effect on Tier 1, 5-yr | Direction |
|:--:|---|---|---:|:--:|
| 1 | **Build effort** — `GV-007`'s band | 1,658 → 2,303 PW | **−$272K / +$460K** | Both |
| 2 | **Screen count** — the class 5 driver | 660 → 1,500 screens | **−$53K / +$109K** | Both |
| 3 | **FX** | 110 → 122.70 | **$0 on cost**; −10.4% on USD benefit | Benefit only |
| 4 | **Withholding gross-up clause** | Present → absent | **$0 / +$83K** | Up |
| 5 | **VAT rebate** | Full recovery → 15% lost | **$0 / +$50K** | Up |
| 6 | **Offshore share** | 40% → 70% | **−$45K / +$90K** | Both |
| 7 | **Escalation** | 5% → 11% | **−$64K / +$188K** | Both |
| 8 | **RMM agent (`D-18`)** at 1,000 endpoints | Not adopted → adopted | **$0 / +$180K over 5 yrs** | Up |
| 9 | **Hypercare** (`CVA-06`) — `SV-005` §5.5's 538 Tier-1 PW at the rate band | $131K → $223K | **−$46K / +$46K** | Both |
| 10 | **`BD-R` facility tier** | Tier III → Tier IV + dedicated HSM | **$0 / +$140K over 5 yrs** | Up |
| 11 | **Backfill policy** | Absorb → 30% backfill | **$0 / +$204K** | Up |
| 12 | **MinIO replacement** is commercial | OSS → managed | **$0 / +$60K–$150K over 5 yrs** | Up |

> **Eight of the twelve variables can only move the number up.** That is the arithmetic signature of
> a model built by adding omitted lines to an existing figure, and it is why §7.5 says the expected
> case is a floor. The four two-directional variables are the effort bands, which `GV-007` already
> holds at class 2–5, and the commercial choices the Company controls.

**The two variables that matter most are not on this list**, because they are scope decisions rather
than cost variables: whether Waves 5–9 proceed (`D-017`), and whether the `RQ-003` fit-gap reduces
build scope. `GV-008` §7.3 notes that nobody has determined what Odoo 19 CE and OCA already deliver.
**That is the only variable in the programme with a plausible seven-figure downside on cost**, and
it is unexamined.

---

## 9. Reconciliation

### 9.1 Every cost figure the estate carries

| Figure | Source | Basis | Disposition | vs Tier 1 3-yr expected ($2,558K) |
|---|---|---|---|---:|
| $182K – $342K | `SB-1`, March 2026 | 11 modules | **Superseded** | — |
| **$455K – $780K** | `00-02` §6.1 — **the figure the Board holds** | 834 PW, 30 modules | **Superseded** | **4.1× the midpoint** |
| $455K – **$850K** | `06-02` §3.3 | Same baseline, **different upper bound** | **Superseded**; `PGD-A2-09` | 3.9× the midpoint |
| $620K – $1,050K | `00-02` §2 provisional | ~1,302 PW | **Superseded** | 3.1× the midpoint |
| **$690K – $1,150K** | **RFP §16.1 — issued to the market 13 August 2026** | 1,513 PW, module build only | ⚠ **LIVE IN AN OPEN PROCUREMENT** | **2.8× the midpoint** |
| ~$690K – $1,150K | `00-07` H2-08 · `AR-013` §7 | 1,513 PW | **Superseded** | 2.8× the midpoint |
| $1,024K – $2,608K, exp **$1,630K** | `GV-008` §4.4 | 3,022 PW, **3-year programme cost baseline** | **Current, for its purpose** | **1.57×** — the difference is the twelve lines a budget baseline does not carry |
| **$1,488K – $4,330K, exp $2,558K** | **This document — Tier 1, 3-year** | `GV-008` + re-derived non-people + tax + FX + escalation + hypercare + PMO | **Current** | — |
| **$1,912K – $5,367K, exp $3,249K** | **This document — Tier 1, 5-year** | + Years 4–5 run | **Current** | — |
| **$2,311K – $6,568K, exp $3,977K** | **This document — Tier 2, 5-year** | + internal resource cost | **Current** | — |

> **Eight figures have circulated. Three are current and they measure three different things.**
> `GV-008` measures what the programme may spend over three years. This document's Tier 1 measures
> what the Company pays over five. Tier 2 measures what it costs. **A reader who quotes one of them
> without saying which has said nothing**, and `TCO-10` requires the tier and horizon to be stated
> with every figure.

### 9.2 Is `H-02` confirmed, finally?

`H-02` predicted the implementation line was understated by 70–80% and instructed that the TCO not
be presented to the Board as final.

| Test | Approved | This document | Understatement |
|---|---:|---:|---:|
| 3-year TCO vs the figure the Board holds ($455K–$780K, mid $618K) | $618K | **$2,558K** | **4.1×** |
| 3-year TCO vs the **live RFP envelope** ($690K–$1,150K, mid $920K) | $920K | **$2,558K** | **2.8×** |
| 5-year Tier 1 vs the Board's 3-year figure, like-for-unlike | $618K | **$3,249K** | 5.3× |
| Full economic 5-year vs the Board's figure | $618K | **$3,977K** | 6.4× |

> **`H-02` is confirmed for the third time and was conservative each time.** `00-06` measured one
> work stream. `GV-008` §4.6 measured four and found 2.2×–3.3×. This document measures four work
> streams plus twelve absent lines and finds **4.1×**. The progression is not evidence that the
> auditors were wrong; it is evidence that **each measurement was bounded by what had been written
> down at the time**, which is precisely the failure mode `EM-04` and `RG-08` were created to stop.

### 9.3 The 5-year comparison the RFP demands and the Company cannot make

RFP §17.1 Stage 6 is *"3-year and 5-year TCO analysis"*. RFP §16.2.10 requires respondents to state
Year 4 and Year 5 run rates, mandatory for alternative-architecture proposals under `ALT-05`.

**Before this document, the Company had no five-year figure of its own.** It would have received
five-year respondent submissions in a Stage 6 commercial evaluation and had nothing to evaluate them
against. §7.2's run-rate table is now the yardstick, and `CO-002` §7 applies it.

### 9.4 `CVA-02` — the live RFP carries a superseded envelope

**This is the most time-critical item in Category 14 and it is a procurement-integrity matter, not
merely a cost one.**

| Date | Event |
|---|---|
| **13 August 2026** | RFP v2.0 issued. §16.1 publishes **$690K–$1,150K**; §17.2 criterion 7 (8% of the score) requires *"an independent capacity analysis against **1,513 PW**"*; §16.2.1 sets the effort basis; §20.3.1 discloses the 1,513 PW variance as `D-14` |
| **18 August 2026** | `GV-007` issued. **1,513 PW is superseded by 1,842 PW build / 3,022 PW programme** |
| **19 August 2026** | `GV-008` issued. **The envelope is superseded by $1,024K–$2,608K** |
| **17 September 2026** | ⚠ **Written-question deadline.** The last date on which the market can be told, through the RFP's own machinery |
| 30 October 2026 | Proposal submission deadline |
| 16 April 2027 | Contract signature target |

**Four consequences, each independently sufficient to require an addendum:**

| # | Consequence |
|:--:|---|
| 1 | **The scoring rubric rewards the wrong answer.** §17.2 criterion 7 awards 8% for a capacity analysis *against 1,513 PW*. A respondent who correctly analyses against 3,022 PW is scored against a rubric keyed to a superseded figure. §17.5 item 3 marks down *"accepting the published wave plan without an independent capacity analysis"* — so the RFP simultaneously demands independent analysis and fixes its benchmark |
| 2 | **Adverse selection.** §16.1 warns that *"a bid materially below the envelope will be scrutinised for scope understanding, not rewarded for price."* The envelope's **upper** bound ($1,150K) is now below this document's three-year expected case ($2,558K). A respondent who prices the work correctly is **outside the envelope and must justify the variance**; a respondent who prices it optimistically sits comfortably inside. **The instrument as written penalises the accurate bidder** |
| 3 | **`CR-01` and `CR-02` become unarbitrable.** Prices are *"firm and fixed for the wave to which they relate"* and re-baselined at wave start, with variance beyond **±10%** requiring Steering Committee approval. A bid priced on 1,513 PW will breach ±10% at **every** wave, converting a fixed-price contract into a continuous change-request negotiation — which is exactly what `CO-003` exists to prevent |
| 4 | **Award challenge exposure.** §18.5 reserves the Company's rights, but a disappointed respondent who priced to the published envelope has a straightforward complaint: the Company evaluated against a basis it had internally superseded and did not disclose. `CO-002` §3 records the defence; the addendum removes the need for one |

**Recommended action — `CO-005-D-05`:**

| # | Action | Owner | By |
|:--:|---|---|---|
| 1 | Issue **RFP Addendum 1** restating §16.1's envelope, §16.2.1's effort basis, §17.2 criterion 7's benchmark and §20.3.1's disclosure onto the `GV-007` / `GV-008` / `CO-005` basis | Head of Procurement | **Before 17 September 2026** |
| 2 | Extend the submission deadline by the notice period §18.1 requires, if the addendum materially changes the pricing basis — which it does | Head of Procurement | With Addendum 1 |
| 3 | Restate `OPT-01`…`OPT-12` so descope options are priced against the correct base | Head of Procurement | With Addendum 1 |
| 4 | Escalate to `GV-005` as a **Critical** risk and to `GV-003` as a decision, since amending an issued RFP is a Steering Committee matter | Programme Director | **Immediately** |

> **The alternative to an addendum is not "do nothing"; it is "receive bids the Company cannot
> accept."** A proposal priced to a superseded envelope is not a proposal the Company can sign
> against a budget baseline of $1,024K–$2,608K, and discovering that at Stage 6 in February 2027
> costs the programme its entire procurement timetable — six months, and a kickoff that slips from
> May 2027 into the following fiscal year.

---

## 10. The Return Position, Restated at the Verified Rate

### 10.1 Benefit, as claimed and as claimable, at 122.70

| Basis | BDT lac / yr | At 110 | **At 122.70** |
|---|---:|---:|---:|
| Claimed annual benefit at steady state, base case (`06-02` §3.1) | 876 | $797K | **$714K** |
| Benefit whose KPI has **no measured baseline** (`RP-02`: 44 of 95) | ~396 | $360K | **$323K** |
| **Claimable** under `06-02` §6 — *"a KPI without a baseline cannot claim a benefit"* | ~480 | $436K | **$391K** |

### 10.2 Payback

Against `06-02` §3.2's curve read as **annual** (`PGD-A2-10`; the row notes settle it), base case:
Year 1: 45 lac · Year 2: 310 · Year 3: 645 · Year 4: 876 · Year 5: 920.

| Year | Annual (lac) | At 122.70 | Cumulative |
|:--:|---:|---:|---:|
| 1 | 45 | $36.7K | $36.7K |
| 2 | 310 | $252.6K | $289.3K |
| 3 | 645 | $525.7K | **$815.0K** |
| 4 | 876 | $714.0K | **$1,529.0K** |
| 5 | 920 | $749.8K | **$2,278.8K** |

**Verification**: 45 ÷ 122.70 × 100 = $36.7K ✓ · 310 ÷ 122.70 × 100 = $252.6K ✓ ·
645 ÷ 122.70 × 100 = $525.7K ✓ · 876 ÷ 122.70 × 100 = $714.0K ✓ · 920 ÷ 122.70 × 100 = $749.8K ✓.

| Cost basis | At FX 110 (`GV-008` §7.2) | **At FX 122.70** |
|---|---|---|
| `GV-008` expected, $1,630K | Year 4, ~month 48 | **Year 5, ~month 50** |
| **This document, Tier 1 3-year, $2,558K** | — | **Year 6** — cumulative benefit reaches $2,279K at the end of Year 5 and does not cover it |
| **Tier 1 5-year, $3,249K** | — | **Beyond Year 6** |
| Tier 1 3-year, **claimable benefit only** (~55%) | — | **Beyond Year 8** |

**Verification of the `GV-008` restatement**: cumulative to end of Year 4 is $1,529.0K, short of
$1,630K by **$100.9K**; Year 5's annual benefit is $749.8K, so 100.9 ÷ 749.8 = **0.135 of a year** =
1.6 months → payback at approximately **month 49.6** ✓, against approximately **month 47** at FX 110.

> **The FX correction alone moves `GV-008`'s payback by two months and across a year boundary — from
> "Year 4" to "Year 5".** That is a change in the sentence the Board will remember, produced by
> correcting an assumption the estate itself marked *"not verified"*.
>
> **`BM-003` must not simply adopt these figures.** Two problems remain unresolved and both are
> `BM-003`'s: the annual-versus-cumulative label defect (`PGD-A2-10`), which is worth 2.2×–3.3× on
> the three-year benefit and is **larger than everything in this document**; and whether the FX rate
> should be a spot rate, a forward curve, or a hedged rate under `CO-003` `SOW-44`.

### 10.3 Is the programme still worth doing?

Stated because a restatement that reports only the downside is as misleading as the figure it
replaces, and because `GV-008` §7.3 set the precedent.

| Point | Evidence |
|---|---|
| **The benefit case is not disputed by any audit.** Four audits have qualified the cost side; none has qualified the benefit side | `00-06` §7 |
| **Five-year cumulative benefit at the verified rate is $2,279K** against a Tier 1 five-year cost of $3,249K — negative at five years, and positive on any horizon that includes the years the benefit compounds at the Year-5 run rate of ~$750K a year | §10.2 |
| **The programme can legitimately stop at the Wave 4 gate** with the whole v1.0 commitment delivered | `GV-001` §7.3; `D-017`; `GV-008` option B |
| **~BDT 396 lac of benefit is recoverable, not lost** — by measuring baselines before the process changes | `BM-002`; `CC-09` |
| **`RQ-003`'s fit-gap is the largest untested cost lever in the programme** | `GV-007` §9.2 trigger 2; §8 above |
| **$928K of the increase over `GV-008` is arithmetic, not deterioration.** Nothing got worse between 19 August and this document; lines that were always being incurred became visible | §7.1 |

> **The honest summary for the Board is one sentence:** the programme's benefit case is intact and
> unchallenged, its cost is roughly four times what the approved case says at three years, and the
> decision `D-014` requires is not *"is this worth doing"* but *"how much of it do we authorise
> before the Wave 4 gate tells us whether the delivery factor is real."*

---

## 11. The Options, Priced

`GV-008` §9 put four options to the Board on the three-year programme baseline. They are re-priced
here on the **five-year Tier 1** basis, and a fifth is added that `GV-008` could not see because it
is commercial rather than budgetary.

| # | Option | 5-yr Tier 1 | Delivers | Consequence |
|:--:|---|---:|---|---|
| **A** | **Fund the restated position** | **$3,249K** | All 67 modules, 12 portals, full content estate, full engineering definition | Payback beyond Year 6. Requires +15.8 FTE (`GV-007` §7.4) and the `GV-004` §7.2 re-shaping |
| **B** | **Fund Tranche 0 + Tranche 1; re-decide at the Wave 4 gate** | **~$1,790K** to the gate, plus run cost | The complete v1.0 committed scope by Month 18 | **Recommended, as in `GV-008` §9** — and this document strengthens the case: at $2,558K over three years the Wave 4 decision point is worth proportionately more than it was at $1,630K |
| **C** | **Descope Categories D, F, I or J** | **~$3,000K** | 47–63 modules | `RSK-036`. Removes 349 PW. **`CC-05`: each removal must state the benefit forgone** — Category D alone carries BDT 125 lac |
| **D** | **Defer Waves 8 and 9** | **~$3,055K** | 30 months of delivery | `CON-01`. Forgoes BDT 52 lac and second-country readiness (`BO-18`). **Note: deferral does not reduce the Years 4–5 run rate**, which is the larger part of the five-year difference |
| **E** | **Re-let the procurement on the corrected basis** | **$3,249K, with a defensible contract** | The same scope | **Not an alternative to A–D; a precondition for all of them.** §9.4. The addendum route preserves the timetable; a re-let costs about six months |

> **The five-year view changes the ranking of C and D, and that is the point of computing it.**
> On the three-year programme baseline, deferring Waves 8–9 (option D) looked comparable to
> descoping categories (option C). Over five years it does not: **a deferred wave still arrives and
> still costs, while a descoped category never does** — but a descoped category also never earns.
> `CC-05` exists so that trade is made explicitly.

---

## 12. Governing Rules

| # | Rule |
|---|---|
| **`TCO-01`** | The analysis period is **five years** from kickoff. Years 4–5 are reported **separately** from Years 1–3 and never blended |
| **`TCO-02`** | Effort is taken from `GV-007` §7.1 unchanged. **This document does not re-estimate effort.** A disagreement is raised to `GV-007`, not resolved here |
| **`TCO-03`** | Rates are `GV-008` §3.2's, unchanged. **Every difference between this document and `GV-008` is attributable to a line, never to a re-rating** |
| **`TCO-04`** | A non-people line is **re-derived from a counted driver with a stated multiplier**, never substituted with a new absolute figure |
| **`TCO-05`** | A cost the Company will incur is **in the model with an estimate class**, not excluded for being imprecise. `EM-06` governs budget lines; this rule governs TCO lines |
| **`TCO-06`** | The model's estimate class is the class of its **worst** input (`EM-05`). It is currently **5** |
| **`TCO-07`** | Every figure states whether it is **VAT-inclusive or exclusive**. A total that does not is not a total |
| **`TCO-08`** | The **backfill decision** is taken explicitly at the Board before Wave 1 |
| **`TCO-09`** | The model is **bounded below**. Every published quotation of it carries that qualification |
| **`TCO-10`** | Every quoted figure states its **tier** and its **horizon**. *"The TCO is $X"* is an incomplete statement in this estate and will be treated as an error |
| **`TCO-11`** | The model is **re-baselined at every wave gate** (`GV-009`), and the re-baseline states which estimate classes migrated and how the band narrowed — mirroring `GV-008` `CB-06` |
| **`TCO-12`** | **Commitment, not just spend, is tracked** (`GV-008` `CB-09`). A signed L6 subscription is committed money for its full term, not its first month |
| **`TCO-13`** | **Every per-unit metric is modelled at 5× projected volume before signing** (`AR-013` `L6-02`) and the modelled figure, not the projected one, enters the high case |
| **`TCO-14`** | **Both cost-per-transaction measures are reported together, monthly** (`PE-006` `PE-006-D-04`) — infrastructure cost per order, which falls with scale, and third-party cost per order, which rises |
| **`TCO-15`** | A **new L6 component** requires Design Authority and CFO approval (`AR-013` `L6-04`) **and** a five-year entry in this model before it is signed |

---

## 13. Unit Economics

`PE-006` §8.3 defines the two measures and rules that both are reported together. This document
supplies their five-year shape so the trend has a baseline.

| Measure | Direction with scale | Why it matters commercially |
|---|---|---|
| **Infrastructure cost per service order** | **Falls** — fixed platform cost spread over more orders | A *rise* signals inefficiency, not growth |
| **Third-party cost per service order** | **Rises** — SMS, WhatsApp, Maps, KYC and e-signature are per-use | This is the line that makes marketplace growth less profitable than it looks |
| **Total cost per order** | Depends which dominates | The figure `BM-003` needs for the margin model |

> **`PE-006-D-04` and `TCO-14` exist because reporting only the first flatters the picture as volume
> grows.** At the §7.2 run rate, infrastructure is $124K–$175K a year against third-party API
> consumption of $40K–$63K a year and rising with volume. **By Year 5 the two lines are converging**,
> and the crossover — after which growth costs more per order than it saves — is a commercial event
> the Board should see coming rather than discover.

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CO-005-D-01` | Whether to include lines `GV-008-D-02` excluded under `EM-06` | Exclude and declare, as `GV-008` did · **Include with an estimate class** | **Include with a class** | A budget line must be individually defensible; a TCO line must be individually honest. An omission is not honesty | The two documents differ by $871K expected and §7.1 reconciles the difference line by line |
| `CO-005-D-02` | Whether to include contingency and management reserve | Include, for a fundable total · **Exclude, cross-referenced to `GV-008` §6** | **Exclude** | A TCO with contingency inside it is not comparable to a bid, and `GV-008` already carries them. Including both would double-count $217K | §7 is a cost model, not a funding request. `GV-008` §5 remains the drawdown authority |
| `CO-005-D-03` | Horizon | 3 years, for comparability · **5 years** · 7–10 years | **5 years** | RFP §16.2.10 already requires respondents to state Years 4–5; the Company must be able to evaluate what it asked for. Beyond 5 years the model is dominated by an untaken upgrade decision | The steady-state run rate — $337K a year expected — becomes visible for the first time |
| `CO-005-D-04` | Whether to publish one TCO or two tiers | One number, simpler · **Two tiers, stated separately** | **Two tiers** | Tier 1 understates what the programme costs; Tier 2 overstates what it costs in cash. Publishing either alone is an argument, not a measurement | `TCO-10`: every quotation must state its tier. The backfill decision (`TCO-08`) becomes explicit |
| `CO-005-D-05` | What to do about the live RFP envelope | Let the procurement run and correct at negotiation · Re-let · **Issue Addendum 1 before 17 September 2026** | **Addendum 1** | The written-question deadline is the last date the RFP's own machinery can carry the correction. Correcting at negotiation means evaluating bids on a basis the Company knew was wrong | §9.4. Escalated to `GV-003` as a decision and `GV-005` as a Critical risk |
| `CO-005-D-06` | How to treat the non-people lines `GV-008` carried | Substitute new absolute figures · **Keep the published base and derive a multiplier from a counted driver** | **Multiplier from a counted driver** | A new absolute figure would have no better provenance than the one it replaced. A multiplier is auditable: the driver is counted and the judgement is visible | `TCO-04`. §5.2's 2.20×–3.34× is re-performable from `PE-002` §5 |
| `CO-005-D-07` | Whether to carry the withholding gross-up as a cost | Assume the clause will be negotiated · **Carry the exposure until the clause exists** | **Carry it** | The clause does not exist at the date of issue. A model that assumes a favourable negotiation outcome is a forecast of success, not an estimate | $83K expected in line L, removable to zero the day `CO-003` `SOW-42` is agreed |
| `CO-005-D-08` | Whether to verify the FX assumption or carry it for comparability | Carry 110, as `GV-008` did · **Verify and restate** | **Verify and restate** | `GV-008` `A1` explicitly asked for verification and `PG-M4` requires it. 110 has not been the market rate at any point in 2026 | `CVA-04`; §10's return position moves; `BM-003` inherits a verified rate rather than an assumption |
| `CO-005-D-09` | Whether to size the internal draw when the commitment percentages are unvalidated | Leave it to `GV-007` §7.5's FTE statement · **Convert to person-weeks and cost it at class 5** | **Convert and cost it** | `CH-002` `TPD-14` requires learner time to be costed and named this document as failing to. An unvalidated commitment that is costed becomes a decision; uncosted it stays an assumption | §6.6's 3,655–5,143 PW. Escalated to the CEO and `D-002` |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `TCO-Q-01` | What is the **actual loaded cost per grade** for the internal populations in §6.6, from the `M21` payroll data? | HR Director | **Before the Board paper** | The Tier 2 figure's class; §7.3 |
| `TCO-Q-02` | **Is input VAT fully recoverable** on this contract, and what proportion of 1000FiX output is exempt or zero-rated for apportionment? | CFO with Legal Counsel | **Before contract signature** | §6.1; line K; the `GV-008` §5 drawdown |
| `TCO-Q-03` | **Will the winning respondent be resident, non-resident, or a mixed structure**, and does a double-taxation agreement apply? | Head of Procurement | Stage 6, February 2027 | §6.2; the gross-up clause `SOW-42`; line L |
| `TCO-Q-04` | **What is the `BD-R` facility tier and key-custody model** — colocation with a dedicated HSM, or an in-country managed KMS? | CTO with Chief Architect | **W0** | §5.3's band, which is 3× wide because of this question alone |
| `TCO-Q-05` | Where do **payment gateway fees** appear, given `02-05` §8.3 nets them against revenue and ISO 15686-5 requires costs to be stated? | CFO with `BM-003` | W2 | The marketplace margin model |
| `TCO-Q-06` | **Is the MinIO replacement open-source or commercial** (`BEA-16`), and if commercial, does it become the fifth L6 component under `L6-04`? | Chief Architect with CFO | **W0 — blocking Wave 1** | §5.5; `TCO-15`; `CO-006` |
| `TCO-Q-07` | **Is hypercare 4 weeks or 4–8 weeks** (`CVA-06`), and does the clock run from first or last tranche? | Service Manager | W1 | §6.4's band; `SV-005`; `CO-003`'s payment milestones |
| `TCO-Q-08` | **What is the backfill policy** (`TCO-08`)? | CEO with the Board | **Before Wave 1** | §7.3; `CH-001` §8 saturation; `RSK-001` |
| `TCO-Q-09` | **Has Addendum 1 been issued** (`CO-005-D-05`)? | Head of Procurement | **17 September 2026** | The entire procurement's defensibility |
| `TCO-Q-10` | What does **test execution** cost against `QA-001`…`QA-011`, now that they exist? | QA Lead | W1 | §7.5's exclusion list; the next `GV-007` re-estimate |

> An open question with no owner and no needed-by date is not an open question — it is an unrecorded
> risk. All ten are escalated to `GV-005` RAID at issue.

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every one of the five non-people lines `GV-008` §4.3 carried with a caveat is **re-derived from a `PE-*` document that exists**, with the driver counted and the multiplier shown | §5.2–§5.7; `GV-008-D-03` closed |
| `AC-02` | **`BD-R` is priced**, closing `GV-008` `Q-03`, from `PE-001` §3.4's five named components | §5.3 |
| `AC-03` | Every total is **regenerated from its own rows** and the arithmetic is shown inline, per `PG-M10` | §5.2, §5.5, §5.8, §6.4, §6.6, §6.8, §7.1, §7.2, §7.3, §10.2 |
| `AC-04` | Every line carries an **estimate class**, and the document's class is the class of its worst input | §4.3, §7.1; `TCO-06` |
| `AC-05` | The **tax, FX and escalation** positions are stated with **verified** external sources and a `verified_on` date, per `PG-M4` | §6.1, §6.2, §6.7, §6.8; front matter |
| `AC-06` | The **internal resource cost** is stated and reported alongside delivery cost, closing `CH-002` `TPD-14` | §6.6, §7.3 |
| `AC-07` | **Every cost figure circulating in the estate** is placed in one reconciliation table with its basis and disposition | §9.1 |
| `AC-08` | The **five-year** run rate exists, so RFP §17.1 Stage 6's five-year commercial evaluation has a yardstick | §7.2, §9.3 |
| `AC-09` | The boundary against `GV-008` is stated **before** any number appears, and the two documents reconcile line by line | §3.1, §7.1 |
| `AC-10` | What is **not** in the model is listed, and the model is declared **bounded below** per `GV-007` §7.3's instruction | §7.5; `TCO-09` |
| `AC-11` | `CVA-02` is raised with a **dated, owned action** before the RFP's own written-question deadline | §9.4; `CO-005-D-05`; `TCO-Q-09` |
| `AC-12` | The local rule prefix `TCO-nn` was **verified to zero occurrences** workspace-wide before allocation, and the `CO-nn` collision is recorded | Header note; `CVA-01` |

**Definition of done.** This document is complete when every acceptance criterion above is met, its
`PGD-000` status is updated with a fresh enumeration date, `TCO-Q-01` through `TCO-Q-04` are
answered or formally accepted as open by the approver, and the Board has taken `D-014` against it.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-007` | Supplies the effort position this document prices. `TCO-02` forbids re-estimating it |
| Upstream | `GV-008` | **Names this document as its successor** for the non-people lines (`GV-008-D-03`) and poses `Q-03` |
| Upstream | `PE-001`, `PE-002`, `PE-006`, `PE-007` | Supply the infrastructure drivers §5 prices. `PE-006-F-07` and `PE-002-F-04` refer their numbers here |
| Upstream | `AR-013`, `BE-007` | The L6 register, the licence watch, `L6-02`'s 5× rule, and the MinIO currency finding |
| Upstream | `CH-002` | Learner time, OJT supervisor time and `TPD-14`'s costing obligation |
| Upstream | `SC-007` | `SC-007-D-01` makes `BD-R` a Year 1 cost |
| Downstream | `CO-002` | Evaluates bids against this model; §7.2's run rate is the Stage 6 yardstick |
| Downstream | `CO-003` | `SOW-42` (no gross-up) and `SOW-44` (FX) remove $83K of exposure this model currently carries |
| Downstream | `CO-004` | Owns the licence obligations §5.5 and §7.4 cost |
| Downstream | `CO-006` | Procures what §5 prices, including the learner devices `CH-002` §7.1 assigns to it |
| Downstream | `BM-003` | Inherits the verified FX rate and the restated payback; owns `PGD-A2-10` |
| Downstream | `GV-008` | Must absorb §6.1's VAT cash requirement into the §5 drawdown schedule |
| Downstream | `GV-004`, `GV-007` | §6.4's 270 PW of hypercare is a capacity input, not only a cost |
| Lateral | `GV-005` | Ten open questions and `CVA-02` escalated at issue |
| Lateral | `GV-003` | `D-014` is decided against this document; `CO-005-D-05` requires a new `D-nnn` |
| Lateral | `../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` | §16.1, §16.2, §17.1, §17.2, §18.1, §20.3.1 — the instrument §9.4 recommends amending |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` | §8's production progression, re-derived here rather than replaced |

---

## 18. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
`./_CATEGORY_OVERVIEW.md` · `./CO-002_Vendor_Evaluation_and_Selection_Report.md` ·
`./CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md` ·
`./CO-004_Licence_and_Open_Source_Compliance_Register.md` ·
`./CO-006_Procurement_and_Purchase_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md` ·
`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md` ·
`../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md` ·
`../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md` ·
`../13_Training_Change_and_Adoption/CH-002_Training_Plan_and_Delivery_Schedule.md`

**Workspace**
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
`../../project_content/_AUDIT/AUDIT-001_*`

**External standards and sources** *(all verified 2026-08-19)*

| Source | Used for |
|---|---|
| **ISO 15686-5:2017**, *Buildings and constructed assets — Service life planning — Part 5: Life-cycle costing* | §3.2's cost categories, §3.3's analysis period, and the two declared departures |
| **AACE International RP 17R-97**, *Cost Estimate Classification System* | §4.3's estimate classes |
| **ISO 21502:2020** §7.9 | §12's cost-management rules |
| **ISO/IEC 19770-1:2017**, *IT asset management systems* (Edition 3, reviewed and confirmed 2024) | §5.5's entitlement–consumption treatment of the L6 set |
| **ISO/IEC 5230:2020** (OpenChain Specification 2.1) | The licence-obligation cost consequences carried in §5.5 and §7.4; owned by `CO-004` |
| **Bangladesh VAT and Supplementary Duty Act 2012**, and NBR guidance on imported services, input rebate, Mushak 6.3 / 6.6 / 9.1 | §6.1 |
| **Income Tax Act 2023**, as amended by the **Finance Act 2026**; PwC Worldwide Tax Summaries — Bangladesh, corporate withholding taxes | §6.2's rates: non-resident technical/professional services 10% (entities) / 20% (individuals); royalties 20%; resident services 5%; treaty relief by NBR certificate |
| **Bangladesh Bureau of Statistics** — July 2026 CPI release: general 8.32%, food 7.16%, non-food 9.28% | §6.8's escalation derivation |
| Foreign-exchange market data — USD/BDT 122.70 (17 Aug 2026), 2026 average 122.44, August high 123.785 (5 Aug 2026) | §6.7, §10 |
| Public reporting of **MinIO community-edition archival, 25 April 2026**, and of **Garage** (AGPL-3, S3-compatible, release 16 April 2026) and **SeaweedFS** (Apache-2.0) as maintained alternatives | §5.5's fifth-L6-component exposure; corroborates `BE-007` §7.1 |
| **n8n Sustainable Use Licence** — *"internal business purposes"*, with the test being whether value derives *"entirely or substantially"* from n8n functionality | §5.5; the obligation itself is `CO-004`'s |

> Verify every path resolves before issuing. Nine module files carried references to superseded
> filenames until the August 2026 audits corrected them.

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Chief Financial Officer, with Enterprise Architecture | Initial issue. Discharges `GV-008-D-03` and `GV-008` `Q-03`; closes `PE-006-F-07` and `PE-002-F-04`; completes `H-02` at **4.1×** the figure the Board holds. Raises `CVA-01` through `CVA-06`, of which **`CVA-02` is Critical and time-limited to 17 September 2026**. **Hypercare (line C) and the internal draw (§6.6) were restated at audit against `SV-005`, issued the same day**, which supersedes this document's own first estimate with a three-pool derivation of ≈ 678 PW; `TCO-02` requires the owning document's figure to be taken rather than re-derived | Board of Directors |

---

*`CO-005` · Category 14 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
