"""M30 capture audit, second pass (2026-11-19): the records the six pages now
capture, driven through /p03/model/form, /p03/model/write and /p03/model/action
as NON-ADMIN Platform Admins (not system administrators) with the fields m30.js
posts. The superuser is trusted by the model guards and would hide a gap.

  * Every new chip, including the ones that open another module's form (cost
    centre, business line, shift pattern, zone boundary), opens blank and saves
    for a Platform Admin.
  * Branch Master: a capability profile limits the repair level a workshop at
    that branch may take (FR-ADM-004); a branch without one is not limited.
  * Entity Structure: an organisation change is dated forward only, approved by
    a second person, applied on its date and keeps the structure before it
    (FR-ADM-010/011, BRU-ADM-08).
  * Config & Flags: a freeze blocks applying changes and turning a flag on but
    not the kill switch (BRU-ADM-22); the emergency path is one person, loud,
    and reverted without its change record (BRU-ADM-04); copyleft licences need
    a compliance note (FR-ADM-021).
  * Announcements: maintenance windows stay in the night band, under the
    monthly cap, and start only once announced 72 hours ahead (BRU-ADM-19).
  * Audit: an alert needs a live runbook (BRU-ADM-14); a capacity review below
    20% headroom must decide, and its measurement is evidence (OPS-08).
"""

from __future__ import annotations

import datetime
import re
import types
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

