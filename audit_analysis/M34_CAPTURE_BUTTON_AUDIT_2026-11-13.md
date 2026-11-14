# M34 CX, Feedback & Complaints: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** fully live on 8069/8089. The JS was in production bundle `9f7bed6`; the models and controller went live with a restart at 17:45–17:46 (user approved). Nothing committed.

## 1. The question

The M34 workspace has 8 sub-module pages (Function Register, 69 functions). Not all of them showed a button that captures the right record. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M34_Customer_Experience_Feedback_and_Complaints.md` (FR-CXM-001…042, BRU-CXM-01…15, entities §10)
- `contracts/nav/registry.json` (the 8 sub-modules and their function counts)

| # | Sub-module | Spec | What a person records |
|---|---|---|---|
| 1 | Survey Design & Distribution | FR-001…010 | the survey **instrument** (questions, branching, bilingual text); the per-customer **frequency cap**. Dispatch is automatic (AUT-CXM-01) |
| 2 | CSAT / NPS / CES | FR-011…019 | the customer's **response** to a survey already raised |
| 3 | Multi-Parameter Ratings | FR-014/015 | overall, timeliness, professionalism and behaviour **per question**, on that response |
| 4 | Closed Feedback Loop | FR-020…027 | the loop case is auto-created (BRU-03); a person records **contact** and **closure** |
| 5 | Complaint Management | FR-028…038 | the complaint |
| 6 | Categorisation & SLA | FR-030/031 | the **SLA by severity / branch** a complaint buys; re-categorising an existing complaint |
| 7 | Compensation & Goodwill | FR-036 | a goodwill credit within authority |
| 8 | VoC Analytics | FR-039…042 | analytics are calculated; the one entered record is a **review / testimonial** (FR-040) |

## 3. What the code had (before)

The engine's own `fregCreate` / `fregPanels` were run over the real registry, then each page was clicked on 8069.

| # | Page | Button before | Defect |
|---|---|---|---|
| 1 | Survey Design | + New Survey | **Wrong record.** It made a response row, which the `service_order.closed` consumer raises, one per order. The instrument designer (`fix.survey.template`), its answers and the throttle rules were on **no page**, which hid the 3 instruments and 1 throttle row on fix_real. The "Survey Designer" screen was a fixed report saying *"a question designer is not built (no model for custom questions)"*, which was false. |
| 2 | CSAT / NPS / CES | + New Survey | A survey could be typed for any order, and its **state was editable**: "Sent" with nothing sent, or "Responded" with no answer. A rating entered on the form left the survey "sent", so it was **outside every CSAT/NPS figure**, because those count responded surveys only. |
| 3 | Multi-Parameter Ratings | + New Customer Review | **Wrong record.** That is an external Google or Facebook review. The per-question answers were on no page, and the survey's answer grid keyed `question_code` (a related field) instead of the question, so **no answer could ever be saved**. |
| 4 | Closed Feedback Loop | + New Detractor Follow-up | Button correct. But "Customer Contacted" and "Closed — no recovery" had no action: the only way to reach them was typing the state on the form. |
| 5 | Complaint Management | + Complaint | Correct. |
| 6 | Categorisation & SLA | + New Complaint | **Wrong record.** The complaint SLA binding (`fix.complaint.sla.rule`: severity × branch/unit → SLA policy) had no screen anywhere. |
| 7 | Compensation & Goodwill | + New Goodwill Credit | Correct. |
| 8 | VoC Analytics | **nothing** | Reviews (FR-040) and Experience by Branch were on no page. |

Two more defects were in the forms:

- On the instrument form, `state` was editable. Typing "Published" skipped `action_publish`'s Bengali-text check (DE-17) and the freeze.
- On the follow-up form, `state` was editable.

## 4. What was changed

| # | Page | Capture now |
|---|---|---|
| 1 | Survey Design | **+ New Survey Instrument**; chips Survey Instrument and **Distribution Throttle**. The Instruments list, the **Survey Designer** (now the question bank of every instrument) and Distribution & Throttling are on the page. |
| 2 | CSAT / NPS / CES | **+ Record a Survey Response**. Step 1 picks a pending or sent survey; step 2 takes the instrument, overall rating, comment and per-question answers. State, order, customer and unit are read-only. |
| 3 | Multi-Parameter Ratings | **+ Record a Survey Response** (the answers grid); the Collected Answers list; chip Survey Instrument (where the parameters are defined). |
| 4 | Closed Feedback Loop | Unchanged button. The list adds **Record Contact** (what was said, required) and **Close (Not Recovered)** (reason required). State is read-only on the form. |
| 5 | Complaint Management | Unchanged. |
| 6 | Categorisation & SLA | Page reads **Complaint SLA Bindings**, with the **Complaint SLA Binding** chip. Only an administrator can save one (model ACL), so it has no "+ New" that would be refused. Complaints list (with Reassess) added. |
| 7 | Compensation & Goodwill | Unchanged. |
| 8 | VoC Analytics | **+ New Customer Review**; Reviews & Testimonials and Experience by Branch/Tech lists added. |

Server rules added, so the new capture cannot write a misleading score:

- `fix.survey.write`: writing a rating or answers on a pending or sent survey makes it **Responded**. It also logs who keyed it on the survey's chatter (BRU-CXM-15 provenance) and raises the detractor follow-up for an NPS answer as well as a low rating.
- `fix.survey.answer` constraint: the question must belong to the survey's instrument, and the value must fit its scale (as `record_answers()` always checked). A scored question with no score is refused, because it would otherwise be stored as NPS 0, the strongest detractor.
- `fix.cx.followup.action_mark_contacted` / `action_close_unrecovered`: both are whitelisted in `controllers/a03/m34.py`.
- `fix.complaint.sla.rule` is served as a workspace surface.
- The stale "Survey Designer" report text was corrected.

### Files

- `addons/platform/cd_p03_portal/static/src/a03/m34.js`: mappings, screens, forms, chips
- `addons/platform/cd_p03_portal/controllers/a03/m34.py`: SLA surface, follow-up actions, report note
- `addons/platform/cd_p03_portal/controllers/a03/writable.py`: regenerated (`form_fields.py --a03`). Survey: +template_id, −state/order/unit/customer. Instrument: −state and counts. Follow-up: −state. New SLA binding entry.
- `addons/domain/b_customer_engagement/cd_cx_feedback/models/fix_survey_designer.py`, `fix_cx_selfservice.py`
- Tests (new): `cd_p03_portal/tests/test_m34_capture_buttons.py` (19, file-only; **10 fail on HEAD**) and `test_m34_capture_live.py` (9, through the endpoints as a non-admin clerk)

## 5. Verification

- Guard 19/19, plus estate standard, A03 mapping and registry coverage: **659 passed**.
- Live endpoint tests on a private clone `fix_test_m34`: **9/9**. The clone was brought up to the working tree's cd_billing_engine and cd_quotation schema, because shared fix_test lacks a peer's `res_partner.fix_po_currency_id`.
- A03 whitelist, control suite, and the cd_cx_feedback suite on the clone: **127 passed, 3 failed, 162 skipped**.
  - The 3 failures are event-relay tests (`closed order event produces the survey`, `post-closure survey sent`, `escalation notifies tier 4`). The clone carries a backlog of 53,621 pending outbox events and the relay drains the oldest first. None of these tests touches the changed code; the rating → follow-up test that does, passes.
- Live on 8069:
  - The production bundle `9f7bed6` contains the change.
  - A server probe posted every M34 page grid, list, form and report: 0 errors and 0 dropped columns. The one exception is `fix.complaint.sla.rule`, "not served" until a restart.
  - Clicking all 8 pages shows the buttons in section 4.
  - "Record a Survey Response" opens its pick step with "No survey is waiting for an answer" (fix_real has 0 surveys and 0 service orders).

**Until 8069/8089 restart:**

- the Categorisation & SLA grid and its list show "Model not served";
- Record Contact and Close (Not Recovered) are refused as "not available";
- a recorded rating does not yet move the survey to Responded.

A schema check on fix_real found every peer column or table changed since the 16:13 start already present, so a restart is schema-safe.

**After the restart** (8089 pid 55512, 8069 pid 54384, both `-d fix_real`), the same probe made **35 calls with 0 errors**:

- the SLA-binding list is served;
- `action_mark_contacted` and `action_close_unrecovered` are accepted (they answer "Record not found" for a dummy id, not "not available");
- page 6 shows Complaint SLA Bindings with both chips.

Not exercised on fix_real: saving. It would create estate data, and there are no surveys or complaints to act on.

## 6. Gaps the spec asks for and the estate does not have

| Spec | Missing |
|---|---|
| FR-007 / T-05 / AC-09 | **No customer response link** (tokenised, no login). Every response today is keyed by staff. |
| FR-002/003/004 | Trigger and timing definitions, and sampling. The survey always goes on order close, to every customer. |
| FR-009/019, BRU-11, AC-10 | Response provenance fields and anomaly detection (only a chatter line now) |
| FR-022/024/025, BRU-04/05 | Contact deadline clock, escalation of unclosed loops, and closure on *customer confirmation* (Mark Recovered asks for none) |
| FR-030 | Maintained complaint taxonomy (`fix.complaint.taxonomy`). The category is a fixed selection. |
| FR-033 | Complaint status updates entity (`fix.complaint.update`) |
| FR-039/041 | Journey definitions, verbatim theme extraction |
| FR-040, BRU-13 | Review publication consent and reply |
