# G12 (owner decision 12 Nov 2026): a billed part that was never fitted.
#
# D-11 made the close refuse an order whose approved estimate bills a stocked
# part no M15 issue covers. When the part was genuinely never fitted (not
# needed after all, the customer declined it on the bench, the wrong part was
# quoted) the order could never close: a delivered order is neither cancelled
# nor revised. The owner approved an exemption path:
#
#   * the service desk or the technician lead raises a "billed part not
#     fitted" exemption for one estimate part line: quantity, a reason code
#     and the reason in words;
#   * someone else holding branch authority (DOFA Tier 2, the branch manager)
#     decides it from the M63 inbox; the requester never decides their own;
#   * an APPROVED exemption counts as covered at the close gate;
#   * the decision is logged on the order.
#
# Every step runs as the non-admin users of the shared M01 fixture.
# ruff: noqa: F811 - `w` and `d11` are shared fixtures.
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import (  # noqa: F401 (fixtures)
    GUARD,
    _user,
    attempt,
    handover_evidence,
    order,
    w,
)
from odoo.addons.cd_service_order.tests.test_d11_billed_parts_issued import (  # noqa: F401
    LABOUR,
    _delivered,
    _fit,
    _onhand,
    _part_line,
    d11,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)

EXEMPTION = "fix.so.part.exemption"


def _ram_line(o):
    est = o._fix_governing_estimate()
    return est.line_ids.filtered(lambda line: line.line_type == "part")[:1]


def _raise(w, o, qty=1.0, user=None, code="customer_declined", reason="declined on the bench"):
    return o.with_user(user or w.clerk).action_request_part_exemption(
        _ram_line(o).id, qty, code, reason
    )


def _close_refused(w, o):
    return attempt(w, lambda: o.with_user(w.clerk).action_close()) or ""


def test_g12_an_approved_exemption_lets_the_order_close(d11):
    w = d11
    o = _delivered(w, [_part_line(w), LABOUR])
    assert "billed 1" in _close_refused(w, o)
    ex = _raise(w, o)
    assert ex._name == EXEMPTION and len(ex) == 1
    assert (ex.state, ex.requested_by_id, ex.order_id) == ("pending", w.clerk, o)
    assert ex.estimate_line_id == _ram_line(o) and ex.part_id == w.ram
    assert ex.quantity == 1.0 and ex.reason_code == "customer_declined"
    assert ex.approval_state == "pending"
    # pending is not covered: the order still cannot close
    assert "billed 1" in _close_refused(w, o)
    # the branch manager decides it from the inbox
    approve_via_inbox(ex, w.bm, requester=w.clerk)
    assert ex.state == "approved" and ex.approved_by_id == w.bm and ex.decided_on
    o.with_user(w.clerk).action_close()
    assert o.state == "closed"
    # nothing left the store: the part was never fitted
    assert _onhand(w) == 5.0
    bodies = " ".join(o.message_ids.mapped("body"))
    assert "not fitted" in bodies and w.ram.part_number in bodies
    assert "approved" in bodies.lower()


