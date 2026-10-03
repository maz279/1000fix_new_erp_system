---
id: EO-010
title: Franchise and Channel Partner Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with Operations and Content Design
reviewers: [Chief Executive Officer, Chief Commercial Officer, Chief Financial Officer, Operations Director, Quality Manager, Legal Counsel, Brand Lead, Content Design Lead]
approver: Content Design Lead with Commercial
content_class: D
purpose: >
  The pack issued to a prospective or appointed franchisee or channel partner: the franchise
  model, the territory and its exclusivity, the fees and royalties and how they are computed, the
  brand and operating standards a franchise branch must meet, what systems access they receive and
  what data they can see, and the reporting and audit obligations that follow. M40 extends the
  network through partners operating under the 1000FiX name, and a partner trading under our name
  to standards nobody wrote is the fastest way to lose the brand authorisations the core business
  rests on.
traces_to: [M40, M04, M01, M15, M23, M24, M25, M29, M11, M20, M53, P11, P12, P03, 04-00 P12, 05-04 §8 EA-01, EA-02, FR-PCM-001, FR-PCM-002, FR-PCM-003, FR-PCM-006, FR-PCM-007, FR-PCM-008, FR-PCM-010, FR-PCM-011, FR-PCM-033, FR-PCM-034, FR-PCM-035, FR-PCM-036, FR-PCM-037, FR-PCM-038, FR-PCM-041, BRU-PCM-01, BRU-PCM-10, BRU-PCM-12, BRU-PCM-13, BRU-PCM-14, BRU-PCM-16, BRU-PCM-17, BRU-PCM-18, KPI-C40-14, MD-002, MD-003, MD-005, MD-006, MD-009, MD-011, MD-029, MD-036, LG-007, LG-022, LG-023, SP-004, SP-029, SP-032, VB-001, UI-022, HC-014, EO-009, EO-011, EO-012, EO-014]
priority: P3
wave: W8
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §3.1 item 10 franchise management — franchisee lifecycle, territory, fees and royalties, brand standards, compliance audits; §3.2 franchise branch operations, service delivery and inventory belong to M04/M01/M15, and franchise staff are the franchisee's employees under M21/M56; §5.4 FR-PCM-033…038 reseller allocation and settlement, franchise territory with exclusivity and conflict prevention, fees and royalties computing amounts due and instructing M20/M53, brand-standards manual with acknowledgement and audits through M23/P11, franchise performance benchmarking against owned branches
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §6 T-13 franchise data segregation enforced at the record-rule layer alongside the standard branch tier; §9 BRU-PCM-16 territory exclusivity as declared with cross-territory activity requiring documented agreement, BRU-PCM-17 franchise royalties computed from ERP-recorded revenue rather than franchisee self-declaration; §15 KPI-C40-14 franchise branches meeting brand standards at audit 90% at W8 rising to 95%
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §18 Q-05 — "Is franchise expansion an approved strategy with a defined model, or an aspiration in the business plan? The 2 PW franchise build should not proceed on an aspiration", owner CEO, needed by W6, marked blocking for §5.4
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §4 Benchmark Basis — franchise management systems (FranConnect class) adopted wholesale for territory definition, royalty schedules, brand-standards audit and franchisee benchmarking, "because franchise is a distinct discipline and the business plan commits to it"; a separate franchise product rejected because the volume does not justify it
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P11 Field Auditor & Quality Application, Wave W5, capability "complete audit checklists offline · capture photo and document evidence · record observations against clauses"; P12 Partner & Referral Portal, Wave W7
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Franchise and Channel Partner Pack

| Item | Value |
|---|---|
| Audience | Prospective and appointed franchisees; channel partners operating under the 1000FiX name |
| Population | Undefined — **no franchise target exists in any programme document** (`O-01`) |
| Portals | `P12` for the relationship · `P03` for branch operations · `P11` for standards audits |
| Language | **English only** (`CG-010` §3.2) — **contested; see `O-06`** |
| Issued by | Commercial |
| Wave | W8 · Months 31–34 (`06-01` §3) — **`M40` is W7** |
| Standard measured | `KPI-C40-14` — franchise branches meeting brand standards at audit: 90% at W8, **> 95%** at W9 |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions appear as §4.1 (**journey** — appointment to
> first audit), §4.4 (**checklist** — the standards a branch must meet before it may open) and
> §4.8 (**first 90 days** of a trading franchise branch). Template 15 does not exist.

