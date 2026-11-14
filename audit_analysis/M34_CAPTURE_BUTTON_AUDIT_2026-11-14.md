# M34 CX, Feedback & Complaints: capture-button audit, second pass

**Date:** 14 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** live on 8069 since the user-approved 16:35 restart (bundle `9f9ab68`). The first pass is `M34_CAPTURE_BUTTON_AUDIT_2026-11-13.md`.

## 1. The question

The user still saw M34 sub-module pages without a relevant data-capture button after the 13 Nov pass. Which pages lack one, what does the spec say each should capture, and is what each button saves allowed by the spec's rules?

## 2. What the live pages showed before

All 8 pages were clicked on 8069 (fix_real) before any change:

| # | Sub-module | "+" button | Relevant? |
|---|---|---|---|
| 1 | Survey Design & Distribution | + New Survey Instrument | Yes (FR-CXM-001, 005) |
| 2 | CSAT / NPS / CES | + Record a Survey Response | Yes (FR-CXM-011..013) |
| 3 | Multi-Parameter Ratings | + Record a Survey Response | Yes (FR-CXM-014) |
| 4 | Closed Feedback Loop | + New Detractor Follow-up | Yes, but its close actions broke two hard rules (section 3) |
| 5 | Complaint Management | + Complaint | Yes |
| 6 | Categorisation & SLA | **none** | **No capture at all** |
| 7 | Compensation & Goodwill | + New Goodwill Credit | Yes (FR-CXM-036) |
| 8 | VoC Analytics | + New Customer Review | Yes, but the form broke a hard rule (section 3) |

## 3. Spec against code

Spec: `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M34_Customer_Experience_Feedback_and_Complaints.md`, sections 5, 9, 10.1 and 13.

**Page 6, Categorisation & SLA (FR-CXM-030/031).**
- FR-CXM-030 says complaints are categorised "using a maintained taxonomy".
- Section 10.1 names the entity `fix.complaint.taxonomy` (code, parent, English and Bengali names, default severity).
- Section 13 gives it to the Customer Service Manager (C R U D A).
- The estate had no such model: a complaint's category was a fixed six-value list. The only record on the page, the SLA binding, could be saved by an administrator only, so the first pass gave the page a chip and deliberately no "+".
- Result: nothing a person could capture from that page.

**Page 4, Closed Feedback Loop.**
- BRU-CXM-03 (hard block) says a loop case "cannot be dismissed without contact". But `action_close_unrecovered` closed an open follow-up nobody had contacted.
- BRU-CXM-04 (hard block) and FR-CXM-024 say a loop "closes only on confirmed customer acknowledgement, never on internal action alone". But `action_close_recovered` took no input and needed no prior contact.

**Page 8, VoC Analytics (reviews).**
- BRU-CXM-13 (hard block) says reviews are published only with the customer's explicit consent.
- The review form let anyone type "Published"; there was no consent field at all.
- FR-CXM-040 also asks for moderation and a reply. Neither existed.

## 4. What was changed

| # | Page | Now |
|---|---|---|
| 6 | Categorisation & SLA | **+ New Complaint Category**. The Complaint Categories list (new) and Complaint SLA Bindings list both have "+". Chips: Complaint Category, Complaint SLA Binding, Complaint. |
| 4 | Closed Feedback Loop | Mark Recovered asks what the customer said. Both closes are refused until Record Contact is done. The form shows first contact, the customer's confirmation and when it was given. |
| 8 | VoC Analytics | The review's publishing state is read-only. List actions: Record Consent (how the customer agreed, required), Publish (refused without consent), Hold Back, Reply, Withdraw Consent. |
| 5 | Complaint Management | The complaint intake names its Complaint Category. |

