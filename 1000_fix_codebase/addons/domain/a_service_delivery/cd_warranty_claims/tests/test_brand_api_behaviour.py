"""Behavioural tests for the P08 brand partner API (security model + contract) on
the live ORM; ``request`` is replaced by a stand-in, the controller runs unmodified.
Fixtures: conftest.py."""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import api, http
from odoo.addons.cd_warranty_claims.controllers import brand_api
from odoo.addons.cd_warranty_claims.controllers.brand_api import BrandApiController

ROUTES = ("claims", "claim_status", "claim_webhook", "reconciliation")


class _Request:
    def __init__(self, env):
        self.env = env
        self.session = http.Session(http.get_default_session(), "test-sid", new=True)
        self.httprequest = SimpleNamespace(headers={})


@contextmanager
def _as(env, user):
    fake = _Request(env(user=user.id) if user else api.Environment(env.cr, None, env.context))
    with patch.object(brand_api, "request", fake):
        yield fake


@pytest.fixture
def bw(wc):
    """The brand world: a portal user and an integration (internal) user per brand."""
    env = wc.env
    users = env["res.users"].with_context(no_reset_password=True)
    portal = env.ref("base.group_portal")
    brand_user = users.create(
        {"name": "Brand A Portal", "login": "brand.a@bapi.test", "group_ids": [(6, 0, [portal.id])]}
    )
    other_user = users.create({"name": "Brand B Bot", "login": "brand.b@bapi.test"})
    multi_user = users.create({"name": "Distributor", "login": "dist@bapi.test"})
    stranger = users.create({"name": "Not A Brand", "login": "nobody@bapi.test"})
    wc.brand.api_user_ids = brand_user | multi_user
    wc.other_brand.api_user_ids = other_user | multi_user
    own = wc.claim(state="submitted", amount=12500.0)
    foreign = wc.claim(brand_rec=wc.other_brand, state="submitted", amount=900.0)
    return SimpleNamespace(
        wc=wc,
        env=env,
        brand_user=brand_user,
        other_user=other_user,
        multi_user=multi_user,
        stranger=stranger,
        own=own,
        foreign=foreign,
    )


def _call(bw, user, route, **kwargs):
    with _as(bw.env, user):
        return getattr(BrandApiController(), route)(**kwargs)


@pytest.mark.parametrize("route", ROUTES)
def test_routes_require_bearer_auth_and_send_no_cors(route):
    routing = getattr(BrandApiController, route).original_routing
    assert routing["auth"] == "bearer"
    assert "cors" not in routing


# --- identity: the brand comes from the authenticated user ------------------------------------


@pytest.mark.parametrize("route", ROUTES)
def test_anonymous_callers_and_unlinked_users_get_nothing(bw, route):
    assert _call(bw, None, route)["error"]["code"] == "unauthenticated"
    assert _call(bw, bw.env.ref("base.public_user"), route)["error"]["code"] == "unauthenticated"
    res = _call(bw, bw.stranger, route, brand_id=bw.wc.brand.id)
    assert res == {
        "error": {"code": "no_brand", "message": "No brand is linked to the authenticated user"}
    }


@pytest.mark.parametrize("route", ROUTES)
def test_a_brand_id_naming_another_brand_is_forbidden(bw, route):
    """Regression: brand_id was caller-chosen - any user could read and decide any
    brand's claims by changing it."""
    for claimed in (bw.wc.other_brand.id, "abc"):
        res = _call(bw, bw.brand_user, route, brand_id=claimed, claim_no=bw.foreign.claim_no)
        assert res["error"]["code"] == "forbidden", (route, claimed)
    assert bw.foreign.state == "submitted"


def test_brand_id_is_optional_for_a_single_brand_and_required_for_several(bw):
    implicit = _call(bw, bw.brand_user, "claims")
    explicit = _call(bw, bw.brand_user, "claims", brand_id=str(bw.wc.brand.id))
    assert (
        [c["id"] for c in implicit["claims"]]
        == [bw.own.id]
        == [c["id"] for c in explicit["claims"]]
    )
    assert _call(bw, bw.multi_user, "claims")["error"]["code"] == "missing_brand"
    theirs = _call(bw, bw.multi_user, "claims", brand_id=bw.wc.other_brand.id)
    assert [c["id"] for c in theirs["claims"]] == [bw.foreign.id]


# --- /brand/claims ---------------------------------------------------------------------------


