# cd_rbac_ext - LIVE record-rule isolation proof (R01 re-audit 2026-10-22).
#
# The earlier "negative permission" suite raised AccessError itself and
# asserted it (tautology). This file exercises the REAL ir.rule records that
# generate-isolation-rules.py loaded, against the live test database, as a
# real non-superuser: cross-company records must be invisible (global rule)
# and a record in an operating unit the user does not belong to must be
# invisible to internal users (OCA operating-unit rule).
#
# Runs under the estate harness: the addons/conftest.py `odoo_env` fixture
# provides a superuser environment over fix_test whose transaction rolls
# back, so this test never persists anything.
from __future__ import annotations

import pytest
from odoo.exceptions import AccessError

pytestmark = [pytest.mark.isolation]


def _internal_user(env, company):
    """A plain internal user whose ONLY allowed company is `company`."""
    login = "isolation-probe@example.test"
    existing = env["res.users"].search([("login", "=", login)])
    if existing:
        existing.unlink()
    return env["res.users"].create(
        {
            "name": "Isolation Probe",
            "login": login,
            "email": login,
            "group_ids": [(4, env.ref("base.group_user").id)],
            "company_id": company.id,
            "company_ids": [(6, 0, [company.id])],
        }
    )


class TestCompanyIsolationLive:
    """Global company rule: another company's records are unreachable."""

    def test_company_rule_exists_for_entity(self, odoo_env):
        rules = odoo_env["ir.rule"].search(
            [("model_id.model", "=", "fix.entity"), ("name", "=", "fix.entity: allowed companies")]
        )
        assert rules, "generated multi-company ir.rule for fix.entity missing - run generate-isolation-rules and upgrade"

    def test_cross_company_record_invisible_to_user(self, odoo_env):
        env = odoo_env
        company_a = env.ref("base.main_company")
        company_b = env["res.company"].create({"name": "Isolation Probe Co B"})
        entity_b = env["fix.entity"].create(
            {
                "code": "ISO-B",
                "legal_name": "Isolation Probe Entity B",
                "company_id": company_b.id,
            }
        )
        env.flush_all()  # rules apply to flushed rows
        user = _internal_user(env, company_a)

        # search as the user: the global rule must filter it out
        visible = env["fix.entity"].with_user(user).search_count([("id", "=", entity_b.id)])
        assert (
            visible == 0
        ), "cross-company fix.entity VISIBLE to a company-A-only user - company rule not enforced"

        # direct read as the user: must raise
        with pytest.raises(AccessError):
            entity_b.with_user(user).read(["legal_name"])

        # and write must raise too
        with pytest.raises(AccessError):
            entity_b.with_user(user).write({"legal_name": "taken over"})

    def test_same_company_record_visible_to_user(self, odoo_env):
        env = odoo_env
        company_a = env.ref("base.main_company")
        entity_a = env["fix.entity"].create(
            {
                "code": "ISO-A",
                "legal_name": "Isolation Probe Entity A",
                "company_id": company_a.id,
            }
        )
        env.flush_all()
        user = _internal_user(env, company_a)
        visible = env["fix.entity"].with_user(user).search_count([("id", "=", entity_a.id)])
        assert visible == 1, "own-company fix.entity invisible - rule over-restricts"


class TestOperatingUnitIsolationLive:
    """Group-scoped OU rule (internal users): a unit the user is not in is
    unreachable unless the record carries no unit."""

    def test_ou_rule_exists_for_entity(self, odoo_env):
        rules = odoo_env["ir.rule"].search(
            [
                ("model_id.model", "=", "fix.entity"),
                ("name", "=", "fix.entity: allowed operating units (internal users)"),
            ]
        )
        assert rules, "generated operating-unit ir.rule for fix.entity missing"

    def test_other_ou_record_invisible_to_internal_user(self, odoo_env):
        env = odoo_env
        company = env.ref("base.main_company")
        ou_model = env.get("operating.unit")
        if ou_model is None:
            pytest.skip("OCA operating_unit not loaded in this database")
        ou_b = ou_model.create(
            {
                "name": "Isolation Probe OU B",
                "code": "ISO-OU-B",
                "company_id": company.id,
                "partner_id": env["res.partner"]
                .create({"name": "Isolation Probe OU B", "is_company": True})
                .id,
            }
        )
        entity_ou = env["fix.entity"].create(
            {
                "code": "ISO-OU",
                "legal_name": "Isolation Probe Entity OU",
                "company_id": company.id,
                "operating_unit_id": ou_b.id,
            }
        )
        env.flush_all()
        user = _internal_user(env, company)  # belongs to no operating unit
        visible = env["fix.entity"].with_user(user).search_count([("id", "=", entity_ou.id)])
        assert (
            visible == 0
        ), "fix.entity in an unassigned operating unit VISIBLE to a unit-less internal user"

    def test_no_ou_record_visible_to_internal_user(self, odoo_env):
        env = odoo_env
        company = env.ref("base.main_company")
        entity = env["fix.entity"].create(
            {
                "code": "ISO-NOOU",
                "legal_name": "Isolation Probe Entity No OU",
                "company_id": company.id,
                "operating_unit_id": False,
            }
        )
        env.flush_all()
        user = _internal_user(env, company)
        visible = env["fix.entity"].with_user(user).search_count([("id", "=", entity.id)])
        assert visible == 1, "record with no operating unit invisible - OU rule over-restricts"
