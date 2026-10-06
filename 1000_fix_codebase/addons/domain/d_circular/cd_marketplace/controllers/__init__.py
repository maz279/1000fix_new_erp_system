# cd_marketplace controllers — the P07 Seller API surface (PP5).
#
# Serves the W4 OpenAPI contract: /seller/dashboard, /seller/orders,
# /seller/quotes, /seller/scorecard. Settlement statements live with the
# ledger model in cd_settlement_ext (FL-03: no duplicated surface).
from . import seller_api
