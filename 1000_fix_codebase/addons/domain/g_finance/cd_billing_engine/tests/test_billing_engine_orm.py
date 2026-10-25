# cd_billing_engine — live-ORM behaviour of M20 AR: auto-invoicing a closed
# job with its Mushak 6.3 row, dunning, credit notes, consolidated bills.
# DoD-03 statutory set; every amount is worked out by hand below.
from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial, pytest.mark.tax]

D = Decimal
COMPANY_BIN = "1234567890123"
CUSTOMER_BIN = "9876543210123"


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def shop(odoo_env):
    """A PRIVATE company (own BIN, OU, entity): the shared fix_test database
    serves concurrent suites, so the main company's row and its
    one-entity-per-company key are never touched here."""
    company = odoo_env["res.company"].create(
        {"name": "M20 Billing ORM Test Co", "vat": COMPANY_BIN}
    )
    env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
    ou = env["operating.unit"].create(
        {
            "name": "Billing OU",
            "code": "BIL",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    entity = env["fix.entity"].create(
        {"code": "EN-BIL", "legal_name": "Billing Test Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {"code": "BIL01", "name": "Dhanmondi", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "Zeltrix Billing Test Brand", "code": "ZBIL"})
    model = env["fix.device.model"].create(
        {"brand_id": brand.id, "name": "ZB-15", "device_type": "laptop"}
    )
    customer = env["res.partner"].create({"name": "Karim Electronics", "vat": CUSTOMER_BIN})
    lcd = env["product.product"].create({"name": "LCD 15.6in", "default_code": "PART-LCD"})
    return SimpleNamespace(env=env, ou=ou, branch=branch, model=model, customer=customer, lcd=lcd)


def _closed_order(shop, lines, discount=0.0, state="closed", estimate_state="approved"):
    """lines: [(product_or_None, description, qty, unit_price, line_type)]"""
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
            "discount": discount,
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


STANDARD_JOB = [
    (None, "Panel replacement labour", 1.0, 1500.0, "labour"),  # code SVC
    ("lcd", "LCD 15.6in", 1.0, 4200.0, "part"),
    (None, "Bench test", 2.0, 250.0, "labour"),  # code SVC again
]


def _job(shop, discount=300.0):
    lines = [(shop.lcd if p == "lcd" else p, d, q, u, t) for p, d, q, u, t in STANDARD_JOB]
    return _closed_order(shop, lines, discount=discount)


class TestAutoInvoice:
    def test_closed_job_invoice_and_mushak_in_one_go(self, shop):
        """Regressions: (1) the engine read fix.estimate.line.discount, which
        does not exist — every closed order raised AttributeError; (2) lines
        were paired with determinations by product code, so the two 'SVC'
        labour lines both took the LAST one's amounts."""
        env = shop.env
        order = _job(shop)
        before = env["fix.mushak.register"].search_count([("company_id", "=", env.company.id)])

        invoice = env["fix.ar.invoice"].from_closed_service_order(order, None)

        # gross 1,500.00 / 4,200.00 / 500.00 = 6,200.00; header discount 300.00
        # allocated pro rata: 72.58 / 203.23 / 24.19 (sum 300.00)
        # taxable 1,427.42 / 3,996.77 / 475.81; VAT 15% half-up per line
        # 214.11 / 599.52 / 71.37
        lines = invoice.line_ids.sorted("id")
        assert [_money(v) for v in lines.mapped("taxable_amount")] == [
            D("1427.42"),
            D("3996.77"),
            D("475.81"),
        ]
        assert [_money(v) for v in lines.mapped("vat_amount")] == [
            D("214.11"),
            D("599.52"),
            D("71.37"),
        ]
        assert [_money(v) for v in lines.mapped("line_total")] == [
            D("1641.53"),
            D("4596.29"),
            D("547.18"),
        ]
        assert lines.mapped("description") == [
            "Panel replacement labour",
            "LCD 15.6in",
            "Bench test",
        ]
        assert _money(invoice.taxable_amount) == D("5900.00")
        assert _money(invoice.vat_amount) == D("885.00")
        assert _money(invoice.total_payable) == D("6785.00")
        assert (invoice.state, invoice.source_model, invoice.source_id) == (
            "issued",
            "fix.service.order",
            order.id,
        )
        assert (invoice.branch_id, invoice.operating_unit_id) == (shop.branch, shop.ou)
        assert 0.0 <= invoice.generation_seconds < 5.0  # NFR-040
        assert invoice.generated_at

        mushak = invoice.mushak_id
        fy_start = env.company.compute_fiscalyear_dates(invoice.invoice_date)["date_from"]
        expected_no = "%d-%06d" % (fy_start.year, before + 1)
        assert mushak.mushak_no == expected_no
        assert (mushak.supplier_bin, mushak.customer_bin) == (COMPANY_BIN, CUSTOMER_BIN)
        assert mushak.invoice_ref == "AR/%s" % invoice.id
        assert _money(mushak.total_payable) == D("6785.00")
        assert mushak.treatment_summary == (
            "SVC: standard_15 @ 15%\nPART-LCD: standard_15 @ 15%\nSVC: standard_15 @ 15%"
        )
        (event,) = _events(env, "invoice.created", invoice.id)
        assert (event["mushak_no"], event["vat_amount"], event["total_payable"]) == (
            expected_no,
            885.0,
            6785.0,
        )
        assert event["supplier_bin"] == COMPANY_BIN

        # idempotent on the source document
        assert env["fix.ar.invoice"].from_closed_service_order(order, None) == invoice
        assert (
            env["fix.mushak.register"].search_count([("company_id", "=", env.company.id)])
            == before + 1
        )

    def test_mushak_numbering_is_a_per_company_fiscal_year_sequence(self, shop):
        """Regression: numbers were search_count + 1 with a calendar-year
        prefix - two concurrent invoices could draw the same number and the
        series never restarted with the fiscal year."""
        env = shop.env
        company = env.company
        company.write({"fiscalyear_last_month": "6", "fiscalyear_last_day": 30})  # BD FY
        Invoice = env["fix.ar.invoice"]
        assert Invoice._next_mushak_no(company, date(2026, 6, 30)) == "2025-000001"
        assert Invoice._next_mushak_no(company, date(2026, 6, 15)) == "2025-000002"
        # a new fiscal year restarts the series
        assert Invoice._next_mushak_no(company, date(2026, 7, 1)) == "2026-000001"
        assert Invoice._next_mushak_no(company, date(2026, 6, 1)) == "2025-000003"
        seq = Invoice._mushak_sequence(company)
        assert (seq.company_id, seq.implementation, seq.use_date_range) == (
            company,
            "no_gap",
            True,
        )
        # another company numbers independently
        other = env["res.company"].create({"name": "M20 Other Numbering Co"})
        assert Invoice._next_mushak_no(other, date(2026, 7, 1)) == "2026-000001"
        assert Invoice._mushak_sequence(other) != seq

    def test_numbering_refuses_without_the_sequence_template(self, shop):
        """A company's Mushak series is copied from the module template; with
        the template gone numbering stops instead of inventing a number."""
        env = shop.env
        other = env["res.company"].create({"name": "M20 No Template Co"})
        with (
            pytest.raises(UserError, match=r"Mushak 6.3 numbering sequence is missing"),
            env.cr.savepoint(),
        ):
            env.ref("cd_billing_engine.seq_fix_mushak_63").unlink()
            env["fix.ar.invoice"]._mushak_sequence(other)

    def test_new_fiscal_range_continues_after_existing_numbers(self, shop):
        """Numbers written by the old scheme are never re-issued."""
        env = shop.env
        env["fix.mushak.register"].create(
            {
                "operating_unit_id": shop.ou.id,
                "mushak_no": "2030-000041",
                "invoice_ref": "AR/LEGACY",
                "invoice_date": date(2030, 3, 1),
                "supplier_name": "Legacy",
                "supplier_bin": COMPANY_BIN,
                "customer_name": "Legacy customer",
                "taxable_amount": 100.0,
                "vat_amount": 15.0,
                "total_payable": 115.0,
            }
        )
        nxt = env["fix.ar.invoice"]._next_mushak_no(env.company, date(2030, 5, 1))
        assert nxt == "2030-000042"

    def test_order_without_ou_invoices_under_its_branch_ou(self, shop):
        order = _closed_order(shop, [(None, "Labour", 1.0, 100.0, "labour")])
        order.operating_unit_id = False
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, None)
        assert invoice.operating_unit_id == shop.branch.operating_unit_id
        assert invoice.mushak_id.operating_unit_id == shop.branch.operating_unit_id
        assert _money(invoice.total_payable) == D("115.00")  # 100.00 + 15% VAT

    def test_only_closed_jobs_are_invoiced(self, shop):
        order = _closed_order(shop, [(None, "Labour", 1.0, 100.0, "labour")], state="ready")
        with pytest.raises(UserError, match="closed jobs only"), shop.env.cr.savepoint():
            shop.env["fix.ar.invoice"].from_closed_service_order(order, None)

    def test_approved_estimate_required(self, shop):
        order = _closed_order(shop, [(None, "Labour", 1.0, 100.0, "labour")], estimate_state="sent")
        with (
            pytest.raises(UserError, match="No approved estimate on %s" % order.name),
            shop.env.cr.savepoint(),
        ):
            shop.env["fix.ar.invoice"].from_closed_service_order(order, None)

    def test_supplier_bin_never_invented(self, shop):
        shop.env.company.vat = " "
        order = _closed_order(shop, [(None, "Labour", 1.0, 100.0, "labour")])
        with pytest.raises(UserError, match="Company BIN missing"), shop.env.cr.savepoint():
            shop.env["fix.ar.invoice"].from_closed_service_order(order, None)

    def test_loyalty_discount_reduces_payable_never_below_zero(self, shop):
        invoice = shop.env["fix.ar.invoice"].create(
            {
                "customer_id": shop.customer.id,
                "operating_unit_id": shop.ou.id,
                "source_model": "manual",
                "source_id": 1,
                "line_ids": [(0, 0, {"taxable_amount": 1000.0, "vat_amount": 150.0})],
                "loyalty_discount_amount": 100.0,
            }
        )
        assert _money(invoice.total_payable) == D("1050.00")  # 1,150.00 - 100.00
        invoice.loyalty_discount_amount = 2000.0
        assert _money(invoice.total_payable) == D("0.00")

    def test_payment_receipt(self, shop):
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(_job(shop), None)
        # A08 M20: never paid without evidence - the open residual refuses
        with (
            pytest.raises(UserError, match="never marked paid without settlement evidence"),
            shop.env.cr.savepoint(),
        ):
            invoice.action_register_paid()
        assert invoice.state == "issued"
        assert _events(shop.env, "invoice.paid", invoice.id) == []
        # loyalty redemption covering the whole bill leaves nothing to settle
        invoice.loyalty_discount_amount = 6785.0
        assert invoice.amount_residual == 0.0
        invoice.action_register_paid()
        assert invoice.state == "paid" and invoice.paid_date
        assert _events(shop.env, "invoice.paid", invoice.id) == [
            {
                "invoice": invoice.name,
                "mushak_no": invoice.mushak_id.mushak_no,
                "total_payable": 0.0,
                "evidence": "",
            }
        ]
        with (
            pytest.raises(UserError, match="Only issued invoices can be paid"),
            shop.env.cr.savepoint(),
        ):
            invoice.action_register_paid()

    def test_nfr040_benchmark(self, shop):
        orders = _job(shop) | _job(shop)
        invoices = shop.env["fix.ar.invoice"]
        by_ids = invoices.benchmark_auto_invoice_timing(orders.ids)
        assert len(by_ids["invoice_ids"]) == 2
        assert by_ids["nfr_040_met"] is True
        assert by_ids["max_seconds"] == max(by_ids["durations"])
        by_records = invoices.benchmark_auto_invoice_timing(orders)
        assert by_records["invoice_ids"] == by_ids["invoice_ids"]  # idempotent
        assert invoices.benchmark_auto_invoice_timing([]) == {
            "invoice_ids": [],
            "durations": [],
            "average_seconds": 0.0,
            "max_seconds": 0.0,
            "nfr_040_met": True,
        }


class TestDiscountAllocation:
    def test_pro_rata_with_residue_on_the_largest_line(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import allocate_discount

        # 100.00 / 3 = 33.33 x 3 = 99.99; the 0.01 residue goes to the first largest
        assert allocate_discount([D("100.00")] * 3, D("100")) == [
            D("33.34"),
            D("33.33"),
            D("33.33"),
        ]
        assert allocate_discount([D("50.00"), D("150.00")], D("20.005")) == [D("5.00"), D("15.01")]

    def test_no_discount_and_excess_discount(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import allocate_discount

        assert allocate_discount([D("10.00"), D("20.00")], D("0")) == [D("0.00"), D("0.00")]
        with pytest.raises(UserError, match="exceeds the invoiced lines"):
            allocate_discount([D("10.00")], D("10.01"))


def _invoice(shop, invoice_date, taxable=1000.0, vat=150.0, state="issued", customer=None):
    return shop.env["fix.ar.invoice"].create(
        {
            "customer_id": (customer or shop.customer).id,
            "operating_unit_id": shop.ou.id,
            "source_model": "manual",
            "source_id": shop.env["fix.ar.invoice"].search_count([]) + 1000,
            "invoice_date": invoice_date,
            "state": state,
            "line_ids": [(0, 0, {"taxable_amount": taxable, "vat_amount": vat})],
        }
    )


class TestDunning:
    @pytest.mark.parametrize(
        ("age_days", "overdue", "bucket"),
        [
            (10, 0, "current"),
            (30, 0, "current"),
            (45, 15, "d1_30"),
            (60, 30, "d1_30"),
            (75, 45, "d31_60"),
            (110, 80, "d61_90"),
            (200, 170, "d90_plus"),
        ],
    )
    def test_net30_ageing_buckets(self, shop, age_days, overdue, bucket):
        invoice = _invoice(shop, date.today() - timedelta(days=age_days))
        run = shop.env["fix.dunning"].create({"invoice_id": invoice.id, "overdue_amount": 1150.0})
        assert (run.days_overdue, run.bucket) == (overdue, bucket)

    def test_unsaved_run_without_invoice(self, odoo_env):
        """Regression: the stored compute assigned nothing when the invoice
        had no date (form onchange), which Odoo rejects."""
        draft = odoo_env["fix.dunning"].new({})
        assert (draft.days_overdue, draft.bucket) == (0, "current")


class TestCreditNote:
    def _note(self, shop, amount):
        invoice = _invoice(shop, date.today(), taxable=60000.0, vat=9000.0)
        return shop.env["fix.credit.note"].create(
            {
                "operating_unit_id": shop.ou.id,
                "invoice_id": invoice.id,
                "amount": amount,
                "reason_code": "pricing_error",
            }
        )

    def test_threshold_routes_approval(self, shop):
        small = self._note(shop, 25000.0)
        large = self._note(shop, 25000.01)
        (small | large).action_submit()
        assert (small.state, large.state) == ("approved", "pending_approval")

    def test_manager_authority_above_threshold(self, shop):
        note = self._note(shop, 30000.0)
        clerk = shop.env["res.users"].create(
            {
                "name": "AR Clerk",
                "login": "ar_clerk@billing.test",
                "group_ids": [(6, 0, [shop.env.ref("base.group_user").id])],
            }
        )
        with (
            pytest.raises(UserError, match="above BDT 25000 require managerial approval"),
            shop.env.cr.savepoint(),
        ):
            note.with_user(clerk).sudo().action_approve()
        note.action_approve()  # superuser holds base.group_system
        assert (note.state, note.approved_by) == ("approved", shop.env.user)

    def test_issue_applies_credit_partially_then_fully(self, shop):
        """CD-M20-02 semantics: a note applies its amount — only a FULLY
        credited invoice flips to 'credited' (the old any-note-credits-all
        behaviour was the audit's partial-application defect)."""
        note = self._note(shop, 5000.0)  # invoice total is 69000
        with pytest.raises(UserError, match="Approve before issuing"), shop.env.cr.savepoint():
            note.action_issue()
        note.action_submit()
        note.action_issue()
        invoice = note.invoice_id
        assert note.state == "issued"
        assert invoice.state == "issued"  # partial credit keeps it open
        assert _money(invoice.amount_residual) == D("64000.00")
        assert _events(shop.env, "credit_note.issued", note.id)[-1] == {
            "invoice_ref": "AR/%s" % invoice.id,
            "invoice": invoice.name,
            "amount": 5000.0,
            "reason": "pricing_error",
            "invoice_residual": 64000.0,
        }
        # a second note clearing the residual flips the invoice to credited
        settle = self._note(shop, 64000.0)
        settle.invoice_id = invoice
        settle.action_submit()
        settle.action_approve()  # above BDT 25,000 — superuser holds the group
        settle.action_issue()
        invoice.invalidate_recordset()
        assert invoice.state == "credited"
        assert _money(invoice.amount_residual) == D("0.00")


class TestConsolidatedBill:
    def test_period_selection_and_totals(self, shop):
        in_period = _invoice(shop, date(2026, 9, 5), taxable=1000.0, vat=150.0)
        draft_in_period = _invoice(shop, date(2026, 9, 30), taxable=200.5, vat=30.08, state="draft")
        _invoice(shop, date(2026, 10, 1))  # after the period
        _invoice(shop, date(2026, 9, 10), state="paid")  # already settled
        other = shop.env["res.partner"].create({"name": "Other Corp"})
        _invoice(shop, date(2026, 9, 10), customer=other)

        bill = shop.env["fix.ar.consolidated.bill"].create(
            {
                "operating_unit_id": shop.ou.id,
                "customer_id": shop.customer.id,
                "bill_ref": "CB-2026-09",
                "period_start": date(2026, 9, 1),
                "period_end": date(2026, 9, 30),
            }
        )
        bill.action_generate()
        assert bill.invoice_ids == in_period | draft_in_period
        assert _money(bill.total_taxable) == D("1200.50")
        assert _money(bill.total_vat) == D("180.08")
        assert _money(bill.total_payable) == D("1380.58")
        assert bill.state == "generated"
        assert _events(shop.env, "consolidated_bill.generated", bill.id) == [
            {
                "bill_ref": "CB-2026-09",
                "customer_id": shop.customer.id,
                "total_payable": 1380.58,
                "invoice_count": 2,
            }
        ]

    def test_preselected_invoices_are_kept(self, shop):
        chosen = _invoice(shop, date(2026, 8, 1))
        bill = shop.env["fix.ar.consolidated.bill"].create(
            {
                "operating_unit_id": shop.ou.id,
                "customer_id": shop.customer.id,
                "bill_ref": "CB-MANUAL",
                "period_start": date(2026, 9, 1),
                "period_end": date(2026, 9, 30),
                "invoice_ids": [(6, 0, chosen.ids)],
            }
        )
        bill.action_generate()
        assert bill.invoice_ids == chosen
