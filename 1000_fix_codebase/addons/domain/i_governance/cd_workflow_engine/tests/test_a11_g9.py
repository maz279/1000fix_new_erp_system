"""A11 audit G9 (M63-8): the rule book is VERSIONED, and a request is decided
by the row that was in force when it was submitted.

  - a dated row that has come into force is never edited in place — a new
    ruling is a NEW row (action_new_version closes the current one and opens
    the successor from tomorrow);
  - closing (date_to) and archiving stay writable: that is how a version is
    retired, and it rewrites nothing;
  - fix.approval.request.matrix_id pins the governing row at submission, so
    later rulings never re-route a pending request;
  - the simulation shows who a rule WOULD route to and creates nothing.

Reuses the E1-E4 fixture shapes (fix.complaint is the concession-domain
routable record; <=1,000 is Tier 1).
"""

import datetime
import types

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

T1 = "cd_entity_config.group_dofa_tier_1"
DOA = "cd_workflow_engine.group_doa_administrator"


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    if "fix.complaint" not in env:
        pytest.skip("cd_cx_feedback is not installed")
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([], limit=1)
    x.today = fields.Date.context_today(env["fix.approval.matrix"])
    x.clerk = _user(env, "a11g9_clerk")
    x.t1 = _user(env, "a11g9_t1", [T1])
    x.doa = _user(env, "a11g9_doa", [DOA])
    x.customer = env["res.partner"].create({"name": "A11G9 Customer"})
    return x


def _rule(c, date_from=None, **extra):
    """A concession rule for fix.complaint. Dated rows are the versioned
    regime; undated rows are the always-in-force fallback."""
    vals = {
        "name": "G9 concession rule",
        "res_model": "fix.complaint",
        "decision_domain": "concession",
        "approval_policy": "any",
        "sla_hours": 5,
    }
    if date_from is not None:
        vals["date_from"] = date_from
    vals.update(extra)
    return c.env["fix.approval.matrix"].create(vals)


def _complaint(c, user=None):
    return (
        c.env["fix.complaint"]
        .with_user(user or c.clerk)
        .create(
            {
                "name": "A11G9-%s" % (user or c.clerk).login,
                "customer_id": c.customer.id,
                "operating_unit_id": c.ou.id,
                "description": "g9 probe",
                "severity": "minor",
                "concession_amount": 800.0,
                "concession_type": "refund",
                "dofa_justification": "G9 versioning probe.",
            }
        )
    )


# ---------------------------------------------------------------------------
# a dated row in force is never edited in place
# ---------------------------------------------------------------------------


class TestDatedRowsAreImmutable:
    def test_a_row_in_force_refuses_content_edits_even_for_admin(self, c):
        rule = _rule(c, date_from=c.today - datetime.timedelta(days=30))
        for vals in (
            {"condition": "[('severity', '=', 'critical')]"},
            {"approval_policy": "all"},
            {"sla_hours": 99},
            {"date_from": c.today - datetime.timedelta(days=10)},
        ):
            with pytest.raises(UserError, match="(?i)never edited in place"):
                rule.write(vals)
            # the DoA Administrator is refused too: history is not a privilege
            with pytest.raises(UserError, match="(?i)never edited in place"):
                rule.with_user(c.doa).write(vals)

    def test_closing_and_archiving_stay_writable(self, c):
        """date_to and active are the retirement controls, not content."""
        rule = _rule(c, date_from=c.today - datetime.timedelta(days=30))
        rule.write({"date_to": c.today})
        rule.with_user(c.doa).write({"active": False})
        assert rule.date_to == c.today
        assert not rule.active

    def test_a_future_row_is_still_a_draft_of_a_ruling(self, c):
        rule = _rule(c, date_from=c.today + datetime.timedelta(days=7))
        rule.write({"sla_hours": 48})
        assert rule.sla_hours == 48

    def test_an_undated_row_still_edits(self, c):
        """The regime governs DATED rows; the always-in-force row keeps the
        legacy behaviour the fallback needs."""
        rule = _rule(c)
        rule.write({"sla_hours": 12})
        assert rule.sla_hours == 12


# ---------------------------------------------------------------------------
# action_new_version: close at today, successor from tomorrow
# ---------------------------------------------------------------------------


class TestNewVersion:
    def test_the_current_row_is_closed_and_the_successor_takes_over(self, c):
        rule = _rule(
            c,
            date_from=c.today - datetime.timedelta(days=30),
            condition="[('severity', '=', 'critical')]",
            approval_policy="all",
        )
        action = rule.action_new_version()
        assert action["res_model"] == "fix.approval.matrix"
        successor = c.env["fix.approval.matrix"].browse(action["res_id"])
        tomorrow = c.today + datetime.timedelta(days=1)
        assert rule.date_to == c.today, "the old row still governs today, then stops"
        assert successor.date_from == tomorrow
        assert not successor.date_to
        assert successor.approval_policy == "all"
        assert successor.condition == rule.condition
        assert successor.res_model == rule.res_model
        assert successor.decision_domain == rule.decision_domain
        # the successor is not yet in force, so the guard lets it be edited
        successor.write({"approval_policy": "any"})
        assert successor.approval_policy == "any"

    def test_a_row_without_a_date_cannot_be_versioned(self, c):
        rule = _rule(c)
        with pytest.raises(UserError, match="(?i)no effective date"):
            rule.action_new_version()

    def test_two_versions_on_one_date_are_refused(self, c):
        rule = _rule(c, date_from=c.today - datetime.timedelta(days=30))
        rule.action_new_version()
        second = _rule(c, date_from=c.today)  # different row, same ruling slot
        # its successor would collide with the first successor's date
        with pytest.raises((ValidationError, UserError)):
            second.action_new_version()


# ---------------------------------------------------------------------------
# the request pins the row that governed it
# ---------------------------------------------------------------------------


class TestRequestPinsTheRule:
    def test_the_request_keeps_its_row_after_a_new_ruling(self, c):
        rule = _rule(c, date_from=c.today - datetime.timedelta(days=30), approval_policy="all")
        complaint = _complaint(c)
        complaint.with_user(c.clerk).action_request_approval(justification="g9 pin")
        req = complaint.approval_request_id
        assert req.matrix_id == rule, "the row in force at submission governs"
        assert req.approval_policy == "all"
        # a new ruling lands: the pending request does not move with it
        rule.action_new_version()
        req.invalidate_recordset()
        assert req.matrix_id == rule
        assert req.approval_policy == "all", "a later ruling never re-routes a pending request"


# ---------------------------------------------------------------------------
# the simulation creates nothing
# ---------------------------------------------------------------------------


class TestSimulation:
    def test_simulate_routes_without_creating_anything(self, c):
        _rule(c, date_from=c.today - datetime.timedelta(days=30))
        complaint = _complaint(c)
        requests_before = c.env["fix.approval.request"].search_count([])
        tasks_before = c.env["fix.workflow.task"].search_count([])
        out = complaint.approval_simulate()
        assert out["approvers"], "Tier 1 holders must appear as approvers"
        assert any(c.t1.name == a.split(" (on behalf")[0] for a in out["approvers"])
        assert c.env["fix.approval.request"].search_count([]) == requests_before
        assert c.env["fix.workflow.task"].search_count([]) == tasks_before
        assert complaint.approval_state == "none"

    def test_action_test_rule_answers_from_the_row(self, c):
        rule = _rule(c, date_from=c.today - datetime.timedelta(days=30))
        complaint = _complaint(c)
        out = rule.action_test_rule(res_id=complaint.id)
        assert out["rule"] == rule.display_name
        assert out["approvers"]
