/** @odoo-module **/
/* A06 · Supply Chain — M43 Demand Planning & Replenishment (v2 rebuild).
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 3 forms / freg 58,
 * plus the capture audit (2026-11-16): every sub-module page captures the spec
 * §10.1 record it names - history adjustments, drivers, service targets,
 * lead-time models, new-part and end-of-life plans, van par and network
 * stocking policy - each with its own list and form.
 * A06 audit (2026-11-03): the forms offer only what a planner may type. State,
 * approval stamps and every computed figure (forecast from M15 history,
 * actuals, safety stock / ROP / target, plan position, rebalance value) are
 * read-only; transitions are the declared actions, which enforce the Demand
 * Planner / Demand Plan Approver roles and segregation of duties. */

export const MODULE = {
  area: 'A06', code: 'M43', en: 'Demand Planning', title: 'M43 · Demand Planning',
  bn: 'চাহিদা পরিকল্পনা', icon: '📈',
  desc: 'History assembly, forecast models and accuracy/bias (MAPE), part segmentation, safety stock and reorder-point policy, lead-time modelling, planned orders to purchase requisitions, network rebalancing, van-stock par and what-if simulation.',
  kpis: [
    { l: 'Forecasts Pending', m: 'forecasts_pending' },
    { l: 'MAPE', m: 'mape_pct', suffix: '%' },
    { l: 'Active Policies', m: 'policies_active' },
    { l: 'Planned Orders', m: 'planned_orders' },
    { l: 'Stock Value Rebalanced', m: 'rebalance_value_moved', prefix: '৳ ' },
    { l: 'Avg Service Level', m: 'service_level_avg', suffix: '%' }
  ],
  groups: [
    { en: 'Forecasting', screens: [
      { id: 'M43-history', en: 'History Assembly', bn: 'ইতিহাস সংকলন', t: 'r' },
      { id: 'M43-adjustments', en: 'History Adjustments', bn: 'ইতিহাস সমন্বয়', t: 'g' },
      { id: 'M43-models', en: 'Model Orchestration', bn: 'মডেল অর্কেস্ট্রেশন', t: 'g' },
      { id: 'M43-drivers', en: 'Demand Drivers', bn: 'চাহিদা চালক', t: 'g' },
      { id: 'M43-accuracy', en: 'Accuracy & Bias (MAPE)', bn: 'নির্ভুলতা ও বায়াস', t: 'r' }
    ]},
    { en: 'Policies', screens: [
      { id: 'M43-segments', en: 'Part Segmentation', bn: 'পার্ট সেগমেন্টেশন', t: 'g' },
      { id: 'M43-safety', en: 'Safety Stock & ROP', bn: 'সেফটি স্টক ও আরওপি', t: 'g' },
      { id: 'M43-targets', en: 'Service-Level Targets', bn: 'সার্ভিস লেভেল লক্ষ্য', t: 'g' },
      { id: 'M43-leadtimes', en: 'Supplier Lead Times', bn: 'সরবরাহকারী লিড টাইম', t: 'g' },
      { id: 'M43-leadtime', en: 'Lead-Time Modelling', bn: 'লিড-টাইম মডেলিং', t: 'r' }
    ]},
    { en: 'Execution', screens: [
      { id: 'M43-planned', en: 'Planned Orders → PR', bn: 'পরিকল্পিত অর্ডার', t: 'g' },
      { id: 'M43-npi', en: 'New-Part Introduction', bn: 'নতুন পার্ট প্রবর্তন', t: 'g' },
      { id: 'M43-eol', en: 'End-of-Life & Last-Time Buy', bn: 'জীবনশেষ ও শেষ ক্রয়', t: 'g' },
      { id: 'M43-reviews', en: 'Review Cycles', bn: 'পর্যালোচনা চক্র', t: 'g' },
      { id: 'M43-rebalance', en: 'Network Rebalancing', bn: 'নেটওয়ার্ক রিব্যালান্স', t: 'g' },
      { id: 'M43-network', en: 'Network Stocking Policy', bn: 'নেটওয়ার্ক স্টকিং নীতি', t: 'g' },
      { id: 'M43-vanpars', en: 'Van Par Recommendations', bn: 'ভ্যান পার সুপারিশ', t: 'g' },
      { id: 'M43-vanpar', en: 'Van-Stock Par Calculation', bn: 'ভ্যান পার', t: 'r' }
    ]},
    { en: 'Simulation', screens: [
      { id: 'M43-whatif', en: 'What-If Simulation', bn: 'হোয়াট-ইফ সিমুলেশন', t: 'g' }
    ]}
  ],
  reports: ['Forecast Accuracy by Class', 'Stockout Root Causes', 'Excess & Obsolescence Exposure', 'Rebalancing Value Moved', 'New-Part Introduction'],
  forms: ['Review Cycle', 'Policy Assignment', 'Rebalance Proposal',
    'Demand Adjustment', 'Part Segmentation', 'Demand Forecast', 'Demand Driver',
    'Service-Level Target', 'Lead-Time Model', 'Demand Plan', 'New-Part Recommendation',
    'End-of-Life Plan', 'Van Par Recommendation', 'Network Stocking Policy', 'What-If Scenario'],
  cross: ['M26 forecast models', 'M16 planned orders', 'M15 stock positions', 'M37 lifecycle states'],
  freg: { src: 58, sub: [
    /* capture audit 2026-11-16: pages 1, 4 and 6 captured nothing (create:
     * false), 2, 3, 7 and 9 had a "+ New" but no chip, and the spec records of
     * pages 1, 3, 5, 6, 7 and 8 did not exist. */
    ['1', 'History & Cleansing', 7, { model: 'fix.demand.adjustment', cols: ['name', 'product_id', 'period', 'adjustment_type', 'original_qty', 'adjusted_qty', 'state'], screens: ['M43-adjustments', 'M43-history'], reports: ['Stockout Root Causes'], forms: ['Demand Adjustment'] }],
    ['2', 'Segmentation', 6, { model: 'fix.demand.segment', cols: ['product_id', 'abc_class', 'xyz_class', 'criticality', 'state'], screens: ['M43-segments'], reports: ['Excess & Obsolescence Exposure'], forms: ['Part Segmentation'] }],
    ['3', 'Forecast Orchestration', 8, { model: 'fix.demand.forecast', cols: ['name', 'product_id', 'period', 'forecast_qty', 'method'], screens: ['M43-models', 'M43-drivers', 'M43-reviews'], reports: ['Forecast Accuracy by Class'], forms: ['Demand Forecast', 'Demand Driver', 'Review Cycle'] }],
    /* accuracy is measured from M15, never typed (BRU-DPL-16): the page
     * captures the review cycle that acts on it */
    ['4', 'Accuracy Tracking', 6, { model: 'fix.demand.forecast', cols: ['product_id', 'period', 'forecast_qty', 'actual_qty', 'abs_error_pct'], screens: ['M43-accuracy', 'M43-reviews'], reports: ['Forecast Accuracy by Class'], forms: ['Review Cycle'], create: 'M43-form-review' }],
    ['5', 'Safety Stock & ROP', 9, { model: 'fix.demand.policy', cols: ['product_id', 'service_level_pct', 'safety_stock', 'reorder_point', 'target_level', 'state'], screens: ['M43-safety', 'M43-targets'], reports: ['Stockout Root Causes'], forms: ['Policy Assignment', 'Service-Level Target'] }],
    ['6', 'Lead-Time', 5, { model: 'fix.demand.lead.time', cols: ['product_id', 'vendor_id', 'quoted_days', 'mean_days', 'std_dev_days', 'p95_days', 'state'], screens: ['M43-leadtimes', 'M43-leadtime'], reports: [], forms: ['Lead-Time Model'] }],
    ['7', 'Planned Orders', 6, { model: 'fix.demand.plan', cols: ['name', 'product_id', 'forecast_quantity', 'recommended_order', 'state'], screens: ['M43-planned', 'M43-npi', 'M43-eol'], reports: ['New-Part Introduction'], forms: ['Demand Plan', 'New-Part Recommendation', 'End-of-Life Plan'] }],
    ['8', 'Multi-Echelon Rebalancing', 7, { model: 'fix.demand.rebalance', cols: ['name', 'product_id', 'source_location_id', 'target_location_id', 'qty'], screens: ['M43-rebalance', 'M43-network', 'M43-vanpars', 'M43-vanpar'], reports: ['Rebalancing Value Moved'], forms: ['Rebalance Proposal', 'Van Par Recommendation', 'Network Stocking Policy'] }],
    ['9', 'What-If', 4, { model: 'fix.demand.scenario', cols: ['name', 'product_id', 'demand_adjust_pct', 'projected_reorder_point', 'state'], screens: ['M43-whatif'], reports: ['Excess & Obsolescence Exposure'], forms: ['What-If Scenario'] }]
  ] }
};

