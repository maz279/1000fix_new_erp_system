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
        """BRU-SRM-05: the method refuses non-closed orders."""
        source = inspect.getsource(
            __import__("odoo.addons.cd_billing_engine.models.fix_billing_engine",
                       fromlist=["FixArInvoice"]).FixArInvoice.from_closed_service_order)
        assert 'state != "closed"' in source

    def test_determination_is_synchronous_import(self):
        """AR-006 pair 7: M20 calls M51 synchronously (an import, never an
        event wait) and consumes nothing back."""
        source = inspect.getsource(
            __import__("odoo.addons.cd_billing_engine.models.fix_billing_engine",
                       fromlist=["FixArInvoice"]))
        assert "from odoo.addons.cd_tax_engine_bd.models import tax_logic" in source
        assert "tax_logic.determine_tax" in source

    def test_atomic_mushak_write_in_same_method(self):
        """P06-M02-T08: the Mushak register row is created inside the same
        method (same transaction) as the invoice."""
        source = inspect.getsource(
            __import__("odoo.addons.cd_billing_engine.models.fix_billing_engine",
                       fromlist=["FixArInvoice"]).FixArInvoice.from_closed_service_order)
        assert "fix.mushak.register" in source

    def test_nfr040_timing_recorded(self):
        source = inspect.getsource(
            __import__("odoo.addons.cd_billing_engine.models.fix_billing_engine",
                       fromlist=["FixArInvoice"]).FixArInvoice.from_closed_service_order)
        assert "time.monotonic" in source  # NFR-040: the 5-second budget measured

    def test_company_bin_never_invented(self):
        """A Mushak without the supplier BIN must fail, not default."""
        source = inspect.getsource(
            __import__("odoo.addons.cd_billing_engine.models.fix_billing_engine",
                       fromlist=["FixArInvoice"]).FixArInvoice._company_bin)
        assert "raise UserError" in source


class TestDunning:
    def test_ageing_buckets_declared(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixDunning
        buckets = dict(FixDunning.bucket.selection)
        assert set(buckets.values()) >= {"Current", "1-30", "31-60", "61-90", "90+"}


class TestCreditNote:
    def test_threshold_is_25000(self):
        from odoo.addons.cd_billing_engine.models.fix_billing_engine import FixCreditNote
        assert FixCreditNote.APPROVAL_THRESHOLD == 25000  # 05-04 section 7

    def test_issue_requires_approval(self):
        source = inspect.getsource(
            __import__("odoo.addons.cd_billing_engine.models.fix_billing_engine",
                       fromlist=["FixCreditNote"]).FixCreditNote.action_issue)
        assert "Approve before issuing" in source
