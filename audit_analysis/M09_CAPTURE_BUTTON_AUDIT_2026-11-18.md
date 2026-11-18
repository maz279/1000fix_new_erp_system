# M09 Warranty & Claims: second capture audit (18 Nov 2026)

**Reported:** not all M09 sub-module pages have a relevant data-capture button.
**Scope:** the 12 sub-module pages of the M09 workspace (`static/src/a04/m09.js`), measured against:
- the M09 specification (`1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md`): 66 FR-WTY requirements, 22 BRU-WTY rules, 22 owned entities (§10.1);
- the code: `cd_warranty_claims`, `cd_device_registry` (`fix.warranty`) and `controllers/a04/m09.py`.

The first pass ([M09_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M09_CAPTURE_BUTTON_AUDIT_2026-11-13.md)) gave six pages a "+ New" and marked the rest as list steps. Its §6 listed what it could not fix with a button: brand rules, protection policies, inbound claims, write-off and defective returns.

## 1. What was there (shared tip 4f09c1db)

Measured with the engine's own `fregCreate` / `fregPanels`, run in node over the real registry:
- 6 of 12 pages showed a "+ New" (1, 5, 7, 8, 9, 11).
- Read against the spec, **8 pages could not record what the spec says is recorded there**. In each case the record did not exist anywhere in the estate.

| Page | What it offered | What the spec says is captured there | Verdict |
|---|---|---|---|
| 1 Warranty Register | Register entry, transfer. A **"Void Warranty"** list button voided cover on a typed reason | FR-WTY-010, **BRU-WTY-17 (H)**: a void condition (unauthorised repair, liquid, tampering, seal breach) is *evidenced* before it refuses cover; owned entity `fix.warranty.void` | **Rule broken**: cover could be voided with no evidence |
| 4 Entitlement Evaluation | Nothing (verdict computed) | The verdict is computed, but the void conditions it applies are entered (FR-WTY-010) | Missing |
| 5 Protection Products | "+ New Protection Product". The "Protection Policy" chip opened a **warranty register row** | FR-WTY-015..024: the **sold policy** (number, customer, device, premium, term, waiting period, excess, limits); FR-WTY-017 / BRU-WTY-11 pre-sale inspection; FR-WTY-036 / BRU-WTY-15 reserve from issue. Entities `fix.protection.policy`, `.inspection`, `.reserve` | **Missing**: no plan could be sold, activated, cancelled or reserved |
| 6 Claim Assessment | Nothing. It re-listed brand claims | FR-WTY-027..036 (all P0/P1): a customer's claim on a plan: intake, damage assessment, waiting period (**BRU-WTY-12 H**), limits (BRU-WTY-14), excess before fulfilment (**BRU-WTY-13 H**), decision, fulfilment. Entity `fix.protection.claim` | **Missing** |
| 8 Brand Submission | "+ New Brand Claim". "Brand Rules & Formats" **listed protection products** | FR-WTY-040 (P0), T-03: each brand's rule set as data. The evidence list was fixed in code (all 7 items for every brand), the window a fixed 72 h. Entity `fix.brand.claim.rule` | **Missing** |
| 9 Decisions & Appeals | "+ New Claim Appeal" | FR-WTY-047: the brand's **request for information**. FR-WTY-049: an appeal with additional evidence (the appeal had no evidence field) | Partly missing |
| 10 Reconciliation | Per-claim "Record Bank Receipt" only | FR-WTY-053: one brand payment matched across claims, unmatched amounts surfaced (T-08); FR-WTY-054: signed period statement; FR-WTY-055 / **BRU-WTY-07 (H)**: write-off with SoD; FR-WTY-057 / **BRU-WTY-19 (H)**: defective-part return before recovery | **Missing** (4 records) |
| 12 Fraud Detection | Nothing (signals computed) | **BRU-WTY-21**: a flagged claim is *investigated* before settlement; FR-WTY-051: a confirmed finding blocks the claim | Missing |
| 2, 3, 7, 11 | Request Verification; Open Comeback; + New Evidence; + New Recall | Steps on existing records or already captured | OK |

Also found:
- "Policy Lifecycle" listed the **IAS 37 provision policies** (M53 accounting configuration), not policies sold.
- "Loss Ratio by Product" declared the actuarial loss ratio a gap, because no premium was recorded anywhere.

