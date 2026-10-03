---
id: LG-013
title: Service Terms, Warranty Terms and Exclusions
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Service Operations, Warranty Operations and Content Design
reviewers: [Legal Counsel, Operations Director, Warranty Officer, Quality Manager, CFO delegate, Content Design Lead, Localisation Lead, Accessibility reviewer]
approver: Legal Counsel
content_class: B
purpose: >
  The company's own warranty on the work it performs and the parts it supplies — scope, duration,
  what starts the clock, exclusions, the claim route, liability caps, the data-loss position and the
  uncollected-device regime. This is the principal consumer-facing liability limit in the business,
  it must be presented at intake and reproduced on the warranty certificate, and MD-031 hard-blocks
  activation of any warranty type whose exclusions do not match this file verbatim.
traces_to: [M09, M01, M31, M14, M20, M34, P01, P02, LG-001, LG-002, LG-014, LG-015, LG-017, DT-002, DT-005, DT-007, DT-009, DT-032, DT-033, MD-025, MD-026, MD-031, SP-013, SP-028, UI-038, HC-003, BRU-WTY-01, BRU-WTY-02, BRU-WTY-16, BRU-WTY-17, BRU-SRM-02, BRU-QMS-04, BRU-CXM-01, BRU-ESG-01, WTY-01, WTY-02, WTY-06]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: LG-013_Service_Terms_Warranty_Terms_and_Exclusions_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md §2 record structure — the exclusions column states "Must match LG-013 verbatim"; §4 validation rule WTY-02 makes a divergence a hard block on activation; WTY-06 prohibits changing coverage or exclusions on a type with issued warranties
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031 §9 sample rows — a 30-day repair warranty starting from service completion covering parts and labour with a 30-day claim window; manufacturer and extended-purchased classes
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09 §9 BRU-WTY-16 — repair warranty applies automatically to a return within its window and is charged to no one but 1000FiX; BRU-WTY-17 — a void condition must be evidenced before it is applied to refuse coverage; BRU-WTY-02 — before and after photographs are mandatory and the order cannot close without them
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-02 — a warranty-type service order can only be created if warranty is active at the service request date; BRU-QMS-04 — a complaint cannot be closed without confirming the outcome with the customer
    verified: 2026-08-18
    class: P1
  - source: Consumer Rights Protection Act 2009 — statutory limits on excluding consumer remedies and the complaint route to the Directorate of National Consumer Rights Protection. **Instrument-level citation from a secondary source; clause-level content is unverified and is pending G5**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-013 — Service Terms, Warranty Terms and Exclusions

| Item | Value |
|---|---|
| Document class | **Terms** — the company's repair warranty and its service liability position |
| Counterparty | Every service customer, consumer and business |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval*. **`W1`, ahead of the customer portal** |
| Acceptance capture method | **`AC-3` signature at intake on `DT-002`**, and reproduced on the warranty certificate `DT-032`. Where intake is digital, `AC-1` with the version recorded (`LG-001` `LR-06`) |
| Version accepted by users | Recorded in `LG-001`. **`WTY-06` prohibits changing coverage or exclusions on a warranty type with issued warranties — a change means a new type** |
| External counsel review | **Required** — the §5 caps, the §4.7 data-loss position and the §4.9 uncollected-device regime |
| Bengali version | **Required and operative.** These terms are presented at a counter, in Bengali, to a customer handing over a device |