> ⚠ **Read `O-01` before using this pack.** `M40` Q-05 asks whether franchise expansion is an
> approved strategy or an aspiration in the business plan, and marks the question **blocking for
> `M40` §5.4**. This pack is written against the model `M40` §5.4 specifies. If the answer to
> Q-05 is "aspiration", the pack is a design, not an offer, and must not be issued to anyone.

---

## 1. Purpose

`M40` §2 lists franchise branches among the relationships it owns and states why:
*"the business plan's expansion depends on a model that is not owned-branch."*

A franchise is categorically different from every other relationship in Category 18. A marketplace
seller does a job under our standards; a franchisee **is** 1000FiX to everyone who walks through
their door. They use the name, the livery, the pricing, the systems and the promise. `M12`'s
category risk register rates marketplace quality failure as Critical because it endangers the 17+
manufacturer authorisations; **a franchise branch carries the same exposure at a higher
concentration**, because a customer cannot tell it apart from an owned branch and a brand auditor
may not either.

Three failures follow from appointing a franchisee without a pack:

| Absent | Consequence |
|---|---|
| A written standard | `KPI-C40-14` measures branches "meeting brand standards at audit" against a standard nobody issued. The first audit becomes a negotiation |
| A stated territory and its exclusivity | Two partners compete for one district, or a franchisee believes they hold exclusivity they were never granted (`BRU-PCM-16`) |
| A stated royalty basis | The franchisee reports their own revenue, which `BRU-PCM-17` explicitly forbids as the basis, and the first royalty invoice is disputed |

**What this pack is not.** It is not the franchise agreement — `LG-007` covers referral and
alliance and marks reseller and franchise terms *pending* (`O-02`). It is not the co-branding asset
guide (`EO-012`), not the branch operating procedures (which are the same `SP` procedures owned
branches use), and not the referral kit (`EO-009`).

---

## 2. Scope

**In scope.** The franchise and channel-partner model and what each type is; appointment,
qualification and agreement; territory definition and exclusivity; fees, royalties and marketing
levies, and how each is computed; the brand and operating standards a branch must meet; systems
access and the data boundary a franchisee sits behind; the reporting obligations; the audit
programme and its consequences; performance benchmarking against owned branches; the reseller
variant; and the first 90 days of a trading branch.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Branch operations, service delivery, dispatch and inventory | **`M04`, `M01`, `M15` and the `SP` procedures — franchise branches use the same ones as owned branches** |
| Franchise staff employment, payroll and HR | `M21`, `M56` — **they are the franchisee's employees**, not ours |
| The franchise agreement instrument | `LG-007` §4.9 — **marked *pending*** |
| Referral and alliance mechanics | **`EO-009`** |
| Marks, livery, co-branded materials and their approval route | **`EO-012`** |
| Quality policy, ISO position and the audit standard | `LG-022`; `SP-029` internal audit and CAPA; `SP-032` checklists |
| Anti-bribery and ethics | `LG-023` |
| Rate cards and pricing | `MD-029`; change communication **`EO-011`** |
| Brand and design standards as a system | `VB-001` and the `VB` set |
| Termination, de-branding, territory return and settlement | **`EO-014`** |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Prospective franchisee / investor** | The model, the obligations and the economics before committing capital |
| **Appointed franchisee principal** | Territory, fees, standards, reporting and audit |
| **Franchise branch manager** | The standards their branch is measured against, day to day |
| **Channel partner / reseller principal** | The allocation and settlement variant (§4.7) |
| **1000FiX Commercial lead** | The pack they present and the obligations they commit us to |
| **1000FiX Operations Director** | What a franchise branch is required to run, and where it differs from an owned branch |
| **Quality Manager (`R32`)** | The audit programme and the standard it audits against |
| **CFO** | Royalty basis, fee schedule and the revenue recognition that follows |

