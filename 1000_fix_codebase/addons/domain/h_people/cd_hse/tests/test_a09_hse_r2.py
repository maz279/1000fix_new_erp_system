# A09 M59 round-2 acceptance suite: anonymous reporting (BRU-HSE-01, T-10),
# the fitness-status split and return to work (FR-HSE-037, BRU-HSE-14/15),
# the PPE replacement cron (FR-HSE-032), line and branch manager read of
# incidents, investigation and CAPA as child records (M59-F8), driving-licence
# eligibility (BRU-HSE-07, FR-HSE-019) and lone-worker sessions opened by a
# dispatcher (FR-HSE-022).
#
# Same standard as test_a09_hse_controls.py, whose cast and helpers this file
# reuses: every attack runs as a freshly created NON-admin user.
import importlib.util
import types
from datetime import timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_hse.tests.test_a09_hse_controls import (
    _SEQ,
    REFUSED,
    FakeRequest,
    _capa,
    _driver,
    _investigated,
    _notify,
    _report,
    _rpc_write,
    _serious,
    _user,
    make_x,
)
from odoo.addons.cd_p03_portal.controllers import a09
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations" / "19.0.0.4.0"


@pytest.fixture
def x(odoo_env):
    return make_x(odoo_env)


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


def _traces(env, user, incident_id):
    """Every place a reporter's identity could be stored for an incident."""
    cr = env.cr
    env.flush_all()
    cr.execute(
        "SELECT create_uid, write_uid, employee_id FROM fix_hse_incident WHERE id = %s",
        (incident_id,),
    )
    row = cr.fetchone()
    cr.execute(
        "SELECT count(*) FROM mail_message WHERE model = 'fix.hse.incident' AND res_id = %s "
        "AND (author_id = %s OR create_uid = %s)",
        (incident_id, user.partner_id.id, user.id),
    )
    messages = cr.fetchone()[0]
    cr.execute(
        "SELECT count(*) FROM mail_followers WHERE res_model = 'fix.hse.incident' "
        "AND res_id = %s AND partner_id = %s",
        (incident_id, user.partner_id.id),
    )
    followers = cr.fetchone()[0]
    cr.execute(
        "SELECT count(*) FROM fix_event_outbox WHERE aggregate_id = %s AND create_uid = %s",
        (incident_id, user.id),
    )
    events = cr.fetchone()[0]
    return row, messages, followers, events


# ============================================ anonymous reporting (BRU-HSE-01)
def test_an_anonymous_report_stores_no_user_id(x):
    ids = call_kw(
        x.env(user=x.plain.id, context={"tracking_disable": True})["fix.hse.incident"],
        "create",
        [
            {
                "anonymous": True,
                "incident_type": "near_miss",
                "description": "Frayed mains lead at bench 4",
                "branch_id": x.branch.id,
            }
        ],
        {},
    )
    incident_id = ids[0] if isinstance(ids, list) else ids
    (create_uid, write_uid, employee_id), messages, followers, events = _traces(
        x.env, x.plain, incident_id
    )
    assert x.plain.id not in (create_uid, write_uid) and employee_id is None
    assert messages == 0 and followers == 0 and events == 0
    inc = x.env["fix.hse.incident"].browse(incident_id)
    assert inc.anonymous and not inc.employee_id
    # the reporter keeps no access to it, and it cannot be "un-anonymised"
    assert not x.env(user=x.plain.id)["fix.hse.incident"].search([("id", "=", incident_id)])
    with pytest.raises(UserError, match="fixed when it is filed"):
        _rpc_write(x.env, x.hse, inc, {"anonymous": False})


def test_an_anonymous_report_through_the_workspace_form(x, call):
    res = call(
        x.env(user=x.plain.id),
        "model_write",
        model="fix.hse.incident",
        values={
            "anonymous": True,
            "incident_type": "injury",
            "severity": "medium",
            "description": "Colleague cut by a screen panel",
            "branch_id": x.branch.id,
            "injured_employee_id": x.colleague.employee_id.id,
        },
    )
    assert res.get("id"), res
    (create_uid, _w, employee_id), messages, followers, _e = _traces(x.env, x.plain, res["id"])
    assert create_uid != x.plain.id and employee_id is None and not messages and not followers
    inc = x.env["fix.hse.incident"].browse(res["id"])
    # a reportable injury still enters the Form 28 register, under the worker hurt
    assert inc.statutory_record_id.employee_id == x.colleague.employee_id


