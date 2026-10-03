---
id: LG-004
title: Marketplace Seller Agreement and Policy Handbook
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with Marketplace Operations
author: Legal & Compliance with Marketplace Operations, Finance and Quality
reviewers: [Legal Counsel, CFO, CCO, Marketplace Operations Manager, Quality Manager, Chief Data Officer, Localisation Lead]
approver: Legal Counsel with CCO
content_class: B
purpose: >
  The contract and the platform standards on which an external engineer or shop transacts through
  P07 — qualification, listing, job execution, evidence, commission, payout, holds, performance
  thresholds, appeal, suspension and removal. Automatic visibility reduction and suspension on
  performance failure is only enforceable if the agreement says so before it happens, and every
  enforcement consequence M12 automates has to be a term the seller accepted.
traces_to: [P07, M12, M11, M15, M20, M22, M23, M27, M53, LG-001, LG-006, LG-008, LG-009, LG-013, LG-019, LG-023, DT-039, MD-018, SP-024, EO-004, BRU-MKP-01, BRU-MKP-02, BRU-MKP-03, BRU-MKP-04, BRU-MKP-05, BRU-MKP-06, BRU-MKP-07, BRU-MKP-08, BRU-MKP-09, BRU-MKP-10, BRU-MKP-11, BRU-MKP-12, BRU-MKP-13, BRU-MKP-14, BRU-MKP-15, BRU-MKP-16, BRU-MKP-17, BRU-MKP-18, BRU-MKP-19, BRU-MKP-20, BRU-MKP-21, BRU-MKP-22]
priority: P1
wave: W7
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 P07 governance requirements — a seller cannot transact until documents are verified, the agreement is signed and admin approval is granted; quality and evidence standards identical to owned jobs; payouts held for a defined period and blocked while a dispute is open; falling below the performance threshold reduces visibility automatically, then suspends
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md §9 BRU-MKP-01 … BRU-MKP-22
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12 §9 BRU-MKP-15 — no settlement, invoicing or VAT logic is built before the external tax and legal opinion is documented (RSK-022); BRU-TAX-17 — marketplace determination is refused rather than defaulted until decision D-03 is settled
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §8 EA-04 — a seller sees customer name, contact and address only for an awarded job and only until a defined period after completion; §4 T5 — seller KYC documents
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md §7 CR-07 — the marketplace VAT and liability model is undecided, so P07 content cannot state commission, payout or liability terms correctly
    verified: 2026-08-18
    class: P1
  - source: Consumer Rights Protection Act 2009 and the Digital Commerce Operation Guidelines 2021 — platform-mediated transactions and the consumer's route of recourse. Instrument-level citation; clause-level content unverified in this file, pending G5
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-004 — Marketplace Seller Agreement and Policy Handbook

| Item | Value |
|---|---|
| Document class | **Agreement** — bilateral contract, plus a policy handbook incorporated by reference |
| Counterparty | An external engineer (individual) or shop (business) approved to transact through `P07` |
| Governing law | **Bangladesh** |
| Effective date | On execution by the seller — *pending approval and pending `O-01`* |
| Acceptance capture method | **`AC-2` e-signature** through an `M24` envelope with a completion certificate. **`BRU-MKP-01` makes execution a hard gate: no signature, no transacting** |
| Version accepted by users | Recorded in `LG-001`; **a seller is bound to the version in force at their agreement date** unless re-accepted |
| External counsel review | **Required, and it is not the only external input needed** — see §1.2 |
| Bengali version | **Not required** per `CG-010` §3.2 — **and this is contested. See `O-02`** |

> ⚠ **Class B. This document is blocked on two decisions the content function cannot make.**
>
> `BRU-MKP-15`: *"No settlement, invoicing or VAT logic is built before the external tax and legal
> opinion is documented."* `BRU-TAX-17`: *"The marketplace model is not configured until decision
> D-03 is settled by external tax opinion; until then, marketplace determination is refused rather
> than defaulted."* `CG-013` `CR-07` records the same thing from the content side.
>
> **Commission, payout, invoicing and who contracts with the customer all follow from the
> principal-or-agent determination. Until it is documented, §4.5, §4.6 and §5.2 are drafted as
> alternatives, not as terms.**
>
> **Conformance note.** All ten template sections retained in order. The policy handbook is §4.9
> rather than a separate document, because the register allocates one file and `CP-01` forbids
> splitting it into an unregistered second.

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Marketplace Operations | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — Marketplace Operations Manager | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| **External tax and legal opinion — D-03 principal/agent** | *pending* | | **Required, blocking (`BRU-MKP-15`)** |
| Approved by — Legal Counsel with CCO | *pending* | | |