---

## 4. Content

### 4.1 The appointment journey

| # | Stage | Partner does | 1000FiX does | Exit condition |
|---|---|---|---|---|
| **1** | **Enquire** | Expresses interest; receives this pack | Confirms whether the territory is available | Territory available and unreserved |
| **2** | **Qualify** | Supplies §4.4 documents, financial standing and operating experience | Qualifies against the programme's entry criteria (`FR-PCM-006`) | Qualified with a recorded reason |
| **3** | **Agree** | Signs the franchise agreement | Links it in `M08`; **transacting is blocked until it is executed** (`BRU-PCM-01`) | Agreement executed |
| **4** | **Territory** | Confirms the territory and its boundaries | Defines it with exclusivity rules and conflict prevention (`FR-PCM-035`, `BRU-PCM-16`) | Territory recorded; no cross-territory conflict |
| **5** | **Standards** | Acknowledges the brand-standards manual (`FR-PCM-037`) | Issues it and records acknowledgement | Acknowledgement recorded against the agreement version |
| **6** | **Establish** | Fits out the branch to standard; recruits and certifies staff | Verifies against §4.4 **before** opening | **Pre-opening audit passed** |
| **7** | **Enable** | Named users complete access setup | Provisions `P03` for operations and `P12` for the relationship, **scoped to their territory only** (`T-13`) | Users see only their own territory |
| **8** | **Train** | Completes programme training and certification (`FR-PCM-041`) | Assigns; gates programme benefits on completion | Certification recorded |
| **9** | **Open** | Trades | Royalty and fee computation begins from ERP-recorded revenue (`BRU-PCM-17`) | First trading day |
| **10** | **Audit** | Hosts the first standards audit | Conducts it through `M23` / `P11` (`FR-PCM-037`) | First audit result recorded against `KPI-C40-14` |

> **Stage 6 is the only gate that cannot be waived.** A branch trading under the 1000FiX name that
> has not passed a pre-opening standards check is an uncontrolled brand exposure from day one, and
> the first customer through the door cannot tell.

### 4.2 What a franchise is, and what it is not

| Type | Operates | Under | Pays | Systems |
|---|---|---|---|---|
| **Franchise branch** | A full service branch in a defined territory | The 1000FiX name, livery, pricing and standards | Initial fee, ongoing royalty, marketing levy | `P03` — the same operational modules as an owned branch, territory-scoped |
| **Channel partner** | Onward sale of 1000FiX services in a segment or geography | Their own name, referencing 1000FiX per `EO-012` | Margin or commission | `P12` |
| **Corporate reseller** | Onward sale of refurbished stock or services against an allocation | Their own name | Reseller pricing | `P12` (`FR-PCM-033`, `FR-PCM-034`) |

**The distinctions that matter to a prospective franchisee:**

| They may assume | The position |
|---|---|
| "I own the customers in my territory" | Customers are 1000FiX customers, held in `M33`. The franchisee serves them; they do not own the relationship |
| "I set my own prices" | **No.** Pricing is `M11` and `MD-029`; a franchise branch trades at 1000FiX pricing, which is what makes the brand promise consistent |
| "I choose my own suppliers and parts" | **No.** Genuine-parts obligations flow from the brand authorisations (`EO-003`, `EO-004`); an unauthorised part in a franchise branch is a brand exposure |
| "My staff are 1000FiX staff" | **No** — `M40` §3.2. They are the franchisee's employees. **Their certification, however, is ours to verify** (`MD-011`) |
| "I report my revenue and you invoice the royalty" | **No** — `BRU-PCM-17`. Royalties are computed **from ERP-recorded revenue**, not from self-declaration. §4.5 |

### 4.3 Territory and exclusivity

