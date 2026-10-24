# cd_design_tokens — R1 design-token realisation (P04-M07-T07, P04-M06-T04).

# DSY-01: one token source, one component contract, five realisations, one
# conformance suite. This module is the R1 (OWL 2 / Odoo Web) carrier: it
# contributes GENERATED SCSS to the web bundle. It authors no design value —
# every variable in static/src/tokens.scss is generated from
# libs/ts/ui/src/tokens/tokens.json by tooling/generators/generate-design-tokens.py.
#
# Register note: BE-005 §6 has no design-system row. CR raised:
# docs/p04/CR-cd-register-design-tokens.md — until the Change Board rules,
# this manifest deliberately carries no CD id (FF-16 honesty over invention).
{
    "name": "1000FiX Design Tokens (R1)",
    "summary": "Generated DTCG design tokens + W1 component styles for Odoo Web (DSY-01)",
    "description": """
R1 realisation of the design-token system (UX-001 §3.1, §5.3).

static/src/tokens.scss and static/src/tokens.css are GENERATED — never edited:
  py tooling/generators/generate-design-tokens.py

The W1 component partials under static/src/components/ consume ONLY tokens
(CFM-01: no raw colour/size literals) and are covered by the cross-runtime
conformance suite tooling/design-system/conformance.py (CFM-01…CFM-05).
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/DesignSystem",
    "depends": ["base", "web"],
    "assets": {
        "web.assets_backend": [
            "cd_design_tokens/static/src/tokens.scss",
            "cd_design_tokens/static/src/components/*.scss",
        ],
        "web.report_assets_common": [
            "cd_design_tokens/static/src/tokens.css",
        ],
    },
    "installable": True,
    "application": False,
    "x_module_id": "DSY-01",
    "x_cd_id": "CD-M30-05",
    "x_wave": "W1",
    "x_owner": "Experience",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
    "x_generated_assets": [
        "static/src/tokens.scss",
        "static/src/tokens.css",
    ],
}
