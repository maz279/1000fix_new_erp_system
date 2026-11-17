"""M47 capture audit (2026-11-17), live: what each page now captures works, and
its controls hold, when a NON-ADMIN user with the real role does it through the
workspace endpoints (model_write, model_action, model_report), rolled back.

The registry side (which chip each page offers) is guarded statically by
cd_p03_portal/tests/test_m47_capture_buttons.py.
"""

from __future__ import annotations

import base64
import types
from datetime import timedelta

import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.form_fields import editable_by_model
from odoo.exceptions import UserError

FM = "cd_facility.group_facility_manager"
BOL = "cd_facility.group_branch_operations_lead"
OPSDIR = "cd_facility.group_operations_director"
CFO = "cd_entity_config.group_dofa_tier_4"
SCAN = base64.b64encode(b"%PDF-1.4 licence scan").decode()
PHOTO = base64.b64encode(b"\xff\xd8\xff\xe0 jpeg of a leaking AC").decode()


def _user(env, login, company, ou, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, company.ids)],
                "company_id": company.id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
                "tz": "Asia/Dhaka",
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.site"])
    x.co = env["res.company"].create({"name": "M47 Capture Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "M47 Cap OU",
            "code": "M47CAPOU",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.clerk = _user(env, "m47cap_clerk", x.co, x.ou)
    x.fm = _user(env, "m47cap_fm", x.co, x.ou, FM)
    x.fm2 = _user(env, "m47cap_fm2", x.co, x.ou, FM)
    x.bol = _user(env, "m47cap_bol", x.co, x.ou, BOL)
    x.od = _user(env, "m47cap_od", x.co, x.ou, OPSDIR)
    x.od2 = _user(env, "m47cap_od2", x.co, x.ou, OPSDIR)
    x.cfo = _user(env, "m47cap_cfo", x.co, x.ou, CFO)
    x.site = env["fix.site"].create(
        {"name": "M47 Cap Branch", "company_id": x.co.id, "operating_unit_id": x.ou.id}
    )
    x.site.sudo().write({"state": "active"})
    x.other_site = env["fix.site"].create(
        {"name": "M47 Cap Other", "company_id": x.co.id, "operating_unit_id": x.ou.id}
    )
    x.partner = env["res.partner"].create({"name": "M47 Cap Landlord / DESCO"})
    return x


@pytest.fixture
def ui(c, monkeypatch):
    cls = api.P03GenericApiController
    ctl = cls()
    generated = editable_by_model()
    for model, conf in api.SURFACES.items():
        if model in generated:
            monkeypatch.setitem(conf, "writable", frozenset(generated[model]))

    def call(name, user, **kw):
        ctx = dict(c.env.context, allowed_company_ids=user.company_ids.ids, tz="Asia/Dhaka")
        monkeypatch.setattr(
            api, "request", types.SimpleNamespace(env=c.env(user=user.id, context=ctx))
        )
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    def new(user, model, values):
        res = call("model_write", user, model=model, record_id=None, values=values)
        assert "id" in res, res
        return c.env[model].browse(res["id"])

    def refused(user, model, values, match, record_id=None):
        res = call("model_write", user, model=model, record_id=record_id, values=values)
        assert "error" in res, res
        assert match.lower() in res["error"].lower(), res["error"]

    def ok(user, model, rec, method, **kwargs):
        res = call(
            "model_action", user, model=model, ids=rec.ids, method=method, kwargs=kwargs or None
        )
        assert res.get("success"), res
        rec.invalidate_recordset()
        return res

    def no(user, model, rec, method, match=None, **kwargs):
        res = call(
            "model_action", user, model=model, ids=rec.ids, method=method, kwargs=kwargs or None
        )
        assert res.get("success") is False, res
        if match:
            assert match.lower() in res["error"].lower(), res["error"]
        return res

    return types.SimpleNamespace(
        new=new,
        refused=refused,
        write=lambda user, **kw: call("model_write", user, **kw),
        report=lambda user, **kw: call("model_report", user, **kw),
        ok=ok,
        no=no,
    )


def _licence(c, ltype, valid_to, number):
    return (
        c.env["fix.site.licence"]
        .with_user(c.fm)
        .create(
            {
                "site_id": c.site.id,
                "licence_type": ltype,
                "number": number,
                "issued_on": valid_to - timedelta(days=365),
                "valid_to": valid_to,
                "evidence_file": SCAN,
                "evidence_filename": "scan.pdf",
            }
        )
    )


def _events(c, event_type, record):
    return c.env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", record._name),
            ("aggregate_id", "=", record.id),
        ]
    )


