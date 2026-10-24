---
id: OP-012
title: Disaster Recovery and Continuity Playbook
project: 1000FiX ERP System v2.0
content_type: Runbook
template: TPL_Runbook.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering with Risk
author: Platform Engineering with Risk, Security and Operations
reviewers: [Chief Technology Officer, Chief Financial Officer, Operations Director, Security Lead, Data Protection Officer, Legal Counsel, Internal Audit, Programme Manager]
approver: Chief Technology Officer
content_class: C
purpose: >
  The failover decision authority, the procedures, the communication, the data-loss assessment and
  the return to normal for every scenario in which the primary environment is lost or must be
  abandoned. NFR-007 sets an RPO of 15 minutes and an RTO of 2 hours; those numbers are only
  achievable with a rehearsed playbook and a decision-maker who does not have to be found.
traces_to: [05-06 NFR-007, NFR-030, NFR-050, NFR-051, NFR-052, NFR-086, NFR-094, NFR-099, M29, M60, OP-007, OP-008, OP-009, OP-010, OP-011, OP-013, OP-014, OP-016, LG-021, LG-024, SP-005]
priority: P0
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-007 RPO ≤ 15 min, RTO ≤ 2 h; NFR-050 every P0 integration has a documented, tested manual fallback; NFR-051 full failover exercised twice yearly with documented results; NFR-052 automated restore test weekly; NFR-030 backup retention
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6 NFR-086, NFR-086a–c — split-residency data architecture; Sensitive Personally Identifiable Data held in a Bangladesh-resident store; NFR-099 restrictions on large-scale transfer of sensitive data
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-05 §9 — environments local, dev, staging, training, prod, **dr**
    verified: 2026-08-20
    class: P1
  - source: ISO 22301 clause 8.5 — exercise programme; exercises at planned intervals across tabletop, walk-through, functional and full-scale, with documented results carried into improvement. https://iso-docs.com/blogs/iso-22301-standard/iso-22301-clause-8-5-exercise-program
    verified: 2026-08-20
    class: P3
  - source: Cyber Security Ordinance 2025 (Bangladesh) — national incident response structure and reporting expectations for declared critical infrastructure. https://www.mondaq.com/new-technology/1659100/cyber-security-ordinance-2025-implications-for-businesses-in-bangladesh
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# Disaster Recovery and Continuity Playbook

> **A disaster recovery plan that has never been executed is a document about what somebody once
> intended.** `NFR-051` requires a full failover exercise twice a year with documented results.
> This playbook is written to be executed, and the parts of it that cannot yet be executed are
> named as such.
>
> **Read §6 if you are in one now.** Read §5 to know which scenario you are in.

| Item | Value |
|---|---|
| System | The whole production estate — ERP core, identity, integration, data platform, portals, apps and their data |
| Owner team | Platform Engineering, with Risk accountable for the continuity position |
| Criticality | **P0** |
| Availability target | `NFR-007` **RPO ≤ 15 minutes, RTO ≤ 2 hours** · `NFR-051` two full exercises a year · `NFR-052` weekly restore verification |
| On-call rota | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) |
| Escalation path | Incident Commander → CTO → **Crisis Management Team** (§4.2) → Board |

---

## 1. What This System Does

This playbook covers the loss of the environment itself, rather than a failure inside it. The
boundary is deliberate:

