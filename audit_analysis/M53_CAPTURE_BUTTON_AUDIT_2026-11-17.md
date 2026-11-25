# M53 Revenue Recognition & Settlement: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M53 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M53_Revenue_Recognition_Commission_and_Settlement.md`. Sections used:
  - §3: scope (22 in-scope capabilities and the boundaries with M12, M39, M50, M51);
  - §5: FR-REV-001 … 044;
  - §8: the obligation/schedule, settlement-cycle and escrow lifecycles;
  - §9: BRU-REV-01 … 26;
  - §10.1: the 30 owned entities;
  - §11: AUT-REV-01 … 23;
  - §13: roles and segregation of duties.
- Research: `audit_analysis/A08_FINANCE_RESEARCH.md` (M53 table) and `A08_FINANCE_TARGET_SPEC.md` (M53).
- Governance: `00-04_Risks_Assumptions_Dependencies_and_Governance.md` (decision D-03, principal vs agent, still open).
- Code:
  - `cd_p03_portal/static/src/a08/m53.js`: the page registry (9 sub-module pages);
  - `cd_p03_portal/controllers/a08/m53.py`: surfaces, reports and KPIs;
  - `cd_subscription/models/*.py`: subscriptions, obligations, revenue schedules;
  - `cd_settlement_ext/models/*.py`: commission ledger, payout runs, statements, escrow/clawback, warranty provision.
- Live data (fix_real, read-only count on 17 Nov): every M53 table is empty except one seeded commission scheme (the partner TDS line). There are no subscriptions, obligations, schedules, commissions, payout runs, statements, referrals or marketplace sellers.

## 1. What was there (HEAD 94bf9e99)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Performance Obligations | Performance Obligation | Performance Obligation | The **warranty provision** (IAS 37) and **warranty policy** lists and forms existed but sat on no page. |
| 2 | Allocation & SSP | **Performance Obligation** | Performance Obligation | The page captured an obligation, not a price. **No stand-alone selling price** existed (FR-REV-006 P0, AUT-REV-03): each obligation's SSP was typed on its contract with nothing to check it against, so a bundle's allocation was whatever was typed. |
| 3 | Schedules & Triggers | Revenue Schedule (manual, CFO) | Revenue Schedule | The **Held Revenue Schedules** list (the M53-6 decision queue) sat on no page. |
| 4 | Modifications & Reversals | **Subscription** | Subscription Contract | The page captured a new contract, not a modification. **No contract modification** existed (FR-REV-008, BRU-REV-04 H, AUT-REV-06). A price change on a scheduled contract was refused with "cancel and re-create the affected obligations", which throws away the schedule history that BRU-REV-04 requires to be kept. |
| 5 | Principal vs Agent | **none** | **none** | The page captured nothing. **No declared position** existed (FR-REV-007 P0, BRU-REV-08/09 H, AUT-REV-22), yet every marketplace commission was booked as an agent (net) with nothing declared, although D-03 is still an open decision. |
| 6 | Commission Ledger | **none** | Commission Scheme | No "+ New" on the page. The **Commissions with No Source** list (M53-4) sat on no page. |
| 7 | Seller Settlement | **Seller Statement** | Payout Run, Payout Reconciliation | The "+ New" opened a statement with typed GMV, commission and TDS. The model issues a statement only for its paid payout run, which a typed one can never have: it was a dead record. **No payout hold** (FR-REV-035 P0, BRU-REV-16 H) and **no settlement dispute** holding only the disputed lines (FR-REV-039 P0, BRU-REV-17 H). The only hold was M12's automatic flag for an open marketplace dispute or chargeback, which holds the whole seller; nobody could hold a payout for quality, KYC or tax status. |
| 8 | Partner Payouts | **none** | **none** | The page captured nothing: partner commissions are paid in payout runs, but the page offered neither the run nor a hold. |
| 9 | Escrow & Clawbacks | Clawback / Escrow | Clawback | None. |

Guard `cd_p03_portal/tests/test_m53_capture_buttons.py` on HEAD: **19 of 35 tests fail**, covering 7 of the 9 pages.

## 2. What was built

