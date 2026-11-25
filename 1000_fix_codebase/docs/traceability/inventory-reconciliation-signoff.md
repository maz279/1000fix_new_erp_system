# Inventory Physical Count Reconciliation Record (G2-04)

**Standard Reference**: `G2-04` Wave Gate Criterion · `MIG-02` Control Totals · `MIG-03` Legacy References · `GV-009` Measured Evidence  
**Milestone**: `R03-M01-T06` (Spare Parts & Inventory, ETL-5)  
**Generated At**: 2026-10-22T10:11:26.995703+00:00 by `migrations/load_inventory.py`  
**Target Database**: `127.0.0.1:5433/fix_migration`  
**Data Classification**: SYNTHETIC  
**Data Sources**:
- `SRC-37`: SKU catalog extract - 150 parts
- `SRC-38`: physical count extract - 10 locations, 950 count lines (audited 2026-10-16T18:00:00Z)

Every number below is read back from the target database after the load (by legacy reference) and compared with the physical count in the SRC-38 extract. Accuracy = 1 - sum(|loaded - counted|) / sum(counted) over every count line; a rejected line counts in full as variance.

---

## 1. Measured Reconciliation Summary

| Metric | Target | Measured | Result |
|---|---|---|---|
| Inventory count accuracy | >= 95.0% | 99.51% | MET |
| SKUs in database (`LEG:SRC37:*`) | 150 | 150 | 0 rejected |
| Stock locations in database (`LEG:SRC38:<loc>`) | 10 | 10 | 0 rejected |
| Count lines in database | 950 | 950 | 0 rejected |
| Physical units counted (extract) | - | 4,115 | - |
| System units loaded (database) | - | 4,095 | - |
| Absolute unit variance | - | 20 | - |
| Duplicate suspense rows per legacy reference | 0 | 0 | - |
| Parts whose qty_available != loaded units | 0 | 0 | - |
| Initial stock valuation (database) | - | BDT 12,605,500.00 | suspense 110999 / STUB-M15-M19-001 |

**Measured G2-04 status: PASS**

- measured accuracy 99.51% >= 95.0%; no rejections

This record is generated evidence, not an approval: gate G2-04 stays open until every role in section 4 has completed its sign-off.

---

## 2. Location Breakdown

| Branch / Hub | Location Code | Type | Counted Qty | Loaded Qty (DB) | Net Variance | Accuracy |
|---|---|---|---|---|---|---|
| Dhaka Central HQ & Service Hub | `CENTRAL-WH` | central | 744 | 744 | 0 | 100.00% |
| Dhanmondi Service Centre | `DHAN-HUB` | branch | 744 | 739 | 5 | 99.33% |
| Uttara Service Centre | `UTT-HUB` | branch | 744 | 739 | 5 | 99.33% |
| Mirpur Service Centre | `MIR-HUB` | branch | 744 | 739 | 5 | 99.33% |
| Chattogram Agrabad Service Centre | `CTG-HUB` | branch | 744 | 739 | 5 | 99.33% |
| Dhanmondi Service Centre | `VAN-DHAN-01` | van | 79 | 79 | 0 | 100.00% |
| Uttara Service Centre | `VAN-UTT-01` | van | 79 | 79 | 0 | 100.00% |
| Mirpur Service Centre | `VAN-MIR-01` | van | 79 | 79 | 0 | 100.00% |
| Chattogram Agrabad Service Centre | `VAN-CTG-01` | van | 79 | 79 | 0 | 100.00% |
| Dhaka Central HQ & Service Hub | `VAN-HQ-01` | van | 79 | 79 | 0 | 100.00% |
| **Totals** | - | - | **4,115** | **4,095** | **20** | **99.51%** |

| Location Code | Lines (extract) | Lines (DB) | Lines matching count | Abs Variance | Van Plate (DB) |
|---|---|---|---|---|---|
| `CENTRAL-WH` | 150 | 150 | 150 | 0 | - |
| `DHAN-HUB` | 150 | 150 | 145 | 5 | - |
| `UTT-HUB` | 150 | 150 | 145 | 5 | - |
| `MIR-HUB` | 150 | 150 | 145 | 5 | - |
| `CTG-HUB` | 150 | 150 | 145 | 5 | - |
| `VAN-DHAN-01` | 40 | 40 | 40 | 0 | DHAKA METRO-GA-11-2041 |
| `VAN-UTT-01` | 40 | 40 | 40 | 0 | DHAKA METRO-GA-11-2042 |
| `VAN-MIR-01` | 40 | 40 | 40 | 0 | DHAKA METRO-GA-11-2043 |
| `VAN-CTG-01` | 40 | 40 | 40 | 0 | CHATTO METRO-NA-11-0457 |
| `VAN-HQ-01` | 40 | 40 | 40 | 0 | - |

---

## 3. Rejected Extract Rows

None - every extract row was loaded.

---

## 4. Sign-off

No sign-off has been recorded. Each role must review the measured figures above:

- Sign-off: PENDING - Stock Controller (Head of Supply Chain)
- Sign-off: PENDING - Lead Inventory Auditor (physical blind count)
- Sign-off: PENDING - System Architect (G2-04 gate owner)
