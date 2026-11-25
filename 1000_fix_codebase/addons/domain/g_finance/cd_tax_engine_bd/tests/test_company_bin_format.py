# 2026-11-11 fix_real audit: the company's real BIN is kept as NBR prints it,
# `001821833-0401`. Read raw it is 14 characters; the resolvers stripped only
# spaces, so every Mushak 6.3 issue and every VAT return was refused with
# "Company has no valid 13-digit BIN" (and the 13-character register fields
# cut it to `001821833-040`). The BIN is now normalised to its digits.
#
# M51-F12 / X-1 (A08 audit, Nov 2026): the BUYER BIN suffered the mirror
# defect. A customer whose BIN is stored in the same NBR print format was
# silently dropped by the native registration path (space-stripping is not
# normalisation), so the Mushak 6.3 printed without the buyer BIN Rule 40(1)
# requires for registered buyers; and the billing-engine path fed the raw
# value to the register's _check_bins constraint, refusing the whole invoice
# issuance. Both paths now normalise; valid_bin stays the acceptance test.
from __future__ import annotations

import pytest
from odoo import fields
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


@pytest.fixture
def native_invoice(odoo_env, company):
    """A posted native sales invoice for a buyer whose BIN is whatever the
    caller set — posting itself registers the Mushak 6.3 (B4's hook)."""

    def _invoice(vat):
        env = odoo_env
        buyer = env["res.partner"].create({"name": "Grouped BIN Buyer", "vat": vat})
        tax = env["account.tax"].search(
            [
                ("company_id", "=", company.id),
                ("type_tax_use", "=", "sale"),
                ("amount_type", "=", "percent"),
                ("amount", "=", 15.0),
            ],
            limit=1,
        )
        if not tax:
            group = env["account.tax.group"].search([("company_id", "=", company.id)], limit=1)
            tax = env["account.tax"].create(
                {
                    "name": "M51-F12 VAT 15",
                    "amount": 15.0,
                    "amount_type": "percent",
                    "type_tax_use": "sale",
                    "company_id": company.id,
                    **({"tax_group_id": group.id} if group else {}),
                }
            )
        product = env["product.product"].create(
            {"name": "M51-F12 repair", "default_code": "M51F12"}
        )
        move = env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": buyer.id,
                "invoice_date": fields.Date.context_today(env.user),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": 2000.0,
                            "tax_ids": [(6, 0, tax.ids)],
                        },
                    )
                ],
            }
        )
        move.action_post()
        return move

    return _invoice


class TestCustomerBinOnTheRegister:
    """M51-F12: the buyer BIN is normalised in BOTH issue paths; a
    grouped-format BIN reaches the Mushak 6.3 / the register, a genuinely
    invalid one is dropped without refusing the registration."""

    def test_grouped_buyer_bin_lands_normalised(self, odoo_env, company, native_invoice):
        move = native_invoice(REAL_BIN_PRINTED)
        row = odoo_env["fix.mushak.register"].search([("source_move_id", "=", move.id)])
        assert row, "posting registered the 6.3 row"
        assert row.customer_bin == REAL_BIN  # digits only, not the raw print form
        # idempotent re-registration keeps the normalised BIN
        assert odoo_env["fix.mushak.register"]._fix_register_from_invoice(move) == row
        assert row.customer_bin == REAL_BIN

    def test_invalid_buyer_bin_is_dropped_not_rejected(self, odoo_env, company, native_invoice):
        move = native_invoice("BIN-PENDING")  # a genuinely invalid BIN
        row = odoo_env["fix.mushak.register"].search([("source_move_id", "=", move.id)])
        assert row, "issuance was NOT refused for the buyer BIN's format"
        assert not row.customer_bin  # dropped, exactly as before
        assert row.supplier_bin == REAL_BIN  # the company side still carries its BIN

    def test_the_event_replay_normalises_a_raw_payload_bin(self, odoo_env, company):
        Register = odoo_env["fix.mushak.register"]
        row = Register.create(
            {
                "company_id": company.id,
                "operating_unit_id": odoo_env["operating.unit"]
                .search([("company_id", "=", company.id)], limit=1)
                .id,
                "row_type": "invoice",
                "mushak_no": "2026-900001",
                "invoice_ref": "M51F12/%s" % company.id,
                "invoice_date": fields.Date.context_today(odoo_env.user),
                "supplier_name": company.name,
                "supplier_bin": REAL_BIN,
                "customer_name": "Replay Buyer",
                "taxable_amount": 100.0,
                "vat_amount": 15.0,
                "total_payable": 115.0,
            }
        )
        replayed = Register.consume_invoice_created(
            {
                "event_id": "evt-m51f12-replay-%s" % company.id,
                "payload": {
                    "mushak_no": "2026-900002",
                    "invoice_ref": "M51F12B/%s" % company.id,
                    "invoice_date": str(fields.Date.context_today(odoo_env.user)),
                    "supplier_name": company.name,
                    "supplier_bin": REAL_BIN,
                    "customer_name": "Replay Buyer",
                    # a pre-fix event carries the raw print form
                    "customer_bin": REAL_BIN_PRINTED,
                    "taxable_amount": 50.0,
                    "vat_amount": 7.5,
                    "total_payable": 57.5,
                    "operating_unit_id": row.operating_unit_id.id,
                },
            }
        )
        assert replayed.customer_bin == REAL_BIN
        assert replayed != row
