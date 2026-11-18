/** @odoo-module **/
/* A06 · Supply Chain — M16 Procurement & Sourcing (v2 rebuild).
 * Requisition/PO existed; RFQ+bids+awards, blankets, expediting, inspection
 * and the requisition→PO conversion are new. PO Goods Receipts are this
 * module's own document: they feed the PO lines and the three-way match. The
 * warehouse stock receipts and RTV read M15's documents (single-owner surfaces).
 *
 * Capture-button audit (13 Nov 2026): Consolidation and 3-Way Match offered
 * nothing; RFQ & Bidding had no chip for the bid or the award, Blanket Orders
 * and Expediting no chip at all; GRN & Inspection offered a "GRN" chip that
 * made an M15 warehouse receipt with no purchase order, and the RTV list
 * refused "+ New" although its chip raised one. Each page now names what
 * captures its record (report: audit_analysis/M16_CAPTURE_BUTTON_AUDIT_2026-11-13.md).
 *
 * Capture audit pass 2 (19 Nov 2026), read against FR-PRO-001..038: the
 * buttons were there but several records lacked what the spec is about. A
 * requisition did not say where its demand came from; there was no
 * approved-source list (FR-PRO-009); an RFQ invited nobody and had no
 * deadline (FR-PRO-011); a bid had no warranty, MOQ, payment terms, incoterm
 * or quotation file (FR-PRO-012/013); a PO had no payment terms or incoterm
 * (FR-PRO-017); a blanket offered no call-off; a receipt line recorded no
 * condition (FR-PRO-026); services had no service entry (BRU-PRO-19); and the
 * 3-Way Match page offered no exception case or tolerance (FR-PRO-030, BRU-PRO-09).
 * Report: audit_analysis/M16_CAPTURE_BUTTON_AUDIT_PASS2_2026-11-19.md. */

export const MODULE = {
  area: 'A06', code: 'M16', en: 'Procurement & Sourcing', title: 'M16 · Procurement & Sourcing',
  bn: 'সংগ্রহ ও সোর্সিং', icon: '🛒',
  desc: 'Demand intake, requisitions and approval, cross-branch consolidation, RFQ events with bid comparison and award decisions, purchase orders, blanket agreements, expediting, goods receipts and inspection outcomes, the 3-way match workbench, spend analysis, price history and the RTV lifecycle.',
  kpis: [
    { l: 'Open Requisitions', m: 'open_requisitions' },
    { l: 'RFQs Open', m: 'rfq_open' },
    { l: 'Open POs', m: 'po_open' },
    { l: 'Match Exceptions', m: 'match_exceptions' },
    { l: 'Spend MTD', m: 'spend_mtd', prefix: '৳ ' },
    { l: 'OTD', m: 'otd_pct', suffix: '%' }
  ],
  groups: [
    { en: 'Requisitions', screens: [
      { id: 'M16-prs', en: 'Purchase Requisitions', bn: 'ক্রয়ের অনুরোধ', t: 'g' },
      { id: 'M16-consol', en: 'Cross-Branch Consolidation', bn: 'শাখা একীকরণ', t: 'r' }
    ]},
    { en: 'Sourcing', screens: [
      { id: 'M16-rfqs', en: 'RFQ Events', bn: 'আরএফকিউ', t: 'g' },
      { id: 'M16-compare', en: 'Bid Comparison', bn: 'দর তুলনা', t: 'g' },
      { id: 'M16-award', en: 'Award Decisions', bn: 'অ্যাওয়ার্ড', t: 'g' },
      { id: 'M16-sources', en: 'Approved Sources', bn: 'অনুমোদিত সরবরাহ উৎস', t: 'g' }
    ]},
    { en: 'Orders', screens: [
      { id: 'M16-pos', en: 'Local Purchase Orders', bn: 'স্থানীয় ক্রয়াদেশ', t: 'g' },
      { id: 'M16-pos-import', en: 'Import Purchase Orders', bn: 'আমদানি ক্রয়াদেশ', t: 'g' },
      { id: 'M16-proformas', en: 'Supplier Proformas', bn: 'সরবরাহকারীর প্রফর্মা ইনভয়েস', t: 'g' },
      { id: 'M16-advances', en: 'Supplier Advances', bn: 'সরবরাহকারীকে অগ্রিম', t: 'g' },
      { id: 'M16-blanket', en: 'Blanket / Call-Off', bn: 'ব্ল্যাংকেট অর্ডার', t: 'g' },
      { id: 'M16-expedite', en: 'Expediting Desk', bn: 'এক্সপিডাইটিং', t: 'g' }
    ]},
    { en: 'Receiving & Match', screens: [
      { id: 'M16-po-receipts', en: 'PO Goods Receipts', bn: 'ক্রয়াদেশের পণ্য গ্রহণ', t: 'g' },
      { id: 'M16-inspection', en: 'Inspection Outcomes', bn: 'পরিদর্শন ফলাফল', t: 'g' },
      { id: 'M16-service-entries', en: 'Service Entries', bn: 'সেবা প্রাপ্তি নিশ্চিতকরণ', t: 'g' },
      { id: 'M16-match', en: '3-Way Match Workbench', bn: 'থ্রি-ওয়ে ম্যাচ', t: 'r' },
      { id: 'M16-match-cases', en: 'Match Exception Cases (M52)', bn: 'ম্যাচ ব্যতিক্রম কেস (M52)', t: 'g' },
      { id: 'M16-grir', en: 'GR/IR Reconciliation', bn: 'জিআর/আইআর সমন্বয়', t: 'r' },
      { id: 'M16-grn', en: 'Warehouse Stock Receipts (M15)', bn: 'গুদামের স্টক রসিদ (M15)', t: 'g' }
    ]},
    { en: 'Analysis', screens: [
      { id: 'M16-spend', en: 'Spend Analysis', bn: 'ব্যয় বিশ্লেষণ', t: 'r' },
      { id: 'M16-pricehist', en: 'Price History & Alerts', bn: 'মূল্যের ইতিহাস', t: 'r' },
      { id: 'M16-emergency', en: 'Emergency Purchases', bn: 'জরুরি ক্রয়', t: 'r' },
      { id: 'M16-rtv', en: 'RTV Lifecycle', bn: 'ভেন্ডর ফেরত চক্র', t: 'g' }
    ]}
  ],
  reports: ['Spend by Category & Vendor', 'Match Exception Pareto', 'OTD by Vendor', 'Price Variance Alert', 'Maverick Spend', 'PO Cycle Time', 'GR/IR Reconciliation', 'Emergency Purchases'],
  forms: ['Purchase Requisition', 'Consolidated RFQ', 'RFQ', 'Supplier Bid', 'Award Decision', 'Purchase Order', 'Import Purchase Order', 'Supplier Proforma', 'Supplier Advance', 'Blanket Agreement', 'Expediting Case', 'PO Goods Receipt', 'Inspection Outcome', 'RTV Request', 'Vendor Bill', 'Approved Source', 'Service Entry', 'Match Exception Case', 'Match Tolerance'],
  cross: ['M43 planned orders', 'M42 supplier gate', 'M52 invoices', 'M44 imports', 'P05 vendor portal'],
  freg: { src: 88, sub: [
    ['1', 'Demand Intake', 8, { model: 'fix.requisition', cols: ['description', 'demand_source', 'source_ref', 'branch_id', 'requested_by', 'urgency', 'create_date'], screens: ['M16-prs'], reports: ['Emergency Purchases'], forms: ['Purchase Requisition'] }],
    ['2', 'Requisition & Approval', 10, { model: 'fix.requisition', cols: ['description', 'estimate_amount', 'urgency', 'state', 'purchase_order_id'], screens: ['M16-prs'], reports: ['Maverick Spend'], forms: ['Purchase Requisition'] }],
    /* FR-PRO-006: the approved requisitions still to be bought; the capture is
     * the one sourcing event that buys a part for several branches */
    ['3', 'Consolidation', 6, { model: 'fix.requisition', cols: ['product_id', 'branch_id', 'qty', 'required_by', 'estimate_amount', 'state'], domain: [['state', '=', 'approved'], ['purchase_order_id', '=', false]], screens: ['M16-consol'], reports: [], forms: ['Consolidated RFQ'], create: 'M16-form-rfq-consol' }],
    ['4', 'RFQ & Bidding', 12, { model: 'fix.procurement.rfq', cols: ['name', 'product_id', 'qty', 'required_by', 'state'], screens: ['M16-rfqs', 'M16-compare', 'M16-award', 'M16-sources'], reports: ['Price Variance Alert'], forms: ['RFQ', 'Supplier Bid', 'Award Decision', 'Approved Source'] }],
    ['5', 'PO Lifecycle', 11, { model: 'fix.purchase.order', cols: ['name', 'vendor_id', 'date_order', 'amount_total', 'state'], screens: ['M16-pos', 'M16-pos-import', 'M16-proformas', 'M16-advances'], reports: ['PO Cycle Time', 'OTD by Vendor'], forms: ['Purchase Order', 'Import Purchase Order', 'Supplier Proforma', 'Supplier Advance'] }],
    ['6', 'Blanket Orders', 6, { model: 'fix.procurement.blanket', cols: ['name', 'vendor_id', 'valid_from', 'valid_to', 'cap_amount'], screens: ['M16-blanket'], reports: ['Spend by Category & Vendor'], forms: ['Blanket Agreement'] }],
    ['7', 'Expediting', 7, { model: 'fix.procurement.expedite', cols: ['name', 'purchase_order_id', 'promised_date', 'follow_up_date', 'state'], screens: ['M16-expedite'], reports: ['OTD by Vendor'], forms: ['Expediting Case'] }],
    /* goods are received against a PO here (PO Goods Receipt), judged
     * (Inspection Outcome) and returned (RTV Request); a service or non-stock
     * line is confirmed by its requester instead (Service Entry, BRU-PRO-19);
     * the warehouse's own stock receipt is M15's and is only read here */
    ['8', 'GRN & Inspection', 9, { model: 'fix.procurement.inspection', cols: ['name', 'receipt_ref', 'product_id', 'qty_accepted', 'outcome'], screens: ['M16-po-receipts', 'M16-inspection', 'M16-service-entries', 'M16-rtv', 'M16-grn'], reports: ['GR/IR Reconciliation'], forms: ['PO Goods Receipt', 'Inspection Outcome', 'Service Entry', 'RTV Request'] }],
    /* the match itself is computed when the bill is registered; the record a
     * person enters is the vendor's bill (M52's form), the third document; an
     * exception is worked as a case and the tolerance bands are set by the
     * CFO (M52's own records, FR-PRO-030 / BRU-PRO-09) */
    ['9', '3-Way Match', 10, { model: 'fix.vendor.invoice', cols: ['invoice_ref', 'vendor_id', 'requisition_id', 'match_state', 'total_payable'], domain: [['bill_type', '=', 'po']], screens: ['M16-match-queue', 'M16-match-cases', 'M16-match'], reports: ['Match Exception Pareto', 'GR/IR Reconciliation'], forms: ['Vendor Bill', 'Match Exception Case', 'Match Tolerance'], create: 'M52-form-bill' }],
    ['10', 'Spend Analysis', 9, { model: 'fix.purchase.order', cols: ['vendor_id', 'branch_id', 'date_order', 'amount_total', 'state'], screens: ['M16-spend', 'M16-pricehist'], reports: ['Spend by Category & Vendor', 'Maverick Spend', 'Price Variance Alert', 'Emergency Purchases'], forms: [], create: false }]
  ] }
};

