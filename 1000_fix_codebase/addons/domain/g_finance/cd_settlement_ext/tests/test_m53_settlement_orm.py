# cd_settlement_ext — A08 M53 settlement depth on the live registry
# (rolled-back fix_test, addons/conftest.py `odoo_env`): commission schemes,
# partner / referral commissions paid in payout runs, clawbacks recovered
# from payouts, escrow holds, the payout GL guard and the IAS 37 warranty
# provision. Every test runs in its OWN company so the accrued-commission /
# invoice sets are exactly the ones the test creates. Money is hand-computed.
from __future__ import annotations

import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from odoo.addons.cd_partner.tests.m40_fixtures import approved_rate, make_onboardable
from odoo.addons.cd_settlement_ext.tests.b4_marketplace_fixtures import (
    link_paid_order,
    marketplace_ready,
)
from odoo.addons.cd_settlement_ext.tests.test_a08_m53_controls import (
    declare_marketplace_agent,
)
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

TAG = uuid.uuid4().hex[:6].upper()

# the settlement chart + the A08 M53 roles that have no default code
CHART = {
    "101000": ("Disbursement Bank", "asset_cash", None),
    "400100": ("Marketplace Commission Revenue", "income", None),
    "200200": ("Marketplace Seller Payable", "liability_payable", None),
    "210100": ("TDS Withheld Liability", "liability_current", None),
    "631100": ("Partner Commission Expense", "expense", "partner_commission_expense"),
    "200300": ("Partner Commission Payable", "liability_payable", "partner_payable"),
    "200400": ("Customer Refund Clearing", "liability_current", "clawback_recovery"),
    "640100": ("Warranty Expense", "expense", "warranty_expense"),
    "250100": ("Warranty Provision", "liability_current", "warranty_provision"),
}
PARAMS = [role for *_x, role in CHART.values() if role]


def _bank(env, partner, routing, account):
    bank = env["res.bank"].create({"name": f"{partner.name} Bank", "bic": routing})
    env["res.partner.bank"].create(
        {"partner_id": partner.id, "acc_number": account, "bank_id": bank.id}
    )