def test_an_anonymous_report_carries_no_reporter_field(x):
    with pytest.raises(UserError, match="not employee_id"):
        x.env(user=x.plain.id)["fix.hse.incident"].create(
            {
                "anonymous": True,
                "description": "x",
                "employee_id": x.plain.employee_id.id,
            }
        )


def test_the_hse_officer_triages_an_anonymous_report(x):
    inc = x.env(user=x.plain.id)["fix.hse.incident"].create(
        {
            "anonymous": True,
            "incident_type": "injury",
            "severity": "high",
            "description": "Someone fell from the ladder at the depot",
            "branch_id": x.branch.id,
        }
    )
    inc = x.env["fix.hse.incident"].browse(inc.id)
    assert not inc.statutory_record_id  # no worker named: never refused, waits for triage
    with pytest.raises(AccessError):
        inc.with_user(x.plain).action_triage(note="x")
    with pytest.raises(UserError, match="triage note"):
        inc.with_user(x.hse).action_triage()
    inc.with_user(x.hse).action_triage(
        note="Confirmed with the depot lead", injured_employee=str(x.colleague.employee_id.id)
    )
    assert inc.triaged_by_id == x.hse and inc.injured_employee_id == x.colleague.employee_id
    assert inc.statutory_record_id.employee_id == x.colleague.employee_id
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, inc, {"triaged_by_id": x.hse2.id})


def test_a_named_report_still_records_its_reporter(x):
    inc = _report(x, x.plain, incident_type="near_miss")
    assert inc.employee_id == x.plain.employee_id and not inc.anonymous
    assert inc.sudo().create_uid == x.plain


# ============================================ fitness status (FR-HSE-037)
def _health(x, employee, fitness, **vals):
    return x.env(user=x.oh.id)["fix.hse.health"].create(
        {
            "employee_id": employee.id,
            "fitness": fitness,
            "clinician": "Dr Rahman",
            "restrictions": "Epilepsy - no ladder work",
            **vals,
        }
    )


def test_hse_and_the_line_manager_read_the_status_never_the_medical_record(x):
    manager = _user(x.env)
    x.plain.employee_id.sudo().write({"parent_id": manager.employee_id.id})
    rec = _health(x, x.plain.employee_id, "fit_restricted", work_restriction="No work at height")
    rec.with_user(x.oh).action_publish_fitness()
    status = rec.fitness_status_id
    assert status.status == "restricted" and status.work_restriction == "No work at height"
    for who in (x.hse, manager, x.plain):
        got = x.env(user=who.id)["fix.hse.fitness.status"].search([("id", "=", status.id)])
        assert got, who.name
        assert "Epilepsy" not in (got.work_restriction or "")
    for who in (x.hse, manager):
        with pytest.raises(AccessError):
            rec.with_user(who).read(["restrictions"])
        with pytest.raises(AccessError):  # the link to the medical record is OH's too
            status.with_user(who).read(["health_id"])
    assert not x.env(user=x.colleague.id)["fix.hse.fitness.status"].search([("id", "=", status.id)])


def test_nobody_types_a_fitness_status(x):
    for who in (x.oh, x.hse):
        with pytest.raises(REFUSED):
            x.env(user=who.id)["fix.hse.fitness.status"].create(
                {
                    "employee_id": x.plain.employee_id.id,
                    "status": "fit",
                    "valid_from": str(x.today),
                }
            )
    rec = _health(x, x.plain.employee_id, "unfit")
    rec.with_user(x.oh).action_publish_fitness()
    with pytest.raises(REFUSED):
        _rpc_write(x.env, x.oh, rec.fitness_status_id, {"status": "fit"})
    with pytest.raises(AccessError):
        rec.with_user(x.hse).action_publish_fitness()


def test_a_restricted_status_needs_its_functional_restriction(x):
    rec = _health(x, x.plain.employee_id, "fit_restricted")
    with pytest.raises(UserError, match="work restriction"):
        rec.with_user(x.oh).action_publish_fitness()


def test_a_new_decision_supersedes_the_old_one(x):
    first = _health(x, x.plain.employee_id, "unfit")
    first.with_user(x.oh).action_publish_fitness()
    second = _health(x, x.plain.employee_id, "fit")
    second.with_user(x.oh).action_publish_fitness()
    assert first.fitness_status_id.state == "superseded"
    assert x.plain.employee_id._fix_fitness_status().status == "fit"


