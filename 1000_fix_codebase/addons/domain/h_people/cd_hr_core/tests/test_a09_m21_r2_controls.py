# A09 M21 round 2 acceptance suite:
#   1. NID, birth registration and e-TIN in the Bangladesh-resident store
#      (M21-A6 / report P2; BRU-HCM-06/07; FF-09);
#   2. the employee.role_changed consumer (C3);
#   3. the s.27(3A) absence timeline, the s.31 service certificate and the s.19
#      death-in-service exit (P2 missing lifecycles);
#   4. the read-only data clean-up findings (decision support).
#
# Evidence standard (BUILD_BRIEF §7): attacks run as freshly created NON-admin
# users through call_kw (with the client-controlled tracking_disable key) and
# the real /p03 controller; SQL proves what the database holds. The residency
# client is an in-memory store (values round-trip) except in the one test that
# proves the real local store answers synthetic values.
import importlib.util
import itertools
import json
from datetime import timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_hr_core.tests.residency_memory import install
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError, ValidationError)
_SEQ = itertools.count(1)
NID, NID2 = "19901234567890123", "2345678901"
TIN, TIN2 = "123456789012", "998877665544"
BRN = "20001234567890123"
MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "19.0.0.3.0" / "post-migrate.py"


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
                "name": "M21R2 User %d" % n,
                "login": "a09-m21r2-%d@test.local" % n,
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
        {"name": "M21R2 Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


def _contract(env, emp, **vals):
    base = {
        "employee_id": emp.id,
        "contract_type": "permanent",
        "joining_date": fields.Date.to_date("2020-01-01"),
        "basic_monthly": 30000.0,
    }
    base.update(vals)
    return env["fix.employment.contract"].create(base)


def _rpc(env, user, model, method, args, kwargs=None):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[model], method, args, kwargs or {}
    )


def _row(env, emp):
    """The whole hr_employee row as text: what the regional database holds."""
    env.flush_all()
    env.cr.execute("SELECT row_to_json(e)::text FROM hr_employee e WHERE id = %s", (emp.id,))
    return env.cr.fetchone()[0]


def _logs(env, emp, field=None):
    domain = [("employee_id", "=", emp.id)]
    if field:
        domain.append(("field_name", "=", field))
    return env["fix.hr.identity.access.log"].sudo().search(domain)


def _task(rec, user):
    return (
        rec.env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("request_id", "=", rec.approval_request_id.id),
                ("assigned_user_id", "=", user.id),
                ("state", "=", "pending"),
            ]
        )
    )


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(r.payload) for r in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def store(monkeypatch):
    return install(monkeypatch)


@pytest.fixture
def w(odoo_env, store):
    class W:
        pass

    c = W()
    env = c.env = odoo_env
    c.store = store
    c.today = fields.Date.context_today(odoo_env.user)
    c.plain = _user(env)
    c.hro = _user(env, "cd_hr_core.group_hr_officer")
    c.hro2 = _user(env, "cd_hr_core.group_hr_officer")
    c.hrm = _user(env, "hr.group_hr_manager")
    c.execu = _user(env, "cd_hr_core.group_hr_executive")
    c.fin = _user(env, "cd_hr_core.group_hr_finance")
    c.it = _user(env, "cd_hr_core.group_clearance_it")
    c.assets = _user(env, "cd_hr_core.group_clearance_assets")
    c.colleague = _emp(env)
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


# ====================================================== 1. identity residency
def test_identity_values_never_land_in_the_regional_database(w):
    """M21-A6: hr_employee holds a pointer and keyed hashes, never the value."""
    ids = _rpc(
        w.env,
        w.hro,
        "hr.employee",
        "create",
        [
            {
                "name": "M21R2 Residency",
                "nid_number": NID,
                "tin_number": TIN,
                "birth_reg_number": BRN,
            }
        ],
    )
    emp = w.env["hr.employee"].browse(ids)
    w.env.cr.precommit.run()  # the chatter's tracking values are written at commit
    row = _row(w.env, emp)
    for value in (NID, TIN, BRN):
        assert value not in row
    assert emp.residency_ref and emp.nid_hash and emp.tin_hash and emp.birth_reg_hash
    assert NID not in emp.nid_hash  # a keyed hash, not the value
    ref = emp.residency_ref
    assert w.store.data == {"hr nid:%s" % ref: NID, "hr tin:%s" % ref: TIN, "hr brn:%s" % ref: BRN}
    # the change is on the history; its value never is
    w.env.cr.execute(
        "SELECT count(*) FROM mail_tracking_value v JOIN mail_message m ON m.id = v.mail_message_id "
        "WHERE m.model = 'hr.employee' AND m.res_id = %s AND (v.old_value_char IN %s OR "
        "v.new_value_char IN %s)",
        (emp.id, (NID, TIN, BRN), (NID, TIN, BRN)),
    )
    assert w.env.cr.fetchone()[0] == 0
    bodies = " ".join(emp.message_ids.mapped("body"))
    assert "NID recorded" in bodies and NID not in bodies
    # ... and the ORM API is unchanged: read back through the residency client
    w.env.invalidate_all()
    got = _rpc(w.env, w.hro, "hr.employee", "read", [[emp.id], ["nid_number", "tin_number"]])
    assert (got[0]["nid_number"], got[0]["tin_number"]) == (NID, TIN)
    assert ("get", "hr nid:%s" % ref) in w.store.calls


