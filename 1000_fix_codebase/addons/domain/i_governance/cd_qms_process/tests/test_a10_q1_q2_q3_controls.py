# A10 remediation (2026-11-04), M23: Q1 CAPA verification authority,
# Q2 NCR closure record, Q3 audit objectivity + certification.
#
# Every control is exercised as NON-ADMIN users holding only the role
# groups each step needs (the superuser is trusted by the field guard and
# would hide a gap). Each control is attacked three ways where it applies:
# the wrong role, a plain write() (the JSON-RPC path) and the real P03
# endpoints (/p03/model/write, /p03/model/action). The legitimate paths run
# end to end through the real actions. The odoo_env fixture rolls back.
import base64
import itertools
import json
import types
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import AccessError, UserError, ValidationError

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
                "name": "A10 M23 %s %d" % (login, n),
                "login": "a10m23.%s.%d@a10.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")
    x.qm = _user(env, "qm", [QM])
    x.qm_emp = env["hr.employee"].create({"name": "A10 QM Rahman", "user_id": x.qm.id})
    x.impl = _user(env, "impl")
    x.impl_emp = env["hr.employee"].create({"name": "A10 Implementer Salam", "user_id": x.impl.id})
    x.owner_emp = env["hr.employee"].create({"name": "A10 Owner Neha"})
    # the private-company branch the audit programme needs
    company = env["res.company"].create({"name": "A10 M23 Audit Co %d" % next(_SEQ)})
    entity = env["fix.entity"].create(
        {"code": "EN-A10M23-%d" % next(_SEQ), "legal_name": "A10 Test Entity", "company_id": company.id}
    )
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.branch = env["fix.branch"].create(
        {"code": "A10M23-%d" % next(_SEQ), "name": "Uttara", "entity_id": entity.id, "operating_unit_id": ou.id}
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
            {"source": "service_order", "severity": severity, "description": "Seal missing on enclosure", **vals}
        )
    )


def _capa_ready(x, severity="major"):
    """new -> root cause -> CAPA (owner = the standalone owner employee)."""
    ncr = _ncr(x, severity)
    ncr.action_set_root_cause("Gasket bin mislabelled")
    capa = ncr.action_open_capa(
        "Fix labelling", "Re-label the bin and rack", owner_id=x.owner_emp.id
    )
    return ncr, capa


# --------------------------------------------------------------------------- Q1
def test_q1_verification_is_quality_manager_only(w):
    _ncr, capa = _capa_ready(w)
    capa.with_user(w.impl).action_implement()
    assert capa.implemented_by_id == w.impl_emp
    # the owner, the implementer and a clerk are all refused: the verdict
    # belongs to the Quality Manager (A10 Q1 / M23-1)
    for user in (w.impl, w.clerk):
        with pytest.raises(UserError, match="Only the Quality Manager"):
            capa.with_user(user).action_verify("looked fine", effective=True)
    with pytest.raises(UserError, match="Only the Quality Manager"):
        capa.with_user(w.clerk).action_verify(note="looked fine")


def test_q1_owner_and_implementer_cannot_verify(w):
    # the QM owns this CAPA themself — refused
    ncr = _ncr(w)
    ncr.action_set_root_cause("Gasket bin mislabelled")
    own_capa = ncr.action_open_capa("Fix labelling", owner_id=w.qm_emp.id)
    own_capa.with_user(w.impl).action_implement()
    with pytest.raises(UserError, match=r"owner of .* cannot verify"):
        own_capa.with_user(w.qm).action_verify("independent enough?")
    # and implementing it themself is refused the same way
    ncr2 = _ncr(w, description="Second case")
    ncr2.action_set_root_cause("Sleeve omitted")
    own_capa2 = ncr2.action_open_capa("Fix sleeve", owner_id=w.owner_emp.id)
    own_capa2.with_user(w.qm).action_implement()  # the QM implemented it
    with pytest.raises(UserError, match=r"implementer of .* cannot verify"):
        own_capa2.with_user(w.qm).action_verify("tried anyway")


