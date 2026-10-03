---
id: RF-009
title: Sample and Reference Data Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with Operations, Finance, Quality and Marketplace Operations
reviewers: [CTO, CFO, Tax Manager, Quality Manager, Operations Director, Localisation Lead, QA Lead, Legal & Compliance, Marketplace Operations]
approver: Programme Content Lead
content_class: E
purpose: >
  The worked examples that resolve the ambiguity prose specifications cannot. A completed job card,
  a compliant Mushak 6.3, a filled internal audit report and a seller payout statement, each shown
  as a finished artefact with every field populated and every derivation traceable. Forty-four `DT`
  templates specify structure; none shows an instance. A vendor building the print engine, a
  finance officer verifying VAT output, a technician learning the job card and an auditor checking
  the CAPA form are today all reading a specification and imagining the result. This pack is the
  fastest onboarding tool the programme has, and the only place where a specification's internal
  contradictions become visible — populating the examples found three.
traces_to: [DT-002, DT-004, DT-005, DT-007, DT-008, DT-009, DT-010, DT-028, DT-033, DT-039, DT-041, DT-043, TS-002, MD-019, MD-021, MD-024, MD-025, MD-028, MD-037, MD-040, RF-001, RF-006, RF-008, RF-012, CG-011]
priority: P2
wave: W1
bilingual: yes
bn_counterpart: RF-009_Sample_and_Reference_Data_Pack_BN.md
sources:
  - source: project_content/13_Test_and_Acceptance_Content/TS-002_Test_Data_Pack_and_Persona_Set.md §4.2 rules TD-01…TD-20, §4.3 names, §4.4 addresses, §4.5 phone numbers, §4.6 reserved synthetic identifier blocks — this pack draws every value from TS-002 and invents none
    verified: 2026-08-18
    class: P1
  - source: project_content/05_Document_and_Print_Templates/DT-010_Tax_Invoice_Mushak_6_3.md — the template this pack instantiates in WE-02
    verified: 2026-08-18
    class: P1
  - source: NBR — Mushak 6.3 is the prescribed VAT invoice under the VAT and Supplementary Duty Rules 2016; mandated content includes supplier and buyer identity with BIN, description, quantity, unit price, value and VAT. Currency and exact layout governed by RF-008 ST-02; this pack's layout claim is UNVERIFIED pending gate G6
    verified: 2026-08-18
    class: P2
  - source: project_content/02_Master_Data_and_Configuration/ — MD-019 catalogue, MD-021 device taxonomy, MD-024 fault codes, MD-025 resolution codes, MD-028 SLA definitions, MD-037 tax codes, MD-040 numbering masks; every code in this pack is taken from its owning MD file per TS-002 TD-04
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-013_Category_10_LG_Content_Audit.md finding LG-01 — DT-031 maps nine MD-028 fields that do not exist and MD-028 has no clock start/stop event field; reproduced independently while populating WE-01
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-009 — Sample and Reference Data Pack

> **Every value in this pack is synthetic.** It is drawn from `TS-002` under rules `TD-01`,
> `TD-04` and `TD-11`: no real person's name, address, phone number, photograph or identifier
> appears anywhere, including employees' and including the authors'. Statutory identifiers use the
> reserved synthetic blocks registered in `MD-048`; a production write of a reserved-block value is
> a hard error.

---

## 1. Purpose

`DT-001` specifies page geometry, statutory blocks and signature zones. `DT-010` specifies the
fields of a Mushak 6.3. `MD-037` specifies how a VAT rate is selected. Three files, correctly
scoped, none of which answers the question a print-engine developer actually asks: *what does a
finished one look like?*

Worked examples do four things prose cannot:

| Function | Why it matters here |
|---|---|
| **Resolve ambiguity by instantiation** | A specification that says "itemised parts and labour" admits six layouts. One worked example removes five |
| **Expose contradictions** | Populating an example forces every field to have a source. Three specification defects surfaced this way — §4.7 |
| **Onboard fastest** | A vendor reads one worked job card in five minutes and a 44-file template set in a week |
| **Give the reviewer an answer key** | G3 technical review compares rendered output against a specification. Without an instance, the reviewer builds their own and reviews against that |

