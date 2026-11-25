"""A02 ERP review (20 Nov 2026), M01 SLA clocks and report periods.

- a technician assigned while the order is still a draft stamped the first
  response before any clock existed; intake then skipped the response clock
  and the order dropped out of response-SLA reporting
- a priority change re-timed the clocks from the policy header, not the
  policy's item (target, calendar, warning point) a fresh start uses
- the M01 reports cut periods on UTC days, unlike M02-M31 (Dhaka)

``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (fixtures are imported and used as parameters)

from datetime import datetime

from odoo.addons.cd_p03_portal.controllers.a02 import m01 as p03_m01
from odoo.addons.cd_service_order.models import fix_service_order as so_mod
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import order, w  # noqa: F401
from odoo.addons.cd_service_order.tests.test_a02_p1p2_cd_service_order import supervisor


def _clocks(w, o, kpi):
    return w.env["fix.sla.kpi.instance"].for_record(o, kpi_code=kpi)


def test_a_draft_assignment_does_not_pre_empt_the_response_clock(w):
    o = order(w)
    assert o.state == "draft"
    tech = w.env["hr.employee"].create({"name": "Review draft tech"})
    o.sudo().write({"technician_id": tech.id})
    assert not o.sla_response_at  # no clock yet, nothing to answer
    o.action_intake()
    # the clock starts at intake and the assignment already made answers it
    assert o.sla_response_at and o.sla_response_deadline
    clocks = w.env["fix.sla.kpi.instance"].search(
        [
            ("res_model", "=", o._name),
            ("res_id", "=", o.id),
            ("kpi_code", "=", so_mod.RESPONSE_KPI),
        ]
    )
    assert clocks and set(clocks.mapped("state")) == {"succeeded"}


def test_a_priority_change_takes_the_policy_items_target(w):
    sup = supervisor(w)
    o = order(w)
    o.action_intake()
    urgent = (
        w.env["fix.sla.policy"]
        .sudo()
        .create(
            {
                "code": "RV-URG-%d" % o.id,
                "name": "Review urgent walk-in",
                "service_type": "walk_in",
                "priority": "urgent",
                "response_hours": 1.0,
                "resolution_hours": 4.0,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Resolution (item)",
                            "kpi_code": "resolution",
                            "target_hours": 6.0,
                            "warn_at_pct": 50.0,
                        },
                    )
                ],
            }
        )
    )
    if o._fix_match_sla_policy("urgent") != urgent:
        import pytest

        pytest.skip("another urgent walk-in policy ranks first in this database")
    o.with_user(sup).action_override_priority("urgent", "VIP escalation")
    clock = _clocks(w, o, "resolution")
    assert clock.policy_id == urgent
    # the item's 6 h, as start_for would give, not the header's 4 h
    assert clock.target_hours == 6.0


def test_m01_report_periods_are_dhaka_days():
    domain = p03_m01._period([], "sla_resolution_at", "2026-11-20", "2026-11-20")
    # 20 Nov in Dhaka is 19 Nov 18:00 UTC .. 20 Nov 18:00 UTC
    assert domain == [
        ("sla_resolution_at", ">=", datetime(2026, 11, 19, 18, 0)),
        ("sla_resolution_at", "<", datetime(2026, 11, 20, 18, 0)),
    ]
