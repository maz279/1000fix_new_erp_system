---
id: FIX-ERP2-015
title: Business Rules & Automation Catalog
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Business Rules & Automation Catalog

---

## 1. How Rules Are Implemented

| # | Standard | Detail |
|---|---|---|
| BR-STD-01 | Rules are enforced at the model layer, never only in the user interface | A rule bypassed by an API call is not a rule |
| BR-STD-02 | Every rule has an identifier, an owner and a test | Rules without tests are not released |
| BR-STD-03 | Thresholds are configuration, not code | Values change without a deployment |
| BR-STD-04 | Every rule violation produces a message stating what is wrong and what to do | In the user's language |
| BR-STD-05 | Hard rules block; soft rules warn and log | Classification is explicit per rule |
| BR-STD-06 | Overrides are possible only where designed, and always logged with a reason and an approver | No silent overrides |
| BR-STD-07 | Rules are versioned; changing one requires the owner's approval | Audit of what was in force when |

**Rule classification**

| Class | Behaviour |
|---|---|
| **H** — Hard | Blocks the transaction. No override. |
| **A** — Approved override | Blocks, but a named role may override with a recorded reason. |
| **S** — Soft | Warns and logs; the user may proceed. |
| **C** — Computed | Automatically derives a value; not user-overridable. |

---

## 2. Service & Repair Rules (M01)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-SRM-01 | A service order cannot be created without an identified device; if the device is not registered, it must be registered as part of intake | H | Ops Director |
| BRU-SRM-02 | A warranty-type order can only be created if the device's warranty is active at the date of the service request | H | Warranty Officer |
| BRU-SRM-03 | An AMC-type order can only be created if the device appears on an active contract's covered-asset list | H | Account Manager |
| BRU-SRM-04 | A service order cannot reach Completed unless its quality checklist is recorded as passed | H | Quality Manager |
| BRU-SRM-05 | An invoice cannot be raised for a service order that is not Completed | H | Finance Manager |
| BRU-SRM-06 | A new order for the same device and fault category within 30 days is automatically flagged as rework and linked to the original | C | Quality Manager |
| BRU-SRM-07 | Repair estimates above BDT 5,000 require documented customer approval before work begins | H | Ops Director |
| BRU-SRM-08 | Repair estimates above BDT 25,000 require customer approval and branch manager approval | H | Ops Director |
| BRU-SRM-09 | A service order cannot be assigned to a technician lacking a current certification for that brand's warranty work | H | Quality Manager |
| BRU-SRM-10 | Privilege Gold and Diamond members automatically receive priority-1 SLA regardless of service type | C | CCO |
| BRU-SRM-11 | Parts cannot be issued against an unapproved paid repair | H | Inventory Manager |
| BRU-SRM-12 | A device declared beyond economic repair requires photographic evidence and a second technician's confirmation | H | Ops Director |
| BRU-SRM-13 | An estimate expires at its stated validity; expired estimates require re-issue, not extension | H | CCO |
| BRU-SRM-14 | Level 3 board-level repairs may be performed only at a workshop with the required equipment and by a certified specialist | H | Ops Director |
| BRU-SRM-15 | The SLA clock is suspended only by an approved hold reason and resumes automatically when the hold is released | C | Ops Director |
| BRU-SRM-16 | A device uncollected 30 days after Ready enters the abandonment process with statutory notice | C | Branch Manager |
| BRU-SRM-17 | Before/after photographs are mandatory on every warranty job; the job cannot be closed without them | H | Warranty Officer |
| BRU-SRM-18 | Independent QC by a second person is mandatory for repairs above BDT 25,000 | H | Quality Manager |
| BRU-SRM-19 | A closed order may be reopened only within the repair warranty period, and reopening links it as rework | A | Branch Manager |
| BRU-SRM-20 | Customer data-access notes (passwords, unlock codes) are captured only with explicit consent and are purged at handover | H | Quality Manager |

---