@pytest.mark.parametrize(
    "field,value",
    [
        ("nid_number", "NID-ABC-12"),
        ("nid_number", "123456789012"),
        ("tin_number", "12345"),
        ("birth_reg_number", "1234"),
    ],
)
def test_the_format_is_checked_before_the_value_is_routed(w, field, value):
    with pytest.raises(ValidationError, match="not valid"):
        _rpc(w.env, w.hro, "hr.employee", "write", [[w.colleague.id], {field: value}])
    assert not w.store.ops("put")  # nothing left the ERP


def test_duplicate_nid_and_tin_are_refused_through_the_hash(w):
    first = _emp(w.env, nid_number=NID, tin_number=TIN)
    puts = len(w.store.ops("put"))
    other = _emp(w.env)
    with pytest.raises(ValidationError, match="already recorded"):
        _rpc(w.env, w.hro, "hr.employee", "write", [[other.id], {"nid_number": " %s " % NID}])
    with pytest.raises(ValidationError, match="already recorded"):
        _rpc(w.env, w.hro, "hr.employee", "write", [[other.id], {"tin_number": TIN}])
    with pytest.raises(ValidationError, match="already recorded"):
        _rpc(w.env, w.hro, "hr.employee", "create", [{"name": "Dup", "nid_number": NID}])
    assert len(w.store.ops("put")) == puts  # a duplicate is refused before routing
    # a forged hash is refused too (the hash and the pointer are guarded)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc(w.env, w.hro, "hr.employee", "write", [[other.id], {"nid_hash": first.nid_hash}])
    assert not other.nid_hash


def test_search_with_equals_finds_the_employee(w):
    a = _emp(w.env, nid_number=NID, tin_number=TIN)
    b = _emp(w.env, nid_number=NID2)
    Employee = w.env(user=w.hro.id)["hr.employee"].with_context(active_test=False)
    assert Employee.search([("nid_number", "=", NID)]) == a
    assert Employee.search([("tin_number", "=", TIN)]) == a
    assert Employee.search([("nid_number", "in", [NID, NID2])]) == a | b
    assert Employee.search([("nid_number", "ilike", NID2)]) == b  # matched whole
    assert a not in Employee.search([("nid_number", "!=", NID)])
    assert w.colleague in Employee.search([("nid_number", "=", False)])
    assert not Employee.search([("nid_number", "=", "1111111111")])


def test_every_read_is_logged_and_the_log_is_the_hr_managers(w, call):
    a = _emp(w.env, nid_number=NID)
    b = _emp(w.env, nid_number=NID2, tin_number=TIN)
    w.env.invalidate_all()
    # reading other fields reads nothing sensitive
    _rpc(w.env, w.hro, "hr.employee", "read", [[a.id, b.id], ["name"]])
    assert not _logs(w.env, a) and not _logs(w.env, b)
    # one employee's NID: one log row for that employee only (no prefetch)
    _rpc(w.env, w.hro, "hr.employee", "read", [[b.id], ["nid_number"]])
    log = _logs(w.env, b)
    assert len(log) == 1 and not _logs(w.env, a)
    assert (log.user_id, log.field_name, log.employee_name) == (w.hro, "nid_number", b.name)
    # the workspace form logs its reads as the caller too
    res = call(
        w.env(user=w.hro2.id),
        "model_form",
        model="hr.employee",
        fields=[{"name": "name"}, {"name": "nid_number"}],
        record_id=a.id,
    )
    assert "error" not in res, res
    assert _logs(w.env, a, "nid_number").user_id == w.hro2
    # append-only, for everyone
    with pytest.raises(AccessError):
        log.write({"purpose": "forged"})
    with pytest.raises(AccessError):
        log.unlink()
    with pytest.raises(AccessError):
        w.env(user=w.hrm.id)["fix.hr.identity.access.log"].create(
            {"field_name": "nid_number", "user_id": w.hrm.id}
        )
    # HR Manager only reads it
    for user in (w.plain, w.hro):
        with pytest.raises(AccessError):
            _rpc(w.env, user, "fix.hr.identity.access.log", "search_read", [[]], {"limit": 1})
        res = call(w.env(user=user.id), "model_report", module="M21", report="identity_access_log")
        assert res.get("error"), res
    seen = _rpc(w.env, w.hrm, "fix.hr.identity.access.log", "search_read", [[]], {"limit": 50})
    assert {r["employee_name"] for r in seen} >= {a.name, b.name}
    res = call(w.env(user=w.hrm.id), "model_report", module="M21", report="identity_access_log")
    assert not res.get("error") and res["rows"] and NID not in json.dumps(res)


