# cd_cash_position — A05 ERP audit, interface I3 (stream S4), live ORM:
#
#   FIN-10  the treasury confirmation posts with the payment's operating unit
#           and the source document's branch (it posted on the company's
#           FIRST unit with no branch: a Motijheel deposit refunded on Main);
#   FIN-12  a cash instruction (rental deposit refund, trade-in cash at the
#           counter) has a confirmation path — a cash voucher paid out by a
#           cashier / treasury user who is not the requester, the source's
#           approver or the releaser — and its entry posts Dr the instruction's
#           debit account / Cr the cash journal; the instruction pre-fills a
#           journal of the method's kind;
#   FIN-25  a card deposit is refunded to the card (acquirer account, original
#           card transaction named), not by bank transfer.
from __future__ import annotations

import itertools

import pytest
from odoo import fields
from odoo.addons.cd_cash_position.tests.test_treasury_a08 import Kit, _balance, _events
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]

_N = itertools.count(1)


class I3Kit(Kit):
    """Kit plus a second operating unit with its own branch, a cash journal
    (the only active one of the company), an acquirer journal and a cashier."""

    def __init__(self, env):
        super().__init__(env)
        n = next(_N)
        company = self.company
        self.ou2 = env["operating.unit"].create(
            {
                "name": "A05 S4 OU2 %s" % n,
                "code": "A5S4%s" % n,
                "company_id": company.id,
                "partner_id": company.partner_id.id,
            }
        )
        self.branch2 = env["fix.branch"].create(
            {
                "code": "A5B%s" % n,
                "name": "A05 S4 Branch %s" % n,
                "entity_id": self.branch.entity_id.id,
                "operating_unit_id": self.ou2.id,
            }
        )
        for user in (self.maker, self.checker):
            user.write({"operating_unit_ids": [(4, self.ou2.id)]})
        # the one cash journal: other cash journals of the company are
        # archived inside the rolled-back test, so "the one of its kind" is
        # deterministic
        env["account.journal"].search(
            [("company_id", "=", company.id), ("type", "=", "cash")]
        ).write({"active": False})
        self.cash = env["account.journal"].create(
            {"name": "A05 Cash %s" % n, "type": "cash", "code": "AC%s" % (n % 1000)}
        )
        self.card_journal = env["account.journal"].create(
            {
                "name": "A05 Card Acquirer %s" % n,
                "type": "bank",
                "code": "AQ%s" % (n % 1000),
                "fix_treasury_role": "gateway",
            }
        )
        self.liability = env["account.account"].create(
            {
                "code": "A5L%04d" % n,
                "name": "A05 deposits held %s" % n,
                "account_type": "liability_current",
            }
        )
        self.cashier = self._cashier("a05cashier%s" % n)
        self.requester = self._cashier("a05requester%s" % n)

    def _cashier(self, login):
        env = self.env
        return env["res.users"].create(
            {
                "name": login,
                "login": "%s@m50.test" % login,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            env.ref("cd_front_desk.group_fd_cashier").id,
                            env.ref("base.group_user").id,
                        ],
                    )
                ],
                "operating_unit_ids": [(6, 0, [self.ou.id, self.ou2.id])],
                "default_operating_unit_id": self.ou2.id,
                "company_id": self.company.id,
                "company_ids": [(6, 0, [self.company.id])],
            }
        )

    def shift(self, branch=None, unit=None):
        """A source document that carries a branch and a unit."""
        return self.env["fix.cash.shift"].create(
            {
                "operating_unit_id": (unit or self.ou2).id,
                "branch_id": (branch or self.branch2).id,
                "operator_id": self.employee.id,
                "shift_date": fields.Date.context_today(self.env.user),
                "opening_float": 0.0,
                "cash_payments": 0.0,
                "closing_counted": 0.0,
                "state": "closed",
            }
        )

    def request(self, source, amount=4500.0, user=None, **options):
        Exec = self.env["fix.payment.execution"]
        if user:
            Exec = Exec.with_user(user)
        options.setdefault("debit_account_id", self.liability.id)
        return Exec._fix_request_payment(
            source._name,
            source.id,
            self.vendor,
            options.pop("bank", False),
            amount,
            "BDT",
            "A05 S4 %s" % source.id,
            False,
            **options,
        )


