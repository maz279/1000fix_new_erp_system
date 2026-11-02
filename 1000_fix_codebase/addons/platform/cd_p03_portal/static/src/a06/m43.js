/** @odoo-module **/
/* A06 · Supply Chain — M43 Demand Planning & Replenishment (v2 rebuild).
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 3 forms / freg 58.
 * Demand plans existed (with approve); forecasts, segmentation, safety-stock
 * policy, reviews, rebalancing, scenarios and the planned-order → PR bridge
 * are new. */

export const MODULE = {
  area: 'A06', code: 'M43', en: 'Demand Planning', title: 'M43 · Demand Planning',
  bn: 'চাহিদা পরিকল্পনা', icon: '📈',
  desc: 'History assembly, forecast models and accuracy/bias (MAPE), part segmentation, safety stock and reorder-point policy, lead-time modelling, planned orders to purchase requisitions, network rebalancing, van-stock par and what-if simulation.',
  kpis: [
    { l: 'Forecasts Pending', m: 'forecasts_pending' },
    { l: 'MAPE', m: 'mape_pct', suffix: '%' },
    { l: 'Active Policies', m: 'policies_active' },
    { l: 'Planned Orders', m: 'planned_orders' },
    { l: 'Rebalance Savings', m: 'rebalance_savings', prefix: '৳ ' },
    { l: 'Avg Service Level', m: 'service_level_avg', suffix: '%' }
  ],
  groups: [
    { en: 'Forecasting', screens: [
      { id: 'M43-history', en: 'History Assembly', bn: 'ইতিহাস সংকলন', t: 'g' },
      { id: 'M43-models', en: 'Model Orchestration', bn: 'মডেল অর্কেস্ট্রেশন', t: 'g' },
      { id: 'M43-accuracy', en: 'Accuracy & Bias (MAPE)', bn: 'নির্ভুলতা ও বায়াস', t: 'g' }
    ]},
    { en: 'Policies', screens: [
      { id: 'M43-segments', en: 'Part Segmentation', bn: 'পার্ট সেগমেন্টেশন', t: 'g' },
      { id: 'M43-safety', en: 'Safety Stock & ROP', bn: 'সেফটি স্টক ও আরওপি', t: 'g' },
      { id: 'M43-leadtime', en: 'Lead-Time Modelling', bn: 'লিড-টাইম মডেলিং', t: 'g' }
    ]},
    { en: 'Execution', screens: [
      { id: 'M43-planned', en: 'Planned Orders → PR', bn: 'পরিকল্পিত অর্ডার', t: 'g' },
      { id: 'M43-reviews', en: 'Review Cycles', bn: 'পর্যালোচনা চক্র', t: 'g' },
      { id: 'M43-rebalance', en: 'Network Rebalancing', bn: 'নেটওয়ার্ক রিব্যালান্স', t: 'g' },
      { id: 'M43-vanpar', en: 'Van-Stock Par Calculation', bn: 'ভ্যান পার', t: 'g' }
    ]},
    { en: 'Simulation', screens: [
      { id: 'M43-whatif', en: 'What-If Simulation', bn: 'হোয়াট-ইফ সিমুলেশন', t: 'g' }
    ]}
  ],
  reports: ['Forecast Accuracy by Class', 'Stockout Root Causes', 'Excess & Obsolescence Exposure', 'Rebalancing Savings', 'New-Part Introduction'],
  forms: ['Review Cycle', 'Policy Assignment', 'Rebalance Proposal'],
  cross: ['M26 forecast models', 'M16 planned orders', 'M15 stock positions', 'M37 lifecycle states'],
  freg: { src: 58, sub: [
    ['1', 'History & Cleansing', 7], ['2', 'Segmentation', 6],
    ['3', 'Forecast Orchestration', 8], ['4', 'Accuracy Tracking', 6],
    ['5', 'Safety Stock & ROP', 9], ['6', 'Lead-Time', 5],
    ['7', 'Planned Orders', 6], ['8', 'Multi-Echelon Rebalancing', 7],
    ['9', 'What-If', 4]
  ] }
};

