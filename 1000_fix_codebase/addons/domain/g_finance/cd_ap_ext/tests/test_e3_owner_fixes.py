# cd_ap_ext — owner-approved fixes of 12 Nov 2026 (third end-to-end rehearsal).
#
#   C9 / D-05  a bill whose TDS category was ASSUMED (the vendor's tax profile
#              names none: service_general 10% x 2.25 = 22.5% for a supplier with
#              no TIN) was submitted, approved and posted with the flag still up.
#              Submission and approval are now refused until an accountant sets
#              the right category or confirms the default, and the confirmation
#              is written to the bill's approval log.
#   F11 / E3-17 an advance's cash recovery was posted Dr the payment bank
#              journal's account with no bank evidence. Cash returned to the
#              office debits Cash in Hand; a bank transfer keeps the bank.
#   F8 / E3-13 a vendor credit note for returned goods reverses the TDS withheld
#              on the returned part of the bill (while the deduction is not yet
#              deposited), and carries the VAT the returned part bore.
from __future__ import annotations

import itertools
from datetime import date

import pytest
from odoo.exceptions import AccessError, UserError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, AccessError)
_SEQ = itertools.count(1)


def _user(env, ou, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "E3 AP User %d" % n,
                "login": "e3-ap-%d@test.local" % n,
                "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
                "company_id": env.company.id,
                "company_ids": [(6, 0, [env.company.id])],
                "operating_unit_ids": [(6, 0, [ou.id])],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def e3(odoo_env):
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

    accounts = {
        "ap": acc("990201", "E3 trade payables", "liability_payable"),
        "grni": acc("990503", "E3 GRNI", "liability_current"),
        "vat_input": acc("990131", "Test input VAT", "asset_current"),
        "vds_payable": acc("990252", "Test VDS payable", "liability_current"),
        "tds_payable": acc("990253", "Test TDS payable", "liability_current"),
        "employee_advance": acc("990141", "Test employee advances", "asset_current"),
        "expense": acc("990600", "Test expense", "expense"),
        "cash": acc("990108", "E3 Cash in hand", "asset_cash"),
    }
    icp = env["ir.config_parameter"].sudo()
    for param, code in (
        ("cd_ap_ext.account_code.ap", "990201"),
        ("cd_ap_ext.account_code.grni", "990503"),
        ("cd_tax_engine_bd.vat_input_account_code", "990131"),
        ("cd_tax_engine_bd.account_code.vds_payable", "990252"),
        ("cd_tax_engine_bd.account_code.tds_payable", "990253"),
        ("cd_ap_ext.account_code.employee_advance", "990141"),
        ("cd_ap_ext.account_code.expense", "990600"),
    ):
        icp.set_param(param, code)
    bank = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "bank")], limit=1
    )
    icp.set_param("cd_ap_ext.payment_journal_code", bank.code)
    purchase = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "purchase")], limit=1
    )
    icp.set_param("cd_ap_ext.bill_journal_code", purchase.code)
    # a supplier with NO tax profile: the D-05 case
    vendor = env["res.partner"].create({"name": "E3 Lucid Computer", "is_company": True})
    return {
        "env": env,
        "company": company,
        "ou": ou,
        "accounts": accounts,
        "bank": bank,
        "vendor": vendor,
        "product": env["product.product"].create({"name": "E3 SSD 512GB"}),
        "acc1": _user(env, ou, "account.group_account_user"),
        "acc2": _user(env, ou, "account.group_account_user"),
        "mgr": _user(env, ou, "account.group_account_manager"),
        "clerk": _user(env, ou),
    }


def _bill(e, qty=20.0, price=1480.0, vat=0.0, **line):
    vals = {
        "product_id": e["product"].id,
        "description": "SSD",
        "quantity": qty,
        "unit_price": price,
    }
    vals.update(line)
    return (
        e["env"]["fix.vendor.invoice"]
        .with_user(e["acc1"])
        .create(
            {
                "vendor_id": e["vendor"].id,
                "invoice_ref": "E3-%d" % next(_SEQ),
                "invoice_date": date(2026, 11, 10),
                "bill_type": "non_po",
                "operating_unit_id": e["ou"].id,
                "vat_amount": vat,
                "line_ids": [(0, 0, vals)],
            }
        )
    )


