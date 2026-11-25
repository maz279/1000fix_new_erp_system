---
id: DT-014
title: VAT Return Pack — Mushak 9.1
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Tax with Finance
author: Tax with Finance and Content Design
reviewers: [External tax adviser, Finance, Internal Audit, Platform Engineering, Treasury]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The statutory VAT return itself, and the supporting schedules that must accompany it. This is
  the filing — late, incomplete or unsupported submission carries penalty and audit consequence,
  and the return is the document against which every other Mushak record is tested. Everything
  else in 05B exists so that this can be produced correctly and on time.
traces_to: [M51, M19, M20, M50, M52, DT-001, DT-010, DT-011, DT-012, DT-013, DT-015, MD-035, MD-037, MD-041, RP-009, AP-002, 05-06 NFR-100]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-014_VAT_Return_Pack_Mushak_9_1_BN.md
sources:
  - source: VAT and Supplementary Duty Rules 2016, Form Mushak 9.1 — VAT return. **The prescribed form and its schedules must be obtained from the enacted Rules and verified at G6**
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-100 — Mushak 9.1 filed by the 15th of the following month through the NBR VAT Online portal
    verified: 2026-08-15
    class: P1
  - source: Secondary guidance describes a quarterly filing obligation in Form Mushak 9.1 within 15 days of quarter-end for certain registered persons. **This conflicts with the monthly-by-the-15th basis in 05-06 NFR-100 and must be resolved at G6 — see §2.2**
    verified: 2026-08-15
    class: P3
  - source: VDS withheld is adjustable on receipt of a Mushak 6.6 certificate in the month of payment or a subsequent window
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-014 — VAT Return Pack (Mushak 9.1)

> ⚠ **Tier S — the form is prescribed. Gate G6 mandatory and unwaivable (`WV-02`).**
>
> **This is the filing.** `DT-010` through `DT-013` are the records; this is the declaration made
> to the state on the strength of them. It is signed by a named officer, it is late or it is not,
> and it is either supported by the registers or it is an unsupported assertion.
>
> **There is an unresolved conflict about the filing frequency itself.** See §2.2. It is the
> single most important open question in Category 05, because it determines the period structure
> of every register beneath it.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Statutory VAT return and supporting schedule pack** |
| Owning module | `M51`, with `M19`, `M20`, `M50` and `M52` |
| Statutory | **Yes — Tier S.** VAT & SD Rules 2016, Form Mushak 9.1 |
| Recipient(s) | NBR via the VAT Online portal; internal audit; external adviser; company record |
| Languages | **Bilingual.** The prescribed form's language governs |
| Output formats | A4 portrait (form) + A4 landscape (schedules) · **structured submission to the NBR portal** · PDF/A-3 archive of the filed pack |
| Numbering mask | Not sequenced. Identified by **entity + tax period** |
| Retention period | **At least 5 years** from the end of the tax period — confirmed at G6 |
| Fiscal pin | **FY2026-27** |
| **Filing deadline** | **By the 15th of the following month** per `05-06` NFR-100 — **contested, see §2.2** |

### 1.1 The pack

| # | Component | Source | Mandatory |
|---:|---|---|:--:|
| 1 | **Mushak 9.1 return form** | Computed from the registers | ✔ |
| 2 | Output-tax schedule | `DT-011` sales register | ✔ |
| 3 | Input-tax schedule | `DT-012` purchase register | ✔ |
| 4 | Decreasing-adjustment schedule (VDS suffered) | `DT-013` certificates **received** from customers | ✔ where applicable |
| 5 | Increasing-adjustment schedule (VDS deducted) | `DT-013` certificates **issued** to suppliers | ✔ where applicable |
| 6 | Credit / debit note schedule | `DT-015` | ✔ where applicable |
| 7 | Export / zero-rated schedule | `DT-011` segregation | ✔ where applicable |
| 8 | Treasury payment evidence | `M50` deposit references | ✔ where a payment is due |
| 9 | Reconciliation statement to the general ledger | `M19` | **Internal, not filed** — but required before filing (§5.1) |

> Components 2–8 are **the prescribed schedules as we currently understand them**. G6 replaces
> this list with the actual schedule set.

---

## 2. Statutory Requirements

