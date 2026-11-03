/** @odoo-module **/
/* A04 · Commercial & Revenue — M40 Partner & Channel (v2 rebuild).
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 4 forms / freg 80.
 * Partners (8) and referrals (7) are real; authorisations, deals, rebates,
 * franchises and conflicts are new. Partner revenue = recorded referral
 * commission + won deal value; co-marketing is a declared gap. */

export const MODULE = {
  area: 'A04', code: 'M40', en: 'Partner & Channel', title: 'M40 · Partner & Channel',
  bn: 'পার্টনার ও চ্যানেল', icon: '🤝',
  desc: 'Partner master and onboarding, brand authorisations, alliances, referral programme, deal registration, resellers, franchises, rebates and MDF, channel conflict and partner health/ranking.',
  kpis: [
    { l: 'Brand Partners', m: 'brand_partners' },
    { l: 'Referral Partners', m: 'referral_partners' },
    { l: 'Deal Registrations', m: 'deal_registrations' },
    { l: 'Partner Revenue MTD', m: 'partner_revenue_mtd', prefix: '৳ ' },
    { l: 'Audits Due (90d)', m: 'audits_due_90d' },
    { l: 'Rebates Accrued', m: 'rebates_accrued', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Partner Master', screens: [
      { id: 'M40-partners', en: 'Partner Directory', bn: 'পার্টনার ডিরেক্টরি', t: 'g' },
      { id: 'M40-brand', en: 'Brand Partner Relations', bn: 'ব্র্যান্ড পার্টনার', t: 'g' },
      { id: 'M40-authorisation', en: 'Authorisation & Certification', bn: 'অনুমোদন', t: 'g' }
    ]},
    { en: 'Programmes', screens: [
      { id: 'M40-alliance', en: 'Alliance Benefits', bn: 'অ্যালায়েন্স সুবিধা', t: 'g' },
      { id: 'M40-referral', en: 'Referral Programme', bn: 'রেফারেল কার্যক্রম', t: 'g' },
      { id: 'M40-dealreg', en: 'Deal Registration', bn: 'ডিল নিবন্ধন', t: 'g' },
      { id: 'M40-reseller', en: 'Resellers', bn: 'রিসেলার', t: 'g' },
      { id: 'M40-franchise', en: 'Franchise Management', bn: 'ফ্র্যাঞ্চাইজি', t: 'g' }
    ]},
    { en: 'Commercial', screens: [
      { id: 'M40-rebates', en: 'Rebates & MDF', bn: 'রিবেট ও MDF', t: 'g' },
      { id: 'M40-comarketing', en: 'Co-Marketing', bn: 'কো-মার্কেটিং', t: 'g' },
      { id: 'M40-conflict', en: 'Channel Conflict', bn: 'চ্যানেল দ্বন্দ্ব', t: 'g' }
    ]},
    { en: 'Performance', screens: [
      { id: 'M40-health', en: 'Health & Risk', bn: 'স্বাস্থ্য ও ঝুঁকি', t: 'r' },
      { id: 'M40-ranking', en: 'Ranking & Scorecards', bn: 'র্যাঙ্কিং', t: 'r' }
    ]}
  ],
  reports: ['Partner Revenue Contribution', 'Referral Conversion', 'Brand Audit Calendar', 'Rebate Accruals', 'Channel Conflict Log', 'Deal Register'],
  forms: ['Partner', 'Deal Registration', 'Rebate Scheme', 'Franchise Agreement'],
  cross: ['M07 CRM', 'M12 Marketplace', 'M35 Marketing', 'M20 AR'],
  freg: { src: 80, sub: [
    ['1', 'Partner Master', 10, { model: 'fix.partner', cols: ['name', 'state', 'partner_type', 'commission_rate', 'territory', 'technical_audit_score'], screens: ['M40-partners'] }],
    ['2', 'Recruitment & Onboarding', 8, { model: 'fix.partner.authorisation', cols: ['name', 'state', 'partner_id', 'brand_id', 'scope', 'valid_from', 'valid_to'], screens: ['M40-authorisation'] }],
    ['3', 'Brand Relations', 9, { model: 'fix.partner.authorisation', cols: ['name', 'partner_id', 'brand_id', 'valid_to', 'state'], screens: ['M40-brand', 'M40-authorisation'] }],
    ['4', 'Alliances', 6, { model: 'fix.partner', cols: ['name', 'territory', 'commission_rate', 'contract_id', 'state'], screens: ['M40-alliance', 'M40-comarketing', 'M40-partners'], domain: [['partner_type', '=', 'alliance']] }],
    ['5', 'Referrals', 8, { model: 'fix.referral', cols: ['name', 'state', 'partner_id', 'referred_partner_id', 'base_amount', 'commission_amount'], screens: ['M40-referral', 'M40-rpt-referral'] }],
    ['6', 'Deal Registration', 7, { model: 'fix.partner.deal', cols: ['name', 'state', 'partner_id', 'customer_id', 'value', 'registered_on'], screens: ['M40-dealreg', 'M40-rpt-deals'] }],
    ['7', 'Resellers', 6, { model: 'fix.partner', cols: ['name', 'partner_id', 'territory', 'commission_rate', 'state'], screens: ['M40-reseller', 'M40-partners'], domain: [['partner_type', '=', 'reseller']] }],
    ['8', 'Franchise', 9, { model: 'fix.partner.franchise', cols: ['name', 'state', 'partner_id', 'territory', 'fee', 'start_date', 'end_date'], screens: ['M40-franchise'] }],
    ['9', 'Commercial Terms', 8, { model: 'fix.partner.rebate', cols: ['name', 'state', 'partner_id', 'amount', 'period', 'basis', 'rate'], screens: ['M40-rebates', 'M40-rpt-rebates'] }],
    ['10', 'Performance', 9, { model: 'fix.partner.conflict', cols: ['name', 'state', 'customer_id', 'partner_a_id', 'partner_b_id', 'dofa_arbitrator_id', 'dofa_decision'], screens: ['M40-conflict', 'M40-health', 'M40-ranking'] }]
  ] }
};

