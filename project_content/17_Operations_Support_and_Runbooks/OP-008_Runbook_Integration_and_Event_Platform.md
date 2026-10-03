---
id: OP-008
title: Runbook — Integration and Event Platform
project: 1000FiX ERP System v2.0
content_type: Runbook
template: TPL_Runbook.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering
author: Platform Engineering with Enterprise Architecture
reviewers: [Chief Technology Officer, Enterprise Architect, Security Lead, Finance Systems Lead, Support Lead, Data Engineering Lead]
approver: Chief Technology Officer
content_class: C
purpose: >
  The operating procedures for the API gateway, the event bus, the transactional outbox, webhook
  delivery, dead-letter handling, replay, backlog drain and circuit breakers across 47 external
  integrations and the internal event estate. IP-05 and IP-06 require every integration to fail
  safely and be observable; without these procedures those principles are aspirations, and the
  first dead-letter queue nobody drains becomes a month of missing warranty claims.
traces_to: [M28, 05-02 DM-15, 05-03, 05-06 NFR-043, NFR-048, OPS-03, OPS-05, DI-05, DI-07, OP-007, OP-013, OP-014, OP-016, NT-021, AP-004, AP-009, SP-005]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §1 IP-01…IP-10, §2 the 47-integration catalogue, §4.1 event envelope, §4.3 consumer rules, §7 integration monitoring thresholds and the P0 fallback register
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 DM-15 — every state change writes to the outbox table in the same transaction; entity fix.domain.event
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-05 §4 — Kong Gateway 3.x, Redpanda/Kafka, n8n, Novu, Redis, OpenTelemetry/Prometheus/Loki/Tempo
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-043 event delivery ≤ 5 s p95; DI-05 at-least-once with idempotent consumption; DI-07 nightly cross-system reconciliation with divergence alerting; OPS-03 every alert has a runbook entry
    verified: 2026-08-20
    class: P1
  - source: project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021 — alert texts 3, 4, 5, 8 name this runbook as their remedy
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Runbook — Integration and Event Platform

> **Integration failures are quiet.** A screen that will not load produces 40 tickets in ten
> minutes; a webhook that stopped delivering produces nothing at all until a brand partner asks
> where three weeks of claims went. Everything in this runbook exists to make silence detectable.
>
> **Verification status.** Authored at W0/W1 against a platform delivered from W1 to W3. Commands
> and thresholds are indicative until verified in the built environment (G3).

| Item | Value |
|---|---|
| System | API gateway, event bus, transactional outbox, webhook delivery, workflow automation, notification orchestration |
| Owner team | Platform Engineering |
| Criticality | **P0** — 13 P0 integrations depend on it, including every payment path |
| Availability target | `NFR-002` API p95 ≤ 400 ms · `NFR-043` event delivery ≤ 5 s p95 · `NFR-048` payment path ≥ 99.95% |
| On-call rota | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) |
| Escalation path | On-call → Platform lead → CTO → [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) TE-E1; **integration owner** in parallel for a single-integration failure |

---

## 1. What This System Does

Everything that leaves or enters the ERP passes through here. `IP-02` routes all traffic through
the gateway; `DM-15` writes every state change to a transactional outbox in the same transaction
as the change itself; the relay publishes those events to the bus; consumers — internal modules,
portals, and external counterparties by webhook — act on them.

**If it stops:** the ERP still works, and that is exactly the danger. Jobs are created, invoices
are raised and payments are taken while nothing reaches the counterparties who need to know. The
damage is discovered later and has to be reconciled backwards.

---

## 2. Architecture Summary

