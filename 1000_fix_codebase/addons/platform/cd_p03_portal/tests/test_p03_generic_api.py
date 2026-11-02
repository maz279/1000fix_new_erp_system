# Behavioural tests for the A08 generic workspace endpoints (/p03/model/*):
# the module-level `request` is patched with the rolled-back `odoo_env` and
# the route methods are called directly (same pattern as the service-order
# API tests).
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import a08
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError

_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _user(env, *groups):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": f"A08 Surface User {n}",
            "login": f"a08-surface-{n}@test.local",
            "group_ids": [(6, 0, [env.ref(g).id for g in groups])],
        }
    )


@pytest.fixture
def call(odoo_env):
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def test_every_surface_is_declared_by_exactly_one_module():
    owners = {}
    for mod in (a08.m19, a08.m20, a08.m52, a08.m50, a08.m51, a08.m53, a08.m49, a08.m54):
        for model in mod.SURFACES:
            assert model not in owners, f"{model} declared by {owners[model]} and {mod.__name__}"
            owners[model] = mod.__name__
    assert set(owners) == set(a08.SURFACES)


def test_undeclared_model_is_refused(odoo_env, call):
    # res.users/res.partner ARE served (M29 user directory, M33 parties);
    # res.company is a real model no workspace screen declares — refusal.
    res = call(odoo_env, "model_records", model="res.company", cols=["name"])
    assert res == {"error": "Model not served by the workspace screens"}


def test_portal_user_is_refused(odoo_env, call):
    portal = _user(odoo_env, "base.group_portal")
    with pytest.raises(AccessError):
        call(
            odoo_env(user=portal),
            "model_records",
            model="fix.vendor.invoice",
            cols=["invoice_ref"],
        )


def test_employee_without_finance_read_access_cannot_list_vendor_bills(odoo_env, call):
    """Regression: the company-wide sudo read let ANY internal user list
    finance records the accounting ACLs keep from them."""
    clerk = _user(odoo_env, "base.group_user")
    if odoo_env["fix.vendor.invoice"].with_user(clerk).has_access("read"):
        pytest.skip("vendor bills are readable by plain employees in this build")
    res = call(
        odoo_env(user=clerk), "model_records", model="fix.vendor.invoice", cols=["invoice_ref"]
    )
    assert "error" in res and "rows" not in res


def test_accountant_lists_vendor_bills(odoo_env, call):
    accountant = _user(odoo_env, "base.group_user", "account.group_account_user")
    res = call(
        odoo_env(user=accountant),
        "model_records",
        model="fix.vendor.invoice",
        cols=["invoice_ref", "access_token"],
    )
    assert "error" not in res, res
    assert "access_token" not in res["labels"]


def test_only_declared_workflow_methods_run(odoo_env, call):
    res = call(odoo_env, "model_action", model="fix.vendor.invoice", ids=[1], method="unlink")
    assert res == {"success": False, "error": "Action not available for this surface"}


def test_unexpected_failures_do_not_leak_internals(odoo_env, call):
    with mock.patch.object(
        type(odoo_env["fix.vendor.invoice"]), "search", side_effect=RuntimeError("SELECT secret")
    ):
        res = call(odoo_env, "model_records", model="fix.vendor.invoice", cols=["invoice_ref"])
    assert "secret" not in res["error"]


def test_undeclared_report_is_refused(odoo_env, call):
    res = call(odoo_env, "model_report", module="M52", report="nope")
    assert res == {"error": "Report not available on this surface"}


def test_declared_report_runs_with_params_and_defaults(odoo_env, call):
    def ageing(env, date_from=None, date_to=None):
        return {"cols": ["bucket"], "rows": [{"bucket": f"{date_from}..{date_to}"}]}

    with mock.patch.object(a08.m52, "REPORTS", {"ageing": ageing}, create=True):
        res = call(
            odoo_env,
            "model_report",
            module="M52",
            report="ageing",
            params={"date_from": "2026-07-01", "date_to": "2027-06-30"},
        )
    assert res["rows"] == [{"bucket": "2026-07-01..2027-06-30"}]


def test_report_failures_do_not_leak_internals(odoo_env, call):
    def broken(env, **kw):
        raise RuntimeError("SELECT secret")

    with mock.patch.object(a08.m52, "REPORTS", {"broken": broken}, create=True):
        res = call(odoo_env, "model_report", module="M52", report="broken")
    assert "secret" not in res["error"]
