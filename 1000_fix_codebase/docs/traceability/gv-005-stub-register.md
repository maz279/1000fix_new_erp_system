# GV-005 Cross-Wave Stub Register (Traceability & Expiry Management)

**Standard Reference**: `GV-005` RAID Register · `AR-006` §5 Wave Ordering Dispositions · `IR-002` §0.9  
**Rule**: *"Every STUB is registered in GV-005 with an expiry date. A stub that always returns 'eligible' or leaves unreconciled balances is a control that does not work. Closing them is not optional work that can slip."*

---

## Active Cross-Wave Stub Registry

| Stub ID | From Module | Target Module | Wave Boundary | Mechanism / Behavior | Suspense Account | Opened In | Expiry Milestone | Target Date | Owner | Closure Condition | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `STUB-M15-M19-001` | **M15** (`cd_inventory`) | **M19** (`cd_gl_ext` / General Ledger) | Wave 2 → Wave 3 | Stock valuation posts to `fix.inventory.valuation.suspense` instead of immediate GL line items | `110999` (Inventory Valuation Suspense) | R03-M01-T04 | **R04-M01** (Task R04-M01-T04) | 2026-11-30 | Lead Data Architect / Finance Lead | Suspense balance reconciled to zero against General Ledger cutover journal; verified by automated GL check | **ACTIVE** |

---

## Detailed Stub Records

### `STUB-M15-M19-001`: M15 Spare Parts Inventory Valuation Suspense

- **Context**: In Wave 2 (Milestone R03-M01), M15 introduces spare parts master, multi-location stocking (including technician mobile vans), and barcode/QR scan-to-consume operations. However, General Ledger and Chart of Accounts deep integration (M19) is scheduled for Wave 3 (Milestone R04-M01).
- **Architecture Mechanism**:
  1. Every consumption action in `fix.stock.consumption` creates an entry in `fix.inventory.valuation.suspense` recording `quantity * unit_cost`.
  2. Every returned part creates an offsetting entry reversing the valuation.
  3. Every physical count migration load creates initial count valuation baseline records.
  4. All records carry `suspense_account_code = '110999'` and `status = 'pending_gl_cutover'`.
- **Finance Risk**: Unreconciled suspense balances across wave boundaries represent inventory valuation exposure.
- **De-risking & Audit Trail**:
  - The model `fix.inventory.valuation.suspense` tracks each transaction with immutable audit timestamps.
  - Method `action_reconcile_to_gl(gl_voucher_ref)` is prepared to transition status to `'reconciled'` upon M19 activation.
- **Expiry & Closure**:
  - **Expiry Milestone**: `R04-M01-T04`
  - **Required Action**: Sweep all `pending_gl_cutover` records, verify sum balances, post consolidated opening journal voucher in M19 GL, and close stub in this register.
