# ensure_legacy_account (2026-11-11 fix_real audit): the take-on wizards
# created their contra / unallocated-receipts accounts with a create that,
# on any exception, created again through a fallback writing the code as a
# stringified dict. The first create had already inserted its row, so the
# real chart carried two "Legacy Ledger Take-on Contra" accounts with one
# code and an account coded "{'1': '2-99-99-902'}".
from __future__ import annotations

import uuid
from unittest import mock

import pytest
from odoo.addons.cd_gl_ext.models.fix_gl_ext import ensure_legacy_account
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]


def _code():
    return "9.99.%s" % uuid.uuid4().hex[:6]


def _accounts(env, code):
    return env["account.account"].search([("code", "=", code)])


class TestEnsureLegacyAccount:
    def test_the_take_on_codes_are_valid_odoo_account_codes(self, odoo_env):
        """A dashed code never validates in Odoo 19 - the cause of the
        duplicates. The wizards' own codes must create cleanly."""
        for code in ("2.99.99.901", "2.99.99.902"):
            if _accounts(odoo_env, code):
                continue
            acc = ensure_legacy_account(
                odoo_env, odoo_env.company, "TEST %s" % code, code, "liability_current"
            )
            assert acc.code == code

    def test_created_once_with_a_real_code(self, odoo_env):
        company, code = odoo_env.company, _code()
        first = ensure_legacy_account(
            odoo_env, company, "TEST contra %s" % code, code, "liability_current"
        )
        second = ensure_legacy_account(
            odoo_env, company, "TEST contra %s" % code, code, "liability_current"
        )
        assert first == second
        assert len(_accounts(odoo_env, code)) == 1
        assert first.code == code  # never a stringified dict

    def test_an_existing_code_is_reused_whatever_its_name(self, odoo_env):
        company, code = odoo_env.company, _code()
        existing = odoo_env["account.account"].create(
            {"name": "TEST renamed %s" % code, "code": code, "account_type": "liability_current"}
        )
        got = ensure_legacy_account(odoo_env, company, "Another name", code, "liability_current")
        assert got == existing

    def test_a_failed_create_refuses_and_leaves_no_account(self, odoo_env):
        company, code = odoo_env.company, _code()
        Account = type(odoo_env["account.account"])
        with (
            mock.patch.object(Account, "create", side_effect=ValueError("boom")),
            pytest.raises(UserError, match="Could not create account"),
        ):
            ensure_legacy_account(
                odoo_env, company, "TEST fail %s" % code, code, "liability_current"
            )
        assert not _accounts(odoo_env, code)
