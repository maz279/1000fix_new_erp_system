# cd_cash_position — the bank branch directory (A08 · M50 take-on 2026-11-09):
# the Bank -> Branch -> Account middle layer and its routing-number
# propagation into res.partner.bank / account.journal. Real ORM behaviour on
# fix_test via odoo_env; everything rolls back.
from __future__ import annotations

import pytest
from odoo.exceptions import UserError, ValidationError
from psycopg2.errors import UniqueViolation

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError)


@pytest.fixture
def ab_bank(odoo_env):
    return odoo_env["res.bank"].create({"name": "AB BANK PLC", "bic": "ABBLBDDH"})


@pytest.fixture
def ab_branch(odoo_env, ab_bank):
    return odoo_env["res.bank.branch"].create(
        {
            "bank_id": ab_bank.id,
            "name": "New Elephant Road",
            "district": "DHAKA",
            "routing_number": "020263498",
        }
    )


def test_branch_display_name_carries_routing(odoo_env, ab_branch):
    # payment operators select on the routing, so it belongs in the label
    assert ab_branch.display_name == "AB BANK PLC — New Elephant Road (020263498)"
    # ...and typing the routing (or the bank) in a dropdown finds the branch
    Branch = odoo_env["res.bank.branch"]
    assert ab_branch in Branch.search([("display_name", "ilike", "020263498")])
    assert ab_branch in Branch.search([("display_name", "ilike", "AB BANK")])


def test_branch_routing_must_be_nine_digits(odoo_env, ab_bank):
    # eight digits refused; the savepoint keeps the poisoned insert out
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        odoo_env["res.bank.branch"].create(
            {"bank_id": ab_bank.id, "name": "Gulshan", "routing_number": "90261725"}
        )
    # nine accepted, empty accepted (unverified branch)
    ok = odoo_env["res.bank.branch"].create(
        {"bank_id": ab_bank.id, "name": "Gulshan", "routing_number": "090261725"}
    )
    assert ok.routing_number == "090261725"
    pending = odoo_env["res.bank.branch"].create({"bank_id": ab_bank.id, "name": "Satmasjid Road"})
    assert pending.routing_number is False


def test_branch_unique_per_bank(odoo_env, ab_bank, ab_branch):
    # the DB constraint refuses a second branch of the same name at the bank
    with pytest.raises(UniqueViolation), odoo_env.cr.savepoint():
        odoo_env["res.bank.branch"].create({"bank_id": ab_bank.id, "name": "New Elephant Road"})
    # the same branch name at another bank is a different branch
    other = odoo_env["res.bank"].create({"name": "PUBALI BANK PLC"})
    odoo_env["res.bank.branch"].create({"bank_id": other.id, "name": "New Elephant Road"})


def test_partner_bank_onchange_defaults_from_directory(odoo_env, ab_branch):
    pb = odoo_env["res.partner.bank"].new({"acc_number": "4006762569000"})
    pb.bank_branch_id = ab_branch
    pb._onchange_bank_branch_id()
    # institution, free-text branch and routing all flow from the directory
    assert pb.bank_id.id == ab_branch.bank_id.id
    assert pb.fix_branch_name == "New Elephant Road"
    assert pb.fix_routing_number == "020263498"


def test_account_and_journal_carry_the_directory_routing(odoo_env, ab_branch):
    env = odoo_env
    company = env.ref("base.main_company")
    partner = company.partner_id
    pb = env["res.partner.bank"].create(
        {
            "acc_number": "4006762569000",
            "partner_id": partner.id,
            "bank_id": ab_branch.bank_id.id,
            "bank_branch_id": ab_branch.id,
            "fix_branch_name": ab_branch.name,
            "fix_routing_number": ab_branch.routing_number,
            "fix_account_type": "current",
        }
    )
    assert pb.fix_routing_number == "020263498"
    journal = env["account.journal"].create(
        {
            "name": "AB Bank — Elephant Road (test)",
            "code": "ABTST",
            "type": "bank",
            "bank_account_id": pb.id,
            "company_id": company.id,
        }
    )
    # the journal reads the account's BD fields through its related fields
    assert journal.fix_routing_number == "020263498"
    assert journal.fix_account_type == "current"


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "company_id": env.company.id,
                "company_ids": [(6, 0, [env.company.id])],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def test_house_bank_account_under_four_eyes_control(odoo_env, ab_branch):
    # report R8: the company's OWN (house-bank) accounts sit under the same
    # M52 dual control as payee accounts — confirmed only by a second person
    # after a recorded call-back, and any payment-field edit withdraws it.
    env = odoo_env
    if "fix.payee.bank.change" not in env:
        pytest.skip("cd_ap_ext (M52 bank-detail control) is not installed")
    company = env.company
    proposer = _user(env, "bankdir_proposer", ["account.group_account_manager"])
    confirmer = _user(env, "bankdir_confirmer", ["account.group_account_manager"])
    change = (
        env["fix.payee.bank.change"]
        .with_user(proposer)
        .create(
            {
                "partner_id": company.partner_id.id,
                "acc_number": "4006762569000",
                "bank_id": ab_branch.bank_id.id,
                "routing_number": ab_branch.routing_number,
                "acc_holder_name": company.name,
                "verification_ref": "Called AB Bank Elephant Road on its published number; "
                "account and routing read back from the cheque leaf",
            }
        )
    )
    change.with_user(proposer).action_propose()
    # the proposer cannot also confirm (segregation of duties)
    with pytest.raises(REFUSED), env.cr.savepoint():
        change.with_user(proposer).action_confirm()
    change.with_user(confirmer).action_confirm()
    acct = env["res.partner.bank"].search(
        [("partner_id", "=", company.partner_id.id), ("acc_number", "=", "4006762569000")]
    )
    assert len(acct) == 1 and acct.fix_confirmed
    assert acct.fix_routing_number == "020263498"
    # the confirmation is never written directly
    with pytest.raises(REFUSED), env.cr.savepoint():
        acct.write({"fix_confirmed": True})
    # re-pointing the routing makes it a new account: the confirmation lapses
    acct.write({"fix_routing_number": "020264000"})
    assert not acct.fix_confirmed


def test_partner_bank_bad_routing_refused(odoo_env, ab_branch):
    env = odoo_env
    company = env.ref("base.main_company")
    with pytest.raises(REFUSED), env.cr.savepoint():
        env["res.partner.bank"].create(
            {
                "acc_number": "4006762569001",
                "partner_id": company.partner_id.id,
                "bank_id": ab_branch.bank_id.id,
                "fix_routing_number": "20263",
            }
        )
