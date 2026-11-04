"""cd_inventory_ops behaviour (live ORM, rolled back): the M15 workspace ledger —
on-hand buckets, goods receipt inspection gate, transfers, counts, quarantine,
RTV, van reconciliation and the reorder trigger.

A06 remediation: these are the PROPER paths, run as trusted code (the test
superuser) through the same actions a user runs. The flows follow the
remediated model: a transfer is submitted and approved before it moves, a
count is blind and a variance goes through recount and approval, a
write-off above the threshold is approved, an RTV ships with its RMA, and a
van reconciliation takes its expected quantity from the van ledger. (The
pre-remediation versions dispatched a draft transfer, typed a count's
expected quantity and scrapped/shipped with no approval: they asserted the
defects the A06 audit reported.)"""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    big = env["fix.stock.location"].create({"name": "Ops Central", "code": f"OPC-{TAG}"})
    hub = env["fix.stock.location"].create({"name": "Ops Hub", "code": f"OPH-{TAG}"})
    technician = env["hr.employee"].create({"name": f"Ops Tech {TAG}"})
    van = env["fix.stock.location"].create(
        {
            "name": "Ops Van",
            "code": f"OPV-{TAG}",
            "location_type": "van",
            "technician_id": technician.id,
        }
    )
    part = env["fix.spare.part"].create(
        {"name": "Ops Test Display", "part_number": f"OPS-{TAG}", "unit_cost": 500.0}
    )
    Onhand = env["fix.stock.onhand"]
    Onhand._apply(part, big, "owned", 8.0, 500.0)
    Onhand._apply(part, hub, "owned", 2.0, 500.0)
    supplier = env["res.partner"].create({"name": f"Ops Supplier {TAG}"})
    return {"env": env, "big": big, "hub": hub, "van": van, "part": part, "supplier": supplier}


def _row(ctx, location, status="unrestricted"):
    return ctx["env"]["fix.stock.onhand"]._bucket(ctx["part"], location, "owned", status)


def _receipt(ctx, accepted=4.0, received=5.0):
    return ctx["env"]["fix.stock.receipt"].create(
        {
            "partner_id": ctx["supplier"].id,
            "location_id": ctx["big"].id,
            "received_on": date(2026, 10, 28),
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": ctx["part"].id,
                        "qty_received": received,
                        "qty_accepted": accepted,
                        "unit_cost": 500.0,
                        "line_no": f"LOT-{TAG}",
                    },
                )
            ],
        }
    )


def test_onhand_unique_and_reserved_bound(ctx):
    env, part, big = ctx["env"], ctx["part"], ctx["big"]
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.stock.onhand"].create(
            {
                "part_id": part.id,
                "location_id": big.id,
                "ownership_class": "owned",
                "qty": 1.0,
            }
        )
    row = _row(ctx, big)
    with pytest.raises(IntegrityError), env.cr.savepoint():
        row.reserved = 9.0
        row.flush_recordset()


def test_receipt_inspection_gate_and_post(ctx):
    env, part = ctx["env"], ctx["part"]
    receipt = _receipt(ctx)
    assert receipt.name.startswith("GRN/")
    assert receipt.state == "draft"
    receipt.action_inspect()
    assert receipt.state == "inspected"
    before = part.qty_available
    receipt.action_post()
    assert receipt.state == "posted"
    # 4 accepted into available stock, the rejected 1 held in quarantine
    assert part.qty_available == pytest.approx(before + 5.0)
    assert _row(ctx, ctx["big"]).qty == pytest.approx(12.0)
    assert _row(ctx, ctx["big"], "quarantine").qty == pytest.approx(1.0)
    lot = env["fix.stock.lot"].search([("name", "=", f"LOT-{TAG}")], limit=1)
    assert lot and lot.qty == pytest.approx(4.0)
    with pytest.raises(UserError, match="inspected"), env.cr.savepoint():
        receipt.action_post()


def test_receipt_refuses_zero_accepted_line(ctx):
    env = ctx["env"]
    receipt = _receipt(ctx, accepted=0.0)
    with pytest.raises(UserError, match="accepted quantity"), env.cr.savepoint():
        receipt.action_inspect()


