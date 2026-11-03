/** @odoo-module **/
/* A11 · Insights & Intelligence — M26 AI/ML Services (v2 re-audit).
 * Registry-faithful: 4 groups / 10 screens / 4 reports / 3 forms / freg 58.
 * The model registry and inference engines are real (fix.ml.*), governance
 * records are real, and generative/OCR surfaces declare their true status. */

export const MODULE = {
  area: 'A11', code: 'M26', en: 'AI/ML Services (14 models)', title: 'M26 · AI/ML Services (14 models)',
  bn: 'এআই/এমএল সেবা', icon: '🧠',
  desc: 'Dispatch scoring, Bengali fault classification, predictive maintenance, trade-in valuation — plus model governance and honest GenAI/OCR status.',
  kpis: [
    { l: 'Auto-Assign Rate', m: 'auto_assign_rate', suffix: '%' },
    { l: 'Demand MAPE', m: 'demand_mape', suffix: '%' },
    { l: 'Fault Classification F1', m: 'fault_f1' },
    { l: 'Churn Model AUC', m: 'churn_auc' },
    { l: 'Override Rate', m: 'override_rate', suffix: '%' },
    { l: 'Drift Alerts', m: 'drift_alerts' },
    { l: 'Models Live', m: 'models_live' },
    { l: 'Inferences (7d)', m: 'runs_7d' }
  ],
  groups: [
    { en: 'Portfolio', screens: [
      { id: 'M26-models', en: 'Model Portfolio (14)', bn: 'মডেল পোর্টফোলিও', t: 'g' },
      { id: 'M26-registry', en: 'Model Registry', bn: 'মডেল রেজিস্ট্রি', t: 'g' },
      { id: 'M26-runs', en: 'Inference Run Log', bn: 'ইনফারেন্স রান লগ', t: 'g' },
      { id: 'M26-ai', en: 'Predictive Failure Predictions', bn: 'প্রেডিক্টিভ ফেইলিউর', t: 'g' }
    ]},
    { en: 'Operations', screens: [
      { id: 'M26-deploy', en: 'Deployment Patterns', bn: 'ডিপ্লয়মেন্ট প্যাটার্ন', t: 'g' },
      { id: 'M26-monitor', en: 'Production Monitoring', bn: 'প্রোডাকশন মনিটরিং', t: 'd' },
      { id: 'M26-fallback', en: 'Inference Fallback', bn: 'ফলব্যাক', t: 'g' }
    ]},
    { en: 'Governance', screens: [
      { id: 'M26-governance', en: 'Guard Rails & HITL', bn: 'গার্ড রেল', t: 'g' },
      { id: 'M26-bias', en: 'Bias Testing', bn: 'বায়াস টেস্টিং', t: 'g' },
      { id: 'M26-cards', en: 'Model Cards', bn: 'মডেল কার্ড', t: 'g' }
    ]},
    { en: 'Generative', screens: [
      { id: 'M26-genai', en: 'Self-Hosted GenAI + RAG', bn: 'জেনএআই ও RAG', t: 'c' },
      { id: 'M26-ocr', en: 'OCR & Bengali NLP', bn: 'ওসিআর ও বাংলা এনএলপি', t: 'g' }
    ]}
  ],
  reports: ['Model Performance Pack', 'Override Analysis', 'Drift Report', 'Fairness Summary', 'Model Accuracy & Retraining Log'],
  forms: ['Model Version', 'Evaluation Gate', 'Guard-Rail Config', 'Run ML Model Inference'],
  cross: ['M02 Dispatch', 'M15 Parts', 'M48 Predictive Maintenance'],
  freg: { src: 58, sub: [
    ['1', 'Portfolio & Governance', 10, { model: 'fix.ml.model', cols: ['code', 'name', 'kind', 'implementation', 'status', 'owning_module'], screens: ['M26-models', 'M26-governance'] }],
    ['2', 'Training Pipelines', 8, { model: 'fix.ml.model.version', cols: ['model_id', 'version', 'training_dataset', 'artifact_ref', 'state'], screens: ['M26-registry'] }],
    ['3', 'Evaluation Gates', 7, { model: 'fix.ml.evaluation.gate', cols: ['version_id', 'gate', 'result', 'checked_by', 'checked_at'], screens: ['M26-bias', 'M26-registry'] }],
    ['4', 'Deployment & Monitoring', 11, { model: 'fix.ml.model.version', cols: ['model_id', 'version', 'deployment_mode', 'deployed_at', 'drift_score', 'state'], screens: ['M26-deploy', 'M26-monitor', 'M26-fallback'], domain: [['deployment_mode', '!=', 'none']] }],
    ['5', 'Explainability', 5, { model: 'fix.ml.model.version', cols: ['model_id', 'version', 'model_card', 'bias_status', 'approved_by'], screens: ['M26-cards', 'M26-runs'] }],
    ['6', 'GenAI & RAG', 9, { model: 'fix.ml.model', cols: ['code', 'name', 'kind', 'implementation', 'status'], screens: ['M26-genai', 'M26-governance'] }],
    ['7', 'Bengali NLP & OCR', 8, { model: 'fix.ml.inference.run', cols: ['model_code', 'input_text', 'state', 'latency_ms', 'ran_at'], screens: ['M26-ocr', 'M26-runs'] }]
  ] }
};

