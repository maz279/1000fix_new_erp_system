---
id: AP-009
title: Payment Gateway Integration Runbook Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with Finance Systems and Treasury
reviewers: [CTO, Solution Architect, CFO, Finance Manager, Treasury Lead, Security Lead, Support Lead, QA Lead, Content Design Lead]
approver: Content Design Lead with CFO
content_class: D
purpose: >
  The integration content behind the nine payment rails — what each one does, how a payment is
  confirmed, what a timeout actually means, how refunds and reversals behave, how each reconciles,
  what fails and what happens when it does, and the manual path that keeps 51+ branches trading
  through an outage. `NFR-048` commits to 99.95% payment-path availability with multi-gateway
  failover across nine integrations, four of them `P0`; that number is only reachable with
  documented, drilled behaviour per gateway, and the single most expensive defect in the estate —
  a payment taken twice, or taken and lost — lives in the gap this file closes.
traces_to: [05-03, 05-03 §2.1, 05-03 §7, 05-03 IP-04, 05-03 IP-05, 05-03 IP-09, 05-06 NFR-042, 05-06 NFR-048, 05-06 NFR-050, 05-06 DI-01, 05-06 DI-02, 05-06 DI-07, M19, M20, M50, M28, M28 FR-IPF-043, M28 AC-13, MD-038, MD-040, AP-001, AP-002, AP-004, AP-005, AP-006, AP-010, AP-012, OP-008, OP-014, DT-010, NT-009, UI-004, TS-017, 06-02]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §2.1 the nine payment integrations INT-001…INT-009 with direction, pattern, module, wave and priority; §7 monitoring thresholds and the P0 fallback register; §1 IP-04, IP-05, IP-09
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-042 payment confirmation round trip ≤ 3 s p95; NFR-048 payment path availability ≥ 99.95% with multi-gateway failover; NFR-050 documented tested manual fallback for every P0 integration; DI-01 decimal arithmetic; DI-02 every posting reconcilable to its source; DI-07 nightly cross-system reconciliation
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §5.5 FR-IPF-039…FR-IPF-045 connector framework, credentials, circuit breakers, automatic fallback; §17 AC-13 — each of the twelve P0 integrations engages its fallback automatically within two minutes of an induced outage
    verified: 2026-08-18
    class: P1
  - source: SSLCOMMERZ v4 developer documentation — IPN listener, `verify_sign` MD5 hash match, and mandatory Order/Transaction Validation API call before treating a transaction as successful; separate sandbox at sandbox.sslcommerz.com. https://developer.sslcommerz.com/doc/v4/
    verified: 2026-08-18
    class: P2
  - source: bKash PGW tokenized checkout API surface — Grant Token, Refresh Token, Create Payment, Execute Payment, Query Payment, Search Transaction, Refund Transaction, with a recommended 30-second call timeout. https://www.bkash.com/en/page/tokenized_checkout
    verified: 2026-08-18
    class: P3
  - source: Nagad merchant API integration practice — merchant key-pair signing and encryption established at onboarding, with a payment-status verification call in the confirmation flow. https://a-pay.one/industry/nagad-payment-gateway
    verified: 2026-08-18
    class: P3
supersedes: none
review_due: 2027-02-18
---

# Payment Gateway Integration Runbook Content

| Item | Value |
|---|---|
| Payment integrations | 9 — `INT-001`…`INT-009` (`05-03` §2.1) |
| `P0` among them | **4** — bKash, Nagad, SSLCOMMERZ, BEFTN, plus bank statement import |
| Availability commitment | **≥ 99.95%** payment path, with multi-gateway failover (`NFR-048`) |
| Confirmation latency target | ≤ 3 s p95 (`NFR-042`) |
| Payment states | 9 (§4.2) |
| Failure modes catalogued | 14 (§4.6) |
| Manual fallbacks | 5 (§4.9) |
| External publication | **Extract only** — the gateway-facing contract. Failure modes, fallbacks and escalation are internal (`AP-001` §4.8) |
| Wave | W3 — aligned with `05-03` §8 |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.11. The **error catalogue table** required by `CG-009` §3 is
> §4.10, indexing `AP-006` codes plus the gateway-outcome mapping that is unique to payments.
>
> **This file is a `TPL_Runbook.md` candidate that `CG-009` §3 allocates to template 1.** The
> allocation is followed as written (`CP-09`); the runbook-shaped material — failure modes,
> fallback, drills — sits inside §4 rather than in runbook sections. The tension is recorded as
> `O-08` rather than resolved unilaterally.

---

## 1. Purpose

Nine payment integrations. Four `P0`. One availability commitment of 99.95% that no single
Bangladeshi gateway meets on its own, which is why `NFR-048` says *"with multi-gateway
failover"* — failover being a behaviour, not a product.

The register justification names the requirement: *"Nine payment integrations with a 99.95%
availability target and multi-gateway failover need documented, drilled fallbacks."* `M28` `AC-13`
makes it testable: each `P0` integration must engage its fallback **automatically within two
minutes** of an induced outage, with users receiving a clear localised message.

