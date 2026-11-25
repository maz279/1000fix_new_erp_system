/** @odoo-module **/
/* A04 · Commercial & Revenue — M36 Quotations & Tenders (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 86,
 * plus the tender BOQ / price schedule screen (quote-to-cash, 13 Nov 2026).
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
      { id: 'M36-buildup', en: 'Build-Up Workbench', bn: 'বিল্ড-আপ', t: 'g' },
      { id: 'M36-est-reviews', en: 'Technical Reviews (second opinion)', bn: 'কারিগরি পর্যালোচনা', t: 'g' }
    ]},
    { en: 'Quotations', screens: [
      { id: 'M36-quotes', en: 'Customer Quotations', bn: 'গ্রাহক কোটেশন', t: 'g' },
      { id: 'M36-record', en: 'Quotation Record', bn: 'কোটেশন রেকর্ড', t: 'f' },
      { id: 'M36-proformas', en: 'Proforma Invoices (Local)', bn: 'প্রফর্মা ইনভয়েস (স্থানীয়)', t: 'g' },
      { id: 'M36-billing-quotes', en: 'Billing Plan & Advances', bn: 'বিলিং পরিকল্পনা ও অগ্রিম', t: 'g' },
      { id: 'M36-billing-lines', en: 'Billing Plan Lines', bn: 'বিলিং লাইন', t: 'g' },
      { id: 'M36-handoffs', en: 'Fulfilment Hand-offs', bn: 'হস্তান্তর লগ', t: 'g' },
      { id: 'M36-templates', en: 'Quotation Templates', bn: 'কোটেশন টেমপ্লেট', t: 'g' },
      { id: 'M36-std-terms', en: 'Standard Terms Library', bn: 'মানক শর্তাবলি', t: 'g' },
      { id: 'M36-terms', en: 'Quotation Terms & Exclusions', bn: 'কোটেশনের শর্ত ও বর্জন', t: 'g' },
      { id: 'M36-renewals', en: 'Renewal Quotations', bn: 'নবায়ন কোটেশন', t: 'g' },
      { id: 'M36-legal-holds', en: 'Legal Holds', bn: 'আইনি স্থগিতাদেশ', t: 'g' },
      { id: 'M36-doc-templates', en: 'Bilingual Document Templates', bn: 'দ্বিভাষিক নথি টেমপ্লেট', t: 'g' },
      { id: 'M36-contract-scope', en: 'Contracted Scope (from quotations)', bn: 'চুক্তির পরিধি', t: 'g' },
      { id: 'M36-proposed-entitlements', en: 'Proposed Contract Entitlements', bn: 'প্রস্তাবিত এনটাইটেলমেন্ট', t: 'g' },
      { id: 'M36-versions', en: 'Quotation Versions', bn: 'কোটেশন ভার্সন', t: 'g' },
      { id: 'M36-esign', en: 'e-Signature & Evidence', bn: 'ই-সাইন', t: 'r' }
    ]},
    { en: 'Approval Loop', screens: [
      { id: 'M36-loop', en: 'Customer Approval Loop', bn: 'গ্রাহক অনুমোদন', t: 'g' },
      { id: 'M36-deliveries', en: 'Deliveries & Views', bn: 'ডেলিভারি ও দেখা', t: 'g' },
      { id: 'M36-counters', en: 'Counter-Offers & Partial Acceptance', bn: 'কাউন্টার অফার ও আংশিক সম্মতি', t: 'g' },
      { id: 'M36-internal', en: 'Internal Approval Routing', bn: 'অভ্যন্তরীণ অনুমোদন', t: 'g' },
      { id: 'M36-pending', en: 'Drafts Awaiting Approval', bn: 'অনুমোদনের অপেক্ষায় খসড়া', t: 'g' },
      { id: 'M36-term-deviations', en: 'Term Deviations Awaiting CCO / CFO', bn: 'শর্ত বিচ্যুতি অনুমোদন', t: 'g' },
      { id: 'M36-credit-overrides', en: 'Credit Gate Overrides (Finance)', bn: 'ক্রেডিট ওভাররাইড', t: 'g' },
      { id: 'M36-declined', en: 'Declined-Repair Handling', bn: 'প্রত্যাখ্যাত মেরামত', t: 'r' }
    ]},
    { en: 'Tenders', screens: [
      { id: 'M36-tenders', en: 'Tenders & Bids', bn: 'দরপত্র', t: 'g' },
      { id: 'M36-boq', en: 'Tender BOQ / Price Schedule', bn: 'দরপত্র BOQ / মূল্য তফসিল', t: 'g' },
      { id: 'M36-compliance', en: 'Compliance Matrix', bn: 'কমপ্লায়েন্স ম্যাট্রিক্স', t: 'r' },
      { id: 'M36-bonds', en: 'Bid Bonds', bn: 'বিড বন্ড', t: 'g' },
      { id: 'M36-variations', en: 'Variation Orders', bn: 'ভেরিয়েশন অর্ডার', t: 'g' },
      { id: 'M36-tender-docs', en: 'Submission Pack (document checklist)', bn: 'দাখিলের নথি তালিকা', t: 'g' },
      { id: 'M36-tender-outcomes', en: 'Tender Outcomes & Loss Reasons', bn: 'দরপত্রের ফলাফল', t: 'g' }
    ]}
  ],
  reports: ['Quote Conversion by Channel', 'Approval Cycle Time', 'Decline Reasons Pareto', 'Tender Win/Loss', 'Margin on Approved Quotes'],
  forms: ['Estimate', 'Quotation (versioned)', 'Revise a Quotation', 'Submit for Internal Approval',
    'Issue to the Customer', 'Quotation Delivery', 'Accept by Customer Code', 'Record Signed Acceptance',
    'Counter-Offer / Partial Acceptance', 'Decide a Counter-Offer', 'Record a Customer Decline',
    'Tender Bid', 'Bid Bond', 'Variation Order', 'Quotation Template', 'Document Template (bilingual)',
    'Proforma Invoice (Local)',
    'Technical Review Request', 'Record Technical Review Outcome', 'Quotation Term', 'Renewal Quotation',
    'Decide a Term Deviation', 'Finance Credit Override', 'Accept by Phone (recorded consent)',
    'Legal Hold', 'Release a Legal Hold', 'Tender Document', 'Tender Outcome (loss)', 'Standard Term (library)',
    'Bulk Estate Quotation (asset upload)', 'Compare with the Previous Version', 'Send Customer Approval Link'],
  cross: ['M37 Catalogue', 'M11 Pricing', 'M01 Service Orders'],
  /* Capture audit 2026-11-14 (spec sections 5, 8.2, 10.1): each page's
   * "+ New" captures the record the page names. Before it only page 2 had
   * one; 3-8 and 10 captured nothing, 1 and 9 had a chip only. The
   * quotation lifecycle moves by its workflow methods, so the quotation
   * pages pick an existing quotation and run the step (never a write). */
  /* Capture audit, second pass 2026-11-19 (FR-QTE-009/018/024/027/028/042/
   * 046/048, BRU-QTE-08/14/15/16/17): the spec records the pages are about
   * that still had nowhere to be captured now have their forms. */
  freg: { src: 86, sub: [
    ['1', 'Estimate Build-Up', 10, { model: 'fix.estimate.line', cols: ['estimate_id', 'line_type', 'description', 'quantity', 'unit_price', 'line_total'], screens: ['M36-buildup', 'M36-estimates', 'M36-est-reviews'], reports: [], forms: ['Estimate', 'Technical Review Request', 'Record Technical Review Outcome'], create: 'M36-form-estimate' }],
    ['2', 'Quotation Object', 12, { model: 'fix.quotation', cols: ['name', 'state', 'customer_id', 'version', 'value', 'vat_amount'], screens: ['M36-quotes', 'M36-terms', 'M36-renewals', 'M36-proformas', 'M36-billing-quotes', 'M36-billing-lines', 'M36-handoffs', 'M36-contract-scope', 'M36-proposed-entitlements'], reports: ['Quote Conversion by Channel', 'Margin on Approved Quotes'], forms: ['Quotation (versioned)', 'Quotation Term', 'Renewal Quotation', 'Bulk Estate Quotation (asset upload)', 'Proforma Invoice (Local)', 'Proposed Contract Entitlement'] }],
    /* FR-QTE-012/015, BRU-QTE-02/04: an issued, expired or declined version is
     * never edited; it is revised into the next version. */
    ['3', 'Versioning', 7, { model: 'fix.quotation', cols: ['name', 'version', 'parent_version_id', 'state', 'customer_id', 'value', 'valid_until'], screens: ['M36-versions'], reports: [], forms: ['Revise a Quotation', 'Compare with the Previous Version'], create: 'M36-form-revise' }],
    /* FR-QTE-025..032: submitted to the value-band approver (never the author);
     * the review log is written by the decision in the M63 inbox. */
    ['4', 'Approval Routing', 9, { model: 'fix.quote.review', cols: ['quotation_id', 'version', 'reviewer_id', 'decision', 'value_reviewed', 'reviewed_at'], screens: ['M36-internal', 'M36-pending', 'M36-term-deviations', 'M36-credit-overrides'], reports: ['Approval Cycle Time'], forms: ['Submit for Internal Approval', 'Decide a Term Deviation', 'Finance Credit Override'], create: 'M36-form-submit' }],
    /* FR-QTE-033/034/039/042: issued on a channel, every delivery recorded,
     * accepted on the code the customer reads out. */
    ['5', 'Customer Approval Loop (8 channels)', 13, { model: 'fix.quotation.delivery', cols: ['quotation_id', 'channel', 'recipient', 'sent_at', 'delivered_at', 'first_viewed_at', 'view_count'], screens: ['M36-loop', 'M36-deliveries'], reports: ['Quote Conversion by Channel'], forms: ['Issue to the Customer', 'Send Customer Approval Link', 'Quotation Delivery', 'Accept by Customer Code', 'Accept by Phone (recorded consent)'], create: 'M36-form-issue' }],
    /* FR-QTE-035/036, BRU-QTE-11, T-03: the customer's counter or line-level
     * decision is a record, decided by someone other than who took it down;
     * "revise" derives the next version for approval. */
    ['6', 'Partial Accept & Counter', 6, { model: 'fix.quotation.counter', cols: ['name', 'kind', 'channel', 'requested_value', 'state', 'decided_by_id', 'revised_quotation_id'], screens: ['M36-counters', 'M36-loop'], reports: [], forms: ['Counter-Offer / Partial Acceptance', 'Decide a Counter-Offer'] }],
    /* FR-QTE-037/038: the signed copy or the customer's code; the evidence
     * pack is sealed by the acceptance. */
    ['7', 'e-Signature', 6, { model: 'fix.quotation', cols: ['name', 'customer_id', 'esign_state', 'acceptance_method', 'signed_at', 'evidence_hash', 'state'], screens: ['M36-esign', 'M36-loop', 'M36-legal-holds'], reports: [], forms: ['Record Signed Acceptance', 'Accept by Customer Code', 'Accept by Phone (recorded consent)', 'Legal Hold', 'Release a Legal Hold'], create: 'M36-form-signed' }],
    /* FR-QTE-041, BRU-QTE-12/16: a governed reason; the service order gets the
     * return / collection task with the diagnostic fee owed. */
    ['8', 'Declined Handling', 6, { model: 'fix.quotation', cols: ['name', 'customer_id', 'state', 'decline_reason_code', 'decline_reason', 'declined_at'], screens: ['M36-declined', 'M36-rpt-decline', 'M36-loop'], reports: ['Decline Reasons Pareto'], forms: ['Record a Customer Decline'], create: 'M36-form-decline' }],
    ['9', 'Tender & Bid', 9, { model: 'fix.tender', cols: ['name', 'state', 'client_name', 'due_date', 'estimated_value', 'compliance_pct', 'bonds_required'], screens: ['M36-tenders', 'M36-boq', 'M36-compliance', 'M36-tender-docs', 'M36-bonds', 'M36-variations', 'M36-tender-outcomes', 'M36-rpt-tender'], reports: ['Tender Win/Loss'], forms: ['Tender Bid', 'Tender Document', 'Bid Bond', 'Variation Order', 'Tender Outcome (loss)'] }],
    /* FR-QTE-008/018/019: the quotation templates (terms, lines, options) and
     * the bilingual document templates the PDFs are generated from (M24). */
    ['10', 'Templates & Bilingual Gen', 8, { model: 'fix.quotation.template', cols: ['sequence', 'name', 'segment', 'quote_type', 'payment_term_id', 'advance_pct', 'validity_days'], screens: ['M36-templates', 'M36-std-terms', 'M36-doc-templates'], reports: [], forms: ['Quotation Template', 'Standard Term (library)', 'Document Template (bilingual)'] }]
  ] }
};

