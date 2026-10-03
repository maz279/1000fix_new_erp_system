---
id: FIX-ERP2-M20
module_id: M20
module_code: ARB
module_name: Accounts Receivable, Invoicing & Collections
category: G — Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P0
wave: W3
---

# M20 — Accounts Receivable, Invoicing & Collections
### Category G · Code `ARB` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M20 |
| **Module code** | `ARB` *(supersedes the retired `BIL` code — see `02-02` §5)* |
| **Category** | G — Finance & Treasury |
| **Status** | Existing (re-scoped in v2.1 — recurring billing schedules moved to M39, revenue recognition and settlement to M53, tax determination to M51, receipt banking to M50, pricing to M11) |
| **Priority** | **P0** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account` (customer invoicing) · L2 OCA `account-invoicing`, `account-payment`, `credit-control`, `account-financial-reporting` · L5 custom invoice orchestration, receipt matching, credit control and dunning |
| **Custom modules** | `cd_billing_engine`, `cd_ar_ext`, `cd_receipt_matching`, `cd_credit_note_refund`, `cd_dunning` |
| **Requirement range** | FR-ARB-001 … FR-ARB-044 |
| **Requirement count** | **44** *(measured — supersedes the 36 estimate in `02-02`)* |
| **Effort estimate** | **24 person-weeks** *(measured — supersedes the 20 PW estimate)* |
| **Depends on** | M19 GL · M33 Party Master · M11 Pricing · M37 Catalogue · M51 Tax · M50 Treasury · M29 Identity · M30 Platform Admin · M28 Integration |
| **Depended on by** | M01, M31, M02, M04, M08, M09, M13, M14, M12, M38, M39, M06, M05, M07, M27, M50, M51, M53, M54, M25, M10, M18, M67 |

---

## 2. Purpose

M20 turns work that has been done into **money the Company is owed, and then into money the
Company has**. It issues the invoice, presents it to the customer, captures the payment,
matches it, chases what is late, and credits what was wrong.

Today an invoice is typed by hand from a paper service form, sent over WhatsApp or email, and
recorded manually when payment arrives — **three to seven days after the job was finished**.
In a business closing roughly 250,000 jobs a year across 51+ branches, that delay is not an
administrative inconvenience; it is a cash-flow structure and a revenue-leakage channel. Work
that is delivered but never invoiced simply disappears, and nobody can say how much of it
there is.

M20's governing commitment is blunt: **every delivered, billable event produces an invoice
automatically, within one hour, without anyone typing anything.** M20 does not decide what to
charge — M11 does that. It does not decide when revenue is earned — M53 does that. It does not
compute the VAT — M51 does that. It takes a billable event, assembles it into a compliant
customer document, delivers it, and pursues it until it is paid or written off under approval.

### Why It Exists

Invoicing sits at the junction of every revenue stream. A repair job, an AMC contract cycle, a
rental period, a marketplace order, a refurbished-device sale, a managed-service month, a data
services engagement and a warranty claim to a brand partner all produce a receivable, and each
arrives in a different shape. Handling that with a manual billing desk means the desk becomes
the constraint on how many revenue streams the business can operate.

Three failures follow from the current state, and M20 exists to close all three:

1. **Revenue leakage** — delivered work that is never billed. Currently unknown and therefore
   unmanaged; the target is < 0.5%.
2. **Cash delay** — three to seven days of invoicing lag on every job, compounded by no
   systematic collection follow-up. Days sales outstanding is not even measured today.
3. **Billing errors** — invoices typed from paper produce disputes, credit notes and lost
   customer confidence. Credit notes as a proportion of invoices is the honest measure of it,
   and the target is < 1.5%.

M20 is P0 and lands in Wave 3 with M19, M52 and M50. It is the module that most directly
converts the operational modules of Waves 1–2 into cash.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-002 | "Automatically generate invoices from completed service orders without manual data entry" |
| ERP BRD BR-FIN-003 | "Generate warranty claim invoices to brand partners with all required documentation attached" |
| ERP BRD BR-FIN-004 | "Support multiple payment methods: cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer" |
| ERP BRD BR-FIN-009 | "Track accounts receivable aging with automated payment reminder workflows" |
| ERP BRD BR-FIN-011 | "Support AMC/RAMC subscription billing with configurable billing cycles" |
| ERP BRD BR-FIN-014 | "Support credit note and refund processing" |
| ERP BRD §Process 6 (As-Is) | "Billing staff manually creates invoice from paper service form → sent via WhatsApp/email/printed → payment received in cash or bank transfer → manually recorded. Pain points: invoice errors; delayed invoicing (often 3–7 days post-service); no automated reminders; cash reconciliation unreliable" |
| ERP BRD §Process 5 (To-Be) Invoice-to-Cash | "Work order closed → auto-generate invoice (labor + parts + VAT) → Mushak VAT invoice → payment link → AR cleared → GL updated" |
| ERP BRD UC-006 | Generate invoice and collect payment; alternate flow A2 — corporate client invoice added to monthly statement |
| ERP BRD Automation A5 | "Invoice auto-generated when work order closed" replaces manual invoice preparation |
| ERP BRD BRU-FIN-01 / 03 / 04 | VAT and BIN on every invoice; no payment against a cancelled invoice; credit note requires Finance Manager approval |
| Business Objective BO-06 | Financial control and reporting, owner CFO |
| Exec Summary §6.2 | Financial close and cash flow benefit **BDT 26 lac per year** (M19 with M20) |
| `_CATEGORY_OVERVIEW.md` §8 | 100% invoices auto-generated · > 97% within 1 hour · DSO < 32 days · credit notes < 1.5% · leakage < 0.5% |
| Company Profile §Payment Options | Multiple payment channels including MFS, cards and bank transfer |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M20 in the v2.0 draft absorbed pricing, subscription
> mechanics, revenue recognition and settlement. All four have moved out and are claimed by the
> modules named below; both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The billable-event intake: receiving, validating and queueing billable events from every operational module |
| 2 | Invoice assembly: lines, quantities, descriptions (English and Bengali), taxes as determined by M51, totals and rounding |
| 3 | Invoice issuance, numbering, sequencing and the statutory Mushak 6.3 rendering supplied by M51 |
| 4 | Proforma invoices, advance/deposit invoices and their application to the final invoice |
| 5 | Consolidated and statement-based invoicing for corporate accounts |
| 6 | Warranty-claim invoicing to brand partners, including the required evidence attachments |
| 7 | Invoice delivery across channels — portal, email, WhatsApp, SMS, print — with delivery confirmation |
| 8 | Receipt capture across all tender types: cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer, cheque, adjustment |
| 9 | Payment links and the customer-initiated payment journey through the gateway |
| 10 | Receipt-to-invoice matching and allocation, including partial, over-, under- and multi-invoice payments |
| 11 | Unapplied receipts, on-account balances and their clearance |
| 12 | The customer open-item ledger: invoices, receipts, credit notes, adjustments and running balance |
| 13 | Ageing analysis by customer, segment, branch, business line and age bucket |
| 14 | Credit control: credit limits, credit terms, credit holds and release authority |
| 15 | Dunning: reminder schedules, escalation ladders, channel selection and suppression rules |
| 16 | Collections case management, promise-to-pay, dispute logging and resolution tracking |
| 17 | Credit notes: request, approval, issuance and application, including the statutory credit-note document |
| 18 | Refunds: authorisation, method selection, execution instruction to M50, and reconciliation |
| 19 | Write-offs and bad-debt provisioning proposals |
| 20 | Customer statements of account, on demand and on schedule |
| 21 | Deposit and retention-money tracking for contract customers |
| 22 | Revenue-leakage detection: delivered-but-unbilled reconciliation against operational modules |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Price determination, rate cards, discount policy, dynamic pricing | **M11** Pricing (Category C) | What to charge is a commercial decision; M20 bills the price it is given |
| Quotation and estimate | **M36** Quotation & Estimation (Category C) | A quote is pre-commitment; an invoice is post-delivery |
| Recurring billing schedule, cycle definition, proration, plan change, dunning of subscriptions' *schedule* | **M39** Subscription & Recurring Billing (Category C) | The schedule is a commercial construct; M39 raises the billable event and M20 issues the resulting invoice (BR-FIN-011 is delivered jointly, with M39 owning the cycle) |
| Product and service definition, SKU, service catalogue | **M37** Catalogue (Category C) | An invoice line references a catalogue item; it does not define one |
| Revenue recognition timing, deferral, performance obligations, contract balances | **M53** Revenue & Settlement | Issuing an invoice and earning revenue are different events; conflating them is the single most common cause of misstatement |
| Commission calculation and seller/partner payouts | **M53** with **M12** | A marketplace payout is a settlement, not a receivable |
| VAT and SD determination, Mushak form definition, VAT registers, TDS/VDS treatment on receipts | **M51** Tax & Regulatory | Tax rules change annually by SRO; they belong in a country pack |
| Bank accounts, deposit banking, gateway settlement reconciliation, cash position | **M50** Treasury & Cash | M20 records that a receipt occurred; M50 proves the money reached the bank |
| Counter cash drawer, shift float, shift close | **M04** Branch Operations | Cash handling happens at the counter |
| Journal posting of revenue, receivable, receipt and provision | **M19** General Ledger | Only Category G's ledger creates journal entries |
| Customer master, contact, segment, party hierarchy | **M33** Party Master | One customer record serves every module |
| Contract terms, SLA, entitlement | **M08** Contract & SLA Management | M20 bills against a contract; it does not author one |
| Warranty claim adjudication, evidence capture, brand approval | **M09** Warranty & Claims | M09 establishes the claim; M20 invoices it |
| Customer conversations, complaints and case handling | **M27** Contact Centre | A billing dispute is logged in M20 and conversed in M27 |
| Loyalty points, vouchers and reward redemption value | **M10** Loyalty & Rewards | M10 computes the entitlement; M20 applies it as an invoice line or credit |
| Collections analytics and predictive payment behaviour | **M26** AI/ML Services | M20 executes the strategy; M26 may propose it |

### 3.3 Shared Concepts

| Concept | M20's Role | Owning Module |
|---|---|---|
| Customer invoice | **Owns** — the defining artefact of this module | M20 |
| Billable event | Consumes; each operational module owns raising it | M20 / M01, M31, M08, M39, M13, M12, M38, M09, M05, M06, M14 |
| Price | Reads the determined price at invoice assembly | M11 |
| Tax on an invoice | Requests determination and renders the result | M51 |
| Mushak 6.3 document | Renders and issues; M51 owns the format, sequence and register | M20 / M51 |
| Receipt | **Owns** the capture and the application | M20 |
| Bank deposit of a receipt | Raises; M50 proves it against the statement | M20 / M50 |
| Gateway transaction | Records the customer-side payment; M50 reconciles the settlement | M20 / M50 |
| Receivable balance | Owns the open-item detail; M19 owns the control account | M20 / M19 |
| Credit limit | **Owns** the enforcement; M07 informs the commercial judgement | M20 / M07 |
| Credit note | **Owns**; M51 supplies the statutory document treatment | M20 / M51 |
| Refund | Owns the authorisation; M50 executes the payment | M20 / M50 |
| Deferred revenue | Raises the invoice that creates it; M53 owns the schedule | M20 / M53 |
| Customer statement | **Owns**; delivered through P01/P04 | M20 |
| Dunning communication | Owns the trigger and content; M27 owns the channel and the conversation record | M20 / M27 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — FI-AR & Billing (SD/BRIM)** | Billing document requests from operational documents, billing due list, collective and periodic billing, dunning procedures with levels and areas, credit management with automatic blocks | **The billing-due-list pattern** — operational modules place billable events into a queue that is processed on a schedule and by exception, rather than each module calling an invoicing API directly. This is what makes 100% auto-invoicing measurable: anything unbilled is visibly sitting in the queue. Also adopted: multi-level dunning procedures with per-level channel, tone and escalation | SAP's convergent-invoicing/BRIM stack for high-volume rating — M39 and M11 cover our rating need at far lower complexity |
| **SAP FSCM — Credit, Collections and Dispute Management** | Credit exposure scoring, collections worklists prioritised by value and risk, formal dispute cases separate from the invoice | **Collections as a prioritised worklist rather than an ageing report**, and **disputes as first-class objects** that suspend dunning on the disputed amount only, not on the whole account. This distinction removes the most common cause of losing a good customer to an aggressive reminder | The full credit-scoring engine; our credit decisions are policy-driven with M07 input |
| **Oracle Fusion Cloud Receivables** | AutoInvoice import from external sources, receipt application with AutoMatch, lockbox processing, revenue-recognition separation, late-charge processing | **The strict separation of *invoicing* from *revenue recognition*** — Oracle keeps them as distinct engines against the same transaction. We adopt it exactly, with M53 as the recognition engine. Also adopted: automated receipt application scoring with a manual exception queue | Oracle's lockbox model (no equivalent in Bangladesh) and late-charge automation (commercially unsuitable for our market) |
| **Microsoft Dynamics 365 Finance — Accounts Receivable** | Free-text and project invoices, settlement of payments against invoices with discounts, collections module, customer ageing snapshots, payment predictions | **Ageing snapshots** — an ageing computed and stored at a point in time rather than always recalculated, so that a historical ageing can be reproduced exactly for audit and for trend analysis | Dynamics' payment-prediction ML in v1; deferred to M26 as an enhancement |
| **NetSuite / Zuora — invoice presentment and payment** | Hosted payment pages, invoice-embedded pay-now links, automated payment retries, customer portal statements | **Payment link on every invoice, on every channel** — this is the highest-leverage feature for a market where the customer has a phone and an MFS wallet in hand at the moment they read the message | Subscription-billing depth — M39's scope |
| **Bangladesh MFS and gateway practice (bKash, Nagad, SSLCOMMERZ)** | Merchant payment APIs, settlement to the merchant's bank on a T+1 to T+3 cycle, gateway-side reconciliation reports | **The two-stage payment model as a first-class design constraint**: the customer's payment and the merchant's settlement are separate events, days apart, and must be reconciled separately. M20 records the customer-side receipt; M50 reconciles the settlement. Modelling this as one event is the classic Bangladeshi ERP failure and produces a permanently unreconciled suspense account | Direct gateway-to-GL posting without an intervening clearing account |
| **NBR VAT & SD Act 2012 / Rules 2016 practice** | Mushak 6.3 tax invoice at the time of supply, sequential numbering, BIN display, 5-year (and Companies Act 7-year) retention | Invoice numbering and sequencing that satisfies statutory continuity; no gaps, no reuse, no post-hoc renumbering | — |
| **Odoo 19 CE `account` + OCA `account-invoicing` / `credit-control` / `account-payment`** | Customer invoices, payment registration and reconciliation, invoice sending, credit-control policies with reminder levels | The transactional substrate. OCA `account_credit_control` supplies the multi-level policy engine behind our dunning ladder; `account_invoice_*` modules supply presentment refinements | Odoo's default single-reminder model and its assumption that the invoice is created by a human |

**Design position.** Five deliberate positions.

First, **the invoice is a consequence, not an action**. No user creates an invoice. Operational
modules declare that something billable happened; M20 assembles and issues. A manually created
invoice is possible but is an exception requiring a reason code, and is reported. This is the
only design under which "100% of invoices auto-generated" is a target rather than a slogan.

Second, **the billable-event queue is the leakage detector**. Because every billable event
enters a visible queue, "delivered but unbilled" stops being an unknowable quantity and becomes
a number on a dashboard with an age. Revenue leakage below 0.5% is achievable only because the
leak is visible while it is happening.

Third, **customer payment and merchant settlement are separate events**. Every non-cash receipt
lands first in a channel clearing account and moves to the bank only when M50 matches the
settlement. The gap is normal and is reported as an ageing, not hidden.

Fourth, **dunning is segmented, not uniform**. A walk-in retail customer three days late, a
corporate account under a 30-day term, and a brand partner settling a warranty claim batch are
three different conversations. One reminder ladder for all three would damage the relationships
that matter most. Ladders are configured per customer segment, with hard suppression rules for
accounts in active dispute or under an agreed payment plan.

Fifth, **a credit note is a control point, not a correction tool**. Credit notes require
approval by someone who did not raise them (SOD-04), carry a mandatory reason taxonomy, and are
measured as a proportion of invoices. A rising credit-note rate is a signal that something
upstream — pricing, job data capture, or expectation setting — is broken, and M20 is where that
signal is generated.

---

## 5. Functional Areas & Features

### 5.1 Billable Event Intake & Invoice Generation

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ARB-001 | Billable event queue | Receive typed billable events from every revenue-producing module into a single queue carrying customer, source document, lines, price, dimensions, currency and due-by time | **P0** | L5 |
| FR-ARB-002 | Automatic invoice generation | Generate and issue a customer invoice from a billable event without manual data entry, within one hour of the event (BR-FIN-002, Automation A5) | **P0** | L5 |
| FR-ARB-003 | Multi-source line assembly | Assemble a single invoice from labour, parts, call-out, freight, discount, loyalty redemption and tax lines originating in different modules | **P0** | L5 |
| FR-ARB-004 | Bilingual invoice content | Render every invoice line description, heading and total in Bengali as well as English, with Bengali numerals where the statutory format requires them | **P0** | L5 |
| FR-ARB-005 | Invoice numbering | Assign gapless, sequential, entity- and document-type-scoped invoice numbers that satisfy statutory continuity, with no reuse and no post-hoc renumbering | **P0** | L1/L5 |
| FR-ARB-006 | Mushak 6.3 issuance | Issue the statutory tax invoice in the NBR-prescribed Mushak 6.3 format, displaying the Company BIN, the customer BIN where applicable, taxable value and VAT, using the format and register owned by M51 (BR-FIN-006, BRU-FIN-01) | **P0** | L5 |
| FR-ARB-007 | Proforma and advance invoice | Issue a proforma or advance/deposit invoice, and apply the advance automatically against the final invoice when it is raised | P1 | L1/L5 |
| FR-ARB-008 | Consolidated corporate invoicing | Consolidate a period's jobs for a corporate account into one invoice or one statement-based invoice, per the account's billing agreement (UC-006 alternate flow A2) | **P0** | L5 |
| FR-ARB-009 | Warranty claim invoice | Generate a brand-partner claim invoice with the required evidence attached — job record, part serials, technician certification, customer acknowledgement — in the brand's required format and currency (BR-FIN-003) | **P0** | L5 |
| FR-ARB-010 | Manual invoice exception | Permit a manually created invoice only with a reason code and an approver, and include it on a standing manual-invoice report | P1 | L5 |
| FR-ARB-011 | Invoice cancellation | Cancel an unpaid, un-dispatched invoice with approval and reason, preserving the number in the sequence as a cancelled document | **P0** | L5 |
| FR-ARB-012 | Rounding and presentation | Apply a single, declared rounding policy at the invoice level, posting the rounding difference to a named account | **P0** | L5 |

### 5.2 Invoice Delivery & Presentment

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ARB-013 | Multi-channel delivery | Deliver an invoice by customer portal, email, WhatsApp, SMS and print, per the customer's recorded preference, with a single delivery record per invoice | **P0** | L5 |
| FR-ARB-014 | Delivery confirmation | Record delivery status per channel — sent, delivered, opened, failed — and retry or escalate on failure | **P0** | L5 |
| FR-ARB-015 | Embedded payment link | Include a secure, single-use payment link on every delivered invoice, offering bKash, Nagad, card and bank transfer (BR-FIN-004) | **P0** | L5 |
| FR-ARB-016 | Portal presentment | Present open and settled invoices, credit notes, receipts and the running balance in P01 (individual) and P04 (corporate), with download and pay actions | **P0** | L5 |
| FR-ARB-017 | Customer statement | Produce a statement of account on demand and on a scheduled cycle, showing opening balance, transactions, ageing and closing balance | **P0** | L2/L5 |
| FR-ARB-018 | Brand partner presentment | Present claim invoices, their evidence and their settlement status in P08 | P1 | L5 |

### 5.3 Receipt Capture, Matching & Allocation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ARB-019 | Multi-tender receipt capture | Capture a receipt in any tender type — cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer, cheque, on-account adjustment — with the tender-specific reference required to reconcile it (BR-FIN-004) | **P0** | L1/L5 |
| FR-ARB-020 | Channel clearing accounts | Post every non-cash receipt to its channel clearing account and hold it there until M50 matches the settlement, never directly to a bank account | **P0** | L5 |
| FR-ARB-021 | Automatic matching | Match an incoming receipt to open invoices automatically using reference, amount, customer and date signals, with a confidence score and a manual exception queue below the threshold | **P0** | L5 |
| FR-ARB-022 | Partial and multi-invoice allocation | Allocate one receipt across several invoices, and several receipts to one invoice, including partial settlement with a tracked remaining balance | **P0** | L1/L5 |
| FR-ARB-023 | Over- and under-payment | Handle overpayment as an on-account balance and underpayment as a partial settlement with the shortfall retained on the open item, both visible to the customer | **P0** | L5 |
| FR-ARB-024 | Unapplied receipts | Hold unmatched receipts as unapplied, age them, and escalate any receipt unapplied beyond the configured period | **P0** | L5 |
| FR-ARB-025 | Payment against cancelled invoice | Reject any attempt to record a payment against a cancelled invoice (BRU-FIN-03) | **P0** | L5 |
| FR-ARB-026 | High-value cash NID capture | Require the customer's NID before completing a cash receipt above the statutory threshold, applying the rule and threshold owned by M51 (BRU-FIN-02) | **P0** | L5 |
| FR-ARB-027 | Receipt reversal | Reverse a receipt (bounced cheque, failed settlement, gateway reversal) with a reason code, restoring the invoice to open and notifying the customer and the branch | **P0** | L5 |
| FR-ARB-028 | Deposit and retention | Track customer deposits and contract retention money separately from trade receivables, with scheduled release or application | P1 | L5 |

### 5.4 Ageing, Credit Control & Collections

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ARB-029 | Ageing analysis | Produce ageing by customer, segment, branch, business line, currency and age bucket, with a point-in-time snapshot retained per period (BR-FIN-009) | **P0** | L2/L5 |
| FR-ARB-030 | Credit terms and limits | Hold payment terms and a credit limit per customer, and evaluate exposure as open invoices plus undelivered committed work | **P0** | L5 |
| FR-ARB-031 | Credit hold | Place an account on credit hold automatically on limit breach or overdue threshold, blocking new billable commitments in M01/M08 until released by an authorised role | **P0** | L5 |
| FR-ARB-032 | Dunning ladders | Configure multi-level reminder ladders per customer segment, each level defining timing, channel, tone, recipient and escalation, and execute them automatically (BR-FIN-009) | **P0** | L2/L5 |
| FR-ARB-033 | Dunning suppression | Suppress reminders for an invoice under active dispute, under an agreed payment plan, or for accounts flagged strategic, and record every suppression | **P0** | L5 |
| FR-ARB-034 | Collections worklist | Present collectors with a worklist prioritised by value, age, risk and promise status, rather than an undifferentiated ageing report | P1 | L5 |
| FR-ARB-035 | Promise to pay | Record a promise to pay with amount and date, suspend dunning until it lapses, and escalate automatically on breach | P1 | L5 |
| FR-ARB-036 | Dispute management | Log a dispute against a specific invoice or line, suspend dunning on the disputed amount only, route it for resolution, and track it to closure with an outcome code | **P0** | L5 |
| FR-ARB-037 | Payment plans | Agree and monitor an instalment plan against an overdue balance, with automatic escalation on a missed instalment | P2 | L5 |

### 5.5 Credit Notes, Refunds & Write-Offs

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ARB-038 | Credit note request and approval | Require a credit-note request carrying a mandatory reason from a controlled taxonomy, approved by the Finance Manager or above and never by the requester (BR-FIN-014, BRU-FIN-04, SOD-04) | **P0** | L5 |
| FR-ARB-039 | Credit note issuance and application | Issue the statutory credit-note document, apply it against the original invoice or hold it on account, and reflect the VAT adjustment through M51 | **P0** | L1/L5 |
| FR-ARB-040 | Refund authorisation and execution | Authorise a refund within the authority matrix, select the method (original tender where possible), instruct M50 to execute, and reconcile the outcome | **P0** | L5 |
| FR-ARB-041 | Write-off | Write off an uncollectible balance only with approval within the authority matrix and a documented recovery history, and report every write-off | **P0** | L5 |
| FR-ARB-042 | Bad-debt provisioning | Compute a provision by ageing band and customer risk class and raise it to M19 for posting, without posting a journal itself | P1 | L5 |

### 5.6 Revenue Leakage Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ARB-043 | Delivered-but-unbilled reconciliation | Reconcile, daily, completed operational transactions against issued invoices across every revenue stream, and report every delivered item with no invoice, by age and value | **P0** | L5 |
| FR-ARB-044 | Billable-event ageing and escalation | Age every unprocessed billable event, escalate beyond threshold to the branch manager and then to the CFO, and never allow an event to expire silently | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Billable event contract** | Every revenue module publishes a versioned `billing.event` with customer, source document, lines, unit price (from M11), quantity, dimensions, currency, tax context and an idempotency key. M20 refuses an unmapped schema version rather than partially assembling an invoice |
| T-02 | **Exactly-once invoicing** | A billable event produces exactly one invoice. Duplicate delivery, retry and replay are all resolved by idempotency key at the persistence layer; a duplicate invoice to a customer is treated as a severity-1 defect |
| T-03 | **Invoice generation latency** | p95 from billable event to issued and delivered invoice ≤ 10 minutes; hard target ≤ 1 hour for > 97% of invoices (KPI-054) |
| T-04 | **Gapless statutory numbering under concurrency** | Invoice numbers are allocated from a per-entity, per-document-type sequence that is gapless even under concurrent generation and under transaction rollback; a rolled-back invoice consumes and records a cancelled number rather than leaving a gap |
| T-05 | **Tax determination as a call, never a calculation** | M20 never computes tax. It calls M51's determination service with the transaction context and renders what is returned, storing the determination reference on the invoice for audit |
| T-06 | **Monetary discipline** | All amounts `Monetary` with explicit currency; no floats (AS-10). Line-level tax is stored as returned; invoice totals are derived, never independently recomputed at presentation |
| T-07 | **Two-stage payment model** | Customer-side receipt and merchant-side settlement are distinct records linked by a channel reference. The clearing-account balance per channel is a reported figure and must age to zero |
| T-08 | **Receipt matching engine** | Deterministic scoring over reference, amount, customer, date proximity and history; auto-apply above the configured confidence, queue below it. Target auto-match ≥ 90% by count |
| T-09 | **Payment link security** | Payment links are single-use, time-limited, signed, and bound to the invoice and amount; a replayed or tampered link is rejected and logged as a security event |
| T-10 | **Volume envelope** | ~250,000 jobs/year plus contract, rental, marketplace, e-commerce and subscription billing → **~400,000–500,000 invoices and ~600,000 receipt applications per year**. Open-item tables are indexed on (customer, state, due_date) and (entity, period) |
| T-11 | **Ageing snapshot immutability** | A period ageing is computed once at close and stored; subsequent transactions never alter a historical snapshot |
| T-12 | **Delivery idempotency** | A re-delivered invoice does not create a second invoice, a second payment link, or a second dunning clock; delivery attempts are recorded against one invoice |
| T-13 | **Offline receipt capture** | Branch counters continue to capture cash receipts during a connectivity loss through an append-only local journal, synchronising with server-side conflict resolution (AS-13); non-cash tenders require connectivity by design |
| T-14 | **Event emission via outbox** | Every AR state change emits a domain event through the transactional outbox (AS-08); M19, M50, M51, M53 and M54 consume, never poll |
| T-15 | **Multi-entity and operating-unit scoping** | Every AR record carries `company_id` and `operating_unit_id`; a branch sees only its own receivables unless the role grants wider scope (AS-03) |
| T-16 | **PII and payment-data handling** | Customer NID, contact details and any payment identifiers are field-level encrypted (AS-14); no card data is stored — the gateway holds it, and M20 stores only a token and the last four digits |
| T-17 | **Retention** | Invoices, credit notes, receipts and their delivery evidence retained seven years and queryable (Companies Act / NBR) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M20 |
|---|---|---|
| **Billing staff** | Types every invoice from a paper form, 3–7 days after the job | Reviews exceptions. The typing has gone; the role becomes collections and dispute resolution |
| **Cashier / counter finance** | Records a payment on paper, reconciles from memory at shift end | Captures the receipt at the counter against the open invoice, with the tender reference required to reconcile it |
| **Customer** | Waits days for an invoice, receives it on WhatsApp, pays by whatever means is convenient, and has no record | Receives the invoice within the hour with a pay-now link, sees every document in the portal, and gets an instant receipt |
| **Corporate client** | Receives inconsistent invoices per job and reconciles them manually | Receives one consolidated statement-based invoice per period against their agreed terms, in P04 |
| **Brand partner** | Receives claim invoices by email with evidence assembled by hand | Receives claim invoices with evidence attached automatically, visible in P08 |
| **Branch manager** | Cannot see what their branch is owed | Sees branch receivables, ageing and unbilled work live |
| **Collector** | Works from a printed ageing report | Works a prioritised worklist with promise tracking and dispute context |
| **Finance Manager** | Discovers billing errors when a customer complains | Sees credit-note rate, dispute rate and unbilled ageing as leading indicators |
| **CFO** | Cannot state DSO or revenue leakage | Both are measured daily; both have targets |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Cash flow acceleration** | Invoicing lag falls from 3–7 days to < 1 hour, and reminders run automatically | Contributes to the **BDT 26 lac per year** financial close and cash-flow benefit (Exec Summary §6.2, M19 with M20) |
| **Revenue leakage recovery** | Delivered-but-unbilled becomes visible and ageing; leakage falls below 0.5% | On a business of this scale, closing even one percentage point of leakage is a material recurring recovery |
| **Administrative labour released** | Manual invoice preparation, delivery and payment recording eliminated across 51+ branches | A material share of the **BDT 62 lac** cross-module administrative saving |
| **Working capital release** | DSO to < 32 days from an unmeasured baseline | One-time cash release proportional to the reduction in receivable days |
| **Warranty revenue recovery** | Claim invoices generated with complete evidence, on time, to 17+ brands | Directly supports the **BDT 100 lac** warranty revenue recovery benefit owned by M09 |
| **Billing accuracy** | Invoices assembled from system data rather than transcribed from paper; credit notes < 1.5% of invoices | Reduces dispute handling cost and the customer churn that follows a wrong invoice |
| **Bad debt reduction** | Credit limits enforced at the point of commitment, not discovered at the point of default | Reduces write-offs and the provision charge |
| **Payment convenience** | Pay-now links on every invoice across bKash, Nagad, card and bank | Higher first-attempt collection rate; fewer counter visits |
| **Close acceleration** | Receivables reconciled continuously rather than at month-end | Direct contributor to the ≤ 3-day close (KPI-050) |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Statutory invoice compliance** | Every sale produces a compliant Mushak 6.3 with gapless numbering — the single most frequently examined item in an NBR VAT audit |
| **Customer trust and transparency** | A customer who can see every invoice, receipt and credit note in a portal argues less and stays longer. Transparency is a stated 1000FiX competitive advantage |
| **ISO 9001 conformance** | Documented, controlled billing and dispute processes with evidence retention |
| **Brand partner assurance** | Claim invoices with automatic evidence packs change the tone of a brand's annual partner audit |
| **Fraud reduction** | Receipts matched to invoices and to bank settlement, with no path from a counter to a bank account that is not reconciled |
| **Institutional memory** | Billing arrangements live in customer records, not in the billing clerk's head |
| **Scalability of revenue streams** | A fourteenth revenue stream needs a billable-event contract, not a new billing desk |

---

## 8. Lifecycle & State Models

### 8.1 Invoice Lifecycle

```
  BILLABLE EVENT (from M01/M31/M08/M39/M13/M12/M38/M09/M05/M06/M14)
         │
         ▼
   ┌───────────┐   validation failed   ┌──────────────┐
   │  QUEUED   │──────────────────────►│  EXCEPTION   │──► resolved ──┐
   └─────┬─────┘                       │  (aged,      │               │
         │ assembled + tax determined  │  escalated)  │◄──────────────┘
         ▼                             └──────────────┘
   ┌───────────┐
   │   DRAFT   │  (proforma / advance may stop here)
   └─────┬─────┘
         │ issued — number allocated, Mushak 6.3 rendered
         ▼
   ┌───────────┐        cancelled (unpaid, approved)      ┌───────────┐
   │  ISSUED   │────────────────────────────────────────► │ CANCELLED │
   └─────┬─────┘                                          └───────────┘
         │ delivered
         ▼
   ┌───────────┐  partial receipt   ┌──────────────────┐
   │ DELIVERED │───────────────────►│ PARTIALLY PAID   │
   └─────┬─────┘                    └────────┬─────────┘
         │ full receipt applied              │ balance received
         ▼                                   ▼
   ┌─────────────────────────────────────────────┐
   │                   PAID                      │
   └─────────────────────────────────────────────┘
         ▲                                   │
         │ credit note applied               │ receipt reversed
         │                                   ▼
   ┌───────────┐   ┌──────────┐        ┌──────────┐
   │ CREDITED  │   │ DISPUTED │        │ OVERDUE  │──► dunning ladder
   └───────────┘   └──────────┘        └────┬─────┘
                                            │ uncollectible, approved
                                            ▼
                                      ┌────────────┐
                                      │ WRITTEN OFF│
                                      └────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Queued | A billable event is received and passes schema validation | System |
