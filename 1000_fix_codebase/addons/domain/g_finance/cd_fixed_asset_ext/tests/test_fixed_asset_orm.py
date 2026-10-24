# cd_fixed_asset_ext — live-ORM behaviour of M49 assets and CWIP.
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]

D = Decimal


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _asset(env, **vals):
    base = {
        "name": "Diagnostic bench DHK-01",
        "category": "workshop_equipment",
        "gross": 120000.0,
        "salvage": 20000.0,
        "life_months": 50,
        "purchase_date": date(2026, 7, 1),
    }
    base.update(vals)
    return env["fix.fixed.asset"].create(base)


class TestFixedAsset:
    def test_straight_line_depreciation_and_capitalisation_event(self, odoo_env):
        asset = _asset(odoo_env)
        assert _money(asset.monthly_depreciation) == D("2000.00")  # (120,000 - 20,000) / 50
        assert asset.state == "draft"
        assert _events(odoo_env, "asset.capitalized", asset.id) == [
            {"name": "Diagnostic bench DHK-01", "gross": 120000.0}
        ]

    def test_rounding_and_recompute(self, odoo_env):
        asset = _asset(odoo_env, gross=1000.0, salvage=0.0, life_months=3)
        assert _money(asset.monthly_depreciation) == D("333.33")  # 333.333... half-up
        asset.life_months = 0
        assert asset.monthly_depreciation == 0.0

    def test_invalid_depreciation_inputs_are_validation_errors(self, odoo_env):
        # the stored compute runs when the savepoint flushes; the failed
        # computation is discarded with the savepoint (as a request would)
        with pytest.raises(ValidationError, match="salvage above gross"), odoo_env.cr.savepoint():
            _asset(odoo_env, gross=100.0, salvage=200.0)

    def test_monthly_accrual_only_for_active_assets(self, odoo_env):
        asset = _asset(odoo_env)
        with pytest.raises(UserError, match="Only ACTIVE assets accrue"), odoo_env.cr.savepoint():
            asset.action_accrue_month()
        asset.state = "active"
        asset.action_accrue_month()
        assert _events(odoo_env, "depreciation.accrued", asset.id) == [
            {"asset": "Diagnostic bench DHK-01", "amount": 2000.0}
        ]

    def test_disposal(self, odoo_env):
        asset = _asset(odoo_env, state="active")
        asset.action_dispose()
        assert asset.state == "disposed"
        assert _events(odoo_env, "asset.disposed", asset.id) == [
            {"name": "Diagnostic bench DHK-01"}
        ]


class TestCwip:
    def _cwip(self, env, name, amount, company=None, ou=None):
        vals = {"name": name, "amount": amount}
        if company:
            vals["company_id"] = company.id
        if ou:
            vals["operating_unit_id"] = ou.id
        return env["fix.cwip.entry"].create(vals)

    def test_capitalise_every_entry(self, odoo_env):
        """Regression: `return asset` inside the loop capitalised only the
        first entry of a multi-record call and left the rest open."""
        ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
        a = self._cwip(odoo_env, "Server room fit-out", 450000.0, ou=ou)
        b = self._cwip(odoo_env, "Van racking", 60000.0)
        assets = (a | b).action_capitalise("infrastructure", 60, salvage=6000.0)
        assert len(assets) == 2
        assert (a.state, b.state) == ("capitalised", "capitalised")
        assert (a.asset_id | b.asset_id) == assets
        fit_out = a.asset_id
        assert (fit_out.state, fit_out.category, fit_out.operating_unit_id) == (
            "active",
            "infrastructure",
            ou,
        )
        assert _money(fit_out.gross) == D("450000.00")
        assert _money(fit_out.monthly_depreciation) == D("7400.00")  # (450,000 - 6,000) / 60
        assert fit_out.purchase_date == date.today()
        assert _events(odoo_env, "cwip.capitalised", a.id) == [
            {"asset": "Server room fit-out", "amount": 450000.0}
        ]

    def test_asset_belongs_to_the_entries_company(self, odoo_env):
        """Regression: the asset was created under the user's current company
        instead of the CWIP entry's company."""
        other = odoo_env["res.company"].create({"name": "1000FiX Khulna Ltd"})
        entry = self._cwip(odoo_env, "Khulna workshop", 90000.0, company=other)
        asset = entry.action_capitalise("workshop_equipment", 36)
        assert asset.company_id == other

    def test_refusals(self, odoo_env):
        empty = self._cwip(odoo_env, "Nothing yet", 0.0)
        with pytest.raises(UserError, match="Nothing accumulated"), odoo_env.cr.savepoint():
            empty.action_capitalise("x", 12)
        done = self._cwip(odoo_env, "Done", 10.0)
        done.action_capitalise("x", 12)
        with pytest.raises(UserError, match="already capitalised"), odoo_env.cr.savepoint():
            done.action_capitalise("x", 12)
