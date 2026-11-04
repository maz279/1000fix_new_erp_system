"""A02 audit P0 for M03 Service Logistics (findings M03-1 to M03-12).

The A02 probes (working/A02_evidence/probes/m02_m03/probe_m03.py) attacked
every M03 control as a plain internal user and 22 of 28 attacks got through.
Each probe is turned into a test here, as a NON-ADMIN user created in the
test, with the legitimate path checked alongside. The superuser is trusted
by the guards, so it would hide a gap; it is used only for setup.

``odoo_env`` (addons/conftest.py) rolls back after every test.
"""

import json
import types

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError, ValueError)
GUARD = "changes only through its workflow"


@pytest.fixture
def w(odoo_env, monkeypatch):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    co = env.company
    entity = env["fix.entity"].create(
        {"code": "A2PM03", "legal_name": "A02 P0 M03 entity", "company_id": co.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "A02 P0 M03 Branch",
            "code": "A2PM03",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "A2P0Brand3", "code": "A2P3"})
    model = env["fix.device.model"].create({"name": "A2P0 Phone 3", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A02 P0 M03 Customer", "phone": "01711000998"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-A2P0-3"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "pick&drop P0",
            "service_type": "collection",
        }
    )

    def mk(login, *xmlids):
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [(6, 0, groups)],
                    "company_id": co.id,
                    "company_ids": [(6, 0, [co.id])],
                    "operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )
        emp = env["hr.employee"].create({"name": login, "user_id": user.id})
        return user, emp

    rider, rider_emp = mk("a2p0_rider", "cd_consignment.group_fix_logistics_rider")
    rider2, _e = mk("a2p0_rider2", "cd_consignment.group_fix_logistics_rider")
    hub, _e = mk("a2p0_hub", "cd_consignment.group_fix_logistics_hub")
    manager, _e = mk("a2p0_mgr", "cd_consignment.group_fix_logistics_manager")
    clerk, _e = mk("a2p0_clerk")
    approver, _e = mk(
        "a2p0_approver",
        "cd_consignment.group_fix_damage_claim_approver",
        "cd_entity_config.group_dofa_tier_2",
        "cd_entity_config.group_dofa_tier_3",
        "cd_entity_config.group_dofa_tier_4",
        "cd_entity_config.group_dofa_tier_5",
    )
    approver_t2, _e = mk(
        "a2p0_approver_t2",
        "cd_consignment.group_fix_damage_claim_approver",
        "cd_entity_config.group_dofa_tier_2",
    )

    sms = []
    monkeypatch.setattr(
        env.registry["fix.consignment"],
        "_pod_send_otp",
        lambda self, phone, code: sms.append((phone, code)),
    )

    def cons(state="draft", ctype="delivery", **kw):
        rec = env["fix.consignment"].create(
            {
                "consignment_type": ctype,
                "scheduled_date": fields.Datetime.now(),
                "operating_unit_id": ou.id,
                "dest_branch_id": branch.id,
                "service_order_id": order.id,
                "rider_id": rider_emp.id,
                **kw,
            }
        )
        if state != "draft":
            rec.write({"state": state})  # setup by the superuser
        return rec

    def moving(ctype="delivery", **kw):
        """A consignment confirmed by the hub and taken into custody by the rider."""
        rec = cons(ctype=ctype, **kw)
        rec.with_user(hub).action_confirm()
        rec.with_user(rider).action_start_transit()
        return rec

    def at_door(**kw):
        rec = moving(**kw)
        rec.with_user(rider).action_out_for_delivery()
        rec.with_user(rider).action_generate_otp()
        return rec, sms[-1][1]

    def claim(amount, user=None, declared=0.0, **kw):
        c = kw.pop("consignment", None) or cons("delivered", declared_value_bdt=declared)
        return (
            env["fix.damage.claim"]
            .with_user(user or clerk)
            .create(
                {
                    "consignment_id": c.id,
                    "operating_unit_id": ou.id,
                    "description": "screen cracked in transit",
                    "claimed_amount": amount,
                    "dofa_justification": kw.pop(
                        "justification", "Photos and the hub report agree."
                    ),
                    **kw,
                }
            )
        )

    return types.SimpleNamespace(
        env=env,
        ou=ou,
        branch=branch,
        order=order,
        customer=customer,
        cons=cons,
        moving=moving,
        at_door=at_door,
        claim=claim,
        sms=sms,
        rider=rider,
        rider_emp=rider_emp,
        rider2=rider2,
        hub=hub,
        manager=manager,
        clerk=clerk,
        approver=approver,
        approver_t2=approver_t2,
    )


