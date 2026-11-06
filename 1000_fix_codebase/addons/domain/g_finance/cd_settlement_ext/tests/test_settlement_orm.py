# cd_settlement_ext — live-ORM behaviour of M53: commission accrual (FF-91),
# SoD-gated payout runs paid through treasury (M50), statements,
# reconciliation and the seller settlement API. DoD-03 statutory set.
from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

D = Decimal
YEAR = date.today().year


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _user(env, login, *groups, partner=None):
    vals = {
        "name": login.replace("_", " ").title(),
        "login": f"{login}@settlement.test",
        "group_ids": [(6, 0, [env.ref(g).id for g in groups])],
    }
    if partner:
        vals["partner_id"] = partner.id
    return env["res.users"].create(vals)


COMPANY_ROUTING, COMPANY_ACCOUNT = "020270001", "1101000099887"


def _bank_account(env, partner, routing, account):
    bank = env["res.bank"].create({"name": f"{partner.name} Bank", "bic": routing})
    return env["res.partner.bank"].create(
        {"partner_id": partner.id, "acc_number": account, "bank_id": bank.id}
    )


def _seller(env, name, routing="060272531", account="2050123456789"):
    seller = env["res.partner"].create({"name": name})
    if account:
        _bank_account(env, seller, routing, account)
    return seller


def _commission(env, seller, gross, rate, tds=0.0, **vals):
    return env["fix.commission.ledger"].create(
        {
            "seller_partner_id": seller.id,
            "gross_amount": gross,
            "commission_rate": rate,
            "tds_amount": tds,
            **vals,
        }
    )


SETTLEMENT_CHART = {
    "101000": ("Customer Payment Clearing", "asset_cash"),
    "400100": ("Marketplace Commission Revenue", "income"),
    "200200": ("Marketplace Seller Payable", "liability_payable"),
    "210100": ("TDS Withheld Liability", "liability_current"),
}


def _settlement_chart(env, company):
    """The configured settlement accounts (the module no longer creates or
    guesses them) — created here only where the test company lacks them."""
    Account = env["account.account"].with_company(company)
    for code, (name, account_type) in SETTLEMENT_CHART.items():
        if not Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1):
            Account.create(
                {
                    "code": code,
                    "name": name,
                    "account_type": account_type,
                    "company_ids": [(6, 0, company.ids)],
                }
            )


@pytest.fixture
def book(odoo_env):
    """Seller A: 10,000.00 @10% (TDS 450.00) + 2,500.50 @10%; seller B:
    4,000.00 @5% (TDS 190.00). Net payable 8,550.00 + 2,250.45 + 3,610.00."""
    env = odoo_env
    _settlement_chart(env, env.company)
    # the paying company's own (originating) account
    _bank_account(env, env.company.partner_id, COMPANY_ROUTING, COMPANY_ACCOUNT)
    seller_a = _seller(env, "Bengal Gadget House")
    seller_b = _seller(env, "Sylhet Mobile Point", routing="175260162", account="0911100012345")
    c1 = _commission(env, seller_a, 10000.0, 0.10, tds=450.0, payment_id="PAY-1", rail="bKash")
    c2 = _commission(env, seller_a, 2500.5, 0.10)
    c3 = _commission(env, seller_b, 4000.0, 0.05, tds=190.0)
    return SimpleNamespace(env=env, seller_a=seller_a, seller_b=seller_b, c1=c1, c2=c2, c3=c3)


def _run(book, **vals):
    commissions = book.c1 | book.c2 | book.c3
    return book.env["fix.payout.run"].create(
        {"period": "2026-10", "commission_ids": [(6, 0, commissions.ids)], **vals}
    )


# --------------------------------------------------------------------------- commission ledger