| Component | Purpose | Depends on |
|---|---|---|
| **Kong Gateway 3.x** | Single ingress for all API traffic: authentication, per-portal rate limits, versioning, observability (`IP-02`, `PS-02`) | Identity ([`OP-009`](OP-009_Runbook_Identity_and_Access.md)), Redis, upstream services |
| **Transactional outbox** (`fix.domain.event`) | Guarantees an event is written atomically with the state change (`DM-15`) | PostgreSQL ([`OP-007`](OP-007_Runbook_Core_ERP_Platform.md)) |
| **Outbox relay** | Reads unpublished outbox rows and publishes to the bus | Outbox table, bus |
| **Event bus** — Redpanda (Kafka-compatible), W6 at scale; Redis streams before that | Durable, ordered-per-aggregate event transport | Storage, cluster quorum |
| **Consumers** | Internal modules, portals, warehouse loader ([`OP-010`](OP-010_Runbook_Data_Platform_and_Warehouse.md)), webhook dispatcher | Bus, their own datastore |
| **Webhook dispatcher** | Signed, retried delivery to external endpoints ([`AP-004`](../15_Integration_and_Developer_Content/AP-004_Webhook_and_Callback_Integration_Guide.md)) | Bus, counterparty endpoints |
| **n8n** | Workflow automation and low-code orchestration between systems | Gateway, credentials in vault |
| **Novu** | Notification orchestration and channel routing (`M27`) | SMS/WhatsApp/email/push providers |
| **Circuit breakers** | Per-integration failure isolation (`IP-05`) | Gateway/service configuration |
| **Observability** | OpenTelemetry traces with a single correlation id (`05-06` §7 `NFR-092`), Prometheus metrics, Loki logs | Independent of the ERP estate |

**Event envelope (`05-03` §4.1)** — every event carries `event_id`, `event_type`,
`schema_version`, `occurred_at`, `company_id`, `operating_unit_id`, `actor`, `correlation_id`,
`causation_id`, `aggregate` and `payload`. **The `correlation_id` is what makes an incident
traceable end to end; an event without one cannot be followed and is a defect.**

---

## 3. Health Checks

| Check | Command / dashboard | Healthy looks like |
|---|---|---|
| Gateway health | Kong status endpoint; Grafana → *Gateway* | All upstreams healthy; 5xx rate < 0.5% |
| Per-integration availability | Grafana → *Integrations* → availability by `INT-nnn` | ≥ 99% over 15 min (`05-03` §7 threshold) |
| Per-integration error rate | Same dashboard | ≤ 2% over 5 min |
| Latency | p95 by integration | ≤ 2× the recorded baseline |
| **Outbox lag** | `SELECT count(*), max(now()-created_at) FROM fix_domain_event WHERE published_at IS NULL;` | Count draining; **oldest unpublished < 60 s** |
| Bus consumer lag | Consumer group lag per topic | Draining; ≤ 5 s p95 end to end (`NFR-043`) |
| Queue depth | Per-queue pending count | < 1,000 pending (`05-03` §7) |
| **Dead-letter count** | Per-topic DLQ size | **Zero older than 1 hour — mandatory triage** (`05-03` §7) |
| Webhook delivery | Failures per endpoint | < 5 consecutive to any one endpoint |
| Circuit breaker state | Breaker dashboard | All closed; any open breaker has an incident or a known third-party outage behind it |
| Credential expiry | Vault expiry report | > 30 days remaining (`05-03` §7) |
| Nightly reconciliation | Reconciliation service report (`DI-07`) | Zero unexplained divergences |
| Schema registry | Registry health; compatibility check results | No incompatible producer deployed |

**Daily check (09:15 BST).** Outbox lag · DLQ counts · breaker states · overnight reconciliation
divergences · credential expiry within 30 days · any integration below 99% for the prior 24 hours.

---

## 4. Routine Operations

