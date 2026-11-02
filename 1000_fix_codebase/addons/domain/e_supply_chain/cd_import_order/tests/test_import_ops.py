"""cd_import_order ops behaviour (live ORM, rolled back): LC/LCA flow, HS rates,
the duty cascade, the BOE assessment guard, arrivals/demurrage and the landed
cost sheet."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    supplier = env["res.partner"].create({"name": f"Import Supplier {TAG}", "is_company": True})
    order = env["fix.import.order"].create(
        {"name": f"IMP-{TAG}", "supplier_id": supplier.id, "fob_value": 100000, "state": "draft"}
    )
    product = env["product.product"].create({"name": f"Import Product {TAG}"})
    hs = env["fix.import.hs"].create(
        {
            "product_id": product.id,
            "hs_code": f"8471.{TAG[:4]}",
            "cd_pct": 5,
            "rd_pct": 2,
            "sd_pct": 10,
            "vat_pct": 15,
            "at_pct": 5,
        }
    )
    return {"env": env, "supplier": supplier, "order": order, "product": product, "hs": hs}


def test_lc_flow_and_guards(ctx):
    env, order = ctx["env"], ctx["order"]
    lc = env["fix.import.lc"].create({"order_id": order.id, "lc_no": f"LC-{TAG}", "amount": 50000})
    assert lc.name.startswith("ILC/")
    assert lc.display_name == f"LC-{TAG}"
    with pytest.raises(UserError, match="applied"), env.cr.savepoint():
        lc.action_open()
    lc.action_apply()
    lc.action_open()
    assert lc.state == "opened"
    lc.action_close()
    assert lc.state == "closed"


def test_lca_approval(ctx):
    env, order = ctx["env"], ctx["order"]
    lc = env["fix.import.lc"].create({"order_id": order.id, "lc_no": f"LC2-{TAG}"})
    lca = env["fix.import.lca"].create({"lc_id": lc.id, "lca_no": f"LCA-{TAG}"})
    assert lca.display_name == f"LCA-{TAG}"
    lca.action_approve()
    assert lca.state == "approved"


def test_hs_ruling_and_unique_product(ctx):
    env, product = ctx["env"], ctx["product"]
    hs = env["fix.import.hs"].browse(ctx["hs"].id)
    hs.action_rule()
    assert hs.state == "ruled"
    assert hs.display_name == hs.hs_code
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.import.hs"].create({"product_id": product.id, "hs_code": "0000.00.00"})


def test_duty_cascade_amounts(ctx):
    env, order, hs = ctx["env"], ctx["order"], ctx["hs"]
    boe = env["fix.import.boe"].create(
        {
            "order_id": order.id,
            "boe_no": f"BE-{TAG}",
            "state": "draft",
            "line_ids": [(0, 0, {"hs_id": hs.id, "assessable_value": 1000})],
        }
    )
    line = boe.line_ids
    assert line.cd_amount == pytest.approx(50.0)
    assert line.rd_amount == pytest.approx(20.0)
    assert line.sd_amount == pytest.approx(100.0)
    # VAT on value + CD + RD + SD = 1170 × 15%
    assert line.vat_amount == pytest.approx(175.5)
    assert line.at_amount == pytest.approx(50.0)
    assert boe.total_tax == pytest.approx(395.5)
    boe.action_assess()
    assert boe.state == "assessed"
    boe.action_pay()
    assert boe.state == "paid"


def test_boe_assess_requires_hs_and_value(ctx):
    env, order = ctx["env"], ctx["order"]
    boe = env["fix.import.boe"].create(
        {
            "order_id": order.id,
            "boe_no": f"BE0-{TAG}",
            "line_ids": [(0, 0, {"description": "no HS", "assessable_value": 500})],
        }
    )
    with pytest.raises(UserError, match="HS classification"), env.cr.savepoint():
        boe.action_assess()


def test_arrival_demurrage_and_clearance(ctx):
    env, order = ctx["env"], ctx["order"]
    arrival = env["fix.import.arrival"].create(
        {
            "order_id": order.id,
            "vessel": f"MV {TAG}",
            "etd": date(2026, 10, 1),
            "eta": date(2026, 10, 10),
            "free_days": 5,
        }
    )
    arrival.action_arrive()
    assert arrival.state == "arrived"
    arrival.action_clear()
    assert arrival.state == "cleared"
    assert arrival.cleared_on


def test_landed_cost_total_and_finalise(ctx):
    env, order = ctx["env"], ctx["order"]
    landed = env["fix.import.landed"].create(
        {
            "order_id": order.id,
            "freight": 1000,
            "insurance": 200,
            "duty": 300,
            "clearing_charges": 400,
            "other_charges": 100,
        }
    )
    assert landed.name.startswith("ILND/")
    assert landed.total_landed == pytest.approx(2000.0)
    landed.action_finalise()
    assert landed.state == "finalised"
    with pytest.raises(UserError, match="draft"), env.cr.savepoint():
        landed.action_finalise()
