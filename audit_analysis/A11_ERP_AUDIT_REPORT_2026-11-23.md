# A11 ERP audit report — Insights & Intelligence (M25 / M26 / M62 / M63)

Date: 2026-11-22/23 · Area A11 of the 1000 FiX integrated platform
Companion documents:
- Owner decisions (23, each with a recommendation + the delegation annex):
  `audit_analysis/A11_ERP_AUDIT_DECISIONS_2026-11-23.md`
- The approval authority in force today, all 53 document types:
  `audit_analysis/A11_DOA_IN_FORCE_2026-11-23.md`
- Working register, defect list and every measurement:
  `1000_fix_codebase/scratch/a11_deep/REGISTER.md`
- Six independent audit reports: `scratch/a11_deep/findings/A1..A6`
- Live screen-by-screen evidence: `scratch/a11_deep/evidence/IAB_PASS1_LIVE.md`

---

## 1. What was audited and how

**Scope.** The four modules of area A11 — M25 Business Intelligence, M26 AI/ML Services,
M62 Data Platform & Governance, M63 Process Automation (approvals, delegation of authority,
business rules) — as an ERP area: data capture forms, functions, dashboards, approval and
business flows, business rules and logic, professional exports, calculations and accounting
logic, and every cross-relation to other areas.

**Contract measured against.** The navigation registry (`contracts/nav/registry.json`):
42 screens, 18 report chips, 12 forms, 24 KPI tiles, 14 cross-links; plus each module's
specification (34/42/38/32 functional requirements) and its business-rule list.

**Method.**
1. **Two clean engineering baselines first** (so "pre-existing" and "caused by us" can be told
   apart): backend suites 330 passed / 1 skipped / 0 failed; workspace suites 364 passed /
   0 failed.
2. **Six independent read-only audits** — one per module, one on cross-area relations, one on
   external ERP + legal benchmarks. Each finding carries file:line and a measured query/RPC.
3. **Lead re-verification of every critical and high finding** before any change: 13 of 13
   spot-checks held (see REGISTER §"Lead re-verification").
4. **A live screen-by-screen drive-through in the in-app browser on the production estate**:
   42/42 screens, 18/18 report chips, 12/12 forms opened, plus every KPI tile read and
   compared with its JSON route.
5. **Fixes built on private databases** (one per builder, so runs could not collide), then
   **integrated on a fresh copy** and re-tested.
6. **Professional exports validated as files**: 29 report packs × CSV, Excel and PDF = 87/87
   downloads valid, each PDF carrying logo, letterhead, document number, generation stamp and
   footer.

**An important calibration.** The live estate (`fix_real`, 8069) holds masters and 35
opening-balance journals — no service orders, invoices or stock movements yet. So the zeros on
the operational dashboards are honest. **The audit's subject is wiring and configuration: what
will happen when real transactions start.** That is what most findings below are about.

**Totals: 3 critical · 27 high · 37 medium · 13 low.** Of the 14 cross-links the registry
promises between A11 and the rest of the ERP: **1 wired · 6 partial · 7 missing.**

---

## 2. The critical findings, and what happened to them

### C1 — The automation register was fiction (M63) — **FIXED**
60 automations, all marked active, each naming an engine. **0 of 60 references resolved** to
anything that exists: 32 pointed at server actions that do not exist, 16 at Airflow DAGs that do
not exist, 12 at service functions that do not exist (four of the six named modules do not exist
at all). The catalogue file nevertheless asserted "ZERO gaps", and the gap-report only matched
its own placeholder strings.

The audit also established that for **52 of the 60** rows the described behaviour *does* exist
elsewhere in the estate as an Odoo scheduled action, a model method or an event consumer — and
that **8 rows describe automations nobody built** (AUT-003 tracking link, 004 draft estimate,
007 parts-unavailable sourcing, 029 registration points, 037 dead-stock disposition, 057 drift
retraining, 058 anomaly session-suspend, 059 quality-failure dashboard block).

*Fixed:* the register now names, for every row, the mechanism that really executes it and the
engine verifies the reference at run time. An active row whose reference does not resolve is
refused at save, with a message naming the reference.

| | before | after (verified on the integration database) |
|---|---|---|
| engine values | 3 fictional kinds | 23 Odoo scheduled actions · 21 model methods · 8 event consumers · 8 manual |
| implementation | unstated | 20 full · 32 partial · 8 none |
| active rows | 60 (all, unverified) | 52 verified (20 full + 32 partial); 8 correctly inactive |
| retired phantom values | 60 | 0 |
| my independent re-check of all 60 references | 0 resolvable | **0 unresolved** |

