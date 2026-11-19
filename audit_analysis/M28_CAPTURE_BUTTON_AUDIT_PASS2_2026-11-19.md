# M28 Integration, API & Events: sub-module capture audit, pass 2

**Date:** 19 Nov 2026
**Scope:** the 8 Function Register sub-module pages of the M28 workspace. Pass 1 (14 Nov, `M28_CAPTURE_BUTTON_AUDIT_2026-11-14.md`) gave every page a "+ New". This pass asks a different question: **can each page capture the records the spec says belong to it?** Every page was read against M28 §5 (FR-IPF-001..057), §9 (business rules) and §10 (owned entities). Buttons were not counted.

**Status:** see "State" at the end.

## What each page must capture, and what it could

| # | Page | Spec | Before this pass | Gap |
|---|---|---|---|---|
| 1 | Gateway | 5.1: per-consumer rate limit (FR-IPF-004) | + New API Rate Limit | none |
| 2 | Versioning & Portals | 5.2: API registry (011/013); consumer registration **and scoped credentials per environment, with rotation and revocation** (FR-IPF-016, entity `fix.api.credential`) | + API Endpoint; chips Endpoint, Consumer | A consumer held **one** key reference: no environment, no expiry, **no revocation**. A production key and a sandbox key could not both exist. |
| 3 | Outbox & Event Bus | 5.3: topic, schema registry (025) | + New Event Topic; chips Topic, Schema | none |
| 4 | Subscriptions & DLQ | 5.3: **subscription management: which consumer receives which event, discoverable** (026); dead-letter triage (030); **consumer replay from a point in time** (031) | + New Event Subscription: **the Webhooks page's form** | The in-process subscriptions (`fix.event.consumer`; **191 on fix_real**) were on no screen. Replay had a method (`action_backfill`) with no screen, no approval and no audit, and it re-released events to every consumer, not just one. |
| 5 | Webhooks | 5.4: outbound registration (034); **inbound receiver with signature verification, replay protection and idempotent ingestion (037), routed to the owning module (038)**. Both are P0. | + New Event Subscription; chips Subscription, Allowed Host | No inbound webhook could be registered, and nothing received one. |
| 6 | Connector Framework (47) | 5.5: connector (039); **pattern declaration (040, BRU-IPF-13 H)**; credentials (041); **automatic fallback (043): a registered, tested fallback, without which a P0 integration cannot go to production (BRU-IPF-12 H)**; **batch and file exchange (045)**; the integration register's owner, priority and INT id (055) | + New Connector; chips Connector, Credential | A connector declared no pattern, priority or owner. The "fallback" was one Many2one: no type, no message to users, no test. So "tested" could not be shown, and a P0 connector went live without one. There was no batch file record at all. All 8 connectors on fix_real (6 live) show pattern "—" and priority "—". |
| 7 | Offline Sync | 5.6: the decision on a conflict (049) | + Decide a Sync Conflict | none. The device state and command journal (`fix.sync.state`/`command`) are engine records, not captures. |
| 8 | Reconciliation | 5.7: investigation (BRU-IPF-19); suppression | + Record a Reconciliation Investigation; chips Investigation, Suppression | none |

## What was built

All in `cd_itsm` 19.0.0.2.0, `models/fix_integration_capture.py` (imported last, after `fix_integration`). Every decision is an Integration Admin's, and every privileged act writes a security-audit row, as elsewhere in M28.

