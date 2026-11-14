# M32 Conversational AI: sub-module capture audit

**Date:** 14 Nov 2026 · **Area:** A03 · **Workspace fragment:** `cd_p03_portal/static/src/a03/m32.js`
**Backend:** `cd_contact_centre` (models), `cd_p03_portal/controllers/a03/m32.py` (surfaces, reports, KPIs), `controllers/a03/writable.py` (write whitelist, generated)

The user reported that not every M32 sub-module page has a relevant data-capture button.
That was right, and worse than it looked: **five of the nine pages captured nothing at all**.
Three of them had nothing to capture because the records the spec gives the Customer Service
Manager had never been built.

## What M32 is supposed to capture

The Function Register only names the nine sub-modules (62 functions). The detail is in
`1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32_Conversational_AI_and_Virtual_Assistant.md`:
§5 (FR-CAI-001..038), §9 (BRU-CAI-01..15), §10.1 (owned entities), §11 (automations) and §13 (roles).

| # | Sub-module | Spec basis | What a person records there |
|---|---|---|---|
| 1 | Intent Recognition | FR-CAI-001..008, §10.1 `fix.intent.taxonomy` | Intents, and the NLU release bundle that takes a corpus to production |
| 2 | Entity Extraction | FR-CAI-003, §10.1 `fix.entity.definition` (code, type, extraction rules, validation, examples) | **Entity definitions** |
| 3 | Dialogue Management | FR-CAI-009..014 | Dialogue flows |
| 4 | RAG Grounding | FR-CAI-015..020, T-01 | Knowledge sources, model providers (residency) |
| 5 | Authenticated Actions | FR-CAI-021..030, BRU-CAI-03/04/05; §13: Customer Service Manager owns the **authority matrix** | **Action authority rules** (the actions themselves are written by the assistant) |
| 6 | Guard Rails | FR-CAI-031..035, BRU-CAI-08; SOD-20 | Guard-rail rules |
| 7 | Handoff Decision | FR-CAI-036 ("each independently tunable"), BRU-CAI-06/07, AUT-CAI-04, §8.2 | **Handoff triggers** (handoffs themselves are written by the assistant) |
| 8 | Agent Assistance | FR-CAI-038 ("always editable and never auto-sent") | **The review, then the send**, of an AI answer |
| 9 | Analytics | §14, AUT-CAI-08/10 (unresolved queue, weekly review) | **The review of mined candidate intents** (accept / reject) |

## What the code did (proved on HEAD before the fix)

`cd_p03_portal/tests/test_m32_capture_buttons.py` runs the engine's own `fregCreate` / `fregPanels` in
node over the real registry. Against unmodified HEAD (`4a4842b9`) **17 of its 35 checks fail**.

| # | Page | "+ New" on HEAD | Chips on HEAD | Defect |
|---|---|---|---|---|
| 1 | Intent Recognition | + Intent | Intent, NLU Release Bundle | The release-bundle chip captured a record the page did not list. The playground was on no page. |
| 2 | Entity Extraction | **none** | **none** | Listed AI answers and a report of three hard-coded regexes. No entity definition record existed. |
| 3 | Dialogue Management | + Dialogue Flow | Dialogue Flow | — |
| 4 | RAG Grounding | + RAG Source | RAG Source, Model Provider | The Model Provider chip captured a record the page did not list. |
| 5 | Authenticated Actions | **none** | **none** | Listed conversations. **No authority matrix existed**, so nothing recorded what the assistant may do. |
| 6 | Guard Rails | + Guard-Rail Rule | Guard-Rail Rule | **Every employee could create, change or delete a guard rail** (ACL `base.group_user` 1,1,1,1), and nothing enforced SOD-20. |
| 7 | Handoff Decision | **none** | **none** | Listed conversations. **No handoff trigger existed**, so nothing could be tuned, and every handoff got the same queue priority. |
| 8 | Agent Assistance | **none** | **none** | Listed AI answers needing a person, with no way to review or send one from the page. |
| 9 | Analytics | **none** | **none** | The improvement queue (Candidate Intents) sat on no page. |