def test_claim_list_is_scoped_formatted_and_filterable(bw):
    draft = bw.wc.claim(amount=1234567.5)
    res = _call(bw, bw.brand_user, "claims")
    assert [c["id"] for c in res["claims"]] == [draft.id, bw.own.id]  # newest first
    row = res["claims"][0]
    assert row == {
        "id": draft.id,
        "claim_no": draft.claim_no,
        "state": "draft",
        "amount_bdt": "12,34,567.50",
        "approved_bdt": "0.00",
        "submitted_at": None,
        "decided_at": None,
        "rejection_reason": "",
        "evidence_complete": False,
        "missing_evidence": draft.missing_evidence,
    }
    submitted = _call(bw, bw.brand_user, "claims", state="submitted")
    assert ([c["id"] for c in submitted["claims"]], submitted["total"]) == ([bw.own.id], 1)


def test_decisions_only_on_own_received_claims(bw):
    user = bw.brand_user
    bad = _call(bw, user, "claims", claim_id=bw.own.id, decision="maybe")
    assert bad["error"] == {
        "code": "invalid_decision",
        "message": "decision must be approve|reject",
    }
    for claim_id in (bw.foreign.id, "abc", 999999999):
        res = _call(bw, user, "claims", claim_id=claim_id, decision="approve")
        assert res["error"] == {"code": "no_claim", "message": "Claim not found for this brand"}
    draft = bw.wc.claim()
    refused = _call(bw, user, "claims", claim_id=draft.id, decision="approve")
    assert refused["error"]["code"] == "decision_rejected"
    assert "only a submitted or in-review claim can be decided" in refused["error"]["message"]
    ok = _call(
        bw,
        user,
        "claims",
        brand_id=bw.wc.brand.id,
        claim_id=bw.own.id,
        decision="reject",
        reason="No proof",
    )
    assert ok == {"claim": {"id": bw.own.id, "claim_no": bw.own.claim_no, "state": "rejected"}}
    assert (bw.own.rejection_reason, bw.foreign.state, draft.state) == (
        "No proof",
        "submitted",
        "draft",
    )


# --- /brand/claims/status ------------------------------------------------------------------------


def test_claim_status(bw):
    user = bw.brand_user
    assert _call(bw, user, "claim_status")["error"]["code"] == "missing_claim_no"
    hidden = _call(bw, user, "claim_status", claim_no=bw.foreign.claim_no)
    assert hidden["error"]["code"] == "no_claim"
    bw.own.action_decide(approved=True)
    res = _call(bw, user, "claim_status", claim_no=bw.own.claim_no)
    assert res["claim"]["decision"]["approved"] is True
    assert (res["claim"]["amount_bdt"], res["claim"]["remitted_bdt"]) == ("12,500.00", "0.00")
    assert res["claim"]["decision"]["decided_at"]
    assert res["claim"]["decision"]["reason"] == ""


# --- /brand/claims/webhook -----------------------------------------------------------------------


def test_webhook_events(bw):
    user = bw.brand_user
    no = bw.own.claim_no
    assert _call(bw, user, "claim_webhook", claim_no=no)["error"]["code"] == "invalid_payload"
    hidden = _call(
        bw, user, "claim_webhook", claim_no=bw.foreign.claim_no, event_type="claim.approved"
    )
    assert hidden["error"]["code"] == "no_claim"
    assert bw.foreign.state == "submitted"
    review = _call(bw, user, "claim_webhook", claim_no=no, event_type="claim.in_review")
    assert review == {
        "status": "acknowledged",
        "claim_no": no,
        "state": "in_review",
        "event_type": "claim.in_review",
    }
    noise = _call(bw, user, "claim_webhook", claim_no=no, event_type="claim.viewed")
    assert noise["state"] == "in_review"  # unknown events are acknowledged, change nothing
    rejected = _call(
        bw,
        user,
        "claim_webhook",
        claim_no=no,
        event_type="claim.update",
        decision="reject",
        reason="Late",
    )
    assert (rejected["state"], bw.own.rejection_reason) == ("rejected", "Late")


def test_webhook_cannot_reopen_a_decided_claim(bw):
    """Regression: a late or replayed webhook re-decided closed claims."""
    user = bw.brand_user
    no = bw.own.claim_no
    approved = _call(bw, user, "claim_webhook", claim_no=no, event_type="claim.approved")
    assert approved["state"] == "approved"
    for event in (
        {"event_type": "claim.rejected"},
        {"event_type": "x", "decision": "approve"},
        {"event_type": "claim.in_review"},
    ):
        res = _call(bw, user, "claim_webhook", claim_no=no, **event)
        assert res["error"]["code"] == "event_rejected", event
    assert bw.own.state == "approved"


