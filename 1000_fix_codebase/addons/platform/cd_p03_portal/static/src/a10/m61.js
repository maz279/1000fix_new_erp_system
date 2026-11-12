/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M61 Knowledge & Technical Library.
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 48. */

export const MODULE = {
  area: 'A10', code: 'M61', en: 'Knowledge & Technical Library', title: 'M61 · Knowledge & Technical Library',
  bn: 'জ্ঞান ও কারিগরি গ্রন্থাগার', icon: '📚',
  desc: 'Article library across seven types, troubleshooting trees, review workflow, manuals and schematics, video and image content, context-aware surfacing to faults, offline distribution, article health and gaps, and brand bulletins and recalls.',
  kpis: [
    { l: 'Articles', m: 'articles' },
    { l: 'Coverage (Serviced Models)', m: 'coverage_serviced', suffix: '%' },
    { l: 'Offline Articles', m: 'offline_articles' },
    { l: 'Usefulness Score', m: 'usefulness_score', suffix: '%' },
    { l: 'Reviews Due', m: 'reviews_due' },
    { l: 'Brand Bulletins MTD', m: 'brand_bulletins_mtd' }
  ],
  groups: [
    { en: 'Authoring', screens: [
      { id: 'M61-articles', en: 'Article Library (7 types)', bn: 'নিবন্ধ লাইব্রেরি', t: 'g' },
      { id: 'M61-trees', en: 'Troubleshooting Trees', bn: 'সমস্যা নিরসন ট্রি', t: 'g' },
      { id: 'M61-review', en: 'Review Workflow', bn: 'পর্যালোচনা প্রবাহ', t: 'g' }
    ]},
    { en: 'Technical Library', screens: [
      { id: 'M61-manuals', en: 'Manuals & Schematics', bn: 'ম্যানুয়াল', t: 'g' },
      { id: 'M61-media', en: 'Video & Image Content', bn: 'ভিডিও', t: 'g' }
    ]},
    { en: 'Distribution', screens: [
      { id: 'M61-context', en: 'Context-Aware Surfacing', bn: 'প্রসঙ্গ-সচেতন', t: 'g' },
      { id: 'M61-offline', en: 'Offline Distribution', bn: 'অফলাইন বিতরণ', t: 'g' }
    ]},
    { en: 'Feedback', screens: [
      { id: 'M61-health', en: 'Article Health & Gaps', bn: 'নিবন্ধ স্বাস্থ্য', t: 'r' },
      { id: 'M61-bulletins', en: 'Brand Bulletins & Recalls', bn: 'ব্র্যান্ড বুলেটিন', t: 'g' },
      { id: 'M61-recipients', en: 'Recall Recipients', bn: 'প্রাপক শাখা', t: 'g' },
      { id: 'M61-recalls', en: 'Recall Routing', bn: 'রিকল রাউটিং', t: 'r' }
    ]}
  ],
  reports: ['Coverage Analysis', 'Article Usage & Usefulness', 'Gap Report by Brand/Model', 'Contribution Leaderboard', 'Recall Routing'],
  forms: ['Article', 'Troubleshooting Tree', 'Bulletin', 'Bulletin Recipient'],
  cross: ['M02 Dispatch knowledge links', 'M32 Bengali NLU', 'M22 Training', 'M23 QMS'],
  freg: { src: 48, sub: [
    ['1', 'Authoring & Versioning', 8, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'category', 'version', 'state'], screens: ['M61-articles', 'M61-review'], reports: ['Contribution Leaderboard'], forms: ['Article'] }],
    ['2', 'Troubleshooting Trees', 7, { model: 'fix.knowledge.tree', cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'state'], screens: ['M61-trees'], reports: [], forms: ['Troubleshooting Tree'] }],
    ['3', 'Technical Library', 7, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'category', 'device_brand', 'device_model'], screens: ['M61-manuals', 'M61-media'], reports: ['Gap Report by Brand/Model'], forms: [], create: false, domain: [['category', 'in', ['schematic', 'device_guide', 'repair_procedure']]] }],
    ['4', 'Search & Surfacing', 7, { model: 'fix.knowledge.article', cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'views'], screens: ['M61-context'], reports: ['Article Usage & Usefulness'], forms: [], create: false, domain: [['state', '=', 'published']] }],
    ['5', 'Offline Distribution', 5, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'category', 'version', 'content_hash'], screens: ['M61-offline'], reports: [], forms: [], create: false, domain: [['offline_available', '=', true]] }],
    ['6', 'Feedback & Health', 6, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'views', 'helpful_votes', 'state'], screens: ['M61-health'], reports: ['Coverage Analysis', 'Article Usage & Usefulness', 'Gap Report by Brand/Model'], forms: [] }],
    ['7', 'Brand Bulletins', 4, { model: 'fix.knowledge.bulletin', cols: ['name', 'brand', 'bulletin_type', 'issued_on', 'severity'], screens: ['M61-bulletins'], reports: ['Recall Routing'], forms: ['Bulletin', 'Bulletin Recipient'] }],
    ['8', 'Expertise Mapping', 4, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'device_brand', 'rework_level', 'category'], screens: ['M61-articles'], reports: ['Contribution Leaderboard'], forms: [] }]
  ] }
};

