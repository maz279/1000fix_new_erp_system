# cd_settlement_ext — live-ORM behaviour of M53: commission accrual (FF-91),
# SoD-gated payout runs on the INT-007 rail, statements, reconciliation and
# the seller settlement API. DoD-03 statutory set.
#
# The INT-007 rail is the in-memory library (no network); outcomes it cannot
# produce on demand (FAILED) come from a stub rail.
from __future__ import annotations

import base64
import json
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from odoo.exceptions import AccessError, UserError

from libs.py.payout_rail import INT007PayoutRail, PayoutStatus

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


def _approved_run(book):
    manager = _user(
        book.env, "finance_manager_karim", "base.group_user", "account.group_account_manager"
    )
    run = _run(book)
    run.with_user(manager).action_approve()
    return run


# --------------------------------------------------------------------------- commission ledger


class TestCommissionLedger:
    def test_commission_and_net_entitlement(self, book):
        assert book.c1.name == f"COM/{YEAR}/New"
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


class TestPayoutRun:
    def test_totals_and_reference(self, book):
        run = _run(book)
        assert run.name == f"PAY/{YEAR}/New"
        assert _money(run.total_gross) == D("16500.50")
        assert _money(run.total_tds) == D("640.00")
        assert _money(run.total_payable) == D("14410.45")  # 8,550.00 + 2,250.45 + 3,610.00
        assert run.seller_count == 2
        assert _run(book, name="PAY/MANUAL/9").name == "PAY/MANUAL/9"

    def test_sod_gate(self, book):
        manager = _user(
            book.env, "finance_manager_karim", "base.group_user", "account.group_account_manager"
        )
        clerk = _user(book.env, "payout_clerk_rahim", "base.group_user")
        empty = book.env["fix.payout.run"].create({"period": "2026-10"})
        with pytest.raises(UserError, match="No commissions attached"), book.env.cr.savepoint():
            empty.action_approve()
        own = _run(book, prepared_by_id=manager.id)
        with pytest.raises(UserError, match="Preparer cannot approve"), book.env.cr.savepoint():
            own.with_user(manager).action_approve()
        run = _run(book)
        with pytest.raises(AccessError, match="Only Finance Managers"), book.env.cr.savepoint():
            run.with_user(clerk).action_approve()
        run.with_user(manager).action_approve()
        assert (run.state, run.approved_by_id, run.sod_verified) == ("approved", manager, True)
        assert _events(book.env, "payout.approved", run.id) == [
            {
                "payout_run": run.name,
                "total_payable": 14410.45,
                "total_tds": 640.0,
                "seller_count": 2,
                "approved_by": manager.name,
            }
        ]

    def test_execution_requires_approval(self, book):
        run = _run(book)
        with pytest.raises(UserError, match="Approve before executing"), book.env.cr.savepoint():
            run.action_execute()
        with pytest.raises(UserError, match="must be SoD-approved"), book.env.cr.savepoint():
            run.action_submit_payout()
        with (
            pytest.raises(UserError, match="Approve payout run before generating BEFTN"),
            book.env.cr.savepoint(),
        ):
            run.action_generate_beftn()

    def test_confirmed_api_payout_finalises(self, book, monkeypatch):
        # WIRE-STUB at the rail seam: the ORM state machine is under test here;
        # the rail's own suite (libs/py/payout_rail) proves the HTTP contract,
        # including its fail-closed refusal without an endpoint.
        from decimal import Decimal as _D

        from odoo.addons.cd_settlement_ext.models import fix_settlement_ext as mod

        from libs.py.payout_rail import (
            PayoutBatchResult,
            PayoutStatus,
            RecipientResult,
        )

        class _WireRail:
            def __init__(self, *a, **k):
                pass

            def submit_payout_batch(self, req, **kwargs):
                results = tuple(
                    RecipientResult(
                        seller_ref=r.seller_ref,
                        status=PayoutStatus.CONFIRMED,
                        rail_tx_id=f"TX-{r.seller_ref}",
                        amount_bdt=r.amount_bdt,
                    )
                    for r in req.recipients
                )
                return PayoutBatchResult(
                    batch_ref=req.batch_ref,
                    rail_batch_id=f"RAIL-{req.batch_ref}-W1",
                    idempotency_key=req.idempotency_key,
                    status=PayoutStatus.CONFIRMED,
                    submission_time="2026-10-22T00:00:00+00:00",
                    recipient_results=results,
                    total_amount=req.total_amount,
                    recipient_count=req.recipient_count,
                    confirmed_count=req.recipient_count,
                    confirmed_amount=req.total_amount,
                    failed_count=0,
                    failed_amount=_D("0.00"),
                    unknown_count=0,
                    unknown_amount=_D("0.00"),
                    rail_type="api",
                )

        monkeypatch.setattr(mod, "INT007PayoutRail", _WireRail)
        run = _approved_run(book)
        run.action_execute()
        assert run.state == "executed"
        assert run.rail_status == "confirmed"
        assert run.idempotency_key.startswith(f"IDEMP-{run.name}-")
        assert run.rail_batch_id.startswith(f"RAIL-{run.name}-")
        assert set((book.c1 | book.c2 | book.c3).mapped("state")) == {"paid"}

        statements = {s.seller_partner_id: s for s in run.statement_ids}
        a, b = statements[book.seller_a], statements[book.seller_b]
        assert [
            _money(v) for v in (a.gross_gmv, a.commission_amount, a.tds_withheld, a.net_payable)
        ] == [
            D("12500.50"),
            D("1250.05"),
            D("450.00"),
            D("10800.45"),
        ]
        assert [
            _money(v) for v in (b.gross_gmv, b.commission_amount, b.tds_withheld, b.net_payable)
        ] == [
            D("4000.00"),
            D("200.00"),
            D("190.00"),
            D("3610.00"),
        ]
        assert a.withholding_cert_ref == f"NBR-TDS52-{YEAR}-{book.seller_a.id:04d}-0001"
        assert b.withholding_cert_ref == f"NBR-TDS52-{YEAR}-{book.seller_b.id:04d}-0002"
        assert {a.state, b.state} == {"issued"}

        move = run.gl_move_id
        lines = {line.name.split(":")[0]: line for line in move.line_ids}
        # discharge the seller liability 15,050.45 = net 14,410.45 + TDS 640.00
        assert _money(lines["Discharge Seller Liability"].debit) == D("15050.45")
        assert _money(lines["Statutory TDS Withheld (ITA 2023 s.140)"].credit) == D("640.00")
        assert _money(lines["Net Disbursed Funds via api"].credit) == D("14410.45")
        assert _events(book.env, "payout.executed", run.id) == [
            {
                "payout_run": run.name,
                "rail_type": "api",
                "rail_status": "confirmed",
                "sellers_paid": 2,
                "total_disbursed": 14410.45,
                "tds_withheld": 640.0,
            }
        ]
        # the GL discharge is posted once
        run.action_post_payout_to_gl()
        assert (
            book.env["account.move"].search_count([("ref", "=", f"PAYOUT-DISCHARGE-{run.name}")])
            == 1
        )

    def test_timeout_is_unknown_until_the_bank_confirms(self, book):
        """Regression: the read-back passed CONFIRMED as the outcome itself,
        so every timed-out payout was finalised as paid with invented
        transaction ids. Without a bank response it stays pending."""
        run = _approved_run(book)
        rail = INT007PayoutRail()
        run.action_submit_payout(simulate_timeout=True, rail_instance=rail)
        assert (run.state, run.rail_status) == ("executing", "unknown")  # never 'failed'
        assert not run.statement_ids
        key = run.idempotency_key
        run.action_query_status(rail_instance=rail)
        assert (run.state, run.rail_status) == ("executing", "pending_bank_confirmation")
        assert not run.statement_ids and not run.gl_move_id
        assert set((book.c1 | book.c2 | book.c3).mapped("state")) == {"earned"}
        assert run.idempotency_key == key
        # the bank's reference, recorded by a finance manager, finalises it
        manager = _user(
            book.env, "finance_manager_salma", "base.group_user", "account.group_account_manager"
        )
        run.with_user(manager).action_confirm_bank_settlement("BEFTN-STL-20261023-0042")
        assert (run.state, run.rail_status) == ("executed", "confirmed")
        assert run.bank_confirmation_ref == "BEFTN-STL-20261023-0042"
        assert run.bank_confirmed_by_id == manager
        assert run.gl_move_id and len(run.statement_ids) == 2

    def test_read_back_with_a_real_bank_response(self, book):
        run = _approved_run(book)
        run.action_submit_payout(simulate_timeout=True, rail_instance=INT007PayoutRail())
        # a bank response without the bank's reference is not a confirmation
        run.action_query_status(rail_instance=_BankQueryRail(PayoutStatus.CONFIRMED, ""))
        assert (run.state, run.rail_status) == ("executing", "pending_bank_confirmation")
        run.action_query_status(rail_instance=_BankQueryRail(PayoutStatus.CONFIRMED, "BK-77"))
        assert (run.state, run.rail_status, run.bank_confirmation_ref) == (
            "executed",
            "confirmed",
            "BK-77",
        )

    def test_read_back_reporting_failure(self, book):
        run = _approved_run(book)
        run.action_submit_payout(simulate_timeout=True, rail_instance=INT007PayoutRail())
        run.action_query_status(rail_instance=_BankQueryRail(PayoutStatus.FAILED, ""))
        assert (run.state, run.rail_status) == ("executing", "failed")
        with (
            pytest.raises(UserError, match=r"reported payout .* as FAILED"),
            book.env.cr.savepoint(),
        ):
            run.action_confirm_bank_settlement("BK-1")
        assert run.state == "executing"

    def test_bank_confirmation_needs_reference_manager_and_pending_state(self, book):
        run = _approved_run(book)
        with (
            pytest.raises(UserError, match="not awaiting bank confirmation"),
            book.env.cr.savepoint(),
        ):
            run.action_confirm_bank_settlement("BK-1")
        run.action_generate_beftn()
        with (
            pytest.raises(UserError, match="Enter the bank's settlement reference"),
            book.env.cr.savepoint(),
        ):
            run.action_confirm_bank_settlement()
        clerk = _user(book.env, "payout_clerk_jamal", "base.group_user")
        with (
            pytest.raises(AccessError, match="Only Finance Managers"),
            book.env.cr.savepoint(),
        ):
            run.with_user(clerk).action_confirm_bank_settlement("BK-1")
        assert run.state == "file_generated"
        # the form route: reference keyed into the field, then the button
        run.bank_confirmation_ref = "  BK-REF-9  "
        run.action_confirm_bank_settlement()
        assert (run.state, run.bank_confirmation_ref) == ("executed", "BK-REF-9")

    def test_failed_rail_outcome_does_not_finalise(self, book):
        run = _approved_run(book)
        run.idempotency_key = "IDEMP-FIXED-KEY"
        run.action_submit_payout(rail_instance=_StubRail(PayoutStatus.FAILED))
        assert (run.state, run.rail_status, run.rail_batch_id) == ("approved", "failed", "STUB-1")
        assert run.idempotency_key == "IDEMP-FIXED-KEY"  # reused, never regenerated
        run.action_query_status(rail_instance=_StubRail(PayoutStatus.FAILED))
        assert (run.state, run.rail_status) == ("approved", "failed")

    def test_query_needs_a_rail_reference(self, book):
        run = _approved_run(book)
        with pytest.raises(UserError, match="No rail batch reference"), book.env.cr.savepoint():
            run.action_query_status()

    def test_beftn_fallback_file_is_not_a_confirmed_payment(self, book):
        """Regression: generating the BEFTN file marked the payout confirmed,
        the commissions paid and posted the GL discharge - although the file
        had not even been uploaded to the bank."""
        run = _approved_run(book)
        run.action_generate_beftn(rail_instance=INT007PayoutRail())
        assert (run.state, run.rail_type, run.rail_status) == (
            "file_generated",
            "beftn",
            "file_generated",
        )
        assert run.beftn_filename == "BEFTN_PAY_%d_New.txt" % YEAR
        content = base64.b64decode(run.beftn_file).decode("ascii")
        assert all(len(row) == 128 for row in content.splitlines())
        assert run.idempotency_key.startswith(f"IDEMP-BEFTN-{run.name}-")
        assert run.rail_batch_id.startswith(f"BEFTN-{run.name}-")
        assert not run.gl_move_id and not run.statement_ids
        assert set((book.c1 | book.c2 | book.c3).mapped("state")) == {"earned"}
        assert not _events(book.env, "payout.executed", run.id)

        run.action_confirm_bank_settlement("BEFTN-SETTLED-0091")
        assert (run.state, run.rail_status) == ("executed", "confirmed")
        assert set((book.c1 | book.c2 | book.c3).mapped("state")) == {"paid"}
        lines = {line.name.split(":")[0]: line for line in run.gl_move_id.line_ids}
        assert _money(lines["Net Disbursed Funds via beftn"].credit) == D("14410.45")

    def test_beftn_file_carries_the_recorded_bank_details(self, book):
        """Regression: the file's originating routing was the payout
        library's built-in sponsor routing, not the company's account."""
        run = _approved_run(book)
        run.action_generate_beftn()  # default rail: built from the company account
        rows = base64.b64decode(run.beftn_file).decode("ascii").splitlines()
        file_header, entries = rows[0], [r for r in rows if r.startswith("6")]
        assert file_header[13:23].strip() == COMPANY_ROUTING
        assert file_header[63:86].strip() == book.env.company.name[:23]
        by_ref = {e[39:54].strip(): e for e in entries}
        a = by_ref["SLR-%04d" % book.seller_a.id]
        b = by_ref["SLR-%04d" % book.seller_b.id]
        assert (a[3:12], a[12:29].strip(), a[29:39]) == ("060272531", "2050123456789", "0001080045")
        assert (b[3:12], b[12:29].strip(), b[29:39]) == ("175260162", "0911100012345", "0000361000")

    def test_every_missing_bank_detail_is_named(self, book):
        """All gaps — the company's and every seller's — in ONE refusal."""
        company = book.env["res.company"].create({"name": "1000FiX No-Bank Payouts Ltd"})
        nobank = _seller(book.env, "Cash Only Traders", account=None)
        bad = _seller(book.env, "Misrouted Mobiles", routing="BRAC-DHK")
        extra = _commission(book.env, nobank, 500.0, 0.1) | _commission(book.env, bad, 800.0, 0.1)
        run = _run(book, company_id=company.id)
        run.commission_ids |= extra
        run.state = "approved"
        with pytest.raises(UserError) as refused, book.env.cr.savepoint():
            run.action_generate_beftn()
        message = str(refused.value)
        assert "company 1000FiX No-Bank Payouts Ltd: no bank account" in message
        assert "seller Cash Only Traders: no bank account" in message
        assert "seller Misrouted Mobiles: routing 'BRAC-DHK' is not a 9-digit" in message
        assert "Bengal Gadget House" not in message  # complete details pass
        assert (run.state, run.beftn_file) == ("approved", False)

    def test_company_routing_must_be_valid(self, book):
        company = book.env["res.company"].create({"name": "1000FiX Bad-Routing Payouts Ltd"})
        _bank_account(book.env, company.partner_id, "12345", "1101000011111")
        run = _run(book, company_id=company.id)
        run.state = "approved"
        with (
            pytest.raises(
                UserError, match="company 1000FiX Bad-Routing Payouts Ltd: routing '12345'"
            ),
            book.env.cr.savepoint(),
        ):
            run.action_submit_payout()

    def test_beftn_keeps_an_existing_idempotency_key(self, book):
        run = _approved_run(book)
        run.idempotency_key = "IDEMP-KEEP"
        run.action_generate_beftn()
        assert run.idempotency_key == "IDEMP-KEEP"

    def test_seller_without_bank_account_is_refused(self, book):
        """Regression: a seller without bank details was paid into a
        hard-coded placeholder account via the sponsor routing number."""
        nobank = _seller(book.env, "Cash Only Traders", account=None)
        _commission(book.env, nobank, 500.0, 0.1)
        run = _approved_run(book)
        run.commission_ids |= book.env["fix.commission.ledger"].search(
            [("seller_partner_id", "=", nobank.id)]
        )
        with (
            pytest.raises(UserError, match="seller Cash Only Traders: no bank account"),
            book.env.cr.savepoint(),
        ):
            run.action_submit_payout(rail_instance=INT007PayoutRail())
        assert run.state == "approved"

    def test_invalid_routing_number_is_refused(self, book):
        """Regression: an invalid routing number was silently replaced by
        a hard-coded sponsor routing number."""
        bad = _seller(book.env, "Misrouted Mobiles", routing="BRAC-DHK")
        _commission(book.env, bad, 500.0, 0.1)
        run = _approved_run(book)
        run.commission_ids |= book.env["fix.commission.ledger"].search(
            [("seller_partner_id", "=", bad.id)]
        )
        with (
            pytest.raises(
                UserError,
                match="seller Misrouted Mobiles: routing 'BRAC-DHK' is not a 9-digit BEFTN",
            ),
            book.env.cr.savepoint(),
        ):
            run.action_generate_beftn()


