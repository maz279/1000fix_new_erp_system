# cd_customer_portal controllers — the P01 API surface (PP5).
#
# Serves the W4 OpenAPI contract (contracts/openapi/w4-portals.json):
# /customer/devices, /customer/bookings, /customer/tracking,
# /customer/estimates, /customer/consent, /customer/ownership/transfer.
# All validation is server-side (AS-09); monetary values are
# backend-computed BN-007 strings (AS-10).
from . import customer_api