def p03(w, user, monkeypatch):
    """The workspace endpoints, as `user` (the controller's request mocked)."""
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    monkeypatch.setattr(g, "request", types.SimpleNamespace(env=w.env(user=user.id)))
    ctl = g.P03GenericApiController()

    def raw(fn):
        return getattr(fn, "original_endpoint", fn)

    mw = raw(g.P03GenericApiController.model_write)
    ma = raw(g.P03GenericApiController.model_action)
    return (lambda **kw: mw(ctl, **kw)), (lambda **kw: ma(ctl, **kw))


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return "%s: %s" % (type(exc).__name__, exc)
    return None


def events(env, etype, model, rec_id):
    rows = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", etype), ("aggregate", "=", model), ("aggregate_id", "=", rec_id)]
        )
    )
    return [json.loads(r.payload) for r in rows]


# ================================================================ A1 guard
def test_state_cannot_be_written_but_the_workflow_delivers(w):
    """M03-1 (probe S2a): a plain write to 'delivered' is refused; the POD
    flow delivers."""
    c = w.cons()
    for user in (w.clerk, w.rider, w.manager):
        err = refused(w.env, lambda u=user: c.with_user(u).write({"state": "delivered"}))
        assert err and GUARD in err
    c, code = w.at_door()
    c.with_user(w.rider).action_verify_pod(otp=code)
    assert c.state == "delivered" and c.delivered_at


def test_consignment_cannot_be_born_delivered(w):
    err = refused(
        w.env,
        lambda: w.env["fix.consignment"]
        .with_user(w.hub)
        .create(
            {
                "consignment_type": "delivery",
                "scheduled_date": fields.Datetime.now(),
                "operating_unit_id": w.ou.id,
                "state": "delivered",
            }
        ),
    )
    assert err and GUARD in err


def test_p03_refuses_state_and_seal_verdict_but_saves_a_plain_field(w, monkeypatch):
    """M03-1 (probe S2b)."""
    c = w.cons("in_transit", outbound_seal_number="SEAL-1")
    mw, _ma = p03(w, w.hub, monkeypatch)
    res = mw(
        model="fix.consignment",
        record_id=c.id,
        values={"state": "delivered", "seal_status": "verified"},
    )
    w.env.invalidate_all()
    assert res.get("error") and c.state == "in_transit" and c.seal_status == "intact"
    draft = w.cons()
    res = mw(model="fix.consignment", record_id=draft.id, values={"outbound_seal_number": "SEAL-9"})
    w.env.invalidate_all()
    assert not res.get("error"), res
    assert draft.outbound_seal_number == "SEAL-9"


def test_pod_stamps_cannot_be_forged(w):
    """M03-1 (probe S2d)."""
    c = w.cons("in_transit")
    err = refused(
        w.env,
        lambda: c.with_user(w.rider).write(
            {"pod_verified_at": fields.Datetime.now(), "pod_verified_by": w.rider.id}
        ),
    )
    assert err and GUARD in err
    assert not c.pod_verified_at


