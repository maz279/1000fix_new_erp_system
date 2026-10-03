-- fact_service_orders — the service-delivery backbone fact (P07-M07-T04).
-- LB-06 (AR-001): the warehouse READS the replica; this model never writes
-- back to an OLTP table. Grain: one row per fix.service.order.
{{ config(materialized='table') }}

with orders as (
    select
        so.id                        as order_key,
        so.name                      as order_ref,
        so.order_category,
        so.service_type,
        so.state                     as order_state,
        so.is_rework,
        so.create_date::date         as opened_date,
        so.sla_resolution_deadline,
        so.sla_resolution_at,
        so.branch_id                 as branch_key,
        so.customer_id               as customer_key,
        so.device_id                 as device_key,
        so.technician_id             as technician_key
    from {{ source('oltp_replica', 'fix_service_order') }} so
)

select * from orders
