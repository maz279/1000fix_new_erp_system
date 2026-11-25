# A08 · M20 Accounts Receivable — the control suite (B4 remediation).
#
# One test per gap probe of working/A08_evidence/probes/m20/probe_m20.py,
# named after the probe id: the same attack, run as a NON-ADMIN user holding
# the real finance role (created in the transaction), now REFUSED; plus the
# proper path — the legitimate maker and checker can still do the job.
#   acct / acct2 : account.group_account_user (Accountant / Finance Officer)
#   mgr / mgr2   : account.group_account_manager (Accounting Administrator)
#   billing      : account.group_account_invoice (Billing clerk: raises drafts)
#   itadmin      : base.group_system only (IT administrator, no finance role)
#   plain        : base.group_user only
import json
import types
import uuid
from datetime import date, timedelta

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GL_CODES = {
    "ar": ("121000", "asset_receivable"),
    "revenue": ("400000", "income"),
    "vat_output": ("211000", "liability_current"),
    "writeoff_expense": ("630000", "expense"),
    "cash": ("101401", "asset_cash"),
    "bank": ("101402", "asset_cash"),
    "channel_mfs": ("251000", "liability_current"),
    "vds_receivable": ("132000", "asset_current"),
    "deferred_revenue": ("212000", "liability_current"),
    "ecl_expense": ("630500", "expense"),
    "ecl_provision": ("121900", "asset_receivable"),
}
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
BIL = "account.group_account_invoice"


class Ctx:
    pass


@pytest.fixture
def c_raw(odoo_env):
    env0 = odoo_env
    tag = uuid.uuid4().hex[:5].upper()
    x = Ctx()
    company = env0["res.company"].create({"name": "B4M20 Co %s" % tag, "vat": "1234567890123"})
    env = env0(context=dict(env0.context, allowed_company_ids=company.ids))
    x.env, x.company, x.tag = env, company, tag
    x.ou = env["operating.unit"].create(
        {
            "name": "B4M20 OU %s" % tag,
            "code": "B4%s" % tag[:4],
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    x.journal = env["account.journal"].create(
        {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
    )
    Account = env["account.account"].with_company(company)
    x.acc = {
        role: Account.create(
            {
                "name": "%s %s" % (role, code),
                "code": code,
                "account_type": t,
                "company_ids": [(6, 0, company.ids)],
            }
        )
        for role, (code, t) in GL_CODES.items()
    }
    x.customer = env["res.partner"].create({"name": "B4M20 Cust %s" % tag, "vat": "9876543210123"})
    x.customer2 = env["res.partner"].create({"name": "B4M20 Cust2 %s" % tag})

    def user(login, *groups):
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "%s %s" % (login, tag),
                    "login": "%s-%s@b4m20.test" % (login, tag),
                    "company_id": company.id,
                    "company_ids": [(6, 0, company.ids)],
                    "assigned_operating_unit_ids": [(6, 0, x.ou.ids)],
                    "default_operating_unit_id": x.ou.id,
                    "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
                }
            )
        )

    x.acct = user("acct", ACC)
    x.acct2 = user("acct2", ACC)
    x.mgr = user("mgr", MGR)
    x.mgr2 = user("mgr2", MGR)
    x.billing = user("billing", BIL)
    x.itadmin = user("itadmin", "base.group_system")
    x.plain = user("plain")
    return x


@pytest.fixture
def c(c_raw):
    """c_raw with the company's invoice / Mushak sequences already drawn and
    the cheque-in-hand account a cheque receipt stages into. The real chart
    carries it as 16556556 (the AR engine's default for that role); a test
    template built on another chart does not, and a cheque receipt then
    refuses before reaching the behaviour under test."""
    c_raw.env["fix.ar.invoice"]._invoice_sequence(c_raw.company)
    c_raw.env["fix.ar.invoice"]._mushak_sequence(c_raw.company)
    Account = c_raw.env["account.account"].with_company(c_raw.company)
    if not Account.search([("code", "=", "16556556")], limit=1):
        Account.create(
            {
                "name": "Cheque In Hand",
                "code": "16556556",
                "account_type": "asset_cash",
                "company_ids": [(6, 0, c_raw.company.ids)],
            }
        )
    return c_raw


def as_(c, user):
    return c.env(user=user.id)


def ecl_rates(c):
    """The approved IFRS 9 loss rates a run stamps at Compute (M20-5)."""
    rates = as_(c, c.mgr)["fix.ar.ecl.rate"].create(
        {
            "name": "ECL %s" % c.tag,
            "company_id": c.company.id,
            "date_from": date(2020, 1, 1),
            "rate_current": 0.5,
            "rate_1_30": 2.0,
            "rate_31_60": 10.0,
            "rate_61_90": 25.0,
            "rate_90_plus": 50.0,
            "basis_note": "control suite",
        }
    )
    rates.with_user(c.mgr2).action_approve()
    return rates


