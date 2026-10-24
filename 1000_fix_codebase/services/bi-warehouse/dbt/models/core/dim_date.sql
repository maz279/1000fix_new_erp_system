-- dim_date — Conformed calendar dimension (Asia/Dhaka, BD holidays) (R05-M04-T02).
-- LB-06 (AR-001): Conformed dimension over read replica.
{{ config(materialized='table') }}

with date_spine as (
    select
        datum::date as calendar_date,
        to_char(datum, 'YYYYMMDD')::integer as date_key,
        extract(year from datum)::integer as year_number,
        extract(quarter from datum)::integer as quarter_number,
        extract(month from datum)::integer as month_number,
        to_char(datum, 'TMMonth') as month_name,
        extract(day from datum)::integer as day_of_month,
        extract(isodow from datum)::integer as day_of_week,
        to_char(datum, 'TMDay') as day_name,
        -- Bangladesh statutory weekend: Friday (5) and Saturday (6)
        case when extract(isodow from datum) in (5, 6) then true else false end as is_weekend,
        -- Statutory Bangladesh holidays
        case
            when to_char(datum, 'MMDD') = '0221' then 'Language Martyrs Day'
            when to_char(datum, 'MMDD') = '0326' then 'Independence Day'
            when to_char(datum, 'MMDD') = '0414' then 'Bengali New Year (Pohela Boishakh)'
            when to_char(datum, 'MMDD') = '0501' then 'May Day'
            when to_char(datum, 'MMDD') = '1216' then 'Victory Day'
            else null
        end as bd_holiday_name,
        case
            when to_char(datum, 'MMDD') in ('0221', '0326', '0414', '0501', '1216') then true
            else false
        end as is_bd_holiday
    from generate_series('2025-01-01'::date, '2030-12-31'::date, '1 day'::interval) datum
)

select
    date_key,
    calendar_date,
    year_number,
    quarter_number,
    month_number,
    month_name,
    day_of_month,
    day_of_week,
    day_name,
    is_weekend,
    is_bd_holiday,
    bd_holiday_name,
    case when is_weekend or is_bd_holiday then false else true end as is_business_day
from date_spine
