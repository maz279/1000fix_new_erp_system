# M52 AP & Employee Expense: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M52 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M52_Accounts_Payable_and_Employee_Expense.md`. Sections used:
  - §3: scope (22 capabilities) and the boundaries with M15, M16, M42, M50 and M51;
  - §5: FR-APE-001 … 038;
  - §8: the invoice, claim and advance lifecycles;
  - §9: BRU-APE-01 … 26;
  - §10.1: the 24 owned entities;
  - §13 and §14: roles and reports.
- Research: `audit_analysis/A08_FINANCE_TARGET_SPEC.md` (M52).
- Code:
  - `cd_p03_portal/static/src/a08/m52.js`: the page registry (9 sub-module pages);
  - `cd_p03_portal/controllers/a08/m52.py`: surfaces, reports and KPIs;
  - `cd_ap_ext/models/*.py`: the AP and expense models.
- Live data (fix_real, read-only count on 17 Nov): 0 vendor bills, 0 notes, 0 payment runs, 0 claims, 0 advances, 0 payee bank changes, 0 received PO lines, 0 take-on batches. There are 23 vendor tax profiles, 8 expense policies and 8 per-diem/mileage rates. The M52 lists on fix_real are therefore mostly empty; that is a data take-on matter, not a screen defect.

## 1. What was there (HEAD 94bf9e99)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Invoice Capture | Vendor Bill | Vendor Bill | None. |
| 2 | Matching | **none** | **none** | **The page captured nothing.** A blocked bill had no exception case: no type, owner, responsible party, due date or resolution (FR-APE-007 P0, BRU-APE-03 H). **The match tolerance was hard-coded**: exact quantity and 0.01 on price, with no record to configure it by category or value band (FR-APE-005 P0). |
| 3 | Approval | **none** | **none** | The page lists the matrix change requests, but had no chip for them although the form existed. |
| 4 | Payable Ledger | none | Debit Note | **No vendor dispute** (FR-APE-017), **no vendor statement reconciliation** (FR-APE-016), and **the ageing was never kept**: no snapshot at a period close (FR-APE-013 P0, BRU-APE-23 H). The legacy AP take-on wizard and its audit list sat on no page. |
| 5 | Payment Runs | Payment Run | **none** | The page lists payee bank changes (both queues) with no chip, although the form existed. |
| 6 | TDS/VDS | **none** | Vendor Tax Profile | No "+ New" on the page. Withholding lines are computed, so the tax profile is the page's capture. |
| 7 | Employee Expenses | Expense Claim | Expense Claim | The page lists the expense policy and the per-diem/mileage rates with no chip, although both forms existed. Expense categories and grades were listed on no page. |
| 8 | Advances & Cards | Employee Advance | Employee Advance | **No card record** of any kind (FR-APE-038), although "Cards" is in the page title. The supplier advance, which M52 pays and takes back on the bill, had no link from the page. |
| 9 | GRNI | **none** | **none** | **The page captured nothing.** GRNI existed only as a live report: nothing was kept for a period end, there was no unrecorded-liability estimate, and no second person signed it off (FR-APE-031 P0, BRU-APE-22 H). |

The page-9 grid listed goods receipts (an M15 record).

The guard `cd_p03_portal/tests/test_m52_capture_buttons.py` was run on HEAD: **24 of 43 tests fail.** The failures cover pages 2 to 9, the creatable lists with no capture, the orphan screens, the missing records, an untabbed 18-field form (Payee Bank Change), and the case and accrual actions.

## 2. What was built

### Backend: `cd_ap_ext` 19.0.1.1.0, new file `models/fix_ap_capture.py`

