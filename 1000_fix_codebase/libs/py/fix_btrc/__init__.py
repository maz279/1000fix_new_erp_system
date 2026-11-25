# libs/py/fix_btrc — THE Bangladesh promotional-curfew clock (REQ-35.2).
#
# WHY a shared library. The curfew window was implemented on fix.campaign in
# cd_campaign (M35). The A03 gap plan then required the notification delivery
# service (S1, M27-owned, cd_contact_centre) to enforce the same window on
# every outbound promotional message — and cd_contact_centre and cd_campaign
# are siblings: neither may import the other. Copying the window into M27
# would have produced the exact duplication the plan forbids ("call it, don't
# copy it"), with two places for the hours to drift apart.
#
# So the clock lives here, in a library with no Odoo dependency, and both
# modules call it. fix.campaign keeps its method names and delegates.
#
# The rule being implemented: BTRC A2P directives permit promotional traffic
# to an individual subscriber only between 08:00 and 22:00 Bangladesh
# Standard Time (UTC+6). Transactional traffic — an order status, an OTP, an
# appointment reminder — is NOT promotional and is not curfewed; the caller
# decides which it is by passing the processing purpose.
"""fix_btrc — the single implementation of the BTRC promotional curfew."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

# Bangladesh Standard Time is a fixed UTC+6 offset with no daylight saving,
# so a fixed-offset tzinfo is exactly right here and needs no tz database.
BST = timezone(timedelta(hours=6))

# Promotional traffic is permitted 08:00–22:00 BST only.
CURFEW_OPEN_HOUR = 8
CURFEW_CLOSE_HOUR = 22

# The purposes that are PROMOTIONAL and therefore curfewed. Everything else
# is transactional or statutory and sends at any hour: refusing to tell a
# customer their device is ready until 08:00 would be a worse service, and
# the directive does not ask for it.
CURFEWED_PURPOSES = frozenset({"marketing", "profiling"})

# The channels that address an individual subscriber. Social, search and
# billboard reach no one in particular, so the curfew does not bind them.
REGULATED_CHANNELS = frozenset({"sms", "email", "portal", "whatsapp", "push", "voice"})


def now_bst(reference: datetime | None = None) -> datetime:
    """Wall-clock time in Bangladesh Standard Time.

    `reference` is a NAIVE UTC datetime (Odoo's storage convention). Passing
    one keeps the function testable under freezegun and lets a caller ask
    "would this have been inside the window?" about a historical send.
    """
    base = reference or datetime.utcnow()
    if base.tzinfo is None:
        base = base.replace(tzinfo=UTC)
    return base.astimezone(BST)


def within_curfew(reference: datetime | None = None) -> bool:
    """True when the clock is inside the permitted 08:00–22:00 BST window."""
    return CURFEW_OPEN_HOUR <= now_bst(reference).hour < CURFEW_CLOSE_HOUR


def next_window_open(reference: datetime | None = None) -> datetime:
    """The next 08:00 BST, as a NAIVE UTC datetime ready for Odoo storage.

    Called at 03:00 BST this returns 08:00 BST the same day; called at 23:00
    BST it returns 08:00 BST the next day. Called INSIDE the window it still
    returns the next day's opening, because the only caller that asks is one
    that has already decided to hold.
    """
    bst = now_bst(reference)
    opens = bst.replace(hour=CURFEW_OPEN_HOUR, minute=0, second=0, microsecond=0)
    if bst.hour >= CURFEW_OPEN_HOUR:
        opens = opens + timedelta(days=1)
    return opens.astimezone(UTC).replace(tzinfo=None)


def is_curfewed(purpose: str, channel: str) -> bool:
    """Does the curfew bind a send of this purpose on this channel?

    Both conditions must hold: the purpose must be promotional AND the
    channel must address an individual subscriber.
    """
    return purpose in CURFEWED_PURPOSES and channel in REGULATED_CHANNELS


def curfew_verdict(purpose: str, channel: str, reference: datetime | None = None) -> dict:
    """The full decision, explained, for a delivery row to record.

    Returns:
        bound        bool — whether the curfew applies at all
        allowed      bool — whether this send may go out now
        hold_until   naive UTC datetime when it may go out, or None
        reason       human-readable, safe to log
    """
    if not is_curfewed(purpose, channel):
        return {
            "bound": False,
            "allowed": True,
            "hold_until": None,
            "reason": "Not promotional traffic to an individual subscriber: the "
            f"BTRC 08:00–22:00 curfew does not bind purpose '{purpose}' on channel '{channel}'.",
        }
    if within_curfew(reference):
        return {
            "bound": True,
            "allowed": True,
            "hold_until": None,
            "reason": "Inside the BTRC promotional window (08:00–22:00 BST).",
        }
    opens = next_window_open(reference)
    return {
        "bound": True,
        "allowed": False,
        "hold_until": opens,
        "reason": "Outside the BTRC promotional window (08:00–22:00 BST); held "
        f"until {opens} UTC (REQ-35.2).",
    }


__all__ = [
    "BST",
    "CURFEWED_PURPOSES",
    "CURFEW_CLOSE_HOUR",
    "CURFEW_OPEN_HOUR",
    "REGULATED_CHANNELS",
    "curfew_verdict",
    "is_curfewed",
    "next_window_open",
    "now_bst",
    "within_curfew",
]
