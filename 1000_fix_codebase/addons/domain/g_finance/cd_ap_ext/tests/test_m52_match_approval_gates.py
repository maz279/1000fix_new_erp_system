# cd_ap_ext — the three-way match and the approval matrix as gates (CD-M52-01).
#
# Each test runs the reported attack through the ORM as a NON-ADMIN user with
# the real finance role (the `c` fixture of test_a08_m52_controls), and a proper
# path beside it shows the legitimate route still works.
from __future__ import annotations

import pytest
from odoo.addons.cd_ap_ext.models.ap_gl import ap_journal
from odoo.addons.cd_ap_ext.tests.test_a08_m52_controls import (
    D,
    approve,
    bill,
    c,  # noqa: F401 - the fixture
    claim,
    disbursed_advance,
    issued_po,
    refused,
)
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]


def _po_bill(c, po, lines, ref, by=None):  # noqa: F811
    """lines: [(quantity, unit_price)] of the fixture product, against po."""
    return (
        c.env["fix.vendor.invoice"]
        .with_user(by or c.acc1)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.vendor.id,
                "invoice_ref": ref,
                "invoice_date": D,
                "payment_term_days": 0,
                "bill_type": "po",
                "requisition_id": po.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.product.id,
                            "description": "A08B2 Logic board",
                            "quantity": qty,
                            "unit_price": price,
                        },
                    )
                    for qty, price in lines
                ],
            }
        )
    )


def _note(c, b, amount, by=None, note_type="increase", **vals):  # noqa: F811
    return (
        c.env["fix.vendor.note"]
        .with_user(by or c.acc1)
        .create(
            {
                "invoice_id": b.id,
                "note_type": note_type,
                "mushak_ref": "68-G1-%s" % int(amount),
                "note_date": "2026-10-20",
                "reason": "price",
                "amount": amount,
                **vals,
            }
        )
    )


# ============================================================ 1. line signs
def test_negative_quantity_line_cannot_net_an_overbilled_bill_to_matched(c):  # noqa: F811
    """10 ordered and received at 1,000. A bill for 20, with a second line of
    -10 at price 0, summed to 10 invoiced and read 'matched' at 20,000."""
    po = issued_po(c, 10.0, 1000.0, received=10.0)
    made = []
    err = refused(
        c.env, lambda: made.append(_po_bill(c, po, [(20.0, 1000.0), (-10.0, 0.0)], "G1-NEG-1"))
    )
    assert isinstance(err, ValidationError), "saved as %s at %s" % (
        made and made[0].match_state,
        made and made[0].subtotal,
    )
    # proper path: the true quantity matches
    assert _po_bill(c, po, [(10.0, 1000.0)], "G1-NEG-2").match_state == "matched"


def test_line_sign_is_checked_on_the_line_itself(c):  # noqa: F811
    """The check fires where the line is written: a child created or edited
    directly (the portal and the workspace both do) never passes the parent."""
    po = issued_po(c, 10.0, 1000.0, received=10.0)
    b = _po_bill(c, po, [(10.0, 1000.0)], "G1-NEG-3")
    Line = c.env["fix.vendor.invoice.line"].with_user(c.acc1)
    base = {"invoice_id": b.id, "product_id": c.product.id, "description": "x"}
    for qty, price in ((-10.0, 0.0), (0.0, 1000.0), (1.0, -500.0)):
        err = refused(
            c.env, lambda q=qty, p=price: Line.create({**base, "quantity": q, "unit_price": p})
        )
        assert isinstance(err, ValidationError), (qty, price)
    line = b.line_ids.with_user(c.acc1)
    assert isinstance(refused(c.env, lambda: line.write({"quantity": -1.0})), ValidationError)
    assert isinstance(refused(c.env, lambda: line.write({"quantity": 0.0})), ValidationError)
    assert isinstance(refused(c.env, lambda: line.write({"unit_price": -1.0})), ValidationError)
    line.write({"quantity": 9.0, "unit_price": 0.0})  # a free-of-charge line is a price, not a sign
    assert (b.line_ids.quantity, b.match_state) == (9.0, "matched")


# ============================================================ 2. the PO's vendor
def test_bill_of_another_vendor_never_matches_the_po(c):  # noqa: F811
    """Vendor B's bill against vendor A's PO and receipt read 'matched' and
    would have been paid to B."""
    po = issued_po(c, 5.0, 2000.0, received=5.0)  # c.vendor's order
    other = c.env["res.partner"].create({"name": "A08B2 Meghna Traders (not the PO vendor)"})
    b = bill(c, 2000.0, qty=5.0, po=po, vendor=other)
    assert b.match_state == "blocked", b.match_detail
    assert "is not the supplier of the purchase order" in b.match_detail
    assert refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval())
    err = refused(c.env, lambda: b.with_user(c.acc1).action_request_payment())
    assert err and "G3-06" in str(err)