def test_q1_verdict_is_stamped_and_evidenced(w):
    ncr, capa = _capa_ready(w)
    capa.with_user(w.impl).action_implement()
    with pytest.raises(UserError, match="verification evidence"):
        capa.with_user(w.qm).action_verify()
    with pytest.raises(UserError, match="only after implementation"):
        (  # a second CAPA that was never implemented
            w.env["fix.capa"]
            .create(
                {
                    "ncr_id": ncr.id,
                    "severity": "minor",
                    "corrective_action": "Second action",
                    "owner_id": w.owner_emp.id,
                }
            )
            .with_user(w.qm)
            .action_verify(note="premature")
        )
    capa.with_user(w.qm).action_verify(note="Recurrence watch: 30 days clean")
    assert (capa.state, capa.effectiveness_result) == ("verified", "effective")
    assert capa.verified_by_id == w.qm_emp
    assert capa.verified_on == fields.Date.context_today(capa)
    assert _events(w.env, "capa.verified", capa.id) == [
        {"ncr": ncr.name, "effective": True}
    ]
    capa.with_user(w.qm).action_close()
    assert capa.state == "closed"


def test_q1_not_effective_reopens_and_blocks_closure(w):
    ncr, capa = _capa_ready(w, "critical")
    capa.with_user(w.impl).action_implement()
    # the workspace prompt arrives as text — "no" is an honest answer
    capa.with_user(w.qm).action_verify(note="Two units failed again", effective="no")
    assert (capa.state, capa.effectiveness_result) == ("open", "not_effective")
    assert _events(w.env, "capa.verified", capa.id)[-1] == {"ncr": ncr.name, "effective": False}
    # a failed verdict can never close the CAPA…
    with pytest.raises(UserError, match="NOT EFFECTIVE"):
        capa.with_user(w.qm).action_close()
    # …nor the CRITICAL NCR behind it
    ncr.action_dispose("rework", "Reworked both units")
    ncr.containment = "Batch held at QC"
    with pytest.raises(UserError, match="VERIFIED-EFFECTIVE, CLOSED CAPA"):
        ncr.with_user(w.qm).action_close()
    # rework, then a clean verdict closes both
    capa.with_user(w.impl).action_implement()
    capa.with_user(w.qm).action_verify(note="Clean for 30 days", effective="yes")
    capa.with_user(w.qm).action_close()
    ncr.with_user(w.qm).action_close()
    assert (ncr.state, capa.state) == ("closed", "closed")


def test_q1_verdict_fields_are_guarded(w):
    ncr, capa = _capa_ready(w)
    capa.with_user(w.impl).action_implement()
    for vals in (
        {"state": "verified"},
        {"effectiveness_result": "effective"},
        {"verified_by_id": w.qm_emp.id},
    ):
        with pytest.raises(UserError, match=GUARD):
            capa.with_user(w.clerk).write(vals)
    with pytest.raises(UserError, match=GUARD):
        w.env["fix.capa"].with_user(w.clerk).create(
            {
                "ncr_id": ncr.id,
                "severity": "minor",
                "corrective_action": "Born verified",
                "owner_id": w.owner_emp.id,
                "state": "verified",
            }
        )
    # closed verdicts freeze the record itself — the form endpoint refuses
    # the changed locked fields (the ORM-level guard covers the verdict
    # fields above; the freeze extends to the closed actions here)
    capa.with_user(w.qm).action_verify(note="Done")
    capa.with_user(w.qm).action_close()
    out = p03(
        w, _MW, user=w.qm, model="fix.capa", record_id=capa.id,
        values={"corrective_action": "rewritten"},
    )
    assert "error" in out


def test_q1_p03_write_and_action(w):
    _ncr, capa = _capa_ready(w)
    capa.with_user(w.impl).action_implement()
    out = p03(
        w, _MW, user=w.clerk, model="fix.capa", record_id=capa.id,
        values={"effectiveness_result": "effective"},
    )
    assert "error" in out and GUARD in out["error"]
    out = p03(
        w, _MA, user=w.qm, model="fix.capa", ids=capa.ids, method="action_verify",
        kwargs={"note": "P11 evidence reviewed", "effective": True},
    )
    assert out.get("success") is True
    assert (capa.state, capa.verified_by_id) == ("verified", w.qm_emp)
    # closure after the verdict is mechanical — the VERDICT was the
    # protected step, not the closing click
    out = p03(w, _MA, user=w.clerk, model="fix.capa", ids=capa.ids, method="action_close")
    assert out.get("success") is True
    assert capa.state == "closed"


# --------------------------------------------------------------------------- Q2
def test_q2_concession_is_quality_manager_stamped(w):
    ncr, _capa = _capa_ready(w)
    with pytest.raises(UserError, match="Only the Quality Manager"):
        ncr.with_user(w.clerk).action_dispose("use_as_is", "field fix ok")
    ncr.with_user(w.qm).action_dispose("use_as_is", "Cosmetic only, customer informed")
    assert ncr.disposition == "use_as_is"
    assert ncr.concession_approved_by_id == w.qm_emp  # stamped, never typed
    # a caller-typed approver never reaches the record
    with pytest.raises(UserError, match=GUARD):
        ncr.with_user(w.qm).write({"concession_approved_by_id": w.owner_emp.id})