**The specific defect this file exists to prevent is not an outage.** It is the *indeterminate
outcome*: a payment call that times out. The money may have moved or it may not, and the two
wrong responses are symmetrical and both expensive — retry and take it twice, or fail it and lose
it. Every gateway in §4.3 has this failure mode, every one resolves it differently, and none of
that is written down anywhere in the repository.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| Per-gateway confirmation contract | Each connector is built by whoever picks it up. **At least one will treat a callback as proof of payment** — which SSLCOMMERZ's own documentation explicitly forbids |
| The indeterminate-outcome rule | Double charges and lost payments, discovered at reconciliation, disputed by customers, and unattributable |
| Reconciliation keys | `G3-02` requires auto-matching ≥ 90%; `DI-02` requires every posting reconcilable to its source. Both need a stated key per rail |
| Refund and reversal behaviour | Refunds are attempted through the wrong rail, or against the wrong original, and fail silently at settlement |
| Failover logic | `NFR-048` becomes an aspiration. Nine gateways with no failover order is nine independent single points of failure |
| Manual fallback | `IP-09` and `NFR-050` require one per `P0` integration. 51+ branches must keep trading; without a written path they stop taking money or take it off-system |
| Drill content | `M28` `AC-13` cannot be evidenced. An untested fallback is a hypothesis |

---

## 2. Scope

**In scope.** The nine rails and what each is for; the common payment state machine; per-rail
integration content — confirmation, reconciliation key, refund path, sandbox, credential model;
the idempotency and indeterminate-outcome rules; reconciliation; failure modes; refunds and
reversals; failover and the availability arithmetic; manual fallback; the error and
gateway-outcome mapping; endpoint reference; and the drill schedule.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| Accounting treatment, revenue recognition, gateway fee posting | `M19`, `M53`, `MD-035` | This file moves money and reconciles it; it does not post it |
| Payment method, term and bank master data; settlement account mapping | `MD-038` | The reconciliation **keys** live there; §4.5 references them |
| Statutory invoice and receipt output | `DT-010`…`DT-014`, `MD-040` | A payment is not an invoice |
| Customer-facing payment messaging | `NT-009`, `UI-004` | §4.9 names which message; the copy is theirs |
| Operating the platform through an incident — on-call, escalation, comms | `OP-008`, `OP-013`, `OP-004` | Runbook and incident content |
| The manual branch cash procedure | `OP-014`, and the branch SOPs in `SP` | §4.9 names the fallback; the procedure is theirs |
| Which fields leave the company to a gateway, and the lawful basis | `AP-012` | §4.12 summarises; `AP-012` is the register |
| Webhook signature mechanics | `AP-004` §4.9 | Per-provider verification is tabled there; §4.3 gives what the callback **means** |
| Gateway commercial terms, merchant fees, settlement periods | Treasury and Commercial | Not content |
| Card data handling and PCI scope | **Nobody — `O-03`** | Recorded, not assumed |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Platform engineers building the nine connectors** | The primary audience. §4.3 is the build brief per rail |
| **Finance Systems and Treasury** | §4.5 reconciliation and §4.7 refunds — the two places money is reconciled or lost |
| **`R26` Finance Manager, `R27` Finance Officer** | What a failed, pending or indeterminate payment means for their day |
| **Support (`OP-001`)** | §4.6 and §4.9 — what a branch does when a rail is down |
| **`R29` Cashier / Counter Finance (51+)** | Indirectly, through `OP-014` and the branch SOPs this file feeds |
| **Security** | Credential model, callback verification, and the `O-03` PCI gap |
| **QA** | `TS-017` and the `M28` `AC-13` drill evidence |
| **Gateway integration teams** | The **external extract only** — the gateway-facing contract, not the fallbacks |

---

## 4. Content

### 4.1 The nine rails

| INT | Rail | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|:--:|:--:|:--:|
| **INT-001** | **bKash** | Bidirectional | Sync + webhook | Mobile money collection, refund, reversal | `M19`, `M20` | W3 | **P0** |
| **INT-002** | **Nagad** | Bidirectional | Sync + webhook | Mobile money collection, refund | `M19`, `M20` | W3 | **P0** |
| **INT-003** | **SSLCOMMERZ** | Bidirectional | Sync + webhook | Card, net banking, aggregated wallets | `M19`, `M20` | W3 | **P0** |
| INT-004 | Rocket (via aggregator) | Bidirectional | Sync | Mobile money collection | `M19`, `M20` | W3 | P1 |
| **INT-005** | **Bank BEFTN** | Outbound | Batch file | Payroll and vendor disbursement | `M19`, `M21` | W5 | **P0** |
| **INT-006** | **Bank statement import** | Inbound | Batch file / API | Automated reconciliation | `M19` | W3 | **P0** |
| INT-007 | Seller payout rail | Outbound | Batch + API | Marketplace seller payouts | `M20` | W7 | P1 |
| INT-008 | International gateway (Stripe/PayPal) | Bidirectional | Sync + webhook | Cross-border customer payments | `M20` | W9 | P3 |
| INT-009 | Instalment / BNPL partner | Bidirectional | Sync + webhook | Consumer instalment on high-value repairs and refurbished sales | `M20` | W8 | P3 |

**Three groups, three different problems.**

| Group | Rails | The problem |
|---|---|---|
| **Collection** — money in, synchronously, with a customer waiting | INT-001, -002, -003, -004, -008, -009 | Latency (`NFR-042` 3 s p95), the indeterminate outcome, and failover |
| **Disbursement** — money out, in batches, no customer waiting | INT-005, INT-007 | Control totals, authorisation, and the impossibility of an easy reversal |
| **Reconciliation** — evidence of what actually happened | INT-006 | Matching rate (`G3-02` ≥ 90%) and the truth against which the other eight are checked |

> **INT-006 is the quiet one and the most important.** Bank statement import is the only rail that
> tells 1000FiX what the **bank** thinks happened. Every other rail reports what the *gateway*
> thinks happened. When those disagree, the statement wins, and `DI-07`'s nightly reconciliation
> is where the disagreement surfaces.