On no page at all: the Assistant Playground, Model Providers, NLU Release Bundles and Candidate Intents.

Defects found on the way:
- **The Candidate Intent form let anyone type the mined evidence and the review state.** Phrase, occurrences, distinct conversations, samples and `state` were all editable, and all were in the write whitelist. So "Accepted" could be typed, bypassing Accept/Reject and its `assistant.intent_candidate_accepted` event.
- **The Guard-Rail Intervention Log said "the estate has NO per-utterance intervention log"**, although `fix.assistant.ask` has recorded the verdict and the rule that fired on every answer since the S7 build. It listed rules only.
- **Every IMEI is masked before a transcript turn is stored.** The REQ-32.3 card mask (13-16 digits) also covers a 15-digit IMEI, so an IMEI can never be extracted from a stored transcript. That is the safe default, because an IMEI and a payment card both pass the Luhn check. I left the masking as it is: see gaps.
- **Observation, not M32:** the isolation-rule generator shows that M31's new `fix.workshop.test.result` has no company rule. I reverted the generator's change in `cd_workshop` so as not to touch another module, and left it for M31's owner.

## What was changed

**Workspace (`m32.js`)**
- Every page names its captures explicitly (`create:` and `forms:`):
  - 1 Intent Recognition: + New Intent, with the NLU Release Bundle chip. The page now lists the release bundles and the playground.
  - 2 Entity Extraction: **+ Define an Extractable Entity**. It lists Entity Definitions and the extraction report.
  - 4 RAG Grounding: also lists Model Providers.
  - 5 Authenticated Actions: **+ Set an Action Authority Rule**. It lists the Action Authority Matrix and the conversations.
  - 7 Handoff Decision: **+ Tune a Handoff Trigger**. It lists Handoff Triggers, the handoff packages and the Handoff Reasons report.
  - 8 Agent Assistance: **+ Review an AI Answer**, with a **Send a Reviewed Answer** chip. Both are pick forms: step 1 chooses the answer, step 2 runs `action_mark_reviewed` / `action_send_to_customer`. Nothing can be typed.
  - 9 Analytics: **+ Review a Candidate Intent** (accept), with a **Reject a Candidate Intent** chip. Both are pick forms that carry the reviewer's note; a rejection needs a reason. It lists Candidate Intents.
- A new nav group, "Actions & Handoff", holds the matrix and the triggers. The seven new forms are in "Assistant Configuration".
- The Candidate Intent form shows the mined evidence and the state read-only. The regenerated whitelist drops them.

**Backend (`cd_contact_centre`, new `models/fix_assistant_registers.py`)**, following spec §10.1 and §13:
- `fix.assistant.entity`: code, type, pattern, validation (none, IMEI Luhn, Bangladesh mobile, positive amount), examples and counter-examples.
  - **A definition is proved when saved:** every example must extract and no counter-example may. A pattern that matches an empty message is refused, as is one that repeats a repeating group (`(\d+)+`), which can hang on a crafted message. The pattern runs on every customer turn.
  - Bengali digits (০-৯) count as digits (FR-CAI-003).
  - The **Entity Extraction report runs the registered definitions**. With none registered it runs the three built-in patterns and says so.
- `fix.assistant.action.authority`: one rule per action (status enquiry, booking, reschedule, price quote, warranty check, payment link, complaint capture, repair approval, contract cancellation, refund, goodwill credit). The hard rules are on the model:
  - BRU-CAI-04: cancellation, refund and goodwill credit can never be delegated, with or without a row.
  - BRU-CAI-03: an action the assistant performs needs identity verification first.
  - BRU-CAI-05: a commitment needs explicit confirmation.
  - A repair approval needs a limit, above which a person approves.
  - **The live assistant reads it.** Before a grounder answers order status, invoice, price or booking, the matrix is checked. A withdrawn action hands off as `action_beyond_authority`. An unverified customer hands off as `identity_not_verified`. A withheld action is never answered by the LLM instead (`_generate` refuses). With no row, today's behaviour is unchanged.