| Operation | Steps | Risk | Approval needed |
|---|---|---|:--:|
| **Rotate an integration credential** | Create new credential at the counterparty → store in vault → deploy → verify a live call → revoke the old one **after** verification | Medium — revoking first causes an outage | Standard change |
| **Add or change a rate limit** | Confirm the counterparty's published limits → set at the gateway → observe for 24 h | Medium — a limit set too low throttles production | Normal change |
| **Register a webhook endpoint** | Validate URL and TLS → configure signing secret → send a test event → confirm receipt and signature verification with the counterparty (`AP-004`) | Low | Standard change |
| **Disable a failing webhook endpoint** | After 5 consecutive failures: disable, notify the owner, queue events for replay (`05-03` §7) | Low | Standard change |
| **Replay a consumer from a point in time** | Confirm the consumer is idempotent (`DI-05`) → set the offset → replay → verify no duplicate side effects on other consumers (`05-03` §4.3) | **High** — replaying a non-idempotent consumer duplicates payments, messages or postings | Normal change + integration owner |
| **Drain a dead-letter queue** | Inspect each message → classify (transient / poison / already handled) → replay the transient, archive the poison with a defect, discard the already-handled with a recorded reason | Medium | Normal change |
| **Deploy a new event schema version** | Additive only within a version; a breaking change gets a new `schema_version` **and a dual-publish period** (`05-03` §4.3) | **High** — a breaking change without dual publish silently breaks consumers | CAB |
| **Open or close a circuit breaker manually** | Only during an incident, by the Incident Commander; record the time and the reason | Medium | Incident authority |
| **Onboard a new integration** | Pattern declared (`IP-03`) → idempotency proven (`IP-04`) → fallback documented (`IP-09`) → observability configured (`IP-06`) → data minimisation recorded (`IP-10`, [`AP-012`](../15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md)) → runbook entry added **here** | Medium | CAB |
| **Pause a batch integration** | Stop the schedule, not the consumer; record the pause and the resumption plan | Medium — silent pauses become permanent | Normal change |

> **`RO-01`.** No integration goes live without an entry in §5 of this runbook. `OPS-03` states it
> from the other direction: *every alert has a runbook entry; alerts without actions are removed*.
> An integration with no failure-mode row cannot be operated at 02:00.

---

## 5. Common Failure Modes

| Symptom | Likely cause | Diagnosis | Fix | Escalate if |
|---|---|---|---|---|
| **Outbox lag rising, nothing publishing** | Relay stopped, or the bus is unreachable | Relay process health; bus connectivity; unpublished count trend | Restart the relay; if the bus is down, the outbox **is the buffer** — it will drain on recovery | Lag > 15 min, or the outbox table is growing beyond its normal high-water mark |
| **Events publishing, consumers not consuming** | Consumer crashed, or is stuck on a poison message | Consumer group lag; consumer logs | Restart the consumer; move the poison message to the DLQ | Lag affects a customer-visible path |
| **Duplicate side effects after a replay** | A consumer that is not idempotent (`DI-05` breach) | Compare processed `event_id` records against side effects | Stop the replay immediately; assess and reverse the duplicates; raise a defect | **Always** — a `DI-05` breach is a design defect, `Sev2` minimum, `Sev1` if money moved |
| **Payment gateway unreachable** | Third-party outage or credential failure | Gateway availability dashboard; the counterparty's own status page | Fail over to the secondary gateway; if all are down, counter payment only ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) FB-07) | Any payment path degradation — `NFR-048` is 99.95% |
| **All payment gateways failing simultaneously** | Network egress, DNS, or a shared upstream | Egress path; DNS resolution; test from a second network | Restore egress; declare `Sev1`; counter-payment fallback | **Immediately — `Sev1`** |
| **SMS/OTP not delivering** | Provider outage or throttling | Provider dashboard; delivery receipts | Fail over to `INT-011`; escalate OTP to WhatsApp/push per [`NT-025`](../04_Notification_and_Messaging/NT-025_Notification_Failure_and_Fallback_Copy.md) | OTP failure blocks sign-in — `Sev1` |
| **Webhook endpoint failing repeatedly** | Counterparty endpoint down or rejecting signatures | Delivery log; response codes | Disable after 5 consecutive (`05-03` §7); notify the owner; queue for replay | Counterparty is a P0 integration |
| **Dead-letter queue growing** | A schema change, a poison payload, or a consumer defect | Sample messages; compare payload against the registered schema | Triage per §4; a DLQ is never left to grow | **Any DLQ item older than 1 hour** |
| **Circuit breaker open and not closing** | The upstream is still failing, or the breaker threshold is wrong | Breaker metrics; upstream health | Leave open while the upstream is unhealthy — that is its purpose; correct the threshold only after the incident | The breaker is protecting a P0 path with no fallback |
| **Nightly reconciliation reports divergence** (`DI-07`) | A missed event, a partial failure, or a counterparty-side change | Reconciliation report; trace by `correlation_id` | Identify and re-drive the missing transactions; never mass-replay to "fix" a count | Financial divergence of any size |
| **Gateway 429s in normal traffic** | Rate limit set below actual demand, or a portal misbehaving in a loop | Rate-limit metrics by consumer | Raise the limit **or** fix the caller; a retry loop is a defect, not a capacity problem | Customer-facing portal affected |
| **Latency doubled on one integration** | Counterparty degradation | Latency trend vs baseline | Notify the counterparty; extend timeouts only with care — long timeouts propagate failure | Sustained beyond 30 min on a P0 path |
| **Events arriving out of order** | Assumption of global ordering — there is none (`05-03` §4.3) | Compare `occurred_at` against processing order per aggregate | Correct the consumer's assumption. **Ordering is guaranteed per aggregate id only** | Any consumer relying on global order — design defect |
| **Correlation id missing from a trace** | Producer not propagating (`05-06` §7 `NFR-092`) | Trace inspection | Raise a defect against the producer | Incident traceability lost |

