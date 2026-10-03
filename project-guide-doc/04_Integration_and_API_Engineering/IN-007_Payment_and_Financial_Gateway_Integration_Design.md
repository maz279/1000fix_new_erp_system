---
id: IN-007
title: Payment & Financial Gateway Integration Design
category: 04 — Integration & API Engineering
code: IN
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Integration Architect with Head of Finance Systems
approver: CTO with CFO
standards_basis: >
  PCI DSS v4.0 (scope definition and SAQ applicability) · ISO 20022 (message concepts) ·
  ISO 4217 (currency) · Bangladesh Bank BEFTN Operating Rules ·
  Saga pattern (Garcia-Molina & Salem) · Enterprise Integration Patterns
traces_to: >
  PGD-000 IN-007 · 05-03 §2.1 INT-001…009 · M19, M20, M53 · AP-009 · audit AP-06 (high) ·
  NFR-042, NFR-048, NFR-050 · M28 AC-13 · G3-03 · IN-001 §7.6 · IN-004 §4, §5, §6, §8
depends_on: IN-001 · IN-004 · IN-006 · DA-001 (ledger schema) · AR-008 (aggregates)
verified_on: 2026-08-18
priority: P0
needed_by: W3
enumeration_timestamp: 2026-08-18 17:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-007 — Payment & Financial Gateway Integration Design

### Category 04 · Code `IN` · PCI DSS v4.0 scope · Saga pattern

---

> **Money movement across bKash, Nagad and SSLCOMMERZ with marketplace split settlement is the
> highest-consequence integration in the programme, and it had no design.** `AP-009` provides runbook
> *content* — failure modes, manual fallback, drills, escalation — written against a design that did
> not exist.
>
> **Three commitments cannot all hold** (`AUDIT-016` `AP-06`, high, open). `IN-001-D-02` and
> `IN-001-D-03` ruled the architectural half; **§9 reconciles all three here**, and one of them
> resolves to a **procurement decision, not a design decision**.

---

## 1. Purpose

This document designs the money path: the payment state machine, tokenisation and PCI scope,
idempotency and its 7-day window, the read-back rule per rail, refunds and reversals, marketplace
split settlement, COD custody, ledger posting rules, reconciliation, and the failure semantics that
keep money correct when a rail is unavailable.

It exists because **every other document in this category treats a payment as an integration.** It is
not. It is a **distributed transaction across systems that cannot be rolled back**, and the design
question is not "how do we call the gateway" but "what is true when the call's outcome is unknown."

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The payment **state machine**, and why it has no terminal `failed` from `executing` |
| 2 | **PCI DSS scope boundary** — what the estate must never touch |
| 3 | Tokenisation and credential custody per rail |
| 4 | **Idempotency on the money path**, and why 7 days |
| 5 | The **read-back rule** per rail, and the reconciliation when records disagree |
| 6 | Refunds, partial refunds, reversals and chargebacks |
| 7 | **Marketplace split settlement** — the hardest flow in the estate |
| 8 | **COD custody** — cash collected by a courier is our money in their hands |
| 9 | Ledger posting rules and the `LB-04` boundary |
| 10 | **The `AP-06` reconciliation** — all three commitments |
| 11 | Reconciliation jobs, breaks and their treatment |
| 12 | Payout execution: BEFTN, seller payouts, refunds |
| 13 | Gates `FF-85`…`FF-94` |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Wire contracts per rail | **`IN-004`** §4, §5, §6 | The ICD is the bilateral contract; this is the design that uses it |
| Webhook signature and read-back mechanics | **`IN-006`** | Common across all inbound webhooks |
| Ledger schema, chart of accounts, journal structure | `DA-001`, M19 | This states **when** a posting occurs and what it must contain |
| Tax calculation and VAT return generation | M51, `IN-004` §7 | `INT-038` is a batch filing, not a payment |
| Pricing, discounting, commission calculation | M11, M53 | This settles what they compute |
| Credit control and collections | M20 | Downstream of receipt |
| Fraud scoring | M26, `SC-*` | Named as a hook; not designed here |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **CTO and CFO** | §9 is the reconciliation they must decide, and §9.3 is a **procurement** decision |
| Payment engineers | §3–§8 are the build specification |
| Finance systems | §10's posting rules and §11's reconciliation |
| Treasury | §12's payout execution and the BEFTN dependency |
| QA lead | §13's gates and every §'s failure table |
| Service desk | `AP-009`'s runbook content now has a design to describe |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **PCI DSS v4.0** | §4 defines the scope boundary and the SAQ position per rail | **Not a certification claim.** §4.4 states what must be assessed and by whom |
| **ISO 20022** | Message *concepts* — end-to-end id, instruction id, remittance information — inform §5 and §12 | **The estate does not exchange ISO 20022 messages.** BEFTN uses a fixed-width national format |
| **ISO 4217** | Currency codes; `Money` is `{amount: string-decimal, currency}` | None |
| **BEFTN Operating Rules** | §12.2's file structure and SEC codes | Mediated by the sponsoring bank (`IN-004` §8) |
| **Saga pattern** | §7's split settlement and §6's compensating reversals | None |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `05-03` §2.1 | `INT-001`…`INT-009` — nine payment integrations, four of them P0 |
| `IN-004` §4, §5, §6, §8, §9 | **The wire contracts.** bKash's 30 s timeout, SSLCOMMERZ's mandatory validation call, Nagad's RSA position, BEFTN's counterparty correction |
| `AP-009` | Runbook content: failure modes, manual fallback, drills, escalation — **the operational half** |
| `AUDIT-016` `AP-06` | The three irreconcilable commitments |
| `NFR-042`, `NFR-048`, `NFR-050` | 3 s p95 · 99.95% with multi-gateway failover · tested manual fallback |
| `M28` `AC-13` | Automatic fallback within 2 minutes |
| `06-02` `G3-03` | **bKash, Nagad and card payments live and reconciling at the W3 gate** |
| `AR-001` `LB-04` | **Financial postings originate only in category G** |
| `IN-001` §6, §7.6 | Idempotency semantics; the failover ruling |

