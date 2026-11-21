"""Behavioural tests for the cd_service_order models on the live ORM.

``odoo_env`` (addons/conftest.py): superuser environment on fix_test, rolled back
after every test. Expected values are computed by hand in the comments.
"""

import json
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from types import SimpleNamespace

import pytest
from odoo import Command
from odoo import fields as odoo_fields
from odoo.addons.cd_service_order.models.fix_service_order import SERVICE_ORDER_STATES
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import UserError, ValidationError


@pytest.fixture
def base(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "SOMENT", "legal_name": "SO Model Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "SO Branch", "code": "SOMB", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "SoModelBrand", "code": "SOMBR"})
    device_model = env["fix.device.model"].create({"name": "SoPhone X", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "SO Customer", "phone": "01711999888"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-SOM-1"}
    )
    tech = env["hr.employee"].create({"name": "SO Technician"})
    inspector = env["hr.employee"].create({"name": "SO Inspector"})
    return SimpleNamespace(
        env=env,
        branch=branch,
        device_model=device_model,
        customer=customer,
        device=device,
        tech=tech,
        inspector=inspector,
    )


def _order(base, **vals):
    return base.env["fix.service.order"].create(
        {
            "device_id": base.device.id,
            "customer_id": base.customer.id,
            "branch_id": base.branch.id,
            "fault_description": "No display",
            **vals,
        }
    )


def _device(base, serial):
    return base.env["fix.device"].create(
        {
            "device_model_id": base.device_model.id,
            "owner_id": base.customer.id,
            "serial_number": serial,
        }
    )


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the offending operation is rolled back (flushing savepoint),
    so the records keep their last valid state and nothing invalid is left for
    the fixture's teardown flush."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


def _events(env, aggregate, rec_id, event_type=None):
    domain = [("aggregate", "=", aggregate), ("aggregate_id", "=", rec_id)]
    if event_type:
        domain.append(("event_type", "=", event_type))
    return env["fix.event.outbox"].search(domain, order="id asc")


# --- fix.service.order: state machine ---------------------------------------------


def test_group_expand_lists_every_state_in_declaration_order(base):
    states = base.env["fix.service.order"]._read_group_states(None, [], None)
    assert states == [code for code, _label in SERVICE_ORDER_STATES]
    assert states[0] == "draft" and states[-1] == "cancelled" and len(states) == 14


def test_full_lifecycle_records_history_events_and_sla_clocks(base):
    env = base.env
    order = _order(base)
    assert order.state == "draft"
    assert order.idempotency_key  # DI-04: a key is generated when none is given
    assert len(_events(env, "fix.service.order", order.id, "service_order.created")) == 1

    order.state = "intake"
    assert not order.sla_response_at
    order.action_start_diagnostic()
    # A02 ERP audit M01-F15: the response is the first diagnostic action
    response_at = order.sla_response_at
    assert response_at
    order.state = "estimate_pending"
    order.action_send_estimate()
    order.state = "awaiting_approval"
    order.action_approve()
    order.action_start_repair()
    assert order.sla_response_at == response_at  # stamped once
    order.action_submit_qc()
    env["fix.qc.checklist"].create(
        {
            "order_id": order.id,
            "qc_round": order.qc_round,
            "state": "passed",
            "item_ids": [Command.create({"name": "Boot"})],
        }
    )
    order.action_ready()
    # ... and the resolution is Ready (the resolution promise is intake to ready)
    resolved_at = order.sla_resolution_at
    assert resolved_at and resolved_at == order.ready_at
    order.action_deliver()
    assert order.sla_resolution_at == resolved_at
    order.action_close()
    assert order.state == "closed"
    assert order.sla_resolution_at == resolved_at  # not re-stamped on close

    history = base.device.history_ids.sorted("id").mapped("description")
    name = order.name
    assert history == [
        f"Order {name}: draft -> intake",
        f"Order {name}: intake -> diagnostic",
        f"Order {name}: diagnostic -> estimate_pending",
        f"Order {name}: estimate_pending -> estimate_sent",
        f"Order {name}: estimate_sent -> awaiting_approval",
        f"Order {name}: awaiting_approval -> approved",
        f"Order {name}: approved -> in_repair",
        f"Order {name}: in_repair -> qc_pending",
        f"Order {name}: qc_pending -> ready",
        f"Order {name}: ready -> delivered",
        # A02 ERP audit M01-F21: the repair warranty is issued with the handover
        f"Repair warranty issued with order {name}: 90 days",
        f"Order {name}: delivered -> closed",
    ]
    assert set(base.device.history_ids.mapped("service_order_id")) == {order}
    emitted = _events(env, "fix.service.order", order.id).mapped("event_type")
    assert emitted.count("service_order.in_repair") == 1
    payload = json.loads(
        _events(env, "fix.service.order", order.id, "service_order.closed").payload
    )
    assert payload == {
        "order_id": order.id,
        "service_order_id": order.id,  # A02 audit B2 hand-back contract
        "name": name,
        "device_id": base.device.id,
        "customer_id": base.customer.id,
        "state": "closed",
    }


def test_writing_the_current_state_is_not_a_transition(base):
    order = _order(base)
    order.write({"state": "draft"})
    assert order.state == "draft"


def test_invalid_transitions_name_the_valid_targets(base):
    order = _order(base)
    with _refused(base.env, ValidationError) as err:
        order.write({"state": "ready"})
    assert str(err.value) == (
        "Invalid state transition: draft -> ready. Valid transitions from 'draft': intake"
    )
    order.state = "intake"
    order.action_cancel(reason_code="duplicate")  # A02 M01-12: a reason code
    assert order.state == "cancelled"
    with _refused(base.env, ValidationError, r"from 'cancelled': \(terminal state\)"):
        order.state = "intake"


def test_ready_requires_a_passed_qc_checklist(base):
    order = _order(base)
    for state in ("intake", "diagnostic", "estimate_pending", "estimate_sent"):
        order.state = state
    order.write({"state": "awaiting_approval"})
    order.write({"state": "approved"})
    order.write({"state": "in_repair"})
    order.write({"state": "qc_pending"})
    with _refused(base.env, UserError, "has no QC checklist"):
        order.action_ready()
    base.env["fix.qc.checklist"].create(
        {"order_id": order.id, "qc_round": order.qc_round, "state": "passed"}
    )
    base.env["fix.qc.checklist"].create(
        {"order_id": order.id, "qc_round": order.qc_round, "state": "failed"}
    )
    # A02 ERP audit M01-F4: the newest inspection decides
    with _refused(base.env, UserError, "latest QC checklist is failed"):
        order.action_ready()
    assert order.state == "qc_pending"


def test_plain_write_to_ready_is_held_by_the_qc_gate(base):
    """Regression: the QC gate lived only in action_ready — a direct
    write({'state': 'ready'}) (RPC, controller, sync) skipped it."""
    order = _order(base)
    for state in ("intake", "diagnostic", "estimate_pending", "estimate_sent"):
        order.state = state
    for state in ("awaiting_approval", "approved", "in_repair", "qc_pending"):
        order.write({"state": state})
    with _refused(base.env, UserError, "has no QC checklist"):
        order.write({"state": "ready"})
    base.env["fix.qc.checklist"].create(
        {"order_id": order.id, "qc_round": order.qc_round, "state": "failed"}
    )
    with _refused(base.env, UserError, "latest QC checklist is failed"):
        order.state = "ready"
    assert order.state == "qc_pending"
    order.qc_checklist_ids.write({"state": "passed"})
    order.write({"state": "ready"})
    assert order.state == "ready"


# --- fix.service.order: W2 business-line actions -----------------------------------


def test_swap_device_requires_an_existing_replacement(base):
    order = _order(base)
    with _refused(base.env, UserError, "does not exist"):
        order.action_swap_device(999999999)
    spare = _device(base, "SN-SOM-SWAP")
    order.action_swap_device(spare.id, reason="sla_breach_risk", grade="grade_b")
    assert (order.is_swap_out, order.swap_device_id, order.swap_reason) == (
        True,
        spare,
        "sla_breach_risk",
    )
    assert (order.swap_condition_grade, order.swap_logistics_status) == ("grade_b", "dispatched")
    assert "FR-SRM-064" in order.message_ids[0].body
    assert _events(base.env, "fix.service.order", order.id, "service_order.device_swapped")


def test_defer_pauses_and_resume_restarts_the_sla_clock(base):
    order = _order(base)
    order.action_defer_order(reason="customer_travel", resume_date=date(2026, 11, 2), notes="Away")
    assert (order.is_deferred_block, order.sla_clock_paused) == (True, True)
    assert (order.deferred_reason, order.deferred_until, order.deferred_notes) == (
        "customer_travel",
        date(2026, 11, 2),
        "Away",
    )
    assert "Resumption target: 2026-11-02." in order.message_ids[0].body
    order.action_defer_order()
    assert "Resumption target: Indefinite." in order.message_ids[0].body
    order.action_resume_order()
    assert (order.is_deferred_block, order.sla_clock_paused) == (False, False)
    assert "processing resumed" in order.message_ids[0].body
    assert len(_events(base.env, "fix.service.order", order.id, "service_order.deferred")) == 2
    assert _events(base.env, "fix.service.order", order.id, "service_order.resumed")


# --- fix.service.order: creation gates ------------------------------------------


def test_idempotency_key_replay_returns_the_existing_order(base):
    first = _order(base, idempotency_key="IDEM-SOM-1")
    again = _order(base, idempotency_key="IDEM-SOM-1", fault_description="retried POST")
    assert again == first
    assert first.fault_description == "No display"
    assert base.env["fix.service.order"].search_count([("idempotency_key", "=", "IDEM-SOM-1")]) == 1


def test_batch_with_a_replayed_key_still_creates_the_other_orders(base):
    """Regression: the first replayed key RETURNED from create, dropping the rest."""
    first = _order(base, idempotency_key="IDEM-SOM-2")
    other = _device(base, "SN-SOM-2")
    common = {"customer_id": base.customer.id, "branch_id": base.branch.id}
    batch = base.env["fix.service.order"].create(
        [
            dict(common, device_id=other.id, fault_description="new A"),
            dict(
                common,
                device_id=base.device.id,
                fault_description="dup",
                idempotency_key="IDEM-SOM-2",
            ),
            dict(
                common, device_id=other.id, fault_description="new B", idempotency_key="IDEM-SOM-3"
            ),
        ]
    )
    assert len(batch) == 3
    assert batch[1] == first
    assert batch.mapped("fault_description") == ["new A", "No display", "new B"]
    assert batch[2].idempotency_key == "IDEM-SOM-3"
    assert batch[0].idempotency_key not in (False, "IDEM-SOM-2", "IDEM-SOM-3")


def _biz_today(base):
    """The date the BUSINESS is on, not the date this machine is on.

    Bangladesh is UTC+6. The warranty gate decides cover on
    `fields.Date.context_today`, so a test that builds its windows from
    Python's `date.today()` asserts the runner's timezone: for the first six
    hours of every Dhaka day - and across a month boundary, by a whole month -
    the two disagree and these tests failed on correct code (A04 audit,
    2026-11-01).
    """
    return odoo_fields.Date.context_today(base.env.user)


def _warranted_device(base, serial, status="active", start=-30, end=335):
    device = _device(base, serial)
    today = _biz_today(base)
    base.env["fix.warranty"].create(
        {
            "device_id": device.id,
            "status": status,
            "start_date": today + timedelta(days=start),
            "end_date": today + timedelta(days=end),
        }
    )
    return device


def test_warranty_order_accepted_for_a_device_under_warranty(base):
    """Regression: the gate compared warranty_status with "active", a value the
    field never takes, so EVERY warranty order was refused (P01 booking, P04
    corporate request)."""
    covered = _warranted_device(base, "SN-SOM-WTY")
    assert covered.warranty_status == "in_warranty"
    order = _order(base, device_id=covered.id, order_category="warranty")
    assert (order.order_category, order.device_id) == ("warranty", covered)
    # the last covered day still counts
    last_day = _warranted_device(base, "SN-SOM-LAST", start=-365, end=0)
    assert _order(base, device_id=last_day.id, order_category="warranty").id


@pytest.mark.parametrize(
    ("serial", "warranty", "status_label"),
    [
        ("SN-SOM-NONE", None, "unknown"),
        ("SN-SOM-EXP", {"end": -1}, "out_of_warranty"),
        ("SN-SOM-VOID", {"status": "voided"}, "unknown"),
        ("SN-SOM-PEND", {"status": "pending"}, "unknown"),
        ("SN-SOM-FUT", {"start": 5, "end": 370}, "in_warranty"),  # not started yet
    ],
)
def test_warranty_order_refused_without_cover_on_the_request_date(
    base, serial, warranty, status_label
):
    device = (
        _device(base, serial) if warranty is None else _warranted_device(base, serial, **warranty)
    )
    with _refused(base.env, UserError) as err:
        _order(base, device_id=device.id, order_category="warranty")
    assert str(err.value) == (
        f"BRU-SRM-02: device {device.display_name} has no active warranty on {_biz_today(base)} "
        f"(warranty status '{status_label}') — a warranty order needs an ACTIVE warranty at "
        "the request date"
    )
    assert _order(base, device_id=device.id).order_category == "standard"  # paid order is fine


def test_return_within_30_days_is_flagged_as_rework(base):
    # A02 M01-1 / BRU-SRM-06: same device AND same fault category.
    fault = [Command.create({"fault_code": "DSP-01", "description": "No display"})]
    original = _order(base, fault_line_ids=fault)
    # A02 ERP audit M01-F21: the original is a repair handed back (delivered)
    base.env.cr.execute(
        "UPDATE fix_service_order SET state = 'delivered', delivered_at = %s WHERE id = %s",
        (odoo_fields.Datetime.now(), original.id),
    )
    original.invalidate_recordset()
    unrelated = _order(base, fault_description="Battery swelling")
    assert not unrelated.is_rework
    repeat = _order(base, fault_description="No display again", fault_line_ids=fault)
    assert (repeat.is_rework, repeat.rework_of_id) == (True, original)
    assert "flagged as rework" in repeat.message_ids[0].body
    assert original.name in repeat.message_ids[0].body
    preset = _order(base, is_rework=True)  # already classified: not re-linked
    assert not preset.rework_of_id
    fresh = _device(base, "SN-SOM-FRESH")
    first_visit = _order(base, device_id=fresh.id)
    assert not first_visit.is_rework


def test_cancelled_order_does_not_make_a_return_a_rework(base):
    fault = [Command.create({"fault_code": "DSP-01", "description": "No display"})]
    first = _order(base, fault_line_ids=fault)
    first.state = "intake"
    first.action_cancel(reason_code="duplicate")
    assert not _order(base, fault_line_ids=fault).is_rework


# --- fix.estimate ----------------------------------------------------------------


def _estimate(base, lines=(("part", 2, 1500.0), ("labour", 1, 500.0)), **vals):
    order = _order(base)
    return base.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "line_ids": [
                Command.create(
                    {
                        "line_type": kind,
                        "description": f"{kind} line",
                        "quantity": qty,
                        "unit_price": price,
                    }
                )
                for kind, qty, price in lines
            ],
            **vals,
        }
    )


