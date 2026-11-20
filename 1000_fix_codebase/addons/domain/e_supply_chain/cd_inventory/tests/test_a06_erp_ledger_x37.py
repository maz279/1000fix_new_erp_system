# A06 ERP X37 (20 Nov 2026): counter and storefront sales posted revenue and
# VAT at once, and their parts cost only at the month-end cut-over. With the
# stock subledger posting in real time (D1), the stock leg of each sale posts
# its own parts cost (Dr 600002 / Cr stock) at sale time, and the revenue
# entry carries no cost line: nothing is posted twice.
#
# The counter (cd_front_desk_finance) and storefront (cd_storefront_finance)
# bridges are not dependencies of cd_inventory: on a database without them
# these tests skip. They run on the fix_real copy, where both are installed.
# ruff: noqa: F811  (the bridges' fixtures are imported and used as parameters)
import pytest
from odoo import fields

try:  # the bridges' own worlds (cashier, shift, storefront operator...)
    from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
    from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import fin  # noqa: F401
    from odoo.addons.cd_storefront.tests.test_a04_c2_c13_storefront import w  # noqa: F401
    from odoo.addons.cd_storefront_finance.tests.test_storefront_books import sf  # noqa: F401
except ImportError:  # pragma: no cover - the bridges are not on this code base
    pytest.skip("counter / storefront bridges not present", allow_module_level=True)

D2 = {
    "100502": "asset_current",
    "100503": "asset_current",
    "600002": "expense_direct_cost",
    "500905": "expense",
    "300101": "equity",
}


def _realtime(env):
    """The company on real-time stock posting, with the D2 accounts it needs."""
    company = env.company
    Account = env["account.account"].sudo().with_company(company)
    for code, kind in D2.items():
        if not Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1):
            Account.create(
                {
                    "code": code,
                    "name": "X37 %s" % code,
                    "account_type": kind,
                    "company_ids": [(6, 0, company.ids)],
                }
            )
    Journal = env["account.journal"].sudo()
    if not Journal.search(
        [("company_id", "=", company.id), ("code", "=", "STJ"), ("type", "=", "general")], limit=1
    ):
        Journal.create(
            {"name": "Stock", "code": "STJ", "type": "general", "company_id": company.id}
        )
    company.sudo()._fix_set_realtime(fields.Datetime.now())


def _rows(env, ref):
    return (
        env["fix.inventory.valuation.suspense"]
        .sudo()
        .search([("source_ref", "like", ref)], order="id")
    )


def _codes(move):
    out = {}
    for line in move.line_ids:
        out[line.account_id.code] = round(out.get(line.account_id.code, 0.0) + line.balance, 2)
    return out


def _cogs_moves(env, ref):
    env.flush_all()
    return (
        env["account.move.line"]
        .sudo()
        .search(
            [
                ("account_id.code", "=", "600002"),
                ("parent_state", "=", "posted"),
                ("move_id.ref", "like", ref),
            ]
        )
        .move_id
    )


@pytest.fixture
def counter(odoo_env, request):
    if "fix.counter.sale" not in odoo_env:
        pytest.skip("cd_front_desk_finance is not installed on this database")
    m = request.getfixturevalue("fin")
    _realtime(m.env)
    return m


@pytest.fixture
def store(odoo_env, request):
    if "fix.storefront.order" not in odoo_env or not hasattr(
        odoo_env["fix.storefront.order"], "_cron_retry_storefront_postings"
    ):
        pytest.skip("cd_storefront_finance is not installed on this database")
    s = request.getfixturevalue("sf")
    _realtime(s.env)
    return s


def test_x37_counter_sale_posts_its_parts_cost_at_sale_time_once(counter):
    m = counter
    env = m.env
    sale = m.confirmed(1150.0, "cash", shift=m.shift())
    (row,) = _rows(env, sale.name)
    assert (row.entry_type, row.status) == ("counter_sale", "posted")
    cogs = row.move_id
    assert cogs.state == "posted" and cogs.date == row.posting_date
    assert _codes(cogs) == {"600002": 600.0, "100502": -600.0}
    # the revenue entry carries no cost and no stock line: nothing doubles
    revenue = sale.sudo().gl_move_id
    assert revenue and revenue != cogs
    assert not {"600002", "100502"} & set(_codes(revenue))
    assert _cogs_moves(env, sale.name) == cogs
    # a retry posts nothing more
    sale.action_retry_posting()
    assert len(_rows(env, sale.name)) == 1
    # the refund reverses the cost, once
    m.refund(sale)
    back = _rows(env, sale.name) - row
    assert len(back) == 1 and back.status == "posted"
    assert _codes(back.move_id) == {"100502": 600.0, "600002": -600.0}


def test_x37_storefront_dispatch_posts_its_parts_cost_once(store):
    s = store
    env = s.env
    order, _receipt = s.paid(2)
    order.with_user(s.operator).action_dispatch()
    (row,) = _rows(env, order.name)
    assert (row.entry_type, row.status) == ("storefront_sale", "posted")
    assert _codes(row.move_id) == {"600002": 3000.0, "100502": -3000.0}
    order.with_user(s.operator).action_deliver()
    order.with_user(s.operator).action_retry_posting()
    env["fix.storefront.order"]._cron_retry_storefront_postings()
    assert len(_rows(env, order.name)) == 1
    invoice_moves = (
        order.sudo().ar_invoice_id.mapped("move_id")
        if "move_id" in order.sudo().ar_invoice_id._fields
        else env["account.move"]
    )
    for move in invoice_moves:
        assert "600002" not in _codes(move)
