# cd_cash_position — live-ORM behaviour of the A08 · M50 treasury build:
# bank-confirmed payment execution, strict auto-match, bank master BD
# fields, cash-in-transit, rider COD, imprest, cheques, gateway settlement,
# facilities/covenants and the computed reports. Runs on fix_test inside a
# rolled-back transaction (odoo_env).
from __future__ import annotations

import base64
import itertools
import json
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]

_SEQ = itertools.count(1)
ROLES = (
    "branch_cash",
    "cash_in_transit",
    "cod_clearing",
    "rider_shortage",
    "gateway_fees",
    "channel_clearing",
    "outgoing_clearing",
    "interest_expense",
    "bank_charges",
    "cash_shortage",
)


def _events(env, event_type, aggregate_id):
    return [
        json.loads(e.payload)
        for e in env["fix.event.outbox"].search(
            [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
        )
    ]


def _balance(env, account):
    lines = env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("balance")), 2)


class Kit:
    """Accounts, a bank journal, an OU/branch and two finance users."""

    def __init__(self, env):
        self.env = env
        n = next(_SEQ)
        self.company = env.company
        self.ou = env["operating.unit"].search([("company_id", "=", self.company.id)], limit=1)
        self.accounts = {}
        for i, role in enumerate(ROLES):
            acc = env["account.account"].create(
                {
                    "code": "T9%02d%02d" % (n % 100, i),
                    "name": "Test %s" % role,
                    "account_type": "expense"
                    if role.endswith(("fees", "expense", "charges"))
                    else "asset_current",
                }
            )
            self.accounts[role] = acc
            env["ir.config_parameter"].sudo().set_param(
                "cd_cash_position.account_code.%s" % role, acc.code
            )
        self.bank = env["account.journal"].create(
            {"name": "Test Bank %s" % n, "type": "bank", "code": "TB%s" % (n % 1000)}
        )
        self.bank_acc = self.bank.default_account_id
        entity = env["fix.entity"].search([("company_id", "=", self.company.id)], limit=1) or env[
            "fix.entity"
        ].create(
            {
                "code": "E%s" % self.company.id,
                "legal_name": self.company.name,
                "company_id": self.company.id,
            }
        )
        self.branch = env["fix.branch"].create(
            {
                "code": "TBR%s" % (n % 1000),
                "name": "Test Branch %s" % n,
                "entity_id": entity.id,
                "operating_unit_id": self.ou.id,
            }
        )
        self.employee = env["hr.employee"].create({"name": "Rider %s" % n})
        self.maker = self._user("maker%s" % n)
        self.checker = self._user("checker%s" % n)
        self.vendor = env["res.partner"].create({"name": "Vendor %s" % n})

    def _user(self, login):
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
                            env.ref("account.group_account_manager").id,
                            env.ref("base.group_user").id,
                        ],
                    )
                ],
                "operating_unit_ids": [(6, 0, [self.ou.id])],
                "default_operating_unit_id": self.ou.id,
                "company_id": self.company.id,
                "company_ids": [(6, 0, [self.company.id])],
            }
        )

    def payee_bank(self, routing="123456789"):
        return self.env["res.partner.bank"].create(
            {
                "partner_id": self.vendor.id,
                "acc_number": "ACC%s" % next(_SEQ),
                "fix_routing_number": routing,
                "fix_account_type": "current",
            }
        )

    def payment(self, amount=4500.0, **vals):
        base = {
            "operating_unit_id": self.ou.id,
            "source_model": "fix.vendor.invoice",
            "source_id": 900000 + next(_SEQ),
            "payee": self.vendor.name,
            "partner_id": self.vendor.id,
            "amount": amount,
            "journal_id": self.bank.id,
            "rail": "beftn",
        }
        base.update(vals)
        if "partner_bank_id" not in base:
            base["partner_bank_id"] = self.payee_bank().id
        return self.env["fix.payment.execution"].create(base)

    def line(self, amount, reference="", narration="", day=None):
        return self.env["fix.bank.statement.line"].create(
            {
                "journal_id": self.bank.id,
                "date": day or fields.Date.today(),
                "amount": amount,
                "reference": reference,
                "narration": narration,
            }
        )

    def shift(self, opening, counted, day=None, state="closed"):
        return self.env["fix.cash.shift"].create(
            {
                "operating_unit_id": self.ou.id,
                "branch_id": self.branch.id,
                "operator_id": self.employee.id,
                "shift_date": day or fields.Date.today(),
                "opening_float": opening,
                "cash_payments": counted - opening,
                "closing_counted": counted,
                "state": state,
            }
        )


