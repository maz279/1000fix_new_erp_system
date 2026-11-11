# fix.ledger.takeon — control-account resolution (2026-11-10 fix_real audit).
#
# The wizard used to fall back to "the first account of the right type". On a
# chart that keeps its own legacy codes (the real 376-account chart has three
# receivable and nine payable accounts) that row is arbitrary: first-by-code
# is 100029 "Advance Loan (Office Employee)", so every customer opening
# balance would have landed on the staff-loan account. The resolver now takes
# an explicit estate parameter and refuses an ambiguous chart.
from __future__ import annotations

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

PARAM = "cd_gl_ext.ledger_takeon.%s"


@pytest.fixture()
def batch(odoo_env):
    return odoo_env["fix.ledger.takeon.batch"].create(
        {
            "name": "TEST partner-ledger take-on",
            "import_ref": "LEDGER-TEST-CTRL",
            "takeon_date": "2026-11-01",
        }
    )


def _account(env, code, name, account_type):
    return env["account.account"].create({"code": code, "name": name, "account_type": account_type})


def _set(env, key, value):
    env["ir.config_parameter"].sudo().set_param(PARAM % key, value)


def _strip_statutory_defaults(env, kind):
    """Leave the chart as a legacy chart would be: no estate chart link and
    no statutory 121000/211000 code for `kind`."""
    if "fix.chart.account" in env:
        env.cr.execute(
            "UPDATE fix_chart_account SET odoo_account_id = NULL WHERE control_subledger = %s",
            (kind,),
        )
        env["fix.chart.account"].invalidate_model(["odoo_account_id"])
    code = "121000" if kind == "receivable" else "211000"
    statutory = env["account.account"].search([("code", "=", code)])
    if statutory:
        statutory.write({"code": "9%s" % code[1:]})


class TestLedgerTakeonControlAccount:
    def test_parameter_names_the_receivable_control_account(self, odoo_env, batch):
        # two receivable accounts whose codes sort BEFORE the real control
        # account, exactly like 100029 sorts before 100201 on the real chart
        _account(odoo_env, "100029T", "TEST Advance Loan (Office Employee)", "asset_receivable")
        control = _account(odoo_env, "100201T", "TEST Account Receivable", "asset_receivable")
        _set(odoo_env, "receivable_account_code", "100201T")
        assert batch._control_account("receivable") == control

    def test_parameter_names_the_payable_control_account(self, odoo_env, batch):
        _account(odoo_env, "200012T", "TEST A/P Local Supplier", "liability_payable")
        control = _account(odoo_env, "200101T", "TEST Account Payable", "liability_payable")
        _set(odoo_env, "payable_account_code", "200101T")
        assert batch._control_account("payable") == control

    def test_parameter_naming_a_missing_account_is_refused(self, odoo_env, batch):
        _set(odoo_env, "receivable_account_code", "NO-SUCH-CODE")
        with pytest.raises(UserError, match="does not exist"):
            batch._control_account("receivable")

    def test_parameter_naming_the_wrong_account_type_is_refused(self, odoo_env, batch):
        _account(odoo_env, "100502T", "TEST Stock Of Inventory", "asset_current")
        _set(odoo_env, "receivable_account_code", "100502T")
        with pytest.raises(UserError, match="not of type asset_receivable"):
            batch._control_account("receivable")

    @pytest.mark.parametrize(
        ("kind", "atype"),
        [("receivable", "asset_receivable"), ("payable", "liability_payable")],
    )
    def test_ambiguous_chart_without_parameter_is_refused(self, odoo_env, batch, kind, atype):
        _strip_statutory_defaults(odoo_env, kind)
        _account(odoo_env, "T%s01" % kind[:3], "TEST first %s" % kind, atype)
        _account(odoo_env, "T%s02" % kind[:3], "TEST second %s" % kind, atype)
        with pytest.raises(UserError, match="%s_account_code" % kind):
            batch._control_account(kind)

    def test_single_candidate_chart_still_resolves_by_type(self, odoo_env, batch):
        _strip_statutory_defaults(odoo_env, "payable")
        Account = odoo_env["account.account"]
        Account.search([("account_type", "=", "liability_payable")]).write(
            {"account_type": "liability_current"}
        )
        only = _account(odoo_env, "TPAY01", "TEST the only payable", "liability_payable")
        assert batch._control_account("payable") == only

    def test_suspense_kind_reads_its_own_parameter(self, odoo_env, batch):
        offset = _account(odoo_env, "300101T", "TEST Data Migration Offset", "equity")
        _set(odoo_env, "suspense_stock_migration_account_code", "300101T")
        assert batch._configured_account("suspense_stock_migration_account_code") == offset
        # an unset kind falls through to the built-in mapping
        assert not batch._configured_account("suspense_office_use_account_code")
