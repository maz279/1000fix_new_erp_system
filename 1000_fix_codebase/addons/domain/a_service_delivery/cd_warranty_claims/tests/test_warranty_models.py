"""Behavioural tests for M09 warranty claims on the live ORM (fixtures: conftest.py).

These run as the trusted superuser (the AUT-018 intake, the brand API); the
role and segregation-of-duties controls are in test_a04_m09_controls.py."""

import json
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_warranty_claims.models.fix_warranty_claims import EVIDENCE_REQUIREMENTS
from odoo.exceptions import UserError

ALL_KEYS = [key for key, _label in EVIDENCE_REQUIREMENTS]


def _events(env, claim, event_type):
    return env["fix.event.outbox"].search(
        [
            ("aggregate", "=", "fix.warranty.claim"),
            ("aggregate_id", "=", claim.id),
            ("event_type", "=", event_type),
        ]
    )


def _complete_pack(wc, claim):
    claim.evidence_ids = [
        Command.create({"requirement_key": key, "document_id": wc.document(key).id})
        for key in ALL_KEYS
    ]


# --- fix.warranty.product ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("vals", "message"),
    [
        ({"duration_months": 0}, "The duration must be positive"),
        ({"waiting_days": -1}, "Waiting days and claim limit cannot be negative"),
        ({"claim_limit": -0.01}, "Waiting days and claim limit cannot be negative"),
    ],
)
def test_protection_product_terms_are_validated(wc, vals, message):
    with wc.refused(UserError, message):
        wc.env["fix.warranty.product"].create({"name": "WCL Care", **vals})


def test_protection_product_defaults(wc):
    product = wc.env["fix.warranty.product"].create({"name": "WCL Care+", "claim_limit": 50000.0})
    assert (product.product_type, product.duration_months, product.waiting_days) == (
        "extension",
        12,
        0,
    )
    assert product.currency_id.name == "BDT"


# --- creation, numbering and timing ----------------------------------------------------------


def test_claims_are_numbered_by_sequence_and_unique_within_a_day(wc):
    """Regression: no fix.warranty.claim sequence existed, every claim was
    "CLM/<today>" and the second claim of a day violated UNIQUE (claim_no)."""
    first, second = wc.claim(), wc.claim(amount=100.0)
    year = fields.Date.today().year
    assert first.claim_no.startswith(f"CLM/{year}/") and second.claim_no.startswith(f"CLM/{year}/")
    assert first.claim_no != second.claim_no
    assert wc.claim(claim_no="CLM-MANUAL-1").claim_no == "CLM-MANUAL-1"


def test_submission_window_and_latencies(wc):
    claim = wc.claim()
    assert claim.submission_deadline == claim.created_at + timedelta(hours=72)
    assert claim.job_completed_at == claim.created_at
    assert (claim.auto_creation_latency_hours, claim.submission_latency_hours) == (0.0, 0.0)
    created = claim.created_at
    claim.write(
        {
            "job_completed_at": created - timedelta(hours=30),
            "submitted_at": created + timedelta(hours=10, minutes=30),
        }
    )
    assert (claim.auto_creation_latency_hours, claim.submission_latency_hours) == (30.0, 10.5)
    claim.job_completed_at = created + timedelta(hours=1)  # clock skew never goes negative
    assert claim.auto_creation_latency_hours == 0.0
    claim.job_completed_at = False
    assert claim.auto_creation_latency_hours == 0.0


def test_overdue_only_while_unsubmitted_and_searchable(wc):
    """A04 M09-12: the flag is computed at read time (the stored one froze)
    and its search twin finds exactly the late, unsubmitted claims."""
    Claim = wc.env["fix.warranty.claim"]
    claim = wc.claim()
    on_time = wc.claim()
    assert claim.is_submission_overdue is False
    claim.submission_deadline = fields.Datetime.now() - timedelta(hours=1)
    assert claim.is_submission_overdue is True
    mine = [("id", "in", (claim | on_time).ids)]
    assert Claim.search([*mine, ("is_submission_overdue", "=", True)]) == claim
    assert Claim.search([*mine, ("is_submission_overdue", "=", False)]) == on_time
    claim.state = "submitted"
    assert claim.is_submission_overdue is False
    assert not Claim.search([*mine, ("is_submission_overdue", "=", True)])
    claim.write({"state": "draft", "submission_deadline": False})
    assert claim.is_submission_overdue is False


