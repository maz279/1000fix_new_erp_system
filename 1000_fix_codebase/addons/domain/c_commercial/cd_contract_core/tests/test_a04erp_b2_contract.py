"""A04 ERP audit (20 Nov 2026), stream B2: the M08 contract side.

Live ORM, rolled back per test, as non-admin users where a role is the
control. Each test is built so only the new rule refuses or produces it:
  M08-F6 / M36-F3  calendar-month billing that totals the term value;
  M08-F1           suspension windows are never billed;
  M08-F2           termination ends the term and re-prices it;
  M08-F7           a term amendment cannot end before the billed-through date;
  M08-F12          DOFA / Legal on the total value, and an amendment crossing
                   the Legal threshold waits for Legal;
  M08-F9           the contract's SLA is the order's SLA;
  M08-F10          a RAMC / managed visit is contract work;
  M08-F14          an entitlement states its quantity;
  M08-F17          auto-renew is a choice; expiry is announced regardless;
  M08-F22          the OCA reference is archived (outside OCA's billing cron).
"""

from __future__ import annotations

import types
import uuid
from datetime import date, timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
OFFICER = "cd_contract_core.group_contract_officer"
MANAGER = "cd_contract_core.group_contract_manager"
LEGAL = "cd_contract_core.group_contract_legal"


