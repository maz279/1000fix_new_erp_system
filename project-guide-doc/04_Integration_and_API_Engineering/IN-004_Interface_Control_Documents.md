---
id: IN-004
title: Interface Control Documents (ICD) — per External System
category: 04 — Integration & API Engineering
code: IN
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Integration Architect
approver: Design Authority (constituted under GV-002)
standards_basis: >
  IEEE 1016-2009 §5.7 interface viewpoint · ISO/IEC/IEEE 42010:2022 (via AR-001) ·
  Bangladesh Bank BEFTN Operating Rules · Standard Webhooks · OpenAPI 3.1 (where a
  counterparty publishes one) · PCI DSS v4.0 scope definition
traces_to: >
  PGD-000 IN-004 · 05-03 §2 INT-001…INT-047 · Technology Stack §12.2.4 ·
  M28 §12.4 · IN-001 §7.2, §8, §10 · audit AP-04, AP-06, AP-08, AP-12 ·
  NFR-050, NFR-086, NFR-098, NFR-099 · AP-012 DS-01
depends_on: IN-001 · IN-006 (signature scheme) · IN-007 (payment design) · AP-012
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 17:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-004 — Interface Control Documents (ICD) — per External System

### Category 04 · Code `IN` · IEEE 1016-2009 interface viewpoint

---

> **What was measured, 2026-08-18 17:25 (+06):**
>
> | Measure | Count |
> |---|---:|
> | External integrations catalogued in `05-03` §2 | **47** — contiguous `INT-001`…`INT-047`, no gaps, no duplicates |
> | Of those, **P0** — the business stops without them | **13** — counted from `05-03` §2's rows; its own summary states 12 (`PE-A-01`) |
> | Integrations with a **technology assignment** (Tech Stack §12.2.4) | **47** |
> | Integrations with an **interface control document** | **0** |
> | Integrations with a **tested** fallback (`NFR-050` requires one for every P0) | **0** |
> | Counterparties with a `Determined` field-level disclosure register (`AP-012`) | **9 of 53** |
> | Integrations cited in only **two** files in the whole estate | **8** |
>
> `05-03` §2 catalogues each integration as **one table row**. A payment reconciliation dispute with
> bKash, a rejected VAT return, or a courier holding a customer's device cannot be adjudicated from a
> table row. **This document issues 14 ICDs and states, per integration, why the remaining 33 are
> deferred rather than pretending otherwise.**

---

## 1. Purpose

An ICD is the **bilateral contract** for one external interface: what crosses the boundary, in what
form, under what authentication, with what failure semantics, what data leaves, under what lawful
basis, and what happens when the counterparty is unavailable. `IN-001` fixes the patterns and the
resilience ladder; `IN-002` and `IN-003` fix the estate's *own* contracts. **This document is where
the estate meets someone else's.**

It does three things. It defines the **ICD standard** — the sections every ICD carries, so 47 of
them are comparable. It **issues the ICDs** for the twelve P0 integrations and two structurally
significant others. And it records the **counterparty findings** authoring them produced, several of
which change who the counterparty is.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The ICD standard — sixteen mandatory sections |
| 2 | The **common clauses** every ICD inherits from `IN-001` |
| 3 | **Fourteen issued ICDs**, covering all **13** P0 integrations plus CON-03 and `INT-047` |
| 4 | Per-integration timeouts, retry ladders, breaker settings and fallbacks |
| 5 | Per-integration data-egress position against `AP-012` and `NFR-098` |
| 6 | The **counterparty-identity findings** — where `05-03` names the wrong party |
| 7 | Deferral register for the 33 not issued, each with a reason and a review wave |
| 8 | ICD lifecycle: draft → agreed → signed → in force → superseded |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Payment flow design, settlement, reconciliation, ledger posting | **`IN-007`** | The money design is larger than an ICD; `IN-007` designs it, the ICDs here carry the wire contract |
| Webhook signature scheme and receiver contract | **`IN-006`** | Common across all inbound webhooks, so it is specified once |
| Sandbox provisioning and certification | **`IN-008`** | Verification, not contract |
| The estate's own API contracts | `IN-002` | Unilateral publication, not a bilateral contract |
| Commercial terms, SLAs, pricing, liability | `CO-*` | An ICD is technical. `IN-A-13` records that the two must reference each other and currently do not |
| Processor contracts under `NFR-098` | Legal Counsel, `SC-*` | This document names where one is required; Legal writes it |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Integration engineers | §4–§9 are the build specification |
| Counterparty engineers | An issued ICD is the document exchanged and agreed with them |
| Legal Counsel | §3.4's data-egress section per ICD is the input to `NFR-098` processor contracts |
| Treasury / Finance | §7 (NBR) and §8 (BEFTN) change who the counterparty is |
| QA lead | Every ICD's §12 failure matrix is a test charter (`IN-008`) |
| Service desk | Every ICD's §11 fallback is a runbook input (`OP-014`) |

---

## 2. Basis and Inputs, and the ICD Standard

> **Template note.** `TPL_Guiding_Document.md` places *Basis and Inputs* at §2 and the
> standard-governed body at §3. This document merges them, because an ICD standard **is** the
> basis every issued ICD inherits, and splitting them would separate the sixteen mandatory
> sections (§2.4) from the clauses that populate them (§2.5). §2.1–§2.3 carry the template's three
> required sub-parts unchanged; §2.4–§2.6 carry the standard. Recorded as a deliberate deviation
> in `PGD-AUDIT-006`, not an omission.

### 2.1 Standards conformance

