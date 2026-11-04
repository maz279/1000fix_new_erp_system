# cd_metric_registry — P06 analytics API, called directly with a fake
# `request` over the live ORM (KPIs) and over temporary evidence trees
# (register / governance / STT endpoints; repo root = __file__.parents[5]).
import json
import sys
import threading
import types
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.addons.cd_metric_registry.controllers import analytics_api

API = analytics_api.AnalyticsApiController()


@pytest.fixture
def live(odoo_env, monkeypatch):
    monkeypatch.setattr(analytics_api, "request", SimpleNamespace(env=odoo_env))
    return odoo_env


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A fake repository root: the controller resolves files from it."""
    fake_file = tmp_path / "addons" / "domain" / "j" / "cd_x" / "controllers" / "analytics_api.py"
    monkeypatch.setattr(analytics_api, "__file__", str(fake_file))
    return tmp_path


def _write(root, relative, data):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# --- /analytics/dashboards ----------------------------------------------------------


def test_dashboards_embed_only_when_configured(live):
    result = API.dashboards()
    assert result["total"] == 6
    ids = [d["id"] for d in result["dashboards"]]
    assert ids == ["executive", "branch", "technician", "finance", "warranty", "people"]
    assert all(d["embed_url"] is None and not d["embed_available"] for d in result["dashboards"])
    live["ir.config_parameter"].set_param(
        "fix_bi_embed_finance", "http://superset.local/embed/finance"
    )
    finance = API.dashboards()["dashboards"][3]
    assert finance == {
        "id": "finance",
        "area": "A11",
        "title_en": "Finance",
        "title_bn": "ফাইন্যান্স",
        "audience": "finance",
        "embed_available": True,
        "embed_url": "http://superset.local/embed/finance",
    }


# --- /analytics/kpis --------------------------------------------------------------


def test_kpis_reject_unknown_dashboard(live):
    assert API.kpis(dashboard="sales") == {
        "error": {
            "code": "invalid_dashboard",
            "message": "dashboard must be one of branch, executive, finance, people, "
            "technician, warranty",
        }
    }


@pytest.fixture
def orders(live):
    env = live
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].create(
        {"code": "ANLT", "legal_name": "Analytics Test Ltd", "company_id": env.company.id}
    )
    branches = [
        env["fix.branch"].create(
            {"code": code, "name": name, "entity_id": entity.id, "operating_unit_id": ou.id}
        )
        for code, name in (("AN1", "Gulshan"), ("AN2", "Mirpur"))
    ]
    brand = env["fix.brand"].create({"name": "Analytics Brand", "code": "ANLB"})
    model = env["fix.device.model"].create({"name": "Model K", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "KPI Customer"})
    tech = env["hr.employee"].create({"name": "Tech Kpi"})

    def order(branch, **vals):
        device = env["fix.device"].create({"device_model_id": model.id, "branch_id": branch.id})
        return env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": branch.id,
                "fault_description": "KPI fixture",
                **vals,
            }
        )

    created = [
        order(branches[0]),
        order(branches[0], technician_id=tech.id),
        order(branches[1]),
    ]
    return SimpleNamespace(env=env, ou=ou, brand=brand, orders=created, branches=branches)


def test_executive_kpis_count_orders_by_state(orders):
    assert [o.state for o in orders.orders] == ["draft"] * 3
    orders.orders[2].write({"state": "intake"})
    result = API.kpis()["kpis"]  # executive is the default dashboard
    assert result == {
        "dashboard": "executive",
        "orders_by_state": {"draft": 2, "intake": 1},
        "orders_total": 3,
    }


def test_branch_and_technician_breakdowns(orders):
    branch = API.kpis(dashboard="branch")["kpis"]["breakdown"]
    assert sorted((row["name"], row["open"]) for row in branch) == [("Gulshan", 2), ("Mirpur", 1)]
    tech = API.kpis(dashboard="technician")["kpis"]["breakdown"]
    assert sorted((row["name"], row["open"]) for row in tech) == [
        ("(unassigned)", 2),
        ("Tech Kpi", 1),
    ]


def test_warranty_claims_by_state(orders):
    order = orders.orders[0]
    orders.env["fix.warranty.claim"].create(
        {
            "operating_unit_id": orders.ou.id,
            "brand_id": orders.brand.id,
            "service_order_id": order.id,
            "claim_amount": 1500.0,
        }
    )
    result = API.kpis(dashboard="warranty")["kpis"]
    assert result["claims_by_state"] == {"draft": 1}
    assert result["orders_total"] == 3


def test_people_governance_kpi_090(live):
    """Regression: active_contracts was always 0 (an empty recordset is falsy)."""
    Employee = live["hr.employee"]
    active_before = Employee.search_count([("active", "=", True)])
    first = API.kpis(dashboard="people")["kpis"]["people_metrics"]
    assert first["active_employees"] == active_before
    assert first["kpi_090_orphaned_accounts"] == 0
    assert first["kpi_090_status"] == "COMPLIANT"
    emp = Employee.create({"name": "Contracted"})
    live["fix.employment.contract"].create(
        {
            "employee_id": emp.id,
            "joining_date": fields.Date.today(),
            "basic_monthly": 30000.0,
            "state": "active",
        }
    )
    # a leaver (the archive is the leaver event) whose Keycloak removal was
    # never confirmed, the event now 2 days old - arranged through the
    # people-side ORM (LB-06: no SQL mutation from the analytics module)
    leaver = Employee.create({"name": "Leaver Not Revoked", "joined_date": date(2024, 1, 1)})
    leaver.write({"active": False})
    assert leaver.keycloak_deprovision_status == "pending"
    leaver.write({"left_at": fields.Datetime.now() - timedelta(days=2)})
    metrics = API.kpis(dashboard="people")["kpis"]["people_metrics"]
    assert metrics == {
        "active_employees": active_before + 1,
        "active_contracts": first["active_contracts"] + 1,
        "kpi_090_orphaned_accounts": 1,
        "kpi_090_target": 0,
        "kpi_090_status": "BREACH",
        "leaver_deprovision_sla_hours": 1.0,
    }


class _EnvWithoutHrCore:
    """The registry as it looks when cd_hr_core is not installed."""

    def __init__(self, env):
        self._env = env

    def __contains__(self, model):
        return model != "fix.employment.contract" and model in self._env

    def __getitem__(self, model):
        if model == "hr.employee":
            real = self._env["hr.employee"]
            return SimpleNamespace(sudo=lambda: SimpleNamespace(search_count=real.search_count))
        return self._env[model]


def test_people_kpis_degrade_without_hr_core(odoo_env, monkeypatch):
    monkeypatch.setattr(analytics_api, "request", SimpleNamespace(env=_EnvWithoutHrCore(odoo_env)))
    metrics = API.kpis(dashboard="people")["kpis"]["people_metrics"]
    assert metrics["active_contracts"] == 0
    assert metrics["kpi_090_orphaned_accounts"] == 0
    assert metrics["kpi_090_status"] == "COMPLIANT"


# --- /analytics/kpis/register -------------------------------------------------------

REGISTER = {
    "total_registered": 95,
    "reconciliation_bm002": {"status": "reconciled"},
    "register": [
        {"kpi": "KPI-001", "family": "service", "owner": "M01"},
        {"kpi": "KPI-002", "family": "service", "owner": "M02"},
        {"kpi": "KPI-050", "family": "finance", "owner": "M01"},
    ],
}


def test_kpi_register_missing(repo):
    assert API.kpi_register() == {
        "error": {"code": "not_found", "message": "kpi-register.json not found"}
    }


def test_kpi_register_filters(repo):
    _write(repo, "services/bi-warehouse/kpi-register.json", REGISTER)
    everything = API.kpi_register()
    assert (everything["total_registered"], everything["returned_count"]) == (95, 3)
    assert everything["reconciliation"] == {"status": "reconciled"}
    assert [k["kpi"] for k in API.kpi_register(family="service")["kpis"]] == ["KPI-001", "KPI-002"]
    assert [k["kpi"] for k in API.kpi_register(owner="M01")["kpis"]] == ["KPI-001", "KPI-050"]
    both = API.kpi_register(family="service", owner="M01")
    assert (both["returned_count"], both["kpis"][0]["kpi"]) == (1, "KPI-001")


def test_kpi_register_total_defaults_to_the_list_length(repo):
    _write(repo, "services/bi-warehouse/kpi-register.json", {"register": REGISTER["register"]})
    result = API.kpi_register()
    assert (result["total_registered"], result["reconciliation"]) == (3, None)


def test_kpi_register_against_the_repository_file():
    result = API.kpi_register(family="service")
    assert result["total_registered"] == 95
    assert result["returned_count"] == 10
    assert all(k["family"] == "service" for k in result["kpis"])


# --- /analytics/governance/* ---------------------------------------------------------

EVIDENCE = "docs/traceability/evidence/"


@pytest.mark.parametrize(
    ("endpoint", "filename"),
    [
        ("governance_catalogue", "r09-m02-data-catalogue-audit.json"),
        ("governance_dq", "r09-m02-dq-monitoring-evidence.json"),
        ("governance_residency", "r09-m02-nfr086c-residency-scan.json"),
    ],
)
def test_governance_evidence_passthrough(repo, endpoint, filename):
    assert getattr(API, endpoint)() == {
        "error": {"code": "not_found", "message": f"{filename} not found"}
    }
    _write(repo, EVIDENCE + filename, {"status": "PASS", "file": filename})
    # A11 audit E5: the artefact is served verbatim AND labelled as a frozen
    # audit artefact — the endpoint must not imply a live measurement.
    result = getattr(API, endpoint)()
    assert result["status"] == "PASS" and result["file"] == filename
    assert result["is_frozen_artifact"] is True
    assert result["artifact"] == filename
    assert "NOT a live measurement" in result["note"]


def test_governance_lineage(repo):
    assert API.governance_lineage() == {
        "error": {"code": "not_found", "message": "r09-m02-lineage-audit.json not found"}
    }
    _write(
        repo,
        EVIDENCE + "r09-m02-lineage-audit.json",
        {
            "milestone": "R09-M02",
            "task": "T02",
            "standard": "DA-003",
            "audit_timestamp": "2026-09-30T10:00:00Z",
            "lineage_coverage_pct": 100.0,
            "status": "PASS",
            "feeds": [{"feed_name": "fact_invoices"}, {"feed_name": "fact_nps"}],
        },
    )
    full = API.governance_lineage()
    assert full["total_warehouse_feeds"] == 2
    assert (full["milestone"], full["status"], full["lineage_coverage_pct"]) == (
        "R09-M02",
        "PASS",
        100.0,
    )
    one = API.governance_lineage(feed="fact_nps")
    assert (one["total_warehouse_feeds"], one["feeds"]) == (1, [{"feed_name": "fact_nps"}])


# --- /analytics/stt/dashboard --------------------------------------------------------


def test_stt_dashboard_prefers_the_evidence_file(repo):
    _write(repo, EVIDENCE + "r09-m03-stt-production-evidence.json", {"measured_wer": 0.104})
    assert API.stt_dashboard() == {"measured_wer": 0.104}


def test_stt_dashboard_falls_back_to_the_service(repo, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    fake = types.ModuleType("stt")
    fake.get_stt_dashboard_metrics = lambda: {"measured_wer": 0.111, "stage": "production"}
    monkeypatch.setitem(sys.modules, "stt", fake)
    stt_src = str(repo / "services" / "stt" / "src")
    assert API.stt_dashboard() == {"measured_wer": 0.111, "stage": "production"}
    assert sys.path[0] == stt_src
    API.stt_dashboard()  # second call: the path is not inserted twice
    assert sys.path.count(stt_src) == 1


def test_stt_dashboard_reports_an_unavailable_service(repo, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setitem(sys.modules, "stt", None)  # import fails
    result = API.stt_dashboard()
    assert result["drift_monitoring"] == {"drift_detected": False, "status": "HEALTHY"}
    assert result["active_version"] == "1.0.0"
    assert "stt" in result["error"]


# --- route registration & the published contract ------------------------------------
# A11 P3: these replaced the old source-grep suite (assertIn on the .py text).
# The behaviour under test is what the SERVER actually registered, read from
# the live routing map — if a decorator drifts, the map drifts with it.

ANALYTICS_ROUTES = (
    "/analytics/dashboards",
    "/analytics/kpis",
    "/analytics/kpis/register",
    "/analytics/governance/catalogue",
    "/analytics/governance/lineage",
    "/analytics/governance/dq",
    "/analytics/governance/residency",
    "/analytics/stt/dashboard",
)


def test_routes_are_registered_jsonrpc_user_readonly(live):
    registered = {}
    # routing_map() builds lazily via Registry(threading.current_thread().dbname);
    # Odoo sets that attribute on its worker threads, pytest runs on the bare
    # main thread — stamp it for the duration, restore afterwards.
    thread = threading.current_thread()
    previous = getattr(thread, "dbname", None)
    thread.dbname = live.cr.dbname
    try:
        rules = list(live["ir.http"].routing_map().iter_rules())
    finally:
        if previous is None:
            del thread.dbname
        else:
            thread.dbname = previous
    for rule in rules:
        path = rule.rule
        if path.startswith("/analytics"):
            registered[path] = rule.endpoint.routing
    assert sorted(registered) == sorted(ANALYTICS_ROUTES), (
        "the analytics surface changed: %s" % sorted(registered)
    )
    for path, routing in registered.items():
        assert routing.get("type") == "jsonrpc", "%s is not jsonrpc" % path
        assert routing.get("auth") == "user", "%s is not auth=user" % path
        assert routing.get("readonly") is True, "%s is not readonly" % path


def test_openapi_contract_lists_the_analytics_operations():
    """The published W4 contract carries the same eight operations the server
    registers (the contract file is data, not module source)."""
    import json
    from pathlib import Path

    spec = json.loads(
        (
            Path(__file__).resolve().parents[5] / "contracts" / "openapi" / "w4-portals.json"
        ).read_text(encoding="utf-8")
    )
    missing = [r for r in ANALYTICS_ROUTES if r not in spec["paths"]]
    assert not missing, "the OpenAPI contract is missing %s" % missing