> ⚠ **Class B, `P0`, `W1` — the earliest legal file the programme needs, and the one with a hard
> systemic dependency.**
>
> **`MD-031` §2 says the `exclusions` column "must match `LG-013` verbatim", and validation rule
> `WTY-02` makes a divergence a hard block on activating a warranty type.** That is the same control
> shape as `MD-028` `SLA-03` against `LG-015`: **master data will not activate unless this file's
> wording is copied into it exactly.**
>
> **§4.6 therefore publishes the canonical exclusion text as a numbered, quotable list.** It is not
> prose to be paraphrased into a data field.
>
> **Conformance note.** All ten template sections retained in order. The canonical exclusions are
> §4.6 within §4 Terms. Gate questions and open items are §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Service and Warranty Operations | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — Operations Director with Warranty Officer | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it matters |
|---|---|---|
| **WT1** | **Does a consumer-protection instrument prescribe mandatory warranty content?** If it does, this file is **Class A** and the Category 10 split becomes 7 A / 17 B | **`LG-001` `O-02`. A register change, not a local edit** |
| **WT2** | Are the §4.6 **exclusions** enforceable against a consumer, and which of them are at risk of being read as excluding a core obligation? | An exclusion struck down leaves the company covering the excluded case, and `MD-031` will already have been loaded with it |
| **WT3** | Is the **§5.2 liability cap** enforceable against a consumer, and at what level? | Same exposure as `LG-002` `CU1`; the answers must be identical |
| **WT4** | Is the **§4.7 data-loss position** enforceable, and does it survive where the loss was avoidable? | Same as `LG-002` `CU2`. **The two files must give one answer** |
| **WT5** | Is the **§4.9 uncollected-device regime** lawful — storage charge, then disposal after notice? What notice, to what address, and after how long? | Same as `LG-002` `CU3`. Disposing of another person's property |
| **WT6** | Is a **30-day repair warranty** defensible as the standard term, or does statute or market practice require longer? `MD-031` samples 30 days from service completion | The most-quoted number in the business |
| **WT7** | May the company **void** coverage for unauthorised third-party interference, and what evidence standard applies? `BRU-WTY-17` requires the void condition to be evidenced | An unevidenced void is a refusal a customer will win |
| **WT8** | Where a **manufacturer** warranty and the company's repair warranty both apply, may the company direct the customer to the manufacturer, or must it remedy first? | §4.4 takes a position |
| **WT9** | Is the **§4.10 no-fault-found charge** lawful where the customer reported a fault the company could not reproduce? | A common and contested charge |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `WT1`–`WT9` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | **`WT1` may reclassify this file to Class A**, adding G6 external verification and changing the `CG-002` §4.1 split. Registered in `LG-001` `O-02` | **Yes** | Legal Counsel |
| **O-03** | **`WT3`, `WT4` and `WT5` are the same three questions as `LG-002` `CU1`, `CU2` and `CU3`.** They must be answered **once**, and both files updated together, or the two documents will diverge on the company's principal consumer liability | **Yes — a single G5 instruction covering both files** | Legal Counsel |
| **O-04** | **`MD-031` §9 sample rows omit the required `device_families` and `exclusions` columns.** The record structure marks both mandatory; the CSV header has neither. **A load built from that sample cannot satisfy `WTY-02`, because the column carrying this file's text is absent** | **Yes — an upstream `MD-031` defect** | Master Data Owner |
| **O-05** | **`MD-031` expresses the 30-day repair warranty as `duration_months = 1`.** Thirty days and one month are not the same period, and the difference decides a claim made on day 31 of a 31-day month | **Yes — blocks §4.3** | Master Data Owner with Legal |
| **O-06** | **The storage-charge amount and the free period in §4.9 are undefined.** `MD-029` holds rate cards; no rate is published | **Yes — blocks §4.9** | CCO with Finance |
| **O-07** | **The no-fault-found charge in §4.10 is undefined** and is subject to `WT9` | Yes — blocks §4.10 | CCO with Legal |
| **O-08** | **This file is `W1`; `LG-014` refunds is `W2` and `LG-002` portal terms is `W2`.** The warranty terms go live one wave before the refund policy they interlock with, and before the terms that incorporate them | **Yes — sequencing** | Programme Content Lead |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited |
| **The Customer** | The person or organisation for whom the Company performs a service |

