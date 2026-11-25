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
      { id: 'M10-memberships', en: 'Privilege Memberships', bn: 'প্রিভিলেজ সদস্যপদ', t: 'g' },
      { id: 'M10-benefits', en: 'Tier Benefit Definitions', bn: 'টিয়ার সুবিধার সংজ্ঞা', t: 'g' },
      { id: 'M10-alliance', en: 'Alliance Benefits', bn: 'অ্যালায়েন্স সুবিধা', t: 'g' }
    ]},
    { en: 'Points & Wallet', screens: [
      { id: 'M10-ledger', en: 'Points Ledger', bn: 'পয়েন্ট লেজার', t: 'g' },
      { id: 'M10-wallet', en: 'Wallet & Credits', bn: 'ওয়ালেট', t: 'g' },
      { id: 'M10-wallet-txns', en: 'Wallet Transactions', bn: 'ওয়ালেট লেনদেন', t: 'g' },
      { id: 'M10-points-balances', en: 'Points Balances', bn: 'পয়েন্ট ব্যালান্স', t: 'g' },
      { id: 'M10-redemption', en: 'Redemption Rules', bn: 'রিডেম্পশন নিয়ম', t: 'r' }
    ]},
    { en: 'Vouchers & Referrals', screens: [
      { id: 'M10-vouchers', en: 'Vouchers & Coupons', bn: 'ভাউচার', t: 'g' },
      { id: 'M10-hooks', en: 'Campaign Reward Hooks', bn: 'ক্যাম্পেইন হুক', t: 'g' },
      { id: 'M10-voucher-batches', en: 'Voucher Batches', bn: 'ভাউচার ব্যাচ', t: 'g' },
      { id: 'M10-stacking', en: 'Stacking Rules', bn: 'স্ট্যাকিং নিয়ম', t: 'g' },
      { id: 'M10-referral', en: 'Referral Programme', bn: 'রেফারেল কর্মসূচি', t: 'g' },
      { id: 'M10-referral-events', en: 'Referral Registrations', bn: 'রেফারেল নিবন্ধন', t: 'g' },
      { id: 'M10-fraud', en: 'Fraud Controls', bn: 'প্রতারণা নিয়ন্ত্রণ', t: 'r' }
    ]},
    { en: 'Finance', screens: [
      { id: 'M10-liability', en: 'Liability & Breakage (IFRS 15)', bn: 'দায় ও ব্রেকেজ', t: 'r' },
      { id: 'M10-liability-runs', en: 'Period-End Liability Runs', bn: 'মেয়াদান্তে দায় হিসাব', t: 'g' },
      { id: 'M10-rpt-deferral', en: 'Membership Revenue Deferral', bn: 'সদস্য ফি স্থগিত রাজস্ব', t: 'r' },
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
  forms: ['Loyalty Programme', 'Tier Configuration', 'Voucher Campaign', 'Points Adjustment', 'Referral Code', 'Loyalty Scheme', 'Loyalty Affiliation', 'Member Enrolment', 'Loyalty Card', 'Redemption Rule', 'Point Type',
    'Privilege Membership', 'Tier Benefit', 'Wallet Transaction', 'Voucher Batch', 'Stacking Rule',
    'Referral Registration', 'Liability Run'],
  cross: ['M33 Customer Master', 'M20 AR &Invoicing', 'M07 CRM'],
  /* M10 capture audit (2026-11-13). Three pages had no button at all
   * (Wallet, Vouchers & Coupons, Liability & Breakage); Tiers & Enrolment
   * could add a tier but not enrol a member; Alliance Benefits offered
   * "+ New Tier Configuration"; and seven working screens (schemes,
   * redemption rules, point types, affiliations, cards, campaign hooks,
   * fraud controls) sat on no page, so the 3 schemes, 3 rules, 2 point types
   * and 2 affiliations live on fix_real were unreachable from the register.
   * Each page now names what captures its record:
   *   - its own form (enrolment, card, scheme, redemption rule, point type,
   *     affiliation, adjustment, referral code);
   *   - Vouchers: the campaign hook that mints them (a voucher is issued to a
   *     qualifying campaign responder; the model accepts no typed voucher);
   *   - Wallet: the points adjustment, the only thing that moves a balance
   *     (the balance is derived from posted ledger lines);
   *   - Liability & Breakage: nothing - it is a period calculation. */
  /* M10 capture audit, pass 2 (2026-11-18). The 13 Nov pass gave every page
   * a button, but only for records the estate could hold; six pages still could
   * not capture what the spec says they are for:
   *   1 paid membership (price, term, lapse)       -> Privilege Membership
   *   2 benefit scope, labour only (BRU-LOY-01)    -> Tier Benefit
   *   4 BDT stored value; it offered a POINTS
   *     adjustment                                  -> Wallet Transaction
   *   5 code batches and stacking caps             -> Voucher Batch, Stacking Rule
   *   6 attribution of a shared code, with blocks  -> Referral Registration
   *   8 the period-end calculation Finance
   *     publishes (AUT-LOY-12)                      -> Liability Run */
  freg: { src: 63, sub: [
    ['1', 'Tiers & Enrolment', 10, { model: 'fix.loyalty.tier', cols: ['name', 'code', 'sequence', 'min_points_threshold', 'min_spend_bdt'], screens: ['M10-tiers', 'M10-memberships', 'M10-enrol', 'M10-cards'], reports: ['Member Growth & Tier Mix'], forms: ['Tier Configuration', 'Privilege Membership', 'Member Enrolment', 'Loyalty Card'] }],
    ['2', 'Benefit Engine', 9, { model: 'fix.loyalty.program', cols: ['name', 'code', 'active', 'name_bn', 'description', 'points_per_bdt'], screens: ['M10-programmes', 'M10-benefits', 'M10-schemes', 'M10-burn-rules', 'M10-point-types'], reports: ['Points Earn/Burn Analysis'], forms: ['Loyalty Programme', 'Tier Benefit', 'Loyalty Scheme', 'Redemption Rule', 'Point Type'] }],
    ['3', 'Points Ledger', 9, { model: 'fix.loyalty.ledger', cols: ['partner_id', 'transaction_type', 'points', 'balance_after', 'state'], screens: ['M10-ledger', 'M10-points-balances', 'M10-redemption', 'M10-rpt-earnburn'], reports: ['Points Earn/Burn Analysis'], forms: ['Points Adjustment'] }],
    ['4', 'Wallet', 7, { model: 'fix.loyalty.wallet', cols: ['name', 'partner_id', 'balance_bdt', 'state'], screens: ['M10-wallet', 'M10-wallet-txns'], reports: [], forms: ['Wallet Transaction'], create: 'M10-form-wallet-txn' }],
    ['5', 'Vouchers & Coupons', 9, { model: 'fix.loyalty.voucher', cols: ['name', 'partner_id', 'state', 'discount_type', 'discount_value', 'valid_until'], screens: ['M10-vouchers', 'M10-voucher-batches', 'M10-hooks', 'M10-stacking', 'M10-fraud', 'M10-rpt-voucher'], reports: ['Voucher Usage & Fraud'], forms: ['Voucher Batch', 'Voucher Campaign', 'Stacking Rule'], create: 'M10-form-voucher-batch' }],
    ['6', 'Referrals', 7, { model: 'fix.loyalty.referral.code', cols: ['name', 'state', 'program_id', 'referrer_partner_id', 'referee_partner_id', 'points_awarded'], screens: ['M10-referral', 'M10-referral-events', 'M10-rpt-referral'], reports: ['Referral Funnel'], forms: ['Referral Code', 'Referral Registration'] }],
    ['7', 'Alliance Benefits', 5, { model: 'fix.loyalty.affiliation', cols: ['name', 'code', 'program_id', 'member_count', 'active'], screens: ['M10-affiliations', 'M10-alliance'], reports: [], forms: ['Loyalty Affiliation'] }],
    ['8', 'Liability & Breakage', 7, { model: 'fix.loyalty.liability.run', cols: ['name', 'program_id', 'period_end', 'net_liability', 'state'], screens: ['M10-liability-runs', 'M10-liability', 'M10-rpt-deferral', 'M10-profit', 'M10-rpt-pnl'], reports: ['Programme P&L'], forms: ['Liability Run'], create: 'M10-form-liability' }]
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
  /* The benefit set an alliance cohort is extended (read here, configured on
   * Tiers & Benefits). Its "+ New" used to open the tier form, so the
   * Alliance Benefits page offered "+ New Tier Configuration" (audit
   * 2026-11-13); the alliance record itself is the affiliation. */
  'M10-alliance': { kind: 'model_list', model: 'fix.loyalty.tier', stateField: 'active', create: false,
    domain: [['active', '=', true]],
    cols: ['name', 'dedicated_support', 'priority_diagnostic', 'labour_discount_pct',
      'parts_discount_pct'],
    note: 'The benefits each active tier carries. An alliance cohort (an affiliation) is extended these benefits; tiers are changed on Tiers & Benefits.' },
  'M10-ledger': { kind: 'model_list', model: 'fix.loyalty.ledger', stateField: 'state',
    cols: ['transaction_type', 'points', 'balance_after', 'order_amount_bdt', 'expiry_date',
      'state', 'approval_state', 'notes'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_post', l: 'Post Ledger Line' },
      { m: 'action_reverse', l: 'Reverse Line', ask: 'Why is this posted line being reversed?', kwarg: 'reason' }
    ] },
  /* Points balances (was the "Wallet" list): opened by enrolment, moved only
   * by posted ledger lines (spec T-03), so never typed in here. */
  'M10-points-balances': { kind: 'model_list', model: 'fix.loyalty.account', stateField: 'state', create: false,
    domain: [['points_balance', '>', 0]],
    cols: ['partner_id', 'tier_id', 'points_balance', 'lifetime_spend_bdt', 'tier_upgraded_date'],
    empty: 'No member holds points yet. A points balance opens when a member is enrolled (Tiers & Enrolment) and moves only through posted ledger lines: earned on a paid service, redeemed on a bill, or a Points Adjustment once it is approved and posted.' },
  /* The BDT stored-value wallet (FR-LOY-022..026). A wallet opens with the
   * customer's first wallet transaction; its balance is the sum of posted
   * transactions, so it is never typed. Points never convert into it (BRU-LOY-07). */
  'M10-wallet': { kind: 'model_list', model: 'fix.loyalty.wallet', stateField: 'state', create: false,
    cols: ['name', 'partner_id', 'balance_bdt', 'state', 'last_activity_at'],
    actions: [
      { m: 'action_freeze', l: 'Freeze Wallet', ask: 'Why is this wallet frozen?', kwarg: 'reason', states: ['active'] },
      { m: 'action_unfreeze', l: 'Release Wallet (Finance)', states: ['frozen'] }
    ],
    empty: 'No customer wallet yet. A wallet opens with its first transaction (+ New Wallet Transaction): a refund, trade-in proceeds, a prepayment or a goodwill credit. Loyalty points never convert into wallet money (BRU-LOY-07).' },
  'M10-wallet-txns': { kind: 'model_list', model: 'fix.loyalty.wallet.txn', stateField: 'state',
    cols: ['name', 'partner_id', 'entry_type', 'amount', 'balance_after', 'state', 'dofa_tier_required', 'approval_state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['draft'] },
      { m: 'action_post', l: 'Post', states: ['draft'] },
      { m: 'action_cancel', l: 'Cancel Draft', states: ['draft'] }
    ],
    note: 'Append-only. A payout needs a verified identity document and, above BDT 5,000, DOFA approval by someone who created no credit on the wallet (BRU-LOY-13, SOD-18). A wallet can never be overdrawn.' },
  'M10-redemption': { kind: 'table_report', module: 'M10', report: 'redemption_rules', title: 'Redemption Rules', period: false },
  'M10-vouchers': { kind: 'model_list', create: false, model: 'fix.loyalty.voucher', stateField: 'state',
    cols: ['name', 'partner_id', 'discount_type', 'discount_value', 'valid_from', 'state'],
    empty: 'No voucher issued yet. Vouchers are not typed in: an active Voucher Campaign hook issues one to each customer who qualifies in its running marketing campaign (M35), with the discount and validity set on the hook.' },
  'M10-hooks': { kind: 'model_list', model: 'fix.loyalty.campaign.hook', stateField: 'state',
    cols: ['name', 'campaign_id', 'program_id', 'reward_type', 'bonus_points', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Hook', states: ['draft'] },
      { m: 'action_complete', l: 'Complete Hook', states: ['active'] }
    ],
    empty: 'No campaign reward hook yet. Create one with + New Voucher Campaign: it ties a marketing campaign (M35) to a voucher or bonus-points reward, and goes live with Activate once that campaign is running.',
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
    lines: { field: 'benefit_ids', title: 'Tier Benefits', readonlyGrid: true,
      note: 'What this tier gives and what each benefit applies to. Defined on Tier Benefit Definitions, where a discount outside labour is refused (BRU-LOY-01).',
      fields: [
        { name: 'code', label: 'Code', readonly: true },
        { name: 'name', label: 'Benefit', readonly: true },
        { name: 'benefit_type', label: 'Type', readonly: true },
        { name: 'value', label: 'Value', readonly: true },
        { name: 'applies_to', label: 'Applies To', readonly: true },
        { name: 'active', label: 'Active', readonly: true }
      ]
    },
    kind: 'model_form',
    model: 'fix.loyalty.tier',
    title: 'Tier Configuration',
    back: 'M10-tiers',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'general', label: 'Tier Definition', bn: 'টিয়ার বিবরণ', icon: '🏷️' },
      { id: 'benefits', label: 'Benefits & Privileges', bn: 'সুবিধা ও ছাড়', icon: '🎁' },
      { id: 'membership', label: 'Membership Price & Term', bn: 'সদস্য ফি ও মেয়াদ', icon: '💳' },
      { id: 'audit', label: 'Audit & Governance', bn: 'অডিট ও পরিচালনা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'membership',
        title: 'Paid Membership Terms (FR-LOY-001)',
        note: 'What a Privilege Membership in this tier costs and how long it runs. A membership keeps the price it was sold at; a renewal pays the price then in force.',
        fields: [
          { name: 'membership_fee_bdt', label: 'Membership Fee (BDT)' },
          { name: 'membership_duration_months', label: 'Term (months)' },
          { name: 'membership_grace_days', label: 'Renewal Grace (days)' }
        ]
      },
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
        note: 'A privilege discount applies to labour charges only, never to parts, consumables or transport (BRU-LOY-01): a parts discount above 0 is refused. Each benefit and its scope is defined on Tier Benefit Definitions.',
        fields: [
          { name: 'labour_discount_pct', label: 'Labour Discount %' },
          { name: 'parts_discount_pct', label: 'Parts Discount % (must stay 0: BRU-LOY-01)' },
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
    /* back to the hook list: that is where the saved hook is activated */
    back: 'M10-hooks',
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
          { name: 'reward_type', required: true, label: 'Reward Type', value: 'voucher' },
          { name: 'bonus_points', label: 'Bonus Points (bonus-points hooks only)' }
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
        { name: 'referral_window_days', label: 'Referral Attribution Window (days)' },
        { name: 'referral_cap_per_month', label: 'Referrals per Referrer per Month (0 = no cap)' },
        { name: 'max_aggregate_discount_pct', label: 'Max Aggregate Discount % (BRU-LOY-09, DOFA Tier 3)' },
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
        fields: []
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
  'M10-form-burn-rule': {
    kind: 'model_form', model: 'fix.loyalty.burn.rule',
    title: 'Redemption Rule', back: 'M10-burn-rules',
    tabs: [
      { id: 'identity', label: '1. Rule', bn: '১. নিয়ম', icon: '🔥' },
      { id: 'scope', label: '2. Who It Applies To', bn: '২. প্রযোজ্যতা', icon: '🎯' },
      { id: 'limits', label: '3. Redemption Limits', bn: '৩. রিডেম্পশন সীমা', icon: '🚧' },
      { id: 'validity', label: '4. Validity', bn: '৪. মেয়াদ', icon: '📅' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Rule Identity',
        note: 'Evaluated in priority order inside its scheme, like the earn rules: the first rule that matches decides whether, and how far, points may pay a bill.',
        fields: [
        { name: 'scheme_id', label: 'Scheme', required: true },
        { name: 'name', label: 'Rule', required: true },
        { name: 'priority', label: 'Order', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'scope',
        title: 'Keyed On, Tier & Affiliation',
        note: 'An empty tier or affiliation means the rule applies to every member. The value is matched against the dimension (a category, a channel, a product code, or a minimum bill amount).',
        fields: [
        { name: 'dimension', label: 'Keyed On', required: true },
        { name: 'dimension_value', label: 'Value' },
        { name: 'tier_id', label: 'Applies To Tier' },
        { name: 'affiliation_id', label: 'Applies To Affiliation' }
        ]
      },
      {
        tab: 'limits',
        title: 'How Much Points May Cover',
        note: 'The discount ceiling must lie between 0 and 100 percent. A blocked rule refuses payment by points for every matching transaction.',
        fields: [
        { name: 'min_points', label: 'Minimum Balance' },
        { name: 'max_points_per_transaction', label: 'Max Points per Transaction (0 = no ceiling)' },
        { name: 'max_discount_pct', label: 'Max Share of Bill (%)' },
        { name: 'blocked', label: 'Redemption Blocked' }
        ]
      },
      {
        tab: 'validity',
        title: 'When It Applies',
        fields: [
        { name: 'valid_from', label: 'Valid From' },
        { name: 'valid_until', label: 'Valid Until' }
        ]
      }
    ]
  },
  'M10-point-types': { kind: 'model_list', model: 'fix.loyalty.point.type', create: true,
    cols: ['sequence', 'name', 'name_bn', 'code', 'program_id', 'point_class', 'bdt_per_point', 'expiry_months', 'active'],
    note: 'A qualifying point moves a member up the ladder and can never be spent, which is what decouples tier marketing from the IFRS-15 liability.' },
  'M10-form-point-type': {
    kind: 'model_form', model: 'fix.loyalty.point.type',
    title: 'Loyalty Point Type', back: 'M10-point-types',
    tabs: [
      { id: 'identity', label: '1. Point Type', bn: '১. পয়েন্টের ধরন', icon: '🪙' },
      { id: 'value', label: '2. Value & Expiry', bn: '২. মূল্য ও মেয়াদ', icon: '⏳' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Point Currency',
        note: 'Each code exists once per programme. The class says what the point DOES: a redeemable point is spendable and an IFRS-15 liability; a qualifying point only moves a member up the ladder.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'code', label: 'Code', required: true },
        { name: 'program_id', label: 'Programme', required: true },
        { name: 'sequence', label: 'Order' },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'value',
        title: 'Redemption Value & Expiry',
        note: 'A tier-qualifying point cannot carry a BDT value: the save is refused, because it would reappear in the redemption liability this class exists to keep it out of.',
        fields: [
        { name: 'point_class', label: 'Class', required: true },
        { name: 'bdt_per_point', label: 'BDT per Point' },
        { name: 'expiry_months', label: 'Expiry (months, 0 = never)' }
        ]
      }
    ]
  },
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
  'M10-form-card': {
    kind: 'model_form', model: 'fix.loyalty.card',
    title: 'Loyalty Card', back: 'M10-cards',
    status: { field: 'state', labels: { active: 'Active', blocked: 'Blocked', replaced: 'Replaced' } },
    tabs: [
      { id: 'identity', label: '1. Card', bn: '১. কার্ড', icon: '💳' },
      { id: 'validity', label: '2. Validity & Status', bn: '২. মেয়াদ ও অবস্থা', icon: '📅' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Card Identity',
        note: 'A card number identifies one card across the estate. The barcode is what the POS scanner reads; a blocked card resolves to no member at the counter.',
        fields: [
        { name: 'account_id', label: 'Loyalty Account', required: true },
        { name: 'card_number', label: 'Card Number', required: true },
        { name: 'barcode', label: 'Barcode' },
        { name: 'card_type', label: 'Card Type', required: true }
        ]
      },
      {
        tab: 'validity',
        title: 'Issue, Expiry & Block',
        note: 'Blocking needs a stated reason and is done with Block Card on the list, which records the reason here.',
        fields: [
        { name: 'issued_on', label: 'Issued On', required: true },
        { name: 'expires_on', label: 'Expires On' },
        { name: 'state', label: 'State', readonly: true },
        { name: 'block_reason', label: 'Block Reason', readonly: true }
        ]
      }
    ]
  },
  /* ============ M10 capture audit, pass 2 (2026-11-18) ============ */
  'M10-memberships': { kind: 'model_list', model: 'fix.loyalty.membership', stateField: 'state',
    cols: ['name', 'partner_id', 'tier_id', 'channel', 'price_bdt', 'started_on', 'expires_on', 'state', 'deferred_bdt'],
    actions: [
      { m: 'action_confirm_payment', l: 'Confirm Payment (M20)', ask: 'M20 receipt or invoice reference', kwarg: 'payment_ref', states: ['pending'] },
      { m: 'action_suspend', l: 'Suspend', ask: 'Why is the membership suspended?', kwarg: 'reason', states: ['active', 'expiring'] },
      { m: 'action_reinstate', l: 'Reinstate', states: ['suspended'] },
      { m: 'action_renew', l: 'Renew', states: ['active', 'expiring', 'lapsed'] },
      { m: 'action_cancel', l: 'Cancel', ask: 'Why is the membership cancelled?', kwarg: 'reason', states: ['pending', 'active', 'expiring', 'suspended'] }
    ],
    note: 'A paid membership activates on confirmed payment, is noticed at 60/30/7 days, and lapses after its grace period. Benefits stop on the stated date, never retroactively (BRU-LOY-03); the fee is earned over the term (BRU-LOY-12).' },
  'M10-form-membership': {
    kind: 'model_form', model: 'fix.loyalty.membership',
    title: 'Privilege Membership', back: 'M10-memberships',
    status: { field: 'state', labels: { pending: 'Pending Payment', active: 'Active', expiring: 'Expiring', suspended: 'Suspended', lapsed: 'Lapsed', cancelled: 'Cancelled', completed: 'Completed (Renewed)' } },
    tabs: [
      { id: 'member', label: '1. Member & Tier', bn: '১. সদস্য ও টিয়ার', icon: '👑' },
      { id: 'term', label: '2. Price & Term', bn: '২. ফি ও মেয়াদ', icon: '📅' },
      { id: 'status', label: '3. Status & Revenue', bn: '৩. অবস্থা ও রাজস্ব', icon: '📊' }
    ],
    sections: [
      { tab: 'member', title: 'Who Joins, Which Tier, Through Which Channel',
        note: 'One open membership per customer per programme; a renewal waits beside the membership it renews. Price and term default from the tier and are fixed once paid.',
        fields: [
          { name: 'partner_id', label: 'Member', required: true },
          { name: 'program_id', label: 'Programme', required: true },
          { name: 'tier_id', label: 'Tier', required: true },
          { name: 'channel', label: 'Enrolment Channel', required: true },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' }
        ] },
      { tab: 'term', title: 'Price, Term & Grace',
        note: 'Leave the price empty to take the tier fee. A paid membership stays Pending until Confirm Payment records its M20 reference.',
        fields: [
          { name: 'price_bdt', label: 'Price (BDT)' },
          { name: 'duration_months', label: 'Term (months)' },
          { name: 'grace_days', label: 'Grace (days)' },
          { name: 'started_on', label: 'Starts On', readonly: true },
          { name: 'expires_on', label: 'Expires On', readonly: true },
          { name: 'grace_until', label: 'Lapses After', readonly: true }
        ] },
      { tab: 'status', title: 'Payment, Status & Deferred Revenue',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'payment_ref', label: 'Payment Reference (M20)', readonly: true },
          { name: 'status_reason', label: 'Suspension / Cancellation Reason', readonly: true },
          { name: 'benefits_withdrawn_on', label: 'Benefits Withdrawn On', readonly: true },
          { name: 'recognised_bdt', label: 'Revenue Recognised to Date', readonly: true },
          { name: 'deferred_bdt', label: 'Revenue Still Deferred', readonly: true }
        ] }
    ]
  },
  'M10-benefits': { kind: 'model_list', model: 'fix.loyalty.benefit', stateField: 'active',
    cols: ['tier_id', 'priority', 'code', 'name', 'benefit_type', 'value', 'applies_to', 'stackable', 'active'],
    note: 'What each tier benefit applies to. A discount applies to labour only; parts, consumables and transport are refused (BRU-LOY-01).' },
  'M10-form-benefit': {
    kind: 'model_form', model: 'fix.loyalty.benefit',
    title: 'Tier Benefit', back: 'M10-benefits',
    tabs: [
      { id: 'what', label: '1. Benefit', bn: '১. সুবিধা', icon: '🎁' },
      { id: 'scope', label: '2. Scope & Stacking', bn: '২. প্রযোজ্যতা', icon: '🎯' }
    ],
    sections: [
      { tab: 'what', title: 'Benefit Definition', fields: [
        { name: 'tier_id', label: 'Tier', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'benefit_type', label: 'Benefit Type', required: true },
        { name: 'value', label: 'Value (% for a discount; hours, days or count otherwise)' }
      ] },
      { tab: 'scope', title: 'What It Applies To',
        note: 'A Labour Discount must apply to labour charges; any other scope is refused. Entitlements (SLA, logistics, warranty, health check) apply as a service, not a price.',
        fields: [
          { name: 'applies_to', label: 'Applies To', required: true },
          { name: 'priority', label: 'Order' },
          { name: 'stackable', label: 'Combines with Vouchers & Promotions' },
          { name: 'effective_from', label: 'Effective From' },
          { name: 'effective_to', label: 'Effective To' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M10-form-wallet-txn': {
    kind: 'model_form', model: 'fix.loyalty.wallet.txn',
    title: 'Wallet Transaction', back: 'M10-wallet-txns',
    status: { field: 'state', labels: { draft: 'Draft', posted: 'Posted', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'entry', label: '1. Entry', bn: '১. এন্ট্রি', icon: '💳' },
      { id: 'target', label: '2. Source / Invoice / Payout', bn: '২. উৎস / ইনভয়েস / পরিশোধ', icon: '🏦' },
      { id: 'approval', label: '3. DOFA & Posting', bn: '৩. অনুমোদন', icon: '⚖️' }
    ],
    sections: [
      { tab: 'entry', title: 'Customer, Type & Amount',
        note: 'The customer’s wallet is found or opened automatically. Credits: refund, trade-in, prepayment, goodwill. Debits: applied to an invoice, or paid out. The amount is always positive; the type gives its direction.',
        fields: [
          { name: 'partner_id', label: 'Customer', required: true },
          { name: 'entry_type', label: 'Transaction Type', required: true },
          { name: 'amount', label: 'Amount (BDT)', required: true },
          { name: 'company_id', label: 'Company', required: true },
          { name: 'wallet_id', label: 'Wallet', readonly: true }
        ] },
      { tab: 'target', title: 'Where It Comes From or Goes To',
        note: 'A credit names its source document. An application names a posted invoice of the same customer. A payout needs a VERIFIED identity document and the bank account or bKash/Nagad/Rocket number (BRU-LOY-13).',
        fields: [
          { name: 'source_ref', label: 'Source Document (refund / trade-in / receipt)' },
          { name: 'invoice_id', label: 'Invoice (application)' },
          { name: 'payout_method', label: 'Payout Method' },
          { name: 'payout_account', label: 'Payout Account / Wallet No.' },
          { name: 'id_document_id', label: 'Identity Verified With' },
          { name: 'reason', label: 'Reason (goodwill)', type: 'text' }
        ] },
      { tab: 'approval', title: 'Approval & Posting',
        note: 'A payout or goodwill credit above BDT 5,000 needs DOFA approval before Post. The approver of a payout must not have created credits on this wallet (SOD-18).',
        fields: [
          { name: 'dofa_justification', label: 'DOFA Justification', type: 'text' },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'dofa_approved', label: 'Approved', readonly: true },
          { name: 'dofa_approved_by', label: 'Approver', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'balance_after', label: 'Wallet Balance After', readonly: true }
        ] }
    ]
  },
  'M10-voucher-batches': { kind: 'model_list', model: 'fix.loyalty.voucher.batch', stateField: 'state',
    cols: ['name', 'code_prefix', 'batch_type', 'discount_type', 'discount_value', 'valid_until', 'issued_count', 'redeemed_count', 'state'],
    actions: [
      { m: 'action_issue', l: 'Issue Codes', states: ['draft'] },
      { m: 'action_close', l: 'Close Batch', states: ['issued'] }
    ],
    note: 'A batch mints its codes on Issue, within its issuance limit; closing it (or its expiry) cancels unredeemed codes (AUT-LOY-14).' },
  'M10-form-voucher-batch': {
    lines: { field: 'voucher_ids', title: 'Issued Codes', readonlyGrid: true,
      note: 'Minted by Issue Codes, never typed. A bulk code takes its holder when it is redeemed.',
      fields: [
        { name: 'name', label: 'Code', readonly: true },
        { name: 'partner_id', label: 'Holder', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'redeemed_at', label: 'Redeemed At', readonly: true }
      ]
    },
    kind: 'model_form', model: 'fix.loyalty.voucher.batch',
    title: 'Voucher Batch', back: 'M10-voucher-batches',
    status: { field: 'state', labels: { draft: 'Draft', issued: 'Issued', closed: 'Closed' } },
    tabs: [
      { id: 'batch', label: '1. Batch & Codes', bn: '১. ব্যাচ', icon: '🎟️' },
      { id: 'value', label: '2. Value & Validity', bn: '২. মূল্য ও মেয়াদ', icon: '💰' },
      { id: 'elig', label: '3. Eligibility', bn: '৩. যোগ্যতা', icon: '🎯' }
    ],
    sections: [
      { tab: 'batch', title: 'Batch & Codes (FR-LOY-027)',
        note: 'Personalised: one code for each listed customer. Bulk: the given number of codes, the holder named when a code is redeemed. A batch issues at most 10,000 codes.',
        fields: [
          { name: 'name', label: 'Batch Name', required: true },
          { name: 'code_prefix', label: 'Code Prefix (2-8 capitals/digits)', required: true },
          { name: 'program_id', label: 'Programme', required: true },
          { name: 'campaign_id', label: 'Campaign (M35)' },
          { name: 'batch_type', label: 'Batch Type', required: true },
          { name: 'quantity', label: 'Codes to Issue (bulk)' },
          { name: 'partner_ids', label: 'Customers (personalised)' }
        ] },
      { tab: 'value', title: 'Discount & Validity', fields: [
        { name: 'discount_type', label: 'Discount Type', required: true },
        { name: 'discount_value', label: 'Discount Value', required: true },
        { name: 'min_spend_bdt', label: 'Minimum Spend (BDT)' },
        { name: 'valid_from', label: 'Valid From', required: true },
        { name: 'valid_until', label: 'Valid Until', required: true }
      ] },
      { tab: 'elig', title: 'Who May Redeem (FR-LOY-028)',
        note: 'Checked when a code is redeemed: tier, channel, first purchase only and uses per customer.',
        fields: [
          { name: 'tier_ids', label: 'Eligible Tiers (empty = all)' },
          { name: 'channel', label: 'Channel', required: true },
          { name: 'first_purchase_only', label: 'First Purchase Only' },
          { name: 'max_per_customer', label: 'Uses per Customer (0 = no limit)' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'closed_unredeemed', label: 'Codes Unredeemed at Close', readonly: true }
        ] }
    ]
  },
  'M10-stacking': { kind: 'model_list', model: 'fix.loyalty.stacking.rule', stateField: 'active',
    cols: ['program_id', 'sequence', 'component_a', 'component_b', 'allowed', 'max_aggregate_pct', 'active'],
    note: 'Which benefits, vouchers, promotions and points may combine, and the combined ceiling. The programme’s Max Aggregate Discount % caps every bill (BRU-LOY-09).' },
  'M10-form-stacking': {
    kind: 'model_form', model: 'fix.loyalty.stacking.rule',
    title: 'Stacking Rule', back: 'M10-stacking',
    tabs: [{ id: 'rule', label: '1. Stacking Rule', bn: '১. স্ট্যাকিং', icon: '🧮' }],
    sections: [
      { tab: 'rule', title: 'Combination Control (FR-LOY-029)',
        note: 'Components apply in the order tier benefit, voucher, promotion, points. When a pair is not allowed, the later one is dropped; when allowed, together they may take at most the ceiling.',
        fields: [
          { name: 'program_id', label: 'Programme', required: true },
          { name: 'component_a', label: 'Component A', required: true },
          { name: 'component_b', label: 'Component B', required: true },
          { name: 'allowed', label: 'May Combine' },
          { name: 'max_aggregate_pct', label: 'Combined Ceiling %' },
          { name: 'sequence', label: 'Order' },
          { name: 'note', label: 'Note' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M10-referral-events': { kind: 'model_list', model: 'fix.loyalty.referral.event', stateField: 'state',
    cols: ['name', 'code_id', 'referrer_partner_id', 'referee_partner_id', 'registered_at', 'window_until', 'state', 'block_reason'],
    actions: [{ m: 'action_qualify', l: 'Qualify & Reward', states: ['registered'] }],
    note: 'A shared code attributed to a new customer. Self-referral, same phone, email or address, circular referral, a second attribution and the per-referrer cap are blocked and kept as evidence (BRU-LOY-10).' },
  'M10-form-referral-event': {
    kind: 'model_form', model: 'fix.loyalty.referral.event',
    title: 'Referral Registration', back: 'M10-referral-events',
    status: { field: 'state', labels: { registered: 'Registered', qualified: 'Qualified', rewarded: 'Rewarded', not_qualified: 'Not Qualified', blocked: 'Blocked' } },
    tabs: [
      { id: 'who', label: '1. Attribution', bn: '১. অ্যাট্রিবিউশন', icon: '🔗' },
      { id: 'outcome', label: '2. Outcome', bn: '২. ফলাফল', icon: '🏆' }
    ],
    sections: [
      { tab: 'who', title: 'Which Code Brought Which New Customer (FR-LOY-034)',
        note: 'A saved registration is checked at once; a blocked one is kept with its reason. It qualifies on the new customer’s first completed service within the programme’s window, and both sides are rewarded.',
        fields: [
          { name: 'code_id', label: 'Referral Code', required: true },
          { name: 'referee_partner_id', label: 'New Customer', required: true },
          { name: 'channel', label: 'Channel' },
          { name: 'registered_at', label: 'Registered At', readonly: true }
        ] },
      { tab: 'outcome', title: 'Outcome', fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'block_reason', label: 'Block / Not-Qualified Reason', readonly: true },
        { name: 'window_until', label: 'Qualify By', readonly: true },
        { name: 'reward_referrer_points', label: 'Referrer Points', readonly: true },
        { name: 'reward_referee_points', label: 'New Customer Points', readonly: true }
      ] }
    ]
  },
  'M10-liability-runs': { kind: 'model_list', model: 'fix.loyalty.liability.run', stateField: 'state',
    cols: ['name', 'program_id', 'period_end', 'points_outstanding', 'gross_liability', 'breakage_amount', 'net_liability', 'movement', 'reconciles', 'state'],
    actions: [
      { m: 'action_calculate', l: 'Calculate', states: ['draft', 'calculated'] },
      { m: 'action_publish', l: 'Publish to M19 (Finance)', states: ['calculated'] }
    ],
    note: 'The period-end IFRS 15 calculation (AUT-LOY-12). It must reconcile to the posted ledger, and is published by a Finance user other than the one who calculated it.' },
  'M10-form-liability': {
    kind: 'model_form', model: 'fix.loyalty.liability.run',
    title: 'Period-End Liability Run', back: 'M10-liability-runs',
    status: { field: 'state', labels: { draft: 'Draft', calculated: 'Calculated', published: 'Published to M19' } },
    tabs: [
      { id: 'period', label: '1. Period', bn: '১. সময়কাল', icon: '📅' },
      { id: 'figures', label: '2. Liability & Breakage', bn: '২. দায় ও ব্রেকেজ', icon: '📊' },
      { id: 'sign', label: '3. Calculation & Publication', bn: '৩. হিসাব ও প্রকাশ', icon: '✍️' }
    ],
    sections: [
      { tab: 'period', title: 'Which Programme, Which Period',
        note: 'Save, then Calculate on the list. Outstanding points are the posted ledger up to the end of the period, valued at the programme’s BDT per point, net of the expected breakage.',
        fields: [
          { name: 'program_id', label: 'Programme', required: true },
          { name: 'period_end', label: 'Period End', required: true },
          { name: 'company_id', label: 'Company', required: true },
          { name: 'breakage_basis', label: 'Breakage Basis (required when breakage > 0)', type: 'text' }
        ] },
      { tab: 'figures', title: 'Figures', fields: [
        { name: 'points_outstanding', label: 'Points Outstanding', readonly: true },
        { name: 'valuation', label: 'BDT per Point', readonly: true },
        { name: 'gross_liability', label: 'Gross Liability', readonly: true },
        { name: 'breakage_rate_pct', label: 'Breakage %', readonly: true },
        { name: 'breakage_amount', label: 'Breakage Amount', readonly: true },
        { name: 'net_liability', label: 'Net Liability', readonly: true },
        { name: 'prior_net_liability', label: 'Prior Period Net', readonly: true },
        { name: 'movement', label: 'Movement', readonly: true },
        { name: 'membership_deferred_bdt', label: 'Membership Fees Deferred', readonly: true }
      ] },
      { tab: 'sign', title: 'Reconciliation & Sign-Off', fields: [
        { name: 'ledger_points', label: 'Ledger Points at Period End', readonly: true },
        { name: 'account_points', label: 'Member Balances Now', readonly: true },
        { name: 'reconciles', label: 'Balances Reconcile to Ledger', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'calculated_by', label: 'Calculated By', readonly: true },
        { name: 'calculated_at', label: 'Calculated At', readonly: true },
        { name: 'published_by', label: 'Published By', readonly: true },
        { name: 'published_at', label: 'Published At', readonly: true }
      ] }
    ]
  },
  'M10-rpt-deferral': { kind: 'table_report', module: 'M10', report: 'membership_deferral', title: 'Membership Revenue Deferral', period: false },
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
  'M10:Member Enrolment': 'M10-form-account',
  'M10:Loyalty Card': 'M10-form-card',
  'M10:Redemption Rule': 'M10-form-burn-rule',
  'M10:Point Type': 'M10-form-point-type',
  'M10:Privilege Membership': 'M10-form-membership',
  'M10:Tier Benefit': 'M10-form-benefit',
  'M10:Wallet Transaction': 'M10-form-wallet-txn',
  'M10:Voucher Batch': 'M10-form-voucher-batch',
  'M10:Stacking Rule': 'M10-form-stacking',
  'M10:Referral Registration': 'M10-form-referral-event',
  'M10:Liability Run': 'M10-form-liability',
  'M10:__by_model__': {
    'fix.loyalty.scheme': 'M10-form-scheme',
    'fix.loyalty.affiliation': 'M10-form-affiliation',
    'fix.loyalty.tier': 'M10-form-tier',
    'fix.loyalty.campaign.hook': 'M10-form-voucher-campaign',
    'fix.loyalty.ledger': 'M10-form-adjustment',
    'fix.loyalty.referral.code': 'M10-form-referral',
    'fix.loyalty.program': 'M10-form-programme',
    'fix.loyalty.account': 'M10-form-account',
    'fix.loyalty.burn.rule': 'M10-form-burn-rule',
    'fix.loyalty.point.type': 'M10-form-point-type',
    'fix.loyalty.card': 'M10-form-card',
    'fix.loyalty.membership': 'M10-form-membership',
    'fix.loyalty.benefit': 'M10-form-benefit',
    'fix.loyalty.wallet.txn': 'M10-form-wallet-txn',
    'fix.loyalty.voucher.batch': 'M10-form-voucher-batch',
    'fix.loyalty.stacking.rule': 'M10-form-stacking',
    'fix.loyalty.referral.event': 'M10-form-referral-event',
    'fix.loyalty.liability.run': 'M10-form-liability'
  },
  'M10:__by_screen__': {
    'M10-schemes': 'M10-form-scheme',
    'M10-affiliations': 'M10-form-affiliation',
    'M10-programmes': 'M10-form-programme',
    'M10-form-programme': 'M10-form-programme',
    'M10-tiers': 'M10-form-tier',
    'M10-form-tier': 'M10-form-tier',
    'M10-enrol': 'M10-form-account',
    // M10-wallet rows are wallets: a row opens the wallet itself, not a new
    // transaction (the page's + New still posts a Wallet Transaction).
    'M10-wallet-txns': 'M10-form-wallet-txn',
    'M10-memberships': 'M10-form-membership',
    'M10-benefits': 'M10-form-benefit',
    'M10-voucher-batches': 'M10-form-voucher-batch',
    'M10-stacking': 'M10-form-stacking',
    'M10-referral-events': 'M10-form-referral-event',
    'M10-liability-runs': 'M10-form-liability',
    'M10-referral': 'M10-form-referral',
    'M10-ledger': 'M10-form-adjustment',
    'M10-hooks': 'M10-form-voucher-campaign',
    'M10-burn-rules': 'M10-form-burn-rule',
    'M10-point-types': 'M10-form-point-type',
    'M10-cards': 'M10-form-card'
  }
};

export const FORM_MODELS = {
  'M10:Loyalty Affiliation': 'fix.loyalty.affiliation',
  'M10:Loyalty Scheme': 'fix.loyalty.scheme',
  'M10:Tier Configuration': 'fix.loyalty.tier',
  'M10:Loyalty Programme': 'fix.loyalty.program',
  'M10:Voucher Campaign': 'fix.loyalty.campaign.hook',
  'M10:Points Adjustment': 'fix.loyalty.ledger',
  'M10:Referral Code': 'fix.loyalty.referral.code',
  'M10:Member Enrolment': 'fix.loyalty.account',
  'M10:Loyalty Card': 'fix.loyalty.card',
  'M10:Redemption Rule': 'fix.loyalty.burn.rule',
  'M10:Point Type': 'fix.loyalty.point.type',
  'M10:Privilege Membership': 'fix.loyalty.membership',
  'M10:Tier Benefit': 'fix.loyalty.benefit',
  'M10:Wallet Transaction': 'fix.loyalty.wallet.txn',
  'M10:Voucher Batch': 'fix.loyalty.voucher.batch',
  'M10:Stacking Rule': 'fix.loyalty.stacking.rule',
  'M10:Referral Registration': 'fix.loyalty.referral.event',
  'M10:Liability Run': 'fix.loyalty.liability.run'
};

export const CREATE = {
  M10: { screen: 'M10-form-programme', model: 'fix.loyalty.program', label: 'Loyalty Programme' }
};