| Queued | Exception | Customer, price, tax context or dimension is missing or invalid | System |
| Exception | Queued | The blocking data is corrected in the owning module | Finance Officer / owning module |
| Queued | Draft | Lines assembled, price obtained from M11, tax determined by M51 | System |
| Draft | Issued | Number allocated from the gapless sequence; statutory document rendered | System |
| Issued | Cancelled | Unpaid and undelivered, with approval and reason; number retained as cancelled | Finance Manager |
| Issued | Delivered | Delivered on at least one channel with confirmation | System |
| Delivered | Partially paid | A receipt is applied for less than the balance | System |
| Delivered / Partially paid | Paid | Applied receipts equal the invoice balance | System |
| Delivered | Overdue | Due date passed with a balance outstanding | System |
| Any open state | Disputed | A dispute is logged against the invoice or a line | Customer / agent / collector |
| Disputed | Prior state | Dispute resolved with an outcome code | Finance Manager |
| Any open state | Credited | An approved credit note is applied | Finance Manager |
| Paid | Overdue | An applied receipt is reversed (bounced cheque, failed settlement) | System |
| Overdue | Written off | Approved within the authority matrix with documented recovery history | CFO / Finance Manager |

### 8.2 Receipt Lifecycle

```
   CUSTOMER PAYS
        │
        ├── cash at counter ──────────► CAPTURED ──► (M04 drawer, M50 deposit)
        │
        ├── card / bKash / Nagad /
        │   SSLCOMMERZ ──────────────► CAPTURED ──► IN CHANNEL CLEARING
        │                                                │
        │                                                │ M50 matches settlement
        │                                                ▼
        │                                          SETTLED TO BANK
        │
        └── bank transfer / cheque ───► CAPTURED ──► AWAITING CLEARANCE ──► CLEARED
                                                              │
                                                              └──► BOUNCED ──► REVERSED

   Every CAPTURED receipt then follows:
        CAPTURED ──► MATCHED (auto or manual) ──► APPLIED ──► [FULLY | PARTIALLY] ALLOCATED
              └──► UNAPPLIED (aged, escalated) ──┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Captured | Payment recorded with tender type and the reference that tender requires | Cashier / system / customer (portal) |
| Captured | In channel clearing | Non-cash tender; posted to the channel clearing account, never to a bank account | System |
| In channel clearing | Settled to bank | M50 matches the gateway/MFS settlement to the bank statement | M50 |
| Captured | Awaiting clearance | Cheque or bank transfer pending confirmation | System |
| Awaiting clearance | Cleared / Bounced | Bank confirmation received via M50 | M50 |
| Captured | Matched | Auto-match confidence above threshold, or manual match | System / Finance Officer |
| Matched | Applied | Allocation posted against one or more open items | System |
| Captured | Unapplied | No match found; held on account, aged and escalated | System |
| Applied / Cleared | Reversed | Bounce, failed settlement or gateway reversal, with reason code | System / Finance Officer |

### 8.3 Credit Note Lifecycle

| State | Meaning | Guard to Exit |
|---|---|---|
| Requested | Raised with a mandatory reason from the controlled taxonomy and a reference to the original invoice | Submitted for approval |
| Pending approval | Awaiting Finance Manager or above | Approver must not be the requester (SOD-04) |
| Approved | Authorised for issuance | Statutory document rendered |
| Issued | Statutory credit note issued; VAT adjustment raised to M51 | — |
| Applied | Set against the original invoice or a later invoice | — |
| On account | Held as a credit balance for the customer | Applied or refunded |
| Refunded | Converted to a refund executed by M50 | — |
| Rejected | Declined with a reason; the original invoice stands | — |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-ARB-01 | Every billable event must result in an invoice or an explicitly approved suppression; an event may never expire unprocessed | **H** | CFO |
| BRU-ARB-02 | An invoice is generated automatically from a billable event; a manually created invoice requires a reason code and an approver and is separately reported | **H** | Finance Manager |
| BRU-ARB-03 | Every customer invoice includes VAT at the rate determined by M51 and displays the Company's BIN (BRU-FIN-01) | **H** | CFO |
| BRU-ARB-04 | M20 never computes tax; it renders the determination returned by M51 and stores the determination reference | **H** | CTO |
| BRU-ARB-05 | Invoice numbers are gapless and sequential per entity and document type; a cancelled invoice retains its number and is never reused | **H** | CFO |
| BRU-ARB-06 | A payment cannot be recorded against a cancelled invoice (BRU-FIN-03) | **H** | Finance Manager |
| BRU-ARB-07 | A cash receipt above BDT 50,000 cannot be completed without recording the customer's NID (BRU-FIN-02) | **H** | CFO |
| BRU-ARB-08 | Every non-cash receipt posts to its channel clearing account and moves to a bank account only on M50 settlement match | **H** | CFO |
| BRU-ARB-09 | A credit note requires approval by the Finance Manager or above, and never by the person who requested it (BRU-FIN-04, SOD-04) | **H** | CFO |
| BRU-ARB-10 | A credit note requires a reason from the controlled taxonomy; free-text-only reasons are rejected | **H** | Finance Manager |
| BRU-ARB-11 | A refund is executed only through M50, to a method within the approved set, and never in cash above the approval threshold | **H** | CFO |
| BRU-ARB-12 | A write-off requires approval within the authority matrix and a documented recovery history | **H** | CFO |
| BRU-ARB-13 | An account exceeding its credit limit or its overdue threshold is placed on credit hold, blocking new billable commitments until released by an authorised role | **H** | Finance Manager |
| BRU-ARB-14 | Credit-hold release requires a role senior to the one that would raise the commitment, and is logged | **A** | Finance Manager |
| BRU-ARB-15 | Dunning is suppressed on an invoice under active dispute or under an agreed payment plan, for the disputed or scheduled amount only | **C** | Finance Manager |
| BRU-ARB-16 | Every dunning suppression records who suppressed it, why, and until when | **H** | Finance Manager |
| BRU-ARB-17 | A dispute must carry an outcome code at closure; a dispute cannot be closed as "resolved" without one | **H** | Finance Manager |
| BRU-ARB-18 | Ageing snapshots taken at period close are immutable and are never recomputed | **H** | CFO |
| BRU-ARB-19 | A warranty claim invoice cannot be issued without the complete evidence set required by that brand's agreement | **H** | Warranty Claims Officer |
| BRU-ARB-20 | Warranty claim invoices to brand partners are raised in the agreed currency at the rate prevailing on the date of service completion | **C** | Finance Manager |
| BRU-ARB-21 | A receipt cannot be applied across legal entities | **H** | CFO |
| BRU-ARB-22 | Unapplied receipts older than the configured period are escalated and may not be netted against unrelated balances | **H** | Finance Manager |
| BRU-ARB-23 | Bad-debt provision is computed by ageing band and risk class and is raised to M19 for posting; M20 never posts it | **C** | CFO |
| BRU-ARB-24 | Delivered-but-unbilled items are reconciled daily; any item older than the configured threshold escalates to the CFO | **H** | CFO |
| BRU-ARB-25 | No card data is stored in the ERP; only a gateway token and the last four digits | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.billable.event` | `fix_billable_event` | The intake queue — and the leakage detector | source_module, event_type, schema_version, idempotency_key, customer_id, source_doc_type, source_doc_id, lines_json, currency, dimensions_json, received_at, due_by, state, invoice_id, exception_reason, age_hours, escalated_to |
| `fix.ar.invoice` | `fix_ar_invoice` | Customer invoice header | number, document_type (tax/proforma/advance/claim/consolidated), entity_id, operating_unit_id, customer_id, customer_bin, invoice_date, due_date, currency, fx_rate, subtotal, tax_total, total, rounding, balance, state, mushak_reference, tax_determination_ref, source_event_ids, business_line_id, contract_id, gl_entry_ref |
| `fix.ar.invoice.line` | `fix_ar_invoice_line` | Invoice line | invoice_id, sequence, catalogue_item_id, description_en, description_bn, quantity, uom, unit_price, price_source_ref (M11), discount, line_total, tax_code, tax_amount, cost_center_id, project_id, brand_id, channel_id, source_doc_type, source_doc_id |
| `fix.ar.invoice.delivery` | `fix_ar_invoice_delivery` | Delivery attempt and outcome | invoice_id, channel (portal/email/whatsapp/sms/print), recipient, sent_at, status, opened_at, failure_reason, retry_count, payment_link_id |
| `fix.ar.payment.link` | `fix_ar_payment_link` | Secure pay-now link | invoice_id, token, amount, methods_offered, expires_at, single_use, used_at, gateway_session_ref, state |
| `fix.ar.receipt` | `fix_ar_receipt` | Money received | entity_id, operating_unit_id, customer_id, receipt_date, tender_type, amount, currency, fx_rate, tender_reference, gateway_txn_ref, channel_clearing_account_id, captured_by, shift_id (M04), nid_captured, state, reversal_of_id, reversal_reason |
| `fix.ar.allocation` | `fix_ar_allocation` | Receipt applied to an open item | receipt_id, invoice_id, credit_note_id, amount, allocated_at, allocated_by, match_confidence, match_method (auto/manual), reversed_at |
| `fix.ar.open.item` | `fix_ar_open_item` | The customer ledger line | customer_id, entity_id, document_type, document_id, document_date, due_date, original_amount, balance, currency, age_days, age_bucket, state, dispute_id, hold_flag |
| `fix.ar.ageing.snapshot` | `fix_ar_ageing_snapshot` | Immutable period ageing | period_id, entity_id, customer_id, segment, branch_id, business_line_id, bucket_current, bucket_1_30, bucket_31_60, bucket_61_90, bucket_90_plus, total, taken_at |
| `fix.ar.credit.profile` | `fix_ar_credit_profile` | Credit terms and exposure | customer_id, entity_id, payment_terms, credit_limit, currency, current_exposure, committed_exposure, risk_class, hold_state, hold_reason, held_at, released_by |
| `fix.ar.credit.hold` | `fix_ar_credit_hold` | Hold event | customer_id, trigger (limit/overdue/manual), placed_at, placed_by, blocked_modules, released_at, released_by, release_reason |
| `fix.ar.dunning.policy` | `fix_ar_dunning_policy` | Ladder definition | name, customer_segment, entity_id, active, levels_json (offset_days, channel, template, recipient_role, escalation_role) |
| `fix.ar.dunning.action` | `fix_ar_dunning_action` | One executed reminder | invoice_id, policy_id, level, scheduled_for, executed_at, channel, recipient, delivery_status, suppressed, suppression_reason, suppressed_by |
| `fix.ar.collection.case` | `fix_ar_collection_case` | Collections worklist item | customer_id, total_overdue, oldest_age, priority_score, assigned_to, state, next_action_at, last_contact_at, outcome |
| `fix.ar.promise` | `fix_ar_promise` | Promise to pay | case_id, customer_id, amount, promised_date, made_by, recorded_by, state (open/kept/broken), broken_at |
| `fix.ar.dispute` | `fix_ar_dispute` | Billing dispute | invoice_id, line_id, disputed_amount, reason_code, raised_by, raised_at, assigned_to, state, outcome_code, resolved_at, resolution_note, linked_case_id (M27) |
| `fix.ar.payment.plan` | `fix_ar_payment_plan` | Instalment arrangement | customer_id, total_amount, instalments_json, approved_by, state, missed_count |
| `fix.ar.credit.note` | `fix_ar_credit_note` | Credit note | number, original_invoice_id, customer_id, entity_id, reason_code, reason_note, amount, tax_amount, requested_by, approved_by, state, mushak_reference, applied_to_invoice_id, gl_entry_ref |
| `fix.ar.refund` | `fix_ar_refund` | Refund authorisation | customer_id, credit_note_id, receipt_id, amount, method, bank_details_ref, authorised_by, state, payment_instruction_id (M50), executed_at, reconciled_at |
| `fix.ar.writeoff` | `fix_ar_writeoff` | Write-off | customer_id, open_item_ids, amount, reason_code, recovery_history_ref, requested_by, approved_by, approved_at, gl_entry_ref |
| `fix.ar.provision` | `fix_ar_provision` | Bad-debt provision proposal | period_id, entity_id, ageing_band, risk_class, base_amount, provision_rate, provision_amount, raised_to_gl_at |
| `fix.ar.deposit` | `fix_ar_deposit` | Customer deposit / retention | customer_id, contract_id, type (deposit/retention), amount, received_at, release_due_at, released_at, applied_to_invoice_id, state |
| `fix.ar.statement` | `fix_ar_statement` | Statement of account | customer_id, entity_id, period_from, period_to, opening_balance, closing_balance, lines_json, generated_at, delivered_at, document_id |
| `fix.ar.unbilled.exception` | `fix_ar_unbilled_exception` | Delivered but not invoiced | source_module, source_doc_id, customer_id, delivered_at, estimated_value, age_days, state, escalated_to, resolved_at, resolution |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party` (customer, brand partner, corporate account, seller) | M33 | Read via API |
| `fix.price.resolution.log` | M11 | Read — the price is obtained, never derived |
| `fix.catalogue.item` | M37 | Read for line description and tax classification |
| `fix.tax.determination` | M51 | Call and store the reference; M51 owns the result |
| `fix.mushak.sequence`, `fix.vat.register.line` | M51 | Read format and sequence; M51 owns the register |
| `fix.service.order`, `fix.work.order` | M01 / M02 | Read as billable-event source |
| `fix.contract`, `fix.contract.sla` | M08 | Read for terms, entitlement and consolidation rules |
| `fix.billing.schedule` | M39 | Read as billable-event source |
| `fix.rental.agreement` | M13 | Read as billable-event source |
| `fix.marketplace.job`, `fix.marketplace.job` | M12 | Read as billable-event source |
| `fix.brand.claim` | M09 | Read for claim invoicing and evidence assembly |
| `fix.wallet.transaction` | M10 | Read for redemption value applied to an invoice |
| `fix.bank.account`, `fix.settlement.batch`, `fix.payment.instruction` | M50 | Read settlement state; instruct refunds |
| `fix.revenue.schedule` | M53 | Read — M53 consumes the invoice, not the reverse |
| `fix.gl.account`, `fix.fiscal.period` | M19 | Read for period state and control-account balance |
| `fix.branch.shift`, `fix.cash.drawer` | M04 | Read to bind a counter receipt to its shift |
| `fix.conversation`, `fix.conversation` | M27 | Link a dispute to its conversation |
| `fix.document` | M24 | Store and reference invoice, credit note and evidence documents |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-ARB-01 | A billable event is received | Validate, obtain price from M11, request tax determination from M51, assemble, issue and deliver the invoice | Move to exception with a precise reason, age it, and escalate; **never** issue a partial invoice |
| AUT-ARB-02 | An invoice is issued | Deliver on the customer's preferred channels, attach the payment link, and record the delivery outcome | Retry on the configured schedule, then fall back to an alternative channel, then raise a delivery exception |
| AUT-ARB-03 | An invoice is issued to a corporate account with consolidated billing | Add the item to the account's open statement instead of delivering an individual invoice | Deliver individually and flag the consolidation configuration |
| AUT-ARB-04 | A warranty claim is approved in M09 | Assemble the claim invoice with the brand's required evidence set, convert at the service-completion-date rate, and issue | Hold and notify the Warranty Claims Officer with the missing evidence named |
| AUT-ARB-05 | A receipt is captured | Attempt automatic matching against open items, apply above the confidence threshold, queue below it | Hold as unapplied, age it, and escalate beyond the threshold |
| AUT-ARB-06 | A gateway or MFS payment completes | Record the customer-side receipt against the channel clearing account and confirm to the customer immediately | Record the payment as pending confirmation and reconcile through M50; never leave the customer without acknowledgement |
| AUT-ARB-07 | M50 reports a settlement match | Move the receipt from channel clearing to bank and close the clearing entry | Keep in clearing, age it, and report on the unreconciled settlement list |
| AUT-ARB-08 | M50 reports a bounced cheque or a reversed gateway transaction | Reverse the receipt, restore the invoice to open, notify the customer and the branch, and restart the dunning clock | Raise a high-priority exception |
| AUT-ARB-09 | An invoice passes its due date | Move it to overdue and start the dunning ladder for the customer's segment | Ladder starts on the next scheduled run; no invoice is silently skipped |
| AUT-ARB-10 | Dunning level due | Send the reminder on the level's channel to the level's recipient, unless a suppression rule applies | Log a suppressed or failed action and escalate at the next level |
| AUT-ARB-11 | Credit limit or overdue threshold breached | Place the account on credit hold and notify sales, the branch and the account manager; block new billable commitments in M01/M08 | Alert only, with the failure reported — the block is never silently skipped |
| AUT-ARB-12 | A promise to pay lapses without payment | Mark the promise broken, escalate the collection case, and resume dunning | Case escalates on the next run |
| AUT-ARB-13 | A dispute is logged | Suspend dunning on the disputed amount, assign to the resolver by reason code, and start the resolution clock | Dispute recorded and escalated manually |
| AUT-ARB-14 | A credit note is approved | Issue the statutory document, apply it to the original invoice or hold on account, and raise the VAT adjustment to M51 | Hold in approved state and alert |
| AUT-ARB-15 | A refund is authorised | Create the payment instruction in M50, track it to execution, and reconcile the outcome to the credit note | Refund remains authorised and appears on the pending-refund report |
| AUT-ARB-16 | Statement cycle due | Generate and deliver customer statements for accounts on a statement cycle | Retry; report failures per customer |
| AUT-ARB-17 | Daily | Reconcile completed operational transactions across every revenue stream against issued invoices, and publish the delivered-but-unbilled exception list | Report with a data-availability warning; never suppress the list |
| AUT-ARB-18 | Billable event exceeds its age threshold | Escalate to the branch manager, then to the Finance Manager, then to the CFO | Escalation is unconditional |
| AUT-ARB-19 | Period close | Take the immutable ageing snapshot, compute the bad-debt provision proposal, and raise it to M19 | Block the close task and report |
| AUT-ARB-20 | An unapplied receipt exceeds its age threshold | Escalate to the Finance Manager with the customer and tender context | Escalation is unconditional |

---

## 12. Interfaces

### 12.1 Upstream — M20 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 Service Order / M31 Workshop | Job closed and billable — labour, parts, call-out | Event `billing.event` |
| M02 Field Service | On-site job completion and field-collected payment | Event + command |
| M04 Branch Operations | Counter receipt against an open invoice, bound to a shift | Command |
| M08 Contract & SLA | Contract billing cycle, entitlement consumption, excess usage | Event |
| M39 Subscription & Recurring Billing | Subscription cycle due, proration, plan change | Event |
| M13 Rental & EaaS | Rental period, usage, damage recovery | Event |
| M14 Trade-In & Refurbishment | Refurbished device sale | Event |
| M12 Marketplace / M38 E-Commerce | Order captured, marketplace commission invoice | Event |
| M09 Warranty & Claims | Approved claim with its evidence set | Event + REST |
| M05 Managed Services / M06 Data Services | Service period and engagement milestones | Event |
| M11 Pricing | Determined price for each billable line | REST |
| M37 Catalogue | Item description, unit of measure, tax classification | REST |
| M51 Tax & Regulatory | Tax determination, Mushak format and sequence, NID threshold rule | REST |
| M50 Treasury & Cash | Settlement match, cheque clearance, bounce, refund execution status | Events |
| M33 Party Master | Customer identity, segment, contact preference, BIN | REST |
| M10 Loyalty & Rewards | Redemption value to apply | REST |
| M19 General Ledger | Period state, receivable control-account balance | REST |
| M27 Contact Centre | Customer-raised billing queries linked to disputes | Event |

### 12.2 Downstream — M20 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M19 General Ledger | Invoice issued, credit note, receipt applied, write-off, provision — as financial events for posting | Events |
| M50 Treasury & Cash | Expected receipts by channel, refund instructions, deposit expectations | Events + commands |
| M51 Tax & Regulatory | Issued invoices and credit notes with their tax determination, for the VAT registers and the Mushak 9.1 return | Events |
| M53 Revenue & Settlement | Issued invoices as the basis for revenue schedules and contract balances | Events |
| M54 Costing & FP&A | Revenue by customer, business line, branch and channel | Warehouse extract |
| M07 CRM | Customer payment behaviour, credit hold state, dispute history | REST + events |
| M08 Contract & SLA | Billing status against contract entitlement | REST |
| M09 Warranty & Claims | Claim invoice and settlement status | Events |
| M01 / M08 | Credit-hold block on new billable commitments | REST |
| M27 Contact Centre | Invoice, balance and dispute context for the agent console | REST |
| M25 BI / M62 Data Platform | Invoicing, receipt, ageing, dispute and leakage facts | Warehouse extract |
| M26 AI/ML | Payment behaviour series for collections prioritisation models | Warehouse extract |
| P01 Customer Portal | Invoices, receipts, credit notes, balance, pay-now | REST |
| P04 Corporate B2B Portal | Consolidated invoices, statements, approvals, dispute raising | REST |
| P08 Brand Partner Portal | Claim invoices, evidence packs and settlement status | REST |
| P03 Admin Portal | Full AR workspace | Native |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `ar.invoice_issued` | invoice, customer, entity, lines, tax determination, dimensions, totals | M19, M51, M53, M54, M25 |
| `ar.invoice_delivered` | invoice, channel, recipient, status | M27, M07, M25 |
| `ar.invoice_cancelled` | invoice, reason, approver | M19, M51, M53 |
| `ar.receipt_captured` | receipt, tender, amount, channel clearing account, shift | M19, M50, M04 |
| `ar.receipt_applied` | receipt, invoices, amounts, match method and confidence | M19, M53, M25 |
| `ar.receipt_reversed` | receipt, reason, restored invoices | M19, M50, M27 |
| `ar.receipt_unapplied_aged` | receipt, age, customer, amount | M50, M25 |
| `ar.credit_note_issued` | credit note, original invoice, reason, tax adjustment | M19, M51, M53 |
| `ar.refund_authorised` | customer, amount, method, credit note | M50, M19 |
| `ar.writeoff_posted` | customer, open items, amount, approver | M19, M07, M23 |
| `ar.provision_raised` | period, entity, band, provision amount | M19, M54 |
| `ar.credit_hold_placed` | customer, trigger, blocked modules | M01, M08, M07, M12 |
| `ar.credit_hold_released` | customer, releaser, reason | M01, M08, M07 |
| `ar.dunning_executed` | invoice, level, channel, outcome | M27, M07, M25 |
| `ar.dispute_raised` | invoice, line, amount, reason | M27, M23, M07 |
| `ar.dispute_resolved` | dispute, outcome code, resolution | M27, M23, M11 |
| `ar.unbilled_detected` | source module, document, customer, age, estimated value | M19, M25, owning module |
| `ar.ageing_snapshot_taken` | period, entity, buckets, totals | M19, M54, M25 |
| `receivable.dunning_stage_changed` | customer id, open item, prior stage, new stage, days overdue, action taken | M08, M07, M33, M53 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-ARB-01 | bKash merchant payment API | Bidirectional | Customer-initiated payment against an invoice; transaction status callback |
| INT-ARB-02 | Nagad merchant payment API | Bidirectional | Customer-initiated payment; status callback |
| INT-ARB-03 | SSLCOMMERZ payment gateway | Bidirectional | Card and aggregated wallet payment; IPN callback and refund initiation |
| INT-ARB-04 | Email service provider | Outbound | Invoice, statement, reminder and receipt delivery |
| INT-ARB-05 | WhatsApp Business API (via M27) | Outbound | Invoice and reminder delivery on the channel customers actually read |
| INT-ARB-06 | SMS gateway (via M27) | Outbound | Reminder and receipt confirmation |
| INT-ARB-07 | Brand partner claim portals (Dell, HP, Lenovo, Acer and others) | Outbound | Claim invoice and evidence submission where the brand exposes an interface; file exchange otherwise |
| INT-ARB-08 | Thermal and A4 printers at branch counters | Outbound | Printed Mushak 6.3 invoice and receipt at the point of service |
| INT-ARB-09 | Legacy billing spreadsheets and standalone accounting software | Inbound, one-time | Open receivable migration; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/ar/billable-events` | POST | Submit a billable event (idempotent) | All revenue modules |
| `/api/v1/ar/billable-events` | GET | Queue state, exceptions and ageing | P03, P06 |
| `/api/v1/ar/invoices` | GET · POST | List, retrieve and (exceptionally) create invoices | P03, P01, P04, P08 |
| `/api/v1/ar/invoices/{id}/deliver` | POST | Deliver or re-deliver on nominated channels | P03 |
| `/api/v1/ar/invoices/{id}/cancel` | POST | Cancel with approval and reason | P03 |
| `/api/v1/ar/invoices/{id}/payment-link` | POST | Issue a single-use payment link | P01, P04, P03, M27 |
| `/api/v1/ar/receipts` | POST | Capture a receipt (offline-capable at the counter) | P03, P02, P01, P04, M04 |
| `/api/v1/ar/receipts/{id}/allocate` | POST | Apply or re-apply a receipt to open items | P03 |
| `/api/v1/ar/receipts/{id}/reverse` | POST | Reverse a receipt with reason | P03 |
| `/api/v1/ar/open-items` | GET | Customer open-item ledger | P01, P04, P03, M27 |
| `/api/v1/ar/ageing` | GET | Live or snapshot ageing by any dimension | P03, P06, M54 |
| `/api/v1/ar/statements/{customer}` | GET | Statement of account for a period | P01, P04, P03 |
| `/api/v1/ar/credit-profile/{customer}` | GET · PUT | Terms, limit, exposure and hold state | P03, M01, M08, M07 |
| `/api/v1/ar/credit-holds` | POST · DELETE | Place and release a credit hold | P03 |
| `/api/v1/ar/credit-notes` | POST | Request a credit note | P03, P04 |
| `/api/v1/ar/credit-notes/{id}/approve` | POST | Approve and issue | P03 |
| `/api/v1/ar/refunds` | POST | Authorise a refund | P03 |
| `/api/v1/ar/disputes` | POST · GET | Raise, list and update disputes | P01, P04, P03, M27 |
| `/api/v1/ar/collections/worklist` | GET | Prioritised collections worklist | P03 |
| `/api/v1/ar/promises` | POST | Record a promise to pay | P03, M27 |
| `/api/v1/ar/unbilled` | GET | Delivered-but-unbilled exception list | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | R U A | All entities; approves write-offs, refunds and credit notes above threshold |
| R26 Finance Manager | C R U A | All entities; approves credit notes, refunds, holds and write-offs within authority |
| R27 Finance Officer | C R U | Assigned scope; captures receipts, allocates, raises credit-note requests, works collections |
| R29 Cashier / Counter Finance | C R | Own counter and shift; captures receipts and prints invoices only |
| R08 Service Centre Agent | R | Own branch; views invoice and balance to answer a customer, cannot alter |
| R06 Branch Manager | R A | Own branch; releases holds within branch authority, reviews unbilled exceptions |
| R05 Operations Director | R | All branches |
| R21 Sales Manager / R22 Account Manager (Corporate) | R | Assigned accounts; sees exposure, hold state and dispute history, cannot release a hold |
| R28 Warranty Claims Officer | C R U | Claim invoices and their evidence only |
| R34 Contact Centre Agent | R | Customer-facing scope; views invoices and balances, raises disputes, cannot allocate or credit |
| R35 Contact Centre Supervisor | R U | Own queues; may escalate a dispute |
| R32 Quality Manager / ISO Coordinator | R | Credit-note, dispute and write-off registers |
| R33 IT / System Administrator | R | Configuration and technical support; **no financial transaction rights** |
| R36 Customer (individual) | R | Own invoices, receipts, credit notes and balance only (P01) |
| R37 Corporate Portal User | R U | Own company only; Finance sub-role may raise disputes and download statements (P04) |
| R38 Brand Partner | R | Own claim invoices and evidence only (P08) |
| R24 Marketplace Operations Officer | R | Marketplace-originated invoices only |

