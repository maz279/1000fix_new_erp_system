"""A07 ERP audit (2026-11-20), stream M47: the facility money and control fixes.

Every test drives the ORM (rolled back), as the role that would really act.
Money hand-offs to M52 are observed at the M47 boundary: `queue_cost` (the
call into `fix.asset.cost.entry._m52_queue`) is captured, so the facts M47
states are asserted whatever the bridge's cost types are on this database.
"""

from __future__ import annotations

import datetime
import json
import types

import odoo.addons.cd_facility.models.fix_facility as fac
import odoo.addons.cd_facility.models.fix_facility_money as money
import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cd_asset_workorder_spine.models.fix_asset_alert import _route
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
FM = "cd_facility.group_facility_manager"
BOL = "cd_facility.group_branch_operations_lead"
OD = "cd_facility.group_operations_director"
TIER = "cd_entity_config.group_dofa_tier_%d"


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
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fac.dhaka_today(env["fix.site"])
    x.month = x.today.replace(day=1)
    x.co = env.company
    x.ou = env["operating.unit"].create(
        {
            "name": "A7ERP M47 OU",
            "code": "A7EM47",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    entity = env["fix.entity"].search([("company_id", "=", x.co.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "A7EM", "legal_name": "A07 ERP entity", "company_id": x.co.id})
    x.br = env["fix.branch"].create(
        {
            "name": "A7ERP M47 Branch",
            "code": "A7EMB",
            "entity_id": entity.id,
            "operating_unit_id": x.ou.id,
        }
    )
    x.site = env["fix.site"].create(
        {
            "name": "A7ERP M47 Site",
            "company_id": x.co.id,
            "operating_unit_id": x.ou.id,
            "branch_id": x.br.id,
        }
    )
    x.site.sudo()._guarded().write({"state": "active"})
    u = lambda login, *g: _user(env, login, x.co, x.ou, *g)  # noqa: E731
    x.clerk = u("a7e47_clerk")
    x.fm, x.fm2 = u("a7e47_fm", FM), u("a7e47_fm2", FM)
    x.bol, x.bol2 = u("a7e47_bol", BOL), u("a7e47_bol2", BOL)
    x.od = u("a7e47_od", OD)
    x.t2, x.t3 = u("a7e47_t2", TIER % 2), u("a7e47_t3", TIER % 3)
    x.cfo, x.ceo = u("a7e47_cfo", TIER % 4), u("a7e47_ceo", TIER % 5)
    x.landlord = env["res.partner"].create({"name": "A7ERP Landlord"})
    x.vendor = env["res.partner"].create({"name": "A7ERP Vendor"})
    return x


@pytest.fixture
def queued(monkeypatch):
    """What M47 hands to M52 (record, facts), captured at the boundary."""
    out = []

    def capture(record, vals):
        out.append((record, dict(vals)))
        return None

    monkeypatch.setattr(money, "queue_cost", capture)
    return out


def _lease(c, user=None, **vals):
    Lease = c.env["fix.site.lease"]
    if user:
        Lease = Lease.with_user(user)
    return Lease.create(
        {
            "site_id": c.site.id,
            "lessor_id": c.landlord.id,
            "start_date": c.month,
            "end_date": c.month + relativedelta(years=2, days=-1),
            "monthly_rent": 100000.0,
            **vals,
        }
    )


def _events(c, event_type, record):
    rows = c.env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", record._name),
            ("aggregate_id", "=", record.id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows], rows


def _row(lease, period):
    return lease.schedule_ids.filtered(lambda r: r.period == period)


# ============================================================ M47-03 (P0)
def test_m47_03_a_rent_month_sent_to_ap_is_never_recreated_by_a_modification(c):
    lease = _lease(c)
    period = c.month.strftime("%Y-%m")
    row = _row(lease, period)
    row.with_user(c.fm).action_send_to_ap()
    assert row.ap_requested_on
    sent_id = row.id
    # what Apply Modification runs after writing the approved terms
    lease.sudo()._guarded().write({"monthly_rent": 120000.0})
    lease.sudo()._lease_build_schedule()
    again = _row(lease, period)
    assert len(again) == 1 and again.id == sent_id, "the sent row was deleted and re-created"
    assert again.ap_requested_on and again.rent_due == 100000.0
    assert again.revised_rent_due == 120000.0
    later = _row(lease, (c.month + relativedelta(months=1)).strftime("%Y-%m"))
    assert later.rent_due == 120000.0 and not later.ap_requested_on


# ============================================================ M47-27 / M47-07
def test_m47_27_rent_before_the_recording_month_is_history_never_sent(c):
    lease = _lease(c, start_date=c.month - relativedelta(months=6))
    assert lease.schedule_from == c.month
    old = lease.schedule_ids.filtered(lambda r: r.due_date < c.month)
    assert len(old) == 6 and all(old.mapped("historical"))
    with pytest.raises(UserError, match="history"):
        old[:1].with_user(c.fm).action_send_to_ap()


def test_m47_07_the_daily_job_sends_rent_that_has_fallen_due(c):
    lease = _lease(c, start_date=c.month - relativedelta(months=2))
    c.env["fix.site.lease.schedule"].cron_rent_due_to_ap()
    current = _row(lease, c.month.strftime("%Y-%m"))
    assert current.ap_requested_on == c.today
    assert not lease.schedule_ids.filtered("historical").filtered("ap_requested_on")
    assert not lease.schedule_ids.filtered(lambda r: r.due_date > c.today and r.ap_requested_on)
    payload, _rows = _events(c, "lease.rent_payment_requested", current)
    assert payload[-1]["amount"] == current.amount_payable
    assert payload[-1]["operating_unit_id"] == c.ou.id
    # idempotent: a second run sends nothing more
    c.env["fix.site.lease.schedule"].cron_rent_due_to_ap()
    assert len(_events(c, "lease.rent_payment_requested", current)[0]) == 1


def test_m47_13_rent_of_a_site_with_no_cost_centre_is_kept_back_with_the_reason(c):
    bare = c.env["fix.site"].create({"name": "A7ERP no OU", "company_id": c.co.id})
    bare.sudo()._guarded().write({"state": "active"})
    lease = _lease(c, site_id=bare.id)
    c.env["fix.site.lease.schedule"].cron_rent_due_to_ap()
    current = _row(lease, c.month.strftime("%Y-%m"))
    assert not current.ap_requested_on
    assert "operating unit" in (current.ap_block_reason or "")
    assert "an operating unit" in "; ".join(bare._site_readiness_items())


# ============================================================ D6 / M47-04 / M47-18
def test_d6_a_plain_user_cannot_record_a_lease(c):
    with pytest.raises(AccessError):
        _lease(c, user=c.clerk)


def test_d6_a_recorded_lease_is_a_draft_until_its_commitment_is_approved(c):
    lease = _lease(
        c, user=c.fm, monthly_rent=20000.0, end_date=c.month + relativedelta(years=1, days=-1)
    )
    assert lease.state == "draft" and not lease.schedule_ids
    assert lease.total_commitment == 240000.0
    assert not _events(c, "lease.recorded", lease)[0]
    with pytest.raises(REFUSED):
        lease.with_user(c.fm).action_activate()
    # a user cannot type it active
    with pytest.raises(REFUSED):
        lease.with_user(c.fm).write({"state": "active"})
    lease.with_user(c.fm).action_request_approval(justification="New branch premises")
    # <= 1,000,000: the Operations Director, no DOFA tier group
    assert not lease.approval_request_id.tier
    assert inbox_task(lease, c.od) and not inbox_task(lease, c.cfo)
    approve_via_inbox(lease, c.od, requester=c.fm)
    assert lease.dofa_approved
    lease.with_user(c.fm).action_activate()
    assert lease.state == "active" and len(lease.schedule_ids) == 12
    assert _events(c, "lease.recorded", lease)[0]


@pytest.mark.parametrize(
    "rent,tier,who", [(100000.0, "tier_4", "cfo"), (500000.0, "tier_5", "ceo")]
)
def test_d6_a_larger_commitment_goes_to_the_cfo_and_above_ten_million_the_ceo(c, rent, tier, who):
    lease = _lease(c, user=c.fm, monthly_rent=rent)
    lease.with_user(c.fm).action_request_approval(justification="Flagship branch")
    assert lease.approval_request_id.tier == tier
    assert not inbox_task(lease, c.od)
    approve_via_inbox(lease, getattr(c, who), requester=c.fm)
    lease.with_user(c.fm).action_activate()
    assert lease.state == "active"


def test_d6_the_operations_director_cannot_sign_a_cfo_commitment(c):
    lease = _lease(c, user=c.fm)  # 2.4M
    lease.with_user(c.fm).action_request_approval(justification="x")
    # the engine routes nothing to the Operations Director ...
    assert not inbox_task(lease, c.od)
    # ... and a vote carried under the CFO's task by the Operations Director fails
    task = inbox_task(lease, c.cfo)
    with pytest.raises(REFUSED):
        lease.with_user(c.od).with_context(fix_approval_task=task).action_dofa_approve()
    assert not lease.dofa_approved


def test_d6_the_approval_pins_the_lessor_and_the_amount(c):
    lease = _lease(
        c, user=c.fm, monthly_rent=20000.0, end_date=c.month + relativedelta(years=1, days=-1)
    )
    approve_via_inbox(lease, c.od, requester=c.fm, justification="ok")
    other = c.env["res.partner"].create({"name": "A7ERP other landlord"})
    lease.with_user(c.fm).write({"lessor_id": other.id})
    assert not lease.dofa_approved
    with pytest.raises(REFUSED):
        lease.with_user(c.fm).action_activate()


def test_d6_termination_is_approved_on_the_commitment_and_raises_the_penalty(c, queued):
    lease = _lease(c, monthly_rent=50000.0, deposit=600000.0)
    with pytest.raises(REFUSED):
        lease.with_user(c.fm).action_request_termination(reason="x", deposit_outcome="refund")
    with pytest.raises(UserError, match="deposit"):
        lease.with_user(c.bol).action_request_termination(reason="Branch merged")
    lease.with_user(c.bol).action_request_termination(
        reason="Branch merged",
        effective_date=str(c.month + relativedelta(months=3, days=-1)),
        penalty="100000",
        deposit_outcome="refund",
    )
    assert lease.termination_requested and lease.approval_state == "pending"
    with pytest.raises(REFUSED):
        lease.with_user(c.bol).action_terminate()
    assert lease.approval_request_id.tier == "tier_4"  # 1.2M commitment: CFO
    approve_via_inbox(lease, c.cfo, requester=c.bol)
    lease.with_user(c.bol).action_terminate()
    assert lease.state == "terminated" and lease.terminated_reason == "Branch merged"
    kinds = [(v["cost_type"], v["subtype"], v["vendor_id"], v["amount"]) for _r, v in queued]
    assert ("lease_rent", "break_penalty", c.landlord.id, 100000.0) in kinds
    payload, rows = _events(c, "lease.terminated", lease)
    assert payload[-1]["break_penalty"] == 100000.0 and payload[-1]["deposit_outcome"] == "refund"
    # M47-17: the consumer stops the rent after the effective date
    lease.consume_lease_terminated(rows[-1]._relay_event_dict())
    after = lease.schedule_ids.filtered(lambda r: r.due_date > lease.termination_effective_date)
    assert after and all(after.mapped("cancelled"))
    assert not lease.schedule_ids.filtered(lambda r: r.due_date <= c.month).filtered("cancelled")


# ============================================================ M47-08 / M47-28
def test_m47_08_deposit_and_advance_are_owed_and_settled_only_with_approval(c, queued):
    lease = _lease(
        c,
        user=c.fm,
        monthly_rent=20000.0,
        end_date=c.month + relativedelta(years=1, days=-1),
        deposit=300000.0,
        advance_rent_amount=120000.0,
        advance_adjust_monthly=10000.0,
    )
    approve_via_inbox(lease, c.od, requester=c.fm, justification="ok")
    lease.with_user(c.fm).action_activate()
    facts = {v["cost_type"]: v for _r, v in queued}
    assert facts["deposit"]["amount"] == 300000.0 and facts["deposit"]["vendor_id"] == c.landlord.id
    assert facts["deposit"]["operating_unit_id"] == c.ou.id
    assert facts["deposit"]["payment_method"] == "vendor_bill"
    assert facts["advance_rent"]["amount"] == 120000.0
    assert lease.deposit_balance == 300000.0 and lease.advance_balance == 120000.0
    # the advance the landlord adjusts is taken off the rent sent to AP
    row = _row(lease, c.month.strftime("%Y-%m"))
    row.with_user(c.fm).action_send_to_ap()
    assert row.advance_adjusted == 10000.0 and row.amount_payable == 10000.0
    assert lease.advance_balance == 110000.0
    with pytest.raises(UserError):
        lease.with_user(c.fm).action_settle_deposit("deposit_refund", 400000, "too much")
    out = lease.with_user(c.fm).action_settle_deposit("deposit_refund", 300000, "Landlord letter 7")
    charge = c.env["fix.site.charge"].browse(out["charge_ids"])
    assert charge.state == "draft"
    with pytest.raises(REFUSED):
        charge.with_user(c.fm).action_confirm()
    approve_via_inbox(charge, c.t3, requester=c.fm, justification="Landlord letter 7")
    charge.with_user(c.fm).action_confirm()
    assert charge.state == "confirmed" and lease.deposit_balance == 0.0
    assert (queued[-1][1]["cost_type"], queued[-1][1]["subtype"]) == ("deposit", "refund")


def test_m47_08_a_charge_is_never_typed(c):
    with pytest.raises(UserError):
        c.env["fix.site.charge"].with_user(c.fm).create(
            {
                "site_id": c.site.id,
                "operating_unit_id": c.ou.id,
                "kind": "deposit_paid",
                "amount": 1,
            }
        )


def test_m47_28_a_quarterly_lease_with_service_charge(c):
    lease = _lease(
        c,
        payment_frequency="quarterly",
        monthly_rent=10000.0,
        service_charge=1000.0,
        end_date=c.month + relativedelta(years=1, days=-1),
    )
    rows = lease.schedule_ids.sorted("due_date")
    assert len(rows) == 4 and set(rows.mapped("months")) == {3}
    assert rows[0].rent_due == 30000.0 and rows[0].service_charge_due == 3000.0
    assert rows[0].amount_payable == 33000.0
    assert lease.total_commitment == 132000.0
    extract = json.loads(lease.extract_ids[:1].payload)
    assert extract["payment_frequency"] == "quarterly" and len(extract["payments"]) == 4


# ============================================================ M47-05 / M47-06
def test_m47_05_06_billed_is_not_paid_and_a_rejected_bill_reopens_the_rent(c):
    lease = _lease(c)
    row = _row(lease, c.month.strftime("%Y-%m"))
    row.with_user(c.fm).action_send_to_ap()
    row._m52_mark_billed(c.today, "RENT-1")
    assert row.matched_on and not row.paid_on and row.variance == 0.0
    row._m52_mark_paid(105000.0, c.today, "RENT-1")
    assert row.paid_amount == 105000.0 and row.variance == 5000.0
    row._m52_mark_unbilled("rejected")
    assert not row.matched_on and not row.paid_on and row.ap_requested_on


# ============================================================ M47-10
def test_m47_10_a_renewal_raises_its_fee_and_penalty_on_the_authority(c, queued):
    authority = c.env["res.partner"].create({"name": "A7ERP City Corporation"})
    licence = c.env["fix.site.licence"].create(
        {
            "site_id": c.site.id,
            "licence_type": "trade",
            "number": "TL-1",
            "valid_to": c.today + datetime.timedelta(days=20),
        }
    )
    renewal = (
        c.env["fix.site.licence.renewal"]
        .with_user(c.fm)
        .create(
            {
                "licence_id": licence.id,
                "responsible_id": c.fm.id,
                "documents_assembled": True,
                "challan_ref": "CH-9",
                "government_fee": 5000.0,
                "other_cost": 1000.0,
            }
        )
    )
    with pytest.raises(UserError, match="authority"):
        renewal.with_user(c.fm).action_submit()
    renewal.with_user(c.fm).write({"authority_partner_id": authority.id})
    renewal.with_user(c.fm).action_submit()
    facts = [
        (v["cost_type"], v["subtype"], v["amount"], v["vendor_id"], v["invoice_ref"])
        for _r, v in queued
    ]
    assert ("licence_fee", "trade", 5000.0, authority.id, "CH-9") in facts
    assert ("licence_fee", "agent", 1000.0, authority.id, "CH-9") in facts
    assert all(v["operating_unit_id"] == c.ou.id for _r, v in queued)
    # the fee went to AP: it does not change after submission
    with pytest.raises(UserError):
        renewal.with_user(c.fm).write({"government_fee": 9000.0})
    new = c.env["fix.site.licence"].create(
        {
            "site_id": c.site.id,
            "licence_type": "trade",
            "number": "TL-2",
            "valid_to": c.today + datetime.timedelta(days=400),
            "evidence_file": "UERG",
        }
    )
    renewal.with_user(c.fm).write(
        {"new_licence_id": new.id, "penalty": 2000.0, "penalty_reason": "late"}
    )
    renewal.with_user(c.fm2).action_complete()
    assert ("licence_fee", "penalty", 2000.0, authority.id, "CH-9") in [
        (v["cost_type"], v["subtype"], v["amount"], v["vendor_id"], v["invoice_ref"])
        for _r, v in queued
    ]
    assert len(renewal.charge_ids) == 3


# ============================================================ M47-12 / M47-25
def _account(c, no, provider):
    return (
        c.env["fix.site.utility.account"]
        .with_user(c.fm)
        .create(
            {
                "site_id": c.site.id,
                "utility_type": "power",
                "provider_id": provider.id,
                "account_no": no,
            }
        )
    )


def test_m47_12_a_utility_bill_is_owed_only_to_its_accounts_provider(c):
    loose = (
        c.env["fix.site.utility"]
        .with_user(c.fm)
        .create(
            {"site_id": c.site.id, "period": "2026-07", "utility_type": "water", "amount": 900.0}
        )
    )
    assert not loose.ap_requested_on and "utility account" in loose.ap_block_reason
    assert not _events(c, "site.utility_payable", loose)[0]
    desco = c.env["res.partner"].create({"name": "A7ERP DESCO"})
    _account(c, "D-1", desco)
    bill = (
        c.env["fix.site.utility"]
        .with_user(c.fm)
        .create(
            {"site_id": c.site.id, "period": "2026-02", "utility_type": "power", "amount": 3000.0}
        )
    )
    payload = _events(c, "site.utility_payable", bill)[0][-1]
    assert payload["vendor_id"] == desco.id and payload["cost_date"] == "2026-02-28"
    assert payload["operating_unit_id"] == c.ou.id


def test_m47_18_only_a_facility_manager_records_a_utility_bill(c):
    with pytest.raises(AccessError):
        c.env["fix.site.utility"].with_user(c.clerk).create(
            {"site_id": c.site.id, "period": "2026-07", "utility_type": "power", "amount": 1.0}
        )


def test_m47_25_a_bill_is_compared_with_its_own_meter(c):
    desco = c.env["res.partner"].create({"name": "A7ERP DESCO 2"})
    small, big = _account(c, "S-1", desco), _account(c, "B-1", desco)
    Bill = c.env["fix.site.utility"].with_user(c.fm)
    for period in ("2026-05", "2026-06", "2026-07"):
        Bill.create(
            {
                "site_id": c.site.id,
                "account_id": small.id,
                "period": period,
                "utility_type": "power",
                "amount": 1000.0,
            }
        )
    bill = Bill.create(
        {
            "site_id": c.site.id,
            "account_id": big.id,
            "period": "2026-08",
            "utility_type": "power",
            "amount": 50000.0,
        }
    )
    assert bill.review_state == "none", bill.anomaly_basis


# ============================================================ M47-16 (D15)
def test_m47_16_triage_starts_the_sla_clocks_and_an_unanswered_job_escalates(c):
    wo = (
        c.env["fix.facility.work.order"]
        .with_user(c.clerk)
        .create(
            {
                "site_id": c.site.id,
                "company_id": c.co.id,
                "operating_unit_id": c.ou.id,
                "description": "Fire alarm fault",
            }
        )
    )
    wo.with_user(c.fm).action_triage("emergency")
    assert wo.response_due_at == wo.triaged_on + datetime.timedelta(hours=2)
    assert wo.restore_due_at == wo.triaged_on + datetime.timedelta(hours=8)
    past = fields.Datetime.now() - datetime.timedelta(hours=3)
    wo.sudo()._guarded().write({"response_due_at": past})
    c.env["fix.facility.work.order"].cron_wo_sla_escalation()
    assert wo.sla_escalation_level == 1 and wo.sla_response_breached
    assert c.bol in wo.activity_ids.mapped("user_id")
    c.env["fix.facility.work.order"].cron_wo_sla_escalation()
    assert len(wo.activity_ids.filtered(lambda a: a.user_id == c.bol)) == 1
    wo.with_user(c.fm).action_accept()
    assert wo.accepted_by_id == c.fm


def test_m47_16_the_sla_hours_are_parameters(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_facility.wo_sla_low_response_hours", "10")
    assert c.env["fix.facility.work.order"]._wo_sla_hours("low") == (10.0, 360.0)
    assert c.env["fix.facility.work.order"]._wo_sla_hours("normal") == (24.0, 120.0)


# ============================================================ M47-19 / M47-23 / M47-29
def test_m47_19_23_the_closed_event_states_who_is_owed_and_the_dhaka_day(c):
    wo = c.env["fix.facility.work.order"].create(
        {
            "site_id": c.site.id,
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "description": "x",
            "actual_cost": 500.0,
        }
    )
    wo.sudo()._guarded().write(
        {"state": "verified", "verified_at": datetime.datetime(2026, 11, 30, 19, 30)}
    )
    facts = wo._m52_cost_facts()
    assert facts["payment_method"] == "internal" and not facts["vendor_id"]
    assert facts["cost_date"] == datetime.date(2026, 12, 1)
    assert facts["operating_unit_id"] == c.ou.id
    wo.sudo().write({"assigned_type": "vendor", "vendor_id": c.vendor.id, "invoice_ref": "V-1"})
    assert wo._m52_cost_facts()["payment_method"] == "vendor_bill"


def test_m47_29_a_job_names_the_plant_of_its_own_site(c):
    other = c.env["fix.site"].create({"name": "A7ERP other site", "company_id": c.co.id})
    plant = c.env["fix.site.asset"].create({"site_id": other.id, "asset_type": "generator"})
    with pytest.raises(ValidationError):
        c.env["fix.facility.work.order"].create(
            {
                "site_id": c.site.id,
                "company_id": c.co.id,
                "description": "x",
                "site_asset_id": plant.id,
            }
        )


# ============================================================ M47-34
def test_m47_34_a_failed_generator_test_raises_a_high_priority_job(c):
    gen = c.env["fix.site.asset"].create({"site_id": c.site.id, "asset_type": "generator"})
    test = c.env["fix.site.power.test"].create(
        {"asset_id": gen.id, "test_type": "load_test", "result": "fail", "finding": "No start"}
    )
    assert test.work_order_id.priority == "high"
    assert test.work_order_id.site_asset_id == gen and test.work_order_id.response_due_at


# ============================================================ M47-24
def test_m47_24_only_opening_hours_count_as_operating_hours_lost(c):
    c.site.write({"opening_hour": 9.0, "closing_hour": 20.0})
    utc = lambda y, m, d, h: datetime.datetime(y, m, d, h)  # noqa: E731
    # 20:00 -> 08:00 Dhaka (14:00 -> 02:00 UTC): the branch was closed
    assert c.site._site_open_hours_between(utc(2026, 11, 3, 14), utc(2026, 11, 4, 2)) == 0.0
    # 08:00 -> 11:00 Dhaka: two of those hours were open
    assert c.site._site_open_hours_between(utc(2026, 11, 4, 2), utc(2026, 11, 4, 5)) == 2.0
    c.site.write({"weekly_off_day": "2"})  # 4 Nov 2026 is a Wednesday
    assert c.site._site_open_hours_between(utc(2026, 11, 4, 2), utc(2026, 11, 4, 5)) == 0.0


# ============================================================ M47-26
def test_m47_26_a_suspension_is_lifted_only_by_a_second_person_on_evidence(c):
    licence = c.env["fix.site.licence"].create(
        {
            "site_id": c.site.id,
            "licence_type": "fire",
            "number": "F-1",
            "valid_to": c.today + datetime.timedelta(days=200),
        }
    )
    licence.with_user(c.bol).action_suspend("FSCD notice 12")
    assert licence.state == "suspended" and not licence.is_valid
    with pytest.raises(UserError):
        licence.with_user(c.fm).write({"state": "valid"})
    with pytest.raises(UserError):
        licence.with_user(c.bol).action_reinstate("FSCD order 13")
    licence.with_user(c.bol2).action_reinstate("FSCD order 13")
    assert licence.state == "valid" and licence.reinstated_by_id == c.bol2


# ============================================================ M47-15
def test_m47_15_alerts_escalate_to_the_deciding_roles(c):
    ev = lambda et, **p: {"event_type": et, "payload": p}  # noqa: E731
    assert _route(ev("site.compliance_expiring", days_remaining=60))[1] == [FM]
    assert _route(ev("site.compliance_expiring", days_remaining=25))[1] == [BOL]
    assert _route(ev("site.compliance_expiring", days_remaining=10))[1] == [OD]
    assert set(_route(ev("site.risk_exception_raised"))[1]) == {OD, TIER % 5}
    assert _route(ev("lease.renewal_decision_required"))[1] == [TIER % 4]
    assert _route(ev("site.outage", branch_stopped=False)) is None
    licence = c.env["fix.site.licence"].create(
        {
            "site_id": c.site.id,
            "licence_type": "trade",
            "number": "T-9",
            "valid_to": c.today + datetime.timedelta(days=40),
        }
    )
    Alert = c.env["fix.asset.alert"]
    base = {"aggregate": "fix.site.licence", "aggregate_id": licence.id, "company_id": c.co.id}
    Alert.consume_asset_alert({**base, **ev("site.compliance_expiring", days_remaining=40)})
    Alert.consume_asset_alert({**base, **ev("site.compliance_expiring", days_remaining=10)})
    alert = Alert.search([("res_model", "=", "fix.site.licence"), ("res_id", "=", licence.id)])
    assert len(alert) == 1 and alert.raise_count == 2
    assert OD in alert.notified_groups
    assert c.od in alert.activity_ids.mapped("user_id")


# ============================================================ M47-11
def test_m47_11_a_fit_out_records_its_actual_cost_within_budget_and_its_cwip(c, queued):
    project = c.env["fix.site.project"].create(
        {"site_id": c.site.id, "project_type": "open", "budget": 100000.0}
    )
    project.sudo()._guarded().write(
        {
            "state": "in_progress",
            "dofa_approved": True,
            "dofa_approved_tier": "tier_2",
            "dofa_approved_amount": 100000.0,
        }
    )
    Cost = c.env["fix.site.project.cost"].with_user(c.fm)
    first = Cost.create(
        {
            "project_id": project.id,
            "description": "Partitioning",
            "vendor_id": c.vendor.id,
            "invoice_ref": "FO-1",
            "amount": 60000.0,
        }
    )
    first.with_user(c.fm).action_confirm()
    assert (queued[-1][1]["cost_type"], queued[-1][1]["subtype"]) == (
        "facility_work_order",
        "fit_out",
    )
    assert queued[-1][1]["invoice_ref"] == "FO-1"
    assert project.actual_cost == 60000.0
    second = Cost.create(
        {
            "project_id": project.id,
            "description": "Signage",
            "vendor_id": c.vendor.id,
            "invoice_ref": "FO-2",
            "amount": 50000.0,
        }
    )
    with pytest.raises(UserError, match="budget"):
        second.with_user(c.fm).action_confirm()
    second.with_user(c.fm).action_cancel()
    with pytest.raises(UserError, match="CWIP"):
        project.action_done()
    project.write({"cwip_ref": "CWIP/2026/0001", "useful_life_months": 120})
    project.action_done()
    assert project.capitalisation_requested_on == c.today
    assert project._m47_capitalisation_facts()["amount"] == 60000.0


# ============================================================ M47-17
def test_m47_17_a_stopped_branch_flags_its_open_service_orders(c):
    brand = c.env["fix.brand"].create({"name": "A7ERP Brand", "code": "A7EB"})
    model = c.env["fix.device.model"].create({"name": "A7ERP model", "brand_id": brand.id})
    owner = c.env["res.partner"].create({"name": "A7ERP owner"})
    device = c.env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": owner.id, "serial_number": "A7ERP-SN-1"}
    )
    tech = c.env["hr.employee"].create({"name": "A7ERP tech", "user_id": c.clerk.id})
    order = c.env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": owner.id,
            "branch_id": c.br.id,
            "operating_unit_id": c.ou.id,
            "fault_description": "No charge",
            "technician_id": tech.id,
        }
    )
    outage = c.env["fix.site.outage"].create(
        {
            "site_id": c.site.id,
            "service": "power",
            "cause": "Grid down",
            "branch_stopped": True,
            "started_at": fields.Datetime.now() - datetime.timedelta(hours=3),
        }
    )
    outage.action_end()
    _payload, rows = _events(c, "site.outage", outage)
    sub = c.env.ref("cd_facility.consumer_site_outage_sla_impact")
    assert c.env["fix.event.outbox"]._relay_deliver(sub, rows[-1]) == ""
    impact = outage.impact_ids.filtered(lambda i: i.res_model == "fix.service.order")
    assert impact.res_id == order.id and impact.window_end == outage.ended_at
    # redelivery adds nothing
    assert c.env["fix.event.outbox"]._relay_deliver(sub, rows[-1]) == ""
    assert len(outage.impact_ids.filtered(lambda i: i.res_id == order.id)) == 1


def test_m47_17_the_readiness_gate_marks_the_opening_projects_milestone(c):
    project = c.env["fix.site.project"].create({"site_id": c.site.id, "project_type": "open"})
    done = c.env["fix.site.project"].consume_site_readiness_gate_passed(
        {"aggregate": "fix.site", "aggregate_id": c.site.id, "payload": {"site_id": c.site.id}}
    )
    assert done and project.readiness_passed_on == c.today


# ============================================================ M47-36 / D4
def test_m47_36_the_business_day_is_dhaka_whatever_the_cron_users_zone(c):
    brussels = c.env["fix.site"].with_context(tz="Europe/Brussels")
    utc_now = datetime.datetime.utcnow()
    assert fac.dhaka_today(brussels) == (utc_now + datetime.timedelta(hours=6)).date()


# ============================================================ M47-21 / M47-22
def test_m47_21_22_cost_per_site_is_one_period_and_packs_honour_dates(c):
    import odoo.addons.cd_p03_portal.controllers.a07.m47 as pack

    lease = _lease(c, monthly_rent=30000.0, start_date=c.month - relativedelta(months=3))
    start = c.month - relativedelta(months=2)
    end = c.month - relativedelta(days=1)
    rows = pack.cost_per_site(c.env, date_from=str(start), date_to=str(end))["rows"]
    mine = next(r for r in rows if r["site"] == c.site.name)
    assert mine["rent"] == 60000.0  # two months of rent, not one beside lifetime costs
    due = lease.schedule_ids.filtered(lambda r: start <= r.due_date <= end)
    assert len(due) == 2
    wo = c.env["fix.facility.work.order"].create(
        {
            "site_id": c.site.id,
            "company_id": c.co.id,
            "description": "x",
            "scheduled_date": c.today - datetime.timedelta(days=400),
        }
    )
    out = pack.work_order_performance(c.env, date_from=str(c.today - datetime.timedelta(days=30)))
    assert wo.name not in [r["order"] for r in out["rows"]]
