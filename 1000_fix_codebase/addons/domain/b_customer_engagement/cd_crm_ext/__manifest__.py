# cd_crm_ext — M07 CRM W1 slice (P04-M04): lead and opportunity only.
# Built on Odoo crm, extended not forked (AS-05/FF-03).
{
    "name": "1000FiX CRM Extension",
    "summary": "Lead and opportunity W1 slice on Odoo crm, party-linked, with lead-to-service-order conversion (M07 W1)",
    "description": """
CD-M07-nn: CRM extension, W1 slice only (lead + opportunity).

W4 slice (quotation, pricing) arrives with M07's W4 completion — deferred
explicitly in the backlog (P04-M04-T08).
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Customer Engagement/CRM",
    "depends": ["base", "mail", "crm", "cd_entity_config", "cd_party_master",
                 "cd_event_outbox", "cd_service_order"],
    "data": ["security/ir.model.access.csv", "views/crm_lead_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M07-01",
    "x_module_id": "M07",
    "x_wave": "W1",
    "x_owner": "Service Delivery",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T3",
}