| Situation | Owned by |
|---|---|
| A component fails and can be repaired in place | [`OP-007`](OP-007_Runbook_Core_ERP_Platform.md)…[`OP-011`](OP-011_Runbook_Portal_and_Mobile_App_Operations.md) |
| The environment is unreachable, unusable, untrustworthy or destroyed | **This playbook** |
| The business must keep trading without the system at all | [`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) |
| A third party has failed, not us | [`OP-008`](OP-008_Runbook_Integration_and_Event_Platform.md) §7 |

**If this playbook is needed and does not work:** the company is offline for as long as it takes to
improvise a rebuild. At 250,000+ customers a month across 51+ branches, `NFR-007`'s two-hour RTO is
not an engineering preference — it is roughly the point at which branch queues become
unrecoverable for the day and same-day field commitments start to fail.

---

## 2. Architecture Summary

| Element | Purpose | Depends on |
|---|---|---|
| **Primary environment (`prod`)** | Normal operation | Cloud region, network, provider account |
| **DR environment (`dr`)** (`02-05` §9) | Recovery target | Provider account, replicated data, rebuildable configuration |
| **Database replication** | Continuous WAL streaming to DR, meeting the 15-minute RPO | Network, WAL archiving (`OP-007` OI-03) |
| **Filestore replication** | Object replication to the DR target, versioned | Object store replication |
| **Bangladesh-resident store** (`NFR-086`) | Sensitive Personally Identifiable Data — NID, passport, TIN, biometric templates | **Its own resident DR, which cannot be a foreign region** |
| **Infrastructure as code** (`OPS-02`) | Rebuild the environment rather than restore a snapshot of it | Version control availability |
| **Secrets and keys** | Vault, replicated; break-glass sealed copies ([`OP-009`](OP-009_Runbook_Identity_and_Access.md) §9) | Vault DR |
| **DNS and traffic steering** | Redirect users to DR | Registrar, TTL discipline |
| **Out-of-band communications** | Reach staff when the estate is unreachable | Independent of the estate (`OP-013` §4.10) |
| **Status page** | External communication during a disaster | **Independently hosted** ([`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) `SP-10`) |

> **The constraint that makes this playbook unusual.** `NFR-086` requires Sensitive Personally
> Identifiable Data to sit in a **Bangladesh-resident** store, joined to the regional store by a
> resident key. A disaster affecting Bangladesh infrastructure therefore cannot be answered by
> failing that store over to the regional site — `NFR-086b` requires an Authority notification and a
> documented safeguard **before** any cross-border transfer executes. **Failing over the sensitive
> store abroad in an emergency is not a technical decision; it is a regulatory act.** §4.3 states
> what to do instead, and OI-02 records that the second Bangladesh-resident site this implies does
> not yet exist.

---

## 3. Health Checks

DR readiness is a state that decays. These checks assert it while nothing is wrong.

| Check | Frequency | Healthy looks like |
|---|---|---|
| Replication lag to DR | Continuous | **< 15 min always** (`NFR-007` RPO) |
| Filestore replication lag | Continuous | < 15 min; object counts converging |
| Backup completion and **restore verification** | **Weekly** (`NFR-052`) | Restore test passes: row counts, checksum, attachment fetch, document render |
| DR environment buildable from code | Monthly | Full rebuild in a sandbox completes without manual steps |
| DR capacity | Quarterly | Sufficient for **at least degraded operation** — see §4.4 |
| Secrets replicated | Monthly | Vault DR reachable; break-glass envelope verified (`OP-009` `BG-10`) |
| DNS TTLs | Quarterly | ≤ 300 s on records used for failover |
| Contact tree current | Quarterly | Every role in §4.2 has a named holder and a verified number |
| Runbook currency | After every incident | `OP-007`…`OP-011` updated within 2 working days |
| **Exercise programme on schedule** | Quarterly review | Two full exercises a year, plus the tabletop schedule in §11 |
| Third-party dependency DR posture | Annually | Every P0 vendor's continuity position is on file ([`AP-009`](../15_Integration_and_Developer_Content/AP-009_Payment_Gateway_Integration_Runbook_Content.md) for gateways) |

**`HC-01`.** DR readiness is reported to the Steering Committee **monthly** as a single red/amber/
green with the evidence behind it. A DR position nobody reports is a DR position nobody funds.

---

## 4. Routine Operations

### 4.1 Declaration authority

| Decision | Who decides | Deputy | Time limit |
|---|---|---|---|
| **Declare a disaster** (invoke this playbook) | **CTO** | Operations Director, then Programme Manager — in that order, each recorded | If the CTO cannot be reached in **15 minutes**, the deputy decides. Waiting longer is itself a decision |
| Fail over the regional estate | CTO | Platform lead **with** Operations Director concurrence | Within 30 min of declaration |
| **Fail over or transfer the Bangladesh-resident store** | **CTO + Legal Counsel + DPO jointly** | **No deputy** | Not time-boxed — see §4.3 |
| Accept data loss (choose a recovery point) | CTO **and** CFO | — | Recorded before restore begins |
| Invoke manual trading (`OP-014`) | Operations Director | Branch operations manager | Immediately, in parallel with the technical response |
| Notify the Authority (`NFR-094`) | DPO | Legal Counsel | Assessment starts at detection |
| Communicate externally | Communications Owner, on the Incident Commander's facts | — | Per [`OP-004`](OP-004_Incident_Communication_Template_Set.md) matrix |
| Declare recovery complete and fail back | CTO + Operations Director | — | After §4.6 verification |

