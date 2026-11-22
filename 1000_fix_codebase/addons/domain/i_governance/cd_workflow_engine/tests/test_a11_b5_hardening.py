"""A11 fix programme B5 (2026-11-23): the approval engine's robustness holes.

Each class closes one audit finding, with the failing-then-passing discipline:

  F10 the decide-path race — two approvers acting in the same window both
     passed _decide_check and both decisions took effect. The decision is now
     atomic: the request's row lock, taken before any write;
  F09 orphaned requests — a pending request with no open task was immortal
     (never swept, only the requester could end it). The cron re-derives the
     approvers once, and the DoA Administrator gets a recorded void;
  F08 the silent keep-pending expiry — one history row nobody read, no event,
     and group-routed approvals (no tier) could never escalate. The expiry now
     publishes approval.expired and the contact centre turns it into the last
     warning;
  F18 cron batches had no per-request isolation — one poisoned record
     aborted the whole hourly run;
  F17 mutual delegation — A could substitute for B while B substituted for A;
  F05 dead DoA rows — three of the live estate's six matrix rows can never
     match a record; the rule book now says so on the row itself (flag only:
     no row and no routing behaviour is changed).

Records are driven as NON-ADMIN users where a role acts; the race test drives
two real cursors, because the window it pins only exists across transactions.
"""

import contextlib
import json
import logging
import types
from datetime import timedelta

import pytest
from odoo import SUPERUSER_ID, api, fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"
DOA = "cd_workflow_engine.group_doa_administrator"
CTX = {"lang": "en_US", "tz": "Asia/Dhaka"}


def _user(env, login, groups=(), employee=False, reachable=False):
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
    if employee:
        env["hr.employee"].create({"name": login, "user_id": user.id})
    if reachable:
        # An address on both channels, so a notification test proves the wire
        # rather than the skip (mirrors the contact-centre notify suite).
        user.partner_id.write({"email": "%s@1000fix.test" % login, "phone": "+88017000022101"})
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    if "fix.complaint" not in env:
        pytest.skip("cd_cx_feedback is not installed")
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([], limit=1)
    x.clerk = _user(env, "b5_clerk")
    x.p = _user(env, "b5_plain")  # the attacker: base.group_user + OU only
    x.t2 = _user(env, "b5_t2", [T2])
    x.t2b = _user(env, "b5_t2b", [T2])
    x.t3 = _user(env, "b5_t3", [T3])
    x.doa = _user(env, "b5_doa", [DOA])
    x.customer = env["res.partner"].create({"name": "B5 Customer"})
    return x


def complaint(c, user=None, amount=3000.0, **kw):
    vals = {
        "name": "B5-%s" % (user or c.clerk).login,
        "customer_id": c.customer.id,
        "operating_unit_id": c.ou.id,
        "description": "b5 hardening probe",
        "severity": "minor",
        "concession_amount": amount,
        "concession_type": "refund",
        "dofa_justification": "Repeat failure on the same repair.",
    }
    vals.update(kw)
    return c.env["fix.complaint"].with_user(user or c.clerk).create(vals)


def task_of(rec, user):
    return rec.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == user
    )


def overdue(req):
    req.task_ids.filtered(lambda t: t.state == "pending")._guarded().write(
        {"due_at": fields.Datetime.now() - timedelta(hours=2)}
    )


def matrix_row(env, **kw):
    vals = {
        "name": "B5 rule",
        "decision_domain": "concession",
        "res_model": "fix.complaint",
        "approval_policy": "any",
        "sla_hours": 4,
        "max_escalations": 1,
        "final_action": "keep",
    }
    vals.update(kw)
    return env["fix.approval.matrix"].create(vals)


def bare_request(c, rec, rule=None, tier=None):
    """A request pinned straight on the record, the shape a group-routed
    record produces (no DOFA tier); tests drive its escalation path with it."""
    req = (
        c.env["fix.approval.request"]
        .sudo()
        .create(
            {
                "res_model": rec._name,
                "res_id": rec.id,
                "res_name": rec.display_name,
                "matrix_id": rule.id if rule else False,
                "decision_domain": "concession",
                "tier": tier or False,
                "requested_by_id": c.clerk.id,
            }
        )
    )
    rec._guarded().write({"approval_state": "pending", "approval_request_id": req.id})
    req._open_tasks([(c.t2, None)])
    req._log("requested")
    return req


