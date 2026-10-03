# cd_document_core — M24-core Document kernel (P03-M07-T03, MV-02).
# fix.document on ir.attachment + retention class + attachment API.
# 17 modules in W1-W2 attach documents — this is what they all consume.
{
    "name": "1000FiX Document Core",
    "summary": "Document kernel: fix.document on ir.attachment, retention class, attachment API (M24-core, MV-02)",
    "description": """
CD-M24-nn: the document kernel (M24-core, moved to W1 by MV-02).

Owns:
- fix.document (the kernel document model on ir.attachment)
- fix.retention.class (the retention schedule model, loaded as content per LG-009)
- The attachment API consumed by every W1-W2 module (AS-01/IN-002)

Templates, e-signature envelopes, approval chains, legal hold and Mayan EDMS
integration stay in W3/W5 — this is the kernel only.
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/Documents",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/fix_document_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M24-01",
    "x_module_id": "M24",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