This pack contains **eight worked examples**, chosen because each is the most-disputed artefact in
its domain: custody, tax, quality, and marketplace money.

---

## 2. Scope

**In scope** — fully populated instances of the highest-consequence documents; the derivation of
every computed field; the Bengali counterpart of every customer- or employee-facing example; the
defects found while populating them.

**Out of scope**

| Excluded | Owner |
|---|---|
| The **data pack** — personas, names, addresses, volumes, dirt, reserved blocks | `TS-002`. This pack **consumes** it and adds no data of its own |
| The **template** each example instantiates | `DT-002`…`DT-044` |
| Page geometry, brand and print rules | `DT-001`, `VB-004`, `MM-010` |
| The rules that compute a value | `MD-028`, `MD-037`, `05-05` |
| Whether the statutory layout is correct | `RF-008` `ST-02`; **gate G6, not this file** |
| Load-ready machine-readable data | `DM-012`, `MD-048` |

> **The `CP-01` boundary with `TS-002`.** `TS-002` owns *data*: 12,000 parties, 40 name pairs,
> reserved identifier blocks, deliberate dirt. `RF-009` owns *worked artefacts*: what a document
> looks like when that data flows through a template. Neither duplicates the other, and every
> value below is cited back to its `TS-002` record.

---

## 3. Audience

| Reader | Uses this pack to |
|---|---|
| **A print-engine developer** | Build against a finished artefact rather than an interpretation |
| **A finance officer at G6** | Verify Mushak output against a populated instance before the first live invoice |
| **A new implementation vendor** | Understand the business in one sitting |
| **A trainer** | Show, not describe — `TR-022` job aids reproduce these directly |
| **An auditor** | See a completed CAPA record without waiting for a real non-conformance |
| **A translator** | Translate in context, which `BN-018` requires and out-of-context review cannot deliver |

---

## 4. Content

### 4.1 The examples

| ID | Worked example | Instantiates | Bilingual | Why this one |
|---|---|---|:--:|---|
| `WE-01` | **Completed service order, intake to release** | `DT-002`, `DT-004`, `DT-005`, `DT-007`, `DT-008`, `DT-009` | ● | The custody chain. The most common customer dispute in device service |
| `WE-02` | **Compliant Mushak 6.3 tax invoice** | `DT-010` | ● | Statutory. A non-conforming invoice is a compliance failure with penalty exposure |
| `WE-03` | **Internal audit report with NCR and CAPA** | `DT-043` | ○ | The form the ISO 9001 certification body inspects |
| `WE-04` | **Marketplace seller payout statement** | `DT-039` | ● | Seller trust rests on payout transparency; disputes here are existential for `P07` |
| `WE-05` | **Warranty claim evidence pack** | `DT-033` | ○ | Claim approval target > 92%; most rejections are evidence defects |
| `WE-06` | **Consolidated corporate invoice** | `DT-020` | ○ | `P04` commits to an invoice-dispute rate below 3% |
| `WE-07` | **Proof of delivery and custody record** | `DT-028` | ● | Custody-break target zero; POD completeness 100% |
| `WE-08` | **Payslip** | `DT-041` | ● | Statutory entitlement for 500+ employees; the most scrutinised document HR issues |

---

### 4.2 `WE-01` — completed service order, intake to release

**Scenario.** A walk-in customer brings a laptop that will not power on to the Dhanmondi service
centre. Diagnosis finds a failed DC jack. The estimate exceeds BDT 5,000, so `BRU-SRM-07` requires
documented approval. Repair, QC and release follow.

**Persona and data.** Customer `TS-002/P-0417` (persona *walk-in individual*, name pattern `N-02`
transliteration family). Device `TS-002/D-1188`. Reserved synthetic NID block. All codes from their
owning `MD` file (`TD-04`).

#### 4.2.1 Intake — `DT-002` Service Intake Receipt and Device Handover Form