A migration carries the truth to existing databases: it deactivates non-catalogue rows that
still carry a retired engine value and says why ("its engine reference (airflow
'dag: fix_aut999') could not be resolved to anything executable").

### C2 — BI reported receivables of ৳0 (M25) — **FIXED**
The CFO dashboard and the finance/executive packs showed **AR Outstanding ৳ 0** while the books
carried **৳ 15,38,59,759.09** of migrated open receivables (957 parties). The BI metric bank
counted only operational invoices, of which there are none yet; the receivables module (M20) had
already been corrected for exactly this in an earlier audit, and the pack claimed to share its
source.

*Fixed:* BI reads the migrated balances through the same helper M20 uses, only for callers who
hold the finance entitlement (otherwise the tiles are withheld, not zeroed), and the finance pack
adds a ledger tie-out line.

Measured on a copy of the live database:
`open invoices ৳0 + legacy take-on ৳15,38,59,759.09 = total ৳15,38,59,759.09; AR per general
ledger ৳15,38,59,759.09; difference 0.00`.

**Deployed and confirmed on the live estate:** the CFO Dashboard now shows
`AR Outstanding ৳ 15,38,59,759.09` (screenshot in
`scratch/a11_deep/evidence/`), and the tile's own basis caption reads "AR Outstanding and
Overdue > 60d cover open issued invoices PLUS the legacy take-on still open on the AR control
(M20 basis); a caller without the BI finance entitlement sees '—' on those tiles."
On the reference estate the pack additionally surfaces a **৳361,841.61 difference** between the
receivables total and the ledger — a gap it previously concealed entirely.

### C3 — The "one certified number" service was read by nobody (M62) — **PARTLY FIXED; the rest is a decision**
The metric registry — the module's whole purpose — was read by no code: its five definitions
were hand-made rows on two estates, had no versions, no consumers, and shipped with nothing on a
fresh database.

*Fixed:* the five definitions are now product data with external ids, loaded as **draft**
(publication stays a governance act, not a data file), and an adopting migration gives the
existing hand rows their identity **and withdraws their bogus "published" claim** — verified on
a copy of live: 5 adopted, 5 demoted, so the "published metrics" tile now honestly reads 0.
*Still open:* binding the BI figures to these definitions, and which formula wins where they
disagree, is decision D6.

---

## 3. High findings — fixed in this pass