## 3. Field Service & Dispatch Rules (M02)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-FSM-01 | A technician on leave, off-shift or already at capacity is never offered as a candidate | H | Dispatch Manager |
| BRU-FSM-02 | Assignment requires a skill match to the required competency for the job | H | Quality Manager |
| BRU-FSM-03 | An automatic assignment is made only when the top candidate's score exceeds the configured confidence threshold | C | Ops Director |
| BRU-FSM-04 | Every dispatcher override of an automatic recommendation requires a reason code | H | Ops Director |
| BRU-FSM-05 | GPS capture occurs only during working hours and while on duty | H | HR Director |
| BRU-FSM-06 | A job cannot be marked Arrived outside the customer's geofence without an exception reason | A | Dispatch Manager |
| BRU-FSM-07 | On-site payment must be reconciled to the branch cash book by the end of the technician's shift | H | Finance Manager |
| BRU-FSM-08 | Van stock cannot exceed the configured maximum per item per technician | H | Inventory Manager |
| BRU-FSM-09 | A failed visit requires geotagged evidence before it can be recorded | H | Ops Director |
| BRU-FSM-10 | Scheduling that would breach working-time limits requires approved overtime first | H | HR Director |
| BRU-FSM-11 | Emergency job insertion may displace lower-priority jobs but never an SLA-critical job already at risk | C | Dispatch Manager |
| BRU-FSM-12 | A marketplace seller may be offered a job only if their score, certification and category access all qualify | H | Marketplace Operations |

---

## 4. Logistics Rules (M03)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-LOG-01 | No custody transfer without a scan and an identity capture from both parties | H | Logistics Manager |
| BRU-LOG-02 | A consignment cannot be closed without proof of delivery | H | Logistics Manager |
| BRU-LOG-03 | Consignments above the declared-value threshold require dual signature and insurance flagging | H | CFO |
| BRU-LOG-04 | Any seal break or weight discrepancy automatically raises an incident and blocks onward movement pending review | H | Logistics Manager |
| BRU-LOG-05 | Restricted items (lithium batteries, refrigerant) may only be carried by a rider or courier certified for them | H | Quality Manager |
| BRU-LOG-06 | Cash collected on delivery is reconciled per rider per shift with zero tolerance for unexplained variance | H | Finance Manager |
| BRU-LOG-07 | Logistics charges are waived automatically where contract, warranty or Privilege tier entitles the customer | C | CCO |
| BRU-LOG-08 | Failed delivery is re-attempted per policy, then returned to origin with charge rules applied | C | Logistics Manager |

---

## 5. Contract & Warranty Rules (M08, M09)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-CTR-01 | A contract cannot be activated without at least one covered asset or seat, defined entitlements, a billing frequency and approval | H | CCO |
| BRU-CTR-02 | Service delivered outside contract scope is billed separately and never silently absorbed | H | Finance Manager |
| BRU-CTR-03 | On contract expiry, all future scheduled work orders are cancelled and the customer is notified | C | Account Manager |
| BRU-CTR-04 | Entitlement over-consumption is blocked or flagged for billing per the contract's configuration; it is never invisible | H | Finance Manager |
| BRU-CTR-05 | Contract suspension for non-payment follows the defined notice sequence; it cannot be applied without it | H | CFO |
| BRU-CTR-06 | RAMC package price is derived from the number and type of registered appliances, never a flat fee | C | CCO |
| BRU-CTR-07 | Healthcare equipment contracts require calibration scheduling as a mandatory contract element | H | Quality Manager |
| BRU-CTR-08 | Service credits are calculated automatically from measured SLA breach; manual credits require CFO approval | C/A | CFO |
| BRU-WTY-01 | A warranty claim cannot be submitted without: a completed work order, device serial, at least one before-photo, a technician diagnosis, and the replaced-parts list | H | Warranty Officer |
| BRU-WTY-02 | A warranty claim is auto-created and queued within 24 hours of a warranty work order closing | C | Warranty Officer |
| BRU-WTY-03 | Duplicate claims for the same serial and fault within 90 days are blocked | H | Warranty Officer |
| BRU-WTY-04 | Brand-supplied warranty parts cannot be consumed on non-warranty jobs | H | Inventory Manager |
| BRU-WTY-05 | Claims to brand partners are valued in the agreed currency at the rate prevailing on the service completion date | C | Finance Manager |
| BRU-WTY-06 | Privilege discounts apply to labour only — never to parts, consumables or transport | C | CCO |
| BRU-WTY-07 | A warranty product cannot be sold on a device that fails the eligibility assessment | H | CCO |
| BRU-WTY-08 | A warranty claim not submitted within the brand's stated window is escalated as revenue leakage before it expires | C | Finance Director |

