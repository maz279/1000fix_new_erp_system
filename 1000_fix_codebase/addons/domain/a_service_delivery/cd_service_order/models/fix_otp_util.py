# One-time codes for M01 evidence: the delivery handover OTP (A5) and the
# customer's estimate approval (BRU-SRM-07).
#
# A02 workflow audit M01-9 / M01-10: the delivery "OTP" was a Boolean any clerk
# ticked, and the "documented customer approval" was free text ("trust me" was
# accepted). A code is now issued here, sent to the CUSTOMER's phone through
# the notification dispatcher's SMS channel (the same hand-off the P01 portal
# login uses: cd_customer_portal/controllers/otp_delivery.py), and only its
# keyed digest is stored. The staff member never sees the code; the customer
# reads it out (or the collector, holding the customer's phone, does).
#
# The code is never written to the outbox, the chatter or the log: an outbox
# row is persisted and fanned out, so a code published there would sit in
# clear on the bus (the reason otp_delivery posts it directly).
import hashlib
import hmac
import re
import secrets

from odoo.exceptions import UserError

OTP_TTL_SECONDS = 600
OTP_MAX_ATTEMPTS = 5


def issue_code() -> str:
    return "%06d" % secrets.randbelow(10**6)


def digest(env, scope: str, res_id: int, code: str) -> str:
    """Keyed digest of a code, bound to one record and one purpose."""
    secret = env["ir.config_parameter"].sudo().get_param("database.secret") or ""
    message = "%s:%s:%s" % (scope, res_id, (code or "").strip())
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def matches(env, scope: str, res_id: int, code: str, stored: str) -> bool:
    return bool(stored) and hmac.compare_digest(digest(env, scope, res_id, code), stored)


def bd_mobile(partner) -> str:
    """The partner's 11-digit Bangladesh mobile (01XXXXXXXXX), or ''."""
    for raw in (getattr(partner, "mobile", False), partner.phone):
        digits = re.sub(r"\D", "", raw or "")
        if digits.startswith("880"):
            digits = digits[2:]
        if re.fullmatch(r"01[3-9]\d{8}", digits):
            return digits
    return ""


def mask(phone: str) -> str:
    return phone[:3] + "*****" + phone[-3:] if phone else ""


def dispatch_otp(phone: str, code: str, ttl_seconds: int, language: str = "bn") -> None:
    """Hand the code to the notification dispatcher's SMS channel.

    Fail-closed: when the dispatcher integration is not installed or refuses
    the code, no code exists and the evidence cannot be captured. Tests
    replace this function; nothing else should."""
    try:
        from odoo.addons.cd_customer_portal.controllers import otp_delivery
    except ImportError:
        raise UserError(
            "The SMS one-time-code service is not installed, so the customer's "
            "confirmation cannot be captured. Ask an administrator to enable it."
        ) from None
    try:
        otp_delivery.send_otp(phone, code, ttl_seconds, language)
    except otp_delivery.OtpDeliveryError as exc:
        raise UserError(
            "The one-time code could not be sent to the customer's phone (%s). "
            "Try again shortly." % exc
        ) from None
