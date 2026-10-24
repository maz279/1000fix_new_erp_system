---
id: RP-009
title: Statutory and Regulatory Report Format Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with Compliance
author: Finance Manager with Legal & Compliance and an external tax adviser
reviewers: [CFO, Legal Counsel, Chief Data Officer, Company Secretary, HR Manager, Quality Manager, BI Lead]
approver: CFO with Legal Counsel
content_class: A
purpose: >
  Every report this company is required to submit to an external authority — its prescribed format,
  its deadline and how that deadline is derived, its submission route, the data it is compiled from,
  and the named person accountable for filing it. Statutory deadlines do not move and a missed format
  requirement is discovered at filing time, when there is no remedy left. This is the only file in
  Category 14 whose failure mode is a penalty rather than a bad decision, which is why it is the
  category's single statutory-class artefact and cannot be approved on internal authority alone.
traces_to: [M51, M19, M24, M56, M60, M65, 05-06 §6, 05-06 §6.1, 05-06 §6.2, 05-06 NFR-021, 05-06 NFR-022, 05-06 NFR-100, 05-06 NFR-101, 05-06 NFR-083, 05-06 NFR-088, 06-02 §4, LG-001, LG-024, DT-010, DT-011, DT-012, DT-013, DT-014, DT-041, MD-037, MD-040, MD-041, RP-001, RP-002, RP-004, RP-006, RP-010, RP-014, TS-009, TS-010, SP-020, SP-021, CG-007, CG-012, CG-013]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/_CATEGORY_OVERVIEW.md §6 — the complete table of Bangladesh statutory obligations: Mushak 6.3 tax invoice per taxable sale; Mushak 6.1/6.2/6.2.1/6.5/6.6 registers maintained continuously; Mushak 9.1 VAT return monthly; input VAT credit monthly; TDS/VDS deduction per applicable payment; TDS challan and certificate per deduction; corporate income tax schedules annual; fiscal year July–June; high-value cash NID capture; import duty and VAT at import per shipment
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §6.1 statutory currency table (VAT and SD Act 2012 in force; Income Tax Act 2023; Bangladesh Labour Act 2006 as amended; Personal Data Protection Act 2026 in force with enforcement activating ~13 May 2027); §6.2 NFR-021 Mushak 6.3 compliance, NFR-022 NBR income tax computation, NFR-100 Mushak 9.1 filed by the 15th of the following month through the NBR VAT Online portal vat.gov.bd, NFR-101 input VAT credit only against a valid Mushak 6.3, NFR-083 Labour Act compliance, NFR-088 records retention per the statutory schedule
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M51_Tax_and_Regulatory_Compliance_Bangladesh.md §19 — VAT & SD Act 2012 / VAT & SD Rules 2016 Rule 40(1) prescribes Mushak 6.3 and Mushak 9.1 is the monthly return; Income Tax Act 2023 withholding sections, Third Schedule depreciation, July–June income year; Finance Ordinance 2025, SRO 182-Ain/2025/310-Mushak and VDS Rules 2025 for FY 2025-26 TDS and VDS rates with VDS mandatory for 45 specified services
    verified: 2026-08-20
    class: P1
  - source: Company income tax return submission deadline for AY 2025–26 is 15 March per the NBR Income Tax Paripatra. https://vatax.bd/company-tax-return-submission-deadline/ and https://hsa.com.bd/blog/key-tax-deadlines-bangladesh-2026
    verified: 2026-08-20
    class: P2
  - source: RJSC annual return is filed as Schedule X (annual summary of share capital and list of shareholders) within 21 days of the Annual General Meeting under the Companies Act 1994 section 36 — a deadline derived from an internal event, not a fixed calendar date. https://hsa.com.bd/blog/rjsc-filing-requirements-bangladesh and https://vatax.bd/rjsc-annual-return-filing/
    verified: 2026-08-20
    class: P2
supersedes: none
review_due: 2027-02-20
---

# Statutory and Regulatory Report Format Register

