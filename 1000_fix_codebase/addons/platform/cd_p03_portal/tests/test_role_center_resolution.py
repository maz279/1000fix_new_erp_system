# Role-center resolution on the live ORM (2026-11-10 role-center audit).
#
# The centers shipped without behavioural tests. The audit of the real estate
# found: a person the register could not place saw all 16 centers, the lazy
# KPI route served any center to any internal user, the group fallback ran on
# top of a register assignment (every Senior Technician landed on the dispatch
# console), an administrator's pill read "R-01 Chief Executive Officer", and
# seven tiles drilled to screen ids that do not exist.
from __future__ import annotations

import re
import uuid
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_role_center_api as api

U = uuid.uuid4().hex[:6]
SRC = Path(__file__).resolve().parents[1] / "static" / "src"


def _user(env, tag, groups=()):
    internal = env.ref("base.group_user")
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "RC test %s %s" % (tag, U),
                "login": "rc_%s_%s@example.test" % (tag, U),
                "group_ids": [(6, 0, [internal.id, *[g.id for g in groups]])],
            }
        )
    )


def _assign(env, user, code):
    role = env["fix.role"].search([("code", "=", code)], limit=1)
    assert role, "register role %s missing" % code
    env["fix.role.assignment"].sudo().create(
        {"user_id": user.id, "role_id": role.id, "source": "test:role-center"}
    )
    return role


def _resolve(env, user):
    controller = api.P03RoleCenterApiController()
    employee = env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
    return controller._resolve_roles(env, user, employee)


@pytest.fixture()
def register(odoo_env):
    if "fix.role" not in odoo_env or "fix.role.assignment" not in odoo_env:
        pytest.skip("cd_rbac_ext register not installed")
    return odoo_env


class TestRoleCenterResolution:
    def test_assignment_resolves_to_its_own_center_only(self, register):
        """A Senior Technician (R-10) holds the shared service-orders group
        that R-07 and R-21 also map to. The assignment is the authority: no
        dispatch or account-manager center on top of it."""
        env = register
        role = env["fix.role"].search([("code", "=", "R-10")], limit=1)
        shared = env["fix.role"].search([("code", "in", ["R-07", "R-21"])]).mapped("group_ids")
        user = _user(env, "tech", groups=[*role.group_ids, *shared])
        _assign(env, user, "R-10")
        resolved, is_admin = _resolve(env, user)
        assert not is_admin
        assert [r["ws"] for r in resolved] == ["field_technician"]
        assert resolved[0]["source"] == "assignment"

    def test_unmapped_role_holder_gets_no_center(self, register):
        """R-53 Project Manager has no functional center. The holder must
        resolve to nothing — not to a group guess, not to a title hint."""
        env = register
        shared = env["fix.role"].search([("code", "in", ["R-07", "R-21"])]).mapped("group_ids")
        user = _user(env, "pm", groups=shared)
        _assign(env, user, "R-53")
        env["hr.employee"].sudo().create(
            {"name": user.name, "user_id": user.id, "job_title": "Project Manager"}
        )
        resolved, is_admin = _resolve(env, user)
        assert not is_admin
        assert resolved == []

    def test_person_without_role_or_groups_gets_no_center(self, register):
        user = _user(register, "partner")
        resolved, is_admin = _resolve(register, user)
        assert (resolved, is_admin) == ([], False)

    def test_team_leader_resolves_to_workshop_supervisor(self, register):
        user = _user(register, "tl")
        _assign(register, user, "R-47")
        resolved, _is_admin = _resolve(register, user)
        assert [(r["code"], r["ws"]) for r in resolved] == [("R-47", "workshop_supervisor")]

    def test_group_fallback_still_serves_a_person_without_assignment(self, register):
        env = register
        role = env["fix.role"].search([("code", "=", "R-06")], limit=1)
        if not role.group_ids:
            pytest.skip("R-06 carries no mapped groups on this estate")
        user = _user(env, "bm", groups=role.group_ids)
        resolved, _is_admin = _resolve(env, user)
        assert "branch_manager" in [r["ws"] for r in resolved]
        assert {r["source"] for r in resolved} == {"groups"}

    def test_administrator_without_assignment_is_not_given_a_register_title(self, register):
        """The system administrator holds the administration workspace group,
        which R-01 also maps to; that must not label them "R-01 Chief
        Executive Officer". They preview every center instead."""
        env = register
        admin_group = env.ref("cd_rbac_ext.group_ws_administration", raise_if_not_found=False)
        if not admin_group:
            pytest.skip("administration workspace group not installed")
        user = _user(env, "adm", groups=[admin_group])
        resolved, is_admin = _resolve(env, user)
        assert is_admin
        assert resolved == []

    def test_project_manager_title_never_hints_executive(self):
        assert not [ws for needle, ws in api.JOB_TITLE_WS if "project manager" in needle]


class TestRoleCenterTiles:
    def _declared_screens(self):
        ids = set()
        for path in SRC.rglob("*.js"):
            ids.update(
                re.findall(r"id:\s*'(M\d{2}-[A-Za-z0-9-]+)'", path.read_text(encoding="utf-8"))
            )
        return ids

    def test_every_tile_drills_to_a_declared_screen(self):
        declared = self._declared_screens()
        assert len(declared) > 500, "screen scan found too little to be trusted"
        missing = {
            key: cue["screen"]
            for key, cue in api.KPI_CATALOG.items()
            if cue.get("screen") and cue["screen"] not in declared
        }
        assert not missing, "tiles drill to undeclared screens: %s" % missing

    def test_every_center_uses_catalogued_tiles_and_mapped_roles_exist(self):
        for ws, spec in api.ROLE_CENTER_SPECS.items():
            unknown = [k for k in spec["kpis"] if k not in api.KPI_CATALOG]
            assert not unknown, "%s uses uncatalogued tiles %s" % (ws, unknown)
        assert set(api.ROLE_TO_WS.values()) <= set(api.ROLE_CENTER_SPECS)

    def test_contracts_expiring_filters_on_a_real_field(self, odoo_env):
        if "fix.contract" not in odoo_env:
            pytest.skip("cd_contract_core not installed")
        ctx = {"day_start": None, "month_start": None, "team": [], "branch_domain": []}
        value = api.KPI_CATALOG["contracts_expiring"]["fn"](odoo_env, ctx)
        assert isinstance(value, int), "tile returned %r — its domain names a missing field" % (
            value,
        )

    def test_unassigned_tile_counts_the_model_its_screen_lists(self, odoo_env):
        if "fix.field.order" not in odoo_env:
            pytest.skip("cd_field_service not installed")
        ctx = {"day_start": None, "month_start": None, "team": [], "branch_domain": []}
        expected = (
            odoo_env["fix.field.order"]
            .sudo()
            .search_count([("state", "in", ["draft", "pending_dispatch", "declined"])])
        )
        assert api.KPI_CATALOG["unassigned_wos"]["fn"](odoo_env, ctx) == expected
        assert api.KPI_CATALOG["unassigned_wos"]["screen"] == "M02-unassigned"
