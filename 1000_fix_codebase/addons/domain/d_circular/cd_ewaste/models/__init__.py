# cd_ewaste models.
# M18 capture pass 2 (19 Nov 2026): imported after the base models, it extends them.
# A05 ERP build S3 (20 Nov 2026): fix_s3_a05_build is imported last (it extends all).
from . import (
    fix_ewaste,
    fix_ewaste_compliance,
    fix_ewaste_ops,
    fix_m18_capture,
    fix_s3_a05_build,
)
