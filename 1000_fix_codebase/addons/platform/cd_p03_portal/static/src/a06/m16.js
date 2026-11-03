/** @odoo-module **/
/* A06 · Supply Chain — M16 Procurement & Sourcing (v2 rebuild).
 * Registry-faithful: 5 groups / 14 screens / 6 reports / 5 forms / freg 88.
 * Requisition/PO existed; RFQ+bids+awards, blankets, expediting, inspection
 * and the requisition→PO conversion are new. Receipts and RTV read M15's
 * documents (single-owner surfaces). */

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
      { id: 'M16-consol', en: 'Cross-Branch Consolidation', bn: 'শাখা একীকরণ', t: 'g' }
    ]},
    { en: 'Sourcing', screens: [
      { id: 'M16-rfqs', en: 'RFQ Events', bn: 'আরএফকিউ', t: 'g' },
      { id: 'M16-compare', en: 'Bid Comparison', bn: 'দর তুলনা', t: 'g' },
      { id: 'M16-award', en: 'Award Decisions', bn: 'অ্যাওয়ার্ড', t: 'g' }
    ]},
    { en: 'Orders', screens: [
      { id: 'M16-pos', en: 'Purchase Orders', bn: 'ক্রয়াদেশ', t: 'g' },
      { id: 'M16-blanket', en: 'Blanket / Call-Off', bn: 'ব্ল্যাংকেট অর্ডার', t: 'g' },
      { id: 'M16-expedite', en: 'Expediting Desk', bn: 'এক্সপিডাইটিং', t: 'g' }
    ]},
    { en: 'Receiving & Match', screens: [
      { id: 'M16-grn', en: 'Goods Receipts', bn: 'পণ্য গ্রহণ', t: 'c' },
      { id: 'M16-inspection', en: 'Inspection Outcomes', bn: 'পরিদর্শন ফলাফল', t: 'g' },
      { id: 'M16-match', en: '3-Way Match Workbench', bn: 'থ্রি-ওয়ে ম্যাচ', t: 'g' }
    ]},
    { en: 'Analysis', screens: [
      { id: 'M16-spend', en: 'Spend Analysis', bn: 'ব্যয় বিশ্লেষণ', t: 'r' },
      { id: 'M16-pricehist', en: 'Price History & Alerts', bn: 'মূল্যের ইতিহাস', t: 'r' },
      { id: 'M16-rtv', en: 'RTV Lifecycle', bn: 'ভেন্ডর ফেরত চক্র', t: 'g' }
    ]}
  ],
  reports: ['Spend by Category & Vendor', 'Match Exception Pareto', 'OTD by Vendor', 'Price Variance Alert', 'Maverick Spend', 'PO Cycle Time'],
  forms: ['Purchase Requisition', 'RFQ', 'Purchase Order', 'GRN', 'RTV Request'],
  cross: ['M43 planned orders', 'M42 supplier gate', 'M52 invoices', 'M44 imports', 'P05 vendor portal'],
  freg: { src: 88, sub: [
    ['1', 'Demand Intake', 8, { model: 'fix.requisition', cols: ['description', 'branch_id', 'requested_by', 'urgency', 'create_date'], screens: ['M16-prs'] }],
    ['2', 'Requisition & Approval', 10, { model: 'fix.requisition', cols: ['description', 'estimate_amount', 'urgency', 'state', 'purchase_order_id'], screens: ['M16-prs'] }],
    ['3', 'Consolidation', 6, { model: 'fix.requisition', cols: ['product_id', 'branch_id', 'qty', 'vendor_id', 'state'], screens: ['M16-consol'] }],
    ['4', 'RFQ & Bidding', 12, { model: 'fix.procurement.rfq', cols: ['name', 'product_id', 'qty', 'required_by', 'state'], screens: ['M16-rfqs', 'M16-compare', 'M16-award'] }],
    ['5', 'PO Lifecycle', 11, { model: 'fix.purchase.order', cols: ['name', 'vendor_id', 'date_order', 'amount_total', 'state'], screens: ['M16-pos'] }],
    ['6', 'Blanket Orders', 6, { model: 'fix.procurement.blanket', cols: ['name', 'vendor_id', 'valid_from', 'valid_to', 'cap_amount'], screens: ['M16-blanket'] }],
    ['7', 'Expediting', 7, { model: 'fix.procurement.expedite', cols: ['name', 'purchase_order_id', 'promised_date', 'follow_up_date', 'state'], screens: ['M16-expedite'] }],
    ['8', 'GRN & Inspection', 9, { model: 'fix.procurement.inspection', cols: ['name', 'receipt_ref', 'product_id', 'qty_accepted', 'outcome'], screens: ['M16-grn', 'M16-inspection', 'M16-rtv'] }],
    ['9', '3-Way Match', 10, { model: 'fix.vendor.invoice', cols: ['invoice_ref', 'vendor_id', 'requisition_id', 'match_state', 'total_payable'], screens: ['M16-match'] }],
    ['10', 'Spend Analysis', 9, { model: 'fix.purchase.order', cols: ['vendor_id', 'branch_id', 'date_order', 'amount_total', 'state'], screens: ['M16-spend', 'M16-pricehist'] }]
  ] }
};