### 4.2 The Crisis Management Team

| Role | Held by | Responsible for |
|---|---|---|
| **Crisis Lead** | CTO | The declaration, the strategy, the authority to spend |
| **Incident Commander** | Senior on-call engineer (`OP-013` §4.6) | Technical execution and the timeline |
| **Business Continuity Lead** | Operations Director | Branches, field, and manual trading (`OP-014`) |
| **Communications Owner** | Change Lead or Support Lead | Every message, internal and external (`OP-004` `IC-01`) |
| **Finance Lead** | CFO | Data-loss acceptance, payment continuity, emergency spend |
| **Legal and Privacy Lead** | Legal Counsel with DPO | Residency, notification and disclosure decisions |
| **Scribe** | Named at declaration | The timeline: every decision, its time, and who made it |
| **People Lead** | HR Director | Staff safety, shift cover, welfare during a prolonged event |

> **`CM-01`.** The **Scribe is appointed within the first five minutes and does nothing else**. A
> disaster with no timeline cannot be reviewed, cannot be reported to an auditor, and cannot be
> defended in a dispute — and nobody reconstructs it accurately afterwards.

### 4.3 The residency decision (`NFR-086`)

If the disaster affects the Bangladesh-resident store, this is the sequence — and it does not
begin with a technical action.

| Step | Action | Owner |
|---:|---|---|
| 1 | Establish whether the resident store is **lost** or merely **unreachable**. They lead to different answers | Incident Commander |
| 2 | If unreachable: operate **without** the sensitive fields. Most operations do not need NID, passport or TIN; the system must degrade to identify customers by mobile and reference | Platform + Operations |
| 3 | If lost: restore from the **resident backup to a resident target** (`NFR-086c` also forbids unmasked resident data in non-production, so the target must be a production-class resident environment) | Platform |
| 4 | If no resident recovery target exists: **stop and escalate to Legal and the DPO.** Cross-border restoration requires the `NFR-086b` notification and a documented safeguard **before** the transfer executes | CTO + Legal + DPO |
| 5 | Record the decision, its basis and its timing, whichever way it goes | Scribe + DPO |

**`RD-01`.** Under no circumstances does an engineer restore the resident store into a foreign
region to shorten an outage. The regulatory consequence outlasts the outage by years, and the
decision is not theirs to make. This sentence exists so that it has already been said before the
night it matters.

### 4.4 Recovery priority

Not everything comes back at once. This is the order, and it is a business decision recorded here
so that it is not made under pressure.

| Tier | Restore | Target | Why first |
|:--:|---|---|---|
| **1** | Identity (`OP-009`) | ≤ 1 h | Nothing else is usable without it |
| **1** | ERP core — service orders, customers, devices (`OP-007`) | ≤ 2 h (`NFR-007`) | Branches and field work resume |
| **2** | Payments and the payment path (`OP-008`, `NFR-048`) | ≤ 3 h | Cash at counter covers the gap (`OP-014` FB-07) |
| **2** | Notifications (`M27`) | ≤ 3 h | Customers must be reachable |
| **2** | Technician app sync (`OP-011`) | ≤ 4 h | Devices buffer for 24 h; sync must return before that window closes |
| **3** | Customer portal and booking | ≤ 6 h | Hotline covers the gap |
| **3** | Integrations — couriers, brands, vendors | ≤ 8 h | Manual fallbacks exist (`OP-014`) |
| **4** | Corporate, seller, brand and partner portals | ≤ 24 h | Email intake covers the gap |
| **4** | Data platform and dashboards ([`OP-010`](OP-010_Runbook_Data_Platform_and_Warehouse.md)) | ≤ 72 h | Rebuildable from source; management can wait |
| **4** | Non-production environments | Last | They compete for the same capacity |

**Degraded-capacity rule `DC-01`:** the DR environment is sized for **tier 1 and 2 at full load and
tiers 3–4 at reduced load**. Recovering everything at production capacity is not funded, and
pretending otherwise produces a plan that fails at the moment of use.

### 4.5 Failover procedure (regional estate)

