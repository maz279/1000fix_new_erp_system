-- fact_nps — Customer satisfaction & Net Promoter Score fact (R05-M04-T02).
-- Grain: one row per survey response (KPI-021 evidence source).
{{ config(materialized='table') }}

with surveys as (
    select
        s.id                                 as survey_key,
        s.service_order_id                   as order_key,
        s.customer_id                        as customer_key,
        s.channel                            as channel,
        s.score                              as nps_score, -- 0 to 10
        case
            when s.score >= 9 then 'promoter'
            when s.score >= 7 then 'passive'
            else 'detractor'
        end as nps_category,
        s.create_date::date                  as response_date,
        to_char(s.create_date, 'YYYYMMDD')::integer as date_key,
        coalesce(s.has_complaint_escalation, false) as is_complaint_escalated
    from {{ source('oltp_replica', 'fix_customer_survey') }} s
)

select * from surveys