# ------------------------------------------------------------ C9 / D-05 --
def test_c9_a_bill_with_an_assumed_tds_category_is_not_submitted(e3):
    bill = _bill(e3)
    assert bill.tds_category_review
    with pytest.raises(UserError, match="TDS category"), e3["env"].cr.savepoint():
        bill.with_user(e3["acc1"]).action_submit_approval()
    assert bill.approval_state == "draft"


def test_c9_the_reviewer_confirms_and_the_confirmation_is_logged(e3):
    bill = _bill(e3)
    with pytest.raises(REFUSED), e3["env"].cr.savepoint():
        bill.with_user(e3["clerk"]).action_confirm_tds_category()
    bill.with_user(e3["acc2"]).action_confirm_tds_category()
    assert not bill.tds_category_review
    log = bill.approval_log_ids.filtered(lambda r: r.action == "tds_confirm")
    assert log.user_id == e3["acc2"] and "service_general" in (log.note or "")
    bill.with_user(e3["acc1"]).action_submit_approval()
    assert bill.approval_state == "to_approve"


def test_c9_choosing_the_category_also_clears_the_gate(e3):
    bill = _bill(e3)
    bill.line_ids.with_user(e3["acc1"]).write({"tds_category": "supply_of_goods"})
    bill.with_user(e3["acc1"]).action_submit_approval()
    assert bill.approval_state == "to_approve"


def test_c9_a_flagged_bill_already_awaiting_approval_is_not_approved(e3):
    """A bill submitted before the gate existed is stopped at approval."""
    bill = _bill(e3)
    bill.sudo()._guarded().write(
        {"approval_state": "to_approve", "submitted_by": e3["acc1"].id, "approval_level": 0}
    )
    with pytest.raises(UserError, match="TDS category"), e3["env"].cr.savepoint():
        bill.with_user(e3["mgr"]).action_approve()
    assert bill.approval_state == "to_approve" and not bill.move_id


# ------------------------------------------------------------ F11 / E3-17 --
def _disbursed_advance(e, method, amount=800.0):
    env = e["env"]
    employee = env["hr.employee"].create({"name": "E3 Advance Employee %d" % next(_SEQ)})
    adv = env["fix.employee.advance"].create(
        {
            "operating_unit_id": e["ou"].id,
            "employee_id": employee.id,
            "purpose": "E3 parts float",
            "amount": amount,
        }
    )
    # trusted set-up: treasury disbursed it (cd_cash_position's tests cover that)
    adv._guarded().write({"state": "disbursed", "approved_amount": amount})
    adv.recovery_method = method
    return adv


def _recovery_debit(adv):
    move = adv.recovery_move_id
    assert move and move.state == "posted"
    return move.line_ids.filtered(lambda ml: ml.debit)


def test_f11_cash_recovery_debits_cash_in_hand(e3):
    e3["env"]["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.account_code.branch_cash", "990108"
    )
    adv = _disbursed_advance(e3, "cash")
    adv.with_user(e3["acc1"]).action_record_recovery()
    debit = _recovery_debit(adv)
    assert debit.account_id == e3["accounts"]["cash"] and debit.debit == 800.0
    assert debit.account_id != e3["bank"].default_account_id
    assert adv.state == "settled" and adv.balance == 0.0


def test_f11_cash_recovery_falls_back_to_the_billing_cash_role(e3):
    icp = e3["env"]["ir.config_parameter"].sudo()
    icp.set_param("cd_cash_position.account_code.branch_cash", "")
    icp.set_param("cd_billing_engine.account_code.cash", "990108")
    adv = _disbursed_advance(e3, "cash")
    adv.with_user(e3["acc1"]).action_record_recovery()
    assert _recovery_debit(adv).account_id == e3["accounts"]["cash"]


def test_f11_cash_recovery_without_a_cash_account_is_refused(e3):
    icp = e3["env"]["ir.config_parameter"].sudo()
    icp.set_param("cd_cash_position.account_code.branch_cash", "")
    icp.set_param("cd_billing_engine.account_code.cash", "")
    adv = _disbursed_advance(e3, "cash")
    with pytest.raises(UserError, match="branch_cash"), e3["env"].cr.savepoint():
        adv.with_user(e3["acc1"]).action_record_recovery()
    assert adv.state == "disbursed" and adv.balance == 800.0