def test_estimate_totals_apply_discount_before_vat(base):
    est = _estimate(base, discount=200.0)
    # parts 2 x 1500 = 3000; labour 500; subtotal 3500 - 200 = 3300;
    # VAT 15% = 495.00; grand total 3795.00
    assert (est.parts_total, est.labour_total, est.diagnostic_total) == (3000.0, 500.0, 0.0)
    assert (est.vat_amount, est.grand_total) == (495.0, 3795.0)
    assert est.line_ids.mapped("line_total") == [3000.0, 500.0]


def test_diagnostic_fee_is_charged_and_taxed(base):
    """Regression: diagnostic lines were summed into no total - a charged
    diagnostic fee never reached the subtotal, the VAT base or the grand total."""
    est = _estimate(
        base,
        lines=(("part", 1, 1450.0), ("labour", 1.5, 1200.0), ("diagnostic", 1, 500.0)),
        discount=250.0,
    )
    # parts 1450; labour 1.5 x 1200 = 1800; diagnostic 500
    # subtotal 1450 + 1800 + 500 - 250 = 3500; VAT 15% = 525; grand total 4025
    assert (est.parts_total, est.labour_total, est.diagnostic_total) == (1450.0, 1800.0, 500.0)
    assert (est.vat_amount, est.grand_total) == (525.0, 4025.0)