def test_return_to_work_needs_a_fitness_decision_made_after_the_accident(x):
    inc = _report(
        x,
        x.plain,
        incident_type="injury",
        severity="high",
        injured_employee_id=x.plain.employee_id.id,
        accident_datetime=x.now - timedelta(days=10),
    )
    reg = _notify(x, inc)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, reg, {"return_to_work_date": str(x.today)})
    with pytest.raises(UserError, match="no Occupational Health fitness decision"):
        reg.with_user(x.hse).action_record_return_to_work()
    old = _health(x, x.plain.employee_id, "fit", record_date=str(x.today - timedelta(days=30)))
    old.with_user(x.oh).action_publish_fitness()
    with pytest.raises(UserError, match="predates the accident"):
        reg.with_user(x.hse).action_record_return_to_work()
    unfit = _health(x, x.plain.employee_id, "unfit")
    unfit.with_user(x.oh).action_publish_fitness()
    with pytest.raises(UserError, match="unfit"):
        reg.with_user(x.hse).action_record_return_to_work()
    fit = _health(x, x.plain.employee_id, "fit_restricted", work_restriction="Light duties")
    fit.with_user(x.oh).action_publish_fitness()
    with pytest.raises(AccessError):
        reg.with_user(x.plain).action_record_return_to_work()
    reg.with_user(x.hse).action_record_return_to_work()
    # the ORM stamps the context date (env tz Asia/Dhaka), not UTC
    assert reg.return_to_work_date == fields.Date.context_today(reg)
    assert reg.return_fitness_status == "restricted"


# ============================================ PPE replacement (FR-HSE-032)
def _issue(x, replace_by, employee=None):
    ppe = x.env(user=x.hse.id)["fix.ppe.register"].create(
        {"name": "Respirator %d" % next(_SEQ), "stock_quantity": 10, "min_required_quantity": 1}
    )
    return x.env(user=x.hse.id)["fix.ppe.issue"].create(
        {
            "employee_id": (employee or x.plain.employee_id).id,
            "ppe_id": ppe.id,
            "replace_by": replace_by,
        }
    )


def test_ppe_past_replace_by_alerts_then_escalates_once_each(x):
    manager = _user(x.env)
    x.plain.employee_id.sudo().write({"parent_id": manager.employee_id.id})
    # the cron decides on the context date (Asia/Dhaka): an issue due "today"
    # on the UTC clock is already overdue in Dhaka after 18:00 UTC
    issue = _issue(x, fields.Date.context_today(x.env["fix.ppe.issue"]))
    Issue = x.env["fix.ppe.issue"]
    assert Issue.cron_ppe_replacement_alerts() >= 1
    assert issue.replacement_alert_level == 1
    owners = issue.activity_ids.mapped("user_id")
    assert x.plain in owners and x.hse in owners and manager not in owners
    count = len(issue.activity_ids)
    Issue.cron_ppe_replacement_alerts()
    assert len(issue.activity_ids) == count  # idempotent
    issue.sudo().write({"replace_by": x.today - timedelta(days=3)})
    Issue.cron_ppe_replacement_alerts()
    assert issue.replacement_alert_level == 2
    assert manager in issue.activity_ids.mapped("user_id")
    count = len(issue.activity_ids)
    Issue.cron_ppe_replacement_alerts()
    assert len(issue.activity_ids) == count
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, issue, {"replacement_alert_level": 0})


def test_a_replaced_issue_stops_alerting(x):
    old = _issue(x, x.today - timedelta(days=5))
    new = x.env(user=x.hse.id)["fix.ppe.issue"].create(
        {
            "employee_id": old.employee_id.id,
            "ppe_id": old.ppe_id.id,
            "replaces_id": old.id,
            "replace_by": x.today + timedelta(days=180),
        }
    )
    assert old.replaced and not new.replaced
    x.env["fix.ppe.issue"].cron_ppe_replacement_alerts()
    assert old.replacement_alert_level == 0
    with pytest.raises(UserError, match="already replaced"):
        x.env(user=x.hse.id)["fix.ppe.issue"].create(
            {"employee_id": old.employee_id.id, "ppe_id": old.ppe_id.id, "replaces_id": old.id}
        )


def test_ppe_grace_is_a_setting(x):
    x.env["ir.config_parameter"].sudo().set_param("cd_hse.ppe_replacement_grace_days", "7")
    issue = _issue(x, x.today - timedelta(days=3))
    x.env["fix.ppe.issue"].cron_ppe_replacement_alerts()
    assert issue.replacement_alert_level == 1  # inside the grace: alert, no escalation


