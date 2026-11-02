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
    { l: 'FX Exposure', m: 'fx_exposure', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Orders & Finance', screens: [
      { id: 'M44-orders', en: 'Import Orders', bn: 'আমদানি অর্ডার', t: 'g' },
      { id: 'M44-proforma', en: 'Proforma Invoices', bn: 'প্রফর্মা ইনভয়েস', t: 'g' },
      { id: 'M44-lc', en: 'Letters of Credit', bn: 'এলসি', t: 'g' },
      { id: 'M44-incoterms', en: 'Incoterms & FX', bn: 'ইনকোটার্ম ও এফএক্স', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M44-hs', en: 'HS Classification', bn: 'এইচএস শ্রেণিবিন্যাস', t: 'g' },
      { id: 'M44-irc', en: 'IRC & Restrictions', bn: 'আইআরসি', t: 'g' },
      { id: 'M44-lca', en: 'LCA via Dealer Bank', bn: 'এলসিএ', t: 'g' }
    ]},
    { en: 'Shipping & Customs', screens: [
      { id: 'M44-docs', en: 'Shipping Documents', bn: 'শিপিং নথি', t: 'g' },
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
    ['1', 'Import Order Lifecycle', 9], ['2', 'LC & Payments', 10],
    ['3', 'HS Classification', 7], ['4', 'Eligibility & IRC', 5],
    ['5', 'Shipping & Insurance', 8], ['6', 'Port & Customs', 9],
    ['7', 'Duty Computation', 8], ['8', 'Landed Cost', 8]
  ] }
};

