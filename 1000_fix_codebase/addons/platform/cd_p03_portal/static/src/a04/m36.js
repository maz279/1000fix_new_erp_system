/** @odoo-module **/
/* A04 · Commercial & Revenue — M36 Quotations & Tenders (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 86.
 * Estimates and counter-sales are real; quotations, internal reviews, tenders
 * and bonds are new. Conversion/win rates are measured; the declined→
 * diagnostic-fee conversion is a declared gap. */

export const MODULE = {
  area: 'A04', code: 'M36', en: 'Quotations & Tenders', title: 'M36 · Quotations & Tenders',
  bn: 'কোটেশন ও দরপত্র', icon: '📄',
  desc: 'Internal estimates and build-up, versioned customer quotations, e-signature evidence, approval routing and the customer loop, declined-repair handling, public tenders, compliance and bid bonds.',
  kpis: [
    { l: 'Quotes Open', m: 'quotes_open' },
    { l: 'Conversion', m: 'conversion', suffix: '%' },
    { l: 'Awaiting Customer', m: 'awaiting_customer' },
    { l: 'Avg Turnaround (h)', m: 'avg_turnaround' },
    { l: 'Tenders Live', m: 'tenders_live' },
    { l: 'Declined → Diagnostic Fee', m: 'declined_conversion' }
  ],
  groups: [
    { en: 'Estimates', screens: [
      { id: 'M36-estimates', en: 'Internal Estimates', bn: 'অভ্যন্তরীণ এস্টিমেট', t: 'g' },
      { id: 'M36-buildup', en: 'Build-Up Workbench', bn: 'বিল্ড-আপ', t: 'f' }
    ]},
    { en: 'Quotations', screens: [
      { id: 'M36-quotes', en: 'Customer Quotations', bn: 'গ্রাহক কোটেশন', t: 'g' },
      { id: 'M36-form-quotation', en: 'Quotation Record', bn: 'কোটেশন রেকর্ড', t: 'f' },
      { id: 'M36-versions', en: 'Versions & Counter-Offer', bn: 'ভার্সন ও কাউন্টার', t: 'g' },
      { id: 'M36-esign', en: 'e-Signature & Evidence', bn: 'ই-সাইন', t: 'g' }
    ]},
    { en: 'Approval Loop', screens: [
      { id: 'M36-loop', en: 'Customer Approval Loop', bn: 'গ্রাহক অনুমোদন', t: 'c' },
      { id: 'M36-internal', en: 'Internal Approval Routing', bn: 'অভ্যন্তরীণ অনুমোদন', t: 'g' },
      { id: 'M36-declined', en: 'Declined-Repair Handling', bn: 'প্রত্যাখ্যাত মেরামত', t: 'g' }
    ]},
    { en: 'Tenders', screens: [
      { id: 'M36-tenders', en: 'Tenders & Bids', bn: 'দরপত্র', t: 'g' },
      { id: 'M36-compliance', en: 'Compliance Matrix', bn: 'কমপ্লায়েন্স ম্যাট্রিক্স', t: 'f' },
      { id: 'M36-bonds', en: 'Bid Bonds', bn: 'বিড বন্ড', t: 'g' }
    ]}
  ],
  reports: ['Quote Conversion by Channel', 'Approval Cycle Time', 'Decline Reasons Pareto', 'Tender Win/Loss', 'Margin on Approved Quotes'],
  forms: ['Estimate', 'Quotation (versioned)', 'Tender Bid', 'Counter-Offer'],
  cross: ['M37 Catalogue', 'M11 Pricing', 'M01 Service Orders'],
  freg: { src: 86, sub: [
    ['1', 'Estimate Build-Up', 10, { model: 'fix.estimate.line', cols: ['estimate_id', 'line_type', 'description', 'quantity', 'unit_price', 'line_total'], screens: ['M36-buildup', 'M36-estimates'] }],
    ['2', 'Quotation Object', 12, { model: 'fix.quotation', cols: ['name', 'state', 'customer_id', 'version', 'value', 'vat_amount'], screens: ['M36-quotes'] }],
    ['3', 'Versioning', 7, { model: 'fix.quotation', cols: ['name', 'state', 'customer_id', 'version', 'value', 'vat_amount'], screens: ['M36-versions'] }],
    ['4', 'Approval Routing', 9, { model: 'fix.quote.review', cols: ['quotation_id', 'reviewer_id', 'decision', 'reviewed_at'], screens: ['M36-internal'] }],
    ['5', 'Customer Approval Loop (8 channels)', 13, { model: 'fix.quote.review', cols: ['quotation_id', 'reviewer_id', 'decision', 'reviewed_at'], screens: ['M36-loop'] }],
    ['6', 'Partial Accept & Counter', 6, { model: 'fix.quotation', cols: ['name', 'state', 'customer_id', 'version', 'value', 'vat_amount'], screens: ['M36-quotes'] }],
    ['7', 'e-Signature', 6, { model: 'fix.quotation', cols: ['name', 'customer_id', 'esign_state', 'signed_at', 'state'], screens: ['M36-esign', 'M36-quotes'] }],
    ['8', 'Declined Handling', 6, { model: 'fix.quotation', cols: ['name', 'customer_id', 'state', 'decline_reason', 'valid_until'], screens: ['M36-declined', 'M36-rpt-decline', 'M36-quotes'] }],
    ['9', 'Tender & Bid', 9, { model: 'fix.tender', cols: ['name', 'state', 'client_name', 'due_date', 'estimated_value', 'compliance_pct', 'bonds_required'], screens: ['M36-tenders', 'M36-bonds', 'M36-rpt-tender'] }],
    ['10', 'Templates & Bilingual Gen', 8, { model: 'fix.document.template', cols: ['code', 'name', 'name_bn', 'document_type', 'bilingual'], screens: ['M36-compliance'] }]
  ] }
};

