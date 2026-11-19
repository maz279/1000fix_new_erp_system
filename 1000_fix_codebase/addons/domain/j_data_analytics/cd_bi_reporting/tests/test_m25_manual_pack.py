"""M25 capture audit (2026-11-13) - the spreadsheet-retirement register
(FR-BID-034) and the two capture defects fixed on the existing forms.

Driven through the ORM as real, non-admin users, both ways: the bypass is
refused AND the governed path works.

  * fix.bi.manual.pack: registered -> parallel run -> (investigated) ->
    accepted -> retired. BRU-BID-16: no retirement without a reconciled
    parallel run; BRU-BID-17: retirement closes the source data; §13 SoD: the
    pack's owner neither reconciles nor retires their own pack.
  * BRU-BID-06: only a certified dashboard can be shared.
  * A schedule sends the format it names (it used to attach CSV whatever the
    format said).
"""

import base64

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

AUTHOR = "cd_bi_reporting.group_bi_author"
CERTIFIER = "cd_bi_reporting.group_bi_certifier"

REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def env(odoo_env):
    if "fix.bi.manual.pack" not in odoo_env:
        pytest.skip("cd_bi_reporting (with the retirement register) is not installed")
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M25 Pack Probe %d" % counter["n"],
                    "login": "m25.pack.%d@capture.test" % counter["n"],
                    "email": "m25.pack.%d@capture.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


def _pack(env, owner, **vals):
    return (
        env["fix.bi.manual.pack"]
        .with_user(owner)
        .create(
            {
                "name": "Monthly branch P&L workbook",
                "function_area": "finance",
                "owner_id": owner.id,
                "frequency": "monthly",
                "effort_hours": 14.5,
                **vals,
            }
        )
    )


class TestRegister:
    def test_a_plain_user_cannot_register_a_pack(self, env, make_user):
        plain = make_user()
        with pytest.raises(AccessError):
            _pack(env, plain)

    def test_an_author_registers_a_pack_as_registered(self, env, make_user):
        author = make_user(AUTHOR)
        pack = _pack(env, author)
        assert pack.state == "registered"
        assert pack.owner_id == author

    def test_the_lifecycle_cannot_be_typed(self, env, make_user):
        author = make_user(AUTHOR)
        with pytest.raises(ValidationError, match="(?i)REGISTERED"):
            _pack(env, author, state="retired")
        with pytest.raises(ValidationError, match="(?i)REGISTERED"):
            _pack(env, author, reconciliation_result="matched")
        pack = _pack(env, author)
        with pytest.raises(UserError, match="(?i)moves only through its actions"):
            pack.with_user(author).write({"state": "accepted"})

    def test_an_unknown_replacement_report_is_refused(self, env, make_user):
        author = make_user(AUTHOR)
        with pytest.raises(ValidationError, match="(?i)not in the M25 report library"):
            _pack(env, author, replacement_report_key="M09:payroll_register_full")

    def test_negative_effort_is_refused(self, env, make_user):
        author = make_user(AUTHOR)
        with pytest.raises(ValidationError, match="(?i)negative"):
            _pack(env, author, effort_hours=-1)


class TestParallelRun:
    def test_no_parallel_run_without_a_replacement(self, env, make_user):
        author = make_user(AUTHOR)
        pack = _pack(env, author)
        with pytest.raises(UserError, match="(?i)name the replacement"):
            pack.with_user(author).action_start_parallel_run()

    def test_an_uncertified_dashboard_is_no_replacement(self, env, make_user):
        author = make_user(AUTHOR)
        dash = (
            env["fix.bi.dashboard"].with_user(author).create({"name": "Draft P&L", "role": "cfo"})
        )
        pack = _pack(env, author, replacement_dashboard_id=dash.id)
        with pytest.raises(UserError, match="(?i)CERTIFIED dashboard"):
            pack.with_user(author).action_start_parallel_run()

    def test_a_library_report_starts_the_parallel_run(self, env, make_user):
        author = make_user(AUTHOR)
        pack = _pack(env, author, replacement_report_key="M25:branch_league")
        pack.with_user(author).action_start_parallel_run()
        assert pack.state == "parallel_run" and pack.parallel_run_started_at