# ---------------------------------------------------------------- page 1
def test_1_a_site_type_profile_sets_what_the_site_must_hold(c, ui):
    ui.refused(c.fm, "fix.site.type.profile", {"site_type": "branch"}, "branch operations lead")
    profile = ui.new(
        c.bol,
        "fix.site.type.profile",
        {"site_type": "branch", "req_fire": False, "req_signage": True},
    )
    assert profile._m47_types() == ["trade", "signage"]
    ui.refused(c.bol, "fix.site.type.profile", {"site_type": "branch"}, "already has")
    # the readiness gate asks for exactly the profile's licences
    planned = c.env["fix.site"].create(
        {"name": "M47 Cap Planned", "company_id": c.co.id, "operating_unit_id": c.ou.id}
    )
    items = " | ".join(planned._site_readiness_items())
    assert "signage permit" in items and "fire" not in items
    # and an operational site without one shows the gap
    rows = ui.report(c.bol, module="M47", report="licence_compliance")["rows"]
    assert any(r.get("site") == c.site.name and "Signage" in str(r) for r in rows), rows


# ---------------------------------------------------------------- page 3
def test_3_a_renewal_runs_from_initiation_to_the_new_licence(c, ui):
    fire = _licence(c, "fire", c.today + timedelta(days=20), "FSCD-1")
    trade = _licence(c, "trade", c.today + timedelta(days=40), "TL-1")
    ui.write(
        c.fm,
        model="fix.site.licence",
        record_id=fire.id,
        values={"authority": "FSCD Mirpur", "fee": 5000, "responsible_id": c.fm2.id},
    )
    assert fire.authority == "FSCD Mirpur" and fire.fee == 5000
    ui.refused(
        c.clerk,
        "fix.site.licence.renewal",
        {"licence_id": fire.id, "responsible_id": c.fm2.id},
        "facility manager",
    )
    ren = ui.new(
        c.fm, "fix.site.licence.renewal", {"licence_id": fire.id, "responsible_id": c.fm2.id}
    )
    assert ren.authority == "FSCD Mirpur" and ren.site_id == c.site
    ui.refused(
        c.fm,
        "fix.site.licence.renewal",
        {"licence_id": fire.id, "responsible_id": c.fm.id},
        "in progress",
    )
    ui.no(c.fm, ren._name, ren, "action_submit", match="documents")
    ui.write(
        c.fm,
        model=ren._name,
        record_id=ren.id,
        values={"documents_assembled": True, "government_fee": 4000, "penalty": 500},
    )
    ui.no(c.fm, ren._name, ren, "action_submit", match="challan")
    ui.write(
        c.fm,
        model=ren._name,
        record_id=ren.id,
        values={"challan_ref": "SONALI-778", "penalty_reason": "Inspector visit delayed"},
    )
    ui.ok(c.fm, ren._name, ren, "action_submit")
    assert ren.state == "submitted" and ren.submitted_by_id == c.fm
    ui.no(c.fm, ren._name, ren, "action_complete", match="renewed licence")
    new_fire = _licence(c, "fire", c.today + timedelta(days=385), "FSCD-2")
    ui.write(c.fm, model=ren._name, record_id=ren.id, values={"new_licence_id": trade.id})
    ui.no(c.fm, ren._name, ren, "action_complete", match="new fire")
    ui.write(c.fm, model=ren._name, record_id=ren.id, values={"new_licence_id": new_fire.id})
    # a penalty arose from fm2's renewal: fm2 does not complete it (§13)
    ui.no(c.fm2, ren._name, ren, "action_complete", match="segregation")
    ui.ok(c.fm, ren._name, ren, "action_complete")
    assert ren.state == "completed" and ren.total_cost == 4500
    ui.refused(c.fm, ren._name, {"government_fee": 1}, "read-only", record_id=ren.id)
    with pytest.raises(UserError, match="does not change"):
        ren.with_user(c.fm).write({"government_fee": 1})
    # Cost per Site counts the renewal
    rows = ui.report(c.bol, module="M47", report="cost_per_site")["rows"]
    assert next(r for r in rows if r["site"] == c.site.name)["compliance"] == 4500