export const SCREENS = {
  'M43-history': { kind: 'table_report', module: 'M43', report: 'history_assembly', title: 'History Assembly', period: false },
  'M43-models': { kind: 'model_list', model: 'fix.demand.forecast', stateField: 'state',
    cols: ['name', 'product_id', 'period', 'forecast_qty', 'method', 'confidence_pct', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_publish', l: 'Publish' }
    ] },
  'M43-accuracy': { kind: 'table_report', module: 'M43', report: 'accuracy_bias', title: 'Accuracy & Bias (MAPE)', period: false },
  'M43-segments': { kind: 'model_list', model: 'fix.demand.segment',
    cols: ['product_id', 'abc_class', 'xyz_class', 'criticality', 'assigned_on', 'state'] },
  'M43-safety': { kind: 'model_list', model: 'fix.demand.policy', stateField: 'state',
    cols: ['product_id', 'avg_daily_demand', 'demand_stddev', 'lead_time_days', 'service_level_pct', 'safety_stock', 'reorder_point', 'state'],
    actions: [{ m: 'action_pause', l: 'Pause Policy' }] },
  'M43-leadtime': { kind: 'table_report', module: 'M43', report: 'lead_time', title: 'Lead-Time Modelling', period: false },
  'M43-planned': { kind: 'model_list', model: 'fix.demand.plan', stateField: 'state',
    cols: ['name', 'product_id', 'period_start', 'forecast_quantity', 'current_stock', 'recommended_order', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve Plan' },
      { m: 'action_generate_pr', l: 'Generate PR' }
    ] },
  'M43-reviews': { kind: 'model_list', model: 'fix.demand.review', stateField: 'state',
    cols: ['name', 'period', 'owner_id', 'due_on', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete Review' }] },
  'M43-rebalance': { kind: 'model_list', model: 'fix.demand.rebalance', stateField: 'state',
    cols: ['name', 'product_id', 'source_branch', 'target_branch', 'qty', 'savings', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M43-vanpar': { kind: 'table_report', module: 'M43', report: 'van_par', title: 'Van-Stock Par Calculation', period: false },
  'M43-whatif': { kind: 'model_list', model: 'fix.demand.scenario', stateField: 'state',
    cols: ['name', 'product_id', 'demand_adjust_pct', 'lead_time_delta_days', 'base_reorder_point', 'projected_reorder_point', 'state'],
    actions: [{ m: 'action_run', l: 'Run Scenario' }] },

  /* Report chips -> their own computed pack */
  'M43-rpt-class': { kind: 'table_report', module: 'M43', report: 'accuracy_by_class', title: 'Forecast Accuracy by Class', period: false },
  'M43-rpt-stockout': { kind: 'table_report', module: 'M43', report: 'stockout_causes', title: 'Stockout Root Causes', period: false },
  'M43-rpt-excess': { kind: 'table_report', module: 'M43', report: 'excess_obsolescence', title: 'Excess & Obsolescence Exposure', period: false },
  'M43-rpt-rebalance': { kind: 'table_report', module: 'M43', report: 'rebalancing_savings', title: 'Rebalancing Savings', period: false },
  'M43-rpt-newpart': { kind: 'table_report', module: 'M43', report: 'new_part_intro', title: 'New-Part Introduction', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M43-form-forecast': {
    kind: 'model_form',
    model: 'fix.demand.forecast',
    title: 'Demand Forecast',
    back: 'M43-models',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', published: 'Published' } },
    sections: [
      { title: 'Forecast', note: 'Approve a draft with a positive quantity; publish an approved forecast. Variance and error are computed from the recorded actual.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'forecast_qty', label: 'Forecast Qty' },
          { name: 'actual_qty', label: 'Actual Qty' },
          { name: 'method', required: true, label: 'Method' },
          { name: 'source', required: true, label: 'Source' },
          { name: 'confidence_pct', label: 'Confidence %' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M43-form-segment': {
    kind: 'model_form',
    model: 'fix.demand.segment',
    title: 'Part Segmentation',
    back: 'M43-segments',
    status: { field: 'state', labels: { active: 'Active', archived: 'Archived' } },
    sections: [
      { title: 'Segment', note: 'One segmentation row per product; ABC is value, XYZ is demand stability, criticality is the planning importance.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'abc_class', required: true, label: 'ABC' },
          { name: 'xyz_class', required: true, label: 'XYZ' },
          { name: 'criticality', required: true, label: 'Criticality' },
          { name: 'assigned_on', required: true, label: 'Assigned On' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M43-form-policy': {
    kind: 'model_form',
    model: 'fix.demand.policy',
    title: 'Policy Assignment',
    back: 'M43-policy',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused' } },
    sections: [
      { title: 'Policy', note: 'Safety stock = z × σ × √lead time; ROP = avg daily × lead time + safety stock. Both are computed, not typed.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'avg_daily_demand', label: 'Avg Daily Demand' },
          { name: 'demand_stddev', label: 'Demand Std Dev' },
          { name: 'lead_time_days', label: 'Lead Time (days)' },
          { name: 'service_level_pct', required: true, label: 'Service Level' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M43-form-review': {
    kind: 'model_form',
    model: 'fix.demand.review',
    title: 'Review Cycle',
    back: 'M43-planned',
    status: { field: 'state', labels: { scheduled: 'Scheduled', done: 'Done' } },
    sections: [
      { title: 'Review', fields: [
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'owner_id', label: 'Owner' },
          { name: 'due_on', required: true, label: 'Due On' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M43-form-rebalance': {
    kind: 'model_form',
    model: 'fix.demand.rebalance',
    title: 'Rebalance Proposal',
    back: 'M43-rebalance',
    status: { field: 'state', labels: {
      proposed: 'Proposed', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Proposal', note: 'Savings = qty × unit cost × 10% (the declared avoided-buy assumption).',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'source_branch', required: true, label: 'From Branch' },
          { name: 'target_branch', required: true, label: 'To Branch' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'unit_cost', label: 'Unit Cost' },
          { name: 'proposed_on', required: true, label: 'Proposed On' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M43-form-scenario': {
    kind: 'model_form',
    model: 'fix.demand.scenario',
    title: 'What-If Scenario',
    back: 'M43-whatif',
    status: { field: 'state', labels: { draft: 'Draft', run: 'Run' } },
    sections: [
      { title: 'Scenario', note: 'The projected ROP is the base ROP scaled by the demand adjustment; the lead-time delta is recorded for review.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'demand_adjust_pct', label: 'Demand Adjustment %' },
          { name: 'lead_time_delta_days', label: 'Lead Time Delta (days)' },
          { name: 'base_reorder_point', label: 'Base ROP' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M43:Forecast Accuracy by Class': 'M43-rpt-class',
  'M43:Stockout Root Causes': 'M43-rpt-stockout',
  'M43:Excess & Obsolescence Exposure': 'M43-rpt-excess',
  'M43:Rebalancing Savings': 'M43-rpt-rebalance',
  'M43:New-Part Introduction': 'M43-rpt-newpart'
};

export const FORM_MODELS = {
  'M43:Review Cycle': 'fix.demand.review',
  'M43:Policy Assignment': 'fix.demand.policy',
  'M43:Rebalance Proposal': 'fix.demand.rebalance'
};

export const FORM_CHIPS = {
  'M43:Review Cycle': 'M43-form-review',
  'M43:Policy Assignment': 'M43-form-policy',
  'M43:Rebalance Proposal': 'M43-form-rebalance',
  'M43:__by_model__': {
    'fix.demand.forecast': 'M43-form-forecast',
    'fix.demand.segment': 'M43-form-segment',
    'fix.demand.policy': 'M43-form-policy',
    'fix.demand.review': 'M43-form-review',
    'fix.demand.rebalance': 'M43-form-rebalance',
    'fix.demand.scenario': 'M43-form-scenario'
  },
  'M43:__by_screen__': {
    'M43-models': 'M43-form-forecast',
    'M43-segments': 'M43-form-segment',
    'M43-safety': 'M43-form-policy',
    'M43-planned': 'M43-form-review',
    'M43-reviews': 'M43-form-review',
    'M43-rebalance': 'M43-form-rebalance',
    'M43-whatif': 'M43-form-scenario'
  }
};

export const CREATE = {
  M43: { screen: 'M43-form-policy', model: 'fix.demand.policy', label: 'Policy Assignment' }
};
