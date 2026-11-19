# M33 Customer & Party Master: sub-module capture audit, pass 2

**Date:** 19 Nov 2026 · **Area:** A03 · **Workspace fragment:** `cd_p03_portal/static/src/a03/m33.js`
**Backend:** `cd_party_master` 19.0.1.6.0, `cd_billing_engine` 19.0.2.6.0 (credit limit), `cd_p03_portal` (surfaces, write whitelist, AR credit table)
**Pass 1:** `M33_CAPTURE_BUTTON_AUDIT_2026-11-14.md` (commit 54dd2ae3). Its 43-check guard still passes on HEAD 742e46bc.

The user again saw M33 pages without a relevant capture.
Pass 1 gave every page a button, and its own guard still holds. So this pass read each page against the spec's FRs, business rules and section 10.1 entities, not against a button count.
Five pages still could not capture a record the spec names there. For one of those records, the model did not exist anywhere in the estate.

## What the spec asks, and what HEAD could capture

Spec: `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md`.

| # | Page | Spec record | On HEAD 742e46bc |
|---|---|---|---|
| 1, 5 | Party Record & Roles; Identity & OTP | **Contact point** (10.1 `fix.contact.point`; FR-CPM-022 P0; BRU-CPM-01 H; KPI-125) | **No model.** An OTP log line was tied to no phone or email, so nothing could show which contact was verified. BRU-CPM-01 ("activation needs a verified contact point") was enforced nowhere. |
| 1, 3 | Party Record & Roles; Account Hierarchy | **Party relationship** (10.1 `fix.party.relationship`; FR-CPM-006): employer, guardian, referrer, group member, authorised representative | **No model.** The hierarchy holds household, corporate, guarantor and care-of links only. |
| 3 | Account Hierarchy | **Corporate contact roles** (FR-CPM-009 P1) and **delegated administration within 1000FiX limits** (FR-CPM-011 P1) | **No model and no limit.** |
| 9 | Consent & DSR | **Minor / assisted-consent party** (FR-CPM-052; BRU-CPM-16 H) | **No flag.** A consent could not record who gave it on a minor's behalf. |
| 9 | Consent & DSR | Rectification notified within 30 days (BRU-CPM-10 H) | `notified_at` was a field nothing read. A rectification closed without the party being told. |
| 11 | Credit Profile | **Approval-controlled limit change with history** (FR-CPM-047; BRU-CPM-12 H; SOD-04) | `credit_limit` was a plain field. It was typed on the M33/M20 form and on the AR credit table's inline box, with no approval and no requester. |
| 5 | Identity & OTP (form) | Scans stored in M24 under residency control (FR-CPM-024) | The form's "Scans & Evidence" tab promised an upload with a checksum, but it had no field. |
| 11 | Credit Profile (form) | — | The form note claimed "limits above BDT 500,000 need Head of Commercial DOFA authorization". No such rule existed. |

## What was built

**`cd_party_master` (`models/fix_party_capture2.py`, imported last):**

- **`fix.contact.point`**
  - Fields: party, type (mobile / email / WhatsApp / landline), value, primary flag.
  - A mobile is normalised (`+880 1711-…` becomes `01711…`) and must be 013–019 plus 8 digits. An email is validated.
  - One primary per type per party, and no duplicate value.
  - **Verification is never typed.** "Send Verification Code" opens an OTP log line carrying the masked destination and the contact point. When the channel marks that line verified, the contact is stamped verified (method OTP, time, log).
  - Changing a verified contact makes it unverified again (FR-CPM-022, "on any change").
- **BRU-CPM-01:** `cd_party_master.require_verified_contact` (default `0`). When it is `1`, reactivating a draft party needs a verified contact point or OTP. **It is off**: fix_real holds no verified contact, so switching it on stops every activation. That is the owner's call.
- **`fix.party.relationship`**
  - Party A *is employer of / guardian of / referred / has as group member / is authorised representative of* Party B, with dates and evidence.
  - **A data steward who did not record it** verifies it against the evidence.
  - A verified link cannot be re-pointed. It is ended with a reason, never deleted.
- **`fix.party.contact.role`**
  - Fields: corporate account (company, dealer, corporate or government), person, role (authorised requester / approver / billing / technical / corporate administrator), approval limit (approvers only).
  - Suspend, reinstate and remove need a reason. Removed roles are kept.
  - **`res.partner.delegated_contact_limit`** is set only by a 1000FiX registration administrator. Granting or reinstating past the limit is refused.
