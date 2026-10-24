"""AS-03 record-rule isolation (FF-47, pentest A01-05) on the live registry.

The rules written by tooling/generators/generate-isolation-rules.py must not
only exist - they must restrict an internal user: another operating unit's or
another company's records are invisible, unit-less records stay visible, and
operating-unit managers (OCA operating_unit) see every unit.
"""

from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_MODELS = ("fix.org.position", "fix.cost.allocation")


def _generated_plan():
    spec = importlib.util.spec_from_file_location(
        "generate_isolation_rules_live",
        ROOT / "tooling" / "generators" / "generate-isolation-rules.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return [
        m
        for p in module.plan(ROOT / "addons", module.load_exempt_models()).values()
        for m in p.models
    ]


@pytest.fixture
def iso(odoo_env):
    """Two operating units of the main company and an internal user of unit A."""
    from odoo import Command

    env = odoo_env
    tag = uuid.uuid4().hex[:8]  # fix_test is shared: never collide on unique keys
    company = env.company

    def unit(code):
        partner = env["res.partner"].create({"name": f"Isolation unit {code}-{tag}"})
        return env["operating.unit"].create(
            {
                "name": f"Isolation {code}-{tag}",
                "code": f"ISO{code}{tag}",
                "partner_id": partner.id,
                "company_id": company.id,
            }
        )

    unit_a, unit_b = unit("A"), unit("B")
    user = env["res.users"].create(
        {
            "name": f"Isolation probe {tag}",
            "login": f"isolation.probe.{tag}@example.test",
            "group_ids": [Command.set([env.ref("base.group_user").id])],
            "company_id": company.id,
            "company_ids": [Command.set([company.id])],
            "assigned_operating_unit_ids": [Command.set([unit_a.id])],
            "default_operating_unit_id": unit_a.id,
        }
    )
    return {"env": env, "tag": tag, "company": company, "a": unit_a, "b": unit_b, "user": user}


def _records(iso, model, **extra):
    env, tag = iso["env"], iso["tag"]
    Model = env[model]
    return {
        key: Model.create({"name": f"iso-{key}-{tag}", "operating_unit_id": ou, **extra})
        for key, ou in (("a", iso["a"].id), ("b", iso["b"].id), ("none", False))
    }


def test_every_transactional_model_has_both_rules_loaded(odoo_env):
    plan = _generated_plan()
    assert len(plan) >= 170
    odoo_env.cr.execute(
        """
        SELECT m.model,
               bool_or(r.global AND r.domain_force LIKE '%%company_ids%%'),
               bool_or(NOT r.global AND r.domain_force LIKE '%%operating_unit_ids%%')
          FROM ir_rule r JOIN ir_model m ON m.id = r.model_id
         WHERE r.active AND m.model = ANY(%s)
         GROUP BY m.model
        """,
        ([m.name for m in plan],),
    )
    loaded = {model: (co, ou) for model, co, ou in odoo_env.cr.fetchall()}
    missing = [
        m.name
        for m in plan
        if (m.company and not loaded.get(m.name, (False, False))[0])
        or (m.ou_field and not loaded.get(m.name, (False, False))[1])
    ]
    assert not missing, f"generated rules not loaded for: {missing[:10]}"


@pytest.mark.parametrize("model", SAMPLE_MODELS)
def test_internal_user_sees_only_own_unit_and_unitless(iso, model):
    from odoo.exceptions import AccessError

    recs = _records(iso, model)
    as_user = iso["env"][model].with_user(iso["user"])
    ids = [r.id for r in recs.values()]
    assert set(as_user.search([("id", "in", ids)]).ids) == {recs["a"].id, recs["none"].id}
    with pytest.raises(AccessError):
        as_user.browse(recs["b"].id).read(["name"])


@pytest.mark.parametrize("model", SAMPLE_MODELS)
def test_operating_unit_manager_sees_every_unit(iso, model):
    recs = _records(iso, model)
    user = iso["user"]
    user.write(
        {"group_ids": [(4, iso["env"].ref("operating_unit.group_manager_operating_unit").id)]}
    )
    iso["env"].invalidate_all()
    iso["env"].registry.clear_cache()
    as_user = iso["env"][model].with_user(user)
    ids = [r.id for r in recs.values()]
    assert set(as_user.search([("id", "in", ids)]).ids) == set(ids)


@pytest.mark.parametrize("model", SAMPLE_MODELS)
def test_other_company_records_are_invisible(iso, model):
    env = iso["env"]
    other = env["res.company"].create({"name": f"Isolation other co {iso['tag']}"})
    mine = env[model].create({"name": f"iso-mine-{iso['tag']}", "operating_unit_id": False})
    theirs = env[model].create(
        {"name": f"iso-theirs-{iso['tag']}", "operating_unit_id": False, "company_id": other.id}
    )
    as_user = env[model].with_user(iso["user"])
    assert as_user.search([("id", "in", [mine.id, theirs.id])]).ids == [mine.id]
