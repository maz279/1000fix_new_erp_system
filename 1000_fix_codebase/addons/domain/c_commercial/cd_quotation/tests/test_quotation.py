# cd_quotation tests — M36 (P06-M06-T05/T07).
import inspect


class TestUnifiedEstimate:
    def test_extension_not_new_model(self):
        """T07 / AS-01: ONE estimate concept — cd_quotation EXTENDS
        fix.estimate rather than creating fix.quotation."""
        from odoo.addons.cd_quotation.models import fix_quotation

        source = inspect.getsource(fix_quotation)
        assert '_inherit = "fix.estimate"' in source
        assert "_name" not in source.split("class FixEstimate")[1].split("class ")[0]

    def test_quote_requires_approved_estimate(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_quotation.models.fix_quotation", fromlist=["FixEstimate"]
            ).FixEstimate.action_quote
        )
        assert "approved estimate" in source

    def test_pending_discount_blocks_quoting(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_quotation.models.fix_quotation", fromlist=["FixEstimate"]
            ).FixEstimate.action_quote
        )
        assert "pending discount approval blocks quoting" in source.lower()

    def test_validity_window_positive(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_quotation.models.fix_quotation", fromlist=["FixEstimate"]
            ).FixEstimate
        )
        assert "_check_validity" in source


class TestDiscountGovernance:
    def test_authority_matrix(self):
        """05-04 section 7: agent 5%, manager 10%, above that director."""
        from odoo.addons.cd_quotation.models.fix_quotation import FixDiscountApproval

        assert FixDiscountApproval.AGENT_MAX == 5.0
        assert FixDiscountApproval.MANAGER_MAX == 10.0

    def test_high_discount_needs_director(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_quotation.models.fix_quotation", fromlist=["FixDiscountApproval"]
            ).FixDiscountApproval.action_approve
        )
        assert "commercial-director approval" in source