- **`res.partner.consent_handling`** (standard / minor / needs assisted consent) and its reason. Guarded.
  - `action_set_consent_handling`: anyone serving the party may raise the flag. Only the DPO clears it.
  - **`fix.consent.assisted_by_id`:** a granted consent for a flagged party is refused unless it names a **verified, open** guardian or authorised-representative relationship to the party. A withdrawal carries the helper over. The field is locked once captured.
- `fix.rights.request.action_fulfil`: a rectification is refused until `notified_at` is recorded (BRU-CPM-10).

**`cd_billing_engine` (`models/fix_credit_limit_change.py`):**

- **`fix.credit.limit.change`**
  - Fields: profile, limit when requested (snapshot), proposed limit, reason.
  - Approved or rejected by an **Accounting Administrator who did not request it** (SOD-04). A rejection needs a reason.
  - Approval applies the limit at once and logs it on the profile.
  - The request is refused if the limit has moved since it was raised. Only one open request per profile. Only the requester withdraws it.
- **`fix.credit.profile`**
  - The limit can no longer be typed: a write that changes it is refused outside an approved change.
  - A new profile starts at 0 (the superuser excepted, for migration and seeding).
  - Posting the unchanged limit with new terms still saves, which is what the AR table does.
  - The profile shows its customer's name in pickers. It was `fix.credit.profile,7`.

**Workspace (`m33.js`, `controllers/a03/m33.py`, `writable.py` regenerated):**

| Page | New captures (chips) | New register on the page |
|---|---|---|
| 1 Party Record & Roles | Contact Point, Party Relationship | Contact Points, Party Relationships |
| 3 Account Hierarchy | Corporate Contact Role, Corporate Contact Limit (pick form), Party Relationship | Corporate Contact Roles, Party Relationships |
| 5 Identity & OTP | Contact Point | Contact Points |
| 9 Consent & DSR | Consent Handling (pick form, runs `action_set_consent_handling`); the consent form gains "Given By" | — |
| 11 Credit Profile | Credit Limit Change | Credit Limit Changes; the credit form shows its change history as a read-only grid |

List actions:
- Send Verification Code.
- Verify and End Relationship.
- Suspend, Reinstate and Remove.
- Approve, Reject and Withdraw.

Every action is served by the surface, and the new pickers are fenced server-side:
- corporate accounts only;
- persons only;
- no merged or blacklisted parties.

Corrections:
- The credit form's limit is read-only, and the invented BDT 500,000 DOFA note is replaced by the real rule.
- The identity form states that scans are not captured until the resident document store (DEP-31) is live.
- The DSR form labels `notified_at` as required for a rectification.
- **The AR credit-control table's inline limit box** (`p03_workspace.xml`) now shows the limit read-only. Before, it wrote the limit straight to the profile.

## Evidence

- **Node guard** `cd_p03_portal/tests/test_m33_capture_pass2.py`: 7/7 pass. On HEAD 742e46bc, 7/7 fail. It runs the engine's own `fregCreate`/`fregPanels` over the real fragments. Pass 1's 43-check guard still passes.
- **Live tests** on the private clone `fix_test_m33c2`, run as clerk, steward, Tier 2, DPO, registration administrator, accountant and two Accounting Administrators (never the superuser):
  - `cd_party_master/tests/test_m33_capture_pass2_live.py` 7/7;
  - `cd_billing_engine/tests/test_m33_credit_limit_change.py` 3/3.
