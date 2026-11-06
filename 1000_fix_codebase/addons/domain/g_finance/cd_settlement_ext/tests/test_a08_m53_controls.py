# A08 · M53 Settlements, commissions, revenue, subscriptions — the control
# suite (B4 remediation).
#
# One test per gap probe of working/A08_evidence/probes/m53/probe_m53.py,
# named after the probe id: the same attack, run as a NON-ADMIN user holding
# the real role (created in the transaction), now REFUSED; plus the proper
# path end to end — referral converted from a paid invoice, accrued, paid in
# a payout run prepared by one person, approved from the M63 inbox by
# another, released by treasury (M50) and confirmed by an imported bank
# statement debit.
#   acct / acct2     : account.group_account_user
#   mgr / mgr2       : account.group_account_manager
#   cfo              : account.group_account_manager + DOFA Tier 4 (CFO)
#   sales            : cd_partner.group_fix_referral_manager (R21)
#   plain            : base.group_user only
import types
import uuid
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
CHART = {
    "101000": ("Disbursement Bank", "asset_cash", None),
    "400100": ("Marketplace Commission Revenue", "income", None),
    "200200": ("Marketplace Seller Payable", "liability_payable", None),
    "210100": ("TDS Withheld Liability", "liability_current", None),
    "631100": ("Partner Commission Expense", "expense", "partner_commission_expense"),
    "200300": ("Partner Commission Payable", "liability_payable", "partner_payable"),
    "200400": ("Customer Refund Clearing", "liability_current", "clawback_recovery"),
    "640100": ("Warranty Expense", "expense", "warranty_expense"),
    "250100": ("Warranty Provision", "liability_current", "warranty_provision"),
    "121000": ("Trade Receivables", "asset_receivable", None),
    "400000": ("Service Revenue", "income", None),
    "211000": ("VAT Output", "liability_current", None),
    "212000": ("Contract Liability", "liability_current", None),
    "101401": ("Cash", "asset_cash", None),
}


class Ctx:
    pass


@pytest.fixture
def c(odoo_env):
    env0 = odoo_env
    tag = uuid.uuid4().hex[:5].upper()
    x = Ctx()
    company = env0["res.company"].create({"name": "B4M53 Co %s" % tag, "vat": "1234567890123"})
    env = env0(context=dict(env0.context, allowed_company_ids=company.ids))
    x.env, x.company, x.tag = env, company, tag
    x.ou = env["operating.unit"].create(
        {
            "name": "B4M53 OU %s" % tag,
            "code": "B5%s" % tag[:4],
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    x.journal = env["account.journal"].create(
        {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
    )
    x.bank_journal = env["account.journal"].create(
        {"name": "Payout Bank", "code": "PB%s" % tag[:3], "type": "bank", "company_id": company.id}
    )
    Account = env["account.account"].with_company(company)
    x.acc = {
        code: Account.create(
            {"code": code, "name": name, "account_type": kind, "company_ids": [(6, 0, company.ids)]}
        )
        for code, (name, kind, _r) in CHART.items()
    }
    param = env["ir.config_parameter"].sudo()
    for code, (_n, _k, role) in CHART.items():
        if role:
            param.set_param("cd_settlement_ext.account_code.%s" % role, code)
    param.set_param("cd_settlement_ext.payout_journal_code", x.bank_journal.code)
    # treasury's single-releaser ceiling: the payout tests exercise the M53
    # approval; M50's own DOFA leg is B1's suite
    param.set_param("cd_cash_position.release_single_ceiling", "5000000")
    env["fix.ar.invoice"]._invoice_sequence(company)
    env["fix.ar.invoice"]._mushak_sequence(company)

    def user(login, *groups):
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "%s %s" % (login, tag),
                    "login": "%s-%s@b4m53.test" % (login, tag),
                    "company_id": company.id,
                    "company_ids": [(6, 0, company.ids)],
                    "assigned_operating_unit_ids": [(6, 0, x.ou.ids)],
                    "default_operating_unit_id": x.ou.id,
                    "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
                }
            )
        )

    x.acct, x.acct2 = user("acct", ACC), user("acct2", ACC)
    x.mgr, x.mgr2 = user("mgr", MGR), user("mgr2", MGR)
    x.cfo = user("cfo", MGR, "cd_entity_config.group_dofa_tier_4")
    x.sales = user("sales", "cd_partner.group_fix_referral_manager")
    x.plain = user("plain")
    x.payee = env["res.partner"].create({"name": "B4M53 Payee %s" % tag})
    x.payee_bank = _confirmed_bank(x, x.payee, "060272531", "2050123456789")
    x.payee2 = env["res.partner"].create({"name": "B4M53 Payee2 %s" % tag})
    _confirmed_bank(x, x.payee2, "060272531", "2050999999999")
    x.customer = env["res.partner"].create({"name": "B4M53 Customer %s" % tag})
    x.fpartner = env["fix.partner"].create(
        {
            "name": x.payee.name,
            "partner_id": x.payee.id,
            "partner_type": "referral",
            "commission_rate": 0.05,
            "company_id": company.id,
        }
    )
    x.pscheme = env["fix.commission.scheme"].create(
        {
            "name": "Partner TDS 10%",
            "scheme_type": "partner",
            "tds_rate": 0.10,
            "date_from": date(2025, 7, 1),
            "company_id": company.id,
        }
    )
    return x