---

## 6. Incident Response

| Severity | Response time | First actions | Who to notify | Comms template ([`OP-004`](OP-004_Incident_Communication_Template_Set.md)) |
|---|---|---|---|---|
| **Sev1** — customer-facing path (payments, booking, OTP) failing | Page immediately | Declare · identify affected integrations · **switch to fallback (`OP-014`)** · publish status | Incident Commander, CTO, Finance if money, Support Lead | 1, 3, 5 |
| **Sev2** — internal path failing, or a single P0 integration with a working fallback | 30 min | Confirm fallback is in use · notify the integration owner · assess backlog growth | Platform lead, integration owner | 2 |
| **Sev3** — non-P0 integration failing with a fallback | Next business day | Ticket; monitor backlog | Integration owner | — |
| **Sev4** | Backlog | Trend only | — | — |

**Backlog arithmetic — do this in the first ten minutes.** When an integration is down, the
question that decides severity is *how fast is the backlog growing and how long can we absorb it?*

```
absorb_hours = (queue_capacity − current_depth) ÷ arrival_rate_per_hour
drain_hours  = accumulated_backlog ÷ (processing_rate_per_hour − arrival_rate_per_hour)
```

If `drain_hours` exceeds the time until the next business deadline (a settlement window, a filing,
a payout run), the incident is `Sev1` regardless of how calm the dashboards look.

---

## 7. Manual Fallback

> `IP-09` requires a defined manual fallback for **every P0 integration**. The detailed procedures
> are in `OP-014`; this section is the operational index and the escalation rule.

| P0 integration | Fallback (from `05-03` §7) | `OP-014` ref | Tolerable duration |
|---|---|---|---|
| `INT-001` bKash · `INT-002` Nagad · `INT-003` SSLCOMMERZ | Alternative gateway; cash at counter; payment link resent on restore | FB-07 | 4 h |
| `INT-005` BEFTN | Manual bank file submission via the bank portal | FB-12 | 1 working day |
| `INT-006` Bank statement import | Manual statement upload | FB-13 | 2 working days |
| `INT-010` SMS gateway | Failover gateway (`INT-011`); WhatsApp; push; queued retry | FB-03 | 1 h for OTP |
| `INT-012` WhatsApp | SMS; email; in-app inbox | FB-04 | 4 h |
| **`INT-013` Email** | **No fallback is recorded in `05-03` §7** — see the note below | **FB-05 (new)** | 4 h |
| `INT-014` Push notifications | SMS fallback for critical messages | FB-06 | 4 h |
| `INT-019` Google Maps | Cached geocodes; OSRM-only routing; manual address entry | FB-08 | 8 h |
| `INT-023` Traccar GPS | Last known position; manual status updates by technician | FB-09 | 8 h |
| `INT-034` Identity verification (KYC) | Manual document review by compliance | FB-14 | 2 working days |
| `INT-038` NBR e-VAT filing | Manual portal filing from the generated return | FB-15 | Until the filing deadline |

