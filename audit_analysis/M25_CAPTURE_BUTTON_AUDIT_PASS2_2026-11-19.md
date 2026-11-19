# M25 Business Intelligence: second data-capture audit

**Date:** 19 Nov 2026 · **Estate:** fix_real on port 8069 (fix_dev on 8090)
**Branch:** `fix/m25-capture-pass2` (worktree `1000 fix/m25cap2-wt`), cut from shared `a6ca660a`
**Status:** see §6.

## 1. The question

The user again saw M25 sub-module pages without a relevant capture button. This follows the [14 Nov audit](M25_CAPTURE_BUTTON_AUDIT_2026-11-14.md), which gave all seven pages a "+ New". This pass asks a narrower question: **does each page capture the record the spec names for it?**

Sources:
- `1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M25_Business_Intelligence_and_Reporting.md`:
  - FR-BID-001…034
  - §8.1 content lifecycle and §8.2 retirement
  - §9 rules, §10 entities, §11 automations, §13 SoD
- The 14 Nov report's own "not built" list (§6 there)

## 2. Page by page: spec vs code before this pass

| # | Page | Spec record (§5 / §10) | What the page captured on 14 Nov | Gap |
|---|---|---|---|---|
| 1 | Role Dashboards | `fix.dashboard` with `business_owner_id`, tier, review cycle; `fix.annotation` (FR-BID-009) | + Dashboard | **No annotation** anywhere. The dashboard had no **business owner** (BRU-BID-07 H) and no "decision it supports" (§8.1 Requested → In Build). Nothing recorded the steward's **verification** of definition, scope and Bengali rendering before certification (§8.1 In Review → Certified; BRU-BID-10 H). A dashboard went from draft straight to a certification request. |
| 2 | Standard Report Library | `fix.report.definition` (owner, definition, certification); `fix.report.run` (as-of, metric versions, restatement flag) | + New Distribution Schedule | The library had **no owner, no definition and no certification** per report (FR-BID-011). A generated report was **stamped nowhere**, so it could not be reproduced (FR-BID-017, BRU-BID-08 H). Nothing could flag a run as restated (BRU-BID-09 H). |
| 3 | Self-Service | `fix.exploration` (personal / shared workspace, metric codes) | + Dashboard | There was **no saved exploration** (FR-BID-018), so personal work could not be kept apart from published content (FR-BID-019). |
| 4 | Distribution & Alerting | `fix.alert.instance` (raised, routed, acknowledged, escalated) | + New Distribution Schedule, Alert chip | An alert only stamped `last_fired_at`. **Nothing was raised, routed for acknowledgement, suppressed or escalated** (FR-BID-025/026, T-14, BRU-BID-14). |
| 5 | Embedded Analytics | `fix.embedded.surface` (host screen, context binding, audience, token TTL); signed tokens (T-08) | + New Sync Connection | The page captured the dataset connection, **not the chart placement**. There were **no signed, short-lived, single-use tokens** (BRU-BID-12 H) and no portal own-data binding (BRU-BID-18 H). |
| 6 | Mobile | Low-bandwidth delivery (FR-BID-028) | + Dashboard | No channel other than an e-mail with an attachment. |
| 7 | Lifecycle & Usage | `fix.content.usage` (FR-BID-033); `fix.manual.pack` | + Register a Manual Pack | **No usage telemetry**: the role cockpits said so themselves ("have no model yet"). The register itself was fine. |

## 3. What was built

`cd_bi_reporting` 19.0.0.4.0. The new file is `models/fix_bi_capture.py`, imported last.

