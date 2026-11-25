-- fact_invoices — AR invoice and VAT mushak-paired fact (R05-M04-T02).
-- Grain: one row per AR invoice.
{{ config(materialized='table') }}

with invoices as (
    select
        inv.id                               as invoice_key,
        inv.name                             as invoice_number,
        inv.service_order_id                 as order_key,
        inv.partner_id                       as customer_key,
        inv.branch_id                        as branch_key,
        inv.invoice_date::date               as invoice_date,
        inv.to_char(inv.invoice_date, 'YYYYMMDD')::integer as date_key,
        inv.amount_untaxed                   as subtotal_bdt,
        inv.amount_tax                       as vat_amount_bdt,
        inv.amount_total                     as total_amount_bdt,
        inv.state                            as invoice_state,
        inv.payment_state                    as payment_state,
        inv.mushak_6_3_number                as mushak_6_3_ref,
        inv.is_auto_generated                as is_auto_generated,
        inv.auto_match_reconciled            as is_bank_auto_matched
    from {{ source('oltp_replica', 'account_move') }} inv
    where inv.move_type = 'out_invoice'
)

select * from invoices
