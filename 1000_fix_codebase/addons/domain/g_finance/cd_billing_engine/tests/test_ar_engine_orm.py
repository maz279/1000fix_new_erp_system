# cd_billing_engine — live-ORM behaviour of the M20 engine depth (CD-M20-02):
# the billable-event queue, AR→GL posting through M19's hardened engine,
# receipts + matching + allocation (the evidence-bearing paid path), credit
# control, the dunning ladder with disputes, ageing snapshots, statements
# and leakage. Runs against the rolled-back fix_test database (odoo_env);
# every money expectation is worked out by hand.
from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError
from odoo.fields import Datetime

pytestmark = [pytest.mark.financial]

D = Decimal
COMPANY_BIN = "1234567890123"
CUSTOMER_BIN = "9876543210123"

# the GL account codes the engine resolves by default (AR_ACCOUNTS)
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
}


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _gl_company(env, label):
    """A private company WITH the AR chart accounts and a misc journal —
    the configuration under which GL posting must actually happen. All
    creates below run through `shop.env` so company defaults resolve to the
    private company, never the shared main one."""
    company = env["res.company"].create({"name": f"M20 GL {label} Co", "vat": COMPANY_BIN})
    env_ctx = env(context=dict(env.context, allowed_company_ids=company.ids))
    ou = env_ctx["operating.unit"].create(
        {
            "name": f"OU {label}",
            "code": f"AR-{label.upper()[:8]}",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    journal = env_ctx["account.journal"].create(
        {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
    )
    Account = env_ctx["account.account"].with_company(company)
    accounts = {
        role: Account.create(
            {
                "name": f"{role} {code}",
                "code": code,
                "account_type": atype,
                "company_ids": [(6, 0, company.ids)],
            }
        )
        for role, (code, atype) in GL_CODES.items()
    }
    brand = env_ctx["fix.brand"].create({"name": f"AR Brand {label}", "code": f"AB{label[:3]}"})
    model = env_ctx["fix.device.model"].create(
        {"brand_id": brand.id, "name": "AR-1", "device_type": "laptop"}
    )
    customer = env_ctx["res.partner"].create({"name": f"AR Cust {label}", "vat": CUSTOMER_BIN})
    lcd = env_ctx["product.product"].create({"name": "LCD AR", "default_code": "AR-LCD"})
    entity = env_ctx["fix.entity"].create(
        {
            "code": f"EN-{label.upper()[:8]}",
            "legal_name": f"Entity {label}",
            "company_id": company.id,
        }
    )
    branch = env_ctx["fix.branch"].create(
        {
            "code": f"BR-{label.upper()[:6]}",
            "name": f"Branch {label}",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    return SimpleNamespace(
        env=env_ctx,
        company=company,
        ou=ou,
        journal=journal,
        accounts=accounts,
        model=model,
        customer=customer,
        lcd=lcd,
        branch=branch,
    )


def _closed_order(shop, lines, state="closed", estimate_state="approved"):
    env = shop.env
    device = env["fix.device"].create({"device_model_id": shop.model.id})
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": shop.customer.id,
            "branch_id": shop.branch.id,
            "operating_unit_id": shop.ou.id,
            "fault_description": "No display",
            "state": state,
        }
    )
    env["fix.estimate"].create(
        {
            "order_id": order.id,
            "state": estimate_state,
            "discount": 0.0,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": p.id if p else False,
                        "description": d,
                        "quantity": q,
                        "unit_price": u,
                        "line_type": t,
                    },
                )
                for p, d, q, u, t in lines
            ],
        }
    )
    return order


JOB = [(None, "Labour", 1.0, 1000.0, "labour")]  # 1000 taxable + 150 VAT (15%)


def _events(env, event_type):
    return [
        json.loads(e.payload)
        for e in env["fix.event.outbox"].sudo().search([("event_type", "=", event_type)])
    ]


def _postings(env, move):
    """(account code, debit, credit) rows of a posted move — the code is the
    company-dependent computed field, read in the move's company."""
    rows = []
    for line in move.line_ids:
        code = line.account_id.with_company(move.company_id).code or ""
        rows.append((code, line.debit, line.credit))
    return sorted(rows)


def _issued(shop, taxable=1000.0):
    order = _closed_order(shop, [(None, "Job", 1.0, taxable, "labour")])
    return shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())


