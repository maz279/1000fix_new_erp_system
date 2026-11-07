"""A06 final pass B2 (M15-10): a part fitted on a field job leaves the M15 ledger.

Attacks and proper paths run as the assigned technician (NON-ADMIN), through the
same action the workspace and the offline sync use. Uses the A02 M02 fixture;
`odoo_env` rolls back.
"""

from odoo.exceptions import UserError

from . import test_a02_p0_m02 as p0

w = p0.w
refused = p0.refused


def _m15(w, tech, qty=3.0, cost=400.0, **part_vals):
    """A product mapped to an M15 part, and a van in the technician's custody."""
    env = w.env
    product = env["product.product"].create(
        {"name": "A06F field part", "default_code": "A6FP-%s" % tech.id, "standard_price": 1.0}
    )
    part = env["fix.spare.part"].create(
        {
            "name": "A06F field part",
            "part_number": "A6FP-%s" % tech.id,
            "unit_cost": cost,
            "product_id": product.id,
            **part_vals,
        }
    )
    van = env["fix.stock.location"].create(
        {
            "name": "A06F Van",
            "code": "A6FV-%s" % tech.id,
            "location_type": "van",
            "technician_id": tech.id,
            "operating_unit_id": w.ou.id,
        }
    )
    env["fix.stock.onhand"]._apply(part, van, "van", qty, cost)
    return product, part, van


def _van_qty(w, part, van):
    w.env.invalidate_all()
    row = w.env["fix.stock.onhand"]._bucket(part, van, "van")
    return row.qty if row else 0.0


def _line(w, rec, product, qty=1.0, **vals):
    return w.env["fix.field.order.part"].create(
        {"field_order_id": rec.id, "product_id": product.id, "quantity": qty, **vals}
    )


def test_b2_a_fitted_mapped_part_leaves_the_technicians_van(w):
    product, part, van = _m15(w, w.ea)
    rec = w.fo("in_progress", w.ea)
    line = _line(w, rec, product, qty=2.0)
    line.with_user(w.ua).action_consume()
    issue = line.m15_consumption_id
    assert issue.state == "consumed"
    assert (issue.product_id, issue.location_id, issue.quantity) == (part, van, 2.0)
    assert (issue.job_model, issue.job_res_id) == ("fix.field.order", rec.id)
    assert issue.ownership_class == "van"
    assert _van_qty(w, part, van) == 1.0


def test_b2_not_enough_van_stock_refuses_the_fit(w):
    product, part, van = _m15(w, w.ea, qty=1.0)
    rec = w.fo("in_progress", w.ea)
    line = _line(w, rec, product, qty=2.0)
    exc = refused(w.env, lambda: line.with_user(w.ua).action_consume())
    assert exc and "Insufficient" in str(exc)
    assert line.state == "planned" and _van_qty(w, part, van) == 1.0


def test_b2_a_held_technician_cannot_fit_from_his_van(w):
    product, part, van = _m15(w, w.ea)
    recon = w.env["fix.stock.van.recon"].create({"location_id": van.id, "counted_qty": 0.0})
    recon.action_confirm()
    assert recon.state == "discrepancy"
    rec = w.fo("in_progress", w.ea)
    line = _line(w, rec, product)
    exc = refused(w.env, lambda: line.with_user(w.ua).action_consume())
    assert exc and "discrepancy" in str(exc)
    assert _van_qty(w, part, van) == 3.0


def test_b2_someone_elses_van_on_the_line_is_refused(w):
    product, part, van = _m15(w, w.eb)  # the van of technician B
    rec = w.fo("in_progress", w.ea)
    line = _line(w, rec, product, van_location_id=van.id)
    exc = refused(w.env, lambda: line.with_user(w.ua).action_consume())
    assert exc and "custody" in str(exc)
    assert _van_qty(w, part, van) == 3.0


def test_b2_a_serialized_part_needs_its_serial(w):
    product, part, van = _m15(w, w.ea, is_serialized=True, qty=1.0)
    lot = w.env["fix.stock.lot"].create(
        {"name": "A6F-SN", "part_id": part.id, "location_id": van.id, "qty": 1.0}
    )
    rec = w.fo("in_progress", w.ea)
    line = _line(w, rec, product)
    exc = refused(w.env, lambda: line.with_user(w.ua).action_consume())
    assert exc and "Serial number is mandatory" in str(exc)
    fitted = _line(w, rec, product, lot_serial_number=lot.name)
    fitted.with_user(w.ua).action_consume()
    assert fitted.m15_consumption_id.lot_id == lot and lot.status == "issued"


def test_b2_an_unmapped_product_is_unchanged_unless_the_param_is_on(w):
    product = w.env["product.product"].create({"name": "A06F unmapped"})
    rec = w.fo("in_progress", w.ea)
    line = _line(w, rec, product)
    line.with_user(w.ua).action_consume()
    assert line.state == "consumed" and not line.m15_consumption_id
    w.env["ir.config_parameter"].sudo().set_param("cd_field_service.m15_issue_required", "1")
    second = _line(w, rec, product)
    exc = refused(w.env, lambda: second.with_user(w.ua).action_consume())
    assert exc and "m15_issue_required" in str(exc)


def test_b2_the_issue_link_cannot_be_forged(w):
    product, _part, _van = _m15(w, w.ea)
    rec = w.fo("in_progress", w.ea)
    line = _line(w, rec, product)
    other = w.env["fix.stock.consumption"].search([], limit=1)
    if other:
        exc = refused(w.env, lambda: line.with_user(w.ua).write({"m15_consumption_id": other.id}))
        assert isinstance(exc, UserError)
