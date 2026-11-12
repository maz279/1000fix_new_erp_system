# cd_crm_ext — M07 CRM (P04-M04 W1 slice + 2026-10-27 rebuild surfaces).
# Built on Odoo crm, extended not forked (AS-05/FF-03).
{
    "name": "1000FiX CRM Extension",
    "summary": "M07 CRM on Odoo crm: party-linked leads/opportunities, multi-pipeline, forecast snapshots, account management, QBR, renewal pipeline",
    "description": """
CD-M07-01: CRM extension on Odoo crm (L1 substrate, extended not forked).

W1 slice (P04-M04): lead + opportunity, party-kernel link, lead-to-service-order
conversion. W4 slice (quotation, pricing) arrives with M07's W4 completion —
deferred explicitly in the backlog (P04-M04-T08).

M07 rebuild (2026-10-27) adds:
- fix.pipeline (multi-revenue-stream stage configuration, T-02/BRU-CRM-03 gating)
- fix.account.assignment (BRU-CRM-08 owner coverage) + fix.account.plan
- fix.qbr + fix.qbr.action (scheduling, meeting records, action tracking;
  data assembly/PDF is the W4 seam on M05/M34 data)
- fix.renewal (the T-90 renewal pipeline, BRU-CRM-12 no-delete, win-back handoff)
- fix.forecast.snapshot (immutable period snapshots, BRU-CRM-06/07)
- crm.lead: pipeline, forecast category, competitor/price position, loss
  reason code, cross-sell flag, stage-gate confirmation

A03 P2 (2026-11-03) adds:
- opportunity -> estimate link; Won and conversion need the approved estimate
- contract verification routed through the M63 engine (no self-certification)
- standard stage gates as data; schedulers for QBR, forecast and renewals
- the journey.lead_requested consumer (R8)

D365 screen convention: the user-facing screens are the in-workspace surfaces
in cd_p03_portal (static/src/a03/m07.js); Odoo views here are substrate only.
""",
    "version": "19.0.1.3.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Customer Engagement/CRM",
    "depends": [
        "base",
        "mail",
        "crm",
        "cd_entity_config",
        "cd_party_master",
        "cd_event_outbox",
        "cd_service_order",
        "cd_contact_centre",
        "cd_workflow_engine",
    ],
    "data": [
        "data/fix_lead_score_data.xml",
        "data/fix_crm_gap_cron.xml",
        "data/fix_pipeline_default.xml",
        "data/fix_crm_event_consumers.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        # A03 audit W1: party.merged consumer (re-points are logged).
        "data/fix_party_merge_consumers.xml",
        "views/crm_lead_views.xml",
        "views/fix_crm_rebuild_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M07-01",
    "x_module_id": "M07",
    "x_wave": "W1",
    "x_owner": "Service Delivery",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T3",
}
