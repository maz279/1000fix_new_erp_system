"""A04 audit C2-C13 (M40): partner, programme and payout lifecycles.

Behaviour tests run as non-admin users created in the transaction (a plain
clerk, channel officers, a KYC officer, channel managers, rebate approvers
holding DOFA tiers, Tier-3 directors and a finance user). They replace the
October source-text tests (test_partner.py) for what the audit found open:
  - M40-8/9: onboarding forged by a write, self-ticked documents, no second
    person, re-onboarding a suspended partner, the PII mask crash;
  - M40-1/2/3: rebates paid by a write, from draft, past a context bypass of
    the audit gate, at 250%, and raised after payout;
  - M40-4/5/11: deal, authorisation and franchise lifecycles;
  - M40-6: the conflict ruling forged or changed;
  - M40-10: PDPA erasure forged, "blocked" lost, the party left intact.
fix.referral (A08) is not exercised here.
"""

import base64
import types
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GUARD = "changes only through its workflow"


def _mk(env, login, *xmlids):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                ],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    pa = "cd_partner.group_fix_channel_"
    tier = "cd_entity_config.group_dofa_tier_%d"
    x = types.SimpleNamespace(env=env)
    x.clerk = _mk(env, "a4pa_clerk")
    x.officer = _mk(env, "a4pa_officer", pa + "officer")
    x.officer2 = _mk(env, "a4pa_officer2", pa + "officer")
    x.kyc = _mk(env, "a4pa_kyc", pa + "kyc_officer")
    x.manager = _mk(env, "a4pa_manager", pa + "manager")
    x.manager2 = _mk(env, "a4pa_manager2", pa + "manager")
    x.approver = _mk(
        env, "a4pa_approver", "cd_partner.group_fix_rebate_approver", tier % 2, tier % 3, tier % 4
    )
    x.dir3 = _mk(env, "a4pa_dir3", tier % 3, pa + "officer")
    x.dir3b = _mk(env, "a4pa_dir3b", tier % 3)
    x.finance = _mk(env, "a4pa_finance", "account.group_account_invoice")
    x.party = env["res.partner"].create(
        {"name": "A4PA Reseller", "phone": "01711000401", "street": "Road 4", "city": "Dhaka"}
    )
    x.party_b = env["res.partner"].create({"name": "A4PA Reseller B"})
    x.customer = env["res.partner"].create({"name": "A4PA End Customer"})
    x.today = fields.Date.context_today(env.user)
    return x


def _partner(w, user=None, **kw):
    vals = {
        "name": "A4PA Partner",
        "partner_id": w.party.id,
        "partner_type": "reseller",
        "tin_number": "123456789012",
        "trade_license_no": "TL-1",
    }
    vals.update(kw)
    return w.env["fix.partner"].with_user(user or w.officer).create(vals)


def _onboarded(w, **kw):
    p = _partner(w, **kw)
    p.with_user(w.manager).action_onboard()
    return p


def _doc(w, record, name, user=None):
    return (
        w.env["ir.attachment"]
        .with_user(user or w.officer)
        .create(
            {
                "name": name,
                "res_model": record._name,
                "res_id": record.id,
                "datas": base64.b64encode(b"%PDF-1.4 a04 evidence"),
            }
        )
    )


def _audit(w, partner, score=90.0, approve=True, **kw):
    audit = (
        w.env["fix.partner.audit"]
        .with_user(w.officer)
        .create({"partner_id": partner.id, "score": score, **kw})
    )
    audit.with_user(w.officer).write({"evidence_attachment_id": _doc(w, audit, "audit.pdf").id})
    audit.with_user(w.officer).action_submit()
    if approve:
        audit.with_user(w.manager).action_approve()
    return audit


def _events(w, etype, rec):
    return (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", etype), ("aggregate_id", "=", rec.id)])
    )


# ============================================================ partner
def test_a_plain_user_reads_but_cannot_create_or_onboard(w):
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        _partner(w, user=w.clerk)
    p = _partner(w)
    assert p.with_user(w.clerk).read(["masked_phone", "masked_nid"])
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        p.with_user(w.clerk).write({"state": "onboarded"})
    with pytest.raises(UserError, match="Channel Manager"), w.env.cr.savepoint():
        p.with_user(w.clerk).action_onboard()


