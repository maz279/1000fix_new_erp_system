# D-038: Odoo Major-Version Upgrade Slot Execution & Controlled Deferral (P09-M02 / R07-M02)

**Status:** APPROVED  
**Date:** 2026-10-18  
**Deciders:** Architecture Review Board (ARB), Chief Architect (`CA`), Steering Committee  
**Governing Documents:** D-025, D-029, GV-003, AS-05, FF-03, AR-004  
**Cross-References:** [`../p09/oca-v20-migration-matrix.md`](../p09/oca-v20-migration-matrix.md), [`../traceability/evidence/fork-audit-and-oca-v20-matrix.json`](../traceability/evidence/fork-audit-and-oca-v20-matrix.json)

---

## 1. Context & Upstream Reality

`D-025` established the Odoo 19.0 Community baseline with a reserved major-version upgrade slot scheduled for Wave 6 (Month 26). The decision stipulated that at Month 26, engineering would formally evaluate upstream Odoo 20 release maturity and OCA (Odoo Community Association) module readiness before proceeding.

### Upstream Lifecycle & Support Analysis:
- **Odoo 19.0 Community:** Released October 2025. Standard community support extends to ~September 2028 (Month 23 post-launch); extended support horizon to ~September 2029 (Month 35).
- **PostgreSQL 17 (`D-029`):** Released September 2024. Supported upstream until 8 November 2029 (Month ~37). This clears the complete 36-month programme build and launch lifecycle with 11 months of margin. Sequencing PostgreSQL 17 ahead of any Odoo upgrade eliminates database-level upgrade friction.
- **Upstream Odoo 20 Status:** Odoo 20 Community core is released, but introduces substantial internal refactorings in the OWL 3 frontend framework, reporting engine hooks, and async queue mechanics.

---

## 2. Fork Audit & OCA v20 Availability Assessment

In accordance with `R07-M02-T02` (`P09-M02-T02/T03`), automated audits were executed against the codebase:

### Fork Audit (`AS-05`, `FF-03`):
- `FORKS.yaml` is clean with `forks: []` (0 unauthorized forks).
- All 20 OCA subtrees in `addons/vendor/` track pristine upstream release branches with zero dirty patches.
- The repository fully complies with zero-unauthorized-fork rules.

### OCA v20 Migration Matrix:
Across the 20 OCA repositories utilized in the 1000FiX architecture:
- **Migrated (M):** 4 repos (`server-tools`, `dms`, `operating-unit`, `partner-contact`).
- **In Progress (P):** 6 repos (`web`, `field-service`, `account-financial-tools`, `account-financial-reporting`, `reporting-engine`, `rest-framework`).
- **Not Started (N):** 10 repos (`helpdesk`, `hr`, `payroll`, `management-system`, `queue`, `attachment-storage`, `stock-logistics-workflow`, `stock-logistics-barcode`, `commission`, `agreement`).
- **Threshold Required by D-025 §5:** >= 12 of 18/20 repositories migrated.
- **Current Available Count:** 4 (deficit of 8 repositories).

---

## 3. Options Considered

1. **Option A1: Force Immediate Odoo 20 Upgrade in Wave 6**
   - *Rationale:* Stay on the newest Odoo major release immediately.
   - *Failure Mode:* Forcing an upgrade when only 4 of 20 OCA repos are ready requires internal engineering to fork and maintain 16 complex third-party repositories (`AS-05` breach). This introduces severe risk of regressions in statutory VAT reporting (Mushak 6.3), payroll calculations, and field service workflows during the critical pre-go-live phase.

2. **Option A2: Controlled Deferral to Post-Go-Live (RECOMMENDED & ADOPTED)**
   - *Rationale:* Exercise the explicit revisit trigger defined in `D-025 §5`. Pin Odoo 19.0 Community for production cutover; preserve stability and 100% clean fork baseline; schedule the Odoo 20/21 major upgrade to Post-Go-Live Phase 11 / Year 2 when community ecosystem maturity reaches >= 90%.
   - *Outcome:* Zero fork debt, rock-solid stability for statutory launch, full upstream support through September 2028/2029.

---

## 4. Formal Decision

The Architecture Review Board and Chief Architect formally **ADOPT Option A2: Controlled Deferral**.

1. **Baseline Freeze:** The 1000FiX ERP production baseline is locked to **Odoo 19.0 Community** running on **PostgreSQL 17.x**.
2. **Support Coverage:** Odoo 19.0 Community provides full stability, security backports, and bug fixes well past go-live into Q3 2028 (standard) and Q3 2029 (extended).
3. **Rescheduled Upgrade Slot:** The major version upgrade is scheduled for **Post-Go-Live Phase 11 / Year 2 maintenance window**, landing on the stabilized 79-unit production estate.
4. **Silence Is Not Acceptable (`R07-M02-T04`):** This decision and its operational consequences are formally recorded in `GV-003` (Entry `D-038`), `D-025 §6`, and published in the architecture register.

---

## 5. Consequences & Risk Management

### Positive:
- **Zero Fork Technical Debt:** Preserves `FORKS.yaml: []` clean baseline with zero custom vendor patches.
- **Statutory Delivery Confidence:** Uncompromised stability for Bangladesh statutory modules (Mushak 6.3/6.6/9.1 in `cd_tax_engine_bd`, TDS withholding, Labour Act payroll).
- **Resource Focus:** 100% of engineering bandwidth remains focused on circular economy depth (Rental, Trade-in, Data Services) and ML platform go-live instead of upstream plumbing.

### Operational Consequences:
- The post-go-live upgrade will land on a 79-unit production estate (67 domain modules + 12 vendor modules), requiring rigorous automated migration scripts (OpenUpgrade / custom ETL) in Phase 11.
- Bengali font shaping and QWeb report rendering (`TR-07`) must continue to be regression-tested continuously against the committed reference baseline (`bengali-conjunct-reference.png`).
