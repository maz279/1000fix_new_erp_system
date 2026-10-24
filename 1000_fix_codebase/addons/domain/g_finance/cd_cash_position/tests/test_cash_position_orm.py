# cd_cash_position — live-ORM behaviour of M50 treasury: the payment-request
# seam, bank-feed import (INT-006) and auto-reconciliation, cash position.
from __future__ import annotations

import hashlib
import json
from datetime import date
from decimal import Decimal

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

D = Decimal


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _ou(env, company=None):
    company = company or env.company
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    return ou or env["operating.unit"].create(
        {
            "name": f"{company.name} OU",
            "code": f"OU{company.id}",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )


def _request(model, source_id, payload):
    return {"aggregate": model, "aggregate_id": source_id, "payload": payload}


# --------------------------------------------------------------------------- payment execution


class TestPaymentExecutionSeam:
    def test_vendor_request_consumed_once(self, odoo_env):
        ou = _ou(odoo_env)
        executions = odoo_env["fix.payment.execution"]
        event = _request(
            "fix.vendor.invoice", 41, {"vendor_id": 7, "amount": 4500.0, "operating_unit_id": ou.id}
        )
        payment = executions.consume_payment_requested(event)
        assert (payment.source_model, payment.source_id) == ("fix.vendor.invoice", 41)
        assert (payment.payee, payment.operating_unit_id) == ("vendor:7", ou)
        assert _money(payment.amount) == D("4500.00")
        assert (payment.state, payment.method) == ("pending", "bank_transfer")
        assert executions.consume_payment_requested(event) == payment
        assert (
            executions.search_count(
                [("source_model", "=", "fix.vendor.invoice"), ("source_id", "=", 41)]
            )
            == 1
        )

    def test_explicit_payee_wins(self, odoo_env):
        event = _request(
            "fix.ar.invoice",
            9,
            {"payee": "Karim Electronics", "amount": 10.0, "operating_unit_id": _ou(odoo_env).id},
        )
        assert (
            odoo_env["fix.payment.execution"].consume_payment_requested(event).payee
            == "Karim Electronics"
        )

    def test_expense_request_takes_ou_from_the_claim(self, odoo_env):
        """Regression: operating_unit_id is required on the execution but
        was never set — every consumed payment.requested failed."""
        ou = _ou(odoo_env)
        employee = odoo_env["hr.employee"].create({"name": "Rafiq"})
        claim = odoo_env["fix.expense.claim"].create(
            {
                "operating_unit_id": ou.id,
                "employee_id": employee.id,
                "description": "Fuel",
                "amount": 640.0,
            }
        )
        payment = odoo_env["fix.payment.execution"].consume_payment_requested(
            _request("fix.expense.claim", claim.id, {"employee_id": employee.id, "amount": 640.0})
        )
        assert payment.operating_unit_id == ou
        assert payment.payee == "employee:%s" % employee.id

    def test_end_to_end_from_the_ap_outbox(self, odoo_env):
        ou = _ou(odoo_env)
        vendor = odoo_env["res.partner"].create({"name": "Apex"})
        product = odoo_env["product.product"].create({"name": "Screen"})
        po = odoo_env["fix.purchase.order"].create(
            {
                "operating_unit_id": ou.id,
                "vendor_id": vendor.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "qty_ordered": 1,
                            "qty_received": 1,
                            "unit_price": 2000.0,
                        },
                    )
                ],
            }
        )
        inv = odoo_env["fix.vendor.invoice"].create(
            {
                "operating_unit_id": ou.id,
                "vendor_id": vendor.id,
                "invoice_ref": "APX-1",
                "requisition_id": po.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "description": "Screen",
                            "quantity": 1,
                            "unit_price": 2000.0,
                        },
                    )
                ],
            }
        )
        inv.action_request_payment()
        outbox = odoo_env["fix.event.outbox"].search(
            [("event_type", "=", "payment.requested"), ("aggregate_id", "=", inv.id)]
        )
        payment = odoo_env["fix.payment.execution"].consume_payment_requested(
            {
                "aggregate": outbox.aggregate,
                "aggregate_id": outbox.aggregate_id,
                "payload": json.loads(outbox.payload),
            }
        )
        assert _money(payment.amount) == D("1800.00")  # 2,000.00 less 10% TDS
        assert payment.operating_unit_id == ou

    @pytest.mark.parametrize(
        ("model", "source_id"),
        [("legacy.bill", 3), ("res.partner", 1), ("fix.vendor.invoice", 999999)],
    )
    def test_request_without_resolvable_ou_is_refused(self, odoo_env, model, source_id):
        with pytest.raises(UserError, match="carries no operating unit"), odoo_env.cr.savepoint():
            odoo_env["fix.payment.execution"].consume_payment_requested(
                _request(model, source_id, {"amount": 1.0})
            )

    def test_execute_once(self, odoo_env):
        payment = odoo_env["fix.payment.execution"].create(
            {
                "operating_unit_id": _ou(odoo_env).id,
                "source_model": "fix.ar.invoice",
                "source_id": 12,
                "payee": "vendor:1",
                "amount": 999.99,
                "method": "mobile_fs",
            }
        )
        payment.action_execute()
        assert payment.state == "executed"
        assert payment.executed_at
        assert _events(odoo_env, "payment.executed", payment.id) == [
            {
                "source_model": "fix.ar.invoice",
                "source_id": 12,
                "amount": 999.99,
                "method": "mobile_fs",
            }
        ]
        with (
            pytest.raises(UserError, match="Only pending payments execute"),
            odoo_env.cr.savepoint(),
        ):
            payment.action_execute()