> **Two defects in the upstream fallback register, recorded here and carried into `OP-014`:**
>
> 1. **`05-03` §7's fallback register omits `INT-013` (email), which is a P0 integration.** Email is
>    the delivery path for invoices, corporate notifications and inbound ticket parsing. `IP-09`
>    requires a fallback for every P0 integration; there is none. `OP-014` FB-05 supplies one.
> 2. **`05-03`'s Integration Priority Summary states 12 P0 integrations; enumerating the catalogue
>    gives 13.** The summary also states P1 = 17 and P3 = 6 against enumerated 14 and 8. Counted
>    2026-08-20 from `05-03` §2.1–§2.7. Raised as a finding in the Category 17 audit; the operational
>    consequence is that any coverage claim of the form "all 12 P0 integrations have a fallback" is
>    both wrong and incomplete.
>
> The fallback register also lists **telephony** and **LLM inference** — `INT-015` (P1) and `INT-043`
> (P2). Having a fallback for a non-P0 integration is not a defect; counting it as evidence of P0
> coverage would be.

**On recovery, always:** drain the queue before re-enabling the integration for new traffic;
reconcile what was handled manually; and check for duplicates created by the fallback (a manual
receipt and an automatic one for the same payment is the classic case).

---

## 8. Backup and Recovery

| Item | RPO | RTO | Procedure | Last tested |
|---|---|---|---|---|
| Outbox (`fix.domain.event`) | Same as the ERP database — it is a table in it (`OP-007` §8) | ≤ 2 h | Restored with the database; **unpublished rows republish automatically**, which is the point of the pattern | *Not yet* |
| Event bus topics | Retention-window dependent (target: 7 days) | ≤ 1 h | Rebuild the cluster from version-controlled configuration; replay from the outbox for anything lost | *Not yet* |
| Gateway configuration | Per commit | ≤ 30 min | Re-apply the version-controlled declaration (`OPS-02`) | *Not yet* |
| Credentials | Per rotation | ≤ 1 h | Vault restore (`NFR-062`, `IP-07`) | *Not yet* |
| Webhook delivery log | Daily | ≤ 4 h | Restored with the database | *Not yet* |
| n8n workflows | Per commit | ≤ 1 h | Version-controlled export | *Not yet* |

**The recovery property that matters:** because `DM-15` writes the event in the same transaction as
the state change, **the outbox is the recovery source of truth**. If the bus loses data, events are
republished from the outbox. If the outbox is lost, the state change was lost too — which means the
recovery problem is `OP-007`'s, not this runbook's.

---

## 9. Break-Glass Access

| Scenario | Who may authorise | Procedure | Audit record |
|---|---|---|---|
| Gateway locked out (misconfigured auth plugin blocking all traffic) | CTO | Direct administrative access to the gateway node from the bastion path; two people present | Session recording, change record |
| Manual publication of an event to unblock a business-critical flow | CTO **and** the integration owner | Event constructed with a full envelope including `correlation_id` and a `causation_id` naming the incident; published once; verified once | Incident record, published payload retained |
| Direct call to a counterparty API outside the gateway | CTO | Only where the gateway itself is the failure. Credentials from vault, use logged, rotated afterwards (`BG-01` in `OP-007`) | Vault log, incident record |
| Suppressing an alert during a known incident | Incident Commander | Time-boxed suppression with an automatic expiry, never open-ended (`AL-04`) | Alert system record |

**`BG-05`.** Manually publishing an event is the most dangerous action in this file. A malformed or
duplicated event propagates to every consumer and cannot be recalled. It is done by two people, one
constructing and one verifying, or it is not done.

---

## 10. Change and Rollback

