# A04 C2-C13 build (2026-11-04): M36 quotation, tender and bond controls,
# exercised as NON-ADMIN users with the roles that do the work.
#
# Each test replays an attack of working/A04_evidence/probes/m11_m36_m37/
# probe_m36.py (named in its docstring) as a role holder, so the evidence
# does not depend on the probe's plain clerk, who now lacks write access.
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_quotation.models.fix_quote_ops import ESIGN_PROVIDER_PARAM, esign_signature
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.addons.cd_workflow_engine.tests.approval_helpers import assigned, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)


class Ctx:
    pass


def _user(env, login, groups=()):
    Users = env["res.users"].with_context(no_reset_password=True)
    ids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    return Users.create({"name": login, "login": login, "group_ids": [(6, 0, ids)]})


def _branch(env):
    b = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if b:
        return b
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {"legal_name": "M36 Test Entity", "code": "M36E", "company_id": env.company.id}
    )
    return env["fix.branch"].create(
        {"name": "M36 Branch", "code": "M36-BR", "entity_id": entity.id, "operating_unit_id": ou.id}
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.today = fields.Date.context_today(env.user)
    x.clerk = _user(env, "m36t_clerk")
    x.author = _user(env, "m36t_author", ["cd_quotation.group_quotation_user"])
    x.author2 = _user(env, "m36t_author2", ["cd_quotation.group_quotation_user"])
    x.t1 = _user(env, "m36t_t1", ["cd_entity_config.group_dofa_tier_1"])
    x.t2 = _user(env, "m36t_t2", ["cd_entity_config.group_dofa_tier_2"])
    x.t3 = _user(env, "m36t_t3", ["cd_entity_config.group_dofa_tier_3"])
    x.coord = _user(env, "m36t_coord", ["cd_quotation.group_bid_coordinator"])
    x.member = _user(env, "m36t_member", ["cd_quotation.group_tender_committee"])
    x.member2 = _user(env, "m36t_member2", ["cd_quotation.group_tender_committee"])
    x.manager = _user(env, "m36t_manager", ["cd_quotation.group_quotation_manager"])
    x.branch = _branch(env)
    x.ou = x.branch.operating_unit_id or env["operating.unit"].search([], limit=1)
    x.customer = env["res.partner"].create({"name": "M36 Test Customer", "phone": "01711000361"})
    x.agency = env["res.partner"].create({"name": "M36 Ministry", "is_company": True})
    brand = env["fix.brand"].create({"name": "M36TBrand", "code": "M36T"})
    x.model = env["fix.device.model"].create({"name": "M36T Model", "brand_id": brand.id})
    x.n = 0
    return x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
        g.P03GenericApiController.model_write
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def call(user, **kw):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        return mw(ctl, **kw)

    try:
        yield call
    finally:
        g.request, s.request = old_g, old_s


def _estimate(c, amount=3000.0, discount=0.0):
    c.n += 1
    env = c.env
    dev = env["fix.device"].create(
        {
            "device_model_id": c.model.id,
            "owner_id": c.customer.id,
            "serial_number": "M36T-%03d" % c.n,
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": dev.id,
            "customer_id": c.customer.id,
            "branch_id": c.branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "M36 test",
        }
    )
    return env["fix.estimate"].create(
        {
            "order_id": order.id,
            "discount": discount,
            "operating_unit_id": c.ou.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "line_type": "labour",
                        "description": "labour",
                        "quantity": 1,
                        "unit_price": amount,
                    },
                )
            ],
        }
    )


def _approved_estimate(c, amount=3000.0):
    est = _estimate(c, amount)
    est.action_send()
    est.action_approve()
    assert est.state == "approved"
    return est


def _quote(c, user=None, **kw):
    vals = {
        "customer_id": c.customer.id,
        "value": 15000.0,
        "cost_amount": 9000.0,
        "valid_until": c.today + timedelta(days=15),
        "quote_type": "contract",
        "operating_unit_id": c.ou.id,
    }
    vals.update(kw)
    return c.env["fix.quotation"].with_user(user or c.author).create(vals)


def _approved_quote(c, **kw):
    q = _quote(c, **kw)
    q.with_user(c.author).action_submit(justification="test")
    task = inbox_task(q, c.t1) or inbox_task(q, c.t2) or inbox_task(q, c.t3)
    task.with_user(task.assigned_user_id).action_approve(comment="ok")
    assert q.state == "approved", q.state
    return q


def _sent_quote(c, **kw):
    q = _approved_quote(c, **kw)
    q.with_user(c.author).action_send()
    assert q.state == "sent"
    return q


def _events(env, event_type, model, res_id):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate", "=", model), ("aggregate_id", "=", res_id)]
    )


