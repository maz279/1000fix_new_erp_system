# A08 · M20 — the workspace registry (static/src/a08/m20.js) keeps its fifteen
# bespoke /p03/ar/* screens and adds generic screens that agree with the
# backend surface (controllers/a08/m20.py): customer VDS certificates
# (Mushak 6.6 received), invoice close-out (action_register_paid) and the VDS
# claim register; the Hold button runs fix.credit.profile.action_toggle_hold.
from __future__ import annotations

import json
import re
import shutil
import subprocess
import uuid
from datetime import date
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_ar_api, p03_generic_api
from odoo.addons.cd_p03_portal.controllers.a08 import m20

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
CODE = "M20"
BESPOKE = {
    "M20-invoices": "ar_invoices",
    "M20-invoice": "ar_editor",
    "M20-events": "ar_events",
    "M20-consolidated": "ar_consolidated",
    "M20-brand": "ar_brand",
    "M20-receipts": "ar_receipts",
    "M20-links": "ar_links",
    "M20-allocation": "ar_allocation",
    "M20-credit": "ar_credit",
    "M20-dunning": "ar_dunning",
    "M20-disputes": "ar_disputes",
    "M20-refunds": "ar_refunds",
    "M20-aging": "ar_aging",
    "M20-leakage": "ar_leakage",
    "M20-statements": "ar_statements",
}
# metrics the shared /p03/finance/kpis endpoint already computes for M20
BUILTIN_KPIS = {
    "ar_invoices_mtd",
    "overdue_gt_60d",
    "dso",
    "auto_generated_pct",
    "within_1h_pct",
    "credit_notes_total",
}