| Page | Record | Rules it enforces |
|---|---|---|
| 2 | `fix.api.credential` (**+ API Credential** chip, API Credentials list) | One live credential per consumer and environment. A production credential needs a registered consumer; sandbox and staging may come first. The client id is issued by the server. The secret is a vault:// reference only. **Rotate** issues the next vault version and revokes the old credential in one step. **Revoke** needs a reason. An issued credential's consumer, environment and secret reference cannot be changed. |
| 4 | `fix.event.consumer.replay` (**+ Request a Consumer Replay**, the page's own button); **In-Process Subscriptions** list (read-only) | Saving creates a request. **Request Replay** routes it to a second Integration Admin, and on approval the window is re-delivered **to that subscription only**. The other consumers are untouched (FR-IPF-031); this is proved by a test with two consumers on one event type. The window must start in the past and must contain events. It is capped by `fix.integration.replay_max_events` (5000). A replay runs once. Delivered and failed counts are recorded and audited. |
| 5 | `fix.webhook.inbound.source` (**Inbound Webhook Source** chip) + `fix.webhook.inbound.event` (receipt log, read-only) + receiver **`POST /hooks/v1/inbound/<code>`** | A new source receives nothing until a second Integration Admin takes it live. Changing the code, secret, route key or owning module takes it out again. The receiver checks the source is active, the secret value is present (`FIX_VAULT_<PATH>`), the HMAC-SHA256 signature (the same Standard Webhooks scheme the outbound dispatcher signs with), the timestamp against the replay window, and that the body is a JSON object. A verified post becomes ONE `integration.webhook_received` event carrying the owning module and route key; its content is not interpreted (FR-IPF-038). A repeated message id gets the first answer. Every refusal is recorded with its reason, except an unknown code, which gets the same 401 as a bad signature. |
| 6 | `fix.connector` register fields (pattern, priority, owner, INT id) on the Connector form and list | **Go-live gate:** request and approval both refuse a connector with no pattern (BRU-IPF-13) or no priority. A **P0** connector also needs an active fallback whose **latest** test passed (BRU-IPF-12). The approval re-checks, so a failed test recorded after the request stops the go-live. Lowering an approved connector's priority voids the approval. |
| 6 | `fix.integration.fallback` (**Integration Fallback** chip) | Type: alternate provider, cached, queued or manual. An alternate names a connector of the same type. A procedure and a message to affected users in English and Bangla (FR-IPF-043) are required. Once tested, what the test proved cannot change. |
| 6 | `fix.integration.fallback.test` (**Fallback Test** chip) | Evidence, so it is never edited or deleted; a re-test is a new row. It cannot be dated in the future. It is stamped with who recorded it. |
| 6 | `fix.integration.batch.run` (**Batch File Run** chip) | The integration must declare the Batch File pattern. The file is uploaded and its SHA-256 recorded. Declared records and control total are captured. **Verify** is a second Integration Admin entering the counts they made: a mismatch is refused, and the run must then be rejected with its reason (AUT-IPF-20). A recorded file and its totals never change; a corrected file is a new run. |

**Workspace:** a "Registers & Exchange" navigation group holds the 8 new lists. Pages 2, 4, 5 and 6 list their new screens and chips. Page 4's grid now shows consumer replays, so a replay made there lands there.
**Controller:** `cd_p03_portal/controllers/a12/m28.py` serves the 8 models and their row actions. `WRITABLE` holds only the fields the forms offer as editable. Client ids, issue/revoke/replay/verify stamps, receipts and the in-process subscriptions are never typed.
**Also:** company record rules for the 7 new models (regenerated by `generate-isolation-rules.py`), 7 ACL rows, the BFX sequence, and the event contract `contracts/events/integration_webhook_received.json`.

### Not built (owner or infrastructure)

- **Automatic fallback switching (FR-IPF-043 "detect an outage and switch").** Traffic still does not flow through the connector register, so a fallback is engaged by the people its procedure names. The register, the test evidence and the go-live gate are what the spec's hard rule (BRU-IPF-12) needs; the switch needs a gateway.
- **SFTP or signed file drop (FR-IPF-045).** None is attached. The batch run records a file that was exchanged, by whatever means.
- **Credentials do not authenticate calls yet.** The API edge still recognises a consumer by its linked partner (pass 1). `fix.api.credential` is the register of what was issued and revoked. Wiring the edge to it is a gateway change.
- **Owning-module consumers of `integration.webhook_received`.** Each module that takes inbound webhooks (M20 for bKash/Nagad, for example) registers its own `consume_*` for its route key.
- **No connector on fix_real declares a pattern or priority yet.** This is owner data (which integrations are P0). Until it is entered, any of the 8 connectors that comes back for a go-live decision will be refused.

## Evidence

**Guard (node, the engine's own `fregCreate`/`fregPanels` over the real fragments):** `cd_p03_portal/tests/test_m28_capture_buttons.py`. It has 32 checks: **10 fail on HEAD's `m28.js`/`m28.py`, 32/32 pass after.**

**Live tests, run as non-admin users through `/p03/model/write` and `/p03/model/action`:** `cd_itsm/tests/test_m28_capture_pass2.py`, **23/23** pass. They found two real receiver defects before any deploy, both fixed:
- `env.with_company` does not exist on an Environment.
- `_reply(200, status=...)` collided with `_reply`'s own `status` parameter, so every accepted post would have raised.

**Mutation check:** 31 mutants, each re-introducing one defect into the new code or the receiver. They ran in a throwaway worktree, each against the tests for its area. **27 go red.**
- The first run left 7 alive. Two were real test gaps: a tested fallback and a recorded batch had only been probed through the workspace form, and the form's field lock hid the model guard. Direct ORM-write tests now kill both. A third survivor was a runner scoping error, and it dies once its test is selected.
- The 4 that survive are held by a second barrier. Fallback tests and receipts are write-protected by the ACL even for an Integration Admin; a plain user has no create ACL on fallbacks; and a replay that already ran is refused by the approval mixin.

**Regression:**
- `cd_itsm`, the whole suite on a private clone: **377 tests, 375 pass, 2 fail.**
- The 2 failures (`test_a12f_m28_8_payload_is_checked_at_emit...` and `test_a12f_handoff_a_late_allocation_blocks_action_clear`) fail identically on HEAD code.
- `test_a12f_m28_second_pass`: the two connector go-live tests now declare pattern and priority. The gate is new, so this is a rule change, not a relaxation.
- Static portal suites (estate page standard, A12 write whitelist, DOFA coverage, form defaults, M28 guard) pass.

**UI walk:** headless Chromium against a private server (worktree code, DB `fix_test_m28c2`, port 8143).
- The 8 pages' buttons, in order: + New API Rate Limit, + API Endpoint, + New Event Topic, **+ Request a Consumer Replay**, + New Event Subscription, + New Connector, + Decide a Sync Conflict, + Record a Reconciliation Investigation.
- The 8 new lists, the 7 new or changed forms and the connector list render with **0 console errors**.
- A real UI save of an Inbound Webhook Source stored it as "Awaiting Go-Live".

## State

- **Landed and pushed** on `fix/a03-live-data-and-pending-work`: fix, test and this report. The feature branch `fix/m28-capture-pass2` is pushed too.
- **Deployed 19 Nov 2026.** `-u cd_itsm,cd_p03_portal` ran on fix_real and fix_dev inside the combined, owner-approved wave run by the M22 session (with M22/M23/M25/M26/M27/M29/M30). There was one restart at 10:57 local: 8069 is PID 64400, 8090 is PID 77212.
- **Post-deploy checks.** All are read-only and all pass on both databases:
  - `cd_itsm` is 19.0.0.2.0 (installed).
  - The 7 new tables and the 4 `fix_connector` columns exist, and the BFX sequence is present.
  - The connectors are unchanged (8 in total, 6 live). None declares a pattern or priority yet; that is owner data.
  - `POST /hooks/v1/inbound/nope` answers 401 JSON "Unknown source or bad signature" on 8069 and 8090.
  - The current backend bundle (`57ed71c`) carries the new forms and screens.
  - The new processes logged no "Failed to load registry", and 8069 logged 0 ERROR lines. 8090 logged one asset-attachment DELETE serialization failure, which Odoo retried, and the request then answered 200. It is unrelated to M28.
- **Live walk.** Headless Chromium on 8069/fix_real, with no saves:
  - The 8 pages show the same buttons as on the private server.
  - All 16 new or changed screens render with 0 console errors.
  - In-Process Subscriptions lists the 191 real rows.