# =========================================================================== roles
def test_a_plain_user_reads_but_cannot_write_m36_records(c):
    """§7.1: plain users keep read; the work goes to the role."""
    q = _quote(c)
    assert c.env["fix.quotation"].with_user(c.clerk).search([("id", "=", q.id)])
    for model, vals in (
        ("fix.quotation", {"customer_id": c.customer.id}),
        ("fix.tender", {"name": "x", "client_name": "y", "due_date": c.today}),
    ):
        with pytest.raises(AccessError), c.env.cr.savepoint():
            c.env[model].with_user(c.clerk).create(vals)
    with pytest.raises(AccessError), c.env.cr.savepoint():
        q.with_user(c.clerk).write({"cost_amount": 1.0})


# =========================================================================== quotation guard
def test_quote_state_esign_and_signed_at_cannot_be_written(c):
    """probe q_01/q_02/q_05: forged signature, back-dated signed_at, accepted
    after expiry by writing the fields."""
    q = _quote(c)
    for vals in (
        {"esign_state": "signed", "state": "accepted"},
        {"signed_at": "2026-10-01 09:00:00"},
        {"state": "accepted"},
        {"margin_pct": 45.0},
    ):
        with pytest.raises(UserError), c.env.cr.savepoint():
            q.with_user(c.author).write(vals)
    with pytest.raises(UserError), c.env.cr.savepoint():
        _quote(c, state="accepted")


def test_quote_workflow_fields_refused_through_p03(c, p03):
    """probe q_03."""
    q = _quote(c)
    res = p03(c.author, model="fix.quotation", record_id=q.id, values={"esign_state": "signed"})
    assert res.get("error")
    res = p03(c.author, model="fix.quotation", record_id=q.id, values={"state": "accepted"})
    assert res.get("error")
    q.invalidate_recordset()
    assert (q.state, q.esign_state) == ("draft", "none")


def test_quote_has_a_lifecycle_and_no_cost_means_unknown_margin(c):
    """probe q_06/q_08/q_09."""
    q = _quote(c, cost_amount=0.0)
    assert (q.margin_pct, q.margin_known) == (0.0, False)
    with pytest.raises(UserError, match="direct cost"), c.env.cr.savepoint():
        q.with_user(c.author).action_submit()
    q2 = _quote(c, value=10000.0, cost_amount=7500.0)
    assert (q2.margin_pct, q2.margin_known) == (25.0, True)


def test_quote_value_is_the_estimate_total(c):
    """probe q_07: BDT 1 quoted on a BDT 3,450 estimate."""
    est = _approved_estimate(c)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _quote(c, quote_type="service", estimate_id=est.id, value=1.0)
    q = (
        c.env["fix.quotation"]
        .with_user(c.author)
        .create(
            {
                "estimate_id": est.id,
                "cost_amount": 1000.0,
                "valid_until": c.today + timedelta(days=5),
            }
        )
    )
    assert q.value == est.grand_total and q.customer_id == c.customer


def test_quotation_numbers_come_from_a_sequence(c):
    """probe q_11: a count-based number was reused after a delete."""
    q1, q2 = _quote(c), _quote(c)
    names = {q1.name, q2.name}
    q1.sudo().unlink()
    q3 = _quote(c)
    assert len(names | {q3.name}) == 3 and q3.name.startswith("QTN/")


# =========================================================================== internal approval
def test_quote_review_is_the_approvers_decision_not_a_typed_row(c):
    """probe qr_01/qr_02: a review in someone else's name, or one's own."""
    q = _quote(c)
    for vals in ({"reviewer_id": c.t3.id, "decision": "approved"}, {"decision": "approved"}):
        with pytest.raises(REFUSED), c.env.cr.savepoint():
            c.env["fix.quote.review"].with_user(c.author).create(dict(vals, quotation_id=q.id))
    q.with_user(c.author).action_submit()
    assert c.author not in assigned(q) and c.t1 in assigned(q)
    with pytest.raises(UserError, match="inbox"), c.env.cr.savepoint():
        q.with_user(c.t1).action_approve_quote()
    inbox_task(q, c.t1).with_user(c.t1).action_approve(comment="fine")
    assert q.state == "approved" and q.dofa_approved_by == c.t1
    review = c.env["fix.quote.review"].search([("quotation_id", "=", q.id)])
    assert (review.reviewer_id, review.decision, review.version) == (c.t1, "approved", 1)


def test_rejected_review_blocks_issue(c):
    """probe qr_03."""
    q = _quote(c)
    q.with_user(c.author).action_submit()
    inbox_task(q, c.t1).with_user(c.t1).action_reject(comment="margin too thin")
    assert (q.state, q.approval_state) == ("draft", "rejected")
    assert c.env["fix.quote.review"].search([("quotation_id", "=", q.id)]).decision == "rejected"
    with pytest.raises(UserError), c.env.cr.savepoint():
        q.with_user(c.author).action_send()


