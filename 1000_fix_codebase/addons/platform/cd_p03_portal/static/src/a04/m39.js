/** @odoo-module **/
/* A04 · Commercial & Revenue — M39 Subscriptions & Recurring (v2 rebuild).
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 92.
 * Subscriptions and charges are real; usage, proration and autopay are new.
 * MRR is the recorded recurring amount of live subscriptions; NRR is a
 * declared gap (no expansion/contraction history).
 *
 * Capture audit (2026-11-19): only page 1 had a "+ New". Each sub-module page
 * now captures the record the spec gives it: billing schedule (FR-SUB-002),
 * charge line / usage tariff (FR-SUB-004/024), plan or quantity change
 * (FR-SUB-005/012), usage reading with its exception queue (FR-SUB-023/030),
 * billing run with dry run and review (FR-SUB-031..038, BRU-SUB-17), credit /
 * adjustment (FR-SUB-037), pause / resume / cancel / renew request (section 8,
 * BRU-SUB-07/13), autopay mandate (FR-SUB-009) and churn reason (FR-SUB-042). */

export const MODULE = {
  area: 'A04', code: 'M39', en: 'Subscriptions & Recurring', title: 'M39 · Subscriptions & Recurring',
  bn: 'সাবস্ক্রিপশন ও রিকারিং', icon: '🔁',
  desc: 'Subscription object and plans, usage rating and overage, billing runs, proration, autopay and dunning, MRR movement, cohorts and the recurring forecast.',
  kpis: [
    { l: 'MRR', m: 'mrr', prefix: '৳ ' },
    { l: 'ARR', m: 'arr', prefix: '৳ ' },
    { l: 'NRR', m: 'nrr', src: false, suffix: '%' },
    { l: 'Churn (Logo)', m: 'churn_logo', suffix: '%' },
    { l: 'Billing Exceptions', m: 'billing_exceptions' },
    { l: 'Dunning in Progress', m: 'dunning_in_progress' }
  ],
  groups: [
    { en: 'Subscriptions', screens: [
      { id: 'M39-subs', en: 'Subscriptions', bn: 'সাবস্ক্রিপশন', t: 'g' },
      { id: 'M39-record', en: 'Subscription Record', bn: 'সাবস্ক্রিপশন রেকর্ড', t: 'f' },
      { id: 'M39-lines', en: 'Charge Lines & Tariffs', bn: 'চার্জ লাইন ও ট্যারিফ', t: 'g' },
      { id: 'M39-plans', en: 'Plan Changes', bn: 'প্ল্যান পরিবর্তন', t: 'r' },
      { id: 'M39-lifecycle', en: 'Pause / Cancel / Renew Requests', bn: 'বিরতি / বাতিল / নবায়ন', t: 'g' }
    ]},
    { en: 'Rating & Billing', screens: [
      { id: 'M39-schedules', en: 'Billing Schedules', bn: 'বিলিং শিডিউল', t: 'g' },
      { id: 'M39-usage', en: 'Usage Rating', bn: 'ব্যবহার রেটিং', t: 'g' },
      { id: 'M39-usage-exceptions', en: 'Unrated Usage Queue', bn: 'রেটিং-বিহীন ব্যবহার', t: 'g' },
      { id: 'M39-billing-runs', en: 'Billing Runs', bn: 'বিলিং রান', t: 'g' },
      { id: 'M39-runs', en: 'Cycle Charges', bn: 'সাইকেল চার্জ', t: 'g' },
      { id: 'M39-proration', en: 'Proration Engine', bn: 'প্রোরেশন', t: 'g' },
      { id: 'M39-adjustments', en: 'Credits & Adjustments', bn: 'ক্রেডিট ও সমন্বয়', t: 'g' }
    ]},
    { en: 'Payments', screens: [
      { id: 'M39-autopay', en: 'Autopay & Retry', bn: 'অটোপে', t: 'g' },
      { id: 'M39-dunning', en: 'Dunning Coordination', bn: 'ডানিং', t: 'r' }
    ]},
    { en: 'Metrics', screens: [
      { id: 'M39-mrr', en: 'MRR Movement', bn: 'এমআরআর', t: 'r' },
      { id: 'M39-cohorts', en: 'Cohort Analysis', bn: 'কোহোর্ট', t: 'r' },
      { id: 'M39-churn', en: 'Churn Reasons', bn: 'চার্ন কারণ', t: 'g' },
      { id: 'M39-forecast', en: 'Recurring Forecast', bn: 'পূর্বাভাস', t: 'r' }
    ]}
  ],
  reports: ['MRR Waterfall', 'Churn & NRR Cohorts', 'Usage vs Committed', 'Billing Exception Log', 'Deferred Revenue Bridge', 'Plan Mix'],
  forms: ['Subscription', 'Billing Schedule', 'Charge Line', 'Plan Change', 'Usage Reading', 'Billing Run',
    'Cycle Charge', 'Credit / Adjustment', 'Lifecycle Request', 'Autopay Mandate', 'Dunning Step', 'Churn Record'],
  cross: ['M20 AR', 'M53 Rev-Rec', 'M08 Contracts'],
  freg: { src: 92, sub: [
    ['1', 'Subscription Object', 10, { model: 'fix.subscription', cols: ['name', 'customer_id', 'state', 'recurring_amount', 'next_invoice_date'], screens: ['M39-subs'], reports: [], forms: ['Subscription'] }],
    // capture audit 2026-11-19: pages 2-10 had no "+ New". Page 2 offered a
    // hand-typed cycle charge that was never invoiced; the schedule is its record.
    ['2', 'Billing Schedules', 9, { model: 'fix.subscription.schedule', cols: ['name', 'subscription_id', 'alignment', 'timing', 'first_period', 'planned_total', 'state'], screens: ['M39-schedules', 'M39-plans', 'M39-rpt-planmix'], reports: ['Plan Mix'], forms: ['Billing Schedule'] }],
    ['3', 'Charge Models', 10, { model: 'fix.subscription.line', cols: ['subscription_id', 'name', 'charge_type', 'quantity', 'unit_rate', 'amount', 'state'], screens: ['M39-lines'], reports: [], forms: ['Charge Line'] }],
    ['4', 'Quantity & Proration', 12, { model: 'fix.subscription.proration', cols: ['name', 'state', 'subscription_id', 'amount', 'change_type', 'effective_date'], screens: ['M39-proration', 'M39-lines'], reports: [], forms: ['Plan Change', 'Charge Line'] }],
    ['5', 'Usage Rating', 8, { model: 'fix.subscription.usage', cols: ['subscription_id', 'metric', 'quantity', 'committed', 'overage_quantity', 'overage_charge', 'state'], screens: ['M39-usage', 'M39-usage-exceptions', 'M39-rpt-usage'], reports: ['Usage vs Committed'], forms: ['Usage Reading'] }],
    ['6', 'Billing Runs', 11, { model: 'fix.subscription.billing.run', cols: ['name', 'as_of', 'billing_cycle', 'unit_count', 'exception_count', 'total_amount', 'state'], screens: ['M39-billing-runs', 'M39-runs', 'M39-rpt-deferred'], reports: ['Deferred Revenue Bridge', 'Billing Exception Log'], forms: ['Billing Run', 'Cycle Charge'] }],
    ['7', 'Credits & Adjustments', 7, { model: 'fix.subscription.adjustment', cols: ['name', 'subscription_id', 'adjustment_type', 'direction', 'amount', 'state'], screens: ['M39-adjustments', 'M39-proration', 'M39-rpt-exceptions'], reports: ['Billing Exception Log'], forms: ['Credit / Adjustment', 'Plan Change'] }],
    ['8', 'Suspend / Cancel / Renew', 9, { model: 'fix.subscription.lifecycle', cols: ['name', 'subscription_id', 'action_type', 'effective_date', 'notice_ok', 'state'], screens: ['M39-lifecycle', 'M39-subs'], reports: [], forms: ['Lifecycle Request'] }],
    ['9', 'Autopay & Dunning', 8, { model: 'fix.subscription.autopay', cols: ['subscription_id', 'state', 'method', 'mandate_ref', 'last_attempt_at', 'last_result'], screens: ['M39-autopay', 'M39-dunning', 'M39-subs'], reports: [], forms: ['Autopay Mandate', 'Dunning Step'] }],
    ['10', 'Metrics & Forecast', 8, { model: 'fix.subscription.churn', cols: ['subscription_id', 'churn_date', 'churn_type', 'reason_code', 'competitor', 'lost_mrr'], screens: ['M39-churn', 'M39-mrr', 'M39-cohorts', 'M39-forecast'], reports: ['MRR Waterfall', 'Churn & NRR Cohorts'], forms: ['Churn Record'] }]
  ] }
};

