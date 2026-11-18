# cd_hr_core: M21 capture audit pass 2 (2026-11-19), on a real database.
#
# The records the second audit found the pages could not capture:
#   * page 2/4/7 - the line manager's probation review, which HR's confirm /
#     extend now requires (FR-HCM-016/029, AUT-HCM-03, KPI-218);
#   * page 3     - the dual role, acting charge and dotted-line manager
#     (FR-HCM-024, BRU-HCM-10, T-06), an approved dual role taking a seat;
#   * page 8     - the leaver's knowledge handover, which the HR clearance
#     tick now waits for (FR-HCM-036);
#   * page 7     - an employee's own change of address, contact, emergency
#     contact and family details through the maker-checker request
#     (FR-HCM-040/042).
#
# Every capture and decision runs as a NON-ADMIN user through the P03
# endpoints or the ORM. Arrangement that is not under test is done as
# superuser and says so. Everything rolls back (odoo_env).
import itertools
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_hr_core.tests.residency_memory import install
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09 import m21 as m21_surfaces
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (AccessError, UserError, ValidationError)
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
                "name": "M21P2 User %d" % n,
                "login": "a09-m21p2-%d@test.local" % n,
                "tz": "UTC",
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _emp(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "M21P2 Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


@pytest.fixture(autouse=True)
def residency(monkeypatch):
    return install(monkeypatch)


@pytest.fixture
def w(odoo_env):
    class W:
        pass

    c = W()
    env = c.env = odoo_env
    c.today = fields.Date.context_today(env.user)
    c.plain = _user(env)
    c.hro = _user(env, "cd_hr_core.group_hr_officer")
    c.hro2 = _user(env, "cd_hr_core.group_hr_officer")
    c.mgr_user = _user(env)
    c.mgr = _emp(env, c.mgr_user)
    c.staff_user = _user(env)
    c.staff = _emp(env, c.staff_user, parent_id=c.mgr.id)
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


def _probation(w, emp, probation_class="skilled", days_left=20):
    """Arrangement (superuser): an active probation contract."""
    return w.env["fix.employment.contract"].create(
        {
            "employee_id": emp.id,
            "contract_type": "probation",
            "probation_class": probation_class,
            "joining_date": w.today - timedelta(days=60),
            "probation_end": w.today + timedelta(days=days_left),
            "basic_monthly": 25000.0,
            "state": "active",
        }
    )


RATED = {
    "rating_attendance": "4",
    "rating_quality": "4",
    "rating_skill": "3",
    "rating_conduct": "5",
}


# ------------------------------------------- pages 2/4/7: probation review
def test_hr_cannot_confirm_a_probation_without_the_managers_review(w):
    contract = _probation(w, w.staff)
    with pytest.raises(UserError, match="submitted probation review"):
        contract.with_user(w.hro).action_confirm_probation()
    assert contract.contract_type == "probation"


def test_the_line_manager_reviews_through_the_workspace_and_hr_decides(w, call):
    contract = _probation(w, w.staff)
    mss = w.env(user=w.mgr_user.id)
    # MSS: the picker offers employees on probation, never everyone
    offered = call(
        mss, "model_lookup", model="fix.hr.probation.review", field="employee_id", term="M21P2"
    )
    ids = [
        o["id"]
        for o in (offered.get("options") or offered.get("rows") or offered.get("results") or [])
    ]
    assert w.staff.id in ids, offered
    assert w.mgr.id not in ids, "an employee with no probation is offered"
    out = call(
        mss,
        "model_write",
        model="fix.hr.probation.review",
        values={"employee_id": w.staff.id, "recommendation": "confirm", **RATED},
    )
    assert out.get("id"), out
    review = w.env["fix.hr.probation.review"].browse(out["id"])
    # the server found the contract; the reviewer is the manager
    assert review.contract_id == contract and review.reviewer_id == w.mgr_user
    act = call(
        mss,
        "model_action",
        model="fix.hr.probation.review",
        ids=[review.id],
        method="action_submit",
    )
    assert not act.get("error"), act
    assert review.state == "submitted"
    # once submitted the answers are evidence
    with pytest.raises(UserError, match="cannot be edited"):
        review.with_user(w.mgr_user).write({"recommendation": "not_confirm"})
    contract.with_user(w.hro).action_confirm_probation()
    assert contract.contract_type == "permanent" and contract.probation_review_id == review


def test_nobody_else_reviews_and_the_subject_never_does(w):
    contract = _probation(w, w.staff)
    with pytest.raises(REFUSED):
        w.env["fix.hr.probation.review"].with_user(w.plain).create(
            {"employee_id": w.staff.id, "recommendation": "confirm"}
        )
    with pytest.raises(REFUSED):
        w.env["fix.hr.probation.review"].with_user(w.staff_user).create(
            {"employee_id": w.staff.id, "recommendation": "confirm"}
        )
    # an HR officer may key it, naming the reviewer, but not the subject
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        w.env["fix.hr.probation.review"].with_user(w.hro).create(
            {"employee_id": w.staff.id, "recommendation": "confirm", "reviewer_id": w.staff_user.id}
        )
    assert not contract.probation_review_ids


def test_an_employee_with_no_active_probation_cannot_be_reviewed(w):
    with pytest.raises(UserError, match="no active probation"):
        w.env["fix.hr.probation.review"].with_user(w.hro).create(
            {"employee_id": w.mgr.id, "recommendation": "confirm"}
        )


def test_submit_needs_ratings_and_the_statutory_recommendation(w):
    _probation(w, w.staff, probation_class="clerical")
    Review = w.env["fix.hr.probation.review"].with_user(w.mgr_user)
    bare = Review.create({"employee_id": w.staff.id, "recommendation": "confirm"})
    with pytest.raises(UserError, match="Rate"):
        bare.action_submit()
    extend = Review.create({"employee_id": w.staff.id, "recommendation": "extend", **RATED})
    with pytest.raises(UserError, match="skilled"):
        extend.action_submit()
    no = Review.create({"employee_id": w.staff.id, "recommendation": "not_confirm", **RATED})
    with pytest.raises(UserError, match="concerns"):
        no.action_submit()


def test_hr_decides_only_what_the_latest_review_recommends_and_never_its_own(w):
    contract = _probation(w, w.staff)
    review = (
        w.env["fix.hr.probation.review"]
        .with_user(w.hro)
        .create(
            {
                "employee_id": w.staff.id,
                "recommendation": "extend",
                "concerns": "Needs BGA practice",
                **RATED,
            }
        )
    )
    review.action_submit()
    with pytest.raises(UserError, match="recommends"):
        contract.with_user(w.hro2).action_confirm_probation()
    with pytest.raises(UserError, match="another HR officer"):
        contract.with_user(w.hro).action_extend_probation()
    contract.with_user(w.hro2).action_extend_probation()
    assert contract.probation_extended and contract.probation_review_id == review


def test_the_kpi_counts_probations_ending_with_no_review(w):
    before = m21_surfaces.kpis(w.env(user=w.hro.id))["probation_unreviewed_30d"]
    _probation(w, w.staff, days_left=10)
    assert m21_surfaces.kpis(w.env(user=w.hro.id))["probation_unreviewed_30d"] == before + 1
    review = (
        w.env["fix.hr.probation.review"]
        .with_user(w.mgr_user)
        .create({"employee_id": w.staff.id, "recommendation": "confirm", **RATED})
    )
    review.action_submit()
    assert m21_surfaces.kpis(w.env(user=w.hro.id))["probation_unreviewed_30d"] == before


# -------------------------------------------- page 3: additional assignment
def _position(w, headcount=1, **vals):
    """Arrangement (superuser): a sanctioned position."""
    n = next(_SEQ)
    return w.env["fix.org.position"].create(
        {"name": "M21P2 Seat %d" % n, "headcount": headcount, **vals}
    )


def test_only_hr_records_an_assignment_and_another_officer_approves(w, call):
    seat = _position(w)
    with pytest.raises(REFUSED):
        w.env["fix.hr.additional.assignment"].with_user(w.plain).create(
            {
                "employee_id": w.staff.id,
                "assignment_type": "dual_role",
                "position_id": seat.id,
                "reason": "x",
            }
        )
    out = call(
        w.env(user=w.hro.id),
        "model_write",
        model="fix.hr.additional.assignment",
        values={
            "employee_id": w.staff.id,
            "assignment_type": "dual_role",
            "position_id": seat.id,
            "reason": "Covers the branch store as well",
        },
    )
    assert out.get("id"), out
    rec = w.env["fix.hr.additional.assignment"].browse(out["id"])
    with pytest.raises(UserError, match="another HR officer"):
        rec.with_user(w.hro).action_approve()
    rec.with_user(w.hro2).action_approve()
    assert rec.state == "approved" and rec.approved_by_id == w.hro2
    with pytest.raises(UserError, match="end it"):
        rec.with_user(w.hro).write({"position_id": _position(w).id})


def test_an_approved_dual_role_takes_a_sanctioned_seat(w):
    seat = _position(w, headcount=1)
    rec = (
        w.env["fix.hr.additional.assignment"]
        .with_user(w.hro)
        .create(
            {
                "employee_id": w.staff.id,
                "assignment_type": "dual_role",
                "position_id": seat.id,
                "reason": "x",
            }
        )
    )
    rec.with_user(w.hro2).action_approve()
    seat.invalidate_recordset()
    assert (seat.filled_count, seat.vacant_count) == (1, 0)
    # nobody else is put into the seat it holds (BRU-HCM-10)
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        w.env["hr.employee"].create({"name": "M21P2 Newcomer", "position_id": seat.id})
    second = (
        w.env["fix.hr.additional.assignment"]
        .with_user(w.hro)
        .create(
            {
                "employee_id": w.mgr.id,
                "assignment_type": "dual_role",
                "position_id": seat.id,
                "reason": "x",
            }
        )
    )
    with pytest.raises(UserError, match="full"):
        second.with_user(w.hro2).action_approve()
    # ending it frees the seat
    rec.with_user(w.hro).action_end()
    seat.invalidate_recordset()
    assert seat.filled_count == 0
    second.with_user(w.hro2).action_approve()


def test_assignment_terms_are_checked(w):
    seat = _position(w)
    frozen = _position(w, frozen=True)
    Assignment = w.env["fix.hr.additional.assignment"].with_user(w.hro)
    w.env["hr.employee"].browse(w.staff.id).write({"position_id": seat.id})
    bad = [
        {"assignment_type": "dual_role", "position_id": seat.id},  # already their own
        {"assignment_type": "acting", "position_id": _position(w).id},  # no end date
        {"assignment_type": "dotted_line", "manager_id": w.mgr.id},  # the solid line
        {"assignment_type": "dotted_line", "manager_id": w.staff.id},  # themselves
        {"assignment_type": "dual_role"},  # no position
    ]
    for vals in bad:
        with pytest.raises(ValidationError), w.env.cr.savepoint():
            Assignment.create({"employee_id": w.staff.id, "reason": "x", **vals})
    on_frozen = Assignment.create(
        {
            "employee_id": w.staff.id,
            "assignment_type": "dual_role",
            "position_id": frozen.id,
            "reason": "x",
        }
    )
    with pytest.raises(UserError, match="frozen"):
        on_frozen.with_user(w.hro2).action_approve()
    dotted = Assignment.create(
        {
            "employee_id": w.staff.id,
            "assignment_type": "dotted_line",
            "manager_id": _emp(w.env).id,
            "reason": "x",
        }
    )
    dotted.with_user(w.hro2).action_approve()
    twin = Assignment.create(
        {
            "employee_id": w.staff.id,
            "assignment_type": "dotted_line",
            "manager_id": dotted.manager_id.id,
            "reason": "y",
        }
    )
    with pytest.raises(UserError, match="already covers"):
        twin.with_user(w.hro2).action_approve()


# ----------------------------------------------- page 8: knowledge handover
def _exit_in_notice(w, emp):
    """Arrangement: an exit, its notice confirmed by another officer."""
    ex = (
        w.env["fix.hr.exit"]
        .with_user(w.hro)
        .create({"employee_id": emp.id, "exit_type": "contract_end", "last_working_day": w.today})
    )
    ex.with_user(w.hro2).action_confirm_notice()
    return ex


def test_the_hr_clearance_waits_for_the_accepted_handover(w, call):
    ex = _exit_in_notice(w, w.staff)
    with pytest.raises(UserError, match="knowledge handover"):
        ex.with_user(w.hro2).action_clear_hr()
    successor_user = _user(w.env)
    successor = _emp(w.env, successor_user)
    # ESS: the leaver writes their own handover through the workspace
    leaver_env = w.env(user=w.staff_user.id)
    out = call(
        leaver_env,
        "model_write",
        model="fix.hr.exit.handover",
        values={
            "exit_id": ex.id,
            "successor_id": successor.id,
            "open_work": "3 open field jobs (JOB/101-103); Dhanmondi AMC visit on Friday",
            "accounts_contacts": "Two corporate clients",
        },
    )
    assert out.get("id"), out
    handover = w.env["fix.hr.exit.handover"].browse(out["id"])
    act = call(
        leaver_env,
        "model_action",
        model="fix.hr.exit.handover",
        ids=[handover.id],
        method="action_hand_over",
    )
    assert not act.get("error"), act
    assert handover.state == "handed"
    with pytest.raises(UserError, match="cannot be edited"):
        handover.with_user(w.staff_user).write({"open_work": "nothing"})
    # handed over is not enough
    with pytest.raises(UserError, match="knowledge handover"):
        ex.with_user(w.hro2).action_clear_hr()
    # the leaver, a bystander and HR do not accept for the successor
    for user in (w.staff_user, w.plain, w.hro2):
        with pytest.raises(REFUSED), w.env.cr.savepoint():
            handover.with_user(user).action_accept()
    act = call(
        w.env(user=successor_user.id),
        "model_action",
        model="fix.hr.exit.handover",
        ids=[handover.id],
        method="action_accept",
    )
    assert not act.get("error"), act
    assert handover.state == "accepted" and handover.accepted_by_id == successor_user
    ex.with_user(w.hro2).action_clear_hr()
    assert ex.clearance_hr


def test_the_line_manager_accepts_when_the_successor_has_no_login(w):
    ex = _exit_in_notice(w, w.staff)
    handover = (
        w.env["fix.hr.exit.handover"]
        .with_user(w.hro)
        .create({"exit_id": ex.id, "successor_id": _emp(w.env).id, "open_work": "none"})
    )
    handover.action_hand_over()
    with pytest.raises(UserError), w.env.cr.savepoint():
        handover.with_user(w.hro2).action_accept()
    handover.with_user(w.mgr_user).action_accept()
    assert handover.accepted_by_id == w.mgr_user


def test_handover_parties_and_terms(w):
    ex = _exit_in_notice(w, w.staff)
    with pytest.raises(REFUSED):
        w.env["fix.hr.exit.handover"].with_user(w.plain).create(
            {"exit_id": ex.id, "successor_id": w.mgr.id, "open_work": "x"}
        )
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        w.env["fix.hr.exit.handover"].with_user(w.hro).create(
            {"exit_id": ex.id, "successor_id": w.staff.id, "open_work": "x"}
        )
    w.env["fix.hr.exit.handover"].with_user(w.hro).create(
        {"exit_id": ex.id, "successor_id": w.mgr.id, "open_work": "x"}
    )
    with pytest.raises(IntegrityError), w.env.cr.savepoint():
        w.env["fix.hr.exit.handover"].with_user(w.hro).create(
            {"exit_id": ex.id, "successor_id": w.mgr.id, "open_work": "y"}
        )


def test_a_bystander_reads_no_handover(w):
    ex = _exit_in_notice(w, w.staff)
    handover = (
        w.env["fix.hr.exit.handover"]
        .with_user(w.hro)
        .create({"exit_id": ex.id, "successor_id": w.mgr.id, "open_work": "x"})
    )
    assert not w.env["fix.hr.exit.handover"].with_user(w.plain).search([("id", "=", handover.id)])
    assert w.env["fix.hr.exit.handover"].with_user(w.mgr_user).search([("id", "=", handover.id)])


# ------------------------------------- page 7: an employee's contact change
def test_an_employee_changes_their_contact_details_through_maker_checker(w, call):
    out = call(
        w.env(user=w.staff_user.id),
        "model_write",
        model="fix.hr.master.change",
        values={
            "employee_id": w.staff.id,
            "reason": "Moved house; new emergency contact",
            "proposed_private_street": "House 12, Road 5",
            "proposed_private_district": "Gazipur",
            "proposed_emergency_contact": "Rahima Begum",
            "proposed_emergency_phone": "01711000222",
            "proposed_children_set": True,
            "proposed_children": 0,
        },
    )
    assert out.get("id"), out
    req = w.env["fix.hr.master.change"].browse(out["id"])
    req.with_user(w.staff_user).action_submit()
    with pytest.raises(UserError, match="never edited"):
        req.with_user(w.staff_user).write({"proposed_private_district": "Dhaka"})
    _approve_by_officer(w, req)
    staff = w.staff.sudo()
    assert (staff.private_street, staff.private_district) == ("House 12, Road 5", "Gazipur")
    assert (staff.emergency_contact, staff.emergency_phone) == ("Rahima Begum", "01711000222")
    w.staff.sudo().write({"children": 2})
    req2 = (
        w.env["fix.hr.master.change"]
        .with_user(w.staff_user)
        .create(
            {
                "employee_id": w.staff.id,
                "reason": "Children",
                "proposed_children_set": True,
                "proposed_children": 0,
            }
        )
    )
    req2.action_submit()
    _approve_by_officer(w, req2)
    assert w.staff.sudo().children == 0, "0 children is a real answer"


def _approve_by_officer(w, req):
    """An HR officer decides the request from the approval inbox; the
    employee who raised it is never offered the task."""
    task = (
        w.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", req.approval_request_id.id), ("state", "=", "pending")])
    )
    assert task and w.staff_user not in task.mapped("assigned_user_id")
    officer_task = task.filtered(
        lambda t: t.assigned_user_id.has_group("cd_hr_core.group_hr_officer")
    )[:1]
    officer_task.with_user(officer_task.assigned_user_id).action_approve()
    assert req.state == "applied", req.state


def test_personal_email_is_checked(w):
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        w.env["fix.hr.master.change"].with_user(w.hro).create(
            {"employee_id": w.staff.id, "reason": "x", "proposed_private_email": "not an email"}
        )


# ------------------------------------------------------- the lists serve
@pytest.mark.parametrize(
    "model,cols",
    [
        (
            "fix.hr.probation.review",
            [
                "name",
                "employee_id",
                "probation_end",
                "reviewer_id",
                "review_date",
                "recommendation",
                "state",
            ],
        ),
        (
            "fix.hr.additional.assignment",
            [
                "name",
                "employee_id",
                "assignment_type",
                "position_id",
                "manager_id",
                "date_from",
                "date_to",
                "approved_by_id",
                "state",
            ],
        ),
        (
            "fix.hr.exit.handover",
            [
                "name",
                "employee_id",
                "last_working_day",
                "successor_id",
                "handover_date",
                "accepted_by_id",
                "state",
            ],
        ),
    ],
)
def test_each_new_list_serves_every_column_it_declares(w, call, model, cols):
    assert model in m21_surfaces.SURFACES
    out = call(w.env(user=w.hro.id), "model_records", model=model, cols=cols)
    assert not out.get("error"), out
    served = set(out.get("labels") or {})
    assert set(cols) <= served, "dropped: %s" % sorted(set(cols) - served)


def test_establishment_register_counts_a_dual_role_holder(w):
    seat = _position(w, headcount=2)
    w.env["hr.employee"].browse(w.mgr.id).write({"position_id": seat.id})
    rec = (
        w.env["fix.hr.additional.assignment"]
        .with_user(w.hro)
        .create(
            {
                "employee_id": w.staff.id,
                "assignment_type": "dual_role",
                "position_id": seat.id,
                "reason": "x",
                "date_from": date(2026, 1, 1),
            }
        )
    )
    rec.with_user(w.hro2).action_approve()
    pack = m21_surfaces.establishment_register(w.env(user=w.hro.id))
    row = next(r for r in pack["rows"] if r["position"] == seat.name)
    assert (row["filled"], row["vacant"]) == (2, 0)
