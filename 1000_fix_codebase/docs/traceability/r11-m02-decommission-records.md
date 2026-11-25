# Legacy Decommission Register (RL-006 / P12-M02)

## Task R11-M02-T03 Verification Record

- **Execution Timestamp**: 2026-10-22T10:21:50Z — MEASURE_ONLY (no legacy system is touched by this tool)
- **Verdict (computed)**: `FAIL`
- **Sources in register**: 48 (declared R=32, K=4, P=1, N=11)
- **Verified outcomes**: D7 retired 0, retained 0, purged 0, transitioned 0; UNMEASURED 48, blocked 0
- **Annual run cost**: BDT 0.00M / year released (of BDT 1.26M declared)
- **Negative connection tests passed**: 0 (32 UNMEASURED)
- **DPO countersigns observed**: 0 / 27

### Estate checks

| Check | Status | Detail |
|---|:---:|---|
| `register_complete` | `PASS` | 48 distinct sources, each with a valid disposition |
| `register_agrees_with_t01` | `FAIL` | 12 source(s) disagree with the T01 register: SRC-22: 'Jessore MK Road (Telematics Tracking Provider)' vs T01 'Jessore MK Road Point'; SRC-38: 'Warehouse Physical Count Practices (Knowledge)' vs T01 'Branch Spare Parts Stock Count'; SRC-39: 'National Standard Hardware SKU Directory' vs T01 'Supplier Part Number Crosswalk'; SRC-40: 'DoE E-Waste Compliance Knowledge' vs T01 'Damaged / Scrapped Parts Log'; SRC-41: 'Corporate Client Account Knowledge' vs T01 'Corporate Client Contact List'; SRC-42: 'SMS Gateway Provider API Credentials & Secrets' vs T01 'Retail SMS Gateway Delivery Log'; SRC-43: 'Legacy Application Database Credentials & Root Keys' vs T01 'Warranty Card Registration Store'; SRC-44: 'BTRC & Consumer Rights Regulatory Feed' vs T01 'Customer Inbound Feedback Log'; SRC-45: 'Global Brand RMA Standards & Warranty Directory' vs T01 'Brand RMA Authorisation Forms'; SRC-46: 'Lab Machine Calibration Profiles & Firmware Hashes' vs T01 'Workshop Machine Calibration Logs'; SRC-47: 'NBR National Depreciation & Asset Tax Table' vs T01 'Branch Fixed Assets Register'; SRC-48: 'Legacy Scheduled Cron Tasks & Service Keys' vs T01 'Environmental Disposal Certificates' |
| `codebase_legacy_endpoint_references` | `PASS` | no reference to ['123.0.26.238', 'station.1000fix.com'] in 1312 files |
| `shadow_system_scan` | `UNMEASURED` | the estate shadow-system scan runs against branch endpoints and the network, which this workstation cannot reach (DE-11) |

---

### 48-Source Decommission Register