SRC = Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src"
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
                "email": "%s@m30cap2.test" % login,
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
    x.plain = _user(env, "m30cap2_plain")
    x.pa1 = _user(env, "m30cap2_pa1", [PA])
    x.pa2 = _user(env, "m30cap2_pa2", [PA])
    assert not x.pa1.has_group(SYSTEM)
    x.branch = env["fix.branch"].search([("active", "=", True)], limit=1)
    if not x.branch:
        # The clean fix_test carries no demo branch (the old assertion assumed
        # a seeded database); the fixture builds its own spine. fix.entity is
        # UNIQUE per company, so reuse the company's entity when present.
        company = env.company
        entity = env["fix.entity"].search([("company_id", "=", company.id)], limit=1)
        if not entity:
            entity = env["fix.entity"].create(
                {"code": "M30C2", "legal_name": "M30 Capture Entity", "company_id": company.id}
            )
        ou = env["operating.unit"].search([], limit=1)
        x.branch = env["fix.branch"].create(
            {
                "name": "M30 Capture Branch",
                "code": "M30C2",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
    # A Platform Admin administers the branches of every unit they are given;
    # without the branch's unit the OU record rule hides it (as it should).
    for user in (x.pa1, x.pa2):
        user.assigned_operating_unit_ids = [(4, x.branch.operating_unit_id.id)]
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
    """The fields one workspace form posts, from whichever area file holds it."""
    for js_path in SRC.glob("a*/m*.js"):
        js = js_path.read_text(encoding="utf-8")
        key = "'%s': {" % screen
        if key not in js:
            continue
        start = js.index(key)
        nxt = re.compile(r"^  '(M\d\d[-:][\w-]+)': \{", re.M).search(js, start + 10)
        block = js[start : nxt.start() if nxt else len(js)]
        return [{"name": n} for n in re.findall(r"name: '(\w+)'", block)]
    raise AssertionError("no form %s" % screen)


def _err(res):
    return res.get("error") or (res.get("success") is False and "failed")


def _ok(res):
    assert not _err(res), res
    return res.get("id", res)


def _local_str(local_dt):
    """The form posts the user's wall clock (Dhaka); the endpoint stores UTC."""
    return fields.Datetime.to_string(local_dt)


# ------------------------------------------------------------ every chip opens
CHIPS = {
    "M30-form-capability": "fix.branch.capability",
    "M30-form-org-change": "fix.org.change",
    "M30-form-freeze": "fix.change.freeze",
    "M30-form-licence": "fix.component.licence",
    "M30-form-maintenance": "fix.maintenance.window",
    "M30-form-runbook": "fix.runbook",
    "M30-form-alert": "fix.platform.alert",
    "M30-form-capacity": "fix.capacity.metric",
    "M02-form-zone": "fix.geofence",
    "M54-form-centre": "fix.cost.centre",
    "M54-form-bline": "fix.business.line",
    "M55-form-shift": "fix.shift.template",
}


@pytest.mark.parametrize("screen", sorted(CHIPS))
def test_every_new_capture_opens_blank_for_a_platform_admin(c, p03, screen):
    got = p03.form(c.pa1, model=CHIPS[screen], fields=_form_fields(screen))
    assert not got.get("error"), (screen, got)


def test_a_platform_admin_saves_the_foreign_masters_from_entity_structure(c, p03):
    centre = _ok(
        p03.write(
            c.pa1,
            model="fix.cost.centre",
            values={
                "code": "M30CAP2-CC",
                "name": "Platform operations",
                "owner_id": c.pa1.id,
                "centre_type": "absorbing",
                "branch_id": c.branch.id,
            },
        )
    )
    assert c.env["fix.cost.centre"].browse(centre).owner_id == c.pa1
    line = _ok(
        p03.write(c.pa1, model="fix.business.line", values={"code": "BL-97", "name": "M30 line"})
    )
    assert c.env["fix.business.line"].browse(line).exists()
    shift = _ok(
        p03.write(
            c.pa1,
            model="fix.shift.template",
            values={"name": "M30 night desk", "start_hour": 22.0, "end_hour": 6.0},
        )
    )
    assert c.env["fix.shift.template"].browse(shift).exists()
    # a plain employee still cannot
    refused = p03.write(
        c.plain,
        model="fix.cost.centre",
        values={"code": "M30X", "name": "x", "owner_id": c.plain.id},
    )
    assert _err(refused), refused


@pytest.mark.parametrize(
    "model",
    ["fix.org.change", "fix.component.licence", "fix.platform.alert", "fix.capacity.metric"],
)
def test_a_plain_employee_reads_none_of_the_private_registers(c, p03, model):
    got = p03.records(c.plain, model=model, cols=["id"])
    assert got.get("error"), (model, got)


@pytest.mark.parametrize(
    "model", ["fix.branch.capability", "fix.change.freeze", "fix.maintenance.window", "fix.runbook"]
)
def test_a_plain_employee_reads_but_never_writes_operational_registers(c, p03, model):
    assert c.env[model].with_user(c.plain).has_access("read")
    assert not c.env[model].with_user(c.plain).has_access("create")


# ------------------------------------------------------------- 1 Branch Master
def test_a_capability_profile_limits_the_workshop_of_its_branch(c, p03):
    workshop = c.env["fix.workshop"].create(
        {
            "code": "WS-M30C2",
            "name": "M30 capability depot",
            "name_bn": "এম৩০ ডিপো",
            "branch_id": c.branch.id,
        }
    )
    job = c.env["fix.workshop.job"].create(
        {"workshop_id": workshop.id, "fault_description": "Board dead", "repair_level": "l1"}
    )
    # no profile yet: any level is accepted
    job.write({"repair_level": "l3"})
    job.write({"repair_level": "l1"})

    _ok(
        p03.write(
            c.pa1,
            model="fix.branch.capability",
            values={
                "branch_id": c.branch.id,
                "service_kind": "carry_in",
                "max_repair_level": "l2",
                "effective_from": fields.Date.to_string(datetime.date.today()),
            },
        )
    )
    job.write({"repair_level": "l2"})
    with pytest.raises(ValidationError, match="level 2"):
        job.write({"repair_level": "l3"})
    # the same service twice for one category is refused
    dup = p03.write(
        c.pa1,
        model="fix.branch.capability",
        values={"branch_id": c.branch.id, "service_kind": "carry_in", "max_repair_level": "l3"},
    )
    assert _err(dup), dup
    # a plain employee cannot widen the profile
    widen = p03.write(
        c.plain,
        model="fix.branch.capability",
        values={"branch_id": c.branch.id, "service_kind": "onsite", "max_repair_level": "l3"},
    )
    assert _err(widen), widen


# ---------------------------------------------------------- 2 Entity Structure
def test_an_org_change_is_dated_forward_approved_by_a_second_person_and_kept(c, p03):
    today = datetime.date.today()
    old_name = c.branch.name
    back = p03.write(
        c.pa1,
        model="fix.org.change",
        values={
            "branch_id": c.branch.id,
            "change_type": "rename",
            "new_name": old_name + " (M30)",
            "effective_from": fields.Date.to_string(today - datetime.timedelta(days=1)),
            "reason": "rebrand",
        },
    )
    assert _err(back) and "today or later" in str(back), back
    rid = _ok(
        p03.write(
            c.pa1,
            model="fix.org.change",
            values={
                "branch_id": c.branch.id,
                "change_type": "rename",
                "new_name": old_name + " (M30)",
                "effective_from": fields.Date.to_string(today),
                "reason": "rebrand",
                "state": "applied",  # typed stamps are dropped or refused
            },
        )
    )
    change = c.env["fix.org.change"].browse(rid)
    assert change.state == "proposed" and change.name.startswith("ORG/")
    assert c.branch.name == old_name
    own = p03.action(c.pa1, model="fix.org.change", record_id=rid, method="action_approve")
    assert _err(own), own
    _ok(p03.action(c.pa2, model="fix.org.change", record_id=rid, method="action_approve"))
    assert change.state == "applied" and change.approved_by_id == c.pa2
    assert c.branch.name == old_name + " (M30)"
    assert change.previous_state == "Name: %s" % old_name
    # history is kept
    edit = p03.write(c.pa1, model="fix.org.change", record_id=rid, values={"reason": "x"})
    assert _err(edit), edit
    with pytest.raises(REFUSED):
        change.with_user(c.pa1).unlink()


def test_a_future_org_change_waits_for_its_date(c, p03):
    zones = c.env["fix.zone"].search([("id", "!=", c.branch.zone_id.id)], limit=1)
    if not zones:
        zones = c.env["fix.zone"].create({"name": "M30 test zone", "code": "M30Z"})
    rid = _ok(
        p03.write(
            c.pa1,
            model="fix.org.change",
            values={
                "branch_id": c.branch.id,
                "change_type": "zone_move",
                "new_zone_id": zones.id,
                "effective_from": fields.Date.to_string(
                    datetime.date.today() + datetime.timedelta(days=10)
                ),
                "reason": "rezoning",
            },
        )
    )
    change = c.env["fix.org.change"].browse(rid)
    _ok(p03.action(c.pa2, model="fix.org.change", record_id=rid, method="action_approve"))
    assert change.state == "approved" and c.branch.zone_id != zones
    c.env["fix.org.change"].cron_apply_due_changes()
    assert change.state == "approved", "not before its date"
    c.env.cr.execute(
        "UPDATE fix_org_change SET effective_from = CURRENT_DATE WHERE id = %s", (rid,)
    )
    change.invalidate_recordset()
    c.env["fix.org.change"].cron_apply_due_changes()
    assert change.state == "applied" and c.branch.zone_id == zones


# ---------------------------------------------------------- 3 Config & Flags
KEY = "fix_m30cap2.batch_size"


def _param(c):
    param = (
        c.env["fix.config.parameter"]
        .sudo()
        .create(
            {
                "key": KEY,
                "description": "Rows per batch",
                "value_type": "integer",
                "min_value": 1,
                "max_value": 1000,
                "business_impact": "Imports time out",
            }
        )
    )
    c.env["ir.config_parameter"].sudo().set_param(KEY, "100")
    return param


def _freeze(c, p03, scope="all"):
    now = fields.Datetime.now()
    return _ok(
        p03.write(
            c.pa1,
            model="fix.change.freeze",
            values={
                "name": "M30 test freeze",
                "date_from": fields.Datetime.to_string(now - datetime.timedelta(hours=1)),
                "date_to": fields.Datetime.to_string(now + datetime.timedelta(days=2)),
                "scope": scope,
                "reason": "Eid sales",
            },
        )
    )


def test_a_routine_change_must_cite_its_change_record(c, p03):
    param = _param(c)
    res = p03.write(
        c.pa1,
        model="fix.config.change",
        values={"parameter_id": param.id, "new_value": "200", "reason": "x"},
    )
    assert _err(res) and "change record" in str(res), res


def test_a_freeze_blocks_apply_but_not_the_emergency_path(c, p03):
    param = _param(c)
    icp = c.env["ir.config_parameter"].sudo()
    routine = _ok(
        p03.write(
            c.pa1,
            model="fix.config.change",
            values={
                "parameter_id": param.id,
                "new_value": "200",
                "reason": "x",
                "change_reference": "CHG-1",
            },
        )
    )
    fid = _freeze(c, p03)
    blocked = p03.action(c.pa2, model="fix.config.change", record_id=routine, method="action_apply")
    assert _err(blocked) and "freeze" in str(blocked), blocked
    assert icp.get_param(KEY) == "100"
    # a started freeze is not edited, only lifted with a reason
    edit = p03.write(c.pa1, model="fix.change.freeze", record_id=fid, values={"name": "y"})
    assert _err(edit), edit
    p03.action(
        c.pa2,
        model="fix.config.change",
        record_id=routine,
        method="action_reject",
        kwargs={"reason": "superseded"},
    )

    emergency = _ok(
        p03.write(
            c.pa1,
            model="fix.config.change",
            values={
                "parameter_id": param.id,
                "new_value": "300",
                "reason": "outage",
                "emergency": True,
            },
        )
    )
    rec = c.env["fix.config.change"].browse(emergency)
    # an emergency change is not applied through the routine action
    assert _err(
        p03.action(c.pa2, model="fix.config.change", record_id=emergency, method="action_apply")
    )
    _ok(
        p03.action(
            c.pa1, model="fix.config.change", record_id=emergency, method="action_apply_emergency"
        )
    )
    assert rec.state == "applied" and icp.get_param(KEY) == "300"
    assert rec.regularise_by and not rec.regularised_on
    loud = rec.message_ids.filtered(lambda m: "EMERGENCY" in (m.body or ""))
    assert loud and c.pa2.partner_id in loud.partner_ids, "every Platform Admin is told"

    _ok(
        p03.action(
            c.pa1,
            model="fix.config.change",
            record_id=emergency,
            method="action_regularise",
            kwargs={"reference": "CHG-EMG-7"},
        )
    )
    assert rec.change_reference == "CHG-EMG-7" and rec.regularised_on
    # lifted early with a reason
    assert _err(p03.action(c.pa2, model="fix.change.freeze", record_id=fid, method="action_lift"))
    _ok(
        p03.action(
            c.pa2,
            model="fix.change.freeze",
            record_id=fid,
            method="action_lift",
            kwargs={"reason": "sales ended"},
        )
    )
    assert c.env["fix.change.freeze"].browse(fid).status == "ended"


def test_an_emergency_change_without_its_record_is_reverted(c, p03):
    param = _param(c)
    icp = c.env["ir.config_parameter"].sudo()
    eid = _ok(
        p03.write(
            c.pa1,
            model="fix.config.change",
            values={
                "parameter_id": param.id,
                "new_value": "400",
                "reason": "outage",
                "emergency": True,
            },
        )
    )
    _ok(
        p03.action(c.pa1, model="fix.config.change", record_id=eid, method="action_apply_emergency")
    )
    rec = c.env["fix.config.change"].browse(eid)
    assert not c.env["fix.config.change"].cron_revert_unregularised(), "not before 24 hours"
    c.env.cr.execute(
        "UPDATE fix_config_change SET regularise_by = now() at time zone 'UTC' - interval '1 hour' "
        "WHERE id = %s",
        (eid,),
    )
    rec.invalidate_recordset()
    assert c.env["fix.config.change"].cron_revert_unregularised() == rec
    assert rec.state == "rolled_back" and icp.get_param(KEY) == "100"


def test_a_freeze_lets_the_kill_switch_through_and_nothing_else(c, p03):
    from odoo.addons.cd_entity_config.models.fix_feature_flag import FLAG_WIRED_KEYS

    Flag = c.env["fix.feature.flag"].sudo()
    flag = Flag.search([("key", "in", sorted(FLAG_WIRED_KEYS))], limit=1) or Flag.create(
        {"key": sorted(FLAG_WIRED_KEYS)[0], "name": "test flag"}
    )
    flag.enabled = True
    _freeze(c, p03, scope="flags")
    other = p03.write(
        c.pa1, model="fix.feature.flag", record_id=flag.id, values={"scope": "branch"}
    )
    assert _err(other) and "freeze" in str(other), other
    _ok(p03.write(c.pa1, model="fix.feature.flag", record_id=flag.id, values={"enabled": False}))
    assert not flag.enabled
    on = p03.write(c.pa1, model="fix.feature.flag", record_id=flag.id, values={"enabled": True})
    assert _err(on) and "freeze" in str(on), on
    # owner and removal date are bookkeeping, allowed during a freeze
    _ok(
        p03.write(
            c.pa1,
            model="fix.feature.flag",
            record_id=flag.id,
            values={"owning_module": "M30", "planned_removal_date": "2020-01-01"},
        )
    )
    assert flag.stale


def test_a_copyleft_licence_needs_its_compliance_note(c, p03):
    base = {
        "component": "M30 test lib",
        "version": "1.0",
        "licence": "AGPL-3.0",
        "licence_class": "network_copyleft",
        "next_review_due": fields.Date.to_string(
            datetime.date.today() + datetime.timedelta(days=90)
        ),
    }
    assert _err(p03.write(c.pa1, model="fix.component.licence", values=base))
    _ok(
        p03.write(
            c.pa1,
            model="fix.component.licence",
            values=dict(base, compliance_note="Used unmodified as a separate service"),
        )
    )


# ------------------------------------------------------------ 5 Announcements
def _window(c, p03, day, hour, minutes, who=None):
    start = datetime.datetime.combine(day, datetime.time(hour % 24))
    return p03.write(
        who or c.pa1,
        model="fix.maintenance.window",
        values={
            "scheduled_from": _local_str(start),
            "scheduled_to": _local_str(start + datetime.timedelta(minutes=minutes)),
            "scope": "Database upgrade",
            "impact": "outage",
        },
    )


def _far_month_day(n):
    d = (datetime.date.today() + datetime.timedelta(days=45)).replace(day=n)
    return d


def test_maintenance_stays_in_the_night_band_and_under_the_cap(c, p03):
    day = _far_month_day(5)
    daytime = _window(c, p03, day, 10, 60)
    assert _err(daytime) and "23:00" in str(daytime), daytime
    late = _window(c, p03, day, 22, 120)  # 22:00 is still business hours
    assert _err(late), late
    _ok(_window(c, p03, day, 23, 120))
    _ok(_window(c, p03, _far_month_day(6), 1, 90))
    over = _window(c, p03, _far_month_day(7), 2, 60)  # 120 + 90 + 60 > 240
    assert _err(over) and "240" in str(over), over


def test_maintenance_starts_only_once_announced_72_hours_ahead(c, p03):
    wid = _ok(_window(c, p03, _far_month_day(12), 23, 60))
    window = c.env["fix.maintenance.window"].browse(wid)
    early = p03.action(c.pa1, model="fix.maintenance.window", record_id=wid, method="action_start")
    assert _err(early) and "announced" in str(early), early
    _ok(
        p03.action(
            c.pa1, model="fix.maintenance.window", record_id=wid, method="action_raise_announcement"
        )
    )
    ann = window.announcement_id
    assert ann.kind == "maintenance" and ann.state == "draft"
    assert ann.maintenance_start == window.scheduled_from
    # the window is not moved under its announcement
    moved = p03.write(
        c.pa1,
        model="fix.maintenance.window",
        record_id=wid,
        values={
            "scheduled_to": fields.Datetime.to_string(
                window.scheduled_to + datetime.timedelta(minutes=30)
            )
        },
    )
    assert _err(moved), moved
    # and not through the ORM either (the form lock above is one layer of two)
    with pytest.raises(REFUSED):
        window.with_user(c.pa1).write(
            {"scheduled_to": window.scheduled_to + datetime.timedelta(minutes=30)}
        )
    # the author does not publish; a second Platform Admin does
    assert _err(
        p03.action(
            c.pa1, model="fix.platform.announcement", record_id=ann.id, method="action_publish"
        )
    )
    _ok(
        p03.action(
            c.pa2, model="fix.platform.announcement", record_id=ann.id, method="action_publish"
        )
    )
    _ok(p03.action(c.pa1, model="fix.maintenance.window", record_id=wid, method="action_start"))
    _ok(p03.action(c.pa1, model="fix.maintenance.window", record_id=wid, method="action_complete"))
    assert window.state == "completed" and window.actual_from and window.actual_to


def test_an_announcement_carries_bengali_title_and_message(c, p03):
    rid = _ok(
        p03.write(
            c.pa1,
            model="fix.platform.announcement",
            values={
                "name": "Release notes",
                "name_bn": "রিলিজ নোট",
                "kind": "general",
                "severity": "info",
                "audience": "all",
                "publish_on": fields.Date.to_string(datetime.date.today()),
                "body": "New screens",
                "body_bn": "নতুন স্ক্রিন",
            },
        )
    )
    ann = c.env["fix.platform.announcement"].browse(rid)
    assert ann.name_bn == "রিলিজ নোট" and ann.body_bn == "নতুন স্ক্রিন"


# -------------------------------------------------------------------- 6 Audit
def test_every_alert_has_a_live_runbook(c, p03):
    empty = p03.write(c.pa1, model="fix.runbook", values={"code": "RB-M30", "name": "DB full"})
    assert _err(empty), "a runbook needs steps or a link"
    rb = _ok(
        p03.write(
            c.pa1,
            model="fix.runbook",
            values={
                "code": "RB-M30",
                "name": "DB full",
                "scope": "alert",
                "steps": "1. Extend the volume",
            },
        )
    )
    alert_vals = {
        "code": "AL-M30",
        "name": "Database volume above 85%",
        "source": "database",
        "severity": "p2",
        "threshold_expression": "pg volume > 85% for 10 min",
        "routing": "On-call DBA",
    }
    assert _err(p03.write(c.pa1, model="fix.platform.alert", values=alert_vals))
    _ok(p03.write(c.pa1, model="fix.platform.alert", values=dict(alert_vals, runbook_id=rb)))
    archive = p03.write(c.pa1, model="fix.runbook", record_id=rb, values={"active": False})
    assert _err(archive) and "BRU-ADM-14" in str(archive), archive
    book = c.env["fix.runbook"].browse(rb)
    assert book.next_review_due and not book.review_overdue


def test_a_capacity_review_decides_below_20_percent_and_is_evidence(c, p03):
    vals = {
        "resource": "PostgreSQL data volume",
        "dimension": "storage_gb",
        "measured_on": fields.Date.to_string(datetime.date.today()),
        "current_value": 85.0,
        "capacity_value": 100.0,
        "growth_rate_pct": 5.0,
        "scaling_action": "none",
        "review_note": "Monthly review",
    }
    low = p03.write(c.pa1, model="fix.capacity.metric", values=vals)
    assert _err(low) and "20%" in str(low), low
    rid = _ok(
        p03.write(
            c.pa1, model="fix.capacity.metric", values=dict(vals, scaling_action="scale_planned")
        )
    )
    rec = c.env["fix.capacity.metric"].browse(rid)
    assert rec.headroom_pct == 15.0 and rec.projected_exhaustion > datetime.date.today()
    assert rec.name.startswith("CAP/")
    redo = p03.write(
        c.pa1, model="fix.capacity.metric", record_id=rid, values={"current_value": 10.0}
    )
    assert _err(redo) or rec.current_value == 85.0, redo
    assert rec.current_value == 85.0
    with pytest.raises(REFUSED):
        rec.with_user(c.pa1).write({"current_value": 10.0})
    assert rec.current_value == 85.0
    _ok(
        p03.write(
            c.pa1,
            model="fix.capacity.metric",
            record_id=rid,
            values={"review_note": "Ordered disk"},
        )
    )
    with pytest.raises(REFUSED):
        rec.with_user(c.pa1).unlink()


def test_the_health_console_and_kpis_read_the_new_registers(c, p03):
    import odoo.addons.cd_p03_portal.controllers.a12.m30 as m30

    env = c.env(user=c.pa1.id)
    rows = m30._operations_signals(env, lambda m: m in env and env[m].has_access("read"))
    signals = " | ".join(r["signal"] for r in rows)
    for word in ("freeze", "Emergency", "maintenance", "Runbooks", "alerts", "headroom"):
        assert word in signals, word
    kpis = m30.kpis(env)
    assert "emergency_open" in kpis and "maintenance_upcoming" in kpis
    # a plain employee still gets a console, without the private rows
    plain = c.env(user=c.plain.id)
    rows = m30._operations_signals(plain, lambda m: m in plain and plain[m].has_access("read"))
    assert not any("Emergency" in r["signal"] for r in rows)
