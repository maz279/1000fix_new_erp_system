# M32 Conversational AI: sub-module capture audit, pass 2

**Date:** 19 Nov 2026 · **Area:** A03 · **Pass 1:** `M32_CAPTURE_BUTTON_AUDIT_2026-11-14.md`
**Workspace:** `cd_p03_portal/static/src/a03/m32.js` · **Backend:** `cd_contact_centre` (new `models/fix_assistant_capture2.py`), `cd_p03_portal/controllers/a03/m32.py`

The user again saw M32 pages without a relevant data-capture button. Pass 1 gave every page a "+"
button, so this pass read each page against what the spec says a person records there
(`1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M32_Conversational_AI_and_Virtual_Assistant.md`
§5 FR-CAI, §6 T-, §9 BRU-CAI, §10.1 owned entities, §11 AUT-CAI, §13 roles, §14 reports).
**Four of the nine pages still could not record a spec record**. The pass also found **one live-bot
defect**, which made the confidence gate leak, and **four access gaps**.

## What each page must capture, and what it could on HEAD (742e46bc)

| # | Page | Spec basis | On HEAD | Gap |
|---|---|---|---|---|
| 1 | Intent Recognition | §10.1 `fix.intent.taxonomy` (category, confidence_threshold), FR-CAI-002, T-05; T-11, BRU-CAI-14, AUT-CAI-11 (shadow evaluation) | Intent, NLU Release Bundle | **No category and no per-intent threshold.** The engine applied one global 0.75. **Nothing ran a shadow evaluation**, so a second bundle could replace production on the golden set alone. **The playground ran a fresh built-in engine**, not the released bundle the bot runs. |
| 2 | Entity Extraction | §10.1 `fix.entity.definition` | Entity Definition | — |
| 3 | Dialogue Management | FR-CAI-009..014 | Dialogue Flow | — (see gaps left) |
| 4 | RAG Grounding | FR-CAI-015..020 | RAG Source, Model Provider | — (see gaps left) |
| 5 | Authenticated Actions | FR-CAI-021..030, §13 | Action Authority Rule | — (actions are system-written) |
| 6 | Guard Rails | §10.1 `fix.guardrail.rule` (stage, severity); §14 guard-rail report "false-positive review"; §13 CDO R A | Guard-Rail Rule | **No stage and no severity**: every rule ran on both the question and the generated answer. **Nobody could review a firing**, so the report could not measure precision. |
| 7 | Handoff Decision | FR-CAI-036/037 | Handoff Trigger | — |
| 8 | Agent Assistance | FR-CAI-038 "always editable and never auto-sent"; §12.2 correction signals to M26 | Review / Send an AI Answer | **The answer could only be sent verbatim.** An agent who wanted to change one word had to abandon it and type a reply. |
| 9 | Analytics | §10.1 `fix.unresolved.intent`; AUT-CAI-06/08/10; §14 Knowledge gap report; KPI-184; §13 CSM C R U D A on the unresolved queue | Accept / Reject a Candidate Intent (mined n-grams) | **The unresolved queue did not exist.** A question the assistant could not answer was handed off and forgotten. Nobody gave it a disposition, no knowledge gap reached M61, and KPI-184 could not be measured. |

**Defect found while testing (live bot, REQ-32.1):** when the classifier was *not* confident (the
0.50–0.75 "ask the customer" tier), `intake_message` still wrote its best guess on the conversation.
`ask()` then grounded on `conversation.intent` and sent the authored answer, and the conversation
closed as **resolved by AI**. The three-tier gate was bypassed for every knowledge intent, and a
per-intent threshold could never take effect.

**Access (spec 13: the Customer Service Manager owns the taxonomy and the queue; agents read):**
- Every employee could create and edit intents (ACL 1,1,1,0).
- Every employee could accept or reject mined candidate intents (1,1,1,0).
- Every employee could create, edit and **delete** dialogue flows and RAG knowledge sources (1,1,1,1).

## What was changed

**Page 1, Intent Recognition**
- Intent form: **Taxonomy Category**, **Confidence Threshold (T-05)** and **Calibration Evidence**.
  - A threshold must lie between 0.60 and 0.99, which keeps a band where the assistant asks rather than guesses.
  - A threshold needs its calibration evidence.
- `AssistantEngine.classify_intent(text, thresholds)` applies the intent's own threshold. The live bot, the benchmark, the playground, the shadow run and the unresolved log all use it.
- New chip **Shadow-Evaluate a Release Bundle** (pick a benchmarked bundle), and a **Run Shadow Evaluation** action on the bundle list.
  - The PII-scrubbed customer turns of the last 30 days are replayed through production and the candidate; nobody is answered and only counts are kept.
  - It passes when the candidate answers at least as many turns and changes at most 2% of production's answers.
  - **Request and release now refuse a bundle that would replace production without a passing shadow run over this exact file against that production bundle (BRU-CAI-14).** The first release has nothing to shadow, so it is gated by the golden set alone.
  - The result is guarded (measured, never typed). It publishes `model.evaluation_completed`.
