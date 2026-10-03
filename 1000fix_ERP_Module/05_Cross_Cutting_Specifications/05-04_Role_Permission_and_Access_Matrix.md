---
id: FIX-ERP2-014
title: Role, Permission & Access Matrix
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Role, Permission & Access Matrix
# 38 Roles Across 30 Modules and 12 Portals

---

## 1. Role Register

Expanded from 20 roles in v1.0 to 38 in v2.0.

### 1.1 Internal — Executive & Management (5)

| ID | Role | Headcount | Portals | MFA | Data Scope |
|---|---|---:|---|:--:|---|
| R01 | Chief Executive Officer | 1 | P03, P06 | Yes | All entities |
| R02 | Chief Technology Officer | 1 | P03, P06 | Yes | All entities + system |
| R03 | Chief Financial Officer | 1 | P03, P06 | Yes | All entities |
| R04 | Chief Commercial Officer | 1 | P03, P06 | Yes | All entities |
| R05 | Operations Director | 1–2 | P03, P06 | Yes | All branches |

### 1.2 Internal — Service Operations (9)

| ID | Role | Headcount | Portals | MFA | Data Scope |
|---|---|---:|---|:--:|---|
| R06 | Branch Manager | 51+ | P03, P06, P11 | Yes | Own branch |
| R07 | Dispatch Manager | 3–8 | P03, P06 | Yes | Assigned zones |
| R08 | Service Centre Agent | 150–250 | P03 | No | Own branch |
| R09 | Workshop Supervisor | 20–40 | P03 | No | Own workshop |
| R10 | Senior Technician | 80–150 | P02 | No | Assigned jobs + zone |
| R11 | Junior Technician | 120–250 | P02 | No | Assigned jobs |
| R12 | Specialist Technician (L3 / board-level) | 15–30 | P02, P03 | No | Assigned jobs + workshop |
| R13 | Remote Support Engineer | 15–40 | P03, P10 | Yes | Assigned clients |
| R14 | Data Services Technician | 5–12 | P03 | Yes | Assigned cases only (T5) |

### 1.3 Internal — Logistics & Supply Chain (6)

| ID | Role | Headcount | Portals | MFA | Data Scope |
|---|---|---:|---|:--:|---|
| R15 | Logistics Coordinator | 10–25 | P03, P09 | No | Own area or central |
| R16 | Rider / Delivery Agent | 50–150 | P09 | No | Own manifest |
| R17 | Inventory Manager | 5–10 | P03, P06 | No | All locations |
| R18 | Branch Store Keeper | 51+ | P03 | No | Own branch stock |
| R19 | Procurement Officer | 4–8 | P03, P05 | Yes | Central procurement |
| R20 | Warehouse Operative | 15–30 | P03 | No | Own warehouse |

### 1.4 Internal — Commercial (5)

| ID | Role | Headcount | Portals | MFA | Data Scope |
|---|---|---:|---|:--:|---|
| R21 | Sales Manager | 3–6 | P03, P06 | Yes | Assigned segment |
| R22 | Account Manager (Corporate) | 8–20 | P03, P06 | Yes | Assigned accounts |
| R23 | Marketing Manager | 2–4 | P03, P06 | Yes | All customer segments |
| R24 | Marketplace Operations Officer | 4–10 | P03 | Yes | Marketplace domain |
| R25 | Retail / Refurbishment Officer | 5–15 | P03 | No | Refurbishment & resale |

### 1.5 Internal — Finance, People & Governance (7)

| ID | Role | Headcount | Portals | MFA | Data Scope |
|---|---|---:|---|:--:|---|
| R26 | Finance Manager | 2–4 | P03, P06 | Yes | All entities |
| R27 | Finance Officer | 10–20 | P03 | Yes | Assigned scope |
| R28 | Warranty Claims Officer | 4–10 | P03, P08 | Yes | All claims |
| R29 | Cashier / Counter Finance | 51+ | P03 | No | Own counter & shift |
| R30 | HR Manager | 1–2 | P03, P06 | Yes | All employees |
| R31 | HR Officer | 3–6 | P03 | Yes | Assigned scope |
| R32 | Quality Manager / ISO Coordinator | 2–4 | P03, P06, P11 | Yes | All branches |