def test_rf009_sample_estimate_with_a_waived_diagnostic_fee(base):
    """RF-009 4.2.3: the waived diagnostic fee is a 0.00 line - subtotal 3,250.00,
    VAT 487.50, total payable 3,737.50."""
    est = _estimate(
        base, lines=(("part", 1, 1450.0), ("labour", 1.5, 1200.0), ("diagnostic", 1, 0.0))
    )
    assert est.diagnostic_total == 0.0
    assert (est.vat_amount, est.grand_total) == (487.5, 3737.5)


def test_a_diagnostic_only_estimate_can_be_sent(base):
    est = _estimate(base, lines=(("diagnostic", 1, 300.0),), discount=300.0)
    # the fee itself bounds the discount: 300 - 300 = 0, nothing payable
    assert (est.diagnostic_total, est.grand_total) == (300.0, 0.0)
    est.action_send()
    assert est.state == "sent"


def test_discount_is_bounded_by_parts_labour_and_diagnostic(base):
    with _refused(base.env, ValidationError, "cannot be negative"):
        _estimate(base, discount=-1.0)
    with _refused(base.env, ValidationError) as err:
        _estimate(base, discount=4000.0)
    assert str(err.value) == (
        "The discount (4000.00) cannot exceed the parts, labour and diagnostic total (3500.00)."
    )
    # a diagnostic fee raises the bound: 3000 + 500 + 600 = 4100 >= 4000
    with_fee = _estimate(
        base,
        lines=(("part", 2, 1500.0), ("labour", 1, 500.0), ("diagnostic", 1, 600.0)),
        discount=4000.0,
    )
    # (4100 - 4000) = 100, + 15% = 115
    assert with_fee.grand_total == 115.0
    # the R01 case: no lines and discount 200 (grand total used to be -200.30)
    with _refused(base.env, ValidationError, r"\(200.00\) cannot exceed .* \(0.00\)"):
        _estimate(base, lines=(), discount=200.0)
    assert _estimate(base, discount=3500.0).grand_total == 0.0  # the full amount is allowed