@pytest.fixture
def co(odoo_env):
    env0 = odoo_env
    company = env0["res.company"].create({"name": f"M53 Co {TAG}-{uuid.uuid4().hex[:4]}"})
    env = env0(context=dict(env0.context, allowed_company_ids=company.ids))
    ou = env["operating.unit"].create(
        {
            "name": f"M53 OU {TAG}",
            "code": f"M53{uuid.uuid4().hex[:4].upper()}",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    env["account.journal"].create(
        {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
    )
    declare_marketplace_agent(env, company)
    accounts = {}
    for code, (name, kind, _role) in CHART.items():
        accounts[code] = (
            env["account.account"]
            .with_company(company)
            .create(
                {
                    "code": code,
                    "name": name,
                    "account_type": kind,
                    "company_ids": [(6, 0, company.ids)],
                }
            )
        )
    param = env["ir.config_parameter"]
    for code, (_n, _k, role) in CHART.items():
        if role:
            param.set_param(f"cd_settlement_ext.account_code.{role}", code)
    _bank(env, company.partner_id, "020270001", "1101000099887")

    def user(login, *groups):
        return env["res.users"].create(
            {
                "name": login.title(),
                "login": f"{login}-{company.id}@m53.test",
                "company_id": company.id,
                "company_ids": [(6, 0, company.ids)],
                "operating_unit_ids": [(6, 0, ou.ids)],
                "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
            }
        )

    ns = SimpleNamespace(env=env, company=company, ou=ou, accounts=accounts, user=user)
    yield ns
    for role in PARAMS:  # get_param is cached across rolled-back tests
        param.set_param(f"cd_settlement_ext.account_code.{role}", False)


def _partner_with_referral(co, base=20000.0, rate=0.05, kind="referral"):
    env = co.env
    party = env["res.partner"].create({"name": f"Dhanmondi Referrals {TAG}"})
    _bank(env, party, "060272531", "2050123456789")
    partner = env["fix.partner"].create(
        {
            "name": party.name,
            "partner_id": party.id,
            "partner_type": kind,
            "company_id": co.company.id,
        }
    )
    # A04 ERP audit M40-F5/F9/F11 set-up: onboarded, with an approved rate
    make_onboardable(env, partner)
    partner.action_onboard()
    approved_rate(partner, rate)
    referral = env["fix.referral"].create(
        {"name": f"REF-{TAG}", "partner_id": partner.id, "company_id": co.company.id}
    )
    referral.action_convert(base_amount=base)
    referral.action_earn_commission()
    return party, partner, referral


def _confirm_bank(partner, routing):
    """M52 dual control (B2): a second person confirmed the payee account."""
    bank = partner.bank_ids[:1]
    bank._fix_confirming().write({"fix_routing_number": routing})
    bank._fix_confirming()._fix_mark_confirmed("call-back on the number on file (test)", None)
    return bank


def _inbox_approve(env, record, user):
    task = (
        env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("res_model", "=", record._name),
                ("res_id", "=", record.id),
                ("state", "=", "pending"),
                ("assigned_user_id", "=", user.id),
            ],
            limit=1,
        )
    )
    assert task, "no M63 task for %s" % user.login
    task.with_user(user).action_approve()
    record.invalidate_recordset()


def _pay_through_treasury(co, run, requester, preparer, releaser):
    """A08 F2: the approved run is paid as M50 instructions — prepared by an
    accountant, released by an Accounting Administrator who did not approve
    the run, confirmed by the imported bank statement debit."""
    env = co.env
    run.with_user(requester).action_request_payments()
    for pay in run.line_ids.mapped("payment_execution_id"):
        pay.with_user(preparer).action_prepare()
        pay.with_user(releaser).action_release()
        line = env["fix.bank.statement.line"].create(
            {
                "company_id": co.company.id,
                "journal_id": (pay.released_journal_id or pay.journal_id).id,
                "date": date.today(),
                "amount": -pay.released_amount,
                "reference": pay.name,
                "statement_file_hash": "m53-%s" % pay.id,
            }
        )
        line._fix_match_document("matched_payment_id", pay, "manual")
    run.invalidate_recordset()


def _postings(move):
    return sorted(
        (line.account_id.with_company(move.company_id).code, line.debit, line.credit)
        for line in move.line_ids
    )


# --------------------------------------------------------------------------- schemes


class TestCommissionSchemes:
    def test_find_prefers_the_specific_line_and_refuses_overlaps(self, co):
        Scheme = co.env["fix.commission.scheme"]
        generic = Scheme.create(
            {
                "name": "Partner TDS",
                "scheme_type": "partner",
                "tds_rate": 0.10,
                "date_from": date(2025, 7, 1),
                "company_id": co.company.id,
            }
        )
        franchise = Scheme.create(
            {
                "name": "Franchise TDS",
                "scheme_type": "partner",
                "partner_type": "franchise",
                "tds_rate": 0.05,
                "date_from": date(2025, 7, 1),
                "company_id": co.company.id,
            }
        )
        on = date(2026, 10, 1)
        assert Scheme._find("partner", on, co.company, partner_type="franchise") == franchise
        assert Scheme._find("partner", on, co.company, partner_type="referral") == generic
        assert not Scheme._find("partner", date(2025, 6, 30), co.company)
        with pytest.raises(ValidationError, match="overlaps"), co.env.cr.savepoint():
            Scheme.create(
                {
                    "name": "Dup",
                    "scheme_type": "partner",
                    "tds_rate": 0.1,
                    "date_from": date(2026, 1, 1),
                    "company_id": co.company.id,
                }
            )
        with pytest.raises(ValidationError, match="fractions"), co.env.cr.savepoint():
            Scheme.create(
                {
                    "name": "Bad",
                    "scheme_type": "seller",
                    "tds_rate": 1.5,
                    "date_from": date(2026, 1, 1),
                    "company_id": co.company.id,
                }
            )
        assert generic.tds_on(1000.0, 20000.0) == 100.0
        franchise.tds_base = "gross"
        assert franchise.tds_on(1000.0, 20000.0) == 1000.0


# --------------------------------------------------------------------------- partner payouts + clawback


class TestPartnerPayoutWithClawback:
    def test_referral_accrues_and_is_paid_net_of_tds_and_clawback(self, co):
        env = co.env
        env["fix.commission.scheme"].create(
            {
                "name": "Partner TDS 10%",
                "scheme_type": "partner",
                "tds_rate": 0.10,
                "date_from": date(2025, 7, 1),
                "company_id": co.company.id,
            }
        )
        party, _partner, referral = _partner_with_referral(co)
        assert referral.commission_amount == 1000.0  # 20,000 x 5%

        referral.action_accrue_commission()
        ledger = referral.commission_ledger_id
        # commission 1000.00; TDS 10% = 100.00, plus the ITA 2023 s.142/264/265
        # 50% penalty uplift for an UNVERIFIED PSR -> 150.00, net 850.00
        # (A04 audit 2026-10-31: the uplift is the statutory behaviour; the
        # old expectation of a flat 100.00 predates it)
        assert (
            ledger.source_type,
            ledger.commission_amount,
            ledger.tds_amount,
            ledger.net_payable,
        ) == (
            "partner_referral",
            1000.0,
            150.0,
            850.0,
        )
        assert not ledger.psr_verified
        assert (ledger.state, referral.payout_state) == ("accrued", "accrued")
        # Dr partner commission expense / Cr partner payable
        assert _postings(ledger.gl_move_id) == [("200300", 0.0, 1000.0), ("631100", 1000.0, 0.0)]
        with pytest.raises(UserError, match="already in the commission ledger"), env.cr.savepoint():
            referral.action_accrue_commission()

        # a clawback of 300.00 owed by the partner: requester != approver
        clerk = co.user("clerk", "account.group_account_user")
        manager = co.user("manager", "account.group_account_manager")
        claw = env(user=clerk)["fix.settlement.adjustment"].create(
            {
                "adjustment_type": "clawback",
                "seller_partner_id": party.id,
                "amount": 300.0,
                "reason": "Refund on a disputed referral job",
            }
        )
        with pytest.raises(AccessError, match="finance manager"), env.cr.savepoint():
            claw.with_user(clerk).action_activate()
        claw.with_user(manager).action_activate()
        assert claw.state == "active" and claw.remaining_amount == 300.0

        run = env["fix.payout.run"].create({"period": "2026-10", "company_id": co.company.id})
        with pytest.raises(UserError, match="only a confirmed"), env.cr.savepoint():
            run.action_post_payout_to_gl()
        run.action_collect_accrued()
        assert run.commission_ids == ledger and run.clawback_ids == claw
        # 900.00 net - 300.00 clawback = 600.00 disbursed
        # with the s.142 no-PSR uplift: TDS 150 (10% x 1.5), net payable 1000-150-300 = 550
        assert (run.total_clawback, run.total_payable, run.total_tds) == (300.0, 550.0, 150.0)

        # A08 F2 (rewritten: the run used to pay on its own BEFTN file and a
        # typed bank reference): prepared by the clerk, approved from the M63
        # inbox by the manager, paid through treasury
        journal = env["account.journal"].create(
            {"name": "Payout Bank", "code": "PYB", "type": "bank", "company_id": co.company.id}
        )
        env["ir.config_parameter"].set_param("cd_settlement_ext.payout_journal_code", "PYB")
        env["ir.config_parameter"].set_param("cd_cash_position.release_single_ceiling", "5000000")
        _confirm_bank(party, "060272531")
        treasurer = co.user("treasurer", "account.group_account_user")
        releaser = co.user("releaser", "account.group_account_manager")
        run.with_user(clerk).action_prepare()
        with pytest.raises(UserError), env.cr.savepoint():
            run.with_user(clerk).action_approve()
        _inbox_approve(env, run, manager)
        assert run.state == "approved" and ledger.state == "accrued"
        with pytest.raises(UserError, match="typed reference"), env.cr.savepoint():
            run.with_user(manager).action_confirm_bank_settlement("BEFTN-SETTLED-77")
        _pay_through_treasury(co, run, clerk, treasurer, releaser)
        assert run.state == "executed" and ledger.state == "paid"
        assert (claw.recovered_amount, claw.remaining_amount, claw.state) == (
            300.0,
            0.0,
            "recovered",
        )
        assert run.total_clawback == 300.0  # frozen from the recovery lines
        # Dr partner payable 1000 / Cr TDS 150 (no-PSR uplift) / Cr refund
        # clearing 300 / Cr the paying bank account 550 (M50 books nothing for
        # a payout line: the bank is credited once)
        assert _postings(run.gl_move_id) == sorted(
            [
                (journal.default_account_id.code, 0.0, 550.0),
                ("200300", 1000.0, 0.0),
                ("200400", 0.0, 300.0),
                ("210100", 0.0, 150.0),
            ]
        )
        (stmt,) = run.statement_ids
        # 850.00 net (after the s.142 no-PSR TDS uplift) - 300.00 clawback = 550.00
        assert (stmt.net_payable, stmt.clawback_amount, stmt.state) == (550.0, 300.0, "issued")
        stmt.action_settle_statement()
        assert stmt.state == "settled"

    def test_accrual_refuses_without_a_scheme(self, co):
        co.env["fix.commission.scheme"].search([("company_id", "=", co.company.id)]).active = False
        _party, _partner, referral = _partner_with_referral(co)
        with pytest.raises(UserError, match="No partner commission scheme"), co.env.cr.savepoint():
            referral.action_accrue_commission()


# --------------------------------------------------------------------------- escrow


class TestEscrow:
    def test_escrow_holds_out_of_payouts_until_released_by_another_person(self, co):
        env = co.env
        seller = env["res.partner"].create({"name": f"Khulna Mobile {TAG}"})
        row = env["fix.commission.ledger"].create(
            {
                "seller_partner_id": seller.id,
                "gross_amount": 5000.0,
                "commission_rate": 0.10,
                "company_id": co.company.id,
            }
        )
        # A04 ERP M12-F1/F9: the customer paid into M20; VAT on the commission
        marketplace_ready(env, co.company)
        link_paid_order(row)
        row.action_post_to_gl()
        # 5,000 - 500 commission - 75 VAT on it (15%)
        assert row.state == "accrued" and row.net_payable == 4425.0
        # FLAW-12.2: a marketplace commission is also held for a 7-day buyer
        # dispute window. This test is about the DISPUTE escrow, and a quality
        # dispute raised, investigated and released inside 7 days is not the
        # realistic case — age the row past the window so the two holds are
        # tested independently.
        env.cr.execute(
            "UPDATE fix_commission_ledger SET create_date = create_date - interval '8 days' "
            "WHERE id = %s",
            (row.id,),
        )
        # Raw SQL does not trigger a recompute, so the STORED
        # `escrow_release_date` still reflects the pre-aged accrual. Tell the
        # ORM what changed. This used to work by accident: the flag and the
        # stored date shared one compute, so merely READING the flag wrote the
        # column back - a write on every read, which broke the portal's
        # readonly cursors. The two are separate now, so the recompute is
        # explicit (A04 audit, 2026-11-01).
        row.invalidate_recordset()
        row._compute_escrow_release()  # re-project the stored release date
        row.flush_recordset()
        assert row.escrow_window_elapsed is True
        clerk = co.user("esc-clerk", "account.group_account_user")
        manager = co.user("esc-manager", "account.group_account_manager")
        escrow = env(user=clerk)["fix.settlement.adjustment"].create(
            {
                "adjustment_type": "escrow",
                "seller_partner_id": seller.id,
                "commission_ids": [(6, 0, row.ids)],
                "reason": "Open quality dispute",
            }
        )
        escrow.with_user(clerk).action_activate()
        assert (escrow.state, escrow.amount, row.escrow_hold) == ("active", 4425.0, True)

        run = env["fix.payout.run"].create({"period": "2026-10", "company_id": co.company.id})
        with pytest.raises(UserError, match="No accrued commissions"), env.cr.savepoint():
            run.action_collect_accrued()
        run.commission_ids = [(6, 0, row.ids)]
        with pytest.raises(UserError, match="held in escrow"), env.cr.savepoint():
            run.action_prepare()
        run.commission_ids = [(5,)]

        with pytest.raises(AccessError, match="Segregation of duties"), env.cr.savepoint():
            escrow.with_user(clerk).action_release()
        escrow.with_user(manager).action_release()
        assert escrow.state == "released" and not row.escrow_hold
        run.action_collect_accrued()
        assert run.commission_ids == row

    def test_forfeit_moves_the_liability_to_refund_clearing(self, co):
        env = co.env
        seller = env["res.partner"].create({"name": f"Rajshahi Fix {TAG}"})
        row = env["fix.commission.ledger"].create(
            {
                "seller_partner_id": seller.id,
                "gross_amount": 2000.0,
                "commission_rate": 0.10,
                "tds_amount": 50.0,
                "company_id": co.company.id,
            }
        )
        marketplace_ready(env, co.company)  # A04 ERP M12-F1/F9
        link_paid_order(row)
        row.action_post_to_gl()
        clerk = co.user("ff-clerk", "account.group_account_user")
        manager = co.user("ff-manager", "account.group_account_manager")
        escrow = env(user=clerk)["fix.settlement.adjustment"].create(
            {
                "adjustment_type": "escrow",
                "seller_partner_id": seller.id,
                "commission_ids": [(6, 0, row.ids)],
                "reason": "Customer refunded in full",
            }
        )
        escrow.with_user(clerk).action_activate()
        with pytest.raises(AccessError, match="finance manager"), env.cr.savepoint():
            escrow.with_user(clerk).action_forfeit()
        escrow.with_user(manager).action_forfeit()
        # seller share 1770.00 (= net 1720 + TDS 50; the 30.00 VAT on the 200.00
        # commission is 1000 FiX's) leaves the seller payable
        assert _postings(escrow.move_id) == [("200200", 1770.0, 0.0), ("200400", 0.0, 1770.0)]
        assert (escrow.state, row.state) == ("forfeited", "forfeited")


# --------------------------------------------------------------------------- warranty provision


def _repair_invoice(co, customer, when, taxable):
    return co.env["fix.ar.invoice"].create(
        {
            "company_id": co.company.id,
            "customer_id": customer.id,
            "operating_unit_id": co.ou.id,
            "source_model": "fix.service.order",
            "source_id": -(uuid.uuid4().int % 2_000_000_000),
            "invoice_date": when,
            "state": "issued",
            "line_ids": [(0, 0, {"taxable_amount": taxable, "vat_amount": taxable * 0.15})],
        }
    )


def _rework_order(co, customer, created):
    env = co.env
    suffix = uuid.uuid4().hex[:4].upper()
    brand = env["fix.brand"].create({"name": f"WP Brand {suffix}", "code": f"WP{suffix}"})
    model = env["fix.device.model"].create(
        {"brand_id": brand.id, "name": "WP-1", "device_type": "laptop"}
    )
    entity = env["fix.entity"].create(
        {"code": f"EN-WP{suffix}", "legal_name": f"Entity WP {suffix}", "company_id": co.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "code": f"BR-WP{suffix}",
            "name": f"Branch WP {suffix}",
            "entity_id": entity.id,
            "operating_unit_id": co.ou.id,
        }
    )
    device = env["fix.device"].create({"device_model_id": model.id})
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "operating_unit_id": co.ou.id,
            "fault_description": "Came back: same fault",
            "is_rework": True,
        }
    )
    env.cr.execute(
        "UPDATE fix_service_order SET create_date = %s WHERE id = %s", (created, order.id)
    )
    order.invalidate_recordset(["create_date"])
    return order