# =========================================================================== F10
class TestF10DecidePathRace:
    @staticmethod
    def _wipe(registry, ids):
        """The race test must COMMIT to be a race, so it cleans up after
        itself on this private test database: evidence rows first, then the
        record, then the users and partners."""
        wipe = registry.cursor()
        try:
            wipe.execute("DELETE FROM fix_approval_history WHERE request_id = %s", [ids["req"]])
            wipe.execute(
                "DELETE FROM mail_activity WHERE res_model = %s AND res_id = %s",
                ["fix.complaint", ids["rec"]],
            )
            wipe.execute(
                "DELETE FROM mail_message WHERE model = %s AND res_id = %s",
                ["fix.complaint", ids["rec"]],
            )
            wipe.execute("DELETE FROM fix_workflow_task WHERE request_id = %s", [ids["req"]])
            wipe.execute("DELETE FROM fix_approval_request WHERE id = %s", [ids["req"]])
            wipe.execute(
                "DELETE FROM fix_event_outbox WHERE aggregate = %s AND aggregate_id = %s",
                ["fix.complaint", ids["rec"]],
            )
            wipe.execute("DELETE FROM fix_complaint WHERE id = %s", [ids["rec"]])
            wipe.execute("DELETE FROM res_users WHERE id = ANY(%s)", [ids["users"]])
            wipe.execute("DELETE FROM res_partner WHERE id = ANY(%s)", [ids["partners"]])
            wipe.commit()
        finally:
            wipe.close()

    def test_two_decisions_in_flight_exactly_one_wins(self, odoo_env):
        """Two cursors decide the same request.

        The interleave is the deterministic core of the race: the REJECTER's
        transaction first reads the request as pending — exactly the cache a
        genuinely concurrent decision holds, because Odoo never invalidates
        another transaction's field cache (only the shared ormcache is
        signalled, and only through the HTTP/cron entry points) — then the
        APPROVER decides and commits, then the rejecter continues. Without
        the row lock the rejection overturned a committed approval; the
        loser must instead be told who decided it, and the winner's stamp,
        state and history must stand.
        """
        if "fix.complaint" not in odoo_env:
            pytest.skip("cd_cx_feedback is not installed")
        registry = odoo_env.registry
        ids = {}
        setup = registry.cursor()
        try:
            senv = api.Environment(setup, SUPERUSER_ID, CTX)
            raiser = _user(senv, "b5_race_raiser@m63.test")
            first = _user(senv, "b5_race_first@m63.test", [T2])
            second = _user(senv, "b5_race_second@m63.test", [T2])
            customer = senv["res.partner"].create({"name": "B5 Race Customer"})
            rec = (
                senv["fix.complaint"]
                .with_user(raiser)
                .create(
                    {
                        "name": "B5-RACE",
                        "customer_id": customer.id,
                        "operating_unit_id": senv["operating.unit"].search([], limit=1).id,
                        "description": "b5 race probe",
                        "severity": "minor",
                        "concession_amount": 3000.0,
                        "concession_type": "refund",
                        "dofa_justification": "Repeat failure on the same repair.",
                    }
                )
            )
            rec.with_user(raiser).action_request_approval()
            ids = {
                "req": rec.approval_request_id.id,
                "rec": rec.id,
                "users": [raiser.id, first.id, second.id],
                "partners": [
                    customer.id,
                    raiser.partner_id.id,
                    first.partner_id.id,
                    second.partner_id.id,
                ],
            }
            setup.commit()
        finally:
            setup.close()

        def task_in(cursor_env, uid):
            return cursor_env["fix.workflow.task"].search(
                [
                    ("request_id", "=", ids["req"]),
                    ("assigned_user_id", "=", uid),
                    ("state", "=", "pending"),
                ]
            )

        cur_a, cur_b, check = None, None, None
        try:
            cur_a, cur_b = registry.cursor(), registry.cursor()
            a = api.Environment(cur_a, SUPERUSER_ID, CTX)
            b = api.Environment(cur_b, SUPERUSER_ID, CTX)
            raiser, first, second = ids["users"]
            task_a, task_b = task_in(a, first), task_in(b, second)
            assert task_a and task_b, "both approvers hold a pending task"
            # The rejecter's transaction reads the request NOW: from here on
            # its cache says pending whatever the other transaction commits.
            rejecter = task_b.with_user(second)
            _ = (rejecter.state, rejecter.request_id.state, rejecter.assigned_user_id)
            # The approver decides and commits first.
            task_a.with_user(first).action_approve(comment="first")
            cur_a.commit()
            # The rejecter continues on the stale read.
            refused = None
            try:
                rejecter.action_reject(comment="second, too late")
                refused = False
            except UserError as exc:
                refused = True
                assert "already decided" in str(exc), str(exc)
            if refused:
                cur_b.rollback()
            else:
                # The old behaviour: let the overturn persist so the damage
                # is measured, not assumed.
                cur_b.commit()
            check = registry.cursor()
            v = api.Environment(check, SUPERUSER_ID, CTX)
            req = v["fix.approval.request"].browse(ids["req"])
            rec = v["fix.complaint"].browse(ids["rec"])
            assert refused, "the second decision went through: it overturned the first"
            assert req.state == "approved"
            assert rec.approval_state == "approved" and rec.dofa_approved
            events = req.history_ids.sorted("id").mapped("event")
            assert "approved" in events and "rejected" not in events, events
            assert len(req.history_ids.filtered(lambda h: h.event == "approved")) == 1
            loser_task = v["fix.workflow.task"].search(
                [("request_id", "=", ids["req"]), ("assigned_user_id", "=", second)]
            )
            assert loser_task.state == "cancelled", "the winner closed the loser's task"
        finally:
            for cr in (cur_a, cur_b, check):
                if cr is not None:
                    with contextlib.suppress(Exception):
                        cr.close()
            self._wipe(registry, ids)