@pytest.mark.parametrize(
    "vals",
    [
        {"state": "onboarded"},
        {"technical_audit_score": 100.0},
        {"commission_rate": 0.5},
        {"kyc_verified": True},
        {"pdpa_erasure_state": "erased"},
    ],
)
def test_workflow_fields_cannot_be_written(w, vals):
    p = _partner(w)
    with pytest.raises(UserError, match=GUARD):
        p.with_user(w.manager).write(vals)


def test_the_audit_score_defaults_to_a_fail(w):
    p = _partner(w)
    assert p.technical_audit_score == 0.0


def test_the_mask_and_onboarding_work_without_the_pii_group(w):
    p = _partner(w)
    p.sudo().write({"nid_number": "1982736450"})
    assert p.with_user(w.clerk).masked_nid == "******6450"
    p.with_user(w.manager).action_onboard()  # no AccessError on the raw NID
    assert (p.state, p.onboarded_by_id) == ("onboarded", w.manager)
    assert len(_events(w, "partner.onboarded", p)) == 1


def test_onboarding_needs_a_second_person(w):
    own = _partner(w, user=w.manager)
    with pytest.raises(UserError, match="Segregation of duties"), w.env.cr.savepoint():
        own.with_user(w.manager).action_onboard()
    submitted = _partner(w, user=w.officer)
    w.manager.group_ids = [(4, w.env.ref("cd_partner.group_fix_channel_officer").id)]
    submitted.with_user(w.manager).action_submit_onboarding()
    with pytest.raises(UserError, match="submitted"), w.env.cr.savepoint():
        submitted.with_user(w.manager).action_onboard()
    submitted.with_user(w.manager2).action_onboard()
    assert submitted.state == "onboarded"


def test_a_franchise_onboards_on_attached_documents_verified_by_someone_else(w):
    p = _partner(w, partner_type="franchise")
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        p.with_user(w.officer).write({"has_trade_license_doc": True, "has_bank_solvency_doc": True})
    with pytest.raises(ValidationError, match="Bank Solvency|Trade License"), w.env.cr.savepoint():
        p.with_user(w.manager).action_onboard()
    p.with_user(w.officer).write(
        {
            "trade_license_attachment_id": _doc(w, p, "tl.pdf").id,
            "bank_solvency_attachment_id": _doc(w, p, "bs.pdf", user=w.kyc).id,
        }
    )
    assert p.has_trade_license_doc and p.has_bank_solvency_doc
    with pytest.raises(ValidationError, match="verified by a KYC officer"), w.env.cr.savepoint():
        p.with_user(w.manager).action_onboard()
    # the KYC officer uploaded one of the documents: another officer verifies
    with pytest.raises(UserError, match="uploaded"), w.env.cr.savepoint():
        p.with_user(w.kyc).action_verify_kyc()
    w.manager2.group_ids = [(4, w.env.ref("cd_partner.group_fix_channel_kyc_officer").id)]
    p.with_user(w.manager2).action_verify_kyc()
    p.with_user(w.manager).action_onboard()
    assert (p.state, p.kyc_verified_by_id) == ("onboarded", w.manager2)
    # a document of another record is not this partner's evidence
    other = _partner(w, partner_id=w.party_b.id)
    with pytest.raises(ValidationError, match="not attached"), w.env.cr.savepoint():
        other.with_user(w.officer).write({"trade_license_attachment_id": _doc(w, p, "x.pdf").id})


def test_a_suspended_partner_is_reinstated_by_another_manager(w):
    p = _onboarded(w)
    with pytest.raises(UserError, match="State why"), w.env.cr.savepoint():
        p.with_user(w.manager).action_suspend()
    p.with_user(w.manager).action_suspend(reason="audit failure")
    with pytest.raises(UserError, match="reinstates"), w.env.cr.savepoint():
        p.with_user(w.manager2).action_onboard()
    with pytest.raises(UserError, match="Segregation"), w.env.cr.savepoint():
        p.with_user(w.manager).action_reinstate()
    p.with_user(w.manager2).action_reinstate(reason="re-audited")
    assert p.state == "onboarded"