| # | Page | Capture now | Rules enforced (server side) |
|---|---|---|---|
| 1 | Role Dashboards | **+ Dashboard** (now a 3-tab form: Definition / Ownership & Review / Verification & Certification), **Annotation** chip and list | <ul><li>The business owner is not the author.</li><li>Requesting or deciding certification needs the business owner, the decision it supports, and the steward's verification.</li><li>**Verify Content**: only in review; by a BI Data Steward who is not the author, and by the *named* steward when that employee has a user; a written note is required.</li><li>Editing name, role, description or layout voids the verification.</li><li>Verification fields cannot be typed.</li><li>Annotation: written by a BI author or steward; on a dashboard with a business owner, by that owner (or a steward). Its role must match the dashboard's. The metric must come from the measured bank. It shows in the cockpit's notes for its audience, and is withdrawn by unticking Visible.</li></ul> |
| 2 | Standard Report Library | **+ New Report Definition** (primary), Distribution Schedule chip, **Report Definitions** and **Report Runs** lists. The library pack shows **Business Owner** and **Certification**. | <ul><li>The key must be a library pack, registered once per company.</li><li>Born draft. **Certify**: a steward who neither registered nor owns the report. Changing the definition reverts it to draft.</li><li>**Generate Run** renders the pack *as the caller*, so the finance pack still needs BI Finance Reader. It stamps requester, as-of time, period, parameters, scope, rows, duration, the definition's certification and its version.</li><li>Runs are append-only.</li><li>**Flag Restatement** is a steward act and needs the M62/M19 reference.</li></ul> |
| 3 | Self-Service | **+ New Exploration** (primary), Dashboard chip | <ul><li>Metrics come only from the measured bank (no metric is redefined).</li><li>Born **personal**: a record rule hides it from other analysts until **Share**; the steward sees all.</li><li>Only the author edits, shares or promotes it.</li><li>**Run Question** answers it in the caller's scope.</li><li>**Promote to Dashboard** builds a *draft* dashboard, which then goes through review, verification and certification (BRU-BID-06). A promoted exploration is closed.</li></ul> |
| 4 | Distribution & Alerting | + New Distribution Schedule, Alert chip (threshold owner, suppression window, escalation after / to), **Raised Alerts** list | <ul><li>The hourly evaluator raises an alert on a crossing.</li><li>A repeat while one is live, or inside the suppression window, adds to it (`repeat_count`, T-14).</li><li>An unmeasurable metric raises nothing.</li><li>**Acknowledge**: the routed recipients, the threshold owner or the escalation contact.</li><li>**Close**: only after acknowledgement, with a reason. An *acknowledged* alert also closes on recovery; an unacknowledged one waits.</li><li>The new hourly cron **escalates** unacknowledged alerts after the window, with an activity for the escalation contact.</li><li>Raised alerts cannot be typed.</li></ul> |
| 5 | Embedded Analytics | **+ New Embedded Surface** (primary), Sync Connection chip | <ul><li>Host module is M01–M69 or P01–P07.</li><li>Token lifetime is 30–900 s.</li><li>A portal audience must bind to the viewing party (BRU-BID-18).</li><li>**Activate**: a steward who is not the author. Active surfaces are not edited.</li><li>Route `/p03/bi/embed/token` issues an HMAC-signed token bound to surface, viewer and context. Redeeming it checks signature, viewer, expiry and a single-use ledger (`fix.bi.embed.token`).</li><li>The viewer must be in the audience (internal group, or a portal partner).</li></ul> |
| 6 | Mobile | **+ New Low-Bandwidth Summary** (the page lists only low-bandwidth schedules, and its form starts with that channel) | Schedule `channel` = e-mail with attachment, or low-bandwidth text summary: no attachment, the first 10 rows as text, and a count of the rest. Logged as format `text`. |
| 7 | Lifecycle & Usage | + Register a Manual Pack (unchanged), **Content Usage** list | Each `/p03/bi/role` view writes a usage row: user, company, cockpit and device class from the user agent. A telemetry failure never blocks the cockpit. Usage is append-only, and only stewards (and system) read it. |

The other pieces:

- **ACL** – 22 new rows.
- **Record rules** – two exploration rules (personal / steward) and generated company rules for the 7 new company-scoped models.
- **Cron** – *M25: BI alert escalation* (hourly).
- **Controller `a11/m25.py`**:
  - 7 surfaces
  - `action_steward_verify` served
  - `report_library` gains owner and certification columns
  - `bi_role` appends annotations and logs usage; the route is no longer `readonly`, because a view writes its usage row
  - new `bi_embed_token` route
- **Fragment `a11/m25.js`**:
  - 7 new screens, 4 new forms; all reachable from the navigation groups
  - page maps, chips and choices; the metric and role choices equal the server's
  - the dashboard form is tabbed (17 fields, more than the 15-field limit)

## 4. Evidence

All runs were on the private clone `fix_test_m25c2`, a copy of the M19 pass-2 DB upgraded to this branch: `-u` of the 10 lagging modules, `cd_bi_reporting` and `cd_p03_portal`. Every check ran as a non-admin user unless noted.

**Model tests:** `cd_bi_reporting/tests/test_m25_capture_pass2.py`, 37 tests.
- Each rule is checked both ways.
- The cd_bi_reporting suite runs **77/77** (governance 20, sync 5, manual pack 15, pass 2 37).
- The 14 Nov tests that certified a dashboard straight from draft now go through the business owner, Submit for Review and Verify Content.

**Page guard:** `cd_p03_portal/tests/test_m25_capture_pass2.py`, 22 tests.
- node runs the engine's own `fregCreate` / `fregPanels` over the real registry.
- It checks each page's new register, the primary buttons, and page 6's filter and preset.
- System-written lists offer no "+ New".
- Every action is served with its asks.
- The metric and role choices equal the server's.
- A form over 15 fields is tabbed.
- No form omits a required field that has no default.
- Endpoint round trips through `/p03/model/write` and `/p03/model/action`, plus the BI routes:
  - verification before certification, and the annotation showing in the cockpit
  - library certification, run and restatement, and the library columns
  - an exploration run and promoted
  - an alert acknowledged by its recipient and refused to a stranger
  - a surface activated, then its token issued and redeemed
  - a low-bandwidth summary saved
  - a cockpit view logged as `mobile` and hidden from a plain user

