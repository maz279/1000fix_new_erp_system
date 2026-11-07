# A06 control suite, M42 Supplier Relationship & Performance (A06 workflow
# audit 2026-11-03).
#
# One test per gap probe of working/A06_evidence/probes/m42/probe_m42.py (named
# after the probe id): the same attack as a NON-ADMIN user created in the
# transaction, now refused, plus proper-path tests showing a steward and an
# approver can still onboard, govern and pay a supplier. Rolled back.
import base64
import json
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

try:
    from psycopg2 import IntegrityError
except Exception:  # pragma: no cover
    IntegrityError = Exception

REFUSED = (UserError, ValidationError, AccessError, IntegrityError)
GS = "cd_vendor_portal.group_fix_supplier_steward"
GSA = "cd_vendor_portal.group_fix_supplier_approver"
CFO = "cd_entity_config.group_dofa_tier_4"
GUARD = "changes only through its workflow"
DOCS = ("trade_licence", "tin", "vat")
SCREENINGS = ("sanctions", "coi", "abac")
PDF = base64.b64encode(b"%PDF-1.4 a06 m42 evidence")


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env["fix.supplier"])
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.plain = _user(env, "a06m42t_plain")
    x.steward = _user(env, "a06m42t_steward", [GS])
    x.steward2 = _user(env, "a06m42t_steward2", [GS])
    x.approver = _user(env, "a06m42t_approver", [GSA])
    x.approver2 = _user(env, "a06m42t_approver2", [GSA])
    x.cfo_approver = _user(env, "a06m42t_cfo_approver", [GSA, CFO])
    x.acct = _user(env, "a06m42t_acct", ["account.group_account_user"])
    x.prod = env["product.product"].create({"name": "A06M42T Part"})
    return x


def supplier(c, user=None, **kw):
    c.n += 1
    partner = c.env["res.partner"].create({"name": "A06M42T Supplier %d" % c.n, "is_company": True})
    vals = {"name": partner.name, "partner_id": partner.id}
    vals.update(kw)
    return c.env["fix.supplier"].with_user(user or c.steward).create(vals)


def docs(c, s, verify=True, valid_to=None):
    out = c.env["fix.supplier.document"]
    for t in DOCS:
        out |= (
            c.env["fix.supplier.document"]
            .with_user(c.steward)
            .create(
                {
                    "supplier_id": s.id,
                    "doc_type": t,
                    "number": "%s-%s" % (t, s.id),
                    "file_ref": "dms://suppliers/%s/%s" % (s.id, t),
                    "file": PDF,
                    "valid_to": valid_to or c.today + timedelta(days=365),
                }
            )
        )
    if verify:
        out.with_user(c.steward2).action_verify()
    return out


def cleared_screenings(c, s):
    for key in SCREENINGS:
        rec = (
            c.env["fix.supplier.screening"]
            .with_user(c.steward)
            .create({"supplier_id": s.id, "screening_type": key, "result": "clear"})
        )
        rec.with_user(c.steward).action_clear()


def qual(c, s, score=80, approve=True):
    q = (
        c.env["fix.supplier.qualification"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "score": score})
    )
    if approve:
        q.with_user(c.steward).action_start()
        q.with_user(c.approver).action_approve()
    return q


def gate(c, s, q, user=None):
    return (
        c.env["fix.supplier.activation"]
        .with_user(user or c.steward)
        .create({"supplier_id": s.id, "qualification_id": q.id if q else False})
    )


def active_supplier(c):
    s = supplier(c)
    docs(c, s)
    cleared_screenings(c, s)
    q = qual(c, s)
    gate(c, s, q).with_user(c.approver).action_activate()
    assert s.status == "active"
    return s


def _po_gate(c, partner):
    return c.env["fix.purchase.order"]._fix_vendor_blockers(partner)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    as_user(c.steward)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), as_user=as_user
        )
    finally:
        g.request, s.request = old_g, old_s


# =================================================================== S: register / status
def test_m42_S01_supplier_cannot_be_born_active(c):
    with pytest.raises(UserError, match=GUARD):
        supplier(c, status="active")
    with pytest.raises(AccessError):
        supplier(c, user=c.plain)


def test_m42_S02_status_write_refused(c):
    s = supplier(c)
    with pytest.raises(UserError, match=GUARD):
        s.with_user(c.steward).write({"status": "active"})


def test_m42_S03_p03_status_write_refused(c, p03):
    s = supplier(c)
    out = p03.write(model="fix.supplier", record_id=s.id, values={"status": "active"})
    s.invalidate_recordset()
    assert "error" in out and s.status == "prospect"