@pytest.fixture
def kit(odoo_env):
    return Kit(odoo_env)


# --------------------------------------------------------------------------- bank master


def test_routing_number_must_be_nine_digits(kit):
    with pytest.raises(ValidationError, match="9 digits"), kit.env.cr.savepoint():
        kit.payee_bank(routing="12345")
    acct = kit.env["res.partner.bank"].create(
        {
            "partner_id": kit.company.partner_id.id,
            "acc_number": "OWN%s" % next(_SEQ),
            "fix_routing_number": "123456789",
            "fix_account_type": "current",
        }
    )
    kit.bank.bank_account_id = acct.id
    assert kit.bank.fix_routing_number == "123456789"
    assert kit.bank.fix_account_type == "current"
    assert kit.bank.fix_gl_balance == 0.0


# --------------------------------------------------------------------------- payments


def test_release_validates_rail_data(kit):
    pay = kit.payment(journal_id=False)
    with pytest.raises(UserError, match="bank account"), kit.env.cr.savepoint():
        pay.action_release()
    pay = kit.payment(partner_bank_id=kit.payee_bank(routing=False).id)
    with pytest.raises(UserError, match="routing number"), kit.env.cr.savepoint():
        pay.action_release()
    pay = kit.payment(rail=False)
    with pytest.raises(UserError, match="rail"), kit.env.cr.savepoint():
        pay.action_release()


def test_release_then_bank_confirmation_posts_and_publishes(kit):
    env = kit.env
    pay = kit.payment(4500.0)
    pay.action_release()
    assert pay.state == "sent"
    assert pay.instruction_attachment_id.raw.decode().splitlines()[1].startswith(pay.name)
    assert _events(env, "payment.executed", pay.id) == []  # nothing until the bank confirms
    with pytest.raises(UserError, match="bank's reference"), env.cr.savepoint():
        pay.action_confirm_bank()
    pay.bank_reference = "BEFTN-77812"
    pay.action_confirm_bank()
    assert (pay.state, pay.confirmation_source, pay.bank_confirmed) == (
        "executed",
        "bank_reference",
        True,
    )
    assert _balance(env, kit.bank_acc) == -4500.0
    assert _balance(env, kit.accounts["outgoing_clearing"]) == 4500.0
    assert len(_events(env, "payment.executed", pay.id)) == 1


def test_confirmation_fails_closed_without_clearing_account(kit):
    kit.env["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.account_code.outgoing_clearing", ""
    )
    pay = kit.payment(100.0)
    pay.action_release()
    pay.bank_reference = "X1"
    with pytest.raises(UserError, match="outgoing_clearing"), kit.env.cr.savepoint():
        pay.action_confirm_bank()
    assert pay.state == "sent"


def test_bank_rejection_and_requeue(kit):
    pay = kit.payment(10.0)
    pay.action_release()
    with pytest.raises(UserError, match="rejection reason"), kit.env.cr.savepoint():
        pay.action_mark_failed()
    pay.failure_reason = "Account closed"
    pay.action_mark_failed()
    assert pay.state == "failed"
    assert _events(kit.env, "payment.failed", pay.id)[0]["reason"] == "Account closed"
    pay.action_retry()
    assert pay.state == "pending"


def test_legacy_execute_is_flagged_unconfirmed(kit):
    pay = kit.payment(20.0)
    pay.action_execute()
    assert (pay.state, pay.confirmation_source, pay.bank_confirmed) == (
        "executed",
        "caller_asserted",
        False,
    )
    assert not pay.move_id


# --------------------------------------------------------------------------- auto-match


