# M27 Contact Centre (16743): sub-module capture-button audit

**Date:** 14 Nov 2026 · **Estate:** 8069 = `fix_real` · **Unit:** CD-M27

## 1. Question

Does every M27 sub-module page offer a capture button, and does that button capture the record the sub-module exists to produce?

The reference is the M27 module specification, section 5 (FR-CCE-001…058). Its file is `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md`. The function register only names the 9 sub-modules and their function counts.

## 2. Findings (before)

| # | Sub-module (spec) | Button before | Verdict |
|---|---|---|---|
| 1 | Voice & IVR (FR-001…008) | + New IVR Flow | Relevant. Outbound dial lists (outbound voice, FR-004) sat on page 9 instead. |
| 2 | Digital Channels (FR-009…016) | **none** (`create: false`) | **Missing.** WhatsApp and web chat arrive through `/contact/chat/message`. E-mail and social messages have no adapter, so they could not be recorded at all. |
| 3 | Unified Conversation (FR-017…) | + Conversation | Relevant, but the form was defective. It required a telephony SID, a disposition and 20+ characters of wrap-up at **capture**, so a contact could not be logged while it was still open. It also let a recording URL be typed; `action_resolve` then refused that call for ever, because a URL has no digest of the audio (REQ-27.2). |
| 4 | Queue & Routing (FR-019…023) | + New Queue | Relevant. The Skills Routing Rule form existed but had no chip. |
| 5 | Agent Desktop (FR-026…034) | + New Disposition **Code** | **Irrelevant.** That is supervisor configuration. No page let an agent wrap up a contact (FR-033, BRU-CCE-11), and no code path let an agent set their own presence (FR-032). Every `set_presence()` caller is system-forced, so no agent could ever make themselves available for routing. |
| 6 | Workforce Management (FR-050…053) | + New Roster Shift | Relevant. |
| 7 | Quality Monitoring (FR-054…058) | + New QA Evaluation | Relevant, but the form had no rubric. A score said nothing about what it measured. |
| 8 | ERP Notification Service (FR-035…049) | + New Notification Template | Relevant, but the form had no Bengali body (`body_bn`). The model calls it "the field that matters": every workspace template sent English to Bengali-preferring customers. |
| 9 | Consent Enforcement (FR-038…041, 046) | + New Outbound **Dial List** | **Irrelevant.** Dial lists enforce nothing. Spec 10.1 makes the BTRC DND registry M27's record, and the delivery service reads it at every promotional send (`_dnd_reason`). It was on no screen. |

There was also an integrity hole on the Agent Presence form. Anyone could overwrite presence, its "Set By" source, its time and the missed-offer count. Those writes went straight through and skipped `set_presence()`, so no history row was written. Adherence is measured from that history.

## 3. What was changed

**Registry `cd_p03_portal/static/src/a03/m27.js`**

- Page 1 now shows Outbound Campaigns and the Outbound List chip.
- Page 2 captures through the new **Log a Digital Contact** form (`M27-form-digital`). The channel list offers only Email, WhatsApp, Web Chat and In-App. The form has the required Operating Unit and a message grid, and asks for no SID and no wrap-up.
- Page 4 has a new Routing Rule chip.
- Page 5 lists the conversations being handled (`state = with_agent`):
  - It captures through **Wrap Up a Conversation** (`M27-form-wrapup`). Step 1 picks the conversation. Step 2 takes the disposition, FCR flag and notes, then calls `action_wrap_up`.
  - Chips: Set My Presence, Disposition Code, Agent Script.
  - **Set My Presence** (`M27-form-set-presence`) picks one of the active statuses, then calls `action_set_my_presence`.
- Page 9 lists the DND registry and captures **DND Registry Entry** (`M27-form-dnd`). It adds a **Suppressed at Send** list (`fix.notif.delivery`, state suppressed) and a **Consent Record** chip that opens M33's own consent form. M33 owns consent; M27 enforces it.
- Conversation form:
  - SID, disposition and wrap-up notes are no longer required at capture. The close gates still demand them.
  - Recording URL is read-only, with the recording basis and the refusal reason shown beside it.