@pytest.fixture
def k(odoo_env):
    return I3Kit(odoo_env)


def _dims(env, move):
    return env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])


# ------------------------------------------------------------------ FIN-10
def test_fin10_confirmation_posts_on_the_payment_unit_and_source_branch(k):
    env = k.env
    first_ou = env["operating.unit"].search([("company_id", "=", k.company.id)], limit=1)
    assert first_ou != k.ou2, "the test needs a unit other than the company's first"
    pay = k.request(k.shift(), bank=k.payee_bank(), journal_id=k.bank.id, rail="beftn")
    assert (pay.operating_unit_id, pay.branch_id) == (k.ou2, k.branch2)
    k.release(pay)
    pay.bank_reference = "BEFTN-A05-1"
    k.line(-4500.0, reference="BEFTN-A05-1")
    pay.action_confirm_bank()
    assert pay.state == "executed" and pay.move_id
    dims = _dims(env, pay.move_id)
    assert len(dims) == 2
    assert set(dims.mapped("operating_unit_id")) == {k.ou2}
    assert set(dims.mapped("branch_id")) == {k.branch2}
    assert _balance(env, k.liability) == 4500.0


def test_fin10_unit_alone_is_carried_when_the_source_has_no_branch(k):
    """A manual instruction in unit 2 with no branch posts on unit 2, not on
    the company's first unit."""
    env = k.env
    pay = k.payment(700.0, operating_unit_id=k.ou2.id)
    assert not pay.branch_id
    k.release(pay)
    pay.bank_reference = "BEFTN-A05-2"
    k.line(-700.0, reference="BEFTN-A05-2")
    pay.action_confirm_bank()
    assert set(_dims(env, pay.move_id).mapped("operating_unit_id")) == {k.ou2}


def test_fin10_named_branch_of_another_unit_is_refused(k):
    with pytest.raises(UserError, match="belongs to"), k.env.cr.savepoint():
        k.request(k.shift(), operating_unit_id=k.ou.id, branch_id=k.branch2.id)
    # a manual instruction cannot pair them either
    with pytest.raises(ValidationError, match="belongs to"), k.env.cr.savepoint():
        k.payment(10.0, operating_unit_id=k.ou.id, branch_id=k.branch2.id)


def test_fin10_branch_is_pinned_on_a_source_request(k):
    pay = k.request(k.shift(), bank=k.payee_bank(), journal_id=k.bank.id, rail="beftn")
    with pytest.raises(UserError, match="cannot change in treasury"), k.env.cr.savepoint():
        pay.with_user(k.maker).write({"branch_id": k.branch.id, "operating_unit_id": k.ou.id})


# ------------------------------------------------------------------ FIN-12
def test_fin12_cash_request_prefills_the_cash_journal(k):
    # the caller passed the first BANK journal (the rental refund did): replaced
    pay = k.request(k.shift(), method="cash", journal_id=k.bank.id)
    assert pay.journal_id == k.cash
    # a bank transfer keeps its bank journal; a card goes to the acquirer
    assert k.request(k.shift(), method="bank_transfer", journal_id=k.bank.id).journal_id == k.bank
    card = k.request(k.shift(), method="card", original_payment_ref="RRN-1", journal_id=k.bank.id)
    assert card.journal_id == k.card_journal