class TestReconcileAndRetire:
    def _running(self, env, owner):
        pack = _pack(env, owner, replacement_report_key="M25:finance_pack")
        pack.with_user(owner).action_start_parallel_run()
        return pack

    def test_only_a_steward_reconciles_and_never_the_owner(self, env, make_user):
        owner = make_user(AUTHOR, CERTIFIER)  # owner who also holds the steward hat
        author = make_user(AUTHOR)
        pack = self._running(env, owner)
        with pytest.raises(UserError, match="(?i)Data Steward act"):
            pack.with_user(author).action_reconcile_matched(note="looks fine")
        with pytest.raises(UserError, match="(?i)cannot reconcile their own"):
            pack.with_user(owner).action_reconcile_matched(note="mine is fine")
        assert pack.state == "parallel_run"

    def test_a_discrepancy_needs_a_note_and_holds_the_retirement(self, env, make_user):
        owner = make_user(AUTHOR)
        steward = make_user(CERTIFIER)
        pack = self._running(env, owner)
        with pytest.raises(UserError, match="(?i)say what differs"):
            pack.with_user(steward).action_reconcile_discrepancy(note="  ")
        pack.with_user(steward).action_reconcile_discrepancy(note="AR total differs by 2.1M")
        assert pack.state == "investigated"
        assert pack.reconciliation_result == "discrepancy"
        assert pack.reconciled_by == steward
        with pytest.raises(UserError, match="(?i)BRU-BID-16"):
            pack.with_user(steward).action_retire()
        # the metric is fixed in M62; the run starts again
        pack.with_user(owner).action_start_parallel_run()
        assert pack.state == "parallel_run" and not pack.reconciliation_result

    def test_retirement_closes_the_source_and_is_never_the_owners_act(self, env, make_user):
        owner = make_user(AUTHOR, CERTIFIER)
        steward = make_user(CERTIFIER)
        pack = self._running(env, owner)
        with pytest.raises(UserError, match="(?i)BRU-BID-16"):
            pack.with_user(steward).action_retire()  # not yet reconciled
        pack.with_user(steward).action_reconcile_matched(note="Jan-Mar match to the taka")
        assert pack.state == "accepted"
        with pytest.raises(UserError, match="(?i)own retirement"):
            pack.with_user(owner).action_retire()
        pack.with_user(steward).action_retire()
        assert pack.state == "retired"
        assert pack.retired_by == steward
        assert pack.source_data_retired_at and pack.retired_at
        with pytest.raises(UserError, match="(?i)retired pack is closed"):
            pack.with_user(owner).write({"name": "Revived"})

    def test_a_retired_pack_cannot_be_deleted(self, env, make_user):
        owner = make_user(AUTHOR)
        steward = make_user(CERTIFIER)
        pack = self._running(env, owner)
        pack.with_user(steward).action_reconcile_matched(note="ok")
        pack.with_user(steward).action_retire()
        with pytest.raises(REFUSED):
            pack.with_user(env.ref("base.user_admin")).unlink()


class TestDashboardSharing:
    def test_a_draft_dashboard_cannot_be_shared(self, env, make_user):
        author = make_user(AUTHOR)
        with pytest.raises(ValidationError, match="(?i)BRU-BID-06"):
            env["fix.bi.dashboard"].with_user(author).create(
                {"name": "Shared draft", "role": "ceo", "is_shared": True}
            )
        dash = env["fix.bi.dashboard"].with_user(author).create({"name": "Draft", "role": "ceo"})
        with pytest.raises(ValidationError, match="(?i)BRU-BID-06"):
            dash.with_user(author).write({"is_shared": True})

    def test_a_certified_dashboard_shares_and_retirement_unshares(self, env, make_user):
        author = make_user(AUTHOR)
        certifier = make_user(CERTIFIER)
        steward = env["hr.employee"].create({"name": "M25 Capture Steward"})
        dash = (
            env["fix.bi.dashboard"]
            .with_user(author)
            .create(
                {
                    "name": "CFO cockpit",
                    "role": "cfo",
                    "steward_id": steward.id,
                    "business_owner_id": certifier.id,
                    "decision_supported": "Month-end close review",
                }
            )
        )
        dash.with_user(author).action_submit_review()
        dash.with_user(certifier).action_steward_verify(note="scope and Bengali checked")
        dash.with_user(author).action_request_approval(justification="month-end")
        task = dash.approval_request_id.task_ids.filtered(
            lambda t: t.assigned_user_id == certifier and t.state == "pending"
        )
        task.with_user(certifier).action_approve(comment="ok")
        dash.invalidate_recordset()
        assert dash.state == "certified"
        dash.with_user(author).write({"is_shared": True})
        assert dash.is_shared
        dash.with_user(certifier).action_retire()
        assert dash.state == "retired" and not dash.is_shared


class TestScheduleFormat:
    def test_the_schedule_sends_the_format_it_names(self, env, make_user):
        reader = make_user()
        sched = env["fix.bi.distribution.schedule"].create(
            {
                "name": "Weekly branch league (xlsx)",
                "report_key": "M25:branch_league",
                "recipients": reader.login,
                "format": "xlsx",
            }
        )
        before = env["mail.mail"].search([]).ids
        sched.action_send_now()
        assert sched.last_status == "sent"
        mail = env["mail.mail"].search([("id", "not in", before)])
        assert len(mail) == 1
        att = mail.attachment_ids
        assert att.name.endswith(".xlsx"), att.name
        assert att.mimetype.endswith("spreadsheetml.sheet"), att.mimetype
        assert base64.b64decode(att.datas)[:2] == b"PK"  # a real workbook, not CSV
        log = env["fix.bi.export.log"].search(
            [("pack", "=", "M25:branch_league"), ("channel", "=", "distribution")],
            order="id desc",
            limit=1,
        )
        assert log.format == "xlsx"