| Item | Value |
|---|---|
| Content class | **A — statutory.** The only class-`A` file in Category 14 |
| Approval | CFO with Legal Counsel, **plus external verification** (`CG-002` §5.1) |
| Obligations registered | **21** (§4.3) |
| Authorities | NBR · RJSC · Bangladesh Bank · DIFE · NDMA · BIDA *(as applicable)* |
| Filing calendar basis | Fiscal year **July–June** (`MD-041`) |
| Wave | W3 · `P1` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), which
> `CG-009` assigns to all `RP` files, with the `RP` table addition applied as the obligation schema in
> §4.2. All six sections retained in order.
>
> **`CG-009` allocates no Legal Document template to this file, and that is correct**: this is a
> *register of obligations*, not a legal instrument. `LG-001` is the legal content register and uses
> template 1 for the same reason. Recorded so a reviewer does not reallocate it to template 10.

---

## 1. Purpose

Every other file in this category can be wrong and cost a decision. **This one costs money and
standing.** `06-02` `G3-04` requires *"Mushak invoices accepted with zero NBR exceptions"*; `KPI-057`
targets VAT returns filed on time with zero adjustment at 100%; `KPI-058` targets tax compliance
findings at zero. Those are not stretch goals — a VAT return filed late attracts interest and penalty
irrespective of intent.

The register's justification states the mechanism: *"statutory deadlines do not move; a missed format
requirement is discovered at filing time."* By then the period is closed, the data is fixed, and the
only options are a late filing or an incorrect one.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| A single register of obligations | Each obligation is known by the person who happens to handle it. `AUDIT-013` already found `LG-024`'s obligation register carrying uncertainty markers throughout and its licence register **empty** |
| Deadline derivation | A deadline stated as a date is wrong for the obligations whose deadline derives from an event — the RJSC Schedule X falls **21 days after the AGM**, not on a calendar date (§4.4) |
| Format specification | The output is built to our reading of the rule and validated by the regulator's rejection |
| Submission route | `NFR-100` names the NBR VAT Online portal; several others have no recorded route at all |
| A named filer | An obligation with no name against it is filed by whoever remembers |
| Retention | `NFR-088` enforces a statutory schedule; a filing is the record that proves compliance and is itself subject to it |

---

## 2. Scope