**Server rules (cd_cx_feedback):**
- `fix.complaint.taxonomy` (new, `models/fix_complaint_taxonomy.py`). It is a tree with a unique upper-case code and a required Bengali name (DE-17), and it refuses cycles. A sub-category carries its parent's ISO category; a mismatch is refused, and changing a parent's category moves its sub-tree and its open complaints.
- `fix.complaint.taxonomy_id`. The complaint's ISO category follows its category. The category's default severity is a **floor at intake**: the new-complaint form pre-fills "Minor", so a category that is always Major or Critical (an unsafe repair) would otherwise be filed as Minor. A chatter line records the raise. After intake the severity moves only through Assess and Reassess, as before. The category is frozen on closed or declined complaints, like the ISO category.
- Access: every internal user reads taxonomy and SLA bindings. The Contact Centre Supervisor group writes both, as do administrators. This is the group the M32 pass already uses for the Customer Service Manager's registers.
- `fix.cx.followup`:
  - `action_close_recovered(confirmation)` requires a recorded contact and stores the customer's words and time (`customer_confirmation`, `customer_confirmed_at`).
  - `action_close_unrecovered` requires a recorded contact.
  - `action_mark_contacted` stamps `contacted_at`.
- `fix.cx.review`:
  - A constraint: "published" requires consent, and consent requires recorded evidence. It holds on every route, not only the form.
  - The rating must be 1 to 5.
  - New actions: `action_record_consent`, `action_publish`, `action_flag`, `action_reply`, `action_withdraw_consent`.
  - New fields: consent, moderation and reply.

**Workspace (cd_p03_portal):**
- `m34.js`: page 6 mapping, taxonomy list and form (with a read-only sub-categories grid), review actions and read-only fields, follow-up confirmation prompt.
- `m34.py`: taxonomy surface and review actions. The Category Pareto counts by maintained category where one is set.
- `writable.py` regenerated: + `taxonomy_id` on the complaint, + the taxonomy entry, − review `state`.

## 5. Verification

| Check | Result |
|---|---|
| Guard `test_m34_capture_buttons.py` (file-level, node evaluates the engine's own `fregCreate`) | 23/23 pass. Against HEAD's code: **7 fail**, every new check. |
| Estate page standard, A03 sub-module mapping, forms-show-children, A03 registry coverage | All pass (653 + 34). |
| A03 write whitelist | Passes, except one M33 test that needs the peer session's uncommitted `fix_processing_record` table on fix_test. Not M34. |
| Live endpoint tests `test_m34_capture_live.py`, as non-admin clerk and supervisor users on private clone `fix_test_m34` | **14/14** |
| cd_cx_feedback suite + A03 control suite on the clone | 3 failures, all event-relay tests. They fail the same way as in the first pass: the clone carries 53,625 pending outbox events and the relay drains oldest first. They don't touch the changed code. |
| fix_real upgrade (`-u cd_cx_feedback`) | Exit 0. Table `fix_complaint_taxonomy` and the new columns are present. |
| 8069 after restart (pid 47000, bundle `9f9ab68`) | Clicking all 8 pages shows a "+" on each, with no errors. A server probe made 37 calls: every M34 list, report, sub-module grid and form loaded, with no dropped columns and no missing fields. The new actions are whitelisted (a dummy id answers "Record not found"; an unknown method answers "not available"). |

Not exercised on fix_real: saving a record. That would create estate data, and fix_real has no M34 rows (0 surveys, complaints, follow-ups, reviews or SLA bindings).

Not live yet: one label wording fix on the Complaint Category form ("a sub-category uses its parent's"). JS reaches the production bundle only at the next restart.

## 6. Gaps still open (need models or owner decisions)

| Spec | Missing |
|---|---|
| FR-CXM-031 | SLA by **customer tier** (the binding is by severity and branch/unit only) |
| §10.1 taxonomy `default_owner_role` | Not built. No owner-routing rule exists to apply it, so a stored role would be dead data. |
| FR-CXM-002/003/004 | Survey trigger, timing and sampling definitions |
| FR-CXM-007 | Tokenised no-login response link (every response is still keyed by staff) |
| FR-CXM-025, BRU-CXM-05 | Contact-deadline breach escalation of unclosed loops |
| FR-CXM-033 | `fix.complaint.update` (status communications) |
| FR-CXM-039/041 | Journey definitions, verbatim theme extraction |
| Roles | fix_real has **1** Contact Centre Supervisor. Only that person or an administrator can save a complaint category or SLA binding. Granting more people the role is the owner's call. |