**Field-level restrictions.** Customer credit limit, risk class, exposure, provision rate and
write-off history are visible only to R01–R05, R26, R27 and R06 (own branch). Counter cashiers
and service agents see invoice totals and balances, never credit or risk data. Customer NID is
masked to all roles except R26, R27 and R03, and every unmasking is logged (AS-14).

**Segregation of duties.**
- **SOD-04 enforced here:** the user who requests a credit note can never approve it — hard block at any value.
- A user may not both capture a receipt and reverse it.
- A user may not both raise a write-off and approve it.
- A user may not both place a customer on credit hold and release them.
- **SOD-08** (create customer + approve their credit limit) is enforced jointly with M33: M20 blocks a credit-limit change by the user who created the customer record.
- R29 Cashier / Counter Finance can capture receipts but can never allocate, credit, refund or write off — the counter never touches the customer's balance except by taking money.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Receivables ageing** | CFO, Finance Manager, Branch Manager | Daily | Balance by bucket, customer, segment, branch, business line and currency |
| **DSO trend** | CFO, CEO | Weekly | Days sales outstanding by entity, segment and business line against the < 32-day target |
| **Delivered-but-unbilled exception list** | CFO, Operations Director, Branch Manager | Daily | Every completed job, contract cycle, rental period or order with no invoice, by age and value — the leakage control |
| **Billable event queue health** | Finance Manager, CTO | Real time | Queue depth, exception count and age, processing latency against the 1-hour target |
| **Invoice generation performance** | CFO, Finance Manager | Weekly | % auto-generated, % within 1 hour, manual-invoice register with reasons |
| **Credit note analysis** | CFO, Quality Manager, CCO | Monthly | Credit notes as % of invoices, by reason code, branch, business line and originating module — the billing-accuracy signal |
| **Dispute register and cycle time** | Finance Manager, Quality Manager, CCO | Weekly | Open disputes by reason, age, value and resolver; outcome distribution |
| **Collections worklist performance** | Finance Manager, CFO | Weekly | Cases worked, promises made and kept, amount recovered, contact effectiveness by channel |
| **Dunning effectiveness** | Finance Manager | Monthly | Payment rate by ladder level and channel; suppression register |
| **Credit hold register** | CFO, CCO, Sales Manager | Weekly | Accounts held, trigger, value blocked, release history and releaser |
| **Receipt matching performance** | Finance Manager, CTO | Weekly | Auto-match rate, exception queue depth and age, unapplied receipt ageing |
| **Channel clearing ageing** | CFO, Treasury (M50) | Daily | Balance per payment channel awaiting settlement, by age — the leading indicator of a gateway reconciliation failure |
| **Warranty claim invoicing** | Warranty Claims Officer, CFO | Weekly | Claims invoiced, evidence completeness, brand settlement ageing and FX exposure |
| **Customer statement pack** | Corporate clients, Account Managers | Monthly | Statement of account per corporate customer |
| **Write-off and provision register** | CFO, auditor, Internal Audit | Monthly | Every write-off with approver and recovery history; provision by band |
| **Revenue by stream, branch and channel** | CEO, CFO, CCO | Monthly | Invoiced revenue across all 14 streams by dimension |
| **Payment method mix** | CFO, CCO, CTO | Monthly | Share by tender type and trend — informs gateway commercial negotiation |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| **KPI-053** | Invoices auto-generated (no manual data entry) | 0% | 100% | **100%** |
| **KPI-054** | Invoice issued within 1 hour of job closure | 3–7 days | 95% | **> 97%** |
| **KPI-055** | Billing accuracy — credit notes as % of invoices | unmeasured | < 2.5% | **< 1.5%** |
| **KPI-056** | Revenue leakage — delivered but unbilled | unknown | < 1.5% | **< 0.5%** |
| **KPI-052** | Days sales outstanding *(jointly with M19)* | unmeasured | 38 | **< 32** |
| — | Receipt auto-match rate | manual | 85% | **≥ 90%** |
| — | Unapplied receipts older than 7 days | unmeasured | < 2% of receipts | **< 0.5%** |
| — | Channel clearing balance older than 3 days | unmeasured | < 5% | **Zero** |
| — | Billable events unprocessed beyond 24 hours | n/a | < 1% | **Zero** |
| — | Overdue receivables as % of total receivables | unmeasured | < 25% | **< 15%** |
| — | Dispute resolution cycle time | unmeasured | < 7 days | **< 3 days** |
| — | Bad-debt write-off as % of revenue | unknown | < 1% | **< 0.4%** |
| — | Invoices delivered successfully on first attempt | unmeasured | 92% | **97%** |
| — | Payments made via embedded payment link | 0% | 35% | **55%** |
| — | Warranty claim invoices issued with complete evidence | unmeasured | 95% | **100%** |
| — | Manual invoices as % of total invoices | 100% | < 3% | **< 1%** |

