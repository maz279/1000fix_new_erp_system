{
    "name": "1000FiX E-Signature",
    "summary": "M24 completion: provider-independent e-signature envelopes with evidence hashing (CD-M24-03)",
    "description": """
CD-M24-03: e-signature envelopes.

- fix.esignature.envelope — subject + document + ordered signers; SHA-256
  evidence hash over document identity + signer list (tamper evidence);
  completion events
- fix.esignature.signer — the signing order (unique sequences enforced)
- The L6 qualified-signature PROVIDER is a CFO-approved external component
  (a written OSS-alternative review is a governance item); the envelope is
  deliberately provider-independent
""",
    "version": "19.0.2.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/Documents",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox", "cd_document_core"],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/fix_esignature_views.xml",
        "data/fix_esignature_cron.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M24-03",
    "x_module_id": "M24",
    "x_wave": "W3",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
