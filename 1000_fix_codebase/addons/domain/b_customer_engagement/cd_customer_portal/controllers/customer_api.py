# P01 Customer Self-Service API — the W4 contract endpoints (PP5).
#
# Serves booking, live tracking, device history, ownership transfer,
# estimate approval and the PDPA consent dashboard. Every write goes
# through the owning model's action methods — the portal passes through;
# validation and money are server-side (AS-09/AS-10). The customer is
# scoped to the session's partner (EA-05: a customer sees only their own
# devices, orders, estimates and consent rows).
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

import json


def _fmt_bdt(amount):
    """Format a monetary value as a BN-007-style South Asian-grouped string.
    The portal never does this math — it receives the string (AS-10)."""
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


def _scoped_partner(kwargs):
    """The customer this request acts for: the session user's partner,
    unless an internal user explicitly passes one (admin support view)."""
    partner_id = kwargs.get("partner_id")
    if partner_id:
        return int(partner_id)
    return request.env.user.partner_id.id


def _error(code, message):
    return {"error": {"code": code, "message": message}}


class CustomerApiController(http.Controller):
    """The P01 customer self-service portal API (W4 contract)."""

    # --- Devices & history ------------------------------------------------

    @http.route("/customer/devices", type="json", auth="user", readonly=True)
    def devices(self, **kwargs):
        """The customer's registered devices with warranty status and the
        M17 history timeline (T07)."""
        partner = _scoped_partner(kwargs)
        devices = request.env["fix.device"].search(
            [("owner_id", "=", partner)], limit=100)
        result = []
        for d in devices:
            history = request.env["fix.device.history"].search(
                [("device_id", "=", d.id)], limit=10, order="date desc")
            result.append({
                "id": d.id,
                "brand": d.brand_id.name or "",
                "model": d.device_model_id.name or "",
                "identifier": (d.imei_1 or d.serial_number or "")[:6] + "…",
                "warranty_status": d.warranty_status or "none",
                "state": d.state,
                "history": [{
                    "event": h.event_type,
                    "description": h.description,
                    "date": str(h.date or ""),
                } for h in history],
            })
        return {"devices": result, "total": len(result)}

    @http.route("/customer/ownership/transfer", type="json",
                auth="user", readonly=False)
    def ownership_transfer(self, **kwargs):
        """Transfer device ownership — T05: "portal P01 exposes this in
        Phase 5". The model writes the ownership trail (T05 audit)."""
        device_id = kwargs.get("device_id")
        to_partner_id = kwargs.get("to_partner_id")
        if not device_id or not to_partner_id:
            return _error("missing_params",
                          "device_id and to_partner_id are required")
        device = request.env["fix.device"].browse(int(device_id))
        if not device.exists():
            return _error("no_device", "Device not found")
        if device.owner_id.id != _scoped_partner(kwargs):
            return _error("not_owner",
                          "Only the current owner can transfer this device")
        try:
            device.action_transfer_ownership(int(to_partner_id))
        except (UserError, ValidationError) as exc:
            return _error("transfer_rejected", str(exc))
        return {"transferred": True, "device_id": device.id}

    # --- Booking & live tracking -------------------------------------------

    @http.route("/customer/bookings", type="json", auth="user",
                readonly=False)
    def bookings(self, **kwargs):
        """Combined endpoint: create when `fault_description` is present,
        otherwise list. (JSON-RPC routes are always POST; two routes at
        the same path conflict in Odoo's dispatcher.)"""
        if kwargs.get("fault_description"):
            return self._create_booking(**kwargs)
        return self._list_bookings(**kwargs)

    def _list_bookings(self, **kwargs):
        partner = _scoped_partner(kwargs)
        orders = request.env["fix.service.order"].search(
            [("customer_id", "=", partner)], limit=50,
            order="id desc")
        result = [{
            "id": o.id,
            "ref": o.name,
            "state": o.state,
            "category": o.order_category,
            "device": o.device_id.device_model_id.name or "",
            "fault": (o.fault_description or "")[:80],
            "technician": o.technician_id.name or "",
            "created": str(o.create_date or ""),
        } for o in orders]
        return {"bookings": result, "total": len(result)}

    def _create_booking(self, **kwargs):
        """<=3-step booking (DE-17: the Bengali copy lives portal-side;
        the data contract is language-neutral). Writes through the model —
        server-side validation is the gate (AS-09)."""
        partner = _scoped_partner(kwargs)
        device_id = kwargs.get("device_id")
        if not device_id:
            return _error("missing_device",
                          "device_id is required (M17 — every order needs "
                          "an identified device)")
        device = request.env["fix.device"].browse(int(device_id))
        if device.owner_id.id != partner:
            return _error("not_owner",
                          "Bookings are only accepted for your own devices")
        branch = device.branch_id or request.env["fix.branch"].search(
            [], limit=1)
        if not branch:
            return _error("no_branch", "No branch configured")
        try:
            order = request.env["fix.service.order"].create({
                "customer_id": partner,
                "device_id": int(device_id),
                "branch_id": branch.id,
                "order_category": kwargs.get("order_category", "standard"),
                "fault_description": kwargs.get("fault_description", ""),
                "priority": kwargs.get("priority", "normal"),
            })
        except (UserError, ValidationError) as exc:
            return _error("booking_rejected", str(exc))
        return {"booking": {"id": order.id, "ref": order.name,
                            "state": order.state}}

    @http.route("/customer/tracking", type="json", auth="user",
                readonly=True)
    def tracking(self, **kwargs):
        """Live tracking: order state, technician, SLA clocks. Polling
        today; the websocket upgrade (PP5 special requirement) rides this
        same payload shape."""
        order_id = kwargs.get("order_id")
        if not order_id:
            return _error("missing_order", "order_id is required")
        partner = _scoped_partner(kwargs)
        order = request.env["fix.service.order"].browse(int(order_id))
        if not order.exists():
            return _error("no_order", "Order not found")
        if order.customer_id.id != partner:
            return _error("not_your_order",
                          "This order belongs to another customer")
        return {"tracking": {
            "id": order.id,
            "ref": order.name,
            "state": order.state,
            "technician": order.technician_id.name or "",
            "eta_resolution": str(order.sla_resolution_deadline or ""),
            "sla_paused": order.sla_clock_paused,
            "stage_history": [],  # work-order stages ride M03; the
                                  # prototype pill states map 1:1 to `state`
        }}

    # --- Estimate approval ---------------------------------------------------

    @http.route("/customer/estimates", type="json", auth="user",
                readonly=False)
    def estimates(self, **kwargs):
        """Combined endpoint: act when `estimate_id`+`action` are present,
        otherwise list the estimates on the customer's orders."""
        if kwargs.get("estimate_id") and kwargs.get("action"):
            return self._act_on_estimate(**kwargs)
        return self._list_estimates(**kwargs)

    def _list_estimates(self, **kwargs):
        partner = _scoped_partner(kwargs)
        orders = request.env["fix.service.order"].search(
            [("customer_id", "=", partner)], limit=50)
        estimates = request.env["fix.estimate"].search(
            [("order_id", "in", orders.ids), ("state", "=", "sent")],
            limit=50, order="id desc")
        result = [{
            "id": e.id,
            "order_ref": e.order_id.name,
            "version": e.version,
            "grand_total_bdt": _fmt_bdt(e.grand_total),
            "expiry": str(e.expiry_date or ""),
            "customer_approval_ref": e.customer_approval_ref or "",
        } for e in estimates]
        return {"estimates": result, "total": len(result)}

    def _act_on_estimate(self, **kwargs):
        """The customer's documented approval (BRU-SRM-07) then the
        model's own approve action — the hard gates stay server-side.
        A gate rejection is RETURNED, never warned about in the portal."""
        action = kwargs.get("action")
        if action not in ("approve", "reject"):
            return _error("invalid_action",
                          "action must be approve|reject")
        estimate = request.env["fix.estimate"].browse(
            int(kwargs.get("estimate_id")))
        if not estimate.exists():
            return _error("no_estimate", "Estimate not found")
        partner = _scoped_partner(kwargs)
        if estimate.order_id.customer_id.id != partner:
            return _error("not_your_estimate",
                          "This estimate belongs to another customer")
        approval_ref = kwargs.get("approval_ref", "")
        try:
            if action == "reject":
                estimate.action_reject()
            else:
                if not approval_ref:
                    return _error(
                        "missing_approval_ref",
                        "BRU-SRM-07: a documented approval reference is "
                        "required (OTP id, e-sign ref or signed form ID)")
                estimate.write({"customer_approval_ref": approval_ref})
                estimate.action_approve()  # enforces the >BDT 5k/25k gates
        except (UserError, ValidationError) as exc:
            return _error("estimate_rejected", str(exc))
        return {"estimate": {"id": estimate.id, "state": estimate.state}}

    # --- PDPA consent dashboard ----------------------------------------------

    @http.route("/customer/consent", type="json", auth="user",
                readonly=False)
    def consent(self, **kwargs):
        """Combined endpoint: grant/withdraw when `action` is present,
        otherwise the full per-channel dashboard (status visible — the
        PP0 audit gap closed)."""
        if kwargs.get("action"):
            return self._act_on_consent(**kwargs)
        partner = _scoped_partner(kwargs)
        rows = request.env["fix.consent"].search(
            [("partner_id", "=", partner)], limit=100,
            order="channel, date_granted desc")
        result = [{
            "id": c.id,
            "channel": c.channel,
            "state": c.state,
            "date_granted": str(c.date_granted or ""),
            "date_withdrawn": str(c.date_withdrawn or "") or None,
            "proof": c.proof or "",
        } for c in rows]
        return {"consents": result, "total": len(result)}

    def _act_on_consent(self, **kwargs):
        action = kwargs.get("action")
        if action not in ("grant", "withdraw"):
            return _error("invalid_action", "action must be grant|withdraw")
        channel = kwargs.get("channel")
        if channel not in ("sms", "whatsapp", "email", "push", "marketing"):
            return _error("invalid_channel",
                          "channel must be sms|whatsapp|email|push|marketing")
        partner = _scoped_partner(kwargs)
        Consent = request.env["fix.consent"]
        if action == "withdraw":
            rows = Consent.search([("partner_id", "=", partner),
                                   ("channel", "=", channel),
                                   ("state", "=", "granted")])
            if not rows:
                return _error("nothing_to_withdraw",
                              "No granted consent on this channel")
            rows.action_withdraw()  # keeps the record forever (BTRC/DND)
            return {"consent": {"channel": channel, "state": "withdrawn"}}
        proof = kwargs.get("proof", "")
        if not proof:
            return _error("missing_proof",
                          "A granted consent needs its proof reference — "
                          "an unverifiable grant is not a grant")
        row = Consent.create({
            "partner_id": partner,
            "channel": channel,
            "state": "granted",
            "proof": proof,
            "source": "web",
        })
        return {"consent": {"id": row.id, "channel": channel,
                            "state": row.state}}
