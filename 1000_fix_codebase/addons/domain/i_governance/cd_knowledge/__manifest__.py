# cd_knowledge — M61 (P09).
{
    "name": "1000FiX Knowledge Management & Technical Library",
    "summary": "M61: Knowledge Management & Technical Library (CD-M61-01)",
    "description": """
CD-M61-01 (P09) — Knowledge Management & Technical Library.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.3.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Knowledge Management & Technical Library",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_event_outbox",
        # A10 P1-7 (M61-4): the recipient lines name a duty officer
        # (hr.employee) and a recall closes only under the Quality Manager.
        "cd_employee_core",
        # M61 capture audit (2026-11-18): links, captures and feedback name the
        # catalogue's fault codes, device models and brands and the job they
        # came from (FR-KMS-006/023/030). cd_service_order brings cd_catalogue
        # and does not depend on this module (no cycle).
        "cd_service_order",
        # NOTE: cd_qms_process is deliberately NOT a dependency. The recall
        # closure gate resolves the Quality Manager group through
        # ir.model.data (raise_if_not_found=False), so no install-order
        # edge is needed — and the edge created a dependency loop once
        # A04's billing consumer (cd_billing_engine -> cd_warranty_claims)
        # met this module's recall consumers (cd_warranty_claims ->
        # cd_knowledge -> cd_qms_process -> cd_cx_feedback ->
        # cd_loyalty -> cd_billing_engine). Cross-session composition
        # caught 2026-11-05; neither branch's cycle check saw the other's.
    ],
    "data": [
        "security/fix_knowledge_groups.xml",
        "security/fix_m61_capture_rules.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/knowledge_ops_sequences.xml",
        "data/fix_m61_capture_sequences.xml",
        "data/fix_knowledge_consumers.xml",
        "data/fix_knowledge_cron.xml",
        "views/cd_knowledge_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M61-01",
    "x_module_id": "M61",
    "x_wave": "W6",
    "x_owner": "Knowledge Management & Technical Library",
    "x_category": "Phase9",
    "x_tier": "T9",
}
