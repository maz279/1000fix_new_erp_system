/** @odoo-module **/
/* A06 · Supply Chain — M15 Spare Parts & Inventory (v2 rebuild).
 * Registry-faithful: 5 groups / 16 screens / 6 reports / 5 forms / freg 107,
 * plus one receipts worklist (the registry ships the Goods Receipt form but
 * no list screen, so the inspection gate could not be exercised in-workspace). */

export const MODULE = {
  area: 'A06', code: 'M15', en: 'Spare Parts & Inventory', title: 'M15 · Spare Parts & Inventory',
  bn: 'স্পেয়ার পার্টস ও ইনভেন্টরি', icon: '🧰',
  desc: 'Stock ledger across 6 ownership classes, on-hand by location, issues and returns, serial/lot trace, van stock and par replenishment, daily reconciliation, cycle/full counts, inter-branch transfers, quarantine and scrap, RTV, valuation, ageing and ABC/XYZ/criticality.',
  kpis: [
    { l: 'Stock Value', m: 'stock_value', prefix: '৳ ' },
    { l: 'Stocked SKUs', m: 'stocked_skus' },
    { l: 'Stock-Out SKUs', m: 'stockout_skus' },
    { l: 'Pending Counts', m: 'pending_counts' },
    { l: 'Open Transfers', m: 'open_transfers' },
    { l: 'Van Variance', m: 'van_variance_pcs', suffix: ' pcs' }
  ],
  groups: [
    { en: 'Stock Ledger', screens: [
      { id: 'M15-onhand', en: 'On-Hand by Location', bn: 'স্টক অন-হ্যান্ড', t: 'g' },
      { id: 'M15-ownership', en: '6 Ownership Classes', bn: 'মালিকানা শ্রেণি', t: 'g' },
      { id: 'M15-movements', en: 'Issues & Returns', bn: 'ইস্যু ও রিটার্ন', t: 'g' },
      { id: 'M15-network', en: 'Network Availability Search', bn: 'প্রাপ্যতা অনুসন্ধান', t: 'g' },
      { id: 'M15-receipts', en: 'Goods Receipts', bn: 'পণ্য গ্রহণ', t: 'g' }
    ]},
    { en: 'Traceability', screens: [
      { id: 'M15-serials', en: 'Serial & Lot Trace', bn: 'সিরিয়াল ও লট ট্রেস', t: 'g' },
      { id: 'M15-genealogy', en: 'Consumption Genealogy', bn: 'ব্যবহারের বংশতালিকা', t: 'g' }
    ]},
    { en: 'Van Stock', screens: [
      { id: 'M15-van', en: 'Van Stock by Technician', bn: 'ভ্যান স্টক', t: 'g' },
      { id: 'M15-replen', en: 'Replenishment & Par', bn: 'রিপ্লেনিশমেন্ট', t: 'g' },
      { id: 'M15-recon', en: 'Daily Reconciliation', bn: 'দৈনিক মিলকরণ', t: 'g' }
    ]},
    { en: 'Control', screens: [
      { id: 'M15-counts', en: 'Cycle & Full Counts', bn: 'সাইকেল কাউন্ট', t: 'g' },
      { id: 'M15-transfers', en: 'Inter-Branch Transfers', bn: 'শাখা স্থানান্তর', t: 'g' },
      { id: 'M15-quarantine', en: 'Quarantine & Scrap', bn: 'কোয়ারেন্টিন ও স্ক্র্যাপ', t: 'g' },
      { id: 'M15-rtv', en: 'RTV Initiation', bn: 'ভেন্ডর ফেরত', t: 'g' },
      { id: 'M15-classchange', en: 'Ownership-Class Changes', bn: 'মালিকানা শ্রেণি পরিবর্তন', t: 'g' }
    ]},
    { en: 'Valuation & Analysis', screens: [
      { id: 'M15-valuation', en: 'Valuation (FIFO/WAC)', bn: 'ভ্যালুয়েশন', t: 'r' },
      { id: 'M15-ageing', en: 'Ageing & Obsolescence', bn: 'এজিং', t: 'r' },
      { id: 'M15-abc', en: 'ABC / XYZ / Criticality', bn: 'এবিসি শ্রেণিবিন্যাস', t: 'r' },
      { id: 'M15-suspense', en: 'Valuation Suspense Integrity', bn: 'মূল্যায়ন সাসপেন্স যাচাই', t: 'r' }
    ]}
  ],
  reports: ['Stock Valuation by Class', 'Inventory Accuracy Audit', 'Ageing & Dead Stock', 'Van Stock Variance', 'Transfer Performance', 'ABC Segmentation'],
  forms: ['Goods Receipt (inspection gate)', 'Stock Issue', 'Transfer Request', 'Cycle Count', 'Scrap Order'],
  cross: ['M41 warehouse execution', 'M16 procurement', 'M02 van consumption', 'M09 consignment stock', 'M31 bench stock'],
  freg: { src: 107, sub: [
    ['1', 'On-Hand & Classes', 12, { model: 'fix.stock.onhand', cols: ['part_id', 'location_id', 'ownership_class', 'qty', 'available_qty'], screens: ['M15-onhand', 'M15-network'] }],
    ['2', 'Location Hierarchy', 8, { model: 'fix.stock.location', cols: ['name', 'code', 'location_type', 'parent_id', 'branch_id'], screens: ['M15-network', 'M15-onhand'] }],
    ['3', 'Ownership Segregation', 9, { model: 'fix.stock.onhand', cols: ['ownership_class', 'part_id', 'location_id', 'qty', 'unit_cost'], screens: ['M15-ownership'] }],
    ['4', 'Reservations', 7, { model: 'fix.stock.onhand', cols: ['part_id', 'location_id', 'qty', 'reserved', 'available_qty'], screens: ['M15-onhand'], domain: [['reserved', '>', 0]] }],
    ['5', 'Issue / Return / Consumption', 10, { model: 'fix.stock.consumption', cols: ['name', 'product_id', 'technician_id', 'quantity', 'state'], screens: ['M15-movements', 'M15-genealogy'] }],
    ['6', 'Van Stock', 11, { model: 'fix.stock.van.recon', cols: ['name', 'location_id', 'technician_id', 'recon_date', 'variance'], screens: ['M15-van', 'M15-recon', 'M15-replen'] }],
    ['7', 'Serial & Lot Trace', 10, { model: 'fix.stock.lot', cols: ['name', 'part_id', 'location_id', 'status', 'warranty_until'], screens: ['M15-serials', 'M15-genealogy'] }],
    ['8', 'Valuation', 8, { model: 'fix.stock.onhand', cols: ['part_id', 'location_id', 'qty', 'unit_cost', 'valuation_method'], screens: ['M15-valuation'] }],
    ['9', 'Goods Receipt', 7, { model: 'fix.stock.receipt', cols: ['name', 'partner_id', 'location_id', 'received_on', 'state'], screens: ['M15-receipts'] }],
    ['10', 'Counting', 9, { model: 'fix.stock.count', cols: ['name', 'location_id', 'count_type', 'counted_on', 'state'], screens: ['M15-counts'] }],
    ['11', 'Ageing & Analysis', 8, { model: 'fix.stock.onhand', cols: ['part_id', 'location_id', 'qty', 'last_move_date', 'unit_cost'], screens: ['M15-ageing', 'M15-abc'] }],
    ['12', 'Transfers & RTV', 8, { model: 'fix.stock.transfer', cols: ['name', 'from_location_id', 'to_location_id', 'dispatched_on', 'state'], screens: ['M15-transfers', 'M15-rtv', 'M15-quarantine'] }]
  ] }
};