### 4.2 The common payment state machine

One state model across all collection rails. Gateways use different vocabulary; the connector maps
into this and the estate reasons in one language.

```
     INITIATED ──► the payment intent exists; nothing has been asked of the rail
         │
         ▼
     PENDING ──► the rail has the request; the customer may be authorising
         │
         ├──────────────► FAILED        rail returned a definitive failure
         │                   │           → customer may retry; nothing moved
         │                   ▼
         │              (terminal)
         │
         ├──────────────► CANCELLED     customer abandoned, or the intent expired
         │
         ├──────────────► INDETERMINATE ⚠ timeout, or no callback within the window
         │                   │           **We do not know whether money moved**
         │                   │  resolved ONLY by querying the rail (§4.4)
         │                   ├──► CONFIRMED   query says it succeeded
         │                   └──► FAILED      query says it did not
         │
         ▼
     CONFIRMED ──► rail confirms the money moved; invoice application may proceed
         │
         ▼
     SETTLED ──► the amount appears on the bank statement (INT-006) and reconciles
         │
         ├──► REFUNDED         full refund executed on the same rail
         ├──► PART_REFUNDED    partial refund executed
         └──► REVERSED         chargeback or rail-initiated reversal
```

| # | Rule | Basis |
|---|---|---|
| **PS-1** | **`CONFIRMED` is set only by 1000FiX querying the rail**, never by a callback alone | `RX-06`, and SSLCOMMERZ's own validation requirement |
| **PS-2** | **`INDETERMINATE` is a real state and must be modelled.** A payment system with no indeterminate state resolves every timeout as a guess | §4.4 |
| **PS-3** | `SETTLED` requires the bank statement, not the gateway | `DI-02`, INT-006 |
| **PS-4** | `invoice.paid` is emitted on invoice settlement, **not** on `CONFIRMED`. A confirmed payment against a partially settled invoice emits nothing today | `AP-003` `O-03` |
| **PS-5** | Refund and reversal are **new movements** on the original, never a state rewind | `AP-003` `EV-02` |
| **PS-6** | Every state carries the rail's own reference **and** ours. Reconciliation joins on both | §4.5 |

### 4.3 Per-rail integration content

**INT-001 · bKash · `P0` · W3**

| Aspect | Content |
|---|---|
| Model | Tokenised checkout. Grant a token, refresh it, create a payment, execute it, then query |
| Confirmation | **Execute, then Query.** A callback is a prompt to query, never proof (`PS-1`) |
| Call timeout | The provider recommends **30 seconds** per call. **A 30-second call cannot meet `NFR-042`'s 3 s p95 confirmation round trip** — see `O-01` |
| Idempotency | Our `Idempotency-Key` on the initiating call; the rail's `paymentID` is the correlation for query and refund |
| Reconciliation key | `trxID` on the statement line; `paymentID` for the intent — both stored (`PS-6`) |
| Refund | Refund Transaction against the original `trxID`. Partial supported |
| Search | Search Transaction resolves an `INDETERMINATE` where the `paymentID` is lost |
| Sandbox | Provider sandbox available; credentials issued at merchant onboarding |
| Credentials | App key, app secret, username, password — **vault-held, never in configuration** (`IP-07`, `NFR-062`) |
| Failure signature | Token expiry mid-flow; grant-token rate limits under burst |

**INT-002 · Nagad · `P0` · W3**

| Aspect | Content |
|---|---|
| Model | Merchant key-pair. Requests are signed and sensitive fields encrypted with keys exchanged at onboarding |
| Confirmation | Initiate, complete, then **verify by payment-status call** (`PS-1`) |
| Idempotency | Our order reference is the idempotency anchor; the rail's payment reference correlates |
| Reconciliation key | Payment reference plus order reference |
| Refund | Supported per merchant agreement; **the reversal path is materially less documented than bKash's** and needs confirmation at onboarding |
| Sandbox | Available at merchant onboarding |
| Credentials | **Key pair**, not a shared secret. Key rotation is a joint operation with the provider and is not self-service — `O-04` |
| Failure signature | Signature or encryption mismatch after a key rotation on either side |

**INT-003 · SSLCOMMERZ · `P0` · W3**

| Aspect | Content |
|---|---|
| Model | Hosted checkout aggregating card, net banking and wallets |
| Confirmation | IPN to our listener → **match `verify_sign`** → **then call the Transaction Validation API**. The provider's documentation states the validation call is required before treating a transaction as successful. **Two steps, both mandatory** |
| Idempotency | `tran_id` is ours and must be unique per attempt; `val_id` is theirs and is the validation handle |
| Reconciliation key | `tran_id` ↔ `val_id` ↔ bank statement narration |
| Refund | Refund API against the validated transaction |
| Sandbox | Separate sandbox host and separate credentials. **Sandbox transactions have no accounting effect** |
| Credentials | Store id and store password, vault-held |
| Failure signature | IPN listener unreachable → the transaction succeeds at the rail and is invisible to us until reconciliation. **This is the most likely silent-loss path in the estate** |

**INT-004 · Rocket via aggregator · `P1` · W3**

| Aspect | Content |
|---|---|
| Model | Through an aggregator. **`05-03` §2.1 does not name the aggregator** |
| Confirmation | Unknown until the aggregator is named |
| Pattern | `05-03` records **Sync only — no webhook**, unlike the other three mobile-money rails. Confirmation is therefore synchronous or by polling |
| Everything else | **Cannot be authored.** Recorded as `O-02` rather than guessed (`CG-012`, `CM-R8`) |