- `fix.assistant.handoff.trigger`: one row per signal, using the spec's 17 signals across emotional, operational and technical. The **category follows from the signal** and cannot be typed. A row sets the queue priority and whether supervisors are alerted.
  - **Distress** is Urgent and always alerts (BRU-CAI-06, AUT-CAI-04). **An explicit request for a human** is at least High. Neither can be switched off or deleted (BRU-CAI-07).
  - **Every handoff now reads it.** `action_handoff_to_agent` stamps `handoff_signal`, `handoff_category` and `handoff_priority` on the conversation; these are guarded and never typed. It raises the routed work item to that priority (spec §8.2: "priority set by trigger"), alerts every supervisor when the trigger says so, and publishes `assistant.handoff` (spec §12.3).
  - With no row, the spec defaults apply.
- **Guard rails:** every employee still reads them, but only a Contact Centre Supervisor writes them. **SOD-20:** the author of a rule cannot switch it off or delete it; another supervisor must.
- **Access:** the three registers are read by every employee and written by a Contact Centre Supervisor or a system administrator. Each has a company isolation rule, generated by `generate-isolation-rules.py`.

**Controller (`controllers/a03/m32.py`)**
- Three new surfaces.
- **Handoff Reasons** groups by trigger category and counts the urgent handoffs (spec §14: "by trigger category").
- **Handoff Packages** shows each handoff's category and queue priority.
- **Guard-Rail Intervention Log** counts per rule how often it blocked and how often it flagged, from the grounded-answer log.
- **Entity Extraction** runs the registered definitions.

## Evidence

- `cd_p03_portal/tests/test_m32_capture_buttons.py`, 35 checks: **17 fail on HEAD, 35 pass after the fix.** The estate-wide page guard (`test_estate_module_pages.py`) still passes alongside it.
- `cd_contact_centre/tests/test_m32_capture_live.py`, **44/44 pass** on a private clone of fix_test (`fix_test_m32`, with `-u cd_entity_config,cd_workshop,cd_contact_centre,cd_p03_portal`; fix_test predated the M30/M31 builds). The tests run as non-admin users (Contact Centre Supervisors and plain agents) through `/p03/model/form|write|action` and the live bot. They show that:
  - every register form opens blank for a supervisor, and every pick form opens its record for an agent;
  - a plain agent reads the registers but cannot change them, or any guard rail;
  - a definition is proved against its examples, Bengali digits extract, the IMEI check digit is applied, and a catastrophic or empty-matching pattern is refused;
  - refund and goodwill rules are refused, as are identity-free and confirmation-free rules and a limitless repair approval;
  - with "identity first", an order-status question from an unverified customer goes to a person (`identity_not_verified`). A withdrawn action hands off as `action_beyond_authority`, and no LLM answer is generated instead. With no rule, behaviour is unchanged;
  - SOD-20: the author cannot switch their own guard rail off, but another supervisor can;
  - the trigger category cannot be typed. Distress and an explicit request cannot be weakened or deleted. A handoff is stamped and its work item raised to the trigger's priority (50 = High, 100 = Urgent). Distress schedules an activity for every supervisor;
  - review by another person, then send, puts the answer on the transcript. The asker cannot review their own answer, and an unreviewed answer cannot be sent;
  - a candidate's mined evidence and state cannot be typed, and Accept/Reject keep the reviewer's note.
