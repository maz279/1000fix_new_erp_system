# A10 remediation (2026-11-05), D2 + P1-1: legal hold & disposal authority,
# retention enforcement, Mayan honesty and the controlled-document workflow.
#
# Every control is exercised as NON-ADMIN users holding only the role groups
# each step needs (the superuser is trusted by the field guard and would hide
# a gap). Each control is attacked three ways where it applies: the wrong
# role, a plain write() (the JSON-RPC path) and the real P03 endpoints
# (/p03/model/write, /p03/model/action). The legitimate paths run end to end
# through the real actions and the M63 approval inbox. The odoo_env fixture
# rolls back.
import base64
import itertools
import types
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_document_core.models.fix_document_capture import (  # pass 2: disposal
    _BATCH_TOKEN,
    BATCH_KEY,
)
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
)
from odoo.exceptions import AccessError, UserError


def _via_batch(rec):
    """What an approved fix.disposal.batch passes to action_dispose (pass 2,
    19 Nov 2026): a lone action_dispose is refused (FR-DMS-038, SOD-23)."""
    return rec.with_context(**{BATCH_KEY: _BATCH_TOKEN})


RECORDS = "cd_document_core.group_document_records"
CONTROLLER = "cd_document_core.group_document_controller"
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
                "name": "A10 D2 %s %d" % (login, n),
                "login": "a10d2.%s.%d@a10.test" % (login, n),
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
    x.author = _user(env, "author")
    x.controller = _user(env, "controller", [CONTROLLER])
    x.records = _user(env, "records", [RECORDS])
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


