# cd_campaign — M35 Marketing, Campaigns & Demand Generation (P08-M04-T08).
{
    "name": "1000FiX Marketing",
    "summary": "M35: campaigns with audience segments, response attribution, bilingual content (CD-M35-nn)",
    "description": """
CD-M35-01 (P08-M04-T08) — 02-02 Category B W5 places M35 here (02-02
4.2 omits it entirely; §0.4.0 records the variance):

- fix.campaign — channel, budget (Monetary), state machine with the
  pause/resume discipline; consumes M10's campaign hooks from Phase 5
  via events (campaign hooks were the seam; attribution flows back)
- fix.campaign.response — the attribution ledger: every lead/response
  carries its campaign; demand generation is measurable per spend
- bilingual content fields throughout (DE-17)
- events: campaign.launched, campaign.completed, campaign.response
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Marketing",
    "depends": ["base", "mail", "cd_entity_config", "cd_party_master",
                 "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/fix_campaign_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M35-01",
    "x_module_id": "M35",
    "x_wave": "W5",
    "x_owner": "Growth",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T7",
}
