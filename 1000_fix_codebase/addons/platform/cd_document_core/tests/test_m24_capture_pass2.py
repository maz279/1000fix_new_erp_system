# M24 capture audit, second pass (19 Nov 2026): the spec records the
# sub-module pages capture, driven as NON-ADMIN users through the workspace
# endpoints (/p03/model/write, /p03/model/action) where a person would, and
# their rules checked against the live ORM.
#
#   p1  fix.physical.record, fix.document.integrity.check
#   p2  template versions under approval (FR-DMS-021)
#   p3  fix.document.class + fix.document.exception (FR-DMS-004/006)
#   p4  fix.document.distribution + acknowledgement (FR-DMS-019)
#   p5  fix.esignature.wet.signature, envelope verification (FR-DMS-026/033)
#   p6  fix.legal.hold.order, fix.disposal.batch, fix.retention.violation
#   p7  fix.evidence.pack, fix.external.release + the public route
import base64
import io
import itertools
import types
from datetime import date, timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import AccessError, UserError

RECORDS = "cd_document_core.group_document_records"
CONTROLLER = "cd_document_core.group_document_controller"
APPROVER = "cd_document_core.group_disposal_approver"
FILE = base64.b64encode(b"M24 pass 2 evidence bytes").decode()

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)
_SEQ = itertools.count(1)


def _user(env, tag, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M24P2 %s %d" % (tag, n),
                "login": "m24p2.%s.%d@a10.test" % (tag, n),
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
    x.clerk2 = _user(env, "clerk2")
    x.records = _user(env, "records", [RECORDS])
    x.records2 = _user(env, "records2", [RECORDS, APPROVER])
    x.controller = _user(env, "controller", [CONTROLLER])
    x.controller2 = _user(env, "controller2", [CONTROLLER])
    x.approver = _user(env, "approver", [APPROVER])
    x.rc = env["fix.retention.class"].create(
        {"code": "T24-%d" % next(_SEQ), "name": "Pass-2 class", "retention_years": 3}
    )
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


def p03(x, endpoint, user, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=user.id))
    return endpoint(g.P03GenericApiController(), **kw)


def write(x, user, model, values, **kw):
    return p03(x, _MW, user, model=model, values=values, **kw)


def act(x, user, model, ids, method, **kwargs):
    return p03(x, _MA, user, model=model, ids=ids, method=method, kwargs=kwargs or None)


def _doc(x, user=None, raw=b"document bytes", **vals):
    attachment = x.env["ir.attachment"].create({"name": "f", "datas": base64.b64encode(raw)})
    return (
        x.env["fix.document"]
        .with_user(user or x.clerk)
        .create({"name": "P2 Doc %d" % next(_SEQ), "attachment_id": attachment.id, **vals})
        .sudo()
    )


def _expire(x, doc, days_ago=1):
    x.env.flush_all()
    x.env.cr.execute(
        "UPDATE fix_document SET state='expired', retention_expires=%s WHERE id=%s",
        [date.today() - timedelta(days=days_ago), doc.id],
    )
    doc.invalidate_recordset()
    return doc


def _class(x, doc_type="contract", **extra):
    res = write(
        x,
        x.records,
        "fix.document.class",
        dict(
            code="C%d" % next(_SEQ),
            name="Class",
            document_type=doc_type,
            retention_class_id=x.rc.id,
            isolation_tier="T3",
            **extra,
        ),
    )
    assert "id" in res, res
    return x.env["fix.document.class"].browse(res["id"])


