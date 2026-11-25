# Tests for cd_mdm_core (P03-M07) — MDM governance core.


class TestFixMdmChangeRequest:
    def test_model_exists(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_change_request import FixMdmChangeRequest

        assert FixMdmChangeRequest is not None

    def test_state_machine(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_change_request import FixMdmChangeRequest

        assert "action_submit" in dir(FixMdmChangeRequest)
        assert "action_approve" in dir(FixMdmChangeRequest)
        assert "action_reject" in dir(FixMdmChangeRequest)

    def test_snapshot_method(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_change_request import FixMdmChangeRequest

        assert "_snapshot_current" in dir(FixMdmChangeRequest)


class TestFixMdmGoldenRule:
    def test_model_exists(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_golden_rule import FixMdmGoldenRule

        assert FixMdmGoldenRule is not None

    def test_resolve_method(self):
        """The survivorship engine's resolve() API."""
        from odoo.addons.cd_mdm_core.models.fix_mdm_golden_rule import FixMdmGoldenRule

        assert "resolve" in dir(FixMdmGoldenRule)

    def test_model_field_unique(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_golden_rule import FixMdmGoldenRule

        assert hasattr(FixMdmGoldenRule, "_model_field_unique")  # Odoo 19 models.Constraint attr


class TestFixMdmMatchRule:
    def test_model_exists(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_match_rule import FixMdmMatchRule

        assert FixMdmMatchRule is not None


class TestFixMdmStewardship:
    def test_model_exists(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_stewardship import FixMdmStewardship

        assert FixMdmStewardship is not None
        assert FixMdmStewardship._name == "fix.mdm.stewardship"

    def test_quality_index_compute_and_actions(self):
        from odoo.addons.cd_mdm_core.models.fix_mdm_stewardship import FixMdmStewardship

        assert "_compute_quality_index" in dir(FixMdmStewardship)
        assert "action_audit_data_quality" in dir(FixMdmStewardship)
        assert hasattr(FixMdmStewardship, "_domain_company_unique")
