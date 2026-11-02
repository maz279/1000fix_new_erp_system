# cd_wms_structure models.
# The M41 execution models (slot/dock/put-away/wave/carton/stage/task/floor
# count/template/station) live in cd_inventory/models/fix_wms_ops.py: this
# module loads BEFORE cd_inventory (cd_inventory depends on it), so a
# fix.spare.part foreign key cannot be declared here without a module cycle.
from . import fix_wms_structure