**In scope:** the Company's own repair warranty; what it covers and excludes; how a claim is made
and decided; the service liability position including data loss; device custody and uncollected
devices; and the interaction with a manufacturer warranty or a purchased protection product.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **Refunds, cancellation and compensation** | [`LG-014_Refund_Cancellation_and_Compensation_Policy.md`](LG-014_Refund_Cancellation_and_Compensation_Policy.md) — **a warranty remedy is not a refund** |
| **AMC, RAMC and SLA commitments, and service credits** | [`LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) |
| Portal account terms | [`LG-002_Portal_Terms_of_Use_Customer.md`](LG-002_Portal_Terms_of_Use_Customer.md) — **which defers to this file on warranty** |
| Data recovery and secure destruction | [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) |
| Personal data | `LG-008`, `LG-009`, `LG-012` |
| **A manufacturer's own warranty terms** | The manufacturer. The Company administers a claim; it does not set the brand's terms (`LG-005`) |
| The warranty-type catalogue and its data | [`../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md) — **it carries this file's text; it does not author it** |
| Protection-plan and extended-warranty product terms | `MD-031` `protection_plan` and `extended_purchased` classes, with their own certificate on `DT-032` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Repair warranty** | The Company's warranty on **its own workmanship and the parts it supplied**, for the fault it repaired |
| **Warranty period** | The duration from the start point in §4.3, as registered in `MD-031` for the applicable warranty type |
| **Claim window** | The period within which a claim must be raised — `claim_window_days` in `MD-031` |
| **Manufacturer warranty** | A brand's warranty on the device itself, administered by the Company where it is authorised (`LG-005`) |
| **Protection product** | A purchased extended warranty or protection plan, with its own terms and its own certificate |
| **Void condition** | A circumstance that removes coverage. **It must be evidenced before it is applied** (`BRU-WTY-17`) |
| **Recurrence** | The same fault, on the same device, within the warranty period |
| **No fault found** | The reported fault could not be reproduced or identified on inspection |
| **Governing text** | The **English** version (`LG-001` `LR-03`), with `LR-04` preserving the Bengali version's operative effect |

---

## 4. Terms

### 4.1 What the Company undertakes

| # | Clause |
|---|---|
| **4.1.1** | The Company performs the service with reasonable skill and care, by a technician competent for the work, using parts fit for the purpose |
| **4.1.2** | The Company records the device's stated condition at intake and issues a receipt for it (`DT-002`) |
| **4.1.3** | Chargeable work proceeds only on an approved estimate (`DT-005`, `LG-002` §4.4) |
| **4.1.4** | **Before and after photographs are taken on every warranty order and the order cannot close without them** (`BRU-WTY-02`). The Customer may ask for them |
| **4.1.5** | A completion report is issued stating what was done, what was replaced and what was tested (`DT-007`) |
| **4.1.6** | A quality check is passed before the device is released (`BRU-QMS-01`) |

### 4.2 What the repair warranty covers

| # | Clause |
|---|---|
| **4.2.1** | **The Company's workmanship** on the repair it performed |
| **4.2.2** | **The parts the Company supplied and fitted**, against failure in normal use |
| **4.2.3** | **Recurrence of the same fault** within the warranty period. **A return within the window is repaired at the Company's cost and is charged to no one but the Company** (`BRU-WTY-16`) |
| **4.2.4** | Coverage is **parts and labour** as registered for the type in `MD-031`, and may include collection where the type provides for it |
| **4.2.5** | Coverage is **transferable on resale only where the registered type says so** (`MD-031` `transferable`) |

### 4.3 Duration and when the clock starts

| # | Clause |
|---|---|
| **4.3.1** | The **standard repair warranty is 30 days from service completion**, covering parts and labour, with a **30-day claim window** — as registered in `MD-031` (`WTY-00101`), and **subject to `WT6`** |
| **4.3.2** | Some repair types carry a longer period, registered against the type. **The period that applies is the one registered when the service completed** |
| **4.3.3** | The start point is `starts_from` in `MD-031` — **service completion** for a repair warranty, purchase date for a manufacturer warranty, activation for a purchased product |
| **4.3.4** | The period, the start point and the claim window are printed on the warranty certificate (`DT-032`) and on the completion report (`DT-007`). **A term the Customer was not given is a term the Company should not rely on** |
| **4.3.5** | **`O-05`: "30 days" and "one month" are different periods.** `MD-031` currently registers the standard warranty as one month. **The operative period is 30 calendar days**, and `MD-031` must be corrected to express it in days |