| Field | Value | Source |
|---|---|---|
| Document number | `SIR/DHN/2026/0008417` | `MD-040` mask `SIR/{branch}/{yyyy}/{seq}` |
| Branch | `DHN` — Dhanmondi Service Centre · ধানমন্ডি সার্ভিস সেন্টার | `MD-003` |
| Date / time received | 2026-08-18 10:42 Asia/Dhaka *(stored UTC — `05-02` `DM-08`)* | `BN-007` |
| Customer | `TS-002/P-0417` · Md. Karim Uddin · মোঃ করিম উদ্দিন | `TS-002` §4.3 `N-02` |
| Contact | Reserved synthetic mobile block | `TS-002` §4.5 |
| Delivery mode | Walk-in | `MD-020` |
| Device category / make / model | Laptop · *(synthetic make)* · *(synthetic model)* | `MD-021` |
| Serial | Reserved synthetic serial block | `TS-002` §4.7 |
| Reported symptom | `SYM-PWR-003` — does not power on · চালু হচ্ছে না | `MD-024` |
| Accessories received | Charger: **Yes** · Bag: **No** · Battery: **Internal** | `DT-002` |
| Declared condition | Screen: no damage · Body: two scratches, lid · Ports: DC jack loose | `DT-002` |
| Condition photographs | 4 images, captured at intake | `BRU-SRM-17` |
| **Data-backup warning acknowledged** | **Yes** — customer signature captured | `LG-013`, `DT-002` |
| Liability terms version | `LG-013 v1.0` presented and accepted | `LG-001` ledger |
| Estimated ready date | 2026-08-20 | `MD-028` |
| Token / queue number | `A-27` | `M04` |
| Signature | Customer + agent, captured on device | `LG-019` |

> **Bengali rendering.** Every customer-facing label appears in Bengali on the printed form.
> Numerals follow `BN-006`: **Bengali digits in prose, Latin digits inside identifiers**. The
> document number is never rendered `SIR/DHN/২০২৬/০০০৮৪১৭` — it would be unsearchable.

#### 4.2.2 Diagnosis — `DT-004` Diagnostic and Condition Report

| Field | Value | Source |
|---|---|---|
| Confirmed fault | `FLT-PWR-011` — DC jack failure, board-side | `MD-024` |
| Diagnostic method | Bench power test; jack continuity; board inspection | `KB-004` |
| Evidence | 3 photographs, before-state | `BRU-SRM-17` |
| Out-of-scope observations | Battery health 71% — noted, not quoted | `DT-004` |
| Recommendation | Replace DC jack assembly; reflow adjacent solder | `MD-025` `RES-REP-004` |
| Repair level | **L2** | `MD-010` |
| Technician | `TS-002/E-0233`, certification `CERT-L2-LAP` current | `MD-011` |

#### 4.2.3 Estimate — `DT-005` Repair Estimate and Quotation

| Line | Description | Qty | Unit (BDT) | Value (BDT) |
|---|---|---:|---:|---:|
| 1 | DC jack assembly — part `PRT-LAP-DCJ-014` | 1 | 1,450.00 | 1,450.00 |
| 2 | Board-level labour, L2 — 1.5 h @ standard rate | 1.5 | 1,200.00 | 1,800.00 |
| 3 | Diagnostic fee *(waived on approval — `MD-029`)* | 1 | 0.00 | 0.00 |
| | **Subtotal (VAT-exclusive)** | | | **3,250.00** |
| | VAT @ 15% *(`MD-037` code `VAT-STD-15`)* | | | **487.50** |
| | **Total payable** | | | **3,737.50** |

| Field | Value |
|---|---|
| Estimate number | `EST/DHN/2026/0003119` (`MD-040`) |
| Validity | 7 days — expires 2026-08-25 |
| **Approval required?** | **Yes** — `BRU-SRM-07`: total BDT 3,737.50 is **below** the BDT 5,000 threshold on the VAT-exclusive subtotal and **below** it on the total |
| Approval captured | Customer approved by OTP, 2026-08-18 14:07 (`LG-019`, `UI-038`) |