- **Mutation check: 19/19 red.** Each rule was removed in turn and its suite went red: OTP stamping, re-verify on change, the BRU-CPM-01 gate, steward four-eyes, evidence, the assisted-consent check, guardian verification, DPO-only clearing, the contact limit, limit authority, the rectification notice, the typed limit, the profile born with a limit, the requester approving, a stale request applied, the guard token leaking from create, and three page/form mutants.
- **A real defect the tests caught:** `fix.credit.limit.change.create` handed back records that still carried the guard token from its own create, so a later direct write of `state` went through. It now returns the records in the caller's context.
- **Static guards:** 721 passed, 0 failed. This covers A03 registry coverage, sub-module mapping, the estate page standard, the create button, forms showing their children (which caught the missing limit-history grid) and the write whitelist.
- **Regression** on `fix_test_m33c2`: all of `cd_party_master`, all of `cd_billing_engine`, every `test_a03_*` and `test_m33_*` portal test, the M20 registry and the estate pages. **1,440 tests, 5 failures:**
  - **One was mine.** The Consent Handling form offered its guarded fields as editable. Fixed by declaring them read-only; the save action still takes them as inputs.
  - **One was a serialization conflict** from my private server's crons sharing the clone. It passed with the server stopped.
  - **Three are pre-existing.** They fail the same way on base code against the base clone `fix_test_m25c2`:
    - two invoice-gate message tests now meet the BIN/e-TIN rule first;
    - the routed-approval sweep stops on a model without an integration pattern.
  - After the fixes, the re-run of those files plus the guards gave 211 passed and the same 3 base failures.
- **UI on the private server (8163, dev login):**
  - pages 1, 3, 5, 9 and 11 show the new chips in the real workspace;
  - the new lists serve every declared column (none dropped);
  - a Contact Point was saved through the form, and `+880 1711-555123` was stored as `01711555123`;
  - Send Verification Code moved it to "Code Sent";
  - the endpoint refuses the internal stamping method;
  - Consent Handling was set to Minor with its reason through the form.

## Owner decisions and what is not built

- **BRU-CPM-01 switch** (`cd_party_master.require_verified_contact`). It is off because no fix_real party has a verified contact; switching it on stops all activations until contacts are verified.
- **OTP "Mark Verified" still needs no code.** This is unchanged from pass 1. The code is issued and checked by the channel (M27 / portal), which does not exist yet. Until it does, a person presses Mark Verified, and that now stamps a specific contact point.
- **Who decides:**
  - Accounting Administrators on fix_real must be at least two for SOD-04 to work.
  - Data stewards (0 on fix_real, per pass 1) are needed for relationship verification. So a minor's consent cannot be captured on fix_real until a steward exists. That is fail-closed, as BRU-CPM-16 asks.
- **Corporate self-service (P07 portal)** is not built here. A corporate administrator adding users from the portal is the portal's work. The roles and the limit it would act within now exist.
- **Not built (P2/P3):**
  - hierarchy change control with effective dating (FR-CPM-012);
  - government entity specifics (FR-CPM-013);
  - `fix.bd.geography` cascading reference (FR-CPM-015, which pass 1 also noted);
  - price-book assignment (FR-CPM-048), which needs M11's engine to consume it;
  - sanctions screening (FR-CPM-025);
  - notice supersede automation (AUT-CPM-07, carried from pass 1).
- **Stewardship queue (FR-CPM-033)** is M64's DQ Remediation worklist. No M33 chip was added, because its form takes a typed database id.

## State

**LANDED, PUSHED AND LIVE on fix_real (8069) and fix_dev (8090), 19 Nov 2026.**

- **Landed and pushed.** The fix landed as 3190a8ce on `fix/a03-live-data-and-pending-work`, rebased twice over peer landings with no overlap; the regenerated whitelist matched the merged one. The shared branch and `fix/m33-capture-pass2` are pushed.
- **Approved.** The user approved the deploy of both DBs.
- **Backups** were taken first: `_migration/backups/fix_{real,dev}_pre_m33_capture2_2026-11-19.dump`.
- **Upgrade:** `-u cd_party_master,cd_billing_engine,cd_p03_portal` on fix_real (155 modules) and on fix_dev (151 modules). Both exited 0 with no registry errors.
- **One restart for several sessions.** The restart was held for M40's `cd_partner`, which M37's combined `-u` on both DBs closed. The M40 session then restarted both servers once, at 13:24: 8069 = PID 60036, 8090 = PID 83644. The gap check before it was empty.
- **Verified live on both servers** (dev login, read-only):
  - all four new tables, their ACL rows and company rules, and the new columns are in place;
  - every new list and the credit profile list are served with no dropped column;
  - the internal stamping method is refused;
  - bundle `01944e2` carries the new forms, and the AR table's inline limit edit is gone.
- **fix_real facts for the owner:**
  - 4 Accounting Administrators (enough for SOD-04);
  - 0 Party Data Stewards;
  - 0 Registration Administrators;
  - 0 credit profiles with a limit.
- **Clean-up:** the worktree, the private clone `fix_test_m33c2` and the launch entry were removed.