### 4.4 Where a manufacturer warranty also applies

| # | Clause |
|---|---|
| **4.4.1** | Where the device is under a manufacturer warranty and the fault falls within it, the Company administers the claim to the brand where it is authorised to do so |
| **4.4.2** | **A manufacturer's decision is the manufacturer's.** The Company presents the evidence the brand's rules require (`DT-033`) and states the outcome and the reason |
| **4.4.3** | **A brand rejection does not by itself create a Company warranty obligation**, and does not remove one where the fault is in the Company's own work |
| **4.4.4** | Where both could apply, the Company **does not use the existence of a brand claim to delay a remedy the Customer is entitled to from the Company** — subject to `WT8` |
| **4.4.5** | Warranty work under a brand authorisation is performed by the Company or its authorised network. **It is never broadcast to the marketplace** (`BRU-MKP-09`) |

### 4.5 Making a claim

| # | Clause |
|---|---|
| **4.5.1** | A claim is raised in the portal, by hotline **16743**, or at any branch, within the claim window |
| **4.5.2** | The Customer provides the service order reference or the warranty certificate, and the device |
| **4.5.3** | **A warranty-type order can only be created where warranty is active at the request date** (`BRU-SRM-02`, `WTY-01`). Where it is not, the Company says so and quotes for the work instead |
| **4.5.4** | The Company inspects and decides. **A refusal states the ground and the evidence for it** (`BRU-WTY-17`) |
| **4.5.5** | Where the claim is accepted, the Company repairs, and where repair is not possible, applies the remedy in §4.11 |
| **4.5.6** | A dispute about a warranty decision runs as a complaint (`SP-028`), **and a complaint is closed only on the Customer's confirmation** (`BRU-QMS-04`, `BRU-CXM-04`) |

### 4.6 Exclusions — **the canonical text**

> **`CL-01`. This numbered list is the text `MD-031` must carry verbatim.**
> `MD-031` §2 marks the `exclusions` column *"Must match `LG-013` verbatim"*; `WTY-02` makes a
> divergence a **hard block on activation**; `WTY-06` prohibits changing it on a type with issued
> warranties. **The list is therefore written to be quoted, not summarised — each item numbered,
> self-contained, and independently arguable.** Every item is provisional pending `WT2`.

**The repair warranty does not cover:**

| # | Exclusion |
|---|---|
| **EX-01** | A fault different from the fault the Company repaired |
| **EX-02** | A part the Company did not supply, and a fault in a part the Customer supplied |
| **EX-03** | Damage caused after the device was released — impact, liquid, crushing, or misuse |
| **EX-04** | Liquid or moisture damage, and corrosion arising from it |
| **EX-05** | Damage caused by a power surge, incorrect voltage, or a non-approved charger or accessory |
| **EX-06** | Fair wear and tear, including battery capacity loss in normal use, cosmetic marking, and consumable deterioration |
| **EX-07** | **Interference with the repair by anyone other than the Company or a party the Company authorised**, including a broken warranty seal — **subject to `WT7` evidence** |
| **EX-08** | A device modified after release, including a changed operating system, unlocking, rooting or jailbreaking |
| **EX-09** | Software faults, configuration, data, applications and operating-system behaviour, except where the Company's own work caused them |
| **EX-10** | Loss of, or damage to, data — **the position is §4.7 and it is not simply excluded** |
| **EX-11** | A fault the Company disclosed as unrepaired, or a pre-existing condition recorded on `DT-002` at intake |
| **EX-12** | A device the Customer declined to have fully repaired, in respect of the work declined |
| **EX-13** | Theft, loss, fire, flood, lightning, and other insurable events |
| **EX-14** | Consequential loss — including lost income, lost data value, lost opportunity and inconvenience — **subject to §5** |
| **EX-15** | A device used outside its intended purpose or environmental limits |
| **EX-16** | Work performed on the Customer's express instruction against the Company's recorded advice |
| **EX-17** | A device whose identifiers have been altered or removed, so the repair cannot be tied to it |
| **EX-18** | Any period after the warranty period expires, and any claim raised after the claim window closes |