export const SCREENS = {
  'M61-articles': { kind: 'model_list', model: 'fix.knowledge.article', stateField: 'state',
    cols: ['article_code', 'name', 'category', 'device_brand', 'device_model', 'rework_level', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish Article',
        asks: [{ label: 'Reviewer user ID (required for safety-tagged content)', kwarg: 'reviewer_id', number: true }] },
      { m: 'action_archive', l: 'Archive Article' }
    ] },
  'M61-trees': { kind: 'model_list', model: 'fix.knowledge.tree', stateField: 'state',
    cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish Tree',
        asks: [{ label: 'Reviewer user ID (required for safety-tagged content)', kwarg: 'reviewer_id', number: true }] },
      { m: 'action_archive', l: 'Archive Tree' }
    ] },
  'M61-review': { kind: 'model_list', model: 'fix.knowledge.article', stateField: 'state',
    cols: ['article_code', 'name', 'category', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish',
        asks: [{ label: 'Reviewer user ID (required for safety-tagged content)', kwarg: 'reviewer_id', number: true }] }
    ] },
  'M61-manuals': { kind: 'model_list', model: 'fix.knowledge.article',
    cols: ['article_code', 'name', 'category', 'device_brand', 'device_model', 'state'] },
  'M61-media': { kind: 'model_list', model: 'fix.knowledge.media',
    cols: ['name', 'media_type', 'article_id', 'url', 'duration_min', 'size_mb', 'offline_available'] },
  'M61-context': { kind: 'model_list', model: 'fix.knowledge.article',
    cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'category', 'state'] },
  'M61-offline': { kind: 'model_list', model: 'fix.knowledge.article', stateField: 'state',
    cols: ['article_code', 'name', 'category', 'offline_available', 'state'] },
  'M61-health': { kind: 'table_report', module: 'M61', report: 'usage_usefulness', title: 'Article Health & Gaps', period: false },
  'M61-bulletins': { kind: 'model_list', model: 'fix.knowledge.bulletin', stateField: 'state',
    cols: ['name', 'brand', 'bulletin_type', 'issued_on', 'affected_models', 'serial_scope', 'severity', 'recipients_acknowledged', 'recipients_total', 'state'],
    actions: [
      { m: 'action_distribute', l: 'Distribute' },
      { m: 'action_acknowledge', l: 'Acknowledge (Branch)',
        asks: [{ label: 'Recipient line ID to acknowledge (blank = every line you may)', kwarg: 'recipient_id', number: true }] },
      { m: 'action_close', l: 'Close Bulletin',
        asks: [{ label: 'Closure note — what the field did with it', kwarg: 'note' }] }
    ] },
  'M61-recipients': { kind: 'model_list', model: 'fix.knowledge.bulletin.recipient',
    cols: ['bulletin_id', 'branch_id', 'employee_id', 'acknowledged_on', 'acknowledged_by_id', 'note'] },

  /* Report chips -> their own computed pack */
  'M61-rpt-coverage': { kind: 'table_report', module: 'M61', report: 'coverage_analysis', title: 'Coverage Analysis', period: false },
  'M61-rpt-usage': { kind: 'table_report', module: 'M61', report: 'usage_usefulness', title: 'Article Usage & Usefulness', period: false },
  'M61-rpt-gap': { kind: 'table_report', module: 'M61', report: 'gap_report', title: 'Gap Report by Brand/Model', period: false },
  'M61-rpt-contrib': { kind: 'table_report', module: 'M61', report: 'contribution_leaderboard', title: 'Contribution Leaderboard', period: false },
  'M61-recalls': { kind: 'table_report', module: 'M61', report: 'recall_routing', title: 'Recall Routing', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M61-form-article': {
    kind: 'model_form',
    model: 'fix.knowledge.article',
    title: 'Article',
    back: 'M61-articles',
    status: { field: 'state', labels: {
      draft: 'Draft', published: 'Published', archived: 'Archived' } },
    sections: [
      { title: 'Article', note: 'Seven article types; the brand/model/symptom fields are what context-aware surfacing matches on, and offline articles are synced to technicians. Publishing is a Knowledge Publisher act — safety-tagged content also needs a named reviewer (K1).',
        fields: [
          { name: 'name', required: true, label: 'Article Title (English)' },
          { name: 'title_bn', label: 'Article Title (Bengali)' },
          { name: 'article_code', label: 'Reference Code' },
          { name: 'category', required: true, label: 'Article Type' },
          { name: 'device_brand', label: 'Target Brand' },
          { name: 'device_model', label: 'Target Model' },
          { name: 'fault_symptom', label: 'Fault Symptom' },
          { name: 'rework_level', label: 'Rework Level' },
          { name: 'tags', label: 'Search Tags (electrical/battery/high-voltage = safety-critical)' },
          { name: 'offline_available', label: 'Available Offline' },
          { name: 'safety_critical', readonly: true, label: 'Safety-Critical (computed)' },
          { name: 'owner_id', readonly: true, label: 'Owner (stamped at creation)' },
          { name: 'review_due', readonly: true, label: 'Review Due (publish/revision + 12 months)' },
          { name: 'reviewed_by_id', readonly: true, label: 'Reviewed By (Publish action)' },
          { name: 'reviewed_on', readonly: true, label: 'Reviewed On' },
          { name: 'version', readonly: true, label: 'Version (rises on publish and revision)' },
          { name: 'content_hash', readonly: true, label: 'Content Hash (offline delta sync)' }
        ] },
      { title: 'Content', fields: [
          { name: 'content', required: true, type: 'text', label: 'Content (English)' },
          { name: 'content_bn', type: 'text', label: 'Content (Bengali)' }
        ] }
    ]
  },

  'M61-form-tree': {
    kind: 'model_form',
    model: 'fix.knowledge.tree',
    title: 'Troubleshooting Tree',
    back: 'M61-trees',
    status: { field: 'state', labels: {
      draft: 'Draft', published: 'Published', archived: 'Archived' } },
    sections: [
      { title: 'Tree', note: 'Entry symptom and the ordered decision nodes; publishing makes it available for dispatch. A tree drives live decisions, so it publishes under the same review gate as an article (K1).',
        fields: [
          { name: 'name', required: true, label: 'Tree Name' },
          { name: 'device_brand', label: 'Brand' },
          { name: 'device_model', label: 'Model / Chassis' },
          { name: 'fault_symptom', label: 'Entry Symptom' },
          { name: 'linked_article_id', label: 'Root Article' },
          { name: 'tags', label: 'Search Tags (electrical/battery/high-voltage = safety-critical)' },
          { name: 'safety_critical', readonly: true, label: 'Safety-Critical (computed)' },
          { name: 'reviewed_by_id', readonly: true, label: 'Reviewed By (Publish action)' },
          { name: 'reviewed_on', readonly: true, label: 'Reviewed On' }
        ] },
      { title: 'Decision Nodes', fields: [
          { name: 'nodes_text', type: 'text', label: 'Nodes (question -> branch -> action)' }
        ] }
    ]
  },

  'M61-form-bulletin': {
    kind: 'model_form',
    model: 'fix.knowledge.bulletin',
    title: 'Bulletin',
    back: 'M61-bulletins',
    status: { field: 'state', labels: {
      received: 'Received', distributed: 'Distributed', closed: 'Closed' } },
    sections: [
      { title: 'Brand Bulletin', note: 'Recall, technical bulletin, advisory or parts-change notice. Severity and type LOCK once distributed — the field acted on that classification; a correction is a new bulletin (A10 P1-7).',
        fields: [
          { name: 'name', required: true, label: 'Bulletin Reference' },
          { name: 'brand', required: true, label: 'Brand' },
          { name: 'bulletin_type', required: true, label: 'Bulletin Type' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'severity', required: true, label: 'Severity' }
        ] },
      { title: 'Recall Scope (required for recalls)', note: 'A recall distributes only over what it recalls: affected models (comma-separated) and/or serials in scope, to named recipient branches. Distribution hands it to M09 as an active recall campaign and flags M01 open orders on the affected models (A10 P1-7).',
        fields: [
          { name: 'affected_models', label: 'Affected Models (comma-separated)' },
          { name: 'serial_scope', label: 'Serials in Scope' }
        ] },
      { title: 'Distribution', note: 'Each branch acknowledges its own line (its duty officer or branch staff); the Quality Manager closes the recall once every branch has answered.',
        fields: [
          { name: 'recipients_total', readonly: true, label: 'Recipient Branches' },
          { name: 'recipients_acknowledged', readonly: true, label: 'Acknowledged' }
        ] },
      { title: 'Summary', fields: [
          { name: 'summary', type: 'text', label: 'Summary' }
        ] }
    ]
  },

  'M61-form-recipient': {
    kind: 'model_form',
    model: 'fix.knowledge.bulletin.recipient',
    title: 'Bulletin Recipient',
    back: 'M61-recipients',
    sections: [
      { title: 'Recipient Branch', note: 'One line per branch per bulletin: who must hold it. The acknowledgement stamps itself when the branch answers — it is never typed (A10 P1-7).',
        fields: [
          { name: 'bulletin_id', required: true, label: 'Bulletin' },
          { name: 'branch_id', required: true, label: 'Recipient Branch / Hub' },
          { name: 'employee_id', label: 'Duty Officer (optional — they and branch staff acknowledge)' },
          { name: 'note', label: 'Instruction to the Branch' },
          { name: 'acknowledged_on', readonly: true, label: 'Acknowledged On (stamped by the branch)' },
          { name: 'acknowledged_by_id', readonly: true, label: 'Acknowledged By' }
        ] }
    ]
  },

  'M61-form-media': {
    kind: 'model_form',
    model: 'fix.knowledge.media',
    title: 'Media Asset',
    back: 'M61-media',
    sections: [
      { title: 'Media', note: 'Video, image, diagram or audio attached to an article; offline availability is a distribution decision.',
        fields: [
          { name: 'name', required: true, label: 'Media Name' },
          { name: 'media_type', required: true, label: 'Media Type' },
          { name: 'article_id', label: 'Attached Article' },
          { name: 'url', label: 'Asset URL' },
          { name: 'duration_min', label: 'Duration (minutes)' },
          { name: 'size_mb', label: 'Size (MB)' },
          { name: 'offline_available', label: 'Available Offline' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M61:Coverage Analysis': 'M61-rpt-coverage',
  'M61:Article Usage & Usefulness': 'M61-rpt-usage',
  'M61:Gap Report by Brand/Model': 'M61-rpt-gap',
  'M61:Contribution Leaderboard': 'M61-rpt-contrib',
  'M61:Recall Routing': 'M61-recalls'
};

export const FORM_MODELS = {
  'M61:Article': 'fix.knowledge.article',
  'M61:Troubleshooting Tree': 'fix.knowledge.tree',
  'M61:Bulletin': 'fix.knowledge.bulletin',
  'M61:Bulletin Recipient': 'fix.knowledge.bulletin.recipient'
};

export const FORM_CHIPS = {
  'M61:Article': 'M61-form-article',
  'M61:Troubleshooting Tree': 'M61-form-tree',
  'M61:Bulletin': 'M61-form-bulletin',
  'M61:Bulletin Recipient': 'M61-form-recipient',
  'M61:__by_model__': {
    'fix.knowledge.article': 'M61-form-article',
    'fix.knowledge.tree': 'M61-form-tree',
    'fix.knowledge.bulletin': 'M61-form-bulletin',
    'fix.knowledge.bulletin.recipient': 'M61-form-recipient',
    'fix.knowledge.media': 'M61-form-media'
  },
  'M61:__by_screen__': {
    'M61-articles': 'M61-form-article',
    'M61-review': 'M61-form-article',
    'M61-manuals': 'M61-form-article',
    'M61-context': 'M61-form-article',
    'M61-offline': 'M61-form-article',
    'M61-trees': 'M61-form-tree',
    'M61-bulletins': 'M61-form-bulletin',
    'M61-recipients': 'M61-form-recipient',
    'M61-media': 'M61-form-media'
  }
};

export const CREATE = {
  M61: { screen: 'M61-form-article', model: 'fix.knowledge.article', label: 'Article' }
};
