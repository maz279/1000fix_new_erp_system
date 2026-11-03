# The M33 decision groups (A03 audit M33-6). Merge execution, KYC
# verification and data-subject-rights fulfilment were open to every internal
# user with Contact write. The groups are declared in
# security/fix_party_master_groups.xml; these helpers are the one place the
# models check them.
from odoo.exceptions import UserError

STEWARD_GROUP = "cd_party_master.group_party_data_steward"
DPO_GROUP = "cd_party_master.group_party_dpo"


def require_group(env, xmlid: str, what: str) -> None:
    """Refuse `what` unless the acting user holds `xmlid`.

    The superuser (crons, data loading, R8 consumers) is trusted, as the
    field guard trusts it."""
    if env.su or env.user.has_group(xmlid):
        return
    group = env.ref(xmlid, raise_if_not_found=False)
    raise UserError("%s needs the '%s' group." % (what, group.name if group else xmlid))
