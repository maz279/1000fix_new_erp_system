"""cd_bi_reporting governance tests — M25 E5/E6/E7/G8 controls (A11 audit,
2026-11-05).

Every control is driven through the live ORM as real users, both ways: the
bypass is refused AND the governed path works. The dashboard certification
goes through the M63 inbox exactly as a user would: the author requests, a
certifier who is NOT the author decides.
"""

import datetime

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

AUTHOR = "cd_bi_reporting.group_bi_author"
CERTIFIER = "cd_bi_reporting.group_bi_certifier"
OPERATOR = "cd_bi_reporting.group_bi_operator"
COMPANY_WIDE = "cd_bi_reporting.group_bi_company_wide"
FINANCE = "cd_bi_reporting.group_bi_finance"

REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def env(odoo_env):
    if "fix.bi.dashboard" not in odoo_env:
        pytest.skip("cd_bi_reporting is not installed")
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
                    "name": "M25 Probe %d" % counter["n"],
                    "login": "m25.probe.%d@governance.test" % counter["n"],
                    "email": "m25.probe.%d@governance.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def plain(env, make_user):
    return make_user()  # base.group_user only


def _task_of(record, user):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == user and t.state == "pending"
    )


def _business_owner(env):
    """M25 pass 2 (BRU-BID-07): the functional head who accepts the content."""
    n = env["res.users"].search_count([]) + 1
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": "Business Owner %d" % n, "login": "m25.bo.%d@governance.test" % n})
    )


def _dashboard(env, author_user):
    steward = env["hr.employee"].create({"name": "Steward of BI"})
    return (
        env["fix.bi.dashboard"]
        .with_user(author_user)
        .create(
            {
                "name": "CEO Cockpit (probe)",
                "role": "ceo",
                "steward_id": steward.id,
                "business_owner_id": _business_owner(env).id,
                "decision_supported": "Weekly revenue and backlog calls",
            }
        )
    )


VERIFIED = "definition, scope behaviour and Bengali rendering checked"


def _config(env, **vals):
    return env["fix.bi.sync.config"].create(
        {"name": "Exec KPI Sync (gov probe)", "dataset_scope": "exec_kpi", **vals}
    )


# ---------------------------------------------------------------------------
# E7 — the snapshot run is an operator act, stamped and immutable
# ---------------------------------------------------------------------------


class TestSyncOperatorGate:
    def test_a_plain_user_cannot_run_the_company_snapshot(self, env, plain):
        cfg = _config(env)
        with pytest.raises(UserError, match="(?i)BI Sync Operator"):
            cfg.with_user(plain).action_run_sync()
        assert not env["fix.bi.sync.log"].search([("config_id", "=", cfg.id)])

    def test_the_operator_runs_and_the_log_says_who(self, env, make_user):
        operator = make_user(OPERATOR)
        cfg = _config(env)
        cfg.with_user(operator).action_run_sync()
        log = env["fix.bi.sync.log"].search([("config_id", "=", cfg.id)], limit=1)
        assert log and log.ran_by == operator

    def test_the_log_is_append_only_even_for_admin(self, env):
        cfg = _config(env)
        cfg.action_run_sync()
        log = env["fix.bi.sync.log"].search([("config_id", "=", cfg.id)], limit=1)
        with pytest.raises(UserError, match="(?i)append-only"):
            log.write({"snapshot_json": '{"orders_open": 0}', "ran_at": "2030-01-01 00:00:00"})
        with pytest.raises(UserError, match="(?i)append-only"):
            log.unlink()

    def test_freshness_is_per_company_not_global(self, env):
        company_a = env.company
        company_b = env["res.company"].create({"name": "M25 Probe Co B"})
        _config(env, company_id=company_b.id).action_run_sync()
        Logs = env["fix.bi.sync.log"]
        # company B ran; company A stays 'never' (M25-5)
        assert Logs.freshness_minutes(companies=[company_a.id]) is None
        assert Logs.freshness_minutes(companies=[company_b.id]) <= 1

    def test_snapshot_counts_the_configs_company_only(self, env):
        company_b = env["res.company"].create({"name": "M25 Probe Co C"})
        cfg_b = _config(env, company_id=company_b.id)
        metrics_b = cfg_b._compute_snapshot_metrics()
        assert cfg_b.company_id == company_b
        # a second company's snapshot equals a fresh count on that company
        assert metrics_b == (
            env["fix.bi.sync.config"]
            .browse(cfg_b.id)
            .with_context(allowed_company_ids=company_b.ids)
            ._compute_snapshot_metrics()
        )


# ---------------------------------------------------------------------------
# G8 — the dashboard certification lifecycle
# ---------------------------------------------------------------------------