export const SCREENS = {
  'M16-prs': { kind: 'model_list', model: 'fix.requisition', stateField: 'state',
    cols: ['description', 'branch_id', 'vendor_id', 'qty', 'estimate_amount', 'urgency', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_convert_to_po', l: 'Convert to PO' }
    ] },
  'M16-consol': { kind: 'table_report', module: 'M16', report: 'consolidation', title: 'Cross-Branch Consolidation', period: false },
  'M16-rfqs': { kind: 'model_list', model: 'fix.procurement.rfq', stateField: 'state',
    cols: ['name', 'description', 'product_id', 'qty', 'required_by', 'target_price', 'state'],
    actions: [
      { m: 'action_open', l: 'Open RFQ' },
      { m: 'action_close', l: 'Close RFQ' }
    ] },
  'M16-compare': { kind: 'model_list', model: 'fix.procurement.bid', stateField: 'state',
    cols: ['rfq_id', 'vendor_id', 'unit_price', 'lead_time_days', 'valid_until', 'state'] },
  'M16-award': { kind: 'model_list', model: 'fix.procurement.award', stateField: 'state',
    cols: ['name', 'rfq_id', 'bid_id', 'decided_on', 'rationale', 'state'] },
  'M16-pos': { kind: 'model_list', model: 'fix.purchase.order', stateField: 'state',
    cols: ['name', 'vendor_id', 'date_order', 'amount_total', 'state'],
    actions: [
      { m: 'action_send', l: 'Send PO' },
      { m: 'action_acknowledge', l: 'Acknowledge' }
    ] },
  'M16-blanket': { kind: 'model_list', model: 'fix.procurement.blanket', stateField: 'state',
    cols: ['name', 'vendor_id', 'valid_from', 'valid_to', 'cap_amount', 'consumed_amount', 'remaining_amount', 'state'] },
  'M16-expedite': { kind: 'model_list', model: 'fix.procurement.expedite', stateField: 'state',
    cols: ['name', 'purchase_order_id', 'reason', 'promised_date', 'follow_up_date', 'state'],
    actions: [
      { m: 'action_chase', l: 'Chase' },
      { m: 'action_resolve', l: 'Resolve' }
    ] },
  'M16-grn': { kind: 'model_list', model: 'fix.stock.receipt', stateField: 'state', create: false,
    cols: ['name', 'partner_id', 'location_id', 'received_on', 'state'] },
  'M16-inspection': { kind: 'model_list', model: 'fix.procurement.inspection', stateField: 'state',
    cols: ['name', 'receipt_ref', 'product_id', 'qty_received', 'qty_accepted', 'outcome', 'state'],
    actions: [{ m: 'action_confirm', l: 'Confirm Outcome' }] },
  'M16-match': { kind: 'table_report', module: 'M16', report: 'three_way', title: '3-Way Match Workbench', period: false },
  'M16-spend': { kind: 'table_report', module: 'M16', report: 'spend_by_category', title: 'Spend Analysis', period: false },
  'M16-pricehist': { kind: 'table_report', module: 'M16', report: 'price_history', title: 'Price History & Alerts', period: false },
  'M16-rtv': { kind: 'model_list', model: 'fix.stock.rtv', stateField: 'state', create: false,
    cols: ['name', 'partner_id', 'part_id', 'qty', 'reason', 'state'] },

  /* Report chips -> their own computed pack */
  'M16-rpt-spend': { kind: 'table_report', module: 'M16', report: 'spend_by_category', title: 'Spend by Category & Vendor', period: false },
  'M16-rpt-match': { kind: 'table_report', module: 'M16', report: 'match_exception', title: 'Match Exception Pareto', period: false },
  'M16-rpt-otd': { kind: 'table_report', module: 'M16', report: 'otd_by_vendor', title: 'OTD by Vendor', period: false },
  'M16-rpt-price': { kind: 'table_report', module: 'M16', report: 'price_variance', title: 'Price Variance Alert', period: false },
  'M16-rpt-maverick': { kind: 'table_report', module: 'M16', report: 'maverick_spend', title: 'Maverick Spend', period: false },
  'M16-rpt-cycle': { kind: 'table_report', module: 'M16', report: 'po_cycle_time', title: 'PO Cycle Time', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M16-form-requisition': {
    kind: 'model_form',
    model: 'fix.requisition',
    title: 'Purchase Requisition',
    back: 'M16-prs',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', converted: 'Converted to PO', rejected: 'Rejected' } },
    sections: [
      { title: 'Request', note: 'Approve, then Convert to PO: the conversion needs a product, quantity and vendor and keeps the requisition link for maverick-spend analysis.',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'product_id', label: 'Product' },
          { name: 'qty', label: 'Quantity' },
          { name: 'vendor_id', label: 'Preferred Vendor' },
          { name: 'estimate_amount', label: 'Estimated Amount' },
          { name: 'urgency', required: true, label: 'Urgency' },
          { name: 'requested_by', required: true, label: 'Requested By' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
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
      { title: 'RFQ', note: 'Open the event, record supplier bids, then award one; awarding marks the other bids lost.',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'qty', label: 'Quantity' },
          { name: 'required_by', label: 'Required By' },
          { name: 'target_price', label: 'Target Price' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M16-form-po': {
    kind: 'model_form',
    model: 'fix.purchase.order',
    title: 'Purchase Order',
    back: 'M16-pos',
    status: { field: 'state', labels: {
      draft: 'Draft', sent: 'Sent', acknowledged: 'Acknowledged',
      partially_received: 'Partially Received', received: 'Received',
      closed: 'Closed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Order', note: 'The PO is the ordered side of the three-way match. Send it, then the vendor acknowledges.',
        fields: [
          { name: 'vendor_id', required: true, label: 'Vendor' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'branch_id', label: 'Deliver-to Branch' },
          { name: 'date_order', required: true, label: 'Order Date' },
          { name: 'promised_date', label: 'Promised Date' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Order Lines',
      note: 'Ordered quantity must be positive; the received quantity can never exceed it.',
      fields: [
        { name: 'product_id', required: true, label: 'Product' },
        { name: 'description', label: 'Description' },
        { name: 'qty_ordered', required: true, label: 'Ordered' },
        { name: 'unit_price', required: true, label: 'Unit Price' }
      ]
    }
  },

  'M16-form-grn': {
    kind: 'model_form',
    model: 'fix.stock.receipt',
    title: 'GRN',
    back: 'M16-grn',
    status: { field: 'state', labels: {
      draft: 'Draft', inspected: 'Inspected', posted: 'Posted' } },
    sections: [
      { title: 'Goods Receipt', note: 'The inspection gate is M15\'s: accepted quantity per line, then Inspect and Post from the receipts screen.',
        fields: [
          { name: 'partner_id', required: true, label: 'Supplier' },
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
      draft: 'Draft', approved: 'Approved', shipped: 'Shipped' } },
    sections: [
      { title: 'Return to Vendor', note: 'Approve, then ship; shipping is M15\'s stock deduction.',
        fields: [
          { name: 'partner_id', required: true, label: 'Vendor' },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'From Location' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'requested_on', required: true, label: 'Requested On' },
          { name: 'rtv_ref', label: 'RTV Reference' },
          { name: 'notes', label: 'Notes' }
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
      { title: 'Bid', note: 'One bid per vendor per RFQ; price and lead time are the comparison basis.',
        fields: [
          { name: 'rfq_id', required: true, label: 'RFQ' },
          { name: 'vendor_id', required: true, label: 'Vendor' },
          { name: 'unit_price', required: true, label: 'Unit Price' },
          { name: 'lead_time_days', label: 'Lead Time (days)' },
          { name: 'valid_until', label: 'Valid Until' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M16-form-award': {
    kind: 'model_form',
    model: 'fix.procurement.award',
    title: 'Award Decision',
    back: 'M16-award',
    status: { field: 'state', labels: { decided: 'Decided', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Award', note: 'Saving an award marks the winning bid awarded, the others lost, and the RFQ awarded.',
        fields: [
          { name: 'rfq_id', required: true, label: 'RFQ' },
          { name: 'bid_id', required: true, label: 'Winning Bid' },
          { name: 'decided_on', required: true, label: 'Decided On' },
          { name: 'rationale', label: 'Rationale' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M16-form-blanket': {
    kind: 'model_form',
    model: 'fix.procurement.blanket',
    title: 'Blanket Agreement',
    back: 'M16-blanket',
    status: { field: 'state', labels: {
      active: 'Active', expired: 'Expired', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Agreement', note: 'Consumed is the total of this vendor\'s non-cancelled POs inside the window — computed, not typed.',
        fields: [
          { name: 'vendor_id', required: true, label: 'Vendor' },
          { name: 'valid_from', required: true, label: 'Valid From' },
          { name: 'valid_to', required: true, label: 'Valid To' },
          { name: 'cap_amount', label: 'Cap Amount' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Case', note: 'Chase stamps the follow-up date; resolve closes the case.',
        fields: [
          { name: 'purchase_order_id', required: true, label: 'Purchase Order' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'promised_date', label: 'Promised Date' },
          { name: 'follow_up_date', label: 'Follow-up Date' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', type: 'text', label: 'Notes' }
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
      { title: 'Inspection', note: 'Rejected = received − accepted; the receipt itself stays M15\'s document.',
        fields: [
          { name: 'receipt_ref', required: true, label: 'Receipt Reference' },
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'qty_received', label: 'Received' },
          { name: 'qty_accepted', label: 'Accepted' },
          { name: 'outcome', required: true, label: 'Outcome' },
          { name: 'inspected_on', required: true, label: 'Inspected On' },
          { name: 'inspector_id', label: 'Inspector' },
          { name: 'state', required: true, label: 'State' },
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
  'M16:PO Cycle Time': 'M16-rpt-cycle'
};

export const FORM_MODELS = {
  'M16:Purchase Requisition': 'fix.requisition',
  'M16:RFQ': 'fix.procurement.rfq',
  'M16:Purchase Order': 'fix.purchase.order',
  'M16:GRN': 'fix.stock.receipt',
  'M16:RTV Request': 'fix.stock.rtv'
};

export const FORM_CHIPS = {
  'M16:Purchase Requisition': 'M16-form-requisition',
  'M16:RFQ': 'M16-form-rfq',
  'M16:Purchase Order': 'M16-form-po',
  'M16:GRN': 'M16-form-grn',
  'M16:RTV Request': 'M16-form-rtv',
  'M16:__by_model__': {
    'fix.requisition': 'M16-form-requisition',
    'fix.procurement.rfq': 'M16-form-rfq',
    'fix.purchase.order': 'M16-form-po',
    'fix.procurement.bid': 'M16-form-bid',
    'fix.procurement.award': 'M16-form-award',
    'fix.procurement.blanket': 'M16-form-blanket',
    'fix.procurement.expedite': 'M16-form-expedite',
    'fix.procurement.inspection': 'M16-form-inspection',
    'fix.stock.receipt': 'M16-form-grn',
    'fix.stock.rtv': 'M16-form-rtv'
  },
  'M16:__by_screen__': {
    'M16-prs': 'M16-form-requisition',
    'M16-rfqs': 'M16-form-rfq',
    'M16-pos': 'M16-form-po',
    'M16-blanket': 'M16-form-blanket',
    'M16-expedite': 'M16-form-expedite',
    'M16-inspection': 'M16-form-inspection',
    'M16-grn': 'M16-form-grn',
    'M16-rtv': 'M16-form-rtv'
  }
};

export const CREATE = {
  M16: { screen: 'M16-form-requisition', model: 'fix.requisition', label: 'Purchase Requisition' }
};
