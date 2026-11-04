/** @odoo-module **/
/* A06 · Supply Chain — M44 Import, Trade Compliance & Landed Cost (v2 rebuild).
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 4 forms / freg 64.
 * The import order existed; proforma/LC/LCA, HS, IRC, shipping documents,
 * arrivals, bills of entry with the duty cascade and landed-cost sheets are new. */

export const MODULE = {
  area: 'A06', code: 'M44', en: 'Import & Trade Compliance', title: 'M44 · Import & Trade Compliance',
  bn: 'আমদানি ও বাণিজ্য কমপ্লায়েন্স', icon: '🚢',
  desc: 'Import orders with incoterms and FX, proforma invoices, letters of credit and LCA, HS classification, IRC and restrictions, shipping documents, arrival and port handling, ASYCUDA bills of entry with the CD/RD/SD/VAT/AT/AIT cascade, landed-cost allocation and C&F management.',
  kpis: [
    { l: 'Open Imports', m: 'open_imports' },
    { l: 'LCs Open', m: 'lc_open' },
    { l: 'BOE Unpaid', m: 'boe_unpaid' },
    { l: 'Demurrage Days', m: 'demurrage_days' },
    { l: 'Landed Cost MTD', m: 'landed_mtd', prefix: '৳ ' },
    { l: 'Open FX Commitment', m: 'fx_commitment', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Orders & Finance', screens: [
      { id: 'M44-orders', en: 'Import Orders', bn: 'আমদানি অর্ডার', t: 'g' },
      { id: 'M44-proforma', en: 'Proforma Invoices', bn: 'প্রফর্মা ইনভয়েস', t: 'g' },
      { id: 'M44-lc', en: 'Letters of Credit', bn: 'এলসি', t: 'g' },
      { id: 'M44-lc-amend', en: 'LC Amendments', bn: 'এলসি সংশোধন', t: 'g' },
      { id: 'M44-lc-pay', en: 'LC Payments', bn: 'এলসি পেমেন্ট', t: 'g' },
      { id: 'M44-incoterms', en: 'Incoterms & FX', bn: 'ইনকোটার্ম ও এফএক্স', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M44-tariff', en: 'HS Tariff Master', bn: 'শুল্ক তালিকা', t: 'g' },
      { id: 'M44-hs', en: 'HS Classification', bn: 'এইচএস শ্রেণিবিন্যাস', t: 'g' },
      { id: 'M44-irc', en: 'IRC & Restrictions', bn: 'আইআরসি', t: 'g' },
      { id: 'M44-restriction', en: 'Restricted & Prohibited Goods', bn: 'নিয়ন্ত্রিত পণ্য', t: 'g' },
      { id: 'M44-permit', en: 'Import Permits', bn: 'আমদানি অনুমতিপত্র', t: 'g' },
      { id: 'M44-lca', en: 'LCA via Dealer Bank', bn: 'এলসিএ', t: 'g' }
    ]},
    { en: 'Shipping & Customs', screens: [
      { id: 'M44-docs', en: 'Shipping Documents', bn: 'শিপিং নথি', t: 'g' },
      { id: 'M44-insurance', en: 'Cargo Insurance', bn: 'কার্গো বীমা', t: 'g' },
      { id: 'M44-agent', en: 'C&F Agents', bn: 'সিএন্ডএফ এজেন্ট', t: 'g' },
      { id: 'M44-arrival', en: 'Arrival & Port Handling', bn: 'আগমন ও বন্দর', t: 'g' },
      { id: 'M44-boe', en: 'Bill of Entry (ASYCUDA)', bn: 'বিল অব এন্ট্রি', t: 'g' },
      { id: 'M44-duty', en: 'Duty Cascade (CD/RD/SD/VAT/AT/AIT)', bn: 'শুল্ক ক্যাসকেড', t: 'g' }
    ]},
    { en: 'Costing', screens: [
      { id: 'M44-landed', en: 'Landed Cost Allocation', bn: 'ল্যান্ডেড কস্ট', t: 'g' },
      { id: 'M44-cf', en: 'C&F Management', bn: 'সিএন্ডএফ ম্যানেজমেন্ট', t: 'g' }
    ]}
  ],
  reports: ['Landed Cost by Shipment', 'Duty & Tax Cascade', 'Cycle-Time Analysis', 'Demurrage Avoidance', 'FX Exposure'],
  forms: ['Import Order', 'LC Application', 'HS Ruling Request', 'Bill of Entry'],
  cross: ['M16 import POs', 'M50 trade finance', 'M51 import VAT/duty', 'M15 landed cost'],
  freg: { src: 64, sub: [
    ['1', 'Import Order Lifecycle', 9, { model: 'fix.import.order', cols: ['name', 'supplier_id', 'incoterm', 'fob_value', 'state'], screens: ['M44-orders', 'M44-proforma'] }],
    ['2', 'LC & Payments', 10, { model: 'fix.import.lc', cols: ['lc_no', 'order_id', 'bank', 'amount', 'state'], screens: ['M44-lc', 'M44-incoterms'] }],
    ['3', 'HS Classification', 7, { model: 'fix.import.hs', cols: ['product_id', 'hs_code', 'description', 'cd_pct', 'state'], screens: ['M44-hs'] }],
    ['4', 'Eligibility & IRC', 5, { model: 'fix.import.irc', cols: ['irc_no', 'issued_on', 'valid_to', 'is_valid', 'state'], screens: ['M44-irc', 'M44-lca'] }],
    ['5', 'Shipping & Insurance', 8, { model: 'fix.import.shipdoc', cols: ['name', 'order_id', 'doc_type', 'ref', 'state'], screens: ['M44-docs'] }],
    ['6', 'Port & Customs', 9, { model: 'fix.import.arrival', cols: ['name', 'order_id', 'vessel', 'arrival_date', 'demurrage_days'], screens: ['M44-arrival', 'M44-boe', 'M44-cf'] }],
    ['7', 'Duty Computation', 8, { model: 'fix.import.boe', cols: ['boe_no', 'order_id', 'cd_amount', 'vat_amount', 'total_tax'], screens: ['M44-duty', 'M44-boe'] }],
    ['8', 'Landed Cost', 8, { model: 'fix.import.landed', cols: ['name', 'order_id', 'freight', 'duty', 'total_landed'], screens: ['M44-landed'] }]
  ] }
};

