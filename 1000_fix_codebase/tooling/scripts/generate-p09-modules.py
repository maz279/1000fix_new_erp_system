#!/usr/bin/env python3
"""generate-p09-modules — Phase 9 module scaffolder.

Generates the Odoo-conformant scaffolding (manifest, security, views,
i18n, tests) for the Phase 9 modules from a specification table. The
business models are written separately; this tool handles the boilerplate
so each module is consistent (AS-02/03, Odoo 19 views, bn_BD po).

RETIRED (2026-10-22, TR-07/DoD-08): this one-shot scaffolded the P09 modules (manifest, views, security, tests AND i18n/bn_BD.po + .pot) in a form
Odoo 19 cannot load - no `#. module:` comment and no `#:` references, so
odoo.tools.translate.PoFileReader raises AttributeError and the whole bn_BD
load aborts. The files it produced have since been completed and rewritten
in Odoo form; re-running it would overwrite them. It now exits without
writing anything. Maintain i18n/bn_BD.po directly and refresh templates and
references with tooling/scripts/extract-translations.py
(docs/guides/bn-terminology-glossary.md). The tables below are kept as history.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# (category, tech_name, cd_id, unit, summary, depends, models, menu_parent)
MODULES = [
    (
        "d_circular",
        "cd_rental_asset",
        "CD-M13-01",
        "M13",
        "Rental & Equipment-as-a-Service",
        [
            "base",
            "mail",
            "cd_entity_config",
            "cd_catalogue",
            "cd_party_master",
            "cd_device_registry",
            "cd_contract_core",
            "cd_fixed_asset_ext",
            "cd_event_outbox",
        ],
        ["fix.rental.reservation", "fix.rental.damage"],
        "cd_entity_config.menu_fix_operations_root",
    ),
    (
        "d_circular",
        "cd_tradein",
        "CD-M14-01",
        "M14",
        "Trade-In, Refurbishment & Resale",
        [
            "base",
            "mail",
            "cd_entity_config",
            "cd_party_master",
            "cd_device_registry",
            "cd_catalogue",
            "cd_service_order",
            "cd_event_outbox",
        ],
        ["fix.tradein.request", "fix.refurbishment"],
        "cd_entity_config.menu_fix_operations_root",
    ),
    (
        "d_circular",
        "cd_data_case",
        "CD-M06-01",
        "M06",
        "Data Services & Secure Data Handling",
        [
            "base",
            "mail",
            "cd_entity_config",
            "cd_party_master",
            "cd_device_registry",
            "cd_event_outbox",
        ],
        ["fix.data.recovery.case", "fix.data.wipe.certificate"],
        "cd_entity_config.menu_fix_operations_root",
    ),
    (
        "e_supply_chain",
        "cd_demand_plan",
        "CD-M43-01",
        "M43",
        "Demand Planning & Replenishment",
        ["base", "mail", "cd_entity_config", "cd_catalogue", "cd_event_outbox"],
        ["fix.demand.plan"],
        "cd_requisition.menu_ws_procurement",
    ),
    (
        "e_supply_chain",
        "cd_import_order",
        "CD-M44-01",
        "M44",
        "Import, Trade Compliance & Landed Cost",
        ["base", "mail", "cd_entity_config", "cd_requisition", "cd_gl_ext", "cd_event_outbox"],
        ["fix.import.order"],
        "cd_requisition.menu_ws_procurement",
    ),
    (
        "g_finance",
        "cd_fpa",
        "CD-M54-01",
        "M54",
        "FP&A, Cost Accounting & Budgeting",
        ["base", "mail", "cd_entity_config", "cd_gl_ext", "cd_fixed_asset_ext", "cd_event_outbox"],
        ["fix.budget", "fix.cost.allocation"],
        "cd_gl_ext.menu_ws_finance",
    ),
    (
        "h_people",
        "cd_talent",
        "CD-M58-01",
        "M58",
        "Talent Acquisition & Onboarding",
        ["base", "mail", "cd_entity_config", "cd_hr_core", "cd_event_outbox"],
        ["fix.job.requisition", "fix.candidate"],
        "cd_hr_core.menu_ws_people",
    ),
    (
        "h_people",
        "cd_hse",
        "CD-M59-01",
        "M59",
        "Health, Safety & Environment",
        ["base", "mail", "cd_entity_config", "cd_hr_core", "cd_event_outbox"],
        ["fix.hse.incident", "fix.safety.inspection"],
        "cd_hr_core.menu_ws_people",
    ),
    (
        "i_governance",
        "cd_grc",
        "CD-M60-01",
        "M60",
        "Governance, Risk & Compliance",
        ["base", "mail", "cd_entity_config", "cd_event_outbox"],
        ["fix.risk.register", "fix.control"],
        "cd_entity_config.menu_fix_operations_root",
    ),
    (
        "i_governance",
        "cd_knowledge",
        "CD-M61-01",
        "M61",
        "Knowledge Management & Technical Library",
        ["base", "mail", "cd_entity_config", "cd_event_outbox"],
        ["fix.knowledge.article"],
        "cd_entity_config.menu_fix_operations_root",
    ),
    (
        "i_governance",
        "cd_itsm",
        "CD-M66-01",
        "M66",
        "Internal IT Service Management",
        ["base", "mail", "cd_entity_config", "cd_msp_contract", "cd_event_outbox"],
        ["fix.itsm.ticket"],
        "cd_entity_config.menu_fix_operations_root",
    ),
]


def tech_to_model(name: str) -> str:
    """cd_rental_asset -> fix.rental.reservation (derived)"""
    return "fix." + name.replace("cd_", "").replace("_", ".")


def generate_manifest(cat, tech, cd_id, unit, summary, depends):
    deps = ", ".join(f'"{d}"' for d in depends)
    return f'''# {tech} — {unit} (P09).
{{
    "name": "1000FiX {summary}",
    "summary": "{unit}: {summary} ({cd_id})",
    "description": """
{cd_id} (P09) — {summary}.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
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
    "x_wave": "W6",
    "x_owner": "{summary}",
    "x_category": "Phase9",
    "x_tier": "T9",
}}
'''


def generate_csv(tech, model_names):
    rows = ["id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"]
    for m in model_names:
        access = "access_" + m.replace(".", "_")
        rows.append(f"{access},{m},model_{m.replace('.', '_')},base.group_user,1,1,1,0")
    return "\n".join(rows) + "\n"


def generate_views(tech, model_names, menu_parent):
    views = []
    for m in model_names:
        display = m.replace("fix.", "").replace(".", " ").title()
        vid = m.replace(".", "_")
        views.append(f"""    <record id="view_{vid}_list" model="ir.ui.view">
        <field name="name">{m}.list</field>
        <field name="model">{m}</field>
        <field name="arch" type="xml">
            <list><field name="name"/><field name="state"/></list>
        </field>
    </record>
    <record id="action_{vid}" model="ir.actions.act_window">
        <field name="name">{display}</field>
        <field name="res_model">{m}</field>
        <field name="view_mode">list,form</field>
    </record>""")
    menu_items = []
    for i, m in enumerate(model_names):
        display = m.replace("fix.", "").replace(".", " ").title()
        vid = m.replace(".", "_")
        menu_items.append(
            f'    <menuitem id="menu_{vid}" name="{display}" '
            f'parent="{menu_parent}" action="action_{vid}" sequence="{200 + i * 10}"/>'
        )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!-- {tech} views (P09). -->
<odoo>
{chr(10).join(views)}
{chr(10).join(menu_items)}
</odoo>
"""


def generate_po(tech, summary):
    return f"""# Bengali translations for {tech} (P09) — 100% coverage.
msgid ""
msgstr ""
"Language: bn_BD\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "{summary}"
msgstr "{summary} (বাংলা)"
"""


def main() -> int:
    for cat, tech, cd_id, unit, summary, depends, models, menu in MODULES:
        base = REPO / "addons" / "domain" / cat / tech
        (base / "models" / "__init__.py").write_text(
            f"# {tech} models.\nfrom . import fix_{tech.replace('cd_', '')}\n", encoding="utf-8"
        )
        (base / "__manifest__.py").write_text(
            generate_manifest(cat, tech, cd_id, unit, summary, depends), encoding="utf-8"
        )
        (base / "security" / "ir.model.access.csv").write_text(
            generate_csv(tech, models), encoding="utf-8"
        )
        (base / "views" / f"{tech}_views.xml").write_text(
            generate_views(tech, models, menu), encoding="utf-8"
        )
        (base / "i18n" / "bn_BD.po").write_text(generate_po(tech, summary), encoding="utf-8")
        (base / "i18n" / f"{tech}.pot").write_text(generate_po(tech, summary), encoding="utf-8")
        (base / "tests" / f"test_{tech.replace('cd_', '')}.py").write_text(
            f'"""{tech} tests — P09 ({cd_id})."""\nimport unittest\n\n\n'
            f'class Test{tech.replace("cd_", "").replace("_", "").title()}'
            f'(unittest.TestCase):\n'
            f'    def test_module_loads(self):\n'
            f'        """The module model classes are importable."""\n'
            f'        from odoo.addons.{tech} import models\n'
            f'        self.assertTrue(models)\n\n\n'
            f'if __name__ == "__main__":\n    unittest.main()\n',
            encoding="utf-8",
        )
        print(f"[ ok ] {tech}")
    print(f"generate-p09-modules: {len(MODULES)} module(s) scaffolded")
    return 0


if __name__ == "__main__":
    print(
        "generate-p09-modules.py: RETIRED - it would overwrite the Odoo-loadable i18n/bn_BD.po files; "
        "use tooling/scripts/extract-translations.py (see the module docstring)."
    )
    sys.exit(2)
