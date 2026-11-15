# M42 capture audit 2026-11-15 - live ORM proof for the records the sub-module
# pages now capture: segment reviews, agreements, agreed prices, price changes,
# contacts, questionnaire templates, classification / authorisation evidence,
# and the PO price gate (BRU-SRM2-14). Every step runs as a NON-ADMIN steward
# or approver created in the transaction; everything is rolled back.
import importlib.util
from datetime import timedelta
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

_spec = importlib.util.spec_from_file_location(
    "_m42_controls", Path(__file__).with_name("test_a06_m42_controls.py")
)
_ctl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ctl)

c = _ctl.c  # the fixture: steward, steward2, approver, approver2, plain users
p03 = _ctl.p03
supplier, active_supplier, docs, qual = (
    _ctl.supplier,
    _ctl.active_supplier,
    _ctl.docs,
    _ctl.qual,
)
PDF = _ctl.PDF
REFUSED = (UserError, ValidationError, AccessError)


def _agreement(c, s, user=None, **kw):
    vals = {
        "supplier_id": s.id,
        "agreement_type": "framework",
        "reference": "FA-%s" % s.id,
        "term_from": c.today - timedelta(days=10),
        "term_to": c.today + timedelta(days=365),
        "currency_id": c.env.ref("base.BDT").id,
        "file": PDF,
        "file_filename": "fa.pdf",
    }
    vals.update(kw)
    return c.env["fix.supplier.agreement"].with_user(user or c.steward).create(vals)


def _in_force(c, s, **kw):
    a = _agreement(c, s, **kw)
    a.with_user(c.approver).action_activate()
    assert a.state == "active"
    return a


def _price(c, a, price=1000.0, approve=True):
    p = (
        c.env["fix.supplier.price.list"]
        .with_user(c.steward)
        .create(
            {
                "agreement_id": a.id,
                "product_id": c.prod.id,
                "price": price,
                "valid_from": c.today - timedelta(days=5),
            }
        )
    )
    if approve:
        p.with_user(c.approver).action_approve()
    return p


# ------------------------------------------------------------ segmentation
def test_segment_is_fixed_after_onboarding_and_moves_by_review(c):
    s = active_supplier(c)
    with pytest.raises(UserError, match="segment review"):
        s.with_user(c.steward).write({"segment": "strategic"})
    # resending the unchanged value (the workspace form re-posts every field) passes
    s.with_user(c.steward).write({"segment": s.segment, "notes": "re-sent"})
    r = (
        c.env["fix.supplier.segment.review"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "to_segment": "strategic", "reason": "BDT 4M spend"})
    )
    r.with_user(c.steward).action_propose()
    assert r.state == "proposed" and r.from_segment == "transactional"
    with pytest.raises(UserError, match="role"):
        r.with_user(c.steward).action_approve()
    with pytest.raises(UserError, match="proposal|proposed|reject"):
        r.with_user(c.steward).write({"to_segment": "preferred"})
    r.with_user(c.approver).action_approve()
    assert s.segment == "strategic" and r.state == "approved"
    assert r.decided_by_id == c.approver


def test_a_prospect_segment_is_set_at_onboarding(c):
    s = supplier(c)
    s.with_user(c.steward).write({"segment": "preferred"})
    assert s.segment == "preferred"


def test_segment_review_needs_a_change_and_reject_needs_a_reason(c):
    s = active_supplier(c)
    same = (
        c.env["fix.supplier.segment.review"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "to_segment": s.segment, "reason": "x"})
    )
    with pytest.raises(UserError, match="already"):
        same.with_user(c.steward).action_propose()
    r = (
        c.env["fix.supplier.segment.review"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "to_segment": "preferred", "reason": "growth"})
    )
    r.with_user(c.steward).action_propose()
    with pytest.raises(UserError, match="why"):
        r.with_user(c.approver).action_reject(reason=" ")
    r.with_user(c.approver).action_reject(reason="spend not sustained")
    assert r.state == "rejected" and s.segment == "transactional"


def test_plain_user_cannot_create_a_segment_review(c):
    s = supplier(c)
    with pytest.raises(AccessError):
        c.env["fix.supplier.segment.review"].with_user(c.plain).create(
            {"supplier_id": s.id, "to_segment": "strategic", "reason": "x"}
        )


