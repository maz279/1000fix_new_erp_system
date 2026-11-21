"""A04 ERP audit (20 Nov 2026), stream B5: M40 money and control findings.

Every test runs the rule as the non-admin user it governs and is built so
that only the rule under test can refuse it (mutation-checked: the report
lists the defect re-introduced for each). Business set-up the test does not
prove (programme, agreement, checklist, approved rate, paid invoices) is
prepared as the system through m40_fixtures."""

import base64
import threading
import types
from datetime import timedelta
from unittest import mock

import psycopg2.errors
import pytest
from odoo import fields
from odoo.addons.cd_partner.controllers import partner_api
from odoo.addons.cd_partner.tests.m40_fixtures import (
    CONSENT,
    PAYOUT_PARAMS,
    approved_rate,
    configure_payout_accounts,
    ensure_account,
    guarded_write,
    make_onboardable,
    paid_invoice,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
PA = "cd_partner.group_fix_channel_"
TIER = "cd_entity_config.group_dofa_tier_%d"


def _mk(env, login, *xmlids, share=False, party=None):
    groups = [] if share else [env.ref("base.group_user").id]
    vals = {
        "name": login,
        "login": login,
        "group_ids": [(6, 0, groups + [env.ref(x).id for x in xmlids])],
    }
    if party:
        vals["partner_id"] = party.id
    return env["res.users"].with_context(no_reset_password=True).create(vals)


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.clerk = _mk(env, "b5_clerk")
    x.officer = _mk(env, "b5_officer", PA + "officer")
    x.kyc = _mk(env, "b5_kyc", PA + "kyc_officer")
    x.manager = _mk(env, "b5_manager", PA + "manager")
    x.manager2 = _mk(env, "b5_manager2", PA + "manager")
    x.cco = _mk(env, "b5_cco", TIER % 2, TIER % 3)
    x.approver = _mk(
        env, "b5_approver", "cd_partner.group_fix_rebate_approver", TIER % 2, TIER % 3, TIER % 4
    )
    x.finance = _mk(env, "b5_finance", "account.group_account_invoice")
    x.accountant = _mk(env, "b5_accountant", "account.group_account_user")
    x.refmgr = _mk(env, "b5_refmgr", "cd_partner.group_fix_referral_manager")
    x.today = fields.Date.context_today(env.user)
    x.company = env.company
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    params = env["ir.config_parameter"].sudo()
    for key in PAYOUT_PARAMS:
        params.set_param(key, False)
    params.set_param("cd_partner.lead_attribution_days", False)
    params.set_param("cd_partner.dormancy_days", False)
    return x


def _party(w, name):
    return w.env["res.partner"].create({"name": name})


def _doc(w, record, user=None):
    return (
        w.env["ir.attachment"]
        .with_user(user or w.officer)
        .create(
            {
                "name": "doc.pdf",
                "res_model": record._name,
                "res_id": record.id,
                "datas": base64.b64encode(b"%PDF-1.4 b5"),
            }
        )
    )


def _partner(w, ptype="referral", onboard=True, **kw):
    w.n += 1
    vals = {
        "name": "B5 %s %d" % (ptype, w.n),
        "partner_id": _party(w, "B5 party %d" % w.n).id,
        "partner_type": ptype,
        "tin_number": "123456789012",
        "trade_license_no": "TL-B5-%d" % w.n,
    }
    vals.update(kw)
    p = w.env["fix.partner"].with_user(w.officer).create(vals)
    if ptype == "franchise":
        p.with_user(w.officer).write(
            {
                "trade_license_attachment_id": _doc(w, p).id,
                "bank_solvency_attachment_id": _doc(w, p).id,
            }
        )
        p.with_user(w.kyc).action_verify_kyc()
    if onboard:
        make_onboardable(w.env, p)
        p.with_user(w.manager).action_onboard()
    return p


def _scheme(w, tds=0.10, rate=0.0, ptype="reseller"):
    """A scheme for one partner type (the database may already hold the
    generic one; a type-specific line does not overlap it)."""
    return (
        w.env["fix.commission.scheme"]
        .sudo()
        .create(
            {
                "name": "B5 partner scheme",
                "scheme_type": "partner",
                "partner_type": ptype,
                "commission_rate": rate,
                "tds_rate": tds,
                "date_from": w.today - timedelta(days=30),
                "company_id": w.company.id,
            }
        )
    )


def _relay(w, etype, rec):
    """The relay's delivery of the event the action published."""
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", etype), ("aggregate_id", "=", rec.id)], order="id desc", limit=1
        )
    )
    assert event, "%s was published" % etype
    sub = w.env["fix.event.consumer"].sudo().search([("event_type", "=", etype)], limit=1)
    assert sub, "%s has a consumer" % etype
    return getattr(w.env[sub.model].sudo(), sub.method)(event._relay_event_dict())