class _StubRail:
    """Stands in for the INT-007 gateway with a fixed outcome (no network)."""

    def __init__(self, status):
        self.status = status

    def _result(self):
        return SimpleNamespace(rail_batch_id="STUB-1", status=self.status)

    def submit_payout_batch(self, request, rail_type="api", simulate_timeout=False):
        return self._result()

    def read_back_status(self, batch_ref, rail_batch_id, simulate_rail_outcome=None):
        return self._result()


class _BankQueryRail:
    """A rail with a REAL bank status query (the seam action_query_status
    trusts): returns the bank's status and settlement reference."""

    def __init__(self, status, bank_reference):
        self.status, self.bank_reference = status, bank_reference

    def query_bank_status(self, batch_ref, rail_batch_id):
        return SimpleNamespace(status=self.status, bank_reference=self.bank_reference)


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
                "net_payable": 4275.0,
                "withholding_cert_ref": "NBR-TDS52-X",
            }
        )
        assert stmt.name == f"STM/{YEAR}/New"
        assert stmt.state == "draft"
        assert "Section 52 of the Income Tax Act 2023" in stmt.statutory_note
        stmt.action_issue_statement()
        assert stmt.state == "issued"
        assert _events(odoo_env, "seller.statement_issued", stmt.id) == [
            {
                "statement_ref": stmt.name,
                "seller": "Barishal Phone Care",
                "period": "2026-10",
                "gross_gmv": 5000.0,
                "tds_withheld": 225.0,
                "net_disbursed": 4275.0,
                "cert_ref": "NBR-TDS52-X",
            }
        ]
        # A08 M53: settled only once the money really moved (executed run)
        with pytest.raises(UserError, match="not confirmed as paid"), odoo_env.cr.savepoint():
            stmt.action_settle_statement()
        run = odoo_env["fix.payout.run"].create({"period": "2026-10"})
        stmt.payout_run_id = run
        with pytest.raises(UserError, match="not confirmed as paid"), odoo_env.cr.savepoint():
            stmt.action_settle_statement()
        run.state = "executed"
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
                "net_payable": 0.0,
                "withholding_cert_ref": "NBR-TDS52-Y",
            }
        )
        assert named.name == "STM/MANUAL/1"