export const SCREENS = {
  'M44-orders': { kind: 'model_list', model: 'fix.import.order', stateField: 'state',
    cols: ['name', 'supplier_id', 'incoterm', 'fob_value', 'customs_duty', 'landed_cost', 'state'],
    actions: [{ m: 'action_receive', l: 'Receive into Stock' }] },
  'M44-proforma': { kind: 'model_list', model: 'fix.import.proforma', stateField: 'state',
    cols: ['proforma_no', 'order_id', 'currency_id', 'amount', 'issued_on', 'valid_until', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve Proforma' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M44-lc': { kind: 'model_list', model: 'fix.import.lc', stateField: 'state',
    cols: ['lc_no', 'order_id', 'bank', 'amount', 'paid_amount', 'expiry', 'approval_state', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply' },
      { m: 'action_request_approval', l: 'Request Approval' },
      { m: 'action_recall_approval', l: 'Recall Approval' },
      { m: 'action_open', l: 'Open LC' },
      { m: 'action_close', l: 'Close LC' }
    ] },
  'M44-lc-amend': { kind: 'model_list', model: 'fix.import.lc.amendment', stateField: 'state',
    cols: ['name', 'lc_id', 'old_amount', 'new_amount', 'new_expiry', 'reason', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval' },
      { m: 'action_recall_approval', l: 'Recall Approval' },
      { m: 'action_apply_amendment', l: 'Apply Amendment' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M44-lc-pay': { kind: 'model_list', model: 'fix.import.lc.payment',
    cols: ['lc_id', 'payment_date', 'amount', 'reference', 'recorded_by_id'] },
  'M44-incoterms': { kind: 'table_report', module: 'M44', report: 'incoterms_fx', title: 'Incoterms & FX', period: false },
  'M44-tariff': { kind: 'model_list', model: 'fix.import.tariff', stateField: 'state',
    cols: ['hs_code', 'sro_ref', 'date_from', 'date_to', 'cd_pct', 'rd_pct', 'sd_pct', 'vat_pct', 'at_pct', 'ait_pct', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_retire', l: 'Retire' }
    ] },
  'M44-hs': { kind: 'model_list', model: 'fix.import.hs', stateField: 'state',
    cols: ['product_id', 'hs_code', 'ruling_ref', 'cd_pct', 'rd_pct', 'sd_pct', 'vat_pct', 'ruled_by_id', 'state'],
    actions: [
      { m: 'action_rule', l: 'Rule' },
      { m: 'action_reopen', l: 'Reopen for Reclassification' }
    ] },
  'M44-irc': { kind: 'model_list', model: 'fix.import.irc', stateField: 'state',
    cols: ['irc_no', 'company_id', 'issued_on', 'valid_to', 'is_valid', 'state'],
    actions: [
      { m: 'action_suspend', l: 'Suspend' },
      { m: 'action_reinstate', l: 'Reinstate' }
    ] },
  'M44-lca': { kind: 'model_list', model: 'fix.import.lca', stateField: 'state',
    cols: ['lca_no', 'lc_id', 'bank', 'amount', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve LCA' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M44-docs': { kind: 'model_list', model: 'fix.import.shipdoc', stateField: 'state',
    cols: ['name', 'order_id', 'doc_type', 'ref', 'received_on', 'state'],
    actions: [
      { m: 'action_receive', l: 'Mark Received' },
      { m: 'action_verify', l: 'Verify' }
    ] },
  'M44-arrival': { kind: 'model_list', model: 'fix.import.arrival', stateField: 'state',
    cols: ['name', 'order_id', 'vessel', 'eta', 'arrival_date', 'demurrage_days', 'release_ref', 'state'],
    actions: [
      { m: 'action_arrive', l: 'Mark Arrived' },
      { m: 'action_clear', l: 'Clear' }
    ] },
  'M44-boe': { kind: 'model_list', model: 'fix.import.boe', stateField: 'state',
    cols: ['boe_no', 'order_id', 'boe_date', 'total_tax', 'customs_assessed_total', 'duty_variance', 'state'],
    actions: [
      { m: 'action_assess', l: 'Assess' },
      { m: 'action_pay', l: 'Pay Duty' },
      { m: 'action_reverse', l: 'Reverse' }
    ] },
  'M44-duty': { kind: 'table_report', module: 'M44', report: 'duty_cascade', title: 'Duty Cascade', period: false },
  'M44-landed': { kind: 'model_list', model: 'fix.import.landed', stateField: 'state',
    cols: ['name', 'order_id', 'sheet_type', 'freight', 'insurance', 'duty', 'clearing_charges', 'total_landed', 'state'],
    actions: [
      { m: 'action_post_estimate', l: 'Post Estimate' },
      { m: 'action_finalise', l: 'Finalise Sheet' }
    ] },
  'M44-cf': { kind: 'table_report', module: 'M44', report: 'cnf_management', title: 'C&F Management', period: false },

  /* Report chips -> their own computed pack */
  'M44-rpt-landed': { kind: 'table_report', module: 'M44', report: 'landed_cost_by_shipment', title: 'Landed Cost by Shipment', period: false },
  'M44-rpt-duty': { kind: 'table_report', module: 'M44', report: 'duty_cascade', title: 'Duty & Tax Cascade', period: false },
  'M44-rpt-cycle': { kind: 'table_report', module: 'M44', report: 'cycle_time', title: 'Cycle-Time Analysis', period: false },
  'M44-rpt-demurrage': { kind: 'table_report', module: 'M44', report: 'demurrage_avoidance', title: 'Demurrage Avoidance', period: false },
  'M44-rpt-fx': { kind: 'table_report', module: 'M44', report: 'fx_exposure', title: 'Open FX Commitments', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============
   * A06 audit M44-6: no form offers a state, approval, evidence or stamp
   * field; those change only through the actions above. */
  'M44-form-order': {
    kind: 'model_form',
    model: 'fix.import.order',
    title: 'Import Order',
    back: 'M44-orders',
    status: { field: 'state', labels: {
      draft: 'Draft', shipped: 'Shipped', customs: 'In Customs', cleared: 'Cleared by Customs',
      received: 'Received', landed: 'Landed Cost Applied' } },
    sections: [
      { title: 'Order', note: 'The currency, FX rate (with its source), incoterm, FOB and lines are pinned once the proforma is approved; freight and insurance once a Bill of Entry is assessed.',
        fields: [
          { name: 'name', required: true, label: 'Order Reference' },
          { name: 'supplier_id', label: 'Supplier' },
          { name: 'purchase_order_id', label: 'Purchase Order (M16)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'country_origin', label: 'Country of Origin' },
          { name: 'incoterm', label: 'Incoterm' },
          { name: 'shipment_mode', label: 'Shipment Mode' },
          { name: 'currency_id', label: 'Currency' },
          { name: 'fx_rate', label: 'FX Rate' },
          { name: 'fx_rate_source', label: 'FX Rate Source' },
          { name: 'fx_rate_date', label: 'FX Rate Date' },
          { name: 'fob_value', label: 'FOB Value' },
          { name: 'freight_cost', label: 'Freight' },
          { name: 'insurance_cost', label: 'Insurance' },
          { name: 'location_id', label: 'Receiving Location' },
          { name: 'customs_duty', readonly: true, label: 'Customs Duty (from paid B/E)' },
          { name: 'landed_cost', readonly: true, label: 'Landed Cost' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Lines — what is imported',
      note: 'The receipt, the assessable value and the landed-cost allocation read these lines.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'description', label: 'Description' },
        { name: 'hs_id', label: 'HS Classification' },
        { name: 'quantity', required: true, label: 'Quantity' },
        { name: 'unit_price', required: true, label: 'Unit Price' }
      ]
    }
  },

  'M44-form-proforma': {
    kind: 'model_form',
    model: 'fix.import.proforma',
    title: 'Proforma Invoice',
    back: 'M44-proforma',
    status: { field: 'state', labels: {
      received: 'Received', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Proforma', note: 'Approved by an Import Approver who did not record it, against the order value and a valid IRC.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'proforma_no', required: true, label: 'Proforma No' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'amount', label: 'Amount' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'valid_until', label: 'Valid Until' }
        ] }
    ]
  },

  'M44-form-lc': {
    kind: 'model_form',
    model: 'fix.import.lc',
    title: 'LC Application',
    back: 'M44-lc',
    status: { field: 'state', labels: {
      draft: 'Draft', applied: 'Applied', opened: 'Opened',
      amended: 'Amended', closed: 'Closed' } },
    sections: [
      { title: 'Letter of Credit', note: 'Apply, request approval (routed by amount to an Import Approver with the DOFA tier), then open. An opened LC changes only through an amendment.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'lc_no', required: true, label: 'LC No' },
          { name: 'bank', label: 'Issuing Bank' },
          { name: 'facility_id', required: true, label: 'LC Facility (M50)' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'amount', label: 'LC Amount' },
          { name: 'expiry', label: 'Expiry' },
          { name: 'margin_pct', label: 'Margin %' },
          { name: 'dofa_justification', type: 'text', label: 'Justification' },
          { name: 'paid_amount', readonly: true, label: 'Paid' }
        ] }
    ]
  },

  'M44-form-lc-amend': {
    kind: 'model_form',
    model: 'fix.import.lc.amendment',
    title: 'LC Amendment',
    back: 'M44-lc-amend',
    status: { field: 'state', labels: { draft: 'Draft', applied: 'Applied', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Amendment', note: 'Approved at the authority band of the NEW total (BRU-ITC-20), then applied.',
        fields: [
          { name: 'lc_id', required: true, label: 'Letter of Credit' },
          { name: 'new_amount', label: 'New LC Amount' },
          { name: 'new_expiry', label: 'New Expiry' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'dofa_justification', type: 'text', label: 'Justification' }
        ] }
    ]
  },

  'M44-form-lc-pay': {
    kind: 'model_form',
    model: 'fix.import.lc.payment',
    title: 'LC Payment',
    back: 'M44-lc-pay',
    sections: [
      { title: 'Payment', note: 'Finance only. Payments never exceed the LC; a recorded payment is final.',
        fields: [
          { name: 'lc_id', required: true, label: 'Letter of Credit' },
          { name: 'payment_date', required: true, label: 'Payment Date' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'reference', required: true, label: 'Bank Reference' }
        ] }
    ]
  },

  'M44-form-lca': {
    kind: 'model_form',
    model: 'fix.import.lca',
    title: 'LCA',
    back: 'M44-lca',
    status: { field: 'state', labels: {
      applied: 'Applied', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'LCA', fields: [
          { name: 'lc_id', required: true, label: 'Letter of Credit' },
          { name: 'lca_no', required: true, label: 'LCA No' },
          { name: 'bank', label: 'Dealer Bank' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'amount', label: 'Amount' }
        ] }
    ]
  },

  'M44-form-tariff': {
    kind: 'model_form',
    model: 'fix.import.tariff',
    title: 'Tariff Rate',
    back: 'M44-tariff',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    sections: [
      { title: 'Tariff row', note: 'Rates are entered from the operative tariff and SRO; activated by an Import Approver who did not enter them, then frozen. A new rate is a new row with its own effective date.',
        fields: [
          { name: 'hs_code', required: true, label: 'HS Code' },
          { name: 'description', label: 'Description' },
          { name: 'sro_ref', required: true, label: 'SRO / Tariff Reference' },
          { name: 'date_from', required: true, label: 'Effective From' },
          { name: 'date_to', label: 'Effective To' },
          { name: 'cd_pct', label: 'CD %' },
          { name: 'rd_pct', label: 'RD %' },
          { name: 'sd_pct', label: 'SD %' },
          { name: 'vat_pct', label: 'VAT %' },
          { name: 'at_pct', label: 'AT %' },
          { name: 'ait_pct', label: 'AIT %' }
        ] }
    ]
  },

  'M44-form-hs': {
    kind: 'model_form',
    model: 'fix.import.hs',
    title: 'HS Ruling Request',
    back: 'M44-hs',
    status: { field: 'state', labels: { draft: 'Draft', ruled: 'Ruled' } },
    sections: [
      { title: 'Classification', note: 'Ruled by an Import Approver who did not classify it. The rates are the tariff row in force, never typed here.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'hs_code', required: true, label: 'HS Code' },
          { name: 'description', label: 'Description' },
          { name: 'ruling_ref', label: 'Ruling Reference' },
          { name: 'cd_pct', readonly: true, label: 'CD %' },
          { name: 'rd_pct', readonly: true, label: 'RD %' },
          { name: 'sd_pct', readonly: true, label: 'SD %' },
          { name: 'vat_pct', readonly: true, label: 'VAT %' },
          { name: 'at_pct', readonly: true, label: 'AT %' },
          { name: 'ait_pct', readonly: true, label: 'AIT %' }
        ] }
    ]
  },

  'M44-form-irc': {
    kind: 'model_form',
    model: 'fix.import.irc',
    title: 'IRC Register',
    back: 'M44-irc',
    status: { field: 'state', labels: {
      valid: 'Valid', expired: 'Expired', suspended: 'Suspended' } },
    sections: [
      { title: 'IRC', note: 'Validity is computed from the state and the end date on every read; a daily job expires lapsed certificates. A renewal is a new certificate.',
        fields: [
          { name: 'irc_no', required: true, label: 'IRC No' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'restrictions', type: 'text', label: 'Restrictions' },
          { name: 'is_valid', readonly: true, label: 'Valid Today' }
        ] }
    ]
  },

  'M44-form-shipdoc': {
    kind: 'model_form',
    model: 'fix.import.shipdoc',
    title: 'Shipping Document',
    back: 'M44-docs',
    status: { field: 'state', labels: {
      pending: 'Pending', received: 'Received', verified: 'Verified' } },
    sections: [
      { title: 'Document', fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'doc_type', required: true, label: 'Document Type' },
          { name: 'ref', label: 'Document Reference' },
          { name: 'received_on', required: true, label: 'Received On' }
        ] }
    ]
  },

  'M44-form-arrival': {
    kind: 'model_form',
    model: 'fix.import.arrival',
    title: 'Shipment Arrival',
    back: 'M44-arrival',
    status: { field: 'state', labels: {
      in_transit: 'In Transit', arrived: 'Arrived', cleared: 'Cleared' } },
    sections: [
      { title: 'Arrival', note: 'Free time runs from the actual arrival; demurrage is computed to release. Clearance needs a paid Bill of Entry and the customs release order number.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'vessel', label: 'Vessel / Flight' },
          { name: 'bl_no', label: 'B/L No' },
          { name: 'port', label: 'Port' },
          { name: 'etd', label: 'ETD' },
          { name: 'eta', label: 'ETA' },
          { name: 'free_days', label: 'Free Days' },
          { name: 'cnf_agent_id', label: 'C&F Agent' },
          { name: 'release_ref', label: 'Customs Release Order No' },
          { name: 'demurrage_days', readonly: true, label: 'Demurrage Days' }
        ] }
    ]
  },

  'M44-form-boe': {
    kind: 'model_form',
    model: 'fix.import.boe',
    title: 'Bill of Entry',
    back: 'M44-boe',
    status: { field: 'state', labels: {
      draft: 'Draft', assessed: 'Assessed', paid: 'Paid', reversed: 'Reversed' } },
    sections: [
      { title: 'Bill of Entry', note: 'Assessed with the document checklist complete; paid by Finance with the payment reference once the customs-assessed total agrees. A paid Bill of Entry is final: a correction is a reversal.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'boe_no', required: true, label: 'Bill of Entry No' },
          { name: 'asycuda_ref', label: 'ASYCUDA Reference' },
          { name: 'cnf_agent_id', label: 'C&F Agent' },
          { name: 'boe_date', required: true, label: 'Lodgement Date' },
          { name: 'customs_assessed_total', label: 'Customs Assessed Total' },
          { name: 'payment_ref', label: 'Duty Payment Reference' },
          { name: 'reversal_reason', label: 'Reversal Reason' },
          { name: 'total_tax', readonly: true, label: 'Computed Duty & Tax' },
          { name: 'duty_variance', readonly: true, label: 'Variance vs Customs' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'BOE Lines — duty cascade per line',
      note: 'Each line is a line of the import order; the assessable value (CIF × FX + landing charge), the rates (tariff in force on the lodgement date) and the amounts are computed, never typed.',
      fields: [
        { name: 'order_line_id', required: true, label: 'Import Order Line' },
        { name: 'quantity', required: true, label: 'Quantity' },
        { name: 'description', label: 'Description' }
      ]
    }
  },

  'M44-form-landed': {
    kind: 'model_form',
    model: 'fix.import.landed',
    title: 'Landed Cost Sheet',
    back: 'M44-landed',
    status: { field: 'state', labels: { draft: 'Draft', estimated: 'Estimate Posted', finalised: 'Finalised' } },
    sections: [
      { title: 'Landed Cost', note: 'An estimate is posted at shipment and valued into stock at receipt. The final sheet takes CD + RD + SD from the paid Bills of Entry (VAT, AT and AIT are recoverable, never capitalised), is finalised by an Import Approver who did not prepare it, revalues the stock and posts the true-up.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'sheet_type', required: true, label: 'Sheet Type' },
          { name: 'freight', label: 'Freight' },
          { name: 'insurance', label: 'Insurance' },
          { name: 'clearing_charges', label: 'Clearing, Port & C&F' },
          { name: 'duty_estimate', label: 'Estimated CD + RD + SD (estimate only)' },
          { name: 'allocation_method', required: true, label: 'Allocation Method' },
          { name: 'duty', readonly: true, label: 'Duty (CD + RD + SD)' },
          { name: 'total_landed', readonly: true, label: 'Total Landed' }
        ] }
    ]
  },

  /* ---- BRU-ITC-10 / -12 / -13 compliance masters ---- */
  'M44-restriction': { kind: 'model_list', model: 'fix.import.restriction', stateField: 'state',
    cols: ['name', 'hs_code_pattern', 'product_id', 'restriction_type', 'permit_type', 'date_from', 'date_to', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_retire', l: 'Retire' }
    ] },
  'M44-permit': { kind: 'model_list', model: 'fix.import.permit', stateField: 'state',
    cols: ['order_id', 'restriction_id', 'permit_no', 'issuer', 'valid_to', 'verified_by_id', 'state'],
    actions: [
      { m: 'action_verify', l: 'Verify' },
      { m: 'action_revoke', l: 'Revoke' }
    ] },
  'M44-agent': { kind: 'model_list', model: 'fix.import.cnf.agent', stateField: 'state',
    cols: ['name', 'supplier_id', 'licence_no', 'licence_expiry', 'is_usable', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_block', l: 'Block' },
      { m: 'action_unblock', l: 'Unblock' }
    ] },
  'M44-insurance': { kind: 'model_list', model: 'fix.import.insurance', stateField: 'state',
    cols: ['order_id', 'insurer_id', 'policy_no', 'sum_insured', 'premium', 'cover_from', 'cover_to', 'state'],
    actions: [
      { m: 'action_verify', l: 'Verify Cover' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },

  'M44-form-restriction': {
    kind: 'model_form',
    model: 'fix.import.restriction',
    title: 'Import Restriction',
    back: 'M44-restriction',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    sections: [
      { title: 'Restriction', note: 'BRU-ITC-10: prohibited goods are refused outright; restricted goods need a verified permit on the order. Entered from the Import Policy Order; activated by an Import Approver who did not enter it.',
        fields: [
          { name: 'name', required: true, label: 'Description' },
          { name: 'hs_code_pattern', label: 'HS Code / Prefix' },
          { name: 'product_id', label: 'Product' },
          { name: 'restriction_type', required: true, label: 'Type' },
          { name: 'permit_type', label: 'Permit Required' },
          { name: 'issuing_authority', label: 'Issuing Authority' },
          { name: 'legal_ref', label: 'Legal Reference' },
          { name: 'date_from', required: true, label: 'Effective From' },
          { name: 'date_to', label: 'Effective To' }
        ] }
    ]
  },

  'M44-form-permit': {
    kind: 'model_form',
    model: 'fix.import.permit',
    title: 'Import Permit',
    back: 'M44-permit',
    status: { field: 'state', labels: { draft: 'Draft', verified: 'Verified', revoked: 'Revoked' } },
    sections: [
      { title: 'Permit', note: 'Attach the permit document; an Import Approver who did not record it verifies it.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'restriction_id', required: true, label: 'Restriction' },
          { name: 'permit_no', required: true, label: 'Permit No' },
          { name: 'issuer', required: true, label: 'Issued By' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'valid_to', required: true, label: 'Valid To' },
          { name: 'document', type: 'binary', label: 'Permit Document' },
          { name: 'document_name', label: 'File Name' }
        ] }
    ]
  },

  'M44-form-agent': {
    kind: 'model_form',
    model: 'fix.import.cnf.agent',
    title: 'C&F Agent',
    back: 'M44-agent',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', blocked: 'Blocked', expired: 'Licence Expired' } },
    sections: [
      { title: 'Agent', note: 'BRU-ITC-12: instructed only when active in M42, licensed and approved by an Import Approver who did not enter it. A renewed licence is a new record.',
        fields: [
          { name: 'name', required: true, label: 'Agent' },
          { name: 'supplier_id', required: true, label: 'M42 Supplier Record' },
          { name: 'licence_no', required: true, label: 'C&F Licence No' },
          { name: 'licence_authority', label: 'Licensing Custom House' },
          { name: 'licence_expiry', required: true, label: 'Licence Expiry' },
          { name: 'is_usable', readonly: true, label: 'Can Be Instructed' }
        ] }
    ]
  },

  'M44-form-insurance': {
    kind: 'model_form',
    model: 'fix.import.insurance',
    title: 'Cargo Insurance',
    back: 'M44-insurance',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Cover', note: 'BRU-ITC-13: under FOB/EXW/CFR the cover must equal at least the consignment value before shipment. The verified premium is the insurance in the CIF.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'insurer_id', required: true, label: 'Insurer' },
          { name: 'policy_no', required: true, label: 'Policy / Cover Note No' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'sum_insured', required: true, label: 'Sum Insured' },
          { name: 'premium', label: 'Premium' },
          { name: 'cover_from', required: true, label: 'Cover From' },
          { name: 'cover_to', required: true, label: 'Cover To' }
        ] }
    ]
  }

};

export const REPORT_ROUTES = {
  'M44:Landed Cost by Shipment': 'M44-rpt-landed',
  'M44:Duty & Tax Cascade': 'M44-rpt-duty',
  'M44:Cycle-Time Analysis': 'M44-rpt-cycle',
  'M44:Demurrage Avoidance': 'M44-rpt-demurrage',
  'M44:FX Exposure': 'M44-rpt-fx'
};

export const FORM_MODELS = {
  'M44:Import Order': 'fix.import.order',
  'M44:LC Application': 'fix.import.lc',
  'M44:HS Ruling Request': 'fix.import.hs',
  'M44:Bill of Entry': 'fix.import.boe'
};

export const FORM_CHIPS = {
  'M44:Import Order': 'M44-form-order',
  'M44:LC Application': 'M44-form-lc',
  'M44:HS Ruling Request': 'M44-form-hs',
  'M44:Bill of Entry': 'M44-form-boe',
  'M44:__by_model__': {
    'fix.import.order': 'M44-form-order',
    'fix.import.proforma': 'M44-form-proforma',
    'fix.import.lc': 'M44-form-lc',
    'fix.import.lca': 'M44-form-lca',
    'fix.import.hs': 'M44-form-hs',
    'fix.import.irc': 'M44-form-irc',
    'fix.import.shipdoc': 'M44-form-shipdoc',
    'fix.import.arrival': 'M44-form-arrival',
    'fix.import.boe': 'M44-form-boe',
    'fix.import.landed': 'M44-form-landed',
    'fix.import.tariff': 'M44-form-tariff',
    'fix.import.lc.amendment': 'M44-form-lc-amend',
    'fix.import.lc.payment': 'M44-form-lc-pay',
    'fix.import.restriction': 'M44-form-restriction',
    'fix.import.permit': 'M44-form-permit',
    'fix.import.cnf.agent': 'M44-form-agent',
    'fix.import.insurance': 'M44-form-insurance'
  },
  'M44:__by_screen__': {
    'M44-orders': 'M44-form-order',
    'M44-proforma': 'M44-form-proforma',
    'M44-lc': 'M44-form-lc',
    'M44-lca': 'M44-form-lca',
    'M44-hs': 'M44-form-hs',
    'M44-irc': 'M44-form-irc',
    'M44-docs': 'M44-form-shipdoc',
    'M44-arrival': 'M44-form-arrival',
    'M44-boe': 'M44-form-boe',
    'M44-landed': 'M44-form-landed',
    'M44-tariff': 'M44-form-tariff',
    'M44-lc-amend': 'M44-form-lc-amend',
    'M44-lc-pay': 'M44-form-lc-pay',
    'M44-restriction': 'M44-form-restriction',
    'M44-permit': 'M44-form-permit',
    'M44-agent': 'M44-form-agent',
    'M44-insurance': 'M44-form-insurance'
  }
};

export const CREATE = {
  M44: { screen: 'M44-form-order', model: 'fix.import.order', label: 'Import Order' }
};
