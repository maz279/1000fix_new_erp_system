# A06 Supply Chain workspace: data-capture audit

Follows the M43 reference (CD-M43-01). Applies to M15, M41, M16, M42 and M44 in
`addons/platform/cd_p03_portal/static/src/p03_modules_meta.js`.

## What was wrong

- The metadata had drifted from `contracts/nav/registry.json`. Screens, sub-modules, KPIs,
  reports and forms were wrong, and three modules carried each other's content: M41 showed
  purchase orders, M42 showed warehouse dock receiving, and M44 showed quarantine.
- Every capture button opened the generic service-order intake modal.
- `cd_inventory` views referenced fields that do not exist (`category`, `brand`, `uom`,
  `parent_id`, `state`), so the module failed to install and no M15 form could open.

## What changed

- Each module entry is regenerated from the registry. That covers groups and screens (ids,
  labels, types), reports, KPIs, cross-links and the function register (`freg`). Registry
  forms are kept verbatim.
- `captures` routes each sub-module and screen to the real Odoo form of an existing `fix.*`
  model. An optional `ctx` supplies form defaults, for example a consignment pre-typed as a
  branch transfer.
- `gaps` lists every sub-module or screen with no backing model yet. Its button explains the
  gap and never opens an unrelated form.
- `TestP03CaptureMap` checks registry alignment and full coverage (capture or declared gap).
  It also checks that targets are real models, that `ctx` defaults are real field options,
  and that A06 screen links resolve.

Coverage: count of sub-modules and screens with at least one capture, out of the total.

| Module | Sub-modules captured | Screens captured | Capture forms | Gaps |
|---|---|---|---|---|
| M15 Spare Parts & Inventory | 7/12 | 8/16 | 9 | 9 |
| M41 Warehouse Management | 1/9 | 1/12 | 3 | 10 |
| M16 Procurement & Sourcing | 4/10 | 4/14 | 4 | 6 |
| M42 Supplier Relationship | 3/9 | 3/11 | 3 | 7 |
| M43 Demand Planning | 9/9 | 10/10 | 14 | 0 |
| M44 Import & Trade Compliance | 2/8 | 2/13 | 1 | 9 |

## M15 · Spare Parts & Inventory

| Capture | Model | Defaults | Sub-modules | Screens |
|---|---|---|---|---|
| Spare Part | `fix.spare.part` | - | 1 | M15-onhand |
| Stock Location | `fix.stock.location` | - | 2 | M15-onhand |
| Stock Issue | `fix.stock.consumption` | - | 5 | M15-movements |
| Van Stock Location | `fix.stock.location` | `default_location_type=van` | 6 | M15-van |
| Reorder Rule | `fix.reorder.rule` | - | 6 | M15-replen |
| Valuation Entry | `fix.inventory.valuation.suspense` | `default_entry_type=revaluation` | 8 | M15-valuation |
| Part Segment Classification | `fix.part.segment` | - | 11 | M15-abc |
| Transfer Request | `fix.consignment` | `default_consignment_type=branch_transfer` | 12 | M15-transfers |
| Return-to-Vendor Consignment | `fix.consignment` | `default_consignment_type=return_to_vendor` | 12 | M15-rtv |

Gaps (no backing model yet, nothing invented):

| Gap | Sub-modules | Screens | Missing |
|---|---|---|---|
| Ownership Class Assignment | 3 | M15-ownership | no ownership-class field or record (6 classes) on any stock model |
| Stock Reservation | 4 | - | only a qty_reserved counter on fix.spare.part; no reservation record |
| Serial / Lot Record | 7 | M15-serials, M15-genealogy | no serial/lot model; a serial is free text on fix.stock.consumption |
| Goods Receipt (inspection gate) | 9 | - | no GRN model; receipt is only qty_received on fix.purchase.order.line |
| Cycle Count | 10 | M15-counts | no count plan / count sheet model |
| Network Availability Search | - | M15-network | search console over on-hand stock; no record to capture |
| Van Reconciliation | - | M15-recon | no daily van reconciliation record |
| Scrap Order | - | M15-quarantine | no quarantine disposition / scrap order model |
| Ageing & Obsolescence Review | - | M15-ageing | no ageing or obsolescence provision model |

## M41 · Warehouse Management

| Capture | Model | Defaults | Sub-modules | Screens |
|---|---|---|---|---|
| Warehouse | `fix.warehouse` | - | 1 | M41-zones |
| Warehouse Zone | `fix.warehouse.zone` | - | 1 | M41-zones |
| Bin | `fix.warehouse.bin` | - | 1 | M41-zones |

Gaps (no backing model yet, nothing invented):

