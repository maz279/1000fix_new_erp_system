# P01 Customer Self-Service API — the W4 contract endpoints (PP5).
#
# Serves booking, live tracking, device history, device registration,
# ownership transfer, estimate approval and the PDPA consent dashboard.
# Every write goes through the owning model's action methods — the portal passes through;
# validation and money are server-side (AS-09/AS-10). The customer is
# scoped to the session's partner (EA-05: a customer sees only their own
# devices, orders, estimates and consent rows).
#
# Public routes (R01 re-audit 2026-10-22):
# - OTP send/verify: a random 6-digit code per phone, held server-side in the
#   session for OTP_TTL_SECONDS with at most OTP_MAX_ATTEMPTS guesses; a session
#   may request a new code for a phone once per OTP_RESEND_SECONDS (cross-session
#   volume is capped by the Kong rate-limiting plugin). The code is delivered by
#   SMS through the notification dispatcher (``otp_delivery`` - never through the
#   event bus) and echoed back (``dev_code``) only in the synthetic local
#   environment (FIX_ENV=local, DE-11). A verified phone signs into ITS OWN portal
#   account (login = the phone number, created on first use) - never a shared or
#   internal account. Errors never reveal whether a phone is known.
# - tracking: an order is disclosed only to its owner (commercial partner match),
#   to internal staff with read access, or to a caller presenting the order's
#   signed tracking token (``tracking_token``); anything else is "not found".
#   A ``ref`` is matched literally (LIKE wildcards are escaped).
#
# No route declares ``cors``: browsers reach this API only through the Kong
# gateway (P-11), which terminates CORS against its explicit portal-origin
# allow-list (infra/compose/kong/kong.yml); mobile and server clients need none.
# Bookings are classified by the server: a customer may book standard, warranty
# (gated by BRU-SRM-02) or AMC work at normal priority - goodwill/rework/internal
# categories and priority overrides (FR-SRM-080) are staff decisions.
import hmac
import logging
import math
import os
import secrets
import time

from odoo import SUPERUSER_ID, Command, fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import misc

from . import otp_delivery

_logger = logging.getLogger(__name__)

OTP_TTL_SECONDS = 300
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_SECONDS = 60
OTP_SESSION_PREFIX = "customer_otp_"
TRACKING_SIGNATURE_SCOPE = "cd_customer_portal.tracking"
BOOKABLE_CATEGORIES = ("standard", "warranty", "amc")
SERVICE_TYPES = ("walk_in", "collection", "onsite")


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
        groups.insert(0, rest)  # 1-2 leading digits: len(whole_str) > 3 leaves rest non-empty
        grouped = ",".join(groups) + "," + last3
    else:
        grouped = whole_str
    sign = "-" if is_neg else ""
    return f"{sign}{grouped}.{frac_str}"


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _scoped_partner(kwargs):
    """The customer this request acts for: the session user's partner,
    unless an internal user explicitly passes one (admin support view)."""
    partner_id = _to_int(kwargs.get("partner_id"))
    user = request.env.user
    if partner_id and user and user._is_internal():
        return partner_id
    return request.env.user.partner_id.id


# A07 audit (2026-11-04) M17-6: any internal login passed `partner_id` to
# /customer/devices and read that customer's full serials, IMEIs and history
# as superuser, whatever branch it served. Acting for a customer on the device
# endpoints is the Device Registry Agent's support view (R08), and the devices
# returned are only those the agent's own record rules let him open.
DEVICE_SUPPORT_GROUP = "cd_device_registry.group_device_registry_user"


def _device_support_partner(kwargs):
    """The customer the device endpoint acts for, and the environment that may
    read that customer's devices; or an error payload."""
    partner_id = _to_int(kwargs.get("partner_id"))
    user = request.env.user
    if partner_id and user and user._is_internal() and partner_id != user.partner_id.id:
        if not user.has_group(DEVICE_SUPPORT_GROUP):
            return (
                None,
                None,
                _error(
                    "not_permitted",
                    "Acting for a customer on their devices needs the Device Registry Agent role",
                ),
            )
        return partner_id, request.env, None
    return request.env.user.partner_id.id, _su_env(), None


