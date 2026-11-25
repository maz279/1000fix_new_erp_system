"""M30 capture audit (2026-11-14): the captures the six sub-module pages now
offer, driven through /p03/model/form, /p03/model/write and /p03/model/action
as NON-ADMIN users (Platform Admins who are not system administrators) with
the fields m30.js posts. The superuser is trusted by the model guards and
would hide a gap.

  * Every chip form of every page opens blank for its actor.
  * Config & Flags: a system administrator registers a key; a Platform Admin
    proposes a change citing an approved change record; a SECOND Platform
    Admin applies it; it rolls back in one action (BRU-ADM-02, FR-ADM-015/018/019).
  * Config & Flags: a Platform Admin registers a real scheduled action with an
    owner, duration and impact (BRU-ADM-11), and a stale one shows as missed (T-09).
  * Audit: restore tests are evidence that cannot be rewritten (BRU-ADM-17);
    a DR drill is signed off by a second person (BRU-ADM-18).
  * A plain employee can read none of the new registers.
"""

from __future__ import annotations

import datetime
import re
import types
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

JS = Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src" / "a12" / "m30.js"
PA = "cd_entity_config.group_platform_admin"
SYSTEM = "base.group_system"
REFUSED = (UserError, ValidationError, AccessError)


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "email": "%s@m30cap.test" % login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.plain = _user(env, "m30cap_plain")
    x.pa1 = _user(env, "m30cap_pa1", [PA])
    x.pa2 = _user(env, "m30cap_pa2", [PA])
    x.sys = _user(env, "m30cap_sys", [SYSTEM, PA])
    assert not x.pa1.has_group(SYSTEM), "the Platform Admin under test must not be a system admin"
    return x


@pytest.fixture
def p03(odoo_env):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()

    def ep(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    old = getattr(g, "request", None)

    def call(user, name, **kw):
        g.request = types.SimpleNamespace(env=odoo_env(user=user.id))
        return ep(name)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            write=lambda user, **kw: call(user, "model_write", **kw),
            action=lambda user, record_id=None, **kw: call(
                user, "model_action", ids=[record_id], **kw
            ),
            records=lambda user, **kw: call(user, "model_records", **kw),
            form=lambda user, **kw: call(user, "model_form", **kw),
        )
    finally:
        g.request = old


def _form_fields(screen):
    """The field list one m30.js form posts (its block, up to the next screen)."""
    js = JS.read_text(encoding="utf-8")
    start = js.index("'%s': {" % screen)
    nxt = re.compile(r"^  '(M30[-:][\w-]+)': \{", re.M).search(js, start + 10)
    block = js[start : nxt.start() if nxt else len(js)]
    return [{"name": n} for n in re.findall(r"name: '(\w+)'", block)]


def _err(res):
    return res.get("error") or (res.get("success") is False and "failed")


# ---------------------------------------------------------------- every chip opens
CHIPS = {
    "M30-form-branch": ("fix.branch", "pa1"),
    "M30-form-zone": ("fix.zone", "pa1"),
    "M30-form-entity": ("fix.entity", "pa1"),
    "M30-form-flag": ("fix.feature.flag", "pa1"),
    "M30-form-config-change": ("fix.config.change", "pa1"),
    "M30-form-param": ("fix.config.parameter", "sys"),
    "M30-form-job": ("fix.scheduled.job", "pa1"),
    "M30-form-env": ("fix.platform.environment", "pa1"),
    "M30-form-calendar": ("fix.working.calendar", "pa1"),
    "M30-form-holiday": ("fix.working.calendar.holiday", "pa1"),
    "M30-form-announcement": ("fix.platform.announcement", "pa1"),
    "M30-form-notif": ("fix.notification.config", "pa1"),
    "M30-form-dofa-ladder": ("fix.dofa.ladder", "pa1"),
    "M30-form-dofa-band": ("fix.dofa.threshold", "pa1"),
    "M30-form-release": ("fix.platform.release", "pa1"),
    "M30-form-backup": ("fix.backup.verification", "pa1"),
    "M30-form-drill": ("fix.dr.drill", "pa1"),
}


