"""Behavioural tests for the lead -> service order conversion (T06, live ORM)."""

from unittest.mock import patch

import pytest
from odoo.exceptions import ValidationError


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


def _won(lead):
    """FLAW-07.1 / REQ-07.1 / REQ-07.2: conversion is gated to won deals with a
    verified contract, an approved rate card and no credit hold — tests must
    qualify their leads through the full gate ladder before converting.

    A03 P2: the ladder includes the approved estimate the order is built on
    (approved quote before order)."""
    estimate = lead.env["fix.estimate"].create({"lead_id": lead.id})
    lead.env["fix.estimate.line"].create(
        {"estimate_id": estimate.id, "description": "Screen", "unit_price": 1500.0}
    )
    estimate.action_approve()
    lead.write(
        {
            "probability": 100,
            "contract_ref": "PO-2026-TEST",
            "contract_verified": True,
            "rate_card_approved": True,
        }
    )
    return lead


def test_conversion_refuses_a_lead_that_has_not_reached_won(env, branch, phone_model):
    """The stage gate itself: an unqualified lead must NEVER convert (FLAW-07.1)."""
    customer = env["res.partner"].create({"name": "CRM Gate Customer"})
    env["fix.device"].create(
        {
            "device_model_id": phone_model.id,
            "owner_id": customer.id,
            "serial_number": "SN-CRM-GATE",
            "branch_id": branch.id,
        }
    )
    lead = _lead(env, customer)
    with pytest.raises(Exception, match="won"):
        lead.action_convert_to_service_order()
    assert not lead.converted_service_order_id
    # once qualified (won + verified contract + approved rate card) it converts
    _won(lead)
    lead.action_convert_to_service_order()
    assert lead.converted_service_order_id


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
    lead = _won(_lead(env, contact, "<p>Cracked <b>screen</b> after a fall</p>"))
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
    lead = _won(_lead(env, customer))
    first_branch = env["fix.branch"].search([], limit=1)
    lead.action_convert_to_service_order()
    assert lead.converted_service_order_id.branch_id == first_branch
    assert lead.converted_service_order_id.fault_description == "Converted from CRM lead"


def test_leads_that_cannot_be_converted_say_why(env, phone_model):
    """Remediated behaviour: each conversion precondition is a hard, named
    refusal (ValidationError) — the batch no longer soft-logs notes."""
    orphan = _won(_lead(env))
    deviceless = _won(_lead(env, env["res.partner"].create({"name": "CRM No Device"})))
    branchless_customer = env["res.partner"].create({"name": "CRM No Branch"})
    env["fix.device"].create(
        {
            "device_model_id": phone_model.id,
            "owner_id": branchless_customer.id,
            "serial_number": "SN-CRM-NB",
        }
    )
    branchless = _won(_lead(env, branchless_customer))
    with pytest.raises(ValidationError, match="No customer linked"):
        orphan.action_convert_to_service_order()
    with pytest.raises(ValidationError, match="no registered device"):
        deviceless.action_convert_to_service_order()
    with (
        patch.object(type(env["fix.branch"]), "search", return_value=env["fix.branch"]),
        pytest.raises(ValidationError, match="No branch is configured"),
    ):
        branchless.action_convert_to_service_order()
    for lead in (orphan, deviceless, branchless):
        assert not lead.converted_service_order_id