def _user(env, login, *groups):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "%s_%s" % (login, TAG),
                "group_ids": [(6, 0, ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def b(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.contract"])
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.officer = _user(env, "b2_officer", OFFICER)
    x.manager = _user(env, "b2_manager", MANAGER)
    x.legal = _user(env, "b2_legal", LEGAL)
    x.customer = env["res.partner"].create({"name": "B2 Customer %s" % TAG, "phone": "01711000802"})
    brand = env["fix.brand"].create({"name": "B2 Brand %s" % TAG, "code": "B2%s" % TAG})
    x.model = env["fix.device.model"].create({"name": "B2 Model", "brand_id": brand.id})
    x.branch = env["fix.branch"].search([("operating_unit_id", "=", x.ou.id)], limit=1)
    if not x.branch:
        entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1)
        if not entity:  # the template has none to reuse
            entity = env["fix.entity"].create(
                {"legal_name": "B2 Entity", "code": "B2E%s" % TAG, "company_id": env.company.id}
            )
        x.branch = env["fix.branch"].create(
            {
                "name": "B2 Branch",
                "code": "B2-BR-%s" % TAG,
                "entity_id": entity.id,
                "operating_unit_id": x.ou.id,
            }
        )
    x.n = 0
    return x


def _device(b):
    b.n += 1
    vals = {
        "device_model_id": b.model.id,
        "owner_id": b.customer.id,
        "serial_number": "B2-%s-%03d" % (TAG, b.n),
    }
    if b.branch:
        vals["branch_id"] = b.branch.id
    return b.env["fix.device"].create(vals)


def _contract(b, start, end, annual=120000.0, **kw):
    vals = {
        "name": "B2 AMC",
        "family": "amc",
        "customer_id": b.customer.id,
        "operating_unit_id": b.ou.id,
        "date_start": start,
        "date_end": end,
        "annual_value": annual,
        "stamp_duty_cert_no": "SD-%s" % TAG,
        "stamp_duty_amount": 300.0,
        "has_signed_contract_doc": True,
    }
    vals.update(kw)
    return b.env["fix.contract"].with_user(b.officer).create(vals)


def _active(b, start, end, annual=120000.0, **kw):
    k = _contract(b, start, end, annual, **kw)
    k.sudo().action_activate()
    k.invalidate_recordset()
    assert k.state == "active"
    return k


def _total(rows):
    return round(sum(r["amount"] for r in rows), 2)


# ===================================================== M08-F6 / M36-F3: the schedule


def test_a_12_month_amc_bills_twelve_calendar_months(b):
    k = _contract(b, date(2027, 1, 1), date(2027, 12, 31))
    rows = k._fix_billing_schedule()
    assert len(rows) == 12, "fixed 30-day steps gave 13 invoices and a stub"
    assert [r["period_start"] for r in rows] == [date(2027, m, 1) for m in range(1, 13)]
    assert {r["amount"] for r in rows} == {10000.0}
    assert _total(rows) == 120000.0 == k.term_value


@pytest.mark.parametrize(
    "start,months,value",
    [
        (date(2027, 1, 1), 6, 120000.0),
        (date(2027, 2, 1), 1, 10000.0),
        (date(2028, 1, 1), 12, 120000.0),  # a leap year
        (date(2027, 1, 1), 24, 240000.0),
        (date(2027, 1, 31), 7, 100000.0),  # month-end anchor, rounding
    ],
)
def test_the_term_bills_exactly_its_value(b, start, months, value):
    """M36-F3: the probe found 6 months -986.30, 1 month -794.52, a leap year
    +328.77 and 24 months +328.77 against the quoted value."""
    end = start + relativedelta(months=months) - timedelta(days=1)
    k = _contract(b, start, end, annual=round(value * 12.0 / months, 2), term_value=value)
    rows = k._fix_billing_schedule()
    assert len(rows) == months
    assert _total(rows) == value


def test_frequency_and_timing_shape_the_periods(b):
    k = _contract(
        b,
        date(2027, 1, 1),
        date(2027, 12, 31),
        billing_frequency="quarterly",
        billing_timing="advance",
    )
    rows = k._fix_billing_schedule()
    assert [(r["period_start"], r["period_end"]) for r in rows] == [
        (date(2027, 1, 1), date(2027, 3, 31)),
        (date(2027, 4, 1), date(2027, 6, 30)),
        (date(2027, 7, 1), date(2027, 9, 30)),
        (date(2027, 10, 1), date(2027, 12, 31)),
    ]
    assert [r["amount"] for r in rows] == [30000.0] * 4


def test_the_total_contract_value_drives_dofa_and_legal(b):
    """M08-F12: a 3-year BDT 2.7M contract was tested as 900k a year: Tier 3
    and no Legal review."""
    k = _contract(b, date(2027, 1, 1), date(2029, 12, 31), annual=900000.0)
    assert k.term_value == 2700000.0
    assert k.legal_review_required
    assert k.dofa_tier_required == "tier_4"


# ===================================================== M08-F1: suspension windows


def _suspend(b, k, on):
    k.sudo()._guarded().write({"state": "suspended", "suspended_on": on})
    (window,) = k.sudo().suspension_ids
    assert window.date_from == on and not window.date_to
    return window


def test_a_suspended_period_is_not_billed_and_not_back_billed(b):
    start = b.today - timedelta(days=100)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    window = _suspend(b, k, b.today - timedelta(days=40))
    k.with_user(b.manager).action_resume(treatment="forfeit", note="customer resumed")
    assert k.state == "active"
    assert window.date_to == b.today - timedelta(days=1) and not window.compensated
    lost = k._fix_fee_between(window.date_from, window.date_to, suspended=False)
    assert lost > 0
    rows = k._fix_billing_schedule()
    # every suspended day is out of the bill, and only those
    assert _total(rows) == round(k.term_value - lost, 2)
    for row in rows:
        inside = max(row["period_start"], window.date_from) <= min(
            row["period_end"], window.date_to
        )
        full = k._fix_fee_between(row["period_start"], row["period_end"], suspended=False)
        if row is not rows[-1]:
            assert (row["amount"] < round(full, 2)) == inside


def test_a_term_extended_on_resume_bills_the_term_value_once(b):
    """The probe billed 196,602.74 on a 120,000 term: the suspension was
    back-billed AND the term extended."""
    start = b.today - timedelta(days=100)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    end_before = k.date_end
    _suspend(b, k, b.today - timedelta(days=30))
    k.with_user(b.manager).action_resume(treatment="extend_term", note="extend")
    assert k.date_end == end_before + timedelta(days=30)
    assert k.sudo().suspension_ids.compensated
    assert _total(k._fix_billing_schedule()) == k.term_value == 120000.0


def test_only_the_engine_writes_a_suspension_window(b):
    k = _contract(b, date(2027, 1, 1), date(2027, 12, 31))
    with pytest.raises(UserError, match="suspension"):
        b.env["fix.contract.suspension"].with_user(b.officer).create(
            {"contract_id": k.id, "date_from": date(2027, 2, 1)}
        )


# ===================================================== M08-F2: termination


def _approved_termination(b, k, effective, penalty=0.0):
    term = (
        b.env["fix.contract.termination"]
        .sudo()
        .create(
            {
                "name": "B2 termination %s" % TAG,
                "contract_id": k.id,
                "kind": "termination",
                "reason": "customer exit",
                "effective_date": effective,
                "penalty_amount": penalty,
            }
        )
    )
    term._guarded().write(
        {
            "state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": "tier_5",
            "dofa_approved_amount": 10**9,
        }
    )
    return term


def test_termination_ends_and_reprices_the_term(b):
    start = b.today - timedelta(days=70)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    end_before, value_before = k.date_end, k.term_value
    term = _approved_termination(b, k, b.today)
    term.with_user(b.manager).action_execute_termination()
    assert k.state == "terminated"
    assert k.date_end == b.today - timedelta(days=1)
    assert k.date_end_before_termination == end_before
    assert k.terminated_on == b.today
    lost = k._fix_fee_between(b.today, end_before, suspended=False)
    assert k.term_value == round(value_before - lost, 2)
    rows = k._fix_billing_schedule()
    assert rows[-1]["period_end"] == k.date_end
    assert _total(rows) == k.term_value


# ===================================================== M08-F7: term amendment


def test_a_term_amendment_cannot_end_before_the_billed_through_date(b):
    start = b.today - timedelta(days=200)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    k.sudo().mark_billed_through(b.today - timedelta(days=5))
    amendment = (
        b.env["fix.contract.amendment"]
        .with_user(b.officer)
        .create(
            {
                "name": "shorten %s" % TAG,
                "contract_id": k.id,
                "kind": "term",
                "new_date_end": b.today - timedelta(days=30),
                "effective_from": b.today,
            }
        )
    )
    with pytest.raises(UserError, match="termination notice"):
        amendment.action_request_approval(justification="shorten")


def test_a_term_amendment_moves_the_term_value(b):
    start = b.today - timedelta(days=10)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    amendment = (
        b.env["fix.contract.amendment"]
        .sudo()
        .create(
            {
                "name": "extend %s" % TAG,
                "contract_id": k.id,
                "kind": "term",
                "new_date_end": k.date_end + relativedelta(months=6),
                "effective_from": b.today + timedelta(days=1),
            }
        )
    )
    amendment._amendment_apply()
    assert amendment.state == "applied"
    assert k.term_value == 180000.0
    assert _total(k._fix_billing_schedule()) == 180000.0


# ===================================================== M08-F12: Legal on amendments


def test_an_amendment_crossing_the_legal_threshold_waits_for_legal(b):
    start = b.today - timedelta(days=10)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1), annual=900000.0)
    assert not k.legal_review_required  # 900k, AMC: below the threshold
    amendment = (
        b.env["fix.contract.amendment"]
        .sudo()
        .create(
            {
                "name": "uplift %s" % TAG,
                "contract_id": k.id,
                "kind": "pricing",
                "delta_value": 300000.0,
                "effective_from": b.today + timedelta(days=1),
            }
        )
    )
    assert amendment.legal_review_required
    amendment._guarded().write({"state": "approved"})
    amendment._amendment_apply()  # trusted service code, still held for Legal
    assert amendment.state == "approved" and k.annual_value == 900000.0
    with pytest.raises(UserError, match="Legal"):
        amendment.with_user(b.officer).action_legal_review("ok")
    amendment.with_user(b.legal).action_legal_review("terms reviewed")
    # effective tomorrow: applied by the daily job once it is due
    assert amendment.legal_reviewed_by == b.legal
    with_today = amendment.with_context()
    with_today._guarded().write({"effective_from": b.today})
    with_today.sudo()._amendment_apply()
    assert amendment.state == "applied" and k.annual_value == 1200000.0
    assert k.term_value > 1000000.0


