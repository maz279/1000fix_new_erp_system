"""M12 seller stock positions and seller standards / certifications.

The M12-stock and M12-training reports were declared gaps: no model tied
stock to a seller (a listing carries no SKU or quantity) and training and
certification were keyed to staff (hr.employee) only. These are the two
records that close them, exercised as the roles that use them:

  * fix.seller.stock - a seller's position per listing and SKU (on hand,
    reserved), reported by the seller (portal), by an operator or by an
    import. Who reported it, when and how are stamped by the server.
  * fix.seller.standard / fix.seller.certification - the standards and
    courses a seller must hold (mapped to the service categories that
    require them) and the seller's evidence of holding one, verified by a
    Marketplace Compliance Reviewer who did not submit it, expiring on its
    date.
"""

import base64
import types
from contextlib import contextmanager
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
GUARD = "changes only through its workflow"
OPERATOR = "cd_marketplace.group_marketplace_operator"
COMPLIANCE = "cd_marketplace.group_marketplace_compliance"
SELLER_PORTAL = "cd_marketplace.group_fix_marketplace_seller"
STOCK, STANDARD, CERT = "fix.seller.stock", "fix.seller.standard", "fix.seller.certification"


@contextmanager
def _refused(env, exc=REFUSED, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def sm(odoo_env):
    env = odoo_env
    users = env["res.users"].with_context(no_reset_password=True)

    def user(login, *groups):
        return users.create(
            {
                "name": login.replace("_", " ").title(),
                "login": login,
                "group_ids": [Command.set([env.ref(g).id for g in groups])],
            }
        )

    x = types.SimpleNamespace(env=env)
    x.plain = user("sm_plain", "base.group_user")
    x.operator = user("sm_operator", "base.group_user", OPERATOR)
    x.compliance = user("sm_compliance", "base.group_user", COMPLIANCE)
    x.compliance2 = user("sm_compliance_two", "base.group_user", COMPLIANCE)
    x.seller_user = user("sm_seller", SELLER_PORTAL)
    x.other_seller_user = user("sm_seller_two", SELLER_PORTAL)
    x.category = env["product.category"].create({"name": "SM Screen Repair"})
    x.seller = env["fix.marketplace.seller"].create(
        {
            "name": "SM Shop",
            "partner_id": x.seller_user.partner_id.id,
            "category_ids": [Command.set(x.category.ids)],
        }
    )
    x.other_seller = env["fix.marketplace.seller"].create(
        {"name": "SM Other Shop", "partner_id": x.other_seller_user.partner_id.id}
    )
    x.listing = env["fix.marketplace.listing"].create(
        {"name": "SM Screen Swap", "seller_id": x.seller.id, "category_id": x.category.id}
    )
    x.other_listing = env["fix.marketplace.listing"].create(
        {"name": "SM Other Swap", "seller_id": x.other_seller.id}
    )
    x.standard = env[STANDARD].create(
        {
            "name": "SM Display Handling",
            "code": "SM-DH",
            "validity_months": 12,
            "category_ids": [Command.set(x.category.ids)],
        }
    )
    x.today = fields.Date.context_today(env["fix.seller.certification"])
    return x


def _doc(x, record, user=None):
    return (
        x.env["ir.attachment"]
        .with_user(user or x.operator)
        .create(
            {
                "name": "certificate.pdf",
                "res_model": record._name,
                "res_id": record.id,
                "datas": base64.b64encode(b"%PDF-1.4 seller certificate"),
            }
        )
    )


# ---------------------------------------------------------------- stock


def test_an_operator_reports_a_position_and_the_server_stamps_it(sm):
    pos = (
        sm.env[STOCK]
        .with_user(sm.operator)
        .create(
            {"listing_id": sm.listing.id, "sku": "SM-LCD-A12", "qty_on_hand": 10, "qty_reserved": 3}
        )
    )
    assert pos.seller_id == sm.seller  # the listing's seller, never typed
    assert pos.qty_available == 7.0
    assert pos.source == "operator"
    assert pos.updated_by_id == sm.operator
    assert pos.last_updated
    assert pos.company_id == sm.listing.company_id


def test_a_plain_user_reads_stock_but_does_not_report_it(sm):
    pos = sm.env[STOCK].create({"listing_id": sm.listing.id, "sku": "SM-1", "qty_on_hand": 1})
    assert pos.with_user(sm.plain).sku == "SM-1"
    with _refused(sm.env, AccessError):
        sm.env[STOCK].with_user(sm.plain).create(
            {"listing_id": sm.listing.id, "sku": "SM-2", "qty_on_hand": 1}
        )


def test_the_stamp_is_not_typed(sm):
    pos = (
        sm.env[STOCK]
        .with_user(sm.operator)
        .create({"listing_id": sm.listing.id, "sku": "SM-3", "qty_on_hand": 4})
    )
    for vals in ({"source": "import"}, {"updated_by_id": sm.plain.id}):
        with _refused(sm.env, UserError, GUARD):
            pos.with_user(sm.operator).write(vals)
    with _refused(sm.env, UserError, GUARD):
        sm.env[STOCK].with_user(sm.operator).create(
            {"listing_id": sm.listing.id, "sku": "SM-4", "qty_on_hand": 1, "source": "import"}
        )


def test_a_quantity_change_restamps_and_a_note_does_not(sm):
    pos = (
        sm.env[STOCK]
        .with_user(sm.operator)
        .create({"listing_id": sm.listing.id, "sku": "SM-5", "qty_on_hand": 4})
    )
    old = fields.Datetime.now() - timedelta(days=40)
    sm.env.flush_all()
    sm.env.cr.execute("UPDATE fix_seller_stock SET last_updated=%s WHERE id=%s", [old, pos.id])
    pos.invalidate_recordset()
    pos.with_user(sm.operator).write({"note": "shelf B"})
    assert pos.last_updated == old
    other_operator = (
        sm.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "SM Operator Two",
                "login": "sm_operator_two",
                "group_ids": [Command.set([sm.env.ref(OPERATOR).id])],
            }
        )
    )
    pos.with_user(other_operator).write({"qty_on_hand": 6})
    assert pos.last_updated > old
    assert pos.updated_by_id == other_operator


