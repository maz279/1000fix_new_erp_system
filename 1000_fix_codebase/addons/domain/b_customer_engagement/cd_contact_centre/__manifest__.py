{
    "name": "1000FiX Contact Centre & AI",
    "summary": "M27 conversations + M32 assistant: unified channels, transcripts (G4-04), transactional intents, clean handoff (G4-05) (CD-M27-nn)",
    "description": """
CD-M27-nn + CD-M32-nn (P07-M05):

- fix.conversation (+turn) — unified channel model (voice/WhatsApp/chat/
  email/in-app); transcripts are the system of record (G4-04: hotline
  conversations captured); the customer-360 join key (party or contact
  identity); the human-handoff path carries FULL context (T07);
  resolution_rate() measures G4-05 against handoffs, not sessions
- fix.assistant.intent — the TRANSACTIONAL intent register (T06: the M61
  knowledge base is W6 — an already-ratified scope cut); Bengali
  utterances authored, never machine-translated (T08); grounding on live
  ERP data (CD-M32-03); handoff-on-failure
- M32 runs on self-hosted Ollama (customer data must not leave the Company
  under PDPA transfer restrictions) — the deployment config ships in
  infra/observability/ollama; this module is the Odoo-side register
- The M27<->M32 co-design pair is one increment here (AR-006 pair 16)
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Customer/Contact Centre",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox", "cd_party_master"],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/fix_contact_centre_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M27-02",
    "x_module_id": "M27",
    "x_wave": "W4",
    "x_owner": "Experience",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T7",
}