def _confirmed_bank(x, partner, routing, account):
    """A payee account confirmed under M52's dual control (B2): proposed by an
    accountant with the call-back recorded, confirmed by another manager."""
    env, company = x.env, x.company
    bank = env["res.bank"].create({"name": "%s Bank" % partner.name, "bic": routing})
    change = env(user=x.acct2.id)["fix.payee.bank.change"].create(
        {
            "company_id": company.id,
            "partner_id": partner.id,
            "acc_number": account,
            "bank_id": bank.id,
            "routing_number": routing,
            "verification_ref": "call-back on the number on file (test)",
        }
    )
    change.action_propose()
    change.with_user(x.cfo).action_confirm()
    return change.with_env(env).result_bank_id


def as_(c, user):
    return c.env(user=user.id)


def lines(move):
    return sorted(
        (ln.account_id.with_company(move.company_id).code, ln.debit, ln.credit)
        for ln in move.line_ids
    )


def inbox_approve(c, record, user):
    task = (
        c.env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("res_model", "=", record._name),
                ("res_id", "=", record.id),
                ("state", "=", "pending"),
                ("assigned_user_id", "=", user.id),
            ],
            limit=1,
        )
    )
    assert task, "no pending M63 task for %s on %s" % (user.login, record.display_name)
    task.with_user(user).action_approve()
    record.invalidate_recordset()


def paid_invoice(c, taxable=20000.0, customer=None):
    """A paid M20 invoice of the referred customer (raised by acct, issued by acct2)."""
    customer = customer or c.customer
    inv = as_(c, c.acct)["fix.ar.invoice"].create_manual_invoice(
        {"customer_id": customer.id, "operating_unit_id": c.ou.id, "company_id": c.company.id},
        [{"description": "Referred repair", "taxable_amount": taxable}],
        reason_code="referred job",
    )
    inv.with_user(c.acct2).action_issue()
    r = as_(c, c.acct)["fix.ar.receipt"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": customer.id,
            "amount": inv.total_payable,
            "method": "cash",
        }
    )
    r.action_confirm()
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": inv.id, "amount": inv.total_payable}
    )
    assert inv.state == "paid"
    return inv


def referral(c, user=None):
    return as_(c, user or c.acct)["fix.referral"].create(
        {
            "name": "REF-%s" % uuid.uuid4().hex[:6],
            "partner_id": c.fpartner.id,
            "referred_partner_id": c.customer.id,
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
        }
    )


def accrued_referral(c, taxable=20000.0):
    """Proper path: converted from the paid invoice (R21), earned, accrued (acct)."""
    inv = paid_invoice(c, taxable)
    r = referral(c)
    r.with_user(c.sales).action_convert(invoice=inv)
    r.with_user(c.sales).action_earn_commission()
    r.with_user(c.acct).action_accrue_commission()
    return r, r.commission_ledger_id


def system_row(c, gross, rate, payee=None, source_type="partner_referral", post=True, **kw):
    """A ledger row raised by trusted code (as the relay / a migration would)."""
    row = c.env["fix.commission.ledger"].create(
        dict(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "source_type": source_type,
                "seller_partner_id": (payee or c.payee).id,
                "gross_amount": gross,
                "commission_rate": rate,
                "scheme_id": c.pscheme.id,
            },
            **kw,
        )
    )
    if post:
        row.action_post_to_gl()
    return row


def prepared_run(c, preparer=None):
    run = as_(c, preparer or c.acct)["fix.payout.run"].create(
        {"period": "2026-10", "company_id": c.company.id, "operating_unit_id": c.ou.id}
    )
    run.action_collect_accrued()
    run.action_prepare()
    return run


def bank_confirm(c, pay):
    """The bank statement import debits the released amount (M50 evidence)."""
    line = c.env["fix.bank.statement.line"].create(
        {
            "company_id": c.company.id,
            "journal_id": (pay.released_journal_id or pay.journal_id).id,
            "date": fields.Date.today(),
            "amount": -pay.released_amount,
            "reference": pay.name,
            "statement_file_hash": uuid.uuid4().hex,
        }
    )
    line._fix_match_document("matched_payment_id", pay, "manual")


def pay_run(c, run):
    """Treasury: an accountant prepares each instruction, an Accounting
    Administrator other than the payout approver releases it, the bank
    statement confirms it."""
    run.with_user(c.acct).action_request_payments()
    for pay in run.line_ids.mapped("payment_execution_id"):
        pay.with_user(c.acct2).action_prepare()
        releaser = c.mgr2 if run.approved_by_id != c.mgr2 else c.mgr
        pay.with_user(releaser).action_release()
        bank_confirm(c, pay)
    run.invalidate_recordset()


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write, "original_endpoint", g.P03GenericApiController.model_write
    )
    old = getattr(g, "request", None)
    holder = types.SimpleNamespace(env=None)
    g.request = holder

    def write(user, **kw):
        holder.env = as_(c, user)
        return mw(ctl, **kw)

    try:
        yield types.SimpleNamespace(write=write)
    finally:
        g.request = old