### 2.3 Audit findings this document closes

| Finding | Disposition |
|---|---|
| **`AP-06` (high)** — three payment availability commitments do not reconcile | **§9 reconciles all three.** Two are design rulings (`IN-001-D-02`, `IN-001-D-03`); **the third is a procurement decision the CFO must take** |
| `AP-009` `O-01` | The design `AP-009`'s runbook content describes |
| `IN-001` `FB-05` — `INT-003` has no failover | §9.3 — stated, quantified, and escalated |
| `IN-001` §9.2 — `/api/v1/payments/confirm` is declared by no module | **Assigned to M20** and issued in `IN-002_artefacts/finance/openapi.yaml` |
| `IN-003` §7.3.4 — `payment.received` is published by no module | **Assigned to M20**, `RE-02`, W1 |

---

## 3. The Payment State Machine

### 3.1 States

| State | Meaning | Terminal |
|---|---|:--:|
| `initiated` | Our record exists; the rail has not been called | |
| `awaiting_customer` | The rail holds a session; the customer must act | |
| **`executing`** | We have called the rail and **do not yet know the outcome** | |
| **`unknown`** | The call timed out or errored **without a determinate result** | |
| `received` | **Read-back confirms funds** | |
| `failed` | **Read-back confirms failure** | ✔ |
| `reversed` | Confirmed, then reversed by the rail | ✔ |
| `refunded` / `part_refunded` | Refund executed | ✔ |
| `abandoned` | Session expired with no customer action | ✔ |

### 3.2 The state that matters

> **`unknown` is a first-class state, and its absence is the defect most payment integrations
> ship with.**
>
> A timeout is not a failure. bKash's own guidance sets a **30-second** client timeout; a call that
> exceeds it has told us **nothing** about whether money moved. A system that maps timeout → `failed`
> will:
>
> - show the customer a failure for a payment that succeeded;
> - permit a second payment attempt against an already-paid invoice;
> - reconcile short against the rail's settlement file the next morning.
>
> **`unknown` exits only through read-back** (§5), never through elapsed time, never through a
> customer complaint, and never through an operator's judgement.

### 3.3 Transitions

| From | To | Trigger |
|---|---|---|
| `initiated` | `awaiting_customer` | Rail session created |
| `awaiting_customer` | `executing` | Customer approved; execute called |
| `awaiting_customer` | `abandoned` | Session expiry |
| `executing` | `received` | **Read-back confirms** |
| `executing` | `failed` | **Read-back confirms failure** |
| `executing` | **`unknown`** | **Timeout, connection failure, or an indeterminate response** |
| **`unknown`** | `received` / `failed` | **Read-back only** |
| `received` | `reversed` | Rail-initiated reversal |
| `received` | `refunded` / `part_refunded` | Refund executed (§6) |

**No transition out of `unknown` exists that is not a read-back.** `FF-85`.

### 3.4 What the customer sees in `unknown`

| Never | Always |
|---|---|
| "Payment failed" | **"We are confirming your payment"** |
| A retry button | A status that refreshes |
| A second charge | The order preserved, unbilled |

`AP-006`'s remediation copy standard (`EP-02`) requires every error to state a remedy the caller can
act on. **In `unknown` the honest remedy is "wait", and saying so is better than a false failure.**

---

## 4. PCI DSS Scope

### 4.1 The boundary

> **`PCI-01`. The estate never receives, transmits, processes or stores a primary account number,
> CVV, magnetic-stripe data or a PIN block. Ever.**

| Rail | Card data path | Our exposure |
|---|---|---|
| **SSLCOMMERZ** (`INT-003`) | Customer enters card details **on the acquirer's hosted page** | **None** — we hold a transaction reference only |
| bKash, Nagad, Rocket | Wallet rails; **no card data exists** | None |
| BEFTN, bank statement | Bank account numbers — **not card data**, but sensitive | Bank account is personal/financial data under the PDPO, not PCI |
| International gateway (`INT-008`, W9, P3) | Hosted page, same as SSLCOMMERZ | None |

### 4.2 The consequences of holding the boundary

