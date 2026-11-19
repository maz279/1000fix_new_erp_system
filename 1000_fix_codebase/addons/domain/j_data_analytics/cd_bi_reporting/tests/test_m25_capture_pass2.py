"""M25 second capture pass (2026-11-19): the records the spec names for each
sub-module page, driven through the ORM as real, non-admin users. Each rule
is checked both ways: the bypass is refused AND the governed path works.

  p1  dashboard business owner + steward verification (BRU-BID-07/10, §8.1),
      fix.bi.annotation (FR-BID-009)
  p2  fix.bi.report.definition / fix.bi.report.run (FR-BID-011/017,
      BRU-BID-08/09)
  p3  fix.bi.exploration (FR-BID-018/019, BRU-BID-06)
  p4  fix.bi.alert.instance (FR-BID-025/026, T-14, BRU-BID-14)
  p5  fix.bi.embedded.surface + signed tokens (FR-BID-029, T-08, BRU-BID-12/18)
  p6  low-bandwidth distribution (FR-BID-028)
  p7  fix.bi.content.usage (FR-BID-033)
"""

import base64
import json
import time

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

AUTHOR = "cd_bi_reporting.group_bi_author"
CERTIFIER = "cd_bi_reporting.group_bi_certifier"
FINANCE = "cd_bi_reporting.group_bi_finance"

REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def env(odoo_env):
    if "fix.bi.report.definition" not in odoo_env:
        pytest.skip("cd_bi_reporting 19.0.0.4.0 (second capture pass) is not installed")
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids, share=False):
        counter["n"] += 1
        base = "base.group_portal" if share else "base.group_user"
        groups = [env.ref(base).id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M25 Pass2 %d" % counter["n"],
                    "login": "m25.p2.%d@capture.test" % counter["n"],
                    "email": "m25.p2.%d@capture.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


# ---------------------------------------------------------------------------
# p1 - the dashboard's business owner and the steward's verification
# ---------------------------------------------------------------------------


def _review_dashboard(env, author, owner, **extra):
    steward = env["hr.employee"].create({"name": "P2 Steward"})
    vals = {
        "name": "Branch cockpit",
        "role": "coo",
        "steward_id": steward.id,
        "business_owner_id": owner.id,
        "decision_supported": "Which branch needs a supervisor visit this week",
    }
    vals.update(extra)
    dash = env["fix.bi.dashboard"].with_user(author).create(vals)
    dash.with_user(author).action_submit_review()
    return dash


class TestDashboardOwnershipAndVerification:
    def test_certification_needs_owner_decision_and_verification(self, env, make_user):
        author, steward, owner = make_user(AUTHOR), make_user(CERTIFIER), make_user()
        dash = _review_dashboard(env, author, owner, decision_supported=False)
        with pytest.raises(UserError, match="decision"):
            dash.with_user(author).action_request_approval(justification="x")
        dash.with_user(author).write({"decision_supported": "Weekly branch visits"})
        with pytest.raises(UserError, match="BRU-BID-10"):
            dash.with_user(author).action_request_approval(justification="x")
        dash.with_user(steward).action_steward_verify(note="scope and Bengali checked")
        assert dash.verified_by == steward and dash.verified_at
        dash.with_user(author).action_request_approval(justification="weekly visits")
        assert dash.approval_state == "pending"

    def test_no_business_owner_no_certification(self, env, make_user):
        author, steward = make_user(AUTHOR), make_user(CERTIFIER)
        steward_emp = env["hr.employee"].create({"name": "P2 Steward"})
        dash = (
            env["fix.bi.dashboard"]
            .with_user(author)
            .create(
                {
                    "name": "Orphan",
                    "role": "ceo",
                    "steward_id": steward_emp.id,
                    "decision_supported": "x",
                }
            )
        )
        dash.with_user(author).action_submit_review()
        dash.with_user(steward).action_steward_verify(note="checked")
        with pytest.raises(UserError, match="BRU-BID-07"):
            dash.with_user(author).action_request_approval(justification="x")

    def test_the_author_is_not_the_business_owner(self, env, make_user):
        author = make_user(AUTHOR)
        with pytest.raises(ValidationError, match="functional head"):
            env["fix.bi.dashboard"].with_user(author).create(
                {"name": "Self owned", "role": "ceo", "business_owner_id": author.id}
            )

    def test_only_a_steward_who_is_not_the_author_verifies_in_review(self, env, make_user):
        author, owner = make_user(AUTHOR, CERTIFIER), make_user()
        plain, steward = make_user(AUTHOR), make_user(CERTIFIER)
        dash = _review_dashboard(env, author, owner)
        with pytest.raises(UserError, match="Data Steward act"):
            dash.with_user(plain).action_steward_verify(note="ok")
        with pytest.raises(UserError, match="own dashboard"):
            dash.with_user(author).action_steward_verify(note="ok")
        with pytest.raises(UserError, match="Say what was verified"):
            dash.with_user(steward).action_steward_verify(note="  ")
        dash.with_user(steward).action_steward_verify(note="ok")
        draft = env["fix.bi.dashboard"].with_user(author).create({"name": "Draft", "role": "ceo"})
        with pytest.raises(UserError, match="In Review"):
            draft.with_user(steward).action_steward_verify(note="ok")

    def test_the_named_steward_verifies_their_dashboard(self, env, make_user):
        author, owner = make_user(AUTHOR), make_user()
        named, other = make_user(CERTIFIER), make_user(CERTIFIER)
        emp = env["hr.employee"].create({"name": "Named Steward", "user_id": named.id})
        dash = _review_dashboard(env, author, owner, steward_id=emp.id)
        with pytest.raises(UserError, match="named steward"):
            dash.with_user(other).action_steward_verify(note="ok")
        dash.with_user(named).action_steward_verify(note="ok")
        assert dash.verified_by == named

    def test_editing_the_content_voids_the_verification(self, env, make_user):
        author, owner, steward = make_user(AUTHOR), make_user(), make_user(CERTIFIER)
        dash = _review_dashboard(env, author, owner)
        dash.with_user(steward).action_steward_verify(note="ok")
        dash.with_user(author).write({"business_owner_id": make_user().id})
        assert dash.verified_at, "an ownership change is not a content change"
        dash.with_user(author).write({"role": "cfo"})
        assert not dash.verified_at and not dash.verified_by

    def test_verification_is_never_typed(self, env, make_user):
        author, owner = make_user(AUTHOR), make_user()
        with pytest.raises(ValidationError, match="recorded by its action"):
            env["fix.bi.dashboard"].with_user(author).create(
                {"name": "Typed", "role": "ceo", "verified_at": fields.Datetime.now()}
            )
        dash = _review_dashboard(env, author, owner)
        with pytest.raises(UserError, match="Verify Content"):
            dash.with_user(author).write({"verification_note": "self-verified"})


# ---------------------------------------------------------------------------
# p1 - annotations (FR-BID-009)
# ---------------------------------------------------------------------------


class TestAnnotation:
    def _vals(self, **extra):
        vals = {"name": "Eid dip", "role": "coo", "period": "2026-11", "text_en": "Eid closures"}
        vals.update(extra)
        return vals

    def test_an_author_annotates_a_cockpit_and_it_shows_there(self, env, make_user):
        author = make_user(AUTHOR)
        note = (
            env["fix.bi.annotation"]
            .with_user(author)
            .create(self._vals(metric_key="open_orders", text_bn="ঈদের ছুটি"))
        )
        assert note.author_id == author
        everyone = (
            env["fix.bi.annotation"]
            .with_user(author)
            .create(self._vals(name="All roles", role="all"))
        )
        shown = env["fix.bi.annotation"]._for_role("coo")
        assert note in shown and everyone in shown
        assert note not in env["fix.bi.annotation"]._for_role("cfo")
        note.with_user(author).write({"active": False})
        assert note not in env["fix.bi.annotation"]._for_role("coo")

    def test_a_plain_user_does_not_annotate(self, env, make_user):
        with pytest.raises(REFUSED):
            env["fix.bi.annotation"].with_user(make_user()).create(self._vals())
        # a system administrator passes the ACL but holds no BI role: the
        # model still refuses (the administrator does not read the business, §13)
        with pytest.raises(AccessError, match="BI Author or Data Steward"):
            env["fix.bi.annotation"].with_user(make_user("base.group_system")).create(self._vals())

    def test_a_dashboards_annotation_is_its_business_owners(self, env, make_user):
        author, owner = make_user(AUTHOR), make_user(AUTHOR)
        other = make_user(AUTHOR)
        dash = (
            env["fix.bi.dashboard"]
            .with_user(author)
            .create({"name": "Ops", "role": "coo", "business_owner_id": owner.id})
        )
        with pytest.raises(AccessError, match="business owner"):
            env["fix.bi.annotation"].with_user(other).create(self._vals(dashboard_id=dash.id))
        note = (
            env["fix.bi.annotation"]
            .with_user(owner)
            .create(self._vals(dashboard_id=dash.id, role=False))
        )
        assert note.role == "coo"
        with pytest.raises(ValidationError, match="own cockpit"):
            env["fix.bi.annotation"].with_user(owner).create(
                self._vals(dashboard_id=dash.id, role="cfo")
            )
        with pytest.raises(AccessError, match="Only the author"):
            note.with_user(other).write({"text_en": "rewritten"})

    def test_the_metric_must_be_measured(self, env, make_user):
        with pytest.raises(ValidationError, match="metric bank"):
            env["fix.bi.annotation"].with_user(make_user(AUTHOR)).create(
                self._vals(metric_key="made_up_metric")
            )


# ---------------------------------------------------------------------------
# p2 - library entry and reproducible runs (FR-BID-011/017)
# ---------------------------------------------------------------------------


def _definition(env, user, owner, key="M25:branch_league", **extra):
    vals = {
        "name": "Branch League",
        "report_key": key,
        "business_owner_id": owner.id,
        "definition": "Comparable branch performance on one definition",
    }
    vals.update(extra)
    return env["fix.bi.report.definition"].with_user(user).create(vals)


class TestReportDefinition:
    def test_the_key_must_be_a_library_pack_and_registered_once(self, env, make_user):
        author, owner = make_user(AUTHOR), make_user()
        with pytest.raises(ValidationError, match="report library"):
            _definition(env, author, owner, key="M25:invented_pack")
        _definition(env, author, owner)
        with pytest.raises(Exception, match="(?i)once per company|unique"), env.cr.savepoint():
            _definition(env, author, owner)

    def test_born_draft_and_certified_by_an_independent_steward(self, env, make_user):
        author, steward = make_user(AUTHOR, CERTIFIER), make_user(CERTIFIER)
        owner = make_user(CERTIFIER)
        with pytest.raises(ValidationError, match="draft"):
            _definition(env, author, owner, certification_state="certified")
        rd = _definition(env, author, owner)
        with pytest.raises(UserError, match="Certify / Retire"):
            rd.with_user(author).write({"certification_state": "certified"})
        with pytest.raises(UserError, match="independent check"):
            rd.with_user(author).action_certify()
        with pytest.raises(UserError, match="independent check"):
            rd.with_user(owner).action_certify()
        with pytest.raises(UserError, match="Data Steward act"):
            rd.with_user(make_user(AUTHOR)).action_certify()
        rd.with_user(steward).action_certify()
        assert rd.certification_state == "certified" and rd.certified_by == steward
        rd.with_user(author).write({"definition": "Changed meaning"})
        assert rd.certification_state == "draft" and not rd.certified_by

    def test_at_least_one_output_format(self, env, make_user):
        with pytest.raises(ValidationError, match="output format"):
            _definition(
                env, make_user(AUTHOR), make_user(), fmt_csv=False, fmt_xlsx=False, fmt_pdf=False
            )

    def test_a_run_is_stamped_as_the_caller_and_append_only(self, env, make_user):
        author, steward = make_user(AUTHOR), make_user(CERTIFIER)
        rd = _definition(env, author, make_user())
        with pytest.raises(UserError, match="date"):
            rd.with_user(author).action_generate_run(date_from="last week")
        with pytest.raises(UserError, match="starts after"):
            rd.with_user(author).action_generate_run(date_from="2026-11-10", date_to="2026-11-01")
        res = rd.with_user(author).action_generate_run(date_from="2026-11-01", date_to="2026-11-18")
        run = env["fix.bi.report.run"].browse(res["run_id"])
        assert run.requested_by == author and run.report_key == "M25:branch_league"
        assert run.data_as_of and run.definition_version and run.scope_applied
        assert str(run.period_from) == "2026-11-01" and str(run.period_to) == "2026-11-18"
        assert json.loads(run.parameters) == {"date_from": "2026-11-01", "date_to": "2026-11-18"}
        assert run.duration_ms >= 0 and not run.definition_certified
        with pytest.raises(REFUSED):
            run.with_user(author).write({"row_count": 999})
        # even a system administrator, whom the ACL lets write, cannot edit a run
        with pytest.raises(UserError, match="append-only"):
            run.with_user(make_user("base.group_system")).write({"row_count": 999})
        with pytest.raises(REFUSED):
            env["fix.bi.report.run"].with_user(author).create(
                {
                    "definition_id": rd.id,
                    "company_id": env.company.id,
                    "report_key": "x",
                    "requested_by": author.id,
                    "data_as_of": fields.Datetime.now(),
                }
            )
        with pytest.raises(REFUSED):
            run.with_user(steward).unlink()

    def test_a_finance_pack_run_needs_the_finance_entitlement(self, env, make_user):
        author = make_user(AUTHOR)
        rd = _definition(env, author, make_user(), key="M25:finance_pack", name="Finance Pack")
        with pytest.raises(REFUSED):
            rd.with_user(author).action_generate_run()
        reader = make_user(AUTHOR, FINANCE)
        res = rd.with_user(reader).action_generate_run()
        assert env["fix.bi.report.run"].browse(res["run_id"]).requested_by == reader

    def test_a_restatement_is_flagged_by_a_steward_with_its_reference(self, env, make_user):
        author, steward = make_user(AUTHOR), make_user(CERTIFIER)
        rd = _definition(env, author, make_user())
        run = env["fix.bi.report.run"].browse(rd.with_user(author).action_generate_run()["run_id"])
        with pytest.raises(UserError, match="Data Steward act"):
            run.with_user(author).action_flag_restatement(reference="M62/RST/1")
        with pytest.raises(UserError, match="Name the restatement"):
            run.with_user(steward).action_flag_restatement(reference=" ")
        run.with_user(steward).action_flag_restatement(reference="M62/RST/1")
        assert run.restatement_flag and run.restatement_reference == "M62/RST/1"
        assert run.flagged_by == steward
        with pytest.raises(UserError, match="already flagged"):
            run.with_user(steward).action_flag_restatement(reference="again")

    def test_a_retired_report_is_not_generated(self, env, make_user):
        author, steward = make_user(AUTHOR), make_user(CERTIFIER)
        rd = _definition(env, author, make_user())
        rd.with_user(steward).action_retire()
        with pytest.raises(UserError, match="retired"):
            rd.with_user(author).action_generate_run()
        with pytest.raises(UserError, match="closed"):
            rd.with_user(author).write({"name": "Revived"})


# ---------------------------------------------------------------------------
# p3 - exploration (FR-BID-018/019)
# ---------------------------------------------------------------------------


def _exploration(env, user, **extra):
    vals = {
        "name": "Repair backlog vs SLA",
        "question": "Is the backlog driving SLA breaches?",
        "metric_key": "in_repair",
        "metric_key_2": "sla_overdue",
        "target_role": "service",
    }
    vals.update(extra)
    return env["fix.bi.exploration"].with_user(user).create(vals)


class TestExploration:
    def test_composed_from_measured_metrics_only(self, env, make_user):
        with pytest.raises(ValidationError, match="metric bank"):
            _exploration(env, make_user(AUTHOR), metric_key_3="my_own_formula")

    def test_personal_until_shared_and_only_the_author_changes_it(self, env, make_user):
        author, peer, steward = make_user(AUTHOR), make_user(AUTHOR), make_user(CERTIFIER)
        exp = _exploration(env, author, workspace="shared")
        assert exp.workspace == "personal" and exp.author_id == author
        assert not env["fix.bi.exploration"].with_user(peer).search([("id", "=", exp.id)])
        assert env["fix.bi.exploration"].with_user(steward).search([("id", "=", exp.id)])
        with pytest.raises(UserError, match="their actions"):
            exp.with_user(author).write({"workspace": "shared"})
        exp.with_user(author).action_share()
        assert env["fix.bi.exploration"].with_user(peer).search([("id", "=", exp.id)])
        with pytest.raises(AccessError, match="Only the author"):
            exp.with_user(peer).write({"question": "hijacked"})
        with pytest.raises(AccessError, match="Only the author"):
            exp.with_user(peer).action_promote()

    def test_run_answers_and_promote_builds_a_draft_dashboard(self, env, make_user):
        author = make_user(AUTHOR)
        exp = _exploration(env, author)
        exp.with_user(author).action_run()
        assert exp.last_run_at and "in_repair:" in exp.last_result
        assert "sla_overdue:" in exp.last_result
        exp.with_user(author).action_promote()
        dash = exp.dashboard_id
        assert exp.state == "promoted" and dash.state == "draft"
        assert dash.role == "service" and dash.owner_id == author
        assert json.loads(dash.sections_json) == [{"metrics": ["in_repair", "sla_overdue"]}]
        with pytest.raises(UserError, match="Already promoted"):
            exp.with_user(author).action_promote()
        with pytest.raises(UserError, match="lives on as its dashboard"):
            exp.with_user(author).write({"name": "renamed"})


# ---------------------------------------------------------------------------
# p4 - raised alerts (FR-BID-025/026, T-14, BRU-BID-14)
# ---------------------------------------------------------------------------


@pytest.fixture
def measured(env, monkeypatch):
    """The watched metric's value, set by the test."""
    box = {"value": 0.0}
    cls = type(env["fix.bi.alert.subscription"])
    monkeypatch.setattr(cls, "_current_value", lambda self: box["value"])
    return box


def _alert(env, owner, recipient, escalate_to=None, **extra):
    vals = {
        "name": "Overdue AR",
        "metric_key": "overdue_gt_60d",
        "comparator": "gt",
        "threshold": 100.0,
        "recipients": recipient.login,
        "owner_id": owner.id,
        "escalate_to_id": escalate_to.id if escalate_to else False,
    }
    vals.update(extra)
    return env["fix.bi.alert.subscription"].create(vals)


class TestRaisedAlerts:
    def test_a_crossing_raises_one_alert_and_repeats_are_suppressed(self, env, make_user, measured):
        owner, recipient = make_user(), make_user()
        alert = _alert(env, owner, recipient)
        measured["value"] = 50.0
        alert._evaluate()
        assert not alert.instance_ids
        measured["value"] = 150.0
        alert._evaluate()
        inst = alert.instance_ids
        assert len(inst) == 1 and inst.state == "open" and inst.observed_value == 150.0
        assert inst.routed_to == recipient.login
        measured["value"] = 175.0
        alert._evaluate()
        alert.invalidate_recordset()
        assert len(alert.instance_ids) == 1
        assert inst.repeat_count == 1 and inst.last_observed_value == 175.0

    def test_an_unmeasurable_metric_raises_nothing(self, env, make_user, measured):
        alert = _alert(env, make_user(), make_user())
        measured["value"] = None
        assert alert._evaluate() is False
        assert not alert.instance_ids and not alert.last_checked_at

    def test_acknowledged_by_the_routed_people_then_closed_with_a_reason(
        self, env, make_user, measured
    ):
        owner, recipient, stranger = make_user(), make_user(), make_user()
        alert = _alert(env, owner, recipient)
        measured["value"] = 500.0
        alert._evaluate()
        inst = alert.instance_ids
        with pytest.raises(AccessError):
            inst.with_user(stranger).action_acknowledge(note="mine now")
        with pytest.raises(UserError, match="Acknowledge the alert"):
            inst.with_user(recipient).action_close(note="done")
        inst.with_user(recipient).action_acknowledge(note="chasing the top 5 debtors")
        assert inst.state == "acknowledged" and inst.acknowledged_by == recipient
        with pytest.raises(UserError, match="Say why"):
            inst.with_user(owner).action_close(note="")
        inst.with_user(owner).action_close(note="collected")
        assert inst.state == "closed" and inst.closed_at

    def test_an_acknowledged_alert_closes_on_recovery_an_open_one_waits(
        self, env, make_user, measured
    ):
        recipient = make_user()
        alert = _alert(env, make_user(), recipient, suppression_hours=0)
        measured["value"] = 500.0
        alert._evaluate()
        first = alert.instance_ids
        measured["value"] = 10.0
        alert._evaluate()
        assert first.state == "open", "nobody acknowledged it: it keeps waiting"
        first.with_user(recipient).action_acknowledge(note="on it")
        alert._evaluate()
        assert first.state == "closed" and first.close_note

    def test_an_unacknowledged_alert_escalates(self, env, make_user, measured):
        boss = make_user()
        alert = _alert(env, make_user(), make_user(), escalate_to=boss, escalate_after_hours=2)
        measured["value"] = 500.0
        alert._evaluate()
        inst = alert.instance_ids
        assert env["fix.bi.alert.instance"]._cron_escalate() == 0
        env.flush_all()
        env.cr.execute(
            "UPDATE fix_bi_alert_instance SET raised_at = raised_at - interval '3 hours' WHERE id=%s",
            (inst.id,),
        )
        inst.invalidate_recordset()
        assert env["fix.bi.alert.instance"]._cron_escalate() == 1
        assert inst.state == "escalated" and inst.escalated_to_id == boss
        assert inst.activity_ids.filtered(lambda a: a.user_id == boss)
        inst.with_user(boss).action_acknowledge(note="escalation taken")
        assert inst.state == "acknowledged"

    def test_a_raised_alert_is_never_typed(self, env, make_user, measured):
        alert = _alert(env, make_user(), make_user())
        with pytest.raises(UserError, match="raised by the evaluator"):
            env["fix.bi.alert.instance"].create(
                {"alert_id": alert.id, "company_id": env.company.id, "metric_key": "x"}
            )
        measured["value"] = 500.0
        alert._evaluate()
        with pytest.raises(UserError, match="Acknowledge and Close"):
            alert.instance_ids.write({"state": "closed"})

    def test_windows_must_be_sane(self, env, make_user):
        with pytest.raises(ValidationError, match="suppression"):
            _alert(env, make_user(), make_user(), escalate_after_hours=0)


# ---------------------------------------------------------------------------
# p5 - embedded surfaces and their tokens (FR-BID-029, T-08, BRU-BID-12/18)
# ---------------------------------------------------------------------------


def _surface(env, author, **extra):
    vals = {
        "name": "Order backlog on the WIP board",
        "host_module": "M02",
        "host_screen": "M02-wip",
        "metric_key": "in_repair",
        "context_binding": "scope",
    }
    vals.update(extra)
    return env["fix.bi.embedded.surface"].with_user(author).create(vals)


class TestEmbeddedSurface:
    def test_placement_rules(self, env, make_user):
        author = make_user(AUTHOR)
        with pytest.raises(ValidationError, match="30 to 900"):
            _surface(env, author, token_ttl_seconds=3600)
        with pytest.raises(ValidationError, match="module code"):
            _surface(env, author, host_module="Workshop")
        with pytest.raises(ValidationError, match="BRU-BID-18"):
            _surface(env, author, audience="customer_p01", context_binding="scope")
        with pytest.raises(ValidationError, match="metric bank"):
            _surface(env, author, metric_key="nope")
        portal = _surface(
            env,
            author,
            audience="customer_p01",
            context_binding="viewer_party",
            host_module="P01",
            host_screen="my-history",
        )
        assert portal.state == "draft" and portal.author_id == author

    def test_activated_by_a_steward_who_is_not_the_author(self, env, make_user):
        author, steward = make_user(AUTHOR, CERTIFIER), make_user(CERTIFIER)
        surface = _surface(env, author, state="active")
        assert surface.state == "draft"
        with pytest.raises(UserError, match="Data Steward act"):
            surface.with_user(make_user(AUTHOR)).action_activate()
        with pytest.raises(UserError, match="own surface"):
            surface.with_user(author).action_activate()
        surface.with_user(steward).action_activate()
        assert surface.state == "active" and surface.activated_by == steward
        with pytest.raises(UserError, match="not edited"):
            surface.with_user(author).write({"token_ttl_seconds": 600})

    def test_a_token_is_the_viewers_once_and_until_it_expires(self, env, make_user):
        author, steward, viewer, other = (
            make_user(AUTHOR),
            make_user(CERTIFIER),
            make_user(),
            make_user(),
        )
        surface = _surface(env, author)
        with pytest.raises(UserError, match="not active"):
            surface.with_user(viewer)._issue_token()
        surface.with_user(steward).action_activate()
        issued = surface.with_user(viewer)._issue_token()
        assert issued["expires_in"] == 300
        Surface = env["fix.bi.embedded.surface"]
        with pytest.raises(AccessError, match="another user"):
            Surface.with_user(other)._redeem_token(issued["token"])
        body, sig = issued["token"].rsplit(".", 1)
        forged = json.loads(base64.urlsafe_b64decode(body))
        forged["u"] = other.id
        forged_body = base64.urlsafe_b64encode(json.dumps(forged, sort_keys=True).encode()).decode()
        with pytest.raises(AccessError, match="signature"):
            Surface.with_user(other)._redeem_token("%s.%s" % (forged_body, sig))
        payload = Surface.with_user(viewer)._redeem_token(issued["token"])
        assert payload["s"] == surface.id and payload["u"] == viewer.id
        with pytest.raises(AccessError, match="already used"):
            Surface.with_user(viewer)._redeem_token(issued["token"])

    def test_an_expired_token_is_refused(self, env, make_user, monkeypatch):
        author, steward, viewer = make_user(AUTHOR), make_user(CERTIFIER), make_user()
        surface = _surface(env, author, token_ttl_seconds=30)
        surface.with_user(steward).action_activate()
        issued = surface.with_user(viewer)._issue_token()
        real = time.time
        monkeypatch.setattr(time, "time", lambda: real() + 31)
        with pytest.raises(AccessError, match="expired"):
            env["fix.bi.embedded.surface"].with_user(viewer)._redeem_token(issued["token"])

    def test_the_audience_and_context_bind_the_token(self, env, make_user):
        author, steward = make_user(AUTHOR), make_user(CERTIFIER)
        finance_group = env.ref(FINANCE)
        surface = _surface(
            env, author, audience_group_id=finance_group.id, context_binding="record"
        )
        surface.with_user(steward).action_activate()
        with pytest.raises(AccessError, match="audience"):
            surface.with_user(make_user())._issue_token(record_ref="fix.service.order,1")
        reader = make_user(FINANCE)
        with pytest.raises(UserError, match="record in context"):
            surface.with_user(reader)._issue_token()
        assert surface.with_user(reader)._issue_token(record_ref="fix.service.order,1")["token"]
        portal_surface = _surface(
            env,
            author,
            audience="customer_p01",
            context_binding="viewer_party",
            host_module="P01",
            host_screen="history",
        )
        portal_surface.with_user(steward).action_activate()
        with pytest.raises(AccessError):
            portal_surface.with_user(reader)._issue_token()
        customer = make_user(share=True)
        # as /p03/bi/embed/token does: the placement is read with sudo, the
        # viewer stays the customer and is checked against the audience
        token = portal_surface.with_user(customer).sudo()._issue_token()["token"]
        payload = env["fix.bi.embedded.surface"].with_user(customer)._redeem_token(token)
        assert payload["r"] == "res.partner,%d" % customer.partner_id.id


# ---------------------------------------------------------------------------
# p6 - low-bandwidth delivery (FR-BID-028)
# ---------------------------------------------------------------------------


class TestLowBandwidth:
    def test_a_low_bandwidth_schedule_mails_text_without_an_attachment(self, env, make_user):
        reader = make_user()
        sched = env["fix.bi.distribution.schedule"].create(
            {
                "name": "Branch league for Rangpur",
                "report_key": "M25:branch_league",
                "recipients": reader.login,
                "channel": "low_bandwidth",
                "format": "xlsx",
            }
        )
        before = env["mail.mail"].search([]).ids
        sched.action_send_now()
        mail = env["mail.mail"].search([("id", "not in", before)])
        assert len(mail) == 1 and not mail.attachment_ids
        assert "Branch" in mail.body_html
        log = env["fix.bi.export.log"].search(
            [("pack", "=", "M25:branch_league"), ("channel", "=", "distribution")],
            order="id desc",
            limit=1,
        )
        assert log.format == "text"

    def test_the_summary_is_capped(self, env):
        sched = env["fix.bi.distribution.schedule"].new({"report_key": "M25:x"})
        out = {
            "title": "T",
            "cols": ["a"],
            "labels": {"a": "A"},
            "rows": [{"a": i} for i in range(25)],
        }
        text = sched._low_bandwidth_text(out)
        assert text.count("A: ") == 10 and "+15 more rows" in text
        assert "No rows" in sched._low_bandwidth_text({"title": "T", "rows": []})


# ---------------------------------------------------------------------------
# p7 - usage telemetry (FR-BID-033)
# ---------------------------------------------------------------------------


class TestContentUsage:
    def test_a_view_is_logged_with_its_device_class(self, env, make_user):
        viewer = make_user()
        Usage = env["fix.bi.content.usage"]
        phone = "Mozilla/5.0 (Linux; Android 13; SM-A145F) Mobile Safari/537.36"
        assert Usage.with_user(viewer)._log_view("role_dashboard", "M25:coo", phone)
        assert Usage.with_user(viewer)._log_view("role_dashboard", "M25:coo", "Windows NT 10.0")
        rows = Usage.search([("user_id", "=", viewer.id)], order="id")
        assert rows.mapped("device_class") == ["mobile", "desktop"]
        assert set(rows.mapped("content_ref")) == {"M25:coo"}
        with pytest.raises(UserError, match="append-only"):
            rows[:1].write({"content_ref": "M25:ceo"})

    def test_only_stewards_read_usage(self, env, make_user):
        viewer = make_user()
        env["fix.bi.content.usage"].with_user(viewer)._log_view("role_dashboard", "M25:ceo")
        with pytest.raises(AccessError):
            env["fix.bi.content.usage"].with_user(viewer).search([])
        assert env["fix.bi.content.usage"].with_user(make_user(CERTIFIER)).search([])
