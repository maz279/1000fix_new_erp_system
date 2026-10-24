# Legacy 48-Source Business Reconciliation Register (MIG-08 / MG-004)

## Task R11-M02-T01 Verification & Audit Record

- **Execution Timestamp**: 2026-10-22T10:21:49Z
- **Verdict (computed)**: `INCOMPLETE`
- **Sources in register**: 48
- **Sources reconciled (measured)**: 0 / 48
- **Sources with an observed MG-004 sign-off**: 0 / 48
- **Sources UNMEASURED**: 48
- **Binding Standard**: `MIG-08` (*Legacy systems decommissioned only after reconciliation sign-off*)

Measurement policy (GV-009): a legacy source's counts and its business sign-off are not observable from a workstation (DE-11 / DE-12); each is reported `UNMEASURED` with its reason, never as reconciled or approved.

---

### Rehearsal reconciliation (measured, synthetic extracts)

- **Run**: `WAVE1_REHEARSAL_20261016` — status `INCOMPLETE`
- **Target database**: 127.0.0.1:5433/fix_migration
- **Unaccounted variance**: 0.00%

| Entity | Control | Extract | Accepted | Quarantined | Live (target) | Delta | Status |
|---|---:|---:|---:|---:|---:|---:|:---:|
| `attendance_opening` | 20 | 20 | 0 | 20 | 0 | 0 | `INCOMPLETE` |
| `branches` | 6 | 6 | 6 | 0 | 6 | 0 | `PASS` |
| `customers` | 50 | 50 | 49 | 1 | 49 | 0 | `INCOMPLETE` |
| `devices` | 50 | 50 | 49 | 1 | 49 | 0 | `INCOMPLETE` |
| `employees` | 20 | 20 | 20 | 0 | 20 | 0 | `PASS` |

Checks not passed:

- `attendance_opening.quarantine_signoff` — UNMEASURED: quarantined records await a data steward's disposition; that sign-off is a human act this tool cannot observe
- `customers.quarantine_signoff` — UNMEASURED: quarantined records await a data steward's disposition; that sign-off is a human act this tool cannot observe
- `devices.quarantine_signoff` — UNMEASURED: quarantined records await a data steward's disposition; that sign-off is a human act this tool cannot observe

---

### 48-Source Reconciliation Register