# --- /brand/reconciliation -------------------------------------------------------------------------


def test_reconciliation_flags_mismatches_with_signed_variance(bw):
    """A04 M09-4: the brand posts a remittance ADVICE; it never settles the
    claim. The claim is settled when a Claim Decision Officer records the
    money received against a bank reference."""
    user = bw.brand_user
    bw.own.action_decide(approved=True)
    matched = bw.wc.claim(state="submitted", amount=500.0)
    matched.action_decide(approved=True)
    pending = bw.wc.claim(state="submitted", amount=800.0)
    pending.action_decide(approved=True)
    short = _call(
        bw, user, "reconciliation", claim_id=bw.own.id, bank_ref="BRAC-77", amount="11000"
    )
    # advised 11,000.00 against 12,500.00 approved: a -1,500.00 variance, flagged
    assert short == {
        "remittance": {
            "claim_no": bw.own.claim_no,
            "state": "approved",
            "expected_bdt": "12,500.00",
            "advised_bdt": "11,000.00",
            "received_bdt": "0.00",
            "mismatch": True,
            "variance_bdt": "-1,500.00",
            "status": "advice_noted",
        }
    }
    assert bw.own.state == "approved" and not bw.own.remittance_amount
    exact = _call(bw, user, "reconciliation", claim_id=matched.id, bank_ref="BRAC-78", amount=500)
    assert (exact["remittance"]["mismatch"], exact["remittance"]["variance_bdt"]) == (False, "0.00")
    # the money: a Claim Decision Officer records what the bank received
    officer = bw.wc.officer
    matched.with_user(officer).action_record_remittance(500.0, "BRAC-78")
    bw.own.with_user(officer).action_record_remittance(11000.0, "BRAC-77")
    assert (matched.state, bw.own.state, bw.own.remittance_mismatch) == (
        "remitted",
        "approved",
        True,
    )
    view = {r["claim_no"]: r for r in _call(bw, user, "reconciliation")["reconciliation"]}
    assert set(view) == {bw.own.claim_no, matched.claim_no, pending.claim_no}  # never brand B's
    assert (view[bw.own.claim_no]["mismatch"], view[bw.own.claim_no]["variance_bdt"]) == (
        True,
        "-1,500.00",
    )
    assert (view[matched.claim_no]["mismatch"], view[matched.claim_no]["variance_bdt"]) == (
        False,
        "0.00",
    )
    # an approved claim with no advice and no receipt is never "mismatched"
    assert (view[pending.claim_no]["mismatch"], view[pending.claim_no]["received_bdt"]) == (
        False,
        "0.00",
    )


def test_a_brand_decides_in_part_as_itself(bw):
    res = _call(
        bw,
        bw.brand_user,
        "claims",
        claim_id=bw.own.id,
        decision="approve",
        approved_amount="9000",
        reason="Labour over the rate card",
    )
    assert res["claim"]["state"] == "partially_approved"
    assert (bw.own.approved_amount, bw.own.decided_by_id, bw.own.decision_source) == (
        9000.0,
        bw.brand_user,
        "brand_api",
    )
    assert bw.own.decision_ids.approved_amount == 9000.0


def test_the_openapi_contract_lists_the_brand_operations():
    import json
    from pathlib import Path

    repo = Path(__file__).resolve().parents[5]
    spec = json.loads((repo / "contracts" / "openapi" / "w4-portals.json").read_text("utf-8"))
    for path in (
        "/brand/claims",
        "/brand/claims/{claim_no}/status",
        "/brand/claims/webhook",
        "/brand/reconciliation",
    ):
        assert path in spec["paths"]


def test_remittance_input_and_state_validation(bw):
    user = bw.brand_user
    hidden = _call(bw, user, "reconciliation", claim_id=bw.foreign.id, bank_ref="X", amount=1)
    assert hidden["error"]["code"] == "no_claim"
    junk = _call(bw, user, "reconciliation", claim_id=bw.own.id, bank_ref="X", amount="lots")
    assert junk["error"] == {"code": "invalid_amount", "message": "amount must be a number"}
    early = _call(bw, user, "reconciliation", claim_id=bw.own.id, bank_ref="X", amount=12500)
    assert early["error"] == {
        "code": "remittance_rejected",
        "message": "Only an approved claim takes a remittance",
    }
    assert bw.own.state == "submitted"
