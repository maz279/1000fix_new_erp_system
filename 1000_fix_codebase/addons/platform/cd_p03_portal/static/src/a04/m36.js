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
    { l: 'Declined → Diagnostic Fee', m: 'declined_conversion', src: false }
  ],
  groups: [
    { en: 'Estimates', screens: [
      { id: 'M36-estimates', en: 'Internal Estimates', bn: 'অভ্যন্তরীণ এস্টিমেট', t: 'g' },
      { id: 'M36-buildup', en: 'Build-Up Workbench', bn: 'বিল্ড-আপ', t: 'g' }
    ]},
    { en: 'Quotations', screens: [
      { id: 'M36-quotes', en: 'Customer Quotations', bn: 'গ্রাহক কোটেশন', t: 'g' },
      { id: 'M36-record', en: 'Quotation Record', bn: 'কোটেশন রেকর্ড', t: 'f' },
      { id: 'M36-versions', en: 'Versions & Counter-Offer', bn: 'ভার্সন ও কাউন্টার', t: 'g' },
      { id: 'M36-esign', en: 'e-Signature & Evidence', bn: 'ই-সাইন', t: 'r' }
    ]},
    { en: 'Approval Loop', screens: [
      { id: 'M36-loop', en: 'Customer Approval Loop', bn: 'গ্রাহক অনুমোদন', t: 'g' },
      { id: 'M36-internal', en: 'Internal Approval Routing', bn: 'অভ্যন্তরীণ অনুমোদন', t: 'g' },
      { id: 'M36-declined', en: 'Declined-Repair Handling', bn: 'প্রত্যাখ্যাত মেরামত', t: 'r' }
    ]},
    { en: 'Tenders', screens: [
      { id: 'M36-tenders', en: 'Tenders & Bids', bn: 'দরপত্র', t: 'g' },
      { id: 'M36-compliance', en: 'Compliance Matrix', bn: 'কমপ্লায়েন্স ম্যাট্রিক্স', t: 'r' },
      { id: 'M36-bonds', en: 'Bid Bonds', bn: 'বিড বন্ড', t: 'g' },
      { id: 'M36-variations', en: 'Variation Orders', bn: 'ভেরিয়েশন অর্ডার', t: 'g' }
    ]}
  ],
  reports: ['Quote Conversion by Channel', 'Approval Cycle Time', 'Decline Reasons Pareto', 'Tender Win/Loss', 'Margin on Approved Quotes'],
  forms: ['Estimate', 'Quotation (versioned)', 'Tender Bid'],
  cross: ['M37 Catalogue', 'M11 Pricing', 'M01 Service Orders'],
  freg: { src: 86, sub: [
    ['1', 'Estimate Build-Up', 10, { model: 'fix.estimate.line', cols: ['estimate_id', 'line_type', 'description', 'quantity', 'unit_price', 'line_total'], screens: ['M36-buildup', 'M36-estimates'], reports: [], forms: ['Estimate'] }],
    ['2', 'Quotation Object', 12, { model: 'fix.quotation', cols: ['name', 'state', 'customer_id', 'version', 'value', 'vat_amount'], screens: ['M36-quotes'], reports: ['Quote Conversion by Channel', 'Margin on Approved Quotes'], forms: ['Quotation (versioned)'] }],
    ['3', 'Versioning', 7, { model: 'fix.quotation', cols: ['name', 'state', 'customer_id', 'version', 'value', 'vat_amount'], screens: ['M36-versions'], reports: [], forms: [], create: false }],
    ['4', 'Approval Routing', 9, { model: 'fix.quote.review', cols: ['quotation_id', 'reviewer_id', 'decision', 'reviewed_at'], screens: ['M36-internal'], reports: ['Approval Cycle Time'], forms: [] }],
    ['5', 'Customer Approval Loop (8 channels)', 13, { model: 'fix.quote.review', cols: ['quotation_id', 'reviewer_id', 'decision', 'reviewed_at'], screens: ['M36-loop'], reports: ['Approval Cycle Time', 'Quote Conversion by Channel'], forms: [] }],
    ['6', 'Partial Accept & Counter', 6, { model: 'fix.quotation', cols: ['name', 'state', 'customer_id', 'version', 'value', 'vat_amount'], screens: ['M36-quotes'], reports: [], forms: [], create: false }],
    ['7', 'e-Signature', 6, { model: 'fix.quotation', cols: ['name', 'customer_id', 'esign_state', 'signed_at', 'state'], screens: ['M36-esign', 'M36-quotes'], reports: [], forms: [], create: false }],
    ['8', 'Declined Handling', 6, { model: 'fix.quotation', cols: ['name', 'customer_id', 'state', 'decline_reason', 'valid_until'], screens: ['M36-declined', 'M36-rpt-decline', 'M36-quotes'], reports: ['Decline Reasons Pareto'], forms: [], create: false }],
    ['9', 'Tender & Bid', 9, { model: 'fix.tender', cols: ['name', 'state', 'client_name', 'due_date', 'estimated_value', 'compliance_pct', 'bonds_required'], screens: ['M36-tenders', 'M36-bonds', 'M36-rpt-tender'], reports: ['Tender Win/Loss'], forms: ['Tender Bid'] }],
    ['10', 'Templates & Bilingual Gen', 8, { model: 'fix.document.template', cols: ['code', 'name', 'name_bn', 'document_type', 'bilingual'], screens: ['M36-compliance'], reports: [], forms: [] }]
  ] }
};