# ============================================================ reference run
def test_ref_01_referral_to_payout_proper_path(c):
    r, led = accrued_referral(c)
    assert r.base_amount == 20000.0 and r.invoice_id
    assert lines(led.gl_move_id) == [("200300", 0.0, 1000.0), ("631100", 1000.0, 0.0)]
    assert led.tds_amount == 150.0 and not led.psr_verified  # 10% x 1.5 (no PSR on file)
    run = prepared_run(c)
    assert run.state == "prepared" and run.prepared_by_id == c.acct
    inbox_approve(c, run, c.mgr)
    assert run.state == "approved" and run.approved_by_id == c.mgr and run.approved_total == 850.0
    line = run.line_ids
    assert line.partner_id == c.payee and line.acc_number == "2050123456789" and line.amount == 850.0
    pay_run(c, run)
    assert run.state == "executed" and led.state == "paid" and run.gl_move_id
    pay = line.payment_execution_id
    assert pay.state == "executed" and pay.source_posts_gl and not pay.move_id
    assert lines(run.gl_move_id) == sorted(
        [("200300", 1000.0, 0.0), ("210100", 0.0, 150.0),
         (c.bank_journal.default_account_id.code, 0.0, 850.0)]
    )
    st = run.statement_ids
    assert st.state == "issued" and st.net_payable == 850.0 and st.withholding_cert_ref.startswith("TDSC/")
    assert run.name.startswith("PAY/") and led.name.startswith("COM/") and st.name.startswith("STM/")


# ============================================================ commission maths
def test_m53_01_scheme_rate_applies(c):
    s = c.env["fix.commission.scheme"].create(
        {
            "name": "Platinum 12%",
            "scheme_type": "seller",
            "seller_tier": "platinum",
            "commission_rate": 0.12,
            "tds_rate": 0.10,
            "date_from": date(2025, 7, 1),
            "company_id": c.company.id,
        }
    )
    row = system_row(
        c, 100000.0, 0.10, payee=c.payee2, source_type="marketplace", post=False, scheme_id=s.id
    )
    assert row.commission_rate == 0.12 and abs(row.commission_amount - 12000.0) < 0.01


def test_m53_02_commission_rows_are_never_typed(c):
    with pytest.raises(UserError, match="never typed"):
        as_(c, c.acct)["fix.commission.ledger"].create(
            {
                "company_id": c.company.id,
                "seller_partner_id": c.payee2.id,
                "gross_amount": 100000.0,
                "commission_rate": 0.0,
            }
        )
    row = system_row(c, 100000.0, 0.0, payee=c.payee2, source_type="marketplace", post=False,
                     scheme_id=False)
    with pytest.raises(UserError):
        row.with_user(c.acct).action_post_to_gl()


def test_m53_03_tds_locked_after_accrual(c):
    _r, row = accrued_referral(c)
    with pytest.raises(UserError):
        row.with_user(c.acct).write({"tds_amount": 0.0})
    assert row.tds_amount == 150.0


def test_m53_04_psr_comes_from_the_tax_profile(c):
    _r, row = accrued_referral(c)
    with pytest.raises(UserError):
        row.with_user(c.acct).write({"psr_verified": True, "psr_slip_number": "x"})
    evidence = c.env["ir.attachment"].create({"name": "psr.pdf", "raw": b"%PDF-1.4 test"})
    c.env["fix.vendor.tax.profile"].create(
        {
            "company_id": c.company.id,
            "partner_id": c.payee.id,
            "tin": "123456789012",
            "psr_reference": "PSR-2026-001",
            "psr_valid_until": date.today() + timedelta(days=90),
            "psr_attachment_ids": [(6, 0, evidence.ids)],
        }
    )
    row2 = system_row(c, 20000.0, 0.05, post=False)
    assert row2.psr_verified and row2.psr_slip_number == "PSR-2026-001"
    assert row2.tds_amount == 100.0  # 10% of 1,000, no non-filer uplift


def test_m53_05_unaccrued_row_cannot_be_forged_into_a_run(c):
    row = system_row(c, 20000.0, 0.05, post=False)
    with pytest.raises(UserError):
        row.with_user(c.acct).write({"state": "accrued"})
    run = as_(c, c.acct)["fix.payout.run"].create({"period": "2026-10", "company_id": c.company.id})
    with pytest.raises(UserError):
        run.action_collect_accrued()
    assert row not in run.commission_ids


def test_m53_06_lp07_lock_on_gross(c):
    _r, row = accrued_referral(c)
    with pytest.raises(UserError):
        row.with_user(c.acct).write({"gross_amount": 999999.0})


def test_m53_07_partner_commission_needs_its_referral(c):
    with pytest.raises(UserError):
        as_(c, c.acct)["fix.commission.ledger"].create(
            {
                "company_id": c.company.id,
                "source_type": "partner_referral",
                "seller_partner_id": c.payee.id,
                "gross_amount": 2000000.0,
                "commission_rate": 0.5,
            }
        )
    orphan = system_row(c, 2000000.0, 0.5, post=False)
    with pytest.raises(UserError, match="referral"):
        orphan.with_user(c.acct).action_post_to_gl()


# ============================================================ payout approval (F2)
def test_m53_08_preparer_cannot_approve(c):
    accrued_referral(c)
    run = prepared_run(c, c.mgr)
    assigned = run.approval_request_id.sudo().task_ids.mapped("assigned_user_id")
    assert c.mgr not in assigned
    with pytest.raises(UserError):
        run.with_user(c.mgr).action_approve()


def test_m53_09_accountant_cannot_approve(c):
    accrued_referral(c)
    run = prepared_run(c)
    with pytest.raises(UserError):
        run.with_user(c.acct2).action_approve()
    assert c.acct2 not in run.approval_request_id.sudo().task_ids.mapped("assigned_user_id")


def test_m53_10_preparer_stamp_cannot_be_blanked(c):
    accrued_referral(c)
    run = prepared_run(c, c.mgr)
    with pytest.raises(UserError):
        run.with_user(c.mgr).write({"prepared_by_id": False})