def test_3_a_trade_renewal_waits_for_the_fire_licence(c, ui):
    fire = _licence(c, "fire", c.today + timedelta(days=10), "FSCD-9")
    trade = _licence(c, "trade", c.today + timedelta(days=30), "TL-9")
    fire.sudo()._guarded().write({"state": "expired"})
    ui.refused(
        c.fm,
        "fix.site.licence.renewal",
        {"licence_id": trade.id, "responsible_id": c.fm.id},
        "BRU-FAC-03",
    )


def test_3_the_renewal_owner_does_not_decide_the_lapse(c, ui):
    lapsed = c.env["fix.site.licence"].create(
        {
            "site_id": c.site.id,
            "licence_type": "health",
            "number": "H-1",
            "valid_to": c.today - timedelta(days=1),
            "evidence_file": SCAN,
        }
    )
    exc = c.env["fix.site.risk.exception"].search([("licence_id", "=", lapsed.id)])
    assert exc, "a lapsed licence at an operational site raises the exception"
    c.env["fix.site.licence.renewal"].create({"licence_id": lapsed.id, "responsible_id": c.od.id})
    ui.no(c.od, exc._name, exc, "action_decide_suspend", match="segregation", notes="close it")
    ui.ok(
        c.od2,
        exc._name,
        exc,
        "action_decide_suspend",
        notes="No health licence: stop until renewed",
    )


# ---------------------------------------------------------------- page 2
def test_2_a_lease_event_is_owned_alerted_and_decided(c, ui):
    lease = (
        c.env["fix.site.lease"]
        .with_user(c.fm)
        .create(
            {
                "site_id": c.site.id,
                "lessor_id": c.partner.id,
                "start_date": c.today - timedelta(days=200),
                "end_date": c.today + timedelta(days=900),
                "monthly_rent": 100000,
            }
        )
    )
    ui.refused(
        c.clerk,
        "fix.site.lease.event",
        {
            "lease_id": lease.id,
            "event_type": "break_option",
            "due_on": str(c.today + timedelta(days=20)),
            "responsible_id": c.bol.id,
        },
        "facility manager",
    )
    ui.refused(
        c.fm,
        "fix.site.lease.event",
        {
            "lease_id": lease.id,
            "event_type": "landlord_obligation",
            "due_on": str(c.today + timedelta(days=20)),
            "responsible_id": c.bol.id,
        },
        "obliges",
    )
    brk = ui.new(
        c.fm,
        "fix.site.lease.event",
        {
            "lease_id": lease.id,
            "event_type": "break_option",
            "due_on": str(c.today + timedelta(days=20)),
            "responsible_id": c.bol.id,
            "amount": 300000,
        },
    )
    assert brk.site_id == c.site
    # Critical-Date Control lists it
    rows = ui.report(c.fm, module="M47", report="critical_dates")["rows"]
    assert any(r["reference"] == brk.name for r in rows), rows
    # alerted once per horizon, not every day
    c.env["fix.site.lease.event"].cron_lease_event_alerts()
    c.env["fix.site.lease.event"].cron_lease_event_alerts()
    assert len(_events(c, "lease.critical_date_due", brk)) == 1 and brk.alert_horizon == 30
    # a break is the CFO's decision, and is exercised or not
    ui.no(c.bol, brk._name, brk, "action_decide_exercise", match="CFO", notes="go")
    ui.no(c.cfo, brk._name, brk, "action_mark_met", match="decided", notes="x")
    ui.ok(c.cfo, brk._name, brk, "action_decide_decline", notes="Branch is profitable: stay")
    assert brk.state == "done" and brk.decision == "decline" and brk.decided_by_id == c.cfo
    # an obligation is met by its owner, never by the person who recorded it
    dep = ui.new(
        c.bol,
        "fix.site.lease.event",
        {
            "lease_id": lease.id,
            "event_type": "deposit_return",
            "due_on": str(c.today + timedelta(days=60)),
            "responsible_id": c.bol.id,
        },
    )
    ui.no(c.bol, dep._name, dep, "action_mark_met", match="segregation", notes="received")
    ui.no(c.clerk, dep._name, dep, "action_mark_met", notes="received")
    dep.sudo().write({"responsible_id": c.fm2.id})
    ui.no(c.fm2, dep._name, dep, "action_decide_exercise", match="obligation", notes="x")
    ui.ok(c.fm2, dep._name, dep, "action_mark_met", notes="Deposit received, bank ref 4471")
    assert dep.decision == "met"


