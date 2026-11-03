/** @odoo-module **/
/* A03 · Customer Experience — M10 Loyalty & Rewards (v2 rebuild).
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 63.
 * All screens read the real fix.loyalty.* models; the programme is empty
 * until configured, and every empty state says so. */

export const MODULE = {
  area: 'A03', code: 'M10', en: 'Loyalty & Rewards', title: 'M10 · Loyalty & Rewards',
  bn: 'লয়্যালটি ও পুরস্কার', icon: '🎁',
  desc: 'Tiers and benefits, points ledger and wallet, vouchers, referrals, fraud controls, IFRS 15 points liability.',
  kpis: [
    { l: 'Members', m: 'members' },
    { l: 'Points Liability', m: 'points_liability', prefix: 'BDT ' },
    { l: 'Redemption MTD', m: 'redemption_mtd' },
    { l: 'Referral Conversions', m: 'referral_conversions' },
    { l: 'Breakage', m: 'breakage', suffix: '%' },
    { l: 'Tier Upgrades MTD', m: 'tier_upgrades_mtd' }
  ],
  groups: [
    { en: 'Programme', screens: [
      { id: 'M10-programmes', en: 'Loyalty Programmes', bn: 'লয়্যালটি প্রোগ্রাম', t: 'g' },
      { id: 'M10-form-programme', en: 'Loyalty Programme Form', bn: 'প্রোগ্রাম ফর্ম', t: 'f' },
      { id: 'M10-tiers', en: 'Tiers & Benefits', bn: 'টিয়ার ও সুবিধা', t: 'g' },
      { id: 'M10-form-tier', en: 'Tier Configuration Form', bn: 'টিয়ার কনফিগ ফর্ম', t: 'f' },
      { id: 'M10-enrol', en: 'Enrolment & Upgrade', bn: 'এনরোলমেন্ট ও আপগ্রেড', t: 'g' },
      { id: 'M10-alliance', en: 'Alliance Benefits', bn: 'অ্যালায়েন্স সুবিধা', t: 'g' }
    ]},
    { en: 'Points & Wallet', screens: [
      { id: 'M10-ledger', en: 'Points Ledger', bn: 'পয়েন্ট লেজার', t: 'g' },
      { id: 'M10-wallet', en: 'Wallet & Credits', bn: 'ওয়ালেট', t: 'g' },
      { id: 'M10-redemption', en: 'Redemption Rules', bn: 'রিডেম্পশন নিয়ম', t: 'g' }
    ]},
    { en: 'Vouchers & Referrals', screens: [
      { id: 'M10-vouchers', en: 'Vouchers & Coupons', bn: 'ভাউচার', t: 'g' },
      { id: 'M10-hooks', en: 'Campaign Reward Hooks', bn: 'ক্যাম্পেইন হুক', t: 'g' },
      { id: 'M10-referral', en: 'Referral Programme', bn: 'রেফারেল কর্মসূচি', t: 'g' },
      { id: 'M10-fraud', en: 'Fraud Controls', bn: 'প্রতারণা নিয়ন্ত্রণ', t: 'g' }
    ]},
    { en: 'Finance', screens: [
      { id: 'M10-liability', en: 'Liability & Breakage (IFRS 15)', bn: 'দায় ও ব্রেকেজ', t: 'r' },
      { id: 'M10-profit', en: 'Programme Profitability', bn: 'কর্মসূচির লাভজনকতা', t: 'r' }
    ]},
    { en: 'Schemes & Earn Rules', bn: 'স্কিম ও আর্ন রুল', screens: [
      { id: 'M10-schemes', en: 'Loyalty Schemes', bn: 'লয়্যালটি স্কিম', t: 'g' },
      { id: 'M10-form-scheme', en: 'Loyalty Scheme', bn: 'স্কিম ফর্ম', t: 'f' },
      { id: 'M10-burn-rules', en: 'Redemption Rules', bn: 'রিডেম্পশন রুল', t: 'g' },
      { id: 'M10-point-types', en: 'Point Types', bn: 'পয়েন্ট ধরন', t: 'g' }
    ]},
    { en: 'Affiliations & Cards', bn: 'অ্যাফিলিয়েশন ও কার্ড', screens: [
      { id: 'M10-affiliations', en: 'Affiliations', bn: 'অ্যাফিলিয়েশন', t: 'g' },
      { id: 'M10-form-affiliation', en: 'Affiliation', bn: 'অ্যাফিলিয়েশন ফর্ম', t: 'f' },
      { id: 'M10-cards', en: 'Loyalty Cards', bn: 'লয়্যালটি কার্ড', t: 'g' }
    ]}
  ],
  reports: ['Member Growth & Tier Mix', 'Points Earn/Burn Analysis', 'Referral Funnel', 'Voucher Usage & Fraud', 'Programme P&L'],
  forms: ['Loyalty Programme', 'Tier Configuration', 'Voucher Campaign', 'Points Adjustment', 'Referral Code', 'Loyalty Scheme', 'Loyalty Affiliation'],
  cross: ['M33 Customer Master', 'M20 AR &Invoicing', 'M07 CRM'],
  freg: { src: 63, sub: [
    ['1', 'Tiers & Enrolment', 10, { model: 'fix.loyalty.tier', cols: ['name', 'code', 'sequence', 'min_points_threshold', 'min_spend_bdt'], screens: ['M10-tiers', 'M10-enrol'] }],
    ['2', 'Benefit Engine', 9, { model: 'fix.loyalty.program', cols: ['name', 'code', 'active', 'name_bn', 'description', 'points_per_bdt'], screens: ['M10-programmes'] }],
    ['3', 'Points Ledger', 9, { model: 'fix.loyalty.ledger', cols: ['partner_id', 'transaction_type', 'points', 'balance_after', 'state'], screens: ['M10-ledger', 'M10-rpt-earnburn'] }],
    ['4', 'Wallet', 7, { model: 'fix.loyalty.account', cols: ['name', 'partner_id', 'state'], screens: ['M10-wallet'] }],
    ['5', 'Vouchers & Coupons', 9, { model: 'fix.loyalty.voucher', cols: ['name', 'partner_id', 'state', 'discount_type', 'discount_value', 'valid_until'], screens: ['M10-vouchers', 'M10-rpt-voucher'] }],
    ['6', 'Referrals', 7, { model: 'fix.loyalty.referral.code', cols: ['name', 'state', 'program_id', 'referrer_partner_id', 'referee_partner_id', 'points_awarded'], screens: ['M10-referral', 'M10-rpt-referral'] }],
    ['7', 'Alliance Benefits', 5, { model: 'fix.loyalty.tier', cols: ['name', 'code', 'points_multiplier'], screens: ['M10-alliance'] }],
    ['8', 'Liability & Breakage', 7, { model: 'fix.loyalty.account', cols: ['name', 'partner_id', 'points_balance', 'lifetime_points_earned', 'lifetime_points_redeemed'], screens: ['M10-liability', 'M10-profit', 'M10-rpt-pnl', 'M10-wallet'] }]
  ] }
};

