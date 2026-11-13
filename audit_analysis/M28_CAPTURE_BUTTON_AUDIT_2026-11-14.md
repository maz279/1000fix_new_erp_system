# M28 Integration, API & Events: sub-module capture audit

**Date:** 14 Nov 2026
**Scope:** the 8 Function Register sub-module pages of the M28 workspace. For each page:
- does it have a "+ New" button;
- does that button capture the record the page is about;
- does its form panel list every record the page covers.

**Status:** fixed and live on 8069 (`fix_real`) after a user-approved restart at 04:48. Production bundle `0010718`.

## What M28 is supposed to capture

The authority is `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md` §5 (FR-IPF-001..057), plus the business rules in §9. The Function Register (`contracts/nav/registry.json`) gives only the 8 sub-module names and their function counts. Each page was therefore mapped to its §5 section:

| # | Sub-module | Spec section | What a person records there |
|---|---|---|---|
| 1 | Gateway | 5.1 API Gateway & Traffic Management | Per-consumer rate limits and quotas (FR-IPF-004) |
| 2 | Versioning & Portals | 5.2 API Lifecycle & Governance | API registry entry or version (FR-IPF-011/013); consumer registration (FR-IPF-016) |
| 3 | Outbox & Event Bus | 5.3 Domain Event Platform | Event topic; schema registry entry (FR-IPF-025) |
| 4 | Subscriptions & DLQ | 5.3 Domain Event Platform | Subscription (FR-IPF-026). Dead letters are raised by the engine and replayed or discarded by action (FR-IPF-029/030). |
| 5 | Webhooks | 5.4 Webhooks | Outbound webhook registration (FR-IPF-034); the allowed host it must sit on |
| 6 | Connector Framework (47) | 5.5 External Connectors, Credentials & Resilience | Connector (FR-IPF-039/040/043); vault credential reference (FR-IPF-041) |
| 7 | Offline Sync | 5.6 Offline Synchronisation | The DECISION on a conflict the engine raised (FR-IPF-049, BRU-IPF-17). Nobody types a conflict. |
| 8 | Reconciliation | 5.7 Portal Contract, Reconciliation & Observability | The INVESTIGATION of a divergence ("investigated, never absorbed", BRU-IPF-19); a time-boxed alert suppression |

## What the code did (proved on the code before the fix)

The proof is `test_m28_capture_buttons.py`. It runs the engine's own `fregCreate`/`fregPanels` in node over the real registry, and 16 of its 22 checks failed before the fix.

| # | Before | Defect |
|---|---|---|
| 1 | + New API Endpoint (the module button) | Same button as page 2. The gateway's own record, the rate limit, could not be captured from it. |
| 2 | + API Endpoint | OK. The endpoint form was missing from its forms panel. |
| 3 | + New Event Topic | OK. Topic and schema forms were missing from its forms panel. |
| 4 | **No button** | Both of its lists are engine-fed dead letters (create: false), so the page offered nothing, although its own form chip was Event Subscription. |
| 5 | + New Event Subscription | OK. Allowed Hosts (a webhook cannot go live without one) was on no sub-module page. |
| 6 | + New Connector | OK. Connector Credentials list was on no sub-module page. |
| 7 | **No button** | Conflicts are engine-raised, and deciding one was only possible from four row buttons on another list. |
| 8 | **No button, wrong records** | The page listed **offline sync conflicts** (`fix.sync.conflict`). The reconciliation runs, the suppressions and the investigation were on no sub-module page. |

The Reconciliation Runs and Reconciliation Suppressions screens, which hold the nightly results, also sat on no sub-module page.

## What was changed