export const SCREENS = {
  'M40-partners': { kind: 'model_list', model: 'fix.partner', stateField: 'state',
    cols: ['name', 'partner_id', 'partner_type', 'territory', 'commission_rate', 'state'] },
  'M40-brand': { kind: 'table_report', module: 'M40', report: 'brand_partners', title: 'Brand Partner Relations', period: false },
  'M40-authorisation': { kind: 'model_list', model: 'fix.partner.authorisation', stateField: 'state',
    cols: ['name', 'partner_id', 'brand_id', 'valid_from', 'valid_to', 'state'] },
  'M40-alliance': { kind: 'table_report', module: 'M40', report: 'alliance_report', title: 'Alliance Benefits', period: false },
  'M40-referral': { kind: 'model_list', model: 'fix.referral', stateField: 'state',
    cols: ['name', 'partner_id', 'referred_partner_id', 'base_amount', 'commission_amount', 'state'] },
  'M40-dealreg': { kind: 'model_list', model: 'fix.partner.deal', stateField: 'state',
    cols: ['name', 'partner_id', 'customer_id', 'value', 'registered_on', 'state'] },
  'M40-reseller': { kind: 'table_report', module: 'M40', report: 'reseller_report', title: 'Resellers', period: false },
  'M40-franchise': { kind: 'model_list', model: 'fix.partner.franchise', stateField: 'state',
    cols: ['name', 'partner_id', 'territory', 'fee', 'start_date', 'end_date', 'state'] },
  'M40-rebates': { kind: 'model_list', model: 'fix.partner.rebate', stateField: 'state',
    cols: ['name', 'partner_id', 'period', 'kind', 'basis', 'rate', 'amount', 'state'] },
  'M40-comarketing': { kind: 'table_report', module: 'M40', report: 'comarketing_gap', title: 'Co-Marketing', period: false },
  'M40-conflict': { kind: 'model_list', model: 'fix.partner.conflict', stateField: 'state',
    cols: ['name', 'partner_a_id', 'partner_b_id', 'customer_id', 'state'] },
  'M40-health': { kind: 'table_report', module: 'M40', report: 'health', title: 'Health & Risk', period: false },
  'M40-ranking': { kind: 'table_report', module: 'M40', report: 'ranking', title: 'Ranking & Scorecards', period: false },

  /* Report chips -> their own computed pack */
  'M40-rpt-revenue': { kind: 'table_report', module: 'M40', report: 'partner_revenue', title: 'Partner Revenue Contribution', period: false },
  'M40-rpt-referral': { kind: 'table_report', module: 'M40', report: 'referral_conversion', title: 'Referral Conversion', period: false },
  'M40-rpt-audits': { kind: 'table_report', module: 'M40', report: 'brand_audit_calendar', title: 'Brand Audit Calendar', period: false },
  'M40-rpt-rebates': { kind: 'table_report', module: 'M40', report: 'rebate_accruals', title: 'Rebate Accruals', period: false },
  'M40-rpt-conflict': { kind: 'table_report', module: 'M40', report: 'conflict_log', title: 'Channel Conflict Log', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M40-form-partner': {
    kind: 'model_form',
    model: 'fix.partner',
    title: 'Channel Partner & Franchise Master',
    back: 'M40-partners',
    status: { field: 'state' },
    tabs: [
      { id: 'partner', label: '1. Partner Master', bn: '১. পার্টনার পরিচিতি', icon: '🏢', badge: '6' },
      { id: 'brand_auth', label: '2. Brand Authorisations', bn: '২. ব্র্যান্ড অনুমোদন', icon: '🛡️', badge: '2' },
      { id: 'financials', label: '3. Financials & Rebates', bn: '৩. কমিশন ও রিবেট', icon: '২', badge: '3' },
      { id: 'statutory', label: '4. Statutory Tax & KYC', bn: '৪. কেওয়াইসি ও কর', icon: '⚖️', badge: '5' },
      { id: 'technical', label: '5. Technical Audits & ESD', bn: '৫. টেকনিক্যাল অডিট', icon: '🔬', badge: '2' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'partner', title: 'Channel Partner Identity',
        note: 'Authorized franchise, reseller, or referral partner under 1000FiX partner governance.',
        fields: [
          { name: 'name', required: true, label: 'Partner Entity Name' },
          { name: 'partner_id', required: true, label: 'Party Master Record (M33)' },
          { name: 'partner_type', required: true, label: 'Partnership Classification' },
          { name: 'territory', label: 'Assigned Geographic Territory' },
          { name: 'contract_id', label: 'Master Franchise Agreement (M08)' },
          { name: 'state', required: true, label: 'Partnership Status' }
        ] },
      { tab: 'brand_auth', title: 'Brand Certifications & Scopes',
        note: 'Brand certifications authorizing partner workshop technicians to perform warranty repairs.',
        fields: [] },
      { tab: 'financials', title: 'Commercial Commission & Volume Rebates',
        fields: [
          { name: 'commission_rate', label: 'Standard Referral Commission Rate' }
        ] },
      { tab: 'statutory', title: 'Bangladesh Statutory Compliance & Tax Registrations',
        note: 'Mandatory trade license, e-TIN, and National ID verification under Bangladesh law.',
        fields: [
          { name: 'nid_number', label: 'National ID (NID)' },
          { name: 'tin_number', label: '12-Digit e-TIN' },
          { name: 'trade_license_no', label: 'Trade License Number' },
          { name: 'trade_license_expiry', label: 'Trade License Expiry Date' },
          { name: 'bank_solvency_ref', label: 'Bank Solvency Reference' }
        ] },
      { tab: 'technical', title: 'Technical Compliance, Workshop Tooling & ESD Audit',
        note: 'Annual technical audit score (minimum 85.0% required for volume rebate payouts / FLAW-40.1).',
        fields: [
          { name: 'technical_audit_score', label: 'Technical Audit Score (%)' }
        ] },
      { tab: 'vault', title: 'Partner Agreement & Certificate Vault',
        note: 'Verified trade licenses, bank solvency certificates, ESD audit reports, and franchise agreements.',
        fields: [] }
    ]
  },

  'M40-form-deal': { kind: 'model_form', model: 'fix.partner.deal',
    title: 'Deal Registration', back: 'M40-dealreg',
    status: { field: 'state' },
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
        { name: 'name', label: 'Deal Name', required: true },
        { name: 'state', label: 'State', required: true },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'value', label: 'Deal Value' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'registered_on', label: 'Registered On', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'customer_id', label: 'End Customer' },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M40-form-rebate': {
    kind: 'model_form',
    model: 'fix.partner.rebate',
    title: 'Channel Partner Rebate & MDF Scheme',
    back: 'M40-rebates',
    status: { field: 'state' },
    tabs: [
      { id: 'rebate_header', label: '1. Scheme Identification', bn: '১. স্কিম শনাক্তকরণ', icon: '🏷️', badge: '4' },
      { id: 'computation', label: '2. Basis & Rate', bn: '২. ভিত্তি ও হার', icon: '🧮', badge: '3' },
      { id: 'audit_payout', label: '3. Audit Gate & State', bn: '৩. অডিট গেট ও অবস্থা', icon: '🔒', badge: '1' }
    ],
    sections: [
      { tab: 'rebate_header', title: 'Rebate Scheme Target', note: 'Performance-driven channel partner rebate under statutory withholding rules.',
        fields: [
          { name: 'name', required: true, label: 'Scheme Name' },
          { name: 'partner_id', required: true, label: 'Authorized Partner' },
          { name: 'period', required: true, label: 'Evaluation Period' },
          { name: 'kind', required: true, label: 'Rebate Classification' }
        ] },
      { tab: 'computation', title: 'Stored Computation Formula', fields: [
          { name: 'basis', label: 'Gross Volume Basis (BDT)' },
          { name: 'rate', required: true, label: 'Incentive Rate (decimal)' },
          { name: 'amount', readonly: true, label: 'Gross Rebate Amount (computed BDT)' }
        ] },
      { tab: 'audit_payout', title: 'Technical Audit Gate & Settlement', fields: [
          { name: 'state', required: true, label: 'Settlement State' }
        ] }
    ]
  },
  'M40-form-conflict': {
    kind: 'model_form',
    model: 'fix.partner.conflict',
    title: 'Channel Territory Conflict & Arbitration',
    back: 'M40-conflict',
    status: { field: 'state' },
    tabs: [
      { id: 'parties', label: '1. Contesting Partners', bn: '১. বিবদমান অংশীদার', icon: '👥', badge: '4' },
      { id: 'dispute_narrative', label: '2. Territory Conflict Narrative', bn: '২. অঞ্চল বিরোধের বিবরণ', icon: '📝', badge: '1' },
      { id: 'dofa_arbitration', label: '3. DOFA Arbitration & Outcome', bn: '৩. ডোফা সালিশ ও ফলাফল', icon: '⚖️', badge: '4' }
    ],
    sections: [
      { tab: 'parties', title: 'Contesting Parties', note: 'A territorial or account dispute between registered commercial partners.',
        fields: [
          { name: 'name', required: true, label: 'Conflict Docket Number' },
          { name: 'partner_a_id', required: true, label: 'Partner A (Complainant)' },
          { name: 'partner_b_id', label: 'Partner B (Respondent)' },
          { name: 'customer_id', label: 'Contested Account / Enterprise Customer' }
        ] },
      { tab: 'dispute_narrative', title: 'Factual Conflict Narrative', fields: [
          { name: 'description', required: true, label: 'Incident Statement & Overlap Details', type: 'text' }
        ] },
      { tab: 'dofa_arbitration', title: 'DOFA Arbitration Governance', fields: [
          { name: 'dofa_arbitrator_id', label: 'Appointed DOFA Arbitrator' },
          { name: 'dofa_decision', label: 'Arbitration Ruling Code' },
          { name: 'resolution', label: 'Final Resolution Narrative / Settlement Terms', type: 'text' },
          { name: 'state', required: true, label: 'Docket Status' }
        ] }
    ]
  },
  'M40-form-franchise': { kind: 'model_form', model: 'fix.partner.franchise',
    title: 'Franchise Agreement', back: 'M40-franchise',
    status: { field: 'state' },
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
        { name: 'name', label: 'Agreement Name', required: true },
        { name: 'territory', label: 'Territory', required: true },
        { name: 'state', label: 'State', required: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'fee', label: 'Franchise Fee' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'start_date', label: 'Start Date', required: true },
        { name: 'end_date', label: 'End Date' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M40-form-auth': { kind: 'model_form', model: 'fix.partner.authorisation',
    title: 'Partner Authorisation', back: 'M40-authorisation',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'scope', label: 'Scope' },
        { name: 'state', label: 'State', required: true },
        { name: 'certificate_ref', label: 'Certificate Ref' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'valid_from', label: 'Valid From', required: true },
        { name: 'valid_to', label: 'Valid To', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'brand_id', label: 'Brand' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },
  'M40-form-referral': { kind: 'model_form', model: 'fix.referral',
    title: 'Partner Referral', back: 'M40-referral',
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
        { name: 'name', label: 'Name', required: true },
        { name: 'state', label: 'State', required: true },
        { name: 'payout_state', label: 'Payout State', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'base_amount', label: 'Referred Revenue (Gross)' },
        { name: 'commission_amount', label: 'Commission Earned', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'partner_id', label: 'Referring Partner', required: true },
        { name: 'referred_partner_id', label: 'Referred Customer' },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'commission_ledger_id', label: 'Commission Ledger Entry', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
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
  'M40-rpt-deals': { kind: 'table_report', module: 'M40', report: 'deal_register', title: "Deal Register", period: false },
};

export const REPORT_ROUTES = {
  'M40:Deal Register': 'M40-rpt-deals',
  'M40:Partner Revenue Contribution': 'M40-rpt-revenue',
  'M40:Referral Conversion': 'M40-rpt-referral',
  'M40:Brand Audit Calendar': 'M40-rpt-audits',
  'M40:Rebate Accruals': 'M40-rpt-rebates',
  'M40:Channel Conflict Log': 'M40-rpt-conflict'
};

export const FORM_MODELS = {
  'M40:Partner': 'fix.partner',
  'M40:Deal Registration': 'fix.partner.deal',
  'M40:Rebate Scheme': 'fix.partner.rebate',
  'M40:Franchise Agreement': 'fix.partner.franchise'
};

export const FORM_CHIPS = {
  'M40:Partner Authorisation': 'M40-form-auth',
  'M40:Referral': 'M40-form-referral',
  'M40:Partner': 'M40-form-partner',
  'M40:Deal Registration': 'M40-form-deal',
  'M40:Rebate Scheme': 'M40-form-rebate',
  'M40:Franchise Agreement': 'M40-form-franchise',
  'M40:__by_model__': {
    'fix.partner.authorisation': 'M40-form-auth',
    'fix.referral': 'M40-form-referral',
    'fix.partner': 'M40-form-partner',
    'fix.partner.deal': 'M40-form-deal',
    'fix.partner.rebate': 'M40-form-rebate',
    'fix.partner.franchise': 'M40-form-franchise',
    'fix.partner.conflict': 'M40-form-conflict'
  },
  'M40:__by_screen__': {
    'M40-authorisation': 'M40-form-auth',
    'M40-referral': 'M40-form-referral',
    'M40-partners': 'M40-form-partner',
    'M40-dealreg': 'M40-form-deal',
    'M40-rebates': 'M40-form-rebate',
    'M40-franchise': 'M40-form-franchise',
    'M40-conflict': 'M40-form-conflict'
  }
};

export const CREATE = {
  M40: { screen: 'M40-form-partner', model: 'fix.partner', label: 'Partner' }
};
