# M11 Pricing & Rate Cards: sub-module capture audit, pass 2 (18 Nov 2026)

**Reported:** not all M11 sub-modules have a relevant data-capture button.
**Spec:** `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` (§5 FR-PRC-001…052, §8 lifecycles, §9 BRU-PRC rules, §10 entities, §16.4 migration).
**Code:** `cd_p03_portal/static/src/a04/m11.js`, `controllers/a04/m11.py`, `cd_rate_card`, `cd_quotation` (discount approval).
**Branch:** `fix/m11-capture-pass2`, based on `03f2d7b4`.
**Previous pass:** `all_working_folder/1000fix-2/function wise check/m11/M11_Submodule_Capture_Audit_2026-11-13.md`. It gave every page a "+ New" or a chip, and built the brand reimbursement rate.

## 1. Method

1. **Spec, page by page.** The Function Register (`contracts/nav/registry.json`, source 97) names 11 sub-modules and their function counts, but not the functions. Each page was therefore read against the spec section for its subject, and against the entity §10.1 assigns to it. A page passes only if its capture can record what that section requires, not merely if it shows a button. That was the lesson of the M02 and M04 second passes.
2. **Code, as the browser runs it.** Node ran the workspace engine's own `fregCreate` and `fregPanels` over the real registry. That gave each page's "+ New", its chips and its lists (guard `test_m11_submodule_capture.py`).
3. **Data.** fix_real and fix_dev hold 0 rate cards, 0 discount approvals, 0 simulations and 0 contracts, plus 1 promotion on fix_dev. No live record is affected by the new rules.

## 2. What the pages offered at HEAD

| # | Page | "+ New" at HEAD | What the spec asks of it | Finding |
|---|---|---|---|---|
| 1 | Pricing Engine | none (engine-written trace) + Simulation chip | FR-PRC-001…010 | Capture correct. **The simulation asked for its inputs as raw JSON** (`{"quantity":…}`): unusable at a branch counter (AC-06) |
| 2 | Price Books | Price Book | FR-PRC-011, 025 | Button correct (see §6 for what the book still lacks) |
| 3 | Rate Cards | Rate Card | FR-PRC-012, 014 | correct |
| 4 | Parts Pricing | Rate Card preset to *Part* | **FR-PRC-013 (P0):** price parts by markup on cost, banded markup by cost tier, or a provenance-grade differential | **Wrong record.** Only a fixed price per part code could be recorded. The ~18,000-row parts list (§16.4) is a markup scheme and had nowhere to go |
| 5 | Customer/Contract Pricing | Rate Card preset to tier 99 | **FR-PRC-016 (P0)**, BRU-PRC-11, **AC-08**: bound to an M08 contract, for its term, lapsing at expiry | **Contract typed, not named.** `contract_no` was free text: a typo priced a contract that does not exist, and the rate never lapsed with its contract |
| 6 | Brand Reimbursement | Brand Reimbursement Rate | FR-PRC-015 | correct (built 13 Nov) |
| 7 | Discount Governance | Discount Approval | FR-PRC-026…036; **BRU-PRC-13 (H)**, **FR-PRC-030**, KPI-C11-07 | **No reason code.** A discount request carried free text only. There was no governed reason list, so the hard rule "a discount above the threshold needs a reason code from the governed list" could not exist |
| 8 | Promotions | Promotion | **FR-PRC-037:** a time-boxed price on a *defined item and audience set* | **No item scope.** A promotion discounted every item it was used on |
| 9 | Adjustment Rules | Dynamic Price Rule | **FR-PRC-018/019 (P1)**: zone/distance and express/emergency/after-hours/weekend/holiday premiums (entity `fix.price.adjustment`) | **Wrong record.** The only record was the W7 marketplace/storefront *dynamic* rule (demand surge, off-peak). No premium or surcharge could be recorded |
| 10 | Simulation & Trace | Price Simulation | FR-PRC-002/003 | Same JSON defect as page 1 |
| 11 | Versioning & Approval | Price Book Version | **FR-PRC-024, BRU-PRC-16 (H):** a mass change across a filtered set with preview, approval, scheduled activation and one-step rollback; an immediate one needs the CCO | **Missing record.** Prices moved one rate at a time through single change requests |

## 3. What was built

### `cd_rate_card` 19.0.1.2.0 (new `models/fix_m11_capture.py`, now depends on `cd_contract_core`)

All new records share one release lifecycle, the module's existing control:
- A **Pricing Officer** records the record; a plain user only reads it.
- A **Price-Book Releaser who is not the author** releases it from the M63 inbox (BRU-PRC-07).
- Released terms never change. A new version with its own date supersedes the old one, which keeps its window. A back-dated version that would rewrite history is refused.

