# cd_warranty_claims models.
# fix_warranty_recall_consumer must load after fix_warranty_ops (it extends
# fix.warranty.recall): the import order below is load order.
from . import fix_brand_ext, fix_warranty_claims, fix_warranty_ops

# isort: split

from . import fix_warranty_recall_consumer  # A10 P1-7: bulletin.distributed consumer

# isort: split

# M09 capture audit, second pass (2026-11-18): imported last - it extends
# fix.warranty.claim, .product and fix.claim.appeal defined above.
from . import fix_m09_capture
