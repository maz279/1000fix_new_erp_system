"""A05 ERP remediation, builder stream S3 (20 Nov 2026): M18 e-waste.

Each finding is attacked as a NON-ADMIN user (the superuser is trusted by the
field guard and would hide a gap) and the legitimate path is proved too.
Money is driven through the real routed approval and the real settlement
consumer; the GL accounts come from the D1 parameters, pointed here at
accounts that exist in the test database's chart. ``odoo_env`` rolls back.
"""

import base64
import itertools
from datetime import datetime, timedelta

import pytest
from odoo.addons.cd_ewaste.models import ewaste_common as c
from odoo.addons.cd_ewaste.tests.m18_fixtures import (
    M18,
    G,
    attachment,
    events,
    make_user,
    refused,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

_N = itertools.count(1)
INCOME_CODE = "450000"  # test chart: Other Income (fix_real: 400109, D1)
EXPENSE_CODE = "600000"  # test chart: Expenses (fix_real: NEW 500910, D1)


def build(env):
    """The S3 test world on top of the M18 fixtures (also used by the
    mutation check)."""
    x = M18(env)
    param = env["ir.config_parameter"].sudo()
    param.set_param("cd_ewaste.account_code.recovery_income", INCOME_CODE)
    param.set_param("cd_ewaste.account_code.recycling_cost", EXPENSE_CODE)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "S3E%d" % next(_N), "legal_name": "S3 Entity", "company_id": env.company.id})
    x.branch = env["fix.branch"].create(
        {
            "name": "S3 Branch %d" % next(_N),
            "code": "S3B%d" % next(_N),
            "entity_id": entity.id,
            "operating_unit_id": x.ou.id,
        }
    )
    x.cfo2 = make_user(env, "cfo2", [G.finance])
    return x


@pytest.fixture
def m(odoo_env):
    x = build(odoo_env)
    try:
        yield x
    finally:
        x.close()


def _bank(m, partner):
    return m.env["res.partner.bank"].create(
        {"acc_number": "S3-%d" % next(_N), "partner_id": partner.id}
    )


def _triaged(m, weight=0.5):
    col = m.collection(weight_kg=weight, operating_unit_id=m.ou.id)
    m.triage(col, "recycle")
    return col


def _incentive(m, col=None, amount=800.0, **vals):
    col = col or _triaged(m)
    data = {
        "kind": "incentive",
        "collection_id": col.id,
        "partner_id": col.customer_id.id,
        "amount": amount,
        "branch_id": m.branch.id,
        "payment_method": "bank_transfer",
        "partner_bank_id": _bank(m, col.customer_id).id,
    }
    data.update(vals)
    return m.env["fix.ewaste.settlement"].with_user(m.dispatcher).create(data)


def _consume(m, s):
    return (
        m.env["fix.a05.settlement.consumers"]
        .sudo()
        .consume_ewaste_settlement_approved(
            {"aggregate": s._name, "aggregate_id": s.id, "payload": {"amount": s.amount}}
        )
    )


def _received_batch(m):
    item = m.ready_item(weight=1.0)
    b = m.dispatched_batch([item])
    b.write({"received_weight_kg": b.weight_kg, "recycler_receipt_ref": "RCV-S3"})
    b.action_receive()
    b.sudo()._guarded().write({"operating_unit_id": m.ou.id})
    return b


def _processed_batch(m):
    b = _received_batch(m)
    b.write({"processing_evidence_id": attachment(m.env, "processed.pdf").id})
    b.action_process()
    return b


def _income(m):
    """A processed batch, its recovery lines and the raised income."""
    b = _processed_batch(m)
    Rec = m.env["fix.ewaste.material.recovery"].with_user(m.dispatcher)
    lines = Rec.create(
        {"batch_id": b.id, "material_class": "pcb", "weight_kg": 0.3, "agreed_rate": 1000.0}
    ) | Rec.create(
        {"batch_id": b.id, "material_class": "plastic", "weight_kg": 0.5, "agreed_rate": 40.0}
    )
    lines.with_user(m.dispatcher).action_raise_income()
    s = lines.settlement_id
    assert s and s.kind == "recovery_income" and s.amount == pytest.approx(320.0)
    return b, lines, s


# ===================================================== M18-01/02/04 FIN-05/06/11
def test_payout_is_a_pinned_request_debiting_the_expense_on_the_collection_ou(m):
    s = _incentive(m)
    approve_via_inbox(s, m.cfo, requester=m.dispatcher)
    assert s.state == "approved" and s.operating_unit_id == m.ou
    res = _consume(m, s)
    pay = m.env["fix.payment.execution"].sudo().browse(res["id"])
    expense = m.env["account.account"].search([("code", "=", EXPENSE_CODE)], limit=1)
    assert pay.source_pinned and pay.source_approved_by_id == m.cfo  # FIN-05
    assert pay.debit_account_id == expense  # FIN-06: never Bank Suspense
    assert pay.operating_unit_id == m.ou  # FIN-11 / M18-04
    assert pay.partner_bank_id == s.partner_bank_id and pay.method == "bank_transfer"
    assert pay.amount == 800.0 and pay.partner_id == s.partner_id
    # treasury cannot re-point what the approval pinned
    clerk_t = make_user(m.env, "treasury", ["account.group_account_user"])
    with pytest.raises(UserError), m.env.cr.savepoint():
        pay.with_user(clerk_t).write({"amount": 9999.0})
    # idempotent
    assert _consume(m, s)["id"] == pay.id and not _consume(m, s)["created"]