# ---------------------------------------------------------------------------
class TestBillableEventQueue:
    def test_intake_is_idempotent_and_queues_the_order(self, odoo_env):
        shop = _gl_company(odoo_env, "queue")
        order = _closed_order(shop, JOB)
        Queue = odoo_env["fix.billable.event"]
        event = {"event_id": "ev-ar-001", "aggregate_id": order.id}
        first = Queue.consume_order_closed(event)
        assert first and first.state == "new" and first.customer_id == shop.customer
        assert Queue.consume_order_closed(event) is None
        assert Queue.search_count([("event_id", "=", "ev-ar-001")]) == 1

    def test_generate_invoices_the_order_and_draws_a_number(self, odoo_env):
        shop = _gl_company(odoo_env, "gen")
        order = _closed_order(shop, JOB)
        Queue = odoo_env["fix.billable.event"]
        row = Queue.consume_order_closed({"event_id": "ev-ar-002", "aggregate_id": order.id})
        row.action_generate_invoice()
        assert row.state == "invoiced" and row.invoice_id
        assert row.invoice_id.name and row.invoice_id.name != "New"
        assert row.invoice_id.source_id == order.id

    def test_failure_is_recorded_and_never_silently_dropped(self, odoo_env):
        shop = _gl_company(odoo_env, "fail")
        order = _closed_order(shop, JOB, estimate_state="draft")  # gate will refuse
        Queue = odoo_env["fix.billable.event"]
        row = Queue.consume_order_closed({"event_id": "ev-ar-003", "aggregate_id": order.id})
        row.action_generate_invoice()
        assert row.state == "failed" and row.attempts == 1
        assert "approved estimate" in row.last_error

    def test_retry_ceiling_keeps_poison_events_visible(self, odoo_env):
        shop = _gl_company(odoo_env, "retry")
        order = _closed_order(shop, JOB, estimate_state="draft")
        Queue = odoo_env["fix.billable.event"]
        row = Queue.consume_order_closed({"event_id": "ev-ar-004", "aggregate_id": order.id})
        row.action_generate_invoice()
        row.action_generate_invoice()
        # 2 manual attempts already; the batch picks it up once more (attempts<3)
        Queue.action_process_all_due()
        assert row.attempts == 3
        Queue.action_process_all_due()  # ceiling reached — not reprocessed
        assert row.attempts == 3 and row.state == "failed"

    def test_deleted_source_is_skipped_not_failed(self, odoo_env):
        odoo_env_shop = _gl_company(odoo_env, "skip")
        Queue = odoo_env["fix.billable.event"]
        row = Queue.create(
            {
                "event_id": "ev-ar-005",
                "source_type": "service_order",
                "source_model": "fix.service.order",
                "source_id": 99999999,
            }
        )
        row.action_generate_invoice()
        assert row.state == "skipped" and "deleted" in (row.last_error or "")
        assert odoo_env_shop  # company created for isolation


