---
id: EO-014
title: Ecosystem Offboarding and Exit Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal with Marketplace Operations
author: Legal Counsel with Marketplace Operations, Procurement and Content Design
reviewers: [Chief Commercial Officer, Chief Financial Officer, Data Protection Officer, Procurement Manager, Account Management, Partnerships, Quality Manager, Localisation Lead, Content Design Lead]
approver: Legal Counsel
content_class: B
purpose: >
  What happens when an ecosystem relationship ends — by notice, by expiry, by breach or by the
  counterparty's own choice: the notice that must be given, how open work is protected, how the
  final settlement is computed and paid, what happens to data on both sides, what is removed from
  public view, what obligations survive the ending, and on what terms a party may return. Exit is
  the point at which every ecosystem relationship becomes capable of being a legal dispute, and
  the content has to pre-exist the exit: a termination notice drafted on the day it is served is
  drafted by the person least able to be dispassionate about it.
traces_to: [P07, P05, P12, P04, P08, M12, M40, M42, M24, M29, M33, M53, M52, M20, M08, M06, 04-00 P07, 05-04 §8 EA-04, FR-MKP-063, FR-MKP-067, FR-SRM2-011, FR-SRM2-014, FR-PCM-010, FR-PCM-011, FR-PCM-013, FR-PCM-014, BRU-MKP-05, BRU-MKP-17, BRU-ECM-08, BRU-SRM2-04, BRU-SRM2-16, BRU-PCM-01, BRU-PCM-07, BRU-PCM-08, BRU-PCM-13, BRU-PCM-15, AUT-MKP-18, T-13, KPI-C40-05, KPI-C40-06, MD-016, MD-017, MD-018, MD-026, LG-003, LG-004, LG-005, LG-006, LG-007, LG-008, LG-009, LG-010, LG-017, SP-004, SP-024, DT-039, DT-040, UI-017, HC-009, NT-011, NT-012, NT-013, RF-006, EO-001, EO-002, EO-003, EO-005, EO-007, EO-009, EO-010, EO-012, EO-013, OP-001, OP-015]
priority: P2
wave: W8
bilingual: yes
bn_counterpart: EO-014_Ecosystem_Offboarding_and_Exit_Content_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md §5.6 FR-MKP-067 seller offboarding with settlement of outstanding earnings, retention of records, revocation of access and customer continuity for open jobs; §11 AUT-MKP-18 "transition open jobs, settle earnings, close disputes, revoke access, retain records per policy — escalate to operations; never strand a customer's open job"; §6 T-13 seller data portability and erasure within PDPA 2026 obligations, subject to statutory retention on transactions; §8.1 OFFBOARDING to REMOVED with records retained per policy
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §5.1 FR-PCM-010 standing including exiting and exited, FR-PCM-011 renewal at the M08 lead time and exit with obligation settlement and access revocation; §9 BRU-PCM-13 portal access revoked within one hour of exit, suspension or agreement expiry, BRU-PCM-15 outstanding partner commission settled before a relationship reaches Exited, BRU-PCM-07 a brand authorisation may never lapse without escalation having fired, BRU-PCM-08 work requiring a lapsed authorisation cannot be performed
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md §5.2 FR-SRM2-014 de-activate, suspend or permanently block with a recorded reason, immediately preventing new orders while leaving open orders visible; §9 BRU-SRM2-16 a confirmed sanctions match or confirmed counterfeit supply is blocked permanently by CFO or CEO authority and cannot be reversed below that authority; BRU-SRM2-04 expiry automatically suspends for the affected categories
    verified: 2026-08-18
    class: P1
  - source: project_content/10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md — the retention periods and deletion obligations that govern what survives an exit
    verified: 2026-08-18
    class: P1
  - source: Digital Commerce Operation Guidelines 2021 (Ministry of Commerce, Bangladesh) — the marketplace owner must finalise payment to the business owner within ten days after deducting charges and commission
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Ecosystem Offboarding and Exit Content

