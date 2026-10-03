---
id: SP-019
title: SOP — Cash Collection and Banking
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Business Process Lead with Finance Operations
reviewers: [CFO, Finance Manager, Operations Director, Branch Managers Forum, Internal Audit, HSE Lead, Legal Counsel, Localisation Lead]
approver: Chief Financial Officer
content_class: C
purpose: >
  Cash across 51+ branches and 50–150 riders is the highest fraud-risk process in the business.
  This SOP governs collection at the counter and in the field, custody, daily reconciliation,
  banking and shortfall handling. Branch cash must be reconciled and closed daily and an
  unclosed shift blocks the next shift's opening; that rule is only a control if the SOP that
  operates it separates the person who holds cash from the person who reconciles it.
traces_to: [M20, M50, M04, M02, M03, P03, P09, DT-016, MD-038, SP-004, SP-005, SP-006, SP-007, SP-008, SP-009, SP-020]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: SP-019_SOP_Cash_Collection_and_Banking_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §7 BRU-FIN-02, BRU-FIN-10; §3 BRU-FSM-07; §4 BRU-LOG-06
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md — BRU-FRD-11 and SOD-12, counter cash handler cannot perform the shift reconciliation
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §6 SOD-12 — handle cash and reconcile the cash book, hard block
    verified: 2026-08-15
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md §4.6 — SOD-12 is structurally violated at C4/C5 single-person sites; compensating controls defined
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.1 controlled conditions; clause 9.1 monitoring and measurement
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Cash Collection and Banking

| Item | Value |
|---|---|
| SOP ID | `SP-019` |
| Process owner | Chief Financial Officer; executed under Branch Manager (R06) and Finance Manager (R26) |
| Roles performing | `R29` Cashier / Counter Finance · `R08` Service Centre Agent · `R16` Rider · `R10`–`R12` Technicians · `R06` Branch Manager · `R27` Finance Officer · `R26` Finance Manager |
| Systems used | `P03` Finance console (`UI-029`) · `P09` · `M20` · `M50` |
| Frequency / volume | Every shift, every day, at 51+ branches plus field collections |
| ISO 9001 clause reference | 8.5.1 controlled conditions · 9.1 monitoring · 7.5.3 documented information |

---

## 1. Purpose and Outcome

**Purpose.** To take money from a customer, give a receipt, hold it securely, count it, reconcile
it to the system, bank it, and account for any difference — every shift, at every site, without
exception.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Every collection produced a receipt | `DT-016` |
| Cash receipts above BDT 50,000 recorded the customer's NID | `BRU-FIN-02` |
| The shift closed with a reconciled position | `BRU-FIN-10` — an unclosed shift blocks the next |
| Field and rider cash reached the branch by shift end | `BRU-FSM-07`, `BRU-LOG-06` |
| The person who held the cash did not reconcile it | `SOD-12`, or the documented compensating control |
| Banking matched the reconciled position | Bank reconciliation (`AUT-044`) |
| Variance was explained, not absorbed | Variance register |

---

## 2. Scope

**Applies to:** cash, mobile financial services (MFS), card and bank transfers collected at
branch counters, in the field by technicians, and on delivery by riders; the branch float; and
banking of takings.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Invoicing and credit control | `M20`; dunning in `DT-018` |
| Vendor payments out | `SP-017` |
| Payroll disbursement | `SP-021` |
| Petty cash expenditure approval | `SP-004` A-38; the custody rules here still apply |
| Marketplace seller payouts | `SP-024` |
| Month-end bank reconciliation and posting | `SP-020` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Float | The opening cash held at a counter to give change |
| Takings | Cash collected during a shift, excluding the float |
| Shift close | The counted, reconciled and signed end of a cashier's session |
| Blind declaration | Counting and declaring the cash before the system's expected figure is visible |
| Variance | Declared cash minus system-expected cash |
| Banking | Physical or electronic transfer of takings to the company bank account |
| MFS | Mobile financial services (bKash, Nagad and similar), settled per `MD-038` |
| Drop | Transfer of accumulated cash from the counter to the branch safe during a shift |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Prior shift closed and reconciled | `M50` | **An unclosed shift blocks the next shift's opening** (`BRU-FIN-10`) |
| Float issued and counted | `M50` | Counted by the incoming cashier in the presence of the issuer |
| Safe operational, keys and combination controlled | `M47`, `SP-032` | Access list current; combination changed on a leaver event |
| Receipt capability | `DT-016` | System receipts, or the pre-numbered manual receipt book |
| Payment methods configured | `MD-038` | MFS merchant accounts and settlement cycles known |
| Cashier logged in individually | `M29` | **No shared logins.** Attribution is the whole control |
| Cash-in-transit arrangement | Contract | Collection schedule and limits agreed |