def test_the_commission_rate_is_a_managers_bounded_decision(w):
    p = _partner(w)
    with pytest.raises(UserError, match="Channel Manager"), w.env.cr.savepoint():
        p.with_user(w.officer).action_set_commission_rate(rate=0.1)
    with pytest.raises(UserError, match="at most 1"), w.env.cr.savepoint():
        p.with_user(w.manager).action_set_commission_rate(rate=2.5)
    p.with_user(w.manager).action_set_commission_rate(rate="0.075")
    assert p.commission_rate == 0.075


# ============================================================ technical audit
def test_the_audit_score_comes_from_an_approved_audit(w):
    p = _onboarded(w)
    draft = (
        w.env["fix.partner.audit"].with_user(w.officer).create({"partner_id": p.id, "score": 99.0})
    )
    with pytest.raises(UserError, match="Attach the audit report"), w.env.cr.savepoint():
        draft.with_user(w.officer).action_submit()
    audit = _audit(w, p, score=91.0, approve=False)
    assert p.technical_audit_score == 0.0  # submitted is not approved
    with pytest.raises(UserError, match="auditor"), w.env.cr.savepoint():
        audit.sudo().write({"auditor_id": w.manager.id})
        audit.with_user(w.manager).action_approve()
    with pytest.raises(UserError, match="the audit is submitted"), w.env.cr.savepoint():
        audit.with_user(w.officer).write({"score": 100.0})
    audit.with_user(w.manager).action_approve()
    p.invalidate_recordset()
    assert (p.technical_audit_score, p.technical_audit_id) == (91.0, audit)
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        _audit(w, p, score=140.0)
    old = _audit(w, _onboarded(w, partner_id=w.party_b.id), score=95.0)
    old.sudo().write({"audit_date": w.today - timedelta(days=400)})
    old.partner_id.invalidate_recordset()
    assert old.partner_id.technical_audit_score == 0.0  # expired


# ============================================================ rebates
def _rebate(w, partner, **kw):
    vals = {
        "name": "A4PA rebate",
        "partner_id": partner.id,
        "period": "2026-Q4",
        "basis": 100000.0,
        "rate": 0.03,
    }
    vals.update(kw)
    return w.env["fix.partner.rebate"].with_user(w.officer).create(vals)


def test_a_rebate_rate_is_bounded_and_the_partner_onboarded(w):
    with pytest.raises(ValidationError, match="between 0 and 20"), w.env.cr.savepoint():
        _rebate(w, _onboarded(w), rate=2.5)
    prospect = _partner(w, partner_id=w.party_b.id)
    r = _rebate(w, prospect)
    with pytest.raises(ValidationError, match="onboarded"), w.env.cr.savepoint():
        r.with_user(w.officer).action_accrue()


def test_a_rebate_cannot_be_written_paid_or_raised(w):
    r = _rebate(w, _onboarded(w))
    for vals in ({"state": "paid"}, {"amount": 5000000.0}):
        with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
            r.with_user(w.officer).write(vals)
    with pytest.raises(UserError, match="inbox"), w.env.cr.savepoint():
        r.with_user(w.approver).action_approve_payout()
    r.with_user(w.officer).action_accrue()
    with pytest.raises(UserError, match="pinned"), w.env.cr.savepoint():
        r.with_user(w.officer).write({"basis": 10000000.0, "rate": 0.2})


def test_the_payout_is_a_routed_dofa_approval_behind_a_real_audit(w):
    p = _onboarded(w)
    r = _rebate(w, p)
    r.with_user(w.officer).action_accrue()
    r.with_user(w.officer).write({"dofa_justification": "Q4 volume met"})
    # no approved audit: the gate holds, and a context key does not open it
    r.with_user(w.officer).action_request_approval(justification="Q4 volume met")
    task = r.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == w.approver
    )
    assert task, "routed to the rebate approver holding Tier 2"
    assert w.officer not in r.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    with pytest.raises(ValidationError, match="technical audit score is 0.0"), w.env.cr.savepoint():
        task.with_user(w.approver).with_context(skip_audit_score_check=True).action_approve()
    _audit(w, p, score=88.0)
    task.with_user(w.approver).action_approve()
    r.invalidate_recordset()
    assert (r.state, r.dofa_approved_by, r.dofa_approved_amount) == ("approved", w.approver, 3000.0)
    assert r.audit_id.score == 88.0
    [instruction] = _events(w, "partner.rebate_approved", r)
    assert '"amount": 3000.0' in instruction.payload
    # paid only by finance, with the payout reference
    with pytest.raises(UserError, match="finance"), w.env.cr.savepoint():
        r.with_user(w.approver).action_record_payout(payment_ref="PAY-1")
    with pytest.raises(UserError, match="reference"), w.env.cr.savepoint():
        r.with_user(w.finance).action_record_payout()
    r.with_user(w.finance).action_record_payout(payment_ref="AP/2026/0001")
    assert (r.state, r.paid_ref, r.paid_by_id) == ("paid", "AP/2026/0001", w.finance)
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        r.with_user(w.officer).write({"basis": 10000000.0})


