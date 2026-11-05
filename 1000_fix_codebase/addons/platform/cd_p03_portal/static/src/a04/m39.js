/** @odoo-module **/
/* A04 · Commercial & Revenue — M39 Subscriptions & Recurring (v2 rebuild).
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 92.
 * Subscriptions and charges are real; usage, proration and autopay are new.
 * MRR is the recorded recurring amount of live subscriptions; NRR is a
 * declared gap (no expansion/contraction history). */

export const MODULE = {
  area: 'A04', code: 'M39', en: 'Subscriptions & Recurring', title: 'M39 · Subscriptions & Recurring',
  bn: 'সাবস্ক্রিপশন ও রিকারিং', icon: '🔁',
  desc: 'Subscription object and plans, usage rating and overage, billing runs, proration, autopay and dunning, MRR movement, cohorts and the recurring forecast.',
  kpis: [
    { l: 'MRR', m: 'mrr', prefix: '৳ ' },
    { l: 'ARR', m: 'arr', prefix: '৳ ' },
    { l: 'NRR', m: 'nrr', suffix: '%' },
    { l: 'Churn (Logo)', m: 'churn_logo', suffix: '%' },
    { l: 'Billing Exceptions', m: 'billing_exceptions' },
    { l: 'Dunning in Progress', m: 'dunning_in_progress' }
  ],
  groups: [
    { en: 'Subscriptions', screens: [
      { id: 'M39-subs', en: 'Subscriptions', bn: 'সাবস্ক্রিপশন', t: 'g' },
      { id: 'M39-form-subscription', en: 'Subscription Record', bn: 'সাবস্ক্রিপশন রেকর্ড', t: 'f' },
      { id: 'M39-plans', en: 'Plan Changes', bn: 'প্ল্যান পরিবর্তন', t: 'g' }
    ]},
    { en: 'Rating & Billing', screens: [
      { id: 'M39-usage', en: 'Usage Rating', bn: 'ব্যবহার রেটিং', t: 'g' },
      { id: 'M39-runs', en: 'Billing Runs', bn: 'বিলিং রান', t: 'c' },
      { id: 'M39-proration', en: 'Proration Engine', bn: 'প্রোরেশন', t: 'c' }
    ]},
    { en: 'Payments', screens: [
      { id: 'M39-autopay', en: 'Autopay & Retry', bn: 'অটোপে', t: 'g' },
      { id: 'M39-dunning', en: 'Dunning Coordination', bn: 'ডানিং', t: 'g' }
    ]},
    { en: 'Metrics', screens: [
      { id: 'M39-mrr', en: 'MRR Movement', bn: 'এমআরআর', t: 'd' },
      { id: 'M39-cohorts', en: 'Cohort Analysis', bn: 'কোহোর্ট', t: 'r' },
      { id: 'M39-forecast', en: 'Recurring Forecast', bn: 'পূর্বাভাস', t: 'r' }
    ]}
  ],
  reports: ['MRR Waterfall', 'Churn & NRR Cohorts', 'Usage vs Committed', 'Billing Exception Log', 'Deferred Revenue Bridge', 'Plan Mix'],
  forms: ['Subscription', 'Billing Schedule', 'Plan Change', 'Dunning Step'],
  cross: ['M20 AR', 'M53 Rev-Rec', 'M08 Contracts'],
  freg: { src: 92, sub: [
    ['1', 'Subscription Object', 10, { model: 'fix.subscription', cols: ['name', 'customer_id', 'state', 'recurring_amount', 'next_invoice_date'], screens: ['M39-subs'] }],
    ['2', 'Billing Schedules', 9, { model: 'fix.subscription.charge', cols: ['subscription_id', 'customer_id', 'period_start', 'period_end', 'amount'], screens: ['M39-plans', 'M39-rpt-planmix', 'M39-runs'] }],
    ['3', 'Charge Models', 10, { model: 'fix.subscription.charge', cols: ['subscription_id', 'customer_id', 'amount', 'period_start', 'period_end', 'invoice_state'], screens: ['M39-runs'] }],
    ['4', 'Quantity & Proration', 12, { model: 'fix.subscription.proration', cols: ['name', 'state', 'subscription_id', 'amount', 'change_type', 'effective_date'], screens: ['M39-proration'] }],
    ['5', 'Usage Rating', 8, { model: 'fix.subscription.usage', cols: ['subscription_id', 'metric', 'quantity', 'committed', 'overage_quantity', 'overage_charge'], screens: ['M39-usage', 'M39-rpt-usage'] }],
    ['6', 'Billing Runs', 11, { model: 'fix.subscription.charge', cols: ['subscription_id', 'customer_id', 'amount', 'period_start', 'period_end', 'invoice_state'], screens: ['M39-runs', 'M39-rpt-deferred'] }],
    ['7', 'Credits & Adjustments', 7, { model: 'fix.subscription.proration', cols: ['name', 'subscription_id', 'change_type', 'amount', 'state'], screens: ['M39-rpt-exceptions', 'M39-proration'] }],
    ['8', 'Suspend / Cancel / Renew', 9, { model: 'fix.subscription', cols: ['name', 'customer_id', 'state', 'recurring_amount', 'next_invoice_date'], screens: ['M39-subs'] }],
    ['9', 'Autopay & Dunning', 8, { model: 'fix.subscription.autopay', cols: ['subscription_id', 'state', 'method', 'mandate_ref', 'last_attempt_at', 'last_result'], screens: ['M39-autopay', 'M39-dunning'] }],
    ['10', 'Metrics & Forecast', 8, { model: 'fix.subscription', cols: ['name', 'plan', 'recurring_amount', 'state', 'start_date'], screens: ['M39-mrr', 'M39-cohorts', 'M39-forecast', 'M39-subs'] }]
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
  'M39-usage': { kind: 'model_list', model: 'fix.subscription.usage', create: false,
    cols: ["subscription_id", "currency_id", "create_date", "period_start", "period_end", "metric", "quantity", "overage_charge", "state", "charge_id"] },
  'M39-runs': { kind: 'model_list', model: 'fix.subscription.charge', create: false,
    cols: ["customer_id", "subscription_id", "amount", "overage_amount", "currency_id", "create_date", "invoice_state", "days_past_due", "company_id", "operating_unit_id"] },
  'M39-proration': { kind: 'model_list', model: 'fix.subscription.proration', create: false,
    stateField: 'state',
    cols: ["name", "subscription_id", "state", "old_amount", "new_amount", "amount", "currency_id", "create_date", "change_type", "approval_state"],
    actions: [
      { m: 'action_request_approval', l: 'Submit Plan Change for Approval', states: ['draft'], ask: 'Business justification (mandatory from Tier 2)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['pending'] },
      { m: 'action_void', l: 'Void', states: ['draft', 'pending'] }
    ] },
  'M39-autopay': { kind: 'model_list', model: 'fix.subscription.autopay', create: false,
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


  /* Report screens */
  'M39-rpt-exceptions': { kind: 'table_report', module: 'M39', report: 'billing_exception_log', title: 'Billing Exception Log', period: false },
  'M39-rpt-deferred': { kind: 'table_report', module: 'M39', report: 'deferred_revenue_bridge', title: 'Deferred Revenue Bridge', period: false },

  'M39-subs': { kind: 'model_list', model: 'fix.subscription', stateField: 'state',
    cols: ['name', 'customer_id', 'plan', 'billing_cycle', 'recurring_amount', 'next_invoice_date', 'state'] },
  'M39-form-subscription': {

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
          { name: 'dunning_step', required: true, label: 'Current Dunning Stage' },
          { name: 'days_overdue', readonly: true, label: 'Days In Arrears' },
          { name: 'grace_period_days', label: 'Contractual Grace Period (Days)' }
        ] },
      { tab: 'vault', title: 'Subscription Mandate Vault',
        note: 'Customer autopay mandates, corporate master agreements, and billing exception waivers.',
        fields: [] }
    ]
  },

  'M39-form-schedule': { kind: 'model_form', model: 'fix.subscription.charge',
    title: 'Billing Schedule', back: 'M39-runs',
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
        { name: 'days_past_due', label: 'Days Past Due', readonly: true }
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
    title: 'Subscription Mid-Cycle Proration',
    back: 'M39-plans',
    status: { field: 'state' },
    tabs: [
      { id: 'event_core', label: '1. Plan Change Event', bn: '১. প্ল্যান পরিবর্তন', icon: '🔄', badge: '3' },
      { id: 'tier_transition', label: '2. Tier Transition', bn: '২. টিয়ার পরিবর্তন', icon: '📊', badge: '2' },
      { id: 'financial_effective', label: '3. Prorated Amount & Timing', bn: '৩. আনুপাতিক অর্থ ও সময়', icon: '💵', badge: '3' }
    ],
    sections: [
      { tab: 'event_core', title: 'Proration Identification', note: 'An upgrade/downgrade/cancellation proration under IFRS 15.',
        fields: [
          { name: 'name', required: true, label: 'Proration Reference' },
          { name: 'subscription_id', required: true, label: 'Subscription Master' },
          { name: 'change_type', required: true, label: 'Change Event Type' }
        ] },
      { tab: 'tier_transition', title: 'Plan Migration Mapping', fields: [
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
          { name: 'state', label: 'Billing Settlement State', readonly: true }
        ] }
    ]
  },
  'M39-form-dunning': { kind: 'model_form', model: 'fix.subscription',
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
    title: 'Usage Meter', back: 'M39-usage',
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
        { name: 'metric', label: 'Metric', required: true },
        { name: 'quantity', label: 'Used Quantity', required: true },
        { name: 'committed', label: 'Committed Quantity', required: true },
        { name: 'overage_quantity', label: 'Overage (computed)', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'overage_charge', label: 'Overage Charge (computed)', readonly: true },
        { name: 'overage_rate', label: 'Overage Rate (BDT/unit)' },
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
    title: 'Autopay Mandate', back: 'M39-autopay',
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
  'M39:Billing Schedule': 'fix.subscription.charge',
  'M39:Plan Change': 'fix.subscription.proration',
  'M39:Dunning Step': 'fix.subscription'
};

export const FORM_CHIPS = {
  'M39:Subscription': 'M39-form-subscription',
  'M39:Billing Schedule': 'M39-form-schedule',
  'M39:Plan Change': 'M39-form-proration',
  'M39:Dunning Step': 'M39-form-dunning',
  'M39:__by_model__': {
    'fix.subscription': 'M39-form-subscription',
    'fix.subscription.charge': 'M39-form-schedule',
    'fix.subscription.proration': 'M39-form-proration',
    'fix.subscription.autopay': 'M39-form-autopay',
    'fix.subscription.usage': 'M39-form-usage'
  },
  'M39:__by_screen__': {
    'M39-subs': 'M39-form-subscription',
    'M39-runs': 'M39-form-schedule',
    'M39-plans': 'M39-form-proration',
    'M39-usage': 'M39-form-usage',
    'M39-autopay': 'M39-form-autopay',
    'M39-dunning': 'M39-form-dunning'
  }
};

export const CREATE = {
  M39: { screen: 'M39-form-subscription', model: 'fix.subscription', label: 'Subscription' }
};