### 1.2 Questions for Legal Counsel and the external adviser (G5)

| # | Question | Owner | Why it blocks |
|---|---|---|---|
| **MP1** | **Is 1000FiX principal or agent** on a marketplace-fulfilled job? | External tax adviser → CFO | Determines who invoices the customer, who bears VAT, who owes the consumer, and whether commission is a fee or a share of revenue. **Decision D-03** |
| **MP2** | Given `MP1`, is commission a deduction from the seller's revenue or a charge for a platform service, and what is its VAT treatment? | External tax adviser | §4.5 cannot be drafted without it |
| **MP3** | Is the seller an **independent contractor**, and what in the platform's control over pricing, ranking, standards and suspension risks recharacterising that? | Legal Counsel | Employment recharacterisation is the standard platform risk, and `BRU-MKP-22` ranking control is a factor in it |
| **MP4** | Is **automatic visibility reduction and suspension** on a performance score enforceable, and what notice, reasons and appeal make it so? (`BRU-MKP-06`) | Legal Counsel | The consequence is automated. If unenforceable, the automation is a liability |
| **MP5** | Is **recovery from seller earnings** enforceable, and what limits apply? `BRU-MKP-17` requires notice, a declared limit and a right of appeal | Legal Counsel | Set-off against a contractor's earnings is regulated in many jurisdictions |
| **MP6** | Where the Company **remedies the customer first and recovers from the seller** (`BRU-MKP-20`), what is the basis of recovery and its ceiling? | Legal Counsel | This is the Company's principal marketplace credit exposure |
| **MP7** | Does the Company's warranty (`LG-013`) attach to seller-performed work, and if so who bears the cost? | Legal Counsel with Warranty | `BRU-ECM-03` holds seller jobs to the same warranty standard but does not allocate cost |
| **MP8** | Are the KYC documents collected — National ID, trade licence, references, and any criminal-record check — proportionate and lawfully retained? | Chief Data Officer with Legal | These are `T5`/`S3` residency-restricted (`05-06` §6.4) |
| **MP9** | Is an English-only agreement appropriate for 500–2,000 predominantly Bengali-first sellers? | Legal Counsel with Localisation | `O-02` |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **Decision D-03 principal/agent is unresolved** (`RSK-022`, `BRU-MKP-15`, `BRU-TAX-17`, `CG-013` `CR-07`). §4.5, §4.6 and §5.2 are drafted as **alternatives A and B** and are not terms until it is settled | **Yes — blocks the document and the build** | CFO with external tax adviser |
| **O-02** | **English-only conflicts with the audience.** `CG-010` §3.2 puts `LG-004` in the English-only set; §3.3 marks marketplace sellers bilingual. `BRU-MKP-17` gives a right of appeal that a seller must be able to read. **Registered in `LG-001` `O-01` and repeated here because it is this file's problem** | **Yes — blocks G5** | Legal Counsel with Localisation Lead |
| **O-03** | Performance thresholds are not numerically defined anywhere. `BRU-MKP-06` automates a consequence at "the threshold"; `MD-018` holds the seller category and standard register. **A term cannot cite a threshold that does not exist** | **Yes — blocks §4.8** | Marketplace Operations with Quality |
| **O-04** | The payout hold period is "the declared period" in `BRU-MKP-05` and is undeclared | **Yes — blocks §4.6** | CFO |
| **O-05** | The period after job completion when customer contact data is revoked (`EA-04`, `BRU-MKP-04`) is undefined | Yes — blocks §4.7 | CTO with CDO |
| **O-06** | `MD-018` and `SP-024` exist; `EO-004` seller onboarding kit is unwritten (Category 18 unstarted). **The handbook in §4.9 will be the seller's only written standard until then** | No | Marketplace Operations |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited, operator of the marketplace |
| **The Seller** | An individual engineer or a business approved under `SP-024` and holding an executed copy of this Agreement |

**This Agreement comprises:** these terms; the **Policy Handbook** in §4.9; the category
qualification requirements in `MD-018`; the rate and commission schedule published in the portal
(held in `M11`); and the Supplier Code of Conduct in
[`LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md`](LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md)
§5, which applies to the Seller as an ethical standard.

