# P08 Brand Partner API — the W4 contract endpoints (PP5).
#
# Claim submission status, decision capture and remittance
# reconciliation for the brands 1000FiX recovers warranty costs from.
# Decisions ride fix.warranty.claim.action_decide (the brand's OWN decision,
# recorded with the brand user as decider; partial approvals carry
# approved_amount); reconciliation surfaces FLAGGED mismatches, never
# auto-adjusts (T08).
#
# A04 workflow audit (2026-11-03) M09-4: the paying brand recorded its own
# remittance, which settled the claim. A brand now posts a remittance ADVICE;
# the claim is settled only when a Claim Decision Officer records the money
# received against a bank reference (fix.warranty.claim.action_record_remittance).
#
# Security model (R01 re-audit 2026-10-22, same model as the P02 technician API):
# - every route is ``auth="bearer"``: an Odoo API key in ``Authorization: Bearer``
#   (a brand partner system / the webhook) or an authenticated interactive session.
#   No CORS header is emitted.
# - BRAND ISOLATION: the brand is ALWAYS resolved from the authenticated user
#   (``fix.brand.api_user_ids``, ``resolve_brand``). The ``brand_id`` request
#   parameter never selects the brand: it may only confirm one of the caller's
#   brands (required when the caller acts for several) and is refused with
#   ``forbidden`` otherwise. A claim outside the resolved brand is
#   indistinguishable from a claim that does not exist.
# - the superuser environment is only used for model access (brand partners are
#   not internal users); every read and write is scoped to the resolved brand.

from odoo import SUPERUSER_ID, http
from odoo.addons.cd_service_order.controllers.technician_api import _error, _fmt_bdt, _to_int
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


def _su_env():
    return request.env(user=SUPERUSER_ID, su=True)


def resolve_brand(kwargs):
    """Resolve the acting brand from the AUTHENTICATED user only.

    Returns ``(brand, None)`` or ``(None, error_dict)``:
    - no authenticated (non-public) user -> ``unauthenticated``;
    - the user is linked to no brand -> ``no_brand`` (never an all-brands default);
    - ``brand_id`` naming a brand the user does not act for -> ``forbidden``;
    - no ``brand_id`` while the user acts for several brands -> ``missing_brand``.
    """
    user = request.env.user
    if not user or user._is_public():
        return None, _error("unauthenticated", "Brand partner authentication is required")
    brands = _su_env()["fix.brand"].search([("api_user_ids", "in", user.id)])
    if not brands:
        return None, _error("no_brand", "No brand is linked to the authenticated user")
    claimed = kwargs.get("brand_id")
    if claimed in (None, "", False):
        if len(brands) > 1:
            return None, _error(
                "missing_brand", "brand_id is required: the user acts for several brands"
            )
        return brands, None
    brand = brands.filtered(lambda b: b.id == _to_int(claimed))
    if not brand:
        return None, _error("forbidden", "brand_id is not a brand of the authenticated user")
    return brand, None


def _brand_claim(brand, claim_id):
    """The claim ``claim_id`` if it belongs to ``brand``, else an empty recordset
    (another brand's claim and an unknown id are indistinguishable)."""
    claim_int = _to_int(claim_id)
    if claim_int is None:
        return _su_env()["fix.warranty.claim"]
    return _su_env()["fix.warranty.claim"].search(
        [("id", "=", claim_int), ("brand_id", "=", brand.id)], limit=1
    )


def _variance(claim):
    """Received against what the OEM APPROVED (a partial approval is not a
    short payment)."""
    mismatch = abs(claim.remittance_amount - claim.approved_amount) > 0.01
    diff = round(claim.remittance_amount - claim.approved_amount, 2)
    return mismatch, _fmt_bdt(diff) if mismatch else "0.00"


def _amount(kwargs):
    """An optional approved_amount parameter (partial approval), or None."""
    raw = kwargs.get("approved_amount")
    if raw in (None, "", False):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


