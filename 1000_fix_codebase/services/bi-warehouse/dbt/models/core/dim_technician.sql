-- dim_technician — Technician dimension with competency & branch attributes (R05-M04-T02).
-- LB-06: Downstream analytical read from read replica.
{{ config(materialized='table') }}

with technicians as (
    select
        t.id                                 as technician_key,
        t.name                               as technician_name,
        t.branch_id                          as branch_key,
        coalesce(t.skill_tier, 'level_1')    as skill_tier, -- level_1..level_4
        coalesce(t.specialization, 'it')     as specialization, -- it, appliance, mobile, board
        coalesce(t.certification_count, 1)   as active_certifications,
        coalesce(t.is_active, true)          as is_active,
        t.hire_date::date                    as hire_date
    from {{ source('oltp_replica', 'fix_technician') }} t
)

select * from technicians