| Standard | Clause / concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **IEEE 1016-2009** | §5.7 **interface viewpoint** — interface identification, resources, attributes, detailed design | §2.4's sixteen sections are that viewpoint applied to an *external* interface | **Extension, not departure.** IEEE 1016 addresses interfaces within one design; §2.4 adds the bilateral elements — data-egress lawful basis, change-control obligations *from* the counterparty, and a signed lifecycle |
| **ISO/IEC/IEEE 42010:2022** | Context view, external entity register | Inherits `AR-001` §5.2, which names each external entity and the architectural obligation it creates | None |
| **Bangladesh Bank BEFTN Operating Rules** | File structure, Standard Entry Class codes, participant definition | §8 | **The rules are conformed to *through the sponsoring bank*** — see `IN-004-D-03` |
| **Standard Webhooks** | Inbound verification where a counterparty offers it | §2.5 delegates to `IN-006` §4 | None |
| **OpenAPI 3.1** | Where a counterparty publishes a machine-readable contract | Referenced, never re-authored | **Departure:** no counterparty in the 47 publishes one that was locatable at 2026-08-18, so every ICD is written from prose documentation |
| **PCI DSS v4.0** | Scope definition | §6 and `IN-007` §4 hold the boundary at the acquirer's hosted page | Not a certification claim — `IN-007` §4.4 |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Integration catalogue | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §2, §7 | The 47 integrations, their pattern, wave, priority and declared fallback |
| Technology assignment | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2.4 | A named client technology per integration — 47 of 47, no gaps |
| `M28` §12.4 | `.../K_Platform_and_Technology/M28_*.md` | The connector framework and the seven `INT-IPF-*` infrastructure integrations |
| **`AP-012`** | `../../project_content/15_Integration_and_Developer_Content/AP-012_*.md` | The field-level disclosure register — **9 of 53 counterparties `Determined`** |
| `AP-009` | Ibid. | Payment-gateway runbook content: failure modes, manual fallback, drills, escalation |
| `AP-010` | Ibid. | Sandbox onboarding and test-credential content |
| **`IN-001`** §7.2, §8, §10 | `./IN-001_*.md` | Per-counterparty timeouts, the anticorruption obligation, the integration register fields |
| **Counterparty documentation** | External — see §25 | bKash, Nagad, SSLCOMMERZ, BEFTN, NBR IVAS, the courier market. **Every claim carries `verified_on: 2026-08-18`** |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`AP-06` (high)** — three payment availability commitments do not reconcile | `AUDIT-016` | **Contributes the evidence.** §4.3 `B-01` records bKash's published 30-second timeout, which is the empirical basis of limb 1; §6.2 records the single-acquirer position behind limb 3. **`IN-007` §9 reconciles all three** |
| **`AP-08` (high)** — Class `B` register incompletable; three W3 couriers `Undetermined`; no DPIA, processor inventory or DPO | `AUDIT-016` | **Contributes decisively.** §16 and §17 issue the affected ICDs **as blocked**, with the named prerequisites, owners and dates. Closes with Legal Counsel's action, not with this document |
| `AP-07` (high) — ITSM is `P3`/W7 against a W4 "condition of contract" | `AUDIT-016` | §19 — the ICD is **deferred rather than written against a false premise**, and the commercial exposure is restated |
| `AP-12` (medium) — the partner sandbox is a seventh environment | `AUDIT-016` | Each ICD's §14 records sandbox availability; **`IN-008` §6 specifies the environment** |
| `AP-04` (high) — no webhook signature scheme | `AUDIT-016` | Each ICD's inbound verification clause delegates to **`IN-006` §8.4** |
| `IN-001` `IN-A-04` — `INT-038` and `INT-005` counterparty identities | `IN-001` §7.2 | **Closed here.** §7.1 and §8.1, with `IN-004-D-02` and `IN-004-D-03` |
| `NFR-050` — every P0 integration has a documented, **tested** fallback | `05-06` | Every issued ICD declares one; **`IN-008` §9 makes "tested" mean a timed drill.** Currently **0 of 13** |

### 2.4 Sixteen mandatory sections

Every ICD, in this order. **A missing section is a defect, and a section marked "not applicable"
must say why** — the estate's recurring failure is the silent omission, not the stated gap.

| § | Section | What it must establish |
|---|---|---|
| 1 | **Identity** | `INT-nnn`, counterparty **legal entity**, our owning module, our owning role, their contact channel |
| 2 | **Purpose and business consequence** | What stops if this interface stops, in business terms |
| 3 | **Pattern and direction** | One of `IN-001` §5's five patterns; inbound, outbound or bidirectional |
| 4 | **Transport and endpoints** | Protocol, hosts per environment, ports, TLS version, IP allow-listing both ways |
| 5 | **Authentication and credentials** | Scheme, key material, rotation, vault path, expiry alerting |
| 6 | **Operations** | Every call, request and response, with field-level detail |
| 7 | **Idempotency and duplicate handling** | The counterparty's key, ours, and the reconciliation when they disagree |
| 8 | **Data egress** | Every field that leaves, its `AP-012` classification, lawful basis, residency position |
| 9 | **Timing** | Timeout, retry ladder, breaker thresholds, published latency expectation |
| 10 | **Ordering and consistency** | What may arrive out of order; what is authoritative |
| 11 | **Failure and fallback** | Failure modes, detection, the declared manual fallback, drill cadence |
| 12 | **Failure matrix** | Each failure mode → detection → user-visible behaviour → recovery |
| 13 | **Monitoring** | Health signal, thresholds, who is alerted |
| 14 | **Environments and test data** | Sandbox availability, test credentials, whether real data is possible |
| 15 | **Change control** | Their notice obligation to us, ours to them, version support window |
| 16 | **Open items** | Named, owned, dated |

### 2.5 Clauses every ICD inherits

Stated once here rather than repeated 47 times.

| Clause | Source |
|---|---|
| **No external system's model enters the domain** — every interface is mediated by an anticorruption layer | `IN-001` `AC-01` |
| Identifier translation both ways, persisted; enumeration translation with an alerting `unknown` branch | `IN-001` `AC-02`, `AC-03` |
| **Money is `{amount: string-decimal, currency}`**; time is RFC 3339 UTC at the boundary | `IN-001` `AC-04`, `AC-05` |
| Counterparty errors are translated into the `AP-006` code set; a counterparty's error string never reaches a user | `IN-001` `AC-06` |
| **Only the fields the counterparty's purpose requires** leave, per `AP-012`'s field-level register | `IP-10`, `IN-001` `AC-07` |
| **Residency-classified values cross only through CD-233**, which is also the only place the transfer is logged | `AR-001` `LB-08`, `NFR-099` |
| **The counterparty's SDK appears only inside the ACL.** No module imports it | `IN-001` `AC-09`, `FF-41` |
| No synchronous external call inside a database transaction; none on the critical path of a state transition | `IN-001` `PT-02`, `PT-03`, `FF-42` |
| **An inbound notification is a hint, never authority** — verify, deduplicate, acknowledge, then **read back** | `IN-001` `PT-05`, `IN-001-D-06` |
| Every outbound destination is on the **Z6 egress allow-list** | `AR-001` §8.1, `FF-44` |
| Credentials are vault-referenced with an expiry; **none in code or configuration** | `IP-07`, `NFR-062` |
| **Failover is driven by circuit-breaker state, not the monitoring window** | `IN-001-D-02` |
| Every P0 integration has a **documented, tested** fallback, drilled each wave gate | `NFR-050`, `IN-001` `FB-02` |

### 2.6 ICD lifecycle

| State | Meaning | Gate to leave |
|---|---|---|
| **Draft** | Written from our side, from published counterparty documentation | Internal review |
| **Agreed** | The counterparty's engineers have confirmed it describes their interface | Their written confirmation |
| **Signed** | Countersigned, and referenced by the commercial agreement | Legal + Commercial |
| **In force** | Live; changes follow §15 | — |
| **Superseded** | Replaced; retained with a pointer (`GV-011` `CM-21`) | — |