export const SCREENS = {
  'M15-onhand': { kind: 'model_list', model: 'fix.stock.onhand',
    cols: ['part_id', 'location_id', 'ownership_class', 'stock_status', 'qty', 'reserved', 'available_qty', 'unit_cost'] },
  'M15-ownership': { kind: 'table_report', module: 'M15', report: 'ownership_classes', title: '6 Ownership Classes', period: false },
  'M15-movements': { kind: 'model_list', model: 'fix.stock.consumption', stateField: 'state',
    cols: ['name', 'product_id', 'location_id', 'technician_id', 'quantity', 'state', 'consumed_at'],
    actions: [
      { m: 'action_scan_and_consume', l: 'Scan & Consume' },
      { m: 'action_return_part', l: 'Return Part', ask: 'Return reason: wrong_diagnosis, defective_new (goes to quarantine), customer_refusal or excess_draw', kwarg: 'reason' }
    ] },
  'M15-network': { kind: 'table_report', module: 'M15', report: 'availability', title: 'Network Availability Search', period: false },
  'M15-serials': { kind: 'model_list', model: 'fix.stock.lot', stateField: 'status',
    cols: ['name', 'part_id', 'location_id', 'qty', 'status', 'received_on'] },
  'M15-genealogy': { kind: 'table_report', module: 'M15', report: 'genealogy', title: 'Consumption Genealogy', period: false },
  'M15-van': { kind: 'table_report', module: 'M15', report: 'van_stock', title: 'Van Stock by Technician', period: false },
  'M15-replen': { kind: 'model_list', model: 'fix.reorder.rule', stateField: 'state',
    cols: ['name', 'spare_part_id', 'location_id', 'min_qty', 'max_qty', 'current_stock', 'suggested_order_qty', 'state'],
    actions: [
      { m: 'action_trigger_reorder', l: 'Trigger Reorder' },
      { m: 'action_activate', l: 'Activate Rule' },
      { m: 'action_archive_rule', l: 'Archive Rule' }
    ] },
  'M15-recon': { kind: 'model_list', model: 'fix.stock.van.recon', stateField: 'state',
    cols: ['name', 'location_id', 'technician_id', 'recon_date', 'expected_qty', 'counted_qty', 'variance', 'state'],
    actions: [
      { m: 'action_confirm', l: 'Confirm Reconciliation' },
      { m: 'action_resolve', l: 'Resolve Discrepancy (controller)', ask: 'How the van discrepancy was resolved', kwarg: 'note' }
    ] },
  'M15-counts': { kind: 'model_list', model: 'fix.stock.count', stateField: 'state',
    cols: ['name', 'location_id', 'count_type', 'counted_on', 'counted_by_id', 'reason_code', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit Count' },
      { m: 'action_approve', l: 'Approve Variance (controller)' },
      { m: 'action_reject', l: 'Reject Variance (controller)', ask: 'Why the variance is rejected', kwarg: 'note' }
    ] },
  'M15-transfers': { kind: 'model_list', model: 'fix.stock.transfer', stateField: 'state',
    cols: ['name', 'from_location_id', 'to_location_id', 'requested_on', 'dispatched_on', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval' },
      { m: 'action_approve', l: 'Approve (controller)' },
      { m: 'action_reject', l: 'Reject (controller)' },
      { m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_receive', l: 'Receive' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M15-quarantine': { kind: 'model_list', model: 'fix.stock.quarantine', stateField: 'state',
    cols: ['name', 'part_id', 'location_id', 'qty', 'reason', 'quarantined_on', 'state'],
    actions: [
      { m: 'action_release', l: 'Release' },
      { m: 'action_scrap', l: 'Scrap (within threshold)' },
      { m: 'action_request_scrap', l: 'Request Write-off' },
      { m: 'action_approve_scrap', l: 'Approve Write-off (controller)' },
      { m: 'action_reject_scrap', l: 'Reject Write-off (controller)', ask: 'Why the write-off is rejected', kwarg: 'note' }
    ] },
  'M15-rtv': { kind: 'model_list', model: 'fix.stock.rtv', stateField: 'state',
    cols: ['name', 'partner_id', 'part_id', 'location_id', 'qty', 'reason', 'rtv_ref', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit RTV' },
      { m: 'action_approve', l: 'Approve RTV (controller)' },
      { m: 'action_ship', l: 'Ship to Vendor' },
      { m: 'action_mark_credited', l: 'Record Credit', ask: 'Vendor credit note / replacement reference', kwarg: 'credit_ref' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M15-classchange': { kind: 'model_list', model: 'fix.stock.class.change', stateField: 'state',
    cols: ['name', 'part_id', 'location_id', 'from_class', 'to_class', 'qty', 'requested_by_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit' },
      { m: 'action_approve', l: 'Approve & Apply (controller)' },
      { m: 'action_reject', l: 'Reject (controller)', ask: 'Why the class change is rejected', kwarg: 'note' }
    ] },
  'M15-suspense': { kind: 'table_report', module: 'M15', report: 'suspense_integrity', title: 'Valuation Suspense Integrity', period: false },
  'M15-valuation': { kind: 'table_report', module: 'M15', report: 'valuation_by_class', title: 'Valuation (FIFO/WAC)', period: false },
  'M15-ageing': { kind: 'table_report', module: 'M15', report: 'ageeing', title: 'Ageing & Obsolescence', period: false },
  'M15-abc': { kind: 'table_report', module: 'M15', report: 'abc_segmentation', title: 'ABC / XYZ / Criticality', period: false },

  /* Extra worklist (declared): the registry ships the Goods Receipt form but
   * no list screen, so the inspection gate needs this grid to be postable. */
  'M15-receipts': { kind: 'model_list', model: 'fix.stock.receipt', stateField: 'state',
    cols: ['name', 'partner_id', 'location_id', 'received_on', 'state'],
    actions: [
      { m: 'action_inspect', l: 'Inspect' },
      { m: 'action_post', l: 'Post Receipt' }
    ] },

  /* Report chips -> their own computed pack */
  'M15-rpt-valuation': { kind: 'table_report', module: 'M15', report: 'valuation_by_class', title: 'Stock Valuation by Class', period: false },
  'M15-rpt-accuracy': { kind: 'table_report', module: 'M15', report: 'accuracy_audit', title: 'Inventory Accuracy Audit', period: false },
  'M15-rpt-ageing': { kind: 'table_report', module: 'M15', report: 'ageeing', title: 'Ageing & Dead Stock', period: false },
  'M15-rpt-van': { kind: 'table_report', module: 'M15', report: 'van_variance', title: 'Van Stock Variance', period: false },
  'M15-rpt-transfer': { kind: 'table_report', module: 'M15', report: 'transfer_performance', title: 'Transfer Performance', period: false },
  'M15-rpt-abc': { kind: 'table_report', module: 'M15', report: 'abc_segmentation', title: 'ABC Segmentation', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M15-form-receipt': {
    kind: 'model_form',
    model: 'fix.stock.receipt',
    title: 'Goods Receipt (inspection gate)',
    back: 'M15-receipts',
    status: { field: 'state', labels: {
      draft: 'Draft', inspected: 'Inspected', posted: 'Posted' } },
    sections: [
      { title: 'Receipt', note: 'Inspection gate: post only after every line has an accepted quantity. Rejected quantity (received minus accepted) is held in quarantine, never dropped. A posted receipt is final.',
        fields: [
          { name: 'partner_id', required: true, label: 'Supplier' },
          { name: 'location_id', required: true, label: 'Receiving Location' },
          { name: 'ownership_class', required: true, label: 'Ownership Class' },
          { name: 'purchase_order_id', label: 'Purchase Order' },
          { name: 'source_ref', label: 'Source Reference' },
          { name: 'received_on', required: true, label: 'Received On' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'inspection_notes', label: 'Inspection Notes' },
          { name: 'inspected_by_id', label: 'Inspected By', readonly: true },
          { name: 'posted_by_id', label: 'Posted By', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Receipt Lines — accepted ≤ received',
      note: 'Accepted quantity posts to the location ledger at its weighted-average cost; a serialized part is one unit per line with its serial (received once).',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'qty_received', required: true, label: 'Received' },
        { name: 'qty_accepted', required: true, label: 'Accepted' },
        { name: 'unit_cost', label: 'Unit Cost' },
        { name: 'line_no', label: 'Serial / Lot' }
      ]
    }
  },

  'M15-form-issue': {
    kind: 'model_form',
    model: 'fix.stock.consumption',
    title: 'Stock Issue',
    back: 'M15-movements',
    status: { field: 'state', labels: {
      draft: 'Draft Scan', consumed: 'Consumed', returned: 'Returned', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Issue', note: 'Saving a draft scan does not move stock. Scan & Consume takes unrestricted, unreserved stock of this location (a van only by its custodian), at its average cost; a serial must be in stock here. An issued record is final.',
        fields: [
          { name: 'product_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'Deduction Location / Van' },
          { name: 'technician_id', required: true, label: 'Technician' },
          { name: 'quantity', required: true, label: 'Quantity' },
          { name: 'service_order_ref', required: true, label: 'Service Order Ref' },
          { name: 'work_order_ref', label: 'Work Order Ref' },
          { name: 'scanned_code', required: true, label: 'Scanned Code' },
          { name: 'serial_number', label: 'Serial / IMEI' }
        ] }
    ]
  },

  'M15-form-transfer': {
    kind: 'model_form',
    model: 'fix.stock.transfer',
    title: 'Transfer Request',
    back: 'M15-transfers',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Awaiting Approval', approved: 'Approved',
      dispatched: 'Dispatched', received: 'Received', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Transfer', note: 'Submit, then an Inventory Controller who did not raise it approves; dispatch moves the stock into transit (the sender keeps it), and a different person receives it at the dispatch cost.',
        fields: [
          { name: 'from_location_id', required: true, label: 'From' },
          { name: 'to_location_id', required: true, label: 'To' },
          { name: 'requested_on', required: true, label: 'Requested On' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'dispatched_by_id', label: 'Dispatched By', readonly: true },
          { name: 'received_by_id', label: 'Received By', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Transfer Lines',
      note: 'Each line moves from the source on-hand bucket; a line that would take the source below zero is refused.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'qty', required: true, label: 'Quantity' }
      ]
    }
  },

  'M15-form-count': {
    kind: 'model_form',
    model: 'fix.stock.count',
    title: 'Cycle Count',
    back: 'M15-counts',
    status: { field: 'state', labels: {
      draft: 'Counting', recount: 'Recount Required', to_approve: 'Awaiting Approval',
      posted: 'Posted', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Count', note: 'Blind count: the system takes the expected quantity when each line is added and does not show it. Inside tolerance the count posts; outside it asks for a recount, then a reason and an Inventory Controller who is not the counter.',
        fields: [
          { name: 'location_id', required: true, label: 'Location' },
          { name: 'count_type', required: true, label: 'Count Type' },
          { name: 'counted_on', required: true, label: 'Counted On' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'reason_code', label: 'Variance Reason (after recount)' },
          { name: 'reason_note', label: 'Variance Explanation' },
          { name: 'counted_by_id', label: 'Counted By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Count Lines',
      note: 'Enter what is physically there. The recount column is used only when the count asks for a recount.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'counted_qty', required: true, label: 'Counted' },
        { name: 'recount_qty', label: 'Recount' }
      ]
    }
  },

  'M15-form-scrap': {
    kind: 'model_form',
    model: 'fix.stock.quarantine',
    title: 'Scrap Order',
    back: 'M15-quarantine',
    status: { field: 'state', labels: {
      quarantined: 'Quarantined', released: 'Released', scrap_pending: 'Write-off Awaiting Approval',
      scrapped: 'Scrapped', returned: 'Returned to Vendor' } },
    sections: [
      { title: 'Quarantine / Scrap', note: 'Saving moves the quantity out of available stock into quarantine. A write-off above the configured value needs an Inventory Controller who did not quarantine it.',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'Location' },
          { name: 'lot_id', label: 'Serial / Lot' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'quarantined_on', required: true, label: 'Quarantined On' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M15-form-onhand': {
    kind: 'model_form',
    model: 'fix.stock.onhand',
    title: 'On-Hand Adjustment',
    back: 'M15-onhand',
    sections: [
      { title: 'Bucket', note: 'Read-only: the ledger moves only by receipts, issues, transfers, approved counts, quarantine, scrap, RTV and approved class changes.',
        fields: [
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'location_id', label: 'Location', readonly: true },
          { name: 'ownership_class', label: 'Ownership Class', readonly: true },
          { name: 'stock_status', label: 'Stock Status', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'reserved', label: 'Reserved', readonly: true },
          { name: 'unit_cost', label: 'Average Cost', readonly: true },
          { name: 'valuation_method', label: 'Valuation Method', readonly: true }
        ] }
    ]
  },

  'M15-form-lot': {
    kind: 'model_form',
    model: 'fix.stock.lot',
    title: 'Serial / Lot',
    back: 'M15-serials',
    status: { field: 'status', labels: {
      in_stock: 'In Stock', issued: 'Issued', quarantined: 'Quarantined', scrapped: 'Scrapped' } },
    sections: [
      { title: 'Lot', note: 'Receipts create lots; issues, quarantine, scrap and RTV move them. Only the warranty date and the reference are maintained here.',
        fields: [
          { name: 'name', label: 'Serial / Lot', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'location_id', label: 'Location', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'received_on', label: 'Received On', readonly: true },
          { name: 'warranty_until', label: 'Warranty Until' },
          { name: 'source_ref', label: 'Source Reference' }
        ] }
    ]
  },

  'M15-form-recon': {
    kind: 'model_form',
    model: 'fix.stock.van.recon',
    title: 'Van Reconciliation',
    back: 'M15-recon',
    status: { field: 'state', labels: {
      draft: 'Draft', confirmed: 'Confirmed', discrepancy: 'Discrepancy', resolved: 'Resolved' } },
    sections: [
      { title: 'Reconciliation', note: 'The expected quantity is the van ledger, taken by the system. A variance outside tolerance is a discrepancy: it holds the van\'s issues until an Inventory Controller resolves it.',
        fields: [
          { name: 'location_id', required: true, label: 'Van Location' },
          { name: 'technician_id', label: 'Technician (the van custodian)' },
          { name: 'recon_date', required: true, label: 'Date' },
          { name: 'expected_qty', label: 'Expected (pcs)', readonly: true },
          { name: 'counted_qty', label: 'Counted (pcs)' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M15-form-rtv': {
    kind: 'model_form',
    model: 'fix.stock.rtv',
    title: 'Return to Vendor',
    back: 'M15-rtv',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Awaiting Approval', approved: 'Approved', shipped: 'Shipped',
      credited: 'Credited / Closed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'RTV', note: 'Approved by an Inventory Controller who did not raise it; after submission the vendor, part, location and quantity are pinned. It ships only with the vendor\'s RMA reference and closes when the credit is recorded.',
        fields: [
          { name: 'partner_id', required: true, label: 'Vendor' },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'From Location' },
          { name: 'quarantine_id', label: 'From Quarantine' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'requested_on', required: true, label: 'Requested On' },
          { name: 'rtv_ref', label: 'Vendor RMA Reference' },
          { name: 'credit_ref', label: 'Credit Reference', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M15-form-reorder': {
    kind: 'model_form',
    model: 'fix.reorder.rule',
    title: 'Reorder Rule',
    back: 'M15-replen',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active Rule', alert: 'Replenishment Alert',
      ordered: 'Requisition In Flight', archived: 'Archived' } },
    sections: [
      { title: 'Par Levels', note: 'Current stock is this location\'s unrestricted, unreserved stock. Entering the reorder point raises one alert and a draft requisition to M16 (hourly sweep); the state changes only by its actions.',
        fields: [
          { name: 'name', required: true, label: 'Rule' },
          { name: 'spare_part_id', required: true, label: 'Spare Part' },
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'location_id', required: true, label: 'Location' },
          { name: 'requester_id', label: 'Replenishment Requester' },
          { name: 'min_qty', label: 'Minimum' },
          { name: 'max_qty', label: 'Maximum' },
          { name: 'safety_stock', label: 'Safety Stock' },
          { name: 'lead_time_days', label: 'Lead Time (days)' },
          { name: 'current_stock', label: 'Current Stock', readonly: true },
          { name: 'requisition_id', label: 'Requisition', readonly: true },
          { name: 'plan_source_ref', label: 'Published From Plan', readonly: true }
        ] }
    ]
  },

  'M15-form-classchange': {
    kind: 'model_form',
    model: 'fix.stock.class.change',
    title: 'Ownership-Class Change',
    back: 'M15-classchange',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Awaiting Approval', done: 'Applied', rejected: 'Rejected' } },
    sections: [
      { title: 'Class Change', note: 'BRU-INV-06: stock changes ownership class only through this document, approved by an Inventory Controller who did not request it. The stock moves at its average cost.',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'Location' },
          { name: 'from_class', required: true, label: 'From Class' },
          { name: 'to_class', required: true, label: 'To Class' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M15:Stock Valuation by Class': 'M15-rpt-valuation',
  'M15:Inventory Accuracy Audit': 'M15-rpt-accuracy',
  'M15:Ageing & Dead Stock': 'M15-rpt-ageing',
  'M15:Van Stock Variance': 'M15-rpt-van',
  'M15:Transfer Performance': 'M15-rpt-transfer',
  'M15:ABC Segmentation': 'M15-rpt-abc'
};

export const FORM_MODELS = {
  'M15:Goods Receipt (inspection gate)': 'fix.stock.receipt',
  'M15:Stock Issue': 'fix.stock.consumption',
  'M15:Transfer Request': 'fix.stock.transfer',
  'M15:Cycle Count': 'fix.stock.count',
  'M15:Scrap Order': 'fix.stock.quarantine'
};

export const FORM_CHIPS = {
  'M15:Goods Receipt (inspection gate)': 'M15-form-receipt',
  'M15:Stock Issue': 'M15-form-issue',
  'M15:Transfer Request': 'M15-form-transfer',
  'M15:Cycle Count': 'M15-form-count',
  'M15:Scrap Order': 'M15-form-scrap',
  'M15:__by_model__': {
    'fix.stock.receipt': 'M15-form-receipt',
    'fix.stock.consumption': 'M15-form-issue',
    'fix.stock.transfer': 'M15-form-transfer',
    'fix.stock.count': 'M15-form-count',
    'fix.stock.quarantine': 'M15-form-scrap',
    'fix.stock.onhand': 'M15-form-onhand',
    'fix.stock.lot': 'M15-form-lot',
    'fix.stock.van.recon': 'M15-form-recon',
    'fix.stock.rtv': 'M15-form-rtv',
    'fix.reorder.rule': 'M15-form-reorder',
    'fix.stock.class.change': 'M15-form-classchange'
  },
  'M15:__by_screen__': {
    'M15-onhand': 'M15-form-onhand',
    'M15-movements': 'M15-form-issue',
    'M15-serials': 'M15-form-lot',
    'M15-replen': 'M15-form-reorder',
    'M15-recon': 'M15-form-recon',
    'M15-counts': 'M15-form-count',
    'M15-transfers': 'M15-form-transfer',
    'M15-quarantine': 'M15-form-scrap',
    'M15-rtv': 'M15-form-rtv',
    'M15-receipts': 'M15-form-receipt',
    'M15-classchange': 'M15-form-classchange'
  }
};

export const CREATE = {
  M15: { screen: 'M15-form-receipt', model: 'fix.stock.receipt', label: 'Goods Receipt' }
};