# ------------------------------------------------------------ agreements
def test_agreement_goes_in_force_by_a_second_person_with_its_signed_copy(c):
    s = active_supplier(c)
    a = _agreement(c, s, file=False)
    with pytest.raises(UserError, match="signed copy"):
        a.with_user(c.approver).action_activate()
    a.with_user(c.steward).write({"file": PDF})
    with pytest.raises(UserError, match="role"):
        a.with_user(c.steward).action_activate()
    a.with_user(c.approver).action_activate()
    assert a.state == "active" and a.approved_by_id == c.approver
    with pytest.raises(UserError, match="terms are fixed"):
        a.with_user(c.steward).write({"committed_value": 5})
    with pytest.raises(UserError, match="cannot be set directly|workflow"):
        _agreement(c, s, state="active")


def test_consignment_agreement_needs_its_terms(c):
    s = active_supplier(c)
    a = _agreement(c, s, agreement_type="consignment")
    with pytest.raises(UserError, match="BRU-SRM2-15"):
        a.with_user(c.approver).action_activate()
    a.with_user(c.steward).write(
        {
            "parts_scope": "All genuine display assemblies",
            "valuation_basis": "agreed_price",
            "settlement_trigger": "consumption",
            "settlement_cadence": "monthly",
            "return_rights": "Unused parts within 90 days",
            "reconciliation_frequency": "monthly",
            "loss_liability": "fix",
        }
    )
    a.with_user(c.approver2).action_activate()
    assert a.state == "active"


def test_agreement_expiry_cron_warns_then_expires(c):
    s = active_supplier(c)
    soon = _in_force(c, s, term_to=c.today + timedelta(days=30), reference="SOON")
    out = c.env["fix.supplier.agreement"]._cron_agreement_expiry()
    assert out["reminders"]
    soon._guarded().write({"term_to": c.today - timedelta(days=1)})
    out = c.env["fix.supplier.agreement"]._cron_agreement_expiry()
    assert soon.id in out["expired"] and soon.state == "expired"


def test_terminate_needs_a_reason(c):
    a = _in_force(c, active_supplier(c))
    with pytest.raises(UserError, match="why"):
        a.with_user(c.approver).action_terminate(reason="")
    a.with_user(c.approver).action_terminate(reason="supplier exit")
    assert a.state == "terminated"


# ------------------------------------------------------------ prices
def test_agreed_price_is_approved_by_a_second_person_under_an_agreement_in_force(c):
    s = active_supplier(c)
    draft = _agreement(c, s)
    p = _price(c, draft, approve=False)
    with pytest.raises(UserError, match="not in force"):
        p.with_user(c.approver).action_approve()
    draft.with_user(c.approver).action_activate()
    p.with_user(c.approver).action_approve()
    assert p.state == "approved"
    with pytest.raises(UserError, match="price change"):
        p.with_user(c.steward).write({"price": 900})
    dup = _price(c, draft, price=950, approve=False)
    with pytest.raises(UserError, match="already has an approved price"):
        dup.with_user(c.approver2).action_approve()


def test_price_change_requires_justification_and_a_second_person(c):
    a = _in_force(c, active_supplier(c))
    p = _price(c, a, price=1000)
    ch = (
        c.env["fix.supplier.price.change"]
        .with_user(c.steward)
        .create(
            {
                "price_list_id": p.id,
                "proposed_price": 1100,
                "effective_from": c.today + timedelta(days=1),
                "justification": "Copper +12%",
            }
        )
    )
    ch.with_user(c.steward).action_submit()
    assert ch.old_price == 1000 and ch.variance_pct == 10.0
    with pytest.raises(UserError, match="Price change"):
        ch.with_user(c.steward).write({"proposed_price": 1050})
    ch.with_user(c.approver).action_approve()
    new = ch.new_price_id
    assert new.state == "approved" and new.price == 1100
    assert new.valid_from == c.today + timedelta(days=1)
    assert p.valid_to == c.today and p.price == 1000


def test_price_change_reject_needs_reason(c):
    a = _in_force(c, active_supplier(c))
    p = _price(c, a)
    ch = (
        c.env["fix.supplier.price.change"]
        .with_user(c.steward)
        .create(
            {
                "price_list_id": p.id,
                "proposed_price": 2000,
                "effective_from": c.today + timedelta(days=2),
                "justification": "x",
            }
        )
    )
    ch.with_user(c.steward).action_submit()
    with pytest.raises(UserError, match="why"):
        ch.with_user(c.approver).action_reject(reason="")
    ch.with_user(c.approver).action_reject(reason="not justified")
    assert ch.state == "rejected" and p.price == 1000.0