| # | Rule |
|---|---|
| **EX-R1** | **An exclusion is applied only where it is evidenced** (`BRU-WTY-17`). *"Probably liquid"* is not `EX-04` |
| **EX-R2** | **An exclusion the Customer was not given cannot be relied on.** The list is on `DT-032` and available at intake |
| **EX-R3** | **`EX-14` does not disapply §5.5.** Nothing in this list excludes liability that cannot lawfully be excluded |
| **EX-R4** | **This list is amended only in this file.** An amendment in `MD-031` is a data defect, and `WTY-02` will block the type rather than accept it |
| **EX-R5** | A new exclusion is a **MAJOR** change and requires a new warranty type for future work; issued warranties keep their list (`WTY-06`) |

### 4.7 Data on the device — the Company's position

| # | Clause |
|---|---|
| **4.7.1** | **The Customer is asked to back up their data before handing over a device**, at intake, on `DT-002`, and in the portal |
| **4.7.2** | Repair may require access to data on the device. **The Company does not copy or retain it** (`UI-042` §3.2) |
| **4.7.3** | **Some procedures carry an irreducible risk of data loss** — board-level work, storage replacement, factory reset, software reinstallation. Where the Company knows a procedure carries that risk, **it says so before the Customer approves it** (`UI-038`) |
| **4.7.4** | Where data is lost in the course of a repair, the Company will **attempt recovery at no charge where recovery is technically possible**, and will re-perform the service |
| **4.7.5** | **Chargeable data recovery is a separate service on separate terms** (`LG-017`), and the Company will not present a recovery charge for data it lost |
| **4.7.6** | The Company's liability for data loss is stated in §5.3 and is **provisional pending `WT4`** |
| **4.7.7** | **A device leaving the Company for recycling, refurbishment or disposal passes a certified destruction gate first** (`BRU-ESG-01`, `LG-017` §4.6). **A customer's data never leaves on a device the Company disposed of** |

> **`CL-02`. §4.7.1 is a disclosure and §4.7.4 is a remedy. Neither is a defence.** The substantive
> limit is §5.3, and if `WT4` refuses it the Company's exposure is what §4.7.4 offers plus whatever
> the law requires — which is why the sentence *"the Company does not copy or retain it"* in §4.7.2
> matters operationally: **the less data the Company holds, the less there is to lose.**

### 4.8 Device custody

| # | Clause |
|---|---|
| **4.8.1** | The Company holds the device as a custodian from intake to release, and records custody at each handover with time, place and both parties (`DT-028`) |
| **4.8.2** | The Company is responsible for loss of, or damage to, the device while in its custody, subject to §5 and to §4.8.3 |
| **4.8.3** | The Company is not responsible for a pre-existing condition recorded on `DT-002`, or for accessories and items the Customer did not declare and hand over |
| **4.8.4** | The device is released to the Customer or an authorised person, on identity verification, against a release receipt (`DT-009`) |

### 4.9 Uncollected devices — **pending `WT5`, `O-06`**

| # | Clause |
|---|---|
| **4.9.1** | The Company notifies the Customer when the device is ready and repeats the notification on the schedule in `NT-020` |
| **4.9.2** | Storage is free for a stated period. **A storage charge may apply after it, at the published rate** — `O-06` |
| **4.9.3** | After a longer stated period, and **after notice to the last contact details the Customer gave**, the Company may dispose of the device and apply proceeds against unpaid charges, accounting to the Customer for any surplus |
| **4.9.4** | **Any device disposed of under §4.9.3 passes the certified destruction gate first** (§4.7.7) |
| **4.9.5** | **Periods, notice content and notice method are `WT5`.** They are not drafted here and then defended |
| **4.9.6** | **The Company does not dispose of a device that is the subject of an open complaint or dispute** |

### 4.10 No fault found — **pending `WT9`, `O-07`**

Where the reported fault cannot be reproduced or identified, the Company reports what it tested and
what it found. **An inspection charge applies only where it was disclosed before the inspection
began** (`LG-002` §4.4.5). The device is returned in the condition it arrived in, and the report is
retained so a later recurrence can be linked to it.

