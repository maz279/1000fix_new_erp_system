---
id: SP-017
title: SOP — Procurement to Payment
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement with Finance
author: Business Process Lead with Procurement and Finance
reviewers: [CFO, Finance Manager, Procurement Manager, Inventory Manager, Internal Audit, Legal Counsel, Localisation Lead]
approver: Chief Financial Officer
content_class: C
purpose: >
  The company's principal cash-outflow control chain. This SOP governs requisition, sourcing,
  purchase order, receipt, three-way match, payment and vendor performance, with the
  segregation-of-duties controls that stop fictitious vendors, duplicate payments and directed
  awards. A vendor invoice cannot be approved without a matched purchase order and goods receipt
  within tolerance; the process is what makes that rule meaningful rather than a configuration
  setting nobody exercises.
traces_to: [M16, M42, M52, M50, M44, M15, M41, P05, DT-021, DT-022, DT-023, DT-024, DT-025, MD-016, MD-038, SP-004, SP-005, SP-018, SP-020]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: SP-017_SOP_Procurement_to_Payment_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M16_Procurement_and_Strategic_Sourcing.md — SOD-01 and SOD-02 enforcement, requester cannot approve own requisition
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §6 BRU-SCM-01…BRU-SCM-05, BRU-INV-03; §7 BRU-FIN-09 TDS; §12.3 AUT-031…AUT-034
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md — requester of a bank-detail change cannot approve it
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-048 vendor on-time delivery, KPI-049 three-way match exception rate
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.4 — control of externally provided processes, products and services, including criteria for evaluation, selection and re-evaluation of external providers
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Procurement to Payment

| Item | Value |
|---|---|
| SOP ID | `SP-017` |
| Process owner | Chief Financial Officer; executed under Procurement Manager and Finance Manager (R26) |
| Roles performing | `R19` Procurement Officer · Procurement Manager · `R17` Inventory Manager · `R20` Warehouse Operative · `R27` Finance Officer · `R26` Finance Manager · CFO |
| Systems used | `P03` Procurement console (`UI-028`) and Finance console (`UI-029`) · `P05` Vendor Portal · `M16` · `M52` · `M50` |
| Frequency / volume | Continuous. The dominant non-payroll cash outflow |
| ISO 9001 clause reference | **8.4** externally provided processes · 8.4.2 type and extent of control · 8.4.3 information for external providers |

---

## 1. Purpose and Outcome

**Purpose.** To buy what the business needs, from an approved supplier, at an authorised value,
receive what was ordered, and pay once — for goods actually received, at the agreed price, with
tax correctly deducted.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Every purchase traces to an approved requisition | `DT-021` with the `SP-004` band satisfied |
| No purchase order went to an inactive or unapproved vendor | `BRU-SCM-02` |
| The invoice matched the PO and the GRN within tolerance | `BRU-SCM-01`; `KPI-049` |
| Nobody created a vendor and approved that vendor's invoice | `SOD-01`, `BRU-SCM-03` |
| Nobody held all three of raise-PO, receive-goods, approve-invoice | `SOD-02` |
| TDS was deducted at the correct rate before payment | `BRU-FIN-09` |
| No duplicate payment left the company | Duplicate detection at §10 |

---

## 2. Scope

**Applies to:** procurement of spare parts, consumables, equipment, services, subcontracted repair
capacity, and capital items; the vendor lifecycle from onboarding to performance review; and
payment through to ledger posting.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Physical receipt, put-away and counting mechanics | `SP-018` |
| Issue of parts to a repair | `SP-016` |
| Import customs, duty and landed cost | `M44`; this SOP resumes at three-way match |
| Payroll disbursement | `SP-021` |
| Employee expense reimbursement | `SP-004` A-39/A-40; processed through `M52` |
| Marketplace seller payouts | `SP-024` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Requisition | The internal request to buy, with justification and budget reference (`DT-021`) |
| RFQ | Request for quotation issued through `P05` (`DT-022`) |
| PO | The purchase order — a legally binding contract with the supplier (`DT-023`) |
| GRN | Goods receipt note with inspection outcome (`DT-024`) |
| Three-way match | Agreement of PO, GRN and invoice within tolerance |
| Tolerance | The configured allowable difference in quantity and price |
| TDS | Tax deducted at source on applicable vendor payments |
| VDS | VAT deducted at source; the supplier's certificate is `DT-013` |
| Competitive threshold | The value above which multiple quotations are required |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Approved budget or cost centre | `M54`, `MD-036` | A requisition without a budget reference is not approvable |
| Vendor master current | `MD-016` | Active and approved status (`BRU-SCM-02`); bank details verified |
| Demand signal | `M43` reorder point or a business request | `AUT-031` drafts the requisition at the reorder point |
| Network stock position | `M15` | A PO for an item already above network maximum requires an override (`BRU-INV-03`, class **A**) |
| Tax configuration | `MD-037` | TDS and VDS rates by supply type |
| Payment terms | `MD-038` | Agreed terms, not improvised per invoice |
| Approval authority current | `SP-004`, `MD-008` | Delegation recorded where an approver is absent |