def test_m42_S04_partner_unique(c):
    s = supplier(c)
    with pytest.raises(REFUSED):
        c.env["fix.supplier"].with_user(c.steward).create(
            {"name": "dup", "partner_id": s.partner_id.id}
        )
        c.env.flush_all()


# =================================================================== G: activation gate
def test_m42_G01_gate_blocks_without_qualification(c):
    s = supplier(c)
    docs(c, s)
    with pytest.raises(UserError, match="no approved qualification"):
        gate(c, s, None).with_user(c.approver).action_activate()
    assert s.status == "prospect"


def test_m42_G02_gate_blocks_on_expired_documents(c):
    s = supplier(c)
    d = docs(c, s, verify=False)
    d[0].sudo()._guarded().write({"state": "valid", "valid_to": c.today - timedelta(days=1)})
    d[1:].with_user(c.steward2).action_verify()
    with pytest.raises(UserError, match="Activation blocked"):
        gate(c, s, qual(c, s)).with_user(c.approver).action_activate()
    assert s.status != "active"


def test_m42_G03_documents_cannot_be_self_certified(c):
    s = supplier(c)
    with pytest.raises(UserError, match=GUARD):
        c.env["fix.supplier.document"].with_user(c.steward).create(
            {"supplier_id": s.id, "doc_type": "trade_licence", "state": "valid"}
        )
    bare = (
        c.env["fix.supplier.document"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "doc_type": "trade_licence"})
    )
    with pytest.raises(UserError, match="number and the uploaded file"):
        bare.with_user(c.steward2).action_verify()
    own = docs(c, s, verify=False)
    with pytest.raises(UserError, match="Segregation"):
        own.with_user(c.steward).action_verify()
    with pytest.raises(UserError, match="Activation blocked"):
        gate(c, s, qual(c, s)).with_user(c.approver).action_activate()


def test_m42_G04_one_user_cannot_create_qualify_and_activate(c):
    emp = c.env["hr.employee"].create({"name": "buyer emp", "user_id": c.approver.id})
    s = supplier(c, buyer_id=emp.id)
    docs(c, s)
    cleared_screenings(c, s)
    zero = qual(c, s, score=0, approve=False)
    zero.with_user(c.steward).action_start()
    with pytest.raises(UserError, match="threshold"):
        zero.with_user(c.approver2).action_approve()
    q = qual(c, s, approve=False)
    q.with_user(c.steward).action_start()
    with pytest.raises(UserError, match=r"Qualification|role"):
        q.with_user(c.steward).action_approve()
    with pytest.raises(UserError, match="Segregation"):
        q.with_user(c.approver).action_approve()  # the supplier's own buyer
    q.with_user(c.approver2).action_approve()
    g = gate(c, s, q)
    with pytest.raises(UserError, match="Segregation"):
        g.with_user(c.approver).action_activate()  # its buyer
    with pytest.raises(UserError, match="role"):
        g.with_user(c.steward).action_activate()
    g.with_user(c.approver2).action_activate()
    assert s.status == "active" and g.activated_by_id == c.approver2


def test_m42_G04b_preparer_cannot_activate(c):
    preparer = _user(c.env, "a06m42t_steward_approver", [GS, GSA])
    s = supplier(c)
    docs(c, s)
    q = qual(c, s)
    g = gate(c, s, q, user=preparer)
    with pytest.raises(UserError, match="Segregation"):
        g.with_user(preparer).action_activate()


def test_m42_G05_qualification_state_write_refused(c):
    s = supplier(c)
    docs(c, s)
    q = qual(c, s, approve=False)
    with pytest.raises(UserError, match=GUARD):
        q.with_user(c.steward).write({"state": "approved"})


def test_m42_G05b_approved_score_is_final(c):
    s = supplier(c)
    q = qual(c, s)
    with pytest.raises(UserError, match="final"):
        q.with_user(c.steward).write({"score": 100})


def test_m42_G06_gate_refuses_another_suppliers_qualification(c):
    a = supplier(c)
    qa = qual(c, a)
    b = supplier(c)
    docs(c, b)
    with pytest.raises(UserError, match="another supplier"):
        gate(c, b, qa).with_user(c.approver).action_activate()
    assert b.status == "prospect"


def test_m42_G07_blocked_or_suspended_not_reactivated_through_the_gate(c):
    for how, who in (("action_suspend", c.steward), ("action_block", c.cfo_approver)):
        s = active_supplier(c)
        getattr(s.with_user(who), how)(reason="audit finding")
        q = c.env["fix.supplier.qualification"].search([("supplier_id", "=", s.id)], limit=1)
        with pytest.raises(UserError, match="reinstatement"):
            gate(c, s, q).with_user(c.approver).action_activate()
        assert s.status in ("suspended", "deactivated")