export const SCREENS = {
  'M43-history': { kind: 'table_report', module: 'M43', report: 'history_assembly', title: 'History Assembly', period: false },
  'M43-models': { kind: 'model_list', model: 'fix.demand.forecast', stateField: 'state',
    cols: ['name', 'product_id', 'part_id', 'period', 'window_months', 'statistical_qty', 'forecast_qty', 'method', 'source', 'state'],
    actions: [
      { m: 'action_compute_forecast', l: 'Compute from History' },
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reset_draft', l: 'Re-open' },
      { m: 'action_publish', l: 'Publish' }
    ] },
  'M43-accuracy': { kind: 'table_report', module: 'M43', report: 'accuracy_bias', title: 'Accuracy & Bias (MAPE)', period: false },
  'M43-segments': { kind: 'model_list', model: 'fix.demand.segment',
    cols: ['product_id', 'part_id', 'abc_class', 'xyz_class', 'criticality', 'consumption_value', 'demand_cv', 'classified_on', 'state'],
    actions: [{ m: 'action_classify', l: 'Classify from M15 History' }] },
  'M43-safety': { kind: 'model_list', model: 'fix.demand.policy', stateField: 'state',
    cols: ['name', 'version', 'product_id', 'location_id', 'avg_daily_demand', 'demand_stddev', 'provisional_state', 'lead_time_days', 'lead_time_source', 'service_level_pct', 'safety_stock', 'reorder_point', 'target_level', 'state'],
    actions: [
      { m: 'action_refresh_from_history', l: 'Refresh from History' },
      { m: 'action_approve_provisional', l: 'Approve Provisional Demand' },
      { m: 'action_activate', l: 'Activate / Approve' },
      { m: 'action_revise', l: 'Revise (new version)' },
      { m: 'action_pause', l: 'Pause Policy' },
      { m: 'action_resume', l: 'Resume Policy' }
    ] },
  'M43-leadtime': { kind: 'table_report', module: 'M43', report: 'lead_time', title: 'Lead-Time Modelling', period: false },
  'M43-planned': { kind: 'model_list', model: 'fix.demand.plan', stateField: 'state',
    cols: ['name', 'product_id', 'location_id', 'period_start', 'forecast_quantity', 'current_stock', 'on_order_qty', 'reorder_point', 'target_level', 'recommended_order', 'approved_order_qty', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve Plan' },
      { m: 'action_generate_pr', l: 'Release PR to M16' },
      { m: 'action_reopen', l: 'Reopen (PR rejected or cancelled)', ask: 'Why the plan is reopened', kwarg: 'reason' }
    ] },
  'M43-reviews': { kind: 'model_list', model: 'fix.demand.review', stateField: 'state',
    cols: ['name', 'period', 'owner_id', 'due_on', 'completed_by_id', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete Review' }] },
  'M43-rebalance': { kind: 'model_list', model: 'fix.demand.rebalance', stateField: 'state',
    cols: ['name', 'product_id', 'source_location_id', 'target_location_id', 'qty', 'stock_value', 'transfer_cost', 'benefit_value', 'net_benefit', 'transfer_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (create M15 transfer)' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M43-vanpar': { kind: 'table_report', module: 'M43', report: 'van_par', title: 'Van-Stock Par Calculation', period: false },
  'M43-whatif': { kind: 'model_list', model: 'fix.demand.scenario', stateField: 'state',
    cols: ['name', 'product_id', 'policy_id', 'demand_adjust_pct', 'lead_time_delta_days', 'base_reorder_point', 'projected_reorder_point', 'state'],
    actions: [{ m: 'action_run', l: 'Run Scenario' }] },

  /* capture audit 2026-11-16 - the spec §10.1 records each page captures */
  'M43-adjustments': { kind: 'model_list', model: 'fix.demand.adjustment', stateField: 'state',
    cols: ['name', 'product_id', 'part_id', 'location_id', 'period', 'adjustment_type', 'demand_stream', 'original_qty', 'adjusted_qty', 'applied_by_id', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply to History' },
      { m: 'action_revoke', l: 'Revoke', ask: 'Why the adjustment is revoked', kwarg: 'reason' }
    ] },
  'M43-drivers': { kind: 'model_list', model: 'fix.demand.driver', stateField: 'state',
    cols: ['name', 'driver_type', 'product_id', 'location_id', 'period_from', 'period_to', 'expected_impact_pct', 'source_ref', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_retire', l: 'Retire' }
    ] },
  'M43-targets': { kind: 'model_list', model: 'fix.demand.service.target', stateField: 'state',
    cols: ['name', 'abc_class', 'criticality', 'location_type', 'target_pct', 'effective_from', 'prepared_by_id', 'approved_by_id', 'state'],
    actions: [{ m: 'action_activate', l: 'Approve & Activate' }] },
  'M43-leadtimes': { kind: 'model_list', model: 'fix.demand.lead.time', stateField: 'state',
    cols: ['name', 'product_id', 'vendor_id', 'quoted_days', 'sample_count', 'mean_days', 'std_dev_days', 'p95_days', 'variance_days', 'supply_source', 'state'],
    actions: [{ m: 'action_measure', l: 'Measure from Receipts' }] },
  'M43-npi': { kind: 'model_list', model: 'fix.demand.npi', stateField: 'state',
    cols: ['name', 'product_id', 'part_id', 'analogy_part_id', 'recommended_initial_qty', 'confidence', 'prepared_by_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M43-eol': { kind: 'model_list', model: 'fix.demand.eol', stateField: 'state',
    cols: ['name', 'part_id', 'successor_part_id', 'run_down_start', 'last_buy_date', 'projected_remaining_demand', 'last_time_buy_qty', 'last_time_buy_value', 'needs_cfo', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_approve_cfo', l: 'CFO Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Why the plan is rejected', kwarg: 'reason' }
    ] },
  'M43-vanpars': { kind: 'model_list', model: 'fix.demand.van.par', stateField: 'state',
    cols: ['name', 'van_location_id', 'technician_id', 'part_id', 'suggested_min', 'suggested_max', 'min_qty', 'max_qty', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_compute', l: 'Compute from Van Use' },
      { m: 'action_approve', l: 'Approve & Apply to M15' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M43-network': { kind: 'model_list', model: 'fix.demand.network.policy', stateField: 'state',
    cols: ['name', 'part_id', 'central_stock', 'location_ids', 'van_stock', 'prepared_by_id', 'approved_by_id', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }] },

  /* Report chips -> their own computed pack */
  'M43-rpt-class': { kind: 'table_report', module: 'M43', report: 'accuracy_by_class', title: 'Forecast Accuracy by Class', period: false },
  'M43-rpt-stockout': { kind: 'table_report', module: 'M43', report: 'stockout_causes', title: 'Stockout Root Causes', period: false },
  'M43-rpt-excess': { kind: 'table_report', module: 'M43', report: 'excess_obsolescence', title: 'Excess & Obsolescence Exposure', period: false },
  'M43-rpt-rebalance': { kind: 'table_report', module: 'M43', report: 'rebalancing_value', title: 'Rebalancing Value Moved', period: false },
  'M43-rpt-newpart': { kind: 'table_report', module: 'M43', report: 'new_part_intro', title: 'New-Part Introduction', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M43-form-plan': {
    kind: 'model_form',
    model: 'fix.demand.plan',
    title: 'Demand Plan',
    back: 'M43-planned',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', released: 'Released to M16', converted: 'Converted to PO', closed: 'Closed (received)' } },
    tabs: [
      { id: 'plan', label: '1. Plan', bn: '১. পরিকল্পনা', icon: '📈', badge: '8' },
      { id: 'position', label: '2. Position', bn: '২. অবস্থান', icon: '📊', badge: '8' },
      { id: 'release', label: '3. Approval & M16', bn: '৩. অনুমোদন ও এম১৬', icon: '📝', badge: '7' }
    ],
    sections: [
      { tab: 'plan', title: 'Plan', note: 'Demand is the approved forecasts of the plan months; stock is M15 owned on-hand at the location; ROP and target come from the active policy. Order when projected stock is at or below ROP, up to the target, net of stock on order. Changing an input voids an approval. The supplier must be active in M42 before release; empty takes the last purchase order\'s supplier.',
        fields: [
          { name: 'name', required: true, label: 'Plan' },
          { name: 'product_id', required: true, label: 'Product (M16)' },
          { name: 'part_id', label: 'M15 Spare Part' },
          { name: 'location_id', label: 'Stock Location', domain: [['state', '=', 'active']] },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'vendor_id', label: 'Supplier' },
          { name: 'period_start', required: true, label: 'Period Start' },
          { name: 'period_end', required: true, label: 'Period End' }
        ] },
      { tab: 'position', title: 'Position (computed)', fields: [
          { name: 'forecast_quantity', readonly: true, label: 'Forecast Demand' },
          { name: 'current_stock', readonly: true, label: 'Current Stock' },
          { name: 'on_order_qty', readonly: true, label: 'On Order' },
          { name: 'reorder_point', readonly: true, label: 'Reorder Point' },
          { name: 'target_level', readonly: true, label: 'Target Level' },
          { name: 'projected_stock', readonly: true, label: 'Projected Stock' },
          { name: 'raw_order_qty', readonly: true, label: 'Order Before MOQ / Pack' },
          { name: 'recommended_order', readonly: true, label: 'Recommended Order' }
        ] },
      { tab: 'release', title: 'Approval & M16', note: 'A plan moves to Converted when M16 converts its requisition, and to Closed when the PO is fully received, with the actual lead time written back. If M16 rejects or cancels it, Reopen returns the plan to draft to be approved and reissued.',
        fields: [
          { name: 'approved_order_qty', readonly: true, label: 'Approved Order Qty' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'budget_check', readonly: true, label: 'Budget Check' },
          { name: 'pr_requisition_id', readonly: true, label: 'Requisition' },
          { name: 'pr_state', readonly: true, label: 'Requisition State' },
          { name: 'purchase_order_id', readonly: true, label: 'Purchase Order' },
          { name: 'actual_lead_time_days', readonly: true, label: 'Actual Lead Time (days)' }
        ] }
    ]
  },

  'M43-form-forecast': {
    kind: 'model_form',
    model: 'fix.demand.forecast',
    title: 'Demand Forecast',
    back: 'M43-models',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', published: 'Published' } },
    tabs: [
      { id: 'forecast', label: '1. Forecast', bn: '১. পূর্বাভাস', icon: '📈', badge: '10' },
      { id: 'computed', label: '2. Computed', bn: '২. গণনা', icon: '🧮', badge: '10' }
    ],
    sections: [
      { tab: 'forecast', title: 'Forecast', note: 'Compute from History takes the moving average of the M15 consumption of the window months before the period. An override keeps the statistical value and needs a rationale. Approval is by a Demand Plan Approver who did not prepare it.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'part_id', label: 'M15 Spare Part' },
          { name: 'location_id', label: 'Stock Location' },
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'window_months', label: 'Window (months)' },
          { name: 'has_override', label: 'Planner Override' },
          { name: 'override_qty', label: 'Override Qty' },
          { name: 'override_rationale', type: 'text', label: 'Override Rationale' },
          { name: 'override_driver_id', label: 'Driver the Override Answers', domain: [['state', '=', 'active']] },
          { name: 'notes', label: 'Notes' }
        ] },
      { tab: 'computed', title: 'Computed', note: 'The method is a moving average of M15 consumption (months marked * carry an applied history adjustment) or a planner override; active demand drivers are shown for an override to answer. Exponential and seasonal models need the M26 forecast engine, which is not built.', fields: [
          { name: 'statistical_qty', readonly: true, label: 'Statistical Forecast' },
          { name: 'history_detail', readonly: true, label: 'History Used' },
          { name: 'forecast_qty', readonly: true, label: 'Forecast Qty' },
          { name: 'method', readonly: true, label: 'Method' },
          { name: 'source', readonly: true, label: 'Source' },
          { name: 'actual_qty', readonly: true, label: 'Actual (M15)' },
          { name: 'abs_error_pct', readonly: true, label: 'Abs Error %' },
          { name: 'driver_impact_pct', readonly: true, label: 'Active Driver Impact %' },
          { name: 'driver_note', readonly: true, label: 'Active Drivers' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
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
      { title: 'Segment', note: 'ABC (consumption value) and XYZ (demand variability) are computed by Classify from M15 History. Criticality is set by a Demand Plan Approver.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'part_id', label: 'M15 Spare Part' },
          { name: 'criticality', required: true, label: 'Criticality' },
          { name: 'abc_class', readonly: true, label: 'ABC' },
          { name: 'xyz_class', readonly: true, label: 'XYZ' },
          { name: 'consumption_value', readonly: true, label: 'Consumption Value' },
          { name: 'demand_cv', readonly: true, label: 'Demand CV' },
          { name: 'classified_on', readonly: true, label: 'Classified On' }
        ] }
    ]
  },

  'M43-form-policy': {
    kind: 'model_form',
    model: 'fix.demand.policy',
    title: 'Policy Assignment',
    back: 'M43-safety',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', paused: 'Paused', superseded: 'Superseded' } },
    tabs: [
      { id: 'policy', label: '1. Policy', bn: '১. নীতি', icon: '📋', badge: '11' },
      { id: 'provisional', label: '2. Provisional Demand', bn: '২. অস্থায়ী চাহিদা', icon: '✋', badge: '5' },
      { id: 'computed', label: '3. Computed', bn: '৩. গণনা', icon: '🧮', badge: '12' }
    ],
    sections: [
      { tab: 'policy', title: 'Policy', note: 'Demand statistics come from M15 consumption and the lead time from M16 and M44 receipts (Refresh from History); a typed lead time that differs from the observed one needs a rationale. Orders are at least the MOQ and in whole packs. Safety stock = z × σ × √lead time; ROP = avg daily × lead time + safety stock; target = ROP + avg daily × review period. A-class, critical or unclassified items are activated by a Demand Plan Approver; a policy below the service-level target of its segment, or at a location the network stocking policy of the part excludes, is not activated an active policy changes only through a new version. Pausing suspends the published M15 reorder rule; resuming restores it.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'part_id', label: 'M15 Spare Part' },
          { name: 'location_id', label: 'Stock Location', domain: [['state', '=', 'active']] },
          { name: 'history_days', label: 'History Window (days)' },
          { name: 'lead_time_window_days', label: 'Lead-Time Window (days)' },
          { name: 'lead_time_days', label: 'Lead Time (days)' },
          { name: 'lead_time_override_rationale', type: 'text', label: 'Lead-Time Override Rationale' },
          { name: 'service_level_pct', required: true, label: 'Service Level' },
          { name: 'review_period_days', label: 'Review Period (days)' },
          { name: 'moq_qty', label: 'Minimum Order Qty' },
          { name: 'pack_size', label: 'Pack Size' }
        ] },
      { tab: 'provisional', title: 'Provisional Demand', note: 'For a part with no M15 history: state a manual daily demand and why. A Demand Plan Approver who did not enter it approves it, and it stands in until real history exists; a plan on the policy is then refused until the policy is revised from history.',
        fields: [
          { name: 'provisional_daily_demand', label: 'Provisional Daily Demand' },
          { name: 'provisional_reason', label: 'Why Provisional' },
          { name: 'provisional_state', readonly: true, label: 'Status' },
          { name: 'provisional_entered_by_id', readonly: true, label: 'Entered By' },
          { name: 'provisional_approved_by_id', readonly: true, label: 'Approved By' }
        ] },
      { tab: 'computed', title: 'Computed', fields: [
          { name: 'avg_daily_demand', readonly: true, label: 'Avg Daily Demand' },
          { name: 'demand_stddev', readonly: true, label: 'Demand Std Dev' },
          { name: 'observed_lead_time_days', readonly: true, label: 'Observed Lead Time (M16, M44)' },
          { name: 'lead_time_samples', readonly: true, label: 'Lead-Time Samples' },
          { name: 'lead_time_source', readonly: true, label: 'Lead-Time Source' },
          { name: 'safety_stock', readonly: true, label: 'Safety Stock' },
          { name: 'reorder_point', readonly: true, label: 'Reorder Point' },
          { name: 'target_level', readonly: true, label: 'Target Level' },
          { name: 'segment_target', readonly: true, label: 'Segment Service-Level Target' },
          { name: 'version', readonly: true, label: 'Version' },
          { name: 'approved_by_id', readonly: true, label: 'Activated By' },
          { name: 'published_on', readonly: true, label: 'Published to M15' }
        ] }
    ]
  },

  'M43-form-review': {
    kind: 'model_form',
    model: 'fix.demand.review',
    title: 'Review Cycle',
    back: 'M43-reviews',
    status: { field: 'state', labels: { scheduled: 'Scheduled', done: 'Done' } },
    sections: [
      { title: 'Review', note: 'The owner completes the review and records its outcome.', fields: [
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'owner_id', label: 'Owner' },
          { name: 'due_on', required: true, label: 'Due On' },
          { name: 'notes', type: 'text', label: 'Outcome / Notes' },
          { name: 'completed_by_id', readonly: true, label: 'Completed By' }
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
      { title: 'Proposal', note: 'Approval by a Demand Plan Approver who did not propose it creates a draft M15 transfer, only where the estimated benefit exceeds the transfer cost (BRU-DPL-13). The benefit is the proposer\'s estimate with its basis, not a measured saving.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'part_id', label: 'M15 Spare Part' },
          { name: 'source_location_id', label: 'From Location' },
          { name: 'target_location_id', label: 'To Location' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'transfer_cost', label: 'Estimated Transfer Cost' },
          { name: 'benefit_value', label: 'Estimated Benefit' },
          { name: 'benefit_basis', label: 'Benefit Basis' },
          { name: 'proposed_on', required: true, label: 'Proposed On' },
          { name: 'notes', label: 'Notes' },
          { name: 'source_available', readonly: true, label: 'Available at Source' },
          { name: 'stock_value', readonly: true, label: 'Stock Value Moved' },
          { name: 'net_benefit', readonly: true, label: 'Net Benefit' },
          { name: 'transfer_id', readonly: true, label: 'M15 Transfer' }
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
      { title: 'Scenario', note: 'The projected ROP re-applies the base policy with the demand adjustment and the lead-time delta. Running it changes no policy or plan.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'policy_id', label: 'Base Policy', domain: [['state', 'in', ['active', 'paused']]] },
          { name: 'demand_adjust_pct', label: 'Demand Adjustment %' },
          { name: 'lead_time_delta_days', label: 'Lead Time Delta (days)' },
          { name: 'notes', label: 'Notes' },
          { name: 'base_reorder_point', readonly: true, label: 'Base ROP' },
          { name: 'projected_lead_time', readonly: true, label: 'Projected Lead Time' },
          { name: 'projected_reorder_point', readonly: true, label: 'Projected ROP' }
        ] }
    ]
  },

  /* ============ capture audit 2026-11-16 ============ */
  'M43-form-adjustment': {
    kind: 'model_form',
    model: 'fix.demand.adjustment',
    title: 'Demand Adjustment',
    back: 'M43-adjustments',
    status: { field: 'state', labels: { draft: 'Draft', applied: 'Applied', revoked: 'Revoked' } },
    sections: [
      { title: 'Adjustment', note: 'An overlay on the M15 history, never an edit of it (T-01): Apply records the month\'s M15 consumption beside the treated value, and the next forecast computed over that month uses the treated value. Exclude and reclassify take the month out of routine demand (a project or campaign spike, BRU-DPL-05); replace lowers an outlier to a typical value; a censored-demand correction raises a month consumed while out of stock (BRU-DPL-19). One applied adjustment per part, location and month; revoke it to change it.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'part_id', required: true, label: 'M15 Spare Part' },
          { name: 'location_id', label: 'Stock Location (empty = all)' },
          { name: 'period', required: true, label: 'Month (YYYY-MM)' },
          { name: 'adjustment_type', required: true, label: 'Treatment' },
          { name: 'demand_stream', label: 'Moved To Stream (reclassify)' },
          { name: 'adjusted_qty', label: 'Adjusted Quantity (replace / censored)' },
          { name: 'reason', type: 'text', required: true, label: 'Reason' },
          { name: 'original_qty', readonly: true, label: 'M15 Consumption (source)' },
          { name: 'applied_by_id', readonly: true, label: 'Applied By' },
          { name: 'applied_on', readonly: true, label: 'Applied On' },
          { name: 'revoke_reason', readonly: true, label: 'Revoke Reason' }
        ] }
    ]
  },

  'M43-form-driver': {
    kind: 'model_form',
    model: 'fix.demand.driver',
    title: 'Demand Driver',
    back: 'M43-drivers',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    sections: [
      { title: 'Driver', note: 'A known influence on demand: installed base (M17), a contract or AMC schedule (M08), a warranty campaign (M09), seasonality or a branch opening. An active driver is shown on every forecast of its product and months; a planner override can cite it, with its rationale.',
        fields: [
          { name: 'driver_type', required: true, label: 'Driver' },
          { name: 'source_ref', label: 'Source Reference' },
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'location_id', label: 'Stock Location (empty = all)' },
          { name: 'period_from', required: true, label: 'From (YYYY-MM)' },
          { name: 'period_to', required: true, label: 'To (YYYY-MM)' },
          { name: 'expected_impact_pct', required: true, label: 'Expected Impact %' },
          { name: 'basis', type: 'text', required: true, label: 'Basis' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' }
        ] }
    ]
  },

  'M43-form-target': {
    kind: 'model_form',
    model: 'fix.demand.service.target',
    title: 'Service-Level Target',
    back: 'M43-targets',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', superseded: 'Superseded' } },
    sections: [
      { title: 'Target', note: 'The service level a segment must be planned to (FR-DPL-018), for example 98% for A-class critical parts at central. A Demand Plan Approver who did not write it activates it, superseding the target it replaces. A policy is not activated below the most specific active target of its part\'s segment and location type.',
        fields: [
          { name: 'abc_class', required: true, label: 'ABC Class' },
          { name: 'criticality', label: 'Criticality (empty = any)' },
          { name: 'location_type', label: 'Location Type (empty = any)' },
          { name: 'target_pct', required: true, label: 'Target Service Level' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'rationale', label: 'Rationale' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
        ] }
    ]
  },

  'M43-form-leadtime': {
    kind: 'model_form',
    model: 'fix.demand.lead.time',
    title: 'Lead-Time Model',
    back: 'M43-leadtimes',
    status: { field: 'state', labels: { quoted: 'Quoted only', measured: 'Measured' } },
    sections: [
      { title: 'Supplier Lead Time', note: 'The supplier\'s quoted lead time is kept for comparison only (BRU-DPL-09): Measure from Receipts computes the actual mean, deviation and 95th percentile from this supplier\'s posted M16 receipts (PO sent to receipt) and M44 imports (commitment to receipt) in the window. Changing the product, supplier or window clears the measurement.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'vendor_id', required: true, label: 'Supplier' },
          { name: 'quoted_days', required: true, label: 'Quoted Lead Time (days)' },
          { name: 'window_days', label: 'Receipt Window (days)' },
          { name: 'notes', label: 'Notes' },
          { name: 'supply_source', readonly: true, label: 'Supply Source' },
          { name: 'sample_count', readonly: true, label: 'Receipts Measured' },
          { name: 'mean_days', readonly: true, label: 'Actual Mean (days)' },
          { name: 'std_dev_days', readonly: true, label: 'Actual Std Dev (days)' },
          { name: 'p95_days', readonly: true, label: 'Actual P95 (days)' },
          { name: 'variance_days', readonly: true, label: 'Actual − Quoted (days)' },
          { name: 'measured_on', readonly: true, label: 'Measured On' }
        ] }
    ]
  },

  'M43-form-npi': {
    kind: 'model_form',
    model: 'fix.demand.npi',
    title: 'New-Part Recommendation',
    back: 'M43-npi',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Recommendation', note: 'An initial stocking position for a part with no M15 history (FR-DPL-030), by analogy to a similar part and installed-base or launch data. A Demand Plan Approver who did not prepare it decides; a part that already has M15 history is planned from its own demand instead.',
        fields: [
          { name: 'product_id', required: true, label: 'New Product' },
          { name: 'part_id', label: 'New M15 Spare Part' },
          { name: 'analogy_part_id', label: 'Analogy Part' },
          { name: 'installed_base_ref', label: 'Installed Base / Launch Data (M17)' },
          { name: 'location_ids', label: 'Stock At' },
          { name: 'recommended_initial_qty', required: true, label: 'Initial Quantity' },
          { name: 'confidence', required: true, label: 'Confidence' },
          { name: 'rationale', type: 'text', required: true, label: 'Rationale' },
          { name: 'analogy_monthly_avg', readonly: true, label: 'Analogy Avg / Month (12 m, M15)' },
          { name: 'approved_by_id', readonly: true, label: 'Decided By' }
        ] }
    ]
  },

  'M43-form-eol': {
    kind: 'model_form',
    model: 'fix.demand.eol',
    title: 'End-of-Life Plan',
    back: 'M43-eol',
    status: { field: 'state', labels: { draft: 'Draft', cfo: 'Awaiting CFO', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Run-Down & Last-Time Buy', note: 'A last-time buy creates unavoidable future dead stock (BRU-DPL-14): a Demand Plan Approver who did not prepare it approves it, and above the configured value (cd_demand_plan.ltb_cfo_threshold, BDT, at the M15 standard cost) it then waits for a DOFA Tier 4 (CFO) approver who is neither.',
        fields: [
          { name: 'part_id', required: true, label: 'Part Going Out' },
          { name: 'successor_part_id', label: 'Successor Part' },
          { name: 'run_down_start', required: true, label: 'Run-Down Start' },
          { name: 'last_buy_date', label: 'Last-Buy Window Closes' },
          { name: 'projected_remaining_demand', required: true, label: 'Projected Remaining Demand' },
          { name: 'last_time_buy_qty', required: true, label: 'Last-Time-Buy Qty' },
          { name: 'rationale', type: 'text', required: true, label: 'Rationale' },
          { name: 'last_time_buy_value', readonly: true, label: 'Last-Time-Buy Value' },
          { name: 'needs_cfo', readonly: true, label: 'Needs CFO' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'cfo_approved_by_id', readonly: true, label: 'CFO Approved By' },
          { name: 'reject_reason', readonly: true, label: 'Reject Reason' }
        ] }
    ]
  },

  'M43-form-vanpar': {
    kind: 'model_form',
    model: 'fix.demand.van.par',
    title: 'Van Par Recommendation',
    back: 'M43-vanpars',
    status: { field: 'state', labels: { proposed: 'Proposed', applied: 'Applied to M15', rejected: 'Rejected' } },
    tabs: [
      { id: 'par', label: '1. Van & Par', bn: '১. ভ্যান ও পার', icon: '🚐', badge: '9' },
      { id: 'basis', label: '2. Computed Basis', bn: '২. গণনার ভিত্তি', icon: '🧮', badge: '8' }
    ],
    sections: [
      { tab: 'par', title: 'Van & Par', note: 'Van par levels are computed by M43 and enforced by M15 (BRU-DPL-12): Compute from Van Use reads the van\'s own M15 consumption; a par that differs from the suggestion needs its reason. A Demand Plan Approver who did not prepare it approves it, which publishes it as the van\'s M15 reorder rule. A part the network stocking policy keeps off vans is refused.',
        fields: [
          { name: 'van_location_id', required: true, label: 'Van', domain: [['location_type', '=', 'van']] },
          { name: 'technician_id', readonly: true, label: 'Technician' },
          { name: 'part_id', required: true, label: 'M15 Spare Part' },
          { name: 'history_days', label: 'History Window (days)' },
          { name: 'replenish_days', label: 'Van Replenishment Cycle (days)' },
          { name: 'service_level_pct', required: true, label: 'Service Level' },
          { name: 'min_qty', label: 'Par Min' },
          { name: 'max_qty', label: 'Par Max' },
          { name: 'deviation_reason', label: 'Why Not the Suggestion' }
        ] },
      { tab: 'basis', title: 'Computed Basis', fields: [
          { name: 'avg_daily_demand', readonly: true, label: 'Van Avg Daily Use' },
          { name: 'demand_stddev', readonly: true, label: 'Van Use Std Dev' },
          { name: 'suggested_min', readonly: true, label: 'Suggested Min' },
          { name: 'suggested_max', readonly: true, label: 'Suggested Max' },
          { name: 'computed_on', readonly: true, label: 'Computed On' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'approved_by_id', readonly: true, label: 'Decided By' },
          { name: 'published_rule_id', readonly: true, label: 'M15 Reorder Rule' }
        ] }
    ]
  },

  'M43-form-network': {
    kind: 'model_form',
    model: 'fix.demand.network.policy',
    title: 'Network Stocking Policy',
    back: 'M43-network',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', superseded: 'Superseded' } },
    sections: [
      { title: 'Where the Part Is Held', note: 'Which parts are stocked centrally, forward-stocked at which branches and held on vans (FR-DPL-027). A Demand Plan Approver who did not prepare it approves it, superseding the earlier policy; a replenishment policy or van par at a location it excludes is then refused.',
        fields: [
          { name: 'part_id', required: true, label: 'M15 Spare Part' },
          { name: 'central_stock', label: 'Held at Central' },
          { name: 'location_ids', label: 'Forward-Stocked At (branches)', domain: [['location_type', '=', 'branch']] },
          { name: 'van_stock', label: 'Held on Vans' },
          { name: 'rationale', type: 'text', required: true, label: 'Rationale' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M43:Forecast Accuracy by Class': 'M43-rpt-class',
  'M43:Stockout Root Causes': 'M43-rpt-stockout',
  'M43:Excess & Obsolescence Exposure': 'M43-rpt-excess',
  'M43:Rebalancing Value Moved': 'M43-rpt-rebalance',
  'M43:New-Part Introduction': 'M43-rpt-newpart'
};

export const FORM_MODELS = {
  'M43:Review Cycle': 'fix.demand.review',
  'M43:Policy Assignment': 'fix.demand.policy',
  'M43:Rebalance Proposal': 'fix.demand.rebalance',
  'M43:Demand Adjustment': 'fix.demand.adjustment',
  'M43:Part Segmentation': 'fix.demand.segment',
  'M43:Demand Forecast': 'fix.demand.forecast',
  'M43:Demand Driver': 'fix.demand.driver',
  'M43:Service-Level Target': 'fix.demand.service.target',
  'M43:Lead-Time Model': 'fix.demand.lead.time',
  'M43:Demand Plan': 'fix.demand.plan',
  'M43:New-Part Recommendation': 'fix.demand.npi',
  'M43:End-of-Life Plan': 'fix.demand.eol',
  'M43:Van Par Recommendation': 'fix.demand.van.par',
  'M43:Network Stocking Policy': 'fix.demand.network.policy',
  'M43:What-If Scenario': 'fix.demand.scenario'
};

export const FORM_CHIPS = {
  'M43:Review Cycle': 'M43-form-review',
  'M43:Policy Assignment': 'M43-form-policy',
  'M43:Rebalance Proposal': 'M43-form-rebalance',
  'M43:Demand Adjustment': 'M43-form-adjustment',
  'M43:Part Segmentation': 'M43-form-segment',
  'M43:Demand Forecast': 'M43-form-forecast',
  'M43:Demand Driver': 'M43-form-driver',
  'M43:Service-Level Target': 'M43-form-target',
  'M43:Lead-Time Model': 'M43-form-leadtime',
  'M43:Demand Plan': 'M43-form-plan',
  'M43:New-Part Recommendation': 'M43-form-npi',
  'M43:End-of-Life Plan': 'M43-form-eol',
  'M43:Van Par Recommendation': 'M43-form-vanpar',
  'M43:Network Stocking Policy': 'M43-form-network',
  'M43:What-If Scenario': 'M43-form-scenario',
  'M43:__by_model__': {
    'fix.demand.plan': 'M43-form-plan',
    'fix.demand.forecast': 'M43-form-forecast',
    'fix.demand.segment': 'M43-form-segment',
    'fix.demand.policy': 'M43-form-policy',
    'fix.demand.review': 'M43-form-review',
    'fix.demand.rebalance': 'M43-form-rebalance',
    'fix.demand.scenario': 'M43-form-scenario',
    'fix.demand.adjustment': 'M43-form-adjustment',
    'fix.demand.driver': 'M43-form-driver',
    'fix.demand.service.target': 'M43-form-target',
    'fix.demand.lead.time': 'M43-form-leadtime',
    'fix.demand.npi': 'M43-form-npi',
    'fix.demand.eol': 'M43-form-eol',
    'fix.demand.van.par': 'M43-form-vanpar',
    'fix.demand.network.policy': 'M43-form-network'
  },
  'M43:__by_screen__': {
    'M43-models': 'M43-form-forecast',
    'M43-segments': 'M43-form-segment',
    'M43-safety': 'M43-form-policy',
    'M43-planned': 'M43-form-plan',
    'M43-reviews': 'M43-form-review',
    'M43-rebalance': 'M43-form-rebalance',
    'M43-whatif': 'M43-form-scenario',
    'M43-adjustments': 'M43-form-adjustment',
    'M43-drivers': 'M43-form-driver',
    'M43-targets': 'M43-form-target',
    'M43-leadtimes': 'M43-form-leadtime',
    'M43-npi': 'M43-form-npi',
    'M43-eol': 'M43-form-eol',
    'M43-vanpars': 'M43-form-vanpar',
    'M43-network': 'M43-form-network'
  }
};

export const CREATE = {
  M43: { screen: 'M43-form-policy', model: 'fix.demand.policy', label: 'Policy Assignment' }
};
