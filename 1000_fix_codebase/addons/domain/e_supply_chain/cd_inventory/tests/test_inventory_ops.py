"""cd_inventory_ops behaviour (live ORM, rolled back): the M15 workspace ledger —
on-hand buckets, goods receipt inspection gate, transfers, counts, quarantine,
RTV, van reconciliation and the reorder trigger."""

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
        {
            "name": "Ops Test Display",
            "part_number": f"OPS-{TAG}",
            "unit_cost": 500.0,
            "qty_available": 10.0,
            "is_serialized": True,
        }
    )
    env["fix.stock.onhand"].create(
        {
            "part_id": part.id,
            "location_id": big.id,
            "ownership_class": "owned",
            "qty": 8.0,
            "unit_cost": 500.0,
        }
    )
    env["fix.stock.onhand"].create(
        {
            "part_id": part.id,
            "location_id": hub.id,
            "ownership_class": "owned",
            "qty": 2.0,
            "unit_cost": 500.0,
        }
    )
    supplier = env["res.partner"].create({"name": f"Ops Supplier {TAG}"})
    return {"env": env, "big": big, "hub": hub, "van": van, "part": part, "supplier": supplier}


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
    row = env["fix.stock.onhand"].search(
        [("part_id", "=", part.id), ("location_id", "=", big.id)], limit=1
    )
    with pytest.raises(IntegrityError), env.cr.savepoint():
        row.reserved = 9.0


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
    assert part.qty_available == pytest.approx(before + 4.0)
    row = env["fix.stock.onhand"].search(
        [("part_id", "=", part.id), ("location_id", "=", ctx["big"].id)], limit=1
    )
    assert row.qty == pytest.approx(12.0)
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
        transfer.action_dispatch()
    env["fix.stock.transfer.line"].create(
        {"transfer_id": transfer.id, "part_id": part.id, "qty": 3.0}
    )
    transfer.action_dispatch()
    transfer.action_receive()
    assert transfer.state == "received"
    big = env["fix.stock.onhand"].search(
        [("part_id", "=", part.id), ("location_id", "=", ctx["big"].id)], limit=1
    )
    hub = env["fix.stock.onhand"].search(
        [("part_id", "=", part.id), ("location_id", "=", ctx["hub"].id)], limit=1
    )
    assert big.qty == pytest.approx(5.0)
    assert hub.qty == pytest.approx(5.0)
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
    transfer.action_dispatch()
    with pytest.raises(UserError, match="insufficient"), env.cr.savepoint():
        transfer.action_receive()


def test_count_posts_variance(ctx):
    env, part = ctx["env"], ctx["part"]
    count = env["fix.stock.count"].create(
        {
            "location_id": ctx["hub"].id,
            "count_type": "cycle",
            "counted_on": date(2026, 10, 28),
            "line_ids": [(0, 0, {"part_id": part.id, "expected_qty": 2.0, "counted_qty": 1.0})],
        }
    )
    assert count.name.startswith("CNT/")
    count.action_post()
    assert count.state == "posted"
    row = env["fix.stock.onhand"].search(
        [("part_id", "=", part.id), ("location_id", "=", ctx["hub"].id)], limit=1
    )
    assert row.qty == pytest.approx(1.0)
    assert part.qty_available == pytest.approx(9.0)


def test_quarantine_scrap_deducts(ctx):
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
    scrap.action_scrap()
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
    rtv.action_ship()
    assert rtv.state == "shipped"
    assert part.qty_available == pytest.approx(9.0)


def test_van_reconciliation_flags_discrepancy(ctx):
    env = ctx["env"]
    recon = env["fix.stock.van.recon"].create(
        {
            "location_id": ctx["van"].id,
            "recon_date": date(2026, 10, 28),
            "expected_qty": 10,
            "counted_qty": 9,
        }
    )
    assert recon.name.startswith("VRC/")
    recon.action_confirm()
    assert recon.state == "discrepancy"
    assert recon.variance == pytest.approx(-1.0)
