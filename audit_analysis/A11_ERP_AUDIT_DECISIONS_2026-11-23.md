# A11 ERP audit — owner decisions, 2026-11-23

Area A11 "Insights & Intelligence": M25 Business Intelligence · M26 AI/ML Services ·
M62 Data Platform & Governance · M63 Process Automation (approvals, delegation of authority).

**How this list was produced.** Six independent read-only audits (one per module, one on
cross-area relations, one on external ERP and legal benchmarks) on the live estate, then every
critical and high finding re-measured by me before anything was changed, then a screen-by-screen
drive-through of all 42 screens, 18 reports and 12 forms in the in-app browser. Evidence:
`1000_fix_codebase/scratch/a11_deep/` (REGISTER.md, findings/, evidence/).

**Totals:** 3 critical · 27 high · 37 medium · 13 low findings. Of the 14 links the registry
promises between A11 and the rest of the ERP, 1 is fully wired, 6 partial, 7 missing.

**Calibration:** the live estate currently holds masters and opening-balance journals only (no
service orders, invoices or stock moves yet), so every "0" on an operational dashboard is honest.
The problems are in wiring and configuration — what will happen when real transactions start.

Each decision carries a recommendation. Approve as recommended, or state the alternative.
"Needed by": **go-live** = must be answered before real transactions; **soon** = within the
first weeks; **later** = backlog.

---

## Part A — being fixed now, no decision needed (for information)

**Status 2026-11-23: A1–A11 are built, tested and DEPLOYED to both estates** (`fix_real` 8069 and
`fix_dev` 8090). Verified after deploy: live AR Outstanding ৳15,38,59,759.09 (= the ledger),
52 active automations with 0 broken bindings, the six data-platform tiles live with honest
captions, and the screens re-driven in the browser. Integration suites after all changes:
412 backend + 599 workspace tests passing.

| # | What was wrong | What the fix does |
|---|---|---|
| A1 | **M63 automation register was fiction (critical).** 60 automations all "active", each naming an engine; 0 of 60 references resolved to anything that exists (32 server actions, 16 Airflow DAGs, 12 service functions that do not exist). The catalogue file asserted "ZERO gaps". | Every row now names what really executes it (an Odoo scheduled action, a model method, or an event consumer), verified by the system at run time; rows are labelled fully automated / partially automated / not implemented; the gap report, tiles and screens count only what is real; a row cannot be activated unless its reference resolves. |
| A2 | **BI reported receivables of ৳0** on the CFO dashboard and finance packs while the books carry ৳15.39 crore of migrated open receivables. | BI now counts migrated balances the same way the receivables module does, and adds a tie-out line to the general ledger so a CFO can reconcile. |
| A3 | One failing data source blanked every later figure on a dashboard and broke PDF/Excel exports. | Each source is isolated; a failing source blanks only its own tile and is logged. |
| A4 | Money in BI reports had no currency sign; AI/ML reports printed raw codes (`live_engine`, `production`, `deployed`). | Money carries ৳; codes are shown as labels. |
| A5 | "STP Share" read 75% on a database with nothing automated; "Automation Rate" read 0% with nothing to measure. | Both show "—" with an honest caption until routine work is registered. |
| A6 | **Data Platform configuration was seed residue:** all pipelines, contracts and quality rules attached to one unrelated entity; quality rules "passing" that were never measured; metrics "published" with no version; contracts "active" with no signature. | An explicit, logged, repeatable repair (run by me on each estate, before/after recorded) plus guards so those states cannot return. The registry's six Data Platform KPI tiles are added with honest bases. |
| A7 | The "Delegation of Authority" grid showed neither who approves nor up to how much; the "Catalogue & Glossary" screen showed a lineage report; "Scheduled Jobs" listed 16 Airflow jobs that do not exist. | Grids show approver, threshold and escalation target; a real catalogue; the real scheduled jobs. |
| A8 | Approval engine: a race between simultaneous approve/reject; requests with no approver could wait forever; expired approvals died silently; two people could swap approval queues permanently. | All closed with tests. |
| A9 | AI/ML: "override rate" counted never-reviewed suggestions as decisions; the GenAI status was hard-coded; two deployed models declared no fallback; no evaluation could be recorded for a deployed model. | Corrected; fallback rule enforced on new promotions. |
| A10 | All four modules' "Quick Cross-Navigation" and Bengali labels disagreed with the registry. | Aligned to the registry. |
| A11 | Role Center tile "Awaiting Approval" (service orders waiting for the customer) was confused with the approver inbox. | Relabelled "Awaiting Customer Approval". |