def test_value_band_routes_above_25k_to_a_branch_manager(c):
    """BRU-QTE-06: above BDT 25,000 a Branch Manager (Tier 2) approves, with a
    justification."""
    q = _quote(c, value=30000.0, cost_amount=20000.0)
    with pytest.raises(UserError, match="justification"), c.env.cr.savepoint():
        q.with_user(c.author).action_submit()
    q.with_user(c.author).action_submit(justification="corporate account")
    assert c.t2 in assigned(q) and c.t1 not in assigned(q)


def test_a_change_after_approval_needs_re_approval(c):
    """Snapshot re-approval: the approval covered the terms it was given for."""
    q = _approved_quote(c)
    q.with_user(c.author).write({"cost_amount": 12000.0})
    assert (q.state, q.approval_state, q.dofa_approved) == ("draft", "none", False)
    with pytest.raises(UserError), c.env.cr.savepoint():
        q.with_user(c.author).action_send()


def test_an_issued_version_is_immutable_and_revised_as_a_new_one(c):
    """BRU-QTE-02/04."""
    q = _sent_quote(c)
    assert _events(c.env, "quotation.issued", "fix.quotation", q.id)
    with pytest.raises(UserError, match="immutable"), c.env.cr.savepoint():
        q.with_user(c.author).write({"value": 1.0})
    action = q.with_user(c.author).action_revise()
    new = c.env["fix.quotation"].browse(action["res_id"])
    assert (new.name, new.version, new.state, new.parent_version_id) == (q.name, 2, "draft", q)
    assert q.state == "superseded"


# =========================================================================== customer acceptance
def test_otp_acceptance_within_validity_hands_off_to_the_contract(c, monkeypatch):
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    q = _sent_quote(c)
    q.with_user(c.author).action_send_acceptance_otp()
    assert q.with_user(c.author).action_verify_acceptance_otp(otp="000000x")["verified"] is False
    assert q.state == "sent"
    q.with_user(c.author).action_verify_acceptance_otp(otp=sent[-1])
    assert (q.state, q.acceptance_method, q.accepted_value) == ("accepted", "otp", 15000.0)
    assert len(q.evidence_hash) == 64 and q.acceptance_recorded_by == c.author
    if "fix.contract" in c.env:
        contract = c.env["fix.contract"].browse(q.converted_res_id)
        assert q.converted_res_model == "fix.contract" and contract.customer_id == c.customer
        assert contract.state == "draft" and round(contract.annual_value, 2) == 15000.0
    with pytest.raises(UserError), c.env.cr.savepoint():
        q.with_user(c.author).action_decline(reason="changed mind", code="price")


def test_acceptance_after_expiry_is_refused(c, monkeypatch):
    """probe q_05 / BRU-QTE-03."""
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    q = _sent_quote(c)
    q.with_user(c.author).action_send_acceptance_otp()
    c.env.cr.execute(
        "UPDATE fix_quotation SET valid_until = %s WHERE id = %s",
        (c.today - timedelta(days=1), q.id),
    )
    q.invalidate_recordset()
    with pytest.raises(UserError, match="BRU-QTE-03"), c.env.cr.savepoint():
        q.with_user(c.author).action_verify_acceptance_otp(otp=sent[-1])
    assert c.env["fix.quotation"].cron_expire_quotations() >= 1
    assert q.state == "expired"


def test_signed_acceptance_is_recorded_by_someone_other_than_the_author(c):
    q = _sent_quote(c)
    att = c.env["ir.attachment"].create({"name": "signed.pdf", "raw": b"%PDF signed"})
    q.with_user(c.author).write({"signed_attachment_id": att.id})
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        q.with_user(c.author).action_record_signed_acceptance()
    q.with_user(c.author2).action_record_signed_acceptance()
    assert (q.state, q.acceptance_method) == ("accepted", "signed_form")
    with pytest.raises(UserError), c.env.cr.savepoint():
        q.with_user(c.author).write({"cost_amount": 1.0})


def test_esign_acceptance_only_from_the_verified_provider_callback(c):
    """probe q_01: e-signature completed by the provider, not forged."""
    q = _sent_quote(c)
    Q = c.env["fix.quotation"].sudo()
    with pytest.raises(UserError, match="provider"), c.env.cr.savepoint():
        Q._esign_provider_complete(q.name, q.version, "SIG-1", "x")
    c.env["ir.config_parameter"].set_param(ESIGN_PROVIDER_PARAM, "test-secret")
    with pytest.raises(UserError, match="verify"), c.env.cr.savepoint():
        Q._esign_provider_complete(q.name, q.version, "SIG-1", "forged")
    good = esign_signature("test-secret", q.name, q.version, q.value, "SIG-1")
    Q._esign_provider_complete(q.name, q.version, "SIG-1", good)
    assert (q.state, q.esign_state, q.acceptance_method) == ("accepted", "signed", "esign")
    assert q.signed_at and q.esign_provider_ref == "SIG-1"