# ---------------------------------------------------------------- page 4
def test_4_a_utility_account_owns_its_bills(c, ui):
    vals = {
        "site_id": c.site.id,
        "utility_type": "power",
        "provider_id": c.partner.id,
        "account_no": "DESCO-100",
        "meter_no": "M-1",
    }
    ui.refused(c.clerk, "fix.site.utility.account", vals, "facility manager")
    acc = ui.new(c.fm, "fix.site.utility.account", vals)
    ui.refused(
        c.fm,
        "fix.site.utility.account",
        dict(vals, account_no="desco-100 ", site_id=c.other_site.id),
        "already registered",
    )
    ui.refused(c.fm, acc._name, {"account_no": "DESCO-101"}, "read-only", record_id=acc.id)
    # the branch records a bill: its only account is filled in
    bill = ui.new(
        c.clerk,
        "fix.site.utility",
        {"site_id": c.site.id, "period": "2026-09", "utility_type": "power", "amount": 20000},
    )
    assert bill.account_id == acc
    # a second meter: a bill must say which, and both meters bill the month
    acc2 = ui.new(
        c.fm, "fix.site.utility.account", dict(vals, account_no="DESCO-200", meter_no="M-2")
    )
    ui.refused(
        c.clerk,
        "fix.site.utility",
        {"site_id": c.site.id, "period": "2026-10", "utility_type": "power", "amount": 1},
        "choose the account",
    )
    ui.new(
        c.clerk,
        "fix.site.utility",
        {
            "site_id": c.site.id,
            "account_id": acc2.id,
            "period": "2026-09",
            "utility_type": "power",
            "amount": 9000,
        },
    )
    ui.refused(
        c.clerk,
        "fix.site.utility",
        {
            "site_id": c.site.id,
            "account_id": acc2.id,
            "period": "2026-09",
            "utility_type": "power",
            "amount": 9000,
        },
        "already has a bill",
    )
    ui.refused(
        c.clerk,
        "fix.site.utility",
        {
            "site_id": c.site.id,
            "account_id": acc2.id,
            "period": "2026-11",
            "utility_type": "water",
            "amount": 9,
        },
        "not of this bill",
    )
    ui.no(c.fm, acc2._name, acc2, "action_close", match="why")
    ui.ok(c.fm, acc2._name, acc2, "action_close", reason="Meter merged into M-1")
    later = (c.today + timedelta(days=40)).strftime("%Y-%m")
    ui.refused(
        c.clerk,
        "fix.site.utility",
        {
            "site_id": c.site.id,
            "account_id": acc2.id,
            "period": later,
            "utility_type": "power",
            "amount": 9,
        },
        "closed",
    )


# ---------------------------------------------------------------- page 5
def test_5_an_outage_counts_the_hours_the_branch_lost(c, ui):
    gen = c.env["fix.site.asset"].create(
        {"site_id": c.site.id, "asset_type": "generator", "make": "Cummins", "capacity": "60 kVA"}
    )
    far = c.env["fix.site.asset"].create({"site_id": c.other_site.id, "asset_type": "ups"})
    start = fields.Datetime.now() - timedelta(hours=5)
    local = lambda dt: fields.Datetime.to_string(dt + timedelta(hours=6))  # noqa: E731 - Dhaka wall clock
    ui.refused(
        c.clerk,
        "fix.site.outage",
        {
            "site_id": c.site.id,
            "service": "ups",
            "asset_id": far.id,
            "started_at": local(start),
            "cause": "x",
        },
        "is not at",
    )
    out = ui.new(
        c.clerk,
        "fix.site.outage",
        {
            "site_id": c.site.id,
            "service": "generator",
            "asset_id": gen.id,
            "started_at": local(start),
            "cause": "Load shedding, generator failed to start",
            "branch_stopped": True,
        },
    )
    assert out.recorded_by_id == c.clerk and out.state == "open"
    assert (
        abs((out.started_at - start).total_seconds()) < 60
    ), "the typed Dhaka time is stored as UTC"
    ui.ok(c.clerk, out._name, out, "action_end", ended_at=local(start + timedelta(hours=3)))
    assert out.state == "ended" and out.duration_hours == 3.0 and out.operating_hours_lost == 3.0
    assert _events(c, "site.outage", out)
    ui.refused(c.clerk, out._name, {"cause": "rewritten"}, "read-only", record_id=out.id)
    rows = ui.report(c.fm, module="M47", report="infrastructure_availability")["rows"]
    row = next(r for r in rows if r["site"] == c.site.name)
    assert row["outages"] == 1 and row["hours_lost"] == 3.0