def inv(c, maker=None, taxable=10000.0, issue=True, when=None, issuer=None, **line):
    """A manual invoice raised by `maker` and issued by a second person."""
    maker = maker or c.acct
    vals = {"customer_id": c.customer.id, "operating_unit_id": c.ou.id, "company_id": c.company.id}
    if when:
        vals["invoice_date"] = when
    i = as_(c, maker)["fix.ar.invoice"].create_manual_invoice(
        vals,
        [dict({"description": "Job", "taxable_amount": taxable}, **line)],
        reason_code="B4 test",
    )
    if issue:
        i.with_user(issuer or (c.acct2 if maker != c.acct2 else c.acct)).action_issue()
    return i


def cn(c, user, invoice, amount, reason="goodwill"):
    return as_(c, user)["fix.credit.note"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "invoice_id": invoice.id,
            "amount": amount,
            "reason_code": reason,
        }
    )


def rcpt(c, user, amount, method="cash", confirm=True, customer=None, **kw):
    r = as_(c, user)["fix.ar.receipt"].create(
        dict(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "customer_id": (customer or c.customer).id,
                "amount": amount,
                "method": method,
            },
            **kw,
        )
    )
    if confirm:
        r.action_confirm()
    return r


def lines(move):
    return sorted(
        (ln.account_id.with_company(move.company_id).code, ln.debit, ln.credit)
        for ln in move.line_ids
    )


def inbox_approve(c, record, user):
    """Approve `record` from `user`'s M63 inbox task (the routed path)."""
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


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
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


# ============================================================ reference runs
def test_ref_01_accountant_issues_and_gl_posts(c):
    """Proper path: one accountant raises, a colleague issues; Mushak 6.3 + balanced AR posting."""
    i = inv(c, c.acct)
    assert i.state == "issued" and i.mushak_id and i.posted_move_id
    assert i.issued_by_id == c.acct2
    assert lines(i.posted_move_id) == sorted(
        [("121000", 11500.0, 0.0), ("400000", 0.0, 10000.0), ("211000", 0.0, 1500.0)]
    )
    assert i.mushak_id.posted and i.mushak_id.vat_amount == 1500.0


def test_ref_02_receipt_confirm_posts_cash_against_ar(c):
    i = inv(c)
    r = rcpt(c, c.acct, 11500.0)
    assert lines(r.posted_move_id) == sorted([("101401", 11500.0, 0.0), ("121000", 0.0, 11500.0)])
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0}
    )
    assert i.state == "paid"


# ============================================================ credit notes (S3)
def test_m20_01_credit_note_maker_is_not_checker(c):
    """The raiser never approves, within the band or above it; a colleague /
    the Accounting Administrator does, and only then the note issues."""
    i = inv(c, c.acct, 100000.0)
    small = cn(c, c.acct, i, 5000.0)
    small.action_submit()
    assert small.state == "pending_approval" and not small.approved_by
    with pytest.raises(REFUSED):
        small.action_approve()
    with pytest.raises(REFUSED):
        small.action_issue()
    small.with_user(c.acct2).action_approve()
    assert small.state == "approved" and small.approved_by == c.acct2
    small.action_issue()
    assert small.state == "issued" and small.posted_move_id

    big = cn(c, c.acct, i, 20000.0)
    big.action_submit()
    assert big.approval_state == "pending"
    with pytest.raises(REFUSED):
        big.action_approve()
    with pytest.raises(REFUSED):
        big.with_user(c.acct2).action_approve()
    inbox_approve(c, big, c.mgr)
    assert big.state == "approved" and big.approved_by == c.mgr
    big.action_issue()
    assert big.state == "issued"


def test_m20_02_split_credit_notes_reach_the_cumulative_tier(c):
    """Three 9,000 notes on one invoice: the second's tier is cumulative (18,000)
    and goes to the Accounting Administrator, not a direct approval."""
    i = inv(c, c.acct, 100000.0)
    first = cn(c, c.acct, i, 9000.0)
    first.action_submit()
    assert first._dofa_current_tier() == "tier_0"
    second = cn(c, c.acct, i, 9000.0)
    second.action_submit()
    assert second.tier_basis_amount == 18000.0
    assert second._dofa_current_tier() != "tier_0" and second.approval_state == "pending"
    with pytest.raises(REFUSED):
        second.with_user(c.acct2).action_approve()


def test_m20_03_cumulative_over_credit_refused(c):
    i = inv(c)
    n1 = cn(c, c.acct, i, 6000.0)
    n1.action_submit()
    n2 = cn(c, c.acct, i, 11000.0)
    with pytest.raises(UserError, match="never exceed"):
        n2.action_submit()
    assert i.credited_amount <= i.total_payable


