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

from ..models.fix_partner import CONSENT_METHODS, EARNING_STATES


def _fmt_bdt(amount):
    """BN-007 South Asian grouping (``1,23,45,678.00``) - the portal receives the
    string (AS-10). (The former int()/fraction split rounded 1.999 down to
    "1.00" and turned -1234.5 into "-1,2340.50".)"""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    whole_str, frac_str = f"{abs(n):.2f}".split(".")
    if len(whole_str) > 3:
        rest = whole_str[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        groups.insert(0, rest)  # 1-2 leading digits: len(whole_str) > 3 leaves rest non-empty
        whole_str = ",".join(groups) + "," + whole_str[-3:]
    sign = "-" if n < 0 else ""
    return f"{sign}{whole_str}.{frac_str}"


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _partner_profile(kwargs):
    """The referring partner this request acts for. EA-05: scoped to the
    session partner's profile; an internal user may pass partner_profile_id
    (partnership support view).
    Anti-IDOR: Portal users cannot override session partner binding."""
    user = request.env.user
    profile_id = kwargs.get("partner_profile_id")
    if profile_id:
        profile = request.env["fix.partner"].browse(_to_int(profile_id) or 0).exists()
        if not profile:
            return None
        # ownership is decided on the raw row: a foreign profile is "none", not an AccessError
        if not user.has_group("base.group_user") and profile.sudo().partner_id != user.partner_id:
            return None
        return profile
    partner = request.env.user.partner_id
    profile = request.env["fix.partner"].search([("partner_id", "=", partner.id)], limit=1)
    # A04 ERP audit M40-F9 (BRU-PCM-13): a suspended, dormant or exiting
    # partner's portal user acts for no profile.
    if profile and user.share and profile.sudo().state not in EARNING_STATES:
        return None
    return profile or None


class PartnerApiController(http.Controller):
    """The P12 partner & referral portal API (W4 contract)."""

    @http.route("/partner/profile", type="jsonrpc", auth="user", readonly=True)
    def profile(self, **kwargs):
        """The partner's own standing: type, territory, rate, state."""
        profile = _partner_profile(kwargs)
        if not profile:
            return _error(
                "no_partner_profile",
                "No partner profile for this account — " "onboarding is internal (M53)",
            )
        return {
            "partner": {
                "id": profile.id,
                "name": profile.name,
                "partner_type": profile.partner_type,
                "territory": profile.territory or "",
                "commission_rate": profile.commission_rate,
                "state": profile.state,
                "kyc_verified": bool(profile.kyc_verified),
                "email": profile.partner_id.email or "",
                "phone": profile.partner_id.phone or "",
            }
        }

    @http.route("/partner/referrals", type="jsonrpc", auth="user", readonly=False)
    def referrals(self, **kwargs):
        """Combined endpoint: submit when `referred_name` is present,
        otherwise list (tracking)."""
        profile = _partner_profile(kwargs)
        if not profile:
            return _error("no_partner_profile", "No partner profile for this account")
        if kwargs.get("referred_name"):
            return self._submit_referral(profile, **kwargs)
        # A04 ERP audit M40-F8: what the partner itself submitted is all it
        # sees - the lead as it typed it, never the party master's record.
        leads = (
            request.env["fix.partner.lead"]
            .sudo()
            .search([("partner_id", "=", profile.id)], limit=100, order="id desc")
        )
        rows = request.env["fix.referral"].search(
            [("partner_id", "=", profile.id)], limit=100, order="id desc"
        )
        typed = {lead.referral_id.id: lead.customer_name for lead in leads if lead.referral_id}
        service = {
            lead.referral_id.id: (lead.service_interest or "") for lead in leads if lead.referral_id
        }
        result = [
            {
                "id": r.id,
                "name": r.name,
                "referred": typed.get(r.id, ""),
                "service_interest": service.get(r.id, ""),
                "state": r.state,
                "commission_bdt": _fmt_bdt(r.commission_amount),
            }
            for r in rows
        ]
        lead_rows = [
            {
                "lead": lead.name,
                "referred": lead.customer_name,
                "state": lead.state,
                "loss_reason": lead.loss_reason or "",
                "service_interest": lead.service_interest or "",
                "attributed_at": str(lead.attributed_at or ""),
                "attribution_expires_on": str(lead.attribution_expires_on or ""),
                "converted_at": str(lead.converted_at or ""),
                "referral": lead.referral_id.name or "",
                "commission_bdt": _fmt_bdt(lead.referral_id.commission_amount)
                if lead.referral_id
                else "0.00",
            }
            for lead in leads
        ]
        return {"referrals": result, "total": len(result), "leads": lead_rows}

    def _submit_referral(self, profile, **kwargs):
        """A04 ERP audit M40-F8/F10: a partner submits a LEAD - the customer's
        name and phone as the partner knows them, and the customer's consent
        (BRU-PCM-06). The portal never names an existing party: it used to take
        any res.partner id, echo that party's name back (a lookup of every
        customer) and reserve the customer against other partners (first in
        wins). The company links the lead to the customer when it converts."""
        if profile.state not in EARNING_STATES:
            return _error("partner_not_active", "This partner account is not active.")
        if kwargs.get("referred_partner_id"):
            return _error(
                "referred_party_not_accepted",
                "Name and phone the customer: the portal does not take party ids.",
            )
        phone = (kwargs.get("referred_phone") or "").strip()
        if not phone:
            return _error("missing_phone", "referred_phone is required")
        consent = kwargs.get("consent_given") in (True, "true", "1", 1, "yes")
        method = kwargs.get("consent_method")
        if not consent or method not in dict(CONSENT_METHODS):
            return _error(
                "missing_consent",
                "Record the customer's consent and how it was given (consent_given, "
                "consent_method: %s) - BRU-PCM-06." % ", ".join(dict(CONSENT_METHODS)),
            )
        try:
            with request.env.cr.savepoint():  # a refused lead leaves no row behind
                # sudo after the profile check: the partner is the session's own
                # profile and every field is whitelisted here
                lead = (
                    request.env["fix.partner.lead"]
                    .sudo()
                    .create(
                        {
                            "partner_id": profile.id,
                            "company_id": profile.company_id.id,
                            "customer_name": str(kwargs.get("referred_name"))[:120],
                            "customer_phone": phone[:32],
                            "customer_email": (kwargs.get("referred_email") or "")[:120] or False,
                            "service_interest": (kwargs.get("service_interest") or "")[:120]
                            or False,
                            "consent_given": True,
                            "consent_method": method,
                        }
                    )
                )
        except (UserError, ValidationError) as exc:
            return _error("referral_rejected", str(exc))
        return {"lead": {"name": lead.name, "state": lead.state}}

    @http.route("/partner/commissions", type="jsonrpc", auth="user", readonly=True)
    def commissions(self, **kwargs):
        """The commission statement: referral ledger rows with earned
        totals. fix.referral IS the partner commission record (M53's
        commission.earned events originate from it)."""
        profile = _partner_profile(kwargs)
        if not profile:
            return _error("no_partner_profile", "No partner profile for this account")
        rows = request.env["fix.referral"].search(
            [("partner_id", "=", profile.id)], limit=200, order="id desc"
        )
        # The referral row is the commission record; the customer name the
        # partner typed lives on the lead that fed it (M40-F8), so the
        # statement shows that name, not the internal party master.
        leads = request.env["fix.partner.lead"].sudo().search([("partner_id", "=", profile.id)])
        typed = {lead.referral_id.id: lead.customer_name for lead in leads if lead.referral_id}
        service = {
            lead.referral_id.id: (lead.service_interest or "") for lead in leads if lead.referral_id
        }
        lines = []
        for r in rows:
            if not r.commission_amount:
                continue
            # M40-F8: the party master's name is NEVER echoed. The rebuild's
            # ACL-guarded fallback could not protect it - base portal ACLs let
            # a portal user read every partner, so the guard never fired (the
            # A04 regression test caught the leak on the clean fix_test,
            # 2026-11-24). A company-created referral without a portal lead
            # shows its reference only, exactly like referrals() above.
            name = typed.get(r.id) or ""
            lines.append(
                {
                    "referral": r.name,
                    "referred": name,
                    "service_interest": service.get(r.id, ""),
                    "state": r.state,
                    "referred_on": str(r.referred_on or ""),
                    "base_amount_bdt": _fmt_bdt(r.base_amount),
                    "commission_rate": r.commission_rate,
                    "commission_bdt": _fmt_bdt(r.commission_amount),
                }
            )
        total = sum(r.commission_amount for r in rows)
        return {
            "commissions": {
                "lines": lines,
                "earned_total_bdt": _fmt_bdt(total),
            }
        }