- The bundle form has a new **Shadow Evaluation** tab.
- The playground now classifies with the released bundle and the per-intent thresholds.

**Page 6, Guard Rails**
- Rule form: **Stage** (input, output or both) and **Severity**. `_evaluate_guardrails` runs a rule only at its stage.
- New chip **Review a Guard-Rail Firing**, and a new list **Guard-Rail Firings**. A supervisor picks a blocked or flagged answer and records *correct*, *false positive* or *attempted injection*.
  - A false positive needs a note.
  - A firing is reviewed once.
  - Agents are refused.
  - It publishes `guardrail.reviewed`.
- The **Guard-Rail Intervention Log** gains stage, severity, reviewed, false positives, attempted injections and **precision**, measured only over reviewed firings.

**Page 8, Agent Assistance**
- **Send a Reviewed Answer** now offers the reply prefilled and editable.
  - An edited reply goes on the transcript as the **agent's** turn. The AI draft stays on the record, with `sent_text` and `edited_by_agent`.
  - The edit publishes `assistant.answer_corrected` for M26.
  - An unedited reply is sent as the assistant's, as before.

**Page 9, Analytics**
- New register `fix.assistant.unresolved` (spec `fix.unresolved.intent`).
  - Every handoff with a no-answer signal (low confidence, out of scope, nothing retrieved) logs the customer's last, PII-scrubbed message, with the best-guess intent and confidence. It is logged once per open conversation and publishes `assistant.unresolved`.
  - Guard-rail, identity and authority handoffs are not knowledge questions and are not logged.
- The page's "+" is now **Review an Unresolved Question**, which records a disposition: knowledge gap, new intent, add an utterance, out of scope, or no action.
  - "Out of scope" and "No action" need a reason.
  - A knowledge gap publishes `assistant.knowledge_gap` for M61.
- New chip **Close a Knowledge Gap**: a gap closes only against the M61 article that now answers it.
- New **Knowledge Gap Report** (§14): unanswered questions by best-guess intent, gaps open and closed, and **KPI-184**, gaps closed within 30 days.
- The candidate-intent chips stay.
- Only a Contact Centre Supervisor (or an administrator) reviews or closes. The logged facts are guarded.

**Access:** intents, candidates, dialogue flows and RAG sources are now read by every employee and written by a Contact Centre Supervisor or an administrator. The unresolved queue: every employee reads it, supervisors review it, and it has its own company isolation rule.

**Bot fix:** an unconfident guess is still written on the conversation for the record. It is passed to `ask()` with `assistant_intent_unconfirmed`, so the grounder no longer answers from it.

| # | Page | "+ New" now | Chips now |
|---|---|---|---|
| 1 | Intent Recognition | + New NLU Intent Definition & Bengali Training Corpus | Intent, NLU Release Bundle, **Shadow-Evaluate a Release Bundle** |
| 2 | Entity Extraction | + Define an Extractable Entity | Entity Definition |
| 3 | Dialogue Management | + New Dialogue Flow FSM | Dialogue Flow |
| 4 | RAG Grounding | + New RAG Knowledge Source | RAG Knowledge Source, Model Provider |
| 5 | Authenticated Actions | + Set an Action Authority Rule | Action Authority Rule |
| 6 | Guard Rails | + New Safety Guardrail Rule | Guard-Rail Rule, **Review a Guard-Rail Firing** |
| 7 | Handoff Decision | + Tune a Handoff Trigger | Handoff Trigger |
| 8 | Agent Assistance | + Review an AI Answer | Review an AI Answer, Send a Reviewed Answer (**editable**) |
| 9 | Analytics | **+ Review an Unresolved Question** | **Review an Unresolved Question, Close a Knowledge Gap**, Accept / Reject a Candidate Intent |

## Evidence

