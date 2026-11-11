# cd_tax_engine_bd — owner-approved fixes of 12 Nov 2026 (third rehearsal).
#
#   E3-12  a decreasing adjustment (supplier credit note, Mushak 6.7) was always
#          'eligible', even when the credit it reduces was ineligible (no BIN):
#          the 9.1 then deducted input VAT that was never claimed. Its verdict
#          now mirrors the original credit's, and follows it when the original
#          is re-checked.
#   E3-13  the TDS engine's contract for a credit note on goods returned: a
#          deduction still 'withheld' falls by the returned share against the
#          note's posted entry that debits the TDS payable; a deposited or
#          certified deduction is never edited.
from __future__ import annotations

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial, pytest.mark.tax]


@pytest.fixture
def tx(odoo_env):
    env = odoo_env
    company = env.company
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    Account = env["account.account"]

    def acc(code, name, kind):
        found = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        return found or Account.create(
            {
                "code": code,
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, [company.id])],
            }
        )

    tds = acc("990253", "Test TDS payable", "liability_current")
    other = acc("990254", "Test TDS counter-account", "liability_current")
    env["ir.config_parameter"].sudo().set_param(
        "cd_tax_engine_bd.account_code.tds_payable", "990253"
    )
    journal = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "general")], limit=1
    )
    supplier = env["res.partner"].create({"name": "E3 Tax Supplier"})
    return {
        "env": env,
        "company": company,
        "ou": ou,
        "tds": tds,
        "other": other,
        "journal": journal,
        "supplier": supplier,
    }


def _credit(t, **vals):
    return t["env"]["fix.input.vat.credit"].create(
        {
            "partner_id": t["supplier"].id,
            "supplier_bin": "9876543210123",
            "supplier_mushak_no": "63-E3",
            "invoice_date": "2026-11-05",
            "taxable_amount": 29600.0,
            "vat_amount": 4440.0,
            **vals,
        }
    )


def _decrease(t, original, **vals):
    return _credit(
        t,
        adjustment_type="decrease",
        original_credit_id=original.id if original else False,
        supplier_mushak_no="67-E3",
        invoice_date="2026-11-11",
        taxable_amount=7400.0,
        vat_amount=1110.0,
        **vals,
    )


def test_e3_12_decrease_against_an_ineligible_credit_is_ineligible(tx):
    original = _credit(tx, supplier_bin=False)  # D2-02: no BIN
    original.action_check_eligibility()
    assert original.state == "ineligible"
    dec = _decrease(tx, original, supplier_bin=False)
    dec.action_check_eligibility()
    assert dec.state == "ineligible"
    assert "not claimable" in dec.ineligible_reason


def test_e3_12_decrease_against_an_eligible_credit_is_eligible(tx):
    original = _credit(tx)
    original.action_check_eligibility()
    assert original.state == "eligible"
    dec = _decrease(tx, original)
    dec.action_check_eligibility()
    assert dec.state == "eligible"


def test_e3_12_decrease_follows_its_original_when_that_is_rechecked(tx):
    original = _credit(tx, supplier_bin=False)
    original.action_check_eligibility()
    dec = _decrease(tx, original, supplier_bin=False)
    dec.action_check_eligibility()
    assert dec.state == "ineligible"
    original.supplier_bin = "9876543210123"  # the BIN is captured later
    original.action_check_eligibility()
    assert original.state == "eligible" and dec.state == "eligible"


def test_e3_12_unlinked_decrease_is_still_reported(tx):
    dec = _decrease(tx, None)
    dec.action_check_eligibility()
    assert dec.state == "eligible"


# ----------------------------------------------------------- E3-13 contract --
def _posted(t, debit_tds, label):
    """A posted entry; debit_tds > 0 debits the TDS payable (a credit note's
    reversal), < 0 credits it (a bill's liability)."""
    amount = abs(debit_tds)
    tds_side = (amount, 0.0) if debit_tds > 0 else (0.0, amount)
    move = t["env"]["account.move"].create(
        {
            "journal_id": t["journal"].id,
            "date": "2026-11-11",
            "ref": label,
            "move_type": "entry",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": t["tds"].id,
                        "name": label,
                        "debit": tds_side[0],
                        "credit": tds_side[1],
                    },
                ),
                (
                    0,
                    0,
                    {
                        "account_id": t["other"].id,
                        "name": label,
                        "debit": tds_side[1],
                        "credit": tds_side[0],
                    },
                ),
            ],
        }
    )
    move.action_post()
    return move


def _deduction(t, base=29600.0, amount=6660.0):
    rate = t["env"].ref("cd_tax_engine_bd.tax_rate_tds_service_general")
    bill_move = _posted(t, -amount, "BILL E3")
    return t["env"]["fix.withholding.line"]._fix_record_deductions(
        [
            {
                "operating_unit_id": t["ou"].id,
                "tax_kind": "tds",
                "partner_id": t["supplier"].id,
                "rate_id": rate.id,
                "document_date": "2026-11-10",
                "base_amount": base,
                "rate": rate.rate,
                "multiplier": round(amount * 100.0 / base / rate.rate, 3),
                "paid_by_bank": True,
                "amount": amount,
                "source_ref": "BILL E3",
            }
        ],
        bill_move,
    )


def test_e3_13_withheld_deduction_falls_by_the_returned_share(tx):
    line = _deduction(tx)
    assert line._fix_reducible_for_credit_note()
    note_move = _posted(tx, 1665.0, "Mushak 6.7 E3")
    line._fix_reduce_for_credit_note(7400.0, 1665.0, note_move, "Mushak 6.7 E3")
    assert (line.base_amount, line.amount, line.state) == (22200.0, 4995.0, "withheld")
    assert "Mushak 6.7 E3" in " ".join(line.message_ids.mapped("body"))


def test_e3_13_reversal_needs_the_note_entry_to_debit_the_tds_payable(tx):
    line = _deduction(tx)
    wrong = _posted(tx, -100.0, "not a reversal")
    with pytest.raises(UserError, match="debit"), tx["env"].cr.savepoint():
        line._fix_reduce_for_credit_note(7400.0, 1665.0, wrong, "bad")
    assert line.amount == 6660.0


def test_e3_13_deposited_deduction_is_never_reduced(tx):
    line = _deduction(tx)
    line._guarded().write({"state": "deposited"})
    assert not line._fix_reducible_for_credit_note()
    note_move = _posted(tx, 1665.0, "Mushak 6.7 E3")
    with pytest.raises(UserError, match="deposited"), tx["env"].cr.savepoint():
        line._fix_reduce_for_credit_note(7400.0, 1665.0, note_move, "Mushak 6.7 E3")
    assert line.amount == 6660.0


def test_e3_13_a_reversal_never_exceeds_the_deduction(tx):
    line = _deduction(tx)
    note_move = _posted(tx, 7000.0, "too much")
    with pytest.raises(UserError, match="exceed"), tx["env"].cr.savepoint():
        line._fix_reduce_for_credit_note(29600.0, 7000.0, note_move, "too much")