**INT-005 · Bank BEFTN · `P0` · W5**

| Aspect | Content |
|---|---|
| Model | Outbound **batch file** to the bank. Payroll and vendor disbursement |
| Confirmation | Bank acknowledgement file, then the statement (INT-006) |
| Idempotency | **File-level.** A batch carries a unique reference and a **control total**; a resubmitted file with the same reference must be rejected by the bank, not processed |
| Reconciliation key | Batch reference + per-line beneficiary reference, against the statement |
| Refund | **There is no refund.** A wrong disbursement is recovered commercially, not technically. This is why authorisation matters more here than anywhere else |
| Authorisation | `SOD-03` — process payroll and approve payroll are a hard block; `05-04` §7 requires HR Manager **and** CFO |
| Sandbox | **Bank test facility availability is unknown** — `O-05` |
| Failure signature | Format rejection of the whole file for one bad line; and `G5-02` requires BEFTN accepted at the W5 gate |

**INT-006 · Bank statement import · `P0` · W3**

| Aspect | Content |
|---|---|
| Model | Inbound batch file or API from the bank |
| Purpose | **The truth against which every other rail is checked** |
| Matching | `G3-02` requires auto-matching ≥ **90%**. The unmatched 10% is a daily Finance task, not an exception |
| Reconciliation key | Statement narration parsed to the rail reference — the weakest join in the estate, because narration formats vary by rail and by bank |
| Failure signature | A narration format change by the bank silently drops the match rate. **Monitored as a rate, not as an error** |
| Fallback | Manual statement upload (`05-03` §7) |

**INT-007 · Seller payout rail · `P1` · W7**

| Aspect | Content |
|---|---|
| Model | Batch + API, outbound to marketplace sellers |
| Rail | **Not named in `05-03`.** Whether it is BEFTN, a mobile-money bulk disbursement, or a third party is undecided — `O-02` |
| Idempotency | **Money control, not hygiene.** `G7-02` requires 100% payout accuracy with zero unexplained variance; `payout.executed` is financially irreversible in practice (`AP-003` §4.5.10) |
| Hold rule | A payout is held while a dispute is open (`P07`, `dispute.raised`) |
| Authorisation | `SOD-06` — approve a seller and approve their payout is a hard block |

**INT-008 · International gateway · `P3` · W9** and **INT-009 · Instalment/BNPL · `P3` · W8**

| Aspect | Content |
|---|---|
| Status | Both `P3`, both late-wave, both with an **unnamed provider** |
| Content authored | The state machine (§4.2), the idempotency rule (§4.4) and the reconciliation obligation (§4.5) apply to both. **Provider-specific content cannot be authored before the provider is chosen** |
| INT-009 note | Instalment introduces a payment that is **confirmed but not fully collected**, which `PS-4` and `AP-003` `O-03` already identify as an unmodelled state |

### 4.4 Idempotency and the indeterminate outcome

**The rule that prevents the most expensive defect in the estate:**

> **A timeout is not a failure. It is an unknown outcome, and the only thing that resolves it is
> asking the rail.**

| # | Rule | Reason |
|---|---|---|
| **ID-1** | Every payment initiation carries an `Idempotency-Key` we generate and persist **before** the call | If we crash between generating and calling, the key survives and the retry is safe (`API-07`, `IP-04`) |
| **ID-2** | The key is bound to the **payment intent**, not to the HTTP attempt. Three attempts at one payment share one key | A per-attempt key defeats the mechanism entirely |
| **ID-3** | On timeout, the payment moves to `INDETERMINATE` and **a query is scheduled**. It is never marked failed and never retried blind | §4.2 `PS-2` |
| **ID-4** | The query uses the rail's own status or search endpoint, with our reference | bKash Query/Search, SSLCOMMERZ validation, Nagad status |
| **ID-5** | The query is retried with backoff until it returns a definitive answer or the reconciliation window closes. **`INDETERMINATE` is never left to age out** | An aged-out indeterminate is an unreconciled payment |
| **ID-6** | The customer is told the truth: *"we are confirming your payment"*, never *"payment failed"* | `NFR-078`, `UI-004` three-part structure. Telling a customer it failed when it succeeded produces a duplicate payment **by the customer** |
| **ID-7** | `idempotency.key_expired` (`AP-006`) means the original result is no longer retrievable. **Reconcile before resubmitting. Never blind-resubmit a payment** | `AP-006` §4.8's unknown-outcome class |
| **ID-8** | Disbursement rails are idempotent at **file level** with a control total, not at record level | INT-005, INT-007 |

**Why `ID-6` is a content rule and not an engineering one.** `UI-004` §5.2's timeout message reads
*"This took longer than expected and was stopped. Nothing was saved. Try again."* On a payment
path that assertion is false and it instructs the customer to pay twice. `AP-006` `O-04` records
the required `UI-004` change; until it is made, **no payment flow may use
`common.error.system.timeout`.**

### 4.5 Reconciliation

`DI-02`: every financial posting is reconcilable to its source. `DI-07`: cross-system
reconciliation runs nightly with divergence alerting. `G3-02`: auto-match ≥ 90%. `G3-09`: branch
cash reconciling daily.

