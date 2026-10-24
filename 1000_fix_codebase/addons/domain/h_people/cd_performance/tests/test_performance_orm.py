# cd_performance live-ORM tests — P08-M04 (CD-M57-01): scorecards and the
# banded incentive run that feeds payroll (it pays people: every figure is
# hand-computed from WEIGHTS 0.35/0.30/0.20/-0.15 and bands 15/8/4/0 %).
import json

import pytest
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


def _scorecard(env, name, period, ftf, sla, csat, rework):
    return env["fix.performance.scorecard"].create(
        {
            "employee_id": env["hr.employee"].create({"name": name}).id,
            "period": period,
            "first_time_fix": ftf,
            "sla_hit": sla,
            "csat": csat,
            "rework_rate": rework,
        }
    )


def test_scorecard_composite_and_publication(odoo_env):
    # 0.35 x 0.9 + 0.30 x 0.8 + 0.20 x 0.7 - 0.15 x 0.1
    # = 0.315 + 0.24 + 0.14 - 0.015 = 0.68
    card = _scorecard(odoo_env, "Tech Arif", "2026-09", 0.9, 0.8, 0.7, 0.1)
    assert card.score == 0.68
    card.action_publish()
    assert _events(odoo_env, "scorecard.published", card.id) == [
        {"employee": "Tech Arif", "period": "2026-09", "score": 0.68}
    ]


def test_incentive_run_computes_banded_lines_and_feeds_payroll(odoo_env):
    top = _scorecard(odoo_env, "Tech Arif", "2026-09", 1, 1, 1, 0)  # 0.85 -> 8% band
    mid = _scorecard(odoo_env, "Tech Bina", "2026-09", 0.9, 0.8, 0.7, 0.1)  # 0.68 -> 4%
    low = _scorecard(odoo_env, "Tech Chan", "2026-09", 0.5, 0.5, 0.5, 0.5)  # 0.35 -> 0%
    _scorecard(odoo_env, "Other Month", "2026-08", 1, 1, 1, 0)
    run = odoo_env["fix.incentive.run"].create({"period": "2026-09", "band_base": 20000.0})
    with pytest.raises(UserError, match="Compute before applying"), odoo_env.cr.savepoint():
        run.action_apply()
    run.action_compute()
    assert run.state == "computed"
    amounts = {line.scorecard_id: line.amount for line in run.line_ids}
    # 20,000 x 8% = 1,600; x 4% = 800; x 0% = 0
    assert amounts == {top: 1600.00, mid: 800.00, low: 0.00}
    assert run.total == 2400.00
    with pytest.raises(UserError, match="Compute runs from draft only"), odoo_env.cr.savepoint():
        run.action_compute()

    run.action_apply()
    assert run.state == "applied"
    granted = {
        line.employee_id.name: _events(odoo_env, "incentive.granted", line.id)
        for line in run.line_ids
    }
    assert granted["Tech Arif"] == [
        {"employee": "Tech Arif", "period": "2026-09", "amount": 1600.0}
    ]
    assert granted["Tech Bina"] == [{"employee": "Tech Bina", "period": "2026-09", "amount": 800.0}]
    assert granted["Tech Chan"] == [{"employee": "Tech Chan", "period": "2026-09", "amount": 0.0}]


def test_incentive_run_needs_scorecards(odoo_env):
    run = odoo_env["fix.incentive.run"].create({"period": "1999-01", "band_base": 20000.0})
    with pytest.raises(UserError, match="No scorecards for 1999-01"), odoo_env.cr.savepoint():
        run.action_compute()
    assert run.state == "draft"


def test_compensation_band_ordering(odoo_env):
    Band = odoo_env["fix.compensation.band"]
    band = Band.create(
        {"name": "T2", "grade": "G2", "range_min": 25000, "range_mid": 32000, "range_max": 40000}
    )
    assert band.range_mid == 32000
    Band.create({"name": "Flat", "grade": "G0", "range_min": 1, "range_mid": 1, "range_max": 1})
    with (
        pytest.raises(UserError, match="Band range must be min <= mid <= max"),
        odoo_env.cr.savepoint(),
    ):
        Band.create(
            {
                "name": "Bad",
                "grade": "G3",
                "range_min": 50000,
                "range_mid": 45000,
                "range_max": 60000,
            }
        )
    with (
        pytest.raises(UserError, match="Band range must be min <= mid <= max"),
        odoo_env.cr.savepoint(),
    ):
        band.write({"range_max": 30000})
