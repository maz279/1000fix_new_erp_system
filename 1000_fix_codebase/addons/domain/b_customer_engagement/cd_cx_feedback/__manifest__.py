{
    "name": "1000FiX Customer Experience & Supplier Performance",
    "summary": "M34 feedback/complaints/surveys-from-events + M42 event-consuming supplier scorecards (CD-M34-nn)",
    "description": """
CD-M34-nn + CD-M42-nn (P07-M06):

- fix.survey — the post-service survey consumed FROM service_order.closed
  events (journey 1's ending); NPS-style rating; idempotent per order
- fix.complaint — the full lifecycle (journey 14: complaint -> NCR -> root
  cause -> CAPA -> verification -> closure); CRITICAL complaints close only
  through CAPA; the M23 NCR/CAPA linkages are REGISTERED STUBS with expiry
  (AR-006 §5.4 STUB + GV-005)
- fix.supplier.scorecard — M42 as the read-and-score consumer of M16 events
  (AR-006 §4.1 pair 10, the asymmetric interface): goods.received events
  score on-time/late; blocked-invoice rejections score quality; scorecards
  PUBLISH through events for the P05 portal's API
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Customer/Experience",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_party_master",
        "cd_service_order",
        "cd_document_core",
        "cd_contact_centre",
        "cd_workflow_engine",
        # A03 audit M34-9: an approved concession becomes an M20 credit note
        # or an M10 voucher. Neither depends on this module (checked), so the
        # dependency adds no cycle.
        "cd_billing_engine",
        "cd_loyalty",
    ],
    "data": [
        "data/fix_cx_gap_cron.xml",
        "data/fix_cx_cron.xml",
        "data/fix_cx_event_consumers.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        # A03 audit W1: party.merged consumer (re-points are logged).
        "data/fix_party_merge_consumers.xml",
        "views/fix_cx_feedback_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M34-01",
    "x_module_id": "M34",
    "x_wave": "W4",
    "x_owner": "Experience",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T7",
}
