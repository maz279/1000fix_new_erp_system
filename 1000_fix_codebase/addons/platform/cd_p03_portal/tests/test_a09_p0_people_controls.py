# A09 P0 acceptance suite (A1, A2, A5, A6, A7 of the A09 workflow audit,
# working/A09_Workflow_and_Approval_Report.md): employee master, HR roles,
# people-data reads, workspace scoping and the identity lifecycle.
#
# Every attack runs as a freshly created NON-admin user (the A03 lesson:
# admin-created data hid the worst defect). Writes go through call_kw with
# the client-controlled `tracking_disable` key, because that is how the audit
# got a plain employee's master write past the accidental refusal of mail
# tracking (A09 report §8.4).
import itertools
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a09
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError)
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 P0 User %d" % n,
                "login": "a09-p0-%d@test.local" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _employee(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "A09 P0 Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


def _contract(env, employee, basic=40000.0):
    return env["fix.employment.contract"].create(
        {
            "employee_id": employee.id,
            "contract_type": "permanent",
            "joining_date": fields.Date.today(),
            "weekly_hours": 48,
            "basic_monthly": basic,
        }
    )


def _rpc_write(env, user, model, rec, vals):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[model], "write", [[rec.id], vals], {}
    )


@pytest.fixture
def x(odoo_env):
    class X:
        pass

    c = X()
    c.env = odoo_env
    c.plain = _user(odoo_env)
    c.me = _employee(odoo_env, c.plain)
    c.colleague = _employee(odoo_env, bank_account_number="1111222233334", basic_wage=30000)
    c.hro = _user(odoo_env, "cd_hr_core.group_hr_officer")
    return c


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


# ---------------------------------------------------------------- A1 master
@pytest.mark.parametrize(
    "field,value",
    [
        ("bank_account_number", "9999999999999"),
        ("routing_number", "123456789"),
        ("nid_number", "1234567890"),
        ("basic_wage", 999999),
        ("mfs_account_number", "01700000000"),
    ],
)
def test_a1_plain_employee_cannot_rewrite_colleague_master(x, field, value):
    with pytest.raises(REFUSED):
        _rpc_write(x.env, x.plain, "hr.employee", x.colleague, {field: value})
    assert x.colleague[field] != value


def test_a1_plain_employee_cannot_raise_own_wage(x):
    with pytest.raises(REFUSED):
        _rpc_write(x.env, x.plain, "hr.employee", x.me, {"basic_wage": 250000})


def test_a1_plain_employee_cannot_read_colleague_bank_or_wage(x):
    with pytest.raises(AccessError):
        x.env(user=x.plain.id)["hr.employee"].browse(x.colleague.id).read(
            ["bank_account_number", "basic_wage"]
        )


def test_a1_plain_employee_still_reads_the_directory(x):
    """Non-sensitive fields stay readable: other modules show employees."""
    row = x.env(user=x.plain.id)["hr.employee"].browse(x.colleague.id).read(["name"])
    assert row[0]["name"] == x.colleague.name


# ---------------------------------------------------------------- A2 roles
def test_a2_hr_officer_creates_and_maintains_the_master(x):
    env = x.env(user=x.hro.id)
    emp = env["hr.employee"].create({"name": "A09 P0 Joiner"})
    emp.write({"name": "A09 P0 Joiner Renamed", "bank_account_number": "5555666677778"})
    assert emp.bank_account_number == "5555666677778"


def test_a2_recruiter_completes_a_hire(x):
    """A2 on the proper path. The A09 M58 build closed the walk-in hire
    (M58-F1), so the candidate is on an open, approved requisition with an
    accepted offer, a positive interview and verified NID and reference
    checks. The Recruitment Officer holds no hr.employee create and still
    completes the hire: the employee is created as a controlled step."""
    env = x.env
    recruiter = _user(env, "cd_talent.group_talent")
    assert not env(user=recruiter.id)["hr.employee"].has_access("create")
    # The approvals, clearances and acceptance are other roles' steps
    # (cd_talent/tests/test_a09_talent_controls.py walks them): their
    # outcomes are recorded here by the superuser.
    position = env["fix.org.position"].create({"name": "A09 P0 Position"})
    req = env["fix.job.requisition"].create(
        {"name": "A09 P0 Requisition", "position_id": position.id, "openings": 1}
    )
    req.write({"state": "open", "approval_state": "approved", "approved_openings": 1})
    cand = env["fix.candidate"].create(
        {
            "name": "A09 P0 Candidate",
            "requisition_id": req.id,
            "consent_given": True,
            "declaration_accepted": True,
            "date_of_birth": "1998-03-01",
            "state": "offered",
        }
    )
    env["fix.talent.interview"].create(
        {
            "candidate_id": cand.id,
            "scheduled_on": fields.Datetime.now(),
            "interviewer_id": _employee(env).id,
            "recommendation": "yes",
            "state": "done",
        }
    )
    for kind in ("nid", "reference"):
        env["fix.talent.check"].create(
            {
                "candidate_id": cand.id,
                "check_type": kind,
                "result": "clear",
                "verified_by_id": env.ref("base.user_admin").id,
            }
        )
    env["fix.talent.offer"].create(
        {
            "candidate_id": cand.id,
            "gross_salary": 30000,
            "basic_salary": 18000,
            "joining_date": fields.Date.add(fields.Date.today(), days=30),
            "state": "accepted",
        }
    )
    cand.with_user(recruiter).action_hire()
    assert cand.state == "hired" and cand.employee_id