class TestPayoutReconciliation:
    def _recon(self, env, run, **vals):
        return env["fix.payout.reconciliation"].create({"payout_run_id": run.id, **vals})

    def test_confirmed_run_balances_on_the_rail_figures(self, book):
        run = _run(book, rail_status="confirmed")
        recon = self._recon(book.env, run, rail_count=3, rail_amount=14410.45)
        assert recon.name == f"REC/{YEAR}/New"
        recon.action_run_reconciliation()
        assert (recon.system_count, recon.rail_count) == (3, 3)
        assert _money(recon.system_amount) == D("14410.45")
        assert _money(recon.rail_amount) == D("14410.45")
        assert (recon.count_matched, recon.amount_matched, recon.state) == (True, True, "balanced")

    def test_count_and_amount_breaks_reported_separately(self, book):
        run = _run(book, rail_status="confirmed")
        recon = self._recon(book.env, run, rail_count=2, rail_amount=14000.0, name="REC/MANUAL/2")
        assert recon.name == "REC/MANUAL/2"
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
            {
                "reconciliation_id": recon.id,
                "seller_partner_id": book.seller_a.id,
                "discrepancy": 10.0,
            }
        )
        assert (aged.age_days, aged.is_aged) == (40, True)
        assert (fresh.age_days, fresh.is_aged) == (0, False)
        recon.action_run_reconciliation()
        assert (recon.count_matched, recon.amount_matched) == (False, False)
        assert (recon.unmatched_count, recon.aged_unmatched_count) == (2, 1)
        assert _money(recon.unmatched_amount) == D("420.45")
        assert _money(recon.aged_unmatched_amount) == D("410.45")
        assert recon.state == "break_detected"
        assert _events(book.env, "platform.reconciliation_divergence", recon.id) == [
            {
                "reconciliation_ref": "REC/MANUAL/2",
                "payout_run": run.name,
                "count_diff": 1,
                "amount_diff": 410.45,  # 14,410.45 - 14,000.00
                "aged_unmatched": 1,
            }
        ]

    def test_rail_figures_are_never_copied_from_the_system(self, book):
        """Regression: with no rail figures entered, a 'confirmed' run copied
        the SYSTEM count/amount into the rail side and always balanced."""
        for rail_status in ("confirmed", "draft"):
            run = _run(book, rail_status=rail_status)
            recon = self._recon(book.env, run)
            with (
                pytest.raises(UserError, match="Enter the rail / bank statement"),
                book.env.cr.savepoint(),
            ):
                recon.action_run_reconciliation()
            assert (recon.rail_count, recon.rail_amount, recon.state) == (0, 0.0, "draft")

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
