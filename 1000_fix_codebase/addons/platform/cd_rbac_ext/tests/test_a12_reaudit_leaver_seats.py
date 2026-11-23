"""test_a12_reaudit_leaver_seats.py — M66-3 (A12 re-audit 2026-11-22).

The leaver hand-off already unassigns ITSM assets, revokes devices and ends
delegations; the licence seats must go back to the entitlement pool too, or
utilisation keeps counting people who left.
"""

import pytest
from odoo import fields


@pytest.fixture
def env(odoo_env):
    return odoo_env


def test_leaver_handoff_releases_active_licence_seats(env):
    if "fix.itsm.licence.seat" not in env:
        pytest.skip("cd_itsm licence seats not installed")
    employee = env["hr.employee"].create({"name": "Leaving Licence Holder"})
    licence = env["fix.itsm.licence"].create(
        {"name": "Reaudit Suite", "vendor": "Vendor", "seats_owned": 3}
    )
    licence.action_assign_seat(employee=employee.id)
    assert licence.seats_assigned == 1
    Jml = env["fix.jml.event"]
    released = Jml._fix_release_leaver_licence_seats(employee)
    assert released == 1
    seat = licence.seat_ids.filtered(lambda s: s.employee_id == employee)
    assert seat.state == "revoked" and seat.revoked_on == fields.Date.context_today(Jml)
    audit = (
        env["fix.security.audit"]
        .sudo()
        .search(
            [
                ("event", "=", "leaver_licence_seats"),
                ("object_ref", "=", "hr.employee,%d" % employee.id),
            ],
            limit=1,
        )
    )
    assert audit, "the release must leave its security-audit row"