def test_decline_needs_a_governed_reason(c):
    """BRU-QTE-16."""
    q = _sent_quote(c)
    with pytest.raises(UserError, match="governed"), c.env.cr.savepoint():
        q.with_user(c.author).action_decline(reason="too dear")
    q.with_user(c.author).action_decline(reason="too dear", code="price")
    assert q.state == "declined" and q.decline_reason.startswith("Price too high")


def test_a_service_quote_releases_its_service_order(c, monkeypatch):
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    est = _approved_estimate(c)
    q = _sent_quote(
        c, quote_type="service", estimate_id=est.id, value=est.grand_total, cost_amount=1000.0
    )
    q.with_user(c.author).action_send_acceptance_otp()
    q.with_user(c.author).action_verify_acceptance_otp(otp=sent[-1])
    assert q.state == "accepted" and q.service_order_id == est.order_id
    assert _events(c.env, "quotation.accepted", "fix.quotation", q.id)


# =========================================================================== estimate quotation
def test_estimate_quotation_state_cannot_be_written(c, p03):
    """probe eq_01/eq_02."""
    est = _estimate(c)
    with pytest.raises(UserError), c.env.cr.savepoint():
        est.with_user(c.clerk).write({"quotation_state": "accepted"})
    res = p03(
        c.clerk, model="fix.estimate", record_id=est.id, values={"quotation_state": "accepted"}
    )
    est.invalidate_recordset()
    assert res.get("error") and est.quotation_state == "internal"


def test_estimate_quote_accept_decline_rules(c):
    """probe eq_06/eq_07/eq_08."""
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import SURFACES

    assert {"action_quote", "action_accept", "action_decline"} <= SURFACES["fix.estimate"][
        "actions"
    ]
    est = _approved_estimate(c)
    est.with_user(c.clerk).action_quote()
    c.env.flush_all()  # the quote's own sent_at would overwrite the UPDATE
    c.env.cr.execute(
        "UPDATE fix_estimate SET sent_at = now() - interval '30 days' WHERE id = %s", (est.id,)
    )
    est.invalidate_recordset()
    with pytest.raises(UserError, match="BRU-QTE-03"), c.env.cr.savepoint():
        est.with_user(c.clerk).action_accept()
    est2 = _approved_estimate(c)
    est2.with_user(c.clerk).action_quote()
    with pytest.raises(UserError, match="why"), c.env.cr.savepoint():
        est2.with_user(c.clerk).action_decline()
    est2.with_user(c.clerk).action_accept()
    with pytest.raises(UserError), c.env.cr.savepoint():
        est2.with_user(c.clerk).action_decline(reason="changed mind")
    assert est2.quotation_state == "accepted"


# =========================================================================== discount approval
def test_discount_approval_is_pinned_to_its_percent_and_estimate(c):
    """probe da_07/da_08/da_10."""
    Approval = c.env["fix.discount.approval"]
    est = _estimate(c)

    def req(pct, e=est):
        return Approval.with_user(c.clerk).create(
            {
                "quotation_id": e.id,
                "operating_unit_id": c.ou.id,
                "discount_pct": pct,
                "justification": "t",
            }
        )

    small = req(3.0)
    assert (small.state, small.approved_pct) == ("approved", 3.0)
    with pytest.raises(UserError, match="decided"), c.env.cr.savepoint():
        small.with_user(c.clerk).write({"discount_pct": 45.0})
    mid = req(15.0)
    mid.with_user(c.clerk).action_request_approval(justification="match")
    inbox_task(mid, c.t2).with_user(c.t2).action_approve(comment="ok")
    assert (mid.state, mid.approved_pct) == ("approved", 15.0)
    with pytest.raises(UserError, match="decided"), c.env.cr.savepoint():
        mid.with_user(c.clerk).write({"discount_pct": 40.0})
    deep = _estimate(c, 10000.0, discount=4000.0)
    typed_low = req(2.0, deep)
    assert typed_low.discount_pct == pytest.approx(deep.discount_pct, abs=0.01)
    assert typed_low.state == "pending"


def test_an_approved_discount_must_cover_the_discount_quoted(c):
    """A request approves the discount it was decided for, not a later, deeper one."""
    est = _estimate(c, 3000.0)
    a = (
        c.env["fix.discount.approval"]
        .with_user(c.clerk)
        .create(
            {
                "quotation_id": est.id,
                "operating_unit_id": c.ou.id,
                "discount_pct": 3.0,
                "justification": "t",
            }
        )
    )
    assert a.state == "approved"
    est.write({"discount": 120.0})  # now 4%: within the front desk, but above the 3% approved
    est.action_send()
    est.action_approve()
    with pytest.raises(UserError, match="does not cover"), c.env.cr.savepoint():
        est.with_user(c.clerk).action_quote()