@pytest.fixture(scope="module")
def registry(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_registry_m20")
    # every area folder the registry imports (a02, a08, ...)
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as M from './meta.mjs';\n"
        "const pick = (o) => Object.fromEntries(Object.entries(o).filter(([k]) => k.startsWith('M20')));\n"
        "console.log(JSON.stringify({module: M.P03_MODULES.M20,\n"
        "  screens: pick(M.P03_DATA_SCREENS), routes: pick(M.P03_REPORT_ROUTES),\n"
        "  forms: pick(M.P03_FORM_MODELS), create: M.P03_MODULE_CREATE.M20}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv built in-process, no shell
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def test_bespoke_screens_kept_and_every_screen_is_real(registry):
    ids = [s["id"] for g in registry["module"]["groups"] for s in g["screens"]]
    assert len(ids) == len(set(ids))
    # Every nav screen renders (no dead nav entries)…
    assert set(ids) <= set(registry["screens"])
    # …and every non-nav SCREENS entry is a reachable D365 surface: a
    # model_form with a back-target grid, or a pack routed from a report
    # chip (the AR form/report sweeps added these deliberately).
    routed = set(registry["routes"].values())
    orphans = [
        sid
        for sid, cfg in registry["screens"].items()
        if sid not in set(ids)
        and not (cfg.get("kind") == "model_form" and cfg.get("back"))
        and sid not in routed
    ]
    assert not orphans, f"orphan screens unreachable from nav or chips: {orphans}"
    for sid, kind in BESPOKE.items():
        assert registry["screens"][sid]["kind"] == kind
    # the bespoke dunning WORKLIST console keeps M20-dunning; the fix.dunning
    # register grid is the separate M20-dunning-register screen (the shared
    # id previously clobbered the ar_dunning kind in the SCREENS map).
    added = set(ids) - set(BESPOKE)
    assert added == {
        "M20-writeoffs",
        "M20-unapplied",
        "M20-ecl-rates",
        "M20-gl-recon",
        "M20-vds",
        "M20-tds",
        "M20-closeout",
        "M20-vds-register",
        "M20-ecl",
        "M20-ar-dispute",
        "M20-ar-consolidated-bill",
        "M20-dunning-register",
        "M20-notes-register",
        # capture pass 2 (2026-11-19): the spec's records on pages 4/5/8/9/10
        "M20-deliveries",
        "M20-statement-register",
        "M20-deposits",
        "M20-dunning-policies",
        "M20-promises",
        "M20-plans",
        "M20-cases",
        "M20-oa-refunds",
        "M20-unbilled",
        # A08 wave 5 (M20-F5): the reminder delivery evidence and the M27
        # call hand-off queue of the dunning ladder.
        "M20-dunning-evidence",
        "M20-handoffs",
    }
    for g in registry["module"]["groups"]:
        for s in g["screens"]:
            assert s.get("bn"), s["id"]


def test_generic_screens_match_surfaces_and_fields(registry, odoo_env):
    for sid, cfg in registry["screens"].items():
        if cfg["kind"] == "model_list":
            model = cfg["model"]
            assert model in m20.SURFACES, f"{sid}: {model} not served"
            fields_ = odoo_env[model]._fields
            for col in cfg["cols"]:
                assert col in fields_, f"{sid}: {model}.{col}"
            for act in cfg.get("actions", []):
                assert act["m"] in m20.SURFACES[model]["actions"]
                assert callable(getattr(odoo_env[model], act["m"], None))
            for leaf in cfg.get("domain", []):
                assert leaf[0] in fields_
        elif cfg["kind"] == "table_report":
            assert cfg["module"] == CODE and cfg["report"] in m20.REPORTS
    assert registry["screens"]["M20-closeout"]["actions"][0]["m"] == "action_register_paid"
    for model, conf in m20.SURFACES.items():
        for method in conf["actions"]:
            assert callable(getattr(odoo_env[model], method, None))


def test_chips_and_kpis(registry, odoo_env):
    module = registry["module"]
    for chip in module["reports"]:
        assert registry["routes"].get(f"{CODE}:{chip}") in registry["screens"], chip
    for chip in module["forms"]:
        model = registry["forms"].get(f"{CODE}:{chip}")
        assert model and model in odoo_env, f"form chip {chip!r} unmapped"
    keys = set(m20.kpis(odoo_env)) | BUILTIN_KPIS
    for kpi in module["kpis"]:
        assert kpi.get("m") in keys, kpi


# --------------------------------------------------------------------------- behaviour


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def shop(odoo_env):
    env = odoo_env
    if not env.company.vat:
        env.company.vat = "1234567890123"
    customer = env["res.partner"].create(
        {"name": f"VDS Corp {uuid.uuid4().hex[:5]}", "vat": "9876543210123"}
    )
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    invoice = env["fix.ar.invoice"].create(
        {
            "customer_id": customer.id,
            "operating_unit_id": ou.id,
            "source_model": "manual",
            "source_id": -(uuid.uuid4().int % 2_000_000_000),
            "state": "issued",
            "invoice_date": date(2026, 10, 2),
            "line_ids": [(0, 0, {"taxable_amount": 1000.0, "vat_amount": 150.0})],
        }
    )
    return env, customer, invoice


def test_vds_claim_register_report(shop):
    env, _customer, invoice = shop
    Cert = env["fix.vds.certificate.received"]
    Cert.create(
        {
            "invoice_id": invoice.id,
            "certificate_no": f"R-{uuid.uuid4().hex[:6]}",
            "certificate_date": date(2026, 10, 9),
            "vds_amount": 100.0,
            "period": "1990-01",
        }
    )
    Cert.create(
        {
            "invoice_id": invoice.id,
            "certificate_no": f"R-{uuid.uuid4().hex[:6]}",
            "certificate_date": date(2026, 10, 9),
            "vds_amount": 50.0,
            "period": "1990-02",
        }
    )
    out = m20.vds_claim_register(env, date_from="1990-01-01", date_to="1990-01-31")
    assert [r["period"] for r in out["rows"]] == ["1990-01"]
    assert (out["rows"][0]["draft"], out["rows"][0]["total"]) == (100.0, 100.0)
    both = m20.vds_claim_register(env, date_from="1990-01-01", date_to="1990-12-31")
    assert both["totals"]["total"] == 150.0
    assert set(both["cols"]) <= set(both["labels"])
    assert m20.vds_claim_register(env, date_from="1980-01-01", date_to="1980-12-31")["rows"] == []
    assert "vds_unclaimed" in m20.kpis(env)


def test_closeout_action_refuses_an_open_residual(shop):
    env, _customer, invoice = shop
    with mock.patch.object(p03_generic_api, "request", FakeRequest(env)):
        res = p03_generic_api.P03GenericApiController().model_action(
            model="fix.ar.invoice", ids=[invoice.id], method="action_register_paid"
        )
    assert res["success"] is False and "never marked paid" in res["error"]
    assert invoice.state == "issued"


def test_hold_button_runs_the_toggle_workflow(shop):
    env, customer, _invoice = shop
    with mock.patch.object(p03_ar_api, "request", FakeRequest(env)):
        ctl = p03_ar_api.P03ArApiController()
        res = ctl.ar_credit_profile_save(customer_id=customer.id, credit_limit=1000, terms_days=30)
        assert res["success"], res
        profile = env["fix.credit.profile"].browse(res["id"])
        assert not profile.credit_hold
        res = ctl.ar_credit_profile_save(
            customer_id=customer.id, credit_limit=1000, terms_days=30, hold=True, hold_reason=""
        )
        assert res["success"], res
        assert profile.credit_hold and profile.hold_by == env.user and profile.hold_date
        assert profile.hold_reason == "Manual hold placed by %s" % env.user.name
        res = ctl.ar_credit_profile_save(
            customer_id=customer.id, credit_limit=1000, terms_days=30, hold=False
        )
        assert res["success"] and not profile.credit_hold and not profile.hold_reason