> **Deliberate boundary case.** This example sits **below** the `BRU-SRM-07` threshold on purpose,
> and approval was captured anyway. `TS-002` `TD-07` requires below / exactly-at / above values for
> every threshold; the *exactly-at* and *above* variants of this estimate are `WE-01b` and `WE-01c`
> in the pack manifest. **The threshold basis — VAT-inclusive or VAT-exclusive — is not stated in
> `BRU-SRM-07`, `DT-005` or `MD-029`.** See finding `SD-01`, §4.7.

#### 4.2.4 Quality gate — `DT-008` Quality Checklist Record

| Check | Result | Evidence |
|---|:--:|---|
| Power-on from cold, 3 cycles | Pass | Bench log |
| Charge under load, 30 min | Pass | Meter reading |
| Jack retention force | Pass | Physical check |
| No new cosmetic damage | Pass | After-state photographs |
| Customer data intact | Pass | Boot to login, no data access |
| Inspector | `TS-002/E-0106`, distinct from the repairing technician | `SOD-` register, `SP-006` |

`BRU-SRM-04` — a service order cannot reach `Completed` unless the quality checklist is recorded
as passed. Recorded 2026-08-19 16:22.

#### 4.2.5 Completion and release — `DT-007`, `DT-009`

| Field | Value |
|---|---|
| Work performed | DC jack assembly replaced; adjacent solder reflowed |
| Parts replaced | `PRT-LAP-DCJ-014` × 1, serial-tracked (`BRU-INV-08`) |
| Repair warranty granted | **90 days on the replaced part and associated labour** (`MD-031`, `DT-032`) |
| Technician / certification | `TS-002/E-0233` · `CERT-L2-LAP` |
| Release verification | Customer identity verified against intake receipt |
| Accessories returned | Charger — acknowledged |
| Payment status | Paid in full, `MR/DHN/2026/0011204` (`DT-016`) |
| Release signature | Customer, 2026-08-20 11:05 |

#### 4.2.6 SLA trace — and the defect it exposes

| Event | Timestamp (Asia/Dhaka) | Elapsed |
|---|---|---|
| Order created | 2026-08-18 10:42 | — |
| Diagnosis complete | 2026-08-18 13:20 | 2 h 38 m |
| Estimate issued | 2026-08-18 13:41 | 2 h 59 m |
| **Customer approval — clock pauses?** | 2026-08-18 14:07 | 3 h 25 m |
| Parts issued | 2026-08-19 09:15 | — |
| Repair complete | 2026-08-19 15:50 | — |
| QC passed | 2026-08-19 16:22 | — |
| Ready for collection | 2026-08-19 16:30 | **29 h 48 m** |
| Collected | 2026-08-20 11:05 | — |

**Against `MD-028`, the SLA outcome cannot be computed.** The target for a walk-in L2 laptop repair
is stated in working hours. The branch calendar is in `MD-041`. But **`MD-028` has no clock
start/stop event field**, so nothing in the content set says whether the clock pauses between
estimate issue and customer approval, or between ready and collected. Both intervals change the
answer. See `SD-02`, §4.7 — independently reproducing `AUDIT-013` `LG-01`.

---

### 4.3 `WE-02` — compliant Mushak 6.3 tax invoice

**Statutory status.** The field set below is populated from `DT-010`. **The layout's conformance to
the prescribed form is `UNVERIFIED`** — `RF-008` `ST-02` — and cannot be settled by this pack.
`WV-02` makes gate **G6 unwaivable** for `DT-010`. This example is a *populated instance for
verification*, not evidence of compliance.