Test status before any change: 330 + 364 tests passing, 0 failing (private copies). The same
suites are re-run after the changes before anything is deployed; live verification follows.

---

## Part B — decisions

### Direction of the four platforms

**D1 — The 8 automations that do not exist, and the 27 that only partly exist (M63).**
Needed by: **soon.**
Of the 60 automations in the business catalogue, 52 have real logic somewhere in the system
(25 complete, 27 partial) and 8 have none: technician tracking link (AUT-003), draft estimate from
fault code (004), parts-unavailable network search / transfer / purchase (007), registration
points and welcome journey (029), dead-stock disposition (037), model-drift alert and retraining
(057), security-anomaly session suspend (058), data-quality failure blocking a dashboard (059).
The register now says this truthfully. Nothing is built by this audit.
*Recommendation:* accept the truthful register now; schedule AUT-003, 004, 007 and 029 first
(they are customer-visible), and let each area owner rank the 27 partial rows after go-live.
*Alternative:* commission all 8 now (multi-area build; several weeks).

**D2 — Is Airflow part of the production runtime? (M63).**
Needed by: **soon.**
The register claimed 16 automations run as Airflow DAGs. None exist; Airflow is deployed but
runs only two unrelated jobs. In this estate every scheduled automation is an Odoo scheduled
action.
*Recommendation:* business automations run as Odoo scheduled actions only (visible and
governable in-app); keep Airflow only for data-platform batch work if D5 says yes.
*Alternative:* build the 16 DAGs in Airflow and connect them back to the register.

**D3 — Is a separate workflow engine needed? (M63).**
Needed by: **later.**
The specification describes a process engine (definitions with steps, instances, compensation).
What exists is a shell: no production code ever starts a "workflow instance". Meanwhile the
approval engine is real and is used by 117+ document types across the ERP.
*Recommendation:* treat approvals as the workflow runtime; retire the empty "Open Workflows"
shell at the next registry regeneration; revisit only when a genuinely multi-step process needs
orchestration (employee onboarding/offboarding, AUT-047/048, would be the natural first case).
*Alternative:* build the process engine as specified (large; second engine to govern).

**D4 — What is the business-rule repository? (M63).**
Needed by: **soon.**
Four "business rules" are prose sentences; nothing evaluates them; the "Rule Change Log" is a
version counter with no history. The limits that really govern approvals live in the delegation
ladders and system parameters.
*Recommendation:* (a) the delegation ladders and parameters become THE governed rule book;
(b) the repository is relabelled "rule register — documented, not executed by the system" and
given real change history (who, what, when, why), which ISO 9001 requires for controlled
documents; (c) do not build an expression evaluator.
*Alternative:* build an executable rule engine with approval, effective dating, simulation and
rollback (large, and arbitrary-expression execution is a control risk).

**D5 — Should data pipelines actually run? (M62).**
Needed by: **go-live** (decides whether BI "certified datasets", freshness and lineage are real).
Four pipelines are registered as active (real-time / hourly / daily). None has ever run; there is
no executor. A real PostgreSQL→ClickHouse sync service exists in the repo but is connected to
nothing. Until an executor exists, "certified datasets", freshness and lineage in BI are labels.
*Recommendation:* connect the existing sync service as the executor (scheduled run → recorded
run, freshness stamps, lineage) as a planned build if the analytics warehouse is in the
production target; until then the screens say "register — no executor connected".
*Alternative:* register-only for now (already honest after this audit).

