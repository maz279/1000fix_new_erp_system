# M25 capture audit (2026-11-13) - the captures the sub-module pages now
# offer, driven through the workspace endpoints (/p03/model/write,
# /p03/model/action, /p03/model/report, /p03/bi/kpis) as NON-ADMIN users:
# the superuser is trusted by the model guards and would hide a gap.
#
#   * Lifecycle & Usage: a BI author registers a manual pack; a steward who is
#     not the owner reconciles it and retires it; the KPI tile counts it.
#   * Self-Service / Role Dashboards: the dashboard form carries its Data
#     Steward, so Submit for Review now succeeds from the workspace.
#   * Embedded Analytics: a BI Sync Operator creates a sync connection and
#     runs a snapshot; a clerk is refused.
#   * Standard Report Library: the library pack lists the six canonical packs.
#   * Distribution & Alerting: a schedule saved from the dropdown key sends now.
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a11 import m25

_SEQ = itertools.count(1)

AUTHOR = "cd_bi_reporting.group_bi_author"
CERTIFIER = "cd_bi_reporting.group_bi_certifier"
OPERATOR = "cd_bi_reporting.group_bi_operator"


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def env(odoo_env):
    if "fix.bi.manual.pack" not in odoo_env:
        pytest.skip("cd_bi_reporting (with the retirement register) is not installed")
    return odoo_env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        for module in (api, m25):
            p = mock.patch.object(module, "request", FakeRequest(env))
            p.start()
            patchers.append(p)
        if route == "bi_kpis":
            return m25.P03BiApi().bi_kpis(module="M25")
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _user(env, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M25 Capture User %d" % n,
                "login": "m25.capture.%d@a11.test" % n,
                "email": "m25.capture.%d@a11.test" % n,
                "group_ids": [(6, 0, groups)],
            }
        )
    )
    return env(user=user.id)


def test_the_retirement_register_round_trip(call, env):
    author = _user(env, AUTHOR)
    steward = _user(env, CERTIFIER)
    clerk = _user(env)

    refused = call(
        clerk,
        "model_write",
        model="fix.bi.manual.pack",
        values={"name": "Clerk pack", "function_area": "service", "frequency": "weekly"},
    )
    assert "id" not in refused, refused

    res = call(
        author,
        "model_write",
        model="fix.bi.manual.pack",
        values={
            "name": "Weekly branch KPI workbook",
            "function_area": "service",
            "owner_id": author.uid,
            "frequency": "weekly",
            "effort_hours": 6,
            "metrics_harvested": "orders delivered, TAT, FTF",
            "replacement_report_key": "M25:branch_league",
        },
    )
    assert "id" in res, res
    pack_id = res["id"]
    kpis_before = call(author, "bi_kpis")["M25"]["spreadsheets_retired"]

    def act(who, method, **kwargs):
        return call(
            who,
            "model_action",
            model="fix.bi.manual.pack",
            ids=[pack_id],
            method=method,
            kwargs=kwargs or None,
        )

    assert act(author, "action_start_parallel_run").get("success")
    blocked = act(author, "action_reconcile_matched", note="mine")
    assert not blocked.get("success") and "Steward" in (blocked.get("error") or ""), blocked
    assert act(steward, "action_reconcile_matched", note="Oct-Nov reconciled").get("success")
    assert act(steward, "action_retire").get("success")

    pack = env["fix.bi.manual.pack"].browse(pack_id)
    assert pack.state == "retired" and pack.retired_by.id == steward.uid
    assert call(author, "bi_kpis")["M25"]["spreadsheets_retired"] == kpis_before + 1


def test_the_lifecycle_cannot_be_typed_through_the_form(call, env):
    author = _user(env, AUTHOR)
    res = call(
        author,
        "model_write",
        model="fix.bi.manual.pack",
        values={
            "name": "Typed retired",
            "function_area": "finance",
            "frequency": "monthly",
            "owner_id": author.uid,
            "state": "retired",
        },
    )
    pack = env["fix.bi.manual.pack"].search([("name", "=", "Typed retired")])
    assert not pack or pack.state == "registered", res


def test_a_dashboard_with_its_steward_enters_review_from_the_workspace(call, env):
    author = _user(env, AUTHOR)
    steward = env["hr.employee"].create({"name": "M25 Live Steward"})
    res = call(
        author,
        "model_write",
        model="fix.bi.dashboard",
        values={"name": "COO morning board", "role": "coo", "steward_id": steward.id},
    )
    assert "id" in res, res
    out = call(
        author,
        "model_action",
        model="fix.bi.dashboard",
        ids=[res["id"]],
        method="action_submit_review",
    )
    assert out.get("success"), out
    assert env["fix.bi.dashboard"].browse(res["id"]).state == "review"


def test_a_shared_draft_is_refused_from_the_form(call, env):
    author = _user(env, AUTHOR)
    res = call(
        author,
        "model_write",
        model="fix.bi.dashboard",
        values={"name": "Shared draft", "role": "ceo", "is_shared": True},
    )
    assert "id" not in res and "BRU-BID-06" in (res.get("error") or ""), res


def test_the_operator_creates_and_runs_a_sync_connection(call, env):
    operator = _user(env, OPERATOR)
    clerk = _user(env)
    values = {"name": "Exec KPI dataset", "dataset_scope": "exec_kpi", "sync_frequency": "daily"}
    assert "id" not in call(clerk, "model_write", model="fix.bi.sync.config", values=values)
    res = call(operator, "model_write", model="fix.bi.sync.config", values=values)
    assert "id" in res, res
    for method in ("action_test_connection", "action_run_sync"):
        out = call(
            operator, "model_action", model="fix.bi.sync.config", ids=[res["id"]], method=method
        )
        assert out.get("success"), (method, out)
    logs = env["fix.bi.sync.log"].search([("config_id", "=", res["id"])])
    assert len(logs) == 1 and logs.ran_by.id == operator.uid


def test_the_report_library_lists_the_canonical_packs(call, env):
    clerk = _user(env)
    out = call(clerk, "model_report", module="M25", report="report_library", params={})
    assert not out.get("error"), out
    keys = [r["key"] for r in out["rows"]]
    assert keys == ["M25:%s" % k for k, *_ in m25.STANDARD_REPORTS]
    finance = next(r for r in out["rows"] if r["key"] == "M25:finance_pack")
    assert finance["entitlement"] == "BI Finance Reader"
    assert finance["exports_30d"] == "—"  # a clerk may not read the export audit


def test_a_schedule_from_the_dropdown_key_sends_now(call, env):
    author = _user(env, AUTHOR)
    reader = _user(env)
    res = call(
        author,
        "model_write",
        model="fix.bi.distribution.schedule",
        values={
            "name": "People pack monthly",
            "report_key": "M25:people_pack",
            "cadence": "monthly",
            "recipients": reader.user.login,
            "format": "csv",
        },
    )
    assert "id" in res, res
    out = call(
        author,
        "model_action",
        model="fix.bi.distribution.schedule",
        ids=[res["id"]],
        method="action_send_now",
    )
    assert out.get("success"), out
    assert env["fix.bi.distribution.schedule"].browse(res["id"]).last_status == "sent"
