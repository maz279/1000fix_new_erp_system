# M37 catalogue roles and the switches the business must confirm
# (A04 audit, 2026-11-04).
from odoo.exceptions import AccessError

ROLE_OFFICER = "cd_catalogue.group_catalogue_officer"
ROLE_PUBLISHER = "cd_catalogue.group_catalogue_publisher"

# BRU-CAT-14 / FR-CAT-045: an item that is not Active is not sellable. On
# fix_dev 403 of 404 catalogue items are still Draft (none was ever approved,
# because there was no approval), so refusing every unapproved item on deploy
# would stop the estimates of every branch. The switch therefore defaults OFF
# (safe for deploy): with it off, only a Discontinued, Obsolete, archived,
# out-of-scope or unauthorised-brand item is refused. The business turns it
# on once the publisher has worked the approval queue (report §7.1).
SALE_GATE_PARAM = "cd_catalogue.sale_requires_active_item"

# Channels on which a Restricted item may not be sold: the customer-facing
# ones. Service work on an existing customer's device (an estimate) stays
# possible, which is what "existing customers only" means for a repair house.
RESTRICTED_CHANNELS = frozenset({"storefront", "marketplace", "web", "quotation"})


def has_role(env, *xmlids) -> bool:
    return env.su or any(env.user.has_group(x) for x in xmlids)


def require_role(env, xmlids, what: str, role: str = "Catalogue Officer") -> None:
    """Refuse unless the acting user holds one of the catalogue roles."""
    if has_role(env, *xmlids):
        return
    raise AccessError(
        "%s needs the %s role (M37). Plain users read the catalogue but do not "
        "change it." % (what, role)
    )
