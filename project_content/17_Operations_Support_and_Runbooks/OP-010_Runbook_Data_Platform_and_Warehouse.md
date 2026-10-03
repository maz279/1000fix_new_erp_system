---
id: OP-010
title: Runbook — Data Platform and Warehouse
project: 1000FiX ERP System v2.0
content_type: Runbook
template: TPL_Runbook.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Engineering
author: Data Engineering with BI Lead
reviewers: [Chief Technology Officer, BI Lead, Enterprise Architect, Finance Controller, Data Protection Officer, MDM Lead]
approver: Chief Technology Officer
content_class: C
purpose: >
  The monitoring, reload, backfill, schema-change and certification procedures for the analytical
  estate — warehouse loads, time-series ingestion, semantic models and published dashboards.
  Silent pipeline failure produces confidently wrong dashboards, which is worse than an outage: an
  outage is noticed and corrected, a wrong number is acted on.
traces_to: [M62, M25, M26, 05-06 DI-06, DI-07, NFR-039, NFR-071, NFR-086, KPI-093, KPI-094, OP-007, OP-008, OP-013, RP-001, RP-016, DM-011]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M62_Data_Platform_Warehouse_and_Governance.md — warehouse, pipeline, governance and certification scope
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-05 §4, §5.3 — ClickHouse 24.x analytical warehouse (W8), TimescaleDB 2.x time series (W2), Metabase 0.52+ (W4), warehouse ETL in Python/dbt
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 DI-06 data quality tests run on every warehouse load and failures block dependent refreshes; DI-07 nightly cross-system reconciliation with divergence alerting; NFR-039 analytical query ≤ 10 s p95; NFR-071 non-production masked data only
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-093 data quality test pass rate > 99%; KPI-094 manual management reports remaining zero
    verified: 2026-08-20
    class: P1
  - source: project_content/14_Reporting_Analytics_and_KPI/RP-016_Data_Quality_Scorecard_Definition.md — completeness, validity, uniqueness and timeliness measures per master-data domain
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Runbook — Data Platform and Warehouse

> **The failure mode here is not downtime; it is confidence.** A dashboard that is down gets a
> ticket in ten minutes. A dashboard that is quietly eight hours stale gets a decision.
>
> **Verification status.** Authored at W0/W1 against a platform delivered W2–W8. Indicative until
> G3 verification.

| Item | Value |
|---|---|
| System | Warehouse loads, time-series ingestion, semantic layer, published dashboards and scheduled reports |
| Owner team | Data Engineering, with the BI Lead accountable for published content |
| Criticality | **P2** — no customer-facing impact; **P1 in the last five working days of a month**, when the close and management packs depend on it |
| Availability target | `NFR-039` analytical query ≤ 10 s p95 · `NFR-005` standard report ≤ 20 s · **freshness targets in §3, which matter more than availability** |
| On-call rota | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) — **business-hours cover only**, except during close |
| Escalation path | On-call → Data Engineering lead → BI Lead → CTO; Finance Controller in parallel during close |

---

## 1. What This System Does

It turns operational records into the numbers the company manages itself with: branch league
tables, technician utilisation, SLA attainment, margin by service line, stock position, the
executive dashboard (`P06`) and the board pack ([`RP-010`](../14_Reporting_Analytics_and_KPI/RP-010_Board_and_Management_Pack_Template.md)). `KPI-094` targets **zero manual
management reports** — meaning that when this platform is wrong, there is no shadow spreadsheet
left to catch it.

**If it stops:** nothing operational breaks. Jobs, invoices and payments continue. Management
loses sight, and — the specific danger — **management may not notice it has lost sight**, because a
stale dashboard looks exactly like a current one.

---

## 2. Architecture Summary