---

## 6. Inventory & Procurement Rules (M15, M16)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-INV-01 | Stock cannot be issued against an unapproved paid repair | H | Inventory Manager |
| BRU-INV-02 | Inter-branch transfer requires the source branch manager's approval and the destination's confirmed receipt | H | Inventory Manager |
| BRU-INV-03 | A purchase order cannot be raised for an item whose network-wide stock already exceeds the maximum level | A | Procurement Manager |
| BRU-INV-04 | Brand consignment stock is excluded from own-stock valuation and reported separately | C | CFO |
| BRU-INV-05 | Expired shelf-life stock cannot be issued | H | Inventory Manager |
| BRU-INV-06 | Stock adjustments above threshold require approval with a reason code | H | CFO |
| BRU-INV-07 | Goods failing inspection go to quarantine and never to available stock | H | Quality Manager |
| BRU-INV-08 | Serialised parts must have their serial captured at both receipt and issue | H | Inventory Manager |
| BRU-SCM-01 | A vendor invoice cannot be approved for payment without a matched purchase order and goods receipt within tolerance | H | Finance Manager |
| BRU-SCM-02 | A purchase order cannot be issued to a vendor who is not active and approved | H | Procurement Manager |
| BRU-SCM-03 | The same user cannot create a vendor and approve that vendor's invoice | H | CFO |
| BRU-SCM-04 | Import landed cost must be allocated before the received stock can be valued as final | C | Finance Manager |
| BRU-SCM-05 | Sub-contracted devices must move under a logistics consignment with full custody evidence | H | Ops Director |

---

## 7. Financial Rules (M19, M20)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-FIN-01 | Every customer invoice includes VAT at the applicable rate and displays the Company's BIN | H | CFO |
| BRU-FIN-02 | Cash receipts above BDT 50,000 require the customer's NID to be recorded | H | CFO |
| BRU-FIN-03 | A payment cannot be recorded against a cancelled invoice | H | Finance Manager |
| BRU-FIN-04 | A credit note requires approval by the Finance Manager or above | H | CFO |
| BRU-FIN-05 | A financial period cannot be closed while unposted entries exist in it | H | CFO |
| BRU-FIN-06 | Once a period is hard-closed, no posting to it is possible without CFO-approved reopening, which is logged | H | CFO |
| BRU-FIN-07 | Foreign-currency balances are revalued at period end at the official rate | C | Finance Manager |
| BRU-FIN-08 | Marketplace transactions are accounted per the declared principal-or-agent model; the model cannot vary by transaction | H | CFO |
| BRU-FIN-09 | TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise | H | CFO |
| BRU-FIN-10 | Branch cash must be reconciled and closed daily; an unclosed shift blocks the next shift's opening | H | Finance Manager |
| BRU-BIL-01 | An invoice is generated automatically on job closure; manual invoice creation for a completed job requires approval | C/A | Finance Manager |
| BRU-BIL-02 | Subscription billing runs on the contract's cycle; a missed cycle raises an exception, never a silent skip | H | Finance Manager |
| BRU-BIL-03 | A seller payout is held for the configured period after job completion and blocked entirely while a dispute is open | H | CFO |
| BRU-BIL-04 | Commission is reversed automatically when the underlying transaction is refunded or a dispute is decided against the seller | C | Finance Manager |
| BRU-BIL-05 | Refunds are issued to the original payment method unless the customer accepts store credit | C | Finance Manager |
| BRU-BIL-06 | Deferred revenue is released only per the recognition schedule; manual release requires CFO approval | H | CFO |
| BRU-BIL-07 | A consolidated corporate invoice cannot be issued until every constituent job is Completed and priced | H | Finance Manager |

