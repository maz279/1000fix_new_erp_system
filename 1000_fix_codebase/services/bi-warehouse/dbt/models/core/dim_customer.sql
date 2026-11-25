-- dim_customer — Party dimension for customer roles (R05-M04-T02).
-- NFR-086c: PII minimised / pseudonymised — zero classified/S3 data in warehouse.
{{ config(materialized='table') }}

with customers as (
    select
        p.id                                  as customer_key,
        p.ref                                 as customer_ref,
        -- Non-identifying category & geographic segmentation
        coalesce(p.customer_tier, 'standard') as customer_tier,
        coalesce(p.customer_type, 'retail')   as customer_type, -- retail, corporate, brand
        coalesce(p.city, 'Dhaka')             as city,
        coalesce(p.zone, 'Central')           as zone,
        p.company_id                          as company_key,
        -- Pseudonymised identifier hash for longitudinal cohort analytics (PDPA compliant)
        md5(coalesce(p.phone, '') || coalesce(p.email, '') || p.id::text) as pseudonym_hash,
        coalesce(p.active, true)              as is_active,
        p.create_date::date                   as registration_date
    from {{ source('oltp_replica', 'res_partner') }} p
    where p.customer_rank > 0 or p.is_company = true
)

select * from customers
