# cd_requisition tests — M16 W3 (P06-M07).
#
# A06 audit (2026-11-03): this file asserted source text (inspect.getsource)
# and the single 25,000 constant that was the defect (one hard-coded band,
# passable only by the IT administrator). It now checks behaviour: the DoA
# ladder the routed approval uses, its configuration, and the acknowledgement
# state guard.
import pytest
from odoo.addons.cd_requisition.models.fix_requisition import (
    DEFAULT_LADDER,
    PARAM_TIER2,
    procurement_ladder,
)
from odoo.exceptions import UserError


def test_models_exist(odoo_env):
    for model in (
        "fix.requisition",
        "fix.purchase.order",
        "fix.purchase.order.line",
        "fix.purchase.receipt",
        "fix.purchase.receipt.line",
    ):
        assert model in odoo_env


def test_default_ladder_is_the_spec_matrix(odoo_env):
    """05-04 §7: <=50k / <=500k / <=2M / above, on DOFA tiers 2-5."""
    assert DEFAULT_LADDER[PARAM_TIER2] == 50000.0
    req = odoo_env["fix.requisition"].new({"estimate_amount": 0.0})
    cases = [
        (0.0, "tier_0"),
        (25000.0, "tier_2"),
        (50000.01, "tier_3"),
        (600000.0, "tier_4"),
        (3e6, "tier_5"),
    ]
    for amount, tier in cases:
        req.estimate_amount = amount
        assert req._dofa_current_tier() == tier, amount


def test_ladder_is_configuration(odoo_env):
    odoo_env["ir.config_parameter"].set_param(PARAM_TIER2, "10000")
    assert procurement_ladder(odoo_env)[1] == (10000.0, "tier_2")
    req = odoo_env["fix.requisition"].new({"estimate_amount": 20000.0})
    assert req._dofa_current_tier() == "tier_3"


def test_acknowledge_only_from_sent(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    po = env["fix.purchase.order"].create(
        {"operating_unit_id": ou.id, "vendor_id": env["res.partner"].create({"name": "Ack V"}).id}
    )
    with pytest.raises(UserError, match="Only a sent PO can be acknowledged"):
        po.action_acknowledge_on_behalf(evidence="vendor e-mail reference 1")