**Page 4: `fix.parts.price.scheme`** (FR-PRC-013), with **`fix.parts.price.band`** lines.
- **Scope:** part category, brand and provenance grade, each optional. The most specific scheme in force wins (`scheme_for()`).
- **Methods:**
  - markup on cost;
  - banded markup by cost tier. Bands start at 0 and meet without a gap or an overlap; this is checked on release;
  - markup plus a per-grade adjustment (genuine / OEM / aftermarket / refurbished). A grade can never sell below cost;
  - fixed price.
- **Rounding:** to the paisa or to 1/5/10 taka (FR-PRC-008), in Decimal.
- **Bands are frozen** once the scheme leaves Draft.

**Page 9: `fix.price.adjustment`** (FR-PRC-018/019).
- **Types:** express, emergency, after-hours, weekend, holiday, zone and distance.
- **Amount:** a percentage (at most 100%) or a fixed amount, always positive.
- **Applies to** labour, parts, consumables, transport or all lines.
- **Conditions:**
  - zone: the branches in the zone. A zone premium without branches cannot be submitted;
  - distance: a km band;
  - after-hours: an hour window, which may run past midnight.
- **`premiums_for()`** returns each matching premium in force as a named amount. The simulation shows these on the trace (BRU-PRC-02).

**Page 11: `fix.price.mass.change`** (FR-PRC-024, BRU-PRC-16), with **`fix.price.mass.change.line`**.
- **Filters:** line type, product-code prefix and catalogue category. Contract rates stay out unless ticked (BRU-PRC-11).
- **Change:** a percentage or an absolute amount, effective on a date.
- **Preview Affected Rates** lists each released rate with its current price, new price and floor. A rate at or below zero or below its floor **blocks submission**, which is the margin-floor guard of §8.1. A rate that moved since the preview blocks approval and application.
- **Routing:**
  - a future date goes to a Price-Book Releaser and is applied by a daily job on that date;
  - a date of today is **immediate** and goes to the **CCO** (DOFA tier 4) only. The author never decides it.
- **Rollback** is one step, by a releaser, with a reason. It is refused if any rate moved after the change.
- Every price move emits `pricing.price_changed`.
- The approved terms are pinned.

**Page 5: `fix.rate.card.contract_id`** (FR-PRC-016, AC-08).
- A contract rate names its M08 contract. Its number and tier 99 follow from the contract, and its validity defaults to the contract term and must stay inside it.
- A tier-99 card whose number matches no contract is refused.
- The engine skips a contract rate whose contract is not Active/Expiring on the day, so the customer falls back to their tier rate.

**Pages 1/10: the simulation** asks for quantity, customer tier, contract, channel, a price to test against the floor, and premiums, as fields. It also passes the item code to the promotion check.
- **Bug found by the existing suite and fixed:** the new Quantity field's default of 1 overrode the quantity of an older JSON input.

**Page 8: `fix.promotion.catalogue_item_ids`** (FR-PRC-037).
- A promotion for named items discounts only those items' codes. With no code given, it discounts nothing.
- The item scope is frozen once the promotion leaves Draft.

### `cd_quotation` 19.0.1.3.0 (new `models/fix_discount_reason.py`)

**Page 7: `fix.discount.reason`** (BRU-PRC-13, FR-PRC-030), plus `reason_code_id` on `fix.discount.approval`.
- **The list is governed:** Pricing Officers keep it, and codes are upper-cased.
- A code that was used is never renamed or deleted, only archived.
- **The rule:** a discount above the threshold (`cd_quotation.discount_reason_threshold_pct`, default 0) cannot be sent for approval without a reason code. The rule applies **once the company has at least one active code**: a request cannot be held hostage to an empty list.
- A decided request keeps its reason.
- The **Discount Register by Approver** report gains a Reason Code column.

### Workspace (`m11.js`, `controllers/a04/m11.py`, `writable.py` regenerated)

| # | Page | "+ New" now | Chips now | New lists |
|---|---|---|---|---|
| 4 | Parts Pricing | **Parts Pricing Scheme** (5 tabs + cost-band grid) | Parts Pricing Scheme, Rate Card, Price Floor | Parts Pricing Schemes |
| 5 | Contract Pricing | Rate Card at tier 99, **Contract (M08)** picker | Rate Card | (Contract Rates shows the contract) |
| 7 | Discount Governance | Discount Approval (**+ Reason Code**) | Discount Approval, **Discount Reason Code**, Discount Policy, Price Floor | Discount Reason Codes |
| 8 | Promotions | Promotion (**+ Items It Applies To**) | Promotion | n/a |
| 9 | Adjustment Rules | **Price Premium / Surcharge** | Price Premium, Dynamic Price Rule | Premiums & Surcharges |
| 1/10 | Engine / Simulation | Simulation (**fields, no JSON**) | Price Simulation Request | n/a |
| 11 | Versioning & Approval | Price Book Version | Version, Price Change, **Mass Price Change** | Mass Price Changes, Mass Change Preview (read-only) |

