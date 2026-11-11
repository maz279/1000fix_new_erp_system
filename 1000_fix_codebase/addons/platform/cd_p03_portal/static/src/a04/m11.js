/** @odoo-module **/
/* A04 · Commercial & Revenue — M11 Pricing & Rate Cards (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 6 reports / 5 forms / freg 97.
 * Rate cards, dynamic rules, explanations and discount approvals are real;
 * price books/versions/floors/promotions/simulations/policies are new. */

export const MODULE = {
  area: 'A04', code: 'M11', en: 'Pricing & Rate Cards', title: 'M11 · Pricing & Rate Cards',
  bn: 'মূল্য ও রেট কার্ড', icon: '💲',
  desc: 'Price books and versions, labour/parts/brand rate cards, dynamic adjustment rules, discount governance, cost-plus floors, promotions, simulation and realised-price analytics.',
  kpis: [
    { l: 'Realised Margin', m: 'realised_margin', suffix: '%' },
    { l: 'Discount Leaks MTD', m: 'discount_leaks_mtd' },
    { l: 'Rate Cards Live', m: 'rate_cards_live' },
    { l: 'Brand Reimb. Rates', m: 'brand_reimb_rates' },
    { l: 'Simulations MTD', m: 'simulations_mtd' },
    { l: 'Margin Floors Breached', m: 'margin_floors_breached' }
  ],
  groups: [
    { en: 'Pricing Records', screens: [
      { id: 'M11-price-explanation', en: "Price Explanation", bn: "Price Explanation", t: 'g' }
    ]},
    { en: 'Price Books', screens: [
      { id: 'M11-books', en: 'Price Books', bn: 'প্রাইস বুক', t: 'g' },
      { id: 'M11-engine', en: 'Price Resolution Engine', bn: 'প্রাইস ইঞ্জিন', t: 'c' },
      { id: 'M11-versions', en: 'Versioning & Mass Changes', bn: 'ভার্সনিং', t: 'g' }
    ]},
    { en: 'Rate Cards', screens: [
      { id: 'M11-labour', en: 'Labour Rate Cards', bn: 'শ্রম রেট কার্ড', t: 'g' },
      { id: 'M11-parts', en: 'Parts Pricing Rules', bn: 'পার্টস মূল্য', t: 'g' },
      { id: 'M11-brand', en: 'Brand Reimbursement Rates', bn: 'ব্র্যান্ড রেট', t: 'g' },
      { id: 'M11-adjust', en: 'Adjustment Rules', bn: 'সমন্বয় নিয়ম', t: 'g' }
    ]},
    { en: 'Pricing Governance', screens: [
      { id: 'M11-discounts', en: 'Discount Governance', bn: 'ডিসকাউন্ট গভর্নেন্স', t: 'c' },
      { id: 'M11-floors', en: 'Cost-Plus & Margin Floors', bn: 'মার্জিন ফ্লোর', t: 'g' },
      { id: 'M11-promos', en: 'Promotions', bn: 'প্রমোশন', t: 'g' },
      { id: 'M11-changes', en: 'Rate & Floor Changes', bn: 'রেট ও ফ্লোর পরিবর্তন', t: 'g' },
      { id: 'M11-policies', en: 'Discount Ladder', bn: 'ডিসকাউন্ট ধাপ', t: 'g' }
    ]},
    { en: 'Analytics', screens: [
      { id: 'M11-simulate', en: 'Price Simulation', bn: 'মূল্য সিমুলেশন', t: 'c' },
      { id: 'M11-realised', en: 'Realised-Price Analytics', bn: 'বাস্তব মূল্য বিশ্লেষণ', t: 'r' }
    ]}
  ],
  reports: ['Realised Price vs Card', 'Discount Register by Approver', 'Rate-Card Utilisation', 'Margin by Service Line', 'Promotion Effectiveness', 'Brand Reimbursement Recovery', 'Floor vs Realised Rate'],
  forms: ['Price Book', 'Rate Card', 'Discount Policy', 'Promotion', 'Price Simulation Request'],
  cross: ['M37 Catalogue', 'M36 Quotations', 'M20 AR'],
  freg: { src: 97, sub: [
    ['1', 'Pricing Engine', 12, { model: 'fix.price.explanation', cols: ['name', 'rule_id', 'base_price', 'final_price', 'model_driven'], screens: ['M11-engine', 'M11-price-explanation'] }],
    ['2', 'Price Books', 10, { model: 'fix.price.book', cols: ['name', 'code', 'state', 'currency_id', 'active'], screens: ['M11-books'] }],
    ['3', 'Rate Cards', 11, { model: 'fix.rate.card', cols: ['name', 'product_code', 'line_type', 'unit_price', 'catalogue_item_id', 'min_tier', 'valid_from'], screens: ['M11-labour'] }],
    ['4', 'Parts Pricing', 9, { model: 'fix.rate.card', cols: ['name', 'product_code', 'line_type', 'unit_price', 'catalogue_item_id', 'min_tier', 'valid_from'], screens: ['M11-parts'] }],
    ['5', 'Customer/Contract Pricing', 8, { model: 'fix.price.book', cols: ['name', 'code', 'state', 'currency_id', 'active'], screens: ['M11-books'] }],
    ['6', 'Brand Reimbursement', 7, { model: 'fix.warranty.claim', cols: ['brand_id', 'claim_no', 'claim_amount', 'remittance_amount', 'state'], screens: ['M11-brand', 'M11-rpt-brand'] }],
    ['7', 'Discount Governance', 10, { model: 'fix.discount.approval', cols: ['quotation_id', 'discount_pct', 'state', 'justification', 'approved_by'], screens: ['M11-discounts', 'M11-rpt-discount'] }],
    ['8', 'Promotions', 7, { model: 'fix.promotion', cols: ['code', 'name', 'discount_type', 'value', 'channel', 'state'], screens: ['M11-promos', 'M11-rpt-promo'] }],
    ['9', 'Adjustment Rules', 8, { model: 'fix.dynamic.price.rule', cols: ['name', 'rule_type', 'channel', 'adjustment_pct'], screens: ['M11-adjust'] }],
    ['10', 'Simulation & Trace', 7, { model: 'fix.price.simulation', cols: ['name', 'catalogue_item_id', 'rate_card_id', 'state', 'computed_at'], screens: ['M11-simulate', 'M11-price-explanation'] }],
    ['11', 'Versioning & Approval', 8, { model: 'fix.price.version', cols: ['name', 'state', 'book_id', 'version', 'effective_from', 'approved_by'], screens: ['M11-versions'] }]
  ] }
};

