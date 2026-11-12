# M16 local supplier proforma and advance (user request, 12 Nov 2026): a local
# supplier's proforma invoice is recorded against its purchase order and
# approved by someone else when it reconciles; an advance against it is
# requested by a Buyer and approved by someone else, within the proforma and
# the advance cap. Every case runs as a NON-ADMIN user created in the
# rolled-back transaction, the way the M16 control suite does.
import types
from datetime import date, timedelta

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GB = "cd_requisition.group_fix_procurement_buyer"
GA = "cd_requisition.group_fix_procurement_approver"
T = {n: "cd_entity_config.group_dofa_tier_%d" % n for n in range(1, 6)}
APPROVER_BY_TIER = {"tier_2": "t2", "tier_3": "t3", "tier_4": "cfo", "tier_5": "md"}
SOON = date.today() + timedelta(days=14)


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def _active_supplier(env, partner):
    sup = env["fix.supplier"].create(
        {"name": partner.name, "partner_id": partner.id, "status": "active"}
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {
                "supplier_id": sup.id,
                "doc_type": doc_type,
                "number": "SPI-%s" % doc_type,
                "file_ref": "dms://spi/%s" % doc_type,
                "state": "valid",
                "valid_to": date.today() + timedelta(days=365),
            }
        )
    return sup


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.requester = _user(env, "spi_requester")
    x.clerk = _user(env, "spi_clerk")
    x.buyer = _user(env, "spi_buyer", [GB])
    x.buyer_approver = _user(env, "spi_buyer_approver", [GB, GA])
    x.approver = _user(env, "spi_approver", [GA])
    x.t2 = _user(env, "spi_t2", [T[2]])
    x.t3 = _user(env, "spi_t3", [T[3]])
    x.cfo = _user(env, "spi_cfo", [T[4]])
    x.md = _user(env, "spi_md", [T[5]])
    x.emp = env["hr.employee"].create({"name": "SPI Requester", "user_id": x.requester.id})
    x.prod = env["product.product"].create({"name": "SPI Compressor"})
    x.vendor = env["res.partner"].create({"name": "SPI Local Supplier Ltd", "is_company": True})
    _active_supplier(env, x.vendor)
    return x


def _decide(record, c):
    approver = getattr(c, APPROVER_BY_TIER[record._dofa_current_tier()])
    task = record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "no inbox task for %s" % approver.login
    task.with_user(approver).action_approve(comment="ok")


def _po(c, send=True, amount=20000.0):
    req = (
        c.env["fix.requisition"]
        .with_user(c.requester)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "requested_by": c.emp.id,
                "description": "SPI requisition",
                "justification": "Local purchase of compressors",
                "estimate_amount": amount,
                "product_id": c.prod.id,
                "qty": 2,
                "vendor_id": c.vendor.id,
                "cost_centre": "CC-SPI",
                "required_by": SOON,
            }
        )
    )
    req.with_user(c.requester).action_submit()
    _decide(req, c)
    req.with_user(c.buyer).action_convert_to_po()
    po = req.purchase_order_id
    po.with_user(c.buyer).action_submit_for_approval()
    _decide(po, c)
    if send:
        po.with_user(c.buyer).action_send()
        assert po.state == "sent"
    return po


def _proforma(c, po, amount=None, user=None, **kw):
    vals = {
        "purchase_order_id": po.id,
        "proforma_no": kw.pop("proforma_no", "PI-%s" % po.id),
        "amount": po.amount_total if amount is None else amount,
        "valid_until": SOON,
        "payment_terms": "50% advance, balance on delivery",
    }
    vals.update(kw)
    return c.env["fix.purchase.proforma"].with_user(user or c.buyer).create(vals)


def _approved_proforma(c, po=None):
    po = po or _po(c)
    pi = _proforma(c, po)
    pi.with_user(c.approver).action_approve()
    assert pi.state == "approved"
    return pi


def _advance(c, pi, amount, user=None, **kw):
    vals = {"proforma_id": pi.id, "amount": amount, "purpose": "Supplier needs 50% to ship"}
    vals.update(kw)
    return c.env["fix.purchase.advance"].with_user(user or c.buyer).create(vals)


# ---- proforma ----------------------------------------------------------------------
def test_a_local_proforma_is_recorded_and_approved_by_another_person(c):
    po = _po(c)
    pi = _proforma(c, po)
    assert pi.name.startswith("SPI/")
    assert pi.vendor_id == c.vendor and pi.currency_id == po.currency_id
    assert pi.recorded_by_id == c.buyer
    pi.with_user(c.approver).action_approve()
    assert pi.state == "approved" and pi.decided_by_id == c.approver
    assert pi in po.proforma_ids