| Layer | What is compared | Frequency | Key | Divergence handling |
|---|---|---|---|---|
| **L1 — Intent vs rail** | Our payment records against the rail's transaction list | Daily per rail | Our reference ↔ rail reference | `platform.reconciliation_divergence`; investigated, never absorbed (`BRU-IPF-19`) |
| **L2 — Rail vs bank** | Rail settlement reports against the bank statement (INT-006) | Daily | Rail settlement batch ↔ statement narration | Treasury |
| **L3 — Bank vs ledger** | Statement against `M19` postings | Daily | `MD-038` settlement account mapping | Finance |
| **L4 — Invoice application** | Confirmed payments against invoice balances | Daily | Invoice number (`MD-040`) | Finance |
| **L5 — Indeterminates** | Every `INDETERMINATE` older than the resolution window | **Hourly** | Payment intent | **Escalated, not queued** (`ID-5`) |

**Three reconciliation facts a builder needs.**

1. **`MD-038` holds the settlement and reconciliation keys** — payment methods, terms, bank
   accounts, settlement mapping. Nine rails settle into accounts that must be pre-defined for
   automated reconciliation. That file is the authority and is not restated here (`CP-01`).
2. **The narration join is the weak point.** L2 depends on parsing bank statement narration into a
   rail reference. Formats vary by rail and change without notice. Monitor the **match rate** and
   alert on a drop, because a format change produces no error at all.
3. **Gateway fees are a reconciliation item, not a rounding difference.** A rail settling net of
   fees produces a permanent L2 difference unless the fee is modelled. Whether `MD-038` carries a
   fee structure per rail is unverified — `O-06`.

### 4.6 Failure modes

Fourteen. Each is a real, observed failure class in payment integration; each has a detection
signal and a response.

| # | Failure | Detection | Response | State |
|---:|---|---|---|---|
| **F-01** | Rail returns a definitive decline | Rail response | Tell the customer what and what next; offer an alternative rail | `FAILED` |
| **F-02** | Rail times out on the initiating call | Timeout | Query. **Do not retry blind** | `INDETERMINATE` |
| **F-03** | Callback never arrives | No callback within the window | Query on a schedule | `INDETERMINATE` |
| **F-04** | Callback arrives but fails verification | `verify_sign` / signature mismatch | **Reject; raise a security event.** Do not process | Unchanged |
| **F-05** | Callback arrives for an unknown reference | No matching intent | Quarantine; investigate. May be a replay or a cross-environment leak | Unchanged |
| **F-06** | Our IPN listener is unreachable | Rail-side delivery failure, or a silence anomaly | **The rail succeeded and we do not know.** Detected only by L1 reconciliation. Alert on listener availability, not only on errors | `INDETERMINATE` at reconciliation |
| **F-07** | Duplicate callback | Same rail reference twice | De-duplicate on the rail reference (`AP-004` `CO-03`) | Unchanged |
| **F-08** | Rail error rate above threshold | > 2% over 5 min (`05-03` §7) | Alert; circuit half-open | Degraded |
| **F-09** | Rail unavailable | Availability < 99% over 15 min, or circuit opens | **Automatic failover** (§4.8); notify affected users | Degraded → failover |
| **F-10** | Credential expired | `platform.credential_expiring` ignored | Rail returns auth errors; **treat as an outage** | Failover |
| **F-11** | Amount mismatch between intent and rail confirmation | L1 reconciliation | **Never auto-correct.** Hold and escalate to Finance | Held |
| **F-12** | Currency or decimal error | Validation, or L3 | Blocked at source — `DI-01` prohibits floating point in money paths (`AS-10`) | Rejected |
| **F-13** | Statement narration format change | **Match-rate drop**, not an error | Alert on the rate; re-parse | — |
| **F-14** | Disbursement file rejected for one bad line | Bank acknowledgement | The **whole file** is rejected. Correct and resubmit with a new batch reference | Failed batch |

> **`F-06` deserves its own paragraph.** An unreachable IPN listener means the customer paid, the
> rail recorded it, and 1000FiX has no record. There is no error anywhere in our systems — the
> absence of a callback looks exactly like the absence of a payment. It is caught only by L1
> reconciliation, up to 24 hours later, during which the customer has an unpaid invoice and a
> debited account. **Monitor listener availability as a first-class signal**, and treat a
> statistically improbable silence as an incident.

### 4.7 Refunds and reversals

| # | Rule |
|---|---|
| **RF-1** | A refund goes back **on the rail that took the payment**, against the original transaction reference. Cross-rail refunds are a Treasury exception, not an integration path |
| **RF-2** | A refund is a **new movement**, never a state rewind (`PS-5`). The original payment stays `CONFIRMED` |
| **RF-3** | A refund never reverses the **invoice**. Reversing an invoice is a credit note — and `credit_note.issued` is **not a registered event** (`AP-003` §4.9, `AP-008` `O-03`) |
| **RF-4** | Partial refunds are supported where the rail supports them, and are tracked against the original to prevent over-refunding beyond the original amount |
| **RF-5** | A refund is subject to approval (`05-04` §7 credit note thresholds) and, where external, to MFA (`EA-09`) |
| **RF-6** | A **reversal** is rail-initiated — a chargeback or a rail-side correction. It is not a refund, it arrives without our involvement, and it must be modelled as an inbound event |
| **RF-7** | **There is no refund on a disbursement rail.** Recovery of a wrong BEFTN payment or seller payout is commercial |
| **RF-8** | **No refund SLA exists anywhere in the repository** — not in `LG-014` refund policy terms, not in `MD-028`. A customer asking "when will I get my money" has no documented answer. `O-07` |

