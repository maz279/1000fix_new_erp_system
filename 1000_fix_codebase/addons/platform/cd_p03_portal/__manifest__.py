# cd_p03_portal — the Admin Operations Portal P03 (R1 OWL, PP2).
#
# The 823-screen back-office surface as a registry-driven workspace: menus
# generated from contracts/nav/registry.json, an OWL workspace client action
# (archetype A2), the Report Center (A10/A11), Tell-ME search (A13) and the
# four persona role centers (A1).
{
    "name": "P03 Admin Operations Portal",
    "version": "19.0.1.5.1",
    "category": "Platform/Portal",
    "author": "1000FiX Services Ltd",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
        "cd_entity_config",
        "cd_rbac_ext",
        "cd_design_tokens",
        "cd_service_order",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/p03_menus.xml",
        "views/p03_actions.xml",
        "views/p03_service_order_details.xml",
        "views/p03_login_templates.xml",
        "views/ir_cron_report_delivery.xml",
        # A02 ERP audit X-17: the A02 printable documents (counter receipt, wipe
        # certificate, field service report, waybill, workshop job card)
        "report/p03_a02_documents.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cd_p03_portal/static/src/**/*",
        ],
    },
    "installable": True,
    "application": True,
    "x_cd_id": "CD-P03-01",
    "x_module_id": "P03",
    "x_wave": "PP2",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
    "x_generated_assets": [
        "views/p03_menus.xml",
    ],
}