# =========================================================================== tender
def _tender(c, **kw):
    vals = {
        "name": "M36 Tender",
        "client_name": "BD Ministry",
        "client_id": c.agency.id,
        "operating_unit_id": c.ou.id,
        "estimated_value": 750000.0,
        "bid_value": 700000.0,
        "due_date": c.today + timedelta(days=10),
        "score_fit": 4,
        "score_capacity": 4,
        "score_competition": 3,
        "score_margin": 3,
        "score_risk": 2,
        "requirement_ids": [
            (0, 0, {"requirement": "Trade licence", "state": "complied", "evidence_ref": "TL-1"})
        ],
    }
    vals.update(kw)
    return c.env["fix.tender"].with_user(c.coord).create(vals)


def _bond(c, t, **kw):
    vals = {
        "tender_id": t.id,
        "bond_type": "bid",
        "amount": 20000.0,
        "bank": "Sonali Bank",
        "guarantee_no": "BG-%s" % (c.n + 1),
        "expires_on": c.today + timedelta(days=120),
    }
    c.n += 1
    vals.update(kw)
    return c.env["fix.tender.bond"].with_user(c.coord).create(vals)


def _submitted(c, **kw):
    t = _tender(c, **kw)
    t.with_user(c.member).action_decide_bid(reason="good fit")
    if t.bonds_required:
        _bond(c, t).with_user(c.coord).action_activate()
    t.with_user(c.coord).action_submit()
    assert t.state == "submitted"
    return t


def test_tender_state_and_compliance_cannot_be_typed(c, p03):
    """probe t_01/t_02."""
    t = _tender(c)
    for vals in ({"state": "won"}, {"compliance_pct": 50.0}, {"bid_decision": "bid"}):
        with pytest.raises(UserError), c.env.cr.savepoint():
            t.with_user(c.coord).write(vals)
    res = p03(c.coord, model="fix.tender", record_id=t.id, values={"state": "won"})
    assert res.get("error")


def test_bid_decision_is_the_committees(c):
    """probe t_08 / FR-QTE-044."""
    t = _tender(c)
    with pytest.raises(AccessError), c.env.cr.savepoint():
        t.with_user(c.coord).action_decide_bid(reason="x")
    unscored = _tender(c, score_risk=0)
    with pytest.raises(UserError, match="Score"), c.env.cr.savepoint():
        unscored.with_user(c.member).action_decide_bid(reason="x")
    t.with_user(c.member).action_decide_bid(reason="fits our AMC capability")
    assert (t.bid_decision, t.bid_decision_by, t.bid_score) == ("bid", c.member, 3.2)
    nb = _tender(c)
    nb.with_user(c.member).action_decide_no_bid(reason="capacity")
    assert nb.state == "no_bid"


def test_submission_gates(c):
    """probe t_03/t_04 / BRU-QTE-15."""
    t = _tender(c, requirement_ids=[(0, 0, {"requirement": "ISO cert"})])
    with pytest.raises(UserError, match="bid' decision"), c.env.cr.savepoint():
        t.with_user(c.coord).action_submit()
    t.with_user(c.member).action_decide_bid(reason="ok")
    with pytest.raises(UserError, match="still open"), c.env.cr.savepoint():
        t.with_user(c.coord).action_submit()
    with pytest.raises(ValidationError, match="evidence"), c.env.cr.savepoint():
        t.requirement_ids.with_user(c.coord).write({"state": "complied"})
    t.requirement_ids.with_user(c.coord).write({"state": "complied", "evidence_ref": "ISO-9001"})
    assert t.compliance_pct == 100.0
    t.with_user(c.coord).write({"bonds_required": True, "bid_security_amount": 20000.0})
    with pytest.raises(UserError, match="bid security"), c.env.cr.savepoint():
        t.with_user(c.coord).action_submit()
    short = _bond(c, t, expires_on=c.today + timedelta(days=20))
    short.with_user(c.coord).action_activate()
    with pytest.raises(UserError, match="28 days"), c.env.cr.savepoint():
        t.with_user(c.coord).action_submit()
    _bond(c, t).with_user(c.coord).action_activate()
    t.with_user(c.coord).action_submit()
    assert t.state == "submitted" and t.submitted_by == c.coord
    with pytest.raises(UserError, match="frozen"), c.env.cr.savepoint():
        t.requirement_ids.with_user(c.coord).write({"state": "open"})
    with pytest.raises(UserError), c.env.cr.savepoint():
        t.with_user(c.coord).write({"estimated_value": 1.0})