| Source ID | Class | Source Name | Target | Reconciliation | Sign-off | Required signatory |
|---|---|---|---|:---:|:---:|---|
| **SRC-01** | 1. Live Tracker | station.1000fix.com | M01, P01 | `UNMEASURED` | `UNMEASURED` | Mohammad Ali (Data Steward) & Shafiul Alam (CTO) |
| **SRC-02** | 1. Live Tracker | 123.0.26.238/orderTracking | M01, P01 | `UNMEASURED` | `UNMEASURED` | Mohammad Ali (Data Steward) & Shafiul Alam (CTO) |
| **SRC-03** | 2. Branch Sheet | Tejgaon Central Hub Orders | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Tariqul Islam (Central Hub Manager) |
| **SRC-04** | 2. Branch Sheet | Dhanmondi Service Center | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Tanvir Ahmed (Dhanmondi Branch Lead) |
| **SRC-05** | 2. Branch Sheet | Mirpur-10 Service Center | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Kamrul Hassan (Mirpur Branch Lead) |
| **SRC-06** | 2. Branch Sheet | Uttara Sector-3 Center | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Mahmudur Rahman (Uttara Branch Lead) |
| **SRC-07** | 2. Branch Sheet | Motijheel Commercial Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Farhana Yasmin (Motijheel Branch Lead) |
| **SRC-08** | 2. Branch Sheet | Banani Luxury Care Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Zahid Hossain (Banani Branch Lead) |
| **SRC-09** | 2. Branch Sheet | Chittagong Agrabad Center | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Nasir Uddin (Chittagong Regional Lead) |
| **SRC-10** | 2. Branch Sheet | Chittagong GEC Circle Center | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Anisur Rahman (GEC Branch Lead) |
| **SRC-11** | 2. Branch Sheet | Sylhet Zindabazar Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Jashim Uddin (Sylhet Branch Lead) |
| **SRC-12** | 2. Branch Sheet | Rajshahi Alokar More Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Sabbir Hossain (Rajshahi Branch Lead) |
| **SRC-13** | 2. Branch Sheet | Khulna KDA Avenue Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Abdur Razzak (Khulna Branch Lead) |
| **SRC-14** | 2. Branch Sheet | Barisal Sadar Road Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Shahadat Hossain (Barisal Branch Lead) |
| **SRC-15** | 2. Branch Sheet | Rangpur Station Road Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Mostafa Kamal (Rangpur Branch Lead) |
| **SRC-16** | 2. Branch Sheet | Bogra Satmatha Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Ashraful Islam (Bogra Branch Lead) |
| **SRC-17** | 2. Branch Sheet | Comilla Kandirpar Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Enamul Haque (Comilla Branch Lead) |
| **SRC-18** | 2. Branch Sheet | Mymensingh Town Hall Branch | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Saiful Islam (Mymensingh Branch Lead) |
| **SRC-19** | 2. Branch Sheet | Gazipur Chowrasta Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Abdul Mannan (Gazipur Point Lead) |
| **SRC-20** | 2. Branch Sheet | Narayanganj Chasara Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Monirul Islam (Narayanganj Point Lead) |
| **SRC-21** | 2. Branch Sheet | Savar Bus Stand Center | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Delwar Hossain (Savar Point Lead) |
| **SRC-22** | 2. Branch Sheet | Jessore MK Road Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Habibur Rahman (Jessore Point Lead) |
| **SRC-23** | 2. Branch Sheet | Kushtia NS Road Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Sharif Ahmed (Kushtia Point Lead) |
| **SRC-24** | 2. Branch Sheet | Dinajpur Ganeshtola Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Nazrul Islam (Dinajpur Point Lead) |
| **SRC-25** | 2. Branch Sheet | Feni Trunk Road Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Mizanur Rahman (Feni Point Lead) |
| **SRC-26** | 2. Branch Sheet | Cox's Bazar Main Road Point | M01 Kernel | `UNMEASURED` | `UNMEASURED` | Shah Alam (Cox's Bazar Point Lead) |
| **SRC-27** | 3. Accounting | Tally ERP 9 Company File A | M19, M55 | `UNMEASURED` | `UNMEASURED` | Mustafizur Rahman (Financial Controller) |
| **SRC-28** | 3. Accounting | Tally ERP 9 Company File B | M19, M55 | `UNMEASURED` | `UNMEASURED` | Mustafizur Rahman (Financial Controller) |
| **SRC-29** | 3. Accounting | Branch Cash Book Spreadsheets | M59, M60 | `UNMEASURED` | `UNMEASURED` | Mohammad Harun (Chief Treasury Officer) |
| **SRC-30** | 3. Accounting | Corporate Invoicing Register | M19, M36 | `UNMEASURED` | `UNMEASURED` | Arifur Rahman (Corporate Billing Lead) |
| **SRC-31** | 4. HR & Payroll | Staff Master Register | M21 Core | `UNMEASURED` | `UNMEASURED` | Nasreen Sultana (Head of HR) |
| **SRC-32** | 4. HR & Payroll | Monthly Payroll Sheets 2025-26 | M22 Payroll | `UNMEASURED` | `UNMEASURED` | Kazi Touhid (Payroll Lead) |
| **SRC-33** | 4. HR & Payroll | Technician Commission Logs | M22 Payroll | `UNMEASURED` | `UNMEASURED` | Kazi Touhid (Payroll Lead) |
| **SRC-34** | 4. HR & Payroll | Statutory Tax Deduction Sheets | M51 Tax | `UNMEASURED` | `UNMEASURED` | Rezaul Karim (Tax Compliance Lead) |
| **SRC-35** | 5. WordPress CMS | WordPress Portal Database | Portal CMS | `UNMEASURED` | `UNMEASURED` | Shumona Akter (Marketing Head) |
| **SRC-36** | 5. WordPress CMS | Media Uploads Repository | Ceph Store | `UNMEASURED` | `UNMEASURED` | Tanvir Mahmud (Media Custodian) |
| **SRC-37** | 6. Inventory | Central Warehouse SKU Catalog | M15, M37 | `UNMEASURED` | `UNMEASURED` | Mahbub Alam (Warehouse Manager) |
| **SRC-38** | 6. Inventory | Branch Spare Parts Stock Count | M15 Inventory | `UNMEASURED` | `UNMEASURED` | Mahbub Alam (Warehouse Manager) |
| **SRC-39** | 6. Inventory | Supplier Part Number Crosswalk | M39 Vendor | `UNMEASURED` | `UNMEASURED` | Selim Reza (Head of Procurement) |
| **SRC-40** | 6. Inventory | Damaged / Scrapped Parts Log | M50 E-Waste | `UNMEASURED` | `UNMEASURED` | Tareq Hasan (E-Waste Compliance Lead) |
| **SRC-41** | 7. Contacts | Corporate Client Contact List | M09, M33 | `UNMEASURED` | `UNMEASURED` | Fahim Chowdhury (B2B Accounts Director) |
| **SRC-42** | 7. Contacts | Retail SMS Gateway Delivery Log | M26, M33 | `UNMEASURED` | `UNMEASURED` | Farzana Haque (Customer Service Head) |
| **SRC-43** | 7. Contacts | Warranty Card Registration Store | M05, M17 | `UNMEASURED` | `UNMEASURED` | Imtiaz Ahmed (Warranty Operations Lead) |
| **SRC-44** | 7. Contacts | Customer Inbound Feedback Log | M34 CSAT | `UNMEASURED` | `UNMEASURED` | Zubair Hossain (QA Manager) |
| **SRC-45** | 8. Misc Records | Brand RMA Authorisation Forms | M05 Warranty | `UNMEASURED` | `UNMEASURED` | Kamrul Islam (Brand Relations Lead) |
| **SRC-46** | 8. Misc Records | Workshop Machine Calibration Logs | M62 Tools | `UNMEASURED` | `UNMEASURED` | Shahin Alam (Technical Services Supervisor) |
| **SRC-47** | 8. Misc Records | Branch Fixed Assets Register | M56 Assets | `UNMEASURED` | `UNMEASURED` | Jamil Ahmed (Fixed Assets Accountant) |
| **SRC-48** | 8. Misc Records | Environmental Disposal Certificates | M50 E-Waste | `UNMEASURED` | `UNMEASURED` | Tareq Hasan (E-Waste Compliance Lead) |

UNMEASURED reconciliation: the legacy source system and its production extract are not reachable from this workstation (DE-11 local-only endpoints; DE-12 no production data on a workstation) and no committed extract + control-totals manifest belongs to this source, so its legacy vs migrated counts cannot be measured here.

UNMEASURED sign-off: the MG-004 business sign-off is a human act by the required signatory; no signed sign-off is observable by this tool.

No source is approved for decommission by this record (verdict `INCOMPLETE`).
