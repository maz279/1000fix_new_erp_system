# cd_vendor_portal controllers — the P05 API surface (PP5).
#
# Serves the W4 OpenAPI contract: /vendor/purchase-orders (list +
# acknowledge + delivery confirm) and /vendor/invoices (list + submit
# feeding the three-way match). EA-05 record rules scope a vendor to
# their own rows; every write rides the owning model's action methods.
from . import vendor_api