def p03(x, endpoint, user=None, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return endpoint(g.P03GenericApiController(), **kw)


def _doc(x, user=None, raw=b"policy bytes", **vals):
    """A document created by `user` (default: the author) over a fixture file."""
    attachment = x.env["ir.attachment"].create({"name": "file", "datas": base64.b64encode(raw)})
    return (
        x.env["fix.document"]
        .with_user(user or x.author)
        .create({"name": "Doc %d" % next(_SEQ), "attachment_id": attachment.id, **vals})
    )


def _expired(x, user=None, **vals):
    doc = _doc(x, user=user, **vals)
    x.env.flush_all()  # let the create land before the raw SQL touches its row
    x.env.cr.execute(
        "UPDATE fix_document SET state = 'expired', retention_expires = %s WHERE id = %s",
        [date.today() - timedelta(days=1), doc.id],
    )
    doc.invalidate_recordset()
    return doc


# ------------------------------------------------------------------ D2: holds
def test_hold_authority_is_records_only_and_needs_the_matter(w):
    doc = _doc(w)
    with pytest.raises(UserError, match="Only a Records Officer"):
        doc.with_user(w.clerk).action_legal_hold("Court order 12/2026")
    with pytest.raises(UserError, match="matter reference"):
        doc.with_user(w.records).action_legal_hold("  ")
    assert not doc.legal_hold

    doc.with_user(w.records).action_legal_hold("Court order 12/2026")
    assert doc.legal_hold and doc.legal_hold_reason == "Court order 12/2026"
    (hold,) = w.env["fix.legal.hold"].search([("document_id", "=", doc.id)])
    assert (hold.state, hold.matter_ref, hold.placed_by_id) == (
        "held",
        "Court order 12/2026",
        w.records,
    )
    # the flag is never typed, on either side (a no-change write passes by
    # design — the form posts every field it shows — so attack with CHANGES)
    for vals in ({"legal_hold": False}, {"legal_hold_reason": "typed"}):
        with pytest.raises(UserError, match=GUARD):
            doc.with_user(w.records).write(vals)
    out = p03(
        w, _MW, user=w.records, model="fix.document", record_id=doc.id, values={"legal_hold": False}
    )
    assert "error" in out and GUARD in out["error"]


def test_hold_freezes_the_file_until_records_releases_it(w):
    doc = _doc(w)
    doc.with_user(w.records).action_legal_hold("Tax inquiry 9/2026")
    # the record's content is frozen…
    with pytest.raises(UserError, match=GUARD):
        doc.with_user(w.records).write({"name": "renamed under hold"})
    out = p03(
        w,
        _MW,
        user=w.author,
        model="fix.document",
        record_id=doc.id,
        values={"description": "rewritten under hold"},
    )
    assert "error" in out
    # …and so is the underlying file: the audit swapped it past the record
    with pytest.raises(UserError, match="e-signature seal"):
        doc.attachment_id.with_user(w.clerk).write(
            {"datas": base64.b64encode(b"swapped under hold")}
        )

    with pytest.raises(UserError, match="Only a Records Officer"):
        doc.with_user(w.clerk).action_release_hold("matter closed")
    with pytest.raises(UserError, match="State why the hold is released"):
        doc.with_user(w.records).action_release_hold(" ")

    doc.with_user(w.records).action_release_hold("Matter closed 3/2026")
    assert not doc.legal_hold
    hold = w.env["fix.legal.hold"].search([("document_id", "=", doc.id)])
    assert (hold.state, hold.release_reason, hold.released_by_id) == (
        "released",
        "Matter closed 3/2026",
        w.records,
    )
    # the file is serviceable again: the seal refusal is gone (a plain-ACL
    # refusal may remain — that is the store's business, not the hold's)
    try:
        doc.attachment_id.with_user(w.records).write(
            {"datas": base64.b64encode(b"new bytes after release")}
        )
    except AccessError:
        pass
    except UserError as exc:
        pytest.fail("the hold's file freeze outlived the hold: %s" % exc)


def test_a_hold_flag_without_its_register_row_is_refused(w):
    # a forged flag (superuser write) with no register row behind it cannot
    # be released through the action: the register is the record
    doc = _doc(w)
    doc.sudo().write({"legal_hold": True, "legal_hold_reason": "typed"})
    with pytest.raises(UserError, match="resolve the register first"):
        doc.with_user(w.records).action_release_hold("cleaning up")


# ------------------------------------------------------------- D2: retention
def test_retention_state_moves_only_through_the_cron(w):
    doc = _doc(w)
    with pytest.raises(UserError, match=GUARD):
        doc.with_user(w.records).write({"state": "expired"})
    out = p03(
        w,
        _MW,
        user=w.records,
        model="fix.document",
        record_id=doc.id,
        values={"state": "destroyed"},
    )
    assert "error" in out and GUARD in out["error"]
    with pytest.raises(UserError, match=GUARD):
        w.env["fix.document"].with_user(w.clerk).create(
            {"name": "Born destroyed", "attachment_id": doc.attachment_id.id, "state": "destroyed"}
        )


def test_disposal_is_records_only_and_records_everything(w):
    doc = _expired(w)
    # pass 2: nobody disposes outside an approved batch, a Records Officer included
    for who in (w.clerk, w.records):
        with pytest.raises(UserError, match="Disposal Batch"):
            doc.with_user(who).action_dispose()
    out = p03(w, _MA, user=w.records, model="fix.document", ids=doc.ids, method="action_dispose")
    assert out.get("success") is False
    # inside a batch the Records-only rule still holds
    with pytest.raises(UserError, match="Only a Records Officer"):
        _via_batch(doc.with_user(w.clerk)).action_dispose()

    _via_batch(doc.with_user(w.records)).action_dispose("physical_shredding")
    (register,) = w.env["fix.disposal.record"].sudo().search([("document_id", "=", doc.id)])
    assert register.method == "physical_shredding"
    assert register.performed_by_id == w.records
    assert register.certificate_doc_id.document_type == "destruction_certificate"
    assert not doc.attachment_id.datas
    assert (doc.state, doc.active) == ("destroyed", False)
    # the register is permanent, and the destroyed row anchors it
    with pytest.raises(UserError, match="permanent"):
        register.with_user(w.records).unlink()
    with pytest.raises(UserError, match="anchors the permanent disposal register"):
        doc.with_user(w.records).unlink()

    held = _expired(w, name="Held expiry")
    held.with_user(w.records).action_legal_hold("Litigation 44/2026")
    with pytest.raises(UserError, match="strictly blocked"):
        _via_batch(held.with_user(w.records)).action_dispose()
    assert held.state == "expired"  # untouched


def test_mayan_sync_never_claims_an_endpoint_it_does_not_have(w):
    doc = _doc(w)
    w.env["ir.config_parameter"].search(
        [("key", "in", ("mayan_edms.base_url", "mayan_edms.token"))]
    ).unlink()
    out = p03(
        w, _MA, user=w.clerk, model="fix.document", ids=doc.ids, method="action_sync_to_mayan"
    )
    assert out.get("success") is False
    assert doc.mayan_sync_status == "not_synced" and not doc.mayan_document_id
    # and the fingerprint is derived, never typed
    with pytest.raises(UserError, match=GUARD):
        doc.with_user(w.records).write({"mayan_sync_status": "synced"})


# ------------------------------------------------- P1-1: controlled documents
def test_controlled_documents_are_born_draft_and_move_via_actions(w):
    attachment = w.env["ir.attachment"].create(
        {"name": "f", "datas": base64.b64encode(b"procedure")}
    )
    with pytest.raises(UserError, match=GUARD):
        w.env["fix.document"].with_user(w.author).create(
            {
                "name": "Born published",
                "attachment_id": attachment.id,
                "is_controlled": True,
                "control_state": "published",
            }
        )
    doc = _doc(w, is_controlled=True, document_type="other")
    assert (doc.control_state, doc.is_current) == ("draft", True)
    with pytest.raises(UserError, match="Publishing follows approval"):
        doc.with_user(w.controller).action_publish()
    with pytest.raises(UserError, match=GUARD):
        doc.with_user(w.controller).write({"control_state": "approved"})


def test_controlled_review_routes_to_a_controller_who_is_not_the_author(w):
    doc = _doc(w, user=w.author, is_controlled=True, name="SOP-1 Bench repair")
    doc.with_user(w.author).action_submit_review("Annual review")
    assert doc.control_state == "in_review" and doc.approval_state == "pending"
    routed = assigned(doc)
    assert w.controller in routed and w.author not in routed  # M63 never routes to the author

    # the approve method is the engine's to call — not a button to press
    with pytest.raises(UserError, match="approved from the approver's inbox"):
        doc.with_user(w.controller).action_approve()

    task = approve_via_inbox(doc, w.controller, comment="Reviewed with Legal")
    assert task and task.res_id == doc.id
    assert doc.control_state == "approved"
    assert doc.approved_by_id == w.controller and doc.approved_on == fields.Date.context_today(doc)
    assert doc.approval_state == "approved"

    doc.with_user(w.author).action_publish()
    assert (doc.control_state, doc.is_current, doc.published_on) == (
        "published",
        True,
        fields.Date.context_today(doc),
    )
    # a published controlled version freezes its content AND its version
    # fields: currency and lineage move only through the workflow (M24-5/-9)
    for vals in ({"name": "SOP-1 renamed"}, {"is_current": False}, {"version": "9.9"}):
        with pytest.raises(UserError, match=GUARD):
            doc.with_user(w.author).write(vals)


def test_publishing_a_revision_supersedes_the_previous_version(w):
    v1 = _doc(w, user=w.author, is_controlled=True, name="SOP-2 Calibration", version="1.0")
    v1.with_user(w.author).action_submit_review("initial issue")
    approve_via_inbox(v1, w.controller)
    v1.with_user(w.author).action_publish()

    v2 = v1.with_user(w.author).action_new_revision()
    assert isinstance(v2, dict) and v2["reporter"] == "Draft created"
    (draft,) = w.env["fix.document"].search(
        [("name", "=", "SOP-2 Calibration"), ("control_state", "=", "draft")]
    )
    assert draft.previous_version_id == v1 and draft.version == "1.1"
    assert not draft.is_current  # the published version stays THE current one
    assert v1.control_state == "published" and v1.is_current

    draft.with_user(w.author).action_submit_review("tolerance update")
    approve_via_inbox(draft, w.controller)
    draft.with_user(w.author).action_publish()
    v1.invalidate_recordset()
    assert (v1.control_state, v1.is_current, v1.superseded_by_id) == (
        "superseded",
        False,
        draft,
    )
    assert (draft.control_state, draft.is_current) == ("published", True)


def test_p03_document_actions_run_the_real_journeys(w):
    doc = _doc(w, is_controlled=True, name="SOP-3 Via P03")
    out = p03(
        w,
        _MA,
        user=w.author,
        model="fix.document",
        ids=doc.ids,
        method="action_submit_review",
        kwargs={"justification": "from the workspace"},
    )
    assert out.get("success") is True and doc.control_state == "in_review"
    approve_via_inbox(doc, w.controller)
    out = p03(w, _MA, user=w.author, model="fix.document", ids=doc.ids, method="action_publish")
    assert out.get("success") is True and doc.control_state == "published"

    plain = _doc(w, name="Operational via P03")
    out = p03(
        w,
        _MA,
        user=w.records,
        model="fix.document",
        ids=plain.ids,
        method="action_legal_hold",
        kwargs={"matter_ref": "Notice 7/2026"},
    )
    assert out.get("success") is True and plain.legal_hold
    out = p03(
        w,
        _MA,
        user=w.records,
        model="fix.legal.hold",
        ids=w.env["fix.legal.hold"].sudo().search([("document_id", "=", plain.id)]).ids,
        method="action_release",
        kwargs={"reason": "notice withdrawn"},
    )
    plain.invalidate_recordset()  # the action ran in another env's cache
    assert out.get("success") is True and not plain.legal_hold
