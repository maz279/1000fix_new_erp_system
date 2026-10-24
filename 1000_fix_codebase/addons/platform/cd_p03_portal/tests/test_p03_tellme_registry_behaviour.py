# Behavioural tests for the P03 registry + Tell-ME search controllers. The
# registry is the committed contracts/nav/registry.json; live-record search
# runs against the rolled-back `odoo_env` through a patched `request`.
import json
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_registry, p03_tellme
from odoo.exceptions import AccessError

REGISTRY = json.loads(p03_registry.REGISTRY_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def search(odoo_env):
    with mock.patch.object(p03_tellme, "request", SimpleNamespace(env=odoo_env)):
        controller = p03_tellme.TellMeSearchController()
        yield controller.search


_INTERNAL_USER = SimpleNamespace(id=2, _is_internal=lambda: True)


class _BrokenEnv:
    """An authenticated internal session whose record search fails."""

    user = _INTERNAL_USER

    def __getitem__(self, model):
        raise RuntimeError("no database bound to this request")


class _BrokenRequest:
    env = _BrokenEnv()


def test_registry_endpoint_serves_the_committed_registry():
    fake = SimpleNamespace(env=SimpleNamespace(user=_INTERNAL_USER))
    with mock.patch.object(p03_registry, "request", fake):
        served = p03_registry.P03RegistryController().get_registry()
    assert served == REGISTRY
    assert {"areas", "modules", "personas"} <= set(served)


def _portal_env(odoo_env):
    user = odoo_env["res.users"].create(
        {
            "name": "P03 Portal Probe",
            "login": "p03.portal.probe@example.test",
            "group_ids": [(6, 0, [odoo_env.ref("base.group_portal").id])],
        }
    )
    return odoo_env(user=user)


def test_registry_and_tellme_refuse_portal_sessions(odoo_env):
    """auth="user" admits portal users — the P03 back-office endpoints must
    refuse them (pentest: portal session reading the back-office index)."""
    portal = SimpleNamespace(env=_portal_env(odoo_env))
    with mock.patch.object(p03_registry, "request", portal), pytest.raises(AccessError):
        p03_registry.P03RegistryController().get_registry()
    with mock.patch.object(p03_tellme, "request", portal), pytest.raises(AccessError):
        p03_tellme.TellMeSearchController().search(query="Order")


def test_index_is_built_once_and_cached(monkeypatch):
    monkeypatch.setattr(p03_tellme, "_INDEX", None)
    first = p03_tellme._get_index()
    assert p03_tellme._get_index() is first

    kinds = {entry["kind"] for entry in first}
    assert kinds == {"module", "screen", "report", "form"}
    modules = [e for e in first if e["kind"] == "module"]
    assert len(modules) == len(REGISTRY["modules"])
    m01 = REGISTRY["modules"][0]
    assert {
        "kind": "module",
        "id": m01["id"],
        "en": m01["en"],
        "bn": m01["bn"],
        "area": m01["area"],
    } in first


def test_index_tolerates_sparse_registry_entries(monkeypatch, tmp_path):
    sparse = {"modules": [{"id": "MX", "en": "Sparse Module"}]}
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(sparse), encoding="utf-8")
    monkeypatch.setattr(p03_tellme, "REGISTRY_PATH", path)
    assert p03_tellme._build_index() == [
        {"kind": "module", "id": "MX", "en": "Sparse Module", "bn": "", "area": ""}
    ]


@pytest.mark.parametrize("query", ["", " ", "a", " b "])
def test_too_short_queries_return_nothing(search, query):
    assert search(query=query) == {"results": []}


def test_english_search_ranks_modules_before_screens_reports_forms(search):
    results = search(query="ORDER", limit=500)["results"]
    registry_hits = [r for r in results if r["kind"] in ("module", "screen", "report", "form")]
    ranks = [("module", "screen", "report", "form").index(r["kind"]) for r in registry_hits]
    assert ranks == sorted(ranks)
    assert any(r["id"] == "M01-board" and r["kind"] == "screen" for r in registry_hits)
    assert all("order" in r["en"].lower() for r in registry_hits)
    assert all(r["matched_locale"] == "en" for r in registry_hits)


