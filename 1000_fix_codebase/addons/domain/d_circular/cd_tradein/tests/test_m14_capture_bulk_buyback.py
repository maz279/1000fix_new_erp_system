# M14 sub-module capture audit (2026-11-13).
#
# Three M14 sub-module pages offered no relevant capture:
# - Destruction Gate had no button: nothing let a person attach the M06
#   certificate the gate checks;
# - Resale had no button: nothing let a person prepare the listing
#   (channel, price, merchant) before Resale Ready stocks and lists the unit;
# - Bulk Buy-Back offered the single-unit intake: there was no lot, no
#   declared asset list and nothing to reconcile (FR-TRF-009, BRU-TRF-23).
#
# Run as NON-ADMIN users through the real /p03/model/write and
# /p03/model/action endpoints; the odoo_env fixture rolls everything back.
# ruff: noqa: F811 - `m` is the shared M14 fixture, taken as each test's argument
import types

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.addons.cd_tradein.tests.test_a05_m14_controls import (  # noqa: F401 - m is a fixture
    _MA,
    _MW,
    TRD,
    accepted,
    approved,
    cert,
    device,
    graded,
    m,
    p03_action,
    p03_write,
    paying,
    refused,
)
from odoo.exceptions import UserError

BBK = "fix.bulk.buyback"


def _lot_write(x, values, rows=(), record_id=None, user=None):
    """/p03/model/write with the declared-asset grid, as the form posts it."""
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return _MW(
        g.P03GenericApiController(),
        model=BBK,
        record_id=record_id,
        values=values,
        lines={"field": "asset_ids", "rows": [{"values": r} for r in rows], "removed": []},
    )


def _client(x):
    return x.env["res.partner"].create({"name": "A05 M14 Corporate Client", "is_company": True})


def _lot(x, serials, **vals):
    vals.setdefault("partner_id", _client(x).id)
    # A05 ERP M14-23: the lot's intakes are taken in at its operating unit
    vals.setdefault("operating_unit_id", x.ou.id)
    res = _lot_write(x, vals, [{"serial_number": s} for s in serials])
    assert "error" not in res, res
    return x.env[BBK].browse(res["id"]).with_user(x.clerk)


# ---------------------------------------------------------------- bulk buy-back
def test_a_lot_is_captured_with_its_declared_assets_from_the_form(m):
    lot = _lot(m, ["sn-0001 ", "SN-0002"], contract_ref="PO-77")
    assert lot.state == "draft" and lot.name.startswith("BBK/")
    # identifiers are normalised so the reconciliation matches the register
    assert lot.asset_ids.mapped("serial_number") == ["SN-0001", "SN-0002"]
    assert lot.declared_asset_count == 2 and lot.pending_count == 2


def test_receiving_opens_one_trade_in_per_declared_asset(m):
    dev = device(m)
    lot = _lot(m, [dev.imei_1, "UNREGISTERED-9"])
    res = p03_action(m, BBK, lot, "action_open_intakes")
    assert res.get("success"), res
    assert lot.state == "received" and lot.received_by_id == m.clerk
    intakes = lot.asset_ids.mapped("tradein_id")
    assert len(intakes) == 2
    assert set(intakes.mapped("customer_id")) == {lot.partner_id}
    assert set(intakes.mapped("state")) == {"draft"}
    # the registered device is linked by its IMEI; the unknown one is not guessed
    by_serial = {a.serial_number: a.tradein_id for a in lot.asset_ids}
    assert by_serial[dev.imei_1].device_id == dev
    assert not by_serial["UNREGISTERED-9"].device_id
    # A05 ERP M14-17: an opened intake is not reconciled until the unit is
    # collected and its wipe certified
    assert lot.opened_count == 2 and lot.matched_count == 0 and lot.pending_count == 0


def test_an_asset_declared_after_receipt_gets_its_intake_on_the_next_run(m):
    lot = _lot(m, ["LATE-1"])
    lot.action_open_intakes()
    res = _lot_write(m, {}, [{"serial_number": "LATE-2"}], record_id=lot.id)
    assert "error" not in res, res
    assert lot.pending_count == 1
    lot.action_open_intakes()
    assert lot.pending_count == 0 and len(lot.asset_ids.mapped("tradein_id")) == 2


def test_the_lot_closes_only_when_every_asset_is_reconciled(m):
    lot = _lot(m, ["CL-1", "CL-2"])
    lot.action_open_intakes()
    second = lot.asset_ids.filtered(lambda a: a.serial_number == "CL-2")
    # the client declined the offer on CL-2: the asset is no longer reconciled
    second.tradein_id.action_reject(reason="client kept the unit")
    assert second.status == "pending" and lot.pending_count == 1
    res = p03_action(m, BBK, lot, "action_close")
    assert not res.get("success") and "not reconciled" in str(res), res
    refused(lot.action_close, "not reconciled")
    second.write({"exception_reason": "Retained by the client (declined the offer)"})
    # CL-1's intake is open but not collected and wipe-certified (M14-17)
    refused(lot.action_close, "wipe-certified")
    first = lot.asset_ids - second
    first.write({"exception_reason": "Not delivered with the lot"})
    assert second.status == "exception"
    assert second.exception_by_id == m.clerk and second.exception_at
    res = p03_action(m, BBK, lot, "action_close")
    assert res.get("success"), res
    assert lot.state == "closed" and lot.closed_by_id == m.clerk


