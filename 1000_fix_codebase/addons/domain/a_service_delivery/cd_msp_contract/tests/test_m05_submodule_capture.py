"""M05 Function Register: every sub-module page captures its own data.

Reported 2026-11-13 from the M05 workspace: not every sub-module had a
relevant capture button. Measured against the module spec (FR-RMS-*):
  3 Metrics & Health Scoring  no button - the metrics were written by the
                              collector only (FR-RMS-010/011)
  4 Alerting Engine           "+ New MSP Ticket" - and no alert rule existed
                              anywhere, though the screen is "Alert Rules &
                              Inbox" (FR-RMS-015)
  8 MSP Service Desk          no button - its list refused "+ New"; a client
                              could not report by phone or email (FR-RMS-026)
  9 Client Reporting          no button - the monthly report is generated
                              from its contract (FR-RMS-035)
Five pages also named no form in "Forms Capturing It" though they had one.

The button rule is JavaScript (p03_workspace.js fregCreate), executed here
over the real registry by the cd_p03_portal ``registry`` fixture. Each
capture is then saved through the real controller as an MSP engineer, never
as the superuser.

``odoo_env`` (addons/conftest.py): rolled back after every test.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.tests import test_submodule_create_button as scb
from odoo.exceptions import UserError, ValidationError

from . import test_a02_p0_m05 as p0

# fixtures shared with the estate guard and the A02 P0 suite
registry = scb.registry
m5 = p0.m5
call = p0.call
_as = p0._as
_window = p0._window

# sub-module -> (the form its button opens, the button's words)
EXPECTED = {
    "1": ("M05-form-session", "Remote Session"),
    "2": ("M05-form-estate", "Managed Estate Device"),
    "3": ("M05-form-reading", "Record a Health Reading"),
    "4": ("M05-form-alert-rule", "Define an Alert Rule"),
    "5": ("M05-form-oncall", "On-Call Shift"),
    "6": ("M05-form-runbook", "Runbook"),
    "7": ("M05-form-patch", "Patch Update"),
    "8": ("M05-form-ticket", "Log a Client Ticket"),
    "9": ("M05-form-monthly-report", "Generate a Monthly Service Report"),
}


def _rows(registry):
    return {r["no"]: r for r in registry["rows"] if r["mid"] == "M05"}


@pytest.fixture(scope="module")
def screens():
    """The fragment's own screens, read by node like the registry fixture."""
    import odoo.addons.cd_p03_portal as portal

    src = Path(portal.__file__).parent / "static" / "src" / "a02" / "m05.js"
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the M05 fragment")
    probe = (
        "import { pathToFileURL } from 'node:url';\n"
        "import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';\n"
        "import { tmpdir } from 'node:os';\n"
        "import { join } from 'node:path';\n"
        "const dir = mkdtempSync(join(tmpdir(), 'm05cap'));\n"
        "const file = join(dir, 'm05.mjs');\n"
        "writeFileSync(file, readFileSync(process.argv[1], 'utf-8'));\n"
        "const M = await import(pathToFileURL(file).href);\n"
        "console.log(JSON.stringify({ screens: M.SCREENS, module: M.MODULE }));\n"
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary, inline probe, our file
        [node, "--input-type=module", "-e", probe, str(src)],
        capture_output=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


# --- every page offers its capture -------------------------------------------


def test_every_m05_submodule_offers_its_capture(registry):
    rows = _rows(registry)
    assert len(rows) == 10
    got = {
        no: ((r["create"] or {}).get("screen"), (r["create"] or {}).get("label"))
        for no, r in rows.items()
        if no != "10"
    }
    assert got == EXPECTED
    # 10 Onboarding Projects lists the MSP contract itself: the module's button
    assert rows["10"]["create"] == {"module": True}
    assert all(r["formKind"] == "model_form" for no, r in rows.items() if no != "10")


def test_every_page_names_the_forms_that_capture_it(registry):
    empty = [no for no, r in _rows(registry).items() if not r["forms"]]
    assert not empty, "pages naming no form: %s" % empty


def test_every_capture_form_shows_fields_of_its_model(screens, odoo_env):
    """A form field the model lacks renders empty and can never be saved."""
    bad = []
    for sid, cfg in screens["screens"].items():
        if cfg.get("kind") not in ("model_form", "model_list"):
            continue
        model_fields = odoo_env[cfg["model"]]._fields
        names = list(cfg.get("cols") or [])
        for section in cfg.get("sections") or []:
            names += [f["name"] for f in section["fields"]]
        names += list((cfg.get("pickRecord") or {}).get("cols") or [])
        bad += ["%s.%s" % (sid, n) for n in names if n not in model_fields]
        for kwarg_field in ((cfg.get("saveAction") or {}).get("kwargs") or {}).values():
            if kwarg_field not in model_fields:
                bad.append("%s saveAction %s" % (sid, kwarg_field))
    assert not bad, "\n  ".join(bad)


def test_a_ticket_logged_on_the_desk_lands_on_the_desk(screens):
    """The desk lists client reports and ticketed alerts; the form starts as a
    phone report, so the ticket is on the page it was logged from."""
    desk = screens["screens"]["M05-tickets"]
    assert desk.get("create") is not False
    assert desk["domain"] == [
        "|",
        ["state", "in", ["ticketed", "resolved"]],
        ["source", "!=", "monitoring"],
    ]
    source = next(
        f
        for s in screens["screens"]["M05-form-ticket"]["sections"]
        for f in s["fields"]
        if f["name"] == "source"
    )
    assert source["value"] == "phone" and source["required"]


# --- each capture saves through the workspace, as an MSP engineer ------------


def _rule(m5, user=None, **vals):
    base = {
        "name": "CPU above 90",
        "metric": "cpu_utilization_pct",
        "operator": "above",
        "threshold": 90.0,
        "severity": "major",
        "msp_contract_id": m5.msp.id,
        "operating_unit_id": m5.ou.id,
    }
    base.update(vals)
    return _as(m5.env["fix.msp.alert.rule"], user or m5.eng).create(base)


def _reading(m5, call, user=None, **kwargs):
    return call(
        m5.env(user=(user or m5.eng).id),
        "model_action",
        model="fix.monitored.asset",
        ids=[m5.asset.id],
        method="action_record_reading",
        kwargs=kwargs,
    )


def _alerts(m5):
    return m5.env["fix.msp.alert"].search([("asset_id", "=", m5.asset.id)])


def test_an_alert_rule_is_defined_from_the_workspace(m5, call):
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.alert.rule",
        record_id=False,
        values={
            "name": "Disk below 10 GB",
            "metric": "disk_free_gb",
            "operator": "below",
            "threshold": 10,
            "severity": "minor",
            "msp_contract_id": m5.msp.id,
            "operating_unit_id": m5.ou.id,
        },
    )
    assert "error" not in out, out
    rule = m5.env["fix.msp.alert.rule"].search([("name", "=", "Disk below 10 GB")])
    assert rule.metric == "disk_free_gb" and rule.msp_contract_id == m5.msp


