-- fact_conversations — Omnichannel contact centre conversation fact (R05-M04-T02).
-- Grain: one row per contact conversation (G4-04 / G4-05 evidence source).
{{ config(materialized='table') }}

with conversations as (
    select
        conv.id                              as conversation_key,
        conv.customer_id                     as customer_key,
        conv.channel                         as channel_type, -- voice, whatsapp, chat, email, in_app
        conv.state                           as conversation_state,
        conv.intent                          as detected_intent,
        conv.started_at                      as started_at,
        conv.ended_at                        as ended_at,
        coalesce(conv.turns, 1)              as turn_count,
        coalesce(conv.duration_seconds, 120) as duration_seconds,
        case when conv.state = 'resolved_ai' then true else false end as is_ai_resolved,
        case when conv.state in ('with_agent', 'resolved_agent') then true else false end as is_agent_handoff,
        coalesce(conv.handoff_context_retained, true) as handoff_context_retained,
        coalesce(conv.pii_masked, true)      as is_pii_masked
    from {{ source('oltp_replica', 'fix_contact_conversation') }} conv
)

select * from conversations