| Step | Action | Verification | Owner |
|---:|---|---|---|
| 1 | **Declare.** Name the Crisis Lead, Incident Commander and Scribe. Start the timeline | Declaration recorded | CTO |
| 2 | **Communicate immediately** — internal broadcast, status page, branch instruction to invoke `OP-014` | Messages sent, in both languages | Communications Owner |
| 3 | **Freeze the primary.** Prevent split-brain: primary must not accept writes once DR is promoted | Writes blocked | Incident Commander |
| 4 | **Determine the recovery point.** State it explicitly: "we will lose everything after HH:MM" | Recovery point accepted by CTO + CFO | Crisis Lead |
| 5 | Promote the DR database; verify replication position and integrity | Row counts, control totals | Platform |
| 6 | Attach the filestore replica **at the same point in time** | Attachment fetch test | Platform |
| 7 | Bring up identity (`OP-009` §8 verification set) | Five-check set passes | Security |
| 8 | Bring up ERP core; run the smoke pack ([`TS-013`](../13_Test_and_Acceptance_Content/TS-013_Regression_Pack_and_Smoke_Test_Checklist.md)) | Smoke pass | Platform + QA |
| 9 | Redirect DNS / traffic steering | Synthetic checks from an external network | Platform |
| 10 | Bring up integrations in priority order; **drain queues before re-enabling inbound traffic** | Queue depth, DLQ zero | Platform |
| 11 | Confirm apps are syncing; watch for duplicate submission (`DI-04`) | Sync dashboard | Mobile |
| 12 | **Assess the loss window** (§4.6) and start reconciliation | Loss statement issued | Finance + Operations |
| 13 | Publish restoration; **do not say "resolved" until §4.6 completes** | `OP-004` template 16/19 | Communications Owner |

### 4.6 Data-loss assessment

Failover almost always loses something. Naming it is what separates a recovery from a
mystery.

| Question | Method | Owner |
|---|---|---|
| What is the exact recovery point? | Replication position / WAL replay target | Platform |
| Which transactions fall in the loss window? | Compare source-of-record sequences and last known references either side of the window | Finance + Operations |
| Which payments were taken but are not in the restored data? | Gateway settlement reports against restored records — **the gateway is the external witness** | Finance |
| Which customer-facing commitments were made in the window? | Notification send logs (`M27`) — messages sent are evidence of promises made | Support |
| Which field work was in flight? | Device sync state; buffered work re-syncs and may **re-create** records already lost | Mobile + Field Ops |
| What did the manual fallback record? | `OP-014` paper forms | Branch operations |
| Is anything double-applied after re-sync? | Idempotency key audit (`DI-04`) | Platform |

**Output: a written loss statement** naming the window, the affected records, the recovery actions
and the residual uncertainty. It goes to the CFO, the Operations Director, and — where customers
were affected — into `OP-004` template 21. **A recovery with no loss statement is not complete.**

### 4.7 Failback

| Step | Rule |
|---|---|
| 1 | Failback is a **planned change**, never an emergency. It happens in a maintenance window (`OP-005`) with 72 hours' notice |
| 2 | The primary is rebuilt from code (`OPS-02`), not repaired in place, unless the cause is fully understood |
| 3 | Data flows **DR → primary** with the same verification set used at failover |
| 4 | Run in DR until the primary has demonstrated stability for a stated period — typically **5 working days** |
| 5 | Failback is exercised in the DR programme (§11); an unexercised failback is a second disaster waiting for a calmer day |

---

## 5. Common Failure Modes

The scenario table. Identify the row before choosing an action — the recovery for corruption is the
opposite of the recovery for an outage.