| # | Module | Finding | Now |
|---|---|---|---|
| H1 | M25 | One failing data source aborted the whole metric bank: two packs 500'd, PDF/Excel exports failed, several tiles silently blanked | every source isolated in its own savepoint, failure logged, blanks only its own tiles |
| H2 | M25 | BI usage telemetry was silently lost whenever a metric failed | the view is logged before computing; a telemetry failure is logged, not swallowed |
| H3 | M25 | Money in BI packs printed with no currency in screen or export | money columns carry ৳; exports print the unit in the label |
| H4 | M25 | "Dashboards Live" counted drafts; "Standard Reports" counted self-listing catalogues; "Weekly Manager Usage" counted any login | each basis corrected and stated on the tile |
| H5 | M25 | Packs accepted a period and silently ignored it (a run could be stamped with a period never applied) | month-to-date anchored at the requested date; a mismatched start date is refused |
| H6 | M25 | Three of the module's own content models had no company isolation rule | rules added; the isolation generator now agrees (verified `--check`) |
| H7 | M25 | The domain module imported the portal controller, and three key validators disagreed on failure | the report library moved into the domain module; all three refuse an unknown key |
| H8 | M26 | "Override rate" counted suggestions nobody reviewed as decisions | denominator = runs with a human decision; `None` when there are none |
| H9 | M26 | AI/ML packs printed raw codes (`live_engine`, `production`, `deployed`, `untested`) | labels everywhere |
| H10 | M26 | The "named consumer + target + fallback, or not deployed" governance rule was not enforced; two deployed models declared no fallback | enforced at promotion; declarations fillable by an idempotent method; catalogue fallbacks added |
| H11 | M26 | An evaluation gate could not be recorded for any deployed version | deployed versions can be re-evaluated (evidence only) |
| H12 | M26 | The GenAI status screen was hard-coded and contradicted the provider register | derived from the register |
| H13 | M62 | All pipelines, contracts and quality rules hung off one unrelated entity; rules "passing" that were never measured; contracts "active" without signature; metrics "published" without version | guards refuse the impossible states; an explicit, logged, idempotent repair method; migration withdraws the bogus claims |
| H14 | M62 | The registry's six KPI tiles did not exist on screen | the six registry tiles, with honest bases, first in registry order |
| H15 | M62 | The hourly quality cron measured nothing (no entity mapped, no check field) | one shared "can this rule be measured" test; skips are logged and counted; a rule that cannot run never looks green |
| H16 | M62 | Retention disposition compared a free-text field to "delete" — no live policy could ever purge | a disposition selection; only `delete` deletes |
| H17 | M62 | "Catalogue & Glossary" opened a lineage report | opens the entity catalogue |
| H18 | M63 | Simultaneous approve/reject could leave an approved stamp under a rejected request | the decision takes a row lock first; the loser is refused by name |
| H19 | M63 | A request whose tasks were lost was immortal (pending forever, only the requester could end it) | the cron re-derives approvers or voids it; a recorded admin intervention closes it |
| H20 | M63 | "Keep pending" expiry was silent; group-routed approvals could never escalate | an expiry event with a consumer; escalation honours a named target |
| H21 | M63 | Two people could permanently swap approval queues | mutual delegation refused |
| H22 | M63 | One poisoned request aborted the whole hourly escalation run | per-request isolation |
| H23 | M63 | "STP share" read 75% on a database with nothing automated | both process KPIs measure the routine-work register and show "—" when it is empty |
| H24 | M63 | "Scheduled Jobs" listed 16 Airflow jobs that do not exist | the real Odoo scheduled actions |
| H25 | M63 | The delegation screen showed neither who approves nor up to what amount | threshold, approver, escalation target columns added; dead rules labelled |
| H26 | M63 | Escalations MTD counted none of the three escalation systems | counts approvals + escalated instances, basis stated |
| H27 | all | Cross-navigation and Bengali labels disagreed with the registry | aligned to the registry in all four modules |

---

## 4. Medium and low findings

Recorded in full in `scratch/a11_deep/findings/` (A1–A6) with file:line and evidence. The ones
that remain open are listed in §6, and the ones that need a business decision are in the
decisions document.

---

## 5. Cross-relations — the ERP view

The registry promises 14 links between A11 and the rest of the platform. Measured on committed
code, both ends:

| Link | Verdict | What actually happens |
|---|---|---|
| M26 → M48 predictive failure | **WIRED** | a prediction drives work only from a deployed version with a passed accuracy gate; monthly precision suspends on two bad months |
| M26 → M07 lead scoring | **WIRED** | the only model consumer that logs runs, reads back the score and degrades honestly when M26 is absent |
| M26 → M02 dispatch | partial | M02 serves its own ranking directly; no run is logged, so auto-assign and dispatcher agreement can never be measured (decision D11) |
| M63 → every module with approvals | partial | 117 document types route through the engine, but ~129 further approve actions use their own inline checks |
| M63 → M60 segregation of duties | partial | self-approval is blocked; the 63 SoD controls are never consulted (decision D9) |
| M62 → M29 access | partial | row isolation yes; no column masking rule and no SoD control covers an A11 group |
| M62 → M63 approvals | partial | M62's governance acts route through M63; no automation triggers a pipeline |
| M25 → M62 semantic layer | missing → **documented, awaiting D6** | definitions now ship and are adopted; no consumer registered yet |
| M25 → M26 model outputs | missing | BI displays no model output |
| M25 → analytics portal (P06) | missing | the portal uses the data-platform API + Superset; BI's embed machinery has no consumer |
| M25 → M54 FP&A | missing | FP&A reads the ledgers directly |
| M26 → M43 demand forecast | missing | both sides fail closed; nothing connects |
| M26 → M32 conversational AI | missing | neither side knows about the other |

Event bus: A11 publishes 7 event types; 5 have consumers (approval notifications, quality
incidents, model suspension). Nothing in A11 consumes a business event from another area —
`journal.posted` (34 events on live) has no consumer at all (recorded as an observation).

---

## 6. Owner decisions actioned (2026-11-23, after the deploy)

The owner answered four of the 23 decisions. What was executed, and what was deliberately
NOT faked:

**Live restart hazard — CLOSED (owner: "run the consistency upgrade now").** The live estate was
running a registry older than the code: **14 modules** had been committed by other sessions but
not deployed, and `cd_attendance` declared a `res.company` field the live database did not have.
A throw-away server against a copy of live proved the consequence — every company read failed
with `column res_company.fix_attendance_exception_escalate_days does not exist` — so the next
restart of 8069 would have broken the web client. One `-u` pass over those 14 modules: **drift is
now 0**, the column exists, and a fresh registry loads and logs in. Backup taken first (50 MB).
*(During the window another session began its own upgrade; Odoo refused both with a
serialization error and mine rolled back cleanly — nothing half-applied. Live was briefly down
while its watchdog was suspended and was restored in 15 seconds.)*

**D8 delegation of authority — 51 ladders STAGED AND PROPOSED.** One ladder per governed document
type, carrying exactly the bands each model applies today (176 bands across 53 types), so ruling
them changes no behaviour. They were **proposed** as admin (a genuine Tier 4 holder) naming
**Md. Rizwanul Hoque Chowdhury** (Tier 5, the MD) as countersigner, with the owner's decision as
the cited authority. They are **not in force**: the module's own control is two acts by two
different people, and faking the countersignature would recreate exactly the forgeability an
earlier audit removed. **One action remains: the MD's countersignature per ladder** (the module
offers it per record; a bulk "countersign all pending" action is a small follow-up if wanted).

**D7 governance appointments — ALL TEN GROUPS STAFFED.** Each group now holds admin plus two
named people drawn from the roles they already hold:
DoA Administrator = Ashish Kumar Mazumder (CFO, Tier 4) + Md Mainul Hasan ·
BI Author = Md Mainul Hasan + Md. Tanjin Ahmed Rabby ·
BI Certifier = Ashish Kumar Mazumder + Md. Rizwanul Hoque Chowdhury ·
BI Company-Wide Reader = Ashish Kumar Mazumder + Md. Rizwanul Hoque Chowdhury ·
BI Finance Reader = all three finance holders ·
BI Sync Operator = Md. Tanjin Ahmed Rabby + Md Mainul Hasan ·
Data Governance Officer = Md. Tanvir Mahmood (IT security) + Ashish Kumar Mazumder ·
ML Data Scientist = Md. Tanvir Mahmood + Md. Tanjin Ahmed Rabby ·
ML Evaluation Reviewer = Ashish Kumar Mazumder + Md. Tanvir Mahmood ·
ML Model Owner = Md. Tanvir Mahmood + Md. Rizwanul Hoque Chowdhury.
*Caveat recorded:* this database has no identifiable "BI / strategy lead" or "ML analyst" user, so
those groups are staffed from the finance and IT-security authorities. Every appointment is
reversible one group at a time.

**D10 AI/ML governance — BARS, OWNERS, GUARD-RAILS, HONEST BIAS TESTS.**
- Bars: dispatch scoring **6 months / 5,000 orders**, lead scoring **12 months / 2,000 leads**;
  promotion is provably unblocked — a data-sufficiency gate now records
  *"bars 6 months / 5000 records, observed 12/9000 → met"* where it previously refused with
  *"declares no minimum history or volume"*. The other five models keep NULL bars deliberately:
  their numbers are the owner's next input, not mine to invent.
- Owner + annual review on **all 7** models (Md. Tanvir Mahmood, review 2027-11-23).
- Two guard-rails, active, both **flag-only** (no blocking): dispatch `score < 30` → dispatcher
  decides; lead scoring `score < 40` → shown unscored, qualified by hand.
