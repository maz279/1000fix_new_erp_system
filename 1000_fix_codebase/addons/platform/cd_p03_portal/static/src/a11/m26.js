/** @odoo-module **/
/* A11 · Insights & Intelligence — M26 AI/ML Services (v2 re-audit).
 * True counts in this file: 5 groups (the registry's four first — Portfolio,
 * Operations, Governance, Generative — then the Evidence Registers the capture
 * audits added), 20 navigable screens + 6 computed report screens in SCREENS,
 * 6 report chips (the registry's 4 + the accuracy log + the portfolio summary),
 * 15 forms, freg 58 functions in 7 sub-modules. The registry contract names 4
 * groups / 10 screens / 4 reports / 3 forms; the extras below are evidence
 * surfaces it does not name, not a claim against it.
 * The model registry and inference engines are real (fix.ml.*), governance
 * records are real, and generative/OCR surfaces declare their true status.
 *
 * Capture audit 2026-11-14 - what each sub-module page captures:
 *   1 Portfolio & Governance  + New ML Model (with the spec's portfolio
 *                             declaration); AI Risk, Guard-Rail chips
 *   2 Training Pipelines      + New Model Version (it could not save: the
 *                             form posted `state` and the lifecycle guard
 *                             refused every create and every edit)
 *   3 Evaluation Gates        + New Evaluation Gate, now with its own log
 *   4 Deployment & Monitoring + Record Drift Observation; Record Fallback
 *                             Test (had no capture at all)
 *   5 Explainability          + Write Model Card (it offered a new version);
 *                             Record Human Decision (the override capture
 *                             was refused on every computed run)
 *   6 GenAI & RAG             + Record AI Risk, generative (it offered a
 *                             deterministic model entry: no GenAI kind exists)
 *   7 Bengali NLP & OCR       + Classify Fault Text (any model before)
 *
 * Capture audit, second pass (2026-11-19) - read against the spec's
 * lifecycle (§8.1) and owned entities (§10.1), four pages still had nowhere
 * to record what is decided or measured there:
 *   2 Training Pipelines      + Record Training Run (FR-AIM-002/003: a version
 *                             named no reproducible run); Model Version chip
 *                             now links the run
 *   3 Evaluation Gates        Data-Sufficiency Gate (FR-AIM-006, BRU-AIM-12),
 *                             Bias Test (FR-AIM-042): the bias status was
 *                             typed by the registrant, it now follows the test
 *   4 Deployment & Monitoring Performance Observation (FR-AIM-008): a floor
 *                             breach auto-demotes when a prior champion exists
 *   5 Explainability          an override without a reason is refused
 *   7 Bengali NLP & OCR       Record Human Decision (the confirmed fault)
 * Retire now records the consumers' confirmation (FR-AIM-010). */