def test_fin12_cheque_in_hand_is_never_the_cash_journal(k):
    """fix_real's only 'cash' journal is CIH (cheques in hand): it is not
    pre-filled, and a cash voucher is never paid from it."""
    env = k.env
    cih_account = k.accounts["cheque_returned"]
    env["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.account_code.cheque_in_hand", cih_account.code
    )
    cih = env["account.journal"].create(
        {
            "name": "Cheque In Hand A05",
            "type": "cash",
            "code": "CIHA5",
            "default_account_id": cih_account.id,
        }
    )
    k.cash.write({"active": False})
    pay = k.request(k.shift(), amount=50.0, method="cash")
    assert not pay.journal_id, "no cash journal of the right kind: none is guessed"
    pay.write({"journal_id": cih.id})
    k.release(pay)
    with pytest.raises(UserError, match="cheques in hand"), env.cr.savepoint():
        pay.with_user(k.cashier).action_pay_cash_voucher()


def test_fin12_cash_voucher_posts_dr_liability_cr_cash_once(k):
    env = k.env
    pay = k.request(k.shift(), amount=3000.0, method="cash", user=k.requester)
    assert pay.create_uid == k.requester
    k.release(pay)
    assert pay.state == "sent"
    # the requester and the releaser never pay it out; a plain user cannot
    for user in (k.requester, k.checker):
        with pytest.raises(UserError, match="Segregation of duties"), env.cr.savepoint():
            pay.with_user(user).action_pay_cash_voucher()
    plain = env["res.users"].create(
        {
            "name": "a05plain",
            "login": "a05plain@m50.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    with pytest.raises(UserError, match="cashier"), env.cr.savepoint():
        pay.with_user(plain).action_pay_cash_voucher()
    pay.with_user(k.cashier).action_pay_cash_voucher(received_by="Customer, NID 1234")
    assert (pay.state, pay.confirmation_source, pay.bank_confirmed) == (
        "executed",
        "cash_voucher",
        True,
    )
    assert pay.cash_paid_by_id == k.cashier and pay.cash_voucher_no
    assert pay.cash_received_by == "Customer, NID 1234"
    assert _balance(env, k.liability) == 3000.0
    assert _balance(env, k.cash.default_account_id) == -3000.0
    dims = _dims(env, pay.move_id)
    assert set(dims.mapped("operating_unit_id")) == {k.ou2}
    assert set(dims.mapped("branch_id")) == {k.branch2}
    assert len(_events(env, "payment.executed", pay.id)) == 1
    # a double click pays nothing twice
    with pytest.raises(UserError, match="prepared and released"), env.cr.savepoint():
        pay.with_user(k.cashier).action_pay_cash_voucher()
    assert _balance(env, k.liability) == 3000.0


def test_fin12_cash_voucher_only_after_release_and_only_for_cash(k):
    env = k.env
    pay = k.request(k.shift(), amount=100.0, method="cash")
    with pytest.raises(UserError, match="prepared and released"), env.cr.savepoint():
        pay.with_user(k.cashier).action_pay_cash_voucher()
    bank = k.payment(100.0)
    k.release(bank)
    with pytest.raises(UserError, match="only a cash instruction"), env.cr.savepoint():
        bank.with_user(k.cashier).action_pay_cash_voucher()


# ------------------------------------------------------------------ FIN-25
def test_fin25_card_refund_names_the_card_payment_and_pays_through_the_acquirer(k):
    env = k.env
    with pytest.raises(UserError, match="original_payment_ref"), env.cr.savepoint():
        k.request(k.shift(), method="card")
    pay = k.request(k.shift(), amount=900.0, method="card", original_payment_ref="RRN-77")
    assert pay.journal_id == k.card_journal and pay.method == "card"
    # an ordinary bank account is not the card channel
    pay.write({"journal_id": k.bank.id})
    with pytest.raises(UserError, match="card acquirer"), env.cr.savepoint():
        pay.with_user(k.maker).action_prepare()
    pay.write({"journal_id": k.card_journal.id})
    k.release(pay)
    csv_text = pay.instruction_attachment_id.raw.decode()
    assert "RRN-77" in csv_text and pay.state == "sent"
