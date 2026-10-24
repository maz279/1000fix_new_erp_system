# P09-M02 / R07-M02 — OCA v20 Availability Matrix & Fork Audit

**Authority:** ARB / Lead Architect (`CA`), recorded under `GV-003` (entry `D-038`).  
**Milestone:** R07-M02-T02 (P09-M02-T02 / T03)  
**Date:** 2026-10-18  
**Reference Evidence:** [`../traceability/evidence/fork-audit-and-oca-v20-matrix.json`](../traceability/evidence/fork-audit-and-oca-v20-matrix.json)

---

## 1. Fork Audit Summary (`AS-05`, `FF-03`)

The 1000FiX codebase enforces a strict zero-unauthorized-forks policy (`AS-05`). Vendor additions must be clean upstream tracking branches without unrecorded patches (`FF-03`).

| Parameter | State | Compliant |
|---|---|---|
| `FORKS.yaml` entries | `forks: []` (0 forks) | **YES** |
| `addons/vendor/` subtree inspection | 20 OCA community subtrees | **YES** |
| Dirty / uncommitted vendor modifications | None detected | **YES** |
| Patch status | 100% upstream release tags | **YES** |

---

## 2. OCA v20 Availability Assessment Matrix

Across the 20 OCA repositories utilized in the 1000FiX architecture, migration readiness for Odoo 20 was evaluated against upstream OCA community branches, automated test status, and dependency graphs.

**Status Legend:**
- **M (Migrated):** Official `20.0` branch cut, CI green, core modules usable in production.
- **P (In Progress):** Active PRs or drafts open on upstream OCA repo; partial porting; breaking changes unresolved.
- **N (Not Started):** No `20.0` branch or PR open; migration awaiting upstream core refactoring.
- **A (Abandoned):** Community abandoned or deprecated in v20.
- **R (Reclassify):** Core merged into Odoo 20 standard; community module obsolete.

### Repository Status Breakdown (Month 26 Evaluation)

| # | Repository | Load / Criticality | Tier | v20 Status | Current 19.0 Usage & Notes |
|---|---|---|---|---|---|
| 1 | `server-tools` | Heavy | L2 | **M** | Core base utilities, auditlog, sql_export; basic 20.0 branch operational. |
| 2 | `web` | Heavy | L2 | **P** | `web_responsive` port in progress; OWL 3 UI component adaptations ongoing. |
| 3 | `field-service` | Heavy | L3 | **P** | Core FSM models porting; substatus PR under community review. |
| 4 | `helpdesk` | Heavy | L3 | **N** | No 20.0 branch cut; planning community sprint for late Q4. |
| 5 | `hr` | Medium | L3 | **N** | v20 migration pending upstream HR model renames and structural changes. |
| 6 | `payroll` | Medium | L3 | **N** | Statutory rule engine porting not started; waiting for hr base modules. |
| 7 | `dms` | Medium | L3 | **M** | `dms` 20.0 branch merged with CE storage adapter. |
| 8 | `management-system` | Medium | L3 | **N** | Waiting on upstream quality and ISO audit modules. |
| 9 | `operating-unit` | Medium | L2 | **M** | `operating_unit` 20.0 released with multi-company hooks. |
| 10 | `account-financial-tools` | Medium | L3 | **P** | Fiscal year utilities under active porting; reconciliations in progress. |
| 11 | `account-financial-reporting` | Medium | L3 | **P** | Financial report engine porting to OWL 3; alpha release only. |
| 12 | `partner-contact` | Heavy | L2 | **M** | Partner contact and identification engines migrated to 20.0. |
| 13 | `reporting-engine` | Medium | L2 | **P** | QWeb report helpers; PDF generation adapting to new wkhtmltopdf hooks. |
| 14 | `rest-framework` | Heavy | L2 | **P** | Fast-API and JSON:API bridge undergoing major schema updates for v20. |
| 15 | `queue` | Heavy | L2 | **N** | `queue_job` porting pending async engine changes in Odoo 20 core. |
| 16 | `attachment-storage` | Medium | L2 | **N** | S3 / Ceph attachment storage adapter not yet ported to v20. |
| 17 | `stock-logistics-workflow` | Heavy | L3 | **N** | Complex warehouse reservation hooks awaiting community porting. |
| 18 | `stock-logistics-barcode` | Medium | L3 | **N** | Barcode client adaptations pending UI redesign. |
| 19 | `commission` | Low | L3 | **N** | Sales commission calculations not yet prioritized by community. |
| 20 | `agreement` | Medium | L3 | **N** | SLA and service agreement management pending field-service porting. |

### Summary Statistics
- **Total Repositories Evaluated:** 20
- **Migrated (M):** 4 (20%)
- **In Progress (P):** 6 (30%)
- **Not Started (N):** 10 (50%)
- **Abandoned / Reclassified (A/R):** 0

---

## 3. D-025 §5 Revisit Trigger Analysis

`D-025 §5` sets the strict architectural gate condition:
> *"OCA v20 availability for fewer than 12 of 18 repositories at G5/G6 -> escalate to Steering: extend Odoo 19 extended support (to ~Sept 2029) and re-slot."*

### Metric Evaluation:
- **Available / Migrated Repositories:** 4
- **Threshold Required for Migration:** 12
- **Variance:** -8 repositories below required threshold

### Architectural Impact:
If an upgrade to Odoo 20 were forced at Month 26 (Wave 6):
1. **Fork Explosion (`AS-05` breach):** 16 OCA repositories would require bespoke in-house porting and maintenance, creating 16 long-lived L5 forks.
2. **Maintenance Drag (`FF-03` breach):** The internal engineering team would be forced to maintain community accounting, queue, and field-service plumbing instead of delivering customer value.
3. **Go-Live Risk:** Unstable OWL 3 and async event loop changes in alpha OCA ports would introduce critical regressions into VAT and inventory engines.

---

## 4. Formal Decision: Controlled Deferral (Option A2)

In accordance with `D-025 §5` and recorded under `GV-003` entry `D-038`:
1. **Odoo 19.0 Community Baseline Maintained:** The estate remains pinned to Odoo 19.0 Community edition.
2. **Vendor Support Horizon:** Odoo 19.0 Community enjoys active community maintenance through ~September 2028, and LTS enterprise/extended support through ~September 2029 (Month ~35).
3. **Post-Go-Live Upgrade Slot:** The major version upgrade to Odoo 20 / 21 is formally re-slotted to Post-Go-Live Phase 11 / Year 2, when upstream OCA v20/v21 ecosystem maturity exceeds 90% (>= 18/20 repos).
