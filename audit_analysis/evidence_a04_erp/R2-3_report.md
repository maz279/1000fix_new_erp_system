# R2-3 (round 2, M11/M37 deferred items), 21 Nov 2026

## Fixed
- **M11-F19: pricing mechanisms.**
  - **FR-PRC-012, labour pricing:** a labour_hour rate card × SRT (from the applied `fix.srt.baseline`, else the item's `standard_labour_time`) feeds `price_for`.
  - **FR-PRC-017, volume breaks:** new `fix.price.break`.
  - **FR-PRC-020 / BRU-14, channel differential:** new `fix.channel.differential`, released by a second releaser; fail-closed while the spread parameter is unset.
  - **FR-PRC-010 / BRU-17, public indicative band:** `GET /api/v1/pricing/indicative`, rate-limited.
  - **FR-PRC-032, override log:** `fix.price.override.log` is append-only, wired into M01 estimate lines and into first use of a below-floor override.
  - **FR-PRC-036 / 045:** `price_exceptions` and `price_consistency` packs.
  - **AUT-PRC-08..12:** `fix.price.review`, created by consumers and crons:
    - 08 discontinued items retire their cards;
    - 09 an SRT re-baseline is held until a second releaser accepts it;
    - 10 a cost scan flags cards below the floor;
    - 11 consistency scan;
    - 12 leakage scan.
- **M37-F5:**
  - plan-def hook `_fix_subscription_vals`;
  - the catalogue item's `repair_warranty_days` reaches the M01 repair warranty (the longer of policy and item wins).
- **M37-F7:** the live successor is offered (`price_for` returns `successor_item_id`, plus `action_use_live_successor`).
- **M37-F11:**
  - FR-CAT-046: an impact preview is required before restrict, discontinue or revise;
  - FR-CAT-007: numbering rules (`fix.catalogue.numbering`, no gaps, `legacy_codes`);
  - FR-CAT-015: skill band and brand certification requirements.
- **M11-F15:** the VAT rate follows the item's VAT class (exempt or zero → 0); `price_for` returns `price_incl`.

## Tests
- New: 26, all passing.
- Suites: 283 passed, 0 failed; cd_catalogue all pass.
- Mutants: 18/20 killed. The 2 survivors are each blocked by a second, independent layer.

## Deploy
- Versions: cd_rate_card 19.0.1.2.2, cd_catalogue 19.0.1.4.2.
- `-u`: cd_catalogue, cd_rate_card, cd_p03_portal.
- cd_service_order changed logic only.

## Owner
- `max_channel_spread_pct`, `margin_target_pct`, `leakage_alert_pct`.
- Labour rates and skill bands.
- Numbering masks.
- Whether the repair warranty may be shorter than the policy.
- Pricing Officer holders.

## Needs from others
- **R2-2:** `plan_def_id` on the subscription, plus the hook call.
- **M09:** the warranty product should link the catalogue item.
- **M36/M38/M12:** call `record_override`.
- **M02/M31:** gate dispatch on `_fix_technician_qualified`.
- **Lead:**
  - regenerate the event schema for `catalogue.srt_rebaselined`;
  - `pricing.*` / `catalogue.item_activated` consumers belong to the M36/M38/M12/M25 spec owners.
