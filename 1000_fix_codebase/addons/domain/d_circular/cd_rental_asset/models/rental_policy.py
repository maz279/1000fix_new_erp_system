# rental_policy — M13 business-policy switches (A05 audit report §7).
#
# Each open business decision is an ir.config_parameter with a SAFE default,
# read here and nowhere else, so a deployment changes the policy without a
# code change and an unset parameter never weakens a control:
#
#   cd_rental_asset.turnaround_padding_days    1   days a fleet unit is blocked
#                                                  after a booking for turnaround
#   cd_rental_asset.late_fee_grace_days        0   overdue days not charged
#   cd_rental_asset.late_fee_multiplier        1.5 x the daily rate per late day
#   cd_rental_asset.late_fee_settlement   invoice  'invoice': the late fee is
#                                                  billed once, on the Mushak 6.3;
#                                                  'deposit': deducted once from
#                                                  the deposit and kept off 6.3
#   cd_rental_asset.damage_charge_requires_approval 1  a damage charge against
#                                                  the customer needs a routed
#                                                  DOFA approval before close
#   cd_rental_asset.enforce_sku_deposit        1   the deposit is at least the
#                                                  SKU's (and kit's) security deposit
#   cd_rental_asset.require_return_inspection  1   a post-return condition report
#                                                  is required for every SKU
#   cd_rental_asset.cancellation_fee_pct       0   % of the deposit forfeited on
#                                                  cancellation (0 = full refund)
#   cd_rental_asset.data_bearing_categories    every category but 'tool': fleet
#                                                  categories whose turnaround
#                                                  needs a verified M06 wipe
#   cd_rental_asset.require_verified_identity  1   a booking is confirmed only for a
#                                                  party with a verified M33 identity
#                                                  document (BRU-RNT-20)
#   cd_rental_asset.condition_photo_minimum    1   photographs each condition report
#                                                  needs before handover / assessment
#                                                  / close (BRU-RNT-01; 0 = off)
#   cd_rental_asset.swap_sla_hours            24   in-rental swap-out SLA (FR-RNT-027)
#
# A05 remediation (2026-11-20, stream S1):
#   cd_rental_asset.late_fee_settlement        IGNORED now: a late fee is always
#                                                  invoiced with M51 VAT (owner D2);
#                                                  it is never taken from the deposit
#   cd_rental_asset.deposit_rate_pct.low      10   owner D8: deposit = max(SKU floor,
#   cd_rental_asset.deposit_rate_pct.standard 20   unit book value x the customer's
#   cd_rental_asset.deposit_rate_pct.high     35   risk-tier rate)
#   cd_rental_asset.hold_grace_hours          24   a reserved booking not handed over
#                                                  this long after its start day ends
#                                                  is released (AUT-RNT-02)
#   cd_rental_asset.min_dispatch_grade         c   lowest condition grade a unit may
#   cd_rental_asset.min_dispatch_grade.<cat>       be allocated at (BRU-RNT-14), per
#                                                  fleet category or for all
#   cd_rental_asset.overdue_reminder_days  1,3,7   overdue days on which rental.overdue
#                                                  is published and the booker is
#                                                  escalated (M13-26)
#   cd_rental_asset.return_due_notice_days     1   days before the due date the
#                                                  rental.return_due notice goes (I5)
#   cd_rental_asset.lease_assessment_days    365   rentals this long need an M53 lease
#                                                  assessment before activation
#                                                  (BRU-RNT-18)
#   cd_rental_asset.vat_treatment_code.rental  -   optional M51 tariff code for the
#                                                  rental lines (else M51's standard)
#   cd_rental_asset.vat_treatment_code.damage  -   REQUIRED to invoice damage or loss
#                                                  compensation: an exempt / zero-rated
#                                                  M51 row (outside VAT, owner D2)
#   cd_rental_asset.account_code.<role>        -   REQUIRED, see rental_gl.py
PREFIX = "cd_rental_asset."
DEFAULT_DATA_BEARING = "camera,laptop,projector,audio,medical,network,other"
GRADE_ORDER = ("d", "c", "b", "a")
DEPOSIT_TIER_DEFAULTS = {"low": 10.0, "standard": 20.0, "high": 35.0}


def dhaka_today(env):
    """The Asia/Dhaka business day now (Odoo runs in UTC; a cron has no tz)."""
    from odoo import fields
    from odoo.addons.cd_billing_engine.models.fix_billing_engine import dhaka_date

    return dhaka_date(fields.Datetime.now())


def deposit_rate_pct(env, tier):
    tier = tier if tier in DEPOSIT_TIER_DEFAULTS else "standard"
    return max(param_float(env, "deposit_rate_pct.%s" % tier, DEPOSIT_TIER_DEFAULTS[tier]), 0.0)


def min_dispatch_grade(env, category):
    raw = _raw(env, "min_dispatch_grade.%s" % (category or "other"), None) or _raw(
        env, "min_dispatch_grade", "c"
    )
    raw = str(raw).strip().lower()
    return raw if raw in GRADE_ORDER else "c"


def grade_below(grade, minimum):
    """True when `grade` is worse than `minimum` (d < c < b < a)."""
    if not grade:
        return False
    return GRADE_ORDER.index(grade) < GRADE_ORDER.index(minimum)


def int_list(env, key, default):
    raw = str(_raw(env, key, default))
    out = []
    for part in raw.split(","):
        try:
            value = int(part.strip())
        except ValueError:
            continue
        if value > 0:
            out.append(value)
    return sorted(set(out))


def _raw(env, key, default):
    value = env["ir.config_parameter"].sudo().get_param(PREFIX + key)
    return default if value in (None, False, "") else value


def param_float(env, key, default):
    try:
        return float(_raw(env, key, default))
    except (TypeError, ValueError):
        return float(default)


def param_int(env, key, default):
    try:
        return max(int(float(_raw(env, key, default))), 0)
    except (TypeError, ValueError):
        return int(default)


def param_on(env, key, default=True):
    """A control switch: anything but an explicit off value keeps it on."""
    value = str(_raw(env, key, "1" if default else "0")).strip().lower()
    return value not in ("0", "false", "no", "off")


def late_fee_mode(env):
    mode = str(_raw(env, "late_fee_settlement", "invoice")).strip().lower()
    return "deposit" if mode == "deposit" else "invoice"


def data_bearing_categories(env):
    raw = str(_raw(env, "data_bearing_categories", DEFAULT_DATA_BEARING))
    return {c.strip() for c in raw.split(",") if c.strip()}
