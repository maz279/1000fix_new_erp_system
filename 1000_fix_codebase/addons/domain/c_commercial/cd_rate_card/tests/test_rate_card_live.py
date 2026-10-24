# cd_rate_card live-ORM tests — M11 rate-card data core (P06-M06).
import sys
import uuid
from datetime import date
from decimal import Decimal

import pytest
from odoo.addons.cd_rate_card.models import fix_rate_card
from odoo.exceptions import UserError

# per-run product codes: the unique key never collides with a concurrent run
SRV = f"SRV-AC-{uuid.uuid4().hex[:6].upper()}"
PART = f"PART-{uuid.uuid4().hex[:6].upper()}"


def _card(env, **overrides):
    vals = {"product_code": SRV, "unit_price": 450.0, "min_tier": 3}
    vals.update(overrides)
    return env["fix.rate.card"].create(vals)


def test_tier_card_name_and_defaults(odoo_env):
    card = _card(odoo_env)
    assert card.name == f"{SRV} @ tier 3"
    assert (card.line_type, card.active) == ("labour", True)
    assert card.currency_id == odoo_env.ref("base.BDT")


def test_contract_card_name(odoo_env):
    card = _card(odoo_env, min_tier=99, contract_no="AMC-2026-0001")
    assert card.name == f"{SRV} @ contract AMC-2026-0001"


def test_name_follows_the_tier(odoo_env):
    card = _card(odoo_env, min_tier=1)
    card.min_tier = 5
    assert card.name == f"{SRV} @ tier 5"


def test_tier_99_requires_a_contract_number(odoo_env):
    with pytest.raises(UserError, match="tier-99 rate is a CONTRACT rate"), odoo_env.cr.savepoint():
        _card(odoo_env, min_tier=99)


def test_contract_number_requires_tier_99(odoo_env):
    with (
        pytest.raises(UserError, match="Contract rates carry min_tier 99"),
        odoo_env.cr.savepoint(),
    ):
        _card(odoo_env, min_tier=3, contract_no="AMC-1")


@pytest.mark.parametrize("price", [0.0, -1.0])
def test_rate_must_be_positive(odoo_env, price):
    with pytest.raises(UserError, match="A rate must be positive"), odoo_env.cr.savepoint():
        _card(odoo_env, unit_price=price)


def test_inverted_validity_window_is_refused(odoo_env):
    with pytest.raises(UserError, match="Validity window is inverted"), odoo_env.cr.savepoint():
        _card(odoo_env, valid_from=date(2026, 6, 1), valid_to=date(2026, 5, 31))


def test_valid_and_open_ended_windows_are_accepted(odoo_env):
    bounded = _card(odoo_env, valid_from=date(2026, 1, 1), valid_to=date(2026, 1, 1))
    open_ended = _card(odoo_env, product_code=PART, valid_from=date(2026, 1, 1))
    assert bounded.valid_to == date(2026, 1, 1)
    assert open_ended.valid_to is False


def test_one_tier_rate_per_product(odoo_env):
    """Regression: tier cards carry no contract_no, and a plain UNIQUE never
    sees two NULLs as equal - duplicate tier rates were accepted."""
    _card(odoo_env)
    with pytest.raises(Exception, match="product_tier_unique"), odoo_env.cr.savepoint():
        _card(odoo_env, unit_price=500.0)


def test_one_contract_rate_per_product_and_contract(odoo_env):
    _card(odoo_env, min_tier=99, contract_no="AMC-1")
    other_contract = _card(odoo_env, min_tier=99, contract_no="AMC-2")
    assert other_contract.contract_no == "AMC-2"
    with pytest.raises(Exception, match="product_tier_unique"), odoo_env.cr.savepoint():
        _card(odoo_env, min_tier=99, contract_no="AMC-1", unit_price=380.0)


def test_projects_to_the_pricing_engine_line(odoo_env, monkeypatch):
    """Regression: `from services.pricing_engine import ...` could never
    resolve (the service folder is `pricing-engine`) - the projection always
    raised ModuleNotFoundError."""
    src = str(fix_rate_card.PRICING_ENGINE_SRC)
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != src])
    card = _card(odoo_env, line_type="part", unit_price=2000.0, min_tier=1)
    line = card.to_engine_line()
    assert sys.path[0] == src  # the engine's src/ was put on the path once
    engine = sys.modules["pricing_engine"]
    assert line == engine.RateCardLine(
        product_code=SRV, line_type="part", unit_price=Decimal("2000.0"), min_tier=1
    )
    # a second projection reuses the path entry (no duplicate)
    contract = _card(odoo_env, min_tier=99, contract_no="AMC-9", unit_price=400.0)
    assert contract.to_engine_line().min_tier == 99
    assert sys.path.count(src) == 1


def test_engine_prices_from_projected_cards(odoo_env):
    """End-to-end seam: the projected lines are what the L5 engine resolves."""
    cards = _card(odoo_env, min_tier=1, unit_price=500.0) | _card(
        odoo_env, min_tier=3, unit_price=450.0
    )
    lines = [card.to_engine_line() for card in cards]
    engine = sys.modules["pricing_engine"]
    request = engine.PriceRequest(
        customer_tier=3,
        lines=(engine.PriceRequestLine(SRV, Decimal("2"), "labour"),),
    )
    result = engine.price(request, lines, {})
    # tier 3 customer: the tier-3 card (450.00) wins over tier 1 -> 2 x 450
    assert result.lines[0].unit_price == Decimal("450.00")
    assert result.lines[0].gross == Decimal("900.00")