def test_m20_04_accountant_cannot_approve_above_the_band(c):
    i = inv(c, c.acct, 100000.0)
    n = cn(c, c.acct, i, 30000.0)
    n.action_submit()
    assert n.state == "pending_approval"
    with pytest.raises(UserError):
        n.with_user(c.acct2).action_approve()


def test_m20_05_finance_manager_approves_above_band_it_admin_cannot(c):
    i = inv(c, c.acct, 100000.0)
    n = cn(c, c.acct, i, 30000.0)
    n.action_submit()
    req = n.approval_request_id.sudo()
    assigned = req.task_ids.mapped("assigned_user_id")
    assert c.mgr in assigned and c.itadmin not in assigned and c.acct not in assigned
    with pytest.raises(REFUSED):
        n.with_user(c.itadmin).action_approve()
    inbox_approve(c, n, c.mgr)
    assert n.state == "approved" and n.dofa_approved_by == c.mgr


def test_m20_06_credit_note_state_cannot_be_written(c):
    i = inv(c, c.acct, 100000.0)
    n = cn(c, c.acct, i, 50000.0)
    with pytest.raises(UserError):
        n.write({"state": "issued"})
    assert n.state == "draft" and i.credited_amount == 0.0


def test_m20_07_forged_approval_refused(c):
    i = inv(c, c.acct, 100000.0)
    n = cn(c, c.acct, i, 50000.0)
    with pytest.raises(UserError):
        n.write({"state": "approved", "approved_by": c.mgr.id})
    with pytest.raises(UserError):
        n.action_issue()


def test_m20_08_amount_frozen_once_submitted(c):
    i = inv(c, c.acct, 300000.0)
    n = cn(c, c.acct, i, 8000.0)
    n.action_submit()
    n.with_user(c.acct2).action_approve()
    with pytest.raises(UserError):
        n.write({"amount": 250000.0})
    n.action_issue()
    assert i.credited_amount == 8000.0


def test_m20_09_billing_clerk_raises_drafts_accountant_decides(c):
    """M20-15 role split: Billing raises a draft invoice and a credit note;
    it cannot issue, confirm or approve — an Accountant does."""
    draft = inv(c, c.billing, issue=False)
    with pytest.raises(AccessError):
        draft.with_user(c.billing).action_issue()
    draft.with_user(c.acct).action_issue()
    assert draft.state == "issued"
    n = cn(c, c.billing, draft, 1000.0)
    n.action_submit()
    with pytest.raises(REFUSED):
        n.with_user(c.billing).action_approve()
    n.with_user(c.acct).action_approve()
    r = rcpt(c, c.billing, 100.0, confirm=False)
    with pytest.raises(AccessError):
        r.with_user(c.billing).action_confirm()


def test_m20_10_plain_user_cannot_create_credit_note(c):
    i = inv(c)
    with pytest.raises(AccessError):
        cn(c, c.plain, i, 100.0)


# ============================================================ write-off
def test_m20_11_write_off_needs_a_second_person(c):
    i = inv(c, c.acct, 8000.0)
    wo = i.with_user(c.acct).action_write_off(reason="uncollectable", recovery_history="3 calls")
    assert i.state == "issued" and wo.state == "requested"
    with pytest.raises(REFUSED):
        wo.with_user(c.acct).action_approve()
    wo.with_user(c.acct2).action_approve()
    assert wo.state == "posted" and i.state == "written_off" and wo.fin_approved_by_id == c.acct2


def test_m20_12_large_write_off_by_finance_manager_not_it_admin(c):
    i = inv(c, c.acct, 100000.0)
    wo = i.with_user(c.acct).action_write_off(reason="big loss", recovery_history="legal notice")
    assert wo.approval_state == "pending"
    with pytest.raises(REFUSED):
        wo.with_user(c.itadmin).action_approve()
    with pytest.raises(REFUSED):
        wo.with_user(c.acct2).action_approve()
    inbox_approve(c, wo, c.mgr)
    assert wo.state == "posted" and i.state == "written_off"


def test_m20_13_write_off_state_cannot_be_written(c):
    i = inv(c, c.acct, 100000.0)
    with pytest.raises(UserError):
        i.with_user(c.acct).write({"state": "written_off"})
    assert i.state == "issued"