@pytest.mark.parametrize("screen", sorted(CHIPS))
def test_every_page_capture_opens_blank_for_its_actor(c, p03, screen):
    model, who = CHIPS[screen]
    got = p03.form(getattr(c, who), model=model, fields=_form_fields(screen))
    assert not got.get("error"), (screen, got)


@pytest.mark.parametrize(
    "model",
    [
        "fix.scheduled.job",
        "fix.config.parameter",
        "fix.config.change",
        "fix.backup.verification",
        "fix.dr.drill",
    ],
)
def test_a_plain_employee_reads_none_of_the_new_registers(c, p03, model):
    got = p03.records(c.plain, model=model, cols=["id"])
    assert got.get("error"), (model, got)
    assert not c.env[model].with_user(c.plain).has_access("read")


# ---------------------------------------------------------------- 3 Config & Flags
KEY = "fix_m30cap.batch_size"


def _param(c, p03, **extra):
    vals = {
        "key": KEY,
        "description": "Rows per import batch",
        "value_type": "integer",
        "min_value": 10,
        "max_value": 5000,
        "business_impact": "Imports time out if it is too large",
    }
    vals.update(extra)
    res = p03.write(c.sys, model="fix.config.parameter", values=vals)
    assert not _err(res), res
    c.env["ir.config_parameter"].sudo().set_param(KEY, "100")
    return c.env["fix.config.parameter"].sudo().browse(res["id"])


def test_only_a_system_administrator_registers_a_key(c, p03):
    res = p03.write(
        c.pa1,
        model="fix.config.parameter",
        values={"key": "fix_m30cap.other", "description": "x", "business_impact": "y"},
    )
    assert _err(res), res
    assert not c.env["fix.config.parameter"].sudo().search([("key", "=", "fix_m30cap.other")])


def test_a_credential_key_never_enters_the_registry(c, p03):
    res = p03.write(
        c.sys,
        model="fix.config.parameter",
        values={
            "key": "cd_storefront.gateway_secret.bkash",
            "description": "x",
            "business_impact": "y",
        },
    )
    assert _err(res) and "credential" in str(res), res


def test_a_change_is_proposed_applied_by_a_second_person_and_rolled_back(c, p03):
    param = _param(c, p03)
    icp = c.env["ir.config_parameter"].sudo()
    # FR-ADM-019: an invalid value is refused at the point of change
    bad = p03.write(
        c.pa1,
        model="fix.config.change",
        values={
            "parameter_id": param.id,
            "new_value": "99999",
            "reason": "x",
            "change_reference": "CHG-1",
        },
    )
    assert _err(bad) and "above" in str(bad), bad
    res = p03.write(
        c.pa1,
        model="fix.config.change",
        values={
            "parameter_id": param.id,
            "new_value": "250",
            "reason": "Large branch imports",
            "change_reference": "CHG-2026-0042",
            # typed stamps are dropped by the whitelist or refused by the guard
            "state": "applied",
            "previous_value": "1",
        },
    )
    assert not _err(res), res
    change = c.env["fix.config.change"].sudo().browse(res["id"])
    assert change.state == "proposed" and change.proposed_by_id == c.pa1
    assert change.name.startswith("CFG/")
    assert icp.get_param(KEY) == "100", "a proposal changes nothing"

    # BRU-ADM-02: the proposer cannot apply their own change
    own = p03.action(c.pa1, model="fix.config.change", record_id=change.id, method="action_apply")
    assert _err(own), own
    assert change.state == "proposed"

    got = p03.action(c.pa2, model="fix.config.change", record_id=change.id, method="action_apply")
    assert not _err(got), got
    assert change.state == "applied" and change.applied_by_id == c.pa2
    assert change.previous_value == "100"
    assert icp.get_param(KEY) == "250", "effective at once, no restart (T-14)"

    # an applied change is frozen
    edit = p03.write(
        c.pa1, model="fix.config.change", record_id=change.id, values={"new_value": "300"}
    )
    assert _err(edit), edit

    # the audit trail carries the key and number, never the value
    rows = (
        c.env["fix.security.audit"]
        .sudo()
        .search([("object_ref", "=", "fix.config.change,%d" % change.id)])
        if "fix.security.audit" in c.env
        else []
    )
    for row in rows:
        assert "250" not in row.detail and "100" not in row.detail

    # FR-ADM-018: one action rolls it back
    back = p03.action(
        c.pa1,
        model="fix.config.change",
        record_id=change.id,
        method="action_rollback",
        kwargs={"reason": "Imports slowed down"},
    )
    assert not _err(back), back
    assert change.state == "rolled_back" and icp.get_param(KEY) == "100"