---

## 8. Marketplace Rules (M12)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-ECM-01 | A seller cannot transact until documents are verified, the agreement is digitally signed, and an administrator has approved | H | Marketplace Operations |
| BRU-ECM-02 | Only customers with a completed transaction may leave a review | H | Marketplace Operations |
| BRU-ECM-03 | Marketplace jobs are held to the same evidence, QC and warranty standards as owned jobs | H | Quality Manager |
| BRU-ECM-04 | A seller whose performance score falls below threshold has visibility reduced automatically; below the suspension threshold they are suspended | C | Marketplace Operations |
| BRU-ECM-05 | Seller access to customer contact data is limited to awarded jobs and expires a defined period after completion | H | CTO |
| BRU-ECM-06 | Paid boost and advertising never override the disclosure that a listing is promoted | H | CCO |
| BRU-ECM-07 | A seller cannot list in a category for which they hold no verified qualification | H | Marketplace Operations |
| BRU-ECM-08 | Registration expiry automatically suspends the seller until renewed | C | Marketplace Operations |
| BRU-ECM-09 | Disputes are decided by 1000FiX, not by the parties; the decision and its evidence are recorded | H | Marketplace Operations |
| BRU-ECM-10 | Stock cannot be sold below available quantity; out-of-stock items cannot be ordered | H | Inventory Manager |

---

## 9. Rental, Refurbishment & E-Waste Rules (M13, M14, M18)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-RNT-01 | A rental asset cannot be dispatched without a completed pre-dispatch condition report | H | Retail Manager |
| BRU-RNT-02 | A rental agreement requires a signed condition report and the deposit received before handover | H | Finance Manager |
| BRU-RNT-03 | Damage charges are derived from the difference between outbound and inbound condition reports; discretionary charges require approval | C/A | Retail Manager |
| BRU-RNT-04 | A returned rental asset re-enters the available pool only after cleaning, servicing and functional test | H | Retail Manager |
| BRU-RNT-05 | Overdue rentals accrue charges automatically per the tariff with escalating notification | C | Finance Manager |
| BRU-TRF-01 | No trade-in device proceeds to refurbishment or resale without a certified data destruction record | H | Quality Manager |
| BRU-TRF-02 | Provenance and identity checks (including stolen-device screening where available) must pass before a trade-in offer is paid | H | Retail Manager |
| BRU-TRF-03 | A refurbished unit cannot be listed for sale without a completed QA test protocol and an assigned grade | H | Quality Manager |
| BRU-TRF-04 | Battery health and known defects must be disclosed on every refurbished listing | H | CCO |
| BRU-TRF-05 | A supervisor grade override requires a recorded justification | A | Quality Manager |
| BRU-ESG-01 | No device may leave for recycling without a certified wipe or physical destruction record | H | Quality Manager |
| BRU-ESG-02 | E-waste may be transferred only to a partner whose certification is current at the transfer date | H | Quality Manager |
| BRU-ESG-03 | Every recycled unit must have a retrievable disposal certificate | H | Quality Manager |
| BRU-ESG-04 | Hazardous items follow their specific handling, storage and transport rules without exception | H | Quality Manager |

---