def test_quantities_are_sane_and_one_position_per_listing_and_sku(sm):
    make = sm.env[STOCK].with_user(sm.operator).create
    with _refused(sm.env, ValidationError, "negative"):
        make({"listing_id": sm.listing.id, "sku": "SM-6", "qty_on_hand": -1})
    with _refused(sm.env, ValidationError, "reserved"):
        make({"listing_id": sm.listing.id, "sku": "SM-6", "qty_on_hand": 2, "qty_reserved": 3})
    make({"listing_id": sm.listing.id, "sku": "SM-6", "qty_on_hand": 2})
    with _refused(sm.env, ValidationError, "already"):
        make({"listing_id": sm.listing.id, "sku": " SM-6 ", "qty_on_hand": 5})


def test_a_removed_listing_takes_no_stock(sm):
    sm.listing.with_user(sm.operator).action_remove()
    with _refused(sm.env, ValidationError, "removed"):
        sm.env[STOCK].with_user(sm.operator).create(
            {"listing_id": sm.listing.id, "sku": "SM-7", "qty_on_hand": 1}
        )


def test_the_seller_reports_own_stock_and_sees_only_their_own(sm):
    model = sm.env[STOCK].with_user(sm.seller_user)
    pos = model.report_position(sm.listing.id, "SM-8", 12, 2)
    assert pos.source == "seller" and pos.updated_by_id == sm.seller_user
    assert pos.qty_available == 10.0
    again = model.report_position(sm.listing.id, "SM-8", 9)
    assert again == pos and pos.qty_on_hand == 9.0 and pos.qty_reserved == 0.0
    with _refused(sm.env):
        model.report_position(sm.other_listing.id, "SM-9", 1)
    theirs = sm.env[STOCK].create({"listing_id": sm.other_listing.id, "sku": "SM-10"})
    assert theirs not in model.search([])
    assert pos in model.search([])


