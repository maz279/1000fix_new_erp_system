# cd_d365_chrome — the Dynamics-365/Fluent skin over the native Odoo
# webclient chrome (navbar, dropdowns) and the Discuss chat app, so the
# deliberately-native surfaces (Team Chat at /odoo/action-mail.action_discuss
# and any backend view reached from it) carry the same identity as the P03
# D365 Operations Workspace.
#
# CFM-01 contract, same as cd_design_tokens components: SCSS consumes ONLY
# the generated token variables — no raw colour or size literals — so the
# skin re-skins itself when tokens.json changes.
#
# Register note: like cd_design_tokens before CR ruling (FF-16 honesty over
# invention), this manifest deliberately carries no CD id.
{
    "name": "1000FiX D365 Chrome Skin (R1)",
    "summary": "Fluent/D365 skin for the Odoo webclient chrome + Discuss app (DSY realisation)",
    "description": """
Restyles the native Odoo backend chrome and the Discuss chat app to the
estate's Dynamics-365/Fluent identity (UX-001): white command bar with teal
accents, D365 sitemap-style channel rail, Fluent composer with focus ring,
token-driven throughout (CFM-01).

Scope is deliberately CHROME + DISCUSS ONLY: business screens render the
D365 workspace (cd_p03_portal); native views remain the substrate. The
skin changes no functionality and no vendor file (FORKS.yaml stays empty).
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/DesignSystem",
    "depends": ["base", "web", "mail", "cd_design_tokens"],
    "assets": {
        "web.assets_backend": [
            "cd_d365_chrome/static/src/chrome.scss",
            "cd_d365_chrome/static/src/discuss.scss",
        ],
    },
    "installable": True,
    "application": False,
    "x_owner": "Experience",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
