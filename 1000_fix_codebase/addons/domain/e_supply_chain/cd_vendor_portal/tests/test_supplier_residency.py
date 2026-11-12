# A foreign (non-resident) supplier can be activated on its own document set.
#
# fix_real, 12 Nov 2026: the activation gate demanded a Bangladeshi trade
# licence, TIN and VAT registration from every supplier, so the 13 foreign
# suppliers among the 25 largest by open payable (Shenzhen, Guangzhou,
# Singapore...) could never take a purchase order. A supplier now carries a
# residency; a foreign one is activated on its certificate of incorporation,
# home-country tax residency and bank letter (configurable), and the
# residency must agree with the contact's country so a Bangladeshi supplier
# cannot be re-labelled to escape its TIN and VAT. Rolled back.
# ruff: noqa: F811  (the M42 suite's fixture `c` is imported and used as a parameter)
import pytest
from odoo.exceptions import UserError

from .test_a06_m42_controls import (
    PDF,
    c,  # noqa: F401 - pytest fixture
    cleared_screenings,
    docs,
    gate,
    qual,
    supplier,
)

FOREIGN_DOCS = ("incorporation", "tax_residency", "bank")


def _country(c, code):
    return c.env["res.country"].search([("code", "=", code)], limit=1)


def foreign_supplier(c, code="CN"):
    s = supplier(c, residency="foreign")
    s.partner_id.sudo().write({"country_id": _country(c, code).id})
    return s


def foreign_docs(c, s, types=FOREIGN_DOCS):
    out = c.env["fix.supplier.document"]
    for t in types:
        out |= (
            c.env["fix.supplier.document"]
            .with_user(c.steward)
            .create(
                {"supplier_id": s.id, "doc_type": t, "number": "%s-%s" % (t, s.id), "file": PDF}
            )
        )
    out.with_user(c.steward2).action_verify()
    return out


def test_a_foreign_supplier_is_activated_on_its_own_documents(c):
    s = foreign_supplier(c)
    assert s._a06_mandatory_docs() == FOREIGN_DOCS
    foreign_docs(c, s)
    cleared_screenings(c, s)
    q = qual(c, s)
    gate(c, s, q).with_user(c.approver).action_activate()
    assert s.status == "active"
    assert c.env["fix.purchase.order"]._fix_vendor_blockers(s.partner_id) == []


def test_a_foreign_supplier_still_needs_every_foreign_document(c):
    s = foreign_supplier(c)
    foreign_docs(c, s, types=("incorporation", "bank"))
    cleared_screenings(c, s)
    q = qual(c, s)
    with pytest.raises(UserError, match="Tax Residency"):
        gate(c, s, q).with_user(c.approver).action_activate()


def test_bangladeshi_documents_do_not_activate_a_foreign_supplier(c):
    s = foreign_supplier(c)
    docs(c, s)  # trade licence, TIN, VAT
    cleared_screenings(c, s)
    q = qual(c, s)
    with pytest.raises(UserError, match="Incorporation"):
        gate(c, s, q).with_user(c.approver).action_activate()


def test_a_resident_supplier_keeps_the_bangladeshi_set(c):
    s = supplier(c)
    assert s.residency == "resident"
    assert s._a06_mandatory_docs() == ("trade_licence", "tin", "vat")


def test_a_bangladeshi_contact_cannot_be_activated_as_foreign(c):
    s = supplier(c, residency="foreign")
    s.partner_id.sudo().write({"country_id": _country(c, "BD").id})
    foreign_docs(c, s)
    cleared_screenings(c, s)
    q = qual(c, s)
    with pytest.raises(UserError, match="home country"):
        gate(c, s, q).with_user(c.approver).action_activate()


def test_a_foreign_contact_cannot_be_activated_as_resident(c):
    s = supplier(c)
    s.partner_id.sudo().write({"country_id": _country(c, "CN").id})
    docs(c, s)
    cleared_screenings(c, s)
    q = qual(c, s)
    with pytest.raises(UserError, match="record the supplier as foreign"):
        gate(c, s, q).with_user(c.approver).action_activate()


def test_residency_is_a_stewards_call_and_only_before_activation(c):
    s = supplier(c)
    with pytest.raises(UserError, match="Supplier Steward"):
        s.with_user(c.plain).write({"residency": "foreign"})
    s.with_user(c.steward).write({"residency": "foreign"})
    assert s.residency == "foreign"
    s.partner_id.sudo().write({"country_id": _country(c, "CN").id})
    foreign_docs(c, s)
    cleared_screenings(c, s)
    gate(c, s, qual(c, s)).with_user(c.approver).action_activate()
    with pytest.raises(UserError, match="changes only before activation"):
        s.with_user(c.steward).write({"residency": "resident"})


def test_the_foreign_set_is_configurable_and_fails_closed(c):
    s = foreign_supplier(c)
    params = c.env["ir.config_parameter"].sudo()
    params.set_param("cd_vendor_portal.mandatory_docs_foreign", "incorporation, bank")
    assert s._a06_mandatory_docs() == ("incorporation", "bank")
    params.set_param("cd_vendor_portal.mandatory_docs_foreign", "nonsense")
    assert s._a06_mandatory_docs() == FOREIGN_DOCS


def test_vendor_pickers_can_filter_contacts_by_residency(c):
    """The local PO picker asks for resident suppliers, the import PO picker
    for foreign ones (13 Nov 2026)."""
    home = supplier(c)
    abroad = foreign_supplier(c)
    Partner = c.env["res.partner"]
    resident = Partner.search([("fix_supplier_residency", "=", "resident")])
    foreign = Partner.search([("fix_supplier_residency", "=", "foreign")])
    assert home.partner_id in resident and home.partner_id not in foreign
    assert abroad.partner_id in foreign and abroad.partner_id not in resident
    assert abroad.partner_id.fix_supplier_residency == "foreign"
    # a contact with no supplier record matches neither
    stranger = Partner.create({"name": "A06M42T not a supplier"})
    assert stranger not in resident | foreign
    assert not stranger.fix_supplier_residency