- **Mutation check:** I re-introduced eight defects one at a time, and **all eight turned the suite red**: refund delegable, identity not checked, authority not consulted, author removes own guard rail, explicit request switchable, handoff priority not applied, generation answers a withheld action, and candidate state typeable. The first run caught only 7: the priority test skipped its check when no workstream existed. The test now builds its own queue and workstream and requires the work item.
- **Regression** on `fix_test_m32`: the whole `cd_contact_centre` suite plus the M27 capture suites, the A03 registry/mapping/control/whitelist suites, the KPI tile guard and the estate page guard. Everything passed except three tests, `test_a10_s6_knowledge_binding` (2) and `test_a11_approval_notify` (1). **Those three fail identically with the unmodified HEAD code** (run from the `m31rel-wt` worktree against the same database). They are outbox event-consumer paths and were not touched here.
- **Browser check** on a private Odoo (`fix_test_m32`, port 8073, served from the worktree; the live 8069 server was not touched):
  - all nine pages show their "+" button and the right capture chips (table above);
  - "Define an Extractable Entity" refused a counter-example that extracts, then saved the IMEI definition: "2 of 2 examples extract; 0 of 1 counter-examples do", one example written in Bengali digits;
  - "Review a Candidate Intent" listed the mined phrase in step 1, offered only the reviewer note in step 2, and "Accept for Authoring" stored `accepted` with the note;
  - all six M32 lists return every declared column;
  - the only console errors were two cached asset bundles missing from the clone's filestore (a SQL-level clone copies no files), which is unrelated to M32.

| # | Page | "+ New" now | Chips now |
|---|---|---|---|
| 1 | Intent Recognition | + Intent | Intent, NLU Release Bundle |
| 2 | Entity Extraction | + Define an Extractable Entity | Entity Definition |
| 3 | Dialogue Management | + New Dialogue Flow FSM | Dialogue Flow |
| 4 | RAG Grounding | + New RAG Knowledge Source | RAG Knowledge Source, Model Provider |
| 5 | Authenticated Actions | + Set an Action Authority Rule | Action Authority Rule |
| 6 | Guard Rails | + New Safety Guardrail Rule | Guard-Rail Rule |
| 7 | Handoff Decision | + Tune a Handoff Trigger | Handoff Trigger |
| 8 | Agent Assistance | + Review an AI Answer | Review an AI Answer, Send a Reviewed Answer |
| 9 | Analytics | + Review a Candidate Intent | Accept a Candidate Intent, Reject a Candidate Intent |

## Gaps left (no model, or an owner decision)

- **The assistant performs no actions yet.** Booking, rescheduling, payment links and complaint capture all hand off: the grounders only answer status, price and branch questions. The authority matrix therefore gates disclosures and hand-offs today. It is the check that any future action must call (`fix.assistant.action.authority.check`).
- **Identity verification** is read as "the conversation has an identified customer". There is no OTP step in the assistant (FR-CAI-021).
- **Nothing detects the emotional and operational signals yet.** Frustration, distress, SLA risk, repeat contact and high-value customers have triggers that can be tuned, but no detector raises them. The technical signals (low confidence, guard rail, no retrieval, out of scope, authority, review) are raised today.
- **Per-intent confidence thresholds** (T-05, `fix.intent.taxonomy.confidence_threshold`): the engine still uses one global 0.75 / 0.50 gate.
- **Turn-level records** (`fix.assistant.turn`, `fix.grounding.source`, `fix.guardrail.event`, `fix.assistant.action`, `fix.handoff.record`, `fix.unresolved.intent`) do not exist as separate models. Their facts live on `fix.conversation`, `fix.conversation.turn` and `fix.assistant.ask`.
- **Entities are not extracted at intake**, so no `entities_json` is stored per turn. Because the PII scrubber masks 13-16-digit numbers, IMEIs and card-length serials can only be extracted at intake, before scrubbing. Doing that means storing the extracted IMEI. That is a data-protection decision for the CDO.
- **Guard rails have no stage (input/output) or severity**, and the output filter (FR-CAI-032) is not configurable.
- **Assistant CSAT** still cannot be attributed: the survey links to the service order, not to the conversation.
- **People:** on fix_real **one** user holds Contact Centre Supervisor. Switching off a guard rail someone else wrote needs a second supervisor. Supervisor alerts on distress reach that one person. Name a second supervisor.

## Deploy

<!-- DEPLOY -->