| Component | Purpose | Depends on |
|---|---|---|
| **Source systems** | Odoo core ([`OP-007`](OP-007_Runbook_Core_ERP_Platform.md)), event stream ([`OP-008`](OP-008_Runbook_Integration_and_Event_Platform.md)), external files | Their own availability |
| **Ingestion** | Batch extract from PostgreSQL replicas; streaming consumption of domain events | `OP-007` replicas, `OP-008` bus |
| **TimescaleDB 2.x** (W2) | GPS, telemetry and other high-rate time series with compression | Storage |
| **ClickHouse 24.x** (W8) | Analytical warehouse at scale | Storage, cluster health |
| **Transformation** — Python + dbt | Modelled layers: raw → staged → core → mart | Ingested data, model repository |
| **Data quality tests** | Assertions run on every load; failures **block dependent refreshes** (`DI-06`) | dbt test suite |
| **Semantic layer** ([`RP-002`](../14_Reporting_Analytics_and_KPI/RP-002_Report_Catalogue_by_Role_and_Module.md) pattern) | One definition per metric, consumed by every dashboard | Core models |
| **Metabase 0.52+** (W4) | Dashboards and self-service exploration | Warehouse, semantic layer |
| **Scheduled reports and subscriptions** ([`RP-013`](../14_Reporting_Analytics_and_KPI/RP-013_Scheduled_Report_and_Subscription_Catalogue.md)) | Standing deliveries | Metabase, `M27` delivery |
| **Reconciliation service** (`DI-07`) | Nightly cross-system divergence detection | Source and warehouse |

**The load-order dependency that causes most incidents:** master data (`M64`) must load before
transactions, and transactions before marts. A mart refreshed against yesterday's master data
produces figures that are internally consistent and externally wrong — the hardest class of error
to detect.

---

## 3. Health Checks

| Check | Command / dashboard | Healthy looks like |
|---|---|---|
| **Freshness by mart** | Freshness dashboard: `max(loaded_at)` per mart | Within its stated SLA: operational marts ≤ 2 h, financial marts ≤ 24 h, executive marts ≤ 24 h |
| Load success | Orchestrator run history | Last scheduled run of every model succeeded |
| **Data quality test pass rate** | dbt test results | **> 99%** (`KPI-093`); any failure blocks dependents (`DI-06`) |
| Row-count drift | Load-over-load delta per source table | Within the expected band; a 0-row load on a table that always has rows is a failure, not a quiet day |
| Reconciliation divergence (`DI-07`) | Nightly reconciliation report | Zero unexplained; every explained item has an owner |
| Query latency | p95 analytical query | ≤ 10 s (`NFR-039`) |
| Storage headroom | Cluster storage | > 25% free |
| Time-series ingestion rate | TimescaleDB ingest metrics | Matches the emitting fleet: 400 technicians at 30-second intervals (`NFR-056`) |
| Compression jobs | Timescale compression policy status | Running; backlog not growing |
| Dashboard errors | Metabase error rate | Flat |
| Subscription delivery | Scheduled report send log (`RP-013`) | All sent; failures visible, not silent |
| **Certification status** | Certified dataset register (`M62`) | Every published dashboard sources only certified models |
| Masking in non-production | Environment check | **No unmasked personal or residency-classified data outside production** (`NFR-071`, `NFR-086c`) |

**Daily check (08:30 BST, before the business reads anything).** Freshness by mart · overnight load
failures · failed quality tests · reconciliation divergences · subscription failures. **The result
is posted where dashboard users can see it** — a freshness banner on `P06` is worth more than an
alert to an engineer, because it reaches the person about to make a decision.

---

## 4. Routine Operations