# ---------------------------------------------------------------- page 6
def test_6_a_generator_test_is_recorded_and_a_missed_one_escalates(c, ui):
    gen = c.env["fix.site.asset"].create(
        {
            "site_id": c.site.id,
            "asset_type": "generator",
            "installed_on": c.today - timedelta(days=200),
        }
    )
    ups = c.env["fix.site.asset"].create(
        {"site_id": c.site.id, "asset_type": "ups", "installed_on": c.today - timedelta(days=10)}
    )
    t1 = ui.new(
        c.clerk,
        "fix.site.power.test",
        {
            "asset_id": gen.id,
            "test_type": "load_test",
            "result": "pass",
            "run_hours": 1200,
            "load_pct": 70,
            "fuel_level_pct": 80,
        },
    )
    assert t1.tested_by_id == c.clerk and t1.site_id == c.site
    ui.refused(
        c.clerk,
        "fix.site.power.test",
        {"asset_id": gen.id, "test_type": "run_test", "result": "pass", "run_hours": 1100},
        "cannot go back",
    )
    ui.refused(
        c.clerk,
        "fix.site.power.test",
        {"asset_id": ups.id, "test_type": "fuel_check", "result": "pass"},
        "UPS has no fuel",
    )
    ui.refused(
        c.clerk,
        "fix.site.power.test",
        {"asset_id": ups.id, "test_type": "battery_check", "result": "fail"},
        "what failed",
    )
    fail = ui.new(
        c.clerk,
        "fix.site.power.test",
        {
            "asset_id": ups.id,
            "test_type": "battery_check",
            "result": "fail",
            "battery_condition": "replace",
            "finding": "Two cells swollen",
        },
    )
    assert (
        fail.work_order_id
        and fail.work_order_id.work_type == "repair"
        and fail.work_order_id.site_id == c.site
    )
    ui.refused(c.clerk, fail._name, {"result": "pass"}, "read-only", record_id=fail.id)
    with pytest.raises(UserError, match="does not change"):
        fail.with_user(c.clerk).write({"result": "pass"})
    # BRU-FAC-10: an untested generator escalates to the Operations Director, once
    stale = c.env["fix.site.asset"].create(
        {
            "site_id": c.site.id,
            "asset_type": "generator",
            "installed_on": c.today - timedelta(days=90),
        }
    )
    Asset = c.env["fix.site.asset"]
    Asset.cron_power_test_due()
    Asset.cron_power_test_due()
    rows = _events(c, "site.power_test_overdue", stale)
    assert len(rows) == 1 and not _events(c, "site.power_test_overdue", gen)
    sub = c.env.ref("cd_asset_workorder_spine.consumer_alert_site_power_test_overdue")
    assert c.env["fix.event.outbox"]._relay_deliver(sub, rows) == ""
    alert = c.env["fix.asset.alert"].search(
        [("res_model", "=", "fix.site.asset"), ("res_id", "=", stale.id)]
    )
    assert alert.module == "M47" and "Operations Director" in alert.role_group


# ---------------------------------------------------------------- page 7 and the asset form
def test_7_a_request_carries_its_photo_and_an_asset_its_identity(c, ui):
    wo = ui.new(
        c.clerk,
        "fix.facility.work.order",
        {
            "name": "New",
            "site_id": c.site.id,
            "work_type": "repair",
            "description": "AC leaking over the counter",
            "request_photo": PHOTO,
            "request_photo_filename": "ac.jpg",
        },
    )
    assert wo.request_photo and wo.request_photo_filename == "ac.jpg"
    asset = ui.new(
        c.clerk,
        "fix.site.asset",
        {
            "name": "New",
            "site_id": c.site.id,
            "asset_type": "ups",
            "make": "APC",
            "model_name": "SRT10K",
            "capacity": "10 kVA",
            "expected_life_months": 84,
        },
    )
    assert (asset.make, asset.model_name, asset.capacity, asset.expected_life_months) == (
        "APC",
        "SRT10K",
        "10 kVA",
        84,
    )