def test_line_changes_cannot_push_the_total_under_the_discount(base):
    """Regression: the discount check ran only on estimate writes."""
    env = base.env
    est = _estimate(base, discount=3000.0)
    part, labour = est.line_ids
    with _refused(env, ValidationError, r"\(3000.00\) cannot exceed .* \(2000.00\)"):
        part.unit_price = 750.0  # 2 x 750 + 500 = 2000 < 3000
    part.line_type = "diagnostic"  # re-typed: moves between the totals (a depends regression)
    assert (est.parts_total, est.diagnostic_total, est.grand_total) == (0.0, 3000.0, 575.0)
    part.line_type = "part"
    assert (est.parts_total, est.diagnostic_total) == (3000.0, 0.0)
    with _refused(env, ValidationError, r"cannot exceed .* \(500.00\)"):
        part.unlink()
    assert est.line_ids == part | labour
    labour.unit_price = 1000.0  # raising a price is always fine
    # (3000 + 1000 - 3000) = 1000 subtotal, + 15% VAT 150 = 1150
    assert est.grand_total == 1150.0
    labour.unlink()  # the 3000 of parts still cover the 3000 discount
    assert (est.line_ids, est.grand_total) == (part, 0.0)


def test_send_and_approve_refuse_an_empty_estimate(base):
    empty = _estimate(base, lines=())
    with _refused(base.env, UserError) as err:
        empty.action_send()
    assert str(err.value) == (
        "An estimate with no parts, labour or diagnostic lines cannot be sent to the customer."
    )
    with _refused(base.env, UserError, "lines cannot be approved"):
        empty.action_approve()
    assert empty.state == "draft"
    assert not _events(base.env, "fix.estimate", empty.id)