---

## 5. Procedure

### 5.1 Requisition

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | Requester / `AUT-031` | Raise the requisition: item, quantity, need-by date, justification, budget reference | `P03` | `DT-021` draft | 10 min |
| 2 | System | Check network stock; flag where the purchase would exceed the maximum level (`BRU-INV-03`) | `M15` | Stock check | — |
| 3 | Approver per band | Approve. **A requester may never approve their own requisition at any value** (`SOD-46`) | `P03` | Approval recorded | — |

### 5.2 Source

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 4 | R19 | Below the competitive threshold, buy from the contracted supplier at the agreed rate | `P03` | Sourcing decision |
| 5 | R19 | At or above the threshold, issue the RFQ through `P05` with specification, quantity, terms and deadline | `P05` · `DT-022` | RFQ issued |
| 6 | R19 | Evaluate responses on stated criteria recorded **before** the responses were opened | `P03` | Evaluation record |
| 7 | R19 | Award. **The person who awards may not approve the resulting PO above the competitive threshold** (`SOD-47`) | `P03` | Award decision |

### 5.3 Purchase order

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 8 | R19 | Raise the PO against the approved requisition, to an active approved vendor only (`BRU-SCM-02`) | `P03` · `DT-023` | PO raised |
| 9 | Approver per band | Approve per `SP-004` A-43…A-46 | `P03` | PO approval |
| 10 | System | Transmit and track acknowledgement (`AUT-032`) | `P05` | PO acknowledged |

### 5.4 Receive

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 11 | R20 / R18 | Receive against the PO; count, inspect and record condition (`SP-018`) | `P03` · `DT-024` | GRN |
| 12 | R20 / R18 | Goods failing inspection go to quarantine, never to available stock (`BRU-INV-07`) | `M15` | Quarantine record |
| 13 | R26 | For imports, allocate landed cost before final valuation (`BRU-SCM-04`) | `M44` | Landed cost allocation |

### 5.5 Match and pay

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 14 | R27 | Receive the vendor invoice; verify it carries the supplier's BIN and the correct tax treatment | `P03` | Invoice registered |
| 15 | System | Three-way match PO ↔ GRN ↔ invoice within tolerance (`AUT-033`, `AUT-034`) | `M52` | Match result |
| 16 | R27 | Route matched invoices to the payment schedule; exceptions to the exception queue | `P03` | Routing |
| 17 | R26 | Approve payment. **Never the person who created the vendor** (`SOD-01`, `BRU-SCM-03`) | `P03` | Payment approval |
| 18 | R27 | Deduct TDS at the correct rate; the payment cannot proceed otherwise (`BRU-FIN-09`) | `M51` | TDS computed |
| 19 | R27 | Where VAT is deducted at source, issue `DT-013` VDS certificate to the supplier | `DT-013` | VDS certificate |
| 20 | R26 | Release the payment file; post to the ledger | `M50` · `M19` | Payment and posting |
| 21 | R27 | Reconcile the bank statement; auto-match, present only exceptions (`AUT-044`) | `M50` | Reconciliation |

