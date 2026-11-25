"""M05 extension tests: alert resolution leg + remote session state guards.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

from unittest.mock import patch

import pytest
from odoo import fields
from odoo.exceptions import UserError


@pytest.fixture
def ms(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "MSEXT", "legal_name": "MS Ext Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "MS Ext Branch",
            "code": "MSE1",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    customer = env["res.partner"].create({"name": "MS Customer"})
    brand = env["fix.brand"].create({"name": "MsExtBrand", "code": "MSE"})
    device_model = env["fix.device.model"].create({"name": "MsExt Laptop", "brand_id": brand.id})
    device = env["fix.device"].create(
        {
            "device_model_id": device_model.id,
            "owner_id": customer.id,
            "branch_id": branch.id,
            "serial_number": "SN-MSE-1",
        }
    )
    contract = env["fix.contract"].create(
        {
            "name": "MS Ext Contract",
            "customer_id": customer.id,
            "family": "managed",
            "state": "active",  # A02 audit M05-P2: MSP work needs a term in force
            "operating_unit_id": ou.id,
            "date_start": fields.Date.today(),
            "date_end": fields.Date.today().replace(year=fields.Date.today().year + 1),
            "annual_value": 120000.0,
        }
    )
    msp = env["fix.msp.contract"].create(
        {
            "name": "MS Ext MSP",
            "contract_id": contract.id,
            "operating_unit_id": ou.id,
            "device_count": 1,
        }
    )
    asset = env["fix.monitored.asset"].create(
        {
            "msp_contract_id": msp.id,
            "agent_id": "AGT-MSE-1",
            "hostname": "ws-mse-01",
            "device_id": device.id,
        }
    )
    tech = env["hr.employee"].create({"name": "MS Tech"})
    from types import SimpleNamespace

    return SimpleNamespace(env=env, msp=msp, asset=asset, device=device, tech=tech, branch=branch)


# --- alert resolution ----------------------------------------------------


def test_alert_full_lifecycle_to_resolved(ms):
    alert = ms.env["fix.msp.alert"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "severity": "major",
            "message": "Disk failing",
        }
    )
    alert.action_acknowledge()
    alert.action_to_ticket()
    assert alert.state == "ticketed" and alert.order_id
    # A02 audit M05-P2: a ticketed alert resolves on its order's outcome
    assert alert.order_id.contract_id == ms.msp.contract_id
    with pytest.raises(UserError, match="resolves when service order"):
        alert.action_resolve(note="Disk replaced on-site")
    # the order's outcome, set as its workflow would (the walk itself is M01's)
    ms.env.flush_all()
    ms.env.cr.execute(
        "UPDATE fix_service_order SET state = 'ready' WHERE id = %s", (alert.order_id.id,)
    )
    ms.env.invalidate_all()
    alert.action_resolve(note="Disk replaced on-site")
    assert alert.state == "resolved"
    assert alert.resolved_at and alert.resolution_note == "Disk replaced on-site"


def test_alert_resolve_from_new_allowed(ms):
    """A false alarm can be resolved without ever ticketing."""
    alert = ms.env["fix.msp.alert"].create(
        {"msp_contract_id": ms.msp.id, "asset_id": ms.asset.id, "message": "Flapping"}
    )
    alert.action_resolve(note="False positive")
    assert alert.state == "resolved"


def test_alert_resolve_refuses_resolved(ms):
    alert = ms.env["fix.msp.alert"].create(
        {"msp_contract_id": ms.msp.id, "asset_id": ms.asset.id, "message": "x"}
    )
    with pytest.raises(UserError, match="resolution note"):
        alert.action_resolve()
    alert.action_resolve(note="flapping sensor")
    with pytest.raises(UserError, match="cannot be resolved"):
        alert.action_resolve(note="again")


# --- remote session guards -------------------------------------------------


def _grant_consent(session):
    """A02 audit M05-4: consent is the client's one-time code, not a tickbox."""
    sent = {}

    def _send(self, partner, code, ttl_seconds):
        sent["code"] = code
        return {"destination": "017*****000"}

    with patch.object(type(session), "_consent_send_code", _send):
        session.action_request_consent()
    session.action_verify_consent(code=sent["code"])


def test_remote_session_start_end_flow(ms):
    env = ms.env
    # consent required first
    session = env["fix.remote.session"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "technician_id": ms.tech.id,
            "tool": "rustdesk",
        }
    )
    _grant_consent(session)
    session.action_start()
    with pytest.raises(UserError, match="already running"):
        session.action_start()
    session.action_end(recording_url="mesh://recordings/1")
    assert session.ended_at
    with pytest.raises(UserError, match="already ended"):
        session.action_end()
    with pytest.raises(UserError, match="open a new session"):
        session.action_start()
    assert session.action_session_duration_minutes() is not None


def test_remote_session_pdpa_gate_still_enforced(ms):
    session = ms.env["fix.remote.session"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "technician_id": ms.tech.id,
            "tool": "meshcentral",
            "consent_captured": False,
        }
    )
    with pytest.raises(UserError, match="consent"):
        session.action_start()


def test_remote_session_end_requires_start(ms):
    session = ms.env["fix.remote.session"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "technician_id": ms.tech.id,
            "tool": "rustdesk",
            "consent_captured": True,
        }
    )
    with pytest.raises(UserError, match="has not started"):
        session.action_end()