Pages 2, 3 and 6 are unchanged.

## 4. Evidence

All runs used a private copy of `fix_test` (`fix_test_m11b`, `-u all` from the worktree, 0 errors) and a private server on port 8097. Nothing ran against fix_real or fix_dev.

| Check | Result |
|---|---|
| Guard `test_m11_submodule_capture.py` (node runs the engine's own `fregCreate`/`fregPanels`) on the **HEAD** registry | **12 of 31 red**: contract named, parts scheme, premiums, mass change, reason code, simulation fields, promotion items, and 5 lifecycle whitelists |
| Same guard on the fix | **31/31** |
| `cd_rate_card` suite (existing + 28 new in `test_m11_capture_pass2.py`) | **90 passed**, 0 skipped. The existing contract-lane tests now create the real M08 contract they price (`tests/contract_helpers.py`) |
| `cd_quotation` `test_m11_discount_reason.py` | **6/6** |
| Estate page standard, A04 mapping/registry/write-whitelist, all-submodule mapping, report-export standard, A04 forms-show-children | **942/942** together with the two suites above |
| Mutation check: 16 controls broken one at a time | **15 killed.** One survivor, *releaser may be author*, is equivalent: the M63 engine never routes a task to the author (`test_an_author_who_is_also_a_releaser_never_releases_their_own`), so the record's own check is a second layer that no test can reach |
| Live endpoints as three roles (officer, releaser, CCO), `live_probe.py` | **43/43**: all 19 M11 lists serve every column; scheme + 2 bands saved in one write, released from the releaser's M63 inbox, then frozen; a back-dated second scheme of the same scope refused; 150% premium and branch-less zone premium refused; typed non-existent contract refused; mass change previewed (2 rates), routed past the plain releaser to the CCO, applied +10%, rolled back in one step; a plain user refused a reason code; simulation computed from fields |
| Headless click walk of the 11 pages (`walk.mjs`, Playwright) | Every page shows its "+ New" (page 1 by design only its chip) and the forms open with their tabs: p4 Parts Pricing Scheme (5 tabs), p7 Discount Reason Code, p9 Price Premium / Surcharge (4 tabs), p11 Mass Price Change (3 tabs). 0 page errors |
| Ruff 0.8.4 check + format | clean |

**Defects only the tests caught (fixed):**
- The new Quantity field's default of 1 overrode a quantity from the older JSON input (`test_simulation_is_computed`).
- A first draft refused a tier-3 card with a contract number with the wrong message, which hid the original "contract rates carry min_tier 99" rule.

**By design (noted, not changed):** a Price-Book Releaser implies the Pricing Officer role, so a releaser may also keep the reason list.

## 5. State

- Built on `fix/m11-capture-pass2` (worktree `1000 fix/m11cap2-wt`).
- `contracts/events/pricing_price_changed.json` was regenerated for the second publish site.
- No live data changes meaning: fix_real and fix_dev hold 0 rate cards and 0 discount approvals.

## 6. Not done here (owner decisions or larger builds)

1. **Price books are empty containers.** The spec's `fix.price.rule` and the book's scope (channel, segment, branch group, precedence, validity: FR-PRC-011) are not built. Rate cards are priced on their own, outside any book version. This is an architectural build of the engine (CD-C11-01), not a capture button.
2. **Labour rate by repair level, skill class, brand and delivery mode** (FR-PRC-012 `fix.rate.card.line`): a labour rate is still one price per product code and tier.
3. **Price lock and the override log** (FR-PRC-005/032) are system-written by quotations; they are not built.
4. **Marketplace fee schedule (FR-PRC-023), price experiments (FR-PRC-050), competitor prices (FR-PRC-052)** are not on any of the 11 pages and not built.
5. **The parts scheme and the premiums are not yet read by the estimate or quotation.** They are read by the simulation (premiums) and by `scheme_for()` / `price_for()` (parts). Wiring them into M01/M36 line pricing changes what customers are charged, which is a business decision.
6. **Reason codes:** the business must load its list. Until it does, the rule does not block.
7. **The default threshold of 0** makes every discount above the agent's own band need a code once the list exists. The owner may set `cd_quotation.discount_reason_threshold_pct`.