- **Node guard** `cd_p03_portal/tests/test_m32_capture_pass2.py` (8 checks) runs the engine's own `fregCreate` / `fregPanels` over the real registry. **All 8 fail on HEAD 742e46bc** (run against a `git archive` of HEAD) and pass after the change. The pass-1 guard was updated for the two intended changes: page 9's "+" and the editable reply. Together with the estate page guard: 648 checks, 0 failures.
- **Live suite** `cd_contact_centre/tests/test_m32_capture_pass2_live.py` (9 tests) runs as **non-admin** supervisors and agents through `/p03/model/form|write|action` and the live bot, on a private clone `fix_test_m32c2` (of `fix_test_m30c2`, with the six modules that lagged the code upgraded). Together with the pass-1 suite (44) and the release-flow suite (6): **59/59**.
  - The live bot answers a message at 0.75 and **hands it off once the intent's own threshold is above its confidence**, logging it as unresolved.
  - A disambiguation-tier message is **not** answered (the REQ-32.1 defect).
  - The first release needs no shadow run. A second bundle is **refused (BRU-CAI-14)** until a shadow run over live scrubbed turns passes. The shadow result cannot be typed.
  - Rule stage is respected both ways.
  - An agent cannot review a firing. A false positive needs a note, and a firing is reviewed once. The log shows 1 blocked, 1 reviewed, 1 false positive, 0% precision.
  - An edited reply lands as the agent's turn and publishes `assistant.answer_corrected`. An unedited one is sent as the assistant's turn and publishes nothing.
  - A no-answer handoff is logged once (a guard-rail handoff is not). An agent cannot review it. "No action" needs a reason. A gap cannot close before review or without a reference. The report shows KPI-184.
  - Agents cannot create intents, dialogue flows or RAG sources, nor accept a candidate. Supervisors can.
- **Mutation check:** 11 defects re-introduced one at a time; **10/11 turn the suite red**. The survivor (the role check on the unresolved queue removed) is equivalent: the ACL row already refuses an agent's write on `fix.assistant.unresolved`, so the agent is still refused. A first run was invalidated because I edited files while it ran. The figures here are from a clean rerun.
- **Regression** on `fix_test_m32c2`: the whole `cd_contact_centre` suite plus the A03 control, registry, mapping, whitelist and children suites, the A12 whitelist, the KPI-tile guard, both M32 guards and the estate page guard. **1,342 passed, 8 failed, 212 skipped.** **All 8 fail identically with the base code on the same database**, run from a worktree at 60cb545c, whose cd_contact_centre and cd_p03_portal are identical to HEAD:
  - three `test_contact_live` (a `fix_entity` fixture collides with clone data);
  - the hotline work-item queue id;
  - the notification tariff;
  - the `fix.survey.question` display name;
  - the M10 `fix.estimate.line.qty`;
  - the A03 routed-approval check, which fails on an M28 integration ("declares no integration pattern").
- **Browser walk** on a private Odoo (`fix_test_m32c2`, port 8175, served from the worktree; 8069 and 8090 untouched):
  - all nine pages show the "+" and chips in the table above;
  - all ten new or changed screens open, and the Knowledge Gap Report and the intervention log show their new columns;
  - a real low-confidence handoff logged unresolved question #62, and **"Review an Unresolved Question" saved it through the UI** as a knowledge gap with the reviewer's note;
  - 0 console errors and 0 server errors.

## Gaps left (no model to build on, or an owner decision)

- **Dialogue flows are not executed.** `flow_json` is stored but no engine runs it, so session continuity (FR-CAI-014) and slot-retry limits would be decorative fields. The Dialogue Flow form's "Slot Extraction" and "Fallback" tabs carry notes only.
- **RAG freshness (FR-CAI-018, AUT-CAI-09).** Nothing indexes the sources: `chunk_count` and `last_indexed_at` are never written, so a freshness interval would flag everything as stale. This waits for the M61 indexer (W6).
- **The assistant performs no actions** (`fix.assistant.action` is unchanged since pass 1). There is no OTP identity step (FR-CAI-021).
- ~~Abandoned sessions not logged~~: **closed in pass 3** (below).
- ~~No emotional detectors~~: distress, abuse, explicit request and frustration are **detected from pass 3** (below). The **operational** signals (SLA risk, repeat contact, high-value customer) still have no detector. They need rules over M27/M33 data rather than phrases.
- **People:** one Contact Centre Supervisor on fix_real. The queue reviews, guard-rail reviews and SOD-20 all need at least two. **Name a second supervisor.**
- **Owner decision (CTO):** the shadow pass rule (no fewer answers; at most 2% changed) is a measurable floor, not a labelled accuracy comparison. With labelled live traffic it could become one.

## Pass 3 (same day): the two capture-shaped gaps pass 2 left open

The goal check pointed out that pass 2 listed open gaps. Two of them are capture work and were built. The rest need whole new engines (dialogue execution, the RAG indexer, assistant-performed actions) or are the owner's people and data (a second supervisor, intents and guard-rail settings on fix_real).

**7 Handoff Decision: Handoff Signal Phrases** (new register `fix.assistant.signal.phrase`, `models/fix_assistant_signals.py`). Pass 1 made the emotional triggers tunable, but nothing ever raised them.
- The Customer Service Manager now records what a customer says that means **distress or a safety risk, abuse, an explicit request for a human, or frustration**: page 7 has a new **Add a Handoff Signal Phrase** chip and a **Handoff Signal Phrases** list.
- **The live bot checks every customer message against the register before classifying it.**
  - On a match it hands off on the same turn through the trigger table: distress is Urgent and alerts the supervisors (BRU-CAI-06, AUT-CAI-04); an explicit request is High (BRU-CAI-07).
  - Nothing is classified or generated for that message.
  - It publishes `sentiment.detected` (spec 12.3).
  - When several signals match, the most serious one wins.