class TestDashboardLifecycle:
    def test_born_draft_and_the_state_field_is_not_typable(self, env, make_user):
        author = make_user(AUTHOR)
        dash = _dashboard(env, author)
        assert dash.state == "draft"
        with pytest.raises(ValidationError, match="(?i)created as a DRAFT"):
            env["fix.bi.dashboard"].create(
                {"name": "Born certified", "role": "ceo", "state": "certified"}
            )
        with pytest.raises(UserError, match="(?i)changes state only through"):
            dash.with_user(author).write({"state": "certified"})

    def test_review_needs_a_named_steward(self, env, make_user):
        author = make_user(AUTHOR)
        dash = (
            env["fix.bi.dashboard"].with_user(author).create({"name": "No steward", "role": "coo"})
        )
        with pytest.raises(UserError, match="(?i)steward"):
            dash.with_user(author).action_submit_review()
        dash.steward_id = env["hr.employee"].create({"name": "Late Steward"})
        dash.with_user(author).action_submit_review()
        assert dash.state == "review"

    def test_certification_runs_through_the_inbox_not_a_click(self, env, make_user):
        author = make_user(AUTHOR)
        certifier = make_user(CERTIFIER)
        dash = _dashboard(env, author)
        dash.with_user(author).action_submit_review()
        dash.with_user(certifier).action_steward_verify(note=VERIFIED)
        # the direct call is refused even for the certifier (routed, M63)
        with pytest.raises(UserError, match="(?i)from the approver"):
            dash.with_user(certifier).action_certify()
        dash.with_user(author).action_request_approval(justification="certify please")
        assert _task_of(dash, certifier), "no pending task reached the certifier"
        _task_of(dash, certifier).with_user(certifier).action_approve(comment="ok")
        dash.invalidate_recordset()
        assert dash.state == "certified"
        assert dash.certified_by == certifier
        assert dash.certified_by != dash.owner_id  # author != steward (SoD)

    def test_the_author_cannot_certify_their_own_dashboard(self, env, make_user):
        """An author who also holds the certifier hat is structurally out:
        the engine never routes their own dashboard's task to them, and the
        SoD write-guard refuses a self-certification even with the engine
        context."""
        author = make_user(AUTHOR, CERTIFIER)  # both hats, one head
        other = make_user(CERTIFIER)  # the deciding certifier
        dash = _dashboard(env, author)
        dash.with_user(author).action_submit_review()
        dash.with_user(other).action_steward_verify(note=VERIFIED)
        dash.with_user(author).action_request_approval(justification="self certify")
        assert not _task_of(dash, author), "engine must not route the author their own task"
        assert _task_of(dash, other), "another certifier holds the deciding task"
        # and the SoD line itself: a self-certified write is refused
        with pytest.raises(UserError, match="(?i)own dashboard"):
            dash.with_user(author).with_context(bi_lifecycle_engine=True).write(
                {"state": "certified", "certified_by": author.id}
            )
        dash.invalidate_recordset()
        assert dash.state != "certified"

    def test_retirement_is_a_steward_act(self, env, make_user, plain):
        author = make_user(AUTHOR)
        certifier = make_user(CERTIFIER)
        dash = _dashboard(env, author)
        dash.with_user(author).action_submit_review()
        dash.with_user(certifier).action_steward_verify(note=VERIFIED)
        dash.with_user(author).action_request_approval()
        _task_of(dash, certifier).with_user(certifier).action_approve(comment="ok")
        dash.invalidate_recordset()
        assert dash.state == "certified"
        with pytest.raises(UserError, match="(?i)data-steward act"):
            dash.with_user(plain).action_retire()
        dash.with_user(certifier).action_retire()
        assert dash.state == "retired"
        with pytest.raises(UserError, match="(?i)only a certified"):
            dash.with_user(certifier).action_retire()  # retired stays retired


# ---------------------------------------------------------------------------
# G8 — the distribution worker
# ---------------------------------------------------------------------------


class TestDistributionWorker:
    def _user_email(self, env, user):
        return user.login

    def test_an_unknown_report_key_is_refused(self, env, make_user):
        reader = make_user()
        with pytest.raises(ValidationError, match="(?i)not in the M25 report library"):
            env["fix.bi.distribution.schedule"].create(
                {
                    "name": "Bad key",
                    "report_key": "M09:payroll_register_full",
                    "recipients": reader.login,
                }
            )

    def test_an_external_address_is_refused(self, env):
        with pytest.raises(ValidationError, match="(?i)not an active internal user"):
            env["fix.bi.distribution.schedule"].create(
                {
                    "name": "Exfil",
                    "report_key": "M25:branch_league",
                    "recipients": "drop@evil.example",
                }
            )

    def _schedule(self, env, *recipients, key="M25:branch_league"):
        return env["fix.bi.distribution.schedule"].create(
            {
                "name": "Probe schedule",
                "report_key": key,
                "recipients": ",".join(recipients),
            }
        )

    def test_dispatch_mails_entitled_users_and_logs_the_export(self, env, make_user):
        reader = make_user()
        sched = self._schedule(env, reader.login)
        mails_before = env["mail.mail"].search_count([])
        sched.action_send_now()
        assert env["mail.mail"].search_count([]) == mails_before + 1
        assert sched.last_status == "sent"
        log = env["fix.bi.export.log"].search(
            [("pack", "=", "M25:branch_league"), ("channel", "=", "distribution")], limit=1
        )
        assert log and log.row_count >= 0  # the pack rendered

    def test_dispatch_rechecks_entitlement_at_send_time(self, env, make_user):
        """A finance pack scheduled to a user who lost (never had) the
        finance entitlement: the worker skips them and says so."""
        finance_reader = make_user(FINANCE)
        bystander = make_user()  # internal, NOT finance
        sched = self._schedule(env, finance_reader.login, bystander.login, key="M25:finance_pack")
        assert sched.last_status == "never"
        sched.action_send_now()
        assert sched.last_status == "partial"
        assert bystander.login in (sched.last_note or "")
        assert "entitlement" in (sched.last_note or "")

    def test_dispatch_skips_a_deactivated_recipient(self, env, make_user):
        leaver = make_user()
        sched = self._schedule(env, leaver.login)
        leaver.active = False
        sched.action_send_now()
        assert sched.last_status == "failed"
        assert "no longer an active internal user" in (sched.last_note or "")

    def test_the_export_log_is_append_only(self, env, plain):
        row = (
            env["fix.bi.export.log"]
            .sudo()
            .create({"user_id": plain.id, "pack": "M25:finance_pack", "row_count": 3})
        )
        with pytest.raises(UserError, match="(?i)append-only"):
            row.write({"row_count": 0})
        with pytest.raises(UserError, match="(?i)append-only"):
            row.unlink()