def test_m53_11_run_state_cannot_be_written(c):
    accrued_referral(c)
    run = prepared_run(c)
    with pytest.raises(UserError):
        run.with_user(c.acct).write({"state": "approved"})
    with pytest.raises(UserError):
        run.with_user(c.acct).action_generate_beftn()
    assert run.state == "prepared"


def test_m53_12_rows_frozen_once_prepared_and_pinned_at_approval(c):
    accrued_referral(c)
    run = prepared_run(c)
    big = system_row(c, 2000000.0, 0.5)
    with pytest.raises(UserError):
        run.with_user(c.acct).write({"commission_ids": [(4, big.id)]})
    inbox_approve(c, run, c.mgr)
    with pytest.raises(UserError):
        run.with_user(c.acct).write({"commission_ids": [(4, big.id)]})
    assert run.total_payable == run.approved_total == 850.0


def test_m53_13_payee_bank_swapped_after_approval_is_not_paid(c):
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    with pytest.raises(REFUSED):
        as_(c, c.acct)["res.partner.bank"].browse(c.payee_bank.id).write(
            {"acc_number": "9999000011112222"}
        )
    # even someone allowed to change it cannot redirect the approved payout
    c.payee_bank.sudo().write({"acc_number": "9999000011112222"})
    with pytest.raises(UserError):
        run.with_user(c.acct).action_request_payments()
    assert not run.line_ids.payment_execution_id


def test_m53_14_executed_run_is_never_approved_or_paid_again(c):
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    pay_run(c, run)
    assert run.state == "executed"
    with pytest.raises(REFUSED):
        run.with_user(c.mgr2).action_approve()
    with pytest.raises(UserError):
        run.sudo().action_approve()
    with pytest.raises(UserError):
        run.with_user(c.acct).action_request_payments()
    assert len(run.statement_ids) == 1
    assert c.env["fix.payment.execution"].search_count(
        [("source_model", "=", "fix.payout.run.line"), ("source_id", "in", run.line_ids.ids)]
    ) == 1


def test_m53_15_no_typed_bank_confirmation_and_approver_does_not_release(c):
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    with pytest.raises(UserError):
        run.with_user(c.mgr).action_confirm_bank_settlement("x")
    run.with_user(c.acct).action_request_payments()
    pay = run.line_ids.payment_execution_id
    pay.with_user(c.acct2).action_prepare()
    with pytest.raises(UserError):
        pay.with_user(c.mgr).action_release()
    assert run.state == "executing"


def test_m53_16_large_payout_goes_to_the_cfo(c):
    system_row(c, 6000000.0, 0.5)  # commission 3,000,000 -> net above the CFO band
    run = prepared_run(c)
    assert run._dofa_current_tier() == "tier_4"
    assigned = run.approval_request_id.sudo().task_ids.mapped("assigned_user_id")
    assert c.cfo in assigned and c.mgr not in assigned
    inbox_approve(c, run, c.cfo)
    assert run.state == "approved"


# ============================================================ escrow
def test_m53_17_escrow_only_released_by_its_action(c):
    _r, row = accrued_referral(c)
    adj = as_(c, c.acct)["fix.settlement.adjustment"].create(
        {
            "adjustment_type": "escrow",
            "seller_partner_id": c.payee.id,
            "commission_ids": [(6, 0, row.ids)],
            "reason": "buyer dispute",
            "company_id": c.company.id,
        }
    )
    adj.action_activate()
    assert row.escrow_hold
    with pytest.raises(UserError):
        row.with_user(c.acct).write({"escrow_hold": False})
    run = as_(c, c.acct)["fix.payout.run"].create({"period": "2026-10", "company_id": c.company.id})
    with pytest.raises(UserError):
        run.action_collect_accrued()
    adj.with_user(c.acct2).action_release()
    assert not row.escrow_hold


def test_m53_18_escrow_release_needs_second_person(c):
    _r, row = accrued_referral(c)
    adj = as_(c, c.acct)["fix.settlement.adjustment"].create(
        {
            "adjustment_type": "escrow",
            "seller_partner_id": c.payee.id,
            "commission_ids": [(6, 0, row.ids)],
            "reason": "buyer dispute",
            "company_id": c.company.id,
        }
    )
    adj.action_activate()
    with pytest.raises(AccessError):
        adj.action_release()


# ============================================================ seller statements
def statement(c, user, **vals):
    return as_(c, user)["fix.seller.statement"].create(
        dict(
            {
                "company_id": c.company.id,
                "seller_partner_id": c.payee2.id,
                "period": "2026-10",
                "gross_gmv": 25000.0,
                "commission_amount": 2500.0,
                "tds_withheld": 250.0,
            },
            **vals,
        )
    )


def test_m53_19_statement_born_draft_issued_only_after_payout(c):
    with pytest.raises(UserError):
        statement(c, c.acct, state="issued")
    with pytest.raises(UserError):
        statement(c, c.acct, withholding_cert_ref="NBR-TDS52-TYPED")
    st = statement(c, c.acct)
    assert st.state == "draft"
    with pytest.raises(UserError):
        st.action_issue_statement()


def test_m53_20_statement_settle_requires_executed_run(c):
    st = statement(c, c.acct)
    with pytest.raises(UserError):
        st.action_settle_statement()


