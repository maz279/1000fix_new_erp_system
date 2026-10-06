{
    "name": "1000FiX Customer Self-Service Portal (P01)",
    "summary": "P01 PP5 slice: booking, live tracking, device history, ownership transfer, estimate approval and the PDPA consent dashboard via the portal API (CD-P01-01)",
    "description": """
P01 PP5 slice (roadmap PP5-M01):

- The API surface the Next.js (R2) customer portal consumes — the W4
  OpenAPI contract in contracts/openapi/w4-portals.json (PS-11 tests
  enforce; AS-09: no business rule lives in portal code)
- Booking: <=3-step service booking writing fix.service.order with the
  model's own validation (the portal passes through)
- Live tracking: order state, technician, SLA clocks — polling today,
  the websocket upgrade rides the same payload shape
- Device history: the M17 registry's own timeline (T07 history entries)
- Ownership transfer: fix.device.action_transfer_ownership — T05 said
  "portal P01 exposes this in Phase 5"; this IS that exposure
- Estimate approval: the customer records their documented approval
  (BRU-SRM-07), then the model's action_approve enforces the hard gates
- PDPA consent dashboard: grant/withdraw per channel on fix.consent
  with the state visible — closes the audit gap surfaced in PP0
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Sales/Portal",
    "depends": ["base", "portal", "mail", "cd_entity_config", "cd_rbac_ext",
                 "cd_service_order", "cd_device_registry", "cd_party_master"],
    "data": ["security/fix_customer_portal_security.xml",
             "security/ir.model.access.csv"],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-P01-01",
    "x_module_id": "P01",
    "x_wave": "W4",
    "x_owner": "Experience",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T7",
}