| ID | Source Name | Class | Disp | Wave | Target | State | Status |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **SRC-01** | station.1000fix.com | DB | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-02** | 123.0.26.238/orderTracking | DB | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-03** | Tejgaon Central Hub Orders | SS | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-04** | Dhanmondi Service Center | SS | `R` | W3 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-05** | Mirpur-10 Service Center | SS | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-06** | Uttara Sector-3 Center | SS | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-07** | Motijheel Commercial Branch | SS | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-08** | Banani Luxury Care Point | SS | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-09** | Chittagong Agrabad Center | SS | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-10** | Chittagong GEC Circle Center | SS | `R` | W4 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-11** | Sylhet Zindabazar Branch | SS | `R` | W3 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-12** | Rajshahi Alokar More Branch | SS | `R` | W3 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-13** | Khulna KDA Avenue Branch | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-14** | Barisal Sadar Road Branch | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-15** | Rangpur Station Road Branch | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-16** | Bogra Satmatha Branch | SS | `R` | W3 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-17** | Comilla Kandirpar Branch | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-18** | Mymensingh Town Hall Branch | SS | `R` | W3 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-19** | Gazipur Chowrasta Point | SS | `R` | W4 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-20** | Narayanganj Chasara Point (bKash/Nagad Integration) | PORTAL | `K` | n/a | RETAINED | `UNMEASURED` | `INCOMPLETE` |
| **SRC-21** | Savar Bus Stand Center (City Bank BEFTN Portal) | PORTAL | `K` | n/a | RETAINED | `UNMEASURED` | `INCOMPLETE` |
| **SRC-22** | Jessore MK Road (Telematics Tracking Provider) | PORTAL | `K` | n/a | RETAINED | `UNMEASURED` | `INCOMPLETE` |
| **SRC-23** | Kushtia NS Road Point (Historical Recruitment DB) | PORTAL | `P` | W3 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-24** | Dinajpur Ganeshtola Point | SS | `R` | W4 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-25** | Feni Trunk Road Point | SS | `R` | W3 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-26** | Cox's Bazar Main Road Point | SS | `R` | W6 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-27** | Tally ERP 9 Company File A | DB | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-28** | Tally ERP 9 Company File B | DB | `R` | W2 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-29** | Branch Cash Book Spreadsheets | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-30** | Corporate Invoicing Register | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-31** | Staff Master Register (Physical Contract Originals) | PAPER | `K` | n/a | RETAINED | `UNMEASURED` | `INCOMPLETE` |
| **SRC-32** | Monthly Payroll Sheets 2025-26 | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-33** | Technician Commission Logs | SS | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-34** | Statutory Tax Deduction Sheets | SS | `R` | W7 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-35** | WordPress Portal Database | DB | `R` | W5 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-36** | Media Uploads Repository | MAIL | `R` | W6 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-37** | Central Warehouse SKU Catalog | SS | `R` | W6 | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-38** | Warehouse Physical Count Practices (Knowledge) | PEOPLE | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-39** | National Standard Hardware SKU Directory | PUB | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-40** | DoE E-Waste Compliance Knowledge | PEOPLE | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-41** | Corporate Client Account Knowledge | PEOPLE | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-42** | SMS Gateway Provider API Credentials & Secrets | CFG | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-43** | Legacy Application Database Credentials & Root Keys | CFG | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-44** | BTRC & Consumer Rights Regulatory Feed | PUB | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-45** | Global Brand RMA Standards & Warranty Directory | PUB | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-46** | Lab Machine Calibration Profiles & Firmware Hashes | CFG | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-47** | NBR National Depreciation & Asset Tax Table | PUB | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |
| **SRC-48** | Legacy Scheduled Cron Tasks & Service Keys | CFG | `N` | n/a | D7 | `UNMEASURED` | `INCOMPLETE` |

Per-source checks not passed, and why:

- archive_restorable: T04 archive ARCH-CL-01: 'INCOMPLETE' (not measured)
- archive_restorable: T04 archive ARCH-CL-02: 'INCOMPLETE' (not measured)
- archive_restorable: T04 archive ARCH-CL-03: 'INCOMPLETE' (not measured)
- archive_restorable: T04 archive ARCH-CL-04: 'INCOMPLETE' (not measured)
- archive_restorable: T04 archive ARCH-CL-05: 'INCOMPLETE' (not measured)
- archive_restorable: T04 archive ARCH-CL-06: 'INCOMPLETE' (not measured)
- dpo_countersign: a DPO countersign is a human act; no countersign is observable by this tool
- mig08_reconciliation_signoff: T01 MG-004 sign-off: 'UNMEASURED' - the MG-004 business sign-off is a human act by the required signatory; no signed sign-off is observable by this tool
- negative_connection_test: a negative connection test must reach the legacy host, which this workstation may not do (DE-11: the local environment never reaches non-local endpoints)
- purge_verification: purge / media-destruction verification happens on the legacy estate and its certificate is not observable by this tool
- retention_review: the annual retention review is a contractual / human act; no review record is observable by this tool
- transition_evidence: capture into an SOP, conversion to a reference feed or credential rotation in Vault is not observable from this workstation

No legacy source is certified decommissioned by this record (verdict `FAIL`).