def test_m53_21_issued_statement_is_immutable(c):
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    pay_run(c, run)
    st = run.statement_ids
    st.with_user(c.acct).action_settle_statement()
    with pytest.raises(UserError):
        st.with_user(c.acct).write({"tds_withheld": 0.0})
    with pytest.raises(UserError):
        st.with_user(c.acct).write({"withholding_cert_ref": "EDITED"})
    assert st.tds_withheld == 150.0


def test_m53_22_net_is_computed_with_the_platform_fee(c):
    st = statement(
        c, c.acct, gross_gmv=50000.0, commission_amount=5000.0, tds_withheld=500.0,
        platform_fee=135.0, net_payable=44500.0,
    )
    assert st.net_payable == 50000.0 - 5000.0 - 500.0 - 135.0


# ============================================================ IFRS 15 revenue
def sub(c, user, **kw):
    return as_(c, user)["fix.subscription"].create(
        dict(
            {
                "name": "SUB-%s" % uuid.uuid4().hex[:5],
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "customer_id": c.payee2.id,
                "recurring_amount": 1000.0,
                "billing_cycle": "monthly",
                "start_date": date.today() - timedelta(days=60),
                "next_invoice_date": date.today() - timedelta(days=60),
            },
            **kw,
        )
    )


def test_m53_23_recognition_cannot_be_reset_or_doubled(c):
    s = sub(c, c.acct, contract_value=120000.0, contract_end_date=date.today() + timedelta(days=185))
    s.with_user(c.acct).action_generate_revrec_schedule()
    sched = s.obligation_ids.schedule_id
    sched.with_user(c.acct).action_recognize_period()
    first = sched.recognized_amount
    assert first > 0
    with pytest.raises(UserError):
        sched.with_user(c.acct).write({"recognized_amount": 0.0})
    sched.with_user(c.acct).action_recognize_period()
    assert sched.recognized_amount == first == sum(sched.line_ids.mapped("amount"))
    with pytest.raises(AccessError):
        as_(c, c.acct)["fix.revenue.recognition.line"].create(
            {"schedule_id": sched.id, "date": date.today(), "amount": -first}
        )


def test_m53_24_manual_schedule_needs_contract_and_cfo(c):
    S = as_(c, c.acct)["fix.revenue.schedule"]
    s = S.create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "description": "manual",
            "total_amount": 1200000.0,
            "start_date": date.today() - timedelta(days=180),
            "end_date": date.today() + timedelta(days=185),
        }
    )
    assert s.source_model == "manual" and s.state == "draft"
    with pytest.raises(UserError):
        s.action_recognize_period()
    with pytest.raises(UserError):
        s.action_request_cfo_approval()
    contract = sub(c, c.acct, contract_value=100000.0)
    s2 = S.create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "description": "manual release",
            "total_amount": 60000.0,
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today() + timedelta(days=335),
            "subscription_id": contract.id,
            "manual_reason": "contract modification",
            "evidence_ref": "Addendum 3",
        }
    )
    s2.action_request_cfo_approval()
    assigned = s2.approval_request_id.sudo().task_ids.mapped("assigned_user_id")
    assert c.cfo in assigned and c.acct not in assigned and c.mgr not in assigned
    with pytest.raises(UserError):
        s2.with_user(c.cfo).action_dofa_approve()
    inbox_approve(c, s2, c.cfo)
    assert s2.state == "active" and s2.dofa_approved_by == c.cfo
    s2.with_user(c.acct).action_recognize_period()
    assert s2.recognized_amount > 0


def test_m53_25_obligation_allocation_cannot_be_forged(c):
    s = sub(c, c.acct, contract_value=12000.0, contract_end_date=date.today() + timedelta(days=300))
    ob = as_(c, c.acct)["fix.performance.obligation"].create(
        {"subscription_id": s.id, "name": "AMC", "standalone_price": 12000.0,
         "start_date": s.start_date, "end_date": s.contract_end_date}
    )
    with pytest.raises(UserError):
        ob.write({"allocated_amount": 999999.0, "state": "allocated"})
    s.with_user(c.acct).action_allocate_price()
    ob.action_create_schedule()
    assert ob.schedule_id.total_amount == 12000.0


def test_m53_26_allocation_sums_to_price(c):
    s = sub(c, c.acct, contract_value=10000.0, contract_end_date=date.today() + timedelta(days=300))
    O = as_(c, c.acct)["fix.performance.obligation"]
    for name, ssp in (("AMC", 7000.0), ("Warranty", 2000.0), ("Parts", 3333.33)):
        O.create({"subscription_id": s.id, "name": name, "standalone_price": ssp})
    s.with_user(c.acct).action_allocate_price()
    assert abs(sum(s.obligation_ids.mapped("allocated_amount")) - 10000.0) < 0.001


def test_m53_27_generator_schedules_the_whole_contract(c):
    start = date.today() - timedelta(days=60)
    s = sub(c, c.acct, start_date=start, contract_end_date=start + timedelta(days=365))
    sch = s.with_user(c.acct).action_generate_revrec_schedule()
    assert s.obligation_ids.obligation_type == "amc_service"
    assert abs(sum(sch.mapped("total_amount")) - 12000.0) < 0.01


# ============================================================ subscriptions (F6)
def test_m53_28_plain_user_cannot_write_refund_fields(c):
    s = sub(c, c.acct)
    with pytest.raises(REFUSED):
        as_(c, c.plain)["fix.subscription"].browse(s.id).write(
            {"last_refund_amount": 99999.0, "state": "cancelled"}
        )
    with pytest.raises(AccessError):
        as_(c, c.plain)["fix.subscription"].browse(s.id).write({"grace_period_days": 1})
    with pytest.raises(UserError):
        s.with_user(c.acct).write({"last_refund_amount": 99999.0})