### 4.8 Failover and the availability arithmetic

`NFR-048`: payment path availability ≥ 99.95% **with multi-gateway failover**. `M28` `AC-13`: fallback
engages automatically within **two minutes** of an induced outage.

**The arithmetic, stated because it is what makes failover mandatory rather than prudent.**
99.95% is roughly **22 minutes of downtime per month** across the whole payment path. No single
Bangladeshi gateway commits to that figure publicly, and 1000FiX cannot commit on their behalf.
The target is only reachable by treating the *path* as available when **any** acceptable rail is
available.

**Failover order — proposed.**

| Customer intent | Primary | Secondary | Tertiary | Last resort |
|---|---|---|---|---|
| Mobile money — bKash | INT-001 | INT-002 Nagad | INT-003 SSLCOMMERZ wallet | Cash at counter |
| Mobile money — Nagad | INT-002 | INT-001 bKash | INT-003 | Cash at counter |
| Card | INT-003 | — *(no second card acquirer)* | — | Cash at counter, or payment link when restored |
| Net banking | INT-003 | — | — | Bank transfer with manual matching |

| # | Rule |
|---|---|
| **FO-1** | Failover is **automatic** (`FR-IPF-043`), not a runbook instruction. `M28` §4: a fallback requiring a human to notice first activates twenty minutes late |
| **FO-2** | The customer is **told** which rail is being used and why, in their language (`M27`, `NT-009`) |
| **FO-3** | Failover never silently changes the amount, the currency or the invoice reference |
| **FO-4** | A customer who has already been debited on the failing rail is **not** offered a second rail. That is `INDETERMINATE` and it is resolved by query (`ID-3`), not by re-collection |
| **FO-5** | On recovery, queued work is replayed and normal service is announced (`AUT-IPF-13`) |
| **FO-6** | **Card has no second acquirer.** A single card acquirer is a single point of failure for every card payment, and no failover exists for it. Stated plainly as `O-01` |

### 4.9 Manual fallback

`IP-09` and `NFR-050`: every `P0` integration has a documented, tested manual fallback. `05-03` §7
registers them; this is the content behind each.

| Rail down | Manual fallback | Who executes | What must be recorded | Reconciled by |
|---|---|---|---|---|
| bKash / Nagad / SSLCOMMERZ | **Cash at counter**, or a payment link resent when restored (`05-03` §7) | `R29` Cashier | Receipt number, amount, invoice reference, shift | Daily branch cash reconciliation (`G3-09`) |
| All collection rails simultaneously | Cash only; **credit terms for corporate clients** already on account | `R29`, `R06` Branch Manager | As above, plus a manager authorisation for any credit extension | Daily |
| Bank statement import | **Manual statement upload** | `R27` Finance Officer | Statement period, file reference | L2/L3 next run |
| BEFTN | **Manual bank file submission through the bank portal** | `R26` Finance Manager with CFO authorisation | Batch reference, control total, submitting user | Bank acknowledgement |
| Seller payout rail | Manual disbursement per the treasury procedure | Treasury | Batch, control total, dual authorisation | L2 |

| # | Rule |
|---|---|
| **MF-1** | A manual fallback is **on-system as soon as the system returns**. Off-system money is unreconcilable and `G3-09` fails |
| **MF-2** | Every manual collection carries a receipt with a number from a controlled sequence (`MD-040`). Handwritten receipts without a sequence are the audit finding this rule exists to prevent |
| **MF-3** | The branch procedure lives in `OP-014` and the branch SOPs. **This file names the fallback; it does not instruct the cashier** (`CP-01`) |
| **MF-4** | Fallbacks are **drilled**, not documented (§4.13). `M28` `AC-13` requires evidence |

### 4.10 Error and gateway-outcome mapping

The error catalogue table required by `CG-009` §3. Codes are `AP-006`'s; the **outcome mapping**
is unique to payments and is authored here.

| Gateway outcome | Our state | `AP-006` code returned to the caller | Customer message intent | Retry |
|---|---|---|---|:--:|
| Success, validated | `CONFIRMED` | — (`2xx`) | Payment received | — |
| Declined — insufficient funds | `FAILED` | `422 rule.*` per rail mapping, or `2xx` with a decline reason | "Your payment was declined. Try another method." | Customer retries |
| Declined — limit exceeded | `FAILED` | as above | "Your daily limit was reached." | Customer retries |
| Declined — customer cancelled | `CANCELLED` | — | "You cancelled the payment." | Customer retries |
| Rail timeout on initiation | `INDETERMINATE` | `504 dependency.timeout` | **"We are confirming your payment."** Never "failed" (`ID-6`) | **No — query** |
| No callback within window | `INDETERMINATE` | — (async) | As above | No — query |
| Rail unavailable | — | `503 dependency.unavailable` | "This payment method is unavailable. Use {alternative}." | Failover |
| Failover engaged | proceeds | `503 dependency.fallback_engaged` — **request succeeded, degraded** | "We used {alternative}." | No |
| No failover available | — | `503 dependency.no_fallback` | "Payment is unavailable. Pay at the counter or we will send a link." | Later |
| Circuit open | — | `503 dependency.circuit_open` | As above | Honour `Retry-After` |
| Callback verification failed | unchanged | — (rejected at the receiver) | None — **security event** | No |
| Amount mismatch | Held | `500 platform.unexpected` to the caller; Finance escalation internally | "We are checking this payment." | No |
| Duplicate idempotency key in flight | — | `409 idempotency.in_flight` | — | Yes, same key |
| Idempotency key expired | — | `422 idempotency.key_expired` | — | **No — reconcile first** (`ID-7`) |