def test_send_emits_estimate_sent(base):
    est = _estimate(base)
    est.action_send()
    assert est.state == "sent"
    event = _events(base.env, "fix.estimate", est.id)
    assert event.event_type == "estimate.sent"
    assert json.loads(event.payload) == {
        "estimate_id": est.id,
        "order_id": est.order_id.id,
        # A02 audit B2: the S2/S3 hand-back contract key
        "service_order_id": est.order_id.id,
        "version": 1,
        "state": "sent",
        # (3000 + 500) * 1.15
        "grand_total": 4025.0,
    }


def test_approval_up_to_5000_needs_no_documented_consent(base):
    est = _estimate(base, lines=(("part", 1, 4000.0),))  # 4000 * 1.15 = 4600
    est.action_send()  # A02 M01-4: only a sent estimate is approved
    est.action_approve()
    assert (est.state, bool(est.approved_at)) == ("approved", True)
    assert _events(base.env, "fix.estimate", est.id, "estimate.approved")


def test_approval_above_5000_needs_the_customer_approval_ref(base):
    est = _estimate(base, lines=(("part", 1, 5000.0),))  # 5750 > 5000
    est.action_send()
    with _refused(base.env, UserError, "BRU-SRM-07.*above BDT 5000"):
        est.action_approve()
    est.customer_approval_ref = "OTP-1234"
    est.action_approve()
    assert est.state == "approved"


