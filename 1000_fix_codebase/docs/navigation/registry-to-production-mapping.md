# Navigation Registry → Production Mapping (PP0-M03-T02)

**Status**: BINDING SPEC · **Date**: 2026-10-05 · **Consumes**:
`contracts/nav/registry.json` (generated from the frozen prototype)
· **Serves**: P03 menus (PP2), portal routes (PP3/PP5), Tell-ME search,
Report Center, the coverage ledger (Gate GP D1)

This document binds every registry module to its production realisation and
defines the screen-key → Odoo menu convention PP2 implements. It is verified
by `tooling/fitness/check_portal_contract.py` (check 6: registry coverage).

## 1. Module-level mapping (67 rows — the binding table)

Realisation kinds: **cd** = first-party Odoo module(s) (manifest
`x_module_id`) · **embedded** = realised inside another cd module ·
**shared** = secondary ID of a cd module · **odoo-core** = Odoo/OCA layer ·
**l4-embed** = embedded BI (L4) · **l5-service** = standalone service (L5) ·
**planned** = scheduled, not yet built · **pending** = no realisation yet
(gap — carried in the completeness ledger, never hidden).

| M-id | Registry name | Kind | Production realisation |
|---|---|---|---|
| M01 | Service Requests & Orders | cd | cd_service_order |
| M02 | Field Service & Dispatch | embedded | cd_service_order (dispatch board + work orders); route-orchestrator seam W3 |
| M03 | Service Logistics (Pick & Drop) | cd | cd_consignment |
| M04 | Branch & Front-Desk | cd | cd_front_desk |
| M05 | Remote Support & MSP | cd | cd_msp_contract |
| M06 | Data Services & Recovery | cd | cd_data_case |
| M07 | CRM & Sales Pipeline | cd | cd_crm_ext |
| M08 | Contract Lifecycle (AMC) | cd | cd_contract_core |
| M09 | Warranty & Claims | cd | cd_warranty_claims |
| M10 | Loyalty & Rewards | pending | NO production realisation yet — gap carried in the completeness ledger |
| M11 | Pricing & Rate Cards | cd | cd_dynamic_pricing, cd_rate_card |
| M12 | Marketplace & Sellers | cd | cd_marketplace |
| M13 | Rental & EaaS | cd | cd_rental_asset |
| M14 | Trade-In & Refurbishment | cd | cd_tradein |
| M15 | Spare Parts & Inventory | odoo-core | Odoo stock + OCA stock-logistics-* (roadmap P05-M01, AS-05) |
| M16 | Procurement & Sourcing | cd | cd_requisition |
| M17 | Device & Asset Registry | cd | cd_device_registry |
| M18 | E-Waste & Recycling | cd | cd_ewaste |
| M19 | Financial Accounting & GL | cd | cd_gl_ext |
| M20 | AR, Invoicing & Collections | cd | cd_billing_engine |
| M21 | Core HR & Lifecycle | cd | cd_employee_core, cd_hr_core |
| M22 | Learning & Certification | cd | cd_competency |
| M23 | Quality Management (ISO) | cd | cd_qms_process |
| M24 | Documents & E-Signature | cd | cd_document_core, cd_esignature |
| M25 | Business Intelligence | l4-embed | Apache Superset + Grafana embedded (P06); catalogue in cd_metric_registry |
| M26 | AI/ML Services (14 models) | l5-service | services/ml-gateway (14 models, dispatch/demand) |
| M27 | Contact Centre (16743) | cd | cd_contact_centre |
| M28 | Integration, API & Events | cd | cd_event_outbox |
| M29 | Identity, Access & Security | cd | cd_rbac_ext |
| M30 | Platform Administration | cd | cd_entity_config |
| M31 | Workshop & Depot Repair | embedded | cd_service_order (fix.work.order + workshop states) |
| M32 | Conversational AI (Bengali) | l5-service | services/stt (Bengali STT + PDPA gate) |
| M33 | Customer & Party Master | cd | cd_party_master |
| M34 | CX, Feedback & Complaints | cd | cd_cx_feedback |
| M35 | Marketing Campaigns | cd | cd_campaign |
| M36 | Quotations & Tenders | cd | cd_quotation |
| M37 | Product & Service Catalogue | cd | cd_catalogue |
| M38 | E-Commerce Storefront | cd | cd_storefront |
| M39 | Subscriptions & Recurring | cd | cd_subscription |
| M40 | Partner & Channel | cd | cd_partner |
| M41 | Warehouse Management | cd | cd_wms_structure |
| M42 | Supplier Relationship | shared | cd_cx_feedback (supplier scorecard — module's secondary ID, primary M34) |
| M43 | Demand Planning | cd | cd_demand_plan |
| M44 | Import & Trade Compliance | cd | cd_import_order |
| M45 | Enterprise Assets & Test Equipment | cd | cd_equipment_register |
| M46 | Fleet & Vehicles | cd | cd_vehicle_ext |
| M47 | Facility & Branch Infrastructure | cd | cd_facility |
| M48 | IoT Telemetry & Predictive | cd | cd_stream_registry |
| M49 | Fixed Assets & Capex | cd | cd_fixed_asset_ext |
| M50 | Treasury & Banking | cd | cd_cash_position |
| M51 | Tax & Regulatory (BD) | cd | cd_tax_engine_bd |
| M52 | AP & Employee Expense | cd | cd_ap_ext |
| M53 | Revenue Recognition & Settlement | cd | cd_settlement_ext |
| M54 | Costing, Budget & FP&A | cd | cd_fpa |
| M55 | Time, Attendance & Scheduling | cd | cd_attendance |
| M56 | Payroll & Statutory | cd | cd_payroll_bd |
| M57 | Performance & Incentives | cd | cd_performance |
| M58 | Talent Acquisition | cd | cd_talent |
| M59 | Health, Safety & Wellbeing | cd | cd_hse |
| M60 | Governance, Risk & Compliance | cd | cd_grc |
| M61 | Knowledge & Technical Library | cd | cd_knowledge |
| M62 | Data Platform & Governance | cd | cd_metric_registry |
| M63 | Process Automation | cd | cd_workflow_engine |
| M64 | Master Data Management | cd | cd_mdm_core |
| M65 | Multi-Entity & Localisation | planned | Phase 12 (P12-M01) — the last module of the 67 |
| M66 | Internal IT Service | cd | cd_itsm |
| M67 | Projects & Portfolio | cd | cd_ppm |

**Coverage at PP0**: 65 of 67 realised. Open items, by design and on the
record: **M10 pending** (no realisation — the completeness ledger carries it;
the registry marks every `nav.module.m10` surface as unbacked), **M65
planned** (Phase 12). Shared IDs (M11, M21, M24, M42) are legal: one registry
module may be realised by several cd modules or carry a secondary ID.

## 2. Screen-key → Odoo menu convention (PP2 implements this)

- Every **cd-kind** module owns a root menu `menu_fix_<key>_root` inside its
  module, grouped under the shared operations root (`cd_entity_config.
  menu_fix_operations_root`) — the pattern the six W1 workspaces established.
- Registry **groups** (278) map to second-level menu sections under the
  module root. **NVR-23 caps a workspace at 7 sections**; 62 of 67 modules
  exceed 7 groups in the prototype. The rule therefore applies at the
  *workspace* level: the module's workspace menu exposes at most 7 PRIMARY
  sections (the registry's own group ordering decides primacy); remaining
  groups nest one level deeper (section → group), which NVR-23 permits.
  Every module whose primary sections ≠ its full group list is recorded in
  the PP2 exceptions register — recorded, never silently dropped.
- Registry **screens** map to `ir.actions.act_window` (t:'g','f','d','x','c')
  and QWeb report actions (t:'r' report screens link the report library).
  Screens with no backend action yet resolve to the module's list view until
  their phase lands; the coverage ledger reports them as *unbacked*.
- **Report library (346) / form register (266)**: entries attach to their
  module as report-action and wizard contracts respectively; the Report
  Center (P03) renders the registry catalogue and marks unbacked entries.

## 3. Verification

`check_portal_contract.py` check 6 (added PP0): every registry module with
kind `cd`/`embedded`/`shared` must have its named cd module(s) present in
`addons/`; kinds `odoo-core`, `l4-embed`, `l5-service`, `planned`, `pending`
must appear verbatim in the exceptions list of THIS document — so a new
module that changes realisation kind forces this spec to move in the same
commit.