def test_a_plain_user_neither_reads_nor_writes_an_identity_number(w):
    _emp(w.env, nid_number=NID)
    with pytest.raises(AccessError):
        _rpc(w.env, w.plain, "hr.employee", "search_read", [[("nid_number", "=", NID)]])
    with pytest.raises(AccessError):
        _rpc(w.env, w.plain, "hr.employee", "write", [[w.colleague.id], {"nid_number": NID2}])
    assert not w.colleague.nid_hash


def test_an_unchanged_echo_is_no_change_on_the_payroll_gate(w, call):
    """The form posts every field it shows: the NID echoed back is no change,
    so an employee on the payroll can still be saved; a new NID is refused."""
    emp = _emp(w.env, nid_number=NID)
    _contract(w.env, emp, state="active")
    puts = len(w.store.ops("put"))
    res = call(
        w.env(user=w.hro.id),
        "model_write",
        model="hr.employee",
        record_id=emp.id,
        values={"nid_number": NID, "name": emp.name},
    )
    assert "error" not in res, res
    assert len(w.store.ops("put")) == puts
    with pytest.raises(UserError, match="Employee Master Change"):
        _rpc(w.env, w.hro, "hr.employee", "write", [[emp.id], {"nid_number": NID2}])


def test_store_down_refuses_the_write_and_reveals_nothing(w):
    emp = _emp(w.env, nid_number=NID)
    w.store.down = True
    with pytest.raises(UserError, match="unreachable"):
        _rpc(w.env, w.hro, "hr.employee", "write", [[w.colleague.id], {"nid_number": NID2}])
    assert NID2 not in _row(w.env, w.colleague) and not w.colleague.nid_hash
    w.env.invalidate_all()
    got = _rpc(w.env, w.hro, "hr.employee", "read", [[emp.id], ["nid_number"]])
    assert got[0]["nid_number"] is False and not _logs(w.env, emp)


def test_master_change_applies_the_nid_and_keeps_no_number_once_decided(w):
    emp = _emp(w.env, nid_number=NID)
    _contract(w.env, emp, state="active")
    req = w.env(user=w.hro.id)["fix.hr.master.change"].create(
        {"employee_id": emp.id, "reason": "Smart card issued", "proposed_nid_number": NID2}
    )
    req.action_submit()
    _task(req, w.hro2).with_user(w.hro2).action_approve()
    assert req.state == "applied" and not req.proposed_nid_number
    assert emp.nid_hash == emp._fix_identity_hash("nid", NID2)
    assert w.store.data["hr nid:%s" % emp.residency_ref] == NID2
    w.env.flush_all()
    w.env.cr.execute(
        "SELECT proposed_nid_number FROM fix_hr_master_change WHERE id = %s", (req.id,)
    )
    assert w.env.cr.fetchone()[0] is None
    # the duplicate check still holds through the request
    other = w.env(user=w.hro.id)["fix.hr.master.change"].create(
        {"employee_id": w.colleague.id, "reason": "r", "proposed_nid_number": NID2}
    )
    other.action_submit()
    with pytest.raises(ValidationError, match="already recorded"):
        _task(other, w.hro2).with_user(w.hro2).action_approve()