| Element | Statement | Rule |
|---|---|---|
| Definition | A territory is defined against the geographic hierarchy (`MD-006`) and the dispatch-zone model (`MD-005`) | `FR-PCM-035` |
| Exclusivity | **Exclusive as declared** — the agreement states the scope of exclusivity, and it is not assumed | `BRU-PCM-16` |
| Cross-territory activity | **Requires documented agreement.** It is not prohibited; it is not unilateral | `BRU-PCM-16` |
| Conflict detection | Detected and prevented at definition, and surfaced for decision in life | `FR-PCM-035`, `FR-PCM-029` |
| Channel precedence | Where a franchise territory, a direct sale, a referral partner and the marketplace all reach one customer, declared precedence applies | `BRU-PCM-10` — **the rule set is undecided**, `EO-009` `O-02` |
| Online demand | **Unallocated.** A customer in a franchise territory booking through `P01` is served by whom? | **`O-03`** |

### 4.4 The standards checklist

**What a branch must meet before stage 6 passes, and continuously afterwards.** Drawn from the
`FR-PCM-037` brand-standards manual, and audited under `FR-PCM-037` through `M23` / `P11`.

| # | Domain | Standard | Evidence at audit |
|---|---|---|---|
| 1 | **Identity and premises** | Livery, signage, layout and customer area to the `VB` standard; `EO-012` governs every mark | Photographic evidence against the specification |
| 2 | **Legal standing** | Trade licence, e-TIN, 13-digit e-BIN where VAT-registered, in the franchisee's own entity | Current documents |
| 3 | **Staff certification** | Technicians certified for the categories the branch offers (`MD-011`); brand-authorised work only where the certification exists | Certification register; **`BRD-03` applies to a franchise branch exactly as to an owned one** |
| 4 | **Systems** | All work recorded in `P03`; **no shadow job book, no parallel invoicing** | System record vs. observed activity |
| 5 | **Parts** | Genuine parts per the brand authorisation; sourced through the approved channel | Parts provenance; stock records (`M15`) |
| 6 | **Service standards** | The same `SP` procedures as an owned branch — intake, diagnosis, estimate approval, evidence, QC, handover | Sampled job evidence |
| 7 | **Pricing** | 1000FiX pricing, no local variation | Invoices vs. `MD-029` |
| 8 | **Cash and banking** | Cash handling and banking to `SP-019`; takings recorded in the system | Reconciliation |
| 9 | **Health, safety and environment** | `SP-030` standards; e-waste routed per `SP-026` and `MD-047` | Records and observation |
| 10 | **Data protection** | Customer data handled under `LG-008`; no local customer database | Access records; absence of local copies |
| 11 | **Quality** | Nonconformities raised and CAPAs closed (`SP-029`) | `M23` record |
| 12 | **Ethics** | Anti-bribery and the standards in `LG-023` | Declaration and training records |
| 13 | **Reporting** | Required returns submitted on time (§4.6) | Submission record |

> **Standard 4 is the one that decides whether every other standard is auditable.** A franchise
> branch keeping any work outside `P03` breaks royalty computation (`BRU-PCM-17`), benchmarking
> (`FR-PCM-038`), quality sampling and warranty claiming simultaneously. It is treated as a
> terminal breach in §4.8, not as a finding.

### 4.5 Fees, royalties and how they are computed

| Element | Basis | Rule |
|---|---|---|
| **Initial fee** | Per the agreement, at appointment | `FR-PCM-036` |
| **Ongoing royalty** | **Computed from ERP-recorded revenue** — never from franchisee self-declaration | **`BRU-PCM-17`** |
| **Marketing levy** | Per the agreement; funds central marketing, and `FR-PCM-039` MDF where the programme carries it | `FR-PCM-036` |
| Amounts due | Computed by `M40` and instructed to `M20` / `M53` | `FR-PCM-036` |
| Rates and values | **`MD-029` and the agreement.** This pack states none | `FC-04` |
| Programme version | The franchisee is bound to the programme version in force at their agreement date | `BRU-PCM-12` |

> **Why `BRU-PCM-17` is stated to the franchisee rather than merely applied.** A royalty computed
> from our records and not their declaration removes the single largest source of dispute in
> franchise operations, **and it only works if every transaction is in the system** — which is
> standard 4. The two rules are one control seen from two sides, and a franchisee who understands
> that understands why standard 4 is not administrative.