def _lines(move):
    return sorted(
        (ln.account_id.code, round(ln.debit, 2), round(ln.credit, 2)) for ln in move.line_ids
    )


# =================================================================== P0
def _active_franchise(w, fee=750000.0, **kw):
    p = _partner(w, "franchise")
    f = (
        w.env["fix.partner.franchise"]
        .with_user(w.officer)
        .create(
            {
                "name": "B5 Franchise %d" % w.n,
                "partner_id": p.id,
                "territory": "Gazipur",
                "fee": fee,
                "start_date": w.today - timedelta(days=60),
                **kw,
            }
        )
    )
    return p, f


def test_f2_the_initial_fee_is_invoiced_at_activation(w):
    p, f = _active_franchise(w)
    # fail closed: no income account configured, no activation
    with pytest.raises(UserError, match="franchise_fee_income"), w.env.cr.savepoint():
        f.with_user(w.manager).action_activate()
    configure_payout_accounts(w.env)
    f.with_user(w.manager).action_activate()
    inv = f.fee_invoice_id.sudo()
    assert inv and inv.state == "draft"
    assert inv.customer_id == p.partner_id
    assert inv.taxable_amount == 750000.0
    assert round(inv.vat_amount, 2) == round(750000.0 * 0.15, 2)  # M51 standard rate
    assert inv.revenue_account_id.code == "400109"
    assert (inv.source_model, inv.source_ref) == (
        "fix.partner.franchise",
        "fix.partner.franchise/%s/initial-fee" % f.id,
    )


def _royalty_case(w):
    configure_payout_accounts(w.env)
    p, f = _active_franchise(w, fee=0.0, operating_unit_id=w.ou.id)
    guarded_write(f, {"royalty_rate": 0.06, "marketing_levy_rate": 0.02})
    f.with_user(w.manager).action_activate()
    start = w.today - timedelta(days=40)
    end = w.today - timedelta(days=10)
    customer = _party(w, "B5 franchise customer")
    inside = paid_invoice(w.env, customer, 100000.0, start + timedelta(days=5), ou=w.ou)
    paid_invoice(w.env, customer, 50000.0, end + timedelta(days=3), ou=w.ou)  # after period
    roy = (
        w.env["fix.franchise.royalty"]
        .with_user(w.officer)
        .create({"franchise_id": f.id, "period_from": start, "period_to": end})
    )
    return p, f, roy, inside


def test_f1_f19_the_royalty_is_an_m20_invoice_on_ex_vat_revenue(w):
    p, f, roy, inside = _royalty_case(w)
    roy.with_user(w.officer).action_compute()
    # ex-VAT (taxable) revenue of the period, not VAT-inclusive cash
    assert roy.revenue_basis == 100000.0 == inside.taxable_amount
    assert (roy.royalty_amount, roy.levy_amount) == (6000.0, 2000.0)
    # a typed reference no longer stands for an invoice
    assert not hasattr(type(roy), "action_record_invoice")
    with pytest.raises(UserError, match="finance"), w.env.cr.savepoint():
        roy.with_user(w.officer).action_raise_invoice()
    roy.with_user(w.finance).action_raise_invoice()
    inv = roy.invoice_id.sudo()
    assert roy.state == "invoiced" and inv.state == "draft"
    assert inv.customer_id == p.partner_id
    assert sorted(inv.line_ids.mapped("taxable_amount")) == [2000.0, 6000.0]
    assert inv.vat_amount == 1200.0  # VAT by M51 on royalty + levy
    assert inv.revenue_account_id.code == "400109"


def test_f19_credit_notes_are_netted_from_the_royalty_basis(w):
    p, f, roy, inside = _royalty_case(w)
    reason = w.env["fix.credit.note"]._fields["reason_code"].selection[0][0]
    note = (
        w.env["fix.credit.note"]
        .sudo()
        .create(
            {
                "invoice_id": inside.id,
                "company_id": inside.company_id.id,
                "operating_unit_id": inside.operating_unit_id.id,
                "amount": 11500.0,  # VAT-inclusive: 10,000 ex-VAT
                "reason_code": reason,
            }
        )
    )
    guarded_write(
        note, {"state": "issued", "issued_at": fields.Datetime.now() - timedelta(days=20)}
    )
    roy.with_user(w.officer).action_compute()
    assert roy.credited_basis == 10000.0
    assert roy.revenue_basis == 90000.0


