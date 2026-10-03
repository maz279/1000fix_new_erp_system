---
id: RP-013
title: Scheduled Report and Subscription Catalogue
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead
author: BI Lead with Platform Engineering
reviewers: [CTO delegate, Security Lead, Finance Manager, Operations Director, Support Lead, Chief Data Officer]
approver: BI Lead with CTO delegate
content_class: E
purpose: >
  Every standing subscription the system sends — its schedule, format, recipients, security scope and
  review date. Unreviewed subscriptions accumulate: a report scheduled for a manager who left two years
  ago is still generated every Monday, consumes warehouse capacity, and is delivered to a mailbox
  nobody reads. Worse, each one is a standing export of scoped data to an address, which makes the
  subscription list a data-distribution list — and the only reason it is P3 rather than higher is that
  the volume problem takes a year to become visible while the scope problem is immediate.
traces_to: [P06, 04-00 P06, RP-002, RP-003, RP-004, RP-005, RP-009, RP-010, RP-014, M27, M62, 05-04, 05-04 §8, 05-02 §10, NT-018, NT-022, TS-017, 05-06 NFR-088, 05-06 NFR-039]
priority: P3
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-10 — "A scheduled report is rendered per recipient under that recipient's security scope"; PRU-P06-11 every export is logged with user, view, row count and timestamp; §11 AUT-P06-03 a subscription schedule falls due — render per recipient under their own security scope and deliver through M27, retry then notify the subscription owner
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 Distribution — "schedule and subscribe to reports; export to PDF, Excel and CSV"
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §9 Access Lifecycle — deprovision revokes all access within 1 hour of a leaver event; §8 EA-12 bulk export by external parties is limited, rate-controlled and logged
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Scheduled Report and Subscription Catalogue

| Item | Value |
|---|---|
| Standing subscriptions | **19** at go-live (§4.3) |
| Rendering | **Per recipient, under that recipient's scope** — `PRU-P06-10` |
| Review | Every subscription, every 6 months (`SB-09`) |
| Leaver rule | Revoked with access, within 1 hour (`SB-11`) |
| Wave | W4 · `P3` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the subscription schema in §4.2. All six sections retained in order.

---

## 1. Purpose

`04-00` `P06` offers users the ability to *"schedule and subscribe to reports"*, and `AUT-P06-03`
delivers them. Self-service subscription is a genuinely useful capability whose cost accrues invisibly.

**Two distinct problems, on two timescales:**

| Problem | Timescale | Consequence |
|---|---|---|
| **Accumulation** | A year or more | Subscriptions are created and never removed. Warehouse capacity is consumed rendering outputs nobody opens, and `PRU-P06-13`'s bound on self-service queries does not apply to a scheduled job |
| **Distribution** | **Immediate** | Every subscription is a standing export of scoped data to an address. A subscription created before a role change delivers data the recipient may no longer see, and `PRU-P06-10` is the only thing preventing it |

The register's justification names the first. **The second is the reason this file is owned jointly
with Security in practice**, and it is why the leaver rule in `SB-11` matters more than the review
cadence.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| A catalogue | Nobody knows how many subscriptions exist or what they carry |
| Per-recipient rendering | One rendering distributed to many recipients, at the scope of whoever created it — the commonest scope breach in a BI estate |
| A leaver rule | A subscription outlives the access it was created under. `05-04` §9 revokes access within an hour; a subscription is not access and is missed |
| Review dates | Accumulation, indefinitely |
| Format and marking | An unmarked Excel export of branch margin in an inbox (`RP-014`) |
| Failure handling | A subscription silently stops and the recipient assumes there was nothing to report |

---

## 2. Scope

