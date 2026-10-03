{
    "name": "1000FiX Workflow Engine",
    "summary": "M63: the AUT-001..060 automation register with named engines, approval matrix seam, Airflow orchestration (CD-M63-01/02/04)",
    "description": """
CD-M63-01/02/04: process automation.

- fix.automation — the 60-automation register (data/aut_register.yaml,
  extracted from 05-05 section 12); every row carries a NAMED engine
  (odoo_automated_action | airflow | domain_service — P06-M08-T04);
  engine-gap reporting for G3 evidence (never assumed done)
- fix.approval.matrix — the 05-04 section 7 authority matrix in one place
- Notifying automations PUBLISH EVENTS consumed by the W1 notification
  dispatcher (closes the M63 -> M27 violation — no direct calls)
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Operations/Automation",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/fix_workflow_engine_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M63-01",
    "x_module_id": "M63",
    "x_wave": "W3",
    "x_owner": "People & Governance",
    "x_category": "I_Governance_Risk_Quality_and_Knowledge",
    "x_tier": "T4",
}