### 4.11 Endpoint reference

The endpoint reference table required by `CG-009` §3. 1000FiX-side endpoints only; each rail's own
API is the rail's documentation.

| Endpoint | Method | Purpose | Owner | Consumer |
|---|:--:|---|:--:|---|
| `/api/v1/payments/confirm` | POST | Payment gateway confirmation into the ERP | `M20` | Portal platform, connectors |
| `/hooks/v1/bkash` | POST | bKash callback receiver | `M28` | INT-001 |
| `/hooks/v1/nagad` | POST | Nagad callback receiver | `M28` | INT-002 |
| `/hooks/v1/sslcommerz` | POST | SSLCOMMERZ IPN listener | `M28` | INT-003 |
| `/hooks/v1/{rail}` | POST | Receiver per remaining rail | `M28` | INT-004, -008, -009 |
| `/api/v1/customers/{id}/invoices` | GET | Invoice and payment status | `M20` | Portals |
| `/api/v1/platform/integrations/{id}/health` | GET | Live health for one rail | `M28` | `P03`, `P06` |
| `/api/v1/platform/integrations/{id}/test-fallback` | POST | Exercise a registered fallback — **non-production and scheduled drills** | `M28` | `R33` IT Administrator |
| `/api/v1/platform/reconciliation` | GET | Reconciliation runs and divergences | `M28` | `P03`, Finance |

**Path names for the receivers are proposals.** `05-03` §5.1 registers the family as
`/hooks/v1/*` and `M28` §12.5 as `/hooks/v1/{integration}`; the per-rail segment is not
enumerated anywhere.

### 4.12 What leaves the company

Summarised; `AP-012` is the register and the authority.

| Rail | Fields sent | Sensitivity | Note |
|---|---|---|---|
| bKash / Nagad / Rocket | Amount, currency, merchant reference, our order reference, **customer mobile number** | S2 | The mobile number is the wallet identity; it cannot be minimised away |
| SSLCOMMERZ | Amount, currency, `tran_id`, customer name, email, phone, address | S2 | Hosted checkout requires a customer profile. **This is the largest personal-data egress of the nine** |
| BEFTN | Beneficiary name, **bank account**, amount, reference | S2/S3 | Employee bank details on the payroll batch |
| Seller payout | Seller name, account, amount | S2 | |
| Bank statement import | **Inbound only** — nothing leaves | — | |
| International / BNPL | Provider-defined | Unknown | **Cross-border transfer** — `NFR-086b` requires an Authority notification record and a documented safeguard **before** the transfer executes |

> **INT-008 and INT-009 are cross-border by construction.** `NFR-099` restricts large-scale
> transfer of Sensitive Personally Identifiable Data and `NFR-086b` gates any cross-border
> transfer of a residency-classified field. Both rails are `P3` and late-wave, which is fortunate,
> because neither has a lawful-basis determination. `AP-012` carries it.

### 4.13 Drills

`M28` `AC-13`: each of the twelve `P0` integrations engages its fallback automatically within two
minutes of an induced outage, with users receiving a clear localised message. Five of the twelve
are payment rails.

| Drill | Frequency | Method | Evidence |
|---|---|---|---|
| Single-rail outage with automatic failover | **Quarterly per `P0` rail** | Induced outage in a non-production environment; `/test-fallback` | Time to detect, time to failover, message shown, user impact |
| All-collection-rails outage → cash fallback | **Twice yearly** | Table-top with two branches | Cashier procedure executed, receipts sequenced, on-system within one working day |
| BEFTN file rejection | **Before each payroll cycle in W5** | Deliberate bad line in a test file | Whole-file rejection observed; corrected resubmission accepted |
| Statement narration change | **Twice yearly** | Altered narration in a test statement | Match-rate alert fires |
| Indeterminate resolution | **Quarterly** | Forced timeout with a real sandbox payment | Query resolves within the window; no double charge; correct customer message |