def test_m20_14_write_off_uses_the_ecl_allowance_first(c):
    ecl_rates(c)
    i = inv(c, c.acct, 10000.0, when=date.today() - timedelta(days=200))
    run = as_(c, c.acct)["fix.ar.impairment"].create(
        {
            "company_id": c.company.id,
            "journal_id": c.journal.id,
            "expense_account_id": c.acc["ecl_expense"].id,
            "provision_account_id": c.acc["ecl_provision"].id,
        }
    )
    run.action_compute()
    run.with_user(c.mgr).action_post()
    assert run.total_provision == 5750.0
    wo = i.with_user(c.acct).action_write_off(reason="bankrupt", recovery_history="liquidator")
    inbox_approve(c, wo, c.mgr2)
    assert wo.allowance_amount == 5750.0 and wo.expense_amount == 5750.0
    assert lines(wo.move_id) == sorted(
        [("121900", 5750.0, 0.0), ("630000", 5750.0, 0.0), ("121000", 0.0, 11500.0)]
    )


# ============================================================ IFRS 9 impairment (F6)
def test_m20_15_plain_user_cannot_touch_the_ecl_run(c):
    with pytest.raises(AccessError):
        as_(c, c.plain)["fix.ar.impairment"].create(
            {"company_id": c.company.id, "journal_id": c.journal.id}
        )
    from odoo.addons.cd_p03_portal.controllers.a08 import m20 as surf

    out = surf.ecl_provision(as_(c, c.plain))
    assert not out["rows"] and "finance roles" in out["notes"][0]


def test_m20_16_existing_provision_is_measured_not_typed(c):
    ecl_rates(c)
    inv(c, c.acct, 10000.0, when=date.today() - timedelta(days=200))
    run = as_(c, c.acct)["fix.ar.impairment"].create(
        {
            "company_id": c.company.id,
            "journal_id": c.journal.id,
            "expense_account_id": c.acc["ecl_expense"].id,
            "provision_account_id": c.acc["ecl_provision"].id,
        }
    )
    run.action_compute()
    with pytest.raises(UserError):
        run.write({"existing_provision": 1000000.0})
    with pytest.raises(UserError):
        run.write({"rate_90_plus": 0.01})
    run.with_user(c.mgr).action_post()
    assert lines(run.move_id) == sorted([("630500", 5750.0, 0.0), ("121900", 0.0, 5750.0)])


def test_m20_17_ecl_post_is_a_review_by_another_administrator(c):
    ecl_rates(c)
    inv(c, c.acct, 10000.0, when=date.today() - timedelta(days=200))
    run = as_(c, c.mgr)["fix.ar.impairment"].create(
        {
            "company_id": c.company.id,
            "journal_id": c.journal.id,
            "expense_account_id": c.acc["ecl_expense"].id,
            "provision_account_id": c.acc["ecl_provision"].id,
        }
    )
    run.action_compute()
    with pytest.raises(REFUSED):
        run.with_user(c.acct).action_post()
    with pytest.raises(UserError):
        run.action_post()
    run.with_user(c.mgr2).action_post()
    assert run.state == "posted" and run.posted_by_id == c.mgr2 and run.move_id


# ============================================================ receipts & allocation
def test_m20_18_batch_over_allocation_refused(c):
    i1, i2 = inv(c), inv(c)
    r = rcpt(c, c.acct, 11500.0)
    with pytest.raises(UserError):
        as_(c, c.acct)["fix.ar.allocation"].create(
            [
                {"receipt_id": r.id, "invoice_id": i1.id, "amount": 11500.0},
                {"receipt_id": r.id, "invoice_id": i2.id, "amount": 11500.0},
            ]
        )


def test_m20_19_allocation_write_checked(c):
    i = inv(c)
    r = rcpt(c, c.acct, 1000.0)
    a = as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 100.0}
    )
    with pytest.raises(UserError):
        a.write({"amount": 11500.0})
    a.write({"amount": 900.0})
    assert i.amount_paid == 900.0


def test_m20_20_receipt_amount_frozen_after_posting(c):
    r = rcpt(c, c.acct, 1000.0)
    with pytest.raises(UserError):
        r.write({"amount": 11500.0})
    assert r.amount == 1000.0


def test_m20_21_receipt_state_cannot_be_forged(c):
    r = rcpt(c, c.acct, 11500.0, confirm=False)
    with pytest.raises(UserError):
        r.write({"state": "confirmed"})
    with pytest.raises(UserError):
        as_(c, c.acct)["fix.ar.receipt"].create(
            {
                "company_id": c.company.id,
                "customer_id": c.customer.id,
                "amount": 5.0,
                "state": "confirmed",
            }
        )


def test_m20_22_invoice_paid_only_with_evidence(c):
    i = inv(c)
    with pytest.raises(UserError):
        i.with_user(c.acct).write({"state": "paid"})
    with pytest.raises(UserError):
        i.with_user(c.acct).action_register_paid()


def test_m20_23_unlink_allocation_of_paid_invoice_refused(c):
    i = inv(c)
    r = rcpt(c, c.acct, 11500.0)
    a = as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0}
    )
    with pytest.raises(UserError):
        a.unlink()


