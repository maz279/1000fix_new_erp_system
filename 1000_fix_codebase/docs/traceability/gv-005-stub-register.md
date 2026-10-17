# GV-005 Cross-Wave Stub Register (Traceability & Expiry Management)

**Standard Reference**: `GV-005` RAID Register · `AR-006` §5 Wave Ordering Dispositions · `IR-002` §0.9  
**Rule**: *"Every STUB is registered in GV-005 with an expiry date. A stub that always returns 'eligible' or leaves unreconciled balances is a control that does not work. Closing them is not optional work that can slip."*

---

## Active Cross-Wave Stub Registry

| Stub ID | From Module | Target Module | Wave Boundary | Mechanism / Behavior | Suspense Account | Opened In | Expiry Milestone | Target Date | Owner | Closure Condition | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `STUB-M15-M19-001` | **M15** (`cd_inventory`) | **M19** (`cd_gl_ext` / General Ledger) | Wave 2 → Wave 3 | Stock valuation posts to `fix.inventory.valuation.suspense` instead of immediate GL line items | `110999` (Inventory Valuation Suspense) | R03-M01-T04 | **R04-M01** (Task R04-M01-T04) | 2026-11-30 | Lead Data Architect / Finance Lead | Suspense balance reconciled to zero against General Ledger cutover journal; verified by automated GL check | **ACTIVE** |
| `STUB-M31-M22-001` | **M31** (`cd_workshop`) | **M22** (`cd_competency` / Learning & Certification) | Wave 2 → Wave 5 | Technician skill & competency check returns "eligible" with audit log until R06-M02 | N/A | R03-M02-T03 | **R06-M02** (Task R06-M02-T05) | 2027-01-31 | Service Operations Lead / HR Competency Lead | M22 competency matrix activated with verified skill ratings for L1/L2/L3 benches | **ACTIVE** |
| `STUB-M31-M23-001` | **M31** (`cd_workshop`) | **M23** (`cd_qms_process` / Quality Management ISO) | Wave 2 → Wave 5 | M01/M31 owns QC checklists internally until formal ISO 9001 NCR takeover | N/A | R03-M02-T03 | **R06-M04** (Task R06-M04-T04) | 2027-02-28 | Quality Assurance Lead / Service Operations Lead | M23 formal QMS process activated with automated Non-Conformance Reporting (NCR) and statistical process control | **ACTIVE** |

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

### `STUB-M31-M22-001`: M31 Workshop Repair Routing to M22 Technician Certification

- **Context**: In Wave 2 (Milestone R03-M02), M31 workshop repair orders enforce repair-level routing across L1 (modular), L2 (component/soldering), and L3 (chip-level/cleanroom). Advanced repair operations require certified technician qualifications. However, M22 Learning & Certification lands in Wave 5 (Phase R06).
- **Architecture Mechanism**:
  1. Method `_check_technician_certification(technician, repair_level)` in `fix.workshop.job` validates technician status and qualifications fallback.
  2. For Wave 2, the check logs `STUB-M31-M22-001` evaluation and returns `True` ("eligible") for active technicians.
  3. All allocations are logged with timestamps and technician badges.
- **Quality Risk**: "A stub that always returns 'eligible' is a control that does not work" (Appendix E). Routing uncertified technicians to L3 chip-level cleanroom benches risks device damage and warranty repeat-faults.
- **De-risking & Audit Trail**:
  - Bench assignment enforces hardware capability and supervisor override logging.
  - Expiry milestone `R06-M02` establishes a hard gate where real competency ratings must be checked.
- **Expiry & Closure**:
  - **Expiry Milestone**: `R06-M02-T05`
  - **Required Action**: Wire `_check_technician_certification` to query `fix.employee.skill` and `fix.certification` records in M22, blocking uncertified technicians on L2/L3 benches without formal manager waiver.

### `STUB-M31-M23-001`: M31 Workshop Quality Control Checklists to M23 ISO 9001 QMS

- **Context**: In Wave 2 (Milestone R03-M02), every repaired device must undergo Quality Control before delivery. In Wave 2, inspection checklists are owned locally within M01/M31 (`fix.qc.checklist` / `fix.workshop.job`), enforcing independent inspector rules (BRU-SRM-18). The enterprise ISO 9001 Quality Management System (M23) lands in Wave 5 (Phase R06).
- **Architecture Mechanism**:
  1. Method `_run_qc_inspection(passed, notes)` in `fix.workshop.job` validates independent inspector identity (BRU-SRM-18: inspector cannot be repairing technician).
  2. Local pass/fail state and rework loops are recorded on `fix.workshop.job`.
  3. Event `workshop.qc.completed` is published.
- **Quality Risk**: Without centralized ISO 9001 Non-Conformance Reports (NCR), recurring component failures and supplier part defect trends are not escalated systematically to vendor warranty claims.
- **De-risking & Audit Trail**:
  - Independent inspector identity is strictly enforced in code.
  - Rework loop counters (`rework_count`, `is_rework`) are tracked on every job.
- **Expiry & Closure**:
  - **Expiry Milestone**: `R06-M04-T04`
  - **Required Action**: Integrate M23 `fix.ncr` creation on `action_fail_qc()`, linking failed workshop inspections directly to ISO 9001 Corrective Action Requests (CAR) and vendor RMA claims.