# ============================================ manager read of incidents
def test_the_line_manager_reads_their_reports_incidents_and_cannot_change_them(x):
    manager = _user(x.env)
    x.plain.employee_id.sudo().write({"parent_id": manager.employee_id.id})
    inc = _serious(x, x.plain)
    other = _serious(x, x.colleague)
    Inc = x.env(user=manager.id)["fix.hse.incident"]
    assert Inc.search([("id", "in", (inc | other).ids)]).ids == inc.ids
    with pytest.raises(AccessError):
        _rpc_write(x.env, manager, inc, {"investigation_findings": "manager note"})


def test_the_injured_workers_manager_reads_it_too(x):
    manager = _user(x.env)
    x.colleague.employee_id.sudo().write({"parent_id": manager.employee_id.id})
    inc = _report(
        x,
        x.plain,
        incident_type="injury",
        severity="low",
        injured_employee_id=x.colleague.employee_id.id,
    )
    assert x.env(user=manager.id)["fix.hse.incident"].search([("id", "=", inc.id)])


def test_the_branch_manager_reads_their_branchs_incidents(x):
    branch_mgr = _user(x.env)
    x.branch.sudo().write({"manager_id": branch_mgr.id})
    inc = _report(x, x.plain, incident_type="near_miss")
    elsewhere = _report(x, x.colleague, incident_type="near_miss", branch_id=False)
    got = x.env(user=branch_mgr.id)["fix.hse.incident"].search(
        [("id", "in", (inc | elsewhere).ids)]
    )
    assert got.ids == inc.ids


# ============================================ investigation and CAPA (M59-F8)
def test_a_capa_is_done_by_its_owner_and_verified_by_someone_else(x):
    inc = _serious(x)
    capa = _investigated(x, inc, owner=x.colleague)
    with pytest.raises(AccessError):
        capa.with_user(x.plain).action_mark_done(note="done")
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, capa, {"state": "verified"})
    with pytest.raises(UserError, match="Say what was done"):
        capa.with_user(x.colleague).action_mark_done()
    capa.with_user(x.colleague).action_mark_done(note="Ladder replaced")
    assert capa.state == "done" and capa.completed_by_id == x.colleague
    with pytest.raises(AccessError):
        capa.with_user(x.colleague).action_verify(note="ok")  # the owner is no HSE Officer
    both = _user(x.env, "cd_hse.group_hse_officer")
    capa2 = _capa(x, inc, owner=both, name="Second action")
    capa2.with_user(both).action_mark_done(note="done")
    with pytest.raises(UserError, match="another HSE Officer"):
        capa2.with_user(both).action_verify(note="self")
    capa.with_user(x.hse2).action_verify(note="Inspected the new ladder")
    assert capa.state == "verified" and capa.verified_by_id == x.hse2


def test_the_owner_reads_their_capa_and_nobody_else_s(x):
    inc = _serious(x)
    capa = _investigated(x, inc, owner=x.colleague)
    assert x.env(user=x.colleague.id)["fix.hse.capa"].search([("id", "=", capa.id)])
    assert not x.env(user=x.plain.id)["fix.hse.capa"].search([("id", "=", capa.id)])
    with pytest.raises(AccessError):
        x.env(user=x.colleague.id)["fix.hse.capa"].create(
            {"incident_id": inc.id, "name": "self-raised"}
        )
    with pytest.raises(AccessError):
        x.env(user=x.plain.id)["fix.hse.root.cause"].create(
            {"incident_id": inc.id, "description": "blame"}
        )


def test_a_closed_incident_freezes_its_investigation(x):
    inc = _report(x, x.plain, incident_type="property_damage", severity="low")
    capa = _investigated(x, inc)
    capa.with_user(x.hse).action_mark_done(note="Repaired")
    inc.with_user(x.hse).action_close()
    assert inc.state == "closed"
    with pytest.raises(UserError, match="closed incident"):
        x.env(user=x.hse.id)["fix.hse.root.cause"].create(
            {"incident_id": inc.id, "description": "late addition"}
        )
    with pytest.raises(UserError, match="closed incident"):
        capa.with_user(x.hse2).action_verify(note="late")


