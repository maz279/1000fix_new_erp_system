# msp_roles — the M05 role groups and the two checks every M05 decision uses
# (A02 audit M05-1, M05-2, M05-5, M05-6). Not a model file: the model files
# import it directly, so models/__init__.py does not list it.
#
# Who decides is the ACTING user (self.env.user), never a typed field.
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError

GROUP_ENGINEER = "cd_msp_contract.group_msp_engineer"
GROUP_CAB = "cd_msp_contract.group_msp_cab_member"
GROUP_CHANGE_MANAGER = "cd_msp_contract.group_msp_change_manager"
GROUP_CREDIT_APPROVER = "cd_msp_contract.group_msp_credit_approver"


def is_system(env) -> bool:
    """True for the system user itself (data loading, crons that run as
    OdooBot, the test harness). Not for sudo() from a person: a sudo keeps
    that person's uid, so their role and segregation checks still apply."""
    return env.uid == SUPERUSER_ID


def has_any(env, groups) -> bool:
    return is_system(env) or any(env.user.has_group(g) for g in groups)


def require_role(env, groups, what):
    """Refuse unless the acting user holds one of ``groups``."""
    if has_any(env, groups):
        return
    names = []
    for xmlid in groups:
        group = env.ref(xmlid, raise_if_not_found=False)
        names.append(group.sudo().name if group else xmlid)
    raise UserError(
        "%s needs the %s role. You do not hold it; ask someone who does. "
        "(Role membership is a business appointment.)" % (what, " or ".join(names))
    )


def require_other_person(env, others, what):
    """Segregation of duties: the acting user must not be one of ``others``."""
    if is_system(env):
        return
    if env.user in others:
        raise UserError(
            "Segregation of duties: %s must be done by a different person from the "
            "one who raised or carried out the work." % what
        )
