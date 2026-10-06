# P12 Partner & Referral API — the W4 contract endpoints (PP5).
#
# Referral submission (the link attribution lands with the referral's
# own name/referred-party pair), referral tracking, and the commission
# statement built from the referral ledger (state submitted→converted→
# commissioned; fix.referral IS the partner commission record). Money
# is backend-computed BN-007 strings (AS-10); conversions and
# commissioning ride the model's action methods (AS-09).
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


def _partner_profile(kwargs):
    """The referring partner this request acts for. EA-05: scoped to the
    session partner's profile; an internal user may pass partner_profile_id
    (partnership support view)."""
    profile_id = kwargs.get("partner_profile_id")
    if profile_id:
        profile = request.env["fix.partner"].browse(int(profile_id))
        return profile if profile.exists() else None
    partner = request.env.user.partner_id
    return request.env["fix.partner"].search(
        [("partner_id", "=", partner.id)], limit=1) or None


class PartnerApiController(http.Controller):
    """The P12 partner & referral portal API (W4 contract)."""

    @http.route("/partner/profile", type="json", auth="user", readonly=True)
    def profile(self, **kwargs):
        """The partner's own standing: type, territory, rate, state."""
        profile = _partner_profile(kwargs)
        if not profile:
            return _error("no_partner_profile",
                          "No partner profile for this account — "
                          "onboarding is internal (M53)")
        return {"partner": {
            "id": profile.id,
            "name": profile.name,
            "partner_type": profile.partner_type,
            "territory": profile.territory or "",
            "commission_rate": profile.commission_rate,
            "state": profile.state,
        }}

    @http.route("/partner/referrals", type="json", auth="user",
                readonly=False)
    def referrals(self, **kwargs):
        """Combined endpoint: submit when `referred_name` is present,
        otherwise list (tracking)."""
        profile = _partner_profile(kwargs)
        if not profile:
            return _error("no_partner_profile",
                          "No partner profile for this account")
        if kwargs.get("referred_name"):
            return self._submit_referral(profile, **kwargs)
        rows = request.env["fix.referral"].search(
            [("partner_id", "=", profile.id)], limit=100, order="id desc")
        result = [{
            "id": r.id,
            "name": r.name,
            "referred": r.referred_partner_id.name or "",
            "state": r.state,
            "commission_bdt": _fmt_bdt(r.commission_amount),
        } for r in rows]
        return {"referrals": result, "total": len(result)}

    def _submit_referral(self, profile, **kwargs):
        """Referral submission: who was referred (the attribution pair).
        The model gates duplicate/self referrals server-side (AS-09)."""
        referred_partner_id = kwargs.get("referred_partner_id")
        if not referred_partner_id:
            return _error("missing_referred",
                          "referred_partner_id is required "
                          "(attribution lands on the referred party)")
        referred = request.env["res.partner"].browse(int(referred_partner_id))
        if not referred.exists():
            return _error("no_referred_party", "Referred party not found")
        try:
            referral = request.env["fix.referral"].create({
                "partner_id": profile.id,
                "referred_partner_id": int(referred_partner_id),
                "name": kwargs.get("referred_name"),
            })
        except (UserError, ValidationError) as exc:
            return _error("referral_rejected", str(exc))
        return {"referral": {"id": referral.id, "state": referral.state}}

    @http.route("/partner/commissions", type="json", auth="user",
                readonly=True)
    def commissions(self, **kwargs):
        """The commission statement: referral ledger rows with earned
        totals. fix.referral IS the partner commission record (M53's
        commission.earned events originate from it)."""
        profile = _partner_profile(kwargs)
        if not profile:
            return _error("no_partner_profile",
                          "No partner profile for this account")
        rows = request.env["fix.referral"].search(
            [("partner_id", "=", profile.id)], limit=200, order="id desc")
        lines = [{
            "referral": r.name,
            "referred": r.referred_partner_id.name or "",
            "state": r.state,
            "commission_bdt": _fmt_bdt(r.commission_amount),
        } for r in rows if r.commission_amount]
        total = sum(r.commission_amount for r in rows)
        return {"commissions": {
            "lines": lines,
            "earned_total_bdt": _fmt_bdt(total),
        }}
