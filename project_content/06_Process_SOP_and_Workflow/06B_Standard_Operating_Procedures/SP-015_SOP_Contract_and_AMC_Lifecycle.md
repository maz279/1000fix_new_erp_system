---
id: SP-015
title: SOP — Contract and AMC Lifecycle
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Account Management
author: Business Process Lead with Commercial and Legal
reviewers: [CCO, CFO, Legal Counsel, Operations Director, Service Operations, Finance Manager, Localisation Lead]
approver: Chief Commercial Officer with Legal Counsel
content_class: B
purpose: >
  Contract revenue is recurring and compounding, so leakage at any lifecycle stage is permanent
  rather than one-off. This SOP governs qualification, quotation, non-standard-term approval,
  activation, entitlement management, amendment, renewal and termination. A contract activated
  without its covered-asset list, entitlements, billing frequency and approval is a promise the
  system cannot keep and the ledger cannot bill.
traces_to: [M08, M07, M36, M24, M39, M53, P04, DT-030, DT-031, LG-015, MD-028, MD-032, SP-004, SP-005, SP-011, SP-020]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: SP-015_SOP_Contract_and_AMC_Lifecycle_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M08_Contract_Lifecycle_Management.md — SOD-15, negotiator cannot approve non-standard terms
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §5 BRU-CTR-01…BRU-CTR-08; §12.2 AUT-015…AUT-017
    verified: 2026-08-15
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md — service credits are a contractual remedy paid in money; must reconcile exactly with LG-015 and DT-031
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-028 renewal rate, KPI-030 contract SLA attainment, KPI-031 contracts with negative margin
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.2.3 — review of requirements before commitment, including requirements not stated by the customer but necessary
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Contract and AMC Lifecycle

| Item | Value |
|---|---|
| SOP ID | `SP-015` |
| Process owner | Chief Commercial Officer with Legal Counsel |
| Roles performing | `R22` Account Manager · `R21` Sales Manager · `R26` Finance Manager · `R32` Quality Manager (calibration contracts) · Legal Counsel |
| Systems used | `P03` Contract console (`UI-032`) · `P04` Corporate B2B Portal · `M08` · `M24` · `M39` |
| Frequency / volume | Continuous; the recurring-revenue engine. 8–20 account managers |
| ISO 9001 clause reference | **8.2.3** review of requirements · 8.2.4 changes to requirements · 8.4 externally provided processes where sub-contracted |

---

## 1. Purpose and Outcome

**Purpose.** To take a contract from qualification to a live, billable, deliverable state — and to
keep it that way through amendment and renewal — without creating obligations the operation
cannot meet or the ledger cannot bill.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The contract has at least one covered asset or seat, defined entitlements, a billing frequency and approval | `BRU-CTR-01` |
| Non-standard terms were approved by someone other than the negotiator | `SOD-15`, `SP-004` A-19 |
| The SLA band promised exists in `MD-028` and matches `LG-015` and `DT-031` exactly | `AUDIT_Checklist_Recurring` F3 |
| The full preventive-maintenance schedule was generated for the term | `AUT-016` |
| Renewal was initiated at T−90, quoted at T−60 | `AUT-015` |
| Out-of-scope work is billed, never silently absorbed | `BRU-CTR-02` |

---

## 2. Scope

**Applies to:** AMC and RAMC agreements, managed-service contracts, enterprise service agreements,
corporate framework agreements, and the SLA schedules attached to them — for the whole lifecycle
from qualification to termination.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| One-off repair quotation | `SP-013` |
| Consumer subscription plans sold self-service | `M39`; the amendment-credit control `SOD-16` still applies |
| Delivery of the contracted service itself | `SP-008`, `SP-010`, `SP-011` |
| Warranty products sold as a protection plan | `M09`; eligibility assessment is a hard gate (`BRU-WTY-07`) |
| Marketplace seller agreements | `SP-024` |
| Vendor contracts (1000FiX as buyer) | `SP-017` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| AMC | Annual maintenance contract |
| RAMC | Residential AMC, priced from the number and type of registered appliances, never a flat fee (`BRU-CTR-06`) |
| Covered asset | A device on the contract's entitlement list; service outside it is chargeable |
| Entitlement | What the contract grants — visit counts, response times, parts inclusion, coverage hours |
| Non-standard term | Any deviation from the approved `DT-030` template clause set |
| Service credit | A contractual remedy paid in money on measured SLA breach (`BRU-CTR-08`) |
| Over-consumption | Entitlement used beyond the contracted allowance; blocked or billed, never invisible (`BRU-CTR-04`) |
| Renewal window | T−90 to expiry, driven by `AUT-015` |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Qualified opportunity | `M07` | Customer, sites and asset population identified |
| Device registry populated for the customer | `M17` | RAMC pricing derives from registered appliances (`BRU-CTR-06`) |
| Approved contract template set | `DT-030` | Bespoke drafting outside the template is an exception, not a norm |
| Approved SLA bands | `MD-028` | A band promised must exist; inventing one in a contract creates an unconfigurable obligation |
| Master terms | `LG-015` | Service credit wording must match `MD-028` §2 `credit_calculation` verbatim (`SLA-03`) |
| Rate card and floor | `MD-029`, `M11` | Below-floor pricing requires CCO approval, proposer excluded (`SOD-14`) |
| Capacity check | `M02`, `MD-005` | A contract promising coverage in an unserved zone cannot be delivered |