| Operation | Steps | Risk | Approval needed |
|---|---|---|:--:|
| **Reload a mart** | Identify the dependency graph → reload upstream first → run tests → publish | Low | Standard |
| **Backfill a period** | Confirm the source is complete for that period → run in a bounded window → **verify counts against source** → publish | Medium — a partial backfill leaves a period that looks loaded | Normal change |
| **Add a model or metric** | Define in the semantic layer first ([`RP-001`](../14_Reporting_Analytics_and_KPI/RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md) definitions) → build → test → **certify** → then publish a dashboard | Medium — an uncertified metric on a published dashboard is how two versions of a number begin | BI Lead |
| **Schema change at source** | Detect via contract test → assess downstream models → update → backfill if the change is retrospective | **High** — silent source schema drift is the most common cause of wrong numbers | CAB |
| **Change a metric definition** | Change in the semantic layer → assess every consumer → **notify consumers before publishing** (`RP-001`) → republish history if the change is retrospective | **High** — a redefined metric changes history and people notice | BI Lead + metric owner |
| **Certify a dataset** | Owner named, definition documented, quality tests present, freshness SLA stated, access class set | Medium | BI Lead |
| **Decertify** | Mark, notify consumers, remove from published dashboards within a stated period | Medium — removing quietly leaves stale copies in use | BI Lead |
| **Add a scheduled subscription** | Confirm recipient, purpose and classification; set a review date (`RP-013`) | Low | BI Lead |
| **Refresh a non-production environment** | Load **masked** data only; residency-classified fields never leave production unmasked (`NFR-086c`) | **High** | DPO + Data Engineering |
| **Purge or archive time series** | Confirm retention policy and statutory position (`NFR-088`) → archive → verify restore path | Medium | Data Engineering + Legal for anything with a retention obligation |

> **`RO-03`.** Reloading during the close window (last five working days of the month) requires the
> Finance Controller's agreement. A reload that changes a number a controller has already signed
> creates a reconciliation problem where none existed.

---

## 5. Common Failure Modes

| Symptom | Likely cause | Diagnosis | Fix | Escalate if |
|---|---|---|---|---|
| **Dashboard shows yesterday's data with no warning** | Load failed silently, or the freshness indicator is missing | Freshness dashboard; orchestrator history | Rerun the load; **add the freshness indicator to the dashboard — its absence is the real defect** | Any executive or financial dashboard |
| Load fails on one model, others succeed | Source schema change, or a data type violation | dbt run log; compare source schema against contract | Fix the model; add a contract test so the next change is caught before the load | Repeats after fix |
| **Data quality test fails and dependents run anyway** | `DI-06` blocking not implemented or overridden | Orchestrator configuration | Restore blocking; treat any override as a change requiring approval | **Always — this is the control that keeps wrong numbers off dashboards** |
| Row counts halved after a load | Partial extract, or a filter change | Compare source count for the window | Reload the window; identify the filter change | Financial marts — `Sev2` |
| Duplicate rows in a mart | Re-run without idempotent keys, or a replayed event stream (`OP-008`) | Uniqueness test results | Deduplicate by natural key; fix the load to be idempotent | Any figure already published |
| Numbers disagree between two dashboards | Two definitions of the same metric — semantic layer bypassed | Trace both to their models | Consolidate to the certified definition; decertify the other | **Always — the credibility cost is permanent** |
| Reconciliation divergence overnight (`DI-07`) | Missed events, a source correction, or a timing boundary | Reconciliation report by entity | Identify and re-drive; never adjust the warehouse to match without finding the cause | Financial divergence of any size |
| Query latency spike | Missing partition pruning, or a report scanning full history | Query plans; slow query log | Add partitioning or pre-aggregate; move heavy exploration off the shared cluster | Sustained beyond `NFR-039` |
| Time-series ingestion falling behind | Emission rate exceeds ingestion, or compression contention | Ingest lag; compression job status | Scale ingestion; adjust compression schedule | GPS gaps affect dispatch or evidence |
| Storage filling | Retention policy not applied, or an un-partitioned table | Largest tables; retention job status | Apply retention; archive | < 15% free |
| Personal data found in a non-production environment | Masking failed or was skipped | Environment scan | **Purge the environment immediately**; treat as a potential data incident ([`OP-004`](OP-004_Incident_Communication_Template_Set.md) §2.6 template 22) | **Always — DPO informed within the hour** |
| Subscription delivered with an empty report | Upstream load failed; the report ran anyway | Send log vs load history | Suppress delivery when the source is stale — **an empty report is read as "zero", not as "missing"** | Any recipient acted on it |

---