def test_f11_bank_recovery_keeps_the_bank_account(e3):
    e3["env"]["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.account_code.branch_cash", "990108"
    )
    adv = _disbursed_advance(e3, "bank")
    adv.with_user(e3["acc1"]).action_record_recovery()
    assert _recovery_debit(adv).account_id == e3["bank"].default_account_id


# ------------------------------------------------- F8 / E3-09, E3-13 (AP side) --
def _posted_bill(e, qty=20.0, price=1480.0, vat=4440.0):
    bill = _bill(e, qty=qty, price=price, vat=vat)
    bill.with_user(e["acc2"]).action_confirm_tds_category()
    bill.sudo()._guarded().write({"approval_state": "approved"})
    bill.sudo()._post_approved_bill()
    assert bill.move_id.state == "posted"
    return bill


def test_f8_return_note_values_the_billed_price_vat_and_tds(e3):
    bill = _posted_bill(e3)
    assert bill.tds_amount > 0  # the D-05 default: 22.5% when the rate master says so
    note = bill.sudo()._fix_raise_return_note(e3["product"], 5.0, "MUSHAK-67-E3", "RTV/E3/1")
    assert note.amount == 7400.0  # 5 x the billed 1,480.00, not the average cost
    assert note.vat_amount == 1110.0  # 4,440 x 7,400 / 29,600
    assert note.tds_amount == round(bill.tds_amount * 5 / 20, 2)
    assert (note.product_id, note.return_qty, note.state) == (e3["product"], 5.0, "draft")
    assert note.signed_total == -(7400.0 + 1110.0 - note.tds_amount)


def test_f8_returning_more_than_billed_is_refused(e3):
    bill = _posted_bill(e3)
    bill.sudo()._fix_raise_return_note(e3["product"], 15.0, "MUSHAK-67-E3a", "RTV/E3/2")
    with pytest.raises(UserError, match="billed"), e3["env"].cr.savepoint():
        bill.sudo()._fix_raise_return_note(e3["product"], 6.0, "MUSHAK-67-E3b", "RTV/E3/3")


def test_f8_approved_return_note_reverses_vat_and_the_withheld_tds(e3):
    bill = _posted_bill(e3)
    deduction = bill.withholding_line_ids.filtered(lambda w: w.tax_kind == "tds")
    base0, tds0 = deduction.base_amount, deduction.amount
    note = bill.sudo()._fix_raise_return_note(e3["product"], 5.0, "MUSHAK-67-E3c", "RTV/E3/4")
    note.with_user(e3["acc2"]).action_approve()
    lines = note.move_id.line_ids
    acc = e3["accounts"]

    def amt(account, side):
        return round(sum(lines.filtered(lambda ml: ml.account_id == account).mapped(side)), 2)

    assert amt(acc["ap"], "debit") == round(7400.0 + 1110.0 - note.tds_amount, 2)
    assert amt(acc["tds_payable"], "debit") == note.tds_amount
    assert amt(acc["vat_input"], "credit") == 1110.0
    # the deduction the 9.1 / TDS return reads falls by the returned share
    assert round(deduction.base_amount, 2) == round(base0 - 7400.0, 2)
    assert round(deduction.amount, 2) == round(tds0 - note.tds_amount, 2)
    # the TDS payable in the GL equals what the return will report
    gl = sum(
        e3["env"]["account.move.line"]
        .search(
            [
                ("account_id", "=", acc["tds_payable"].id),
                ("move_id", "in", (bill.move_id | note.move_id).ids),
            ]
        )
        .mapped("balance")
    )
    assert round(-gl, 2) == round(deduction.amount, 2)


def test_f8_a_deposited_deduction_is_not_reversed(e3):
    bill = _posted_bill(e3)
    deduction = bill.withholding_line_ids.filtered(lambda w: w.tax_kind == "tds")
    deduction.sudo()._guarded().write({"state": "deposited"})
    amount0 = deduction.amount
    note = bill.sudo()._fix_raise_return_note(e3["product"], 5.0, "MUSHAK-67-E3d", "RTV/E3/5")
    note.with_user(e3["acc2"]).action_approve()
    assert note.tds_amount == 0.0 and deduction.amount == amount0
    assert not note.move_id.line_ids.filtered(
        lambda ml: ml.account_id == e3["accounts"]["tds_payable"]
    )
    assert "deposited" in " ".join(note.message_ids.mapped("body"))