def test_delivered_and_lost_consignments_are_frozen(w):
    """M03-7: a closed record no longer changes, on the ORM and on the form."""
    c, code = w.at_door()
    c.with_user(w.rider).action_verify_pod(otp=code)
    err = refused(w.env, lambda: c.with_user(w.hub).write({"recipient_name": "Someone else"}))
    assert err and "closed" in err
    assert "recipient_name" in c.with_user(w.hub)._fix_form_locked_fields()
    lost = w.moving()
    lost.with_user(w.hub).action_report_lost(reason="Bike stolen")
    err = refused(w.env, lambda: lost.with_user(w.hub).write({"vehicle_registration": "DHAKA-1"}))
    assert err and "closed" in err
    # an open consignment still takes ordinary edits
    w.cons().with_user(w.hub).write({"vehicle_registration": "DHAKA-2"})


def test_dispatch_evidence_is_fixed_once_in_transit(w):
    c = w.cons(outbound_seal_number="SEAL-A")
    c.with_user(w.hub).write({"outbound_seal_number": "SEAL-B"})  # still a draft
    c.with_user(w.hub).action_confirm()
    c.with_user(w.rider).action_start_transit()
    err = refused(w.env, lambda: c.with_user(w.hub).write({"outbound_seal_number": "SEAL-C"}))
    assert err and "left dispatch" in err
    err = refused(w.env, lambda: c.with_user(w.hub).write({"declared_value_bdt": 900000.0}))
    assert err


def test_lost_is_terminal(w):
    """M03-7 (probe): a lost consignment is not delivered afterwards."""
    c, code = w.at_door()
    c.with_user(w.hub).action_report_lost(reason="Rider unreachable")
    assert events(w.env, "consignment.lost", "fix.consignment", c.id)
    err = refused(w.env, lambda: c.with_user(w.rider).action_verify_pod(otp=code))
    assert err
    err = refused(w.env, lambda: c.with_user(w.manager).action_deliver())
    assert err and "in transit" in err
    err = refused(w.env, lambda: c.with_user(w.hub).action_return(reason="found"))
    assert err
    assert c.state == "lost"


def test_delivered_is_not_returned_but_a_moving_leg_is(w):
    """M03-7 (probe): delivered -> returned refused; the real return works."""
    c, code = w.at_door()
    c.with_user(w.rider).action_verify_pod(otp=code)
    err = refused(w.env, lambda: c.with_user(w.hub).action_return(reason="customer changed mind"))
    assert err and c.state == "delivered"
    back = w.moving()
    assert refused(w.env, lambda: back.with_user(w.hub).action_return())  # a reason is required
    assert refused(w.env, lambda: back.with_user(w.rider).action_return(reason="x"))  # hub role
    back.with_user(w.hub).action_return(reason="Customer absent twice")
    assert back.state == "returned"
    assert back.custody_ids.sorted("id")[-1:].step == "returned"
    assert events(w.env, "consignment.returned", "fix.consignment", back.id)


def test_workflow_steps_need_their_role(w):
    """M03-12: a plain internal user runs none of the logistics steps."""
    c = w.cons()
    assert refused(w.env, lambda: c.with_user(w.clerk).action_confirm())
    assert refused(w.env, lambda: c.with_user(w.rider).action_confirm())  # hub step
    c.with_user(w.hub).action_confirm()
    assert refused(w.env, lambda: c.with_user(w.clerk).action_start_transit())
    c.with_user(w.rider).action_start_transit()
    assert refused(w.env, lambda: c.with_user(w.rider).action_verify_hub_intake())
    assert refused(w.env, lambda: c.with_user(w.clerk).write({"rider_id": False}))  # no write ACL


# ======================================================= A5 custody chain
def test_skipped_required_steps_break_the_chain(w):
    """M03-2 (probe): picked_up -> delivered skipped three steps silently."""
    c = w.cons("in_transit")
    scan = w.env["fix.custody.scan"]
    scan.create({"consignment_id": c.id, "step": "picked_up"})
    scan.create({"consignment_id": c.id, "step": "out_for_delivery"})
    assert c.chain_broken and "In Transit was skipped" in c.chain_problem
    # the same skip is fine with a named exception
    ok = w.cons("in_transit")
    scan.create({"consignment_id": ok.id, "step": "picked_up"})
    scan.create(
        {"consignment_id": ok.id, "step": "out_for_delivery", "exception_reason": "direct run"}
    )
    assert not ok.chain_broken


