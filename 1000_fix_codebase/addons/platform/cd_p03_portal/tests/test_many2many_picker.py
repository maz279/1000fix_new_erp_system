# The many2many search-and-tick picker (14 Nov 2026).
#
# Every many2many on a workspace form was a native <select multiple> squeezed to
# one input's height: two rows visible, Ctrl+click to add, a plain click dropped
# every earlier pick (M42 "Approved Product Categories", reported by the owner).
# It is now chips plus a dialog; the form keeps the value as [{id, label}] and
# posts it as the whole selection. These tests pin the template and prove the
# server stores exactly what the picker posts.
from __future__ import annotations

import types
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"


def test_no_workspace_form_renders_a_native_multi_select():
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    assert 'multiple="multiple"' not in xml
    assert 'fm.type === \'many2many\'" class="d365-many"' in xml
    # the dialog: a search box, a tick list, Apply and Cancel
    for needle in (
        'id="d365_many_search"',
        "formManyToggle(row)",
        "formManyApply()",
        "formManyCancel()",
    ):
        assert needle in xml


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