def _normalize_bd_phone(phone):
    """``01XXXXXXXXX`` for a valid Bangladesh mobile number, else ``None``."""
    cleaned = "".join(c for c in str(phone or "").strip() if c.isdigit())
    if cleaned.startswith("880"):
        cleaned = "0" + cleaned[3:]
    elif not cleaned.startswith("0") and len(cleaned) == 10:
        cleaned = "0" + cleaned
    if len(cleaned) != 11 or not cleaned.startswith("01"):
        return None
    return cleaned


def _otp_dev_echo():
    """DE-11: only the synthetic local environment echoes the OTP in the response."""
    return os.environ.get("FIX_ENV") == "local"


def _portal_user_for_phone(phone):
    """The portal (share) account whose login is ``phone``, created on first use.
    ``None`` when the login belongs to an internal, public or archived account."""
    users = _su_env()["res.users"].with_context(active_test=False)
    user = users.search([("login", "=", phone)], limit=1)
    if user:
        if not user.active or not user.share or user._is_public():
            return None
        return user
    portal_group = _su_env().ref("base.group_portal")
    return users.with_context(no_reset_password=True).create(
        {
            "name": f"Customer ({phone[-4:]})",
            "login": phone,
            "phone": phone,
            "group_ids": [Command.set([portal_group.id])],
        }
    )


def tracking_token(order):
    """Signed tracking token for a service order (for SMS / e-mail tracking links:
    ``/tracking?ref=<order ref>&token=<token>``)."""
    return misc.hmac(_su_env(), TRACKING_SIGNATURE_SCOPE, order.id)


def _may_track(order, token):
    """Owner, internal staff with read access, or a valid signed tracking token."""
    user = request.env.user
    if user and not user._is_public():
        owner = order.customer_id.commercial_partner_id
        if owner and owner.id == user.partner_id.commercial_partner_id.id:
            return True
        if user._is_internal() and order.with_user(user).has_access("read"):
            return True
    return (
        isinstance(token, str) and bool(token) and hmac.compare_digest(token, tracking_token(order))
    )


