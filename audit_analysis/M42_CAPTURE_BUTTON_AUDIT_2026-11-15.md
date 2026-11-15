# M42 Supplier Relationship & Performance — Sub-Module Capture Audit (2026-11-15)

**Trigger.** The user observed that not every M42 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md`. Sections used: §3.1 scope, §5 FR-SRM2-001…034, §9 BRU-SRM2-01…20, §10.1 owned entities, §13 roles.
- Code:
  - `cd_p03_portal/static/src/a06/m42.js` (the page registry);
  - `cd_p03_portal/controllers/a06/m42.py` (surfaces and report packs);
  - `cd_vendor_portal/models/fix_supplier.py` and `fix_supplier_controls.py` (the supplier register).

## 1. What was there (HEAD 75711b30)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| # | Page | "+ New" | Form chips | Defect |
|---|---|---|---|---|
| 1 | Supplier Profiles | Supplier Profile | Supplier Profile | The profile had no **classification** (FR-SRM2-002, P0) and no **risk tier** (FR-SRM2-004, P0). There were no role-based contacts (§10.1 `fix.supplier.contact`). |
| 2 | **Segmentation** | **none** | **none** | The mapping said `create: false`. The segment was typed on the profile by anyone with write rights, although it sets the review cadence (BRU-SRM2-18) **and the DOFA tier a qualification needs** (`qualification_tier_by_risk`). A steward could lower it to escape a CFO approval. |
| 3 | Qualification | Qualification Questionnaire | Qualification Questionnaire | The activation-gate and re-qualification lists had no chip. No questionnaire **template** existed (FR-SRM2-008, P0). No brand-authorisation evidence existed (FR-SRM2-015, BRU-SRM2-05, H). |
| 4 | Documents & Validity | Supplier Document | **none** (`forms: []`) | The bank-detail change list (FR-SRM2-018) sat on **no page**. |
| 5 | **Contracts & Price Lists** | Supplier Document | **none** | The page listed supplier *documents* of type "contract". No agreement (FR-SRM2-021), agreed price (FR-SRM2-022), price-change approval (FR-SRM2-023), or consignment terms (FR-SRM2-024) existed anywhere. All four are P0. So BRU-SRM2-14 (no PO above the agreed price) and BRU-SRM2-15 (consignment terms are M15's authority) could not even be stated. |
| 6 | Scorecards | Scorecard | **none** | The review-cycle list on this page had no chip. |
| 7 | Corrective Actions | CAR | CAR | — |
| 8 | Risk Assessment | Risk Assessment | Risk Assessment | — |
| 9 | Compliance Screening | Compliance Screening | **none** | No chip. |

In summary:
- Page 2 captured nothing.
- Page 5 captured the wrong record.
- Pages 3, 4, 6 and 9 offered only part of what they list.
- The node guard fails **21 of 38** checks on HEAD; only pages 7 and 8 pass.

## 2. What was built

### Backend — `cd_vendor_portal` 19.0.1.3.0

**New file `models/fix_supplier_terms.py`.** It loads after `fix_supplier` and `fix_supplier_controls`, so the models it extends exist.

| Record | What it enforces |
|---|---|
| `fix.supplier`: `classification`, `risk_tier`, `contact_ids`, `agreement_ids` | The 12 FR-SRM2-002 classes. **After onboarding (status ≠ prospect) the segment is fixed**: a direct write is refused, an unchanged re-send from the form passes, and the form shows it read-only. |
| `fix.supplier.segment.review` | A steward proposes the new segment with its basis (spend, criticality, risk tier, reason); the current segment is snapshot at proposal. A Supplier Approver **other than the proposer** approves, and that writes the segment and publishes `supplier.segment_changed`. A reject needs a reason. It is refused if the supplier's segment moved since the proposal. |
| `fix.supplier.contact` | Role-based contacts (commercial / logistics / quality / finance / escalation). A phone or an e-mail is required. |
| `fix.qualification.questionnaire` | A template per category and risk tier: its questions, its **mandatory evidence** (document types, validated), and a pass mark that only ever **raises** the estate-wide threshold. |
| `fix.supplier.qualification.questionnaire_id` + approval check | Approval is refused while the template's evidence is not verified and unexpired, or the score is below its pass mark. **BRU-SRM2-05**: an *authorised distributor* also needs a verified "Brand / OEM Authorisation" (new document type). The questionnaire is final once the qualification is decided. |
| `fix.supplier.agreement` | Framework / supply / consignment / service / courier. It holds the term, committed value and volume, service levels, penalties, rebates, notice period, renewal mode and the uploaded signed copy. A Supplier Approver **other than the drafter** puts it in force. It is refused without the signed copy, after its end date, or for a suspended or blocked supplier. **A consignment agreement needs all seven consignment terms** (BRU-SRM2-15). Once in force, its terms are fixed. Terminating needs a reason. A daily cron warns at 90/60/30 days (a to-do on the supplier, once each) and expires it on its end date (BRU-SRM2-19). |
| `fix.supplier.price.list` | An agreed price per part under an agreement **in force**. A second person approves it. Overlapping approved prices for the same supplier, part and currency are refused. The price is then fixed. |
| `fix.supplier.price.change` | Submit (justification, an effective date after the current price started; the old price is snapshot). A Supplier Approver **other than the requester** approves it: the old price closes the day before, and a new approved price opens. A reject needs a reason. It is refused if the price moved since submission. |
| `fix.purchase.order` price gate | **BRU-SRM2-14**: when a PO's approval is requested and when it is sent, a line above the approved agreed price in force for its supplier, part and currency is refused, with "submit a price change in M42". A part with no agreed price is not checked. |

Data:
- 4 sequences (SSEG / SAGR / SPRC / SPCH);
- 1 cron (agreement expiry);
- ACLs: plain users read; stewards create and write; approvers write; nobody deletes;
- company isolation rules for agreements and prices (regenerated by `generate-isolation-rules.py`).

### Workspace — `m42.js`, `controllers/a06/m42.py`, `writable.py` (regenerated)

| # | Page | "+ New" (live click) | Form chips (live click) |
|---|---|---|---|
| 1 | Supplier Profiles | + Supplier Profile | Supplier Profile, Supplier Contact |
| 2 | Segmentation | **+ New Segment Review** | Segment Review |
| 3 | Qualification | + New Qualification Questionnaire | Qualification Questionnaire, Questionnaire Template, Activation Gate, Re-Qualification |
| 4 | Documents & Validity | + New Supplier Document | Supplier Document, Bank-Detail Change |
| 5 | Contracts & Price Lists | **+ New Supplier Agreement** | Supplier Agreement, Agreed Price, Price Change |
| 6 | Scorecards | + New Scorecard | Scorecard, Supplier Review |
| 7 | Corrective Actions | + New CAR | CAR |
| 8 | Risk Assessment | + New Risk Assessment | Risk Assessment |
| 9 | Compliance Screening | + New Compliance Screening | Compliance Screening |

Other changes:
- New lists: Supplier Contacts, Segment Reviews, Questionnaire Templates, Supplier Agreements, Agreed Price List, Price Changes. Each has its workflow actions; reject and terminate ask for the reason.
- The bank-change list is now on page 4.
- The Supplier Agreement form has more than 15 fields, so it is tabbed: Agreement & Term / Service & Commercial / Consignment Terms.
- The Supplier Profile form shows Classification (required) and Risk Tier. The qualification form shows its Questionnaire.
- **Contract Coverage** now counts a supplier as covered by an agreement in force today, or by a verified signed-contract document. It shows the agreement end date. The coverage numerator was also wrong: it counted contracts of *inactive* suppliers.

## 3. Evidence

| Check | Result |
|---|---|
| Node guard `cd_p03_portal/tests/test_m42_capture_buttons.py` (engine's own fregCreate/fregPanels) | **38/38** on the fix; **21/38 fail** on HEAD |
| Live ORM `cd_vendor_portal/tests/test_m42_capture_live.py` (non-admin stewards and approvers, rolled back, private DB `fix_test_m42`) | **17/17** |
| Regression: `cd_vendor_portal` + `cd_requisition` + all `cd_p03_portal` tests on `fix_test_m42` | **4,413 passed**, 286 skipped, 2 failed, 1 collection error, in 34 min. The failures were: (1) `test_m42_W01`, which was mine: the new contact and questionnaire models lacked the workflow guard every M42 register carries. They now carry it, and the M42 control, live and guard suites pass **105/105**. (2) M30/1 "Branch Master" in `test_submodule_create_button`, which fails identically on the main checkout without these changes. The collection error is `test_supplier_residency.py` (a relative import in a tests folder with no `__init__`), which is pre-existing. |
| Private UI server (8072, worktree code): click sweep of the 9 pages | Every page shows the "+ New" and chips in the table above. The tabbed agreement form renders. |
| Server probe from the page: every M42 list, report and form endpoint | 40 calls, 0 errors |
| ruff 0.8.4 (the pinned version): check + format | clean |

## 4. Live data (fix_real, read-only, 15 Nov)

- There are 658 suppliers. All are *qualified*, all are *transactional*, and none has a classification.
- There are 0 contract documents, and so far 0 agreements, prices, contacts and templates.
- Supplier Steward: 2 holders. Supplier Approver: 2 holders. So every two-person step can be staffed.
- **Effect of the deploy on existing suppliers:**
  - Their segment can now be changed only through a segment review, because none is a prospect.
  - Saving one of their profiles in the workspace will ask for its classification (FR-SRM2-002 requires every supplier to be classified). Superuser data loads are not affected.

## 5. Not built (spec gaps left for the owner)

- **BRU-SRM2-13 single-source control and concentration (FR-SRM2-033).** There is still no critical-part flag, alternate-source record, or Supply Chain Director role (already reported in the A06 final pass).
- **BRU-SRM2-03 per-category qualification.** A qualification is still per supplier. The approved categories sit on the profile.
- **Provisional activation (BRU-SRM2-12)** and the supplier development plan (FR-SRM2-032, P2).
- **Configurable scorecard weights (FR-SRM2-028):** the weights are still fixed at 35/30/20/15.
- Category strategy (FR-SRM2-034, P2), rebate tracking (FR-SRM2-025, P2), P05 self-registration and supplier-facing scorecards.
- **The price gate checks only lines whose agreed price is in the PO's currency.** A foreign-currency agreed price is not converted.
