/** @odoo-module **/
/* A11 · Insights & Intelligence — M62 Data Platform & Governance.
 * Registry-faithful: 4 groups / 11 screens / 4 reports / 3 forms / freg 62.
 * Scope note: freshness and cost are measured from the recorded runs and the
 * declared volumes; nothing here is a cloud-billing estimate.
 *
 * Capture audit 2026-11-18: every sub-module page now captures each record
 * it covers. Before, page 7 (Security & Cost) offered no "+ New" and no
 * chip; metric versions (the only path to publication), the consumer
 * register and declassification authorisations were on no screen and no
 * form; pages 1, 2, 3 and 6 had no chip; and the data source, conformed
 * dimension, glossary term and analytical erasure registers did not exist. */

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
      { id: 'M62-sources', en: 'Data Sources', bn: 'ডেটা উৎস', t: 'g' },
      { id: 'M62-ingestion', en: 'Ingestion & CDC', bn: 'ইনজেশন', t: 'g' },
      { id: 'M62-medallion', en: 'Medallion Progression', bn: 'মেডেলিয়ন', t: 'g' },
      { id: 'M62-backfill', en: 'Replay & Backfill', bn: 'ব্যাকফিল', t: 'g' }
    ]},
    { en: 'Modelling', screens: [
      { id: 'M62-dimensional', en: 'Dimensional Model', bn: 'ডাইমেনশনাল', t: 'g' },
      { id: 'M62-dimensions', en: 'Conformed Dimensions', bn: 'কনফর্মড ডাইমেনশন', t: 'g' },
      { id: 'M62-contracts', en: 'Data Contracts', bn: 'ডেটা কন্ট্রাক্ট', t: 'g' }
    ]},
    { en: 'Governance', screens: [
      { id: 'M62-metrics', en: 'Metric Registry', bn: 'মেট্রিক', t: 'g' },
      { id: 'M62-metric-versions', en: 'Metric Versions', bn: 'মেট্রিক সংস্করণ', t: 'g' },
      { id: 'M62-metric-consumers', en: 'Metric Consumers', bn: 'মেট্রিক ব্যবহারকারী', t: 'g' },
      { id: 'M62-catalog', en: 'Catalogue & Glossary', bn: 'ক্যাটালগ', t: 'r' },
      { id: 'M62-glossary', en: 'Business Glossary', bn: 'ব্যবসায়িক শব্দকোষ', t: 'g' },
      { id: 'M62-quality', en: 'Quality Tests & Incidents', bn: 'কোয়ালিটি', t: 'g' },
      { id: 'M62-observability', en: 'Observability', bn: 'পর্যবেক্ষণ', t: 'r' },
      { id: 'M62-incidents', en: 'Data Incidents', bn: 'ডেটা ঘটনা', t: 'g' },
      { id: 'M62-rules', en: 'Quality Rules', bn: 'কোয়ালিটি নিয়ম', t: 'g' }
    ]},
    { en: 'Security', screens: [
      { id: 'M62-masking', en: 'Masking & Access', bn: 'মাস্কিং', t: 'g' },
      { id: 'M62-declass', en: 'Declassification Authorisations', bn: 'শ্রেণি হ্রাস অনুমোদন', t: 'g' },
      { id: 'M62-erasure', en: 'Analytical Erasure', bn: 'বিশ্লেষণী মুছে ফেলা', t: 'g' },
      { id: 'M62-retention', en: 'Retention & Cost', bn: 'রিটেনশন', t: 'g' },
      { id: 'M62-disposition', en: 'Disposition Evidence', bn: 'নিষ্পত্তির প্রমাণ', t: 'g' }
    ]}
  ],
  reports: ['Data Quality Scorecard', 'Freshness SLA', 'Lineage Coverage', 'Cost per Domain'],
  forms: ['Data Contract', 'Metric Definition', 'Quality Test', 'Data Source', 'Data Pipeline', 'Pipeline Run',
    'Data Entity', 'Conformed Dimension', 'Metric Version', 'Metric Consumer', 'Glossary Term', 'Quality Rule',
    'Data Incident', 'Data Lineage', 'Retention Policy', 'Declassification Authorisation', 'Analytical Erasure'],
  cross: ['M25 BI', 'M26 ML', 'M29 classification', 'M33 rights requests', 'M60 controls'],
  freg: { src: 62, sub: [
    ['1', 'Ingestion', 10, { model: 'fix.data.pipeline', cols: ['code', 'name', 'data_source_id', 'source_system', 'layer', 'load_mode', 'schedule', 'state'], screens: ['M62-ingestion', 'M62-sources', 'M62-backfill'], reports: ['Freshness SLA'], forms: ['Data Pipeline', 'Data Source', 'Pipeline Run'] }],
    ['2', 'Medallion & Transformation', 9, { model: 'fix.data.run', cols: ['name', 'pipeline_id', 'kind', 'stage', 'started_at', 'rows_written', 'state'], screens: ['M62-medallion', 'M62-backfill'], reports: ['Freshness SLA'], forms: ['Pipeline Run'] }],
    ['3', 'Dimensional Model', 10, { model: 'fix.data.entity', cols: ['name', 'entity_type', 'model_kind', 'grain_declaration', 'owner_module', 'steward_id', 'classification'], screens: ['M62-dimensional', 'M62-dimensions'], reports: [], forms: ['Data Entity', 'Conformed Dimension'] }],
    ['4', 'Semantic Layer', 9, { model: 'fix.metric.definition', cols: ['code', 'name', 'domain_area', 'grain', 'owner_role', 'state'], screens: ['M62-metrics', 'M62-metric-versions', 'M62-metric-consumers', 'M62-glossary', 'M62-contracts'], reports: [], forms: ['Metric Definition', 'Metric Version', 'Metric Consumer', 'Glossary Term', 'Data Contract'] }],
    ['5', 'Quality & Observability', 10, { model: 'fix.data.quality.rule', cols: ['name', 'entity_id', 'rule_type', 'threshold', 'severity', 'last_result', 'state'], screens: ['M62-rules', 'M62-quality', 'M62-observability', 'M62-incidents'], reports: ['Data Quality Scorecard', 'Freshness SLA'], forms: ['Quality Rule', 'Quality Test', 'Data Incident'] }],
    ['6', 'Catalogue & Lineage', 8, { model: 'fix.data.lineage', cols: ['name', 'source_entity_id', 'target_entity_id', 'lineage_order'], screens: ['M62-data-lineage', 'M62-dimensional', 'M62-catalog', 'M62-glossary'], reports: ['Lineage Coverage'], forms: ['Data Lineage', 'Data Entity', 'Glossary Term'] }],
    // The page lists M29's sensitive-field classification (M29 owns it, the
    // list refuses "+ New"); what M62 captures here is its retention policy,
    // the routed declassification and the analytical erasure.
    ['7', 'Security & Cost', 6, { model: 'fix.sensitive.field', create: 'M62-form-retention', cols: ['model_name', 'field_name', 'sensitivity', 'data_class', 'masking_rule'], screens: ['M62-masking', 'M62-retention', 'M62-declass', 'M62-erasure', 'M62-disposition'], reports: ['Cost per Domain'], forms: ['Retention Policy', 'Declassification Authorisation', 'Analytical Erasure', 'Sensitive Field'] }]
  ] }
};

