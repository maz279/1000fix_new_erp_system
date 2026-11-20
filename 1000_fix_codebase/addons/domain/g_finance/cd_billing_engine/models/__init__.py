# cd_billing_engine models.
# fix_ar_capture (M20 capture pass 2) extends the receipt, the allocation and
# the dunning run: it imports fix_billing_engine itself, so the sort order of
# this tuple cannot load it before the models it extends.
from . import (
    account_move_mushak,
    fix_a04_claim_consumer,
    fix_a04_warranty_subscription_billing,
    fix_ar_capture,
    fix_ar_engine,
    fix_ar_impairment,
    fix_ar_invoice_document,
    fix_billing_engine,
    fix_contract_billing_walker,
    fix_credit_limit_change,
    fix_finance_approval,
    fix_order_settlement,
    fix_part_exemption_billing,
    fix_party_merge_consumer,
    fix_payment_method,
    fix_tds_certificate,
    fix_vds_certificate,
    fix_warranty_remittance,
)

# A04 ERP audit (20 Nov 2026, B2): extends the invoice, the credit note and
# the contract billing period defined above, so it loads after them.
# isort: split
from . import fix_a04_contract_billing

# NOTE: the bounced-cheque AR re-open (A08 cheque.bounced consumer) lives in
# cd_cash_position/models/fix_ar_cheque_bounce.py — it extends fix.ar.receipt
# but adds a Many2one to fix.cheque, so it must load beside the cheque
# register; a dependency from here onto cash closed the module cycle
# billing -> cash -> storefront -> billing.
