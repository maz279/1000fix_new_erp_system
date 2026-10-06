# P08 Brand Partner API — the W4 contract endpoints (PP5).
#
# Claim submission status, decision capture and remittance
# reconciliation for the brands 1000FiX recovers warranty costs from.
# BRAND ISOLATION: brand_id is REQUIRED on every endpoint — a claim
# outside the caller's brand is indistinguishable from a claim that
# does not exist. Decisions ride fix.warranty.claim.action_decide
# (SoD-11 companion lives with the callers); reconciliation surfaces
# FLAGGED mismatches, never auto-adjusts (T08).
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

import json


def _fmt_bdt(amount):
    """BN-007 South Asian grouping — the portal receives the string (AS-10)."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    whole = int(n)
    frac = f"{n - whole:.2f}"[1:]
    s = str(whole)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        return ",".join(parts) + "," + last3 + frac
    return s + frac


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _brand_scope(kwargs):
    """Per-brand isolation (PP5 special requirement): brand_id is required.
    Without it the surface refuses rather than defaulting to all-brands —
    an unscoped claim list IS the isolation breach."""
    brand_id = kwargs.get("brand_id")
    if not brand_id:
        return None
    return int(brand_id)


class BrandApiController(http.Controller):
    """The P08 brand partner portal API (W4 contract)."""

    @http.route("/brand/claims", type="json", auth="user", readonly=False)
    def claims(self, **kwargs):
        """Combined endpoint: decide when `claim_id`+`decision` are present,
        otherwise list. brand_id is REQUIRED (isolation)."""
        brand_id = _brand_scope(kwargs)
        if not brand_id:
            return _error("missing_brand",
                          "brand_id is required (per-brand isolation)")
        # the dispatcher passes every param as a kwarg — drop brand_id so
        # the helpers don't receive it twice (positional + kwargs)
        kwargs.pop("brand_id", None)
        if kwargs.get("claim_id") and kwargs.get("decision"):
            return self._decide_claim(brand_id, **kwargs)
        return self._list_claims(brand_id, **kwargs)

    def _list_claims(self, brand_id, **kwargs):
        domain = [("brand_id", "=", brand_id)]
        state = kwargs.get("state")
        if state:
            domain.append(("state", "=", state))
        claims = request.env["fix.warranty.claim"].search(
            domain, limit=100, order="id desc")
        result = [{
            "id": c.id,
            "claim_no": c.claim_no,
            "state": c.state,
            "amount_bdt": _fmt_bdt(c.claim_amount),
            "submitted_at": str(c.submitted_at or "") or None,
            "decided_at": str(c.decided_at or "") or None,
            "rejection_reason": c.rejection_reason or "",
            "evidence_complete": c.evidence_complete,
            "missing_evidence": c.missing_evidence or "",
        } for c in claims]
        return {"claims": result, "total": len(result)}

    def _decide_claim(self, brand_id, **kwargs):
        """The brand's decision (approve/reject with reason). Only a
        SUBMITTED claim in this brand can be decided."""
        decision = kwargs.get("decision")
        if decision not in ("approve", "reject"):
            return _error("invalid_decision",
                          "decision must be approve|reject")
        claim = request.env["fix.warranty.claim"].browse(
            int(kwargs.get("claim_id")))
        if not claim.exists() or claim.brand_id.id != brand_id:
            # isolation: another brand's claim "does not exist"
            return _error("no_claim", "Claim not found for this brand")
        try:
            claim.action_decide(
                approved=(decision == "approve"),
                reason=kwargs.get("reason", ""))
        except (UserError, ValidationError) as exc:
            return _error("decision_rejected", str(exc))
        return {"claim": {"id": claim.id, "claim_no": claim.claim_no,
                          "state": claim.state}}

    @http.route("/brand/claims/status", type="json", auth="user",
                readonly=True)
    def claim_status(self, **kwargs):
        """Single-claim status (webhook-fed path shape: claim_no + brand)."""
        brand_id = _brand_scope(kwargs)
        if not brand_id:
            return _error("missing_brand",
                          "brand_id is required (per-brand isolation)")
        claim_no = kwargs.get("claim_no")
        if not claim_no:
            return _error("missing_claim_no", "claim_no is required")
        claim = request.env["fix.warranty.claim"].search(
            [("claim_no", "=", claim_no),
             ("brand_id", "=", brand_id)], limit=1)
        if not claim:
            return _error("no_claim", "Claim not found for this brand")
        return {"claim": {
            "claim_no": claim.claim_no,
            "state": claim.state,
            "amount_bdt": _fmt_bdt(claim.claim_amount),
            "remitted_bdt": _fmt_bdt(claim.remittance_amount),
            "decision": {
                "approved": claim.state in ("approved", "remitted"),
                "reason": claim.rejection_reason or "",
                "decided_at": str(claim.decided_at or "") or None,
            },
        }}

    @http.route("/brand/reconciliation", type="json", auth="user",
                readonly=False)
    def reconciliation(self, **kwargs):
        """Combined endpoint: record a remittance when `bank_ref` is
        present, otherwise the reconciliation view (T08: mismatches are
        FLAGGED, never auto-adjusted)."""
        brand_id = _brand_scope(kwargs)
        if not brand_id:
            return _error("missing_brand",
                          "brand_id is required (per-brand isolation)")
        kwargs.pop("brand_id", None)
        if kwargs.get("bank_ref") and kwargs.get("claim_id"):
            return self._record_remittance(brand_id, **kwargs)
        claims = request.env["fix.warranty.claim"].search(
            [("brand_id", "=", brand_id),
             ("state", "in", ("approved", "remitted"))], limit=100)
        result = []
        for c in claims:
            mismatch = (c.state == "remitted"
                        and abs(c.remittance_amount - c.claim_amount) > 0.01)
            result.append({
                "claim_no": c.claim_no,
                "state": c.state,
                "expected_bdt": _fmt_bdt(c.claim_amount),
                "received_bdt": _fmt_bdt(c.remittance_amount),
                "mismatch": mismatch,
            })
        return {"reconciliation": result, "total": len(result)}

    def _record_remittance(self, brand_id, **kwargs):
        claim = request.env["fix.warranty.claim"].browse(
            int(kwargs.get("claim_id")))
        if not claim.exists() or claim.brand_id.id != brand_id:
            return _error("no_claim", "Claim not found for this brand")
        try:
            claim.action_record_remittance(
                float(kwargs.get("amount", 0.0)),
                str(kwargs.get("bank_ref", "")))
        except (UserError, ValidationError) as exc:
            return _error("remittance_rejected", str(exc))
        mismatch = abs(claim.remittance_amount - claim.claim_amount) > 0.01
        return {"remittance": {
            "claim_no": claim.claim_no,
            "state": claim.state,
            "expected_bdt": _fmt_bdt(claim.claim_amount),
            "received_bdt": _fmt_bdt(claim.remittance_amount),
            "mismatch": mismatch,  # flagged, never adjusted
        }}