### 1.6 Internal — Technology & Support (3)

| ID | Role | Headcount | Portals | MFA | Data Scope |
|---|---|---:|---|:--:|---|
| R33 | IT / System Administrator | 4–8 | P03 (system console) | Yes | All systems |
| R34 | Contact Centre Agent | 30–60 | P10 | No | Customer-facing scope |
| R35 | Contact Centre Supervisor | 4–10 | P10, P06 | Yes | Own team + queues |

### 1.7 External (3 classes, multiple sub-roles)

| ID | Role | Population | Portals | MFA | Data Scope |
|---|---|---:|---|:--:|---|
| R36 | Customer (Individual) | 250,000+/month | P01 | Optional | Own records only |
| R37 | Corporate Portal User (Requester / Approver / Finance / Admin) | 500–2,000 | P04 | Optional (mandatory for Approver & Finance) | Own company; role-scoped within it |
| R38 | External Party (Vendor · Marketplace Seller · Brand Partner · Courier · Referral Partner · Recycling Partner · External Auditor) | 1,000–3,000 | P05, P07, P08, P09, P12 | Yes for financial actions | Own records only |

---

## 2. Portal Access Matrix

| Role | P01 | P02 | P03 | P04 | P05 | P06 | P07 | P08 | P09 | P10 | P11 | P12 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| R01 CEO | | | ● | | | ● | | | | | | |
| R02 CTO | | | ● | | | ● | | | | | | |
| R03 CFO | | | ● | | | ● | | | | | | |
| R04 CCO | | | ● | | | ● | | | | | | |
| R05 Operations Director | | | ● | | | ● | | | | | ● | |
| R06 Branch Manager | | | ● | | | ● | | | | | ● | |
| R07 Dispatch Manager | | | ● | | | ● | | | ● | | | |
| R08 Service Centre Agent | | | ● | | | | | | | | | |
| R09 Workshop Supervisor | | | ● | | | | | | | | | |
| R10 Senior Technician | | ● | | | | | | | | | | |
| R11 Junior Technician | | ● | | | | | | | | | | |
| R12 Specialist Technician | | ● | ● | | | | | | | | | |
| R13 Remote Support Engineer | | | ● | | | | | | | ● | | |
| R14 Data Services Technician | | | ● | | | | | | | | | |
| R15 Logistics Coordinator | | | ● | | ● | | | | ● | | | |
| R16 Rider | | | | | | | | | ● | | | |
| R17 Inventory Manager | | | ● | | ● | ● | | | | | | |
| R18 Branch Store Keeper | | | ● | | | | | | | | | |
| R19 Procurement Officer | | | ● | | ● | | | | | | | |
| R20 Warehouse Operative | | | ● | | | | | | | | | |
| R21 Sales Manager | | | ● | | | ● | | | | | | |
| R22 Account Manager | | | ● | ● | | ● | | | | | | |
| R23 Marketing Manager | | | ● | | | ● | | | | | | ● |
| R24 Marketplace Operations | | | ● | | | ● | ● | | | | | |
| R25 Retail / Refurb Officer | | | ● | | | | | | | | | |
| R26 Finance Manager | | | ● | | ● | ● | | ● | | | | |
| R27 Finance Officer | | | ● | | ● | | | | | | | |
| R28 Warranty Claims Officer | | | ● | | | ● | | ● | | | | |
| R29 Cashier | | | ● | | | | | | | | | |
| R30 HR Manager | | | ● | | | ● | | | | | | |
| R31 HR Officer | | | ● | | | | | | | | | |
| R32 Quality Manager | | | ● | | | ● | | | | | ● | |
| R33 IT Administrator | | | ● | | | | | | | | | |
| R34 Contact Centre Agent | | | | | | | | | | ● | | |
| R35 Contact Centre Supervisor | | | ● | | | ● | | | | ● | | |
| R36 Customer | ● | | | | | | | | | | | |
| R37 Corporate User | | | | ● | | | | | | | | |
| R38 External Party | | | | | ● | | ● | ● | ● | | | ● |