def test_delivery_needs_the_full_chain_even_with_a_pod(w):
    """M03-2: the gate re-checks the chain; a POD does not excuse a gap."""
    c = w.cons("in_transit", pod_verified_at=fields.Datetime.now())
    scan = w.env["fix.custody.scan"]
    scan.create({"consignment_id": c.id, "step": "picked_up"})
    scan._guarded().create({"consignment_id": c.id, "step": "delivered"})
    err = refused(w.env, lambda: c.action_deliver())
    assert err and "custody chain is broken" in err


def test_a_rider_cannot_type_a_terminal_scan(w):
    """M03-4 (probe 'deliver without POD'): a hand-made 'delivered' scan."""
    c = w.moving()
    err = refused(
        w.env,
        lambda: w.env["fix.custody.scan"]
        .with_user(w.rider)
        .create({"consignment_id": c.id, "step": "delivered"}),
    )
    assert err and "recorded by its transition" in err


def test_scans_are_append_only(w):
    """M03-3 (probes): backdating heals a broken chain; serial and scanner
    rewritten after delivery."""
    c, code = w.at_door()
    first = c.custody_ids.sorted("id")[:1]
    for vals in (
        {"scanned_at": fields.Datetime.add(first.scanned_at, hours=-3)},
        {"device_serial": "SN-SWAPPED"},
        {"scanned_by": w.rider_emp.id},
        {"step": "hub_scan"},
        {"location_branch_id": w.branch.id},
    ):
        err = refused(w.env, lambda v=vals: first.with_user(w.rider).write(v))
        assert err, vals
    c.with_user(w.rider).action_verify_pod(otp=code)
    err = refused(w.env, lambda: first.with_user(w.manager).write({"device_serial": "SN-SWAPPED"}))
    assert err
    assert refused(w.env, lambda: first.with_user(w.manager).unlink())


def test_scans_are_server_stamped(w):
    """M03-3 (probe): scanned_by was free input; now the server stamps it."""
    c = w.moving()
    Scan = w.env["fix.custody.scan"].with_user(w.hub)
    err = refused(
        w.env,
        lambda: Scan.create(
            {"consignment_id": c.id, "step": "hub_scan", "scanned_by": w.rider_emp.id}
        ),
    )
    assert err and "stamped by the server" in err
    err = refused(
        w.env,
        lambda: Scan.create(
            {"consignment_id": c.id, "step": "hub_scan", "scanned_at": "2026-01-01 00:00:00"}
        ),
    )
    assert err
    assert refused(
        w.env,
        lambda: w.env["fix.custody.scan"]
        .with_user(w.clerk)
        .create({"consignment_id": c.id, "step": "hub_scan"}),
    )
    s = Scan.create({"consignment_id": c.id, "step": "hub_scan"})
    assert s.scanned_by_user_id == w.hub and s.scanned_by.user_id == w.hub
    rider_scans = c.custody_ids.filtered(lambda x: x.step in ("picked_up", "in_transit"))
    assert rider_scans and rider_scans.scanned_by_user_id == w.rider
    assert rider_scans.scanned_by == w.rider_emp


def test_closed_and_draft_consignments_take_no_scans(w):
    Scan = w.env["fix.custody.scan"].with_user(w.rider)
    assert refused(w.env, lambda: Scan.create({"consignment_id": w.cons().id, "step": "picked_up"}))
    lost = w.moving()
    lost.with_user(w.hub).action_report_lost()
    assert refused(w.env, lambda: Scan.create({"consignment_id": lost.id, "step": "hub_scan"}))


