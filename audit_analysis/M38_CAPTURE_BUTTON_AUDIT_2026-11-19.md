# M38 E-Commerce & Digital Storefront — capture-button audit (19 Nov 2026)

**Question.** Not every M38 sub-module page has a relevant data-capture button. What should each page capture, what does the codebase do, and what was fixed?

**Sources checked.**
- The spec: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M38_ECommerce_and_Digital_Storefront.md`. §5 holds FR-ECM-001..056, §8 the order and RMA lifecycles, §9 BRU-ECM-01..20, §10.1 the 17 owned entities, §13 the roles.
- The Function Register: `contracts/nav/registry.json`, M38 `freg` (10 sub-modules, 92 functions). It holds names and counts only, so each page's purpose comes from the §5 FR group it covers.
- The workspace and engine:
  - `cd_p03_portal/static/src/a04/m38.js` and `controllers/a04/m38.py`;
  - `p03_workspace.js` `fregCreate` / `fregPanels`, evaluated in node exactly as the browser runs them.
- The models: `cd_storefront` (cart, order, two return models sharing one refund mixin, slot), M15 `fix.graded.stock`, M01 `fix.service.order`, the finance bridge `cd_storefront_finance`.
- Live data, read-only: **fix_real holds 0 carts, orders, returns, RMAs, slots and graded units**; fix_dev holds 2 slots. Each storefront role has one holder on fix_real (the admin).

No earlier M38 capture audit exists; this is the first pass.

## 1. Each page: what it should capture, what it did, verdict

| # | Sub-module (spec) | Before (HEAD 742e46bc) | Verdict |
|---|---|---|---|
| 1 | Storefront & Browse (FR-ECM-001..007, 013; §3.1 #20 content) | Listed **carts**; no "+ New", no form chip. Storefront content (banners, landing and policy pages) — which §3.3 says M38 *owns* — had no model. | **Gap** |
| 2 | Merchandising (FR-ECM-008..012) | **"+ New Graded Stock Item"**: a refurbished unit M14 grades and M15 stocks and values. Collections, featured sets, cross-sell and up-sell had no model. | **Wrong record** |
| 3 | Cart (FR-ECM-015..017; §13 R08/R34 assisted ordering) | Cart list `create: false`; no chip. Staff could not capture a cart for a customer on the phone or at the counter. No item-terms acceptance existed (BRU-ECM-07, hard block). | **Gap** |
| 4 | Checkout & Payments (FR-ECM-018..028) | Page `create: false`, no chip. COD governance (FR-ECM-025, BRU-ECM-08 hard block) had no record: any COD order of any value was accepted. Checkout promotions list sat on no page. | **Gap** |
| 5 | Online Orders (FR-ECM-040..045) | Online Order chip only (read-only; orders come from checkout). Order modification within policy windows (FR-ECM-044) had no record — a slot could not be changed at all. | **Gap** |
| 6 | Stock Exposure (FR-ECM-014, BRU-ECM-04 hard block) | **"+ New Graded Stock Item"** again. The exposure policy (entity `fix.stock.exposure.policy`) did not exist, so nothing limited what is sold online. | **Wrong record** |
| 7 | Returns & RMA (FR-ECM-046..051) | + New RMA Request (correct). The return window and restocking fee were one global setting; the spec's per-category return policy (`fix.return.policy`) had no record. The portal's returns list sat on page 8. | **Partial** |
| 8 | B2B Commerce (FR-ECM-052..054, BRU-ECM-14) | Listed **storefront returns** — nothing B2B. No corporate account, PO reference, agreed catalogue or client approval chain existed. | **Wrong record** |
| 9 | Recovery & Analytics (FR-ECM-029, 055, 056) | Open-cart list, no capture. The recovery report said "No recovery-campaign model exists (declared gap)"; its "recovered" column could never be ✓ (it only listed carts with no order). | **Gap** |
| 10 | Service Booking Commerce (FR-ECM-031..033, BRU-ECM-11) | "+ New Delivery Slot". A repair could not be booked: no booking record, no service slot type, no path to the M01 service order. | **Partial** |

## 2. What was changed

### New records — `cd_storefront/models/fix_storefront_capture.py` (module 19.0.0.2.0)

| Page | Record | Rule it carries |
|---|---|---|
| 1 | `fix.storefront.content` — banner, landing, campaign or policy page; title and body in English **and Bengali**; slot, audience, validity, image | Published only by a **Storefront Merchandiser** (new role, spec R23), only bilingual (FR-ECM-002: Bengali is the default), a banner only with its image. Published content is frozen; retire and re-issue to change it. |
| 2 | `fix.storefront.collection` — collection, featured set, cross-sell, up-sell; manual items or a category rule; "shown with" item | A cross/up-sell names its anchor item and cannot offer the item alongside itself. Publication refuses an item not for sale and runs the M37/M11 sale check on every item. Frozen once published. |
| 3 | **Assisted cart** (fields on `fix.storefront.cart`): channel (web / app / assisted / corporate, stamped by the server), captured-by, delivery address / mode / slot, payment method, item-terms acceptance (method, reference, who/when) | **BRU-ECM-07**: a cart holding a refurbished unit is not placed until the customer's acceptance is recorded (an OTP, signed form or recorded call needs its reference). "Place Order" runs the normal storefront checkout — server prices, gateway check, stock reservation. An ordered cart's checkout data is frozen. |
| 4 | `fix.storefront.cod.rule` — largest COD order, delivered-order history needed above a value, open COD orders allowed | Written by a Payment Officer, **activated by a Storefront Manager who did not write it**; one active rule per company. While active, **BRU-ECM-08** is enforced at every placement. With no active rule, COD behaves as before. |
| 5 | `fix.storefront.order.change` — address, slot or delivery-mode change, with the customer's reason | **FR-ECM-044**: accepted only until dispatch (delivery mode only before payment); applied by an operator **other than the one who recorded it**; a slot change re-checks the new slot's capacity. |
| 6 | `fix.stock.exposure.policy` — one item or one category; locations sold from; buffer in units and %; longest promise; sold online yes/no | Activated by another Storefront Manager. **BRU-ECM-04 / T-05**: checked when a line is added, when its quantity changes and again at placement — online sale is limited to stock on hand in the policy's locations less the larger buffer; "sold online = no" withdraws it. An item's own policy wins over its category's. Strict mode (no policy = not sold online) is a switch, `cd_storefront.exposure_policy_required`, **off** by default. |
| 7 | `fix.storefront.return.policy` — category (or default), return window days, change-of-mind restocking fee % | Activated by another Storefront Manager. The order's return window and the grade-B restocking fee now come from the policies its items fall under (longest window, lowest fee); without one, the configured default applies as before. |
| 8 | `fix.storefront.corporate.account` — the client company, its **own approvers** (its contacts only), approval threshold, PO required, agreed categories | Activated by another Storefront Manager. **Corporate order** = a cart on the account: **BRU-ECM-14** — placed only with the client's PO reference, inside the agreed catalogue, by one of the client's buyers, and (above the threshold) after "Record Client Approval" names one of the account's approvers and the approval reference. Approved lines are frozen. |
| 9 | `fix.storefront.recovery.attempt` — the follow-up of an abandoned cart: channel, outcome, note | A log: only an open, unordered cart; the outcome cannot be rewritten or deleted. "Ordered after contact" is computed. The Abandonment Recovery report now counts contacts and measures recovery as followed-up carts that became orders. |
| 10 | `fix.storefront.service.booking` — customer, **their** device, branch, service slot, fault, photo, channel | The device must be registered to the customer and the slot a **service** slot (new slot type, with a branch) with room — bookings now count against slot capacity. **Confirm** (operator) raises the **M01 service order** (BRU-ECM-11: the booking never holds service state), idempotently, with the photo attached. |

### Changes to existing code
- `fix_storefront_refund.py`: the return window and restocking fee read the order's return policy.
- `fix.storefront.cart.line`: the P03 grid may re-post the unchanged server price; a changed price is still refused. Lines of an ordered or client-approved cart are frozen.
- `fix.storefront.slot`: `service` slot type, `branch_id`; `booked` counts orders **and** service bookings.
- `fix.storefront.order`: shows the corporate account and PO reference of its cart.
- Security: new role **Storefront Merchandiser** (implied by Storefront Manager); ACLs for the 9 models (staff read; the owning role writes); company / operating-unit isolation rules regenerated (`generate-isolation-rules.py`, only cd_storefront's file kept); sequences `SFC/` and `SFB/`.

### Workspace (`static/src/a04/m38.js`)

| # | "+ New" now | Chips | New / changed list |
|---|---|---|---|
| 1 | **+ New Storefront Content** | Storefront Content | `M38-content` (Publish, Retire) |
| 2 | **+ New Storefront Collection** | Storefront Collection | `M38-collections` (Publish, Retire) |
| 3 | **+ New Assisted Cart** | Assisted Cart | `M38-carts` now captures; Record Terms Acceptance, Place Order |
| 4 | **+ New COD Rule** | COD Rule | `M38-cod-rules`; Checkout Promotions (M11 view) placed here |
| 5 | **+ Request Order Change** | Online Order, Order Change | `M38-order-changes` (Apply, Refuse) |
| 6 | **+ New Stock Exposure Policy** | Stock Exposure Policy | `M38-exposure`; graded stock list is read-only ("from M15") |
| 7 | + New RMA Request (unchanged) | RMA Request, **Return Policy** | `M38-return-policies`; the portal's returns list moved here |
| 8 | **+ New Corporate Commerce Account** | Corporate Commerce Account, Corporate Order | `M38-corporate-accounts`, `M38-corporate-orders` (Record Client Approval, Place Order) |
| 9 | **+ Record Recovery Contact** | Cart Recovery Contact | `M38-recovery-attempts` |
| 10 | **+ New Service Booking** | Service Booking, Storefront Slot, Delivery Slot | `M38-service-bookings` (Confirm → M01, Cancel) |

- `controllers/a04/m38.py`: SURFACES for the 9 models with their actions whitelisted; cart actions added; recovery report rewritten.
- `controllers/a04/writable.py`: regenerated with `form_fields.py --a04`; only M38 hunks changed. No stamp or state field is writable.

## 3. Evidence

All runs used worktree `m38cap-wt` (branch `fix/m38-capture-buttons`, from 742e46bc) on the private database `fix_test_m38` (a clone of fix_test_m25c2, `-u all` from the worktree: 0 "has no table", cd_storefront 19.0.0.2.0; `cd_storefront_finance` installed on it as on fix_real).

| Run | Result |
|---|---|
| Page guard `cd_p03_portal/tests/test_m38_submodule_capture.py` (node evaluates the engine's `fregCreate`/`fregPanels` over the real fragments; 18 tests) | **18/18 pass**; on HEAD's workspace files **14 fail** (page 7 was already right) |
| Live suite `cd_storefront/tests/test_storefront_capture.py` (17 tests as clerk, operators, merchandiser, payment officer, two Storefront Managers) | **17/17 pass** |
| Regression: every `cd_storefront` and `cd_storefront_finance` suite | **115/115 pass** (one existing refurb test now records the terms acceptance first, as BRU-ECM-07 requires) |
| Static estate guards: estate page standard, A04 registry / sub-module mapping / children / write-whitelist, all-module mapping, submodule create button, picker | **all pass** |
| A04 guards in cd_contract_core that hard-code the shared checkout path, re-run as copies pointed at the worktree | Same failures as HEAD: 8 M36 step forms with no tabs; document-vault ratio 62/142 here vs 60/132 on HEAD (both below 50%) |
| Mutation check: defects re-introduced one at a time | see §3.1 |
| ruff 0.8.4 check + format | clean |

### 3.1 Mutation check

26 defects re-introduced one at a time (`scratchpad m38/mutate.py`); each must turn its suite red. **26/26 killed.**

- Model (22): terms gate off; COD value limit off; COD open-orders limit off; policy author approves own; exposure withdrawal ignored; exposure buffer ignored; exposure not re-checked at placement; order change applied by its recorder; order change after dispatch; corporate PO not required; client approval skipped; any partner approves a corporate order; agreed catalogue ignored; approved lines editable; recovery log editable; booking for someone else's device; bookings not counted in slot capacity; content published without its Bengali title; content published without its Bengali body; unsellable item merchandised; return-policy window ignored; assisted cart not stamped.
- Workspace (4): page 3 captures nothing; page 8 lists returns again; page 6 offers graded stock; page 5 captures nothing.
- The first run left one survivor: "published in English only" was caught only by the *next* check's message ("both English and Bengali"). The test now asserts each refusal separately and a mutant for the body check was added.

### 3.2 Private-server check (port 8141, `fix_test_m38`, signed in as the clone's admin)

The browser pane was hidden, so the OWL page rendered empty; the workspace's own endpoints were driven from the signed-in page instead:
- **17/17 M38 lists** served by `/p03/model/records` with **0 dropped columns**; **15/15 forms** return every field they declare (`/p03/model/form`).
- An **assisted cart** saved with its line through `/p03/model/write` (the form's own payload) came back as channel "Assisted (staff)"; **Place Order** made order `SF/2026/000579` and set the cart to Ordered.
- **Content** publication was refused without the Bengali title, then published once it was given.
- A **COD rule** written by the admin could not be activated by the same admin ("recorded by you; another Storefront Manager decides it").

## 4. Not done / still open (owner decisions)

- **Who approves.** Policies (COD, exposure, return, corporate account) need a Storefront Manager who did not write them. fix_real has exactly one holder of each storefront role (the admin), so nothing can be activated there until a second person holds Storefront Manager and the new **Storefront Merchandiser** role is granted (spec: R23 Marketing Manager, R17 Inventory Manager, R26 Finance Manager).
- **Exposure strict mode** (`cd_storefront.exposure_policy_required`) is off: turning the storefront off for every uncovered item is the Inventory Manager's decision.
- **COD OTP above a threshold** (FR-ECM-025) and fraud scoring (AUT-ECM-11): no OTP service exists to verify against; not built.
- **Credit terms** (BRU-ECM-19): no "on account" payment rail exists in the storefront or the finance bridge; the corporate account records no credit limit rather than an unenforced one.
- **Two return models** (`fix.storefront.return` from the portal, `fix.storefront.rma` from the workspace) still exist side by side; they share one refund mixin. Merging them needs a data migration — none on fix_real today (0 rows each), so now is the cheapest time.
- Not built from the spec: reviews/ratings moderation (FR-011, P2), wishlist (FR-012), payment-attempt ledger (`fix.payment.attempt`), allocation records (`fix.online.allocation`), funnel and search logs (system-written), rental booking (FR-037, P2), trade-in at checkout (FR-038, P2), subscription checkout (FR-039), CSV bulk order (FR-054).
- Slot capacity comes from the slot record, not from live M02/M55 capacity (FR-ECM-032).

## 5. State
_(landing, deploy and push recorded below once done)_