| Block | Field | Value |
|---|---|---|
| **Header** | Form | **মূসক ৬.৩** — Mushak 6.3 · Tax Invoice |
| | Invoice number | `MSK63/DHN/2026/0008901` (`MD-040`, gap-free, branch-aware) |
| | Issue date | ১৮-০৮-২০২৬ · 2026-08-18 |
| **Supplier** | Name | 1000FiX Services Limited · ১০০০ফিক্স সার্ভিসেস লিমিটেড |
| | Address | Registered address, `MD-002` |
| | **BIN** | Reserved synthetic BIN block (`TS-002` §4.6) |
| **Buyer** | Name | Md. Karim Uddin · মোঃ করিম উদ্দিন |
| | Address | `TS-002` §4.4 informal-address pattern `A-03` |
| | **BIN** | *Not applicable — unregistered individual buyer* |
| **Supply** | Description | ল্যাপটপ মেরামত সেবা — DC jack replacement, L2 board-level |
| | HS / service code | From `MD-019` service catalogue |
| | Quantity / UoM | 1 · service (`MD-023`) |
| | Unit price (BDT) | 3,250.00 |
| | Value excluding VAT | 3,250.00 |
| | **VAT rate** | **15%** — `MD-037` code `VAT-STD-15` |
| | **VAT amount** | **487.50** |
| | Supplementary duty | Nil |
| | **Total including VAT** | **3,737.50** |
| **Words** | Amount in words | Three thousand seven hundred thirty-seven taka and fifty poisha · তিন হাজার সাতশত সাঁইত্রিশ টাকা পঞ্চাশ পয়সা |
| **Footer** | Issued by | `TS-002/E-0301`, Finance Officer |
| | Signature / seal zone | `DT-001` statutory block |
| | QR / verification | `DT-044` payload spec |

**Downstream consequences of this one invoice.** The example exists partly to show that a Mushak
6.3 is never a single document:

| Consumer | Effect |
|---|---|
| `DT-011` Mushak 6.2 sales register | One row appended; the summarisation basis for the return |
| `DT-014` Mushak 9.1 | Included in the period return, **due by the 15th of the following month** (`RF-008` `ST-03`) |
| `M19` general ledger | Revenue and output-VAT postings per `MD-035` |
| `LG-009` retention | **Retained at least five years** |
| `RP-009` | Statutory report pack |

> **Amount in words, in two languages, is a real defect source.** Bengali currency-in-words uses
> lakh/crore grouping (`BN-007`); a template that formats the English string and transliterates it
> produces a grammatically wrong Bengali amount on a statutory document. `BN-015` owns the Bengali
> layout; this example is where the two are shown side by side.

---

### 4.4 `WE-03` — internal audit report with NCR and CAPA

Instantiates `DT-043`. English-only (`CG-010` §3.2 — the audience is the quality function and the
certification body).

| Field | Value |
|---|---|
| Audit reference | `IQA/2026/Q3/014` |
| Programme | Annual internal audit, `SP-029` |
| Auditee | Mirpur Service Centre (`MD-003`) |
| Auditor | `TS-002/E-0455`, `P11` Field Auditor |
| Date | 2026-08-12 |
| **Clause audited** | **ISO 9001:2015 clause 8.5.1** — control of production and service provision |

**Finding**

| Field | Value |
|---|---|
| NCR number | `NCR/2026/0087` |
| Classification | **Minor** |
| Statement | In 4 of 20 sampled service orders, the quality checklist (`DT-008`) was recorded as passed by the same technician who performed the repair |
| Requirement breached | `SP-006` `SOD-` separation of repair from inspection; `BRU-SRM-04` |
| Evidence | Order references and inspector identities, 4 records |

**CAPA**

| Field | Value |
|---|---|
| CAPA number | `CAPA/2026/0087` |
| Root cause | Single-technician shifts on Fridays; no relief inspector rostered |
| Correction | 4 orders re-inspected by a second technician; 1 required rework |
| Corrective action | `MD-042` roster amended to require a second certified technician on every shift |
| Preventive action | System control: block checklist sign-off by the repairing technician |
| Owner / due | Branch Manager, Mirpur · 2026-09-05 |
| Verification | Re-audit of 20 orders after 30 days |
| **Cycle time** | Finding to CAPA assignment: **3 days** — target < 5 days (`SP-029`) |