| # | Clause |
|---|---|
| **2.1** | The Seller is an **independent contractor**. Nothing creates employment, partnership or agency beyond what §4.5 expressly provides — **subject to `MP3`** |
| **2.2** | **A marketplace seller is not a partner** and is not governed by `LG-007` (`BRU-PCM-02`) |
| **2.3** | The Seller may not subcontract a job without the Company's written approval. The person who attends is the person the customer was told would attend |
| **2.4** | The Seller cannot transact until **KYC is verified, this Agreement is signed, and an administrator has approved** (`BRU-MKP-01`, `BRU-ECM-01`). All three. Not two |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Qualification** | Approval to list in a category, granted per category and evidenced (`BRU-MKP-08`, `BRU-ECM-07`) |
| **Listing** | A service or product the Seller offers through `P07` |
| **Broadcast** | The Company offering a job to sellers matching the job's requirements |
| **Award** | The Company assigning a job to the Seller. **Customer contact data is released only on award** (`EA-04`) |
| **Evidence set** | The photographs, diagnosis, parts record and customer sign-off a job cannot close without (`BRU-MKP-02`) |
| **Performance score** | The composite of acceptance rate, on-time rate, rating, rework and disputes shown on the Seller's scorecard |
| **Visibility reduction** | Automatic reduction in listing prominence on falling below the performance threshold (`BRU-MKP-06`) |
| **Wallet** | The Seller's **append-only** earnings ledger. Balances are derived and never edited (`BRU-MKP-16`) |
| **Hold** | Suspension of payout while a dispute is open (`BRU-MKP-05`) |
| **Boost** | Paid placement, which **never overrides a quality-based restriction or suppression** (`BRU-MKP-12`) |
| **Governing text** | This English text — **pending `O-02`** |

---

## 4. Terms

### 4.1 Qualification and registration

| # | Clause |
|---|---|
| **4.1.1** | The Seller submits National ID, trade licence where applicable, references and work samples, and verifies phone and email |
| **4.1.2** | **Qualification is per category, never global** (`BRU-MKP-08`; compare `BRU-SRM2-03`). A Seller may not list in a category for which they hold no verified qualification (`BRU-ECM-07`) |
| **4.1.3** | Where a category requires a brand authorisation or certification, the Seller must hold it currently. **A job requiring an authorisation the Seller does not hold is never broadcast to them** (`BRU-MKP-08`) |
| **4.1.4** | **Warranty work under a brand authorisation is never broadcast to the marketplace** (`BRU-MKP-09`). The Seller should not expect it and cannot request it |
| **4.1.5** | Registration and documents have expiry dates. **A lapse blocks transacting immediately** (`BRU-MKP-21`, `BRU-ECM-08`), with advance warning from the platform |
| **4.1.6** | KYC documents are held as restricted data — allow-list access, step-up authentication, every access logged (`BRU-MKP-19`, `05-04` `T5`) — and are stored in a **Bangladesh-resident** store (`05-06` §6.4) |

### 4.2 Listings and pricing

The Seller sets prices within any published band for the category, maintains accurate availability,
and may not list counterfeit, stolen or unlawfully sourced goods. **Seller-declared stock is never
commingled with Company inventory** (`BRU-MKP-10`). **A counterfeit-part finding suspends the
listing immediately and the Seller pending investigation** (`BRU-MKP-11`).

### 4.3 Job execution standards

| # | Clause |
|---|---|
| **4.3.1** | **Quality and evidence standards for a marketplace job are identical to a Company-performed job. A job cannot complete without them** (`BRU-MKP-02`, `BRU-ECM-03`) |
| **4.3.2** | The Seller records the diagnosis, parts used, before-and-after photographs and the customer's sign-off through `P07` |
| **4.3.3** | The Seller attends in the agreed window, identifies themselves, and behaves toward the customer as the Company's standards require. **The customer's experience is the Company's reputation** |
| **4.3.4** | Sellers and suppliers are audited against the same standards as owned operations (`BRU-QMS-17`), and may be selected for quality audit through `P11` |
| **4.3.5** | The Seller must not solicit the customer to transact off-platform, and must not use customer data for any purpose other than the awarded job |

### 4.4 Communication with the customer

The Seller may chat with the customer on an open job and may escalate to the Company. The Seller
must not give the customer a commitment on price, warranty or timescale beyond what the job
specifies — **those are the Company's commitments** (`LG-013`).

### 4.5 Commission and revenue — **drafted as alternatives pending `O-01`**

