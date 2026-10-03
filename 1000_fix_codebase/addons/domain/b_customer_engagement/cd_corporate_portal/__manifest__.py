{
    "name": "1000FiX Corporate B2B Portal (P04)",
    "summary": "P04 W4 slice: corporate estate view, consolidated invoices, at-scale service requests via the portal API (CD-P04-01)",
    "description": """
P04 W4 slice (roadmap P07-M09-T01/T02):

- Corporate portal group on base.group_portal, EA-05 record rules — a
  corporate user sees only their own estate, invoices and requests
- The API surface the Next.js (R3) portal consumes is the OpenAPI contract
  in services/portal-contracts (PS-11 contract tests enforce server-side
  validation — AS-09: no business rule lives in portal code)
- Multi-site account administration rides fix.party.hierarchy (T02)
- P08 brand partner + P10 agent console surfaces ride the M09 claim model
  and the M27 conversation model respectively — published through events,
  consumed through the API
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Sales/Portal",
    "depends": ["base", "portal", "mail", "cd_entity_config", "cd_rbac_ext",
                 "cd_contract_core", "cd_subscription", "cd_warranty_claims",
                 "cd_contact_centre"],
    "data": ["security/ir.model.access.csv", "views/fix_corporate_portal_views.xml"],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-P04-01",
    "x_module_id": "P04",
    "x_wave": "W4",
    "x_owner": "Experience",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T7",
}
