# M34 CX, Feedback & Complaints: capture-button audit, third pass

**Date:** 19 Nov 2026 · **Estate:** fix_real on 8069, fix_dev on 8090 · **Branch:** `fix/m34-capture-pass3`
Earlier passes: `M34_CAPTURE_BUTTON_AUDIT_2026-11-13.md` (wrong captures on 4 pages) and `M34_CAPTURE_BUTTON_AUDIT_2026-11-14.md` (page 6 had no "+", three hard rules broken).

## 1. The question

The user still saw M34 sub-module pages without a relevant data-capture button. After the 14 Nov pass every page had a "+", so this pass asks the stricter question: **for each page, which records does the spec say are captured there, and can anyone capture them?**

Spec: `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M34_Customer_Experience_Feedback_and_Complaints.md`, sections 5 (FR-CXM-001..042), 9 (BRU-CXM-01..15), 10.1 (16 owned entities), 11 (AUT-CXM-01..14) and 13 (roles, SOD-21/22).

## 2. What each page could capture before this pass

Evaluated from the registry the browser runs (the engine's own `fregCreate` / `fregPanels` over `m34.js`) and the models in `cd_cx_feedback` at `742e46bc`.

| # | Page | Its "+" and chips | Spec records with no capture anywhere |
|---|---|---|---|
| 1 | Survey Design & Distribution | Survey Instrument, Distribution Throttle | **`fix.survey.trigger`**: trigger event, delay, sampling rate, eligibility (FR-002/003/004, AUT-01). Every closed order was surveyed at once, on no instrument. |
| 2 | CSAT / NPS / CES | Record a Survey Response | **Provenance** (FR-009, **BRU-15 hard block**): how, when, from what device. Only a chatter line said who keyed it. **Attribution** (FR-016, **BRU-10 hard block**): branch, technician, service type at capture. The survey held the operating unit only; the CSAT report called technician CSAT a "declared gap". **`fix.response.anomaly`** (FR-019, **BRU-11 hard block**, AUT-11, SOD-21): no way to flag manipulation, and M57 read every rating into incentives. |
| 3 | Multi-Parameter Ratings | Record a Survey Response (the same "+" as page 2) | **`fix.rating`** for a conversation (FR-015): M27 sends a CSAT invitation when a conversation ends, but nothing could record the score. |
| 4 | Closed Feedback Loop | Detractor Follow-up | **Contact deadline and escalation** (FR-022/025, **BRU-05 hard block**, AUT-04): the follow-up had a 2-day due date and no contact window, and no job escalated an uncontacted detractor. |
| 5 | Complaint Management | Complaint | **`fix.complaint.update`** (FR-033, **BRU-07 hard block**, AUT-08): no record of what the customer was told after the acknowledgement. **Intake channel** (FR-028): a complaint keyed by staff was always "Entered by Staff", whether it came by counter, letter or social media. **Regulator / brand-partner referral** (FR-038): no referring body or reference. |
| 6 | Categorisation & SLA | Complaint Category, Complaint SLA Binding | **SLA by customer tier** (FR-031): bindings were by severity, branch and unit only. |
| 7 | Compensation & Goodwill | Goodwill Credit | None missing at page level (see section 6). |
| 8 | VoC Analytics | Customer Review | **`fix.journey.definition` / measurement** (FR-039) and **`fix.voc.theme`** (FR-041). The "Journey Measurement" report counted orders, surveys and complaints by month; no journey or stage existed. |

## 3. What was built

### Server (`cd_cx_feedback` 19.0.1.1.0, `models/fix_cx_capture3.py`, imported last)

| Record / rule | What it does |
|---|---|
| `fix.survey.trigger` (new) | Event (service order closed), published instrument, delay in minutes, sample %, optional branch and service type. `consume_order_closed` applies the most specific active trigger. The sample is a fixed SHA-256 hash of trigger code + order, so it is repeatable and nobody can steer which customers are asked. An unsampled order gets a survey in the new state **Not Sampled** with the reason (AUT-01 "log as not surveyed with reason"), cannot be answered, and is left out of every response-rate denominator. A delayed invitation waits for a new 15-minute cron. With no trigger the old behaviour is unchanged. Written by the Contact Centre Supervisor group and administrators. |
| Response provenance on `fix.survey` | `response_channel` (phone, counter, technician visit, SMS reply, WhatsApp, e-mail, IVR, link, app, system), `response_device`, `responded_at`, `response_recorded_by_id`. Recording a rating or answers **without the channel is refused** on every route (form, `write`, `create`, `record_answers`). The channel of a recorded response cannot be changed. |
| Attribution on `fix.survey` | `branch_id`, `technician_id`, `service_type` copied from the order when the survey is raised, and **frozen**. Reassigning the order later does not move the score. |
| `fix.cx.response.anomaly` (new) | Detection type, one subject (technician, branch or the person keying responses), period, evidence. Raising one holds every response in scope and period (and any that arrive later) out of incentives: `incentive_excluded`. Start Investigation → Clear (released) or Uphold (stays out). State and decision fields are guarded. **SOD-21:** the subject cannot raise, investigate or decide it. Raised and decided by supervisors and administrators; never deleted. |
| M57 feed (`cd_performance`) | The scorecard CSAT now leaves out `incentive_excluded` responses and says how many it held back. |
| `fix.cx.rating` (new) | Conversation rating: overall (required), timeliness, professionalism, behaviour, comment, channel. Agent, customer, conversation channel and unit come from the conversation, never typed. Only an ended conversation is rated, once. The rating cannot be edited. **Overall ≤ 3 opens a detractor follow-up** (BRU-03). |
| `fix.cx.followup` | Can come from a survey or a conversation rating (exactly one). `contact_due` = creation + 24 h (parameter `cd_cx_feedback.loop_contact_hours`). A new hourly cron escalates an uncontacted case to the branch manager, then after another window to the operations director (`cd_cx_feedback.loop_escalation_user`, else the complaint escalation user, else the first DOFA Tier 4 holder). Each step leaves a to-do, a note and a `cx.loop_escalated` event. Raise Complaint from a rating-born case files a contact-centre complaint. |
| `fix.complaint.update` (new) | Type (acknowledgement, progress, delay, information needed, resolution proposed, reopened, closure), channel, content. SMS, e-mail and WhatsApp are queued on the S1 delivery service (consent and the BTRC window apply; a refusal is recorded as Not Sent with the reason). A call, letter or visit is recorded as made. Not editable. A closed complaint takes only a closure notice. The complaint shows `update_count` and `last_update_at`. |
| Complaint intake | `received_via` (counter, phone, e-mail, letter, social, regulator, brand partner) sets the guarded `intake_channel` at intake and is frozen. A regulator or brand-partner complaint must name the body and its reference; `external_response_due` records their deadline. |
| Tiered SLA | `fix.complaint.sla.rule.loyalty_tier_id`. Within each scope (branch, unit, default) a binding for the customer's active membership tier wins over the tier-less one; another tier's binding never applies. |
| `fix.journey.definition` + `fix.journey.stage` (new) | Bilingual journey, ordered stages, each with a touchpoint and the instrument that measures it, plus an optional effort question that must exist on that instrument. Journey Measurement now scores every stage from its instrument's responses. |
| `fix.voc.theme` (new) | Month, bilingual theme, sentiment, operational driver, the survey verbatims and complaints coded to it. The frequency is counted, never typed; a response with no comment cannot be coded. Shown in VoC Analytics. |

### Workspace (`cd_p03_portal`)

| # | Page | Now |
|---|---|---|
| 1 | Survey Design & Distribution | + chip **Survey Trigger**; list *Survey Triggers & Sampling* |
| 2 | CSAT / NPS / CES | Record a Survey Response asks **Received Through** (required) and the number/device; the details tab shows the frozen branch and technician, who recorded it and whether it is held. + chip **Response Anomaly**; list *Response Anomalies* with Start Investigation / Clear / Uphold |
| 3 | Multi-Parameter Ratings | "+" is now **Record a Conversation Rating**; Survey stays as a chip; list *Conversation Ratings* |
| 4 | Closed Feedback Loop | Contact-by deadline and escalation level/person on the list and form |
| 5 | Complaint Management | + chip **Customer Update** (list *Customer Updates*); the complaint form takes *Received Via*, a new *External Referral* tab and a *Customer Updates* tab listing what the customer was told |
| 6 | Categorisation & SLA | SLA binding takes a **Customer Tier** |
| 8 | VoC Analytics | + chips **Customer Journey** and **VoC Theme**; lists *Customer Journeys* and *VoC Themes* |

Reports: CSAT by Branch & Technician now groups by technician; Experience by Branch and the response-rate KPI count only surveys that were asked; Journey Measurement adds per-stage scores; VoC Analytics adds coded themes.
`writable.py` regenerated; isolation rules regenerated for `cd_cx_feedback` only.

## 4. Verification

All on the private clone `fix_test_m34c3` (a pg_dump of fix_real; fix_real and fix_dev differed from this code only by `cd_cx_feedback`), upgraded with `-u cd_cx_feedback` (exit 0, no errors, 7 new tables).

| Check | Result |
|---|---|
| File-level guard `test_m34_capture_buttons.py` (node evaluates the engine's own `fregCreate` / `fregPanels`) | **44/44** pass. With HEAD's `m34.js`, `m34.py` and ACL file swapped back in: **22 fail**, every third-pass check. |
| Model tests `cd_cx_feedback/tests/test_m34_capture_pass3.py`, as non-admin agents and supervisors | **33/33** (every rule both ways, plus the M57 feed). |
| Endpoint tests `test_m34_capture_live.py` (+9 third-pass cases: every new and changed list served with no dropped column, saves as clerk vs supervisor, typed state refused, actions) | all pass |
| Mutation check: 26 mutants, each removing one rule (channel required/frozen, attribution, sampling, delay, SOD on raise/act, hold/release/late join, rating loop/open conversation/edit, both escalation steps, update closed/edit/queue, intake set/frozen, referral, tier filter/preference, theme verbatims, journey question, M57 exclusion) | **26/26 killed** |
| Regression on the clone: cd_cx_feedback, cd_performance, every `test_a03_*` guard, M34, estate pages, picker, KPI tiles (1,289 tests) | 10 failures. 3 were this change's (an M34 live test without a channel; the children guard did not know the engine's `grids:` and my journey grid's closing brace) and are fixed: re-run 117/117. The other **7 fail identically with HEAD code on the same clone** (fix_real data: an existing entity for company 1 breaks 5 M57 fixtures; a real Tier-4 holder; an M28 connector in the routed-approval sweep). |
| Headless UI walk on a private server (port 8134) | All 8 sub-module pages open; each shows its "+" and the new chips (page 3's "+" now reads *Record a Conversation Rating*). 22 lists, forms and reports opened with **0 console errors** and no "not served" / unknown-field text. A **VoC Theme was saved through the form** and read back (coded by the signed-in user, frequency 0). |

The existing tests and the A03 seed that recorded a survey rating with no channel were updated to say how it arrived: the new hard rule applies to them too.

## 5. Still open

| Spec | Missing | Why not built here |
|---|---|---|
| FR-CXM-002 | Triggers for device collection, conversation close, complaint resolution, contract renewal, membership anniversary | Only the service-order-closed consumer creates `fix.survey`; the conversation CSAT is sent by M27 and the post-complaint check is an event. A trigger naming those would be configuration nothing reads. |
| FR-CXM-007 | A tokenised, no-login response link | A public route and its abuse controls are a portal piece of their own. |
| FR-CXM-010 / AUT-02 | One reminder for unanswered surveys | Automation, no capture. |
| FR-CXM-019 | Automatic anomaly detection | Anomalies are raised by a person from evidence; the detector is an M26 model. |
| FR-CXM-027 / AUT-10 | Promoter review/referral invitation | P2. |
| FR-CXM-035 | A separate remedy record per offer (`fix.complaint.remedy`) | The complaint's concession, DOFA approval and the customer's accept/reject already record one remedy per response. |
| FR-CXM-041 | Theme extraction by a model | Themes are coded by the Customer Service Manager until M26 supplies one. |
| Roles | fix_real has 1 Contact Centre Supervisor. Only that person or an administrator can save a trigger, anomaly, journey or theme. | Granting the role is the owner's call. |