export const SCREENS = {
  /* ---- Pipelines ---- */
  'M62-sources': { kind: 'model_list', model: 'fix.data.source', stateField: 'state',
    cols: ['code', 'name', 'source_type', 'owner_module', 'business_owner_id', 'steward_id', 'pipeline_count', 'state'],
    actions: [{ m: 'action_activate', l: 'Activate' }, { m: 'action_retire', l: 'Retire' }] },
  'M62-ingestion': { kind: 'model_list', model: 'fix.data.pipeline', stateField: 'state',
    cols: ['code', 'name', 'data_source_id', 'layer', 'target_entity_id', 'load_mode', 'schedule', 'freshness_sla_minutes', 'state'],
    actions: [{ m: 'action_pause', l: 'Pause' }, { m: 'action_resume', l: 'Resume' }] },
  'M62-medallion': { kind: 'model_list', model: 'fix.data.run', stateField: 'state',
    cols: ['name', 'pipeline_id', 'stage', 'started_at', 'duration_minutes', 'rows_read', 'rows_written', 'state'],
    actions: [{ m: 'action_finish', l: 'Finish' }, { m: 'action_fail', l: 'Mark Failed' }] },
  'M62-backfill': { kind: 'model_list', model: 'fix.data.run', stateField: 'state',
    cols: ['name', 'pipeline_id', 'kind', 'period_from', 'period_to', 'replay_of_run_id', 'stage', 'rows_written', 'state'],
    actions: [{ m: 'action_finish', l: 'Finish' }, { m: 'action_fail', l: 'Mark Failed' }] },

  /* ---- Modelling ---- */
  'M62-dimensional': { kind: 'model_list', model: 'fix.data.entity',
    cols: ['name', 'entity_type', 'model_kind', 'grain_declaration', 'warehouse_layer', 'owner_module', 'steward_id', 'classification'] },
  'M62-dimensions': { kind: 'model_list', model: 'fix.data.dimension',
    cols: ['name', 'entity_id', 'natural_key', 'scd_type', 'surrogate_key_strategy', 'source_master_module'] },
  'M62-contracts': { kind: 'model_list', model: 'fix.data.contract', stateField: 'state',
    // No "Activate" button (A11 audit G1): the backend removed action_activate
    // from this surface on purpose — a contract activates only from an
    // approved M63 task (producer sign -> request approval -> decision).
    cols: ['dataset_code', 'version', 'name', 'entity_id', 'producer', 'producer_signed_by', 'schema_version', 'state'],
    actions: [{ m: 'action_producer_sign', l: 'Producer Sign' },
      { m: 'action_request_approval', l: 'Request Activation (M63)' },
      { m: 'action_new_version', l: 'New Version' }] },

  /* ---- Governance ---- */
  'M62-metrics': { kind: 'model_list', model: 'fix.metric.definition', stateField: 'state',
    // No "Publish" button (A11 audit G2): a metric publishes through its
    // VERSION (steward review, then an approved M63 request) — the
    // definition has no one-click publish and the surface refuses it.
    cols: ['code', 'name', 'domain_area', 'grain', 'owner_role', 'current_version_id', 'state'],
    actions: [{ m: 'action_retire', l: 'Retire' }] },
  'M62-metric-versions': { kind: 'model_list', model: 'fix.metric.version', stateField: 'state',
    cols: ['name', 'definition_id', 'version', 'grain', 'steward_reviewed_by', 'approval_state', 'published_at', 'state'],
    actions: [{ m: 'action_steward_review', l: 'Record Steward Review' },
      { m: 'action_request_approval', l: 'Request Publication (M63)' }] },
  'M62-metric-consumers': { kind: 'model_list', model: 'fix.metric.consumer',
    cols: ['definition_id', 'consumer', 'consumer_type', 'note'] },
  'M62-catalog': { kind: 'table_report', module: 'M62', report: 'lineage_coverage', title: 'Catalogue & Glossary (lineage)', period: false },
  'M62-glossary': { kind: 'model_list', model: 'fix.glossary.term',
    cols: ['term_en', 'term_bn', 'owner_id', 'synonyms', 'metric_ids'] },
  'M62-quality': { kind: 'model_list', model: 'fix.data.quality.test',
    cols: ['name', 'rule_id', 'checked_at', 'observed_value', 'threshold', 'passed', 'measured'] },
  'M62-observability': { kind: 'table_report', module: 'M62', report: 'freshness_sla', title: 'Observability — freshness SLA', period: false },

  /* ---- Security ---- */
  // The classification lives in M29; this screen shows which sensitive fields exist.
  'M62-masking': { kind: 'model_list', model: 'fix.sensitive.field', create: false,
    cols: ['model_name', 'field_name', 'sensitivity', 'data_class', 'masking_rule'] },
  'M62-retention': { kind: 'model_list', model: 'fix.data.retention.policy',
    cols: ['entity_id', 'tier', 'retention_months', 'statutory_floor_months', 'pending_months', 'legal_hold', 'volume_gb', 'monthly_cost', 'purge_rule'],
    actions: [{ m: 'action_request_shorten', l: 'Request Shortening (M63)',
      asks: [{ kwarg: 'new_months', label: 'New retention period (months)', number: true }] },
      { m: 'action_purge', l: 'Run Disposition' }] },
  'M62-declass': { kind: 'model_list', model: 'fix.data.declassification.auth', stateField: 'state',
    cols: ['name', 'entity_id', 'from_classification', 'to_classification', 'expires_on', 'approval_state', 'approved_by', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval (M63)' }] },
  'M62-erasure': { kind: 'model_list', model: 'fix.data.erasure', stateField: 'state',
    cols: ['name', 'request_id', 'partner_id', 'statutory_due', 'bronze_done', 'silver_done', 'gold_done', 'feature_store_done', 'extracts_done', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete Erasure' }] },
  // Written by a disposition run or the weekly report; append-only.
  'M62-disposition': { kind: 'model_list', model: 'fix.data.purge.evidence', create: false,
    cols: ['policy_id', 'cutoff', 'eligible', 'purged', 'action', 'ran_by', 'note'] },

  /* ---- extra operational surfaces (incidents + runs + rules) ---- */
  'M62-incidents': { kind: 'model_list', model: 'fix.data.incident', stateField: 'state',
    cols: ['name', 'title', 'entity_id', 'severity', 'owner_id', 'detected_at', 'due_at', 'state'],
    actions: [{ m: 'action_fix', l: 'Mark Fixed' }, { m: 'action_close', l: 'Close' }] },
  'M62-rules': { kind: 'model_list', model: 'fix.data.quality.rule',
    cols: ['name', 'entity_id', 'rule_type', 'check_field', 'threshold', 'severity', 'active', 'last_result', 'last_measured', 'state'],
    actions: [{ m: 'action_measure', l: 'Measure Now' }] },

  /* ---- report screens (own pack each) ---- */
  'M62-rpt-quality': { kind: 'table_report', module: 'M62', report: 'quality_scorecard', title: 'Data Quality Scorecard', period: false },
  'M62-rpt-freshness': { kind: 'table_report', module: 'M62', report: 'freshness_sla', title: 'Freshness SLA', period: false },
  'M62-rpt-lineage': { kind: 'table_report', module: 'M62', report: 'lineage_coverage', title: 'Lineage Coverage', period: false },
  'M62-rpt-cost': { kind: 'table_report', module: 'M62', report: 'cost_per_domain', title: 'Cost per Domain', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M62-form-source': {
    kind: 'model_form',
    model: 'fix.data.source',
    title: 'Data Source',
    back: 'M62-sources',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'source', label: 'Source', bn: 'উৎস', icon: '🔌', badge: '6' },
      { id: 'ownership', label: 'Ownership', bn: 'মালিকানা', icon: '👤', badge: '6' }
    ],
    sections: [
      { tab: 'source', title: 'Producing System (FR-DAT-001..004)', note: 'A system or module the platform ingests from, and how: change data capture, domain events, batch extracts, files or an external API. The connection reference names the vault entry; a password, token or key is refused.',
        fields: [
          { name: 'code', required: true, label: 'Source Code' },
          { name: 'name', required: true, label: 'Source Name' },
          { name: 'source_type', required: true, label: 'Source Type' },
          { name: 'owner_module', required: true, label: 'Producing Module' },
          { name: 'connection_ref', label: 'Connection Reference (vault entry name)' },
          { name: 'description', type: 'text', label: 'Description' }
        ] },
      { tab: 'ownership', title: 'Owner and Steward (BRU-DAT-09)', note: 'A source is activated by a Data Governance Officer once it has a named business owner and a named technical steward. A retired source feeds no pipeline.',
        fields: [
          { name: 'business_owner_id', label: 'Business Owner' },
          { name: 'steward_id', label: 'Technical Steward' },
          { name: 'active_from', label: 'Active From' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'activated_by', readonly: true, label: 'Activated By' },
          { name: 'activated_at', readonly: true, label: 'Activated At' }
        ] }
    ]
  },

  'M62-form-contract': {
    kind: 'model_form',
    model: 'fix.data.contract',
    title: 'Data Contract',
    back: 'M62-contracts',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', deprecated: 'Deprecated' } },
    tabs: [
      { id: 'contract', label: 'Contract', bn: 'চুক্তি', icon: '📜', badge: '9' },
      { id: 'signature', label: 'Co-Signature', bn: 'সহ-স্বাক্ষর', icon: '🖋️', badge: '6' }
    ],
    sections: [
      { tab: 'contract', title: 'Contract', note: 'A contract states what the producer guarantees — schema version, freshness and completeness — so consumers can rely on the dataset instead of inspecting it. An active contract is frozen: change it with New Version.',
        fields: [
          { name: 'dataset_code', required: true, label: 'Dataset Code' },
          { name: 'name', required: true, label: 'Dataset Name' },
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'data_source_id', label: 'Producing Source' },
          { name: 'producer', required: true, label: 'Producer' },
          { name: 'consumers', label: 'Consumers' },
          { name: 'schema_version', required: true, label: 'Schema Version' },
          { name: 'freshness_sla_minutes', label: 'Freshness SLO (minutes)' },
          { name: 'breaking_change_notice_days', label: 'Breaking-Change Notice (days)' },
          { name: 'guarantees', type: 'text', label: 'Guarantees' }
        ] },
      { tab: 'signature', title: 'Producer, then Platform (BRU-DAT-10)', note: 'The named producer signatory (or a Data Governance Officer) signs the producer side; the platform side is an M63 request decided by another officer. A Silver or Gold load of the entity is refused until a contract is active.',
        fields: [
          { name: 'producer_signatory_id', label: 'Producer Signatory' },
          { name: 'producer_signed_by', readonly: true, label: 'Producer Signed By' },
          { name: 'producer_signed_at', readonly: true, label: 'Producer Signed At' },
          { name: 'version', readonly: true, label: 'Version' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'state', readonly: true, label: 'State' }
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
      { title: 'Metric', note: 'One definition per metric code. The formula must state numerator and denominator, so two dashboards cannot disagree about the same number. It is published by publishing a Metric Version; once published, the code, formula, grain and source change only through a new version.',
        fields: [
          { name: 'code', required: true, label: 'Metric Code' },
          { name: 'name', required: true, label: 'Metric Name' },
          { name: 'domain_area', required: true, label: 'Domain' },
          { name: 'grain', required: true, label: 'Grain' },
          { name: 'source_entity_id', label: 'Source Entity' },
          { name: 'owner_role', label: 'Owner Role' },
          { name: 'current_version_id', readonly: true, label: 'Published Version' },
          { name: 'state', readonly: true, label: 'State' }
        ] },
      { title: 'Definition', fields: [
          { name: 'definition', required: true, type: 'text', label: 'Definition' }
        ] }
    ]
  },

  'M62-form-version': {
    kind: 'model_form',
    model: 'fix.metric.version',
    title: 'Metric Version',
    back: 'M62-metric-versions',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    tabs: [
      { id: 'draft', label: 'The Definition', bn: 'সংজ্ঞা', icon: '📐', badge: '5' },
      { id: 'publication', label: 'Review & Publication', bn: 'পর্যালোচনা ও প্রকাশ', icon: '✅', badge: '8' }
    ],
    sections: [
      { tab: 'draft', title: 'What This Version States (FR-DAT-016/019)', note: 'The version number is given by the server. A version after the first records why the definition changes. Once the steward has reviewed it, the text is frozen: a further change is a new version.',
        fields: [
          { name: 'definition_id', required: true, label: 'Metric' },
          { name: 'definition_text', required: true, type: 'text', label: 'Formula (numerator / denominator, in words)' },
          { name: 'grain', required: true, label: 'Grain' },
          { name: 'source_entity_id', label: 'Source Entity' },
          { name: 'change_reason', type: 'text', label: 'Reason for the Change' }
        ] },
      { tab: 'publication', title: 'Steward Review, then M63 (BRU-DAT-02/03)', note: 'The steward reviews first; the publication request lists every registered consumer the change reaches, and another Data Governance Officer decides it. Publishing retires the earlier version and the definition follows the new text.',
        fields: [
          { name: 'version', readonly: true, label: 'Version' },
          { name: 'steward_reviewed_by', readonly: true, label: 'Steward Reviewed By' },
          { name: 'steward_reviewed_at', readonly: true, label: 'Steward Reviewed At' },
          { name: 'impact_snapshot', readonly: true, type: 'text', label: 'Consumers Reached' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'published_by', readonly: true, label: 'Published By' },
          { name: 'published_at', readonly: true, label: 'Published At' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M62-form-consumer': {
    kind: 'model_form',
    model: 'fix.metric.consumer',
    title: 'Metric Consumer',
    back: 'M62-metric-consumers',
    sections: [
      { title: 'Who Reads the Metric', note: 'The consumer register: every dashboard, report, API, model or portal that reads a metric. A new version lists them as the consumers it reaches, and a metric is not retired while any remains (BRU-DAT-04).',
        fields: [
          { name: 'definition_id', required: true, label: 'Metric' },
          { name: 'consumer', required: true, label: 'Consumer (e.g. M25:executive_pack)' },
          { name: 'consumer_type', label: 'Consumer Type' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },

  'M62-form-glossary': {
    kind: 'model_form',
    model: 'fix.glossary.term',
    title: 'Glossary Term',
    back: 'M62-glossary',
    tabs: [
      { id: 'term', label: 'Term', bn: 'শব্দ', icon: '📖', badge: '6' },
      { id: 'links', label: 'Related', bn: 'সম্পর্কিত', icon: '🔗', badge: '2' }
    ],
    sections: [
      { tab: 'term', title: 'Business Glossary (FR-DAT-022)', note: 'One plain-language meaning per term, in English and Bengali, with a named business owner.',
        fields: [
          { name: 'term_en', required: true, label: 'Term (English)' },
          { name: 'term_bn', label: 'Term (Bengali)' },
          { name: 'definition', required: true, type: 'text', label: 'Plain-Language Meaning' },
          { name: 'definition_bn', type: 'text', label: 'Meaning (Bengali)' },
          { name: 'owner_id', required: true, label: 'Business Owner' },
          { name: 'synonyms', label: 'Synonyms' }
        ] },
      { tab: 'links', title: 'What It Explains', fields: [
          { name: 'metric_ids', label: 'Related Metrics' },
          { name: 'entity_ids', label: 'Related Datasets' }
        ] }
    ]
  },

  'M62-form-quality': {
    kind: 'model_form',
    model: 'fix.data.quality.test',
    title: 'Quality Test',
    back: 'M62-quality',
    sections: [
      { title: 'Test Run', note: 'Records what was measured against the rule threshold. Pass/fail is computed from the observed value — it is never typed, and the threshold is the rule\'s own, stamped at run time. A test recorded here is labelled manual evidence; the rule\'s own Measure Now records a measured one.',
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
    tabs: [
      { id: 'pipeline', label: 'Pipeline', bn: 'পাইপলাইন', icon: '🛠️', badge: '8' },
      { id: 'order', label: 'Dependencies & Owner', bn: 'নির্ভরতা ও মালিক', icon: '🔗', badge: '5' }
    ],
    sections: [
      { tab: 'pipeline', title: 'Pipeline', note: 'Source, target entity, layer, load mode and the freshness SLO. The SLO is what the Freshness SLA report breaches against. With a data source picked, the source system defaults to its code; the source must be active.',
        fields: [
          { name: 'code', required: true, label: 'Pipeline Code' },
          { name: 'name', required: true, label: 'Pipeline Name' },
          { name: 'data_source_id', label: 'Data Source' },
          { name: 'source_system', label: 'Source System (blank: the data source\'s code)' },
          { name: 'target_entity_id', required: true, label: 'Target Entity' },
          { name: 'layer', required: true, label: 'Medallion Layer' },
          { name: 'load_mode', required: true, label: 'Load Mode' },
          { name: 'schedule', required: true, label: 'Schedule' }
        ] },
      { tab: 'order', title: 'Runs After (FR-DAT-008, AUT-DAT-01)', note: 'A run is refused while an upstream pipeline\'s latest load failed, is still running or never succeeded.',
        fields: [
          { name: 'upstream_ids', label: 'Runs After (Upstream)' },
          { name: 'owner_id', label: 'Pipeline Owner' },
          { name: 'freshness_sla_minutes', label: 'Freshness SLO (minutes)' },
          { name: 'last_success_at', readonly: true, label: 'Last Success' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M62-form-run': {
    kind: 'model_form',
    model: 'fix.data.run',
    title: 'Pipeline Run',
    back: 'M62-medallion',
    status: { field: 'state', labels: { running: 'Running', succeeded: 'Succeeded', failed: 'Failed' } },
    tabs: [
      { id: 'run', label: 'Run', bn: 'রান', icon: '▶️', badge: '7' },
      { id: 'backfill', label: 'Backfill / Replay', bn: 'ব্যাকফিল / রিপ্লে', icon: '⏪', badge: '4' }
    ],
    sections: [
      { tab: 'run', title: 'Run', note: 'A scheduled, backfill or replay load landing in one medallion stage. A Silver or Gold load needs an active data contract for the entity; a run never starts on a failed upstream. Finishing measures the duration from the start timestamp; a concluded run is history.',
        fields: [
          { name: 'pipeline_id', required: true, label: 'Pipeline' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'stage', required: true, label: 'Medallion Stage' },
          { name: 'started_at', label: 'Started At' },
          { name: 'rows_read', label: 'Rows Read' },
          { name: 'rows_written', label: 'Rows Written' },
          { name: 'rows_rejected', label: 'Rows Rejected' },
          { name: 'state', readonly: true, label: 'State' }
        ] },
      { tab: 'backfill', title: 'Rebuild a Period from Bronze (AUT-DAT-16)', note: 'A backfill or replay states the period it rebuilds and why (it restates figures that may already be published). A replay names the run it replays, of the same pipeline.',
        fields: [
          { name: 'period_from', label: 'Period From' },
          { name: 'period_to', label: 'Period To' },
          { name: 'replay_of_run_id', label: 'Replays Run' },
          { name: 'reason', type: 'text', label: 'Reason' }
        ] }
    ]
  },

  'M62-form-incident': {
    kind: 'model_form',
    model: 'fix.data.incident',
    title: 'Data Quality Incident',
    back: 'M62-incidents',
    status: { field: 'state', labels: { open: 'Open', fixed: 'Fixed', closed: 'Closed' } },
    tabs: [
      { id: 'incident', label: 'Incident', bn: 'ঘটনা', icon: '🚨', badge: '9' },
      { id: 'narrative', label: 'Narrative', bn: 'বিবরণ', icon: '📝', badge: '3' }
    ],
    sections: [
      { tab: 'incident', title: 'Incident', note: 'Open → fixed → closed. Seeded from a failing quality test or reported by a consumer. Fix and Close demand an owner, a root cause and a resolution.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'rule_id', label: 'Quality Rule' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'classification', label: 'Classification' },
          { name: 'owner_id', label: 'Owner' },
          { name: 'detected_at', label: 'Detected At' },
          { name: 'due_at', readonly: true, label: 'Due (SLA)' },
          { name: 'state', readonly: true, label: 'State' }
        ] },
      { tab: 'narrative', title: 'Narrative', fields: [
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
    tabs: [
      { id: 'retention', label: 'Retention', bn: 'রিটেনশন', icon: '🗄️', badge: '6' },
      { id: 'cost', label: 'Cost', bn: 'খরচ', icon: '💰', badge: '3' }
    ],
    sections: [
      { tab: 'retention', title: 'Retention (FR-DAT-036, BRU-DAT-16)', note: 'One active policy per entity. A period below the statutory floor is refused. Shortening an active policy is a request routed through M63 (Request Shortening on the list). A legal hold, set and lifted by a Data Governance Officer, blocks every purge and every shortening.',
        fields: [
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'tier', required: true, label: 'Tier' },
          { name: 'retention_months', required: true, label: 'Retention (months)' },
          { name: 'statutory_floor_months', label: 'Statutory Floor (months)' },
          { name: 'purge_rule', label: 'Purge Rule (archive / pseudonymise / delete)' },
          { name: 'legal_hold', label: 'Legal Hold' },
          { name: 'pending_months', readonly: true, label: 'Shortening To (awaiting approval)' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'cost', title: 'Retention & Cost', note: 'Monthly cost is computed from the current volume and the storage rate — a measured projection, not a cloud bill.',
        fields: [
          { name: 'volume_gb', label: 'Volume (GB)' },
          { name: 'storage_cost_per_gb', label: 'Storage Cost / GB (BDT)' },
          { name: 'monthly_cost', readonly: true, label: 'Monthly Cost (BDT)' }
        ] }
    ]
  },

  'M62-form-declass': {
    kind: 'model_form',
    model: 'fix.data.declassification.auth',
    title: 'Declassification Authorisation',
    back: 'M62-declass',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', expired: 'Expired' } },
    sections: [
      { title: 'Moving Data to a Less Sensitive Class (BRU-DAT-11)', note: 'A classification downgrade is an approved, time-limited act: the request names the entity, the class it moves to, why, and the day the authorisation lapses (the classification then reverts). It is routed through M63 to a Data Governance Officer; only then can the entity\'s classification be lowered. The From class is the entity\'s current one.',
        fields: [
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'from_classification', label: 'From (current classification)' },
          { name: 'to_classification', required: true, label: 'To' },
          { name: 'reason', required: true, type: 'text', label: 'Reason and Lawful Basis' },
          { name: 'expires_on', required: true, label: 'Expires On' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'approved_by', readonly: true, label: 'Approved By' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M62-form-erasure': {
    kind: 'model_form',
    model: 'fix.data.erasure',
    title: 'Analytical Erasure',
    back: 'M62-erasure',
    status: { field: 'state', labels: { open: 'Open', completed: 'Completed' } },
    tabs: [
      { id: 'request', label: 'Request', bn: 'অনুরোধ', icon: '🧾', badge: '3' },
      { id: 'layers', label: 'Layers Erased', bn: 'স্তর মুছে ফেলা', icon: '🧹', badge: '7' },
      { id: 'completion', label: 'Completion', bn: 'সমাপ্তি', icon: '✅', badge: '3' }
    ],
    sections: [
      { tab: 'request', title: 'The M33 Erasure Request (AUT-DAT-13)', note: 'Opened automatically when the DPO starts an erasure request, or here for an erasure request already in hand. One per request.',
        fields: [
          { name: 'request_id', required: true, label: 'Erasure Request (M33)' },
          { name: 'partner_id', readonly: true, label: 'Party' },
          { name: 'statutory_due', readonly: true, label: 'Statutory Due' }
        ] },
      { tab: 'layers', title: 'Every Analytical Layer (BRU-DAT-15)', note: 'Tick each layer once the party\'s data is erased from it, and name the evidence. An incomplete erasure is a regulatory failure, so completion refuses any layer left.',
        fields: [
          { name: 'bronze_done', label: 'Bronze (raw) erased' },
          { name: 'silver_done', label: 'Silver (conformed) erased' },
          { name: 'gold_done', label: 'Gold (serving) erased' },
          { name: 'feature_store_done', label: 'Feature store erased' },
          { name: 'extracts_done', label: 'Extracts and sandboxes erased' },
          { name: 'evidence_ref', label: 'Completion Evidence' },
          { name: 'note', type: 'text', label: 'Note' }
        ] },
      { tab: 'completion', title: 'Completed by a Data Governance Officer', note: 'Complete Erasure (on the list) stamps who completed it and tells the M33 request. Completed is final.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'completed_by', readonly: true, label: 'Completed By' },
          { name: 'completed_at', readonly: true, label: 'Completed At' }
        ] }
    ]
  },

  /* ===== registry completion forms ===== */
  'M62-form-entity': {
    kind: 'model_form',
    model: 'fix.data.entity',
    title: "Data Entity",
    back: 'M62-dimensional',
    tabs: [
      { id: 'entity', label: 'Entity', bn: 'এন্টিটি', icon: '🗃️', badge: '6' },
      { id: 'model', label: 'Model & Layer', bn: 'মডেল ও স্তর', icon: '🧱', badge: '5' }
    ],
    sections: [
      { tab: 'entity', title: "Data Entity", note: "A catalogued dataset: what it is, which module owns it and how sensitive it is. Lowering its classification needs an approved Declassification Authorisation.",
        fields: [
          { name: 'name', required: true, label: "Entity Name" },
          { name: 'entity_type', label: "Entity Type" },
          { name: 'owner_module', label: "Owning Module" },
          { name: 'steward_id', label: "Data Steward" },
          { name: 'classification', label: "Classification" },
          { name: 'retention_policy', label: "Retention Policy" }
        ] },
      { tab: 'model', title: "Dimensional Role and Layer (FR-DAT-009/012)", note: "A fact declares its grain (what one row means). The Odoo model lets the quality runner measure the entity and a disposition count it. Residency-classified (S3) data never lands in a warehouse layer.",
        fields: [
          { name: 'model_kind', label: "Model Role" },
          { name: 'grain_declaration', label: "Declared Grain" },
          { name: 'warehouse_layer', label: "Warehouse Layer" },
          { name: 'res_model', label: "Odoo Model (e.g. fix.service.order)" },
          { name: 'description', type: 'text', label: "Description" }
        ] }
    ]
  },
  'M62-form-dimension': {
    kind: 'model_form',
    model: 'fix.data.dimension',
    title: 'Conformed Dimension',
    back: 'M62-dimensions',
    tabs: [
      { id: 'keys', label: 'Keys & History', bn: 'কী ও ইতিহাস', icon: '🔑', badge: '6' },
      { id: 'use', label: 'Attributes & Use', bn: 'বৈশিষ্ট্য ও ব্যবহার', icon: '🧩', badge: '3' }
    ],
    sections: [
      { tab: 'keys', title: 'Conformed Dimension (FR-DAT-010/011)', note: 'Party, product, asset, employee, branch, supplier, date or geography, used identically by every fact. Type 2 and 3 keep history: name the attributes tracked, so a transaction is analysed against the values in force when it happened.',
        fields: [
          { name: 'name', required: true, label: 'Dimension Name' },
          { name: 'entity_id', required: true, label: 'Catalogue Entity' },
          { name: 'natural_key', required: true, label: 'Natural Key' },
          { name: 'surrogate_key_strategy', required: true, label: 'Surrogate Key' },
          { name: 'scd_type', required: true, label: 'Slowly-Changing Type' },
          { name: 'tracked_attributes', type: 'text', label: 'History-Tracked Attributes' }
        ] },
      { tab: 'use', title: 'Attributes and the Facts That Use It', fields: [
          { name: 'attributes', type: 'text', label: 'Attribute List' },
          { name: 'source_master_module', label: 'Master Owned By (module)' },
          { name: 'fact_entity_ids', label: 'Used By Facts' }
        ] }
    ]
  },
  'M62-form-qrule': {
    kind: 'model_form',
    model: 'fix.data.quality.rule',
    title: "Quality Rule",
    back: 'M62-rules',
    sections: [
      { title: "Quality Rule", note: "A rule states what is measured on an entity and the threshold its quality percentage must reach. With a check field on an entity mapped to an Odoo model, Measure Now and the hourly runner measure it; otherwise results are recorded by people and labelled manual. The severity is the severity of the incident a failure opens.",
        fields: [
          { name: 'name', required: true, label: "Rule Name" },
          { name: 'entity_id', required: true, label: "Entity" },
          { name: 'rule_type', label: "Rule Type" },
          { name: 'check_field', label: "Check Field (column measured)" },
          { name: 'freshness_window_hours', label: "Freshness Window (hours, timeliness)" },
          { name: 'threshold', label: "Threshold %" },
          { name: 'severity', label: "Incident Severity" },
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
      { title: "Data Lineage", note: "One edge from a source entity to a target entity and what happens between them. An entity is never its own upstream.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'source_entity_id', required: true, label: "Source" },
          { name: 'target_entity_id', required: true, label: "Target" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'lineage_order', label: "Order" },
          { name: 'transformation', type: 'text', label: "Transformation Logic" }
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
  'M62:Data Source': 'M62-form-source',
  'M62:Data Pipeline': 'M62-form-pipeline',
  'M62:Pipeline Run': 'M62-form-run',
  'M62:Data Entity': 'M62-form-entity',
  'M62:Conformed Dimension': 'M62-form-dimension',
  'M62:Metric Version': 'M62-form-version',
  'M62:Metric Consumer': 'M62-form-consumer',
  'M62:Glossary Term': 'M62-form-glossary',
  'M62:Quality Rule': 'M62-form-qrule',
  'M62:Data Incident': 'M62-form-incident',
  'M62:Data Lineage': 'M62-form-data-lineage',
  'M62:Retention Policy': 'M62-form-retention',
  'M62:Declassification Authorisation': 'M62-form-declass',
  'M62:Analytical Erasure': 'M62-form-erasure',
  // M29 owns the classification scheme; its form is offered from page 7.
  'M62:Sensitive Field': 'M29-form-sensitive',
  'M62:__by_model__': {
    'fix.data.source': 'M62-form-source',
    'fix.data.lineage': 'M62-form-data-lineage',
    'fix.data.entity': 'M62-form-entity',
    'fix.data.dimension': 'M62-form-dimension',
    'fix.data.quality.rule': 'M62-form-qrule',
    'fix.data.pipeline': 'M62-form-pipeline',
    'fix.data.run': 'M62-form-run',
    'fix.data.contract': 'M62-form-contract',
    'fix.metric.definition': 'M62-form-metric',
    'fix.metric.version': 'M62-form-version',
    'fix.metric.consumer': 'M62-form-consumer',
    'fix.glossary.term': 'M62-form-glossary',
    'fix.data.quality.test': 'M62-form-quality',
    'fix.data.incident': 'M62-form-incident',
    'fix.data.retention.policy': 'M62-form-retention',
    'fix.data.declassification.auth': 'M62-form-declass',
    'fix.data.erasure': 'M62-form-erasure'
  },
  'M62:__by_screen__': {
    'M62-sources': 'M62-form-source',
    'M62-data-lineage': 'M62-form-data-lineage',
    'M62-dimensional': 'M62-form-entity',
    'M62-dimensions': 'M62-form-dimension',
    'M62-rules': 'M62-form-qrule',
    'M62-ingestion': 'M62-form-pipeline',
    'M62-medallion': 'M62-form-run',
    'M62-backfill': 'M62-form-run',
    'M62-contracts': 'M62-form-contract',
    'M62-metrics': 'M62-form-metric',
    'M62-metric-versions': 'M62-form-version',
    'M62-metric-consumers': 'M62-form-consumer',
    'M62-glossary': 'M62-form-glossary',
    'M62-quality': 'M62-form-quality',
    'M62-incidents': 'M62-form-incident',
    'M62-retention': 'M62-form-retention',
    'M62-declass': 'M62-form-declass',
    'M62-erasure': 'M62-form-erasure'
  }
};

export const CREATE = {
  M62: { screen: 'M62-form-contract', model: 'fix.data.contract', label: 'Data Contract' }
};
