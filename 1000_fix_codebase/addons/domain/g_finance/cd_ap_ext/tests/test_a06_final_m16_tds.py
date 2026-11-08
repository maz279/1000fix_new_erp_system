# A06 final pass, M16-8: a line's TDS category came from the vendor's tax profile
# and fell back silently to service_general when the profile named none, so a
# supply of goods could withhold at a services rate with nobody having chosen it.
# The bill now says so until AP sets the right category or confirms the default.
# No rate is invented here: finance owns the rates.
from __future__ import annotations

import pytest
from odoo.exceptions import AccessError, UserError

pytestmark = [pytest.mark.financial]


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def t(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor = env["res.partner"].create({"name": "A06F TDS Vendor", "is_company": True})
    product = env["product.product"].create({"name": "A06F TDS Part"})
    ap = _user(env, "a06ftds_ap", ["account.group_account_user"])
    return {"env": env, "ou": ou, "vendor": vendor, "product": product, "ap": ap}


def _bill(t, ref="A06F-TDS-1", **line):
    vals = {
        "product_id": t["product"].id,
        "description": "Part",
        "quantity": 1,
        "unit_price": 1000,
    }
    vals.update(line)
    return (
        t["env"]["fix.vendor.invoice"]
        .with_user(t["ap"])
        .create(
            {
                "vendor_id": t["vendor"].id,
                "invoice_ref": ref,
                "bill_type": "non_po",
                "operating_unit_id": t["ou"].id,
                "line_ids": [(0, 0, vals)],
            }
        )
    )


def test_b13_a_defaulted_category_flags_the_bill(t):
    bill = _bill(t)
    assert bill.line_ids.tds_category == "service_general"
    assert bill.line_ids.tds_category_assumed and bill.tds_category_review


def test_b13_a_category_ap_chose_is_not_flagged(t):
    bill = _bill(t, tds_category="supply_of_goods")
    assert not bill.line_ids.tds_category_assumed and not bill.tds_category_review


def test_b13_the_profiles_category_is_not_flagged(t):
    t["env"]["fix.vendor.tax.profile"].create(
        {"partner_id": t["vendor"].id, "default_tds_category": "supply_of_goods"}
    )
    bill = _bill(t)
    assert bill.line_ids.tds_category == "supply_of_goods"
    assert not bill.tds_category_review


def test_b13_a_profile_code_that_is_no_category_is_flagged(t):
    t["env"]["fix.vendor.tax.profile"].create(
        {"partner_id": t["vendor"].id, "default_tds_category": "no_such_code"}
    )
    bill = _bill(t)
    assert bill.line_ids.tds_category == "service_general" and bill.tds_category_review


def test_b13_choosing_another_category_clears_the_flag_and_an_echo_does_not(t):
    bill = _bill(t)
    bill.line_ids.with_user(t["ap"]).write({"tds_category": "service_general"})
    assert bill.tds_category_review  # the form posts what it was shown
    bill.line_ids.with_user(t["ap"]).write({"tds_category": "supply_of_goods"})
    assert not bill.line_ids.tds_category_assumed and not bill.tds_category_review


def test_b13_ap_can_confirm_the_default_and_nobody_else_can(t):
    bill = _bill(t)
    clerk = _user(t["env"], "a06ftds_clerk")
    with pytest.raises((UserError, AccessError)):
        bill.with_user(clerk).action_confirm_tds_category()
    assert bill.tds_category_review
    bill.with_user(t["ap"]).action_confirm_tds_category()
    assert not bill.tds_category_review and bill.line_ids.tds_category == "service_general"