# ---------------------------------------------------------------------------
class TestArGlPosting:
    def test_issue_posts_dr_ar_cr_revenue_cr_vat_and_flags_mushak(self, odoo_env):
        shop = _gl_company(odoo_env, "glpost")
        order = _closed_order(shop, JOB)  # 1000 + 150 VAT = 1150 total
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        assert invoice.posted_move_id and invoice.posted_move_id.state == "posted"
        rows = _postings(odoo_env, invoice.posted_move_id)
        assert rows == sorted(
            [("121000", 1150.0, 0.0), ("400000", 0.0, 1000.0), ("211000", 0.0, 150.0)]
        )
        assert invoice.mushak_id.posted is True  # the never-set flag, set at last
        log = (
            odoo_env["fix.journal.posting.log"]
            .sudo()
            .search([("move_id", "=", invoice.posted_move_id.id)])
        )
        assert log and log.source == "ar"

    def test_chartless_company_skips_gl_with_an_honest_note(self, odoo_env):
        company = odoo_env["res.company"].create({"name": "M20 NoGL Co", "vat": COMPANY_BIN})
        env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
        ou = env["operating.unit"].create(
            {
                "name": "OU",
                "code": "AR-NOGL",
                "company_id": company.id,
                "partner_id": company.partner_id.id,
            }
        )
        brand = env["fix.brand"].create({"name": "B", "code": "BNG"})
        model = env["fix.device.model"].create(
            {"brand_id": brand.id, "name": "M", "device_type": "laptop"}
        )
        customer = env["res.partner"].create({"name": "C", "vat": CUSTOMER_BIN})
        entity = env["fix.entity"].create(
            {"code": "EN-NOGL", "legal_name": "Entity NoGL", "company_id": company.id}
        )
        branch = env["fix.branch"].create(
            {
                "code": "BR-NOGL",
                "name": "Branch NoGL",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
        shop = SimpleNamespace(
            env=env, ou=ou, model=model, customer=customer, lcd=None, branch=branch
        )
        order = _closed_order(shop, JOB)
        invoice = env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        assert invoice.state == "issued" and invoice.name != "New"
        assert not invoice.posted_move_id
        assert invoice.gl_note and "GL not posted" in invoice.gl_note

    def test_manual_invoice_reason_gate_and_full_issue_path(self, odoo_env):
        shop = _gl_company(odoo_env, "manual")
        Invoice = shop.env["fix.ar.invoice"]
        # the reason gate is enforced at CREATION (FR-ARB-010) — never bypassed
        with pytest.raises(UserError, match="reason code"):
            Invoice.create_manual_invoice(
                {"customer_id": shop.customer.id, "operating_unit_id": shop.ou.id},
                [
                    {
                        "description": "x",
                        "taxable_amount": 100.0,
                        "vat_amount": 15.0,
                        "line_total": 115.0,
                    }
                ],
                reason_code="  ",
            )
        invoice = Invoice.create_manual_invoice(
            {
                "customer_id": shop.customer.id,
                "operating_unit_id": shop.ou.id,
                "invoice_date": date(2026, 10, 25),
            },
            [
                {
                    "description": "Exception job",
                    "taxable_amount": 2000.0,
                    "vat_amount": 300.0,
                    "line_total": 2300.0,
                }
            ],
            reason_code="SLA failure rebate reversal",
        )
        assert invoice.state == "draft" and invoice.manual_reason
        invoice.action_issue()
        assert invoice.state == "issued" and invoice.name.startswith("INV/")
        assert invoice.mushak_id and invoice.posted_move_id
        rows = _postings(odoo_env, invoice.posted_move_id)
        assert rows == sorted(
            [("121000", 2300.0, 0.0), ("400000", 0.0, 2000.0), ("211000", 0.0, 300.0)]
        )
        # a second manual invoice must not collide on the one-invoice-per-source guard
        second = Invoice.create_manual_invoice(
            {"customer_id": shop.customer.id, "operating_unit_id": shop.ou.id},
            [
                {
                    "description": "x",
                    "taxable_amount": 100.0,
                    "vat_amount": 15.0,
                    "line_total": 115.0,
                }
            ],
            reason_code="another",
        )
        assert second.source_id != invoice.source_id

    def test_cancel_posts_the_mirror_and_keeps_the_number(self, odoo_env):
        shop = _gl_company(odoo_env, "cancel")
        order = _closed_order(shop, JOB)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        number = invoice.name
        moves_before = odoo_env["account.move"].search_count([("company_id", "=", shop.company.id)])
        with pytest.raises(UserError, match="reason"):
            invoice.action_cancel()
        invoice.action_cancel(reason="duplicate issuance")
        assert invoice.state == "cancelled" and invoice.name == number
        assert (
            odoo_env["account.move"].search_count([("company_id", "=", shop.company.id)])
            == moves_before + 1
        )  # the mirror

    def test_writeoff_authority_matrix(self, odoo_env):
        shop = _gl_company(odoo_env, "woff")
        order = _closed_order(shop, JOB)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        invoice.action_write_off(reason="uncollectable walk-in")  # small: fine
        assert invoice.state == "written_off"
        # a large write-off needs a manager: a plain employee user is refused
        big = [(None, "Big job", 1.0, 100000.0, "labour")]  # 115000 total
        order2 = _closed_order(shop, big)
        invoice2 = shop.env["fix.ar.invoice"].from_closed_service_order(order2, Datetime.now())
        # the M19 SoD lesson, plus the OU rule on fix.* models: the maker may
        # see every company AND operating unit, or the record rule denies the
        # read before the authority check runs
        all_companies = [(6, 0, odoo_env["res.company"].search([]).ids)]
        all_ous = [(6, 0, odoo_env["operating.unit"].search([]).ids)]
        maker = odoo_env["res.users"].create(
            {
                "name": "AR Maker",
                "login": f"ar-maker-{shop.company.id}",
                "email": "m@x.local",
                "company_ids": all_companies,
                "operating_unit_ids": all_ous,
            }
        )
        with pytest.raises(UserError, match="managerial approval"):
            odoo_env(user=maker.id)["fix.ar.invoice"].browse(invoice2.id).action_write_off(
                reason="big loss"
            )


# ---------------------------------------------------------------------------
class TestCreditNoteApplication:
    def test_partial_credit_keeps_invoice_issued_with_residual(self, odoo_env):
        shop = _gl_company(odoo_env, "cnpart")
        order = _closed_order(shop, JOB)  # total 1150
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        note = shop.env["fix.credit.note"].create(
            {
                "operating_unit_id": shop.ou.id,
                "invoice_id": invoice.id,
                "amount": 300.0,
                "reason_code": "goodwill",
            }
        )
        note.action_submit()  # below threshold → approved
        note.action_issue()
        assert note.state == "issued" and note.posted_move_id
        assert invoice.state == "issued"  # NOT fully credited
        assert _money(invoice.amount_residual) == D("850.00")
        rows = _postings(odoo_env, note.posted_move_id)
        # 300 credited pro-rata: VAT 150/1150*300 = 39.13, revenue 260.87
        vat_part = _money(D("300.00") * D("150.00") / D("1150.00"))
        assert rows == sorted(
            [
                ("121000", 0.0, 300.0),
                ("211000", float(vat_part), 0.0),
                ("400000", float(D("300.00") - vat_part), 0.0),
            ]
        )

    def test_full_credit_flips_to_credited(self, odoo_env):
        shop = _gl_company(odoo_env, "cnfull")
        order = _closed_order(shop, JOB)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        note = shop.env["fix.credit.note"].create(
            {
                "operating_unit_id": shop.ou.id,
                "invoice_id": invoice.id,
                "amount": 1150.0,
                "reason_code": "service_failure",
            }
        )
        note.action_submit()
        note.action_issue()
        assert invoice.state == "credited"
        assert _money(invoice.amount_residual) == D("0.00")


# ---------------------------------------------------------------------------
class TestReceiptsAndAllocation:
    def test_nid_rule_blocks_high_value_cash(self, odoo_env):
        shop = _gl_company(odoo_env, "nid")
        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 60000.0, "method": "cash"}
        )
        with pytest.raises(UserError, match="NID"):
            receipt.action_confirm()
        receipt.nid_captured = "1990123456789"
        receipt.action_confirm()
        assert receipt.state == "confirmed"

    def test_confirm_posts_channel_clearing_two_stage(self, odoo_env):
        shop = _gl_company(odoo_env, "rct")
        _issued(shop)
        receipt = shop.env["fix.ar.receipt"].create(
            {
                "customer_id": shop.customer.id,
                "amount": 500.0,
                "method": "bkash",
                "reference": "TRX-77",
            }
        )
        receipt.action_confirm()
        assert receipt.posted_move_id and receipt.account_id == shop.accounts["channel_mfs"]
        assert _postings(odoo_env, receipt.posted_move_id) == sorted(
            [("121000", 0.0, 500.0), ("251000", 500.0, 0.0)]
        )

    def test_allocation_pays_invoice_with_evidence(self, odoo_env):
        shop = _gl_company(odoo_env, "alloc")
        invoice = _issued(shop)  # 1150 total
        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 1150.0, "method": "bank_transfer"}
        )
        receipt.action_confirm()
        shop.env["fix.ar.allocation"].create(
            {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": 1150.0}
        )
        assert invoice.state == "paid" and invoice.paid_date
        assert _money(invoice.amount_residual) == D("0.00")
        paid = [p for p in _events(odoo_env, "invoice.paid") if p.get("evidence")]
        assert paid and "RCP/" in paid[-1]["evidence"]

    def test_fr025_rejects_payment_against_cancelled(self, odoo_env):
        shop = _gl_company(odoo_env, "fr025")
        invoice = _issued(shop)
        invoice.action_cancel(reason="wrong customer")
        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 100.0, "method": "cash"}
        )
        receipt.action_confirm()
        with pytest.raises(UserError, match="FR-ARB-025"):
            shop.env["fix.ar.allocation"].create(
                {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": 100.0}
            )

    def test_over_allocation_refused_both_sides(self, odoo_env):
        shop = _gl_company(odoo_env, "over")
        invoice = _issued(shop)  # 1150
        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 100.0, "method": "cash"}
        )
        receipt.action_confirm()
        with pytest.raises(UserError, match="exceeds receipt"):
            shop.env["fix.ar.allocation"].create(
                {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": 200.0}
            )
        receipt2 = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 2000.0, "method": "cash"}
        )
        receipt2.action_confirm()
        with pytest.raises(UserError, match="exceeds invoice"):
            shop.env["fix.ar.allocation"].create(
                {"receipt_id": receipt2.id, "invoice_id": invoice.id, "amount": 2000.0}
            )

    def test_auto_match_scores_reference_exact_and_tolerance(self, odoo_env):
        shop = _gl_company(odoo_env, "match")
        invoice = _issued(shop)  # residual 1150
        exact = shop.env["fix.ar.receipt"].create(
            {
                "customer_id": shop.customer.id,
                "amount": 1150.0,
                "method": "bkash",
                "reference": invoice.mushak_id.mushak_no,
            }
        )
        exact.action_confirm()
        near = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 1132.0, "method": "nagad"}
        )
        near.action_confirm()
        far = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 10.0, "method": "card"}
        )
        far.action_confirm()
        proposals = shop.env["fix.ar.receipt"].action_auto_match()
        by_score = {p["receipt_id"]: p["score"] for p in proposals}
        assert by_score.get(exact.id) == 0.99  # reference hit
        assert by_score.get(near.id) == 0.75  # within ±2% of 1150
        assert far.id not in by_score  # exception queue

    def test_reversal_needs_zero_application_and_a_reason(self, odoo_env):
        shop = _gl_company(odoo_env, "rev")
        invoice = _issued(shop)
        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 500.0, "method": "cheque"}
        )
        receipt.action_confirm()
        shop.env["fix.ar.allocation"].create(
            {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": 100.0}
        )
        with pytest.raises(UserError, match="allocations"):
            receipt.action_reverse("wrong cheque")
        receipt2 = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 50.0, "method": "cheque"}
        )
        receipt2.action_confirm()
        with pytest.raises(UserError, match="reason"):
            receipt2.action_reverse("")
        receipt2.action_reverse("dishonoured")
        assert receipt2.state == "reversed"