| # | Rule |
|---|---|
| **PCI-02** | Card entry is **always** on the acquirer's hosted page or SDK. **No 1000FiX surface renders a card-number field** — not the customer portal, not the agent console, not the branch till |
| **PCI-03** | **A contact-centre agent never asks a customer to read out a card number.** The agent sends a payment link. This is an operational rule with a technical enforcement: no field exists to type it into |
| **PCI-04** | A rail's token is stored; **no token is used to derive card data**, and a token is scoped to one merchant and one rail |
| **PCI-05** | Logs, traces, DLQ entries and error bodies are **scanned for PAN patterns**; a match is a security incident (`FF-90`) |
| **PCI-06** | Screenshots and screen recordings in support tooling **exclude the acquirer's iframe** |

### 4.3 Why this is worth stating as a design rule

**Every card-data breach in the estate's risk register would be prevented by `PCI-02`, and the only
way `PCI-02` fails is by someone adding a convenient field.** A design that states "we are out of
scope" without stating *what would put us in scope* is a design that drifts into scope in Wave 6.

### 4.4 What must still be assessed

| # | Item | Owner | Wave |
|---|---|---|:--:|
| 1 | **SAQ applicability determination** — which self-assessment questionnaire applies given hosted-page redirect vs iframe | CFO + Security Lead | **W3 − 3 months** |
| 2 | The acquirer's own attestation of compliance, obtained and retained | Finance | W3 |
| 3 | Confirmation that the **hosted-page integration mode** chosen matches the SAQ assumed | Integration Architect | W3 |

> **`IN-A-23` (medium).** Redirect and iframe integration modes carry **different SAQ obligations**,
> and `05-03` does not state which mode `INT-003` uses. The choice is an engineering decision with a
> compliance consequence, and it must be made deliberately rather than discovered during assessment.

---

## 5. Idempotency and Read-Back

### 5.1 Three keys, three owners

| Layer | Key | Owned by | Lifetime |
|---|---|---|---|
| Our API | `Idempotency-Key`, client UUID | The caller | **7 days** |
| Our record | `payment_id` | Us | Permanent |
| The rail | `merchantInvoiceNumber` / `tran_id` / order id | **Us, but meaningful to them** | Permanent |
| The rail's own | `paymentID` / rail transaction id | **Them** | Permanent |

**All four are persisted and cross-referenced.** A reconciliation that can only join on one of them
cannot resolve a break.

### 5.2 Why 7 days

`AP-006`'s `idempotency.key_expired` says, verbatim: *"Treat the outcome as unknown and reconcile
before resubmitting. **Never blind-resubmit a payment or a payout.**"*

| Window | Consequence |
|---|---|
| 24 h (the general default) | A partner whose integration was down over a weekend **cannot safely retry**; the only remaining option is human reconciliation against the rail |
| **7 days** | Covers the realistic outage-and-recovery envelope |
| Cost | Storage of a response body per money operation for a week. **Trivial** |
| Cost of the alternative | **A double payment.** Not trivial |

### 5.3 The merchant reference must not leak

| # | Rule |
|---|---|
| **MR-01** | `merchantInvoiceNumber` is **stable across retries** — a new value is a new payment |
| **MR-02** | It **must not encode a customer identifier**, a phone number or an invoice total. It travels to a third party and appears in their statements and support tooling (`IP-10`) |
| **MR-03** | It is **unique across all rails**, so a reconciliation joining across rails cannot collide |

### 5.4 Read-back, per rail

`IN-001` `PT-05` and `IN-006` §8.2 give the eight-step contract. Per rail:

| Rail | Read-back call | Why it is the authority |
|---|---|---|
| **bKash** | `POST /tokenized/checkout/payment/status` | The documented flow is `create → execute → **query**` |
| **SSLCOMMERZ** | **Transaction Validation API**, returning `VALID` / `FAILED` / `CANCELLED` | Its published integration requirement. The IPN's **MD5** `verify_sign` is a filter, not the authority — **MD5 is not collision-resistant** (`IN-004` `IN-A-15`) |
| **Nagad** | Status query, with **RSA response-signature verification** | A signature failure here is an **integrity event**, not a payment failure, and must not share an error code |
| **Rocket** (via aggregator) | The aggregator's status call | Two hops; the aggregator is the counterparty |

### 5.5 When our record and the rail disagree

> **`PAY-01`. The rail wins. Always. Without exception.**

| Situation | Action |
|---|---|
| We say `received`, rail says failed | **Reverse our record**, publish `payment.reversed`, raise a break, notify Finance |
| We say `failed`/`unknown`, rail says paid | **Move to `received`**, post to the ledger, notify the customer, raise a break |
| Amounts differ | **The rail's amount is authoritative.** Raise a break; **never adjust silently** |
| The rail has no record of our reference | Treat as `failed` **only after** a second read at least 5 minutes later — a rail's read replica may lag |

**Every divergence publishes `platform.reconciliation_divergence` and creates a break (§11).
A break is closed by a human, never by a job.**

---

## 6. Refunds, Reversals and Chargebacks

### 6.1 Three different things