> **All fourteen ICDs issued here are `Draft`.** They are written from published counterparty
> documentation verified on 2026-08-18, not from a bilateral conversation. **A Draft ICD is a
> proposal to the counterparty, not a description of an agreed interface**, and `IN-001` `LC-01`'s
> S2→S3 gate requires `Agreed` before a connector is built.

---

## 3. Issue Register

| ICD | `INT-nnn` | Counterparty | Pri | Wave | Pattern | State |
|---|---|---|:--:|:--:|---|---|
| §4 | `INT-001` | **bKash** | P0 | W3 | P1 sync + P4 webhook | Draft |
| §5 | `INT-002` | **Nagad** | P0 | W3 | P1 sync + P4 webhook | Draft |
| §6 | `INT-003` | **SSLCOMMERZ** | P0 | W3 | P1 sync + P4 webhook | Draft |
| §7 | `INT-038` | **NBR — VAT Online / IVAS** | P0 | W4 | **P5 batch, manual** | Draft |
| §8 | `INT-005` | **The sponsoring bank** (BEFTN) | P0 | W5 | P5 batch file | Draft |
| §9 | `INT-006` | Bank statement import | P0 | W3 | P5 batch / P1 | Draft |
| §10 | `INT-010`, `INT-011` | Bangladesh SMS gateways | P0 | W1 | P1 sync | Draft |
| §11 | `INT-012` | WhatsApp Business Cloud API | P0 | W1 | P1 + P4 | Draft |
| §12 | `INT-013` | Email (SMTP/API + IMAP) | P0 | W1 | P1 + inbound parse | Draft |
| §13 | `INT-014` | Push — FCM / APNs | P0 | W2 | P1 sync | Draft |
| §14 | `INT-019` | Google Maps Platform | P0 | W2 | P1 sync | Draft |
| §15 | `INT-023` | Traccar GPS | P0 | W2 | P1 + WebSocket | Draft |
| §16 | `INT-034` | NID / identity verification | P0 | W7 | P1 sync | **Blocked** |
| §17 | `INT-024`…`026` | Couriers — Pathao, RedX, Steadfast/Sundarban | P2 | W3 | P1 + P4 | **Blocked** |
| §18 | **CON-03** | The portal platform | — | **W1** | All five | Draft |
| §19 | `INT-047` | Client ITSM (ServiceNow / Jira) | P3 | W7 | P1 + P4 | Deferred |

**Thirteen P0 integrations, thirteen covered.** §17 covers three integrations in one ICD because the
three couriers present the same interface shape and the same blocking condition.

---

## 4. `INT-001` — bKash

### 4.1 Identity and purpose

| Field | Value |
|---|---|
| Counterparty | bKash Limited |
| Our modules | M19, M20 (business meaning) · M28 (transport) |
| Consequence if unavailable | **The dominant consumer payment rail in Bangladesh stops.** Cash at counter and payment-link resend remain |
| Pattern | **P1 synchronous** for the payment lifecycle · **P4 inbound webhook** for asynchronous outcomes |

### 4.2 Operations — the tokenised checkout flow

Verified against bKash's published Tokenized Checkout API integration guide, **2026-08-18**:

| # | Operation | Purpose |
|---|---|---|
| 1 | `POST /tokenized/checkout/token/grant` | Obtain an access token from app key + app secret |
| 2 | `POST /tokenized/checkout/create` | Initiate a payment session |
| 3 | `POST /tokenized/checkout/execute` | Confirm after the customer approves |
| 4 | `POST /tokenized/checkout/payment/status` | **Query — the authoritative read** |
| 5 | `POST /tokenized/checkout/payment/refund` | Refund a transaction |

| Environment | Host |
|---|---|
| Sandbox | `*.sandbox.bka.sh` |
| Production | `*.pay.bka.sh` |

### 4.3 The three facts that shape everything else

| # | Fact | Consequence |
|---|---|---|
| **B-01** | **bKash's own guidance instructs merchants to set a 30-second API timeout on all calls** | **`NFR-042`'s 3 s p95 payment confirmation round trip cannot be met end to end.** This is the empirical basis of audit `AP-06` and of ruling `IN-001-D-03` |
| **B-02** | The flow is `create → execute → **query**` | The query is not optional diagnostics; it is **the authoritative read** that `IN-001` `PT-05` requires |
| **B-03** | App key, app secret, username and password are issued at onboarding and **must never appear in frontend code** | All calls originate server-side, from inside the ACL, through the Z6 egress proxy |

### 4.4 Timing

| Setting | Value | Basis |
|---|---|---|
| Connect / read timeout | **30 s** | B-01 |
| Bulkhead | **Its own connection pool and concurrency cap** | A 30-second counterparty must not exhaust the shared pool (`IN-001` §7.1 rung 5) |
| Retry | **3 attempts, idempotent operations only** — `token/grant` and `payment/status` are retryable; **`execute` is not, without the idempotency ledger** | `IN-001` §7.3 |
| Breaker | Open at ≥50% failures over 20 calls; half-open probe after 30 s | `IN-001-D-02` |
| Published expectation | **Internal processing ≤ 3 s p95; end-to-end up to 30 s** | `IN-001-D-03` |

### 4.5 Idempotency

| Layer | Key |
|---|---|
| Our API (`POST /api/v1/payments`) | `Idempotency-Key`, client UUID, **7-day retention** (`IN-001` `ID-08`) |
| bKash | `merchantInvoiceNumber` — ours, and it must be stable across retries |
| Reconciliation when they disagree | **`payment/status` is authoritative.** Never our record, never the webhook body |

### 4.6 Data egress

| Field | Class | Lawful basis | Note |
|---|---|---|---|
| Amount, currency | Non-personal | Contract | |
| `merchantInvoiceNumber` | Pseudonymous | Contract | **Must not encode a customer identifier** |
| Customer MSISDN | **Personal** | Contract performance | The minimum the rail requires |
| Customer name | **Personal** | Contract performance | **Send only if the rail requires it.** `IP-10` |
| NID, TIN, biometric | **Residency-restricted** | — | **Never sent. Never.** `NFR-099`, `AR-001` `LB-08` |

**`AP-012` register row: `Undetermined` at issue.** `DS-01`'s default is refusal, so this must be
`Determined` before the W3 gate (`IN-001` `LC-01`).

### 4.7 Failure matrix

| Failure | Detection | User sees | Recovery |
|---|---|---|---|
| `token/grant` fails | 4xx/5xx | "Payment is temporarily unavailable — please choose another method" | Breaker opens; alternative rail offered |
| `create` times out | 30 s | Same, with the order preserved | No payment was created; safe to retry with a new key |
| **`execute` times out** | 30 s | **"We are confirming your payment"** — never "failed" | **Outcome UNKNOWN. Poll `payment/status`. Never blind-resubmit** |
| Webhook received, signature invalid | Verification | Nothing | `401`; **security event** |
| Webhook received, `payment/status` disagrees | Read-back | Status per the rail | **The rail wins.** Divergence alert |
| Rail down | Breaker | Alternative gateway; cash at counter | `platform.fallback_engaged`; link resent on recovery |