# ======================================================================= p3
def test_class_is_written_by_records_and_activated_by_another_controller(w):
    refused = write(
        w,
        w.clerk,
        "fix.document.class",
        {"code": "X", "name": "X", "document_type": "contract", "retention_class_id": w.rc.id},
    )
    assert "error" in refused, refused
    cls = _class(w)
    assert cls.state == "draft" and cls.last_edited_by_id == w.records
    # a controller who wrote it cannot activate it
    own = write(
        w,
        w.controller2,
        "fix.document.class",
        {
            "code": "C%d" % next(_SEQ),
            "name": "Own",
            "document_type": "invoice",
            "retention_class_id": w.rc.id,
        },
    )
    out = act(w, w.controller2, "fix.document.class", [own["id"]], "action_activate")
    assert not out.get("success") and "Segregation" in out.get("error", ""), out
    assert not act(w, w.clerk, "fix.document.class", cls.ids, "action_activate").get("success")
    assert act(w, w.controller, "fix.document.class", cls.ids, "action_activate").get("success")
    assert cls.state == "active" and cls.activated_by_id == w.controller
    # frozen once active
    out = write(w, w.records, "fix.document.class", {"isolation_tier": "T1"}, record_id=cls.id)
    assert "error" in out, out
    # one active class per type (BRU-DMS-01)
    twin = _class(w)
    with pytest.raises(UserError, match="exactly one"):
        twin.with_user(w.controller2).action_activate()


def test_a_capture_missing_class_metadata_waits_in_the_exception_queue(w):
    cls = _class(w, need_name_bn=True, need_link=True)
    cls.with_user(w.controller).action_activate()
    res = write(
        w,
        w.clerk,
        "fix.document",
        {
            "upload_file": FILE,
            "upload_filename": "c.pdf",
            "name": "Unlinked contract",
            "document_type": "contract",
        },
    )
    assert "id" in res, res
    doc = w.env["fix.document"].browse(res["id"])
    # the class applied its retention class and raised the tier
    assert doc.class_id == cls and doc.retention_class_id == w.rc and doc.isolation_tier == "T3"
    assert doc.filing_state == "exception"
    (exc,) = w.env["fix.document.exception"].search([("document_id", "=", doc.id)])
    assert "Bengali name" in exc.cause and "business-object link" in exc.cause
    # not filed while metadata is missing; a clerk cannot classify
    with pytest.raises(UserError, match="still lacks"):
        exc.with_user(w.records).action_resolve()
    out = write(w, w.clerk, "fix.document.exception", {"doc_name_bn": "চুক্তি"}, record_id=exc.id)
    assert "error" in out, out
    out = write(
        w,
        w.records,
        "fix.document.exception",
        {
            "doc_name_bn": "চুক্তি",
            "doc_res_model": "res.partner",
            "doc_res_id": w.clerk.partner_id.id,
        },
        record_id=exc.id,
    )
    assert "id" in out, out
    assert act(
        w, w.records, "fix.document.exception", exc.ids, "action_resolve", note="linked"
    ).get("success")
    assert (exc.state, doc.filing_state, doc.name_bn) == ("resolved", "filed", "চুক্তি")
    # a complete capture files straight away
    ok = write(
        w,
        w.clerk,
        "fix.document",
        {
            "upload_file": FILE,
            "upload_filename": "d.pdf",
            "name": "Linked",
            "name_bn": "লিঙ্ক",
            "document_type": "contract",
            "res_model": "res.partner",
            "res_id": w.clerk.partner_id.id,
        },
    )
    assert w.env["fix.document"].browse(ok["id"]).filing_state == "filed"


def test_an_unclassifiable_type_is_queued_once_classification_is_on(w):
    _class(w, doc_type="invoice").with_user(w.controller).action_activate()
    doc = _doc(w, document_type="warranty_card")
    assert doc.filing_state == "exception" and not doc.class_id
    assert (
        w.env["fix.document.exception"].search_count(
            [("document_id", "=", doc.id), ("state", "=", "open")]
        )
        == 1
    )


# ======================================================================= p1
def test_paper_original_register_and_evidenced_destruction(w):
    doc = _doc(w, retention_class_id=w.rc.id)
    vals = {
        "document_id": doc.id,
        "location": "Mirpur store room",
        "box_ref": "BX-12",
        "custodian_id": w.clerk.id,
        "condition": "good",
    }
    assert "error" in write(w, w.clerk, "fix.physical.record", vals)
    res = write(w, w.records, "fix.physical.record", vals)
    assert "id" in res, res
    phys = w.env["fix.physical.record"].browse(res["id"])
    assert phys.name.startswith("PHY-") and phys.destruction_due_on == doc.retention_expires
    with pytest.raises(UserError, match="has not run"):
        phys.with_user(w.records).action_record_destruction()
    _expire(w, doc)
    with pytest.raises(UserError, match="evidence"):
        phys.with_user(w.records).action_record_destruction()
    out = write(w, w.records, "fix.physical.record", {"evidence_file": FILE}, record_id=phys.id)
    assert "id" in out, out
    assert phys.destruction_evidence_id.document_type == "destruction_certificate"
    assert act(w, w.records, "fix.physical.record", phys.ids, "action_record_destruction").get(
        "success"
    )
    assert (phys.state, phys.destroyed_by_id) == ("destroyed", w.records)