def test_m42_G07b_reinstatement_needs_a_second_person_and_cfo_for_blocked(c):
    s = active_supplier(c)
    s.with_user(c.steward).action_suspend(reason="late deliveries")
    with pytest.raises(UserError, match="No reinstatement"):
        s.with_user(c.approver).action_approve_reinstatement()
    requester = _user(c.env, "a06m42t_req_appr", [GS, GSA])
    s.with_user(requester).action_request_reinstatement(reason="CAR closed and verified")
    with pytest.raises(UserError, match="Segregation"):
        s.with_user(requester).action_approve_reinstatement()
    s.with_user(c.approver).action_approve_reinstatement()
    assert s.status == "active"
    with pytest.raises(UserError, match="Blocking a supplier needs"):
        s.with_user(c.steward).action_block(reason="counterfeit parts")
    assert s.status == "active"
    s.with_user(c.cfo_approver).action_block(reason="counterfeit parts")
    s.with_user(c.steward).action_request_reinstatement(reason="court ruling 2026-11")
    with pytest.raises(UserError, match="CFO"):
        s.with_user(c.approver).action_approve_reinstatement()
    s.with_user(c.cfo_approver).action_approve_reinstatement()
    assert s.status == "active"


def test_m42_G08_sanctions_hit_and_critical_risk_block_activation(c):
    s = supplier(c)
    docs(c, s)
    c.env["fix.supplier.screening"].with_user(c.steward).create(
        {"supplier_id": s.id, "screening_type": "sanctions", "result": "hit"}
    ).with_user(c.steward).action_flag()
    c.env["fix.supplier.risk"].with_user(c.steward).create(
        {"supplier_id": s.id, "risk_type": "compliance", "likelihood": 5, "impact": 5}
    )
    with pytest.raises(UserError, match=r"screening hit.*critical open risk|critical open risk"):
        gate(c, s, qual(c, s)).with_user(c.approver).action_activate()
    assert s.status != "active"


def test_m42_G09_p03_activate_action_holds_gate(c, p03):
    s = supplier(c)
    g = gate(c, s, None)
    p03.as_user(c.approver)
    out = p03.action(model="fix.supplier.activation", ids=[g.id], method="action_activate")
    s.invalidate_recordset()
    assert not out.get("success") and s.status == "prospect", out


# =================================================================== L: lifecycle after activation
def test_m42_L01_document_change_or_expiry_suspends_and_blocks_pos(c):
    s = active_supplier(c)
    assert _po_gate(c, s.partner_id) == []
    lic = c.env["fix.supplier.document"].search(
        [("supplier_id", "=", s.id), ("doc_type", "=", "trade_licence")]
    )
    lic.with_user(c.steward).write({"valid_to": c.today - timedelta(days=1)})
    assert lic.state == "pending" and s.status == "suspended"
    assert _po_gate(c, s.partner_id)


def test_m42_L01b_cron_expires_documents_and_suspends(c):
    s = active_supplier(c)
    lic = c.env["fix.supplier.document"].search(
        [("supplier_id", "=", s.id), ("doc_type", "=", "tin")]
    )
    lic.sudo()._guarded().write({"valid_to": c.today - timedelta(days=1)})
    # the PO gate fails closed before the sweep runs
    assert any("TIN" in p for p in _po_gate(c, s.partner_id))
    out = c.env["fix.supplier"]._cron_lifecycle_sweep()
    assert lic.id in out["expired_documents"] and s.id in out["suspended"]
    assert lic.state == "expired" and s.status == "suspended"
    cron = c.env.ref("cd_vendor_portal.ir_cron_fix_supplier_lifecycle")
    assert cron.active and "_cron_lifecycle_sweep" in cron.code


def test_m42_L02_flagged_sanctions_hit_blocks(c):
    s = active_supplier(c)
    sc = (
        c.env["fix.supplier.screening"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "screening_type": "sanctions", "result": "hit"})
    )
    assert _po_gate(c, s.partner_id)  # an unresolved hit already blocks POs
    sc.with_user(c.steward).action_flag()
    assert s.status == "deactivated"


def test_m42_L03_failed_requalification_suspends(c):
    s = active_supplier(c)
    r = (
        c.env["fix.supplier.requalification"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "due_on": c.today, "outcome": "fail"})
    )
    r.with_user(c.steward).action_complete()
    assert s.status == "suspended"