# ---------------------------------------------------------------------------
class TestCreditControlDunningAgeing:
    def _old_invoice(self, shop, days, taxable=1000.0):
        order = _closed_order(shop, [(None, "Job", 1.0, taxable, "labour")])
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        invoice.invoice_date = date.today() - timedelta(days=days)
        return invoice

    def test_credit_hold_blocks_auto_invoicing(self, odoo_env):
        shop = _gl_company(odoo_env, "hold")
        shop.env["fix.credit.profile"].create(
            {
                "customer_id": shop.customer.id,
                "credit_limit": 0,
                "credit_hold": True,
                "hold_reason": "chronic late pay",
            }
        )
        order = _closed_order(shop, JOB)
        with pytest.raises(UserError, match="Credit hold"):
            shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())

    def test_profile_terms_drive_the_bucket(self, odoo_env):
        shop = _gl_company(odoo_env, "terms")
        invoice = self._old_invoice(shop, days=40)
        shop.env["fix.credit.profile"].create(
            {"customer_id": shop.customer.id, "payment_terms_days": 60}
        )
        run = shop.env["fix.dunning"].create(
            {
                "company_id": shop.company.id,
                "operating_unit_id": shop.ou.id,
                "invoice_id": invoice.id,
                "overdue_amount": 100.0,
            }
        )
        assert run.bucket == "current"  # 40 days < 60-day terms

    def test_dunning_run_creates_advances_and_respects_disputes(self, odoo_env):
        shop = _gl_company(odoo_env, "dun")
        inv_new = self._old_invoice(shop, days=45)  # overdue 15d (net-30)
        inv_old = self._old_invoice(shop, days=60)  # overdue 30d
        result = shop.env["fix.dunning"].action_run_dunning()
        assert result["created"] >= 2
        row_old = shop.env["fix.dunning"].search([("invoice_id", "=", inv_old.id)])
        assert row_old.overdue_amount > 0
        # partial dispute: dunning shrinks to the undisputed remainder only
        shop.env["fix.ar.dispute"].create(
            {"invoice_id": inv_old.id, "amount_disputed": 500.0, "reason": "wrong part"}
        )
        shop.env["fix.dunning"].action_run_dunning()
        row_old.invalidate_recordset()
        assert _money(row_old.overdue_amount) == _money(inv_old.amount_residual - 500.0)
        # ladder advance after grace
        row_old.step_date = date.today() - timedelta(days=8)
        shop.env["fix.dunning"].action_run_dunning()
        row_old.invalidate_recordset()
        assert row_old.step == "final"
        # a fully disputed invoice is suppressed, not dunned
        shop.env["fix.ar.dispute"].create(
            {
                "invoice_id": inv_new.id,
                "amount_disputed": inv_new.amount_residual,
                "reason": "full dispute",
            }
        )
        shop.env["fix.dunning"].action_run_dunning()
        row_new = shop.env["fix.dunning"].search([("invoice_id", "=", inv_new.id)])
        assert row_new.suppressed and row_new.suppression_reason == "dispute"

    def test_snapshot_capture_is_point_in_time_and_immutable(self, odoo_env):
        shop = _gl_company(odoo_env, "age")
        inv = self._old_invoice(shop, days=75)  # 45 days past net-30
        snap = shop.env["fix.ar.aging.snapshot"].create({"as_of_date": date.today()})
        snap.action_capture()
        assert snap.state == "captured" and snap.line_ids
        line = snap.line_ids.filtered(lambda ln: ln.customer_id == shop.customer)
        assert _money(line.d31_60) == _money(inv.amount_residual)
        with pytest.raises(UserError, match="immutable"):
            snap.write({"as_of_date": date(2020, 1, 1)})
        with pytest.raises(UserError, match="immutable"):
            snap.unlink()
        # backdated capture ages against the as-of date
        snap2 = shop.env["fix.ar.aging.snapshot"].create({"as_of_date": date.today()})
        snap2.action_capture(as_of=date.today() - timedelta(days=70))
        line2 = snap2.line_ids.filtered(lambda ln: ln.customer_id == shop.customer)
        assert _money(line2.current) == _money(inv.amount_residual)  # not yet due then