> **`CL-01`. This is the clause `BRU-MKP-15` prohibits building on until D-03 is documented.**
> Both alternatives are set out so the commercial and system consequences are visible now, and so
> the eventual answer is recorded as a choice rather than as a default.

| | **Alternative A — Company as principal** | **Alternative B — Company as agent** |
|---|---|---|
| Who invoices the customer | The Company | The Seller, through the platform |
| VAT on the service | The Company accounts for it | The Seller accounts for it; the Company accounts for its commission |
| Commission | A margin the Company retains from the price | **A fee the Company charges the Seller for the platform service** |
| Consumer's counterparty | The Company | The Seller, with the Company's platform duties alongside |
| Seller statement (`DT-039`) | Shows gross, deductions, net | Shows collections, commission invoice, net |
| `BRU-MKP-14` flag | `principal` | `agent` |

| # | Clause |
|---|---|
| **4.5.1** | **Every marketplace transaction carries an explicit principal-or-agent flag derived from the documented determination** (`BRU-MKP-14`), and the model **cannot vary by transaction** (`BRU-TAX-16`) |
| **4.5.2** | Commission rates are published in the portal and held in `M11`; they are computed and paid through `M53` (compare `BRU-PCM-03`) |
| **4.5.3** | A commission change is a MAJOR change under §9 and requires notice and re-acceptance |

### 4.6 Payout, holds and recovery — **partly pending `O-01`, `O-04`**

| # | Clause |
|---|---|
| **4.6.1** | Earnings are credited to the Wallet, which is an **append-only ledger; balances are derived and never edited** (`BRU-MKP-16`) |
| **4.6.2** | **Payouts are held for the declared period and are blocked entirely while a dispute is open** (`BRU-MKP-05`). The period is stated in the portal — **`O-04`** |
| **4.6.3** | Approving a Seller and approving their payout cannot be done by the same person (`BRU-MKP-03`, `SOD-06`) |
| **4.6.4** | **Recovery from earnings requires notice, a declared limit and a right of appeal** (`BRU-MKP-17`) — provisional pending `MP5` |
| **4.6.5** | Where the Company remedies the customer first, it may recover from the Seller separately (`BRU-MKP-20`) — provisional pending `MP6` |
| **4.6.6** | The Seller is responsible for its own tax obligations on its earnings. Where the Company is required to withhold, it does so at the determined rate and issues a certificate (`BRU-TAX-07`, `BRU-TAX-10`) |

### 4.7 Customer data

| # | Clause |
|---|---|
| **4.7.1** | The Seller receives the customer's **name, contact and address only for an awarded job**, and access is revoked a defined period after completion (`EA-04`, `BRU-MKP-04`) — **`O-05`** |
| **4.7.2** | The Seller must not copy, retain, export or reuse customer data, and must not contact the customer after the revocation period |
| **4.7.3** | The Seller never sees Company cost, margin, internal notes or any other party's data (`EA-01`, `EA-02`) |
| **4.7.4** | The Seller processes customer personal data **only on the Company's instruction** and is bound by equivalent obligations, which flow down by this clause (`NFR-098`, `BRU-GRC-18`) |
| **4.7.5** | A suspected data breach must be reported to the Company **immediately** — the Company carries the statutory notification duty (`NFR-094`) and cannot discharge it late |

### 4.8 Performance, consequences and appeal — **pending `O-03`**

| # | Clause |
|---|---|
| **4.8.1** | The Seller's scorecard shows acceptance rate, on-time rate, rating breakdown, rework and disputes, and **the consequences of falling below threshold** (`P07` capability set) |
| **4.8.2** | **Below the performance threshold, visibility is reduced automatically. Below the suspension threshold, the Seller is suspended** (`BRU-MKP-06`, `BRU-ECM-04`) — provisional pending `MP4` |
| **4.8.3** | The threshold values, the measurement window and the minimum job count before a score is acted on are published and are **not varied for an individual Seller** — **`O-03`** |
| **4.8.4** | **An appeal is decided by an operator other than the one who imposed the consequence** (`BRU-MKP-18`) |
| **4.8.5** | Disputes between the Seller and a customer **are decided by the Company, not by the parties; the decision and its evidence are recorded** (`BRU-ECM-09`) |
| **4.8.6** | Paid promotion never overrides a quality-based restriction (`BRU-MKP-12`), and **promoted placements are clearly marked as promoted to the customer** (`BRU-MKP-13`, `BRU-ECM-06`) |
| **4.8.7** | **Broadcast ranking is computed from declared factors and every ranking decision is reconstructible** (`BRU-MKP-22`). The Seller may ask why a job was not offered to them |
| **4.8.8** | Only a customer with a completed transaction may leave a review (`BRU-ECM-02`). The Seller may respond once per review |

