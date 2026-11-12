/** @odoo-module **/
/* A06 · Supply Chain — M43 Demand Planning & Replenishment (v2 rebuild).
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 3 forms / freg 58.
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
      { id: 'M43-models', en: 'Model Orchestration', bn: 'মডেল অর্কেস্ট্রেশন', t: 'g' },
      { id: 'M43-accuracy', en: 'Accuracy & Bias (MAPE)', bn: 'নির্ভুলতা ও বায়াস', t: 'r' }
    ]},
    { en: 'Policies', screens: [
      { id: 'M43-segments', en: 'Part Segmentation', bn: 'পার্ট সেগমেন্টেশন', t: 'g' },
      { id: 'M43-safety', en: 'Safety Stock & ROP', bn: 'সেফটি স্টক ও আরওপি', t: 'g' },
      { id: 'M43-leadtime', en: 'Lead-Time Modelling', bn: 'লিড-টাইম মডেলিং', t: 'r' }
    ]},
    { en: 'Execution', screens: [
      { id: 'M43-planned', en: 'Planned Orders → PR', bn: 'পরিকল্পিত অর্ডার', t: 'g' },
      { id: 'M43-reviews', en: 'Review Cycles', bn: 'পর্যালোচনা চক্র', t: 'g' },
      { id: 'M43-rebalance', en: 'Network Rebalancing', bn: 'নেটওয়ার্ক রিব্যালান্স', t: 'g' },
      { id: 'M43-vanpar', en: 'Van-Stock Par Calculation', bn: 'ভ্যান পার', t: 'r' }
    ]},
    { en: 'Simulation', screens: [
      { id: 'M43-whatif', en: 'What-If Simulation', bn: 'হোয়াট-ইফ সিমুলেশন', t: 'g' }
    ]}
  ],
  reports: ['Forecast Accuracy by Class', 'Stockout Root Causes', 'Excess & Obsolescence Exposure', 'Rebalancing Value Moved', 'New-Part Introduction'],
  forms: ['Review Cycle', 'Policy Assignment', 'Rebalance Proposal'],
  cross: ['M26 forecast models', 'M16 planned orders', 'M15 stock positions', 'M37 lifecycle states'],
  freg: { src: 58, sub: [
    ['1', 'History & Cleansing', 7, { model: 'fix.demand.forecast', cols: ['product_id', 'period', 'actual_qty', 'source', 'state'], screens: ['M43-history'], reports: ['Stockout Root Causes'], forms: [], create: false }],
    ['2', 'Segmentation', 6, { model: 'fix.demand.segment', cols: ['product_id', 'abc_class', 'xyz_class', 'criticality', 'state'], screens: ['M43-segments'], reports: ['Excess & Obsolescence Exposure'], forms: [] }],
    ['3', 'Forecast Orchestration', 8, { model: 'fix.demand.forecast', cols: ['name', 'product_id', 'period', 'forecast_qty', 'method'], screens: ['M43-models', 'M43-reviews'], reports: ['Forecast Accuracy by Class'], forms: ['Review Cycle'] }],
    ['4', 'Accuracy Tracking', 6, { model: 'fix.demand.forecast', cols: ['product_id', 'period', 'forecast_qty', 'actual_qty', 'abs_error_pct'], screens: ['M43-accuracy'], reports: ['Forecast Accuracy by Class'], forms: [], create: false }],
    ['5', 'Safety Stock & ROP', 9, { model: 'fix.demand.policy', cols: ['product_id', 'service_level_pct', 'safety_stock', 'reorder_point', 'target_level', 'state'], screens: ['M43-safety'], reports: ['Stockout Root Causes'], forms: ['Policy Assignment'] }],
    ['6', 'Lead-Time', 5, { model: 'fix.demand.policy', cols: ['product_id', 'lead_time_days', 'avg_daily_demand', 'demand_stddev'], screens: ['M43-leadtime'], reports: [], forms: [], create: false }],
    ['7', 'Planned Orders', 6, { model: 'fix.demand.plan', cols: ['name', 'product_id', 'forecast_quantity', 'recommended_order', 'state'], screens: ['M43-planned'], reports: ['New-Part Introduction'], forms: [] }],
    ['8', 'Multi-Echelon Rebalancing', 7, { model: 'fix.demand.rebalance', cols: ['name', 'product_id', 'source_location_id', 'target_location_id', 'qty'], screens: ['M43-rebalance', 'M43-vanpar'], reports: ['Rebalancing Value Moved'], forms: ['Rebalance Proposal'] }],
    ['9', 'What-If', 4, { model: 'fix.demand.scenario', cols: ['name', 'product_id', 'demand_adjust_pct', 'projected_reorder_point', 'state'], screens: ['M43-whatif'], reports: ['Excess & Obsolescence Exposure'], forms: [] }]
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
      { id: 'forecast', label: '1. Forecast', bn: '১. পূর্বাভাস', icon: '📈', badge: '9' },
      { id: 'computed', label: '2. Computed', bn: '২. গণনা', icon: '🧮', badge: '8' }
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
          { name: 'notes', label: 'Notes' }
        ] },
      { tab: 'computed', title: 'Computed', note: 'The method is a moving average of M15 consumption or a planner override. Exponential and seasonal models need the M26 forecast engine, which is not built.', fields: [
          { name: 'statistical_qty', readonly: true, label: 'Statistical Forecast' },
          { name: 'history_detail', readonly: true, label: 'History Used' },
          { name: 'forecast_qty', readonly: true, label: 'Forecast Qty' },
          { name: 'method', readonly: true, label: 'Method' },
          { name: 'source', readonly: true, label: 'Source' },
          { name: 'actual_qty', readonly: true, label: 'Actual (M15)' },
          { name: 'abs_error_pct', readonly: true, label: 'Abs Error %' },
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
      { id: 'computed', label: '3. Computed', bn: '৩. গণনা', icon: '🧮', badge: '11' }
    ],
    sections: [
      { tab: 'policy', title: 'Policy', note: 'Demand statistics come from M15 consumption and the lead time from M16 and M44 receipts (Refresh from History); a typed lead time that differs from the observed one needs a rationale. Orders are at least the MOQ and in whole packs. Safety stock = z × σ × √lead time; ROP = avg daily × lead time + safety stock; target = ROP + avg daily × review period. A-class, critical or unclassified items are activated by a Demand Plan Approver; an active policy changes only through a new version. Pausing suspends the published M15 reorder rule; resuming restores it.',
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
  'M43:Rebalance Proposal': 'fix.demand.rebalance'
};

export const FORM_CHIPS = {
  'M43:Review Cycle': 'M43-form-review',
  'M43:Policy Assignment': 'M43-form-policy',
  'M43:Rebalance Proposal': 'M43-form-rebalance',
  'M43:__by_model__': {
    'fix.demand.plan': 'M43-form-plan',
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
    'M43-planned': 'M43-form-plan',
    'M43-reviews': 'M43-form-review',
    'M43-rebalance': 'M43-form-rebalance',
    'M43-whatif': 'M43-form-scenario'
  }
};

export const CREATE = {
  M43: { screen: 'M43-form-policy', model: 'fix.demand.policy', label: 'Policy Assignment' }
};
