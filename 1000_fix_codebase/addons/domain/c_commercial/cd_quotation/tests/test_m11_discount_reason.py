# M11 capture audit, pass 2 (18 Nov 2026): discount reason codes
# (FR-PRC-030, BRU-PRC-13). The Discount Governance page captured a discount
# request with free text only; the governed reason list and the rule that a
# discount above the threshold carries one are exercised here as non-admin
# users on the live ORM (`odoo_env`, rolled back).
import pytest
from odoo.addons.cd_quotation.models.fix_discount_reason import THRESHOLD_PARAM
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import _estimate, _user, c  # noqa: F401
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_rate_card.group_pricing_officer"


@pytest.fixture
def officer(odoo_env):
    if not odoo_env.ref(OFFICER, raise_if_not_found=False):
        pytest.skip("cd_rate_card (the Pricing Officer role) is not installed")
    return _user(odoo_env, "m11reason_officer", [OFFICER])


def _request(c, pct, **vals):  # noqa: F811
    return (
        c.env["fix.discount.approval"]
        .with_user(c.clerk)
        .create(
            dict(
                {
                    "quotation_id": _estimate(c).id,
                    "operating_unit_id": c.ou.id,
                    "discount_pct": pct,
                    "justification": "customer is moving to a competitor",
                },
                **vals,
            )
        )
    )


def _reason(env, user, code="LOYAL"):
    return (
        env["fix.discount.reason"]
        .with_user(user)
        .create({"code": code, "name": "Retention of a loyal customer"})
    )


def test_the_reason_list_is_governed(c, officer):  # noqa: F811
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        _reason(c.env, c.clerk)
    reason = _reason(c.env, officer, code=" comp-match ")
    assert reason.code == "COMP-MATCH"


def test_a_request_above_the_threshold_needs_a_reason_once_the_list_exists(c, officer):  # noqa: F811
    c.env["fix.discount.reason"].sudo().search([]).write({"active": False})
    pending = _request(c, 15.0)
    assert pending.state == "pending"
    # an empty list cannot hold a request hostage
    pending.with_user(c.clerk).action_request_approval()
    pending.with_user(c.clerk).action_recall_approval()

    reason = _reason(c.env, officer)
    with pytest.raises(UserError, match="needs a reason code"), c.env.cr.savepoint():
        pending.with_user(c.clerk).action_request_approval()
    pending.with_user(c.clerk).write({"reason_code_id": reason.id})
    pending.with_user(c.clerk).action_request_approval()
    assert pending.approval_state == "pending"


def test_the_threshold_is_configurable(c, officer):  # noqa: F811
    _reason(c.env, officer)
    c.env["ir.config_parameter"].sudo().set_param(THRESHOLD_PARAM, "20")
    below = _request(c, 15.0)
    below.with_user(c.clerk).action_request_approval()  # 15% <= 20%: no code needed
    above = _request(c, 25.0)
    with pytest.raises(UserError, match="needs a reason code"), c.env.cr.savepoint():
        above.with_user(c.clerk).action_request_approval()


def test_a_used_code_is_archived_never_renamed_or_deleted(c, officer):  # noqa: F811
    reason = _reason(c.env, officer)
    _request(c, 15.0, reason_code_id=reason.id)
    with pytest.raises(UserError, match="stays as it is"), c.env.cr.savepoint():
        reason.with_user(officer).write({"code": "OTHER"})
    with pytest.raises(UserError, match="archived"), c.env.cr.savepoint():
        reason.with_user(officer).unlink()
    reason.with_user(officer).write({"active": False})
    assert not reason.active


def test_a_decided_request_keeps_its_reason(c, officer):  # noqa: F811
    first, second = _reason(c.env, officer, "R1"), _reason(c.env, officer, "R2")
    auto = _request(c, 5.0, reason_code_id=first.id)  # within the agent band: auto-approved
    assert auto.state == "approved"
    with pytest.raises(UserError, match="keeps the reason"), c.env.cr.savepoint():
        auto.with_user(c.clerk).write({"reason_code_id": second.id})


def test_the_discount_register_shows_the_reason(c, officer):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers.a04 import m11

    reason = _reason(c.env, officer, "VOLUME")
    _request(c, 15.0, reason_code_id=reason.id)
    pack = m11.discount_register(c.env)
    assert "reason" in pack["cols"]
    assert any(row["reason"] == "VOLUME" for row in pack["rows"])
