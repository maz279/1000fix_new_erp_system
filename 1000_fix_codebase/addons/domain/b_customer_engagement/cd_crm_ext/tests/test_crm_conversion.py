"""Behavioural tests for the lead -> service order conversion (T06, live ORM)."""

from unittest.mock import patch

import pytest


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def branch(env):
    # fix.entity is UNIQUE per company: a dedicated company avoids queueing
    # behind other suites' entity on the shared test database
    company = env["res.company"].create({"name": "CRM Conversion Test Co"})
    entity = env["fix.entity"].create(
        {"code": "CRMENT", "legal_name": "CRM Test Entity", "company_id": company.id}
    )
    return env["fix.branch"].create(
        {
            "name": "CRM Gulshan",
            "code": "CRMGU",
            "entity_id": entity.id,
            "operating_unit_id": env["operating.unit"].search([], limit=1).id,
        }
    )


@pytest.fixture
def phone_model(env):
    brand = env["fix.brand"].create({"name": "CRMBrand", "code": "CRMBR"})
    return env["fix.device.model"].create({"name": "CRM Phone", "brand_id": brand.id})


def _lead(env, partner=None, description=None):
    return env["crm.lead"].create(
        {
            "name": "Screen repair enquiry",
            "partner_id": partner.id if partner else False,
            "description": description,
            "lead_source": "hotline",
        }
    )


def _notes(lead):
    return " ".join(lead.message_ids.mapped("body"))


def test_lead_converts_to_an_intake_order_on_the_customers_device(env, branch, phone_model):
    company = env["res.partner"].create({"name": "CRM Customer Ltd", "is_company": True})
    contact = env["res.partner"].create({"name": "CRM Contact", "parent_id": company.id})
    env["fix.device"].create(
        {"device_model_id": phone_model.id, "owner_id": company.id, "serial_number": "SN-CRM-OLD"}
    )
    newest = env["fix.device"].create(
        {
            "device_model_id": phone_model.id,
            "owner_id": contact.id,
            "serial_number": "SN-CRM-NEW",
            "branch_id": branch.id,
        }
    )
    lead = _lead(env, contact, "<p>Cracked <b>screen</b> after a fall</p>")
    lead.action_convert_to_service_order()
    order = lead.converted_service_order_id
    assert (order.device_id, order.branch_id, order.customer_id) == (newest, branch, contact)
    assert order.state == "intake"
    assert order.fault_description == "Cracked *screen* after a fall"
    assert lead.won_status == "won"
    event = env["fix.event.outbox"].search(
        [("event_type", "=", "lead.converted_to_order"), ("aggregate_id", "=", lead.id)]
    )
    assert f'"service_order_id": {order.id}' in event.payload


def test_conversion_falls_back_to_the_first_branch_and_a_default_fault(env, branch, phone_model):
    customer = env["res.partner"].create({"name": "CRM Walk-in"})
    env["fix.device"].create(
        {"device_model_id": phone_model.id, "owner_id": customer.id, "serial_number": "SN-CRM-W"}
    )
    lead = _lead(env, customer)
    first_branch = env["fix.branch"].search([], limit=1)
    lead.action_convert_to_service_order()
    assert lead.converted_service_order_id.branch_id == first_branch
    assert lead.converted_service_order_id.fault_description == "Converted from CRM lead"


def test_leads_that_cannot_be_converted_say_why(env, phone_model):
    orphan = _lead(env)
    deviceless = _lead(env, env["res.partner"].create({"name": "CRM No Device"}))
    branchless_customer = env["res.partner"].create({"name": "CRM No Branch"})
    env["fix.device"].create(
        {
            "device_model_id": phone_model.id,
            "owner_id": branchless_customer.id,
            "serial_number": "SN-CRM-NB",
        }
    )
    branchless = _lead(env, branchless_customer)
    with patch.object(type(env["fix.branch"]), "search", return_value=env["fix.branch"]):
        (orphan | deviceless | branchless).action_convert_to_service_order()
    assert "no customer linked" in _notes(orphan)
    assert "no registered device" in _notes(deviceless)
    assert "no branch is configured" in _notes(branchless)
    for lead in (orphan, deviceless, branchless):
        assert not lead.converted_service_order_id
        assert lead.won_status != "won"