# ---------------------------------------------------------------- A5 reads
def test_a5_plain_employee_reads_only_own_contract(x):
    own = _contract(x.env, x.me)
    _contract(x.env, x.colleague)
    seen = x.env(user=x.plain.id)["fix.employment.contract"].search([])
    assert seen == own


def test_a5_hr_officer_reads_every_contract(x):
    other = _contract(x.env, x.colleague)
    assert other in x.env(user=x.hro.id)["fix.employment.contract"].search([])


def test_a5_health_records_belong_to_occupational_health(x):
    rec = x.env["fix.hse.health"].create(
        {
            "employee_id": x.colleague.id,
            "record_type": "restriction",
            "record_date": fields.Date.today(),
            "fitness": "fit_restricted",
        }
    )
    hse = _user(x.env, "cd_hse.group_hse_officer")
    for who in (x.plain, hse):
        with pytest.raises(AccessError):
            x.env(user=who.id)["fix.hse.health"].browse(rec.id).read(["fitness"])
    oh = _user(x.env, "cd_hse.group_occupational_health")
    assert x.env(user=oh.id)["fix.hse.health"].browse(rec.id).fitness == "fit_restricted"


def test_a5_plain_employee_reads_only_own_review(x):
    Review = x.env["fix.performance.review"]
    own = Review.create({"employee_id": x.me.id, "period": "2026-H2"})
    Review.create({"employee_id": x.colleague.id, "period": "2026-H2"})
    assert x.env(user=x.plain.id)["fix.performance.review"].search([]) == own


def test_a5_manager_reads_direct_reports_review(x):
    report = _employee(x.env, parent_id=x.me.id)
    rev = x.env["fix.performance.review"].create({"employee_id": report.id, "period": "2026-H2"})
    assert rev in x.env(user=x.plain.id)["fix.performance.review"].search([])


@pytest.mark.parametrize(
    "model",
    ["fix.candidate", "fix.talent.offer", "fix.incentive.run", "fix.compensation.band"],
)
def test_a5_plain_employee_has_no_read_on_hr_only_models(x, model):
    assert not x.env(user=x.plain.id)[model].has_access("read")


# ---------------------------------------------------------------- A6 workspace
def test_a6_every_a09_surface_reads_under_record_rules():
    assert all(conf.get("rules") for conf in a09.SURFACES.values())


def test_a6_workspace_list_shows_plain_employee_only_own_contract(x, call):
    own = _contract(x.env, x.me)
    _contract(x.env, x.colleague)
    res = call(
        x.env(user=x.plain.id),
        "model_records",
        model="fix.employment.contract",
        cols=["employee_id", "basic_monthly"],
    )
    assert "error" not in res, res
    assert [r["id"] for r in res["rows"]] == [own.id]


def test_a6_workspace_form_refuses_colleague_contract_by_id(x, call):
    other = _contract(x.env, x.colleague)
    res = call(
        x.env(user=x.plain.id),
        "model_form",
        model="fix.employment.contract",
        fields=[{"name": "basic_monthly"}],
        record_id=other.id,
    )
    assert "error" in res and not res.get("record")


def test_a6_workspace_list_drops_sensitive_columns_for_plain_employee(x, call):
    res = call(
        x.env(user=x.plain.id),
        "model_records",
        model="hr.employee",
        cols=["name", "bank_account_number", "basic_wage", "nid_number"],
    )
    assert "error" not in res, res
    assert set(res["labels"]) <= {"id", "name"}
    assert all("bank_account_number" not in r for r in res["rows"])


def test_a6_people_kpis_do_not_fail_for_plain_employee(x):
    out = a09.kpis(x.env(user=x.plain.id))
    assert set(out) == set(a09.MODULES)


def test_a6_form10_register_refused_for_plain_employee(x):
    lock = x.env["fix.attendance.lock"].create(
        {
            "name": "A09 P0 Lock",
            "period_start": fields.Date.today().replace(day=1),
            "period_end": fields.Date.today(),
        }
    )
    with pytest.raises(AccessError):
        lock.with_user(x.plain).action_export_form10_overtime_register()


# ---------------------------------------------------------------- A7 identity
def test_a7_plain_employee_cannot_mark_a_colleague_left(x):
    with pytest.raises(AccessError):
        x.colleague.with_user(x.plain).action_mark_left()
    assert not x.colleague.left_date


def test_a7_plain_employee_cannot_apply_identity_outcomes(x):
    with pytest.raises(AccessError):
        x.env(user=x.plain.id)["hr.employee"].consume_identity_lifecycle_event(
            {"event_type": "identity.deprovisioned", "payload": {"employee_id": x.colleague.id}}
        )


def test_a7_hr_officer_cannot_forge_deprovisioning(x):
    with pytest.raises(UserError):
        _rpc_write(
            x.env,
            x.hro,
            "hr.employee",
            x.colleague,
            {"keycloak_deprovision_status": "deprovisioned"},
        )
    with pytest.raises(UserError):
        _rpc_write(x.env, x.hro, "hr.employee", x.colleague, {"keycloak_user_id": "attacker-kc-id"})


def test_a7_hr_officer_records_a_leaver(x):
    x.colleague.with_user(x.hro).action_mark_left()
    assert x.colleague.left_date and x.colleague.keycloak_deprovision_status == "pending"
