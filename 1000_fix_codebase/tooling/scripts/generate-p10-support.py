#!/usr/bin/env python3
"""generate-p10-support — Phase 10 supporting file generator.

Generates manifests, security, views, i18n, and tests for the Phase 10
modules from the model files already written. The business logic lives
in the model files; this tool handles the scaffolding.

RETIRED (2026-10-22, TR-07/DoD-08): this one-shot scaffolded the P10 modules (manifest, views, security, tests AND i18n/bn_BD.po + .pot) in a form
Odoo 19 cannot load - no `#. module:` comment and no `#:` references, so
odoo.tools.translate.PoFileReader raises AttributeError and the whole bn_BD
load aborts. The files it produced have since been completed and rewritten
in Odoo form; re-running it would overwrite them. It now exits without
writing anything. Maintain i18n/bn_BD.po directly and refresh templates and
references with tooling/scripts/extract-translations.py
(docs/guides/bn-terminology-glossary.md). The tables below are kept as history.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# (category, tech_name, cd_id, unit, summary, depends, model_file)
MODULES = [
    (
        "d_circular",
        "cd_marketplace",
        "CD-M12-01",
        "M12",
        "Marketplace & Seller Ecosystem",
        "base,mail,cd_entity_config,cd_party_master,cd_service_order,cd_catalogue,cd_tradein,cd_event_outbox",
        "fix_marketplace",
    ),
    (
        "g_finance",
        "cd_settlement_ext",
        "CD-M53-03",
        "M53",
        "Settlement & Payout (W7)",
        "base,mail,cd_entity_config,cd_gl_ext,cd_tax_engine_bd,cd_event_outbox",
        "fix_settlement_ext",
    ),
    (
        "b_customer_engagement",
        "cd_storefront",
        "CD-M38-02",
        "M38",
        "E-Commerce & Digital Storefront",
        "base,mail,cd_entity_config,cd_catalogue,cd_party_master,cd_event_outbox",
        "fix_storefront",
    ),
    (
        "b_customer_engagement",
        "cd_partner",
        "CD-M40-01",
        "M40",
        "Partner, Channel & Franchise",
        "base,mail,cd_entity_config,cd_party_master,cd_contract_core,cd_event_outbox",
        "fix_partner",
    ),
    (
        "c_commercial",
        "cd_dynamic_pricing",
        "CD-M11-01",
        "M11",
        "Dynamic Pricing (W7)",
        "base,mail,cd_entity_config,cd_rate_card,cd_event_outbox",
        "fix_dynamic_pricing",
    ),
    (
        "f_asset_facilities",
        "cd_facility",
        "CD-M47-01",
        "M47",
        "Facility & Branch Infrastructure",
        "base,mail,cd_entity_config,cd_equipment_register,cd_event_outbox",
        "fix_facility",
    ),
    (
        "i_governance",
        "cd_ppm",
        "CD-M67-01",
        "M67",
        "Project, Program & Portfolio Management",
        "base,mail,cd_entity_config,cd_hr_core,cd_event_outbox",
        "fix_ppm",
    ),
]


def gen_manifest(tech, cd_id, unit, summary, depends):
    deps = ", ".join(f'"{d.strip()}"' for d in depends.split(","))
    return f'''# {tech} — {unit} (P10).
{{
    "name": "1000FiX {summary}",
    "summary": "{unit}: {summary} ({cd_id})",
    "description": """
{cd_id} (P10) — {summary}.
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "{summary}",
    "depends": [{deps}],
    "data": ["security/ir.model.access.csv", "views/{tech}_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "{cd_id}",
    "x_module_id": "{unit}",
    "x_wave": "W7",
    "x_owner": "{summary}",
    "x_category": "Phase10",
    "x_tier": "T10",
}}
'''


def gen_csv(model_names):
    rows = ["id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"]
    for mn in model_names:
        rows.append(
            f"access_{mn.replace('.', '_')},{mn},model_{mn.replace('.', '_')},base.group_user,1,1,1,0"
        )
    return "\n".join(rows) + "\n"


def gen_views(tech, model_names):
    views, menus = [], []
    for i, mn in enumerate(model_names):
        display = mn.replace("fix.", "").replace(".", " ").title()
        vid = mn.replace(".", "_")
        views.append(
            f'    <record id="view_{vid}_list" model="ir.ui.view">\n'
            f'        <field name="name">{mn}.list</field>\n'
            f'        <field name="model">{mn}</field>\n'
            f'        <field name="arch" type="xml">\n'
            f'            <list><field name="name"/></list>\n'
            f"        </field>\n"
            f"    </record>\n"
            f'    <record id="action_{vid}" model="ir.actions.act_window">\n'
            f'        <field name="name">{display}</field>\n'
            f'        <field name="res_model">{mn}</field>\n'
            f'        <field name="view_mode">list,form</field>\n'
            f"    </record>"
        )
        menus.append(
            f'    <menuitem id="menu_{vid}" name="{display}" '
            f'parent="cd_entity_config.menu_fix_operations_root" '
            f'action="action_{vid}" sequence="{300 + i * 10}"/>'
        )
    return (
        f'<?xml version="1.0" encoding="utf-8"?>\n<!-- {tech} views (P10). -->\n<odoo>\n'
        + "\n".join(views)
        + "\n\n"
        + "\n".join(menus)
        + "\n</odoo>\n"
    )


def gen_po(tech, summary):
    return f'# Bengali translations for {tech} (P10).\nmsgid ""\nmsgstr ""\n"Language: bn_BD\\n"\n"Content-Type: text/plain; charset=UTF-8\\n"\n\nmsgid "{summary}"\nmsgstr "{summary} (\\u09ac\\u09be\\u0982\\u09b2\\u09be)"\n'


def main() -> int:
    for cat, tech, cd_id, unit, summary, depends, model_fname in MODULES:
        base = REPO / "addons" / "domain" / cat / tech
        model_path = base / "models" / f"{model_fname}.py"

        if not model_path.exists():
            print(f"[SKIP] {tech}: model file {model_fname}.py not found")
            continue

        code = model_path.read_text(encoding="utf-8")
        model_names = re.findall(r'_name = "([^"]+)"', code)

        # manifest
        (base / "__manifest__.py").write_text(
            gen_manifest(tech, cd_id, unit, summary, depends), encoding="utf-8"
        )
        # security
        (base / "security" / "ir.model.access.csv").write_text(
            gen_csv(model_names), encoding="utf-8"
        )
        # views
        (base / "views" / f"{tech}_views.xml").write_text(
            gen_views(tech, model_names), encoding="utf-8"
        )
        # i18n
        po = gen_po(tech, summary)
        (base / "i18n" / "bn_BD.po").write_text(po, encoding="utf-8")
        (base / "i18n" / f"{tech}.pot").write_text(po, encoding="utf-8")
        # tests (placeholder if no real test exists)
        test_file = base / "tests" / f"test_{tech.replace('cd_', '')}.py"
        if not test_file.exists() or len(test_file.read_text(encoding="utf-8")) < 50:
            test_file.write_text(
                f'"""{tech} tests (P10)."""\nimport unittest\n\n\n'
                f'class Test{tech.replace("cd_", "").title().replace("_", "")}'
                f'(unittest.TestCase):\n'
                f'    def test_module_loads(self):\n'
                f'        from odoo.addons.{tech} import models\n'
                f'        self.assertTrue(models)\n\n\n'
                f'if __name__ == "__main__":\n    unittest.main()\n',
                encoding="utf-8",
            )

        print(f"[ ok ] {tech} ({len(model_names)} models)")
    print("generate-p10-support: done")
    return 0


if __name__ == "__main__":
    print(
        "generate-p10-support.py: RETIRED - it would overwrite the Odoo-loadable i18n/bn_BD.po files; "
        "use tooling/scripts/extract-translations.py (see the module docstring)."
    )
    sys.exit(2)
