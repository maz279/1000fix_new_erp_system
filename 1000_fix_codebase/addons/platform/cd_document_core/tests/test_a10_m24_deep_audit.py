# A10 deep audit (2026-11-22) — M24 fixes landed from the five-auditor sweep:
#
# A2-F03  the confidentiality tier read rule: a T3/T5 document is readable
#         only by users whose ACTIVE roles are granted the tier in the M29
#         register; T0/T1 and unclassified stay internal-readable.
# A2-F04  disposal seals the destroyed payload's sha256 + byte count on the
#         register, the single certificate and the batch manifest BEFORE the
#         wipe — the surviving row's checksum recomputes to False.
#
# The odoo_env fixture is a superuser environment; the tier rule is therefore
# exercised through a real non-admin reader.
import base64
import hashlib

import pytest
from odoo.addons.cd_document_core.models.fix_document_capture import (  # pass 2: disposal
    _BATCH_TOKEN,
    BATCH_KEY,
)
from odoo.exceptions import AccessError, UserError


def _attach(env, raw=b"deep audit payload", **kw):
    return env["fix.document"].attach(
        name=kw.pop("name", "DA Report.pdf"),
        datas=base64.b64encode(raw),
        document_type=kw.pop("document_type", "service_report"),
        **kw,
    )


def _via_batch(rec):
    return rec.with_context(**{BATCH_KEY: _BATCH_TOKEN})


def _reader(env, n):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 DA reader %d" % n,
                "login": "a10da.reader.%d@a10.test" % n,
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )


# --------------------------------------------- A2-F03: the tier read rule
def test_a_t3_document_is_readable_only_through_a_granted_role(odoo_env):
    env = odoo_env
    plain = _reader(env, 1)
    # an internal doc (no tier) and a role-scoped doc
    internal = _attach(env, name="DA Internal")
    scoped = _attach(env, name="DA Scoped")
    env.cr.flush()
    scoped._guarded().write({"isolation_tier": "T3"})
    env.cr.flush()

    # the plain internal user sees the unclassified document, not the T3 one
    visible = env["fix.document"].with_user(plain).search([("name", "like", "DA ")])
    assert internal in visible
    assert scoped not in visible
    with pytest.raises(AccessError):
        env["fix.document"].with_user(plain).browse(scoped.ids).read(["name"])

    # a role granted T3 in the M29 register widens exactly that
    Tier = env["fix.isolation.tier"].sudo()
    role = env["fix.role"].sudo().create({"name": "DA T3 role", "code": "R-91"})
    t3 = Tier.search([("code", "=", "T3")], limit=1)
    t3.write({"role_ids": [(4, role.id)]})
    env["fix.role.assignment"].sudo().create(
        {"user_id": plain.id, "role_id": role.id, "source": "a10 deep audit test"}
    )
    # the tier compute caches per environment: a grant made in this same
    # transaction needs the cache dropped before the rule re-evaluates (in
    # production the grant is its own request, so the next request computes
    # fresh)
    plain.invalidate_recordset()
    visible = env["fix.document"].with_user(plain).search([("name", "like", "DA ")])
    assert internal in visible and scoped in visible
    # the lifecycle officers read across tiers by design (the register
    # governs what they may DO with a classified document, not whether the
    # row exists for them)
    officer = _reader(env, 2)
    officer.write({"group_ids": [(4, env.ref("cd_document_core.group_document_records").id)]})
    visible = env["fix.document"].with_user(officer).search([("name", "like", "DA ")])
    assert internal in visible and scoped in visible

    # the reader's tier codes are register-driven, never typed (a write to
    # the non-stored compute is discarded by the ORM — the value stays)
    plain.invalidate_recordset()
    assert "T3" in (plain.fix_document_tier_codes or "").split(",")
    plain.write({"fix_document_tier_codes": "T4,T5"})
    plain.invalidate_recordset()
    assert "T4" not in (plain.fix_document_tier_codes or "").split(",")


# --------------------------------------------- A2-F04: the sealed disposal
def test_disposal_seals_the_destroyed_payload_hash(odoo_env):
    env = odoo_env
    raw = b"the bytes that will be destroyed"
    doc = _attach(env, raw=raw, name="DA Sealed")
    env.cr.flush()
    doc.write({"state": "expired"})
    expected_hash = hashlib.sha256(raw).hexdigest()

    assert _via_batch(doc).action_dispose() is True

    (register,) = env["fix.disposal.record"].search([("document_id", "=", doc.id)])
    # the register seals the fingerprint of exactly what was wiped
    assert register.payload_sha256 == expected_hash
    assert register.payload_size == len(raw)
    # the certificate states it too
    certificate = register.certificate_doc_id
    cert_bytes = base64.b64decode(certificate.attachment_id.sudo().datas or "")
    assert expected_hash in cert_bytes.decode("utf-8")
    assert ("%d bytes" % len(raw)) in cert_bytes.decode("utf-8")
    # while the surviving row's own checksum is gone with the bytes
    assert not doc.attachment_id.datas
    # the seal is the disposal's, not a typed value
    with pytest.raises(UserError), env.cr.savepoint():
        register.with_user(env.ref("base.user_admin")).write({"payload_sha256": "0" * 64})