export const SCREENS = {
  'M11-books': { kind: 'model_list', model: 'fix.price.book', stateField: 'state',
    cols: ['code', 'name', 'currency_id', 'state', 'active_version_id', 'active'],
    // A04 audit 2026-11-04: a book goes Active when its first released
    // version activates; a Price-Book Releaser retires it.
    actions: [
      { m: 'action_retire', l: 'Retire Price Book (Releaser)', ask: 'Why is the book retired?', kwarg: 'reason' }
    ] },
  'M11-engine': { kind: 'table_report', module: 'M11', report: 'pricing_engine', title: 'Price Resolution Engine', period: false },
  'M11-versions': { kind: 'model_list', model: 'fix.price.version', stateField: 'state',
    cols: ['name', 'book_id', 'version', 'effective_from', 'state', 'approval_state', 'approved_by'],
    // Released from the Price-Book Releaser's M63 inbox (approver != author);
    // activates on its effective date.
    actions: [
      { m: 'action_submit', l: 'Submit for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' }
    ] },
  'M11-labour': { kind: 'model_list', model: 'fix.rate.card', stateField: 'state',
    domain: [['line_type', '=', 'labour']],
    cols: ['product_code', 'name', 'unit_price', 'min_tier', 'valid_from', 'valid_to', 'state', 'active'],
    // A rate prices nothing until released; a released rate changes only
    // through a price change a releaser approves (A04 audit M11-5).
    actions: [
      { m: 'action_request_release', l: 'Request Release (Releaser approves)' },
      { m: 'action_request_change', l: 'Request Change to the Proposed Rate' },
      { m: 'action_request_retire', l: 'Request Retirement', ask: 'Why is the rate retired?', kwarg: 'reason' }
    ] },
  'M11-parts': { kind: 'model_list', model: 'fix.rate.card', stateField: 'state',
    domain: [['line_type', '=', 'part']],
    cols: ['product_code', 'name', 'unit_price', 'min_tier', 'valid_from', 'valid_to', 'state', 'active'],
    // A rate prices nothing until released; a released rate changes only
    // through a price change a releaser approves (A04 audit M11-5).
    actions: [
      { m: 'action_request_release', l: 'Request Release (Releaser approves)' },
      { m: 'action_request_change', l: 'Request Change to the Proposed Rate' },
      { m: 'action_request_retire', l: 'Request Retirement', ask: 'Why is the rate retired?', kwarg: 'reason' }
    ] },
  'M11-brand': { kind: 'table_report', module: 'M11', report: 'brand_reimbursement', title: 'Brand Reimbursement Rates', period: false },
  'M11-adjust': { kind: 'model_list', model: 'fix.dynamic.price.rule', stateField: 'active',
    cols: ['name', 'channel', 'rule_type', 'adjustment_pct', 'surge_multiplier', 'active'],
    actions: [
      { m: 'action_disable', l: 'Disable Rule (guardrail)', ask: 'Why is the rule disabled?', kwarg: 'reason' },
      { m: 'action_enable', l: 'Re-enable Rule (Releaser, not the author)' }
    ] },
  'M11-discounts': { kind: 'model_list', model: 'fix.discount.approval', stateField: 'state',
    cols: ['quotation_id', 'discount_pct', 'state', 'approval_state', 'approved_by', 'justification'],
    // Approved or rejected from the approver's M63 inbox (A03 audit R7).
    actions: [
      { m: 'action_request_approval', l: 'Request Discount Approval', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M11-floors': { kind: 'model_list', model: 'fix.price.floor', stateField: 'active',
    cols: ['product_code', 'name', 'floor_price', 'proposed_override_price', 'dofa_tier_required', 'approval_state', 'dofa_approved', 'active'],
    // A below-floor override is a DOFA decision from the approver's M63 inbox;
    // the floor itself changes only through an approved price change.
    actions: [
      { m: 'action_request_approval', l: 'Request Below-Floor Override (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Override Request' },
      { m: 'action_request_floor_change', l: 'Request Floor Change (staged on the form)' },
      { m: 'action_request_retire', l: 'Request Floor Retirement', ask: 'Why is the floor retired?', kwarg: 'reason' }
    ] },
  'M11-promos': { kind: 'model_list', model: 'fix.promotion', stateField: 'state',
    cols: ['code', 'name', 'discount_type', 'value', 'channel', 'valid_from', 'valid_until', 'state', 'approval_state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' },
      { m: 'action_end', l: 'End Promotion Early', ask: 'Why does it end early?', kwarg: 'reason' }
    ] },
  'M11-simulate': { kind: 'model_list', model: 'fix.price.simulation', stateField: 'state',
    cols: ['name', 'catalogue_item_id', 'rate_card_id', 'state', 'requested_by', 'computed_at'],
    actions: [{ m: 'action_compute', l: 'Run Simulation (engine)' }] },
  'M11-changes': { kind: 'model_list', model: 'fix.price.change', stateField: 'state',
    cols: ['name', 'target_type', 'change_type', 'product_code', 'current_value', 'proposed_value', 'state', 'approval_state', 'applied_by'],
    // A04 audit M11-5: the only way a live rate or floor moves.
    actions: [
      { m: 'action_submit', l: 'Submit for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' },
      { m: 'action_cancel', l: 'Cancel Draft' }
    ] },
  'M11-policies': { kind: 'model_list', model: 'fix.discount.policy', stateField: 'state',
    cols: ['name', 'role', 'min_pct', 'max_pct', 'requires_approval', 'approval_tier', 'state', 'approval_state'],
    // The one discount ladder (BRU-PRC-06 until a band is released).
    actions: [
      { m: 'action_submit', l: 'Submit Band for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' },
      { m: 'action_retire', l: 'Retire Band (Releaser)' }
    ] },
  'M11-realised': { kind: 'table_report', module: 'M11', report: 'realised_vs_card', title: 'Realised-Price Analytics', period: false },

  /* Report chips -> their own computed pack */
  'M11-rpt-realised': { kind: 'table_report', module: 'M11', report: 'realised_vs_card', title: 'Realised Price vs Card', period: false },
  'M11-rpt-discount': { kind: 'table_report', module: 'M11', report: 'discount_register', title: 'Discount Register by Approver', period: false },
  'M11-rpt-util': { kind: 'table_report', module: 'M11', report: 'rate_card_utilisation', title: 'Rate-Card Utilisation', period: false },
  'M11-rpt-margin': { kind: 'table_report', module: 'M11', report: 'margin_by_line', title: 'Margin by Service Line', period: false },
  'M11-rpt-promo': { kind: 'table_report', module: 'M11', report: 'promotion_effectiveness', title: 'Promotion Effectiveness', period: false },
  'M11-rpt-brand': { kind: 'table_report', module: 'M11', report: 'brand_reimbursement', title: 'Brand Reimbursement Recovery', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M11-form-book': {
    kind: 'model_form',
    model: 'fix.price.book',
    title: 'Price Book',
    back: 'M11-books',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'general', label: '1. Book Identity', bn: '১. সাধারণ তথ্য', icon: '📘', badge: '3' },
      { id: 'governance', label: '2. Lifecycle & Status', bn: '২. অনুমোদন ও নিয়ন্ত্রণ', icon: '✅', badge: '2' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '⏱️', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Price Book Identity',
        note: 'A price book is the versioned container a rate card is published from. Codes are immutable once a version is live.',
        fields: [
          { name: 'name', label: "Book Name", required: true },
          { name: 'code', label: "Book Code", required: true },
          { name: 'currency_id', label: "Currency", required: true }
        ] },
      { tab: 'governance', title: 'Lifecycle & Status',
        fields: [
          { name: 'state', label: "Lifecycle State", readonly: true },
          { name: 'active_version_id', label: "Version in Force", readonly: true },
          { name: 'active', label: "Active" }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'company_id', label: "Legal Entity" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },


  'M11-form-card': {
    kind: 'model_form',
    model: 'fix.rate.card',
    title: 'Standard Commercial Rate Card',
    back: 'M11-labour',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'identity', label: '1. Identity & Scope', bn: '১. রেট পরিচিতি', icon: '🏷️', badge: '4' },
      { id: 'pricing', label: '2. Labor & Parts Rates', bn: '২. মূল্য ও মার্জিন', icon: '💵', badge: '3' },
      { id: 'multipliers', label: '3. Surge Multipliers', bn: '৩. সার্জ গুণক', icon: '📈', badge: '2' },
      { id: 'statutory', label: '4. Statutory Tax & NBR', bn: '৪. ভ্যাট ও কর', icon: '⚖️', badge: '2' },
      { id: 'governance', label: '5. Governance & DOFA', bn: '৫. ফ্লোর ও অনুমোদন', icon: '🏛️', badge: '3' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'identity', title: 'Rate Scope & Catalogue Association',
        note: 'Published pricing schedule for workshop labor, onsite field service, and genuine spare parts.',
        fields: [
          { name: 'product_code', required: true, label: 'Product SKU / Service Code' },
          { name: 'line_type', required: true, label: 'Service Line Classification' },
          { name: 'catalogue_item_id', label: 'Associated Catalogue Item (M37)' },
          { name: 'state', label: 'Release State', readonly: true },
          { name: 'active', label: 'Active Rate Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Base Tariff & Tier Qualification',
        fields: [
          { name: 'unit_price', required: true, label: 'Base Rate (VAT-exclusive BDT)' },
          { name: 'min_tier', label: 'Customer Tier Requirement' }
        ] },
      { tab: 'multipliers', title: 'Effective Windows & Dynamic Surge Rules',
        fields: [
          { name: 'valid_from', label: 'Tariff Effective From' },
          { name: 'valid_to', label: 'Tariff Valid Until' }
        ] },
      { tab: 'statutory', title: 'Statutory VAT & Mushak Alignment',
        note: 'All rate card items must comply with NBR standard VAT rates and Mushak 6.3 invoice rules.',
        fields: [] },
      { tab: 'governance', title: 'Price Floor Governance & Delegation of Authority',
        note: 'A released rate changes only through a price change that a Price-Book Releaser other than its author approves (BRU-PRC-07). Stage the new rate and reason here, then use Request Change.',
        fields: [
          { name: 'proposed_unit_price', label: 'Proposed Rate (staged)' },
          { name: 'change_reason', label: 'Change Reason', type: 'text' },
          { name: 'released_by', label: 'Released By', readonly: true },
          { name: 'released_at', label: 'Released On', readonly: true }
        ] },
      { tab: 'vault', title: 'Rate Card Circulars & Approval Documents',
        note: 'Executive committee pricing approvals, OEM recommended pricing circulars, and market parity surveys.',
        fields: [] }
    ]
  },
  'M11-form-policy': {
    kind: 'model_form',
    model: 'fix.discount.policy',
    title: 'Discount Policy',
    back: 'M11-discounts',
    tabs: [
      { id: 'general', label: '1. Policy Identity', bn: '১. সাধারণ তথ্য', icon: '📋', badge: '2' },
      { id: 'commercial', label: '2. Discount Band', bn: '২. বাণিজ্যিক শর্ত', icon: '💰', badge: '3' },
      { id: 'governance', label: '3. Approval Requirement', bn: '৩. অনুমোদন ও নিয়ন্ত্রণ', icon: '🔐', badge: '1' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Policy Identity',
        fields: [
          { name: 'name', label: "Policy Name", required: true },
          { name: 'role', label: "Applies to Role" }
        ] },
      { tab: 'commercial', title: 'Permitted Discount Band',
        note: 'The band a holder of this role may grant unaided. Anything beyond it raises a fix.discount.approval for a second signature.',
        fields: [
          { name: 'min_pct', label: "Minimum Discount %" },
          { name: 'max_pct', label: "Maximum Discount %" },
          { name: 'active', label: "Active" }
        ] },
      { tab: 'governance', title: 'Approval Requirement',
        note: 'A band is part of the discount ladder only once a Price-Book Releaser other than its author releases it (M63 inbox).',
        fields: [
          { name: 'requires_approval', label: "Requires a Second Signature" },
          { name: 'approval_tier', label: "Approving DOFA Tier" },
          { name: 'state', label: "Band State", readonly: true },
          { name: 'approval_state', label: "Approval", readonly: true },
          { name: 'approved_by', label: "Released By", readonly: true }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'company_id', label: "Legal Entity" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },

  'M11-form-discount-approval': {
    kind: 'model_form',
    model: 'fix.discount.approval',
    title: 'Discount Approval',
    back: 'M11-discounts',
    status: { field: 'state' },
    tabs: [
      { id: 'request', label: '1. Discount Requested', bn: '১. অনুরোধকৃত ডিসকাউন্ট', icon: '🏷️', badge: '3' },
      { id: 'authority', label: '2. Approval Authority', bn: '২. অনুমোদন কর্তৃপক্ষ', icon: '🔐', badge: '2' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'request', title: 'Requested Concession',
        note: 'A discount beyond the rate card is a concession: it carries a stated justification, and the approver is not the requester.',
        fields: [
          { name: 'quotation_id', required: true, label: "Quotation" },
          { name: 'discount_pct', required: true, label: "Discount Requested (%)" },
          { name: 'justification', label: "Commercial Justification", type: 'text' }
        ] },
      { tab: 'authority', title: 'Delegation of Financial Authority', fields: [
        { name: 'approved_by', label: "Approved By", readonly: true },
        { name: 'state', label: "Approval State" }
      ] },
      { tab: 'audit', title: 'System Audit Trail', fields: [
        { name: 'operating_unit_id', label: "Operating Unit" },
        { name: 'company_id', label: "Legal Entity" },
        { name: 'create_date', label: "Raised On", readonly: true }
      ] }
    ]
  },
  'M11-form-promo': {
    kind: 'model_form',
    model: 'fix.promotion',
    title: 'Promotion',
    back: 'M11-promos',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Promotion Identity', bn: '১. সাধারণ তথ্য', icon: '🏷️', badge: '3' },
      { id: 'commercial', label: '2. Discount Mechanics', bn: '২. বাণিজ্যিক শর্ত', icon: '💰', badge: '3' },
      { id: 'schedule', label: '3. Validity Window', bn: '৩. সময়সূচি', icon: '📅', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Promotion Identity',
        fields: [
          { name: 'name', label: "Promotion Name", required: true },
          { name: 'code', label: "Promo Code", required: true },
          { name: 'channel', label: "Sales Channel" }
        ] },
      { tab: 'commercial', title: 'Discount Mechanics',
        fields: [
          { name: 'discount_type', label: "Discount Type" },
          { name: 'value', label: "Discount Value" },
          { name: 'stackable', label: "Stackable with Other Promotions" },
          { name: 'priority', label: "Priority" },
          { name: 'budget_amount', label: "Budget (BDT)" },
          { name: 'budget_used', label: "Budget Used", readonly: true },
          { name: 'max_uses', label: "Usage Cap" },
          { name: 'use_count', label: "Times Used", readonly: true },
          { name: 'state', label: "Promotion State", readonly: true },
          { name: 'approval_state', label: "Approval", readonly: true },
          { name: 'approved_by', label: "Released By", readonly: true }
        ] },
      { tab: 'schedule', title: 'Validity Window',
        note: 'A promotion outside its window must not price: the dates are the control, not a label.',
        fields: [
          { name: 'valid_from', label: "Valid From" },
          { name: 'valid_until', label: "Valid Until" }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'company_id', label: "Legal Entity" },
          { name: 'active', label: "Active" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },
  'M11-form-simulation': {
    kind: 'model_form',
    model: 'fix.price.simulation',
    title: 'Price Simulation',
    back: 'M11-simulate',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Simulation Request', bn: '১. সাধারণ তথ্য', icon: '🧪', badge: '3' },
      { id: 'commercial', label: '2. Inputs', bn: '২. বাণিজ্যিক শর্ত', icon: '📥', badge: '2' },
      { id: 'result', label: '3. Computed Result', bn: '৩. ফলাফল', icon: '📊', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Simulation Request',
        note: 'A what-if run against the live rate card. Simulations never write a price; they explain one.',
        fields: [
          { name: 'name', label: "Reference", required: true },
          { name: 'catalogue_item_id', label: "Catalogue Item" },
          { name: 'rate_card_id', label: "Rate Card" }
        ] },
      { tab: 'commercial', title: 'Inputs',
        fields: [
          { name: 'input_json', label: "Input Parameters (JSON: quantity, customer_tier, contract_no, channel, price)", type: 'text' },
          { name: 'state', label: "State", readonly: true }
        ] },
      { tab: 'result', title: 'Computed Result',
        fields: [
          { name: 'result_json', label: "Computed Result", type: 'text', readonly: true },
          { name: 'computed_at', label: "Computed At", readonly: true }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'requested_by', label: "Requested By", readonly: true },
          { name: 'company_id', label: "Legal Entity" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },
  'M11-form-version': {
    kind: 'model_form',
    model: 'fix.price.version',
    title: 'Price Book Version',
    back: 'M11-versions',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Version Identity', bn: '১. সাধারণ তথ্য', icon: '🔖', badge: '3' },
      { id: 'schedule', label: '2. Effective Dating', bn: '২. সময়সূচি', icon: '📅', badge: '1' },
      { id: 'governance', label: '3. Approval', bn: '৩. অনুমোদন ও নিয়ন্ত্রণ', icon: '✅', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Version Identity',
        fields: [
          { name: 'name', label: "Version Name", required: true },
          { name: 'book_id', label: "Price Book", required: true },
          { name: 'version', label: "Version No." }
        ] },
      { tab: 'schedule', title: 'Effective Dating',
        note: 'A version prices from its effective date. Back-dating a live version restates history, so the date is governed.',
        fields: [
          { name: 'effective_from', label: "Effective From" }
        ] },
      { tab: 'governance', title: 'Approval',
        fields: [
          { name: 'state', label: "Lifecycle State", readonly: true },
          { name: 'approval_state', label: "Approval", readonly: true },
          { name: 'submitted_by', label: "Submitted By", readonly: true },
          { name: 'approved_by', label: "Approved By", readonly: true },
          { name: 'rejection_reason', label: "Returned Because", type: 'text', readonly: true }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'note', label: "Notes", type: 'text' },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },


  'M11-form-floor': {
    kind: 'model_form',
    model: 'fix.price.floor',
    title: 'Statutory Price Floor Rule',
    back: 'M11-floors',
    status: { field: 'active', labels: { true: 'Active Rule', false: 'Inactive' } },
    tabs: [
      { id: 'floor_scope', label: '1. Product Code & Scope', bn: '১. পণ্য কোড ও পরিধি', icon: '🏷️', badge: '4' },
      { id: 'pricing_limit', label: '2. Floor Price & Limits', bn: '২. ন্যূনতম মূল্য ও সীমা', icon: '💵', badge: '2' },
      { id: 'dofa_override', label: '3. DOFA Override Governance', bn: '৩. ডোফা ওভাররাইড', icon: '🔐', badge: '3' }
    ],
    sections: [
      { tab: 'floor_scope', title: 'Target Identification', note: 'The minimum sellable price per product code. Quotes below it trigger floor breach controls.',
        fields: [
          { name: 'name', required: true, label: 'Floor Rule Name' },
          { name: 'product_code', required: true, label: 'Product Code' },
          { name: 'catalogue_item_id', label: 'Catalogue Item' },
          { name: 'book_id', label: 'Price Book Link' }
        ] },
      { tab: 'pricing_limit', title: 'Statutory Pricing Limit',
        note: 'The floor is set when the rule is created and then changes only through a price change a Price-Book Releaser approves. Stage the new floor and reason, then use Request Floor Change.',
        fields: [
          { name: 'floor_price', required: true, label: 'Floor Price (BDT)' },
          { name: 'proposed_floor_price', label: 'Proposed New Floor (staged)' },
          { name: 'floor_change_reason', label: 'Floor Change Reason', type: 'text' }
        ] },
      { tab: 'dofa_override', title: 'Delegation of Financial Authority (DOFA)', note: 'A price below the floor needs a DOFA approval from the approver inbox; the tier follows how far below the floor the proposed price sits, and the approval covers only that price.',
        fields: [
          { name: 'proposed_override_price', label: 'Proposed Below-Floor Price' },
          { name: 'dofa_justification', label: 'Business Justification', type: 'text' },
          { name: 'dofa_tier', label: 'Required DOFA Tier', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'dofa_override_approved', label: 'DOFA Override Approved', readonly: true },
          { name: 'dofa_override_user_id', label: 'DOFA Approver', readonly: true },
          { name: 'active', label: 'Active Floor Enforcement', readonly: true }
        ] }
    ]
  },
  'M11-form-pricerule': {
    kind: 'model_form',
    model: 'fix.dynamic.price.rule',
    title: "Dynamic Price Rule",
    back: 'M11-adjust',
    tabs: [
      { id: 'general', label: '1. Rule Identity', bn: '১. নিয়ম পরিচয়', icon: '🏷️', badge: '5' },
      { id: 'commercial', label: '2. Adjustment & Bounds', bn: '২. সমন্বয় ও সীমা', icon: '💰', badge: '4' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ', icon: '🔗', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Rule Identity & Scope',
        note: 'A pricing rule adjusts the base rate by a stated condition. The rule must state its own basis — an unexplained adjustment is not defensible to a customer or an auditor.',
        fields: [
          { name: 'name', required: true, label: "Rule Name" },
          { name: 'rule_type', required: true, label: "Rule Type" },
          { name: 'channel', required: true, label: "Sales Channel" },
          { name: 'active', label: "Active", readonly: true },
          { name: 'disabled_reason', label: "Disabled Because", readonly: true },
          { name: 'company_id', required: true, label: "Legal Entity" }
        ] },
      { tab: 'commercial', title: 'Adjustment and its Guard Rails',
        note: 'Adjustments are computed in Decimal and quantised to the paisa (FLAW-11.1). Minimum and maximum bound what the rule may do, and are enforced by a model constraint.',
        fields: [
          { name: 'adjustment_pct', label: "Adjustment %" },
          { name: 'surge_multiplier', label: "Surge Multiplier" },
          { name: 'min_adjustment', label: "Minimum Adjustment %" },
          { name: 'max_adjustment', label: "Maximum Adjustment %" }
        ] },
      { tab: 'relations', title: 'Rate Card Basis', fields: [
        { name: 'rate_card_id', label: "Rate Card Base" },
        { name: 'currency_id', required: true, label: "Currency" }
      ] },
      { tab: 'audit', title: 'System Audit Trail', fields: [
        { name: 'operating_unit_id', label: "Operating Unit" },
        { name: 'create_date', label: "Created", readonly: true },
        { name: 'write_date', label: "Last Updated", readonly: true }
      ] }
    ]
  },
  'M11-rpt-floors': { kind: 'table_report', module: 'M11', report: 'floors_vs_rate', title: "Floor vs Realised Rate", period: false },

  'M11-form-change': {
    kind: 'model_form',
    model: 'fix.price.change',
    title: 'Price Change Request',
    back: 'M11-changes',
    status: { field: 'state' },
    tabs: [
      { id: 'request', label: '1. Change Requested', bn: '১. অনুরোধকৃত পরিবর্তন', icon: '💱', badge: '6' },
      { id: 'decision', label: '2. Release Decision', bn: '২. অনুমোদন সিদ্ধান্ত', icon: '✅', badge: '4' }
    ],
    sections: [
      { tab: 'request', title: 'What Changes and Why',
        note: 'A released rate or a floor moves only through this request; a Price-Book Releaser who did not raise it decides it from the M63 inbox (BRU-PRC-07).',
        fields: [
          { name: 'target_type', label: "Target", required: true },
          { name: 'change_type', label: "Change", required: true },
          { name: 'rate_card_id', label: "Rate Card" },
          { name: 'floor_id', label: "Price Floor" },
          { name: 'proposed_value', label: "New Price (BDT)" },
          { name: 'reason', label: "Reason", type: 'text', required: true }
        ] },
      { tab: 'decision', title: 'Release Decision', fields: [
        { name: 'current_value', label: "Price When Raised", readonly: true },
        { name: 'approval_state', label: "Approval", readonly: true },
        { name: 'applied_by', label: "Released By", readonly: true },
        { name: 'applied_at', label: "Applied On", readonly: true }
      ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M11-price-explanation': { kind: 'model_list', model: 'fix.price.explanation', create: false,
    cols: ['name', 'company_id', 'operating_unit_id', 'rule_id', 'currency_id', 'base_price', 'final_price'],
    // append-only trail (BRU-PRC-02): reconstruct, never edit
    actions: [{ m: 'action_reconstruct', l: 'Reconstruct from the Rule' }] },

  'M11-form-price-explanation': {
    kind: 'model_form',
    model: 'fix.price.explanation',
    title: "Price Explanation",
    back: 'M11-price-explanation',
    tabs: [
      { id: 'general', label: '1. Explanation Header', bn: '১. ব্যাখ্যার শিরোনাম', icon: '📄', badge: '3' },
      { id: 'commercial', label: '2. Price Derivation', bn: '২. মূল্য নির্ধারণ', icon: '💵', badge: '4' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Explanation Header',
        note: 'Every dynamic price writes an explanation record. This is the trail a customer dispute or a commercial audit reads back; it is append-only (BRU-PRC-02).',
        fields: [
          { name: 'name', required: true, label: "Reference", readonly: true },
          { name: 'company_id', required: true, label: "Legal Entity", readonly: true },
          { name: 'currency_id', required: true, label: "Currency", readonly: true }
        ] },
      { tab: 'commercial', title: 'How the Price Was Derived', fields: [
        { name: 'rule_id', label: "Applied Rule", readonly: true },
        { name: 'base_price', label: "Base Price", readonly: true },
        { name: 'final_price', label: "Final Price", readonly: true },
        { name: 'rules_applied', label: "Rules Applied", type: 'text', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit Trail', fields: [
        { name: 'operating_unit_id', label: "Operating Unit", readonly: true },
        { name: 'model_driven', label: "Model Driven", readonly: true },
        { name: 'create_date', label: "Computed At", readonly: true }
      ] }
    ]
  }
};

/* Built-in report chips -> their computed pack. These seven routes used to
 * sit inside SCREENS (so the merge never saw them and every M11 report chip
 * answered "arrives with the workspace phase"). */
export const REPORT_ROUTES = {
  'M11:Floor vs Realised Rate': 'M11-rpt-floors',
  'M11:Realised Price vs Card': 'M11-rpt-realised',
  'M11:Discount Register by Approver': 'M11-rpt-discount',
  'M11:Rate-Card Utilisation': 'M11-rpt-util',
  'M11:Margin by Service Line': 'M11-rpt-margin',
  'M11:Promotion Effectiveness': 'M11-rpt-promo',
  'M11:Brand Reimbursement Recovery': 'M11-rpt-brand'
};

export const FORM_MODELS = {
  'M11:Price Book': 'fix.price.book',
  'M11:Rate Card': 'fix.rate.card',
  'M11:Discount Policy': 'fix.discount.policy',
  'M11:Promotion': 'fix.promotion',
  'M11:Price Simulation Request': 'fix.price.simulation'
};

export const FORM_CHIPS = {
  'M11:Dynamic Price Rule': 'M11-form-pricerule',
  'M11:Price Book': 'M11-form-book',
  'M11:Rate Card': 'M11-form-card',
  'M11:Discount Policy': 'M11-form-policy',
  'M11:Promotion': 'M11-form-promo',
  'M11:Price Simulation Request': 'M11-form-simulation',
  'M11:__by_model__': {
    'fix.price.explanation': 'M11-form-price-explanation',
    'fix.dynamic.price.rule': 'M11-form-pricerule',
    'fix.price.book': 'M11-form-book',
    'fix.rate.card': 'M11-form-card',
    'fix.discount.policy': 'M11-form-policy',
    'fix.discount.approval': 'M11-form-discount-approval',
    'fix.promotion': 'M11-form-promo',
    'fix.price.simulation': 'M11-form-simulation',
    'fix.price.version': 'M11-form-version',
    'fix.price.floor': 'M11-form-floor',
    'fix.price.change': 'M11-form-change'
  },
  'M11:__by_screen__': {
    'M11-price-explanation': 'M11-form-price-explanation',
    'M11-adjust': 'M11-form-pricerule',
    'M11-books': 'M11-form-book',
    'M11-labour': 'M11-form-card',
    'M11-parts': 'M11-form-card',
    'M11-versions': 'M11-form-version',
    'M11-floors': 'M11-form-floor',
    'M11-promos': 'M11-form-promo',
    'M11-simulate': 'M11-form-simulation',
    'M11-discounts': 'M11-form-discount-approval',
    'M11-changes': 'M11-form-change',
    'M11-policies': 'M11-form-policy'
  }
};

export const CREATE = {
  M11: { screen: 'M11-form-book', model: 'fix.price.book', label: 'Price Book' }
};
