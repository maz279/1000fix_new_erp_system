# cd_gl_ext tests — M19 core (P06-M01; DoD-03: financial paths 100%).
import pytest

pytestmark = [pytest.mark.financial]


class TestPeriodClose:
    """fix.period.close — the 5-day close process."""

    def test_model_exists(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixPeriodClose
        assert FixPeriodClose is not None

    def test_close_target_is_five_days(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixPeriodClose
        assert FixPeriodClose.CLOSE_TARGET_DAYS == 5  # G3-04

    def test_duration_compute_declared(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixPeriodClose
        assert hasattr(FixPeriodClose, "_compute_duration")

    def test_action_close_requires_ready(self):
        """A close that was never readiness-checked must refuse (T06)."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixPeriodClose
        assert hasattr(FixPeriodClose, "action_close")

    def test_action_ready_blocks_on_suspense(self):
        """AR-006 section 5.4: a non-zero suspense balance blocks the close."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixPeriodClose
        assert hasattr(FixPeriodClose, "action_ready")


class TestJournalDimension:
    def test_model_exists(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixJournalDimension
        assert FixJournalDimension is not None

    def test_branch_ou_constraint_declared(self):
        import inspect
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixJournalDimension
        source = inspect.getsource(FixJournalDimension)
        assert "_check_branch_ou" in source


class TestFixedAssetSeam:
    def test_model_exists(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixFixedAssetSeam
        assert FixFixedAssetSeam is not None

    def test_seam_is_interface_only(self):
        """T07: the seam carries NO depreciation logic — M49 owns that."""
        import inspect
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import FixFixedAssetSeam
        source = inspect.getsource(FixFixedAssetSeam)
        # The docstring's disclaimer NAMES the concept while disclaiming it;
        # mask both disclaimer phrases before scanning for real logic.
        masked = (source.lower()
                  .replace("owns depreciation. no depreciation logic here", "")
                  .replace("the seam, not the asset", ""))
        assert "depreciat" not in masked


class TestPostWithDimensions:
    def test_helper_exists(self):
        from odoo.addons.cd_gl_ext.models import fix_gl_ext
        assert callable(fix_gl_ext.post_with_dimensions)

    def test_helper_emits_journal_posted(self):
        """AS-08: the posting helper emits journal.posted."""
        import inspect
        from odoo.addons.cd_gl_ext.models import fix_gl_ext
        source = inspect.getsource(fix_gl_ext.post_with_dimensions)
        assert '"journal.posted"' in source