---

## 3. Module Permission Matrix

Legend: **C** create · **R** read · **U** update · **D** delete/archive · **A** approve ·
**–** no access · scope suffix: `(o)` own · `(b)` branch · `(z)` zone · `(a)` all

### 3.1 Pillar A — Service Operations

| Role | M01 SRM | M02 FSM | M03 LOG | M04 FRD | M05 RMS | M06 DTS |
|---|---|---|---|---|---|---|
| R05 Operations Director | CRUDA(a) | CRUDA(a) | CRU(a) | R(a) | R(a) | R(a) |
| R06 Branch Manager | CRUDA(b) | CRUA(b) | CRU(b) | CRUDA(b) | – | R(b) |
| R07 Dispatch Manager | CRU(z) | CRUDA(z) | CRU(z) | R(z) | – | – |
| R08 Service Centre Agent | CRU(b) | R(b) | C,R(b) | CRU(b) | – | C,R(b) |
| R09 Workshop Supervisor | CRU(b) | RU(b) | R(b) | R(b) | – | R(b) |
| R10 Senior Technician | RU(o) | RU(o) | RU(o) | – | R(o) | RU(o) |
| R11 Junior Technician | RU(o) | RU(o) | R(o) | – | – | – |
| R12 Specialist Technician | RU(o) | RU(o) | R(o) | – | – | RU(o) |
| R13 Remote Support Engineer | CRU(a) | R(a) | – | – | CRUDA(a) | R(a) |
| R14 Data Services Technician | R(o) | – | R(o) | – | – | CRUD(o) |
| R15 Logistics Coordinator | R(a) | R(a) | CRUDA(a) | – | – | R(a) |
| R16 Rider | R(o) | – | RU(o) | – | – | – |
| R34 Contact Centre Agent | CRU(a) | R(a) | R(a) | – | CR(a) | CR(a) |

### 3.2 Pillar B — Commercial & Revenue

| Role | M07 CRM | M08 CTR | M09 WTY | M10 LOY | M11 SLS | M12 ECM | M13 RNT | M14 TRF |
|---|---|---|---|---|---|---|---|---|
| R04 CCO | CRUDA(a) | CRUDA(a) | R(a) | CRUDA(a) | CRUDA(a) | CRUDA(a) | RA(a) | RA(a) |
| R06 Branch Manager | CRU(b) | R(b) | R(b) | R(b) | RU(b) | R(b) | CRU(b) | CRU(b) |
| R08 Service Centre Agent | CRU(b) | R(b) | CR(b) | CRU(b) | CR(b) | CR(b) | CR(b) | CR(b) |
| R21 Sales Manager | CRU(a) | CRUA(a) | R(a) | CRU(a) | CRUA(a) | R(a) | CRU(a) | R(a) |
| R22 Account Manager | CRU(o) | CRUA(o) | R(o) | R(o) | CRU(o) | – | CRU(o) | R(o) |
| R23 Marketing Manager | R(a) | – | – | CRUDA(a) | R(a) | RU(a) | – | – |
| R24 Marketplace Operations | R(a) | R(a) | – | R(a) | RU(a) | CRUDA(a) | – | – |
| R25 Retail / Refurb Officer | R(a) | – | R(a) | – | R(a) | CRU(a) | R(a) | CRUD(a) |
| R28 Warranty Claims Officer | R(a) | R(a) | CRUDA(a) | – | – | – | – | – |
| R34 Contact Centre Agent | CRU(a) | R(a) | CR(a) | CRU(a) | CR(a) | CR(a) | CR(a) | CR(a) |
| R36 Customer | RU(o) | R(o) | CR(o) | R(o) | R(o) | CRU(o) | CRU(o) | CR(o) |
| R37 Corporate User | RU(own co.) | R(own co.) | CR(own co.) | – | R(own co.) | CRU(own co.) | CRU(own co.) | CR(own co.) |

