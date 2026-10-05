# cd_catalogue — M37 Product & Service Catalogue kernel (P03-M06).
# The catalogue on product.template with service kits, rental SKUs,
# refurbishment grades, and brand/model masters. AS-10: every price is
# fields.Monetary with explicit currency_id — never Float.
{
    "name": "1000FiX Catalogue Kernel",
    "summary": "Catalogue items, service kits, rental SKUs, refurb grades, brand/model masters (M37)",
    "description": """
CD-M37-nn: the catalogue kernel (M37).

Owns:
- fix.catalogue.item (extends product.template with catalogue metadata)
- fix.service.kit (a service defined as a bundle of parts + labour + time)
- fix.rental.sku (rental SKU model for M13, built here so M13 composes)
- fix.refurb.grade (refurbishment grades for M14)
- fix.brand (brand master — 17+ brand partners)
- fix.device.model (device model master referenced by M17)

AS-10 (FF-22): every price is fields.Monetary with explicit currency_id.
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/Catalogue",
    "depends": ["base", "mail", "product", "cd_entity_config", "cd_rbac_ext",
                 "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "data/fix_refurb_grades.xml",
             "views/fix_catalogue_views.xml",
             "views/fix_catalogue_workspace_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M37-01",
    "x_module_id": "M37",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
