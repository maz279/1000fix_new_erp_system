# cd_billing_engine tests — M20 core (P06-M03).
import inspect

import pytest

pytestmark = [pytest.mark.financial]


class TestAutoInvoice:
    def test_model_exists(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixArInvoice

        assert FixArInvoice is not None

    def test_source_unique_constraint(self):
        """The auto-generation guard: one invoice per source document."""
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixArInvoice

        assert hasattr(FixArInvoice, "_source_key_unique")  # Odoo 19 models.Constraint attr

    def test_closed_only_gate(self):
        """BRU-SRM-05: the method refuses orders not yet delivered or closed
        (A02 ERP audit X-03: the tax point is the delivery)."""
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine", fromlist=["FixArInvoice"]
            ).FixArInvoice.from_closed_service_order
        )
        assert 'state not in ("delivered", "closed")' in source

    def test_determination_is_synchronous_import(self):
        """AR-006 pair 7: M20 calls M51 synchronously (an import, never an
        event wait) and consumes nothing back."""
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine", fromlist=["FixArInvoice"]
            )
        )
        assert "from odoo.addons.cd_tax_engine_bd.models import tax_logic" in source
        assert "tax_logic.determine_tax" in source

    def test_atomic_mushak_write_in_same_method(self):
        """P06-M02-T08: the Mushak register row is written in the invoice's
        transaction through M51's issuing service (A08: register rows are never
        typed). The behaviour is proven live in test_billing_engine_orm
        (test_closed_job_invoice_and_mushak_in_one_go); this pins the seam."""
        from odoo.addons.cd_billing_engine.models import fix_billing_engine as fbe

        assert callable(fbe._issue_mushak_row) and callable(fbe.m51_determine)

    def test_nfr040_timing_recorded(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine", fromlist=["FixArInvoice"]
            ).FixArInvoice.from_closed_service_order
        )
        assert "time.monotonic" in source  # NFR-040: the 5-second budget measured

    def test_nfr040_benchmark_method_present(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixArInvoice

        assert hasattr(FixArInvoice, "benchmark_auto_invoice_timing")

    def test_loyalty_discount_fields_and_compute(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixArInvoice

        assert hasattr(FixArInvoice, "loyalty_points_redeemed")
        assert hasattr(FixArInvoice, "loyalty_discount_amount")
        source = inspect.getsource(FixArInvoice._compute_totals)
        assert "loyalty_discount_amount" in source
        assert "total_payable" in source

    def test_company_bin_never_invented(self):
        """A Mushak without the supplier BIN must fail, not default."""
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine", fromlist=["FixArInvoice"]
            ).FixArInvoice._company_bin
        )
        assert "raise UserError" in source


class TestInterfaceConformance:
    """T02 / AR-006 Section 4.1 Pairs 6 & 7 interface conformance proof."""

    def test_m20_to_m51_is_synchronous_tax_determination(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine", fromlist=["FixArInvoice"]
            )
        )
        assert "from odoo.addons.cd_tax_engine_bd.models import tax_logic" in source
        assert "tax_logic.determine_tax" in source

    def test_m20_to_m50_is_strictly_asynchronous_events(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine", fromlist=["FixArInvoice"]
            )
        )
        assert "cd_cash_position" not in source
        assert "action_register_paid" in source
        assert '"invoice.paid"' in source


class TestDunning:
    def test_ageing_buckets_declared(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixDunning

        buckets = dict(FixDunning.bucket.selection)
        assert set(buckets.values()) >= {"Current", "1-30", "31-60", "61-90", "90+"}


class TestCreditNote:
    def test_direct_band_is_the_05_04_finance_officer_limit(self):
        """A08 S3 (rewritten: the old constant was the 25,000 base.group_system
        threshold). 05-04 §7: credit note <= BDT 10,000 Finance Officer, above
        it Finance Manager — a configurable band, never a self-approval."""
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import (
            DEFAULT_DIRECT_LIMIT,
            PARAM_CREDIT_DIRECT,
            FixCreditNote,
        )

        assert DEFAULT_DIRECT_LIMIT == 10000.0
        assert FixCreditNote._fin_direct_param == PARAM_CREDIT_DIRECT

    def test_issue_requires_approval(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine",
                fromlist=["FixCreditNote"],
            ).FixCreditNote.action_issue
        )
        assert "Approve before issuing" in source


class TestConsolidatedBill:
    def test_model_exists_and_inherits_mail(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixArConsolidatedBill

        assert FixArConsolidatedBill is not None
        assert "mail.thread" in FixArConsolidatedBill._inherit

    def test_generation_action_emits_event(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_billing_engine.models.fix_billing_engine",
                fromlist=["FixArConsolidatedBill"],
            ).FixArConsolidatedBill.action_generate
        )
        assert '"consolidated_bill.generated"' in source