export const MODULE = {
  area: 'A11', code: 'M26', en: 'AI/ML Services (14 models)', title: 'M26 · AI/ML Services (14 models)',
  bn: 'এআই/এমএল সেবা', icon: '🧠',
  desc: 'Dispatch scoring, Bengali fault classification, predictive maintenance, trade-in valuation — plus model governance and honest GenAI/OCR status.',
  kpis: [
    { l: 'Auto-Assign Rate', m: 'auto_assign_rate', src: false, suffix: '%' },
    { l: 'Demand MAPE', m: 'demand_mape', src: false, suffix: '%' },
    { l: 'Fault Classification F1', m: 'fault_f1', src: false },
    { l: 'Churn Model AUC', m: 'churn_auc', src: false },
    { l: 'Override Rate', m: 'override_rate', suffix: '%' },
    { l: 'Drift Alerts', m: 'drift_alerts' },
    { l: 'Models Live', m: 'models_live' },
    { l: 'Inferences (7d)', m: 'runs_7d' }
  ],
  groups: [
    /* The registry's four groups, verbatim, first (A2-F13/registry contract). */
    { en: 'Portfolio', screens: [
      { id: 'M26-models', en: 'Model Portfolio (14)', bn: 'মডেল পোর্টফোলিও', t: 'g' },
      { id: 'M26-registry', en: 'Model Registry', bn: 'মডেল রেজিস্ট্রি', t: 'g' }
    ]},
    { en: 'Operations', screens: [
      { id: 'M26-deploy', en: 'Deployment Patterns', bn: 'স্থাপন পদ্ধতি', t: 'g' },
      { id: 'M26-monitor', en: 'Production Monitoring', bn: 'উৎপাদন পর্যবেক্ষণ', t: 'r' },
      { id: 'M26-fallback', en: 'Inference Fallback', bn: 'ফলব্যাক', t: 'r' }
    ]},
    { en: 'Governance', screens: [
      { id: 'M26-governance', en: 'Guard Rails & HITL', bn: 'গার্ডরেল', t: 'g' },
      { id: 'M26-bias', en: 'Bias Testing', bn: 'পক্ষপাত পরীক্ষা', t: 'r' },
      { id: 'M26-cards', en: 'Model Cards', bn: 'মডেল কার্ড', t: 'g' }
    ]},
    { en: 'Generative', screens: [
      { id: 'M26-genai', en: 'Self-Hosted GenAI + RAG', bn: 'জেনএআই', t: 'r' },
      { id: 'M26-ocr', en: 'OCR & Bengali NLP', bn: 'ওসিআর', t: 'r' }
    ]},
    /* Evidence registers added by the capture audits (2026-11-14/19) — after
     * the registry's screens, never instead of them. */
    { en: 'Evidence Registers', screens: [
      { id: 'M26-training', en: 'Training Runs', bn: 'ট্রেনিং রান', t: 'g' },
      { id: 'M26-runs', en: 'Inference Run Log', bn: 'ইনফারেন্স রান লগ', t: 'g' },
      { id: 'M26-ai', en: 'Predictive Failure Predictions', bn: 'প্রেডিক্টিভ ফেইলিউর', t: 'g' },
      { id: 'M26-risks', en: 'AI Risk Register', bn: 'এআই ঝুঁকি রেজিস্টার', t: 'g' },
      { id: 'M26-drift-log', en: 'Drift Observations', bn: 'ড্রিফট পর্যবেক্ষণ', t: 'g' },
      { id: 'M26-performance', en: 'Production Performance', bn: 'প্রোডাকশন পারফরম্যান্স', t: 'g' },
      { id: 'M26-fallback-tests', en: 'Fallback Tests', bn: 'ফলব্যাক পরীক্ষা', t: 'g' },
      { id: 'M26-gates', en: 'Evaluation Gate Log', bn: 'মূল্যায়ন গেট', t: 'g' },
      { id: 'M26-sufficiency', en: 'Data-Sufficiency Gates', bn: 'ডেটা পর্যাপ্ততা গেট', t: 'g' },
      { id: 'M26-bias-tests', en: 'Bias Tests', bn: 'বায়াস পরীক্ষা', t: 'g' }
    ]}
  ],
  reports: ['Model Performance Pack', 'Override Analysis', 'Drift Report', 'Fairness Summary', 'Model Accuracy & Retraining Log', 'Portfolio Summary'],
  forms: ['ML Model', 'Model Version', 'Evaluation Gate', 'Guard-Rail Config', 'AI Risk', 'Drift Observation', 'Fallback Test',
    'Model Card', 'Record Human Decision', 'Classify Fault Text', 'Run ML Model Inference',
    'Training Run', 'Data-Sufficiency Gate', 'Bias Test', 'Performance Observation'],
  /* Registry verbatim (A2-F13): the old list named M15 Parts, which appears
   * nowhere in the contract, and omitted M43/M32. */
  cross: ['M02 dispatch scoring', 'M43 demand forecasts', 'M48 predictive failure', 'M32 conversational AI'],
  freg: { src: 58, sub: [
    ['1', 'Portfolio & Governance', 10, { model: 'fix.ml.model', cols: ['code', 'name', 'kind', 'consumer_modules', 'risk_class', 'owner_id', 'review_date', 'status'],
      screens: ['M26-models', 'M26-risks', 'M26-governance'], reports: ['Model Performance Pack'],
      forms: ['ML Model', 'AI Risk', 'Guard-Rail Config'], create: 'M26-form-model' }],
    ['2', 'Training Pipelines', 8, { model: 'fix.ml.training.run', cols: ['model_id', 'code_version', 'data_snapshot_ref', 'outcome', 'ended_at', 'trained_by'],
      screens: ['M26-training', 'M26-registry'], reports: ['Model Accuracy & Retraining Log'], forms: ['Training Run', 'Model Version'], create: 'M26-form-training' }],
    ['3', 'Evaluation Gates', 7, { model: 'fix.ml.evaluation.gate', cols: ['version_id', 'gate', 'result', 'checked_by', 'checked_at'],
      screens: ['M26-gates', 'M26-sufficiency', 'M26-bias-tests', 'M26-bias', 'M26-registry'], reports: ['Fairness Summary'],
      forms: ['Evaluation Gate', 'Data-Sufficiency Gate', 'Bias Test'], create: 'M26-form-gate' }],
    ['4', 'Deployment & Monitoring', 11, { model: 'fix.ml.model.version', cols: ['model_id', 'version', 'deployment_mode', 'deployed_at', 'drift_score', 'state'],
      screens: ['M26-deploy', 'M26-monitor', 'M26-performance', 'M26-drift-log', 'M26-fallback', 'M26-fallback-tests'], reports: ['Drift Report', 'Model Performance Pack'],
      forms: ['Drift Observation', 'Performance Observation', 'Fallback Test'], create: 'M26-form-drift', domain: [['deployment_mode', '!=', 'none']] }],
    ['5', 'Explainability', 5, { model: 'fix.ml.model.version', cols: ['model_id', 'version', 'model_card', 'bias_status', 'approved_by'],
      screens: ['M26-cards', 'M26-runs'], reports: ['Override Analysis'], forms: ['Model Card', 'Record Human Decision'], create: 'M26-form-card' }],
    ['6', 'GenAI & RAG', 9, { model: 'fix.ml.ai.risk', cols: ['name', 'likelihood', 'impact', 'control_ref', 'owner_id', 'review_date', 'state'],
      screens: ['M26-genai', 'M26-risks'], reports: [], forms: ['AI Risk'], create: 'M26-form-risk', domain: [['category', '=', 'generative']] }],
    ['7', 'Bengali NLP & OCR', 8, { model: 'fix.ml.inference.run', cols: ['model_code', 'input_text', 'state', 'suggested_value', 'latency_ms', 'ran_at'],
      screens: ['M26-ocr', 'M26-runs'], reports: [], forms: ['Classify Fault Text', 'Record Human Decision', 'Run ML Model Inference'], create: 'M26-form-nlp',
      domain: [['model_id.kind', '=', 'fault_classifier']] }]
  ] }
};

