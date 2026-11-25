"""19.0.1.2.0 — land the truthful engine taxonomy on existing databases.

(a) refresh the register from the truthful catalogue (action_load_register
    rewrites engine / engine_ref / implementation / executor_note /
    failure_policy per the catalogue and deactivates rows the estate does
    not implement);
(b) convert any NON-catalogue row still carrying a retired engine value
    (odoo_automated_action | airflow | domain_service — none of whose
    references ever resolved, A4-F01) to engine 'manual', implementation
    'none', active False, with an executor_note saying the 19.0.1.2.0
    migration deactivated it because its reference could not be resolved;
(c) idempotent: the loader is idempotent by design, and after the first run
    no row carries a retired engine value, so step (b) finds nothing.
"""

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

RETIRED_ENGINES = ("odoo_automated_action", "airflow", "domain_service")


def migrate(cr, version):
    cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'fix_automation'")
    if not cr.fetchone():
        # nothing installed yet — the catalogue loads with the module
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    automations = env["fix.automation"].with_context(active_test=False)

    # (a) the truthful catalogue, then (b) whatever it does not own
    loaded = automations.action_load_register()
    retired = automations.search([]).filtered(lambda a: a.engine in RETIRED_ENGINES)
    for row in retired:
        row.write(
            {
                "engine": "manual",
                "engine_ref": False,
                "implementation": "none",
                "active": False,
                "executor_note": (
                    "Deactivated by the cd_workflow_engine 19.0.1.2.0 migration: "
                    "its engine reference (%s %r) could not be resolved to anything "
                    "executable." % (row.engine, row.engine_ref)
                ),
            }
        )
    _logger.info(
        "cd_workflow_engine 19.0.1.2.0: register refreshed (%d new row(s)), "
        "%d non-catalogue row(s) with retired engine values deactivated",
        loaded,
        len(retired),
    )