### 3.3 Pillar C — Supply Chain & Assets

| Role | M15 INV | M16 SCM | M17 AST | M18 ESG |
|---|---|---|---|---|
| R17 Inventory Manager | CRUDA(a) | CRU(a) | R(a) | R(a) |
| R18 Branch Store Keeper | CRU(b) | C,R(b) | R(b) | C,R(b) |
| R19 Procurement Officer | R(a) | CRUDA(a) | R(a) | R(a) |
| R20 Warehouse Operative | CRU(own loc) | R(own loc) | R(own loc) | CR(own loc) |
| R06 Branch Manager | RU(b) | R,A(b) | RU(b) | R(b) |
| R10/R11/R12 Technician | R(o van) | – | RU(o jobs) | C(o) |
| R32 Quality Manager | R(a) | R(a) | R(a) | CRUDA(a) |
| R38 Vendor | – | R(own POs) | – | – |
| R38 Recycling Partner | – | – | – | RU(own batches) |

### 3.4 Pillar D — Finance, People & Governance

| Role | M19 FIN | M20 BIL | M21 HRM | M22 LMS | M23 QMS | M24 DMS |
|---|---|---|---|---|---|---|
| R03 CFO | CRUDA(a) | CRUDA(a) | R(a) | – | R(a) | R(a) |
| R26 Finance Manager | CRUDA(a) | CRUDA(a) | R(payroll totals) | – | R(a) | RU(a) |
| R27 Finance Officer | CRU(scope) | CRU(scope) | – | – | – | R(scope) |
| R28 Warranty Claims Officer | R(claims) | CRU(claims) | – | – | R(a) | RU(claims) |
| R29 Cashier | CR(own shift) | CR(own counter) | – | – | – | R(o) |
| R30 HR Manager | R(payroll) | – | CRUDA(a) | CRUDA(a) | R(a) | RU(HR) |
| R31 HR Officer | – | – | CRU(scope) | CRU(scope) | – | R(HR) |
| R32 Quality Manager | – | – | R(a) | R(a) | CRUDA(a) | CRUDA(a) |
| R06 Branch Manager | R(b) | R(b) | R(b staff) | R(b staff) | CRU(b) | CRU(b) |
| R10/R11/R12 Technician | – | – | R(o) | RU(o) | CR(o jobs) | R(o jobs) |

### 3.5 Pillar E — Intelligence & Platform

| Role | M25 BID | M26 AIM | M27 CCE | M28 IPF | M29 SEC | M30 ADM |
|---|---|---|---|---|---|---|
| R01 CEO | R(a) | – | – | – | – | – |
| R02 CTO | R(a) | CRUDA(a) | R(a) | CRUDA(a) | CRUDA(a) | CRUDA(a) |
| R33 IT Administrator | RU(a) | R(a) | RU(a) | CRUDA(a) | CRUDA(a) | CRUDA(a) |
| R34 Contact Centre Agent | R(own metrics) | – | CRU(own conversations) | – | – | – |
| R35 CC Supervisor | R(team) | – | CRUDA(team) | – | – | – |
| R05 Operations Director | R(a) | R(a) | R(a) | – | – | – |
| R06 Branch Manager | R(b) | – | R(b) | – | – | R(b config) |
| All other internal roles | R(role-scoped) | – | R(own) | – | – | – |

---

## 4. Data Isolation Tiers

| Tier | Rule | Enforced By |
|---|---|---|
| **T0 — Global** | Visible to all authenticated internal users | No record rule |
| **T1 — Entity** | Visible within the legal entity | `company_id` rule |
| **T2 — Branch** | Visible within the operating unit | `operating_unit_id` rule |
| **T3 — Zone** | Visible within the dispatch zone | `zone_id` rule |
| **T4 — Own record** | Visible only to the owner or assignee | `partner_id` / `user_id` rule |
| **T5 — Restricted** | Explicit grant only, access logged, step-up authentication | Named allow-list + audit |