Every decision is taken by someone other than the person who raised it (`require_other_person`). State, stamps and derived figures are guarded fields, never typed. Nothing is deleted except a draft.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 2 | `fix.ap.match.tolerance` (FR-APE-005) | Product category (or all), the bill value band it applies from, quantity over receipt %, unit price over PO % and per-unit amount, effective date, reason. | **Approved by an Accounting Administrator other than the requester**, then frozen. A new row for the same category and band **supersedes** the active one on approval. The most specific active row applies (own category or a parent, then the highest band reached). With both a price % and a price amount, the smaller allowance applies. **No row means the old exact match.** On approval, bills not yet approved are matched again, and a bill that passes only because of the tolerance says so in its match detail. A bill dated before the row's effective date is not covered. |
| 2 | `fix.ap.match.exception` (FR-APE-007, BRU-APE-03) | The blocked bill, its PO and vendor, the exception type (guessed from the match detail), the variance when opened, the responsible party (buyer, receiver, vendor or finance), owner, due date, actions taken, resolution and age. | Opened from Match Exceptions ("Open Exception Case") or the form. A daily job opens a case for every blocked PO bill that has none, and closes cases whose bill now matches or was rejected. One open case per bill. **A case closes only when its cause is fixed** (the bill matches, or the bill was rejected). There is no override or release action. |
| 4 | `fix.ap.dispute` (FR-APE-017) | Bill, disputed amount (at most the bill's gross), reason, description, vendor's reference, owner, outcome, the vendor credit note that settles it. | **While open, the bill is held from payment runs** (the proposal leaves it out, and submit/approve/release refuse a run that still carries it) **and from single payment requests.** Resolved by someone other than the raiser. An upheld or partly upheld dispute must name the vendor's approved credit note on the same bill. Payment status is per bill, so the whole bill waits, not just the disputed amount: this is stricter than the spec's "disputed amount only". |
| 4 | `fix.ap.vendor.statement` (FR-APE-016) | Vendor, statement date, the balance on the vendor's statement and the file. | "Compare with Ledger" stamps our balance on that date: approved bills unpaid then, plus approved notes not yet netted, plus the vendor's legacy take-on still open. It also stamps the number of open bills and the difference. **Signed off by a second person**, who is refused if the ledger moved since the comparison, or if a difference has no reconciling items. Frozen once signed. |
| 4 | `fix.ap.ageing.snapshot` (+ vendor lines) (FR-APE-013, BRU-APE-23) | The AP ageing at a date, by vendor and bucket, with totals and who took it. | Saving takes it. **It is never edited or deleted.** There is one per company per date, and no future date. It uses the same computation as the AP Ageing report, which now calls the shared function. |
| 9 | `fix.ap.grni.accrual` (+ lines) (FR-APE-031, BRU-APE-22) | Period end; every receipt not yet billed, at the PO price, line by line; the GRNI total; the GRNI clearing account balance at the period end; the estimated unrecorded liability and its basis. | "Compute from Receipts" uses the same computation as the GRNI report (now shared). **Confirmed by an Accounting Administrator other than the person who computed it.** An estimate without a basis is refused. One confirmed accrual per company and period end; frozen once confirmed. |
| 8 | `fix.expense.card` and `fix.expense.card.transaction` (FR-APE-038) | Card type (corporate or fuel), issuer, the last four digits only, holder, limit and expiry. Statement lines record date, merchant, amount and statement reference, then the category, cost centre or job, purpose and receipt. | A line is recorded once per statement reference and never changed. It is "Explained" only with category, cost centre and receipt. **It is approved by finance, never by the cardholder or the person who explained it.** It can be disputed with the issuer. Card spend is coded directly and never matched to an expense claim, so it cannot be reimbursed twice. |

The bill also changed:
- `open_match_case_id` and `open_dispute_id` are shown on the bill;
- `action_open_match_case` was added;
- `action_request_payment` refuses a disputed bill.

The payment run's candidate selection and line checks were extended for disputes.

The match (`fix_ap_ext._compute_match`) reads the tolerance; without a row it behaves exactly as before.

Security and data:
- ACLs: the read-only finance group reads, while Accountants and Accounting Administrators write. Only drafts of statements, accruals and cards can be deleted; nobody deletes the rest.
- Company and branch rules come from `generate-isolation-rules.py`. Only the cd_ap_ext file was kept; the generator's drift in four other modules was reverted.
- Four sequences were added: MEX/, APD/, VSR/, GRNI/. One daily job was added (match exception cases).
- Load order: the new file extends the bill and the payment run, so it is imported last (`# ruff: noqa: I001`).

### Workspace: `m52.js`, `controllers/a08/m52.py`, `writable.py`

- **8 new lists**, on their pages and in the navigation with Bengali labels: Match Exception Cases, Match Tolerances, Vendor Disputes, Vendor Statement Reconciliation, Ageing Snapshots, GRNI Period-End Accruals, Corporate & Fuel Cards, and Card Statement Lines.
- **8 new forms.** Match Exception Case, Match Tolerance, Vendor Dispute, GRNI Accrual and Card Statement Line are tabbed. The snapshot and the accrual show their lines as a read-only grid.
- Changes to existing screens:
  - Match Exceptions shows the open case and offers **Open Exception Case**;
  - the 18-field **Payee Bank Change** form is now tabbed (AGENTS.md: more than 15 fields);
  - the AP Ageing and GRNI reports call the same functions the snapshot and the accrual use (same rows, same notes).
- Page 8 links M16's **Supplier Advance** form, because M16 owns the advance.
- `writable.py` was regenerated with `form_fields.py --a08`; only the M52 entries changed.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Invoice Capture | Vendor Bill | Vendor Bill |
| 2 Matching | **Match Exception Case** | **Match Exception Case**, **Match Tolerance** |
| 3 Approval | **Matrix Change Request** | **Matrix Change Request** |
| 4 Payable Ledger | **Debit / Credit Note** | Debit Note, **Vendor Dispute**, **Vendor Statement Reconciliation**, **Ageing Snapshot**, **Legacy AP Register Take-on** |
| 5 Payment Runs | Payment Run | **Payment Run**, **Payee Bank Change** |
| 6 TDS/VDS | **Vendor Tax Profile** | Vendor Tax Profile |
| 7 Employee Expenses | Expense Claim | Expense Claim, **Expense Policy Limit**, **Per-Diem / Mileage Rate**, **Expense Category**, **Expense Grade** |
| 8 Advances & Cards | Employee Advance | Employee Advance, **Supplier Advance** (M16), **Card**, **Card Statement Line** |
| 9 GRNI | **GRNI Accrual** | **GRNI Accrual** |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m52_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD 94bf9e99: 24 of 43 fail.** After: **43/43.** |
| Live tests `cd_ap_ext/tests/test_m52_capture_live.py`. They run as non-admin finance users (three Accountants, two Accounting Administrators, a plain user) on a private clone `fix_test_m52` (`-u all`, exit 0). | **18/18.** |
| Mutation check: each rule removed in turn (tolerance approver, frozen tolerance, re-match on approval, smaller price limit, bounded quantity, case closes only on its cause, dispute hold on runs / requests / proposed runs, dispute resolver, upheld needs the credit note, statement second person, reconciling items, frozen snapshot, GRNI confirmer, estimate basis, card holder never approves). | **17 of 17 mutations turned the live tests red;** the source was restored byte for byte. The first run left 2 survivors (the dispute and statement self-approval checks were masked by an earlier refusal); those two tests were reordered and both mutants then went red. |
| Guard + estate page guard + M52 registry and report tests on the clone. | **660 tests, 0 failures.** |
| Regression on the same clone: every `cd_ap_ext` test, every other test that touches vendor bills, payment runs or the two shared reports (M15 hand-offs and RTV credit, M16 controls and capture, M42, M44, M47 asset bridge, M50 controls and treasury, M51 controls and withholding reports, the A08 control suite, the M51/M52 report and registry tests), the M52 guard and the estate page guard. | **1,765 tests: 1,764 passed, 36 skipped by design** (the A08 control suite skips models with no workflow-guarded fields). **The one failure was caused by the UI walk**, which committed an ageing snapshot for today on the clone, so the test's own snapshot hit the one-per-date rule. The test now picks a date with no snapshot; live tests and guard re-run: **61/61.** |
| Workspace endpoints and UI walk on a private server (port 8097), signed in to the clone. | All 8 new lists serve every column (none silently dropped). Through `/p03/model/write`: a tolerance saved, a typed `state` refused, self-approval refused on segregation of duties; a snapshot saved and then refused an edit; a GRNI accrual saved and computed. In the browser, page 2 shows "+ New Match Exception Case" with the Match Exception Case and Match Tolerance chips, and the tolerance form opens tabbed and saved (Draft). Page 8 shows Employee Advance, Supplier Advance, Card and Card Statement Line. Page 9 shows "+ New GRNI Accrual" and the saved accrual. No console errors. |
| `generate-isolation-rules.py`, `form_fields.py --a08`, pinned ruff 0.8.4 | Only the cd_ap_ext / M52 entries changed. Format and lint are clean. |

Three defects were found only by the live run and fixed before the evidence above:
- A card's last four digits were declared `size=4`, which silently truncated "12345" instead of refusing it. The constraint now sees what was typed.
- A second open dispute on the same bill failed as a database error. It is now refused with a clear message, and the same applies to a second ageing snapshot for the same date.
- The test's tolerance rows started today, but the fixture's bills are dated 1 Oct. A tolerance does not cover bills dated before it takes effect, which is the intended behaviour; the test now dates its rows.

## 4. Not built here (owner decisions or other modules)

- **Brand consignment settlement** (FR-APE-030 P0). M15 issues brand-consignment stock only on that brand's own warranty jobs (BRU-INV-01). Whether 1000FiX owes the brand for those parts at all, and at what price, is an owner question for the brand agreements. M11's brand reimbursement covers the claim side.
- **Retention money** (FR-APE-027 P1) and **emergency / out-of-cycle payments** (FR-APE-026 P1). Both change what a bill pays and how it posts (a retention payable, an elevated approval path). They need the owner to name the sub-contracts that carry retention, the retention account, and the emergency approval threshold.
- **Proposal review by line** (FR-APE-019 P0, part): a reviewer cannot yet exclude or defer one payee with a reason on a proposed run. A line with a problem is skipped automatically, and a dispute now holds a bill. A per-line exclude needs a line action the run form's grid does not offer today.
- **Posting the GRNI and the unrecorded-liability estimate to the GL.** Bills already debit the GRNI clearing account, and receipts reach the GL through the M19 inventory cut-over. Posting a second GRNI accrual would double count. The accrual record therefore shows the clearing balance next to the computed figure; any difference is for finance to explain. Posting the unrecorded-liability estimate needs the owner to name the accrued-expense account and the reversal policy.
- **Card statement import and cardholder self-service.** Lines are entered from the issuer's statement by finance. Cardholders without a finance role cannot open their own lines yet, which needs an "own card" record rule. Building it is worthwhile only once a card programme exists: the spec says "where such instruments are in use", and fix_real has none.
- **Partial-amount hold on a dispute.** Payment is per bill in this estate, so an open dispute holds the whole bill (stricter than the spec).
- **Tolerances on fix_real**: there are none, so every PO bill still matches exactly. That stays true until finance proposes a tolerance and a second administrator approves it.

## 5. State

- Built and tested in worktree `m52cap-wt` on branch `fix/m52-capture-buttons`, from 94bf9e99 (the working branch tip at the start). **Not committed, not deployed.**
- Peer sessions M51, M53 and M54 are working on the same area and also change the shared A08 files (`controllers/a08/writable.py`). Landing this change needs a rebase onto whatever they have committed, then the guards re-run.
- Deploying to fix_real (8069) needs `-u cd_ap_ext,cd_p03_portal` and one restart, after a backup and the usual version-gap check. It should be coordinated with the peer sessions' deploys.
- The private clone `fix_test_m52` (and its filestore copy) is kept for the re-test after the rebase.
- Owner decisions: see §4 (consignment settlement, retention, emergency payments, posting accounts for the unrecorded liability, card programme).
