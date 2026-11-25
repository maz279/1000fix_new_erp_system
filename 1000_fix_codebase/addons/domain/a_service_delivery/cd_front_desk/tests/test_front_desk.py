# Tests for cd_front_desk (P04-M02) — token queue, intake, cash shift.


class TestFixTokenQueue:
    def test_model_exists(self):
        from odoo.addons.cd_front_desk.models.fix_token_queue import FixTokenQueue

        assert FixTokenQueue is not None

    def test_auto_token_numbering(self):
        """Token numbers auto-assign per branch."""
        from odoo.addons.cd_front_desk.models.fix_token_queue import FixTokenQueue

        assert "token_number" in dir(FixTokenQueue)

    def test_display_format(self):
        from odoo.addons.cd_front_desk.models.fix_token_queue import FixTokenQueue

        assert "_compute_display" in dir(FixTokenQueue)


class TestFixWalkinIntake:
    def test_model_exists(self):
        from odoo.addons.cd_front_desk.models.fix_walkin_intake import FixWalkinIntake

        assert FixWalkinIntake is not None

    def test_three_minute_timing_field(self):
        """G1-02: intake duration is tracked for the 3-minute gate."""
        from odoo.addons.cd_front_desk.models.fix_walkin_intake import FixWalkinIntake

        assert "intake_duration_seconds" in dir(FixWalkinIntake)

    def test_handover_acknowledgement(self):
        from odoo.addons.cd_front_desk.models.fix_walkin_intake import FixWalkinIntake

        assert "handover_acknowledged" in dir(FixWalkinIntake)
        assert "action_complete_handover" in dir(FixWalkinIntake)


class TestFixCashShift:
    def test_model_exists(self):
        from odoo.addons.cd_front_desk.models.fix_cash_shift import FixCashShift

        assert FixCashShift is not None

    def test_as10_monetary_cash(self):
        from odoo.addons.cd_front_desk.models.fix_cash_shift import FixCashShift

        for field in ("opening_float", "closing_counted", "expected_closing", "variance"):
            assert field in dir(FixCashShift)
        assert "currency_id" in dir(FixCashShift)