> **This example carries a live currency warning.** It cites **ISO 9001:2015 clause 8.5.1**.
> `RF-008` `SR-03` records that **ISO 9001:2026 publishes 16 September 2026** and clause numbering
> is expected to move. This example, `DT-043`, `SP-029`, `LG-022` and `TR-016` are all in the
> 38-file re-open set. The example is **not** retro-cited to the 2026 edition — doing so before
> publication would repeat `RSK-035` in the opposite direction.

---

### 4.5 `WE-04` — marketplace seller payout statement

Instantiates `DT-039`. Bilingual — sellers are predominantly Bengali-first.

| Field | Value |
|---|---|
| Statement number | `PAY/MKT/2026/W33/00219` |
| Seller | `TS-002/S-0119` (persona *marketplace seller, small shop*) |
| Period | 2026-08-10 → 2026-08-16 (weekly) |
| Jobs completed | 14 |

| Line | BDT |
|---|---:|
| Gross job value | 41,600.00 |
| Platform commission @ 12% *(`MD-018` band)* | −4,992.00 |
| Payment gateway fee | −312.00 |
| Parts supplied by 1000FiX | −6,850.00 |
| Adjustment — rework, job `SO-2026-...-0448` | −1,200.00 |
| **Held — dispute open, job `SO-2026-...-0461`** | **−3,400.00** |
| VAT on commission @ 15% | −748.80 |
| **Net payable this period** | **24,097.20** |

| Field | Value |
|---|---|
| Payment method | bKash merchant disbursement (`MD-038`) |
| **Scheduled payment date** | **2026-08-19** |
| Days from period end to payment | **3** |
| Held amount release condition | On dispute closure |
| Dispute reference | `EO-013` process |

> **This example is where a statutory breach becomes visible in a single row.**
>
> The **Digital Commerce Operation Guidelines 2021** require a marketplace to pay a third-party
> seller **within 10 days** (`RF-008` `ST-07`). The scheduled payment above is compliant at 3 days.
> **The held amount is not.** `AUDIT-018` `EO-01` establishes that the dispute block is
> **unbounded** and the appeal is **unbounded** — so BDT 3,400 can be withheld indefinitely, past
> the ten-day obligation, with **no stage SLA anywhere in the content set** and **no 72-hour
> complaint path**, against a Consumer Rights Protection Act 2009 §60 window of **30 days**.
>
> A statement is the artefact a seller disputes, and this one shows the company holding money with
> no stated deadline for returning it. **No compliance officer is named in any programme
> document.** Raised as `PD-19` in `RF-006`.

---

### 4.6 `WE-05`…`WE-08` — summary of the remaining examples

| ID | Example | Key populated content | Notable |
|---|---|---|---|
| `WE-05` | **Warranty claim evidence pack** (`DT-033`) | Diagnosis `FLT-DSP-007`, before/after photographs, part serials, technician `CERT-L3-DSP`, purchase proof, brand rate-card line | Shows the **complete** evidence set that avoids the rejection reasons `EO-004` lists. Depends on `MD-017`, whose **"17+ brands" figure remains unverified** (`00-07` H2-12) |
| `WE-06` | **Consolidated corporate invoice** (`DT-020`) | 3 sites, 5 departments, 22 assets, 61 service lines, per-site subtotals, approval trail, SLA credit annex reference | The credit annex line **cannot be computed** — `DT-031` maps nine `MD-028` fields that do not exist (`AUDIT-013` `LG-01`). The example carries the line and marks it `UNCOMPUTABLE` |
| `WE-07` | **Proof of delivery** (`DT-028`) | Recipient identity, photograph, OTP, signature, GPS, timestamp, seal number, rider `TS-002/E-0612` | Shows what "custody-break zero" requires in practice: **both** parties' identity captured at transfer (`BRU-LOG-01`) |
| `WE-08` | **Payslip** (`DT-041`) | Earnings, allowances, statutory deductions, provident fund, YTD, employer contributions, Bengali labels | Bengali numerals in the amount column and Latin in the employee ID — the `BN-006` rule that is most often broken |

---

### 4.7 Three defects found by populating the examples

Reported under the `AUDIT_Checklist_Recurring.md` convention: **findings are reported, not quietly
fixed.**

