"""A07 workflow audit, P0 for M45 Enterprise Assets & Test Equipment (E2 + E5).

The A07 probes (working/A07_evidence/probes/m45/probe_m45.py) turned into
controls. Every attack runs as a NON-ADMIN user created here (base.group_user
plus an operating unit: M45 defines no role groups yet). Each control is tested
both ways: the bypass is refused and the proper path still works. `odoo_env`
(addons/conftest.py) rolls everything back.

  M45-1  fitness = the LATEST calibration passed, not past due, in service
  M45-4  the gate runs on issue, issue re-pointing and usage capture
  M45-5  custody truth: no issue of out-of-service / retired items, one open
         issue per item, is_overdue computed at read time
  M45-3  Retrospective Impact window starts at the last pass before the fail
  M45-10 reports and KPIs fenced to the caller's companies
"""

import itertools
from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError

HELD = (UserError, ValidationError)
_SEQ = itertools.count(1)


# A07 ERP audit (2026-11-20) decision D7(a): a pass always carries its
# certificate file and its (here accredited, external) provider
D7A_PDF = "JVBERi0xLjQgQTA3IGNlcnRpZmljYXRl"


def d7a_evidence(env):
    return {
        "provider_id": env.ref("base.partner_admin").id,
        "provider_accredited": True,
        "accreditation_ref": "BAB-17025-TEST",
        "certificate_file": D7A_PDF,
    }


@contextmanager
def refused(env, exc=HELD, match=None):
    with pytest.raises(exc, match=match), env.cr.savepoint():
        yield
    env.invalidate_all()


def _user(env, tag, company=None, groups=()):
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    vals = {
        "name": "M45 %s %d" % (tag, n),
        "login": "a07.m45.%s.%d@a07.test" % (tag, n),
        "group_ids": [(6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])],
        "assigned_operating_unit_ids": [(6, 0, ou.ids)],
        "default_operating_unit_id": ou.id,
    }
    if company:
        vals.update({"company_id": company.id, "company_ids": [(6, 0, company.ids)]})
    user = env["res.users"].with_context(no_reset_password=True).create(vals)
    emp = env["hr.employee"].create({"name": "M45 %s %d (emp)" % (tag, n), "user_id": user.id})
    return user, emp


class M45:
    def __init__(self, env):
        self.env = env
        self.today = fields.Date.today()
        self.clerk, self.clerk_emp = _user(env, "clerk")
        self.clerk2, self.clerk2_emp = _user(env, "clerk2")
        # A07 P1: returning an instrument to service is the Quality Manager's
        self.qm, self.qm_emp = _user(
            env, "qm", groups=("cd_equipment_register.group_quality_manager",)
        )
        # A07 ERP audit (2026-11-20) M45-15: a store keeper issues equipment
        keeper = ("cd_equipment_register.group_equipment_custodian",)
        self.keeper, self.keeper_emp = _user(env, "keeper", groups=keeper)
        self.keeper2, self.keeper2_emp = _user(env, "keeper2", groups=keeper)
        self.n = 0

    def eq(self, **kw):
        self.n += 1
        vals = {"code": "A7P0-EQ-%02d" % self.n, "name": "A7P0 meter %d" % self.n}
        vals.update(kw)
        return self.env["fix.equipment"].create(vals)

    def cal(self, e, on=None, due=None, result="pass", user=None):
        return (
            self.env["fix.calibration"]
            .with_user(user or self.clerk)
            .create(
                {
                    "equipment_id": e.id,
                    "calibrated_on": on or self.today - timedelta(days=10),
                    "next_due": due or self.today + timedelta(days=355),
                    "standard_ref": "STD-A7P0",
                    "result": result,
                    # P0 recipe (M45-2): a pass names its certificate and performer
                    "certificate_ref": "CERT-A7P0",
                    "performed_by": "A7P0 Lab",
                    **d7a_evidence(self.env),
                }
            )
        )

    def fit(self, **kw):
        e = self.eq(**kw)
        self.cal(e)
        return e

    def issue(self, e, user=None, custodian=None, **kw):
        vals = {
            "equipment_id": e.id,
            "custodian_id": (custodian or self.clerk_emp).id,
            "due_on": self.today + timedelta(days=3),
        }
        vals.update(kw)
        return self.env["fix.equipment.issue"].with_user(user or self.keeper).create(vals)

    def usage(self, e, user=None, **kw):
        vals = {"equipment_id": e.id, "job_ref": "A7P0-JOB", "qc_result": "pass"}
        vals.update(kw)
        return self.env["fix.equipment.usage"].with_user(user or self.clerk).create(vals)

    def oos(self, e):
        return self.env["fix.equipment.oos"].create({"equipment_id": e.id, "reason": "fault"})

    def usable(self, e, user=None):
        e = e.with_user(user or self.clerk)
        e.invalidate_recordset()
        try:
            return e.action_assert_usable() is True
        except HELD:
            return False