def test_payout_fails_closed_without_the_expense_parameter(m):
    s = _incentive(m)
    approve_via_inbox(s, m.cfo, requester=m.dispatcher)
    m.env["ir.config_parameter"].sudo().set_param("cd_ewaste.account_code.recycling_cost", "")
    with pytest.raises(UserError, match="cd_ewaste.account_code.recycling_cost"):
        _consume(m, s)
    m.env["ir.config_parameter"].sudo().set_param(
        "cd_ewaste.account_code.recycling_cost", "S3NOACCT"
    )
    with pytest.raises(UserError, match="S3NOACCT"):
        _consume(m, s)


def test_mfs_and_cash_methods_map_to_m50(m):
    s = _incentive(m, payment_method="cash", partner_bank_id=False)
    approve_via_inbox(s, m.cfo, requester=m.dispatcher)
    pay = m.env["fix.payment.execution"].sudo().browse(_consume(m, s)["id"])
    assert pay.method == "cash" and not pay.partner_bank_id
    s2 = _incentive(m, payment_method="mfs")
    approve_via_inbox(s2, m.cfo, requester=m.dispatcher)
    assert m.env["fix.payment.execution"].sudo().browse(_consume(m, s2)["id"]).method == (
        "mobile_fs"
    )


# ===================================================== M18-03 / XC-05 / D1 / D2
def test_recovery_income_invoice_credits_the_income_account_with_m51_vat(m):
    b, lines, s = _income(m)
    s.with_user(m.dispatcher).write({"branch_id": m.branch.id})
    approve_via_inbox(s, m.cfo, requester=m.dispatcher)
    inv = m.env["fix.ar.invoice"].sudo().browse(_consume(m, s)["id"])
    income = m.env["account.account"].search([("code", "=", INCOME_CODE)], limit=1)
    assert inv.revenue_account_id == income  # not 400100
    assert inv.operating_unit_id == m.ou and inv.branch_id == m.branch
    assert inv.state == "draft" and inv.customer_id == s.partner_id
    line = inv.line_ids
    assert line.taxable_amount == pytest.approx(320.0)
    # D2: the M51 determination at the standard rate, never VAT 0 in code
    assert line.vat_amount == pytest.approx(48.0)


# ===================================================== M18-05
def test_recovery_income_is_raised_once_from_its_lines_and_locked(m):
    b, lines, s = _income(m)
    Settlement = m.env["fix.ewaste.settlement"]
    # never typed
    assert refused(
        m.env,
        lambda: Settlement.with_user(m.dispatcher).create(
            {
                "kind": "recovery_income",
                "batch_id": b.id,
                "partner_id": s.partner_id.id,
                "amount": 5000.0,
            }
        ),
    )
    # its amount is the lines' total, even in draft
    assert refused(m.env, lambda: s.with_user(m.dispatcher).write({"amount": 99999.0}))
    assert m.p03_write(m.dispatcher, "fix.ewaste.settlement", s.id, {"amount": 99999.0}).get(
        "error"
    )
    # one live income settlement per batch
    assert refused(
        m.env,
        lambda: Settlement._guarded().create(
            {
                "kind": "recovery_income",
                "batch_id": b.id,
                "partner_id": s.partner_id.id,
                "amount": 1.0,
            }
        ),
    )
    # an amount that drifted from the lines is refused at request
    s.sudo()._guarded().write({"amount": 999.0})
    s.with_user(m.dispatcher).write({"branch_id": m.branch.id})
    with pytest.raises(UserError, match="recovery lines total"), m.env.cr.savepoint():
        s.with_user(m.dispatcher).action_request_approval()
    # cancelling frees the lines to be raised again
    s.with_user(m.dispatcher).action_cancel()
    assert set(lines.mapped("state")) == {"draft"} and not lines.settlement_id
    lines.with_user(m.dispatcher).action_raise_income()
    assert lines.settlement_id and lines.settlement_id != s


# ===================================================== M18-06
def test_recycler_money_payee_fails_closed_without_a_contact(m):
    b = _received_batch(m)
    recycler = b.partner_id
    contact = recycler.partner_id
    Settlement = m.env["fix.ewaste.settlement"].with_user(m.dispatcher)
    fee = {
        "kind": "recycler_fee",
        "batch_id": b.id,
        "amount": 25000.0,
        "branch_id": m.branch.id,
        "payment_method": "cash",
    }
    stranger = m.env["res.partner"].create({"name": "S3 Stranger"})
    assert refused(m.env, lambda: Settlement.create({**fee, "partner_id": stranger.id}))
    recycler.sudo()._guarded().write({"partner_id": False})
    assert refused(m.env, lambda: Settlement.create({**fee, "partner_id": stranger.id}))
    recycler.sudo()._guarded().write({"partner_id": contact.id})
    assert Settlement.create({**fee, "partner_id": contact.id})
    # a recycler is qualified only with its contact
    p = m.partner()
    p.sudo().write({"partner_id": False})
    with pytest.raises(UserError, match="business contact"):
        approve_via_inbox(p, m.approver, requester=m.dispatcher)


