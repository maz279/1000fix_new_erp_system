# The P03 picker standard (14-15 Nov 2026).
#
# Every many2many on a workspace form was a native <select multiple> squeezed to
# one input's height: two rows visible, Ctrl+click to add, a plain click dropped
# every earlier pick (M42 "Approved Product Categories", reported by the owner).
# It became chips plus a search-and-tick popup; the owner approved it and asked
# for it as the standard across M01-M67. The same popup now serves every long or
# server-searched choice: many2one / selection fields, child-grid cells and the
# finance editors' masters (more than PICK_POPUP_MIN options); a short list
# stays a dropdown. These tests pin the template and the rule, and prove the
# server stores exactly what the picker posts.
from __future__ import annotations

import re
import types
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"


def _xml():
    return (SRC / "p03_workspace.xml").read_text(encoding="utf-8")


def _js():
    return (SRC / "p03_workspace.js").read_text(encoding="utf-8")


def test_no_workspace_form_renders_a_native_multi_select():
    xml = _xml()
    assert 'multiple="multiple"' not in xml
    assert 'fm.type === \'many2many\'" class="d365-many"' in xml
    # the popup: a search box, a tick / pick list, Apply and Cancel
    for needle in (
        'id="d365_many_search"',
        "this.pickerToggle(row)",
        "this.pickerApply()",
        "this.pickerCancel()",
    ):
        assert needle in xml


def test_the_popup_is_one_instance_at_the_workspace_root():
    # it serves the finance editors and modals too, so it is not inside a form
    xml = _xml()
    main = xml[: xml.index('<t t-name="cd_p03_portal.ReportActions">')]
    assert main.count('t-if="picker" class="modal-scrim d365-many-scrim"') == 1
    assert main.rindex("d365-many-scrim") > main.rindex("d365-tabpanel")


def test_the_rule_is_one_threshold_of_ten():
    js = _js()
    assert re.search(r"const PICK_POPUP_MIN = 10;", js)
    assert "return !!remote || (choices || []).length > PICK_POPUP_MIN;" in js


def test_long_single_choices_use_the_popup_on_the_form_and_the_grid():
    xml = _xml()
    assert '<div t-elif="formUsesPicker(fm)" class="d365-one">' in xml
    assert '<div t-elif="formLineUsesPicker(lf)" class="d365-one d365-one-sm">' in xml
    # the old side-by-side "type to search" boxes are gone
    assert "formChoiceSearch(" not in xml and "formLookupInput(" not in xml


@pytest.mark.parametrize(
    "rows",
    [
        "pickAccountRows",
        "pickPartnerRows",
        "pickBranchRows",
        "pickCustomerRows",
        "pickPaymentMethodRows",
        "pickUnappliedRows",
        "pickOpenInvoiceRows",
        "pickConsoleBranchRows",
        "pickNameRows(branchOptions",
        "pickNameRows(technicianOptions)",
        "pickNameRows(flt.options)",
    ],
)
def test_the_finance_and_master_dropdowns_follow_the_rule(rows):
    # a long list opens the popup; the original <select> stays for a short one
    xml = _xml()
    assert f'<button t-if="{rows}' in xml
    at = xml.index(f'<button t-if="{rows}')
    assert ".length &gt; pickPopupMin" in xml[at : at + 120]
    assert '<select t-else=""' in xml[at : at + 1500]


def test_picker_handlers_call_no_template_unsafe_function():
    # Found live on 15 Nov: inside a QWeb handler, t('Account') ran with no
    # component ("reading 'state' of undefined") and String(id) is not a
    # template global - the popup opened but nothing was set. The conversion
    # and the translation happen in pickOneOpen (JS) instead.
    handlers = re.findall(r't-on-click="\(\) => this\.pick[^"]*"', _xml())
    assert len(handlers) >= 16
    for handler in handlers:
        assert not re.search(r"(?<![.\w])(t|String|Number)\(", handler), handler


def test_the_dialog_styles_compile_in_libsass():
    # a CSS min(640px, 90vh) broke the whole workspace stylesheet on 14 Nov
    # ("A css error occurred"): libsass cannot mix vh and px in min()
    sass = pytest.importorskip("sass")
    sass.compile(string=(SRC / "p03_conformance.scss").read_text(encoding="utf-8"))


@pytest.fixture
def ui(odoo_env):
    ctl = api.P03GenericApiController()
    cls = api.P03GenericApiController
    old = getattr(api, "request", None)

    def call(name, **kw):
        api.request = types.SimpleNamespace(env=odoo_env)
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            form=lambda **kw: call("model_form", **kw),
            write=lambda **kw: call("model_write", **kw),
        )
    finally:
        api.request = old


@pytest.fixture
def supplier(odoo_env):
    partner = odoo_env["res.partner"].create({"name": "M2M Picker Supplier", "is_company": True})
    return odoo_env["fix.supplier"].create({"name": partner.name, "partner_id": partner.id})


def _categories(env, n):
    parent = env["product.category"].create({"name": "M2M Picker"})
    return env["product.category"].create(
        [{"name": "Picker Cat %d" % i, "parent_id": parent.id} for i in range(n)]
    )


def test_the_picked_categories_are_saved_as_the_whole_selection(odoo_env, ui, supplier):
    cats = _categories(odoo_env, 3)
    posted = [{"id": c.id, "label": c.display_name} for c in cats[:2]]
    res = ui.write(
        model="fix.supplier", record_id=supplier.id, values={"approved_category_ids": posted}
    )
    assert not res.get("error"), res
    assert supplier.approved_category_ids == cats[:2]
    # a later pick replaces, it does not append
    res = ui.write(
        model="fix.supplier",
        record_id=supplier.id,
        values={"approved_category_ids": [{"id": cats[2].id, "label": cats[2].display_name}]},
    )
    assert not res.get("error"), res
    assert supplier.approved_category_ids == cats[2]


def test_removing_every_chip_clears_the_field(odoo_env, ui, supplier):
    cats = _categories(odoo_env, 2)
    supplier.approved_category_ids = cats
    res = ui.write(
        model="fix.supplier", record_id=supplier.id, values={"approved_category_ids": []}
    )
    assert not res.get("error"), res
    assert not supplier.approved_category_ids


def test_the_form_reloads_the_chips_it_saved(odoo_env, ui, supplier):
    cats = _categories(odoo_env, 2)
    supplier.approved_category_ids = cats
    out = ui.form(
        model="fix.supplier",
        record_id=supplier.id,
        fields=[{"name": "approved_category_ids"}],
    )
    assert out["record"]["approved_category_ids"] == [
        {"id": c.id, "label": c.display_name} for c in cats
    ]
    meta = next(f for f in out["fields"] if f["name"] == "approved_category_ids")
    assert meta["type"] == "many2many"