def test_statement_confirms_sent_payment_on_token_and_amount(kit):
    pay = kit.payment(4500.0)
    pay.action_release()
    wrong_amount = kit.line(-4400.0, reference=pay.name)
    right = kit.line(-4500.0, narration="BEFTN %s Vendor" % pay.name)
    assert kit.env["fix.bank.statement.line"].auto_match() == 1
    assert wrong_amount.match_state == "unmatched"
    assert (right.match_state, right.matched_kind, right.matched_payment_id) == (
        "auto",
        "payment",
        pay,
    )
    assert (pay.state, pay.confirmation_source, pay.statement_line_id) == (
        "executed",
        "statement",
        right,
    )


def test_substring_reference_no_longer_matches(kit):
    legacy = kit.payment(1150.0, source_model="fix.ar.invoice", source_id=777005)
    legacy.action_execute()
    near = kit.line(-1150.0, reference="AR/7770055")
    assert kit.env["fix.bank.statement.line"].auto_match() == 0
    assert near.match_state == "unmatched"
    exact = kit.line(-1150.0, reference="AR/777005")
    assert kit.env["fix.bank.statement.line"].auto_match() == 1
    assert exact.matched_invoice_ref == "AR/777005"
    assert legacy.statement_line_id == exact
    assert legacy.bank_confirmed  # the statement line now evidences it


def test_ambiguous_payee_amount_stays_unmatched(kit):
    a = kit.payment(300.0, payee="Rahim Traders")
    b = kit.payment(300.0, payee="Rahim Traders")
    (a | b).action_release()
    line = kit.line(-300.0, narration="paid Rahim Traders")
    assert kit.env["fix.bank.statement.line"].auto_match() == 0
    assert line.match_state == "unmatched"


def test_manual_match_requires_same_amount(kit):
    pay = kit.payment(250.0)
    pay.action_release()
    line = kit.line(-249.0, narration="unknown")
    line.matched_payment_id = pay.id
    with pytest.raises(UserError, match="Amounts differ"), kit.env.cr.savepoint():
        line.action_confirm_manual_match()
    line.amount = -250.0
    line.action_confirm_manual_match()
    assert (line.match_state, pay.state) == ("manual", "executed")


def test_bank_charge_line_is_booked(kit):
    line = kit.line(-115.0, narration="SMS charge + VAT")
    line.action_post_bank_charge()
    assert (line.match_state, line.matched_kind) == ("manual", "charge")
    assert _balance(kit.env, kit.accounts["bank_charges"]) == 115.0


def test_statement_import_record(kit):
    feed = "Date,Amount,Reference,Description\n2026-10-10,-75.00,CHG-9,Charge\n"
    imp = kit.env["fix.bank.statement.import"].create(
        {"journal_id": kit.bank.id, "file": base64.b64encode(feed.encode()), "filename": "s.csv"}
    )
    imp.action_import()
    assert (imp.state, imp.imported_count) == ("imported", 1)
    assert imp.line_ids.journal_id == kit.bank
    again = kit.env["fix.bank.statement.import"].create(
        {"journal_id": kit.bank.id, "file": base64.b64encode(feed.encode())}
    )
    again.action_import()
    assert again.state == "duplicate"


# --------------------------------------------------------------------------- cash-in-transit


def test_deposit_lifecycle_with_bank_variance(kit):
    env = kit.env
    dep = env["fix.cash.deposit"].create(
        {
            "branch_id": kit.branch.id,
            "journal_id": kit.bank.id,
            "amount": 4000.0,
            "slip_no": "SLP-1",
        }
    )
    assert dep.operating_unit_id == kit.ou
    with pytest.raises(UserError, match="No counted cash shift"), env.cr.savepoint():
        dep.action_dispatch()
    kit.shift(opening=1000.0, counted=5000.0)
    dep.amount = 4500.0
    with pytest.raises(UserError, match="exceeds"), env.cr.savepoint():
        dep.action_dispatch()
    dep.amount = 4000.0
    dep.action_dispatch()
    assert dep.state == "in_transit"
    assert _balance(env, kit.accounts["cash_in_transit"]) == 4000.0
    kit.line(3990.0, reference="SLP-1")
    assert env["fix.bank.statement.line"].auto_match() == 1
    assert (dep.state, dep.variance_amount) == ("variance", -10.0)
    dep.action_resolve_variance()
    assert dep.state == "credited"
    assert _balance(env, kit.accounts["cash_in_transit"]) == 0.0
    assert _balance(env, kit.accounts["cash_shortage"]) == 10.0
    assert _balance(env, kit.bank_acc) == 3990.0