**In scope.** Standing subscriptions and scheduled deliveries: their schedule, recipients, scope,
format, marking, retention, review, failure handling and lifecycle. The self-service subscription
contract.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| What a report contains | `RP-002` |
| Dashboards | `RP-003`, `RP-004`, `RP-005` |
| **Statutory filings** | **`RP-009`** — a filing is never a subscription; §4.5 |
| The board and management pack | `RP-010` — its generation cut-off is a subscription; its contents are not |
| Export marking and watermarking | **`RP-014`** |
| Alerts | `RP-012`, `NT-021` |
| Notification channel behaviour and quiet hours | `NT-018`, `NT-022`; `M27` |
| Retention of the delivered artefact | `M24`, `NFR-088` |
| The proof that scope holds on delivery | `TS-017` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **BI Lead** (accountable) | The catalogue and the six-monthly review |
| **Platform Engineering** | Scheduling, rendering and failure handling |
| **Security Lead** | Per-recipient scope and the leaver rule |
| **Support Lead** | What breaks when a subscription fails, and who notices |
| **Subscription owners** | What they own and when it is reviewed |
| **Every subscriber** | What they will receive and in what format |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **SB-01** | **Every subscription is rendered per recipient under that recipient's own security scope** (`PRU-P06-10`). One definition, many scoped renderings — **never one rendering distributed to a list** |
| **SB-02** | **Every subscription has a named owner** who is accountable for its continued existence, distinct from its recipients |
| **SB-03** | **Every subscription states the decision or routine it supports.** One that supports neither is not created (`RP-002` `CT-01` applied to delivery) |
| **SB-04** | **Recipients are named roles or named people, never a distribution list or a shared mailbox.** A shared mailbox has no scope |
| **SB-05** | **Every delivery is logged** — recipient, view, row count, timestamp (`PRU-P06-11`) |
| **SB-06** | **Every delivered artefact is classified and marked** per `RP-014` before it leaves the platform |
| **SB-07** | **A subscription whose recipient's scope would return no rows is suspended, not delivered empty**, and the owner is notified. An empty report is read as "nothing happened" |
| **SB-08** | **Failure is visible**: a subscription that fails retries once, then **notifies the subscription owner** (`AUT-P06-03`), never fails silently |
| **SB-09** | **Every subscription is reviewed every six months** by its owner, who confirms it is still used |
| **SB-10** | **A subscription with no recorded open in two consecutive review periods is removed**, not suspended (`RP-002` `CT-14`) |
| **SB-11** | **A subscription is revoked with its recipient's access, within one hour of a leaver event** (`05-04` §9). A subscription is not access and will be missed unless this is explicit |
| **SB-12** | **A role change re-evaluates every subscription that recipient holds**, before the next delivery (`AUT-P06-09` pattern) |
| **SB-13** | **No external party receives a subscription containing another party's data**, and every external subscription is scoped and rate-limited (`EA-12`, `RP-005`) |
| **SB-14** | **No `S3` data is ever delivered by subscription**, in any format (`BRU-DAT-11`, `05-02` §10) |
| **SB-15** | **A subscription is not a statutory control** (`RP-009` `ST-10`, `AL-14`). A filing deadline is controlled by the `RP-009` ladder; a subscription may support it |
| **SB-16** | **Schedules avoid the load peak**: no subscription renders between 08:00 and 10:00 BST, the branch morning peak (`PRU-P06-13` intent, `NFR-039`) |
| **SB-17** | **Subscription count and total render cost are reported monthly.** An unmeasured estate grows |

### 4.2 The subscription schema

| # | Field | Content |
|---:|---|---|
| 1 | `id` | `SUB-nn`, permanent |
| 2 | `source` | The `RP-002` report or `RP-003`/`RP-004` view |
| 3 | `purpose` | The decision or routine it supports (`SB-03`) |
| 4 | `owner` | Accountable for its existence (`SB-02`) |
| 5 | `recipients` | Named roles or people (`SB-04`) |
| 6 | `scope` | The `05-04` tier each rendering is scoped to (`SB-01`) |
| 7 | `schedule` | Frequency, day, time — outside 08:00–10:00 BST (`SB-16`) |
| 8 | `format` | PDF · Excel · CSV · in-product inbox |
| 9 | `classification` | `S0`–`S3`; `S3` prohibited (`SB-14`) |
| 10 | `marking` | The `RP-014` treatment |
| 11 | `empty_behaviour` | Suspend and notify (`SB-07`) |
| 12 | `failure` | Retry once, then notify the owner (`SB-08`) |
| 13 | `retention` | How long the delivered artefact is retained (`NFR-088`) |
| 14 | `review_due` | Next six-monthly review (`SB-09`) |
| 15 | `last_opened` | Consumption evidence for `SB-10` |