def test_an_import_upserts_positions_stamped_as_imported(sm):
    model = sm.env[STOCK].with_user(sm.operator)
    out = model.import_positions(
        [
            {"listing_id": sm.listing.id, "sku": "SM-11", "qty_on_hand": 5, "qty_reserved": 1},
            {"listing_id": sm.listing.id, "sku": "SM-12", "qty_on_hand": 0},
        ]
    )
    assert out == {"created": 2, "updated": 0}
    out = model.import_positions([{"listing_id": sm.listing.id, "sku": "SM-11", "qty_on_hand": 7}])
    assert out == {"created": 0, "updated": 1}
    rows = model.search([("listing_id", "=", sm.listing.id), ("sku", "in", ("SM-11", "SM-12"))])
    assert set(rows.mapped("source")) == {"import"}
    assert rows.filtered(lambda r: r.sku == "SM-11").qty_on_hand == 7.0
    # Odoo's own import (load) is an import too
    res = model.load(["listing_id/.id", "sku", "qty_on_hand"], [[str(sm.listing.id), "SM-13", "3"]])
    assert not [m for m in res["messages"] if m.get("type") == "error"], res["messages"]
    assert model.browse(res["ids"]).source == "import"


def test_the_listing_shows_its_stock(sm):
    pos = sm.env[STOCK].create({"listing_id": sm.listing.id, "sku": "SM-14", "qty_on_hand": 1})
    assert pos in sm.listing.stock_ids


# ---------------------------------------------------------------- standards


def _cert(sm, standard=None, user=None, **vals):
    return (
        sm.env[CERT]
        .with_user(user or sm.operator)
        .create(
            {
                "seller_id": sm.seller.id,
                "standard_id": (standard or sm.standard).id,
                "issued_on": sm.today - timedelta(days=10),
                "certificate_no": "SM-CERT-1",
                **vals,
            }
        )
    )


def _submitted(sm, **vals):
    cert = _cert(sm, **vals)
    cert.with_user(sm.operator).write({"evidence_attachment_id": _doc(sm, cert).id})
    cert.with_user(sm.operator).action_submit()
    return cert


def test_the_standard_maps_to_the_categories_that_require_it(sm):
    assert sm.standard in sm.env[STANDARD].search([("category_ids", "in", sm.category.ids)])
    with _refused(sm.env, AccessError):
        sm.env[STANDARD].with_user(sm.operator).create({"name": "X", "code": "SM-X"})
    sm.env[STANDARD].with_user(sm.compliance).create({"name": "Y", "code": "SM-Y"})


def test_expiry_defaults_from_the_standard_validity(sm):
    cert = _cert(sm)
    assert cert.expires_on == fields.Date.add(cert.issued_on, months=12)
    lifetime = sm.env[STANDARD].create({"name": "Life", "code": "SM-LIFE", "validity_months": 0})
    assert not _cert(sm, standard=lifetime).expires_on


def test_a_certificate_is_submitted_with_evidence_and_verified_by_another_reviewer(sm):
    cert = _cert(sm)
    with _refused(sm.env, UserError, "evidence"):
        cert.with_user(sm.operator).action_submit()
    cert.with_user(sm.operator).write({"evidence_attachment_id": _doc(sm, cert).id})
    cert.with_user(sm.compliance).action_submit()
    assert cert.state == "submitted" and cert.submitted_by_id == sm.compliance
    with _refused(sm.env, UserError, "Segregation"):
        cert.with_user(sm.compliance).action_verify()
    with _refused(sm.env, AccessError):
        cert.with_user(sm.operator).action_verify()
    cert.with_user(sm.compliance2).action_verify()
    assert cert.state == "verified" and cert.verified_by_id == sm.compliance2
    assert cert.verified_at