---

## 5. Procedure

### 5.1 Shift open

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R06 | Confirm the prior shift closed. If not, resolve before opening (`BRU-FIN-10`) | `P03` | Prior close verified | 2 min |
| 2 | R06 + R29 | Issue and jointly count the float | `P03` | Float record, both signatures | 5 min |
| 3 | R29 | Open the shift under their own login | `P03` | Shift open, timestamped | 1 min |

### 5.2 Collection at the counter

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 4 | R29 / R08 | Take payment against the specific invoice or order. Never against "the customer" generally | `P03` | Payment allocated |
| 5 | R29 | For cash above BDT 50,000, record the customer's NID. **Class H, no approval path** (`BRU-FIN-02`) | `P03` | NID recorded |
| 6 | R29 | Count the cash in front of the customer; state the amount received and the change given | — | — |
| 7 | R29 | Issue the receipt (`DT-016`) and hand it over before the customer leaves | `P03` print | Receipt issued |
| 8 | R29 | For MFS and card, confirm the transaction reference on the terminal or app **before** releasing the device or closing the order | `P03` | Reference captured |
| 9 | R29 | Drop cash to the safe at the configured accumulation limit, recorded and countersigned | `P03` | Drop record |

### 5.3 Field and rider collection

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 10 | R10–R12 / R16 | Take payment against the order; issue the receipt from `P02`/`P09` (`DT-016`) | `P02` / `P09` | Receipt issued |
| 11 | R10–R12 / R16 | Prefer MFS or card where the customer can use it. **Cash carried is cash at risk** | `P02` / `P09` | Method recorded |
| 12 | R10–R12 / R16 | Hand cash to R29 at the branch **by the end of the shift** (`BRU-FSM-07`, `BRU-LOG-06`) | `P03` | Handover receipt |
| 13 | R29 | Count in the presence of the handing-over person; both sign | `P03` | Handover record |

### 5.4 Shift close and reconciliation

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 14 | R29 | Count the drawer and the safe contents attributable to the shift | — | Physical count |
| 15 | R29 | **Declare the counted figure before viewing the system expectation** — blind declaration | `P03` | Declaration |
| 16 | System | Compare declaration to expected; produce the variance | `M50` | Variance |
| 17 | R29 | Explain any variance with a reason code | `MD-026` | Explanation |
| 18 | **A person other than R29** — R06 or a designated second person | Verify the count and reconcile the cash book (`SOD-12`) | `P03` | Reconciliation signed |
| 19 | R06 | Close the shift. An unclosed shift blocks the next (`BRU-FIN-10`) | `P03` | Shift closed |

