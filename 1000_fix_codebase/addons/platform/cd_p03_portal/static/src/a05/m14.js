/** @odoo-module **/
/* A05 — Circular Economy — M14 Trade-In, Refurbishment & Resale (v2.1 D365 multi-tab standard).
 * 100% Dynamics 365 6-tab forms with Document Vault on all 9 forms.
 * All 8 report packs exposed as chips (including Resale Listings & Unit Economics).
 * Zero phantom fields: all fields verified against PostgreSQL fix_dev. */

export const MODULE = {
  area: 'A05', code: 'M14', en: 'Trade-In & Refurbishment', title: 'M14 — Trade-In & Refurbishment',
  bn: 'ট্রেড-ইন ও রিফার্বিশমেন্ট', icon: '🔄',
  desc: 'Trade-in intake across five channels, automated valuation with manual override, IMEI/blacklist provenance screening, settlement and four-eyes payout, refurb work orders, QA and battery health, A–E grading, harvest to parts, graded stock, resale channel and unit economics.',
  kpis: [
    { l: 'Open Trade-Ins', m: 'open_tradeins' },
    { l: 'Payouts Pending', m: 'pending_payouts' },
    { l: 'Refurb Open', m: 'refurb_open' },
    { l: 'Resale Ready', m: 'resale_ready' },
    { l: 'Graded Stock Value', m: 'graded_stock_value', prefix: '৳ ' },
    { l: 'Margin Pipeline', m: 'margin_pipeline', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Trade-In', screens: [
      { id: 'M14-intake', en: 'Trade-In Intake', bn: 'ট্রেড-ইন গ্রহণ', t: 'g' },
      { id: 'M14-valuation', en: 'Automated Valuation', bn: 'স্বয়ংক্রিয় মূল্যায়ন', t: 'c' },
      { id: 'M14-provenance', en: 'Provenance & IMEI Screen', bn: 'আইএমইআই যাচাই', t: 'g' },
      { id: 'M14-settlement', en: 'Settlement', bn: 'পরিশোধ ও নিষ্পত্তি', t: 'g' }
    ]},
    { en: 'Refurbishment', screens: [
      { id: 'M14-orders', en: 'Refurb Work Orders', bn: 'রিফার্বিশমেন্ট কার্যআদেশ', t: 'g' },
      { id: 'M14-qa', en: 'QA & Battery Health', bn: 'কিউএ ও ব্যাটারি স্বাস্থ্য', t: 'g' },
      { id: 'M14-grading', en: 'A–D Grading', bn: 'গ্রেডিং নির্ধারণ', t: 'c' },
      { id: 'M14-harvest', en: 'Harvest to Parts', bn: 'যন্ত্রাংশ সংগ্রহ', t: 'g' }
    ]},
    { en: 'Resale', screens: [
      { id: 'M14-stock', en: 'Graded Stock', bn: 'গ্রেডেড স্টক', t: 'g' },
      { id: 'M14-listings', en: 'Resale Listings', bn: 'পুনর্বিক্রয় তালিকা', t: 'g' },
      { id: 'M14-wty', en: 'Refurb Warranty', bn: 'রিফার্বিশড ওয়ারেন্টি', t: 'g' },
      { id: 'M14-economics', en: 'Unit Economics', bn: 'ইউনিট অর্থনীতি', t: 'r' }
    ]}
  ],
  reports: [
    'Trade-In Margin by Model',
    'Refurb Cost per Grade',
    'Ageing & Markdown',
    'Resale Channel Performance',
    'Harvest Yield',
    'Valuation Queue',
    'Resale Listings',
    'Unit Economics'
  ],
  forms: [
    'Trade-In Intake Dossier',
    'Automated Valuation File',
    'Provenance Screening & Anti-Theft',
    'Settlement & Four-Eyes Payout',
    'Refurbishment Work Order',
    'QA & Battery Health Dossier',
    'Grading Certificate',
    'Harvest to Parts Dossier',
    'Refurbished Warranty Master'
  ],
  cross: ['M06 destruction gate', 'M31 refurb repairs', 'M15 graded stock', 'M38 online resale', 'M18 recycle routing'],
  freg: { src: 84, sub: [
    ['1', 'Intake (5 channels)', 9, { model: 'fix.tradein.request', cols: ['name', 'customer_id', 'device_model_id', 'offered_value', 'state'], screens: ['M14-intake'] }],
    ['2', 'Valuation Engine', 9, { model: 'fix.tradein.valuation', cols: ['name', 'tradein_id', 'market_ref_price', 'computed_offer', 'final_offer'], screens: ['M14-valuation'] }],
    ['3', 'Provenance Screening', 7, { model: 'fix.tradein.provenance', cols: ['name', 'tradein_id', 'imei', 'btrc_neir_status', 'state'], screens: ['M14-provenance'] }],
    ['4', 'Settlement', 8, { model: 'fix.tradein.request', cols: ['name', 'customer_id', 'payout_amount', 'payout_approval_state', 'net_payout'], screens: ['M14-settlement'] }],
    ['5', 'Bulk Buy-Back', 6, { model: 'fix.tradein.request', cols: ['name', 'customer_id', 'marketplace_seller_id', 'offered_value', 'state'], screens: ['M14-intake'] }],
    ['6', 'Destruction Gate', 4, { model: 'fix.tradein.request', cols: ['name', 'device_id', 'wipe_certificate_id', 'state'], screens: ['M14-intake', 'M14-orders'], domain: [['state', 'in', ['collected', 'wiped']]] }],
    ['7', 'Refurbishment Orders', 11, { model: 'fix.refurbishment', cols: ['name', 'tradein_id', 'step', 'technician_id', 'state'], screens: ['M14-orders'] }],
    ['8', 'Grading & QA', 11, { model: 'fix.tradein.grade', cols: ['name', 'tradein_id', 'grade', 'battery_health_pct', 'graded_on'], screens: ['M14-grading', 'M14-qa'] }],
    ['9', 'Resale', 10, { model: 'fix.graded.stock', cols: ['name', 'device_id', 'grade_id', 'resale_price', 'state'], screens: ['M14-stock', 'M14-listings', 'M14-wty', 'M14-economics'] }],
    ['10', 'Harvesting', 9, { model: 'fix.tradein.harvest', cols: ['name', 'component', 'part_name', 'quantity', 'target'], screens: ['M14-harvest'] }]
  ] }
};