@pytest.fixture
def m(odoo_env):
    return M45(odoo_env)


# ============================================================ M45-1 fitness rule
def test_never_calibrated_is_unfit(m):
    e = m.eq()
    assert e.calibration_state == "never"
    with refused(m.env, UserError, "never been calibrated"):
        e.with_user(m.clerk).action_assert_usable()


def test_only_calibration_failed_is_unfit(m):
    e = m.eq()
    m.cal(e, result="fail")
    assert not m.usable(e)


def test_fail_after_a_pass_makes_unfit_and_a_new_pass_restores(m):
    """Probe 04: pass at D-100 (due +265), FAIL today: the latest result rules."""
    e = m.eq()
    m.cal(e, on=m.today - timedelta(days=100), due=m.today + timedelta(days=265))
    assert m.usable(e)
    m.cal(e, on=m.today, due=m.today + timedelta(days=1), result="fail")
    assert not m.usable(e)
    assert (e.calibration_state, e.next_calibration) == ("failed", False)
    m.cal(e, on=m.today, due=m.today + timedelta(days=365))  # same day, later record
    assert e.calibration_state == "current"
    # A07 P1: the fail put the instrument out of service (spec 8.1); it is fit
    # again once a Quality Manager accepts the new pass and returns it
    assert e.operational_status == "out_of_service" and not m.usable(e)
    hold = m.env["fix.equipment.oos"].search([("equipment_id", "=", e.id), ("state", "=", "open")])
    hold.with_user(m.qm).action_resolve()
    assert m.usable(e)


def test_overdue_is_unfit(m):
    e = m.eq()
    m.cal(e, on=m.today - timedelta(days=400), due=m.today - timedelta(days=5))
    with refused(m.env, UserError, "Calibration overdue"):
        e.with_user(m.clerk).action_assert_usable()


def test_out_of_service_and_retired_are_unfit(m):
    a = m.fit()
    m.oos(a)
    assert a.operational_status == "out_of_service"
    assert not m.usable(a)
    b = m.fit(operational_status="retired")
    assert not m.usable(b)


def test_issued_item_is_usable_by_its_holder_only(m):
    e = m.fit()
    m.issue(e, custodian=m.clerk_emp)
    assert e.operational_status == "issued"
    assert m.usable(e, m.clerk)  # the holder
    assert not m.usable(e, m.clerk2)  # someone else
    # a holder typed by an RPC caller (P03 kwargs) is ignored: the actor counts
    with refused(m.env, UserError, "only its holder"):
        e.with_user(m.clerk2).action_assert_usable(holder=[m.clerk_emp.id])


def test_result_has_no_default(m):
    """The 'pass' default certified an instrument saved without a result."""
    e = m.eq()
    assert not m.env["fix.calibration"].default_get(["result"]).get("result")
    with refused(m.env, (IntegrityError, *HELD)):
        m.env["fix.calibration"].with_user(m.clerk).create(
            {
                "equipment_id": e.id,
                "calibrated_on": m.today,
                "next_due": m.today + timedelta(days=30),
                "standard_ref": "STD",
            }
        )
    assert not m.usable(e)


# ============================================================ M45-4 gate on every path
@pytest.mark.parametrize("kind", ["never", "failed", "overdue"])
def test_unfit_instrument_cannot_be_issued(m, kind):
    e = m.eq()
    if kind == "failed":
        m.cal(e, result="fail")
    elif kind == "overdue":
        m.cal(e, on=m.today - timedelta(days=400), due=m.today - timedelta(days=1))
    # A07 P1: a failed instrument is also out of service, refused on that ground
    with refused(m.env, UserError, "Cannot issue|cannot be issued"):
        m.issue(e)
    assert e.operational_status == ("out_of_service" if kind == "failed" else "available")
    assert not m.env["fix.equipment.issue"].search([("equipment_id", "=", e.id)])


def test_fit_instrument_is_issued(m):
    e = m.fit()
    i = m.issue(e)
    assert (i.state, e.operational_status) == ("issued", "issued")


def test_issue_cannot_be_repointed_to_an_unfit_instrument(m):
    good, bad = m.fit(), m.eq()
    i = m.issue(good)
    # A07 ERP audit M45-01: an open issue is not re-pointed at all, to an
    # unfit instrument or a fit one: a change is a return and a new issue
    for target in (bad, m.fit()):
        with refused(m.env, UserError, "cannot be set directly"):
            i.with_user(m.keeper).write({"equipment_id": target.id})
    assert (i.equipment_id, good.operational_status) == (good, "issued")