export const SCREENS = {
  'M10-tiers': { kind: 'model_list', model: 'fix.loyalty.tier', stateField: 'active',
    cols: ['code', 'name', 'min_points_threshold', 'min_spend_bdt', 'points_multiplier',
      'labour_discount_pct', 'parts_discount_pct', 'active'] },
  'M10-enrol': { kind: 'model_list', model: 'fix.loyalty.account', stateField: 'state',
    cols: ['name', 'partner_id', 'program_id', 'tier_id', 'points_balance', 'state', 'approval_state', 'enrollment_date'],
    actions: [
      /* A03 R7: a fraud-lock release is decided by a DOFA Tier 2 approver
       * from the M63 inbox; this only asks for it. */
      { m: 'action_request_approval', l: 'Request Fraud-Lock Release (Tier 2)', ask: 'What did the investigation find?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Release Request' },
      { m: 'action_suspend', l: 'Suspend' },
      { m: 'action_activate', l: 'Re-activate' },
      { m: 'action_reconcile_balance', l: 'Reconcile Balance with Ledger' }
    ] },
  'M10-alliance': { kind: 'model_list', model: 'fix.loyalty.tier', stateField: 'active',
    domain: [['active', '=', true]],
    cols: ['name', 'dedicated_support', 'priority_diagnostic', 'labour_discount_pct',
      'parts_discount_pct'] },
  'M10-ledger': { kind: 'model_list', model: 'fix.loyalty.ledger', stateField: 'state',
    cols: ['transaction_type', 'points', 'balance_after', 'order_amount_bdt', 'expiry_date',
      'state', 'approval_state', 'notes'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_post', l: 'Post Ledger Line' },
      { m: 'action_reverse', l: 'Reverse Line', ask: 'Why is this posted line being reversed?', kwarg: 'reason' }
    ] },
  'M10-wallet': { kind: 'model_list', model: 'fix.loyalty.account', stateField: 'state',
    domain: [['points_balance', '>', 0]],
    cols: ['partner_id', 'tier_id', 'points_balance', 'lifetime_spend_bdt', 'tier_upgraded_date'] },
  'M10-redemption': { kind: 'table_report', module: 'M10', report: 'redemption_rules', title: 'Redemption Rules', period: false },
  'M10-vouchers': { kind: 'model_list', create: false, model: 'fix.loyalty.voucher', stateField: 'state',
    cols: ['name', 'partner_id', 'discount_type', 'discount_value', 'valid_from', 'state'] },
  'M10-hooks': { kind: 'model_list', model: 'fix.loyalty.campaign.hook', stateField: 'state',
    cols: ['name', 'campaign_id', 'program_id', 'reward_type', 'bonus_points', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Hook' },
      { m: 'action_complete', l: 'Complete Hook' }
    ],
    note: 'A hook goes live only on a running campaign; its reward terms are then fixed (A03 audit M10-8).' },
  'M10-referral': { kind: 'model_list', model: 'fix.loyalty.referral.code', stateField: 'state',
    cols: ['name', 'referrer_partner_id', 'referee_partner_id', 'state', 'points_awarded', 'converted_at'],
    actions: [{ m: 'action_mark_converted', l: 'Mark Converted' }] },
  'M10-fraud': { kind: 'table_report', module: 'M10', report: 'fraud_controls', title: 'Fraud Controls', period: false },
  'M10-liability': { kind: 'table_report', module: 'M10', report: 'points_liability', title: 'Liability & Breakage (IFRS 15)', period: false },
  'M10-profit': { kind: 'table_report', module: 'M10', report: 'programme_profitability', title: 'Programme Profitability', period: false },

  /* Report chips -> their own computed packs */
  'M10-rpt-growth': { kind: 'table_report', module: 'M10', report: 'member_growth_tier_mix', title: 'Member Growth & Tier Mix', period: false },
  'M10-rpt-earnburn': { kind: 'table_report', module: 'M10', report: 'earn_burn', title: 'Points Earn/Burn Analysis', period: false },
  'M10-rpt-referral': { kind: 'table_report', module: 'M10', report: 'referral_funnel', title: 'Referral Funnel', period: false },
  'M10-rpt-voucher': { kind: 'table_report', module: 'M10', report: 'voucher_usage_fraud', title: 'Voucher Usage & Fraud', period: false },
  'M10-rpt-pnl': { kind: 'table_report', module: 'M10', report: 'programme_profitability', title: 'Programme P&L', period: false },

  /* Programme bootstrap (extra): the programme must exist before tiers/accounts */
  'M10-programmes': { kind: 'model_list', model: 'fix.loyalty.program', stateField: 'active',
    cols: ['code', 'name', 'points_per_bdt', 'bdt_per_point', 'min_points_to_redeem',
      'expiry_months', 'account_count', 'active'] },

  /* ============ D365 IN-WORKSPACE MULTI-TAB FORMS ============ */
  'M10-form-tier': {
    kind: 'model_form',
    model: 'fix.loyalty.tier',
    title: 'Tier Configuration',
    back: 'M10-tiers',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'general', label: 'Tier Definition', bn: 'টিয়ার বিবরণ', icon: '🏷️' },
      { id: 'benefits', label: 'Benefits & Privileges', bn: 'সুবিধা ও ছাড়', icon: '🎁' },
      { id: 'audit', label: 'Audit & Governance', bn: 'অডিট ও পরিচালনা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Tier Definition',
        note: 'A tier is a qualification threshold plus its benefits. The benefit engine reads these values when a member’s balance or spend crosses the threshold.',
        fields: [
          { name: 'name', required: true, label: 'Tier Name' },
          { name: 'code', required: true, label: 'Tier Code' },
          { name: 'program_id', required: true, label: 'Programme' },
          { name: 'sequence', label: 'Sequence' },
          { name: 'min_points_threshold', label: 'Minimum Points' },
          { name: 'min_spend_bdt', label: 'Minimum Spend (BDT)' },
          { name: 'points_multiplier', label: 'Points Multiplier' }
        ]
      },
      {
        tab: 'benefits',
        title: 'Benefits & Privileges',
        note: 'Discounts and service privileges automatically applied across counter, workshop, and field repair orders.',
        fields: [
          { name: 'labour_discount_pct', label: 'Labour Discount %' },
          { name: 'parts_discount_pct', label: 'Parts Discount %' },
          { name: 'dedicated_support', label: 'Dedicated Support Line' },
          { name: 'priority_diagnostic', label: 'Priority Diagnostic' }
        ]
      },
      {
        tab: 'audit',
        title: 'Audit & Governance',
        fields: [
          { name: 'active', label: 'Active Status' }
        ]
      }
    ]
  },

  'M10-form-voucher-campaign': {
    kind: 'model_form',
    model: 'fix.loyalty.campaign.hook',
    title: 'Voucher Campaign',
    back: 'M10-vouchers',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', completed: 'Completed' } },
    tabs: [
      { id: 'general', label: 'Campaign Hook', bn: 'ক্যাম্পেইন হুক', icon: '🎯' },
      { id: 'terms', label: 'Voucher Terms', bn: 'ভাউচার শর্তাবলী', icon: '🎟️' },
      { id: 'audit', label: 'State & Governance', bn: 'অবস্থা ও পরিচালনা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Campaign Hook',
        note: 'A hook binds a marketing campaign to a loyalty reward. Voucher issuance needs a real fix.campaign record (M35 owns the campaign).',
        fields: [
          { name: 'name', required: true, label: 'Hook Description' },
          { name: 'campaign_id', required: true, label: 'Marketing Campaign' },
          { name: 'program_id', required: true, label: 'Target Programme' },
          { name: 'reward_type', required: true, label: 'Reward Type' },
          { name: 'bonus_points', label: 'Bonus Points' }
        ]
      },
      {
        tab: 'terms',
        title: 'Voucher Terms',
        note: 'Discount parameters and validity window applied during checkout redemption.',
        fields: [
          { name: 'voucher_discount_type', label: 'Voucher Discount Type' },
          { name: 'voucher_discount_value', label: 'Voucher Discount Value' },
          { name: 'voucher_validity_days', label: 'Validity (days)' }
        ]
      },
      {
        tab: 'audit',
        title: 'State & Governance',
        fields: [
          { name: 'state', readonly: true, label: 'Lifecycle State' }
        ]
      }
    ]
  },

  'M10-form-adjustment': {
    kind: 'model_form',
    model: 'fix.loyalty.ledger',
    title: 'Points Adjustment',
    back: 'M10-ledger',
    status: { field: 'state', labels: { draft: 'Draft', posted: 'Posted', reversed: 'Reversed' } },
    tabs: [
      { id: 'general', label: 'Points Adjustment', bn: 'পয়েন্ট সমন্বয়', icon: '⚖️' },
      { id: 'approval', label: 'DOFA & Narration', bn: 'অনুমোদন ও বিবরণ', icon: '✍️' },
      { id: 'audit', label: 'Ledger Audit', bn: 'লেজার অডিট', icon: '📊' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Adjustment Details',
        note: 'A manual adjustment is a signed ledger line (negative removes points). It stays DRAFT until posted from the ledger. Posting recalculates the wallet and re-evaluates the tier.',
        fields: [
          { name: 'account_id', required: true, label: 'Loyalty Account' },
          { name: 'transaction_type', required: true, label: 'Transaction Type' },
          { name: 'points', required: true, label: 'Points (signed)' },
          { name: 'service_order_id', label: 'Service Order Reference' },
          { name: 'order_amount_bdt', label: 'Order Amount (BDT)' },
          { name: 'expiry_date', label: 'Points Expiry Date' }
        ]
      },
      {
        tab: 'approval',
        title: 'Narration & DOFA Approval',
        note: 'Every adjustment carries its reason. Manual point adjustments exceeding 500 points strictly require supervisor DOFA approval and justification.',
        fields: [
          { name: 'justification', label: 'DOFA Adjustment Justification' },
          { name: 'dofa_justification', label: 'DOFA Justification (mandatory at Tier 2+)', type: 'text' },
          { name: 'dofa_tier_required', readonly: true, label: 'DOFA Tier Required' },
          { name: 'dofa_approved', readonly: true, label: 'DOFA Approval Granted' },
          { name: 'dofa_approved_by', readonly: true, label: 'DOFA Approver' },
          { name: 'company_id', required: true, label: 'Operating Company' },
          { name: 'notes', label: 'Reason / Narration', type: 'text', required: true }
        ]
      },
      {
        tab: 'audit',
        title: 'Ledger Balance & Status',
        fields: [
          { name: 'state', readonly: true, label: 'Ledger State' },
          { name: 'balance_after', readonly: true, label: 'Balance After Posting' }
        ]
      }
    ]
  },

  'M10-form-referral': {
    kind: 'model_form',
    model: 'fix.loyalty.referral.code',
    title: 'Referral Code',
    back: 'M10-referral',
    status: { field: 'state', labels: { pending: 'Pending', converted: 'Converted', expired: 'Expired', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'general', label: 'Referral Definition', bn: 'রেফারেল বিবরণ', icon: '🔗' },
      { id: 'outcome', label: 'Conversion Outcome', bn: 'রূপান্তর ফলাফল', icon: '🏆' },
      { id: 'audit', label: 'Status & Governance', bn: 'অবস্থা ও অডিট', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Referral Parties',
        note: 'A code belongs to the referrer. Mark it converted when the referee’s first qualifying service posts; the points award is recorded on the ledger line.',
        fields: [
          { name: 'name', required: true, label: 'Referral Code' },
          { name: 'program_id', required: true, label: 'Programme' },
          { name: 'referrer_partner_id', required: true, label: 'Referrer' },
          { name: 'referee_partner_id', label: 'Referred Customer' },
          { name: 'note', label: 'Note' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Conversion Outcome',
        fields: [
          { name: 'points_awarded', readonly: true, label: 'Points Awarded' },
          { name: 'converted_at', readonly: true, label: 'Converted At' }
        ]
      },
      {
        tab: 'audit',
        title: 'Referral Status',
        fields: [
          { name: 'state', readonly: true, label: 'Status' }
        ]
      }
    ]
  },

  'M10-form-programme': {
    lines: {
      field: 'tier_ids',
      title: 'Programme Tiers',
      note: 'The tiers a member can reach, and what each one earns them.',
      fields: [
        { name: 'name', label: 'Tier', required: true },
        { name: 'code', label: 'Code' },
        { name: 'sequence', label: 'Order' },
        { name: 'min_points_threshold', label: 'Min Points' },
        { name: 'min_spend_bdt', label: 'Min Spend (BDT)' },
        { name: 'points_multiplier', label: 'Points x' },
        { name: 'labour_discount_pct', label: 'Labour Disc %' },
        { name: 'parts_discount_pct', label: 'Parts Disc %' }
      ]
    }, kind: 'model_form', model: 'fix.loyalty.program',
    title: 'Loyalty & Rewards Programme Master', back: 'M10-programmes',
    tabs: [
      { id: 'general', label: '1. Identity & Branding', bn: '১. পরিচয়', icon: '👑', badge: '6' },
      { id: 'economics', label: '2. Earn & Burn Economics', bn: '২. অর্থনীতি', icon: '💰', badge: '6' },
      { id: 'tiers', label: '3. Configured Tiers', bn: '৩. টিয়ার', icon: '🏷️', badge: '2' },
      { id: 'expiry', label: '4. Expiry & FIFO Breakage', bn: '৪. মেয়াদ নীতি', icon: '⏳', badge: '2' },
      { id: 'liability', label: '5. IFRS 15 Points Liability', bn: '৫. আইএফআরএস ১৫ দায়', icon: '📊', badge: '3' },
      { id: 'audit', label: '6. Governance & Audit', bn: '৬. গভর্নেন্স', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Programme Identity & Operating Scope', fields: [
        { name: 'code', required: true, label: 'Programme Code' },
        { name: 'name', required: true, label: 'Programme Name (English)' },
        { name: 'name_bn', label: 'Programme Name (Bengali)' },
        { name: 'description', label: 'Programme Terms & Summary', type: 'text' },
        { name: 'operating_unit_id', label: 'Operating Unit' },
        { name: 'company_id', label: 'Operating Corporate Legal Entity' },
      ]},
      { tab: 'economics', title: 'Points Valuation & Redemption Thresholds', fields: [
        { name: 'points_per_bdt', required: true, label: 'Points Earned per BDT 100 Spent' },
        { name: 'bdt_per_point', required: true, label: 'BDT Monetary Value per Point' },
        { name: 'min_points_to_redeem', required: true, label: 'Minimum Redeemable Points Threshold' },
        { name: 'active', label: 'Programme Active Operational Status' },
        { name: 'referral_referrer_points', label: 'Referral Award to Referrer (points, DOFA Tier 3)' },
        { name: 'referral_referee_points', label: 'Referral Award to New Customer (points, DOFA Tier 3)' },
      ]},
      { tab: 'tiers', title: 'Configured Member Tiers & Progression Levels', fields: [
        { name: 'tier_ids', label: 'Loyalty Tiers' },
      ]},
      { tab: 'expiry', title: 'Statutory 365-Day FIFO Forfeiture Policy (FLAW-10.2)',
        note: 'Points operate on an immutable 365-day First-In-First-Out (FIFO) validity ledger. Unredeemed points automatically forfeit upon reaching the annual maturity deadline.',
        fields: [
          { name: 'expiry_months', required: true, label: 'Point Expiration Period (Months)' },
        ]},
      { tab: 'liability', title: 'IFRS 15 Deferred Revenue & Breakage Accounting',
        note: 'IFRS 15 mandates treating loyalty points as a separate performance obligation. Unredeemed points are recognized as contract liability on the general ledger, net of the breakage Finance expects. Expected breakage is a Finance ruling (DOFA Tier 3); 0 reports the full gross liability.',
        fields: [
          { name: 'expected_breakage_pct', label: 'Expected Breakage % (IFRS 15, Finance ruling)' },
          { name: 'account_count', label: 'Total Enrolled Member Accounts', readonly: true },
          { name: 'account_ids', label: 'Enrolled Member Account Records', readonly: true },
        ]},
      { tab: 'audit', title: 'System Governance & Administrative Audit Trail', fields: [
        { name: 'create_date', label: 'Programme Launch Date', readonly: true },
        { name: 'write_date', label: 'Last Terms Modification', readonly: true },
      ]}
    ] },

  'M10-form-account': {
    lines: {
      field: 'ledger_ids',
      title: 'Points Ledger',
      note: 'Every points movement on this membership. The balance after each transaction is carried on the row, so a disputed balance can be traced rather than recomputed.',
      fields: [
        { name: 'transaction_type', label: 'Type', required: true },
        { name: 'points', label: 'Points', required: true },
        { name: 'balance_after', label: 'Balance After', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'dofa_tier_required', label: 'DOFA Tier', readonly: true },
        { name: 'dofa_approved', label: 'Approved', readonly: true }
      ]
    },
    kind: 'model_form',
    model: 'fix.loyalty.account',
    title: 'Loyalty Enrolment',
    back: 'M10-enrol',
    status: { field: 'state', labels: { active: 'Active', frozen: 'Frozen — Fraud Review', suspended: 'Suspended', closed: 'Closed' } },
    tabs: [
      { id: 'general', label: 'Member Enrolment', bn: 'সদস্য অন্তর্ভুক্তি', icon: '👤' },
      { id: 'wallet', label: 'Points Wallet', bn: 'পয়েন্ট ওয়ালেট', icon: '💳' },
      { id: 'docs', label: 'Terms & Documents', bn: 'শর্তাবলী ও নথি', icon: '📑' },
      { id: 'audit', label: 'Status & Governance', bn: 'অবস্থা ও পরিচালনা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Member Enrolment',
        note: 'One account per member per programme. The wallet balance only moves through POSTED ledger lines.',
        fields: [
          { name: 'partner_id', required: true, label: 'Customer' },
          { name: 'program_id', required: true, label: 'Programme' },
          { name: 'tier_id', label: 'Current Tier' },
          { name: 'enrollment_date', label: 'Enrolment Date' },
          { name: 'state', readonly: true, label: 'Account State' }
        ]
      },
      {
        tab: 'wallet',
        title: 'Points Wallet Ledger',
        note: 'Live balances and lifetime transactional totals compiled from posted ledger entries.',
        fields: [
          { name: 'points_balance', readonly: true, label: 'Current Points Balance' },
          { name: 'lifetime_points_earned', readonly: true, label: 'Lifetime Points Earned' },
          { name: 'lifetime_points_redeemed', readonly: true, label: 'Lifetime Points Redeemed' },
          { name: 'lifetime_spend_bdt', readonly: true, label: 'Lifetime Spend (BDT)' },
          { name: 'balance_reconciled_at', readonly: true, label: 'Balance Last Reconciled' },
          { name: 'balance_drift', readonly: true, label: 'Drift Found at Reconciliation' }
        ]
      },
      {
        tab: 'docs',
        title: 'Terms, Conditions & Member Documents',
        note: 'Programme terms of service and tier rules live on the Programme master (M10 Programmes form — Expiry Policy tab). Manual credit approvals (>500 pts) attach their DOFA justification to the adjustment ledger line; the checksummed repository (fix.document, M24) is the estate-wide archive — a direct wallet→document relation is a declared platform gap.',
        fields: [
          { name: 'program_id', label: 'Governing Programme Terms (M10 Programmes)', readonly: true }
        ]
      },
      {
        tab: 'audit',
        title: 'Governance & Tracking',
        fields: [
          { name: 'tier_upgraded_date', readonly: true, label: 'Last Tier Upgrade Date' },
          { name: 'freeze_reason', readonly: true, label: 'Fraud Freeze Reason' },
          { name: 'approval_state', readonly: true, label: 'Fraud-Lock Release Approval' },
          { name: 'unlock_supervisor_id', readonly: true, label: 'Released By' }
        ]
      }
    ]
  },
  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M10-schemes': { kind: 'model_list', model: 'fix.loyalty.scheme', create: true,
    cols: ['sequence', 'name', 'code', 'program_id', 'state', 'valid_from', 'valid_until', 'estimated_annual_cost', 'dofa_tier_required', 'approval_state', 'dofa_approved'],
    stateField: 'state',
    actions: [
      { m: 'action_request_approval', l: 'Request Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_retire', l: 'Retire' }
    ],
    note: 'Earn and burn rules, evaluated first-match-wins. Activation is a marketing DOFA decision.' },
  'M10-form-scheme': {
    lines: {
      field: 'earn_rule_ids',
      title: 'Earn Rules',
      note: 'Evaluated in priority order, first match wins. The optional tier makes \'Gold earns on parts and Silver does not\' expressible — without it the engine would need rebuilding the first time marketing asked.',
      fields: [
        { name: 'priority', label: 'Order' },
        { name: 'name', label: 'Rule', required: true },
        { name: 'dimension', label: 'Keyed On', required: true },
        { name: 'dimension_value', label: 'Value' },
        { name: 'tier_id', label: 'Tier' },
        { name: 'affiliation_id', label: 'Affiliation' },
        { name: 'point_type_id', label: 'Awards' },
        { name: 'points_per_bdt', label: 'Points per BDT', required: true },
        { name: 'bonus_multiplier', label: 'Bonus' },
        { name: 'excluded', label: 'Earns Nothing' },
        { name: 'active', label: 'Active' }
      ]
    },
    kind: 'model_form', model: 'fix.loyalty.scheme',
    title: 'Loyalty Scheme', back: 'M10-schemes',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'identity', label: '1. Scheme', bn: '১. স্কিম', icon: '🎁' },
      { id: 'validity', label: '2. Validity', bn: '২. মেয়াদ', icon: '📅' },
      { id: 'governance', label: '3. DOFA Approval', bn: '৩. ডোফা অনুমোদন', icon: '⚖️' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Scheme Identity',
        note: 'One float could express only \'everybody earns the same rate on everything\'. A scheme holds earn and burn rules that differ by tier, by affiliation, by category and by channel.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'code', label: 'Code', required: true },
        { name: 'program_id', label: 'Programme', required: true },
        { name: 'sequence', label: 'Priority' },
        { name: 'state', label: 'State', readonly: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'validity',
        title: 'When It Applies',
        fields: [
        { name: 'valid_from', label: 'Valid From' },
        { name: 'valid_until', label: 'Valid Until' }
        ]
      },
      {
        tab: 'governance',
        title: 'Commercial Sign-Off',
        note: 'Activating a scheme changes what every future transaction costs the business, so it carries the same DOFA ladder as the campaign budget it competes with for money.',
        fields: [
        { name: 'estimated_annual_cost', label: 'Estimated Annual Cost (BDT)' },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'dofa_tier_required', label: 'Tier Required', readonly: true },
        { name: 'approval_state', label: 'Approval', readonly: true },
        { name: 'dofa_approved', label: 'Approved', readonly: true },
        { name: 'dofa_approved_by', label: 'Approver', readonly: true },
        { name: 'dofa_approved_at', label: 'Approved At', readonly: true },
        { name: 'dofa_justification', label: 'Justification' }
        ]
      }
    ]
  },
  'M10-burn-rules': { kind: 'model_list', model: 'fix.loyalty.burn.rule', create: true,
    cols: ['scheme_id', 'priority', 'name', 'dimension', 'dimension_value', 'tier_id', 'affiliation_id', 'min_points', 'max_discount_pct', 'blocked', 'active'],
    note: 'Redemption rules differ by tier and by affiliation, which a single programme-wide minimum cannot express.' },
  'M10-point-types': { kind: 'model_list', model: 'fix.loyalty.point.type', create: true,
    cols: ['sequence', 'name', 'name_bn', 'code', 'program_id', 'point_class', 'bdt_per_point', 'expiry_months', 'active'],
    note: 'A qualifying point moves a member up the ladder and can never be spent, which is what decouples tier marketing from the IFRS-15 liability.' },
  'M10-affiliations': { kind: 'model_list', model: 'fix.loyalty.affiliation', create: true,
    cols: ['name', 'name_bn', 'code', 'program_id', 'member_count', 'active'],
    note: 'Cohort reward rates without inflating the tier ladder — AMC staff, dealer technicians, campaign cohorts.' },
  'M10-form-affiliation': {
    lines: {
      field: 'member_ids',
      title: 'Cohort Members',
      note: 'Affiliations are a commercial decision, so each membership records whose.',
      fields: [
        { name: 'account_id', label: 'Loyalty Account', required: true },
        { name: 'joined_at', label: 'Joined' },
        { name: 'reason', label: 'Why They Qualify' },
        { name: 'active', label: 'Active' }
      ]
    },
    kind: 'model_form', model: 'fix.loyalty.affiliation',
    title: 'Loyalty Affiliation', back: 'M10-affiliations',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'identity', label: '1. Cohort', bn: '১. কোহর্ট', icon: '👥' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Cohort Definition',
        note: 'Affiliations differentiate rewards for a group WITHOUT inflating the tier ladder. Without them every such request becomes a new tier and the ladder degrades into a list of special cases.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'code', label: 'Code', required: true },
        { name: 'program_id', label: 'Programme', required: true },
        { name: 'description', label: 'Description' },
        { name: 'member_count', label: 'Members' },
        { name: 'active', label: 'Active' }
        ]
      }
    ]
  },
  'M10-cards': { kind: 'model_list', model: 'fix.loyalty.card', create: true,
    cols: ['issued_on', 'card_number', 'barcode', 'account_id', 'card_type', 'state', 'expires_on', 'block_reason'],
    stateField: 'state',
    actions: [
      { m: 'action_block', l: 'Block Card' }
    ],
    note: 'Counter and wallet identity for a member.' },
};