def test_report_and_form_entries_are_searchable(search):
    reports = search(query="Daily Intake by Channel")["results"]
    assert {
        "kind": "report",
        "id": "M01-report",
        "en": "Daily Intake by Channel",
        "bn": "",
        "area": "M01",
        "matched_locale": "en",
    } in reports
    forms = search(query="Estimate Request")["results"]
    assert any(r["kind"] == "form" and r["id"] == "M01-form" for r in forms)


def test_bengali_search_matches_the_bengali_locale(search):
    module = REGISTRY["modules"][0]
    results = search(query=module["bn"])["results"]
    hit = next(r for r in results if r["id"] == module["id"])
    assert hit["kind"] == "module"
    assert hit["matched_locale"] == "bn"


def test_limit_caps_the_result_list(search):
    assert len(search(query="report", limit=3)["results"]) == 3


def _p03_world(env):
    company = env.company
    entity = env["fix.entity"].search([("company_id", "=", company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "TELLME", "legal_name": "Tell Me Ltd", "company_id": company.id})
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    branch = env["fix.branch"].create(
        {
            "code": "QZB",
            "name": "Quixotic Branch",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    partner = env["res.partner"].create({"name": "Quixotic Customer", "phone": "01555000111"})
    brand = env["fix.brand"].create({"name": "Quixbrand", "code": "QXB"})
    model = env["fix.device.model"].create({"brand_id": brand.id, "name": "QX-1"})
    device = env["fix.device"].create(
        {"serial_number": "SN-QX-1", "device_model_id": model.id, "owner_id": partner.id}
    )
    order = env["fix.service.order"].create(
        {
            "customer_id": partner.id,
            "branch_id": branch.id,
            "device_id": device.id,
            "fault_description": "Dead pixel",
            "state": "intake",
        }
    )
    employee = env["hr.employee"].create({"name": "Quixotic Engineer"})
    return order, branch, employee


def test_live_records_are_surfaced_ahead_of_the_registry(search, odoo_env):
    order, branch, employee = _p03_world(odoo_env)

    results = search(query="Quixotic", limit=50)["results"]

    assert results[0]["kind"] == "record"
    assert results[0]["res_id"] == order.id
    assert results[0]["en"] == f"📦 {order.name} — Quixotic Customer (intake)"
    assert results[1] == {
        "kind": "branch",
        "id": f"branch-{branch.id}",
        "res_model": "fix.branch",
        "res_id": branch.id,
        "en": "🏢 Quixotic Branch",
        "bn": "🏢 Quixotic Branch",
        "area": "Service Operations",
        "group": "Branches",
        "matched_locale": "en",
    }
    staff = results[-1]
    assert staff["kind"] == "staff" and staff["res_id"] == employee.id
    assert staff["en"] == "👤 Quixotic Engineer (Technician)"


def test_live_order_search_by_customer_phone(search, odoo_env):
    order, _branch, _employee = _p03_world(odoo_env)
    results = search(query="01555000111")["results"]
    assert [r["res_id"] for r in results if r["kind"] == "record"] == [order.id]


def test_branch_hit_leads_when_no_order_matches(search, odoo_env):
    _order, branch, _employee = _p03_world(odoo_env)
    results = search(query="Quixotic Branch")["results"]
    assert results[0]["kind"] == "branch" and results[0]["res_id"] == branch.id


def test_record_search_failure_degrades_to_registry_only():
    with mock.patch.object(p03_tellme, "request", _BrokenRequest()):
        results = p03_tellme.TellMeSearchController().search(query="Order Operations Board")
    kinds = {r["kind"] for r in results["results"]}
    assert kinds == {"screen"}