def test_award_is_a_committee_decision_and_creates_the_contract(c):
    """probe t_05/t_09/t_10 and C8."""
    t = _submitted(
        c, bonds_required=True, bid_security_amount=20000.0, performance_security_pct=10.0
    )
    with pytest.raises(UserError, match="award decision"), c.env.cr.savepoint():
        t.with_user(c.coord).action_record_outcome(True, "we won")
    with pytest.raises(UserError, match="Notification of Award"), c.env.cr.savepoint():
        t.with_user(c.coord).action_request_award()
    t.with_user(c.coord).write({"award_ref": "NOA-77", "awarded_value": 700000.0})
    t.with_user(c.coord).action_request_award(justification="NOA received")
    assert (c.member | c.member2) <= assigned(t) and c.coord not in assigned(t)
    with pytest.raises(UserError, match="inbox"), c.env.cr.savepoint():
        t.with_user(c.member).action_award_approve()
    inbox_task(t, c.member).with_user(c.member).action_approve(comment="award confirmed")
    assert (t.state, t.awarded_by) == ("won", c.member)
    if "fix.contract" in c.env:
        contract = c.env["fix.contract"].browse(t.converted_res_id)
        assert contract.customer_id == c.agency and contract.state == "draft"
        assert round(contract.annual_value, 2) == 700000.0
    perf = t._bonds("performance")
    assert perf.state == "draft" and perf.amount == 70000.0
    with pytest.raises(UserError), c.env.cr.savepoint():
        t.with_user(c.coord).action_cancel(reason="x")


def test_the_bid_preparer_cannot_approve_the_award(c):
    """PPR 2008 r.36(2)-style separation."""
    both = _user(
        c.env,
        "m36t_both",
        ["cd_quotation.group_bid_coordinator", "cd_quotation.group_tender_committee"],
    )
    t = _tender(c)
    t.with_user(c.member).action_decide_bid(reason="ok")
    t.with_user(both).action_submit()
    t.with_user(c.coord).write({"award_ref": "NOA-1", "awarded_value": 700000.0})
    t.with_user(c.coord).action_request_award()
    task = inbox_task(t, both)
    assert task
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        task.with_user(both).action_approve(comment="mine")


def test_won_needs_a_valid_bid_security(c):
    """probe t_06/t_07: an amount-0 bond typed active, or an expired one."""
    t = _submitted(c, bonds_required=True, bid_security_amount=20000.0)
    with pytest.raises(UserError), c.env.cr.savepoint():
        _bond(c, t, state="active", amount=0.0)
    c.env.cr.execute(
        "UPDATE fix_tender_bond SET expires_on = %s WHERE tender_id = %s",
        (c.today - timedelta(days=5), t.id),
    )
    c.env["fix.tender.bond"].invalidate_model()
    t.with_user(c.coord).write({"award_ref": "NOA-2", "awarded_value": 600000.0})
    with pytest.raises(UserError, match="bid security"), c.env.cr.savepoint():
        t.with_user(c.coord).action_request_award()


def test_a_loss_records_its_reason(c):
    t = _submitted(c)
    with pytest.raises(UserError, match="loss reason"), c.env.cr.savepoint():
        t.with_user(c.coord).action_record_outcome(False, "")
    t.with_user(c.coord).action_record_loss(reason="price 4% higher")
    assert (t.state, t.loss_reason) == ("lost", "price 4% higher")


# =========================================================================== bonds
def test_bond_activation_needs_the_bank_evidence_and_the_band(c):
    """probe b_04/b_05."""
    t = _tender(c)
    with pytest.raises(UserError, match="guarantee number"), c.env.cr.savepoint():
        _bond(c, t, bank=False, guarantee_no=False).with_user(c.coord).action_activate()
    with pytest.raises(UserError, match="PPR 2008 r.25"), c.env.cr.savepoint():
        _bond(c, t, amount=37500.0).with_user(c.coord).action_activate()
    b = _bond(c, t)
    b.with_user(c.coord).action_activate()
    assert b.state == "active" and b.activated_by == c.coord
    assert _events(c.env, "tender_bond.activated", "fix.tender.bond", b.id)
    with pytest.raises(UserError, match="frozen"), c.env.cr.savepoint():
        b.with_user(c.coord).write({"amount": 1.0})


