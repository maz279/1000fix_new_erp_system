"""cd_itsm tests — P09-M08 (CD-M66-01).

A12 rewrite (2026-11-05): this suite was four inspect.getsource() greps
(test_ticket_lifecycle / test_categories / test_events / test_resolve_gate
asserting substrings of the model's source). The ticket behaviours they
gestured at are now LIVE-ORM tests in test_itsm_orm.py (lifecycle states,
category values, published events, resolve gating) and the role attacks in
test_a12_m66_controls.py. What this file now covers is the rest of M66 as
behaviour: the catalogue (SLA source), problem register (M66-10), licence
register (M66-11) and CMDB (M66-13).
"""

from __future__ import annotations

import pytest
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError


def _problem(env, **extra):
    vals = {"title": "POS printer batch failure", "severity": "high"}
    vals.update(extra)
    return env["fix.itsm.problem"].create(vals)


def test_catalogue_is_the_sla_source(odoo_env):
    catalogue = odoo_env["fix.itsm.catalogue"].create(
        {"code": "CAT-SLA", "name": "Loaner laptop", "target_hours": 6.0}
    )
    assert catalogue.target_hours == 6.0
    with pytest.raises(IntegrityError), odoo_env.cr.savepoint():
        odoo_env["fix.itsm.catalogue"].create({"code": "CAT-SLA", "name": "Duplicate"})


def test_problem_known_error_needs_workaround_and_state(odoo_env):
    problem = _problem(odoo_env, root_cause="Firmware 3.2 race")
    # M66-10: no workaround, no known error.
    with pytest.raises(UserError, match="workaround"), odoo_env.cr.savepoint():
        problem.action_known_error()
    problem.workaround = "Swap to USB queue; fix in 3.3"
    problem.action_known_error()
    assert (problem.state, problem.known_error) == ("known_error", True)
    # From the wrong state it is refused.
    problem2 = _problem(odoo_env, root_cause="x", workaround="y")
    problem2.action_known_error()
    with pytest.raises(UserError, match="open or under investigation"), odoo_env.cr.savepoint():
        problem2.action_known_error()
    # A resolved problem names its root cause.
    problem2.action_resolve()
    assert problem2.state == "resolved"
    bare = _problem(odoo_env)
    bare.action_investigate()
    with pytest.raises(UserError, match="root cause"), odoo_env.cr.savepoint():
        bare.action_resolve()


def test_problem_state_is_guarded(odoo_env):
    # The guard trusts only superuser code and transition tokens (A03), so the
    # attack runs as a real agent user, not the superuser fixture.
    agent = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M66 Guard Probe",
                "login": "m66.guard.probe@a12.test",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            odoo_env.ref("base.group_user").id,
                            odoo_env.ref("cd_itsm.group_itsm_agent").id,
                        ],
                    )
                ],
            }
        )
    )
    problem = _problem(odoo_env)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        problem.with_user(agent).write({"state": "resolved"})
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        odoo_env["fix.itsm.problem"].with_user(agent).create(
            {"title": "Forged", "state": "closed", "known_error": True}
        )


def test_licence_seats_and_computed_state(odoo_env):
    # M66-11: assigned may never exceed owned.
    with pytest.raises(ValidationError, match="seats assigned"), odoo_env.cr.savepoint():
        odoo_env["fix.itsm.licence"].create(
            {"name": "Office", "vendor": "MS", "seats_owned": 10, "seats_assigned": 11}
        )
    licence = odoo_env["fix.itsm.licence"].create(
        {"name": "Office", "vendor": "MS", "seats_owned": 10, "seats_assigned": 4}
    )
    assert licence.utilisation_pct == 40.0
    with pytest.raises(ValidationError, match="non-negative"), odoo_env.cr.savepoint():
        licence.seats_owned = -1
    # The status is the renewal date, not an opinion.
    from odoo import fields

    licence.renewal_on = fields.Date.subtract(fields.Date.context_today(licence), days=3)
    assert licence.state == "expired"
    licence.renewal_on = fields.Date.add(fields.Date.context_today(licence), days=10)
    assert licence.state == "expiring"
    licence.renewal_on = fields.Date.add(fields.Date.context_today(licence), days=90)
    assert licence.state == "active"


def test_ci_cannot_run_on_retired_asset(odoo_env):
    asset = odoo_env["fix.itsm.asset"].create(
        {"name": "Node R2", "asset_tag": "A12-CI-1", "asset_kind": "server"}
    )
    ci = odoo_env["fix.itsm.ci"].create(
        {"name": "Reporting DB", "ci_key": "a12-ci-rpt", "asset_id": asset.id}
    )
    assert ci.life_status == "in_service"
    asset.action_retire("WIPE-2026-118")
    with pytest.raises(UserError, match="under repair"), odoo_env.cr.savepoint():
        asset.action_recover()  # retirement is one-way: recover is for repair only
    with pytest.raises(ValidationError, match="retired"), odoo_env.cr.savepoint():
        ci.write({"asset_id": asset.id, "life_status": "in_service"})