def test_a_cancelled_capa_needs_a_reason_and_leaves_one_live(x):
    inc = _serious(x)
    inc.with_user(x.hse).action_investigate()
    capa = _capa(x, inc)
    with pytest.raises(UserError, match="why"):
        capa.with_user(x.hse).action_cancel()
    capa.with_user(x.hse).action_cancel(reason="Duplicate")
    with pytest.raises(UserError, match="at least one corrective"):
        inc.with_user(x.hse).action_record_action_taken()
    with pytest.raises(UserError, match="never deleted"):
        capa.with_user(x.hse).unlink()


def _run_migration(env, name):
    spec = importlib.util.spec_from_file_location("m", MIGRATIONS / ("%s.py" % name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.migrate(env.cr, "19.0.0.3.0")


def test_the_migration_moves_the_single_capa_fields_into_child_rows(x):
    """The pre/post migration scripts, run on a rolled-back copy of the old
    columns (Odoo drops a removed field's column, so they are recreated)."""
    inc = _serious(x)
    inc.with_user(x.hse).action_investigate()
    x.env.flush_all()
    cr = x.env.cr
    cr.execute(
        "ALTER TABLE fix_hse_incident ADD COLUMN root_cause text, "
        "ADD COLUMN corrective_action text, ADD COLUMN capa_owner_id int, "
        "ADD COLUMN capa_due_date date, ADD COLUMN capa_verified_by_id int, "
        "ADD COLUMN capa_verified_on timestamp"
    )
    cr.execute(
        "UPDATE fix_hse_incident SET root_cause = 'Worn ladder feet', "
        "corrective_action = 'Replace ladder', capa_owner_id = %s, capa_due_date = %s, "
        "capa_verified_by_id = %s, capa_verified_on = now() WHERE id = %s",
        (x.colleague.employee_id.id, x.today, x.hse2.id, inc.id),
    )
    _run_migration(x.env, "pre-migrate")
    _run_migration(x.env, "post-migrate")
    inc = inc.sudo()
    inc.invalidate_recordset()
    assert inc.root_cause_ids.description == "Worn ladder feet"
    assert inc.investigation_member_ids.employee_id == x.hse.employee_id
    capa = inc.capa_ids
    assert capa.name == "Replace ladder" and capa.owner_id == x.colleague.employee_id
    assert capa.state == "verified" and capa.verified_by_id == x.hse2 and capa.migrated
    cr.execute("SELECT to_regclass('_a09_r2_hse_capa_legacy')")
    assert cr.fetchone()[0] is None


def test_the_migration_publishes_fitness_without_the_clinical_text(x):
    rec = _health(x, x.plain.employee_id, "fit_restricted")
    _run_migration(x.env, "post-migrate")
    status = rec.fitness_status_id
    assert status.migrated and status.status == "restricted"
    assert "Epilepsy" not in status.work_restriction


# ============================================ driving licence (BRU-HSE-07)
def test_an_expired_licence_refuses_the_road_check(x):
    _driver(x, x.plain, x.today - timedelta(days=1))
    # AUT-FLT-05 (A07 P1 M46-6): a driver registered with an already-expired
    # licence is born suspended, so the refusal reason names the suspension;
    # either way the lapsed licence refuses the road check.
    with pytest.raises(UserError, match=r"expired|suspended"):
        x.env(user=x.plain.id)["fix.hse.roadcheck"].create({"vehicle_ref": "DHA-9"})


def test_a_licence_with_no_class_refuses_the_road_check(x):
    _driver(x, x.plain, x.today + timedelta(days=30), licence_class=False)
    with pytest.raises(UserError, match="no class"):
        x.env(user=x.plain.id)["fix.hse.roadcheck"].create({"vehicle_ref": "DHA-8"})


def test_the_licence_on_a_road_check_is_read_not_typed(x):
    _driver(x, x.plain, x.today + timedelta(days=30))
    chk = x.env(user=x.plain.id)["fix.hse.roadcheck"].create(
        {"vehicle_ref": "DHA-7", "licence_expiry": str(x.today + timedelta(days=9999))}
    )
    assert chk.licence_expiry == x.today + timedelta(days=30)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.plain, chk, {"licence_expiry": str(x.today + timedelta(days=9999))})


def _vehicle(x):
    brand = x.env["fleet.vehicle.model.brand"].create({"name": "A09 M59 Brand"})
    model = x.env["fleet.vehicle.model"].create({"name": "A09 Van", "brand_id": brand.id})
    vehicle = x.env["fleet.vehicle"].create(
        {
            "model_id": model.id,
            "license_plate": "A09-M59-%d" % next(_SEQ),
            "fitness_expiry": x.today + timedelta(days=60),
            "insurance_expiry": x.today + timedelta(days=60),
        }
    )
    # A07 M46-2/3: the document register, not the header dates, decides the
    # vehicle is dispatchable; without these rows the licence control under
    # test is never reached.
    for doc_type, valid_to in (
        ("fitness", x.today + timedelta(days=60)),
        ("insurance", x.today + timedelta(days=60)),
        ("tax", x.today + timedelta(days=90)),
    ):
        x.env["fix.vehicle.document"].create(
            {"vehicle_id": vehicle.id, "doc_type": doc_type, "valid_to": valid_to}
        )
    return vehicle


def test_a_vehicle_is_not_assigned_to_a_technician_without_a_valid_licence(x):
    vehicle = _vehicle(x)
    Assign = x.env["fix.vehicle.assignment"]
    with pytest.raises(ValidationError, match="no driving licence on record"), x.env.cr.savepoint():
        Assign.create(
            {"vehicle_id": vehicle.id, "date": x.today, "technician_id": x.plain.employee_id.id}
        )
    _driver(x, x.plain, x.today + timedelta(days=2))
    ok = Assign.create(
        {"vehicle_id": vehicle.id, "date": x.today, "technician_id": x.plain.employee_id.id}
    )
    with pytest.raises(ValidationError, match="expired"), x.env.cr.savepoint():
        ok.write({"date": x.today + timedelta(days=10)})
    # a vehicle-only booking (no technician) is unaffected
    assert Assign.create({"vehicle_id": _vehicle(x).id, "date": x.today})


# ============================================ dispatcher lone-worker sessions
@pytest.fixture
def fs(x):
    env = x.env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    zone = env["fix.zone"].create({"name": "A09 M59 Zone", "code": "A9MZ"})
    x.branch.write({"zone_id": zone.id})
    brand = env["fix.brand"].create({"name": "A9M59Brand", "code": "A9MB"})
    model = env["fix.device.model"].create({"name": "A9 Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A09 M59 Customer", "phone": "01711000997"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-A9M59-1"}
    )
    so = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": x.branch.id,
            "fault_description": "onsite A09",
            "service_type": "onsite",
        }
    )
    dispatcher = _user(env, "cd_field_service.group_fix_field_service_manager")
    dispatcher.write({"operating_unit_ids": [(6, 0, ou.ids)], "default_operating_unit_id": ou.id})

    def order(tech, state="dispatched"):
        rec = env["fix.field.order"].create(
            {"order_id": so.id, "zone_id": zone.id, "operating_unit_id": ou.id}
        )
        # setup only: the superuser places the record in the state under test
        rec.write({"state": state, "technician_id": tech.id})
        return rec

    return types.SimpleNamespace(dispatcher=dispatcher, order=order)


