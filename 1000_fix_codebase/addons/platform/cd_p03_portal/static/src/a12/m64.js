/** @odoo-module **/
/* A12 · M64 Master Data Management. 3 groups / 6 screens / 4 reports / 3 forms / freg 52. */

export const MODULE = {
  area: 'A12', code: 'M64', en: 'Master Data Management', title: 'M64 · Master Data Management',
  bn: 'মাস্টার ডেটা', icon: '🗂️',
  desc: 'Steward-governed master data: steward requests with review and approval, data-quality rules per master field, governed code lists with bilingual entries, and golden-record coverage.',
  kpis: [
    { l: 'Steward Open', m: 'steward_open' },
    { l: 'Steward Total', m: 'steward_total' },
    { l: 'Active DQ Rules', m: 'dq_rules' },
    { l: 'Published Lists', m: 'code_lists' },
    { l: 'Code Entries', m: 'code_entries' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M64-mdm-golden-rule', en: "Mdm Golden Rule", bn: "Mdm Golden Rule", t: 'g' },
      { id: 'M64-mdm-stewardship', en: "Mdm Stewardship", bn: "Mdm Stewardship", t: 'g' },
      { id: 'M64-mdm-change-request', en: "Mdm Change Request", bn: "Mdm Change Request", t: 'g' },
      { id: 'M64-mdm-match-rule', en: "Mdm Match Rule", bn: "Mdm Match Rule", t: 'g' }
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
  forms: ['Steward Request', 'DQ Rule', 'Code List Entry'],
  cross: ['M30 branch master', 'M33 golden party', 'M25 DQ dashboards'],
  freg: { src: 52, sub: [
    ['1', 'Stewardship', 10], ['2', 'Data Quality', 12], ['3', 'Code Lists', 9],
    ['4', 'Golden Records', 8], ['5', 'Workflows', 7], ['6', 'Audit', 6]
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
    actions: [{ m: 'action_review', l: 'Start Review' }, { m: 'action_approve', l: 'Approve' },
              { m: 'action_reject', l: 'Reject' }] },
  'M64-domains': { kind: 'table_report', module: 'M64', report: 'golden_coverage', title: 'Master Models (governed)', period: false },
  'M64-rules': { kind: 'model_list', model: 'fix.mdm.dq.rule',
    cols: ['code', 'name', 'res_model', 'field_name', 'rule_type', 'severity', 'active'] },
  'M64-scoring': { kind: 'table_report', module: 'M64', report: 'golden_coverage', title: 'Golden Coverage', period: false },
  'M64-codelists': { kind: 'model_list', model: 'fix.mdm.code.list', stateField: 'state',
    cols: ['code', 'name', 'domain_area', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish List' }] },
  'M64-entries': { kind: 'model_list', model: 'fix.mdm.code.entry',
    cols: ['list_id', 'value', 'label', 'label_bn', 'active'] },

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
      submitted: 'Submitted', in_review: 'In Review', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Request', note: 'Submitted → in review → approved/rejected. A steward is assigned for the review.',
        fields: [
          { name: 'request_type', required: true, label: 'Request Type' },
          { name: 'res_model', required: true, label: 'Master Model' },
          { name: 'record_ref', label: 'Record Reference' },
          { name: 'requested_by_id', label: 'Requested By' },
          { name: 'steward_id', label: 'Assigned Steward' },
          { name: 'reason', required: true, type: 'text', label: 'Reason' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Entry', note: 'A value is unique inside its list (database UNIQUE). The Bengali label carries the bn_BD rendering.',
        fields: [
          { name: 'list_id', required: true, label: 'Code List' },
          { name: 'value', required: true, label: 'Value' },
          { name: 'label', required: true, label: 'Label (English)' },
          { name: 'label_bn', label: 'Label (Bengali)' },
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
      { title: 'Code List', note: 'Draft → published; entries are added on the entries screen.',
        fields: [
          { name: 'code', required: true, label: 'List Code' },
          { name: 'name', required: true, label: 'List Name' },
          { name: 'domain_area', label: 'Domain' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  /* registry completion screens */
  'M64-dedupe': { kind: 'model_list', model: 'fix.mdm.duplicate', stateField: 'decision', cols: ['name', 'res_model', 'record_a_ref', 'record_b_ref', 'score', 'decision'], actions: [{ m: 'action_merge', l: 'Merge' }, { m: 'action_keep_separate', l: 'Keep Separate' }] },
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
      { title: "Duplicate Candidate", note: "A candidate pair from the detection run with its match score and factors. Merging records the survivor; nothing is deleted silently.",
        fields: [
          { name: 'res_model', required: true, label: "Master Model" },
          { name: 'record_a_ref', required: true, label: "Record A" },
          { name: 'record_b_ref', required: true, label: "Record B" },
          { name: 'score', label: "Match Score" },
          { name: 'match_factors', label: "Match Factors" },
          { name: 'decision', required: true, label: "Decision" }
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
    cols: ['name', 'company_id', 'operating_unit_id', 'domain', 'lead_steward_id'] },
  'M64-mdm-change-request': { kind: 'model_list', model: 'fix.mdm.change.request', stateField: 'state',
    cols: ['title', 'state', 'company_id', 'operating_unit_id', 'model_name', 'record_id', 'priority'] },
  'M64-mdm-match-rule': { kind: 'model_list', model: 'fix.mdm.match.rule',
    cols: ['active', 'sequence', 'model_name', 'field_name', 'match_type', 'weight', 'normalize'] },

  'M64-form-mdm-stewardship': {
    kind: 'model_form',
    model: 'fix.mdm.stewardship',
    title: "Mdm Stewardship",
    back: 'M64-mdm-stewardship',
    sections: [
      { title: "Mdm Stewardship", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Stewardship Domain Title" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'domain', required: true, label: "Data Domain" },
          { name: 'lead_steward_id', required: true, label: "Lead Data Steward" },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ] }
    ]
  },
  'M64-form-mdm-change-request': {
    kind: 'model_form',
    model: 'fix.mdm.change.request',
    title: "Mdm Change Request",
    back: 'M64-mdm-change-request',
    status: { field: 'state' },
    sections: [
      { title: "Mdm Change Request", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'title', required: true, label: "Title" },
          { name: 'state', required: true, label: "State" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'model_name', required: true, label: "Target Model" },
          { name: 'record_id', required: true, label: "Target Record ID" },
          { name: 'priority', required: true, label: "Priority" },
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
  'M64:Steward Request': 'fix.mdm.steward',
  'M64:DQ Rule': 'fix.mdm.dq.rule',
  'M64:Code List Entry': 'fix.mdm.code.entry'
};

export const FORM_CHIPS = {
  'M64:Steward Request': 'M64-form-steward',
  'M64:DQ Rule': 'M64-form-dq',
  'M64:Code List Entry': 'M64-form-entry',
  'M64:__by_model__': {
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
  M64: { screen: 'M64-form-steward', model: 'fix.mdm.steward', label: 'Steward Request' }
};