def test_g12_the_requester_never_decides_their_own_exemption(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    # a branch manager who raises it while no other one is appointed cannot
    # be routed his own request: it is refused, not self-approved
    msg = attempt(w, lambda: _raise(w, o, user=w.bm)) or ""
    assert "No one can approve" in msg
    assert not w.env[EXEMPTION].search([("order_id", "=", o.id)])
    # with a second branch manager it routes there, never back to him
    bm2 = _user(w.env, "bm2", ["cd_entity_config.group_dofa_tier_2"])
    ex = _raise(w, o, user=w.bm)
    assert bm2 in assigned(ex) and w.bm not in assigned(ex)
    assert not inbox_task(ex, w.bm)
    # and the approve method cannot be pressed directly by anyone
    assert "approver's inbox" in (attempt(w, lambda: ex.with_user(w.bm).action_apply()) or "")
    assert "approver's inbox" in (attempt(w, lambda: ex.with_user(w.clerk).action_apply()) or "")
    assert ex.state == "pending"


def test_g12_the_decider_needs_branch_authority(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    ex = _raise(w, o)
    # routed to Tier 2 holders only: the clerk2 / cashier hold no branch authority
    assert w.bm in assigned(ex)
    assert not (assigned(ex) & (w.clerk | w.clerk2 | w.cashier))
    assert ex.approval_request_id.tier == "tier_2"


def test_g12_a_rejected_exemption_does_not_count(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    ex = _raise(w, o)
    inbox_task(ex, w.bm).with_user(w.bm).action_reject(comment="it was fitted, issue it")
    assert ex.state == "rejected" and ex.decided_on and not ex.approved_by_id
    assert "billed 1" in _close_refused(w, o)
    bodies = " ".join(o.message_ids.mapped("body"))
    assert "rejected" in bodies.lower()


def test_g12_the_requester_may_withdraw_a_pending_exemption(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    ex = _raise(w, o)
    ex.with_user(w.clerk).action_recall_approval()
    assert ex.state == "withdrawn"
    # the quantity is free again for a fresh request
    assert _raise(w, o).state == "pending"


def test_g12_a_reason_is_required(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    assert attempt(w, lambda: _raise(w, o, reason="   "))
    assert attempt(w, lambda: _raise(w, o, code=""))
    assert attempt(w, lambda: _raise(w, o, code="because"))
    assert not w.env[EXEMPTION].search([("order_id", "=", o.id)])


def test_g12_quantity_is_what_was_billed_and_not_fitted(d11):
    w = d11
    o = _delivered(w, [_part_line(w, qty=2.0)])
    _fit(w, o, qty=1.0)  # one RAM was fitted and left the store
    assert attempt(w, lambda: _raise(w, o, qty=0.0))
    assert attempt(w, lambda: _raise(w, o, qty=-1.0))
    # two billed, one issued: only one can be "not fitted"
    msg = attempt(w, lambda: _raise(w, o, qty=2.0)) or ""
    assert "1" in msg and w.ram.part_number in msg
    ex = _raise(w, o, qty=1.0)
    # a second request on top of the live one is over the quantity too
    assert attempt(w, lambda: _raise(w, o, qty=1.0))
    approve_via_inbox(ex, w.bm, requester=w.clerk)
    o.with_user(w.clerk).action_close()
    assert o.state == "closed" and _onhand(w) == 4.0


def test_g12_a_part_issued_after_the_request_cannot_be_exempted(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    ex = _raise(w, o)
    _fit(w, o)  # it WAS fitted after all
    assert attempt(w, lambda: approve_via_inbox(ex, w.bm, requester=w.clerk))
    assert ex.state == "pending"


def test_g12_only_a_part_line_of_a_delivered_or_closed_order(d11):
    w = d11
    # labour is not a part
    o = _delivered(w, [_part_line(w), LABOUR])
    labour = o._fix_governing_estimate().line_ids.filtered(lambda x: x.line_type == "labour")
    assert attempt(
        w,
        lambda: o.with_user(w.clerk).action_request_part_exemption(
            labour.id, 1.0, "not_needed", "labour"
        ),
    )
    # before delivery the estimate is revised instead
    early = order(w, branch_id=w.store_branch.id)
    msg = attempt(
        w,
        lambda: early.with_user(w.clerk).action_request_part_exemption(
            _ram_line(o).id, 1.0, "not_needed", "x"
        ),
    )
    assert msg
    # another order's line is refused
    other = _delivered(w, [_part_line(w)])
    assert attempt(
        w,
        lambda: other.with_user(w.clerk).action_request_part_exemption(
            _ram_line(o).id, 1.0, "not_needed", "x"
        ),
    )


def test_g12_state_and_decision_fields_are_guarded(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    ex = _raise(w, o)
    for field, value in (
        ("state", "approved"),
        ("approved_by_id", w.bm.id),
        ("decided_on", "2026-11-12 10:00:00"),
        ("quantity", 5.0),
        ("requested_by_id", w.clerk2.id),
        ("estimate_line_id", False),
        ("reason", "changed"),
    ):
        msg = attempt(w, lambda f=field, v=value: ex.with_user(w.clerk).write({f: v}))
        assert msg and GUARD in msg, (field, msg)
    # nor born approved
    forged = attempt(
        w,
        lambda: w.env[EXEMPTION]
        .with_user(w.clerk)
        .create(
            {
                "order_id": o.id,
                "estimate_line_id": _ram_line(o).id,
                "quantity": 1.0,
                "reason_code": "not_needed",
                "reason": "x",
                "state": "approved",
            }
        ),
    )
    assert forged and GUARD in forged
    assert "billed 1" in _close_refused(w, o)


def test_g12_the_gate_reads_exemptions_with_issues(d11):
    w = d11
    o = _delivered(w, [_part_line(w, qty=3.0)])
    _fit(w, o, qty=1.0)
    ex = _raise(w, o, qty=1.0)
    approve_via_inbox(ex, w.bm, requester=w.clerk)
    gaps = o._fix_unissued_billed_parts()
    assert [(g["part"], g["billed"], g["issued"], g["exempted"]) for g in gaps] == [
        (w.ram, 3.0, 1.0, 1.0)
    ]
    msg = _close_refused(w, o)
    assert "billed 3" in msg and "issued 1" in msg and "exempted 1" in msg