def test_paper_original_of_a_held_document_is_never_destroyed(w):
    doc = _expire(w, _doc(w, retention_class_id=w.rc.id))
    phys = (
        w.env["fix.physical.record"]
        .with_user(w.records)
        .create({"document_id": doc.id, "location": "Vault", "evidence_file": FILE})
    )
    doc.with_user(w.records).action_legal_hold("Case 7")
    with pytest.raises(UserError, match="legal hold"):
        phys.with_user(w.records).action_record_destruction()


def test_integrity_sweep_finds_bytes_that_no_longer_match(w):
    doc = _doc(w, raw=b"original bytes")
    w.env.flush_all()
    w.env.cr.execute("UPDATE fix_document SET checksum_sha256=%s WHERE id=%s", ["0" * 64, doc.id])
    doc.invalidate_recordset()
    assert "error" in write(w, w.clerk, "fix.document.integrity.check", {"note": "x"})
    res = write(w, w.records, "fix.document.integrity.check", {"note": "audit prep"})
    assert "id" in res, res
    sweep = w.env["fix.document.integrity.check"].browse(res["id"])
    assert sweep.run_by_id == w.records and sweep.documents_checked >= 1
    assert doc in sweep.line_ids.document_id and sweep.divergences_found >= 1
    # a sweep is a record: it is not edited afterwards
    assert "error" in write(
        w, w.records, "fix.document.integrity.check", {"note": "edited"}, record_id=sweep.id
    )


# ======================================================================= p2
def test_template_versions_are_approved_by_another_controller_and_never_edited(w):
    code = "P2T%d" % next(_SEQ)
    res = write(
        w,
        w.clerk,
        "fix.document.template",
        {"code": code, "name": "Notice", "name_bn": "নোটিশ", "document_type": "notice"},
    )
    assert "id" in res, res
    v1 = w.env["fix.document.template"].browse(res["id"])
    assert (v1.state, v1.version) == ("draft", 1)
    with pytest.raises(AccessError):
        v1.with_user(w.clerk).action_approve()
    assert act(w, w.controller, "fix.document.template", v1.ids, "action_approve").get("success")
    assert (v1.state, v1.approved_by_id) == ("approved", w.controller)
    out = write(w, w.clerk, "fix.document.template", {"name": "Edited in place"}, record_id=v1.id)
    assert "error" in out, out
    # frozen on both layers: the form shows the terms read-only, the ORM refuses
    assert {"name", "code", "report_ref"} <= v1._fix_form_locked_fields()
    with pytest.raises(UserError, match="never edited"):
        v1.with_user(w.clerk).write({"name": "Edited through the ORM"})
    out = act(w, w.clerk, "fix.document.template", v1.ids, "action_new_version")
    assert out.get("success"), out
    v2 = w.env["fix.document.template"].search([("code", "=", code), ("version", "=", 2)])
    assert v2.state == "draft" and v2.previous_id == v1
    # an unapproved change generates nothing
    with pytest.raises(UserError, match="unapproved change"):
        _doc(w, template_id=v2.id, document_type="other")
    # its author (a controller) cannot approve it
    v2.with_user(w.controller2).write({"name": "Notice v2"})
    with pytest.raises(UserError, match="Segregation"):
        v2.with_user(w.controller2).action_approve()
    v2.with_user(w.controller).action_approve()
    assert (v1.state, v2.state) == ("retired", "approved")
    with pytest.raises(UserError, match="retired"):
        _doc(w, template_id=v1.id, document_type="other")