> All rows **unverified pending G6**.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Prescribed form title — *Mushak 9.1* | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Registered person's name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Tax period | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Total value of supplies made | VAT & SD Rules 2016 — **pending G6** | pending | Output section |
| Output VAT by rate band | VAT & SD Rules 2016 — **pending G6** | pending | Output section |
| Supplementary duty payable | VAT & SD Rules 2016 — **pending G6** | pending | Output section |
| Total value of purchases | VAT & SD Rules 2016 — **pending G6** | pending | Input section |
| Input VAT claimed | VAT & SD Rules 2016 — **pending G6** | pending | Input section |
| Decreasing adjustments | VAT & SD Rules 2016 — **pending G6** | pending | Adjustment section |
| Increasing adjustments | VAT & SD Rules 2016 — **pending G6** | pending | Adjustment section |
| Net VAT payable or refundable | VAT & SD Rules 2016 — **pending G6** | pending | Net section |
| Treasury deposit particulars | VAT & SD Rules 2016 — **pending G6** | pending | Payment section |
| Declaration by the registered person | VAT & SD Rules 2016 — **pending G6** | pending | Statutory block |
| Signature of the authorised officer | VAT & SD Rules 2016 — **pending G6** | pending | Signature zone |

### 2.2 ⚠ Unresolved: monthly or quarterly?

Two positions are in the programme's evidence base and they contradict each other.

| Position | Source | Class |
|---|---|:--:|
| **Monthly**, filed by the 15th of the following month | `05-06` NFR-100 — our own non-functional requirement | P1 |
| **Quarterly**, filed within 15 days of quarter-end, for certain registered persons availing input tax credit | Secondary commentary encountered in research, 2026 | **P3** |

| # | Consequence of not resolving this |
|---|---|
| **FQ-01** | The **tax period** is the organising unit of `DT-011` and `DT-012`. If it is wrong, both registers are structured wrongly and cannot be corrected retrospectively without regeneration — which `FZ-04` prohibits |
| **FQ-02** | The `M19` period-close calendar in `MD-041` is built on it |
| **FQ-03** | The `05-03` NBR portal integration submits on it |
| **FQ-04** | Cash-flow forecasting for the VAT payment depends on it |
| **FQ-05** | A `P3`-class secondary source **cannot** be allowed to sit unresolved against a `P1` internal requirement. `CG-012` EV-02 forbids relying on secondary summaries, and audit precedent `00-07` H2-13 records exactly this failure mode |

> **This is G6 question T1, and it is answered first.** Not because it is the hardest, but
> because everything else in 05B is shaped by the answer.

### 2.3 G6 questions specific to the return

| # | Question |
|---|---|
| **T1** | **What is our filing frequency and deadline, given our registration type and turnover?** (§2.2) |
| **T2** | Provide the current prescribed Mushak 9.1 and its complete schedule set |
| **T3** | Is filing exclusively electronic through the VAT Online portal, or is a physical filing also required? |
| **T4** | What is the payment mechanism and deadline relative to the filing deadline? |
| **T5** | What is the procedure and window for an **amended return**? |
| **T6** | How is a refund position handled, and what evidence must accompany it? |
| **T7** | What are the penalty provisions for late filing, late payment and understatement? |
| **T8** | What is the record-retention obligation for the filed pack and its supporting registers? |
| **T9** | Is any real-time or e-invoicing obligation applicable that would change how output data reaches this return? (paired with `DT-010` Q10) |
| **T10** | Where a group of entities exists, is filing per entity or consolidated? (`M65` multi-entity) |

---

## 3. Layout

**Form: A4 portrait, prescribed. Schedules: A4 landscape.**

| Zone | Content | Bilingual |
|---|---|---|
| Header | Prescribed title, entity, BIN, VAT circle, tax period | Per the instrument |
| Body | Prescribed sections: output, input, adjustments, net | Per the instrument |
| Totals | Net VAT payable or refundable | Arabic numerals |
| Statutory block | Prescribed declaration, verbatim | Per the instrument |
| Signature | Authorised officer, with designation and date | — |
| Footer | Entity, period, `page n of m`, pack component `n of 9` | English |

| # | Rule |
|---|---|
| **L-14-a** | The form is reproduced exactly. Schedules follow the prescribed format where one exists, and `VB-004` geometry where one does not |
| **L-14-b** | Every schedule carries the entity, BIN and tax period in its own header. A schedule separated from the pack must still identify itself |
| **L-14-c** | The pack is paginated **as a whole** — `page n of m` across the full pack — and each component also states `component n of m` |
| **L-14-d** | The declaration never splits |
| **L-14-e** | The filed pack is archived as **one PDF/A-3 file**. A pack held as loose components is a pack that loses a component |

---

## 4. Field Mapping

The return's own fields are computed, not captured. Each traces to a register, and the trace is
the auditable part.

