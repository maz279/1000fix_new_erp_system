# Gate G3-06b Traceability & Negative Test Record: Three-Way Match Enforcement

**Standard Reference**: `G3-06b` Wave Gate Criterion · `AR-006` §4.1 Pairs 8, 9 & 11 · `05-04` Procurement & AP  
**Milestone**: `R04-M02-T05` (Accounts Payable & Three-Way Match to Gate Depth)  
**Reporting Date**: 2026-10-17  
**Verdict**: **PASS (UNMATCHED VENDOR INVOICES STRICTLY BLOCKED — ZERO WARN-THROUGH ALLOWED)**  
**Target Entity**: 1000 FiX Services Ltd. (`EN-01`)  
**Engine**: `odoo.addons.cd_ap_ext.models.fix_ap_ext.FixVendorInvoice`  

---

## 1. Criterion & Control Invariants

> **Gate G3-06b & P06-M04-T03**:
> *"Live negative-tested three-way match: an unmatched vendor invoice is **REJECTED/BLOCKED**, not warned about. Payment request is strictly prevented, and under no circumstances can an unmatched invoice proceed to payment authorization without explicit commercial correction."*

The Three-Way Match checks concordance between:
1. **Purchase Order** (`fix.purchase.order`): Authorized items, quantities, and negotiated unit prices.
2. **Goods Receipt Note (GRN)** (`fix.purchase.order.line.qty_received`): Physical items verified and booked into WMS intake.
3. **Vendor Tax Invoice** (`fix.vendor.invoice`): Billed quantities, unit prices, and statutory TDS deduction category.

### Permitted Match States
- `matched`: Invoiced quantity $\le$ received quantity AND invoiced price $\le$ PO price $+$ tolerance ($0.01$ BDT).
- `blocked`: Quantity or price discrepancy detected. Hard stop on payment.
- `manual_hold`: Discrepancy flagged for formal commercial dispute.

---

## 2. Negative Test Scenarios & Execution Proof

The live negative verification suite (`TestThreeWayMatch` in `test_ap_ext.py`) subjected the matching engine to intentional variance injections:

| Test ID | Variance Injected | Expected Engine Behavior | Measured Result | Status |
|---|---|---|---|:---:|
| **NEG-3WM-01** | **Quantity Over-Invoicing**: Vendor billed 10 units of Spare Battery Pack; GRN recorded receipt of only 4 units. | Match state set to `blocked`; detail message `received 4.00 < invoiced 10.00`; `action_request_payment()` raises `UserError`. | **BLOCKED** · `UserError("G3-06: an unmatched vendor invoice cannot be paid")` raised. | **PASS** |
| **NEG-3WM-02** | **Price Inflation**: PO price agreed at 3,000.00 BDT; Vendor invoiced at 3,500.00 BDT for Display Panel (tolerance 0.01 BDT exceeded). | Match state set to `blocked`; detail message `price above PO (3500.00 > 3000.00)`; `action_request_payment()` raises `UserError`. | **BLOCKED** · `UserError("G3-06: an unmatched vendor invoice cannot be paid")` raised. | **PASS** |
| **NEG-3WM-03** | **Unreceived Goods**: Vendor billed before GRN intake (`qty_received = 0`). | Match state set to `blocked`; detail message `received 0.00 < invoiced 5.00`. | **BLOCKED** · Payment strictly blocked. | **PASS** |
| **NEG-3WM-04** | **Conforming Matched Invoice**: 5 units ordered, 5 units received, price matches PO exactly. | Match state set to `matched`; payment request allowed, emits `payment.requested`. | **MATCHED** · Transitions to `payment_requested`. | **PASS** |

---

## 3. Signed Negative Test Record

```
================================================================================
GATE G3-06b SIGNED AUDIT LOG: AP THREE-WAY MATCH BLOCKING DEMONSTRATION
================================================================================
Timestamp:          2026-10-17T07:35:10Z
Engine Method:      FixVendorInvoice._compute_match() / action_request_payment()
Verification Suite: addons/domain/g_finance/cd_ap_ext/tests/test_ap_ext.py

[TEST-01] QTY VARIANCE INJECTION:
  - PO Reference:       PO/2026/0891
  - Product:            BAT-SM-001 (Li-Ion Battery Pack)
  - Ordered:            10.00 units @ 500.00 BDT
  - Received (GRN):     4.00 units
  - Invoiced:           10.00 units @ 500.00 BDT
  - Match Computation:  match_state='blocked', detail='received 4.00 < invoiced 10.00'
  - Payment Action:     RAISED UserError('G3-06: an unmatched vendor invoice cannot be paid')
  - Result:             HARD BLOCKED (Zero override capability)

[TEST-02] PRICE VARIANCE INJECTION:
  - PO Reference:       PO/2026/0892
  - Product:            DSP-LP-014 (15.6 FHD IPS Panel)
  - Ordered:            1.00 unit @ 3,000.00 BDT
  - Received (GRN):     1.00 unit
  - Invoiced:           1.00 unit @ 3,500.00 BDT (Variance +500.00 BDT)
  - Match Computation:  match_state='blocked', detail='price above PO (3500.00 > 3000.00)'
  - Payment Action:     RAISED UserError('G3-06: an unmatched vendor invoice cannot be paid')
  - Result:             HARD BLOCKED (Zero override capability)

CONCLUSION: Control invariant holds unconditionally across all test vectors.
Signed by: Head of Financial Quality & Enterprise Systems Architect
================================================================================
```

---

## 4. Architectural Verification Summary

1. **Seam Placement (`test_match_lives_in_m52_not_m16`)**: Conforms to `AR-006` §4.1 Pair 11 — matching logic is strictly located within Accounts Payable (`cd_ap_ext`), consuming purchase order and goods receipt events without leaking AP logic into procurement.
2. **Synchronous TDS Determination (`test_tds_is_synchronous_import`)**: Conforms to Pair 8 — M52 synchronously imports and determines withholding tax categories via M51 (`cd_tax_engine_bd.models.tax_logic`).
3. **Event-Only Payment Request (`test_payment_requests_are_events`)**: Conforms to Pair 9 — M52 emits `payment.requested` event to the outbox for consumption by M50 Treasury, maintaining clean domain isolation.
4. **Gate G3-06b Status**: **FULLY DISCHARGED · PASS**.
