# Legacy Archive Integrity & Restorability Verification (DA-006 / ISO 15489)

## Task R11-M02-T04 Verification Record

- **Execution Timestamp**: 2026-10-22T10:21:50Z
- **Verdict (computed)**: `INCOMPLETE`
- **Archive store mounted**: False — the Z7-S3-ARCHIVE archive store is not mounted on this workstation (pass --archive-root or set R11_ARCHIVE_ROOT)
- **Restore drills executed**: 0 / 8; restorable: 0 (n/a)
- **Measured archive volume**: n/a

---

### 8-Class Archive Register

| Class ID | Class Name | Size | SHA-256 | Present | Checksum | Restore drill | Human read | Retention clock | Status |
|---|---|---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **ARCH-CL-01** | Database Dumps (MySQL & MS SQL) | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |
| **ARCH-CL-02** | Branch Service Order Spreadsheets (excluding retained / purged sources) | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |
| **ARCH-CL-03** | Accounting History & Cash Books | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |
| **ARCH-CL-04** | HR & Historic Payroll Records | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |
| **ARCH-CL-05** | WordPress CMS & Technical Media | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |
| **ARCH-CL-06** | Inventory SKU & Spare Parts Crosswalks | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |
| **ARCH-CL-07** | Contact Histories & Warranty Registrations | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |
| **ARCH-CL-08** | Scanned RMA & Environmental Disposal Evidence | n/a | n/a | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `UNMEASURED` | `INCOMPLETE` |

UNMEASURED, and why:

- archive_present: the Z7-S3-ARCHIVE archive store is not mounted on this workstation (pass --archive-root or set R11_ARCHIVE_ROOT)
- checksum: the Z7-S3-ARCHIVE archive store is not mounted on this workstation (pass --archive-root or set R11_ARCHIVE_ROOT)
- human_sample_read: DCM-25: D3 is reached when a person reads a sample; a person's read cannot be observed by this tool
- machine_restore_drill: the Z7-S3-ARCHIVE archive store is not mounted on this workstation (pass --archive-root or set R11_ARCHIVE_ROOT)
- retention_clock: DCM-18: the retention clock runs from the decommission trigger event; that event is not observable here, so no trigger or disposal date is recorded

Archive integrity and restorability are not established by this record (verdict `INCOMPLETE`).
