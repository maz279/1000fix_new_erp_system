# cd_document_core — M24-core document kernel (P03-M07; M24 completion P06-M08-T01)
# M24 capture pass 2 (19 Nov 2026): fix_document_capture extends the models of
# the other files and imports them itself, so the sorted order is safe
from . import (
    fix_disposal,
    fix_document,
    fix_document_capture,
    fix_document_handoffs,
    fix_document_template,
    fix_legal_hold,
    fix_retention_class,
    ir_attachment_ext,
    res_users_tiers,
)