**D6 — How deep should "one certified number" go? (M25 ↔ M62).**
Needed by: **later.**
The metric registry ("one certified number") was read by nobody; BI, FP&A and the analytics
portal each compute their own figures. I am binding BI's figures to the registry definitions
(consumer registration + consistency tests) so the registry describes what BI really computes.
*Recommendation:* accept "BI computes, registry defines and versions" for now.
*Alternative:* a full metric service every consumer must call (about 7 person-weeks in the
specification).

### Governance content — business acts only you can perform

**D7 — Appointments.**
Needed by: **go-live.**
All ten A11 governance groups contain only the administrator account (342 active users, none
appointed): BI Author, BI Certifier, BI Company-Wide Reader, BI Finance Reader, BI Sync Operator,
Data Governance Officer, ML Data Scientist, ML Evaluation Reviewer, ML Model Owner, DoA
Administrator. Consequences today: no dashboard can be certified (author ≠ certifier), no model
version can be promoted, no data-governance decision has a second decider, and delegation of
authority has one administrator. (The five approval *tiers* are staffed: 20 / 42 / 7 / 3 / 1.)
*Recommendation:* appoint at least two people for each sensitive group — DoA Administrator:
CFO office + Financial Controller; BI Certifier + Steward: Financial Controller + Strategy/BI
lead; BI Finance Readers: CFO and controllers; Data Governance Officer: Compliance/DPO + IT
Security; ML roles: Head of IT + one analyst. I need names (or roles mapped to names).
*Alternative:* fewer, broader groups (higher key-person risk).

**D8 — Delegation of Authority schedule.**
Needed by: **go-live.**
What is on the Delegation screen does not govern amounts: approver groups and escalation
targets are empty on all 6 rows, 2 rows are seed residue (`seed_role`), 3 rows name decision
domains no document uses (`write_off`, `estimate`, `expense`). The amounts that really apply
are developer defaults written inside each document type — nobody in the business chose them.
Of 53 amount-governed document types only 2 have a formally ruled schedule (Annex A). Among
today's defaults: **credit notes and AR write-offs up to ৳10,000, stock write-offs up to
৳25,000, a loyalty scheme or a marketing campaign up to ৳50,000, and a 10% estimate discount
need no approval at all**; a payout run up to ৳2,000,000 and a manual journal up to ৳500,000
need only a branch / operations manager. The same decision can also carry different limits in
different places (write-off: matrix 10,000 / stock count 25,000 / inventory parameter 5,000;
requisition: matrix 100,000 vs coded ladder 50,000 / 500,000 / 2,000,000).
*Recommendation:* (1) CFO and MD review Annex A line by line and mark *accept* or *change* — I
load accepted lines as formal schedules (no behaviour change) and changed lines as new rulings
with an effective date; (2) remove the two seed rows and re-point the three dead matrix rows to
the real decision domains with named approver groups and escalation targets; (3) in every case
set the no-approval bands deliberately, not by default.
*Needed from you:* the marked-up Annex A (or "accept all as today", or your own schedule), and
who approves each decision domain.
*Alternative:* a fresh DoA written top-down (slower; every difference from today's defaults is
a behaviour change to test).

**D9 — Segregation of duties inside approvals (M63 ↔ M60).**
Needed by: **soon** (after the parallel governance work lands).
The approval engine blocks self-approval (requester, creator, anyone who changed the amount, and
their delegates) but never consults the 63 segregation-of-duties controls. An approver whose role
conflicts with the requester's is routed to normally.
*Recommendation:* evaluate active SoD controls when approvers are derived: exclude conflicting
candidates; if nobody eligible remains, escalate rather than route. Needs your answer on which
controls block *routing* versus *decision*; coordinate with the governance (A10) work in flight.
*Alternative:* leave as self-approval exclusion only.

