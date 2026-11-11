/** @odoo-module **/
/* A11 · Insights & Intelligence — M62 Data Platform & Governance.
 * Registry-faithful: 4 groups / 11 screens / 4 reports / 3 forms / freg 62.
 * Scope note: freshness and cost are measured from the recorded runs and the
 * declared volumes; nothing here is a cloud-billing estimate. */

export const MODULE = {
  area: 'A11', code: 'M62', en: 'Data Platform & Governance', title: 'M62 · Data Platform & Governance',
  bn: 'ডেটা প্ল্যাটফর্ম', icon: '🗄️',
  desc: 'Ingestion pipelines with CDC and freshness SLOs, the medallion progression and backfill history, dimensional entities with documented lineage, data contracts, the metric registry, quality tests and incidents, and retention cost per domain.',
  kpis: [
    { l: 'Pipelines Active', m: 'pipelines_active' },
    { l: 'Runs (24h)', m: 'runs_24h' },
    { l: 'Runs Failed', m: 'runs_failed' },
    { l: 'Quality Failures', m: 'quality_failures' },
    { l: 'Incidents Open', m: 'incidents_open' },
    { l: 'Metrics Published', m: 'metrics_published' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M62-data-lineage', en: "Data Lineage", bn: "Data Lineage", t: 'g' }
    ]},
    { en: 'Pipelines', screens: [
      { id: 'M62-ingestion', en: 'Ingestion & CDC', bn: 'ইনজেশন', t: 'g' },
      { id: 'M62-medallion', en: 'Medallion Progression', bn: 'মেডেলিয়ন', t: 'g' },
      { id: 'M62-backfill', en: 'Replay & Backfill', bn: 'ব্যাকফিল', t: 'g' }
    ]},
    { en: 'Modelling', screens: [
      { id: 'M62-dimensional', en: 'Dimensional Model', bn: 'ডাইমেনশনাল', t: 'g' },
      { id: 'M62-contracts', en: 'Data Contracts', bn: 'ডেটা কন্ট্রাক্ট', t: 'g' }
    ]},
    { en: 'Governance', screens: [
      { id: 'M62-metrics', en: 'Metric Registry', bn: 'মেট্রিক', t: 'g' },
      { id: 'M62-catalog', en: 'Catalogue & Glossary', bn: 'ক্যাটালগ', t: 'g' },
      { id: 'M62-quality', en: 'Quality Tests & Incidents', bn: 'কোয়ালিটি', t: 'g' },
      { id: 'M62-observability', en: 'Observability', bn: 'পর্যবেক্ষণ', t: 'r' },
      { id: 'M62-incidents', en: 'Data Incidents', bn: 'ডেটা ঘটনা', t: 'g' },
      { id: 'M62-rules', en: 'Quality Rules', bn: 'কোয়ালিটি নিয়ম', t: 'g' }
    ]},
    { en: 'Security', screens: [
      { id: 'M62-masking', en: 'Masking & Access', bn: 'মাস্কিং', t: 'g' },
      { id: 'M62-retention', en: 'Retention & Cost', bn: 'রিটেনশন', t: 'g' }
    ]}
  ],
  reports: ['Data Quality Scorecard', 'Freshness SLA', 'Lineage Coverage', 'Cost per Domain'],
  forms: ['Data Contract', 'Metric Definition', 'Quality Test'],
  cross: ['M25 BI', 'M26 ML', 'M29 classification', 'M60 controls'],
  freg: { src: 62, sub: [
    ['1', 'Ingestion', 10, { model: 'fix.data.pipeline', cols: ['code', 'name', 'source_system', 'load_mode', 'schedule', 'state'], screens: ['M62-ingestion', 'M62-backfill'] }],
    ['2', 'Medallion & Transformation', 9, { model: 'fix.data.run', cols: ['name', 'pipeline_id', 'stage', 'started_at', 'rows_written', 'state'], screens: ['M62-medallion', 'M62-backfill'] }],
    ['3', 'Dimensional Model', 10, { model: 'fix.data.entity', cols: ['name', 'entity_type', 'owner_module', 'steward_id', 'classification'], screens: ['M62-dimensional'] }],
    ['4', 'Semantic Layer', 9, { model: 'fix.metric.definition', cols: ['code', 'name', 'domain_area', 'grain', 'owner_role', 'state'], screens: ['M62-metrics', 'M62-contracts'] }],
    ['5', 'Quality & Observability', 10, { model: 'fix.data.quality.rule', cols: ['name', 'entity_id', 'rule_type', 'threshold', 'last_result', 'state'], screens: ['M62-rules', 'M62-quality', 'M62-observability', 'M62-incidents'] }],
    ['6', 'Catalogue & Lineage', 8, { model: 'fix.data.lineage', cols: ['name', 'source_entity_id', 'target_entity_id', 'lineage_order'], screens: ['M62-data-lineage', 'M62-catalog'] }],
    ['7', 'Security & Cost', 6, { model: 'fix.sensitive.field', cols: ['model_name', 'field_name', 'sensitivity', 'data_class', 'masking_rule'], screens: ['M62-masking', 'M62-retention'] }]
  ] }
};

