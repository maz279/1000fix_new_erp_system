# CR-R10M02-04 — Module Register Change Request: M42 Delivery by Coverage & Pair 10 Interface

| Attribute | Value |
|---|---|
| **CR ID** | `CR-R10M02-04` |
| **Date** | 2026-10-21 |
| **Milestone** | R10-M02 (Task R10-M02-T04) |
| **Target Module** | `M42` — Supplier Relationship & Performance (Category E) |
| **Raised Against** | `1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` §3 |
| **Authority** | Change Board / Enterprise System Architecture (`RR-10` / `DoD-01` / `Appendix E Pair 10`) |
| **Status** | **APPROVED & RATIFIED** |

---

## 1. Context & Business Rationale

The baseline module catalogue (`02-02` §3) initially listed M42 as an unwritten prospect, estimated at 26 requirements. In Phase 6 and Phase 7 (`P06-M07-T07`, `P07-M06-T06`, `AR-006` §4.1 pair 10), the critical architectural cycle between **M16 (Procurement)** and **M42 (Supplier Performance)** was analyzed and broken:

> **The Appendix E Pair 10 Asymmetric Break**:
> If M16 and M42 directly depend on each other's ORM tables, a bidirectional architectural cycle is created, violating architectural fitness rules.
> Instead, **M42 is designed as a pure read-and-score consumer of M16 domain events** (`goods.received`, `invoice.blocked`). It never executes SQL or ORM queries against M16 purchase order tables. M16, in turn, reads supplier scores exclusively through published scorecard records and APIs.

The implementation was delivered across:
1. **Event-Driven Scoring Engine (`cd_cx_feedback`)**: `addons/domain/b_customer_engagement/cd_cx_feedback` implements `fix.supplier.scorecard`, consuming `goods.received` line items, weighting on-time delivery (0.6) and quality (0.4), and maintaining period uniqueness per vendor.
2. **Vendor Portal (P05) (`cd_vendor_portal`)**: `addons/domain/e_supply_chain/cd_vendor_portal` provides the self-service supplier portal where qualification documents, onboarding workflows, and published performance scorecards are accessed.
3. **Automated Cycle Break Verification (`tests/test_m16_m42_break.py` & `test_cx_feedback.py`)**: Continuously verifies zero direct coupling to `fix.purchase.order` tables.

---

## 2. Requirement Traceability Mapping (34/34 Requirements)

All 34 requirements defined in `M42_Supplier_Relationship_and_Performance.md` (`FR-SRM2-001` through `FR-SRM2-034`) are mapped to the delivered units:

| Req ID | Requirement Name | Layer | Delivered Unit | Verification / Test Reference |
|---|---|:--:|---|---|
| `FR-SRM2-001` | Supplier profile | L1 | `cd_party_master` / `res.partner` vendor profiles | `cd_party_master` models |
| `FR-SRM2-002` | Supplier classification | L1 | Vendor classification (OEM, authorized, local) | `cd_party_master` category tags |
| `FR-SRM2-003` | Segmentation | L5 | Strategic, preferred, transactional segments | `cd_vendor_portal` vendor tiering |
| `FR-SRM2-004` | Risk tiering | L5 | Risk-weighted review frequency rules | `cd_vendor_portal` risk models |
| `FR-SRM2-005` | Category coverage | L1 | Product category vendor qualification lines | `cd_inventory` category mapping |
| `FR-SRM2-006` | Supplier 360 | L5 | Consolidated supplier view on P05 / Odoo | `cd_vendor_portal_views.xml` |
| `FR-SRM2-007` | Self-service registration | L5 | P05 Portal vendor onboarding wizard | `addons/domain/e_supply_chain/cd_vendor_portal` |
| `FR-SRM2-008` | Qualification questionnaire | L5 | Dynamic qualification questionnaire engine | `cd_vendor_portal` forms |
| `FR-SRM2-009` | Qualification workflow | L5 | Multi-stage review and approval pipeline | `cd_vendor_portal` approval states |
| `FR-SRM2-010` | Activation gate | L5 | Authoritative vendor activation status | Gate check in purchase requisition |
| `FR-SRM2-011` | Qualification validity and expiry | L5 | Qualification date tracking with renewal warnings | Automated cron alert |
| `FR-SRM2-012` | Re-qualification | L5 | Triggered re-qualification workflows | `cd_vendor_portal` workflows |
| `FR-SRM2-013` | Conditional and provisional approval | L5 | Time-boxed provisional status with spend limits | Vendor status validation rules |
| `FR-SRM2-014` | De-activation and blocking | L5 | Instant vendor blocking with open PO freeze | PO validation rules |
| `FR-SRM2-015` | Authorisation evidence | L5 | OEM brand authorization letter validation | `cd_document_core` attachments |
| `FR-SRM2-016` | Document register | L5 | Trade license, 13-digit BIN, 12-digit TIN vault | `cd_document_core` / `cd_entity_config` |
| `FR-SRM2-017` | Expiry monitoring | L5 | 30-day and 15-day document expiry notifications | Automated notification cron |
| `FR-SRM2-018` | Bank detail change control | L5 | Dual-authorization workflow for payout accounts | `libs/py/payout_rail` BEFTN checks |
| `FR-SRM2-019` | Integrity screening | L5 | Anti-corruption & conflict of interest screening | Vendor onboarding questionnaire |
| `FR-SRM2-020` | Supplier code of conduct | L5 | Mandatory digital signature of code of conduct | `cd_vendor_portal` terms agreement |
| `FR-SRM2-021` | Framework agreement | L2/L5 | Long-term master service agreements | Odoo `contract` / `cd_vendor_portal` |
| `FR-SRM2-022` | Agreed price list | L1 | Vendor price lists with effective dating | Odoo `product.supplierinfo` |
| `FR-SRM2-023` | Price change governance | L5 | Price change request and margin impact workflow | `services/pricing-engine` |
| `FR-SRM2-024` | Consignment agreement | L5 | Consignment stock terms per brand | `cd_inventory` consignment locations |
| `FR-SRM2-025` | Rebate and volume commitment | L5 | Periodic volume commitment tracking | ClickHouse `fact_invoices` aggregation |
| `FR-SRM2-026` | Agreement expiry and renewal | L5 | Contract renewal pipeline | `cd_vendor_portal` contract alerts |
| `FR-SRM2-027` | Performance scorecard | L5 | Periodic scorecard from M16 `goods.received` | `cd_cx_feedback/models/fix_cx_feedback.py` |
| `FR-SRM2-028` | Weighted scoring model | L5 | Formula: $0.6 \times \text{on\_time} + 0.4 \times \text{quality}$ | `TestSupplierScorecard::test_score_weights` |
| `FR-SRM2-029` | Supplier-facing scorecard | L5 | Scorecard publication on P05 Portal | `cd_cx_feedback` portal publication |
| `FR-SRM2-030` | Performance review cycle | L5 | Quarterly and annual scorecard aggregations | `fix.supplier.scorecard` period model |
| `FR-SRM2-031` | Corrective action request | L5 | Supplier CAR ticket generation | `cd_cx_feedback` complaint / CAPA |
| `FR-SRM2-032` | Supplier development plan | L5 | Strategic vendor improvement plans | `cd_vendor_portal` plans |
| `FR-SRM2-033` | Risk assessment and concentration | L4/L5 | Single-source risk & spend concentration analytics | ClickHouse `dim_branch` / spend queries |
| `FR-SRM2-034` | Category strategy & base analytics | L4/L5 | Category spend analytics & supplier count ratios | Apache Superset procurement dashboard |

---

## 3. Register Ruling & Conclusion

The requirement traceability for M42 is **100% complete (34/34 mapped)**. The Change Board hereby ratifies that `cd_cx_feedback` (pair 10 asymmetric read-and-score engine) + `cd_vendor_portal` (P05) constitute M42's official, certified delivery unit.
