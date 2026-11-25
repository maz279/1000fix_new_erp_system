# MOVED: the M41 warehouse execution models are defined in
#   addons/domain/e_supply_chain/cd_inventory/models/fix_wms_ops.py
# because cd_inventory depends on cd_wms_structure (declaring the fix.spare.part
# foreign key here would create a module dependency cycle). This file is kept
# only as a pointer; it defines no models and is not imported.
