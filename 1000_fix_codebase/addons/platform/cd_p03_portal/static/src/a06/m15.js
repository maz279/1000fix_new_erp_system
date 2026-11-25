/** @odoo-module **/
/* A06 · Supply Chain — M15 Spare Parts & Inventory (v2 rebuild).
 * Registry-faithful: 5 groups / 16 screens / 6 reports / 5 forms / freg 107,
 * plus one receipts worklist (the registry ships the Goods Receipt form but
 * no list screen, so the inspection gate could not be exercised in-workspace).
 * Real-inventory upgrade (2026-11-07, fit-gap report R4): +Item Master group,
 * the M15-parts grid and the 7-tab M15-form-part master form — the D365
 * data-capture surface for the 14,198-row real inventory statement.
 * Capture audit (2026-11-13): each sub-module page now offers the form that
 * captures its record - a stock location (FR-INV-002), the approved
 * ownership-class change (FR-INV-018), van par levels (FR-INV-029), a return
 * to vendor (FR-INV-052) - and serials, which only goods receipts create, are
 * no longer offered as a blank form the server refuses.
 * Capture pass 2 (2026-11-19): four pages still could not record what the
 * spec says is recorded there - page 4 a reservation held for a job, with
 * priority, expiry and override (FR-INV-019..021, 027); page 5 a backorder
 * when the part is not at hand (FR-INV-025) and an issue from the job's own
 * reservation; page 7 a recall that quarantines every affected unit
 * (FR-INV-040); page 3 the per-brand consignment statement (FR-INV-012/014).
 * Page 6 adds the Transfer Request chip: van-to-van is a transfer between
 * two vans (FR-INV-033). */