export const SCREENS = {
  /* ---- registry screens restored (A04 zero-trust audit 2026-10-31): nav ids that dead-ended ---- */
  'M39-plans': { kind: 'table_report', module: 'M39', report: 'plan_mix', title: 'Plan Mix', period: true },
  // A04 build (2026-11-04): usage locks once billed (state), a charge is
  // frozen once invoiced, a proration is COMPUTED from the billed cycle and
  // approved from the M63 inbox, and a mandate activates only on the
  // customer's recorded consent (OTP, or a signed form verified by another
  // officer).
  // capture audit 2026-11-19: a reading is recorded here (Subscription Officer);
  // it rates against its usage tariff, and what cannot be rated is queued.
  'M39-usage': { kind: 'model_list', model: 'fix.subscription.usage', stateField: 'state',
    cols: ["subscription_id", "period_start", "period_end", "metric", "line_id", "quantity", "committed", "overage_charge", "source_module", "state", "charge_id"],
    actions: [{ m: 'action_rerate', l: 'Re-rate', states: ['exception'] }] },
  'M39-usage-exceptions': { kind: 'model_list', model: 'fix.subscription.usage', create: false, stateField: 'state',
    domain: [['state', '=', 'exception']],
    cols: ["subscription_id", "period_start", "period_end", "metric", "quantity", "exception_cause", "source_module", "source_key"],
    actions: [{ m: 'action_rerate', l: 'Re-rate (after giving it a tariff)', states: ['exception'] }] },
  // the cycle charges a billing run (or the daily job) raised: never typed
  'M39-runs': { kind: 'model_list', model: 'fix.subscription.charge', create: false,
    cols: ["customer_id", "subscription_id", "amount", "overage_amount", "currency_id", "create_date", "invoice_state", "days_past_due", "company_id", "operating_unit_id"] },
  'M39-proration': { kind: 'model_list', model: 'fix.subscription.proration',
    stateField: 'state',
    cols: ["name", "subscription_id", "change_type", "line_id", "new_quantity", "old_amount", "new_amount", "amount", "effective_date", "approval_state", "state", "billed_charge_id"],
    actions: [
      { m: 'action_request_approval', l: 'Submit Plan Change for Approval', states: ['draft'], ask: 'Business justification (mandatory from Tier 2)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['pending'] },
      { m: 'action_void', l: 'Void', states: ['draft', 'pending'] }
    ] },
  'M39-autopay': { kind: 'model_list', model: 'fix.subscription.autopay',
    stateField: 'state',
    cols: ["subscription_id", "state", "create_date", "method", "mandate_ref", "max_amount", "consent_channel", "consent_at", "last_attempt_at", "last_result", "failure_count"],
    actions: [
      { m: 'action_send_consent_otp', l: 'Send Consent Code to the Customer', states: ['draft'] },
      { m: 'action_verify_consent_otp', l: 'Verify Consent Code', states: ['draft'], ask: 'The code the customer reads back', kwarg: 'otp' },
      { m: 'action_verify_signed_form', l: 'Verify Signed Mandate Form (another officer)', states: ['draft'] },
      { m: 'action_activate', l: 'Activate Mandate', states: ['draft'] },
      { m: 'action_revoke', l: 'Revoke Mandate', states: ['draft', 'active', 'suspended'], ask: 'Why is the mandate revoked?', kwarg: 'reason' }
    ] },
  'M39-dunning': { kind: 'table_report', module: 'M39', report: 'dunning_ladder', title: 'Dunning Ladder', period: true },
  'M39-mrr': { kind: 'table_report', module: 'M39', report: 'mrr_waterfall', title: 'MRR Waterfall', period: true },
  'M39-cohorts': { kind: 'table_report', module: 'M39', report: 'churn_nrr_cohorts', title: 'Churn & NRR Cohorts', period: true },
  'M39-forecast': { kind: 'table_report', module: 'M39', report: 'recurring_forecast', title: 'Recurring Revenue Forecast', period: true },

  /* ---- capture audit 2026-11-19: the records pages 2, 3, 6, 7, 8 and 10 capture ---- */
  'M39-schedules': { kind: 'model_list', model: 'fix.subscription.schedule', stateField: 'state',
    cols: ['name', 'subscription_id', 'billing_cycle', 'alignment', 'timing', 'first_period', 'horizon', 'planned_total', 'state', 'activated_by_id'],
    actions: [
      { m: 'action_regenerate', l: 'Regenerate Periods', states: ['draft'] },
      { m: 'action_activate', l: 'Activate (billing user, not the author)', states: ['draft'] },
      { m: 'action_void', l: 'Void', states: ['draft'] }
    ] },
  'M39-lines': { kind: 'model_list', model: 'fix.subscription.line', stateField: 'state',
    cols: ['subscription_id', 'name', 'charge_type', 'quantity', 'unit_rate', 'amount', 'metric', 'included_qty', 'rating_model', 'start_date', 'end_date', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (billing user, not the author)', states: ['draft'] },
      { m: 'action_end', l: 'End Line', states: ['active'], ask: 'End date (YYYY-MM-DD, today or later)', kwarg: 'end_date' },
      { m: 'action_void', l: 'Void', states: ['draft'] }
    ] },
  'M39-billing-runs': { kind: 'model_list', model: 'fix.subscription.billing.run', stateField: 'state',
    cols: ['name', 'as_of', 'billing_cycle', 'customer_id', 'unit_count', 'exception_count', 'total_amount', 'dry_run_by_id', 'reviewed_by_id', 'state'],
    actions: [
      { m: 'action_dry_run', l: 'Run Dry Run', states: ['draft', 'dry_run'] },
      { m: 'action_review', l: 'Review Dry Run (Finance Manager)', states: ['dry_run'] },
      { m: 'action_commit', l: 'Commit / Resume Run', states: ['reviewed', 'partial'] },
      { m: 'action_void', l: 'Void', states: ['draft', 'dry_run', 'reviewed'] }
    ] },
  'M39-adjustments': { kind: 'model_list', model: 'fix.subscription.adjustment', stateField: 'state',
    cols: ['name', 'subscription_id', 'adjustment_type', 'direction', 'amount', 'charge_id', 'approval_state', 'state', 'applied_charge_id'],
    actions: [
      { m: 'action_request_approval', l: 'Submit for Approval', states: ['draft'], ask: 'Business justification', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['pending'] },
      { m: 'action_void', l: 'Void', states: ['draft', 'pending'] }
    ] },
  'M39-lifecycle': { kind: 'model_list', model: 'fix.subscription.lifecycle', stateField: 'state',
    cols: ['name', 'subscription_id', 'action_type', 'effective_date', 'pause_until', 'renewal_end_date', 'escalation_pct', 'notice_ok', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit', states: ['draft'] },
      { m: 'action_approve', l: 'Approve (not the requester)', states: ['pending'] },
      { m: 'action_reject', l: 'Reject', states: ['pending'], ask: 'Why is it rejected?', kwarg: 'reason' },
      { m: 'action_void', l: 'Void', states: ['draft', 'pending', 'scheduled'] }
    ] },
  'M39-churn': { kind: 'model_list', model: 'fix.subscription.churn',
    cols: ['subscription_id', 'customer_id', 'churn_date', 'churn_type', 'reason_code', 'competitor', 'cohort', 'lost_mrr'] },

  /* Report screens */
  'M39-rpt-exceptions': { kind: 'table_report', module: 'M39', report: 'billing_exception_log', title: 'Billing Exception Log', period: false },
  'M39-rpt-deferred': { kind: 'table_report', module: 'M39', report: 'deferred_revenue_bridge', title: 'Deferred Revenue Bridge', period: false },

  'M39-subs': { kind: 'model_list', model: 'fix.subscription', stateField: 'state',
    cols: ['name', 'customer_id', 'plan', 'billing_cycle', 'recurring_amount', 'next_invoice_date', 'state'] },
  'M39-record': {

    lines: {

      field: 'obligation_ids',

      title: 'Performance Obligations (IFRS 15)',

      note: 'Revenue is recognised per obligation as it is satisfied, not on invoice date.',

      fields: [

        { name: 'name', label: 'Obligation', required: true },

        { name: 'obligation_type', label: 'Type', required: true },

        { name: 'satisfaction', label: 'Satisfaction' },

        { name: 'standalone_price', label: 'Standalone Price' }

      ]

    },
    kind: 'model_form',
    model: 'fix.subscription',
    title: 'Recurring Subscription & Corporate Plan',
    back: 'M39-subs',
    status: { field: 'state' },
    tabs: [
      { id: 'header', label: '1. Subscription Profile', bn: '১. সাবস্ক্রিপশন পরিচিতি', icon: '📑', badge: '7' },
      { id: 'billing', label: '2. Recurring Plan & Charges', bn: '২. রিকারিং বিলিং ও চার্জ', icon: '💳', badge: '5' },
      { id: 'ifrs15', label: '3. IFRS 15 Revenue Obligations', bn: '৩. আইএফআরএস ১৫ রেভিনিউ', icon: '📊', badge: '3' },
      { id: 'statutory', label: '4. Statutory VAT & Mushak 6.3', bn: '৪. ভ্যাট ও চালান', icon: '⚖️', badge: '2' },
      { id: 'dunning', label: '5. Dunning & Service Lock', bn: '৫. ডানিং ও সার্ভিস লক', icon: '🔒', badge: '4' },
      { id: 'vault', label: '6. Mandate & Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'header', title: 'Subscription Identity & Enterprise Customer',
        note: 'Recurring device protection, managed IT services, and software subscription agreement.',
        fields: [
          { name: 'name', required: true, label: 'Subscription Reference' },
          { name: 'customer_id', required: true, label: 'Corporate Customer' },
          { name: 'contract_id', label: 'Master Contract Reference (M08)' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'state', label: 'Subscription Status', readonly: true },
          { name: 'consolidated', label: 'Roll into Consolidated Corporate Bill' }
        ] },
      { tab: 'billing', title: 'Recurring Tariff, Billing Cycles & Dates',
        fields: [
          { name: 'plan', required: true, label: 'Service Level Plan' },
          { name: 'billing_cycle', required: true, label: 'Billing Frequency' },
          { name: 'recurring_amount', required: true, label: 'Cycle Recurring Amount (BDT)' },
          { name: 'start_date', required: true, label: 'Subscription Start Date' },
          { name: 'next_invoice_date', required: true, label: 'Next Scheduled Invoice Date' }
        ] },
      { tab: 'ifrs15', title: 'IFRS 15 Revenue Recognition Schedules',
        note: 'Ratable revenue recognition over service performance term (BRU-LOY-12 / FLAW-39.1).',
        fields: [
          { name: 'contract_value', label: 'Term Transaction Price (BDT)' },
          { name: 'contract_end_date', label: 'Contract Expiration Date' }
        ] },
      { tab: 'statutory', title: 'Statutory VAT & Monthly Tax Invoice',
        note: 'Automatic Mushak 6.3 periodic invoicing under Bangladesh Value Added Tax Act 2012.',
        fields: [] },
      { tab: 'dunning', title: 'Dunning Escalation Ladder & Service Lock',
        note: 'Stage 1 (Day 3 SMS), Stage 2 (Day 7 Warning Email), Stage 3 (Day 14 Automated Service Order Lock).',
        fields: [
          { name: 'dunning_step', readonly: true, label: 'Current Dunning Stage' },
          { name: 'days_overdue', readonly: true, label: 'Days In Arrears' },
          { name: 'grace_period_days', label: 'Contractual Grace Period (Days)' }
        ] },
      { tab: 'vault', title: 'Subscription Mandate Vault',
        note: 'Customer autopay mandates, corporate master agreements, and billing exception waivers.',
        fields: [] }
    ]
  },

  // capture audit 2026-11-19: this form created a charge with no invoice that
  // then blocked the real cycle (one charge per subscription and period). A
  // cycle is billed by a billing run; the form opens an existing charge.
  'M39-form-schedule': { kind: 'model_form', model: 'fix.subscription.charge', create: false,
    title: 'Cycle Charge', back: 'M39-runs',
    // A04 build (2026-11-04): the usage readings billed on this cycle (locked).
    lines: {
      field: 'usage_ids',
      title: 'Usage billed on this cycle',
      note: 'The overage of each reading is added to the cycle charge and the reading locks.',
      fields: [
        { name: 'metric', label: 'Metric', readonly: true },
        { name: 'period_start', label: 'From', readonly: true },
        { name: 'period_end', label: 'To', readonly: true },
        { name: 'quantity', label: 'Used', readonly: true },
        { name: 'committed', label: 'Committed', readonly: true },
        { name: 'overage_charge', label: 'Overage (BDT)', readonly: true }
      ]
    },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'audit', label: '6. System Audit', bn: '৬. সিস্টেম অডিট' },
      { id: 'docs', label: '7. Documents', bn: '৭. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'invoice_state', label: 'Invoice State', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'amount', label: 'Amount', required: true },
        { name: 'overage_amount', label: 'Usage Overage Billed', readonly: true },
        { name: 'invoice_due_date', label: 'Invoice Due', readonly: true },
        { name: 'days_past_due', label: 'Days Past Due', readonly: true },
        { name: 'composition', label: 'What This Charge Is Made Of', type: 'text', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'period_start', label: 'Period Start', required: true },
        { name: 'period_end', label: 'Period End', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'subscription_id', label: 'Subscription', required: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'currency_id', label: 'Currency', readonly: true },
        { name: 'invoice_id', label: 'Invoice', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M39-form-proration': {
    kind: 'model_form',
    model: 'fix.subscription.proration',
    title: 'Subscription Mid-Cycle Proration', newLabel: 'New Plan / Quantity Change',
    back: 'M39-plans',
    status: { field: 'state' },
    tabs: [
      { id: 'event_core', label: '1. Plan Change Event', bn: '১. প্ল্যান পরিবর্তন', icon: '🔄', badge: '3' },
      { id: 'tier_transition', label: '2. Plan / Quantity', bn: '২. প্ল্যান / পরিমাণ', icon: '', badge: '7' },
      { id: 'financial_effective', label: '3. Prorated Amount & Timing', bn: '৩. আনুপাতিক অর্থ ও সময়', icon: '💵', badge: '3' }
    ],
    sections: [
      { tab: 'event_core', title: 'Proration Identification', note: 'An upgrade/downgrade/cancellation proration under IFRS 15.',
        fields: [
          { name: 'name', required: true, label: 'Proration Reference' },
          { name: 'subscription_id', required: true, label: 'Subscription Master' },
          { name: 'change_type', required: true, label: 'Change Event Type' }
        ] },
      { tab: 'tier_transition', title: 'Plan Migration Mapping',
        note: 'A quantity change names a recurring charge line and its new quantity (FR-SUB-005/012).',
        fields: [
          { name: 'line_id', label: 'Charge Line (quantity change)' },
          { name: 'old_quantity', label: 'Quantity in Force', readonly: true },
          { name: 'new_quantity', label: 'New Quantity' },
          { name: 'from_plan', label: 'From Plan', readonly: true },
          { name: 'to_plan', label: 'To Plan' },
          { name: 'old_amount', label: 'Recurring Amount in Force', readonly: true },
          { name: 'new_amount', label: 'New Recurring Amount' }
        ] },
      { tab: 'financial_effective', title: 'Mid-Cycle Adjustment Value',
        note: 'Computed from the billed cycle: (new - old) x unused days / cycle days. A credit is approved under DOFA.',
        fields: [
          { name: 'amount', label: 'Net Adjustment Amount (BDT, computed)', readonly: true },
          { name: 'days_remaining', label: 'Unused Days of the Billed Cycle', readonly: true },
          { name: 'effective_date', required: true, label: 'Effective Cut-off Date' },
          { name: 'dofa_tier_required', label: 'DOFA Tier (credit)', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'state', label: 'Billing Settlement State', readonly: true },
          { name: 'billed_charge_id', label: 'Billed On Cycle', readonly: true }
        ] }
    ]
  },
  // capture audit 2026-11-19: the dunning ladder is run by the daily job on
  // unpaid cycle invoices; this form opened BLANK and created a subscription.
  'M39-form-dunning': { kind: 'model_form', model: 'fix.subscription', create: false,
    title: 'Dunning Step', back: 'M39-dunning',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'flags', label: '6. Status Flags', bn: '৬. অবস্থা নির্দেশক' },
      { id: 'audit', label: '7. System Audit', bn: '৭. সিস্টেম অডিট' },
      { id: 'docs', label: '8. Documents', bn: '৮. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Subscription', required: true },
        { name: 'plan', label: 'Plan', required: true },
        { name: 'billing_cycle', label: 'Billing Cycle', required: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'dunning_step', label: 'Dunning Step', readonly: true },
        { name: 'grace_period_days', label: 'Grace Period (days)' },
        { name: 'days_overdue', label: 'Days Overdue', readonly: true },
        { name: 'last_refund_earned', label: 'Earned at Cancellation', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'recurring_amount', label: 'Recurring Amount', required: true },
        { name: 'contract_value', label: 'Transaction Price' },
        { name: 'last_refund_amount', label: 'Last Refund (net)', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'start_date', label: 'Start Date', required: true },
        { name: 'next_invoice_date', label: 'Next Invoice Date', required: true },
        { name: 'contract_end_date', label: 'Contract End' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'customer_id', label: 'Customer', required: true },
        { name: 'contract_id', label: 'Contract' },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'refund_credit_note_id', label: 'Refund Credit Note', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit', required: true }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'consolidated', label: 'Consolidated' },
        { name: 'refund_requires_approval', label: 'Refund Needs Manager Approval', readonly: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (obligation_ids, charge_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  'M39-form-usage': { kind: 'model_form', model: 'fix.subscription.usage',
    title: 'Usage Reading', newLabel: 'Record Usage Reading', back: 'M39-usage',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'audit', label: '5. System Audit', bn: '৫. সিস্টেম অডিট' },
      { id: 'docs', label: '6. Documents', bn: '৬. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'line_id', label: 'Usage Tariff (sets metric, commitment and rate)' },
        { name: 'metric', label: 'Metric', required: true },
        { name: 'quantity', label: 'Used Quantity', required: true },
        { name: 'committed', label: 'Committed Quantity (no tariff only)', required: true },
        { name: 'overage_quantity', label: 'Overage (computed)', readonly: true },
        { name: 'source_module', label: 'Source', required: true },
        { name: 'source_key', label: 'Source Record Key (duplicates refused)' },
        { name: 'exception_cause', label: 'Why It Is Not Rated', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'overage_charge', label: 'Overage Charge (computed)', readonly: true },
        { name: 'overage_rate', label: 'Overage Rate (BDT/unit, no tariff only)' },
        { name: 'state', label: 'Billing State', readonly: true },
        { name: 'charge_id', label: 'Billed On', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'period_start', label: 'Period Start', required: true },
        { name: 'period_end', label: 'Period End', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'subscription_id', label: 'Subscription', required: true },
        { name: 'currency_id', label: 'Currency', readonly: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M39-form-autopay': { kind: 'model_form', model: 'fix.subscription.autopay',
    title: 'Autopay Mandate', newLabel: 'New Autopay Mandate', back: 'M39-autopay',
    // A04 build (2026-11-04): every collection request and the gateway's answer.
    lines: {
      field: 'attempt_ids',
      title: 'Collection attempts',
      note: 'Raised by the daily autopay job; the result is recorded by the payment gateway only.',
      fields: [
        { name: 'requested_at', label: 'Requested', readonly: true },
        { name: 'charge_id', label: 'Cycle Charge', readonly: true },
        { name: 'amount', label: 'Amount', readonly: true },
        { name: 'state', label: 'Result', readonly: true },
        { name: 'provider_ref', label: 'Provider Ref', readonly: true },
        { name: 'reason', label: 'Reason', readonly: true }
      ]
    },
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'method', label: 'Method', required: true },
        { name: 'mandate_ref', label: 'Mandate Reference' },
        { name: 'max_amount', label: 'Collection Limit (BDT)', required: true },
        { name: 'consent_channel', label: 'Consent Channel', required: true },
        { name: 'consent_phone', label: 'Consenting Phone' },
        { name: 'consent_signatory', label: 'Account Holder' },
        { name: 'consent_document_id', label: 'Signed Mandate Form' },
        { name: 'consent_at', label: 'Consent Recorded', readonly: true },
        { name: 'consent_evidence', label: 'Consent Evidence', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'last_result', label: 'Last Result', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'valid_from', label: 'Valid From' },
        { name: 'valid_until', label: 'Valid Until' },
        { name: 'last_attempt_at', label: 'Last Attempt', readonly: true },
        { name: 'failure_count', label: 'Failed Collections', readonly: true },
        { name: 'next_retry_on', label: 'Next Retry', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'subscription_id', label: 'Subscription', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  /* ---- capture audit 2026-11-19: the new capture forms ---- */
  'M39-form-billing-schedule': { kind: 'model_form', model: 'fix.subscription.schedule',
    title: 'Billing Schedule', newLabel: 'New Billing Schedule', back: 'M39-schedules',
    status: { field: 'state' },
    lines: {
      field: 'period_ids', fixedRows: true,
      title: 'Generated periods',
      note: 'Generated from the frequency, alignment and timing; billing bills them in order once the schedule is active.',
      fields: [
        { name: 'sequence', label: '#', readonly: true },
        { name: 'period_start', label: 'From', readonly: true },
        { name: 'period_end', label: 'To', readonly: true },
        { name: 'billing_date', label: 'Billed On', readonly: true },
        { name: 'amount_planned', label: 'Planned (BDT)', readonly: true },
        { name: 'explanation', label: 'Basis', readonly: true },
        { name: 'state', label: 'State', readonly: true }
      ]
    },
    sections: [
      { title: 'Schedule Terms', note: 'FR-SUB-002/003: anniversary or calendar alignment, billed in advance or in arrears; a partial first period is prorated by day or billed in full.',
        fields: [
          { name: 'subscription_id', label: 'Subscription', required: true },
          { name: 'billing_cycle', label: 'Frequency (from the subscription)', readonly: true },
          { name: 'alignment', label: 'Alignment', required: true },
          { name: 'timing', label: 'Timing', required: true },
          { name: 'first_period', label: 'Partial First Period', required: true },
          { name: 'anchor_date', label: 'First Period Starts', required: true },
          { name: 'horizon', label: 'Periods to Generate', required: true },
          { name: 'planned_total', label: 'Planned Total (BDT)', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'activated_by_id', label: 'Activated By', readonly: true }
        ] }
    ] },

  'M39-form-line': { kind: 'model_form', model: 'fix.subscription.line',
    title: 'Charge Line', newLabel: 'New Charge Line / Tariff', back: 'M39-lines',
    status: { field: 'state' },
    lines: {
      field: 'tier_ids',
      title: 'Rate bands (tiered / volume usage tariffs)',
      note: 'Bands start from 0 billable units (above the included quantity). Tiered: each band at its own rate; volume: every unit at the reached band.',
      fields: [
        { name: 'from_qty', label: 'From (billable units)', required: true },
        { name: 'rate', label: 'Rate (BDT/unit)', required: true }
      ]
    },
    tabs: [
      { id: 'charge', label: '1. Charge', bn: '১. চার্জ', icon: '💳' },
      { id: 'usage', label: '2. Usage Tariff', bn: '২. ব্যবহার ট্যারিফ', icon: '📈' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '🕑' }
    ],
    sections: [
      { tab: 'charge', title: 'Charge Line', note: 'FR-SUB-004/006: recurring (every cycle), one-time (next cycle, once) or usage. A second person approves it; a quantity change afterwards is a proration.',
        fields: [
          { name: 'subscription_id', label: 'Subscription', required: true },
          { name: 'name', label: 'Description', required: true },
          { name: 'charge_type', label: 'Charge Type', required: true },
          { name: 'quantity', label: 'Quantity (devices, sites, seats...)' },
          { name: 'unit_rate', label: 'Unit Rate per Cycle (BDT)' },
          { name: 'amount', label: 'Line Amount (computed)', readonly: true },
          { name: 'start_date', label: 'Starts', required: true },
          { name: 'end_date', label: 'Ends' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'billed_charge_id', label: 'Billed On (one-time)', readonly: true }
        ] },
      { tab: 'usage', title: 'Usage Rating Tariff', note: 'FR-SUB-024: usage above the included quantity is rated flat, tiered or by volume.',
        fields: [
          { name: 'metric', label: 'Metric (remote hours, GB, prints...)' },
          { name: 'included_qty', label: 'Included Quantity' },
          { name: 'rating_model', label: 'Rating Model' },
          { name: 'overage_rate', label: 'Flat Overage Rate (BDT/unit)' }
        ] },
    { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] }
    ] },

  'M39-form-billing-run': { kind: 'model_form', model: 'fix.subscription.billing.run',
    title: 'Billing Run', newLabel: 'New Billing Run', back: 'M39-billing-runs',
    status: { field: 'state' },
    lines: {
      field: 'unit_ids', fixedRows: true,
      title: 'Run units (one per subscription)',
      note: 'Filled by the dry run. Give every exception a disposition before review; commit bills each unit on its own and resumes after a failure.',
      fields: [
        { name: 'subscription_id', label: 'Subscription', readonly: true },
        { name: 'period_start', label: 'Cycle From', readonly: true },
        { name: 'amount', label: 'Amount (BDT)', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'detail', label: 'Exception', readonly: true },
        { name: 'disposition', label: 'Disposition' },
        { name: 'disposition_note', label: 'Note' },
        { name: 'charge_id', label: 'Charge', readonly: true }
      ]
    },
    sections: [
      { title: 'Run Scope', note: 'BRU-SUB-17: dry run first, reviewed by a Finance Manager who did not run it, then committed.',
        fields: [
          { name: 'name', label: 'Run', readonly: true },
          { name: 'company_id', label: 'Company', required: true },
          { name: 'as_of', label: 'Bill Cycles Due By', required: true },
          { name: 'billing_cycle', label: 'Cycle (optional)' },
          { name: 'operating_unit_id', label: 'Operating Unit (optional)' },
          { name: 'customer_id', label: 'Customer (optional)' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'unit_count', label: 'Units', readonly: true },
          { name: 'exception_count', label: 'Exceptions', readonly: true },
          { name: 'total_amount', label: 'Run Total (BDT)', readonly: true },
          { name: 'dry_run_by_id', label: 'Dry Run By', readonly: true },
          { name: 'reviewed_by_id', label: 'Reviewed By', readonly: true },
          { name: 'committed_at', label: 'Committed', readonly: true }
        ] }
    ] },

  'M39-form-adjustment': { kind: 'model_form', model: 'fix.subscription.adjustment',
    title: 'Credit / Adjustment', newLabel: 'New Credit / Adjustment', back: 'M39-adjustments',
    status: { field: 'state' },
    sections: [
      { title: 'Credit or Adjustment', note: 'FR-SUB-037 / BRU-SUB-11: approved (a credit under DOFA from the M63 inbox, never by its author) and applied to the next cycle charge.',
        fields: [
          { name: 'name', label: 'Reference', required: true },
          { name: 'subscription_id', label: 'Subscription', required: true },
          { name: 'charge_id', label: 'Cycle Concerned' },
          { name: 'adjustment_type', label: 'Type', required: true },
          { name: 'direction', label: 'Direction', required: true },
          { name: 'amount', label: 'Amount (BDT)', required: true },
          { name: 'reason', label: 'Reason', type: 'text', required: true },
          { name: 'evidence_ref', label: 'Evidence (ticket, SLA report, dispute ref)' },
          { name: 'dofa_tier_required', label: 'DOFA Tier', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'applied_charge_id', label: 'Applied On Cycle', readonly: true }
        ] }
    ] },

  'M39-form-lifecycle': { kind: 'model_form', model: 'fix.subscription.lifecycle',
    title: 'Lifecycle Request', newLabel: 'Pause / Resume / Cancel / Renew', back: 'M39-lifecycle',
    status: { field: 'state' },
    tabs: [
      { id: 'request', label: '1. Request', bn: '১. অনুরোধ', icon: '📝' },
      { id: 'notice', label: '2. Notice & Renewal', bn: '২. নোটিশ ও নবায়ন', icon: '📨' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '🕑' }
    ],
    sections: [
      { tab: 'request', title: 'Lifecycle Change', note: 'A pause is approved by a Finance Manager, the others by a billing user; never by the requester. A future date takes effect on that date.',
        fields: [
          { name: 'subscription_id', label: 'Subscription', required: true },
          { name: 'action_type', label: 'Change', required: true },
          { name: 'effective_date', label: 'Effective Date', required: true },
          { name: 'pause_until', label: 'Paused Until (pause)' },
          { name: 'reason', label: 'Reason', type: 'text', required: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true }
        ] },
      { tab: 'notice', title: 'Notice Evidence', note: 'BRU-SUB-13: a cancellation honours the contract notice period. BRU-SUB-07: a renewal price escalation needs the customer told in advance, with channel and evidence.',
        fields: [
          { name: 'notice_received_on', label: 'Customer Notice Received (cancel)' },
          { name: 'renewal_end_date', label: 'New Term End (renew)' },
          { name: 'escalation_pct', label: 'Price Escalation % (renew)' },
          { name: 'notice_sent_on', label: 'Price Notice Sent On' },
          { name: 'notice_channel', label: 'Notice Channel' },
          { name: 'notice_evidence', label: 'Notice Evidence (ref / document)' },
          { name: 'notice_required_days', label: 'Notice Required (days)', readonly: true },
          { name: 'notice_ok', label: 'Notice Satisfied', readonly: true },
          { name: 'escalation_proration_id', label: 'Escalation Plan Change', readonly: true }
        ] },
    { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] }
    ] },

  'M39-form-churn': { kind: 'model_form', model: 'fix.subscription.churn',
    title: 'Churn Record', newLabel: 'Record Churn Reason', back: 'M39-churn',
    sections: [
      { title: 'Why the Customer Left', note: 'FR-SUB-042: logo churn is recorded once the subscription is cancelled; the lost MRR is stamped from its monthly value.',
        fields: [
          { name: 'subscription_id', label: 'Subscription', required: true },
          { name: 'churn_date', label: 'Churn Date', required: true },
          { name: 'churn_type', label: 'Churn Type', required: true },
          { name: 'reason_code', label: 'Reason', required: true },
          { name: 'competitor', label: 'Competitor (if moved)' },
          { name: 'notes', label: 'Notes', type: 'text' },
          { name: 'cohort', label: 'Start Cohort', readonly: true },
          { name: 'lost_mrr', label: 'Lost MRR (BDT)', readonly: true }
        ] }
    ] },

  /* computed pack that had no screen (closure 2026-10-28) */
  'M39-rpt-planmix': { kind: 'table_report', module: 'M39', report: 'plan_mix', title: "Plan Mix", period: false },
  // The "Usage vs Committed" chip routed here, but the screen was never
  // declared — a dead report link (A04 audit, 2026-11-01). The report has
  // always existed in controllers/a04/m39.py.
  'M39-rpt-usage': { kind: 'table_report', module: 'M39', report: 'usage_vs_committed', title: 'Usage vs Committed', period: false }
};

export const REPORT_ROUTES = {
  'M39:Plan Mix': 'M39-rpt-planmix',
  'M39:MRR Waterfall': 'M39-mrr',
  'M39:Churn & NRR Cohorts': 'M39-cohorts',
  'M39:Usage vs Committed': 'M39-rpt-usage',
  'M39:Billing Exception Log': 'M39-rpt-exceptions',
  'M39:Deferred Revenue Bridge': 'M39-rpt-deferred'
};

export const FORM_MODELS = {
  'M39:Subscription': 'fix.subscription',
  'M39:Billing Schedule': 'fix.subscription.schedule',
  'M39:Charge Line': 'fix.subscription.line',
  'M39:Plan Change': 'fix.subscription.proration',
  'M39:Usage Reading': 'fix.subscription.usage',
  'M39:Billing Run': 'fix.subscription.billing.run',
  'M39:Cycle Charge': 'fix.subscription.charge',
  'M39:Credit / Adjustment': 'fix.subscription.adjustment',
  'M39:Lifecycle Request': 'fix.subscription.lifecycle',
  'M39:Autopay Mandate': 'fix.subscription.autopay',
  'M39:Dunning Step': 'fix.subscription',
  'M39:Churn Record': 'fix.subscription.churn'
};

export const FORM_CHIPS = {
  'M39:Subscription': 'M39-record',
  'M39:Billing Schedule': 'M39-form-billing-schedule',
  'M39:Charge Line': 'M39-form-line',
  'M39:Plan Change': 'M39-form-proration',
  'M39:Usage Reading': 'M39-form-usage',
  'M39:Billing Run': 'M39-form-billing-run',
  'M39:Cycle Charge': 'M39-form-schedule',
  'M39:Credit / Adjustment': 'M39-form-adjustment',
  'M39:Lifecycle Request': 'M39-form-lifecycle',
  'M39:Autopay Mandate': 'M39-form-autopay',
  'M39:Dunning Step': 'M39-form-dunning',
  'M39:Churn Record': 'M39-form-churn',
  'M39:__by_model__': {
    'fix.subscription': 'M39-record',
    'fix.subscription.charge': 'M39-form-schedule',
    'fix.subscription.proration': 'M39-form-proration',
    'fix.subscription.autopay': 'M39-form-autopay',
    'fix.subscription.usage': 'M39-form-usage',
    'fix.subscription.schedule': 'M39-form-billing-schedule',
    'fix.subscription.line': 'M39-form-line',
    'fix.subscription.billing.run': 'M39-form-billing-run',
    'fix.subscription.adjustment': 'M39-form-adjustment',
    'fix.subscription.lifecycle': 'M39-form-lifecycle',
    'fix.subscription.churn': 'M39-form-churn'
  },
  'M39:__by_screen__': {
    'M39-subs': 'M39-record',
    'M39-runs': 'M39-form-schedule',
    'M39-plans': 'M39-form-proration',
    'M39-proration': 'M39-form-proration',
    'M39-usage': 'M39-form-usage',
    'M39-usage-exceptions': 'M39-form-usage',
    'M39-autopay': 'M39-form-autopay',
    'M39-dunning': 'M39-form-dunning',
    'M39-schedules': 'M39-form-billing-schedule',
    'M39-lines': 'M39-form-line',
    'M39-billing-runs': 'M39-form-billing-run',
    'M39-adjustments': 'M39-form-adjustment',
    'M39-lifecycle': 'M39-form-lifecycle',
    'M39-churn': 'M39-form-churn'
  }
};

export const CREATE = {
  M39: { screen: 'M39-record', model: 'fix.subscription', label: 'Subscription' }
};