def test_m53_29_refund_credit_note_needs_another_approver(c):
    s = sub(c, c.acct, recurring_amount=20000.0, next_invoice_date=date.today() - timedelta(days=10),
            start_date=date.today() - timedelta(days=10))
    s.with_user(c.acct).action_generate_charge()
    invoice = s.charge_ids.invoice_id
    invoice.with_user(c.acct2).action_issue()
    s.with_user(c.acct).action_request_refund(cancellation_date=date.today())
    note = s.refund_credit_note_id
    assert note.state == "draft" and s.refund_requires_approval
    note.with_user(c.acct).action_submit()
    with pytest.raises(REFUSED):
        note.with_user(c.acct).action_approve()
    with pytest.raises(UserError):
        note.with_user(c.acct).action_issue()
    inbox_approve(c, note, c.mgr)
    note.with_user(c.acct).action_issue()
    assert note.state == "issued"


def test_m53_30_reinstate_needs_finance_and_settled_invoices(c):
    start = date.today() - timedelta(days=20)  # inside the 31-day backdate floor
    s = sub(c, c.acct, start_date=start, next_invoice_date=start)
    s.with_user(c.acct).action_generate_charge()
    # trusted staging: the cycle invoice issued 45 days ago — past the
    # default 30-day terms, so the overdue-unpaid basis sees it owed
    s.charge_ids.invoice_id.sudo().write(
        {"invoice_date": date.today() - timedelta(days=45), "state": "issued"}
    )
    s.sudo()._guarded().write({"state": "hold", "dunning_step": "escalate", "days_overdue": 40})
    with pytest.raises(AccessError):
        as_(c, c.plain)["fix.subscription"].browse(s.id).action_reinstate()
    with pytest.raises(UserError, match="owes"):
        s.with_user(c.acct).action_reinstate()
    assert s.state == "hold"


def test_m53_31_plain_user_cannot_raise_charge(c):
    s = sub(c, c.acct)
    with pytest.raises(REFUSED):
        as_(c, c.plain)["fix.subscription"].browse(s.id).action_generate_charge()


# ============================================================ referral (F6)
def test_m53_32_conversion_by_r21_from_the_paid_invoice(c):
    r = referral(c, c.plain)
    with pytest.raises(AccessError):
        r.with_user(c.plain).action_convert(base_amount=5000000.0)
    with pytest.raises(UserError):
        r.with_user(c.sales).action_convert(base_amount=5000000.0)
    unpaid = as_(c, c.acct)["fix.ar.invoice"].create_manual_invoice(
        {"customer_id": c.customer.id, "operating_unit_id": c.ou.id, "company_id": c.company.id},
        [{"description": "x", "taxable_amount": 5000.0}],
        reason_code="x",
    )
    with pytest.raises(UserError, match="PAID"):
        r.with_user(c.sales).action_convert(invoice=unpaid)
    inv = paid_invoice(c, 4000.0)
    r.with_user(c.sales).action_convert(invoice=inv)
    assert r.state == "converted" and r.base_amount == 4000.0 and r.converted_by_id == c.sales


def test_m53_33_referral_state_cannot_be_written(c):
    r = referral(c, c.plain)
    with pytest.raises(REFUSED):
        r.with_user(c.plain).write({"state": "commissioned", "base_amount": 750000.0})
    with pytest.raises(UserError):
        r.with_user(c.sales).write({"state": "commissioned"})


def test_m53_34_plain_user_cannot_accrue(c):
    inv = paid_invoice(c, 1000.0)
    r = referral(c, c.plain)
    r.with_user(c.sales).action_convert(invoice=inv)
    r.with_user(c.sales).action_earn_commission()
    with pytest.raises(AccessError):
        r.with_user(c.plain).action_accrue_commission()


# ============================================================ warranty provision (IAS 37)
@pytest.fixture
def wp(c):
    c.env["fix.warranty.provision.policy"].create(
        {"name": "90d", "warranty_days": 90, "lookback_months": 12, "cost_ratio": 0.2,
         "date_from": date(2000, 1, 1), "company_id": c.company.id}
    )
    return c


def test_m53_35_provision_computer_cannot_post(wp):
    p = as_(wp, wp.mgr)["fix.warranty.provision"].create({"period": "2026-09", "company_id": wp.company.id})
    p.action_compute()
    with pytest.raises(AccessError):
        p.action_post()


def test_m53_36_provision_figures_cannot_be_typed(wp):
    p = as_(wp, wp.acct)["fix.warranty.provision"].create({"period": "2026-09", "company_id": wp.company.id})
    p.action_compute()
    with pytest.raises(UserError):
        p.write({"required_balance": 5000000.0, "movement": 5000000.0})
    p.with_user(wp.mgr).action_post()
    assert p.state == "posted" and p.movement == 0.0 and not p.move_id


def test_m53_37_provision_computer_stamp_cannot_be_rewritten(wp):
    p = as_(wp, wp.mgr)["fix.warranty.provision"].create({"period": "2026-09", "company_id": wp.company.id})
    p.action_compute()
    with pytest.raises(UserError):
        p.write({"computed_by_id": wp.acct.id})
    with pytest.raises(AccessError):
        p.action_post()


