/** @odoo-module **/
/* A03 · Customer Experience — M32 Conversational AI (Bengali NLU).
 * Rebuilt 2026-10-31: Full Microsoft Dynamics 365 multi-tab form architecture
 * across all 4 in-workspace forms with zero Bengali/English mixing, three-tier
 * confidence gating, automated PII scrubbing, and dialectical phonetic search.
 *
 * Capture audit 2026-11-14: five of the nine sub-module pages (Entity
 * Extraction, Authenticated Actions, Handoff Decision, Agent Assistance,
 * Analytics) captured nothing. Each page now captures what its sub-module
 * names: entity definitions, the action authority matrix, the handoff
 * triggers (registers the spec gives the Customer Service Manager, built in
 * cd_contact_centre/models/fix_assistant_registers.py), the review and send
 * of AI answers, and the review of mined candidate intents.
 *
 * Capture audit pass 2 (2026-11-19), read against spec 10.1 / 13 / 14:
 *   1 intent category + per-intent confidence threshold (T-05), and a
 *     shadow evaluation before a bundle replaces production (BRU-CAI-14);
 *   6 guard-rail stage + severity, and the review of a firing (spec 14
 *     "false-positive review");
 *   8 the agent edits the AI answer before sending it (FR-CAI-038);
 *   9 the unresolved queue: review a question the assistant could not
 *     answer, and close a knowledge gap against its M61 article (KPI-184).
 */

export const MODULE = {
  area: 'A03', code: 'M32', en: 'Conversational AI (Bengali)', title: 'M32 · Conversational AI (Bengali)',
  bn: 'কথোপকথন এআই', icon: '🤖',
  desc: 'Native Bengali NLU engine, intent classification, multi-turn dialogue state machines, RAG knowledge retrieval, safety guardrails, and human agent handoff.',
  kpis: [
    { l: 'FAQ Automation', m: 'faq_automation', suffix: '%' },
    { l: 'AI FCR', m: 'ai_fcr', suffix: '%' },
    { l: 'Handoff Precision', m: 'handoff_precision', src: false, suffix: '%' },
    { l: 'Bengali Sessions', m: 'bengali_sessions', suffix: '%' },
    { l: 'Guard-Rail Blocks', m: 'guardrail_blocks' },
    { l: 'Avg Turns', m: 'avg_turns' }
  ],
  groups: [
    { en: 'Assistant', bn: 'অ্যাসিস্ট্যান্ট', screens: [
      { id: 'M32-chat', en: 'Assistant Playground', bn: 'অ্যাসিস্ট্যান্ট প্লেগ্রাউন্ড', t: 'c' },
      { id: 'M32-sessions', en: 'Bengali AI Conversations', bn: 'কথোপকথন', t: 'g' }
    ]},
    { en: 'Understanding', bn: 'বোঝা', screens: [
      { id: 'M32-intents', en: 'Intent Library', bn: 'ইনটেন্ট লাইব্রেরি', t: 'g' },
      { id: 'M32-entity-defs', en: 'Entity Definitions', bn: 'সত্তা সংজ্ঞা', t: 'g' },
      { id: 'M32-entities', en: 'Entity Extraction', bn: 'সত্তা নিষ্কাশন', t: 'r' },
      { id: 'M32-dialogue', en: 'Dialogue Flows', bn: 'ডায়ালগ ফ্লো', t: 'g' }
    ]},
    { en: 'Actions & Handoff', bn: 'কাজ ও হ্যান্ডঅফ', screens: [
      { id: 'M32-authority', en: 'Action Authority Matrix', bn: 'কাজের কর্তৃত্ব', t: 'g' },
      { id: 'M32-handoff-triggers', en: 'Handoff Triggers', bn: 'হ্যান্ডঅফ ট্রিগার', t: 'g' }
    ]},
    { en: 'Grounding & Safety', bn: 'গ্রাউন্ডিং ও সুরক্ষা', screens: [
      { id: 'M32-rag', en: 'RAG Knowledge Sources', bn: 'আরএজি জ্ঞান ভাণ্ডার', t: 'g' },
      { id: 'M32-guardrails', en: 'Guard Rails', bn: 'গার্ডরেইল', t: 'g' },
      { id: 'M32-guardrail-firings', en: 'Guard-Rail Firings', bn: 'গার্ডরেইল সক্রিয়তা', t: 'g' },
      { id: 'M32-handoff', en: 'Handoff Packages', bn: 'হ্যান্ডঅফ প্যাকেজ', t: 'r' }
    ]},
    { en: 'Agent Assist', bn: 'এজেন্ট সহায়তা', screens: [
      { id: 'M32-assist', en: 'Suggested Replies / NBA', bn: 'প্রস্তাবিত উত্তর', t: 'r' },
      { id: 'M32-analytics', en: 'Conversation Analytics', bn: 'কথোপকথন বিশ্লেষণ', t: 'r' }
    ]},
    { en: 'Assistant Configuration', bn: 'কনফিগারেশন ও ফর্ম', screens: [
      { id: 'M32-form-intent', en: 'Intent', bn: 'ইনটেন্ট ফর্ম', t: 'f' },
      { id: 'M32-form-dialogue', en: 'Dialogue Flow', bn: 'ডায়ালগ ফ্লো ফর্ম', t: 'f' },
      { id: 'M32-form-guardrail', en: 'Guard-Rail Rule', bn: 'গার্ডরেইল ফর্ম', t: 'f' },
      { id: 'M32-form-rag', en: 'RAG Knowledge Source', bn: 'আরএজি ফর্ম', t: 'f' },
      { id: 'M32-form-entity', en: 'Entity Definition', bn: 'সত্তা সংজ্ঞা ফর্ম', t: 'f' },
      { id: 'M32-form-authority', en: 'Action Authority Rule', bn: 'কর্তৃত্ব নিয়ম ফর্ম', t: 'f' },
      { id: 'M32-form-handoff-trigger', en: 'Handoff Trigger', bn: 'হ্যান্ডঅফ ট্রিগার ফর্ম', t: 'f' },
      { id: 'M32-form-review-answer', en: 'Review an AI Answer', bn: 'এআই উত্তর পর্যালোচনা', t: 'f' },
      { id: 'M32-form-send-answer', en: 'Send a Reviewed Answer', bn: 'পর্যালোচিত উত্তর পাঠান', t: 'f' },
      { id: 'M32-form-candidate-accept', en: 'Accept a Candidate Intent', bn: 'প্রস্তাবিত ইনটেন্ট গ্রহণ', t: 'f' },
      { id: 'M32-form-candidate-reject', en: 'Reject a Candidate Intent', bn: 'প্রস্তাবিত ইনটেন্ট বাতিল', t: 'f' },
      { id: 'M32-form-shadow', en: 'Shadow-Evaluate a Release Bundle', bn: 'শ্যাডো মূল্যায়ন', t: 'f' },
      { id: 'M32-form-guardrail-review', en: 'Review a Guard-Rail Firing', bn: 'গার্ডরেইল সক্রিয়তা পর্যালোচনা', t: 'f' },
      { id: 'M32-form-unresolved-review', en: 'Review an Unresolved Question', bn: 'অমীমাংসিত প্রশ্ন পর্যালোচনা', t: 'f' },
      { id: 'M32-form-gap-close', en: 'Close a Knowledge Gap', bn: 'জ্ঞান ঘাটতি বন্ধ', t: 'f' }
    ]},
    { en: 'Assistant Reports', bn: 'রিপোর্ট', screens: [
      { id: 'M32-rpt-coverage', en: 'Intent Coverage & FCR', bn: 'ইনটেন্ট কভারেজ ও এফসিআর', t: 'r' },
      { id: 'M32-rpt-handoffrsn', en: 'Handoff Reasons', bn: 'হ্যান্ডঅফ কারণ', t: 'r' },
      { id: 'M32-rpt-guardlog', en: 'Guard-Rail Intervention Log', bn: 'গার্ডরেইল হস্তক্ষেপ লগ', t: 'r' },
      { id: 'M32-rpt-langperf', en: 'Bengali vs English Performance', bn: 'বাংলা-ইংরেজি পারফরম্যান্স', t: 'r' },
      { id: 'M32-rpt-csat', en: 'Assistant CSAT', bn: 'অ্যাসিস্ট্যান্ট সিএসএটি', t: 'r' },
      { id: 'M32-rpt-gaps', en: 'Knowledge Gap Report', bn: 'জ্ঞান ঘাটতি রিপোর্ট', t: 'r' }
    ]},
    { en: 'Grounding Service (S7)', bn: 'গ্রাউন্ডিং সার্ভিস', screens: [
      { id: 'M32-llm-providers', en: 'Model Providers & Residency', bn: 'মডেল প্রোভাইডার', t: 'g' },
      { id: 'M32-form-llm-provider', en: 'Model Provider', bn: 'প্রোভাইডার ফর্ম', t: 'f' },
      { id: 'M32-asks', en: 'Grounded Answers Log', bn: 'গ্রাউন্ডেড উত্তর', t: 'g' }
    ]},
    { en: 'NLU Release Gate', bn: 'এনএলইউ রিলিজ গেট', screens: [
      { id: 'M32-datasets', en: 'NLU Release Bundles', bn: 'এনএলইউ রিলিজ বান্ডেল', t: 'g' },
      { id: 'M32-form-dataset', en: 'NLU Release Bundle', bn: 'রিলিজ বান্ডেল ফর্ম', t: 'f' }
    ]},
    { en: 'Intent Mining', bn: 'ইনটেন্ট মাইনিং', screens: [
      { id: 'M32-unresolved', en: 'Unresolved Questions', bn: 'অমীমাংসিত প্রশ্ন', t: 'g' },
      { id: 'M32-intent-candidates', en: 'Candidate Intents', bn: 'প্রস্তাবিত ইনটেন্ট', t: 'g' }
    ]}
  ],
  reports: ['Intent Coverage & FCR', 'Handoff Reasons', 'Guard-Rail Intervention Log', 'Bengali vs English Performance', 'Assistant CSAT', 'Knowledge Gap Report'],
  forms: ['Intent', 'Dialogue Flow', 'Guard-Rail Rule', 'RAG Knowledge Source', 'Model Provider', 'NLU Release Bundle',
    'Entity Definition', 'Action Authority Rule', 'Handoff Trigger', 'Review an AI Answer', 'Send a Reviewed Answer',
    'Accept a Candidate Intent', 'Reject a Candidate Intent', 'Shadow-Evaluate a Release Bundle',
    'Review a Guard-Rail Firing', 'Review an Unresolved Question', 'Close a Knowledge Gap'],
  cross: ['M27 Contact Centre', 'M33 Party Master', 'M01 Service Orders Central Hub', 'M61 Knowledge Base'],
  freg: {
    src: 62,
    sub: [
      /* 1 Intent Recognition (FR-CAI-001..008): the intent library is the
       * module's own record; a corpus reaches production as a release bundle. */
      ['1', 'Intent Recognition (bn/en/mixed)', 9, { model: 'fix.assistant.intent', cols: ['name', 'code', 'category', 'confidence_threshold', 'active', 'name_bn', 'sample_bn'], screens: ['M32-intents', 'M32-chat', 'M32-datasets', 'M32-rpt-coverage'], reports: ['Intent Coverage & FCR'], forms: ['Intent', 'NLU Release Bundle', 'Shadow-Evaluate a Release Bundle'], create: 'M32-form-intent' }],
      /* 2 Entity Extraction (FR-CAI-003, spec 10.1 fix.entity.definition):
       * what the assistant extracts, proved against examples when saved. */
      ['2', 'Entity Extraction', 7, { model: 'fix.assistant.entity', cols: ['code', 'name', 'entity_type', 'validation', 'pattern', 'active'], screens: ['M32-entity-defs', 'M32-entities'], reports: [], forms: ['Entity Definition'], create: 'M32-form-entity' }],
      ['3', 'Dialogue Management', 8, { model: 'fix.assistant.dialogue', cols: ['name', 'active', 'channel', 'version', 'flow_json'], screens: ['M32-dialogue'], reports: [], forms: ['Dialogue Flow'] }],
      ['4', 'RAG Grounding', 7, { model: 'fix.assistant.rag.source', cols: ['name', 'active', 'source_type', 'reference', 'chunk_count', 'last_indexed_at'], screens: ['M32-rag', 'M32-llm-providers'], reports: [], forms: ['RAG Knowledge Source', 'Model Provider'] }],
      /* 5 Authenticated Actions (FR-CAI-021..030): the authority matrix the
       * Customer Service Manager owns. The assistant's own actions are
       * system-written; this is what it is allowed to do. */
      ['5', 'Authenticated Actions', 6, { model: 'fix.assistant.action.authority', cols: ['action_type', 'assistant_may_perform', 'requires_identity', 'requires_confirmation', 'approval_limit_bdt', 'never_delegable', 'active'], screens: ['M32-authority', 'M32-sessions'], reports: [], forms: ['Action Authority Rule'], create: 'M32-form-authority' }],
      ['6', 'Guard Rails', 7, { model: 'fix.assistant.guardrail', cols: ['name', 'stage', 'severity', 'rule', 'action', 'active'], screens: ['M32-guardrails', 'M32-guardrail-firings', 'M32-rpt-guardlog'], reports: ['Guard-Rail Intervention Log'], forms: ['Guard-Rail Rule', 'Review a Guard-Rail Firing'], create: 'M32-form-guardrail' }],
      /* 7 Handoff Decision (FR-CAI-036/037): the triggers, each independently
       * tunable; handoffs themselves are written by the assistant. */
      ['7', 'Handoff Decision', 5, { model: 'fix.assistant.handoff.trigger', cols: ['signal', 'category', 'priority', 'notify_supervisor', 'mandatory', 'active'], screens: ['M32-handoff-triggers', 'M32-handoff', 'M32-rpt-handoffrsn', 'M32-sessions'], reports: ['Handoff Reasons'], forms: ['Handoff Trigger'], create: 'M32-form-handoff-trigger' }],
      /* 8 Agent Assistance (FR-CAI-038): an AI answer is never auto-sent - a
       * person other than the asker reviews it, then it is sent. */
      ['8', 'Agent Assistance', 6, { model: 'fix.assistant.ask', cols: ['asked_at', 'intent', 'engine', 'grounded', 'requires_human', 'human_reviewed_by', 'sent_at'], screens: ['M32-assist', 'M32-asks'], reports: [], forms: ['Review an AI Answer', 'Send a Reviewed Answer'], create: 'M32-form-review-answer', domain: [['consumer', '=', 'm27_agent_assist']] }],
      /* 9 Analytics (spec 14, AUT-CAI-08/10): the improvement loop - phrases
       * the assistant could not place are mined and reviewed here. */
      ['9', 'Analytics', 7, { model: 'fix.conversation', cols: ['started_at', 'channel', 'intent', 'ai_resolved', 'state'], screens: ['M32-analytics', 'M32-unresolved', 'M32-intent-candidates', 'M32-rpt-gaps', 'M32-rpt-langperf', 'M32-rpt-csat', 'M32-sessions'], reports: ['Knowledge Gap Report', 'Bengali vs English Performance', 'Assistant CSAT', 'Intent Coverage & FCR'], forms: ['Review an Unresolved Question', 'Close a Knowledge Gap', 'Accept a Candidate Intent', 'Reject a Candidate Intent'], create: 'M32-form-unresolved-review' }]
    ]
  }
};