> **`M28` `AC-13`'s two-minute target is a detection-plus-switch budget, not a switch budget.** `05-03`
> §7 detects unavailability at *< 99% over 15 minutes* and error rate at *> 2% over 5 minutes*.
> **A 5-minute detection window cannot produce a 2-minute failover.** The reconciliation is that
> circuit-breaker state, not the monitoring window, drives failover — a circuit opens in seconds.
> That is a design position, and it is not stated anywhere. `O-01`.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-03` §2.1, §7 | The nine rails, the monitoring thresholds and the registered fallbacks |
| `M28` `FR-IPF-039`…`FR-IPF-045` | Connector framework, credentials, circuit breakers, automatic fallback |
| `M20`, `M19`, `M50` | Billing, ledger and treasury — the modules that own the money |
| **`MD-038`** | Payment methods, terms, bank accounts and settlement mapping. §4.5 does not work without it |
| `MD-040` | Document sequences for receipts (`MF-2`) |
| `AP-004` §4.9 | Per-provider callback verification |
| `AP-005` | Credentials, vault, rotation |
| `AP-006` | The codes §4.10 maps to |
| `AP-010` | Sandboxes per rail — and four of nine have unknown sandbox availability |
| `AP-012` | The disclosure register behind §4.12 |
| `OP-014` | The manual fallback procedures §4.9 names |
| `OP-008` | Operating the connectors through an incident |
| `NT-009`, `UI-004` | Customer payment messaging — and `UI-004`'s timeout copy must change (`ID-6`) |
| `LG-014` | Refund and cancellation policy — the home of the missing refund SLA (`RF-8`) |
| `06-02` `G3-02`, `G3-03`, `G3-09`, `G5-02`, `G7-02` | The gate criteria these rails evidence |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, and after every payment incident |
| Trigger for out-of-cycle review | A new rail · a rail changing its API · a provider naming (INT-004, INT-007, INT-008, INT-009) · a drill failure · any double-charge or lost-payment incident · a change to `NFR-048` |
| Owner | Platform Engineering Lead, with **CFO accountable** for §4.5, §4.7 and §4.9 |
| Change control | Changes to §4.4 (idempotency), §4.8 (failover) or §4.9 (manual fallback) require **CTO and CFO** approval and a `RF-006` entry. These are money controls |
| Version pinning | Pinned to **API version** for the external extract; the internal content is reviewed per wave |
| Publication | **Extract only** externally (`AP-001` §4.8): the gateway-facing contract. §4.6, §4.8, §4.9 and §4.13 are internal |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Three availability commitments do not reconcile.** `NFR-042` sets payment confirmation at **≤ 3 s p95** while bKash's own guidance is a **30-second** call timeout. `M28` `AC-13` requires failover **within 2 minutes** while `05-03` §7 detects unavailability over a **5–15 minute** window. And `NFR-048` commits **99.95%** on a card path with **a single acquirer and no failover** (`FO-6`). All three need resolving together, because each constrains the others | CTO with CFO | **W3 minus 2 months — before the connectors are built** |
| **O-02** | **Four of nine rails have no named provider.** INT-004's aggregator, INT-007's payout rail, INT-008's international gateway and INT-009's BNPL partner are all unnamed in `05-03` §2.1. **INT-004 is W3** — the same wave as the three `P0` rails — so a quarter of the W3 payment scope cannot be specified | Treasury with Commercial Director | **INT-004: W3 minus 3 months** |
| **O-03** | **PCI DSS scope has never been determined.** INT-003 handles cards. Whether 1000FiX is in scope, and at what level, is not addressed in `05-06` §4, `M29`, `LG-021` or anywhere else. **A hosted-checkout model keeps scope minimal, but "minimal" is still a determination somebody must make and evidence** | CFO with Security Lead | **W3 minus 3 months** |
| **O-04** | **Nagad key rotation is not self-service** and is a joint operation with the provider. `AUT-IPF-15` alerts 30 days before expiry and `FR-IPF-016` assumes self-service rotation. A joint rotation needs a lead time nobody has established | Treasury with Platform Engineering Lead | W3 |
| **O-05** | **Sandbox availability is unknown for five rails.** SSLCOMMERZ and bKash publish sandboxes. Nagad's is issued at onboarding. **BEFTN bank test facilities, and the sandboxes for INT-004, -007, -008, -009, are unknown** — so `AP-010`'s promotion gate cannot be satisfied for them | Treasury with Platform Engineering Lead | W3 |
| **O-06** | **Gateway fees may not be modelled.** A rail settling net of fees produces a permanent L2 reconciliation difference. Whether `MD-038` carries a fee structure per rail is unverified, and `G3-02`'s 90% auto-match target is affected directly | Finance Manager with MDM | W3 |
| **O-07** | **No refund SLA exists** (`RF-8`). Not in `LG-014`, not in `MD-028`. A customer asking when their money returns has no documented answer, and support has nothing to quote | CFO with Legal Counsel | **W3 — before the first refund** |
| **O-08** | **Template allocation is contested.** `CG-009` §3 allocates all twelve `AP` files to template 1 (Generic). This file is a **runbook** — failure modes, fallback, drills, escalation — and `TPL_Runbook.md` exists and governs exactly that shape for Category 17. The allocation was followed (`CP-09`); whether it is right is a `CG-009` question | Programme Content Lead with Content Design Lead | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` as `CG-009` §3 allocates; the template tension recorded rather than resolved unilaterally
- [x] All nine rails tabled, grouped by the problem each presents
- [x] **One payment state machine across all rails, with `INDETERMINATE` modelled as a first-class state**
- [x] Per-rail content for every rail that can be specified; the four unnamed providers recorded as unspecifiable (`CG-012`, `CM-R8`)
- [x] **The indeterminate-outcome rule stated as eight rules, including the customer-message rule that prevents customer-initiated double payment**
- [x] Five-layer reconciliation model with the narration join identified as the weak point
- [x] Fourteen failure modes with detection signal and response, including the silent-loss path
- [x] Eight refund and reversal rules, including the absence of a refund on disbursement rails
- [x] **The 99.95% arithmetic stated, and the single-acquirer card gap named**
- [x] Manual fallback per `P0` rail with who executes and what is recorded
- [x] Gateway-outcome-to-error mapping authored, referencing `AP-006` codes without inventing new ones
- [x] Data egress per rail summarised against `AP-012`, with the cross-border rails flagged
- [x] Drill schedule with evidence per drill, and the `M28` `AC-13` timing contradiction surfaced
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` three availability commitments do not reconcile — outstanding; blocks connector design**
- [ ] **`O-02` four rails have no named provider, one of them at W3 — outstanding**
- [ ] **`O-03` PCI scope never determined — outstanding**
- [ ] **`O-07` no refund SLA — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CFO**
- [ ] Bengali counterpart — n/a for the developer content per `CG-010` §3.2. **The customer-facing payment messages this file governs are bilingual and live in `NT-009` and `UI-004`**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
