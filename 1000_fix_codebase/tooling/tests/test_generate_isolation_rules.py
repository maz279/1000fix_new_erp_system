"""generate-isolation-rules (FF-47): which models get which rule, and --check drift."""

from __future__ import annotations

import ast
import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

GEN_PATH = Path(__file__).resolve().parents[1] / "generators" / "generate-isolation-rules.py"


@pytest.fixture(scope="module")
def gen():
    spec = importlib.util.spec_from_file_location("generate_isolation_rules", GEN_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve the defining module
    spec.loader.exec_module(module)
    return module


MODELS_PY = """
from odoo import fields, models


class Order(models.Model):
    _name = "fix.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    company_id = fields.Many2one("res.company", required=True)
    operating_unit_id = fields.Many2one("operating.unit")


class Tagged(models.Model):
    _name = "fix.tagged"
    company_id = fields.Many2one("res.company")
    operating_unit_ids = fields.Many2many("operating.unit")


class Config(models.Model):
    _name = "fix.config"
    company_id = fields.Many2one("res.company")
    operating_unit_id = fields.Many2one("operating.unit")


class Owned(models.Model):
    _name = "fix.owned"
    company_id = fields.Many2one("res.company")
    operating_unit_id = fields.Many2one("operating.unit")


class Derived(models.Model):
    _name = "fix.derived"
    company_id = fields.Many2one("res.company", compute="_c")
    operating_unit_id = fields.Many2one("operating.unit", related="x.operating_unit_id")


class Extension(models.Model):
    _name = "fix.order"
    _inherit = "fix.order"
    company_id = fields.Many2one("res.company")


class Wizard(models.TransientModel):
    _name = "fix.wizard"
    company_id = fields.Many2one("res.company")
"""

OWNED_RULE = """<odoo>
    <record id="rule_owned_ou" model="ir.rule">
        <field name="model_id" ref="model_fix_owned"/>
        <field name="domain_force">[('operating_unit_id', 'in', operating_unit_ids)]</field>
    </record>
</odoo>
"""


def make_addon(root: Path, data: str = '"security/ir.model.access.csv",') -> Path:
    mod = root / "domain" / "x" / "cd_demo"
    (mod / "models").mkdir(parents=True)
    (mod / "security").mkdir()
    (mod / "models" / "fix_demo.py").write_text(MODELS_PY, encoding="utf-8")
    (mod / "security" / "owned_rules.xml").write_text(OWNED_RULE, encoding="utf-8")
    (mod / "__manifest__.py").write_text(
        '{\n    "name": "demo",\n    "depends": ["operating_unit"],\n    "data": [\n'
        f"        {data}\n    ],\n}}\n",
        encoding="utf-8",
    )
    return mod


@pytest.fixture
def addon(tmp_path, gen, monkeypatch):
    monkeypatch.setattr(gen, "load_exempt_models", lambda: {"fix.config"})
    return make_addon(tmp_path / "addons")


def rules_by_id(mod: Path) -> dict[str, dict[str, str]]:
    # The file this test just generated in tmp_path - not untrusted input.
    tree = ET.parse(mod / "security" / "fix_isolation_rules.xml")  # noqa: S314
    return {
        rec.get("id"): {f.get("name"): (f.text or f.get("eval") or f.get("ref")) for f in rec}
        for rec in tree.getroot()
    }


def test_check_fails_before_generation_and_passes_after(gen, addon, capsys):
    addons = str(addon.parents[2])
    assert gen.main(["--check", "--addons", addons]) == 1
    assert "FAIL" in capsys.readouterr().out
    assert gen.main(["--addons", addons]) == 0
    assert gen.main(["--check", "--addons", addons]) == 0


def test_rules_cover_exactly_the_transactional_gap(gen, addon):
    gen.main(["--addons", str(addon.parents[2])])
    rules = rules_by_id(addon)
    assert set(rules) == {
        "rule_fix_order_company",
        "rule_fix_order_operating_unit",
        "rule_fix_tagged_company",
        "rule_fix_tagged_operating_unit",
        "rule_fix_owned_company",  # its hand-written OU rule is left to the owner
        "rule_fix_derived_operating_unit",  # related = searchable; compute-only is not
    }
    company = rules["rule_fix_order_company"]
    assert company["model_id"] == "model_fix_order"
    assert "groups" not in company  # global: every user, portal included
    assert "('company_id', 'in', company_ids)" in company["domain_force"]
    ou = rules["rule_fix_order_operating_unit"]
    assert ou["groups"] == "[(4, ref('base.group_user'))]"  # internal users only
    assert "('operating_unit_id', 'in', operating_unit_ids)" in ou["domain_force"]
    assert (
        "('operating_unit_ids', 'in', operating_unit_ids)"
        in (rules["rule_fix_tagged_operating_unit"]["domain_force"])
    )


def test_manifest_lists_the_rules_once(gen, addon):
    addons = str(addon.parents[2])
    gen.main(["--addons", addons])
    gen.main(["--addons", addons])
    text = (addon / "__manifest__.py").read_text(encoding="utf-8")
    assert text.count(gen.RULES_FILE) == 1
    assert ast.literal_eval(text)["data"][0] == gen.RULES_FILE


def test_drift_in_generated_file_fails_check(gen, addon):
    addons = str(addon.parents[2])
    gen.main(["--addons", addons])
    target = addon / gen.RULES_FILE
    target.write_text(target.read_text(encoding="utf-8").replace("company_ids", "[]"), "utf-8")
    assert gen.main(["--check", "--addons", addons]) == 1


def test_single_line_data_list_is_edited(gen):
    out = gen.manifest_with_entry('{"name": "x", "data": ["views/a.xml"]}')
    assert out == '{"name": "x", "data": ["security/fix_isolation_rules.xml", "views/a.xml"]}'


def test_manifest_without_data_is_reported(gen, tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "load_exempt_models", lambda: set())
    mod = make_addon(tmp_path / "addons")
    (mod / "__manifest__.py").write_text('{"name": "demo"}', encoding="utf-8")
    assert gen.main(["--addons", str(mod.parents[2])]) == 2
