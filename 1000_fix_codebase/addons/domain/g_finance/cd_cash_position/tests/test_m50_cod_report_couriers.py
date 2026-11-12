# cd_cash_position — M50 COD report covers courier remittances (G10 follow-up).
#
# treasury_reports.cod_report listed in-house rider settlements only. Since
# G10 (12 Nov 2026) third-party couriers' COD cash is cleared by
# fix.courier.remittance batches (Dr bank net + Dr courier charges / Cr COD
# clearing gross), so the report showed none of it, and a courier's delivered
# but unremitted COD was invisible. The report now lists both channels with
# per-channel totals, and proves gross collected, charges and net banked
# against the COD clearing movements the entries actually made.
#
# The arrangement runs as superuser; the workflow as the real roles; the
# report as an accountant.
# ruff: noqa: F811  (the M50 / G10 fixtures are imported and used as parameters)
from __future__ import annotations

import pytest
from odoo.addons.cd_cash_position.models import treasury_reports
from odoo.addons.cd_cash_position.tests.test_a08_m50_controls import (  # noqa: F401
    _cod,
    _cod_orders,
    c,
)
from odoo.addons.cd_cash_position.tests.test_g10_courier_remittance import (  # noqa: F401
    _courier_orders,
    _remittance,
    cr,
)

pytestmark = [pytest.mark.financial]


def _report(c):
    env = c.env(user=c.acct.id)
    return treasury_reports.cod_report(env, date_from=c.today, date_to=c.today)


def _row(out, ref):
    rows = [r for r in out["rows"] if r.get("ref") == ref]
    assert len(rows) == 1, "%s appears %d times in the COD report" % (ref, len(rows))
    return rows[0]


def _settled_rider(c, amounts, remitted=None):
    _cod_orders(c, amounts)
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    s.with_user(c.acct).write({"remitted_amount": sum(amounts) if remitted is None else remitted})
    s.with_user(c.acct).action_submit()
    if s.remitted_amount + 0.005 < s.expected_amount:
        s.with_user(c.mgr2).action_approve_shortage(note="Rider short, recovery requested")
    s.with_user(c.mgr).action_settle()
    return s


def _settled_courier(c, courier, amounts, delivery=0.0, cod=0.0):
    _courier_orders(c, courier, amounts)
    r = _remittance(
        c,
        courier=courier,
        delivery_charges=delivery,
        cod_charges=cod,
        net_amount=sum(amounts) - delivery - cod,
    )
    r.with_user(c.acct).action_load_orders()
    r.with_user(c.acct).action_submit()
    r.with_user(c.mgr).action_settle()
    return r


def test_courier_remittances_are_in_the_cod_report(cr):
    c = cr
    r = _settled_courier(c, c.pathao, [3000.0, 2000.0], delivery=120.0, cod=50.0)
    row = _row(_report(c), r.name)
    assert c.pathao.name in row["channel"]
    assert (row["orders"], row["gross"], row["charges"], row["net"]) == (2, 5000.0, 170.0, 4830.0)
    assert row["variance"] == 0.0 and row["state"] == "Settled"
    # what the entry itself credited to COD clearing
    assert row["gl_cleared"] == 5000.0 and row["tie"] == "Ties"


def test_rider_settlements_keep_their_rows_beside_the_couriers(cr):
    c = cr
    s = _settled_rider(c, [4000.0, 1000.0], remitted=4900.0)  # 100 short
    row = _row(_report(c), s.name)
    assert c.rider.name in row["channel"]
    assert (row["gross"], row["charges"], row["net"], row["variance"]) == (
        5000.0,
        0.0,
        4900.0,
        -100.0,
    )
    assert row["gl_cleared"] == 5000.0 and row["tie"] == "Ties"


def test_per_channel_totals_and_the_grand_total(cr):
    c = cr
    _settled_rider(c, [4000.0])
    _settled_courier(c, c.pathao, [3000.0], delivery=100.0)
    _settled_courier(c, c.pathao, [2000.0], cod=40.0)
    _settled_courier(c, c.redx, [1500.0], delivery=60.0)
    out = _report(c)
    by_channel = {t["channel"]: t for t in out["channel_totals"]}
    pathao = next(t for k, t in by_channel.items() if c.pathao.name in k)
    redx = next(t for k, t in by_channel.items() if c.redx.name in k)
    riders = next(t for k, t in by_channel.items() if "Rider" in k)
    assert (pathao["orders"], pathao["gross"], pathao["charges"], pathao["net"]) == (
        2,
        5000.0,
        140.0,
        4860.0,
    )
    assert (redx["gross"], redx["charges"], redx["net"]) == (1500.0, 60.0, 1440.0)
    assert (riders["gross"], riders["net"]) == (4000.0, 4000.0)
    # the subtotal rows are shown, but the grand total counts each batch once
    t = out["totals"]
    assert (t["orders"], t["gross"], t["charges"], t["net"]) == (4, 10500.0, 200.0, 10300.0)


def test_gross_charges_and_net_tie_to_cod_clearing_movements(cr):
    c = cr
    _settled_rider(c, [4000.0], remitted=3950.0)
    _settled_courier(c, c.pathao, [3000.0, 2000.0], delivery=120.0, cod=50.0)
    tie = _report(c)["tie"]
    # COD clearing credited by the period's entries = gross settled, exactly
    assert tie["gross_settled"] == 9000.0
    assert tie["gl_cod_clearing_credits"] == 9000.0
    assert tie["gross_difference"] == 0.0
    # the net banked and the charges are what the entries debited
    assert (tie["net_banked"], tie["gl_net_banked"]) == (8780.0, 8780.0)
    assert (tie["charges"], tie["gl_charges"]) == (170.0, 170.0)


def test_a_manual_credit_to_cod_clearing_shows_as_unexplained(cr):
    """A COD clearing credit no settlement or remittance made breaks the tie,
    and the report says by how much."""
    c = cr
    _settled_courier(c, c.pathao, [3000.0])
    from odoo.addons.cd_cash_position.models.treasury_common import post_treasury_move

    post_treasury_move(
        c.env,
        c.company,
        c.today,
        "Manual COD clearing write-back",
        [
            (c.bank_acc, "manual", 250.0, 0.0, None),
            (c.acc["cod_clearing"], "manual", 0.0, 250.0, None),
        ],
    )
    tie = _report(c)["tie"]
    assert tie["gl_cod_clearing_credits"] == 3250.0
    assert tie["gross_difference"] == -250.0
    assert any("250.00" in n for n in _report(c)["notes"])


def test_couriers_delivered_but_unremitted_cod_is_listed(cr):
    c = cr
    held = _courier_orders(c, c.redx, [1800.0, 700.0])
    _settled_courier(c, c.pathao, [3000.0])
    out = _report(c)
    open_rows = [
        r for r in out["rows"] if r["state"] == "Unsettled" and c.redx.name in (r["channel"] or "")
    ]
    assert len(open_rows) == 1
    assert (open_rows[0]["orders"], open_rows[0]["gross"]) == (len(held), 2500.0)
    # an order in a live courier remittance is not also a rider's open COD
    rider_orders = _cod_orders(c, [900.0])
    rider_orders.carrier_consignment_id.sudo().write({"courier_partner_id": c.pathao.id})
    r = _remittance(c, net_amount=900.0)
    r.with_user(c.acct).action_load_orders()
    out = _report(c)
    assert not [
        x for x in out["rows"] if x["state"] == "Unsettled" and c.rider.name in (x["channel"] or "")
    ]