export const SCREENS = {
  /* Portfolio */
  'M26-models': { kind: 'model_list', model: 'fix.ml.model',
    cols: ['code', 'name', 'kind', 'implementation', 'status', 'owning_module', 'run_count', 'last_run_at'] },
  'M26-registry': { kind: 'model_list', model: 'fix.ml.model.version', stateField: 'state',
    cols: ['model_id', 'version', 'state', 'deployment_mode', 'bias_status', 'drift_score', 'approved_by'] },

  /* Operations */
  'M26-deploy': { kind: 'model_list', model: 'fix.ml.model.version', stateField: 'deployment_mode',
    domain: [['deployment_mode', '!=', 'none']],
    cols: ['model_id', 'version', 'deployment_mode', 'deployed_at', 'state'] },
  'M26-monitor': { kind: 'table_report', module: 'M26', report: 'production_monitoring', title: 'Production Monitoring', period: false },
  'M26-fallback': { kind: 'table_report', module: 'M26', report: 'fallback_status', title: 'Inference Fallback', period: false },

  /* Governance */
  'M26-governance': { kind: 'model_list', model: 'fix.ml.guardrail', stateField: 'active',
    cols: ['name', 'model_id', 'rule', 'action', 'active'] },
  'M26-bias': { kind: 'table_report', module: 'M26', report: 'fairness_summary', title: 'Bias Testing', period: false },
  'M26-cards': { kind: 'model_list', model: 'fix.ml.model.version', stateField: 'state',
    cols: ['model_id', 'version', 'state', 'model_card', 'approved_by'] },

  /* Generative (honest status catalogs) */
  'M26-genai': { kind: 'table_report', module: 'M26', report: 'genai_catalog', title: 'Self-Hosted GenAI + RAG', period: false },
  'M26-ocr': { kind: 'table_report', module: 'M26', report: 'bengali_nlp_catalog', title: 'OCR & Bengali NLP', period: false },

  /* Extras kept from the first build (not registry, still live) */
  'M26-ai': { kind: 'model_list', model: 'fix.predictive.maintenance', create: false,
    cols: ['name', 'equipment_id', 'prediction', 'confidence', 'estimated_days_to_failure', 'work_order_created'],
    stateField: 'prediction',
    actions: [{ m: 'action_create_preventive_wo', l: 'Create Preventive Work Order' }] },
  'M26-runs': { kind: 'model_list', model: 'fix.ml.inference.run', stateField: 'state',
    cols: ['model_code', 'input_text', 'field_order_id', 'state', 'latency_ms', 'ran_at', 'ran_by'],
    actions: [{ m: 'action_execute', l: 'Execute Engine' }] },
  'M26-accuracy': { kind: 'table_report', module: 'M26', report: 'model_accuracy_retraining', title: 'Model Accuracy & Retraining Log', period: false },

  /* Report packs (the four registry chips) */
  'M26-rpt-performance': { kind: 'table_report', module: 'M26', report: 'model_performance_pack', title: 'Model Performance Pack', period: false },
  'M26-rpt-override': { kind: 'table_report', module: 'M26', report: 'override_analysis', title: 'Override Analysis', period: false },
  'M26-rpt-drift': { kind: 'table_report', module: 'M26', report: 'drift_report', title: 'Drift Report', period: false },
  'M26-rpt-fairness': { kind: 'table_report', module: 'M26', report: 'fairness_summary', title: 'Fairness Summary', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M26-form-model': {
    kind: 'model_form',
    model: 'fix.ml.model',
    title: 'ML Model Catalogue Entry',
    back: 'M26-models',
    status: { field: 'status', labels: { production: 'Production', planned: 'Planned' } },
    sections: [
      { title: 'Model', note: 'One catalogue entry per REAL engine. Implementation states honestly whether a live engine exists or the entry is a declared seam.',
        fields: [
          { name: 'code', required: true, label: 'Model Code' },
          { name: 'name', required: true, label: 'Model Name' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'implementation', required: true, label: 'Implementation' },
          { name: 'status', required: true, label: 'Status' },
          { name: 'owning_module', label: 'Owning Module' }
        ] },
      { title: 'Notes', fields: [
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M26-form-version': {
    kind: 'model_form',
    model: 'fix.ml.model.version',
    title: 'Model Version',
    back: 'M26-registry',
    status: { field: 'state', labels: { draft: 'Draft', evaluated: 'Evaluated', approved: 'Approved', deployed: 'Deployed', retired: 'Retired' } },
    sections: [
      {
        title: 'Version & Artifact',
        note: 'One version of a registered model. The artifact reference must point at a real registry object — metrics are keyed in from the evaluation run, never estimated.',
        fields: [
          { name: 'model_id', required: true, label: 'Registered Model' },
          { name: 'version', required: true, label: 'Version' },
          { name: 'artifact_ref', label: 'Artifact Reference' },
          { name: 'training_dataset', label: 'Training Dataset' }
        ]
      },
      {
        title: 'Evaluation & Release',
        note: 'Bias status and drift score come from recorded evaluations; deployment mode drives the Deployment Patterns screen.',
        fields: [
          { name: 'metrics_json', label: 'Metrics (JSON)', type: 'text' },
          { name: 'bias_status', required: true, label: 'Bias Test Status' },
          { name: 'bias_notes', label: 'Bias Notes', type: 'text' },
          { name: 'drift_score', label: 'Observed Drift Score' },
          { name: 'deployment_mode', required: true, label: 'Deployment Mode' },
          { name: 'state', required: true, label: 'State' }
        ]
      },
      {
        title: 'Model Card & Approval (system)',
        fields: [
          { name: 'model_card', label: 'Model Card (purpose, limits, ethics)', type: 'text' },
          { name: 'approved_by', readonly: true, label: 'Approved By' },
          { name: 'deployed_at', readonly: true, label: 'Deployed At' }
        ]
      }
    ]
  },

  'M26-form-gate': {
    kind: 'model_form',
    model: 'fix.ml.evaluation.gate',
    title: 'Evaluation Gate',
    back: 'M26-registry',
    status: { field: 'result', labels: { passed: 'Passed', failed: 'Failed' } },
    sections: [
      {
        title: 'Gate Result',
        note: 'One recorded gate per evaluation: accuracy, latency budget, bias, explainability or safety. A failed gate is evidence, not an error — it blocks promotion.',
        fields: [
          { name: 'version_id', required: true, label: 'Model Version' },
          { name: 'gate', required: true, label: 'Gate' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'notes', label: 'Notes' }
        ]
      },
      {
        title: 'Reviewer (system)',
        fields: [
          { name: 'checked_by', readonly: true, label: 'Checked By' },
          { name: 'checked_at', readonly: true, label: 'Checked At' }
        ]
      }
    ]
  },

  'M26-form-guardrail': {
    kind: 'model_form',
    model: 'fix.ml.guardrail',
    title: 'Guard-Rail Config',
    back: 'M26-governance',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    sections: [
      {
        title: 'Guard Rail',
        note: 'A guard rail acts on a model output: flag for human review, block it, or fall back to the deterministic rule (the Inference Fallback screen counts the fallback rules per model).',
        fields: [
          { name: 'name', required: true, label: 'Guard-Rail Name' },
          { name: 'model_id', label: 'Applies to Model' },
          { name: 'rule', required: true, label: 'Condition (precise)' },
          { name: 'threshold', label: 'Threshold' },
          { name: 'action', required: true, label: 'Action' },
          { name: 'active', label: 'Active' },
          { name: 'note', label: 'Note' }
        ]
      }
    ]
  },

  'M26-form-inference': {
    kind: 'model_form',
    model: 'fix.ml.inference.run',
    title: 'Run ML Model Inference',
    back: 'M26-runs',
    status: { field: 'state', labels: { draft: 'Draft', computed: 'Computed', failed: 'Failed' } },
    sections: [
      {
        title: 'Inference Input',
        note: 'Execute from the Inference Run Log (the action dispatches to the model’s real engine). Capturing the human decision here is what makes the Override Analysis measurable.',
        fields: [
          { name: 'model_id', required: true, label: 'Model' },
          { name: 'input_text', label: 'Input (free text)', type: 'text' },
          { name: 'field_order_id', label: 'Field Order (dispatch input)' },
          { name: 'suggested_value', label: 'Engine Suggestion', readonly: true },
          { name: 'final_value', label: 'Final Human Decision' },
          { name: 'overridden', label: 'Overridden' },
          { name: 'override_reason', label: 'Override Reason' }
        ]
      },
      {
        title: 'Execution (system)',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'latency_ms', readonly: true, label: 'Latency (ms)' },
          { name: 'error_note', readonly: true, label: 'Error' },
          { name: 'ran_at', readonly: true, label: 'Ran At' },
          { name: 'output_json', readonly: true, label: 'Output (JSON)', type: 'text' }
        ]
      }
    ]
  }
};

/* built-in report chips -> their computed pack (D17) */
export const REPORT_ROUTES = {
  'M26:Model Performance Pack': 'M26-rpt-performance',
  'M26:Override Analysis': 'M26-rpt-override',
  'M26:Drift Report': 'M26-rpt-drift',
  'M26:Fairness Summary': 'M26-rpt-fairness',
  'M26:Model Accuracy & Retraining Log': 'M26-accuracy'
};

export const FORM_MODELS = {
  'M26:Model Version': 'fix.ml.model.version',
  'M26:Evaluation Gate': 'fix.ml.evaluation.gate',
  'M26:Guard-Rail Config': 'fix.ml.guardrail',
  'M26:Run ML Model Inference': 'fix.ml.inference.run'
};

export const FORM_CHIPS = {
  'M26:Model Version': 'M26-form-version',
  'M26:Evaluation Gate': 'M26-form-gate',
  'M26:Guard-Rail Config': 'M26-form-guardrail',
  'M26:Run ML Model Inference': 'M26-form-inference',
  'M26:__by_model__': {
    'fix.ml.model': 'M26-form-model',
    'fix.ml.model.version': 'M26-form-version',
    'fix.ml.evaluation.gate': 'M26-form-gate',
    'fix.ml.guardrail': 'M26-form-guardrail',
    'fix.ml.inference.run': 'M26-form-inference'
  },
  'M26:__by_screen__': {
    'M26-models': 'M26-form-model',
    'M26-registry': 'M26-form-version',
    'M26-cards': 'M26-form-version',
    'M26-governance': 'M26-form-guardrail',
    'M26-runs': 'M26-form-inference'
  }
};

export const CREATE = {
  M26: { screen: 'M26-form-inference', model: 'fix.ml.inference.run', label: 'ML Inference Run' }
};