def test_f1_the_royalty_invoice_is_refused_without_its_income_account(w):
    p, f, roy, inside = _royalty_case(w)
    roy.with_user(w.officer).action_compute()
    w.env["ir.config_parameter"].sudo().set_param("cd_partner.account_code.royalty_income", False)
    with pytest.raises(UserError, match="royalty_income"):
        roy.with_user(w.finance).action_raise_invoice()


def _mdf_claim(w):
    p = _partner(w, "reseller")
    fund = (
        w.env["fix.mdf.fund"]
        .with_user(w.officer)
        .create({"name": "B5 MDF", "partner_id": p.id, "period": "2026-Q4", "allocated": 200000.0})
    )
    fund.with_user(w.manager).action_open()
    claim = (
        w.env["fix.mdf.claim"]
        .with_user(w.officer)
        .create({"fund_id": fund.id, "amount": 120000.0, "description": "Dhaka fair stall"})
    )
    claim.with_user(w.officer).write({"evidence_attachment_id": _doc(w, claim).id})
    claim.with_user(w.officer).action_submit()
    return p, claim


def test_f3_an_mdf_claim_accrues_and_pays_through_m50(w):
    p, claim = _mdf_claim(w)
    with pytest.raises(UserError, match="partner_mdf_expense"), w.env.cr.savepoint():
        claim.with_user(w.manager2).action_approve()
    configure_payout_accounts(w.env)
    _scheme(w, tds=0.10, ptype="reseller")
    claim.with_user(w.manager2).action_approve()
    result = _relay(w, "partner.mdf_claim_approved", claim)
    pay = w.env["fix.payment.execution"].sudo().browse(result["id"])
    move = w.env["account.move"].sudo().browse(result["move_id"])
    tds = round(12000.0 * 1.5, 2)  # 10% TDS, non-filer uplift 50%
    assert _lines(move) == sorted(
        [("500210", 120000.0, 0.0), ("200202", 0.0, 120000.0 - tds), ("200905", 0.0, tds)]
    )
    assert (pay.state, pay.amount, pay.debit_account_id.code) == (
        "pending",
        120000.0 - tds,
        "200202",
    )
    assert pay.partner_id == p.partner_id
    # a replay raises nothing twice
    assert _relay(w, "partner.mdf_claim_approved", claim)["created"] is False
    # paid only when the instruction is executed, not on a typed reference
    with pytest.raises(UserError, match="pending"), w.env.cr.savepoint():
        claim.with_user(w.finance).action_record_payment()
    guarded_write(pay, {"state": "executed", "bank_reference": "BEFTN-77"})
    claim.with_user(w.finance).action_record_payment()
    assert (claim.state, claim.payment_ref) == ("paid", "BEFTN-77")


# =================================================================== rebates
def _rebate(w, p, **kw):
    vals = {
        "name": "B5 rebate",
        "partner_id": p.id,
        "period": "2026-Q3",
        "period_from": w.today - timedelta(days=90),
        "period_to": w.today - timedelta(days=1),
        "rate": 0.03,
    }
    vals.update(kw)
    return w.env["fix.partner.rebate"].with_user(w.officer).create(vals)


def test_f12_the_rebate_basis_is_the_partners_paid_invoices(w):
    p = _partner(w, "reseller")
    paid_invoice(w.env, p.partner_id, 100000.0, w.today - timedelta(days=30))
    paid_invoice(w.env, p.partner_id, 70000.0, w.today - timedelta(days=200))  # outside
    paid_invoice(w.env, _party(w, "someone else"), 90000.0, w.today - timedelta(days=30))
    with pytest.raises(UserError), w.env.cr.savepoint():
        _rebate(w, p, basis=9999999.0)
    r = _rebate(w, p)
    with pytest.raises(UserError), w.env.cr.savepoint():
        r.with_user(w.officer).write({"basis": 9999999.0})
    r.with_user(w.officer).action_accrue()
    assert (r.basis, r.basis_invoice_count, r.amount) == (100000.0, 1, 3000.0)