**Field 15 is the field the estate depends on and the one nobody builds.** Without consumption
evidence, `SB-10` cannot operate and the catalogue can only grow. `O-02`.

### 4.3 The nineteen standing subscriptions

| `id` | Source | Recipients | Schedule | Format | Class |
|---|---|---|---|---|:--:|
| `SUB-01` | Daily branch performance (`RP-004` `C3`) | `R06` per branch | Daily 06:30 | PDF | `S2` |
| `SUB-02` | Network daily summary (`RP-003` `E4`) | `R05` | Daily 07:00 | PDF | `S2` |
| `SUB-03` | Unassigned and SLA-risk digest (`C2`) | `R07` per zone | Daily 07:00 | in-product | `S1` |
| `SUB-04` | WIP ageing and stuck jobs (`C4`) | `R09` per workshop | Daily 07:00 | in-product | `S1` |
| `SUB-05` | Stock reorder and stockout impact (`C5`) | `R17` | Daily 07:00 | Excel | `S2` |
| `SUB-06` | Van-stock variance (`KPI-047`) | `R17`, `R06` per branch | Weekly Mon 07:00 | Excel | `S2` |
| `SUB-07` | Three-way-match exceptions (`C6`) | `R19` | Daily 07:00 | Excel | `S2` |
| `SUB-08` | Vendor scorecard | `R19`, `R17` | Monthly | PDF | `S2` |
| `SUB-09` | Unbilled completed work (`KPI-056`) | `R26`, `R27` | Daily 07:00 | Excel | `S2` |
| `SUB-10` | Receivables ageing | `R26`, `R27` | Weekly Mon | Excel | `S2` |
| `SUB-11` | Close checklist state (`KPI-050`) | `R26`, `R03` | Daily during close | PDF | `S2` |
| `SUB-12` | **`RP-009` statutory calendar, T−15 onward** | `R26`, `R03` | Weekly Mon | PDF | `S2` |
| `SUB-13` | Claim pipeline and ageing (`C11`) | `R28` | Daily 07:00 | Excel | `S2` |
| `SUB-14` | Certification expiry 90/60/30/15 (`C8`) | `R32`, `R30` | Weekly Mon | Excel | `S2` |
| `SUB-15` | Attendance exceptions (`C8`) | `R31` | Daily 07:00 | Excel | `S2` |
| `SUB-16` | NCR and CAPA ageing (`C9`) | `R32` | Weekly Mon | PDF | `S2` |
| `SUB-17` | Job failure and integration health (`C14`) | `R33` | Daily 07:00 | in-product | `S1` |
| `SUB-18` | **`RP-016` data-quality scorecard** | `R33`, MDM Lead, BI Lead | Weekly Mon | PDF | `S1` |
| `SUB-19` | **`RP-010` monthly management pack** | `R01`–`R05` | Monthly, at cut-off | PDF | `S2` |

**Nineteen, and deliberately no external subscriptions at go-live.** `SB-13` permits them and `RP-005`
scopes them, but **a standing external delivery is a standing disclosure**, and the four external
agreements do not exist (`RP-005` `O-06`). External parties pull from their portal until an agreement
authorises a push. `O-04`.

**Every `SUB-*` above is a *scoped* subscription.** `SUB-01` is one definition rendered 51+ times, once
per branch manager, each seeing their own branch. That is `SB-01`, and it is the difference between a
subscription catalogue and a distribution list.

### 4.4 The self-service subscription contract