**In scope.** Every externally mandated periodic or event-driven submission: its authority, legal
basis, prescribed format, deadline and derivation, submission route, source data, preparer, reviewer,
approver, filer, evidence and retention. The escalation path when a deadline is at risk.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The **documents** themselves — Mushak 6.3 challan, registers, payslip layouts | **Category 05 `DT`** — `DT-010`…`DT-014`, `DT-041`. This register says *what must be filed and when*; `DT` specifies *what it looks like* |
| Tax determination, rates and computation logic | `M51` |
| Internal management and operational reports | `RP-002` |
| The board pack | `RP-010` |
| Legal texts, notices and disclosures | `LG-024`, `LG-001` |
| Data-protection breach notification to the NDMA | **`M60` and `LG-012`** — an incident-driven notification, not a periodic report. §4.5 states the boundary |
| Statutory registers maintained continuously rather than filed | `M51`; §4.3 lists them as `Maintain` obligations for completeness |
| Verification that output is correct | **`TS-009`** finance UAT; **`TS-010`** payroll |
| Retention enforcement mechanics | `M24` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **CFO** (approver) | The filing calendar and the exposure |
| **Finance Manager** (`R26`) | Preparation, review and submission |
| **Company Secretary** | RJSC and corporate obligations |
| **HR Manager** (`R30`) | Labour and payroll statutory filings |
| **Legal Counsel** (approver) | The legal basis of each obligation |
| **External tax adviser** | The verification `CG-002` §5.1 requires of a class-`A` file |
| **BI Lead** | The `RP-004` `C7` panel 6 statutory panel and the source datasets |
| **QA** (`TS-009`) | What finance verifies before `G3` |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **ST-01** | **Every obligation names its legal instrument**, section or rule, with a verification date (`CG-012`, `CM-R8`). *"NBR requires it"* is not a basis |
| **ST-02** | **Every deadline states how it is derived** — a fixed calendar date, an offset from period end, or **an offset from an internal event** (§4.4). The third class is the one that gets missed |
| **ST-03** | **Every obligation names four people**: preparer, reviewer, approver and filer. The approver and the filer may not be the same person |
| **ST-04** | **Format is taken from the instrument or the portal's published schema**, never from a previous filing. A format that changed silently is discovered by rejection |
| **ST-05** | **Every filing is compiled from the system, not from a spreadsheet** (`06-02` §5 criterion 1; `NFR-100`'s "auto-compiled" intent). A manual compilation step is recorded as an exception with a target date to remove it |
| **ST-06** | **Every filing reconciles to the ledger before submission**, and the reconciliation is the evidence (`TS-009` `UA-30`) |
| **ST-07** | **No filing is submitted on an unverified reading of the instrument.** Where the reading is uncertain the filing is escalated under `CG-013`, not filed on assumption (`TS-009` `UA-27`) |
| **ST-08** | **Every submission produces an acknowledgement, and the acknowledgement is the evidence of filing** — not the act of pressing submit |
| **ST-09** | **Every filing and its acknowledgement is retained as a compliance record** through `M24` for the statutory period (`NFR-088`, `NFR-095`), not as a report artefact |
| **ST-10** | **A deadline at risk escalates at a stated lead time**, not on the day (§4.6) |
| **ST-11** | **A late or amended filing is recorded with its cause**, and an amendment is never made silently |
| **ST-12** | **Every obligation states its penalty exposure** where known, so prioritisation is informed rather than intuitive |
| **ST-13** | **The register is reviewed on every Finance Act, Finance Ordinance or SRO**, because rates and sometimes formats change annually (`CG-006` §5 statutory pinning) |
| **ST-14** | **Bengali is used where the instrument requires it** — the Mushak 6.3 challan carries Bengali (`DT-010`); the filings themselves follow the portal's language |

### 4.2 The obligation schema

| # | Field | Content |
|---:|---|---|
| 1 | `id` | `STR-nn`, permanent |
| 2 | `obligation` | The name the authority uses |
| 3 | `authority` | NBR · RJSC · Bangladesh Bank · DIFE · NDMA · other |
| 4 | `instrument` | Act, rule, section or SRO, with a verification date (`ST-01`) |
| 5 | `type` | `File` · `Maintain` · `Issue` · `Notify` |
| 6 | `frequency` | Per transaction · monthly · quarterly · annual · event-driven |
| 7 | `deadline` | The date **and its derivation** (`ST-02`) |
| 8 | `format` | Prescribed form and its version |
| 9 | `route` | Portal, physical, or agent — with the URL where one exists |
| 10 | `source` | The `RP-006` dataset or `DT` output it is compiled from |
| 11 | `preparer` / `reviewer` / `approver` / `filer` | Four named roles (`ST-03`) |
| 12 | `reconciliation` | What it must tie to before submission (`ST-06`) |
| 13 | `evidence` | The acknowledgement retained (`ST-08`) |
| 14 | `retention` | Period and basis (`NFR-088`) |
| 15 | `penalty` | Exposure for late or incorrect filing (`ST-12`) |
| 16 | `verification` | External adviser confirmation status (`CG-002` §5.1) |

### 4.3 The register — 21 obligations

**VAT and indirect tax — NBR**

| `id` | Obligation | Instrument | Type | Frequency | Deadline and derivation |
|---|---|---|---|---|---|
| `STR-01` | **Mushak 6.3 tax invoice** | VAT & SD Rules 2016 Rule 40(1) | Issue | Per taxable sale | **At the time of supply** — event-derived |
| `STR-02` | **Mushak 9.1 monthly VAT return** | VAT & SD Act 2012; `NFR-100` | File | Monthly | **15th of the following month**, via `vat.gov.bd` |
| `STR-03` | Mushak 6.1 purchase register | VAT & SD Rules 2016 | Maintain | Continuous | Reconcilable at all times |
| `STR-04` | Mushak 6.2 sales register | VAT & SD Rules 2016 | Maintain | Continuous | Reconcilable at all times |
| `STR-05` | Mushak 6.2.1 register | VAT & SD Rules 2016 | Maintain | Continuous | — |
| `STR-06` | Mushak 6.5 stock transfer register | VAT & SD Rules 2016 | Maintain | Continuous | — |
| `STR-07` | **Mushak 6.6 VDS certificate** | VDS Rules 2025 | Issue | Per deduction | On deduction, to the supplier |
| `STR-08` | Mushak 6.7 / 6.8 credit and debit notes | VAT & SD Rules 2016 | Issue | Per event | On issue |
| `STR-09` | **Input VAT credit claim** | `NFR-101` | File | Monthly, with `STR-02` | **Only against a valid Mushak 6.3** — the system blocks otherwise |

**Direct tax and withholding — NBR**

| `id` | Obligation | Instrument | Type | Frequency | Deadline and derivation |
|---|---|---|---|---|---|
| `STR-10` | **TDS / VDS deduction at source** | Income Tax Act 2023 withholding sections; SRO 182-Ain/2025/310-Mushak; VDS Rules 2025 (**VDS mandatory for 45 specified services**) | Issue | Per applicable payment | At payment |
| `STR-11` | **TDS challan deposit** | Income Tax Act 2023 | File | Per deduction cycle | Per the prescribed deposit window |
| `STR-12` | TDS certificate to the payee | Income Tax Act 2023 | Issue | Per deduction | Per the prescribed window |
| `STR-13` | Withholding return | Income Tax Act 2023 | File | Periodic | Per the prescribed schedule |
| `STR-14` | **Company income tax return** | Income Tax Act 2023; NBR Income Tax Paripatra | File | Annual | **15 March** for AY 2025–26 · income year **July–June** |
| `STR-15` | Import duty and VAT at import | Customs Act; VAT & SD Act 2012 | File | Per shipment | At clearance; allocated to landed cost (`BRU-SCM-04`) |

**Corporate — RJSC**

| `id` | Obligation | Instrument | Type | Frequency | Deadline and derivation |
|---|---|---|---|---|---|
| `STR-16` | **Annual return, Schedule X** — annual summary of share capital and list of shareholders | Companies Act 1994 **s.36** | File | Annual | **Within 21 days of the AGM** — **event-derived, not a calendar date** (§4.4) |
| `STR-17` | Form XII and other change filings — directors, registered office, capital | Companies Act 1994 | File | Event-driven | Within the prescribed window of the change |
| `STR-18` | Audited financial statements filed with the annual return | Companies Act 1994 | File | Annual | With `STR-16` |

**Labour, payroll and people — DIFE and others**

| `id` | Obligation | Instrument | Type | Frequency | Deadline and derivation |
|---|---|---|---|---|---|
| `STR-19` | Statutory payroll deductions and their deposit | Bangladesh Labour Act 2006 as amended; `NFR-083` | File | Monthly | Per the prescribed window |
| `STR-20` | Labour and establishment returns | Bangladesh Labour Act 2006; Labour Rules | File | Periodic | Per the prescribed schedule |

**Data protection — NDMA**

| `id` | Obligation | Instrument | Type | Frequency | Deadline and derivation |
|---|---|---|---|---|---|
| `STR-21` | **Processing records retained for a minimum of five years** | Personal Data Protection Act 2026; `NFR-095` | Maintain | Continuous | Five years minimum |

> **Breach notification to the NDMA (`NFR-094`) is deliberately not `STR-22`.** It is
> **incident-driven**, owned by `M60` and `LG-012`, and belongs to an incident procedure rather than a
> filing calendar. Registering it here would place a same-day obligation in a monthly register and
> attach the wrong control regime — the distinction `RP-002` §4.1 draws between a report and a filing,
> applied again. §4.5 records the seam.

### 4.4 Deadline derivation — three classes, and the one that gets missed

`ST-02` exists because deadlines are not all the same kind of thing.

| Class | Example | Control |
|---|---|---|
| **Fixed calendar date** | `STR-14` company income tax return, 15 March | A calendar entry works |
| **Offset from period end** | `STR-02` Mushak 9.1, 15th of the following month | A calendar entry works, driven by `MD-041` |
| **Offset from an internal event** | **`STR-16` Schedule X, within 21 days of the AGM**; `STR-17` change filings; `STR-01` at time of supply | **A calendar entry does not work.** The clock starts when the company does something |

**The third class is the one this register exists to catch.** The AGM date is chosen by the company,
often late, and the 21-day clock starts from it — so the filing deadline is unknowable until the AGM is
convened, and a fixed 15 January or 31 July calendar reminder would be wrong in either direction.

| # | Rule |
|---|---|
| **ST-15** | **An event-derived deadline is triggered by the event in the system**, not by a calendar. The AGM record, the change record or the supply event starts the clock |
| **ST-16** | **Every event-derived obligation names the system event that starts its clock**, and where no such event exists in any module the gap is recorded (§4.6 `O-03`) |

### 4.5 Boundaries with three neighbouring registers

| Neighbour | Holds | Seam |
|---|---|---|
| **`LG-024`** Regulatory Disclosure and Statutory Notice Register | Notices, disclosures and the regulator-handling procedure; the obligation and licence registers | **`LG-024` holds *what we must tell people and hold licences for*; this file holds *what we must submit periodically*.** `AUDIT-013` records `LG-024`'s obligation register as carrying uncertainty markers throughout and its licence register as **empty** — so the two must be reconciled, not assumed complementary. `O-02` |
| **`M60`** / **`LG-012`** | Breach notification, data-protection compliance | Incident-driven notification stays there (§4.3 note) |
| **Category 05 `DT`** | The rendered artefacts | `DT-010`…`DT-014`, `DT-041`. **26 `DT` files are blocked on gate `G6` external verification** (`AUDIT-007`), and every statutory output in this register is one of them. `O-01` |

### 4.6 The filing calendar and escalation

`ST-10` requires escalation at a lead time, not on the day.

| Lead time | Action | To |
|---|---|---|
| **T−15 working days** | Obligation appears on `RP-004` `C7` panel 6 with its source reconciliation state | Finance Manager |
| **T−10** | Preparation must be complete; reconciliation run (`ST-06`) | Finance Manager |
| **T−5** | Review complete; **any unresolved reading escalated under `CG-013`** (`ST-07`) | CFO, Legal Counsel |
| **T−2** | Approved and ready to file | CFO |
| **T−0** | Filed; acknowledgement retained (`ST-08`, `ST-09`) | Filer |
| **T+1, no acknowledgement** | Escalate as a compliance incident | CFO, Company Secretary |

**Event-derived obligations run the same ladder from the event**, not from a date — `STR-16` starts at
the AGM record and its T−0 is AGM + 21 days.

### 4.7 Verification — why this file cannot be approved internally

`CG-002` §5.1 requires class-`A` content to carry external verification, and `CG-007` requires a named
approver. This register asserts what the law requires of the company; **an internal reading of a
statute is a position, not a verification.**

| Element | Verified by |
|---|---|
| Instrument citation and section for all 21 obligations | External tax adviser and Legal Counsel |
| Deadlines, especially the event-derived class | External adviser; Company Secretary for RJSC |
| Formats and portal schemas | Confirmed against the authority's published form, not a prior filing (`ST-04`) |
| Penalty exposure | Legal Counsel |
| VDS applicability across the 45 specified services | **External adviser** — this is the most rate- and scope-volatile item in the register |

**No filing proceeds on this register until §4.7 is complete** (`ST-07`). That is the same block
`TS-009` `O-01` records from the test side and `AUDIT-007` records for 26 `DT` files.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M51` | Tax determination, registers, return compilation |
| **`DT-010`…`DT-014`, `DT-041`** | The rendered statutory artefacts — all `G6`-blocked |
| `MD-037`, `MD-040`, `MD-041` | Tax codes and Mushak mapping, document sequences, fiscal calendar |
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | The datasets each filing is compiled from (`ST-05`) |
| [`RP-004`](RP-004_Dashboard_Specification_Pack_Operational_Consoles.md) `C7` panel 6 | Where the calendar becomes visible to the finance team |
| [`RP-014`](RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) | Marking on any export of a filing |
| `M24` | Retention of filings and acknowledgements (`ST-09`) |
| [`LG-024`](../10_Legal_Policy_and_Compliance/LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md), `LG-001` | The neighbouring obligation and legal registers (`O-02`) |
| **`TS-009`**, `TS-010` | Where output correctness is proved by Finance and HR |
| `CG-007`, `CG-012`, `CG-013` | Sign-off, evidence and escalation |
| `SP-020`, `SP-021` | The close and payroll procedures that produce the data |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annually on the Finance Act / Finance Ordinance**, and on any SRO affecting rates, scope or format (`ST-13`) |
| Trigger for out-of-cycle review | A new SRO; a portal schema change; a rejected filing; a new authority; an AGM date being set (`ST-15`); an entity added (`M65`) |
| Owner | Finance Manager, with Legal & Compliance |
| Data file | `RP-009_Obligation_Register.csv` — 21 obligations × 16 fields · `RP-009_Filing_Calendar.csv` · `RP-009_Acknowledgement_Log.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No external verification exists for any of the 21 obligations**, and `CG-002` §5.1 requires it for class-`A` content. `AUDIT-007` records **26 `DT` files blocked on gate `G6`** and every statutory output here is one of them; `TS-009` `O-01` records the same block from the test side. **`ST-07` means no filing proceeds until this is closed** — and `G3-04` at Month 13 requires Mushak accepted with zero NBR exceptions | CFO with Legal Counsel and an external tax adviser | **W3 — before `G3`; the single hard blocker** |
| **O-02** | **`LG-024`'s obligation register carries uncertainty markers throughout and its licence register is empty** (`AUDIT-013`). This file registers 21 *filings*; `LG-024` registers *obligations and licences*. **Neither is complete and the two have never been reconciled**, so the company does not have a single answer to "what must we submit, hold and disclose?" | Legal Counsel with Finance Manager | **W3** |
| **O-03** | **`ST-16` requires every event-derived obligation to name the system event that starts its clock, and for `STR-16` there is no such event.** No module holds an AGM record — `M60` governance and `M67` project management are the candidates and neither specifies one. **The 21-day Schedule X clock therefore has no trigger in the system** | Company Secretary with Solution Architect | **W3** |
| **O-04** | **Several deadlines are recorded as "per the prescribed window" or "per the prescribed schedule"** — `STR-11`, `STR-12`, `STR-13`, `STR-17`, `STR-19`, `STR-20`. Those are placeholders, not deadlines, and each needs the instrument's actual period. **Recorded as unknown rather than guessed** (`CG-012`), and they are the most likely source of a first missed filing | Finance Manager with the external adviser | **W3 — with `O-01`** |
| **O-05** | **VDS applies to 45 specified services under VDS Rules 2025 and the list is not held anywhere in the content set.** `MD-037` holds tax codes and Mushak mapping; whether all 45 are mapped, and which of the company's fourteen revenue streams fall inside them, is unverified. **A missed VDS deduction is recovered from the company, not the supplier** | Finance Manager with the external adviser | **W3** |
| **O-06** | **`ST-05` requires compilation from the system and `M51` is a W4 module** while this file is W3 and `G3` falls at Month 13. Until `M51` is live, `STR-02`'s return is compiled with manual steps — which `ST-05` permits only as a recorded exception with a removal date | Finance Manager with CTO | **W3** |
| **O-07** | **`STR-21` PDPA processing records are a `Maintain` obligation whose enforcement activates ~13 May 2027, inside Wave 4** (`05-06` §6.1). This register records the retention duty; **what a "processing record" must contain is `M60`/`LG-012` work that does not exist**, so the five-year clock may already be running on records not being kept | Chief Data Officer with Legal Counsel | **W3 — before 13 May 2027** |
| **O-08** | **`M65` multi-entity is a W9 capability and `06-02` `G9-01` requires a second-country entity by configuration.** Every obligation here is Bangladesh-specific; **a second jurisdiction multiplies this register and nothing states who maintains the second set** | CFO with CTO | W9 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 per `CG-009`, with the reason it is not a Legal Document template recorded
- [x] **Content class `A` — the only statutory-class file in Category 14 — with external verification required before any filing**
- [x] Sixteen rules stated, including compile-from-the-system, reconcile-before-submit and escalate-don't-assume
- [x] Sixteen-field obligation schema including four named people and penalty exposure
- [x] **21 obligations registered across NBR, RJSC, labour and data protection, each with its instrument**
- [x] **Deadline derivation split into three classes, with the event-derived class identified as the one that gets missed**
- [x] `STR-16`'s 21-days-after-AGM deadline sourced externally and its lack of a system trigger raised
- [x] External sources carry verification dates: 15 March income tax return, 21-day Schedule X, Mushak 9.1 by the 15th, VDS on 45 services
- [x] Breach notification deliberately excluded, with the reason and the seam recorded
- [x] Boundaries drawn against `LG-024`, `M60`/`LG-012` and Category 05 `DT`
- [x] A T−15 to T+1 escalation ladder that also runs from an event for the event-derived class
- [x] **Placeholders recorded as unknown rather than guessed (`O-04`), per `CG-012`**
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` no external verification — outstanding; blocks every filing and `G3-04`**
- [ ] **`O-02` `LG-024` reconciliation — outstanding; no single answer on obligations**
- [ ] **`O-03` no AGM event to start the Schedule X clock — outstanding**
- [ ] **`O-04`/`O-05` six deadlines and the 45-service VDS list unknown — outstanding**
- [ ] Named approvers recorded — **pending CFO and Legal Counsel; external verifier not appointed**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