### 4.6 Systems access, data boundary and reporting

| Item | Position |
|---|---|
| **Operational access** | `P03`, scoped to the franchisee's own territory, enforced **at the record-rule layer alongside the standard branch tier** (`T-13`) |
| **Relationship access** | `P12` — agreement, standards, performance, fees, communications |
| **What they see** | Their own territory's operational data; their own performance; their own fees |
| **What they do not see** | Any other branch or territory's data; 1000FiX group cost or margin; another partner's records (`BRU-PCM-14`, `EA-01`, `EA-02`) |
| **Benchmarking** | They see **their own position against a benchmark**, not other branches' identifiable figures (`FR-PCM-038`) |
| **Access revocation** | Within one hour of exit, suspension or agreement expiry (`BRU-PCM-13`) |
| **Reporting obligations** | The returns the agreement requires, on the stated cadence; **most operational reporting is automatic because the work is in `P03`** |

### 4.7 The reseller and channel variant

Shorter, because it is a supply relationship rather than an operating one.

| Element | Position |
|---|---|
| Allocation | Refurbished stock and service capacity allocated to the reseller, with visibility of the allocation and its status (`FR-PCM-033`) |
| Ordering | Against allocation and agreed pricing, through `P12` (`FR-PCM-034`) |
| Settlement | Per the programme terms |
| Brand | The reseller trades in **their own** name; use of 1000FiX marks is governed by **`EO-012`** |
| Standards | Product condition, warranty representation and customer-facing claims — **a reseller misrepresenting a refurbished device's warranty creates our liability, not theirs** |
| Channel conflict | With direct sale, franchise territory and the marketplace (`BRU-PCM-10`) |

### 4.8 The first 90 days of a trading branch

| Days | Franchisee milestone | 1000FiX milestone | Test |
|---|---|---|---|
| **0–30** | Trading; all work in `P03`; staff certifications current | First royalty computed from ERP revenue; benchmarking baseline established | **Is there any work not in the system?** |
| **31–60** | First quality sample; first warranty claim if brand-authorised | First quality sampling to the owned-branch standard (`SP-029`) | Evidence quality against an owned branch |
| **61–90** | **First full standards audit** (`P11`) | Findings, CAPA, closure | `KPI-C40-14` — 90% at W8, > 95% at W9 |
| **91+** | Steady state | Quarterly benchmarking; relationship health score with named factors (`FR-PCM-018`, `BRU-PCM-18`) | Trend |

**Consequence ladder for a standards failure.**

| Severity | Consequence |
|---|---|
| Finding at audit | CAPA with an owner and a due date (`SP-029`); overdue escalates |
| Repeated finding | Improvement plan; increased audit frequency |
| **Work outside the system** (standard 4) | **Terminal.** It defeats royalty, quality, warranty and benchmarking simultaneously |
| **Unauthorised or counterfeit parts** | **Terminal**, and reportable to the affected brand — the exposure is to the authorisation, not to the branch |
| **Use of the name outside the agreement or `EO-012`** | Standing change; `EO-014` if unresolved |
| Safety or ethics breach | Immediate suspension of trading under the name |

### 4.9 Rules