def _migration():
    spec = importlib.util.spec_from_file_location("cd_hr_core_post_migrate_0_3", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.migrate


def _plant_clear_values(env, emp, nid, tin):
    """What a pre-residency row looked like: the values in clear columns."""
    env.flush_all()
    for col in ("nid_number", "tin_number"):
        env.cr.execute("ALTER TABLE hr_employee ADD COLUMN IF NOT EXISTS %s varchar" % col)
    env.cr.execute(
        "UPDATE hr_employee SET nid_number = %s, tin_number = %s, nid_hash = NULL, "
        "tin_hash = NULL, residency_ref = NULL WHERE id = %s",
        (nid, tin, emp.id),
    )
    env.invalidate_all()


def test_the_migration_moves_clear_values_is_idempotent_and_survives_the_store_down(w):
    old = _emp(w.env)
    _plant_clear_values(w.env, old, NID, TIN)
    field = w.env["ir.model.fields"]._get("hr.employee", "nid_number")
    msg = w.env["mail.message"].create({"model": "hr.employee", "res_id": old.id, "body": "x"})
    w.env.cr.execute(
        "INSERT INTO mail_tracking_value (field_id, mail_message_id, old_value_char, "
        "new_value_char) VALUES (%s, %s, %s, %s)",
        (field.id, msg.id, "1111111111", NID),
    )
    migrate = _migration()
    # the store is down: the upgrade does not fail, the row is left as it was ...
    w.store.down = True
    migrate(w.env.cr, "19.0.0.1.0")
    w.env.cr.execute("SELECT nid_number, tin_number FROM hr_employee WHERE id = %s", (old.id,))
    assert w.env.cr.fetchone() == (NID, TIN)
    w.env.invalidate_all()
    # ... but its hash is set: the duplicate is caught before the move
    assert old.nid_hash == old._fix_identity_hash("nid", NID)
    w.store.down = False
    with pytest.raises(ValidationError, match="already recorded"):
        _rpc(w.env, w.hro, "hr.employee", "create", [{"name": "Dup", "nid_number": NID}])
    # the API reads the not-yet-moved value meanwhile
    assert (
        _rpc(w.env, w.hro, "hr.employee", "read", [[old.id], ["nid_number"]])[0]["nid_number"]
        == NID
    )
    # the daily cron (a later run) moves it and nulls the columns
    result = w.env["hr.employee"]._cron_identity_residency_move()
    assert result["moved"] >= 1
    w.env.cr.execute("SELECT nid_number, tin_number FROM hr_employee WHERE id = %s", (old.id,))
    assert w.env.cr.fetchone() == (None, None)
    w.env.cr.execute(
        "SELECT count(*) FROM hr_employee WHERE COALESCE(nid_number, '') <> '' "
        "OR COALESCE(tin_number, '') <> ''"
    )
    assert w.env.cr.fetchone()[0] == 0  # no clear value stays in hr_employee
    w.env.invalidate_all()
    assert w.store.data["hr nid:%s" % old.residency_ref] == NID
    assert w.store.data["hr tin:%s" % old.residency_ref] == TIN
    w.env.cr.execute(
        "SELECT old_value_char, new_value_char FROM mail_tracking_value WHERE mail_message_id = %s",
        (msg.id,),
    )
    assert NID not in w.env.cr.fetchone()
    # idempotent
    puts = len(w.store.ops("put"))
    migrate(w.env.cr, "19.0.0.1.0")
    assert len(w.store.ops("put")) == puts
    w.env.invalidate_all()
    assert (
        _rpc(w.env, w.hro, "hr.employee", "read", [[old.id], ["nid_number"]])[0]["nid_number"]
        == NID
    )
    # only the upgrade and the cron move data
    with pytest.raises(AccessError):
        w.env(user=w.hrm.id)["hr.employee"]._fix_identity_move_clear_values()


def test_the_real_local_store_answers_synthetic_values(odoo_env, monkeypatch):
    """DE-12: the local residency store keeps no value and answers a synthetic
    one. Its echo on a form save is no change."""
    from libs.py import fix_residency

    monkeypatch.setattr(fix_residency, "_client", None)  # a fresh real client
    try:
        health = fix_residency.get_client().health()
    except fix_residency.ResidencyError:
        pytest.skip("the local residency store is not running")
    assert health.get("mode") == "synthetic-only"
    hro = _user(odoo_env, "cd_hr_core.group_hr_officer")
    emp = odoo_env(user=hro.id)["hr.employee"].create({"name": "Synthetic", "nid_number": NID})
    assert NID not in _row(odoo_env, emp)
    odoo_env.invalidate_all()
    served = _rpc(odoo_env, hro, "hr.employee", "read", [[emp.id], ["nid_number"]])[0]
    assert served["nid_number"].startswith("SYNTHETIC-LOCAL-ONLY-")
    # the echo of the synthetic value is the stored NID, not an invalid new one
    _rpc(odoo_env, hro, "hr.employee", "write", [[emp.id], {"nid_number": served["nid_number"]}])
    assert emp.sudo().nid_hash == emp._fix_identity_hash("nid", NID)


# ====================================================== 2. employee.role_changed
def test_a_role_change_opens_one_access_review_and_changes_no_access(w):
    """A role change opens exactly ONE access review and grants nothing.

    Composition with the A10 SoD register (fix.sod_control): a pair a BLOCK
    control governs is refused at the write itself — the documented GRC
    exception on the access-request channel is the only override — so the
    review path is staged with roles no block control governs. A WARN
    control's pair is exactly what the review should surface."""
    Role = w.env["fix.role"]
    blocks = w.env["fix.sod.control"].search([("active", "=", True)])
    blocked = blocks.filtered(lambda c: c.conflict_action == "block")
    user = _user(w.env)
    emp = _emp(w.env, user)
    groups_before = user.group_ids

    if blocked:
        # the A10 P1-3 gate: a conflicting pair never lands on the employee
        pair = blocked[0].role_a_id | blocked[0].role_b_id
        with pytest.raises(ValidationError, match="SoD control"):
            emp.write(
                {"primary_role_id": pair[0].id, "additional_role_ids": [(6, 0, pair[1:].ids)]}
            )
        assert not _events(w.env, "employee.role_changed", emp.id)

    # a role change no block control governs (the FINAL set counts: the
    # employee's existing roles participate, so probe candidates inside a
    # savepoint and keep the first that lands)
    landed = None
    for cand in Role.search([]):
        if cand.id == emp.primary_role_id.id or cand in emp.additional_role_ids:
            continue
        try:
            with w.env.cr.savepoint():
                emp.write({"additional_role_ids": [(4, cand.id)]})
            landed = cand
            break
        except ValidationError:
            continue
    assert landed, "the role register has no role addable free of every SoD control"
    assert _events(w.env, "employee.role_changed", emp.id)
    with pytest.raises(AccessError):
        w.env(user=w.plain.id)["hr.employee"].consume_employee_role_changed(
            {"payload": {"employee_id": emp.id}}
        )
    w.env["fix.event.outbox"].cron_relay()
    reviews = emp.activity_ids.filtered(lambda a: a.summary == "Role change access review")
    assert len(reviews) == 1 and user.login in reviews.note
    assert reviews.user_id != user
    assert "no role-to-group mapping is ruled" in reviews.note
    assert (
        w.env["hr.employee"].consume_employee_role_changed({"payload": {"employee_id": emp.id}})
        is False
    )
    assert user.group_ids == groups_before


# ====================================================== 3. exit lifecycles
def _case(w, emp, days_absent=15, **vals):
    return w.env(user=w.hro.id)["fix.hr.abandonment"].create(
        {
            "employee_id": emp.id,
            "absence_start_date": w.today - timedelta(days=days_absent),
            **vals,
        }
    )


def _age(rec, **dates):
    """Move a case's served dates back (the test stands in for elapsed days)."""
    rec.sudo()._guarded().write(dates)


def test_abandonment_follows_the_s27_3a_timeline_and_is_a_routed_decision(w, call):
    user = _user(w.env, "cd_hr_core.group_hr_officer")  # an HR officer absent himself
    emp = _emp(w.env, user)
    contract = _contract(w.env, emp, state="active")
    with pytest.raises(AccessError):
        _rpc(
            w.env,
            w.plain,
            "fix.hr.abandonment",
            "create",
            [{"employee_id": emp.id, "absence_start_date": str(w.today - timedelta(days=15))}],
        )
    early = _case(w, emp, days_absent=5)
    with pytest.raises(UserError, match="more than 10 days"):
        early.action_issue_notice()
    early.action_cancel()
    case = _case(w, emp)
    # the state is the workflow's, not the form's
    res = call(
        w.env(user=w.hro.id),
        "model_write",
        model="fix.hr.abandonment",
        record_id=case.id,
        values={"state": "deemed"},
    )
    assert res.get("error"), res
    # the worker never runs their own case
    with pytest.raises(UserError, match="about yourself"):
        case.with_user(user).action_issue_notice()
    res = call(
        w.env(user=w.hro.id),
        "model_action",
        model="fix.hr.abandonment",
        ids=[case.id],
        method="action_issue_notice",
    )
    assert res.get("success"), res
    assert case.state == "noticed" and case.reply_due == w.today + timedelta(days=10)
    with pytest.raises(UserError, match="self-defence window"):
        case.with_user(w.hro).action_request_approval()
    Case = w.env["fix.hr.abandonment"]
    Case._cron_abandonment_timeline()
    assert case.state == "noticed"  # the reply window is still open
    _age(case, notice_date=w.today - timedelta(days=11))
    Case._cron_abandonment_timeline()
    assert case.state == "hearing" and case.hearing_due == w.today + timedelta(days=7)
    Case._cron_abandonment_timeline()
    assert case.state == "hearing"
    _age(case, hearing_notice_date=w.today - timedelta(days=8))
    Case._cron_abandonment_timeline()
    assert case.state == "decision" and case.approval_state == "pending"
    # the officer who ran it gets no task and nobody decides outside the inbox
    assert not _task(case, w.hro)
    with pytest.raises(UserError, match="approver's inbox"):
        case.with_user(w.execu).action_deem_resigned()
    _task(case, w.execu).with_user(w.execu).action_approve()
    assert case.state == "deemed" and case.decided_by_id == w.execu
    ex = case.exit_id
    assert (ex.exit_type, ex.state, ex.abandonment_id) == ("abandonment", "notice", case)
    assert ex.last_working_day == case.absence_start_date - timedelta(days=1)
    assert ex.contract_id == contract
    Case._cron_abandonment_timeline()  # idempotent
    assert len(w.env["fix.hr.exit"].search([("abandonment_id", "=", case.id)])) == 1


def test_an_abandonment_exit_is_never_confirmed_by_hand(w):
    # M21 audit E14: a hand-made abandonment exit could never be confirmed yet
    # blocked the real s.27(3A) decision as the employee's open exit; it is
    # now refused when raised, and an abandonment exit can only be confirmed
    # through its case
    with pytest.raises(UserError, match="absence case"):
        w.env(user=w.hro.id)["fix.hr.exit"].create(
            {"employee_id": w.colleague.id, "exit_type": "abandonment"}
        )
    ex = (
        w.env["fix.hr.exit"]
        ._guarded()
        .create({"employee_id": w.colleague.id, "exit_type": "abandonment"})
    )
    with pytest.raises(UserError, match="absence case"):
        ex.with_user(w.hro2).action_confirm_notice()
    assert ex.state == "draft"


def test_an_explanation_stops_the_clock_and_leave_is_not_absence(w):
    emp = _emp(w.env)
    case = _case(w, emp)
    case.action_issue_notice()
    case.write({"explanation": "Hospitalised; certificate attached"})
    case.action_record_explanation()
    assert case.state == "explained"
    _age(case, notice_date=w.today - timedelta(days=30))
    w.env["fix.hr.abandonment"]._cron_abandonment_timeline()
    assert case.state == "explained" and not case.approval_request_id
    # approved leave over the absence: not an absence without leave
    other = _emp(w.env)
    leave_type = w.env["fix.leave.type"].search([], limit=1)
    leave = w.env["fix.leave.request"].create(
        {
            "employee_id": other.id,
            "leave_type_id": leave_type.id,
            "date_from": w.today - timedelta(days=14),
            "date_to": w.today - timedelta(days=12),
        }
    )
    w.env.flush_all()
    w.env.cr.execute("UPDATE fix_leave_request SET state = 'approved' WHERE id = %s", (leave.id,))
    w.env.invalidate_all()
    covered = _case(w, other)
    with pytest.raises(UserError, match="approved leave"):
        covered.action_issue_notice()


def _exit(w, emp, **vals):
    return w.env(user=w.hro.id)["fix.hr.exit"].create(
        {"employee_id": emp.id, "exit_type": "contract_end", **vals}
    )


def _cleared(w, ex):
    ex.with_user(w.hro2).action_confirm_notice()
    ex.with_user(w.it).action_clear_it()
    ex.with_user(w.fin).action_clear_finance()
    ex.with_user(w.hro2).action_clear_hr()
    ex.with_user(w.assets).action_clear_assets()
    ex.with_user(w.hro2).action_clear()
    return ex


def test_service_certificate_is_issued_by_hr_once_and_never_self_issued(w):
    leaver_user = _user(w.env, "cd_hr_core.group_hr_officer")  # an HR officer who leaves
    emp = _emp(w.env, leaver_user, employee_code="E-R2-S31")
    ex = _exit(w, emp, last_working_day=w.today - timedelta(days=1))
    with pytest.raises(UserError, match="cleared exit"):
        ex.with_user(w.hro2).action_issue_service_certificate()
    _cleared(w, ex)
    with pytest.raises(UserError, match="self-issued"):
        ex.with_user(leaver_user).action_issue_service_certificate()
    with pytest.raises(REFUSED):
        ex.with_user(w.plain).action_issue_service_certificate()
    out = _rpc(w.env, w.hro, "fix.hr.exit", "action_issue_service_certificate", [[ex.id]])
    doc = w.env["fix.hr.document"].browse(out["documents"])
    assert ex.service_certificate_id == doc and doc.doc_type == "service_certificate"
    assert doc.generated and not doc.verified  # unsigned until its signed scan is verified
    with pytest.raises(UserError, match="already has"):
        ex.with_user(w.hro).action_issue_service_certificate()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc(w.env, w.hro, "fix.hr.exit", "write", [[ex.id], {"service_certificate_id": False}])


@pytest.fixture
def payroll_hook(w):
    Exit = type(w.env["fix.hr.exit"])
    holder = {"net": 100000.0}

    def _breakdown(self):
        return {"lines": [("Death benefit", holder["net"])], "net": holder["net"], "basis": "hook"}

    with mock.patch.object(Exit, "_fix_settlement_breakdown", _breakdown):
        yield holder


def _nominee(w, emp, pct, name):
    return w.env(user=w.hro.id)["fix.hr.dependant"].create(
        {
            "employee_id": emp.id,
            "name": name,
            "relation": "child",
            "is_nominee": True,
            "nominee_pct": pct,
        }
    )


def test_death_in_service_settles_to_the_nominees_and_pins_the_split(w, payroll_hook):
    emp = _emp(w.env)
    _contract(w.env, emp, state="active")
    ex = _exit(w, emp, exit_type="death", last_working_day=w.today - timedelta(days=2))
    assert ex.notice_required_days == 0 and "s.19" in ex.notice_basis
    with pytest.raises(UserError, match="death certificate"):
        ex.with_user(w.hro2).action_confirm_notice()
    ex.write({"death_certificate_file": "ZGVhdGg=", "death_at_work": True})
    first = _nominee(w, emp, 60.0, "Nominee A")
    with pytest.raises(UserError, match=r"total 60.00%"):
        ex.with_user(w.hro2).action_confirm_notice()
    second = _nominee(w, emp, 40.0, "Nominee B")
    _cleared(w, ex)
    with pytest.raises(UserError, match="keeps its terms"):
        _rpc(w.env, w.hro, "fix.hr.exit", "write", [[ex.id], {"death_at_work": False}])
    ex.with_user(w.hro2).action_compute_settlement()
    payees = ex._fix_nominee_payees()
    assert [(p["name"], p["amount"]) for p in payees] == [
        ("Nominee A", 60000.0),
        ("Nominee B", 40000.0),
    ]
    ex.with_user(w.hro2).action_request_approval()
    # a nominee changed after routing: the approved split no longer holds
    first.write({"nominee_pct": 50.0})
    second.write({"nominee_pct": 50.0})
    task = _task(ex, w.fin)
    with pytest.raises(UserError, match="route it again"):
        task.with_user(w.fin).action_approve()
    assert ex.state == "cleared"


def test_the_death_settlement_figure_comes_from_payroll_never_typed(w):
    """I1: payroll computes the s.19 figure. Without payroll's death rule the
    settlement is refused; with it (cd_payroll_bd, A09 round 2) the figure is
    payroll's breakdown, pinned, and never a typed amount."""
    emp = _emp(w.env)
    _contract(w.env, emp, state="active")
    _nominee(w, emp, 100.0, "Sole Nominee")
    ex = _exit(w, emp, exit_type="death", death_certificate_file="ZGVhdGg=")
    _cleared(w, ex)
    if "fix.payroll.period" not in w.env:
        with pytest.raises(UserError):
            ex.with_user(w.hro2).action_compute_settlement()
        assert not ex.settlement_amount and not ex.settlement_digest
        return
    ex.with_user(w.hro2).action_compute_settlement()
    breakdown = ex._fix_settlement_breakdown()
    assert ex.settlement_digest
    assert ex.settlement_amount == breakdown["net"]
    with pytest.raises(UserError, match="changes only through its workflow"):
        ex.with_user(w.hro2).write({"settlement_amount": 1.0})


# ====================================================== 4. data clean-up
def _writes(env):
    env.cr.execute(
        "SELECT COALESCE(sum(n_tup_ins + n_tup_upd + n_tup_del), 0) FROM pg_stat_xact_user_tables"
    )
    return env.cr.fetchone()[0]


def test_cleanup_findings_are_read_only_and_for_the_hr_manager(w, call):
    env = w.env
    # legacy data the new constraints would refuse today, planted by SQL
    twice = _emp(env)
    c1 = _contract(env, twice, state="active")
    c2 = _contract(env, twice, joining_date=fields.Date.to_date("2021-01-01"))
    env.flush_all()
    env.cr.execute("UPDATE fix_employment_contract SET state = 'active' WHERE id = %s", (c2.id,))
    gone_user = _user(env)
    gone = _emp(env, gone_user)
    gone.sudo()._guarded().write({"left_date": w.today - timedelta(days=3)})
    doc = env["fix.hr.document"].create({"employee_id": twice.id, "doc_type": "nda"})
    env.flush_all()
    env.cr.execute("UPDATE fix_hr_document SET verified = TRUE WHERE id = %s", (doc.id,))
    leave_type = env["fix.leave.type"].search([], limit=1)
    leaves = env["fix.leave.request"].create(
        [
            {
                "employee_id": twice.id,
                "leave_type_id": leave_type.id,
                "date_from": w.today + timedelta(days=d),
                "date_to": w.today + timedelta(days=d),
            }
            for d in (10, 20)
        ]
    )
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_leave_request SET state = 'approved', date_from = %s, date_to = %s "
        "WHERE id IN %s",
        (w.today + timedelta(days=10), w.today + timedelta(days=12), tuple(leaves.ids)),
    )
    env.invalidate_all()
    # refused to anyone but the HR Manager
    for user in (w.plain, w.hro):
        with pytest.raises(AccessError):
            _rpc(env, user, "hr.employee", "fix_data_cleanup_findings", [])
    before = _writes(env)
    rows = _rpc(env, w.hrm, "hr.employee", "fix_data_cleanup_findings", [])
    assert _writes(env) == before  # read-only: not one row inserted, updated or deleted
    found = {(r["category"], r["employee_id"]) for r in rows}
    assert ("Multiple active contracts", twice.id) in found
    assert ("Overlapping leave", twice.id) in found
    assert ("Exited but still active", gone.id) in found
    assert ("Decorative flag: document", twice.id) in found
    assert c1.state == "active" and gone_user.active  # nothing was cleaned
    res = call(env(user=w.hrm.id), "model_report", module="M21", report="data_cleanup")
    assert not res.get("error") and len(res["rows"]) == len(rows)
    res = call(env(user=w.hro.id), "model_report", module="M21", report="data_cleanup")
    assert res.get("error")