### 5.5 Banking

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 20 | R06 | Prepare the banking against the reconciled position; do not bank an unreconciled amount | `P03` | Banking slip prepared |
| 21 | R06 + escort or cash-in-transit provider | Transfer to the bank within the configured frequency and never above the configured holding limit | — | Transit record |
| 22 | R27 | Match the bank credit to the banking record | `M50` | Match |
| 23 | R27 | Auto-match the statement; present only exceptions (`AUT-044`) | `M50` | Reconciliation |
| 24 | R26 | Review unmatched items daily; clear or escalate | `P03` | Exception review |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 1 | Prior shift unclosed | Do not open. Resolve the prior close first (`BRU-FIN-10`) | R06 |
| 2 | Float does not count correctly at issue | Do not accept it. Resolve before the shift starts | R06 |
| 5 | Customer refuses to give NID for a cash payment above BDT 50,000 | Offer MFS, card or bank transfer instead. The cash payment cannot proceed — class **H** | — |
| 8 | MFS or card confirmation not received | Do not release the device or close the order. A pending transaction is not a payment | R29 |
| 9 | Counter cash exceeds the accumulation limit | Drop to the safe immediately; do not defer to shift end | R29 |
| 12 | Rider or technician cannot reach the branch by shift end | Arrange a supervised handover the same day; record the exception. Overnight retention is an exception, not a routine | R06 |
| 15 | Cashier can see the expected figure before declaring | Stop. A sighted declaration is not a control | R06 |
| 17 | Variance is a shortfall | Recount; check unallocated receipts and unposted MFS; **do not make it up from personal funds** — that conceals the variance | R06 |
| 17 | Variance is an overage | Record it. An overage is as much a control signal as a shortfall | R06 |
| 18 | No second person is available to reconcile | Apply the `SP-006` §4.6 compensating control: blind declaration plus remote variance review by a Branch Manager at another site | R06 → R26 |
| 20 | Holding exceeds the configured limit before the next banking | Arrange an unscheduled banking. Cash held above the limit is uninsured | R06 |
| — | Robbery, threat or attempted theft | **Comply. Do not resist.** Safety first (`SP-030`), then report immediately | HSE + R06 → R05 + CFO |
| — | Suspected internal theft | **L4-direct: CFO + Internal Audit**, restricted. Do not confront locally | As stated |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Cash receipt above BDT 50,000 without NID | **None — class H, no approval path** (`BRU-FIN-02`) | — | — |
| Write off a cash shortfall | ≤ BDT 5,000 | R26 Finance Manager | CFO |
| Write off a cash shortfall | > BDT 5,000 | CFO | CEO |
| Petty cash / float replenishment | ≤ BDT 25,000 | R06 Branch Manager (`SP-004` A-38) | R26 |
| Hold cash overnight above the configured limit | Any | R06, recorded as an exception | R26 |
| Refund in cash at the counter | ≤ BDT 10,000 | R26 Finance Manager (`SP-004` A-27) | CFO |
| Refund to a method other than the original | Any | CFO (`SP-004` A-29) | — |
| Handle cash + reconcile the cash book | **Incompatible** (`SOD-12`) | Different people, or the documented compensating control | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Unexplained variance at any value | Recount; investigate the same day; do not carry it forward | R06 + R26 (`SP-005` SC-E7) | Variance register |
| Shift not closed | Next shift blocked; escalate within the hour | R06 + R26 (`SP-005` SC-E6) | Shift exception |
| Rider cash not reconciled at shift end | Zero tolerance for unexplained variance (`BRU-LOG-06`) | R15 + R26 (`SP-005` SC-E8) | Rider cash record |
| MFS settlement not received per `MD-038` cycle | Chase the provider; hold the receivable in suspense, not in revenue | R27 → R26 | Suspense |
| Counterfeit note detected | Retain it, record the details, inform the bank; do not return it to the customer | R06, R26 | Counterfeit record |
| Receipt issued but no payment received | Void with a reason and a second signature; a voided receipt is retained, never destroyed | R06 | Void register |
| Manual receipt book page missing | Treat as a control incident, not an administrative slip | R06 → R26 | Stationery control record |
| Safe cannot be opened / key lost | Follow the dual-control key procedure; never force it | R06 → R26 | Facility record |
| Robbery or threat | Comply; preserve the scene; report to police and to the insurer | HSE, R05, CFO, Legal | Incident + insurance claim |
| Suspected internal theft | Restricted escalation; the local manager may be the subject | CFO + Internal Audit | Restricted record |

---

## 9. Manual Fallback

