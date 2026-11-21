{
    "name": "1000FiX Spare Parts & Inventory Management",
    "summary": "M15 Wave-2 slice: multi-location on fix.branch, van stock, barcode/QR scan-to-consume, replenishment rules, M43 seam (CD-M15-01)",
    "description": """
CD-M15-01: Spare Parts & Inventory Management.

Features:
- Multi-location inventory mapped to fix.branch / operating units
- Specialized Technician Van Stock location type
- Spare parts catalog with device compatibility and warranty tracking
- Barcode and QR code scan-to-consume engine on repair jobs
- Automated replenishment alerts and reorder rules with M43 forecasting seam
- GV-005 suspense valuation ledger pending Wave-3 GL cutover
- Transactional outbox events (stock.consumed, stock.returned, reorder.triggered, van.reconciled)
""",
    "version": "19.0.1.7.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Inventory/Logistics",
    "depends": [
        "base",
        "mail",
        "stock",
        "cd_entity_config",
        "cd_wms_structure",
        "cd_device_registry",
        "cd_catalogue",
        "cd_event_outbox",
        "cd_requisition",
        "cd_workflow_engine",
        # A06 ERP D1: every stock movement posts through M19 (post_with_dimensions)
        "cd_gl_ext",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/fix_isolation_rules.xml",
        "security/fix_inventory_rules.xml",
        "security/fix_m15_capture_rules.xml",
        "security/fix_wms_spec_rules.xml",
        "security/fix_stock_posting_rules.xml",
        "security/fix_a06erp_m15_rules.xml",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        # A06 ERP audit M44-17: provisional imported cost escalation (M43/M44 stream)
        "data/fix_stock_provisional_cron.xml",
        "data/ir_config_parameter.xml",
        "data/fix_event_consumers.xml",
        "data/fix_m15_capture_data.xml",
        "data/fix_wms_spec_data.xml",
        "data/fix_a06erp_m15_data.xml",
        "views/fix_inventory_views.xml",
    ],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-M15-01",
    "x_module_id": "M15",
    "x_wave": "W2",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T3",
}
