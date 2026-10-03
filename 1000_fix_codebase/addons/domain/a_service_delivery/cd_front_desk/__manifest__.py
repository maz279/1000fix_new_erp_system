# cd_front_desk — M04 Branch & Front-Desk Operations (P04-M02).
# Token queue, walk-in intake, handover, cash drawer, shift control.
{
    "name": "1000FiX Front Desk",
    "summary": "Token queue, walk-in intake (3-minute target), handover, cash drawer and shift control, daily reconciliation (M04)",
    "description": """
CD-M04-nn: Branch & Front-Desk Operations (M04).

Gate criterion: walk-in intake in under 3 minutes, demonstrated by branch staff.
Token queue management, handover with customer acknowledgement, cash drawer
and shift control with AS-10 Monetary reconciliation.
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Service Delivery/Front Desk",
    "depends": ["base", "mail", "cd_entity_config", "cd_device_registry",
                 "cd_service_order", "cd_document_core", "cd_event_outbox",
                 "cd_employee_core"],
    "data": ["security/ir.model.access.csv", "views/fix_front_desk_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M04-01",
    "x_module_id": "M04",
    "x_wave": "W1",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery_and_Operations",
    "x_tier": "T3",
}
