/** @odoo-module **/
/* A03 · Customer Experience — M27 Contact Centre (Hotline 16743).
 * Rebuilt 2026-10-31: Full Microsoft Dynamics 365 multi-tab form architecture
 * across all 7 in-workspace forms with zero Bengali/English mixing, comprehensive
 * data capture, BTRC 180-day audio retention compliance, and real-time agent balancing.
 */

export const MODULE = {
  area: 'A03', code: 'M27', en: 'Contact Centre (16743)', title: 'M27 · Contact Centre (16743)',
  bn: 'কন্টাক্ট সেন্টার ১৬৭৪৩', icon: '🎧',
  desc: 'Omnichannel contact centre, SIP telephony (Hotline 16743), WhatsApp, real-time queues, skills routing, IVR trees, dispositions, QA scorecards, and WFM rosters.',
  kpis: [
    { l: 'Service Level (20s)', m: 'service_level_pct', suffix: '%' },
    { l: 'Average Handle Time', m: 'avg_handle_time_sec', suffix: 's' },
    { l: 'First Contact Resolution', m: 'fcr_rate', suffix: '%' },
    { l: 'Abandonment Rate', m: 'abandonment_rate', suffix: '%' },
    { l: 'Active Calls', m: 'active_calls' },
    { l: 'Queued Contacts', m: 'queued_contacts' }
  ],
  groups: [
    { en: 'Unified Queue', bn: 'একত্র সারি', screens: [
      { id: 'M27-queue', en: 'Unified Queue Board', bn: 'একত্র সারি বোর্ড', t: 'g' },
      { id: 'M27-conversations', en: 'Call & Chat Conversations', bn: 'কথোপকথন', t: 'g' },
      { id: 'M27-routing', en: 'Skills Routing', bn: 'স্কিল রাউটিং', t: 'g' }
    ]},
    { en: 'Agent Desktop (P10)', bn: 'এজেন্ট ডেস্কটপ', screens: [
      { id: 'M27-desktop', en: 'Agent Desktop Preview', bn: 'এজেন্ট ডেস্কটপ', t: 'r' },
      { id: 'M27-states', en: 'Agent States & Wrap-Up', bn: 'এজেন্ট অবস্থা', t: 'r' },
      { id: 'M27-dispositions', en: 'Disposition Codes', bn: 'নিষ্পত্তি কোড', t: 'g' }
    ]},
    { en: 'Channels', bn: 'চ্যানেল', screens: [
      { id: 'M27-voice', en: 'Voice & IVR Flows', bn: 'ভয়েস ও আইভিআর', t: 'g' },
      { id: 'M27-digital', en: 'WhatsApp / Chat / Email / Social', bn: 'ডিজিটাল চ্যানেল', t: 'r' },
      { id: 'M27-outbound', en: 'Outbound Campaigns', bn: 'আউটবাউন্ড ক্যাম্পেইন', t: 'g' }
    ]},
    { en: 'Notification Hub', bn: 'নোটিফিকেশন হাব', screens: [
      { id: 'M27-templates', en: 'Notification Templates', bn: 'বিজ্ঞপ্তি টেমপ্লেট', t: 'g' },
      { id: 'M27-delivery', en: 'Delivery Tracking & Retry', bn: 'ডেলিভারি ট্র্যাকিং', t: 'r' },
      { id: 'M27-preferences', en: 'Consent & DND', bn: 'সম্মতি ও ডিএনডি', t: 'r' }
    ]},
    { en: 'Quality & WFM', bn: 'গুণগত মান ও ওয়ার্কফোর্স', screens: [
      { id: 'M27-qa', en: 'QA Evaluations', bn: 'কিউএ মূল্যায়ন', t: 'g' },
      { id: 'M27-wfm', en: 'Forecast & Roster', bn: 'পূর্বাভাস ও রোস্টার', t: 'g' }
    ]},
    { en: 'Contact Centre Configuration', bn: 'কনফিগারেশন ও ফর্ম', screens: [
      { id: 'M27-queues', en: 'Queue Definitions', bn: 'কিউ সংজ্ঞা', t: 'g' },
      { id: 'M27-form-call', en: 'Call Record & Interaction', bn: 'কল রেকর্ড ফর্ম', t: 'f' },
      { id: 'M27-form-ivr', en: 'IVR Flow', bn: 'আইভিআর ফ্লো ফর্ম', t: 'f' },
      { id: 'M27-form-template', en: 'Notification Template', bn: 'টেমপ্লেট ফর্ম', t: 'f' },
      { id: 'M27-form-disposition', en: 'Disposition Code', bn: 'ডিসপোজিশন ফর্ম', t: 'f' },
      { id: 'M27-form-outbound', en: 'Outbound List', bn: 'আউটবাউন্ট ফর্ম', t: 'f' },
      { id: 'M27-form-queue', en: 'Queue Definition', bn: 'কিউ ফর্ম', t: 'f' },
      { id: 'M27-form-qa', en: 'QA Evaluation', bn: 'কিউএ ফর্ম', t: 'f' },
      { id: 'M27-form-wfm', en: 'Roster Shift', bn: 'শিফট ফর্ম', t: 'f' }
    ]},
    { en: 'Contact Centre Reports', bn: 'রিপোর্ট', screens: [
      { id: 'M27-rpt-channelmix', en: 'Channel Mix & Volumes', bn: 'চ্যানেল মিশ্রণ ও ভলিউম', t: 'r' },
      { id: 'M27-rpt-slinterval', en: 'Service Level by Interval', bn: 'সময়-অন্তরালে সার্ভিস লেভেল', t: 'r' },
      { id: 'M27-rpt-ahtfcr', en: 'AHT & FCR by Disposition', bn: 'ডিসপোজিশন অনুযায়ী AHT ও FCR', t: 'r' },
      { id: 'M27-rpt-delivery', en: 'Notification Delivery by Channel', bn: 'চ্যানেল অনুযায়ী ডেলিভারি', t: 'r' },
      { id: 'M27-rpt-qadist', en: 'QA Score Distribution', bn: 'কিউএ স্কোর বিতরণ', t: 'r' }
    ]},
    { en: 'Message Delivery (S1)', bn: 'বার্তা ডেলিভারি', screens: [
      { id: 'M27-deliveries', en: 'Delivery Log & Retry', bn: 'ডেলিভারি লগ', t: 'g' },
      { id: 'M27-providers', en: 'Delivery Providers & Tariffs', bn: 'প্রোভাইডার ও ট্যারিফ', t: 'g' },
      { id: 'M27-form-provider', en: 'Delivery Provider', bn: 'প্রোভাইডার ফর্ম', t: 'f' }
    ]},
    { en: 'Unified Routing (S3)', bn: 'ইউনিফাইড রাউটিং', screens: [
      { id: 'M27-workstreams', en: 'Workstreams', bn: 'ওয়ার্কস্ট্রিম', t: 'g' },
      { id: 'M27-form-workstream', en: 'Workstream', bn: 'ওয়ার্কস্ট্রিম ফর্ম', t: 'f' },
      { id: 'M27-workitems', en: 'Routed Work Items', bn: 'রাউট করা কাজ', t: 'g' },
      { id: 'M27-bullseye', en: 'Bullseye Rings', bn: 'বুলসআই রিং', t: 'g' }
    ]},
    { en: 'Capacity & Presence (S4)', bn: 'সক্ষমতা ও উপস্থিতি', screens: [
      { id: 'M27-capacity', en: 'Capacity Profiles', bn: 'সক্ষমতা প্রোফাইল', t: 'g' },
      { id: 'M27-form-capacity', en: 'Capacity Profile', bn: 'সক্ষমতা ফর্ম', t: 'f' },
      { id: 'M27-presence', en: 'Live Agent Presence', bn: 'এজেন্ট উপস্থিতি', t: 'g' },
      { id: 'M27-presence-statuses', en: 'Presence Statuses', bn: 'উপস্থিতি অবস্থা', t: 'g' },
      { id: 'M27-presence-history', en: 'Presence History', bn: 'উপস্থিতির ইতিহাস', t: 'g' }
    ]},
    { en: 'Agent Productivity', bn: 'এজেন্ট উৎপাদনশীলতা', screens: [
      { id: 'M27-scripts', en: 'Agent Scripts', bn: 'এজেন্ট স্ক্রিপ্ট', t: 'g' },
      { id: 'M27-form-script', en: 'Agent Script', bn: 'স্ক্রিপ্ট ফর্ম', t: 'f' },
      { id: 'M27-macros', en: 'Macros', bn: 'ম্যাক্রো', t: 'g' },
      { id: 'M27-knowledge', en: 'Knowledge Bindings', bn: 'নলেজ বাইন্ডিং', t: 'g' },
      { id: 'M27-script-adherence', en: 'Script Adherence', bn: 'স্ক্রিপ্ট অনুসরণ', t: 'g' }
    ]},
    { en: 'Quality at Scale & Adherence', bn: 'গুণমান ও অনুসরণ', screens: [
      { id: 'M27-rubrics', en: 'QA Rubrics', bn: 'কিউএ রুব্রিক', t: 'g' },
      { id: 'M27-form-rubric', en: 'QA Rubric', bn: 'রুব্রিক ফর্ম', t: 'f' },
      { id: 'M27-adherence', en: 'WFM Adherence', bn: 'ডব্লিউএফএম অনুসরণ', t: 'g' }
    ]}
  ],
  reports: ['Channel Mix & Volumes', 'Service Level by Interval', 'AHT & FCR by Disposition', 'Notification Delivery by Channel', 'QA Score Distribution'],
  forms: ['IVR Flow', 'Notification Template', 'Disposition Code', 'Outbound List', 'Call Conversation', 'Queue Definition', 'QA Evaluation', 'Roster Shift', 'Delivery Provider', 'Routing Workstream', 'Capacity Profile', 'Agent Script', 'QA Rubric'],
  cross: ['M32 AI handoff', 'M33 Customer-360 pop', 'M01 create SO in-conversation', 'M55 agent roster'],
  freg: {
    src: 87,
    sub: [
      ['1', 'Voice & IVR', 12, { model: 'fix.cc.ivr.flow', cols: ['name', 'active', 'channel', 'version', 'flow_json'], screens: ['M27-voice'], reports: ['Channel Mix & Volumes'], forms: ['IVR Flow'] }],
      ['2', 'Digital Channels', 12, { model: 'fix.conversation', cols: ['started_at', 'channel', 'contact_identity', 'customer_id', 'state'], screens: ['M27-digital', 'M27-rpt-channelmix', 'M27-conversations'], reports: ['Channel Mix & Volumes'], forms: [], create: false, domain: [['channel', 'in', ['whatsapp', 'chat', 'email', 'in_app']]] }],
      ['3', 'Unified Conversation Object', 8, { model: 'fix.conversation', cols: ['state', 'customer_id', 'channel', 'contact_identity', 'started_at', 'ended_at'], screens: ['M27-conversations'], reports: ['AHT & FCR by Disposition'], forms: ['Call Conversation'] }],
      ['4', 'Queue & Routing', 9, { model: 'fix.cc.queue', cols: ['name', 'code', 'sequence', 'active', 'channel', 'target_answer_seconds'], screens: ['M27-queues', 'M27-routing', 'M27-queue'], reports: ['Service Level by Interval'], forms: ['Queue Definition', 'Routing Workstream', 'Capacity Profile'] }],
      ['5', 'Agent Desktop', 10, { model: 'fix.cc.disposition', cols: ['name', 'code', 'active', 'category', 'is_resolved'], screens: ['M27-desktop', 'M27-dispositions'], reports: ['AHT & FCR by Disposition'], forms: ['Disposition Code', 'Agent Script'] }],
      ['6', 'Workforce Management', 7, { model: 'fix.cc.wfm.shift', cols: ['state', 'agent_id', 'queue_id', 'shift_date', 'start_hour', 'end_hour'], screens: ['M27-wfm', 'M27-rpt-slinterval'], reports: ['Service Level by Interval'], forms: ['Roster Shift'] }],
      ['7', 'Quality Monitoring', 9, { model: 'fix.cc.qa.evaluation', cols: ['conversation_id', 'agent_id', 'score', 'criteria_json', 'notes', 'evaluated_at'], screens: ['M27-qa', 'M27-rpt-qadist'], reports: ['QA Score Distribution'], forms: ['QA Evaluation', 'QA Rubric'] }],
      ['8', 'ERP Notification Service', 14, { model: 'fix.cc.notif.template', cols: ['name', 'active', 'channel', 'subject', 'body', 'consent_class'], screens: ['M27-templates', 'M27-delivery', 'M27-rpt-delivery'], reports: ['Notification Delivery by Channel'], forms: ['Notification Template', 'Delivery Provider'] }],
      ['9', 'Consent Enforcement', 6, { model: 'fix.cc.outbound.list', cols: ['name', 'state', 'campaign_key', 'queue_id', 'priority', 'contact_count'], screens: ['M27-outbound', 'M27-preferences'], reports: [], forms: ['Outbound List'] }]
    ]
  }
};