# ======================================================================= p4
def _published(x):
    doc = _doc(x, user=x.clerk, is_controlled=True)
    doc._guarded().write({"control_state": "published", "published_on": date.today()})
    return doc


def test_distribution_reaches_named_people_who_acknowledge_themselves(w):
    draft = _doc(w, is_controlled=True)
    res = write(
        w,
        w.clerk,
        "fix.document.distribution",
        {"document_id": draft.id, "recipient_ids": [w.clerk2.id]},
    )
    assert "id" in res, res
    with pytest.raises(UserError, match="PUBLISHED"):
        w.env["fix.document.distribution"].browse(res["id"]).with_user(w.clerk).action_distribute()
    doc = _published(w)
    res = write(
        w,
        w.clerk2,
        "fix.document.distribution",
        {
            "document_id": doc.id,
            "recipient_ids": [w.clerk2.id, w.records.id],
            "due_on": str(date.today() + timedelta(days=7)),
        },
    )
    dist = w.env["fix.document.distribution"].browse(res["id"])
    # neither the author nor a controller: refused
    assert not act(w, w.clerk2, "fix.document.distribution", dist.ids, "action_distribute").get(
        "success"
    )
    assert act(w, w.clerk, "fix.document.distribution", dist.ids, "action_distribute").get(
        "success"
    )
    assert dist.state == "distributed" and dist.recipient_count == 2
    mine = dist.ack_ids.filtered(lambda a: a.user_id == w.clerk2)
    assert not act(
        w, w.records, "fix.document.acknowledgement", mine.ids, "action_acknowledge"
    ).get("success")
    assert act(w, w.clerk2, "fix.document.acknowledgement", mine.ids, "action_acknowledge").get(
        "success"
    )
    assert mine.state == "acknowledged" and dist.state == "distributed"
    act(
        w,
        w.records,
        "fix.document.acknowledgement",
        (dist.ack_ids - mine).ids,
        "action_acknowledge",
    )
    assert dist.state == "closed" and dist.acknowledged_count == 2


# ======================================================================= p6
def test_disposal_batch_is_prepared_by_one_and_approved_by_another(w):
    d1, d2 = (_expire(w, _doc(w, retention_class_id=w.rc.id)) for _ in range(2))
    held = _expire(w, _doc(w, retention_class_id=w.rc.id))
    held.with_user(w.records).action_legal_hold("Matter 9")
    vals = {"retention_class_id": w.rc.id, "cutoff_on": str(date.today()), "method": "secure_wipe"}
    assert "error" in write(w, w.clerk, "fix.disposal.batch", vals)
    res = write(w, w.records2, "fix.disposal.batch", vals)
    assert "id" in res, res
    batch = w.env["fix.disposal.batch"].browse(res["id"])
    assert set(batch.document_ids.ids) == {d1.id, d2.id} and batch.excluded_held_ids == held
    assert act(w, w.records2, "fix.disposal.batch", batch.ids, "action_submit").get("success")
    # the preparer cannot approve, even holding the approver role (SOD-23)
    with pytest.raises(UserError, match="Segregation"):
        batch.with_user(w.records2).action_approve()
    with pytest.raises(AccessError):
        batch.with_user(w.records).action_approve()
    assert act(w, w.approver, "fix.disposal.batch", batch.ids, "action_approve").get("success")
    assert act(w, w.records, "fix.disposal.batch", batch.ids, "action_execute").get("success")
    assert batch.state == "completed" and batch.certificate_doc_id
    for d in (d1, d2):
        d.invalidate_recordset()
        assert d.state == "destroyed" and not d.attachment_id.datas
        reg = w.env["fix.disposal.record"].search([("document_id", "=", d.id)])
        assert reg.batch_id == batch and reg.performed_by_id == w.records
    held.invalidate_recordset()
    assert held.state == "expired"