@pytest.mark.parametrize("kind", ["never", "failed", "overdue", "out_of_service", "retired"])
def test_usage_refused_on_unfit_instrument(m, kind):
    if kind == "retired":
        e = m.fit(operational_status="retired")
    else:
        e = m.eq()
        if kind == "failed":
            m.cal(e, result="fail")
        elif kind == "overdue":
            m.cal(e, on=m.today - timedelta(days=400), due=m.today - timedelta(days=1))
        elif kind == "out_of_service":
            m.cal(e)
            m.oos(e)
    with refused(m.env):
        m.usage(e)
    assert not m.env["fix.equipment.usage"].search([("equipment_id", "=", e.id)])


def test_usage_on_fit_instrument_and_by_its_holder(m):
    e = m.fit()
    assert m.usage(e).uses == 1
    m.issue(e, custodian=m.clerk_emp)
    assert m.usage(e, user=m.clerk).uses == 1  # the holder uses his issued meter
    with refused(m.env, UserError, "only its holder"):
        m.usage(e, user=m.clerk2)


def test_usage_cannot_be_repointed_to_an_unfit_instrument(m):
    u = m.usage(m.fit())
    bad = m.eq()
    with refused(m.env, UserError, "never been calibrated"):
        u.with_user(m.clerk).write({"equipment_id": bad.id})


# ============================================================ M45-5 custody truth
def test_out_of_service_item_cannot_be_issued_and_keeps_its_status(m):
    e = m.fit()
    m.oos(e)
    with refused(m.env, UserError, "out of service"):
        m.issue(e)
    assert e.operational_status == "out_of_service"
    # superuser code is trusted for fitness, but not for custody facts
    with refused(m.env, UserError, "out of service"):
        m.env["fix.equipment.issue"].create({"equipment_id": e.id, "custodian_id": m.clerk_emp.id})


def test_retired_item_cannot_be_issued(m):
    e = m.fit(operational_status="retired")
    with refused(m.env, UserError, "retired"):
        m.issue(e)
    assert e.operational_status == "retired"


def test_one_open_issue_per_item(m):
    e = m.fit()
    first = m.issue(e)
    with refused(m.env, ValidationError, "already issued"):
        m.issue(e, user=m.keeper2, custodian=m.clerk2_emp)
    assert (
        m.env["fix.equipment.issue"].search_count(
            [("equipment_id", "=", e.id), ("state", "=", "issued")]
        )
        == 1
    )
    # a returned issue cannot be re-opened beside another open one
    first.action_return(condition="good")
    second = m.issue(e, user=m.keeper2, custodian=m.clerk2_emp)
    # P0 recipe (M45-5): the issue state is guarded, so the re-open is refused
    # before the one-open-issue constraint is even reached
    with refused(m.env, UserError, "cannot be set directly"):
        first.with_user(m.clerk).write({"state": "issued"})
    second.action_return(condition="good")
    assert e.operational_status == "available"


def test_return_does_not_clear_out_of_service(m):
    e = m.fit()
    i = m.issue(e)
    m.oos(e)  # a fault found in the field
    i.with_user(m.clerk).action_return(condition="good")
    assert (i.state, e.operational_status) == ("returned", "out_of_service")


def test_second_return_still_refused(m):
    i = m.issue(m.fit())
    i.with_user(m.clerk).action_return(condition="good")
    with refused(m.env, UserError, "Return an issued item"):
        i.with_user(m.clerk).action_return(condition="good")


def test_is_overdue_is_computed_at_read_time_and_searchable(m):
    Issue = m.env["fix.equipment.issue"]
    assert not Issue._fields["is_overdue"].store
    late = m.issue(m.fit(), due_on=m.today - timedelta(days=1))
    soon = m.issue(m.fit(), due_on=m.today + timedelta(days=1))
    assert (late.is_overdue, soon.is_overdue) == (True, False)
    ids = (late | soon).ids
    scope = [("id", "in", ids)]
    assert Issue.with_user(m.clerk).search([*scope, ("is_overdue", "=", True)]) == late
    assert Issue.with_user(m.clerk).search([*scope, ("is_overdue", "=", False)]) == soon
    assert Issue.with_user(m.clerk).search([*scope, ("is_overdue", "!=", True)]) == soon
    # time passes: five days later the 'soon' issue is overdue too, with no write
    later = m.today + timedelta(days=5)
    with mock.patch.object(fields.Date, "context_today", return_value=later):
        (late | soon).invalidate_recordset(["is_overdue"])
        assert soon.is_overdue is True
        assert Issue.search([*scope, ("is_overdue", "=", True)]) == late | soon
    soon.action_return(condition="good")
    assert Issue.search([*scope, ("is_overdue", "=", True)]) == late