# =================================================================== POD
def test_the_rider_cannot_read_the_pod_code(w):
    """M03-4 (probe): the code was a plain Char the rider read and used."""
    c, code = w.at_door()
    assert w.sms[-1][0] == "01711000998"
    assert "pod_otp" not in c._fields
    with pytest.raises(AccessError):
        c.with_user(w.rider).read(["pod_otp_hash"])
    plain = c.with_user(w.rider).read(
        [
            f
            for f in c._fields
            if f != "pod_otp_hash" and c._fields[f].store and not c._fields[f].groups
        ]
    )
    assert code not in json.dumps(plain, default=str)
    assert code not in (c.sudo().pod_otp_hash or "")


def test_a_hand_typed_code_is_not_accepted(w):
    """M03-4 (probe): write pod_otp='111111' then verify with it."""
    c = w.moving()
    c.with_user(w.rider).action_out_for_delivery()
    assert refused(w.env, lambda: c.with_user(w.rider).write({"pod_otp": "111111"}))
    assert refused(w.env, lambda: c.with_user(w.rider).write({"pod_otp_hash": "x"}))
    admin = w.env.ref("base.user_admin")  # even a system administrator
    err = refused(w.env, lambda: c.with_user(admin).write({"pod_otp_hash": "x"}))
    assert err and "cannot be set on the record" in err
    err = refused(w.env, lambda: c.with_user(w.rider).action_verify_pod(otp="111111"))
    assert err and "No POD OTP" in err
    assert c.state == "in_transit"


def test_deliver_is_not_offered_and_needs_a_pod(w, monkeypatch):
    """M03-4 (probe): the whitelisted action_deliver needed no OTP at all."""
    c = w.moving()
    c.with_user(w.rider).action_out_for_delivery()
    _mw, ma = p03(w, w.rider, monkeypatch)
    res = ma(model="fix.consignment", ids=[c.id], method="action_deliver")
    assert not res.get("success")
    err = refused(w.env, lambda: c.with_user(w.manager).action_deliver())
    assert err and "no verified proof of delivery" in err


def test_wrong_code_and_wrong_rider_are_refused(w, monkeypatch):
    c, code = w.at_door()
    err = refused(w.env, lambda: c.with_user(w.rider).action_verify_pod(otp="000000x"))
    assert err and "mismatch" in err
    err = refused(w.env, lambda: c.with_user(w.rider2).action_verify_pod(otp=code))
    assert err and "only that rider" in err
    _mw, ma = p03(w, w.rider, monkeypatch)
    res = ma(model="fix.consignment", ids=[c.id], method="action_verify_pod", kwargs={"otp": code})
    w.env.invalidate_all()
    assert res.get("success"), res
    assert c.state == "delivered" and c.pod_verified_by == w.rider
    assert not c.sudo().pod_otp_hash  # single-use


def test_pod_needs_out_for_delivery(w):
    c = w.moving()
    c.with_user(w.rider).action_generate_otp()
    err = refused(w.env, lambda: c.with_user(w.rider).action_verify_pod(otp=w.sms[-1][1]))
    assert err and "not out for delivery" in err


def test_a_code_that_cannot_be_sent_is_not_issued(w, monkeypatch):
    def fail(self, phone, code):
        raise RuntimeError("dispatcher down")

    monkeypatch.setattr(w.env.registry["fix.consignment"], "_pod_send_otp", fail)
    monkeypatch.delenv("FIX_ENV", raising=False)
    c = w.moving()
    err = refused(w.env, lambda: c.with_user(w.rider).action_generate_otp())
    assert err and "could not be sent" in err
    assert not c.sudo().pod_otp_hash