## 2. What was built

`cd_warranty_claims` 19.0.2.2.0, new file `models/fix_m09_capture.py` (imported last). Every decision is a method that checks its role. Where the spec asks for it, the person who prepared a record cannot decide it.

| Page | Record | Rules it enforces |
|---|---|---|
| 1, 4 | **Void Condition** `fix.warranty.void` | Declared by a clerk with a photo or report. Applied only by a Warranty Officer who did not declare it, and only with evidence. **`fix.warranty.action_void` now refuses a typed reason** (BRU-WTY-17); the "Void Warranty" list buttons are gone. The warranty form shows its void conditions |
| 5 | **Protection Policy** `fix.protection.policy` | Sold by a clerk with the premium. Term, waiting period, excess and limit are copied from the product and locked. **Activate** checks: eligibility (device age, owner, no duplicate active policy), a passed inspection where the product needs one, and a declared reserve rate. It then establishes the reserve. **Cancel** (Claim Decision Officer) computes a pro-rata refund and releases the reserve. A daily job expires policies past their term |
| 5 | **Pre-sale Inspection** `fix.protection.inspection` | Photo required; never edited. A fail declines the policy |
| 5, 10 | **Reserve Ledger** `fix.protection.reserve` | Append-only (T-09). Written only by the policy and claim transitions |
| 5 | Protection product | New fields: inspection required, max device age, reserve % of premium |
| 6 | **Protection Claim** `fix.protection.claim` | Intake is refused on an inactive policy or for an incident outside the cover. Inside the waiting period it is **rejected at intake** with the reason. Assessment (value, repair or replace, consistency) yields an explainable fraud score. **Approve** is by a Claim Decision Officer who neither received nor assessed it, within the remaining limit, net of the excess; it tops the reserve up. **Settle** is refused until the excess is collected or waived by another officer, and until the fulfilment is recorded. It consumes the limit, releases the reserve and publishes `protection_claim.settled` |
| 8 | **Brand Claim Rule** `fix.brand.claim.rule` | Versioned. Written by a Claim Decision Officer, activated by **another** one. The previous version retires; an active version is never edited. **The brand claim now reads it**: the evidence pack requires exactly the rule's items, and the submission deadline is the brand's window from job completion. With no rule, the old 7 items and 72 h apply |
| 9 | **Brand Information Request** `fix.warranty.claim.info.request` | Only on a submitted or in-review claim; answered with what was sent. Appeals gain **Additional Evidence** |
| 10 | **Brand Remittance** `fix.brand.remittance` (+ lines) | One bank receipt split across claims of that brand. **Match** (officer) posts each line through the claim's own `action_record_remittance`. A remainder the lines do not cover leaves the remittance "Matched - Amount Unallocated" |
| 10 | **Brand Reconciliation** `fix.brand.reconciliation` | Computes claimed, approved, rejected, paid, outstanding and written off for a brand and period. Signed by an officer who did not prepare it; frozen once signed |
| 10 | **Claim Write-off** `fix.claim.writeoff` | Up to the outstanding balance of an approved claim. Decided by a **Finance Manager** who did not raise, submit or request it (BRU-WTY-07). The claim goes to the new state **Written Off**. Publishes `warranty_claim.written_off` for M20 |
| 10 | **Defective Part Return** `fix.defective.return` | Shipped only with waybill, date and proof. Where the brand's rule requires it, **the claim cannot close until the part is shipped** (BRU-WTY-19) |
| 12 | **Fraud Review** `fix.warranty.fraud.review` | About one brand claim or one protection claim, by an officer who did not raise it; never edited. **Cleared** lets a protection claim scoring 50+ be approved. **Confirmed** blocks it, and blocks a brand claim's submission |

**Workspace** (`m09.js`, `controllers/a04/m09.py`):
- 12 new lists, 11 new forms, chips on pages 1, 4, 5, 6, 8, 9, 10 and 12.
- "Brand Rules & Formats" now lists brand rule sets; products moved to their own list.
- "Policy Lifecycle" lists sold policies; provision policies moved to their own list.
- 13 new surfaces; `writable.py` regenerated.
- Loss Ratio by Product is now measured: claims settled divided by premium written, per product, with the reserve held.
- Fraud Detection adds two rows: protection claims that need review, and confirmed findings.
- Events `protection_claim.settled` and `warranty_claim.written_off`. Registry 548 -> 550: only these two were added, and the generator's unrelated drift was left out.