# --- evidence pack ----------------------------------------------------------------------------


def test_missing_evidence_lists_the_labels(wc):
    claim = wc.claim()
    assert claim.evidence_complete is False
    assert claim.missing_evidence == ", ".join(label for _key, label in EVIDENCE_REQUIREMENTS)
    claim.evidence_ids = [Command.create({"requirement_key": "photo_before"})]  # no document yet
    assert claim.missing_evidence.startswith("Before Photograph, ")
    _complete_pack(wc, claim)
    assert (claim.evidence_complete, claim.missing_evidence) == (True, False)
    assert all(claim.evidence_ids.filtered("document_id").mapped("evidence_hash"))


def test_pack_assembly_from_service_order_documents(wc):
    partial = wc.claim()
    wc.document("photo_before")
    partial.action_assemble_workshop_evidence_pack()
    assert partial.evidence_ids.mapped("requirement_key") == ["photo_before"]
    assert partial.state == "draft"  # still incomplete
    for key in ALL_KEYS[1:]:
        wc.document(key)
    assert partial.action_assemble_workshop_evidence_pack() is True
    assert sorted(partial.evidence_ids.mapped("requirement_key")) == sorted(
        ALL_KEYS
    )  # no duplicates
    assert len(partial.evidence_ids.mapped("document_id")) == len(ALL_KEYS)  # one each
    assert (partial.evidence_complete, partial.state) == (True, "ready")
    submitted = wc.claim(state="submitted")
    with wc.refused(UserError, "locked once submitted"):
        submitted.action_assemble_workshop_evidence_pack()


# --- AUT-018 auto-creation --------------------------------------------------------------------


def test_closed_warranty_job_creates_one_claim(wc):
    """Regression: the auto-created claim carried no operating unit (NOT NULL on
    the claim), so AUT-018 never created a single claim."""
    env = wc.env
    order = wc.closed_order(2000.0)
    wc.document("photo_before", so=order)
    model = env["fix.warranty.claim"]
    event = {"aggregate_id": order.id, "payload": {"completed_at": "2026-10-21 08:00:00"}}
    claim = model.consume_order_completed(event)
    estimate = order._fix_governing_estimate()
    # brand from the device; amount = the APPROVED estimate EX-VAT (A04 ERP
    # M09-F4: no brand rate released; it claimed the VAT-inclusive 2300)
    assert (claim.brand_id, claim.claim_amount) == (
        wc.brand,
        estimate.grand_total - estimate.vat_amount,
    )
    assert claim.claim_amount == 2000.0
    assert claim.job_completed_at == fields.Datetime.to_datetime("2026-10-21 08:00:00")
    assert claim.operating_unit_id == wc.branch.operating_unit_id  # the order has no OU of its own
    assert claim.evidence_ids.mapped("requirement_key") == ["photo_before"]
    payload = json.loads(_events(env, claim, "warranty_claim.created").payload)
    assert payload == {
        "claim_no": claim.claim_no,
        "order_id": order.id,
        "brand_id": wc.brand.id,
        "deadline": str(claim.submission_deadline),
    }
    assert model.consume_order_completed(event) == claim  # idempotent on the order


def test_auto_creation_ignores_unknown_paid_and_unclosed_orders(wc):
    """A04 M09-5: a DRAFT warranty job raised a 0.0 claim."""
    env = wc.env
    model = env["fix.warranty.claim"]
    assert model.consume_order_completed({"aggregate_id": 999999999}) is None
    paid = wc.closed_order(category="standard")
    assert model.consume_order_completed({"aggregate_id": paid.id, "payload": {}}) is None
    assert wc.order.state == "draft"
    assert model.consume_order_completed({"aggregate_id": wc.order.id, "payload": {}}) is None
    assert not model.search([("service_order_id", "in", (paid | wc.order).ids)])


def test_auto_created_claim_without_estimate_claims_zero_and_cannot_submit(wc):
    order = wc.closed_order(total=0.0)
    claim = wc.env["fix.warranty.claim"].consume_order_completed({"aggregate_id": order.id})
    assert claim.claim_amount == 0.0
    assert claim.job_completed_at  # completion time defaults to now
    wc.full_pack(claim)
    with wc.refused(UserError, "claims nothing"):
        claim.action_submit()


# --- submission, decision, remittance -----------------------------------------------------------


