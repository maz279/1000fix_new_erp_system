-- dim_device — Device dimension (model, brand, type, warranty status) (R05-M04-T02).
-- LB-06: Conformed analytical view from read replica.
{{ config(materialized='table') }}

with devices as (
    select
        d.id                                 as device_key,
        d.name                               as device_ref,
        coalesce(b.name, 'Generic')          as brand_name,
        coalesce(d.device_type, 'it')        as device_type, -- it, appliance, mobile
        coalesce(d.model_name, 'Standard')   as model_name,
        md5(coalesce(d.serial_number, d.id::text)) as serial_hash,
        coalesce(d.warranty_status, 'out_of_warranty') as warranty_status,
        d.warranty_expiry_date,
        coalesce(d.active, true)             as is_active,
        d.create_date::date                  as registered_date
    from {{ source('oltp_replica', 'fix_device') }} d
    left join {{ source('oltp_replica', 'fix_brand') }} b on d.brand_id = b.id
)

select * from devices