| Return line (indicative) | Label BN | Derived from | Reconciles to |
|---|---|---|---|
| Total supplies made | মোট সরবরাহ | `DT-011` period total, value excl. VAT | `M19` revenue accounts |
| Output VAT by band | হার অনুযায়ী আউটপুট ভ্যাট | `DT-011` band subtotals | `M19` output-VAT liability (`MD-035`) |
| Supplementary duty | সম্পূরক শুল্ক | `DT-011` SD column | `M19` SD liability |
| Total purchases | মোট ক্রয় | `DT-012` period total | `M19` purchase accounts |
| Input VAT claimed | দাবিকৃত ইনপুট ভ্যাট | `DT-012` **reclaimable subtotal only** | `M19` input-VAT asset |
| Decreasing adjustment — VDS suffered | কর্তন সমন্বয় (প্রাপ্ত) | `DT-013` certificates **received** | `M20` receivable net position |
| Increasing adjustment — VDS deducted | কর্তন সমন্বয় (প্রদত্ত) | `DT-013` certificates **issued** | `M50` treasury deposits |
| Credit / debit note adjustments | সমন্বয় নোট | `DT-015` schedule | `M19` adjustment accounts |
| Exports / zero-rated | রপ্তানি / শূন্য হার | `DT-011` segregation | `M19` export revenue |
| **Net VAT payable / refundable** | **নিট প্রদেয় / ফেরতযোগ্য** | Computed | **`M19` VAT control account** |
| Amount deposited | জমাকৃত পরিমাণ | `M50.treasury_challan_ref` | Bank statement |