def test_m42_L03b_overdue_requalification_suspends_by_cron(c):
    s = active_supplier(c)
    c.env["fix.supplier.requalification"].with_user(c.steward).create(
        {"supplier_id": s.id, "due_on": c.today - timedelta(days=3)}
    )
    c.env["fix.supplier"]._cron_lifecycle_sweep()
    assert s.status == "suspended"


def test_m42_L04_requalification_needs_outcome(c):
    s = supplier(c)
    r = (
        c.env["fix.supplier.requalification"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "due_on": c.today})
    )
    with pytest.raises(UserError):
        r.with_user(c.steward).action_complete()


# =================================================================== Q: screening / risk / CAR
def test_m42_Q01_hit_cannot_be_cleared_by_action(c):
    s = supplier(c)
    sc = (
        c.env["fix.supplier.screening"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "result": "hit"})
    )
    with pytest.raises(UserError):
        sc.with_user(c.steward).action_clear()


def test_m42_Q02_hit_cannot_be_rewritten_only_cleared_by_an_approver(c):
    s = supplier(c)
    sc = (
        c.env["fix.supplier.screening"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "screening_type": "abac", "result": "hit"})
    )
    sc.with_user(c.steward).action_flag()
    with pytest.raises(UserError):
        sc.with_user(c.steward).write({"result": "clear", "state": "cleared"})
    with pytest.raises(UserError, match=r"clearance|recorded"):
        sc.with_user(c.steward).write({"result": "clear"})
    with pytest.raises(UserError, match="role"):
        sc.with_user(c.steward).action_clear_hit(reason="name match only, different DOB")
    with pytest.raises(UserError, match="false positive"):
        sc.with_user(c.approver).action_clear_hit(reason="")
    sc.with_user(c.approver).action_clear_hit(reason="name match only, different DOB (ref CMP-77)")
    assert sc.state == "cleared" and sc.result == "hit" and sc.cleared_by_id == c.approver


def test_m42_Q03_car_closed_only_by_someone_other_than_the_raiser(c):
    s = supplier(c)
    car = (
        c.env["fix.supplier.car"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "issue": "late", "due_date": c.today + timedelta(days=5)})
    )
    with pytest.raises(UserError, match=GUARD):
        car.with_user(c.steward).write({"state": "closed"})
    car.with_user(c.steward).write({"action_plan": "weekly dispatch plan"})
    car.with_user(c.steward).action_action()
    with pytest.raises(UserError, match="Segregation"):
        car.with_user(c.steward).action_close()
    # A10 S6 (M23-12): a MAJOR CAR closes on its root cause — the audit
    # closed a critical one with neither root cause nor NCR.
    with pytest.raises(UserError, match="root cause"):
        car.with_user(c.steward2).action_close()
    car.with_user(c.steward).write({"root_cause": "no dispatch plan after the vendor change"})
    car.with_user(c.steward2).action_close()
    assert car.state == "closed" and car.closed_by_id == c.steward2


def test_a10_s6_every_car_announces_itself_to_the_estate(c):
    """The M42 -> M23 hand-off (A10 S6): a CAR is published as
    supplier.car.raised the moment it exists — with what it is, so the QMS
    consumer in cd_qms_process can raise the NCR for the majors. This
    module cannot see the QMS; the event is the hand-off."""
    s = supplier(c)
    car = (
        c.env["fix.supplier.car"]
        .with_user(c.steward)
        .create(
            {
                "supplier_id": s.id,
                "issue": "wrong part shipped twice",
                "severity": "critical",
                "due_date": c.today + timedelta(days=5),
            }
        )
    )
    events = (
        c.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "supplier.car.raised"), ("aggregate_id", "=", car.id)])
    )
    assert len(events) == 1
    payload = json.loads(events[0].payload)
    assert payload["car"] == car.name
    assert payload["supplier"] == s.name
    assert payload["severity"] == "critical"
    assert "wrong part shipped twice" in payload["issue"]


def test_m42_Q04_car_action_needs_plan(c):
    s = supplier(c)
    car = (
        c.env["fix.supplier.car"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "issue": "late", "due_date": c.today + timedelta(days=5)})
    )
    with pytest.raises(UserError):
        car.with_user(c.steward).action_action()
    with pytest.raises(UserError):
        car.with_user(c.steward2).action_close()


def test_m42_Q05_risk_bounds(c):
    s = supplier(c)
    with pytest.raises(REFUSED):
        c.env["fix.supplier.risk"].with_user(c.steward).create(
            {"supplier_id": s.id, "likelihood": 9}
        )
        c.env.flush_all()