# ====================================================== 1b. passport, nominee NID, dependant NID
PASSPORT, NOMINEE_NID, DEP_NID = "EB0123456", "19801234567890123", "3456789012"


def _dependant(env, user, emp, **vals):
    ids = _rpc(
        env,
        user,
        "fix.hr.dependant",
        "create",
        [{"employee_id": emp.id, "name": "M21R2 Dependant", "relation": "child", **vals}],
    )
    return env["fix.hr.dependant"].browse(ids)


def _dependant_row(env, dep):
    env.flush_all()
    env.cr.execute("SELECT row_to_json(d)::text FROM fix_hr_dependant d WHERE id = %s", (dep.id,))
    return env.cr.fetchone()[0]


def test_passport_nominee_and_dependant_nid_are_held_in_the_store(w):
    emp = _emp(w.env)
    _rpc(
        w.env,
        w.hro,
        "hr.employee",
        "write",
        [[emp.id], {"passport_number": PASSPORT, "nominee_nid": NOMINEE_NID}],
    )
    dep = _dependant(w.env, w.hro, emp, nid=DEP_NID)
    row, dep_row = _row(w.env, emp), _dependant_row(w.env, dep)
    assert PASSPORT not in row and NOMINEE_NID not in row and DEP_NID not in dep_row
    assert emp.passport_hash and emp.nominee_nid_hash and dep.nid_hash and dep.residency_ref
    assert w.store.data["hr passport:%s" % emp.residency_ref] == PASSPORT
    assert w.store.data["hr nominee nid:%s" % emp.residency_ref] == NOMINEE_NID
    assert w.store.data["hr dependant nid:%s" % dep.residency_ref] == DEP_NID
    w.env.invalidate_all()
    got = _rpc(w.env, w.hro, "hr.employee", "read", [[emp.id], ["passport_number", "nominee_nid"]])
    assert (got[0]["passport_number"], got[0]["nominee_nid"]) == (PASSPORT, NOMINEE_NID)
    assert _rpc(w.env, w.hro, "fix.hr.dependant", "read", [[dep.id], ["nid"]])[0]["nid"] == DEP_NID
    # each read is logged against the employee, the dependant's naming its record
    assert set(_logs(w.env, emp).mapped("field_name")) == {"passport_number", "nominee_nid", "nid"}
    dep_log = _logs(w.env, emp, "nid")
    assert (dep_log.record_model, dep_log.record_id, dep_log.user_id) == (
        "fix.hr.dependant",
        dep.id,
        w.hro,
    )
    # search with = still finds them
    assert w.env(user=w.hro.id)["hr.employee"].search([("passport_number", "=", PASSPORT)]) == emp
    assert w.env(user=w.hro.id)["fix.hr.dependant"].search([("nid", "=", DEP_NID)]) == dep
    # the hash and the pointer are not the form's to set
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc(w.env, w.hro, "fix.hr.dependant", "write", [[dep.id], {"nid_hash": "forged"}])