## 10. HR, Competency & Quality Rules (M21, M22, M23)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-HRM-01 | A technician cannot be assigned brand warranty work once their certification for that brand has expired | H | Quality Manager |
| BRU-HRM-02 | Overtime must be pre-approved by the line manager before it counts for payroll | H | HR Director |
| BRU-HRM-03 | Performance incentive is calculated only after the minimum monthly job threshold is met | C | HR Director |
| BRU-HRM-04 | Leave cannot be approved where it would take team coverage below the configured minimum | A | HR Director |
| BRU-HRM-05 | Payroll cannot be finalised until attendance for the period is verified and locked | H | HR Director |
| BRU-HRM-06 | Payroll requires two approvals — HR Manager and CFO | H | CFO |
| BRU-HRM-07 | An employee's own payroll record is visible to them and to HR/finance, never to peers or line managers below HR Manager | H | HR Director |
| BRU-LMS-01 | Mandatory training must be completed within the assigned deadline; overdue mandatory training restricts the affected work types | H | Quality Manager |
| BRU-LMS-02 | A marketplace engineer cannot be activated in a category without passing that category's qualification | H | Marketplace Operations |
| BRU-QMS-01 | A quality checklist cannot be marked complete with unanswered mandatory items | H | Quality Manager |
| BRU-QMS-02 | Every non-conformance requires a root cause and a CAPA before it can be closed | H | Quality Manager |
| BRU-QMS-03 | A CAPA cannot be closed without effectiveness verification after the defined interval | H | Quality Manager |
| BRU-QMS-04 | A complaint cannot be closed without confirming the outcome with the customer | H | Quality Manager |
| BRU-QMS-05 | Repeated non-conformance in the same process triggers a mandatory management review item | C | Quality Manager |

---

## 11. Security, Data & Platform Rules (M06, M24, M29, M30)

| ID | Rule | Class | Owner |
|---|---|---|---|
| BRU-SEC-01 | Admin, finance and HR portal access requires MFA at every login | H | CTO |
| BRU-SEC-02 | Sensitive actions (payouts, payroll finalisation, data-case access, bulk export) require step-up authentication | H | CTO |
| BRU-SEC-03 | Access to a data-recovery case is limited to the assigned team; every access is logged | H | CTO |
| BRU-SEC-04 | Recovered customer data is purged at the agreed date unless a documented hold applies | H | CTO |
| BRU-SEC-05 | Personal data cannot be exported in bulk without approval, and every export is logged | H | CTO |
| BRU-SEC-06 | A leaver's access is revoked within one hour of the leaver event | H | HR Director / CTO |
| BRU-SEC-07 | Incompatible duty combinations cannot be assigned; exceptions are time-boxed and reported | H | CFO / CTO |
| BRU-SEC-08 | Production data used in non-production environments must be masked | H | CTO |
| BRU-DMS-01 | Documents cannot be deleted before their retention period expires | H | Quality Manager |
| BRU-DMS-02 | Documents under legal hold cannot be disposed of regardless of retention | H | Quality Manager |
| BRU-DMS-03 | A signed document cannot be modified; changes require a new version and a new signature | H | Quality Manager |
| BRU-ADM-01 | Master data changes above the defined significance require approval before taking effect | H | CTO |
| BRU-ADM-02 | Configuration changes in production must be traceable to an approved change record | H | CTO |
| BRU-AIM-01 | A model recommendation with material customer or financial impact requires human confirmation | H | CTO |
| BRU-AIM-02 | No model output may cross a defined business guard rail (price floor/ceiling, certification requirement, safety rule) | H | CTO |
| BRU-AIM-03 | Recovered customer data (M06) is never used as training data | H | CTO |

---

## 12. Automation Catalogue

Automations are the system acting without a human. Each has a trigger, an action, a failure
behaviour and an owner. Target: **85% of routine operational work automated by Wave 8.**