class BrandApiController(http.Controller):
    """The P08 brand partner portal API (W4 contract)."""

    @http.route("/brand/claims", type="jsonrpc", auth="bearer", readonly=False)
    def claims(self, **kwargs):
        """Combined endpoint: decide when `claim_id`+`decision` are present,
        otherwise list the resolved brand's claims."""
        brand, err = resolve_brand(kwargs)
        if err:
            return err
        if kwargs.get("claim_id") and kwargs.get("decision"):
            return self._decide_claim(brand, **kwargs)
        return self._list_claims(brand, **kwargs)

    def _list_claims(self, brand, **kwargs):
        domain = [("brand_id", "=", brand.id)]
        state = kwargs.get("state")
        if state:
            domain.append(("state", "=", state))
        claims = _su_env()["fix.warranty.claim"].search(domain, limit=100, order="id desc")
        result = [
            {
                "id": c.id,
                "claim_no": c.claim_no,
                "state": c.state,
                "amount_bdt": _fmt_bdt(c.claim_amount),
                "approved_bdt": _fmt_bdt(c.approved_amount),
                "submitted_at": str(c.submitted_at or "") or None,
                "decided_at": str(c.decided_at or "") or None,
                "rejection_reason": c.rejection_reason or "",
                "evidence_complete": c.evidence_complete,
                "missing_evidence": c.missing_evidence or "",
            }
            for c in claims
        ]
        return {"claims": result, "total": len(result)}

    def _decide_claim(self, brand, **kwargs):
        """The brand's decision (approve/reject with reason). Only a submitted /
        in-review claim of the resolved brand can be decided (model gate)."""
        decision = kwargs.get("decision")
        if decision not in ("approve", "reject"):
            return _error("invalid_decision", "decision must be approve|reject")
        claim = _brand_claim(brand, kwargs.get("claim_id"))
        if not claim:
            # isolation: another brand's claim "does not exist"
            return _error("no_claim", "Claim not found for this brand")
        try:
            claim.action_decide(
                approved=(decision == "approve"),
                reason=kwargs.get("reason", ""),
                approved_amount=_amount(kwargs),
                decided_by_id=request.env.user.id,
            )
        except (UserError, ValidationError) as exc:
            return _error("decision_rejected", str(exc))
        return {"claim": {"id": claim.id, "claim_no": claim.claim_no, "state": claim.state}}

    @http.route("/brand/claims/status", type="jsonrpc", auth="bearer", readonly=True)
    def claim_status(self, **kwargs):
        """Single-claim status (webhook-fed path shape: claim_no + brand)."""
        brand, err = resolve_brand(kwargs)
        if err:
            return err
        claim_no = kwargs.get("claim_no")
        if not claim_no:
            return _error("missing_claim_no", "claim_no is required")
        claim = _su_env()["fix.warranty.claim"].search(
            [("claim_no", "=", claim_no), ("brand_id", "=", brand.id)], limit=1
        )
        if not claim:
            return _error("no_claim", "Claim not found for this brand")
        return {
            "claim": {
                "claim_no": claim.claim_no,
                "state": claim.state,
                "amount_bdt": _fmt_bdt(claim.claim_amount),
                "remitted_bdt": _fmt_bdt(claim.remittance_amount),
                "decision": {
                    "approved": claim.state
                    in ("approved", "partially_approved", "remitted", "closed")
                    and bool(claim.approved_amount),
                    "approved_bdt": _fmt_bdt(claim.approved_amount),
                    "reason": claim.rejection_reason or "",
                    "decided_at": str(claim.decided_at or "") or None,
                },
            }
        }

    @http.route("/brand/claims/webhook", type="jsonrpc", auth="bearer", readonly=False)
    def claim_webhook(self, **kwargs):
        """T05: Inbound claim-status webhook for brand partner systems."""
        brand, err = resolve_brand(kwargs)
        if err:
            return err
        claim_no = kwargs.get("claim_no")
        event_type = kwargs.get("event_type")
        if not claim_no or not event_type:
            return _error("invalid_payload", "claim_no and event_type are required")

        claim = _su_env()["fix.warranty.claim"].search(
            [("claim_no", "=", claim_no), ("brand_id", "=", brand.id)], limit=1
        )
        if not claim:
            return _error("no_claim", "Claim not found for this brand")

        decision = kwargs.get("decision")
        reason = kwargs.get("reason", "")
        try:
            if event_type == "claim.approved" or decision == "approve":
                claim.action_decide(
                    approved=True,
                    reason=reason,
                    approved_amount=_amount(kwargs),
                    decided_by_id=request.env.user.id,
                )
            elif event_type == "claim.rejected" or decision == "reject":
                claim.action_decide(
                    approved=False, reason=reason, decided_by_id=request.env.user.id
                )
            elif event_type == "claim.in_review":
                claim.action_mark_in_review()
        except (UserError, ValidationError) as exc:
            return _error("event_rejected", str(exc))

        return {
            "status": "acknowledged",
            "claim_no": claim.claim_no,
            "state": claim.state,
            "event_type": event_type,
        }

    @http.route("/brand/reconciliation", type="jsonrpc", auth="bearer", readonly=False)
    def reconciliation(self, **kwargs):
        """Combined endpoint: record a remittance when `bank_ref` is
        present, otherwise the reconciliation view (T08: mismatches are
        FLAGGED, never auto-adjusted)."""
        brand, err = resolve_brand(kwargs)
        if err:
            return err
        if kwargs.get("bank_ref") and kwargs.get("claim_id"):
            return self._record_remittance(brand, **kwargs)
        claims = _su_env()["fix.warranty.claim"].search(
            [
                ("brand_id", "=", brand.id),
                ("state", "in", ("approved", "partially_approved", "remitted")),
            ],
            limit=100,
        )
        result = []
        for c in claims:
            if c.state == "remitted" or c.remittance_amount:
                mismatch, variance = _variance(c)  # money received vs approved
            elif c.remittance_advice_amount:
                diff = round(c.remittance_advice_amount - c.approved_amount, 2)
                mismatch = abs(diff) > 0.01  # the brand's advice vs approved
                variance = _fmt_bdt(diff) if mismatch else "0.00"
            else:
                mismatch, variance = False, "0.00"
            result.append(
                {
                    "claim_no": c.claim_no,
                    "state": c.state,
                    "expected_bdt": _fmt_bdt(c.approved_amount),
                    "received_bdt": _fmt_bdt(c.remittance_amount),
                    "advised_bdt": _fmt_bdt(c.remittance_advice_amount),
                    "mismatch": mismatch,
                    "variance_bdt": variance,
                }
            )
        return {"reconciliation": result, "total": len(result)}

    def _record_remittance(self, brand, **kwargs):
        claim = _brand_claim(brand, kwargs.get("claim_id"))
        if not claim:
            return _error("no_claim", "Claim not found for this brand")
        try:
            amount = float(kwargs.get("amount", 0.0))
        except (TypeError, ValueError):
            return _error("invalid_amount", "amount must be a number")
        try:
            # An ADVICE: the brand's word, not money received (M09-4).
            claim.action_record_remittance_advice(amount, str(kwargs.get("bank_ref", "")))
        except (UserError, ValidationError) as exc:
            return _error("remittance_rejected", str(exc))
        advised_diff = round(amount - claim.approved_amount, 2)
        mismatch = abs(advised_diff) > 0.01
        return {
            "remittance": {
                "claim_no": claim.claim_no,
                "state": claim.state,
                "expected_bdt": _fmt_bdt(claim.approved_amount),
                "advised_bdt": _fmt_bdt(claim.remittance_advice_amount),
                "received_bdt": _fmt_bdt(claim.remittance_amount),
                "mismatch": mismatch,  # flagged, never adjusted
                "variance_bdt": _fmt_bdt(advised_diff) if mismatch else "0.00",
                "status": "advice_noted",
            }
        }