def test_m42_Q06_car_overdue_is_live_and_escalated_once(c):
    s = supplier(c)
    car = (
        c.env["fix.supplier.car"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "issue": "late", "due_date": c.today - timedelta(days=1)})
    )
    assert car.is_overdue
    assert car in c.env["fix.supplier.car"].search([("is_overdue", "=", True), ("id", "=", car.id)])
    out = c.env["fix.supplier"]._cron_lifecycle_sweep()
    assert car.id in out["escalated_cars"] and car.escalated_on == c.today
    assert car.id not in c.env["fix.supplier"]._cron_lifecycle_sweep()["escalated_cars"]


# =================================================================== P: scorecards
def _issued_po_with_receipt(c, partner, price=1000.0, qty=10.0, accepted=10.0, promised=None):
    """A sent PO with a posted, inspected receipt (seeded as the system: the
    M16 approval path itself is covered by test_a06_m16_controls)."""
    env = c.env
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": c.ou.id,
            "vendor_id": partner.id,
            "promised_date": promised or c.today + timedelta(days=7),
            "line_ids": [
                (0, 0, {"product_id": c.prod.id, "qty_ordered": qty, "unit_price": price})
            ],
        }
    )
    po.action_record_requisition_exception(reason="seeded for the scorecard test")
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po.amount_total,
        }
    )
    po.action_send()
    po.action_acknowledge_on_behalf(
        evidence="seeded vendor confirmation", confirmed_date="2099-01-01"
    )
    po.action_record_receipt({po.line_ids.id: qty})
    rline = po.receipt_ids.line_ids
    insp = env["fix.procurement.inspection"].create(
        {"receipt_line_id": rline.id, "qty_accepted": accepted}
    )
    insp.action_confirm()
    return po


def test_m42_P01_scorecard_cannot_be_typed(c):
    s = supplier(c)
    with pytest.raises(UserError, match=GUARD):
        c.env["fix.supplier.performance"].with_user(c.steward).create(
            {"supplier_id": s.id, "period": "2026-10", "quality_score": 100, "delivery_score": 100}
        )
    card = (
        c.env["fix.supplier.performance"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "period": "2026-10"})
    )
    with pytest.raises(UserError, match="Compute"):
        card.with_user(c.steward).action_publish()
    with pytest.raises(UserError, match="No purchase-order or receipt facts"):
        card.with_user(c.steward).action_compute()
    assert card.state == "draft"


def test_m42_P01b_scorecard_is_computed_from_receipts(c):
    s = active_supplier(c)
    _issued_po_with_receipt(c, s.partner_id, accepted=8.0)
    period = c.today.strftime("%Y-%m")
    card = (
        c.env["fix.supplier.performance"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "period": period})
    )
    card.with_user(c.steward).action_compute()
    assert card.quality_score == pytest.approx(80.0)
    assert card.delivery_score == pytest.approx(100.0)
    assert card.responsiveness_score == pytest.approx(100.0)
    assert not card.cost_measured and "cost: no data" in card.basis_note
    # 80*0.35 + 100*0.30 + 100*0.15 over 0.80 of weight
    assert card.total_score == pytest.approx(91.25, abs=0.06) and card.grade == "a"
    card.with_user(c.steward).action_publish()
    assert card.state == "published"


def test_m42_P02_published_scorecard_is_final(c):
    s = supplier(c)
    card = c.env["fix.supplier.performance"].create(
        {
            "supplier_id": s.id,
            "period": "2026-10",
            "quality_score": 90,
            "computed_at": fields.Datetime.now(),
        }
    )
    card.with_user(c.steward).action_publish()
    with pytest.raises(UserError):
        card.with_user(c.steward2).write({"delivery_score": 10})
    with pytest.raises(UserError):
        card.with_user(c.steward2).write({"state": "draft"})
    with pytest.raises(UserError, match="final"):
        card.with_user(c.steward2).write({"reviewed_on": "2026-01-01"})


def test_m42_P03_grade_cannot_be_written(c):
    s = supplier(c)
    card = (
        c.env["fix.supplier.performance"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "period": "2026-10"})
    )
    with pytest.raises(UserError, match=GUARD):
        card.with_user(c.steward).write({"total_score": 99.0, "grade": "a"})


def test_m42_P04_score_range_constraint(c):
    s = supplier(c)
    with pytest.raises(REFUSED):
        c.env["fix.supplier.performance"].create(
            {"supplier_id": s.id, "period": "2026-10", "quality_score": 150}
        )
        c.env.flush_all()