def test_incomplete_claim_cannot_be_submitted(wc):
    claim = wc.claim()
    with wc.refused(UserError, "cannot be submitted — missing evidence: Before Photograph"):
        claim.action_submit()
    assert claim.state == "draft"


def test_submission_within_and_after_the_window(wc):
    env = wc.env
    on_time = wc.claim()
    _complete_pack(wc, on_time)
    on_time.action_submit()
    assert (on_time.state, bool(on_time.submitted_at)) == ("submitted", True)
    assert (
        json.loads(_events(env, on_time, "warranty_claim.submitted").payload)["amount"] == 12500.0
    )
    assert not any("past 72h" in (m.body or "") for m in on_time.message_ids)
    with wc.refused(UserError, "Only a draft/ready claim submits"):
        on_time.action_submit()
    late = wc.claim()
    late.evidence_ids = [
        Command.create({"requirement_key": key, "document_id": wc.document(key + "_late").id})
        for key in ALL_KEYS
    ]
    late.submission_deadline = fields.Datetime.now() - timedelta(hours=2)
    # A04 ERP M09-F10: past the brand's window a claim has lapsed; it goes only
    # once an officer records the brand's late acceptance (Extend Window)
    with wc.refused(UserError, "lapsed"):
        late.action_submit()
    late.with_user(wc.officer).action_extend_deadline(
        fields.Datetime.now() + timedelta(hours=4), "Brand accepted it late (REF-1)"
    )
    late.action_submit()
    assert late.state == "submitted"


def test_brand_decision_requires_a_received_claim(wc):
    """Regression: a draft (never sent) or remitted claim could be decided, so a
    late brand webhook reopened a remitted claim."""
    env = wc.env
    draft = wc.claim()
    with wc.refused(UserError, "is draft — only a submitted or in-review claim can be decided"):
        draft.action_decide(approved=True)
    with wc.refused(UserError, "Only a submitted claim goes into review"):
        draft.action_mark_in_review()
    claim = wc.claim(state="submitted")
    claim.action_mark_in_review()
    assert claim.state == "in_review"
    claim.action_decide(approved=False, reason="Liquid damage")
    assert (claim.state, claim.rejection_reason, bool(claim.decided_at)) == (
        "rejected",
        "Liquid damage",
        True,
    )
    assert claim.decision_source == "brand_api"
    assert json.loads(_events(env, claim, "warranty_claim.decided").payload) == {
        "claim_no": claim.claim_no,
        "approved": False,
        "decision": "reject",
        "requested_amount": 12500.0,
        "approved_amount": 0.0,
        "brand_id": wc.brand.id,
        "company_id": claim.company_id.id,
        "currency": "BDT",
        "source": "brand_api",
    }
    with wc.refused(UserError, "is rejected"):
        claim.action_decide(approved=True)


def test_remittance_is_flagged_never_adjusted(wc):
    """T08 + A04 M09-4: a short payment is flagged and leaves the claim
    open (chased), it is not 'remitted'; the balance settles it."""
    env = wc.env
    claim = wc.claim(state="submitted")
    with wc.refused(UserError, "Only an approved claim takes a remittance"):
        claim.action_record_remittance(12500.0, "BANK-1")
    claim.action_decide(approved=True)
    assert (claim.state, claim.approved_amount) == ("approved", 12500.0)
    with wc.refused(UserError, "bank reference"):
        claim.action_record_remittance(11000.0, "")
    claim.action_record_remittance(11000.0, "BANK-2")
    assert (claim.state, claim.remittance_amount, claim.remittance_mismatch) == (
        "approved",
        11000.0,
        True,
    )
    payload = json.loads(_events(env, claim, "warranty_claim.remitted").payload)
    assert payload == {
        "claim_no": claim.claim_no,
        "bank_ref": "BANK-2",
        "expected": 12500.0,
        "received": 11000.0,
        "received_total": 11000.0,
        "mismatch": True,
        "settled": False,
    }
    claim.action_record_remittance(1500.0, "BANK-3")
    assert (claim.state, claim.remittance_amount, claim.remittance_mismatch) == (
        "remitted",
        12500.0,
        False,
    )
    assert claim.remittance_ref == "BANK-2, BANK-3"
    with wc.refused(UserError, "is remitted"):
        claim.action_decide(approved=False)  # a late webhook cannot reopen it
