# cd_warranty_claims controllers — the P08 Brand API surface (PP5).
#
# Serves the W4 OpenAPI contract: /brand/claims (list + decide),
# /brand/claims/status, /brand/reconciliation. Per-brand isolation is
# the FIRST rule of this surface: every read and write carries a
# brand_id filter — one brand never sees another's claims (EA-05
# hard-scoped; the portal cannot even ask for another brand).
from . import brand_api
