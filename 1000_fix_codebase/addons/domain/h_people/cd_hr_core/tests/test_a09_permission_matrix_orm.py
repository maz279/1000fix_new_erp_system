# A09 permission matrix — RAP X-02's acceptance criterion.
#
# "Permission matrix test enumerates every A09 model x group and asserts the
# expected allow/deny." Before the 2026-10-30 zero-trust re-audit, 54 of the 84
# A09 ACL rows granted write+create to base.group_user, including every model
# that feeds a control enforced elsewhere: a technician could grant themselves
# the certification the M22 dispatch gate checks, clear their own police
# verification, or edit their own contract basic. The OU record rules do not
# help — they scope WHICH ROWS a user sees, not which models they may write,
# and a self-granted row sits in the user's own operating unit.
import pytest
from odoo.exceptions import AccessError

# The sanctioned self-service surface: a worker must be able to raise a safety
# incident, log their own lone-worker / road check, apply for leave and punch.
SELF_SERVICE = [
    "fix.hse.incident",
    "fix.hse.loneworker",
    "fix.hse.roadcheck",
    "fix.leave.request",
    "fix.attendance.record",
    # A09 P0-b (FR-HCM-042): an employee raises a change of their own bank or
    # identity details; HR decides it (record rule: own requests only).
    "fix.hr.master.change",
]

# Models a plain internal user must NOT be able to write, grouped by why.
GATE_INPUTS = [
    "fix.certification",  # the M22 dispatch gate reads this
    "fix.talent.check",  # the M58 PCC hire gate reads this
    "fix.employment.contract",  # basic pay -> OT, gross, PF, tax
    "fix.attendance.lock",  # the payroll period lock
    "fix.statutory.accident.register",  # the BLA s.90 statutory register
    "fix.performance.scorecard",  # incentive pay input
    "fix.incentive.run",
    "fix.compensation.band",
    "fix.talent.offer",
]
MASTER_DATA = [
    "fix.org.position",
    "fix.hr.transfer",
    "fix.hr.exit",
    "fix.hr.document",
    "fix.hr.disciplinary.case",
    "fix.leave.type",
    "fix.competency",
    "fix.device.category",
    "fix.training.course",
    "fix.roster.slot",
    "fix.shift.template",
    "fix.hr.holiday",
    "fix.biometric.device",
    "fix.safety.inspection",
    "fix.ppe.register",
    "fix.hazardous.substance.register",
    "fix.job.requisition",
    "fix.candidate",
    "fix.performance.review",
    "fix.succession.plan",
]

ROLE_FOR = {
    "cd_hr_core.group_hr_officer": ["fix.org.position", "fix.hr.transfer", "fix.leave.type"],
    "cd_attendance.group_attendance_supervisor": ["fix.roster.slot", "fix.hr.holiday"],
    "cd_competency.group_training": ["fix.competency", "fix.certification"],
    "cd_hse.group_hse_officer": ["fix.safety.inspection", "fix.ppe.register"],
    "cd_talent.group_talent": ["fix.candidate", "fix.job.requisition"],
}


@pytest.fixture
def plain_user(odoo_env):
    """An internal user holding base.group_user and nothing else."""
    user = odoo_env["res.users"].create(
        {
            "name": "A09 Plain Internal",
            "login": "a09.plain.matrix",
            "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
        }
    )
    return odoo_env(user=user.id)


@pytest.mark.parametrize("model", GATE_INPUTS + MASTER_DATA)
def test_plain_internal_user_cannot_write_an_a09_control_model(plain_user, model):
    if model not in plain_user:
        pytest.skip(f"{model} not installed")
    with pytest.raises(AccessError):
        plain_user[model].check_access("write")


@pytest.mark.parametrize("model", SELF_SERVICE)
def test_the_self_service_surface_stays_open(plain_user, model):
    """These five are the sanctioned exception in RAP X-02. If one of them ever
    closes, field staff cannot report a safety incident or punch."""
    if model not in plain_user:
        pytest.skip(f"{model} not installed")
    plain_user[model].check_access("write")  # must not raise


@pytest.mark.parametrize("group,models", sorted(ROLE_FOR.items()))
def test_the_owning_role_group_can_write(odoo_env, group, models):
    user = odoo_env["res.users"].create(
        {
            "name": f"A09 Role {group}",
            "login": f"a09.role.{group.replace('.', '_')}",
            "group_ids": [(6, 0, [odoo_env.ref(group).id])],
        }
    )
    env = odoo_env(user=user.id)
    for model in models:
        if model not in env:
            continue
        env[model].check_access("write")  # must not raise


def test_no_a09_model_outside_the_self_service_set_is_writable_by_base_group_user(odoo_env):
    """The estate-level invariant, read from the live ACL table rather than the
    CSVs, so a row added anywhere is caught."""
    base_group = odoo_env.ref("base.group_user")
    rows = odoo_env["ir.model.access"].search(
        [
            ("group_id", "=", base_group.id),
            "|",
            "|",
            ("perm_write", "=", True),
            ("perm_create", "=", True),
            ("perm_unlink", "=", True),
            ("model_id.model", "=like", "fix.%"),
        ]
    )
    a09_prefixes = (
        "fix.hr.",
        "fix.leave.",
        "fix.org.",
        "fix.employment.",
        "fix.attendance.",
        "fix.roster.",
        "fix.shift.",
        "fix.biometric.",
        "fix.payroll.",
        "fix.payslip",
        "fix.beftn.",
        "fix.wppf.",
        "fix.performance.",
        "fix.incentive.",
        "fix.compensation.",
        "fix.succession.",
        "fix.competency",
        "fix.certification",
        "fix.training.",
        "fix.learning.",
        "fix.ojt.",
        "fix.audit.evidence",
        "fix.device.category",
        "fix.job.requisition",
        "fix.candidate",
        "fix.talent.",
        "fix.onboarding.",
        "fix.hse.",
        "fix.safety.",
        "fix.ppe.",
        "fix.hazardous.",
        "fix.statutory.accident",
    )
    offenders = sorted(
        r.model_id.model
        for r in rows
        if r.model_id.model.startswith(a09_prefixes) and r.model_id.model not in SELF_SERVICE
    )
    assert offenders == [], f"A09 models writable by any internal user: {offenders}"