### 12.1 Service Delivery Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-001 | Booking received on any channel | Create service order, evaluate entitlement, assign SLA, acknowledge to customer, enter dispatch queue | Queue for manual creation; alert |
| AUT-002 | Order enters dispatch queue | Score candidates; auto-assign above confidence or present ranked list | Present list to dispatcher |
| AUT-003 | Technician assigned | Notify technician and customer; publish tracking link; update route | Manual notification task |
| AUT-004 | Diagnosis completed | Draft estimate from fault code and standard repair mapping | Blank estimate for manual build |
| AUT-005 | Estimate issued | Send on preferred channels; start expiry timer; remind at 24h and 48h; expire on limit | Manual follow-up task |
| AUT-006 | Customer approves | Reserve parts, release work order, notify technician | Manual release task |
| AUT-007 | Parts unavailable | Search network; recommend source; raise transfer or purchase; hold job; inform customer with revised ETA | Escalate to inventory manager |
| AUT-008 | QC passed | Generate service report, raise invoice, notify customer as Ready | Manual invoice task |
| AUT-009 | SLA at 50/75/90/100% | Escalate to defined roles with acknowledgement tracking | Repeat and escalate further |
| AUT-010 | Job completed | Trigger CSAT survey after the configured delay | Retry once, then drop |
| AUT-011 | Same device + fault within 30 days | Flag rework, link records, notify quality and the original technician's manager | — |
| AUT-012 | Device ready and uncollected | Reminder sequence at 3, 7, 15 and 30 days; then abandonment process | — |
| AUT-013 | Nightly 05:00 | Optimise all routes for the next day; publish; notify technicians | Retain previous manual sequence |
| AUT-014 | Technician syncs offline work | Reconcile parts, time and evidence; release downstream actions | Flag conflicts for review |

### 12.2 Commercial & Revenue Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-015 | Contract expiry − 90/60/30/15 days | Notify customer and account owner; generate renewal quotation at 60 days | Manual renewal task |
| AUT-016 | Contract activated | Generate the full preventive-maintenance schedule for the term | Manual scheduling task |
| AUT-017 | Preventive visit due − lead time | Create the work order and enter the dispatch queue | Alert account manager |
| AUT-018 | Warranty job closed | Create claim, assemble evidence pack, validate completeness, queue for submission | Manual claim task with checklist |
| AUT-019 | Claim validated | Submit to the brand in their required format | Route to manual submission queue |
| AUT-020 | Brand response received | Update claim; on approval queue for billing; on rejection open a dispute task | Manual review queue |
| AUT-021 | Brand remittance received | Match to claims; post to ledger; flag unmatched | Manual matching queue |
| AUT-022 | Invoice issued | Deliver on preferred channels with payment link | Retry; then manual delivery task |
| AUT-023 | Invoice unpaid at 7/14/21/30 days | Execute the dunning sequence; at 30 days enter the collections queue | — |
| AUT-024 | Payment received | Match to invoice; mark paid; post to ledger; receipt to customer | Manual matching queue |
| AUT-025 | Subscription cycle due | Generate the invoice with proration and usage | Alert finance |
| AUT-026 | Marketplace job completed and hold period elapsed | Accrue commission; add to the next payout run | Hold and alert |
| AUT-027 | Payout run scheduled | Calculate, produce statements, generate the disbursement file, request approval | Alert finance |
| AUT-028 | Refund approved | Execute through the original method; post; notify customer | Manual refund task |
| AUT-029 | Customer registers | Award registration points; send welcome journey; set preferences | Retry |
| AUT-030 | Referral converts | Credit both parties; notify; accrue partner commission | Manual credit task |

### 12.3 Supply Chain Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-031 | Stock reaches reorder point | Alert; draft purchase requisition with recommended quantity | Alert only |
| AUT-032 | Requisition approved | Generate and transmit the purchase order; track acknowledgement | Manual PO task |
| AUT-033 | Goods received and inspected | Update stock; allocate landed cost; trigger three-way match | Manual posting task |
| AUT-034 | Three-way match successful | Route the vendor invoice to the payment schedule | Exception queue |
| AUT-035 | Technician shift ends | Reconcile van stock; report variance to branch manager | Alert |
| AUT-036 | Cycle count due | Generate the count task list by ABC class and location | Alert inventory manager |
| AUT-037 | Dead stock threshold reached | Produce a disposition recommendation | — |
| AUT-038 | Asset telemetry breaches threshold | Raise an alert; correlate; open a ticket if the rule requires | Alert only |
| AUT-039 | Predicted failure above confidence | Notify account manager; propose a proactive service booking | — |
| AUT-040 | E-waste item triaged for recycling | Verify a destruction certificate exists; batch for transfer | Block and alert |

