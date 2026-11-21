# cd_fixed_asset_ext — A05 ERP audit, stream S4 (M49 side), live ORM:
#
#   M13-14  a retired rental unit's disposal is a transfer to resale stock
#           (carrying amount to the refurbished-stock account, no gain/loss)
#           or a recycling — not always a write-off;
#   M18-14  the e-waste hand-off of a disposal carries the device, its weight
#           and material (it opened a 0 kg 'other' collection);
#   FIN-15  a public API capitalises a source's unit (register + catch-up
#           depreciation) and reads its M49 book value.
from __future__ import annotations

from datetime import date

import pytest
from dateutil.relativedelta import relativedelta
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import PARAM_RESALE_STOCK
from odoo.addons.cd_fixed_asset_ext.tests.test_a08_m49_controls import (
    _approve,
    balance,
    c,  # noqa: F401 - the fixture
    seam_asset,
)
from odoo.addons.cd_fixed_asset_ext.tests.test_a08_m49_operability import relay
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]


def _stock_account(c):  # noqa: F811
    acc = c.cenv["account.account"].create(
        {
            "code": "A5S4STK%s" % c.co.id,
            "name": "Stock of Inventory - Refurbished (test)",
            "account_type": "asset_current",
            "company_ids": [(6, 0, c.co.ids)],
        }
    )
    c.env["ir.config_parameter"].sudo().set_param(PARAM_RESALE_STOCK, acc.code)
    return acc


def _tier_user(c, record):  # noqa: F811
    by_tier = {"tier_2": c.t2, "tier_3": c.t3, "tier_4": c.t4, "tier_5": c.t5}
    return by_tier[record.dofa_tier_required]


def _post_disposal(c, disposal):  # noqa: F811
    disposal.with_user(c.acc1).action_submit()
    if disposal.state == "submitted":
        _approve(disposal, _tier_user(c, disposal))
    disposal.with_user(c.acc2).action_post()
    return disposal


def _depreciated_asset(c, gross=120000.0):  # noqa: F811
    asset = seam_asset(c, gross=gross, life=12)
    asset._fix_catch_up_depreciation()
    assert asset.accumulated_depreciation > 0
    return asset


# ------------------------------------------------------------------ M13-14
def test_m13_14_transfer_to_resale_moves_the_carrying_amount_to_stock(c):  # noqa: F811
    stock = _stock_account(c)
    asset = _depreciated_asset(c)
    nbv, accumulated = asset.book_nbv, asset.accumulated_depreciation
    disposal = asset._fix_open_disposal("transfer_resale", "Retired from rental: resale route")
    assert disposal.kind == "transfer_resale" and not disposal.ewaste_route
    _post_disposal(c, disposal)
    assert disposal.state == "posted" and disposal.gain_loss == 0.0
    assert balance(c, stock) == nbv
    assert balance(c, c.a["accum"]) == 0.0 and balance(c, c.a["asset"]) == 0.0
    assert balance(c, c.a["loss"]) == 0.0 and balance(c, c.a["gain"]) == 0.0
    assert accumulated + nbv == 120000.0
    assert asset.state == "disposed" and asset._fix_book_value() == 0.0


def test_m13_14_transfer_to_resale_fails_closed_without_the_stock_account(c):  # noqa: F811
    c.env["ir.config_parameter"].sudo().set_param(PARAM_RESALE_STOCK, "")
    asset = seam_asset(c)
    disposal = asset._fix_open_disposal("transfer_resale", "resale route")
    disposal.with_user(c.acc1).action_submit()
    if disposal.state == "submitted":
        _approve(disposal, _tier_user(c, disposal))
    with pytest.raises(UserError, match="resale_inventory"), c.env.cr.savepoint():
        disposal.with_user(c.acc2).action_post()


def test_m13_14_recycle_is_a_loss_and_no_proceeds_on_either_route(c):  # noqa: F811
    asset = _depreciated_asset(c)
    nbv = asset.book_nbv
    disposal = asset._fix_open_disposal("recycle", "Retired: recycle route", source=c.co)
    # a source (the rental retirement event) hands the item to M18 itself
    assert not disposal.ewaste_route
    assert (disposal.source_model, disposal.source_res_id) == ("res.company", c.co.id)
    with pytest.raises(ValidationError, match="no proceeds"), c.env.cr.savepoint():
        disposal.write({"proceeds": 10.0})
    _post_disposal(c, disposal)
    assert disposal.gain_loss == -nbv and balance(c, c.a["loss"]) == nbv


