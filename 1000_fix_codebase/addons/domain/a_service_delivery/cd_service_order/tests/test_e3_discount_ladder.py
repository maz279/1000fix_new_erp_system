"""D3-03 (owner decision 12 Nov 2026, E3-02): ONE discount ladder.

The estimate's DOFA discount bands were its own 5/15/30/50 while the M11
discount approval read the pricing ladder (BRU-PRC-06, 10/20/35): an 8%
discount was Tier 2 on the estimate and the agent's own authority on the
approval. The estimate now READS the M11 ladder
(fix.discount.policy.discount_ladder(), cd_rate_card) - the released bands of
the company, the spec default while none is released - instead of keeping
numbers of its own."""

from __future__ import annotations

import pytest
from odoo.addons.cd_service_order.tests.test_service_order_models import (  # noqa: F401
    _estimate,
    base,
)


@pytest.fixture
def ladder(base):  # noqa: F811
    """The spec ladder in force: every released band retired (rolled back)."""
    Policy = base.env["fix.discount.policy"]
    Policy.sudo().search([("state", "=", "active")])._guarded().write({"state": "retired"})
    return Policy


def _discounted(base, pct):  # noqa: F811
    # parts 2 x 1500 + labour 500 = 3,500.00 chargeable
    return _estimate(base, discount=round(3500.0 * pct / 100.0, 2))


def test_the_estimate_reads_the_m11_ladder(base, ladder):  # noqa: F811
    est = _discounted(base, 8.0)
    assert est._dofa_thresholds() == ladder.discount_ladder(est.company_id)


@pytest.mark.parametrize(
    "pct, tier",
    [
        (4.0, "tier_0"),
        (8.0, "tier_0"),  # E3-02: Tier 2 on the old estimate bands
        (10.0, "tier_0"),
        (12.0, "tier_2"),
        (20.0, "tier_2"),
        (25.0, "tier_3"),
        (35.0, "tier_3"),
        (40.0, "tier_4"),
        (60.0, "tier_4"),  # the CCO is the ceiling of BRU-PRC-06 (no Tier 5 band)
    ],
)
def test_estimate_and_discount_approval_agree(base, ladder, pct, tier):  # noqa: F811
    est = _discounted(base, pct)
    assert est._dofa_current_tier() == tier
    assert est.dofa_tier_required == tier
    assert ladder.tier_for_discount(est.discount_pct, company=est.company_id) == tier


def test_a_released_band_moves_the_estimate_with_it(base, ladder):  # noqa: F811
    band = ladder.sudo().create(
        {"name": "agent 5", "min_pct": 0.0, "max_pct": 5.0, "requires_approval": False}
    )
    band._guarded().write({"state": "active"})
    est = _discounted(base, 8.0)
    # above every released band: the CCO, on the estimate as on the approval
    assert ladder.tier_for_discount(8.0, company=est.company_id) == "tier_4"
    assert est._dofa_current_tier() == "tier_4"


def test_the_estimate_keeps_no_bands_of_its_own(base):  # noqa: F811
    assert not hasattr(type(base.env["fix.estimate"]), "_DOFA_DISCOUNT_THRESHOLDS")
