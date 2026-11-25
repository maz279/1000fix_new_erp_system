"""cd_demand_plan tests - P09-M07 (CD-M43-01): the planning formulas.

Rewritten in the A06 remediation: the previous file asserted source text
(inspect.getsource) instead of behaviour. These exercise the formulas the
models compute with."""

from datetime import date

import pytest
from odoo.addons.cd_demand_plan.models import fix_demand_common as c
from odoo.exceptions import UserError


@pytest.mark.parametrize(
    ("projected", "rop", "target", "expected"),
    [
        (-5.0, 20.0, 80.0, 85.0),  # finding E03: below ROP -> up to target
        (-100.0, 50.0, 200.0, 300.0),  # finding E04: covers demand AND restores target
        (20.0, 20.0, 80.0, 60.0),  # at the ROP orders
        (20.01, 20.0, 80.0, 0.0),  # above the ROP does not
        (90.0, 20.0, 80.0, 0.0),  # above target never orders
        (5.0, 20.0, 3.0, 0.0),  # a target below the position never goes negative
    ],
)
def test_order_up_to(projected, rop, target, expected):
    assert c.order_up_to(projected, rop, target) == pytest.approx(expected)


def test_safety_stock_formula():
    # A06 ERP M43-08: z is the inverse normal of the level
    assert c.safety_stock("95", 2, 9) == pytest.approx(round(1.644854 * 2 * 3, 2))
    assert c.safety_stock("99", 2.2, 13) == pytest.approx(round(2.326348 * 2.2 * 13**0.5, 2))
    assert c.safety_stock("95", 2, 0) == 0.0


def test_periods():
    assert c.month_start("2026-11") == date(2026, 11, 1)
    assert c.add_months(date(2026, 11, 1), 3) == date(2027, 2, 1)
    assert c.add_months(date(2026, 1, 1), -1) == date(2025, 12, 1)
    assert c.month_end(date(2028, 2, 1)) == date(2028, 2, 29)
    assert c.months_between(date(2026, 11, 15), date(2027, 1, 2)) == [
        "2026-11",
        "2026-12",
        "2027-01",
    ]
    assert c.months_between(date(2026, 11, 15), date(2026, 11, 1)) == []
    with pytest.raises(UserError):
        c.month_start("banana")


def test_mean_and_stddev():
    assert c.mean_and_stddev([]) == (0.0, 0.0)
    mean, std = c.mean_and_stddev([2, 0, 2, 0])
    assert mean == pytest.approx(1.0)
    assert std == pytest.approx((4 / 3) ** 0.5)