def test_m20_24_cross_customer_allocation_refused(c):
    i = inv(c)
    r = rcpt(c, c.acct, 11500.0, customer=c.customer2)
    with pytest.raises(UserError):
        as_(c, c.acct)["fix.ar.allocation"].create(
            {"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0}
        )


def test_m20_25_cash_nid_must_be_a_national_id(c):
    with pytest.raises(UserError):
        rcpt(c, c.acct, 60000.0)
    with pytest.raises(UserError):
        rcpt(c, c.acct, 60000.0, nid_captured="0")
    r = rcpt(c, c.acct, 60000.0, nid_captured="1234567890")
    assert r.state == "confirmed"


# ============================================================ disputes & dunning
def test_m20_26_cumulative_disputes_capped_at_open_amount(c):
    i = inv(c)
    D = as_(c, c.acct)["fix.ar.dispute"]
    D.create({"invoice_id": i.id, "amount_disputed": 11500.0, "reason": "a"})
    with pytest.raises(UserError):
        D.create({"invoice_id": i.id, "amount_disputed": 11500.0, "reason": "b"})


def test_m20_27_open_dispute_holds_dunning(c):
    i = inv(c, when=date.today() - timedelta(days=90))
    as_(c, c.acct)["fix.ar.dispute"].create(
        {"invoice_id": i.id, "amount_disputed": 11500.0, "reason": "wrong part"}
    )
    c.env["fix.dunning"].action_run_dunning()
    assert not c.env["fix.dunning"].search([("invoice_id", "=", i.id)])


def test_m20_28_dispute_closed_by_a_second_person_with_an_outcome(c):
    i = inv(c, when=date.today() - timedelta(days=90))
    d = as_(c, c.acct)["fix.ar.dispute"].create(
        {"invoice_id": i.id, "amount_disputed": 11500.0, "reason": "x"}
    )
    with pytest.raises(UserError):
        d.action_resolve(note="checked", outcome_code="rejected")
    with pytest.raises(UserError):
        d.with_user(c.acct2).action_resolve(note="checked")
    with pytest.raises(UserError):
        d.write({"state": "resolved"})
    d.with_user(c.acct2).action_resolve(note="price confirmed", outcome_code="rejected")
    assert d.state == "resolved" and d.outcome_code == "rejected" and d.resolved_by == c.acct2


def test_m20_29_dunning_suppression_is_kept_with_who_why_until(c):
    i = inv(c, when=date.today() - timedelta(days=90))
    c.env["fix.dunning"].action_run_dunning()
    run = c.env["fix.dunning"].search([("invoice_id", "=", i.id)])
    run.with_user(c.acct).action_suppress("payment_plan")
    c.env["fix.dunning"].action_run_dunning()
    assert run.suppressed and run.suppression_reason == "payment_plan"
    assert run.suppressed_by_id == c.acct and run.suppressed_until > date.today()
    with pytest.raises(UserError):
        run.with_user(c.acct).write({"suppressed": False})


def test_m20_30_credit_hold_released_by_a_senior_role(c):
    prof = as_(c, c.acct)["fix.credit.profile"].create(
        {
            "company_id": c.company.id,
            "customer_id": c.customer.id,
            "credit_hold": True,
            "hold_reason": "overdue 90+",
        }
    )
    with pytest.raises(UserError):
        inv(c, c.acct)
    with pytest.raises(AccessError):
        prof.action_toggle_hold()
    with pytest.raises(UserError):
        prof.write({"credit_hold": False})
    prof.with_user(c.mgr).action_toggle_hold()
    assert not prof.credit_hold and prof.hold_by == c.mgr
    assert inv(c, c.acct).state == "issued"


# ============================================================ VDS (Mushak 6.6 received)
def vds(c, user, invoice, amount, no=None):
    return as_(c, user)["fix.vds.certificate.received"].create(
        {
            "invoice_id": invoice.id,
            "certificate_no": no or "M66-%s" % uuid.uuid4().hex[:6],
            "certificate_date": date.today(),
            "vds_amount": amount,
        }
    )


def test_m20_31_vds_above_invoice_vat_refused(c):
    i = inv(c)
    with pytest.raises(ValidationError):
        vds(c, c.acct, i, 1500.01)


def test_m20_32_vds_preparer_cannot_verify(c):
    i = inv(c)
    v = vds(c, c.acct, i, 1500.0)
    with pytest.raises(AccessError):
        v.action_verify()


def test_m20_33_vds_preparer_cannot_be_rewritten(c):
    i = inv(c)
    v = vds(c, c.acct, i, 1500.0)
    with pytest.raises(UserError):
        v.write({"prepared_by_id": c.acct2.id})
    with pytest.raises(AccessError):
        v.action_verify()


def test_m20_34_vds_state_cannot_be_forged(c):
    i = inv(c)
    v = vds(c, c.acct, i, 1500.0)
    with pytest.raises(UserError):
        v.write({"state": "settled"})
    assert i.vds_settled_amount == 0.0


def test_m20_35_vds_amount_pinned_after_verification(c):
    i = inv(c)
    v = vds(c, c.acct, i, 100.0)
    v.with_user(c.acct2).action_verify()
    with pytest.raises(UserError):
        v.write({"vds_amount": 1500.0})
    v.action_settle()
    assert lines(v.settled_move_id) == sorted([("132000", 100.0, 0.0), ("121000", 0.0, 100.0)])


def test_m20_36_vds_claimed_only_by_a_filed_9_1_return(c):
    i = inv(c)
    v = vds(c, c.acct, i, 1500.0)
    v.with_user(c.acct2).action_verify()
    v.action_settle()
    with pytest.raises(UserError):
        v.action_mark_claimed("anything")
    assert v.state == "settled"
    ret = c.env["fix.vat.return"].create(
        {
            "company_id": c.company.id,
            "period": v.period,
            "state": "filed",
            "vds_certificate_ids": json.dumps([v.id]),
        }
    )
    v.sudo().action_mark_claimed("Mushak 9.1 %s" % v.period)
    assert v.state == "claimed" and v.claimed_return_id == ret


# ============================================================ invoice rules
def test_m20_37_manual_invoice_vat_is_m51s(c):
    with pytest.raises(UserError, match="M51"):
        inv(c, c.acct, 10000.0, vat_amount=1.0)
    i = inv(c, c.acct, 10000.0)
    assert i.vat_amount == 1500.0 and i.mushak_id.vat_amount == 1500.0


def test_m20_38_issued_invoice_is_frozen(c):
    i = inv(c)
    with pytest.raises(UserError):
        i.line_ids.with_user(c.acct).write({"taxable_amount": 1.0})
    with pytest.raises(UserError):
        i.with_user(c.acct).write({"customer_id": c.customer2.id})
    assert i.total_payable == 11500.0


def test_m20_39_consolidated_bill_takes_issued_invoices_only(c):
    issued = inv(c)
    draft = inv(c, issue=False)
    b = as_(c, c.acct)["fix.ar.consolidated.bill"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": c.customer.id,
            "bill_ref": "CB-1",
            "period_start": date.today() - timedelta(days=1),
            "period_end": date.today() + timedelta(days=1),
        }
    )
    b.action_generate()
    assert draft not in b.invoice_ids and issued in b.invoice_ids
    b2 = as_(c, c.acct)["fix.ar.consolidated.bill"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": c.customer.id,
            "bill_ref": "CB-2",
            "period_start": date.today(),
            "period_end": date.today(),
            "invoice_ids": [(6, 0, draft.ids)],
        }
    )
    with pytest.raises(UserError):
        b2.action_generate()