def test_m42_P05_two_d_grades_raise_a_car(c):
    s = active_supplier(c)
    for period in ("2026-09", "2026-10"):
        card = c.env["fix.supplier.performance"].create(
            {
                "supplier_id": s.id,
                "period": period,
                "quality_score": 10,
                "delivery_score": 10,
                "cost_score": 10,
                "responsiveness_score": 10,
                "computed_at": fields.Datetime.now(),
            }
        )
        card.with_user(c.steward).action_publish()
    cars = c.env["fix.supplier.car"].search([("supplier_id", "=", s.id)])
    assert len(cars) == 1 and "D-grade" in cars.issue


def test_m42_P06_goods_received_carries_the_vendor(c):
    """The event scorecard (fix.supplier.scorecard, cd_cx_feedback) could not be
    fed: goods.received had no vendor. It now carries it."""
    s = active_supplier(c)
    po = _issued_po_with_receipt(c, s.partner_id)
    row = c.env["fix.event.outbox"].search(
        [("event_type", "=", "goods.received"), ("aggregate_id", "=", po.line_ids.id)], limit=1
    )
    assert json.loads(row.payload)["vendor_id"] == s.partner_id.id


# =================================================================== B: bank-detail change control
def test_m42_B01_plain_and_accounting_users_cannot_edit_bank(c):
    s = active_supplier(c)
    change = (
        c.env["fix.supplier.bank.change"]
        .with_user(c.steward)
        .create(
            {
                "supplier_id": s.id,
                "acc_number": "A06M42T-ORIG-1",
                "verification_ref": "call-back 01711",
                "evidence_ref": "dms://bank/1",
            }
        )
    )
    change.with_user(c.steward).action_propose()
    change.with_user(c.steward2).action_confirm()
    bank = s.bank_account_id
    for u in (c.plain, c.acct):
        with pytest.raises(REFUSED), c.env.cr.savepoint():
            bank.with_user(u).write({"acc_number": "A06M42T-MULE-%s" % u.id})
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["res.partner.bank"].with_user(c.plain).create(
            {"partner_id": s.partner_id.id, "acc_number": "MULE"}
        )


def test_m42_B02_bank_document_cannot_be_typed_valid(c):
    s = active_supplier(c)
    with pytest.raises(UserError, match=GUARD):
        c.env["fix.supplier.document"].with_user(c.steward).create(
            {"supplier_id": s.id, "doc_type": "bank", "number": "MULE-999", "state": "valid"}
        )


def test_m42_B03_bank_change_needs_a_second_person_and_blocks_payment(c):
    s = active_supplier(c)
    pm = _user(c.env, "a06m42t_partner_mgr", ["base.group_partner_manager"])
    with pytest.raises(UserError, match="bank-detail change"):
        c.env["res.partner.bank"].with_user(pm).create(
            {"partner_id": s.partner_id.id, "acc_number": "A06M42T-MULE"}
        )
    change = (
        c.env["fix.supplier.bank.change"]
        .with_user(c.steward)
        .create(
            {"supplier_id": s.id, "acc_number": "A06M42T-NEW-003", "routing_number": "123456789"}
        )
    )
    with pytest.raises(UserError, match="call-back"):
        change.with_user(c.steward).action_propose()
    change.with_user(c.steward).write(
        {"verification_ref": "called 01711000000 on file", "evidence_ref": "dms://b/3"}
    )
    change.with_user(c.steward).action_propose()
    assert s.payment_block
    with pytest.raises(UserError, match="fixed"):
        change.with_user(c.steward).write({"acc_number": "A06M42T-MULE-3"})
    with pytest.raises(UserError, match="Segregation"):
        change.with_user(c.steward).action_confirm()
    bill = c.env["fix.vendor.invoice"].create(
        {
            "vendor_id": s.partner_id.id,
            "invoice_ref": "A06M42T-B03",
            "operating_unit_id": c.ou.id,
            "bill_type": "non_po",
        }
    )
    bill.with_context(ap_internal=True).write({"approval_state": "approved"})
    with pytest.raises(UserError, match="blocked"):
        bill.action_request_payment()
    audits_before = c.env["fix.security.audit"].search_count(
        [("object_ref", "=", "fix.supplier,%s" % s.id)]
    )
    change.with_user(c.approver).action_confirm()
    assert not s.payment_block and s.bank_account_id.acc_number == "A06M42T-NEW-003"
    assert (
        c.env["fix.security.audit"].search_count([("object_ref", "=", "fix.supplier,%s" % s.id)])
        == audits_before + 1
    )
    with pytest.raises(UserError, match="bank-detail change"):
        s.bank_account_id.with_user(pm).write({"acc_number": "A06M42T-MULE-003"})
    events = c.env["fix.event.outbox"].search(
        [
            (
                "event_type",
                "in",
                ("supplier.bank_change.proposed", "supplier.bank_change.confirmed"),
            ),
            ("aggregate_id", "=", s.id),
        ]
    )
    assert len(events) == 2