| Item | Value |
|---|---|
| Audience | Departing marketplace sellers, suppliers, brand partners, corporate clients, referral and alliance partners, franchisees — and the internal owners who end the relationship |
| Content class | **B — legal / contractual.** Approver: Legal Counsel (`CG-002` §4) |
| Language | **Bilingual**; English governs (`CG-010` §4.1) |
| Wave | W8 · Months 31–34 — **and the first relationships begin at W3** (`O-01`) |
| Governing instruments | `LG-003` §7 · `LG-004` §7 · `LG-005` §7 · `LG-006` §7 · `LG-007` §7 |
| Absolute rule | **`AUT-MKP-18` — never strand a customer's open job** |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions are applied to the ending rather than to the
> beginning: §4.2 is the **journey** an exit travels, §4.4 is the **exit checklist**, and §4.8 is
> the **first 90 days after exit** — which for this file is the genuine article, because the
> obligations that survive an exit are what turn an ending into a dispute. Declared; template 15
> `TPL_Onboarding_Kit.md` does not exist.

---

## 1. Purpose

Every other file in Category 18 assumes a relationship that is working. This one assumes it has
stopped, and it exists because **that is the moment at which all the goodwill that has been
covering the gaps disappears at once.**

Four things become simultaneously urgent and contested:

| At exit | Why it is contested |
|---|---|
| **Money** | The counterparty wants everything owed, immediately. We want deductions, recoveries and dispute holds applied first — and `BRU-MKP-17` requires notice, a limit and an appeal for each |
| **Open work** | A customer with a device at a departing seller, an open purchase order with a blocked supplier, or a live claim with a lapsing brand does not care why the relationship ended |
| **Data** | The counterparty wants their data and wants ours deleted. `T-13` grants portability and erasure **subject to statutory retention on transactions**, and the two obligations point in opposite directions |
| **Reputation and visibility** | Listings, marks, profiles, signage and directory entries persist long after access is revoked, and each one is a continuing representation |

`M12`'s `AUT-MKP-18` states the one absolute in the whole file: **"never strand a customer's open
job."** Everything else in an exit is negotiable, sequenced or deferrable. That is not.

**What this file is not.** It is not the termination clause — `LG-003` §7, `LG-004` §7, `LG-005`
§7, `LG-006` §7 and `LG-007` §7 each carry one, and this file operationalises them. It is not the
sanction ladder that may lead to removal (`EO-002` §4.5), not the dispute process (`EO-013`) and
not the retention schedule (`LG-009`).

---

## 2. Scope

**In scope.** The six ways a relationship ends and how each differs; the exit journey; notice —
who gives it, in what form and how much; protection of open work per ecosystem; the final
settlement and its computation; data handling in both directions; removal of listings, profiles,
marks and public presence; obligations that survive termination; the reinstatement position; the
permanent-block cases that admit no return; and the ninety days after an exit.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Termination clauses, governing law and notice periods as contractual terms | `LG-003` §7, `LG-004` §7, `LG-005` §7, `LG-006` §7, `LG-007` §7 |
| The sanction ladder that may lead to removal | **`EO-002` §4.5** |
| The dispute process, including a dispute open at exit | **`EO-013`** |
| Retention periods and deletion obligations | `LG-009`; data-subject requests `LG-010`; privacy `LG-008` |
| Secure destruction of customer media | `LG-017`; `M06` |
| Employee exit | `M21`; the internal joiner-mover-leaver process is **`OP-015`** |
| Support routing for a departed counterparty's residual queries | `OP-001` — which cites this file for the exit case |
| Payout and settlement mechanics | `M53`, `M52`, `M20`; statements `DT-039`, `DT-040` |
| Reason-code values for termination | `MD-026` |
| Contract renewal and expiry management before exit | `M08`; `FR-PCM-011`; `BRU-SRM2-19` |
| Mark and asset withdrawal mechanics | **`EO-012` §4.7** |
| Franchise de-branding standards | **`EO-010`** |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Departing counterparty** | What they will be paid, when, what happens to their data, and whether they can return |
| **Marketplace Operations (`R24`)** | The seller offboarding sequence and the open-job transition |
| **Procurement Manager** | De-activation, blocking, and open purchase orders |
| **Account Management** | Corporate contract exit, estate data and final invoicing |
| **Commercial / Partnerships** | Brand authorisation lapse, partner exit, franchise termination |
| **Finance Manager (`R26`)** | Final settlement, deductions, recoveries and the release authority |
| **Data Protection Officer** | The portability-versus-retention position |
| **Legal Counsel** | The whole file — it is a class `B` instrument |