export const SCREENS = {
  /* ---- registry screens restored (A04 zero-trust audit 2026-10-31): nav ids that dead-ended ---- */
  'M36-versions': { kind: 'model_list', model: 'fix.quotation', create: false,
    cols: ["name", "customer_id", "state", "currency_id", "create_date", "company_id", "estimate_id"] },
  'M36-esign': { kind: 'table_report', module: 'M36', report: 'esign_status', title: 'E-Signature Status', period: true },
  'M36-loop': { kind: 'model_list', model: 'fix.quote.review', create: false,
    cols: ["create_date", "quotation_id", "reviewer_id", "decision", "notes", "reviewed_at"],
    empty: 'No quotation review yet. A review is recorded when a quotation is sent for approval or decided by the customer; it is not typed in here.' },
  'M36-internal': { kind: 'model_list', model: 'fix.quote.review', create: false,
    cols: ["create_date", "quotation_id", "reviewer_id", "decision", "notes", "reviewed_at"],
    empty: 'No quotation review yet. A review is recorded when a quotation is sent for approval or decided by the customer; it is not typed in here.' },
  'M36-declined': { kind: 'table_report', module: 'M36', report: 'decline_pareto', title: 'Decline Pareto', period: true },
  // A04 audit M36-7 (C2-C13 build 2026-11-04): a tender moves only through
  // these. The bid decision and the award are the Tender Committee's; a win
  // is approved from the M63 inbox by a member who did not prepare the bid.
  'M36-tenders': { kind: 'model_list', model: 'fix.tender', create: false, stateField: 'state',
    cols: ["name", "state", "client_name", "due_date", "compliance_pct", "bid_decision", "approval_state"],
    actions: [
      { m: 'action_decide_bid', l: 'Decide: Bid (Tender Committee)', ask: 'Basis of the bid decision (scores are on the form)', kwarg: 'reason', states: ['draft'] },
      { m: 'action_decide_no_bid', l: 'Decide: No Bid (Tender Committee)', ask: 'Why not bid?', kwarg: 'reason', states: ['draft'] },
      { m: 'action_submit', l: 'Submit Bid', states: ['draft'] },
      { m: 'action_request_award', l: 'Request Award Approval (award ref and value staged on the form)', ask: 'Justification for the award', kwarg: 'justification', states: ['submitted'] },
      { m: 'action_recall_approval', l: 'Recall Award Request', states: ['submitted'] },
      { m: 'action_record_loss', l: 'Record Loss', ask: 'Loss reason', kwarg: 'reason', states: ['submitted'] },
      { m: 'action_create_contract', l: 'Create Contract (retry)', states: ['won'] },
      { m: 'action_cancel', l: 'Cancel Tender', ask: 'Why is the tender withdrawn?', kwarg: 'reason', states: ['draft', 'submitted'] }
    ] },
  'M36-compliance': { kind: 'table_report', module: 'M36', report: 'tender_compliance', title: 'Tender Compliance', period: true },
  // Report §6 P2 M36 (variation cap): within the cumulative cap the Tender
  // Committee decides a variation; beyond it the Commercial Manager.
  'M36-variations': { kind: 'model_list', model: 'fix.tender.variation', stateField: 'state',
    cols: ['name', 'tender_id', 'amount', 'cumulative_pct', 'within_cap', 'state', 'approval_state'],
    actions: [
      { m: 'action_request', l: 'Request Approval', ask: 'Justification for the variation', kwarg: 'justification', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Request', states: ['draft'] },
      { m: 'action_cancel', l: 'Withdraw Variation', ask: 'Why is it withdrawn?', kwarg: 'reason', states: ['draft'] }
    ] },
  // A04 audit M36-8: a guarantee is activated with the bank's evidence and
  // released or claimed only by a routed DOFA decision on its amount.
  'M36-bonds': { kind: 'model_list', model: 'fix.tender.bond', create: false, stateField: 'state',
    cols: ["name", "state", "amount", "tender_id", "bond_type", "bank", "expires_on", "is_expiring_soon", "approval_state"],
    actions: [
      { m: 'action_activate', l: 'Activate (guarantee issued)', states: ['draft'] },
      { m: 'action_release', l: 'Request Release (after the award)', ask: 'Bank discharge / return reference', kwarg: 'release_ref', states: ['active'] },
      { m: 'action_claim', l: 'Record Encashment (claim)', ask: 'Why was the guarantee encashed?', kwarg: 'reason', states: ['active'] },
      { m: 'action_extend', l: 'Record Extension', ask: 'New expiry date (YYYY-MM-DD)', kwarg: 'expires_on', states: ['active'] },
      { m: 'action_recall_approval', l: 'Recall Release / Claim Request', states: ['active'] }
    ] },


  /* Report screens */
  'M36-rpt-conv': { kind: 'table_report', module: 'M36', report: 'quote_conversion', title: 'Quote Conversion by Channel', period: false },
  'M36-rpt-cycle': { kind: 'table_report', module: 'M36', report: 'approval_cycle', title: 'Approval Cycle Time', period: false },
  'M36-rpt-decline': { kind: 'table_report', module: 'M36', report: 'decline_pareto', title: 'Decline Reasons Pareto', period: false },
  'M36-rpt-tender': { kind: 'table_report', module: 'M36', report: 'tender_winloss', title: 'Tender Win/Loss', period: false },
  'M36-rpt-margin': { kind: 'table_report', module: 'M36', report: 'margin_approved', title: 'Margin on Approved Quotes', period: false },

  // A04 audit M36-2: the estimate's quotation moves only through these
  // (approved estimate, no pending discount, acceptance within validity).
  'M36-estimates': { kind: 'model_list', model: 'fix.estimate', stateField: 'state',
    cols: ['order_id', 'version', 'state', 'grand_total', 'discount', 'expiry_date', 'approved_by', 'quotation_state'],
    actions: [
      { m: 'action_quote', l: 'Quote to Customer', states: ['approved'] },
      { m: 'action_negotiate', l: 'Customer Counter (negotiating)', states: ['approved'] },
      { m: 'action_accept', l: 'Record Acceptance (within validity)', states: ['approved'] },
      { m: 'action_decline', l: 'Record Decline', ask: 'Why did the customer decline?', kwarg: 'reason', states: ['approved'] }
    ] },
  'M36-buildup': { kind: 'model_list', create: false, model: 'fix.estimate.line',
    cols: ['estimate_id', 'description', 'quantity', 'unit_price', 'line_total'] },
  // A04 audit M36-1 (C2-C13 build 2026-11-04): the quotation moves only
  // through these. Approval comes from the M63 inbox (value band, never the
  // author); acceptance from the customer's code, the provider's e-signature
  // callback, or a signed copy recorded by someone other than the author.
  'M36-quotes': { kind: 'model_list', model: 'fix.quotation', stateField: 'state',
    cols: ['name', 'customer_id', 'version', 'value', 'margin_pct', 'valid_until', 'state', 'approval_state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval', ask: 'Business justification (required above BDT 25,000)', kwarg: 'justification', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['draft'] },
      { m: 'action_send', l: 'Issue to Customer', states: ['approved'] },
      { m: 'action_send_acceptance_otp', l: 'Send Acceptance Code', states: ['sent'] },
      { m: 'action_verify_acceptance_otp', l: 'Verify Acceptance Code', ask: 'Code the customer read out', kwarg: 'otp', states: ['sent'] },
      { m: 'action_record_signed_acceptance', l: 'Record Signed Acceptance (attached on the form)', states: ['sent'] },
      { m: 'action_decline', l: 'Record Decline (reason code on the form)', ask: 'Why did the customer decline?', kwarg: 'reason', states: ['sent'] },
      { m: 'action_revise', l: 'Revise (new version)', states: ['sent', 'expired', 'declined'] },
      { m: 'action_convert', l: 'Convert (retry hand-off)', states: ['accepted'] },
      { m: 'action_cancel', l: 'Cancel Quotation', ask: 'Why is it withdrawn?', kwarg: 'reason', states: ['draft', 'approved', 'sent'] }
    ] },
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
        { name: 'quotation_state', label: 'Quotation State', readonly: true },
        { name: 'valid_days', label: 'Valid Days' },
        { name: 'tender_ref', label: 'Tender Reference' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'parts_total', label: 'Parts Total', readonly: true },
        { name: 'labour_total', label: 'Labour Total', readonly: true },
        { name: 'diagnostic_total', label: 'Diagnostic Total', readonly: true },
        { name: 'discount', label: 'Discount' },
        // the rate is the model's: statutory by default, a scheduled reduced
        // rate only by a commercial approver's action - never free entry
        { name: 'vat_rate', label: 'VAT Rate (%)', readonly: true },
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
        { name: 'order_id', label: 'Service Order' },  // optional for a pre-sales estimate; the server requires an order or an opportunity (A03 W8)
        /* the other owner the server accepts: without it a pre-sales estimate
         * could not be saved from M36 at all (fix_real, 12 Nov 2026) */
        { name: 'lead_id', label: 'CRM Opportunity',
          emptyNote: 'No open opportunity yet. An estimate belongs to a service order or to a CRM opportunity: create the opportunity in M07 CRM & Sales Pipeline first.' },
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

  'M36-record': {
    kind: 'model_form',
    model: 'fix.quotation',
    title: 'Commercial Proposal & Tender Quotation',
    back: 'M36-quotes',
    status: { field: 'state' },
    tabs: [
      { id: 'header', label: '1. Proposal Header', bn: '১. প্রস্তাবনা পরিচিতি', icon: '📄', badge: '9' },
      { id: 'pricing', label: '2. Cost, Margins & SRT', bn: '২. খরচ ও মার্জিন', icon: '💵', badge: '7' },
      { id: 'statutory', label: '3. Withholding Tax (TDS)', bn: '৩. উৎসে কর কর্তন', icon: '⚖️', badge: '4' },
      { id: 'approval', label: '4. Internal Approval', bn: '৪. অভ্যন্তরীণ অনুমোদন', icon: '✅', badge: '5' },
      { id: 'esign', label: '5. Customer Acceptance', bn: '৫. গ্রাহক সম্মতি', icon: '✍️', badge: '10' },
      { id: 'handoff', label: '6. Contract & Order Hand-off', bn: '৬. চুক্তি ও অর্ডার', icon: '🔗', badge: '6' },
      { id: 'vault', label: '7. Document Vault', bn: '৭. নথিপত্র', icon: '📁', badge: '0' }
    ],
    sections: [
      { tab: 'header', title: 'Proposal Identity & Version Tracking',
        note: 'Number, version and status are set by the lifecycle (Submit, Issue, Revise); an issued version never changes.',
        fields: [
          { name: 'name', label: 'Quotation Reference (auto)', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'estimate_id', label: 'Originating Technical Estimate (M01)' },
          { name: 'quote_type', required: true, label: 'Converts Into' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'version', label: 'Quotation Version', readonly: true },
          { name: 'parent_version_id', label: 'Previous Version', readonly: true },
          { name: 'valid_until', label: 'Validity Expiration Date' },
          { name: 'state', label: 'Lifecycle Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Direct Cost, Pre-Tax Margin & Value',
        note: 'Linked to an estimate, the value is the estimate total. Without a direct cost the margin is unknown.',
        fields: [
          { name: 'value', required: true, label: 'Quotation Subtotal (BDT)' },
          { name: 'cost_amount', label: 'Direct Labor & Parts Cost (BDT)' },
          { name: 'margin_known', label: 'Margin Known (cost recorded)', readonly: true },
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
      { tab: 'approval', title: 'Value-Band Approval (BRU-QTE-06/07/09)',
        note: 'Submit routes the quotation to a holder of its value band who is not its author; any change after approval sends it back for re-approval.',
        fields: [
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'dofa_tier_required', label: 'Approval Band', readonly: true },
          { name: 'dofa_justification', label: 'Business Justification', type: 'text' },
          { name: 'dofa_approved_by', label: 'Approved By', readonly: true },
          { name: 'approved_at', label: 'Approved At', readonly: true }
        ] },
      { tab: 'esign', title: 'Customer Acceptance & Evidence Pack',
        note: 'Acceptance is a verified customer code, the e-signature provider callback, or a signed copy recorded by someone other than the author, within validity.',
        fields: [
          { name: 'sent_at', label: 'Issued At', readonly: true },
          { name: 'esign_state', label: 'Digital Signature Status', readonly: true },
          { name: 'signed_at', readonly: true, label: 'Signed Timestamp' },
          { name: 'signed_attachment_id', label: 'Signed Quotation (for Record Signed Acceptance)' },
          { name: 'acceptance_method', label: 'Acceptance Method', readonly: true },
          { name: 'acceptance_ref', label: 'Acceptance Reference', readonly: true },
          { name: 'accepted_at', label: 'Accepted At', readonly: true },
          { name: 'evidence_hash', label: 'Evidence Hash (SHA-256)', readonly: true },
          { name: 'decline_reason_code', label: 'Decline Reason (governed list)' },
          { name: 'decline_reason', label: 'Customer Decline Rationale', readonly: true }
        ] },
      { tab: 'handoff', title: 'What the Accepted Quotation Becomes',
        note: 'On acceptance a service quotation releases its M01 order; a contract quotation creates an M08 draft contract.',
        fields: [
          { name: 'contract_family', label: 'Contract Family' },
          { name: 'contract_months', label: 'Contract Term (months)' },
          { name: 'contract_start', label: 'Contract Start' },
          { name: 'service_order_id', label: 'Service Order', readonly: true },
          { name: 'converted_ref', label: 'Converted Into', readonly: true },
          { name: 'converted_at', label: 'Converted At', readonly: true }
        ] },
      { tab: 'vault', title: 'Commercial Proposal Vault',
        note: 'Detailed bill of quantities, tender compliance sheets, and signed purchase orders.',
        fields: [] }
    ]
  },

  'M36-form-tender': {
    lines: {
      field: 'requirement_ids',
      title: 'Compliance Matrix',
      note: 'Every mandatory requirement must be complied with (against its evidence document) or not applicable before the bid is submitted (BRU-QTE-15). Frozen once submitted.',
      fields: [
        { name: 'clause_ref', label: 'Clause' },
        { name: 'requirement', label: 'Requirement', required: true },
        { name: 'mandatory', label: 'Mandatory' },
        { name: 'state', label: 'Status', required: true },
        { name: 'evidence_ref', label: 'Evidence Document Ref' },
        { name: 'response', label: 'Response' }
      ]
    },
    kind: 'model_form',
    model: 'fix.tender',
    title: 'Public / Institutional Tender Bid',
    back: 'M36-tenders',
    status: { field: 'state' },
    tabs: [
      { id: 'tender_header', label: '1. Tender Bid Info', bn: '১. দরপত্রের তথ্য', icon: '📑', badge: '8' },
      { id: 'decision', label: '2. Bid / No-Bid', bn: '২. বিড সিদ্ধান্ত', icon: '⚖️', badge: '9' },
      { id: 'bond_compliance', label: '3. Bond & Compliance', bn: '৩. বন্ড ও সম্মতি', icon: '🛡️', badge: '5' },
      { id: 'status', label: '4. Tender Outcome', bn: '৪. দরপত্রের ফলাফল', icon: '🏁', badge: '12' }
    ],
    sections: [
      { tab: 'tender_header', title: 'Tender Identification', note: 'Public Procurement Act (PPA 2006) tender bid details. Frozen once the bid is submitted.',
        fields: [
          { name: 'name', required: true, label: 'Tender Name' },
          { name: 'reference', label: 'Tender ID / e-GP Ref' },
          { name: 'client_name', required: true, label: 'Tendering Client' },
          { name: 'client_id', label: 'Procuring Entity (contract party)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'due_date', required: true, label: 'Submission Deadline' },
          { name: 'estimated_value', label: 'Official Estimated Value' },
          { name: 'bid_value', label: 'Bid Price Lodged' },
          { name: 'state', label: 'Bid Lifecycle State', readonly: true }
        ] },
      { tab: 'decision', title: 'Bid / No-Bid Decision (FR-QTE-044)', note: 'Score 1-5; the Tender Committee decides, never the person who registered the tender.',
        fields: [
          { name: 'score_fit', label: 'Fit' },
          { name: 'score_capacity', label: 'Capacity' },
          { name: 'score_competition', label: 'Competition' },
          { name: 'score_margin', label: 'Margin' },
          { name: 'score_risk', label: 'Risk' },
          { name: 'bid_score', label: 'Bid Score (avg)', readonly: true },
          { name: 'bid_decision', label: 'Decision', readonly: true },
          { name: 'bid_decision_by', label: 'Decided By', readonly: true },
          { name: 'bid_decision_reason', label: 'Basis', readonly: true }
        ] },
      { tab: 'bond_compliance', title: 'Bank Guarantee & Technical Compliance', note: 'The bid security must cover the bid validity plus 28 days and stay within 3% of the estimated value (PPR 2008 r.25).',
        fields: [
          { name: 'bonds_required', label: 'Bid Security Required' },
          { name: 'bid_security_amount', label: 'Bid Security Required (BDT)' },
          { name: 'bid_validity_days', label: 'Bid Validity (days)' },
          { name: 'compliance_pct', label: 'Compliance % (computed)', readonly: true },
          { name: 'open_mandatory_count', label: 'Open Mandatory Items', readonly: true }
        ] },
      { tab: 'status', title: 'Award & Contract', note: 'Stage the award letter and value, then Request Award: a Tender Committee member who did not prepare the bid approves it, and the M08 contract is created.',
        fields: [
          { name: 'award_ref', label: 'Notification of Award Ref' },
          { name: 'awarded_value', label: 'Awarded Value' },
          { name: 'award_variation_pct', label: 'Award vs Bid (%)', readonly: true },
          { name: 'contract_value', label: 'Contract Value (with variations)', readonly: true },
          { name: 'contract_family', label: 'Contract Family' },
          { name: 'contract_months', label: 'Contract Term (months)' },
          { name: 'performance_security_pct', label: 'Performance Security (%)' },
          { name: 'approval_state', label: 'Award Approval', readonly: true },
          { name: 'awarded_by', label: 'Award Approved By', readonly: true },
          { name: 'award_date', label: 'Award Date', readonly: true },
          { name: 'converted_ref', label: 'Contract', readonly: true },
          { name: 'awarded_to', label: 'Awarded To (on a loss)' },
          { name: 'winning_value', label: 'Winning Value (on a loss)' },
          { name: 'loss_reason', label: 'Loss Reason', readonly: true }
        ] }
    ]
  },
  /* NOT a counter-offer: fix.counter.sale is the Front-Desk cash-drawer sale
   * (M04). The "Counter-Offer" chip opened this form; a customer's counter is
   * an action on the quotation ("Customer Counter (negotiating)", "Revise
   * (new version)") on Quotations. The chip is gone (2026-11-12). The screen
   * stays only because its fields still feed the counter-sale write
   * whitelist in a02/writable.py (the generator unions every form on a
   * model); removing it is an A02 change. */
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
        { name: 'mushak_63_ref', readonly: true, label: 'NBR Mushak-6.3 Tax Challan Ref' }
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
      { tab: 'general', title: '1. General', note: 'What the bank issued is frozen once the guarantee is active; release and encashment are approved on the amount (DOFA).', fields: [
        { name: 'bond_type', label: 'Bond Type', required: true },
        { name: 'bank', label: 'Bank' },
        { name: 'guarantee_no', label: 'Bank Guarantee No.' },
        { name: 'state', label: 'State', readonly: true },
        { name: 'requested_action', label: 'Pending Request', readonly: true },
        { name: 'approval_state', label: 'Approval', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'amount', label: 'Amount' },
        { name: 'dofa_tier_required', label: 'Approval Tier', readonly: true },
        { name: 'release_ref', label: 'Bank Discharge Ref', readonly: true },
        { name: 'claim_reason', label: 'Encashment Reason', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'issued_on', label: 'Issued On' },
        { name: 'expires_on', label: 'Expires On' },
        { name: 'days_to_expiry', label: 'Days to Expiry', readonly: true },
        { name: 'released_at', label: 'Released At', readonly: true },
        { name: 'claimed_at', label: 'Claimed At', readonly: true }
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

  'M36-form-variation': { kind: 'model_form', model: 'fix.tender.variation',
    title: 'Variation Order', back: 'M36-variations',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Variation', bn: '১. ভেরিয়েশন' },
      { id: 'decision', label: '2. Decision', bn: '২. সিদ্ধান্ত' }
    ],
    sections: [
      { tab: 'general', title: 'Variation Order', note: 'Frozen once requested. The cumulative variation decides who approves it (cap: cd_quotation.variation_cap_pct).', fields: [
        { name: 'name', label: 'Variation Ref', required: true },
        { name: 'tender_id', label: 'Tender (won)', required: true },
        { name: 'amount', label: 'Change to Contract Value' },
        { name: 'reason', label: 'Reason', type: 'text', required: true }
      ] },
      { tab: 'decision', title: 'Decision', fields: [
        { name: 'cumulative_pct', label: 'Cumulative Variation (%)', readonly: true },
        { name: 'within_cap', label: 'Within Cap', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'approval_state', label: 'Approval', readonly: true },
        { name: 'approved_by', label: 'Approved By', readonly: true },
        { name: 'approved_at', label: 'Approved At', readonly: true }
      ] }
    ] },

  'M36-form-review': { kind: 'model_form', model: 'fix.quote.review',
    title: 'Quotation Review', back: 'M36-internal',
    create: false, pick: 'A review is recorded by the approval workflow: open one from Internal Approvals.',
    status: { field: 'decision' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', note: 'Written by the approver decision in the M63 inbox; the log cannot be typed or edited.', fields: [
        { name: 'decision', label: 'Decision', readonly: true },
        { name: 'notes', label: 'Notes', readonly: true },
        { name: 'version', label: 'Version Reviewed', readonly: true },
        { name: 'value_reviewed', label: 'Value Reviewed', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'reviewed_at', label: 'Reviewed At', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'quotation_id', label: 'Quotation', readonly: true },
        { name: 'reviewer_id', label: 'Reviewer', readonly: true },
        { name: 'on_behalf_of_id', label: 'On Behalf Of', readonly: true }
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
  'M36:Tender Bid': 'fix.tender'
};

export const FORM_CHIPS = {
  'M36:Estimate': 'M36-form-estimate',
  'M36:Quotation (versioned)': 'M36-record',
  'M36:Tender Bid': 'M36-form-tender',
  'M36:__by_model__': {
    'fix.estimate': 'M36-form-estimate',
    'fix.quotation': 'M36-record',
    'fix.tender': 'M36-form-tender',
    'fix.tender.bond': 'M36-form-bond',
    'fix.quote.review': 'M36-form-review',
    'fix.tender.variation': 'M36-form-variation'
  },
  'M36:__by_screen__': {
    'M36-estimates': 'M36-form-estimate',
    'M36-quotes': 'M36-record',
    'M36-versions': 'M36-record',
    'M36-loop': 'M36-form-review',
    'M36-declined': 'M36-record',
    'M36-tenders': 'M36-form-tender',
    'M36-bonds': 'M36-form-bond',
    'M36-variations': 'M36-form-variation'
  }
};

export const CREATE = {
  M36: { screen: 'M36-record', model: 'fix.quotation', label: 'Quotation' }
};