| # | Rule |
|---|---|
| **FM-14-a** | **Every return line is computed from a finalised register.** No line is entered by hand, and a line that cannot be traced to a register cannot be filed |
| **FM-14-b** | Input VAT claimed uses the **reclaimable subtotal only** (`DT-012` L-12-a). This is the single most common source of an overstated claim |
| **FM-14-c** | A decreasing adjustment for VDS suffered may only be taken where the `DT-013` certificate has been **received and recorded** — not where a deduction is merely expected |
| **FM-14-d** | The net position must equal the `M19` VAT control account balance for the period. A difference blocks filing (§5.1) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-FIN-05` | The period cannot be closed while unposted entries exist — the return would be incomplete |
| `BRU-FIN-06` | A hard-closed period reopens only on CFO approval, logged. **Reopening after filing triggers the G6 T5 amended-return procedure** |
| `BRU-FIN-07` | Foreign-currency balances revalued at period end at the official rate |
| `BRU-FIN-08` | The marketplace principal-or-agent model determines what appears as our supply |
| `BRU-FIN-09` | VDS/TDS correctness on vendor payments feeds the increasing-adjustment schedule |
| `TAX-05` (`MD-037`) | Every VAT code maps to at least one Mushak form — this is what makes the return derivable |
| `TAX-08` (`MD-037`) | A code unverified for more than 12 months blocks new transactions, and therefore protects the return |

### 5.1 The pre-filing gate

Filing is blocked until every one of these passes. This is the control that turns a return from
an assertion into a supported declaration.

| # | Gate | Blocks filing |
|---|---|:--:|
| **PF-01** | `DT-011` sales register finalised for the period (`FZ-01`) | ✔ |
| **PF-02** | `DT-012` purchase register finalised, **with no unresolved `D-8` duplicate** | ✔ |
| **PF-03** | All `DT-013` certificates due for the period **issued** | ✔ |
| **PF-04** | Register totals reconciled to `M19` VAT control account, **difference zero** | ✔ |
| **PF-05** | Period hard-closed in `M19` (`BRU-FIN-05`) | ✔ |
| **PF-06** | Treasury funding confirmed for the net payable (`M50`) | ✔ |
| **PF-07** | External adviser review recorded where the period contains an exception, a new supply type or a rate change | ✔ |
| **PF-08** | Named authorised officer available to sign | ✔ |

> **PF-04 has no tolerance.** A difference of any size between the registers and the general
> ledger means one of them is wrong, and filing before knowing which is filing a figure nobody
> can defend.

### 5.2 Late filing

| # | Rule |
|---|---|
| **LF-01** | The deadline is tracked in `MD-041` and alerted at T−7, T−3 and T−1 days (`NT-021`) |
| **LF-02** | A projected late filing is escalated to the CFO at T−3, not at T+1 |
| **LF-03** | A late filing is a **compliance incident** under `CG-013`, logged in `RF-011`, with cause analysis |
| **LF-04** | Penalty exposure per **G6 T7** is quantified and reported, not absorbed silently |
| **LF-05** | **A filing is never delayed to avoid disclosing an unfavourable position.** That decision belongs to the CFO with the adviser, and it is recorded |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Period return pack** | The governing filing | Form plus all applicable schedules, filed and archived as one PDF/A-3 |
| **Nil return** | A period with no taxable activity | Still filed. **A nil return is a filing obligation, not an exemption** |
| **Refund-position return** | Input exceeds output | Adds the evidence required by **G6 T6**; expect scrutiny and prepare for it |
| **Amended return** | Correction after filing | Per **G6 T5**. References the original; the original is retained (`CP-10`) |
| **Per-entity** | Multi-entity operation (`M65`) | One pack per entity unless G6 T10 permits consolidation |
| **Adviser review pack** | Pre-filing | Adds the `M19` reconciliation, exception notes and the register defect summary. **Not filed** |
| **Draft** | Mid-period forecasting | Watermarked **DRAFT**, no signature block, cannot be submitted (`RC-05`) |

---

## 7. Worked Example

> **Specimens produced only after G6 delivers the prescribed form and answers T1.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-014-S1` | Standard period, net payable | Base pack, all schedules, traceability to registers |
| `DT-014-S2` | Period with VDS suffered and VDS deducted | Both adjustment schedules |
| `DT-014-S3` | Period with credit notes | `DT-015` schedule |
| `DT-014-S4` | Refund position | G6 T6 evidence set |
| `DT-014-S5` | Nil return | Filing obligation with no activity |
| `DT-014-S6` | Amended return after a reopened period | G6 T5 path and original retention |

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Tax with Finance | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Treasury | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser; T1 answered first** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — Chief Financial Officer | *pending* | | |
| Per-period filing signature | Authorised officer per G6 | Per period | Recorded with the filed pack |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | None. Identified by **entity + tax period + version** (original / amended n) |
| Archive format | **One PDF/A-3 file per filed pack** (`L-14-e`), plus the structured submission payload and the portal acknowledgement |
| Acknowledgement | **The NBR portal acknowledgement is part of the archived pack.** A filing with no retained acknowledgement is a filing we cannot prove |
| Retention | **At least 5 years** from the end of the tax period — pending **G6 T8** |
| Re-render | **Prohibited absolutely.** The filed pack is the filed pack |
| Amendment | A new pack version referencing the original; the original is never replaced (`CP-10`) |
| Supporting registers | Retained for the same period, linked to the pack (`DT-011`, `DT-012`) |
| Reconciliation evidence | The `PF-04` reconciliation is archived with the pack |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | The output records |
| [`DT-011_Sales_Register_Mushak_6_2.md`](DT-011_Sales_Register_Mushak_6_2.md) | Output schedule source; must be finalised first |
| [`DT-012_Purchase_Register_Mushak_6_1.md`](DT-012_Purchase_Register_Mushak_6_1.md) | Input schedule source; reclaimable subtotal only |
| [`DT-013_VDS_Certificate_Mushak_6_6.md`](DT-013_VDS_Certificate_Mushak_6_6.md) | Both adjustment schedules |
| [`DT-015_Credit_Note_and_Debit_Note.md`](DT-015_Credit_Note_and_Debit_Note.md) | Adjustment schedule |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md) | VAT control accounts for `PF-04` |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Tax periods and deadline tracking |
| `05-03` Integration and API Catalogue — NBR VAT Online | Submission and acknowledgement |
| [`NT-021_System_Integration_and_Job_Failure_Alert_Library.md`](../../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) | Deadline and submission-failure alerts |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) | The operational sequence and the `PF` gate |
| `RP-009` Statutory and Regulatory Report Format Register | Production and reconciliation |
| `TS-009` UAT Script Pack — Finance Roles | Where the return's derivation is proven end to end |
| `RF-011` Content Risk Register | Where `FQ-05` and late-filing incidents are recorded |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Nine-component pack, the monthly-versus-quarterly conflict raised as G6 T1 with its five consequences, eight-gate pre-filing control with zero-tolerance reconciliation, five late-filing rules, acknowledgement-as-part-of-pack rule | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] **The filing-frequency conflict is raised explicitly rather than silently resolved** (§2.2)
- [x] Every return line traced to a register, none hand-entered (`FM-14-a`)
- [x] Pre-filing gate defined with no tolerance on reconciliation (`PF-04`)
- [x] Late-filing treated as a compliance incident with escalation
- [x] Portal acknowledgement made part of the archived pack
- [x] All internal links resolve
- [ ] **G6 T1 — filing frequency and deadline confirmed** — **outstanding, unwaivable; blocks the period structure of `DT-011`, `DT-012` and `MD-041`**
- [ ] **G6 T2 — prescribed form and schedule set obtained** — **outstanding, unwaivable (`WV-02`)**
- [ ] G6 T5 amended-return procedure — **outstanding; `M51` cannot implement corrections without it**
- [ ] G6 T7 penalty provisions quantified for `LF-04` — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
