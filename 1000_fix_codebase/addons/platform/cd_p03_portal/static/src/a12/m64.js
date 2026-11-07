/** @odoo-module **/
/* A12 · M64 Master Data Management. 3 groups / 6 screens / 4 reports / 3 forms / freg 52. */

export const MODULE = {
  area: 'A12', code: 'M64', en: 'Master Data Management', title: 'M64 · Master Data Management',
  bn: 'মাস্টার ডেটা', icon: '🗂️',
  desc: 'Steward-governed master data: steward requests with review and approval, data-quality rules per master field, governed code lists with bilingual entries, and golden-record coverage.',
  kpis: [
    { l: 'Steward Open', m: 'steward_open' },
    { l: 'Steward Total', m: 'steward_total' },
    { l: 'Change Requests Open', m: 'change_requests_open' },
    { l: 'Changes Applied', m: 'change_requests_applied' },
    { l: 'Duplicates Pending', m: 'duplicates_pending' },
    { l: 'Active DQ Rules', m: 'dq_rules' },
    { l: 'Measured Violations', m: 'dq_violations_measured' },
    { l: 'Published Lists', m: 'code_lists' },
    { l: 'Code Entries', m: 'code_entries' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M64-mdm-golden-rule', en: "Mdm Golden Rule", bn: "Mdm Golden Rule", t: 'g' },
      { id: 'M64-mdm-stewardship', en: "Mdm Stewardship", bn: "Mdm Stewardship", t: 'g' },
      { id: 'M64-mdm-change-request', en: "Mdm Change Request", bn: "Mdm Change Request", t: 'g' },
      { id: 'M64-mdm-match-rule', en: "Mdm Match Rule", bn: "Mdm Match Rule", t: 'g' },
      { id: 'M64-governed', en: 'Governed Attributes', bn: 'নিয়ন্ত্রিত বৈশিষ্ট্য', t: 'g' }
    ]},
    { en: 'Registry Completion', screens: [
      { id: 'M64-dedupe', en: 'Duplicate Detection', bn: 'Duplicate Detection', t: 'g' },
      { id: 'M64-xref', en: 'Cross-Reference Mapping', bn: 'Cross-Reference Mapping', t: 'g' },
      { id: 'M64-impact', en: 'Impact Analysis', bn: 'Impact Analysis', t: 'g' },
      { id: 'M64-lineage', en: 'Lineage', bn: 'Lineage', t: 'g' }
    ]},
    { en: 'Stewardship', screens: [
      { id: 'M64-stewardship', en: 'Stewardship Workflow', bn: 'স্টুয়ার্ড', t: 'g' },
      { id: 'M64-domains', en: 'Domain Register', bn: 'মাস্টার মডেল', t: 'r' }
    ]},
    { en: 'Data Quality', screens: [
      { id: 'M64-rules', en: 'DQ Rule Engine', bn: 'ডিকিউ নিয়ম', t: 'g' },
      { id: 'M64-scoring', en: 'Quality Scoring & Gating', bn: 'কভারেজ', t: 'r' }
    ]},
    { en: 'Code Lists', screens: [
      { id: 'M64-codelists', en: 'Code Lists', bn: 'কোড তালিকা', t: 'g' },
      { id: 'M64-entries', en: 'List Entries', bn: 'এন্ট্রি', t: 'g' }
    ]}
  ],
  reports: ['Steward Request Backlog', 'DQ Rule Register', 'Code List Usage', 'Golden Record Coverage'],
  forms: ['Change Request', 'Steward Request', 'DQ Rule', 'Code List Entry'],
  cross: ['M30 branch master', 'M33 golden party', 'M25 DQ dashboards'],
  freg: { src: 52, sub: [
    ['1', 'Stewardship', 10, { model: 'fix.mdm.steward', cols: ['name', 'request_type', 'res_model', 'steward_id', 'state'], screens: ['M64-stewardship', 'M64-mdm-stewardship', 'M64-domains'] }],
    ['2', 'Data Quality', 12, { model: 'fix.mdm.dq.rule', cols: ['code', 'name', 'res_model', 'rule_type', 'severity'], screens: ['M64-rules', 'M64-scoring'] }],
    ['3', 'Code Lists', 9, { model: 'fix.mdm.code.list', cols: ['code', 'name', 'domain_area', 'state'], screens: ['M64-codelists', 'M64-entries', 'M64-xref'] }],
    ['4', 'Golden Records', 8, { model: 'fix.mdm.golden.rule', cols: ['model_name', 'field_name', 'strategy', 'sequence', 'active'], screens: ['M64-mdm-golden-rule', 'M64-mdm-match-rule', 'M64-governed'] }],
    ['5', 'Workflows', 7, { model: 'fix.mdm.change.request', cols: ['reference', 'title', 'model_name', 'priority', 'state'], screens: ['M64-mdm-change-request', 'M64-impact'] }],
    ['6', 'Audit', 6, { model: 'fix.mdm.duplicate', cols: ['name', 'res_model', 'decision', 'decided_by_id', 'decided_on'], screens: ['M64-lineage', 'M64-dedupe'] }]
  ] }
};