export const REPORT_ROUTES = {
  'M10:Member Growth & Tier Mix': 'M10-rpt-growth',
  'M10:Points Earn/Burn Analysis': 'M10-rpt-earnburn',
  'M10:Referral Funnel': 'M10-rpt-referral',
  'M10:Voucher Usage & Fraud': 'M10-rpt-voucher',
  'M10:Programme P&L': 'M10-rpt-pnl'
};



export const FORM_CHIPS = {
  'M10:Loyalty Scheme': 'M10-form-scheme',
  'M10:Loyalty Affiliation': 'M10-form-affiliation',
  'M10:Tier Configuration': 'M10-form-tier',
  'M10:Loyalty Programme': 'M10-form-programme',
  'M10:Voucher Campaign': 'M10-form-voucher-campaign',
  'M10:Points Adjustment': 'M10-form-adjustment',
  'M10:Referral Code': 'M10-form-referral',
  'M10:__by_model__': {
    'fix.loyalty.scheme': 'M10-form-scheme',
    'fix.loyalty.affiliation': 'M10-form-affiliation',
    'fix.loyalty.tier': 'M10-form-tier',
    'fix.loyalty.campaign.hook': 'M10-form-voucher-campaign',
    'fix.loyalty.ledger': 'M10-form-adjustment',
    'fix.loyalty.referral.code': 'M10-form-referral',
    'fix.loyalty.program': 'M10-form-programme',
    'fix.loyalty.account': 'M10-form-account'
  },
  'M10:__by_screen__': {
    'M10-schemes': 'M10-form-scheme',
    'M10-affiliations': 'M10-form-affiliation',
    'M10-programmes': 'M10-form-programme',
    'M10-form-programme': 'M10-form-programme',
    'M10-tiers': 'M10-form-tier',
    'M10-form-tier': 'M10-form-tier',
    'M10-enrol': 'M10-form-account',
    'M10-wallet': 'M10-form-account',
    'M10-referral': 'M10-form-referral',
    'M10-ledger': 'M10-form-adjustment',
    'M10-vouchers': 'M10-form-voucher-campaign',
    'M10-hooks': 'M10-form-voucher-campaign'
  }
};

export const FORM_MODELS = {
  'M10:Loyalty Affiliation': 'fix.loyalty.affiliation',
  'M10:Loyalty Scheme': 'fix.loyalty.scheme',
  'M10:Tier Configuration': 'fix.loyalty.tier',
  'M10:Loyalty Programme': 'fix.loyalty.program',
  'M10:Voucher Campaign': 'fix.loyalty.campaign.hook',
  'M10:Points Adjustment': 'fix.loyalty.ledger',
  'M10:Referral Code': 'fix.loyalty.referral.code'
};

export const CREATE = {
  M10: { screen: 'M10-form-programme', model: 'fix.loyalty.program', label: 'Loyalty Programme' }
};