# --------------------------------------------------------------------------- bank feed


FEED = "Date,Amount,Reference,Description\n2026-10-10,4500.00,AP/41,Payment Apex\n2026-10-11,-120.50,CHG-1,Bank charge\n"


class TestBankFeedImport:
    def test_parser_import_and_duplicate_file(self, odoo_env):
        lines = odoo_env["fix.bank.statement.line"]
        digest = hashlib.sha256(FEED.encode("utf-8")).hexdigest()
        assert lines.import_bank_feed(FEED) == {
            "imported": 2,
            "status": "success",
            "file_hash": digest,
        }
        created = lines.search([("statement_file_hash", "=", digest)], order="date")
        assert created.mapped("date") == [date(2026, 10, 10), date(2026, 10, 11)]
        assert [_money(a) for a in created.mapped("amount")] == [D("4500.00"), D("-120.50")]
        assert created.mapped("reference") == ["AP/41", "CHG-1"]
        assert set(created.mapped("statement_sequence")) == {"1"}
        assert lines.import_bank_feed(FEED) == {
            "imported": 0,
            "status": "duplicate_file",
            "file_hash": digest,
        }

    def test_statement_without_lines(self, odoo_env):
        empty = "Date,Amount,Reference,Description\n"
        result = odoo_env["fix.bank.statement.line"].import_bank_feed(empty)
        assert (result["imported"], result["status"]) == (0, "success")

    def test_csv_fallback_when_the_parser_fails(self, odoo_env, monkeypatch):
        from services.reconciliation.src import bank_feed_parser

        def broken(*_a, **_k):
            raise ValueError("unsupported layout")

        monkeypatch.setattr(bank_feed_parser, "parse_bank_feed", broken)
        feed = (
            "date,credit,reference,narration\n"
            "2026-10-12,700.25,AR/5,bKash settlement\n"
            ",50.00,NODATE,skipped\n"
            "2026-10-13,,EMPTY,skipped\n"
        )
        result = odoo_env["fix.bank.statement.line"].import_bank_feed(feed)
        assert (result["imported"], result["status"]) == (1, "success")
        line = odoo_env["fix.bank.statement.line"].search([("reference", "=", "AR/5")])
        assert (line.date, _money(line.amount), line.narration) == (
            date(2026, 10, 12),
            D("700.25"),
            "bKash settlement",
        )
        assert line.statement_sequence is False

    def test_parser_failing_midway_does_not_duplicate(self, odoo_env, monkeypatch):
        """Regression: lines the parser yielded before failing were kept and
        the CSV fallback appended the same rows again."""
        from services.reconciliation.src import bank_feed_parser

        real = bank_feed_parser.parse_bank_feed

        class HalfParsed:
            sequence_number = "7"

            def __init__(self, parsed):
                self._first = parsed.lines[0]

            @property
            def lines(self):
                yield self._first
                raise RuntimeError("connection reset while streaming")

        monkeypatch.setattr(
            bank_feed_parser, "parse_bank_feed", lambda c, format_type="auto": HalfParsed(real(c))
        )
        result = odoo_env["fix.bank.statement.line"].import_bank_feed(FEED)
        assert result["imported"] == 2
        digest = hashlib.sha256(FEED.encode("utf-8")).hexdigest()
        assert (
            odoo_env["fix.bank.statement.line"].search_count([("statement_file_hash", "=", digest)])
            == 2
        )


# --------------------------------------------------------------------------- auto-match


