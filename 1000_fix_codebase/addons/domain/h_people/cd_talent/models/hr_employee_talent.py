# cd_talent — the M58 -> M21 / M29 hand-off (A09 audit M58-F6, interface I6).
#
# The employee master used to be created at candidate hire, and its create
# queued `employee.joined`, which M29 turns into a Keycloak account. So a
# candidate whose onboarding had not even started (NID unverified, no signed
# contract) already held a corporate identity. The hire still creates the
# employee (the draft contract needs one), but holds the joiner event; the
# onboarding plan publishes it, with the employee id and code M29 keys on,
# once onboarding completes.
from odoo import models

# An object, never a flag: a JSON-RPC caller can put any key it likes in the
# context, but it cannot put this object there.
_JOINER_HOLD = object()
JOINER_HOLD_KEY = "fix_talent_joiner_hold"


def hold_joiner(env):
    """An environment whose hr.employee creates do not publish employee.joined."""
    return env(context=dict(env.context, **{JOINER_HOLD_KEY: _JOINER_HOLD}))


class HrEmployeeTalent(models.Model):
    _inherit = "hr.employee"

    def _emit_jml(self, event_type: str, payload: dict):
        if (
            event_type == "employee.joined"
            and self.env.context.get(JOINER_HOLD_KEY) is _JOINER_HOLD
        ):
            return None
        return super()._emit_jml(event_type, payload)

    def _fix_joiner_payload(self) -> dict:
        """The employee.joined payload M29 provisions from (same shape as
        cd_employee_core's create event)."""
        self.ensure_one()
        return {
            "employee_id": self.id,
            "employee_code": self.employee_code,
            "branch_id": self.branch_id.id if self.branch_id else None,
            "primary_role": self.primary_role_id.code if self.primary_role_id else None,
            "joined_date": str(self.joined_date) if self.joined_date else None,
            "name": self.name,
            "work_email": self.work_email or None,
        }