- Bias tests: the model offered only *passed*/*failed*, which would have forced a claim nobody
  measured. Added an honest third state (**"not evaluable — no scored ground truth yet"**, code
  `60eeba88`, three tests) and recorded one per people-affecting model. The Fairness Summary now
  reads **0 passed / 0 failed / 4 untested / 2 not evaluable** with the reason stated.

## 7. Deployment — both estates, 2026-11-23

| Step | `fix_real` (8069, LIVE) | `fix_dev` (8090, reference) |
|---|---|---|
| Backup before touching anything | 50 MB dump | 47 MB dump |
| Modules upgraded | cd_workflow_engine 19.0.1.2.0 · cd_metric_registry 19.0.0.4.0 · cd_ml_services 19.0.0.4.2 · cd_bi_reporting 19.0.0.4.1 · cd_p03_portal 19.0.1.5.2 | same |
| Upgrade log | 0 CRITICAL / 0 Traceback | 0 CRITICAL / 0 Traceback |
| Automation register | 52 active · 23 cron / 21 method / 8 consumer / 8 manual · 20 implemented / 32 partial / 8 planned / **0 broken** · gap report 0 | same (plus the reference estate's 7 non-catalogue rows, all inactive) |
| Seed-residue repair | 3 unsigned contracts → draft · **4 fake "last success" stamps cleared** · 3 unmeasured rules → untested · 2 rules re-pointed · 1 check field set · 3 entities modelled + 3 created · 4 pipelines and 3 contracts re-pointed · 4 retention dispositions derived | same, plus 3 contracts and 3 entities from its own residue |
| Metric definitions | 5 present, 5 draft, **0 published** (the bogus claims withdrawn), 0 consumers | same |
| Behaviour after deploy (API) | AR Outstanding **৳15,38,59,759.09** · automation rate / STP share **null ("—")** · six data-platform registry tiles present | AR Outstanding **৳52,125,362.62** with a **৳361,841.61** ledger difference surfaced |
| Behaviour after deploy (in-app browser) | CFO cockpit shows ৳15,38,59,759.09 with its basis caption · Workflow Definitions shows Engine / Binding = Verified / Coverage = Partial · Delegation grid shows Threshold ৳10,000 and Approver Role · Scheduled Jobs lists the real Odoo crons with Dhaka timestamps · data-platform home shows the six registry tiles with honest captions | screens render; API identical |

Known and accepted at deploy time: the shared working tree carried other sessions' uncommitted
files; all were syntax-validated before the restart, and the upgrade touched only the five A11
modules. Two watchdogs were suspended for the window and restored afterwards (one duplicate
killed); the 8069 and 8090 listeners were verified back at HTTP 200 within seconds.

## 8. What is still open after this pass

**Needs your decision** (23 items, `A11_ERP_AUDIT_DECISIONS_2026-11-23.md`). The ones that
block go-live: appointments to the ten governance groups (D7), the delegation-of-authority
schedule (D8, with the 53-document annex), retention floors (D13), masking scope (D14), the
AI/ML governance pack (D10), and whether dispatch scoring goes through the AI/ML gateway (D11).

**Engineering backlog, no decision needed:** BI drill-down and report-run filing (D20 in the
decision list because it is prioritisation), the `fix.workflow.instance` shell (D3), the
`fix.business.rule` prose repository (D4), pipeline execution (D5), a full metric service (D6).

**Deliberately not touched:** the three dead delegation matrix rows and the two `seed_role` rows
(re-pointing them would change live approval routing — D8); the "14 models" title (D10); the
`docs/traceability/aut-60-...md` report, which already carries a provenance warning and is
superseded by this audit's measurements.

---

## 9. How to re-verify (for the next session)
1. `python scratch/a11_deep/verify_aut_catalogue.py --db fix_real` → expect **UNRESOLVED: 0**.
2. `/p03/workflow/kpis` → `automations` counts implemented rows only; `automation_rate` and
   `stp_share` are null while the routine-work register is empty.
3. `/p03/bi/kpis` and the CFO cockpit → AR total equals the GL receivable control balance; the
   finance pack's "Difference (AR total − GL)" is 0.00.
4. `/p03/dataops/kpis` → the six registry tiles exist and `certified_metrics` is 0 until a
   definition is published through governance.
5. The suites: `FIX_TEST_DB=<private copy> pytest addons/domain/j_data_analytics
   addons/domain/i_governance/cd_workflow_engine/tests` plus the 17 portal A11 files.

---

## 10. A note on process (recorded because it affected the work)

A parallel session repeatedly committed the shared working tree with `git commit -a` and once
restored it wholesale (`git restore`), which reverted **all** uncommitted changes — including
work built over two hours. Recovery was possible because every builder kept evidence outside the
tree and could re-apply from its own record; `git status` was misleading for about twenty minutes
because the other session's index was stale (a file can differ from HEAD and still show clean).
The rule adopted: verify by content hash, never by status alone, and commit each unit as soon as
it is verified.

---

*Measurements in this report were produced by the commands and probes recorded in
`scratch/a11_deep/`; nothing here is asserted without an artefact behind it.*