def test_m20_40_payment_link_asks_the_residual_and_expires(c):
    i = inv(c)
    r = rcpt(c, c.acct, 5000.0)
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 5000.0}
    )
    link = as_(c, c.acct)["fix.ar.payment.link"].create({"invoice_id": i.id})
    assert link.amount == i.amount_residual == 6500.0
    with pytest.raises(UserError):
        link.write({"amount": 1.0})
    link.sudo().write({"expires_at": fields_now() - timedelta(minutes=1)})
    assert c.env["fix.ar.payment.link"]._cron_expire() >= 1
    assert link.state == "expired"


def fields_now():
    from odoo import fields

    return fields.Datetime.now()


def test_m20_41_issue_into_locked_period_refused_or_redated(c):
    lock = date.today() - timedelta(days=10)
    c.company.sudo().write({"fiscalyear_lock_date": lock})
    try:
        i = inv(c, when=date.today() - timedelta(days=40))
    except REFUSED:
        return
    mv = i.posted_move_id
    assert mv and mv.date > lock


def test_m20_42_cancelling_an_issued_invoice_needs_an_administrator(c):
    i = inv(c, c.acct, 100000.0)
    with pytest.raises(AccessError):
        i.with_user(c.acct).action_cancel(reason="duplicate")
    i.with_user(c.mgr).action_cancel(reason="duplicate issuance")
    assert i.state == "cancelled" and i.cancelled_by_id == c.mgr


# ============================================================ P03 path
def test_m20_43_p03_cannot_forge_credit_note_state(c, p03):
    i = inv(c, c.acct, 100000.0)
    n = cn(c, c.acct, i, 50000.0)
    out = p03.write(c.acct, model="fix.credit.note", record_id=n.id, values={"state": "issued"})
    n.invalidate_recordset()
    assert out.get("error") and n.state == "draft"


