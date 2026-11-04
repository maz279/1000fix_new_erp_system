"""Shared live-ORM fixtures for the cd_warranty_claims tests (``odoo_env`` from
addons/conftest.py: fix_test, rolled back after every test).

A04 C2-C13 (2026-11-04): the claim work belongs to roles, so the fixture also
builds the people: two Warranty Claims Clerks, two Claim Decision Officers and
a plain internal user (read only), all in the claim's operating unit."""

import base64
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import Command, fields

CLERK = "cd_warranty_claims.group_warranty_claims_clerk"
OFFICER = "cd_warranty_claims.group_warranty_claims_officer"
KEYS = [
    "photo_before",
    "photo_after",
    "diagnostic",
    "parts_issued",
    "device_serial",
    "technician_cert",
    "purchase_proof",
]


@contextmanager
def refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def wc(odoo_env):
    env = odoo_env
    today = fields.Date.context_today(env.user)
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "WCLENT", "legal_name": "Warranty Claims Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "Warranty Desk",
            "code": "WCLB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "WclBrandA", "code": "WCLA"})
    other_brand = env["fix.brand"].create({"name": "WclBrandB", "code": "WCLB"})
    model = env["fix.device.model"].create({"name": "WclPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "Warranty Customer"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-WCL-1"}
    )
    warranty = env["fix.warranty"].create(
        {
            "device_id": device.id,
            "start_date": today - timedelta(days=60),
            "end_date": today + timedelta(days=300),
            "status": "active",  # A02 M01-W1: a new warranty is born pending
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Speaker dead",
            "order_category": "warranty",
        }
    )

    users = env["res.users"].with_context(no_reset_password=True)

    def user(login, *groups):
        return users.create(
            {
                "name": login.replace("_", " ").title(),
                "login": login,
                "group_ids": [Command.set([env.ref(g).id for g in ("base.group_user", *groups)])],
                "operating_unit_ids": [Command.set(ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )

    def claim(brand_rec=None, amount=12500.0, so=None, **vals):
        """A claim as the trusted intake raises it (superuser)."""
        return env["fix.warranty.claim"].create(
            {
                "operating_unit_id": ou.id,
                "service_order_id": (so or order).id,
                "brand_id": (brand_rec or brand).id,
                "claim_amount": amount,
                **vals,
            }
        )

    def document(key, so=None):
        return env["fix.document"].attach(
            name=f"{key}.jpg",
            datas=base64.b64encode(("%s-%s" % (key, (so or order).id)).encode()),
            document_type="other",
            res_model="fix.service.order",
            res_id=(so or order).id,
        )

    def full_pack(rec):
        rec.evidence_ids = [
            Command.create({"requirement_key": key, "document_id": document(key).id})
            for key in KEYS
        ]
        return rec

    def closed_order(total=2000.0, category="warranty"):
        """A warranty job with an approved estimate, CLOSED (M01's own close
        needs payment, QC and delivery evidence; its state is set directly)."""
        so = env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": branch.id,
                "fault_description": "Board fault",
                "order_category": category,
            }
        )
        if total:
            est = env["fix.estimate"].create(
                {
                    "order_id": so.id,
                    "line_ids": [
                        Command.create(
                            {"line_type": "part", "description": "Board", "unit_price": total}
                        )
                    ],
                }
            )
            est.action_send()
            est.action_approve()
        env.flush_all()
        env.cr.execute("UPDATE fix_service_order SET state = 'closed' WHERE id = %s", [so.id])
        so.invalidate_recordset(["state"])
        return so

    return SimpleNamespace(
        env=env,
        today=today,
        refused=lambda exc, match=None: refused(env, exc, match),
        ou=ou,
        branch=branch,
        brand=brand,
        other_brand=other_brand,
        customer=customer,
        device=device,
        warranty=warranty,
        order=order,
        claim=claim,
        document=document,
        full_pack=full_pack,
        closed_order=closed_order,
        user=user,
        clerk=user("wcl_clerk", CLERK),
        clerk2=user("wcl_clerk_two", CLERK),
        officer=user("wcl_officer", OFFICER),
        officer2=user("wcl_officer_two", OFFICER),
        plain=user("wcl_plain"),
    )
