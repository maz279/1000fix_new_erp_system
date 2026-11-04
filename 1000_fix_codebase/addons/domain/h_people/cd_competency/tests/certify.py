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