# ===================================================== M08-F10 / F9: cover and SLA


def test_a_ramc_visit_is_contract_work_drawing_its_entitlement(b):
    device = _device(b)
    start = b.today - timedelta(days=10)
    k = _contract(b, start, start + relativedelta(years=1) - timedelta(days=1), family="ramc")
    k.write({"covered_device_ids": [(6, 0, device.ids)]})
    b.env["fix.contract.entitlement"].with_user(b.officer).create(
        {"contract_id": k.id, "entitlement_type": "visits", "quantity_included": 4}
    )
    k.sudo().action_activate()
    assert b.env["fix.contract.entitlement"].entitlement_active(device.id, "amc")
    visit = k.pm_visit_ids[:1] or b.env["fix.contract.pm.visit"].sudo()._guarded().create(
        {"contract_id": k.id, "device_id": device.id, "scheduled_date": b.today}
    )
    visit.sudo().action_create_service_order()
    assert visit.service_order_id.order_category == "amc"


def test_the_contract_sla_is_the_orders_sla(b):
    device = _device(b)
    policy = b.env["fix.sla.policy"].create(
        {
            "code": "B2-SLA-%s" % TAG,
            "name": "B2 4h contract SLA",
            "service_type": "onsite",
            "response_hours": 2.0,
            "resolution_hours": 4.0,
            "priority": "high",
        }
    )
    start = b.today - timedelta(days=10)
    k = _active(
        b,
        start,
        start + relativedelta(years=1) - timedelta(days=1),
        sla_policy_ids=[(6, 0, policy.ids)],
        covered_device_ids=[(6, 0, device.ids)],
    )
    order = b.env["fix.service.order"].create(
        {
            "customer_id": b.customer.id,
            "device_id": device.id,
            "branch_id": b.branch.id,
            "service_type": "walk_in",
            "fault_description": "B2 SLA",
            "contract_id": k.id,
        }
    )
    # a walk-in normal order: M01 alone picks a walk-in policy
    assert order._fix_match_sla_policy("normal") == policy
    order.contract_id = False
    assert order._fix_match_sla_policy("normal") != policy