def _escape_like(value):
    """``value`` as a literal (I)LIKE pattern: ``%``, ``_`` and ``\\`` escaped."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _error(code, message):
    return {"error": {"code": code, "message": message}}


class CustomerApiController(http.Controller):
    """The P01 customer self-service portal API (W4 contract)."""

    # --- Phone OTP Auth & Registration -------------------------------------

    @http.route("/customer/auth/otp/send", type="jsonrpc", auth="public", readonly=False)
    def otp_send(self, **kwargs):
        """Send an OTP by SMS to an 11-digit Bangladesh mobile number (login/registration).

        The answer is identical for every well-formed number (no account oracle)."""
        cleaned = _normalize_bd_phone(kwargs.get("phone"))
        if not cleaned:
            return _error(
                "invalid_phone",
                "Please enter a valid 11-digit Bangladesh mobile number (01XXXXXXXXX)",
            )

        key = OTP_SESSION_PREFIX + cleaned
        now = time.time()
        pending = request.session.get(key)
        if isinstance(pending, dict) and now < pending.get("issued_at", 0) + OTP_RESEND_SECONDS:
            wait = math.ceil(pending["issued_at"] + OTP_RESEND_SECONDS - now)
            res = _error("otp_throttled", f"Please wait {wait}s before requesting a new code")
            res["error"]["retry_after"] = wait
            return res

        masked = cleaned[:3] + "*****" + cleaned[-3:]
        code = f"{secrets.randbelow(10**6):06d}"
        try:
            otp_delivery.send_otp(cleaned, code, OTP_TTL_SECONDS, kwargs.get("lang") or "bn")
        except otp_delivery.OtpDeliveryError as exc:
            _logger.warning("OTP SMS hand-off for %s failed: %s", masked, exc)
            if not _otp_dev_echo():
                return _error(
                    "otp_unavailable", "The verification code could not be sent, try again shortly"
                )
        request.session[key] = {
            "code": code,
            "issued_at": now,
            "expires_at": now + OTP_TTL_SECONDS,
            "attempts": 0,
        }
        result = {
            "sent": True,
            "phone": cleaned,
            "masked_phone": masked,
            "expires_in": OTP_TTL_SECONDS,
            "message": f"Verification code sent to {masked}",
        }
        if _otp_dev_echo():
            result["dev_code"] = code
        return result

    @http.route("/customer/auth/otp/verify", type="jsonrpc", auth="public", readonly=False)
    def otp_verify(self, **kwargs):
        """Verify OTP, establish the phone's own portal session and return its profile.

        The code is single-use, expires after OTP_TTL_SECONDS and is burnt after
        OTP_MAX_ATTEMPTS wrong guesses (a new code must then be requested)."""
        cleaned = _normalize_bd_phone(kwargs.get("phone"))
        otp = str(kwargs.get("otp") or "").strip()
        if not otp:
            return _error("missing_otp", "Verification code is required")

        key = OTP_SESSION_PREFIX + (cleaned or "")
        pending = request.session.get(key) if cleaned else None
        if (
            not isinstance(pending, dict)
            or pending.get("expires_at", 0) < time.time()
            or pending.get("attempts", 0) >= OTP_MAX_ATTEMPTS
        ):
            if cleaned:
                request.session.pop(key, None)
            return _error("invalid_otp", "Invalid or expired OTP code")

        if not hmac.compare_digest(otp, str(pending.get("code", ""))):
            attempts = pending.get("attempts", 0) + 1
            if attempts >= OTP_MAX_ATTEMPTS:
                request.session.pop(key, None)
                return _error("too_many_attempts", "Too many invalid attempts, request a new code")
            request.session[key] = dict(pending, attempts=attempts)
            return _error("invalid_otp", "Invalid or expired OTP code")

        request.session.pop(key, None)
        try:
            with _su_env().cr.savepoint():
                user = _portal_user_for_phone(cleaned)
        except (UserError, ValidationError):
            _logger.warning("OTP sign-in: could not provision a portal account", exc_info=True)
            user = None
        if not user:
            return _error("auth_failed", "Unable to sign in with this number")

        # Same session finalisation as Session.authenticate (no password involved).
        request.session["pre_login"] = user.login
        request.session["pre_uid"] = user.id
        request.session.finalize(request.env)
        request.update_env(user=user.id)

        return {
            "verified": True,
            "user": {
                "uid": user.id,
                "name": user.name or f"Customer ({cleaned[-4:]})",
                "phone": cleaned,
                "partner_id": user.partner_id.id,
                "is_portal": True,
            },
        }

    # --- Device Catalogue & Branches ---------------------------------------

    @http.route("/customer/models", type="jsonrpc", auth="user", readonly=True)
    def models(self, **kwargs):
        """Available device catalogue models for registration dropdown."""
        records = _su_env()["fix.device.model"].search([], limit=150, order="name asc")
        result = [
            {
                "id": m.id,
                "name": m.name,
                "brand": m.brand_id.name or "",
                "device_type": m.device_type or "smartphone",
            }
            for m in records
        ]
        return {"models": result, "total": len(result)}

    @http.route("/customer/branches", type="jsonrpc", auth="user", readonly=True)
    def branches(self, **kwargs):
        """Active branches for booking walk-in drop-off or service center allocation."""
        records = _su_env()["fix.branch"].search([], limit=50, order="name asc")
        result = [{"id": b.id, "name": b.name} for b in records]
        return {"branches": result, "total": len(result)}

    # --- Devices & history ------------------------------------------------

    @http.route("/customer/devices", type="jsonrpc", auth="user", readonly=False)
    def devices(self, **kwargs):
        """The customer's registered devices with warranty status and the
        M17 history timeline (T07). Supports action='register' to register
        a new device under the customer's ownership."""
        if kwargs.get("action") == "register" or kwargs.get("device_model_id"):
            return self._register_device(**kwargs)

        partner, env, err = _device_support_partner(kwargs)
        if err:
            return err
        devices = env["fix.device"].search([("owner_id", "=", partner)], limit=100)
        result = []
        for d in devices:
            history = env["fix.device.history"].search(
                [("device_id", "=", d.id)], limit=10, order="date desc"
            )
            result.append(
                {
                    "id": d.id,
                    "brand": d.brand_id.name or "",
                    "model": d.device_model_id.name or "",
                    "identifier": (d.imei_1 or d.serial_number or "")[:6] + "…",
                    "serial_number": d.serial_number or "",
                    "imei_1": d.imei_1 or "",
                    "warranty_status": d.warranty_status or "none",
                    "state": d.state,
                    "history": [
                        {
                            "event": h.event_type,
                            "description": h.description,
                            "date": str(h.date or ""),
                        }
                        for h in history
                    ],
                }
            )
        return {"devices": result, "total": len(result)}

    def _register_device(self, **kwargs):
        """Register a new customer device into the M17 device registry."""
        partner, _env, err = _device_support_partner(kwargs)
        if err:
            return err
        model_id = kwargs.get("device_model_id")
        if not model_id:
            return _error("missing_model", "device_model_id is required")
        model = _su_env()["fix.device.model"].browse(_to_int(model_id) or 0).exists()
        if not model:
            return _error("invalid_model", "Selected device model does not exist")

        serial = (kwargs.get("serial_number") or "").strip() or False
        imei = (kwargs.get("imei_1") or "").strip() or False
        if not serial and not imei:
            return _error("missing_identifier", "Please provide a Serial Number or IMEI")

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
            with _su_env().cr.savepoint():  # a rejected registration leaves no row behind
                device = _su_env()["fix.device"].create(vals)
        except (UserError, ValidationError, ValueError) as exc:
            # ValueError: an unknown purchase_channel / malformed purchase_date
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
            },
        }

    @http.route("/customer/ownership/transfer", type="jsonrpc", auth="user", readonly=False)
    def ownership_transfer(self, **kwargs):
        """Transfer device ownership — T05: 'portal P01 exposes this in
        Phase 5'. The model writes the ownership trail (T05 audit).

        A07 operability (2026-11-07): the trail read "System / data migration"
        with no reason. The owner's own request is the evidence; the channel and
        the reason say so. `reason` and `transfer_type` are the customer's words."""
        device_id = kwargs.get("device_id")
        to_partner_id = kwargs.get("to_partner_id")
        if not device_id or not to_partner_id:
            return _error("missing_params", "device_id and to_partner_id are required")
        device = _su_env()["fix.device"].browse(_to_int(device_id) or 0).exists()
        if not device:
            return _error("no_device", "Device not found")
        # The OWNER transfers, always as themself. `_scoped_partner` lets an internal
        # user act for any customer (the support read view); for a transfer that
        # meant any staff login could give any customer's device away, as
        # superuser (A07 audit 2026-11-03, M17-1). Staff transfers go through the
        # back office, which records them.
        if device.owner_id != request.env.user.partner_id:
            return _error("not_owner", "Only the current owner can transfer this device")
        new_owner = _su_env()["res.partner"].browse(_to_int(to_partner_id) or 0).exists()
        if not new_owner:
            return _error("no_recipient", "The new owner does not exist")
        transfer_type = kwargs.get("transfer_type") or None
        if transfer_type and transfer_type not in dict(
            device._fields["transfer_type_pending"].selection
        ):
            return _error("invalid_transfer_type", "Unknown transfer type")
        reason = (kwargs.get("reason") or "").strip()
        reason = reason or "Requested by the owner, %s, in the customer portal" % (
            request.env.user.partner_id.name
        )
        try:
            with _su_env().cr.savepoint():
                device.action_transfer_ownership(
                    new_owner.id,
                    transfer_type=transfer_type,
                    reason=reason,
                    channel="customer_portal",
                )
        except (UserError, ValidationError) as exc:
            return _error("transfer_rejected", str(exc))
        return {"transferred": True, "device_id": device.id}

    # --- Booking & live tracking -------------------------------------------

    @http.route("/customer/bookings", type="jsonrpc", auth="user", readonly=False)
    def bookings(self, **kwargs):
        """Combined endpoint: create when `fault_description` is present,
        otherwise list."""
        if kwargs.get("fault_description"):
            return self._create_booking(**kwargs)
        return self._list_bookings(**kwargs)

    def _list_bookings(self, **kwargs):
        partner = _scoped_partner(kwargs)
        orders = _su_env()["fix.service.order"].search(
            [("customer_id", "=", partner)], limit=50, order="id desc"
        )
        result = [
            {
                "id": o.id,
                "ref": o.name,
                "state": o.state,
                "category": o.order_category,
                "device": o.device_id.device_model_id.name or "",
                "fault": (o.fault_description or "")[:80],
                "technician": o.technician_id.name or "",
                "created": str(o.create_date or ""),
            }
            for o in orders
        ]
        return {"bookings": result, "total": len(result)}

    def _create_booking(self, **kwargs):
        """<=3-step booking with appointment slot selection (DE-17: Bengali-first)."""
        partner = _scoped_partner(kwargs)
        device_id = kwargs.get("device_id")
        if not device_id:
            return _error(
                "missing_device",
                "device_id is required (M17 — every order needs an identified device)",
            )
        device = _su_env()["fix.device"].browse(_to_int(device_id) or 0).exists()
        if not device or device.owner_id.id != partner:
            return _error("not_owner", "Bookings are only accepted for your own devices")

        category = kwargs.get("order_category") or "standard"
        if category not in BOOKABLE_CATEGORIES:
            return _error(
                "invalid_category", f"order_category must be {'|'.join(BOOKABLE_CATEGORIES)}"
            )

        branch_id = kwargs.get("branch_id")
        if branch_id:
            branch = _su_env()["fix.branch"].browse(_to_int(branch_id) or 0).exists()
        else:
            branch = device.branch_id or _su_env()["fix.branch"].search([], limit=1)
        if not branch:
            return _error("no_branch", "No branch configured")

        service_type = kwargs.get("service_type") or "walk_in"
        if service_type not in SERVICE_TYPES:
            service_type = "walk_in"

        slot = kwargs.get("slot") or "morning"
        slot_date = kwargs.get("slot_date") or str(fields.Date.today())
        raw_fault = kwargs.get("fault_description", "").strip()
        formatted_fault = f"[{service_type.upper()} | Slot: {slot} | Date: {slot_date}] {raw_fault}"

        try:
            # the model's gates (e.g. BRU-SRM-02) raise after the INSERT: a
            # rejected booking must not leave the order behind
            with _su_env().cr.savepoint():
                order = _su_env()["fix.service.order"].create(
                    {
                        "customer_id": partner,
                        "device_id": device.id,
                        "branch_id": branch.id,
                        "service_type": service_type,
                        "order_category": category,
                        "fault_description": formatted_fault,
                        # priority stays the model default: overrides are staff-only (FR-SRM-080)
                    }
                )
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

    @http.route(
        ["/customer/tracking", "/customer/tracking/public"],
        type="jsonrpc",
        auth="public",
        readonly=True,
    )
    def tracking(self, **kwargs):
        """Live tracking: order state, technician, milestone stages, SLA clocks (W4/PP5).
        Supports querying by order_id or order reference `ref` (G2-05/T04).

        A single order is disclosed only to its owner (same commercial partner as
        the authenticated user), to internal staff with read access, or to a caller
        presenting the order's signed tracking ``token`` (see ``tracking_token``).
        Any other lookup - including a sequential ``order_id`` - is answered exactly
        like a non-existent order. Without ``ref``/``order_id`` the caller's own
        orders are listed (none for an anonymous caller)."""
        ref = (kwargs.get("ref") or "").strip()
        order_id = kwargs.get("order_id")
        token = kwargs.get("token")

        if ref:
            # MIG-03 / FR-SRM-088: match both current SO reference and legacy
            # reference, case-insensitively but literally (no caller wildcards)
            pattern = _escape_like(ref)
            order = _su_env()["fix.service.order"].search(
                ["|", ("name", "=ilike", pattern), ("legacy_reference", "=ilike", pattern)],
                limit=1,
            )
            if not order or not _may_track(order, token):
                return _error("no_order", f"Order '{ref}' not found")
        elif order_id:
            order = _su_env()["fix.service.order"].browse(_to_int(order_id) or 0).exists()
            if not order or not _may_track(order, token):
                return _error("no_order", "Order not found")
        else:
            if request.env.user._is_public():
                return {"orders": [], "total": 0}
            partner = _scoped_partner(kwargs)
            orders = _su_env()["fix.service.order"].search(
                [("customer_id", "=", partner)], limit=20, order="id desc"
            )
            result = [
                {
                    "id": o.id,
                    "ref": o.name,
                    "legacy_reference": o.legacy_reference or None,
                    "state": o.state,
                    "device": f"{o.device_id.brand_id.name or ''} {o.device_id.device_model_id.name or ''}".strip(),
                    "created": str(o.create_date or ""),
                }
                for o in orders
            ]
            return {"orders": result, "total": len(result)}

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
            {
                "id": "intake",
                "label_en": "Intake Received",
                "label_bn": "ইন্ট্যাক গ্রহণ",
                "completed": current_stage >= 0,
            },
            {
                "id": "diagnostic",
                "label_en": "Diagnostic",
                "label_bn": "রোগ নির্ণয় ও পরীক্ষা",
                "completed": current_stage >= 1,
            },
            {
                "id": "in_repair",
                "label_en": "Bench Repair",
                "label_bn": "বেঞ্চ মেরামত",
                "completed": current_stage >= 2,
            },
            {
                "id": "qc",
                "label_en": "Quality Control",
                "label_bn": "কোয়ালিটি কন্ট্রোল (QC)",
                "completed": current_stage >= 3,
            },
            {
                "id": "ready",
                "label_en": "Ready / Delivered",
                "label_bn": "ডেলিভারি প্রস্তুত / সম্পন্ন",
                "completed": current_stage >= 4,
            },
        ]

        return {
            "tracking": {
                "id": order.id,
                "ref": order.name,
                "legacy_reference": order.legacy_reference or None,
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
            }
        }

    # --- Estimate approval & Mushak 6.3 --------------------------------------

    @http.route("/customer/estimates", type="jsonrpc", auth="user", readonly=False)
    def estimates(self, **kwargs):
        """Combined endpoint: act when `estimate_id`+`action` are present,
        otherwise list the estimates on the customer's orders."""
        if kwargs.get("estimate_id") and kwargs.get("action"):
            return self._act_on_estimate(**kwargs)
        return self._list_estimates(**kwargs)

    def _list_estimates(self, **kwargs):
        partner = _scoped_partner(kwargs)
        orders = _su_env()["fix.service.order"].search([("customer_id", "=", partner)], limit=50)
        estimates = _su_env()["fix.estimate"].search(
            [("order_id", "in", orders.ids), ("state", "=", "sent")], limit=50, order="id desc"
        )
        result = [
            {
                "id": e.id,
                "order_ref": e.order_id.name,
                "device": f"{e.order_id.device_id.brand_id.name or ''} {e.order_id.device_id.device_model_id.name or ''}".strip(),
                "version": e.version,
                "parts_total_bdt": _fmt_bdt(e.parts_total),
                "labour_total_bdt": _fmt_bdt(e.labour_total),
                # the diagnostic fee is a priced line of the estimate (RF-009)
                "diagnostic_total_bdt": _fmt_bdt(e.diagnostic_total),
                "discount_bdt": _fmt_bdt(e.discount),
                "vat_rate": e.vat_rate,
                "vat_amount_bdt": _fmt_bdt(e.vat_amount),
                "grand_total_bdt": _fmt_bdt(e.grand_total),
                "expiry": str(e.expiry_date or ""),
                "customer_approval_ref": e.customer_approval_ref or "",
            }
            for e in estimates
        ]
        return {"estimates": result, "total": len(result)}

    def _act_on_estimate(self, **kwargs):
        """The customer's documented approval (BRU-SRM-07) then the
        model's own approve action. Only an estimate awaiting the customer
        (state ``sent``) can be approved or rejected - never a draft, an
        expired or an already-decided one."""
        action = kwargs.get("action")
        if action not in ("approve", "reject"):
            return _error("invalid_action", "action must be approve|reject")
        estimate = _su_env()["fix.estimate"].browse(_to_int(kwargs.get("estimate_id")) or 0)
        if not estimate.exists():
            return _error("no_estimate", "Estimate not found")
        partner = _scoped_partner(kwargs)
        if estimate.order_id.customer_id.id != partner:
            return _error("not_your_estimate", "This estimate belongs to another customer")
        if estimate.state != "sent":
            return _error(
                "estimate_not_pending",
                "Only an estimate awaiting your decision can be approved or rejected "
                f"(this one is {estimate.state})",
            )
        approval_ref = kwargs.get("approval_ref", "")
        if action == "approve" and not approval_ref:
            return _error(
                "missing_approval_ref",
                "BRU-SRM-07: a documented approval reference is "
                "required (OTP id, e-sign ref or signed form ID)",
            )
        try:
            with _su_env().cr.savepoint():  # a refused approval records nothing
                if action == "reject":
                    estimate.action_reject()
                else:
                    estimate.write({"customer_approval_ref": approval_ref})
                    if (
                        estimate.grand_total > estimate.DUAL_APPROVAL_THRESHOLD
                        and not estimate.manager_approval_uid
                    ):
                        return {
                            "estimate": {
                                "id": estimate.id,
                                "state": estimate.state,
                                "pending_manager": True,
                                "customer_approval_ref": approval_ref,
                                "message": "Customer approval documented. Awaiting branch-manager second-key approval (BRU-SRM-08).",
                            }
                        }
                    estimate.action_approve()
        except (UserError, ValidationError) as exc:
            return _error("estimate_rejected", str(exc))
        return {
            "estimate": {
                "id": estimate.id,
                "state": estimate.state,
                "customer_approval_ref": estimate.customer_approval_ref,
            }
        }

    # --- PDPA consent dashboard ----------------------------------------------

    @http.route("/customer/consent", type="jsonrpc", auth="user", readonly=False)
    def consent(self, **kwargs):
        """Combined endpoint: grant/withdraw when `action` is present,
        otherwise the full per-channel dashboard."""
        if kwargs.get("action"):
            return self._act_on_consent(**kwargs)
        partner = _scoped_partner(kwargs)
        rows = _su_env()["fix.consent"].search(
            [("partner_id", "=", partner)], limit=100, order="channel, date_granted desc"
        )
        result = [
            {
                "id": c.id,
                "channel": c.channel,
                "state": c.state,
                "date_granted": str(c.date_granted or ""),
                "date_withdrawn": str(c.date_withdrawn or "") or None,
                "proof": c.proof or "",
            }
            for c in rows
        ]
        return {"consents": result, "total": len(result)}

    def _act_on_consent(self, **kwargs):
        action = kwargs.get("action")
        if action not in ("grant", "withdraw"):
            return _error("invalid_action", "action must be grant|withdraw")
        channel = kwargs.get("channel")
        if channel not in ("sms", "whatsapp", "email", "push", "marketing"):
            return _error("invalid_channel", "channel must be sms|whatsapp|email|push|marketing")
        partner = _scoped_partner(kwargs)
        Consent = _su_env()["fix.consent"]
        if action == "withdraw":
            rows = Consent.search(
                [("partner_id", "=", partner), ("channel", "=", channel), ("state", "=", "granted")]
            )
            if not rows:
                return _error("nothing_to_withdraw", "No granted consent on this channel")
            rows.action_withdraw()
            return {"consent": {"channel": channel, "state": "withdrawn"}}
        proof = kwargs.get("proof", "")
        if not proof:
            return _error(
                "missing_proof",
                "A granted consent needs its proof reference — "
                "an unverifiable grant is not a grant",
            )
        # BRU-CPM-08: a grant must record the transparency-notice version PRESENTED
        # at capture, and fix.consent refuses one without it. This endpoint used to
        # create the record without a notice, so every grant died on that
        # constraint — the endpoint could not record a consent at all (re-audit
        # 2026-10-31). The version to record is the ACTIVE notice, which
        # fix.transparency.notice defines as "published and not retired — the
        # versions new consent is captured against"; when none is published there
        # is nothing lawful to capture against, and the caller is told so plainly
        # instead of receiving a constraint traceback.
        notice = _su_env()["fix.transparency.notice"].search(
            [("active", "=", True)], order="published_at desc, version desc", limit=1
        )
        if not notice:
            return _error(
                "no_transparency_notice",
                "No published transparency notice to capture consent against "
                "(BRU-CPM-08) — publish a notice version before collecting consent",
            )
        row = Consent.create(
            {
                "partner_id": partner,
                "channel": channel,
                "state": "granted",
                "proof": proof,
                "source": "web",
                "notice_version_id": notice.id,
            }
        )
        return {
            "consent": {
                "id": row.id,
                "channel": channel,
                "state": row.state,
                "notice_version": notice.version,
            }
        }