# ===================================================== I2: pinned terms
def test_ou_branch_method_and_account_are_required_and_pinned(m):
    col = _triaged(m)
    s = _incentive(m, col=col, branch_id=False)
    with pytest.raises(UserError, match="branch"), m.env.cr.savepoint():
        s.with_user(m.dispatcher).action_request_approval()
    s.with_user(m.dispatcher).write({"branch_id": m.branch.id, "partner_bank_id": False})
    with pytest.raises(UserError, match="account or wallet"), m.env.cr.savepoint():
        s.with_user(m.dispatcher).action_request_approval()
    other = m.env["res.partner"].create({"name": "S3 Other"})
    assert refused(
        m.env, lambda: s.with_user(m.dispatcher).write({"partner_bank_id": _bank(m, other).id})
    )
    s.with_user(m.dispatcher).write({"partner_bank_id": _bank(m, col.customer_id).id})
    s.with_user(m.dispatcher).action_request_approval()
    assert s.approval_state == "pending"
    # a change of the payment terms voids the pending approval
    s.with_user(m.dispatcher).write({"payment_method": "cash", "partner_bank_id": False})
    assert s.approval_state == "none"
    # and a collection without an operating unit is refused, not given the first OU
    bare = m.collection(weight_kg=0.4, operating_unit_id=False)
    m.triage(bare, "recycle")
    s2 = _incentive(m, col=bare, branch_id=False)
    assert not s2.operating_unit_id
    with pytest.raises(UserError, match="operating unit"):
        s2.with_user(m.dispatcher).action_request_approval()


# ===================================================== XC-24
def test_settlement_amount_tiers(m):
    small = _incentive(m, amount=40000.0)
    assert small._approval_tier() is False
    big = _incentive(m, amount=60000.0)
    assert big._approval_tier() == "tier_2"
    huge = _incentive(m, amount=2000000.0)
    assert huge._approval_tier() == "tier_4"
    tier2 = make_user(m.env, "tier2", ["cd_entity_config.group_dofa_tier_2"])
    big.with_user(m.dispatcher).action_request_approval(justification="large incentive")
    assert big.approval_request_id.tier == "tier_2"
    # the E-Waste Finance Approver alone cannot decide it
    assert not inbox_task(big, m.cfo)
    approve_via_inbox(big, tier2, requester=m.dispatcher)
    assert big.state == "approved"


# ===================================================== M18-31 / M18-30 / M18-22
def test_no_incentive_to_the_company_itself_and_restricted_settlement_access(m):
    own = m.collection(
        weight_kg=0.5, operating_unit_id=m.ou.id, customer_id=m.env.company.partner_id.id
    )
    m.triage(own, "recycle")
    assert refused(m.env, lambda: _incentive(m, col=own))
    s = _incentive(m)
    # amounts are not read by every internal user (M18-30); clerks raise nothing
    with pytest.raises(AccessError):
        s.with_user(m.clerk).read(["amount"])
    assert refused(
        m.env,
        lambda: m.env["fix.ewaste.settlement"]
        .with_user(m.clerk)
        .create({"kind": "incentive", "collection_id": own.id, "partner_id": 1, "amount": 1}),
    )


def test_partner_downstream_and_hazmat_are_not_any_users(m):
    assert refused(
        m.env,
        lambda: m.env["fix.ewaste.partner"]
        .with_user(m.clerk)
        .create({"name": "Clerk Recycler", "valid_to": m.today + timedelta(days=10)}),
    )
    p = m.partner()
    down = p.downstream_ids
    assert refused(
        m.env,
        lambda: m.env["fix.ewaste.partner.downstream"]
        .with_user(m.clerk)
        .create({"partner_id": p.id, "name": "X"}),
    )
    assert refused(m.env, lambda: down.with_user(m.clerk).action_withdraw())
    assert refused(m.env, lambda: down.with_user(m.dispatcher).action_withdraw())
    down.with_user(m.approver).action_withdraw()
    assert down.state == "withdrawn"
    # an orphan hazmat record (no intake behind it) is refused, for every user
    Bat = m.env["fix.ewaste.battery"]
    assert refused(m.env, lambda: Bat.with_user(m.clerk).create({"weight_kg": 0.2}))
    assert refused(m.env, lambda: Bat.with_user(m.hse).create({"weight_kg": 0.2}))


