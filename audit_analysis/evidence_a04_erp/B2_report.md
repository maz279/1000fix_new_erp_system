# B2 report: M36 quotation/tender and M08 contracts (21 Nov 2026)

Of 39 findings:
- **34 FIXED**;
- **2 OWNER:** the Tender Committee and Legal Reviewer roles;
- **2 PARTIAL**, waiting on others: M08-F4 (OU, which needs B5's `_ar_posting_dims`) and M08-F5 (recognition side, B3);
- **1 DEFERRED:** M36-F13 (the cd_doc_suite PDF).

## P0
- **M36-F1:** the tender award is taken ex-VAT (by the quotation ratio, else the M51 rate). The contract carries `term_value` and `accepted_total`. 115,000 now bills 100,000 + VAT.
- **M08-F1:** `fix.contract.suspension` windows. Suspended days are never billed, and `extend_term` bills the term value once.
- **M08-F2:** termination:
  - sets `date_end` and re-prices the term;
  - the `contract.terminated` consumer cancels drafts beyond the end, bills the stub, raises a credit note for over-billing, and drafts the penalty invoice (role `contract_penalty_income`, default 400109).
- **M08-F3:** the top-up consumer raises an invoice, with the amount checked against the record.

## P1
- **M36-F2:** VAT via M51 per line; `vat_rate` is computed and guarded. The walker and the billing plan never invoice above `accepted_total`.
- **M36-F3 / M08-F6:** calendar-month periods with a frequency (monthly / quarterly / half-yearly / annual) and timing (arrears / advance). The last period absorbs value and VAT rounding.
- **M36-F4:** contract and subscription invoices find their quotation, so advances are applied.
- **M36-F5:** the `quotation.declined` consumer declines the M01 estimate and schedules the device return (which drives the existing A02 fee path); other quotations get a close-out to-do.
- **M36-F6:**
  - bonds get an instrument, margin and charges, posted through M19;
  - accounts: `cd_quotation.account_code.bond_margin` 100035, `bond_deposit` 100031, `bond_charges` 500226;
  - retention is withheld at issue (Dr `contract_retention_receivable` 100031 / Cr AR), with `action_release_retention`.
- **M36-F7:** the `tender.variation_approved` consumer turns a variation into a contract amendment.
- **M08-F7:** a term amendment that would end before the billed-through date is refused.
- **M08-F9:** the contract SLA policy wins in `_fix_match_sla_policy`.
- **M08-F10:** a family registry `CONTRACT_FAMILY_PROFILES`; every asset family is covered.
- **M08-F11:** the cron `ir_cron_contract_service_credits` raises service-credit credit notes.
- **M08-F12:** DOFA and legal review on the total term value; an amendment crossing 1M needs `action_legal_review`.
- **M08-F8:** the UI is honest about the families; reports read the registry.
- **M08-F4 (partial):** every contract invoice carries the branch.
- **M08-F5 (partial):** family revenue roles `cd_billing_engine.account_code.contract_revenue_<family>` (amc and managed 400107, rental 400108, otherwise 400100). Arrears bill to it directly; advance periods record `revenue_account_id`.

## P2/P3
- **M36-F9:** the tender contract gets the BOQ scope, retention and LD terms; the pricing quotation is closed.
- **M36-F10:** new `fix.quotation.entitlement`; entitlements, SLAs and devices are copied to the contract.
- **M36-F11:** reports read through `scoped()`; formulas corrected.
- **M36-F12:** estimate acceptance needs evidence and publishes `estimate.quotation_accepted`.
- **M36-F14:** cost is built from the lines and M15.
- **M36-F15:** PO, template and language are frozen once decided.
- **M36-F16:** bid scoring inverted for competition and risk.
- **M36-F17:** resends do not reset attempts; there is a lifetime cap.
- **M08-F13:** profitability at cost over the term. OWNER: `cd_contract_core.labour_cost_per_hour`.
- **M08-F14:** an entitlement needs a quantity; an explicit 0 means unlimited.
- **M08-F15:** reset period and exhaustion policy.
- **M08-F16:** a PM dispatch cron.
- **M08-F17:** auto-renew off by default; alerts for all contracts; no renewal draft while a renewal quote is open.
- **M08-F18:** the walker catches up expired contracts.
- **M08-F19:** KPIs scoped and on Dhaka dates, with the 90-day expiring count.
- **M08-F20:** a contract printout (`report/fix_contract_report.xml`).
- **M08-F21:** scope amendments are prorated.
- **M08-F22:** the OCA contract is archived.

## Tests
- **New:** 49 functions (56 cases), all passing.
- **Mutants:** 22 of 22 red.
- **Suites:**
  - cd_contract_core: 1 failure (M11 rounding, B1's);
  - cd_quotation: clean;
  - billing engine (walker and recognition): clean.
- **Failures owned by others:**
  - `test_f5_document_vaults` (B1's new m11 form has no vault);
  - registry coverage of `fix.partner.rate.change` / `fix.reseller.draw` (B5);
  - the m38 `posting_state` column (B4);
  - the m40 `draw_ids` form (B5).

## Needs from others
- **B3:**
  - M53 recognition should credit `revenue_account_id` for advance periods;
  - `consume_quotation_accepted` should check the aggregate model.
- **B5:** `_ar_posting_dims` (done by B5).
- **cd_doc_suite:** quotation PDF issue date and terms; map `fix.contract` in `p03_commercial_docs.doc_print_url`.
- **OWNER:** bond encashment loss account (500906 vs 500226).

## Owner decisions
- Account defaults: 400107 / 400108 / 400100, 400109, 100031, 100035 / 100031 / 500226.
- `labour_cost_per_hour`, and whether the penalty carries VAT.
- Tender Committee and Legal Reviewer holders.

## Deploy
- Versions: cd_contract_core 19.0.1.3.1, cd_quotation 19.0.1.5.2.
- `-u`: cd_contract_core, cd_billing_engine, cd_quotation, cd_p03_portal.
