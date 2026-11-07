"""cd_import_order ops behaviour (live ORM, rolled back): LC/LCA guards, the
HS tariff master, the FR-ITC-033 duty cascade, the BOE assessment gate,
arrivals/demurrage and the landed-cost sheet.

A06 audit (2026-11-03) M44-3: this file used to assert the WRONG cascade
(SD and AT on the assessable value only: SD 100, VAT 175.50, AT 50 on an AV of
1,000). test_duty_cascade_amounts now asserts the module spec FR-ITC-033:
SD on AV + CD + RD, VAT on AV + CD + RD + SD, AT on AV + CD + SD. The rates
are test inputs, not a claim about any NBR heading. Role and approval
controls are in test_a06_m44_controls.py.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    today = fields.Date.context_today(env["fix.import.order"])
    env["ir.config_parameter"].sudo().set_param("cd_import_order.landing_charge_pct", "0")
    supplier = env["res.partner"].create({"name": f"Import Supplier {TAG}", "is_company": True})
    product = env["product.product"].create({"name": f"Import Product {TAG}"})
    part = env["fix.spare.part"].create(
        {"name": f"Import Part {TAG}", "part_number": f"IMP-{TAG}", "product_id": product.id}
    )
    tariff = env["fix.import.tariff"].create(
        {
            "hs_code": "8471.30.00",
            "sro_ref": f"TEST-{TAG}",
            "date_from": today - timedelta(days=10),
            "cd_pct": 5,
            "rd_pct": 2,
            "sd_pct": 10,
            "vat_pct": 15,
            "at_pct": 5,
        }
    )
    tariff.action_activate()
    hs = env["fix.import.hs"].create(
        {"product_id": product.id, "hs_code": "8471.30.00", "ruling_ref": f"R-{TAG}"}
    )
    # BDT order: CIF of the single line is exactly 1,000 BDT
    order = env["fix.import.order"].create(
        {
            "name": f"IMP-{TAG}",
            "supplier_id": supplier.id,
            "currency_id": env.ref("base.BDT").id,
            "fx_rate": 1.0,
            "fob_value": 1000.0,
            "line_ids": [
                (0, 0, {"part_id": part.id, "hs_id": hs.id, "quantity": 1, "unit_price": 1000})
            ],
        }
    )
    # BRU-ITC-13: FOB, so the importer insures the consignment value
    cover = env["fix.import.insurance"].create(
        {
            "order_id": order.id,
            "insurer_id": env["res.partner"].create({"name": f"Insurer {TAG}"}).id,
            "policy_no": f"MC-{TAG}",
            "currency_id": env.ref("base.BDT").id,
            "sum_insured": 1000.0,
            "premium": 0.0,
            "cover_from": today - timedelta(days=1),
            "cover_to": today + timedelta(days=60),
        }
    )
    cover.action_verify()
    # BRU-ITC-03: the B/L and the Bill of Entry need a valid IRC
    env["fix.import.irc"].create({"irc_no": f"IRC-{TAG}", "valid_to": today + timedelta(days=100)})
    # scorecard 24: the B/L ships against an approved advance
    advance = env["fix.import.advance"].create(
        {
            "order_id": order.id,
            "currency_id": env.ref("base.BDT").id,
            "amount": 100.0,
            "bank": "Test AD Bank",
            "guarantee_ref": f"APG-{TAG}",
        }
    )
    advance.action_request()
    advance.action_approve("Test instrument")
    # BRU-ITC-12: a licensed C&F agent, active in M42
    agent = env["fix.import.cnf.agent"].create(
        {
            "name": f"Agent {TAG}",
            "supplier_id": env["fix.supplier"]
            .create(
                {
                    "name": f"Agent supplier {TAG}",
                    "partner_id": env["res.partner"].create({"name": f"Agent {TAG}"}).id,
                    "status": "active",
                }
            )
            .id,
            "licence_no": f"CNF-{TAG}",
            "licence_expiry": today + timedelta(days=100),
        }
    )
    agent.action_approve()
    return {
        "env": env,
        "today": today,
        "supplier": supplier,
        "order": order,
        "product": product,
        "part": part,
        "hs": hs,
        "tariff": tariff,
        "agent": agent,
    }


def test_lc_flow_and_guards(ctx):
    env, order = ctx["env"], ctx["order"]
    lc = env["fix.import.lc"].create(
        {
            "order_id": order.id,
            "lc_no": f"LC-{TAG}",
            "amount": 1000,
            "expiry": ctx["today"] + timedelta(days=30),
        }
    )
    assert lc.name.startswith("ILC/")
    assert lc.display_name == f"LC-{TAG}"
    with pytest.raises(UserError, match="applied"), env.cr.savepoint():
        lc.action_open()
    # no approved proforma on the order yet
    with pytest.raises(UserError, match="proforma"), env.cr.savepoint():
        lc.action_apply()
    with pytest.raises(IntegrityError), env.cr.savepoint():
        lc.write({"margin_pct": 150})
        env.flush_all()


def test_lca_approval(ctx):
    env, order = ctx["env"], ctx["order"]
    lc = env["fix.import.lc"].create({"order_id": order.id, "lc_no": f"LC2-{TAG}", "amount": 1000})
    lca = env["fix.import.lca"].create({"lc_id": lc.id, "lca_no": f"LCA-{TAG}", "amount": 1000})
    assert lca.display_name == f"LCA-{TAG}"
    lca.action_approve()
    assert lca.state == "approved"
    short = env["fix.import.lca"].create({"lc_id": lc.id, "lca_no": f"LCA2-{TAG}", "amount": 1})
    with pytest.raises(UserError, match="cover the LC"), env.cr.savepoint():
        short.action_approve()


def test_hs_ruling_and_unique_product(ctx):
    env, product, hs = ctx["env"], ctx["product"], ctx["hs"]
    hs.action_rule()
    assert hs.state == "ruled"
    assert hs.display_name == hs.hs_code
    assert hs.cd_pct == 5 and hs.tariff_id == ctx["tariff"]
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.import.hs"].create({"product_id": product.id, "hs_code": "0000.00.00"})
        env.flush_all()
    with pytest.raises(ValidationError, match="tariff heading"), env.cr.savepoint():
        env["fix.import.hs"].create(
            {"product_id": env["product.product"].create({"name": "x"}).id, "hs_code": "ABC"}
        )


def test_duty_cascade_amounts(ctx):
    env, order = ctx["env"], ctx["order"]
    ctx["hs"].action_rule()
    boe = env["fix.import.boe"].create(
        {
            "order_id": order.id,
            "boe_no": f"BE-{TAG}",
            "cnf_agent_id": ctx["agent"].id,
            "line_ids": [(0, 0, {"order_line_id": order.line_ids.id, "quantity": 1})],
        }
    )
    line = boe.line_ids
    assert line.assessable_value == pytest.approx(1000.0)
    assert line.cd_amount == pytest.approx(50.0)
    assert line.rd_amount == pytest.approx(20.0)
    # SD on AV + CD + RD = 1070 x 10%
    assert line.sd_amount == pytest.approx(107.0)
    # VAT on AV + CD + RD + SD = 1177 x 15%
    assert line.vat_amount == pytest.approx(176.55)
    # AT on AV + CD + SD = 1157 x 5%
    assert line.at_amount == pytest.approx(57.85)
    assert boe.total_tax == pytest.approx(411.4)
    assert line.formula_version == "FR-ITC-033/v1"
    for doc_type in ("bl", "invoice", "packing"):
        env["fix.import.shipdoc"].create(
            {"order_id": order.id, "doc_type": doc_type, "ref": f"{doc_type}-{TAG}"}
        ).action_receive()
    boe.action_assess()
    assert boe.state == "assessed"
    # the rates are frozen on the line at assessment
    assert (line.cd_rate, line.sd_rate, line.at_rate) == (5, 10, 5)


def test_boe_assess_requires_documents_and_order_lines(ctx):
    env, order = ctx["env"], ctx["order"]
    boe = env["fix.import.boe"].create(
        {
            "order_id": order.id,
            "boe_no": f"BE0-{TAG}",
            "cnf_agent_id": ctx["agent"].id,
            "line_ids": [(0, 0, {"description": "no order line", "assessable_value": 500})],
        }
    )
    with pytest.raises(UserError, match="checklist"), env.cr.savepoint():
        boe.action_assess()
    for doc_type in ("bl", "invoice", "packing"):
        env["fix.import.shipdoc"].create(
            {"order_id": order.id, "doc_type": doc_type, "ref": f"{doc_type}-{TAG}"}
        ).action_receive()
    with pytest.raises(UserError, match="line of import order"), env.cr.savepoint():
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
            "cnf_agent_id": ctx["agent"].id,
        }
    )
    with pytest.raises(UserError, match="bill of lading"), env.cr.savepoint():
        arrival.action_arrive()
    env["fix.import.shipdoc"].create(
        {"order_id": order.id, "doc_type": "bl", "ref": f"BL-{TAG}"}
    ).action_receive()
    arrival.action_arrive(arrival_date=ctx["today"] - timedelta(days=8))
    assert arrival.state == "arrived" and order.state == "customs"
    # 8 days at port, 5 free -> 3 days of demurrage, computed, not typed
    assert arrival.demurrage_days == 3
    arrival.write({"release_ref": f"RO-{TAG}"})
    # BRU-ITC-17: past the free time it needs a cause, and still a paid Bill of Entry
    with pytest.raises(UserError, match="demurrage cause"), env.cr.savepoint():
        arrival.action_clear()
    arrival.write({"demurrage_cause": "customs"})
    with pytest.raises(UserError, match="Bill of Entry"), env.cr.savepoint():
        arrival.action_clear()


def test_landed_cost_total_and_finalise(ctx):
    env, order = ctx["env"], ctx["order"]
    landed = env["fix.import.landed"].create(
        {
            "order_id": order.id,
            "freight": 1000,
            "insurance": 200,
            "clearing_charges": 400,
        }
    )
    assert landed.name.startswith("ILND/")
    # final sheet: duty comes from the paid Bills of Entry (none yet)
    assert landed.duty == 0.0
    assert landed.total_landed == pytest.approx(1600.0)
    with pytest.raises(UserError, match="receive the consignment"), env.cr.savepoint():
        landed.action_finalise()
    assert landed.state == "draft"
