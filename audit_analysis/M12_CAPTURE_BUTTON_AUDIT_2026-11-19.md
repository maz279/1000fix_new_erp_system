# M12 Marketplace & Sellers — capture-button audit, second pass (19 Nov 2026)

**Question.** Not every M12 sub-module page has a relevant data capture button. What should each page capture, what does the codebase do, and what was fixed?

**Previous pass.** On 13 Nov (`M12_CAPTURE_BUTTON_AUDIT_2026-11-13.md`) every one of the 11 pages got a "+ New" button, and its guard test still passed today (21/21). So this pass asked a narrower question: **does each button capture that page's own record, or does it borrow another page's, or capture nothing?**

**Sources checked.**
- The spec: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md`. §5 holds FR-MKP-001..078, §8 the lifecycles, §9 the BRU-MKP rules and §10 the entities.
- The Function Register: `contracts/nav/registry.json`, M12 `freg` (11 sub-modules, 101 functions). It holds names and counts only, so each page's purpose comes from the §5 FR groups it covers.
- The workspace and engine:
  - `cd_p03_portal/static/src/a04/m12.js` and `controllers/a04/m12.py`;
  - `p03_workspace.js` `fregCreate` / `fregPanels`, evaluated in node as the browser runs them.
- The models:
  - `cd_marketplace`;
  - M52 `fix.payee.bank.change`, the verified payee account;
  - M53 payout runs, which pay a seller only to a confirmed `res.partner.bank`.
- Live data on `fix_real`: 0 sellers, orders, quotes, listings, consequences, disputes, marketplace agreements, seller schemes and seller standards. A changed rule therefore touches no live record.

## 1. Each page: what it should capture, what it did, verdict

| # | Sub-module (spec FRs) | Before (13 Nov build) | Verdict |
|---|---|---|---|
| 1 | Seller Registration & KYC (FR-001..016) | + Seller Application. The form had no seller type (FR-001: individual vs shop, with different documents). The approved categories field existed on the model but **not on the form** (FR-007/008). Nothing reached the payout account (FR-006), although M53 pays a seller only to a confirmed bank account and M52 already has that form. | **Partial** |
| 2 | Agreements & Tiers (FR-009, 010, 012, 013) | + Seller Agreement (M08 contract, Marketplace family); Seller Commission Scheme chip | OK |
| 3 | Listings (FR-017..026) | + Listing; Stock Position | OK |
| 4 | Job Broadcast & Bidding (FR-027..038) | + Marketplace Order; Seller Bid. **No way to record the customer's consent to an external seller** (FR-037, BRU-MKP-07, a hard block before broadcast). The order's quote grid offered the quote **state** as an edit field. | **Gap** |
| 5 | Execution Oversight (FR-039..048) | + Record Job Completion: a pick-then-click that **captures nothing**. No photo, QC checklist or parts declaration existed, yet BRU-MKP-02 (hard block) says a job cannot complete without the owned-job evidence (FR-040), and FR-042 needs the parts declaration. | **Gap** |
| 6 | Ratings (FR-049..052, 056, 057) | + Record Customer Sign-off: **page 5's workflow step**, storing one 1–5 number. No review store, so no multi-parameter rating, written review, moderation or seller response (FR-049/050). | **Borrowed** |
| 7 | Performance Consequences (FR-053..055) | + Seller Consequence | OK |
| 8 | Disputes (FR-058..063) | + Dispute Case; Chargeback | OK |
| 9 | Commission & Fees (FR-068, 069, 074..077) | + Seller Commission Scheme | OK for commission. Fees remain an owner decision (§4). |
| 10 | Wallet & Payouts (FR-070..073) | + Payout Run. Wallet and statements are issued by the system. | OK |
| 11 | Trust & Safety (FR-064..067) | + Seller Consequence: **page 7's record**. A counterfeit-part report, fraud or off-platform dealing had nowhere to go, and BRU-MKP-11 (the listing is suspended at once) had no trigger. | **Borrowed** |

## 2. What was changed

### New records (`cd_marketplace/models/fix_marketplace_capture.py`, module 19.0.0.4.0)

**`fix.marketplace.job.evidence` (page 5; FR-MKP-040/042, BRU-MKP-02).**
- One row per artefact: before photograph, after photograph, diagnostic record, QC checklist, or parts-used declaration (provenance genuine / OEM-equivalent / refurbished / used / "no parts used", plus the part, plus warranty days).
- `compliant` is computed:
  - a photograph needs its file;
  - a QC checklist needs its scan or notes AND "every check passed";
  - a parts declaration needs a provenance and the part, or "no parts used".
- It is captured only while the job is in progress, and cannot be changed or removed after.
- **`action_complete` now refuses a service job that lacks compliant evidence of every required kind.** The kinds come from the system parameter `cd_marketplace.completion_evidence`, default `before_photo,after_photo,qc_checklist,parts_declaration`. The Quality Manager owns this rule.

**`fix.seller.review` (page 6; FR-MKP-049/050).**
- It records one review per signed-off job (verified-job attribution): an overall rating (required) plus workmanship, timeliness, communication and value, each 1–5, and the written text.
- It is moderated (published or rejected with a policy reason) by an operator who did not record it and does not act for the seller. The text is pinned once moderated.
- The seller responds once, to a published review.
- A **published** review's overall rating is the job's rating in the measured seller score. Without one, the sign-off rating counts, as before.
- The seller's portal account reads only published reviews of their own work.

**`fix.trust.signal`, "Trust & Safety Report" (page 11; FR-MKP-064..066, BRU-MKP-11).**
- **Content:** the concern (counterfeit part, off-platform dealing, collusion, fake job, payment fraud, review manipulation, other), its source and severity, the seller's listing or job, the description and the evidence.
- **On save:** a counterfeit-part report naming a live listing suspends that listing at once.
- **Lifecycle:** reported → under investigation → substantiated or dismissed. The decision is made by an operator other than the one who recorded it.
- **Outcomes:**
  - A substantiated counterfeit, payment-fraud, collusion or fake-job finding imposes a seller suspension (`fix.seller.consequence`), which blocks quotes, awards and listings. An appeal against it goes to yet another operator (BRU-MKP-18, existing).
  - A dismissed report puts the listing back live, unless the seller is suspended for another reason.
- The seller under investigation has no access to reports.

### Changes to existing records

- **Customer consent (page 4; FR-MKP-037, BRU-MKP-07).**
  - New fields on `fix.marketplace.order`: consent yes/no, how it was taken (signed form, OTP, recorded call, in-app) and a reference. Who recorded it and when are stamped by the server.
  - **No seller quote is accepted on a service job until consent is recorded.** Refurbished-device resale is exempt.
  - Consent is pinned once quotes exist.
- **Seller type (page 1; FR-MKP-001/003).** `seller_type` (individual / shop or business). **Verify KYC** refuses an individual without the NID, and a shop or business without its trade licence and e-TIN. Submitting stays possible without them, as before.
- **Score.** `action_measure` reads each job's rating through `_fix_job_rating()`.

### Workspace (`static/src/a04/m12.js`)

| # | "+ New" now | Chips | New list |
|---|---|---|---|
| 1 | Seller Application | Seller Application, **Seller Payout Account** (opens M52's own `M52-form-bank-change`: proposed with the call-back, confirmed by a second person, only then payable) | |
| 4 | Marketplace Order | unchanged | Order form gains a **Customer Consent** tab. The quote grid's state is read-only. |
| 5 | **Record Job Evidence** | Job Evidence, Job Completion, Customer Sign-off | `M12-job-evidence` |
| 6 | **Record Customer Review** | Customer Review (the sign-off stays on page 5) | `M12-review-list` (Publish, Reject, Record Seller Response) |
| 11 | **Trust & Safety Report** | Trust & Safety Report, Seller Consequence, Chargeback, Seller Certification, Seller Standard | `M12-trust-signals` (Start Investigation, Substantiate, Dismiss) |

- **Seller form:** Seller Type and Service Categories Applied For.
- **Job Completion form:** its note now names the evidence it needs.

### Wiring

- `controllers/a04/m12.py`: SURFACES for the three models, with their actions whitelisted.
- `controllers/a04/writable.py`: regenerated with `form_fields.py --a04`. Only the M12 hunks changed.
- **Security:**
  - ACL: staff read; Marketplace Operators create and write (evidence: also delete, while the job runs).
  - Company and operating-unit rules from `generate-isolation-rules.py`.
  - Seller-portal rules: own job evidence, own published reviews; no access to trust reports.
- **Sequences:** `JEV/`, `SRV/`, `TSR/`.
- **System parameter:** `cd_marketplace.completion_evidence`.

## 3. Evidence

All runs used worktree `m12cap2-wt`, on HEAD 6d1dbd77 plus this change, on the private database `fix_test_m12c2`. That is a fix_test clone with `-u all` from the worktree, which loaded cleanly, with cd_marketplace at 19.0.0.4.0.

| Run | Result |
|---|---|
| Page guard `cd_p03_portal/tests/test_m12_submodule_capture.py`: runs the engine's `fregCreate` / `fregPanels` in node over the real fragments, with 15 new tests | **36 passed**. On HEAD the new tests fail; they are killed by the page mutants below. |
| `cd_marketplace/tests/`, all 9 files, including the new `test_marketplace_capture.py` with 37 tests run as operator, second operator, compliance, plain user and the seller's portal account | **235 passed**, 0 failed |
| Focused regression (estate page standard, A04 children, registry, sub-module mapping and write-whitelist guards, M01/M02/M03/M08/M52/M53 capture guards, cd_settlement_ext, cd_tradein, cd_rbac_ext permissions) | All pass except 4, which **fail identically on a clean HEAD checkout**: `test_submodule_create_button` (M30 "Branch Master"), and the A04 `no flat forms` pair (8 M36 step forms) |
| A04 guards in cd_contract_core, which hard-code the **shared checkout's** path and so never see a worktree. Re-run as copies pointed at this worktree and at HEAD | Same two M36 flat-form failures on both. The document-vault ratio fails on HEAD (53 of 107 forms) and **passes** here (55 of 110), because the two new forms that hold uploads use the estate's `docs` tab id. |
| Mutation check: 16 defects re-introduced one at a time; the suite must go red | **16/16 killed**: consent gate off; evidence gate off; photo compliant without its file; evidence editable after completion; recorder moderates own review; second seller response; published review ignored by the score; counterfeit report leaves the listing live; finding imposes no suspension; reporter decides own report; KYC verified without identity; ratings page borrows the sign-off; trust page borrows the consequence; execution page captures nothing; payout chip dropped; consent stamp typed |
| ruff 0.8.4, check and format, on changed Python | clean |

**UI walk.** A private server ran on port 8074 against `fix_test_m12c2`, and every one of the 11 pages was opened in the browser pane.

| # | Page | "+ New" shown | Form chips |
|---|---|---|---|
| 1 | Seller Registration & KYC | + Seller Application | Seller Application, Seller Payout Account |
| 2 | Agreements & Tiers | **+ New Seller Agreement** | Seller Agreement, Seller Commission Scheme |
| 3 | Listings | + New Listing | Listing, Stock Position |
| 4 | Job Broadcast & Bidding | + New Marketplace Order | Marketplace Order, Seller Bid |
| 5 | Execution Oversight | **+ Record Job Evidence** | Job Evidence, Job Completion, Customer Sign-off |
| 6 | Ratings | **+ Record Customer Review** | Customer Review |
| 7 | Performance Consequences | + New Seller Consequence | Seller Consequence |
| 8 | Disputes | + New Marketplace Merchant Dispute Case | Dispute Case, Chargeback |
| 9 | Commission & Fees | + New Seller Commission Scheme | Seller Commission Scheme |
| 10 | Wallet & Payouts | + New Payout Run | Payout Run |
| 11 | Trust & Safety | **+ New Trust & Safety Report** | Trust & Safety Report, Seller Consequence, Chargeback, Seller Certification, Seller Standard |

- **Page 2's label.** The walk itself found a further defect: page 2's button read "+ New Enterprise Service Contract", the title of M08's form. A sub-module mapping can now carry its own wording (`createLabel`, a 6-line engine addition in `fregCreate`).
- **Forms open.** Every "+ New" opened its form with its tabs: Customer Review, Job Evidence and Trust & Safety Report are new; the seller form shows Seller Type and Service Categories.
- **Pickers honour their rules.** The review's job picker offered nothing on a clone with no signed-off job.
- **A real save.** A Trust & Safety Report was entered and saved through the UI for a seeded seller and live listing. It was stored as `TSR/2026/00040`, recorded by the signed-in user, and the listing went to **paused** at once.

## 4. Not done / still open

- **Fees (FR-MKP-069)** and the **two commission-rate sources** are still Finance decisions, as recorded on 13 Nov. BRU-MKP-15 forbids settlement or VAT logic before the external tax opinion.
- **Agreement before transacting (BRU-MKP-01).** The seller agreement is captured on page 2 as an M08 contract, but nothing yet stops an unsigned seller from quoting. That needs a link from the seller to their active Marketplace contract: a control build, not a capture button.
- **Not built from the spec:**
  - seller offboarding (FR-MKP-067);
  - escalation and takeover of a live job (FR-044);
  - rework routing (FR-047);
  - promotions and boosts (FR-075..077);
  - tier definition records (FR-013; tiers remain the measured selection plus per-tier system parameters);
  - automatic detection of off-platform or collusion patterns (FR-064/065 detect; this pass records and decides the reports people make).
- **The evidence is captured by an operator in the workspace.** The seller's own job app (FR-039, offline-tolerant) is not built.

DEPLOY_PLACEHOLDER
