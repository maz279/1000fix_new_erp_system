# cd_contract_core live-ORM tests — M08 contract lifecycle (P07-M01).
#
# Runs on the real registry via addons/conftest.py `odoo_env` (fix_test,
# rolled back per test). Expected values are hand-computed in comments.
import json
import uuid
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError

# per-run tag: unique keys never collide with a concurrent run on fix_test
TAG = uuid.uuid4().hex[:6].upper()


def _events(env, event_type, aggregate, aggregate_id=None):
    domain = [("event_type", "=", event_type), ("aggregate", "=", aggregate)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    rows = env["fix.event.outbox"].search(domain, order="id")
    return [json.loads(row.payload) for row in rows]


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    brand = env["fix.brand"].create({"name": f"QA Contract Brand {TAG}", "code": f"C{TAG}"})
    model = env["fix.device.model"].create({"name": "WSI-1", "brand_id": brand.id})
    devices = env["fix.device"].create(
        [
            {"device_model_id": model.id, "serial_number": f"AC-001-{TAG}"},
            {"device_model_id": model.id, "serial_number": f"AC-002-{TAG}"},
            {"device_model_id": model.id, "serial_number": f"AC-003-{TAG}"},
        ]
    )
    partner = env["res.partner"].create({"name": "Apex Bank Ltd."})
    return SimpleNamespace(env=env, ou=ou, devices=devices, partner=partner)


def _isolated_branch(env, ou, name):
    """A branch on its OWN company: fix.entity is UNIQUE per company, so an
    entity on the shared main company would serialise every concurrent
    test run on this database behind one uncommitted row."""
    company = env["res.company"].create({"name": f"QA {name} {TAG}"})
    entity = env["fix.entity"].create(
        {"code": f"E{TAG}", "legal_name": f"QA {name} Ltd", "company_id": company.id}
    )
    return env["fix.branch"].create(
        {"code": f"B{TAG}", "name": name, "entity_id": entity.id, "operating_unit_id": ou.id}
    )


def _contract(ctx, **overrides):
    vals = {
        "operating_unit_id": ctx.ou.id,
        "name": "AMC Gold",
        "family": "amc",
        "customer_id": ctx.partner.id,
        "date_start": date(2026, 1, 1),
        "date_end": date(2026, 12, 31),
        "annual_value": 120000.0,
        # A contract that reaches 'active' in Bangladesh is a stamped,
        # executed instrument (Stamp Act 1899 Schedule I) — the fixture
        # reflects that rather than bypassing the control.
        "stamp_duty_cert_no": "SD-2026-%s" % TAG,
        "stamp_duty_amount": 300.0,
        "has_signed_contract_doc": True,
    }
    vals.update(overrides)
    return ctx.env["fix.contract"].create(vals)


def _policy(ctx, code, response, resolution, priority):
    return ctx.env["fix.sla.policy"].create(
        {
            "code": f"{code}-{TAG}",
            "name": f"SLA {code}",
            "service_type": "onsite",
            "response_hours": response,
            "resolution_hours": resolution,
            "priority": priority,
        }
    )


def _envelope(ctx, state):
    attachment = ctx.env["ir.attachment"].create({"name": "contract.pdf", "raw": b"%PDF-1.4"})
    document = ctx.env["fix.document"].create(
        {"name": "AMC contract", "attachment_id": attachment.id}
    )
    envelope = ctx.env["fix.esignature.envelope"].create(
        {"name": "AMC signing", "document_id": document.id, "operating_unit_id": ctx.ou.id}
    )
    envelope.state = state
    return envelope


# --- numbering, term ---------------------------------------------------------


def test_contracts_get_distinct_sequence_numbers(ctx):
    """Regression: without the fix.contract sequence every contract fell back
    to 'CTR/<today>' and the second one of a day hit UNIQUE(code)."""
    first, second = ctx.env["fix.contract"].create(
        [
            {
                "operating_unit_id": ctx.ou.id,
                "name": name,
                "family": "amc",
                "customer_id": ctx.partner.id,
                "date_start": date(2026, 1, 1),
                "date_end": date(2026, 12, 31),
                "annual_value": 1000.0,
            }
            for name in ("A", "B")
        ]
    )
    prefix = f"CTR/{date.today().year}/"
    assert first.code.startswith(prefix)
    assert second.code.startswith(prefix)
    assert first.code != second.code


def test_explicit_code_is_kept(ctx):
    assert _contract(ctx, code=f"AMC-{TAG}-1").code == f"AMC-{TAG}-1"


def test_defaults(ctx):
    contract = _contract(ctx)
    assert (contract.state, contract.auto_renew, contract.renewal_lead_days) == ("draft", True, 90)
    assert contract.currency_id == ctx.env.ref("base.BDT")


def test_term_end_must_follow_start(ctx):
    with pytest.raises(UserError, match="term end must be after the start"), ctx.env.cr.savepoint():
        _contract(ctx, date_end=date(2026, 1, 1))


# --- T01 OCA contract sync ---------------------------------------------------


def test_sync_creates_then_updates_the_oca_contract(ctx):
    """Regression: the sync guard tested an EMPTY recordset for truthiness,
    so no OCA contract was ever created."""
    contract = _contract(ctx)
    assert contract.action_sync_oca_contract() is True
    oca = contract.oca_contract_id
    assert oca
    assert (oca.name, oca.partner_id, oca.company_id, oca.code) == (
        "AMC Gold",
        ctx.partner,
        contract.company_id,
        contract.code,
    )
    assert (oca.date_start, oca.date_end) == (date(2026, 1, 1), date(2026, 12, 31))
    contract.name = "AMC Platinum"
    contract.action_sync_oca_contract()
    assert contract.oca_contract_id == oca  # updated in place, not duplicated
    assert oca.name == "AMC Platinum"


# --- T01 price revision ------------------------------------------------------


def test_price_revision_updates_value_posts_and_publishes(ctx):
    contract = _contract(ctx)
    assert contract.action_price_revision(150000.0, "CPI uplift") is True
    assert contract.annual_value == 150000.0
    bodies = [str(m.body) for m in contract.message_ids]
    assert any(
        "Annual value revised from 120000.0 to 150000.0. Reason: CPI uplift" in b for b in bodies
    )
    assert _events(ctx.env, "contract.price_revised", "fix.contract", contract.id) == [
        {
            "code": contract.code,
            "old_annual_value": 120000.0,
            "new_annual_value": 150000.0,
            "reason": "CPI uplift",
        }
    ]


@pytest.mark.parametrize("state", ["expired", "terminated", "pending_signature"])
def test_price_revision_refused_outside_live_states(ctx, state):
    contract = _contract(ctx, state=state)
    with (
        pytest.raises(UserError, match="Price revision can only be applied"),
        ctx.env.cr.savepoint(),
    ):
        contract.action_price_revision(1.0)


@pytest.mark.parametrize("value", [0.0, -10.0])
def test_price_revision_must_be_positive(ctx, value):
    contract = _contract(ctx, state="active")
    with pytest.raises(UserError, match="strictly positive"), ctx.env.cr.savepoint():
        contract.action_price_revision(value)
    assert contract.annual_value == 120000.0


# --- T04 SLA reconciliation --------------------------------------------------


def test_sla_without_policies_falls_back_to_standard(ctx):
    contract = _contract(ctx)
    assert contract.reconcile_service_sla() == {
        "contract_id": contract.id,
        "contract_code": contract.code,
        "reconciled": False,
        "effective_policies": [],
        "priority": "standard",
        "max_response_hours": 8.0,
        "max_resolution_hours": 48.0,
    }


def test_sla_reconciliation_uses_the_policies_own_targets(ctx):
    """Regression: the hours were read from non-existent `*_time_hours`
    attributes, so every contract reported 4h/24h."""
    gold = _policy(ctx, "AMC-G", 2.0, 12.0, "urgent")
    silver = _policy(ctx, "AMC-S", 6.0, 30.0, "normal")
    contract = _contract(ctx, sla_policy_ids=[(6, 0, [gold.id, silver.id])])
    out = contract.reconcile_service_sla()
    assert out["reconciled"] is True
    assert out["effective_policies"] == [
        {
            "policy_id": gold.id,
            "policy_name": "SLA AMC-G",
            "response_time_hours": 2.0,
            "resolution_time_hours": 12.0,
            "priority_override": "urgent",
        },
        {
            "policy_id": silver.id,
            "policy_name": "SLA AMC-S",
            "response_time_hours": 6.0,
            "resolution_time_hours": 30.0,
            "priority_override": "normal",
        },
    ]
    # the tightest bound of the two policies wins
    assert (out["priority"], out["max_response_hours"], out["max_resolution_hours"]) == (
        "urgent",
        2.0,
        12.0,
    )


def test_sla_reconciliation_is_per_contract(ctx):
    contracts = _contract(ctx) | _contract(ctx, name="Second")
    with pytest.raises(ValueError), ctx.env.cr.savepoint():
        contracts.reconcile_service_sla()


# --- T07 activation + T06 PM schedule ----------------------------------------


def test_activation_generates_pm_visits_syncs_oca_and_publishes(ctx):
    devices = ctx.devices[:2]
    contract = _contract(ctx, covered_device_ids=[(6, 0, devices.ids)])
    contract.action_activate()
    assert contract.state == "active"
    assert contract.oca_contract_id  # T01 sync runs at activation
    visits = ctx.env["fix.contract.pm.visit"].search([("contract_id", "=", contract.id)])
    # AMC every 90 days from Jan 1: Apr 1, Jun 30, Sep 28, Dec 27 (next would
    # be Mar 27 2027, past the Dec 31 term end) - for each of 2 devices
    expected_dates = [date(2026, 4, 1), date(2026, 6, 30), date(2026, 9, 28), date(2026, 12, 27)]
    assert sorted((v.scheduled_date, v.device_id.id) for v in visits) == [
        (d, dev_id) for d in expected_dates for dev_id in sorted(devices.ids)
    ]
    assert set(visits.mapped("state")) == {"scheduled"}
    assert _events(ctx.env, "contract.activated", "fix.contract", contract.id) == [
        {
            "code": contract.code,
            "family": "amc",
            "customer_id": ctx.partner.id,
            "annual_value": 120000.0,
        }
    ]


def test_activation_blocked_by_an_unsigned_envelope(ctx):
    contract = _contract(ctx, esignature_envelope_id=_envelope(ctx, "sent").id)
    with (
        pytest.raises(UserError, match="the e-signature envelope is 'sent'"),
        ctx.env.cr.savepoint(),
    ):
        contract.action_activate()
    assert contract.state == "draft"


def test_activation_with_a_completed_envelope(ctx):
    contract = _contract(ctx, esignature_envelope_id=_envelope(ctx, "completed").id)
    contract.action_activate()
    assert contract.state == "active"


def test_no_pm_visits_for_marketplace_or_uncovered_contracts(ctx):
    marketplace = _contract(ctx, family="marketplace", covered_device_ids=[(6, 0, ctx.devices.ids)])
    uncovered = _contract(ctx, name="No assets")
    (marketplace | uncovered).action_activate()
    visits = ctx.env["fix.contract.pm.visit"].search(
        [("contract_id", "in", (marketplace | uncovered).ids)]
    )
    assert not visits


def test_managed_contract_visits_monthly(ctx):
    contract = _contract(
        ctx,
        family="managed",
        date_end=date(2026, 3, 1),
        covered_device_ids=[(6, 0, ctx.devices[:1].ids)],
    )
    contract.action_activate()
    visits = ctx.env["fix.contract.pm.visit"].search([("contract_id", "=", contract.id)])
    # every 30 days from Jan 1 until Mar 1: Jan 31, Mar 2 is past the end
    assert visits.mapped("scheduled_date") == [date(2026, 1, 31)]


# --- PM visit -> service order -----------------------------------------------


def test_pm_visit_opens_an_amc_service_order_once(ctx):
    device = ctx.devices[0]
    device.branch_id = _isolated_branch(ctx.env, ctx.ou, "Dhaka HQ")
    contract = _contract(ctx, code=f"AMC-{TAG}-77", covered_device_ids=[(6, 0, device.ids)])
    visit = ctx.env["fix.contract.pm.visit"].create(
        {"contract_id": contract.id, "device_id": device.id, "scheduled_date": date(2026, 4, 1)}
    )
    visit.action_create_service_order()
    order = visit.service_order_id
    assert visit.state == "dispatched"
    assert (order.device_id, order.customer_id, order.branch_id, order.order_category) == (
        device,
        ctx.partner,
        device.branch_id,
        "amc",
    )
    assert order.fault_description == f"Preventive maintenance visit (AMC-{TAG}-77)"
    visit.action_create_service_order()  # already dispatched: no second order
    assert ctx.env["fix.service.order"].search_count([("device_id", "=", device.id)]) == 1


def test_non_amc_pm_visit_is_a_standard_order(ctx):
    device = ctx.devices[1]
    device.branch_id = _isolated_branch(ctx.env, ctx.ou, "Ctg Hub")
    contract = _contract(ctx, family="rental", covered_device_ids=[(6, 0, device.ids)])
    visit = ctx.env["fix.contract.pm.visit"].create(
        {"contract_id": contract.id, "device_id": device.id, "scheduled_date": date(2026, 7, 1)}
    )
    visit.action_create_service_order()
    assert visit.service_order_id.order_category == "standard"


# --- T05 renewal --------------------------------------------------------------


def test_renewal_escalates_and_carries_entitlements(ctx):
    contract = _contract(
        ctx,
        state="active",
        escalation_pct=10.0,
        covered_device_ids=[(6, 0, ctx.devices[:2].ids)],
        entitlement_ids=[(0, 0, {"entitlement_type": "visits", "quantity_included": 4.0})],
    )
    contract.entitlement_ids.consume(3.0)
    renewal = contract.action_renew()
    assert len(renewal) == 1
    # 120,000 * 1.10 = 132,000.00; term Jan 1 2027 .. Dec 31 2027
    assert renewal.annual_value == 132000.0
    assert (renewal.date_start, renewal.date_end) == (date(2027, 1, 1), date(2027, 12, 31))
    assert (renewal.state, renewal.name) == ("draft", "AMC Gold (renewal)")
    assert renewal.code != contract.code
    assert renewal.covered_device_ids == ctx.devices[:2]
    # Regression: entitlements did not carry (One2many is copy=False by
    # default); the renewed term starts with its FULL quantity
    assert [
        (e.entitlement_type, e.quantity_included, e.quantity_consumed, e.quantity_remaining)
        for e in renewal.entitlement_ids
    ] == [("visits", 4.0, 0.0, 4.0)]
    assert contract.state == "expired"
    assert _events(ctx.env, "contract.renewed", "fix.contract", renewal.id) == [
        {"old_code": contract.code, "new_code": renewal.code, "new_value": 132000.0}
    ]


def test_renewal_without_escalation_keeps_the_value(ctx):
    renewal = _contract(ctx, state="expired").action_renew()
    assert renewal.annual_value == 120000.0


def test_renewing_several_contracts_renews_each(ctx):
    """Regression: a `return` inside the loop renewed only the first."""
    contracts = _contract(ctx, state="active") | _contract(
        ctx, name="Second", state="expiring", annual_value=50000.0
    )
    renewals = contracts.action_renew()
    assert len(renewals) == 2
    assert sorted(renewals.mapped("annual_value")) == [50000.0, 120000.0]
    assert set(contracts.mapped("state")) == {"expired"}


def test_draft_contract_cannot_renew(ctx):
    with (
        pytest.raises(UserError, match="Only an active/expiring/expired contract renews"),
        ctx.env.cr.savepoint(),
    ):
        _contract(ctx).action_renew()


# --- AUT-015 expiring ladder --------------------------------------------------


def test_expiring_ladder_publishes_each_window(ctx):
    today = date.today()
    baseline = ctx.env["fix.contract"].cron_expiring_contracts()

    def make(name, days, **extra):
        return _contract(
            ctx,
            name=name,
            state=extra.pop("state", "active"),
            date_start=today - timedelta(days=300),
            date_end=today + timedelta(days=days),
            **extra,
        )

    in_10 = make("in 10 days", 10)  # inside 90, 60, 30 and 15
    in_45 = make("in 45 days", 45)  # inside 90 and 60
    make("in 100 days", 100)  # outside every window
    make("ends today", 0)  # date_end must be strictly in the future
    make("no auto-renew", 10, auto_renew=False)
    make("draft", 10, state="draft")
    assert ctx.env["fix.contract"].cron_expiring_contracts() == baseline + 6
    assert [
        e["window_days"] for e in _events(ctx.env, "contract.expiring", "fix.contract", in_10.id)
    ] == [
        90,
        60,
        30,
        15,
    ]
    events_45 = _events(ctx.env, "contract.expiring", "fix.contract", in_45.id)
    assert events_45 == [
        {"code": in_45.code, "window_days": 90, "date_end": str(today + timedelta(days=45))},
        {"code": in_45.code, "window_days": 60, "date_end": str(today + timedelta(days=45))},
    ]


# --- T03 entitlement drawdown -------------------------------------------------


def _entitlement(ctx, contract, **vals):
    return ctx.env["fix.contract.entitlement"].create({"contract_id": contract.id, **vals})


def test_remaining_compute_and_unlimited_sentinel(ctx):
    contract = _contract(ctx)
    limited = _entitlement(ctx, contract, quantity_included=10.0, quantity_consumed=3.0)
    unlimited = _entitlement(ctx, contract, quantity_included=0.0, quantity_consumed=5.0)
    assert limited.entitlement_type == "incidents"
    assert limited.quantity_remaining == 7.0
    assert unlimited.quantity_remaining == -1


def test_consume_draws_down_until_exhausted(ctx):
    ent = _entitlement(ctx, _contract(ctx), quantity_included=5.0)
    assert ent.consume(2.0, "SO000101") is True
    assert (ent.quantity_consumed, ent.quantity_remaining) == (2.0, 3.0)
    assert ent.consume(4.0, "SO000102") is False  # 3 left < 4 asked: never negative
    assert (ent.quantity_consumed, ent.quantity_remaining) == (2.0, 3.0)
    assert ent.consume(3.0, "SO000103") is True
    assert ent.quantity_remaining == 0.0
    assert _events(ctx.env, "entitlement.consumed", "fix.contract.entitlement", ent.id) == [
        {"qty": 2.0, "source": "SO000101", "remaining": 3.0},
        {"qty": 3.0, "source": "SO000103", "remaining": 0.0},
    ]


def test_consume_unlimited_always_succeeds(ctx):
    ent = _entitlement(ctx, _contract(ctx), quantity_included=0.0)
    assert ent.consume(7.0, "SO9") is True
    assert ent.quantity_consumed == 7.0
    assert ent.quantity_remaining == -1
    assert _events(ctx.env, "entitlement.consumed", "fix.contract.entitlement", ent.id) == [
        {"qty": 7.0, "source": "SO9", "remaining": -1}
    ]


def test_consume_on_nothing_is_refused(ctx):
    assert ctx.env["fix.contract.entitlement"].consume(1.0) is False


# --- BRU-SRM-03 entitlement_active ---------------------------------------------


def _active_amc(ctx, devices, entitlements, **extra):
    vals = {
        "state": "active",
        "covered_device_ids": [(6, 0, devices.ids)],
        "entitlement_ids": [(0, 0, line) for line in entitlements],
    }
    vals.update(extra)
    return _contract(ctx, **vals)


def test_entitlement_active_with_remaining_quantity(ctx):
    device = ctx.devices[0]
    _active_amc(ctx, device, [{"entitlement_type": "incidents", "quantity_included": 3.0}])
    Ent = ctx.env["fix.contract.entitlement"]
    assert Ent.entitlement_active(device.id, "amc") is True
    assert Ent.entitlement_active(device.id, "ramc") is False  # wrong family
    assert Ent.entitlement_active(ctx.devices[1].id, "amc") is False  # not covered


def test_entitlement_active_with_unlimited_line(ctx):
    device = ctx.devices[0]
    _active_amc(ctx, device, [{"entitlement_type": "visits", "quantity_included": 0.0}])
    assert ctx.env["fix.contract.entitlement"].entitlement_active(device.id, "amc") is True


def test_entitlement_inactive_once_drawn_down(ctx):
    """The documented check: remaining entitlement, not mere coverage."""
    device = ctx.devices[0]
    contract = _active_amc(ctx, device, [{"entitlement_type": "hours", "quantity_included": 2.0}])
    Ent = ctx.env["fix.contract.entitlement"]
    contract.entitlement_ids.consume(1.5)
    assert Ent.entitlement_active(device.id, "amc") is True  # 0.5 h left
    contract.entitlement_ids.consume(0.5)
    assert Ent.entitlement_active(device.id, "amc") is False  # exhausted


def test_entitlement_inactive_without_any_entitlement(ctx):
    device = ctx.devices[0]
    _active_amc(ctx, device, [])
    assert ctx.env["fix.contract.entitlement"].entitlement_active(device.id, "amc") is False


def test_entitlement_inactive_on_a_draft_contract(ctx):
    device = ctx.devices[0]
    _active_amc(ctx, device, [{"quantity_included": 0.0}], state="draft")
    assert ctx.env["fix.contract.entitlement"].entitlement_active(device.id, "amc") is False


def test_asset_specific_lines_only_cover_their_asset(ctx):
    covered = ctx.devices[:2]
    _active_amc(
        ctx,
        covered,
        [{"entitlement_type": "loaners", "quantity_included": 1.0, "device_id": covered[1].id}],
    )
    Ent = ctx.env["fix.contract.entitlement"]
    assert Ent.entitlement_active(covered[0].id, "amc") is False
    assert Ent.entitlement_active(covered[1].id, "amc") is True


def test_an_exhausted_contract_does_not_hide_another(ctx):
    device = ctx.devices[0]
    exhausted = _active_amc(ctx, device, [{"quantity_included": 1.0}], name="Old AMC")
    exhausted.entitlement_ids.consume(1.0)
    Ent = ctx.env["fix.contract.entitlement"]
    assert Ent.entitlement_active(device.id, "amc") is False
    _active_amc(ctx, device, [{"quantity_included": 2.0}], name="Top-up AMC")
    assert Ent.entitlement_active(device.id, "amc") is True