**Page "+ New" after the fix:**

| Page | Opens |
|---|---|
| 1 | Warranty Register Entry |
| 4 | Void Condition |
| 5 | Protection Policy |
| 6 | Protection Claim |
| 7 | Warranty Claim Evidence |
| 8 | Brand Claim |
| 9 | Claim Appeal |
| 10 | Brand Remittance |
| 11 | Recall Campaign |
| 12 | Fraud Review |
| 2, 3 | none (Request Verification and Open Comeback / Zero-Charge Rework are steps on existing rows) |

## 3. Evidence

All runs were on a private clone of the test database (`fix_test_m09c2`, upgraded to the branch). fix_real and fix_dev were not touched while testing.

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m09_capture_buttons.py`, run by node over the real registry with the engine's own `fregCreate` / `fregPanels` | **57/57 pass** on the fix; on HEAD's `m09.js` + `m09.py`, **37 fail** (each page's capture, chips, list buttons and whitelist) |
| Live ORM suite `cd_warranty_claims/tests/test_m09_capture_live.py`, all as non-admin users with the real roles | **18/18 pass** |
| Mutation check: each of the 25 new rules re-broken in turn (void gate, evidence, SoD on every decision, inspection, device age, reserve, pro-rata refund, waiting period, limit, excess, fraud threshold, confirmed fraud in and out, rule pack, rule window, RFI state, unmatched remainder, write-off cap and SoD, statement SoD, defective return) | **25/25 red** |
| Regression: `cd_warranty_claims` (all), `cd_service_order/test_a02_p0_m01.py`, `cd_device_registry` (all) | **270 pass, 0 fail**. One M01 test changed on purpose: it voided cover on a typed reason, which BRU-WTY-17 now refuses; it now voids through an evidenced condition |
| Registry suites: estate pages, submodule mapping (A04 and all), A04 write whitelist, forms show their children, A04 registry coverage, picker | all pass except `test_no_submodule_page_offers_another_records_button`, which names **M30 Branch Master** and fails identically on the shared tip (a peer's, not M09) |
| Private server on 8141, endpoint probe as the role users (`/p03/model/records`, `/form`, `/write`, `/action`, exactly what the browser calls) | **21 lists**, 0 dropped columns. **18 forms**, every field served. **24/24 capture steps OK**: void applied by a Warranty Officer; policy sold, inspected, activated (reserve 1,200); protection claim received, assessed, approved by another officer, excess collected, settled; brand rule activated by a second officer; RFI answered; remittance matched; statement computed and signed by another; write-off approved by Finance (claim to Written Off); part shipped; fraud review recorded. The 4 IAS 37 provision screens refuse users without an accounting role, as they did before this change (M53's ACL) |
| Same server, browser, signed in as the probe clerk | "+ New" per page: 1 Warranty Register Entry · 4 Void Condition · 5 Protection Policy · 6 Protection Claim · 7 Warranty Claim Evidence · 8 Brand Claim · 9 Claim Appeal · 10 Brand Remittance · 11 Recall Campaign · 12 Fraud Review; none on 2 and 3 (by design). Reconciliation shows its 8 screens and 5 form chips; the remittance form renders its claim-lines grid |

Not verified: a click-through on fix_real itself. fix_real has 0 rows in every M09 model, and its only real users would have to sign in.

## 4. Not built (named, not hidden)

- **Consignment parts governance** (FR-WTY-056, P1), **old-part retention** (FR-WTY-058) and **campaign claim rules / serial ranges** (FR-WTY-059/060): recall campaigns still count units, not serials.
- **Brand partner performance** (FR-WTY-061) as a stored scorecard: the claim reports measure it, but no period record is kept.
- **Certified-technician check** at submission: the rule set records the flag, but the claim does not yet read M22 competencies.
- **A single structured appeal on a protection claim** (FR-WTY-034): a rejected protection claim has a reason, but no appeal record.
- **Reserve rate per product** is a business decision. No product on fix_real has one, so **no protection policy can be activated until a Warranty Officer sets it**. Nothing was invented.