def test_bill_from_the_po_vendors_own_contact_matches(c):  # noqa: F811
    """Commercial partners are compared: the supplier's billing contact is the
    supplier."""
    po = issued_po(c, 5.0, 2000.0, received=5.0)
    desk = c.env["res.partner"].create({"name": "A08B2 Padma AR desk", "parent_id": c.vendor.id})
    assert desk.commercial_partner_id == c.vendor
    b = bill(c, 2000.0, qty=5.0, po=po, vendor=desk)
    assert (b.match_state, b.match_detail) == ("matched", "PO / receipt / invoice reconciled")


def test_match_follows_a_vendor_change_on_the_draft(c):  # noqa: F811
    po = issued_po(c, 5.0, 2000.0, received=5.0)
    other = c.env["res.partner"].create({"name": "A08B2 Meghna Traders (not the PO vendor)"})
    b = bill(c, 2000.0, qty=5.0, po=po)
    assert b.match_state == "matched"
    b.with_user(c.acc1).write({"vendor_id": other.id})
    assert b.match_state == "blocked"


# ============================================================ 3. match before approval
def test_blocked_po_bill_cannot_be_submitted(c):  # noqa: F811
    po = issued_po(c, 1.0, 1000.0, received=1.0)
    b = bill(c, 1500.0, po=po)  # 1,500 billed against a PO price of 1,000
    assert b.match_state == "blocked"
    err = refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval())
    assert err and "G3-06" in str(err) and "price above PO" in str(err)
    assert b.approval_state == "draft"


def test_po_bill_without_a_purchase_order_cannot_be_submitted(c):  # noqa: F811
    b = bill(c, 80000.0, bill_type="po")
    assert b.match_state == "unmatched"
    err = refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval())
    assert err and "G3-06" in str(err)
    assert b.approval_state == "draft"


def test_bill_blocked_after_submission_is_not_approved_or_posted(c):  # noqa: F811
    """One receipt, two bills. The first is rejected, so the second matches
    and is submitted; the first then returns to draft and claims the receipt
    again. The second, now blocked, was still approved and posted."""
    po = issued_po(c, 5.0, 2000.0, received=5.0)
    first = bill(c, 2000.0, qty=5.0, po=po)
    second = bill(c, 2000.0, qty=5.0, po=po)
    assert (first.match_state, second.match_state) == ("matched", "blocked")
    first.with_user(c.acc1).action_submit_approval()
    first.with_user(c.acc2).action_reject()
    assert second.match_state == "matched"
    second.with_user(c.acc1).action_submit_approval()
    first.with_user(c.acc1).action_reset_draft()
    assert second.match_state == "blocked" and second.approval_state == "to_approve"
    err = refused(c.env, lambda: second.with_user(c.acc2).action_approve())
    assert err and "G3-06" in str(err), "approved: %s, GL %s" % (
        second.approval_state,
        second.move_id.name,
    )
    assert second.approval_state == "to_approve" and not second.move_id
    # the posting itself refuses too (it is also reached by other modules)
    assert "G3-06" in str(refused(c.env, lambda: second._post_approved_bill()))
    assert not second.move_id
    # proper path: the bill that holds the receipt goes through
    first.with_user(c.acc1).action_submit_approval()
    first.with_user(c.acc2).action_approve()
    assert first.approval_state == "approved" and first.move_id.state == "posted"


# ============================================================ 4. debit notes
def test_increase_note_needs_the_matrix_level_of_its_amount(c):  # noqa: F811
    """A 600,000 bill needs the level-2 manager; a 600,000 debit note on a
    20,000 bill was approved by one accountant."""
    b = approve(c, bill(c, 20000.0))
    note = _note(c, b, 600000.0)
    err = refused(c.env, lambda: note.with_user(c.acc2).action_approve())
    assert err and "approval matrix" in str(err), "approved: %s, GL %s" % (
        note.state,
        note.move_id.name,
    )
    assert note.state == "draft" and not note.move_id
    assert refused(c.env, lambda: note.with_user(c.acc1).action_approve())  # still not the maker
    note.with_user(c.mgr).action_approve()
    assert note.state == "approved" and note.move_id.state == "posted"


def test_increase_notes_on_one_bill_are_summed_for_the_matrix(c):  # noqa: F811
    """Two 300,000 notes are 600,000 added to one bill."""
    b = approve(c, bill(c, 20000.0))
    one = _note(c, b, 300000.0, mushak_ref="68-G1-A")
    two = _note(c, b, 300000.0, mushak_ref="68-G1-B")
    one.with_user(c.acc2).action_approve()  # 300,000: level 1
    assert one.state == "approved"
    assert refused(c.env, lambda: two.with_user(c.acc2).action_approve())
    two.with_user(c.mgr).action_approve()
    assert two.state == "approved"