export const MODULE = {
  area: 'A06', code: 'M15', en: 'Spare Parts & Inventory', title: 'M15 · Spare Parts & Inventory',
  bn: 'স্পেয়ার পার্টস ও ইনভেন্টরি', icon: '🧰',
  desc: 'Stock ledger across 6 ownership classes, on-hand by location, issues and returns, serial/lot trace, van stock and par replenishment, daily reconciliation, cycle/full counts, inter-branch transfers, quarantine and scrap, RTV, valuation, ageing and ABC/XYZ/criticality.',
  kpis: [
    { l: 'Stock Value', m: 'stock_value', prefix: '৳ ' },
    { l: 'Stocked SKUs', m: 'stocked_skus' },
    { l: 'Stock-Out SKUs', m: 'stockout_skus' },
    { l: 'Below Minimum', m: 'below_min_lines' },
    { l: 'Pending Counts', m: 'pending_counts' },
    { l: 'Open Transfers', m: 'open_transfers' },
    { l: 'Van Variance', m: 'van_variance_pcs', suffix: ' pcs' },
    /* A06 ERP audit A23: the spec's KPI-042..047 (section 15), month to date */
    { l: 'KPI-042 Inventory Accuracy', m: 'kpi_042_accuracy_pct', suffix: ' %' },
    { l: 'KPI-043 Available at First Request', m: 'kpi_043_first_request_pct', suffix: ' %' },
    { l: 'KPI-044 Stockout Job Delays', m: 'kpi_044_stockout_delay_pct', suffix: ' %' },
    { l: 'KPI-045 Inventory Turns', m: 'kpi_045_turns', suffix: ' /yr' },
    { l: 'KPI-046 Dead Stock (value)', m: 'kpi_046_dead_stock_pct', suffix: ' %' },
    { l: 'KPI-047 Van Stock Variance', m: 'kpi_047_van_variance_pct', suffix: ' %' }
  ],
  groups: [
    { en: 'Item Master', screens: [
      { id: 'M15-parts', en: 'Item Master (Real Inventory)', bn: 'আইটেম মাস্টার (প্রকৃত ইনভেন্টরি)', t: 'g' }
    ]},
    { en: 'Stock Ledger', screens: [
      { id: 'M15-onhand', en: 'On-Hand by Location', bn: 'স্টক অন-হ্যান্ড', t: 'g' },
      { id: 'M15-locations', en: 'Stock Locations', bn: 'স্টক লোকেশন', t: 'g' },
      { id: 'M15-ownership', en: '6 Ownership Classes', bn: 'মালিকানা শ্রেণি', t: 'r' },
      { id: 'M15-reservations', en: 'Reservations', bn: 'রিজার্ভেশন', t: 'g' },
      { id: 'M15-movements', en: 'Issues & Returns', bn: 'ইস্যু ও রিটার্ন', t: 'g' },
      { id: 'M15-backorders', en: 'Backorders (Parts Wait)', bn: 'ব্যাকঅর্ডার', t: 'g' },
      { id: 'M15-network', en: 'Network Availability Search', bn: 'প্রাপ্যতা অনুসন্ধান', t: 'r' },
      { id: 'M15-receipts', en: 'Goods Receipts', bn: 'পণ্য গ্রহণ', t: 'g' }
    ]},
    { en: 'Traceability', screens: [
      { id: 'M15-serials', en: 'Serial & Lot Trace', bn: 'সিরিয়াল ও লট ট্রেস', t: 'g' },
      { id: 'M15-genealogy', en: 'Consumption Genealogy', bn: 'ব্যবহারের বংশতালিকা', t: 'r' },
      { id: 'M15-recalls', en: 'Recalls', bn: 'রিকল', t: 'g' }
    ]},
    { en: 'Van Stock', screens: [
      { id: 'M15-van', en: 'Van Stock by Technician', bn: 'ভ্যান স্টক', t: 'r' },
      { id: 'M15-replen', en: 'Replenishment & Par', bn: 'রিপ্লেনিশমেন্ট', t: 'g' },
      { id: 'M15-recon', en: 'Daily Reconciliation', bn: 'দৈনিক মিলকরণ', t: 'g' }
    ]},
    { en: 'Control', screens: [
      { id: 'M15-counts', en: 'Cycle & Full Counts', bn: 'সাইকেল কাউন্ট', t: 'g' },
      { id: 'M15-transfers', en: 'Inter-Branch Transfers', bn: 'শাখা স্থানান্তর', t: 'g' },
      { id: 'M15-quarantine', en: 'Quarantine & Scrap', bn: 'কোয়ারেন্টিন ও স্ক্র্যাপ', t: 'g' },
      { id: 'M15-rtv', en: 'RTV Initiation', bn: 'ভেন্ডর ফেরত', t: 'g' },
      { id: 'M15-classchange', en: 'Ownership-Class Changes', bn: 'মালিকানা শ্রেণি পরিবর্তন', t: 'g' },
      { id: 'M15-consignment', en: 'Brand Consignment Statements', bn: 'ব্র্যান্ড কনসাইনমেন্ট বিবরণী', t: 'g' }
    ]},
    { en: 'Valuation & Analysis', screens: [
      { id: 'M15-valuation', en: 'Valuation (WAC)', bn: 'ভ্যালুয়েশন', t: 'r' },
      { id: 'M15-ageing', en: 'Ageing & Obsolescence', bn: 'এজিং', t: 'r' },
      { id: 'M15-abc', en: 'ABC / XYZ / Criticality', bn: 'এবিসি শ্রেণিবিন্যাস', t: 'r' },
      { id: 'M15-stock-ledger', en: 'Stock Valuation Ledger', bn: 'স্টক মূল্যায়ন খতিয়ান', t: 'g' },
      { id: 'M15-stock-gl-tieout', en: 'Stock to GL Tie-out', bn: 'স্টক বনাম জিএল মিলকরণ', t: 'r' },
      { id: 'M15-suspense', en: 'Valuation Suspense Integrity', bn: 'মূল্যায়ন সাসপেন্স যাচাই', t: 'r' }
    ]},
    /* A06 ERP audit A22: the spec's section 14 registers */
    { en: 'Registers', screens: [
      { id: 'M15-position', en: 'Branch Stock Position', bn: 'শাখা স্টক অবস্থান', t: 'r' },
      { id: 'M15-adjustments', en: 'Adjustment & Write-off Register', bn: 'সমন্বয় ও রাইট-অফ রেজিস্টার', t: 'r' },
      { id: 'M15-qregister', en: 'Quarantine & Counterfeit Register', bn: 'কোয়ারেন্টিন রেজিস্টার', t: 'r' },
      { id: 'M15-rtvreg', en: 'RTV & Credit Recovery', bn: 'ভেন্ডর ফেরত ও ক্রেডিট', t: 'r' },
      { id: 'M15-stockouts', en: 'Stockout & Unmet Demand', bn: 'স্টকআউট ও অপূর্ণ চাহিদা', t: 'r' },
      { id: 'M15-movers', en: 'Slow & Fast Movers', bn: 'ধীর ও দ্রুত চলমান', t: 'r' }
    ]}
  ],
  reports: ['Stock Valuation by Class', 'Inventory Accuracy Audit', 'Ageing & Dead Stock', 'Van Stock Variance', 'Transfer Performance', 'ABC Segmentation',
    'Adjustment & Write-off Register', 'Quarantine & Counterfeit Register', 'RTV & Credit Recovery', 'Stockout & Unmet Demand', 'Branch Stock Position', 'Slow & Fast Movers'],
  forms: ['Goods Receipt (inspection gate)', 'Stock Issue', 'Transfer Request', 'Cycle Count', 'Scrap Order', 'Item Master (7 tabs)',
    'Stock Location', 'Ownership-Class Change', 'Reorder Rule', 'Return to Vendor',
    'Stock Reservation', 'Backorder', 'Stock Recall', 'Consignment Statement'],
  cross: ['M41 warehouse execution', 'M16 procurement', 'M02 van consumption', 'M09 consignment stock', 'M31 bench stock'],
  freg: { src: 107, sub: [
    ['1', 'On-Hand & Classes', 12, { model: 'fix.stock.onhand', cols: ['part_id', 'location_id', 'ownership_class', 'qty', 'available_qty'], screens: ['M15-onhand', 'M15-network', 'M15-position'], reports: ['Stock Valuation by Class', 'Inventory Accuracy Audit', 'Branch Stock Position'], forms: [] }],
    /* a location (van, store, quarantine...) is mastered on M41's form */
    ['2', 'Location Hierarchy', 8, { model: 'fix.stock.location', cols: ['name', 'code', 'location_type', 'parent_id', 'branch_id'], screens: ['M15-locations', 'M15-network', 'M15-onhand'], reports: [], forms: ['Stock Location'], create: 'M41-form-stock-location' }],
    /* stock changes class only by the approved document (BRU-INV-06) */
    /* the brand's monthly consignment statement is captured here (FR-INV-012/014) */
    ['3', 'Ownership Segregation', 9, { model: 'fix.stock.onhand', cols: ['ownership_class', 'part_id', 'location_id', 'qty', 'unit_cost'], screens: ['M15-ownership', 'M15-classchange', 'M15-consignment'], reports: ['Stock Valuation by Class'], forms: ['Ownership-Class Change', 'Consignment Statement'], create: 'M15-form-classchange' }],
    /* a reservation is a record held for a job (FR-INV-019..021, 027) */
    ['4', 'Reservations', 7, { model: 'fix.stock.reservation', cols: ['name', 'part_id', 'location_id', 'qty_open', 'priority', 'service_order_ref', 'expires_at', 'state'], screens: ['M15-reservations', 'M15-onhand'], reports: [], forms: ['Stock Reservation'], create: 'M15-form-reservation' }],
    ['5', 'Issue / Return / Consumption', 10, { model: 'fix.stock.consumption', cols: ['name', 'product_id', 'technician_id', 'quantity', 'state'], screens: ['M15-movements', 'M15-backorders', 'M15-genealogy', 'M15-stockouts'], reports: ['Stockout & Unmet Demand'], forms: ['Stock Issue', 'Backorder'] }],
    /* van-to-van (FR-INV-033) is a transfer request between two vans */
    ['6', 'Van Stock', 11, { model: 'fix.stock.van.recon', cols: ['name', 'location_id', 'technician_id', 'recon_date', 'variance'], screens: ['M15-van', 'M15-recon', 'M15-replen'], reports: ['Van Stock Variance'], forms: ['Reorder Rule', 'Transfer Request'] }],
    /* serials come from receipts; what a person records here is a recall (FR-INV-040) */
    ['7', 'Serial & Lot Trace', 10, { model: 'fix.stock.lot', cols: ['name', 'part_id', 'location_id', 'status', 'warranty_until'], screens: ['M15-serials', 'M15-recalls', 'M15-genealogy'], reports: [], forms: ['Stock Recall'], create: 'M15-form-recall' }],
    ['8', 'Valuation', 8, { model: 'fix.stock.onhand', cols: ['part_id', 'location_id', 'qty', 'unit_cost', 'valuation_method'], screens: ['M15-valuation', 'M15-stock-ledger', 'M15-stock-gl-tieout', 'M15-suspense'], reports: ['Stock Valuation by Class', 'Stock to GL Tie-out'], forms: [] }],
    ['9', 'Goods Receipt', 7, { model: 'fix.stock.receipt', cols: ['name', 'partner_id', 'location_id', 'received_on', 'state'], screens: ['M15-receipts'], reports: [], forms: ['Goods Receipt (inspection gate)'] }],
    ['10', 'Counting', 9, { model: 'fix.stock.count', cols: ['name', 'location_id', 'count_type', 'counted_on', 'state'], screens: ['M15-counts', 'M15-adjustments'], reports: ['Inventory Accuracy Audit', 'Adjustment & Write-off Register'], forms: ['Cycle Count'] }],
    ['11', 'Ageing & Analysis', 8, { model: 'fix.stock.onhand', cols: ['part_id', 'location_id', 'qty', 'last_move_date', 'unit_cost'], screens: ['M15-ageing', 'M15-abc', 'M15-movers'], reports: ['Ageing & Dead Stock', 'ABC Segmentation', 'Slow & Fast Movers'], forms: [] }],
    ['12', 'Transfers & RTV', 8, { model: 'fix.stock.transfer', cols: ['name', 'from_location_id', 'to_location_id', 'dispatched_on', 'state'], screens: ['M15-transfers', 'M15-rtv', 'M15-quarantine', 'M15-qregister', 'M15-rtvreg'], reports: ['Transfer Performance', 'Quarantine & Counterfeit Register', 'RTV & Credit Recovery'], forms: ['Transfer Request', 'Scrap Order', 'Return to Vendor'] }],
    ['13', 'Item Master (real inventory)', 12, { model: 'fix.spare.part', cols: ['part_number', 'name', 'brand_id', 'category_id', 'qty_available', 'unit_cost', 'state'], screens: ['M15-parts'], reports: ['ABC Segmentation'], forms: ['Item Master (7 tabs)'] }]
  ] }
};

