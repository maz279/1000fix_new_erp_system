# M11 pricing roles, the shared role check, and the business defaults the
# business must confirm (A04 audit, 2026-11-04).
from odoo.exceptions import AccessError, UserError

ROLE_OFFICER = "cd_rate_card.group_pricing_officer"
ROLE_RELEASER = "cd_rate_card.group_price_releaser"

# BRU-PRC-06, the one discount ladder of the spec: <=10% agent (no second
# signature), <=20% branch manager, <=35% sales manager, above 35% the CCO.
# Expressed on the estate's DOFA tiers (upper bound inclusive, tier). It is
# what fix.discount.policy.discount_ladder() returns until the business
# releases its own bands; the three ladders that exist today (discount
# approval 5/10, estimate 5/15/30/50, floor 15/30) are to be replaced by it
# (report §7 item 7: business decision).
DEFAULT_DISCOUNT_LADDER = (
    (10.0, "tier_0"),
    (20.0, "tier_2"),
    (35.0, "tier_3"),
    (float("inf"), "tier_4"),
)


def has_role(env, *xmlids) -> bool:
    return env.su or any(env.user.has_group(x) for x in xmlids)


def require_role(env, xmlids, what: str, role: str = "Pricing Officer") -> None:
    """Refuse unless the acting user holds one of the pricing roles."""
    if has_role(env, *xmlids):
        return
    raise AccessError(
        "%s needs the %s role (M11). Plain users read prices but do not change "
        "them." % (what, role)
    )


def require_releaser_not_author(env, authority, acting, record, authors, what):
    """The releaser holds the role and is none of the record's authors
    (BRU-PRC-07, SOD-14). Superuser code is trusted."""
    if env.su:
        return
    if not authority.has_group(ROLE_RELEASER):
        raise AccessError("%s needs the Price-Book Releaser role (M11)." % what)
    if acting & authors:
        raise UserError(
            "Segregation of duties: you raised or submitted %s, so another releaser "
            "decides it (BRU-PRC-07)." % record.display_name
        )