def test_a_failed_audit_blocks_the_payout(w):
    p = _onboarded(w)
    _audit(w, p, score=40.0)
    r = _rebate(w, p)
    r.with_user(w.officer).action_accrue()
    with pytest.raises(ValidationError, match="40.0"):
        approve_via_inbox(r, w.approver, requester=w.officer, justification="x")


# ============================================================ deals
def _deal(w, partner, customer=None, user=None, **kw):
    return (
        w.env["fix.partner.deal"]
        .with_user(user or w.officer)
        .create(
            {
                "name": "DR-%s" % partner.id,
                "partner_id": partner.id,
                "customer_id": (customer or w.customer).id,
                "value": 250000.0,
                "registered_on": w.today,
                **kw,
            }
        )
    )


def test_a_deal_is_approved_by_a_manager_and_protected_for_90_days(w):
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        _deal(w, _onboarded(w), state="won")
    prospect = _partner(w, partner_id=w.party_b.id)
    with pytest.raises(ValidationError, match="onboarded"), w.env.cr.savepoint():
        _deal(w, prospect).with_user(w.manager).action_approve()
    d = _deal(w, _onboarded(w))
    with pytest.raises(UserError, match="Segregation"), w.env.cr.savepoint():
        _deal(w, d.partner_id, user=w.manager).with_user(w.manager).action_approve()
    d.with_user(w.manager).action_approve()
    assert (d.state, d.protected_until) == ("approved", w.today + timedelta(days=90))
    with pytest.raises(UserError, match="the deal is approved"), w.env.cr.savepoint():
        d.with_user(w.officer).write({"customer_id": w.party.id})
    d.with_user(w.officer).action_mark_won()
    assert d.state == "won"


def test_a_clash_raises_a_conflict_and_the_ruling_decides(w):
    a = _onboarded(w)
    b = _onboarded(w, partner_id=w.party_b.id, name="A4PA Partner B")
    first = _deal(w, a)
    first.with_user(w.manager).action_approve()
    second = _deal(w, b)
    res = second.with_user(w.manager).action_approve()
    assert second.state == "conflict" and res["conflict"]
    conflict = second.conflict_id
    assert (conflict.partner_a_id, conflict.partner_b_id) == (a, b)
    with pytest.raises(UserError, match="waits for the Tier 3 ruling"), w.env.cr.savepoint():
        second.with_user(w.manager).action_approve()
    conflict.with_user(w.dir3b).action_rule_partner_b(notes="B registered the opportunity first")
    second.with_user(w.manager).action_approve()
    assert (second.state, first.state) == ("approved", "declined")


def test_the_deal_job_warns_then_expires(w):
    d = _deal(w, _onboarded(w))
    d.with_user(w.manager).action_approve()
    d.sudo()._guarded().write({"protected_until": w.today + timedelta(days=10)})
    Deal = w.env["fix.partner.deal"]
    Deal.cron_deal_expiry()
    Deal.cron_deal_expiry()
    assert len(_events(w, "partner.deal_expiring", d)) == 1
    d.sudo()._guarded().write({"protected_until": w.today - timedelta(days=1)})
    Deal.cron_deal_expiry()
    assert d.state == "expired"