| | **Refund** | **Reversal** | **Chargeback** |
|---|---|---|---|
| Initiated by | Us | The rail | The customer, via their issuer |
| Trigger | A business decision | A rail-side correction | A dispute |
| Our control | Full | None | None — we respond |
| Ledger effect | Contra-posting | Contra-posting | Contra-posting **plus a fee** |
| Timing | Immediate to days | Any time | **Weeks to months later** |

> **Conflating them is the classic reconciliation defect.** A reversal booked as a refund loses the
> distinction between "we chose to return money" and "the rail took it back", and the two have
> different accounting treatment and different operational responses.

### 6.2 Refund rules

| # | Rule |
|---|---|
| **RF-01** | A refund is a **new object with its own idempotency key**, not a mutation of the payment |
| **RF-02** | A refund **may never exceed** the sum received less refunds already issued. Enforced server-side (`FF-86`) |
| **RF-03** | Partial refunds are permitted and **enumerated against invoice lines** — a refund with no line attribution cannot be reconciled to revenue |
| **RF-04** | A refund follows the **original rail**. Cross-rail refunds are forbidden — a bKash payment is not refunded to a card |
| **RF-05** | **Approval is required above a threshold**, with `approve` scope separate from `write` (`IN-005` `SC-05`, `SOD-*`) |
| **RF-06** | A refund on an `unknown` payment is **refused**. Resolve the payment first (§3.2) |
| **RF-07** | Refund execution is **`R3` on replay** (`IN-003` §8.3) — the replay service refuses it without a named operator override |

### 6.3 Chargebacks

| # | Rule |
|---|---|
| **CB-01** | A chargeback arrives **weeks or months after** the payment, often after the service order has closed. **The design must not assume the order is open** |
| **CB-02** | It creates a **receivable against the customer**, not a reversal of revenue — the service was delivered |
| **CB-03** | Evidence assembly — service order, handover signature, delivery evidence — is a **defined operational flow with a deadline set by the acquirer** |
| **CB-04** | The chargeback **fee** is a separate cost line, not netted against the disputed amount |
| **CB-05** | Chargeback rate is a **monitored metric**; acquirers impose thresholds |

> **`IN-A-24` (medium). No module specification declares a chargeback flow.** M20 covers receivables
> and collections; `05-03` §2.1 lists no chargeback integration; no `dispute.*` event names a card
> dispute as distinct from a marketplace dispute. **A chargeback is the one money movement that
> arrives entirely outside our control, after the transaction is closed, with a deadline** — and it
> has no owner. Referred to M20 and `RQ-009`.

---

## 7. Marketplace Split Settlement

### 7.1 Why this is the hardest flow in the estate

A marketplace job involves **one customer payment** and **two or more recipients** — the seller, and
1000FiX's commission — with a **hold period** between them, and 500–2,000 sellers at steady state.

```
Customer pays 5,000 BDT
    │
    ├─ received into a 1000FiX-controlled account          (funds are OURS in law)
    │
    ├─ commission 750 BDT recognised (M53)                 (revenue)
    ├─ seller entitlement 4,250 BDT accrued                (LIABILITY — not revenue)
    │
    │   … hold period: dispute window, quality gate …
    │
    └─ payout batch → seller's bank / wallet               (liability discharged)
```

### 7.2 The rules that keep it correct

| # | Rule | Why |
|---|---|---|
| **MS-01** | **Funds received on a marketplace job are a liability, not revenue**, until the entitlement is released. Only the commission is revenue at receipt | Booking the gross as revenue overstates it by the seller's share and creates a tax exposure |
| **MS-02** | The seller's entitlement is an **accrued payable per job**, individually traceable to the payment that funded it | A pooled balance cannot answer "which jobs is this payout for?", which is the first question a seller asks |
| **MS-03** | **The hold period is a state, not a delay.** `held` → `releasable` → `released` → `paid`, each with a trigger and an owner | |
| **MS-04** | A dispute (`dispute.raised`) **freezes** the entitlement. It cannot be paid while frozen | |
| **MS-05** | A refund to the customer **claws back** the entitlement — from the accrual if unpaid, or as a **negative entitlement** against future payouts if already paid | The clawback case is what makes MS-02's per-job traceability necessary |
| **MS-06** | A payout batch is a **saga with compensations**: reserve → generate file → transmit → acknowledge → mark paid. **A failure at any step is compensated, never left half-applied** | `PT-06` |
| **MS-07** | **A seller is never paid from an unreconciled receipt.** The payment must be `received` and confirmed by read-back | Otherwise a failed payment funds a real payout |
| **MS-08** | Payout execution is **`R3` on replay** | A replayed payout batch pays every seller twice |

### 7.3 The seller-facing obligation

| # | Requirement |
|---|---|
| A seller can see, per job: gross, commission, deductions, net, hold state and expected payout date | `P07` |
| A statement reconciles to the payout to the taka | A statement that does not reconcile generates a support ticket per seller, at 500–2,000 sellers |
| Every deduction names its reason and its rule | `AP-006` `rule` and `rule_class` |

