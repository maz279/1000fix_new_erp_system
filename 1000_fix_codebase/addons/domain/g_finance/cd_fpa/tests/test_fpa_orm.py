# cd_fpa — live-ORM behaviour of M54 budgets and cost allocations.
from __future__ import annotations

from decimal import Decimal

import pytest

pytestmark = [pytest.mark.financial]

D = Decimal


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def test_budget_variance_follows_actuals(odoo_env):
    budget = odoo_env["fix.budget"].create(
        {"name": "FY2027 Dhaka workshop", "fiscal_year": "FY2027", "planned_amount": 500000.0}
    )
    assert budget.currency_id == odoo_env.ref("base.BDT")
    assert _money(budget.variance) == D("500000.00")
    budget.actual_amount = 512345.67
    assert _money(budget.variance) == D("-12345.67")  # overspend is negative


def test_cost_allocation_total(odoo_env):
    alloc = odoo_env["fix.cost.allocation"].create(
        {"name": "Job JOB-8849", "direct_cost": 1999.99, "allocated_overhead": 250.01}
    )
    assert _money(alloc.total_cost) == D("2250.00")
    alloc.allocated_overhead = 0.0
    assert _money(alloc.total_cost) == D("1999.99")