def test_approval_above_25000_needs_customer_then_manager(base):
    est = _estimate(base, lines=(("part", 1, 30000.0),))  # 34500 > 25000
    est.action_send()
    with _refused(base.env, UserError, "BRU-SRM-07.*above BDT 25000"):
        est.action_approve()
    with _refused(base.env, UserError, "customer approval must be documented"):
        est.action_manager_approve()
    est.customer_approval_ref = "SIG-77"
    with _refused(base.env, UserError, "BRU-SRM-08"):
        est.action_approve()
    # The second key is a branch manager's (DOFA Tier 2), and not the
    # preparer's own: whoever called this used to become the manager.
    manager = base.env["res.users"].create(
        {
            "name": "Branch Manager",
            "login": "so-branch-manager@a02.test",
            "group_ids": [
                (
                    6,
                    0,
                    [
                        base.env.ref("base.group_user").id,
                        base.env.ref("cd_entity_config.group_dofa_tier_2").id,
                    ],
                )
            ],
        }
    )
    # A02 audit B1: the key is requested, and given from the manager's M63
    # inbox; pressed directly by the manager it is refused.
    with _refused(base.env, UserError, "approver's inbox"):
        est.with_user(manager).action_manager_approve()
    est.action_request_manager_key("34.5k repair")
    req = base.env["fix.so.approval"].search([("estimate_id", "=", est.id)], limit=1)
    approve_via_inbox(req, manager)
    assert est.manager_approval_uid == manager
    est.action_approve()
    assert est.state == "approved"


def test_manager_approval_is_not_recorded_at_or_below_25000(base):
    est = _estimate(base, lines=(("part", 1, 1000.0),))
    est.action_manager_approve()
    assert not est.manager_approval_uid


def test_reject_emits_estimate_rejected(base):
    est = _estimate(base)
    est.action_send()  # A02 M01-4: the customer rejects a SENT estimate
    est.action_reject()
    assert est.state == "rejected"
    assert _events(base.env, "fix.estimate", est.id, "estimate.rejected")


def test_revision_is_a_new_draft_version_with_the_lines(base):
    """Regression: One2many lines are not copied by default - revisions were empty."""
    est = _estimate(base, customer_approval_ref="OTP-9")
    est.action_send()
    est.action_approve()
    action = est.action_revise()
    new = base.env["fix.estimate"].browse(action["res_id"])
    assert action == {
        "type": "ir.actions.act_window",
        "res_model": "fix.estimate",
        "res_id": new.id,
        "view_mode": "form",
    }
    assert (new.version, new.state, new.order_id) == (2, "draft", est.order_id)
    assert [(line.line_type, line.quantity, line.unit_price) for line in new.line_ids] == [
        ("part", 2.0, 1500.0),
        ("labour", 1.0, 500.0),
    ]
    assert new.line_ids != est.line_ids  # copies, not shared lines
    assert (new.customer_approval_ref, new.approved_at) == (False, False)
    assert new.grand_total == est.grand_total == 4025.0