def test_m13_14_open_disposal_is_idempotent_and_refuses_another_route_in_approval(c):  # noqa: F811
    asset = seam_asset(c)
    first = asset._fix_open_disposal("transfer_resale", "resale")
    assert asset._fix_open_disposal("transfer_resale", "resale") == first
    first.with_user(c.acc1).action_submit()
    if first.state in ("submitted", "approved"):
        with pytest.raises(UserError, match="in approval"), c.env.cr.savepoint():
            asset._fix_open_disposal("recycle", "recycle")


# ------------------------------------------------------------------ M18-14
def test_m18_14_ewaste_route_needs_weight_and_material(c):  # noqa: F811
    asset = seam_asset(c)
    disposal = asset._fix_open_disposal("recycle", "standalone recycling")
    assert disposal.ewaste_route  # a standalone recycling goes to M18 from here
    with pytest.raises(UserError, match="weight"), c.env.cr.savepoint():
        disposal.with_user(c.acc1).action_submit()


def test_m18_14_collection_carries_device_weight_and_material(c):  # noqa: F811
    asset = seam_asset(c)
    device = None
    if "fix.device" in c.env:
        brand = c.env["fix.brand"].create({"name": "A05S4 brand", "code": "A5S4B"})
        model = c.env["fix.device.model"].create(
            {"brand_id": brand.id, "name": "A05S4-1", "device_type": "laptop"}
        )
        device = c.env["fix.device"].create({"device_model_id": model.id})
    disposal = asset._fix_open_disposal(
        "recycle",
        "standalone recycling",
        device_id=device.id if device else 0,
        weight_kg=2.4,
        material="laptop",
    )
    _post_disposal(c, disposal)
    relay(
        c,
        "asset.disposed",
        "fix.fixed.asset",
        asset.id,
        "cd_fixed_asset_ext.consumer_asset_disposed_m18",
    )
    collection = c.env["fix.ewaste.collection"].sudo().browse(disposal.ewaste_collection_res_id)
    assert collection.exists()
    assert (collection.weight_kg, collection.material_type) == (2.4, "laptop")
    if device:
        assert collection.device_id == device


# ------------------------------------------------------------------ FIN-15
def test_fin15_capitalise_from_source_registers_and_catches_up_depreciation(c):  # noqa: F811
    today = c.today
    purchase = (today - relativedelta(months=3)).replace(day=10)
    unit = c.env["res.partner"].create({"name": "A05S4 fleet unit"})
    asset = c.env["fix.fixed.asset"]._fix_capitalise_from_source(
        unit,
        c.cat_it,
        36000.0,
        purchase,
        credit_account=c.a["payable"],
        name="Fleet laptop A05S4",
        operating_unit=c.ou,
        salvage=0.0,
        life_months=36,
    )
    assert asset.state == "active" and asset.company_id == c.co
    assert (asset.source_model, asset.source_res_id) == ("res.partner", unit.id)
    # acquisition month .. last month: 3 months at 1,000 (this month is the
    # company's month run's)
    assert asset.book_months_done == 3
    assert asset.accumulated_depreciation == 3000.0
    assert asset._fix_book_value() == 33000.0
    assert balance(c, c.a["asset"]) == 36000.0 and balance(c, c.a["payable"]) == -36000.0
    assert balance(c, c.a["expense"]) == 3000.0
    # the book value as of the end of the acquisition month: one month charged
    end_first = purchase + relativedelta(day=31)
    assert asset._fix_book_value(as_of=end_first) == 35000.0
    # idempotent on the source
    again = c.env["fix.fixed.asset"]._fix_capitalise_from_source(
        unit, c.cat_it, 36000.0, purchase, credit_account=c.a["payable"]
    )
    assert again == asset and balance(c, c.a["asset"]) == 36000.0
    # the company's month run is still prepared (the scoped catch-up run of
    # this month is not the month run) and charges this month once
    other = seam_asset(c, gross=12000.0, purchase=date(today.year, today.month, 1), life=12)
    prepared = c.env["fix.asset.depreciation.run"]._cron_prepare_monthly_runs()
    book_runs = prepared.filtered(lambda r: r.company_id == c.co and r.book == "book")
    charged = book_runs.line_ids.mapped("asset_id")
    assert book_runs and other in charged and asset in charged


def test_fin15_capitalise_needs_a_credit_account_or_a_posted_cost(c):  # noqa: F811
    unit = c.env["res.partner"].create({"name": "A05S4 fleet unit 2"})
    with pytest.raises(UserError, match="credit_account"), c.env.cr.savepoint():
        c.env["fix.fixed.asset"]._fix_capitalise_from_source(unit, c.cat, 1000.0, c.today)