Cash does not stop when the system does. Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Issue payments on the **pre-numbered manual receipt book**. This book is controlled stationery: issued by Finance, its range recorded, its return accounted for |
| 2 | Record each receipt: date, receipt number, customer, order reference, amount, method, cashier signature |
| 3 | Above BDT 50,000 in cash, record the NID on the manual receipt — the rule does not relax during an outage |
| 4 | At shift end, count physically and complete the **manual shift reconciliation sheet**, signed by the cashier and by a second person |
| 5 | Bank against the manual reconciliation; retain the bank slip |
| 6 | **Back-enter every receipt and reconciliation within 24 hours**, preserving receipt numbers and times |
| 7 | R26 reconciles the manual book against the system and signs; unused numbers are accounted for; Internal Audit samples |

> The pre-numbered receipt book is the oldest control in this SOP and the most reliable. It works
> because a missing number is visible. Any replacement must have the same property.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Cash above BDT 50,000 requires NID | Preventive (`BRU-FIN-02`) | Per receipt | Hard block |
| Unclosed shift blocks the next | Preventive (`BRU-FIN-10`) | Per shift | Hard block |
| Field cash reconciled by shift end | Preventive (`BRU-FSM-07`, `BRU-LOG-06`) | Per shift | Reconciliation record |
| Cash handling and reconciliation separated | Preventive (`SOD-12`) | Per shift | Hard block at assignment |
| Blind declaration before the expected figure | Preventive | Per shift close | Declaration sequence |
| Individual logins, no sharing | Preventive | Continuous | `M29` |
| Payment allocated to a specific invoice | Preventive | Per payment | Hard block |
| Manual receipt books issued and reconciled | Preventive | Per issue | Stationery register |
| Accumulation and holding limits | Preventive | Continuous | Drop and banking records |
| Daily variance review | Detective | Daily | Variance register |
| Bank reconciliation auto-match | Detective (`AUT-044`) | Daily | `KPI-051` |
| Surprise cash counts | Detective | Monthly, unannounced | Count record |
| Variance trend by site and cashier | Detective | Monthly | Internal Audit report |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Handle cash | Reconcile the cash book (`SOD-12`) | Hard block at assignment | **Structurally violated at C4/C5 single-person sites.** Apply `SP-006` §4.6: blind declaration before the expected figure is visible, variance auto-reported to a Branch Manager at another site and to Finance, plus a weekly surprise count by the cluster manager or a `P11` field auditor |
| Take a payment | Approve a refund on the same order (`SOD-04` pattern) | Hard block | Refund approval sits with Finance |
| Hold the safe key | Hold the safe combination | Dual control | Both held by different people; changed on a leaver event |
| Issue manual receipt books | Reconcile their use | Hard block | Finance issues; Internal Audit samples |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-051` | Bank reconciliation auto-match | manual | 90%; stretch 94% |
| Unexplained cash variance | Value unexplained after investigation | untracked | **Zero** |
| Shifts closed on time | Shifts reconciled and closed within the shift | untracked | 100% |
| Field cash reconciled same shift | Technician and rider cash handed over by shift end | untracked | 100% |
| Cash as a share of collections | Proportion collected in cash rather than MFS/card | untracked | Falling — cash risk falls with cash volume |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-016` Payment Receipt and Money Receipt | Issued at steps 7 and 10 |
| `UI-029` Workspace — Finance Console Copy | The screens used |
| [`SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | Counter collection |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | Field collection and handover |
| [`SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | Cash on delivery |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](SP-020_SOP_Month_End_and_Year_End_Close.md) | Bank reconciliation at close |
| [`SP-032_Operational_Checklist_Library.md`](SP-032_Operational_Checklist_Library.md) | Shift open and close checklists |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | `SOD-12` and its compensating controls |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) | Methods and settlement cycles |
| `TR-014` Course Pack — Finance Officer and Manager · `TR-011` Course Pack — Branch Manager | Train this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Blind declaration specified before the expected figure is shown
- [x] "Do not make up a shortfall from personal funds" stated explicitly
- [x] The structural `SOD-12` violation at small sites is named, not hidden, with its compensating control
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback keeps the NID rule and the pre-numbered receipt control in force
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Accumulation, holding and banking-frequency limits configured per site class — **outstanding, depends on `SP-002`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