# ============================================================ reconciliation
def test_m53_38_reconciliation_reads_the_bank_side(c):
    accrued_referral(c)
    run = prepared_run(c)
    Rec = as_(c, c.acct)["fix.payout.reconciliation"]
    with pytest.raises(UserError):
        Rec.create({"company_id": c.company.id, "payout_run_id": run.id, "rail_count": 7,
                    "rail_amount": 1.0})
    rec = Rec.create({"company_id": c.company.id, "payout_run_id": run.id})
    with pytest.raises(UserError, match="released nothing"):
        rec.action_run_reconciliation()
    inbox_approve(c, run, c.mgr)
    run.with_user(c.acct).action_request_payments()
    rec.action_run_reconciliation()
    assert rec.state == "break_detected" and rec.rail_count == 0
    with pytest.raises(UserError):
        rec.write({"state": "balanced"})
    pay = run.line_ids.payment_execution_id
    pay.with_user(c.acct2).action_prepare()
    pay.with_user(c.mgr2).action_release()
    bank_confirm(c, pay)
    rec2 = Rec.create({"company_id": c.company.id, "payout_run_id": run.id})
    rec2.action_run_reconciliation()
    assert rec2.state == "balanced" and rec2.rail_amount == 850.0 and rec2.rail_count == 1


# ============================================================ P03 path
def test_m53_39_p03_cannot_approve_a_payout(c, p03):
    accrued_referral(c)
    run = prepared_run(c)
    out = p03.write(c.acct, model="fix.payout.run", record_id=run.id, values={"state": "approved"})
    run.invalidate_recordset()
    assert out.get("error") and run.state == "prepared"


def test_m53_40_p03_plain_user_cannot_commission_a_referral(c, p03):
    r = referral(c, c.plain)
    out = p03.write(c.plain, model="fix.referral", record_id=r.id,
                    values={"state": "commissioned", "base_amount": 900000.0})
    r.invalidate_recordset()
    assert out.get("error") and r.state == "submitted" and not r.base_amount


def test_m53_41_p03_plain_user_cannot_rewrite_a_subscription(c, p03):
    s = sub(c, c.acct)
    out = p03.write(c.plain, model="fix.subscription", record_id=s.id,
                    values={"state": "active", "recurring_amount": 1.0})
    s.invalidate_recordset()
    assert out.get("error") and s.recurring_amount == 1000.0


def test_m53_42_p03_refuses_readonly_sod_stamp(c, p03):
    accrued_referral(c)
    run = prepared_run(c)
    out = p03.write(c.acct, model="fix.payout.run", record_id=run.id,
                    values={"approved_by_id": c.mgr.id, "sod_verified": True})
    run.invalidate_recordset()
    assert out.get("error") and not run.sod_verified


def test_m53_43_manager_cannot_redirect_an_approved_payout(c):
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    try:
        as_(c, c.mgr2)["res.partner.bank"].browse(c.payee_bank.id).write(
            {"acc_number": "9999000011112222"}
        )
    except REFUSED:
        return
    # the change withdrew the account's confirmation and broke the pin
    with pytest.raises(UserError):
        run.with_user(c.acct).action_request_payments()


# ============================================================ wiring (M53-15)
def test_m53_15_wiring_sequences_cron_consumer(c):
    for xmlid, code in (
        ("seq_fix_payout_run", "fix.payout.run"),
        ("seq_fix_commission_ledger", "fix.commission.ledger"),
        ("seq_fix_seller_statement", "fix.seller.statement"),
        ("seq_fix_seller_statement_tds_cert", "fix.seller.statement.tds_cert"),
    ):
        assert c.env.ref("cd_settlement_ext.%s" % xmlid).code == code
    consumer = c.env.ref("cd_settlement_ext.consumer_commission_earned_marketplace")
    assert consumer.event_type == "commission.earned" and consumer.active
    cron = c.env.ref("cd_subscription.ir_cron_revenue_recognition")
    assert cron.active and "_cron_recognize" in cron.code


def test_m53_commission_consumer_is_relay_only(c):
    with pytest.raises(AccessError):
        as_(c, c.acct)["fix.commission.ledger"].consume_commission_earned(
            {"aggregate": "fix.marketplace.order", "aggregate_id": 1}
        )


# ============================================================ A04 requests (M39 / M40)
def _no_a04_proration(c):
    P = c.env["fix.subscription.proration"] if "fix.subscription.proration" in c.env else None
    return P is None or not hasattr(P, "create_for_plan_change")


def test_a04_m39_price_is_guarded_and_changed_by_a_second_person(c):
    s = sub(c, c.acct)
    with pytest.raises(UserError, match="Request Price"):
        s.with_user(c.acct).write({"recurring_amount": 1.0})
    if not _no_a04_proration(c):
        pytest.skip("A04's proration service decides the change on the merged branch")
    s.with_user(c.acct).action_request_price_change(1200.0, reason="plan upgrade")
    assert s.recurring_amount == 1000.0 and s.pending_recurring_amount == 1200.0
    with pytest.raises(UserError, match="Segregation"):
        s.with_user(c.acct).action_approve_price_change()
    s.with_user(c.acct2).action_approve_price_change()  # 2,400 a year: within the band
    assert s.recurring_amount == 1200.0 and not s.price_change_requested_by_id
    s.with_user(c.acct).action_request_price_change(5000.0, reason="enterprise tier")
    with pytest.raises(AccessError):  # 45,600 a year: the Accounting Administrator's
        s.with_user(c.acct2).action_approve_price_change()
    s.with_user(c.mgr).action_approve_price_change()
    assert s.recurring_amount == 5000.0


