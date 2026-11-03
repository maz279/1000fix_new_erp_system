"""Shared live-ORM fixtures for the cd_warranty_claims tests (``odoo_env`` from
addons/conftest.py: fix_test, rolled back after every test)."""

import base64
from contextlib import contextmanager
from datetime import date, timedelta
from types import SimpleNamespace

import pytest


@contextmanager
def refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def wc(odoo_env):
    env = odoo_env
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
    env["fix.warranty"].create(
        {
            "device_id": device.id,
            "start_date": date.today() - timedelta(days=60),
            "end_date": date.today() + timedelta(days=300),
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

    def claim(brand_rec=None, amount=12500.0, **vals):
        return env["fix.warranty.claim"].create(
            {
                "operating_unit_id": ou.id,
                "service_order_id": order.id,
                "brand_id": (brand_rec or brand).id,
                "claim_amount": amount,
                **vals,
            }
        )

    def document(key):
        return env["fix.document"].attach(
            name=f"{key}.jpg",
            datas=base64.b64encode(key.encode()),
            document_type="other",
            res_model="fix.service.order",
            res_id=order.id,
        )

    return SimpleNamespace(
        env=env,
        refused=lambda exc, match=None: refused(env, exc, match),
        ou=ou,
        branch=branch,
        brand=brand,
        other_brand=other_brand,
        customer=customer,
        device=device,
        order=order,
        claim=claim,
        document=document,
    )