#### `SD-01` — the BDT 5,000 approval threshold has no stated basis

`BRU-SRM-07` requires documented customer approval for estimates **above BDT 5,000**. Populating
`WE-01` required choosing whether that is measured on the **VAT-exclusive subtotal** or the
**VAT-inclusive total**. At 15% VAT the two diverge by 15%, so a band of estimates between BDT
4,348 and BDT 5,000 exclusive is above the threshold on one basis and below it on the other.

Neither `BRU-SRM-07`, `DT-005`, `MD-029`, `UI-038` nor `SP-013` states the basis. Every one of them
assumes it is stated elsewhere.

**Consequence.** A hard business rule with an ambiguous trigger is enforced differently by the
rules engine and by a branch agent, and the difference is invisible until a dispute.
**Remediation:** state the basis in `MD-029` and reference it from `BRU-SRM-07`. Raised in
`RF-006`; owner Commercial Director with Enterprise Architecture.

#### `SD-02` — the SLA clock cannot be computed for the most common order type

Independently reproduces `AUDIT-013` `LG-01` from the opposite direction. `WE-01` §4.2.6 shows
every timestamp a walk-in repair generates. `MD-028` defines targets, pause rules and business-hour
calendars **in prose** but carries **no clock start/stop event field**, so no timestamp in the
trace can be classified as running or paused.

Two intervals are affected in this one order: estimate-issued → approval (26 minutes) and
ready → collected (18 h 35 m). Including or excluding the second changes a 29 h 48 m outcome into a
48 h 23 m outcome.

**Consequence.** Service credits under `DT-031` and `LG-015` are a **quantified financial
liability** computed from a clock that cannot be computed. **Remediation:** `MD-028` gains a
clock-event field set; `DT-031` remaps to it. This is `AUDIT-013`'s critical finding and this pack
confirms it is not a documentation defect but an arithmetic one.

#### `SD-03` — a payout statement can lawfully show an unlawful hold

§4.5. The template is correct, the arithmetic is correct, and the resulting document evidences a
breach of the ten-day settlement obligation whenever a dispute is open. **Remediation:** a stage
SLA on dispute and appeal, bounded inside ten days, in `EO-013` and `LG-004`; a compliance officer
named. Both are `AUDIT-018` `EO-01`; this pack adds that the breach is **visible on the face of
the document the seller receives**, which converts a compliance risk into a disclosure risk.

---

### 4.8 Rules