# =========================================================================== F09
class TestF09OrphansAreSwept:
    @staticmethod
    def _backdate_past_sla(req, record):
        """Age the request past its SLA the way the cron's clock sees it.

        The record may sit in the requester's environment (ACL write = 0 on
        requests): the sweep is superuser code, so back-date as one."""
        sla = max(req._rule_value("sla_hours"), 1)
        req.sudo().write({"requested_at": fields.Datetime.now() - timedelta(hours=sla + 2)})

    def test_tasks_lost_the_cron_re_routes_the_request(self, c):
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        req = rec.approval_request_id
        assert req.task_ids, "routed in the first place"
        # The evidence's shape (fix_dev APR/2026/00014): zero task rows.
        c.env.cr.execute("DELETE FROM fix_workflow_task WHERE request_id = %s", [req.id])
        c.env.cr.execute(
            "DELETE FROM mail_activity WHERE res_model = %s AND res_id = %s",
            ["fix.complaint", rec.id],
        )
        req.invalidate_recordset()
        self._backdate_past_sla(req, rec)
        c.env["fix.approval.request"].cron_escalate_overdue()
        assert req.state == "pending", "re-routed, not decided"
        fresh = req.task_ids.filtered(lambda t: t.state == "pending")
        assert fresh and c.t2 in fresh.mapped("assigned_user_id")
        assert "requeued" in req.history_ids.mapped("event")
        # The re-route is an approval.requested event, so the approvers get
        # their inbox notice like any fresh request.
        assert (
            c.env["fix.event.outbox"].search_count(
                [
                    ("event_type", "=", "approval.requested"),
                    ("aggregate_id", "=", rec.id),
                ]
            )
            >= 2
        )

    def test_nobody_left_orphan_voids_instead_of_waiting_forever(self, c):
        rec = complaint(c)
        req = bare_request(c, rec, tier=False)  # no coded group: nobody derivable
        c.env.cr.execute("DELETE FROM fix_workflow_task WHERE request_id = %s", [req.id])
        c.env.cr.execute(
            "DELETE FROM mail_activity WHERE res_model = %s AND res_id = %s",
            ["fix.complaint", rec.id],
        )
        req.invalidate_recordset()
        self._backdate_past_sla(req, rec)
        c.env["fix.approval.request"].cron_escalate_overdue()
        assert req.state == "voided"
        assert rec.approval_state == "none"
        row = req.history_ids.filtered(lambda h: h.event == "voided")
        assert row and "nobody can approve" in row.comment
        events = (
            c.env["fix.event.outbox"]
            .sudo()
            .search([("event_type", "=", "approval.decided"), ("aggregate_id", "=", rec.id)])
        )
        assert any(json.loads(e.payload or "{}").get("state") == "voided" for e in events)

    def test_an_orphan_inside_its_sla_is_left_alone(self, c):
        rec = complaint(c)
        req = bare_request(c, rec, tier=False)
        c.env.cr.execute("DELETE FROM fix_workflow_task WHERE request_id = %s", [req.id])
        c.env.cr.execute(
            "DELETE FROM mail_activity WHERE res_model = %s AND res_id = %s",
            ["fix.complaint", rec.id],
        )
        req.invalidate_recordset()
        c.env["fix.approval.request"].cron_escalate_overdue()  # SLA not yet due
        assert req.state == "pending"
        assert not req.history_ids.filtered(lambda h: h.event in ("requeued", "voided"))


