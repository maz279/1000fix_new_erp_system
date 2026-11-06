# cd_cash_position tests — M50 core (P06-M04): registry-free checks.
#
# A08 workflow audit (2026-11-04): the source-grep tests that lived here
# (inspect.getsource(...) contains "payment.executed" / "payload" /
# "fix.cash.shift") proved nothing about behaviour and were removed; the
# behaviour they pointed at is executed in test_treasury_a08.py (payment.executed
# published once, on the bank's confirmation), test_cash_position_orm.py (the
# payment.requested consumer, the drawer total) and test_a08_m50_controls.py.


class TestPaymentExecution:
    def test_idempotent_on_source_key(self):
        """DI-04: a replayed payment.requested never double-pays."""
        from odoo.addons.cd_cash_position.models.fix_cash_position import FixPaymentExecution

        assert hasattr(FixPaymentExecution, "_request_key_unique")  # Odoo 19 models.Constraint attr

    def test_release_ladder_defaults_route_every_release(self):
        """No dual-authorisation value in the M50 spec (BRU-TRE-12 'the
        configured value'): the single-releaser ceiling defaults to 0 and the
        bands are the 05-04 §7 cash-commitment bands."""
        from odoo.addons.cd_cash_position.models import fix_cash_position as m

        assert m.DEFAULT_RELEASE_LADDER == {
            m.PARAM_SINGLE_CEILING: 0.0,
            m.PARAM_TIER2: 50000.0,
            m.PARAM_TIER3: 500000.0,
            m.PARAM_TIER4: 2000000.0,
        }

    def test_self_posting_sources(self):
        from odoo.addons.cd_cash_position.models.fix_cash_position import SELF_POSTING_SOURCES

        assert {"fix.payment.run.line", "fix.employee.advance"} == SELF_POSTING_SOURCES


class TestBankReconciliation:
    def test_match_states(self):
        from odoo.addons.cd_cash_position.models.fix_cash_position import FixBankStatementLine

        states = dict(FixBankStatementLine.match_state.selection)
        assert set(states) == {"unmatched", "auto", "manual"}

    def test_auto_match_ladder_supports_ar_ap_and_exp(self):
        from odoo.addons.cd_cash_position.models.fix_cash_position import LEGACY_PREFIX

        assert set(LEGACY_PREFIX.values()) == {"AR", "AP", "EXP"}

    def test_reference_match_is_whole_token(self):
        """A08: 'AR/5' must not match inside 'AR/55' (the old substring rule did)."""
        from odoo.addons.cd_cash_position.models.treasury_common import has_token

        assert has_token("paid AR/5 ok", "AR/5")
        assert not has_token("paid AR/55", "AR/5")
        assert not has_token("", "AR/5")