export const SCREENS = {
  /* ---- registry screens restored (A04 zero-trust audit 2026-10-31): nav ids that dead-ended ---- */
  'M36-versions': { kind: 'model_list', model: 'fix.quotation', create: false,
    cols: ['name', 'version', 'parent_version_id', 'state', 'customer_id', 'value', 'valid_until', 'create_date'],
    empty: 'No quotation yet. Revise a Quotation makes the next version of an issued, expired or declined one.' },
  'M36-esign': { kind: 'table_report', module: 'M36', report: 'esign_status', title: 'E-Signature Status', period: true },
  /* Capture audit 2026-11-14: the customer loop is the quotations WITH the
   * customer (it listed the internal review log, the same as page 4). */
  'M36-loop': { kind: 'model_list', model: 'fix.quotation', create: false, stateField: 'state',
    domain: [['state', '=', 'sent']],
    cols: ['name', 'version', 'customer_id', 'amount_total', 'valid_until', 'delivery_channel', 'delivery_count', 'first_viewed_at', 'esign_state'],
    empty: 'No quotation is with a customer. Issue an approved quotation with Issue to the Customer.',
    actions: [
      { m: 'action_send_acceptance_otp', l: 'Send Acceptance Code', states: ['sent'] },
      { m: 'action_revise', l: 'Revise (new version)', states: ['sent'] }
    ] },
  /* FR-QTE-019: the bilingual (Bengali / English) document templates the
   * quotation PDF is generated from; the M24 template form captures them. */
  'M36-doc-templates': { kind: 'model_list', model: 'fix.document.template',
    cols: ['code', 'name', 'name_bn', 'document_type', 'bilingual', 'requires_approval'],
    empty: 'No document template yet.' },
  'M36-deliveries': { kind: 'model_list', model: 'fix.quotation.delivery',
    cols: ['quotation_id', 'version', 'channel', 'recipient', 'sent_at', 'delivered_at', 'first_viewed_at', 'view_count', 'recorded_by_id'],
    empty: 'No delivery recorded yet. Issuing a quotation on a channel records its first delivery; a re-send is recorded here.' },
  'M36-pending': { kind: 'model_list', model: 'fix.quotation', create: false, stateField: 'state',
    domain: [['state', '=', 'draft']],
    cols: ['name', 'version', 'customer_id', 'value', 'margin_pct', 'dofa_tier_required', 'approval_state'],
    empty: 'No draft quotation. A draft is submitted with Submit for Internal Approval.',
    actions: [
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['draft'] }
    ] },
  'M36-counters': { kind: 'model_list', model: 'fix.quotation.counter', stateField: 'state',
    cols: ['name', 'customer_id', 'kind', 'channel', 'quoted_value', 'requested_value', 'state', 'decided_by_id', 'revised_quotation_id'],
    empty: 'No counter-offer yet. Record what the customer asked for on a quotation they hold.' },
  'M36-internal': { kind: 'model_list', model: 'fix.quote.review', create: false,
    cols: ['reviewed_at', 'quotation_id', 'version', 'reviewer_id', 'on_behalf_of_id', 'decision', 'value_reviewed', 'notes'],
    empty: 'No quotation review yet. A review is recorded when a quotation is sent for approval or decided by the customer; it is not typed in here.' },
  'M36-declined': { kind: 'table_report', module: 'M36', report: 'decline_pareto', title: 'Decline Pareto', period: true },
  // A04 audit M36-7 (C2-C13 build 2026-11-04): a tender moves only through
  // these. The bid decision and the award are the Tender Committee's; a win
  // is approved from the M63 inbox by a member who did not prepare the bid.
  'M36-tenders': { kind: 'model_list', model: 'fix.tender', stateField: 'state',
    cols: ["name", "state", "client_name", "due_date", "compliance_pct", "bid_decision", "approval_state"],
    actions: [
      { m: 'action_decide_bid', l: 'Decide: Bid (Tender Committee)', ask: 'Basis of the bid decision (scores are on the form)', kwarg: 'reason', states: ['draft'] },
      { m: 'action_decide_no_bid', l: 'Decide: No Bid (Tender Committee)', ask: 'Why not bid?', kwarg: 'reason', states: ['draft'] },
      { m: 'action_import_boq', l: 'Import BOQ (price schedule file on the BOQ screen)', states: ['draft'] },
      { m: 'action_price_as_quotation', l: 'Price BOQ as Quotation (for internal approval)', states: ['draft'] },
      { m: 'action_submit', l: 'Submit Bid (quotation approved, every BOQ item priced)', states: ['draft'] },
      { m: 'action_request_award', l: 'Request Award Approval (award ref and value staged on the form)', ask: 'Justification for the award', kwarg: 'justification', states: ['submitted'] },
      { m: 'action_recall_approval', l: 'Recall Award Request', states: ['submitted'] },
      { m: 'action_create_contract', l: 'Create Contract (retry)', states: ['won'] },
      { m: 'action_record_acceptance', l: 'Record Acceptance Certificate (staged on the form)', states: ['won'] },
      { m: 'action_cancel', l: 'Cancel Tender', ask: 'Why is the tender withdrawn?', kwarg: 'reason', states: ['draft', 'submitted'] }
    ] },
  // Quote-to-cash, tender part (13 Nov 2026): the BOQ / price schedule
  // (BPPA e-PG2-3A goods / 3B related services, prices incl. VAT) is imported
  // from the procuring entity's sheet, priced on a contract quotation that
  // takes the value-band approval, and frozen once the bid is submitted.
  'M36-boq': { kind: 'model_list', model: 'fix.tender', create: false, stateField: 'state',
    cols: ['name', 'reference', 'egp_package_no', 'state', 'boq_line_count', 'boq_unpriced_count', 'boq_total', 'quotation_id', 'quotation_state', 'bid_value'],
    empty: 'No tender yet. Register the tender on Tenders & Bids, then open it here to load its price schedule.',
    actions: [
      { m: 'action_import_boq', l: 'Import BOQ (from the uploaded / attached .xlsx or .csv)', states: ['draft'] },
      { m: 'action_price_as_quotation', l: 'Price BOQ as Quotation (for internal approval)', states: ['draft'] },
      { m: 'action_submit', l: 'Submit Bid', states: ['draft'] }
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
  'M36-bonds': { kind: 'model_list', model: 'fix.tender.bond', stateField: 'state',
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
      { m: 'action_accept', l: 'Record Acceptance (within validity)', ask: 'Customer acceptance evidence (signed slip no., message or call reference)', kwarg: 'evidence', states: ['approved'] },
      { m: 'action_decline', l: 'Record Decline', ask: 'Why did the customer decline?', kwarg: 'reason', states: ['approved'] },
      { m: 'action_create_proforma', l: 'Raise Proforma Invoice', states: ['sent', 'approved'] },
      { m: 'action_fix_print', l: '🖨 Print Estimate (PDF)' },
      { m: 'action_fix_print_receipt', l: '🧾 Estimate Slip (80 mm)' }
    ] },
  'M36-buildup': { kind: 'model_list', create: false, model: 'fix.estimate.line',
    cols: ['estimate_id', 'description', 'quantity', 'unit_price', 'line_total'] },
  // A04 audit M36-1 (C2-C13 build 2026-11-04): the quotation moves only
  // through these. Approval comes from the M63 inbox (value band, never the
  // author); acceptance from the customer's code, the provider's e-signature
  // callback, or a signed copy recorded by someone other than the author.
  'M36-quotes': { kind: 'model_list', model: 'fix.quotation', stateField: 'state',
    cols: ['name', 'customer_id', 'version', 'value', 'amount_total', 'margin_pct', 'valid_until', 'state', 'approval_state'],
    actions: [
      { m: 'action_pull_estimate_lines', l: 'Pull Lines from Estimate', states: ['draft'] },
      { m: 'action_apply_template', l: 'Apply Template (replaces the lines)', states: ['draft'] },
      { m: 'action_apply_standard_terms', l: 'Attach the Standard Terms', states: ['draft'] },
      { m: 'action_import_estate', l: 'Re-import the Asset Upload (replaces the lines)', states: ['draft'] },
      { m: 'action_choose_option', l: 'Customer Chooses Option', ask: 'Which option did the customer take? (its description)', kwarg: 'choice', states: ['draft', 'approved', 'sent'] },
      { m: 'action_submit', l: 'Submit for Approval', ask: 'Business justification (required above BDT 25,000)', kwarg: 'justification', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['draft'] },
      { m: 'action_send', l: 'Issue to Customer', states: ['approved'] },
      { m: 'action_send_acceptance_otp', l: 'Send Acceptance Code', states: ['sent'] },
      { m: 'action_verify_acceptance_otp', l: 'Verify Acceptance Code', ask: 'Code the customer read out', kwarg: 'otp', states: ['sent'] },
      { m: 'action_record_signed_acceptance', l: 'Record Signed Acceptance (attached on the form)', states: ['sent'] },
      { m: 'action_decline', l: 'Record Decline (reason code on the form)', ask: 'Why did the customer decline?', kwarg: 'reason', states: ['sent'] },
      { m: 'action_revise', l: 'Revise (new version)', states: ['sent', 'expired', 'declined'] },
      { m: 'action_convert', l: 'Convert (retry hand-off)', states: ['accepted'] },
      { m: 'action_cancel', l: 'Cancel Quotation', ask: 'Why is it withdrawn?', kwarg: 'reason', states: ['draft', 'approved', 'sent'] },
      { m: 'action_create_proforma', l: 'Raise Proforma Invoice', states: ['approved', 'sent', 'accepted'] },
      { m: 'action_fix_print', l: '🖨 Print Quotation (PDF)' },
      { m: 'action_fix_print_receipt', l: '🧾 Quotation Slip (80 mm)' }
    ] },
  // Commercial document standard (17 Nov 2026): the customer's LOCAL
  // proforma invoice - from a quotation, an estimate or typed - with the same
  // line standard as every document; issued with its PI number, then
  // converted into the draft tax invoice (Mushak 6.3 at issue).
  'M36-proformas': { kind: 'model_list', model: 'fix.sales.proforma', stateField: 'state',
    cols: ['name', 'date', 'customer_id', 'customer_category', 'quotation_id', 'taxable_amount', 'vat_amount', 'amount_total', 'advance_amount', 'valid_until', 'invoice_id', 'state'],
    empty: 'No proforma invoice yet. + New here, or Raise Proforma Invoice from a quotation or an estimate.',
    actions: [
      { m: 'action_issue', l: 'Issue to Customer (PI number)', states: ['draft'] },
      { m: 'action_convert_to_invoice', l: 'Convert to Tax Invoice (draft)', states: ['issued'] },
      { m: 'action_cancel', l: 'Cancel Proforma', ask: 'Why is the proforma cancelled?', kwarg: 'reason', states: ['draft', 'issued'] },
      { m: 'action_reset_draft', l: 'Back to Draft', states: ['cancelled'] },
      { m: 'action_fix_print', l: '🖨 Print Proforma (PDF)' },
      { m: 'action_fix_print_receipt', l: '🧾 Proforma Receipt (80 mm)' }
    ] },
  'M36-form-proforma': {
    kind: 'model_form',
    model: 'fix.sales.proforma',
    title: 'Proforma Invoice (Local Customer)',
    back: 'M36-proformas',
    status: { field: 'state', labels: { draft: 'Draft', issued: 'Issued to Customer', converted: 'Converted to Invoice', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'customer', label: '1. Customer & Bill-to', bn: '১. গ্রাহক ও বিল-টু', icon: '👤', badge: '9' },
      { id: 'lines', label: '2. Items & Charges', bn: '২. পণ্য ও চার্জ', icon: '🧾', badge: '6' },
      { id: 'terms', label: '3. Terms & Delivery', bn: '৩. শর্ত ও ডেলিভারি', icon: '🤝', badge: '9' },
      { id: 'links', label: '4. Source & Invoice', bn: '৪. উৎস ও ইনভয়েস', icon: '🔗', badge: '5' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথিপত্র', icon: '📁', badge: '0' }
    ],
    sections: [
      { tab: 'customer', title: 'Customer', note: 'The category decides what the proforma must state: a walk-in customer\'s name and phone, the buyer\'s BIN for corporate, dealer and government customers.',
        fields: [
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'customer_category', label: 'Customer Category' },
          { name: 'date', required: true, label: 'Proforma Date' },
          { name: 'valid_until', label: 'Valid Until' },
          { name: 'bill_to_name', label: 'Bill-to Name (walk-in: the person)' },
          { name: 'bill_to_phone', label: 'Bill-to Phone' },
          { name: 'bill_to_address', type: 'text', label: 'Bill-to Address' },
          { name: 'customer_bin', label: 'Buyer BIN / e-TIN' },
          { name: 'salesperson_id', label: 'Sales Person' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ] },
      { tab: 'lines', title: 'Totals from the lines', note: 'Taxable value = the lines less their discounts and the overall discount; VAT is M51\'s determination, exactly as the tax invoice will state it.',
        fields: [
          { name: 'overall_discount', label: 'Overall Discount (BDT)' },
          { name: 'gross_total', readonly: true, label: 'Amount before Discount' },
          { name: 'discount_total', readonly: true, label: 'Total Discount' },
          { name: 'taxable_amount', readonly: true, label: 'Taxable Value' },
          { name: 'vat_amount', readonly: true, label: 'VAT' },
          { name: 'amount_total', readonly: true, label: 'Grand Total' }
        ] },
      { tab: 'terms', title: 'Payment, delivery and warranty',
        fields: [
          { name: 'advance_pct', label: 'Advance Required (%)' },
          { name: 'advance_amount', readonly: true, label: 'Advance Required (BDT)' },
          { name: 'payment_term_id', label: 'Payment Terms' },
          { name: 'payment_method_ids', label: 'Payment Methods Accepted' },
          { name: 'customer_po_ref', label: 'Customer PO / Ref No.' },
          { name: 'customer_po_date', label: 'Customer PO Date' },
          { name: 'service_item', label: 'Service Item (device, model, serial)' },
          { name: 'delivery_address', type: 'text', label: 'Delivery / Service Address' },
          { name: 'delivery_terms', type: 'text', label: 'Delivery Terms' },
          { name: 'warranty_terms', type: 'text', label: 'Warranty Terms' },
          { name: 'terms', type: 'text', label: 'Terms & Conditions' },
          { name: 'remarks', type: 'text', label: 'Remarks' }
        ] },
      { tab: 'links', title: 'Where it came from and what it became', note: 'Read from the lifecycle.',
        fields: [
          { name: 'name', readonly: true, label: 'Proforma No.' },
          { name: 'quotation_id', label: 'From Quotation' },
          { name: 'estimate_id', label: 'From Estimate' },
          { name: 'invoice_id', readonly: true, label: 'Tax Invoice' },
          { name: 'issued_by_id', readonly: true, label: 'Issued By' },
          { name: 'issued_at', readonly: true, label: 'Issued At' }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The customer PO, the signed proforma and the advance proof attach to this record.', fields: [] }
    ],
    lines: {
      field: 'line_ids',
      tab: 'lines',
      title: 'Items & Charges (SL / code / description / qty / unit / price / discount)',
      note: 'Spare Part, Accessory and Finished Product lines take an inventory item by its part number; Service, Labour, Support, Diagnostic, Call-out, Transport, Installation and Fee lines take a charge code (left empty: the generic code of its type). Empty price: the item\'s list price.',
      fields: [
        { name: 'line_type', label: 'Type', required: true },
        { name: 'product_id', label: 'Item / Part No. or Charge Code (search)' },
        { name: 'item_code', label: 'Item Code', readonly: true },
        { name: 'description', label: 'Description', required: true },
        { name: 'serial_ref', label: 'Serial / IMEI' },
        { name: 'quantity', label: 'Qty', required: true },
        { name: 'uom_id', label: 'Unit' },
        { name: 'unit_price', label: 'Unit Price', required: true },
        { name: 'discount_pct', label: 'Disc %' },
        { name: 'discount_amount', label: 'Discount', readonly: true },
        { name: 'subtotal', label: 'Amount excl. VAT', readonly: true }
      ]
    }
  },
  // P2 (12-13 Nov 2026): the billing plan, the advance and what acceptance created.
  'M36-billing-quotes': { kind: 'model_list', model: 'fix.quotation', create: false, stateField: 'state',
    cols: ['name', 'customer_id', 'segment', 'quote_type', 'amount_total', 'advance_amount', 'advance_received', 'advance_outstanding', 'state'],
    actions: [
      { m: 'action_record_advance', l: 'Record Advance Received (amount and method on the form)', states: ['sent', 'accepted'] }
    ] },
  'M36-billing-lines': { kind: 'model_list', model: 'fix.quotation.billing.line', create: false, stateField: 'state',
    cols: ['quotation_id', 'sequence', 'kind', 'pct', 'amount', 'note', 'state', 'invoice_id'],
    actions: [
      { m: 'action_invoice', l: 'Draft the Invoice for this Share', states: ['planned'] }
    ] },
  'M36-templates': { kind: 'model_list', model: 'fix.quotation.template',
    cols: ['sequence', 'name', 'segment', 'quote_type', 'payment_term_id', 'advance_pct', 'validity_days'] },
  'M36-form-template': {
    lines: {
      field: 'line_ids',
      tab: 'lines',
      title: 'Template Lines',
      note: 'Lines a quotation starts with. Empty unit price: priced from the M11 rate card / catalogue when applied. Lines sharing an option group are alternatives (good / better / best).',
      fields: [
        { name: 'sequence', label: 'Seq' },
        { name: 'display_type', label: 'Section / Note' },
        { name: 'line_type', label: 'Type' },
        { name: 'product_id', label: 'Item / Service' },
        { name: 'description', label: 'Description', required: true },
        { name: 'quantity', label: 'Qty' },
        { name: 'unit_price', label: 'Unit Price' },
        { name: 'discount_pct', label: 'Disc %' },
        { name: 'is_optional', label: 'Optional' },
        { name: 'alternative_group', label: 'Option Group' },
        { name: 'is_selected', label: 'Chosen' }
      ]
    },
    kind: 'model_form', model: 'fix.quotation.template',
    title: 'Quotation Template', back: 'M36-templates',
    tabs: [
      { id: 'template', label: '1. Template & Terms', bn: '১. টেমপ্লেট ও শর্ত', icon: '📋', badge: '12' },
      { id: 'lines', label: '2. Lines', bn: '২. লাইন', icon: '🧾', badge: '11' }
    ],
    sections: [
      { tab: 'template', title: 'Template', fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'segment', label: 'Customer Segment' },
        { name: 'quote_type', label: 'Converts Into' },
        { name: 'validity_days', label: 'Valid For (days)' },
        { name: 'payment_term_id', label: 'Payment Terms' },
        { name: 'payment_method_ids', label: 'Payment Methods' },
        { name: 'advance_pct', label: 'Advance Required (%)' },
        { name: 'expected_vds_rate', label: 'Expected VDS (%)' },
        { name: 'picking_type_id', label: 'Deliver From' },
        { name: 'delivery_terms', label: 'Delivery Terms', type: 'text' },
        { name: 'warranty_terms', label: 'Warranty Terms', type: 'text' },
        { name: 'note', label: 'When to Use' }
      ] }
    ]
  },
  // A04 ERP audit M36-F10: what a contract quotation proposes the customer may
  // draw; copied onto the M08 contract when the quotation converts.
  'M36-proposed-entitlements': { kind: 'model_list', model: 'fix.quotation.entitlement',
    cols: ['quotation_id', 'entitlement_type', 'quantity_included', 'device_id'] },
  'M36-form-proposed-entitlement': { kind: 'model_form', model: 'fix.quotation.entitlement',
    title: 'Proposed Contract Entitlement', back: 'M36-proposed-entitlements',
    tabs: [
      { id: 'general', label: '1. Entitlement', bn: '১. এনটাইটেলমেন্ট' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি' }
    ],
    sections: [
      { tab: 'general', title: '1. What the Contract Will Include', note: 'Editable while the quotation is a draft or approved. State the quantity: 0 is unlimited and must be entered on purpose.', fields: [
        { name: 'quotation_id', label: 'Quotation (contract)', required: true, domain: [['quote_type', '=', 'contract'], ['state', 'in', ['draft', 'approved']]] },
        { name: 'entitlement_type', label: 'Entitlement Type', required: true },
        { name: 'quantity_included', label: 'Included (0 = unlimited)', required: true },
        { name: 'device_id', label: 'Specific Asset (empty = all covered assets)' }
      ] },
      { tab: 'docs', title: '2. Documents', fields: [] }
    ] },
  'M36-contract-scope': { kind: 'model_list', model: 'fix.contract.scope.line', create: false,
    cols: ['contract_id', 'line_type', 'description', 'device_id', 'site_id', 'quantity', 'unit_price', 'subtotal'] },
  'M36-handoffs': { kind: 'model_list', model: 'fix.quotation.handoff', create: false,
    cols: ['quotation_id', 'kind', 'ref', 'state', 'note', 'create_date'] },
  'M36-billing': {
    lines: {
      field: 'billing_line_ids',
      tab: 'plan',
      title: 'Billing Plan (shares total 100%)',
      note: 'How the quoted value is invoiced: milestones, on delivery, on completion, recurring (contract / subscription billing), retention. Left empty, Submit fills the default plan. The advance is not an invoice: it is a receipt applied to these invoices.',
      fields: [
        { name: 'sequence', label: 'Seq' },
        { name: 'kind', label: 'When', required: true },
        { name: 'pct', label: 'Share %', required: true },
        { name: 'amount', label: 'Amount excl. VAT', readonly: true },
        { name: 'due_days', label: 'Due (days)' },
        { name: 'note', label: 'Trigger / Milestone' },
        { name: 'state', label: 'State', readonly: true }
      ]
    },
    kind: 'model_form', model: 'fix.quotation',
    title: 'Billing Plan & Advance', back: 'M36-billing-quotes',
    status: { field: 'state' },
    tabs: [
      { id: 'advance', label: '1. Advance', bn: '১. অগ্রিম', icon: '💳', badge: '9' },
      { id: 'plan', label: '2. Billing Plan', bn: '২. বিলিং পরিকল্পনা', icon: '🧾', badge: '7' }
    ],
    sections: [
      { tab: 'advance', title: 'Advance', note: 'Record what the customer paid in advance; Finance confirms the receipt, and it is applied to this quotation\'s invoices as they are issued.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT (BDT)', readonly: true },
          { name: 'advance_pct', label: 'Advance Required (%)', readonly: true },
          { name: 'advance_amount', label: 'Advance Required (BDT)', readonly: true },
          { name: 'advance_received', label: 'Advance Received (BDT)', readonly: true },
          { name: 'advance_outstanding', label: 'Advance Outstanding (BDT)', readonly: true },
          { name: 'advance_entry_amount', label: 'Advance Amount Received Now (BDT)' },
          { name: 'advance_entry_method_id', label: 'Received By' },
          { name: 'advance_entry_ref', label: 'Payment Reference (TrxID / cheque no.)' }
        ] }
    ]
  },
  'M36-form-estimate': {

    lines: {

      field: 'line_ids',

      title: 'Estimate Lines',

      note: 'Parts from inventory (by part number) and service, labour, support, transport or other charges (by charge code); the diagnostic fee is excluded from contract delivery cost.',

      fields: [

        { name: 'line_type', label: 'Type', required: true },

        { name: 'product_id', label: 'Item / Part No. (search)' },
        { name: 'item_code', label: 'Item Code', readonly: true },
        { name: 'description', label: 'Description', required: true },
        { name: 'serial_ref', label: 'Serial / IMEI' },
        { name: 'quantity', label: 'Qty', required: true },
        { name: 'uom_id', label: 'Unit' },
        { name: 'unit_price', label: 'Unit Price', required: true },

        { name: 'line_total', label: 'Total', readonly: true }

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
        { name: 'version', label: 'Version (set by Revise)', readonly: true },
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
    // Quote-to-cash P1 (12 Nov 2026): WHAT is quoted. The value is the sum of
    // these lines less the overall discount; nobody types it.
    lines: {
      field: 'line_ids',
      tab: 'scope',
      title: 'Quoted Lines (what the customer is buying)',
      note: 'Parts, goods, labour, services, AMC and fees. Leave the price empty to take the M11 rate card or catalogue price; a lower price is a discount the approval tier covers. Optional lines are offered but not in the total. A service quotation pulls its lines from the M01 estimate.',
      fields: [
        { name: 'sequence', label: 'Seq' },
        { name: 'display_type', label: 'Section / Note' },
        { name: 'line_type', label: 'Type' },
        { name: 'product_id', label: 'Item / Part No. or Charge Code (search)' },
        { name: 'item_code', label: 'Item Code', readonly: true },
        { name: 'description', label: 'Description', required: true },
        { name: 'serial_ref', label: 'Serial / IMEI' },
        { name: 'quantity', label: 'Qty' },
        { name: 'uom_id', label: 'Unit' },
        { name: 'unit_price', label: 'Unit Price' },
        { name: 'discount_pct', label: 'Disc %' },
        { name: 'discount_amount', label: 'Discount', readonly: true },
        { name: 'subtotal', label: 'Amount excl. VAT', readonly: true },
        { name: 'list_price', label: 'List / Rate', readonly: true },
        { name: 'cost_unit', label: 'Unit Cost' },
        { name: 'is_optional', label: 'Optional' },
        { name: 'alternative_group', label: 'Option Group' },
        { name: 'is_selected', label: 'Chosen' },
        { name: 'fulfilment', label: 'Fulfilled By' },
        { name: 'device_id', label: 'Device' },
        { name: 'site_id', label: 'Site' }
      ]
    },
    kind: 'model_form',
    model: 'fix.quotation',
    title: 'Commercial Proposal & Tender Quotation',
    back: 'M36-quotes',
    status: { field: 'state' },
    tabs: [
      { id: 'header', label: '1. Proposal Header', bn: '১. প্রস্তাবনা পরিচিতি', icon: '📄', badge: '9' },
      { id: 'scope', label: '2. Scope & Pricing', bn: '২. পরিধি ও মূল্য', icon: '🧾', badge: '4' },
      { id: 'terms', label: '3. Commercial Terms', bn: '৩. বাণিজ্যিক শর্ত', icon: '🤝', badge: '8' },
      { id: 'pricing', label: '4. Cost, Margins & SRT', bn: '৪. খরচ ও মার্জিন', icon: '💵', badge: '8' },
      { id: 'statutory', label: '5. Withholding Tax (TDS)', bn: '৫. উৎসে কর কর্তন', icon: '⚖️', badge: '4' },
      { id: 'approval', label: '6. Internal Approval', bn: '৬. অভ্যন্তরীণ অনুমোদন', icon: '✅', badge: '5' },
      { id: 'esign', label: '7. Customer Acceptance', bn: '৭. গ্রাহক সম্মতি', icon: '✍️', badge: '11' },
      { id: 'handoff', label: '8. Contract & Order Hand-off', bn: '৮. চুক্তি ও অর্ডার', icon: '🔗', badge: '6' },
      { id: 'vault', label: '9. Document Vault', bn: '৯. নথিপত্র', icon: '📁', badge: '0' }
    ],
    sections: [
      { tab: 'header', title: 'Proposal Identity & Version Tracking',
        note: 'Number, version and status are set by the lifecycle (Submit, Issue, Revise); an issued version never changes.',
        fields: [
          { name: 'name', label: 'Quotation Reference (auto)', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'segment', label: 'Customer Segment' },
          { name: 'template_id', label: 'Start From Template (then Apply Template)' },
          { name: 'document_lang', label: 'Document Language' },
          { name: 'estimate_id', label: 'Originating Technical Estimate (M01)' },
          { name: 'quote_type', required: true, label: 'Converts Into' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'version', label: 'Quotation Version', readonly: true },
          { name: 'parent_version_id', label: 'Previous Version', readonly: true },
          { name: 'valid_until', label: 'Validity Expiration Date' },
          { name: 'state', label: 'Lifecycle Status', readonly: true }
        ] },
      { tab: 'scope', title: 'Totals from the Lines',
        note: 'The quotation value is the lines total less the overall discount. Discount off list is measured against the rate card / catalogue prices.',
        fields: [
          { name: 'lines_total', label: 'Lines Total excl. VAT (BDT)', readonly: true },
          { name: 'discount_amount', label: 'Overall Discount (BDT)' },
          { name: 'list_total', label: 'At List / Rate Prices (BDT)', readonly: true },
          { name: 'discount_pct', label: 'Discount off List (%)', readonly: true }
        ] },
      { tab: 'terms', title: 'Payment, Delivery & Warranty Terms',
        note: 'What the customer agrees to by accepting: how and when they pay, the advance, delivery and warranty. A change after approval sends the quotation back for approval.',
        fields: [
          { name: 'payment_term_id', label: 'Payment Terms' },
          { name: 'payment_method_ids', label: 'Payment Methods Accepted' },
          { name: 'advance_pct', label: 'Advance Required (%)' },
          { name: 'advance_amount', label: 'Advance Required (BDT)', readonly: true },
          { name: 'delivery_terms', label: 'Delivery / Completion Terms', type: 'text' },
          { name: 'warranty_terms', label: 'Warranty Terms', type: 'text' },
          { name: 'customer_po_ref', label: 'Customer PO No.' },
          { name: 'customer_po_date', label: 'Customer PO Date' },
          { name: 'picking_type_id', label: 'Deliver Goods From' }
        ] },
      { tab: 'pricing', title: 'Direct Cost, Pre-Tax Margin & Value',
        note: 'The value is the lines total less the overall discount (from an estimate: its total before VAT); VAT is added once, giving the Total Payable. Without a direct cost the margin is unknown.',
        fields: [
          { name: 'value', readonly: true, label: 'Quotation Amount excl. VAT (BDT)' },
          { name: 'cost_amount', label: 'Direct Labor & Parts Cost (BDT)' },
          { name: 'margin_known', label: 'Margin Known (cost recorded)', readonly: true },
          { name: 'pretax_margin_bdt', label: 'Pre-Tax Operational Margin (BDT)', readonly: true },
          { name: 'margin_pct', label: 'Gross Margin (%)', readonly: true },
          { name: 'vat_rate', label: 'VAT Rate (%) - M51 on the lines', readonly: true },
          { name: 'vat_amount', label: 'Mushak VAT Amount (BDT)', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT (BDT)', readonly: true }
        ] },
      { tab: 'statutory', title: 'Statutory Withholding Tax & Net Cash Margin',
        note: 'Statutory TDS deductions under Income Tax Act 2023 s.89/90 for supply of service/goods.',
        fields: [
          { name: 'tds_rate', label: 'Withholding Tax TDS Rate (%)' },
          { name: 'tds_amount', label: 'TDS Deduction (BDT)', readonly: true },
          { name: 'net_cash_margin_bdt', label: 'Net Cash Margin After-Tax (BDT)', readonly: true },
          { name: 'net_cash_margin_pct', label: 'Net Cash Margin (%)', readonly: true },
          { name: 'expected_vds_rate', label: 'Expected VDS by Customer (%)' },
          { name: 'expected_vds_amount', label: 'Expected VDS (BDT)', readonly: true },
          { name: 'expected_net_receipt', label: 'Expected Cash Receipt (BDT)', readonly: true }
        ] },
      { tab: 'approval', title: 'Value-Band Approval (BRU-QTE-06/07/09)',
        note: 'Submit routes the quotation to a holder of its value band who is not its author; any change after approval sends it back for re-approval.',
        fields: [
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'dofa_tier_required', label: 'Approval Band', readonly: true },
          { name: 'dofa_justification', label: 'Business Justification', type: 'text' },
          { name: 'dofa_approved_by', label: 'Approved By', readonly: true },
          { name: 'approved_at', label: 'Approved At', readonly: true },
          { name: 'credit_block_reason', label: 'Credit Gate (M20; Finance override on Approval Routing)', readonly: true },
          { name: 'renewal_of_contract_id', label: 'Renewal Of Contract', readonly: true },
          { name: 'version_diff', label: 'What Changed from the Previous Version', type: 'text', readonly: true },
          { name: 'estate_breakdown', label: 'Breakdown by Site / Department / Cost Centre', type: 'text', readonly: true }
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
          { name: 'accepted_total', label: 'Accepted Total incl. VAT (BDT)', readonly: true },
          { name: 'evidence_hash', label: 'Evidence Hash (SHA-256)', readonly: true },
          { name: 'legal_hold', label: 'On Legal Hold (BRU-QTE-17)', readonly: true },
          { name: 'decline_reason_code', label: 'Decline Reason (governed list)' },
          { name: 'decline_reason', label: 'Customer Decline Rationale', readonly: true }
        ] },
      { tab: 'handoff', title: 'What the Accepted Quotation Becomes',
        note: 'On acceptance a service quotation releases its M01 order; a contract quotation creates an M08 draft contract.',
        fields: [
          { name: 'contract_family', label: 'Contract Family' },
          { name: 'contract_months', label: 'Contract Term (months)' },
          { name: 'contract_start', label: 'Contract Start' },
          { name: 'contract_sla_policy_ids', label: 'Proposed Service Levels (contract)' },
          { name: 'service_order_id', label: 'Service Order', readonly: true },
          { name: 'converted_ref', label: 'Converted Into', readonly: true },
          { name: 'converted_at', label: 'Converted At', readonly: true }
        ] },
      { tab: 'vault', title: 'Commercial Proposal Vault',
        note: 'Detailed bill of quantities, tender compliance sheets, and signed purchase orders.',
        fields: [] }
    ]
  },

  /* ---- capture audit 2026-11-14: the quotation steps, one pick form each ---- */
  'M36-form-revise': {
    kind: 'model_form', model: 'fix.quotation',
    title: 'Revise a Quotation', newLabel: 'Revise a Quotation (new version)', back: 'M36-versions',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the issued, expired or declined quotation',
      search: 'Search quotation', choose: 'Revise this version',
      cols: ['name', 'version', 'customer_id', 'value', 'valid_until', 'state'],
      domain: [['state', 'in', ['sent', 'expired', 'declined']]],
      empty: 'No issued, expired or declined quotation. A draft is edited directly on Customer Quotations.'
    },
    saveAction: { method: 'action_revise', label: 'Make the Next Version', done: 'Next version made as a draft: edit, submit and issue it from Customer Quotations' },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: The Version Being Replaced',
        note: 'BRU-QTE-02/04: an issued version is immutable and an expired one is never extended. The next version starts as a draft at current prices, with this one as its previous version; an issued version is marked superseded.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'value', label: 'Value (excl. VAT)', readonly: true },
          { name: 'valid_until', label: 'Valid Until', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-submit': {
    kind: 'model_form', model: 'fix.quotation',
    title: 'Submit for Internal Approval', newLabel: 'Submit a Quotation for Approval', back: 'M36-pending',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the draft quotation',
      search: 'Search quotation', choose: 'Submit this quotation',
      cols: ['name', 'version', 'customer_id', 'value', 'dofa_tier_required', 'approval_state'],
      domain: [['state', '=', 'draft'], ['approval_state', 'in', ['none', 'rejected', 'returned']]],
      empty: 'No draft quotation waits for submission.'
    },
    saveAction: { method: 'action_submit', label: 'Submit for Approval', done: 'Submitted: routed by value to an approver other than the author (M63 inbox)', kwargs: { justification: 'dofa_justification' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: Business Justification',
        note: 'BRU-QTE-06/07/09: routed by value band to someone other than the author; above BDT 25,000 a Branch Manager, above BDT 100,000 the Operations Director. Every line must be priced and the direct cost recorded.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'value', label: 'Value (excl. VAT)', readonly: true },
          { name: 'margin_pct', label: 'Margin %', readonly: true },
          { name: 'dofa_tier_required', label: 'Approval Tier Needed', readonly: true },
          { name: 'dofa_justification', label: 'Business Justification (required above BDT 25,000)', type: 'text', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-issue': {
    kind: 'model_form', model: 'fix.quotation',
    title: 'Issue to the Customer', newLabel: 'Issue a Quotation to the Customer', back: 'M36-loop',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the internally approved quotation',
      search: 'Search quotation', choose: 'Issue this quotation',
      cols: ['name', 'version', 'customer_id', 'amount_total', 'valid_until', 'approval_state'],
      domain: [['state', '=', 'approved']],
      empty: 'No approved quotation waits to be issued.'
    },
    saveAction: { method: 'action_issue_on_channel', label: 'Issue', done: 'Issued: the delivery is recorded and the validity clock runs', kwargs: { channel: 'issue_channel', recipient: 'issue_recipient', delivery_ref: 'issue_ref' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: Channel',
        note: 'FR-QTE-033: the channel the customer receives it on. The terms issued are exactly the terms approved; past its validity date it cannot be issued (revise it).',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT', readonly: true },
          { name: 'valid_until', label: 'Valid Until', readonly: true },
          { name: 'issue_channel', label: 'Deliver By', required: true, readonly: true },
          { name: 'issue_recipient', label: 'Delivered To (empty: the customer\'s mobile or email)', readonly: true },
          { name: 'issue_ref', label: 'Message / Delivery Ref', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-delivery': {
    kind: 'model_form', model: 'fix.quotation.delivery',
    title: 'Quotation Delivery', newLabel: 'Record a Delivery / Re-send', back: 'M36-deliveries',
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Delivery',
        note: 'FR-QTE-039: a re-send, a delivery receipt or the customer opening it. What was sent, when, how and to whom is fixed once saved; delivery, first view and views are updated as they happen.',
        fields: [
          { name: 'quotation_id', label: 'Quotation (with the customer)', required: true, domain: [['state', '=', 'sent']] },
          { name: 'channel', label: 'Channel', required: true },
          { name: 'recipient', label: 'Sent To (empty: the customer\'s mobile or email)' },
          { name: 'delivery_ref', label: 'Message / Delivery Ref' },
          { name: 'sent_at', label: 'Sent At', required: true },
          { name: 'delivered_at', label: 'Delivered At' },
          { name: 'first_viewed_at', label: 'First Viewed At' },
          { name: 'view_count', label: 'Views' },
          { name: 'note', label: 'Note' },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'recorded_by_id', label: 'Recorded By', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-otp': {
    kind: 'model_form', model: 'fix.quotation',
    title: 'Accept by Customer Code', newLabel: 'Accept by Customer Code', back: 'M36-loop',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the quotation the customer is accepting',
      search: 'Search quotation', choose: 'Enter the customer\'s code',
      cols: ['name', 'version', 'customer_id', 'amount_total', 'valid_until', 'delivery_channel'],
      domain: [['state', '=', 'sent']],
      empty: 'No quotation is with a customer.'
    },
    saveAction: { method: 'action_verify_acceptance_otp', label: 'Verify and Accept', done: 'Accepted: the evidence pack is sealed and the hand-off has run', kwargs: { otp: 'acceptance_code_entry' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: The Code the Customer Reads Out',
        note: 'FR-QTE-037/042: first press Send Acceptance Code on Customer Approval Loop; the customer reads the code back (in person or on a recorded call). A wrong code is counted; too many burn it.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT', readonly: true },
          { name: 'valid_until', label: 'Valid Until', readonly: true },
          { name: 'acceptance_code_entry', label: 'Code the Customer Read Out', required: true, readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-signed': {
    kind: 'model_form', model: 'fix.quotation',
    title: 'Record Signed Acceptance', newLabel: 'Record a Signed Acceptance', back: 'M36-loop',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the quotation the customer signed',
      search: 'Search quotation', choose: 'Record its signed copy',
      cols: ['name', 'version', 'customer_id', 'amount_total', 'valid_until', 'esign_state'],
      domain: [['state', '=', 'sent']],
      empty: 'No quotation is with a customer.'
    },
    saveAction: { method: 'action_record_signed_acceptance', label: 'Record Acceptance', done: 'Accepted on the signed copy: the evidence pack is sealed', kwargs: { attachment_id: 'signed_attachment_id' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: The Customer\'s Signed Quotation',
        note: 'FR-QTE-037/038: upload the signed copy (PDF or photo). It is recorded by someone other than the author, within validity, against the exact version approved; its checksum goes into the evidence hash. A provider e-signature arrives on its own signed callback.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT', readonly: true },
          { name: 'valid_until', label: 'Valid Until', readonly: true },
          { name: 'signed_attachment_id', label: 'Signed Quotation (scan or photo)', required: true, readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-decline': {
    kind: 'model_form', model: 'fix.quotation',
    title: 'Record a Customer Decline', newLabel: 'Record a Customer Decline', back: 'M36-loop',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the quotation the customer declined',
      search: 'Search quotation', choose: 'Record the decline',
      cols: ['name', 'version', 'customer_id', 'amount_total', 'valid_until', 'estimate_id'],
      domain: [['state', '=', 'sent']],
      empty: 'No quotation is with a customer.'
    },
    saveAction: { method: 'action_decline', label: 'Record Decline', done: 'Declined: the reason is recorded; a repair order gets its return / collection task', kwargs: { code: 'decline_reason_code', reason: 'decline_reason' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: Why the Customer Declined',
        note: 'BRU-QTE-16: a reason from the governed list. BRU-QTE-12: a declined repair gives the service order a task to return or collect the device, with the diagnostic fee owed.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT', readonly: true },
          { name: 'estimate_id', label: 'Repair Estimate (M01)', readonly: true },
          { name: 'decline_reason_code', label: 'Decline Reason (governed)', required: true, readonly: true },
          { name: 'decline_reason', label: 'What the Customer Said', required: true, readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-counter-offer': {
    lines: {
      field: 'line_ids',
      tab: 'lines',
      title: 'Line Decisions (partial acceptance)',
      fixedRows: true,
      note: 'Filled with the quotation\'s priced lines when a partial acceptance is saved: mark the lines the customer declined. A counter-offer on price has no lines.',
      fields: [
        { name: 'quotation_line_id', label: 'Quoted Line', readonly: true },
        { name: 'quantity', label: 'Qty', readonly: true },
        { name: 'subtotal', label: 'Amount excl. VAT', readonly: true },
        { name: 'decision', label: 'Customer\'s Decision' }
      ]
    },
    kind: 'model_form', model: 'fix.quotation.counter',
    title: 'Counter-Offer / Partial Acceptance', newLabel: 'Record a Counter-Offer / Partial Acceptance', back: 'M36-counters',
    status: { field: 'state' },
    tabs: [
      { id: 'request', label: '1. Customer\'s Request', bn: '১. গ্রাহকের অনুরোধ', icon: '💬', badge: '7' },
      { id: 'lines', label: '2. Line Decisions', bn: '২. লাইনভিত্তিক সিদ্ধান্ত', icon: '🧾', badge: '4' },
      { id: 'decision', label: '3. Decision', bn: '৩. সিদ্ধান্ত', icon: '✅', badge: '6' }
    ],
    sections: [
      { tab: 'request', title: 'What the Customer Asked For',
        note: 'FR-QTE-036: written down as a structured request, not left in a phone call. It is decided by someone other than the person who took it down. For a quotation built from an M01 repair estimate, the change goes to the estimate (Customer Counter on Internal Estimates).',
        fields: [
          { name: 'quotation_id', label: 'Quotation (with the customer)', required: true, domain: [['state', '=', 'sent'], ['estimate_id', '=', false]] },
          { name: 'kind', label: 'Kind', required: true },
          { name: 'channel', label: 'Received By', required: true },
          { name: 'customer_request', label: 'What the Customer Asked For', type: 'text', required: true },
          { name: 'requested_value', label: 'Customer\'s Proposed Price (excl. VAT, optional)' },
          { name: 'evidence_ref', label: 'Evidence (call recording / message ref)' },
          { name: 'quoted_value', label: 'Quoted Value (excl. VAT)', readonly: true }
        ] },
      { tab: 'decision', title: 'Decision',
        note: 'Revise makes the next draft version on these terms (declined lines removed, the proposed price as an overall discount); it then takes the value-band approval and is issued and accepted like any version.',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'accepted_value', label: 'Accepted Lines (excl. VAT)', readonly: true },
          { name: 'recorded_by_id', label: 'Taken Down By', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decision_note', label: 'Decision Note', readonly: true },
          { name: 'revised_quotation_id', label: 'Revised Version', readonly: true }
        ] }
    ]
  },
  'M36-form-counter-decide': {
    kind: 'model_form', model: 'fix.quotation.counter',
    title: 'Decide a Counter-Offer', newLabel: 'Decide a Counter-Offer', back: 'M36-counters',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the counter-offer awaiting its decision',
      search: 'Search counter-offer', choose: 'Decide this counter-offer',
      cols: ['name', 'customer_id', 'kind', 'quoted_value', 'requested_value', 'recorded_by_id'],
      domain: [['state', '=', 'requested']],
      empty: 'No counter-offer awaits a decision.'
    },
    saveAction: { method: 'action_decide', label: 'Record Decision', done: 'Decided: a revision is a new draft version on Customer Quotations', kwargs: { decision: 'decision_choice', note: 'decision_note' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: The Decision',
        note: 'Not by the person who took the counter down. Revise: the next version is drafted on the customer\'s terms and goes through internal approval. Reject: the quotation stands as issued; say why.',
        fields: [
          { name: 'name', label: 'Counter-Offer', readonly: true },
          { name: 'customer_request', label: 'What the Customer Asked For', readonly: true },
          { name: 'quoted_value', label: 'Quoted Value (excl. VAT)', readonly: true },
          { name: 'requested_value', label: 'Customer\'s Proposed Price', readonly: true },
          { name: 'accepted_value', label: 'Accepted Lines (excl. VAT)', readonly: true },
          { name: 'decision_choice', label: 'Decision', required: true, readonly: true },
          { name: 'decision_note', label: 'Decision Note (required to reject)', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M36-form-tender': {
    lines: {
      field: 'requirement_ids',
      tab: 'bond_compliance',
      title: 'Compliance Matrix',
      note: 'Every mandatory requirement must be complied with (against its evidence document) or not applicable before the bid is submitted (BRU-QTE-15). Frozen once submitted.',
      fields: [
        { name: 'clause_ref', label: 'Clause' },
        { name: 'requirement', label: 'Requirement', required: true },
        { name: 'mandatory', label: 'Mandatory' },
        { name: 'state', label: 'Status', required: true },
        { name: 'evidence_ref', label: 'Evidence Document Ref' },
        { name: 'owner_id', label: 'Owner' },
        { name: 'response', label: 'Response' }
      ]
    },
    kind: 'model_form',
    model: 'fix.tender',
    title: 'Public / Institutional Tender Bid',
    back: 'M36-tenders',
    status: { field: 'state' },
    tabs: [
      { id: 'tender_header', label: '1. Tender Bid Info', bn: '১. দরপত্রের তথ্য', icon: '📑', badge: '15' },
      { id: 'decision', label: '2. Bid / No-Bid', bn: '২. বিড সিদ্ধান্ত', icon: '⚖️', badge: '9' },
      { id: 'bond_compliance', label: '3. Bond & Compliance', bn: '৩. বন্ড ও সম্মতি', icon: '🛡️', badge: '5' },
      { id: 'contract_terms', label: '4. Contract Terms (PPR 2025)', bn: '৪. চুক্তির শর্ত', icon: '📜', badge: '5' },
      { id: 'status', label: '5. Tender Outcome', bn: '৫. দরপত্রের ফলাফল', icon: '🏁', badge: '14' },
      { id: 'noa', label: '6. NoA Deadlines', bn: '৬. NoA সময়সীমা', icon: '⏱️', badge: '3' },
      { id: 'acceptance', label: '7. Acceptance & Retention', bn: '৭. গ্রহণ ও রিটেনশন', icon: '✅', badge: '6' }
    ],
    sections: [
      { tab: 'tender_header', title: 'Tender Identification', note: 'Public Procurement Act 2006 / PPR 2025 tender bid details. The bid price comes from the pricing quotation of the BOQ (Tender BOQ / Price Schedule) once it is priced. Frozen once the bid is submitted.',
        fields: [
          { name: 'name', required: true, label: 'Tender Name' },
          { name: 'tender_type', required: true, label: 'Tender Type' },
          { name: 'reference', label: 'Tender ID / e-GP Ref' },
          { name: 'egp_package_no', label: 'e-GP Package No.' },
          { name: 'client_name', required: true, label: 'Tendering Client' },
          { name: 'procuring_entity', label: 'Procuring Entity (office)' },
          { name: 'client_id', label: 'Procuring Entity (contract party)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'due_date', required: true, label: 'Submission Deadline' },
          { name: 'estimated_value', label: 'Official Estimated Cost' },
          { name: 'boq_total', label: 'BOQ Total incl. VAT', readonly: true },
          { name: 'quotation_id', label: 'Pricing Quotation', readonly: true },
          { name: 'quotation_state', label: 'Quotation State', readonly: true },
          { name: 'bid_value', label: 'Bid Price Lodged (incl. VAT)' },
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
      { tab: 'bond_compliance', title: 'Bank Guarantee & Technical Compliance', note: 'The tender security is a fixed amount of at most 3% of the official estimated cost and must cover the tender validity plus 28 days (PPR 2025). A public tender is valid 60-150 days.',
        fields: [
          { name: 'bonds_required', label: 'Bid Security Required' },
          { name: 'bid_security_amount', label: 'Bid Security Required (BDT)' },
          { name: 'bid_validity_days', label: 'Tender Validity (days)' },
          { name: 'compliance_pct', label: 'Compliance % (computed)', readonly: true },
          { name: 'open_mandatory_count', label: 'Open Mandatory Items', readonly: true },
          { name: 'missing_document_count', label: 'Required Documents Missing', readonly: true },
          { name: 'submission_pack_hash', label: 'Submission Pack Hash (sealed at submission)', readonly: true }
        ] },
      { tab: 'status', title: 'Award & Contract', note: 'Stage the award letter and value, then Request Award: a Tender Committee member who did not prepare the bid approves it, and the M08 contract is created.',
        fields: [
          { name: 'award_ref', label: 'Notification of Award Ref' },
          { name: 'awarded_value', label: 'Awarded Value' },
          { name: 'award_variation_pct', label: 'Award vs Bid (%)', readonly: true },
          { name: 'contract_value', label: 'Contract Value (with variations)', readonly: true },
          { name: 'contract_family', label: 'Contract Family' },
          { name: 'contract_months', label: 'Contract Term (months)' },
          { name: 'noa_date', label: 'NoA Date' },
          { name: 'approval_state', label: 'Award Approval', readonly: true },
          { name: 'awarded_by', label: 'Award Approved By', readonly: true },
          { name: 'award_date', label: 'Award Date', readonly: true },
          { name: 'converted_ref', label: 'Contract', readonly: true },
          { name: 'awarded_to', label: 'Awarded To (on a loss)', readonly: true },
          { name: 'winning_value', label: 'Winning Value (on a loss)', readonly: true },
          { name: 'loss_reason_code', label: 'Loss Reason (governed)', readonly: true },
          { name: 'loss_reason', label: 'Loss Reason', readonly: true }
        ] },
      { tab: 'contract_terms', title: 'Contract Terms from the Tender Documents', note: 'PPR 2025 STDs: performance security 10% of the contract price; liquidated damages 0.03-0.05% per day capped at 10%; 10% retention from payments after acceptance. Values outside the usual are flagged, not refused. Frozen once the bid is submitted.',
        fields: [
          { name: 'performance_security_pct', label: 'Performance Security (%)' },
          { name: 'retention_pct', label: 'Retention (%)' },
          { name: 'ld_rate_pct_per_day', label: 'Liquidated Damages (% per day)' },
          { name: 'ld_cap_pct', label: 'LD Cap (%)' },
          { name: 'ppr_warnings', label: 'PPR 2025 Checks', readonly: true, type: 'text' }
        ] },
      { tab: 'noa', title: 'Notification of Award Deadlines', note: 'From the NoA date on the Tender Outcome tab: performance security within 7 working days (Sunday-Thursday week, national holidays skipped); contract signed within 14 days; performance security valid 28 days past completion.',
        fields: [
          { name: 'performance_security_due', label: 'Performance Security Due', readonly: true },
          { name: 'contract_signing_due', label: 'Contract Signing Due', readonly: true },
          { name: 'performance_security_valid_until', label: 'Performance Security Valid Until', readonly: true }
        ] },
      { tab: 'acceptance', title: 'Acceptance Certificate & Retention', note: 'After the award: stage the procuring entity acceptance committee certificate, then Record Acceptance Certificate. Retention runs on the accepted value.',
        fields: [
          { name: 'teac_certificate_no', label: 'Acceptance Certificate No.' },
          { name: 'teac_certificate_date', label: 'Certificate Date' },
          { name: 'teac_accepted_value', label: 'Accepted Value (BDT)' },
          { name: 'retention_amount', label: 'Retention (BDT)', readonly: true },
          { name: 'acceptance_recorded_by', label: 'Recorded By', readonly: true },
          { name: 'acceptance_recorded_at', label: 'Recorded At', readonly: true }
        ] }
    ]
  },

  'M36-form-boq': {
    lines: {
      field: 'boq_line_ids',
      tab: 'schedule',
      title: 'Price Schedule (BPPA e-PG2-3A goods / 3B related services)',
      note: 'Unit and total prices INCLUDE VAT and all levies, as the standard tender documents require. Import replaces these rows from the uploaded sheet; Price as Quotation prices them on a contract quotation at the unit price excluding VAT. Frozen once the bid is submitted.',
      fields: [
        { name: 'sequence', label: 'Seq' },
        { name: 'item_no', label: 'Item No.', required: true },
        { name: 'line_kind', label: 'Type', required: true },
        { name: 'description', label: 'Description', required: true },
        { name: 'product_id', label: 'Our Item / Service' },
        { name: 'country_of_origin', label: 'Country of Origin' },
        { name: 'unit', label: 'Unit' },
        { name: 'quantity', label: 'Qty', required: true },
        { name: 'unit_price_incl_vat', label: 'Unit Price incl. VAT' },
        { name: 'total_price', label: 'Total Price incl. VAT', readonly: true },
        { name: 'point_of_delivery', label: 'Point of Delivery' },
        { name: 'delivery_period_required', label: 'Delivery Required' },
        { name: 'delivery_period_offered', label: 'Delivery Offered' },
        { name: 'quotation_line_id', label: 'Priced On', readonly: true }
      ]
    },
    kind: 'model_form',
    model: 'fix.tender',
    title: 'Tender BOQ / Price Schedule',
    back: 'M36-boq',
    create: false, pick: 'Register the tender on Tenders & Bids, then open it from Tender BOQ / Price Schedule.',
    status: { field: 'state' },
    tabs: [
      { id: 'file', label: '1. Tender & BOQ File', bn: '১. দরপত্র ও BOQ ফাইল', icon: '📑', badge: '5' },
      { id: 'schedule', label: '2. Price Schedule', bn: '২. মূল্য তফসিল', icon: '🧾', badge: '3' },
      { id: 'pricing', label: '3. Pricing Quotation', bn: '৩. মূল্য কোটেশন', icon: '💵', badge: '3' }
    ],
    sections: [
      { tab: 'file', title: 'Tender & Price Schedule File',
        note: 'Upload the procuring entity BOQ (.xlsx or .csv) with a header row naming Item No., Description, Unit, Quantity and Unit Price (Country of Origin, Total Price, Point of Delivery and Delivery Period columns are read when present), save, then run Import BOQ.',
        fields: [
          { name: 'name', label: 'Tender', readonly: true },
          { name: 'reference', label: 'Tender ID / e-GP Ref', readonly: true },
          { name: 'state', label: 'Bid Lifecycle State', readonly: true },
          { name: 'boq_file', type: 'file', label: 'BOQ File (.xlsx / .csv)' },
          { name: 'boq_filename', label: 'BOQ File Name' }
        ] },
      { tab: 'schedule', title: 'Price Schedule Totals',
        fields: [
          { name: 'boq_line_count', label: 'BOQ Items', readonly: true },
          { name: 'boq_unpriced_count', label: 'Unpriced Items', readonly: true },
          { name: 'boq_total', label: 'BOQ Total incl. VAT (BDT)', readonly: true }
        ] },
      { tab: 'pricing', title: 'Internal Price Approval',
        note: 'The bid price is the pricing quotation total payable (incl. VAT). Approve the quotation through its value band (Customer Quotations: Submit for Approval) before submitting the bid; it is never issued to the customer.',
        fields: [
          { name: 'quotation_id', label: 'Pricing Quotation', readonly: true },
          { name: 'quotation_state', label: 'Quotation State', readonly: true },
          { name: 'bid_value', label: 'Bid Price incl. VAT (BDT)', readonly: true }
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
    title: 'Counter Sale (walk-in, M04)', back: 'M36-versions',
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
        { name: 'instrument', label: 'Instrument (guarantee / pay order EMD)', required: true },
        { name: 'margin_amount', label: 'Cash Margin Held by the Bank' },
        { name: 'charges_amount', label: 'Bank Commission' },
        { name: 'funding_move_id', label: 'GL: Funding Entry', readonly: true },
        { name: 'release_move_id', label: 'GL: Release Entry', readonly: true },
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
    ] },

  /* ==== Capture audit, third pass (2026-11-19) ============================ */
  // p2 FR-QTE-021/022: a quotation for a corporate estate from its asset list.
  'M36-form-estate': { kind: 'model_form', model: 'fix.quotation',
    title: 'Bulk Estate Quotation (asset upload)', newLabel: 'Quote a Corporate Estate (asset upload)', back: 'M36-quotes',
    status: { field: 'state' },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'One Priced Line per Asset (FR-QTE-022)',
        note: 'Upload the customer\'s asset list (.xlsx or .csv): Description and Unit Price are required; Asset Tag, Site, Department, Cost Centre and Quantity are read when present. The lines are grouped by site and the quotation shows subtotals by site, department and cost centre (FR-QTE-021). The draft then takes the value-band approval like any quotation.',
        fields: [
          { name: 'customer_id', label: 'Corporate Customer', required: true },
          { name: 'quote_type', label: 'Converts Into', required: true },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'valid_until', label: 'Valid Until', required: true },
          { name: 'cost_amount', label: 'Estimated Direct Cost' },
          { name: 'estate_file', type: 'file', label: 'Asset Upload (.xlsx / .csv)', required: true },
          { name: 'estate_filename', label: 'Upload File Name' },
          { name: 'name', label: 'Quotation No.', readonly: true },
          { name: 'value', label: 'Value (excl. VAT)', readonly: true },
          { name: 'estate_breakdown', label: 'Breakdown by Site / Department / Cost Centre', type: 'text', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },
  // p3 FR-QTE-013: the side-by-side difference with the version replaced.
  'M36-form-compare': { kind: 'model_form', model: 'fix.quotation',
    title: 'Compare with the Previous Version', newLabel: 'Compare Two Versions', back: 'M36-versions',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose a revised quotation (version 2 or later)',
      search: 'Search quotation', choose: 'Compare with its previous version',
      cols: ['name', 'version', 'parent_version_id', 'customer_id', 'value', 'state'],
      domain: [['parent_version_id', '!=', false]],
      empty: 'No quotation has been revised yet.'
    },
    saveAction: { method: 'action_record_version_comparison', label: 'Keep This Comparison on the Quotation', done: 'Comparison recorded on the quotation (its history)', kwargs: {} },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: What Changed, in the Customer\'s Words',
        note: 'Price, discount, validity, every line added, removed or re-priced, and every term added or dropped, compared with the version this one replaced.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'parent_version_id', label: 'Previous Version', readonly: true },
          { name: 'version_diff', label: 'What Changed', type: 'text', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },
  // p5 FR-QTE-034 / T-05: the customer's one-screen approval link.
  'M36-form-approval-link': { kind: 'model_form', model: 'fix.quotation',
    title: 'Send Customer Approval Link', newLabel: 'Send Customer Approval Link', back: 'M36-loop',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the quotation with the customer',
      search: 'Search quotation', choose: 'Send its approval link',
      cols: ['name', 'version', 'customer_id', 'amount_total', 'valid_until', 'delivery_channel'],
      domain: [['state', '=', 'sent']],
      empty: 'No quotation is with a customer.'
    },
    saveAction: { method: 'action_send_approval_link', label: 'Send the Link', done: 'Link recorded as a delivery (Deliveries & Views shows it and when it is opened)', kwargs: { channel: 'approval_link_channel', recipient: 'approval_link_recipient' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: Channel',
        note: 'A one-screen Bengali / English page with the price, lines, VAT and terms, never cost or margin. The customer approves with a code sent to their own phone, within validity. Opening it is recorded as a view. A new link replaces the old one.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT', readonly: true },
          { name: 'valid_until', label: 'Valid Until', readonly: true },
          { name: 'approval_link_channel', label: 'Send By', required: true, readonly: true },
          { name: 'approval_link_recipient', label: 'Send To (empty: the customer\'s mobile or email)', readonly: true },
          { name: 'approval_link_sent_at', label: 'Last Link Sent At', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },

  /* ==== Capture audit, second pass (2026-11-19) ============================ */
  // p1 FR-QTE-009: a technical review / second opinion before an estimate is quoted.
  'M36-est-reviews': { kind: 'model_list', model: 'fix.estimate.review', stateField: 'state',
    cols: ['estimate_id', 'estimate_total', 'reason', 'reviewer_id', 'requested_by_id', 'state', 'decided_at'],
    empty: 'No technical review yet. Ask a senior technician for a second opinion on a high-value or contentious estimate; it cannot be quoted while the review is open or returned.' },
  'M36-form-est-review': { kind: 'model_form', model: 'fix.estimate.review',
    title: 'Technical Review Request', newLabel: 'Request a Technical Review', back: 'M36-est-reviews',
    status: { field: 'state' },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Second Opinion (FR-QTE-009)',
        note: 'A high-value or contentious estimate goes to a senior technician or specialist before it becomes a quotation. Until the reviewer clears it, no quotation of this estimate can be submitted or issued; a return sends it back for rework.',
        fields: [
          { name: 'estimate_id', label: 'Estimate', required: true, domain: [['state', 'in', ['draft', 'sent', 'approved']]] },
          { name: 'estimate_total', label: 'Estimate Total', readonly: true },
          { name: 'reason', label: 'Why a Review', required: true },
          { name: 'question', label: 'What the Reviewer Should Check', type: 'text', required: true },
          { name: 'reviewer_id', label: 'Senior Technician / Specialist (not you)', required: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'findings', label: 'Findings', type: 'text', readonly: true },
          { name: 'decided_at', label: 'Decided At', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },
  'M36-form-est-review-decide': { kind: 'model_form', model: 'fix.estimate.review',
    title: 'Record Technical Review Outcome', newLabel: 'Record Technical Review Outcome', back: 'M36-est-reviews',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the review awaiting your opinion',
      search: 'Search review', choose: 'Record the outcome',
      cols: ['estimate_id', 'estimate_total', 'reason', 'reviewer_id', 'requested_by_id'],
      domain: [['state', '=', 'requested']],
      empty: 'No technical review awaits an outcome.'
    },
    saveAction: { method: 'action_decide', label: 'Record Outcome', done: 'Recorded: a cleared estimate can be quoted; a returned one is reworked', kwargs: { decision: 'decision_choice', findings: 'findings_entry' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: The Reviewer\'s Opinion',
        note: 'Only the named reviewer records the outcome. Cleared: the build-up is sound and the estimate can be quoted. Returned: it is reworked and reviewed again.',
        fields: [
          { name: 'estimate_id', label: 'Estimate', readonly: true },
          { name: 'reason', label: 'Why a Review', readonly: true },
          { name: 'question', label: 'What to Check', type: 'text', readonly: true },
          { name: 'decision_choice', label: 'Outcome', required: true, readonly: true },
          { name: 'findings_entry', label: 'Findings', type: 'text', required: true, readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },

  // p10 / p2 FR-QTE-018: the governed library and the terms on each quotation.
  'M36-std-terms': { kind: 'model_list', model: 'fix.quotation.standard.term',
    cols: ['code', 'name', 'term_type', 'quote_type', 'mandatory', 'active'],
    empty: 'No standard term yet. The Commercial Manager keeps the library of standard terms, assumptions and exclusions; a quotation quoting one word for word needs no approval.' },
  'M36-form-std-term': { kind: 'model_form', model: 'fix.quotation.standard.term',
    title: 'Standard Term (library)', newLabel: 'New Standard Term', back: 'M36-std-terms',
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Standard Term, Assumption or Exclusion (FR-QTE-018)',
        note: 'Kept by the Commercial Manager. Mandatory: every quotation of its kind must carry it before it is submitted. Changing the wording here does not change a term already quoted.',
        fields: [
          { name: 'code', label: 'Code', required: true },
          { name: 'name', label: 'Title', required: true },
          { name: 'term_type', label: 'Kind', required: true },
          { name: 'quote_type', label: 'Applies To (empty: every quotation)' },
          { name: 'text_en', label: 'Wording (English)', type: 'text', required: true },
          { name: 'text_bn', label: 'Wording (Bengali)', type: 'text' },
          { name: 'mandatory', label: 'Mandatory on Every Quotation of Its Kind' },
          { name: 'sequence', label: 'Order' },
          { name: 'active', label: 'In Use' }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },
  'M36-terms': { kind: 'model_list', model: 'fix.quotation.term', stateField: 'deviation_state',
    cols: ['quotation_id', 'customer_id', 'term_type', 'standard_term_id', 'deviation_state', 'commercial_approver_id', 'finance_approver_id', 'quotation_state'],
    empty: 'No quotation term yet. Attach the standard terms to a draft (Attach the Standard Terms on Customer Quotations) or write a term; wording that is not the library\'s goes to the CCO and CFO.' },
  'M36-form-term': { kind: 'model_form', model: 'fix.quotation.term',
    title: 'Quotation Term', newLabel: 'Add a Term / Assumption / Exclusion', back: 'M36-terms',
    status: { field: 'deviation_state' },
    tabs: [
      { id: 'term', label: '1. The Term', bn: '১. শর্ত', icon: '📜', badge: '7' },
      { id: 'approval', label: '2. Deviation Approval', bn: '২. বিচ্যুতি অনুমোদন', icon: '✅', badge: '7' }
    ],
    sections: [
      { tab: 'term', title: 'The Term on the Quotation (FR-QTE-018)',
        note: 'Pick a standard term to quote it word for word (no approval). Any other wording is a deviation: say why, and the Commercial Manager (CCO) and Finance (CFO) approve it before the quotation can be submitted or issued (BRU-QTE-08). Set while the quotation is a draft.',
        fields: [
          { name: 'quotation_id', label: 'Quotation (draft)', required: true, domain: [['state', '=', 'draft']] },
          { name: 'standard_term_id', label: 'Standard Term (empty: own wording)' },
          { name: 'term_type', label: 'Kind', required: true },
          { name: 'text_en', label: 'Wording (English; empty: the standard wording)', type: 'text' },
          { name: 'text_bn', label: 'Wording (Bengali)', type: 'text' },
          { name: 'deviation_reason', label: 'Why the Standard Wording Does Not Fit (required for a deviation)' },
          { name: 'sequence', label: 'Order' }
        ] },
      { tab: 'approval', title: 'CCO + CFO Approval of a Deviation',
        note: 'Given with Decide a Term Deviation (Approval Routing page), by two different people, neither the author.',
        fields: [
          { name: 'deviation_state', label: 'Approval', readonly: true },
          { name: 'recorded_by_id', label: 'Written By', readonly: true },
          { name: 'commercial_approver_id', label: 'Approved (Commercial / CCO)', readonly: true },
          { name: 'commercial_approved_at', label: 'At', readonly: true },
          { name: 'finance_approver_id', label: 'Approved (Finance / CFO)', readonly: true },
          { name: 'finance_approved_at', label: 'At', readonly: true },
          { name: 'rejection_note', label: 'Rejection Note', readonly: true }
        ] }
    ] },
  // p4 FR-QTE-027 / BRU-QTE-08 and FR-QTE-028 / BRU-QTE-14.
  'M36-term-deviations': { kind: 'model_list', model: 'fix.quotation.term', create: false, stateField: 'deviation_state',
    domain: [['deviation_state', '=', 'pending']],
    cols: ['quotation_id', 'customer_id', 'term_type', 'deviation_reason', 'recorded_by_id', 'commercial_approver_id', 'finance_approver_id'],
    empty: 'No non-standard term awaits approval.' },
  'M36-form-term-decide': { kind: 'model_form', model: 'fix.quotation.term',
    title: 'Decide a Term Deviation', newLabel: 'Decide a Term Deviation', back: 'M36-term-deviations',
    status: { field: 'deviation_state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the non-standard term awaiting approval',
      search: 'Search term', choose: 'Decide this deviation',
      cols: ['quotation_id', 'customer_id', 'term_type', 'deviation_reason', 'commercial_approver_id', 'finance_approver_id'],
      domain: [['deviation_state', '=', 'pending']],
      empty: 'No non-standard term awaits approval.'
    },
    saveAction: { method: 'action_decide_deviation', label: 'Record Decision', done: 'Recorded: the deviation is approved once both the CCO and the CFO have approved it', kwargs: { decision: 'decision_choice', note: 'decision_note' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: Your Decision (BRU-QTE-08)',
        note: 'The Commercial Manager signs for the CCO and Finance (Accounting Administrator) for the CFO: two different people, neither the author of the quotation or the term. Either may reject; say why.',
        fields: [
          { name: 'quotation_id', label: 'Quotation', readonly: true },
          { name: 'term_type', label: 'Kind', readonly: true },
          { name: 'text_en', label: 'Wording', type: 'text', readonly: true },
          { name: 'deviation_reason', label: 'Why It Deviates', readonly: true },
          { name: 'commercial_approver_id', label: 'Approved (Commercial / CCO)', readonly: true },
          { name: 'finance_approver_id', label: 'Approved (Finance / CFO)', readonly: true },
          { name: 'decision_choice', label: 'Decision', required: true, readonly: true },
          { name: 'decision_note', label: 'Note (required to reject)', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },
  'M36-credit-overrides': { kind: 'model_list', model: 'fix.quotation.credit.override',
    cols: ['quotation_id', 'version', 'customer_id', 'amount_total', 'block_reason', 'granted_by_id', 'granted_at', 'revoked'],
    empty: 'No credit override. A quotation to a customer on credit hold or over the limit is not issued or accepted until Finance records one (BRU-QTE-14).',
    actions: [
      { m: 'action_revoke', l: 'Revoke the Override' }
    ] },
  'M36-form-credit-override': { kind: 'model_form', model: 'fix.quotation.credit.override',
    title: 'Finance Credit Override', newLabel: 'Record a Credit Override (Finance)', back: 'M36-credit-overrides',
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Finance Lets One Quotation Through (FR-QTE-028, BRU-QTE-14)',
        note: 'Only when M20 reports the customer on credit hold or over the limit with this quotation. Recorded by Finance (Accounting Administrator), never the author, for this version only; a revision needs a new one.',
        fields: [
          { name: 'quotation_id', label: 'Quotation', required: true, domain: [['state', 'in', ['draft', 'approved', 'sent']]] },
          { name: 'reason', label: 'Why Finance Lets It Through', type: 'text', required: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'amount_total', label: 'Quotation Total (incl. VAT)', readonly: true },
          { name: 'block_reason', label: 'What the Gate Found', readonly: true },
          { name: 'granted_by_id', label: 'Granted By', readonly: true },
          { name: 'granted_at', label: 'Granted At', readonly: true },
          { name: 'revoked', label: 'Revoked', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },

  // p2 FR-QTE-024 / BRU-QTE-18: a renewal quotation from an expiring contract.
  'M36-renewals': { kind: 'model_list', model: 'fix.quotation', stateField: 'state',
    domain: [['renewal_of_contract_id', '!=', false]],
    cols: ['name', 'version', 'renewal_of_contract_id', 'customer_id', 'contract_start', 'contract_months', 'value', 'state'],
    empty: 'No renewal quotation yet. Quote the renewal of a contract in force or just ended: its scope is carried over with the contract\'s escalation applied.' },
  'M36-form-renewal': { kind: 'model_form', model: 'fix.quotation',
    title: 'Renewal Quotation', newLabel: 'Quote a Contract Renewal', back: 'M36-renewals',
    status: { field: 'state' },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Renewal of an Expiring Contract (FR-QTE-024)',
        note: 'The customer, operating unit and contract family come from the contract; the scope lines are carried over at the contract\'s escalation and the new term starts the day after it ends. The draft then takes the value-band approval like any quotation: record its direct cost on Customer Quotations.',
        fields: [
          { name: 'renewal_of_contract_id', label: 'Contract Being Renewed', required: true, domain: [['state', 'in', ['active', 'expiring', 'expired']]] },
          { name: 'contract_months', label: 'Renewal Term (months)', required: true },
          { name: 'valid_until', label: 'Quotation Valid Until', required: true },
          { name: 'cost_amount', label: 'Estimated Direct Cost' },
          { name: 'name', label: 'Quotation No.', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'contract_start', label: 'Renewal Starts', readonly: true },
          { name: 'value', label: 'Renewal Value (excl. VAT)', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },

  // p5 / p7 FR-QTE-042: acceptance on a recorded phone call.
  'M36-form-phone': { kind: 'model_form', model: 'fix.quotation',
    title: 'Accept by Phone (recorded consent)', newLabel: 'Accept by Phone (recorded consent)', back: 'M36-loop',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the quotation the customer accepted on the call',
      search: 'Search quotation', choose: 'Record the call',
      cols: ['name', 'version', 'customer_id', 'amount_total', 'valid_until', 'delivery_channel'],
      domain: [['state', '=', 'sent']],
      empty: 'No quotation is with a customer.'
    },
    saveAction: { method: 'action_record_phone_acceptance', label: 'Record Acceptance', done: 'Accepted on the recorded call: the evidence pack is sealed', kwargs: { consent_ref: 'phone_consent_ref', called_number: 'phone_called_number' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: The Recorded Call',
        note: 'FR-QTE-042: the call recording or consent reference is required, the number called must be the customer\'s own, and the agent is not the author. Within validity, against the exact version approved. Prefer Accept by Customer Code when the customer can read a code back.',
        fields: [
          { name: 'name', label: 'Quotation', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'amount_total', label: 'Total Payable incl. VAT', readonly: true },
          { name: 'valid_until', label: 'Valid Until', readonly: true },
          { name: 'phone_called_number', label: 'Number Called', required: true, readonly: true },
          { name: 'phone_consent_ref', label: 'Call Recording / Consent Ref', required: true, readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },

  // p7 BRU-QTE-17 / T-14: a disputed quotation on legal hold.
  'M36-legal-holds': { kind: 'model_list', model: 'fix.quotation.legal.hold', stateField: 'state',
    cols: ['quotation_id', 'version', 'customer_id', 'dispute_ref', 'state', 'placed_by_id', 'placed_at', 'released_by_id'],
    empty: 'No quotation is on legal hold. A quotation under dispute is held so it can never be deleted.' },
  'M36-form-legal-hold': { kind: 'model_form', model: 'fix.quotation.legal.hold',
    title: 'Legal Hold', newLabel: 'Place a Legal Hold', back: 'M36-legal-holds',
    status: { field: 'state' },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Quotation Under Dispute (BRU-QTE-17)',
        note: 'While on hold the quotation and its evidence cannot be deleted or purged. The Commercial Manager releases it, never the person who placed it.',
        fields: [
          { name: 'quotation_id', label: 'Quotation', required: true },
          { name: 'dispute_ref', label: 'Dispute / Case Ref', required: true },
          { name: 'reason', label: 'What Is Disputed', type: 'text', required: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'placed_by_id', label: 'Placed By', readonly: true },
          { name: 'placed_at', label: 'Placed At', readonly: true },
          { name: 'released_by_id', label: 'Released By', readonly: true },
          { name: 'release_reason', label: 'Why Released', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },
  'M36-form-hold-release': { kind: 'model_form', model: 'fix.quotation.legal.hold',
    title: 'Release a Legal Hold', newLabel: 'Release a Legal Hold', back: 'M36-legal-holds',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the hold to release',
      search: 'Search hold', choose: 'Release this hold',
      cols: ['quotation_id', 'customer_id', 'dispute_ref', 'placed_by_id', 'placed_at'],
      domain: [['state', '=', 'active']],
      empty: 'No quotation is on legal hold.'
    },
    saveAction: { method: 'action_release', label: 'Release', done: 'Released: the quotation follows its records schedule again', kwargs: { note: 'release_note' } },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Step 2 of 2: Why the Hold Ends',
        note: 'By the Commercial Manager, never the person who placed it.',
        fields: [
          { name: 'quotation_id', label: 'Quotation', readonly: true },
          { name: 'dispute_ref', label: 'Dispute / Case Ref', readonly: true },
          { name: 'reason', label: 'What Was Disputed', type: 'text', readonly: true },
          { name: 'release_note', label: 'Why It Is Released', required: true, readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },

  // p9 FR-QTE-046 / BRU-QTE-15: the submission pack; FR-QTE-048: the outcome.
  'M36-tender-docs': { kind: 'model_list', model: 'fix.tender.document', stateField: 'state',
    cols: ['tender_id', 'document_type', 'name', 'required', 'state', 'version', 'valid_until', 'prepared_by_id', 'tender_state'],
    empty: 'No document on any submission checklist. List every annexe, certificate and form the tender asks for: a bid cannot be submitted while a required one is missing.' },
  'M36-form-tender-doc': { kind: 'model_form', model: 'fix.tender.document',
    title: 'Tender Document', newLabel: 'Add a Document to the Submission Pack', back: 'M36-tender-docs',
    status: { field: 'state' },
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Submission Checklist Item (FR-QTE-046)',
        note: 'Upload the document itself: each new upload is a new version, and the pack is sealed by its hash when the bid is submitted (BRU-QTE-15). A document must be valid past the submission deadline. Frozen once the bid is submitted.',
        fields: [
          { name: 'tender_id', label: 'Tender (draft)', required: true, domain: [['state', '=', 'draft']] },
          { name: 'document_type', label: 'Document', required: true },
          { name: 'name', label: 'Title / Annexe No.', required: true },
          { name: 'required', label: 'Required by the Tender' },
          { name: 'attachment_id', label: 'The Document (upload)' },
          { name: 'reference', label: 'Issuing Ref / Certificate No.' },
          { name: 'valid_until', label: 'Valid Until' },
          { name: 'sequence', label: 'Order in the Pack' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'prepared_by_id', label: 'Prepared By', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },
  'M36-tender-outcomes': { kind: 'model_list', model: 'fix.tender.outcome',
    cols: ['tender_id', 'client_name', 'result', 'loss_reason_code', 'awarded_to', 'winning_value', 'our_value', 'price_gap_pct', 'recorded_by_id'],
    empty: 'No tender outcome recorded. A submitted bid that was not won is recorded here with its governed loss reason; a win is the Tender Committee\'s award.' },
  'M36-form-tender-outcome': { kind: 'model_form', model: 'fix.tender.outcome',
    title: 'Tender Outcome (loss)', newLabel: 'Record a Tender Outcome (not won)', back: 'M36-tender-outcomes',
    tabs: [
      { id: 'main', label: '1. Details', bn: '১. বিবরণ' },
      { id: 'docs', label: '2. Documents', bn: '২. নথি ও প্রমাণক', icon: '📁' }
    ],
    sections: [
      { tab: 'main', title: 'Outcome and Loss Analysis (FR-QTE-048, BRU-QTE-16)',
        note: 'For a submitted bid that was not won. The reason comes from the governed list; the winner and the winning price, where disclosed, feed the win/loss analysis. A win is recorded by the award decision (Request Award), never here.',
        fields: [
          { name: 'tender_id', label: 'Tender (submitted)', required: true, domain: [['state', '=', 'submitted']] },
          { name: 'result', label: 'Result', required: true },
          { name: 'loss_reason_code', label: 'Loss Reason (governed)', required: true },
          { name: 'awarded_to', label: 'Awarded To' },
          { name: 'winning_value', label: 'Winning Price (where disclosed)' },
          { name: 'notes', label: 'What Was Learned', type: 'text', required: true },
          { name: 'our_value', label: 'Our Bid', readonly: true },
          { name: 'price_gap_pct', label: 'Our Price vs Winner (%)', readonly: true },
          { name: 'recorded_by_id', label: 'Recorded By', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The signed papers and the proof this step relies on attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
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
  'M36:Revise a Quotation': 'fix.quotation',
  'M36:Submit for Internal Approval': 'fix.quotation',
  'M36:Issue to the Customer': 'fix.quotation',
  'M36:Quotation Delivery': 'fix.quotation.delivery',
  'M36:Accept by Customer Code': 'fix.quotation',
  'M36:Record Signed Acceptance': 'fix.quotation',
  'M36:Counter-Offer / Partial Acceptance': 'fix.quotation.counter',
  'M36:Decide a Counter-Offer': 'fix.quotation.counter',
  'M36:Record a Customer Decline': 'fix.quotation',
  'M36:Tender Bid': 'fix.tender',
  'M36:Bid Bond': 'fix.tender.bond',
  'M36:Variation Order': 'fix.tender.variation',
  'M36:Quotation Template': 'fix.quotation.template',
  'M36:Document Template (bilingual)': 'fix.document.template',
  'M36:Proforma Invoice (Local)': 'fix.sales.proforma',
  'M36:Technical Review Request': 'fix.estimate.review',
  'M36:Record Technical Review Outcome': 'fix.estimate.review',
  'M36:Quotation Term': 'fix.quotation.term',
  'M36:Proposed Contract Entitlement': 'fix.quotation.entitlement',
  'M36:Renewal Quotation': 'fix.quotation',
  'M36:Decide a Term Deviation': 'fix.quotation.term',
  'M36:Finance Credit Override': 'fix.quotation.credit.override',
  'M36:Accept by Phone (recorded consent)': 'fix.quotation',
  'M36:Legal Hold': 'fix.quotation.legal.hold',
  'M36:Release a Legal Hold': 'fix.quotation.legal.hold',
  'M36:Tender Document': 'fix.tender.document',
  'M36:Tender Outcome (loss)': 'fix.tender.outcome',
  'M36:Standard Term (library)': 'fix.quotation.standard.term',
  'M36:Bulk Estate Quotation (asset upload)': 'fix.quotation',
  'M36:Compare with the Previous Version': 'fix.quotation',
  'M36:Send Customer Approval Link': 'fix.quotation'
};

export const FORM_CHIPS = {
  'M36:Estimate': 'M36-form-estimate',
  'M36:Quotation (versioned)': 'M36-record',
  'M36:Revise a Quotation': 'M36-form-revise',
  'M36:Submit for Internal Approval': 'M36-form-submit',
  'M36:Issue to the Customer': 'M36-form-issue',
  'M36:Quotation Delivery': 'M36-form-delivery',
  'M36:Accept by Customer Code': 'M36-form-otp',
  'M36:Record Signed Acceptance': 'M36-form-signed',
  'M36:Counter-Offer / Partial Acceptance': 'M36-form-counter-offer',
  'M36:Decide a Counter-Offer': 'M36-form-counter-decide',
  'M36:Record a Customer Decline': 'M36-form-decline',
  'M36:Tender Bid': 'M36-form-tender',
  'M36:Bid Bond': 'M36-form-bond',
  'M36:Variation Order': 'M36-form-variation',
  'M36:Quotation Template': 'M36-form-template',
  'M36:Document Template (bilingual)': 'M24-form-template',
  'M36:Proforma Invoice (Local)': 'M36-form-proforma',
  'M36:Technical Review Request': 'M36-form-est-review',
  'M36:Record Technical Review Outcome': 'M36-form-est-review-decide',
  'M36:Quotation Term': 'M36-form-term',
  'M36:Proposed Contract Entitlement': 'M36-form-proposed-entitlement',
  'M36:Renewal Quotation': 'M36-form-renewal',
  'M36:Decide a Term Deviation': 'M36-form-term-decide',
  'M36:Finance Credit Override': 'M36-form-credit-override',
  'M36:Accept by Phone (recorded consent)': 'M36-form-phone',
  'M36:Legal Hold': 'M36-form-legal-hold',
  'M36:Release a Legal Hold': 'M36-form-hold-release',
  'M36:Tender Document': 'M36-form-tender-doc',
  'M36:Tender Outcome (loss)': 'M36-form-tender-outcome',
  'M36:Standard Term (library)': 'M36-form-std-term',
  'M36:Bulk Estate Quotation (asset upload)': 'M36-form-estate',
  'M36:Compare with the Previous Version': 'M36-form-compare',
  'M36:Send Customer Approval Link': 'M36-form-approval-link',
  'M36:__by_model__': {
    'fix.estimate': 'M36-form-estimate',
    'fix.quotation': 'M36-record',
    'fix.tender': 'M36-form-tender',
    'fix.tender.bond': 'M36-form-bond',
    'fix.quote.review': 'M36-form-review',
    'fix.tender.variation': 'M36-form-variation',
    'fix.quotation.template': 'M36-form-template',
    'fix.quotation.delivery': 'M36-form-delivery',
    'fix.quotation.counter': 'M36-form-counter-offer',
    'fix.document.template': 'M24-form-template',
    'fix.sales.proforma': 'M36-form-proforma',
    'fix.estimate.review': 'M36-form-est-review',
    'fix.quotation.standard.term': 'M36-form-std-term',
    'fix.quotation.term': 'M36-form-term',
    'fix.quotation.credit.override': 'M36-form-credit-override',
    'fix.quotation.legal.hold': 'M36-form-legal-hold',
    'fix.tender.document': 'M36-form-tender-doc',
    'fix.tender.outcome': 'M36-form-tender-outcome'
  },
  'M36:__by_screen__': {
    'M36-estimates': 'M36-form-estimate',
    'M36-proposed-entitlements': 'M36-form-proposed-entitlement',
    'M36-quotes': 'M36-record',
    'M36-proformas': 'M36-form-proforma',
    'M36-billing-quotes': 'M36-billing',
    'M36-templates': 'M36-form-template',
    'M36-versions': 'M36-record',
    'M36-loop': 'M36-record',
    'M36-internal': 'M36-form-review',
    'M36-pending': 'M36-record',
    'M36-deliveries': 'M36-form-delivery',
    'M36-counters': 'M36-form-counter-offer',
    'M36-doc-templates': 'M24-form-template',
    'M36-declined': 'M36-record',
    'M36-tenders': 'M36-form-tender',
    'M36-boq': 'M36-form-boq',
    'M36-bonds': 'M36-form-bond',
    'M36-variations': 'M36-form-variation',
    'M36-est-reviews': 'M36-form-est-review',
    'M36-std-terms': 'M36-form-std-term',
    'M36-terms': 'M36-form-term',
    'M36-term-deviations': 'M36-form-term',
    'M36-credit-overrides': 'M36-form-credit-override',
    'M36-renewals': 'M36-form-renewal',
    'M36-legal-holds': 'M36-form-legal-hold',
    'M36-tender-docs': 'M36-form-tender-doc',
    'M36-tender-outcomes': 'M36-form-tender-outcome'
  }
};

export const CREATE = {
  M36: { screen: 'M36-record', model: 'fix.quotation', label: 'Quotation' }
};