# =================================================================== V: P05 vendor on M42 data
def test_m42_V01_portal_vendor_cannot_touch_own_supplier_records(c):
    s = active_supplier(c)
    card = c.env["fix.supplier.performance"].create({"supplier_id": s.id, "period": "2026-10"})
    group = c.env.ref("cd_vendor_portal.group_fix_vendor_portal")
    u = (
        c.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A06M42T vendor",
                "login": "a06m42t_vendor@vendor.test",
                "partner_id": s.partner_id.id,
                "group_ids": [(6, 0, [group.id])],
            }
        )
    )
    q = c.env["fix.supplier.qualification"].search([("supplier_id", "=", s.id)], limit=1)
    for model, rid, vals in (
        ("fix.supplier", s.id, {"segment": "strategic"}),
        ("fix.supplier.performance", card.id, {"reviewed_on": "2026-01-01"}),
        ("fix.supplier.qualification", q.id, {"notes": "x"}),
    ):
        with pytest.raises(REFUSED), c.env.cr.savepoint():
            c.env[model].with_user(u).browse(rid).write(vals)
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.supplier.document"].with_user(u).create(
            {"supplier_id": s.id, "doc_type": "bank"}
        )
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.supplier.bank.change"].with_user(u).create(
            {"supplier_id": s.id, "acc_number": "MULE"}
        )


# =================================================================== W: workspace wiring
def test_m42_W01_supplier_actions_declared_and_forms_offer_no_guarded_field(c):
    from odoo.addons.cd_p03_portal.controllers import form_fields
    from odoo.addons.cd_p03_portal.controllers.a06 import m42 as surf

    assert {
        "action_suspend",
        "action_block",
        "action_request_reinstatement",
        "action_approve_reinstatement",
    } <= set(surf.SURFACES["fix.supplier"]["actions"])
    editable = form_fields.editable_by_model()
    for model in surf.SURFACES:
        guarded = c.env[model].browse()._fix_guarded_fields()
        assert not guarded & editable.get(model, set()), (
            model,
            guarded & editable.get(model, set()),
        )


def test_m42_W02_p03_qualification_and_scorecard_forgery_refused(c, p03):
    s = supplier(c)
    q = qual(c, s, approve=False)
    card = (
        c.env["fix.supplier.performance"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "period": "2026-10"})
    )
    o1 = p03.write(model="fix.supplier.qualification", record_id=q.id, values={"state": "approved"})
    o2 = p03.write(
        model="fix.supplier.performance",
        record_id=card.id,
        values={"state": "published", "quality_score": 100, "delivery_score": 100},
    )
    q.invalidate_recordset()
    card.invalidate_recordset()
    assert "error" in o1 and "error" in o2 and q.state == "draft" and card.state == "draft"


def test_m42_W03_p03_document_and_screening_forgery_refused(c, p03):
    s = supplier(c)
    sc = (
        c.env["fix.supplier.screening"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "result": "hit"})
    )
    o1 = p03.write(
        model="fix.supplier.document",
        values={"supplier_id": s.id, "doc_type": "trade_licence", "state": "valid"},
    )
    o2 = p03.write(
        model="fix.supplier.screening",
        record_id=sc.id,
        values={"result": "clear", "state": "cleared"},
    )
    sc.invalidate_recordset()
    doc = c.env["fix.supplier.document"].search(
        [("supplier_id", "=", s.id), ("doc_type", "=", "trade_licence")]
    )
    assert all(d.state == "pending" for d in doc), o1
    assert "error" in o2 and sc.state == "pending" and sc.result == "hit"


def test_m42_W04_kpis_read_as_the_caller(c):
    from odoo.addons.cd_p03_portal.controllers.a06 import m42 as surf

    active_supplier(c)
    out = surf.kpis(c.env(user=c.plain.id))
    assert out["active_suppliers"] >= 1
    for name, fn in surf.REPORTS.items():
        assert "rows" in fn(c.env(user=c.plain.id)), name