| # | Rule |
|---|---|
| **FC-01** | The pack is not issued to any prospect until `M40` Q-05 is answered (`O-01`). **A franchise offer made against an unapproved strategy is a commitment the company has not decided to make** |
| **FC-02** | Territory exclusivity is stated as **"exclusive as declared"** and never as a general promise (`BRU-PCM-16`) |
| **FC-03** | The royalty basis is stated as **ERP-recorded revenue**, with standard 4 stated in the same section as its precondition (`BRU-PCM-17`) |
| **FC-04** | The pack states no fee, royalty rate or levy value. The agreement and `MD-029` hold them |
| **FC-05** | The five franchisee assumptions in §4.2 are addressed explicitly, because each one is a dispute if left unstated |
| **FC-06** | Franchise staff are described as the franchisee's employees, **and their certification as ours to verify** |
| **FC-07** | A franchise branch is described as running **the same `SP` procedures as an owned branch** — the pack never restates a procedure (`CP-01`) |
| **FC-08** | The pre-opening standards check (stage 6) is stated as unwaivable |
| **FC-09** | The data boundary is stated, including that benchmarking shows position but not other branches' identifiable figures |
| **FC-10** | The consequence ladder names the two terminal breaches explicitly |
| **FC-11** | Programme terms are versioned; the franchisee is bound to the version at their agreement date (`BRU-PCM-12`) |
| **FC-12** | Nothing in the pack varies the agreement. `LG-007` §4.9 covers franchise terms and is **marked *pending*** — the pack says so rather than filling the gap |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M40` §5.4 | Territory, fees and royalties, brand standards, benchmarking, reseller allocation |
| **`LG-007` §4.9** | Franchise and reseller terms — **marked *pending* `O-07`, `PA5`** |
| [`MD-005`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md), [`MD-006`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md) | Dispatch zones and geography, against which a territory is defined |
| [`MD-002`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-002_Legal_Entity_and_Company_Master.md), [`MD-003`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-003_Branch_and_Service_Centre_Master.md) | Legal entity and branch master — a franchise branch must exist in both |
| [`MD-011`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Certifications the branch's staff must hold |
| [`MD-029`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | Pricing a franchise branch trades at |
| [`MD-036`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md) | Cost centre and dimension register for royalty and benchmarking reporting |
| `M04`, `M01`, `M15` and the `SP` set | The operations a franchise branch runs identically to an owned branch |
| `M23`, `P11`, [`SP-029`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md), [`SP-032`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md) | The audit programme and its checklists |
| [`LG-022`](../10_Legal_Policy_and_Compliance/LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md), [`LG-023`](../10_Legal_Policy_and_Compliance/LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) | Quality policy and ethics standards the branch is held to |
| [`VB-001`](../01_Voice_Brand_and_Design_Content/VB-001_ERP_Product_Voice_and_Tone_Guide.md), **[`EO-012`](EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md)** | Brand standards and the marks the branch may use |
| `P03`, `P12`, `M29` | Systems access and the record-rule scoping (`T-13`) |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md), [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Price change communication; termination, de-branding and settlement |

> **Rule-citation attribution.** **BRU-PCM-\***  → `M40` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and at every programme version change |
| Trigger for out-of-cycle review | `M40` Q-05 being answered; a change to `LG-007` §4.9; a territory or exclusivity dispute; a standards audit revealing a standard this pack does not state; a change to `MD-029` pricing policy for franchise branches; a brand partner querying franchise-branch authorisation |
| Owner | Commercial, with the Operations Director for §4.4 and the Quality Manager for the audit programme |
| Change control | **Standards changes apply from the next audit cycle**, with notice; a franchisee is bound to the programme version at their agreement date (`BRU-PCM-12`), so a standards change is a programme version change, not an edit |
| Effectiveness measure | `KPI-C40-14`, and the share of first audits passed without a major finding |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The strategy this pack describes may not be approved.** `M40` Q-05: *"Is franchise expansion an approved strategy with a defined model, or an aspiration in the business plan? The 2 PW franchise build should not proceed on an aspiration."* Owner **CEO**, needed by **W6**, marked **blocking for `M40` §5.4**. **This is the only file in Category 18 whose entire subject is conditional on an undecided strategic question**, and `FC-01` forbids issuing the pack until it is answered. The register's `P3` priority is consistent with that conditionality; the W8 wave is not, because the decision is due at W6 | **CEO** | **W6 — blocking** |
| **O-02** | **There is no franchise agreement.** `LG-007` covers referral and alliance, and its §4.9 *"Reseller and franchise terms"* is **explicitly marked pending `O-07`, `PA5`**. Every obligation in this pack — territory, royalty, standards, termination — needs a contractual instrument, and **`LG-001` registers no separate franchise agreement**. `AUDIT-013` recorded four upstream legal decisions blocking Category 10; this is a fifth, and it is unregistered | Legal Counsel with CCO | **W7 — before any appointment** |
| **O-03** | **Online demand inside a franchise territory is unallocated.** A customer in a franchised district booking through `P01`, or a job broadcast to the marketplace inside that territory, has no declared owner. `BRU-PCM-10` requires declared channel precedence and `EO-009` `O-02` records the rule set as undecided; **the franchise case is the sharpest instance, because the franchisee paid for exclusivity** | CCO | **W7 — before the first territory is granted** |
| **O-04** | **`KPI-C40-14` measures against a brand-standards manual that does not exist.** `FR-PCM-037` requires 1000FiX to *"maintain the brand-standards manual, track franchisee acknowledgement, and schedule standards audits"*. §4.4 specifies thirteen domains; **it is a specification of the manual, not the manual.** No `VB`, `SP` or `EO` file holds a franchise brand-standards manual, and `SP-032`'s checklist library is written for owned branches | Operations Director with Brand Lead and Quality Manager | **W8 — before the first audit** |
| **O-05** | **The audit capability is W5 and the franchise programme is W7–W8, and nobody has assessed whether `P11` covers a franchise branch.** `P11` capability includes *"audit marketplace sellers against platform standards"* and says nothing about franchise branches, though `M40` `FR-PCM-037` routes franchise audits through `M23`/`P11`. **A checklist written for an owned branch will not test the franchise-specific standards** — royalty basis, work-in-system, territory compliance, name use | Quality Manager with the `P11` owner | **W8 — before the first franchise audit** |
| **O-06** | **English-only is a weak allocation for this file.** `CG-010` §3.2's `EO` rationale — *"brand partner and supplier material is English"* — does not describe a franchisee, who is a Bangladeshi business operating a branch with Bengali-speaking staff and customers. The English allocation is held here to keep the category at the `CG-010` 8/6 split; **on the §3.3 audience rule this file would be bilingual.** Recorded, with the category audit, as a `CG-010` allocation defect rather than a file decision | Localisation Lead with Programme Content Lead | **W8** |
| **O-07** | **No franchise volume target exists anywhere.** `KPI-C40-01` counts referral and alliance partners; `KPI-C40-14` measures standards at audit **as a percentage of an unstated denominator**. The business plan is cited by `M40` §2 as committing to the model and **no document states how many franchise branches, over what period, in which territories.** A pack with no target is a pack with no capacity plan | CEO / CCO | **W6 — with `O-01`** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions placed and the template gap noted
- [x] **The conditionality of the whole file stated at the top, not buried in an open item**
- [x] The categorical difference between a franchisee and every other ecosystem partner stated in §1
- [x] Ten-stage appointment journey with the pre-opening gate identified as unwaivable
- [x] **Five franchisee assumptions addressed explicitly, each with the position that contradicts it**
- [x] Territory, exclusivity and cross-territory activity stated per `BRU-PCM-16`
- [x] Thirteen-domain standards checklist with the audit evidence for each
- [x] **Standard 4 identified as the precondition of every other standard being auditable, and tied to the royalty basis**
- [x] Royalty basis stated as ERP-recorded revenue, with the reason it benefits the franchisee
- [x] Data boundary and record-rule scoping stated, including benchmarking without identifiable comparators
- [x] Reseller and channel variant covered separately
- [x] First-90-days section with a consequence ladder naming two terminal breaches
- [x] Twelve rules, including the prohibition on issuing the pack before `M40` Q-05 is answered
- [x] All internal links resolve
- [x] Seven open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` franchise strategy undecided — outstanding; `FC-01` blocks issue of this pack**
- [ ] **`O-02` no franchise agreement exists — outstanding; `LG-007` §4.9 is pending and no separate instrument is registered**
- [ ] **`O-03` online demand in a franchised territory unallocated — outstanding**
- [ ] **`O-04` the brand-standards manual `KPI-C40-14` measures against does not exist — outstanding**
- [ ] **`O-07` no franchise volume target anywhere — outstanding**
- [ ] Named approver recorded — **pending Content Design Lead with Commercial**
- [ ] Bengali counterpart — n/a per `CG-010` §3.2, **contested by `O-06`**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