def test_a_branch_leg_closes_with_the_hub_receipt(w):
    """Pickup and branch-transfer legs end at our branch: hub intake, then
    the receiving hub signs; the rider cannot."""
    c = w.moving(ctype="pickup", outbound_seal_number="SEAL-P1")
    assert refused(w.env, lambda: c.with_user(w.rider).action_generate_otp())
    assert refused(w.env, lambda: c.with_user(w.hub).action_confirm_receipt())  # no intake yet
    assert c.with_user(w.hub).action_verify_hub_intake(inbound_seal="SEAL-P1") is True
    assert c.seal_status == "verified"
    assert refused(w.env, lambda: c.with_user(w.rider).action_confirm_receipt())
    c.with_user(w.hub).action_confirm_receipt()
    assert c.state == "delivered" and c.pod_verified_by == w.hub
    assert c.custody_summary == "Picked Up -> In Transit -> Hub Scan -> Delivered"
    assert not c.chain_broken


# ======================================================= M03-8 tamper hold
def test_seal_mismatch_verdict_persists_and_holds(w, monkeypatch):
    """M03-8 (probe): the verdict was rolled back by its own error."""
    c = w.moving(outbound_seal_number="SEAL-ORIG-1")
    _mw, ma = p03(w, w.hub, monkeypatch)
    res = ma(
        model="fix.consignment",
        ids=[c.id],
        method="action_verify_hub_intake",
        kwargs={"inbound_seal": "SEAL-OTHER-9"},
    )
    w.env.invalidate_all()
    assert res.get("success") and "Tamper Alert" in res["result"]["warning"], res
    assert c.seal_status == "tampered_mismatch" and c.state == "held"
    assert c.inbound_seal_number == "SEAL-OTHER-9" and c.hold_reason
    (event,) = events(w.env, "consignment.tamper_detected", "fix.consignment", c.id)
    assert event["inbound_seal"] == "SEAL-OTHER-9"
    # onward movement is blocked while held
    assert refused(w.env, lambda: c.with_user(w.rider).action_out_for_delivery())
    assert refused(
        w.env,
        lambda: w.env["fix.custody.scan"]
        .with_user(w.rider)
        .create({"consignment_id": c.id, "step": "hub_scan"}),
    )
    # only a manager releases it, with a reason; the verdict stays
    assert refused(w.env, lambda: c.with_user(w.hub).action_release_hold(reason="ok"))
    assert refused(w.env, lambda: c.with_user(w.manager).action_release_hold())
    c.with_user(w.manager).action_release_hold(reason="Seal replaced at origin; photos on file")
    assert c.state == "in_transit" and c.seal_status == "tampered_mismatch"
    assert c.hold_released_by_id == w.manager


def test_weight_variance_holds_too(w):
    c = w.moving(dispatch_weight_g=500.0)
    res = c.with_user(w.hub).action_verify_hub_intake(receive_weight_g="560")
    assert "Weight Variance" in res["warning"]
    assert c.state == "held" and c.seal_status == "tampered_mismatch"


def test_the_inbound_seal_cannot_be_typed_on_the_form(w, monkeypatch):
    c = w.moving(outbound_seal_number="SEAL-X")
    mw, _ma = p03(w, w.hub, monkeypatch)
    res = mw(model="fix.consignment", record_id=c.id, values={"inbound_seal_number": "SEAL-X"})
    assert res.get("error")
    assert refused(w.env, lambda: c.with_user(w.hub).write({"inbound_seal_number": "SEAL-X"}))


# ============================================================ damage claims
# A02 audit B1 (P1): the payout is a routed M63 approval. These P0 controls
# now run through the inbox (approve_via_inbox); the direct press itself is
# refused (test_a02_p1p2_cd_consignment.py).
def _inbox(cl, approver, requester=None):
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    return approve_via_inbox(cl, approver, requester=requester or cl.create_uid)


def test_claim_creator_cannot_approve_own_claim(w):
    """M03-5 (probe, SoD)."""
    cl = w.claim(4500.0, user=w.approver, declared=10000.0)
    cl.with_user(w.approver).action_request_approval()
    tasks = cl.approval_request_id.task_ids
    assert w.approver not in tasks.mapped("assigned_user_id")
    _inbox(cl, w.approver_t2)
    assert cl.state == "approved" and cl.approved_by_id == w.approver_t2
    assert cl.approved_amount == 4500.0 and cl.dofa_approved_amount == 4500.0