# ---------------------------------------------------------------------------
class TestStatementAndLeakage:
    def test_statement_math(self, odoo_env):
        from odoo.addons.cd_billing_engine.models.fix_ar_engine import (
            compute_customer_statement,
        )

        shop = _gl_company(odoo_env, "stmt")
        order1 = _closed_order(shop, [(None, "J1", 1.0, 1000.0, "labour")])
        inv1 = shop.env["fix.ar.invoice"].from_closed_service_order(order1, Datetime.now())
        inv1.invoice_date = date(2026, 9, 10)
        receipt = shop.env["fix.ar.receipt"].create(
            {
                "customer_id": shop.customer.id,
                "amount": 400.0,
                "method": "cash",
                "receipt_date": date(2026, 9, 20),
            }
        )
        receipt.action_confirm()
        order2 = _closed_order(shop, [(None, "J2", 1.0, 500.0, "labour")])
        inv2 = shop.env["fix.ar.invoice"].from_closed_service_order(order2, Datetime.now())
        inv2.invoice_date = date(2026, 10, 5)
        stmt = compute_customer_statement(
            shop.env, shop.customer.id, date(2026, 10, 1), date(2026, 10, 31)
        )
        # opening: 1150 invoice − 400 receipt = 750
        assert _money(stmt["opening"]) == D("750.00")
        kinds = [(r["kind"], _money(r["charge"])) for r in stmt["rows"]]
        assert kinds == [("invoice", D("575.00"))]  # 500 + 75 VAT
        assert _money(stmt["closing"]) == D("1325.00")

    def test_leakage_surfaces_unbilled_orders_and_failed_events(self, odoo_env):
        from odoo.addons.cd_billing_engine.models.fix_ar_engine import compute_leakage

        shop = _gl_company(odoo_env, "leak")
        _closed_order(shop, JOB)  # closed, never invoiced
        odoo_env["fix.billable.event"].create(
            {
                "event_id": "ev-leak-1",
                "company_id": shop.company.id,
                "source_type": "service_order",
                "source_model": "fix.service.order",
                "source_id": 123,
                "state": "failed",
                "attempts": 2,
                "last_error": "No approved estimate",
            }
        )
        leak = compute_leakage(odoo_env, company_id=shop.company.id)
        assert any(u["age_days"] >= 0 for u in leak["unbilled_closed_orders"])
        assert any(e["state"] == "failed" for e in leak["failed_events"])