## 6. Incident Response

| Severity | Response time | First actions | Who to notify | Comms template (`OP-004`) |
|---|---|---|---|---|
| **Sev1** | Rare here. Reserved for: **a published figure that is wrong and has been acted on**, or personal data exposed in a non-production environment | Stop distribution · freeze the affected dashboards · state what is wrong before anyone asks | CTO, BI Lead, affected decision owner, DPO if personal data | 1, 12 |
| **Sev2** | 30 min in hours | Financial or executive dashboards stale or wrong during close; reconciliation divergence with financial impact | Data Engineering, BI Lead, Finance Controller | 2 |
| **Sev3** | Next business day | A non-critical mart stale or a single report failing | Data Engineering | — |
| **Sev4** | Backlog | Cosmetic or single-user | — | — |

**The rule that governs every data incident:** *when a number has been published and is wrong, the
correction is published to everyone who received the original, through the same channel, whether or
not they noticed.* Silent correction is how organisations lose trust in their own reporting.

---

## 7. Manual Fallback

| Scenario | Fallback procedure | Duration tolerable | Reconciliation on recovery |
|---|---|---|---|
| Warehouse unavailable during close | Finance runs the close from the ERP's own reports (`OP-007`), which are the system of record; warehouse figures are management views, not the ledger | 3 working days | Warehouse rebuilt and reconciled to the ledger before any management pack is issued |
| Executive dashboard unavailable | The board pack (`RP-010`) is produced from certified extracts taken **before** the failure, clearly dated | 1 week | Regenerate; state the difference if any figure moved |
| Branch league table unavailable | Suspended for the period with an announcement ([`RP-011`](../14_Reporting_Analytics_and_KPI/RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md)) — **never** published from an alternative source, which would change the basis of comparison mid-period | 1 month | Republish with the period marked as reconstructed |
| Time-series (GPS) ingestion down | Dispatch uses last known position; technicians update status manually ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) FB-09) | 8 h | Backfill from device buffers where available; gaps declared, not interpolated |
| Data quality blocking a needed refresh | Publish with the failure **visible on the dashboard**, or do not publish. There is no third option | Until fixed | — |

> **`FB-03`. Gaps are declared, never interpolated.** An interpolated GPS trail or an estimated
> figure that enters a certified dataset is indistinguishable from measured data six months later,
> and it may end up as evidence in a customer dispute or an audit.

---

## 8. Backup and Recovery

| Item | RPO | RTO | Procedure | Last tested |
|---|---|---|---|---|
| Warehouse (derived data) | **Not backed up by default** — it is rebuildable from source | ≤ 24 h | **Rebuild from source**, in dependency order, then verify against reconciliation | *Not yet* |
| Time series (TimescaleDB) | ≤ 1 h | ≤ 4 h | Backup/restore; **not rebuildable** — GPS and telemetry are only emitted once | *Not yet* |
| Transformation models (dbt) | Per commit | ≤ 30 min | Version control | *Not yet* |
| Semantic layer definitions | Per commit | ≤ 30 min | Version control | *Not yet* |
| Dashboards and subscriptions | Daily | ≤ 4 h | Metabase export/import | *Not yet* |
| Certified extracts used in board packs | Per issue | — | Retained as evidence for 7 years (`NFR-088`) — the pack must be reproducible | *Not yet* |

**The distinction that decides the strategy:** derived data is rebuilt, **captured data is
restored**. Time series is the only genuinely irreplaceable store here, and it is the one most
often left out of a backup plan because it "is only telemetry" — until it is the evidence that a
technician was at the address at 14:20.

---

## 9. Break-Glass Access

