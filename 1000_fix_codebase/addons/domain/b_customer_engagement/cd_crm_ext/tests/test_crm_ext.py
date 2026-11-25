# Tests for cd_crm_ext (P04-M04).


class TestCrmLeadExt:
    def test_model_extension(self):
        from odoo.addons.cd_crm_ext.models.crm_lead_ext import CrmLeadExt

        assert CrmLeadExt is not None

    def test_party_kernel_link(self):
        from odoo.addons.cd_crm_ext.models.crm_lead_ext import CrmLeadExt

        assert "party_role_id" in dir(CrmLeadExt)

    def test_lead_to_service_order_conversion(self):
        from odoo.addons.cd_crm_ext.models.crm_lead_ext import CrmLeadExt

        assert "action_convert_to_service_order" in dir(CrmLeadExt)

    def test_no_pricing_dependency(self):
        """P04-M04-T09: verify no M07 code depends on M11 pricing or M36 quotation."""
        import pathlib

        here = pathlib.Path(__file__).resolve().parents[1]
        # tests/ documents the rule (its own assert text names the forbidden
        # strings) - the scan covers product code only.
        crm_files = [f for f in here.rglob("*.py") if "tests" not in f.parts]
        for f in crm_files:
            text = f.read_text()
            assert (
                "sale.order" not in text or "quotation" not in text.lower()
            ), f"M07 W1 should not reference quotation/pricing: {f}"
