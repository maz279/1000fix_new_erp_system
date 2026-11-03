/** @odoo-module **/
/* A03 · Customer Experience — M32 Conversational AI (Bengali NLU).
 * Rebuilt 2026-10-31: Full Microsoft Dynamics 365 multi-tab form architecture
 * across all 4 in-workspace forms with zero Bengali/English mixing, three-tier
 * confidence gating, automated PII scrubbing, and dialectical phonetic search.
 */

export const MODULE = {
  area: 'A03', code: 'M32', en: 'Conversational AI (Bengali)', title: 'M32 · Conversational AI (Bengali)',
  bn: 'কথোপকথন এআই', icon: '🤖',
  desc: 'Native Bengali NLU engine, intent classification, multi-turn dialogue state machines, RAG knowledge retrieval, safety guardrails, and human agent handoff.',
  kpis: [
    { l: 'FAQ Automation', m: 'faq_automation', suffix: '%' },
    { l: 'AI FCR', m: 'ai_fcr', suffix: '%' },
    { l: 'Handoff Precision', m: 'handoff_precision', suffix: '%' },
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
      { id: 'M32-entities', en: 'Entity Extraction', bn: 'সত্তা নিষ্কাশন', t: 'g' },
      { id: 'M32-dialogue', en: 'Dialogue Flows', bn: 'ডায়ালগ ফ্লো', t: 'g' }
    ]},
    { en: 'Grounding & Safety', bn: 'গ্রাউন্ডিং ও সুরক্ষা', screens: [
      { id: 'M32-rag', en: 'RAG Knowledge Sources', bn: 'আরএজি জ্ঞান ভাণ্ডার', t: 'g' },
      { id: 'M32-guardrails', en: 'Guard Rails', bn: 'গার্ডরেইল', t: 'g' },
      { id: 'M32-handoff', en: 'Handoff Packages', bn: 'হ্যান্ডঅফ প্যাকেজ', t: 'g' }
    ]},
    { en: 'Agent Assist', bn: 'এজেন্ট সহায়তা', screens: [
      { id: 'M32-assist', en: 'Suggested Replies / NBA', bn: 'প্রস্তাবিত উত্তর', t: 'd' },
      { id: 'M32-analytics', en: 'Conversation Analytics', bn: 'কথোপকথন বিশ্লেষণ', t: 'r' }
    ]},
    { en: 'Assistant Configuration', bn: 'কনফিগারেশন ও ফর্ম', screens: [
      { id: 'M32-form-intent', en: 'Intent', bn: 'ইনটেন্ট ফর্ম', t: 'f' },
      { id: 'M32-form-dialogue', en: 'Dialogue Flow', bn: 'ডায়ালগ ফ্লো ফর্ম', t: 'f' },
      { id: 'M32-form-guardrail', en: 'Guard-Rail Rule', bn: 'গার্ডরেইল ফর্ম', t: 'f' },
      { id: 'M32-form-rag', en: 'RAG Knowledge Source', bn: 'আরএজি ফর্ম', t: 'f' }
    ]},
    { en: 'Assistant Reports', bn: 'রিপোর্ট', screens: [
      { id: 'M32-rpt-coverage', en: 'Intent Coverage & FCR', bn: 'ইনটেন্ট কভারেজ ও এফসিআর', t: 'r' },
      { id: 'M32-rpt-handoffrsn', en: 'Handoff Reasons', bn: 'হ্যান্ডঅফ কারণ', t: 'r' },
      { id: 'M32-rpt-guardlog', en: 'Guard-Rail Intervention Log', bn: 'গার্ডরেইল হস্তক্ষেপ লগ', t: 'r' },
      { id: 'M32-rpt-langperf', en: 'Bengali vs English Performance', bn: 'বাংলা-ইংরেজি পারফরম্যান্স', t: 'r' },
      { id: 'M32-rpt-csat', en: 'Assistant CSAT', bn: 'অ্যাসিস্ট্যান্ট সিএসএটি', t: 'r' }
    ]},
    { en: 'Grounding Service (S7)', bn: 'গ্রাউন্ডিং সার্ভিস', screens: [
      { id: 'M32-llm-providers', en: 'Model Providers & Residency', bn: 'মডেল প্রোভাইডার', t: 'g' },
      { id: 'M32-form-llm-provider', en: 'Model Provider', bn: 'প্রোভাইডার ফর্ম', t: 'f' },
      { id: 'M32-asks', en: 'Grounded Answers Log', bn: 'গ্রাউন্ডেড উত্তর', t: 'g' },
      { id: 'M32-form-ask', en: 'Grounded Answer', bn: 'উত্তর ফর্ম', t: 'f' }
    ]},
    { en: 'NLU Release Gate', bn: 'এনএলইউ রিলিজ গেট', screens: [
      { id: 'M32-datasets', en: 'NLU Release Bundles', bn: 'এনএলইউ রিলিজ বান্ডেল', t: 'g' },
      { id: 'M32-form-dataset', en: 'NLU Release Bundle', bn: 'রিলিজ বান্ডেল ফর্ম', t: 'f' }
    ]},
    { en: 'Intent Mining', bn: 'ইনটেন্ট মাইনিং', screens: [
      { id: 'M32-intent-candidates', en: 'Candidate Intents', bn: 'প্রস্তাবিত ইনটেন্ট', t: 'g' },
      { id: 'M32-form-intent-candidate', en: 'Candidate Intent', bn: 'প্রস্তাব ফর্ম', t: 'f' }
    ]}
  ],
  reports: ['Intent Coverage & FCR', 'Handoff Reasons', 'Guard-Rail Intervention Log', 'Bengali vs English Performance', 'Assistant CSAT'],
  forms: ['Intent', 'Dialogue Flow', 'Guard-Rail Rule', 'RAG Knowledge Source', 'Model Provider', 'Grounded Answer', 'Candidate Intent', 'NLU Release Bundle'],
  cross: ['M27 Contact Centre', 'M33 Party Master', 'M01 Service Orders Central Hub', 'M61 Knowledge Base'],
  freg: {
    src: 62,
    sub: [
      ['1', 'Intent Recognition (bn/en/mixed)', 9, { model: 'fix.assistant.intent', cols: ['name', 'code', 'active', 'name_bn', 'description', 'sample_bn'], screens: ['M32-intents', 'M32-rpt-coverage'] }],
      ['2', 'Entity Extraction', 7, { model: 'fix.assistant.ask', cols: ['asked_at', 'intent', 'question', 'language', 'grounded'], screens: ['M32-entities', 'M32-asks'] }],
      ['3', 'Dialogue Management', 8, { model: 'fix.assistant.dialogue', cols: ['name', 'active', 'channel', 'version', 'flow_json'], screens: ['M32-dialogue'] }],
      ['4', 'RAG Grounding', 7, { model: 'fix.assistant.rag.source', cols: ['name', 'active', 'source_type', 'reference', 'chunk_count', 'last_indexed_at'], screens: ['M32-rag'] }],
      ['5', 'Authenticated Actions', 6, { model: 'fix.conversation', cols: ['state', 'customer_id', 'channel', 'contact_identity', 'started_at', 'ended_at'], screens: ['M32-sessions'] }],
      ['6', 'Guard Rails', 7, { model: 'fix.assistant.guardrail', cols: ['name', 'active', 'rule', 'action', 'note'], screens: ['M32-guardrails', 'M32-rpt-guardlog'] }],
      ['7', 'Handoff Decision', 5, { model: 'fix.conversation', cols: ['started_at', 'channel', 'intent', 'handoff_reason', 'state'], screens: ['M32-handoff', 'M32-rpt-handoffrsn', 'M32-sessions'], domain: [['state', 'in', ['with_agent', 'resolved_agent']]] }],
      ['8', 'Agent Assistance', 6, { model: 'fix.assistant.ask', cols: ['asked_at', 'intent', 'engine', 'grounded', 'requires_human'], screens: ['M32-assist', 'M32-asks'], domain: [['consumer', '=', 'm27_agent_assist']] }],
      ['9', 'Analytics', 7, { model: 'fix.conversation', cols: ['started_at', 'channel', 'intent', 'ai_resolved', 'state'], screens: ['M32-analytics', 'M32-rpt-langperf', 'M32-rpt-csat', 'M32-sessions'] }]
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
    cols: ['code', 'name', 'name_bn', 'description', 'company_id'] },
  'M32-entities': { kind: 'table_report', module: 'M32', report: 'entity_catalog', title: 'Entity Extraction', period: false },
  'M32-dialogue': { kind: 'model_list', model: 'fix.assistant.dialogue', create: true,
    cols: ['name', 'channel', 'version', 'active'] },
  'M32-guardrails': { kind: 'model_list', model: 'fix.assistant.guardrail', create: true,
    cols: ['name', 'rule', 'action', 'active'] },
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
        fields: [
          { name: 'sample_bn', label: 'Bengali Corpus Under Test', readonly: true },
          { name: 'sample_en', label: 'English Benchmark Under Test', readonly: true },
          { name: 'active', label: 'Released to Production', readonly: true },
        ]},
      { tab: 'guardrails', title: 'Confidence Gating, PII Scrubbing & System Governance',
        note: 'REQ-32.1 three-tier gating, as the engine implements it: confidence >= 0.75 replies automatically, 0.50-0.74 asks the customer to disambiguate, below 0.50 hands off to a human agent. Credit card numbers, MFS PINs and National IDs are scrubbed before any message is written to disk (REQ-32.3).',
        fields: [
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
    cols: ['name', 'dataset_type', 'language', 'prompt_version', 'benchmark_accuracy_pct', 'approval_state', 'state', 'released_at'],
    stateField: 'state',
    actions: [
      { m: 'action_compute_digest', l: 'Compute Digest' },
      { m: 'action_run_benchmark', l: 'Run Benchmark' },
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
      { id: 'release', label: '4. Release', bn: '৪. রিলিজ', icon: '🚀' }
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
        { name: 'phrase', label: 'Phrase', required: true },
        { name: 'language', label: 'Language', required: true },
        { name: 'frequency', label: 'Occurrences', required: true },
        { name: 'distinct_conversations', label: 'Distinct Conversations', required: true },
        { name: 'first_seen', label: 'First Seen' },
        { name: 'last_seen', label: 'Last Seen' },
        { name: 'sample_utterances', label: 'Scrubbed Samples' },
        { name: 'mined_at', label: 'Mined At' }
        ]
      },
      {
        tab: 'review',
        title: 'Human Decision',
        note: 'Accepting does NOT create the intent: an intent needs authored Bengali utterances and a grounding function, and T08 forbids machine-translated utterances.',
        fields: [
        { name: 'state', label: 'State', required: true },
        { name: 'covered_by_intent', label: 'Already Covered By' },
        { name: 'review_note', label: 'Reviewer Note' }
        ]
      }
    ]
  },
};

export const REPORT_ROUTES = {
  'M32:Intent Coverage & FCR': 'M32-rpt-coverage',
  'M32:Handoff Reasons': 'M32-rpt-handoffrsn',
  'M32:Guard-Rail Intervention Log': 'M32-rpt-guardlog',
  'M32:Bengali vs English Performance': 'M32-rpt-langperf',
  'M32:Assistant CSAT': 'M32-rpt-csat'
};

export const FORM_CHIPS = {
  'M32:Model Provider': 'M32-form-llm-provider',
  'M32:Grounded Answer': 'M32-form-ask',
  'M32:Candidate Intent': 'M32-form-intent-candidate',
  'M32:NLU Release Bundle': 'M32-form-dataset',
  'M32:Intent': 'M32-form-intent',
  'M32:Dialogue Flow': 'M32-form-dialogue',
  'M32:Guard-Rail Rule': 'M32-form-guardrail',
  'M32:RAG Knowledge Source': 'M32-form-rag',
  'M32:__by_model__': {
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