class TestF09VoidIntervention:
    def _pending_round_two(self, c):
        """An approved concession re-requested: the old stamp must not survive
        the void (the recall's clearing, mirrored)."""
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        task_of(rec, c.t2).with_user(c.t2).action_approve()
        assert rec.dofa_approved and rec.concession_approved
        rec.with_user(c.clerk).action_request_approval()
        assert rec.approval_state == "pending"
        return rec, rec.approval_request_id

    def test_only_a_doa_administrator_voids(self, c):
        _rec, req = self._pending_round_two(c)
        with pytest.raises(AccessError):
            req.with_user(c.p).action_void_request(reason="The approver left the company.")
        with pytest.raises(AccessError):
            req.with_user(c.t2).action_void_request(reason="The approver left the company.")
        assert req.state == "pending"

    def test_the_reason_is_required_and_kept(self, c):
        _rec, req = self._pending_round_two(c)
        with pytest.raises(UserError, match="at least a sentence"):
            req.with_user(c.doa).action_void_request(reason="short")
        with pytest.raises(UserError, match="at least a sentence"):
            req.with_user(c.doa).action_void_request(reason=None)
        assert req.state == "pending"

    def test_only_a_pending_request_is_voided(self, c):
        rec, req = self._pending_round_two(c)
        task_of(rec, c.t2).with_user(c.t2).action_approve()
        assert req.state == "approved"
        with pytest.raises(UserError, match="Only a pending"):
            req.with_user(c.doa).action_void_request(reason="The round is already decided.")

    def test_the_void_clears_the_stamp_and_records_the_trail(self, c):
        rec, req = self._pending_round_two(c)
        req.with_user(c.doa).action_void_request(
            reason="The approver left the company; re-request under the new DoA."
        )
        assert req.state == "voided" and req.decided_by_id == c.doa
        assert rec.approval_state == "none"
        assert not rec.dofa_approved and not rec.concession_approved
        row = req.history_ids.filtered(lambda h: h.event == "voided")
        assert row and "pending -> voided" in row.comment
        assert "left the company" in row.comment and row.user_id == c.doa
        events = (
            c.env["fix.event.outbox"]
            .sudo()
            .search([("event_type", "=", "approval.decided"), ("aggregate_id", "=", rec.id)])
        )
        assert any(json.loads(e.payload or "{}").get("state") == "voided" for e in events)