def test_q2_ncr_closes_with_its_full_record(w):
    ncr, capa = _capa_ready(w, "critical")
    # disposition first (ISO 9001 8.7.1)
    with pytest.raises(UserError, match="Record the disposition"):
        ncr.with_user(w.qm).action_close()
    ncr.with_user(w.qm).action_dispose("return", "Returned to supplier")
    # then containment for MAJOR/CRITICAL (8.7.1 f)
    with pytest.raises(UserError, match="containment"):
        ncr.with_user(w.qm).action_close()
    ncr.containment = "Batch quarantined"
    # then a VERIFIED-EFFECTIVE CLOSED CAPA (10.2.1 d) — never a CAPA that
    # merely exists, or stands implemented
    with pytest.raises(UserError, match="VERIFIED-EFFECTIVE"):
        ncr.with_user(w.qm).action_close()
    with pytest.raises(UserError, match="Closure follows verification"):
        capa.with_user(w.qm).action_close()
    capa.with_user(w.impl).action_implement()
    with pytest.raises(UserError, match="Closure follows verification"):
        capa.with_user(w.qm).action_close()
    capa.with_user(w.qm).action_verify(note="Verified clean")
    capa.with_user(w.qm).action_close()
    ncr.with_user(w.qm).action_close()
    assert ncr.state == "closed"
    # the lifecycle stays guarded on the closed record…
    with pytest.raises(UserError, match=GUARD):
        ncr.with_user(w.qm).write({"state": "new"})
    # …and the closed record's analysis is frozen at the form endpoint
    # (append-only, BRU-QMS-11)
    out = p03(
        w, _MW, user=w.qm, model="fix.ncr", record_id=ncr.id,
        values={"root_cause": "rewritten"},
    )
    assert "error" in out


def test_q2_state_and_disposition_are_guarded(w):
    ncr, _capa = _capa_ready(w)
    for vals in ({"state": "closed"}, {"disposition": "scrap"}):
        with pytest.raises(UserError, match=GUARD):
            ncr.with_user(w.clerk).write(vals)
    out = p03(
        w, _MW, user=w.clerk, model="fix.ncr", record_id=ncr.id,
        values={"state": "closed"},
    )
    assert "error" in out and GUARD in out["error"]
    out = p03(
        w, _MA, user=w.clerk, model="fix.ncr", ids=ncr.ids, method="action_dispose",
        kwargs={"disposition": "scrap", "note": "scrapped"},
    )
    assert out.get("success") is True and ncr.disposition == "scrap"


# --------------------------------------------------------------------------- Q3
def _process(x, owner_emp, code):
    return x.env["fix.qms.process"].create(
        {
            "name": "Bench repair %s" % code,
            "code": code,
            "process_owner_id": owner_emp.id,
        }
    )


def _audit(x, auditor_emp, **vals):
    return x.env["fix.internal.audit"].create(
        {
            "branch_id": x.branch.id,
            "scheduled_on": date(2026, 11, 3),
            "auditor_id": auditor_emp.id,
            "scope": "ISO 9001 8.5 production control",
            **vals,
        }
    )


def test_q3_auditor_cannot_own_an_audited_process(w):
    auditor_emp = w.env["hr.employee"].create({"name": "A10 Auditor Tania"})
    owned = _process(w, auditor_emp, "A10OWN")
    other = _process(w, w.owner_emp, "A10OTH")
    audit = _audit(w, auditor_emp, process_ids=[(6, 0, [owned.id, other.id])])
    with pytest.raises(UserError, match="may not audit their own process"):
        audit.with_user(w.clerk).action_execute()
    assert audit.state == "planned"
    # scope the audit honestly and it executes
    audit.process_ids = [(6, 0, [other.id])]
    audit.with_user(w.clerk).action_execute('{"checklist": "8.5", "ok": 9, "nc": 0}')
    assert audit.state == "executed"