| # | Now | How |
|---|---|---|
| 1 | **+ New API Rate Limit**. Lists rate limits. | `create: 'M28-form-quota'`. The form was retitled "API Rate Limit". |
| 2 | + API Endpoint, plus chips API Endpoint and API Consumer | Grid columns now show lifecycle and sunset date. |
| 3 | + New Event Topic, plus chips Event Topic and Event Schema | |
| 4 | **+ New Event Subscription** | `create: 'M28-form-subscription'`. The Webhook Subscriptions list was added to the page. |
| 5 | + New Event Subscription, plus chips Event Subscription and Allowed Host | The Allowed Hosts list was added to the page. |
| 6 | + New Connector, plus chips Connector and Connector Credential | The Connector Credentials list was added to the page. |
| 7 | **+ Decide a Sync Conflict** | A new pick form, `M28-form-conflict-resolve`. Step 1: pick a pending conflict, shown with its field class. Step 2: choose Local Wins, Remote Wins, Manually Merged or Closed, Nothing Applied, and add a note. It saves through the new `fix.sync.conflict.action_resolve_decision`, which calls the same `_resolve` as the row buttons, so all their checks still apply: Integration Admin group, BRU-IPF-17 field class, note rules and audit row. |
| 8 | **+ Record a Reconciliation Investigation**, plus chips Reconciliation Investigation and Reconciliation Suppression. Lists reconciliation runs. | A new pick form, `M28-form-recon-investigation`. It offers only divergent or suppressed runs with no investigation yet, and saves through the existing `action_resolve`. |

The two decision forms send their inputs to a workflow method, never to `/p03/model/write`: the write whitelist still refuses `resolution`, `resolution_note` and `state`.

**Files:**
- `addons/platform/cd_p03_portal/static/src/a12/m28.js`
- `addons/platform/cd_p03_portal/controllers/a12/m28.py`: serves `action_resolve_decision`.
- `addons/domain/i_governance/cd_itsm/models/fix_integration.py`: `SYNC_DECISIONS` and `action_resolve_decision`.

## Evidence

**Guard (node, registry as the browser reads it):** `cd_p03_portal/tests/test_m28_capture_buttons.py`. 22 checks: 16 failed before the fix, 22/22 pass after.

**Live endpoint tests (non-admin users, fix_test):** `cd_itsm/tests/test_m28_capture_live.py`, 11/11 pass. They check that:
- an Integration Admin decides a client-field conflict, the device value is applied, and the decision is audited;
- "pending" is refused, and a server-class field accepts only Remote Wins;
- merge and close need a note;
- a plain user is refused, and a typed decision through the generic write is refused;
- an investigation is recorded and audited, needs a note and an open divergence, and a plain user is refused;
- the Gateway form saves a rate limit.

**Existing suites:** all M28 suites plus the estate page standard give 803 passed and 9 failed.
- The two sweep tests in `test_a12f_m28_finish.py` were taught about decision forms. Inputs a decision form sends to its method must NOT be on the write whitelist, and a decision form's button method must be served.
- The 9 failures are the dead-letter/relay tests (`m28_3` paused topic, `m28_4`, `m28_5`, `m28_6` ×5, `y05`). They fail identically with the HEAD versions of the changed Python files, so they are not caused by this change. fix_test carries a large pending-outbox backlog, which the M27 audit also recorded.

**Live UI on 8069:**
- First checked from disk under `?debug=assets`, then after the restart from the production bundle `0010718`.
- All 8 pages show the buttons and chips above.
- The investigation and sync-decision pick steps open and show their empty messages: fix_real has 0 sync conflicts and 25 reconciliation runs, all clean or not run.
- The rate-limit form opens with Consumer, Endpoint, Requests per minute and Daily Quota.
- `action_resolve_decision` passes the server's action whitelist.
- No record was saved on fix_real.

**Deploy:**
- A schema-drift check of the disk code against fix_real found 0 missing tables or columns.
- 8069 was stopped and relaunched with its existing command line. No supervisor was running.
- HTTP 200 came back in about 5 s, with no registry errors.
- The restart also published another session's uncommitted M34 edits (methods only, no new columns); the user was told before approving.

## Gaps left (no model, or an owner decision)

- **Inbound webhooks (FR-IPF-037/038)** and **batch/file exchange (FR-IPF-045)**: no model exists.
- **Fallback register (FR-IPF-043, BRU-IPF-12)**: only a fallback-connector field exists, and it is a record that switches nothing.
- **Sync device state and command journal (`fix.sync.state`, `fix.sync.command`)**: no models exist. Conflicts come from `fix.offline.idempotency.ledger`.

These are spec gaps, not missing buttons. Each needs a build decision.

- **People:** Integration Admin is held by `admin` and one named user on fix_real. Every M28 decision and every second-admin approval needs that group. With one real holder, a request that needs a second Integration Admin cannot be decided by anyone but the system administrator.