class TestAutoMatch:
    def _payment(self, env, model, source_id, amount, payee="vendor:1", company=None):
        company = company or env.company
        return env["fix.payment.execution"].create(
            {
                "company_id": company.id,
                "operating_unit_id": _ou(env, company).id,
                "source_model": model,
                "source_id": source_id,
                "payee": payee,
                "amount": amount,
                "state": "executed",
            }
        )

    def _line(self, env, amount, reference="", narration="", company=None):
        return env["fix.bank.statement.line"].create(
            {
                "company_id": (company or env.company).id,
                "date": date(2026, 10, 15),
                "amount": amount,
                "reference": reference,
                "narration": narration,
            }
        )

    def test_matching_ladder(self, odoo_env):
        env = odoo_env
        ar = self._payment(env, "fix.ar.invoice", 5, 1150.0)
        exp = self._payment(env, "fix.expense.claim", 7, 640.0)
        ap = self._payment(env, "fix.vendor.invoice", 9, 4500.0)
        other = self._payment(env, "legacy.bill", 3, 300.0, payee="Rahim Traders")

        # pending lines are processed newest first (_order: date desc, id desc)
        second_claim = self._line(env, 640.0, reference="EXP/7")  # EXP/7 used by then
        amount_only = self._line(env, 4500.0, narration="unknown sender")  # no ref, no payee
        payee_and_amount = self._line(env, 300.0, narration="paid Rahim Traders")
        ref_only = self._line(env, 600.0, narration="claim EXP/7 part")  # amount differs
        ref_and_amount = self._line(env, 1150.0, reference="AR/5")

        assert env["fix.bank.statement.line"].auto_match() == 3
        assert (ref_and_amount.match_state, ref_and_amount.matched_payment_id) == ("auto", ar)
        assert ref_and_amount.matched_invoice_ref == "AR/5"
        assert (ref_only.matched_payment_id, ref_only.matched_invoice_ref) == (exp, "EXP/7")
        assert (payee_and_amount.matched_payment_id, payee_and_amount.matched_invoice_ref) == (
            other,
            "3",
        )
        assert amount_only.match_state == "unmatched"
        assert second_claim.match_state == "unmatched"
        assert (
            ap.id
            not in (ref_and_amount | ref_only | payee_and_amount).mapped("matched_payment_id").ids
        )

    def test_payments_never_match_another_companys_bank_line(self, odoo_env):
        """Regression: auto_match paired bank lines with any company's
        payments (cross-entity reconciliation)."""
        other_co = odoo_env["res.company"].create({"name": "1000FiX Ctg Ltd"})
        self._payment(odoo_env, "fix.ar.invoice", 5, 1150.0, company=other_co)
        line = self._line(odoo_env, 1150.0, reference="AR/5")
        assert odoo_env["fix.bank.statement.line"].auto_match() == 0
        assert line.match_state == "unmatched"


# --------------------------------------------------------------------------- cash position


class TestCashPosition:
    def _shift(self, env, expected_float, state="open", company=None):
        company = company or env.company
        ou = _ou(env, company)
        entity = env["fix.entity"].search([("company_id", "=", company.id)], limit=1) or env[
            "fix.entity"
        ].create({"code": f"E{company.id}", "legal_name": company.name, "company_id": company.id})
        branch = env["fix.branch"].create(
            {
                "code": f"B{expected_float:.0f}"[:10],
                "name": "Branch",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
        operator = env["hr.employee"].create({"name": "Cashier"})
        return env["fix.cash.shift"].create(
            {
                "company_id": company.id,
                "operating_unit_id": ou.id,
                "branch_id": branch.id,
                "operator_id": operator.id,
                "opening_float": expected_float,
                "state": state,
            }
        )

    def test_position_sums_own_open_drawers(self, odoo_env):
        """Regression: the drawer search was company-blind — another
        entity's open drawers inflated this company's cash position."""
        own = odoo_env["res.company"].create({"name": "1000FiX Rajshahi Ltd"})
        self._shift(odoo_env, 5000.0, company=own)
        self._shift(odoo_env, 2500.5, state="counting", company=own)
        self._shift(odoo_env, 9999.0, state="closed", company=own)
        other_co = odoo_env["res.company"].create({"name": "1000FiX Sylhet Ltd"})
        self._shift(odoo_env, 7777.0, company=other_co)
        snap = odoo_env["fix.cash.position"].create(
            {"company_id": own.id, "bank_balance": 100000.0, "pending_payments": 25000.0}
        )
        assert _money(snap.drawer_float_total) == D("7500.50")  # 5,000.00 + 2,500.50
        assert _money(snap.total_position) == D("82500.50")  # 100,000.00 + 7,500.50 - 25,000.00
        snap.bank_balance = 90000.0
        assert _money(snap.total_position) == D("72500.50")
        # a re-taken snapshot (as_of moves) picks up a newly opened drawer
        self._shift(odoo_env, 1000.0, company=own)
        snap.as_of = "2026-10-22 18:00:00"
        assert _money(snap.drawer_float_total) == D("8500.50")
        assert _money(snap.total_position) == D("73500.50")