# --------------------------------------------------------------------------- COD


def _cod_order(kit, amount, delivered=True):
    env = kit.env
    consignment = env["fix.consignment"].create(
        {
            "operating_unit_id": kit.ou.id,
            "consignment_type": "delivery",
            "scheduled_date": fields.Datetime.now(),
            "rider_id": kit.employee.id,
            "state": "delivered" if delivered else "in_transit",
        }
    )
    return env["fix.storefront.order"].create(
        {
            "customer_id": kit.vendor.id,
            "total_amount": amount,
            "shipping_address": "Dhanmondi",
            "payment_rail": "cod",
            "state": "dispatched",
            "carrier_consignment_id": consignment.id,
        }
    )


def test_cod_settlement_with_shortage_and_sod(kit):
    env = kit.env
    o1 = _cod_order(kit, 1200.0)
    o2 = _cod_order(kit, 800.0)
    _cod_order(kit, 999.0, delivered=False)
    cash = env["account.journal"].search(
        [("type", "=", "cash"), ("company_id", "=", kit.company.id)], limit=1
    )
    cash = cash or env["account.journal"].create(
        {"name": "Test Cash", "type": "cash", "code": "TCSH"}
    )
    cod = env["fix.cod.settlement"].create(
        {
            "operating_unit_id": kit.ou.id,
            "rider_id": kit.employee.id,
            "remittance_journal_id": cash.id,
            "remitted_amount": 1950.0,
        }
    )
    cod.action_load_orders()
    assert cod.order_ids == o1 | o2
    assert (cod.expected_amount, cod.variance) == (2000.0, -50.0)
    cod.with_user(kit.maker).action_submit()
    with pytest.raises(UserError, match="Segregation"), env.cr.savepoint():
        cod.with_user(kit.maker).action_settle()
    cod.with_user(kit.checker).action_settle()
    assert cod.state == "settled"
    assert _balance(env, kit.accounts["rider_shortage"]) == 50.0
    assert _balance(env, kit.accounts["cod_clearing"]) == -2000.0
    again = env["fix.cod.settlement"].create(
        {"operating_unit_id": kit.ou.id, "rider_id": kit.employee.id}
    )
    again.action_load_orders()
    assert not again.order_ids  # settled orders never load twice


# --------------------------------------------------------------------------- imprest


def test_imprest_cycle(kit):
    env = kit.env
    petty = env["account.account"].create(
        {"code": "T98%04d" % next(_SEQ), "name": "Petty cash test", "account_type": "asset_cash"}
    )
    expense = kit.accounts["bank_charges"]
    fund = env["fix.imprest.fund"].create(
        {
            "name": "Elephant Rd Imprest",
            "operating_unit_id": kit.ou.id,
            "branch_id": kit.branch.id,
            "custodian_id": kit.employee.id,
            "imprest_limit": 10000.0,
            "voucher_limit": 2000.0,
            "account_id": petty.id,
        }
    )
    assert fund.replenish_amount == 10000.0
    topup_ids = fund.with_user(kit.maker).action_request_topup()["topup_ids"]
    topup = env["fix.imprest.topup"].browse(topup_ids)
    topup.journal_id = kit.bank.id
    with pytest.raises(UserError, match="Segregation"), env.cr.savepoint():
        topup.with_user(kit.maker).action_approve()
    topup.with_user(kit.checker).action_approve()
    topup.action_pay()
    env.invalidate_all()
    assert fund.book_balance == 10000.0
    voucher = env["fix.imprest.voucher"].create(
        {
            "fund_id": fund.id,
            "description": "Courier",
            "expense_account_id": expense.id,
            "amount": 2500.0,
            "receipt_ref": "R-1",
        }
    )
    with pytest.raises(UserError, match="per-voucher limit"), env.cr.savepoint():
        voucher.with_user(kit.maker).action_submit()
    voucher.amount = 1500.0
    voucher.with_user(kit.maker).action_submit()
    with pytest.raises(UserError, match="Segregation"), env.cr.savepoint():
        voucher.with_user(kit.maker).action_approve()
    voucher.with_user(kit.checker).action_approve()
    voucher.action_post()
    env.invalidate_all()
    assert fund.book_balance == 8500.0
    assert fund.replenish_amount == 1500.0
    count = (
        env["fix.imprest.count"]
        .with_user(kit.maker)
        .create({"fund_id": fund.id, "counted_amount": 8450.0})
    )
    count.action_reconcile()
    assert (count.state, count.variance) == ("variance", -50.0)
    count.with_user(kit.checker).action_book_variance()
    env.invalidate_all()
    assert fund.book_balance == 8450.0