### Objects by Tier

| Tier | Objects |
|---|---|
| T0 | Service catalogue, parts catalogue, brand and model master, checklist templates, knowledge base, branch directory |
| T1 | Chart of accounts, tax configuration, payroll structures, entity policies |
| T2 | Service orders, work orders, inventory, cash, branch HR, queue, local documents |
| T3 | Technician schedules, van stock, dispatch assignments, route plans |
| T4 | Customer's own orders and invoices; technician's own jobs and earnings; seller's own listings and payouts; vendor's own POs |
| T5 | Individual payroll, NID records, bank details, data-recovery case content, call recordings, audit logs, biometric templates, seller KYC documents |

---

## 5. Field-Level Permissions

Fields visible only to the roles listed.

| Field | Object | Visible To |
|---|---|---|
| `unit_cost`, `total_cost`, `margin` | Estimate, quotation, service order | R01–R05, R06, R17, R21, R22, R26, R27 |
| `salary`, `allowances`, `deductions` | Employee, payslip | R03, R26, R30, R31, own employee |
| `nid_number` | Identity document | R26, R27, R30, R31, R33 (with justification), R38 compliance |
| `bank_account` | Party, employee | R03, R26, R27, R30 |
| `recovered_data_index` | Data case | R14 (case-assigned only), R02 with approval |
| `call_recording_url` | Call record | R35, R32, R02 (audit) |
| `commission_rate` | Commission scheme | R03, R04, R24, R26 |
| `seller_kyc_document` | Marketplace seller | R24, R26, R32 |
| `technician_incentive_detail` | Incentive calculation | R30, R31, own technician, R06 (own branch, summary only) |
| `customer_credit_limit` | Credit profile | R03, R21, R22, R26, R27 |
| `internal_note` | Any object | Internal roles only; never exposed to any external portal |
| `vendor_price` | Vendor price list | R17, R19, R26, R27 |
| `model_confidence`, `model_features` | ML prediction log | R02, R33, model owners |

---

## 6. Segregation of Duties

Combinations that must never be held by the same user.

| # | Incompatible Duties | Risk | Enforcement |
|---|---|---|---|
| SOD-01 | Create vendor + approve vendor invoice | Fictitious vendor payment | Hard block |
| SOD-02 | Raise purchase order + receive goods + approve invoice | Purchase fraud | Hard block (any two permitted, not all three) |
| SOD-03 | Process payroll + approve payroll | Payroll fraud | Hard block |
| SOD-04 | Create credit note + approve credit note | Revenue leakage | Hard block |
| SOD-05 | Adjust inventory + perform the count that justifies it | Inventory theft concealment | Hard block |
| SOD-06 | Approve marketplace seller + approve their payout | Collusion | Hard block |
| SOD-07 | Repair a device + perform its independent QC | Quality concealment | Hard block above value threshold |
| SOD-08 | Create customer + approve their credit limit | Credit fraud | Warning + approval |
| SOD-09 | Administer users + approve access requests for self | Privilege escalation | Hard block |
| SOD-10 | Value a trade-in + purchase it + resell it | Asset misappropriation | Hard block |
| SOD-11 | Raise a warranty claim + approve its write-off | Claim manipulation | Hard block |
| SOD-12 | Handle cash + reconcile the cash book | Cash misappropriation | Hard block |

**Enforcement:** the permission engine evaluates SoD rules at role assignment and blocks
incompatible combinations. Exceptions require CFO or CTO approval, are time-boxed, and appear
on a standing exception report reviewed quarterly.

---

## 7. Approval Authority Matrix