def test_a_value_changed_outside_the_register_is_not_rolled_back_over(c, p03):
    param = _param(c, p03)
    res = p03.write(
        c.pa1,
        model="fix.config.change",
        values={
            "parameter_id": param.id,
            "new_value": "400",
            "reason": "x",
            "change_reference": "CHG-3",
        },
    )
    change = c.env["fix.config.change"].sudo().browse(res["id"])
    p03.action(c.pa2, model="fix.config.change", record_id=change.id, method="action_apply")
    c.env["ir.config_parameter"].sudo().set_param(KEY, "777")
    got = p03.action(
        c.pa1,
        model="fix.config.change",
        record_id=change.id,
        method="action_rollback",
        kwargs={"reason": "x"},
    )
    assert _err(got), got
    assert c.env["ir.config_parameter"].sudo().get_param(KEY) == "777"


def test_a_plain_employee_cannot_propose_a_change(c, p03):
    param = _param(c, p03)
    res = p03.write(
        c.plain,
        model="fix.config.change",
        values={
            "parameter_id": param.id,
            "new_value": "200",
            "reason": "x",
            "change_reference": "CHG-4",
        },
    )
    assert _err(res), res


def _cron(c):
    return c.env["ir.cron"].sudo().search([("active", "=", True)], limit=1)


def test_a_platform_admin_registers_a_scheduled_job(c, p03):
    cron = _cron(c)
    c.env["fix.scheduled.job"].sudo().search([("cron_id", "=", cron.id)]).unlink()
    res = p03.write(
        c.pa1,
        model="fix.scheduled.job",
        values={
            "cron_id": cron.id,
            "owner_id": c.pa2.id,
            "expected_duration_min": 10,
            "failure_impact": "high",
            "owning_module": "M30",
        },
    )
    assert not _err(res), res
    job = c.env["fix.scheduled.job"].sudo().browse(res["id"])
    assert job.name == cron.name, "the job takes the action name when none is typed"
    assert job.schedule and job.cron_active
    # T-09: an enabled action whose next call is long past is a missed run
    cron.write({"nextcall": fields.Datetime.now() - datetime.timedelta(hours=3)})
    job.invalidate_recordset()
    assert job.run_state == "missed"
    # the same action cannot be registered twice
    dup = p03.write(
        c.pa1,
        model="fix.scheduled.job",
        values={
            "cron_id": cron.id,
            "owner_id": c.pa2.id,
            "expected_duration_min": 5,
            "failure_impact": "low",
        },
    )
    assert _err(dup), dup


def test_registered_jobs_feed_the_health_console_and_the_kpis(c, p03):
    import odoo.addons.cd_p03_portal.controllers.a12.m30 as m30

    pack = m30.platform_health(c.env(user=c.pa1.id))
    signals = {r["signal"] for r in pack["rows"]}
    assert "Active jobs with no registration (BRU-ADM-11)" in signals
    assert "DR drills signed off in 12 months (2 required, NFR-051)" in signals
    tiles = m30.kpis(c.env(user=c.pa1.id))
    assert "config_changes_pending" in tiles and "jobs_missed" in tiles
    plain = m30.kpis(c.env(user=c.plain.id))
    assert "config_changes_pending" not in plain and "branches" in plain