# =================================================================== proper path
def test_m42_proper_path_onboarding_to_po_gate(c):
    s = supplier(c)
    assert _po_gate(c, s.partner_id)
    docs(c, s)
    q = qual(c, s)
    assert s.status == "qualified" and q.approved_by_id == c.approver
    with pytest.raises(UserError, match="no cleared"):
        gate(c, s, q).with_user(c.approver).action_activate()
    cleared_screenings(c, s)
    c.env["fix.supplier.activation"].search([("supplier_id", "=", s.id)]).with_user(
        c.approver
    ).action_activate()
    assert s.status == "active" and s.status_changed_by_id == c.approver
    assert _po_gate(c, s.partner_id) == []


# =================================================================== follow-up: M42-10, M42-7, M16-12
def test_m42_M10_no_second_activation_of_an_active_supplier(c):
    s = active_supplier(c)
    q = c.env["fix.supplier.qualification"].search([("supplier_id", "=", s.id)], limit=1)
    with pytest.raises(UserError, match="already active"):
        gate(c, s, q)
    p = supplier(c)
    docs(c, p)
    qp = qual(c, p)
    gate(c, p, qp)
    with pytest.raises(UserError, match="pending activation"):
        gate(c, p, qp)


def test_m42_L05_reminder_before_expiry_once(c):
    s = active_supplier(c)
    lic = c.env["fix.supplier.document"].search(
        [("supplier_id", "=", s.id), ("doc_type", "=", "trade_licence")]
    )
    lic.sudo()._guarded().write({"valid_to": c.today + timedelta(days=10)})
    c.env["fix.supplier.requalification"].with_user(c.steward).create(
        {"supplier_id": s.id, "due_on": c.today + timedelta(days=5)}
    )
    out = c.env["fix.supplier"]._cron_lifecycle_sweep()
    acts = c.env["mail.activity"].search(
        [("res_model", "=", "fix.supplier"), ("res_id", "=", s.id)]
    )
    summaries = acts.mapped("summary")
    assert any(lic.name in x for x in summaries) and any("re-qualification" in x for x in summaries)
    assert set(acts.ids) <= set(out["reminders"]) and s.status == "active"
    assert acts.mapped("user_id") == s.create_uid  # no buyer: the steward who registered it
    assert not c.env["fix.supplier"]._cron_lifecycle_sweep()["reminders"]
    cron = c.env.ref("cd_vendor_portal.ir_cron_fix_supplier_lifecycle")
    assert cron.active and cron.interval_type == "days"


def test_m42_reminder_lead_days_are_configuration(c):
    s = active_supplier(c)
    lic = c.env["fix.supplier.document"].search(
        [("supplier_id", "=", s.id), ("doc_type", "=", "tin")]
    )
    lic.sudo()._guarded().write({"valid_to": c.today + timedelta(days=20)})
    c.env["ir.config_parameter"].set_param("cd_vendor_portal.expiry_reminder_days", "10")
    c.env["fix.supplier"]._cron_lifecycle_sweep()
    assert not c.env["mail.activity"].search_count(
        [("res_model", "=", "fix.supplier"), ("res_id", "=", s.id)]
    )


def test_m16_E02_consumers_refresh_the_scorecard_idempotently(c):
    for xmlid, event in (
        ("cd_vendor_portal.consumer_goods_received_scorecard", "goods.received"),
        ("cd_vendor_portal.consumer_po_acknowledged_scorecard", "po.acknowledged"),
    ):
        sub = c.env.ref(xmlid)
        assert (sub.event_type, sub.model, sub.method, sub.active) == (
            event,
            "fix.supplier.performance",
            "consume_supplier_fact",
            True,
        )
    s = active_supplier(c)
    po = _issued_po_with_receipt(c, s.partner_id, accepted=8.0)
    row = c.env["fix.event.outbox"].search(
        [("event_type", "=", "goods.received"), ("aggregate_id", "=", po.line_ids.id)], limit=1
    )
    Card = c.env["fix.supplier.performance"]
    card = Card.consume_supplier_fact(row._relay_event_dict())
    assert card.supplier_id == s and card.quality_score == pytest.approx(80.0)
    again = Card.consume_supplier_fact(row._relay_event_dict())
    assert again == card and card.quality_score == pytest.approx(80.0)
    assert Card.search_count([("supplier_id", "=", s.id)]) == 1
    ack = c.env["fix.event.outbox"].search(
        [("event_type", "=", "po.acknowledged"), ("aggregate_id", "=", po.id)], limit=1
    )
    assert Card.consume_supplier_fact(ack._relay_event_dict()) == card
    card.with_user(c.steward).action_publish()
    assert Card.consume_supplier_fact(row._relay_event_dict()) is False  # published: frozen
    stranger = c.env["res.partner"].create({"name": "no supplier"})
    assert Card.consume_supplier_fact({"payload": {"vendor_id": stranger.id}}) is False