### 5.6 Vendor performance and returns

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 22 | R19 | Update the vendor scorecard: on-time delivery, quality, responsiveness, price adherence | `M42`, `KPI-048` |
| 23 | R19 | Raise a return to vendor for defective or wrong goods, with `DT-025` debit advice | `SP-016` step 18 |
| 24 | R19 | Track the credit note. **A defective part returned without documentation is an unrecoverable write-off** | `M52` |
| 25 | R19 | Re-evaluate vendors on the review cycle; suspend or remove underperformers | ISO 8.4.1 |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | Network stock already above maximum | Override required, logged (`BRU-INV-03`, class **A**, `SP-004` A-51) | Procurement Manager |
| 3 | Requisition value crosses a band | Approve at the correct band; **splitting to stay below a band is a breach** (`SP-004` AA-05) | Per band |
| 5 | Urgent need below the RFQ timeframe | Emergency sourcing with retrospective justification recorded within 2 business days. Urgency is not a permanent state | Procurement Manager |
| 6 | Only one response received | Record it; a single-source award above the threshold requires a documented justification | Procurement Manager + CFO |
| 8 | Vendor is not active or approved | **Blocked** (`BRU-SCM-02`). Onboard first through `MD-016`; a new vendor is never created to release one payment | R19 |
| 11 | Quantity or specification differs from the PO | Record the actual. Do not receive what was ordered when something else arrived | R20 |
| 12 | Goods fail inspection | Quarantine; notify the vendor; decide return, rework or acceptance with concession | R32 + R19 |
| 15 | Match fails outside tolerance | Exception queue. Resolve with the vendor; **do not adjust the GRN to make the invoice match** | R26 |
| 15 | Invoice arrives with no PO | Return it. Retrospective PO creation to cover an unauthorised purchase defeats the entire control chain | R26 → CFO |
| 17 | The approver created the vendor record | **Blocked** (`SOD-01`). Route to another approver | — |
| 18 | TDS rate uncertain | Do not pay. Confirm with Tax before release; an under-deduction is the company's liability, not the supplier's | R26 → CFO |
| 20 | Suspected duplicate invoice | Hold; verify against paid history by vendor, amount, invoice number and date | R26 |
| 23 | Vendor disputes the return | Escalate through the relationship; document. Do not write off silently | Procurement Manager |
| — | Vendor requests a bank-detail change | **Verify through an independently sourced contact, never the details on the request.** Requester may not approve (`SOD-40`) | R26 + CFO |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Purchase requisition | ≤ BDT 50,000 | R17 Inventory Manager (`SP-004` A-43) | Procurement Manager |
| Purchase requisition | ≤ BDT 500,000 | Procurement Manager (`SP-004` A-44) | CFO |
| Purchase requisition | ≤ BDT 2,000,000 | CFO (`SP-004` A-45) | CEO |
| Purchase requisition | > BDT 2,000,000 | CEO (`SP-004` A-46) | Board |
| Requisition — requester excluded | Any value | Requester never approves own (`SOD-46`) | — |
| Create vendor + approve that vendor's invoice | **Incompatible** (`SOD-01`) | Different people | — |
| Raise PO + receive goods + approve invoice | **Any two permitted, never all three** (`SOD-02`) | — | — |
| Award a sourcing event + approve the resulting PO above the competitive threshold | **Incompatible** (`SOD-47`) | Different people | — |
| Vendor bank-detail change | Any | R26 Finance Manager with independent verification; requester excluded (`SOD-40`, `SP-004` A-97) | CFO |
| Three-way match tolerance override | Outside tolerance | R26 Finance Manager (`SP-004` A-54) | CFO |
| PO exceeding network maximum stock | Any | Procurement Manager override, logged (`SP-004` A-51) | CFO |
| Return to vendor / debit advice | Any | R17 + R26 (`SP-004` A-52) | CFO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Invoice with no PO | Return to the vendor; investigate who committed the spend | R26 → CFO | Unauthorised spend register |
| Three-way match exception | Exception queue; resolve with the vendor, never by editing the receipt | R26 (`SP-005` SC-E3) | Exception log |
| Suspected duplicate payment | Stop the payment; verify; recover if already paid | R26, CFO | Duplicate register |
| Vendor bank details changed and payment misdirected | **L4-direct: CFO + Internal Audit**, restricted. Contact the bank immediately | As stated | Fraud incident |
| Vendor delivery overdue | Chase per `SP-005` SC-E4; assess alternative sourcing before the stockout | R19 | Vendor scorecard |
| Goods failed inspection | Quarantine; supplier nonconformity raised | R32, R19 (`SP-005` SC-E5) | `M42` nonconformity |
| Counterfeit parts received | Quarantine; do not return without instruction; escalate — this is a brand and safety matter | R32, Legal, CCO | Restricted record |
| Emergency purchase without prior approval | Retrospective approval within 2 business days, with the justification. A pattern of these is a control failure | Procurement Manager → CFO | Emergency purchase register |
| TDS under-deducted and payment made | Correct and remit; the liability sits with 1000FiX | R26 → CFO, Tax | Tax exception |
| Vendor portal unavailable | Manual RFQ and PO transmission per §9 | R19, R33 | Manual log |

---

## 9. Manual Fallback

