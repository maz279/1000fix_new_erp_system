# Tests for cd_document_core (P03-M07) — document kernel + retention.
import pytest


class TestFixDocument:
    def test_model_exists(self):
        from addons.platform.cd_document_core.models.fix_document import FixDocument
        assert FixDocument is not None

    def test_attach_api(self):
        """The one API every W1-W2 module calls (P03-M07-T06)."""
        from addons.platform.cd_document_core.models.fix_document import FixDocument
        assert 'attach' in dir(FixDocument)

    def test_retention_compute(self):
        from addons.platform.cd_document_core.models.fix_document import FixDocument
        assert '_compute_retention' in dir(FixDocument)

    def test_as14_residency_flag(self):
        from addons.platform.cd_document_core.models.fix_document import FixDocument
        assert 'is_residency_classified' in dir(FixDocument)


class TestFixRetentionClass:
    def test_model_exists(self):
        from addons.platform.cd_document_core.models.fix_retention_class import FixRetentionClass
        assert FixRetentionClass is not None

    def test_code_unique(self):
        from addons.platform.cd_document_core.models.fix_retention_class import FixRetentionClass
        assert hasattr(FixRetentionClass, "_code_unique")  # Odoo 19 models.Constraint attr
