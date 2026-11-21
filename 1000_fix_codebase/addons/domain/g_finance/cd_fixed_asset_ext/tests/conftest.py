# Shared live-ORM fixtures for the M49 tests: a fully configured asset
# category (accounts + journal) and accounting users for the SoD checks.
import itertools

import pytest

_SEQ = itertools.count(1)


def make_user(env, *groups):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": f"M49 Test User {n}",
            "login": f"m49-test-{n}@test.local",
            "group_ids": [(6, 0, [env.ref(g).id for g in groups])],
        }
    )


def fixture_ou(env, company=None):
    """The branch (operating unit) a fixture asset, CWIP project or lease is
    booked on. A07 ERP audit (2026-11-20, FIN-01/02): an M49 entry is posted
    on the record's own branch and is refused without one (never the
    company's first OU), so every fixture names its branch."""
    company = company or env.company
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    if not ou:
        ou = env["operating.unit"].create(
            {
                "name": "M49 Test Branch",
                "code": "M49TB%s" % next(_SEQ),
                "company_id": company.id,
                "partner_id": company.partner_id.id,
            }
        )
    return ou


@pytest.fixture
def m49(odoo_env):
    """Accounts, journal, a configured category and three users."""
    env = odoo_env
    company = env.company
    # a disposal sale is invoiced through M20, which issues a Mushak 6.3
    company.vat = "1234567890123"
    tag = next(_SEQ)

    def acc(code, name, account_type):
        return env["account.account"].create(
            {
                "code": f"M49{tag:02d}{code}",
                "name": f"M49 {name}",
                "account_type": account_type,
                "company_ids": [(6, 0, [company.id])],
            }
        )

    accounts = {
        "asset": acc("01", "Asset", "asset_fixed"),
        "accum": acc("02", "Accumulated depreciation", "asset_fixed"),
        "expense": acc("03", "Depreciation expense", "expense_depreciation"),
        "cwip": acc("04", "CWIP", "asset_non_current"),
        "surplus": acc("05", "Revaluation surplus", "equity"),
        "impair": acc("06", "Impairment loss", "expense"),
        "gain": acc("07", "Gain on disposal", "income_other"),
        "loss": acc("08", "Loss on disposal", "expense"),
        "proceeds": acc("09", "Disposal receivable", "asset_current"),
        "liability": acc("10", "Lease liability", "liability_non_current"),
        "interest": acc("11", "Interest expense", "expense"),
        "rent": acc("12", "Rent payable", "liability_current"),
    }
    journal = env["account.journal"].create(
        {
            "name": f"M49 Assets {tag}",
            "code": f"M4{tag % 100:02d}",
            "type": "general",
            "company_id": company.id,
        }
    )
    category = env["fix.asset.category"].create(
        {
            "company_id": company.id,
            "code": f"T{tag}",
            "name": f"Test Tools {tag}",
            "useful_life_months": 50,
            "tax_rate_code": "ITA3-PLANT",
            "journal_id": journal.id,
            "asset_account_id": accounts["asset"].id,
            "accumulated_account_id": accounts["accum"].id,
            "expense_account_id": accounts["expense"].id,
            "cwip_account_id": accounts["cwip"].id,
            "revaluation_surplus_account_id": accounts["surplus"].id,
            "impairment_account_id": accounts["impair"].id,
            "gain_account_id": accounts["gain"].id,
            "loss_account_id": accounts["loss"].id,
        }
    )
    users = {
        "accountant": make_user(env, "account.group_account_user"),
        "manager": make_user(env, "account.group_account_manager"),
        "manager2": make_user(env, "account.group_account_manager"),
        "reader": make_user(env, "account.group_account_readonly"),
    }
    return {
        "env": env,
        "company": company,
        "ou": fixture_ou(env),
        "accounts": accounts,
        "journal": journal,
        "category": category,
        "users": users,
    }


def balance(env, account):
    """Posted balance (debit - credit) of an account."""
    lines = env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("debit")) - sum(lines.mapped("credit")), 2)