**D10 — AI/ML governance pack.**
Needed by: **go-live** for anything a model is allowed to influence.
(a) Every model lacks minimum data bars — without them **no new model version can ever be
promoted**; (b) no model has an owner or review date; (c) no guard-rail is defined on live while
six versions sit in "Deployed"; (d) no bias test exists for the two people-affecting models
(dispatch scoring, lead scoring) — the research notes Bangladesh's data-protection law treats
automated evaluation of a worker as "profiling" (confirm with counsel); (e) three "models" are
really report aggregators (trade-in valuation, predictive maintenance, BI aggregator) labelled
`live_engine`; (f) the title says "14 models", 7 exist.
*Recommendation:* (a) you declare bars per model (e.g. dispatch: 6 months / 5,000 orders; lead
scoring: 12 months / 2,000 leads) — the screens have the fields; (b) owner = Head of IT, annual
review; (c) two starter guard-rails (no eligible technician → manual dispatch; low lead score →
"unscored, qualify manually"); (d) record a bias test before go-live; (e) relabel the three as
"aggregator"; (f) retitle to the true count until more models are built.
*Alternative:* register the 9 missing models as "planned" rows to keep the "14".

**D11 — Should dispatch scoring go through the AI/ML gateway? (M26 ↔ M02).**
Needed by: **go-live.**
The dispatch board calls its own ranking directly: no run is logged, no guard-rail applies, no
decision record exists. So the promised "70% auto-assign" and "dispatcher agreement ≥ 90%" can
never be measured, and the technician-ranking model is the one people-affecting model with a
real production consumer.
*Recommendation:* route dispatch suggestions through the AI/ML gateway (small logging overhead),
which makes auto-assign measurable and gives every technician assignment an explainable record.
*Alternative:* keep native scoring and drop the auto-assign targets.

**D12 — Bengali fault taxonomy.**
Needed by: **go-live.**
None of the 24 fault codes carries Bengali text, so the promised "fault classification from
Bengali text" can never match a Bengali-speaking customer's complaint. Model explanations are
English-only.
*Recommendation:* a native speaker approves Bengali names for the 24 fault codes (I can prepare a
draft list for review); load them as taxonomy data; then connect the conversational-AI module
(M32) to the classifier. 
*Alternative:* English-only intake scripting.

**D13 — Record retention floors.**
Needed by: **go-live** (legal).
All four retention policies have statutory floor = 0; service orders are set to "archive after 36
months". Research (to be confirmed by your tax adviser): VAT records 5 years (VAT & SD Act 2012
s.107), income-tax records about 6 years from the assessment year (Income Tax Act 2023 s.130 —
exact wording not verified), data-protection processing register at least 5 years, and
rectification/erasure requests actioned within 30 days.
*Recommendation:* after adviser confirmation set floors of 60 months (VAT) / 72 months (tax) on
service, invoice and contract records; keep identity documents for the relationship plus 5 years;
never purge below a floor; cite the law on each policy.
*Alternative:* leave at 0 (records could be archived or purged before the legal minimum).

**D14 — Masking scope.**
Needed by: **go-live.**
Six sensitive fields (identity document number, private phone/email, partner email, VAT number…)
are masked only when read through the workspace. The standard Odoo screens, direct API reads,
report packs and exports are not masked. Live data: 24,194 partners, 504 employees with national
ID and phone numbers.
*Recommendation:* enforce masking on every read path for roles without entitlement (identity
module work item), before go-live.
*Alternative:* workspace-only (acceptable only if nobody can reach native screens).

**D15 — Working-hours calendar for approval deadlines.**
Needed by: **soon.**
No calendar exists on live, so every approval deadline is wall-clock: a request raised Friday
evening is due Saturday; holidays escalate.
*Recommendation:* HR confirms the official calendar (working days, hours, public holidays) and it
is loaded as the company calendar.
*Alternative:* wall-clock deadlines.