def test_f13_an_approved_rebate_accrues_with_tds_fail_closed(w):
    p = _partner(w, "reseller")
    paid_invoice(w.env, p.partner_id, 100000.0, w.today - timedelta(days=30))
    audit = (
        w.env["fix.partner.audit"].with_user(w.officer).create({"partner_id": p.id, "score": 90})
    )
    audit.with_user(w.officer).write({"evidence_attachment_id": _doc(w, audit).id})
    audit.with_user(w.officer).action_submit()
    audit.with_user(w.manager).action_approve()
    r = _rebate(w, p)
    r.with_user(w.officer).action_accrue()
    r.with_user(w.officer).action_request_approval(justification="Q3 volume")
    with pytest.raises(UserError, match="partner_rebate_payout"), w.env.cr.savepoint():
        approve_via_inbox(r, w.approver, requester=w.officer, justification="Q3 volume")
    configure_payout_accounts(w.env)
    _scheme(w, tds=0.10)
    approve_via_inbox(r, w.approver, requester=w.officer, justification="Q3 volume")
    result = _relay(w, "partner.rebate_approved", r)
    move = w.env["account.move"].sudo().browse(result["move_id"])
    pay = w.env["fix.payment.execution"].sudo().browse(result["id"])
    assert _lines(move) == sorted(
        [("500306", 3000.0, 0.0), ("200202", 0.0, 2550.0), ("200905", 0.0, 450.0)]
    )
    assert (pay.amount, pay.debit_account_id.code) == (2550.0, "200202")
    with pytest.raises(UserError, match="pending"), w.env.cr.savepoint():
        r.with_user(w.finance).action_record_payout(payment_ref="TYPED-1")
    guarded_write(pay, {"state": "executed", "bank_reference": "BEFTN-9"})
    r.with_user(w.finance).action_record_payout()
    assert (r.state, r.paid_ref) == ("paid", "BEFTN-9")


# =================================================================== referrals
def _referral(w, p, customer, user=None, **kw):
    vals = {"name": "B5 ref", "partner_id": p.id, "referred_partner_id": customer.id, **CONSENT}
    vals.update(kw)
    return w.env["fix.referral"].with_user(user or w.officer).create(vals)


def test_f4_f18_attribution_is_frozen_and_base_users_only_read(w):
    p = _partner(w)
    q = _partner(w)
    customer = _party(w, "B5 referred")
    with pytest.raises(AccessError), w.env.cr.savepoint():
        _referral(w, p, customer, user=w.clerk)
    ref = _referral(w, p, customer)
    with pytest.raises(AccessError), w.env.cr.savepoint():
        ref.with_user(w.clerk).write({"name": "renamed"})
    for vals in ({"partner_id": q.id}, {"referred_partner_id": _party(w, "other").id}):
        with pytest.raises(UserError, match="attribution is fixed"), w.env.cr.savepoint():
            ref.with_user(w.officer).write(vals)
    assert ref.partner_id == p


def test_f9_f10_only_a_partner_in_good_standing_refers_on_consent(w):
    customer = _party(w, "B5 referred")
    prospect = _partner(w, onboard=False)
    with pytest.raises(ValidationError, match="only an onboarded partner"), w.env.cr.savepoint():
        _referral(w, prospect, customer)
    p = _partner(w)
    with pytest.raises(ValidationError, match="consent"), w.env.cr.savepoint():
        _referral(w, p, customer, consent_given=False)
    ref = _referral(w, p, customer)
    assert ref.consent_at and ref.referred_on == w.today


def test_f17_a_child_contact_of_a_referred_customer_is_that_customer(w):
    p = _partner(w)
    q = _partner(w)
    company = w.env["res.partner"].create({"name": "B5 Corp", "is_company": True})
    child = w.env["res.partner"].create({"name": "B5 Corp buyer", "parent_id": company.id})
    _referral(w, p, company)
    with pytest.raises(UserError, match="open referral"), w.env.cr.savepoint():
        _referral(w, q, child)
    with pytest.raises(UserError, match="refer themselves"), w.env.cr.savepoint():
        own_child = w.env["res.partner"].create({"name": "self", "parent_id": p.partner_id.id})
        _referral(w, p, own_child)


def _converted(w, p, customer, inv_date):
    ref = _referral(w, p, customer)
    inv = paid_invoice(w.env, customer, 20000.0, inv_date)
    ref.with_user(w.refmgr).action_convert(invoice=inv)
    return ref, inv