| Scenario | Who may authorise | Procedure | Audit record |
|---|---|---|---|
| Direct warehouse query needed during a Sev1 | Data Engineering lead | Read-only role; personal data columns remain masked unless the DPO authorises otherwise | Query log |
| Access to unmasked personal data for an investigation | **DPO** + CTO | Time-boxed, purpose recorded, access revoked on completion (`05-06` §6.3 `NFR-090` purpose limitation) | DPO register, access log |
| Publishing a figure that has bypassed certification | BI Lead + the accountable executive | The figure is **labelled uncertified** wherever it appears; a certification task is raised | Decision record in `RF-006` |
| Emergency export of a dataset to an external party | CTO + DPO + Legal | Only against [`AP-012`](../15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md) field-level disclosure and a lawful basis | Disclosure register |

---

## 10. Change and Rollback

| Change type | Approval | Rollback procedure | Verification |
|---|---|---|---|
| Model change | Normal change | Revert the model version and rebuild | Test suite + row counts |
| Metric definition change | BI Lead + metric owner | Revert the definition; **history changes back too** — consumers must be told both times | Compare a known period before and after |
| Schema change at source | CAB (owned by `OP-007`) | Data Engineering adapts; the source rarely reverts | Contract test passes |
| Certification | BI Lead | Decertify with notification | Consumer list confirmed |
| Retention or purge | Legal + Data Engineering | **No rollback** — purged data is gone. This is why the approval is heavier than the work | Pre-purge extract retained per the retention schedule |
| Dashboard change | BI Lead | Restore the previous export | Visual check + a figure spot check |

> **`CR-05`.** Any change that alters a **published historical figure** is announced before it is
> made, not after. People plan around numbers; changing a past number without warning is
> experienced as the system being unreliable, even when the new number is the correct one.

---

## 11. Post-Incident

Every `Sev1` and `Sev2` requires a review in [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md). Data incidents add:

| Question | Why |
|---|---|
| Was a wrong figure acted on? By whom, and can the decision be revisited? | The impact of a data incident is the decision, not the dashboard |
| Why did quality tests not catch it? | Every data incident should end with a **new test**, not only a fix |
| Was the failure visible to the consumer, or only to engineers? | Freshness and quality state belong on the dashboard ([`RP-016`](../14_Reporting_Analytics_and_KPI/RP-016_Data_Quality_Scorecard_Definition.md)) |
| Did `DI-06` blocking operate? | If it was overridden, who authorised it |
| Is the reconciliation position now clean? | `DI-07` |

**Standing output:** every data incident adds at least one assertion to the test suite. A data
platform's test suite should be a history of its incidents.

---

## Open Items

1. **OP-010-OI-01** — **Wave conflict.** This runbook is `W4`, but time-series ingestion
   (TimescaleDB) starts at `W2` and carries the only irreplaceable data in the estate. Sections 3,
   5 and 8 are needed from W2.
2. **OP-010-OI-02** — ClickHouse arrives at **W8** (`02-05` §4) while `P06` analytics goes live at
   **W4**. What serves W4–W8 is not stated in `02-05`; presumably PostgreSQL replicas. Until
   confirmed, §2 describes a target state and §3's latency targets may be unachievable at W4.
3. **OP-010-OI-03** — **Freshness SLAs per mart (§3) are proposed here and owned by `RP-016`.** They
   must be reconciled; two files must not carry different numbers (`CP-01`).
4. **OP-010-OI-04** — `KPI-094` (zero manual management reports) removes the shadow spreadsheets
   that currently catch errors. That transfer of reliance needs an explicit acceptance by the
   Steering Committee, because it raises the consequence of every incident in this runbook.
5. **OP-010-OI-05** — Non-production masking (`NFR-071`, `NFR-086c`) has no named implementation.
   §4's refresh procedure depends on a masking capability that does not exist yet.
6. **OP-010-OI-06** — Time-series retention is undefined. GPS traces are personal data about
   employees (`05-06` §6.3 `NFR-090`) and evidence in disputes; the retention period is a legal decision, not an
   engineering one, and nobody has made it.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Runbook.md` — all eleven sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a for the runbook; applies to the dashboards it governs
- [x] Bengali counterpart — n/a; English-only by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2
- [ ] Named approver recorded — CTO; DPO co-approval required for §4 and §9
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open items pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ● (deferred). G4 n/a.

---

*`OP-010` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