> **Register note.** KPI-052 … KPI-056 are the canonical identifiers allocated to M20 in `06-02`
> §2.7. The eleven unnumbered metrics are new to this specification and require allocation in
> `06-02` — recorded as audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account` — customer invoices, payment registration, reconciliation, invoice sending, multi-currency | 26% |
| L2 | OCA `account-invoicing` (presentment and validation refinements), `credit-control` (`account_credit_control` — multi-level reminder policies), `account-payment`, `account-financial-reporting` (aged partner balance) | 24% |
| L3 | Free PDF/report and messaging aids | 3% |
| L5 | `cd_billing_engine`, `cd_ar_ext`, `cd_receipt_matching`, `cd_credit_note_refund`, `cd_dunning` | 47% |

> The custom share reflects the fact that the two capabilities that define M20 — the
> billable-event queue that makes 100% auto-invoicing measurable, and the two-stage payment
> model that makes MFS receipts reconcilable — have no L1 or L2 equivalent.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 4 of 5 identifiers below are claimed by another module: **CD-090** also claimed by M59; **CD-161** also claimed by M45, M64; **CD-162** also claimed by M45, M65; **CD-163** also claimed by M46, M66. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-090 | `cd_billing_engine` — billable-event contract and queue, invoice assembly across sources, bilingual rendering, gapless numbering, consolidated and claim invoicing, exception ageing | Odoo module + service | **8 PW** |
| **CD-161** | `cd_ar_ext` — open-item ledger, ageing with immutable snapshots, credit profile, credit limits and holds, deposits and retention, statements | Odoo module | 5 PW |
| **CD-162** | `cd_receipt_matching` — multi-tender capture, channel clearing model, auto-match scoring engine, allocation, unapplied ageing, offline counter capture | Odoo module + service | **6 PW** |
| **CD-163** | `cd_credit_note_refund` — credit-note request and approval with reason taxonomy, statutory document, refund authorisation and M50 instruction, write-off and provision | Odoo module | 3 PW |
| CD-095 | `cd_dunning` — segment-specific ladders, suppression rules, collections worklist, promises, disputes, payment plans | Odoo module | 4 PW |

> **CD register reallocation.** `02-05` §5.2 allocated **CD-090…095** to M20 as
> `cd_billing_engine`, `cd_subscription`, `cd_usage_billing`, `cd_revenue_recognition`,
> `cd_settlement`, `cd_dunning`. Under the v2.1 re-scope: **CD-091** (`cd_subscription`) and
> **CD-092** (`cd_usage_billing`) move to **M39** (Category C); **CD-093**
> (`cd_revenue_recognition`) and **CD-094** (`cd_settlement`) move to **M53**; **CD-090** and
> **CD-095** remain with M20. Three new IDs, **CD-161…163**, are claimed from the Category G
> block defined in `M19` §16.2. **All CD IDs remain provisional** pending the unified CD
> register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M20 is scheduled in **W3** (P0) but declares a dependency on 1 module(s) that land later: **M51** (W4). One of three things must be true before the W3 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W3 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M20 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W3 plan for M20 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M19 General Ledger | Every AR event terminates in a journal entry; the control account and period model must exist |
| M33 Party Master | An invoice without a governed customer record is not collectable |
| M11 Pricing | M20 does not derive prices; the determination service must exist. Before M11 lands in W3, a fixed rate-card fallback is used and is reported as an exception |
| M51 Tax & Regulatory | Tax determination and the Mushak 6.3 format. **M51 is W4 while M20 is W3** — for the W3 window M20 runs against a provisional standard-rate determination stub with the VAT registers reconstructed on M51 go-live. This is a known and accepted sequencing risk, recorded in §18 Q-03 |
| M50 Treasury & Cash | Settlement matching, refund execution and cheque clearance; must go live with M20 |
| M01 / M31 | The primary billable-event source; must be able to publish the event contract |
| M28 Integration | Event outbox and schema registry |
| M29 Identity | SoD service for credit-note and write-off approval separation |

**Delivers into:** M50 (expected receipts), M51 (VAT output registers), M53 (revenue schedules),
M54 (revenue actuals) and every customer-facing portal. **M19, M20, M52 and M50 must go live
together.**

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Open customer invoices at cutover | Estimated 8,000–15,000 open items | `fix.ar.invoice`, `fix.ar.open.item` | W3 cutover |
| Open credit notes and on-account balances | Current only | `fix.ar.credit.note`, `fix.ar.receipt` (unapplied) | W3 cutover |
| Customer credit terms and limits | All corporate and contract accounts | `fix.ar.credit.profile` | W3 minus 1 month |
| Customer deposits and retention money | Current only | `fix.ar.deposit` | W3 cutover |
| Open warranty claim invoices to brands | Per brand, current only | `fix.ar.invoice` (claim type) | W3 cutover, brand-confirmed |
| Open disputes | Current only | `fix.ar.dispute` | W3 cutover |
| Historical invoices | 2 years where recoverable | Warehouse (M62), **not** the operational ledger | W3–W4, best-effort |
| Historical ageing | Not migrated | — | — |

> **Migration position.** Open items migrate at **open-item level, never as a customer balance
> total.** A migrated balance without its underlying invoices cannot be collected, disputed or
> credited, and it destroys ageing accuracy from day one. Every migrated open item must carry
> its original document number and date. The total of migrated open items must reconcile exactly
> to the receivable control account in the M19 opening trial balance before cutover is approved,
> and **each of the top 50 customer balances must be confirmed with the customer** in writing.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | 100% of invoices are generated from billable events with no manual data entry | Production measurement over one full month (KPI-053) |
| AC-02 | More than 97% of invoices are issued within one hour of the billable event | Production measurement over one full month (KPI-054) |
| AC-03 | A billable event produces exactly one invoice, under duplicate delivery, retry and replay | Idempotency test with forced duplicate delivery |
| AC-04 | No billable event can expire unprocessed; every event reaches an invoice, an exception or an approved suppression | Full-queue assertion query plus a negative test |
| AC-05 | Invoice numbering is gapless and sequential per entity and document type, including under concurrent generation and transaction rollback | Concurrency test at 100 parallel generations plus a sequence-continuity audit |
| AC-06 | Every issued tax invoice carries the Company BIN, the determined VAT, and a valid Mushak 6.3 rendering | Statutory format review by the VAT consultant plus a full-table assertion |
| AC-07 | M20 never computes tax; every invoice stores the M51 determination reference | Code review plus a full-table assertion on the determination reference |
| AC-08 | A payment cannot be recorded against a cancelled invoice through any path | Negative test on UI, API and import |
| AC-09 | A cash receipt above the statutory threshold cannot be completed without an NID | Negative test |
| AC-10 | Every non-cash receipt posts to a channel clearing account and never directly to a bank account | Full-table assertion on receipt postings |
| AC-11 | Channel clearing balances age to zero as M50 matches settlements; no balance older than 3 days at steady state | Thirty consecutive days of clearing-account ageing |
| AC-12 | Receipt auto-match rate reaches 90% by count, with all unmatched receipts visible and aged | Production measurement over one month |
| AC-13 | A credit note cannot be approved by the person who requested it, at any value | SoD negative test (SOD-04) |
| AC-14 | A credit note cannot be issued without a reason from the controlled taxonomy | Negative test |
| AC-15 | Refunds execute only through M50 and reconcile to the originating credit note | Scripted scenario across each refund method |
| AC-16 | A credit-limit breach places the account on hold and blocks new billable commitments in M01 and M08 | Scripted scenario |
| AC-17 | Dunning is suppressed for disputed amounts only, not for the whole account, and every suppression is recorded | Scripted scenario |
| AC-18 | The delivered-but-unbilled reconciliation runs daily across all 14 revenue streams and detects a seeded unbilled job within 24 hours | Seeded-defect test |
| AC-19 | Revenue leakage measures below 0.5% of revenue at Wave 8 | Three consecutive monthly reconciliations |
| AC-20 | A warranty claim invoice cannot be issued without the complete evidence set required by that brand | Negative test per brand agreement |
| AC-21 | Period ageing snapshots are immutable and reproduce exactly on re-query | Assertion test after subsequent transactions |
| AC-22 | Counter receipt capture continues through a full connectivity loss and synchronises without loss or duplication | Offline test across 10 counters over three shifts |
| AC-23 | Payment links are single-use, expire, and reject replay or tampering | Security test |
| AC-24 | No card data is present anywhere in the ERP data store | Data scan and PCI-scope review |
| AC-25 | Open items migrate at document level and reconcile exactly to the M19 receivable control account | CFO-signed reconciliation, plus written confirmation from the top 50 customers |
| AC-26 | All customer-facing invoice, receipt and reminder content is complete in Bengali | Translation coverage report (AS-12) |
| AC-27 | CFO and Finance Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 27 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What are the standard payment terms by customer segment — retail, corporate, contract, government, brand partner? Credit policy cannot be configured without them | CFO / CCO | W3 design |
| Q-02 | What credit limits apply, who sets them, and what is the release authority matrix for a credit hold? | CFO / CCO | W3 build |
| Q-03 | **M51 is Wave 4 but M20 is Wave 3.** Is a provisional standard-rate tax determination stub acceptable for the W3 window, with VAT registers reconstructed on M51 go-live — or must M51's determination service be pulled forward? | CFO / CTO | **W3 minus 3 months — blocking** |
| Q-04 | Which corporate accounts bill per job and which bill on a consolidated statement, and on what cycle? | CFO / Account Managers | W3 build |
| Q-05 | What evidence set does each of the 17+ brand partners require on a claim invoice, and in what currency and format? | Warranty Claims Officer / CCO | W3 minus 2 months |
| Q-06 | What is the credit-note reason taxonomy, and who owns it? It is the primary billing-quality signal and must be designed, not accumulated | CFO / Quality Manager | W3 design |
| Q-07 | What are the settlement cycles and reconciliation report formats for bKash, Nagad and SSLCOMMERZ under our current merchant agreements? | CFO / CTO | W3 minus 2 months |
| Q-08 | Is cash refund permitted at a branch counter, and up to what value? | CFO | W3 build |
| Q-09 | What is the write-off authority matrix by value band, and what recovery history must precede a write-off? | CFO | W3 build |
| Q-10 | What are the dunning ladders per segment — timing, channel, tone and escalation — and who signs off the customer-facing wording in Bengali? | CFO / CCO / Marketing Manager | W3 build |
| Q-11 | Are bad-debt provision bands and rates agreed with the external auditor? | CFO / external auditor | W3 design |
| Q-12 | How many years of historical invoices must be available to customer-facing portals, and at what level of detail? | CFO / CCO | W3 minus 2 months |
| Q-13 | Does the business require deposit and retention tracking in Wave 3, or can it follow with M08 contract enhancements? | CFO / Corporate Services Head | W3 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §4 (money flow), §5 (boundary map), §8 (KPIs), §9 (delivery sequence),
§10 (risks) · `M19_Financial_Accounting_and_General_Ledger.md` (posting engine, control
accounts, period model, Category G CD block) · `M50_Treasury_Cash_and_Banking.md` (settlement
matching, refund execution, cheque clearance) · `M51_Tax_and_Regulatory_Compliance_Bangladesh.md`
(tax determination, Mushak 6.3, NID threshold) ·
`M53_Revenue_Recognition_Commission_and_Settlement.md` (revenue schedules from invoices) ·
`M52_Accounts_Payable_and_Employee_Expense.md` ·
`M54_Cost_Accounting_Budgeting_and_FPA.md` (revenue actuals) ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md`
(primary billable-event source) ·
`03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md`
(counter receipts and shifts) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §5 (retired `BIL`
code), §7 · `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` (P01, P04, P08 surfaces) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §6 SOD-04, SOD-08 ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` BRU-FIN-01…04 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §2.7
(KPI-052…056), BO-06

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-002, BR-FIN-003,
BR-FIN-004, BR-FIN-009, BR-FIN-011, BR-FIN-014, BRU-FIN-01…04, BRU-FIN-07 (claim currency),
§Process 6 (As-Is invoicing), §Process 5 (To-Be invoice-to-cash), UC-006, Automation A5 ·
`1000FiX_Services_Company_Profile.md` §Payment Options, §Authorized Service Partnerships,
§Digital Presence

**External benchmark**
SAP S/4HANA FI-AR and SD billing — billing due list, collective billing, multi-level dunning
procedures · SAP FSCM Credit, Collections and Dispute Management — prioritised collections
worklists and disputes as first-class objects ·
[Oracle Fusion Cloud Financials](https://www.oracle.com/erp/financial-management/) —
AutoInvoice, receipt AutoMatch, and the strict separation of invoicing from revenue recognition ·
[Microsoft Dynamics 365 Finance — Accounts Receivable](https://www.randgroup.com/insights/microsoft/dynamics-365/finance-operations/financial-management-in-microsoft-dynamics-365-finance-operations/) —
ageing snapshots and settlement of payments against invoices ·
[Mushak 6.3 tax invoice requirements under VAT & SD Rules 2016 Rule 40(1)](https://rakibhassan.eu/mushak-6-3-vat-invoice-bangladesh/) —
mandatory elements, BIN display, retention ·
[Mushak 9.1 VAT return and its supporting registers](https://rakibhassan.eu/vat-return-bangladesh-mushak-9-1-guide/) —
what an issued invoice must feed ·
[SSLCOMMERZ payment gateway](https://sslcommerz.com/payment-gateway/) and
[bKash merchant payments](https://www.bkash.com/en/business/merchant) — merchant settlement
cycles of T+1 to T+3 that require the two-stage payment model ·
[OCA account-financial-reporting](https://github.com/OCA/account-financial-reporting) — aged
partner balance · OCA `credit-control` — multi-level credit-control policies

---

*Module M20 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
