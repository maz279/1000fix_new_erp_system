# The import proforma as the supplier's document, and the import purchase
# order raised from either side (user request, 12 Nov 2026). Runs on the M44
# control-suite fixture: non-admin users, a USD import order of two lines
# (10 x 600 + 20 x 200 = 10,000 FOB) and a valid IRC.
import pytest

# the `c` fixture comes from this folder's conftest.py
from odoo.addons.cd_import_order.tests.test_a06_m44_controls import _user, proforma
from odoo.exceptions import AccessError, UserError, ValidationError

GROUP_BUYER = "cd_requisition.group_fix_procurement_buyer"


def _line(c, part, qty, price, **kw):
    vals = {"part_id": part.id, "quantity": qty, "unit_price": price}
    vals.update(kw)
    return (0, 0, vals)


# ---- the proforma's lines and totals ----------------------------------------------
def test_a_new_proforma_starts_from_the_order_lines(c):
    pf = proforma(c)
    assert pf.currency_id == c.usd
    assert len(pf.line_ids) == 2
    assert sorted(pf.line_ids.mapped("subtotal")) == [4000.0, 6000.0]
    assert pf.lines_total == pytest.approx(10000.0)
    assert pf.computed_total == pytest.approx(10000.0)
    assert set(pf.line_ids.mapped("hs_code")) == {c.hs.hs_code, c.hs2.hs_code}
    assert pf.supplier_id == c.supplier


def test_a_proforma_that_does_not_add_up_is_not_approved(c):
    pf = proforma(c, other_charges=50.0)
    with pytest.raises(UserError, match="does not add up"):
        pf.with_user(c.approver).action_approve()


def test_a_proforma_names_only_the_order_parts_and_never_more(c):
    stray = c.env["fix.spare.part"].create(
        {"name": "M44T stray %s" % c.tag, "part_number": "M44-STRAY-%s" % c.tag}
    )
    pf = proforma(
        c,
        line_ids=[
            _line(c, c.part, 10, 600.0),
            _line(c, c.part2, 18, 200.0),
            _line(c, stray, 2, 200.0),
        ],
    )
    with pytest.raises(UserError, match="not on import order"):
        pf.with_user(c.approver).action_approve()
    more = proforma(
        c,
        proforma_no="PI-MORE-%s" % c.tag,
        line_ids=[_line(c, c.part, 12, 500.0), _line(c, c.part2, 20, 200.0)],
    )
    with pytest.raises(UserError, match="asks for 12"):
        more.with_user(c.approver).action_approve()


def test_a_proforma_with_no_lines_is_not_approved(c):
    # in BDT the order's USD lines are not copied: the PI's own lines are needed
    pf = proforma(c, currency_id=c.bdt.id, amount=10000.0 * c.order.fx_rate)
    assert not pf.line_ids
    with pytest.raises(UserError, match="no item lines"):
        pf.with_user(c.approver).action_approve()


def test_a_proforma_is_in_the_order_currency_or_bdt(c):
    eur = c.env.ref("base.EUR")
    assert eur.active, "the import currencies are active"
    with pytest.raises(ValidationError, match="order's currency"):
        proforma(c, currency_id=eur.id)


def test_a_decided_proforma_keeps_its_lines_and_lc_terms(c):
    pf = proforma(c, port_of_loading="Shenzhen", beneficiary_swift="ABCDCNSHXXX")
    pf.with_user(c.approver).action_approve()
    assert pf.state == "approved"
    with pytest.raises(UserError):
        pf.with_user(c.officer).write({"port_of_loading": "Ningbo"})
    with pytest.raises(UserError, match="decided"):
        pf.line_ids[0].with_user(c.officer).write({"quantity": 1})


def test_the_supplier_pi_is_attached(c):
    pf = proforma(c, pi_file=b"JVBERi0xLjQK", pi_filename="PI-123.pdf")
    assert pf.pi_filename == "PI-123.pdf" and pf.pi_file


# ---- two purchase formats, linked either way ----------------------------------------
def _import_po(c, currency=None, purchase_type="import"):
    return c.env["fix.purchase.order"].create(
        {
            "vendor_id": c.supplier.id,
            "operating_unit_id": c.ou.id,
            "purchase_type": purchase_type,
            "currency_id": (currency or c.env.ref("base.EUR")).id,
            "line_ids": [
                (0, 0, {"product_id": c.product.id, "qty_ordered": 5, "unit_price": 300.0}),
                (0, 0, {"product_id": c.product2.id, "qty_ordered": 4, "unit_price": 50.0}),
            ],
        }
    )


def test_a_local_purchase_order_is_in_taka_or_dollars(c):
    with pytest.raises(ValidationError, match="BDT or USD"):
        _import_po(c, purchase_type="local")
    assert _import_po(c).currency_id.name == "EUR"


def test_an_import_purchase_order_raises_its_import_order(c):
    po = _import_po(c)
    po.with_user(c.officer).action_create_import_order()
    order = po.import_order_ids
    assert len(order) == 1 and order.purchase_order_id == po
    assert order.currency_id.name == "EUR" and order.supplier_id == c.supplier
    assert sorted(order.line_ids.mapped("part_id").ids) == sorted((c.part | c.part2).ids)
    assert order.fob_value == pytest.approx(1700.0)
    assert order.name in po.import_order_refs
    with pytest.raises(UserError, match="already has import order"):
        po.with_user(c.officer).action_create_import_order()
    local = _import_po(c, currency=c.usd, purchase_type="local")
    with pytest.raises(UserError, match="local purchase order"):
        local.with_user(c.officer).action_create_import_order()
    with pytest.raises((UserError, AccessError)):
        _import_po(c).with_user(c.clerk).action_create_import_order()


def test_an_import_order_raises_its_purchase_order(c):
    buyer = _user(c.env, "m44t_buyer_%s" % c.tag, c.ou, GROUP_BUYER)
    with pytest.raises(UserError, match="Procurement Buyer"):
        c.order.with_user(c.officer).action_create_purchase_order()
    c.order.with_user(buyer).action_create_purchase_order()
    po = c.order.purchase_order_id
    assert po.purchase_type == "import" and po.currency_id == c.usd
    assert po.state == "draft" and po.vendor_id == c.supplier
    assert sorted(po.line_ids.mapped("product_id").ids) == sorted((c.product | c.product2).ids)
    assert po.amount_total == pytest.approx(10000.0)
    with pytest.raises(UserError, match="already has purchase order"):
        c.order.with_user(buyer).action_create_purchase_order()
    # the draft PO is linked, but nothing moves against it until it is issued
    pf = proforma(c)
    with pytest.raises(UserError, match="still a draft"):
        pf.with_user(c.approver).action_approve()
