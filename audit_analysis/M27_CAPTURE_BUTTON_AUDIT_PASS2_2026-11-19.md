# M27 Contact Centre (16743): capture audit, pass 2

**Date:** 19 Nov 2026 · **Estate:** 8069 = `fix_real`, 8090 = `fix_dev` · **Unit:** CD-M27 · **Branch:** `fix/m27-capture-pass2`

## 1. Question

The user again saw M27 sub-module pages without a relevant data-capture button. This was after the 14 Nov pass ([M27_CAPTURE_BUTTON_AUDIT_2026-11-14.md](M27_CAPTURE_BUTTON_AUDIT_2026-11-14.md)) had given every page a "+ New".

This pass checks each page against more of the spec than the first one did:

- the functional requirements, §5 (FR-CCE-001…058);
- the business rules, §9 (BRU-CCE-01…15);
- the entities M27 owns, §10.1;
- the automations, §11 (AUT-CCE-01…14).

The question for each page: does it capture **the records the spec says that sub-module produces**, not just *a* record?

Spec file: `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md`.

## 2. Findings (before, HEAD a6ca660a)

| # | Sub-module | Captured before | What the spec names there that could not be captured |
|---|---|---|---|
| 1 | Voice & IVR (FR-001…008) | IVR flow, outbound list | **Callback** (FR-003): a queue could be set to "offer a callback", but no callback record existed, so the promise was never kept or measured. **Voicemail** (FR-007, AUT-CCE-11): "offer voicemail" was likewise a setting with no record behind it. **On-call rota** (FR-008, 24/7 support model): nothing said who takes 16743 when a queue is shut. |
| 2 | Digital Channels (FR-009…016) | Digital contact (e-mail, WhatsApp, chat, in-app) | **Inbound SMS** (FR-012) and **social messaging** (FR-013) had no channel value, so they could not be logged. |
| 3 | Unified Conversation (FR-017…025) | Conversation | No gap. |
| 4 | Queue & Routing (FR-019…023) | Queue, routing rule, workstream, capacity | No gap. |
| 5 | Agent Desktop (FR-026…034) | Wrap-up, Set My Presence | No gap. |
| 6 | Workforce Management (FR-050…053) | Roster shift | **Volume forecast** (FR-050; spec 10.1 `fix.contact.forecast`). The screen was titled "Forecast & Roster", but no forecast could be entered. Rosters were planned against nothing. |
| 7 | Quality Monitoring (FR-054…058) | QA evaluation, rubric | **Calibration session** (FR-055): several evaluators scoring one interaction. The existing "in calibration" state is a single score's dispute, which is a different thing. **Coaching** (FR-056): no coaching record, so improvement could not be tracked. |
| 8 | ERP Notification Service (FR-035…049) | Notification template, provider | **Per-party volume throttle** (FR-044, BRU-CCE-15, AUT-CCE-13). Nothing limited how many promotional messages one customer received. |
| 9 | Consent Enforcement (FR-038…041, 046) | DND entry, M33 consent | **Preference centre** (FR-046, BRU-CCE-13; spec 10.1 `fix.channel.preference`): a customer could not opt out of one category. **Classification challenge** (FR-041 "auditable and challengeable", BRU-CCE-04): a promotion sent as a "service update" skips consent, DND and the overnight window, and there was no way to challenge it. |

## 3. What was built

**`cd_contact_centre` 19.0.1.1.0**

`models/fix_cc_capture2.py` is imported last. Workflow fields are guarded by `fix.guarded.mixin`, so the endpoint cannot type a state.

| Record | Rules enforced on the server |
|---|---|
| `fix.cc.callback` | Call By must be after Call From.<br>A failed attempt needs a note.<br>Reaching the customer completes it, and records whether that was inside the window.<br>An hourly cron (`ir_cron_cc_callback_missed`) marks a passed window as missed. |
| `fix.cc.voicemail` | Respond-by is the next business day in BST; Friday and Saturday are skipped.<br>*Queue as a Conversation* opens a voice `fix.conversation` in its queue, with the transcript as the first turn, once only.<br>Discarding needs a reason. |
| `fix.cc.oncall.rota` | One primary per queue at a time.<br>Agents can read it; only supervisors can write it.<br>`fix.cc.queue.current_diversion()` names the person on call and their number whenever the queue is shut. |
| `fix.cc.contact.forecast` | One forecast per channel, queue and BST hour (checked in Python, because Postgres treats an empty queue as distinct).<br>Actual volume, the same-hour average of the last 4 weeks, and the forecast error are computed from the conversations that actually arrived. |
| `fix.cc.qa.calibration` + `.line` | Each evaluator enters only their own score, unless they are a supervisor.<br>The agent who handled the call cannot calibrate it; this is checked **before the insert**.<br>Spread, mean and a consistency flag are computed.<br>Closing needs two or more scores and a supervisor.<br>A closed session is kept as evidence. |
| `fix.cc.qa.coaching` | The coach is never the agent.<br>The evaluation coached from must be that agent's.<br>Improvement = the agent's average QA score after the session minus the score coached from.<br>Only the coached agent can acknowledge it. |
| `fix.cc.notif.throttle` | Supervisors only.<br>One active rule per purpose and channel.<br>Covers marketing, research, profiling and collections; service updates can never be throttled. |
| `fix.cc.channel.preference` | Opting out of service updates, payment notices or call recording is refused (BRU-CCE-13).<br>Each change re-stamps who recorded it and when. |
| `fix.cc.urgency.challenge` | The claimed class comes from the message's purpose; the proposal must differ from it.<br>Only a supervisor decides, never the one who raised it, and a reason is required. |