def test_a_percentage_rule_cannot_exceed_100(m5):
    with pytest.raises(ValidationError, match="at most 100"):
        _rule(m5, threshold=120)


def test_a_plain_user_cannot_define_a_rule(m5):
    from odoo.exceptions import AccessError

    with pytest.raises(AccessError):
        _rule(m5, user=m5.plain)


def test_a_reading_that_crosses_a_rule_raises_one_alert(m5, call):
    rule = _rule(m5)
    out = _reading(m5, call, cpu=97, ram=40, disk_free_gb=120)
    assert out.get("success"), out
    assert "1 alert" in out["result"]["warning"]
    alert = _alerts(m5)
    assert len(alert) == 1
    assert (alert.rule_id, alert.severity, alert.source) == (rule, "major", "monitoring")
    assert "CPU load" in alert.message and "97" in alert.message
    m5.asset.invalidate_recordset()
    assert m5.asset.cpu_utilization_pct == 97.0
    assert m5.asset.last_reading_by_id == m5.eng and m5.asset.last_seen

    # still high: the open alert is not repeated (spec T-10: one, not fifty)
    out = _reading(m5, call, cpu=99)
    assert out["result"].get("note"), out
    assert len(_alerts(m5)) == 1


def test_a_reading_below_the_threshold_raises_nothing(m5, call):
    _rule(m5)
    out = _reading(m5, call, cpu=35)
    assert out["result"]["note"] == "Reading recorded. No threshold crossed."
    assert not _alerts(m5)