export const SCREENS = {
  'M16-prs': { kind: 'model_list', model: 'fix.requisition', stateField: 'state',
    cols: ['description', 'demand_source', 'purchase_kind', 'branch_id', 'vendor_id', 'qty', 'estimate_amount', 'cost_centre', 'required_by', 'urgency', 'emergency_state', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval' },
      { m: 'action_request_approval', l: 'Request Approval (re-route)' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_reset_draft', l: 'Back to Draft' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Reason for cancelling the requisition', kwarg: 'reason' },
      { m: 'action_convert_to_po', l: 'Convert to PO' },
      { m: 'action_emergency_release', l: 'Emergency Release (post-hoc approval)', ask: 'What job stopped, and why it cannot wait for approval', kwarg: 'reason' },
      { m: 'action_emergency_close', l: 'Close Failed Emergency (CFO)', ask: 'How the failed emergency purchase was dealt with', kwarg: 'reason' }
    ] },
  'M16-consol': { kind: 'table_report', module: 'M16', report: 'consolidation', title: 'Cross-Branch Consolidation', period: false },
  'M16-rfqs': { kind: 'model_list', model: 'fix.procurement.rfq', stateField: 'state',
    cols: ['name', 'description', 'product_id', 'qty', 'required_by', 'target_price', 'invited_count', 'response_deadline', 'state'],
    actions: [
      /* FR-PRO-009/011: the part's approved sources become the invitations */
      { m: 'action_invite_approved_sources', l: 'Invite Approved Sources', states: ['draft', 'open'] },
      { m: 'action_open', l: 'Open RFQ' },
      { m: 'action_close', l: 'Close RFQ' }
    ] },
  'M16-compare': { kind: 'model_list', model: 'fix.procurement.bid', stateField: 'state',
    /* FR-PRO-013: compared on price, lead time, warranty, MOQ, payment terms
     * and incoterm, not on price alone */
    cols: ['rfq_id', 'vendor_id', 'unit_price', 'total_price', 'lead_time_days', 'warranty_months', 'moq', 'payment_terms', 'incoterm', 'valid_until', 'state'] },
  'M16-award': { kind: 'model_list', model: 'fix.procurement.award', stateField: 'state',
    cols: ['name', 'rfq_id', 'bid_id', 'decided_on', 'is_lowest', 'rationale', 'needs_approval', 'state'],
    actions: [
      { m: 'action_decide', l: 'Decide Award' },
      { m: 'action_create_po', l: 'Raise PO from Award' },
      { m: 'action_cancel', l: 'Cancel Award', ask: 'Reason for cancelling the award', kwarg: 'reason' }
    ] },
  /* Two purchase formats (12 Nov 2026): a local purchase order (BDT or USD)
   * and an import purchase order (the supplier's currency) fulfilled by an
   * M44 import order raised from it, or that raised it. */
  'M16-pos': { kind: 'model_list', model: 'fix.purchase.order', stateField: 'state',
    domain: [['purchase_type', '=', 'local']],
    cols: ['name', 'vendor_id', 'date_order', 'currency_id', 'amount_total', 'payment_terms', 'vendor_confirmed_date', 'receipt_refs', 'approval_state', 'state'],
    actions: [
      { m: 'action_submit_for_approval', l: 'Request Approval', ask: 'Business justification for the PO', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_record_requisition_exception', l: 'No-Requisition Exception (manager)', ask: 'Why this PO has no requisition', kwarg: 'reason' },
      { m: 'action_send', l: 'Send PO' },
      { m: 'action_acknowledge_on_behalf', l: 'Acknowledge on Behalf', asks: [
        { label: "The vendor's confirmation this rests on (e-mail / letter / call reference)", kwarg: 'evidence' },
        { label: 'Delivery date the vendor confirmed (YYYY-MM-DD)', kwarg: 'confirmed_date' }
      ] },
      { m: 'action_start_receipt', l: 'Start Goods Receipt (receiver)' },
      /* a local supplier's proforma invoice, captured on its own form for this order */
      { m: '__record_proforma', l: 'Record Supplier Proforma', form: 'M16-form-proforma', prefill: 'purchase_order_id',
        states: ['draft', 'sent', 'acknowledged', 'partially_received'] },
      { m: 'action_create_change_order', l: 'Raise Change Order' },
      { m: 'action_cancel', l: 'Cancel PO', ask: 'Reason for cancelling the PO', kwarg: 'reason' },
      { m: 'action_close', l: 'Close PO', ask: 'Reason (needed to close a partly received PO short)', kwarg: 'reason' },
      { m: 'action_fix_print', l: '🖨 Print Purchase Order (PDF)' }
    ] },
  'M16-pos-import': { kind: 'model_list', model: 'fix.purchase.order', stateField: 'state',
    domain: [['purchase_type', '=', 'import']],
    cols: ['name', 'vendor_id', 'date_order', 'currency_id', 'amount_total', 'incoterm', 'import_order_refs', 'approval_state', 'state'],
    empty: 'No import purchase order yet. Raise one with + New, or from a draft M44 import order (Create Purchase Order).',
    actions: [
      { m: 'action_submit_for_approval', l: 'Request Approval', ask: 'Business justification for the PO', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_record_requisition_exception', l: 'No-Requisition Exception (manager)', ask: 'Why this PO has no requisition', kwarg: 'reason' },
      { m: 'action_send', l: 'Send PO' },
      { m: 'action_create_import_order', l: 'Create Import Order (M44)', states: ['draft', 'sent', 'acknowledged', 'partially_received'] },
      { m: 'action_create_change_order', l: 'Raise Change Order' },
      { m: 'action_cancel', l: 'Cancel PO', ask: 'Reason for cancelling the PO', kwarg: 'reason' },
      { m: 'action_close', l: 'Close PO', ask: 'Reason (needed to close a partly received PO short)', kwarg: 'reason' },
      { m: 'action_fix_print', l: '🖨 Print Purchase Order (PDF)' }
    ] },
  /* A local supplier's proforma invoice and the advance paid against it
   * (12 Nov 2026): imports had both in M44, a local purchase had neither. */
  'M16-proformas': { kind: 'model_list', model: 'fix.purchase.proforma', stateField: 'state',
    cols: ['name', 'proforma_no', 'vendor_id', 'purchase_order_id', 'amount', 'order_total', 'issued_on', 'valid_until', 'advance_approved', 'decided_by_id', 'state'],
    empty: 'No supplier proforma yet. Open a purchase order and use Record Supplier Proforma, or + New here and choose the order.',
    actions: [
      { m: 'action_approve', l: 'Approve Proforma (approver)', states: ['received'] },
      { m: 'action_reject', l: 'Reject', ask: 'Why the proforma is rejected', kwarg: 'reason', states: ['received'] },
      { m: 'action_cancel', l: 'Cancel', states: ['received'] },
      { m: '__request_advance', l: 'Request Advance', form: 'M16-form-advance', prefill: 'proforma_id', states: ['approved'] }
    ] },
  'M16-advances': { kind: 'model_list', model: 'fix.purchase.advance', stateField: 'state',
    cols: ['name', 'purchase_order_id', 'vendor_id', 'proforma_id', 'amount', 'remaining_amount', 'purpose', 'requested_by_id', 'decided_by_id', 'above_cap', 'state'],
    empty: 'No supplier advance yet. An advance is requested against an approved supplier proforma (Request Advance on the proforma).',
    actions: [
      { m: 'action_request', l: 'Request Approval', states: ['draft'] },
      { m: 'action_approve', l: 'Approve Advance (approver)', ask: 'Reason (needed when the advances pass the advance cap)', kwarg: 'reason', states: ['requested'] },
      { m: 'action_reject', l: 'Reject', ask: 'Why the advance is rejected', kwarg: 'reason', states: ['requested'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft', 'requested'] },
      /* treasury (M50) pays it; the supplier's bill takes it back (M52) */
      { m: 'action_request_payment', l: 'Request Payment (accountant)', states: ['approved'] }
    ] },
  'M16-blanket': { kind: 'model_list', model: 'fix.procurement.blanket', stateField: 'state',
    cols: ['name', 'vendor_id', 'valid_from', 'valid_to', 'cap_amount', 'consumed_amount', 'remaining_amount', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate (approver)' },
      /* FR-PRO-019: a call-off is a purchase order against the agreement,
       * with its vendor; the cap and window are checked when it is sent */
      { m: '__call_off', l: 'Raise Call-Off PO', form: 'M16-form-po', prefill: 'blanket_id', carry: { vendor_id: 'vendor_id' }, states: ['active'] },
      { m: 'action_revise', l: 'Revise Terms' },
      { m: 'action_cancel', l: 'Cancel Agreement' }
    ] },
  'M16-expedite': { kind: 'model_list', model: 'fix.procurement.expedite', stateField: 'state',
    cols: ['name', 'purchase_order_id', 'reason', 'promised_date', 'follow_up_date', 'state'],
    actions: [
      { m: 'action_chase', l: 'Chase' },
      { m: 'action_resolve', l: 'Resolve', ask: 'How the case was resolved', kwarg: 'note' }
    ] },
  'M16-po-receipts': { kind: 'model_list', model: 'fix.purchase.receipt', stateField: 'state',
    cols: ['name', 'purchase_order_id', 'vendor_id', 'delivery_note_ref', 'received_on', 'receiver_id', 'state'],
    actions: [
      { m: 'action_post', l: 'Post Receipt' },
      { m: 'action_cancel', l: 'Cancel Draft' }
    ],
    note: 'The receipt against a purchase order: posting it feeds the PO lines and the three-way match. Start one from a purchase order, or create it here and pick the order.' },
  'M16-grn': { kind: 'model_list', model: 'fix.stock.receipt', stateField: 'state', create: false,
    cols: ['name', 'partner_id', 'location_id', 'received_on', 'state'],
    note: "The warehouse's stock documents (M15). Posting a PO goods receipt raises these; goods are received against a PO on PO Goods Receipts." },
  'M16-inspection': { kind: 'model_list', model: 'fix.procurement.inspection', stateField: 'state',
    cols: ['name', 'receipt_ref', 'purchase_order_id', 'product_id', 'qty_received', 'qty_accepted', 'outcome', 'state'],
    actions: [{ m: 'action_confirm', l: 'Confirm Outcome' }] },
  /* FR-PRO-037 / BRU-PRO-19: a service or non-stock line has no goods
   * receipt; its requester confirms what was delivered */
  'M16-service-entries': { kind: 'model_list', model: 'fix.purchase.service.entry', stateField: 'state',
    cols: ['name', 'purchase_order_id', 'vendor_id', 'product_id', 'qty_confirmed', 'service_period', 'service_date', 'confirmed_by_id', 'receipt_id', 'state'],
    empty: 'No service entry yet. A service or non-stock purchase is confirmed here by its requester once the supplier has delivered (+ New, choose the order and its line).',
    actions: [
      { m: 'action_confirm', l: 'Confirm Delivery (requester)', states: ['draft'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft'] }
    ] },
  /* FR-PRO-009: the suppliers approved to supply each part */
  'M16-sources': { kind: 'model_list', model: 'fix.procurement.approved.source', stateField: 'state',
    cols: ['name', 'product_id', 'vendor_id', 'priority', 'agreed_price', 'currency_id', 'moq', 'lead_time_days', 'valid_from', 'valid_to', 'approved_by_id', 'state'],
    empty: 'No approved source yet. + New proposes a supplier for a part with its priority, agreed price, MOQ and lead time; another Procurement Approver approves it.',
    actions: [
      { m: 'action_approve', l: 'Approve (second approver)', states: ['draft'] },
      { m: 'action_withdraw', l: 'Withdraw', ask: 'Why the supplier is no longer an approved source', kwarg: 'reason', states: ['approved'] }
    ] },
  'M16-match': { kind: 'table_report', module: 'M16', report: 'three_way', title: '3-Way Match Workbench', period: false },
  /* The PO bills and their match verdict, as M16 reads them: the match runs
   * when AP registers the bill (M52) and again when a receipt or inspection
   * changes; it is never typed. */
  'M16-match-queue': { kind: 'model_list', model: 'fix.vendor.invoice', stateField: 'match_state', create: false,
    domain: [['bill_type', '=', 'po']],
    cols: ['invoice_ref', 'vendor_id', 'requisition_id', 'invoice_date', 'total_payable', 'match_state', 'match_detail', 'approval_state'],
    empty: 'No purchase-order bill yet. A vendor bill is registered by Accounts Payable (+ New Vendor Bill on this page opens the M52 form); the match then runs against its purchase order and posted goods receipts.' },
  /* FR-PRO-030: each exception is worked as a case with its cause, owner and
   * due date (M52's record, resolved there when its cause is fixed) */
  'M16-match-cases': { kind: 'model_list', model: 'fix.ap.match.exception', stateField: 'state',
    cols: ['name', 'invoice_id', 'vendor_id', 'purchase_order_id', 'exception_type', 'responsible_party', 'owner_id', 'due_date', 'age_days', 'state'],
    empty: 'No match exception case. A case is opened for a blocked purchase-order bill (+ New here, or the daily check in M52).' },
  'M16-grir': { kind: 'table_report', module: 'M16', report: 'gr_ir', title: 'GR/IR Reconciliation', period: false },
  'M16-spend': { kind: 'table_report', module: 'M16', report: 'spend_by_category', title: 'Spend Analysis', period: false },
  'M16-pricehist': { kind: 'table_report', module: 'M16', report: 'price_history', title: 'Price History & Alerts', period: false },
  'M16-emergency': { kind: 'table_report', module: 'M16', report: 'emergency_spend', title: 'Emergency Purchases', period: false },
  /* FR-PRO-033/034: procurement raises the return and tracks its credit;
   * M15 approves it and ships the stock (its own RTV screen). */
  'M16-rtv': { kind: 'model_list', model: 'fix.stock.rtv', stateField: 'state',
    cols: ['name', 'partner_id', 'part_id', 'qty', 'reason', 'rtv_ref', 'purchase_order_id', 'state'],
    empty: 'No return to vendor yet. A rejection at inspection raises one as a draft; + New raises one for goods found defective later.',
    actions: [
      { m: 'action_submit', l: 'Submit RTV', states: ['draft'] },
      { m: 'action_mark_credited', l: 'Record Credit', ask: 'Vendor credit note / replacement reference', kwarg: 'credit_ref', states: ['shipped'] }
    ] },

  /* Report chips -> their own computed pack */
  'M16-rpt-spend': { kind: 'table_report', module: 'M16', report: 'spend_by_category', title: 'Spend by Category & Vendor', period: false },
  'M16-rpt-match': { kind: 'table_report', module: 'M16', report: 'match_exception', title: 'Match Exception Pareto', period: false },
  'M16-rpt-otd': { kind: 'table_report', module: 'M16', report: 'otd_by_vendor', title: 'OTD by Vendor', period: false },
  'M16-rpt-price': { kind: 'table_report', module: 'M16', report: 'price_variance', title: 'Price Variance Alert', period: false },
  'M16-rpt-maverick': { kind: 'table_report', module: 'M16', report: 'maverick_spend', title: 'Maverick Spend', period: false },
  'M16-rpt-cycle': { kind: 'table_report', module: 'M16', report: 'po_cycle_time', title: 'PO Cycle Time', period: false },
  'M16-rpt-grir': { kind: 'table_report', module: 'M16', report: 'gr_ir', title: 'GR/IR Reconciliation', period: false },
  'M16-rpt-emergency': { kind: 'table_report', module: 'M16', report: 'emergency_spend', title: 'Emergency Purchases', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M16-form-requisition': {
    kind: 'model_form',
    model: 'fix.requisition',
    title: 'Purchase Requisition',
    back: 'M16-prs',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted for Approval', approved: 'Approved',
      converted: 'Converted to PO', rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'request', label: '1. Request', bn: '১. অনুরোধ', icon: '📝', badge: '7' },
      { id: 'source', label: '2. Source & Budget', bn: '২. উৎস ও বাজেট', icon: '🧭', badge: '7' },
      { id: 'status', label: '3. Requester & Status', bn: '৩. অনুরোধকারী ও অবস্থা', icon: '✔', badge: '5' }
    ],
    sections: [
      { tab: 'request', title: 'Request', note: 'Submit for approval: it is routed by amount (related requisitions of the same requester in the split window are added) to a DOFA tier holder other than you, who decides it in the approval inbox. A change to amount, quantity, product or vendor after submission returns it to draft. With no preferred vendor, the part\'s first approved source is filled in when it is submitted. Then a buyer converts it to a PO.',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'justification', type: 'text', label: 'Business Justification' },
          { name: 'product_id', label: 'Product' },
          { name: 'qty', label: 'Quantity' },
          { name: 'vendor_id', label: 'Preferred Vendor', domain: [['fix_supplier_status', '=', 'active']], emptyNote: 'No supplier is active yet. A supplier becomes active in M42 Supplier Management once its trade licence, TIN and VAT documents are verified, it is screened, and a Supplier Approver activates it (BRU-PRO-02).' },
          { name: 'estimate_amount', label: 'Estimated Amount' },
          { name: 'urgency', required: true, label: 'Urgency' }
        ] },
      /* FR-PRO-001/002: where the demand comes from, what it refers to and
       * the budget it is charged to; FR-PRO-037: what kind of purchase */
      { tab: 'source', title: 'Source & Budget', note: 'Where the demand comes from. An M15 replenishment alert, an M43 planned order, a job backorder or a project names its reference before the requisition is submitted; a project also names its budget. A service or non-stock purchase is later confirmed by a Service Entry from you, not by a goods receipt.',
        fields: [
          { name: 'demand_source', required: true, label: 'Demand Source' },
          { name: 'source_ref', label: 'Source Reference (alert / plan / job / project no.)' },
          { name: 'purchase_kind', required: true, label: 'What Is Bought' },
          { name: 'cost_centre', required: true, label: 'Cost Centre' },
          { name: 'budget_ref', label: 'Budget Reference' },
          { name: 'required_by', required: true, label: 'Required By' },
          { name: 'branch_id', label: 'Deliver to Branch' }
        ] },
      { tab: 'status', title: 'Requester & Status', note: 'The requester confirms services when they are delivered. The emergency path is set by Emergency Release on the list.',
        fields: [
          { name: 'requested_by', required: true, label: 'Requested By' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'emergency_state', readonly: true, label: 'Emergency Path' },
          { name: 'emergency_deadline', readonly: true, label: 'Post-Hoc Approval Due' },
          { name: 'purchase_order_id', readonly: true, label: 'Purchase Order' }
        ] }
    ]
  },

  'M16-form-rfq': {
    kind: 'model_form',
    model: 'fix.procurement.rfq',
    title: 'RFQ',
    back: 'M16-rfqs',
    status: { field: 'state', labels: {
      draft: 'Draft', open: 'Open for Bids', closed: 'Closed', awarded: 'Awarded' } },
    sections: [
      { title: 'RFQ', note: 'Choose the suppliers asked to quote (or Invite Approved Sources from the list) and the response deadline, then open the event: only invited suppliers bid, before the deadline; suppliers can be added while it is open, never removed. Bids are sealed (hidden from others until close). Close it, then propose the award: the lowest compliant bid is decided at once; any other bid, or fewer bids than the minimum, needs a rationale or exception that a Procurement Approver decides.',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'requisition_id', label: 'Source Requisition', domain: [['state', '=', 'approved']] },
          { name: 'requisition_ids', readonly: true, label: 'Consolidated Requisitions' },
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'qty', label: 'Quantity' },
          { name: 'required_by', label: 'Required By' },
          { name: 'invited_vendor_ids', required: true, label: 'Invited Suppliers', domain: [['fix_supplier_status', '!=', false]],
            emptyNote: 'No supplier is registered in M42 yet. Suppliers are registered and activated in M42 Supplier Management.' },
          { name: 'response_deadline', required: true, label: 'Response Deadline' },
          { name: 'target_price', label: 'Target Price' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  /* FR-PRO-006: one sourcing event for a part several branches asked for.
   * The quantity is the requisitions' total, set at save; the award's PO
   * converts every requisition with a line of its own. */
  'M16-form-rfq-consol': {
    kind: 'model_form',
    model: 'fix.procurement.rfq',
    title: 'Consolidated RFQ',
    newLabel: 'Consolidate Requisitions into an RFQ',
    back: 'M16-rfqs',
    status: { field: 'state', labels: {
      draft: 'Draft', open: 'Open for Bids', closed: 'Closed', awarded: 'Awarded' } },
    sections: [
      { title: 'Consolidation', note: 'Choose the part, then every approved requisition for it that this event should buy, from any branch (Cross-Branch Consolidation on this page lists the candidates). The RFQ quantity becomes their total. A requisition already on another open RFQ, already on a purchase order, or for another part is refused. Then open the RFQ and record the bids as usual; the award raises one purchase order with a line for each requisition.',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'product_id', required: true, label: 'Part' },
          { name: 'requisition_ids', required: true, label: 'Requisitions to Consolidate',
            domain: [['state', '=', 'approved'], ['purchase_order_id', '=', false]],
            emptyNote: 'No approved requisition is waiting to be bought. Requisitions are raised and approved on Purchase Requisitions first.' },
          { name: 'qty', readonly: true, label: 'Total Quantity' },
          { name: 'required_by', label: 'Required By' },
          { name: 'invited_vendor_ids', required: true, label: 'Invited Suppliers', domain: [['fix_supplier_status', '!=', false]] },
          { name: 'response_deadline', required: true, label: 'Response Deadline' },
          { name: 'target_price', label: 'Target Price' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M16-form-po': {
    kind: 'model_form',
    model: 'fix.purchase.order',
    title: 'Local Purchase Order',
    back: 'M16-pos',
    status: { field: 'state', labels: {
      draft: 'Draft', sent: 'Sent', acknowledged: 'Acknowledged',
      partially_received: 'Partially Received', received: 'Received',
      closed: 'Closed', cancelled: 'Cancelled', superseded: 'Superseded by Change Order' } },
    sections: [
      { title: 'Order', note: 'The PO is the ordered side of the three-way match. It needs an approved requisition (or a manager\'s documented exception) and an active M42 supplier; request approval (routed by amount), then send it. Once sent it is locked: changes go through a change order that is approved again. The vendor acknowledges in the P05 portal with its delivery date. A Receiver then starts the goods receipt from this order (Start Goods Receipt).',
        fields: [
          { name: 'vendor_id', required: true, label: 'Vendor', domain: [['fix_supplier_status', '=', 'active'], ['fix_supplier_residency', '=', 'resident']],
            emptyNote: 'No Bangladesh-registered supplier is active yet, so no purchase order can be raised. A supplier becomes active in M42 Supplier Management: its trade licence, TIN and VAT documents are verified, it is screened, and a Supplier Approver activates it (BRU-PRO-02). Overseas suppliers are ordered from on an Import Purchase Order.' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'branch_id', label: 'Deliver-to Branch' },
          { name: 'date_order', required: true, label: 'Order Date' },
          { name: 'currency_id', required: true, label: 'Currency (BDT or USD)', domain: [['fix_local_purchase', '=', true]] },
          { name: 'promised_date', label: 'Promised Date' },
          { name: 'payment_terms', label: 'Payment Terms' },
          { name: 'incoterm', label: 'Incoterm (delivery terms)' },
          { name: 'blanket_id', label: 'Blanket Agreement (call-off)', domain: [['state', '=', 'active']] },
          { name: 'vendor_confirmed_date', readonly: true, label: 'Vendor-Confirmed Delivery' },
          { name: 'receipt_refs', readonly: true, label: 'Goods Receipts' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Order Lines',
      note: 'Ordered quantity must be positive. Received quantities come from posted goods receipts only.',
      fields: [
        { name: 'product_id', required: true, label: 'Product' },
        { name: 'description', label: 'Description' },
        { name: 'qty_ordered', required: true, label: 'Ordered' },
        { name: 'unit_price', required: true, label: 'Unit Price' },
        { name: 'line_total', readonly: true, label: 'Line Total' }
      ]
    }
  },

  /* The import format: the supplier's currency, fulfilled by an M44 import
   * order raised from it (Create Import Order) or that raised it. */
  'M16-form-po-import': {
    kind: 'model_form',
    model: 'fix.purchase.order',
    title: 'Import Purchase Order',
    back: 'M16-pos-import',
    status: { field: 'state', labels: {
      draft: 'Draft', sent: 'Sent', acknowledged: 'Acknowledged',
      partially_received: 'Partially Received', received: 'Received',
      closed: 'Closed', cancelled: 'Cancelled', superseded: 'Superseded by Change Order' } },
    sections: [
      { title: 'Import Order', note: 'A purchase from an overseas supplier, in its own currency (USD, EUR, CNY, JPY, …). Approved and sent like a local purchase order; then Create Import Order raises the M44 import order (proforma, LC, shipment, customs) with these lines. Started from an M44 import order instead, this purchase order is raised from it.',
        fields: [
          { name: 'purchase_type', required: true, label: 'Purchase Type', value: 'import' },
          { name: 'vendor_id', required: true, label: 'Overseas Supplier', domain: [['fix_supplier_status', '=', 'active'], ['fix_supplier_residency', '=', 'foreign']],
            emptyNote: 'No overseas supplier is active yet, so no import purchase order can be raised. In M42 Supplier Management a Supplier Steward marks the supplier Foreign; its certificate of incorporation, tax residency and bank documents are verified, it is screened, and a Supplier Approver activates it.' },
          { name: 'currency_id', required: true, label: 'Currency (the supplier\'s)', defaultRef: 'base.USD' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'date_order', required: true, label: 'Order Date' },
          { name: 'promised_date', label: 'Expected Shipment' },
          { name: 'incoterm', required: true, label: 'Incoterm' },
          { name: 'payment_terms', label: 'Payment Terms (LC / TT / ...)' },
          { name: 'import_order_refs', readonly: true, label: 'M44 Import Orders' },
          { name: 'vendor_confirmed_date', readonly: true, label: 'Supplier-Confirmed Date' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Order Lines',
      note: 'Each product needs its M15 spare part to be imported. Prices are in the order currency.',
      fields: [
        { name: 'product_id', required: true, label: 'Product' },
        { name: 'description', label: 'Description' },
        { name: 'qty_ordered', required: true, label: 'Quantity' },
        { name: 'unit_price', required: true, label: 'Unit Price' },
        { name: 'line_total', readonly: true, label: 'Line Total' }
      ]
    }
  },

  'M16-form-po-receipt': {
    kind: 'model_form',
    model: 'fix.purchase.receipt',
    title: 'PO Goods Receipt',
    back: 'M16-po-receipts',
    status: { field: 'state', labels: {
      draft: 'Draft', posted: 'Posted', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Goods Receipt', note: 'Pick the purchase order and save: the grid fills with its open lines at what is still due. Correct the delivered quantities, remove what did not arrive, then Post Receipt. Posted by a Receiver who neither requested nor bought the order, and final once posted. Goods wait for their inspection before they can be invoiced.',
        fields: [
          { name: 'purchase_order_id', required: true, label: 'Purchase Order', domain: [['state', 'in', ['sent', 'acknowledged', 'partially_received']]] },
          { name: 'delivery_note_ref', label: 'Vendor Delivery Note / Challan' },
          { name: 'notes', type: 'text', label: 'Notes' },
          { name: 'vendor_id', readonly: true, label: 'Vendor' },
          { name: 'received_on', readonly: true, label: 'Received On' },
          { name: 'receiver_id', readonly: true, label: 'Received By' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Lines of the Chosen Order',
      note: 'Only the open lines of the order above. Over-delivery beyond the configured tolerance is refused at posting. A line that arrived damaged, wrong, short or in excess needs the discrepancy described. Service and non-stock lines are confirmed by a Service Entry instead.',
      fixedRows: true,
      fields: [
        { name: 'po_line_id', readonly: true, label: 'PO Line' },
        { name: 'qty_received', required: true, label: 'Delivered' },
        { name: 'condition', required: true, label: 'Condition' },
        { name: 'discrepancy_note', label: 'Discrepancy' },
        { name: 'inspection_state', readonly: true, label: 'Inspection' },
        { name: 'qty_accepted', readonly: true, label: 'Accepted' }
      ]
    }
  },

  'M16-form-grn': {
    kind: 'model_form',
    model: 'fix.stock.receipt',
    title: 'Warehouse Stock Receipt (M15)',
    back: 'M16-grn',
    create: false, pick: 'A warehouse stock receipt is raised by posting a PO goods receipt (or in M15): open one from Warehouse Stock Receipts.',
    status: { field: 'state', labels: {
      draft: 'Draft', inspected: 'Inspected', posted: 'Posted' } },
    sections: [
      { title: 'Stock Receipt', note: 'A warehouse document of M15: it does not receive a purchase order (PO Goods Receipts does). The inspection gate is M15\'s: accepted quantity per line, then Inspect and Post from the receipts screen.',
        fields: [
          { name: 'partner_id', required: true, label: 'Supplier', domain: [['fix_supplier_status', '!=', false]] },
          { name: 'location_id', required: true, label: 'Receiving Location' },
          { name: 'received_on', required: true, label: 'Received On' },
          { name: 'inspection_notes', label: 'Inspection Notes' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Receipt Lines',
      note: 'Accepted ≤ received; a serial/lot line creates the lot.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'qty_received', required: true, label: 'Received' },
        { name: 'qty_accepted', required: true, label: 'Accepted' },
        { name: 'unit_cost', label: 'Unit Cost' },
        { name: 'line_no', label: 'Serial / Lot' }
      ]
    }
  },

  'M16-form-rtv': {
    kind: 'model_form',
    model: 'fix.stock.rtv',
    title: 'RTV Request',
    back: 'M16-rtv',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Awaiting Approval', approved: 'Approved', shipped: 'Shipped',
      credited: 'Credited / Closed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Return to Vendor', note: 'A rejection at inspection raises this as a draft from its quarantine. Approve, then ship; shipping is M15\'s stock deduction.',
        fields: [
          { name: 'partner_id', required: true, label: 'Vendor', domain: [['fix_supplier_status', '!=', false]] },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'From Location' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'requested_on', required: true, label: 'Requested On' },
          { name: 'rtv_ref', label: 'RTV Reference' },
          { name: 'notes', label: 'Notes' }
        ] },
      { title: 'Goods Receipt, PO and Bill', note: 'The goods receipt the goods came in on (or why there is none): the AP credit note is raised on the bill of its PO.',
        fields: [
          { name: 'receipt_id', label: 'Goods Receipt (GRN)', domain: [['state', '=', 'posted']] },
          { name: 'no_receipt_reason', label: 'Why No Goods Receipt' },
          { name: 'purchase_order_id', label: 'Purchase Order', readonly: true },
          { name: 'vendor_invoice_ref', label: 'Vendor Bill', readonly: true }
        ] }
    ]
  },

  'M16-form-bid': {
    kind: 'model_form',
    model: 'fix.procurement.bid',
    title: 'Supplier Bid',
    back: 'M16-compare',
    status: { field: 'state', labels: {
      received: 'Received', awarded: 'Awarded', lost: 'Lost' } },
    sections: [
      { title: 'Bid', note: 'Bids are received only from a supplier invited to the RFQ, while it is open and before its response deadline; they stay sealed until it closes and cannot change afterwards. Record the terms as quoted so the bids compare on more than price, and attach the supplier\'s quotation.',
        fields: [
          { name: 'rfq_id', required: true, label: 'RFQ', domain: [['state', '=', 'open']] },
          { name: 'vendor_id', required: true, label: 'Vendor', domain: [['fix_supplier_status', '!=', false]] },
          { name: 'unit_price', required: true, label: 'Unit Price' },
          { name: 'lead_time_days', label: 'Lead Time (days)' },
          { name: 'warranty_months', label: 'Warranty (months)' },
          { name: 'moq', label: 'Minimum Order Qty' },
          { name: 'payment_terms', label: 'Payment Terms' },
          { name: 'incoterm', label: 'Incoterm' },
          { name: 'valid_until', label: 'Valid Until' },
          { name: 'quote_file', type: 'binary', filename: 'quote_filename', accept: '.pdf,.jpg,.jpeg,.png,.xlsx,.docx', label: 'Supplier\'s Quotation (copy)' },
          { name: 'quote_filename', label: 'Quotation File Name' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M16-form-award': {
    kind: 'model_form',
    model: 'fix.procurement.award',
    title: 'Award Decision',
    back: 'M16-award',
    status: { field: 'state', labels: { proposed: 'Proposed', decided: 'Decided', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Award', note: 'One live award per closed RFQ, never to an expired bid, an inactive supplier or the company itself. The lowest compliant bid is decided at once; any other bid needs a rationale, and fewer bids than the minimum an exception, decided by a Procurement Approver other than you.',
        fields: [
          { name: 'rfq_id', required: true, label: 'RFQ', domain: [['state', '=', 'closed']] },
          { name: 'bid_id', required: true, label: 'Winning Bid', domain: [['rfq_id.state', '=', 'closed'], ['state', '=', 'received']] },
          { name: 'decided_on', required: true, label: 'Decided On' },
          { name: 'rationale', label: 'Rationale (not the lowest bid)' },
          { name: 'exception_reason', label: 'Bid-Count Exception' }
        ] }
    ]
  },

  'M16-form-proforma': {
    kind: 'model_form',
    model: 'fix.purchase.proforma',
    title: 'Supplier Proforma Invoice',
    back: 'M16-proformas',
    status: { field: 'state', labels: {
      received: 'Received', approved: 'Approved', rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'pi', label: '1. Proforma', bn: '১. প্রফর্মা', icon: '🧾', badge: '7' },
      { id: 'totals', label: '2. Totals', bn: '২. মোট', icon: '৳', badge: '5' },
      { id: 'decision', label: '3. Order & Decision', bn: '৩. অর্ডার ও সিদ্ধান্ত', icon: '✔', badge: '6' }
    ],
    sections: [
      { tab: 'pi', title: 'Proforma', note: 'A local supplier\'s proforma invoice for one LOCAL purchase order, in the order\'s currency (BDT or USD). Leave the item lines empty to start from the order\'s lines, then adjust them to the supplier\'s PI and attach its copy. A Procurement Approver other than you approves it once the order is sent, when its goods value matches the order total, the PI adds up (lines + VAT + charges = total) and it has not expired; it is final once decided. An advance to the supplier is then requested against it.',
        fields: [
          { name: 'purchase_order_id', required: true, label: 'Local Purchase Order',
            domain: [['state', 'in', ['draft', 'sent', 'acknowledged', 'partially_received']], ['purchase_type', '=', 'local']],
            emptyNote: 'No open local purchase order yet. Raise the purchase order first (M16 Local Purchase Orders); a proforma is recorded against it. An import\'s proforma goes on its M44 import order.' },
          { name: 'proforma_no', required: true, label: 'Supplier\'s PI No' },
          { name: 'issued_on', required: true, label: 'PI Date' },
          { name: 'valid_until', label: 'Valid Until' },
          { name: 'payment_terms', label: 'Payment Terms (as on the PI)' },
          { name: 'pi_file', type: 'binary', filename: 'pi_filename', accept: '.pdf,.jpg,.jpeg,.png', label: 'Supplier\'s PI (copy)' },
          { name: 'pi_filename', label: 'PI File Name' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] },
      { tab: 'totals', title: 'Totals', note: 'Goods value is the sum of the lines; the PI total must equal goods + VAT + other charges.',
        fields: [
          { name: 'lines_total', readonly: true, label: 'Goods Value (lines)' },
          { name: 'vat_amount', label: 'VAT' },
          { name: 'other_charges', label: 'Other Charges' },
          { name: 'amount', required: true, label: 'PI Total (as printed)' },
          { name: 'computed_total', readonly: true, label: 'Goods + VAT + Charges' }
        ] },
      { tab: 'decision', title: 'Order & decision', note: 'Read from the order and the approval.',
        fields: [
          { name: 'vendor_id', readonly: true, label: 'Supplier' },
          { name: 'order_total', readonly: true, label: 'Order Total' },
          { name: 'currency_id', readonly: true, label: 'Currency' },
          { name: 'advance_approved', readonly: true, label: 'Advances Approved' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'rejection_reason', readonly: true, label: 'Rejection Reason' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'PI Lines — the supplier\'s items',
      note: 'One line per item on the supplier\'s PI. Each product must be on the purchase order, and never more than it orders.',
      fields: [
        { name: 'product_id', required: true, label: 'Product' },
        { name: 'supplier_part_no', label: 'Supplier\'s Item Code / Part No' },
        { name: 'description', label: 'Description' },
        { name: 'quantity', required: true, label: 'Qty' },
        { name: 'uom', label: 'Unit' },
        { name: 'unit_price', required: true, label: 'Unit Price' },
        { name: 'subtotal', readonly: true, label: 'Line Total' }
      ]
    }
  },

  'M16-form-advance': {
    kind: 'model_form',
    model: 'fix.purchase.advance',
    title: 'Supplier Advance',
    back: 'M16-advances',
    status: { field: 'state', labels: {
      draft: 'Draft', requested: 'Requested', approved: 'Approved', rejected: 'Rejected', cancelled: 'Cancelled',
      payment_requested: 'Payment Requested', paid: 'Paid' } },
    sections: [
      { title: 'Advance', note: 'Paid to the supplier before delivery, against its approved proforma. Save, then Request Approval from the list: a Procurement Approver other than you decides it. The order\'s approved advances never exceed the proforma, and above the advance cap the approver states why. Treasury (M50) makes and posts the payment.',
        fields: [
          { name: 'proforma_id', required: true, label: 'Against Proforma', domain: [['state', '=', 'approved']],
            emptyNote: 'No approved supplier proforma yet. Record the supplier\'s proforma on its purchase order and have it approved first.' },
          { name: 'amount', required: true, label: 'Advance Amount' },
          { name: 'purpose', label: 'Purpose' },
          { name: 'security_ref', label: 'Advance Security (cheque / bank guarantee) Ref' }
        ] },
      { title: 'Order & decision', note: 'Read from the proforma and the approval.',
        fields: [
          { name: 'purchase_order_id', readonly: true, label: 'Purchase Order' },
          { name: 'vendor_id', readonly: true, label: 'Supplier' },
          { name: 'proforma_amount', readonly: true, label: 'Proforma Amount' },
          { name: 'currency_id', readonly: true, label: 'Currency' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'decision_reason', readonly: true, label: 'Decision Reason' },
          { name: 'applied_amount', readonly: true, label: 'Taken Back on Bills' },
          { name: 'remaining_amount', readonly: true, label: 'Still to Take Back' },
          { name: 'payment_failure', readonly: true, label: 'Payment Problem (treasury)' }
        ] }
    ]
  },

  'M16-form-blanket': {
    kind: 'model_form',
    model: 'fix.procurement.blanket',
    title: 'Blanket Agreement',
    back: 'M16-blanket',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', expired: 'Expired', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Agreement', note: 'A Procurement Approver other than you activates the agreement; its cap and window are then fixed (Revise returns it to draft). Called off = the issued POs linked to it; a call-off beyond the cap or the window is refused at send. It expires by itself after its end date.',
        fields: [
          { name: 'vendor_id', required: true, label: 'Vendor', domain: [['fix_supplier_status', '=', 'active']], emptyNote: 'No supplier is active yet. A supplier becomes active in M42 Supplier Management once its trade licence, TIN and VAT documents are verified, it is screened, and a Supplier Approver activates it (BRU-PRO-02).' },
          { name: 'valid_from', required: true, label: 'Valid From' },
          { name: 'valid_to', required: true, label: 'Valid To' },
          { name: 'cap_amount', label: 'Cap Amount' }
        ] }
    ]
  },

  'M16-form-expedite': {
    kind: 'model_form',
    model: 'fix.procurement.expedite',
    title: 'Expediting Case',
    back: 'M16-expedite',
    status: { field: 'state', labels: {
      open: 'Open', chased: 'Chased', resolved: 'Resolved' } },
    sections: [
      { title: 'Case', note: 'Chase stamps the follow-up date; resolve records how the case was closed.',
        fields: [
          { name: 'purchase_order_id', required: true, label: 'Purchase Order', domain: [['state', 'in', ['sent', 'acknowledged', 'partially_received']]] },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'promised_date', label: 'Promised Date' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  /* FR-PRO-009: a supplier approved to supply a part */
  'M16-form-source': {
    kind: 'model_form',
    model: 'fix.procurement.approved.source',
    title: 'Approved Source',
    back: 'M16-sources',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', withdrawn: 'Withdrawn' } },
    sections: [
      { title: 'Source', note: 'A supplier approved to supply this part, first choice = priority 1. A Procurement Approver other than you approves it, once the supplier is active in M42; its terms are then fixed (withdraw it and propose a new one to change them). Approved sources fill an RFQ\'s invitations and the vendor of a requisition submitted without one.',
        fields: [
          { name: 'product_id', required: true, label: 'Part' },
          { name: 'vendor_id', required: true, label: 'Supplier', domain: [['fix_supplier_status', '=', 'active']],
            emptyNote: 'No supplier is active yet. A supplier becomes active in M42 Supplier Management.' },
          { name: 'priority', required: true, label: 'Priority (1 = first choice)' },
          { name: 'agreed_price', label: 'Agreed Unit Price' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'moq', label: 'Minimum Order Qty' },
          { name: 'lead_time_days', label: 'Lead Time (days)' },
          { name: 'valid_from', required: true, label: 'Valid From' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'notes', type: 'text', label: 'Notes' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'withdrawn_reason', readonly: true, label: 'Withdrawn Because' }
        ] }
    ]
  },

  /* FR-PRO-037 / BRU-PRO-19: the requester confirms a service delivered */
  'M16-form-service-entry': {
    kind: 'model_form',
    model: 'fix.purchase.service.entry',
    title: 'Service Entry',
    back: 'M16-service-entries',
    status: { field: 'state', labels: { draft: 'Draft', confirmed: 'Confirmed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Service Delivered', note: 'For a service or a non-stock purchase, which has no goods receipt. Pick the sent order and its line, state what was delivered (quantity, or milestone units) and attach the evidence. The requester of the purchase confirms it from the list (never its buyer); confirming posts the receipt the three-way match reads.',
        fields: [
          { name: 'purchase_order_id', required: true, label: 'Purchase Order', domain: [['state', 'in', ['sent', 'acknowledged', 'partially_received']]] },
          { name: 'po_line_id', required: true, label: 'Order Line',
            domain: [['order_id.state', 'in', ['sent', 'acknowledged', 'partially_received']], '|', ['product_id.type', '=', 'service'], ['order_id.requisition_id.purchase_kind', 'in', ['non_stock', 'service']]],
            emptyNote: 'No sent order has a service or non-stock line. A requisition for a service or non-stock purchase says so on its Source & Budget tab.' },
          { name: 'qty_confirmed', required: true, label: 'Quantity / Milestone Units Delivered' },
          { name: 'service_period', label: 'Period or Milestone' },
          { name: 'service_date', required: true, label: 'Delivered On' },
          { name: 'description', type: 'text', label: 'What Was Delivered' },
          { name: 'evidence_file', type: 'binary', filename: 'evidence_filename', accept: '.pdf,.jpg,.jpeg,.png', label: 'Evidence (job sheet, report, photos)' },
          { name: 'evidence_filename', label: 'Evidence File Name' },
          { name: 'qty_ordered', readonly: true, label: 'Ordered' },
          { name: 'qty_done_before', readonly: true, label: 'Already Confirmed' },
          { name: 'confirmed_by_id', readonly: true, label: 'Confirmed By' },
          { name: 'receipt_id', readonly: true, label: 'Receipt' }
        ] }
    ]
  },

  'M16-form-inspection': {
    kind: 'model_form',
    model: 'fix.procurement.inspection',
    title: 'Inspection Outcome',
    back: 'M16-inspection',
    status: { field: 'state', labels: { draft: 'Draft', done: 'Done' } },
    sections: [
      { title: 'Inspection', note: 'An inspection judges one posted goods-receipt line: the product and received quantity come from it, the outcome is derived (rejected = received − accepted), and only the accepted quantity can be invoiced. Confirming releases accepted goods into stock; rejected goods go to quarantine with a draft return to the vendor. Final once confirmed.',
        fields: [
          { name: 'receipt_line_id', required: true, label: 'Receipt Line', domain: [['state', '=', 'posted'], ['inspection_state', '=', 'pending']] },
          { name: 'qty_accepted', label: 'Accepted' },
          { name: 'inspected_on', required: true, label: 'Inspected On' },
          { name: 'inspector_id', label: 'Inspector' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M16:Spend by Category & Vendor': 'M16-rpt-spend',
  'M16:Match Exception Pareto': 'M16-rpt-match',
  'M16:OTD by Vendor': 'M16-rpt-otd',
  'M16:Price Variance Alert': 'M16-rpt-price',
  'M16:Maverick Spend': 'M16-rpt-maverick',
  'M16:PO Cycle Time': 'M16-rpt-cycle',
  'M16:GR/IR Reconciliation': 'M16-rpt-grir',
  'M16:Emergency Purchases': 'M16-rpt-emergency'
};

export const FORM_MODELS = {
  'M16:Purchase Requisition': 'fix.requisition',
  'M16:RFQ': 'fix.procurement.rfq',
  'M16:Purchase Order': 'fix.purchase.order',
  'M16:Import Purchase Order': 'fix.purchase.order',
  'M16:Supplier Proforma': 'fix.purchase.proforma',
  'M16:Supplier Advance': 'fix.purchase.advance',
  'M16:PO Goods Receipt': 'fix.purchase.receipt',
  'M16:RTV Request': 'fix.stock.rtv',
  'M16:Consolidated RFQ': 'fix.procurement.rfq',
  'M16:Supplier Bid': 'fix.procurement.bid',
  'M16:Award Decision': 'fix.procurement.award',
  'M16:Blanket Agreement': 'fix.procurement.blanket',
  'M16:Expediting Case': 'fix.procurement.expedite',
  'M16:Inspection Outcome': 'fix.procurement.inspection',
  'M16:Vendor Bill': 'fix.vendor.invoice',
  'M16:Approved Source': 'fix.procurement.approved.source',
  'M16:Service Entry': 'fix.purchase.service.entry',
  'M16:Match Exception Case': 'fix.ap.match.exception',
  'M16:Match Tolerance': 'fix.ap.match.tolerance'
};

export const FORM_CHIPS = {
  'M16:Purchase Requisition': 'M16-form-requisition',
  'M16:RFQ': 'M16-form-rfq',
  'M16:Purchase Order': 'M16-form-po',
  'M16:Import Purchase Order': 'M16-form-po-import',
  'M16:Supplier Proforma': 'M16-form-proforma',
  'M16:Supplier Advance': 'M16-form-advance',
  'M16:PO Goods Receipt': 'M16-form-po-receipt',
  'M16:RTV Request': 'M16-form-rtv',
  'M16:Consolidated RFQ': 'M16-form-rfq-consol',
  'M16:Supplier Bid': 'M16-form-bid',
  'M16:Award Decision': 'M16-form-award',
  'M16:Blanket Agreement': 'M16-form-blanket',
  'M16:Expediting Case': 'M16-form-expedite',
  'M16:Inspection Outcome': 'M16-form-inspection',
  /* the bill is M52's record: its own form, as on M52 Invoice Capture */
  'M16:Vendor Bill': 'M52-form-bill',
  'M16:Approved Source': 'M16-form-source',
  'M16:Service Entry': 'M16-form-service-entry',
  /* M52's records, on their own forms (BRU-PRO-09: the CFO sets tolerances) */
  'M16:Match Exception Case': 'M52-form-matchcase',
  'M16:Match Tolerance': 'M52-form-tolerance',
  'M16:__by_model__': {
    'fix.requisition': 'M16-form-requisition',
    'fix.procurement.rfq': 'M16-form-rfq',
    'fix.purchase.order': 'M16-form-po',
    'fix.purchase.proforma': 'M16-form-proforma',
    'fix.purchase.advance': 'M16-form-advance',
    'fix.purchase.receipt': 'M16-form-po-receipt',
    'fix.procurement.bid': 'M16-form-bid',
    'fix.procurement.award': 'M16-form-award',
    'fix.procurement.blanket': 'M16-form-blanket',
    'fix.procurement.expedite': 'M16-form-expedite',
    'fix.procurement.inspection': 'M16-form-inspection',
    'fix.stock.receipt': 'M16-form-grn',
    'fix.stock.rtv': 'M16-form-rtv',
    'fix.procurement.approved.source': 'M16-form-source',
    'fix.purchase.service.entry': 'M16-form-service-entry'
  },
  'M16:__by_screen__': {
    'M16-prs': 'M16-form-requisition',
    'M16-rfqs': 'M16-form-rfq',
    'M16-compare': 'M16-form-bid',
    'M16-award': 'M16-form-award',
    'M16-pos': 'M16-form-po',
    'M16-pos-import': 'M16-form-po-import',
    'M16-proformas': 'M16-form-proforma',
    'M16-advances': 'M16-form-advance',
    'M16-blanket': 'M16-form-blanket',
    'M16-expedite': 'M16-form-expedite',
    'M16-inspection': 'M16-form-inspection',
    'M16-po-receipts': 'M16-form-po-receipt',
    'M16-grn': 'M16-form-grn',
    'M16-rtv': 'M16-form-rtv',
    'M16-match-queue': 'M52-form-bill',
    'M16-sources': 'M16-form-source',
    'M16-service-entries': 'M16-form-service-entry',
    'M16-match-cases': 'M52-form-matchcase'
  }
};

export const CREATE = {
  M16: { screen: 'M16-form-requisition', model: 'fix.requisition', label: 'Purchase Requisition' }
};