export const SCREENS = {
  'M14-intake': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'state',
    cols: ['name', 'customer_id', 'device_model_id', 'offered_value', 'grade', 'state'],
    actions: [
      { m: 'action_send_offer', l: 'Send Offer' },
      { m: 'action_accept', l: 'Accept' },
      { m: 'action_collect', l: 'Collect' },
      { m: 'action_wipe', l: 'Data Wipe' },
      { m: 'action_refurbish', l: 'Refurbish' },
      { m: 'action_grade', l: 'Grade' },
      { m: 'action_resale_ready', l: 'Resale Ready' }
    ] },
  'M14-valuation': { kind: 'model_list', model: 'fix.tradein.valuation', stateField: 'state',
    cols: ['name', 'tradein_id', 'market_ref_price', 'computed_offer', 'final_offer', 'method', 'state'],
    actions: [{ m: 'action_apply_to_tradein', l: 'Apply to Trade-In' }] },
  'M14-provenance': { kind: 'model_list', model: 'fix.tradein.provenance', stateField: 'state',
    cols: ['name', 'tradein_id', 'imei', 'checked_on', 'blacklist_hit', 'stolen_hit', 'state'],
    actions: [
      { m: 'action_clear', l: 'Clear' },
      { m: 'action_flag', l: 'Flag' },
      { m: 'action_run_neir_check', l: 'BTRC NEIR Check' }
    ] },
  'M14-settlement': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'payout_approval_state',
    cols: ['name', 'customer_id', 'graded_value', 'payout_amount', 'payout_approval_state', 'payout_approved_at', 'payout_execution_id', 'state'],
    actions: [
      { m: 'action_request_payout_approval', l: 'Request Approval' },
      { m: 'action_approve_payout', l: 'Approve Payout' },
      { m: 'action_reject_payout', l: 'Reject' },
      { m: 'action_pay', l: 'Pay via Treasury' }
    ] },
  'M14-orders': { kind: 'model_list', model: 'fix.refurbishment', stateField: 'state',
    cols: ['name', 'tradein_id', 'step', 'technician_id', 'parts_cost', 'labor_cost', 'total_cost', 'state'],
    actions: [
      { m: 'action_start', l: 'Start Step' },
      { m: 'action_request_parts', l: 'Request Parts' },
      { m: 'action_complete_repair', l: 'Complete Step' }
    ] },
  'M14-qa': { kind: 'model_list', model: 'fix.refurb.qa', stateField: 'qa_state',
    cols: ['name', 'tradein_id', 'battery_health_pct', 'tests_passed', 'tests_total', 'pass_pct', 'qa_state', 'checked_on', 'inspector_id'] },
  'M14-grading': { kind: 'model_list', model: 'fix.tradein.grade',
    cols: ['name', 'tradein_id', 'grade', 'battery_health_pct', 'screen_grade', 'cosmetic_grade', 'functional_grade', 'graded_on'] },
  'M14-harvest': { kind: 'model_list', model: 'fix.tradein.harvest', stateField: 'state',
    cols: ['name', 'tradein_id', 'component', 'part_name', 'quantity', 'total_value', 'target', 'state'] },
  'M14-stock': { kind: 'model_list', model: 'fix.graded.stock', stateField: 'state', create: false,
    cols: ['name', 'device_id', 'grade_id', 'tradein_ref', 'inventory_valuation', 'resale_price', 'projected_margin', 'state'] },
  'M14-listings': { kind: 'table_report', module: 'M14', report: 'resale_pipeline', title: 'Resale Listings', period: false },
  'M14-wty': { kind: 'model_list', model: 'fix.tradein.warranty', stateField: 'state',
    cols: ['name', 'tradein_id', 'months', 'start_date', 'end_date', 'claims_count', 'state'] },
  'M14-economics': { kind: 'table_report', module: 'M14', report: 'unit_economics', title: 'Unit Economics', period: false },

  /* Report chips -> their own computed packs (All 8 active) */
  'M14-rpt-margin': { kind: 'table_report', module: 'M14', report: 'tradein_margin', title: 'Trade-In Margin by Model', period: false },
  'M14-rpt-grade': { kind: 'table_report', module: 'M14', report: 'refurb_cost_grade', title: 'Refurb Cost per Grade', period: false },
  'M14-rpt-ageing': { kind: 'table_report', module: 'M14', report: 'ageing_markdown', title: 'Ageing & Markdown', period: false },
  'M14-rpt-channel': { kind: 'table_report', module: 'M14', report: 'resale_channel', title: 'Resale Channel Performance', period: false },
  'M14-rpt-harvest': { kind: 'table_report', module: 'M14', report: 'harvest_yield', title: 'Harvest Yield', period: false },
  'M14-rpt-valqueue': { kind: 'table_report', module: 'M14', report: 'valuation_queue', title: 'Valuation Queue', period: false },
  'M14-rpt-resale': { kind: 'table_report', module: 'M14', report: 'resale_pipeline', title: 'Resale Listings', period: false },
  'M14-rpt-economics': { kind: 'table_report', module: 'M14', report: 'unit_economics', title: 'Unit Economics', period: false },

  /* ============ D365 IN-WORKSPACE FORMS (6-TAB STANDARD) ============ */
  'M14-form-request': {
    kind: 'model_form',
    model: 'fix.tradein.request',
    title: 'Trade-In Intake Dossier',
    back: 'M14-intake',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', evaluated: 'Evaluated', accepted: 'Accepted',
      collected: 'Collected', wiped: 'Wiped', refurbishing: 'Refurbishing', graded: 'Graded',
      resale_ready: 'Resale Ready', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'general', label: '1. General & Customer', bn: '১. সাধারণ ও গ্রাহক', icon: '👤', badge: '6' },
      { id: 'pricing', label: '2. Valuation & Tax', bn: '২. মূল্যায়ন ও কর', icon: '৳', badge: '8' },
      { id: 'technical', label: '3. Device & Grading', bn: '৩. ডিভাইস ও গ্রেডিং', icon: '📱', badge: '4' },
      { id: 'lifecycle', label: '4. Workshop & Costs', bn: '৪. ওয়ার্কশপ ও খরচ', icon: '🔧', badge: '4' },
      { id: 'governance', label: '5. Payout & Channel', bn: '৫. পরিশোধ ও চ্যানেল', icon: '⚖️', badge: '11' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ডকুমেন্ট ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Customer & Intake Master',
        fields: [
          { name: 'name', label: 'Trade-In Reference', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'customer_nid', label: 'National ID (NID/Smart Card)' },
          { name: 'state', label: 'Intake State', readonly: true }
        ] },
      { tab: 'general', title: 'Intake Device Reference',
        fields: [
          { name: 'device_model_id', required: true, label: 'Device Model' },
          { name: 'device_id', label: 'Device Serial Master' }
        ] },
      { tab: 'pricing', title: 'Commercial Valuation & Payout Offer',
        fields: [
          { name: 'offered_value', label: 'Initial Offer Value' },
          { name: 'graded_value', label: 'Post-Inspection Value' },
          { name: 'payout_amount', label: 'Gross Payout Amount' },
          { name: 'net_payout', label: 'Net Payout After Tax', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'pricing', title: 'Statutory Withholding Tax (ITA 2023 s.89/90)',
        fields: [
          { name: 'tds_applicable', label: 'TDS Withholding Applicable' },
          { name: 'tds_rate_pct', label: 'TDS Rate (%)' },
          { name: 'tds_amount', label: 'TDS Withheld Amount', readonly: true }
        ] },
      { tab: 'technical', title: 'Technical Grading & Diagnostic',
        fields: [
          { name: 'grade', label: 'Preliminary Grade' },
          { name: 'refurb_grade_id', label: 'Final Graded Class' },
          { name: 'battery_health_pct', label: 'Battery Health (%)' },
          { name: 'wipe_certificate_id', label: 'Data Sanitization Certificate' }
        ] },
      { tab: 'lifecycle', title: 'Refurbishment Workshop Integration',
        fields: [
          { name: 'workshop_job_id', label: 'Origin Workshop Job' },
          { name: 'labour_cost', label: 'Direct Labour Cost' },
          { name: 'parts_cost', label: 'Replacement Parts Cost' },
          { name: 'refurbishment_cost', label: 'Total Refurbishment Cost', readonly: true }
        ] },
      { tab: 'governance', title: 'Four-Eyes Settlement Approval',
        fields: [
          { name: 'payout_approval_state', label: 'Payout Approval State', readonly: true },
          { name: 'payout_requested_by_id', label: 'Requested By' },
          { name: 'payout_approved_by_id', label: 'Approver (Director/Manager)' },
          { name: 'payout_approved_at', label: 'Approval Timestamp' },
          { name: 'payout_execution_id', label: 'Treasury Execution Reference' }
        ] },
      { tab: 'governance', title: 'Resale Marketplace Channel Allocation',
        fields: [
          { name: 'resale_channel', label: 'Target Resale Channel' },
          { name: 'resale_listed_on', label: 'Marketplace Listing Date' },
          { name: 'resale_value', label: 'Target Resale Value' },
          { name: 'marketplace_seller_id', label: 'Merchant / Seller Account' },
          { name: 'consignment_id', label: 'B2B Consignment Batch' },
          { name: 'company_id', label: 'Operating Entity' },
          { name: 'operating_unit_id', label: 'Operating Unit Hub' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-valuation': {
    kind: 'model_form',
    model: 'fix.tradein.valuation',
    title: 'Automated Valuation File',
    back: 'M14-valuation',
    status: { field: 'state', labels: { draft: 'Draft', computed: 'Computed', applied: 'Applied' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '📄', badge: '4' },
      { id: 'pricing', label: '2. Reference Pricing', bn: '২. বেঞ্চমার্ক মূল্য', icon: '৳', badge: '5' },
      { id: 'technical', label: '3. Condition Factor', bn: '৩. শর্ত গুণাঙ্ক', icon: '⚙️', badge: '3' },
      { id: 'lifecycle', label: '4. Valuer & Override', bn: '৪. মূল্যায়নকারী ও ব্যত্যয়', icon: '✍️', badge: '3' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Valuation Run Master',
        fields: [
          { name: 'name', label: 'Valuation Run ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request' },
          { name: 'method', label: 'Algorithm Method' },
          { name: 'state', label: 'Valuation State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Market Benchmark & Calculations',
        fields: [
          { name: 'device_model_id', label: 'Device Model' },
          { name: 'market_ref_price', label: 'Market Benchmark Price' },
          { name: 'computed_offer', label: 'Algorithm Computed Offer', readonly: true },
          { name: 'final_offer', label: 'Final Commercial Offer' },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'technical', title: 'Depreciation & Age Factors',
        fields: [
          { name: 'condition_factor_pct', label: 'Physical Condition Factor (%)' },
          { name: 'age_factor_pct', label: 'Depreciation Factor (%)' },
          { name: 'age_months', label: 'Device Age (Months)' }
        ] },
      { tab: 'lifecycle', title: 'Manual Review & Override Audit',
        fields: [
          { name: 'valuated_by_id', label: 'Valuation Specialist' },
          { name: 'valuated_on', label: 'Valuation Timestamp' },
          { name: 'override_reason', label: 'Manager Override Justification' }
        ] },
      { tab: 'governance', title: 'Corporate Entity Scope',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-provenance': {
    kind: 'model_form',
    model: 'fix.tradein.provenance',
    title: 'Provenance Screening & Anti-Theft',
    back: 'M14-provenance',
    status: { field: 'state', labels: { pending: 'Pending', cleared: 'Cleared', flagged: 'Flagged' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔍', badge: '4' },
      { id: 'pricing', label: '2. Audit Timestamp', bn: '২. সময়কাল', icon: '⏱️', badge: '1' },
      { id: 'technical', label: '3. Blacklist & Stolen', bn: '৩. ব্ল্যাকলিস্ট ও চুরি', icon: '🛡️', badge: '6' },
      { id: 'lifecycle', label: '4. BTRC NEIR Screening', bn: '৪. বিটিআরসি এনইআইআর', icon: '🇧🇩', badge: '4' },
      { id: 'governance', label: '5. Governance & Notes', bn: '৫. নিয়ন্ত্রণ ও নোট', icon: '📝', badge: '2' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Screening Subject',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request' },
          { name: 'imei', required: true, label: 'Primary IMEI' },
          { name: 'state', label: 'Clearance Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Inspection Timing',
        fields: [
          { name: 'checked_on', label: 'Inspection Timestamp' }
        ] },
      { tab: 'technical', title: 'Anti-Theft & Stolen Database Checks',
        fields: [
          { name: 'stolen_checked', label: 'Police Stolen DB Verified' },
          { name: 'stolen_hit', label: 'Stolen Record Hit' },
          { name: 'blacklist_checked', label: 'GSMA Blacklist Verified' },
          { name: 'blacklist_hit', label: 'Blacklist Hit Flag' },
          { name: 'warranty_checked', label: 'OEM Warranty Verified' },
          { name: 'warranty_active', label: 'Active OEM Coverage' }
        ] },
      { tab: 'lifecycle', title: 'Bangladesh Telecommunication Regulatory Commission (BTRC) NEIR',
        fields: [
          { name: 'btrc_neir_checked', label: 'BTRC NEIR Portal Verified' },
          { name: 'btrc_neir_status', label: 'NEIR Legal Status (White/Grey/Black)' },
          { name: 'customer_nid_no', label: 'Customer Verified NID' },
          { name: 'customer_nid_verified', label: 'EC NID Portal Cleared' }
        ] },
      { tab: 'governance', title: 'Security Notes & Company',
        fields: [
          { name: 'notes', label: 'Investigator Notes' },
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-settlement': {
    kind: 'model_form',
    model: 'fix.tradein.request',
    title: 'Settlement & Four-Eyes Payout',
    back: 'M14-settlement',
    status: { field: 'payout_approval_state', labels: {
      draft: 'Draft', requested: 'Approval Requested', approved: 'Approved',
      rejected: 'Rejected', paid: 'Settled & Paid' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '👤', badge: '4' },
      { id: 'pricing', label: '2. Payout & Tax', bn: '২. মূল্য ও উৎসে কর', icon: '৳', badge: '7' },
      { id: 'technical', label: '3. Valuation Target', bn: '৩. মূল্যায়ন রেফারেন্স', icon: '📱', badge: '3' },
      { id: 'lifecycle', label: '4. Four-Eyes Authorization', bn: '৪. চার-চক্ষু অনুমোদন', icon: '👔', badge: '4' },
      { id: 'governance', label: '5. Treasury & Ops', bn: '৫. ট্রেজারি ও পরিচালনা', icon: '🏦', badge: '3' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Settlement Beneficiary',
        fields: [
          { name: 'name', label: 'Trade-In Reference', readonly: true },
          { name: 'customer_id', label: 'Customer Account' },
          { name: 'customer_nid', label: 'National ID / Tax Identity' },
          { name: 'state', label: 'Trade-In State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Settlement & Statutory Withholding (ITA 2023)',
        fields: [
          { name: 'graded_value', label: 'Approved Graded Value' },
          { name: 'payout_amount', label: 'Gross Payout' },
          { name: 'tds_applicable', label: 'TDS Applicable' },
          { name: 'tds_rate_pct', label: 'TDS Rate (%)' },
          { name: 'tds_amount', label: 'Withheld TDS (BDT)' },
          { name: 'net_payout', label: 'Net Payable via MFS/Bank', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'technical', title: 'Device & Graded Unit Reference',
        fields: [
          { name: 'device_model_id', label: 'Device Model' },
          { name: 'grade', label: 'Inspection Grade' },
          { name: 'graded_stock_id', label: 'Graded Stock Inventory Master' }
        ] },
      { tab: 'lifecycle', title: 'DOFA Four-Eyes Verification',
        fields: [
          { name: 'payout_approval_state', label: 'Payout Stage', readonly: true },
          { name: 'payout_requested_by_id', label: 'Submitted By (Agent)' },
          { name: 'payout_approved_by_id', label: 'Authorized Approver' },
          { name: 'payout_approved_at', label: 'Authorization Timestamp' }
        ] },
      { tab: 'governance', title: 'Treasury Execution & Operating Hub',
        fields: [
          { name: 'payout_execution_id', label: 'Payment Gateway / Journal Reference' },
          { name: 'company_id', label: 'Company' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ] },
      { tab: 'vault', title: 'Settlement Voucher Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-refurb': {
    kind: 'model_form',
    model: 'fix.refurbishment',
    title: 'Refurbishment Work Order',
    back: 'M14-orders',
    status: { field: 'state', labels: { draft: 'Draft', in_progress: 'In Progress', completed: 'Completed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔧', badge: '4' },
      { id: 'pricing', label: '2. Job Costing', bn: '২. কার্য ব্যয়', icon: '৳', badge: '4' },
      { id: 'technical', label: '3. Technical Routing', bn: '৩. কারিগরি বরাদ্দ', icon: '👨‍🔧', badge: '2' },
      { id: 'lifecycle', label: '4. Observations', bn: '৪. পর্যবেক্ষণ', icon: '📋', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Refurbishment Step Identification',
        fields: [
          { name: 'name', label: 'Work Order ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request' },
          { name: 'step', label: 'Refurbishment Stage (Screen/Battery/Motherboard)' },
          { name: 'state', label: 'Progress Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Job Costing & Absorption',
        fields: [
          { name: 'labor_cost', label: 'Allocated Labor Cost' },
          { name: 'parts_cost', label: 'BOM Replacement Parts Cost' },
          { name: 'total_cost', label: 'Total Refurb Cost', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'technical', title: 'Technician Assignment',
        fields: [
          { name: 'technician_id', required: true, label: 'Assigned Master Technician' },
          { name: 'operating_unit_id', label: 'Refurbishment Center' }
        ] },
      { tab: 'lifecycle', title: 'Technician Log & Repair Observations',
        fields: [
          { name: 'notes', label: 'Step Procedure & Diagnostic Notes' }
        ] },
      { tab: 'governance', title: 'Corporate Entity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-qa': {
    kind: 'model_form',
    model: 'fix.refurb.qa',
    title: 'QA & Battery Health Dossier',
    back: 'M14-qa',
    status: { field: 'qa_state', labels: { pending: 'Pending', passed: 'Passed', failed: 'Failed' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔍', badge: '4' },
      { id: 'pricing', label: '2. Pass Metrics', bn: '২. পাসের অনুপাত', icon: '📊', badge: '1' },
      { id: 'technical', label: '3. Diagnostics & Battery', bn: '৩. ব্যাটারি ও ডায়াগনস্টিকস', icon: '🔋', badge: '3' },
      { id: 'lifecycle', label: '4. Inspector Log', bn: '৪. পরিদর্শক লগ', icon: '✍️', badge: '3' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Quality Assurance Docket',
        fields: [
          { name: 'name', label: 'QA Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request' },
          { name: 'refurbishment_id', label: 'Refurbishment Step' },
          { name: 'qa_state', label: 'Quality Assessment', readonly: true }
        ] },
      { tab: 'pricing', title: 'Test Metrics',
        fields: [
          { name: 'pass_pct', label: 'Diagnostic Pass Rate (%)', readonly: true }
        ] },
      { tab: 'technical', title: 'Battery Health & Automated Suite',
        fields: [
          { name: 'battery_health_pct', label: 'Battery Health (%)' },
          { name: 'tests_passed', label: 'Automated Tests Passed' },
          { name: 'tests_total', label: 'Total Test Cases' }
        ] },
      { tab: 'lifecycle', title: 'Inspector Evaluation & Sign-off',
        fields: [
          { name: 'inspector_id', label: 'Lead QA Inspector' },
          { name: 'checked_on', label: 'Audit Timestamp' },
          { name: 'notes', label: 'Defect Analysis' }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-grade': {
    kind: 'model_form',
    model: 'fix.tradein.grade',
    title: 'Grading Certificate',
    back: 'M14-grading',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🏷️', badge: '3' },
      { id: 'pricing', label: '2. Grade Output', bn: '২. গ্রেড স্তর', icon: '🎖️', badge: '1' },
      { id: 'technical', label: '3. Physical Dimensions', bn: '৩. বহিরাঙ্গ ও স্ক্রিন', icon: '📐', badge: '4' },
      { id: 'lifecycle', label: '4. Grading Sign-off', bn: '৪. গ্রেডার নিরীক্ষা', icon: '👨‍🔬', badge: '3' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Grading Docket',
        fields: [
          { name: 'name', label: 'Grade Certificate ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request' },
          { name: 'grade', required: true, label: 'Calculated Grade (A/B/C/D/E)' }
        ] },
      { tab: 'pricing', title: 'Grade Classification',
        fields: [
          { name: 'grade', label: 'Commercial Resale Grade' }
        ] },
      { tab: 'technical', title: 'Multi-Axis Assessment',
        fields: [
          { name: 'cosmetic_grade', label: 'Cosmetic / Housing Condition' },
          { name: 'functional_grade', label: 'Hardware Functionality' },
          { name: 'screen_grade', label: 'Display Panel Clarity' },
          { name: 'battery_health_pct', label: 'Battery Capacity (%)' }
        ] },
      { tab: 'lifecycle', title: 'Inspector Authentication',
        fields: [
          { name: 'inspector_id', label: 'Certified Grader' },
          { name: 'graded_on', label: 'Graded Timestamp' },
          { name: 'notes', label: 'Defect Explanations' }
        ] },
      { tab: 'governance', title: 'Corporate Entity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-harvest': {
    kind: 'model_form',
    model: 'fix.tradein.harvest',
    title: 'Harvest to Parts Dossier',
    back: 'M14-harvest',
    status: { field: 'state', labels: { pending: 'Pending', harvested: 'Harvested', tested: 'Tested', stocked: 'Stocked' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '📦', badge: '3' },
      { id: 'pricing', label: '2. Recovered Value', bn: '২. উদ্ধারকৃত মূল্য', icon: '৳', badge: '3' },
      { id: 'technical', label: '3. Part Specifications', bn: '৩. যন্ত্রাংশের বিবরণ', icon: '🔩', badge: '4' },
      { id: 'lifecycle', label: '4. Harvest Timeline', bn: '৪. সংগ্রহের সময়কাল', icon: '📅', badge: '2' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Harvest Case',
        fields: [
          { name: 'name', label: 'Harvest Record ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request' },
          { name: 'state', label: 'Harvesting State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Inventory Valuation of Harvested Spares',
        fields: [
          { name: 'unit_value', label: 'Standard Unit Value (BDT)' },
          { name: 'total_value', label: 'Total Valuation Absorbed', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'technical', title: 'Harvested Component Definition',
        fields: [
          { name: 'component', label: 'Component Category' },
          { name: 'part_name', required: true, label: 'Spare Part SKU / Name' },
          { name: 'quantity', required: true, label: 'Quantity Salvaged' },
          { name: 'target', label: 'Destination Stock / Refurb Buffer' }
        ] },
      { tab: 'lifecycle', title: 'Dismantling Execution',
        fields: [
          { name: 'harvested_on', label: 'Harvest Date' },
          { name: 'notes', label: 'Extraction Conditions' }
        ] },
      { tab: 'governance', title: 'Corporate Entity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-warranty': {
    kind: 'model_form',
    model: 'fix.tradein.warranty',
    title: 'Refurbished Warranty Master',
    back: 'M14-wty',
    status: { field: 'state', labels: { active: 'Active', expired: 'Expired', voided: 'Voided' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🛡️', badge: '3' },
      { id: 'pricing', label: '2. Claims Liability', bn: '২. দাবির দায়', icon: '⚠️', badge: '1' },
      { id: 'technical', label: '3. Coverage Term', bn: '৩. কভারেজের মেয়াদ', icon: '📅', badge: '3' },
      { id: 'lifecycle', label: '4. Terms & Exclusions', bn: '৪. শর্ত ও ব্যতিক্রম', icon: '📜', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Policy Header',
        fields: [
          { name: 'name', label: 'Warranty Policy ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Origin Trade-In' },
          { name: 'state', label: 'Coverage Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Claims Experience',
        fields: [
          { name: 'claims_count', label: 'Service Claims Registered', readonly: true }
        ] },
      { tab: 'technical', title: 'Validity Window',
        fields: [
          { name: 'months', label: 'Warranty Duration (Months)' },
          { name: 'start_date', required: true, label: 'Coverage Start Date' },
          { name: 'end_date', label: 'Coverage Expiration Date' }
        ] },
      { tab: 'lifecycle', title: 'Policy Terms',
        fields: [
          { name: 'terms', label: 'Refurbished Warranty Terms & Conditions' }
        ] },
      { tab: 'governance', title: 'Issuing Legal Entity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M14:Trade-In Margin by Model': 'M14-rpt-margin',
  'M14:Refurb Cost per Grade': 'M14-rpt-grade',
  'M14:Ageing & Markdown': 'M14-rpt-ageing',
  'M14:Resale Channel Performance': 'M14-rpt-channel',
  'M14:Harvest Yield': 'M14-rpt-harvest',
  'M14:Valuation Queue': 'M14-rpt-valqueue',
  'M14:Resale Listings': 'M14-rpt-resale',
  'M14:Unit Economics': 'M14-rpt-economics'
};

export const FORM_MODELS = {
  'M14:Trade-In Intake Dossier': 'fix.tradein.request',
  'M14:Automated Valuation File': 'fix.tradein.valuation',
  'M14:Provenance Screening & Anti-Theft': 'fix.tradein.provenance',
  'M14:Settlement & Four-Eyes Payout': 'fix.tradein.request',
  'M14:Refurbishment Work Order': 'fix.refurbishment',
  'M14:QA & Battery Health Dossier': 'fix.refurb.qa',
  'M14:Grading Certificate': 'fix.tradein.grade',
  'M14:Harvest to Parts Dossier': 'fix.tradein.harvest',
  'M14:Refurbished Warranty Master': 'fix.tradein.warranty'
};

export const FORM_CHIPS = {
  'M14:Trade-In Intake Dossier': 'M14-form-request',
  'M14:Automated Valuation File': 'M14-form-valuation',
  'M14:Provenance Screening & Anti-Theft': 'M14-form-provenance',
  'M14:Settlement & Four-Eyes Payout': 'M14-form-settlement',
  'M14:Refurbishment Work Order': 'M14-form-refurb',
  'M14:QA & Battery Health Dossier': 'M14-form-qa',
  'M14:Grading Certificate': 'M14-form-grade',
  'M14:Harvest to Parts Dossier': 'M14-form-harvest',
  'M14:Refurbished Warranty Master': 'M14-form-warranty',
  'M14:__by_model__': {
    'fix.tradein.request': 'M14-form-request',
    'fix.tradein.valuation': 'M14-form-valuation',
    'fix.tradein.provenance': 'M14-form-provenance',
    'fix.refurbishment': 'M14-form-refurb',
    'fix.refurb.qa': 'M14-form-qa',
    'fix.tradein.grade': 'M14-form-grade',
    'fix.tradein.harvest': 'M14-form-harvest',
    'fix.tradein.warranty': 'M14-form-warranty'
  },
  'M14:__by_screen__': {
    'M14-intake': 'M14-form-request',
    'M14-valuation': 'M14-form-valuation',
    'M14-provenance': 'M14-form-provenance',
    'M14-settlement': 'M14-form-settlement',
    'M14-orders': 'M14-form-refurb',
    'M14-qa': 'M14-form-qa',
    'M14-grading': 'M14-form-grade',
    'M14-harvest': 'M14-form-harvest',
    'M14-wty': 'M14-form-warranty'
  }
};

export const CREATE = {
  M14: { screen: 'M14-form-request', model: 'fix.tradein.request', label: 'Trade-In Request' }
};