# --------------------------------------------------------------------------- cheques


def test_received_pdc_cheque_and_bounce(kit):
    env = kit.env
    today = fields.Date.today()
    chq = env["fix.cheque"].create(
        {
            "operating_unit_id": kit.ou.id,
            "direction": "received",
            "cheque_no": "CHQ%s" % next(_SEQ),
            "partner_id": kit.vendor.id,
            "amount": 7000.0,
            "cheque_date": today + timedelta(days=5),
            "journal_id": kit.bank.id,
        }
    )
    assert chq.is_pdc and chq.state == "received"
    with pytest.raises(UserError, match="post-dated"), env.cr.savepoint():
        chq.action_deposit()
    chq.cheque_date = today
    chq.action_deposit()
    kit.line(7000.0, reference=chq.cheque_no)
    assert env["fix.bank.statement.line"].auto_match() == 1
    assert chq.state == "cleared"
    with pytest.raises(UserError, match="return reason"), env.cr.savepoint():
        chq.action_bounce()
    chq.bounce_reason = "Insufficient funds"
    chq.action_bounce()
    assert (chq.state, chq.bounce_count) == ("bounced", 1)
    assert _events(env, "cheque.bounced", chq.id)[0]["reason"] == "Insufficient funds"


def test_cheque_payment_confirms_when_cheque_clears(kit):
    pay = kit.payment(900.0, method="cheque", rail=False, bank_reference="000123")
    pay.action_release()
    chq = kit.env["fix.cheque"].search([("payment_execution_id", "=", pay.id)])
    assert (chq.direction, chq.state, chq.cheque_no) == ("issued", "issued", "000123")
    kit.line(-900.0, narration="CHQ 000123 presented")
    kit.env["fix.bank.statement.line"].auto_match()
    assert chq.state == "cleared"
    assert pay.state == "executed"


# --------------------------------------------------------------------------- gateway


def test_gateway_three_way_match_and_post(kit):
    env = kit.env
    orders = env["fix.storefront.order"]
    for trx, amount in (("TRXA1", 1000.0), ("TRXA2", 500.0)):
        order = orders.create(
            {
                "customer_id": kit.vendor.id,
                "total_amount": amount,
                "shipping_address": "Gulshan",
                "payment_rail": "bkash",
            }
        )
        order.action_confirm_payment(payment_ref=trx)
    csv_text = (
        "TrxID,Transaction Date,Amount,Fee,VAT on Fee,Net Amount\n"
        "TRXA1,2026-10-20,1000.00,15.00,2.25,982.75\n"
        "TRXA2,2026-10-20,500.00,7.50,1.13,491.37\n"
    )
    batch = env["fix.gateway.settlement"].create(
        {
            "provider": "bkash",
            "provider_batch_ref": "BK-SET-%s" % next(_SEQ),
            "journal_id": kit.bank.id,
            "settlement_date": fields.Date.today(),
            "report_file": base64.b64encode(csv_text.encode()),
        }
    )
    batch.action_import_report()
    assert batch.line_count == 2 and batch.exception_count == 0
    assert batch.state == "imported"  # bank credit not yet seen
    with pytest.raises(UserError, match="three-way"), env.cr.savepoint():
        batch.action_post()
    kit.line(1474.12, narration="BKASH settlement %s" % batch.provider_batch_ref)
    env["fix.bank.statement.line"].auto_match()
    assert batch.state == "matched" and batch.bank_matched
    batch.action_post()
    assert batch.state == "posted"
    assert _balance(env, kit.accounts["channel_clearing"]) == -1500.0
    assert _balance(env, kit.accounts["gateway_fees"]) == 25.88
    dup = env["fix.gateway.settlement"].create(
        {
            "provider": "bkash",
            "journal_id": kit.bank.id,
            "report_file": base64.b64encode(csv_text.encode()),
        }
    )
    with pytest.raises(UserError, match="already imported"), env.cr.savepoint():
        dup.action_import_report()