### 12.4 People, Finance & Governance Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-041 | Certification expiry − 90/60/30/15 days | Notify technician, manager and HR; schedule re-certification | Escalate |
| AUT-042 | Certification expires | Remove the technician from that brand's warranty dispatch pool | — |
| AUT-043 | Month end | Run close checklist, accruals, prepayment amortisation, FX revaluation, recurring journals | Alert finance |
| AUT-044 | Bank statement imported | Auto-match; present only exceptions | Full manual reconciliation |
| AUT-045 | Payroll period locked | Calculate payroll, incentives and tax; present for approval | Alert HR |
| AUT-046 | Payroll approved | Generate the BEFTN file, distribute payslips, post to ledger | Alert finance |
| AUT-047 | Employee joins | Create identity, assign role from position profile, grant portal access, assign onboarding and mandatory training | Manual provisioning task |
| AUT-048 | Employee leaves | Revoke all access within one hour; deregister devices; reassign delegated authority; trigger clearance | Immediate escalation |
| AUT-049 | Quality event (rework, failed QC, complaint) | Raise a non-conformance; route to the process owner | Alert quality manager |
| AUT-050 | CAPA due date + verification interval | Prompt effectiveness verification; reopen if not verified | Escalate |
| AUT-051 | Document reaches end of retention | Present for disposal review unless under legal hold | Hold and alert |
| AUT-052 | Access certification cycle due | Issue review tasks to all managers; revoke unconfirmed access at the deadline | Escalate to CTO |

### 12.5 Platform Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-053 | Integration error rate above threshold | Alert the owner; open the circuit breaker; activate the documented fallback | Escalate |
| AUT-054 | Event in dead letter > 1 hour | Alert; create a triage task | Escalate |
| AUT-055 | Backup completes | Verify integrity; report; alert on failure | Immediate escalation |
| AUT-056 | Scheduled restore test due | Execute; verify; record evidence | Escalate |
| AUT-057 | Model drift detected | Alert the model owner; schedule retraining; continue with the current model | Fall back to rules |
| AUT-058 | Security anomaly detected | Alert; if severity warrants, suspend the session and require re-authentication | Escalate |
| AUT-059 | Data quality test fails | Block the dependent dashboard refresh; alert the data owner | Show last-known-good with a staleness warning |
| AUT-060 | Certificate or credential expiry − 30 days | Alert the owner; create a rotation task | Escalate at 7 days |

---

## 13. Automation Coverage Targets

| Process | Manual Today | Automated Target | Wave |
|---|---|---|---|
| Service order creation | 100% manual | 90% automatic from digital channels | W2 |
| Technician assignment | 100% manual | 70% automatic | W6 |
| Route planning | Not done | 100% automatic | W2 |
| Customer status notification | Manual on request | 100% automatic | W1 |
| Invoice generation | 100% manual | 100% automatic | W3 |
| Payment matching | 100% manual | 94% automatic | W3 |
| Warranty claim creation | 100% manual | 100% automatic | W4 |
| Warranty claim submission | 100% manual | 85% automatic | W4 |
| Replenishment ordering | 100% manual | 80% automatic | W3 |
| Contract renewal outreach | 100% manual | 100% automatic | W4 |
| Preventive work order creation | 100% manual | 100% automatic | W4 |
| Payroll calculation | 100% manual | 100% automatic | W5 |
| Commission and payout calculation | Not done | 100% automatic | W7 |
| VAT return preparation | 100% manual | 100% automatic | W4 |
| Management reporting | 100% manual | 100% automatic | W8 |
| Access provisioning and revocation | 100% manual | 100% automatic | W1 |
| **Overall routine operational work** | **~20%** | **85%** | **W8** |

---

*Next document: `16_NonFunctional_Requirements_and_Architecture_Standards.md`*