---

## 5. `INT-002` — Nagad

### 5.1 What is different, and why it matters

Verified against Nagad's merchant API integration guidance, **2026-08-18**:

| # | Fact | Consequence |
|---|---|---|
| **N-01** | **The merchant generates an RSA key pair.** The merchant's **private** key signs sensitive data before sending | Key generation, custody and rotation are **ours**, and the private key is vault-held and never leaves it |
| **N-02** | Nagad publishes an **RSA public key**; the merchant encrypts sensitive request data with it, and **verifies Nagad's response signatures** with it | Signature verification is **mandatory on responses**, not only requests — unusual among the rails and easy to skip |
| **N-03** | The merchant's public key is uploaded through Nagad's portal | **A manual, out-of-band step** in an otherwise automated onboarding — it belongs in the runbook, not in code |

### 5.2 Consequences for the design

| Concern | Position |
|---|---|
| Cryptographic work | RSA sign + encrypt per request, verify per response. **Budget for it** — this is why §5.3 sets a 20 s timeout rather than bKash's 30 s or Maps' 3 s |
| Key rotation | **The hardest rotation in the estate**: it requires a portal upload and a coordinated cutover. An overlap window must be agreed with Nagad before the first rotation, not at it. **`IN-A-14`** |
| Failure mode unique to this rail | **A signature that fails to verify is not a payment failure** — it is either a key mismatch or an integrity event. The two must not share an error code; `dependency.*` for the former, a security event for the latter |
| Sandbox | Test merchant ID and Nagad public key issued after registration; demo customer accounts |

### 5.3 Timing and failure

| Setting | Value |
|---|---|
| Timeout | **20 s** — crypto at both ends |
| Retry | 3, idempotent operations only |
| Breaker | As `IN-001` §7.1 |
| Fallback | Alternative gateway; cash at counter |
| **Read-back** | **Mandatory.** `IN-001` `PT-05` |

---

## 6. `INT-003` — SSLCOMMERZ

### 6.1 The rule that must not be shortcut

Verified against SSLCOMMERZ's published developer documentation, **2026-08-18**:

> **An IPN carries an MD5 `verify_sign`, and signature verification alone is NOT the published
> sufficient condition. The merchant must call the Transaction Validation API and act on its
> `VALID` / `FAILED` / `CANCELLED` result before treating a payment as complete.**

| # | Step | Non-negotiable |
|---|---|---|
| 1 | Receive the IPN POST at `/hooks/v1/sslcommerz` | |
| 2 | **Verify `verify_sign`** — MD5 over the documented value set with the store password | ✔ |
| 3 | Deduplicate on `tran_id` | ✔ |
| 4 | Persist the raw envelope verbatim | ✔ |
| 5 | Acknowledge `200` fast | ✔ |
| 6 | **Call the Transaction Validation API with transaction id, amount and currency** | ✔ **This is the step that gets skipped** |
| 7 | Apply the state change from **that** response | ✔ |

> **`IN-A-15` (high).** MD5 is the algorithm SSLCOMMERZ specifies for `verify_sign`. **MD5 is not
> collision-resistant**, which is why step 6 is not defence in depth but **the actual control** — the
> signature is a filter, the validation call is the authority. Any implementation that treats the
> MD5 check as sufficient has a financial-fraud exposure. Recorded so it is a stated design position
> rather than an implementation detail someone optimises away.

### 6.2 The single-acquirer problem

| Fact | Consequence |
|---|---|
| **`INT-003` is the only card acquirer in the entire 47-integration catalogue** | **The card path has no failover to be had** |
| `NFR-048` requires payment path availability ≥ 99.95% **with multi-gateway failover** | ~22 minutes of downtime per month, unachievable for cards with one acquirer |
| `IN-001` `FB-05` records it | Either procure a second acquirer, or restate `NFR-048` as applying to the **aggregate** payment path rather than to every method |

**This is audit `AP-06`'s third limb, and it is the one that cannot be resolved by a design
decision.** It is a procurement decision. `IN-001` Q-05, owned by CTO + CFO, needed at W3.

### 6.3 Timing

| Setting | Value |
|---|---|
| Timeout | **15 s** — the validation call is on the critical path of "paid" |
| Retry | Validation call: 3, with backoff. IPN acknowledgement: never retried by us |
| Fallback | bKash / Nagad for wallet-capable customers; **cash at counter for cards** |

---

## 7. `INT-038` — NBR VAT Online / IVAS

### 7.1 The counterparty finding

> **`IN-A-04` (high) — restated here in full because it changes the design.**
>
> `05-03` §2.6 assigns `INT-038` the pattern **"File / API"**. Verification at **2026-08-18** finds:
>
> - VAT return submission runs through the **NBR VAT Online portal at `vat.gov.bd`**, on the
>   **Integrated VAT Administration System (IVAS)**.
> - The return is **Mushak-9.1**, filed **monthly, by the 15th**.
> - **No publicly documented machine API for Mushak-9.1 submission was found.**
>
> **`INT-038` is therefore a `P5` batch integration whose "transmission" is a human uploading or
> keying a generated return into a portal.** That is not a degraded mode; on current evidence it is
> the *only* mode.

### 7.2 What the design must therefore be

| Concern | Position |
|---|---|
| What we build | **CD-195 `cd_mushak_return` generates a complete, arithmetically reconciled Mushak-9.1** from the ledger, in the portal's required layout |
| What crosses the boundary | A **file and a human**, not an API call |
| The "fallback" | **There is no fallback, because the manual path *is* the path.** `05-03` §7's *"manual portal filing from the generated return"* is the primary mode |
| What must be tested | **Generation accuracy and completeness**, not connectivity |
| The real risk | **Not availability — correctness.** IVAS flags late submissions and data mismatches, and a mismatch is a compliance event with a deadline attached |
| Freeze point | Stated and owned by Finance (`IN-001` `BF-03`), not implied by a job schedule |
| Retention | The generated return and its acknowledgement retained **7 years**, immutably (`BF-04`) |

### 7.3 Open item

**`IN-001` Q-06** — is there *any* machine API for IVAS submission, whether public or issued to
registered filers? Owner Head of Tax + CTO, needed **W4 minus 3 months**. If yes, this ICD is
rewritten; if no, it is correct and the effort moves from integration to report generation.

> **This is a case where the honest ICD is smaller than the register implies, and saying so is worth
> more than writing an API contract against an API nobody has seen.**

---

## 8. `INT-005` — BEFTN, through the sponsoring bank

### 8.1 The counterparty finding

