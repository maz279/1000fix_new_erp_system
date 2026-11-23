# cd_event_outbox — the transactional outbox (P03-M03-T02, CD-M28-01).
# AS-08: the outbox write happens in the SAME database transaction as the
# business write — that is what makes events reliable rather than best-effort.
# FF-28: only libs/py/fix_events may publish; no direct bus clients.
{
    "name": "1000FiX Event Outbox",
    "summary": "Transactional outbox — domain events written atomically with the business write (AS-08)",
    "description": """
CD-M28-01: the transactional outbox.

Every model that produces a domain event writes a fix.event.outbox record in
the SAME transaction as the business write. The publisher (fix_events) drains
the outbox and publishes to the bus. An event delivered twice produces one
effect (idempotent consumers); a failed publish retries; a poisoned message
dead-letters.
    """,
    "version": "19.0.1.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/Integration",
    "depends": ["base", "mail", "cd_entity_config"],
    "data": [
        "security/ir.model.access.csv",
        "security/fix_event_outbox_security.xml",
        "data/fix_event_relay_cron.xml",
        "views/fix_event_outbox_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M28-01",
    "x_module_id": "M28",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T0",
}