def test_f7_only_revenue_inside_the_attribution_window_converts(w):
    p = _partner(w)
    customer = _party(w, "B5 window")
    ref = _referral(w, p, customer)
    before = paid_invoice(w.env, customer, 20000.0, w.today - timedelta(days=400))
    with pytest.raises(UserError, match="attribution window"), w.env.cr.savepoint():
        ref.with_user(w.refmgr).action_convert(invoice=before)
    guarded_write(ref, {"referred_on": w.today - timedelta(days=200)})
    late = paid_invoice(w.env, customer, 20000.0, w.today)
    with pytest.raises(UserError, match="90 days"), w.env.cr.savepoint():
        ref.with_user(w.refmgr).action_convert(invoice=late)
    w.env["ir.config_parameter"].sudo().set_param("cd_partner.lead_attribution_days", "365")
    ref.with_user(w.refmgr).action_convert(invoice=late)
    assert ref.state == "converted" and ref.base_amount == 20000.0


def test_f6_m53_accrues_at_the_rate_the_referral_earned(w):
    configure_payout_accounts(w.env)
    params = w.env["ir.config_parameter"].sudo()
    ensure_account(w.env, "500306")
    params.set_param("cd_settlement_ext.account_code.partner_commission_expense", "500306")
    p = _partner(w)
    approved_rate(p, 0.5)
    _scheme(w, tds=0.10, rate=0.03, ptype="referral")  # a scheme rate that used to override
    ref, inv = _converted(w, p, _party(w, "B5 rated"), w.today)
    ref.with_user(w.refmgr).action_earn_commission()
    assert (ref.commission_rate, ref.commission_amount) == (0.5, 10000.0)
    approved_rate(p, 0.2)  # a later rate change does not reach this referral
    ref.with_user(w.accountant).action_accrue_commission()
    ledger = ref.commission_ledger_id.sudo()
    assert (ledger.commission_rate, ledger.commission_amount) == (0.5, 10000.0)
    assert ("500306", 10000.0, 0.0) in _lines(ledger.gl_move_id)


def test_f9_a_suspended_partner_loses_the_portal_and_earns_nothing(w):
    p = _partner(w)
    approved_rate(p, 0.05)
    contact = w.env["res.partner"].create(
        {"name": "B5 portal contact", "parent_id": p.partner_id.id}
    )
    portal = _mk(
        w.env, "b5_portal", "cd_partner.group_fix_partner_portal", share=True, party=contact
    )
    ref, inv = _converted(w, p, _party(w, "B5 susp"), w.today)
    p.with_user(w.manager).action_suspend(reason="breach")
    group = w.env.ref("cd_partner.group_fix_partner_portal")
    assert portal not in group.sudo().all_user_ids
    with pytest.raises(ValidationError, match="suspended"), w.env.cr.savepoint():
        ref.with_user(w.refmgr).action_earn_commission()
    p.with_user(w.manager2).action_reinstate(reason="cured")
    assert portal in group.sudo().all_user_ids
    ref.with_user(w.refmgr).action_earn_commission()
    assert ref.state == "commissioned"


def _call_portal(w, user, **kw):
    req = types.SimpleNamespace(env=w.env(user=user))
    with mock.patch.object(partner_api, "request", req):
        return partner_api.PartnerApiController().referrals(**kw)


def test_f8_the_portal_submits_a_lead_and_never_echoes_a_party(w):
    p = _partner(w)
    portal = _mk(
        w.env, "b5_portal2", "cd_partner.group_fix_partner_portal", share=True, party=p.partner_id
    )
    existing = _party(w, "B5 Secret Customer Name")
    out = _call_portal(w, portal, referred_name="x", referred_partner_id=existing.id)
    assert out["error"]["code"] == "referred_party_not_accepted"
    assert "Secret" not in str(out)
    out = _call_portal(w, portal, referred_name="Rahim", referred_phone="01711000000")
    assert out["error"]["code"] == "missing_consent"
    out = _call_portal(
        w,
        portal,
        referred_name="Rahim",
        referred_phone="01711000000",
        consent_given=True,
        consent_method="digital",
    )
    lead = w.env["fix.partner.lead"].sudo().search([("name", "=", out["lead"]["name"])])
    assert lead.partner_id == p and lead.customer_name == "Rahim" and lead.consent_given
    # the portal cannot create a referral itself (ACL)
    with pytest.raises(AccessError):
        w.env["fix.referral"].with_user(portal).check_access("create")