# --- fix.qc.checklist ------------------------------------------------------------


def test_qc_checklist_completion(base):
    order = _order(base)
    qc = base.env["fix.qc.checklist"].create({"order_id": order.id})
    assert qc.all_passed is False  # no items is never "all passed"
    with _refused(base.env, ValidationError, "at least one item"):
        qc.action_complete()
    qc.item_ids = [Command.create({"name": "Screen", "passed": True})]
    qc.item_ids = [Command.create({"name": "Charging", "passed": False})]
    qc.action_complete()
    assert (qc.state, bool(qc.checked_at)) == ("failed", True)
    # A02 M01-6: a completed inspection is evidence; the re-test is a new one.
    with _refused(base.env, UserError, "already failed"):
        qc.action_complete()
    retest = base.env["fix.qc.checklist"].create(
        {"order_id": order.id, "item_ids": [Command.create({"name": "Charging", "passed": True})]}
    )
    assert retest.all_passed is True
    retest.action_complete()
    assert retest.state == "passed"


def test_qc_inspector_must_not_be_the_repairing_technician(base):
    order = _order(base)
    wo = base.env["fix.work.order"].create(
        {"order_id": order.id, "technician_id": base.tech.id, "certification_waiver": True}
    )
    qc_model = base.env["fix.qc.checklist"]
    with _refused(base.env, ValidationError, "BRU-SRM-18"):
        qc_model.create(
            {"order_id": order.id, "work_order_id": wo.id, "inspector_id": base.tech.id}
        )
    ok = qc_model.create(
        {"order_id": order.id, "work_order_id": wo.id, "inspector_id": base.inspector.id}
    )
    assert ok.inspector_id == base.inspector
    assert qc_model.create({"order_id": order.id, "inspector_id": base.tech.id})  # no work order


# --- fix.sla.policy / fix.diagnostic.node -------------------------------------------


def test_sla_targets_must_be_positive_and_ordered(base):
    policy = base.env["fix.sla.policy"]
    vals = {"code": "SOM-SLA", "name": "Walk-in normal", "service_type": "walk_in"}
    with _refused(base.env, ValidationError, "must be positive"):
        policy.create(dict(vals, response_hours=0, resolution_hours=8))
    with _refused(base.env, ValidationError, "must be positive"):
        policy.create(dict(vals, response_hours=2, resolution_hours=-1))
    with _refused(base.env, ValidationError, "cannot exceed resolution"):
        policy.create(dict(vals, response_hours=9, resolution_hours=8))
    ok = policy.create(dict(vals, response_hours=8, resolution_hours=8))
    assert (ok.response_hours, ok.resolution_hours, ok.priority) == (8.0, 8.0, "normal")


def test_diagnostic_tree_terminal_and_cycle_rules(base):
    node = base.env["fix.diagnostic.node"]
    with _refused(base.env, ValidationError, "terminal diagnostic node must carry"):
        node.create({"name": "Dead?", "code": "SOM-D0"})
    root = node.create(
        {
            "name": "Powers on?",
            "code": "SOM-D1",
            "children_ids": [
                Command.create({"name": "No - PSU", "code": "SOM-D1A", "fault_code": "F-PSU"})
            ],
        }
    )
    leaf = root.children_ids
    assert (root.is_terminal, leaf.is_terminal) == (False, True)
    env = base.env
    with _refused(env, ValidationError, "Only terminal nodes carry a fault code"):
        root.fault_code = "F-ROOT"
    with _refused(env, ValidationError, "contains a cycle"):
        root.parent_id = leaf
    assert not root.parent_id and not root.fault_code


# --- fix.work.order ----------------------------------------------------------------


def test_work_order_name_and_duration(base):
    order = _order(base)
    wo = base.env["fix.work.order"].create(
        {"order_id": order.id, "sequence": 3, "start_time": datetime(2026, 10, 22, 8, 0)}
    )
    assert wo.name == f"{order.name}/W03"
    assert wo.duration_hours == 0.0  # still open
    wo.end_time = datetime(2026, 10, 22, 10, 30)
    assert wo.duration_hours == 2.5
