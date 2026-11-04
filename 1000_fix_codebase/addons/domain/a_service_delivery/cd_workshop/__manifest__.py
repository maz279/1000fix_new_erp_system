# cd_workshop — M31 Workshop & Depot Repair (P05-M02, RR-03 Milestone R03-M02).
# Bench assignment, WIP board, repair-level routing L1/L2/L3, evidence packs, burn-in & QC.
{
    "name": "1000FiX Workshop & Depot Repair",
    "summary": "Workshop & depot repair management: bench allocation, L1/L2/L3 routing, WIP board, burn-in protocols, and document evidence pack (M31)",
    "description": """
CD-M31-01 / CD-M31-02 / CD-M31-03: Workshop & Depot Repair (M31, Wave 2).

Key Features:
- Workshop & Depot Facility Master (fix.workshop)
- Repair Bench Master with L1/L2/L3 capabilities & ESD safety (fix.workshop.bench)
- Workshop Job with unified state machine (AS-06) and multi-job handling (fix.workshop.job)
- Consumed Parts Line with stock decrements (fix.workshop.part.line)
- Governed Evidence Pack utilizing cd_document_core attachment API (AS-01 / fix.workshop.evidence)
- Burn-in testing protocols and station management
- Cross-wave stubs: STUB-M31-M22-001 (Certification) and STUB-M31-M23-001 (QC)
- Domain events emitted via fix_events outbox (AS-08)
- 100% Bilingual support (English + Bengali)
""",
    "version": "19.0.2.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Service Delivery/Workshop",
    "depends": [
        "base",
        "mail",
        "operating_unit",
        "cd_entity_config",
        "cd_service_order",
        "cd_document_core",
        "cd_event_outbox",
        "cd_employee_core",
        "cd_inventory",
        "cd_equipment_register",
        "cd_qms_process",
        # A02 audit B1: BER, extra parts and the certification waiver are
        # routed M63 approvals (already loaded through cd_service_order)
        "cd_workflow_engine",
        # A02 audit M31-4: parts are reserved and consumed as stock.move
        # (stock is already loaded through cd_inventory)
        "stock",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_workshop_security.xml",
        "security/fix_workshop_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/fix_workshop_data.xml",
        "views/fix_workshop_views.xml",
        "views/fix_workshop_menus.xml",
    ],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-M31-01",
    "x_module_id": "M31",
    "x_wave": "W2",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery_and_Operations",
    "x_tier": "T3",
}