# =================================================================== F5 rate
def test_f5_a_commission_rate_is_a_routed_tier3_decision(w):
    p = _partner(w)
    assert p.commission_rate == 0.0  # no hard-coded 5%
    res = p.with_user(w.manager).action_set_commission_rate(rate=1.0)
    change = w.env["fix.partner.rate.change"].browse(res["res_ids"])
    assert p.commission_rate == 0.0 and change.approval_state == "pending"
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        change.with_user(w.manager).action_apply()
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        p.with_user(w.manager).write({"commission_rate": 1.0})
    approve_via_inbox(change, w.cco, requester=w.manager)
    p.invalidate_recordset()
    assert (p.commission_rate, change.state) == (1.0, "applied")


# =================================================================== F11/F24/F30
def test_f11_onboarding_needs_programme_agreement_and_checklist(w):
    p = _partner(w, onboard=False)
    with pytest.raises(ValidationError, match="programme"), w.env.cr.savepoint():
        p.with_user(w.manager).action_onboard()
    from odoo.addons.cd_partner.tests.m40_fixtures import agreement, published_programme

    guarded_write(p, {"programme_id": published_programme(w.env, "referral").id})
    with pytest.raises(ValidationError, match="agreement"), w.env.cr.savepoint():
        p.with_user(w.manager).action_onboard()
    guarded_write(p, {"contract_id": agreement(w.env, p.partner_id).id})
    with pytest.raises(ValidationError, match="checklist"), w.env.cr.savepoint():
        p.with_user(w.manager).action_onboard()
    make_onboardable(w.env, p)
    p.with_user(w.manager).action_onboard()
    assert p.state == "onboarded"


def test_f24_standings_and_an_exit_waits_for_settlement(w):
    p = _partner(w, "reseller")
    p.with_user(w.manager).action_probation(reason="SLA miss plan")
    assert p.state == "probation"
    p.with_user(w.manager).action_end_probation()
    paid_invoice(w.env, p.partner_id, 100000.0, w.today - timedelta(days=30))
    r = _rebate(w, p)
    r.with_user(w.officer).action_accrue()
    exiter = _mk(w.env, "b5_exiter", TIER % 3)
    p.with_user(exiter).action_start_exit(reason="non-renewal")
    with pytest.raises(ValidationError, match="BRU-PCM-15"), w.env.cr.savepoint():
        p.with_user(exiter).action_complete_exit()
    r.with_user(w.officer).action_cancel()
    p.with_user(exiter).action_complete_exit()
    assert p.state == "exited" and p.exited_on == w.today
    # dormancy is an owner window: unset, the job does nothing
    q = _partner(w)
    assert w.env["fix.partner"].cron_partner_dormancy() == 0
    w.env["ir.config_parameter"].sudo().set_param("cd_partner.dormancy_days", "1")
    w.env.flush_all()  # the pending ORM writes must not overwrite the back-dating
    w.env.cr.execute(
        "UPDATE fix_partner SET onboarded_at = now() - interval '5 days', "
        "create_date = now() - interval '5 days' WHERE id = %s",
        (q.id,),
    )
    q.invalidate_recordset()
    assert w.env["fix.partner"].cron_partner_dormancy() >= 1
    assert q.state == "dormant"


def test_f30_a_tier_move_waits_for_its_notice(w):
    p = _partner(w)
    prog = p.programme_id.sudo()
    tier2 = (
        w.env["fix.partner.tier"]
        .sudo()
        .create(
            {
                "programme_id": prog.id,
                "code": "T2",
                "name": "Tier 2",
                "criteria": "c",
                "notice_days": 30,
            }
        )
    )
    guarded_write(p, {"tier_id": prog.tier_ids[0].id})
    p.with_user(w.manager).action_change_tier(tier_code="T2")
    assert p.tier_id != tier2 and p.pending_tier_id == tier2
    assert p.tier_effective_on == w.today + timedelta(days=30)
    w.env["fix.partner"].cron_apply_tier_changes()
    assert p.tier_id != tier2
    guarded_write(p, {"tier_effective_on": w.today})
    w.env["fix.partner"].cron_apply_tier_changes()
    assert p.tier_id == tier2 and not p.pending_tier_id