@pytest.mark.parametrize(
    "model,field,value",
    [
        ("hr.employee", "nominee_nid", "NOM-1"),
        ("hr.employee", "nominee_nid", "123456789012"),
        ("fix.hr.dependant", "nid", "12345"),
    ],
)
def test_nominee_and_dependant_nid_formats_are_checked_before_routing(w, model, field, value):
    target = w.colleague if model == "hr.employee" else _dependant(w.env, w.hro, w.colleague)
    with pytest.raises(ValidationError, match="not valid"):
        _rpc(w.env, w.hro, model, "write", [[target.id], {field: value}])
    assert not w.store.ops("put")


def test_the_migration_moves_passport_nominee_and_dependant_nid(w):
    emp = _emp(w.env)
    dep = _dependant(w.env, w.hro, emp)
    w.env.flush_all()
    w.env.cr.execute("ALTER TABLE hr_employee ADD COLUMN IF NOT EXISTS passport_number varchar")
    w.env.cr.execute("ALTER TABLE hr_employee ADD COLUMN IF NOT EXISTS nominee_nid varchar")
    w.env.cr.execute("ALTER TABLE fix_hr_dependant ADD COLUMN IF NOT EXISTS nid varchar")
    w.env.cr.execute(
        "UPDATE hr_employee SET passport_number = %s, nominee_nid = %s WHERE id = %s",
        (PASSPORT, NOMINEE_NID, emp.id),
    )
    w.env.cr.execute("UPDATE fix_hr_dependant SET nid = %s WHERE id = %s", (DEP_NID, dep.id))
    w.env.invalidate_all()
    migrate = _migration()
    w.store.down = True
    migrate(w.env.cr, "19.0.0.2.0")  # the store is down: nothing fails, nothing moves
    w.env.cr.execute("SELECT nid FROM fix_hr_dependant WHERE id = %s", (dep.id,))
    assert w.env.cr.fetchone()[0] == DEP_NID
    w.env.invalidate_all()
    assert dep.nid_hash == dep._fix_identity_hash("dependant_nid", DEP_NID)
    w.store.down = False
    result = w.env["hr.employee"]._cron_identity_residency_move()
    assert result["moved"] >= 2 and result["dependants_moved"] >= 1
    w.env.cr.execute(
        "SELECT count(*) FROM hr_employee WHERE COALESCE(passport_number, '') <> '' "
        "OR COALESCE(nominee_nid, '') <> ''"
    )
    assert w.env.cr.fetchone()[0] == 0
    w.env.cr.execute("SELECT count(*) FROM fix_hr_dependant WHERE COALESCE(nid, '') <> ''")
    assert w.env.cr.fetchone()[0] == 0  # no clear value left in either table
    w.env.invalidate_all()
    assert w.store.data["hr dependant nid:%s" % dep.residency_ref] == DEP_NID
    assert w.store.data["hr passport:%s" % emp.residency_ref] == PASSPORT
    puts = len(w.store.ops("put"))
    migrate(w.env.cr, "19.0.0.2.0")  # idempotent
    assert len(w.store.ops("put")) == puts


def test_generated_form7_shows_only_the_last_four_digits_of_the_nid(w):
    import base64

    emp = _emp(w.env, nid_number=NID)
    docs = emp.with_user(w.hro).action_generate_form7_service_book()
    text = base64.b64decode(docs.sudo().file_data).decode()
    assert NID not in text
    assert "NID / Smart Card: %s%s" % ("*" * (len(NID) - 4), NID[-4:]) in text
    assert _logs(w.env, emp, "nid_number").purpose == "Form 7 service book (masked)"