export const SCREENS = {
  'M64-rpt-dqdomain': { kind: 'table_report', module: 'M64', report: 'dq_by_domain',
    title: 'Data Quality by Domain', period: false },
  'M64-form-goldenrule': {
    kind: 'model_form',
    model: 'fix.mdm.golden.rule',
    title: "Golden Record Rule",
    back: 'M64-mdm-golden-rule',
    sections: [
      { title: "Golden Record Rule", note: "The survivorship strategy per master field: which record wins when duplicates are merged (most recent, most complete, source priority).",
        fields: [
          { name: 'model_name', required: true, label: "Master Model" },
          { name: 'field_name', required: true, label: "Field" },
          { name: 'strategy', required: true, label: "Survivorship Strategy" },
          { name: 'priority_source_ids', label: "Priority Sources (ranked by each source's sequence)" },
          { name: 'sequence', label: "Sequence" },
          { name: 'description', label: "Description" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },

  'M64-form-matchrule': {
    kind: 'model_form',
    model: 'fix.mdm.match.rule',
    title: "Match Rule",
    back: 'M64-mdm-match-rule',
    sections: [
      { title: "Match Rule", note: "Duplicate detection scoring: each field contributes its weight, and the sum decides whether a pair is a candidate.",
        fields: [
          { name: 'model_name', required: true, label: "Master Model" },
          { name: 'field_name', required: true, label: "Field" },
          { name: 'match_type', required: true, label: "Match Type" },
          { name: 'weight', required: true, label: "Weight" },
          { name: 'normalize', label: "Normalise" },
          { name: 'sequence', label: "Sequence" },
          { name: 'description', label: "Description" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },

  'M64-stewardship': { kind: 'model_list', model: 'fix.mdm.steward', stateField: 'state',
    cols: ['name', 'request_type', 'res_model', 'record_ref', 'steward_id', 'created_at', 'state'],
    /* A12 P1-2: approval itself is M63-routed (no Approve button) - the
       steward decides from the approver's inbox; here we review, route,
       recall, reject (needs a decision note) and apply the approved change. */
    actions: [{ m: 'action_review', l: 'Start Review (another steward)' },
              { m: 'action_request_approval', l: 'Route for Approval', ask: 'Justification for the steward decision', kwarg: 'justification' },
              { m: 'action_recall_approval', l: 'Recall Approval' },
              { m: 'action_apply', l: 'Apply Approved Change' }] },
  'M64-domains': { kind: 'table_report', module: 'M64', report: 'golden_coverage', title: 'Master Models (governed)', period: false },
  'M64-rules': { kind: 'model_list', model: 'fix.mdm.dq.rule',
    cols: ['code', 'name', 'res_model', 'field_name', 'rule_type', 'severity', 'last_status', 'last_violation_count', 'active'],
    actions: [{ m: 'action_evaluate', l: 'Run Evaluator' }] },
  'M64-scoring': { kind: 'table_report', module: 'M64', report: 'golden_coverage', title: 'Golden Coverage', period: false },
  'M64-codelists': { kind: 'model_list', model: 'fix.mdm.code.list', stateField: 'state',
    cols: ['code', 'name', 'domain_area', 'version', 'effective_from', 'effective_to', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish List (second steward)' }, { m: 'action_new_version', l: 'New Version' },
              { m: 'action_retire', l: 'Retire List' }] },
  'M64-entries': { kind: 'model_list', model: 'fix.mdm.code.entry',
    cols: ['list_id', 'value', 'label', 'label_bn', 'effective_from', 'effective_to', 'active'] },

  /* Report chips */
  'M64-rpt-backlog': { kind: 'table_report', module: 'M64', report: 'steward_backlog', title: 'Steward Request Backlog', period: false },
  'M64-rpt-dq': { kind: 'table_report', module: 'M64', report: 'dq_rule_register', title: 'DQ Rule Register', period: false },
  'M64-rpt-lists': { kind: 'table_report', module: 'M64', report: 'code_list_usage', title: 'Code List Usage', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M64-form-steward': {
    kind: 'model_form',
    model: 'fix.mdm.steward',
    title: 'Steward Request',
    back: 'M64-stewardship',
    status: { field: 'state', labels: {
      submitted: 'Submitted', in_review: 'In Review', approved: 'Approved', rejected: 'Rejected', applied: 'Applied' } },
    sections: [
      { title: 'Request', note: 'Raised by a steward. Another steward starts the review; the raiser routes it; a steward decides from the M63 inbox, where a rejection carries its note; Apply lands it. Update writes the proposed values, Deactivate archives the record, Merge opens a duplicate pair and routes its M33 merge. A new record is raised in its own module: Create is refused. The state badge is decided by the buttons, never typed.',
        fields: [
          { name: 'request_type', required: true, label: 'Request Type' },
          { name: 'res_model', required: true, label: 'Master Model' },
          { name: 'record_ref', label: 'Record ID (database id)', bn: 'রেকর্ড আইডি' },
          { name: 'merge_with_ref', label: 'Merge Into (record id, merge only)', bn: 'যার সাথে একীভূত হবে' },
          { name: 'steward_id', label: 'Assigned Steward' },
          { name: 'reason', required: true, type: 'text', label: 'Reason' },
          { name: 'proposed_changes', type: 'text', label: 'Proposed Changes (one field=value per line, or a JSON object)', bn: 'প্রস্তাবিত পরিবর্তন (প্রতি লাইনে একটি field=value, অথবা JSON)' }
        ] }
    ]
  },

  'M64-form-dq': {
    kind: 'model_form',
    model: 'fix.mdm.dq.rule',
    title: 'DQ Rule',
    back: 'M64-rules',
    sections: [
      { title: 'Rule', note: 'Code is unique per company. The expression is the checked condition on the named field.',
        fields: [
          { name: 'code', required: true, label: 'Rule Code' },
          { name: 'name', required: true, label: 'Rule Name' },
          { name: 'res_model', required: true, label: 'Master Model' },
          { name: 'field_name', required: true, label: 'Field' },
          { name: 'rule_type', required: true, label: 'Rule Type' },
          { name: 'expression', required: true, label: 'Expression' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M64-form-entry': {
    kind: 'model_form',
    model: 'fix.mdm.code.entry',
    title: 'Code List Entry',
    back: 'M64-entries',
    sections: [
      { title: 'Entry', note: 'A value is unique inside its list (database UNIQUE). The Bengali label carries the bn_BD rendering. A published or retired list cannot change: cut a new version.',
        fields: [
          { name: 'list_id', required: true, label: 'Code List' },
          { name: 'value', required: true, label: 'Value' },
          { name: 'label', required: true, label: 'Label (English)' },
          { name: 'label_bn', label: 'Label (Bengali)' },
          { name: 'effective_from', label: 'Effective From', bn: 'কার্যকর শুরু' },
          { name: 'effective_to', label: 'Effective To', bn: 'কার্যকর শেষ' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M64-form-list': {
    kind: 'model_form',
    model: 'fix.mdm.code.list',
    title: 'Code List',
    back: 'M64-codelists',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    sections: [
      { title: 'Code List', note: 'Draft → published (frozen) by a second steward → new version for changes, same code. Publishing a version retires the one it supersedes. The state badge is set by the buttons, never typed.',
        fields: [
          { name: 'code', required: true, label: 'List Code' },
          { name: 'name', required: true, label: 'List Name' },
          { name: 'domain_area', label: 'Domain' },
          { name: 'version', label: 'Version' },
          { name: 'effective_from', label: 'Effective From', bn: 'কার্যকর শুরু' },
          { name: 'effective_to', readonly: true, label: 'Effective To', bn: 'কার্যকর শেষ' }
        ] }
    ]
  },

  /* registry completion screens */
  'M64-dedupe': { kind: 'model_list', model: 'fix.mdm.duplicate', stateField: 'decision', cols: ['name', 'res_model', 'record_a_ref', 'record_b_ref', 'score', 'match_factors', 'survivor_ref', 'decision'],
    /* A12: Merge no longer writes the master - it routes an M33 fix.party.merge
       (itself M63-approved); the decision lands when that merge executes. */
    actions: [{ m: 'action_merge', l: 'Merge (routes M33)',
                asks: [{ kwarg: 'survivor', label: 'Which record survives? Enter the Record A or Record B reference (blank keeps Record A)' },
                       { kwarg: 'justification', label: 'Why should this pair be merged? (required below the score threshold)' }] },
              { m: 'action_keep_separate', l: 'Keep Separate', ask: 'Why are they kept separate?', kwarg: 'note' },
              { m: 'action_false_positive', l: 'False Positive', ask: 'Why is this not a duplicate?', kwarg: 'note' },
              { m: 'action_sync_merge_state', l: 'Sync Merge State' }] },
  'M64-xref': { kind: 'model_list', model: 'fix.mdm.xref', cols: ['code_list', 'source_system', 'source_value', 'canonical_value', 'confidence'] },
  'M64-impact': { kind: 'table_report', module: 'M64', report: 'impact_analysis', title: 'Impact Analysis', period: false },
  'M64-lineage': { kind: 'table_report', module: 'M64', report: 'lineage_coverage', title: 'Lineage', period: false },


  /* ===== registry completion forms ===== */
  'M64-form-dup': {
    kind: 'model_form',
    model: 'fix.mdm.duplicate',
    title: "Duplicate Candidate",
    back: 'M64-dedupe',
    status: { field: 'decision', labels: { pending: "Pending", merged: "Merged", kept_separate: "Kept Separate", false_positive: "False Positive" } },
    sections: [
      { title: "Duplicate Candidate", note: "A candidate pair from the daily detection run, or raised by a steward. The score is measured by detection and is never typed: a pair below the threshold needs a justification to merge. Merge asks which record survives and routes an M33 golden-party merge (M63-approved); the golden rules decide which values survive; nothing is deleted silently, and the decision badge follows that merge.",
        fields: [
          { name: 'res_model', required: true, label: "Master Model" },
          { name: 'record_a_ref', required: true, label: "Record A" },
          { name: 'record_b_ref', required: true, label: "Record B" },
          { name: 'score', readonly: true, label: "Match Score" },
          { name: 'match_factors', label: "Match Factors" },
          { name: 'decision_note', type: 'text', label: "Decision Note" }
        ] }
    ]
  },
  'M64-form-xref': {
    kind: 'model_form',
    model: 'fix.mdm.xref',
    title: "Cross-Reference",
    back: 'M64-xref',
    sections: [
      { title: "Cross-Reference", note: "Maps a source system's value onto the canonical value. A source value maps once per domain and system (database UNIQUE).",
        fields: [
          { name: 'code_list', required: true, label: "Domain" },
          { name: 'source_system', required: true, label: "Source System" },
          { name: 'source_value', required: true, label: "Source Value" },
          { name: 'canonical_value', required: true, label: "Canonical Value" },
          { name: 'canonical_label', label: "Canonical Label" },
          { name: 'confidence', required: true, label: "Confidence" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M64-mdm-golden-rule': { kind: 'model_list', model: 'fix.mdm.golden.rule',
    cols: ['active', 'sequence', 'model_name', 'field_name', 'strategy'] },
  'M64-mdm-stewardship': { kind: 'model_list', model: 'fix.mdm.stewardship',
    cols: ['name', 'company_id', 'operating_unit_id', 'domain', 'lead_steward_id', 'owner_id', 'overall_quality_score', 'audit_state', 'last_audit_date'],
    actions: [{ m: 'action_audit_data_quality', l: 'Audit Data Quality' }] },
  'M64-mdm-change-request': { kind: 'model_list', model: 'fix.mdm.change.request', stateField: 'state',
    cols: ['reference', 'title', 'state', 'company_id', 'operating_unit_id', 'model_name', 'record_id', 'priority'],
    /* A12 P1-2: approval is M63-routed - Submit validates + freezes the
       payload, Route sends it to the steward inbox, Apply lands it. */
    actions: [{ m: 'action_submit', l: 'Submit' },
              { m: 'action_request_approval', l: 'Route to Steward', ask: 'Why is this master-data change needed?', kwarg: 'justification' },
              { m: 'action_recall_approval', l: 'Recall' },
              { m: 'action_reject', l: 'Reject', ask: 'Why is this change rejected?', kwarg: 'comment' },
              { m: 'action_cancel', l: 'Cancel Request' },
              { m: 'action_apply', l: 'Apply Approved Change' }] },
  'M64-mdm-match-rule': { kind: 'model_list', model: 'fix.mdm.match.rule',
    cols: ['active', 'sequence', 'model_name', 'field_name', 'match_type', 'weight', 'normalize'] },
  'M64-governed': { kind: 'model_list', model: 'fix.mdm.governed.attribute',
    cols: ['model_name', 'field_name', 'category', 'block_direct_edit', 'note', 'active'] },

  'M64-form-governed': {
    kind: 'model_form',
    model: 'fix.mdm.governed.attribute',
    title: 'Governed Attribute',
    title_bn: 'নিয়ন্ত্রিত বৈশিষ্ট্য',
    back: 'M64-governed',
    sections: [
      { title: 'Governed Attribute', note: 'What a change request may write. Anything off this register is refused, and so are access control, technical configuration and workflow fields. Block Direct Edits refuses a change of a stored value outside a change request, while the parameter fix.mdm.enforce_direct_edit_block is on. A Platform Admin maintains this register.',
        fields: [
          { name: 'model_name', required: true, label: 'Master Model', bn: 'মাস্টার মডেল' },
          { name: 'field_name', required: true, label: 'Attribute', bn: 'বৈশিষ্ট্য' },
          { name: 'category', required: true, label: 'Category', bn: 'শ্রেণি' },
          { name: 'block_direct_edit', label: 'Block Direct Edits', bn: 'সরাসরি সম্পাদনা বন্ধ' },
          { name: 'note', label: 'Note', bn: 'নোট' },
          { name: 'active', label: 'Active', bn: 'সক্রিয়' }
        ] }
    ]
  },

  'M64-form-mdm-stewardship': {
    kind: 'model_form',
    model: 'fix.mdm.stewardship',
    title: "Mdm Stewardship",
    back: 'M64-mdm-stewardship',
    sections: [
      { title: "Mdm Stewardship", note: "The measured quality scores and audit stamps are computed daily, and by the Audit Data Quality action, and blend the DQ rules' measured results - they are never typed here. A Platform Admin appoints the lead steward, who must hold the steward role, and the business owner.",
        fields: [
          { name: 'name', required: true, label: "Stewardship Domain Title" },
          { name: 'domain', required: true, label: "Data Domain" },
          { name: 'lead_steward_id', required: true, label: "Lead Data Steward" },
          { name: 'owner_id', label: "Business Owner", bn: 'ব্যবসায়িক মালিক' },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ] }
    ]
  },
  'M64-form-mdm-change-request': {
    kind: 'model_form',
    model: 'fix.mdm.change.request',
    title: "Mdm Change Request",
    back: 'M64-mdm-change-request',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', under_review: 'Under Review', approved: 'Approved',
      rejected: 'Rejected', implemented: 'Applied', cancelled: 'Cancelled' } },
    sections: [
      { title: "Mdm Change Request", note: "Proposed values are held on the request - never written to the master until a steward approves and Apply runs. Only attributes on the Governed Attributes register can change. Submit tests the values, measures the impact and freezes the request. The state badge is decided by Submit/Route/Apply, never typed.",
        fields: [
          { name: 'title', required: true, label: "Title" },
          { name: 'description', type: 'text', label: "Description" },
          { name: 'model_name', required: true, label: "Target Model" },
          { name: 'record_id', required: true, label: "Target Record ID" },
          { name: 'proposed_changes', type: 'text', label: "Proposed Changes (one field=value per line, or a JSON object; frozen at submit)", bn: 'প্রস্তাবিত পরিবর্তন (প্রতি লাইনে একটি field=value, অথবা JSON)' },
          { name: 'priority', required: true, label: "Priority" },
          { name: 'impact_summary', type: 'text', readonly: true, label: "Impact (measured at submit)", bn: 'প্রভাব (জমা দেওয়ার সময় পরিমাপ)' },
          { name: 'current_values', type: 'text', readonly: true, label: "Current Values (at submit)", bn: 'বর্তমান মান (জমা দেওয়ার সময়)' },
          { name: 'review_notes', type: 'text', label: "Review Notes (the deciding steward's)", bn: 'পর্যালোচনার নোট' },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M64:Data Quality by Domain': 'M64-rpt-dqdomain',
  'M64:Stewardship SLA': 'M64-stewardship',
  'M64:Merge/Unmerge Audit': 'M64-dedupe',
  'M64:Code List Versions': 'M64-codelists',
  'M64:Steward Request Backlog': 'M64-rpt-backlog',
  'M64:DQ Rule Register': 'M64-rpt-dq',
  'M64:Code List Usage': 'M64-rpt-lists',
  'M64:Golden Record Coverage': 'M64-scoring'
};

export const FORM_MODELS = {
  'M64:Change Request': 'fix.mdm.change.request',
  'M64:Steward Request': 'fix.mdm.steward',
  'M64:DQ Rule': 'fix.mdm.dq.rule',
  'M64:Code List Entry': 'fix.mdm.code.entry'
};

export const FORM_CHIPS = {
  'M64:Change Request': 'M64-form-mdm-change-request',
  'M64:Steward Request': 'M64-form-steward',
  'M64:DQ Rule': 'M64-form-dq',
  'M64:Code List Entry': 'M64-form-entry',
  'M64:__by_model__': {
    'fix.mdm.governed.attribute': 'M64-form-governed',
    'fix.mdm.match.rule': 'M64-form-matchrule',
    'fix.mdm.golden.rule': 'M64-form-goldenrule',
    'fix.mdm.stewardship': 'M64-form-mdm-stewardship',
    'fix.mdm.change.request': 'M64-form-mdm-change-request',
    'fix.mdm.duplicate': 'M64-form-dup',
    'fix.mdm.xref': 'M64-form-xref',
    'fix.mdm.steward': 'M64-form-steward',
    'fix.mdm.dq.rule': 'M64-form-dq',
    'fix.mdm.code.entry': 'M64-form-entry',
    'fix.mdm.code.list': 'M64-form-list'
  },
  'M64:__by_screen__': {
    'M64-governed': 'M64-form-governed',
    'M64-mdm-match-rule': 'M64-form-matchrule',
    'M64-mdm-golden-rule': 'M64-form-goldenrule',
    'M64-mdm-stewardship': 'M64-form-mdm-stewardship',
    'M64-mdm-change-request': 'M64-form-mdm-change-request',
    'M64-dedupe': 'M64-form-dup',
    'M64-xref': 'M64-form-xref',
    'M64-stewardship': 'M64-form-steward',
    'M64-rules': 'M64-form-dq',
    'M64-entries': 'M64-form-entry',
    'M64-codelists': 'M64-form-list'
  }
};

export const CREATE = {
  /* E13: a change request is what anyone may raise; a steward request is a steward's. */
  M64: { screen: 'M64-form-mdm-change-request', model: 'fix.mdm.change.request', label: 'Change Request' }
};