| Transaction | Threshold | Approver |
|---|---|---|
| Repair estimate | Any | Customer |
| Repair estimate | > BDT 5,000 | Customer + system record |
| Repair estimate | > BDT 25,000 | Customer + Branch Manager |
| Repair estimate | > BDT 100,000 | Customer + Operations Director |
| Discount | ≤ 10% | Service Centre Agent |
| Discount | ≤ 20% | Branch Manager |
| Discount | ≤ 35% | Sales Manager |
| Discount | > 35% | CCO |
| Purchase requisition | ≤ BDT 50,000 | Inventory Manager |
| Purchase requisition | ≤ BDT 500,000 | Procurement Manager |
| Purchase requisition | ≤ BDT 2,000,000 | CFO |
| Purchase requisition | > BDT 2,000,000 | CEO |
| Credit note | ≤ BDT 10,000 | Finance Officer |
| Credit note | > BDT 10,000 | Finance Manager |
| Inventory write-off | ≤ BDT 25,000 | Inventory Manager |
| Inventory write-off | > BDT 25,000 | CFO |
| Contract — standard terms | Any value | Sales Manager |
| Contract — non-standard terms | Any value | CCO + CFO |
| Marketplace seller approval | Any | Marketplace Operations Officer |
| Marketplace seller payout | Standard | Automatic on schedule |
| Marketplace seller payout | Held / disputed | Finance Manager |
| Trade-in offer | ≤ BDT 30,000 | Retail Officer |
| Trade-in offer | > BDT 30,000 | Retail Manager + Finance |
| Payroll run | Any | HR Manager + CFO |
| Data destruction | Any | Data Services Technician + witness |
| Access request — standard role | Any | Line Manager |
| Access request — privileged role | Any | Line Manager + IT Administrator + CTO |
| SoD exception | Any | CFO or CTO, time-boxed |

---

## 8. External Party Access Rules

| Rule | Detail |
|---|---|
| EA-01 | An external party may see only records where they are a named party |
| EA-02 | An external party never sees cost, margin, internal notes or other parties' data |
| EA-03 | Corporate portal users see only their own company's data, further scoped by their role in that company |
| EA-04 | A marketplace seller sees the customer's name, contact and address only for a job they have been awarded, and only until a defined period after completion |
| EA-05 | A brand partner sees only claims and service data relating to their own brand |
| EA-06 | A vendor sees only their own purchase orders, receipts and invoices |
| EA-07 | A courier partner sees only consignments assigned to them, with the minimum data needed to deliver |
| EA-08 | External sessions time out after 30 minutes of inactivity |
| EA-09 | MFA is mandatory for any external action with financial consequence |
| EA-10 | Every external access to customer personal data is logged and reportable |
| EA-11 | External API access is scoped by credential; scope cannot be widened by request parameters |
| EA-12 | Bulk export by external parties is limited, rate-controlled and logged |

---

## 9. Access Lifecycle

| Stage | Trigger | Action |
|---|---|---|
| **Provision** | `employee.joined` event from M21 | Identity created; role assigned from the position profile; portal access granted; welcome and training assigned |
| **Modify** | Transfer, promotion or role change | Old permissions revoked and new granted on the effective date; no accumulation |
| **Elevate** | Approved access request | Time-boxed elevation with automatic expiry and session recording |
| **Review** | Quarterly | Manager confirms or revokes each report's access; unconfirmed access is revoked |
| **Suspend** | Leave of absence, investigation | Access disabled but records preserved |
| **Deprovision** | `employee.left` event from M21 | All access revoked within 1 hour; devices deregistered; delegated authority reassigned |
| **External expiry** | Agreement or registration expiry | External access automatically disabled; data retained per retention schedule |

**Control:** zero orphaned accounts beyond 24 hours after a leaver event. Measured weekly.

---

## 10. Role Definition-of-Done

A role is not released until:

| # | Criterion |
|---|---|
| 1 | Permission set defined for every module the role touches |
| 2 | Record rules defined for the correct isolation tier |
| 3 | Field-level restrictions applied and tested |
| 4 | SoD conflicts evaluated and resolved |
| 5 | Portal access configured and tested |
| 6 | Negative tests prove the role cannot see or do what it must not |
| 7 | Training material exists in Bengali and English for the role |
| 8 | A named business owner has signed off the definition |

---

*Next document: `15_Business_Rules_and_Automation_Catalog.md`*