Every decision is taken by someone other than the person who raised it. Stamps and derived figures are guarded fields, never typed. Nothing that left draft is deleted.

### Backend: `cd_subscription` 19.0.1.3.0, new file `models/fix_revenue_capture.py`

| Page | Record | Holds | Rules |
|---|---|---|---|
| 2 | `fix.ssp` (FR-REV-006 P0, AUT-REV-03) | Obligation type, plan (or every plan), method (observable, adjusted market, cost-plus, residual), price, tolerance band, effective date, the price list or study it rests on. | Submitted by an accountant, **approved by an Accounting Administrator who did not submit it**, then frozen. A change is a new SSP that **supersedes** the old one from its date (the old one keeps its dates, so a past allocation can be re-read). **Allocating a contract with more than one obligation refuses an obligation whose typed SSP is outside the band of the approved SSP in force.** Each obligation records which SSP its allocation used, or "typed on the contract" when none is on file. A single-obligation contract is not checked (there is nothing to split). |
| 4 | `fix.contract.modification` (+ lines) (FR-REV-008, BRU-REV-04 H, AUT-REV-06) | The contract, effective date, nature (price change, term change, added scope), treatment (prospective, cumulative catch-up, separate contract), new transaction price and end date, the separate contract for added scope, reason and evidence. | **Approved by an Accounting Administrator who did not request it**, then applied at once. Each scheduled obligation is recognised up to the effective date; its schedule is **closed and kept** with what it recognised; a **new schedule version** recognises the re-allocated remainder (split by SSP, rounding residue on the largest, so it sums exactly). A cumulative catch-up becomes a **manual schedule for the CFO** (BRU-REV-01): nothing is released before the CFO approves it. A price below what is already recognised is refused as a reversal; a future-dated change is refused until its date; added scope is a separate contract and only records the link. One line per obligation keeps the previous and new versions, recognised-before, new allocation, catch-up and remainder. |

### Backend: `cd_settlement_ext` 19.0.0.4.0, new file `models/fix_settlement_capture.py`