export const SCREENS = {
  /* The playground runs the REAL classifier through /p03/assistant/classify —
   * the same engine the hotline assistant uses (three-tier confidence gate). */
  'M32-chat': { kind: 'assistant_play' },
  'M32-sessions': { kind: 'model_list', model: 'fix.conversation', create: false,
    cols: ['started_at', 'channel', 'contact_identity', 'customer_id', 'intent', 'ai_resolved', 'handoff_reason', 'ended_at'],
    stateField: 'state' },
  'M32-intents': { kind: 'model_list', model: 'fix.assistant.intent', create: true,
    cols: ['code', 'name', 'name_bn', 'category', 'confidence_threshold', 'company_id'],
    note: 'Empty threshold = the global 0.75. A calibrated threshold is applied by the live bot, the playground and the benchmark.' },
  'M32-entities': { kind: 'table_report', module: 'M32', report: 'entity_catalog', title: 'Entity Extraction', period: false },
  'M32-dialogue': { kind: 'model_list', model: 'fix.assistant.dialogue', create: true,
    cols: ['name', 'channel', 'version', 'active'] },
  'M32-guardrails': { kind: 'model_list', model: 'fix.assistant.guardrail', create: true,
    cols: ['name', 'stage', 'severity', 'rule', 'action', 'active'] },
  'M32-guardrail-firings': { kind: 'model_list', model: 'fix.assistant.ask', create: false,
    domain: [['guardrail_fired', '=', true]],
    cols: ['asked_at', 'consumer', 'question', 'guardrail_verdict', 'guardrail_reason', 'guardrail_review', 'guardrail_reviewed_by'],
    note: 'Every answer a guard rail blocked or flagged. A supervisor says whether the rail was right: the guard-rail log measures precision from these reviews.' },
  'M32-rag': { kind: 'model_list', model: 'fix.assistant.rag.source', create: true,
    cols: ['name', 'source_type', 'reference', 'chunk_count', 'active'] },
  'M32-handoff': { kind: 'table_report', module: 'M32', report: 'handoff_packages', title: 'Handoff Packages', period: true },
  'M32-assist': { kind: 'table_report', module: 'M32', report: 'suggested_replies', title: 'Suggested Replies / NBA', period: false },
  'M32-analytics': { kind: 'table_report', module: 'M32', report: 'conversation_analytics', title: 'Conversation Analytics', period: true },

  /* Built-in reports (registry report centre) */
  'M32-rpt-coverage': { kind: 'table_report', module: 'M32', report: 'intent_coverage_fcr', title: 'Intent Coverage & FCR', period: true },
  'M32-rpt-handoffrsn': { kind: 'table_report', module: 'M32', report: 'handoff_reasons', title: 'Handoff Reasons', period: true },
  'M32-rpt-guardlog': { kind: 'table_report', module: 'M32', report: 'guardrail_status', title: 'Guard-Rail Intervention Log', period: true },
  'M32-rpt-langperf': { kind: 'table_report', module: 'M32', report: 'bengali_vs_english', title: 'Bengali vs English Performance', period: true },
  'M32-rpt-csat': { kind: 'table_report', module: 'M32', report: 'assistant_csat', title: 'Assistant CSAT', period: true },
  'M32-rpt-gaps': { kind: 'table_report', module: 'M32', report: 'knowledge_gap_report', title: 'Knowledge Gap Report', period: true },

  /* ==================================================================
   * D365 IN-WORKSPACE RECORD FORMS (Dynamics 365 Multi-Tab Forms)
   * ================================================================== */
  'M32-form-intent': { kind: 'model_form', model: 'fix.assistant.intent',
    title: 'NLU Intent Definition & Bengali Training Corpus', back: 'M32-intents',
    tabs: [
      { id: 'general', label: '1. Intent Header', bn: '১. ইনটেন্ট শিরোনাম', icon: '🤖', badge: '6' },
      { id: 'training_bn', label: '2. Bengali Corpus', bn: '২. বাংলা কর্পাস', icon: '🇧🇩', badge: '3' },
      { id: 'training_en', label: '3. English Benchmarks', bn: '৩. ইংরেজি কর্পাস', icon: '🇬🇧', badge: '2' },
      { id: 'grounding', label: '4. ERP Grounding', bn: '৪. ইআরপি গ্রাউন্ডিং', icon: '🔗', badge: '3' },
      { id: 'docs', label: '5. Datasets & Release Evidence', bn: '৫. ডেটাসেট ও নথি', icon: '📎', badge: '3' },
      { id: 'guardrails', label: '6. Guardrails & Audit', bn: '৬. গার্ডরেইল ও অডিট', icon: '🛡️', badge: '4' }
    ],
    sections: [
      { tab: 'general', title: 'Intent Identification & Metadata', fields: [
        { name: 'code', required: true, label: 'Intent Canonical Code' },
        { name: 'name', required: true, label: 'Intent Name (English)' },
        { name: 'name_bn', label: 'Intent Name (Bengali Bangla)' },
        { name: 'description', label: 'Intent Semantic Scope & Business Purpose', type: 'text' },
        { name: 'category', label: 'Taxonomy Category (FR-CAI-002)' },
        { name: 'active', label: 'Model Production Active Flag' },
        { name: 'company_id', label: 'Operating Legal Entity' },
      ]},
      { tab: 'training_bn', title: 'Authentic Author-Verified Bengali Training Utterances',
        note: 'Minimum 8 authentic Bengali utterances covering standard, phonetic (Banglish), and regional dialects. Every utterance is processed through the Bengali phonetic normalizer.',
        fields: [
          { name: 'sample_bn', required: true, label: 'Bengali Training Utterances (Newline Separated)', type: 'text' },
        ]},
      { tab: 'training_en', title: 'English Benchmark Utterance Samples', fields: [
        { name: 'sample_en', required: true, label: 'English Training Corpus (Newline Separated)', type: 'text' },
      ]},
      { tab: 'grounding', title: 'Live Odoo ERP Method Grounding & Fallback Policy',
        note: 'Grounding target routes detected intents directly to ERP execution methods (e.g. order tracking, hotline dispatch) with zero hallucination risk.',
        fields: [
          { name: 'grounding', required: true, label: 'Grounding Target Model & Method' },
          { name: 'handoff_on_failure', label: 'Automatic Human Agent Escalation on Failure' },
        ]},
      { tab: 'docs', title: 'Training Datasets, Digests & Production Release',
        note: 'REQ-32.5: every training corpus, golden benchmark and model artifact is registered on fix.assistant.dataset with a SHA-256 digest taken over the file itself. Production release is refused below 92% golden-benchmark accuracy, refused for machine-translated Bengali (REQ-32.2), and requires DOFA Tier 3 authority.',
        fields: []},
      { tab: 'guardrails', title: 'Confidence Gating, PII Scrubbing & System Governance',
        note: 'REQ-32.1 three-tier gating: at or above this intent\'s threshold (empty = 0.75) the assistant answers, from 0.50 it asks the customer to clarify, below 0.50 it hands off. T-05: a threshold is calibrated per intent from the labelled evaluation set (0.60-0.99), and its evidence is recorded. Credit card numbers, MFS PINs and National IDs are scrubbed before any message is written to disk (REQ-32.3).',
        fields: [
          { name: 'confidence_threshold', label: 'Confidence Threshold (T-05)' },
          { name: 'threshold_basis', label: 'Calibration Evidence' },
          { name: 'create_date', label: 'Model Registration Timestamp', readonly: true },
          { name: 'write_date', label: 'Last Training Update Timestamp', readonly: true },
        ]}
    ] },

  'M32-form-dialogue': { kind: 'model_form', model: 'fix.assistant.dialogue',
    title: 'Dialogue Flow FSM', back: 'M32-dialogue',
    tabs: [
      { id: 'dialogue', label: '1. Dialogue Flow Specification', bn: '১. সংলাপ ফ্লো স্পেসিফিকেশন', icon: '💬', badge: '3' },
      { id: 'fsm', label: '2. Visual State Machine Graph (JSON)', bn: '২. স্টেট মেশিন ডায়াগ্রাম', icon: '🔀', badge: '2' },
      { id: 'slots', label: '3. Slot Extraction & Entity Validation', bn: '৩. স্লট ফিলিং ও সত্তা যাচাই', icon: '🧩', badge: '1' },
      { id: 'fallback', label: '4. Multi-Turn Fallback Policy', bn: '৪. মাল্টি-টার্ন ফলব্যাক নীতি', icon: '↩️', badge: '1' }
    ],
    sections: [
      { tab: 'dialogue', title: 'Dialogue Header & Entry', fields: [
        { name: 'name', required: true, label: 'Flow Name' },
        { name: 'channel', required: true, label: 'Conversation Channel' },
        { name: 'version', label: 'Flow Version' },
      ]},
      { tab: 'fsm', title: 'State Transition Graph (JSON)', fields: [
        { name: 'flow_json', label: 'Dialogue State Machine as JSON (entry node, condition gates, slot prompts, fallback counters)', type: 'text' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'slots', title: 'Entity Extraction & Slot Prompts',
        note: 'Entities (Service Order ID, Phone Number, Device Serial, Problem Category) are extracted via deterministic regex parsers and mapped to active dialogue context.',
        fields: [] },
      { tab: 'fallback', title: 'Multi-Turn Repetition & Handoff Rule',
        note: 'If a customer fails slot fulfillment twice consecutively, the dialogue engine must abort bot traversal and route the full conversation to an M27 live agent.',
        fields: [] }
    ] },

  'M32-form-guardrail': { kind: 'model_form', model: 'fix.assistant.guardrail',
    title: 'Safety Guardrail Rule', back: 'M32-guardrails',
    tabs: [
      { id: 'definition', label: '1. Safety Guardrail Rule', bn: '১. সুরক্ষা গার্ডরেইল নিয়ম', icon: '🛡️', badge: '4' },
      { id: 'patterns', label: '2. Blocked Patterns & Toxic Language', bn: '২. নিষিদ্ধ শব্দ ও প্যাটার্ন', icon: '🚫', badge: '2' },
      { id: 'pii', label: '3. Automated PII Regex Scrubbing', bn: '৩. সংবেদনশীল ডেটা মাস্কিং', icon: '🔒', badge: '1' },
      { id: 'audit', label: '4. Guardrail Interception Audit', bn: '৪. হস্তক্ষেপ অডিট ট্রেইল', icon: '⚙️', badge: '1' }
    ],
    sections: [
      { tab: 'definition', title: 'Guardrail Identification', fields: [
        { name: 'name', required: true, label: 'Guardrail Rule Name' },
        { name: 'action', required: true, label: 'Interception Action (Block / Redact / Escalate)' },
        { name: 'stage', required: true, label: 'Stage (Input / Output / Both)' },
        { name: 'severity', required: true, label: 'Severity' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'patterns', title: 'Blocked Lexical Patterns & Rationale', fields: [
        { name: 'rule', required: true, label: 'Rule Condition (e.g. advice on legal liability)' },
        { name: 'note', label: 'Interception Rationale / Notes' },
      ]},
      { tab: 'pii', title: 'Automated Financial PII Scrubbing (FLAW-32.2 / REQ-32.3)',
        note: 'Pre-persistence regular expressions sanitize customer bKash/Nagad PINs, credit card numbers, and National IDs before saving message turns to database disks.',
        fields: [] },
      { tab: 'audit', title: 'Zero Hallucination & Legal Liability Law (REQ-32.6)',
        note: 'The assistant is strictly forbidden from making autonomous financial discount promises, repair warranty extensions, or admission of legal liability.',
        fields: [] }
    ] },

  'M32-form-rag': { kind: 'model_form', model: 'fix.assistant.rag.source',
    title: 'RAG Knowledge Source', back: 'M32-rag',
    tabs: [
      { id: 'source', label: '1. RAG Knowledge Source', bn: '১. আরএজি জ্ঞান ভাণ্ডার', icon: '📚', badge: '4' },
      { id: 'indexing', label: '2. Vector Embeddings & Similarity Threshold', bn: '২. ভেক্টর ইনডেক্সিং ও থ্রেশহোল্ড', icon: '🔍', badge: '2' },
      { id: 'chunks', label: '3. Document Chunks & Sync History', bn: '৩. ডকুমেন্ট চাঙ্ক ও হিস্ট্রি', icon: '📄', badge: '2' },
      { id: 'governance', label: '4. Hallucination Prevention Policy', bn: '৪. হ্যালুসিনেশন প্রতিরোধ নীতি', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'source', title: 'Source Configuration', fields: [
        { name: 'name', required: true, label: 'Knowledge Source Name' },
        { name: 'source_type', required: true, label: 'Source Type (FAQ Table / Policy PDF / M61 Article)' },
        { name: 'reference', label: 'Target Model / Document URL Reference' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'indexing', title: 'Embedding Model & Search Thresholds',
        note: 'The 0.82 cosine similarity floor is engine policy (assistant_engine retriever), not a per-source stored field — sources below the floor hand off to human staff.',
        fields: [] },
      { tab: 'chunks', title: 'Indexing Metrics & Chunks', fields: [
        { name: 'chunk_count', readonly: true, label: 'Total Ingested Document Chunks' },
        { name: 'last_indexed_at', readonly: true, label: 'Last Vector Index Timestamp' },
      ]},
      { tab: 'governance', title: 'Authoritative Grounding Mandate',
        note: 'The RAG retriever grounds assistant responses strictly in verified 1000FiX service policy documents. If the similarity score falls below 0.82, the engine hands off to human staff.',
        fields: [] }
    ] },
  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M32-llm-providers': { kind: 'model_list', model: 'fix.assistant.llm.provider', create: true,
    cols: ['sequence', 'name', 'code', 'model_name', 'residency', 'may_receive_customer_context', 'state', 'active'],
    stateField: 'state',
    note: 'Residency is enforced, not documented: an offshore provider cannot be allowed customer context.' },
  'M32-form-llm-provider': {
    kind: 'model_form', model: 'fix.assistant.llm.provider',
    title: 'Model Provider', back: 'M32-llm-providers',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', disabled: 'Disabled' } },
    tabs: [
      { id: 'identity', label: '1. Provider', bn: '১. প্রোভাইডার', icon: '🧠' },
      { id: 'residency', label: '2. Residency & PDPA', bn: '২. আবাসন ও পিডিপিএ', icon: '🛡️' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Served Model',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'model_name', label: 'Served Model' },
        { name: 'endpoint_config_key', label: 'Endpoint Config Key' },
        { name: 'max_tokens', label: 'Max Tokens' },
        { name: 'sequence', label: 'Priority' },
        { name: 'state', label: 'State', required: true }
        ]
      },
      {
        tab: 'residency',
        title: 'Data Residency',
        note: 'M32 runs self-hosted because customer data must not leave the Company under PDPA transfer restrictions. This field enforces that rather than documenting it: an offshore provider cannot be granted customer context.',
        fields: [
        { name: 'residency', label: 'Residency', required: true },
        { name: 'may_receive_customer_context', label: 'May Receive Customer Context' },
        { name: 'active', label: 'Active' }
        ]
      }
    ]
  },
  'M32-asks': { kind: 'model_list', model: 'fix.assistant.ask', create: false,
    cols: ['asked_at', 'consumer', 'intent', 'engine', 'grounded', 'guardrail_verdict', 'requires_human', 'latency_ms'],
    actions: [
      { m: 'action_mark_reviewed', l: 'Mark Reviewed' },
      { m: 'action_send_to_customer', l: 'Send to Customer' }
    ],
    note: 'Every AI answer with its basis and citations. An answer that cites nothing is refused rather than shown. One that needs review is sent only after someone other than the asker reviews it.' },
  'M32-form-ask': {
    kind: 'model_form', model: 'fix.assistant.ask',
    title: 'Grounded Answer', back: 'M32-asks',
    create: false, pick: 'A grounded answer is recorded when the assistant answers a question: open one from the Grounded Answers Log.',
    status: { field: 'engine', labels: { rule_grounder: 'Rule-grounded', llm: 'Generated', refused: 'Refused' } },
    tabs: [
      { id: 'question', label: '1. Question', bn: '১. প্রশ্ন', icon: '❓' },
      { id: 'answer', label: '2. Answer & Citations', bn: '২. উত্তর ও তথ্যসূত্র', icon: '📚' },
      { id: 'governance', label: '3. Guardrails & Review', bn: '৩. গার্ডরেল ও পুনর্বিবেচনা', icon: '🛡️' }
    ],
    sections: [
      {
        tab: 'question',
        title: 'What Was Asked',
        fields: [
        { name: 'asked_at', label: 'Asked At', required: true, readonly: true },
        { name: 'asked_by', label: 'Asked By', readonly: true },
        { name: 'consumer', label: 'Consumer', required: true, readonly: true },
        { name: 'intent', label: 'Intent', readonly: true },
        { name: 'question', label: 'Question', required: true, readonly: true },
        { name: 'language', label: 'Language', readonly: true },
        { name: 'conversation_id', label: 'Conversation', readonly: true },
        { name: 'partner_id', label: 'Customer', readonly: true }
        ]
      },
      {
        tab: 'answer',
        title: 'Answer And Its Basis',
        note: 'An answer that cites nothing is refused rather than shown. The engine column is never hidden: a rule-based answer presented as generative misleads whoever is deciding how much to trust it.',
        fields: [
        { name: 'answer_bn', label: 'Answer (Bengali)', readonly: true },
        { name: 'answer_en', label: 'Answer (English)', readonly: true },
        { name: 'grounded', label: 'Grounded', readonly: true },
        { name: 'citations', label: 'Citations', readonly: true },
        { name: 'engine', label: 'Engine', required: true, readonly: true },
        { name: 'provider_id', label: 'Provider', readonly: true },
        { name: 'latency_ms', label: 'Latency (ms)', readonly: true }
        ]
      },
      {
        tab: 'governance',
        title: 'Guardrails & Human Review',
        note: 'A generated answer always needs a human before it reaches a customer; a rule-grounded one does not, because its text was authored.',
        fields: [
        { name: 'guardrail_verdict', label: 'Guardrail Verdict', required: true, readonly: true },
        { name: 'guardrail_reason', label: 'Guardrail Reason', readonly: true },
        { name: 'requires_human', label: 'Requires Human Review', readonly: true },
        { name: 'human_reviewed_by', label: 'Reviewed By', readonly: true },
        { name: 'human_reviewed_at', label: 'Reviewed At', readonly: true },
        { name: 'sent_at', label: 'Sent To Customer At', readonly: true },
        { name: 'sent_by', label: 'Sent By', readonly: true },
        { name: 'release_id', label: 'Released Bundle Used', readonly: true },
        { name: 'runtime_basis', label: 'Model & Prompt Basis', readonly: true }
        ]
      }
    ]
  },
  'M32-datasets': { kind: 'model_list', model: 'fix.assistant.dataset', create: true,
    cols: ['name', 'dataset_type', 'language', 'prompt_version', 'benchmark_accuracy_pct', 'shadow_state', 'approval_state', 'state', 'released_at'],
    stateField: 'state',
    actions: [
      { m: 'action_compute_digest', l: 'Compute Digest' },
      { m: 'action_run_benchmark', l: 'Run Benchmark' },
      { m: 'action_run_shadow', l: 'Run Shadow Evaluation' },
      { m: 'action_request_approval', l: 'Request Release Approval', ask: 'Why should this bundle go to production?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' }
    ],
    note: 'Accuracy is measured against an independent golden set, never typed. A Tier-3 director other than the author and the requester releases from the approval inbox; the live assistant then runs on the released corpus, model and prompt.' },
  'M32-form-dataset': {
    kind: 'model_form', model: 'fix.assistant.dataset',
    title: 'NLU Release Bundle', back: 'M32-datasets',
    status: { field: 'state', labels: { draft: 'Draft', benchmarked: 'Benchmarked', released: 'Released', superseded: 'Superseded', rejected: 'Rejected' } },
    tabs: [
      { id: 'bundle', label: '1. Bundle', bn: '১. বান্ডেল', icon: '📦' },
      { id: 'runtime', label: '2. Model & Prompt', bn: '২. মডেল ও প্রম্পট', icon: '🤖' },
      { id: 'evidence', label: '3. Benchmark Evidence', bn: '৩. বেঞ্চমার্ক প্রমাণ', icon: '📏' },
      { id: 'shadow', label: '4. Shadow Evaluation', bn: '৪. শ্যাডো মূল্যায়ন', icon: '👥' },
      { id: 'release', label: '5. Release', bn: '৫. রিলিজ', icon: '🚀' }
    ],
    sections: [
      {
        tab: 'bundle',
        title: 'What Is Being Released',
        note: 'The corpus adds utterances to intents the assistant can already answer. Its digest is taken from the file itself.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'dataset_type', label: 'Dataset Type', required: true },
        { name: 'language', label: 'Language', required: true },
        { name: 'authored_by_native_speaker', label: 'Native-Speaker Authored' },
        { name: 'attachment_id', label: 'Stored File' },
        { name: 'file_name', label: 'File Name' },
        { name: 'sha256_checksum', label: 'SHA-256 Digest', readonly: true }
        ]
      },
      {
        tab: 'runtime',
        title: 'What The Live Assistant Runs On',
        note: 'Once released, the bot and the generator read these from this record. With nothing released they fall back to the built-in intents, the environment model and the code prompt, and the server log says so.',
        fields: [
        { name: 'model_name', label: 'Model Tag' },
        { name: 'prompt_version', label: 'Prompt Version' },
        { name: 'system_prompt', label: 'System Prompt' }
        ]
      },
      {
        tab: 'evidence',
        title: 'Independent Benchmark',
        note: 'The golden set must be prepared by someone other than the corpus author. Run Benchmark measures the accuracy; it cannot be typed.',
        fields: [
        { name: 'benchmark_dataset_id', label: 'Golden Benchmark Set' },
        { name: 'benchmark_accuracy_pct', label: 'Measured Accuracy (%)', readonly: true },
        { name: 'benchmark_cases', label: 'Golden Cases', readonly: true },
        { name: 'benchmark_correct', label: 'Correct', readonly: true },
        { name: 'benchmark_run_at', label: 'Benchmark Run At', readonly: true },
        { name: 'benchmark_run_by', label: 'Benchmark Run By', readonly: true },
        { name: 'benchmark_training_sha256', label: 'Corpus Digest Measured', readonly: true },
        { name: 'benchmark_set_sha256', label: 'Golden Set Digest Used', readonly: true }
        ]
      },
      {
        tab: 'shadow',
        title: 'Shadow Evaluation On Live Traffic (T-11)',
        note: 'BRU-CAI-14: a bundle replaces the one in production only after passing the golden set AND a shadow run: the PII-scrubbed customer turns of the last 30 days are replayed through production and the candidate, without answering anyone. It passes when the candidate answers at least as many turns and changes at most 2% of the answers production gave. The first release has nothing to shadow.',
        fields: [
        { name: 'shadow_state', label: 'Shadow Result', readonly: true },
        { name: 'shadow_baseline_id', label: 'Measured Against (Production)', readonly: true },
        { name: 'shadow_window_days', label: 'Window (days)', readonly: true },
        { name: 'shadow_turns', label: 'Live Turns Replayed', readonly: true },
        { name: 'shadow_baseline_confident', label: 'Answered by Production', readonly: true },
        { name: 'shadow_candidate_confident', label: 'Answered by Candidate', readonly: true },
        { name: 'shadow_agreement', label: 'Same Answer', readonly: true },
        { name: 'shadow_regressions', label: 'Regressions', readonly: true },
        { name: 'shadow_run_at', label: 'Run At', readonly: true },
        { name: 'shadow_run_by', label: 'Run By', readonly: true }
        ]
      },
      {
        tab: 'release',
        title: 'Four-Eyes Release (M63)',
        fields: [
        { name: 'approval_state', label: 'Approval', readonly: true },
        { name: 'approval_request_id', label: 'Approval Request', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'released_by', label: 'Released By', readonly: true },
        { name: 'released_at', label: 'Released At', readonly: true }
        ]
      }
    ]
  },
  'M32-intent-candidates': { kind: 'model_list', model: 'fix.assistant.intent.candidate', create: false,
    cols: ['frequency', 'distinct_conversations', 'phrase', 'language', 'state', 'first_seen', 'last_seen', 'covered_by_intent'],
    stateField: 'state',
    actions: [
      { m: 'action_accept', l: 'Accept' },
      { m: 'action_reject', l: 'Reject' }
    ],
    note: 'Mined from PII-scrubbed turns by frequency analysis — not a language model, and proposals only.' },
  'M32-form-intent-candidate': {
    kind: 'model_form', model: 'fix.assistant.intent.candidate',
    title: 'Candidate Intent', back: 'M32-intent-candidates',
    create: false, pick: 'Candidate intents are mined from conversations: open one from Candidate Intents to review it.',
    status: { field: 'state', labels: { proposed: 'Proposed', accepted: 'Accepted', rejected: 'Rejected', duplicate: 'Already covered' } },
    tabs: [
      { id: 'evidence', label: '1. Evidence', bn: '১. প্রমাণ', icon: '📈' },
      { id: 'review', label: '2. Review', bn: '২. পুনর্বিবেচনা', icon: '✅' }
    ],
    sections: [
      {
        tab: 'evidence',
        title: 'What The Traffic Shows',
        note: 'Mined from PII-scrubbed turns by frequency analysis. This is n-gram counting, not a language model, and it is labelled that way so nobody over-trusts it.',
        fields: [
        { name: 'phrase', label: 'Phrase', readonly: true },
        { name: 'language', label: 'Language', readonly: true },
        { name: 'frequency', label: 'Occurrences', readonly: true },
        { name: 'distinct_conversations', label: 'Distinct Conversations', readonly: true },
        { name: 'first_seen', label: 'First Seen', readonly: true },
        { name: 'last_seen', label: 'Last Seen', readonly: true },
        { name: 'sample_utterances', label: 'Scrubbed Samples', readonly: true },
        { name: 'mined_at', label: 'Mined At', readonly: true }
        ]
      },
      {
        tab: 'review',
        title: 'Human Decision',
        note: 'Accepting does NOT create the intent: an intent needs authored Bengali utterances and a grounding function, and T08 forbids machine-translated utterances. The decision is made with Accept or Reject, never by typing the state.',
        fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'covered_by_intent', label: 'Already Covered By' },
        { name: 'review_note', label: 'Reviewer Note' }
        ]
      }
    ]
  },

  /* ==================================================================
   * CAPTURE AUDIT 2026-11-14 - the registers and decisions each page names
   * ================================================================== */
  'M32-entity-defs': { kind: 'model_list', model: 'fix.assistant.entity', create: true,
    cols: ['sequence', 'code', 'name', 'entity_type', 'validation', 'pattern', 'active'],
    note: 'What the assistant extracts from a message. A pattern is proved against its examples when saved; Bengali digits count as digits.' },
  'M32-form-entity': {
    kind: 'model_form', model: 'fix.assistant.entity',
    title: 'Entity Definition', back: 'M32-entity-defs',
    newLabel: 'Define an Extractable Entity',
    tabs: [
      { id: 'entity', label: '1. Entity', bn: '১. সত্তা', icon: '🏷️' },
      { id: 'rule', label: '2. Extraction Rule', bn: '২. নিষ্কাশন নিয়ম', icon: '🔎' },
      { id: 'proof', label: '3. Examples & Proof', bn: '৩. উদাহরণ ও প্রমাণ', icon: '✅' }
    ],
    sections: [
      { tab: 'entity', title: 'What Is Extracted', fields: [
        { name: 'code', label: 'Code', required: true },
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'entity_type', label: 'Entity Type', required: true },
        { name: 'sequence', label: 'Order' },
        { name: 'active', label: 'Active' }
      ]},
      { tab: 'rule', title: 'Pattern And Validation',
        note: 'A regular expression, matched case-insensitively after Bengali digits (০-৯) are read as 0-9. A pattern that repeats a repeating group, e.g. (\\d+)+, is refused: it runs on every customer message. The validation must also pass, e.g. the IMEI check digit.',
        fields: [
        { name: 'pattern', label: 'Pattern (Regular Expression)', required: true },
        { name: 'validation', label: 'Validation', required: true }
      ]},
      { tab: 'proof', title: 'Examples The Rule Must Pass',
        note: 'Saved only when every example extracts and no counter-example does.',
        fields: [
        { name: 'examples', label: 'Examples (one message per line)', type: 'text', required: true },
        { name: 'counter_examples', label: 'Counter-Examples (one per line)', type: 'text' },
        { name: 'example_check', label: 'Examples Proved', readonly: true },
        { name: 'note', label: 'Note' }
      ]}
    ]
  },

  'M32-authority': { kind: 'model_list', model: 'fix.assistant.action.authority', create: true,
    cols: ['action_type', 'assistant_may_perform', 'requires_identity', 'requires_confirmation', 'approval_limit_bdt', 'never_delegable', 'active'],
    note: 'What the assistant may do on its own. Checked before it answers: an action it may not take, or a customer not yet verified, goes to a person. Cancellations, refunds and goodwill credit can never be delegated.' },
  'M32-form-authority': {
    kind: 'model_form', model: 'fix.assistant.action.authority',
    title: 'Action Authority Rule', back: 'M32-authority',
    newLabel: 'Set an Action Authority Rule',
    tabs: [
      { id: 'action', label: '1. Action', bn: '১. কাজ', icon: '⚙️' },
      { id: 'safeguards', label: '2. Safeguards', bn: '২. সুরক্ষা', icon: '🛡️' }
    ],
    sections: [
      { tab: 'action', title: 'The Action And Who Performs It',
        note: 'Off: the assistant explains the limit and hands the customer to a person (AUT-CAI-07). Contract cancellation, refund and goodwill credit cannot be switched on (BRU-CAI-04).',
        fields: [
        { name: 'action_type', label: 'Action', required: true },
        { name: 'assistant_may_perform', label: 'Assistant May Perform' },
        { name: 'approval_limit_bdt', label: 'Approval Limit (BDT, repair approval)' },
        { name: 'never_delegable', label: 'Always a Person (BRU-CAI-04)', readonly: true },
        { name: 'commitment', label: 'Creates a Commitment', readonly: true },
        { name: 'active', label: 'Active' }
      ]},
      { tab: 'safeguards', title: 'Before The Assistant Acts',
        note: 'An action the assistant may perform always needs a verified customer (BRU-CAI-03), and a commitment always needs the customer\'s explicit yes (BRU-CAI-05). The record refuses to be saved otherwise.',
        fields: [
        { name: 'requires_identity', label: 'Identity Verification First' },
        { name: 'requires_confirmation', label: 'Explicit Confirmation First' },
        { name: 'note', label: 'Why / Owner Note' }
      ]}
    ]
  },

  'M32-handoff-triggers': { kind: 'model_list', model: 'fix.assistant.handoff.trigger', create: true,
    cols: ['signal', 'category', 'priority', 'notify_supervisor', 'mandatory', 'active'],
    note: 'How each kind of handoff is treated: the queue priority it gets and whether supervisors are alerted. Without a row, the spec default applies. Distress and an explicit request for a human cannot be weakened.' },
  'M32-form-handoff-trigger': {
    kind: 'model_form', model: 'fix.assistant.handoff.trigger',
    title: 'Handoff Trigger', back: 'M32-handoff-triggers',
    newLabel: 'Tune a Handoff Trigger',
    sections: [
      { title: 'Signal And Response',
        note: 'The category (emotional, operational, technical) follows from the signal. Distress escalates as Urgent and always alerts the supervisors (BRU-CAI-06, AUT-CAI-04); an explicit request for a human is at least High and can never be switched off (BRU-CAI-07).',
        fields: [
        { name: 'signal', label: 'Signal', required: true },
        { name: 'category', label: 'Category', readonly: true },
        { name: 'priority', label: 'Queue Priority', required: true },
        { name: 'notify_supervisor', label: 'Alert the Supervisors' },
        { name: 'mandatory', label: 'Cannot Be Weakened', readonly: true },
        { name: 'active', label: 'Active' },
        { name: 'note', label: 'Why / Owner Note' }
      ]}
    ]
  },

  /* Agent Assistance: an AI answer reaches a customer only after a person
   * other than the asker reviews it (FR-CAI-038, A03 audit M32 G12). */
  'M32-form-review-answer': {
    kind: 'model_form', model: 'fix.assistant.ask',
    title: 'Review an AI Answer', back: 'M32-asks',
    newLabel: 'Review an AI Answer',
    status: { field: 'engine', labels: { rule_grounder: 'Rule-grounded', llm: 'Generated', refused: 'Refused' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the AI answer to review',
      note: 'Answers that need a person before they reach the customer and nobody has reviewed yet. You cannot review an answer you asked for.',
      search: 'Search question / intent',
      choose: 'Review this answer',
      cols: ['asked_at', 'consumer', 'intent', 'question', 'engine', 'asked_by'],
      domain: [['requires_human', '=', true], ['human_reviewed_by', '=', false], ['engine', '!=', 'refused']],
      empty: 'No AI answer is waiting for review.'
    },
    saveAction: { method: 'action_mark_reviewed', label: 'Mark Reviewed', done: 'Reviewed: the answer can now be sent', kwargs: {} },
    sections: [
      { title: 'Step 2 of 2: Check The Answer Against Its Basis',
        note: 'Check the answer against its citations. Mark it reviewed only if every statement is grounded; otherwise leave it and reply yourself.',
        fields: [
        { name: 'question', label: 'Question', readonly: true },
        { name: 'answer_bn', label: 'Answer (Bengali)', readonly: true },
        { name: 'answer_en', label: 'Answer (English)', readonly: true },
        { name: 'citations', label: 'Citations', readonly: true },
        { name: 'engine', label: 'Engine', readonly: true },
        { name: 'guardrail_reason', label: 'Guardrail Note', readonly: true },
        { name: 'asked_by', label: 'Asked By', readonly: true },
        { name: 'conversation_id', label: 'Conversation', readonly: true }
      ]}
    ]
  },
  'M32-form-send-answer': {
    kind: 'model_form', model: 'fix.assistant.ask',
    title: 'Send a Reviewed Answer', back: 'M32-asks',
    newLabel: 'Send a Reviewed Answer',
    status: { field: 'engine', labels: { rule_grounder: 'Rule-grounded', llm: 'Generated', refused: 'Refused' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the answer to send',
      note: 'Grounded answers on an open conversation, not yet sent, that need no review or have been reviewed by someone other than the asker.',
      search: 'Search question / intent',
      choose: 'Send this answer',
      cols: ['asked_at', 'intent', 'question', 'engine', 'human_reviewed_by', 'conversation_id'],
      domain: [['grounded', '=', true], ['sent_at', '=', false], ['conversation_id', '!=', false],
        '|', ['requires_human', '=', false], ['human_reviewed_by', '!=', false]],
      empty: 'No reviewed answer is waiting to be sent.'
    },
    saveAction: { method: 'action_send_to_customer', label: 'Send to Customer', done: 'Sent: the reply is on the conversation transcript', kwargs: { reply: 'draft_reply' } },
    sections: [
      { title: 'Step 2 of 2: Edit, Then Send What The Customer Receives',
        note: 'FR-CAI-038: a suggestion is always editable and never auto-sent. Edit the reply as you see fit: an edited reply goes on the transcript as your turn, the AI draft stays on record, and the correction is reported to M26. A closed conversation, a refused or ungrounded answer, or one still awaiting review is refused by the server.',
        fields: [
        { name: 'question', label: 'Question', readonly: true },
        { name: 'language', label: 'Language', readonly: true },
        { name: 'draft_reply', label: 'Reply To Send (editable)', type: 'text', required: true },
        { name: 'answer_bn', label: 'Answer (Bengali)', readonly: true },
        { name: 'answer_en', label: 'Answer (English)', readonly: true },
        { name: 'human_reviewed_by', label: 'Reviewed By', readonly: true },
        { name: 'conversation_id', label: 'Conversation', readonly: true }
      ]}
    ]
  },

  /* Analytics: the improvement loop. Accept or reject what was mined; the
   * intent itself is then authored by a native speaker (T08). */
  'M32-form-candidate-accept': {
    kind: 'model_form', model: 'fix.assistant.intent.candidate',
    title: 'Accept a Candidate Intent', back: 'M32-intent-candidates',
    newLabel: 'Review a Candidate Intent',
    status: { field: 'state', labels: { proposed: 'Proposed', accepted: 'Accepted', rejected: 'Rejected', duplicate: 'Already covered' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the mined phrase to accept',
      note: 'Phrases customers used that the intent library does not cover, by frequency. Proposals only: mined by counting, not by a language model.',
      search: 'Search phrase',
      choose: 'Review this phrase',
      cols: ['phrase', 'language', 'frequency', 'distinct_conversations', 'last_seen'],
      domain: [['state', '=', 'proposed']],
      empty: 'No candidate intent is waiting for review.'
    },
    saveAction: { method: 'action_accept', label: 'Accept for Authoring', done: 'Accepted: the intent is now to be authored by a native speaker', kwargs: { note: 'review_note' } },
    sections: [
      { title: 'Step 2 of 2: Accept For Authoring',
        note: 'Accepting does not create the intent. It records that the library needs one, and a native speaker then authors its Bengali utterances and grounding (T08).',
        fields: [
        { name: 'phrase', label: 'Phrase', readonly: true },
        { name: 'language', label: 'Language', readonly: true },
        { name: 'frequency', label: 'Occurrences', readonly: true },
        { name: 'distinct_conversations', label: 'Distinct Conversations', readonly: true },
        { name: 'sample_utterances', label: 'Scrubbed Samples', readonly: true },
        { name: 'review_note', label: 'Reviewer Note' }
      ]}
    ]
  },
  'M32-form-candidate-reject': {
    kind: 'model_form', model: 'fix.assistant.intent.candidate',
    title: 'Reject a Candidate Intent', back: 'M32-intent-candidates',
    newLabel: 'Reject a Candidate Intent',
    status: { field: 'state', labels: { proposed: 'Proposed', accepted: 'Accepted', rejected: 'Rejected', duplicate: 'Already covered' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the mined phrase to reject',
      note: 'Phrases customers used that the intent library does not cover, by frequency.',
      search: 'Search phrase',
      choose: 'Reject this phrase',
      cols: ['phrase', 'language', 'frequency', 'distinct_conversations', 'last_seen'],
      domain: [['state', '=', 'proposed']],
      empty: 'No candidate intent is waiting for review.'
    },
    saveAction: { method: 'action_reject', label: 'Reject', done: 'Rejected', kwargs: { note: 'review_note' } },
    sections: [
      { title: 'Step 2 of 2: Say Why It Is Rejected',
        fields: [
        { name: 'phrase', label: 'Phrase', readonly: true },
        { name: 'language', label: 'Language', readonly: true },
        { name: 'frequency', label: 'Occurrences', readonly: true },
        { name: 'sample_utterances', label: 'Scrubbed Samples', readonly: true },
        { name: 'review_note', label: 'Reason', required: true }
      ]}
    ]
  },

  /* ==================================================================
   * CAPTURE AUDIT PASS 2 2026-11-19
   * ================================================================== */
  /* 1 Intent Recognition: BRU-CAI-14 shadow evaluation of a benchmarked bundle. */
  'M32-form-shadow': {
    kind: 'model_form', model: 'fix.assistant.dataset',
    title: 'Shadow-Evaluate a Release Bundle', back: 'M32-datasets',
    newLabel: 'Shadow-Evaluate a Release Bundle',
    status: { field: 'shadow_state', labels: { none: 'Not run', passed: 'Passed', failed: 'Failed', no_traffic: 'No live traffic' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the benchmarked bundle',
      note: 'Bundles that passed the golden benchmark. A bundle replaces the one in production only after a passing shadow run.',
      search: 'Search bundle',
      choose: 'Evaluate this bundle',
      cols: ['name', 'language', 'prompt_version', 'benchmark_accuracy_pct', 'shadow_state'],
      domain: [['dataset_type', '=', 'intent_corpus'], ['state', '=', 'benchmarked']],
      empty: 'No benchmarked bundle is waiting for a shadow run.'
    },
    saveAction: { method: 'action_run_shadow', label: 'Run Shadow Evaluation', done: 'Shadow evaluation recorded on the bundle', kwargs: {} },
    sections: [
      { title: 'Step 2 of 2: Replay 30 Days Of Live Traffic',
        note: 'Production and this candidate classify the same PII-scrubbed customer turns; nobody is answered. Only counts are kept. The result is measured, never typed.',
        fields: [
        { name: 'name', label: 'Bundle', readonly: true },
        { name: 'benchmark_accuracy_pct', label: 'Golden Benchmark (%)', readonly: true },
        { name: 'shadow_state', label: 'Shadow Result', readonly: true },
        { name: 'shadow_baseline_id', label: 'Measured Against (Production)', readonly: true },
        { name: 'shadow_window_days', label: 'Window (days)', readonly: true },
        { name: 'shadow_turns', label: 'Live Turns Replayed', readonly: true },
        { name: 'shadow_baseline_confident', label: 'Answered by Production', readonly: true },
        { name: 'shadow_candidate_confident', label: 'Answered by Candidate', readonly: true },
        { name: 'shadow_agreement', label: 'Same Answer', readonly: true },
        { name: 'shadow_regressions', label: 'Regressions', readonly: true },
        { name: 'shadow_run_at', label: 'Run At', readonly: true },
        { name: 'shadow_run_by', label: 'Run By', readonly: true }
      ]}
    ]
  },

  /* 6 Guard Rails: a supervisor reviews a firing (spec 14 false-positive review). */
  'M32-form-guardrail-review': {
    kind: 'model_form', model: 'fix.assistant.ask',
    title: 'Review a Guard-Rail Firing', back: 'M32-guardrail-firings',
    newLabel: 'Review a Guard-Rail Firing',
    status: { field: 'guardrail_verdict', labels: { pass: 'Passed', blocked: 'Blocked', not_run: 'Not run' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the firing to review',
      note: 'Answers a guard rail blocked or flagged that nobody has reviewed yet.',
      search: 'Search question / reason',
      choose: 'Review this firing',
      cols: ['asked_at', 'consumer', 'question', 'guardrail_verdict', 'guardrail_reason'],
      domain: [['guardrail_fired', '=', true], ['guardrail_review', '=', false]],
      empty: 'No guard-rail firing is waiting for review.'
    },
    saveAction: { method: 'action_review_guardrail', label: 'Record Review', done: 'Reviewed: the guard-rail log counts it', kwargs: { verdict: 'review_verdict', note: 'review_note_input' } },
    sections: [
      { title: 'Step 2 of 2: Was The Rail Right?',
        note: 'A false positive needs a note: it is what the rule\'s owner tunes from. Only a Contact Centre Supervisor can record a review.',
        fields: [
        { name: 'question', label: 'Question', readonly: true },
        { name: 'guardrail_verdict', label: 'Verdict', readonly: true },
        { name: 'guardrail_reason', label: 'Rule That Fired', readonly: true },
        { name: 'answer_bn', label: 'Answer (Bengali)', readonly: true },
        { name: 'answer_en', label: 'Answer (English)', readonly: true },
        { name: 'review_verdict', label: 'Review', required: true },
        { name: 'review_note_input', label: 'Note (required for a false positive)' }
      ]}
    ]
  },

  /* 9 Analytics: the unresolved queue (spec 10.1 fix.unresolved.intent). */
  'M32-unresolved': { kind: 'model_list', model: 'fix.assistant.unresolved', create: false,
    cols: ['logged_at', 'question', 'best_guess_intent', 'confidence', 'handoff_reason', 'state', 'disposition', 'knowledge_gap_ref', 'gap_days'],
    stateField: 'state',
    note: 'Every handoff where the assistant had no answer is logged here (AUT-CAI-06/08). A supervisor says what it needs; a knowledge gap is closed against the M61 article that answers it (KPI-184).' },
  'M32-form-unresolved': {
    kind: 'model_form', model: 'fix.assistant.unresolved',
    title: 'Unresolved Question', back: 'M32-unresolved',
    create: false, pick: 'Unresolved questions are logged by the assistant: review one with Review an Unresolved Question.',
    status: { field: 'state', labels: { open: 'Open', reviewed: 'Reviewed', closed: 'Gap Closed' } },
    sections: [
      { title: 'What The Assistant Could Not Answer', fields: [
        { name: 'logged_at', label: 'Logged At', readonly: true },
        { name: 'conversation_id', label: 'Conversation', readonly: true },
        { name: 'question', label: 'Question (PII-scrubbed)', readonly: true },
        { name: 'best_guess_intent', label: 'Best-Guess Intent', readonly: true },
        { name: 'confidence', label: 'Confidence', readonly: true },
        { name: 'handoff_reason', label: 'Handoff Reason', readonly: true },
        { name: 'disposition', label: 'Disposition', readonly: true },
        { name: 'knowledge_gap_ref', label: 'M61 Reference', readonly: true },
        { name: 'review_note', label: 'Reviewer Note', readonly: true },
        { name: 'reviewed_by', label: 'Reviewed By', readonly: true },
        { name: 'gap_closed_at', label: 'Gap Closed At', readonly: true }
      ]}
    ]
  },
  'M32-form-unresolved-review': {
    kind: 'model_form', model: 'fix.assistant.unresolved',
    title: 'Review an Unresolved Question', back: 'M32-unresolved',
    newLabel: 'Review an Unresolved Question',
    status: { field: 'state', labels: { open: 'Open', reviewed: 'Reviewed', closed: 'Gap Closed' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the question to review',
      note: 'Questions the assistant handed off because it had no answer, newest first.',
      search: 'Search question / intent',
      choose: 'Review this question',
      cols: ['logged_at', 'question', 'best_guess_intent', 'confidence', 'handoff_reason'],
      domain: [['state', '=', 'open']],
      empty: 'No unresolved question is waiting for review.'
    },
    saveAction: { method: 'action_review', label: 'Record Disposition', done: 'Reviewed: a knowledge gap is sent to M61', kwargs: { disposition: 'disposition_input', note: 'note_input', gap_ref: 'gap_ref_input' } },
    sections: [
      { title: 'Step 2 of 2: What Does It Need?',
        note: 'A knowledge gap is published to M61 (assistant.knowledge_gap). "Out of scope" and "No action" need a reason.',
        fields: [
        { name: 'question', label: 'Question (PII-scrubbed)', readonly: true },
        { name: 'best_guess_intent', label: 'Best-Guess Intent', readonly: true },
        { name: 'confidence', label: 'Confidence', readonly: true },
        { name: 'handoff_reason', label: 'Handoff Reason', readonly: true },
        { name: 'disposition_input', label: 'Disposition', required: true },
        { name: 'gap_ref_input', label: 'M61 Article / Request (if known)' },
        { name: 'note_input', label: 'Reviewer Note' }
      ]}
    ]
  },
  'M32-form-gap-close': {
    kind: 'model_form', model: 'fix.assistant.unresolved',
    title: 'Close a Knowledge Gap', back: 'M32-unresolved',
    newLabel: 'Close a Knowledge Gap',
    status: { field: 'state', labels: { open: 'Open', reviewed: 'Reviewed', closed: 'Gap Closed' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the knowledge gap M61 has now answered',
      note: 'Reviewed knowledge gaps that are still open. KPI-184 counts the ones closed within 30 days.',
      search: 'Search question / intent',
      choose: 'Close this gap',
      cols: ['logged_at', 'question', 'best_guess_intent', 'knowledge_gap_ref', 'reviewed_at'],
      domain: [['state', '=', 'reviewed'], ['disposition', '=', 'knowledge_gap']],
      empty: 'No knowledge gap is open.'
    },
    saveAction: { method: 'action_close_gap', label: 'Close Gap', done: 'Closed: the gap is answered in M61', kwargs: { gap_ref: 'gap_ref_input' } },
    sections: [
      { title: 'Step 2 of 2: The Article That Answers It',
        fields: [
        { name: 'question', label: 'Question (PII-scrubbed)', readonly: true },
        { name: 'best_guess_intent', label: 'Best-Guess Intent', readonly: true },
        { name: 'review_note', label: 'Reviewer Note', readonly: true },
        { name: 'gap_ref_input', label: 'M61 Article That Answers It', required: true }
      ]}
    ]
  },
};

export const REPORT_ROUTES = {
  'M32:Intent Coverage & FCR': 'M32-rpt-coverage',
  'M32:Handoff Reasons': 'M32-rpt-handoffrsn',
  'M32:Guard-Rail Intervention Log': 'M32-rpt-guardlog',
  'M32:Bengali vs English Performance': 'M32-rpt-langperf',
  'M32:Assistant CSAT': 'M32-rpt-csat',
  'M32:Knowledge Gap Report': 'M32-rpt-gaps'
};

export const FORM_CHIPS = {
  'M32:Shadow-Evaluate a Release Bundle': 'M32-form-shadow',
  'M32:Review a Guard-Rail Firing': 'M32-form-guardrail-review',
  'M32:Review an Unresolved Question': 'M32-form-unresolved-review',
  'M32:Close a Knowledge Gap': 'M32-form-gap-close',
  'M32:Unresolved Question': 'M32-form-unresolved',
  'M32:Entity Definition': 'M32-form-entity',
  'M32:Action Authority Rule': 'M32-form-authority',
  'M32:Handoff Trigger': 'M32-form-handoff-trigger',
  'M32:Review an AI Answer': 'M32-form-review-answer',
  'M32:Send a Reviewed Answer': 'M32-form-send-answer',
  'M32:Accept a Candidate Intent': 'M32-form-candidate-accept',
  'M32:Reject a Candidate Intent': 'M32-form-candidate-reject',
  'M32:Model Provider': 'M32-form-llm-provider',
  'M32:Grounded Answer': 'M32-form-ask',
  'M32:Candidate Intent': 'M32-form-intent-candidate',
  'M32:NLU Release Bundle': 'M32-form-dataset',
  'M32:Intent': 'M32-form-intent',
  'M32:Dialogue Flow': 'M32-form-dialogue',
  'M32:Guard-Rail Rule': 'M32-form-guardrail',
  'M32:RAG Knowledge Source': 'M32-form-rag',
  'M32:__by_model__': {
    'fix.assistant.unresolved': 'M32-form-unresolved',
    'fix.assistant.entity': 'M32-form-entity',
    'fix.assistant.action.authority': 'M32-form-authority',
    'fix.assistant.handoff.trigger': 'M32-form-handoff-trigger',
    'fix.assistant.llm.provider': 'M32-form-llm-provider',
    'fix.assistant.ask': 'M32-form-ask',
    'fix.assistant.intent.candidate': 'M32-form-intent-candidate',
    'fix.assistant.dataset': 'M32-form-dataset',
    'fix.assistant.intent': 'M32-form-intent',
    'fix.assistant.dialogue': 'M32-form-dialogue',
    'fix.assistant.guardrail': 'M32-form-guardrail',
    'fix.assistant.rag.source': 'M32-form-rag'
  },
  'M32:__by_screen__': {
    'M32-unresolved': 'M32-form-unresolved',
    'M32-guardrail-firings': 'M32-form-ask',
    'M32-entity-defs': 'M32-form-entity',
    'M32-authority': 'M32-form-authority',
    'M32-handoff-triggers': 'M32-form-handoff-trigger',
    'M32-llm-providers': 'M32-form-llm-provider',
    'M32-asks': 'M32-form-ask',
    'M32-intent-candidates': 'M32-form-intent-candidate',
    'M32-datasets': 'M32-form-dataset',
    'M32-intents': 'M32-form-intent',
    'M32-form-intent': 'M32-form-intent',
    'M32-dialogue': 'M32-form-dialogue',
    'M32-guardrails': 'M32-form-guardrail',
    'M32-rag': 'M32-form-rag'
  }
};

export const FORM_MODELS = {
  'M32:Shadow-Evaluate a Release Bundle': 'fix.assistant.dataset',
  'M32:Review a Guard-Rail Firing': 'fix.assistant.ask',
  'M32:Review an Unresolved Question': 'fix.assistant.unresolved',
  'M32:Close a Knowledge Gap': 'fix.assistant.unresolved',
  'M32:Unresolved Question': 'fix.assistant.unresolved',
  'M32:Entity Definition': 'fix.assistant.entity',
  'M32:Action Authority Rule': 'fix.assistant.action.authority',
  'M32:Handoff Trigger': 'fix.assistant.handoff.trigger',
  'M32:Review an AI Answer': 'fix.assistant.ask',
  'M32:Send a Reviewed Answer': 'fix.assistant.ask',
  'M32:Accept a Candidate Intent': 'fix.assistant.intent.candidate',
  'M32:Reject a Candidate Intent': 'fix.assistant.intent.candidate',
  'M32:Candidate Intent': 'fix.assistant.intent.candidate',
  'M32:NLU Release Bundle': 'fix.assistant.dataset',
  'M32:Grounded Answer': 'fix.assistant.ask',
  'M32:Model Provider': 'fix.assistant.llm.provider',
  'M32:Intent': 'fix.assistant.intent',
  'M32:Dialogue Flow': 'fix.assistant.dialogue',
  'M32:Guard-Rail Rule': 'fix.assistant.guardrail',
  'M32:RAG Knowledge Source': 'fix.assistant.rag.source'
};

export const CREATE = {
  M32: { screen: 'M32-form-intent', model: 'fix.assistant.intent', label: 'Intent' }
};
