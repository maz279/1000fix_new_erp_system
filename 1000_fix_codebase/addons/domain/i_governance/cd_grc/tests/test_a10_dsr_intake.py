# A10 deep audit (2026-11-23, D-A10-9): the PDPA DSR intake route.
#
# The 30-day clock existed with no producer; the intake route opens the
# register automatically so the clock always runs on real requests.
from unittest.mock import patch

from odoo import api as odoo_api
from odoo.addons.cd_grc.controllers import fix_grc_dsr_api as dsr_api
from odoo.addons.cd_grc.controllers.fix_grc_dsr_api import FixGrcDsrApi


class _Request:
    def __init__(self, env):
        self.env = env


def _call(env, user, **params):
    with patch.object(dsr_api, "request", _Request(env(user=user.id))):
        return FixGrcDsrApi().create_dsr(**params)


def _staff(env):
    return env["res.users"].create(
        {
            "name": "DSR Filer",
            "login": "dsr.filer@a10.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )


def test_an_authenticated_staff_member_files_a_request(odoo_env):
    env = odoo_env
    user = _staff(env)
    out = _call(
        env,
        user,
        request_type="access",
        subject_name="Rahim Uddin",
        contact="01711000123",
        notes="Customer called the hotline",
    )
    assert out["id"] and out["name"].startswith("DSR/")
    dsr = env["fix.grc.pdpa"].browse(out["id"])
    assert dsr.outcome == "pending"
    assert dsr.due_on == dsr.received_on + __import__("datetime").timedelta(days=30)
    assert "01711000123" in (dsr.notes or "")
    # the clock arms: the daily cron tells nobody yet (inside the window)
    env["fix.grc.pdpa"].cron_dsr_overdue()
    dsr.invalidate_recordset()
    assert not dsr.overdue_notified_on


def test_the_anonymous_call_is_refused(odoo_env):
    env = odoo_env
    with patch.object(
        dsr_api, "request", _Request(odoo_api.Environment(env.cr, None, env.context))
    ):
        out = FixGrcDsrApi().create_dsr(request_type="access", subject_name="X")
    assert out["error"] == "unauthenticated"


def test_bad_input_is_refused_with_a_named_reason(odoo_env):
    env = odoo_env
    user = _staff(env)
    assert _call(env, user, request_type="access", subject_name="")["error"] == "missing_subject"
    assert _call(env, user, request_type="delete_everything", subject_name="Y")["error"] == (
        "invalid_type"
    )