def test_po_above_the_agreed_price_is_refused(c):
    s = active_supplier(c)
    a = _in_force(c, s)
    _price(c, a, price=1000)
    po = c.env["fix.purchase.order"].create(
        {
            "operating_unit_id": c.ou.id,
            "vendor_id": s.partner_id.id,
            "currency_id": c.env.ref("base.BDT").id,
            "line_ids": [(0, 0, {"product_id": c.prod.id, "qty_ordered": 2, "unit_price": 1200})],
        }
    )
    with pytest.raises(UserError, match="BRU-SRM2-14"):
        po._a06_check_categories()
    po.line_ids.write({"unit_price": 1000})
    po._a06_check_categories()


def test_po_for_a_part_without_an_agreed_price_is_not_checked(c):
    s = active_supplier(c)
    other = c.env["product.product"].create({"name": "A06M42T unpriced"})
    po = c.env["fix.purchase.order"].create(
        {
            "operating_unit_id": c.ou.id,
            "vendor_id": s.partner_id.id,
            "line_ids": [(0, 0, {"product_id": other.id, "qty_ordered": 1, "unit_price": 99999})],
        }
    )
    po._a06_check_agreed_prices()


# ------------------------------------------------------------ profile, contacts, qualification
def test_contact_needs_a_phone_or_email(c):
    s = supplier(c)
    with pytest.raises(ValidationError):
        c.env["fix.supplier.contact"].with_user(c.steward).create(
            {"supplier_id": s.id, "name": "Rahim", "role": "commercial"}
        )
    rec = (
        c.env["fix.supplier.contact"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "name": "Rahim", "role": "quality", "phone": "01700000000"})
    )
    assert rec in s.contact_ids


def test_authorised_distributor_needs_brand_authorisation_to_qualify(c):
    s = supplier(c, classification="authorised_distributor")
    docs(c, s)
    q = qual(c, s, approve=False)
    q.with_user(c.steward).action_start()
    with pytest.raises(UserError, match="Brand / OEM Authorisation"):
        q.with_user(c.approver).action_approve()
    auth = (
        c.env["fix.supplier.document"]
        .with_user(c.steward)
        .create(
            {
                "supplier_id": s.id,
                "doc_type": "brand_authorisation",
                "number": "AUTH-1",
                "file": PDF,
                "valid_to": c.today + timedelta(days=200),
            }
        )
    )
    auth.with_user(c.steward2).action_verify()
    q.with_user(c.approver).action_approve()
    assert q.state == "approved" and s.status == "qualified"


def test_questionnaire_template_adds_evidence_and_raises_the_bar(c):
    tpl = (
        c.env["fix.qualification.questionnaire"]
        .with_user(c.steward)
        .create(
            {
                "name": "Display assemblies - high risk",
                "questions": "ISO certified? (20)\nCounterfeit controls? (30)",
                "required_doc_types": "iso",
                "pass_threshold": 85,
            }
        )
    )
    with pytest.raises(ValidationError):
        c.env["fix.qualification.questionnaire"].with_user(c.steward).create(
            {"name": "bad", "questions": "q", "required_doc_types": "nonsense"}
        )
    s = supplier(c)
    q = (
        c.env["fix.supplier.qualification"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "score": 80, "questionnaire_id": tpl.id})
    )
    q.with_user(c.steward).action_start()
    with pytest.raises(UserError) as err:
        q.with_user(c.approver).action_approve()
    assert "ISO" in str(err.value) and "85.0" in str(err.value)


def test_workspace_writes_go_through_the_endpoint(c, p03):
    """The forms' own endpoint creates a segment review and refuses a typed
    agreement state (whitelist + guard)."""
    s = active_supplier(c)
    out = p03.write(
        model="fix.supplier.segment.review",
        record_id=None,
        values={"supplier_id": s.id, "to_segment": "preferred", "reason": "via form"},
    )
    assert "error" not in out, out
    a = _agreement(c, s)
    p03.write(model="fix.supplier.agreement", record_id=a.id, values={"state": "active"})
    a.invalidate_recordset()
    assert a.state == "draft"
