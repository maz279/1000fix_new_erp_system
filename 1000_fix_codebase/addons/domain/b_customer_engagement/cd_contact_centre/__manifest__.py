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
    "version": "19.0.1.3.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Customer/Contact Centre",
    # cd_workflow_engine: the NLU dataset release is a routed four-eyes
    # decision through the M63 engine (A03 audit M32 G4).
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_party_master",
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_cc_groups.xml",
        "data/fix_cc_gap_cron.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/fix_cc_presence_data.xml",
        # A03 audit W1: party.merged consumer (re-points are logged).
        "data/fix_party_merge_consumers.xml",
        # A02 audit B2: customer SMS on estimate.sent / service_order.ready.
        "data/fix_m01_notif_consumers.xml",
        "data/fix_a02_notif_consumers.xml",
        # A11 audit P2: approver e-mail/SMS on approval.* events.
        "data/fix_approval_notify_consumers.xml",
        # A10 S6 (M61 -> M27 hand-off): sync knowledge bindings on publish.
        "data/fix_knowledge_consumers.xml",
        "views/fix_contact_centre_views.xml",
        # M27 capture audit pass 2: the missed-callback sweep.
        "data/fix_cc_capture2_data.xml",
        # M32 capture pass 3: the safety floor of the handoff signal phrases.
        "data/fix_assistant_signal_data.xml",
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
