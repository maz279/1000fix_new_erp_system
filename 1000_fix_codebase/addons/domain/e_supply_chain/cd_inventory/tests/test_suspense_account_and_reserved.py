# 2026-11-11 fix_real audit: two defects the real-inventory reload exposed.
#
# 1. Every valuation-suspense row was stamped with account code 110999, which
#    is not on the company's real chart; the period close resolves that code
#    and refuses, so the first stock movement would have blocked every close.
#    The code now comes from cd_inventory.valuation_suspense_account_code.
# 2. A new stock bucket stored `reserved` as SQL NULL (no default, not set on
#    create), so SQL / BI sums over the ledger read NULL instead of 0.
from __future__ import annotations

import pytest
from odoo.addons.cd_inventory.models.fix_valuation_suspense import (
    DEFAULT_SUSPENSE_ACCOUNT_CODE,
    SUSPENSE_ACCOUNT_PARAM,
    suspense_account_code,
)

pytestmark = [pytest.mark.financial]


def _set(env, value):
    env["ir.config_parameter"].sudo().set_param(SUSPENSE_ACCOUNT_PARAM, value)


class TestSuspenseAccountCode:
    def test_unset_parameter_keeps_the_development_chart_code(self, odoo_env):
        _set(odoo_env, False)
        assert suspense_account_code(odoo_env) == DEFAULT_SUSPENSE_ACCOUNT_CODE == "110999"

    def test_parameter_names_the_account_new_rows_carry(self, odoo_env):
        _set(odoo_env, " 100501 ")
        assert suspense_account_code(odoo_env) == "100501"
        Suspense = odoo_env["fix.inventory.valuation.suspense"]
        defaults = Suspense.default_get(["suspense_account_code"])
        assert defaults["suspense_account_code"] == "100501"


class TestReservedIsNeverNull:
    def test_a_new_bucket_stores_reserved_as_zero(self, inv):
        """Built from the shared inventory fixture: its own part and location,
        so the test never depends on what the database happens to hold."""
        Ledger = inv.env["fix.stock.onhand"]
        assert Ledger._fields["reserved"].default(Ledger) == 0.0
        part = inv.env["fix.spare.part"].create(
            {"name": "Reserved probe", "part_number": "RSV-" + inv.tag, "unit_cost": 10.0}
        )
        assert not inv.bucket(part, inv.central), "the bucket must be NEW for this test"
        row = inv.stock(part, inv.central, 3.0, 10.0)
        row.flush_recordset()
        inv.env.cr.execute("SELECT reserved, qty FROM fix_stock_onhand WHERE id = %s", (row.id,))
        assert inv.env.cr.fetchone() == (0.0, 3.0)
