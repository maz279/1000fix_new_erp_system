# ruff: noqa: F811 (the m fixture is imported, and named as test parameters)
"""A02 pass 2 independent review (21 Nov 2026), M06-05 consumer binding on the
M14 trade-in wipe gate: the certificate is bound to THIS trade-in. The
``odoo_env`` fixture rolls back."""

from odoo.addons.cd_tradein.tests.test_a05_m14_controls import (  # noqa: F401
    cert,
    device,
    m,
    request,
)


def _wipe_request(m, serial, source, source_ref):
    return m.env["fix.data.wipe.request"].create(
        {
            "source": source,
            "source_ref": source_ref,
            "serial_number": serial,
            "confidentiality_level": "high",
            "disposition": "resale",
        }
    )


def test_review_m14_a_certificate_raised_for_another_record_does_not_release(m):
    rec = request(m)
    dev = rec.device_id
    other = request(m)
    foreign = cert(m, dev, verified=False)
    foreign.write({"wipe_request_id": _wipe_request(m, dev.serial_number,
                                                    "m14_refurbishment", other.name).id})  # fmt: skip
    log = m.env["ir.attachment"].create({"name": "wipe.log", "raw": b"nwipe: PASS foreign"})
    foreign.write({"sector_count": 1000, "wipe_log_attachment_id": log.id, "media_kind": "flash"})
    foreign.action_verify()
    assert "no wipe request raised for" in rec._wipe_gate_denial(foreign, dev)
    # a customer's own request is not a refurbishment request
    customer = cert(m, dev, verified=False)
    customer.write({"wipe_request_id": _wipe_request(m, dev.serial_number,
                                                     "customer", rec.name).id})  # fmt: skip
    log2 = m.env["ir.attachment"].create({"name": "wipe.log", "raw": b"nwipe: PASS customer"})
    customer.write({"sector_count": 1000, "wipe_log_attachment_id": log2.id})
    customer.action_verify()
    assert "answers a customer request" in rec._wipe_gate_denial(customer, dev)
    # its own certificate releases it
    assert rec._wipe_gate_denial(cert(m, dev), dev) == ""