def test_a_document_held_after_approval_fails_the_whole_batch(w):
    d1, d2 = (_expire(w, _doc(w, retention_class_id=w.rc.id)) for _ in range(2))
    batch = w.env["fix.disposal.batch"].with_user(w.records).create({"retention_class_id": w.rc.id})
    batch.action_submit()
    batch.with_user(w.approver).action_approve()
    d2.with_user(w.records).action_legal_hold("Late notice")
    batch.action_execute()
    assert batch.state == "failed" and d2.name in batch.outcome_note
    for d in (d1, d2):
        d.invalidate_recordset()
        assert d.state == "expired"  # nothing disposed


def test_a_lone_disposal_is_refused(w):
    doc = _expire(w, _doc(w))
    out = act(w, w.records, "fix.document", doc.ids, "action_dispose")
    assert not out.get("success") and "Disposal Batch" in out["error"], out


def test_retention_scan_finds_both_directions_once(w):
    over = _expire(w, _doc(w, retention_class_id=w.rc.id), days_ago=400)
    early = _doc(w, retention_class_id=w.rc.id)
    early._guarded().write({"active": False})
    V = w.env["fix.retention.violation"]
    V.cron_retention_scan()
    V.cron_retention_scan()
    assert (
        V.search_count([("document_id", "=", over.id), ("violation_type", "=", "over_retained")])
        == 1
    )
    (v,) = V.with_context(active_test=False).search([("document_id", "=", early.id)])
    assert v.violation_type == "missing_early" and v.raised_by == "scan"
    assert not act(w, w.clerk, "fix.retention.violation", v.ids, "action_close", note="x").get(
        "success"
    )
    with pytest.raises(UserError, match="cause"):
        v.with_user(w.records).action_close(" ")
    v.with_user(w.records).action_close("Archived by mistake; restored")
    assert v.state == "closed" and v.closed_by_id == w.records
    # a Records Officer raises one found in an audit
    res = write(
        w,
        w.records,
        "fix.retention.violation",
        {"document_id": early.id, "violation_type": "over_retained", "detail": "Found on audit"},
    )
    assert "id" in res, res


def test_a_scoped_hold_catches_existing_and_later_documents_and_releases_matter_by_matter(w):
    partner = w.clerk2.partner_id
    link = {"res_model": "res.partner", "res_id": partner.id}
    a, b = _doc(w, **link), _doc(w, **link)
    other = _doc(w)
    empty = write(
        w, w.records, "fix.legal.hold.order", {"matter_ref": "M-0", "instructed_by": "Counsel"}
    )
    assert "Define the scope" in act(
        w, w.records, "fix.legal.hold.order", [empty["id"]], "action_apply"
    ).get("error", "")
    res = write(
        w,
        w.records,
        "fix.legal.hold.order",
        {
            "matter_ref": "BD-HC 55/2026",
            "instructed_by": "External counsel",
            "scope_res_model": "res.partner",
            "scope_res_id": partner.id,
        },
    )
    order = w.env["fix.legal.hold.order"].browse(res["id"])
    assert not act(w, w.clerk, "fix.legal.hold.order", order.ids, "action_apply").get("success")
    assert act(w, w.records, "fix.legal.hold.order", order.ids, "action_apply").get("success")
    assert a.legal_hold and b.legal_hold and not other.legal_hold and order.document_count == 2
    later = _doc(w, **link)
    assert later.legal_hold  # propagated (FR-DMS-036)
    second = (
        w.env["fix.legal.hold.order"]
        .with_user(w.records)
        .create(
            {
                "matter_ref": "NBR inquiry 3",
                "instructed_by": "NBR",
                "scope_res_model": "res.partner",
                "scope_res_id": partner.id,
            }
        )
    )
    second.action_apply()
    with pytest.raises(UserError, match="more than one matter"):
        a.with_user(w.records).action_release_hold("done")
    order.with_user(w.records).action_release("Court lifted the order")
    a.invalidate_recordset()
    assert (
        a.legal_hold and a.legal_hold_reason == "NBR inquiry 3"
    )  # the other matter still holds it
    second.with_user(w.records).action_release("Inquiry closed")
    a.invalidate_recordset()
    assert not a.legal_hold