def test_a_dispatcher_opens_a_session_for_the_technician_they_dispatched(x, fs):
    tech = x.plain.employee_id
    fo = fs.order(tech)
    Lone = x.env(user=fs.dispatcher.id)["fix.hse.loneworker"]
    session = Lone.create(
        {
            "employee_id": tech.id,
            "field_order_id": fo.id,
            "expected_end": x.now + timedelta(hours=2),
            "location": "Customer site, Mirpur",
        }
    )
    assert session.opened_by_id == fs.dispatcher and session.employee_id == tech
    # the dispatcher can raise the alarm, but not silence the session
    with pytest.raises(AccessError):
        session.with_user(fs.dispatcher).action_checkout()
    session.with_user(fs.dispatcher).action_escalate()
    assert session.state == "escalated"
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, fs.dispatcher, session, {"opened_by_id": x.hse.id})


def test_a_dispatcher_needs_the_field_order_of_that_technician(x, fs):
    Lone = x.env(user=fs.dispatcher.id)["fix.hse.loneworker"]
    end = x.now + timedelta(hours=2)
    with pytest.raises(AccessError, match="name the field order"):
        Lone.create({"employee_id": x.plain.employee_id.id, "expected_end": end})
    other = fs.order(x.colleague.employee_id)
    with pytest.raises(AccessError, match="dispatched to"):
        Lone.create(
            {"employee_id": x.plain.employee_id.id, "field_order_id": other.id, "expected_end": end}
        )
    closed = fs.order(x.plain.employee_id, state="draft")
    with pytest.raises(UserError, match="not active"):
        Lone.create(
            {
                "employee_id": x.plain.employee_id.id,
                "field_order_id": closed.id,
                "expected_end": end,
            }
        )