---

## 5. Procedure

### 5.1 Qualify and scope

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R22 | Qualify: sites, asset population, service expectation, decision process, budget | `P03` · `M07` | Qualified opportunity | — |
| 2 | R22 | Build the covered-asset list from the device registry; survey where the registry is incomplete | `M17` | Asset list | — |
| 3 | R22 | Confirm coverage is deliverable — zone serviceable, skills available, parts supportable | `MD-005`, `MD-010`, `M15` | Deliverability check | — |
| 4 | R22 | Select the SLA band from `MD-028`. **Do not draft a bespoke response time** | `MD-028` | SLA band selected | — |
| 5 | R22 | Price from the rate card; RAMC from registered appliances (`BRU-CTR-06`) | `M11` | Priced proposal | — |
| 6 | R22 | Model the margin. A contract forecast to be margin-negative is escalated before quotation, not after activation (`KPI-031`) | `M54` | Margin model | — |

### 5.2 Quote, approve and sign

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 7 | R22 | Issue the quotation with the `DT-031` SLA schedule attached | `P03` · `P04` | Quotation issued |
| 8 | R22 | Where the customer requires non-standard terms, raise them for approval. **The negotiator may not approve them** (`SOD-15`) | `P03` | Approval request |
| 9 | Legal + CCO/CFO | Review and approve non-standard terms per `SP-004` A-18/A-19 | `P03` | Approval recorded |
| 10 | R22 | Issue the final agreement from `DT-030` with the approved variable clauses only | `M24` | Agreement issued |
| 11 | Customer + R22 | Execute with e-signature. A signed document cannot be modified (`BRU-DMS-03`) | `M24` | Executed agreement |

### 5.3 Activate

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 12 | R22 | Activate: covered assets, entitlements, billing frequency and approval all present (`BRU-CTR-01`) | `M08` | Contract Active |
| 13 | System | Generate the full preventive-maintenance schedule for the term (`AUT-016`) | `M02` | PM schedule |
| 14 | R22 | Provision `P04` access for the customer's users, role-scoped (`EA-03`) | `M29` | Portal access |
| 15 | R32 | For healthcare equipment contracts, schedule calibration as a **mandatory contract element** (`BRU-CTR-07`) | `MD-046` | Calibration schedule |
| 16 | R22 | Hand over to service delivery with a briefing: what is covered, what is not, who to call | — | Handover record |

### 5.4 In-life management

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 17 | R22 | Monitor entitlement consumption; over-consumption is blocked or billed per configuration (`BRU-CTR-04`) | `M08` |
| 18 | R22 | Bill out-of-scope work separately; never absorb it silently (`BRU-CTR-02`) | `M20` |
| 19 | R22 | Monitor SLA attainment; service credits compute automatically from measured breach (`BRU-CTR-08`) | `MD-028`, `SP-005` CO-E3 |
| 20 | R22 | Handle amendments through the same approval path as the original. **The amender may not approve a credit arising from the amendment** (`SOD-16`) | `SP-004` A-23 |
| 21 | R26 | Handle non-payment through the defined notice sequence before any suspension (`BRU-CTR-05`) | `SP-004` A-22 |
| 22 | R22 | Review margin quarterly; a contract drifting negative is renegotiated at renewal, not silently carried | `M54`, `KPI-031` |