# ======================================================================= p7
def test_evidence_pack_names_what_is_missing_and_seals(w):
    partner = w.clerk2.partner_id
    inv = _doc(w, document_type="invoice", res_model="res.partner", res_id=partner.id)
    res = write(
        w,
        w.clerk,
        "fix.evidence.pack",
        {
            "purpose": "claim",
            "subject_label": "Claim WC-1",
            "subject_model": "res.partner",
            "subject_id": partner.id,
        },
        lines={
            "field": "requirement_ids",
            "rows": [
                {"values": {"document_type": "invoice", "min_count": 1}},
                {"values": {"document_type": "service_report", "min_count": 1}},
            ],
        },
    )
    assert "id" in res, res
    pack = w.env["fix.evidence.pack"].browse(res["id"])
    assert act(w, w.clerk, "fix.evidence.pack", pack.ids, "action_collect").get("success")
    assert pack.document_ids == inv
    assert act(w, w.clerk, "fix.evidence.pack", pack.ids, "action_assemble").get("success")
    assert pack.state == "sealed" and pack.completeness_state == "incomplete"
    assert "Service Report: 0 of 1" in pack.missing_items and len(pack.sealed_hash) == 64
    assert pack.manifest_doc_id.document_type == "evidence_pack"
    assert "error" in write(
        w, w.clerk, "fix.evidence.pack", {"subject_label": "changed"}, record_id=pack.id
    )
    pack.action_verify()
    assert pack.verification_result == "intact"
    inv.attachment_id.sudo().write({"datas": base64.b64encode(b"swapped")})
    pack.action_verify()
    assert pack.verification_result == "broken"


def _pdf():
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(72, 720, "Service report body")
    c.save()
    return buf.getvalue()


def test_external_release_is_approved_by_another_scoped_timeboxed_and_logged(w):
    from odoo.addons.cd_document_core.controllers import fix_release

    doc = _doc(w, raw=_pdf())
    t5 = _doc(w, isolation_tier="T5")
    auditor = w.env["res.partner"].create({"name": "Audit Firm LLP"})
    base = {"partner_id": auditor.id, "purpose": "ISO surveillance audit", "watermark": True}
    too_long = write(
        w,
        w.clerk,
        "fix.external.release",
        dict(base, document_ids=[doc.id], expires_on=str(date.today() + timedelta(days=60))),
    )
    assert "too long" not in str(too_long)
    out = act(w, w.clerk, "fix.external.release", [too_long["id"]], "action_request")
    assert "at most 30 days" in out.get("error", ""), out
    secret = write(
        w,
        w.clerk,
        "fix.external.release",
        dict(base, document_ids=[t5.id], expires_on=str(date.today() + timedelta(days=5))),
    )
    assert "T5" in act(w, w.clerk, "fix.external.release", [secret["id"]], "action_request").get(
        "error", ""
    )
    res = write(
        w,
        w.clerk,
        "fix.external.release",
        dict(base, document_ids=[doc.id], expires_on=str(date.today() + timedelta(days=5))),
    )
    rel = w.env["fix.external.release"].browse(res["id"])
    assert act(w, w.clerk, "fix.external.release", rel.ids, "action_request").get("success")
    with pytest.raises(AccessError):
        rel.with_user(w.clerk).action_grant()
    rel_by_records = (
        w.env["fix.external.release"]
        .with_user(w.records)
        .create(
            dict(base, document_ids=[(6, 0, doc.ids)], expires_on=date.today() + timedelta(days=5))
        )
    )
    rel_by_records.action_request()
    with pytest.raises(UserError, match="Segregation"):
        rel_by_records.action_grant()
    assert act(w, w.records, "fix.external.release", rel.ids, "action_grant").get("success")
    token = rel.sudo().access_token
    assert rel.state == "granted" and token and rel.access_url.endswith(token)

    # the public route: scope, watermark, log
    responses = []
    fake = types.SimpleNamespace(
        env=w.env(user=w.env.ref("base.public_user").id),
        httprequest=types.SimpleNamespace(remote_addr="203.0.113.7"),
        make_response=lambda body, headers=None, status=200: responses.append(
            (status, dict(headers or []), body)
        )
        or responses[-1],
    )
    saved = fix_release.request
    fix_release.request = fake
    try:
        cls_ = fix_release.DmsExternalRelease
        raw_index = getattr(cls_.release_index, "original_endpoint", cls_.release_index)
        raw_file = getattr(cls_.release_file, "original_endpoint", cls_.release_file)
        ctl = types.SimpleNamespace(
            release_index=lambda t: raw_index(cls_(), t),
            release_file=lambda t, d: raw_file(cls_(), t, d),
        )
        status, _h, body = ctl.release_index(token)
        assert status == 200 and doc.name in body
        status, headers, raw = ctl.release_file(token, doc.id)
        assert status == 200 and headers["X-Release"] == rel.name and raw[:4] == b"%PDF"
        from odoo.tools.pdf import PdfFileReader

        text = PdfFileReader(io.BytesIO(raw)).pages[0].extract_text()
        assert "CONTROLLED RELEASE" in text and rel.name in text
        assert ctl.release_file(token, t5.id)[0] == 404  # out of scope
        assert ctl.release_index("x" * 43)[0] == 404
        actions = rel.access_log_ids.mapped("action")
        assert {"release", "view", "download"} <= set(actions)
        assert "203.0.113.7" in rel.access_log_ids.mapped("ip_or_device")
        # revoked: the link is dead
        rel.with_user(w.clerk).action_revoke("Audit closed")
        assert not rel.sudo().access_token
        assert ctl.release_index(token)[0] == 404
    finally:
        fix_release.request = saved
    with pytest.raises(AccessError):
        w.env["fix.document.access.log"].with_user(w.records).create(
            {"document_id": doc.id, "action": "view"}
        )


