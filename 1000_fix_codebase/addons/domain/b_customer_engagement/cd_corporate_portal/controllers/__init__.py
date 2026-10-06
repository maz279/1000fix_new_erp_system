# cd_corporate_portal controllers — the P04 API surface (PP3).
#
# Serves the W4 OpenAPI contract (contracts/openapi/w4-portals.json):
# /corporate/estate, /corporate/invoices/consolidated,
# /corporate/service-requests. All monetary values are backend-computed
# strings (AS-10/BN-007); the portal renders, never calculates (AS-09).
from . import corporate_api
