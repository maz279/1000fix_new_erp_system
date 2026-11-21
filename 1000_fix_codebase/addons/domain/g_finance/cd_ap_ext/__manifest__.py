{
    "name": "1000FiX Accounts Payable",
    "summary": "M52 core: vendor invoices with blocking three-way match, TDS, expense claims, payment-request events (CD-M52-01)",
    "description": """
CD-M52-01: the accounts-payable core.

- fix.vendor.invoice (+line) — the THREE-WAY MATCH (AR-006 section 4.1
  pair 11: the seam belongs in M52, consuming M16/M15 events, NOT in M16).
  G3-06: an unmatched invoice is BLOCKED, never warned about — payment is
  refused unless match_state == matched
- TDS determination is a SYNCHRONOUS call into M51 (pair 8); M51 consumes
  AP events, never the reverse
- fix.expense.claim — employee expense on the M21-core master (MV-01)
- T06: payment requests go to M50 as EVENTS (payment.requested) — no
  synchronous back-call (pair 9)
- A08 build: amount-based approval matrix with segregation of duties and an
  append-only approver log; GL posting on approval; TDS/VDS from M51's
  effective-dated Tax Rate Master with the Vendor Tax Profile (PSR expiry
  drives the non-filer multiplier); Mushak 6.7/6.8 vendor notes; payment
  runs creating fix.payment.execution rows on BEFTN/RTGS/NPSB/cheque;
  per-diem & mileage rate master, expense policy enforced on submit,
  employee advances & floats with settlement and recovery
""",
    "version": "19.0.1.1.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Finance/Payables",
    "depends": [
        "base",
        "mail",
        "account",
        "product",
        "hr",
        "cd_entity_config",
        "cd_employee_core",
        "cd_event_outbox",
        "cd_tax_engine_bd",
        "cd_requisition",
        "cd_gl_ext",
        "cd_cash_position",
        # M49 capital invoices: a capital bill line books its posted cost to a
        # CWIP project (no cycle: cd_fixed_asset_ext does not depend on AP)
        "cd_fixed_asset_ext",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "security/fix_a08_rules.xml",
        "data/fix_ap_data.xml",
        "data/fix_ap_automation.xml",
        "data/fix_ap_capture_data.xml",
        "views/fix_ap_ext_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M52-01",
    "x_module_id": "M52",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "G_Finance_and_Treasury",
    "x_tier": "T5",
    "x_note": "Three-way match (CD-M16-04 in the register) lives HERE per AR-006 section 4.1 pair 11.",
}