# ============================================================ authorisations
def test_an_authorisation_is_activated_on_a_certificate_and_lapses(w):
    p = _onboarded(w)
    Auth = w.env["fix.partner.authorisation"].with_user(w.officer)
    with pytest.raises(ValidationError, match="before it starts"), w.env.cr.savepoint():
        Auth.create(
            {
                "name": "x",
                "partner_id": p.id,
                "valid_from": w.today,
                "valid_to": w.today - timedelta(days=400),
            }
        )
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        Auth.create(
            {
                "name": "x",
                "partner_id": p.id,
                "valid_from": w.today,
                "valid_to": w.today,
                "state": "active",
            }
        )
    a = Auth.create(
        {
            "name": "Samsung ASC",
            "partner_id": p.id,
            "valid_from": w.today,
            "valid_to": w.today + timedelta(days=20),
        }
    )
    with pytest.raises(ValidationError, match="certificate"), w.env.cr.savepoint():
        a.with_user(w.manager).action_activate()
    a.with_user(w.officer).write(
        {"certificate_ref": "SAMSUNG-ASC-1", "certificate_attachment_id": _doc(w, a, "cert.pdf").id}
    )
    a.with_user(w.manager).action_activate()
    assert a.state == "active"
    with pytest.raises(UserError, match="is active"), w.env.cr.savepoint():
        a.with_user(w.officer).write({"certificate_ref": "FORGED"})
    Auth = w.env["fix.partner.authorisation"]
    Auth.cron_authorisation_expiry()
    assert len(_events(w, "partner.authorisation_expiring", a)) == 1
    a.sudo()._guarded().write(
        {"valid_from": w.today - timedelta(days=30), "valid_to": w.today - timedelta(days=1)}
    )
    Auth.cron_authorisation_expiry()
    assert a.state == "expired"


def test_a_prospects_authorisation_cannot_be_activated(w):
    a = (
        w.env["fix.partner.authorisation"]
        .with_user(w.officer)
        .create(
            {"name": "x", "partner_id": _partner(w).id, "valid_from": w.today, "valid_to": w.today}
        )
    )
    with pytest.raises(ValidationError, match="onboarded"):
        a.with_user(w.manager).action_activate()


# ============================================================ franchise
def test_a_franchise_activates_on_a_verified_partner_and_bills_its_fee(w):
    p = _partner(w, partner_type="franchise")
    Fr = w.env["fix.partner.franchise"].with_user(w.officer)
    with pytest.raises(ValidationError, match="before it starts"), w.env.cr.savepoint():
        Fr.create(
            {
                "name": "F",
                "partner_id": p.id,
                "territory": "Khulna",
                "fee": 750000.0,
                "start_date": w.today,
                "end_date": w.today - timedelta(days=30),
            }
        )
    f = Fr.create(
        {
            "name": "F",
            "partner_id": p.id,
            "territory": "Sylhet",
            "fee": 500000.0,
            "start_date": w.today,
        }
    )
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        f.with_user(w.officer).write({"state": "active"})
    with pytest.raises(ValidationError, match="onboarded"), w.env.cr.savepoint():
        f.with_user(w.manager).action_activate()
    p.with_user(w.officer).write(
        {
            "trade_license_attachment_id": _doc(w, p, "tl.pdf").id,
            "bank_solvency_attachment_id": _doc(w, p, "bs.pdf").id,
        }
    )
    p.with_user(w.kyc).action_verify_kyc()
    p.with_user(w.manager).action_onboard()
    f.with_user(w.manager).action_activate()
    assert f.state == "active"
    [event] = _events(w, "partner.franchise_activated", f)
    assert '"fee": 500000.0' in event.payload
    with pytest.raises(UserError, match="is active"), w.env.cr.savepoint():
        f.with_user(w.officer).write({"fee": 1.0})


# ============================================================ conflicts
def _conflict(w):
    a = _onboarded(w)
    b = _onboarded(w, partner_id=w.party_b.id, name="A4PA Partner B")
    return (
        w.env["fix.partner.conflict"]
        .with_user(w.officer)
        .create(
            {
                "name": "A4PA CFL",
                "partner_a_id": a.id,
                "partner_b_id": b.id,
                "customer_id": w.customer.id,
                "description": "both chase the same AMC",
            }
        )
    )


def test_a_ruling_cannot_be_forged_or_changed(w):
    k = _conflict(w)
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        k.with_user(w.officer).write(
            {
                "state": "mediated",
                "dofa_decision": "partner_a",
                "dofa_arbitrator_id": w.dir3b.id,
                "arbitrated_at": fields.Datetime.now(),
            }
        )
    with pytest.raises(UserError, match="still OPEN"), w.env.cr.savepoint():
        k.with_user(w.officer).action_close()
    with pytest.raises(UserError, match="Tier 3"), w.env.cr.savepoint():
        k.with_user(w.manager).action_rule_partner_a(notes="x")
    k.with_user(w.dir3b).action_rule_partner_a(notes="A had first contact")
    assert (k.state, k.dofa_arbitrator_id) == ("mediated", w.dir3b)
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        k.with_user(w.officer).write({"dofa_decision": "partner_b"})
    with pytest.raises(UserError, match="already mediated"), w.env.cr.savepoint():
        k.with_user(w.dir3).action_mediate("partner_b", notes="second thoughts")
    k.with_user(w.officer).action_close()
    assert (k.state, k.dofa_decision) == ("closed", "partner_a")