def test_bond_release_only_after_the_award_by_a_dofa_approver(c, p03):
    """probe b_01/b_02/b_03/b_06."""
    t = _submitted(c, bonds_required=True, bid_security_amount=20000.0)
    b = t._bonds("bid", "active").with_user(c.coord)
    with pytest.raises(UserError, match="only after the outcome"), c.env.cr.savepoint():
        b.action_release(release_ref="BANK-1")
    draft = _bond(c, t)
    with pytest.raises(UserError, match="only an active"), c.env.cr.savepoint():
        draft.with_user(c.coord).action_claim(reason="x")
    res = p03(c.coord, model="fix.tender.bond", record_id=b.id, values={"state": "released"})
    assert res.get("error")
    t.with_user(c.coord).action_record_loss(reason="lost on price")
    b.action_release(release_ref="BANK-DISCHARGE-9")
    assert b.approval_state == "pending" and c.t2 in assigned(b) and c.coord not in assigned(b)
    with pytest.raises(UserError, match="inbox"), c.env.cr.savepoint():
        b.with_user(c.t2).action_bond_decision_approve()
    inbox_task(b, c.t2).with_user(c.t2).action_approve(comment="discharge letter seen")
    assert (b.state, b.released_by, b.requested_action) == ("released", c.t2, "none")
    assert _events(c.env, "tender_bond.released", "fix.tender.bond", b.id)
    with pytest.raises(UserError), c.env.cr.savepoint():
        b.action_claim(reason="flip")


def test_bond_expiry_is_live_and_the_cron_alerts_once(c):
    """probe b_08 / AUT-QTE-14."""
    t = _tender(c)
    b = _bond(c, t, expires_on=c.today + timedelta(days=40))
    b.with_user(c.coord).action_activate()
    assert not b.is_expiring_soon
    c.env.cr.execute(
        "UPDATE fix_tender_bond SET expires_on = expires_on - 35 WHERE id = %s", (b.id,)
    )
    b.invalidate_recordset()
    assert b.is_expiring_soon and b in c.env["fix.tender.bond"].search(
        [("is_expiring_soon", "=", True)]
    )
    Bond = c.env["fix.tender.bond"]
    assert Bond.cron_bond_expiry() >= 1 and b.expiry_alerted_on
    assert b.activity_ids.filtered(lambda a: a.user_id == c.coord)
    before = len(b.activity_ids)
    Bond.cron_bond_expiry()
    assert len(b.activity_ids) == before
    c.env.cr.execute(
        "UPDATE fix_tender_bond SET expires_on = %s WHERE id = %s",
        (c.today - timedelta(days=1), b.id),
    )
    b.invalidate_recordset()
    Bond.cron_bond_expiry()
    assert b.state == "expired"


# =========================================================================== crons and the workspace
@pytest.mark.parametrize(
    ("xmlid", "method"),
    [
        ("cd_quotation.ir_cron_quotation_expiry", "cron_expire_quotations"),
        ("cd_quotation.ir_cron_tender_bond_expiry", "cron_bond_expiry"),
    ],
)
def test_crons_exist_are_active_and_name_their_method(c, xmlid, method):
    cron = c.env.ref(xmlid)
    assert cron.active and method in cron.code
    model = c.env[cron.model_id.model]
    assert callable(getattr(model, method))


def test_m36_surfaces_declare_writable_and_their_actions(c):
    """probe p03_m36_surfaces_declare_writable / tender_actions_reachable."""
    from odoo.addons.cd_p03_portal.controllers.a04 import m36

    assert all("writable" in conf for conf in m36.SURFACES.values())
    assert {"state", "esign_state"}.isdisjoint(m36.SURFACES["fix.quotation"]["writable"])
    assert "state" not in m36.SURFACES["fix.tender.bond"]["writable"]
    need = {
        "fix.quotation": {"action_submit", "action_send", "action_verify_acceptance_otp"},
        "fix.tender": {
            "action_submit",
            "action_record_outcome",
            "action_cancel",
            "action_request_award",
        },
        "fix.tender.bond": {"action_activate", "action_release", "action_claim"},
    }
    for model, acts in need.items():
        assert acts <= m36.SURFACES[model]["actions"], model


# =========================================================================== follow-up: ladder, sale check, variation cap
@pytest.mark.parametrize(
    ("pct", "state", "tier"),
    [(10.0, "approved", False), (15.0, "pending", "tier_2"), (25.0, "pending", "tier_3")],
)
def test_discount_band_comes_from_the_single_m11_ladder(c, pct, state, tier):
    """BRU-PRC-06 / probe dp_01: fix.discount.approval reads the M11 ladder
    (fix.discount.policy.tier_for_discount), not its own 5% / 10% constants."""
    est = _estimate(c)
    a = (
        c.env["fix.discount.approval"]
        .with_user(c.clerk)
        .create(
            {
                "quotation_id": est.id,
                "operating_unit_id": c.ou.id,
                "discount_pct": pct,
                "justification": "t",
            }
        )
    )
    assert a.state == state and a._approval_tier() == tier
    if "fix.discount.policy" in c.env:
        assert a._discount_tier() == c.env["fix.discount.policy"].tier_for_discount(pct)
    if tier:
        a.with_user(c.clerk).action_request_approval(justification="x")
        routed = assigned(a)
        assert (c.t3 in routed) == (tier == "tier_3") and (c.t2 in routed) == (tier == "tier_2")


