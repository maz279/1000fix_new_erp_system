# R2 findings: M36 quotation/tender and M08 contracts (20 Nov 2026)

Measured on fix_real_a04 with every probe rolled back. Probes are in `%TEMP%\a04erp\R2\` (p1-p5).
Counts: 39 findings. P0 4, P1 16, P2 15, P3 4.

## P0
- **M36-F1: a tender award bills VAT twice.**
  - `bid_value` / `awarded_value` include VAT, but `fix_tender.py:712` stores `awarded*12/months` as the pre-VAT `annual_value`, and the walker then adds 15%.
  - A 115,000 award is billed 132,250.
  - Fix: `_create_contract` divides out VAT, or uses the pricing quotation's `value`.
- **M08-F1: a suspended contract is billed for the suspension.**
  - On resume the walker back-bills every unbilled past period, and `extend_term` lengthens the term as well.
  - 69,041 was billed for the suspended months; the term total came to 196,602.74 on 120,000.
  - Code: `fix_contract_billing_walker.py:104-135`, `fix_contract_capture.py:1194-1232`.
- **M08-F2: termination moves no money.**
  - The penalty is never invoiced, and no credit or refund is raised. `contract.terminated` has no consumer.
  - The stub days are never billed, because the walker skips terminated contracts.
  - A 50,000 penalty produced 0 invoices, and 24 days went unbilled. Code: `fix_contract_ops.py:745-790`.
- **M08-F3: an entitlement top-up is never billed.**
  - `contract.entitlement_topped_up` has no consumer: a 20,000 top-up produced 0 invoices.
  - Code: `fix_contract_capture.py:520-557`.

## P1
- **M36-F2: the invoice need not match the accepted quotation.**
  - `vat_rate` is a free, writable field, while invoices use M51's 15%.
  - No check compares billing-plan or contract invoices with the accepted total (BRU-QTE-10 / AUT-QTE-15): accepted 70,350, invoiced 77,050.
- **M36-F3: term conversion bills short, long and leap-year terms wrongly.**
  - Conversion stores `value*12/months`, but billing uses `days/365`.
  - Error: 6 months −986.30, 1 month −794.52, a leap year +328.77, 24 months +328.77.
- **M36-F4:** advances on contract and subscription quotations are never applied (`fix_quote_supply.py:844-862`).
- **M36-F5:** `quotation.declined` has no consumer, so a decline raises no diagnostic fee and no return task (FR-QTE-041).
- **M36-F6: bonds, EMD and retention never reach the GL.**
  - Activating or releasing a bond posts nothing. Encashment posts Dr 500906 / Cr 100102 (Bank Suspense).
  - 100035 BG Margin, 100031 Security Deposit and 500226 Tender expense exist but are unused.
  - The 10% retention is computed but never withheld.
- **M36-F7:** `tender.variation_approved` has no consumer, so an approved variation never reaches the contract.
- **M36-F8:** Tender Committee is held only by admin.
- **M08-F4: contract and quotation invoices have no branch.**
  - The GL dimension falls back to "Main Operating Unit"/RETAIL.
  - Cause: M20 `_ar_posting_dims` drops the operating unit.
- **M08-F5:** contract revenue is recognised to 400100 rather than 400107 (AMC/Managed Service) or 400108 (Rental), and arrears billing is deferred unnecessarily.
- **M08-F6: billing uses fixed 30-day periods.**
  - A 12-month AMC gets 13 invoices plus a 5-day stub.
  - There is no frequency setting and no advance billing.
  - Per-invoice VAT rounding gives 17,100.01.
- **M08-F7:** a term amendment can end a contract before its billed-through date with no credit (98,630 billed vs a new value of 59,507).
- **M08-F8:** only 5 of the 14 families exist, but the UI says 14.
- **M08-F9:** contract SLAs never reach M01/M05. M01's SLA selection ignores the contract, and `reconcile_service_sla` is never called.
- **M08-F10:** only the AMC family gets zero-charge cover. RAMC and managed-service visits are charged and never draw down entitlement (`fix_contract.py:1685`).
- **M08-F11:** `_scheme_credit` has no caller, so service credits never reach M20.
- **M08-F12: the ≥1M legal review is weak.**
  - Legal Reviewer is held only by admin.
  - The threshold is tested on annual value, so a 3-year 2.7M contract skips legal review.
  - An amendment that crosses 1M does not re-open the review.

## P2
- **M36-F9:** a won tender's contract has no scope lines or retention/LD terms, and the pricing quotation stays approved forever.
- **M36-F10:** a contract made from an accepted proposal has 0 entitlements, SLAs and assets.
- **M36-F11:** KPIs are unscoped by company and date; the conversion denominator and approval-cycle formula are wrong.
- **M36-F12:** an estimate accepts without evidence and publishes `quotation.accepted`, and the M39 consumer does not check the source model.
- **M36-F13:** the quotation PDF omits terms and exclusions and prints the creation date instead of the issue date.
- **M36-F14:** cost and margin are typed, not taken from M15 cost.
- **M08-F13:** profitability uses selling prices as cost and compares one year's revenue with lifetime cost.
- **M08-F14:** an entitlement saved without a quantity means unlimited (50/50 draws succeeded).
- **M08-F15:** entitlements have no period, no reset and no exhaustion policy.
- **M08-F16:** no PM dispatch cron.
- **M08-F17:** auto-renew defaults on and drafts a renewal without notice, which blocks the M36 renewal quotation; there are no expiry alerts.
- **M08-F18:** if the walker misses the end date, the last period is never billed.
- **M08-F19:** KPIs are unscoped and omit expiring contracts.
- **M08-F20:** no contract printout.
- **M08-F21:** asset attach/detach is not prorated.

## P3
- **M36-F15:** the PO reference, template and language stay editable after acceptance.
- **M36-F16:** the bid score counts risk and competition as positives.
- **M36-F17:** the acceptance code's attempt counter resets on every resend.
- **M08-F22:** every activation creates an empty OCA contract while the OCA invoicing cron is active.

## Measured as correct
- **Quote to cash:**
  - A value of 114,000 (5% discount) is approved at Tier 3, then issued.
  - Acceptance comes to 131,100 and produces a draft contract with an annual value of 114,000.
  - 13 walker invoices total 131,100.01.
  - The issue posts Dr 100201 / Cr 200401 / Cr 200902; recognition posts Dr 200401 / Cr 400100.
- **Quotation locking:**
  - Terms and lines are locked after acceptance.
  - Versioning works: v1 becomes superseded and v2 needs approval again.
  - The author cannot approve their own quotation.
- **Columns:** all m36/m08 cols exist. The template form offers `sequence`, which is not writable.

## Facts on fix_real_a04
- **Data:** 0 contracts, quotations and tenders.
- **Configuration:**
  - `contract_auto_billing` = 1;
  - VDS 200903;
  - bond encashment 500906 / 100102;
  - the e-signature provider secret is unset;
  - the code's default accounts 121000, 400000, 211000, 212000 and 450000 do not exist on this chart.
- **Role holders:**
  - DOFA tiers: 69 / 49 / 10 / 3 / 1;
  - Contract Officer 39, Contract Manager 5;
  - Legal Reviewer 1 (admin);
  - Tender Committee 1 (admin);
  - Quotation Manager 47;
  - Accounting Administrator 4.
- **Approval matrix:** 0 M63 matrix rows for the quotation, contract, tender and bond domains.
- **Events with no consumer:** declined, variation approved, terminated, topped up, asset attached/detached, expired, activated, amended.