def test_gateway_unknown_trx_is_an_exception(kit):
    csv_text = "Transaction ID,Amount,Net\nNOPE-1,100,98\n"
    batch = kit.env["fix.gateway.settlement"].create(
        {
            "provider": "nagad",
            "journal_id": kit.bank.id,
            "report_file": base64.b64encode(csv_text.encode()),
        }
    )
    batch.action_import_report()
    assert batch.state == "exceptions"
    assert batch.line_ids.match_state == "missing_receipt"
    assert batch.line_ids.fee == 2.0


def test_settlement_csv_parser_refuses_unknown_layout():
    from odoo.addons.cd_cash_position.models.gateway_settlement import parse_settlement_csv

    with pytest.raises(UserError, match="not recognised"):
        parse_settlement_csv("foo,bar\n1,2\n")
    with pytest.raises(UserError, match="does not add up"):
        parse_settlement_csv("trxid,amount,fee,net\nA,100,2,50\n")
    rows = parse_settlement_csv('tran_id,amount,store_amount\nS1,"1,000.00",975.00\n')
    assert rows == [
        {"trx_id": "S1", "date": False, "gross": 1000.0, "fee": 25.0, "fee_vat": 0.0, "net": 975.0}
    ]


# --------------------------------------------------------------------------- facilities


def test_term_loan_schedule_payment_and_covenant(kit):
    env = kit.env
    loan_acc = env["account.account"].create(
        {
            "code": "T97%04d" % next(_SEQ),
            "name": "Term loan test",
            "account_type": "liability_non_current",
        }
    )
    fac = env["fix.bank.facility"].create(
        {
            "name": "BRAC TL-1",
            "lender_id": kit.vendor.id,
            "facility_type": "term_loan",
            "limit_amount": 1200000.0,
            "principal": 1200000.0,
            "interest_rate": 12.0,
            "tenor_months": 12,
            "start_date": date(2026, 11, 1),
            "liability_account_id": loan_acc.id,
            "journal_id": kit.bank.id,
        }
    )
    fac.action_generate_schedule()
    assert len(fac.repayment_ids) == 12
    assert round(sum(fac.repayment_ids.mapped("principal")), 2) == 1200000.0
    assert fac.repayment_ids[0].interest == 12000.0
    fac.action_activate()
    # disbursement booked by GL elsewhere: Dr bank / Cr loan
    from odoo.addons.cd_cash_position.models.treasury_common import post_treasury_move

    post_treasury_move(
        env,
        kit.company,
        fields.Date.today(),
        "Loan drawdown",
        [
            (kit.bank_acc, "drawdown", 1200000.0, 0.0, None),
            (loan_acc, "drawdown", 0.0, 1200000.0, None),
        ],
    )
    env.invalidate_all()
    assert (fac.utilised, fac.available) == (1200000.0, 0.0)
    first = fac.repayment_ids[0]
    first.action_pay()
    assert first.state == "paid"
    env.invalidate_all()
    assert fac.utilised == round(1200000.0 - first.principal, 2)
    assert _balance(env, kit.accounts["interest_expense"]) == 12000.0
    cov = env["fix.facility.covenant"].create(
        {
            "facility_id": fac.id,
            "name": "Utilisation cap",
            "metric": "utilisation_pct",
            "operator": "le",
            "threshold": 50.0,
        }
    )
    cov.action_test()
    assert cov.last_result == "breach"
    assert cov.test_ids.result == "breach"


