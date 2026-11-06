# cd_billing_engine models.
from . import (
    account_move_mushak,
    fix_a04_claim_consumer,
    fix_ar_engine,
    fix_ar_impairment,
    fix_billing_engine,
    fix_contract_billing_walker,
    fix_finance_approval,
    fix_party_merge_consumer,
    fix_vds_certificate,
)

# NOTE: the bounced-cheque AR re-open (A08 cheque.bounced consumer) lives in
# cd_cash_position/models/fix_ar_cheque_bounce.py — it extends fix.ar.receipt
# but adds a Many2one to fix.cheque, so it must load beside the cheque
# register; a dependency from here onto cash closed the module cycle
# billing -> cash -> storefront -> billing.