| Change type | Approval | Rollback procedure | Verification |
|---|---|---|---|
| Gateway route or plugin | Standard/normal per risk | Re-apply the previous declaration | Synthetic call per route |
| Rate limit | Standard | Restore the previous value | Observe 429 rate for 1 h |
| New integration | CAB | Disable at the gateway; the ERP continues without it | Contract test + a live sandbox call ([`AP-010`](../15_Integration_and_Developer_Content/AP-010_Sandbox_Onboarding_and_Test_Credential_Guide.md)) |
| **Event schema — additive** | Normal | Consumers ignore unknown fields; no rollback needed | Contract test against the registry |
| **Event schema — breaking** | CAB, with a **dual-publish period** and a consumer migration plan ([`AP-011`](../15_Integration_and_Developer_Content/AP-011_Integration_Change_Deprecation_and_Notice_Content.md)) | Continue publishing the old version; the dual-publish window is the rollback | Every registered consumer confirmed migrated before the old version stops |
| Webhook signing secret | Normal | Restore the old secret; counterparties must be told in advance either way | Signature verification test with the counterparty |
| Consumer deployment | Normal | Redeploy previous version; **offsets are not rolled back** — reprocessing depends on idempotency | Lag drains; no duplicate side effects |
| n8n workflow | Normal | Restore the previous export | Dry run against staging |

> **`CR-03`.** The only safe breaking change is one where the old and new versions both publish for
> long enough that every consumer has migrated **and been observed consuming the new version**.
> "We told them" is not migration evidence.

---

## 11. Post-Incident

Every `Sev1` and `Sev2` requires a review in [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md). Integration incidents carry four additional
mandatory review questions:

| Question | Why it is asked every time |
|---|---|
| **Was the failure detected by monitoring or by a human noticing?** | `KPI-088` targets zero integration failures undetected beyond 5 minutes. A human-detected failure is a monitoring defect regardless of the outcome |
| **Did the fallback work, and did the people who needed it know it existed?** | `IP-09` compliance is only real if the branch could execute it (`OP-014`) |
| **Was anything double-applied?** | `IP-04`/`DI-05` idempotency is asserted at design time and proven only by incidents |
| **What is the reconciliation position now?** | Every integration incident ends with a reconciled statement, not with service restoration |

**Standing outputs:** a new row in §5 for any unlisted failure mode; an alert added or removed in
[`NT-021`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) (`AL-05` noise rule); a fallback correction in `OP-014`; and, where a counterparty caused
it, a record in the vendor performance file ([`EO-006`](../18_Ecosystem_Onboarding_Content/EO-006_Supplier_Performance_Scorecard_Explanation.md) pattern) for the contract review.

---

## Open Items

1. **OP-008-OI-01** — **`05-03` §7's P0 fallback register omits `INT-013` email (P0).** `OP-014` FB-05
   supplies a fallback; the upstream register still requires correction.
2. **OP-008-OI-02** — **`05-03`'s P0/P1/P3 integration counts do not match its own catalogue**
   (12/17/6 stated; 13/14/8 enumerated 2026-08-20). Any statement of fallback coverage is unsafe
   until corrected.
3. **OP-008-OI-03** — The event bus is Redis-streams-based before W6 and Redpanda from W6 (`02-05`
   §4). **The migration between them is not planned anywhere**, and replay semantics differ.
   Escalated to Enterprise Architecture.
4. **OP-008-OI-04** — A **schema registry** is implied by `05-03` §4.3 (`schema_version`, compatibility)
   but is not named in `02-05` §4. Without one, §10's compatibility verification is manual.
5. **OP-008-OI-05** — Dead-letter **retention and disposal** are undefined. A DLQ containing personal
   data is a data store with retention obligations (`NFR-088`, `NFR-095`) and nobody owns it.
6. **OP-008-OI-06** — Severity ownership conflict: `SP-005` §5 and [`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) §2 both direct readers to
   this runbook for "technical severity classification". **The definitive scale is `OP-013` §4.1.**
   Both upstream files require a one-line correction; raised in the Category 17 audit.
7. **OP-008-OI-07** — This file is `W3` in the register, but `NT-021` (W1) already names it as the
   remedy for four W1 alerts. Either the runbook is needed at W1 or those alerts have no procedure
   for two waves.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Runbook.md` — all eleven sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; engineering audience
- [x] Bengali counterpart — n/a; English-only by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2
- [ ] Named approver recorded — CTO; G3 deferred until the platform exists
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — seven open items pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ● (deferred). G4 n/a.

---

*`OP-008` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
