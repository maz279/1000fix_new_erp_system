"""Test helper: an in-force M08 contract for a contract-lane rate card.

M11 capture pass 2 (18 Nov 2026): a contract rate names a real fix.contract
(FR-PRC-016) and lapses with it (AC-08), so a test that records one first
needs the contract it belongs to."""

import uuid
from datetime import timedelta

from odoo import fields


def contract(env, prefix="AMC", state="active"):
    today = fields.Date.context_today(env["res.users"])
    code = "%s-%s" % (prefix, uuid.uuid4().hex[:8].upper())
    customer = env["res.partner"].sudo().create({"name": "%s customer" % code, "is_company": True})
    record = (
        env["fix.contract"]
        .sudo()
        .create(
            {
                "code": code,
                "name": "%s contract" % code,
                "family": "amc",
                "customer_id": customer.id,
                "operating_unit_id": env["operating.unit"].sudo().search([], limit=1).id,
                "date_start": today - timedelta(days=400),
                "date_end": today + timedelta(days=400),
                "annual_value": 120000.0,
                "stamp_duty_cert_no": "SD-%s" % code,
                "stamp_duty_amount": 300.0,
            }
        )
    )
    record._guarded().write({"state": state})
    return record