`04-00` lets users subscribe themselves. That needs bounds, or the catalogue is unmanaged by design.

| A user may | A user may not |
|---|---|
| Subscribe themselves to any view within their own scope | Subscribe **another person** — that is a delivery decision with a scope consequence (`SB-04`) |
| Choose frequency from a permitted set | Choose a schedule inside 08:00–10:00 BST (`SB-16`) |
| Choose PDF, Excel, CSV or in-product | Receive `S3` data in any format (`SB-14`) |
| Unsubscribe at any time | Escape the marking applied by `RP-014` |
| Hold up to **10** personal subscriptions | Exceed 10 without their manager's approval — a soft ceiling that surfaces accumulation early |

**A self-service subscription inherits every rule in §4.1**, including the six-monthly review and the
leaver revocation. It is owned by the subscriber, and when they leave it goes with them (`SB-11`).

### 4.5 What is never a subscription

| Not a subscription | Why | Owned by |
|---|---|---|
| **A statutory filing** | A filing is submitted to an authority, not delivered to a mailbox. `SB-15`; `RP-009` `ST-08` requires an acknowledgement as evidence | `RP-009` |
| **An alert** | An alert is a condition being met; a subscription is a schedule falling due | `RP-012`, `NT-021` |
| **A transactional document** | An invoice, challan or payslip is issued to a party under `DT` rules and `NT` delivery | Category 05, Category 04 |
| **A gate acceptance pack** | Assembled for a decision, not scheduled | `TS-018` §4.5 |
| **A data extract for a third party** | A recurring data transfer is an integration with a contract, not a subscription | `M28`; `AP` category |

> **The last row is the one that will be tested.** A brand partner asking for "a weekly Excel of our
> claims" is asking for an integration. Delivering it as a subscription puts a recurring data transfer
> outside the contract, the schema and the monitoring that `M28` provides — and `RP-005` `ED-10`'s
> export logging is not a substitute for a data-sharing agreement.

### 4.6 Lifecycle

