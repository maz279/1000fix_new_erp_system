# M23 capture audit (2026-11-19): the records the sub-module pages could not
# capture, exercised against the live ORM as NON-ADMIN users (the superuser
# is trusted by the field guard and would hide a gap), and through the real
# P03 endpoints (/p03/model/write with its child grid, /p03/model/action).
# The odoo_env fixture rolls back.
import itertools
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.addons.cd_p03_portal.controllers.a10 import m23 as m23_ctl
from odoo.exceptions import UserError, ValidationError

QM = "cd_qms_process.group_qms_quality_manager"
GUARD = "changes only through its workflow"

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)

_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M23 cap %s %d" % (login, n),
                "login": "m23cap.%s.%d@m23.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")
    x.clerk_emp = env["hr.employee"].create({"name": "M23 Clerk Karim", "user_id": x.clerk.id})
    x.qm = _user(env, "qm", [QM])
    x.qm_emp = env["hr.employee"].create({"name": "M23 QM Rahman", "user_id": x.qm.id})
    x.qm2 = _user(env, "qm2", [QM])
    x.qm2_emp = env["hr.employee"].create({"name": "M23 QM Two Sultana", "user_id": x.qm2.id})
    x.owner_emp = env["hr.employee"].create({"name": "M23 Owner Neha"})
    # the branches belong to the users' own company: the auditor register
    # and the audit read them as those users
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1)
    if not entity:
        entity = env["fix.entity"].create(
            {
                "code": "EN-M23C-%d" % next(_SEQ),
                "legal_name": "M23 Entity",
                "company_id": env.company.id,
            }
        )
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.branch = env["fix.branch"].create(
        {
            "code": "M23C-%d" % next(_SEQ),
            "name": "Mirpur",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    x.branch2 = env["fix.branch"].create(
        {
            "code": "M23D-%d" % next(_SEQ),
            "name": "Banani",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    x.policy = env["fix.qms.policy"].create({"name": "Quality Policy", "year": "2026"})
    x.process = env["fix.qms.process"].create(
        {
            "name": "Bench repair",
            "code": "PR-M23C-%d" % next(_SEQ),
            "process_owner_id": x.owner_emp.id,
        }
    )
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


def p03(x, endpoint, user=None, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return endpoint(g.P03GenericApiController(), **kw)


def _ncr(x, severity="minor", user=None, **vals):
    return (
        x.env["fix.ncr"]
        .with_user(user or x.clerk)
        .create(
            {"source": "service_order", "severity": severity, "description": "Seal missing", **vals}
        )
    )


# ---------------------------------------------------------------- page 1
def test_objective_cascades_and_measures_attainment(w):
    Obj = w.env["fix.qms.objective"].with_user(w.clerk)
    top = Obj.create(
        {
            "name": "Rework below 3%",
            "policy_id": w.policy.id,
            "measure": "rework orders / delivered orders",
            "target": 3.0,
            "actual": 4.0,
            "higher_is_better": False,
            "period": "2026",
            "owner_id": w.owner_emp.id,
        }
    )
    assert top.attainment == 75.0  # lower is better: 3 / 4
    with pytest.raises(ValidationError, match="names its branch"), w.env.cr.savepoint():
        Obj.create(
            {
                "name": "Mirpur rework",
                "policy_id": w.policy.id,
                "parent_id": top.id,
                "scope_level": "branch",
                "measure": "m",
                "target": 2.5,
                "period": "2026",
                "owner_id": w.owner_emp.id,
            }
        )
    child = Obj.create(
        {
            "name": "Mirpur rework",
            "policy_id": w.policy.id,
            "parent_id": top.id,
            "scope_level": "branch",
            "branch_id": w.branch.id,
            "measure": "m",
            "target": 90.0,
            "actual": 45.0,
            "period": "2026",
            "owner_id": w.owner_emp.id,
        }
    )
    assert child.attainment == 50.0
    other = w.env["fix.qms.policy"].create({"name": "Policy 2027", "year": "2027"})
    with pytest.raises(ValidationError, match="another policy year"), w.env.cr.savepoint():
        child.write({"policy_id": other.id})
    with pytest.raises(ValidationError, match="cannot cascade from itself"), w.env.cr.savepoint():
        top.write({"parent_id": child.id})


# ---------------------------------------------------------------- page 2
def test_process_change_is_released_only_with_every_affected_item_updated(w):
    chg = (
        w.env["fix.qms.change.assessment"]
        .with_user(w.clerk)
        .create(
            {
                "process_id": w.process.id,
                "change_summary": "Add ESD wrist-strap check at intake",
                "affects_checklists": True,
                "affects_training": True,
            }
        )
    )
    assert chg.name.startswith("CHG/")
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        chg.with_user(w.clerk).write({"state": "released"})
    with pytest.raises(UserError, match="Record the QMS impact"), w.env.cr.savepoint():
        chg.with_user(w.clerk).action_assess()
    chg.with_user(w.clerk).write({"impact_note": "Intake checklist v2 and ESD refresher"})
    chg.with_user(w.clerk).action_assess()
    assert chg.state == "assessed" and chg.assessed_by_id == w.clerk_emp
    with pytest.raises(UserError, match="Only the Quality Manager"), w.env.cr.savepoint():
        chg.with_user(w.clerk).action_release()
    with pytest.raises(UserError, match="checklists, training first"), w.env.cr.savepoint():
        chg.with_user(w.qm).action_release()
    chg.with_user(w.clerk).write({"checklists_updated": True, "training_updated": True})
    chg.with_user(w.qm).action_release()
    assert chg.state == "released" and chg.released_by_id == w.qm_emp
    with pytest.raises(UserError, match="the record kept"), w.env.cr.savepoint():
        chg.with_user(w.qm).write({"change_summary": "rewritten"})


# ---------------------------------------------------------------- page 3
def test_checklist_items_publish_and_version(w):
    Chk = w.env["fix.qms.checklist"]
    chk = Chk.with_user(w.clerk).create({"name": "Bench QC"})
    with pytest.raises(UserError, match="has no items"), w.env.cr.savepoint():
        chk.with_user(w.qm).action_publish()
    with pytest.raises(ValidationError, match="acceptance criteria"), w.env.cr.savepoint():
        w.env["fix.qms.checklist.item"].with_user(w.clerk).create(
            {"checklist_id": chk.id, "name": "Battery voltage", "response_type": "measurement"}
        )
    item = (
        w.env["fix.qms.checklist.item"]
        .with_user(w.clerk)
        .create(
            {
                "checklist_id": chk.id,
                "name": "Battery voltage",
                "response_type": "measurement",
                "acceptance_criteria": "3.7-4.2 V",
                "evidence_required": "photo",
                "reportable": True,
            }
        )
    )
    assert chk.item_count == 1 and item.company_id == chk.company_id
    chk.with_user(w.qm).action_publish()
    # BRU-QMS-03: the released version is frozen - items and header
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        item.with_user(w.clerk).write({"acceptance_criteria": "3.0-4.5 V"})
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        w.env["fix.qms.checklist.item"].with_user(w.clerk).create(
            {"checklist_id": chk.id, "name": "Screen"}
        )
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        chk.with_user(w.clerk).write({"name": "Renamed"})
    with pytest.raises(UserError, match="Only the Quality Manager"), w.env.cr.savepoint():
        chk.with_user(w.clerk).action_new_version()
    new_ids = chk.with_user(w.qm).action_new_version()
    new = Chk.browse(new_ids)
    assert (new.state, new.version, new.previous_version_id) == ("draft", "2.0", chk)
    assert new.item_ids.mapped("name") == ["Battery voltage"] and new.item_ids != chk.item_ids
    new.item_ids.with_user(w.clerk).write({"acceptance_criteria": "3.6-4.2 V"})
    assert chk.item_ids.acceptance_criteria == "3.7-4.2 V"  # the executed version stays
    with pytest.raises(UserError, match="already has its next version"), w.env.cr.savepoint():
        chk.with_user(w.qm).action_new_version()


def test_typed_item_counts_are_recounted(w):
    chk = w.env["fix.qms.checklist"].create({"name": "Legacy"})
    w.env.flush_all()
    w.env.cr.execute("UPDATE fix_qms_checklist SET item_count = 14 WHERE id = %s", [chk.id])
    w.env.invalidate_all()
    assert chk.item_count == 14
    w.env["fix.qms.checklist"]._m23_recount_items()
    w.env.invalidate_all()
    assert chk.item_count == 0


def test_checklist_and_items_save_through_the_workspace_in_one_write(w):
    out = p03(
        w,
        _MW,
        model="fix.qms.checklist",
        values={
            "name": "Handover check",
            "checklist_type": "handover",
            "applies_delivery_mode": "pickup",
        },
        lines={
            "field": "item_ids",
            "rows": [
                {
                    "values": {
                        "name": "Customer signs",
                        "response_type": "yes_no",
                        "evidence_required": "signature",
                    }
                },
                {
                    "values": {
                        "name": "Device powers on",
                        "response_type": "pass_fail",
                        "evidence_required": "none",
                    }
                },
            ],
            "removed": [],
        },
    )
    assert "id" in out, out
    chk = w.env["fix.qms.checklist"].browse(out["id"])
    assert chk.item_count == 2 and chk.applies_delivery_mode == "pickup"
    out = p03(w, _MW, model="fix.qms.checklist", record_id=chk.id, values={"item_count": 99})
    assert "error" in out or chk.item_count == 2


# ---------------------------------------------------------------- page 4
def test_ncr_sources_types_and_containment(w):
    ncr = _ncr(w, source="rework", nc_type="customer", clause_ref="8.7")
    assert ncr.source == "rework"
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        ncr.with_user(w.clerk).write({"containment_done_on": fields.Date.today()})
    with pytest.raises(UserError, match="who owns it"), w.env.cr.savepoint():
        ncr.with_user(w.clerk).action_record_containment(note="Quarantine bin B")
    ncr.with_user(w.clerk).write(
        {"containment_owner_id": w.owner_emp.id, "containment_due": fields.Date.today()}
    )
    ncr.with_user(w.clerk).action_record_containment(note="Quarantine bin B")
    assert ncr.containment == "Quarantine bin B"
    assert ncr.containment_done_on and ncr.containment_done_by_id == w.clerk_emp
    with pytest.raises(UserError, match="already confirmed"), w.env.cr.savepoint():
        ncr.with_user(w.clerk).action_record_containment()
    out = p03(
        w,
        _MA,
        model="fix.ncr",
        ids=ncr.ids,
        method="action_set_root_cause",
        kwargs={"root_cause": "x"},
    )
    assert out.get("success") is False  # the typed root cause left the workspace


# ---------------------------------------------------------------- page 5
def _rca(x, ncr, **vals):
    return (
        x.env["fix.qms.rca"]
        .with_user(x.clerk)
        .create({"ncr_id": ncr.id, "symptom": "Seal missing on returned unit", **vals})
    )


def test_rca_distinguishes_cause_from_symptom_and_lands_on_the_ncr(w):
    ncr = _ncr(w)
    rca = _rca(w, ncr, method="five_why", why_1="Seal not fitted", why_2="Step skipped")
    assert rca.name.startswith("RCA/")
    with pytest.raises(UserError, match="Record the root cause"), w.env.cr.savepoint():
        rca.with_user(w.clerk).action_complete()
    rca.with_user(w.clerk).write({"root_cause": "  seal missing on RETURNED unit "})
    with pytest.raises(UserError, match="repeats the symptom"), w.env.cr.savepoint():
        rca.with_user(w.clerk).action_complete()
    rca.with_user(w.clerk).write({"root_cause": "Work instruction omits the seal step"})
    with pytest.raises(UserError, match="three answered whys"), w.env.cr.savepoint():
        rca.with_user(w.clerk).action_complete()
    rca.with_user(w.clerk).write({"why_3": "Instruction v1 predates the sealed model"})
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        rca.with_user(w.clerk).write({"state": "completed"})
    rca.with_user(w.clerk).action_complete()
    assert rca.state == "completed" and rca.completed_by_id == w.clerk_emp
    assert ncr.state == "root_cause" and ncr.root_cause == "Work instruction omits the seal step"
    with pytest.raises(UserError, match="a new record"), w.env.cr.savepoint():
        rca.with_user(w.clerk).write({"root_cause": "changed"})


def test_a_major_ncr_is_investigated_by_8d(w):
    ncr = _ncr(w, severity="major")
    rca = _rca(
        w, ncr, method="five_why", why_1="a", why_2="b", why_3="c", root_cause="Fixture worn"
    )
    with pytest.raises(UserError, match="investigated by 8D"), w.env.cr.savepoint():
        rca.with_user(w.clerk).action_complete()
    rca8 = _rca(w, ncr, method="eight_d", root_cause="Fixture worn", d1_team="QM, bench lead")
    with pytest.raises(UserError, match="D2 Problem Description"), w.env.cr.savepoint():
        rca8.with_user(w.clerk).action_complete()
    rca8.with_user(w.clerk).write(
        {
            "d2_problem": "p",
            "d3_containment": "c",
            "d5_corrective": "r",
            "d6_implementation": "i",
            "d7_prevention": "v",
            "d8_recognition": "t",
        }
    )
    rca8.with_user(w.clerk).action_complete()
    assert ncr.state == "root_cause"


def _capa(x, ncr=None, **vals):
    ncr = ncr or _ncr(x)
    ncr.action_set_root_cause("Process gap")
    return ncr.with_user(x.clerk).action_open_capa(
        corrective_action="Retrain the bench", owner_id=x.owner_emp.id
    )


def test_capa_is_implemented_only_when_every_action_is_done(w):
    capa = _capa(w)
    Act = w.env["fix.capa.action"].with_user(w.clerk)
    local = Act.create(
        {"capa_id": capa.id, "name": "Update the bench card", "owner_id": w.clerk_emp.id}
    )
    remote = Act.create(
        {
            "capa_id": capa.id,
            "name": "ESD refresher for the bench",
            "owner_id": w.owner_emp.id,
            "executing_module": "m22",
        }
    )
    assert capa.open_action_count == 2
    with pytest.raises(UserError, match="2 open action"), w.env.cr.savepoint():
        capa.with_user(w.clerk).action_implement()
    with pytest.raises(UserError, match="evidence"), w.env.cr.savepoint():
        local.with_user(w.clerk).action_done()
    local.with_user(w.clerk).action_done(note="Card v3 posted at bench 2")
    with pytest.raises(UserError, match="owner or the Quality Manager"), w.env.cr.savepoint():
        remote.with_user(w.clerk).action_done(note="done")
    with pytest.raises(UserError, match="name the record there"), w.env.cr.savepoint():
        remote.with_user(w.qm).action_done(note="done")
    remote.with_user(w.qm).write({"external_ref": "TRN/2026/0042"})
    remote.with_user(w.qm).action_done(note="Session held, 6 attended")
    with pytest.raises(UserError, match="the record kept"), w.env.cr.savepoint():
        remote.with_user(w.qm).write({"name": "changed"})
    capa.with_user(w.clerk).action_implement()
    assert capa.state == "implemented" and capa.open_action_count == 0
    with pytest.raises(UserError, match="planned while it is open"), w.env.cr.savepoint():
        Act.create({"capa_id": capa.id, "name": "late", "owner_id": w.clerk_emp.id})


def test_effectiveness_waits_for_the_observation_window(w):
    capa = _capa(w)
    capa.with_user(w.clerk).write({"observation_window_days": 30})
    capa.with_user(w.clerk).action_implement()
    assert capa.verification_due_on == fields.Date.context_today(capa) + timedelta(days=30)
    with pytest.raises(UserError, match="observation window"), w.env.cr.savepoint():
        capa.with_user(w.qm).action_verify(note="No recurrence", effective=True)
    capa._guarded().write({"verification_due_on": fields.Date.context_today(capa)})
    capa.with_user(w.qm).action_verify(note="No recurrence in 30 days", effective=True)
    assert capa.state == "verified"


def test_capa_action_plan_saves_with_the_capa_in_one_write(w):
    capa = _capa(w)
    out = p03(
        w,
        _MW,
        model="fix.capa",
        record_id=capa.id,
        values={"observation_window_days": 14},
        lines={
            "field": "action_ids",
            "rows": [
                {
                    "values": {
                        "name": "Fit seal jig",
                        "owner_id": w.owner_emp.id,
                        "executing_module": "m23",
                    }
                }
            ],
            "removed": [],
        },
    )
    assert "id" in out, out
    assert capa.action_ids.mapped("name") == ["Fit seal jig"] and capa.observation_window_days == 14


# ---------------------------------------------------------------- page 6
def _audit(x, user=None, **vals):
    return (
        x.env["fix.internal.audit"]
        .with_user(user or x.qm)
        .create(
            {
                "branch_id": x.branch.id,
                "scheduled_on": fields.Date.today(),
                "auditor_id": x.qm_emp.id,
                "scope": "ISO 9001 8.5 bench control",
                **vals,
            }
        )
    )


def test_auditor_register_enforces_competence_and_independence(w):
    # no register kept yet: assignment stays as before
    _audit(w, auditor_id=w.clerk_emp.id)
    with pytest.raises(UserError, match="kept by the Quality Manager"), w.env.cr.savepoint():
        w.env["fix.qms.auditor"].with_user(w.clerk).create(
            {"employee_id": w.clerk_emp.id, "competence_note": "self-declared"}
        )
    w.env["fix.qms.auditor"].with_user(w.qm).create(
        {
            "employee_id": w.qm_emp.id,
            "competence_note": "IRCA lead auditor course 2025",
            "excluded_branch_ids": [(6, 0, [w.branch2.id])],
        }
    )
    with pytest.raises(UserError, match="not an active registered auditor"), w.env.cr.savepoint():
        _audit(w, auditor_id=w.clerk_emp.id)
    with pytest.raises(UserError, match="their own area"), w.env.cr.savepoint():
        _audit(w, branch_id=w.branch2.id)
    own = w.env["fix.qms.process"].create(
        {"name": "Audit mgmt", "code": "PR-AUD-%d" % next(_SEQ), "process_owner_id": w.qm_emp.id}
    )
    with pytest.raises(UserError, match="own work or process"), w.env.cr.savepoint():
        _audit(w, process_ids=[(6, 0, [own.id])])
    audit = _audit(w, process_ids=[(6, 0, [w.process.id])])
    assert audit.name.startswith("IA/")
    with pytest.raises(UserError, match="their own area"), w.env.cr.savepoint():
        audit.with_user(w.qm).write({"branch_id": w.branch2.id})


def test_findings_are_recorded_classified_and_raise_their_ncr(w):
    audit = _audit(w, process_ids=[(6, 0, [w.process.id])])
    Finding = w.env["fix.qms.audit.finding"]
    vals = {"audit_id": audit.id, "clause_ref": "8.5.1", "statement": "s", "evidence": "e"}
    with pytest.raises(UserError, match="while the audit is executed"), w.env.cr.savepoint():
        Finding.with_user(w.qm).create(dict(vals, classification="minor"))
    audit.with_user(w.qm).action_execute(payload='{"items": 12, "failed": 2}')
    major = Finding.with_user(w.qm).create(
        dict(vals, classification="major", statement="No torque records for 3 weeks")
    )
    minor = Finding.with_user(w.qm).create(
        dict(vals, classification="minor", statement="Label faded")
    )
    obs = Finding.with_user(w.qm).create(
        dict(vals, classification="observation", statement="Bench tidy")
    )
    assert major.company_id == audit.company_id and major.name.startswith("AF/")
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        minor.with_user(w.qm).write({"state": "closed"})
    with pytest.raises(UserError, match="raises no NCR"), w.env.cr.savepoint():
        obs.with_user(w.qm).action_raise_ncr()
    minor.with_user(w.qm).action_raise_ncr()
    assert minor.ncr_id.source == "audit" and minor.ncr_id.audit_id == audit
    assert minor.ncr_id.severity == "minor" and minor.ncr_id.finding_id == minor
    with pytest.raises(UserError, match="the record kept"), w.env.cr.savepoint():
        minor.with_user(w.qm).write({"statement": "rewritten"})
    # AUT-QMS-14: the report raises the NCR of the major finding still
    # without one, and the existing journey opens its CAPA
    audit.with_user(w.qm).action_report()
    assert major.state == "ncr_raised" and major.ncr_id.severity == "major"
    assert major.ncr_id.capa_id, "the major finding's NCR leaves the report with its CAPA"
    with pytest.raises(UserError, match="Only the Quality Manager"), w.env.cr.savepoint():
        obs.with_user(w.clerk).action_close(note="Noted")
    with pytest.raises(UserError, match="closes when its NCR is closed"), w.env.cr.savepoint():
        minor.with_user(w.qm).action_close()
    obs.with_user(w.qm).action_close(note="Shared as good practice")
    assert obs.state == "closed"
    assert m23_ctl.audit_programme(w.env)["rows"][0]["findings"] >= 3


def test_auditee_acknowledges_the_issued_report(w):
    audit = _audit(w)
    with pytest.raises(UserError, match="issued report"), w.env.cr.savepoint():
        audit.with_user(w.clerk).action_acknowledge()
    audit.with_user(w.qm).action_execute(payload="{}")
    audit.with_user(w.qm).action_report()
    with pytest.raises(UserError, match="not the auditor"), w.env.cr.savepoint():
        audit.with_user(w.qm).action_acknowledge()
    audit.with_user(w.clerk).action_acknowledge()
    assert audit.auditee_acknowledged_on


def test_audit_programme_is_approved_by_the_quality_manager(w):
    prog = (
        w.env["fix.qms.audit.programme"]
        .with_user(w.clerk)
        .create({"name": "IA 2026", "year": "2026"})
    )
    with pytest.raises(UserError, match="Only the Quality Manager"), w.env.cr.savepoint():
        prog.with_user(w.clerk).action_approve()
    with pytest.raises(UserError, match="covers nothing"), w.env.cr.savepoint():
        prog.with_user(w.qm).action_approve()
    prog.with_user(w.clerk).write({"process_ids": [(6, 0, [w.process.id])]})
    assert prog.uncovered_processes == 1
    _audit(w, programme_id=prog.id, process_ids=[(6, 0, [w.process.id])])
    assert (prog.planned_count, prog.uncovered_processes) == (1, 0)
    prog.with_user(w.qm).action_approve()
    assert prog.state == "approved" and prog.approved_by_id == w.qm_emp


def test_evidence_is_released_only_on_another_quality_managers_approval(w):
    att = w.env["ir.attachment"].create({"name": "torque-log.pdf", "raw": b"%PDF-1.4 test"})
    rel = (
        w.env["fix.qms.evidence.release"]
        .with_user(w.qm)
        .create(
            {
                "external_party": "BSI surveillance auditor",
                "request_note": "Torque calibration log Q3",
            }
        )
    )
    with pytest.raises(UserError, match="released only after approval"), w.env.cr.savepoint():
        rel.with_user(w.qm).action_release()
    with pytest.raises(UserError, match="Attach the evidence"), w.env.cr.savepoint():
        rel.with_user(w.qm2).action_approve()
    rel.with_user(w.qm).write({"attachment_id": att.id})
    with pytest.raises(UserError, match="another Quality Manager"), w.env.cr.savepoint():
        rel.with_user(w.qm).action_approve()
    with pytest.raises(UserError, match="Only the Quality Manager"), w.env.cr.savepoint():
        rel.with_user(w.clerk).action_approve()
    rel.with_user(w.qm2).action_approve()
    with pytest.raises(UserError, match="what was approved"), w.env.cr.savepoint():
        rel.with_user(w.qm).write({"request_note": "everything"})
    rel.with_user(w.clerk).action_release()
    assert rel.state == "released" and rel.released_on
    assert any("access log" in (m.body or "") for m in rel.message_ids)
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        w.env["fix.qms.evidence.release"].with_user(w.qm).create(
            {"external_party": "x", "request_note": "y", "requested_by_user_id": w.qm2.id}
        )


# ---------------------------------------------------------------- page 8
def test_copq_entry_names_its_cause_with_a_basis(w):
    ncr = _ncr(w)
    Copq = w.env["fix.qms.copq"].with_user(w.clerk)
    with pytest.raises(ValidationError, match="basis of its attribution"), w.env.cr.savepoint():
        Copq.create(
            {"period": "2026-11", "amount": 1200, "ncr_id": ncr.id, "attributed_cause": "part"}
        )
    row = Copq.create(
        {
            "period": "2026-11",
            "amount": 1200,
            "ncr_id": ncr.id,
            "attributed_cause": "part",
            "attribution_basis": "Batch 7 seals failed incoming test",
        }
    )
    assert row.name.startswith("COPQ/")


def test_open_findings_kpi_counts_process_audit_findings(w):
    before = m23_ctl.kpis(w.env)["audit_findings"]
    audit = _audit(w)
    audit.with_user(w.qm).action_execute(payload="{}")
    w.env["fix.qms.audit.finding"].with_user(w.qm).create(
        {
            "audit_id": audit.id,
            "classification": "ofi",
            "clause_ref": "10.3",
            "statement": "s",
            "evidence": "e",
        }
    )
    assert m23_ctl.kpis(w.env)["audit_findings"] == before + 1


def test_every_new_form_saves_through_the_workspace(w):
    """Each new form's required fields are enough to save it as a clerk/QM
    through /p03/model/write (no required field the form omits)."""
    audit = _audit(w)
    audit.with_user(w.qm).action_execute(payload="{}")
    capa = _capa(w)
    cases = [
        (
            w.clerk,
            "fix.qms.objective",
            {
                "name": "First-pass QC 95%",
                "policy_id": w.policy.id,
                "scope_level": "company",
                "owner_id": w.owner_emp.id,
                "measure": "passed / completed checks",
                "target": 95,
                "period": "2026",
            },
        ),
        (w.clerk, "fix.qms.change.assessment", {"process_id": w.process.id, "change_summary": "c"}),
        (
            w.clerk,
            "fix.qms.rca",
            {"ncr_id": _ncr(w).id, "method": "ishikawa", "symptom": "s", "root_cause": "r"},
        ),
        (
            w.clerk,
            "fix.capa.action",
            {
                "capa_id": capa.id,
                "name": "a",
                "owner_id": w.owner_emp.id,
                "executing_module": "m23",
            },
        ),
        (w.clerk, "fix.qms.audit.programme", {"name": "IA 2031", "year": "2031"}),
        (
            w.qm,
            "fix.qms.auditor",
            {
                "employee_id": w.qm2_emp.id,
                "standards": "ISO 9001",
                "competence_note": "c",
                "qualified_on": "2026-01-01",
            },
        ),
        (
            w.qm,
            "fix.qms.audit.finding",
            {
                "audit_id": audit.id,
                "classification": "minor",
                "clause_ref": "7.5",
                "statement": "s",
                "evidence": "e",
            },
        ),
        (
            w.qm,
            "fix.qms.evidence.release",
            {"external_party": "Brand partner", "request_note": "n"},
        ),
        (
            w.clerk,
            "fix.qms.copq",
            {
                "period": "2026-11",
                "category": "scrap",
                "amount": 50,
                "currency_id": w.env.ref("base.BDT").id,
                "attributed_cause": "unknown",
            },
        ),
    ]
    for user, model, values in cases:
        out = p03(w, _MW, user=user, model=model, values=values)
        assert "id" in out, (model, out)