def test_external_release_expires_by_itself(w):
    doc = _doc(w)
    rel = (
        w.env["fix.external.release"]
        .with_user(w.clerk)
        .create(
            {
                "partner_id": w.clerk2.partner_id.id,
                "purpose": "p",
                "document_ids": [(6, 0, doc.ids)],
                "expires_on": date.today() + timedelta(days=2),
            }
        )
    )
    rel.action_request()
    rel.with_user(w.records).action_grant()
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_external_release SET expires_on=%s WHERE id=%s",
        [date.today() - timedelta(days=1), rel.id],
    )
    rel.invalidate_recordset()
    assert not w.env["fix.external.release"]._resolve_token(rel.sudo().access_token)
    w.env["fix.external.release"].cron_expire_releases()
    assert rel.state == "expired" and not rel.sudo().access_token


# ======================================================================= p5
def _sent_envelope(x, partners, doc=None):
    doc = doc or _doc(x)
    env_rec = (
        x.env["fix.esignature.envelope"]
        .with_user(x.clerk)
        .create(
            {
                "name": "P2 envelope %d" % next(_SEQ),
                "document_id": doc.id,
                "operating_unit_id": x.env["operating.unit"].search([], limit=1).id,
                "signer_ids": [
                    (0, 0, {"sequence": (i + 1) * 10, "partner_id": p.id})
                    for i, p in enumerate(partners)
                ],
            }
        )
    )
    env_rec.action_send()
    return env_rec


def test_wet_ink_signature_is_witnessed_scanned_and_in_sequence(w):
    first = w.env["res.partner"].create({"name": "Walk-in Customer"})
    second = w.env["res.partner"].create({"name": "Branch Manager (paper)"})
    envelope = _sent_envelope(w, [first, second])
    s1, s2 = envelope.signer_ids.sorted("sequence")
    out = write(
        w,
        w.clerk2,
        "fix.esignature.wet.signature",
        {
            "envelope_id": envelope.id,
            "signer_id": s2.id,
            "identity_checked": "NID",
            "scan_file": FILE,
        },
    )
    assert "sequential" in out.get("error", ""), out
    no_scan = write(
        w,
        w.clerk2,
        "fix.esignature.wet.signature",
        {"envelope_id": envelope.id, "signer_id": s1.id, "identity_checked": "NID"},
    )
    assert "scan" in no_scan.get("error", "").lower(), no_scan
    res = write(
        w,
        w.clerk2,
        "fix.esignature.wet.signature",
        {
            "envelope_id": envelope.id,
            "signer_id": s1.id,
            "identity_checked": "NID",
            "scan_file": FILE,
        },
    )
    assert "id" in res, res
    wet = w.env["fix.esignature.wet.signature"].browse(res["id"])
    assert (
        wet.witnessed_by_id == w.clerk2 and wet.scan_document_id.document_type == "signature_scan"
    )
    assert (
        s1.signed_at
        and s1.auth_method.startswith("wet_ink_scan")
        and envelope.state == "partially_signed"
    )
    assert "error" in write(
        w, w.clerk2, "fix.esignature.wet.signature", {"note": "edited"}, record_id=wet.id
    )


