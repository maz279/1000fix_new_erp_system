# M36 Quotations & Tenders — Sub-module Capture Audit, Pass 2 (2026-11-19)

**Question.** The user again saw M36 sub-module pages without a relevant data-capture button, after the first pass (14 Nov, `M36_CAPTURE_BUTTON_AUDIT_2026-11-14.md`) had given every page a "+ New".

**Method.** Pass 1 counted buttons. This pass reads each page against what the spec says it captures, record by record:

- Spec: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M36_Quotation_Estimation_and_Tender_Management.md`
  - §5 FR-QTE-001..048, §8 guards, §9 BRU-QTE-01..18, §10.1 owned entities, §11 automations.
- Code at HEAD `742e46bc` (shared branch `fix/a03-live-data-and-pending-work`):
  - `cd_quotation` models, `cd_p03_portal/static/src/a04/m36.js`, `controllers/a04/m36.py`, `writable.py`.
- The pages were evaluated the way the browser evaluates them: node runs the engine's own `fregCreate` / `fregPanels` over the real registry (the pass-1 guard fixture).

## 1. Findings — what each page still could not capture

| # | Page | Spec record the page is about | On HEAD |
|---|---|---|---|
| 1 | Estimate Build-Up | FR-QTE-009 second-opinion / technical review of a high-value or contentious estimate (§8.1 TECHNICAL REVIEW state) | **No record, no button.** Nothing stopped an estimate under dispute being quoted. |
| 2 | Quotation Object | FR-QTE-018 (P0) governed terms, assumptions and exclusions — entity `fix.quotation.term` | **Free text only** (`delivery_terms`, `warranty_terms`). No library, nothing marked a term non-standard. |
| 2 | Quotation Object | FR-QTE-024 renewal quotation from an expiring contract (BRU-QTE-18) | **No capture.** M08 drafts a renewal *contract*; nothing produced the renewal *offer*. |
| 4 | Approval Routing | FR-QTE-027 (P0) / BRU-QTE-08 (H): a non-standard term needs CCO **and** CFO approval | **No record, no rule.** Any wording was issued on the value-band approval alone. |
| 4 | Approval Routing | FR-QTE-028 / BRU-QTE-14 (H): no issue to a customer on credit hold or over the limit without a Finance override | **No gate, no override.** M20's credit profile was never read by M36. |
| 5, 7 | Customer Loop, e-Signature | FR-QTE-042: acceptance on a phone call with a recorded consent reference | **No capture.** Only the code, the provider e-signature or a signed copy. |
| 7 | e-Signature | BRU-QTE-17 (H) / T-14: a disputed quotation on legal hold, never purged | **No record, no rule.** |
| 9 | Tender & Bid | FR-QTE-046 / BRU-QTE-15 (H): document checklist; no submission while a required document is outstanding — entity `fix.tender.document` | **Not built** (pass 1 left it as an owner gap; it needs no owner decision). Submission checked the compliance matrix only. |
| 9 | Tender & Bid | FR-QTE-048 / BRU-QTE-16 (H): outcome with a structured loss reason — entity `fix.tender.outcome` | **Free text.** "Record Loss" asked for any sentence. |
| 10 | Templates & Bilingual Gen | FR-QTE-018 standard terms library | **None.** |

Pages 3, 6 and 8 capture what the spec says (pass 1); nothing new was needed there.

## 2. What was built

### Models — `cd_quotation/models/fix_quote_capture2.py` (cd_quotation 19.0.1.4.0)

Loaded after every file it extends (its own `# isort: split` block), so ruff's import sort cannot reorder it.

