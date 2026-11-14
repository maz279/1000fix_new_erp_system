# M36 Quotations & Tenders — Sub-module Capture Audit (2026-11-14)

**Question.** The user saw M36 sub-module pages without a relevant data-capture button.

**Sources compared.**
- Spec: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M36_Quotation_Estimation_and_Tender_Management.md`
  - §3.1 scope, §5 FR-QTE-001..048, §6 T-01..T-15, §8 lifecycle and transition guards, §9 BRU-QTE-01..18, §10.1 owned entities, §11 automations.
- Code (HEAD `f6fc66cc`):
  - `cd_quotation` (models), `cd_service_order` (the M01 estimate);
  - `cd_p03_portal/static/src/a04/m36.js` (the workspace), `controllers/a04/m36.py` (surfaces, reports).
- Data: fix_real has **0** M36 business rows (estimates, quotations, reviews, tenders, bonds, variations) and 4 quotation templates. No live record is affected by the changes.

## 1. Findings: what each page captured, against what the spec says it should

The Function Register gives M36 ten sub-module pages. The guard test `test_m36_capture_buttons.py` evaluates them with the engine's own `fregCreate`/`fregPanels`. On HEAD, **28 of its 45 checks fail**.

| # | Page | "+ New" on HEAD | What the spec says the page captures | Verdict |
|---|---|---|---|---|
| 1 | Estimate Build-Up | **none** (chip only) | The estimate and its lines (FR-QTE-001..010) | **No button.** The page's list said `create: false`. |
| 2 | Quotation Object | + Quotation | The versioned customer quotation (FR-QTE-011..024) | OK |
| 3 | Versioning | **none** | A new version of an issued, expired or declined quotation; never an edit (FR-QTE-012/015, BRU-QTE-02/04) | **No capture.** Revise was only a row action on another page. |
| 4 | Approval Routing | **none** | Submission to the value-band approver (FR-QTE-025..032) | **No capture.** It listed the review log, which the system writes. |
| 5 | Customer Approval Loop (8 channels) | **none** | Issue on a channel; delivery and view tracking; acceptance by code (FR-QTE-033/034/039/042, entity `fix.quotation.delivery`) | **No capture, and the data could not exist.** No quotation recorded the channel it reached the customer on. The page listed the internal review log, the same list as page 4. "Quote Conversion by Channel" grouped by state. |
| 6 | Partial Accept & Counter | **none** | The customer's counter-offer and line-level partial acceptance, routed to an authority (FR-QTE-035/036, BRU-QTE-11, T-03, AUT-QTE-08) | **No capture, and no record existed.** The only "Counter-Offer" form was M04's walk-in counter **sale** (`fix.counter.sale`) under the wrong title. |
| 7 | e-Signature | **none** | Signed acceptance with its evidence pack (FR-QTE-037/038) | **No capture.** The signed copy had to be attached on the full quotation form, then a row action clicked. |
| 8 | Declined Handling | **none** | The decline with a governed reason; the diagnostic fee and the return task (FR-QTE-041, BRU-QTE-12/16, AUT-QTE-09) | **No capture.** A decline published `quotation.declined`, and **nothing consumes it**, so no return task and no fee were raised. |
| 9 | Tender & Bid | **none** (chip only) | Tender register, bid bonds, compliance, variation orders (FR-QTE-043..048) | **No button.** The list said `create: false`. Bid Bond and Variation Order had no chip. The variation list sat on no page. The compliance report sat on page 10. |
| 10 | Templates & Bilingual Gen | **none** | Quotation templates and the bilingual document templates (FR-QTE-008/018/019) | **No capture.** The page named `fix.document.template` as its record but listed none of them. |

**Found on the way:**

- A wrong acceptance code answered `{verified: false}` with success, so the workspace would have shown "Saved".
- The estimate-based quotation's value is pinned to the M01 estimate (`_check_value_matches_estimate`). A customer change to a repair quotation must therefore go to the estimate, not to the quotation. The counter-offer record refuses such quotations and says so.

## 2. What was built

### Models: `cd_quotation/models/fix_quote_with_customer.py` (cd_quotation 19.0.1.1.0)

- **`fix.quotation.delivery`** (spec entity of the same name).
  - Fields: quotation, version (stamped), one of the 8 channels, recipient, delivery ref, sent / delivered / first viewed, views, who recorded it.
  - Recorded only for a quotation with the customer.
  - The recipient defaults from the customer: mobile for SMS, WhatsApp or phone; email for email.
  - What was sent, when, how and to whom is fixed once recorded. Only delivery, views and the note change. Views never go down.
  - Staff cannot delete a delivery.
- **`fix.quotation.counter`** and **`fix.quotation.counter.line`**: the customer's counter-offer or partial acceptance.
  - Fields: channel, the request in writing, an optional proposed price, and the call or message evidence.
  - A partial acceptance is pre-filled with one decision per priced line.
  - It is decided by **someone other than whoever took it down**.
    - **Revise** makes the next draft version: declined lines removed, the proposed price applied as the overall discount. That version then takes the value-band approval and is issued and accepted like any other (T-03).
    - **Reject** needs a reason.
  - One open counter per quotation. A decided counter is frozen.
- **`fix.quotation` extensions** (none adds a column):
  - `action_issue_on_channel(channel, recipient, delivery_ref)` issues and records the delivery.
  - `action_record_signed_acceptance(attachment_id)` takes the upload, which must be the caller's own.
  - A wrong code returns a warning.
  - On a decline, the service order gets a "return or collect the device" to-do with the diagnostic fee owed (BRU-QTE-12).
  - Derived fields: first delivery channel, delivery count, first viewed, diagnostic fee due.
- `fix.quotation.line` is named by its description. It showed as "fix.quotation.line,440".
- **Security.** Staff read the new records. Quotation Authors record them; Commercial Managers alone delete. Company and operating-unit rules were regenerated.

### Workspace: `m36.js`, `controllers/a04/m36.py`, `controllers/a04/writable.py` (regenerated)

| # | Page | "+ New" now | Chips now |
|---|---|---|---|
| 1 | Estimate Build-Up | **+ New Estimate** | Estimate |
| 2 | Quotation Object | + Quotation | Quotation (versioned) |
| 3 | Versioning | **+ Revise a Quotation (new version)** (pick issued / expired / declined) | Revise a Quotation |
| 4 | Approval Routing | **+ Submit a Quotation for Approval** (pick a draft, justification) | Submit; new list "Drafts Awaiting Approval" |
| 5 | Customer Approval Loop | **+ Issue a Quotation to the Customer** (pick approved, choose channel) | Issue, **Record a Delivery / Re-send**, **Accept by Customer Code**; the loop list is now the quotations with the customer, plus "Deliveries & Views" |
| 6 | Partial Accept & Counter | **+ Record a Counter-Offer / Partial Acceptance** | Counter-Offer, **Decide a Counter-Offer**; list "Counter-Offers & Partial Acceptance" |
| 7 | e-Signature | **+ Record a Signed Acceptance** (upload the signed copy) | Signed Acceptance, Accept by Customer Code |
| 8 | Declined Handling | **+ Record a Customer Decline** (governed reason + what the customer said) | Record a Customer Decline |
| 9 | Tender & Bid | **+ New Public / Institutional Tender Bid** | Tender Bid, **Bid Bond**, **Variation Order**; the compliance matrix and variation list moved here |
| 10 | Templates & Bilingual Gen | **+ New Quotation Template** | Quotation Template, **Document Template (bilingual)** (M24's form); list "Bilingual Document Templates" |

Other changes:

- "Quote Conversion by Channel" now groups by the first delivery channel. It shows issued, viewed, accepted, declined, expired and with-customer counts, plus conversion = accepted / decided.
- M04's counter-sale form is retitled "Counter Sale (walk-in, M04)".

## 3. Evidence

- **Guard test** `cd_p03_portal/tests/test_m36_capture_buttons.py` (node evaluates the real registry): **28/45 fail on HEAD; 45/45 pass** on the build.
- **Live test** `cd_quotation/tests/test_m36_capture_live.py`: 13 tests run as non-admin role holders through the workspace endpoints, on `fix_test_m36`. **13/13 pass.**
- **Mutation check: 9/9 mutants caught**, each by the test aimed at it:
  - counter SoD;
  - declined lines dropped;
  - delivery on issue;
  - full-form save is no edit;
  - decline follow-up;
  - wrong-code warning;
  - delivery frozen;
  - caller's own upload;
  - price as discount.
- **Regression on `fix_test_m36`: 1,034 passed, 1 failed, 0 skipped.**
  - Covered: the cd_quotation full suite, the M36 guard, the estate page standard, sub-module mapping, the create-button rules, A04 registry coverage, the A04 write whitelist, screens wiring, report export, declared gaps and tell-me.
  - The one failure, `test_no_submodule_page_offers_another_records_button`, flags M30/1 "Branch Master". It is not M36 and fails the same way without this change.
- **UI on a private server** (port 8097, worktree code, `fix_test_m36`):
  - All 10 pages show the button and chips in the table above.
  - **Issue:** picked the approved quotation, chose WhatsApp from the 8 channels, pressed Issue. The toast confirmed it, and the loop list shows "First Delivered By: WhatsApp".
  - **Partial acceptance:**
    - Recorded on the issued quotation. The line decisions were pre-filled with its two lines, by name, with no add or remove.
    - Declined one line and saved. Accepted lines went from 12,000 to 9,000.
    - "Decide a Counter-Offer" by the same user was refused on screen: "Segregation of duties: whoever took the counter-offer down does not decide it."
- **Two defects found only by the UI walk, both fixed and covered by a test:**
  - The form re-sends every field it shows, so the freeze refused unchanged fields. It now refuses only real changes.
  - Quoted lines showed as "fix.quotation.line,440"; they now show their description.
- **One defect found only after ruff ran:**
  - Ruff re-sorted `models/__init__.py`, so a file named `fix_quote_loop` loaded before the model it extends, and every DB test silently skipped. The file is now `fix_quote_with_customer.py`.
  - The issue step is its own method (`action_issue_on_channel`). The tender lock overrides `action_send` without arguments.

## 4. Left for the owner (not buildable without a decision)

1. **The diagnostic fee is a task, not an invoice.** A decline now raises the "return or collect the device" to-do with the fee owed. Invoicing it follows the M20 fee policy, which is not defined. The KPI "Declined → Diagnostic Fee" stays a declared gap until it is.
2. **Terms deviation approval (FR-QTE-018/027, BRU-QTE-08: CCO + CFO).** Templates carry the standard terms, but no record says that a term deviates from them, and nothing routes such a term to the CCO and CFO. This needs the governed terms library (`fix.quotation.term`) and the CCO/CFO approver roles to be named.
3. **Tender document checklist (FR-QTE-046, `fix.tender.document`).** The compliance matrix carries an evidence reference per requirement. A separate, versioned submission-pack register is not built.
4. **Tokenised customer view (T-05, FR-QTE-034).** View tracking is recorded by staff. The customer-facing one-tap approval page, which would record views itself, is a portal build.
5. **Who records and decides.** Every new capture needs the Quotation Author role (`cd_quotation.group_quotation_user`).
   - fix_real has 220 Quotation Authors and 47 Commercial Managers, so counter-offers can be taken down by one person and decided by another.
   - fix_real has **1 Bid Coordinator and 1 Tender Committee member**. A tender award must be approved by a committee member who did not prepare the bid, so a second member must be named before any tender can be won in the system.

## 5. Deployed to fix_real (14 Nov 2026, approved by the user)

- Committed `9c0c90a3` on `fix/a03-live-data-and-pending-work` (fast-forward from `f6fc66cc`; **not pushed**). Peers' uncommitted M33 files in the shared checkout were left as they were.
- Backup: `_migration/backups/fix_real_pre_m36_capture_2026-11-14.dump` (48.6 MB, 1,563 tables).
- `-u cd_quotation,cd_p03_portal` on fix_real: 0 errors. The 3 new tables exist; cd_quotation is at 19.0.1.1.0.
- Drift check before the restart: no stored field in the shared checkout's changed model files lacks a column.
- 8069 restarted at 17:59 machine time. One listener; `/web/login` answers 200; 0 errors in the log since.
- **Server probe on fix_real**, as a real non-admin Quotation Author, read-only and rolled back: every M36 list, form, pick list, report and sub-module grid. **64 calls, 0 errors.**
- The production bundle `e69602d` served by 8069 contains the new screens (`action_issue_on_channel`, the counter-offer forms, the bilingual template list).
- Not checked by clicking on fix_real: signing in there needs a real account. The clicks were done on the private copy (section 3).
