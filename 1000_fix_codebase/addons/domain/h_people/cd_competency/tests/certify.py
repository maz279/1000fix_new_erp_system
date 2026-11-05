# Test helper (not a test module): certify a technician for dispatch.
#
# A09 workflow audit C4 / M22-F1-F2: assigning, dispatching or reassigning a
# technician now requires a VALID certification in a dispatch-gating
# competency scoped to the job's device type, and fails CLOSED for a device
# type no gating competency covers. Fixtures in other modules (field service,
# attendance, the workspace service-order API) that assign a technician to a
# job call this instead of each building their own competency.
from datetime import timedelta

from odoo import fields


def certify_for_dispatch(env, employee, device_type="smartphone"):
    """Give `employee` a valid certification for `device_type` (superuser
    setup: a superuser-created certification is valid). The default matches
    fix.device.model's default device type."""
    env = env(su=True)
    Competency = env["fix.competency"]
    comp = Competency.search([("required_for_dispatch", "=", True)]).filtered(
        lambda c: device_type in (c.device_type or "").replace(" ", "").split(",")
    )[:1]
    if not comp:
        comp = Competency.create(
            {
                "name": "Fixture %s dispatch" % device_type,
                "code": "FX-%s" % device_type.upper()[:12],
                "device_type": device_type,
                "required_for_dispatch": True,
            }
        )
    Cert = env["fix.certification"]
    cert = Cert.search(
        [("employee_id", "=", employee.id), ("competency_id", "=", comp.id)], limit=1
    )
    if cert:
        return cert
    today = fields.Date.today()
    return Cert.create(
        {
            "employee_id": employee.id,
            "competency_id": comp.id,
            "issued_on": today - timedelta(days=1),
            "expires_on": today + timedelta(days=365),
        }
    )


def licence_for_driving(env, employee, expiry_days=365):
    """Give `employee` a valid driving licence (M46 `fix.driver`: active, with
    a class and an expiry). Vehicle-based field dispatch checks it
    (FR-HSE-019, A09 round 2) and fails closed without it. No-op when the
    fleet register is not installed."""
    env = env(su=True)
    if "fix.driver" not in env:
        return None
    Driver = env["fix.driver"]
    driver = Driver.search([("employee_id", "=", employee.id)], limit=1)
    vals = {
        "state": "active",
        "license_class": "light",
        "license_expiry": fields.Date.today() + timedelta(days=expiry_days),
    }
    if driver:
        driver.write(vals)
        return driver
    return Driver.create(
        {
            "name": employee.name,
            "employee_id": employee.id,
            "license_no": "FX-DL-%d" % employee.id,
            **vals,
        }
    )
