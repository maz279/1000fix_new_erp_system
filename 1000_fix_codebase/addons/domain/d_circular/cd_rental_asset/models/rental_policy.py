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
PREFIX = "cd_rental_asset."
DEFAULT_DATA_BEARING = "camera,laptop,projector,audio,medical,network,other"


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