# ============================================================ P03 reports / KPIs
def _report(m, name, user=None):
    from odoo.addons.cd_p03_portal.controllers.a07 import m45

    return getattr(m45, name)(m.env(user=(user or m.clerk).id))


def _row(m, name, e, user=None):
    rows = [r for r in _report(m, name, user)["rows"] if r["code"] == e.code]
    return rows[0] if rows else None


def test_retrospective_impact_counts_since_the_last_pass(m):
    """Probe 15: pass D-100, uses D-50/D-20, fail D-10, use D-5 -> 3 suspect uses."""
    e = m.eq()
    m.cal(e, on=m.today - timedelta(days=100), due=m.today + timedelta(days=265))
    for d in (120, 50, 20, 5):
        m.env["fix.equipment.usage"].create(
            {
                "equipment_id": e.id,
                "job_ref": "A7-JOB-%d" % d,
                "used_on": m.today - timedelta(days=d),
            }
        )
    m.cal(e, on=m.today - timedelta(days=10), due=m.today + timedelta(days=1), result="fail")
    row = _row(m, "retrospective_impact", e)
    assert row["affected_uses"] == 3  # D-120 predates the last good calibration
    # re-calibrated and passed at D-3: the window closes, the later use is clean
    m.cal(e, on=m.today - timedelta(days=3), due=m.today + timedelta(days=362))
    m.env["fix.equipment.usage"].create({"equipment_id": e.id, "job_ref": "A7-JOB-NEW"})
    row = _row(m, "retrospective_impact", e)
    assert row["affected_uses"] == 3
    assert row["window"] == "%s to %s" % (
        m.today - timedelta(days=100),
        m.today - timedelta(days=3),
    )


def test_retrospective_impact_with_no_prior_pass_counts_every_use(m):
    e = m.eq()
    m.env["fix.equipment.usage"].create(
        {"equipment_id": e.id, "job_ref": "A7-OLD", "used_on": m.today - timedelta(days=30)}
    )
    m.cal(e, on=m.today - timedelta(days=2), due=m.today + timedelta(days=30), result="fail")
    assert _row(m, "retrospective_impact", e)["affected_uses"] == 1


def test_compliance_and_kpis_use_the_fitness_rule(m):
    failed = m.eq()
    m.cal(failed, on=m.today - timedelta(days=100), due=m.today + timedelta(days=265))
    m.cal(failed, on=m.today, due=m.today + timedelta(days=365), result="fail")
    never = m.eq()
    current = m.fit()
    statuses = {
        e.code: _row(m, "calibration_compliance", e)["status"] for e in (failed, never, current)
    }
    assert statuses == {
        failed.code: "failed",
        never.code: "never calibrated",
        current.code: "current",
    }
    from odoo.addons.cd_p03_portal.controllers.a07 import m45

    before = m45.kpis(m.env(user=m.clerk.id))["calibration_not_current"]
    m.cal(current, on=m.today, due=m.today + timedelta(days=30), result="fail")
    after = m45.kpis(m.env(user=m.clerk.id))["calibration_not_current"]
    assert after == before + 1


def test_reports_and_kpis_are_fenced_to_the_callers_companies(m):
    other = m.env["res.company"].create({"name": "A7P0 OtherCo"})
    theirs = m.env["fix.equipment"].create(
        {"code": "A7P0-OTHERCO", "name": "OtherCo meter", "company_id": other.id}
    )
    # issued and used first: since A07 P1 the failed calibration below puts the
    # instrument out of service, and an out-of-service item is not issued
    m.env["fix.equipment.usage"].create({"equipment_id": theirs.id, "job_ref": "OTHER"})
    m.env["fix.equipment.issue"].create({"equipment_id": theirs.id, "custodian_id": m.clerk_emp.id})
    m.env["fix.calibration"].create(
        {
            "equipment_id": theirs.id,
            "company_id": other.id,
            "calibrated_on": m.today,
            "next_due": m.today + timedelta(days=30),
            "standard_ref": "STD",
            "result": "fail",
        }
    )
    from odoo.addons.cd_p03_portal.controllers.a07 import m45

    for name in m45.REPORTS:
        assert _row(m, name, theirs) is None, name
    mine = m45.kpis(m.env(user=m.clerk.id))
    other_user, _emp = _user(m.env, "otherco", company=other)
    theirs_kpis = m45.kpis(m.env(user=other_user.id))
    assert _row(m, "retrospective_impact", theirs, other_user)["affected_uses"] == 1
    assert theirs_kpis["equipment_total"] == 1
    assert theirs_kpis["issued_out"] == 1
    assert mine["equipment_total"] == m.env["fix.equipment"].search_count(
        [("company_id", "in", m.clerk.company_ids.ids)]
    )
