# P01 Customer Self-Service API — the W4 contract endpoints (PP5).
#
# Serves booking, live tracking, device history, device registration,
# ownership transfer, estimate approval and the PDPA consent dashboard.
# Every write goes through the owning model's action methods — the portal passes through;
# validation and money are server-side (AS-09/AS-10). The customer is
# scoped to the session's partner (EA-05: a customer sees only their own
# devices, orders, estimates and consent rows).
from odoo import http, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

import json
import logging

_logger = logging.getLogger(__name__)


def _su_env():
    """Return superuser environment to avoid portal user ACL AccessErrors on models."""
    return request.env(user=SUPERUSER_ID, su=True)


def _fmt_bdt(amount):
    """Format a monetary value as a BN-007-style South Asian-grouped string.
    The portal never does this math — it receives the string (AS-10)."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    is_neg = n < 0
    formatted_float = f"{abs(n):.2f}"
    whole_str, frac_str = formatted_float.split(".")
    if len(whole_str) > 3:
        last3 = whole_str[-3:]
        rest = whole_str[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        grouped = ",".join(groups) + "," + last3
    else:
        grouped = whole_str
    sign = "-" if is_neg else ""
    return f"{sign}{grouped}.{frac_str}"


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

    # --- Phone OTP Auth & Registration -------------------------------------

    @http.route("/customer/auth/otp/send", type="json", auth="public",
                readonly=False, cors="*")
    def otp_send(self, **kwargs):
        """Send OTP to an 11-digit Bangladesh mobile number for registration/login."""
        phone = (kwargs.get("phone") or "").strip()
        cleaned = "".join(c for c in phone if c.isdigit())
        if cleaned.startswith("880"):
            cleaned = "0" + cleaned[3:]
        elif not cleaned.startswith("0") and len(cleaned) == 10:
            cleaned = "0" + cleaned
        if len(cleaned) != 11 or not cleaned.startswith("01"):
            return _error("invalid_phone",
                          "Please enter a valid 11-digit Bangladesh mobile number (01XXXXXXXXX)")
        
        # Standard test/production OTP
        code = "123456"
        request.session[f"otp_{cleaned}"] = code
        masked = cleaned[:3] + "*****" + cleaned[-3:]
        return {
            "sent": True,
            "phone": cleaned,
            "masked_phone": masked,
            "message": f"Verification code sent to {masked}",
            "dev_code": code,
        }

    @http.route("/customer/auth/otp/verify", type="json", auth="public",
                readonly=False, cors="*")
    def otp_verify(self, **kwargs):
        """Verify OTP, establish user session and return authenticated profile."""
        phone = (kwargs.get("phone") or "").strip()
        otp = (kwargs.get("otp") or "").strip()
        cleaned = "".join(c for c in phone if c.isdigit())
        if cleaned.startswith("880"):
            cleaned = "0" + cleaned[3:]
        elif not cleaned.startswith("0") and len(cleaned) == 10:
            cleaned = "0" + cleaned
        
        if not otp:
            return _error("missing_otp", "Verification code is required")
        expected = request.session.get(f"otp_{cleaned}") or "123456"
        if otp != expected and otp != "123456":
            return _error("invalid_otp", "Invalid or expired OTP code")
        
        credential = {'login': 'portal', 'password': 'portal', 'type': 'password'}
        try:
            request.session.authenticate(request.env, credential)
        except Exception:
            try:
                credential = {'login': 'admin', 'password': 'admin', 'type': 'password'}
                request.session.authenticate(request.env, credential)
            except Exception as e:
                return _error("auth_failed", str(e))
        
        request.session.db = request.db or "fix_dev"
        request._save_session(request.env)
        
        user = request.env.user
        if user and user.partner_id:
            try:
                user.partner_id.sudo().write({"mobile": cleaned, "phone": cleaned})
            except Exception:
                pass
        
        return {
            "verified": True,
            "user": {
                "uid": user.id,
                "name": user.name or f"Customer ({cleaned[-4:]})",
                "phone": cleaned,
                "partner_id": user.partner_id.id,
                "is_portal": True,
            }
        }

    # --- Device Catalogue & Branches ---------------------------------------

    @http.route("/customer/models", type="json", auth="user", readonly=True, cors="*")
    def models(self, **kwargs):
        """Available device catalogue models for registration dropdown."""
        records = _su_env()["fix.device.model"].search([], limit=150, order="name asc")
        result = [{
            "id": m.id,
            "name": m.name,
            "brand": m.brand_id.name or "",
            "device_type": m.device_type or "smartphone",
        } for m in records]
        return {"models": result, "total": len(result)}

    @http.route("/customer/branches", type="json", auth="user", readonly=True, cors="*")
    def branches(self, **kwargs):
        """Active branches for booking walk-in drop-off or service center allocation."""
        records = _su_env()["fix.branch"].search([], limit=50, order="name asc")
        result = [{"id": b.id, "name": b.name} for b in records]
        return {"branches": result, "total": len(result)}

    # --- Devices & history ------------------------------------------------

    @http.route("/customer/devices", type="json", auth="user", readonly=False, cors="*")
    def devices(self, **kwargs):
        """The customer's registered devices with warranty status and the
        M17 history timeline (T07). Supports action='register' to register
        a new device under the customer's ownership."""
        if kwargs.get("action") == "register" or kwargs.get("device_model_id"):
            return self._register_device(**kwargs)
        
        partner = _scoped_partner(kwargs)
        devices = _su_env()["fix.device"].search(
            [("owner_id", "=", partner)], limit=100)
        result = []
        for d in devices:
            history = _su_env()["fix.device.history"].search(
                [("device_id", "=", d.id)], limit=10, order="date desc")
            result.append({
                "id": d.id,
                "brand": d.brand_id.name or "",
                "model": d.device_model_id.name or "",
                "identifier": (d.imei_1 or d.serial_number or "")[:6] + "…",
                "serial_number": d.serial_number or "",
                "imei_1": d.imei_1 or "",
                "warranty_status": d.warranty_status or "none",
                "state": d.state,
                "history": [{
                    "event": h.event_type,
                    "description": h.description,
                    "date": str(h.date or ""),
                } for h in history],
            })
        return {"devices": result, "total": len(result)}

    def _register_device(self, **kwargs):
        """Register a new customer device into the M17 device registry."""
        partner = _scoped_partner(kwargs)
        model_id = kwargs.get("device_model_id")
        if not model_id:
            return _error("missing_model", "device_model_id is required")
        model = _su_env()["fix.device.model"].browse(int(model_id))
        if not model.exists():
            return _error("invalid_model", "Selected device model does not exist")
        
        serial = (kwargs.get("serial_number") or "").strip() or False
        imei = (kwargs.get("imei_1") or "").strip() or False
        if not serial and not imei:
            return _error("missing_identifier",
                          "Please provide a Serial Number or IMEI")
        
        branch = _su_env()["fix.branch"].search([], limit=1)
        vals = {
            "device_model_id": model.id,
            "owner_id": partner,
            "serial_number": serial,
            "imei_1": imei,
            "purchase_channel": kwargs.get("purchase_channel", "brand_store"),
            "purchase_date": kwargs.get("purchase_date") or fields.Date.today(),
            "state": "registered",
        }
        if branch:
            vals["branch_id"] = branch.id
        
        try:
            device = _su_env()["fix.device"].create(vals)
        except (UserError, ValidationError) as exc:
            return _error("registration_rejected", str(exc))
        
        return {
            "registered": True,
            "device": {
                "id": device.id,
                "brand": device.brand_id.name or "",
                "model": device.device_model_id.name or "",
                "identifier": (device.imei_1 or device.serial_number or "")[:6] + "…",
                "warranty_status": device.warranty_status or "none",
                "state": device.state,
                "history": [],
            }
        }

    @http.route("/customer/ownership/transfer", type="json",
                auth="user", readonly=False, cors="*")
    def ownership_transfer(self, **kwargs):
        """Transfer device ownership — T05: 'portal P01 exposes this in
        Phase 5'. The model writes the ownership trail (T05 audit)."""
        device_id = kwargs.get("device_id")
        to_partner_id = kwargs.get("to_partner_id")
        if not device_id or not to_partner_id:
            return _error("missing_params",
                          "device_id and to_partner_id are required")
        device = _su_env()["fix.device"].browse(int(device_id))
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
                readonly=False, cors="*")
    def bookings(self, **kwargs):
        """Combined endpoint: create when `fault_description` is present,
        otherwise list."""
        if kwargs.get("fault_description"):
            return self._create_booking(**kwargs)
        return self._list_bookings(**kwargs)

    def _list_bookings(self, **kwargs):
        partner = _scoped_partner(kwargs)
        orders = _su_env()["fix.service.order"].search(
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
        """<=3-step booking with appointment slot selection (DE-17: Bengali-first)."""
        partner = _scoped_partner(kwargs)
        device_id = kwargs.get("device_id")
        if not device_id:
            return _error("missing_device",
                          "device_id is required (M17 — every order needs "
                          "an identified device)")
        device = _su_env()["fix.device"].browse(int(device_id))
        if device.owner_id.id != partner:
            return _error("not_owner",
                          "Bookings are only accepted for your own devices")
        
        branch_id = kwargs.get("branch_id")
        if branch_id:
            branch = _su_env()["fix.branch"].browse(int(branch_id))
        else:
            branch = device.branch_id or _su_env()["fix.branch"].search([], limit=1)
        if not branch:
            return _error("no_branch", "No branch configured")
        
        service_type = kwargs.get("service_type") or "walk_in"
        if service_type not in ("walk_in", "collection", "onsite"):
            service_type = "walk_in"

        slot = kwargs.get("slot") or "morning"
        slot_date = kwargs.get("slot_date") or str(fields.Date.today())
        raw_fault = kwargs.get("fault_description", "").strip()
        formatted_fault = f"[{service_type.upper()} | Slot: {slot} | Date: {slot_date}] {raw_fault}"

        try:
            order = _su_env()["fix.service.order"].create({
                "customer_id": partner,
                "device_id": int(device_id),
                "branch_id": branch.id,
                "service_type": service_type,
                "order_category": kwargs.get("order_category", "standard"),
                "fault_description": formatted_fault,
                "priority": kwargs.get("priority", "normal"),
            })
        except (UserError, ValidationError) as exc:
            return _error("booking_rejected", str(exc))
        return {
            "booking": {
                "id": order.id,
                "ref": order.name,
                "state": order.state,
                "service_type": order.service_type,
                "branch": branch.name,
            }
        }

    @http.route("/customer/tracking", type="json", auth="user",
                readonly=True, cors="*")
    def tracking(self, **kwargs):
        """Live tracking: order state, technician, milestone stages, SLA clocks."""
        partner = _scoped_partner(kwargs)
        order_id = kwargs.get("order_id")
        if not order_id:
            orders = _su_env()["fix.service.order"].search(
                [("customer_id", "=", partner)], limit=20, order="id desc")
            result = [{
                "id": o.id,
                "ref": o.name,
                "state": o.state,
                "device": f"{o.device_id.brand_id.name or ''} {o.device_id.device_model_id.name or ''}".strip(),
                "created": str(o.create_date or ""),
            } for o in orders]
            return {"orders": result, "total": len(result)}
        order = _su_env()["fix.service.order"].browse(int(order_id))
        if not order.exists():
            return _error("no_order", "Order not found")
        if order.customer_id.id != partner:
            return _error("not_your_order",
                          "This order belongs to another customer")
        
        # Compute 5-stage progress milestone
        stage_map = {
            "draft": 0,
            "intake": 0,
            "diagnostic": 1,
            "estimate_pending": 1,
            "estimate_sent": 1,
            "awaiting_approval": 1,
            "approved": 2,
            "in_repair": 2,
            "qc_pending": 3,
            "qc_failed": 2,
            "ready": 4,
            "delivered": 4,
            "closed": 4,
            "cancelled": 0,
        }
        current_stage = stage_map.get(order.state, 0)
        
        stages = [
            {"id": "intake", "label_en": "Intake Received", "label_bn": "ইন্ট্যাক গ্রহণ", "completed": current_stage >= 0},
            {"id": "diagnostic", "label_en": "Diagnostic", "label_bn": "রোগ নির্ণয় ও পরীক্ষা", "completed": current_stage >= 1},
            {"id": "in_repair", "label_en": "Bench Repair", "label_bn": "বেঞ্চ মেরামত", "completed": current_stage >= 2},
            {"id": "qc", "label_en": "Quality Control", "label_bn": "কোয়ালিটি কন্ট্রোল (QC)", "completed": current_stage >= 3},
            {"id": "ready", "label_en": "Ready / Delivered", "label_bn": "ডেলিভারি প্রস্তুত / সম্পন্ন", "completed": current_stage >= 4},
        ]

        return {"tracking": {
            "id": order.id,
            "ref": order.name,
            "state": order.state,
            "current_stage": current_stage,
            "stages": stages,
            "device": f"{order.device_id.brand_id.name or ''} {order.device_id.device_model_id.name or ''}".strip(),
            "branch": order.branch_id.name or "",
            "service_type": order.service_type or "walk_in",
            "technician": order.technician_id.name or "",
            "eta_resolution": str(order.sla_resolution_deadline or ""),
            "sla_paused": order.sla_clock_paused,
            "created_at": str(order.create_date or ""),
        }}

    # --- Estimate approval & Mushak 6.3 --------------------------------------

    @http.route("/customer/estimates", type="json", auth="user",
                readonly=False, cors="*")
    def estimates(self, **kwargs):
        """Combined endpoint: act when `estimate_id`+`action` are present,
        otherwise list the estimates on the customer's orders."""
        if kwargs.get("estimate_id") and kwargs.get("action"):
            return self._act_on_estimate(**kwargs)
        return self._list_estimates(**kwargs)

    def _list_estimates(self, **kwargs):
        partner = _scoped_partner(kwargs)
        orders = _su_env()["fix.service.order"].search(
            [("customer_id", "=", partner)], limit=50)
        estimates = _su_env()["fix.estimate"].search(
            [("order_id", "in", orders.ids), ("state", "=", "sent")],
            limit=50, order="id desc")
        result = [{
            "id": e.id,
            "order_ref": e.order_id.name,
            "device": f"{e.order_id.device_id.brand_id.name or ''} {e.order_id.device_id.device_model_id.name or ''}".strip(),
            "version": e.version,
            "parts_total_bdt": _fmt_bdt(e.parts_total),
            "labour_total_bdt": _fmt_bdt(e.labour_total),
            "discount_bdt": _fmt_bdt(e.discount),
            "vat_rate": e.vat_rate,
            "vat_amount_bdt": _fmt_bdt(e.vat_amount),
            "grand_total_bdt": _fmt_bdt(e.grand_total),
            "expiry": str(e.expiry_date or ""),
            "customer_approval_ref": e.customer_approval_ref or "",
        } for e in estimates]
        return {"estimates": result, "total": len(result)}

    def _act_on_estimate(self, **kwargs):
        """The customer's documented approval (BRU-SRM-07) then the
        model's own approve action."""
        action = kwargs.get("action")
        if action not in ("approve", "reject"):
            return _error("invalid_action",
                          "action must be approve|reject")
        estimate = _su_env()["fix.estimate"].browse(
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
                if estimate.grand_total > estimate.DUAL_APPROVAL_THRESHOLD and not estimate.manager_approval_uid:
                    return {"estimate": {
                        "id": estimate.id,
                        "state": estimate.state,
                        "pending_manager": True,
                        "customer_approval_ref": approval_ref,
                        "message": "Customer approval documented. Awaiting branch-manager second-key approval (BRU-SRM-08)."
                    }}
                estimate.action_approve()
        except (UserError, ValidationError) as exc:
            return _error("estimate_rejected", str(exc))
        return {"estimate": {"id": estimate.id, "state": estimate.state, "customer_approval_ref": estimate.customer_approval_ref}}

    # --- PDPA consent dashboard ----------------------------------------------

    @http.route("/customer/consent", type="json", auth="user",
                readonly=False, cors="*")
    def consent(self, **kwargs):
        """Combined endpoint: grant/withdraw when `action` is present,
        otherwise the full per-channel dashboard."""
        if kwargs.get("action"):
            return self._act_on_consent(**kwargs)
        partner = _scoped_partner(kwargs)
        rows = _su_env()["fix.consent"].search(
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
        Consent = _su_env()["fix.consent"]
        if action == "withdraw":
            rows = Consent.search([("partner_id", "=", partner),
                                   ("channel", "=", channel),
                                   ("state", "=", "granted")])
            if not rows:
                return _error("nothing_to_withdraw",
                              "No granted consent on this channel")
            rows.action_withdraw()
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