---

## 4. Content

### 4.1 Six ways a relationship ends

**They are not variants of one process.** Notice, settlement and reinstatement differ by cause,
and treating a voluntary exit like a terminal breach loses a counterparty who might have returned.

| # | Cause | Initiated by | Notice | Reinstatement |
|---|---|---|---|---|
| **1** | **Voluntary exit** | The counterparty | Per the instrument | **Open.** They left; nothing prevents return |
| **2** | **Expiry without renewal** | Neither — the clock | `BRU-SRM2-19` warns at 90, 60 and 30 days; `FR-PCM-011` renews at the `M08` lead time | Open — usually a re-qualification |
| **3** | **Document or registration lapse** | Neither | Automatic suspension (`BRU-ECM-08`, `BRU-SRM2-04`) | **Immediate on renewal.** This is a suspension, not an exit — §4.7 |
| **4** | **Performance termination** | 1000FiX | Per the instrument, after the ladder (`EO-002` §4.5) | Conditional — §4.7 |
| **5** | **Breach termination** | 1000FiX | Per the instrument; may be immediate | Rarely, and never for the §4.7 permanent cases |
| **6** | **Permanent block** | 1000FiX, at **CFO or CEO authority** | Immediate | **None.** `BRU-SRM2-16` — confirmed sanctions match or confirmed counterfeit supply, and it **cannot be reversed below that authority** |

> **Cause 3 is misfiled by everyone.** A lapsed trade licence or an expired certification produces
> an automatic suspension that *looks* like a termination to the counterparty. It is not one, it
> reverses on renewal, and the notice must say so — otherwise a supplier with an administrative
> lapse behaves like a supplier who has been dismissed. `XT-03`.

### 4.2 The exit journey

| # | Stage | What happens | Absolute constraint |
|---|---|---|---|
| **1** | **Decide** | Cause classified (§4.1); authority confirmed (`SP-004`); decision recorded with reason (`MD-026`) and logged in **`RF-006`** | Cause 6 requires CFO or CEO |
| **2** | **Notify** | Notice served per the instrument, in both languages, stating cause, effective date, settlement basis, data position and reinstatement position | §4.3 |
| **3** | **Freeze forward** | No new work: no bidding or awards, no new purchase orders, no new leads, no new claims | Open work is **not** frozen |
| **4** | **Protect open work** | Every open item transitioned per §4.5 | **`AUT-MKP-18` — never strand a customer's open job** |
| **5** | **Close disputes** | Open disputes run to conclusion under `EO-013` — **exit does not close a dispute** | §4.6 |
| **6** | **Settle** | Final settlement computed and paid per §4.6 | `BRU-PCM-15` — commission settled **before** `Exited` |
| **7** | **Revoke** | Portal access revoked | **Within one hour** (`BRU-PCM-13`); customer data access immediately (`EA-04`) |
| **8** | **Remove** | Listings, profile, marks, directory entries and signage withdrawn | §4.7 |
| **9** | **Handle data** | Portability and erasure against statutory retention | §4.6 |
| **10** | **Close** | State set to `Removed` / `Exited`; records retained per `LG-009` | Records are **retained, not deleted** |

**Stages 3 and 4 are deliberately separated.** Freezing new work is instant; protecting open work
takes as long as the open work takes. Collapsing them is how a customer's device ends up with a
seller who no longer has an account.

### 4.3 Notice