# =================================================================== F14/F20
def test_f14_authorisation_escalates_at_180_90_30_and_gates_brand_work(w):
    brand = w.env["fix.brand"].sudo().create({"name": "B5 Brand", "code": "B5BR"})
    p = _partner(w, "brand", brand_id=brand.id)
    Auth = w.env["fix.partner.authorisation"]
    auth = Auth.with_user(w.officer).create(
        {
            "name": "B5 auth",
            "partner_id": p.id,
            "brand_id": brand.id,
            "valid_from": w.today - timedelta(days=10),
            "valid_to": w.today + timedelta(days=170),
            "certificate_ref": "CERT-1",
        }
    )
    auth.with_user(w.officer).write({"certificate_attachment_id": _doc(w, auth).id})
    auth.with_user(w.manager).action_activate()
    assert Auth.fix_brand_authorisation(brand) == auth
    Auth.cron_authorisation_expiry()
    assert auth.expiry_warned_days == 180
    Auth.cron_authorisation_expiry()  # once per threshold
    events = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "partner.authorisation_expiring"), ("aggregate_id", "=", auth.id)]
        )
    )
    assert len(events) == 1
    result = _relay(w, "partner.authorisation_expiring", auth)
    assert result["activities"] >= 1
    guarded_write(auth, {"valid_to": w.today + timedelta(days=20)})
    Auth.cron_authorisation_expiry()
    assert auth.expiry_warned_days == 30
    guarded_write(auth, {"valid_to": w.today - timedelta(days=1)})
    Auth.cron_authorisation_expiry()
    with pytest.raises(UserError, match="BRU-PCM-08"):
        Auth.fix_assert_brand_authorised(brand, "Repair under warranty")


def test_f20_a_brand_partner_names_its_brand_once(w):
    brand = w.env["fix.brand"].sudo().create({"name": "B5 Brand2", "code": "B5B2"})
    _partner(w, "brand", onboard=False, brand_id=brand.id)
    with pytest.raises(psycopg2.errors.UniqueViolation), w.env.cr.savepoint():
        _partner(w, "brand", onboard=False, brand_id=brand.id)
    brand3 = w.env["fix.brand"].sudo().create({"name": "B5 Brand3", "code": "B5B3"})
    with pytest.raises(ValidationError, match="brand partner"), w.env.cr.savepoint():
        _partner(w, "reseller", onboard=False, brand_id=brand3.id)


# =================================================================== F16
def test_f16_reseller_price_is_m11s_and_a_draw_bills(w):
    p = _partner(w, "reseller")
    product = (
        w.env["product.product"].sudo().create({"name": "B5 Refurb Phone", "default_code": "B5-RP"})
    )
    alloc = (
        w.env["fix.reseller.allocation"]
        .with_user(w.officer)
        .create(
            {
                "partner_id": p.id,
                "allocation_type": "capacity",
                "item_description": "Refurb phones",
                "product_id": product.id,
                "qty": 10,
                "period": "2026-Q4",
            }
        )
    )
    with pytest.raises(UserError), w.env.cr.savepoint():
        alloc.with_user(w.officer).write({"unit_price": 1.0})
    RateCard = type(w.env["fix.rate.card"])
    with (
        mock.patch.object(RateCard, "price_for", return_value={"price": None, "reason": "no card"}),
        pytest.raises(ValidationError, match="no released reseller price"),
        w.env.cr.savepoint(),
    ):
        alloc.with_user(w.manager).action_allocate()
    quote = {"price": 9500.0, "source": "card", "card_id": False, "reason": ""}
    with mock.patch.object(RateCard, "price_for", return_value=quote) as priced:
        alloc.with_user(w.manager).action_allocate()
    assert priced.call_args.kwargs["channel"] == "reseller"
    assert alloc.unit_price == 9500.0
    res = alloc.with_user(w.officer).action_record_draw(qty=2)
    draw = w.env["fix.reseller.draw"].browse(res["res_ids"])
    inv = draw.invoice_id.sudo()
    assert inv.customer_id == p.partner_id and inv.taxable_amount == 19000.0
    assert alloc.consumed_qty == 2


# =================================================================== F29
def test_f29_a_portal_call_to_a_manager_action_is_refused_not_crashed(w):
    p = _partner(w)
    portal = _mk(w.env, "b5_portal3", "cd_partner.group_fix_partner_portal", share=True)
    with pytest.raises(UserError, match="needs the"):
        p.with_user(portal).action_suspend(reason="x")


# =================================================================== billing engine
def test_m08_f4_the_invoice_operating_unit_reaches_the_gl_dimensions(w):
    other = (
        w.env["operating.unit"]
        .sudo()
        .search([("company_id", "=", w.company.id), ("id", "!=", w.ou.id)], limit=1)
    )
    ou = other or w.ou
    inv = paid_invoice(w.env, _party(w, "B5 OU"), 1000.0, ou=ou)
    dims = inv._ar_posting_dims()
    assert dims["operating_unit_id"] == ou.id
    assert (
        w.env["fix.ar.invoice"]._ar_posting_dims(operating_unit_id=ou.id)["operating_unit_id"]
        == ou.id
    )


