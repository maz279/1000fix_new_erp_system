"""test_a12_reaudit_dimensions.py — M67-1 (A12 re-audit 2026-11-22).

A milestone invoice must carry the PROJECT's operating unit and branch, not
the company default: on a COA-03 chart that requires the branch dimension,
project revenue used to post to head office (or the posting was refused).
"""

import pytest
from odoo.exceptions import UserError


@pytest.fixture
def env(odoo_env):
    return odoo_env


class _Move:
    """_invoice_dimensions only reads len(move.line_ids)."""

    line_ids = [1, 2, 3]


def _project(env, **extra):
    return env["fix.project"].create(
        {
            "name": "Reaudit Dimension Probe",
            "project_type": "internal",
            "contract_value": 100000.0,
            **extra,
        }
    )


def _billing(env, project):
    return env["fix.project.billing"].create(
        {"project_id": project.id, "billing_type": "milestone", "amount": 1000.0}
    )


def _entity(env):
    entity = env["fix.entity"].sudo().search([("company_id", "=", env.company.id)], limit=1)
    if not entity:
        entity = (
            env["fix.entity"]
            .sudo()
            .create({"legal_name": "Reaudit Entity", "company_id": env.company.id})
        )
    return entity


def test_dimensions_carry_the_project_unit_and_branch(env):
    units = env["operating.unit"].sudo().search([("company_id", "=", env.company.id)], limit=2)
    if len(units) < 2:
        pytest.skip("company has fewer than two operating units to separate")
    branch = (
        env["fix.branch"]
        .sudo()
        .create(
            {
                "name": "Reaudit Branch",
                "code": "RB01",
                "entity_id": _entity(env).id,
                "operating_unit_id": units[1].id,
                "company_id": env.company.id,
            }
        )
    )
    project = _project(env, operating_unit_id=units[1].id)
    dims = _billing(env, project)._invoice_dimensions(_Move())
    assert set(dims) == {0, 1, 2}
    assert dims[0]["operating_unit_id"] == units[1].id
    assert dims[0]["branch_id"] == branch.id
    assert dims[0]["project_ref"] == project.code


def test_dimensions_refuse_an_unowned_project_in_a_multi_unit_company(env):
    units = env["operating.unit"].sudo().search([("company_id", "=", env.company.id)], limit=2)
    if len(units) < 2:
        pytest.skip("company has fewer than two operating units to separate")
    project = _project(env)  # no operating unit recorded
    with pytest.raises(UserError, match="Operating Unit"):
        _billing(env, project)._invoice_dimensions(_Move())


def test_dimensions_derive_the_single_unit_company(env):
    units = env["operating.unit"].sudo().search([("company_id", "=", env.company.id)])
    if len(units) != 1:
        pytest.skip("company does not have exactly one operating unit")
    project = _project(env)  # no operating unit recorded
    dims = _billing(env, project)._invoice_dimensions(_Move())
    assert dims[0]["operating_unit_id"] == units.id