| Element | Requirement |
|---|---|
| **Who gives it** | The accountable function per `SP-004`; cause 6 at CFO or CEO authority |
| **Form** | Written, through the portal **and** the counterparty's registered contact — never one channel |
| **Period** | **From the instrument** (`LG-003`…`LG-007` §7). None of the five currently states a numeric period — `O-02` |
| **Language** | Both, in the same despatch. English governs (`CG-010` §4.1) |
| **Content** | Cause and its classification · effective date · what stops immediately and what continues · the settlement basis and its expected date · the data position, both directions · what must be removed and by when · the reinstatement position · who to contact · the dispute route (`EO-013`) |
| **What it must not do** | Assert a debt not yet computed · describe a recovery without its notice, limit and appeal (`BRU-MKP-17`) · imply reinstatement is impossible where §4.7 permits it · state a settlement date the settlement process cannot meet |

### 4.4 The exit checklist

| # | Item | Seller | Supplier | Brand | Corporate | Partner / Franchise |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 1 | New work stopped | ✔ | ✔ | ✔ | ✔ | ✔ |
| 2 | **Open work transitioned or completed** | ✔ | ✔ | ✔ | ✔ | ✔ |
| 3 | Open disputes run to conclusion (`EO-013`) | ✔ | ✔ | ✔ | ✔ | ✔ |
| 4 | Final settlement computed, notified and paid | ✔ | ✔ | ✔ | ✔ | ✔ |
| 5 | Recoveries applied with notice, limit and appeal | ✔ | ✔ | — | — | ✔ |
| 6 | Portal access revoked within one hour | ✔ | ✔ | ✔ | ✔ | ✔ |
| 7 | **Customer-data access revoked immediately** (`EA-04`) | ✔ | — | ✔ | — | ✔ |
| 8 | Listings withdrawn; profile unpublished | ✔ | — | — | — | — |
| 9 | Marks, materials and signage withdrawn (`EO-012` §4.7) | ✔ | — | ✔ | — | ✔ |
| 10 | Consignment or allocated stock returned or settled | — | ✔ | ✔ | — | ✔ |
| 11 | Retained warranty parts returned or disposed (`EO-004` §4.5) | — | ✔ | ✔ | — | — |
| 12 | Client estate data exported and returned | — | — | — | ✔ | — |
| 13 | Destruction and disposal certificates issued (`LG-017`) | — | — | — | ✔ | — |
| 14 | Authorisation record closed and escalation fired (`BRU-PCM-07`) | — | — | ✔ | — | — |
| 15 | Territory released; exclusivity ended (`EO-010`) | — | — | — | — | Franchise |
| 16 | Referral links and codes revoked | — | — | — | — | ✔ |
| 17 | Data portability request handled; erasure applied against retention | ✔ | ✔ | ✔ | ✔ | ✔ |
| 18 | Records retained per `LG-009`; state set and reason coded | ✔ | ✔ | ✔ | ✔ | ✔ |

### 4.5 Protecting open work — per ecosystem

| Ecosystem | Open item | What must happen |
|---|---|---|
| **Marketplace seller** | An accepted or in-progress job | Reassigned to another seller or to owned capacity (`FR-MKP-035`), with continuity for the customer. **`AUT-MKP-18` escalates to operations rather than failing** |
| | A completed job in its hold period | Runs to settlement; the hold is not accelerated by the exit and **not extended by it either** |
| | A device physically with the seller | **The highest-risk case in the whole file** — recovery of a customer's device from a departing seller has no procedure anywhere (`O-03`) |
| **Supplier** | An open purchase order | `FR-SRM2-014` de-activates for **new** orders while *"leaving open orders visible"*. Existing orders are delivered, received and paid |
| | Consignment stock held by us | Returned or settled per the consignment terms — **which have no owning content file** (`EO-003` `O-04`, `EO-005` `O-05`) |
| **Brand partner** | Submitted, undecided claims | Decided under the agreement in force at the service date |
| | Approved, unpaid claims | Pursued to payment; a lapsing relationship does not extinguish a receivable |
| | Work in progress requiring the authorisation | **`BRU-PCM-08` — work requiring a lapsed authorisation cannot be performed.** Jobs must be completed before lapse or re-routed |
| **Corporate client** | Open service requests | Completed or transitioned per the contract |
| | Assets in our custody | Returned with a record; destruction certificates where applicable (`LG-017`) |
| **Partner** | Leads inside their attribution window | **Attribution survives the exit.** A lead created before exit converts within its window and commission is owed (`BRU-PCM-04`, `BRU-PCM-15`) |
| **Franchise** | A trading branch | The longest transition in the set — customers, staff, stock, premises and territory. `EO-010`; **no transition plan exists** (`O-05`) |