| Record | Rules |
|---|---|
| `fix.quotation.standard.term` (library) | Only the Commercial Manager creates, edits or deletes. A term already quoted is archived, not deleted. `mandatory` = every quotation of its kind must carry it before submission. |
| `fix.quotation.term` (spec entity) | Set while the quotation is a draft not awaiting approval. Wording equal to the library's = standard, no approval. Any other wording is a **deviation**: it needs a reason, and `action_decide_deviation` by the Commercial Manager (CCO slot) **and** Finance / Accounting Administrator (CFO slot) — two different people, neither the quotation's nor the term's author. Either can reject (with a reason). New wording clears the approvals. Copied into a revision. |
| `fix.quotation.credit.override` | Finance only, never the author, and only when M20's credit profile shows a hold, or open receivables + this quotation over the limit. One per quotation version; immutable; revocable by Finance. |
| `fix.quotation.legal.hold` | Placed by a Quotation Author with a dispute reference. While active the quotation cannot be deleted, even by the superuser. Released only by the Commercial Manager, never by the person who placed it. |
| `fix.estimate.review` | Requested by anyone on staff, naming someone else as reviewer. Only the named reviewer records cleared / returned, with findings. |
| `fix.tender.document` (spec entity) | Bid Coordinator only, frozen once the bid is submitted. The upload must be the uploader's own. Each new upload bumps the version and stores the checksum. A document must be valid past the submission deadline. |
| `fix.tender.outcome` (spec entity) | Bid Coordinator, for a submitted tender. A governed loss reason and "what was learned" are required. Our bid and the price gap are stamped. It records the loss (or the issuer's cancellation) on the tender with its reason code. |

**Gates on existing flows:**

- **Submit / approve / issue** (`_readiness_problems`) now also refuse when:
  - a deviation awaits approval or was rejected;
  - a mandatory library term is missing;
  - the quotation's estimate has a technical review awaiting a decision, or was returned.
- **Issue** (`action_send`) and **acceptance** (`_accept`) refuse a held or over-limit customer without an unrevoked override for this version (BRU-QTE-14).
- **Tender submission** refuses while a required document is missing or expired. The submitted pack is sealed by a SHA-256 over its documents' checksums.
- **Every loss carries a governed code.** A loss recorded by the old method is filed as "Other". The workspace no longer offers or serves the free-text "Record Loss" (BRU-QTE-16).

**New quotation actions:**

- `action_apply_standard_terms`: attaches the library terms, word for word.
- `action_record_phone_acceptance(consent_ref, called_number)`: needs a consent reference and the customer's own number, and is never run by the author. It stamps `acceptance_method = phone`.
- A renewal quotation is created by naming `renewal_of_contract_id`. It inherits the customer, OU and family. It starts the day after the contract ends. Its scope lines carry the contract's escalation. Only one renewal may be in progress per contract. On conversion, the new contract is linked as the renewal term.

**Security:**

- New ACL rows: staff read; each role writes as listed above.
- Company and operating-unit rules come from `generate-isolation-rules.py`. Only cd_quotation's own new models were taken; the generator's pre-existing drift elsewhere (11 modules, plus `fix.sales.proforma`) was left untouched.

### Workspace — `m36.js`, `controllers/a04/m36.py`, `writable.py` (regenerated with `form_fields.py --a04`)

| # | Page | New captures (chips) | New lists |
|---|---|---|---|
| 1 | Estimate Build-Up | **Request a Technical Review**, **Record Technical Review Outcome** | Technical Reviews |
| 2 | Quotation Object | **Add a Term / Assumption / Exclusion**, **Quote a Contract Renewal**; row action *Attach the Standard Terms* | Quotation Terms & Exclusions, Renewal Quotations |
| 4 | Approval Routing | **Decide a Term Deviation**, **Record a Credit Override (Finance)** | Term Deviations Awaiting CCO / CFO, Credit Gate Overrides |
| 5 | Customer Approval Loop | **Accept by Phone (recorded consent)** | — |
| 7 | e-Signature | **Accept by Phone**, **Place a Legal Hold**, **Release a Legal Hold** | Legal Holds |
| 9 | Tender & Bid | **Add a Document to the Submission Pack**, **Record a Tender Outcome (not won)**; "Record Loss" row action removed | Submission Pack, Tender Outcomes & Loss Reasons |
| 10 | Templates & Bilingual Gen | **New Standard Term** | Standard Terms Library |

Other workspace changes:

- The tender form shows the missing-document count, the pack hash and the governed loss reason. The award fields "awarded to" and "winning value" are now read-only there, because the outcome record sets them. The compliance grid gained the requirement owner (FR-QTE-045).
- The quotation record shows the credit gate, the legal hold and the renewal source.
- "Tender Win/Loss" now lists the losses by governed reason.

## 3. Evidence

- **Static guard** `cd_p03_portal/tests/test_m36_capture_pass2.py` (19 checks, on the engine's own evaluation):
  - **19/19 fail on HEAD `742e46bc`**;
  - **19/19 pass** on the build;
  - the pass-1 guard stays 45/45.
- **Live test** `cd_quotation/tests/test_m36_capture_pass2_live.py`:
  - 15 tests, run as non-admin role holders through `/p03/model/write` and `/p03/model/action` on the private clone `fix_test_m36c2` (cloned from `fix_test_m25c2`; 9 lagging peer modules upgraded first);
  - **15/15 pass**.
  - With the pass-1 live suite, the A04 M36 controls and both guards: **154/154**.
- **Mutation check: 19/19 mutants caught.** The first run had 3 survivors, each a real test gap or dead code:
  - the author holding the approver role (deviation; credit override);
  - the loss code written twice.
  - Two tests were added, the duplicate write was removed, and the 3 mutants were re-run red.
  - The source was restored by sha256 after each mutant.
- **Regression on `fix_test_m36c2`: 1,086 passed, 0 failed.**
  - Covered: the cd_quotation full suite, plus the A04 forms / registry / sub-module mapping / write whitelists, all-submodule mapping, declared gaps, estate pages, picker, tell-me, report export, screens wiring and the A12 whitelist.
- **UI walk** (headless Chromium, private server on port 8181 running the worktree code, a non-admin Commercial Manager + Finance + Bid Coordinator user):
  - all 10 pages show their "+ New" and every chip listed in §2;
  - each chip opens its form with its inputs;
  - 21 screens render;
  - a standard term saved through the form is in the database;
  - **0 console errors**.
- **Live data impact:** fix_real holds 0 quotations, tenders, estimates, credit profiles and in-force contracts, so no existing record meets the new gates.

## 4. Left for the owner

1. **Name the CCO and CFO.** The estate has no such roles. The Commercial Manager (Quotations) signs for the CCO and the Accounting Administrator for the CFO; neither may be the author, and the two must be different people.
2. **The standard terms library is empty on fix_real.** Until the Commercial Manager loads it, every term written on a quotation is a deviation, and nothing is mandatory.
3. **Credit profiles.** The gate reads M20's `fix.credit.profile`. A customer without a profile is not gated.
4. **Not built (no capture gap, but still spec):**
   - automatic renewal quotations at the contract's lead time (AUT-QTE-10; the capture exists, the cron does not);
   - the reminder sequence (FR-QTE-040);
   - the bulk estate quotation from an asset upload (FR-QTE-022);
   - the side-by-side version comparison (FR-QTE-013);
   - the tokenised customer view (T-05; pass 1 owner gap 4).
5. **Still open from pass 1:** the diagnostic-fee invoice policy; a second Tender Committee member on fix_real.