### 4.11 Where repair is not possible

| # | Clause |
|---|---|
| **4.11.1** | Where a warranted fault cannot be repaired, the Company offers repair by another route, replacement of the failed part, or a remedy under `LG-014` |
| **4.11.2** | **The remedy for a warranty failure is not automatically a refund.** `LG-014` governs whether and how a refund arises |
| **4.11.3** | Where a device is replaced, the replacement carries the remainder of the original warranty period, not a new one, unless a new type is issued |
| **4.11.4** | Where a part is discontinued and no equivalent exists, the Company says so and the remedy moves to `LG-014` |

---

## 5. Liability, Exclusions and Limits

> **Every clause here is provisional pending `WT2`, `WT3` and `WT4`, and is marked under `CG-012`
> `PR-01`. `PR-03` prohibits relying on a provisional term for a contractual commitment.**
>
> **`O-03`: these are the same questions as `LG-002` `CU1`–`CU3` and must be answered once.**

| # | Clause |
|---|---|
| **5.1** | The Company is liable for loss it causes by failing to exercise reasonable skill and care |
| **5.2** | **Cap.** The Company's aggregate liability for a service order is limited to the greater of the amount paid for that service order and the reasonable cost of repairing or replacing the device with an equivalent — **provisional pending `WT3`** |
| **5.3** | **Data loss.** Liability is limited to §4.7.4 — attempted recovery at no charge where technically possible, and re-performance — **provisional pending `WT4`** |
| **5.4** | The Company is not liable for the excluded matters in §4.6, subject to `EX-R3` |
| **5.5** | **Nothing in this document limits liability that cannot lawfully be limited**, including for death or personal injury caused by negligence, for fraud, or for a consumer right that a statutory instrument makes non-excludable |
| **5.6** | **The Customer's right to complain to the Directorate of National Consumer Rights Protection is preserved and is not conditional on any step in §8** |
| **5.7** | A warranty given here is **in addition to**, and not in substitution for, any statutory right the Customer has |
| **5.8** | **Where a marketplace seller performed the work, the standards and this warranty apply identically** (`BRU-MKP-02`, `BRU-ECM-03`), and the Company may remedy first and recover from the seller separately (`BRU-MKP-20`, `LG-004` `MP7`) |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | Service records, diagnosis, photographs and warranty claims are processed for `LG-008` `P-01` and `P-07`, on contract performance |
| **6.2** | **Evidence photographs may incidentally show the Customer's home, premises or on-screen data.** `LG-008` `P-01` states that risk to the Customer, and `LG-005` §4.3 limits what a brand partner may do with them |
| **6.3** | Warranty and service records are retained per `LG-009` `RC-01` and `DC-04`…`DC-07` — **warranty period plus the limitation period**, minimum the tax retention. **The Customer's own claim right depends on the Company keeping them** (`LG-009` §4.5) |
| **6.4** | **Data encountered on a device during repair is not copied or retained** (§4.7.2). Recovered data under a data-services case is `LG-017` and is Bangladesh-resident (`BRU-DTS-16`) |
| **6.5** | A device leaving for recycling or resale carries a certified destruction record (§4.7.7) |
| **6.6** | Erasure of service records is subject to the `LG-009` §4.5 override, and the override and its basis are stated to the Customer (`BRU-CPM-11`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Warranty period expires** | No further claim. **A claim already raised within the window continues to decision** |
| **Claim window closes** | No claim on that repair, subject to §5.5 and §5.7 |
| **A void condition is applied** | Coverage refused, **with the evidence stated** (`BRU-WTY-17`). The Customer may complain (§8) |
| **The device is replaced** | The remaining period transfers; a new period is issued only with a new type (§4.11.3) |
| **The Customer's account closes** | **The warranty survives.** It attaches to the repair, not to the account (`LG-002` §7) |
| **These terms are superseded** | **Issued warranties keep the terms they were issued under** (`WTY-06`). Prior versions are retained permanently (`LG-009` `DC-23`) |
| **A device is disposed of under §4.9** | Any remaining warranty ends; the destruction record and the disposal record are retained (`DC-13`) |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Warranty decision review** | The branch or workshop that decided it, then the Warranty Officer. **The evidence for a refusal is producible** (`EX-R1`) |
| **2 — Complaint** | `SP-028`. Acknowledged immediately with a reference and a timescale (`BRU-CXM-01`); **closed only on the Customer's confirmation** (`BRU-QMS-04`) |
| **3 — Escalation** | Branch Manager, then Customer Service Manager (`SP-005`). Compensation authority is `LG-014` §4.7 |
| **4 — Consumer authority** | **The Directorate of National Consumer Rights Protection. Unconditional (§5.6)** |
| **5 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5. Canonical exclusion list `EX-01`…`EX-18` established for `MD-031` | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to coverage, duration, an exclusion or a liability limit is **MAJOR** |
| **9.2** | **A MAJOR change is never retrospective.** An issued warranty keeps its terms; a changed term requires a **new `MD-031` type** for future work (`WTY-06`) |
| **9.3** | **A change to §4.6 must be pushed to `MD-031` in the same release.** Until it is, `WTY-02` blocks activation of the new type — **which is the control working, not a defect** |
| **9.4** | A change here re-opens `LG-002` §4.6, `LG-014`, `DT-002`, `DT-032`, `DT-033` and `MD-031` (`CG-007` §7) |
| **9.5** | Every version is retained permanently, because an issued warranty is defended by the version it was issued under |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md) | **Carries §4.6 verbatim; `WTY-02` hard-blocks a divergence** | The exclusion text, character for character |
| [`LG-002_Portal_Terms_of_Use_Customer.md`](LG-002_Portal_Terms_of_Use_Customer.md) | Defers to this file on warranty (§2, §4.6) | **`CU1`–`CU3` and `WT3`–`WT5` are one set (`O-03`)** |
| [`LG-014_Refund_Cancellation_and_Compensation_Policy.md`](LG-014_Refund_Cancellation_and_Compensation_Policy.md) | §4.11.2 — **a warranty remedy is not a refund** | The boundary between remedy and refund |
| [`LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) | Contract customers | A service credit is not a warranty remedy |
| [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | §4.7.5, §4.7.7 | The destruction gate; recovery charging |
| [`LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md`](LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md) | §5.8 | **`MP7` — who bears warranty cost on a seller job** |
| [`../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | **Where these terms are presented and signed** | Stated condition; backup warning; `EX-11` |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-032_Warranty_Certificate_and_Extension_Document.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-032_Warranty_Certificate_and_Extension_Document.md) | **Reproduces §4.3 and §4.6** | Period, start point, claim window, exclusions |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md) | §4.4.2 brand claims | Evidence requirements |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md) · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Operate §4.2.3 rework and §8 | Rework versus warranty; escalation |
| `HC-003` Help Set `P01` · `TR-007` agent course · `KB-*` technical guidance | Explain these terms | **No help or training text may state an exclusion §4.6 does not contain** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Canonical exclusion list `EX-01`…`EX-18` published as numbered, quotable text for `MD-031` `WTY-02`** (`CL-01`)
- [x] Five rules governing how an exclusion may be applied and amended (`EX-R1`…`EX-R5`)
- [x] Data-loss position stated as a disclosure, a remedy and a limit, with the limit marked provisional (`CL-02`)
- [x] Uncollected-device regime drafted with its periods deliberately left to `WT5`
- [x] **The three shared consumer-liability questions identified as one set with `LG-002`** (`O-03`)
- [x] **Two upstream `MD-031` defects raised** — missing mandatory columns in the sample load, and 30 days expressed as one month (`O-04`, `O-05`)
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied
- [ ] **`WT1`–`WT9` answered at G5** — outstanding, blocks `Approved`
- [ ] **`WT1` may reclassify this file to Class A** — outstanding, `O-02`, a register change
- [ ] **`MD-031` corrected** — outstanding, `O-04`, `O-05`
- [ ] **Storage charge, free period and no-fault-found charge published** — outstanding, `O-06`, `O-07`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding; **these terms are read at a counter in Bengali**
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