def test_plain_user_cannot_approve_and_tier_is_enforced(w):
    """M03-5 (probe): a BDT 200,000 Tier-4 claim approved by a plain user."""
    cl = w.claim(200000.0, declared=250000.0)
    assert cl.dofa_tier == "tier_4" and cl.dofa_tier_required == "tier_4"
    assert refused(w.env, lambda: cl.with_user(w.clerk).action_approve())
    cl.with_user(w.clerk).action_request_approval()
    assigned = cl.approval_request_id.task_ids.mapped("assigned_user_id")
    assert w.approver in assigned and w.approver_t2 not in assigned  # tier enforced
    _inbox(cl, w.approver)
    assert cl.state == "approved" and cl.dofa_approved_tier == "tier_4"


def test_payout_is_capped_at_the_claim_and_the_insured_value(w):
    """M03-5 (probe): BDT 900,000 approved on a 10,000 claim declared at 5,000."""
    cl = w.claim(10000.0, declared=5000.0)
    err = refused(w.env, lambda: cl.with_user(w.clerk).write({"requested_payout": 900000.0}))
    assert err and "cannot exceed the amount claimed" in err
    # above the declared value: Tier 4 at least, not the Tier 2 of the amount
    assert cl.dofa_tier == "tier_4"
    cl.with_user(w.clerk).action_request_approval()
    assert w.approver_t2 not in cl.approval_request_id.task_ids.mapped("assigned_user_id")
    # within the declared value the amount's own tier applies
    cl2 = w.claim(10000.0, declared=5000.0, requested_payout=5000.0)
    _inbox(cl2, w.approver_t2)
    assert cl2.state == "approved" and cl2.approved_amount == 5000.0


def test_a_justification_is_required(w):
    cl = w.claim(3000.0, declared=5000.0, justification=False)
    cl.with_user(w.clerk).action_request_approval()
    task = cl.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == w.approver_t2)
    err = refused(w.env, lambda: task.with_user(w.approver_t2).action_approve())
    assert err and "justification" in err


def test_approved_amount_is_pinned(w):
    """M03-5 (probe S4): approved at 4,000, raised to 400,000, settled."""
    cl = w.claim(4000.0, declared=5000.0)
    _inbox(cl, w.approver_t2)
    err = refused(w.env, lambda: cl.with_user(w.clerk).write({"approved_amount": 400000.0}))
    assert err and GUARD in err
    err = refused(w.env, lambda: cl.with_user(w.clerk).write({"claimed_amount": 400000.0}))
    assert err  # the decided claim is fixed
    # an in-process raise (a future revision path) voids the approval
    cl._guarded().write({"approved_amount": 4500.0})
    assert cl.state == "open" and not cl.dofa_approved and not cl.approved_by_id
    err = refused(w.env, lambda: cl.with_user(w.manager).action_settle())
    assert err and "approved claim" in err


def test_claim_state_cannot_be_forged_through_the_workspace(w, monkeypatch):
    """M03-5 (probe): an open claim written straight to SETTLED via P03."""
    cl = w.claim(30000.0)
    mw, _ma = p03(w, w.clerk, monkeypatch)
    res = mw(model="fix.damage.claim", record_id=cl.id, values={"state": "settled"})
    assert res.get("error")
    res = mw(model="fix.damage.claim", record_id=cl.id, values={"approved_amount": 900.0})
    assert res.get("error")
    # the amount the form really offers saves (the phantom *_bdt fields are gone)
    res = mw(model="fix.damage.claim", record_id=cl.id, values={"claimed_amount": 25000.0})
    w.env.invalidate_all()
    assert not res.get("error"), res
    assert cl.claimed_amount == 25000.0 and cl.state == "open"