export const SCREENS = {
  /* ---- registry screens restored (A04 zero-trust audit 2026-10-31): nav ids that dead-ended ---- */
  'M36-versions': { kind: 'model_list', model: 'fix.quotation', create: false,
    cols: ["name", "customer_id", "state", "currency_id", "create_date", "company_id", "estimate_id"] },
  'M36-esign': { kind: 'table_report', module: 'M36', report: 'esign_status', title: 'E-Signature Status', period: true },
  'M36-loop': { kind: 'model_list', model: 'fix.quote.review', create: false,
    cols: ["create_date", "quotation_id", "reviewer_id", "decision", "notes", "reviewed_at", "create_uid"] },
  'M36-internal': { kind: 'model_list', model: 'fix.quote.review', create: false,
    cols: ["create_date", "quotation_id", "reviewer_id", "decision", "notes", "reviewed_at", "create_uid"] },
  'M36-declined': { kind: 'table_report', module: 'M36', report: 'decline_pareto', title: 'Decline Pareto', period: true },
  'M36-tenders': { kind: 'model_list', model: 'fix.tender', create: false,
    cols: ["name", "state", "currency_id", "create_date", "company_id", "client_name", "due_date"] },
  'M36-compliance': { kind: 'table_report', module: 'M36', report: 'tender_compliance', title: 'Tender Compliance', period: true },
  'M36-bonds': { kind: 'model_list', model: 'fix.tender.bond', create: false,
    cols: ["state", "amount", "currency_id", "create_date", "tender_id", "bond_type", "bank"] },


  /* Report screens */
  'M36-rpt-conv': { kind: 'table_report', module: 'M36', report: 'quote_conversion', title: 'Quote Conversion by Channel', period: false },
  'M36-rpt-cycle': { kind: 'table_report', module: 'M36', report: 'approval_cycle', title: 'Approval Cycle Time', period: false },
  'M36-rpt-decline': { kind: 'table_report', module: 'M36', report: 'decline_pareto', title: 'Decline Reasons Pareto', period: false },
  'M36-rpt-tender': { kind: 'table_report', module: 'M36', report: 'tender_winloss', title: 'Tender Win/Loss', period: false },
  'M36-rpt-margin': { kind: 'table_report', module: 'M36', report: 'margin_approved', title: 'Margin on Approved Quotes', period: false },

  'M36-estimates': { kind: 'model_list', model: 'fix.estimate', stateField: 'state',
    cols: ['order_id', 'version', 'state', 'grand_total', 'discount', 'expiry_date', 'approved_by'] },
  'M36-buildup': { kind: 'model_list', create: false, model: 'fix.estimate.line',
    cols: ['estimate_id', 'description', 'quantity', 'unit_price', 'line_total'] },
  'M36-quotes': { kind: 'model_list', model: 'fix.quotation', stateField: 'state',
    cols: ['name', 'customer_id', 'version', 'value', 'margin_pct', 'valid_until', 'state'] },
  'M36-form-estimate': {

    lines: {

      field: 'line_ids',

      title: 'Estimate Lines',

      note: 'Parts and labour quoted to the customer; the diagnostic fee is excluded from contract delivery cost.',

      fields: [

        { name: 'line_type', label: 'Type', required: true },

        { name: 'product_id', label: 'Product' },

        { name: 'description', label: 'Description', required: true },

        { name: 'quantity', label: 'Qty', required: true },

        { name: 'unit_price', label: 'Unit Price', required: true },

        { name: 'line_total', label: 'Total' }

      ]

    }, kind: 'model_form', model: 'fix.estimate',
    title: 'Estimate', back: 'M36-estimates',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'text', label: '6. Notes & Terms', bn: '৬. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '7. System Audit', bn: '৭. সিস্টেম অডিট' },
      { id: 'docs', label: '8. Documents', bn: '৮. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'version', label: 'Version', required: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'customer_approval_ref', label: 'Customer Approval Ref', readonly: true },
        { name: 'dofa_tier_required', label: 'DOFA Discount Tier', readonly: true },
        { name: 'quotation_state', label: 'Quotation State' },
        { name: 'valid_days', label: 'Valid Days' },
        { name: 'tender_ref', label: 'Tender Reference' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'parts_total', label: 'Parts Total', readonly: true },
        { name: 'labour_total', label: 'Labour Total', readonly: true },
        { name: 'diagnostic_total', label: 'Diagnostic Total', readonly: true },
        { name: 'discount', label: 'Discount' },
        { name: 'vat_rate', label: 'VAT Rate (%)' },
        { name: 'vat_amount', label: 'VAT Amount', readonly: true },
        { name: 'grand_total', label: 'Grand Total', readonly: true },
        { name: 'discount_pct', label: 'Discount (%)', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'approved_at', label: 'Approved At', readonly: true },
        { name: 'expiry_date', label: 'Expiry Date' },
        { name: 'sent_at', label: 'Sent At', readonly: true },
        { name: 'accepted_at', label: 'Accepted At', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'order_id', label: 'Service Order', required: true },
        { name: 'manager_approval_uid', label: 'Manager Approval', readonly: true },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'approved_by', label: 'Approved By', readonly: true },
        { name: 'dofa_approved_by', label: 'DOFA Discount Approver', readonly: true },
        { name: 'signed_estimate_attachment_id', label: 'Signed Customer Estimate PDF' }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'diagnostic_notes', label: 'Engineering Quotation Notes & Scope', type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (line_ids, approval_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M36-form-quotation': {
    kind: 'model_form',
    model: 'fix.quotation',
    title: 'Commercial Proposal & Tender Quotation',
    back: 'M36-quotes',
    status: { field: 'state' },
    tabs: [
      { id: 'header', label: '1. Proposal Header', bn: '১. প্রস্তাবনা পরিচিতি', icon: '📄', badge: '6' },
      { id: 'pricing', label: '2. Cost, Margins & SRT', bn: '২. খরচ ও মার্জিন', icon: '💵', badge: '6' },
      { id: 'statutory', label: '3. Withholding Tax (TDS)', bn: '৩. উৎসে কর কর্তন', icon: '⚖️', badge: '4' },
      { id: 'esign', label: '4. e-Signature & Customer', bn: '৪. ডিজিটাল স্বাক্ষর', icon: '✍️', badge: '3' },
      { id: 'tenders', label: '5. Public Tender & e-GP', bn: '৫. দরপত্র ও বন্ড', icon: '🏛️', badge: '2' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'header', title: 'Proposal Identity & Version Tracking',
        note: 'Version-controlled commercial proposal generated over service estimate or tender specification.',
        fields: [
          { name: 'name', label: 'Quotation Reference (auto)', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'estimate_id', label: 'Originating Technical Estimate (M01)' },
          { name: 'version', required: true, label: 'Quotation Version Code' },
          { name: 'valid_until', label: 'Validity Expiration Date' },
          { name: 'state', required: true, label: 'Lifecycle Status' }
        ] },
      { tab: 'pricing', title: 'Direct Cost, Pre-Tax Margin & Value',
        fields: [
          { name: 'value', required: true, label: 'Quotation Subtotal (BDT)' },
          { name: 'cost_amount', label: 'Direct Labor & Parts Cost (BDT)' },
          { name: 'pretax_margin_bdt', label: 'Pre-Tax Operational Margin (BDT)', readonly: true },
          { name: 'margin_pct', label: 'Gross Margin (%)', readonly: true },
          { name: 'vat_rate', label: 'Standard VAT Rate (%)' },
          { name: 'vat_amount', label: 'Mushak VAT Amount (BDT)', readonly: true }
        ] },
      { tab: 'statutory', title: 'Statutory Withholding Tax & Net Cash Margin',
        note: 'Statutory TDS deductions under Income Tax Act 2023 s.89/90 for supply of service/goods.',
        fields: [
          { name: 'tds_rate', label: 'Withholding Tax TDS Rate (%)' },
          { name: 'tds_amount', label: 'TDS Deduction (BDT)', readonly: true },
          { name: 'net_cash_margin_bdt', label: 'Net Cash Margin After-Tax (BDT)', readonly: true },
          { name: 'net_cash_margin_pct', label: 'Net Cash Margin (%)', readonly: true }
        ] },
      { tab: 'esign', title: 'Customer Acceptance & E-Signature Audit',
        fields: [
          { name: 'esign_state', required: true, label: 'Digital Signature Status' },
          { name: 'signed_at', readonly: true, label: 'Signed Timestamp' },
          { name: 'decline_reason', label: 'Customer Decline Rationale' }
        ] },
      { tab: 'tenders', title: 'Public Procurement & Tender Bond Linkage',
        note: 'Links corporate quotation to public tender and bank guarantee tracking.',
        fields: [] },
      { tab: 'vault', title: 'Commercial Proposal Vault',
        note: 'Detailed bill of quantities, tender compliance sheets, and signed purchase orders.',
        fields: [] }
    ]
  },

  'M36-form-tender': {
    kind: 'model_form',
    model: 'fix.tender',
    title: 'Public / Institutional Tender Bid',
    back: 'M36-tenders',
    status: { field: 'state' },
    tabs: [
      { id: 'tender_header', label: '1. Tender Bid Info', bn: '১. দরপত্রের তথ্য', icon: '📑', badge: '4' },
      { id: 'bond_compliance', label: '2. Bond & Compliance', bn: '২. বন্ড ও সম্মতি', icon: '🛡️', badge: '3' },
      { id: 'status', label: '3. Tender Outcome', bn: '৩. দরপত্রের ফলাফল', icon: '🏁', badge: '1' }
    ],
    sections: [
      { tab: 'tender_header', title: 'Tender Identification', note: 'Public Procurement Act (PPA 2006) tender bid details.',
        fields: [
          { name: 'name', required: true, label: 'Tender Reference / ID' },
          ] },
      { tab: 'bond_compliance', title: 'Bank Guarantee & Technical Compliance', fields: [
          { name: 'compliance_pct', label: 'Technical Spec Compliance %' }
        ] },
      { tab: 'status', title: 'Tender Award State', fields: [
          { name: 'state', required: true, label: 'Bid Lifecycle State' }
        ] }
    ]
  },
  'M36-form-counter': { kind: 'model_form', model: 'fix.counter.sale',
    title: 'Counter-Offer', back: 'M36-versions',
    status: { field: 'state' },
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
        { name: 'name', label: 'Sale No.', readonly: true },
        { name: 'quantity', label: 'Quantity', required: true },
        { name: 'payment_method', label: 'Payment Method', required: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'serial_or_warranty_ref', label: 'Part Serial / Protection Plan Ref' },
        { name: 'transaction_ref', label: 'bKash / Nagad / POS TrxID' },
        { name: 'notes', label: 'Counter Sale Notes' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'unit_price', label: 'Unit Price', required: true },
        { name: 'total', label: 'Total (BDT)', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'sale_date', label: 'Sale Date', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'shift_id', label: 'Cash Shift' },
        { name: 'branch_id', label: 'Branch' },
        { name: 'customer_id', label: 'Customer' },
        { name: 'product_id', label: 'Product', required: true },
        { name: 'sold_by', label: 'Sold By' }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit', required: true },
        { name: 'mushak_63_ref', label: 'NBR Mushak-6.3 Tax Challan Ref' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M36-form-bond': { kind: 'model_form', model: 'fix.tender.bond',
    title: 'Bid Bond', back: 'M36-bonds',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'flags', label: '5. Status Flags', bn: '৫. অবস্থা নির্দেশক' },
      { id: 'audit', label: '6. System Audit', bn: '৬. সিস্টেম অডিট' },
      { id: 'docs', label: '7. Documents', bn: '৭. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'bond_type', label: 'Bond Type', required: true },
        { name: 'bank', label: 'Bank' },
        { name: 'state', label: 'State', required: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'amount', label: 'Amount' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'expires_on', label: 'Expires On' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'tender_id', label: 'Tender', required: true },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'is_expiring_soon', label: 'Expiring Soon (30d)', readonly: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M36-form-review': { kind: 'model_form', model: 'fix.quote.review',
    title: 'Quotation Review', back: 'M36-internal',
    status: { field: 'decision' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'decision', label: 'Decision', required: true },
        { name: 'notes', label: 'Notes' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'reviewed_at', label: 'Reviewed At', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'quotation_id', label: 'Quotation', required: true },
        { name: 'reviewer_id', label: 'Reviewer' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] }
};

export const REPORT_ROUTES = {
  'M36:Quote Conversion by Channel': 'M36-rpt-conv',
  'M36:Approval Cycle Time': 'M36-rpt-cycle',
  'M36:Decline Reasons Pareto': 'M36-rpt-decline',
  'M36:Tender Win/Loss': 'M36-rpt-tender',
  'M36:Margin on Approved Quotes': 'M36-rpt-margin'
};

export const FORM_MODELS = {
  'M36:Estimate': 'fix.estimate',
  'M36:Quotation (versioned)': 'fix.quotation',
  'M36:Tender Bid': 'fix.tender',
  'M36:Counter-Offer': 'fix.counter.sale'
};

export const FORM_CHIPS = {
  'M36:Estimate': 'M36-form-estimate',
  'M36:Quotation (versioned)': 'M36-form-quotation',
  'M36:Tender Bid': 'M36-form-tender',
  'M36:Counter-Offer': 'M36-form-counter',
  'M36:__by_model__': {
    'fix.estimate': 'M36-form-estimate',
    'fix.quotation': 'M36-form-quotation',
    'fix.tender': 'M36-form-tender',
    'fix.counter.sale': 'M36-form-counter',
    'fix.tender.bond': 'M36-form-bond',
    'fix.quote.review': 'M36-form-review'
  },
  'M36:__by_screen__': {
    'M36-estimates': 'M36-form-estimate',
    'M36-quotes': 'M36-form-quotation',
    'M36-versions': 'M36-form-quotation',
    'M36-loop': 'M36-form-review',
    'M36-declined': 'M36-form-quotation',
    'M36-tenders': 'M36-form-tender',
    'M36-bonds': 'M36-form-bond'
  }
};

export const CREATE = {
  M36: { screen: 'M36-form-quotation', model: 'fix.quotation', label: 'Quotation' }
};