def test_quotation_lines_run_the_one_selling_check(c, monkeypatch):
    """B3's product._fix_check_sale (M37 lifecycle + M11 floor), channel
    'quotation', on every priced line of the quoted estimate."""
    Product = type(c.env["product.product"])
    if not hasattr(Product, "_fix_check_sale"):
        pytest.skip("cd_catalogue not installed")
    product = c.env["product.product"].create({"name": "M36 Screen"})
    est = _estimate(c)
    c.env["fix.estimate.line"].sudo().create(
        {
            "estimate_id": est.id,
            "line_type": "part",
            "product_id": product.id,
            "description": "screen",
            "quantity": 1,
            "unit_price": 100.0,
        }
    )
    est.action_send()
    est.action_approve()
    seen = []

    def refuse(self, unit_price=None, channel=None):
        seen.append(channel)
        if channel == "quotation":
            raise UserError("item discontinued")
        return True

    monkeypatch.setattr(Product, "_fix_check_sale", refuse)
    q = _quote(
        c, quote_type="service", estimate_id=est.id, value=est.grand_total, cost_amount=500.0
    )
    with pytest.raises(UserError, match="item discontinued"), c.env.cr.savepoint():
        q.with_user(c.author).action_submit()
    assert "quotation" in seen


def test_award_beyond_the_variation_cap_is_the_commercial_managers(c):
    """Report §6 P2 M36: an award 20% away from the bid lodged (cap 15%)."""
    t = _submitted(c)
    t.with_user(c.coord).write({"award_ref": "NOA-V", "awarded_value": 840000.0})  # +20% on 700k
    assert t.award_variation_pct == 20.0
    with pytest.raises(UserError, match="variation cap"), c.env.cr.savepoint():
        t.with_user(c.coord).action_request_award()
    t.with_user(c.coord).action_request_award(justification="scope added at negotiation")
    routed = assigned(t)
    assert c.manager in routed and c.member not in routed
    inbox_task(t, c.manager).with_user(c.manager).action_approve(comment="accepted")
    assert t.state == "won" and t.awarded_by == c.manager


def test_award_within_the_cap_stays_with_the_committee(c):
    c.env["ir.config_parameter"].set_param("cd_quotation.variation_cap_pct", "25")
    t = _submitted(c)
    t.with_user(c.coord).write({"award_ref": "NOA-W", "awarded_value": 840000.0})
    t.with_user(c.coord).action_request_award()
    assert c.member in assigned(t) and c.manager not in assigned(t)


def test_variation_orders_within_and_beyond_the_cap(c):
    t = _submitted(c)
    t.with_user(c.coord).write({"award_ref": "NOA-X", "awarded_value": 700000.0})
    t.with_user(c.coord).action_request_award()
    inbox_task(t, c.member).with_user(c.member).action_approve(comment="ok")
    V = c.env["fix.tender.variation"].with_user(c.coord)
    with pytest.raises(AccessError), c.env.cr.savepoint():
        c.env["fix.tender.variation"].with_user(c.clerk).create(
            {"name": "VO-0", "tender_id": t.id, "amount": 1.0, "reason": "x"}
        )
    small = V.create(
        {"name": "VO-1", "tender_id": t.id, "amount": 70000.0, "reason": "extra sites"}
    )
    assert small.within_cap and small.cumulative_pct == 10.0
    with pytest.raises(UserError), c.env.cr.savepoint():
        small.with_user(c.coord).write({"state": "approved"})
    small.with_user(c.coord).action_request(justification="client letter")
    assert c.member in assigned(small) and c.coord not in assigned(small)
    with pytest.raises(UserError, match="inbox"), c.env.cr.savepoint():
        small.with_user(c.member).action_approve_variation()
    inbox_task(small, c.member).with_user(c.member).action_approve(comment="ok")
    assert small.state == "approved" and t.contract_value == 770000.0
    assert _events(c.env, "tender.variation_approved", "fix.tender.variation", small.id)
    with pytest.raises(UserError, match="cannot change"), c.env.cr.savepoint():
        small.with_user(c.coord).write({"amount": 1.0})
    big = V.create({"name": "VO-2", "tender_id": t.id, "amount": -42000.0, "reason": "omission"})
    assert not big.within_cap and big.cumulative_pct == 16.0  # 70k + 42k on 700k
    big.with_user(c.coord).action_request(justification="client cut scope")
    assert c.manager in assigned(big) and c.member not in assigned(big)
    inbox_task(big, c.manager).with_user(c.manager).action_approve(comment="ok")
    assert big.state == "approved" and t.contract_value == 728000.0