def test_a_closed_lot_and_its_asset_list_are_frozen(m):
    lot = _lot(m, ["FZ-1"])
    lot.action_open_intakes()
    lot.asset_ids.write({"exception_reason": "Not delivered with the lot"})
    lot.action_close()
    refused(lambda: lot.write({"contract_ref": "changed"}), "closed")
    refused(
        lambda: m.env["fix.bulk.buyback.asset"]
        .with_user(m.clerk)
        .create({"buyback_id": lot.id, "serial_number": "FZ-2"}),
        "closed",
    )
    refused(lambda: lot.asset_ids.write({"exception_reason": "x"}), "closed")
    refused(lambda: lot.unlink(), "not deleted")


def test_received_lot_keeps_its_client_and_pricing(m):
    lot = _lot(m, ["RC-1"], lot_price_basis="lot", lot_price=50000)
    lot.action_open_intakes()
    refused(lambda: lot.write({"partner_id": _client(m).id}), "can no longer change")
    refused(lambda: lot.write({"lot_price": 1.0}), "can no longer change")
    res = _lot_write(m, {"lot_price": 1.0}, record_id=lot.id)
    assert "error" in res


def test_lot_pricing_needs_the_agreed_price(m):
    lot = _lot(m, ["LP-1"], lot_price_basis="lot")
    refused(lambda: lot.action_open_intakes(), "agreed lot price")


def test_the_reconciliation_link_is_never_typed(m):
    lot = _lot(m, ["GD-1"])
    other = (
        m.env[TRD]
        .with_user(m.clerk)
        .create({"customer_id": lot.partner_id.id, "operating_unit_id": m.ou.id})
    )
    asset = lot.asset_ids
    refused(lambda: asset.write({"tradein_id": other.id}), "changes only through")
    refused(
        lambda: m.env["fix.bulk.buyback.asset"]
        .with_user(m.clerk)
        .create({"buyback_id": lot.id, "serial_number": "GD-2", "tradein_id": other.id}),
        "changes only through",
    )
    # nor through the form grid
    res = _lot_write(m, {}, [{"serial_number": "GD-3", "tradein_id": other.id}], record_id=lot.id)
    assert "error" in res
    lot.action_open_intakes()
    refused(lambda: asset.write({"serial_number": "OTHER"}), "no longer changes")
    refused(lambda: asset.unlink(), "reconciliation evidence")
    refused(lambda: lot.write({"state": "closed"}), "changes only through")


def test_an_asset_is_declared_once_per_lot(m):
    res = _lot_write(
        m, {"partner_id": _client(m).id}, [{"serial_number": "DUP-1"}, {"serial_number": "dup-1"}]
    )
    assert "error" in res


# ------------------------------------------------------- destruction gate page
def test_destruction_gate_capture_attaches_the_certificate_then_the_gate_runs(m):
    rec = accepted(m)
    rec.action_collect()
    certificate = cert(m, rec.device_id)
    res = p03_write(m, TRD, rec.id, {"wipe_certificate_id": certificate.id})
    assert "error" not in res, res
    res = p03_action(m, TRD, rec, "action_wipe")
    assert res.get("success"), res
    assert rec.state == "wiped" and rec.wipe_certificate_id == certificate
    # once through the gate the certificate is frozen on the unit
    res = p03_write(m, TRD, rec.id, {"wipe_certificate_id": cert(m, rec.device_id).id})
    assert "error" in res


def test_the_gate_refuses_an_unverified_or_foreign_certificate(m):
    rec = accepted(m)
    rec.action_collect()
    for bad in (cert(m, rec.device_id, verified=False), cert(m, device(m))):
        res = p03_write(m, TRD, rec.id, {"wipe_certificate_id": bad.id})
        assert "error" not in res, res
        res = p03_action(m, TRD, rec, "action_wipe")
        assert not res.get("success") and rec.state == "collected", res


# ------------------------------------------------------------------ resale page
def test_resale_capture_prepares_the_listing_then_resale_ready_stocks_it(m):
    rec = paying(m)
    approved(m, rec)
    rec.action_pay()  # A05 ERP D3: bought in (on the ledger) before it is stocked
    graded(m, rec)
    res = p03_write(m, TRD, rec.id, {"resale_channel": "store", "resale_value": 31000.0})
    assert "error" not in res, res
    # A05 ERP D6: the price is approved by a pricing manager who did not propose it
    res = p03_action(m, TRD, rec, "action_resale_ready")
    assert not res.get("success") and "listing price" in str(res), res
    assert p03_action(m, TRD, rec, "action_request_listing_price").get("success")
    assert p03_action(m, TRD, rec, "action_approve_listing_price", user=m.pricer).get("success")
    res = p03_action(m, TRD, rec, "action_resale_ready")
    assert res.get("success"), res
    assert rec.state == "resale_ready"
    assert rec.graded_stock_id.resale_price == pytest.approx(31000.0)
    # the listing freezes once the unit is stocked
    res = p03_write(m, TRD, rec.id, {"resale_value": 1.0})
    assert "error" in res
    with pytest.raises(UserError):
        rec.write({"resale_channel": "direct"})
