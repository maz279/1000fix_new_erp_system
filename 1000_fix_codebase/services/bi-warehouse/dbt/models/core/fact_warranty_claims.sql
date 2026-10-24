-- fact_warranty_claims — Brand warranty claims fact (R05-M04-T02).
-- Grain: one row per claim (G4-01 / G4-02 evidence source).
{{ config(materialized='table') }}

with claims as (
    select
        c.id                                 as claim_key,
        c.name                               as claim_number,
        c.service_order_id                   as order_key,
        c.brand_id                           as brand_key,
        c.branch_id                          as branch_key,
        c.state                              as claim_state,
        c.claim_amount                       as claim_amount_bdt,
        c.approved_amount                    as approved_amount_bdt,
        c.create_date                        as created_at,
        c.submitted_date                     as submitted_at,
        c.approved_date                      as approved_at,
        c.hours_to_create                    as hours_to_create,
        c.hours_to_submit                    as hours_to_submit,
        coalesce(c.is_auto_created, true)    as is_auto_created,
        case when c.hours_to_create <= 24.0 then true else false end as created_within_24h,
        case when c.hours_to_submit <= 72.0 then true else false end as submitted_within_72h,
        coalesce(c.first_submission_approved, true) as first_submission_approved,
        coalesce(c.evidence_complete, true)  as evidence_complete_at_submission
    from {{ source('oltp_replica', 'fix_warranty_claim') }} c
)

select * from claims
