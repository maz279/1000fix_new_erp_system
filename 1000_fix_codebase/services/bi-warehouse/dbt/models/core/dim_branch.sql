-- dim_branch — Branch dimension conformed to M30 (R05-M04-T02).
-- LB-06: Analytical read from read replica.
{{ config(materialized='table') }}

with branches as (
    select
        b.id                                as branch_key,
        b.code                              as branch_code,
        b.name                              as branch_name,
        coalesce(b.division, 'Dhaka')       as division_name,
        coalesce(b.district, 'Dhaka')       as district_name,
        coalesce(b.zone, 'Central')         as zone_name,
        b.operating_unit_id                 as operating_unit_key,
        b.company_id                        as company_key,
        coalesce(b.active, true)            as is_active,
        coalesce(b.is_hub, false)           as is_regional_hub,
        b.create_date::date                 as opened_date
    from {{ source('oltp_replica', 'fix_branch') }} b
)

select * from branches