### 4.6 Final settlement, and data in both directions

#### Settlement

| Step | Rule |
|---|---|
| Compute gross owed | All completed, eligible value |
| Apply commission, fees and agreed deductions | Per the instrument in force |
| Apply recoveries | **Only with notice, a declared limit and an appeal right** (`BRU-MKP-17`) |
| Hold disputed amounts | Only the disputed amount, and only while the dispute is open (`EO-013` `DR-03`) |
| Release the remainder | **Not held pending the dispute's conclusion** |
| Issue the final statement | `DT-039` sellers, `DT-040` partners; a final statement is issued even where the net is zero |
| Pay | Per the schedule — **and see `O-04`: a ten-day statutory settlement obligation may bind here** |
| **Order of operations** | `BRU-PCM-15` — outstanding commission is settled **before** the standing reaches `Exited`. **Settlement precedes closure; closure does not extinguish settlement** |

#### Data

Two obligations that genuinely conflict, stated as such rather than reconciled away:

| Direction | Obligation | Limit |
|---|---|---|
| **To the counterparty** | Data portability — their own records, in a usable form (`T-13`) | Excludes our commercial data, other parties' data, and internal assessments |
| **From us — erasure** | Erasure of personal data on request under PDPA 2026 (`T-13`, `LG-010`) | **Subject to statutory retention on transactions** (`LG-009`) — tax, statutory and evidential records are retained regardless |
| **From them — our data** | Customer data held by the counterparty **must be deleted**; access is revoked immediately (`EA-04`) | Retention of customer contact data after exit is a **data-protection incident**, not a contract breach |
| **Records** | Transaction, dispute and evidence records are **retained, not deleted**, per `LG-009` | The counterparty is told this at exit, because "delete my account" is not what happens |

> **The conflict is real and the content must not pretend otherwise.** A departing seller asking
> for erasure is entitled to it for their profile and unnecessary personal data, and **not** for
> the transaction record of a job a customer may later dispute. `XT-08` requires the notice to
> state both halves.

### 4.7 Removal, survival and return

#### What is removed, and how fast

| Item | Timing |
|---|---|
| Portal access | **Within one hour** (`BRU-PCM-13`) |
| Customer-data access | Immediately (`EA-04`) |
| Active listings | Immediately on exit — **but not before open jobs are transitioned** |
| Public profile, ratings and reviews | Unpublished. **Reviews are retained as records** and are not deleted |
| Referral links and codes | Revoked (`T-07`) |
| Marks, materials, signage | Per `EO-012` §4.7; franchise de-branding per `EO-010` |
| Directory and third-party listings | The counterparty's obligation; ours to check |

#### What survives termination

| Survives | Basis |
|---|---|
| Confidentiality | The instrument's confidentiality clause |
| Data-protection obligations on both sides | `LG-008`, PDPA 2026 |
| Payment obligations either way | The instrument |
| Warranty on completed work | `LG-013`; the customer's rights are unaffected by our relationship ending |
| Attribution and commission on leads in-window | `BRU-PCM-04`, `BRU-PCM-15` |
| Record retention | `LG-009` |
| Liability for acts before termination | The instrument |
| Prohibition on continued use of the marks | `EO-012`; **this is the one most often breached after exit** |

#### Reinstatement

