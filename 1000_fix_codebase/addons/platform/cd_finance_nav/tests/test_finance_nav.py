# cd_finance_nav — the A08 finance navigation bridge, checked against the live
# registry rather than against its own XML.
#
# The module exists for exactly one reason, stated in its manifest: the actions
# it attaches reference models owned by the g_finance addons, so it depends on
# every owning module to "guarantee every res_model exists in the registry when
# this module's data loads". That guarantee is what these tests measure - a
# menu whose action points at a model the registry does not have is a dead
# click, and the only way to see it is to resolve each one.
from __future__ import annotations

import pytest

pytestmark = [pytest.mark.financial]

MODULE = "cd_finance_nav"


def _own_records(env, model):
    """The records this module's data files created, via their XML ids."""
    data = env["ir.model.data"].sudo().search([("module", "=", MODULE), ("model", "=", model)])
    return env[model].sudo().browse(data.mapped("res_id")).exists()


def test_the_module_actually_attached_its_menus(odoo_env):
    menus = _own_records(odoo_env, "ir.ui.menu")
    assert len(menus) >= 20, f"expected the A08 menu bridge, found {len(menus)} menus"


def test_every_menu_this_module_adds_carries_an_action(odoo_env):
    """An action-less child is indistinguishable from the generated containers
    it is meant to make clickable."""
    actionless = [m.complete_name for m in _own_records(odoo_env, "ir.ui.menu") if not m.action]
    assert not actionless, f"menus with no action: {actionless[:10]}"


def test_every_action_resolves_to_a_model_in_the_registry(odoo_env):
    """The manifest's whole premise. A res_model absent from the registry makes
    the menu raise on click, and nothing in the XML can reveal it."""
    env = odoo_env
    missing = []
    for menu in _own_records(env, "ir.ui.menu"):
        action = menu.action
        res_model = getattr(action, "res_model", None)
        if res_model and res_model not in env:
            missing.append((menu.complete_name, res_model))
    assert not missing, f"menu actions pointing at absent models: {missing[:10]}"


def test_every_action_this_module_defines_is_readable_and_has_views(odoo_env):
    for action in _own_records(odoo_env, "ir.actions.act_window"):
        assert action.res_model, f"{action.name}: no res_model"
        assert action.res_model in odoo_env, f"{action.name}: {action.res_model} not in registry"
        assert action.view_mode, f"{action.name}: no view_mode"


def test_every_menu_hangs_off_a_menu_owned_by_the_workspace_module(odoo_env):
    """The bridge must extend the generated workspace tree (the `menu_p03_ws_*`
    containers from cd_p03_portal), not start a second finance navigation scheme
    beside it."""
    env = odoo_env
    owner = {
        d.res_id: d.module
        for d in env["ir.model.data"].sudo().search([("model", "=", "ir.ui.menu")])
    }
    stray = []
    for menu in _own_records(env, "ir.ui.menu"):
        parent = menu.parent_id
        if not parent or owner.get(parent.id) != "cd_p03_portal":
            stray.append((menu.complete_name, owner.get(parent.id) if parent else None))
    assert not stray, f"menus not parented on a cd_p03_portal menu: {stray[:10]}"