### 5.5 Renew or terminate

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 23 | System | Notify customer and account owner at T−90, T−60, T−30, T−15; generate the renewal quotation at T−60 (`AUT-015`) | `NT-*` |
| 24 | R22 | Review actual consumption, incidents and margin before quoting the renewal. **A renewal priced on the original assumptions repeats an error for another year** | `M54` |
| 25 | R22 | Renew, re-scope or decline to renew. Declining to renew a loss-making contract is a legitimate outcome | `SP-004` A-17/A-18 |
| 26 | System | On expiry, cancel all future scheduled work orders and notify the customer (`BRU-CTR-03`) | `M02` |
| 27 | R22 | On termination, reconcile: final billing, entitlement settlement, asset return, portal access revocation | `M20`, `M29` |
| 28 | R26 | Release or recognise deferred revenue per the schedule; manual release requires CFO approval (`BRU-BIL-06`) | `M53`, `SP-020` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 3 | Coverage is not deliverable in a requested zone | Do not contract it. Offer a different delivery mode or exclude the site explicitly | R22 → R05 Operations Director |
| 4 | The customer demands a response time faster than any `MD-028` band | Escalate. Either a new band is registered in `MD-028` first, or the request is declined. **Never write it only into the contract** | R05 + CCO |
| 6 | Forecast margin is negative | Escalate before quotation. `KPI-031` targets fewer than 6% of contracts negative | CCO + CFO |
| 8 | Customer will not accept standard terms | Route to Legal. Non-standard terms are approved, never assumed | Legal + CCO/CFO |
| 9 | Legal proposes wording that changes the service credit calculation | `MD-028`, `LG-015` and `DT-031` must be updated **together**; a divergence between the three is a dispute waiting to happen | Legal + Service Ops + Finance |
| 12 | Any activation precondition is missing | **Activation is blocked** (`BRU-CTR-01`). Do not activate and complete the data later | — |
| 17 | Entitlement exhausted mid-term | Block or bill per configuration, and tell the customer before the next request, not after | R22 |
| 19 | Service credit becomes payable | Automatic calculation stands; manual credits require CFO approval (`BRU-CTR-08`, `SP-004` A-21) | CFO |
| 20 | Amendment materially changes scope or price | Full approval path, not an administrative edit | Per `SP-004` band |
| 21 | Non-payment beyond the notice sequence | Suspension is permitted only after the sequence completes (`BRU-CTR-05`) | CFO |
| 24 | Consumption was far above or below the assumption | Re-scope at renewal. Consistent under-consumption is also a signal — the customer may not renew a contract they do not use | R22 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Contract — standard terms | Any value | R21 Sales Manager (`SP-004` A-17) | CCO |
| Contract — non-standard terms | Any value | CCO + CFO (`SP-004` A-18) | CEO |
| Non-standard terms — negotiator excluded | Any | Approver ≠ negotiating account manager (`SOD-15`, `SP-004` A-19) | — |
| Discount on contract value | ≤ 10% / ≤ 20% / ≤ 35% / > 35% | R08-equivalent / R06 / R21 / CCO | Next level |
| Below price floor | Any | CCO; proposer excluded (`SOD-14`) | — |
| Manual service credit | Any | CFO (`SP-004` A-21) | — |
| Contract suspension for non-payment | Any | CFO, after the notice sequence (`SP-004` A-22) | CEO |
| Subscription amendment credit | Any | Not the amender (`SOD-16`, `SP-004` A-23) | — |
| Registering a new SLA band | Any | Operations Director + Legal + CCO, in `MD-028` first | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| SLA promised in a signed contract does not exist in `MD-028` | Treat as a live delivery risk. Register the band or negotiate an amendment; do not configure an approximation | R05, CCO, Legal | Contract risk register |
| Service credit wording differs between `LG-015`, `DT-031` and `MD-028` | Halt credit calculation on that contract and reconcile the three (`F3` check) | Legal, Finance, Service Ops | `AUDIT` finding |
| Contract activated without a complete asset list | Blocked by `BRU-CTR-01`; if found live, suspend billing until corrected | R22, R26 | Data quality record |
| Preventive schedule not generated | Manual scheduling task; the customer's cover is otherwise notional | R07 Dispatch Manager | `AUT-016` failure log |
| Customer disputes an out-of-scope charge | Route to `SP-028` with the entitlement evidence | R22, R26 | Complaint record |
| Renewal missed and the contract lapsed | Recover as a new contract, not a backdated renewal. Record the cause — `KPI-028` targets 80% renewal | R21, CCO | Renewal loss analysis |
| Contract running materially negative | Escalate at the quarterly review, not at renewal | CCO + CFO | Margin review |
| Signed agreement modified after signature | Not possible (`BRU-DMS-03`). An attempt is a control event | Legal, CTO | `SP-006` exception report |
| Corporate portal user retains access after termination | Access revocation is part of step 27; a lapse is a security finding | CTO | Access exception |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Quotation and agreement are produced from the **controlled `DT-030` template pack** held by Legal; no local copies |
| 2 | Non-standard terms are approved by email from the named approver, with the email retained as the approval record and back-entered |
| 3 | Wet-ink signature where e-signature is unavailable; the executed copy is scanned into `M24` within 2 business days |
| 4 | Activation data — covered assets, entitlements, billing frequency — is recorded on the **contract activation checklist** and entered on restoration. **The contract is not treated as active until entered**, because entitlement checks at intake resolve against the system |
| 5 | R26 reconciles manually activated contracts against the system at month end |