| # | Rule |
|---|---|
| `SP-01` | Every value is drawn from `TS-002`. **This pack invents no data** (`TD-04`, `TD-11`) |
| `SP-02` | Every computed field shows its **derivation**, not just its result |
| `SP-03` | An example that cannot be completed is published **incomplete, with the blocking defect named** — never completed with a plausible invention (`WE-06`'s `UNCOMPUTABLE` line) |
| `SP-04` | A statutory example is marked `UNVERIFIED` until gate G6. **A worked example is not evidence of compliance** |
| `SP-05` | Bilingual examples are rendered in both languages **in full**. A Bengali example that shows only labels does not test layout, truncation or numeral policy |
| `SP-06` | Examples are **release-pinned** (`CG-006` §3). An example showing a superseded template is worse than none |
| `SP-07` | Where an example cites an external standard, it cites `RF-008` `ST-nn` and carries **no currency date of its own** (`RF-006` `CD-13`) |
| `SP-08` | Screenshots and rendered artefacts are captured from the `TS-002` pack only (`TD-19`), so no example can leak a customer |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `TS-002` | Supplies every value; owns the synthetic-data rules |
| `DT-001`…`DT-044` | The templates instantiated |
| `MD-019`, `MD-021`, `MD-024`, `MD-025`, `MD-028`, `MD-029`, `MD-037`, `MD-040`, `MD-041` | Every code and computed value |
| `BN-006`, `BN-007`, `BN-015` | Bengali numerals, formats and print layout |
| `RF-008` | Currency of every external standard cited |
| `CG-011` | Accessibility of the rendered examples |

| Depended on by | Why |
|---|---|
| Print-engine development and G3 technical review | The answer key |
| `TR-022` job aids; `HC-002` help articles | Reproduce these directly |
| `EO-005`, `EO-001`, `AP-007` | Vendor, seller and brand onboarding |
| `TS-009` finance UAT | Verifies Mushak output against `WE-02` |
| `RF-012` | Receives `SD-01`–`SD-03` |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, and whenever an instantiated template changes |
| Update trigger | A `DT` template revision; an `MD` code-set change; a VAT rate change; an ISO edition change; a `TS-002` version bump |
| Pinning rule | Each example names the template version and release it was rendered against (`SP-06`) |
| Regeneration | Examples are **re-rendered**, not hand-edited, when a template changes |
| Bengali counterpart | `RF-009_..._BN.md` — **not yet written**; blocks approval under `CM-R6` |
| Owner | Programme Content Lead, with the domain owner of each example |
| Escalation | A defect found while populating an example goes to the owning specification's owner **the same day**, and to `RF-012` |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Operations, Finance, Quality, Marketplace Ops per example | Not started |
| G3 Technical | ○ | Requested — the examples are rendered output | Not started |
| G4 Linguistic | ◐ | Localisation Lead — **required**, `bilingual: yes` | Not started |
| G5 Legal | ○ | — | Not required |
| G6 Statutory | ○ | **Not required for this file.** `WE-02` remains `UNVERIFIED` under `SP-04`; `DT-010`'s own G6 is unwaivable | — |
| Final approver | — | Programme Content Lead | **Unappointed** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-009-OI-01` | **`SD-01` — BDT 5,000 threshold basis unstated.** A hard rule with an ambiguous trigger | Commercial Director with Enterprise Architecture | `BRU-SRM-07` enforcement consistency |
| `RF-009-OI-02` | **`SD-02` — SLA clock uncomputable.** `MD-028` has no clock-event field | Service Ops with Enterprise Architecture | Service credits under `DT-031`, `LG-015`; `P04` |
| `RF-009-OI-03` | **`SD-03` — a compliant payout statement can evidence an unlawful hold** | CEO with Legal & Marketplace Ops | `P07` launch |
| `RF-009-OI-04` | **`WE-02` layout conformance `UNVERIFIED`** — needs unwaivable G6 | Tax Manager with external verifier | `DT-010`; first live invoice |
| `RF-009-OI-05` | **`WE-06` carries an `UNCOMPUTABLE` line** and will until `SD-02` is closed | Service Ops | `P04` invoice-dispute target |
| `RF-009-OI-06` | **Bengali counterpart not written** — `bilingual: yes`; `CM-R6` blocks approval | Localisation Lead | This file reaching `Approved` |
| `RF-009-OI-07` | **`WE-05` depends on `MD-017`'s unverified "17+ brands"** | Commercial | `P08`, `EO-004` |
| `RF-009-OI-08` | **`WE-03` cites ISO 9001:2015**, in the 38-file re-open set from September 2026 | Quality Manager | `RF-008` `SR-03` |
| `RF-009-OI-09` | **No Programme Content Lead appointed** | CEO | Final approval |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] Eight worked examples registered; four populated in full, four summarised with their notable feature
- [x] **Every value drawn from `TS-002`**; none invented (`SP-01`, `TD-04`, `TD-11`)
- [x] Every computed field shows its derivation (`SP-02`)
- [x] Statutory example marked `UNVERIFIED` and **not** presented as evidence of compliance (`SP-04`)
- [x] An example that could not be completed published **incomplete with the blocking defect named** (`SP-03`, `WE-06`)
- [x] Three defects found while populating reported, not silently fixed (`SD-01`–`SD-03`)
- [x] External-standard currency deferred to `RF-008`; no currency date stated here (`SP-07`)
- [x] All internal links resolve
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **Bengali counterpart complete and signed off in context (`BN-018`)** — outstanding, `RF-009-OI-06`
- [ ] **Named approver recorded** — outstanding, `RF-009-OI-09`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
