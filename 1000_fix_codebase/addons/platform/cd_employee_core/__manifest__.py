# cd_employee_core — M21-core Employee master (P03-M08, MV-01).
# The W1 slice only: the master and the joiner/mover/leaver lifecycle events.
# Learning, payroll, performance and talent stay in W5.
# MV-01 is the movement that resolves AR-006's most serious finding.
{
    "name": "1000FiX Employee Core",
    "summary": "Employee master + joiner/mover/leaver events (M21-core, MV-01); M29's access lifecycle depends on these events",
    "description": """
CD-M21-nn: the employee master core (M21-core, moved to W1 by MV-01).

Owns:
- hr.employee extension (the employee master, W1 slice only)
- JML event emission: employee.joined, employee.left, employee.role_changed
- The leaver path: M29's Keycloak deprovisioning within 1 hour (KPI-090)

The M21<->M29 interface break (AR-006 section 4.1 pair 17):
- M21 EMITS events that M29 CONSUMES (joiner/left/role_changed)
- M21 CALLS M29's published API for role assignment (sync one-way)
- NEVER synchronous-both-ways — that is a distributed monolith
""",
    "version": "19.0.1.0.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/HR",
    "depends": ["base", "mail", "hr", "cd_entity_config", "cd_event_outbox", "cd_party_master"],
    "data": [
        "security/ir.model.access.csv",
        # A09 ERP audit M58-F1: a hire through M58 dead-ended at onboarding
        # completion because no employee code existed and nothing minted one.
        # The code is now taken from this sequence at creation
        # (models/hr_employee_ext.py, _fix_next_employee_code); a hand-typed
        # code is still honoured and never overwritten.
        "data/employee_code_sequence.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M21-01",
    "x_module_id": "M21",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
