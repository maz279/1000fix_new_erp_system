/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M61 Knowledge & Technical Library.
 * Registry-faithful: 4 groups / 9 screens / 4 reports / 3 forms / freg 48. */

export const MODULE = {
  area: 'A10', code: 'M61', en: 'Knowledge & Technical Library', title: 'M61 · Knowledge & Technical Library',
  bn: 'জ্ঞান ও কারিগরি গ্রন্থাগার', icon: '📚',
  desc: 'Article library across seven types, troubleshooting trees, review workflow, manuals and schematics, video and image content, context-aware surfacing to faults, offline distribution, article health and gaps, and brand bulletins and recalls.',
  kpis: [
    { l: 'Articles', m: 'articles' },
    { l: 'Coverage (Top Faults)', m: 'coverage_top_faults', suffix: '%' },
    { l: 'Offline Synced', m: 'offline_synced_techs' },
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
      { id: 'M61-bulletins', en: 'Brand Bulletins & Recalls', bn: 'ব্র্যান্ড বুলেটিন', t: 'g' }
    ]}
  ],
  reports: ['Coverage Analysis', 'Article Usage & Usefulness', 'Gap Report by Brand/Model', 'Contribution Leaderboard'],
  forms: ['Article', 'Troubleshooting Tree', 'Bulletin'],
  cross: ['M02 Dispatch knowledge links', 'M32 Bengali NLU', 'M22 Training', 'M23 QMS'],
  freg: { src: 48, sub: [
    ['1', 'Authoring & Versioning', 8, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'category', 'version', 'state'], screens: ['M61-articles', 'M61-review'] }],
    ['2', 'Troubleshooting Trees', 7, { model: 'fix.knowledge.tree', cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'state'], screens: ['M61-trees'] }],
    ['3', 'Technical Library', 7, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'category', 'device_brand', 'device_model'], screens: ['M61-manuals', 'M61-media'], domain: [['category', 'in', ['schematic', 'device_guide', 'repair_procedure']]] }],
    ['4', 'Search & Surfacing', 7, { model: 'fix.knowledge.article', cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'views'], screens: ['M61-context'], domain: [['state', '=', 'published']] }],
    ['5', 'Offline Distribution', 5, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'category', 'version', 'content_hash'], screens: ['M61-offline'], domain: [['offline_available', '=', true]] }],
    ['6', 'Feedback & Health', 6, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'views', 'helpful_votes', 'state'], screens: ['M61-health'] }],
    ['7', 'Brand Bulletins', 4, { model: 'fix.knowledge.bulletin', cols: ['name', 'brand', 'bulletin_type', 'issued_on', 'severity'], screens: ['M61-bulletins'] }],
    ['8', 'Expertise Mapping', 4, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'device_brand', 'rework_level', 'category'], screens: ['M61-articles'] }]
  ] }
};

export const SCREENS = {
  'M61-articles': { kind: 'model_list', model: 'fix.knowledge.article', stateField: 'state',
    cols: ['article_code', 'name', 'category', 'device_brand', 'device_model', 'rework_level', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish Article' }] },
  'M61-trees': { kind: 'model_list', model: 'fix.knowledge.tree', stateField: 'state',
    cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish Tree' }] },
  'M61-review': { kind: 'model_list', model: 'fix.knowledge.article', stateField: 'state',
    cols: ['article_code', 'name', 'category', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish' }] },
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
    cols: ['name', 'brand', 'bulletin_type', 'issued_on', 'affected_models', 'severity', 'state'],
    actions: [{ m: 'action_distribute', l: 'Distribute' }] },

  /* Report chips -> their own computed pack */
  'M61-rpt-coverage': { kind: 'table_report', module: 'M61', report: 'coverage_analysis', title: 'Coverage Analysis', period: false },
  'M61-rpt-usage': { kind: 'table_report', module: 'M61', report: 'usage_usefulness', title: 'Article Usage & Usefulness', period: false },
  'M61-rpt-gap': { kind: 'table_report', module: 'M61', report: 'gap_report', title: 'Gap Report by Brand/Model', period: false },
  'M61-rpt-contrib': { kind: 'table_report', module: 'M61', report: 'contribution_leaderboard', title: 'Contribution Leaderboard', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M61-form-article': {
    kind: 'model_form',
    model: 'fix.knowledge.article',
    title: 'Article',
    back: 'M61-articles',
    status: { field: 'state', labels: {
      draft: 'Draft', published: 'Published', archived: 'Archived' } },
    sections: [
      { title: 'Article', note: 'Seven article types; the brand/model/symptom fields are what context-aware surfacing matches on, and offline articles are synced to technicians.',
        fields: [
          { name: 'name', required: true, label: 'Article Title (English)' },
          { name: 'title_bn', label: 'Article Title (Bengali)' },
          { name: 'article_code', label: 'Reference Code' },
          { name: 'category', required: true, label: 'Article Type' },
          { name: 'device_brand', label: 'Target Brand' },
          { name: 'device_model', label: 'Target Model' },
          { name: 'fault_symptom', label: 'Fault Symptom' },
          { name: 'rework_level', label: 'Rework Level' },
          { name: 'offline_available', label: 'Available Offline' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Tree', note: 'Entry symptom and the ordered decision nodes; publishing makes it available for dispatch.',
        fields: [
          { name: 'name', required: true, label: 'Tree Name' },
          { name: 'device_brand', label: 'Brand' },
          { name: 'device_model', label: 'Model / Chassis' },
          { name: 'fault_symptom', label: 'Entry Symptom' },
          { name: 'linked_article_id', label: 'Root Article' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Brand Bulletin', note: 'Recall, technical bulletin, advisory or parts-change notice; distributing marks it pushed to the field.',
        fields: [
          { name: 'name', required: true, label: 'Bulletin Reference' },
          { name: 'brand', required: true, label: 'Brand' },
          { name: 'bulletin_type', required: true, label: 'Bulletin Type' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'affected_models', label: 'Affected Models' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Summary', fields: [
          { name: 'summary', type: 'text', label: 'Summary' }
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
  'M61:Contribution Leaderboard': 'M61-rpt-contrib'
};

export const FORM_MODELS = {
  'M61:Article': 'fix.knowledge.article',
  'M61:Troubleshooting Tree': 'fix.knowledge.tree',
  'M61:Bulletin': 'fix.knowledge.bulletin'
};

export const FORM_CHIPS = {
  'M61:Article': 'M61-form-article',
  'M61:Troubleshooting Tree': 'M61-form-tree',
  'M61:Bulletin': 'M61-form-bulletin',
  'M61:__by_model__': {
    'fix.knowledge.article': 'M61-form-article',
    'fix.knowledge.tree': 'M61-form-tree',
    'fix.knowledge.bulletin': 'M61-form-bulletin',
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
    'M61-media': 'M61-form-media'
  }
};

export const CREATE = {
  M61: { screen: 'M61-form-article', model: 'fix.knowledge.article', label: 'Article' }
};