| Cause | Position |
|---|---|
| Voluntary exit (1) | Open. Re-registration; **KYC and qualification are re-run, never inherited** |
| Expiry (2) | Open via re-qualification |
| **Lapse (3)** | **Not an exit.** Reverses on renewal — `XT-03` |
| Performance (4) | Conditional on remediation and a stated waiting period — **undefined**, `O-06` |
| Breach (5) | Rarely; CCO decision |
| **Permanent block (6)** | **None**, and reversal is not available below CFO or CEO authority (`BRU-SRM2-16`) |

> **`M12` §16.4's migration rule applies to returners too.** No returning counterparty is
> reinstated as approved on the strength of their history; **verification is re-run**, because the
> verification chain must be defensible to a brand partner or a regulator on the date it is
> relied on, not on the date it was first performed.

### 4.8 The first 90 days after exit

The obligations that survive are the ones nobody owns after the relationship has an owner no
longer.

| Days | What must be checked | Why |
|---|---|---|
| **0–7** | Access revoked; customer data access revoked; listings down; **open work transitioned or completed** | The `AUT-MKP-18` absolute |
| **0–30** | Final settlement notified and paid; final statement issued | The statutory settlement question — `O-04` |
| **8–30** | **Marks, signage and third-party listings removed** | The most-breached surviving obligation; nothing monitors it (`EO-012` `O-05`) |
| **30–60** | Data portability delivered; erasure applied against retention; the counterparty told what is retained and why | `LG-010` service levels |
| **30–90** | Open disputes carried past the exit run to conclusion (`EO-013`) | Exit does not close a dispute |
| **60–90** | Warranty on completed work still honoured; customers of a departed seller still served | `LG-013`; the customer never contracted with the seller |
| **90+** | Retention clock running per `LG-009`; reinstatement window position known | So a return request meets an answer, not an argument |

### 4.9 Rules