> **`IN-A-04` second limb. `05-03` §2.1 names the counterparty "Bank BEFTN". That is not a
> counterparty.**
>
> Verified against Bangladesh Bank's BEFTN Operating Rules, **2026-08-18**:
>
> - BEFTN is Bangladesh Bank's **interbank batch clearing network**, live since 28 February 2011.
> - **Participants are banks.** 1000FiX is not a participant and cannot be one.
> - The file format is **fixed-width, record-based**: file header, batch header, entry detail and
>   control records, with three-digit **Standard Entry Class (SEC) codes** identifying the
>   application.
> - Clearing is **batch, typically T+1**.
>
> **1000FiX's counterparty is its own sponsoring bank**, and the file 1000FiX produces is **that
> bank's implementation** of the BEFTN record format — including its own header conventions, its own
> transmission channel (secure file transfer, and in some banks an API or MQ), and its own cut-off
> times. **Two banks will not accept the same file.**

### 8.2 What this changes

| Before | After |
|---|---|
| One ICD against "BEFTN" | **One ICD per sponsoring bank**, and the bank must be named before it can be written |
| Format from Bangladesh Bank's rules | Format from **the bank's** specification, which conforms to those rules |
| Cut-off from the network | **Cut-off from the bank**, which is earlier than the network's |

**`IN-001` Q-07** — which bank, and what is *its* specification? Owner CFO + Treasury, needed
**W5 minus 4 months**. **`CD-100 cd_beftn` cannot be specified until this is answered.**

### 8.3 The clauses that hold regardless of bank

| # | Rule | Basis |
|---|---|---|
| BF-01 | Header, control record and **monotonic sequence number**; a gap is an incident | `IN-001` §7.5 |
| BF-02 | **Control totals** — record count and value sum — verified on generation and on acknowledgement. Mismatch rejects the **whole file** | `PT-06` |
| BF-03 | A stated **freeze point**, owned by Payroll/Treasury as a business decision | |
| BF-04 | File and acknowledgement retained immutably for the statutory period | |
| BF-05 | **Manual submission through the bank's portal is the fallback, exercised before the first live run** | `NFR-050` |
| BF-06 | Returns and rejections have a **declared reconciliation window** with an alert when it lapses | |

> **`IN-A-16` (high).** A payroll disbursement file is the estate's highest-consequence batch. `PT-06`
> — never partially applied — is what prevents half a payroll run, and **half a payroll run is worse
> than none**: it is a same-day treasury and employee-relations incident with no clean reversal.

---

## 9. `INT-006` — Bank statement import

| Concern | Position |
|---|---|
| Pattern | **P5 batch** where the bank provides a file; **P1** where it provides an API |
| Counterparty | The same sponsoring bank as §8 — so §8's open item blocks this too |
| Idempotency | **Statement line hash + statement sequence.** Re-importing the same statement must be a no-op |
| The real risk | **Duplicate import**, not failure. A statement imported twice double-credits reconciliation |
| Ordering | Statements are ordered by sequence; **a gap halts import and alerts** |
| Fallback | Manual statement upload (`05-03` §7) |
| Reconciliation | Divergence between imported balance and ledger publishes `platform.reconciliation_divergence` |

---

## 10. `INT-010`, `INT-011` — SMS gateways

| Concern | Position |
|---|---|
| Wave | **W1 — the first external integration the programme builds** |
| Pattern | P1 synchronous send; delivery receipts inbound where offered |
| Failover | `INT-011` is the declared failover, and **failover is breaker-driven** (`IN-001-D-02`) |
| Bengali | **Unicode SMS is 70 characters per segment, not 160.** A Bengali message segments roughly 2.3× more than the equivalent English one — a cost and a truncation risk, and it belongs in the ICD because it is a wire-level property |
| Sender ID | Masked sender registration is a **regulatory and commercial prerequisite**, with a lead time — named here so it is not discovered at W1 |
| Data egress | **MSISDN and message body.** The body may contain an OTP, a name or an order reference — `AP-012` classification `personal` |
| Retry | 3 with backoff; **never retry a message whose delivery receipt is pending** |
| Idempotency | Our message id, echoed; duplicate suppression window of 60 s on identical `(msisdn, body)` |
| Fallback | Failover gateway → WhatsApp → push → queue for retry (`05-03` §7) |

> **`IN-A-17` (medium).** `AR-009` E4: **a notification is a command, not an event.** The SMS ICD
> therefore sits behind M27's notification service, and **no module calls the SMS gateway directly**.
> Stated in the ICD because a direct call is the shortcut a developer under W1 pressure will take,
> and `FF-41` is what catches it.

---

## 11. `INT-012` — WhatsApp Business Cloud API

| Concern | Position |
|---|---|
| Pattern | P1 send · **P4 inbound webhook** for delivery status and customer replies |
| **Template approval** | Business-initiated messages require **pre-approved templates**. Template authoring, submission and approval is a **content and lead-time dependency**, owned with `NT-*`, not an engineering task |
| Session window | Free-form replies are permitted only inside a customer-initiated session window; outside it, a template is required. **This is a business-rule constraint expressed at the wire** |
| Webhook verification | Provider-specific; **`IN-006` §6 carries the per-provider verification table** |
| Data egress | MSISDN, message body, template parameters — `personal` |
| Fallback | SMS → email → in-app inbox |

---

## 12. `INT-013` — Email

| Concern | Position |
|---|---|
| Pattern | P1 outbound · **IMAP inbound parsing to tickets** |
| **Inbound parsing is the risk** | An inbound mailbox is an **unauthenticated input channel into the ticketing system**. Attachment handling, sender spoofing and auto-reply loops are the failure modes |
| Loop protection | Auto-reply detection and a per-sender rate cap. **An auto-responder pair can generate thousands of tickets overnight** |
| Deliverability | SPF, DKIM and DMARC are **prerequisites**, with DNS lead time |
| Data egress | Address, subject, body, attachments — `personal`, and an attachment may carry far more |

---

## 13. `INT-014` — Push (FCM / APNs)

| Concern | Position |
|---|---|
| Pattern | P1 send |
| Token lifecycle | Device tokens expire and are reissued. **A stale token is a silent non-delivery**, and silent non-delivery of a dispatch notification is an operational failure |
| **Fallback** | **SMS for critical messages** (`05-03` §7) — which means every push must declare whether it is critical |
| Data egress | Device token, notification title and body — `personal` where the body names a person or an order |
| Certificate expiry | APNs credentials expire; `platform.credential_expiring` at **30 and 7 days** |

---

## 14. `INT-019` — Google Maps Platform

