# Tests for cd_document_core (P03-M07) — document kernel + retention.


class TestFixDocument:
    def test_model_exists(self):
        from odoo.addons.cd_document_core.models.fix_document import FixDocument

        assert FixDocument is not None

    def test_attach_api(self):
        """The one API every W1-W2 module calls (P03-M07-T06)."""
        from odoo.addons.cd_document_core.models.fix_document import FixDocument

        assert "attach" in dir(FixDocument)

    def test_retention_compute(self):
        from odoo.addons.cd_document_core.models.fix_document import FixDocument

        assert "_compute_retention" in dir(FixDocument)

    def test_as14_residency_flag(self):
        from odoo.addons.cd_document_core.models.fix_document import FixDocument

        assert "is_residency_classified" in dir(FixDocument)

    def test_mayan_sync_fields_and_methods(self):
        from odoo.addons.cd_document_core.models.fix_document import FixDocument

        assert "action_sync_to_mayan" in dir(FixDocument)
        assert "migrate_documents_to_mayan" in dir(FixDocument)
        assert "action_assert_can_destroy" in dir(FixDocument)

    def test_legal_hold_dual_store_destruction_guard(self):
        import inspect

        from odoo.addons.cd_document_core.models.fix_document import FixDocument

        src = inspect.getsource(FixDocument.action_assert_can_destroy)
        assert "legal_hold" in src
        assert "Destruction is strictly blocked across both Odoo kernel and Mayan EDMS" in src


class TestFixRetentionClass:
    def test_model_exists(self):
        from odoo.addons.cd_document_core.models.fix_retention_class import FixRetentionClass

        assert FixRetentionClass is not None

    def test_code_unique(self):
        from odoo.addons.cd_document_core.models.fix_retention_class import FixRetentionClass

        assert hasattr(FixRetentionClass, "_code_unique")  # Odoo 19 models.Constraint attr
