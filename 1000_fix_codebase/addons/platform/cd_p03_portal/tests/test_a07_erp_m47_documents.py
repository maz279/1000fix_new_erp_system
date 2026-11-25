"""A07 ERP audit (2026-11-20) M47-30 / D18: the printable facility documents.

Each document is a report pack (controllers/a07/m47.py), so the standard report
bar prints exactly what the screen shows. Every test runs the pack against the
ORM (rolled back): the rows it prints, its own filter, the period, and the
company / operating-unit fence (the records of another company, and of another
unit for a branch user, never print).
"""

from __future__ import annotations

import datetime
import types

import odoo.addons.cd_facility.models.fix_facility as fac
import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.a07 import m47 as pack

FM = "cd_facility.group_facility_manager"
DOCS = (
    "facility_job_sheet",
    "site_handover",
    "lease_summary",
    "licence_register",
    "utility_bill_register",
    "outage_report",
)


def _site(env, name, company, ou=False):
    site = env["fix.site"].create(
        {"name": name, "company_id": company.id, "operating_unit_id": ou and ou.id}
    )
    site.sudo()._guarded().write({"state": "active"})
    return site


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fac.dhaka_today(env["fix.site"])
    x.month = x.today.replace(day=1)
    x.co = env.company

    def unit(code):
        return env["operating.unit"].create(
            {
                "name": "A7DOC %s" % code,
                "code": code,
                "company_id": x.co.id,
                "partner_id": x.co.partner_id.id,
            }
        )

    x.ou, x.ou2 = unit("A7DOC1"), unit("A7DOC2")
    x.site = _site(env, "A7DOC Home Site", x.co, x.ou)
    x.far = _site(env, "A7DOC Far Site", x.co, x.ou2)
    x.other_co = env["res.company"].create({"name": "A7DOC OtherCo"})
    x.foreign = _site(env, "A7DOC Foreign Site", x.other_co)
    x.fm = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a7doc_fm",
                "login": "a7doc_fm",
                "group_ids": [(6, 0, [env.ref("base.group_user").id, env.ref(FM).id])],
                "company_ids": [(6, 0, x.co.ids)],
                "company_id": x.co.id,
                "assigned_operating_unit_ids": [(6, 0, x.ou.ids)],
                "default_operating_unit_id": x.ou.id,
            }
        )
    )
    x.fm_env = env(user=x.fm.id, su=False)
    x.landlord = env["res.partner"].create({"name": "A7DOC Landlord"})
    x.vendor = env["res.partner"].create({"name": "A7DOC Vendor"})
    return x


def _wo(c, site, **vals):
    return c.env["fix.facility.work.order"].create(
        {
            "site_id": site.id,
            "company_id": site.company_id.id,
            "operating_unit_id": site.operating_unit_id.id,
            "description": "Replace the DB breaker",
            "vendor_id": c.vendor.id,
            "invoice_ref": "INV-A7DOC-1",
            "estimated_cost": 1500.0,
            **vals,
        }
    )


def _lease(c, site, **vals):
    return c.env["fix.site.lease"].create(
        {
            "site_id": site.id,
            "lessor_id": c.landlord.id,
            "start_date": c.month,
            "end_date": c.month + relativedelta(years=2, days=-1),
            "monthly_rent": 100000.0,
            "deposit": 300000.0,
            "advance_rent_amount": 120000.0,
            "advance_adjust_monthly": 10000.0,
            **vals,
        }
    )


def _licence(c, site, ltype="trade", days=60, **vals):
    return c.env["fix.site.licence"].create(
        {
            "site_id": site.id,
            "licence_type": ltype,
            "number": "TL-%s-%s" % (site.id, ltype),
            "issued_on": c.today - datetime.timedelta(days=300),
            "valid_to": c.today + datetime.timedelta(days=days),
            "authority": "Dhaka North City Corporation",
            "fee": 5000.0,
            **vals,
        }
    )