# =========================================================================== F08
class TestF08SilentExpiry:
    def test_keep_pending_expiry_publishes_the_last_warning(self, c):
        matrix_row(
            c.env,
            name="B5 keep after no escalation",
            max_escalations=0,
            final_action="keep",
        )
        rec = complaint(c)
        rec.with_user(c.clerk).action_request_approval()
        req = rec.approval_request_id
        overdue(req)
        c.env["fix.approval.request"].cron_escalate_overdue()  # the reminder
        assert req.reminded_at and req.state == "pending"
        overdue(req)
        c.env["fix.approval.request"].cron_escalate_overdue()  # the final action
        assert req.final_action_done and req.state == "pending"  # never auto-approve
        assert "expired" in req.history_ids.mapped("event")
        row = (
            c.env["fix.event.outbox"]
            .sudo()
            .search(
                [("event_type", "=", "approval.expired"), ("aggregate_id", "=", rec.id)], limit=1
            )
        )
        assert row, "the keep-pending expiry published no approval.expired event"
        payload = json.loads(row.payload or "{}")
        assert payload["request"] == req.name and payload["level"] == 0
        assert c.t2.id in payload["waiting_for"], "the event says who it waits for"

    def test_a_group_routed_rule_with_a_named_target_escalates_without_a_tier(self, c):
        rule = matrix_row(
            c.env,
            name="B5 group-routed with a named target",
            res_model=False,
            escalate_to_id=c.t3.id,
            max_escalations=1,
        )
        rec = complaint(c)
        req = bare_request(c, rec, rule=rule, tier=False)
        overdue(req)
        c.env["fix.approval.request"].cron_escalate_overdue()  # the reminder
        overdue(req)
        c.env["fix.approval.request"].cron_escalate_overdue()  # the escalation
        assert req.escalation_level == 1, "no tier, but the rule names its target"
        assert task_of(rec, c.t3) and "escalated" in req.history_ids.mapped("event")
        overdue(req)
        c.env["fix.approval.request"].cron_escalate_overdue()  # then the final action
        assert req.final_action_done and req.state == "pending"
        row = (
            c.env["fix.event.outbox"]
            .sudo()
            .search(
                [("event_type", "=", "approval.expired"), ("aggregate_id", "=", rec.id)], limit=1
            )
        )
        assert row, "the group-routed keep-pending expiry published no event"
        payload = json.loads(row.payload or "{}")
        assert c.t3.id in payload["waiting_for"]

    def test_a_group_routed_rule_without_a_target_takes_its_final_action_and_shouts(self, c):
        matrix_row(c.env, name="B5 group-routed, no target", res_model=False, max_escalations=1)
        rec = complaint(c)
        req = bare_request(c, rec, tier=False)
        overdue(req)
        c.env["fix.approval.request"].cron_escalate_overdue()  # the reminder
        overdue(req)
        c.env["fix.approval.request"].cron_escalate_overdue()  # nothing to escalate to
        assert req.final_action_done and req.state == "pending"
        assert (
            c.env["fix.event.outbox"]
            .sudo()
            .search_count([("event_type", "=", "approval.expired"), ("aggregate_id", "=", rec.id)])
        )


class TestF08ExpiredConsumer:
    """The consumer ships IN this module: cd_contact_centre's files were being
    rewritten by another session while the fix was built (edits reverted within
    seconds, twice), so the engine delivers the last warning itself rather than
    publishing an event nobody consumes."""

    def test_the_shipped_data_file_registers_the_consumer(self, c):
        from odoo.tools import convert_file

        # The shipped data file, loaded the way an upgrade loads it (in the
        # rolled-back test transaction), is the artefact under test.
        convert_file(
            c.env,
            "cd_workflow_engine",
            "data/approval_engine_cron.xml",
            {},
            mode="init",
        )
        row = c.env.ref("cd_workflow_engine.consumer_approval_expired_last_warning")
        assert row.event_type == "approval.expired"
        assert row.model == "fix.approval.request"
        assert row.method == "consume_approval_expired"
        assert row.active, "an inactive subscription never fires"

    def test_the_last_warning_reaches_the_requester_once(self, c):
        clerk = _user(c.env, "b5_notify_clerk")
        rec = complaint(c, user=clerk)
        rec.with_user(clerk).action_request_approval()
        req = rec.approval_request_id
        event = {
            "event_id": "evt-b5-expired-1",
            "payload": {
                "request": req.name,
                "record": rec.display_name,
                "rule": "B5 rule",
                "level": 1,
                "waiting_for": [c.t2.id],
            },
        }
        first = c.env["fix.approval.request"].consume_approval_expired(event)
        assert first["notified"] == 1
        Activity = c.env["mail.activity"].sudo()
        todo = Activity.search(
            [("res_model", "=", req._name), ("res_id", "=", req.id)]
        )
        assert todo and todo.user_id == clerk, todo
        assert req.name in (todo.summary or "")
        assert c.t2.name in (todo.note or "")
        body = " ".join(rec.sudo().message_ids.mapped("body"))
        assert "still pending" in body and req.name in body
        # A replayed event adds no second to-do and no second note.
        again = c.env["fix.approval.request"].consume_approval_expired(event)
        assert again["notified"] == 0
        assert (
            Activity.search_count([("res_model", "=", req._name), ("res_id", "=", req.id)])
            == len(todo)
        )

    def test_the_consumer_refuses_a_direct_call(self, c):
        with pytest.raises(AccessError, match="relay"):
            c.env["fix.approval.request"].with_user(c.clerk).consume_approval_expired({})