# --------------------------------------------------------------------------- position & reports


def test_cash_position_reads_gl_and_queue(kit):
    env = kit.env
    pay = kit.payment(700.0)
    snap = env["fix.cash.position"].create({"company_id": kit.company.id})
    assert snap.pending_payments >= 700.0
    assert snap.total_position == round(
        snap.bank_balance
        + snap.drawer_float_total
        + snap.petty_cash_total
        + snap.cash_in_transit_total
        - snap.pending_payments,
        2,
    )
    new_ids = snap.action_take_snapshot()["snapshot_ids"]
    assert len(new_ids) == 1
    assert pay.state == "pending"


def test_reports_compute_from_documents(kit):
    from odoo.addons.cd_cash_position.models import treasury_reports as tr

    env = kit.env
    kit.shift(opening=500.0, counted=2500.0)
    out = tr.branch_cash(env)
    row = next(r for r in out["rows"] if r["branch"] == kit.branch.name)
    assert (row["deposit_due"], row["undeposited"], row["status"]) == (
        2000.0,
        2000.0,
        "Undeposited",
    )
    assert tr.branch_cash_uncollected(env) >= 2000.0

    env["fix.cash.forecast.item"].create(
        {
            "name": "Branch rent",
            "amount": 50000.0,
            "frequency": "monthly",
            "start_date": fields.Date.today() + timedelta(days=7),
        }
    )
    kit.payment(1234.0)
    fc = tr.cash_forecast(env)
    assert len(fc["rows"]) == 17
    current = fc["rows"][4]
    assert current["payments_out"] >= 1234.0
    assert sum(r["recurring_out"] for r in fc["rows"]) >= 50000.0 * 3

    for name, fn in tr.REPORTS.items():
        res = fn(
            env,
            date_from=str(fields.Date.today() - timedelta(days=60)),
            date_to=str(fields.Date.today()),
        )
        assert set(res["cols"]) <= set(res.get("labels", {})) or not res["cols"], name
        for r in res["rows"]:
            assert set(res["cols"]) <= set(r), name
    kp = tr.kpis(env)
    assert set(kp) == {"cash_position", "branch_cash_uncollected", "payments_awaiting_bank"}


def test_fx_holdings_values_at_latest_rate(kit):
    from odoo.addons.cd_cash_position.models import treasury_reports as tr

    env = kit.env
    # the foreign currency: anything but the company's own (fix_test's
    # company may not run on BDT)
    usd = (
        env.ref("base.JPY")
        if kit.company.currency_id == env.ref("base.USD")
        else env.ref("base.USD")
    )
    usd.active = True
    today = fields.Date.today()
    booked_on = today - timedelta(days=3)
    Rate = env["res.currency.rate"]
    Rate.search([("currency_id", "=", usd.id), ("name", "in", (booked_on, today))]).unlink()
    Rate.create(
        {"currency_id": usd.id, "name": booked_on, "rate": 1 / 110.0, "company_id": kit.company.id}
    )
    Rate.create(
        {"currency_id": usd.id, "name": today, "rate": 1 / 120.0, "company_id": kit.company.id}
    )
    journal = env["account.journal"].create(
        {"name": "FX Account", "type": "bank", "code": "TFX", "currency_id": usd.id}
    )
    gen = env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", kit.company.id)], limit=1
    )
    move = env["account.move"].create(
        {
            "journal_id": gen.id,
            "date": booked_on,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": journal.default_account_id.id,
                        "name": "in",
                        "currency_id": usd.id,
                        "amount_currency": 1000.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "account_id": kit.accounts["channel_clearing"].id,
                        "name": "in",
                        "balance": -110000.0,
                    },
                ),
            ],
        }
    )
    move.action_post()
    out = tr.fx_holdings(env)
    row = next(r for r in out["rows"] if r["account"] == "FX Account")
    assert row["foreign"] == 1000.0
    assert row["book"] == 110000.0
    assert row["revalued"] == 120000.0
    assert row["unrealised"] == 10000.0