# ===================================================== M08-F14 / F17 / F22


def test_an_entitlement_states_its_quantity(b):
    k = _contract(b, date(2027, 1, 1), date(2027, 12, 31))
    with pytest.raises(ValidationError, match="quantity"):
        b.env["fix.contract.entitlement"].with_user(b.officer).create(
            {"contract_id": k.id, "entitlement_type": "incidents"}
        )
    ent = (
        b.env["fix.contract.entitlement"]
        .with_user(b.officer)
        .create({"contract_id": k.id, "entitlement_type": "incidents", "quantity_included": 5})
    )
    assert ent.quantity_remaining == 5


def test_auto_renew_is_a_choice_and_expiry_is_announced(b):
    start = b.today - timedelta(days=300)
    k = _active(b, start, b.today + timedelta(days=20))
    assert not k.auto_renew
    b.env["fix.contract"].cron_expiring_contracts()
    assert k.expiry_notified_window == 30
    assert not k.renewal_ids, "no renewal term is drafted without auto-renew"
    assert k.sudo().activity_ids.filtered(lambda a: k.code in (a.summary or ""))


def test_the_oca_reference_is_archived(b):
    start = b.today - timedelta(days=10)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    oca = k.sudo().oca_contract_id
    assert oca and not oca.active
    assert oca not in b.env["contract.contract"].sudo().search([])