def test_m37_f2_an_exempt_catalogue_item_is_not_taxed(w):
    product = w.env["product.product"].sudo().create({"name": "B5 Exempt", "default_code": "B5-EX"})
    item = w.env["fix.catalogue.item"].sudo().search(
        [("product_tmpl_id", "=", product.product_tmpl_id.id)], limit=1
    ) or w.env["fix.catalogue.item"].sudo().create({"product_tmpl_id": product.product_tmpl_id.id})
    guarded_write(item, {"vat_class": "exempt", "hs_code": "9999.99.99"})
    inv = (
        w.env["fix.ar.invoice"]
        .sudo()
        ._fix_draft_invoice_from_source(
            "test.m37",
            "b5-exempt",
            _party(w, "B5 VAT"),
            [{"description": "exempt", "taxable_amount": 1000.0, "product_id": product.id}],
            "test",
            company=w.company,
        )
    )
    assert inv.vat_amount == 0.0 and inv.taxable_amount == 1000.0
    guarded_write(item, {"vat_class": "standard_15"})
    inv2 = (
        w.env["fix.ar.invoice"]
        .sudo()
        ._fix_draft_invoice_from_source(
            "test.m37",
            "b5-standard",
            _party(w, "B5 VAT2"),
            [{"description": "std", "taxable_amount": 1000.0, "product_id": product.id}],
            "test",
            company=w.company,
        )
    )
    assert inv2.vat_amount == 150.0


def test_x10_a_concurrent_invoice_number_waits_instead_of_failing(w):
    """A second connection holds the no_gap sequence row (a concurrent issue
    mid-transaction) and lets go after 1.5 s. The number is drawn after the
    wait; with Odoo's NOWAIT alone it raised LockNotAvailable at once. The
    module's template sequence stands in for the company copy because it is
    committed (a copy made inside this rolled-back test is invisible to the
    other connection)."""
    Invoice = w.env["fix.ar.invoice"]
    seq = w.env.ref("cd_billing_engine.seq_fix_ar_invoice").sudo()
    inv = paid_invoice(w.env, _party(w, "B5 X10"), 10.0)
    other = w.env.registry.cursor()
    try:
        other.execute("SELECT id FROM ir_sequence WHERE id = %s FOR UPDATE", (seq.id,))
        timer = threading.Timer(1.5, other.rollback)
        timer.start()
        with mock.patch.object(type(Invoice), "_invoice_sequence", lambda self, company: seq):
            number = inv._next_invoice_no()
        assert number
        timer.join()
    finally:
        other.close()


# =================================================================== deployment
def test_deployment_wiring(w):
    env = w.env
    for xmlid in (
        "cd_partner.ir_cron_partner_tier_changes",
        "cd_partner.ir_cron_partner_dormancy",
        "cd_partner.ir_cron_partner_authorisation_expiry",
    ):
        assert env.ref(xmlid).active
    Consumer = env["fix.event.consumer"].sudo()
    for etype, model, method in (
        (
            "partner.authorisation_expiring",
            "fix.partner.authorisation",
            "consume_partner_authorisation_expiring",
        ),
        (
            "partner.mdf_claim_approved",
            "fix.a04.finance.consumers",
            "consume_partner_mdf_claim_approved",
        ),
        ("partner.rebate_approved", "fix.a04.finance.consumers", "consume_partner_rebate_approved"),
    ):
        sub = Consumer.search([("event_type", "=", etype), ("model", "=", model)])
        assert sub and sub.method == method and hasattr(env[model], method)
    assert env.ref("cd_partner.access_fix_referral").perm_write is False
    assert env.ref("cd_partner.access_fix_referral").perm_create is False
    from odoo.addons.cd_p03_portal.controllers.a04 import m40

    assert "action_raise_invoice" in m40.SURFACES["fix.franchise.royalty"]["actions"]
    assert "fix.partner.rate.change" in m40.SURFACES
    kpis = m40.kpis(env(user=w.manager))
    assert None not in kpis.values()
    for fn in m40.REPORTS.values():
        fn(env(user=w.manager), date_from=w.today - timedelta(days=30), date_to=w.today)
