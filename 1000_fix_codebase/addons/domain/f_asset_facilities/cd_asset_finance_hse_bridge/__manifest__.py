# cd_asset_finance_hse_bridge — A07 P1 hand-offs from M17/M45/M46/M47 into
# M09, M49, M52, M59 and M60 (A07 audit 2026-11-04, report §6 P1).
{
    "name": "1000FiX Asset Finance & HSE Bridge",
    "summary": "A07 P1 hand-offs: asset capitalisation/disposal requests (M49), IFRS 16 draft "
    "leases (M19/M49), pending cost entries (M52), HSE cases and hazards (M59), one risk "
    "entry per subject (M60), warranty-claim re-checks (M09)",
    "description": """
A07 P1 (2026-11-04), report §6 "Event consumers". The asset modules publish
their hand-off events; this bridge consumes them. Nothing here posts a journal
entry or closes a case: each consumer creates a DRAFT or PENDING row that a
person in the target module confirms.

- M49: equipment / vehicle / site-asset acquisition and write-off become a
  pending capitalisation or disposal request; finance accepts it into a
  draft fixed asset or a draft disposal (M49's own approve/post follow)
- M19/M49 IFRS 16: lease.recorded / lease.extract_published keep a DRAFT
  fix.lease in step with the M47 lease until finance commences it; a later
  extract raises a modification item instead
- M52: closed facility work orders, recorded fuel and completed vehicle
  services become pending cost entries by branch, matched to the vendor bill
- M59: an injury at a site or in a vehicle accident opens an HSE case with
  the BLA s.80 clock, and the case reference goes back to the M47 incident;
  unfit safety equipment raises a hazard
- M60: a lapsed site licence, driver licence or vehicle document raises or
  updates ONE open risk entry per subject
- M09: a device whose owner or warranty changed puts its open warranty
  claims on a re-check before they are submitted

A separate module on purpose (P0 lesson, cd_vehicle_dispatch): the asset
modules keep their dependencies, and a server that has not installed this
bridge never loads it.
""",
    "version": "19.0.0.1.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Asset & Facilities",
    "depends": [
        "cd_event_outbox",
        "cd_entity_config",
        "cd_device_registry",
        "cd_equipment_register",
        "cd_vehicle_ext",
        "cd_facility",
        "cd_fixed_asset_ext",
        "cd_ap_ext",
        "cd_hse",
        "cd_grc",
        "cd_warranty_claims",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/fix_bridge_rules.xml",
        "data/ir_sequence.xml",
        "data/ir_config_parameter.xml",
        "data/fix_event_consumers.xml",
        "views/fix_bridge_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "x_module_id": "M47",
    "x_wave": "W7",
    "x_owner": "Asset & Facilities",
    "x_category": "F_Asset_and_Facilities",
    "x_tier": "T10",
}