def test_m20_44_p03_plain_user_cannot_post_ecl(c, p03):
    run = c.env["fix.ar.impairment"].create(
        {"company_id": c.company.id, "journal_id": c.journal.id}
    )
    out = p03.write(
        c.plain,
        model="fix.ar.impairment",
        record_id=run.id,
        values={"state": "posted", "rate_90_plus": 0.0, "existing_provision": 5000000.0},
    )
    run.invalidate_recordset()
    assert out.get("error") and run.state == "draft" and not run.existing_provision


def test_m20_45_p03_cannot_verify_vds(c, p03):
    i = inv(c)
    v = vds(c, c.acct, i, 1500.0)
    out = p03.write(
        c.acct, model="fix.vds.certificate.received", record_id=v.id, values={"state": "verified"}
    )
    v.invalidate_recordset()
    assert out.get("error") and v.state == "draft"


# ============================================================ wiring
def test_m20_46_first_issue_in_a_company_works_for_an_accountant(c_raw):
    i = inv(c_raw, c_raw.acct)
    assert i.state == "issued" and i.name != "New"


def test_m20_47_p03_refuses_readonly_stamp(c, p03):
    i = inv(c, c.acct, 100000.0)
    n = cn(c, c.acct, i, 50000.0)
    out = p03.write(
        c.acct, model="fix.credit.note", record_id=n.id, values={"approved_by": c.mgr.id}
    )
    n.invalidate_recordset()
    assert out.get("error") and not n.approved_by


def test_m20_crons_and_sequences_ship(c):
    """The payment-link expiry job and the write-off numbering exist."""
    cron = c.env.ref("cd_billing_engine.ir_cron_ar_payment_link_expiry")
    assert cron.active and "_cron_expire" in cron.code
    assert c.env.ref("cd_billing_engine.seq_fix_ar_writeoff").code == "fix.ar.writeoff"


def test_m20_ar_invoice_api_for_disposals(c):
    """B4 -> B5 contract: a system invoice for an approved source, issued with
    M51 VAT and credited to the account the caller names; idempotent."""
    source = c.env["res.partner"].create({"name": "Disposal source %s" % c.tag})
    proceeds = (
        c.env["account.account"]
        .with_company(c.company)
        .create(
            {
                "name": "Disposal proceeds",
                "code": "480100",
                "account_type": "income_other",
                "company_ids": [(6, 0, c.company.ids)],
            }
        )
    )
    Invoice = as_(c, c.acct)["fix.ar.invoice"]
    i = Invoice._fix_ar_invoice_from_source(
        source,
        c.customer,
        [{"description": "Sale of laptop", "taxable_amount": 20000.0}],
        "Disposal approved",
        credit_account=proceeds,
        operating_unit=c.ou,
    )
    assert i.state == "issued" and i.vat_amount == 3000.0
    assert ("480100", 0.0, 20000.0) in lines(i.posted_move_id)
    assert (
        Invoice._fix_ar_invoice_from_source(
            source, c.customer, [{"description": "x", "taxable_amount": 1.0}], "again"
        )
        == i
    )


# ============================================================ cheque.bounced (B1 -> B4)
def _bounced_cheque(c, receipt, cleared=True):
    """The M50 register's returned cheque (as treasury leaves it after
    action_bounce): for a cleared cheque B1 has posted Dr returned cheques /
    Cr bank (bounce_move_id)."""
    vals = {
        "company_id": c.company.id,
        "operating_unit_id": c.ou.id,
        "direction": "received",
        "cheque_no": receipt.reference,
        "partner_id": c.customer.id,
        "amount": receipt.amount,
        "cheque_date": date.today(),
        "source_ref": receipt.name,
        "state": "bounced",
        "bounce_reason": "Insufficient funds",
    }
    if cleared:
        vals["bounce_move_id"] = receipt.posted_move_id.id  # any posted entry stands in for B1's
    return c.env["fix.cheque"].create(vals)


def _cheque_event(chq):
    return {
        "aggregate": "fix.cheque",
        "aggregate_id": chq.id,
        "payload": {"cheque_no": chq.cheque_no, "direction": "received", "amount": chq.amount},
    }


