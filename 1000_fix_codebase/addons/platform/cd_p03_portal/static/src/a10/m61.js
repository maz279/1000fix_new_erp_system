/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M61 Knowledge & Technical Library.
 * Registry-faithful: 4 groups / 8 sub-modules (freg 48).
 *
 * M61 capture audit (2026-11-18): every sub-module page now captures the
 * record it covers. Before, pages 3 (Technical Library), 4 (Search &
 * Surfacing) and 5 (Offline Distribution) offered nothing, pages 6
 * (Feedback & Health) and 8 (Expertise Mapping) offered "+ New Article", the
 * Review Workflow list re-listed articles with a Publish button that asked
 * for a reviewer's numeric user ID, and there was no field capture, review
 * request, library entry, operational link, offline set or feedback record. */

export const MODULE = {
  area: 'A10', code: 'M61', en: 'Knowledge & Technical Library', title: 'M61 · Knowledge & Technical Library',
  bn: 'জ্ঞান ও কারিগরি গ্রন্থাগার', icon: '📚',
  desc: 'Article library across seven types, field captures and their improvement queue, review workflow and version history, troubleshooting trees with decision steps, manuals and schematics with their licence terms, operational links that surface content on a job, technician offline sets, usefulness feedback and article health, expertise, and brand bulletins and recalls.',
  kpis: [
    { l: 'Articles', m: 'articles' },
    { l: 'Coverage (Serviced Models)', m: 'coverage_serviced', suffix: '%' },
    { l: 'Offline Articles', m: 'offline_articles' },
    { l: 'Resolved It (Feedback)', m: 'usefulness_score', suffix: '%' },
    { l: 'Reviews Due', m: 'reviews_due' },
    { l: 'Brand Bulletins MTD', m: 'brand_bulletins_mtd' }
  ],
  groups: [
    { en: 'Authoring', screens: [
      { id: 'M61-articles', en: 'Article Library (7 types)', bn: 'নিবন্ধ লাইব্রেরি', t: 'g' },
      { id: 'M61-captures', en: 'Field Captures & Improvement Queue', bn: 'মাঠের জ্ঞান সংগ্রহ', t: 'g' },
      { id: 'M61-review', en: 'Review Workflow', bn: 'পর্যালোচনা প্রবাহ', t: 'g' },
      { id: 'M61-versions', en: 'Version History', bn: 'সংস্করণের ইতিহাস', t: 'g' },
      { id: 'M61-trees', en: 'Troubleshooting Trees', bn: 'সমস্যা নিরসন ট্রি', t: 'g' }
    ]},
    { en: 'Technical Library', screens: [
      { id: 'M61-manuals', en: 'Manuals & Schematics', bn: 'ম্যানুয়াল', t: 'g' },
      { id: 'M61-media', en: 'Video & Image Content', bn: 'ভিডিও', t: 'g' }
    ]},
    { en: 'Distribution', screens: [
      { id: 'M61-links', en: 'Operational Links', bn: 'কার্যক্রম সংযোগ', t: 'g' },
      { id: 'M61-context', en: 'Context-Aware Surfacing', bn: 'প্রসঙ্গ-সচেতন', t: 'g' },
      { id: 'M61-offline-sets', en: 'Technician Offline Sets', bn: 'টেকনিশিয়ান অফলাইন সেট', t: 'g' },
      { id: 'M61-offline', en: 'Offline Distribution', bn: 'অফলাইন বিতরণ', t: 'g' }
    ]},
    { en: 'Feedback', screens: [
      { id: 'M61-feedback', en: 'Usefulness Feedback', bn: 'উপযোগিতা মতামত', t: 'g' },
      { id: 'M61-health', en: 'Article Health & Gaps', bn: 'নিবন্ধ স্বাস্থ্য', t: 'r' },
      { id: 'M61-expertise', en: 'Expertise Map', bn: 'দক্ষতার মানচিত্র', t: 'r' },
      { id: 'M61-bulletins', en: 'Brand Bulletins & Recalls', bn: 'ব্র্যান্ড বুলেটিন', t: 'g' },
      { id: 'M61-recipients', en: 'Recall Recipients', bn: 'প্রাপক শাখা', t: 'g' },
      { id: 'M61-recalls', en: 'Recall Routing', bn: 'রিকল রাউটিং', t: 'r' }
    ]}
  ],
  reports: ['Coverage Analysis', 'Article Usage & Usefulness', 'Gap Report by Brand/Model', 'Contribution Leaderboard', 'Recall Routing', 'Expertise Map'],
  forms: ['Article', 'Field Capture', 'Review Request', 'Troubleshooting Tree', 'Library Entry', 'Media Asset', 'Knowledge Link', 'Offline Set', 'Usefulness Feedback', 'Bulletin', 'Bulletin Recipient'],
  cross: ['M02 Dispatch knowledge links', 'M32 Bengali NLU', 'M22 Training', 'M23 QMS', 'M01 Fault codes', 'M37 Device models'],
  freg: { src: 48, sub: [
    ['1', 'Authoring & Versioning', 8, { model: 'fix.knowledge.article', cols: ['article_code', 'name', 'category', 'version', 'review_status', 'state'], screens: ['M61-articles', 'M61-captures', 'M61-review', 'M61-versions'], reports: ['Contribution Leaderboard'], forms: ['Article', 'Field Capture', 'Review Request'] }],
    ['2', 'Troubleshooting Trees', 7, { model: 'fix.knowledge.tree', cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'node_count', 'state'], screens: ['M61-trees'], reports: [], forms: ['Troubleshooting Tree', 'Review Request', 'Knowledge Link'] }],
    ['3', 'Technical Library', 7, { model: 'fix.knowledge.library', cols: ['name', 'entry_type', 'brand_id', 'redistribution', 'state'], screens: ['M61-manuals', 'M61-media'], reports: ['Gap Report by Brand/Model'], forms: ['Library Entry', 'Media Asset'] }],
    ['4', 'Search & Surfacing', 7, { model: 'fix.knowledge.link', cols: ['article_id', 'tree_id', 'link_type', 'fault_code_id', 'device_model_id', 'brand_id', 'relevance_weight'], screens: ['M61-links', 'M61-context'], reports: ['Article Usage & Usefulness'], forms: ['Knowledge Link'] }],
    ['5', 'Offline Distribution', 5, { model: 'fix.knowledge.offline.set', cols: ['name', 'user_id', 'max_level', 'article_count', 'total_mb', 'budget_mb', 'last_synced_on'], screens: ['M61-offline-sets', 'M61-offline'], reports: [], forms: ['Offline Set'] }],
    ['6', 'Feedback & Health', 6, { model: 'fix.knowledge.feedback', cols: ['article_id', 'version', 'user_id', 'resolved', 'rating', 'captured_on'], screens: ['M61-feedback', 'M61-health'], reports: ['Coverage Analysis', 'Article Usage & Usefulness', 'Gap Report by Brand/Model'], forms: ['Usefulness Feedback'] }],
    ['7', 'Brand Bulletins', 4, { model: 'fix.knowledge.bulletin', cols: ['name', 'brand', 'bulletin_type', 'issued_on', 'severity'], screens: ['M61-bulletins', 'M61-recipients'], reports: ['Recall Routing'], forms: ['Bulletin', 'Bulletin Recipient'] }],
    /* derived from contribution, review and resolution (FR-KMS-035,
     * AUT-KMS-18): nothing is typed in here */
    ['8', 'Expertise Mapping', 4, { report: 'expertise_map', screens: ['M61-expertise'], reports: ['Expertise Map', 'Contribution Leaderboard'], forms: [] }]
  ] }
};

