# A02 P1/P2 for the M01 workspace (cd_p03_portal), as NON-ADMIN users.
#
# - /p03/dispatch/assign assigned a technician for any user; it is now the
#   dispatcher's, and refuses everyone else before touching the order.
# - The order lists offer the whitelisted order actions that had no button
#   (OTP, settlement, cancel, unrepairable, goodwill...), each whitelisted.
# - Routed approvals are requested from the workspace, never pressed there.
import re
from pathlib import Path
from unittest import mock

from odoo.addons.cd_p03_portal.controllers import p03_service_order_api as api
from odoo.addons.cd_p03_portal.controllers.a02 import m01

M01_JS = Path(__file__).resolve().parents[1] / "static" / "src" / "a02" / "m01.js"


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _clerk(env):
    return env["res.users"].create(
        {
            "name": "A2P1 P03 Clerk",
            "login": "a2p1.p03.clerk@a02.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )


def test_dispatch_assign_is_refused_for_a_non_dispatcher(odoo_env):
    clerk_env = odoo_env(user=_clerk(odoo_env).id)
    order = odoo_env["fix.service.order"].search(
        [("state", "not in", ("closed", "cancelled"))], limit=1
    )
    before = order.technician_id
    with mock.patch.object(api, "request", FakeRequest(clerk_env)):
        result = api.P03ServiceOrderApiController().assign_dispatch(
            order_id=order.id, technician=""
        )
    assert result == {"success": False, "error": "Only a dispatcher assigns a technician."}
    assert order.technician_id == before


def _so_actions():
    src = M01_JS.read_text(encoding="utf-8")
    block = src[src.index("const SO_ACTIONS = [") : src.index("export const SCREENS")]
    return set(re.findall(r"\bm: '(\w+)'", block))


def test_every_order_action_button_is_whitelisted(odoo_env):
    actions = _so_actions()
    allowed = m01.SURFACES["fix.service.order"]["actions"]
    assert {
        "action_cancel",
        "action_mark_unrepairable",
        "action_mark_settled",
        "action_verify_settlement",
        "action_send_delivery_otp",
        "action_verify_delivery_otp",
        "action_request_goodwill",
        "action_change_category",
        "action_override_priority",
        "action_create_field_order",
        "action_create_workshop_job",
    } <= actions
    assert actions <= allowed, sorted(actions - allowed)
    for method in actions:
        assert hasattr(odoo_env["fix.service.order"], method), method


def test_routed_approvals_are_requested_not_pressed():
    order_actions = m01.SURFACES["fix.service.order"]["actions"]
    assert not {"action_approve_goodwill", "action_approve_rework"} & order_actions
    assert "action_manager_approve" not in m01.SURFACES["fix.estimate"]["actions"]
    assert "action_request_manager_key" in m01.SURFACES["fix.estimate"]["actions"]
    assert "action_verify" not in m01.SURFACES["fix.warranty"]["actions"]
    assert "action_request_approval" in m01.SURFACES["fix.warranty"]["actions"]