# ===================================================== M18-07 / M18-12
def _point(m, classes=("li_sound",), ceiling=50.0):
    p = (
        m.env["fix.ewaste.collection.point"]
        .with_user(m.clerk)
        .create(
            {
                "name": "S3 Point %d" % next(_N),
                "kind": "hazmat_store",
                "capacity_kg": 1000.0,
                "responsible_id": m.env["hr.employee"].create({"name": "S3 Resp"}).id,
                "limit_ids": [(0, 0, {"hazard_class": k, "max_kg": ceiling}) for k in classes],
            }
        )
    )
    p.with_user(m.hse).action_activate()
    return p


def _hazmat(m, point, weight=0.4):
    col = m.collection(material_type="battery", weight_kg=weight, collection_point_id=point.id)
    m.triage(col, "hazardous")
    assert col.state == "hazmat"
    return col


def test_hazmat_refused_at_a_point_without_its_ceiling_and_hse_alerted(m):
    crt_only = _point(m, classes=("crt",))
    col = _hazmat(m, crt_only)
    bat = col.battery_ids
    assert len(bat) == 1 and not bat.collection_point_id  # not accepted there
    assert events(m.env, "ewaste.hazmat_ceiling_breach", bat.id) == 1
    # the HSE officer is alerted (a to-do on the item) and the refusal is on file
    assert col.activity_ids.filtered(lambda a: "not accepted" in (a.summary or ""))
    assert any("not accepted" in str(msg.body or "").lower() for msg in bat.sudo().message_ids)
    bat = bat.with_user(m.hse)
    bat.write({"inspection_evidence_id": attachment(m.env, "p.jpg").id})
    with pytest.raises(UserError, match="designated"):
        bat.with_user(m.hse).action_inspect_and_quarantine()
    # a breach of the ceiling is refused the same way
    small = _point(m, ceiling=0.3)
    over = _hazmat(m, small, weight=0.4)
    assert not over.battery_ids.collection_point_id
    # placed at a designated point it proceeds
    good = _point(m)
    bat.with_user(m.hse).write({"collection_point_id": good.id})
    bat.with_user(m.hse).action_inspect_and_quarantine()
    assert bat.terminal_taped


def test_hazmat_is_disposed_only_by_an_issued_certificate(m):
    point = _point(m)
    col = _hazmat(m, point)
    bat = col.battery_ids.with_user(m.hse)
    assert bat.collection_point_id == point
    bat.write({"inspection_evidence_id": attachment(m.env, "p.jpg").id})
    bat.with_user(m.hse).action_inspect_and_quarantine()
    b = m.batch(material="battery")
    b.action_load_ready_items()
    assert b.battery_ids == bat
    m.weigh_out(b)
    b.action_dispatch()
    b.write({"received_weight_kg": b.weight_kg, "recycler_receipt_ref": "R-B"})
    b.action_receive()
    b.write({"processing_evidence_id": attachment(m.env).id})
    b.action_process()
    assert bat.state == "processed"
    assert col.state == "hazmat"  # processed is not disposed (M18-07)
    assert refused(m.env, lambda: col.sudo()._guarded().write({"state": "disposed"}))
    cert = m.issued_certificate(b)
    assert cert.battery_ids == bat and bat.disposal_certificate_id == cert
    assert col.state == "disposed"
    assert events(m.env, "ewaste.disposal_certified", cert.id) == 1
    cert.write({"revoke_reason": "recycler failed audit"})
    cert.with_user(m.compliance).action_revoke()
    assert col.state == "hazmat" and not bat.disposal_certificate_id


# ===================================================== M18-08
def _overdue(m, batch, days=40):
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_ewaste_batch SET dispatched_on=%s WHERE id=%s",
        (m.today - timedelta(days=days), batch.id),
    )
    m.env.invalidate_all()
    batch._compute_certificate_due()


def test_certificate_due_clock_raises_exceptions_and_suspends_on_the_second(m):
    partner = m.approved_partner()
    b1 = m.dispatched_batch([m.ready_item()], partner=partner)
    b2 = m.dispatched_batch([m.ready_item()], partner=partner)
    assert b1.certificate_due_on == b1.dispatched_on + timedelta(days=30)
    Batch = m.env["fix.ewaste.batch"]
    Batch.cron_certificate_due()
    assert not b1.certificate_overdue  # not due yet
    _overdue(m, b1)
    Batch.cron_certificate_due()
    exc = m.env["fix.ewaste.certificate.exception"].search([("batch_id", "=", b1.id)])
    assert exc and exc.kind == "overdue" and exc.collection_id == b1.collection_ids
    assert events(m.env, "ewaste.certificate_exception", exc.id) == 1
    assert b1.certificate_overdue and partner.state == "active"
    assert b1.activity_ids.filtered(lambda a: "overdue" in (a.summary or "").lower())
    Batch.cron_certificate_due()  # safe to re-run
    assert m.env["fix.ewaste.certificate.exception"].search_count([("batch_id", "=", b1.id)]) == 1
    _overdue(m, b2)
    Batch.cron_certificate_due()
    assert partner.state == "suspended" and partner.suspension_reason
    assert events(m.env, "ewaste.partner_suspended", partner.id) == 1
    assert refused(m.env, lambda: m.dispatched_batch([m.ready_item()], partner=partner))