def test_a_signer_cannot_witness_their_own_wet_signature(w):
    envelope = _sent_envelope(w, [w.clerk2.partner_id])
    with pytest.raises(UserError, match="someone other than the signer"):
        w.env["fix.esignature.wet.signature"].with_user(w.clerk2).create(
            {
                "envelope_id": envelope.id,
                "signer_id": envelope.signer_ids.id,
                "identity_checked": "NID",
                "scan_file": FILE,
            }
        )


def test_a_qualified_class_refuses_session_and_wet_signatures(w):
    cls = _class(w, doc_type="contract", signature_assurance_level="qualified", need_link=False)
    cls.with_user(w.controller).action_activate()
    envelope = _sent_envelope(w, [w.clerk2.partner_id], doc=_doc(w, document_type="contract"))
    assert envelope.assurance_level == "qualified"
    with pytest.raises(UserError, match="qualified"):
        envelope.signer_ids.with_user(w.clerk2).action_sign()
    with pytest.raises(UserError, match="qualified"):
        w.env["fix.esignature.wet.signature"].with_user(w.clerk).create(
            {
                "envelope_id": envelope.id,
                "signer_id": envelope.signer_ids.id,
                "identity_checked": "NID",
                "scan_file": FILE,
            }
        )


def test_a_completed_envelope_verifies_and_a_broken_certificate_is_caught(w):
    envelope = _sent_envelope(w, [w.clerk2.partner_id])
    envelope.signer_ids.with_user(w.clerk2).action_sign()
    envelope.with_user(w.clerk).action_check_complete()
    assert act(w, w.clerk2, "fix.esignature.envelope", envelope.ids, "action_verify").get("success")
    assert envelope.verification_result == "intact" and envelope.verified_by_id == w.clerk2
    envelope.completion_certificate_id.attachment_id.sudo().write(
        {"datas": base64.b64encode(b"{}")}
    )
    envelope.action_verify()
    assert envelope.verification_result == "broken" and "sealed hash" in envelope.verification_note


# ============================================================= deployment
def test_the_wiring_exists(w):
    env = w.env
    for xmlid in (
        "cd_document_core.ir_cron_physical_destruction_due",
        "cd_document_core.ir_cron_integrity_sweep",
        "cd_document_core.ir_cron_retention_violation_scan",
        "cd_document_core.ir_cron_external_release_expiry",
    ):
        assert env.ref(xmlid).active, xmlid
    assert env.ref(APPROVER)
    from odoo.addons.cd_p03_portal.controllers.a10 import m24, writable

    for model in (
        "fix.document.class",
        "fix.document.exception",
        "fix.physical.record",
        "fix.document.integrity.check",
        "fix.document.distribution",
        "fix.document.acknowledgement",
        "fix.disposal.batch",
        "fix.retention.violation",
        "fix.legal.hold.order",
        "fix.evidence.pack",
        "fix.external.release",
        "fix.document.access.log",
        "fix.esignature.wet.signature",
    ):
        assert model in m24.SURFACES, model
        assert model in writable.WRITABLE, model
        for method in m24.SURFACES[model]["actions"]:
            assert hasattr(env[model], method), (model, method)
    # no workflow field is writable through a form
    assert not {"state", "approved_by_id", "access_token"} & set(
        writable.WRITABLE["fix.external.release"]
    )
    assert not {"state", "document_ids", "approved_by_id"} & set(
        writable.WRITABLE["fix.disposal.batch"]
    )