### 7.4 What is not designed here

`INT-007` (seller payout rail, W7, P1) is assigned `CD-242` in the technology map. **The rail itself
is not selected**, and `IN-004` §20 defers its ICD to W6. §12.3 states what the design requires of
it, so the selection is made against a specification rather than a brochure.

---

## 8. Cash on Delivery

### 8.1 The exposure nobody has designed

Pick-and-drop consignments through Pathao, RedX and Steadfast (`INT-024`…`026`, W3) carry a **COD
amount**. Cash collected by a courier is **our money in a third party's hands**, and the courier
remits it later, in aggregate, net of their fees.

| # | Rule | Why |
|---|---|---|
| **COD-01** | A COD amount is a **receivable from the courier** the moment they confirm collection — not from the customer, who has paid | The customer's obligation is discharged; the courier's begins |
| **COD-02** | Each consignment's COD amount and its remitted state are **ICD fields** (`IN-004` §17) | |
| **COD-03** | Courier remittances arrive **aggregated**. Reconciliation is **remittance line → consignment**, and it is many-to-one | |
| **COD-04** | A **remittance shortfall** is a break against the courier, escalated commercially, never written off by a job | |
| **COD-05** | Courier fees are a **separate cost line**, not netted into the receipt | Netting loses the gross revenue figure |
| **COD-06** | **Ageing on unremitted COD is monitored.** An unremitted balance beyond the contracted remittance window is a credit exposure | |

> **`IN-A-25` (high). COD reconciliation is not designed anywhere in the estate.** `05-03` §2.3
> catalogues the three couriers as logistics integrations, and `AP-009` covers payment-gateway
> runbook content but not courier cash. **At W3 pick-and-drop volume, unremitted COD is a working
> capital exposure with no owner, no ageing report and no break process.** Referred to M20 and M03,
> owner CFO, needed **W3**.

---

## 9. The `AP-06` Reconciliation

**All three commitments, resolved.**

### 9.1 Commitment 1 — `NFR-042`: payment confirmation ≤ 3 s p95

| Position | |
|---|---|
| **The conflict** | bKash's own integration guidance instructs merchants to set a **30-second** API timeout. A rail whose provider expects 30 s cannot be confirmed inside a 3 s p95 **end to end** |
| **Resolution** | **`IN-001-D-03`.** Restated as **two numbers**: internal processing ≤ 3 s p95 **excluding third-party call time**, plus a **published per-rail end-to-end expectation** |
| **Per-rail figures** | bKash up to 30 s · Nagad up to 20 s · SSLCOMMERZ up to 15 s (`IN-004` §4.4, §5.3, §6.3) |
| **Who must act** | **`RQ-006` owner** — `05-06`'s `NFR-042` row is corrected. Raised as `IN-A-05` |
| **Status** | **Resolved by design ruling** |

### 9.2 Commitment 2 — `M28` `AC-13`: fallback within 2 minutes

| Position | |
|---|---|
| **The conflict** | `05-03` §7 detects unavailability at *< 99% over 15 minutes* and error rate at *> 2% over 5 minutes*. **A 5-minute detection window cannot produce a 2-minute failover** |
| **Resolution** | **`IN-001-D-02`.** The **circuit breaker** engages the fallback — seconds, on ~50% failures over 20 calls. The `05-03` §7 windows are **alerting thresholds**, and its heading is corrected to *"Integration Monitoring and Alerting"* |
| **Status** | **Resolved by design ruling.** `AC-13`'s 2 minutes is comfortably met by a breaker measured in seconds |

### 9.3 Commitment 3 — `NFR-048`: 99.95% with multi-gateway failover

| Position | |
|---|---|
| **The conflict** | 99.95% is ~**22 minutes of downtime per month**. **`INT-003` is the only card acquirer in the entire 47-integration catalogue**, so **for card payments there is no failover to be had** |
| **Why this one is different** | The first two were design errors. **This is not a design error.** No architecture makes a single acquirer redundant |
| **The two options** | **(a) Procure a second card acquirer** — cost, contract, integration, certification, and a second ICD. **(b) Restate `NFR-048`** as applying to the **aggregate payment path** — customers can pay by bKash, Nagad or cash when cards are down — rather than to every method |
| **What (b) actually concedes** | That a card outage is a **degraded** service, not an outage: wallet-capable customers are unaffected; card-only customers cannot pay online and are offered cash at counter |
| **Who must decide** | **CTO and CFO.** `IN-001` Q-05, `IN-004` Q-03 |
| **By when** | **W3.** `G3-03` requires bKash, Nagad **and card** payments live and reconciling at the W3 gate |
| **Status** | **UNRESOLVED — and it cannot be resolved here.** It is a procurement and risk-appetite decision |

> **This is the honest outcome, and it is worth being explicit about.** Two of `AP-06`'s three limbs
> were reconcilable by ruling. **The third is a commercial decision that an engineering document can
> frame but must not pre-empt.** Recording it as "resolved" would be exactly the defect `PGD-A2-06`
> warned about — reporting a gap closed when it is open.

### 9.4 What the wave-3 gate should therefore assess