### 4.9 Policy Handbook

Incorporated into this Agreement and enforceable as a term of it. Each policy states the standard,
the evidence, and the consequence.

| # | Policy | Standard | Consequence of breach |
|---|---|---|---|
| **PH-01** | **Identity and attendance** | The approved person attends; no substitution without approval (§2.3) | Suspension |
| **PH-02** | **Evidence** | The full evidence set on every job (`BRU-MKP-02`) | The job cannot close; repeated failure suspends |
| **PH-03** | **Genuine parts** | No counterfeit or unlawfully sourced parts | **Immediate listing suspension and Seller suspension pending investigation** (`BRU-MKP-11`) |
| **PH-04** | **Customer data** | Use only for the awarded job; no retention, no off-platform contact (§4.7) | Suspension; removal for a repeat |
| **PH-05** | **Off-platform solicitation** | Prohibited (§4.3.5) | Removal |
| **PH-06** | **Safety** | Comply with the safety requirements for the work and the site; report incidents | Suspension; escalation to HSE |
| **PH-07** | **Ethics** | The Supplier Code of Conduct in `LG-006` §5 — no bribery, no facilitation payment, no conflict undeclared | Removal; reported under `LG-023` |
| **PH-08** | **Review integrity** | No solicited, incentivised or fabricated reviews | Removal |
| **PH-09** | **Pricing conduct** | No price manipulation after award; no charging the customer outside the platform | Recovery under §4.6.4, then removal |
| **PH-10** | **Communication** | Professional, in the customer's language, no commitments beyond the job (§4.4) | Coaching, then suspension |
| **PH-11** | **Insurance and licences** | Hold what the category requires, currently (`BRU-MKP-21`) | Transacting blocked at lapse |
| **PH-12** | **Policy acknowledgement** | The Seller acknowledges policy updates in `P07` (`P07` capability set) | Transacting blocked until acknowledged |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | The Seller is responsible for the work it performs, for the parts it supplies, and for loss or damage it causes to the customer's property or premises |
| **5.2** | **Allocation of liability to the customer follows the §4.5 determination** — **pending `O-01`**. Under Alternative A the Company owes the customer and recovers from the Seller; under Alternative B the Seller owes the customer and the Company owes its platform duties |
| **5.3** | **In either case, `BRU-MKP-20` applies: where the customer experience requires it, the Company remedies first and recovers separately.** The Seller agrees to that sequence and to the recovery, subject to §4.6.4 and `MP6` |
| **5.4** | The Company is not liable to the Seller for: the volume or value of jobs offered; the outcome of a ranking decision made on declared factors (`BRU-MKP-22`); a suspension properly applied under §4.8; a customer's rating; or loss of expected earnings |
| **5.5** | **Cap.** The Company's aggregate liability to the Seller is limited to the commission or fees the Company received from the Seller's transactions in the three months preceding the claim — provisional pending G5 |
| **5.6** | The Seller indemnifies the Company against claims arising from the Seller's breach of §4.3, §4.7, `PH-03`, `PH-05` or `PH-07` — provisional pending G5 |
| **5.7** | Nothing limits liability that cannot lawfully be limited, or removes the customer's statutory rights against either party |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009` and `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | The Company processes the Seller's personal data — identity, contact, KYC, banking, performance, earnings — as a controller, on the basis stated in `LG-008` |
| **6.2** | KYC documents, National ID and bank details are **restricted (`S3`) and Bangladesh-resident**; they are not replicated outside Bangladesh (`05-06` NFR-086, §6.4; `BRU-CPM-06`) |
| **6.3** | The Seller processes customer personal data **only as the Company's processor**, only for the awarded job, and only for the access period (§4.7). Equivalent obligations flow down by §4.7.4 (`NFR-098`) |
| **6.4** | The Seller must notify the Company of a suspected breach immediately (§4.7.5); the Company notifies the **National Data Management Authority** where the threshold is met (`NFR-094`) |
| **6.5** | The Seller has access, rectification, erasure and portability rights over its own personal data, exercisable under `LG-010`. **Erasure does not extend to records the Company must retain** (`LG-009`), including transaction, tax and dispute records |
| **6.6** | Performance and earnings records are retained after removal for the period in `LG-009`, because they evidence transactions and tax positions |
| **6.7** | A criminal-record check, where collected for a category, is restricted data with heightened handling and is **subject to `MP8`** |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Seller resigns** | No new awards. **Open jobs must be completed** or reassigned with the customer informed. Wallet balance paid on the normal cycle after holds clear |
| **Registration or document lapse** | Transacting blocked immediately (`BRU-MKP-21`); reinstated on renewal |
| **Suspension for performance** | Automatic per §4.8.2; appeal under §4.8.4 to a different operator |
| **Suspension for counterfeit finding** | **Immediate**, pending investigation (`BRU-MKP-11`) |
| **Removal for breach of `PH-03`, `PH-05`, `PH-07` or `PH-08`** | Agreement terminated. Outstanding earnings settled net of recovery under §4.6.4 |
| **Company withdraws the marketplace** | Notice per §9; open jobs completed; balances settled |
| **In every case** | §4.7 data obligations, §6, confidentiality, indemnities and the record-retention position survive. **Customer access is revoked; the Seller's copy obligation does not lapse with access** |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Platform appeal** | Under §4.8.4, decided by an operator other than the one who imposed the consequence (`BRU-MKP-18`) |
| **2 — Escalation** | Marketplace Operations Manager, then the CCO, per `SP-005` |
| **3 — Mediation** | Good-faith discussion within 15 business days of written notice |
| **4 — Arbitration** | Arbitration in Dhaka under the Arbitration Act 2001, one arbitrator — provisional pending G5 confirmation that it is appropriate for an individual seller |
| **5 — Courts** | The courts of Dhaka, Bangladesh |