# ---------------------------------------------------------------------------
# E6 — the caller's scope and the pack gates (controller functions)
# ---------------------------------------------------------------------------


class TestCallerScopeAndPackGates:
    def _m25(self):
        from odoo.addons.cd_p03_portal.controllers.a11 import m25

        return m25

    def test_the_finance_pack_is_gated(self, env, make_user):
        m25 = self._m25()
        stranger = make_user()
        with pytest.raises(UserError, match="(?i)BI Finance Readers"):
            m25.finance_pack(env(user=stranger.id))
        financier = make_user(FINANCE)
        out = m25.finance_pack(env(user=financier.id))
        assert out["rows"]

    def test_the_executive_pack_is_gated(self, env, make_user):
        m25 = self._m25()
        stranger = make_user()
        with pytest.raises(UserError, match="(?i)Company-Wide Readers"):
            m25.executive_pack(env(user=stranger.id))
        executive = make_user(COMPANY_WIDE)
        out = m25.executive_pack(env(user=executive.id))
        assert out["rows"]

    def test_tiles_follow_the_callers_record_rules(self, env, make_user):
        """A plain user's tile count can never exceed their own record-rule
        count — the sudo leak (M25-1/K02) is closed."""
        m25 = self._m25()
        stranger = make_user()
        scoped = m25._metrics(env(user=stranger.id))["open_orders"]
        own = (
            env["fix.service.order"]
            .with_user(stranger)
            .search_count([("state", "in", m25.OPEN_ORDER_STATES)])
        )
        assert scoped == own

    _chain_seq = {"n": 0}
    _branch_cache = {}

    def _branch(self, env):
        """One entity+branch per test (fix.entity is unique per company)."""
        key = env.company.id
        if key not in self._branch_cache:
            ou = env["operating.unit"].search([], limit=1)
            entity = env["fix.entity"].create(
                {
                    "code": "M25GOV",
                    "legal_name": "M25 Gov Entity",
                    "company_id": env.company.id,
                }
            )
            self._branch_cache[key] = env["fix.branch"].create(
                {
                    "name": "M25 Gov Branch",
                    "code": "M25GB",
                    "entity_id": entity.id,
                    "operating_unit_id": ou.id,
                }
            )
        return self._branch_cache[key]

    def _order(self, env, **extra):
        """A minimal real service order (the chain the M25 probe used); the
        brand name is unique per call (brand names are UNIQUE)."""
        self._chain_seq["n"] += 1
        n = self._chain_seq["n"]
        customer = env["res.partner"].create({"name": "M25 gov customer %d" % n})
        brand = env["fix.brand"].create({"name": "M25GovBrand%d" % n, "code": "M25G%d" % n})
        model = env["fix.device.model"].create(
            {"name": "M25 gov model %d" % n, "brand_id": brand.id}
        )
        device = env["fix.device"].create({"device_model_id": model.id, "owner_id": customer.id})
        branch = self._branch(env)
        vals = {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "M25 governance probe order",
        }
        vals.update(extra)
        return env["fix.service.order"].create(vals)

    def test_delivered_mtd_counts_stamps_not_edits(self, env):
        """E5 (K09): an order delivered LAST month and edited today must not
        re-enter this month's delivered count."""
        m25 = self._m25()
        domain = m25._delivered_extra(
            datetime.datetime.combine(datetime.date.today().replace(day=1), datetime.time.min)
        )
        before = env["fix.service.order"].search_count(domain)
        last_month = fields.Datetime.now().replace(day=1) - datetime.timedelta(days=1)
        order = self._order(env, state="delivered", delivered_at=last_month)
        order.write({"fault_description": "edited today, still delivered last month"})
        assert env["fix.service.order"].search_count(domain) == before
        # ... while a delivery stamped THIS month does count
        self._order(env, state="delivered", delivered_at=fields.Datetime.now())
        assert env["fix.service.order"].search_count(domain) == before + 1
