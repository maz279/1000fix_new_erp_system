# 2026-11-11 fix_real audit: the company's real BIN is kept as NBR prints it,
# `001821833-0401`. Read raw it is 14 characters; the resolvers stripped only
# spaces, so every Mushak 6.3 issue and every VAT return was refused with
# "Company has no valid 13-digit BIN" (and the 13-character register fields
# cut it to `001821833-040`). The BIN is now normalised to its digits.
from __future__ import annotations

import pytest
from odoo.addons.cd_tax_engine_bd.models.fix_tax_engine import normalize_bin, valid_bin
from odoo.addons.cd_tax_engine_bd.models.fix_tax_returns import _company_bin
from odoo.exceptions import UserError

REAL_BIN_PRINTED = "001821833-0401"
REAL_BIN = "0018218330401"


def test_normalize_keeps_only_the_digits():
    assert normalize_bin(REAL_BIN_PRINTED) == REAL_BIN
    assert normalize_bin(" 001821833 0401 ") == REAL_BIN
    assert normalize_bin(None) == ""
    assert valid_bin(normalize_bin(REAL_BIN_PRINTED))


@pytest.fixture
def company(odoo_env):
    company = odoo_env.company
    company.partner_id.vat = REAL_BIN_PRINTED
    return company


class TestCompanyBinResolvers:
    def test_mushak_register_reads_the_printed_bin(self, odoo_env, company):
        Register = odoo_env["fix.mushak.register"]
        assert Register._fix_company_bin(company) == REAL_BIN

    def test_vat_return_reads_the_printed_bin(self, odoo_env, company):
        assert _company_bin(company) == REAL_BIN

    def test_billing_reads_the_printed_bin(self, odoo_env, company):
        if "fix.ar.invoice" not in odoo_env:
            pytest.skip("cd_billing_engine not installed")
        Engine = odoo_env["fix.ar.invoice"]
        if not hasattr(Engine, "_company_bin"):
            pytest.skip("billing BIN resolver lives on another model in this build")
        assert Engine._company_bin(company) == REAL_BIN

    @pytest.mark.parametrize("bad", ["12345", "0000000000000", "00182183304011", "BIN-PENDING"])
    def test_a_bin_that_is_not_13_real_digits_is_still_refused(self, odoo_env, company, bad):
        company.partner_id.vat = bad
        with pytest.raises(UserError, match="13-digit BIN"):
            odoo_env["fix.mushak.register"]._fix_company_bin(company)
        with pytest.raises(UserError, match="13-digit BIN"):
            _company_bin(company)