| Page | Record | Holds | Rules |
|---|---|---|---|
| 5 | `fix.revenue.presentation` (FR-REV-007 P0, BRU-REV-08/09 H, AUT-REV-22) | Arrangement (marketplace, courier share, brand share), position (agent or principal), the D-03 decision record and the external opinion, effective date, basis. | Approved by an Accounting Administrator other than the requester, then frozen; a new declaration supersedes the old one from its date. **A marketplace commission now accrues to the GL only under a declared AGENT position in force on its date.** With none, or with a principal declaration (this ledger books the net presentation only, FF-91), the accrual is refused — for trusted code too. Partner referral commission is unaffected (it is a cost of a repair 1000FiX sells as principal). |
| 7, 8 | `fix.payout.hold` (FR-REV-035 P0, BRU-REV-16 H; FR-REV-039 P0, BRU-REV-17 H) | Payee, reason (settlement dispute, quality investigation, KYC, tax status, other), the lines held (or none = the whole payee), the disputed statement, details; computed scope and amount held. | Raised by an accountant (named, effective at once; refused once the payee's run is approved). **Released only by an Accounting Administrator who did not raise it, with a reason**; a dispute is closed with its coded outcome (upheld, partly upheld, rejected). A **dispute must name the disputed lines and holds only them**: Collect Accrued Commissions leaves those lines out and pays the rest of the payee; Prepare refuses a run that carries a held line. A whole-payee hold keeps the payee out of the run, alongside M12's automatic dispute flag. |

Security and data: ACLs give the read-only finance group read access, accountants and administrators write; nobody deletes; modification lines are written by the model only. Company/branch rules come from `generate-isolation-rules.py` (only the two modules' files kept; the generator's drift in four other modules was reverted). Two sequences: CMOD/, PHD/.

### Workspace: `m53.js`, `controllers/a08/m53.py`, `writable.py`

- Five new lists, on their pages and in the navigation: Stand-alone Selling Prices, Principal / Agent Positions (D-03), Contract Modifications, Re-scheduled Obligations (versions), Payout Holds & Settlement Disputes.
- Four new forms (each under 15 fields).
- **Seller Statements**: no "+ New", and the statement form is read-only. A statement is issued by its paid payout run; a typed one could never be issued.
- Orphan lists placed: warranty provision and policy on page 1, held schedules on page 3, commissions with no source on page 6.
- Obligations show their SSP basis.
- `writable.py` regenerated with `form_fields.py --a08`; only M53 entries changed (the seller statement surface now accepts no writes).

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Performance Obligations | Performance Obligation | Performance Obligation, **Warranty Provision**, **Warranty Policy** |
| 2 Allocation & SSP | **Stand-alone Selling Price** | **Stand-alone Selling Price**, Performance Obligation |
| 3 Schedules & Triggers | Revenue Schedule | Revenue Schedule |
| 4 Modifications & Reversals | **Contract Modification** | **Contract Modification**, Subscription Contract |
| 5 Principal vs Agent | **Principal / Agent Position** | **Principal / Agent Position** |
| 6 Commission Ledger | **Commission Scheme** | Commission Scheme |
| 7 Seller Settlement | **Payout Run** | Payout Run, **Payout Hold**, Payout Reconciliation |
| 8 Partner Payouts | **Payout Run** | **Payout Run**, **Payout Hold** |
| 9 Escrow & Clawbacks | Clawback / Escrow | Clawback |

### Tests changed

Five existing tests accrue marketplace commission. They now first declare the agent position (`declare_marketplace_agent`, added to `test_a08_m53_controls.py` and imported by the operability and ORM suites), exactly as they configure the GL accounts: that declaration is now a precondition.

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m53_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD 94bf9e99: 19 of 35 fail** (pages 1, 2, 4, 5, 6, 7, 8, the typed statement, orphan lists, the four missing records). After: **35/35.** |
| Live tests `cd_settlement_ext/tests/test_m53_capture_live.py`, run as non-admin finance users (two accountants, two Accounting Administrators, the DOFA Tier 4 CFO, a plain user) on a private clone `fix_test_m53` (`-u all`, exit 0, no errors). | **16/16.** |
| Mutation check on a second clone (`fix_test_m53mut`): each rule removed in turn — SSP approver ≠ submitter, SSP band, SSP earlier date refused, modification approver ≠ requester, old schedule closed, catch-up sent to the CFO, price below recognised refused, no future-dated modification, marketplace needs a position, principal refused, position approver ≠ requester, whole-payee hold blocks the run, a dispute holds its lines, releaser ≠ raiser, a dispute names its lines. | **15 of 15 mutations turned the live tests red;** the source was restored byte for byte. |
| Regression on `fix_test_m53`: every `cd_settlement_ext` and `cd_subscription` test, the M53 registry, guard, estate page guard, M12 capture guard and A08 control suite. | **1,341 passed, 0 failed, 0 errors;** 34 skipped (all the A08 control suite's existing "carries no workflow-controlled fields" cases). |
| Workspace endpoints on a private server (port 8098, the clone). | All 7 new/changed lists serve every column (none dropped). Through `/p03/model/write`: an SSP and a principal/agent position saved; a typed `state` refused; Submit ran; self-approval refused on segregation of duties. |
| UI walk on the same server (the browser pane, signed in). | All 9 pages read live show the "+ New" and chips of the table in section 2. A Stand-alone Selling Price was saved from page 2's "+ New" form (Draft); the Payout Hold chip opens its form with the line picker. |
| Pinned ruff 0.8.4, `generate-isolation-rules.py`, `form_fields.py --a08` | Format and lint clean. Only the M53 entries / the two modules changed. |

Two defects were found only by the live run and fixed before the evidence above:
- Two referrals of the same customer are refused by M40 ("one commission per customer"): the dispute test needed a second referred customer.
- The first draft gated marketplace accrual before the row's own checks, so a row with no scheme reported the D-03 error instead of the missing scheme; the row's refusals now come first.

## 4. Not built here (owner decisions or other modules)

- **D-03 is still open** (CEO + CFO + Legal, `00-04` register). Until someone declares the marketplace position on page 5, marketplace commission does not accrue. fix_real has no marketplace sellers or commissions today, so nothing live is blocked; the declaration needs the decision record and the external opinion.
- **Revenue contract / obligation templates** (`fix.revenue.contract`, `fix.obligation.template`, FR-REV-001/002) and the **mandatory warranty classification on catalogue items** (FR-REV-003): M37 owns the catalogue; today obligations are typed per contract with an obligation type that already distinguishes the service-type workmanship warranty.
- **Recognition run record** (FR-REV-016) and the **revenue waterfall / RPO** reports: recognition runs per schedule (daily cron) and every posting is a recognition line; a run header is evidence, not a capture.
- **Settlement cycle, counterparty configuration, reserve policy, self-billing document** (FR-REV-033/040/043): marketplace settlement is not live (no sellers on fix_real) and the reserve rate is a CCO/CFO policy decision.
- **"No SSP on file" as a hard block** (AUT-REV-03 reads that way): left as a recorded basis ("typed on the contract") so existing contracts keep allocating; switch it to a block once finance has loaded the SSP table.
- **CFO approval**: the spec asks the CFO to approve SSPs, positions and payout-hold releases. There is no CFO group (R-03 is a role record); an Accounting Administrator other than the requester approves until the owner maps R-03. Manual and catch-up schedules already go to the DOFA Tier 4 (CFO) inbox.

## 5. State

- Fix commit **bf2e7108** is on the working branch `fix/a03-live-data-and-pending-work`. It was rebased onto 675f071c (M54, a peer session) and landed by compare-and-swap `update-ref`; the shared checkout was fast-forwarded with `read-tree -m -u`. **Not pushed.**
  - After the rebase, the regenerated `writable.py` was byte-identical to the merged file.
  - The M53 guard (35/35), the M54 guard and the estate page guard all pass on the combined tree.
- **Deployed on fix_real and fix_dev on 17 Nov 2026** on the user's approval, coordinated with the M49 session (mid-deploy of M49 + M54), which owns the single restart:
  1. Backups `fix_real_pre_m53_capture_2026-11-17.dump` (48 MB, 50,616 entries read back) and `fix_dev_pre_m53_capture_2026-11-17.dump` (40 MB, 50,429 entries) in `_migration/backups`.
  2. `-u cd_subscription,cd_settlement_ext,cd_p03_portal` from the shared checkout at bf2e7108: fix_real 12:57 UTC, fix_dev 12:58 UTC. Both exited 0 with no errors. cd_subscription is now 19.0.1.3.0 and cd_settlement_ext 19.0.0.4.0 on both databases.
  3. The five new tables and the obligation's SSP columns exist on fix_real (empty).
  4. **8069 restarted at 13:42 UTC** by the M49 session (one combined restart for M49, M52, M53 and M54, after its `-u cd_p03_portal` from the shared checkout at 4e851753): PID 52108 became 78988 (supervisor 23964), `/web/login` 200, 155 modules loaded, 0 errors in the log since. Before it, fix_real had 0 of 83 `cd_` modules behind the code.
  5. **Live on fix_real**: the running bundle (`web.assets_web.min.js`, attachment 10304) carries the four new M53 forms and the Payout Holds list; the served code is the shared checkout, whose M53 controller serves the four new records.
  6. **8090 restarted at 13:46 UTC** by the M49 session, after the M52 session upgraded `cd_ap_ext` on fix_dev (13:43-13:44 UTC): PID 45588 became 66868, `/web/login` 200, 151 modules loaded, 0 errors since. fix_dev had 0 of 80 `cd_` modules behind the code. The fix_dev bundle carries the four new M53 forms and the five new tables exist (empty). **M53 is live on both servers.**
- The `cd_fixed_asset_ext` gap seen after the upgrade (database 19.0.1.2.0, checkout 19.0.1.1.0) closed when the M49 session landed f9c56604 on the branch before the restart.
- Clean-up done: both private clones (`fix_test_m53`, `fix_test_m53mut`) and their filestores, the private server and its launch.json entry, and the build worktree. Branch `fix/m53-capture-buttons` is kept.
