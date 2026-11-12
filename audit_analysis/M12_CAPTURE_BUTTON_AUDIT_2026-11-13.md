# M12 Marketplace & Sellers — sub-module capture-button audit (13 Nov 2026)

**Question.** Not every M12 sub-module page has a button to record its data. What should each page capture, what does the codebase do, and what was fixed?

**Sources checked.**
- The spec: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md` §5 (FR-MKP-001..078), §8 (lifecycles), §9 (BRU-MKP rules) and §10 (entities).
- The Function Register: `contracts/nav/registry.json`, M12 `freg` src 101, 11 sub-modules.
- The workspace: `cd_p03_portal/static/src/a04/m12.js` and `controllers/a04/m12.py`.
- The engine: `p03_workspace.js` `fregCreate` / `fregPanels`, the code that decides a page's "+ New" and its form chips.
- The models: `cd_marketplace`; `cd_settlement_ext` (M53: commission scheme, payout run, statement); `cd_contract_core` (M08: contract, Marketplace family).
- Live data on `fix_real` (the database 8069 serves): **0** sellers, orders, quotes, scores, disputes, listings, statements, payout runs, seller schemes and marketplace agreements. On the live estate, the capture buttons are the only way any M12 record can start.

## 1. What each page offered before, and what it should capture

Engine evaluation over the committed registry (HEAD), run in node as the browser runs it.

| # | Sub-module | Before: "+ New" / form chips | What the spec says is captured here | Verdict |
|---|---|---|---|---|
| 1 | Seller Registration & KYC | + New Seller Application / chip | Seller application, KYC (FR-MKP-001..011) | OK |
| 2 | Agreements & Tiers | **nothing** (`create: false`, no forms) | Seller agreement version and signature (FR-MKP-009, held as an M08 contract); tier commission terms (FR-MKP-013) | **Gap** |
| 3 | Listings | + New Listing / Listing, Stock Position | Listings, seller stock (FR-MKP-017..025) | OK |
| 4 | Job Broadcast & Bidding | + New Seller Quote, **no chips** | Broadcasting a job (the marketplace order); seller bids (FR-MKP-028..030) | **Partial**: the broadcast form was on no page |
| 5 | Execution Oversight | + New Marketplace Order, no chips | Execution steps: job completion, customer sign-off (FR-MKP-039..041). Not a new order | **Wrong button** |
| 6 | Ratings | **nothing** | The customer's rating at sign-off (FR-MKP-049); scores are measured | **Gap** |
| 7 | Performance Consequences | **nothing**, and **no store at all** | Warning, probation with remediation plan, suspension; appeal decided by another operator (FR-MKP-053..055, §8.1, BRU-MKP-18) | **Gap (model missing)** |
| 8 | Disputes | + New Dispute Case | Disputes and chargebacks (FR-MKP-058..063) | **Partial**: the Chargeback form was on no page |
| 9 | Commission & Fees | **nothing** | Commission scheme by tier (FR-MKP-068); fee definitions (FR-MKP-069) | **Gap** |
| 10 | Wallet & Payouts | **no + New** (Payout Run chip only) | Payout run (FR-MKP-072) | **Partial** |
| 11 | Trust & Safety | **nothing** (`create: false`), only certification chips | Suspension on a counterfeit-part or fraud finding (FR-MKP-066, BRU-MKP-11) | **Gap** |

**Other defects found in the same pass:**
- **D1. "Commission Schemes" did not show schemes.** The screen showed the Commission Revenue report a second time. The record that matters is M53 `fix.commission.scheme` with payee type Seller. A marketplace commission accrues only when a seller scheme is in force: `_fix_ensure_scheme` refuses with "nothing accrues until Finance configures one". A scheme's non-zero rate replaces the tier rate pinned on the order. M12 gave no way to reach that scheme, and `fix_real` has none.
- **D2. The Payout Run form let a person type seller statements.** The statement grid (seller, GMV, commission) was editable, and `statement_ids` was on the write whitelist. Statements are issued by the system when the run executes (`fix_settlement_ext.py`, run execution). A typed draft statement would appear in the Commission Revenue and Fees reports as if it were real.
- **D3. Customer rating not range-checked.** `action_review(rating=…)` stored any integer, so 7 or −3 went into the seller's measured score.
- **D4. Chargeback, Marketplace Order and Seller Bid forms sat on no page**, so no sub-module offered them.

## 2. What was changed

**Workspace registry** (`static/src/a04/m12.js`). Every page now names its capture, and every new M12 form has tabs (A04 F-2):

| # | "+ New" now | Chips | How |
|---|---|---|---|
| 1 | Seller Application | Seller Application | unchanged |
| 2 | **Seller Agreement** | Seller Agreement, Seller Commission Scheme | Page lists M08 contracts of the Marketplace family. The button opens **M08's own contract form** (`M08-record`), preset to that family. M08 is the one editor of contracts and their amendments, entitlements, parties and obligations. The new read-only list `M12-agreement-list` carries the M08 approval, legal-review and activation actions. *(Revised the same day: a first version had an M12 form on `fix.contract`, which broke the A04 one-editor and multi-tab guards.)* |
| 3 | Listing | Listing, Stock Position | Stock Positions list added to the page |
| 4 | **Marketplace Order** (broadcast a job) | Marketplace Order, Seller Bid | |
| 5 | **Record Job Completion** | Job Completion, Customer Sign-off | Pick-then-act form: choose a job in progress, then run `action_complete`. The page lists orders in execution only. |
| 6 | **Record Customer Sign-off** | Customer Sign-off | Pick-then-act form: choose a completed job, enter the 1–5 rating, then run `action_review`. Scores stay measured. |
| 7 | **Seller Consequence** | Seller Consequence | New record (below) |
| 8 | Dispute Case | Dispute Case, **Chargeback** | Chargebacks list added to the page |
| 9 | **Seller Commission Scheme** | Seller Commission Scheme | The page and the "Commission Schemes" screen now list M53 seller schemes. The new form `M12-form-scheme` starts on payee type Seller. |
| 10 | **Payout Run** | Payout Run | New list `M12-payout-runs` with the M53 run actions (Collect Accrued, Prepare & Request Approval, Release to Treasury, Refresh, Cancel). The statement grid is now read-only (D2). |
| 11 | **Seller Consequence** | Seller Consequence, Chargeback, Seller Certification, Seller Standard | |

**New record: `fix.seller.consequence`** (`cd_marketplace/models/fix_seller_consequence.py`, module version 19.0.0.3.0):
- **Content.** A formal warning, a probation (remediation plan and review date required), or a suspension. Each carries a trigger (score, upheld dispute, counterfeit part, evidence non-compliance, fraud, lapse, other), a reason and effective dates.
- **Lifecycle.** `draft → active → appealed → active | lifted`; `active → lifted | expired`; `draft → cancelled`. A daily cron expires it on its end date.
- **Segregation of duties.** It is lifted, or its appeal decided, only by an operator who neither recorded nor imposed it and does not act for the seller (BRU-MKP-18). Its terms are pinned once imposed.
- **Enforcement.** While a suspension is in force (an appeal does not lift it), imposing it pauses the seller's live listings. New quotes, awards and listing submit or resume are refused (BRU-MKP-11; hooks in `fix_marketplace.py` and `fix_marketplace_listing.py`).
- **Security.** Read access for staff; create and write for Marketplace Operators. A seller (portal) reads only their own. Company and operating-unit isolation rules were generated by `generate-isolation-rules.py`. The record has its own sequence `SCQ/<year>/`.
- **Endpoint.** Registered in `controllers/a04/m12.py` SURFACES, with its six actions whitelisted.

**Rating check (D3).** `action_review` accepts a whole number from 1 to 5, or none.

**Generated files.** `controllers/a04/writable.py` gains `fix.seller.consequence`. `controllers/a08/writable.py` drops `statement_ids` from `fix.payout.run`.

## 3. Evidence

All runs were on 13 Nov 2026.

| Run | Where | Result |
|---|---|---|
| New guard `cd_p03_portal/tests/test_m12_submodule_capture.py` (20 tests; runs the engine's `fregCreate` / `fregPanels` in node) | committed `m12.js` (HEAD) | **15 failed**, 5 passed: one failure per defect above |
| Same guard + `test_estate_module_pages.py` (all 67 modules) + `test_m02_capture_buttons.py` | working tree, scratch copy (no conftest) | **645 passed** |
| `cd_marketplace/tests/` (all 7 files, incl. new `test_seller_consequence.py`, 20 tests) | private copy `fix_test_m12cap`, cd_marketplace upgraded to 19.0.0.3.0 | **206 passed**, 0 failed |
| `test_a04_submodule_mapping`, `test_all_submodule_mapping`, `test_submodule_create_button`, `test_a04_write_whitelist`, `test_a08_write_whitelist`, `test_m12_submodule_capture` | `fix_test_m12cap` | **55 passed**, 0 failed |
| ruff 0.8.4 check + format | changed Python files | clean |

On the upgraded copy, the model, its two isolation rules, its seller-portal rule and the `SCQ/` sequence are present.

The consequence tests run as real users: operator, second operator, plain user, portal seller. They prove:
- impose, and terms pinned once imposed;
- a probation needs its plan and review date;
- the imposer cannot lift the consequence or decide the appeal, and a second operator can;
- a suspension pauses live listings and refuses resume, new quotes and the award of an earlier quote, even under appeal;
- a warning blocks nothing;
- the cron expires a lapsed consequence;
- a rating of 7, −3, 0.5 or "x" is refused, while 5, "4" and blank are recorded.

## 4. Not done / still open

- **Fees (FR-MKP-069) have no definition record.** The statement's `platform_fee` is never set by the run that issues statements, so it is always 0. Building a fee schedule is a Finance design decision: the basis, who sets it, and VAT treatment (BRU-MKP-15 forbids settlement and VAT logic before the external tax opinion).
- **Two commission rates.** An order pins the tier rate from system parameters `cd_marketplace.commission_rate.<tier>`. The accrual then uses the seller scheme's rate when that rate is non-zero. Finance should either set scheme rates to 0 (the order's rate applies) or retire the per-tier parameters. The new scheme form says this in its note.
- **Not built from the spec:** trust signals (`fix.trust.signal`, FR-MKP-064/065); evidence parity on completion (BRU-MKP-02: `action_complete` checks no photos or QC); promotions and boosts (FR-MKP-075..077); seller offboarding (FR-MKP-067). Each is a build of its own, beyond the capture buttons.
- **Deployment: live on `fix_real` (8069/8089) since 13 Nov 01:41.**
  - **Upgrade.** A peer session's estate-wide upgrade of `fix_real` (01:38–01:40 local) loaded this code from disk. cd_marketplace is at 19.0.0.3.0, and the `fix_seller_consequence` table, model, 3 record rules, 3 access rules, `SCQ/` sequence and expiry cron are present.
  - **Servers.** 8089 restarted at 01:40:59 and 8069 at 01:41:45, both after the last of these files was saved, so both run this code. No further restart was needed, and none was done.
  - **Bundle.** The served bundle `/web/assets/658eef3/web.assets_web.min.js` (built 01:44) contains the new screens and forms: `M12-form-consequence`, `M12-agreement-list`, `M12-form-signoff`, `M12-form-job-complete`, `M12-payout-runs` and `M12-form-scheme`.
  - **Not re-run against `fix_real`.** The read-only test pass could not run there: the shared `.venv` had packages reinstalled around 01:00–02:00 (cryptography 50.0.2 with pyOpenSSL 24.1.0 fails with `lib has no attribute GEN_EMAIL`). The same tests passed on the upgraded copy.
- Nothing is committed.
