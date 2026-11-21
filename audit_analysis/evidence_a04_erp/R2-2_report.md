# R2-2 (round 2, M09/M39 deferred items), 21 Nov 2026

## Fixed
- **M09-F13: brand rules enforced at submit.**
  - The technician needs a valid M22 certification for the brand.
  - Labour is capped at the brand's allowance.
  - Every fault code must translate to a brand code.
  - Parts evidence comes from the job's actual M15 issues.
  - The resubmission window is checked.
- **M09-F12:** owed, age and ageing bucket on the claim; daily chase cron, escalating to Finance at level 2.
- **M09-F15:**
  - per-claim and claim-count limits, plus depreciation, are set on the product and locked on the policy;
  - DOFA value bands use param `protection_claim_dofa_bands`, unset by default.
- **M09-F16:**
  - `fix.warranty.claim.submission` records what was sent and its SHA-256 hash;
  - fault codes translate through the existing M37 `fix.fault.brand.map`;
  - new "Brand Partner Performance" pack.
- **M37-F5:** `fix.warranty.product.catalogue_def_id` links the product to its catalogue item.
- **M39-F16:** a price increase waits for "Send Price Notice" and `price_change_notice_days` (default 30). A customer request (with evidence) or a signed contract amendment is exempt.
- **M39-F17:**
  - usage consumers for msp, data and rental, idempotent and failing loudly;
  - a service gate on suspend/cancel/pause events;
  - M01 intake warns or refuses (`suspended_service_policy`, default warn).
- **M39-F11:**
  - new field `fix.contract.billing_engine` (walker or subscription), so one engine bills each contract;
  - Managed Services default to subscription (owner decision D8; confirm).
- **M37-F5 (M39 side):** `plan_def_id` sets the cycle and price from the R2-3 hook.

## Tests
- New: 29.
- Mutants: 18/18 killed.
- Final run: 337/337.
- Existing tests that encoded old behaviour, updated: 5.

## Deferred
FR-SUB-025: late-arriving usage is not yet re-rated into the next open period.

## Deploy
- Versions: cd_warranty_claims 19.0.2.3.2, cd_subscription 19.0.1.4.3, cd_contract_core 19.0.1.3.2.
- `-u` all three.

## Owner
- DOFA bands, chase days, notice days, service policy.
- Plan limits.
- Confirm the Managed Services billing default (D8).

## Needs from others
- `billing_engine` on the M08 form (lead).
- `fix.storefront.return.line` has no screen (R2-1).
- `alliance_scheme_ids` on the M11 promotion form (done by R2-3).
- The document-vault ratio test.
