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
    # Normalized 3-factor: (0.40 x 0.9 + 0.25 x 0.8 + 0.20 x 0.7) / 0.85 - 0.15 x 0.1
    # = (0.36 + 0.20 + 0.14) / 0.85 - 0.015 = 0.70 / 0.85 - 0.015 = 0.8085
    card = _scorecard(odoo_env, "Tech Arif", "2026-09", 0.9, 0.8, 0.7, 0.1)
    assert card.score == 0.8085
    card.action_publish()
    assert _events(odoo_env, "scorecard.published", card.id) == [
        {"employee": "Tech Arif", "period": "2026-09", "score": 0.8085}
    ]


def test_incentive_run_computes_banded_lines_and_feeds_payroll(odoo_env):
    top = _scorecard(odoo_env, "Tech Arif", "2026-09", 1, 1, 1, 0)  # 1.00 -> 15% top band!
    mid = _scorecard(odoo_env, "Tech Bina", "2026-09", 0.8, 0.8, 0.8, 0.0)  # 0.80 -> 8% band
    low = _scorecard(odoo_env, "Tech Chan", "2026-09", 0.5, 0.5, 0.5, 0.5)  # 0.425 -> 0%
    _scorecard(odoo_env, "Other Month", "2026-08", 1, 1, 1, 0)
    run = odoo_env["fix.incentive.run"].create({"period": "2026-09", "band_base": 20000.0})
    with pytest.raises(UserError, match="Compute before applying"), odoo_env.cr.savepoint():
        run.action_apply()
    run.action_compute()
    assert run.state == "computed"
    amounts = {line.scorecard_id: line.amount for line in run.line_ids}
    # 20,000 x 15% = 3,000; x 8% = 1,600; x 0% = 0
    assert amounts == {top: 3000.00, mid: 1600.00, low: 0.00}
    assert run.total == 4600.00
    with pytest.raises(UserError, match="Compute runs from draft only"), odoo_env.cr.savepoint():
        run.action_compute()

    run.action_apply()
    assert run.state == "applied"
    granted = {
        line.employee_id.name: _events(odoo_env, "incentive.granted", line.id)
        for line in run.line_ids
    }
    assert granted["Tech Arif"] == [
        {"employee": "Tech Arif", "period": "2026-09", "amount": 3000.0}
    ]
    assert granted["Tech Bina"] == [
        {"employee": "Tech Bina", "period": "2026-09", "amount": 1600.0}
    ]
    assert granted["Tech Chan"] == [{"employee": "Tech Chan", "period": "2026-09", "amount": 0.0}]


def test_scorecard_salvage_and_30d_rework_clawback(odoo_env):
    """RAP-M57-02: salvage at target adds +0.15; 6% 30-day rework rate applies -0.30 penalty."""
    emp = odoo_env["hr.employee"].create({"name": "Tech Salvage"})
    card = odoo_env["fix.performance.scorecard"].create(
        {
            "employee_id": emp.id,
            "period": "2026-10",
            "first_time_fix": 1.0,
            "sla_hit": 1.0,
            "csat": 1.0,
            "rework_rate": 0.0,
            "salvage_value": 50000.0,
            "salvage_target": 50000.0,
            "rework_30d_rate": 0.06,
        }
    )
    assert card.salvage_ratio == 1.0
    assert card.rework_penalty_applied == 0.30
    assert card.score == 0.70


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
