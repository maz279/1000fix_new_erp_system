# M05 - the MSP contract is captured INSIDE the workspace.
#
# "+ MSP Contract" is M05's own create button and the create button of every
# sub-module page on that record. M05 declared forms for eight records and
# none for its anchor record, so the button fell through to the engine's last
# resort: the stock Odoo form in a dialog (found 2026-11-12 while walking the
# sub-module pages; the estate rule is that a record surface renders in the
# shell). The write whitelist for the model was empty for the same reason -
# it is generated from the forms.
#
# The registry is evaluated as the browser evaluates it (node, same harness
# as test_a08_m19_registry.py); the save goes through the form's endpoint.
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FORM = "M05-form-msp-contract"
EDITABLE = {
    "name",
    "contract_id",
    "monitoring_scope",
    "device_count",
    "per_device_monthly",
    "sla_target_pct",
    "alert_resolve_hours_major",
    "alert_resolve_hours_minor",
    # BRU-RMS-02 / 05 / 12 (M05 audit 2026-11-13)
    "unattended_access",
    "coverage_window",
    "recording_retention_days",
    "holiday_calendar_id",
    # A02 ERP pass 2 (M05-S09 / S17 / S18): scope and metering terms
    "response_hours_major",
    "response_hours_minor",
    "parts_included",
    "remote_hours_monthly",
    "overage_hourly_rate",
}

PROBE = """
import * as M from './meta.mjs';
const pick = (o) => Object.fromEntries(Object.entries(o).filter(([k]) => k.startsWith('M05')));
console.log(JSON.stringify({ forms: M.P03_MODULES.M05.forms, create: M.P03_MODULE_CREATE.M05,
  screens: pick(M.P03_DATA_SCREENS), chips: pick(M.P03_FORM_CHIPS) }));
"""


@pytest.fixture(scope="module")
def m05(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_registry_m05_contract")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(PROBE, "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)],
        capture_output=True,
        encoding="utf-8",  # Bengali labels: never the Windows ANSI codepage
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def _fields(form):
    return [f for section in form["sections"] for f in section["fields"]]


def test_the_module_button_opens_the_workspace_form(m05):
    """With no `screen`, onModuleNew falls back to the Odoo dialog."""
    assert m05["create"] == {"screen": FORM, "model": "fix.msp.contract", "label": "MSP Contract"}
    form = m05["screens"][FORM]
    assert form["kind"] == "model_form" and form["model"] == "fix.msp.contract"
    assert form.get("create") is not False
    assert m05["screens"][form["back"]]["kind"] == "model_list"


def test_rows_chips_and_the_list_reach_the_same_form(m05):
    assert m05["chips"]["M05:__by_model__"]["fix.msp.contract"] == FORM
    assert m05["chips"]["M05:MSP Contract"] == FORM
    assert "MSP Contract" in m05["forms"]
    # the list offers what the module's button offers
    assert m05["screens"]["M05-contracts"].get("create") is not False


def test_the_form_is_tabbed_and_shows_the_estate_it_covers(m05, odoo_env):
    form = m05["screens"][FORM]
    tabs = {t["id"] for t in form["tabs"]}
    # contract, commercials & SLA, lifecycle & offboarding (BRU-RMS-11), and
    # (A02 ERP pass 2, X5-19) the reports, credits and terms history grids
    assert len(tabs) == 4
    assert {s["tab"] for s in form["sections"]} | {g["tab"] for g in form["grids"]} == tabs
    grids = {g["field"]: g for g in form["grids"]}
    assert set(grids) == {"report_ids", "credit_ids", "terms_amendment_ids"}
    assert all(g["readonlyGrid"] for g in grids.values())
    contract_fields = odoo_env["fix.msp.contract"]._fields
    names = [f["name"] for f in _fields(form)]
    assert len(names) == len(set(names)), "a field declared twice locks its first input"
    assert [n for n in names if n not in contract_fields] == []
    # what the model refuses to save without
    required = {f["name"] for f in _fields(form) if f.get("required")}
    assert required == {"name", "contract_id", "monitoring_scope", "coverage_window"}
    grid = form["lines"]
    assert grid["field"] == "asset_ids" and grid["readonlyGrid"] is True
    asset_fields = odoo_env["fix.monitored.asset"]._fields
    assert [f["name"] for f in grid["fields"] if f["name"] not in asset_fields] == []