class TestCommissionLedger:
    def test_commission_and_net_entitlement(self, book):
        assert book.c1.name.startswith(f"COM/{YEAR}/") and book.c1.name != f"COM/{YEAR}/New"
        assert _money(book.c1.commission_amount) == D("1000.00")
        assert _money(book.c1.net_payable) == D("8550.00")  # 10,000 - 1,000 - 450
        assert _money(book.c2.commission_amount) == D("250.05")  # 2,500.50 x 10%
        assert _money(book.c2.net_payable) == D("2250.45")
        assert book.c1.currency_id == book.env.ref("base.BDT")

    def test_explicit_reference_is_kept(self, book):
        c = _commission(book.env, book.seller_a, 100.0, 0.1, name="COM/MANUAL/1")
        assert c.name == "COM/MANUAL/1"

    def test_accrual_posts_ff91_split(self, book):
        book.c1.action_post_to_gl()
        move = book.c1.gl_move_id
        assert (book.c1.state, move.state) == ("accrued", "posted")
        lines = {line.name.split(":")[0]: line for line in move.line_ids}
        clearing = lines["Customer Receipt Clearing"]
        revenue = lines["Commission Revenue (FF-91)"]
        seller = lines["Seller Entitlement Liability"]
        # gross 10,000.00 Dr; commission 1,000.00 Cr revenue; 9,000.00 Cr seller (never gross to revenue)
        assert (_money(clearing.debit), _money(clearing.credit)) == (D("10000.00"), D("0.00"))
        assert (_money(revenue.debit), _money(revenue.credit)) == (D("0.00"), D("1000.00"))
        assert (_money(seller.debit), _money(seller.credit)) == (D("0.00"), D("9000.00"))
        # found by their configured codes - never by "any account of the type"
        assert clearing.account_id.code == "101000"
        assert revenue.account_id.code == "400100"
        assert seller.account_id.code == "200200"
        assert seller.partner_id == book.seller_a
        dims = book.env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])
        assert sorted(dims.mapped("cost_centre")) == ["CC-MKT", "CC-PAY", "CC-REV"]
        (event,) = _events(book.env, "commission.accrued", book.c1.id)
        assert (event["gross"], event["commission_amount"], event["seller_share"]) == (
            10000.0,
            1000.0,
            9000.0,
        )
        assert (event["payment_id"], event["rail"], event["move_id"]) == ("PAY-1", "bKash", move.id)
        # already accrued: skipped, no second move
        book.c1.action_post_to_gl()
        assert (
            book.env["account.move"].search_count([("ref", "=", f"COM-ACCRUAL-{book.c1.name}")])
            == 1
        )

    def test_accrual_in_a_company_without_chart_is_refused(self, odoo_env):
        """Regression: a company without the settlement accounts had them
        CREATED on the fly (or the posting silently landed on any account of
        the same type). The accrual is now refused, naming the account."""
        env = odoo_env
        company = env["res.company"].create({"name": "1000FiX Marketplace Ltd"})
        env["account.journal"].create(
            {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
        )
        ou = env["operating.unit"].create(
            {
                "name": "Mkt OU",
                "code": "MKT",
                "company_id": company.id,
                "partner_id": company.partner_id.id,
            }
        )
        # an income account of the right TYPE but the wrong code must not be used
        env["account.account"].create(
            {
                "code": "499999",
                "name": "Some other income",
                "account_type": "income",
                "company_ids": [(6, 0, company.ids)],
            }
        )
        seller = _seller(env, "Rangpur Electronics")
        c = _commission(env, seller, 2000.0, 0.10, company_id=company.id, operating_unit_id=ou.id)
        with pytest.raises(UserError, match="no GL account 101000"), env.cr.savepoint():
            c.action_post_to_gl()
        assert (c.state, c.gl_move_id) == ("earned", env["account.move"])
        _settlement_chart(env, company)
        c.action_post_to_gl()
        codes = sorted(c.gl_move_id.line_ids.with_company(company).mapped("account_id.code"))
        assert codes == ["101000", "200200", "400100"]
        assert set(
            env["fix.journal.dimension"]
            .search([("move_line_id", "in", c.gl_move_id.line_ids.ids)])
            .mapped("operating_unit_id")
            .ids
        ) == {ou.id}

    def test_accrual_without_a_general_journal_is_refused(self, odoo_env):
        env = odoo_env
        company = env["res.company"].create({"name": "1000FiX No-Journal Ltd"})
        _settlement_chart(env, company)
        seller = _seller(env, "Khulna Mobiles")
        c = _commission(env, seller, 1000.0, 0.10, company_id=company.id)
        with pytest.raises(UserError, match="no general"), env.cr.savepoint():
            c.action_post_to_gl()
        assert not env["account.journal"].search([("company_id", "=", company.id)])

    def test_account_code_is_configurable(self, book):
        book.env["account.account"].create(
            {
                "code": "400777",
                "name": "Commission income (alt chart)",
                "account_type": "income",
                "company_ids": [(6, 0, book.env.company.ids)],
            }
        )
        book.env["ir.config_parameter"].set_param(
            "cd_settlement_ext.account_code.commission_revenue", "400777"
        )
        book.c1.action_post_to_gl()
        revenue = book.c1.gl_move_id.line_ids.filtered(lambda line: line.credit == 1000.0)
        assert revenue.account_id.code == "400777"

    def test_accrued_entry_is_immutable_for_users(self, book):
        # Ledger writes belong to accounting users (a plain employee is read-only).
        clerk = _user(book.env, "settlement_clerk_mina", "account.group_account_user")
        book.c1.write({"state": "accrued"})
        with pytest.raises(UserError, match="LP-07 Violation"), book.env.cr.savepoint():
            book.c1.with_user(clerk).write({"gross_amount": 1.0})
        book.c1.with_user(clerk).write({"source_ref": "ORD-77"})  # non-financial field
        assert book.c1.source_ref == "ORD-77"
        book.c1.write({"commission_rate": 0.12})  # superuser contra-posting path
        assert _money(book.c1.commission_amount) == D("1200.00")


# --------------------------------------------------------------------------- payout run
#
# A08 F2 / FR-REV-034 (rewritten 4 Nov 2026): the run no longer pays on its
# own INT-007 rail or BEFTN file — those tests asserted the defect the audit
# found (M53 paid without treasury and "confirmed" on a typed reference). A
# run is prepared, approved from the M63 inbox by an Accounting
# Administrator who did not prepare it, pinned, released to M50 as one
# payment instruction per payee and completed by the imported bank
# statement debit.


def _confirm_bank(partner, routing):
    """M52 dual control (B2): the payee account confirmed by a second person."""
    bank = partner.bank_ids[:1]
    bank._fix_confirming().write({"fix_routing_number": routing})
    bank._fix_confirming()._fix_mark_confirmed("call-back on the number on file (test)", None)
    return bank


def _age(env, rows):
    """FLAW-12.2: marketplace rows are collectable once the 7-day buyer
    dispute window has passed — age them past it (as in TestEscrow)."""
    env.cr.execute(
        "UPDATE fix_commission_ledger SET create_date = create_date - interval '8 days' "
        "WHERE id IN %s",
        (tuple(rows.ids),),
    )
    rows.invalidate_recordset()
    rows._compute_escrow_release()
    rows.flush_recordset()


def _treasury(book):
    """Users and the paying bank account for the M50 leg."""
    env = book.env
    journal = env["account.journal"].create(
        {"name": "Payout Bank", "code": "PYB%s" % str(book.seller_a.id)[-2:], "type": "bank",
         "company_id": env.company.id}
    )
    param = env["ir.config_parameter"]
    param.set_param("cd_settlement_ext.payout_journal_code", journal.code)
    param.set_param("cd_cash_position.release_single_ceiling", "5000000")
    _confirm_bank(book.seller_a, "060272531")
    _confirm_bank(book.seller_b, "175260162")
    accrue = book.c1 | book.c2 | book.c3
    accrue.action_post_to_gl()
    _age(env, accrue)
    return SimpleNamespace(
        journal=journal,
        preparer=_user(env, "payout_prep_rahim", "base.group_user", "account.group_account_user"),
        clerk=_user(env, "treasury_clerk_mitu", "base.group_user", "account.group_account_user"),
        approver=_user(env, "fin_mgr_karim", "base.group_user", "account.group_account_manager"),
        releaser=_user(env, "fin_mgr_nasrin", "base.group_user", "account.group_account_manager"),
    )


def _inbox_approve(env, record, user):
    task = env["fix.workflow.task"].sudo().search(
        [("res_model", "=", record._name), ("res_id", "=", record.id),
         ("state", "=", "pending"), ("assigned_user_id", "=", user.id)],
        limit=1,
    )
    assert task, "no M63 task for %s" % user.login
    task.with_user(user).action_approve()
    record.invalidate_recordset()


def _approved(book, t):
    run = book.env["fix.payout.run"].with_user(t.preparer).create(
        {"period": "2026-10", "company_id": book.env.company.id}
    )
    run.action_collect_accrued()
    run.action_prepare()
    _inbox_approve(book.env, run, t.approver)
    return run.with_env(book.env)


def _bank_debit(env, pay):
    line = env["fix.bank.statement.line"].create(
        {
            "company_id": pay.company_id.id,
            "journal_id": (pay.released_journal_id or pay.journal_id).id,
            "date": date.today(),
            "amount": -pay.released_amount,
            "reference": pay.name,
            "statement_file_hash": "test-%s" % pay.id,
        }
    )
    line._fix_match_document("matched_payment_id", pay, "manual")


def _release_all(book, t, run, confirm=True):
    run.with_user(t.preparer).action_request_payments()
    for pay in run.line_ids.mapped("payment_execution_id"):
        pay.with_user(t.clerk).action_prepare()
        pay.with_user(t.releaser).action_release()
        if confirm:
            _bank_debit(book.env, pay)
    run.invalidate_recordset()


class TestPayoutRun:
    def test_totals_and_reference(self, book):
        run = _run(book)
        assert run.name.startswith(f"PAY/{YEAR}/") and run.name != f"PAY/{YEAR}/New"
        assert _money(run.total_gross) == D("16500.50")
        assert _money(run.total_tds) == D("640.00")
        assert _money(run.total_payable) == D("14410.45")  # 8,550.00 + 2,250.45 + 3,610.00
        assert run.seller_count == 2
        assert _run(book, name="PAY/MANUAL/9").name == "PAY/MANUAL/9"

    def test_prepare_route_and_approve(self, book):
        t = _treasury(book)
        empty = book.env["fix.payout.run"].with_user(t.preparer).create({"period": "2026-10"})
        with pytest.raises(UserError, match="No commissions attached"), book.env.cr.savepoint():
            empty.action_prepare()
        run = book.env["fix.payout.run"].with_user(t.approver).create({"period": "2026-10"})
        run.action_collect_accrued()
        run.action_prepare()
        # the preparing manager is never asked, and cannot approve directly
        assigned = run.approval_request_id.sudo().task_ids.mapped("assigned_user_id")
        assert t.approver not in assigned and t.releaser in assigned
        with pytest.raises(UserError), book.env.cr.savepoint():
            run.with_user(t.approver).action_approve()
        with pytest.raises(UserError), book.env.cr.savepoint():
            run.with_user(t.clerk).action_approve()
        _inbox_approve(book.env, run, t.releaser)
        assert (run.state, run.approved_by_id, run.sod_verified) == ("approved", t.releaser, True)
        assert _money(run.approved_total) == D("14410.45")
        assert sorted(run.line_ids.mapped("amount")) == [3610.0, 10800.45]
        assert _events(book.env, "payout.approved", run.id) == [
            {
                "payout_run": run.name,
                "total_payable": 14410.45,
                "total_tds": 640.0,
                "seller_count": 2,
                "approved_by": t.releaser.name,
            }
        ]

    def test_execution_requires_approval(self, book):
        run = _run(book)
        for call in (
            run.action_execute,
            run.action_submit_payout,
            run.action_generate_beftn,
            run.action_request_payments,
        ):
            with pytest.raises(UserError, match="only an approved run"), book.env.cr.savepoint():
                call()

    def test_treasury_pays_and_the_bank_statement_completes_the_run(self, book):
        t = _treasury(book)
        run = _approved(book, t)
        _release_all(book, t, run)
        assert run.state == "executed" and run.rail_status == "confirmed"
        assert set((book.c1 | book.c2 | book.c3).mapped("state")) == {"paid"}
        pays = run.line_ids.mapped("payment_execution_id")
        assert set(pays.mapped("state")) == {"executed"} and all(pays.mapped("source_posts_gl"))
        assert not pays.mapped("move_id")  # M50 books nothing: the run discharges once
        bank_code = t.journal.default_account_id.code
        rows = sorted(
            (line.account_id.code, line.debit, line.credit) for line in run.gl_move_id.line_ids
        )
        assert rows == sorted(
            [("200200", 15050.45, 0.0), ("210100", 0.0, 640.0), (bank_code, 0.0, 14410.45)]
        )
        st_a = run.statement_ids.filtered(lambda s: s.seller_partner_id == book.seller_a)
        assert st_a.state == "issued" and _money(st_a.net_payable) == D("10800.45")
        assert st_a.withholding_cert_ref.startswith("TDSC/")
        (event,) = _events(book.env, "payout.executed", run.id)
        assert (event["sellers_paid"], event["total_disbursed"]) == (2, 14410.45)
        # a second release cannot pay again
        with pytest.raises(UserError), book.env.cr.savepoint():
            run.with_user(t.preparer).action_request_payments()

    def test_a_failed_bank_payment_does_not_complete_the_run(self, book):
        t = _treasury(book)
        run = _approved(book, t)
        _release_all(book, t, run, confirm=False)
        pay = run.line_ids.mapped("payment_execution_id")[:1]
        pay.sudo().write({"failure_reason": "account closed"})
        pay.with_user(t.clerk).action_mark_failed()
        run.invalidate_recordset()
        assert run.state == "executing" and run.rail_status == "failed" and not run.gl_move_id
        assert set((book.c1 | book.c2 | book.c3).mapped("state")) == {"accrued"}

    def test_a_typed_bank_reference_confirms_nothing(self, book):
        t = _treasury(book)
        run = _approved(book, t)
        with pytest.raises(UserError, match="never by a typed reference"), book.env.cr.savepoint():
            run.with_user(t.approver).action_confirm_bank_settlement("BANK-REF-1")
        assert run.state == "approved"

    def test_an_unconfirmed_payee_account_is_not_paid(self, book):
        t = _treasury(book)
        run = _approved(book, t)
        # someone with the rights edits seller B's number after approval
        book.seller_b.bank_ids[:1].write({"acc_number": "0911100099999"})
        with pytest.raises(UserError), book.env.cr.savepoint():
            run.with_user(t.preparer).action_request_payments()
        assert not run.line_ids.mapped("payment_execution_id")

    def test_a_payee_without_an_account_is_not_paid(self, book):
        t = _treasury(book)
        nobank = _seller(book.env, "Comilla Mobile Hub", account=None)
        c4 = _commission(book.env, nobank, 1000.0, 0.10)
        c4.action_post_to_gl()
        _age(book.env, c4)
        run = _approved(book, t)
        assert nobank in run.line_ids.mapped("partner_id")
        with pytest.raises(UserError, match="No payee bank account"), book.env.cr.savepoint():
            run.with_user(t.preparer).action_request_payments()


# --------------------------------------------------------------------------- statements / reconciliation


class TestSellerStatement:
    def test_issue_and_settle(self, odoo_env):
        seller = odoo_env["res.partner"].create({"name": "Barishal Phone Care"})
        stmt = odoo_env["fix.seller.statement"].create(
            {
                "seller_partner_id": seller.id,
                "period": "2026-10",
                "gross_gmv": 5000.0,
                "commission_amount": 500.0,
                "tds_withheld": 225.0,
                "net_payable": 1.0,  # A08 M53-8: a typed net is ignored
            }
        )
        assert stmt.name.startswith(f"STM/{YEAR}/") and stmt.state == "draft"
        assert _money(stmt.net_payable) == D("4275.00")  # 5,000 - 500 - 225
        assert "section 140 of the Income Tax Act 2023" in stmt.statutory_note
        assert "ধারা ১৪০" in stmt.statutory_note
        # A08 M53-8: issued only for a payout run whose money has moved
        with pytest.raises(UserError, match="executed payout run"), odoo_env.cr.savepoint():
            stmt.action_issue_statement()
        run = odoo_env["fix.payout.run"].create({"period": "2026-10"})
        stmt.payout_run_id = run
        with pytest.raises(UserError, match="executed payout run"), odoo_env.cr.savepoint():
            stmt.action_issue_statement()
        run.state = "executed"
        stmt.action_issue_statement()
        assert stmt.state == "issued" and stmt.withholding_cert_ref.startswith("TDSC/")
        assert _events(odoo_env, "seller.statement_issued", stmt.id) == [
            {
                "statement_ref": stmt.name,
                "seller": "Barishal Phone Care",
                "period": "2026-10",
                "gross_gmv": 5000.0,
                "tds_withheld": 225.0,
                "net_disbursed": 4275.0,
                "cert_ref": stmt.withholding_cert_ref,
            }
        ]
        stmt.action_settle_statement()
        assert stmt.state == "settled"
        assert stmt.settled_by_id == odoo_env.user
        with pytest.raises(UserError, match="Only an issued statement"), odoo_env.cr.savepoint():
            stmt.action_settle_statement()
        named = odoo_env["fix.seller.statement"].create(
            {
                "name": "STM/MANUAL/1",
                "seller_partner_id": seller.id,
                "period": "2026-11",
                "gross_gmv": 0.0,
                "commission_amount": 0.0,
                "tds_withheld": 0.0,
            }
        )
        assert named.name == "STM/MANUAL/1"


class TestPayoutReconciliation:
    def _recon(self, env, run, **vals):
        return env["fix.payout.reconciliation"].create({"payout_run_id": run.id, **vals})

    def test_the_bank_side_comes_from_the_m50_instructions(self, book):
        t = _treasury(book)
        run = _approved(book, t)
        recon = self._recon(book.env, run)
        assert recon.name.startswith(f"REC/{YEAR}/")
        with pytest.raises(UserError, match="released nothing"), book.env.cr.savepoint():
            recon.action_run_reconciliation()
        _release_all(book, t, run, confirm=False)
        recon.action_run_reconciliation()
        # released but not yet on the statement: both payees are breaks
        assert (recon.system_count, recon.rail_count) == (2, 0)
        assert (recon.count_matched, recon.amount_matched, recon.state) == (
            False,
            False,
            "break_detected",
        )
        assert recon.unmatched_count == 2 and _money(recon.unmatched_amount) == D("14410.45")
        (event,) = _events(book.env, "platform.reconciliation_divergence", recon.id)
        assert (event["count_diff"], event["amount_diff"]) == (2, 14410.45)
        for pay in run.line_ids.mapped("payment_execution_id"):
            _bank_debit(book.env, pay)
        recon2 = self._recon(book.env, run)
        recon2.action_run_reconciliation()
        assert (recon2.system_count, recon2.rail_count) == (2, 2)
        assert _money(recon2.rail_amount) == D("14410.45")
        assert (recon2.count_matched, recon2.amount_matched, recon2.state) == (
            True,
            True,
            "balanced",
        )

    def test_break_lines_age(self, book):
        recon = self._recon(book.env, _run(book))
        line_model = book.env["fix.payout.reconciliation.line"]
        aged = line_model.create(
            {
                "reconciliation_id": recon.id,
                "seller_partner_id": book.seller_b.id,
                "discrepancy": 410.45,
                "record_date": date.today() - timedelta(days=40),
            }
        )
        fresh = line_model.create(
            {"reconciliation_id": recon.id, "seller_partner_id": book.seller_a.id, "discrepancy": 10.0}
        )
        assert (aged.age_days, aged.is_aged) == (40, True)
        assert (fresh.age_days, fresh.is_aged) == (0, False)
        recon.invalidate_recordset()
        assert (recon.unmatched_count, recon.aged_unmatched_count) == (2, 1)
        assert _money(recon.aged_unmatched_amount) == D("410.45")

    def test_undated_break_line_is_not_aged(self, book):
        recon = self._recon(book.env, _run(book))
        line = book.env["fix.payout.reconciliation.line"].create(
            {
                "reconciliation_id": recon.id,
                "seller_partner_id": book.seller_a.id,
                "record_date": False,
            }
        )
        assert (line.age_days, line.is_aged) == (0, False)

    def test_reconciliation_needs_a_payout_run(self, odoo_env):
        draft = odoo_env["fix.payout.reconciliation"].new({})
        with pytest.raises(UserError, match="Select a payout run"), odoo_env.cr.savepoint():
            draft.action_run_reconciliation()


# --------------------------------------------------------------------------- seller API


class _FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def api(book, monkeypatch):
    from odoo.addons.cd_settlement_ext.controllers import settlement_api

    def call(user, **kwargs):
        monkeypatch.setattr(settlement_api, "request", _FakeRequest(book.env(user=user.id)))
        return settlement_api.SettlementApiController().seller_settlements(**kwargs)

    return call


class TestSettlementApi:
    def test_back_office_reads_any_seller(self, book, api):
        staff = _user(book.env, "settlement_desk_nila", "base.group_user")
        result = api(staff, partner_id=str(book.seller_a.id))
        lines = result["settlements"]["lines"]
        assert [line["ref"] for line in lines] == [book.c2.name, book.c1.name]  # newest first
        assert lines[1] == {
            "ref": book.c1.name,
            "source_ref": "",
            "gross_bdt": "10,000.00",
            "commission_bdt": "1,000.00",
            "tds_bdt": "450.00",
            "net_bdt": "8,550.00",
            "state": "earned",
        }
        assert result["settlements"]["net_total_bdt"] == "10,800.45"  # 8,550.00 + 2,250.45

    def test_session_partner_by_default(self, book, api):
        staff = _user(book.env, "settlement_desk_nila", "base.group_user")
        assert api(staff) == {"settlements": {"lines": [], "net_total_bdt": "0.00"}}

    def test_portal_seller_sees_own_statement(self, book, api):
        portal = _user(book.env, "seller_b_portal", "base.group_portal", partner=book.seller_b)
        result = api(portal)
        assert [line["net_bdt"] for line in result["settlements"]["lines"]] == ["3,610.00"]
        assert (
            api(portal, partner_id=book.seller_b.id)["settlements"]["net_total_bdt"] == "3,610.00"
        )

    def test_portal_seller_cannot_read_another_seller(self, book, api):
        """Regression: the cross-tenant refusal was unreachable (the elif
        re-tested the group the first branch had excluded)."""
        portal = _user(book.env, "seller_b_portal", "base.group_portal", partner=book.seller_b)
        assert api(portal, partner_id=book.seller_a.id) == {
            "error": {"code": "access_denied", "message": "Cross-tenant access forbidden"}
        }

    def test_malformed_partner_id(self, book, api):
        staff = _user(book.env, "settlement_desk_nila", "base.group_user")
        assert api(staff, partner_id="abc")["error"]["code"] == "bad_request"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (0, "0.00"),
        (100, "100.00"),
        (999.999, "1,000.00"),  # regression: printed "999.00"
        (0.005, "0.01"),
        (1234567.891, "12,34,567.89"),
        (12345678.9, "1,23,45,678.90"),
        (-1234.5, "-1,234.50"),  # regression: printed "-1,2340.50"
        (None, "0.00"),
        ("not-a-number", "0.00"),
    ],
)
def test_fmt_bdt_south_asian_grouping(amount, expected):
    from odoo.addons.cd_settlement_ext.controllers.settlement_api import _fmt_bdt

    assert _fmt_bdt(amount) == expected