# ===================================================== M18-14
def test_every_item_is_weighed_before_triage(m):
    assert refused(m.env, lambda: m.collection(weight_kg=0.0))
    handed = (
        m.env["fix.ewaste.collection"]
        .sudo()
        ._guarded()
        .create(
            {"customer_id": m.env.company.partner_id.id, "source_model": "x", "source_ref": "X"}
        )
    )
    handed = m.env["fix.ewaste.collection"].browse(handed.id)
    assert handed.weight_pending
    with pytest.raises(UserError, match="weigh it in"), m.env.cr.savepoint():
        m.triage(handed, "recycle")
    handed.with_user(m.clerk).write({"weight_kg": 0.7})
    m.triage(handed, "recycle")
    assert handed.state == "triaged" and not handed.weight_pending


# ===================================================== M18-13
def test_a_unit_m14_sends_back_reopens_its_original_collection(m):
    col = m.collection(device_id=m.device().id, weight_kg=0.6, operating_unit_id=m.ou.id)
    m.triage(col, "refurbish")
    assert col.state == "routed"
    first = col.triage_id
    out = (
        m.env["fix.tradein.request"]
        .sudo()
        .consume_ewaste_reuse_routed(
            {"aggregate": col._name, "aggregate_id": col.id, "payload": {}}
        )
    )
    tradein = m.env["fix.tradein.request"].browse(out["id"])
    harvest = m.env["fix.tradein.harvest"].create(
        {"tradein_id": tradein.id, "component": "board", "target": "recycle", "state": "harvested"}
    )
    back = (
        m.env["fix.ewaste.collection"]
        .sudo()
        .consume_tradein_harvested(
            {"aggregate": harvest._name, "aggregate_id": harvest.id, "payload": {}}
        )
    )
    assert back == col  # the original, not a new 0 kg item
    assert col.state == "collected" and col.weight_kg == 0.6 and col.reopened_count == 1
    assert not m.env["fix.ewaste.collection"].search_count(
        [("source_model", "=", tradein._name), ("source_res_id", "=", tradein.id)]
    )
    new = m.triage(col, "recycle")
    assert new.supersedes_id == first and col.triage_id == new
    # a repeat delivery is a no-op
    assert (
        m.env["fix.ewaste.collection"]
        .sudo()
        .consume_tradein_harvested(
            {"aggregate": harvest._name, "aggregate_id": harvest.id, "payload": {}}
        )
        == col
    )
    assert col.state == "triaged"
    # nobody but the hand-off re-opens a routed item
    other = m.collection(device_id=m.device().id, weight_kg=0.3)
    m.triage(other, "reuse")
    assert refused(m.env, lambda: other.write({"state": "collected"}))


# ===================================================== M18-15 / M18-16 / M18-21
def test_basel_consent_quantity_is_cumulative(m):
    partner = m.approved_partner()
    pic = (
        m.env["fix.ewaste.basel.pic"]
        .with_user(m.compliance)
        .create(
            {
                "partner_id": partner.id,
                "destination_country_id": m.env.ref("base.in").id,
                "importing_authority": "CPCB",
                "consent_ref": "PIC-S3",
                "max_weight_kg": 1.0,
                "valid_to": m.today + timedelta(days=90),
                "evidence_attachment_id": attachment(m.env, "pic.pdf").id,
            }
        )
    )
    pic.with_user(m.compliance2).action_record_consent()

    def batch_for(weight):
        item = m.ready_item(weight=weight)
        b = m.batch(partner=partner)
        b.action_load_ready_items()
        b.write({"destination_country_id": m.env.ref("base.in").id, "basel_pic_id": pic.id})
        m.weigh_out(b)
        return b, item

    b1, _ = batch_for(0.6)
    b1.action_dispatch()
    b2, item2 = batch_for(0.6)
    with pytest.raises(UserError, match="already left under it"), m.env.cr.savepoint():
        b2.action_dispatch()


def test_outbound_weighing_is_reconciled_before_the_manifest(m):
    item = m.ready_item(weight=1.0)
    b = m.batch()
    b.action_load_ready_items()
    with pytest.raises(UserError, match="weigh it out"), m.env.cr.savepoint():
        b.action_dispatch()
    m.weigh_out(b, net=1.2)
    with pytest.raises(UserError, match="outside the"), m.env.cr.savepoint():
        b.action_dispatch()
    assert not b.manifest_id
    m.weigh_out(b, net=1.02)
    b.action_dispatch()
    assert b.manifest_id.outbound_net_kg == pytest.approx(1.02)
    assert events(m.env, "ewaste.transferred", b.id) == 1
    assert item.batch_id == b
    # the recycler's weight is reconciled to what left (1.02), not stacked
    b.write({"received_weight_kg": 1.06, "recycler_receipt_ref": "R"})
    b.action_receive()
    assert b.state == "received"