| # | Rule |
|---|---|
| **XT-01** | **Never strand a customer's open job** (`AUT-MKP-18`). Every other provision yields to this one |
| **XT-02** | The six causes (§4.1) are distinguished in the notice. A cause stated as "termination" where it is a lapse creates a dispute out of an administrative event |
| **XT-03** | A document or registration lapse is described as a **suspension that reverses on renewal**, never as an exit |
| **XT-04** | Freezing new work and protecting open work are **separate stages** and are never collapsed |
| **XT-05** | Settlement precedes closure (`BRU-PCM-15`); **closure never extinguishes settlement** |
| **XT-06** | Only disputed amounts are held; the remainder is released (`EO-013` `DR-03`) |
| **XT-07** | Recovery at exit carries the same three conditions as at any other time — **notice, declared limit, appeal** (`BRU-MKP-17`) |
| **XT-08** | The notice states **both halves of the data position**: what is returned or erased, and what is retained and why (`LG-009`, `T-13`) |
| **XT-09** | Customer data held by the counterparty must be deleted; retention after exit is a **data-protection incident** |
| **XT-10** | Reviews, ratings and transaction records are **unpublished, not deleted** |
| **XT-11** | Surviving obligations are listed in the notice, not left to the instrument |
| **XT-12** | Reinstatement re-runs verification in full; history is never inherited (`M12` §16.4) |
| **XT-13** | The permanent-block cases are stated as permanent, with the authority that imposed them (`BRU-SRM2-16`) |
| **XT-14** | Exit decisions and their reasons are coded (`MD-026`) and precedent-setting ones logged in **`RF-006`** |
| **XT-15** | Both languages, same despatch; English governs (`CG-010` §4.1) and the precedence clause from `LG-001` is carried |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`LG-003`](../10_Legal_Policy_and_Compliance/LG-003_Portal_Terms_of_Use_Corporate.md) §7, [`LG-004`](../10_Legal_Policy_and_Compliance/LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md) §7, [`LG-005`](../10_Legal_Policy_and_Compliance/LG-005_Brand_Partner_Portal_Terms.md) §7, `LG-006` §7, `LG-007` §7 | The termination clauses this file operationalises |
| [`LG-008`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md), [`LG-009`](../10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md), [`LG-010`](../10_Legal_Policy_and_Compliance/LG-010_Data_Subject_Request_Handling_Content.md), `LG-017` | Privacy, retention, data-subject requests and destruction |
| `M12` `FR-MKP-067`, `AUT-MKP-18`, `T-13`, §8.1, §16.4 | Seller offboarding, the absolute rule, portability and the re-verification principle |
| `M40` `FR-PCM-010`, `FR-PCM-011`, `BRU-PCM-13`, `BRU-PCM-15` | Partner standing, exit, revocation and settlement order |
| `M42` `FR-SRM2-014`, `BRU-SRM2-16` | Supplier de-activation, blocking and the permanent cases |
| `M08` | Contract expiry and renewal lead time |
| `M53`, `M52`, `M20`, [`DT-039`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md), [`DT-040`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-040_Partner_Commission_Statement.md) | Settlement, payment and final statements |
| `M24`, `M29` | Document retention and access revocation |
| [`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md), [`SP-024`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md) | Authority limits and the seller offboarding procedure |
| [`MD-016`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md), [`MD-017`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md), [`MD-018`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md), `MD-026` | The state fields exit writes to, and the reason codes |
| [`EO-002`](EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook.md), [`EO-010`](EO-010_Franchise_and_Channel_Partner_Pack.md), [`EO-012`](EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md), `EO-013` | The ladder that precedes removal, franchise de-branding, mark withdrawal, and disputes that survive exit |
| **`RF-006`** | Precedent log — **unwritten** |

> **Rule-citation attribution.** **BRU-MKP-\***  → `M12` §9 · **BRU-PCM-\***  → `M40` §9 · **BRU-SRM2-\***  → `M42` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. The families this file cites that **do** resolve in `05-05` are `BRU-ECM-*`. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and after every exit that reaches a legal forum |
| Trigger for out-of-cycle review | A change to any `LG` §7 clause; a change to `LG-009` retention; a PDPA 2026 guidance change on erasure or portability; a settlement-timing determination (`O-04`); the first franchise termination; an exit where a customer's device or data was at risk |
| Owner | Legal Counsel, with Marketplace Operations, Procurement and Account Management for their ecosystems |
| Change control | **Class `B`. Every version is approved by Legal Counsel**; a change to notice, settlement or data provisions requires CFO sign-off as well, and a counterparty is bound to the instrument version in force at their agreement date |
| Effectiveness measure | Exits reaching a dispute or an external forum, as a share of exits; and — the harder measure — **customers affected by an exit**, which should be zero |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is W8 and the relationships it ends begin at W3.** `P05` and the vendor ecosystem open at W3 (Months 9–13), `P04` and `P08` at W4, `P07` and `P12` at W7. **W8 is Months 31–34.** A supplier can be de-activated from Month 9 and a seller removed from Month 27, and the content governing those exits arrives up to **twenty-two months** after the first one is possible. The Master Index's own justification for this file says it exactly — *"the content must pre-exist the exit"* — **and the registered wave makes that impossible.** This is the same register-sequencing defect `AUDIT-014` TS-02 measured nine times in Category 13 and asked to be corrected **once, register-wide** | Programme Content Lead with CCO | **W3 — the wave must move, not the content** |
| **O-02** | **No notice period exists in any of the five governing instruments.** `XT-03` and §4.3 require the period to be read from `LG-003`…`LG-007` §7; **none carries a numeric period**, and `AUDIT-013` records all 24 `LG` files awaiting gate `G5`. `EO-011` `O-05` records the identical gap for pricing notices — **one missing quantity, two processes** | Legal Counsel | **W7 — before the first termination** |
| **O-03** | **There is no procedure for recovering a customer's device from a departing or suspended seller.** §4.5 marks it as the highest-risk case in the file. `AUT-MKP-18` requires open jobs transitioned and `FR-MKP-035` reassigns the *job*; **neither moves the physical device**, and `M03` chain-of-custody covers 1000FiX logistics, not recovery from a third party who has just been suspended. A seller suspended for a safety or fraud breach is precisely the seller most likely to be holding a device and least likely to return it | Operations Director with Legal Counsel and Marketplace Operations | **W7 — before the first suspension** |
| **O-04** | **Final settlement timing may be statutorily bound and the file cannot state it.** The Digital Commerce Operation Guidelines 2021 require a marketplace to settle to the business owner **within ten days** after deducting charges and commission. §4.6 sequences settlement behind dispute conclusion and recovery, both unbounded (`EO-013` `O-01`, `O-02`). **`EO-001` `O-01`, `EO-013` `O-02` and this item are one legal question recorded in three files**, and the source in all three is authoritative **secondary** (`class: P2`) — a settlement deadline cannot rest on press and law-firm reporting | **Legal Counsel with CFO**, external verification (`CG-007` G6) | **W6 — before the first payout, not before the first exit** |
| **O-05** | **A franchise termination has no transition plan, and it is the largest exit in the set.** A trading branch has customers, staff, stock, premises, signage, a territory and open jobs. §4.5 names it; `EO-010` `O-02` records that **no franchise agreement exists at all**, so there is no notice period, no de-branding obligation and no territory-return mechanism to operationalise. A franchise exit today would be improvised | Legal Counsel with CCO and Operations Director | **W7 — before the first appointment, not before the first exit** |
| **O-06** | **The reinstatement position after a performance termination is undefined.** §4.7 states "conditional on remediation and a stated waiting period" and **no waiting period, remediation standard or decision authority exists** for causes 4 and 5. `EO-001` §4.3 promises a *"stated reapplication window"* after a **rejected application** and that too is unset (`EO-001` `O-04`). **A counterparty told only that they may not return, without a period, will treat it as permanent** — which for cause 4 is not the intended outcome | CCO with Legal Counsel | **W7** |
| **O-07** | **Nothing detects continued use of the marks after exit.** §4.7 lists it as the most-breached surviving obligation and §4.8 checks it at days 8–30; `EO-012` `O-05` records that **no monitoring capability exists at all.** A departed franchisee's signage or a removed seller's shopfront is a continuing representation that 1000FiX is accountable for work it is not performing | Brand Lead with Partnerships | **W8** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions placed and the template gap noted
- [x] Content class **B** assigned, with Legal Counsel as approver (`CG-002` §4, §6 "B for agreements")
- [x] **`AUT-MKP-18` stated as the one absolute, with every other provision yielding to it**
- [x] Six causes of ending distinguished, with notice and reinstatement differing per cause
- [x] **The lapse-is-not-a-termination distinction stated, as the misfiling that turns an administrative event into a dispute**
- [x] Ten-stage exit journey with freezing new work and protecting open work deliberately separated
- [x] Notice content specified, plus four things a notice must not do
- [x] Eighteen-item exit checklist mapped across five ecosystems
- [x] Open-work protection stated per ecosystem, with the physical-device case identified as the highest risk
- [x] Settlement order stated — **settlement precedes closure and closure never extinguishes settlement**
- [x] **The portability-versus-retention conflict stated as a conflict rather than reconciled away**
- [x] Removal timings, surviving obligations and the reinstatement position per cause
- [x] First-90-days-after-exit section covering the obligations that survive an owner
- [x] Fifteen rules
- [x] All internal links resolve
- [x] Seven open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` file is W8 and the first exit is possible at W3 — outstanding; up to twenty-two months of exits with no content**
- [ ] **`O-02` no notice period in any of the five instruments — outstanding**
- [ ] **`O-03` no procedure for recovering a customer's device from a departing seller — outstanding**
- [ ] **`O-04` settlement timing may be statutorily bound; secondary sources only — outstanding**
- [ ] **`O-05` franchise termination has no agreement and no transition plan — outstanding**
- [ ] **`G5` legal review not run** (`CG-007` §3.5) — required for Class B before `Approved`
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `CG-010` §4.1 precedence clause reproduced from `LG-001` — **outstanding; clause not yet drafted**
- [ ] Named approver recorded — **pending Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