def test_transfer_moves_buckets_and_needs_lines(ctx):
    env, part = ctx["env"], ctx["part"]
    transfer = env["fix.stock.transfer"].create(
        {"from_location_id": ctx["big"].id, "to_location_id": ctx["hub"].id}
    )
    assert transfer.name.startswith("TRF/")
    with pytest.raises(UserError, match="at least one line"), env.cr.savepoint():
        transfer.action_submit()
    env["fix.stock.transfer.line"].create(
        {"transfer_id": transfer.id, "part_id": part.id, "qty": 3.0}
    )
    transfer.action_submit()
    transfer.action_approve()
    transfer.action_dispatch()
    assert _row(ctx, ctx["big"], "in_transit").qty == pytest.approx(3.0)
    transfer.action_receive()
    assert transfer.state == "received"
    assert _row(ctx, ctx["big"]).qty == pytest.approx(5.0)
    assert _row(ctx, ctx["hub"]).qty == pytest.approx(5.0)
    assert part.qty_available == pytest.approx(10.0)


def test_transfer_refuses_overdraw(ctx):
    env, part = ctx["env"], ctx["part"]
    transfer = env["fix.stock.transfer"].create(
        {
            "from_location_id": ctx["hub"].id,
            "to_location_id": ctx["big"].id,
            "line_ids": [(0, 0, {"part_id": part.id, "qty": 9.0})],
        }
    )
    transfer.action_submit()
    transfer.action_approve()
    with pytest.raises(UserError, match="insufficient"), env.cr.savepoint():
        transfer.action_dispatch()


def test_count_posts_variance_after_recount_and_approval(ctx):
    env, part = ctx["env"], ctx["part"]
    count = env["fix.stock.count"].create(
        {
            "location_id": ctx["hub"].id,
            "count_type": "cycle",
            "counted_on": date(2026, 10, 28),
            "line_ids": [(0, 0, {"part_id": part.id, "counted_qty": 1.0})],
        }
    )
    assert count.name.startswith("CNT/")
    assert count.line_ids.expected_qty == pytest.approx(2.0)  # the ledger's, not typed
    count.action_submit()
    assert count.state == "recount"
    count.line_ids.recount_qty = 1.0
    count.reason_code = "damage"
    count.action_submit()
    assert count.state == "to_approve"
    count.action_approve()
    assert count.state == "posted"
    assert _row(ctx, ctx["hub"]).qty == pytest.approx(1.0)
    assert part.qty_available == pytest.approx(9.0)


def test_quarantine_scrap_deducts_after_approval(ctx):
    env, part = ctx["env"], ctx["part"]
    scrap = env["fix.stock.quarantine"].create(
        {
            "part_id": part.id,
            "location_id": ctx["big"].id,
            "qty": 2.0,
            "reason": "damaged",
            "quarantined_on": date(2026, 10, 28),
        }
    )
    assert scrap.name.startswith("QRN/")
    assert _row(ctx, ctx["big"]).qty == pytest.approx(6.0)
    with pytest.raises(UserError, match="approval threshold"), env.cr.savepoint():
        scrap.action_scrap()
    scrap.action_request_scrap()
    scrap.action_approve_scrap()
    assert scrap.state == "scrapped"
    assert part.qty_available == pytest.approx(8.0)
    with pytest.raises(UserError, match="quarantined"), env.cr.savepoint():
        scrap.action_scrap()


def test_rtv_approve_then_ship(ctx):
    env, part = ctx["env"], ctx["part"]
    rtv = env["fix.stock.rtv"].create(
        {
            "partner_id": ctx["supplier"].id,
            "part_id": part.id,
            "location_id": ctx["big"].id,
            "qty": 1.0,
            "reason": "doa",
            "requested_on": date(2026, 10, 28),
        }
    )
    with pytest.raises(UserError, match="approved"), env.cr.savepoint():
        rtv.action_ship()
    rtv.action_approve()
    with pytest.raises(UserError, match="RMA"), env.cr.savepoint():
        rtv.action_ship()
    rtv.rtv_ref = "RMA-001"
    rtv.action_ship()
    assert rtv.state == "shipped"
    assert part.qty_available == pytest.approx(9.0)


def test_van_reconciliation_flags_discrepancy(ctx):
    env = ctx["env"]
    env["fix.stock.onhand"]._apply(ctx["part"], ctx["van"], "van", 10.0, 500.0)
    recon = env["fix.stock.van.recon"].create(
        {
            "location_id": ctx["van"].id,
            "recon_date": date(2026, 10, 28),
            "counted_qty": 9,
        }
    )
    assert recon.name.startswith("VRC/")
    assert recon.expected_qty == pytest.approx(10.0)
    recon.action_confirm()
    assert recon.state == "discrepancy"
    assert recon.variance == pytest.approx(-1.0)