| Event | Action |
|---|---|
| **Create** | Owner named, purpose stated, scope derived from the recipient's `05-04` position, review date set |
| **Deliver** | Rendered per recipient (`SB-01`), marked (`SB-06`), logged (`SB-05`) |
| **Empty** | Suspended and the owner notified (`SB-07`) |
| **Fail** | One retry, then the owner notified (`SB-08`) |
| **Role change** | Every subscription held by that recipient re-evaluated before the next delivery (`SB-12`) |
| **Leaver** | **Revoked within one hour, with access** (`SB-11`) |
| **Review, 6-monthly** | Owner confirms use; unconfirmed subscriptions are suspended pending confirmation (`SB-09`) |
| **Unused twice** | **Removed** (`SB-10`) |
| **Source retired** | Subscription removed with it (`RP-002` `CT-14`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-002`](RP-002_Report_Catalogue_by_Role_and_Module.md)** | Every subscription's source report and its retention |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md), `RP-004` | The views subscribed to |
| **[`RP-014`](RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md)** | Marking on every delivered artefact (`SB-06`) |
| [`RP-005`](RP-005_Dashboard_Specification_Pack_External_Audiences.md) | Scope rules for any future external subscription |
| [`RP-009`](RP-009_Statutory_and_Regulatory_Report_Format_Register.md) | `SUB-12`'s calendar, and the boundary in `SB-15` |
| [`RP-010`](RP-010_Board_and_Management_Pack_Template.md) | `SUB-19` and its generation cut-off |
| [`RP-016`](RP-016_Data_Quality_Scorecard_Definition.md) | `SUB-18`'s scorecard |
| `M27`, `NT-018`, `NT-022` | Delivery, channel and quiet hours |
| `05-04` §8, §9 | Scope, external limits, and the one-hour leaver revocation |
| `05-02` §10 | Classification (`SB-14`) |
| [`TS-017`](../13_Test_and_Acceptance_Content/TS-017_Security_and_Privacy_Test_Case_Pack.md) | Where per-recipient scope is proved |
| `NFR-039`, `NFR-088` | Render performance and retention |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Six-monthly per subscription** (`SB-09`); catalogue count and render cost reported monthly (`SB-17`) |
| Trigger for out-of-cycle review | A leaver; a role change; a source report retired; a render-cost increase; a scope change in `05-04`; a request for an external subscription |
| Owner | BI Lead; each subscription has its own named owner |
| Data file | `RP-013_Subscription_Catalogue.csv` — 19 subscriptions × 15 fields · `RP-013_Delivery_Log.csv` · `RP-013_Review_Log.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`SB-11` requires a subscription revoked within one hour of a leaver event, and nothing connects the two.** `05-04` §9 and `AUT-048` revoke *access*; a subscription is a scheduled job with a stored recipient and **will keep rendering and delivering unless it is explicitly included**. `KPI-090` targets zero orphaned accounts beyond 24 hours; **an orphaned subscription is the same exposure and is not measured** | `M29` owner with BI Lead | **W4 — before the first subscription is enabled** |
| **O-02** | **`SB-10` needs consumption evidence and field 15 has no source.** Nothing records whether a delivered PDF was opened. `RP-002` `O-06` records the same gap for reports. **Without it the catalogue can only grow**, and the accumulation problem this file exists to prevent is unpreventable | BI Lead with Platform Engineering | **W4** |
| **O-03** | **`SB-16`'s 08:00–10:00 exclusion conflicts with six daily 07:00 subscriptions.** Rendering nineteen scoped subscriptions — `SUB-01` alone is 51+ renderings — between 06:30 and 07:00 is a concentrated load nobody has sized. `NFR-039` bounds a query at 10 s; **it says nothing about 200 renderings in 30 minutes** | Platform Engineering with BI Lead | **W4 — needs `TS-014` coverage** |
| **O-04** | **No external subscriptions exist at go-live and `SB-13` permits them.** The four external agreements do not exist (`RP-005` `O-06`), so a standing external delivery has no authorising instrument. **The decision to withhold them is this file's, and it should be an agreed position** | Legal Counsel with CCO delegate | W7 |
| **O-05** | **This file is `P3` and `SUB-12` carries the statutory calendar while `SUB-19` carries the board pack.** `P3` means desirable; **two of the nineteen support a statutory control and a board obligation.** The priority reflects the accumulation problem rather than the distribution problem, and §1 records that the distribution problem is immediate | Programme Content Lead | **W4 — priority review** |
| **O-06** | **`AUT-P06-03` retries once then notifies the subscription owner, and `SB-07` suspends on empty.** Neither is reconciled with `NT-022` quiet hours: a 06:30 failure notification to a subscription owner is inside quiet hours for most recipients | Content Design Lead with BI Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the subscription schema
- [x] **Two problems separated by timescale — accumulation over a year, distribution immediately — and the priority questioned as a result**
- [x] Seventeen rules stated, led by per-recipient rendering and the one-hour leaver revocation
- [x] Fifteen-field schema, with the missing consumption field identified as the estate's dependency
- [x] Nineteen standing subscriptions specified, each scoped rather than distributed
- [x] **`SUB-01` shown as one definition rendered 51+ times, which is the difference from a distribution list**
- [x] A self-service contract with a may / may not table and a soft personal ceiling
- [x] **Five things that are never a subscription, including the third-party extract that is really an integration**
- [x] Full lifecycle from create to removal, including role change and leaver
- [x] No external subscriptions at go-live, with the reason and the decision flagged for agreement
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` leaver revocation not connected to subscriptions — outstanding; an orphaned subscription is an unmeasured exposure**
- [ ] **`O-02` no consumption evidence — outstanding; `SB-10` inoperable**
- [ ] **`O-05` `P3` priority questioned — outstanding; two subscriptions support statutory and board obligations**
- [ ] Named approvers recorded — **pending BI Lead and CTO delegate**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