export const SCREENS = {
  /* Real-inventory master grid (report R4): every loaded row of the real
   * inventory statement, exportable to branded XLSX/PDF/CSV + email via the
   * standard chips. Row click opens the 7-tab master form. */
  'M15-parts': { kind: 'model_list', model: 'fix.spare.part', stateField: 'state',
    cols: ['part_number', 'name', 'brand_id', 'category_id', 'product_id', 'qty_available', 'qty_reserved', 'unit_cost', 'state'],
    /* A06 ERP audit: the standard cost is set here by an Inventory Controller
     * (it left M41: no cost in the warehouse workspace) */
    actions: [
      { m: 'action_discontinue', l: 'Discontinue (controller)' },
      { m: 'action_mark_obsolete', l: 'Mark Obsolete (controller)' },
      { m: 'action_reactivate', l: 'Reactivate (controller)' },
      { m: 'action_set_standard_cost', l: 'Set Standard Cost (controller)', asks: [
        { label: 'New standard cost (BDT)', kwarg: 'cost', number: true }
      ] }
    ] },
  /* A06 ERP D1: the stock valuation ledger - one row per movement with the
   * journal entry it posted; written by the movements, never typed in */
  'M15-stock-ledger': { kind: 'model_list', model: 'fix.inventory.valuation.suspense', create: false,
    cols: ['posting_date', 'entry_type', 'product_id', 'location_id', 'quantity', 'unit_cost', 'total_valuation', 'stock_account_code', 'counter_account_code', 'move_id', 'status'],
    empty: 'No stock valuation entry yet. Every receipt, issue, transfer, count difference, write-off and return posts one row here with its journal entry.' },
  'M15-stock-gl-tieout': { kind: 'table_report', module: 'M15', report: 'stock_gl_tieout', title: 'Stock to GL Tie-out', period: true },

  /* the stock ledger's position: it moves only by receipts, issues, transfers,
   * approved counts, quarantine, scrap and RTV - never typed in (2026-11-12) */
  'M15-onhand': { kind: 'model_list', model: 'fix.stock.onhand', create: false,
    cols: ['part_id', 'location_id', 'ownership_class', 'stock_status', 'qty', 'reserved', 'available_qty', 'unit_cost'],
    empty: 'No stock on hand yet. Quantities appear when goods are received, and change only through issues, transfers, approved counts, quarantine, scrap and returns to vendor.' },
  /* the location hierarchy (FR-INV-002): stores, vans, workbenches,
   * quarantine and scrap; "+ New" and row clicks open M41's location form */
  'M15-locations': { kind: 'model_list', model: 'fix.stock.location', stateField: 'state',
    cols: ['name', 'code', 'location_type', 'parent_id', 'technician_id', 'branch_id', 'operating_unit_id', 'state'],
    actions: [
      { m: 'action_set_active', l: 'Activate (controller)' },
      { m: 'action_set_inactive', l: 'Deactivate (controller)' }
    ] },
  'M15-ownership': { kind: 'table_report', module: 'M15', report: 'ownership_classes', title: '6 Ownership Classes', period: false },
  'M15-movements': { kind: 'model_list', model: 'fix.stock.consumption', stateField: 'state',
    cols: ['name', 'product_id', 'location_id', 'technician_id', 'quantity', 'ownership_class', 'state', 'consumed_at'],
    actions: [
      { m: 'action_scan_and_consume', l: 'Scan & Consume' },
      { m: 'action_return_part', l: 'Return Part', ask: 'Return reason: wrong_diagnosis, defective_new (goes to quarantine), customer_refusal or excess_draw', kwarg: 'reason' },
      { m: 'action_approve_zero_cost', l: 'Approve Uncosted Issue (controller)', ask: 'Why the uncosted stock may be issued', kwarg: 'note' }
    ] },
  'M15-network': { kind: 'table_report', module: 'M15', report: 'availability', title: 'Network Availability Search', period: false },
  /* serials are created by goods receipts and moved by the ledger: the lot's
   * identity is guarded and no store role may create one (2026-11-13) */
  'M15-serials': { kind: 'model_list', model: 'fix.stock.lot', stateField: 'status', create: false,
    cols: ['name', 'part_id', 'location_id', 'qty', 'status', 'received_on'],
    empty: 'No serial or lot yet. A serial is recorded when a goods receipt of a serialized part is posted, and then follows every issue, transfer, quarantine and return.' },
  'M15-genealogy': { kind: 'table_report', module: 'M15', report: 'genealogy', title: 'Consumption Genealogy', period: true },
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
    cols: ['name', 'location_id', 'count_type', 'counted_on', 'counted_by_id', 'reason_code', 'variance_value', 'adjustment_value', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit Count' },
      { m: 'action_approve', l: 'Approve Variance (controller)' },
      { m: 'action_reject', l: 'Reject Variance (controller)', ask: 'Why the variance is rejected', kwarg: 'note' },
      { m: 'action_cancel', l: 'Cancel Count', ask: 'Why the count is cancelled', kwarg: 'note' }
    ] },
  'M15-transfers': { kind: 'model_list', model: 'fix.stock.transfer', stateField: 'state',
    cols: ['name', 'from_location_id', 'to_location_id', 'ownership_class', 'requested_on', 'dispatched_on', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval' },
      { m: 'action_approve', l: 'Approve (controller)' },
      { m: 'action_reject', l: 'Reject (controller)' },
      { m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_receive', l: 'Receive' },
      { m: 'action_resolve_discrepancy', l: 'Resolve Discrepancy (controller)', asks: [
        { label: 'Resolution: found, returned or quarantine', kwarg: 'resolution' },
        { label: 'How the shortage was resolved', kwarg: 'note' }
      ] },
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
  /* capture pass 2 (2026-11-19) */
  'M15-reservations': { kind: 'model_list', model: 'fix.stock.reservation', stateField: 'state',
    cols: ['name', 'part_id', 'location_id', 'booked_class', 'qty', 'qty_open', 'priority', 'service_order_ref', 'expires_at', 'requested_by_id', 'displaces_id', 'state'],
    empty: 'No reservation yet. Reserve stock for a job here; warranty and SLA-bound work ranks first, an unissued hold expires and goes back to stock.',
    actions: [
      { m: 'action_reserve', l: 'Reserve' },
      { m: 'action_release', l: 'Release', ask: 'Why the stock is released', kwarg: 'note' }
    ] },
  'M15-backorders': { kind: 'model_list', model: 'fix.stock.backorder', stateField: 'state',
    cols: ['name', 'part_id', 'location_id', 'qty', 'service_order_ref', 'needed_by', 'transfer_id', 'requisition_id', 'state'],
    actions: [
      { m: 'action_raise_transfer', l: 'Raise Transfer' },
      { m: 'action_raise_requisition', l: 'Raise Requisition' },
      { m: 'action_fulfil', l: 'Fulfil (reserve for the job)' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Why the backorder is cancelled', kwarg: 'note' }
    ] },
  'M15-recalls': { kind: 'model_list', model: 'fix.stock.recall', stateField: 'state',
    cols: ['name', 'part_id', 'scope', 'reason', 'reference', 'qty_quarantined', 'qty_not_reached', 'executed_at', 'state'],
    actions: [
      { m: 'action_execute', l: 'Execute Recall (controller)' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M15-consignment': { kind: 'model_list', model: 'fix.consignment.reconciliation', stateField: 'state',
    cols: ['name', 'brand_id', 'period_start', 'as_at', 'closing_qty', 'brand_qty', 'variance_qty', 'statement_ref', 'state'],
    actions: [
      { m: 'action_compute', l: 'Compute from Ledger' },
      { m: 'action_submit', l: 'Send to Brand' },
      { m: 'action_acknowledge', l: 'Record Brand Acknowledgement (controller)' }
    ] },
  'M15-suspense': { kind: 'table_report', module: 'M15', report: 'suspense_integrity', title: 'Valuation Suspense Integrity', period: false },
  'M15-valuation': { kind: 'table_report', module: 'M15', report: 'valuation_by_class', title: 'Valuation (WAC)', period: false },
  'M15-ageing': { kind: 'table_report', module: 'M15', report: 'ageing', title: 'Ageing & Obsolescence', period: false },
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
  'M15-rpt-accuracy': { kind: 'table_report', module: 'M15', report: 'accuracy_audit', title: 'Inventory Accuracy Audit', period: true },
  'M15-rpt-ageing': { kind: 'table_report', module: 'M15', report: 'ageing', title: 'Ageing & Dead Stock', period: false },
  'M15-rpt-van': { kind: 'table_report', module: 'M15', report: 'van_variance', title: 'Van Stock Variance', period: true },
  'M15-rpt-transfer': { kind: 'table_report', module: 'M15', report: 'transfer_performance', title: 'Transfer Performance', period: true },
  'M15-rpt-abc': { kind: 'table_report', module: 'M15', report: 'abc_segmentation', title: 'ABC Segmentation', period: false },
  /* A06 ERP audit A22: section 14 registers (every one keeps the export bar) */
  'M15-position': { kind: 'table_report', module: 'M15', report: 'branch_position', title: 'Branch Stock Position', period: false },
  'M15-adjustments': { kind: 'table_report', module: 'M15', report: 'adjustment_register', title: 'Adjustment & Write-off Register', period: true },
  'M15-qregister': { kind: 'table_report', module: 'M15', report: 'quarantine_register', title: 'Quarantine & Counterfeit Register', period: true },
  'M15-rtvreg': { kind: 'table_report', module: 'M15', report: 'rtv_register', title: 'RTV & Credit Recovery', period: true },
  'M15-stockouts': { kind: 'table_report', module: 'M15', report: 'stockout_register', title: 'Stockout & Unmet Demand', period: true },
  'M15-movers': { kind: 'table_report', module: 'M15', report: 'movers', title: 'Slow & Fast Movers', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  /* 7-tab item master (fit-gap report R4): the multi-tab data-capture surface
   * for the real inventory statement — the three part identities (new-ERP SKU,
   * previous-ERP number, manufacturer MPN), the governed Group→Category tree,
   * the brand master, stock policy, costing, warranty, the live per-location
   * ledger (the file's 96-column matrix as rows) and the lifecycle/legacy
   * audit trail. Writes go through /p03/model/write guards; ledger quantities
   * stay ledger-driven (read-only here). */
  'M15-form-part': {
    kind: 'model_form',
    model: 'fix.spare.part',
    title: 'Inventory Item Master',
    back: 'M15-parts',
    status: { field: 'state', labels: {
      active: 'Active', discontinued: 'Discontinued', obsolete: 'Obsolete' } },
    tabs: [
      { id: 'identification', label: '1. Identification', bn: '১. পরিচয়', icon: '🔎', badge: '8' },
      { id: 'classification', label: '2. Classification', bn: '২. শ্রেণিবিন্যাস', icon: '🏷️', badge: '7' },
      { id: 'policy', label: '3. Stock Policy', bn: '৩. স্টক নীতি', icon: '📦', badge: '8' },
      { id: 'costing', label: '4. Costing & Pricing', bn: '৪. মূল্য নির্ধারণ', icon: '💰', badge: '6' },
      { id: 'warranty', label: '5. Warranty & Compliance', bn: '৫. ওয়ারেন্টি ও কমপ্লায়েন্স', icon: '🛡️', badge: '4' },
      { id: 'ledger', label: '6. Stock Position', bn: '৬. মজুদ অবস্থান', icon: '📍' },
      { id: 'lifecycle', label: '7. Lifecycle & Legacy', bn: '৭. জীবনচক্র ও লিগ্যাসি', icon: '🔄', badge: '6' }
    ],
    sections: [
      { tab: 'identification', title: 'Identity & Codes',
        note: 'The three part identities of the real inventory statement. The New ERP Part No is the SKU (default_code on the purchased-as product); the previous-ERP and manufacturer numbers live on the product template.',
        fields: [
          { name: 'name', required: true, label: 'Product Description' },
          { name: 'name_bn', label: 'বিবরণ (বাংলা)' },
          { name: 'part_number', required: true, label: 'Part Number / SKU' },
          { name: 'product_default_code', label: 'New ERP Part No (product SKU)' },
          { name: 'product_legacy_erp_part_number', label: 'Previous ERP Part No' },
          { name: 'product_manufacturer_part_number', label: 'Manufacturer Part No (MPN)' },
          { name: 'barcode', label: 'Barcode (EAN-13 / UPC)' },
          { name: 'qr_code', label: 'Internal QR Code' },
          { name: 'uom', label: 'Unit of Measure' }
        ] },
      { tab: 'classification', title: 'Group → Category → Brand',
        note: 'The governed taxonomy seeded from the real file: Level 1 = Group (41), Level 2 = Category (859 group-scoped pairs); Brand = the fix.brand master.',
        fields: [
          { name: 'category_id', label: 'Product Category (Group Tree)' },
          { name: 'brand_id', label: 'Brand (Brand Master)' },
          { name: 'part_category', label: 'Component Category (enum hint)' },
          { name: 'device_brand', label: 'Device Brand (legacy text)' },
          { name: 'compatible_models', label: 'Compatible Models (source text)', type: 'text' },
          { name: 'model_compatibility_ids', label: 'Compatible Device Models (governed)' },
          { name: 'product_id', label: 'Purchased As (Product)' }
        ] },
      { tab: 'policy', title: 'Stocking Policy',
        fields: [
          { name: 'min_qty', label: 'Minimum Reorder Point' },
          { name: 'max_qty', label: 'Target Max Stock' },
          { name: 'safety_stock', label: 'Safety Buffer Stock' },
          { name: 'criticality', label: 'Criticality' },
          { name: 'is_serialized', label: 'Serialized Component' },
          { name: 'core_exchange_required', label: 'Core Return Required' },
          { name: 'storage_class', label: 'Storage Class' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ] },
      { tab: 'costing', title: 'Costs & Prices (BDT)',
        note: 'The standard cost changes only through Set Standard Cost by an Inventory Controller; on-hand quantities and the average cost are ledger-driven and never typed.',
        fields: [
          { name: 'unit_cost', label: 'Standard Cost', readonly: true },
          { name: 'average_cost', label: 'Average Cost (ledger)', readonly: true },
          { name: 'sales_price', label: 'Retail Replacement Price' },
          { name: 'list_price', label: 'List Price' },
          { name: 'qty_available', label: 'Quantity On Hand', readonly: true },
          { name: 'qty_reserved', label: 'Quantity Reserved', readonly: true }
        ] },
      { tab: 'warranty', title: 'Warranty & Handling',
        fields: [
          { name: 'warranty_months', label: 'Warranty Period (Months)' },
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'lifecycle', title: 'Lifecycle & Legacy Audit',
        note: 'Status transitions run through the controller actions (discontinue / obsolete / reactivate). legacy_reference is the permanent migration key (MIG-03) — never edited.',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'active', label: 'Active Record Status' },
          { name: 'legacy_reference', label: 'Legacy Reference (migration key)', readonly: true },
          { name: 'create_date', label: 'Loaded On', readonly: true },
          { name: 'write_date', label: 'Last Changed', readonly: true }
        ] }
    ],
    lines: {
      field: 'onhand_ids',
      readonlyGrid: true,
      title: 'Stock Position — per location × ownership class (read-only ledger)',
      note: 'The live version of the inventory statement\'s per-location quantity matrix. Quantities change only by a movement (receipt, issue, transfer, count) — never on this form.',
      fields: [
        { name: 'location_id', label: 'Location', readonly: true },
        { name: 'ownership_class', label: 'Ownership', readonly: true },
        { name: 'stock_status', label: 'Status', readonly: true },
        { name: 'qty', label: 'On Hand', readonly: true },
        { name: 'reserved', label: 'Reserved', readonly: true },
        { name: 'unit_cost', label: 'Unit Cost', readonly: true },
        { name: 'last_move_date', label: 'Last Movement', readonly: true }
      ]
    }
  },

  'M15-form-receipt': {
    kind: 'model_form',
    model: 'fix.stock.receipt',
    title: 'Goods Receipt (inspection gate)',
    back: 'M15-receipts',
    status: { field: 'state', labels: {
      draft: 'Draft', inspected: 'Inspected', posted: 'Posted' } },
    sections: [
      { title: 'Receipt', note: 'Inspection gate: post only after every line has an accepted quantity. Rejected quantity (received minus accepted) is held in quarantine, never dropped. Against a purchase order the quantity stays within what is open and the cost is the PO price. With no purchase order, record the reason: only an Inventory Controller posts it. A posted receipt is final.',
        fields: [
          { name: 'partner_id', required: true, label: 'Supplier' },
          { name: 'location_id', required: true, label: 'Receiving Location' },
          { name: 'ownership_class', required: true, label: 'Ownership Class' },
          { name: 'purchase_order_id', label: 'Purchase Order', domain: [['state', 'in', ['sent', 'acknowledged', 'partially_received', 'received']]] },
          { name: 'direct_reason', label: 'Reason (no purchase order)' },
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
      note: 'Accepted quantity posts to the location ledger at its weighted-average cost; a serialized part is one unit per line with its serial (received once). The cost shows only to finance and inventory-manager roles; a PO receipt takes the PO price whatever is typed.',
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
      { title: 'Issue', note: 'Saving a draft scan does not move stock. Scan & Consume takes unrestricted, unreserved stock of this location (a van only by its custodian), at its average cost; the scan must read this part and a serial must be in stock here. Brand consignment goes only on a warranty job for that brand, customer-supplied only on that customer\'s job. An issued record is final.',
        fields: [
          { name: 'product_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'Deduction Location / Van' },
          { name: 'technician_id', required: true, label: 'Technician' },
          { name: 'issue_class', required: true, label: 'Issue From Class', value: 'owned' },
          { name: 'quantity', required: true, label: 'Quantity' },
          { name: 'service_order_ref', required: true, label: 'Service Order Ref' },
          { name: 'work_order_ref', label: 'Work Order Ref' },
          { name: 'scanned_code', required: true, label: 'Scanned Code' },
          { name: 'serial_number', label: 'Serial / IMEI' },
          { name: 'reservation_id', label: 'From Reservation (held for this job)', domain: [['state', '=', 'active']] }
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
      dispatched: 'Dispatched', discrepancy: 'Received with Discrepancy',
      received: 'Received', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Transfer', note: 'Submit, then an Inventory Controller who did not raise it approves; dispatch moves the stock into transit (the sender keeps it), and a different person records what arrived and receives it at the dispatch cost. A short quantity stays in transit until an approver resolves the discrepancy.',
        fields: [
          { name: 'from_location_id', required: true, label: 'From' },
          { name: 'to_location_id', required: true, label: 'To' },
          { name: 'ownership_class', required: true, label: 'Stock Class (consignment, warranty reserve and customer property keep theirs)' },
          { name: 'requested_on', required: true, label: 'Requested On' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'transfer_value', label: 'Transfer Value (BDT)', readonly: true },
          { name: 'discrepancy_resolution', label: 'Discrepancy Resolution', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'dispatched_by_id', label: 'Dispatched By', readonly: true },
          { name: 'received_by_id', label: 'Received By', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Transfer Lines',
      note: 'Each line moves from the source on-hand bucket; a line that would take the source below zero is refused. A serialized part travels one serial per line. On arrival, correct Received if less arrived.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'qty', required: true, label: 'Quantity' },
        { name: 'lot_id', label: 'Serial', domain: [['status', '=', 'in_stock']] },
        { name: 'received_qty', label: 'Received' },
        { name: 'discrepancy_qty', label: 'Short', readonly: true }
      ]
    }
  },

  'M15-form-count': {
    kind: 'model_form',
    model: 'fix.stock.count',
    title: 'Cycle Count',
    back: 'M15-counts',
    status: { field: 'state', labels: {
      draft: 'Counting', recount: 'Recount Required', to_approve: 'Awaiting Approval', to_dofa: 'Awaiting DOFA (CFO)',
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
          { name: 'variance_value', label: 'Variance Value, net (BDT)', readonly: true },
          { name: 'adjustment_value', label: 'Adjustment Value, gross (BDT)', readonly: true },
          { name: 'counted_by_id', label: 'Counted By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Count Lines',
      note: 'Enter what is physically there. The recount column is used only when the count asks for a recount. The approver sees the expected quantity and the variance; the counter does not until the count is posted.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'ownership_class', label: 'Class (empty: the location\'s own)' },
        { name: 'counted_qty', required: true, label: 'Counted' },
        { name: 'recount_qty', label: 'Recount' },
        { name: 'expected_qty', label: 'Expected', readonly: true },
        { name: 'variance', label: 'Variance', readonly: true }
      ]
    }
  },

  'M15-form-scrap': {
    kind: 'model_form',
    model: 'fix.stock.quarantine',
    title: 'Scrap Order',
    back: 'M15-quarantine',
    status: { field: 'state', labels: {
      quarantined: 'Quarantined', released: 'Released', scrap_pending: 'Write-off Awaiting Approval', scrap_dofa: 'Awaiting DOFA (CFO)',
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
    create: false, pick: 'Stock on hand changes through receipts, issues, transfers and counts: open a position from On-Hand.',
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
    create: false, pick: 'A serial is recorded by its goods receipt: open one from Serial & Lot Trace.',
    status: { field: 'status', labels: {
      in_stock: 'In Stock', issued: 'Issued', quarantined: 'Quarantined', scrapped: 'Scrapped',
      returned: 'Returned to Vendor', in_transit: 'In Transit', staged: 'Staged for Dispatch', shipped: 'Shipped' } },
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
      { title: 'Reconciliation', note: 'A blind count: the van ledger is taken by the system and shown only to approvers. A variance outside tolerance is a discrepancy: it holds this technician\'s issues until an approver resolves it.',
        fields: [
          { name: 'location_id', required: true, label: 'Van Location' },
          { name: 'technician_id', label: 'Technician (the van custodian)' },
          { name: 'recon_date', required: true, label: 'Date' },
          { name: 'expected_qty', label: 'Expected (pcs)', readonly: true },
          { name: 'counted_qty', label: 'Counted (pcs, from the lines)', readonly: true },
          { name: 'variance_value', label: 'Variance Value (BDT)', readonly: true },
          { name: 'ledger_corrected', label: 'Ledger Corrected', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ],
    /* A06 ERP audit A11: the van is counted part by part; a part on the ledger
     * that is not listed counts as none. An approved discrepancy corrects the
     * ledger from these lines at the van's average cost. */
    lines: {
      field: 'line_ids',
      title: 'Parts Counted',
      note: 'One line per part found on the van. The expected quantity and the variance are shown to approvers only.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'counted_qty', required: true, label: 'Counted' },
        { name: 'expected_qty', label: 'Expected', readonly: true },
        { name: 'variance', label: 'Variance', readonly: true },
        { name: 'variance_value', label: 'Variance Value (BDT)', readonly: true }
      ]
    }
  },

  'M15-form-rtv': {
    kind: 'model_form',
    model: 'fix.stock.rtv',
    title: 'Return to Vendor',
    back: 'M15-rtv',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Awaiting Approval', approved: 'Approved', shipped: 'Shipped',
      credited: 'Credited / Closed', cancelled: 'Cancelled' } },
    // 16 fields: tabbed, not one long scroll (forms over 15 fields, AGENTS.md)
    tabs: [
      { id: 'rtv', label: '1. Return', bn: '১. ফেরত', icon: '↩', badge: '12' },
      { id: 'grn', label: '2. GRN, PO & Bill', bn: '২. জিআরএন, পিও ও বিল', icon: '🧾', badge: '5' }
    ],
    sections: [
      { tab: 'rtv', title: 'RTV', note: 'Approved by an Inventory Controller who did not raise it; after submission the vendor, part, location and quantity are pinned. It ships only with the vendor\'s RMA reference and closes when the credit is recorded.',
        fields: [
          { name: 'partner_id', required: true, label: 'Vendor' },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'From Location' },
          { name: 'quarantine_id', label: 'From Quarantine' },
          { name: 'ownership_class', required: true, label: 'Stock Class (unused brand consignment goes back as consignment)' },
          { name: 'lot_id', label: 'Serial (serialized part, not from quarantine)', domain: [['status', '=', 'in_stock']] },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'requested_on', required: true, label: 'Requested On' },
          { name: 'rtv_ref', label: 'Vendor RMA Reference' },
          { name: 'credit_ref', label: 'Credit Reference', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] },
      { tab: 'grn', title: 'Goods Receipt, PO and Bill', note: 'Name the goods receipt the goods came in on: the PO comes from it and the AP credit note is raised on the bill of that PO, at the billed price with its VAT and TDS. The return is held to what the GRN accepted and the bill billed. Stock with no goods receipt records why; AP then raises its credit by hand.',
        fields: [
          { name: 'receipt_id', label: 'Goods Receipt (GRN)', domain: [['state', '=', 'posted']] },
          { name: 'no_receipt_reason', label: 'Why No Goods Receipt' },
          { name: 'purchase_order_id', label: 'Purchase Order', readonly: true },
          { name: 'vendor_invoice_ref', label: 'Vendor Bill', readonly: true },
          { name: 'vendor_note_status', label: 'AP Credit Note', readonly: true }
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
  },

  /* page 4 (FR-INV-019..021, 027): stock held for a job */
  'M15-form-reservation': {
    kind: 'model_form',
    model: 'fix.stock.reservation',
    title: 'Stock Reservation',
    back: 'M15-reservations',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Held', consumed: 'Issued', released: 'Released',
      expired: 'Expired', overridden: 'Displaced' } },
    sections: [
      { title: 'Reservation', note: 'Save, then Reserve. Only unrestricted, unreserved stock is held. The job sets the priority: warranty and SLA-bound work first, then paid work, then internal demand; a higher-priority job takes stock from lower-priority holds and their requesters are told. An unissued hold expires and goes back to stock. To take an equal or higher-priority job\'s stock, an Inventory Controller or Branch Manager names it under Emergency Override with a reason.',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'Location' },
          { name: 'reserve_class', required: true, label: 'Reserve From Class', value: 'owned' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'service_order_ref', label: 'Job Reference (service order / job)' },
          { name: 'notes', label: 'Notes' },
          { name: 'displaces_id', label: 'Emergency Override Of', domain: [['state', '=', 'active']] },
          { name: 'override_reason', label: 'Override Reason' },
          { name: 'priority', label: 'Priority', readonly: true },
          { name: 'qty_open', label: 'Still Held', readonly: true },
          { name: 'qty_consumed', label: 'Issued', readonly: true },
          { name: 'expires_at', label: 'Expires', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'release_reason', label: 'Released Because', readonly: true }
        ] }
    ]
  },

  /* page 5 (FR-INV-025): the part is not at hand */
  'M15-form-backorder': {
    kind: 'model_form',
    model: 'fix.stock.backorder',
    title: 'Backorder',
    back: 'M15-backorders',
    status: { field: 'state', labels: {
      open: 'Open (parts wait)', transfer: 'Transfer Raised', requisition: 'Requisition Raised',
      fulfilled: 'Fulfilled', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Backorder', note: 'Raised only when the location cannot supply the quantity. If another location holds it, Raise Transfer pulls it from the network source; only when nobody holds it does Raise Requisition send a purchase to M16. When the stock arrives, Fulfil reserves it for the job.',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'location_id', required: true, label: 'Needed At' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'service_order_ref', label: 'Job Reference' },
          { name: 'needed_by', label: 'Needed By' },
          { name: 'notes', label: 'Notes' },
          { name: 'source_location_id', label: 'Network Source', readonly: true },
          { name: 'source_available', label: 'Available There', readonly: true },
          { name: 'transfer_id', label: 'Transfer', readonly: true },
          { name: 'requisition_id', label: 'Requisition (M16)', readonly: true },
          { name: 'reservation_id', label: 'Reservation', readonly: true },
          { name: 'cancel_reason', label: 'Cancelled Because', readonly: true }
        ] }
    ]
  },

  /* page 7 (FR-INV-040 / AUT-INV-14): quarantine every affected unit */
  'M15-form-recall': {
    kind: 'model_form',
    model: 'fix.stock.recall',
    title: 'Stock Recall',
    back: 'M15-recalls',
    status: { field: 'state', labels: { draft: 'Draft', executed: 'Executed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Recall', note: 'Execute (Inventory Controller) quarantines, in one transaction, every unrestricted unit of the part, or of the named serials, at every location and van, releases the reservations that held it and lists the jobs that already consumed it. What it cannot reach (in transit, issued, in warehouse bins, held by a wave pick) is listed as the manual sweep worklist.',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'scope', required: true, label: 'Scope', value: 'all' },
          { name: 'lot_ids', label: 'Serials / Lots (named scope)' },
          { name: 'reason', required: true, label: 'Reason', value: 'recall' },
          { name: 'reference', label: 'Bulletin / Notice Reference' },
          { name: 'notes', label: 'Notes' },
          { name: 'qty_quarantined', label: 'Quarantined', readonly: true },
          { name: 'qty_not_reached', label: 'Not Reached', readonly: true },
          { name: 'worklist', label: 'Manual Sweep Worklist', readonly: true },
          { name: 'affected_consumption_ids', label: 'Jobs Already Consuming It', readonly: true },
          { name: 'executed_by_id', label: 'Executed By', readonly: true },
          { name: 'executed_at', label: 'Executed On', readonly: true }
        ] }
    ]
  },

  /* page 3 (FR-INV-012/014, AUT-INV-07): the brand's consignment statement */
  'M15-form-consignment': {
    kind: 'model_form',
    model: 'fix.consignment.reconciliation',
    title: 'Brand Consignment Statement',
    back: 'M15-consignment',
    status: { field: 'state', labels: {
      draft: 'Draft', computed: 'Computed', submitted: 'Sent to Brand', acknowledged: 'Acknowledged' } },
    // 15 header fields and a part grid: tabbed so the statement and the
    // brand's acknowledgement each fit one screen (AGENTS.md multi-tab forms)
    tabs: [
      { id: 'statement', label: '1. Statement', bn: '১. বিবরণী', icon: '🧾', badge: '9' },
      { id: 'brand', label: '2. Brand Acknowledgement', bn: '২. ব্র্যান্ডের স্বীকৃতি', icon: '✍', badge: '6' }
    ],
    sections: [
      { tab: 'statement', title: 'Statement', note: 'Compute from Ledger: closing is the consignment stock of the brand\'s parts now; received and consumed on warranty jobs count from the period start; the opening carries from the brand\'s last acknowledged statement. Other movements are returns to the brand, transfers out and count adjustments.',
        fields: [
          { name: 'brand_id', required: true, label: 'Brand' },
          { name: 'period_start', required: true, label: 'Period From' },
          { name: 'as_at', label: 'As At', readonly: true },
          { name: 'opening_qty', label: 'Opening', readonly: true },
          { name: 'received_qty', label: 'Received', readonly: true },
          { name: 'consumed_qty', label: 'Consumed on Warranty', readonly: true },
          { name: 'damaged_qty', label: 'Damaged / Written Off', readonly: true },
          { name: 'other_qty', label: 'Other Movements', readonly: true },
          { name: 'closing_qty', label: 'Closing (ledger)', readonly: true }
        ] },
      { tab: 'brand', title: 'Brand Acknowledgement', note: 'Enter the brand\'s own closing figure on each line where it differs. An Inventory Controller who did not prepare the statement records the acknowledgement; a variance needs an explanation.',
        fields: [
          { name: 'brand_qty', label: 'Closing (brand)', readonly: true },
          { name: 'variance_qty', label: 'Variance', readonly: true },
          { name: 'statement_ref', label: 'Brand Statement Reference' },
          { name: 'brand_acknowledged_by', label: 'Acknowledged By (brand)' },
          { name: 'brand_acknowledged_on', label: 'Brand Acknowledged On' },
          { name: 'variance_note', label: 'Variance Explanation' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      fixedRows: true,
      title: 'Parts - ledger against the brand',
      note: 'The rows come from the ledger. Only the brand\'s closing figure is entered.',
      fields: [
        { name: 'part_id', label: 'Spare Part', readonly: true },
        { name: 'opening_qty', label: 'Opening', readonly: true },
        { name: 'received_qty', label: 'Received', readonly: true },
        { name: 'consumed_qty', label: 'Consumed', readonly: true },
        { name: 'damaged_qty', label: 'Damaged', readonly: true },
        { name: 'other_qty', label: 'Other', readonly: true },
        { name: 'closing_qty', label: 'Closing (ledger)', readonly: true },
        { name: 'brand_qty', label: 'Closing (brand)' },
        { name: 'variance_qty', label: 'Variance', readonly: true }
      ]
    }
  }
};

export const REPORT_ROUTES = {
  'M15:Stock Valuation by Class': 'M15-rpt-valuation',
  'M15:Stock to GL Tie-out': 'M15-stock-gl-tieout',
  'M15:Inventory Accuracy Audit': 'M15-rpt-accuracy',
  'M15:Ageing & Dead Stock': 'M15-rpt-ageing',
  'M15:Van Stock Variance': 'M15-rpt-van',
  'M15:Transfer Performance': 'M15-rpt-transfer',
  'M15:ABC Segmentation': 'M15-rpt-abc',
  'M15:Adjustment & Write-off Register': 'M15-adjustments',
  'M15:Quarantine & Counterfeit Register': 'M15-qregister',
  'M15:RTV & Credit Recovery': 'M15-rtvreg',
  'M15:Stockout & Unmet Demand': 'M15-stockouts',
  'M15:Branch Stock Position': 'M15-position',
  'M15:Slow & Fast Movers': 'M15-movers'
};

export const FORM_MODELS = {
  'M15:Goods Receipt (inspection gate)': 'fix.stock.receipt',
  'M15:Stock Issue': 'fix.stock.consumption',
  'M15:Transfer Request': 'fix.stock.transfer',
  'M15:Cycle Count': 'fix.stock.count',
  'M15:Scrap Order': 'fix.stock.quarantine',
  'M15:Item Master (7 tabs)': 'fix.spare.part',
  'M15:Stock Location': 'fix.stock.location',
  'M15:Ownership-Class Change': 'fix.stock.class.change',
  'M15:Reorder Rule': 'fix.reorder.rule',
  'M15:Return to Vendor': 'fix.stock.rtv',
  'M15:Stock Reservation': 'fix.stock.reservation',
  'M15:Backorder': 'fix.stock.backorder',
  'M15:Stock Recall': 'fix.stock.recall',
  'M15:Consignment Statement': 'fix.consignment.reconciliation'
};

export const FORM_CHIPS = {
  'M15:Goods Receipt (inspection gate)': 'M15-form-receipt',
  'M15:Stock Issue': 'M15-form-issue',
  'M15:Transfer Request': 'M15-form-transfer',
  'M15:Cycle Count': 'M15-form-count',
  'M15:Scrap Order': 'M15-form-scrap',
  'M15:Item Master (7 tabs)': 'M15-form-part',
  /* the location master is M41's form (one form, two modules' pages) */
  'M15:Stock Location': 'M41-form-stock-location',
  'M15:Ownership-Class Change': 'M15-form-classchange',
  'M15:Reorder Rule': 'M15-form-reorder',
  'M15:Return to Vendor': 'M15-form-rtv',
  'M15:Stock Reservation': 'M15-form-reservation',
  'M15:Backorder': 'M15-form-backorder',
  'M15:Stock Recall': 'M15-form-recall',
  'M15:Consignment Statement': 'M15-form-consignment',
  'M15:__by_model__': {
    'fix.stock.reservation': 'M15-form-reservation',
    'fix.stock.backorder': 'M15-form-backorder',
    'fix.stock.recall': 'M15-form-recall',
    'fix.consignment.reconciliation': 'M15-form-consignment',
    'fix.spare.part': 'M15-form-part',
    'fix.stock.location': 'M41-form-stock-location',
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
    'M15-parts': 'M15-form-part',
    'M15-onhand': 'M15-form-onhand',
    'M15-locations': 'M41-form-stock-location',
    'M15-movements': 'M15-form-issue',
    'M15-serials': 'M15-form-lot',
    'M15-replen': 'M15-form-reorder',
    'M15-recon': 'M15-form-recon',
    'M15-counts': 'M15-form-count',
    'M15-transfers': 'M15-form-transfer',
    'M15-quarantine': 'M15-form-scrap',
    'M15-rtv': 'M15-form-rtv',
    'M15-receipts': 'M15-form-receipt',
    'M15-classchange': 'M15-form-classchange',
    'M15-reservations': 'M15-form-reservation',
    'M15-backorders': 'M15-form-backorder',
    'M15-recalls': 'M15-form-recall',
    'M15-consignment': 'M15-form-consignment'
  }
};

export const CREATE = {
  M15: { screen: 'M15-form-receipt', model: 'fix.stock.receipt', label: 'Goods Receipt' }
};