**D16 — One escalation picture, or three documented ones?**
Needed by: **later.**
Escalation runs as three parallel systems: approvals (M63), service-SLA ladder (M01), field-order
SLA (M02). After this audit the "Escalations MTD" tile counts approvals; SLA escalations remain
elsewhere.
*Recommendation:* one escalation report with three sections.
*Alternative:* document the split.

**D17 — Approval chain patterns.**
Needed by: **later.**
Only "any one approver" and "all approvers" exist. Ordered chains, quorum ("two of five") and
escalate-by-value are in the specification but not built.
*Recommendation:* add only what the DoA schedule (D8) requires.
*Alternative:* build all three.

**D18 — Block activation of an unsimulated delegation rule?**
Needed by: **soon** (carried over from the earlier audit).
All six in-force rules were never simulated; activation is allowed.
*Recommendation:* warn for one month, then block activation until the rule has been simulated on
real records.

### Business Intelligence specifics

**D19 — Block an export when it cannot be logged?**
Needed by: **soon.**
The BI specification says "block export if logging is unavailable" (every export of customer or
financial data is logged). The implementation deliberately does the opposite ("a logging failure
never blocks the download") in all three places that write the export log.
*Recommendation:* follow the specification — write the log first, then deliver; if the log cannot
be written, refuse the export with a clear message.
*Alternative:* keep availability-first (an export-log outage then produces unlogged exports).

**D20 — Which BI capabilities ship before go-live?**
Needed by: **go-live.**
Missing: threshold alerts that actually notify anyone (today in-app only), filing report runs as
records, drill-down from a figure to its records, bursting one report per branch, analytics in the
customer portal, personal performance view, content review cycle.
*Recommendation:* (1) alert delivery through the existing notification queue, (2) report-run
filing, (3) drill-down to records — before go-live; the rest later.
*Alternative:* all, or none.

**D21 — Analytics portal engine.**
Needed by: **later.**
The analytics portal is wired to the Data Platform's API and Superset; BI's own embed-token
machinery has no consumer anywhere.
*Recommendation:* choose one engine — if Superset, retire BI's embed machinery; if in-house, wire
the portal to it.
*Alternative:* leave both.

**D22 — Routine-work register (the 85% automation target).**
Needed by: **soon.**
The automation rate is measured over registered recurring tasks with monthly volumes. None are
registered, so the rate cannot be measured (it now shows "—").
*Recommendation:* each area owner lists recurring tasks and volumes after go-live training; the
tile stays "—" until then.

### Registry

**D23 — Regenerate the navigation registry.**
Needed by: **soon.**
The workspace ships more than the frozen registry lists (BI 26 screens vs 13, AI/ML 18 vs 10,
Data Platform 22 vs 11, Process Automation 15 vs 8) and Data Platform's six KPI tiles differed.
This audit aligns cross-links, Bengali labels and the missing tiles; the supersets remain.
*Recommendation:* regenerate the registry once for all areas after the current audit waves land
(same decision as the one carried from the November 7 sweep).
*Alternative:* keep the frozen registry and hide the extra screens.

---

## Annex A — approval authority in force today

`audit_analysis/A11_DOA_IN_FORCE_2026-11-23.md` — all 53 amount-governed document types with
the bands and approver tiers applied right now. Source: the authority engine itself
(`fix.dofa.ladder.thresholds_for` and each model's coded default), read from a private copy of
the live database on 2026-11-23 (`scratch/a11_deep/evidence/dofa_effective.out`). Tiers:
1 Team Lead / Contact-Centre Supervisor (20 holders) · 2 Branch / Operations Manager (42) ·
3 CX / Commercial Director (7) · 4 CFO / CCO / COO (3) · 5 Managing Director / Board (1).

## Annex B — external benchmark and legal sources

`scratch/a11_deep/findings/A6_RESEARCH.md` (target capability tables per module, standard KPI
definitions, cited sources). Legal points there are research findings with stated caveats, not
legal advice.