- Phrases match as **whole words** after the assistant's own normalisation, and must have at least three letters.
- A distress or explicit-request phrase is removed only by **a supervisor other than its author** (the SOD-20 pattern). Agents read the register and cannot change it.
- **Safety floor:** ten English phrases (fire, smoke, electric shock, gas leak, burning smell, personal danger, self-harm, "human agent", "real person"), installed `noupdate`. **Bengali phrases are left to a native speaker (T08).**

**9 Analytics: abandoned sessions.** A conversation the assistant took part in that the customer abandons is logged to the unresolved queue as `session_abandoned` (AUT-CAI-08). One the assistant never spoke in is not.

**Evidence (pass 3)**
- Node guard `test_m32_capture_pass3.py`: **3/3 fail on HEAD c73185f4** and pass after the change. With the pass-1/2 guards and the estate guard: 651 checks, 0 failures.
- Live `test_m32_capture_pass3_live.py` on a private clone `fix_test_m32c3`, as non-admin supervisors and agents: **7/7**. With pass 2 (9) and pass 1 (44): **60/60**.
- **Mutation check: 8/8 red**: detector off, precedence reversed, substring instead of whole-word match, author removes own distress phrase, handoff loses the signal, abandonment not logged, silent session logged, too-short phrase accepted.
- **Regression found by the suite and fixed:** the "human agent" seed phrase caught M27's explicit-request messages before the `agent.request` intent did. That changed the recorded reason (`customer_requested_agent`) and the transfer wording two existing tests rely on. The detector now keeps that reason code and uses the engine's own transfer reply (`TRANSFER_REPLY`).
- **Regression** on `fix_test_m32c3`: the `cd_contact_centre` suite with the A03 control, whitelist and registry guards and all three M32 guards. **699 passed, 9 failed, 230 skipped.**
  - 8 of the failures are the base-reproduced set from pass 2.
  - The ninth, the A03 control check on M35's `fix.campaign.spend`, fails identically from the shared checkout without the pass-3 code.
- **UI walk** on a private server (port 8175): page 7 shows **Handoff Signal Phrase**. A distress phrase was saved through the form, and a customer message containing it was handed off at once (distress, Urgent) with the transfer reply and no classification. 0 console errors, 0 server errors.

## Deploy

- **Landed** `bdee1d2e` on `fix/a03-live-data-and-pending-work` (compare-and-swap on `aec0f14e`). The shared branch and `fix/m32-capture-pass2` are both pushed.
- **Deployed (owner's "Yes, deploy", 19 Nov).** M35's combined wave upgraded both databases from the shared checkout, so I ran no `-u` of my own (two sessions upgrading the same database collide):
  - fix_real at 20:37 and fix_dev at about 20:42, covering cd_contact_centre 19.0.1.2.0 and cd_p03_portal together with M35's, M31's and M39's modules;
  - backups by that wave, e.g. `1000 fix/backups/fix_dev_pre_m38_wave_2026-11-19.dump`;
  - one restart at 20:51, once M36's cd_quotation was settled: **8069 = PID 52556 (fix_real), 8090 = PID 80704 (fix_dev)**.
- **Checked on both databases:**
  - cd_contact_centre is at 19.0.1.2.0;
  - the `fix_assistant_unresolved` table and its company rule exist;
  - the intent, guard-rail, answer and shadow columns exist (11 shadow columns);
  - every employee is now read-only on intents and RAG sources.
- **Boot:** fix_real loaded 155 modules and fix_dev 151, with no registry failure.
- **Live walk, read-only, nothing saved,** with the dev login, on 8069 and 8090:
  - all nine pages show exactly the "+" and chips in the table above;
  - the 13 new or changed screens open, among them Unresolved Questions, Guard-Rail Firings, the Knowledge Gap Report, the Intervention Log, and the shadow, review, close and send forms.
- **Errors seen during the walk, none from M32:**
  - the browser could not register Odoo's service worker on the `*.localhost` host names (a PWA issue);
  - one Postgres serialization retry on `mail_presence`.
- **What the owner should do next:**
  - **name a second Contact Centre Supervisor**: fix_real has one and fix_dev none, and the queue and guard-rail reviews and SOD-20 need two;
  - register the intents with their category and threshold;
  - set guard-rail stages.
- fix_real holds no M32 business data yet.
- **Pass 3 deploy:** pending (it needs `-u cd_contact_centre,cd_p03_portal` on both databases and a restart).