def test_a_plain_colleague_still_cannot_open_a_session_for_someone_else(x, fs):
    fo = fs.order(x.plain.employee_id)
    with pytest.raises(AccessError, match="for yourself only"):
        x.env(user=x.colleague.id)["fix.hse.loneworker"].create(
            {
                "employee_id": x.plain.employee_id.id,
                "field_order_id": fo.id,
                "expected_end": x.now + timedelta(hours=1),
            }
        )


# ============================================ deployment
def test_round_two_crons_rules_acl_and_surfaces_are_deployed(odoo_env):
    cron = odoo_env.ref("cd_hse.cron_hse_ppe_replacement")
    assert cron.active and cron.user_id == odoo_env.ref("base.user_root")
    assert cron.code.strip() == "model.cron_ppe_replacement_alerts()"
    assert odoo_env.ref("cd_hse.param_ppe_replacement_grace_days").value == "0"
    for xmlid in (
        "cd_hse.rule_hse_incident_read_scope",
        "cd_hse.rule_hse_capa_scope",
        "cd_hse.rule_hse_fitness_status_scope",
    ):
        rule = odoo_env.ref(xmlid)
        assert rule.active and rule["global"] and rule.perm_read, xmlid
    own = odoo_env.ref("cd_hse.rule_hse_incident_own")
    assert not own.perm_read and own.perm_write
    for xmlid in (
        "cd_hse.access_fix_hse_capa_user",
        "cd_hse.access_fix_hse_capa_role",
        "cd_hse.access_fix_hse_root_cause_role",
        "cd_hse.access_fix_hse_investigation_member_role",
        "cd_hse.access_fix_hse_fitness_status_user",
    ):
        acl = odoo_env.ref(xmlid)
        assert acl.perm_read, xmlid
    assert not odoo_env.ref("cd_hse.access_fix_hse_fitness_status_user").perm_write
    assert odoo_env.ref("cd_field_service.group_fix_field_service_manager", False)
    for model in ("fix.hse.capa", "fix.hse.root.cause", "fix.hse.fitness.status"):
        assert model in a09.SURFACES, model
        for method in a09.SURFACES[model]["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), (model, method)
    for model, method in (
        ("fix.hse.incident", "action_triage"),
        ("fix.statutory.accident.register", "action_record_return_to_work"),
        ("fix.hse.health", "action_publish_fitness"),
    ):
        assert method in a09.SURFACES[model]["actions"], (model, method)
    assert "action_verify_capa" not in a09.SURFACES["fix.hse.incident"]["actions"]


# ============================================ M22 certification.safety_lapsed consumer
def _lapse_payload(x, cert_id=987654):
    return {
        "employee_id": x.plain.employee_id.id,
        "certification_id": cert_id,
        "competency": "ELEC-SAFE",
        "expired_on": str(x.today - timedelta(days=1)),
    }


def test_a_lapsed_safety_certification_opens_one_hse_followup(x):
    Followup = x.env["fix.hse.safety.followup"]
    event = {"aggregate_id": 987654, "payload": _lapse_payload(x)}
    assert Followup.consume_certification_safety_lapsed(event) is True
    rec = Followup.search([("certification_ref", "=", 987654)])
    assert len(rec) == 1 and rec.employee_id == x.plain.employee_id
    assert rec.assigned_to_id and rec.assigned_to_id.has_group("cd_hse.group_hse_officer")
    assert rec.activity_ids.filtered(lambda a: a.user_id == rec.assigned_to_id)
    # idempotent per certification
    assert Followup.consume_certification_safety_lapsed(event) is False
    assert Followup.search_count([("certification_ref", "=", 987654)]) == 1
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, rec, {"state": "closed"})
    with pytest.raises(AccessError):
        rec.with_user(x.plain).action_close(outcome="x")
    rec.with_user(x.hse).action_close(outcome="Renewed on 5 Nov; off electrical work until then")
    assert rec.state == "closed" and rec.closed_by_id == x.hse