def test_a_rule_of_another_contract_does_not_watch_this_asset(m5, call):
    _rule(m5, msp_contract_id=m5.other.id)
    _reading(m5, call, cpu=99)
    assert not _alerts(m5)
    # an unscoped rule watches every contract
    _rule(m5, msp_contract_id=False, name="Any estate: CPU above 90")
    _reading(m5, call, cpu=98)
    assert len(_alerts(m5)) == 1


def test_going_offline_raises_the_collectors_alert(m5, call):
    out = _reading(m5, call, health="offline")
    assert out.get("success"), out
    alert = _alerts(m5)
    assert len(alert) == 1 and alert.severity == "major" and not alert.rule_id
    assert m5.asset.health == "offline"


def test_an_open_maintenance_window_suppresses_the_reading_alerts(m5, call):
    _rule(m5)
    win = _window(m5, m5.cm)
    _as(win, m5.cab).action_approve()
    out = _reading(m5, call, cpu=99, health="degraded")
    assert "maintenance window" in out["result"]["warning"]
    assert not _alerts(m5)


def test_an_impossible_reading_is_refused(m5, call):
    out = _reading(m5, call, ram=140)
    assert not out.get("success") and "not a possible reading" in out["error"]
    out = _reading(m5, call)
    assert not out.get("success") and "at least one reading" in out["error"]


def test_only_an_msp_engineer_records_a_reading(m5):
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(m5.asset, m5.cab).action_record_reading(cpu=10)


def test_the_metrics_are_not_typed_through_the_generic_write(m5, call):
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.monitored.asset",
        record_id=m5.asset.id,
        values={"cpu_utilization_pct": 5},
    )
    assert out.get("error"), out


def test_a_client_ticket_is_logged_on_the_desk(m5, call, screens):
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.alert",
        record_id=False,
        values={
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "source": "phone",
            "severity": "minor",
            "message": "Client reports the shared printer is not printing",
        },
    )
    assert "error" not in out, out
    ticket = _alerts(m5)
    assert ticket.source == "phone" and ticket.state == "new"
    desk = m5.env["fix.msp.alert"].search(screens["screens"]["M05-tickets"]["domain"])
    assert ticket in desk


def test_a_ticket_on_another_contracts_asset_is_refused(m5):
    with pytest.raises(ValidationError, match="not covered by MSP contract"):
        _as(m5.env["fix.msp.alert"], m5.eng).create(
            {
                "msp_contract_id": m5.msp.id,
                "asset_id": m5.other_asset.id,
                "source": "email",
                "message": "wrong client's endpoint",
            }
        )


def test_the_rule_link_cannot_be_typed(m5):
    rule = _rule(m5)
    with pytest.raises(UserError):
        _as(m5.env["fix.msp.alert"], m5.eng).create(
            {
                "msp_contract_id": m5.msp.id,
                "asset_id": m5.asset.id,
                "message": "forged",
                "rule_id": rule.id,
            }
        )


def test_the_monthly_report_is_generated_once_per_month(m5, call):
    def generate():
        return call(
            m5.env(user=m5.eng.id),
            "model_action",
            model="fix.msp.contract",
            ids=[m5.msp.id],
            method="action_generate_monthly_report",
        )

    out = generate()
    assert out.get("success"), out
    label = (fields.Date.today().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    reports = m5.env["fix.msp.service.report"].search([("msp_contract_id", "=", m5.msp.id)])
    assert reports.mapped("period_label") == [label]
    again = generate()
    assert not again.get("success") and "already exists" in again["error"]
    assert m5.env["fix.msp.service.report"].search_count([("msp_contract_id", "=", m5.msp.id)]) == 1