`test_m25_capture_buttons.py` follows the new captures. Its field check now also reads `_inherit` classes.

**Mutation:** 36 mutants over the model, controller and fragment. **36/36 red.** The first run left 2 survivors, both guards that the ACL also enforces. Tests now drive them with a system administrator who passes the ACL but holds no BI role.

**Regression:**
- The full `cd_p03_portal` suite ran: **6,101 tests, 2 failures, both caused by this change and fixed:**
  - the A03 control suite expects the routed-approval refusal first, so `_approval_assert_routed()` now runs before the content checks;
  - `test_all_submodule_mapping` parses `domain:` only as the last key of a page map, so the key moved.
- Final rerun: cd_bi_reporting, every M25 suite, the A11 M25 control suite, `test_all_submodule_mapping` and the A03 control suite: **420 tests, 0 failures** (184 environment skips).

**Lint:** ruff 0.8.4 check and format are clean, and `node --check` passes.

**Live walk:** private server on `127.0.0.1:8125`, worktree code on `fix_test_m25c2`, headless Chromium, signed in as the dev admin. **0 console errors.**

| # | Primary button | Chips |
|---|---|---|
| 1 | + Dashboard (3 tabs: Definition 6 · Ownership & Review 5 · Verification & Certification 6) | Dashboard, Annotation |
| 2 | + New Report Definition | Report Definition, Distribution Schedule |
| 3 | + New Exploration | Exploration, Dashboard |
| 4 | + New Distribution Schedule (channel defaults to e-mail) | Distribution Schedule, Alert Subscription |
| 5 | + New Embedded Surface | Embedded Surface, Sync Connection |
| 6 | + New Low-Bandwidth Summary (form opens with `channel = low_bandwidth`) | Distribution Schedule, Dashboard |
| 7 | + Register a Manual Pack | Manual Pack, Dashboard |

- The library page's grid shows the new columns **Business Owner** and **Certification**.
- **Two real saves through the forms:**
  - an exploration on page 3, with both metrics chosen through the picker popup; it was stored `personal`, `in_repair` + `sla_overdue`;
  - a low-bandwidth summary on page 6; it was stored with `channel = low_bandwidth`.

## 5. Not built: needs an owner decision or a model

| Gap | Spec | Why |
|---|---|---|
| Nobody can verify, certify, activate or reconcile on fix_real | §13 | All five BI groups are still held by **admin only** (checked 19 Nov). Every steward act needs a steward who is not the author, so nothing can complete. This needs an owner appointment. |
| Bursting by scope | FR-BID-024, T-10 | The packs read the caller's company scope and take no branch parameter. Bursting per branch needs a scoped pack API first. |
| Periodic review, deprecation and notice period | §8.1, BRU-BID-15, AUT-BID-10/11 | Usage is now recorded, so the review cycle has its evidence. The Under Review / Deprecated states and the auto-deprecation cron are not built. |
| Restatement and definition-change events from M62 | AUT-BID-04/05 | Restatement is flagged by a steward with the reference. M62 publishes no event that M25 subscribes to. |
| Host screens rendering embedded charts | FR-BID-029…032 | The placement, the token issue and the redemption are built. No host screen calls the route yet. |
| Report runs filed in M24 | FR-BID-016, AUT-BID-09 | `retention_to_m24` is recorded on the definition. Filing is not wired. |
| Alert notification transport | FR-BID-025 | In-app only: the escalation activity, and the Raised Alerts list as the routed person's inbox. E-mail and SMS transport stay porting phase, as the alert model already says. |
| p95 load time | KPI | Still never invented. |

## 6. State

- **Committed** on `fix/m25-capture-pass2`, rebased on the shared branch and landed on `fix/a03-live-data-and-pending-work`. Both branches pushed (see the commit log).
- **Not yet deployed.** The deploy needs `-u cd_bi_reporting,cd_p03_portal` on fix_real and fix_dev, and a restart: `SURFACES`, the `/p03/bi/role` route and the new `/p03/bi/embed/token` route are controller code.
- On 19 Nov the M22 session holds the single 8069/8090 restart until the version gap is closed. The gap is `cd_contact_centre` (M27), `cd_qms_process` (M23) and, on fix_real, `cd_ml_services` (M26). The M25 upgrade joins that wave once the owner approves it.
- Private clone `fix_test_m25c2` and worktree `m25cap2-wt` are kept until the live check.
