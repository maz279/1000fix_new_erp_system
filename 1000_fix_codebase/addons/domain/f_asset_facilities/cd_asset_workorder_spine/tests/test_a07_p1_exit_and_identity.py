"""A07 P1 bridge (builder S): M21 exit clearance against asset custody, and
the M17 identity gate on the M01 invoice and the M09 warranty claim.

Live ORM, rolled back.
"""

from __future__ import annotations

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)


def _refused(env, fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        fn(*args, **kw)


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["res.users"].with_context(tz="Asia/Dhaka"))
    x.emp = env["hr.employee"].create({"name": "A07 Spine Leaver"})
    x.ou = env["operating.unit"].search([], limit=1)
    return x


def _exit(c, employee=None):
    # A09 M21 (merged): clearing runs from a confirmed notice, so the exit
    # carries a served statutory notice (BLA s.27 resignation, 30 days).
    return c.env["fix.hr.exit"].create(
        {
            "employee_id": (employee or c.emp).id,
            "notice_date": c.today - timedelta(days=40),
            "last_working_day": c.today + timedelta(days=5),
            "clearance_it": True,
            "clearance_finance": True,
            "clearance_hr": True,
            "clearance_assets": True,
        }
    )


def _equipment_issued_to(c, employee):
    e = c.env["fix.equipment"].create(
        {"code": "A7SPX-EQ1", "name": "A07 Spine leaver meter", "category": "Electrical"}
    )
    c.env["fix.calibration"].create(
        {
            "equipment_id": e.id,
            "calibrated_on": c.today - timedelta(days=10),
            "next_due": c.today + timedelta(days=300),
            "standard_ref": "STD",
            "result": "pass",
            "certificate_ref": "CERT",
            "performed_by": "Lab",
        }
    )
    return c.env["fix.equipment.issue"].create(
        {"equipment_id": e.id, "custodian_id": employee.id, "due_on": c.today + timedelta(days=3)}
    )


def _vehicle(c, plate, **kw):
    brand = c.env["fleet.vehicle.model.brand"].create({"name": "A7SPX Brand %s" % plate})
    model = c.env["fleet.vehicle.model"].create(
        {"name": "A7SPX Van", "brand_id": brand.id, "vehicle_type": "car"}
    )
    return c.env["fleet.vehicle"].create({"model_id": model.id, "license_plate": plate, **kw})


def test_exit_clearance_refuses_while_equipment_custody_is_open(c):
    issue = _equipment_issued_to(c, c.emp)
    ex = _exit(c)
    _refused(c.env, ex.action_clear, match=r"A7SPX-EQ1.*%s" % issue.name)
    assert ex.state == "draft"
    issue.action_return(condition="good")
    # A09 M21 (merged): an exit is cleared from its confirmed notice, not draft.
    ex.action_confirm_notice()
    ex.action_clear()
    assert ex.state == "cleared"


def test_exit_clearance_names_open_bookings_and_driven_vehicles(c):
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_vehicle_ext.mandatory_document_types", "fitness"
    )
    driver = c.env["fix.driver"].create(
        {
            "name": "A07 Spine Leaver",
            "employee_id": c.emp.id,
            "license_no": "DL-A7SPX",
            "license_class": "Light",
            "license_expiry": c.today + timedelta(days=400),
        }
    )
    van = _vehicle(c, "A7SPX-1", fix_driver_id=driver.id)
    other = _vehicle(c, "A7SPX-2")
    for v in (van, other):
        c.env["fix.vehicle.document"].create(
            {
                "vehicle_id": v.id,
                "doc_type": "fitness",
                "number": "F-%s" % v.id,
                "valid_to": c.today + timedelta(days=200),
                "evidence_file": "JVBERi0xLjQgc2Nhbg==",
            }
        )
    booking = c.env["fix.vehicle.assignment"].create(
        {"vehicle_id": other.id, "date": c.today + timedelta(days=2), "technician_id": c.emp.id}
    )
    past = c.env["fix.vehicle.assignment"].create(
        {"vehicle_id": other.id, "date": c.today - timedelta(days=5), "technician_id": c.emp.id}
    )
    ex = _exit(c)
    with pytest.raises(UserError) as err, c.env.cr.savepoint():
        ex.action_clear()
    text = str(err.value)
    assert "assigned driver of vehicle" in text and "A7SPX-1" in text
    assert "vehicle assignment of" in text and str(booking.date) in text
    assert str(past.date) not in text  # history is not a holding
    # reassigned: the exit clears
    van.write({"fix_driver_id": False})
    if "driver_employee_id" in van._fields:
        van.write({"driver_employee_id": False})
    booking.unlink()
    # A09 M21 (merged): an exit is cleared from its confirmed notice, not draft.
    ex.action_confirm_notice()
    ex.action_clear()
    assert ex.state == "cleared"


def test_an_employee_holding_nothing_clears_as_before(c):
    ex = _exit(c)
    # A09 M21 (merged): an exit is cleared from its confirmed notice, not draft.
    ex.action_confirm_notice()
    ex.action_clear()
    assert ex.state == "cleared"


# ------------------------------------------------------------ identity gate
@pytest.fixture
def m01(c):
    env = c.env
    # one legal entity per company (fix_entity_company_unique): reuse it
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "A7SPI", "legal_name": "A07 spine identity", "company_id": env.company.id})
    branch = env["fix.branch"].create(
        {
            "name": "A07 Spine Identity",
            "code": "A7SPI",
            "entity_id": entity.id,
            "operating_unit_id": c.ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "A7SPIBrand", "code": "A7SI"})
    model = env["fix.device.model"].create({"name": "A7SPI Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A7SPI Customer", "phone": "01711000773"})

    def order(state):
        device = env["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": customer.id,
                "serial_number": "A7SPI-%s" % state,
                "state": state,
            }
        )
        return env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": branch.id,
                "fault_description": "A07 spine identity",
                "operating_unit_id": c.ou.id,
            }
        )

    return types.SimpleNamespace(order=order, brand=brand)


def test_a_provisional_device_reaches_no_customer_invoice(c, m01):
    Invoice = c.env["fix.ar.invoice"]
    provisional = m01.order("provisional")
    assert provisional.device_id.state == "provisional"
    _refused(
        c.env,
        Invoice.from_closed_service_order,
        provisional,
        fields.Datetime.now(),
        match="provisional identity",
    )
    # a confirmed device passes the gate and meets the invoice's own rules
    registered = m01.order("registered")
    _refused(
        c.env,
        Invoice.from_closed_service_order,
        registered,
        fields.Datetime.now(),
        match="closed jobs only",
    )


def test_a_provisional_device_reaches_no_warranty_claim(c, m01):
    Claim = c.env["fix.warranty.claim"]
    vals = {"brand_id": m01.brand.id, "claim_amount": 1200.0, "operating_unit_id": c.ou.id}
    provisional = m01.order("provisional")
    _refused(
        c.env,
        Claim.create,
        dict(vals, service_order_id=provisional.id),
        match="provisional identity",
    )
    registered = m01.order("registered")
    claim = Claim.create(dict(vals, service_order_id=registered.id))
    assert claim.device_id == registered.device_id
    # a device marked provisional after the claim was drafted is not submitted
    registered.device_id._guarded().write({"state": "provisional"})
    _refused(c.env, claim.action_submit, match="provisional identity")