`IP-09` requires a defined manual fallback for every P0 integration. Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Requisitions on the **pre-numbered manual requisition pad**, signed by the approver at the correct band — the band does not relax during an outage |
| 2 | RFQ and PO issued by email from a controlled mailbox, with the PO number allocated from a **reserved manual PO number range** so that no number collides on restoration |
| 3 | Receipts recorded on the **manual GRN book**, countersigned by the receiver and a second person |
| 4 | Three-way match performed on paper: PO copy, GRN copy, invoice, checked and signed by R27 and reviewed by R26 |
| 5 | **No payment is released during an outage without R26 approval on the paper match**, and no payment at all above the `SP-004` A-45 band without CFO signature |
| 6 | **Back-enter every requisition, PO, GRN and invoice within 48 hours**, preserving dates and the manual numbers |
| 7 | R26 reconciles all manual documents against the system and signs; Internal Audit samples them |

> The reserved manual PO number range matters. Without it, back-entry generates system PO numbers
> that do not match the numbers the supplier holds, and every subsequent match fails.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Vendor invoice requires matched PO and GRN within tolerance | Preventive (`BRU-SCM-01`) | Per invoice | Hard block |
| PO only to active approved vendors | Preventive (`BRU-SCM-02`) | Per PO | Hard block |
| Vendor creator cannot approve that vendor's invoice | Preventive (`SOD-01`, `BRU-SCM-03`) | Per invoice | Hard block |
| Raise/receive/approve — any two, never all three | Preventive (`SOD-02`) | At assignment | Hard block |
| Requester cannot approve own requisition | Preventive (`SOD-46`) | Per requisition | Hard block |
| Award and PO approval separated above threshold | Preventive (`SOD-47`) | Per award | Hard block |
| Bank-detail change requester cannot approve | Preventive (`SOD-40`) | Per change | Hard block |
| TDS deducted before payment | Preventive (`BRU-FIN-09`) | Per payment | Hard block |
| Landed cost allocated before final valuation | Preventive (`BRU-SCM-04`) | Per import | Computed |
| Duplicate invoice detection by vendor, number, amount, date | Detective | Per invoice | Duplicate report |
| Split-requisition detection near band ceilings | Detective (`SP-004` AA-12) | Monthly | Internal Audit report |
| Three-way match exception rate | Detective | Monthly | `KPI-049` |
| Vendor scorecard and re-evaluation | Detective (ISO 8.4.1) | Quarterly | `KPI-048` |
| Emergency purchase pattern review | Detective | Monthly | Emergency register |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Create a vendor | Approve that vendor's invoice (`SOD-01`) | Hard block at assignment | — |
| Raise a PO + receive goods | Approve the invoice (`SOD-02`) | Hard block — any two permitted | At small sites, invoice approval routes to central Finance |
| Request a vendor bank-detail change | Approve it (`SOD-40`) | Hard block | Independent verification by a call to a separately sourced number |
| Raise a requisition | Approve it (`SOD-46`) | Hard block, any value | — |
| Award a sourcing event | Approve the resulting PO above the competitive threshold (`SOD-47`) | Threshold block | — |
| Hold procurement authority | Adjust the stock balances that justify buying | Hard block at assignment | R19 holds read-only stock access |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-048` | Vendor on-time delivery | unmeasured | 88%; stretch 92% |
| `KPI-049` | Three-way match exception rate | n/a | < 8%; stretch < 5% |
| `KPI-043` | Part availability at first request | unmeasured | 88%; stretch 93% |
| Duplicate payments | Payments made twice for one liability | untracked | **Zero** |
| Invoices received without a PO | Unauthorised spend indicator | untracked | Falling to zero |
| Emergency purchases | Purchases bypassing the RFQ path | untracked | < 5% of value |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-021` Purchase Requisition | Step 1 |
| `DT-022` Request for Quotation | Step 5 |
| `DT-023` Purchase Order | Step 8 |
| `DT-024` Goods Receipt Note and Inspection Record | Step 11 |
| `DT-025` Return to Vendor and Debit Advice | Step 23 |
| `DT-013` VDS Certificate Mushak 6.6 | Step 19 |
| `UI-028` Workspace — Procurement Console Copy · `UI-015` `P05` Vendor Portal Copy Pack | The screens used |
| [`SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | Physical receipt mechanics |
| [`SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | Downstream consumption |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](SP-020_SOP_Month_End_and_Year_End_Close.md) | Accruals for received-not-invoiced |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Vendor master and bank details |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | TDS and VDS rates |
| `TR-013` Course Pack — Procurement Officer · `TR-014` Course Pack — Finance Officer and Manager | Train this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] "Do not adjust the GRN to make the invoice match" stated at the decision point
- [x] Vendor bank-detail change verified through an independently sourced contact
- [x] Retrospective PO creation named as defeating the control chain
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback reserves a PO number range so back-entry does not collide
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Competitive threshold and match tolerances configured — **outstanding, depends on `SP-002`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
