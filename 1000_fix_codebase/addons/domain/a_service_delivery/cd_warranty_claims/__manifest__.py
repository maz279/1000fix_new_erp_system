{
    "name": "1000FiX Warranty & Claims",
    "summary": "M09: protection products, AUT-018 auto-claims, evidence pack with blocking completeness check, remittance reconciliation (CD-M09-03)",
    "description": """
CD-M09-01..05: the warranty and claims engine.

- fix.warranty.product — extensions and protection plans through M37, with
  waiting periods (WTY-12), aggregate limits (WTY-14) and excess (WTY-13)
- fix.warranty.claim — AUT-018 auto-creation from completed warranty jobs
  (G4-01: within 24h, submitted within 72 — the deadline is on the claim);
  the EVIDENCE PACK completeness check BLOCKS submission (T05: an incomplete
  claim is a rejected claim); the claim record, evidence and reconciliation
  stay in Odoo while the per-brand transformation is Airflow configuration
  (T06); remittance matching flags mismatches, never auto-adjusts (T08)
- fix.warranty.evidence — the seven-item pack: photos before/after,
  diagnostic, parts, serial, technician certification, purchase proof
- Events: warranty_claim.submitted/decided/remitted (AS-08)
""",
    "version": "19.0.2.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Service Delivery/Warranty",
    "depends": [
        "base",
        "mail",
        "product",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_catalogue",
        "cd_device_registry",
        "cd_service_order",
        "cd_document_core",
        # A10 P1-7 (M61-4): a distributed safety recall bulletin becomes an
        # M09 recall campaign (fix.warranty.recall.bulletin_id).
        "cd_knowledge",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron_aut018.xml",
        "data/fix_recall_consumers.xml",
        "views/fix_warranty_claims_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M09-03",
    "x_module_id": "M09",
    "x_wave": "W4",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery_and_Operations",
    "x_tier": "T6",
}
