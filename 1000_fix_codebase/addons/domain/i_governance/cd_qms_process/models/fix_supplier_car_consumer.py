# A10 S6 (M23-12 / the M42 hand-off): a supplier CAR the QMS must answer
# arrives as an NCR through the event relay. cd_vendor_portal does not
# depend on the governance stack (by design — a vendor portal must not
# import the QMS), so the hand-off is the supplier.car.raised event it
# publishes when a CAR is raised. The audit's case: a CRITICAL CAR closed
# with no root cause and no NCR anywhere in the QMS.
#
# This file must load after fix_qms.py (it extends fix.ncr): the import
# order in models/__init__.py is load order.
from odoo import api, fields, models
from odoo.exceptions import AccessError

# severity carries across 1:1 — the shared vocabulary is deliberate
CAR_SEVERITY = {"minor": "minor", "major": "major", "critical": "critical"}


class FixNcrSupplierCarConsumer(models.Model):
    _inherit = "fix.ncr"

    car_ref = fields.Char(
        string="Supplier CAR",
        copy=False,
        index=True,
        help="The fix.supplier.car this NCR was raised from through the event "
        "relay (A10 S6) — one NCR per CAR, however often the relay redelivers.",
    )

    @api.model
    def consume_supplier_car_raised(self, event: dict) -> dict:
        """The M42 -> M23 hand-off. A MAJOR/CRITICAL CAR is a
        non-conformance the QMS must record; a MINOR CAR stays vendor-side
        (proportionate — coaching is not an NCR)."""
        if not self.env.su:
            raise AccessError("Supplier CAR consumers run only from the event relay (A10 S6).")
        payload = event.get("payload") or {}
        car_ref = str(payload.get("car") or event.get("aggregate_id") or "").strip()
        if not car_ref:
            return {"created": 0, "reason": "no CAR reference in the event"}
        existing = self.sudo().search([("car_ref", "=", car_ref)], limit=1)
        if existing:
            # the relay may redeliver: the second delivery changes nothing
            return {"created": 0, "ncr": existing.name, "reason": "already raised"}
        severity = CAR_SEVERITY.get(str(payload.get("severity") or "").strip().lower())
        if severity is None:
            return {"created": 0, "reason": "unknown severity %r" % payload.get("severity")}
        if severity == "minor":
            return {"created": 0, "reason": "a minor CAR stays with the supplier portal"}
        supplier = (str(payload.get("supplier") or "").strip()) or (
            "supplier %s" % payload.get("supplier_id", "?")
        )
        ncr = self.create(
            {
                "source": "supplier",
                "severity": severity,
                "car_ref": car_ref,
                "description": "Supplier CAR %s (%s): %s"
                % (car_ref, supplier, payload.get("issue") or "no issue stated"),
            }
        )
        ncr.message_post(
            body="Raised from supplier CAR %s through the event relay (A10 S6)." % car_ref
        )
        return {"created": 1, "ncr": ncr.name, "car": car_ref, "severity": severity}
