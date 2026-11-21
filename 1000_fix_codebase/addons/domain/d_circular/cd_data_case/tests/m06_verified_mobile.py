"""Test setup shared by the M06 suites (A02 pass 2 review): the hand-over code
goes only to a mobile verified in the party master (M33) before the case was
opened. This stands for that earlier, completed OTP verification."""

from datetime import timedelta

from odoo import fields


def verified_mobile_before(partner, case=None, phone=None):
    """The ``partner``'s mobile (default: its phone) as a contact point
    verified a day before ``case`` was opened (or before now)."""
    env = partner.env
    phone = phone or partner.phone
    Point = env["fix.contact.point"].sudo()
    point = Point.search(
        [("partner_id", "=", partner.id), ("contact_type", "=", "mobile"), ("value", "=", phone)],
        limit=1,
    )
    if not point:
        point = Point.create({"partner_id": partner.id, "contact_type": "mobile", "value": phone})
    since = (case.sudo().create_date if case else None) or fields.Datetime.now()
    point._guarded().write(
        {
            "state": "verified",
            "verification_method": "otp",
            "verified_at": since - timedelta(days=1),
        }
    )
    return point