export const SCREENS = {
  'M44-orders': { kind: 'model_list', model: 'fix.import.order', stateField: 'state',
    cols: ['name', 'supplier_id', 'incoterm', 'fob_value', 'landed_cost', 'state'],
    actions: [{ m: 'action_receive', l: 'Mark Received' }] },
  'M44-proforma': { kind: 'model_list', model: 'fix.import.proforma', stateField: 'state',
    cols: ['proforma_no', 'order_id', 'amount', 'issued_on', 'valid_until', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve Proforma' }] },
  'M44-lc': { kind: 'model_list', model: 'fix.import.lc', stateField: 'state',
    cols: ['lc_no', 'order_id', 'bank', 'amount', 'opened_on', 'expiry', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply' },
      { m: 'action_open', l: 'Open LC' },
      { m: 'action_close', l: 'Close LC' }
    ] },
  'M44-incoterms': { kind: 'table_report', module: 'M44', report: 'incoterms_fx', title: 'Incoterms & FX', period: false },
  'M44-hs': { kind: 'model_list', model: 'fix.import.hs', stateField: 'state',
    cols: ['product_id', 'hs_code', 'cd_pct', 'rd_pct', 'sd_pct', 'vat_pct', 'state'],
    actions: [{ m: 'action_rule', l: 'Rule' }] },
  'M44-irc': { kind: 'model_list', model: 'fix.import.irc', stateField: 'state',
    cols: ['irc_no', 'issued_on', 'valid_to', 'is_valid', 'state'] },
  'M44-lca': { kind: 'model_list', model: 'fix.import.lca', stateField: 'state',
    cols: ['lca_no', 'lc_id', 'bank', 'amount', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve LCA' }] },
  'M44-docs': { kind: 'model_list', model: 'fix.import.shipdoc', stateField: 'state',
    cols: ['name', 'order_id', 'doc_type', 'ref', 'received_on', 'state'],
    actions: [{ m: 'action_receive', l: 'Mark Received' }] },
  'M44-arrival': { kind: 'model_list', model: 'fix.import.arrival', stateField: 'state',
    cols: ['name', 'order_id', 'vessel', 'eta', 'arrival_date', 'demurrage_days', 'state'],
    actions: [
      { m: 'action_arrive', l: 'Mark Arrived' },
      { m: 'action_clear', l: 'Clear' }
    ] },
  'M44-boe': { kind: 'model_list', model: 'fix.import.boe', stateField: 'state',
    cols: ['boe_no', 'order_id', 'assessed_on', 'total_tax', 'state'],
    actions: [
      { m: 'action_assess', l: 'Assess' },
      { m: 'action_pay', l: 'Mark Paid' }
    ] },
  'M44-duty': { kind: 'table_report', module: 'M44', report: 'duty_cascade', title: 'Duty Cascade', period: false },
  'M44-landed': { kind: 'model_list', model: 'fix.import.landed', stateField: 'state',
    cols: ['name', 'order_id', 'freight', 'insurance', 'duty', 'total_landed', 'state'],
    actions: [{ m: 'action_finalise', l: 'Finalise Sheet' }] },
  'M44-cf': { kind: 'table_report', module: 'M44', report: 'cnf_management', title: 'C&F Management', period: false },

  /* Report chips -> their own computed pack */
  'M44-rpt-landed': { kind: 'table_report', module: 'M44', report: 'landed_cost_by_shipment', title: 'Landed Cost by Shipment', period: false },
  'M44-rpt-duty': { kind: 'table_report', module: 'M44', report: 'duty_cascade', title: 'Duty & Tax Cascade', period: false },
  'M44-rpt-cycle': { kind: 'table_report', module: 'M44', report: 'cycle_time', title: 'Cycle-Time Analysis', period: false },
  'M44-rpt-demurrage': { kind: 'table_report', module: 'M44', report: 'demurrage_avoidance', title: 'Demurrage Avoidance', period: false },
  'M44-rpt-fx': { kind: 'table_report', module: 'M44', report: 'fx_exposure', title: 'FX Exposure', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M44-form-order': {
    kind: 'model_form',
    model: 'fix.import.order',
    title: 'Import Order',
    back: 'M44-orders',
    status: { field: 'state', labels: {
      draft: 'Draft', shipped: 'Shipped', customs: 'In Customs',
      received: 'Received', landed: 'Landed Cost Applied' } },
    sections: [
      { title: 'Order', note: 'The incoterm and FX rate are recorded inputs; FOB × rate is the local exposure basis.',
        fields: [
          { name: 'name', required: true, label: 'Order Reference' },
          { name: 'supplier_id', label: 'Supplier' },
          { name: 'country_origin', label: 'Country of Origin' },
          { name: 'incoterm', label: 'Incoterm' },
          { name: 'shipment_mode', label: 'Shipment Mode' },
          { name: 'fx_rate', label: 'FX Rate' },
          { name: 'fob_value', label: 'FOB Value' },
          { name: 'freight_cost', label: 'Freight' },
          { name: 'insurance_cost', label: 'Insurance' },
          { name: 'customs_duty', label: 'Customs Duty' }
        ] }
    ]
  },

  'M44-form-proforma': {
    kind: 'model_form',
    model: 'fix.import.proforma',
    title: 'Proforma Invoice',
    back: 'M44-proforma',
    status: { field: 'state', labels: {
      received: 'Received', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Proforma', fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'proforma_no', required: true, label: 'Proforma No' },
          { name: 'amount', label: 'Amount' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'valid_until', label: 'Valid Until' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Letter of Credit', note: 'Apply from draft, open from applied/amended, close from opened.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'lc_no', required: true, label: 'LC No' },
          { name: 'bank', label: 'Issuing Bank' },
          { name: 'amount', label: 'LC Amount' },
          { name: 'opened_on', label: 'Opened On' },
          { name: 'expiry', label: 'Expiry' },
          { name: 'margin_pct', label: 'Margin %' }
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
          { name: 'amount', label: 'Amount' }
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
      { title: 'Classification', note: 'The rates feed the duty cascade: CD/RD/AT/AIT on the assessable value, SD on duty-inclusive, VAT on value + CD + RD + SD.',
        fields: [
          { name: 'product_id', required: true, label: 'Product' },
          { name: 'hs_code', required: true, label: 'HS Code' },
          { name: 'description', label: 'Description' },
          { name: 'cd_pct', label: 'CD %' },
          { name: 'rd_pct', label: 'RD %' },
          { name: 'sd_pct', label: 'SD %' },
          { name: 'vat_pct', label: 'VAT %' },
          { name: 'at_pct', label: 'AT %' },
          { name: 'ait_pct', label: 'AIT %' },
          { name: 'ruling_ref', label: 'Ruling Reference' }
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
      { title: 'IRC', note: 'Validity is the state AND the end date.',
        fields: [
          { name: 'irc_no', required: true, label: 'IRC No' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'restrictions', type: 'text', label: 'Restrictions' },
          { name: 'state', required: true, label: 'State' }
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
          { name: 'received_on', required: true, label: 'Received On' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Arrival', note: 'Marking arrived stamps the arrival date and computes demurrage beyond the free days; clearance stamps the cleared date.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'vessel', label: 'Vessel / Flight' },
          { name: 'bl_no', label: 'B/L No' },
          { name: 'port', label: 'Port' },
          { name: 'etd', label: 'ETD' },
          { name: 'eta', label: 'ETA' },
          { name: 'free_days', label: 'Free Days' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M44-form-boe': {
    kind: 'model_form',
    model: 'fix.import.boe',
    title: 'Bill of Entry',
    back: 'M44-boe',
    status: { field: 'state', labels: {
      draft: 'Draft', assessed: 'Assessed', paid: 'Paid' } },
    sections: [
      { title: 'Bill of Entry', note: 'Assess from draft with at least one line; the totals are computed from the line cascade.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'boe_no', required: true, label: 'Bill of Entry No' },
          { name: 'asycuda_ref', label: 'ASYCUDA Reference' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'BOE Lines — duty cascade per line',
      note: 'Each line takes its rates from the HS classification; the amounts are computed, never typed.',
      fields: [
        { name: 'hs_id', required: true, label: 'HS Classification' },
        { name: 'description', label: 'Description' },
        { name: 'assessable_value', required: true, label: 'Assessable Value' }
      ]
    }
  },

  'M44-form-landed': {
    kind: 'model_form',
    model: 'fix.import.landed',
    title: 'Landed Cost Sheet',
    back: 'M44-landed',
    status: { field: 'state', labels: { draft: 'Draft', finalised: 'Finalised' } },
    sections: [
      { title: 'Landed Cost', note: 'Total landed = freight + insurance + duty + clearing + other; the allocation method is recorded, the allocation itself is reported.',
        fields: [
          { name: 'order_id', required: true, label: 'Import Order' },
          { name: 'freight', label: 'Freight' },
          { name: 'insurance', label: 'Insurance' },
          { name: 'duty', label: 'Duty' },
          { name: 'clearing_charges', label: 'Clearing Charges' },
          { name: 'other_charges', label: 'Other Charges' },
          { name: 'allocation_method', required: true, label: 'Allocation Method' },
          { name: 'state', required: true, label: 'State' }
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
    'fix.import.landed': 'M44-form-landed'
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
    'M44-landed': 'M44-form-landed'
  }
};

export const CREATE = {
  M44: { screen: 'M44-form-order', model: 'fix.import.order', label: 'Import Order' }
};