| Scenario | First indicator | Immediate action | Recovery strategy | Special considerations |
|---|---|---|---|---|
| **Cloud region or provider zone loss** | Everything unreachable; provider status page | Declare; fail over | §4.5 | Provider status pages lag; do not wait for confirmation |
| **Provider account compromise or lockout** | Administrative access denied; unexpected resource changes | Declare; engage provider support and Security in parallel | Rebuild in a separate account from code and backups | **Backups inside the compromised account may be untrustworthy** — this is why an out-of-account copy exists |
| **Database corruption or destructive change** | Data wrong, not absent; application errors on read | **Do not fail over** — DR has replicated the corruption | Point-in-time restore to before the event (`OP-007` §8) | RPO is irrelevant here; the **correct** point matters, not the latest |
| **Ransomware / malicious encryption** | Files unreadable; ransom artefacts; mass modification | Isolate immediately; declare; Security leads, not Platform | Rebuild from immutable backups into a clean environment | Never pay before Legal, Board and law-enforcement advice. Personal-data assessment starts at detection (`NFR-094`) |
| **Accidental mass deletion** | A large drop in record counts | Freeze writes; assess the window | Point-in-time restore, or targeted restore into an isolated environment | Human error — the review is blameless ([`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md)) |
| **Loss of encryption keys** | Data present, unreadable | Declare | Restore keys from vault DR / sealed offline copy | **If keys are unrecoverable, the data is unrecoverable.** This is why `OP-009` `BG-10` tests them quarterly |
| **Bangladesh national internet disruption** | Local connectivity lost; the estate is healthy | Invoke `OP-014` fully; the system is fine and unreachable | Branches trade on paper; field apps run offline (`NFR-047`); sync when connectivity returns | A genuine and recurring national-level risk; the mitigation is **operational, not technical** |
| **Prolonged power failure at branches** | Sites dark | Manual trading; devices on battery | Restore when power returns | Field apps continue; branch printing does not |
| **Civil disruption / site inaccessibility** | Staff cannot reach sites | Continuity is a people problem first (`HR`), a systems problem second | Remote working where roles allow; branch closure protocol | Safety decisions precede service decisions, always |
| **Flood or fire at a branch or the central warehouse** | Site loss reported | Continuity plan for that site; stock and asset assessment | Systems unaffected; **records of what was in that building are the recovery asset** | Argues for the inventory accuracy the programme targets |
| **Key-person unavailability** | Nobody can perform a procedure | Escalate; use the runbooks | The runbooks are the mitigation — this is their purpose | Any procedure only one person can perform is a finding (`OP-013`) |
| **Third-party P0 provider failure exceeding their own RTO** | Vendor outage with no ETA | `OP-014` fallback; assess switching | Alternate provider where one exists (payments, SMS) | Contractual remedy is Legal's; continuity is ours |
| **DR environment itself unavailable when needed** | Failover fails | Rebuild from code and backups into any available capacity | Slowest possible recovery; RTO will not be met | The scenario the monthly readiness check exists to prevent |

---

## 6. Incident Response

**The first fifteen minutes of a declared disaster.** Do these in order. Do not begin diagnosis
before step 4.

| Minute | Action | Owner |
|---:|---|---|
| 0–2 | **Declare.** Name Crisis Lead, Incident Commander, Scribe. Start the timeline | CTO / deputy |
| 2–5 | **Instruct the business to trade manually** (`OP-014`). This is parallel to, not after, the technical response | Business Continuity Lead |
| 5–8 | **Communicate**: internal broadcast, status page, branch SMS. Both languages. Next update time stated | Communications Owner |
| 8–10 | Identify the scenario in §5. **Write it down.** Corruption and outage need opposite actions | Incident Commander |
| 10–12 | Confirm the decision authority present, and what decisions are needed within the hour | Crisis Lead |
| 12–15 | Start the technical response for that scenario | Incident Commander |

| Severity | This playbook applies when |
|---|---|
| **Sev1 + declared disaster** | Primary environment lost, unusable or untrustworthy; expected outage exceeds the RTO; or data integrity cannot be assured in place |
| **Sev1, no declaration** | Component failure recoverable in place — stay in `OP-007`…`OP-011` |

> **`DR-01`. Declaring is cheap; declaring late is not.** A declaration that turns out to have been
> unnecessary costs an exercise's worth of effort and a stand-down message. A declaration made 90
> minutes late costs the RTO. **When in doubt, declare** — and the review will not criticise it.

---

## 7. Manual Fallback

> `NFR-050` requires every P0 integration to have a documented, tested manual fallback. During a
> disaster **all** of them are invoked at once, which is a different operating state from any single
> fallback and is the state `OP-014` §Total-unavailability describes.

| Business function | Fallback | Duration tolerable | Reconciliation |
|---|---|---|---|
| Branch intake and job creation | `OP-014` FB-01 paper job card | 8 h before the day is unrecoverable | Batch entry within 24 h of restoration |
| Payments | FB-07 counter cash only, manual receipts from the reserved range | 8 h | Receipt numbers matched against gateway settlement |
| Field work | Apps continue offline 24 h (`NFR-047`); beyond that, paper | 24 h+ | Sync, then paper entry for the excess |
| Dispatch | Branch-level manual allocation by telephone | 8 h | Jobs entered with actual times |
| Customer contact | Hotline on diverted mobile numbers, manual log | 24 h | Logged contacts entered |
| Invoicing | Manual invoice from the reserved sequence | 24 h | **VAT sequence integrity verified before filing** ([`DT-011`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-011_Sales_Register_Mushak_6_2.md)) |
| Payroll (if in window) | Prior-period payroll repeated with a corrective run afterwards, on CFO authority | One cycle | Corrective run and employee communication |
| Statutory filing | Manual filing from retained working papers | To the deadline | Filing evidence retained |

---

## 8. Backup and Recovery

| Item | RPO | RTO | Procedure | Last tested |
|---|---|---|---|---|
| ERP database | ≤ 15 min | ≤ 2 h | `OP-007` §8 | *Not yet* |
| Filestore | ≤ 15 min | ≤ 2 h | `OP-007` §8, same point in time | *Not yet* |
| **Bangladesh-resident sensitive store** | ≤ 15 min | ≤ 2 h | **Resident target only** (§4.3) | *Not yet — no resident DR target exists (OI-02)* |
| Identity | ≤ 15 min | ≤ 1 h | `OP-009` §8 | *Not yet* |
| Time series | ≤ 1 h | ≤ 4 h | `OP-010` §8 — **not rebuildable** | *Not yet* |
| Warehouse | N/A | ≤ 72 h | Rebuild from source (`OP-010`) | *Not yet* |
| Secrets and keys | Per rotation | ≤ 1 h | Vault DR + sealed offline copy | *Not yet* |
| Infrastructure definitions | Per commit | ≤ 2 h | Rebuild from version control | *Not yet* |
| **Out-of-account immutable backup copy** | Daily | ≤ 8 h | The copy that survives account compromise and ransomware | *Not provisioned — OI-03* |

**`BK-01`.** Retention is `NFR-030`: daily 30 days, weekly 1 year, monthly 7 years. **`BK-02`:** at
least one copy is **immutable and outside the primary provider account**, or the ransomware and
account-compromise rows of §5 have no recovery path.

---

## 9. Break-Glass Access

| Scenario | Who may authorise | Procedure | Audit record |
|---|---|---|---|
| Vault unavailable during a disaster | CTO + CEO/Managing Director | Sealed offline envelope from the head-office safe, two signatures (`OP-009` §9) | Physical log, photographed into the incident record; rotated immediately |
| Provider account recovery | CTO | Provider's own account-recovery process with the registered owner; identity documents held ready | Provider correspondence retained |
| Emergency spend (capacity, expedited support, alternate provider) | CTO up to a stated limit; CFO above it | Recorded at the time, reconciled afterwards — **not** a reason to delay | Finance record |
| Direct data manipulation to restore consistency | CTO + CFO for financial data | Script reviewed by two engineers, row counts asserted, backup first (`OP-007` §9) | Before/after extract retained 7 years |
| Emergency contact of staff outside the estate | Business Continuity Lead | Out-of-band tree (`OP-013` §4.10) using personal numbers held for this purpose | Privacy basis recorded (`NFR-090`) |

---

## 10. Change and Rollback

| Change type | Approval | Rollback | Verification |
|---|---|---|---|
| DR topology or region change | CTO + Risk | Restore the previous topology | Full exercise before it counts as ready |
| RPO/RTO target change | **Steering Committee** — these are `NFR-007` values | — | `05-06` updated; this playbook follows |
| Recovery priority order (§4.4) | CTO + Operations Director + CFO | Restore the previous order | Tabletop confirmation |
| Declaration authority (§4.1) | CTO + Board | — | Contact tree updated and verified |
| Backup retention or residency | CFO + Legal (statutory) | — | `NFR-030`/`NFR-088` conformance |
| Exercise scope | Risk + CTO | — | Documented results (`NFR-051`) |

---

## 11. Post-Incident

### Exercise programme (`NFR-051`, ISO 22301 cl. 8.5)

| Exercise | Frequency | Scope | Success criteria |
|---|---|---|---|
| **Backup restore verification** | **Weekly**, automated (`NFR-052`) | One database + filestore + attachment fetch + document render | All assertions pass |
| **Tabletop** | Quarterly | One §5 scenario, rotated; decision-makers only, 90 minutes | Every decision in §4.1 made, with the authority present and the timing recorded |
| **Component failover drill** | Twice yearly | Identity, then integration; failover and failback of one component | Component RTO met; no data loss |
| **Full failover exercise** | **Twice yearly** (`NFR-051`) | Complete failover of tier 1 and 2 services, with the business trading manually in parallel (`OP-014`) | **RTO ≤ 2 h and RPO ≤ 15 min demonstrated, with documented results** |
| **Communications drill** | Twice yearly, inside the full exercise | Out-of-band contact tree, both languages, all branches | ≥ 90% of branches acknowledge within 30 minutes |
| **Break-glass test** | Quarterly | Sealed envelope, vault path, provider recovery | Credentials valid; rotated afterwards |

**Exercise rules**

| # | Rule |
|---|---|
| **EX-01** | Exercises are **documented**: what was attempted, what worked, what did not, actions with owners and dates (ISO 22301 cl. 8.5) |
| **EX-02** | **A failed exercise is a successful exercise.** The purpose is to find the gap, and an exercise that never fails is not testing anything real |
| **EX-03** | The full exercise includes the **business side** — a branch trading on paper is part of the test, not an inconvenience to be excused |
| **EX-04** | Exercise findings enter the same register as incident actions (`OP-016`) and are tracked to closure |
| **EX-05** | **DR readiness is amber by default** between exercises older than 6 months, and red beyond 9 months. Readiness decays with time whether or not anything changes |

### After a real invocation

Every declared disaster produces a full review (`OP-016`) within **10 working days**, and it
additionally answers:

| Question | Why |
|---|---|
| Was the declaration made on time, and by whom? | `DR-01` — late declaration is the most common and most costly failure |
| Was the RPO met? What was actually lost? | Against `NFR-007`, evidenced by §4.6's loss statement |
| Was the RTO met, per tier? | Against §4.4, not as a single number |
| Did the business trade throughout? | `OP-014`'s effectiveness is measured here, not in theory |
| Did anything in this playbook prove wrong? | Corrected within 2 working days |
| Was any regulatory duty triggered, and was it met? | `NFR-094`, `NFR-086b`, and the Ordinance position (`OP-004` §2.6) |
| What did the exercises fail to predict? | The exercise programme is corrected, not merely repeated |

---

## Open Items

1. **OP-012-OI-01** — **A DR environment is named in `02-05` §9 but not sized, costed or provisioned
   in `02-05` §8.** Everything in this playbook depends on it existing. Until it does, `NFR-007` is
   an aspiration and the honest RAG status is **red**.
2. **OP-012-OI-02** — **No Bangladesh-resident DR target exists** for the `NFR-086` sensitive store.
   The only lawful recovery route (§4.3 step 3) is therefore unavailable, and the alternative
   requires a regulatory act under time pressure. **This is the most serious gap in Category 17.**
3. **OP-012-OI-03** — No **out-of-account immutable backup copy** is provisioned (`BK-02`), so the
   ransomware and account-compromise scenarios in §5 have no assured recovery path.
4. **OP-012-OI-04** — RPO of 15 minutes requires continuous WAL archiving to a separate failure
   domain, which `OP-007` OI-03 also records as unprovisioned. The two must be resolved together.
5. **OP-012-OI-05** — The recovery priority in §4.4 is proposed by content and requires **business
   ratification** (CFO + Operations Director). It encodes which parts of the company wait, and that
   is not an engineering decision.
6. **OP-012-OI-06** — **No business impact analysis exists.** §4.4 substitutes for one; a proper BIA
   would derive tiers from measured revenue and obligation impact rather than from judgement.
   Recommended owner: Risk, before W2.
7. **OP-012-OI-07** — The exercise programme (§11) is unresourced and unscheduled. `NFR-051`
   requires two full exercises a year from the first production wave; none is in `06-01`.
8. **OP-012-OI-08** — Third-party P0 providers' own continuity positions (payments, SMS, hosting)
   are not on file. Our RTO cannot be shorter than theirs on paths where no alternate exists.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Runbook.md` — all eleven sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; crisis-team audience
- [x] Bengali counterpart — n/a by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2. **The branch instructions this playbook triggers
      are bilingual and live in `OP-014` and `OP-004`**
- [ ] Named approver recorded — CTO; **§4.1, §4.3 and §4.4 additionally require CFO, Legal Counsel
      and Board acknowledgement**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — eight open items pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ● (unachievable until a DR environment exists — OI-01).
G4 n/a. **G5 Legal is additionally required for §4.3**, which states a regulatory position.

---

*`OP-012` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