| Concern | Position |
|---|---|
| Pattern | P1 sync — geocoding, map display, navigation handoff |
| Timeout | **3 s.** Interactive; a slow map is a degraded booking flow |
| **Licence constraint** | Terms restrict caching and derived storage of geocoding results. **`IN-A-18` (medium): `05-03` §7's fallback is "cached geocodes", and the permissible cache duration and scope is a licence question Legal must answer** — the fallback may be narrower than the estate assumes |
| Cost | Per-request billing. A retry storm is a **cost** incident as well as an availability one |
| Fallback | Cached geocodes (subject to the above) → OSRM-only routing → manual address entry |
| Data egress | Addresses and coordinates — `personal` when tied to a customer |

---

## 15. `INT-023` — Traccar GPS

| Concern | Position |
|---|---|
| Pattern | P1 REST + **WebSocket** position streaming |
| Deployment | **Self-hosted (TC-020)** — inside the estate's own boundary, so egress rules differ |
| Volume | Continuous position updates from 200–400 technicians and vehicles. **Throttled before publication** — a domain event per GPS ping is a delivery ladder per ping (`IN-001` §9.3) |
| Data class | **Employee location is personal data**, and continuous tracking is among the most sensitive processing the estate performs. Lawful basis, retention and the employee-facing transparency notice are `SC-*`/`LG-*` items, named here because the ICD is where the data volume becomes visible |
| Fallback | Last known position; manual status updates by the technician |

---

## 16. `INT-034` — NID / identity verification — **BLOCKED**

### 16.1 Why this ICD cannot be completed

`AUDIT-016` `AP-08` records it, and it remains true:

> **The highest-risk single row in `AP-012`** is `INT-034`. It transmits a **national identifier**
> and requires all three of:
>
> | # | Requirement | Status |
> |---|---|:--:|
> | 1 | `LG-2S` **specific consent** under `NFR-091` | ✘ |
> | 2 | The `NFR-086b` gate — an **Authority notification record and a documented safeguard before the transfer executes** | ✘ |
> | 3 | Confirmation that the verification service is **Bangladesh-resident** under `NFR-086` | ✘ |
>
> **None of the three exists.**

### 16.2 The design position, stated so it is not later invented

| # | Rule |
|---|---|
| **NID-01** | The NID number is **residency-classified**. It is read and written **only** through CD-233, never by direct query, not even in a migration or a backfill (`AR-001` `LB-08`) |
| **NID-02** | **It never appears in an event payload** (`AR-009` P-03, `IN-003` `SC-07`) |
| **NID-03** | It never appears in an API response body; a verification returns a **result**, not the identifier |
| **NID-04** | The verification call is the **only** egress point, logged per-read (`AR-001` Z4) |
| **NID-05** | **The counterparty must be Bangladesh-resident.** If it is not, the transfer is a cross-border transfer of a government unique identifier under `NFR-099` and requires Authority notification and disclosed safeguards |
| **NID-06** | Fallback is **manual document review by compliance** — a human path, and the one that operates until NID-01…NID-05 are satisfied |

> **`IN-001` §10.1 `LC-01` applies at full strength: this integration may not reach production while
> its `AP-012` rows are `Undetermined`.** Identity verification is the control the entire marketplace
> trust model rests on, and it is W7 — which is time enough, if the three prerequisites are started
> now rather than at W7.

---

## 17. `INT-024`…`INT-026` — Couriers — **BLOCKED**

### 17.1 The blocking condition

`AUDIT-016` `AP-08`, gap 2:

> **The three W3 courier integrations are `Undetermined` in `AP-012` and carry customer name, phone
> and address.** Under `AP-012` `DS-01`, **no consignment may be booked with Pathao, RedX or
> Steadfast/Sundarban until their rows are determined and `NFR-098` processor contracts exist.**
>
> **This blocks W3 pick-and-drop — in the same wave `G3-07` requires unbroken custody with zero
> exceptions.**

### 17.2 The common interface shape

Verified against the Bangladesh courier market, **2026-08-18** — the three present materially the
same interface:

| # | Operation | Notes |
|---|---|---|
| 1 | Create consignment — recipient name, phone, address, **COD amount** | Returns a **consignment id / tracking number** |
| 2 | Query status | Polling fallback |
| 3 | **Inbound webhook** on status change — delivered, returned, failed | The primary status mechanism |
| 4 | Cancel / reschedule | Availability varies by courier |

| Concern | Position |
|---|---|
| **COD reconciliation** | **The highest-risk element, and it is a money path.** COD collected by a courier is our cash in their hands. Remittance reconciliation is `IN-007`'s, not this ICD's, but the **per-consignment COD amount and its remitted state are ICD fields** |
| Status vocabulary | **Three different vocabularies.** `IN-001` `AC-03`: enumeration translation with an **alerting `unknown` branch** — a courier status the mapping has never seen must not silently become `in_transit` |
| Webhook verification | **Per-courier and inconsistent.** `IN-006` §6 carries the table; where a courier offers no signature, the fallback is **IP allow-listing plus mandatory read-back** (`PT-05`) |
| Custody | Every transition publishes `consignment.custody_transferred` — `G3-07`'s unbroken-custody evidence |
| Data egress | **Name, phone, full address** — `personal`, to a processor. `NFR-098` requires equivalent obligations flowed by contract |
| Fallback | Manual booking through the courier's own portal |

### 17.3 What Legal must produce, and by when

| # | Item | Owner | Needed by |
|---|---|---|---|
| 1 | `AP-012` rows **`Determined`** for all three | Legal Counsel | **W3 − 3 months** |
| 2 | `NFR-098` **processor contracts** with all three | Legal Counsel | W3 − 3 months |
| 3 | Confirmation that no sub-processor receives the data without equivalent obligations | Legal Counsel | W3 − 3 months |

> **`AP-08` is High rather than Critical because `DS-01`'s default is refusal** — the exposure is
> realised only if the promotion gate is bypassed. **It becomes Critical the first time a consignment
> ships with `Undetermined` rows.**

---

## 18. CON-03 — The portal platform

### 18.1 Why it has an ICD at all

`CON-03` states the Next.js 15 + Payload CMS 3 platform cannot be replaced. It is the **only
interface where both sides are ours and neither side owns the whole** — which is precisely why it
needs a bilateral document rather than a unilateral contract.

### 18.2 The measured state of the contract

| Half | Declared in `05-03` §3 | Owned by a module | Gap |
|---|---:|---:|---:|
| Synchronous — §3.2 | 22 endpoints | **10** | **12 — 54.5%** |
| Asynchronous — §3.3 | 11 webhooks | **3** | **8 — 72.7%** |

**Full detail in `IN-001` §9.2.** `/api/v1/payments/confirm` and `payment.received` are both in the
gap, so **the W1 portal contract carries a money path with no producer on either side.**

### 18.3 Contract terms

From `05-03` §3.4, with this document's additions:

| Term | Value |
|---|---|
| Versioning | **Two concurrent API versions**; six months' notice before removal |
| Idempotency | Every POST accepts `Idempotency-Key`; duplicates return the original result |
| Authentication | OAuth 2.0 client credentials per environment, short-lived tokens — `oauthMachine` in `IN-002` |
| Rate limits | **600 req/min per portal instance, burst 100/s** — the `portal` class, and **the only rate-limit figure in the estate with a source** (`AP-005` §4.7) |
| Timeouts | Portal 5 s on synchronous calls; **ERP responds within 2 s at p95** |
| Degradation | Cached catalogue; **queued booking confirmed on recovery** |
| Reconciliation | **Nightly count reconciliation** on orders and customers; divergence alerts |
| **Added: `LB-07` clarification** | The portal may hold an **intent it has not yet submitted**; it may **never** hold a fact (`IN-001` §9.4) |
| **Added: projection channel** | `service_order.status_changed` and `consignment.status_changed` are **declared projections with named projectors** (`IN-003` §7.3.3) |

---

## 19. `INT-047` — Client ITSM — deferred, with a commercial finding

`AUDIT-016` `AP-07` (high, open) is a commercial exposure, not a technical one, and it is restated
because an ICD would otherwise be written against a false premise:

| Capability | Wave | Priority |
|---|:--:|:--:|
| Corporate portal go-live (`P04`) | **W4 — month 18** | — |
| **Client ITSM ticket exchange (`INT-047`)** | **W7 — month 30** | **P3 — "enhancement; opportunistic"** |
| Client SSO federation (`INT-046`) | W6 — month 26 | P2 |

The register's own justification for `AP-008` reads: *"Enterprise clients increasingly require ticket
and asset integration **as a condition of contract**."* `06-02` `G4-05` requires **ten or more
corporate clients transacting at the W4 gate**.

> **The programme expects to sign ten or more corporate clients in month 18 against a capability its
> own register calls a condition of contract, scheduled for month 30, at the lowest priority in the
> catalogue and explicitly marked deferrable. Either the priority is wrong or the justification is.**
>
> **Do not sell against W7 capability at W4.** The ICD is deferred until the Commercial Director
> establishes how many contracted or prospective clients actually require it (`AP-07`).

---

## 20. Deferral Register — the 33 ICDs not issued

Every integration without an ICD, with a reason and a review wave. **A deferral is a decision; an
omission is not.**

| Group | `INT-nnn` | Count | Reason | ICD due |
|---|---|---:|---|:--:|
| Payment — non-P0 | 004, 007, 008, 009 | 4 | W7–W9; `INT-007` is `IN-007`'s settlement design | W6 |
| Communications — non-P0 | 015, 016, 017, 018 | 4 | W4–W6 | W3 |
| Mapping — self-hosted | 020, 021, 022 | 3 | OSRM/VROOM are **self-hosted**; an internal component is not an external interface. `INT-022` is a thin P2 | W1 |
| Couriers — international | 027 | 1 | W9 | W8 |
| **Remote support & monitoring** | 028, 029, 030, 031, 032, 033 | **6** | **Six of the eight integrations cited in only two files estate-wide.** No module specification states what they are *for* beyond a one-line purpose | **W4, after M05's scope is confirmed** |
| Marketplace & trust | 035, 036, 037 | 3 | W6–W7; `INT-035` follows `INT-034`'s blocking conditions | W5 |
| Government — non-P0 | 039, 040, 041, 042 | 4 | `INT-041` biometric templates are **residency-classified** and follow the `INT-034` pattern | W3 (039), W4 (041) |
| AI / data / enterprise | 043, 044, 045, 046 | 4 | `INT-043`/`044`/`045` are **self-hosted**; `INT-046` is per-client federation, so it is **one ICD per corporate client**, templated | W5 |
| Client ITSM | 047 | 1 | §19 — commercial premise unresolved | W6 |
| Infrastructure | `INT-IPF-01`…`07` | 7 | M28's own components, not external counterparties | n/a |

> **`IN-A-19` (medium).** `INT-029`…`INT-033` are cited in only two files each — `05-03` §2.4 and
> Technology Stack §12.2.4 — and nowhere else in 621 files. **An integration named in the catalogue
> and the technology map and nowhere else has no specification asserting what it is for.** Writing an
> ICD against an unstated purpose would manufacture a contract, so the honest disposition is
> deferral with a named review, which is what §20 records. Referred to M05's owner.
>
> **`IN-A-20` (medium).** **`INT-046` is not one integration.** Corporate client SSO is a *federation
> per client*, so it is one ICD per corporate client against a **template**. `05-03` counts it as a
> single row, which understates it by a factor of however many corporate clients federate — and
> `G4-05` targets ten or more at W4.

---

## 21. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-004-D-01` | ICD granularity | One per integration · one per counterparty · **one per integration, with a shared ICD where the interface shape and blocking condition are identical** | **Per integration, shared where identical** | Pathao/RedX/Steadfast present the same shape and the same `AP-012` block; three near-identical documents would diverge | §17 covers three; §10 covers two |
| `IN-004-D-02` | `INT-038` pattern | Keep "File / API" · **`P5` batch, manual portal filing** | **`P5` manual** | No publicly documented machine API for IVAS Mushak-9.1 submission at 2026-08-18 | Effort moves from integration to **report generation accuracy**; `IN-A-04` |
| `IN-004-D-03` | `INT-005` counterparty | "Bank BEFTN" · **the sponsoring bank** | **The sponsoring bank** | BEFTN participants are banks; 1000FiX is not one and cannot be. The file is the bank's implementation | **`CD-100` cannot be specified until the bank is named** (`IN-001` Q-07) |
| `IN-004-D-04` | SSLCOMMERZ IPN trust | Signature sufficient · **signature + mandatory Transaction Validation call** | **Both** | The published integration requirement, and MD5 is not collision-resistant | `IN-A-15`; step 6 is the authority, not defence in depth |
| `IN-004-D-05` | Blocked ICDs | Omit them · **issue them marked BLOCKED with the blocking conditions enumerated** | **Issue as blocked** | An omitted ICD reads as "not needed"; a blocked one names who must act and by when | §16, §17 |
| `IN-004-D-06` | ICD state at issue | Present as agreed · **Draft, written from published counterparty documentation** | **Draft** | None has been confirmed by a counterparty engineer. Presenting them as agreed would be the `⚠`/`✅` confusion `PGD-000` §0.3 exists to prevent | `IN-001` `LC-01` requires `Agreed` before a connector is built |

---

