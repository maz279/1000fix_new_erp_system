# R2-4 (round 2, M40 deferred items), 21 Nov 2026

## Fixed
- **F23: deal conflicts.**
  - Conflicts now cover other partners' open and earlier registrations, their leads within the attribution window, and open M07 opportunities.
  - A won deal or a qualified lead is handed off to an M07 `crm.lead`, idempotently, with guarded attribution (`fix_partner_r2.py` `_inherit`s crm.lead).
- **F26: MDF.** A rebate of kind 'mdf' is refused, with a pointer to MDF funds and claims.
  - A post-migrate (19.0.0.3.2) cancels unapproved legacy MDF rebates; fix_real has 0.
  - The comarketing pack reads MDF claims.
- **F28: alliance benefits.**
  - `fix.alliance.scheme.benefit_promotion_id` is now an M11 `fix.promotion`, member-only.
  - Eligibility grants it through `price_for` with a verified check context; a forged context is dropped.
- **F25 (rest): partner TDS through M51.**
  - Rebate and MDF payout TDS is measured with M51's `find_rate("tds", code)`, using param `cd_settlement_ext.partner_tds_rate_code` (default commission, s.94, 10%) and ×1.5 per default.
  - Each deduction is recorded with `fix.withholding.line._fix_record_deductions`.
- **F14 follow-up:** a new pack, `authorisations_expiring`, scoped and banded T-180/90/30.

## Deferred
Referral payout-run TDS: `fix_settlement_ext._fix_measure_tds` (A08) applies only the no-PSR uplift. The M51 no-TIN default needs that change.

## Tests
- New: 17, plus 9 rewritten. 52/52 pass.
- Mutants: 21/21 killed.
- Suites: about 524 passed. 7 failed and 3 errored, all owned by others:
  - A02 `p1p2` ×2, the bridge env;
  - c7 marketplace ×4, the M12-F15 acceptance gate (R2-1);
  - m53 subscription price ×1 (R2-2);
  - the P03 `test_declared_gap_reports` comarketing fixture ×3 (patch at `%TEMP%\a04erp\R2-4\NEEDS_p03_test_declared_gap_reports_patch.py`).

## Deploy
`-u` cd_partner (19.0.0.3.2, adds the cd_crm_ext dependency) and cd_p03_portal; cd_settlement_ext needs a restart.

## Owner
- The TDS rate code.
- Confirm that a promotion named by an alliance becomes member-only.
- Confirm that F26 refuses instead of routing.