const PUBLISH_NOTE = 'Publishing is a Knowledge Publisher act over reviewed content: an approved review of the content as it stands names the reviewer; without one, a publisher who did not write it reviews it by publishing. Safety-tagged content publishes only through a review with the Quality Manager\'s sign-off (BRU-KMS-02/03).';

export const SCREENS = {
  'M61-articles': { kind: 'model_list', model: 'fix.knowledge.article', stateField: 'state',
    cols: ['article_code', 'name', 'category', 'device_brand', 'device_model', 'rework_level', 'version', 'review_status', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish Article' },
      { m: 'action_archive', l: 'Archive Article' }
    ] },
  'M61-captures': { kind: 'model_list', model: 'fix.knowledge.capture', stateField: 'state',
    cols: ['name', 'captured_by_id', 'captured_on', 'device_brand', 'device_model', 'fault_code_id', 'reviewer_id', 'article_id', 'state'],
    actions: [
      { m: 'action_take', l: 'Take into the Queue' },
      { m: 'action_draft_article', l: 'Structure into a Draft Article' },
      { m: 'action_merge', l: 'Merge into Existing Article',
        asks: [{ label: 'Reference code (or number) of the article that already covers it', kwarg: 'article_ref' }] }
    ] },
  'M61-review': { kind: 'model_list', model: 'fix.knowledge.review', stateField: 'state',
    cols: ['name', 'article_id', 'tree_id', 'reviewer_id', 'requested_by_id', 'safety_required', 'content_changed', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (Technical Review)',
        asks: [{ label: 'Comments for the author (optional)', kwarg: 'note' }] },
      { m: 'action_return', l: 'Return to Author',
        asks: [{ label: 'What should the author change?', kwarg: 'note' }] },
      { m: 'action_safety_approve', l: 'Safety Sign-off (Quality Manager)',
        asks: [{ label: 'Sign-off note (optional)', kwarg: 'note' }] },
      { m: 'action_cancel', l: 'Cancel Request' }
    ] },
  'M61-versions': { kind: 'model_list', model: 'fix.knowledge.article.version', create: false,
    cols: ['article_id', 'version', 'name', 'change_note', 'changed_by_id', 'changed_on', 'reviewed_by_id', 'content_hash'] },
  'M61-trees': { kind: 'model_list', model: 'fix.knowledge.tree', stateField: 'state',
    cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'node_count', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish Tree' },
      { m: 'action_archive', l: 'Archive Tree' }
    ] },
  'M61-manuals': { kind: 'model_list', model: 'fix.knowledge.library', stateField: 'state',
    cols: ['name', 'entry_type', 'brand_id', 'model_text', 'source', 'redistribution', 'offline_allowed', 'state'],
    actions: [
      { m: 'action_make_available', l: 'Make Available' },
      { m: 'action_withdraw', l: 'Withdraw',
        asks: [{ label: 'Why is it withdrawn? (new edition, terms ended…)', kwarg: 'reason' }] }
    ] },
  'M61-media': { kind: 'model_list', model: 'fix.knowledge.media',
    cols: ['name', 'media_type', 'article_id', 'url', 'duration_min', 'size_mb', 'offline_available'] },
  'M61-links': { kind: 'model_list', model: 'fix.knowledge.link',
    cols: ['article_id', 'tree_id', 'link_type', 'fault_code_id', 'device_model_id', 'brand_id', 'relevance_weight', 'linked_by_id'] },
  'M61-context': { kind: 'model_list', model: 'fix.knowledge.article', create: false,
    cols: ['name', 'device_brand', 'device_model', 'fault_symptom', 'category', 'resolution_rate', 'avg_rating', 'state'] },
  'M61-offline-sets': { kind: 'model_list', model: 'fix.knowledge.offline.set',
    cols: ['name', 'user_id', 'max_level', 'article_count', 'stale_count', 'total_mb', 'budget_mb', 'over_budget_count', 'computed_on', 'last_synced_on'],
    actions: [
      { m: 'action_compute', l: 'Compute the Set' }
    ] },
  'M61-offline': { kind: 'model_list', model: 'fix.knowledge.article', stateField: 'state', create: false,
    cols: ['article_code', 'name', 'category', 'offline_available', 'version', 'content_hash', 'state'] },
  'M61-feedback': { kind: 'model_list', model: 'fix.knowledge.feedback',
    cols: ['article_id', 'version', 'user_id', 'service_order_id', 'resolved', 'rating', 'captured_offline', 'captured_on'] },
  'M61-health': { kind: 'table_report', module: 'M61', report: 'usage_usefulness', title: 'Article Health & Gaps', period: false },
  'M61-expertise': { kind: 'table_report', module: 'M61', report: 'expertise_map', title: 'Expertise Map', period: false },
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
    tabs: [
      { id: 'article', label: 'Article & Linkage', bn: 'নিবন্ধ', icon: '📄', badge: '10' },
      { id: 'content', label: 'Content', bn: 'বিষয়বস্তু', icon: '✍️', badge: '3' },
      { id: 'review', label: 'Review, Versions & Usefulness', bn: 'পর্যালোচনা', icon: '✅', badge: '14' }
    ],
    sections: [
      { tab: 'article', title: 'Article', note: 'Seven article types; the brand/model/symptom fields are what context-aware surfacing matches on (add fault-code and catalogue links on the Search & Surfacing page), and offline articles are synced to technicians.',
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
          { name: 'offline_available', label: 'Available Offline' }
        ] },
      { tab: 'content', title: 'Content', note: 'A published article may still be improved: the edit is a revision, its version rises and the devices re-sync it. Each published version is kept in the Version History.',
        fields: [
          { name: 'content', required: true, type: 'text', label: 'Content (English)' },
          { name: 'content_bn', type: 'text', label: 'Content (Bengali)' },
          { name: 'original_capture_text', readonly: true, type: 'text', label: 'Contributor\'s Original Words (from the field capture)' }
        ] },
      { tab: 'review', title: 'Review & Publication', note: PUBLISH_NOTE,
        fields: [
          { name: 'safety_critical', readonly: true, label: 'Safety-Critical (computed)' },
          { name: 'review_status', readonly: true, label: 'Latest Review' },
          { name: 'owner_id', readonly: true, label: 'Owner (stamped at creation)' },
          { name: 'contributor_id', readonly: true, label: 'Contributor (field capture)' },
          { name: 'reviewed_by_id', readonly: true, label: 'Reviewed By' },
          { name: 'reviewed_on', readonly: true, label: 'Reviewed On' },
          { name: 'review_due', readonly: true, label: 'Review Due (publish/revision + 12 months)' },
          { name: 'version', readonly: true, label: 'Version (rises on publish and revision)' },
          { name: 'content_hash', readonly: true, label: 'Content Hash (offline delta sync)' }
        ] },
      { tab: 'review', title: 'Usefulness (from feedback)', note: 'Measured from the Usefulness Feedback page. Three "did not resolve" answers in a row, or a low average rating, flag the article for its owner to revise or retire (AUT-KMS-17); the next publication clears the flag.',
        fields: [
          { name: 'feedback_count', readonly: true, label: 'Feedback Received' },
          { name: 'resolution_rate', readonly: true, label: 'Resolved It (%)' },
          { name: 'avg_rating', readonly: true, label: 'Average Rating (1-5)' },
          { name: 'flagged_on', readonly: true, label: 'Flagged On' },
          { name: 'flag_reason', readonly: true, label: 'Why Flagged' }
        ] }
    ]
  },

  'M61-form-capture': {
    kind: 'model_form',
    model: 'fix.knowledge.capture',
    title: 'Field Capture',
    back: 'M61-captures',
    status: { field: 'state', labels: {
      queued: 'In Improvement Queue', taken: 'Being Structured', drafted: 'Draft Article Created', merged: 'Merged into Existing Article' } },
    tabs: [
      { id: 'capture', label: 'What You Did', bn: 'আপনি কী করেছেন', icon: '🛠️', badge: '8' },
      { id: 'queue', label: 'Improvement Queue', bn: 'উন্নয়ন সারি', icon: '📥', badge: '7' }
    ],
    sections: [
      { tab: 'capture', title: 'Capture a Solution (FR-KMS-023/024)', note: 'Write it the way you would tell a colleague — Bengali is fine, rough is fine. Add a photo or a voice note. Name the job and its device brand, model and fault code are filled in for you. Your words are kept as you wrote them (BRU-KMS-08/09); you can correct them only while the capture waits in the queue.',
        fields: [
          { name: 'service_order_id', label: 'Job (Service Order)' },
          { name: 'raw_text', required: true, type: 'text', label: 'What You Did (your own words)' },
          { name: 'device_brand', label: 'Brand' },
          { name: 'device_model', label: 'Model' },
          { name: 'fault_code_id', label: 'Fault Code' },
          { name: 'fault_symptom', label: 'Symptom' },
          { name: 'rework_level', label: 'Repair Level' },
          { name: 'photo_attachment_id', label: 'Photo' },
          { name: 'voice_attachment_id', label: 'Voice Note' }
        ] },
      { tab: 'queue', title: 'Improvement Queue (FR-KMS-027)', note: 'A Knowledge Publisher other than the contributor takes the capture and either structures it into a draft article (pre-filled, carrying the original words and the fault-code link) or merges it into the article that already covers it. A capture is never discarded.',
        fields: [
          { name: 'name', readonly: true, label: 'Capture No.' },
          { name: 'captured_by_id', readonly: true, label: 'Captured By' },
          { name: 'captured_on', readonly: true, label: 'Captured On' },
          { name: 'reviewer_id', readonly: true, label: 'Reviewer / Technical Writer' },
          { name: 'taken_on', readonly: true, label: 'Taken On' },
          { name: 'article_id', readonly: true, label: 'Resulting Article' },
          { name: 'handled_on', readonly: true, label: 'Structured On' }
        ] }
    ]
  },

  'M61-form-review': {
    kind: 'model_form',
    model: 'fix.knowledge.review',
    title: 'Review Request',
    back: 'M61-review',
    status: { field: 'state', labels: {
      requested: 'Awaiting Review', reviewed: 'Reviewed — Awaiting Safety Sign-off', approved: 'Approved', returned: 'Returned to Author', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'request', label: 'Request', bn: 'অনুরোধ', icon: '📝', badge: '4' },
      { id: 'decision', label: 'Review & Sign-off', bn: 'সিদ্ধান্ত', icon: '🖋️', badge: '10' }
    ],
    sections: [
      { tab: 'request', title: 'Ask for a Technical Review (BRU-KMS-02)', note: 'Name one draft article or one draft tree and a Knowledge Publisher who did not write it. The approval covers the content exactly as it stands now: an edit after the request needs a new review.',
        fields: [
          { name: 'article_id', label: 'Article' },
          { name: 'tree_id', label: 'Troubleshooting Tree' },
          { name: 'reviewer_id', required: true, label: 'Reviewer (Knowledge Publisher, not the author)' },
          { name: 'request_note', type: 'text', label: 'What to Look At' }
        ] },
      { tab: 'decision', title: 'Decision', note: 'The reviewer approves or returns it with comments (kept). Safety-critical content then needs the Quality Manager\'s sign-off — someone who neither wrote nor reviewed it (BRU-KMS-03). Publishing reads the approved review.',
        fields: [
          { name: 'name', readonly: true, label: 'Review No.' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'requested_on', readonly: true, label: 'Requested On' },
          { name: 'safety_required', readonly: true, label: 'Safety Sign-off Required' },
          { name: 'content_changed', readonly: true, label: 'Content Changed Since Request' },
          { name: 'comments', readonly: true, type: 'text', label: 'Reviewer\'s Comments' },
          { name: 'decided_on', readonly: true, label: 'Reviewed On' },
          { name: 'safety_approved_by_id', readonly: true, label: 'Safety Sign-off By' },
          { name: 'safety_approved_on', readonly: true, label: 'Safety Sign-off On' },
          { name: 'content_hash', readonly: true, label: 'Content Reviewed (hash)' }
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
    lines: { field: 'node_ids', title: 'Decision Steps (FR-KMS-005)',
      note: 'One row per step: a question, check, measurement or outcome, the reading that passes it and where each answer leads. Steps change only while the tree is a draft.',
      fields: [
        { name: 'sequence', label: 'Step' },
        { name: 'node_type', label: 'Type', required: true },
        { name: 'text', label: 'Step (English)', required: true },
        { name: 'text_bn', label: 'Step (Bengali)' },
        { name: 'expected', label: 'Expected Reading' },
        { name: 'yes_next', label: 'If Yes / Pass →' },
        { name: 'no_next', label: 'If No / Fail →' },
        { name: 'article_id', label: 'Procedure' },
        { name: 'safety_note', label: 'Safety Note' }
      ] },
    sections: [
      { title: 'Tree', note: 'Entry symptom and the decision steps below; publishing makes it available for dispatch. A tree drives live decisions, so it publishes under the same review gate as an article (BRU-KMS-02/03).',
        fields: [
          { name: 'name', required: true, label: 'Tree Name' },
          { name: 'device_brand', label: 'Brand' },
          { name: 'device_model', label: 'Model / Chassis' },
          { name: 'fault_symptom', label: 'Entry Symptom' },
          { name: 'linked_article_id', label: 'Root Article' },
          { name: 'tags', label: 'Search Tags (electrical/battery/high-voltage = safety-critical)' },
          { name: 'safety_critical', readonly: true, label: 'Safety-Critical (computed)' },
          { name: 'reviewed_by_id', readonly: true, label: 'Reviewed By' },
          { name: 'reviewed_on', readonly: true, label: 'Reviewed On' }
        ] },
      { title: 'Notes', fields: [
          { name: 'nodes_text', type: 'text', label: 'Free-text notes (the steps are the grid above)' }
        ] }
    ]
  },

  'M61-form-library': {
    kind: 'model_form',
    model: 'fix.knowledge.library',
    title: 'Library Entry',
    back: 'M61-manuals',
    status: { field: 'state', labels: { draft: 'Draft', available: 'Available', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'entry', label: 'Entry & Index', bn: 'এন্ট্রি', icon: '📘', badge: '8' },
      { id: 'terms', label: 'Licence & Availability', bn: 'লাইসেন্স', icon: '⚖️', badge: '7' }
    ],
    sections: [
      { tab: 'entry', title: 'Manual or Diagram (FR-KMS-004)', note: 'Indexed by brand and model so a technician finds it from the job. Upload the file, or give the M24 document reference where it is stored.',
        fields: [
          { name: 'name', required: true, label: 'Title' },
          { name: 'entry_type', required: true, label: 'Entry Type' },
          { name: 'brand_id', required: true, label: 'Brand' },
          { name: 'device_model_ids', label: 'Models Covered' },
          { name: 'model_text', label: 'Other Models (not in the catalogue)' },
          { name: 'document_attachment_id', label: 'Manual / Diagram File' },
          { name: 'document_ref', label: 'M24 Document Reference' },
          { name: 'page_count', label: 'Pages' }
        ] },
      { tab: 'terms', title: 'Use Within the Brand\'s Terms (BRU-KMS-16)', note: 'Record where it came from and the terms it may be used under. Only "Technicians — including offline devices" lets it reach an offline set. A publisher makes it available once the file, the models and the terms are recorded; after that they are fixed (a new edition is a new entry).',
        fields: [
          { name: 'source', required: true, label: 'Source' },
          { name: 'licence_terms', type: 'text', label: 'Licence / Usage Terms' },
          { name: 'redistribution', required: true, label: 'Who May Use It' },
          { name: 'offline_allowed', readonly: true, label: 'May Go Offline' },
          { name: 'made_available_by_id', readonly: true, label: 'Made Available By' },
          { name: 'made_available_on', readonly: true, label: 'Available Since' },
          { name: 'withdrawn_reason', readonly: true, label: 'Why Withdrawn' }
        ] }
    ]
  },

  'M61-form-media': {
    kind: 'model_form',
    model: 'fix.knowledge.media',
    title: 'Media Asset',
    back: 'M61-media',
    sections: [
      { title: 'Media', note: 'Video, image, diagram or audio attached to an article; offline availability is a distribution decision, and its size counts against a technician\'s offline budget.',
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
  },

  'M61-form-link': {
    kind: 'model_form',
    model: 'fix.knowledge.link',
    title: 'Knowledge Link',
    back: 'M61-links',
    sections: [
      { title: 'Bind Content to the Operational Spine (FR-KMS-006)', note: 'One article or one tree, and exactly one of: a fault code, a device model or a brand from the catalogue (one link per subject). Context-aware surfacing ranks what a job shows by these links, then by how often the content resolved the fault (FR-KMS-014/015).',
        fields: [
          { name: 'article_id', label: 'Article' },
          { name: 'tree_id', label: 'Troubleshooting Tree' },
          { name: 'fault_code_id', label: 'Fault Code' },
          { name: 'device_model_id', label: 'Device Model' },
          { name: 'brand_id', label: 'Brand' },
          { name: 'relevance_weight', label: 'Relevance (1-10)' },
          { name: 'link_type', readonly: true, label: 'Linked To' },
          { name: 'linked_by_id', readonly: true, label: 'Linked By' }
        ] }
    ]
  },

  'M61-form-offline-set': {
    kind: 'model_form',
    model: 'fix.knowledge.offline.set',
    title: 'Offline Set',
    back: 'M61-offline-sets',
    tabs: [
      { id: 'scope', label: 'Scope & Budget', bn: 'পরিধি', icon: '🎯', badge: '5' },
      { id: 'set', label: 'Computed Set', bn: 'হিসাবকৃত সেট', icon: '📲', badge: '8' }
    ],
    sections: [
      { tab: 'scope', title: 'Technician Offline Scope (FR-KMS-017)', note: 'One set per technician: the brands and models they work on, the highest repair level they do, and the storage their device may give. Set up by a Knowledge Publisher.',
        fields: [
          { name: 'user_id', required: true, label: 'Technician' },
          { name: 'brand_ids', label: 'Brands' },
          { name: 'device_model_ids', label: 'Models' },
          { name: 'max_level', required: true, label: 'Up to Repair Level' },
          { name: 'budget_mb', required: true, label: 'Storage Budget (MB)' }
        ] },
      { tab: 'set', title: 'What the Device Holds (FR-KMS-018, BRU-KMS-05)', note: '"Compute the Set" takes only published, offline-flagged articles in scope, the ones linked to the technician\'s models first, within the budget. Archiving an article removes it from every set; the device reports each completed sync.',
        fields: [
          { name: 'name', readonly: true, label: 'Set No.' },
          { name: 'article_ids', readonly: true, label: 'Articles in the Set' },
          { name: 'article_count', readonly: true, label: 'Articles' },
          { name: 'stale_count', readonly: true, label: 'No Longer Published' },
          { name: 'total_mb', readonly: true, label: 'Size (MB)' },
          { name: 'over_budget_count', readonly: true, label: 'Left Out (Over Budget)' },
          { name: 'computed_on', readonly: true, label: 'Computed On' },
          { name: 'last_synced_on', readonly: true, label: 'Last Synced On' }
        ] }
    ]
  },

  'M61-form-feedback': {
    kind: 'model_form',
    model: 'fix.knowledge.feedback',
    title: 'Usefulness Feedback',
    back: 'M61-feedback',
    sections: [
      { title: 'Did This Resolve It? (FR-KMS-030)', note: 'Given once, by the person who used the published article, on its current version, and kept as given. It sets the article\'s resolved rate and rating, and repeated "no" answers flag it for revision (AUT-KMS-17).',
        fields: [
          { name: 'article_id', required: true, label: 'Article' },
          { name: 'service_order_id', label: 'Job (Service Order)' },
          { name: 'resolved', required: true, label: 'Did This Resolve It?' },
          { name: 'rating', required: true, label: 'Rating (1-5)' },
          { name: 'comment', type: 'text', label: 'Comment / Suggested Improvement' },
          { name: 'captured_offline', label: 'Given Offline' },
          { name: 'version', readonly: true, label: 'Version Rated' },
          { name: 'user_id', readonly: true, label: 'Given By' },
          { name: 'captured_on', readonly: true, label: 'Given On' }
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
  }
};

export const REPORT_ROUTES = {
  'M61:Coverage Analysis': 'M61-rpt-coverage',
  'M61:Article Usage & Usefulness': 'M61-rpt-usage',
  'M61:Gap Report by Brand/Model': 'M61-rpt-gap',
  'M61:Contribution Leaderboard': 'M61-rpt-contrib',
  'M61:Recall Routing': 'M61-recalls',
  'M61:Expertise Map': 'M61-expertise'
};

export const FORM_MODELS = {
  'M61:Article': 'fix.knowledge.article',
  'M61:Field Capture': 'fix.knowledge.capture',
  'M61:Review Request': 'fix.knowledge.review',
  'M61:Troubleshooting Tree': 'fix.knowledge.tree',
  'M61:Library Entry': 'fix.knowledge.library',
  'M61:Media Asset': 'fix.knowledge.media',
  'M61:Knowledge Link': 'fix.knowledge.link',
  'M61:Offline Set': 'fix.knowledge.offline.set',
  'M61:Usefulness Feedback': 'fix.knowledge.feedback',
  'M61:Bulletin': 'fix.knowledge.bulletin',
  'M61:Bulletin Recipient': 'fix.knowledge.bulletin.recipient'
};

export const FORM_CHIPS = {
  'M61:Article': 'M61-form-article',
  'M61:Field Capture': 'M61-form-capture',
  'M61:Review Request': 'M61-form-review',
  'M61:Troubleshooting Tree': 'M61-form-tree',
  'M61:Library Entry': 'M61-form-library',
  'M61:Media Asset': 'M61-form-media',
  'M61:Knowledge Link': 'M61-form-link',
  'M61:Offline Set': 'M61-form-offline-set',
  'M61:Usefulness Feedback': 'M61-form-feedback',
  'M61:Bulletin': 'M61-form-bulletin',
  'M61:Bulletin Recipient': 'M61-form-recipient',
  'M61:__by_model__': {
    'fix.knowledge.article': 'M61-form-article',
    'fix.knowledge.capture': 'M61-form-capture',
    'fix.knowledge.review': 'M61-form-review',
    'fix.knowledge.tree': 'M61-form-tree',
    'fix.knowledge.library': 'M61-form-library',
    'fix.knowledge.media': 'M61-form-media',
    'fix.knowledge.link': 'M61-form-link',
    'fix.knowledge.offline.set': 'M61-form-offline-set',
    'fix.knowledge.feedback': 'M61-form-feedback',
    'fix.knowledge.bulletin': 'M61-form-bulletin',
    'fix.knowledge.bulletin.recipient': 'M61-form-recipient'
  },
  'M61:__by_screen__': {
    'M61-articles': 'M61-form-article',
    'M61-captures': 'M61-form-capture',
    'M61-review': 'M61-form-review',
    'M61-trees': 'M61-form-tree',
    'M61-manuals': 'M61-form-library',
    'M61-media': 'M61-form-media',
    'M61-links': 'M61-form-link',
    'M61-context': 'M61-form-article',
    'M61-offline-sets': 'M61-form-offline-set',
    'M61-offline': 'M61-form-article',
    'M61-feedback': 'M61-form-feedback',
    'M61-bulletins': 'M61-form-bulletin',
    'M61-recipients': 'M61-form-recipient'
  }
};

export const CREATE = {
  M61: { screen: 'M61-form-article', model: 'fix.knowledge.article', label: 'Article' }
};