def test_small_increase_note_and_credit_note_keep_their_route(c):  # noqa: F811
    b = approve(c, bill(c, 20000.0))
    up = _note(c, b, 15000.0)
    up.with_user(c.acc2).action_approve()
    down = _note(c, b, 20000.0, note_type="decrease", mushak_ref="67-G1")
    down.with_user(c.acc2).action_approve()
    assert (up.state, down.state) == ("approved", "approved")


def test_increase_note_cannot_lift_a_po_bill_above_the_po(c):  # noqa: F811
    """A price increase the PO does not cover is what the match blocks on a
    bill; a debit note carried it past the match."""
    po = issued_po(c, 10.0, 1000.0, received=10.0)
    b = approve(c, bill(c, 900.0, qty=10.0, po=po))  # 9,000 billed, PO value 10,000
    assert b.match_state == "matched"
    over = _note(c, b, 5000.0)
    err = refused(c.env, lambda: over.with_user(c.acc2).action_approve())
    assert err and "purchase order" in str(err), "approved: %s" % over.state
    assert over.state == "draft" and not over.move_id
    within = _note(c, b, 1000.0, mushak_ref="68-G1-OK")  # up to the PO price
    within.with_user(c.acc2).action_approve()
    assert within.state == "approved"
    more = _note(c, b, 1.0, mushak_ref="68-G1-MORE")
    assert refused(c.env, lambda: more.with_user(c.acc2).action_approve())


# ============================================================ 5. claim lines
def test_claim_line_cannot_be_moved_into_an_approved_claim(c):  # noqa: F811
    """Only the claim a line LEFT was checked: a 3,000 line of a draft claim
    moved into an approved 1,000 claim settled 4,000 of the advance."""
    adv = disbursed_advance(c)
    approved = claim(
        c,
        c.plain,
        c.emp_plain,
        [{"category_id": c.other.id, "unit_amount": 1000.0, "date": D}],
        advance_id=adv.id,
    )
    approved.with_user(c.plain).action_submit()
    approved.with_user(c.acc1).action_approve()
    draft = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.other.id, "unit_amount": 3000.0, "date": D}]
    )
    line = draft.line_ids.with_user(c.plain)
    err = refused(c.env, lambda: line.write({"claim_id": approved.id}))
    adv.invalidate_recordset()
    assert err, "moved: claim now %s, advance balance %s" % (approved.amount, adv.balance)
    assert (approved.amount, len(approved.line_ids), adv.balance) == (1000.0, 1, 4000.0)
    # proper path: a line moves between the claimant's own drafts
    other = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.other.id, "unit_amount": 200.0, "date": D}]
    )
    line.write({"claim_id": other.id})
    assert (other.amount, draft.amount) == (3200.0, 0.0)


# ============================================================ 6. purchase journal
def _second_purchase_journal(c):  # noqa: F811
    Journal = c.env["account.journal"]
    first = Journal.search([("company_id", "=", c.company.id), ("type", "=", "purchase")])
    assert len(first) == 1, "the test database has one purchase journal"
    second = Journal.create(
        {"name": "G1 Import bills", "code": "G1IB", "type": "purchase", "company_id": c.company.id}
    )
    return first, second


def _journal_params(c, bill_code=False, legacy_code=False):  # noqa: F811
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_ap_ext.bill_journal_code", bill_code)
    icp.set_param("cd_ap_ext.purchase_journal_code", legacy_code)


def test_purchase_journal_honours_the_legacy_parameter(c):  # noqa: F811
    """The databases carry cd_ap_ext.purchase_journal_code; the reader looked
    only at cd_ap_ext.bill_journal_code and posted to whichever purchase
    journal sorted first."""
    first, second = _second_purchase_journal(c)
    _journal_params(c, legacy_code=second.code)
    assert ap_journal(c.env, c.company, "purchase") == second
    b = approve(c, bill(c, 10000.0))
    assert b.move_id.journal_id == second
    _journal_params(c, bill_code=first.code, legacy_code=second.code)
    assert ap_journal(c.env, c.company, "purchase") == first  # the canonical key wins


def test_purchase_journal_is_never_guessed_between_two(c):  # noqa: F811
    _second_purchase_journal(c)
    _journal_params(c)
    with pytest.raises(UserError, match="cd_ap_ext.bill_journal_code"):
        ap_journal(c.env, c.company, "purchase")
    b = bill(c, 10000.0)
    b.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: b.with_user(c.acc2).action_approve())
    assert b.approval_state == "to_approve" and not b.move_id


def test_purchase_journal_needs_no_parameter_when_there_is_one(c):  # noqa: F811
    journal = c.env["account.journal"].search(
        [("company_id", "=", c.company.id), ("type", "=", "purchase")]
    )
    assert len(journal) == 1
    _journal_params(c)
    assert ap_journal(c.env, c.company, "purchase") == journal
    _journal_params(c, legacy_code="NOPE")  # a code that names no journal is not ignored
    with pytest.raises(UserError, match="NOPE"):
        ap_journal(c.env, c.company, "purchase")