def test_the_assessor_does_not_authorise_the_transfer(m):
    both = make_user(m.env, "assessdisp", [G.assessor, G.dispatcher], employee=True)
    dev = m.device()
    col = m.collection(device_id=dev.id, weight_kg=0.5)
    cert = m.verified_cert(dev.serial_number)
    m.env["fix.ewaste.triage"].with_user(both).create(
        {"collection_id": col.id, "decision": "recycle", "data_bearing": True}
    )
    col.write({"wipe_certificate_id": cert.id})
    col.with_user(m.dispatcher).action_secure_destruction()
    col.with_user(m.dispatcher).action_recycle_estimated()
    b = m.batch()
    b.action_load_ready_items()
    m.weigh_out(b)
    with pytest.raises(UserError, match="You triaged"), m.env.cr.savepoint():
        b.with_user(both).action_dispatch()
    b.with_user(m.dispatcher).action_dispatch()
    assert b.state == "dispatched"


# ===================================================== M18-17
def test_next_review_is_guarded_and_at_most_a_quarter_away(m):
    ob = (
        m.env["fix.ewaste.obligation"]
        .with_user(m.compliance)
        .create(
            {
                "name": "Annual return",
                "citation": "Rule 15",
                "obligation_text": "File Form-3",
                "owner_id": m.compliance.id,
                "evidence_source": "DoE portal",
                "frequency": "annual",
            }
        )
    )
    assert refused(
        m.env, lambda: ob.with_user(m.compliance).write({"next_review": m.today + timedelta(400)})
    )
    ob.with_user(m.compliance).action_activate()
    assert ob.next_review <= m.today + timedelta(days=92)
    assert refused(
        m.env, lambda: ob.with_user(m.compliance).write({"next_review": m.today + timedelta(30)})
    )
    with pytest.raises(ValidationError), m.env.cr.savepoint():
        ob.sudo().write({"next_review": m.today + timedelta(days=200)})
        m.env.flush_all()


# ===================================================== M18-28
def test_quick_triage_honours_the_criteria_and_floor_roles(m):
    crit = (
        m.env["fix.ewaste.triage.criteria"]
        .with_user(m.compliance)
        .create(
            {
                "name": "S3-V%d" % next(_N),
                "reuse_criteria": "works",
                "harvest_criteria": "parts",
                "recycle_criteria": "dead",
                "hazardous_criteria": "battery",
                "donation_max_value": 3000,
            }
        )
    )
    crit.with_user(m.compliance2).action_publish()
    col = m.collection(weight_kg=0.5)
    with pytest.raises(UserError, match="Triage & Sanitization Record"), m.env.cr.savepoint():
        col.with_user(m.assessor).action_triage_recycle()
    col.with_user(m.assessor).action_triage_recycle(
        functional_result="fail",
        evidence_file=base64.b64encode(b"photo"),
        evidence_filename="p.jpg",
    )
    assert col.state == "triaged" and col.triage_id.criteria_id == crit
    assert col.triage_id.evidence_attachment_id
    # destruction is the floor's, not a clerk's
    assert refused(m.env, lambda: col.with_user(m.clerk).action_secure_destruction())


# ===================================================== M18-27
def test_storage_clock_skips_hazmat_whose_cells_left(m):
    point = _point(m)
    col = _hazmat(m, point)
    bat = col.battery_ids
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_ewaste_collection SET collected_on=%s WHERE id=%s",
        (m.today - timedelta(days=200), col.id),
    )
    m.env.invalidate_all()
    col._compute_storage_deadline()
    m.env.cr.execute("UPDATE fix_ewaste_battery SET state='dispatched' WHERE id=%s", (bat.id,))
    m.env.invalidate_all()
    m.env["fix.ewaste.collection"].cron_storage_clock()
    assert not col.storage_overdue
    m.env.cr.execute("UPDATE fix_ewaste_battery SET state='stored' WHERE id=%s", (bat.id,))
    m.env.invalidate_all()
    m.env["fix.ewaste.collection"].cron_storage_clock()
    assert col.storage_overdue


# ===================================================== M18-29
def test_licence_warnings_at_t60_t30_t7(m):
    p = m.approved_partner()
    Partner = m.env["fix.ewaste.partner"]
    for days, stage in ((55, 60), (25, 30), (5, 7)):
        p.sudo().write({"valid_to": m.today + timedelta(days=days)})
        Partner.cron_licence_expiry()
        assert p.expiry_warned_stage == stage, (days, p.expiry_warned_stage)
    Partner.cron_licence_expiry()
    assert p.expiry_warned_stage == 7
    p.sudo().write({"valid_from": m.today - timedelta(days=60)})
    m.env.cr.execute(
        "UPDATE fix_ewaste_partner SET valid_to=%s WHERE id=%s", (m.today - timedelta(1), p.id)
    )
    m.env.invalidate_all()
    Partner.cron_licence_expiry()
    assert p.state == "expired"
    assert events(m.env, "ewaste.partner_suspended", p.id) == 1


