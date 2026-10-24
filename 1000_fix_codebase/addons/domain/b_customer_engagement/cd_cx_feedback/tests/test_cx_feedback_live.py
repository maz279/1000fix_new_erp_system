"""Behavioural tests for M34 surveys/complaints and M42 supplier scorecards (live ORM)."""

import pytest
from odoo.exceptions import UserError


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def ou(env):
    return env["operating.unit"].search([], limit=1)


@pytest.fixture
def closed_order(env, ou):
    # fix.entity is UNIQUE per company: a dedicated company avoids queueing
    # behind other suites' entity on the shared test database
    company = env["res.company"].create({"name": "CX Feedback Test Co"})
    entity = env["fix.entity"].create(
        {"code": "CXENT", "legal_name": "CX Test Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "CX Banani", "code": "CXBN", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "CXBrand", "code": "CXBR"})
    model = env["fix.device.model"].create({"name": "CX Tab", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "CX Customer"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-CX-1"}
    )
    return env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No charging",
            "state": "closed",
        }
    )


# --- surveys ------------------------------------------------------------------------


def test_closed_event_triggers_one_survey(env, closed_order, ou):
    """Regression: the survey's required operating unit was never set, so the
    service_order.closed consumer failed for every order."""
    surveys = env["fix.survey"]
    event = {"event_id": "evt-cx-1", "aggregate_id": closed_order.id}
    survey = surveys.consume_order_closed(event)
    replay = surveys.consume_order_closed({"event_id": "evt-cx-2", "aggregate_id": closed_order.id})
    assert replay == survey  # idempotent on the order
    assert (survey.state, survey.source_event_id) == ("sent", "evt-cx-1")
    assert survey.operating_unit_id == ou
    assert survey.customer_id == closed_order.customer_id


@pytest.mark.parametrize(
    ("rating", "nps"), [(False, 0), ("1", -100), ("3", -100), ("4", 0), ("5", 100)]
)
def test_nps_from_rating(env, closed_order, rating, nps):
    survey = env["fix.survey"].consume_order_closed({"aggregate_id": closed_order.id})
    survey.rating = rating
    assert survey.nps_score == nps


# --- complaints ---------------------------------------------------------------------


def _complaint(env, ou, severity="minor", state="new"):
    return env["fix.complaint"].create(
        {
            "operating_unit_id": ou.id,
            "name": "Repeat fault after repair",
            "customer_id": env["res.partner"].create({"name": "CX Complainant"}).id,
            "description": "Same fault within a week",
            "severity": severity,
            "state": state,
        }
    )


def test_ncr_is_raised_only_after_investigation(env, ou):
    complaint = _complaint(env, ou)
    with pytest.raises(UserError, match="Investigate before raising the NCR"), env.cr.savepoint():
        complaint.action_raise_ncr()
    complaint.state = "investigating"
    complaint.action_raise_ncr()
    assert complaint.state == "ncr_raised"
    # the stub reference (cd_qms_process, when installed, links the real NCR onto it)
    assert complaint.ncr_stub_ref.startswith("NCR-STUB")
    assert f"/{complaint.id}" in complaint.ncr_stub_ref
    assert env["fix.event.outbox"].search_count(
        [("event_type", "=", "complaint.ncr_raised"), ("aggregate_id", "=", complaint.id)]
    )


def test_critical_complaints_close_only_through_capa(env, ou):
    critical = _complaint(env, ou, severity="critical")
    minor = _complaint(env, ou)
    with pytest.raises(UserError, match="CAPA verification"), env.cr.savepoint():
        critical.action_close("Refunded")
    minor.action_close("Re-repaired free of charge")
    assert (minor.state, minor.resolution) == ("closed", "Re-repaired free of charge")
    with pytest.raises(UserError, match="already closed"), env.cr.savepoint():
        minor.action_close("again")
    with pytest.raises(UserError, match="Record the resolution"), env.cr.savepoint():
        _complaint(env, ou).action_close("  ")
    if "capa_id" in critical._fields:
        # M23 installed: the linked CAPA record must be verified - free text is not enough
        critical.capa_stub_ref = "CAPA/typed-in"
        with pytest.raises(UserError, match="no CAPA is linked"), env.cr.savepoint():
            critical.action_close("Refunded")
        ncr = env["fix.ncr"].create(
            {"source": "complaint", "complaint_id": critical.id, "description": "Burnt board"}
        )
        capa = env["fix.capa"].create(
            {
                "ncr_id": ncr.id,
                "corrective_action": "Replace board",
                "owner_id": env["hr.employee"].create({"name": "CX QA Owner"}).id,
            }
        )
        critical.capa_id = capa
        with pytest.raises(UserError, match="'open', not verified"), env.cr.savepoint():
            critical.action_close("Refunded")
        capa.action_implement()
        capa.action_verify("Re-tested OK")
    else:
        critical.capa_stub_ref = "CAPA/2026/0001"  # entered by the quality owner
    critical.action_close("CAPA verified")
    assert critical.state == "closed"


def test_critical_closure_without_m23_needs_an_entered_capa_reference(env, ou, monkeypatch):
    critical = _complaint(env, ou, severity="critical")
    fields_without_m23 = {k: v for k, v in critical._fields.items() if k != "capa_id"}
    monkeypatch.setattr(type(critical), "_fields", fields_without_m23)
    assert critical._capa_closure_denial() == "no CAPA reference is entered"
    critical.capa_stub_ref = "CAPA/2026/0002"
    assert critical._capa_closure_denial() == ""


# --- supplier scorecards --------------------------------------------------------------


def test_scores_weight_on_time_and_quality(env, ou):
    vendor = env["res.partner"].create({"name": "CX Vendor A"})
    card = env["fix.supplier.scorecard"].create(
        {"vendor_id": vendor.id, "period": "2026-09", "operating_unit_id": ou.id}
    )
    assert (card.on_time_pct, card.score) == (100.0, 100.0)  # nothing late yet
    card.write({"lines_on_time": 3, "lines_late": 1, "rejection_count": 2})
    assert card.on_time_pct == 75.0
    assert card.score == round(0.6 * 75 + 0.4 * 80, 2)
    card.rejection_count = 15
    assert card.score == 45.0  # quality floors at 0


def test_goods_received_events_build_the_scorecard(env, ou):
    """Regression: a first event for a vendor/period created the card without
    its required operating unit and failed."""
    cards = env["fix.supplier.scorecard"]
    vendor = env["res.partner"].create({"name": "CX Vendor B"})
    assert cards.consume_goods_received({"payload": {}}) is None
    cards.consume_goods_received({"payload": {"vendor_id": vendor.id, "po_date": "2026-10-03"}})
    cards.consume_goods_received(
        {"payload": {"vendor_id": vendor.id, "po_date": "2026-10-21", "late": True}}
    )
    card = cards.search([("vendor_id", "=", vendor.id)])
    assert (card.period, card.lines_on_time, card.lines_late) == ("2026-10", 1, 1)
    assert card.operating_unit_id == ou
    explicit_ou = env["operating.unit"].create(
        {
            "name": "CX Second OU",
            "code": "CXOU2",
            "partner_id": vendor.id,
            "company_id": env.company.id,
        }
    )
    cards.consume_goods_received(
        {
            "payload": {
                "vendor_id": vendor.id,
                "po_date": "2026-11-02",
                "operating_unit_id": explicit_ou.id,
            }
        }
    )
    assert (
        cards.search([("vendor_id", "=", vendor.id), ("period", "=", "2026-11")]).operating_unit_id
        == explicit_ou
    )


def test_scorecards_publish_for_the_vendor_portal(env, ou):
    vendor = env["res.partner"].create({"name": "CX Vendor C"})
    card = env["fix.supplier.scorecard"].create(
        {
            "vendor_id": vendor.id,
            "period": "2026-08",
            "operating_unit_id": ou.id,
            "lines_on_time": 4,
        }
    )
    env["fix.supplier.scorecard"].publish_all_scorecards()
    [event] = env["fix.event.outbox"].search(
        [("event_type", "=", "supplier.scorecard"), ("aggregate_id", "=", card.id)]
    )
    assert '"period": "2026-08"' in event.payload
    assert '"score": 100.0' in event.payload