# ---------------------------------------------------------------- 6 Audit
def test_a_restore_test_is_evidence_that_is_not_rewritten(c, p03):
    now = fields.Datetime.now()
    res = p03.write(
        c.pa1,
        model="fix.backup.verification",
        values={
            "backup_ref": "pg_dump fix_real 2026-11-13",
            "backup_type": "weekly",
            "taken_at": fields.Datetime.to_string(now - datetime.timedelta(hours=5)),
            "restore_tested_at": fields.Datetime.to_string(now),
            "restore_duration_min": 12,
            "result": "pass",
            "evidence": "restore log RST-1",
            "tested_by_id": c.pa2.id,
        },
    )
    assert not _err(res), res
    test = c.env["fix.backup.verification"].sudo().browse(res["id"])
    assert test.tested_by_id == c.pa1 and test.name.startswith("RST/")
    note = p03.write(
        c.pa1,
        model="fix.backup.verification",
        record_id=test.id,
        values={"note": "checked row counts"},
    )
    assert not _err(note), note
    rewrite = p03.write(
        c.pa1, model="fix.backup.verification", record_id=test.id, values={"result": "fail"}
    )
    assert _err(rewrite), rewrite
    assert test.result == "pass"
    # the model refuses it too, not only the form endpoint's locked-field check
    with pytest.raises(UserError), c.env.cr.savepoint():
        test.with_user(c.pa1).write({"result": "fail"})
    assert test.result == "pass"
    # a restore cannot predate its backup
    bad = p03.write(
        c.pa1,
        model="fix.backup.verification",
        values={
            "backup_ref": "x",
            "backup_type": "daily",
            "taken_at": fields.Datetime.to_string(now),
            "restore_tested_at": fields.Datetime.to_string(now - datetime.timedelta(days=1)),
            "result": "pass",
            "evidence": "x",
        },
    )
    assert _err(bad), bad


def _drill(c, p03, user, **extra):
    vals = {
        "drill_date": str(fields.Date.context_today(c.env["fix.dr.drill"].with_user(user))),
        "scenario": "failover",
        "scope": "fix_real database and filestore",
        "rpo_achieved_min": 10,
        "rto_achieved_min": 95,
    }
    vals.update(extra)
    res = p03.write(user, model="fix.dr.drill", values=vals)
    assert not _err(res), res
    return c.env["fix.dr.drill"].sudo().browse(res["id"])


def test_a_dr_drill_is_signed_off_by_a_second_person_and_frozen(c, p03):
    drill = _drill(c, p03, c.pa1)
    assert drill.rpo_met and drill.rto_met and drill.state == "recorded"
    own = p03.action(c.pa1, model="fix.dr.drill", record_id=drill.id, method="action_sign_off")
    assert _err(own), own
    got = p03.action(c.pa2, model="fix.dr.drill", record_id=drill.id, method="action_sign_off")
    assert not _err(got), got
    assert drill.state == "signed_off" and drill.signed_off_by_id == c.pa2
    edit = p03.write(
        c.pa1, model="fix.dr.drill", record_id=drill.id, values={"rto_achieved_min": 1}
    )
    assert _err(edit), edit


def test_a_missed_target_needs_its_issues_before_sign_off(c, p03):
    drill = _drill(c, p03, c.pa1, rto_achieved_min=180)
    assert not drill.rto_met
    got = p03.action(c.pa2, model="fix.dr.drill", record_id=drill.id, method="action_sign_off")
    assert _err(got), got
    p03.write(
        c.pa1,
        model="fix.dr.drill",
        record_id=drill.id,
        values={"issues_found": "Filestore sync lagged 70 minutes"},
    )
    got = p03.action(c.pa2, model="fix.dr.drill", record_id=drill.id, method="action_sign_off")
    assert not _err(got), got