# ===================================================== M18-25
def test_the_business_day_is_dhaka_whatever_the_user(m, monkeypatch):
    from odoo.orm import fields_temporal

    class Late(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 11, 20, 20, 30)  # 20:30 UTC = 02:30 Dhaka, 21 Nov

    monkeypatch.setattr(fields_temporal, "datetime", Late)
    m.clerk.sudo().write({"tz": False})
    env = m.env(user=m.clerk.id, context={})
    assert c.today(env).isoformat() == "2026-11-21"


# ===================================================== M18-11 / M18-24
def test_doe_return_is_a_kg_mass_balance_with_epr(m):
    reg = m.registration()
    reg.sudo().write({"epr_target_pct": 10.0})
    period = m.today.strftime("%Y-%m")
    start, end = c.period_bounds(period)
    old = m.collection(weight_kg=2.0)
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_ewaste_collection SET collected_on=%s WHERE id=%s",
        (start - timedelta(days=5), old.id),
    )
    m.env.invalidate_all()
    b = _processed_batch(m)  # one 1.0 kg item in and out this period
    m.env["fix.ewaste.material.recovery"].with_user(m.dispatcher).create(
        {"batch_id": b.id, "material_class": "pcb", "weight_kg": 0.4, "agreed_rate": 10.0}
    )
    ret = (
        m.env["fix.ewaste.return"]
        .with_user(m.compliance)
        .create({"period": period, "due_date": m.today + timedelta(10), "epr_base_kg": 10.0})
    )
    ret.with_user(m.compliance).action_calculate_mass_balance()
    assert ret.opening_kg >= 2.0
    assert ret.opening_kg + ret.received_kg - ret.out_kg == pytest.approx(ret.closing_kg)
    assert ret.treated_kg == pytest.approx(b.processed_weight_kg)
    assert ret.recovered_kg == pytest.approx(0.4)
    assert ret.disposed_kg == pytest.approx(ret.treated_kg - 0.4)
    assert ret.recovery_rate_pct == pytest.approx(round(0.4 / ret.treated_kg * 100, 2))
    assert ret.recovery_rate_pct <= 100.0
    assert ret.epr_target_pct == 10.0
    assert ret.epr_achievement_pct == pytest.approx(round(ret.received_kg / 10.0 * 100, 2))
    assert refused(m.env, lambda: ret.with_user(m.compliance).write({"recovered_kg": 9.0}))
    ret.with_user(m.compliance).action_submit_return()
    assert events(m.env, "esg.statutory_return_filed", ret.id) == 1


# ===================================================== M18-09 / M18-26
def test_one_gri_306_4_diversion_and_restatement_on_revoke(m):
    period = m.today.strftime("%Y-%m")
    start, end = c.period_bounds(period)
    Metric = m.env["fix.esg.metric"]
    base = Metric._fix_gri_306_4(m.env.company, start, end)
    reuse = m.collection(device_id=m.device().id, weight_kg=0.5)
    m.triage(reuse, "reuse")
    m.ready_item(weight=1.0)
    pending = m.ready_item(weight=0.7, material="laptop")  # recycled, not batched
    b = _processed_batch(m)
    cert = m.issued_certificate(b)
    certified = b.collection_ids
    gri = Metric._fix_gri_306_4(m.env.company, start, end)
    assert gri["triaged_kg"] - base["triaged_kg"] == pytest.approx(
        0.5 + 0.7 + sum(certified.mapped("weight_kg"))
    )
    assert gri["by_operation"]["reuse"] - base["by_operation"]["reuse"] == pytest.approx(0.5)
    assert gri["by_operation"]["recycle"] - base["by_operation"]["recycle"] == pytest.approx(
        sum(certified.mapped("weight_kg"))
    )
    assert pending.state != "certified"
    # GRI 306-4: certified recycling is diversion, like reuse
    assert gri["diverted_kg"] - base["diverted_kg"] == pytest.approx(
        0.5 + sum(certified.mapped("weight_kg"))
    )
    assert gri["diversion_rate_pct"] == pytest.approx(
        round(gri["diverted_kg"] / gri["triaged_kg"] * 100, 2)
    )
    rows = Metric.compute_period(period, m.env.company)
    rate = rows.filtered(lambda r: r.metric_type == "diversion_rate")
    assert rate.value == pytest.approx(gri["diversion_rate_pct"]) and rate.unit == "%"
    co2_before = rows.filtered(lambda r: r.metric_type == "co2_saved").value
    published = m.env["fix.event.outbox"].search_count(
        [("event_type", "=", "esg.metrics_published")]
    )
    cert.write({"revoke_reason": "audit failure"})
    cert.with_user(m.compliance).action_revoke()
    co2_after = Metric.search(
        [("period", "=", period), ("metric_type", "=", "co2_saved"), ("computed", "=", True)]
    ).value
    assert co2_after < co2_before  # restated at the revoke, not at month end
    assert (
        m.env["fix.event.outbox"].search_count([("event_type", "=", "esg.metrics_published")])
        > published
    )