export const SCREENS = {
  /* ---- Pipelines ---- */
  'M62-ingestion': { kind: 'model_list', model: 'fix.data.pipeline', stateField: 'state',
    cols: ['code', 'name', 'source_system', 'target_entity_id', 'load_mode', 'schedule', 'freshness_sla_minutes', 'state'],
    actions: [{ m: 'action_pause', l: 'Pause' }, { m: 'action_resume', l: 'Resume' }] },
  'M62-medallion': { kind: 'model_list', model: 'fix.data.run', stateField: 'state',
    cols: ['name', 'pipeline_id', 'stage', 'started_at', 'duration_minutes', 'rows_read', 'rows_written', 'state'],
    actions: [{ m: 'action_finish', l: 'Finish' }, { m: 'action_fail', l: 'Mark Failed' }] },
  'M62-backfill': { kind: 'model_list', model: 'fix.data.run', stateField: 'state',
    cols: ['name', 'pipeline_id', 'kind', 'stage', 'started_at', 'rows_written', 'state'],
    actions: [{ m: 'action_finish', l: 'Finish' }, { m: 'action_fail', l: 'Mark Failed' }] },

  /* ---- Modelling ---- */
  'M62-dimensional': { kind: 'model_list', model: 'fix.data.entity',
    cols: ['name', 'entity_type', 'owner_module', 'steward_id', 'classification', 'retention_policy'] },
  'M62-contracts': { kind: 'model_list', model: 'fix.data.contract', stateField: 'state',
    // No "Activate" button (A11 audit G1): the backend removed action_activate
    // from this surface on purpose — a contract activates only from an
    // approved M63 task (producer sign -> request approval -> decision).
    cols: ['dataset_code', 'name', 'entity_id', 'producer', 'schema_version', 'freshness_sla_minutes', 'state'] },

  /* ---- Governance ---- */
  'M62-metrics': { kind: 'model_list', model: 'fix.metric.definition', stateField: 'state',
    // No "Publish" button (A11 audit G2): a metric publishes through its
    // VERSION (steward review, then an approved M63 request) — the
    // definition has no one-click publish and the surface refuses it.
    cols: ['code', 'name', 'domain_area', 'grain', 'owner_role', 'state'] },
  'M62-catalog': { kind: 'table_report', module: 'M62', report: 'lineage_coverage', title: 'Catalogue & Glossary (lineage)', period: false },
  'M62-quality': { kind: 'model_list', model: 'fix.data.quality.test',
    cols: ['name', 'rule_id', 'checked_at', 'observed_value', 'threshold', 'passed'] },
  'M62-observability': { kind: 'table_report', module: 'M62', report: 'freshness_sla', title: 'Observability — freshness SLA', period: false },

  /* ---- Security ---- */
  // The classification lives in M29; this screen shows which sensitive fields exist.
  'M62-masking': { kind: 'model_list', model: 'fix.sensitive.field', create: false,
    cols: ['model_name', 'field_name', 'sensitivity', 'data_class', 'masking_rule'] },
  'M62-retention': { kind: 'model_list', model: 'fix.data.retention.policy',
    cols: ['entity_id', 'tier', 'retention_months', 'volume_gb', 'storage_cost_per_gb', 'monthly_cost', 'purge_rule'] },

  /* ---- extra operational surfaces (incidents + runs + rules) ---- */
  'M62-incidents': { kind: 'model_list', model: 'fix.data.incident', stateField: 'state',
    cols: ['name', 'title', 'entity_id', 'severity', 'detected_at', 'state'],
    actions: [{ m: 'action_fix', l: 'Mark Fixed' }, { m: 'action_close', l: 'Close' }] },
  'M62-rules': { kind: 'model_list', model: 'fix.data.quality.rule',
    cols: ['name', 'entity_id', 'rule_type', 'threshold', 'active', 'last_result', 'state'] },

  /* ---- report screens (own pack each) ---- */
  'M62-rpt-quality': { kind: 'table_report', module: 'M62', report: 'quality_scorecard', title: 'Data Quality Scorecard', period: false },
  'M62-rpt-freshness': { kind: 'table_report', module: 'M62', report: 'freshness_sla', title: 'Freshness SLA', period: false },
  'M62-rpt-lineage': { kind: 'table_report', module: 'M62', report: 'lineage_coverage', title: 'Lineage Coverage', period: false },
  'M62-rpt-cost': { kind: 'table_report', module: 'M62', report: 'cost_per_domain', title: 'Cost per Domain', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M62-form-contract': {
    kind: 'model_form',
    model: 'fix.data.contract',
    title: 'Data Contract',
    back: 'M62-contracts',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', deprecated: 'Deprecated' } },
    sections: [
      { title: 'Contract', note: 'A contract states what the producer guarantees — schema version, freshness and completeness — so consumers can rely on the dataset instead of inspecting it.',
        fields: [
          { name: 'dataset_code', required: true, label: 'Dataset Code' },
          { name: 'name', required: true, label: 'Dataset Name' },
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'producer', required: true, label: 'Producer' },
          { name: 'consumers', label: 'Consumers' },
          { name: 'schema_version', required: true, label: 'Schema Version' },
          { name: 'freshness_sla_minutes', label: 'Freshness SLO (minutes)' },
          { name: 'breaking_change_notice_days', label: 'Breaking-Change Notice (days)' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Guarantees', fields: [
          { name: 'guarantees', type: 'text', label: 'Guarantees' }
        ] }
    ]
  },

  'M62-form-metric': {
    kind: 'model_form',
    model: 'fix.metric.definition',
    title: 'Metric Definition',
    back: 'M62-metrics',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    sections: [
      { title: 'Metric', note: 'One definition per metric code. The formula must state numerator and denominator, so two dashboards cannot disagree about the same number.',
        fields: [
          { name: 'code', required: true, label: 'Metric Code' },
          { name: 'name', required: true, label: 'Metric Name' },
          { name: 'domain_area', required: true, label: 'Domain' },
          { name: 'grain', required: true, label: 'Grain' },
          { name: 'source_entity_id', label: 'Source Entity' },
          { name: 'owner_role', label: 'Owner Role' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Definition', fields: [
          { name: 'definition', required: true, type: 'text', label: 'Definition' }
        ] }
    ]
  },

  'M62-form-quality': {
    kind: 'model_form',
    model: 'fix.data.quality.test',
    title: 'Quality Test',
    back: 'M62-quality',
    sections: [
      { title: 'Test Run', note: 'Records what was measured against the rule threshold. Pass/fail is computed from the observed value — it is never typed, and the threshold is the rule\'s own, stamped at run time.',
        fields: [
          { name: 'rule_id', required: true, label: 'Quality Rule' },
          { name: 'checked_at', label: 'Checked At' },
          { name: 'observed_value', label: 'Observed Value' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },

  'M62-form-pipeline': {
    kind: 'model_form',
    model: 'fix.data.pipeline',
    title: 'Data Pipeline',
    back: 'M62-ingestion',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused', retired: 'Retired' } },
    sections: [
      { title: 'Pipeline', note: 'Source, target entity, load mode and the freshness SLO. The SLO is what the Freshness SLA report breaches against.',
        fields: [
          { name: 'code', required: true, label: 'Pipeline Code' },
          { name: 'name', required: true, label: 'Pipeline Name' },
          { name: 'source_system', required: true, label: 'Source System' },
          { name: 'target_entity_id', required: true, label: 'Target Entity' },
          { name: 'load_mode', required: true, label: 'Load Mode' },
          { name: 'schedule', required: true, label: 'Schedule' },
          { name: 'freshness_sla_minutes', label: 'Freshness SLO (minutes)' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M62-form-run': {
    kind: 'model_form',
    model: 'fix.data.run',
    title: 'Pipeline Run',
    back: 'M62-medallion',
    status: { field: 'state', labels: { running: 'Running', succeeded: 'Succeeded', failed: 'Failed' } },
    sections: [
      { title: 'Run', note: 'A scheduled, backfill or replay load landing in one medallion stage. Finishing measures the duration from the start timestamp.',
        fields: [
          { name: 'pipeline_id', required: true, label: 'Pipeline' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'stage', required: true, label: 'Medallion Stage' },
          { name: 'started_at', label: 'Started At' },
          { name: 'rows_read', label: 'Rows Read' },
          { name: 'rows_written', label: 'Rows Written' },
          { name: 'rows_rejected', label: 'Rows Rejected' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M62-form-incident': {
    kind: 'model_form',
    model: 'fix.data.incident',
    title: 'Data Quality Incident',
    back: 'M62-incidents',
    status: { field: 'state', labels: { open: 'Open', fixed: 'Fixed', closed: 'Closed' } },
    sections: [
      { title: 'Incident', note: 'Open → fixed → closed. Seeded from a failing quality test or reported by a consumer. Fix and Close demand an owner, a root cause and a resolution.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'rule_id', label: 'Quality Rule' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'owner_id', label: 'Owner' },
          { name: 'detected_at', label: 'Detected At' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Narrative', fields: [
          { name: 'description', type: 'text', label: 'What happened' },
          { name: 'root_cause', type: 'text', label: 'Root cause' },
          { name: 'resolution', type: 'text', label: 'Resolution' }
        ] }
    ]
  },

  'M62-form-retention': {
    kind: 'model_form',
    model: 'fix.data.retention.policy',
    title: 'Retention Policy',
    back: 'M62-retention',
    sections: [
      { title: 'Retention & Cost', note: 'Monthly cost is computed from the current volume and the storage rate — a measured projection, not a cloud bill.',
        fields: [
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'tier', required: true, label: 'Tier' },
          { name: 'retention_months', required: true, label: 'Retention (months)' },
          { name: 'volume_gb', label: 'Volume (GB)' },
          { name: 'storage_cost_per_gb', label: 'Storage Cost / GB (BDT)' },
          { name: 'purge_rule', label: 'Purge Rule' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* ===== registry completion forms ===== */
  'M62-form-entity': {
    kind: 'model_form',
    model: 'fix.data.entity',
    title: "Data Entity",
    back: 'M62-dimensional',
    sections: [
      { title: "Data Entity", note: "A dimensional entity: what it is, which module owns it and how sensitive it is. The classification decides its residency tier.",
        fields: [
          { name: 'name', required: true, label: "Entity Name" },
          { name: 'entity_type', label: "Entity Type" },
          { name: 'owner_module', label: "Owning Module" },
          { name: 'steward_id', label: "Data Steward" },
          { name: 'classification', label: "Classification" },
          { name: 'retention_policy', label: "Retention Policy" }
        ] }
    ]
  },
  'M62-form-qrule': {
    kind: 'model_form',
    model: 'fix.data.quality.rule',
    title: "Quality Rule",
    back: 'M62-rules',
    sections: [
      { title: "Quality Rule", note: "A rule states what is measured on an entity and the threshold it must not exceed. Tests are run against it; the rule itself never asserts a result.",
        fields: [
          { name: 'name', required: true, label: "Rule Name" },
          { name: 'entity_id', required: true, label: "Entity" },
          { name: 'rule_type', label: "Rule Type" },
          { name: 'threshold', label: "Threshold" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M62-data-lineage': { kind: 'model_list', model: 'fix.data.lineage',
    cols: ['name', 'company_id', 'operating_unit_id', 'source_entity_id', 'target_entity_id', 'lineage_order'] },

  'M62-form-data-lineage': {
    kind: 'model_form',
    model: 'fix.data.lineage',
    title: "Data Lineage",
    back: 'M62-data-lineage',
    sections: [
      { title: "Data Lineage", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'source_entity_id', required: true, label: "Source" },
          { name: 'target_entity_id', required: true, label: "Target" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'lineage_order', label: "Order" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M62:Data Quality Scorecard': 'M62-rpt-quality',
  'M62:Freshness SLA': 'M62-rpt-freshness',
  'M62:Lineage Coverage': 'M62-rpt-lineage',
  'M62:Cost per Domain': 'M62-rpt-cost'
};

export const FORM_MODELS = {
  'M62:Data Contract': 'fix.data.contract',
  'M62:Metric Definition': 'fix.metric.definition',
  'M62:Quality Test': 'fix.data.quality.test'
};

export const FORM_CHIPS = {
  'M62:Data Contract': 'M62-form-contract',
  'M62:Metric Definition': 'M62-form-metric',
  'M62:Quality Test': 'M62-form-quality',
  'M62:Data Pipeline': 'M62-form-pipeline',
  'M62:Pipeline Run': 'M62-form-run',
  'M62:Data Incident': 'M62-form-incident',
  'M62:Retention Policy': 'M62-form-retention',
  'M62:__by_model__': {
    'fix.data.lineage': 'M62-form-data-lineage',
    'fix.data.entity': 'M62-form-entity',
    'fix.data.quality.rule': 'M62-form-qrule',
    'fix.data.pipeline': 'M62-form-pipeline',
    'fix.data.run': 'M62-form-run',
    'fix.data.contract': 'M62-form-contract',
    'fix.metric.definition': 'M62-form-metric',
    'fix.data.quality.test': 'M62-form-quality',
    'fix.data.incident': 'M62-form-incident',
    'fix.data.retention.policy': 'M62-form-retention'
  },
  'M62:__by_screen__': {
    'M62-data-lineage': 'M62-form-data-lineage',
    'M62-dimensional': 'M62-form-entity',
    'M62-rules': 'M62-form-qrule',
    'M62-ingestion': 'M62-form-pipeline',
    'M62-medallion': 'M62-form-run',
    'M62-backfill': 'M62-form-run',
    'M62-contracts': 'M62-form-contract',
    'M62-metrics': 'M62-form-metric',
    'M62-quality': 'M62-form-quality',
    'M62-incidents': 'M62-form-incident',
    'M62-retention': 'M62-form-retention'
  }
};

export const CREATE = {
  M62: { screen: 'M62-form-contract', model: 'fix.data.contract', label: 'Data Contract' }
};