def test_the_form_edits_exactly_what_the_endpoint_accepts(m05):
    """writable.py is generated from the forms: an input the whitelist does
    not carry is refused on save, a whitelisted field with no input is dead."""
    editable = {f["name"] for f in _fields(m05["screens"][FORM]) if not f.get("readonly")}
    assert editable == EDITABLE
    assert WRITABLE["fix.msp.contract"] == frozenset(EDITABLE)
    assert api.SURFACES["fix.msp.contract"]["writable"] is WRITABLE["fix.msp.contract"]


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def m08_contract(odoo_env):
    env = odoo_env
    client = env["res.partner"].create({"name": "MSP Form Client Ltd", "is_company": True})
    return env["fix.contract"].create(
        {
            "code": "MSP-FORM-1",
            "name": "Managed endpoints (form test)",
            "family": "managed",
            "state": "active",
            "annual_value": 54000.0,
            "customer_id": client.id,
            "operating_unit_id": env["operating.unit"].search([], limit=1).id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
        }
    )


def test_a_contract_is_created_and_edited_through_the_form(m05, odoo_env, call, m08_contract):
    """Loads and saves as the form does: its own declared fields and grid."""
    env = odoo_env
    form = m05["screens"][FORM]
    declared = [{"name": f["name"]} for f in _fields(form)]
    grid = {"field": form["lines"]["field"], "fields": form["lines"]["fields"]}

    blank = call(env, "model_form", model="fix.msp.contract", fields=declared, lines=grid)
    assert "error" not in blank, blank
    assert [f["name"] for f in blank["fields"]] == [f["name"] for f in declared]
    assert blank["record"] is None

    saved = call(
        env,
        "model_write",
        model="fix.msp.contract",
        values={
            "name": "Head office endpoints",
            "contract_id": m08_contract.id,
            "monitoring_scope": "endpoints_network",
            "device_count": 40,
            "per_device_monthly": 450,
            "sla_target_pct": 95,
        },
    )
    assert "error" not in saved, saved
    msp = env["fix.msp.contract"].search([("contract_id", "=", m08_contract.id)])
    assert len(msp) == 1 and msp.name == "Head office endpoints"
    assert (msp.device_count, msp.per_device_monthly, msp.sla_target_pct) == (40, 450.0, 95.0)
    assert msp.monitoring_scope == "endpoints_network"

    # A02 ERP audit M05-F3: once saved, the SLA / commercial terms are not
    # re-typed through the form (an engineer lowered a live contract's target
    # and price, and with them the SLA credit owed); they change through Amend
    # Terms, by an SLA credit approver, with the reason on the chatter
    edited = call(
        env,
        "model_write",
        model="fix.msp.contract",
        record_id=msp.id,
        values={"device_count": 55, "alert_resolve_hours_major": 2},
    )
    assert "workflow" in (edited.get("error") or ""), edited
    msp.action_amend_terms(
        device_count=55,
        alert_resolve_hours_major=2,
        reason="Client added 15 branch endpoints (addendum 2)",
    )
    msp.invalidate_recordset()
    assert (msp.device_count, msp.alert_resolve_hours_major) == (55, 2.0)
    # the name is not a term: the form still edits it
    renamed = call(
        env,
        "model_write",
        model="fix.msp.contract",
        record_id=msp.id,
        values={"name": "Head office endpoints"},
    )
    assert "error" not in renamed, renamed

    shown = call(
        env, "model_form", model="fix.msp.contract", fields=declared, record_id=msp.id, lines=grid
    )
    assert "error" not in shown, shown
    assert shown["record"]["name"] == "Head office endpoints"
    # the saved contract's terms render read-only (the Amend Terms action
    # changes them); on the blank form they are typed once
    readonly = {f["name"]: f["readonly"] for f in shown["fields"]}
    assert readonly["device_count"] and readonly["sla_target_pct"]
    assert not readonly["name"]
    typed = {f["name"]: f["readonly"] for f in blank["fields"]}
    assert not typed["device_count"] and not typed["sla_target_pct"]
    assert shown["lines"]["rows"] == []  # no asset enrolled yet


def test_a_computed_figure_cannot_be_typed_through_the_form(odoo_env, call, m08_contract):
    """monthly_value is shown read-only: it is not on the whitelist, so the
    endpoint refuses it rather than storing a typed total."""
    env = odoo_env
    msp = env["fix.msp.contract"].create({"name": "Typed total", "contract_id": m08_contract.id})
    res = call(
        env,
        "model_write",
        model="fix.msp.contract",
        record_id=msp.id,
        values={"monthly_value": 999999},
    )
    assert "error" in res, res