| Criterion | Evidence |
|---|---|
| bKash, Nagad, card **live and reconciling** (`G3-03`) | Reconciliation run, zero unexplained breaks over 7 days |
| Fallback **exercised**, not merely documented (`NFR-050`) | A drill record per P0 rail (`IN-001` `FB-02`) |
| `NFR-042` restated, or accepted with per-rail figures | `RQ-006` change record |
| `NFR-048` restated, **or** a second acquirer contracted | **CFO decision recorded in `GV-003`** |
| **`unknown`-state handling** demonstrated under induced timeout | A test that times out `execute` and shows read-back resolution |

---

## 10. Ledger Posting

### 10.1 The boundary

`AR-001` `LB-04`: **financial postings originate only in category G.** Other categories raise
**billable events**; they never write journal entries.

| Who | Does |
|---|---|
| M01 | Publishes `service_order.delivered` with a `billable_summary` |
| M20 | Consumes it, raises an invoice, and **posts** |
| **Nothing else** | Writes to the ledger. Checked by `FF-05` |

### 10.2 Posting rules

| # | Rule |
|---|---|
| **LP-01** | A posting occurs on a **confirmed** event, never on an initiated one. `received` posts; `executing` and `unknown` do not |
| **LP-02** | Every posting carries the **payment id, rail, rail transaction id and `merchantInvoiceNumber`** — the four keys §5.1 requires for reconciliation |
| **LP-03** | **Money is a string decimal with an explicit currency.** No float reaches the ledger (AS-10) |
| **LP-04** | A marketplace receipt posts **commission to revenue and the seller share to a liability** (`MS-01`), never gross to revenue |
| **LP-05** | Rail fees post as a **cost**, not as a reduction of revenue |
| **LP-06** | A posting into a **closed period** is refused — `422 state.period_closed` — and routed to the current period or to Finance |
| **LP-07** | Every posting is **reversible only by a contra-posting**. No posting is edited or deleted |

---

## 11. Reconciliation

### 11.1 The four runs

| # | Run | Frequency | Compares |
|---|---|---|---|
| **R-01** | **Rail settlement** | Daily | Our `received` payments against each rail's settlement report |
| **R-02** | **Bank statement** (`INT-006`) | Daily | Bank credits against expected settlements |
| **R-03** | **Seller payout** | Per batch | Entitlements released against the payout file and the bank debit |
| **R-04** | **COD remittance** | Per remittance | Courier remittance lines against consignment COD amounts (§8) |

### 11.2 Breaks

| # | Rule |
|---|---|
| **BR-01** | Any difference is a **break** with an owner, an age and a state. Not a log line |
| **BR-02** | **A break is closed by a human**, with a stated reason. **Never by a job** |
| **BR-03** | Breaks are **aged**, and ageing is reported to the CFO. An unexplained break older than the reporting cycle is an audit finding |
| **BR-04** | A break may **never** be closed by adjusting our record to match without a stated cause — `PAY-01` says the rail wins, and the *reason* it won must be recorded |
| **BR-05** | Reconciliation runs publish `platform.reconciliation_divergence` on any non-zero break count |

### 11.3 Why the counts matter more than the amounts

> A reconciliation that matches on **total amount** and not on **transaction count** will pass while
> two errors cancel. `05-03` §3.4's nightly portal reconciliation compares **counts** for exactly
> this reason, and `AUDIT-016` `AP-18` is the estate's own worked example of two cancelling errors
> producing a green tick over an unverified claim. **Every run in §11.1 reconciles both count and
> amount, and reports them separately.**

---

## 12. Payout Execution

### 12.1 Three payout paths

| Path | `INT` | Rail | Wave |
|---|---|---|:--:|
| **Payroll and vendor disbursement** | `INT-005` | BEFTN via the sponsoring bank | W5 |
| **Marketplace seller payouts** | `INT-007` | Not selected | W7 |
| **Customer refunds** | `INT-001`…`003` | The original rail (`RF-04`) | W3 |

### 12.2 BEFTN — what the design must carry

Per `IN-004` §8, and subject to **which bank** (`IN-001` Q-07, unanswered):

| # | Requirement |
|---|---|
| Fixed-width file: file header, batch header, entry detail, control records; three-digit **SEC codes** |
| **Control totals** — count and value — verified on generation **and** on acknowledgement. Mismatch rejects the **whole file** |
| A **freeze point** owned by Payroll/Treasury as a business decision |
| **Monotonic sequence number**; a gap is an incident |
| Returns and rejections have a **declared reconciliation window** with an alert when it lapses |
| File and acknowledgement retained **immutably**, 7 years |
| **Manual submission through the bank's portal is the fallback**, exercised before the first live run |

> **`IN-A-16`, restated: half a payroll run is worse than none.** It is a same-day treasury and
> employee-relations incident with no clean reversal, which is why `PT-06` — never partially
> applied — is absolute here.

### 12.3 What the seller payout rail must provide

Stated so `INT-007`'s selection is made against a specification:

| # | Requirement |
|---|---|
| Per-recipient status, not just per-batch — **a batch that "succeeded" with three failed lines is three unpaid sellers** |
| Idempotent batch submission with our own batch reference |
| A **query** call for read-back, per `PT-05` |
| Reversal or recall for a mis-sent payout, or a documented statement that none exists |
| Failure reasons that map to actionable seller remediation — wrong account, closed account, name mismatch |
| Support for **500–2,000 recipients** in a batch, at the frequency the hold period implies |

---

## 13. Gates

| # | Check | Timing | Enforcement |
|---|---|---|---|
| **FF-85** | **No transition out of `unknown` exists that is not a read-back** | CI static analysis | Fail |
| **FF-86** | Cumulative refunds never exceed the confirmed receipt (`RF-02`) | Runtime + CI | Block |
| **FF-87** | No ledger posting occurs from a payment state other than `received` (`LP-01`) | CI + runtime | Fail |
| **FF-88** | Every posting carries all four reconciliation keys (`LP-02`) | CI | Fail |
| **FF-89** | **No card-number-shaped field exists in any request schema, response schema or UI form** (`PCI-02`) | CI static analysis | Fail |
| **FF-90** | No PAN-pattern string appears in a log, trace, DLQ entry or error body (`PCI-05`) | Log scanning | Alert + incident |
| **FF-91** | Marketplace gross is never posted to revenue (`MS-01`) | CI on posting rules | Fail |
| **FF-92** | Payout and refund consumers are declared **`R3`** in the `IN-003` registry (`MS-08`, `RF-07`) | CI | Fail |
| **FF-93** | Every P0 rail has a **drill record within the current wave** (`NFR-050`, `FB-02`) | Wave gate | Fail |
| **FF-94** | Every reconciliation run reports **count and amount separately** (§11.3) | CI on report definitions | Fail |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-007-D-01` | Timeout handling | Map to `failed` · **first-class `unknown` state** | **`unknown`** | A timeout tells us nothing about whether money moved; mapping it to `failed` produces double charges and short reconciliations | §3.2; `FF-85` |
| `IN-007-D-02` | Disagreement with a rail | Our record wins · **the rail wins, always** | **The rail wins** | We are not the system of record for money that sits in their account | `PAY-01`; every divergence raises a break |
| `IN-007-D-03` | Money idempotency window | 24 h · **7 days** | **7 days** | Covers a weekend outage; storage is trivial, a double payment is not | `IN-001` `ID-08`; `x-idempotency-retention: P7D` |
| `IN-007-D-04` | Card data | Hosted page · iframe · direct capture | **Hosted page / SDK; never direct capture** | Keeps PCI scope minimal and makes drift into scope require adding a field that does not exist | `PCI-01`…`PCI-06`; `FF-89` |
| `IN-007-D-05` | Marketplace receipts | Gross to revenue · **commission to revenue, seller share to liability** | **Liability** | Gross overstates revenue by the seller's share and creates a tax exposure | `MS-01`; `FF-91` |
| `IN-007-D-06` | Refund shape | Mutate the payment · **a new object with its own key** | **New object** | Partial refunds, clawbacks and reversals all need independent identity and their own idempotency | `RF-01` |
| `IN-007-D-07` | Reconciliation basis | Amount · **count and amount, reported separately** | **Both** | Amount-only reconciliation passes while two errors cancel — the estate's own `AP-18` | `FF-94` |
| `IN-007-D-08` | `NFR-048` | Assert compliance · **escalate as a procurement decision** | **Escalate** | No architecture makes a single acquirer redundant. Recording it as resolved would report a closed gap that is open | §9.3; CFO decision in `GV-003` |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Second card acquirer, or restate `NFR-048`?** (`AP-06` limb 3, §9.3) | **CTO + CFO** | **W3** | `G3-03`, `NFR-048`, `IN-004` §6.2 |
| Q-02 | **Which bank sponsors BEFTN, and what is its file specification?** | CFO + Treasury | **W5 − 4 months** | §12.2, `CD-100` |
| Q-03 | **Which SAQ applies**, and does the chosen integration mode match it? (`IN-A-23`) | CFO + Security Lead | **W3 − 3 months** | §4.4 |
| Q-04 | **Who owns the chargeback flow?** No module declares one (`IN-A-24`) | CFO with M20 owner | W3 | §6.3 |
| Q-05 | **Who owns COD remittance reconciliation and its ageing?** (`IN-A-25`) | **CFO with M03, M20** | **W3** | §8, W3 pick-and-drop |
| Q-06 | What is the **hold period** for marketplace entitlements, and who sets it? | Commercial Director | W6 | §7.2 `MS-03` |
| Q-07 | Which **seller payout rail** (`INT-007`), assessed against §12.3? | CFO + Integration Architect | **W6** | W7 payouts, `IN-004` §20 |
| Q-08 | Is there a **fraud-scoring hook** before execution, or is fraud handled post hoc? | Security Lead + M26 | W4 | Design of the `executing` transition |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A payment state machine exists with an explicit **`unknown`** state | §3.1, §3.2 |
| AC-02 | The PCI scope boundary is stated **with what would breach it** | §4.1, §4.2, §4.3 |
| AC-03 | Idempotency on the money path is specified, including **why 7 days** | §5.2 |
| AC-04 | Read-back is specified **per rail**, with the reason each is authoritative | §5.4 |
| AC-05 | Disagreement with a rail has a single, absolute rule | `PAY-01` |
| AC-06 | Refund, reversal and chargeback are distinguished | §6.1 |
| AC-07 | Marketplace split settlement is designed, including **clawback** | §7 |
| AC-08 | **COD custody is designed**, and the gap it exposes is raised | §8, `IN-A-25` |
| AC-09 | **All three `AP-06` commitments are addressed**, and the unresolvable one is **named as unresolved** | §9, `IN-007-D-08` |
| AC-10 | Ledger posting respects `LB-04` and carries the reconciliation keys | §10 |
| AC-11 | Reconciliation reports **count and amount separately** | §11.3, `FF-94` |
| AC-12 | Payout execution states what an unselected rail must provide | §12.3 |

**Definition of done.** Complete when every criterion is met, **Q-01 is decided by the CFO and
recorded in `GV-003`**, Q-02 and Q-03 are answered, `FF-85`…`FF-94` are enabled, one fallback drill
per P0 rail is recorded, and `PGD-000`'s `IN-007` row carries a fresh enumeration timestamp.
**`AP-06` closes only when Q-01 is decided — two of its three limbs are closed by this document; the
third is not an engineering decision.**

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`IN-001`** §6, §7.6 | Idempotency semantics; `IN-001-D-02` and `-D-03`, which resolve two of `AP-06`'s limbs |
| Upstream | **`IN-004`** §4, §5, §6, §8, §9 | The wire contracts and the per-rail timing this design assumes |
| Upstream | **`IN-006`** §8 | Read-back mechanics and per-provider verification |
| Upstream | `AR-001` `LB-04` | Postings originate only in category G |
| Upstream | `DA-001` | Ledger schema — **⛔, and this document depends on it** |
| Downstream | `IN-002` `finance` context | `initiatePayment`, `confirmPayment`, `exportInvoices` realise this design |
| Downstream | `IN-003` | `payment.received`, `payment.reversed`, `refund.completed`, `settlement.*` registrations |
| Downstream | `IN-008` | Rail certification, sandbox test cards, induced-timeout tests |
| Downstream | `AP-009` | The runbook content now has a design to describe |
| Downstream | `SV-*`, `OP-014` | Manual fallback procedures |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §2.1, §7 | The nine payment integrations; **§7's heading corrected by `IN-001-D-02`** |
| Lateral | `../../1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M20_*.md`, `M53_*.md` | Receivables and settlement |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-001_Integration_Architecture_Specification.md`](./IN-001_Integration_Architecture_Specification.md) ·
[`./IN-004_Interface_Control_Documents.md`](./IN-004_Interface_Control_Documents.md) ·
[`./IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](./IN-006_Webhook_Callback_and_Partner_Push_Specification.md) ·
[`./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md) ·
[`./IN-002_artefacts/finance/openapi.yaml`](./IN-002_artefacts/finance/openapi.yaml)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §2.1, §7 ·
`../../1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M20_*.md`, `M53_*.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_*.md` `G3-03` ·
`../../project_content/_AUDIT/AUDIT-016_*.md` `AP-06` ·
`../../project_content/15_Integration_and_Developer_Content/AP-009_*.md`

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| PCI DSS v4.0 | Scope definition; SAQ applicability depends on the integration mode | 2026-08-18 |
| bKash Tokenized Checkout API Integration Guide | `token/grant` → `create` → `execute` → `payment/status` → `refund`; **30 s client timeout**; credentials server-side only | 2026-08-18 |
| SSLCOMMERZ developer documentation (v4) | IPN with MD5 `verify_sign` **plus a mandatory Transaction Validation API call** returning `VALID`/`FAILED`/`CANCELLED` | 2026-08-18 |
| Nagad merchant API integration guidance | Merchant RSA key pair; response signatures verified against Nagad's public key | 2026-08-18 |
| Bangladesh Bank, *BEFTN Operating Rules* | Fixed-width file with header, batch, entry and control records; three-digit SEC codes; **participants are banks**; T+1 | 2026-08-18 |
| ISO 4217 | Currency codes | 2026-08-18 |
| Garcia-Molina & Salem, *Sagas* | Long-running transactions with compensations (§7.2 `MS-06`) | 2026-08-18 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture with Finance Systems | Initial issue. Designs the money path the estate had runbook content but no design for. Introduces **`unknown` as a first-class payment state** (`IN-007-D-01`) and the rule that **the rail always wins** (`PAY-01`). Defines the PCI scope boundary **and what would breach it**. Designs marketplace split settlement with clawback, and **COD custody — raising `IN-A-25`, an unowned working-capital exposure at W3**. **Reconciles all three `AP-06` commitments: two by design ruling, and the third named as an unresolved CFO procurement decision** rather than reported closed | *Pending — CTO and CFO (`PGD-A1-09`)* |

---

*`IN-007` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