def test_claim_buttons_run_from_the_workspace(w, monkeypatch):
    cl = w.claim(1000.0, declared=5000.0)
    _mw, ma = p03(w, w.clerk, monkeypatch)
    res = ma(
        model="fix.damage.claim",
        ids=[cl.id],
        method="action_request_approval",
        kwargs={"justification": "photos agree"},
    )
    w.env.invalidate_all()
    assert res.get("success"), res
    assert cl.approval_state == "pending" and cl.state == "open"
    other = w.claim(800.0, declared=5000.0)
    _mw, ma = p03(w, w.approver, monkeypatch)
    res = ma(
        model="fix.damage.claim",
        ids=[other.id],
        method="action_reject",
        kwargs={"reason": "pre-existing crack"},
    )
    w.env.invalidate_all()
    assert res.get("success") and other.state == "rejected" and other.rejected_by_id == w.approver


def test_settlement_is_capped_and_published(w):
    """M03-6 (probe): settling created nothing finance could act on."""
    cl = w.claim(4000.0, declared=5000.0)
    assert refused(w.env, lambda: cl.with_user(w.manager).action_settle())  # not approved
    _inbox(cl, w.approver_t2)
    assert refused(w.env, lambda: cl.with_user(w.clerk).action_settle())  # role
    err = refused(w.env, lambda: cl.with_user(w.manager).action_settle(settled_amount=4001))
    assert err and "exceeds the approved payout" in err
    cl.with_user(w.manager).action_settle(settled_amount="3500")
    assert cl.state == "settled" and cl.settled_amount == 3500.0 and cl.settled_by_id == w.manager
    (event,) = events(w.env, "damage.claim.settled", "fix.damage.claim", cl.id)
    assert event["amount"] == 3500.0 and event["currency"] == "BDT"
    err = refused(w.env, lambda: cl.with_user(w.clerk).write({"description": "rewritten"}))
    assert err


def test_the_approver_group_ships_empty(w):
    approvers = w.env.ref("cd_consignment.group_fix_damage_claim_approver")
    test_logins = {"a2p0_approver", "a2p0_approver_t2"}
    assert not approvers.user_ids.filtered(lambda u: u.login not in test_logins)
    manager = w.env.ref("cd_consignment.group_fix_logistics_manager")
    assert w.env.ref("base.user_admin") in manager.user_ids


# =================================================================== courier
def test_courier_booking_needs_a_pod(w):
    """M03-10 (probe): a booking delivered with no POD."""
    partner = w.env["fix.courier.partner"].create({"name": "A2P0 Courier", "code": "A2P0C"})
    c, code = w.at_door()
    b = (
        w.env["fix.courier.booking"]
        .with_user(w.hub)
        .create({"partner_id": partner.id, "consignment_id": c.id})
    )
    assert refused(w.env, lambda: b.with_user(w.hub).write({"state": "delivered"}))
    err = refused(w.env, lambda: b.with_user(w.hub).action_deliver())
    assert err and "no proof of delivery" in err
    assert refused(w.env, lambda: b.with_user(w.clerk).action_deliver())
    c.with_user(w.rider).action_verify_pod(otp=code)
    b.with_user(w.hub).action_deliver()
    assert b.state == "delivered" and b.delivered_on


# =================================================================== P03
def test_the_m03_forms_offer_only_real_editable_fields(w):
    """M03-11: phantom fields (approved_amount_bdt, pod_otp_code, …) were
    silently dropped, and the workflow fields were offered as inputs."""
    from odoo.addons.cd_p03_portal.controllers import a02
    from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE

    for model in ("fix.consignment", "fix.custody.scan", "fix.damage.claim", "fix.courier.booking"):
        rec = w.env[model]
        assert set(WRITABLE[model]) <= set(rec._fields), model
        assert not (set(WRITABLE[model]) & rec.browse()._fix_guarded_fields()), model
    actions = a02.SURFACES["fix.consignment"]["actions"]
    assert "action_deliver" not in actions
    assert {
        "action_confirm",
        "action_verify_hub_intake",
        "action_return",
        "action_report_lost",
    } <= actions