- Template form: Bengali name, subject and body added.
- QA form: published-rubric picker added, plus the derived auto-score, coverage and pending-criteria fields.
- Presence form: read-only, history grid read-only.

**Server**

- `controllers/a03/m27.py`:
  - Serves `fix.dnd.registry`.
  - Whitelists `fix.conversation.action_wrap_up` and `fix.cc.presence.status.action_set_my_presence`.
- `controllers/a03/writable.py` was regenerated. The presence whitelist is now `{is_bookable}` only. `recording_url` left the conversation whitelist. The Bengali template fields, `rubric_id` and the DND fields were added.
- `cd_contact_centre/models/fix_contact_centre.py`: new `action_wrap_up(disposition_id, wrapup_notes, fcr)`.
  - It works only on a conversation in `with_agent`.
  - Only the handling agent or a CC supervisor may call it.
  - It closes **through `action_resolve`**, so the disposition, 20-character notes and audio-digest gates still decide.
- `cd_contact_centre/models/fix_cc_routing.py`: new `fix.cc.presence.status.action_set_my_presence()`. It goes through `state_for(user)` and `set_presence(source="manual")`, so the change is logged.

No new columns were added, so no module upgrade was needed.

## 4. Evidence

| Check | Result |
|---|---|
| `tests/test_m27_capture_buttons.py` (node runs the engine's own `fregCreate`/`fregPanels`) | 32/32 pass. **17 fail on HEAD.** |
| `tests/test_m27_capture_live.py`, run as non-admin users through `/p03/model/write` and `/p03/model/action` on private clone `fix_test_m27` | 10/10 pass |
| Estate page standard, A03 mapping, A03 form children, A03 whitelist and coverage, full `cd_contact_centre` suite (same clone) | All pass except 3 relay-dependent tests: M61 knowledge-binding sync ×2 and approval e-mail/SMS. The clone holds 53,621 pending outbox events and the relay drains oldest first. None of the 3 touches changed code. |
| Live 8069 after the user-approved restart (14 Nov 03:41, pid 48996, 155 modules, no registry error), production bundle `8f7cd44` | All 9 pages show the buttons and chips listed in section 3. All 9 new or changed forms open with no "not served" error; DND said "not served" before the restart. Set My Presence lists the 5 real statuses. |
| Live whitelist probe (non-existent id) | `action_wrap_up` and `action_set_my_presence` return "Record not found". The control (`unlink`) returns "Action not available". |

## 5. Not built / owner decisions

- **fix_real has no M27 activity**: 0 conversations, 0 agent-presence rows, 0 deliveries, 0 DND numbers. Wrap Up has nothing to pick until contacts arrive.
- **DND writes are manager-only.** The `fix.dnd.registry` ACL grants create and write to DOFA Tier 2 (42 holders), not to agents. An agent records a customer's opt-out as a marketing-consent withdrawal (Consent Record chip). Decide whether hotline agents should also list numbers.
- **Set My Presence is open to any internal user.** Workstream presence filters and bullseye user groups still limit who receives work. Decide whether it should be limited to a Contact Centre Agent role; none exists today. The CC supervisor group has 1 holder.
- **Spec entities with no model** (a build, not a button):
  - callback (FR-003)
  - voicemail (FR-007)
  - customer inbox (FR-045)
  - per-category preference centre (FR-046)
  - versioned and approved templates (FR-036)
  - volume forecast (FR-050)
  - calibration and coaching sessions (FR-055/056)
  - quiet-hours queue as a record
  - social-messaging channel value
- The workspace cannot attach a call recording; the telephony layer does that through `attach_recording()`.

## 6. Deployment state

Live on 8069 since the 03:41 restart. Every other session's uncommitted file was last changed before 01:10, so the server started at 02:58 was already running them; the restart newly published only this M27 work and the M26 commit `abbc4fe9` (03:30, committed). Committed (with the user's go-ahead) on `fix/a03-live-data-and-pending-work`, not pushed. The commit holds `m27.js`, `controllers/a03/m27.py`, the M27 blocks of `controllers/a03/writable.py` (the M34 blocks in that file go with the M34 commit), the two `cd_contact_centre` model files, the two new tests and this report.