def test_the_safety_lapsed_event_reaches_the_consumer_through_the_relay(x):
    from libs.py.fix_events import publish

    publish(
        x.env, "certification.safety_lapsed", "fix.certification", 987655, _lapse_payload(x, 987655)
    )
    x.env["fix.event.outbox"].cron_relay()
    x.env["fix.event.outbox"].cron_relay()  # a second relay pass changes nothing
    rows = x.env["fix.hse.safety.followup"].search([("certification_ref", "=", 987655)])
    assert len(rows) == 1 and rows.competency == "ELEC-SAFE"


def test_the_safety_lapsed_consumer_is_deployed(odoo_env):
    consumer = odoo_env.ref("cd_hse.consumer_hse_safety_lapsed")
    assert consumer.active and consumer.event_type == "certification.safety_lapsed"
    assert callable(getattr(odoo_env[consumer.model], consumer.method))
    assert odoo_env.ref("cd_hse.access_fix_hse_safety_followup_role").perm_read
    assert "action_close" in a09.SURFACES["fix.hse.safety.followup"]["actions"]


def test_the_dedicated_anonymous_form_sends_only_what_an_anonymous_report_holds():
    """BRU-HSE-01: the workspace's "Anonymous Safety Report" entry offers only
    the fields the anonymous path accepts, pre-ticked anonymous, and no
    reporter field - so a save from it is always filed without a reporter."""
    from odoo.addons.cd_p03_portal.controllers import form_fields

    forms = {sid: (model, editable) for _a, sid, model, editable in form_fields.forms()}
    model, editable = forms["M59-form-anonymous"]
    assert model == "fix.hse.incident"
    accepted = {
        "anonymous",
        "incident_type",
        "severity",
        "description",
        "branch_id",
        "operating_unit_id",
        "accident_datetime",
        "injured_employee_id",
        "company_id",
    }
    assert "anonymous" in editable and editable <= accepted
    assert "employee_id" not in editable


# ================================= CAPA reopen and the overdue reminder (M59-F10)
def test_an_ineffective_action_reopens_instead_of_staying_verified(x):
    """FR-HSE-015 / lifecycle 8.1: a verified action was a dead end. A finding
    on verification returns it to open, with the finding on its history."""
    inc = _serious(x)
    capa = _investigated(x, inc, owner=x.colleague)
    capa.with_user(x.colleague).action_mark_done(note="Ladder replaced")
    capa.with_user(x.hse2).action_verify(note="Inspected the new ladder")
    assert capa.state == "verified"
    with pytest.raises(UserError, match="did not hold"):
        capa.with_user(x.hse).action_reopen()
    with pytest.raises(AccessError):
        capa.with_user(x.colleague).action_reopen(reason="The stand came loose again")
    capa.with_user(x.hse).action_reopen(reason="The stand came loose again")
    assert capa.state == "open" and capa.reopen_count == 1
    assert "came loose again" in " ".join(capa.message_ids.mapped("body"))
    # and the action is worked again to a fresh verification
    capa.with_user(x.colleague).action_mark_done(note="Bolted to the wall")
    capa.with_user(x.hse2).action_verify(note="Checked after a week")
    assert capa.state == "verified" and capa.reopen_count == 1
    capa.with_user(x.hse).action_reopen(reason="Second failure")
    assert capa.reopen_count == 2


def test_overdue_actions_remind_their_owner_once_a_day(x):
    """M59-F10 / AUT-HSE-10: no cron looked at the due date. The owner gets one
    to-do a day while the action is open and late; seven days late the HSE
    officers hear it too."""
    inc = _serious(x)
    capa = _investigated(x, inc, owner=x.colleague)
    capa.sudo()._guarded().write({"due_date": x.today - timedelta(days=3)})
    Capa = x.env["fix.hse.capa"]
    assert Capa.cron_overdue_capas() >= 1
    mine = capa.activity_ids.filtered(
        lambda a: a.summary == "CAPA overdue: %s" % capa.name and a.user_id == x.colleague
    )
    assert mine, capa.activity_ids.mapped("summary")
    assert Capa.cron_overdue_capas() == 0  # once a day
    # still open seven days late: the HSE officers hear it
    capa.sudo()._guarded().write(
        {"due_date": x.today - timedelta(days=9), "overdue_alerted_on": False}
    )
    assert Capa.cron_overdue_capas() >= 1
    assert x.hse in capa.activity_ids.user_id
    # a done action is never chased
    capa.with_user(x.colleague).action_mark_done(note="Stand bolted")
    before = len(capa.activity_ids)
    assert Capa.cron_overdue_capas() == 0
    assert len(capa.activity_ids) == before
