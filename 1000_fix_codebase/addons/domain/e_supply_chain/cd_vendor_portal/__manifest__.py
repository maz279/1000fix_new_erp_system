{
    "name": "1000FiX Vendor Portal (P05)",
    "summary": "P05 W3 slice: vendor PO acknowledgement + invoice submission feeding the three-way match, on Odoo Portal (P06-M09)",
    "description": """
P05 W3 slice (roadmap P06-M09-T01/T02/T03):

- Vendor portal group (base.group_portal + P05 role) with EA-05 record
  rules — a vendor sees only their own POs and invoices
- My Purchase Orders: the acknowledgement surface (fix.purchase.order's
  action_acknowledge, called by the vendor)
- My Invoices: submission feeding cd_ap_ext's three-way match — G3-06:
  blocked invoices are visible with their block reason, never warned about
- M42 supplier register under dual control (A06 S7): Supplier Steward /
  Supplier Approver roles, the activation gate M16 enforces on every PO,
  bank-detail changes as confirmed proposals with a payment block,
  scorecards computed from M16 receipts and frozen once published
- The R2 Bootstrap SCSS bundle and vendor onboarding (EO content, T04) land
  with the Next.js completion; this is the Odoo-native R3 slice
""",
    "version": "19.0.1.2.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Purchase/Portal",
    "depends": [
        "base",
        "portal",
        "mail",
        "cd_entity_config",
        "cd_rbac_ext",
        "cd_event_outbox",
        "cd_requisition",
        "cd_ap_ext",
        # vendor-ledger satellites on the M33 party import batch (2026-11-09
        # readiness report §7A): fix.supplier register + tax profiles
        "cd_party_master",
    ],
    "data": [
        "security/fix_vendor_portal_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_vendor_portal_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "data/fix_supplier_consumers.xml",
        "views/fix_vendor_portal_views.xml",
    ],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-P05-01",
    "x_module_id": "P05",
    "x_wave": "W3",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T4",
    "x_note": "Portal P05 (register: p05_supplier_portal); RFQ rows (CD-M16-02) land with the R2 completion.",
}