**Send path (`fix.notif.delivery.queue`)**

Two no-op hooks were added to the base file. They are implemented in `fix_cc_capture2.py`:

- `_fix_preference_verdict`: an opted-out optional category is **suppressed** with decision `preference_opt_out`, and the preference is stamped on the row.
- `_fix_throttle_vals`: a customer already over the ceiling has the message **deferred** to when the oldest message in the window ages out. The row records `throttle_id` and `throttled_until`.

**Channels**

`fix.conversation.channel` gains `sms` and `social`.

**Workspace (`cd_p03_portal`)**

- `a03/m27.js`:
  - 9 lists and 9 forms, each with a "+ New" label, empty-state text and state-gated list actions (with reason prompts where needed);
  - chips and lists on pages 1, 6, 7, 8 and 9;
  - SMS and Social added to the digital form;
  - nav entries added.
- `controllers/a03/m27.py`: 10 new surfaces, with list actions whitelisted and **server-side pickers** (internal users only, open queues, closed contacts for calibration, sent messages for challenges).
- `controllers/a03/writable.py`: regenerated with `form_fields.py`. Only the M27 blocks changed.

**Security**

- 14 ACL rows.
- Company and operating-unit isolation rules generated for this module only. The other modules' generator drift was reverted.

## 4. Evidence

| Check | Result |
|---|---|
| `tests/test_m27_capture_pass2.py`: registry evaluated in node with the engine's own `fregCreate`/`fregPanels`; ORM driven through `/p03/model/write` and `/p03/model/action` as **non-admin** users on private clone `fix_test_m27c2` | **17/17 pass. 17/17 fail on HEAD a6ca660a.** |
| Mutation check: 20 rule mutants in `fix_cc_capture2.py` | 19 killed; 1 equivalent survivor (§4.1) |
| `cd_contact_centre` suite, all A03 portal guards (`test_a03_*`), M27 pass-1 guards, estate page standard (same clone) | 1,536 tests: **7 failures, 212 skipped.** The same 7 also fail on HEAD a6ca660a against the same DB, so they are test-DB drift: a duplicate `fix_entity` row ×3, `fix.estimate.line.qty` renamed, `fix.survey.question` display name, and pre-existing providers/queues in the clone ×2. |
| Pass-1 guard `test_m27_capture_buttons.py` | It pinned page 1's chips and the digital channel list exactly. It was relaxed to require the old chips and channels, plus the new ones. |
| Module upgrade on the clone | `-u cd_contact_centre,cd_p03_portal`: exit 0, 10 new tables, version 19.0.1.1.0. The "no table" errors are peers' M18/M19 models that this clone never installed. |
| Headless Chromium walk on private server :8137 (worktree code, `fix_test_m27c2`) | All 20 screens open with **no "not served" text and 0 console errors**: 9 new lists, 9 new forms, the digital list and form. All 9 sub-module pages render with their new chips. A callback was **saved through the form UI**: two tabs, local datetimes stored as UTC, state Requested. |

### 4.1 Mutation check

**19 of 20 killed.** Each mutant was applied to `fix_cc_capture2.py` in turn, with the guard run each time. A spot re-run confirmed a kill is an assertion failure, not a crash.

| Mutant | Result |
|---|---|
| Mandatory category opt-out allowed | killed |
| Opt-out not enforced at send | killed |
| Throttle never defers | killed |
| Calibration closes with one score | killed |
| Anyone closes a calibration | killed |
| Evaluator enters scores for others | killed |
| Handling agent calibrates own call (pre-insert check removed) | **survived**: equivalent, the model constraint `_check_line` still refuses it |
| Closed calibration editable | killed |
| Raiser decides own challenge | killed |
| Anyone decides a challenge | killed |
| Challenge proposes the same class | killed |
| Coach acknowledges for the agent | killed |
| Agent coaches self | killed |
| Failed attempt needs no note | killed |
| Friday/Saturday not skipped | killed |
| On-call overlap allowed | killed |
| Closed queue names nobody on call | killed |
| Forecast duplicates allowed | killed |
| Missed-callback sweep does nothing | killed |
| Voicemail queued twice | killed |


## 5. Not built / owner decisions

- **Channel selection from preference (FR-037)** is not automatic. Callers still pass the channel, because the intent API (T-03) is not built. The preferred channel is recorded and readable through `preference_for()`, but only the opt-out is enforced at send.
- **Versioned, approved templates (FR-036).** Adding approval would stop every existing template sending until someone approves it. The owner should decide how existing templates are approved before the gate goes on.
- **Customer inbox (FR-045).** The system writes it, not a person, so it is not a capture. `fix.notif.delivery` is today's durable record.
- **Quality sampling rules (FR-054, AUT-CCE-14).** Not built.
- **Roles.** On-call rota, throttles, calibration close and challenge decisions all need **Contact Centre Supervisor**. On fix_real that group has **1 holder**. Appoint more supervisors, or a Marketing Head role for throttles, before the go-live.
- **Telephony.** It does not yet post callbacks or voicemail itself. Whoever clears the voicemail box logs each message, until the CPaaS adapter exists.

## 6. State

- Committed on `fix/m27-capture-pass2`.
- **Not yet deployed.** It needs `-u cd_contact_centre,cd_p03_portal` on fix_real and fix_dev, plus one restart (new surfaces), with the owner's go-ahead.
