---
id: RP-012
title: Alert Threshold and Anomaly Rule Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI with Operations
author: BI Lead with Operations Director and the metric business owners
reviewers: [CTO delegate, Operations Director, CFO delegate, Quality Manager, Support Lead, Contact Centre Supervisor, Content Design Lead]
approver: BI Lead with Operations Director
content_class: D
purpose: >
  Every analytic alert this system raises — its threshold, its anomaly definition, who receives it,
  how it escalates, and when it is suppressed. P06 promises threshold and anomaly alerts delivered "to
  the right role", and the thresholds are business decisions rather than tool defaults: a threshold set
  by whoever built the alert produces either silence or a volume of notifications that trains every
  recipient to ignore all of them, and an alert nobody reads is worse than no alert because it creates
  the belief that someone is watching.
traces_to: [P06, 04-00 P06, NT-021, NT-018, NT-022, M27, M25, M62, M66, RP-001, RP-002, RP-004, RP-011, RP-016, SP-005, SP-031, OP-002, OP-004, TS-005, TS-018, 05-05, 05-05 §12.5, MD-028]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §11 AUT-P06-01 (a metric crosses a defined threshold — deliver an alert to the accountable role through M27 with the value, the threshold and a link; alert only on failure), AUT-P06-02 (an anomaly detected against a metric's expected range — alert the accountable role with observed and expected values), AUT-P06-10 (an SLA countdown reaching its threshold — surface it on the operations board and notify the accountable role)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 Alerting — "threshold and anomaly alerts delivered to the right role"
    verified: 2026-08-20
    class: P1
  - source: project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md — the system, integration and job-failure alert library, which this register bounds against
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §12.5 AUT-053…AUT-060 platform automations including integration error rate, dead-letter age, backup verification, model drift, security anomaly and credential expiry; §12.1 AUT-009 SLA escalation at 50/75/90/100%
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Alert Threshold and Anomaly Rule Register

| Item | Value |
|---|---|
| Alerts registered | **24** (§4.4) |
| Delivery | Through `M27`, per `AUT-P06-01` |
| Boundary | **`NT-021` owns system alerts; this file owns metric alerts** — §4.1 |
| Suppression | Mandatory design, not an afterthought — §4.5 |
| Wave | W4 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the alert schema in §4.3. All six sections retained in order.

---

## 1. Purpose

`04-00` `P06` promises *"threshold and anomaly alerts delivered to the right role"*, and `AUT-P06-01`
requires an alert to carry the value, the threshold and a link to the view. **What neither supplies is
the thresholds**, and the register states why that matters: *"the thresholds are business decisions,
not defaults."*

The failure mode is asymmetric and well understood. A threshold set too tight produces volume, volume
produces habituation, and a habituated recipient misses the one alert that mattered — while the
organisation believes it is being watched. `OPS-03` already states the principle for operational
alerting: *"every alert has a runbook entry; alerts without actions are removed."* This file applies it
to metric alerting.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Business-set thresholds | Defaults, then habituation, then silence-in-effect |
| A named recipient role | Alerts to a distribution list, which nobody owns |
| An action per alert | `OPS-03` breached; the recipient does not know what they are expected to do |
| Suppression rules | One incident produces forty alerts and the fortieth is the informative one |
| Escalation | An unacknowledged alert stops there, and the assumption that someone saw it persists |
| A boundary with `NT-021` | The same failure alerts twice from two libraries with two owners |

---

## 2. Scope

**In scope.** Metric-derived alerts: threshold alerts, anomaly alerts, trend alerts and absence alerts.
Their thresholds, recipients, channels, escalation, suppression, acknowledgement and review.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| **System, integration and job-failure alerts** | **`NT-021`** — §4.1 draws the line |
| Notification message wording, channel behaviour, quiet hours | `NT-018`, `NT-021`, `NT-022`; `M27` |
| Operational SLA escalation on a single job | **`AUT-009`** and `SP-005` — an SLA breach on one order is a workflow escalation, not a metric alert. §4.1 |
| IT incident management | `M66`, `SP-031`, `OP-002` |
| Metric definitions | `RP-001` |
| The views an alert links to | `RP-003`, `RP-004` |
| Data-quality test failures | **`RP-016`** and `AUT-059` — the quality alert belongs to the scorecard |
| Model drift | `AUT-057`, `M26` |
| Security anomalies | `AUT-058`, `M29` |
| Defect and gate escalation | `TS-018` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **BI Lead** (accountable with Operations) | The register and its implementation |
| **Metric business owners** | Setting and owning their metric's threshold |
| **Recipients** — `R05`, `R06`, `R07`, `R17`, `R26`, `R28`, `R32`, `R33` | What they will receive and what they are expected to do |
| **Support Lead** | The boundary with incidents |
| **Content Design** | Alert copy, via `NT-022` |

---

## 4. Content

### 4.1 Four alert families, four owners

Conflating these is how an organisation ends up with the same event notified three times.

| Family | Trigger | Owner | Example |
|---|---|---|---|
| **Workflow escalation** | A single transaction breaches its rule | `AUT-009`, `SP-005`, module automations | One job's SLA at 75% |
| **System alert** | Infrastructure, integration or job failure | **`NT-021`**, `AUT-053`…`AUT-060`, `M66` | Integration error rate above threshold; nightly job did not run |
| **Metric alert** *(this file)* | An **aggregate** crosses a threshold or deviates from expectation | `RP-012` | First-time fix rate below 80% for the branch this week |
| **Data-quality alert** | A dataset fails its tests | **`RP-016`**, `AUT-059` | Party domain completeness below threshold |

**The distinction that matters most is the first against the third.** One job at 75% of its SLA is a
dispatcher's job to fix now (`AUT-009`). *Twelve percent of this branch's jobs breaching SLA this week*
is a manager's problem to investigate. **Same underlying metric, different aggregation, different
recipient, different action** — and if both are raised by the same mechanism the dispatcher receives
management alerts and the manager receives job alerts.

### 4.2 Rules

| # | Rule |
|---|---|
| **AL-01** | **Every threshold is set by the metric's `RP-001` business owner**, not by the alert's builder or by a tool default |
| **AL-02** | **Every alert names one accountable recipient role** (`AUT-P06-01`), never a distribution list. A second role may be copied; only one is accountable |
| **AL-03** | **Every alert states the action expected.** An alert with no action is removed (`OPS-03`) |
| **AL-04** | **Every alert carries the value, the threshold and a link to the view** (`AUT-P06-01`) |
| **AL-05** | **A threshold is not a target.** `KPI-006`'s target is 96%; its alert threshold is the level at which intervention is warranted, and the two are deliberately different numbers (§4.4) |
| **AL-06** | **Suppression is designed with the alert, not added after the first storm** (§4.5) |
| **AL-07** | **Every alert is acknowledged**, and an unacknowledged alert escalates on a stated timer (§4.6) |
| **AL-08** | **An anomaly alert states the observed and expected values** (`AUT-P06-02`), and its expected range's basis |
| **AL-09** | **No alert fires on a metric with no measured baseline** where the alert's basis is deviation from baseline (`KD-20`) |
| **AL-10** | **No alert fires on data whose `RP-016` domain is below threshold** — it raises a data-quality alert instead (`RP-016`, `LT-10` pattern) |
| **AL-11** | **Alert volume is measured per recipient per week**, and a recipient exceeding the §4.7 ceiling triggers a threshold review, not a filter |
| **AL-12** | **Every alert is reviewed for continued value quarterly**; an alert that produced no action in two consecutive reviews is removed (`OPS-03`) |
| **AL-13** | **A `Provisional` metric may raise an informational alert but not an escalating one** (`KD-22`) |
| **AL-14** | **No alert is the sole control for a statutory deadline** — `RP-009`'s T−15 ladder is the control; an alert supports it |
| **AL-15** | **Alerts respect `NT-022` quiet hours** except the four classified `immediate` in §4.4 |

### 4.3 The alert schema

| # | Field | Content |
|---:|---|---|
| 1 | `id` | `ALR-nn`, permanent |
| 2 | `metric` | The `RP-001` identifier |
| 3 | `type` | `threshold` · `anomaly` · `trend` · `absence` |
| 4 | `condition` | The precise trigger, with its aggregation and window |
| 5 | `threshold` | The value, **and its owner** (`AL-01`) |
| 6 | `severity` | `informational` · `warning` · `urgent` · `immediate` |
| 7 | `recipient` | One accountable `Rnn` (`AL-02`) |
| 8 | `copy_to` | Optional |
| 9 | `channel` | Per `NT-018`/`NT-022`; `M27` delivers |
| 10 | `action` | What the recipient is expected to do (`AL-03`) |
| 11 | `link` | The `RP-003`/`RP-004` view (`AL-04`) |
| 12 | `suppression` | The rule that prevents repetition (`AL-06`) |
| 13 | `escalation` | Timer and next role (`AL-07`) |
| 14 | `review` | Last reviewed, and whether it produced action (`AL-12`) |

### 4.4 The register — 24 alerts

**`absence` alerts are the family most often forgotten**: a metric that stops arriving looks like a
metric with no exceptions.

| `id` | Metric | Type | Condition | Threshold | Recipient | Severity |
|---|---|---|---|---|---|:--:|
| `ALR-01` | `KPI-006` SLA compliance | threshold | Branch weekly, below | **90%** *(target 96%)* | `R06` | warning |
| `ALR-02` | `KPI-006` | threshold | Network weekly, below | 92% | `R05` | urgent |
| `ALR-03` | `KPI-006` hold rate | anomaly | Branch hold rate above class median × 1.5 | relative | `R05` | warning |
| `ALR-04` | `KPI-004` first-time fix | threshold | Branch monthly, below | **78%** *(target 88%)* | `R06` | warning |
| `ALR-05` | `KPI-005` rework rate | threshold | Branch monthly, above | **6%** *(target < 3%)* | `R32` | warning |
| `ALR-06` | `KPI-005` | trend | Network rising 3 consecutive months | any | `R32`, `R05` | urgent |
| `ALR-07` | `KPI-020` CSAT | threshold | Branch monthly, below | **4.0** *(target 4.7)* | `R06` | warning |
| `ALR-08` | `KPI-020` survey response rate | anomaly | Branch below class median × 0.6 | relative | `R05` | warning |
| `ALR-09` | `KPI-047` van-stock variance | threshold | Technician monthly, above | **3%** *(target < 1%)* | `R17` | warning |
| `ALR-10` | `KPI-042` inventory accuracy | threshold | Location count, below | **95%** *(target 98%)* | `R17` | urgent |
| `ALR-11` | `KPI-044` stockout-caused delays | threshold | Weekly, above | 6% | `R17` | warning |
| `ALR-12` | `KPI-037` claims within 72 h | threshold | Weekly, below | **88%** *(target 95%)* | `R28` | urgent |
| `ALR-13` | Claim approaching brand window | threshold | Any claim within 5 days of the window (`BRU-WTY-08`) | 5 days | `R28` | **urgent** |
| `ALR-14` | `KPI-056` revenue leakage | threshold | Monthly unbilled completed work above | **1.5%** | `R26` | urgent |
| `ALR-15` | `KPI-050` close cycle | threshold | Close day 4 with checklist incomplete | day 4 | `R26`, `R03` | urgent |
| `ALR-16` | `RP-009` statutory deadline | threshold | T−15 working days (`RP-009` §4.6) | T−15 | `R26` | urgent |
| `ALR-17` | `RP-009` statutory deadline | threshold | **T−5 with the filing not approved** | T−5 | `R03`, Legal | **immediate** |
| `ALR-18` | `KPI-062` certifications current | threshold | Any certification expiring within 30 days | 30 days | `R32`, `R30` | warning |
| `ALR-19` | `KPI-063` uncertified assignable | threshold | **Any occurrence** *(target zero)* | 1 | `R32` | **immediate** |
| `ALR-20` | `KPI-090` orphaned accounts | threshold | **Any account beyond 24 h after a leaver** | 1 | `R33` | **immediate** |
| `ALR-21` | `KPI-016` technician app usage | threshold | Weekly, below | **90%** *(target > 95%)* | Technical Director | warning |
| `ALR-22` | `KPI-017` offline sync failures | threshold | **Any occurrence** *(target zero)* | 1 | `R02` | **immediate** |
| `ALR-23` | Any `E1`–`E7` metric | **absence** | No value received for 2 consecutive expected periods | 2 periods | `R33`, BI Lead | urgent |
| `ALR-24` | `KPI-024` complaint resolution in SLA | threshold | Monthly, below | **88%** *(target 95%)* | `R32` | warning |

**Look at the threshold column against the target column.** `AL-05` in practice: `KPI-006`'s target is
96% and its branch alert fires at 90%. **Alerting at target would alert almost every branch almost
every week** during ramp-up, which is how habituation begins. The threshold is set where intervention
changes the outcome, and it tightens as the target is approached — recorded in §4.8.

**Four alerts are `immediate` and bypass quiet hours** (`AL-15`): `ALR-17` a statutory filing unapproved
at T−5, `ALR-19` an uncertified technician assignable to brand warranty work, `ALR-20` an orphaned
account past 24 hours, `ALR-22` any offline sync failure. Each has a **zero target** in `06-02` and a
consequence that is legal, contractual or a data loss.

### 4.5 Suppression

`AL-06`. Without these, one cause produces many alerts and the recipient learns to batch-dismiss.

| # | Rule |
|---|---|
| **AL-16** | **De-duplicate on cause, not on message.** Twelve SLA breaches from one parts shortage are one alert with a count of twelve |
| **AL-17** | **One alert per metric per recipient per period.** A weekly threshold alert fires once a week, not on every recalculation |
| **AL-18** | **A firing alert suppresses its own repetition until acknowledged or the condition clears** |
| **AL-19** | **A parent condition suppresses its children.** If the warehouse load failed (`ALR-23`), the metric alerts that depend on it are suppressed — otherwise a single pipeline failure produces the largest alert storm the system can generate |
| **AL-20** | **A planned event suppresses its alerts** — a scheduled count suppresses inventory-accuracy alerts for that location during the count |
| **AL-21** | **A data-quality failure suppresses metric alerts on that domain and raises the quality alert instead** (`AL-10`) |
| **AL-22** | **Suppression is logged.** A suppressed alert is recorded so that "nothing fired" can be distinguished from "everything was suppressed" |

> **`AL-19` and `AL-22` together prevent the worst case**, which is a silent system: a pipeline failure
> suppresses every downstream alert, nobody is notified, and the absence of alerts is read as health.
> `ALR-23`'s absence alert is the counterweight, and it is why it exists.

### 4.6 Escalation and acknowledgement

| Severity | Acknowledge within | Escalates to | Then |
|---|---|---|---|
| `informational` | — | — | Logged only |
| `warning` | 1 working day | The recipient's manager | Weekly digest if unacknowledged twice |
| `urgent` | 4 working hours | Named escalation role | Operations Director at 1 working day |
| `immediate` | **1 hour, any hour** | CTO or CFO per the alert | Steering item if unresolved at 24 hours |

`SP-005` holds the operational escalation matrix; **this table is the analytic-alert ladder and it
follows the same shape deliberately**, so a recipient does not learn two escalation conventions.

### 4.7 Volume ceilings

`AL-11` — measured, and a breach reviews the threshold rather than adding a filter.

| Recipient class | Ceiling per week |
|---|---|
| `R06` branch manager, `R08` agent, operational roles | **5** |
| `R17`, `R26`, `R28`, `R32` functional managers | 10 |
| `R05`, `R33` network and platform | 15 |
| `R01`–`R04` executive | **2** — and only `urgent` or `immediate` |

**A recipient at the ceiling is a signal about the thresholds, not about the recipient.** Adding a
filter hides the alert; reviewing the threshold fixes it.

### 4.8 Threshold evolution

Thresholds are not fixed for the programme's life, and the rule prevents them being quietly loosened.

| # | Rule |
|---|---|
| **AL-23** | **Thresholds tighten as targets are approached**, reviewed at each wave gate against the `06-02` W4 and W8 target for that metric |
| **AL-24** | **A threshold may be loosened only by its `RP-001` business owner, with the reason recorded.** A loosened threshold with no recorded reason is indistinguishable from an alert being switched off |
| **AL-25** | **A zero-target metric's threshold is never loosened** — `ALR-19`, `ALR-20`, `ALR-22` and the statutory alerts stay at one occurrence |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | Every metric, its owner, its target and its baseline |
| **[`RP-016`](RP-016_Data_Quality_Scorecard_Definition.md)** | The quality gate (`AL-10`, `AL-21`) |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md), `RP-004` | The views alerts link to (`AL-04`) |
| [`RP-009`](RP-009_Statutory_and_Regulatory_Report_Format_Register.md) | `ALR-16`, `ALR-17` and the T−15 ladder they support |
| [`RP-011`](RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md) | Class medians for the relative anomaly alerts (`ALR-03`, `ALR-08`) |
| **[`NT-021`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md), `NT-018`, `NT-022`** | The system-alert boundary, channel behaviour and quiet hours |
| `M27` | Delivery (`AUT-P06-01`) |
| `SP-005` | The escalation shape §4.6 follows |
| `05-05` §12.5, `AUT-009` | The neighbouring automation families |
| `MD-028` | SLA definitions behind `ALR-01`…`ALR-03` |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Quarterly** (`AL-12`), and at every wave gate for threshold tightening (`AL-23`) |
| Trigger for out-of-cycle review | A volume-ceiling breach; an alert storm; a metric restatement; a target change; an alert that produced no action twice |
| Owner | BI Lead with Operations Director; each threshold has its metric's business owner |
| Data file | `RP-012_Alert_Register.csv` — 24 alerts × 14 fields · `RP-012_Suppression_Rules.csv` · `RP-012_Volume_Log.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Every threshold in §4.4 is proposed by the content function, and `AL-01` requires the metric's business owner to set it.** Twenty-four thresholds across eight owners, none consulted. **A threshold nobody owns is the tool default in a different form**, which is precisely what this file exists to replace | BI Lead with each metric business owner | **W4 — before any alert is enabled** |
| **O-02** | **Nine of the 24 alerts fire on metrics with no measured baseline**, and `AL-09` forbids a deviation-basis alert on an unbaselined metric. `KPI-006`, `KPI-005`, `KPI-007`, `KPI-024`, `KPI-047` and others read "unmeasured" in `06-02` §2. **Threshold alerts on absolute values can still fire; anomaly and trend alerts cannot** | Programme with BI Lead | **W4 — via `RP-015`** |
| **O-03** | **`ALR-03` and `ALR-08` need a class median**, which requires `RP-011`'s branch classes and several quarters of history. **The two anomaly alerts that detect league gaming cannot operate during the period when gaming incentives are strongest** — `RP-011` `O-06` records the same gap | BI Lead | W4 |
| **O-04** | **The `NT-021` boundary has not been reconciled with `NT-021` itself.** §4.1 asserts that `NT-021` owns system alerts and this file owns metric alerts; **`NT-021` was written before this file existed** and may already cover metric-derived conditions. Both libraries must be read against each other or the same failure alerts twice | Content Design Lead with BI Lead | **W4** |
| **O-05** | **`AL-11` volume measurement and `AL-22` suppression logging both need a mechanism that does not exist.** Without them, the ceilings in §4.7 are unenforceable and a silent system (`AL-19`) is undetectable | Platform Engineering with BI Lead | **W4** |
| **O-06** | **`AL-15` quiet-hours exemption for four `immediate` alerts needs `NT-022`'s agreement.** An alert that wakes a CFO at 03:00 is a policy decision, and `ALR-17`'s statutory case is the one most likely to do it | Content Design Lead with CFO | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the alert schema
- [x] **Four alert families separated with their owners, and the workflow-versus-metric distinction explained**
- [x] Twenty-five rules stated, including threshold-is-not-target and alert-with-no-action-is-removed
- [x] Fourteen-field alert schema including action, suppression and review-produced-action
- [x] **24 alerts registered with threshold shown against target, so the gap is visible and justified**
- [x] Four `immediate` alerts identified, each with a zero target and a legal, contractual or data-loss consequence
- [x] **Seven suppression rules, including parent-suppresses-children and the suppression log that prevents a silent system**
- [x] An `absence` alert included as the counterweight to suppression
- [x] Escalation ladder following `SP-005`'s shape so recipients learn one convention
- [x] Volume ceilings per recipient class, with a breach reviewing the threshold rather than filtering
- [x] Threshold evolution rules preventing silent loosening, with zero-target metrics fixed
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` 24 thresholds unowned — outstanding; blocks enabling any alert**
- [ ] **`O-04` `NT-021` boundary unreconciled — outstanding; risk of double alerting**
- [ ] **`O-05` no volume or suppression logging — outstanding; a silent system would be undetectable**
- [ ] Named approvers recorded — **pending BI Lead and Operations Director**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