def test_the_seller_does_not_verify_their_own_certificate(sm):
    """A reviewer who also acts for the seller (their party's user)."""
    own = sm.env["fix.marketplace.seller"].create(
        {"name": "SM Reviewer's Shop", "partner_id": sm.compliance2.partner_id.id}
    )
    cert = _submitted(sm, seller_id=own.id)
    with _refused(sm.env, UserError, "Segregation"):
        cert.with_user(sm.compliance2).action_verify()
    cert.with_user(sm.compliance).action_verify()
    assert cert.state == "verified"


def test_state_and_verifier_are_not_typed(sm):
    cert = _submitted(sm)
    for vals in ({"state": "verified"}, {"verified_by_id": sm.compliance.id}):
        with _refused(sm.env, UserError, GUARD):
            cert.with_user(sm.compliance).write(vals)


def test_the_evidence_is_pinned_once_submitted(sm):
    cert = _submitted(sm)
    with _refused(sm.env, UserError):
        cert.with_user(sm.operator).write({"expires_on": sm.today + timedelta(days=900)})
    assert {"issued_on", "expires_on", "evidence_attachment_id"} <= cert._fix_form_locked_fields()


def test_reject_needs_a_reason_and_a_rejected_one_is_resubmitted(sm):
    cert = _submitted(sm)
    with _refused(sm.env, UserError, "reason"):
        cert.with_user(sm.compliance).action_reject(reason="")
    cert.with_user(sm.compliance).action_reject(reason="Scan unreadable")
    assert cert.state == "rejected" and "unreadable" in cert.decision_note
    cert.with_user(sm.operator).write({"certificate_no": "SM-CERT-2"})
    cert.with_user(sm.operator).action_submit()
    assert cert.state == "submitted"


def test_a_verified_certificate_is_revoked_with_a_reason(sm):
    cert = _submitted(sm)
    cert.with_user(sm.compliance).action_verify()
    cert.with_user(sm.compliance).action_revoke(reason="Issuer withdrew it")
    assert cert.state == "revoked"


def test_an_expired_certificate_is_not_verified_and_the_cron_expires_the_rest(sm):
    late = _submitted(sm)
    sm.env.flush_all()
    sm.env.cr.execute(
        "UPDATE fix_seller_certification SET expires_on=%s WHERE id=%s",
        [sm.today - timedelta(days=1), late.id],
    )
    late.invalidate_recordset()
    with _refused(sm.env, UserError, "expired"):
        late.with_user(sm.compliance).action_verify()

    live = _submitted(sm, certificate_no="SM-CERT-3")
    live.with_user(sm.compliance).action_verify()
    assert live.expiry_status == "valid"
    sm.env.flush_all()
    sm.env.cr.execute(
        "UPDATE fix_seller_certification SET expires_on=%s WHERE id=%s",
        [sm.today + timedelta(days=5), live.id],
    )
    live.invalidate_recordset()
    assert live.expiry_status == "expiring" and live.days_to_expiry == 5
    sm.env.cr.execute(
        "UPDATE fix_seller_certification SET expires_on=%s WHERE id=%s",
        [sm.today - timedelta(days=2), live.id],
    )
    live.invalidate_recordset()
    sm.env[CERT].cron_expire_certifications()
    assert live.state == "expired"


def test_the_seller_reads_only_their_own_certificates(sm):
    mine = _cert(sm)
    theirs = _cert(sm, seller_id=sm.other_seller.id, certificate_no="SM-OTHER")
    visible = sm.env[CERT].with_user(sm.seller_user).search([])
    assert mine in visible and theirs not in visible
    with _refused(sm.env, AccessError):
        mine.with_user(sm.seller_user).write({"certificate_no": "SELF"})


def test_the_seller_shows_its_certificates(sm):
    cert = _cert(sm)
    assert cert in sm.seller.certification_ids
    assert cert.with_user(sm.plain).standard_id == sm.standard  # internal users read
