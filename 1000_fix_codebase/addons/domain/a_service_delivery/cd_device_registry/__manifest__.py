# cd_device_registry — M17 Device & Customer Asset Registry core (P04-M01, MV-05).
# Every W1 module (M01, M04) depends on this — the device IS the transacting entity.
{
    "name": "1000FiX Device Registry",
    "summary": "Device and customer asset registry: serial/IMEI uniqueness, warranty status, ownership transfer, device history (M17-core, MV-05)",
    "description": """
CD-M17-nn: the device registry core (M17, W1 per MV-05).

THE identity model: serial number and IMEI uniqueness with duplicate detection.
Warranty status (consumed by M09 in Phase 7). Ownership and transfer-of-ownership
(exposed to customers via portal P01 in Phase 5). Device history — every service
order against a device, permanently.
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Service Delivery/Registry",
    "depends": ["base", "mail", "cd_entity_config", "cd_catalogue", "cd_party_master",
                 "cd_document_core", "cd_event_outbox", "cd_employee_core"],
    "data": ["security/ir.model.access.csv", "views/fix_device_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M17-01",
    "x_module_id": "M17",
    "x_wave": "W1",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery_and_Operations",
    "x_tier": "T2",
}
