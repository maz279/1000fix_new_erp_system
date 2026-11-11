# An unknown cost is not a small value (2026-11-10 accuracy audit).
#
# Write-offs and transfers are waved through below a BDT threshold, and a
# bucket with no cost recorded is worth BDT 0.00, so stock of unknown value
# (every on-hand row at cut-over) left the two-person rule entirely. Run as
# NON-ADMIN users: a Storekeeper acts, an Inventory Controller approves.
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
WRITEOFF = "cd_inventory.writeoff_approval_threshold"
TRANSFER = "cd_inventory.transfer_approval_threshold"


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _set(inv, key, value):
    inv.env["ir.config_parameter"].sudo().set_param(key, str(value))


def _uncosted_part(inv, qty=50.0):
    """A part on hand with no cost on the part or the bucket."""
    part = inv.env["fix.spare.part"].create(
        {"name": "A06 Uncosted", "part_number": "A6Z-" + inv.tag}
    )
    inv.stock(part, inv.central, qty, 0.0)
    assert inv.bucket(part, inv.central).unit_cost == 0.0
    return part


def _transfer(inv, user, *lines):
    return (
        inv.env["fix.stock.transfer"]
        .with_user(user)
        .create(
            {
                "from_location_id": inv.central.id,
                "to_location_id": inv.hub.id,
                "operating_unit_id": inv.ou.id,
                "line_ids": [(0, 0, {"part_id": part.id, "qty": qty}) for part, qty in lines],
            }
        )
    )


# ============================================================ scrap / write-off
@pytest.mark.parametrize("threshold", [0, 1000])
def test_uncosted_stock_is_never_scrapped_without_approval(inv, threshold):
    _set(inv, WRITEOFF, threshold)
    part = _uncosted_part(inv)
    q = inv.quarantine(inv.keeper, qty=50.0, part=part)
    assert q.sudo().unit_cost == 0.0
    refused(inv, lambda: q.with_user(inv.keeper).action_scrap(), "no unit cost")
    assert q.state == "quarantined"
    assert inv.qty(part, inv.central, status="quarantine") == 50.0
    # the proper path: a second person, never the storekeeper himself
    q.with_user(inv.keeper).action_request_scrap()
    refused(inv, lambda: q.with_user(inv.keeper).action_approve_scrap())
    q.with_user(inv.controller).action_approve_scrap()
    assert q.state == "scrapped" and q.approved_by_id == inv.controller
    assert inv.qty(part, inv.central, status="quarantine") == 0.0


def test_a_known_small_value_still_scraps_within_the_threshold(inv):
    _set(inv, WRITEOFF, 1000)
    q = inv.quarantine(inv.keeper, qty=2.0)  # 2 x BDT 500 = the threshold exactly
    q.with_user(inv.keeper).action_scrap()
    assert q.state == "scrapped"


def test_a_known_value_with_no_threshold_configured_needs_approval(inv):
    _set(inv, WRITEOFF, 0)
    q = inv.quarantine(inv.keeper, qty=1.0)
    refused(inv, lambda: q.with_user(inv.keeper).action_scrap(), "approval threshold")
    assert q.state == "quarantined"


# ==================================================================== transfers
def test_an_uncosted_transfer_is_never_auto_approved(inv):
    _set(inv, TRANSFER, 1000)
    part = _uncosted_part(inv)
    trf = _transfer(inv, inv.keeper, (part, 50.0))
    trf.with_user(inv.keeper).action_submit()
    assert trf.state == "submitted" and not trf.approval_note
    refused(inv, lambda: trf.with_user(inv.keeper).action_dispatch(), "approved")
    refused(inv, lambda: trf.with_user(inv.keeper).action_approve())
    trf.with_user(inv.controller).action_approve()
    trf.with_user(inv.keeper).action_dispatch()
    assert trf.state == "dispatched"


def test_one_uncosted_line_holds_the_whole_transfer_for_approval(inv):
    _set(inv, TRANSFER, 1000)
    part = _uncosted_part(inv)
    # BDT 500 of costed stock is inside the threshold; the 50 uncosted pieces
    # beside it are worth an unknown amount, not nothing
    trf = _transfer(inv, inv.keeper, (inv.part, 1.0), (part, 50.0))
    trf.with_user(inv.keeper).action_submit()
    assert trf.state == "submitted"


def test_a_known_small_transfer_is_still_auto_approved(inv):
    _set(inv, TRANSFER, 1000)
    trf = _transfer(inv, inv.keeper, (inv.part, 2.0))  # BDT 1,000 exactly
    trf.with_user(inv.keeper).action_submit()
    assert trf.state == "approved" and "auto-approved" in trf.approval_note
    over = _transfer(inv, inv.keeper, (inv.part, 3.0))
    over.with_user(inv.keeper).action_submit()
    assert over.state == "submitted"


def test_with_no_transfer_threshold_every_transfer_needs_approval(inv):
    _set(inv, TRANSFER, 0)
    part = _uncosted_part(inv)
    for lines in (((inv.part, 1.0),), ((part, 1.0),)):
        trf = _transfer(inv, inv.keeper, *lines)
        trf.with_user(inv.keeper).action_submit()
        assert trf.state == "submitted"