| Gap | Sub-modules | Screens | Missing |
|---|---|---|---|
| Slotting Rule | 2 | M41-slotting | no slotting / pick-face model |
| Dock Appointment | 3 | M41-docks | no dock door or appointment model |
| Scan Receipt & Put-Away Task | 3 | M41-receiving, M41-putaway | no inbound receipt or put-away task model |
| Wave Template | 4 | M41-waves | no wave or wave template model |
| Pick Task | 5 | M41-picking | no pick list / pick task model |
| Packing Station Config | 6 | M41-packing, M41-staging | no packing station, carton or staging model |
| Bin Replenishment Task | 7 | - | no pick-face replenishment model (fix.reorder.rule is supplier reorder, M15) |
| RF Task | 8 | M41-rf, M41-tasks | no RF session or warehouse task model |
| Labour Standard | 9 | - | no time standard or productivity model |
| Floor Count | - | M41-counting | no count plan / count sheet model |

## M16 · Procurement & Sourcing

| Capture | Model | Defaults | Sub-modules | Screens |
|---|---|---|---|---|
| Purchase Requisition | `fix.requisition` | - | 1, 2 | M16-prs |
| Purchase Order | `fix.purchase.order` | - | 5 | M16-pos |
| Vendor Invoice (3-way match) | `fix.vendor.invoice` | - | 9 | M16-match |
| RTV Request | `fix.consignment` | `default_consignment_type=return_to_vendor` | - | M16-rtv |

Gaps (no backing model yet, nothing invented):

| Gap | Sub-modules | Screens | Missing |
|---|---|---|---|
| Consolidation Run | 3 | M16-consol | no cross-branch consolidation model |
| RFQ | 4 | M16-rfqs, M16-compare, M16-award | no RFQ, bid or award model |
| Blanket Order | 6 | M16-blanket | no blanket / call-off agreement model |
| Expedite Action | 7 | M16-expedite | no expediting record |
| GRN | 8 | M16-grn, M16-inspection | no GRN or inspection model; receipt is only qty_received on fix.purchase.order.line |
| Spend Review | 10 | M16-spend, M16-pricehist | analysis only; no price history or spend model |

## M42 · Supplier Relationship

| Capture | Model | Defaults | Sub-modules | Screens |
|---|---|---|---|---|
| Supplier Profile | `fix.party.role` | `default_role_type=vendor` | 1 | M42-suppliers |
| Supplier Scorecard | `fix.supplier.scorecard` | - | 6 | M42-scorecards |
| CAR | `fix.ncr` | `default_source=supplier` | 7 | M42-cars |

Gaps (no backing model yet, nothing invented):

| Gap | Sub-modules | Screens | Missing |
|---|---|---|---|
| Supplier Segment | 2 | M42-segments | no supplier segmentation model |
| Qualification Questionnaire | 3 | M42-qualification, M42-gate, M42-requal | no qualification, activation gate or re-qualification model |
| Supplier Document | 4 | M42-docs | no supplier document validity model (fix.document has retention, not validity) |
| Supplier Contract & Price List | 5 | - | no supplier contract or price list model |
| Review Cycle | - | M42-reviews | no supplier review cycle model |
| Risk Assessment | 8 | M42-risk | no supplier risk model (fix.risk.register is the enterprise register, no supplier link) |
| Compliance Screening | 9 | M42-screening | no sanctions / COI / ABAC screening model |

## M44 · Import & Trade Compliance

| Capture | Model | Defaults | Sub-modules | Screens |
|---|---|---|---|---|
| Import Order | `fix.import.order` | - | 1, 8 | M44-orders, M44-landed |

Gaps (no backing model yet, nothing invented):

| Gap | Sub-modules | Screens | Missing |
|---|---|---|---|
| Proforma Invoice | - | M44-proforma | no proforma invoice model |
| LC Application | 2 | M44-lc | no letter of credit / TT payment model |
| Incoterm & FX Terms | - | M44-incoterms | no incoterm or FX booking fields/model |
| HS Ruling Request | 3 | M44-hs | no HS classification model |
| IRC / LCA Record | 4 | M44-irc, M44-lca | no IRC or LCA eligibility model |
| Shipping Document | 5 | M44-docs | no shipping document or insurance model |
| Bill of Entry | 6 | M44-arrival, M44-boe | no port or Bill of Entry model |
| Duty Computation | 7 | M44-duty | no duty line model; customs duty is one amount on fix.import.order |
| C&F Agent Job | - | M44-cf | no C&F agent model |

## Also fixed

- M04 cross-link "M43 Transit Tracking" is now "M03 Collection & Delivery". M43 is Demand
  Planning; transit custody is M03 logistics.
- Workspace links to the removed screen ids `M15-stock` and `M15-reserved` now point to `M15-onhand`.

## Not in scope (found during the audit)

- The 61 other modules still have no `captures` map, so their capture buttons still open the intake modal.
- `M03-counter` (A02) is linked from Tell-Me but no longer exists in the metadata.
- `cd_gl_ext` uses `account.fiscal.year` but does not depend on OCA `account_fiscal_year`. A fresh
  install of `cd_import_order` (M44) fails unless `account_fiscal_year` is installed first.