def _bill(c, site, period, utype="power", amount=8000.0):
    return c.env["fix.site.utility"].create(
        {
            "site_id": site.id,
            "period": period,
            "utility_type": utype,
            "amount": amount,
            "usage": 900.0,
            "unit": "kWh",
        }
    )


def _outage(c, site, hours_ago=3, service="power"):
    outage = c.env["fix.site.outage"].create(
        {
            "site_id": site.id,
            "service": service,
            "cause": "Grid down",
            "branch_stopped": True,
            "started_at": fields.Datetime.now() - datetime.timedelta(hours=hours_ago),
        }
    )
    outage.action_end()
    return outage


def _card(out):
    return {r["field"]: r["value"] for r in out["rows"]}


def _options(out, key):
    return next(f["options"] for f in out["filters"] if f["key"] == key)


def test_m47_30_every_document_is_a_served_pack():
    for name in DOCS:
        assert pack.REPORTS[name] is getattr(pack, name)


# ------------------------------------------------------------ job sheet
def test_m47_30_the_job_sheet_prints_sla_approval_vendor_cost_and_verifier(c):
    wo = _wo(c, c.site)
    empty = pack.facility_job_sheet(c.env)
    assert not empty["rows"] and wo.name in _options(empty, "work_order")
    card = _card(pack.facility_job_sheet(c.env, work_order=wo.name))
    assert card["Work order"] == wo.name and card["Site"] == c.site.name
    assert card["Vendor"] == c.vendor.name and card["Vendor invoice ref"] == "INV-A7DOC-1"
    assert card["Estimated cost (BDT)"] == "1500.00"
    assert card["Actual cost (BDT)"] == "not completed"
    want = (
        (wo.restore_due_at + datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
        if wo.restore_due_at
        else "—"
    )
    assert card["Restore due"] == want  # Dhaka time
    assert card["Restore SLA"] in ("Not triaged yet", "Open, within SLA")
    for line in ("Spend approval", "Approved by / on / amount", "Verified by / at"):
        assert line in card
    # a verified job prints its verifier and its actual cost
    wo.sudo()._guarded().write(
        {
            "state": "verified",
            "actual_cost": 1400.0,
            "verified_by_id": c.fm.id,
            "verified_at": datetime.datetime(2026, 11, 20, 4, 30),
        }
    )
    card = _card(pack.facility_job_sheet(c.env, work_order=wo.name))
    assert card["Actual cost (BDT)"] == "1400.00"
    assert card["Verified by / at"] == "a7doc_fm / 2026-11-20 10:30"  # Dhaka time


def test_m47_30_the_job_sheet_period_narrows_its_choice(c):
    old = _wo(c, c.site, scheduled_date=c.today - datetime.timedelta(days=400))
    now = _wo(c, c.site)
    recent = _options(
        pack.facility_job_sheet(c.env, date_from=str(c.today - datetime.timedelta(days=30))),
        "work_order",
    )
    assert now.name in recent and old.name not in recent
    # a work order outside the period cannot be printed through it
    out = pack.facility_job_sheet(
        c.env, date_from=str(c.today - datetime.timedelta(days=30)), work_order=old.name
    )
    assert not out["rows"]


# ------------------------------------------------------------ site hand-over
def test_m47_30_the_gate_pass_prints_the_readiness_gate_or_the_closure(c):
    c.site.sudo()._guarded().write(
        {"ready_power": True, "ready_security": True, "opened_on": c.today}
    )
    card = _card(pack.site_handover(c.env, site=c.site.name))
    assert card["Power connected"] == "Yes" and card["Connectivity live"] == "No"
    assert card["Hand-over"].startswith("Opening")
    assert "Keys received by (signature)" in card
    c.site.sudo()._guarded().write(
        {"state": "closed", "closure_assets_recovered": True, "closure_notes": "All back"}
    )
    card = _card(pack.site_handover(c.env, site=c.site.name))
    assert card["Hand-over"].startswith("Closing")
    assert card["Assets recovered (M45 / M15 / M46)"] == "Yes"
    assert card["Licences surrendered"] == "No" and card["Recovery notes"] == "All back"
    assert "Power connected" not in card
    # the period lists the sites opened (or signed off) in it
    tomorrow = str(c.today + datetime.timedelta(days=1))
    assert c.site.name not in _options(pack.site_handover(c.env, date_from=tomorrow), "site")
    assert c.site.name in _options(pack.site_handover(c.env, date_to=str(c.today)), "site")


# ------------------------------------------------------------ lease summary
def test_m47_30_the_lease_summary_prints_terms_schedule_balances_and_approvals(c):
    lease = _lease(c, c.site)
    out = pack.lease_summary(c.env, lease=lease.name)
    sections = {r["section"] for r in out["rows"]}
    assert sections >= {"Terms", "Deposit & advance", "Approvals", "Rent schedule"}
    by_item = {r["item"]: r["value"] for r in out["rows"]}
    assert by_item["Lessor"] == c.landlord.name
    assert by_item["Security deposit (BDT)"] == "300000.00"
    assert by_item["Deposit balance held by the lessor (BDT)"] == "%.2f" % lease.deposit_balance
    assert by_item["Advance balance still to adjust (BDT)"] == "%.2f" % lease.advance_balance
    assert "Approval" in by_item
    every = [r for r in out["rows"] if r["section"] == "Rent schedule"]
    assert len(every) == len(lease.schedule_ids)
    # the period prints the schedule rows falling due in it
    month_end = c.month + relativedelta(months=1, days=-1)
    one = pack.lease_summary(
        c.env, date_from=str(c.month), date_to=str(month_end), lease=lease.name
    )
    due = [r for r in one["rows"] if r["section"] == "Rent schedule"]
    assert len(due) == len(
        lease.schedule_ids.filtered(lambda r: c.month <= r.due_date <= month_end)
    )
    assert due and c.month.strftime("%Y-%m") in due[0]["item"]
    # a lease that ended before the period is not offered
    later = str(c.month + relativedelta(years=3))
    assert lease.name not in _options(pack.lease_summary(c.env, date_from=later), "lease")


# ------------------------------------------------------------ licence register
def test_m47_30_the_licence_register_filters_by_site_type_and_expiry(c):
    trade = _licence(c, c.site, "trade", days=60)
    fire = _licence(c, c.far, "fire", days=200, fee=7000.0)
    out = pack.licence_register(c.env)
    names = {r["licence"] for r in out["rows"]}
    assert {trade.name, fire.name} <= names
    row = next(r for r in out["rows"] if r["licence"] == trade.name)
    assert row["authority"] == "Dhaka North City Corporation" and row["fee"] == 5000.0
    assert row["days_left"] == 60 and row["valid_to"] == str(trade.valid_to)
    assert "Fire Safety" in _options(out, "licence_type")
    only_fire = pack.licence_register(c.env, licence_type="Fire Safety")
    assert {r["type"] for r in only_fire["rows"]} == {"Fire Safety"}
    assert fire.name in {r["licence"] for r in only_fire["rows"]}
    home = pack.licence_register(c.env, site=c.site.name)
    assert {r["site"] for r in home["rows"]} == {c.site.name}
    soon = pack.licence_register(c.env, date_to=str(c.today + datetime.timedelta(days=90)))
    soon_names = {r["licence"] for r in soon["rows"]}
    assert trade.name in soon_names and fire.name not in soon_names
    assert soon["totals"]["fee"] == sum(r["fee"] for r in soon["rows"])


# ------------------------------------------------------------ utility bills
def test_m47_30_the_utility_bill_register_filters_by_month_site_and_type(c):
    may = _bill(c, c.site, "2026-05")
    june = _bill(c, c.site, "2026-06", amount=9000.0)
    water = _bill(c, c.site, "2026-06", utype="water", amount=700.0)
    out = pack.utility_bill_register(c.env, date_from="2026-06-01", date_to="2026-06-30")
    names = {r["bill"] for r in out["rows"]}
    assert {june.name, water.name} <= names and may.name not in names
    row = next(r for r in out["rows"] if r["bill"] == june.name)
    assert row["amount"] == 9000.0 and row["unit"] == "kWh" and row["period"] == "2026-06"
    assert out["totals"]["amount"] == round(sum(r["amount"] for r in out["rows"]), 2)
    power = pack.utility_bill_register(
        c.env, date_from="2026-06-01", date_to="2026-06-30", utility_type="Electricity"
    )
    assert water.name not in {r["bill"] for r in power["rows"]}
    assert june.name in {r["bill"] for r in power["rows"]}
    far = pack.utility_bill_register(c.env, site=c.far.name)
    assert not {r["bill"] for r in far["rows"]} & {may.name, june.name, water.name}


# ------------------------------------------------------------ outage report
def test_m47_30_the_outage_report_prints_dhaka_times_and_hours_lost(c):
    outage = _outage(c, c.site)
    out = pack.outage_report(c.env, site=c.site.name)
    row = next(r for r in out["rows"] if r["outage"] == outage.name)
    want = (outage.started_at + datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
    assert row["started"] == want and row["ended"] != "Ongoing"
    assert row["stopped"] == "Yes" and row["hours"] == round(outage.duration_hours, 2)
    assert row["hours_lost"] == round(outage.operating_hours_lost, 2)
    assert "Grid Power" in _options(out, "service")
    assert not pack.outage_report(c.env, site=c.site.name, service="Water")["rows"]
    last_year = str(c.today - datetime.timedelta(days=365))
    assert not pack.outage_report(c.env, date_from=last_year, date_to=last_year)["rows"]
    today = pack.outage_report(c.env, date_from=str(c.today - datetime.timedelta(days=1)))
    assert outage.name in {r["outage"] for r in today["rows"]}


# ------------------------------------------------------------ the fence
def _everything(c, site, tag):
    return {
        "wo": _wo(c, site, description="fence %s" % tag),
        "lease": _lease(c, site),
        "licence": _licence(c, site, "trade"),
        "bill": _bill(c, site, c.month.strftime("%Y-%m")),
        "outage": _outage(c, site),
    }


def _printed(env):
    return {
        "wo": set(_options(pack.facility_job_sheet(env), "work_order")),
        "site": set(_options(pack.site_handover(env), "site")),
        "lease": set(_options(pack.lease_summary(env), "lease")),
        "licence": {r["licence"] for r in pack.licence_register(env)["rows"]},
        "bill": {r["bill"] for r in pack.utility_bill_register(env)["rows"]},
        "outage": {r["outage"] for r in pack.outage_report(env)["rows"]},
    }


def test_m47_30_documents_never_print_another_company_or_another_unit(c):
    home = _everything(c, c.site, "home")
    far = _everything(c, c.far, "far")
    foreign = _everything(c, c.foreign, "foreign")

    def assert_sees(printed, recs, site, yes):
        for key, rec in recs.items():
            assert (rec.name in printed[key]) is yes, (key, rec.name, yes)
        assert (site.name in printed["site"]) is yes, site.name

    # the companies selected in the session fence even a sudo (cron / e-mail) run
    session = c.env(context=dict(c.env.context, allowed_company_ids=c.co.ids))
    admin = _printed(session)
    assert_sees(admin, home, c.site, True)
    assert_sees(admin, far, c.far, True)
    assert_sees(admin, foreign, c.foreign, False)
    # a branch user sees only the sites of the units they work in
    branch = _printed(c.fm_env)
    assert_sees(branch, home, c.site, True)
    assert_sees(branch, far, c.far, False)
    assert_sees(branch, foreign, c.foreign, False)
    # and cannot print another unit's record by naming it
    assert not pack.facility_job_sheet(c.fm_env, work_order=far["wo"].name)["rows"]
    assert not pack.lease_summary(c.fm_env, lease=far["lease"].name)["rows"]
    assert not pack.site_handover(c.fm_env, site=c.far.name)["rows"]