## 22. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Which bank sponsors BEFTN, and what is its file specification?** | CFO + Treasury | **W5 − 4 months** | `CD-100`, §8, §9 |
| Q-02 | **Is there any machine API for IVAS Mushak-9.1 submission?** | Head of Tax + CTO | **W4 − 3 months** | §7 |
| Q-03 | **Is a second card acquirer procured, or does `NFR-048` restate?** | CTO + CFO | **W3** | §6.2, `IN-007`, `AP-06` |
| Q-04 | **Are the three courier `AP-012` rows determined and processor contracts signed?** | Legal Counsel | **W3 − 3 months** | §17, W3 pick-and-drop, `G3-07` |
| Q-05 | Are `INT-034`'s three prerequisites — specific consent, Authority notification, resident service — started? | DPO + Legal Counsel | **W7 − 6 months** | §16, the marketplace trust model |
| Q-06 | What **cache duration and scope** does the Google Maps licence permit for geocodes? The declared fallback depends on it | Legal Counsel | W2 | §14 |
| Q-07 | Is **masked SMS sender ID** registration started? It has a lead time and W1 is the first integration | Marketing + CTO | **W1 − 2 months** | §10 |
| Q-08 | Who owns **WhatsApp template authoring and approval**, and is the lead time in the plan? | Content Lead + M27 owner | **W1 − 2 months** | §11 |
| Q-09 | Does Nagad support a **key-rotation overlap window**? Without one, every rotation is an outage (`IN-A-14`) | Integration Architect | W3 | §5.2 |
| Q-10 | Do the ICDs and the commercial agreements **reference each other**? Today neither does (`IN-A-13`) | Legal + Commercial | W3 | §2.6 signature |

---

## 23. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | An ICD standard exists, with mandatory sections | §2.1 — sixteen |
| AC-02 | Clauses common to all 47 are stated once, not repeated | §2.2 |
| AC-03 | **Every P0 integration has an ICD** | §3 — **13 of 13** |
| AC-04 | Each ICD carries per-counterparty timing, not a global default | §4.4, §5.3, §6.3, §14 |
| AC-05 | Each ICD states what data leaves, its class and its lawful basis | §4.6 and per ICD |
| AC-06 | Blocked integrations are **issued as blocked**, with named owners and dates | §16, §17, `IN-004-D-05` |
| AC-07 | Counterparty-identity errors in `05-03` are corrected | §7.1, §8.1, `IN-004-D-02`, `IN-004-D-03` |
| AC-08 | Every claim about a counterparty's interface carries a verification date | §4.2, §5.1, §6.1, §7.1, §8.1 — all 2026-08-18 |
| AC-09 | The 33 ICDs not issued are **deferred with a reason and a review wave** | §20 |
| AC-10 | The document's own state is stated honestly | §2.6 — all fourteen are `Draft` |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are answered, the twelve
P0 ICDs reach **`Agreed`** with their counterparties, `AP-012` rows are `Determined` for every
integration entering production, and `PGD-000`'s `IN-004` row carries a fresh enumeration timestamp.

---

## 24. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`IN-001`** §7.2, §8, §10 | Per-counterparty timeouts, the ACL obligation, the integration register |
| Upstream | `AR-001` §8.1 | Z6 egress allow-list; Z4 residency |
| Upstream | `AP-012` | The field-level disclosure register every §8 section depends on |
| Downstream | **`IN-006`** | Per-provider inbound webhook verification (§6, §11, §17) |
| Downstream | **`IN-007`** | §4, §5, §6 are its wire contracts; COD remittance is its design |
| Downstream | **`IN-008`** | Every ICD §12 failure matrix is a test charter; §14 drives sandbox provisioning |
| Downstream | `SV-*`, `OP-014` | Every §11 fallback is a runbook input |
| Downstream | `CO-*` | §2.6 signature; `IN-A-13` |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §2, §7 | The 47-row catalogue; **§2.1 and §2.6 counterparties corrected** |
| Lateral | `../../primary-doc/…Technology_Stack_Specification.md` §12.2.4 | The 47 technology assignments |
| Lateral | `../../project_content/15_Integration_and_Developer_Content/AP-009_*.md`, `AP-010`, `AP-012` | Runbook content, sandbox content, disclosure register |

---

## 25. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-001_Integration_Architecture_Specification.md`](./IN-001_Integration_Architecture_Specification.md) ·
[`./IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](./IN-006_Webhook_Callback_and_Partner_Push_Specification.md) ·
[`./IN-007_Payment_and_Financial_Gateway_Integration_Design.md`](./IN-007_Payment_and_Financial_Gateway_Integration_Design.md) ·
[`./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §2, §3, §7 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2.4, §12.2.5 ·
`../../project_content/_AUDIT/AUDIT-016_*.md` `AP-04`, `AP-06`, `AP-07`, `AP-08`, `AP-12` ·
`../../project_content/15_Integration_and_Developer_Content/AP-009_*.md`, `AP-012_*.md`

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| bKash Tokenized Checkout API Integration Guide | `token/grant` → `create` → `execute` → `payment/status` → `refund`; **30 s client timeout**; `sandbox.bka.sh` / `pay.bka.sh`; credentials never in frontend code | 2026-08-18 |
| SSLCOMMERZ developer documentation (v4) | IPN with MD5 `verify_sign` **plus a mandatory Transaction Validation API call**; `VALID`/`FAILED`/`CANCELLED` | 2026-08-18 |
| Nagad Merchant API integration guidance | Merchant RSA key pair; merchant signs with its private key, encrypts with Nagad's public key, **verifies Nagad's response signatures**; public key uploaded via portal | 2026-08-18 |
| Bangladesh Bank, *BEFTN Operating Rules* | Fixed-width file — file header, batch header, entry detail, control records; three-digit SEC codes; **participants are banks**; T+1 clearing; live 28 February 2011 | 2026-08-18 |
| NBR VAT Online / IVAS (`vat.gov.bd`) | **Mushak-9.1**, monthly, by the 15th, filed through the portal; IVAS flags late submissions and mismatches; **no publicly documented machine API found** | 2026-08-18 |
| Bangladesh courier market (Pathao, RedX, Steadfast) | Common shape: create consignment with recipient name, phone, address and COD amount → tracking id; webhook on status change | 2026-08-18 |
| Standard Webhooks specification | The inbound/outbound signature scheme `IN-006` ratifies | 2026-08-18 |

---

## 26. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture | Initial issue. Establishes the sixteen-section ICD standard and issues **14 ICDs covering all 13 P0 integrations**, against **0 previously**. Corrects the P0 count from `05-03` §2's summary figure of 12 to the **13** its rows actually carry (`PE-A-01`, confirming `AUDIT-017` `OP-03`). Corrects two counterparty identities: `INT-038` is a manual portal filing, not an API (`IN-004-D-02`), and `INT-005`'s counterparty is **the sponsoring bank, not Bangladesh Bank** (`IN-004-D-03`) — the latter blocking `CD-100`. Raises `IN-A-13`…`IN-A-20`, issues `INT-034` and the three couriers **as blocked** rather than omitting them, and defers the remaining 33 with a reason and a review wave | *Pending — Design Authority not constituted (`PGD-A1-09`)* |

---

*`IN-004` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