# ============================================================ PDPA
def test_erasure_is_requested_then_executed_by_another_tier3(w):
    p = _partner(w)
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        p.with_user(w.officer).write({"pdpa_erasure_state": "erased"})
    p.with_user(w.dir3).action_request_erasure()
    with pytest.raises(UserError, match="Segregation"), w.env.cr.savepoint():
        p.with_user(w.dir3).action_execute_erasure()
    with pytest.raises(UserError, match="Tier 3"), w.env.cr.savepoint():
        p.with_user(w.officer2).action_execute_erasure()
    p.with_user(w.dir3b).action_execute_erasure()
    p.invalidate_recordset()
    w.party.invalidate_recordset()
    assert p.sudo().pdpa_erasure_state == "erased" and not p.sudo().tin_number
    assert not (w.party.phone or w.party.street or w.party.city)
    assert w.party.name.startswith("Erased party")
    with pytest.raises(UserError, match="already been anonymised"), w.env.cr.savepoint():
        p.with_user(w.officer).action_request_erasure()


def test_a_retention_block_is_kept(w):
    p = _partner(w)
    p.with_user(w.officer).action_request_erasure()
    blocker = "service order SO/1 is still open"
    with (
        mock.patch.object(type(p), "_erasure_blocker", return_value=blocker),
        w.env.cr.savepoint(),
    ):
        res = p.with_user(w.dir3b).action_execute_erasure()
    p.invalidate_recordset()
    assert p.pdpa_erasure_state == "blocked" and "SO/1" in res["message"]
    assert p.pdpa_blocked_reason == "service order SO/1 is still open"


# ============================================================ crons
@pytest.mark.parametrize(
    ("xmlid", "method"),
    [
        ("cd_partner.ir_cron_partner_authorisation_expiry", "cron_authorisation_expiry"),
        ("cd_partner.ir_cron_partner_deal_expiry", "cron_deal_expiry"),
    ],
)
def test_the_partner_jobs_are_scheduled(w, xmlid, method):
    cron = w.env.ref(xmlid)
    assert cron.active and method in cron.code


# ============================================================ the workspace
@pytest.fixture
def p03(w):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()

    def raw(fn):
        return getattr(fn, "original_endpoint", fn)

    def call(user):
        def run(fn, **kw):
            old = getattr(g, "request", None)
            g.request = types.SimpleNamespace(env=w.env(user=user.id))
            try:
                return fn(ctl, **kw)
            finally:
                g.request = old

        return types.SimpleNamespace(
            write=lambda **kw: run(raw(g.P03GenericApiController.model_write), **kw),
            action=lambda **kw: run(raw(g.P03GenericApiController.model_action), **kw),
        )

    return call


def test_the_workspace_refuses_forged_states_and_runs_the_lifecycle(w, p03):
    p = _partner(w)
    res = p03(w.officer).write(
        model="fix.partner",
        record_id=p.id,
        values={"state": "onboarded", "technical_audit_score": 100},
    )
    assert res.get("error") and p.state == "prospective"
    res = p03(w.officer).action(model="fix.partner", ids=[p.id], method="action_onboard", kwargs={})
    assert not res["success"] and "Channel Manager" in res["error"]
    res = p03(w.manager).action(model="fix.partner", ids=[p.id], method="action_onboard", kwargs={})
    assert res["success"], res
    r = _rebate(w, p)
    res = p03(w.officer).write(model="fix.partner.rebate", record_id=r.id, values={"state": "paid"})
    assert res.get("error") and r.state == "draft"
    res = p03(w.officer).action(
        model="fix.partner.rebate", ids=[r.id], method="action_approve_payout", kwargs={}
    )
    assert "not available" in res["error"]  # the payout is approved from the inbox