# ===================================================== I1 + M49: one unit, one item
def _retired_rental_unit(m):
    """A rental unit retired on the recycle route: its M49 disposal (opened by
    the retirement with ewaste_route) posted, as S1's retirement leaves it."""
    env = m.env
    n = next(_N)
    tmpl = env["product.template"].create({"name": "S3 rental router %d" % n})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    sku = env["fix.rental.sku"].create({"catalogue_item_id": item.id})
    device = m.device()
    asset = env["fix.rental.asset"].create(
        {
            "name": "S3-RENT-%d" % n,
            "rental_sku_id": sku.id,
            "purchase_cost": 50000.0,
            "device_id": device.id,
            "operating_unit_id": m.ou.id,
        }
    )
    fa = env["fix.fixed.asset"].create(
        {
            "name": "S3 M49 %d" % n,
            "gross": 50000,
            "life_months": 36,
            "purchase_date": m.today,
            "category": "Rental fleet",
            "company_id": env.company.id,
        }
    )
    fa.write({"state": "active"})
    disposal = env["fix.asset.disposal"].browse(fa.action_dispose()["disposal_ids"][:1])
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_asset_disposal SET state='posted', kind='scrap', ewaste_route=true, "
        "ewaste_weight_kg=1.8, ewaste_material='other', ewaste_device_res_id=%s WHERE id=%s",
        (device.id, disposal.id),
    )
    env.cr.execute(
        "UPDATE fix_rental_asset SET status='retired', disposal_id=%s, fixed_asset_id=%s "
        "WHERE id=%s",
        (disposal.id, fa.id, asset.id),
    )
    env.invalidate_all()
    return asset, fa, disposal


def _i1(m, asset):
    return (
        m.env["fix.ewaste.collection"]
        .sudo()
        .consume_rental_asset_retired(
            {
                "aggregate": "fix.rental.asset",
                "aggregate_id": asset.id,
                "payload": {
                    "asset_id": asset.id,
                    "route": "recycle",
                    "weight_kg": 1.8,
                    "material": "other",
                    "serial": asset.device_id.serial_number,
                },
            }
        )
    )


def _m49(m, fa):
    return m.env["fix.asset.disposal"].sudo().consume_asset_disposed_m18({"aggregate_id": fa.id})


def _unit_collections(m, asset, disposal):
    return m.env["fix.ewaste.collection"].search(
        [
            "|",
            "|",
            "&",
            ("source_model", "=", asset._name),
            ("source_res_id", "=", asset.id),
            "&",
            ("source_model", "=", disposal._name),
            ("source_res_id", "=", disposal.id),
            ("device_id", "=", asset.device_id.id),
        ]
    )


def test_i1_then_m49_gives_one_collection(m):
    asset, fa, disposal = _retired_rental_unit(m)
    col = _i1(m, asset)
    assert col.channel == "rental_retired" and col.weight_kg == 1.8
    assert col.device_id == asset.device_id and col.operating_unit_id == m.ou
    _m49(m, fa)
    assert _unit_collections(m, asset, disposal) == col
    assert disposal.ewaste_collection_res_id == col.id
    # repeats change nothing
    assert _i1(m, asset) == col
    _m49(m, fa)
    assert _unit_collections(m, asset, disposal) == col


def test_m49_then_i1_gives_one_collection(m):
    asset, fa, disposal = _retired_rental_unit(m)
    _m49(m, fa)
    first = _unit_collections(m, asset, disposal)
    assert len(first) == 1
    assert _i1(m, asset) == first
    assert _unit_collections(m, asset, disposal) == first
    assert first.channel == "rental_retired" and first.device_id == asset.device_id
    assert first.weight_kg == 1.8 and not first.weight_pending  # what the retirement weighed


# ===================================================== S2 mirror: paid once
def test_no_incentive_once_the_unit_was_paid_as_a_trade_in(m):
    col = m.collection(device_id=m.device().id, weight_kg=0.6, operating_unit_id=m.ou.id)
    m.triage(col, "reuse")
    out = (
        m.env["fix.tradein.request"]
        .sudo()
        .consume_ewaste_reuse_routed(
            {"aggregate": col._name, "aggregate_id": col.id, "payload": {}}
        )
    )
    tradein = m.env["fix.tradein.request"].browse(out["id"])
    s = _incentive(m, col=col)
    s.with_user(m.dispatcher).action_request_approval()  # not paid yet: routed
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_tradein_request SET paid_at=now() AT TIME ZONE 'UTC' WHERE id=%s",
        (tradein.id,),
    )
    m.env.invalidate_all()
    # the approval refuses ...
    task = inbox_task(s, m.cfo)
    with pytest.raises(UserError, match="trade-in"), m.env.cr.savepoint():
        task.with_user(m.cfo).action_approve()
    assert s.state == "draft"
    # ... and so does a new request
    s.with_user(m.dispatcher).action_recall_approval()
    with pytest.raises(UserError, match="trade-in"), m.env.cr.savepoint():
        s.with_user(m.dispatcher).action_request_approval()