# =========================================================================== F18
class TestF18CronIsolation:
    def test_one_poisoned_record_does_not_abort_the_run(self, c, monkeypatch, caplog):
        ok, bad = complaint(c), complaint(c)
        for rec in (ok, bad):
            rec.with_user(c.clerk).action_request_approval()
        req_ok, req_bad = ok.approval_request_id, bad.approval_request_id
        cls = type(bad)
        original = cls._approval_excluded_for

        def poisoned(self, request):
            if self.id == bad.id:
                raise ValueError("poisoned record")
            return original(self, request)

        monkeypatch.setattr(cls, "_approval_excluded_for", poisoned)
        with caplog.at_level(logging.ERROR):
            for _ in range(2):  # reminder pass, then the escalation pass
                overdue(req_ok)
                overdue(req_bad)
                c.env["fix.approval.request"].cron_escalate_overdue()
        assert req_ok.reminded_at, "the healthy request was reminded"
        assert req_ok.escalation_level == 1 and task_of(ok, c.t3), "and escalated"
        assert req_bad.reminded_at, "the poisoned one got its reminder before the poison"
        assert req_bad.state == "pending" and not req_bad.final_action_done
        failures = [
            r.getMessage() for r in caplog.records if "M63 escalation failed" in r.getMessage()
        ]
        assert failures and req_bad.name in failures[0], "the failure was logged with the request"


# =========================================================================== F17
class TestF17MutualDelegation:
    def _sub(self, env, absent, delegate, **kw):
        today = fields.Date.context_today(env["fix.approval.substitution"])
        vals = {
            "absent_approver_id": absent.employee_ids[:1].id,
            "delegate_id": delegate.employee_ids[:1].id,
            "start_date": today,
            "end_date": today + timedelta(days=5),
            "reason": "annual leave",
        }
        vals.update(kw)
        return env["fix.approval.substitution"].create(vals)

    def test_a_and_b_cannot_substitute_for_each_other(self, c):
        a = _user(c.env, "b5_mutual_a", [T2], employee=True)
        b = _user(c.env, "b5_mutual_b", [T2], employee=True)
        self._sub(c.env, a, b, state="active")
        # The other direction is refused when typed active...
        with pytest.raises(ValidationError) as typed:
            self._sub(c.env, b, a, state="active")
        assert a.name in str(typed.value) and b.name in str(typed.value)
        # ...and on the proper path: a draft, activated by the absent approver.
        back = self._sub(c.env, b, a)
        with pytest.raises(UserError, match="Mutual delegation refused"):
            back.with_user(b).action_activate()
        assert back.state == "draft"

    def test_once_the_periods_do_not_overlap_it_is_allowed(self, c):
        a = _user(c.env, "b5_seq_a", [T2], employee=True)
        b = _user(c.env, "b5_seq_b", [T2], employee=True)
        self._sub(c.env, a, b, state="active")
        today = fields.Date.context_today(c.env["fix.approval.substitution"])
        later = self._sub(
            c.env, b, a, start_date=today + timedelta(days=6), end_date=today + timedelta(days=10)
        )
        later.with_user(b).action_activate()
        assert later.state == "active"


# =========================================================================== F05
class TestF05DeadRuleVisibility:
    def test_dead_rows_say_so_and_live_rows_stay_quiet(self, c):
        Matrix = c.env["fix.approval.matrix"]
        dead_domain = Matrix.create(
            {"decision_domain": "write_off", "res_model": False, "name": "B5 dead write-off row"}
        )
        live_domain = Matrix.create(
            {"decision_domain": "concession", "res_model": False, "name": "B5 live domain row"}
        )
        by_model = Matrix.create(
            {
                "decision_domain": "concession",
                "res_model": "fix.complaint",
                "name": "B5 live model row",
            }
        )
        ghost_model = Matrix.create(
            {
                "decision_domain": "concession",
                "res_model": "not.a.model",
                "name": "B5 ghost model row",
            }
        )
        assert dead_domain.matches_any_model is False
        assert "write_off" in dead_domain.rule_note and "can never match" in dead_domain.rule_note
        assert live_domain.matches_any_model is True and not live_domain.rule_note
        assert by_model.matches_any_model is True and not by_model.rule_note
        assert ghost_model.matches_any_model is False
        assert "not.a.model" in ghost_model.rule_note and "can never match" in ghost_model.rule_note