**A customer-to-Seller dispute is not a §8 dispute.** It is decided by the Company under
`BRU-ECM-09`, and the Seller's route against that decision is §4.8.4.

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft, blocked on decision D-03 | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to commission, payout, holds, thresholds, consequences or liability is **MAJOR**: notice, then **re-acceptance before further transacting** |
| **9.2** | A Policy Handbook update is acknowledged in `P07`; **transacting is blocked until acknowledged** (`PH-12`) |
| **9.3** | A Seller is bound to the version in force at their agreement date until they accept a later one (compare `BRU-PCM-12`) |
| **9.4** | **The resolution of decision D-03 is a MAJOR change by definition**, because it determines who contracts with the customer |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | Version and acceptance record; `AC-2` | Execution as a hard gate |
| [`LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md`](LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) | §5 Code applies to the Seller via §2 and `PH-07` | Ethical standards |
| [`LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) | The customer-facing warranty §4.4 refers to | **Who bears warranty cost on a seller job — `MP7`** |
| [`LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md`](LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) | `PH-07` reporting route | Reporting channel and protection |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | §6 | Check **F6** |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md) | Category qualifications in §4.1.2 and thresholds in §4.8.3 | **`O-03`** |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md) | Renders §4.5 and §4.6 | **Statement shape depends on D-03** |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md) | Operates §4.1 and §4.8 | Threshold values, appeal handling |
| `EO-004` Marketplace Seller Onboarding Kit · `HC-009` Help Set `P07` · `TR-019` course pack | Explain this Agreement to sellers and staff | No kit may state a term this does not |
| `LG-002` §4.13 | The customer-side disclosure of marketplace fulfilment | **`BRU-MKP-07` consent, and who the customer's counterparty is** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; the Policy Handbook is §4.9, declared
- [x] All 22 `BRU-MKP-*` rules reflected in a term, so no automated consequence exists without a contractual basis
- [x] **Commission, payout and liability drafted as explicit alternatives** pending decision D-03, rather than defaulted (`BRU-MKP-15`, `BRU-TAX-17`)
- [x] Twelve-policy handbook with standard, evidence and consequence per policy
- [x] Appeal by a different operator stated (`BRU-MKP-18`); ranking reconstructibility stated (`BRU-MKP-22`)
- [x] All internal links resolve
- [x] Bengali counterpart — **not required per `CG-010` §3.2, and contested at `O-02`**
- [ ] **Decision D-03 documented by external tax opinion** — outstanding, blocks the document and the build
- [ ] **`MP1`–`MP9` answered** — outstanding
- [ ] **Performance thresholds defined in `MD-018`** — outstanding, `O-03`
- [ ] **Payout hold period and data-revocation period declared** — outstanding, `O-04`, `O-05`
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