def test_the_recorder_never_approves_their_own_proforma(c):
    po = _po(c)
    pi = _proforma(c, po, user=c.buyer_approver)
    with pytest.raises(UserError, match="other than you"):
        pi.with_user(c.buyer_approver).action_approve()


def test_a_proforma_that_does_not_reconcile_to_the_order_is_refused(c):
    po = _po(c)
    line = po.line_ids[0]
    price = (po.amount_total + 500) / line.qty_ordered
    pi = _proforma(
        c,
        po,
        amount=po.amount_total + 500,
        line_ids=[
            (
                0,
                0,
                {
                    "product_id": line.product_id.id,
                    "quantity": line.qty_ordered,
                    "unit_price": price,
                },
            )
        ],
    )
    with pytest.raises(UserError, match="does not reconcile"):
        pi.with_user(c.approver).action_approve()
    c.env["ir.config_parameter"].sudo().set_param("cd_requisition.proforma_tolerance_pct", "5")
    pi.with_user(c.approver).action_approve()
    assert pi.state == "approved"


# ---- the PI's own lines, VAT and copy (12 Nov 2026) --------------------------------
def test_a_new_proforma_starts_from_the_order_lines(c):
    po = _po(c)
    pi = _proforma(c, po)
    assert len(pi.line_ids) == len(po.line_ids)
    assert pi.lines_total == pytest.approx(po.amount_total)
    assert pi.line_ids[0].product_id == po.line_ids[0].product_id


def test_vat_and_charges_sit_beside_the_goods_and_must_add_up(c):
    po = _po(c)
    vat = round(po.amount_total * 0.15, 2)
    pi = _proforma(c, po, amount=po.amount_total + vat, vat_amount=vat, pi_filename="PI.pdf")
    assert pi.computed_total == pytest.approx(po.amount_total + vat)
    pi.with_user(c.approver).action_approve()
    assert pi.state == "approved"
    short = _proforma(c, _po(c), proforma_no="PI-SHORT", vat_amount=100.0)
    with pytest.raises(UserError, match="does not add up"):
        short.with_user(c.approver).action_approve()


def test_a_proforma_lists_only_the_order_products_and_never_more(c):
    po = _po(c)
    line = po.line_ids[0]
    other = c.env["product.product"].create({"name": "SPI Not Ordered"})
    stray = _proforma(
        c,
        po,
        proforma_no="PI-STRAY",
        line_ids=[
            (0, 0, {"product_id": other.id, "quantity": 1, "unit_price": po.amount_total}),
        ],
    )
    with pytest.raises(UserError, match="not on purchase order"):
        stray.with_user(c.approver).action_approve()
    more = _proforma(
        c,
        po,
        proforma_no="PI-MORE",
        line_ids=[
            (
                0,
                0,
                {
                    "product_id": line.product_id.id,
                    "quantity": line.qty_ordered * 2,
                    "unit_price": line.unit_price / 2,
                },
            ),
        ],
    )
    with pytest.raises(UserError, match="asks for"):
        more.with_user(c.approver).action_approve()


def test_an_import_purchase_order_takes_no_local_proforma(c):
    po = _po(c, send=False)
    po.with_user(c.buyer).write({"purchase_type": "import"})
    with pytest.raises(ValidationError, match="import purchase order"):
        _proforma(c, po)


def test_a_local_order_is_in_taka_or_dollars_and_its_type_is_fixed_once_sent(c):
    draft = _po(c, send=False)
    with pytest.raises(ValidationError, match="BDT or USD"):
        draft.with_user(c.buyer).write({"currency_id": c.env.ref("base.EUR").id})
    sent = _po(c)
    with pytest.raises(UserError):
        sent.with_user(c.buyer).write({"purchase_type": "import"})
    assert sent.purchase_type == "local"


def test_a_proforma_on_an_unsent_order_waits_for_the_order(c):
    po = _po(c, send=False)
    pi = _proforma(c, po)
    with pytest.raises(UserError, match="sent to the supplier"):
        pi.with_user(c.approver).action_approve()


def test_an_expired_proforma_is_not_approved(c):
    po = _po(c)
    pi = _proforma(
        c,
        po,
        issued_on=date.today() - timedelta(days=30),
        valid_until=date.today() - timedelta(days=1),
    )
    with pytest.raises(UserError, match="expired"):
        pi.with_user(c.approver).action_approve()


def test_the_same_supplier_proforma_number_is_recorded_once(c):
    po = _po(c)
    _proforma(c, po, proforma_no="PI-777")
    with pytest.raises(ValidationError, match="already recorded"):
        _proforma(c, po, proforma_no="PI-777")