export const SCREENS = {
  /* Live queue board & conversation grids */
  'M27-queue': { kind: 'model_list', model: 'fix.conversation', create: false,
    cols: ['started_at', 'channel', 'contact_identity', 'customer_id', 'state', 'queue_id', 'agent_id'],
    domain: [['state', 'in', ['new', 'with_ai', 'with_agent']]],
    stateField: 'state' },
  'M27-conversations': { kind: 'model_list', model: 'fix.conversation', create: false,
    cols: ['started_at', 'channel', 'contact_identity', 'customer_id', 'intent', 'disposition_id', 'state', 'ended_at'],
    stateField: 'state',
    actions: [
      { m: 'action_claim', l: 'Claim' },
      { m: 'action_resolve', l: 'Resolve (Agent)' },
      { m: 'action_create_field_work_order', l: 'Dispatch Emergency Field Order' },
      { m: 'action_create_complaint', l: 'Create Complaint' }
    ] },
  /* M27 sweep audit 2026-11-06 (D17): the agent-desktop screen gets its own
   * per-agent pack - it previously borrowed the queue board's metrics. */
  'M27-desktop': { kind: 'table_report', module: 'M27', report: 'agent_desktop', title: 'Agent Desktop Preview', period: false },
  'M27-states': { kind: 'table_report', module: 'M27', report: 'agent_states', title: 'Agent States & Wrap-Up', period: false },
  'M27-digital': { kind: 'table_report', module: 'M27', report: 'digital_summary', title: 'WhatsApp / Chat / Email / Social', period: true },

  /* Operations & settings */
  'M27-queues': { kind: 'model_list', model: 'fix.cc.queue', create: true,
    cols: ['sequence', 'name', 'code', 'channel', 'target_answer_seconds', 'active'] },
  'M27-routing': { kind: 'model_list', model: 'fix.cc.routing.rule', create: true,
    cols: ['priority', 'name', 'channel', 'queue_id', 'active'] },
  'M27-form-routing': {
    kind: 'model_form', model: 'fix.cc.routing.rule',
    title: 'Skills Routing Rule', back: 'M27-routing',
    tabs: [
      { id: 'rule', label: '1. Rule', bn: '১. নিয়ম', icon: '🔀' },
      { id: 'match', label: '2. Channel & Skill', bn: '২. চ্যানেল ও স্কিল', icon: '🎯' }
    ],
    sections: [
      {
        tab: 'rule',
        title: 'Rule & Target Queue',
        note: 'Rules are evaluated lowest priority number first; the first that matches sends the contact to its queue.',
        fields: [
        { name: 'name', label: 'Rule Name', required: true },
        { name: 'queue_id', label: 'Target Queue', required: true },
        { name: 'priority', label: 'Priority', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'match',
        title: 'What It Matches',
        note: 'The skill is a free-text tag matched by the routing engine against the agent\'s skills.',
        fields: [
        { name: 'channel', label: 'Channel', required: true },
        { name: 'skill', label: 'Required Skill' }
        ]
      }
    ]
  },
  'M27-voice': { kind: 'model_list', model: 'fix.cc.ivr.flow', create: true,
    cols: ['name', 'channel', 'version', 'active'] },
  'M27-dispositions': { kind: 'model_list', model: 'fix.cc.disposition', create: true,
    cols: ['code', 'name', 'category', 'is_resolved', 'active'] },
  'M27-outbound': { kind: 'model_list', model: 'fix.cc.outbound.list', create: true,
    cols: ['name', 'campaign_key', 'contact_count', 'priority', 'queue_id', 'state'] },
  'M27-templates': { kind: 'model_list', model: 'fix.cc.notif.template', create: true,
    cols: ['name', 'channel', 'consent_class', 'active'] },
  'M27-delivery': { kind: 'table_report', module: 'M27', report: 'notification_delivery', title: 'Delivery Tracking & Retry', period: true },
  'M27-preferences': { kind: 'table_report', module: 'M27', report: 'preference_summary', title: 'Consent & DND', period: false },
  'M27-qa': { kind: 'model_list', model: 'fix.cc.qa.evaluation', create: true,
    cols: ['conversation_id', 'agent_id', 'score', 'state', 'evaluated_at'],
    stateField: 'state',
    actions: [
      { m: 'action_dispute', l: 'Dispute My Score', ask: 'Why is this score wrong?', kwarg: 'reason' },
      { m: 'action_send_to_calibration', l: 'Send to Calibration', ask: 'Calibration note', kwarg: 'note' },
      { m: 'action_finalise', l: 'Finalise', ask: 'Supervisor ruling', kwarg: 'note' }
    ],
    note: 'The scored agent can dispute but never edit or delete a score. A supervisor other than the agent calibrates and finalises it.' },
  'M27-wfm': { kind: 'model_list', model: 'fix.cc.wfm.shift', create: true,
    cols: ['agent_id', 'queue_id', 'shift_date', 'start_hour', 'end_hour', 'state'] },

  /* Built-in reports (registry report centre) */
  'M27-rpt-channelmix': { kind: 'table_report', module: 'M27', report: 'channel_mix', title: 'Channel Mix & Volumes', period: true },
  'M27-rpt-slinterval': { kind: 'table_report', module: 'M27', report: 'service_level_by_interval', title: 'Service Level by Interval', period: true },
  'M27-rpt-ahtfcr': { kind: 'table_report', module: 'M27', report: 'aht_fcr', title: 'AHT & FCR by Disposition', period: true },
  'M27-rpt-delivery': { kind: 'table_report', module: 'M27', report: 'notification_delivery', title: 'Notification Delivery by Channel', period: true },
  'M27-rpt-qadist': { kind: 'table_report', module: 'M27', report: 'qa_distribution', title: 'QA Score Distribution', period: true },

  /* ==================================================================
   * D365 IN-WORKSPACE RECORD FORMS (Dynamics 365 Multi-Tab Forms)
   * ================================================================== */
    'M27-form-call': {
      lines: {
        field: 'turn_ids',
        title: 'Transcript',
        note: 'The conversation itself, turn by turn.',
        fields: [
          { name: 'sequence', label: '#' },
          { name: 'speaker', label: 'Speaker', required: true },
          { name: 'text', label: 'Text', required: true },
          { name: 'lang', label: 'Language' },
          { name: 'spoken_at', label: 'At' }
        ]
      }, kind: 'model_form', model: 'fix.conversation',
    title: 'Hotline 16743 Conversation Record', back: 'M27-conversations',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Call Session & Channel', bn: '১. কল সেশন ও চ্যানেল', icon: '📞', badge: '5' },
      { id: 'customer', label: '2. Customer & Telephony Timeline', bn: '২. গ্রাহক ও টেলিফোনি সময়রেখা', icon: '👤', badge: '5' },
      { id: 'utterance', label: '3. NLU Intent & Handoff', bn: '৩. এনএলইউ ইনটেন্ট ও হ্যান্ডঅফ', icon: '🤖', badge: '5' },
      { id: 'disposition', label: '4. Disposition & FCR Resolution', bn: '৪. ডিসপজিশন ও এফসিআর', icon: '📋', badge: '4' },
      { id: 'dispatch', label: '5. Emergency Dispatch & Work Order', bn: '৫. জরুরি ডিসপ্যাচ', icon: '🚛', badge: '2' },
      { id: 'docs', label: '6. Audio Evidence Vault (BTRC 180d)', bn: '৬. অডিও প্রমাণ ও বিটিআরসি', icon: '🎙️', badge: '4' }
    ],
    sections: [
      { tab: 'general', title: 'Telephony Session Identification', fields: [
        { name: 'call_sid', required: true, label: 'Telephony Call SID / Session UUID' },
        { name: 'channel', required: true, label: 'Omnichannel Ingress (Voice / Web / WhatsApp)' },
        { name: 'state', label: 'Conversation Lifecycle State', readonly: true },
        { name: 'agent_id', label: 'Assigned Customer Support Agent', readonly: true },
        { name: 'operating_unit_id', label: 'Contact Centre Operating Unit' },
      ]},
      { tab: 'customer', title: 'Customer Telephony & Interaction Timeline', fields: [
        { name: 'customer_id', label: 'Customer Party Master (M33)' },
        { name: 'contact_identity', label: 'Caller Caller-ID / Normalized Phone' },
        { name: 'queued_at', label: 'Queue Entry Timestamp', readonly: true },
        { name: 'answered_at', label: 'Agent Answered Timestamp', readonly: true },
        { name: 'ended_at', label: 'Call Terminated Timestamp', readonly: true },
      ]},
      { tab: 'utterance', title: 'NLU Intent Detection & AI Agent Routing', fields: [
        { name: 'intent', label: 'Detected Primary Utterance Intent' },
        { name: 'urgency_level', label: 'Urgency Priority Tier (Low / Normal / High / Critical)' },
        { name: 'ai_resolved', label: 'Resolved Autonomously by AI Agent', readonly: true },
        { name: 'handoff_reason', label: 'Agent Escalation / Handoff Rationale' },
        { name: 'pii_masked', label: 'PII Scrubbing & Audio Masking Applied' },
      ]},
      { tab: 'disposition', title: 'Mandatory Wrap-Up & FCR Governance (FLAW-27.1)',
        note: 'Every completed hotline interaction mandates selecting an approved disposition code and documenting resolution notes before ticket closure.',
        fields: [
          { name: 'disposition_id', required: true, label: 'Primary Disposition Code' },
          { name: 'fcr', label: 'First Contact Resolution (FCR) Confirmed' },
          { name: 'wrapup_notes', required: true, label: 'Detailed Interaction Wrap-up Notes', type: 'text' },
          { name: 'company_id', label: 'Operating Corporate Legal Entity' },
        ]},
      { tab: 'dispatch', title: 'Field Operations Escalation & Work Order Creation', fields: [
        { name: 'field_work_order_ref', label: 'Emergency Field Service Work Order Reference', readonly: true },
        { name: 'queue_id', label: 'Contact Centre Routing Queue', readonly: true },
        { name: 'work_item_id', label: 'Routed Work Item', readonly: true },
        { name: 'routing_note', label: 'Why Not Routed', readonly: true },
        { name: 'sla_answer_due_at', label: 'Answer Due By (SLA)', readonly: true },
      ]},
      { tab: 'docs', title: 'Statutory Audio Recording Vault & BTRC Retention (FLAW-27.2)',
        note: 'Under Bangladesh Telecommunication Regulatory Commission (BTRC) guidelines, call voice recordings are stored with immutable SHA-256 cryptographic digests for 180 days.',
        fields: [
          { name: 'recording_url', label: 'Secure S3/R2 Recording Audio URL' },
          { name: 'recording_sha256', label: 'Immutable SHA-256 Audio Checksum', readonly: true },
          { name: 'recording_retention_days', label: 'Statutory Retention Remaining (Days)', readonly: true },
          { name: 'create_date', label: 'Call Logging Timestamp', readonly: true },
        ]}
    ] },

  'M27-form-ivr': { kind: 'model_form', model: 'fix.cc.ivr.flow',
    title: 'IVR Flow', back: 'M27-voice',
    tabs: [
      { id: 'general', label: '1. IVR Flow Header', bn: '১. আইভিআর ফ্লো হেডার', icon: '📞', badge: '3' },
      { id: 'prompts', label: '2. Audio Prompts & Languages', bn: '২. অডিও প্রম্পট ও ভাষা', icon: '🎙️', badge: '2' },
      { id: 'keymap', label: '3. Keypress Menu Navigation', bn: '৩. কি-প্রেস মেনু ও রাউটিং', icon: '🔢', badge: '2' },
      { id: 'governance', label: '4. BTRC Hotline Standards', bn: '৪. বিটিআরসি হটলাইন নিয়ম', icon: '🏛️', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'IVR Flow Configuration', fields: [
        { name: 'name', required: true, label: 'IVR Flow Name' },
        { name: 'channel', required: true, label: 'Telephony Channel (Voice)' },
        { name: 'version', label: 'Flow Version' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'prompts', title: 'Bilingual Prompt Tree (JSON menu contract)', fields: [
        { name: 'flow_json', label: 'IVR Menu Tree as JSON (the telephony engine contract)', type: 'text' },
      ]},
      { tab: 'keymap', title: 'DTMF Keypress Mapping & Target Routing',
        note: 'Keypress-to-queue routing is declared inside flow_json nodes (digit → target queue). BTRC guidance: menu depth must not exceed 3 levels before a live-agent option.',
        fields: [] },
      { tab: 'governance', title: 'Hotline 16743 BTRC Quality Standards',
        note: 'BTRC regulations mandate bilingual (Bengali/English) IVR prompts on emergency and commercial hotlines. Menu depth must not exceed 3 levels before offering live agent transfer.',
        fields: [] }
    ] },

  'M27-form-template': { kind: 'model_form', model: 'fix.cc.notif.template',
    title: 'Notification Template', back: 'M27-templates',
    tabs: [
      { id: 'header', label: '1. Template Scope & Channel', bn: '১. টেমপ্লেট ও চ্যানেল', icon: '📨', badge: '4' },
      { id: 'content', label: '2. Bilingual Message Body', bn: '২. দ্বিভাষিক বার্তা বিবরণ', icon: '📝', badge: '2' },
      { id: 'variables', label: '3. Merge Tags & Dynamic Slots', bn: '৩. ডায়নামিক ভ্যারিয়েবল', icon: '🧩', badge: '1' },
      { id: 'compliance', label: '4. BTRC DND & Character Limits', bn: '৪. বিটিআরসি ক্যারেক্টার লিমিট', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'header', title: 'Template Scope & Channel', fields: [
        { name: 'name', required: true, label: 'Template Name' },
        { name: 'channel', required: true, label: 'Transmission Channel (SMS / WhatsApp / Email)' },
        { name: 'consent_class', label: 'Consent Class (transactional / promotional)' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'content', title: 'Message Subject & Body', fields: [
        { name: 'subject', label: 'Message Subject' },
        { name: 'body', label: 'Message Body (bilingual content)', type: 'text' },
      ]},
      { tab: 'variables', title: 'Dynamic Placeholder Tags',
        note: 'Merge variables (order code, ETA, branch) are resolved by the notification service at dispatch time from the conversation and service-order context.',
        fields: [] },
      { tab: 'compliance', title: 'BTRC Telecom Compliance & SMS Curfew',
        note: 'Promotional SMS broadcasts must adhere to the 08:00 to 22:00 BST delivery window and respect Do-Not-Disturb (DND) registries. Transactional service updates are permitted 24/7.',
        fields: [] }
    ] },

  'M27-form-disposition': { kind: 'model_form', model: 'fix.cc.disposition',
    title: 'Disposition Code', back: 'M27-dispositions',
    tabs: [
      { id: 'definition', label: '1. Disposition Definition', bn: '১. ডিসপোজিশন বিবরণ', icon: '🏷️', badge: '3' },
      { id: 'classification', label: '2. FCR & Categorization', bn: '২. এফসিআর ও ক্যাটাগরি', icon: '📊', badge: '2' },
      { id: 'governance', label: '3. Mandatory Wrap-Up Policy', bn: '৩. র‍্যাপ-আপ নীতিমালা', icon: '🔒', badge: '1' }
    ],
    sections: [
      { tab: 'definition', title: 'Disposition Identification', fields: [
        { name: 'code', required: true, label: 'Disposition Code' },
        { name: 'name', required: true, label: 'Disposition Name' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'classification', title: 'Outcome Category & FCR Impact', fields: [
        { name: 'category', required: true, label: 'Resolution Category' },
        { name: 'is_resolved', label: 'Counts Towards First Contact Resolution (FCR)' },
      ]},
      { tab: 'governance', title: 'Mandatory Call Wrap-Up Governance (FLAW-27.1)',
        note: 'Agents cannot resolve or close conversation tickets without selecting an authorized primary disposition code and entering detailed wrap-up notes. This ensures precise FCR and defect telemetry.',
        fields: [] }
    ] },

  'M27-form-outbound': { kind: 'model_form', model: 'fix.cc.outbound.list',
    title: 'Outbound Dial List', back: 'M27-outbound',
    status: { field: 'state' },
    tabs: [
      { id: 'campaign', label: '1. Outbound Campaign Header', bn: '১. আউটবাউন্ড ক্যাম্পেইন', icon: '📢', badge: '4' },
      { id: 'audience', label: '2. Target Audience & Dialing Mode', bn: '২. টার্গেট গ্রাহক ও ডায়ালিং', icon: '👥', badge: '2' },
      { id: 'curfew', label: '3. BTRC Calling Hours & Curfew', bn: '৩. বিটিআরসি কলিং সময়সীমা', icon: '⏱️', badge: '1' },
      { id: 'analytics', label: '4. Reachability & Conversion Audit', bn: '৪. রূপান্তর ও অডিট', icon: '📈', badge: '1' }
    ],
    sections: [
      { tab: 'campaign', title: 'Outbound Campaign Definition', fields: [
        { name: 'name', required: true, label: 'Campaign List Name' },
        { name: 'campaign_key', label: 'Source Campaign / Batch Key' },
        { name: 'priority', required: true, label: 'Dialing Priority (1 = highest)' },
        { name: 'state', readonly: true, label: 'List Execution State' },
      ]},
      { tab: 'audience', title: 'Customer Audience & Contact Counts', fields: [
        { name: 'queue_id', label: 'Agent Skill Queue Serving the List' },
        { name: 'contact_count', readonly: true, label: 'Total Contacts in List' },
      ]},
      { tab: 'curfew', title: 'BTRC Outbound Calling Curfew Enforcer',
        note: 'Automated outbound progressive and predictive dialers must strictly shut down between 22:00 and 08:00 BST. Dialing outside permitted hours incurs severe telecom regulatory fines.',
        fields: [] },
      { tab: 'analytics', title: 'Performance Metrics & Conversion Tracking',
        note: 'Post-service follow-up and contract renewal outbound calls automatically track contact reachability, customer pickup rate, and conversion to active service bookings.',
        fields: [] }
    ] },

  'M27-form-queue': { kind: 'model_form', model: 'fix.cc.queue',
    title: 'Contact Centre Queue', back: 'M27-queues',
    tabs: [
      { id: 'queue', label: '1. Queue Configuration', bn: '১. কিউ কনফিগারেশন', icon: '🎧', badge: '4' },
      { id: 'concurrency', label: '2. Concurrency & Wrap-Up Grace', bn: '২. কনকারেন্সি ও র‍্যাপ-আপ', icon: '⚖️', badge: '2' },
      { id: 'sla', label: '3. Service Level Targets', bn: '৩. এসএলএ টার্গেট', icon: '⏱️', badge: '2' },
      { id: 'routing', label: '4. Skills-Based Routing Rules', bn: '৪. স্কিলভিত্তিক রাউটিং', icon: '🔀', badge: '1' }
    ],
    sections: [
      { tab: 'queue', title: 'Queue Definition', fields: [
        { name: 'code', required: true, label: 'Queue Code' },
        { name: 'name', required: true, label: 'Queue Name' },
        { name: 'channel', required: true, label: 'Inbound Channel' },
        { name: 'sequence', label: 'Queue Priority Sequence' },
      ]},
      { tab: 'concurrency', title: 'Real-Time Concurrency Balancing (FLAW-27.3)', fields: [
        { name: 'max_agent_concurrency', label: 'Max Simultaneous Interactions per Agent' },
        { name: 'wrapup_seconds', label: 'After-Call Wrap-Up Grace Period (Seconds)' },
      ]},
      { tab: 'sla', title: 'Service Level Agreement Targets', fields: [
        { name: 'target_answer_seconds', label: 'Target Answer Speed (Default 20s)' },
        { name: 'active', label: 'Active Queue Status' },
      ]},
      { tab: 'routing', title: 'Automatic Call Distribution (ACD) Policy',
        note: 'ACD evaluates real-time agent presence, skill proficiencies, and active wrap-up timers before offering incoming contacts, eliminating dropped calls and queue starvation.',
        fields: [] }
    ] },

  'M27-form-qa': { kind: 'model_form', model: 'fix.cc.qa.evaluation',
    title: 'Call QA Evaluation', back: 'M27-qa',
    status: { field: 'state' },
    tabs: [
      { id: 'evaluation', label: '1. Call Evaluation Header', bn: '১. কল মূল্যায়ন হেডার', icon: '📋', badge: '4' },
      { id: 'scorecard', label: '2. 10-Point Quality Scorecard', bn: '২. গুণগত স্কোরকার্ড', icon: '⭐', badge: '3' },
      { id: 'feedback', label: '3. Coaching & Agent Feedback', bn: '৩. ফিডব্যাক ও কোচিং', icon: '💬', badge: '2' },
      { id: 'audio', label: '4. Audio Recording & SHA-256 Checksum', bn: '৪. অডিও ও ক্রিপ্টোগ্রাফিক প্রুফ', icon: '🔒', badge: '2' }
    ],
    sections: [
      { tab: 'evaluation', title: 'Evaluation Identification', fields: [
        { name: 'conversation_id', required: true, label: 'Evaluated Conversation Session' },
        { name: 'agent_id', required: true, label: 'Handling Contact Centre Agent' },
        { name: 'evaluated_at', required: true, label: 'Evaluation Timestamp' },
      ]},
      { tab: 'scorecard', title: 'Quality Score & Benchmark Evaluation', fields: [
        { name: 'score', required: true, label: 'Overall Quality Score (0-100)' },
        { name: 'criteria_json', label: '10-Criteria Scorecard Breakdown (JSON)', type: 'text' },
      ]},
      { tab: 'feedback', title: 'Agent Coaching & Remedial Action', fields: [
        { name: 'notes', label: 'Coaching Notes / Feedback Communicated to Agent' },
        { name: 'state', label: 'Dispute & Calibration State', readonly: true },
        { name: 'dispute_reason', label: 'Agent Dispute Reason', readonly: true },
        { name: 'original_score', label: 'Score When Disputed', readonly: true },
        { name: 'calibration_note', label: 'Calibration Ruling', readonly: true },
        { name: 'calibrated_by', label: 'Calibrated By', readonly: true },
        { name: 'finalised_at', label: 'Finalised At', readonly: true },
      ]},
      { tab: 'audio', title: 'BTRC 180-Day Audio Evidence Compliance (FLAW-27.2)',
        note: 'The conversation record carries the audio evidence (recording_url, SHA-256 checksum and the 180-day retention countdown) on its Audio Evidence tab — QA evaluations reference that conversation.',
        fields: [] }
    ] },

  'M27-form-wfm': { kind: 'model_form', model: 'fix.cc.wfm.shift',
    title: 'Workforce Roster Shift', back: 'M27-wfm',
    status: { field: 'state' },
    tabs: [
      { id: 'shift', label: '1. Workforce Shift Schedule', bn: '১. রোস্টার শিফট সময়সূচি', icon: '📅', badge: '4' },
      { id: 'adherence', label: '2. Login & Schedule Adherence', bn: '২. লগইন ও শিডিউল আনুগত্য', icon: '⏱️', badge: '3' },
      { id: 'aux', label: '3. Auxiliary Idle Codes & Breaks', bn: '৩. অক্সিলিয়ারি কোড ও বিরতি', icon: '☕', badge: '2' },
      { id: 'compliance', label: '4. Labour Act & Overtime Audit', bn: '৪. শ্রম আইন ও ওভারটাইম অডিট', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'shift', title: 'Shift Schedule Details', fields: [
        { name: 'agent_id', required: true, label: 'Agent / Team Member' },
        { name: 'queue_id', label: 'Serving Skill Queue' },
        { name: 'shift_date', required: true, label: 'Scheduled Shift Date' },
        { name: 'state', readonly: true, label: 'Shift Roster State' },
      ]},
      { tab: 'adherence', title: 'Working Hours (24-hour clock)', fields: [
        { name: 'start_hour', required: true, label: 'Shift Start Hour (0-23)' },
        { name: 'end_hour', required: true, label: 'Shift End Hour (0-23)' },
      ]},
      { tab: 'aux', title: 'Auxiliary Non-Productive Time Tracking',
        note: 'Aux idle codes and breaks are captured by the agent-states telemetry (Agent States & Wrap-Up screen), not on the roster line.',
        fields: [] },
      { tab: 'compliance', title: 'Bangladesh Labour Act 2006 Shift Compliance',
        note: 'Continuous screen time is limited to statutory limits with mandatory ergonomic breaks. Night shift rosters mandate security protocols and transport compliance under BLA 2006.',
        fields: [] }
    ] },
  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M27-deliveries': { kind: 'model_list', model: 'fix.notif.delivery', create: false,
    cols: ['queued_at', 'channel', 'purpose', 'to_address', 'partner_id', 'state', 'language', 'attempts', 'cost'],
    stateField: 'state',
    actions: [
      { m: 'action_send', l: 'Send Now' },
      { m: 'action_cancel', l: 'Cancel' }
    ],
    note: 'Every outbound message, including the ones consent or the BTRC window stopped. A suppressed row is the evidence the rule worked.' },
  'M27-form-delivery': {
    kind: 'model_form', model: 'fix.notif.delivery',
    title: 'Delivery Record', back: 'M27-deliveries',
    create: false, pick: 'A delivery record is written when a notification is sent: open one from Delivery Log & Retry.',
    status: { field: 'state', labels: { queued: 'Queued', sent: 'Sent', delivered: 'Delivered', failed: 'Failed', suppressed: 'Suppressed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'message', label: '1. Message', bn: '১. বার্তা', icon: '✉️' },
      { id: 'lawful', label: '2. Consent & Lawful Basis', bn: '২. সম্মতি ও ভিত্তি', icon: '⚖️' },
      { id: 'delivery', label: '3. Provider & Outcome', bn: '৩. প্রোভাইডার ও ফলাফল', icon: '📡' },
      { id: 'provenance', label: '4. Provenance', bn: '৪. উৎস', icon: '🔗' }
    ],
    sections: [
      {
        tab: 'message',
        title: 'What Was Sent',
        note: 'The body is frozen once the message leaves the estate: the log is evidence of what the subscriber was told.',
        fields: [
        { name: 'channel', label: 'Channel', required: true },
        { name: 'to_address', label: 'Destination', required: true },
        { name: 'language', label: 'Language Sent' },
        { name: 'subject', label: 'Subject' },
        { name: 'body', label: 'Body', required: true },
        { name: 'template_id', label: 'Template' }
        ]
      },
      {
        tab: 'lawful',
        title: 'Consent Decision (S2)',
        note: 'Recorded from the single M33 consent service. A suppression is kept, not dropped — it is the proof the rule worked.',
        fields: [
        { name: 'purpose', label: 'Processing Purpose', required: true },
        { name: 'lawful_basis', label: 'Lawful Basis', required: true },
        { name: 'consent_decision', readonly: true, label: 'Verdict' },
        { name: 'consent_id', label: 'Decisive Consent Record' },
        { name: 'consent_reason', label: 'Verdict In Words' },
        { name: 'consent_checked_at', label: 'Checked At' },
        { name: 'curfew_bound', label: 'BTRC Curfew Applies' },
        { name: 'curfew_hold_until', label: 'Held Until' }
        ]
      },
      {
        tab: 'delivery',
        title: 'Provider & Outcome',
        fields: [
        { name: 'provider_id', label: 'Provider' },
        { name: 'provider_ref', label: 'Provider Reference' },
        { name: 'attempts', label: 'Attempts' },
        { name: 'max_attempts', label: 'Attempt Ceiling' },
        { name: 'next_attempt_at', label: 'Next Attempt' },
        { name: 'cost', label: 'Charged Cost' },
        { name: 'last_error', label: 'Last Error' },
        { name: 'sent_at', label: 'Sent At' },
        { name: 'delivered_at', label: 'Delivered At' },
        { name: 'failed_at', label: 'Failed At' }
        ]
      },
      {
        tab: 'provenance',
        title: 'Where It Came From',
        fields: [
        { name: 'source_model', label: 'Source Model' },
        { name: 'source_id', label: 'Source ID' },
        { name: 'source_event_id', label: 'Outbox Event' },
        { name: 'dedup_key', label: 'Idempotency Key' },
        { name: 'partner_id', label: 'Recipient Party' },
        { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      }
    ]
  },
  'M27-providers': { kind: 'model_list', model: 'fix.notif.provider', create: true,
    cols: ['sequence', 'name', 'code', 'channel', 'transport', 'cost_per_message', 'max_attempts', 'active'],
    note: 'Per-message tariffs live here, which is what makes WhatsApp unit economics answerable.' },
  'M27-form-provider': {
    kind: 'model_form', model: 'fix.notif.provider',
    title: 'Delivery Provider', back: 'M27-providers',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'identity', label: '1. Provider', bn: '১. প্রোভাইডার', icon: '🏷️' },
      { id: 'transport', label: '2. Transport & Endpoint', bn: '২. ট্রান্সপোর্ট', icon: '🔌' },
      { id: 'commercial', label: '3. Tariff & Retries', bn: '৩. ট্যারিফ ও রিট্রাই', icon: '💵' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Provider Identity',
        fields: [
        { name: 'name', label: 'Provider Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'channel', label: 'Channel', required: true },
        { name: 'sequence', label: 'Priority' },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'transport',
        title: 'How The Message Moves',
        note: 'Credentials are never stored on this record — the config key names the parameter that holds them.',
        fields: [
        { name: 'transport', label: 'Transport', required: true },
        { name: 'endpoint_config_key', label: 'Endpoint Config Key' },
        { name: 'sender_mask', label: 'Registered Sender Mask (BTRC)' }
        ]
      },
      {
        tab: 'commercial',
        title: 'Tariff & Retry Policy',
        note: 'A tariff of zero means no price is on file, and cost is then recorded as zero rather than estimated.',
        fields: [
        { name: 'cost_per_message', label: 'Tariff per Message' },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'max_attempts', label: 'Attempts Before Abandoning', required: true }
        ]
      }
    ]
  },
  'M27-workstreams': { kind: 'model_list', model: 'fix.routing.workstream', create: true,
    cols: ['sequence', 'name', 'code', 'channel', 'work_type', 'assignment_method', 'queue_id', 'prefer_last_agent', 'active'],
    actions: [
      { m: 'assign_pending', l: 'Assign Pending' }
    ],
    note: 'Intake to assignment. Pick needs no presence model, which is why it is the default.' },
  'M27-form-workstream': {
    lines: {
      field: 'ruleset_ids',
      title: 'Classification Rules',
      note: 'First match wins. A rule may APPEND a capacity profile to the workstream default — an agent needs room in both.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'name', label: 'Rule', required: true },
        { name: 'condition_kind', label: 'Condition' },
        { name: 'condition_value', label: 'Value' },
        { name: 'target_queue_id', label: 'Route To' },
        { name: 'priority', label: 'Priority' },
        { name: 'required_skill', label: 'Skill' },
        { name: 'appended_capacity_profile_id', label: 'Append Profile' },
        { name: 'stop_on_match', label: 'Stop On Match' }
      ]
    },
    kind: 'model_form', model: 'fix.routing.workstream',
    title: 'Routing Workstream', back: 'M27-workstreams',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'identity', label: '1. Workstream', bn: '১. ওয়ার্কস্ট্রিম', icon: '🔀' },
      { id: 'capacity', label: '2. Capacity & Presence', bn: '২. সক্ষমতা ও উপস্থিতি', icon: '📊' },
      { id: 'assignment', label: '3. Assignment Method', bn: '৩. অ্যাসাইনমেন্ট', icon: '🎯' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Intake Definition',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'channel', label: 'Channel', required: true },
        { name: 'work_type', label: 'Work Type', required: true },
        { name: 'source_model', label: 'Source Model' },
        { name: 'queue_id', label: 'Default Queue', required: true },
        { name: 'sequence', label: 'Order' },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'capacity',
        title: 'Capacity Mechanics',
        note: 'Profiles OR flat units, never both: with both configured, which limit applies would depend on evaluation order.',
        fields: [
        { name: 'default_capacity_profile_id', label: 'Default Capacity Profile' },
        { name: 'use_capacity_units', label: 'Use Flat Units Instead' },
        { name: 'allowed_presence_ids', label: 'Allowed Presences' }
        ]
      },
      {
        tab: 'assignment',
        title: 'How Work Reaches An Agent',
        note: 'Pick needs no presence model at all, which makes it the cheapest real slice of unified routing.',
        fields: [
        { name: 'assignment_method', label: 'Assignment Method', required: true },
        { name: 'prefer_last_agent', label: 'Prefer The Agent Who Served Last' },
        { name: 'prefer_last_agent_days', label: 'Affinity Lookback (days)' }
        ]
      }
    ]
  },
  'M27-workitems': { kind: 'model_list', model: 'fix.routing.workitem', create: false,
    cols: ['created_at', 'display_label', 'workstream_id', 'queue_id', 'priority', 'required_skill', 'state', 'assigned_agent_id', 'capacity_released'],
    stateField: 'state',
    actions: [
      { m: 'action_pick', l: 'Pick' },
      { m: 'action_accept', l: 'Accept' },
      { m: 'action_reject', l: 'Reject' },
      { m: 'action_start_work', l: 'Start' },
      { m: 'action_release_capacity', l: 'Release Capacity (Supervisor)', ask: 'Why is this capacity being released by hand?', kwarg: 'reason' }
    ],
    note: 'Capacity release differs by work type: a record or activity never releases automatically.' },
  'M27-form-workitem': {
    kind: 'model_form', model: 'fix.routing.workitem',
    title: 'Routed Work Item', back: 'M27-workitems',
    create: false, pick: 'A work item is created by routing when a conversation or case arrives: open one from Routed Work Items.',
    status: { field: 'state', labels: { pending: 'Pending', offered: 'Offered', assigned: 'Assigned', active: 'Active', closed: 'Closed', abandoned: 'Abandoned' } },
    tabs: [
      { id: 'work', label: '1. The Work', bn: '১. কাজ', icon: '📋' },
      { id: 'classification', label: '2. Classification', bn: '২. শ্রেণিবিন্যাস', icon: '🏷️' },
      { id: 'assignment', label: '3. Offer & Assignment', bn: '৩. অফার ও অ্যাসাইনমেন্ট', icon: '🎧' },
      { id: 'capacity', label: '4. Capacity Release', bn: '৪. সক্ষমতা মুক্তি', icon: '🔓' }
    ],
    sections: [
      {
        tab: 'work',
        title: 'What Is Being Routed',
        fields: [
        { name: 'display_label', label: 'Item' },
        { name: 'source_model', label: 'Source Model', required: true },
        { name: 'source_id', label: 'Source ID', required: true },
        { name: 'partner_id', label: 'Customer' },
        { name: 'workstream_id', label: 'Workstream', required: true },
        { name: 'queue_id', label: 'Queue', required: true },
        { name: 'work_type', label: 'Work Type', required: true },
        { name: 'created_at', label: 'Created', required: true }
        ]
      },
      {
        tab: 'classification',
        title: 'Classification Outcome',
        note: 'The entitlement verdict is captured at intake so an agent sees what the customer is contractually owed without a second lookup.',
        fields: [
        { name: 'priority', label: 'Priority' },
        { name: 'required_skill', label: 'Required Skill' },
        { name: 'capacity_profile_ids', label: 'Capacity Profiles' },
        { name: 'classified_by_id', label: 'Classified By' },
        { name: 'entitlement_note', label: 'Entitlement (S5)' },
        { name: 'overflow_applied', label: 'Overflow / Closure Action' }
        ]
      },
      {
        tab: 'assignment',
        title: 'Offer & Assignment',
        fields: [
        { name: 'offered_agent_id', label: 'Offered To', readonly: true },
        { name: 'offered_at', label: 'Offered At', readonly: true },
        { name: 'offer_expires_at', label: 'Offer Expires', readonly: true },
        { name: 'bullseye_ring_id', label: 'Bullseye Ring', readonly: true },
        { name: 'assigned_agent_id', label: 'Assigned To', readonly: true },
        { name: 'assigned_at', label: 'Assigned At', readonly: true },
        { name: 'assignment_mode', label: 'Mode', readonly: true },
        { name: 'is_monitoring', label: 'Monitoring Only (No Capacity)' }
        ]
      },
      {
        tab: 'capacity',
        title: 'Capacity Release',
        note: 'A conversation releases only when the agent ends it AND closes the session; records and activities never release automatically.',
        fields: [
        { name: 'capacity_released', label: 'Capacity Released', readonly: true },
        { name: 'capacity_released_at', label: 'Released At', readonly: true },
        { name: 'closed_at', label: 'Closed At', readonly: true }
        ]
      }
    ]
  },
  'M27-bullseye': { kind: 'model_list', model: 'fix.routing.bullseye.ring', create: true,
    cols: ['workstream_id', 'sequence', 'name', 'wait_seconds', 'user_group_id', 'active'],
    note: 'Timed rings that widen the eligible pool.' },
  'M27-form-bullseye': {
    kind: 'model_form', model: 'fix.routing.bullseye.ring',
    title: 'Bullseye Ring', back: 'M27-bullseye',
    tabs: [
      { id: 'ring', label: '1. Ring', bn: '১. রিং', icon: '🎯' },
      { id: 'pool', label: '2. Wait & Pool', bn: '২. অপেক্ষা ও পুল', icon: '⏱️' }
    ],
    sections: [
      {
        tab: 'ring',
        title: 'Ring Position',
        note: 'Two rings of one workstream cannot share a sequence: the rings open in sequence order.',
        fields: [
        { name: 'workstream_id', label: 'Workstream', required: true },
        { name: 'sequence', label: 'Sequence', required: true },
        { name: 'name', label: 'Ring Name', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'pool',
        title: 'How Long, and Who It Opens To',
        note: 'A ring waits at least one second before widening to the next. An empty user group opens the ring to every eligible agent, which is what a final ring usually is.',
        fields: [
        { name: 'wait_seconds', label: 'Wait (seconds)', required: true },
        { name: 'user_group_id', label: 'User Group' }
        ]
      }
    ]
  },
  'M27-capacity': { kind: 'model_list', model: 'fix.cc.capacity.profile', create: true,
    cols: ['name', 'code', 'work_item_limit', 'reset_frequency', 'assignment_blocking', 'active'],
    note: 'The four fields Microsoft defines. Blocking forces Busy-DND when the limit is reached.' },
  'M27-form-capacity': {
    lines: {
      field: 'assignment_ids',
      title: 'Agents On This Profile',
      note: 'A personal limit overrides the profile limit, and applies to NEW assignments only.',
      fields: [
        { name: 'agent_id', label: 'Agent', required: true },
        { name: 'max_units_override', label: 'Personal Limit' },
        { name: 'active', label: 'Active' }
      ]
    },
    kind: 'model_form', model: 'fix.cc.capacity.profile',
    title: 'Capacity Profile', back: 'M27-capacity',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'profile', label: '1. Profile', bn: '১. প্রোফাইল', icon: '📊' },
      { id: 'behaviour', label: '2. Reset & Blocking', bn: '২. রিসেট ও ব্লকিং', icon: '🚫' }
    ],
    sections: [
      {
        tab: 'profile',
        title: 'Profile Definition',
        note: 'Microsoft defines exactly four fields here, and the limit cannot be zero: to stop routing to someone, change their presence.',
        fields: [
        { name: 'name', label: 'Profile Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'work_item_limit', label: 'Work Item Limit', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'behaviour',
        title: 'Reset Frequency & Assignment Blocking',
        note: 'An end-of-day profile is a daily quota: closing an item does NOT give the capacity back. Blocking forces Busy-DND at the limit.',
        fields: [
        { name: 'reset_frequency', label: 'Reset Frequency', required: true },
        { name: 'assignment_blocking', label: 'Assignment Blocking' }
        ]
      }
    ]
  },
  'M27-presence': { kind: 'model_list', model: 'fix.cc.agent.state', create: false,
    cols: ['agent_id', 'presence_status_id', 'presence_source', 'changed_at', 'heartbeat_at', 'is_bookable', 'missed_offers'],
    actions: [
      { m: 'heartbeat', l: 'Heartbeat' }
    ],
    note: 'Presence is derived from capacity as well as self-set; the source column says which.' },
  'M27-form-presence': {
    lines: {
      field: 'log_ids',
      title: 'Presence History',
      note: 'Append-only. Adherence is measured from these intervals.',
      fields: [
        { name: 'from_at', label: 'From', required: true },
        { name: 'to_at', label: 'To' },
        { name: 'presence_status_id', label: 'Presence', required: true },
        { name: 'presence_source', label: 'Set By' },
        { name: 'minutes', label: 'Minutes' }
      ]
    },
    kind: 'model_form', model: 'fix.cc.agent.state',
    title: 'Agent Presence', back: 'M27-presence',
    create: false, pick: 'An agent\'s presence is set by the agent\'s own status and heartbeat: open one from Live Agent Presence.',
    status: { field: 'presence_source', labels: { manual: 'Self-set', capacity_block: 'Capacity-forced', missed_notification: 'Missed-offer', shift: 'Roster', system: 'System' } },
    tabs: [
      { id: 'live', label: '1. Live State', bn: '১. চলমান অবস্থা', icon: '🟢' },
      { id: 'routing', label: '2. Routing Eligibility', bn: '২. রাউটিং যোগ্যতা', icon: '🔀' }
    ],
    sections: [
      {
        tab: 'live',
        title: 'Current Presence',
        note: 'A stale heartbeat means the state is untrustworthy, and the agent is treated as offline rather than silently drained of work.',
        fields: [
        { name: 'agent_id', label: 'Agent', required: true },
        { name: 'presence_status_id', label: 'Presence', required: true },
        { name: 'presence_source', label: 'Set By', required: true },
        { name: 'changed_at', label: 'Changed At', required: true },
        { name: 'heartbeat_at', label: 'Last Heartbeat' }
        ]
      },
      {
        tab: 'routing',
        title: 'Eligibility & Offer History',
        note: 'Unified routing only considers agents who exist as bookable resources. Missed offers cost an agent their available status.',
        fields: [
        { name: 'is_bookable', label: 'Bookable Resource' },
        { name: 'missed_offers', label: 'Consecutive Missed Offers' }
        ]
      }
    ]
  },
  'M27-presence-statuses': { kind: 'model_list', model: 'fix.cc.presence.status', create: true,
    cols: ['sequence', 'name', 'code', 'is_available_class', 'is_system_dnd', 'active'],
    note: 'Only an available-class status receives routed work.' },
  'M27-form-presence-status': {
    kind: 'model_form', model: 'fix.cc.presence.status',
    title: 'Presence Status', back: 'M27-presence-statuses',
    tabs: [
      { id: 'identity', label: '1. Status', bn: '১. অবস্থা', icon: '🟢' },
      { id: 'routing', label: '2. Routing Behaviour', bn: '২. রাউটিং আচরণ', icon: '🔀' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Status Identity',
        note: 'Each presence code exists once. Statuses are data, so "On training" or "In a huddle" needs no code change.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'sequence', label: 'Order' },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'routing',
        title: 'Receives Work / Busy-DND',
        note: 'Only an available-class status receives routed work. Busy-DND is the status capacity blocking forces an agent into, so it can never also receive work; exactly one status should carry it.',
        fields: [
        { name: 'is_available_class', label: 'Receives Work' },
        { name: 'is_system_dnd', label: 'System Busy-DND' }
        ]
      }
    ]
  },
  'M27-presence-history': { kind: 'model_list', model: 'fix.cc.agent.state.log', create: false,
    cols: ['from_at', 'to_at', 'agent_id', 'presence_status_id', 'presence_source', 'minutes'],
    note: 'Append-only. Adherence is measured from this, so it cannot be edited.' },
  'M27-scripts': { kind: 'model_list', model: 'fix.cc.script', create: true,
    cols: ['sequence', 'name', 'code', 'queue_id', 'intent', 'support_type', 'state', 'step_count', 'active'],
    stateField: 'state',
    actions: [
      { m: 'action_publish', l: 'Publish' }
    ],
    note: 'Ordered guidance per scenario. D365 keeps scripts and macros separate and so do we.' },
  'M27-form-script': {
    lines: {
      field: 'step_ids',
      title: 'Script Steps',
      note: 'Skipping a mandatory step requires a reason, and that reason is the QA record.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'name', label: 'Step', required: true },
        { name: 'instruction', label: 'What To Do Or Say', required: true },
        { name: 'instruction_bn', label: 'Instruction (Bengali)' },
        { name: 'is_mandatory', label: 'Mandatory' },
        { name: 'macro_id', label: 'Macro' },
        { name: 'knowledge_binding_id', label: 'Surface Article' }
      ]
    },
    kind: 'model_form', model: 'fix.cc.script',
    title: 'Agent Script', back: 'M27-scripts',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    tabs: [
      { id: 'identity', label: '1. Script', bn: '১. স্ক্রিপ্ট', icon: '📜' },
      { id: 'binding', label: '2. Where It Applies', bn: '২. প্রযোজ্যতা', icon: '🎯' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Script Identity',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'code', label: 'Code', required: true },
        { name: 'sequence', label: 'Order' },
        { name: 'state', label: 'State', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'binding',
        title: 'Queue & Intent Binding',
        note: 'A script bound to both a queue and an intent outranks one bound to the intent alone: an agent handed five equal scripts uses none.',
        fields: [
        { name: 'queue_id', label: 'Queue' },
        { name: 'intent', label: 'Intent' },
        { name: 'support_type', label: 'Support Type' }
        ]
      }
    ]
  },
  'M27-macros': { kind: 'model_list', model: 'fix.cc.macro', create: true,
    cols: ['name', 'code', 'macro_action', 'template_id', 'confirm_required', 'active'],
    note: 'A macro names an action from a whitelist — configuration access must not become code execution.' },
  'M27-form-macro': {
    kind: 'model_form', model: 'fix.cc.macro',
    title: 'Agent Macro', back: 'M27-macros',
    tabs: [
      { id: 'identity', label: '1. Macro', bn: '১. ম্যাক্রো', icon: '⚡' },
      { id: 'action', label: '2. Action', bn: '২. কার্যক্রম', icon: '🛠️' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Macro Identity',
        note: 'Each macro code exists once. D365 keeps scripts and macros separate: a script guides, a macro does.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'action',
        title: 'Whitelisted Action',
        note: 'A macro names an action from a fixed whitelist, never a model and method. The send action must name its template or the save is refused.',
        fields: [
        { name: 'macro_action', label: 'Action', required: true },
        { name: 'template_id', label: 'Template (send action)' },
        { name: 'confirm_required', label: 'Agent Confirms Before Running' }
        ]
      }
    ]
  },
  'M27-knowledge': { kind: 'model_list', model: 'fix.cc.knowledge.binding', create: true,
    cols: ['sequence', 'intent', 'queue_id', 'article_ref', 'note', 'active'],
    note: 'Intent to M61 article, as a reviewable record rather than a search.' },
  'M27-form-knowledge': {
    kind: 'model_form', model: 'fix.cc.knowledge.binding',
    title: 'Knowledge Binding', back: 'M27-knowledge',
    tabs: [
      { id: 'binding', label: '1. Binding', bn: '১. বাইন্ডিং', icon: '📚' },
      { id: 'sync', label: '2. Article Sync', bn: '২. আর্টিকেল সিঙ্ক', icon: '🔄' }
    ],
    sections: [
      {
        tab: 'binding',
        title: 'Intent or Queue to Article',
        note: 'The article reference is the M61 article code (or its name). A binding is a record rather than a search, so the article put in front of an agent is deliberate and reviewable.',
        fields: [
        { name: 'intent', label: 'Intent' },
        { name: 'queue_id', label: 'Queue' },
        { name: 'article_ref', label: 'Article Reference', required: true },
        { name: 'note', label: 'Why This Article' },
        { name: 'sequence', label: 'Order' },
        { name: 'active', label: 'Active' },
        { name: 'display_label', label: 'Binding', readonly: true }
        ]
      },
      {
        tab: 'sync',
        title: 'What the Knowledge Module Last Reported',
        note: 'Stamped by the knowledge-published hand-off from M61, so the agent desktop can tell a binding whose article moved on from one that still matches.',
        fields: [
        { name: 'synced_version', label: 'Synced Version', readonly: true },
        { name: 'synced_content_hash', label: 'Synced Hash', readonly: true },
        { name: 'synced_on', label: 'Synced On', readonly: true }
        ]
      }
    ]
  },
  'M27-script-adherence': { kind: 'model_list', model: 'fix.cc.script.completion', create: false,
    cols: ['completed_at', 'conversation_id', 'script_id', 'step_id', 'agent_id', 'skipped', 'skip_reason'],
    note: 'What makes a script QA evidence rather than a wall poster.' },
  'M27-rubrics': { kind: 'model_list', model: 'fix.cc.qa.rubric', create: true,
    cols: ['name', 'code', 'applies_to', 'state', 'active'],
    stateField: 'state',
    actions: [
      { m: 'action_publish', l: 'Publish' },
      { m: 'action_retire', l: 'Retire' }
    ],
    note: '\'Both\' is the default: scoring the assistant on a different scale than agents makes automation\'s effect unmeasurable.' },
  'M27-form-rubric': {
    lines: {
      field: 'criterion_ids',
      title: 'Criteria',
      note: 'Only measurable criteria are auto-scored. Tone, empathy and accuracy are not readable from a database row and stay manual.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'name', label: 'Criterion', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'weight', label: 'Weight %', required: true },
        { name: 'measure', label: 'Measured By', required: true },
        { name: 'active', label: 'Active' }
      ]
    },
    kind: 'model_form', model: 'fix.cc.qa.rubric',
    title: 'QA Rubric', back: 'M27-rubrics',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    tabs: [
      { id: 'identity', label: '1. Rubric', bn: '১. রুব্রিক', icon: '📏' },
      { id: 'scope', label: '2. Scope', bn: '২. পরিধি', icon: '🤖' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Rubric Identity',
        note: 'Criterion weights must total 100: a score out of an unknown denominator is not a score.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'state', label: 'State', required: true, readonly: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'scope',
        title: 'AI And Human On One Scale',
        note: '\'Both\' is the default deliberately — scoring the assistant on a different scale than agents is how an estate ends up unable to say whether automation improved service.',
        fields: [
        { name: 'applies_to', label: 'Applies To', required: true }
        ]
      }
    ]
  },
  'M27-adherence': { kind: 'model_list', model: 'fix.cc.wfm.adherence', create: false,
    cols: ['adherence_date', 'agent_id', 'scheduled_minutes', 'available_minutes', 'adherence_pct', 'shift_count', 'note'],
    note: 'Scheduled versus actually present. Time available outside the shift is overtime, not adherence.' },
};

export const REPORT_ROUTES = {
  'M27:Channel Mix & Volumes': 'M27-rpt-channelmix',
  'M27:Service Level by Interval': 'M27-rpt-slinterval',
  'M27:AHT & FCR by Disposition': 'M27-rpt-ahtfcr',
  'M27:Notification Delivery by Channel': 'M27-rpt-delivery',
  'M27:QA Score Distribution': 'M27-rpt-qadist'
};

export const FORM_CHIPS = {
  'M27:Delivery Record': 'M27-form-delivery',
  'M27:Delivery Provider': 'M27-form-provider',
  'M27:Routing Workstream': 'M27-form-workstream',
  'M27:Routed Work Item': 'M27-form-workitem',
  'M27:Capacity Profile': 'M27-form-capacity',
  'M27:Agent Presence': 'M27-form-presence',
  'M27:Agent Script': 'M27-form-script',
  'M27:QA Rubric': 'M27-form-rubric',
  'M27:IVR Flow': 'M27-form-ivr',
  'M27:Notification Template': 'M27-form-template',
  'M27:Disposition Code': 'M27-form-disposition',
  'M27:Outbound List': 'M27-form-outbound',
  'M27:Call Conversation': 'M27-form-call',
  'M27:Queue Definition': 'M27-form-queue',
  'M27:QA Evaluation': 'M27-form-qa',
  'M27:Roster Shift': 'M27-form-wfm',
  'M27:__by_model__': {
    'fix.notif.delivery': 'M27-form-delivery',
    'fix.notif.provider': 'M27-form-provider',
    'fix.routing.workstream': 'M27-form-workstream',
    'fix.routing.workitem': 'M27-form-workitem',
    'fix.cc.capacity.profile': 'M27-form-capacity',
    'fix.cc.agent.state': 'M27-form-presence',
    'fix.cc.script': 'M27-form-script',
    'fix.cc.qa.rubric': 'M27-form-rubric',
    'fix.conversation': 'M27-form-call',
    'fix.cc.ivr.flow': 'M27-form-ivr',
    'fix.cc.notif.template': 'M27-form-template',
    'fix.cc.disposition': 'M27-form-disposition',
    'fix.cc.outbound.list': 'M27-form-outbound',
    'fix.cc.queue': 'M27-form-queue',
    'fix.cc.qa.evaluation': 'M27-form-qa',
    'fix.cc.wfm.shift': 'M27-form-wfm',
    'fix.cc.routing.rule': 'M27-form-routing',
    'fix.routing.bullseye.ring': 'M27-form-bullseye',
    'fix.cc.presence.status': 'M27-form-presence-status',
    'fix.cc.macro': 'M27-form-macro',
    'fix.cc.knowledge.binding': 'M27-form-knowledge'
  },
  'M27:__by_screen__': {
    'M27-deliveries': 'M27-form-delivery',
    'M27-providers': 'M27-form-provider',
    'M27-workstreams': 'M27-form-workstream',
    'M27-workitems': 'M27-form-workitem',
    'M27-capacity': 'M27-form-capacity',
    'M27-presence': 'M27-form-presence',
    'M27-scripts': 'M27-form-script',
    'M27-rubrics': 'M27-form-rubric',
    'M27-queue': 'M27-form-call',
    'M27-conversations': 'M27-form-call',
    'M27-form-call': 'M27-form-call',
    'M27-queues': 'M27-form-queue',
    'M27-voice': 'M27-form-ivr',
    'M27-dispositions': 'M27-form-disposition',
    'M27-outbound': 'M27-form-outbound',
    'M27-templates': 'M27-form-template',
    'M27-qa': 'M27-form-qa',
    'M27-wfm': 'M27-form-wfm',
    'M27-routing': 'M27-form-routing',
    'M27-bullseye': 'M27-form-bullseye',
    'M27-presence-statuses': 'M27-form-presence-status',
    'M27-macros': 'M27-form-macro',
    'M27-knowledge': 'M27-form-knowledge'
  }
};

export const FORM_MODELS = {
  'M27:QA Rubric': 'fix.cc.qa.rubric',
  'M27:Agent Script': 'fix.cc.script',
  'M27:Agent Presence': 'fix.cc.agent.state',
  'M27:Capacity Profile': 'fix.cc.capacity.profile',
  'M27:Routed Work Item': 'fix.routing.workitem',
  'M27:Routing Workstream': 'fix.routing.workstream',
  'M27:Delivery Provider': 'fix.notif.provider',
  'M27:Delivery Record': 'fix.notif.delivery',
  'M27:IVR Flow': 'fix.cc.ivr.flow',
  'M27:Notification Template': 'fix.cc.notif.template',
  'M27:Disposition Code': 'fix.cc.disposition',
  'M27:Outbound List': 'fix.cc.outbound.list',
  'M27:Call Conversation': 'fix.conversation',
  'M27:Queue Definition': 'fix.cc.queue',
  'M27:QA Evaluation': 'fix.cc.qa.evaluation',
  'M27:Roster Shift': 'fix.cc.wfm.shift'
};

export const CREATE = {
  M27: { screen: 'M27-form-call', model: 'fix.conversation', label: 'Conversation' }
};