def test_q3_report_needs_executed_evidence(w):
    auditor_emp = w.env["hr.employee"].create({"name": "A10 Auditor Rana"})
    audit = _audit(w, auditor_emp)
    with pytest.raises(UserError, match="only after it is executed"):
        audit.with_user(w.clerk).action_report()
    audit.with_user(w.clerk).action_execute()  # no payload yet
    with pytest.raises(UserError, match="checklist evidence"):
        audit.with_user(w.clerk).action_report()
    audit.with_user(w.clerk).action_execute('{"checklist": "8.5", "ok": 8, "nc": 1}')
    audit.with_user(w.clerk).action_report()
    assert audit.state == "reported"
    assert _events(w.env, "audit.reported", audit.id)[0]["major_findings"] == 0
    # the reported record is frozen
    with pytest.raises(UserError, match=GUARD):
        audit.with_user(w.clerk).write({"state": "planned"})


def test_q3_major_findings_leave_with_their_capa(w):
    auditor_emp = w.env["hr.employee"].create({"name": "A10 Auditor Lima"})
    proc_owner = w.env["hr.employee"].create({"name": "A10 Process Owner Kabir"})
    scoped = _process(w, proc_owner, "A10MAJ")
    audit = _audit(w, auditor_emp, process_ids=[(6, 0, [scoped.id])])
    audit.with_user(w.clerk).action_execute('{"checklist": "8.5", "ok": 7, "nc": 2}')
    major = _ncr(w, "major", audit_id=audit.id)
    minor = _ncr(w, "minor", audit_id=audit.id)
    audit.with_user(w.clerk).action_report()
    # the MAJOR finding now carries its CAPA, owned by the audited
    # process's owner (never the auditor's own verdict loop)
    assert major.capa_id and len(major.capa_id) == 1
    assert major.state == "capa_open"
    assert major.capa_id.owner_id == proc_owner
    # the MINOR finding is left to the normal journey
    assert not minor.capa_id and minor.state == "new"
    (payload,) = _events(w.env, "audit.reported", audit.id)
    assert payload == {
        "branch": w.branch.name,
        "major_findings": 1,
        "systems_traced": False,
    }


def test_q3_certification_belongs_to_the_quality_manager(w):
    Cert = w.env["fix.qms.certification"]
    with pytest.raises(AccessError):
        Cert.with_user(w.clerk).create({"name": "ISO 9001 surveillance"})
    rec = Cert.with_user(w.qm).create(
        {"name": "ISO 9001 surveillance", "audit_type": "surveillance"}
    )
    # the clerk reads the certificate record but cannot type on it
    assert Cert.with_user(w.clerk).search([("id", "=", rec.id)]).name == rec.name
    with pytest.raises(AccessError):
        rec.with_user(w.clerk).write({"notes": "typed"})
    with pytest.raises(UserError, match=GUARD):
        rec.with_user(w.qm).write({"result": "passed"})  # even the QM types it
    # a PASS needs the certificate document attached
    with pytest.raises(UserError, match="Attach the certificate document"):
        rec.with_user(w.qm).action_pass()
    attachment = w.env["ir.attachment"].create(
        {"name": "iso9001-cert.pdf", "datas": base64.b64encode(b"%PDF-cert").decode()}
    )
    doc = w.env["fix.document"].create(
        {"name": "ISO 9001 certificate scan", "attachment_id": attachment.id}
    )
    rec.with_user(w.qm).write({"certificate_doc_id": doc.id})
    rec.with_user(w.qm).action_pass()
    assert rec.result == "passed"
    with pytest.raises(UserError, match="Only the Quality Manager"):
        rec.with_user(w.clerk).action_record_result("failed")
    rec.with_user(w.qm).action_record_result("minor_ncs")
    assert rec.result == "minor_ncs"
    with pytest.raises(UserError, match="use action_pass"):
        rec.with_user(w.qm).action_record_result("passed")
    # the certificate window is honest: validity ends after the audit
    # A10 deep audit 2026-11-22 (A1-F08): the validity window is frozen
    # after creation — the QM can no longer type it at all
    with pytest.raises(UserError, match="Valid Until"):
        rec.with_user(w.qm).write({"valid_until": rec.audit_date - timedelta(days=1)})
    # and the constraint still refuses a window that ends before the audit
    # (reachable through the superuser / creation path)
    with pytest.raises(ValidationError, match="validity ends after its audit date"):
        Cert.create(
            {
                "name": "ISO 9001 bad window",
                "audit_type": "surveillance",
                "valid_until": rec.audit_date - timedelta(days=1),
            }
        )
    out = p03(w, _MA, user=w.clerk, model="fix.qms.certification", ids=rec.ids, method="action_pass")
    assert out.get("success") is False
