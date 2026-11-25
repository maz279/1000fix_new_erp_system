# cd_finance_nav — A08 Finance & Treasury navigation bridge (A08 reorg).
#
# Attaches ACTION-BACKED menu children to the P03 workspace's generated A08
# module menus (from cd_p03_portal) for the real g_finance models. Lives as
# its own module because the actions reference models owned by the g_finance
# addons: depending on them guarantees every res_model exists in the
# registry when this module's data loads (a data file inside cd_p03_portal
# itself would parse before those models are set up).
{
    "name": "Finance Navigation Bridge (A08)",
    "version": "19.0.1.0.0",
    "category": "Platform/Portal",
    "author": "1000 FiX Services Ltd",
    "license": "LGPL-3",
    "depends": [
        "cd_p03_portal",
        "cd_gl_ext",
        "cd_billing_engine",
        "cd_cash_position",
        "cd_tax_engine_bd",
        "cd_ap_ext",
        "cd_settlement_ext",
        "cd_fixed_asset_ext",
        "cd_fpa",
        "cd_subscription",
    ],
    "data": [
        "views/finance_nav_menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "x_cd_id": "CD-FINNAV-01",
    "x_module_id": "P03",
    "x_wave": "PP2",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