def test_m20_cheque_bounced_reopens_the_invoice_once(c):
    returned = (
        c.env["account.account"]
        .with_company(c.company)
        .create(
            {
                "name": "Returned cheques",
                "code": "131900",
                "account_type": "asset_receivable",
                "company_ids": [(6, 0, c.company.ids)],
            }
        )
    )
    i = inv(c)
    r = rcpt(c, c.acct, 11500.0, method="cheque", reference="CHQ-778899")
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0}
    )
    assert i.state == "paid"
    chq = _bounced_cheque(c, r)
    Receipt = c.env["fix.ar.receipt"]
    # the consumer runs only from the relay, and never to a guessed account
    with pytest.raises(AccessError):
        as_(c, c.acct)["fix.ar.receipt"].consume_cheque_bounced(_cheque_event(chq))
    c.env["ir.config_parameter"].set_param("cd_cash_position.account_code.cheque_returned", False)
    with pytest.raises(UserError, match="cheque_returned"):
        Receipt.consume_cheque_bounced(_cheque_event(chq))
    c.env["ir.config_parameter"].set_param(
        "cd_cash_position.account_code.cheque_returned", "131900"
    )
    out = Receipt.consume_cheque_bounced(_cheque_event(chq))
    assert out["created"] and r.state == "reversed" and r.bounced_cheque_id == chq
    i.invalidate_recordset()
    assert i.state == "issued" and i.amount_residual == 11500.0 and not i.allocation_ids
    # Dr AR / Cr returned cheques — the bank is not credited a second time
    assert lines(r.bounce_move_id) == sorted([("121000", 11500.0, 0.0), ("131900", 0.0, 11500.0)])
    assert r.bounce_move_id.state == "posted" and returned
    # a replay changes nothing
    again = Receipt.consume_cheque_bounced(_cheque_event(chq))
    assert again == {"model": "fix.ar.receipt", "id": r.id, "created": False}
    assert c.env["account.move"].search_count([("ref", "like", "CHEQUE RETURNED CHQ-778899")]) == 1
    cons = c.env.ref("cd_billing_engine.consumer_cheque_bounced_reopen_ar")
    assert cons.event_type == "cheque.bounced" and cons.method == "consume_cheque_bounced"


def test_m20_cheque_bounced_before_clearing_reverses_the_receipt_account(c):
    i = inv(c)
    r = rcpt(c, c.acct, 11500.0, method="cheque", reference="CHQ-112233")
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0}
    )
    chq = _bounced_cheque(c, r, cleared=False)
    c.env["fix.ar.receipt"].consume_cheque_bounced(_cheque_event(chq))
    # An uncleared cheque never reached the bank: the bounce credits back the
    # very account the receipt debited (since R1, 2026-11-09, a cheque is
    # staged on cheque-in-hand, 16556556 - no longer the bank 101402) and
    # re-opens the receivable.
    staged = [ln for ln in lines(r.posted_move_id) if ln[1] == 11500.0 and ln[0] != "121000"]
    assert [code for code, _dr, _cr in staged] == ["16556556"]
    assert lines(r.bounce_move_id) == sorted([("121000", 11500.0, 0.0), ("16556556", 0.0, 11500.0)])
    assert i.state == "issued"


def test_m20_forged_cheque_bounce_event_refused(c):
    i = inv(c)
    r = rcpt(c, c.acct, 11500.0, method="cheque", reference="CHQ-445566")
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0}
    )
    chq = _bounced_cheque(c, r)
    chq.sudo()._guarded().write({"state": "cleared"})
    with pytest.raises(UserError, match="not returned"):
        c.env["fix.ar.receipt"].consume_cheque_bounced(_cheque_event(chq))
    assert i.state == "paid" and r.state == "confirmed"


# ============================================================ A04 bridge entry points
def test_bridge_a_draft_invoice_from_an_external_source_is_idempotent(c):
    Invoice = c.env["fix.ar.invoice"]
    i = Invoice._fix_draft_invoice_from_source(
        "fix.contract.billing",
        "CB-2026-11-001",
        c.customer,
        [{"description": "AMC November", "taxable_amount": 8000.0}],
        "Contract billing, November",
        company=c.company,
        operating_unit=c.ou,
    )
    assert i.state == "draft" and i.source_ref == "CB-2026-11-001" and i.vat_amount == 1200.0
    again = Invoice._fix_draft_invoice_from_source(
        "fix.contract.billing",
        "CB-2026-11-001",
        c.customer,
        [{"description": "x", "taxable_amount": 1.0}],
        "replay",
        company=c.company,
    )
    assert again == i
    with pytest.raises(UserError):
        Invoice._fix_draft_invoice_from_source("fix.contract.billing", "", c.customer, [], "x")
    i.with_user(c.acct).action_issue()  # finance issues the draft
    assert i.state == "issued"


def test_bridge_b_credit_request_runs_the_ladder_and_the_cap(c):
    i = inv(c, c.acct, 10000.0)
    CN = c.env["fix.credit.note"]
    small = CN._fix_request_credit(i, 2000.0, "service_failure", note="OEM claim 77 rejected")
    assert small.state == "pending_approval" and not small.approved_by
    big = CN._fix_request_credit(i, 9000.0, "goodwill")
    assert big.approval_state == "pending" and big._dofa_current_tier() != "tier_0"
    with pytest.raises(UserError, match="never exceed"):
        CN._fix_request_credit(i, 1000.0, "goodwill")
