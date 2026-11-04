"""A02 P1 for M17 warranties (cd_device_registry), as NON-ADMIN users.

B1: warranty verification is a routed M63 approval. Pressed directly, even by
a Warranty Officer, Verify is refused; the registrar requests it and an
officer who did not register the cover verifies it from the inbox.
B4: a daily cron expires cover past its end date (nothing wrote 'expired').
"""

import itertools
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_device_registry.group_warranty_officer"
_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %d" % (login, n),
                "login": "a02p1m17.%s.%d@a02.test" % (login, n),
                "group_ids": [(6, 0, ids)],
            }
        )
    )


def _refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc)
    return None


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    brand = env["fix.brand"].create({"name": "A2P1 Brand", "code": "A2P1W"})
    model = env["fix.device.model"].create({"name": "A2P1 Phone", "brand_id": brand.id})
    owner = env["res.partner"].create({"name": "A2P1 Owner"})
    x = types.SimpleNamespace(env=env, n=0)
    x.registrar = _user(env, "registrar", [OFFICER])
    x.officer = _user(env, "officer", [OFFICER])
    x.clerk = _user(env, "clerk")

    def proof():
        # one receipt per warranty: A07 M17-13 files a proof against the
        # warranty it verified, so the same paper cannot prove a second one
        att = env["ir.attachment"].create({"name": "receipt.pdf", "datas": b"JVBERg=="})
        return env["fix.document"].create({"name": "Purchase receipt", "attachment_id": att.id})

    x.proof = proof

    def device():
        x.n += 1
        return env["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": owner.id,
                "serial_number": "A2P1W-SN-%03d" % x.n,
            }
        )

    x.device = device
    return x


def _warranty(m, user, **kw):
    today = fields.Date.context_today(m.env["fix.warranty"])
    vals = {
        "device_id": m.device().id,
        "start_date": today - timedelta(days=10),
        "end_date": today + timedelta(days=355),
        "proof_document_id": m.proof().id,
    }
    vals.update(kw)
    return m.env["fix.warranty"].with_user(user).create(vals)


def test_verification_is_decided_from_the_officers_inbox(m):
    wty = _warranty(m, m.registrar)
    assert "approver's inbox" in _refused(m.env, lambda: wty.with_user(m.officer).action_verify())
    wty.with_user(m.registrar).action_request_approval(justification="Receipt attached")
    assert m.officer in assigned(wty) and m.registrar not in assigned(wty)
    assert not inbox_task(wty, m.registrar)
    approve_via_inbox(wty, m.officer, requester=m.registrar)
    assert (wty.status, wty.verified_by, wty.approval_state) == ("active", m.officer, "approved")


def test_verification_still_needs_proof_and_an_officer(m):
    wty = _warranty(m, m.clerk, proof_document_id=False)
    wty.with_user(m.clerk).action_request_approval(justification="Card to follow")
    assert "before verifying" in _refused(
        m.env, lambda: approve_via_inbox(wty, m.officer, requester=m.clerk)
    )
    assert wty.status == "pending"
    # verified cover needs no further approval
    done = _warranty(m, m.registrar)
    approve_via_inbox(done, m.officer, requester=m.registrar)
    assert "needs no approval" in _refused(
        m.env, lambda: done.with_user(m.registrar).action_request_approval()
    )


def test_expiry_cron_expires_only_cover_past_its_end(m):
    today = fields.Date.context_today(m.env["fix.warranty"])
    past = _warranty(
        m, m.registrar, start_date=today - timedelta(days=400), end_date=today - timedelta(days=1)
    )
    approve_via_inbox(past, m.officer, requester=m.registrar)
    pending_past = _warranty(
        m, m.clerk, start_date=today - timedelta(days=400), end_date=today - timedelta(days=5)
    )
    live = _warranty(m, m.registrar)
    approve_via_inbox(live, m.officer, requester=m.registrar)
    assert m.env["fix.warranty"]._cron_expire_warranties() >= 2
    assert (past.status, pending_past.status, live.status) == ("expired", "expired", "active")
    assert "frozen" in _refused(
        m.env,
        lambda: past.with_user(m.registrar).write({"end_date": today + timedelta(days=300)}),
    )


def test_expiry_cron_is_scheduled(m):
    cron = m.env.ref("cd_device_registry.ir_cron_warranty_expiry")
    assert cron.active and "_cron_expire_warranties" in cron.code