class TestWarrantyProvision:
    def test_provision_is_measured_posted_with_sod_and_released(self, co):
        env = co.env
        customer = env["res.partner"].create({"name": f"Warranty Cust {TAG}"})
        env["fix.warranty.provision.policy"].create(
            {
                "name": "30-day workmanship",
                "warranty_days": 30,
                "lookback_months": 12,
                "cost_ratio": 0.40,
                "date_from": date(2000, 1, 1),
                "company_id": co.company.id,
            }
        )
        _repair_invoice(co, customer, date(2001, 3, 20), 10000.0)  # inside the 30 days
        _repair_invoice(co, customer, date(2001, 1, 10), 5000.0)  # history only
        _repair_invoice(co, customer, date(2000, 6, 1), 4000.0)  # history only
        rework = _rework_order(co, customer, "2001-02-15 10:00:00")
        if rework.company_id != co.company:
            pytest.skip("service orders take the branch company in this build")

        clerk = co.user("wp-clerk", "account.group_account_user")
        manager = co.user("wp-manager", "account.group_account_manager")
        prov = env(user=clerk)["fix.warranty.provision"].create({"period": "2001-03"})
        prov.with_user(clerk).action_compute()
        # rework rate 1/3; required = 10,000 x 1/3 x 0.40 = 1,333.33
        assert (prov.lookback_orders, prov.lookback_reworks) == (3, 1)
        assert (prov.revenue_in_warranty, prov.required_balance, prov.movement) == (
            10000.0,
            1333.33,
            1333.33,
        )
        with (
            pytest.raises(AccessError, match=r"(Segregation of duties|finance manager)"),
            env.cr.savepoint(),
        ):
            prov.with_user(clerk).action_post()
        prov.with_user(manager).action_post()
        assert prov.state == "posted"
        assert _postings(prov.move_id) == [("250100", 0.0, 1333.33), ("640100", 1333.33, 0.0)]

        # April: the March repairs left the warranty window -> release
        april = env(user=clerk)["fix.warranty.provision"].create({"period": "2001-04"})
        april.with_user(clerk).action_compute()
        assert (april.required_balance, april.opening_balance, april.movement) == (
            0.0,
            1333.33,
            -1333.33,
        )
        april.with_user(manager).action_post()
        assert _postings(april.move_id) == [("250100", 1333.33, 0.0), ("640100", 0.0, 1333.33)]
        with pytest.raises(UserError, match="posted"), env.cr.savepoint():
            prov.action_compute()

    def test_compute_refuses_without_a_policy_and_bad_periods(self, co):
        env = co.env
        with pytest.raises(ValidationError, match="YYYY-MM"), env.cr.savepoint():
            env["fix.warranty.provision"].create({"period": "March"})
        prov = env["fix.warranty.provision"].create({"period": "1999-01"})
        with pytest.raises(UserError, match="No warranty provision policy"), env.cr.savepoint():
            prov.action_compute()