# ---------------------------------------------------------------------------
# A08 M20 — customer VDS certificates (Mushak 6.6 received), close-out and
# the credit-hold workflow
# ---------------------------------------------------------------------------
def _finance_user(shop, login, *groups):
    env = shop.env
    return env["res.users"].create(
        {
            "name": login.replace("-", " ").title(),
            "login": f"{login}-{shop.company.id}@vds.test",
            "company_id": shop.company.id,
            "company_ids": [(6, 0, shop.company.ids)],
            "operating_unit_ids": [(6, 0, shop.ou.ids)],
            "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
        }
    )


def _cert(shop, invoice, user, amount, number="6.6/OCT/0001", **vals):
    return (
        shop.env(user=user)["fix.vds.certificate.received"]
        .create(
            {
                "invoice_id": invoice.id,
                "certificate_no": number,
                "certificate_date": date(2026, 10, 5),
                "vds_amount": amount,
                "challan_no": "TR-77",
                **vals,
            }
        )
        .sudo(False)
    )


class TestVdsCertificatesReceived:
    def test_vds_settles_the_receivable_and_the_receipt_pays_the_rest(self, odoo_env):
        from odoo.exceptions import AccessError, ValidationError

        shop = _gl_company(odoo_env, "vds1")
        invoice = _issued(shop)  # 1000 taxable + 150 VAT = 1150
        maker = _finance_user(shop, "vds-maker", "account.group_account_user")
        checker = _finance_user(shop, "vds-checker", "account.group_account_user")

        with (
            pytest.raises(ValidationError, match="exceed the invoice VAT"),
            shop.env.cr.savepoint(),
        ):
            _cert(shop, invoice, maker, 150.01)
        cert = _cert(shop, invoice, maker, 150.0)
        assert cert.name.startswith("VDS/")
        assert (cert.period, cert.customer_bin, cert.state) == ("2026-10", CUSTOMER_BIN, "draft")
        assert cert.company_id == shop.company and cert.customer_id == shop.customer

        # a second certificate can never take the invoice past its VAT
        with (
            pytest.raises(ValidationError, match="exceed the invoice VAT"),
            shop.env.cr.savepoint(),
        ):
            _cert(shop, invoice, maker, 1.0, number="6.6/OCT/0002")

        with pytest.raises(UserError, match="Verify certificate"), shop.env.cr.savepoint():
            cert.with_user(checker).action_settle()
        with pytest.raises(AccessError, match="Segregation of duties"), shop.env.cr.savepoint():
            cert.with_user(maker).action_verify()
        cert.with_user(checker).action_verify()
        assert (cert.state, cert.verified_by_id) == ("verified", checker)

        cert.with_user(checker).action_settle()
        assert cert.state == "settled" and cert.settled_move_id
        # Dr VDS receivable 150 / Cr AR 150 (the customer's control line)
        assert _postings(shop.env, cert.settled_move_id) == [
            ("121000", 0.0, 150.0),
            ("132000", 150.0, 0.0),
        ]
        assert _money(invoice.vds_settled_amount) == D("150.00")
        assert _money(invoice.amount_residual) == D("1000.00")
        assert invoice.state == "issued"

        with pytest.raises(UserError, match="locked"), shop.env.cr.savepoint():
            cert.vds_amount = 100.0
        with pytest.raises(UserError, match="GL correction"), shop.env.cr.savepoint():
            cert.action_cancel()

        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 1000.0, "method": "bank_transfer"}
        )
        receipt.action_confirm()
        shop.env["fix.ar.allocation"].create(
            {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": 1000.0}
        )
        assert invoice.state == "paid"

        # the 9.1 contract: settled certificates of the period, claimed once
        Cert = shop.env["fix.vds.certificate.received"]
        assert Cert.claimable_for_period("2026-10", shop.company) == cert
        with pytest.raises(UserError, match="return reference"), shop.env.cr.savepoint():
            cert.action_mark_claimed("")
        cert.action_mark_claimed("9.1/2026-10")
        assert (cert.state, cert.claimed_return_ref) == ("claimed", "9.1/2026-10")
        assert not Cert.claimable_for_period("2026-10", shop.company)
        with pytest.raises(UserError, match="Only settled"), shop.env.cr.savepoint():
            cert.action_mark_claimed("9.1/again")

    def test_vds_last_closes_the_invoice_with_evidence(self, odoo_env):
        shop = _gl_company(odoo_env, "vds2")
        invoice = _issued(shop)
        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 1000.0, "method": "bank_transfer"}
        )
        receipt.action_confirm()
        shop.env["fix.ar.allocation"].create(
            {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": 1000.0}
        )
        assert invoice.state == "issued"  # the VDS 150 is still open
        maker = _finance_user(shop, "vds2-maker", "account.group_account_user")
        checker = _finance_user(shop, "vds2-checker", "account.group_account_user")
        cert = _cert(shop, invoice, maker, 150.0, period="2026-11")
        cert.with_user(checker).action_verify()
        cert.with_user(checker).action_settle()
        assert invoice.state == "paid" and invoice.paid_date
        paid = [p for p in _events(odoo_env, "invoice.paid") if p.get("invoice") == invoice.name]
        assert paid and "VDS certificates 6.6/OCT/0001" in paid[-1]["evidence"]
        assert "RCP/" in paid[-1]["evidence"]
        assert cert.period == "2026-11"  # an explicit claim period wins

    def test_vds_settlement_refuses_without_the_account(self, odoo_env):
        shop = _gl_company(odoo_env, "vds3")
        invoice = _issued(shop)
        shop.accounts["vds_receivable"].active = False
        maker = _finance_user(shop, "vds3-maker", "account.group_account_user")
        checker = _finance_user(shop, "vds3-checker", "account.group_account_user")
        cert = _cert(shop, invoice, maker, 100.0)
        cert.with_user(checker).action_verify()
        with pytest.raises(UserError, match="vds_receivable"), shop.env.cr.savepoint():
            cert.with_user(checker).action_settle()
        assert cert.state == "verified" and invoice.vds_settled_amount == 0.0

    def test_period_format_and_cancel(self, odoo_env):
        from odoo.exceptions import ValidationError

        shop = _gl_company(odoo_env, "vds4")
        invoice = _issued(shop)
        maker = _finance_user(shop, "vds4-maker", "account.group_account_user")
        with pytest.raises(ValidationError, match="YYYY-MM"), shop.env.cr.savepoint():
            _cert(shop, invoice, maker, 10.0, period="10/2026")
        cert = _cert(shop, invoice, maker, 10.0)
        cert.action_cancel()
        assert cert.state == "cancelled"
        # a cancelled certificate frees the VAT headroom
        _cert(shop, invoice, maker, 150.0, number="6.6/OCT/0009")


class TestCloseOutAndHold:
    def test_register_paid_closes_only_a_fully_settled_invoice(self, odoo_env):
        shop = _gl_company(odoo_env, "close")
        invoice = _issued(shop)
        with (
            pytest.raises(UserError, match=r"still has 1150.0 outstanding"),
            shop.env.cr.savepoint(),
        ):
            invoice.action_register_paid()
        # a legacy / zero-residual invoice (here: loyalty covered the bill)
        invoice.loyalty_discount_amount = 1150.0
        invoice.action_register_paid()
        assert invoice.state == "paid"
        with pytest.raises(UserError, match="Only issued"), shop.env.cr.savepoint():
            invoice.action_register_paid()

    def test_toggle_hold_records_reason_who_and_when(self, odoo_env):
        shop = _gl_company(odoo_env, "holdwf")
        profile = shop.env["fix.credit.profile"].create(
            {"customer_id": shop.customer.id, "credit_limit": 5000}
        )
        clerk = _finance_user(shop, "hold-clerk", "account.group_account_user")
        profile.with_user(clerk).action_toggle_hold(reason="cheque bounced twice")
        assert (profile.credit_hold, profile.hold_reason, profile.hold_by) == (
            True,
            "cheque bounced twice",
            clerk,
        )
        assert profile.hold_date
        order = _closed_order(shop, JOB)
        with pytest.raises(UserError, match="Credit hold"), shop.env.cr.savepoint():
            shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        profile.with_user(clerk).action_toggle_hold()
        assert (profile.credit_hold, profile.hold_reason) == (False, False)
        # no reason given: an explicit manual-hold note naming the user
        profile.with_user(clerk).action_toggle_hold()
        assert (
            profile.credit_hold and profile.hold_reason == "Manual hold placed by %s" % clerk.name
        )
        bodies = " ".join(profile.message_ids.mapped("body"))
        assert "cheque bounced twice" in bodies and "released" in bodies