def test_a_decided_proforma_is_final_and_its_state_moves_only_by_action(c):
    pi = _approved_proforma(c)
    with pytest.raises(UserError, match="final"):
        pi.with_user(c.buyer).write({"amount": 1.0})
    fresh = _proforma(c, _po(c))
    with pytest.raises(UserError, match="changes only through its workflow"):
        fresh.with_user(c.buyer).write({"state": "approved"})


def test_rejecting_a_proforma_needs_a_reason_and_a_plain_user_records_none(c):
    pi = _proforma(c, _po(c))
    with pytest.raises(UserError, match="why"):
        pi.with_user(c.approver).action_reject(reason="  ")
    pi.with_user(c.approver).action_reject(reason="Wrong price on line 1")
    assert pi.state == "rejected" and pi.rejection_reason == "Wrong price on line 1"
    with pytest.raises(AccessError):
        _proforma(c, _po(c), user=c.clerk, proforma_no="PI-CLERK")


def test_a_second_approved_proforma_on_one_order_is_refused(c):
    po = _po(c)
    _approved_proforma(c, po)
    second = _proforma(c, po, proforma_no="PI-SECOND")
    with pytest.raises(UserError, match="already has an approved proforma"):
        second.with_user(c.approver).action_approve()


# ---- advance -----------------------------------------------------------------------
def test_an_advance_against_an_approved_proforma_is_approved_by_another_person(c):
    pi = _approved_proforma(c)
    adv = _advance(c, pi, pi.amount / 2)
    assert adv.purchase_order_id == pi.purchase_order_id and adv.name.startswith("SADV/")
    adv.with_user(c.buyer).action_request()
    assert adv.state == "requested" and adv.requested_by_id == c.buyer
    # the default cap is 0 %: every advance is explained
    with pytest.raises(UserError, match="state why"):
        adv.with_user(c.approver).action_approve()
    adv.with_user(c.approver).action_approve(reason="Supplier terms: 50% before dispatch")
    assert adv.state == "approved" and adv.above_cap
    assert pi.purchase_order_id.advance_approved_total == pytest.approx(pi.amount / 2)


def test_an_advance_within_the_cap_needs_no_reason(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_requisition.advance_cap_pct", "50")
    pi = _approved_proforma(c)
    adv = _advance(c, pi, pi.amount / 2)
    adv.with_user(c.buyer).action_request()
    adv.with_user(c.approver).action_approve()
    assert adv.state == "approved" and not adv.above_cap


def test_the_requester_never_approves_their_own_advance(c):
    pi = _approved_proforma(c)
    adv = _advance(c, pi, 100.0, user=c.buyer_approver)
    adv.with_user(c.buyer_approver).action_request()
    with pytest.raises(UserError, match="other than you"):
        adv.with_user(c.buyer_approver).action_approve(reason="x")


def test_advances_never_exceed_the_proforma(c):
    pi = _approved_proforma(c)
    first = _advance(c, pi, pi.amount * 0.8)
    first.with_user(c.buyer).action_request()
    first.with_user(c.approver).action_approve(reason="agreed terms")
    second = _advance(c, pi, pi.amount * 0.3)
    second.with_user(c.buyer).action_request()
    with pytest.raises(UserError, match="above proforma"):
        second.with_user(c.approver).action_approve(reason="more")


def test_an_advance_needs_an_approved_proforma_of_its_own_order(c):
    po = _po(c)
    pending = _proforma(c, po)
    adv = _advance(c, pending, 100.0)
    with pytest.raises(UserError, match="approved proforma"):
        adv.with_user(c.buyer).action_request()
    other = _approved_proforma(c)
    with pytest.raises(ValidationError, match="belongs to purchase order"):
        _advance(c, other, 100.0, purchase_order_id=po.id)


def test_a_requested_advance_is_fixed_and_rejection_is_explained(c):
    pi = _approved_proforma(c)
    adv = _advance(c, pi, 100.0)
    adv.with_user(c.buyer).action_request()
    with pytest.raises(UserError, match="fixed"):
        adv.with_user(c.buyer).write({"amount": 50.0})
    with pytest.raises(UserError, match="why"):
        adv.with_user(c.approver).action_reject(reason="")
    adv.with_user(c.approver).action_reject(reason="No security cheque received")
    assert adv.state == "rejected"
    with pytest.raises(UserError, match="changes only through its workflow"):
        _advance(c, pi, 10.0).with_user(c.buyer).write({"state": "approved"})