def test_a04_m39_reinstate_only_from_suspended(c):
    s = sub(c, c.acct)
    with pytest.raises(UserError, match="suspended"):
        s.with_user(c.acct).action_reinstate()
    s.sudo().write({"state": "past_due", "dunning_step": "reminder"})
    with pytest.raises(UserError, match="suspended"):
        s.with_user(c.acct).action_reinstate()
    s.sudo().write({"state": "hold", "dunning_step": "escalate"})
    s.with_user(c.acct).action_reinstate()  # no overdue unpaid invoice
    assert s.state == "active" and s.dunning_step == "none"


def test_a04_m39_cancellation_is_dated_today(c):
    s = sub(c, c.acct)
    with pytest.raises(UserError, match="never backdated"):
        s.with_user(c.acct).action_request_refund(cancellation_date=date.today() - timedelta(days=5))
    assert s.state == "active"
    s.with_user(c.acct).action_cancel()
    assert s.state == "cancelled" and s.cancelled_on == date.today()


def test_a04_m39_quotation_consumer(c):
    consumer = c.env.ref("cd_subscription.consumer_quotation_accepted_subscription")
    assert consumer.event_type == "quotation.accepted" and consumer.active
    Sub = c.env["fix.subscription"]
    with pytest.raises(AccessError):
        as_(c, c.acct)["fix.subscription"].consume_quotation_accepted({"aggregate_id": 1})
    Quote = c.env["fix.quotation"] if "fix.quotation" in c.env else None
    if Quote is None or "quote_type" not in Quote._fields:
        pytest.skip("subscription quotations exist on A04's branch only")
    quote = Quote.create(
        {
            "name": "QT-B4-%s" % c.tag,
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": c.payee2.id,
            "quote_type": "subscription",
            "value": 12000.0,
            "contract_months": 12,
        }
    )
    event = {"aggregate": "fix.quotation", "aggregate_id": quote.id, "payload": {}}
    with pytest.raises(UserError, match="not accepted"):
        Sub.consume_quotation_accepted(event)
    quote.sudo()._guarded().write({"state": "accepted"})
    out = Sub.consume_quotation_accepted(event)
    s = Sub.browse(out["id"])
    assert out["created"] and s.recurring_amount == 1000.0 and s.contract_value == 12000.0
    assert Sub.consume_quotation_accepted(event)["created"] is False


def test_a04_m40_no_self_or_duplicate_referral(c):
    referral(c)
    # the merged gate: an estate-wide open-referral refusal (UserError from
    # the create gate) or the per-referrer constraint (ValidationError)
    with pytest.raises(REFUSED, match="already has an open referral"):
        referral(c)
    with pytest.raises(REFUSED, match="cannot refer themselves"):
        as_(c, c.acct)["fix.referral"].create(
            {
                "name": "REF-SELF-%s" % c.tag,
                "partner_id": c.fpartner.id,
                "referred_partner_id": c.payee.id,
                "company_id": c.company.id,
            }
        )


# ============================================================ A04 bridge (c) + payout hold
def _commissioned_order(c, gross=50000.0):
    seller = c.env["fix.marketplace.seller"].create(
        {"name": "B4 Seller %s" % c.tag, "partner_id": c.payee2.id, "company_id": c.company.id}
    )
    # trusted staging of the KYC/CFO decision (both stamps are guarded; the
    # quote gate reads them - BRU-ECM-01)
    seller.sudo()._guarded().write({"kyc_status": "verified", "cfo_approved": True})
    order = c.env["fix.marketplace.order"].create(
        {"customer_id": c.customer.id, "description": "Screen repair", "company_id": c.company.id,
         "operating_unit_id": c.ou.id, "budget": gross, "commission_rate": 0.10}
    )
    quote = c.env["fix.seller.quote"].create(
        {"marketplace_order_id": order.id, "seller_id": seller.id, "quoted_price": gross,
         "company_id": c.company.id}
    )
    order.write({"selected_quote_id": quote.id, "state": "commissioned"})
    return seller, order


def test_bridge_c_commission_earned_records_one_ledger_row(c):
    seller, order = _commissioned_order(c)
    event = {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
    Ledger = c.env["fix.commission.ledger"]
    out = Ledger.consume_commission_earned(event)
    row = Ledger.browse(out["id"])
    assert out["created"] and row.marketplace_order_id == order and row.state == "earned"
    assert row.seller_partner_id == c.payee2 and row.gross_amount == 50000.0
    assert abs(row.commission_amount - 5000.0) < 0.01
    assert Ledger.consume_commission_earned(event) == {"id": row.id, "created": False}
    assert Ledger.consume_commission_earned(
        {"aggregate": "fix.referral", "aggregate_id": 1}
    ) == {"skipped": "fix.referral"}


def test_payout_run_skips_a_seller_on_payout_hold(c):
    seller, _order = _commissioned_order(c)
    _r, partner_row = accrued_referral(c)
    held_row = system_row(c, 30000.0, 0.10, payee=c.payee2, source_type="partner_referral")
    seller.write({"payout_hold": True})
    run = as_(c, c.acct)["fix.payout.run"].create({"period": "2026-10", "company_id": c.company.id})
    run.action_collect_accrued()
    assert partner_row in run.commission_ids and held_row not in run.commission_ids
    run.write({"commission_ids": [(4, held_row.id)]})
    with pytest.raises(UserError, match="payout hold"):
        run.action_prepare()