> The fourth row is the important one. A contract that exists on paper but not in the system will
> be refused at intake (`BRU-SRM-03`), which the customer experiences as the company denying its
> own contract.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Activation preconditions enforced | Preventive (`BRU-CTR-01`) | Per contract | Hard block |
| RAMC priced from registered appliances | Preventive (`BRU-CTR-06`) | Per quotation | Computed |
| Out-of-scope work billed separately | Preventive (`BRU-CTR-02`) | Per job | Hard block |
| Entitlement over-consumption blocked or billed | Preventive (`BRU-CTR-04`) | Per request | Hard block |
| Non-standard terms approved by a non-negotiator | Preventive (`SOD-15`) | Per contract | Hard block |
| Suspension only after the notice sequence | Preventive (`BRU-CTR-05`) | Per case | Hard block |
| Calibration mandatory on healthcare contracts | Preventive (`BRU-CTR-07`) | Per contract | Hard block |
| Expiry cancels future work orders | Preventive (`BRU-CTR-03`) | Per expiry | Computed |
| SLA/credit wording reconciliation across `MD-028`, `LG-015`, `DT-031` | Detective | Per audit cycle (`F3`) | Audit record |
| Contract margin review | Detective | Quarterly | `KPI-031` |
| Renewal pipeline ageing | Detective | Monthly | `KPI-028` |
| Contracts active without a complete asset list | Detective | Monthly | Data quality report |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Negotiate a contract | Approve its non-standard terms (`SOD-15`) | Hard block | — |
| Amend a subscription or contract | Approve a credit arising from that amendment (`SOD-16`) | Hard block | — |
| Compute a service credit | Approve it and issue the credit note (`SOD-04` interaction; three separate roles per `M08`) | Hard block | — |
| Own the account | Approve a below-floor price on it (`SOD-14`) | Hard block | — |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-028` | AMC/RAMC renewal rate | 60% | 80%; stretch 88% |
| `KPI-029` | Contract base growth | index | 1.6×; stretch 2.5× |
| `KPI-030` | Contract SLA attainment | unmeasured | 95%; stretch 97% |
| `KPI-031` | Contracts with negative margin | unknown | < 6%; stretch < 3% |
| Activation completeness | Contracts active with a full asset list and entitlements | untracked | 100% |
| Out-of-scope work billed | Proportion of out-of-scope work invoiced rather than absorbed | untracked | 100% |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-030` Contract and AMC Agreement Template Set | The agreement issued at step 10 |
| `DT-031` SLA Schedule and Service Credit Annex | Attached at step 7; **must reconcile exactly** with `MD-028` and `LG-015` |
| `LG-015` AMC/SLA Master Terms and Service Credit Rules | The binding wording |
| `UI-032` Workspace — Contract Console Copy | The screens used |
| `UI-014` `P04` Corporate B2B Portal UI Copy Pack | The customer surface |
| [`SP-011_SOP_Remote_Support_and_Managed_Services.md`](SP-011_SOP_Remote_Support_and_Managed_Services.md) | Delivery of managed-service contracts |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](SP-020_SOP_Month_End_and_Year_End_Close.md) | Deferred revenue and accrual |
| [`../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | §7 bands |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | SLA bands and credit calculation |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032_Contract_and_AMC_Template_Catalogue.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032_Contract_and_AMC_Template_Catalogue.md) | Template catalogue |
| `TR-018` Course Pack — Account and Contract Manager | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CCO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Activation preconditions stated as a hard block with no data-later path
- [x] The "no bespoke SLA in a contract" rule stated at the decision point
- [x] Three-way reconciliation of `MD-028`, `LG-015` and `DT-031` named as a control
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback flags the paper-contract / system-entitlement gap
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `LG-015` written and reconciled with `MD-028` and `DT-031` — **outstanding; `LG` and `DT` categories not yet authored**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CCO and Legal Counsel** (Class B content: Legal approval is the gating control, `CG-007`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