/* FR-AIM-010 / AUT-AIM-22: retirement records who confirmed the fallback as
 * the consumers' standing path (refused without it). */
const RETIRE = { m: 'action_retire', l: 'Retire',
  asks: [{ label: 'Who confirmed the fallback is now the consumers’ standing path?', kwarg: 'confirmation' }] };

export const SCREENS = {
  /* Portfolio */
  'M26-models': { kind: 'model_list', model: 'fix.ml.model',
    cols: ['code', 'name', 'kind', 'implementation', 'status', 'consumer_modules', 'risk_class', 'owner_id', 'review_date', 'run_count', 'last_run_at'],
    /* A2-F01/A2-F08: the '(14 models)' title is an owner decision, so the
     * honest measured line lives one click away, computed — the shared grid
     * template has no note slot of its own. */
    links: [{ s: 'M26-rpt-portfolio', l: 'Portfolio Summary' }] },
  'M26-registry': { kind: 'model_list', model: 'fix.ml.model.version', stateField: 'state',
    cols: ['model_id', 'version', 'state', 'deployment_mode', 'bias_status', 'drift_score', 'approved_by'],
    /* state moves only through these (the deploy itself lands from the Model
     * Owner's inbox once the promotion request is approved) */
    actions: [
      { m: 'action_evaluate', l: 'Mark Evaluated' },
      { m: 'action_request_promotion', l: 'Request Promotion', asks: [{ label: 'Why should this version serve?', kwarg: 'justification' }] },
      RETIRE
    ] },
  'M26-training': { kind: 'model_list', model: 'fix.ml.training.run', stateField: 'outcome', create: true,
    cols: ['model_id', 'code_version', 'data_snapshot_ref', 'environment_ref', 'started_at', 'ended_at', 'outcome', 'trained_by'],
    empty: 'No training run is recorded yet. + New records one with everything needed to reproduce it.' },
  'M26-risks': { kind: 'model_list', model: 'fix.ml.ai.risk', stateField: 'state',
    cols: ['name', 'model_id', 'category', 'likelihood', 'impact', 'owner_id', 'review_date', 'state'],
    empty: 'No AI risk is recorded yet. + New AI Risk records one, by model or estate-wide.' },

  /* Operations */
  'M26-deploy': { kind: 'model_list', model: 'fix.ml.model.version', stateField: 'deployment_mode', create: false,
    domain: [['deployment_mode', '!=', 'none']],
    cols: ['model_id', 'version', 'deployment_mode', 'deployed_at', 'drift_score', 'state'],
    actions: [RETIRE] },
  'M26-monitor': { kind: 'table_report', module: 'M26', report: 'production_monitoring', title: 'Production Monitoring', period: false },
  'M26-drift-log': { kind: 'model_list', model: 'fix.ml.drift.observation', stateField: 'breached',
    cols: ['version_id', 'feature_name', 'psi', 'ks_statistic', 'threshold', 'breached', 'observed_at', 'recorded_by'],
    empty: 'No drift observation is recorded yet. + New records one from a monitoring run on a deployed version.' },
  'M26-performance': { kind: 'model_list', model: 'fix.ml.performance.observation', stateField: 'action_taken', create: true,
    cols: ['version_id', 'metric_name', 'value', 'target', 'floor', 'labelled_sample_size', 'period_end', 'breached', 'action_taken', 'recorded_by'],
    empty: 'No production performance is recorded yet. A floor breach demotes the version (BRU-AIM-19).' },
  'M26-fallback': { kind: 'table_report', module: 'M26', report: 'fallback_status', title: 'Inference Fallback', period: false },
  'M26-fallback-tests': { kind: 'model_list', model: 'fix.ml.fallback.test', stateField: 'outcome',
    cols: ['model_id', 'consumer_module', 'method', 'outcome', 'incidents_raised', 'tested_at', 'tested_by'],
    empty: 'No fallback test is recorded yet. Every consumer needs a tested fallback (BRU-AIM-06).' },

  /* Governance */
  'M26-governance': { kind: 'model_list', model: 'fix.ml.guardrail', stateField: 'active',
    cols: ['name', 'model_id', 'rule', 'action', 'active'] },
  'M26-gates': { kind: 'model_list', model: 'fix.ml.evaluation.gate', stateField: 'result',
    cols: ['version_id', 'gate', 'result', 'checked_by', 'checked_at', 'notes'],
    empty: 'No gate is recorded yet. A reviewer who did not register the version records each gate.' },
  'M26-sufficiency': { kind: 'model_list', model: 'fix.ml.data.sufficiency', stateField: 'result', create: true,
    cols: ['model_id', 'required_history_months', 'observed_history_months', 'required_volume', 'observed_volume', 'result', 'deferred_until', 'evaluated_by'],
    empty: 'No data-sufficiency gate is recorded yet. A model is not promoted without one that reads Met (BRU-AIM-12).' },
  'M26-bias-tests': { kind: 'model_list', model: 'fix.ml.bias.test', stateField: 'assessment', create: true,
    cols: ['version_id', 'segments_tested', 'max_disparity', 'assessment', 'tested_at', 'next_due', 'documented_by'],
    empty: 'No bias test is recorded yet. The version bias status follows the newest test.' },
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
    cols: ['model_code', 'input_text', 'field_order_id', 'state', 'suggested_value', 'final_value', 'latency_ms', 'ran_at', 'ran_by'],
    actions: [{ m: 'action_execute', l: 'Execute Engine' }] },
  'M26-accuracy': { kind: 'table_report', module: 'M26', report: 'model_accuracy_retraining', title: 'Model Accuracy & Retraining Log', period: false },

  /* Report packs (the four registry chips) */
  'M26-rpt-portfolio': { kind: 'table_report', module: 'M26', report: 'model_portfolio', title: 'Portfolio Summary', period: false },
  'M26-rpt-performance': { kind: 'table_report', module: 'M26', report: 'model_performance_pack', title: 'Model Performance Pack', period: false },
  'M26-rpt-override': { kind: 'table_report', module: 'M26', report: 'override_analysis', title: 'Override Analysis', period: false },
  'M26-rpt-drift': { kind: 'table_report', module: 'M26', report: 'drift_report', title: 'Drift Report', period: false },
  'M26-rpt-fairness': { kind: 'table_report', module: 'M26', report: 'fairness_summary', title: 'Fairness Summary', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M26-form-model': {
    kind: 'model_form',
    model: 'fix.ml.model',
    title: 'ML Model',
    back: 'M26-models',
    status: { field: 'status', labels: { production: 'Production', planned: 'Planned' } },
    tabs: [
      { id: 'engine', label: 'Engine', bn: 'ইঞ্জিন', icon: '⚙' },
      { id: 'portfolio', label: 'Portfolio Declaration', bn: 'পোর্টফোলিও ঘোষণা', icon: '🎯' }
    ],
    sections: [
      { tab: 'engine', title: 'Model', note: 'One catalogue entry per REAL engine. Implementation states honestly whether a live engine exists or the entry is a declared seam.',
        fields: [
          { name: 'code', required: true, label: 'Model Code' },
          { name: 'name', required: true, label: 'Model Name' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'implementation', required: true, label: 'Implementation' },
          { name: 'status', required: true, label: 'Status' },
          { name: 'owning_module', label: 'Owning Module' },
          { name: 'notes', type: 'text', label: 'Engine Notes' }
        ] },
      { tab: 'portfolio', title: 'Portfolio Declaration',
        note: 'A model without a named consumer, a stated target and a defined fallback is not deployed (BRU-AIM-11). Review it at least once a year.',
        fields: [
          { name: 'purpose', type: 'text', label: 'Purpose (the decision it informs)' },
          { name: 'consumer_modules', label: 'Named Consumer(s)' },
          { name: 'accuracy_target', label: 'Accuracy Target' },
          { name: 'fallback_definition', type: 'text', label: 'Defined Fallback' },
          { name: 'risk_class', label: 'Risk Class' },
          { name: 'owner_id', label: 'Model Owner' },
          { name: 'review_date', label: 'Next Review' },
          { name: 'min_history_months', label: 'Minimum History (months) - data sufficiency' },
          { name: 'min_volume', label: 'Minimum Volume (labelled records) - data sufficiency' }
        ] }
    ]
  },

  'M26-form-version': {
    kind: 'model_form',
    model: 'fix.ml.model.version',
    title: 'Model Version',
    back: 'M26-registry',
    status: { field: 'state', labels: { draft: 'Draft', evaluated: 'Evaluated', approved: 'Approved', deployed: 'Deployed', demoted: 'Auto-Demoted', retired: 'Retired' } },
    sections: [
      {
        title: 'Version & Artifact',
        note: 'One version of a registered model. It is registered as a draft; Mark Evaluated, Request Promotion and Retire on the Model Registry move it. The artifact reference must point at a real registry object.',
        fields: [
          { name: 'model_id', required: true, label: 'Registered Model' },
          { name: 'version', required: true, label: 'Version' },
          { name: 'training_run_id', label: 'Training Run (that produced it)', domain: [['outcome', '=', 'succeeded']] },
          { name: 'artifact_ref', label: 'Artifact Reference' },
          { name: 'training_dataset', label: 'Training Dataset' }
        ]
      },
      {
        title: 'Evaluation & Release',
        note: 'Metrics are keyed in from the evaluation run, never estimated. The drift score follows the drift observations recorded on Deployment & Monitoring.',
        fields: [
          { name: 'metrics_json', label: 'Metrics (JSON)', type: 'text' },
          { name: 'bias_status', readonly: true, label: 'Bias Test Status (follows the newest Bias Test)' },
          { name: 'bias_notes', label: 'Bias Notes', type: 'text' },
          { name: 'deployment_mode', required: true, label: 'Deployment Mode' },
          { name: 'drift_score', readonly: true, label: 'Observed Drift Score' },
          { name: 'state', readonly: true, label: 'State' }
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
    back: 'M26-gates',
    status: { field: 'result', labels: { pending: 'Pending', passed: 'Passed', failed: 'Failed' } },
    sections: [
      {
        title: 'Gate Result',
        note: 'One recorded gate per evaluation: accuracy, latency budget, bias, explainability or safety. The reviewer must not be the person who registered the version. A recorded gate is evidence: it cannot be edited - record a new one. A DEPLOYED version may be re-evaluated (periodic review): the gate is then evidence only and does not change the version state; a failed gate on a deployed version alerts the model owner.',
        fields: [
          /* D-L15: deployed versions were excluded, so no live version (all six
           * are deployed) could ever be re-evaluated. */
          { name: 'version_id', required: true, label: 'Model Version', domain: [['state', 'in', ['draft', 'evaluated', 'deployed']]] },
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
          /* A2-F14(b): derived from the rule on save — one enforced number. */
          { name: 'threshold', readonly: true, label: 'Threshold (derived from the condition)' },
          { name: 'action', required: true, label: 'Action' },
          { name: 'active', label: 'Active' },
          { name: 'note', label: 'Note' }
        ]
      }
    ]
  },

  /* AI risk register (spec §10.1): by model, or estate-wide - a generative
   * roll-out carries risks before any generative model exists. */
  'M26-form-risk': {
    kind: 'model_form',
    model: 'fix.ml.ai.risk',
    title: 'AI Risk',
    back: 'M26-risks',
    status: { field: 'state', labels: { open: 'Open', treated: 'Treated', accepted: 'Accepted', closed: 'Closed' } },
    sections: [
      { title: 'Risk', note: 'Leave the model empty for an estate-wide risk. Generative risks (customer data leaving the estate, prompt injection, ungrounded answers, unlabelled AI content) are listed on GenAI & RAG.',
        fields: [
          { name: 'name', required: true, label: 'Risk' },
          { name: 'model_id', label: 'Model (empty = estate-wide)' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'likelihood', required: true, label: 'Likelihood' },
          { name: 'impact', required: true, label: 'Impact' }
        ] },
      { title: 'Treatment & Review', note: 'Reviewed at least annually and on every material version change (BRU-AIM-26).',
        fields: [
          { name: 'treatment', type: 'text', label: 'Treatment' },
          { name: 'control_ref', label: 'Control Reference (e.g. BRU-AIM-10)' },
          { name: 'owner_id', required: true, label: 'Risk Owner' },
          { name: 'review_date', required: true, label: 'Next Review' },
          { name: 'state', required: true, label: 'Status' }
        ] }
    ]
  },

  /* A monitoring observation on a SERVING version: PSI and KS per feature.
   * Breached is derived; the version's drift score follows the newest day. */
  'M26-form-drift': {
    kind: 'model_form',
    model: 'fix.ml.drift.observation',
    title: 'Drift Observation',
    newLabel: 'Record Drift Observation',
    back: 'M26-drift-log',
    status: { field: 'breached', labels: { true: 'Breached', false: 'Within threshold' } },
    sections: [
      { title: 'Observation', note: 'From the monitoring run, per served feature. Retraining is triggered by a PSI breach together with an evaluation drop, not by drift alone. An observation is evidence: it cannot be edited.',
        fields: [
          { name: 'version_id', required: true, label: 'Deployed Version', domain: [['state', '=', 'deployed']] },
          { name: 'feature_name', required: true, label: 'Feature' },
          { name: 'psi', required: true, label: 'Population Stability Index (PSI)' },
          { name: 'ks_statistic', label: 'KS Statistic (0-1)' },
          { name: 'threshold', required: true, label: 'PSI Threshold' },
          { name: 'observed_at', label: 'Observed At' },
          { name: 'note', label: 'Note' }
        ] },
      { title: 'Result (system)',
        fields: [
          { name: 'breached', readonly: true, label: 'Breached' },
          { name: 'recorded_by', readonly: true, label: 'Recorded By' }
        ] }
    ]
  },

  /* BRU-AIM-06: every consumer has a TESTED fallback. */
  'M26-form-fallback': {
    kind: 'model_form',
    model: 'fix.ml.fallback.test',
    title: 'Fallback Test',
    newLabel: 'Record Fallback Test',
    back: 'M26-fallback-tests',
    status: { field: 'outcome', labels: { passed: 'Passed', failed: 'Failed' } },
    sections: [
      { title: 'Fallback Test', note: 'Switch the model off (or simulate its failure) and watch the consuming module: model unavailability must never block a business process. A test is evidence: it cannot be edited.',
        fields: [
          { name: 'model_id', required: true, label: 'Model' },
          { name: 'consumer_module', required: true, label: 'Consuming Module' },
          { name: 'method', required: true, label: 'Method' },
          { name: 'consumer_behaviour', required: true, type: 'text', label: 'What the Consumer Did' },
          { name: 'outcome', required: true, label: 'Outcome' },
          { name: 'incidents_raised', label: 'Incidents Raised' },
          { name: 'tested_at', label: 'Tested At' }
        ] },
      { title: 'Tester (system)',
        fields: [{ name: 'tested_by', readonly: true, label: 'Tested By' }] }
    ]
  },

  /* The card of an existing version (BRU-AIM-08): picked, then written. */
  'M26-form-card': {
    kind: 'model_form',
    model: 'fix.ml.model.version',
    title: 'Model Card',
    newLabel: 'Write Model Card',
    back: 'M26-cards',
    pickRecord: {
      label: 'Step 1 of 2: choose the model version',
      note: 'Every production model has a current card: purpose, training data, intended and out-of-scope use, performance by segment, limitations, owner and review date.',
      search: 'Search version',
      choose: 'Write this card',
      cols: ['model_id', 'version', 'state', 'bias_status', 'deployment_mode'],
      domain: [['state', '!=', 'retired']],
      empty: 'No version can take a card: register a version on Training Pipelines first.'
    },
    sections: [
      { title: 'Step 2 of 2: Model Card',
        fields: [
          { name: 'model_id', readonly: true, label: 'Model' },
          { name: 'version', readonly: true, label: 'Version' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'model_card', required: true, type: 'text', label: 'Model Card (purpose, data, intended and out-of-scope use, performance by segment, limitations, owner, review date)' }
        ] }
    ]
  },

  /* The human half of the decision log on a computed run (BRU-AIM-05). */
  'M26-form-decision': {
    kind: 'model_form',
    model: 'fix.ml.inference.run',
    title: 'Record Human Decision',
    newLabel: 'Record Human Decision',
    back: 'M26-runs',
    pickRecord: {
      label: 'Step 1 of 2: choose the computed run',
      note: 'The engine suggests; a person decides. Recording what was finally decided, and why when it differs, is what makes the Override Analysis measurable.',
      search: 'Search run',
      choose: 'Record the decision',
      cols: ['model_code', 'input_text', 'suggested_value', 'final_value', 'ran_at'],
      domain: [['state', '=', 'computed']],
      empty: 'No computed run yet: execute a run on the Inference Run Log first.'
    },
    sections: [
      { title: 'Step 2 of 2: Decision', note: 'Give a reason whenever the decision differs from the engine suggestion: every override is captured with its reason and fed back into training.',
        fields: [
          { name: 'model_id', readonly: true, label: 'Model' },
          { name: 'input_text', readonly: true, type: 'text', label: 'Input' },
          { name: 'suggested_value', readonly: true, label: 'Engine Suggestion' },
          { name: 'final_value', required: true, label: 'Final Human Decision' },
          { name: 'override_reason', label: 'Override Reason' },
          { name: 'overridden', readonly: true, label: 'Overridden (derived)' }
        ] }
    ]
  },

  /* Bengali / English complaint text through the fault classifier. */
  'M26-form-nlp': {
    kind: 'model_form',
    model: 'fix.ml.inference.run',
    title: 'Classify Fault Text',
    newLabel: 'Classify Fault Text',
    back: 'M26-runs',
    status: { field: 'state', labels: { draft: 'Draft', computed: 'Computed', failed: 'Failed' } },
    sections: [
      { title: 'Complaint Text', note: 'Saved as a draft run of the fault classifier; Execute Engine on the Inference Run Log classifies it against the fault taxonomy and logs the result.',
        fields: [
          { name: 'model_id', required: true, label: 'Classifier', domain: [['kind', '=', 'fault_classifier']] },
          { name: 'input_text', required: true, type: 'text', label: 'Complaint Text (Bengali or English)' }
        ] },
      { title: 'Execution (system)',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'suggested_value', readonly: true, label: 'Engine Suggestion' },
          { name: 'output_json', readonly: true, type: 'text', label: 'Output (JSON)' }
        ] }
    ]
  },

  /* Capture audit pass 2: the run a version is trained in (T-10). */
  'M26-form-training': {
    kind: 'model_form',
    model: 'fix.ml.training.run',
    title: 'Training Run',
    newLabel: 'Record Training Run',
    back: 'M26-training',
    status: { field: 'outcome', labels: { succeeded: 'Succeeded', failed: 'Failed', abandoned: 'Abandoned' } },
    tabs: [
      { id: 'repro', label: 'Reproducibility', bn: 'পুনরুৎপাদনযোগ্যতা', icon: '🔁' },
      { id: 'result', label: 'Result', bn: 'ফলাফল', icon: '📊' }
    ],
    sections: [
      { tab: 'repro', title: 'What the run used', note: 'Everything needed to reproduce the run exactly: code version, M62 feature-store snapshot, feature versions, hyperparameters and environment. A recorded run is evidence: it cannot be edited.',
        fields: [
          { name: 'model_id', required: true, label: 'Model' },
          { name: 'code_version', required: true, label: 'Code Version (commit / tag)' },
          { name: 'data_snapshot_ref', required: true, label: 'Data Snapshot (M62, point in time)' },
          { name: 'feature_versions', required: true, type: 'text', label: 'Feature Versions' },
          { name: 'hyperparameters', required: true, type: 'text', label: 'Hyperparameters (JSON object)' },
          { name: 'environment_ref', required: true, label: 'Environment (image / lock file)' },
          { name: 'm06_data_excluded', required: true, label: 'No recovered M06 customer data in the training data (BRU-AIM-03)' }
        ] },
      { tab: 'result', title: 'Run Result', note: 'A succeeded run records its measured evaluation metrics; a failed or abandoned run says why.',
        fields: [
          { name: 'started_at', required: true, label: 'Started' },
          { name: 'ended_at', required: true, label: 'Ended' },
          { name: 'outcome', required: true, label: 'Outcome' },
          { name: 'metrics_json', type: 'text', label: 'Evaluation Metrics (JSON)' },
          { name: 'failure_note', label: 'Why it failed / was abandoned' },
          { name: 'trained_by', readonly: true, label: 'Recorded By' }
        ] }
    ]
  },

  /* FR-AIM-006 / BRU-AIM-12: the model's declared bar against the data. */
  'M26-form-sufficiency': {
    kind: 'model_form',
    model: 'fix.ml.data.sufficiency',
    title: 'Data-Sufficiency Gate',
    newLabel: 'Record Data-Sufficiency Gate',
    back: 'M26-sufficiency',
    status: { field: 'result', labels: { met: 'Met', deferred: 'Deferred' } },
    sections: [
      { title: 'Measured Data', note: 'The bar is the model’s own declaration (Portfolio Declaration: minimum history and volume) - it is copied, not typed. Unmet is deferred with a revisit date, never rejected. Promotion needs the newest gate to read Met.',
        fields: [
          { name: 'model_id', required: true, label: 'Model' },
          { name: 'source_modules', required: true, label: 'Data Source(s)' },
          { name: 'observed_history_months', required: true, label: 'History Available (months)' },
          { name: 'observed_volume', required: true, label: 'Labelled Records Available' },
          { name: 'deferred_until', label: 'Revisit On (if unmet)' },
          { name: 'prerequisite_note', type: 'text', label: 'What must exist first' }
        ] },
      { title: 'Result (system)',
        fields: [
          { name: 'required_history_months', readonly: true, label: 'Required History (months)' },
          { name: 'required_volume', readonly: true, label: 'Required Volume' },
          { name: 'result', readonly: true, label: 'Result' },
          { name: 'evaluated_by', readonly: true, label: 'Evaluated By' }
        ] }
    ]
  },

  /* FR-AIM-042 / BRU-AIM-07: fairness evidence; it sets the bias status. */
  'M26-form-bias': {
    kind: 'model_form',
    model: 'fix.ml.bias.test',
    title: 'Bias Test',
    newLabel: 'Record Bias Test',
    back: 'M26-bias-tests',
    status: { field: 'assessment', labels: { passed: 'Passed', failed: 'Failed' } },
    sections: [
      { title: 'Fairness Evidence', note: 'Documented by someone who neither registered the version nor owns the model (spec §13). The version’s bias status follows this test; a failed test blocks every promotion.',
        fields: [
          { name: 'version_id', required: true, label: 'Model Version', domain: [['state', '!=', 'retired']] },
          { name: 'segments_tested', required: true, type: 'text', label: 'Segments Tested' },
          { name: 'metric_by_segment', required: true, type: 'text', label: 'Metric by Segment' },
          { name: 'max_disparity', label: 'Largest Disparity' },
          { name: 'assessment', required: true, label: 'Assessment' },
          { name: 'notes', type: 'text', label: 'Notes' },
          { name: 'next_due', required: true, label: 'Next Test Due' }
        ] },
      { title: 'Reviewer (system)',
        fields: [{ name: 'documented_by', readonly: true, label: 'Documented By' }] }
    ]
  },

  /* FR-AIM-008 / BRU-AIM-19: production performance against its floor. */
  'M26-form-performance': {
    kind: 'model_form',
    model: 'fix.ml.performance.observation',
    title: 'Performance Observation',
    newLabel: 'Record Performance Observation',
    back: 'M26-performance',
    status: { field: 'action_taken', labels: { none: 'Within floor', demoted: 'Demoted', escalated: 'Escalated' } },
    sections: [
      { title: 'Measured Performance', note: 'On labelled outcomes for a serving version. Crossing the floor demotes the version and restores the prior champion, with no human choosing; with no prior champion it keeps serving and the breach is escalated (a model problem never blocks the business). An observation is evidence: it cannot be edited.',
        fields: [
          { name: 'version_id', required: true, label: 'Deployed Version', domain: [['state', '=', 'deployed']] },
          { name: 'period_start', required: true, label: 'Period From' },
          { name: 'period_end', required: true, label: 'Period To' },
          { name: 'metric_name', required: true, label: 'Metric' },
          { name: 'value', required: true, label: 'Measured Value' },
          { name: 'target', required: true, label: 'Target' },
          { name: 'floor', required: true, label: 'Floor (demotion line)' },
          { name: 'higher_is_better', label: 'Higher is better (off for MAPE / MAE)' },
          { name: 'labelled_sample_size', required: true, label: 'Labelled Sample Size' },
          { name: 'note', label: 'Note' }
        ] },
      { title: 'Result (system)',
        fields: [
          { name: 'breached', readonly: true, label: 'Floor Breached' },
          { name: 'action_taken', readonly: true, label: 'Action Taken' },
          { name: 'recorded_by', readonly: true, label: 'Recorded By' }
        ] }
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
          { name: 'overridden', label: 'Overridden (derived)', readonly: true },
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
  'M26:Portfolio Summary': 'M26-rpt-portfolio',
  'M26:Model Performance Pack': 'M26-rpt-performance',
  'M26:Override Analysis': 'M26-rpt-override',
  'M26:Drift Report': 'M26-rpt-drift',
  'M26:Fairness Summary': 'M26-rpt-fairness',
  'M26:Model Accuracy & Retraining Log': 'M26-accuracy'
};

export const FORM_MODELS = {
  'M26:ML Model': 'fix.ml.model',
  'M26:Model Version': 'fix.ml.model.version',
  'M26:Evaluation Gate': 'fix.ml.evaluation.gate',
  'M26:Guard-Rail Config': 'fix.ml.guardrail',
  'M26:AI Risk': 'fix.ml.ai.risk',
  'M26:Drift Observation': 'fix.ml.drift.observation',
  'M26:Fallback Test': 'fix.ml.fallback.test',
  'M26:Model Card': 'fix.ml.model.version',
  'M26:Record Human Decision': 'fix.ml.inference.run',
  'M26:Classify Fault Text': 'fix.ml.inference.run',
  'M26:Run ML Model Inference': 'fix.ml.inference.run',
  'M26:Training Run': 'fix.ml.training.run',
  'M26:Data-Sufficiency Gate': 'fix.ml.data.sufficiency',
  'M26:Bias Test': 'fix.ml.bias.test',
  'M26:Performance Observation': 'fix.ml.performance.observation'
};

export const FORM_CHIPS = {
  'M26:ML Model': 'M26-form-model',
  'M26:Model Version': 'M26-form-version',
  'M26:Evaluation Gate': 'M26-form-gate',
  'M26:Guard-Rail Config': 'M26-form-guardrail',
  'M26:AI Risk': 'M26-form-risk',
  'M26:Drift Observation': 'M26-form-drift',
  'M26:Fallback Test': 'M26-form-fallback',
  'M26:Model Card': 'M26-form-card',
  'M26:Record Human Decision': 'M26-form-decision',
  'M26:Classify Fault Text': 'M26-form-nlp',
  'M26:Run ML Model Inference': 'M26-form-inference',
  'M26:Training Run': 'M26-form-training',
  'M26:Data-Sufficiency Gate': 'M26-form-sufficiency',
  'M26:Bias Test': 'M26-form-bias',
  'M26:Performance Observation': 'M26-form-performance',
  'M26:__by_model__': {
    'fix.ml.model': 'M26-form-model',
    'fix.ml.model.version': 'M26-form-version',
    'fix.ml.evaluation.gate': 'M26-form-gate',
    'fix.ml.guardrail': 'M26-form-guardrail',
    'fix.ml.inference.run': 'M26-form-inference',
    'fix.ml.ai.risk': 'M26-form-risk',
    'fix.ml.drift.observation': 'M26-form-drift',
    'fix.ml.fallback.test': 'M26-form-fallback',
    'fix.ml.training.run': 'M26-form-training',
    'fix.ml.data.sufficiency': 'M26-form-sufficiency',
    'fix.ml.bias.test': 'M26-form-bias',
    'fix.ml.performance.observation': 'M26-form-performance'
  },
  'M26:__by_screen__': {
    'M26-models': 'M26-form-model',
    'M26-registry': 'M26-form-version',
    'M26-cards': 'M26-form-card',
    'M26-governance': 'M26-form-guardrail',
    'M26-gates': 'M26-form-gate',
    'M26-risks': 'M26-form-risk',
    'M26-drift-log': 'M26-form-drift',
    'M26-fallback-tests': 'M26-form-fallback',
    'M26-runs': 'M26-form-inference',
    'M26-training': 'M26-form-training',
    'M26-sufficiency': 'M26-form-sufficiency',
    'M26-bias-tests': 'M26-form-bias',
    'M26-performance': 'M26-form-performance'
  }
};

export const CREATE = {
  M26: { screen: 'M26-form-inference', model: 'fix.ml.inference.run', label: 'ML Inference Run' }
};