# ===================================================== M08-F16 / F15 / F21


def test_due_pm_visits_are_dispatched_by_the_daily_job(b):
    device = _device(b)
    start = b.today - timedelta(days=10)
    k = _active(
        b,
        start,
        start + relativedelta(years=1) - timedelta(days=1),
        covered_device_ids=[(6, 0, device.ids)],
    )
    visit = (
        b.env["fix.contract.pm.visit"]
        .sudo()
        ._guarded()
        .create({"contract_id": k.id, "device_id": device.id, "scheduled_date": b.today})
    )
    later = (
        b.env["fix.contract.pm.visit"]
        .sudo()
        ._guarded()
        .create(
            {
                "contract_id": k.id,
                "device_id": device.id,
                "scheduled_date": b.today + timedelta(days=40),
            }
        )
    )
    assert b.env["fix.contract.pm.visit"].cron_dispatch_due_pm_visits() >= 1
    assert visit.state == "dispatched" and visit.service_order_id.contract_id == k
    assert later.state == "scheduled"
    cron = b.env.ref("cd_contract_core.ir_cron_contract_pm_dispatch")
    assert cron.active and "cron_dispatch_due_pm_visits()" in cron.code


def test_a_monthly_entitlement_resets_with_its_period(b):
    start = b.today - relativedelta(months=2)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    ent = (
        b.env["fix.contract.entitlement"]
        .sudo()
        ._guarded()
        .create(
            {
                "contract_id": k.id,
                "entitlement_type": "visits",
                "quantity_included": 4,
                "reset_period": "monthly",
            }
        )
    )
    ent._guarded().write({"quantity_consumed": 3, "period_start": start})
    assert b.env["fix.contract.entitlement"].cron_reset_entitlements() >= 1
    assert ent.quantity_consumed == 0 and ent.quantity_remaining == 4
    assert ent.period_start == ent._fix_period_start_on(b.today) != start
    assert ent.movement_ids.filtered(lambda mv: mv.movement_type == "reset").quantity == 3
    # a term entitlement does not reset
    term = (
        b.env["fix.contract.entitlement"]
        .sudo()
        ._guarded()
        .create({"contract_id": k.id, "entitlement_type": "incidents", "quantity_included": 4})
    )
    term._guarded().write({"quantity_consumed": 3})
    b.env["fix.contract.entitlement"].cron_reset_entitlements()
    assert term.quantity_consumed == 3
    assert b.env.ref("cd_contract_core.ir_cron_contract_entitlement_reset").active


def test_a_priced_scope_change_is_prorated(b):
    """M08-F21: attaching an asset mid-term priced the whole year (or nothing)."""
    start = b.today - timedelta(days=10)
    k = _active(b, start, start + relativedelta(years=1) - timedelta(days=1))
    effective = start + relativedelta(months=6)
    printer = _device(b)
    amendment = (
        b.env["fix.contract.amendment"]
        .sudo()
        .create(
            {
                "name": "attach printer %s" % TAG,
                "contract_id": k.id,
                "kind": "scope",
                "delta_value": 12000.0,
                "effective_from": effective,
                "line_ids": [(0, 0, {"action": "attach_asset", "device_id": printer.id})],
            }
        )
    )
    assert amendment._dofa_amount() == 12000.0
    amendment._amendment_apply()
    assert amendment.state == "applied"
    assert k.annual_value == 132000.0 and printer in k.covered_device_ids
    assert k.term_value == 126000.0  # six of twelve months at the new rate
    rows = k._fix_billing_schedule()
    assert rows[0]["amount"] == 10000.0 and rows[7]["amount"] == 11000.0
    assert round(sum(r["amount"] for r in rows), 2) == 126000.0
