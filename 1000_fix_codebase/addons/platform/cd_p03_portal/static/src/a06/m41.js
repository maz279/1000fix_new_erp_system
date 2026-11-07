/** @odoo-module **/
/* A06 · Supply Chain — M41 Warehouse Management (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 78.
 * Warehouse/zone/bin existed; slotting, dock appointments, put-away, waves,
 * cartons, staging, tasks, bin floor counts, templates and packing stations
 * are new. Bin slots are a breakdown of the M15 ledger: put-away, pick, ship
 * and approved counts move it; no form types a stock quantity (A06 R1). */

export const MODULE = {
  area: 'A06', code: 'M41', en: 'Warehouse Management', title: 'M41 · Warehouse Management',
  bn: 'ওয়্যারহাউস ম্যানেজমেন্ট', icon: '🏭',
  desc: 'Zones, aisles and bins, slotting and re-slotting, dock appointments, scan receiving, directed put-away, wave planning, pick strategies, packing and cartons, staging and load, the RF work queue, task management and bin-level floor counts.',
  kpis: [
    { l: 'Open Tasks', m: 'open_tasks' },
    { l: 'Waves In Progress', m: 'waves_in_progress' },
    { l: 'Bins Slotted', m: 'bins_slotted' },
    { l: 'Pick Accuracy', m: 'pick_accuracy_pct', suffix: '%' },
    { l: 'Docks Today', m: 'docks_today' },
    { l: 'Bin Utilisation', m: 'bin_utilisation_pct', suffix: '%' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M41-stock-location', en: "Stock Location", bn: "Stock Location", t: 'g' },
      { id: 'M41-inventory-valuation-suspense', en: "Inventory Valuation Suspense", bn: "Inventory Valuation Suspense", t: 'g' },
      { id: 'M41-spare-part', en: "Spare Part", bn: "Spare Part", t: 'g' },
      { id: 'M41-warehouse', en: "Warehouse", bn: "Warehouse", t: 'g' }
    ]},
    { en: 'Structure', screens: [
      { id: 'M41-wh-zones', en: 'Warehouse Zones', bn: 'ওয়্যারহাউস জোন', t: 'g' },
      { id: 'M41-zones', en: 'Zones, Aisles & Bins', bn: 'জোন ও বিন', t: 'g' },
      { id: 'M41-slotting', en: 'Slotting & Re-Slotting', bn: 'স্লটিং', t: 'g' }
    ]},
    { en: 'Inbound', screens: [
      { id: 'M41-docks', en: 'Dock Appointments', bn: 'ডক অ্যাপয়েন্টমেন্ট', t: 'g' },
      { id: 'M41-receiving', en: 'Scan Receiving', bn: 'স্ক্যান রিসিভিং', t: 'c' },
      { id: 'M41-putaway', en: 'Directed Put-Away', bn: 'ডিরেক্টেড পুট-অ্যাওয়ে', t: 'g' }
    ]},
    { en: 'Outbound', screens: [
      { id: 'M41-waves', en: 'Wave Planning', bn: 'ওয়েভ প্ল্যানিং', t: 'c' },
      { id: 'M41-pick-lines', en: 'Pick Lines', bn: 'পিক লাইন', t: 'g' },
      { id: 'M41-picking', en: 'Pick Strategies', bn: 'পিক কৌশল', t: 'g' },
      { id: 'M41-packing', en: 'Packing & Cartons', bn: 'প্যাকিং', t: 'g' },
      { id: 'M41-staging', en: 'Staging & Load', bn: 'স্টেজিং ও লোড', t: 'g' }
    ]},
    { en: 'Floor Ops', screens: [
      { id: 'M41-rf', en: 'RF Mobile App', bn: 'আরএফ কিউ', t: 'd' },
      { id: 'M41-tasks', en: 'Task Management', bn: 'টাস্ক ম্যানেজমেন্ট', t: 'g' },
      { id: 'M41-counting', en: 'Floor Counts', bn: 'ফ্লোর কাউন্ট', t: 'g' }
    ]}
  ],
  reports: ['Throughput by Shift', 'Pick Accuracy Trend', 'Wave Cycle Time', 'Labour Productivity', 'Bin Utilisation Heatmap'],
  forms: ['Bin', 'Wave Template', 'Dock Appointment', 'Packing Station Config'],
  cross: ['M15 stock ledger', 'M16 goods receipt', 'M03 outbound staging', 'M44 import receiving'],
  freg: { src: 78, sub: [
    ['1', 'Physical Structure', 8, { model: 'fix.warehouse.bin', cols: ['name', 'zone_id', 'barcode', 'capacity_qty'], screens: ['M41-zones', 'M41-warehouse', 'M41-stock-location'] }],
    ['2', 'Slotting', 7, { model: 'fix.wms.slot', cols: ['part_id', 'bin_id', 'velocity', 'slot_type', 'state'], screens: ['M41-slotting'] }],
    ['3', 'Inbound & Put-Away', 12, { model: 'fix.wms.putaway', cols: ['name', 'part_id', 'qty', 'to_bin_id', 'state'], screens: ['M41-docks', 'M41-receiving', 'M41-putaway'] }],
    ['4', 'Wave Planning', 9, { model: 'fix.wms.wave', cols: ['name', 'wave_date', 'strategy', 'released_at', 'state'], screens: ['M41-waves'] }],
    ['5', 'Picking', 11, { model: 'fix.wms.task', cols: ['name', 'part_id', 'bin_id', 'qty', 'state'], screens: ['M41-picking', 'M41-tasks'], domain: [['task_type', '=', 'pick']] }],
    ['6', 'Packing & Staging', 8, { model: 'fix.wms.carton', cols: ['name', 'wave_id', 'carton_size', 'weight_kg', 'state'], screens: ['M41-packing', 'M41-staging'] }],
    ['7', 'Replenishment', 6, { model: 'fix.spare.part', cols: ['name', 'part_number', 'qty_available', 'min_qty', 'max_qty'], screens: ['M41-spare-part', 'M41-tasks'] }],
    ['8', 'RF Execution', 8, { model: 'fix.wms.task', cols: ['name', 'task_type', 'bin_id', 'assignee_id', 'state'], screens: ['M41-rf', 'M41-tasks'] }],
    ['9', 'Labour & Analytics', 9, { model: 'fix.wms.task', cols: ['assignee_id', 'task_type', 'qty', 'done_at', 'state'], screens: ['M41-tasks', 'M41-counting', 'M41-inventory-valuation-suspense'] }]
  ] }
};

export const SCREENS = {
  'M41-wh-zones': { kind: 'model_list', model: 'fix.warehouse.zone',
    cols: ['name', 'code', 'warehouse_id', 'zone_type', 'reservable'] },
  'M41-zones': { kind: 'model_list', model: 'fix.warehouse.bin',
    cols: ['name', 'zone_id', 'barcode', 'capacity_qty', 'blocked', 'block_reason'],
    actions: [
      { m: 'action_block', l: 'Block Bin', ask: 'Reason the bin is blocked', kwarg: 'reason' },
      { m: 'action_unblock', l: 'Unblock Bin (controller)', ask: 'Why the block is lifted', kwarg: 'note' }
    ] },
  'M41-slotting': { kind: 'model_list', model: 'fix.wms.slot', stateField: 'state',
    cols: ['part_id', 'bin_id', 'zone_id', 'qty', 'reserved_qty', 'velocity', 'slot_type', 'last_slotted_on', 'state'],
    actions: [
      { m: 'action_block', l: 'Block Whole Bin', ask: 'Reason the bin is blocked', kwarg: 'reason' },
      { m: 'action_unblock', l: 'Unblock Bin (controller)', ask: 'Why the block is lifted', kwarg: 'note' }
    ] },
  'M41-docks': { kind: 'model_list', model: 'fix.wms.dock', stateField: 'state',
    cols: ['name', 'dock_no', 'partner_id', 'carrier', 'dock_type', 'slot_start', 'slot_end', 'state'],
    actions: [
      { m: 'action_check_in', l: 'Check In' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M41-receiving': { kind: 'model_list', model: 'fix.stock.receipt', stateField: 'state', create: false,
    cols: ['name', 'partner_id', 'location_id', 'received_on', 'state'] },
  'M41-putaway': { kind: 'model_list', model: 'fix.wms.putaway', stateField: 'state',
    cols: ['name', 'part_id', 'qty', 'to_bin_id', 'receipt_line_id', 'assignee_id', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete Put-Away', asks: [
      { label: 'Scan the target bin', kwarg: 'bin_code' },
      { label: 'Scan the item', kwarg: 'item_code' }
    ] }] },
  'M41-waves': { kind: 'model_list', model: 'fix.wms.wave', stateField: 'state',
    cols: ['name', 'wave_date', 'strategy', 'released_at', 'shipped_at', 'pick_all_reason', 'cancel_reason', 'state'],
    actions: [
      { m: 'action_release', l: 'Release (supervisor)' },
      { m: 'action_pick_all', l: 'Pick All Without Scans (supervisor exception)', ask: 'Why this wave is picked without scanning', kwarg: 'reason' },
      { m: 'action_accept_short', l: 'Accept Short Pick' },
      { m: 'action_packed', l: 'Mark Packed' },
      { m: 'action_stage', l: 'Mark Staged' },
      { m: 'action_ship', l: 'Ship Wave' },
      { m: 'action_cancel', l: 'Cancel Wave (supervisor)', ask: 'Why the wave is cancelled', kwarg: 'reason' }
    ] },
  'M41-pick-lines': { kind: 'model_list', model: 'fix.wms.wave.line', stateField: 'state', create: false,
    cols: ['wave_id', 'part_id', 'bin_id', 'qty', 'reserved_qty', 'picked_qty', 'lot_id', 'scanned_bin', 'scanned_item', 'state'],
    actions: [
      { m: 'action_scan_pick', l: 'Scan Pick', asks: [
        { label: 'Scan the bin', kwarg: 'bin_code' },
        { label: 'Scan the item', kwarg: 'item_code' },
        { label: 'Scan the serial (serialized parts; otherwise leave empty)', kwarg: 'serial' }
      ] }
    ] },
  'M41-picking': { kind: 'table_report', module: 'M41', report: 'pick_strategy', title: 'Pick Strategies', period: false },
  'M41-packing': { kind: 'model_list', model: 'fix.wms.carton', stateField: 'state',
    cols: ['name', 'wave_id', 'carton_size', 'weight_kg', 'contents_qty', 'state'],
    actions: [{ m: 'action_seal', l: 'Seal Carton' }] },
  'M41-staging': { kind: 'model_list', model: 'fix.wms.stage', stateField: 'state',
    cols: ['name', 'wave_id', 'lane', 'load_ref', 'state'],
    actions: [
      { m: 'action_load', l: 'Load', ask: 'Scan every carton of this load, separated by spaces', kwarg: 'carton_scans' },
      { m: 'action_dispatch', l: 'Dispatch' }
    ] },
  'M41-rf': { kind: 'table_report', module: 'M41', report: 'rf_queue', title: 'RF Mobile App', period: false },
  'M41-tasks': { kind: 'model_list', model: 'fix.wms.task', stateField: 'state',
    cols: ['name', 'task_type', 'ref', 'part_id', 'bin_id', 'qty', 'assignee_id', 'state'],
    actions: [
      { m: 'action_assign', l: 'Assign' },
      { m: 'action_done', l: 'Complete Task', ask: 'Scan the bin, then the item, then any serial (pick and put-away tasks), e.g. A-01-01 FX-1001', kwarg: 'scan' },
      { m: 'action_cancel', l: 'Cancel Task' }
    ] },
  'M41-counting': { kind: 'model_list', model: 'fix.wms.floor.count', stateField: 'state',
    cols: ['name', 'bin_id', 'part_id', 'counted_qty', 'counted_on', 'stock_count_id', 'state'],
    actions: [{ m: 'action_post', l: 'Post Count' }] },

  /* Report chips -> their own computed pack */
  'M41-rpt-throughput': { kind: 'table_report', module: 'M41', report: 'throughput_by_shift', title: 'Throughput by Shift', period: false },
  'M41-rpt-accuracy': { kind: 'table_report', module: 'M41', report: 'pick_accuracy', title: 'Pick Accuracy Trend', period: false },
  'M41-rpt-cycle': { kind: 'table_report', module: 'M41', report: 'wave_cycle_time', title: 'Wave Cycle Time', period: false },
  'M41-rpt-labour': { kind: 'table_report', module: 'M41', report: 'labour_productivity', title: 'Labour Productivity', period: false },
  'M41-rpt-bins': { kind: 'table_report', module: 'M41', report: 'bin_utilisation', title: 'Bin Utilisation Heatmap', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M41-form-bin': {
    kind: 'model_form',
    model: 'fix.warehouse.bin',
    title: 'Bin',
    back: 'M41-zones',
    sections: [
      { title: 'Bin', note: 'Capacity 0 means unconstrained; a put-away that would exceed a capacity is refused. Hazardous parts go only into hazardous-class bins.',
        fields: [
          { name: 'name', required: true, label: 'Bin' },
          { name: 'zone_id', required: true, label: 'Zone' },
          { name: 'barcode', label: 'Barcode' },
          { name: 'capacity_qty', label: 'Capacity' },
          { name: 'storage_class', required: true, label: 'Storage Class' },
          { name: 'ownership_class', required: true, label: 'Ownership Class' },
          { name: 'blocked', label: 'Blocked', readonly: true },
          { name: 'block_reason', label: 'Block Reason', readonly: true }
        ] }
    ]
  },

  'M41-form-zone': {
    kind: 'model_form',
    model: 'fix.warehouse.zone',
    title: 'Warehouse Zone',
    back: 'M41-wh-zones',
    sections: [
      { title: 'Zone', note: 'Stock in a quarantine or inspection zone is not reservable or pickable: a put-away or wave from its bins is refused.',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'name', required: true, label: 'Zone' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'zone_type', required: true, label: 'Zone Type' },
          { name: 'reservable', label: 'Reservable', readonly: true }
        ] }
    ]
  },

  'M41-form-slot': {
    kind: 'model_form',
    model: 'fix.wms.slot',
    title: 'Slot',
    back: 'M41-slotting',
    status: { field: 'state', labels: { active: 'Active', blocked: 'Blocked' } },
    sections: [
      { title: 'Slot', note: 'One slot per part and bin. The quantity is moved only by put-away, pick and approved counts; blocking and unblocking are actions (a controller unblocks).',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part', domain: [['state', '=', 'active']] },
          { name: 'bin_id', required: true, label: 'Bin', domain: [['zone_id.reservable', '=', true], ['blocked', '=', false]] },
          { name: 'qty', label: 'Quantity in Bin', readonly: true },
          { name: 'reserved_qty', label: 'Allocated to Waves', readonly: true },
          { name: 'velocity', required: true, label: 'Velocity' },
          { name: 'slot_type', required: true, label: 'Slot Type' },
          { name: 'last_slotted_on', label: 'Last Slotted', readonly: true },
          { name: 'block_reason', label: 'Block Reason', readonly: true }
        ] }
    ]
  },

  'M41-form-dock': {
    kind: 'model_form',
    model: 'fix.wms.dock',
    title: 'Dock Appointment',
    back: 'M41-docks',
    status: { field: 'state', labels: {
      scheduled: 'Scheduled', checked_in: 'Checked In',
      completed: 'Completed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Appointment', note: 'One appointment per dock per window. An inbound appointment completes with the goods receipt it delivered.',
        fields: [
          { name: 'dock_no', required: true, label: 'Dock' },
          { name: 'partner_id', label: 'Partner / Carrier' },
          { name: 'carrier', label: 'Carrier Name' },
          { name: 'dock_type', required: true, label: 'Type' },
          { name: 'slot_start', required: true, label: 'Window Start' },
          { name: 'slot_end', required: true, label: 'Window End' },
          { name: 'receipt_id', label: 'Goods Receipt' },
          { name: 'wave_id', label: 'Outbound Wave' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M41-form-putaway': {
    kind: 'model_form',
    model: 'fix.wms.putaway',
    title: 'Directed Put-Away',
    back: 'M41-putaway',
    status: { field: 'state', labels: { pending: 'Pending', done: 'Done' } },
    sections: [
      { title: 'Put-Away', note: 'Puts away stock a POSTED goods-receipt line accepted, up to what is not yet put away, into a bin of the same warehouse (capacity, zone, blocked and hazard rules apply).',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'receipt_line_id', required: true, label: 'Received Line', domain: [['is_posted', '=', true]] },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'to_bin_id', required: true, label: 'Target Bin', domain: [['zone_id.reservable', '=', true], ['blocked', '=', false]] },
          { name: 'lot_id', label: 'Serial / Lot', domain: [['status', '=', 'in_stock']] },
          { name: 'from_ref', label: 'Source Reference' },
          { name: 'assignee_id', label: 'Assigned To' }
        ] }
    ]
  },

  'M41-form-wave': {
    kind: 'model_form',
    model: 'fix.wms.wave',
    title: 'Pick Wave',
    back: 'M41-waves',
    status: { field: 'state', labels: {
      draft: 'Draft', released: 'Released', picking: 'Picking', packed: 'Packed',
      staged: 'Staged', shipped: 'Shipped', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Wave', note: 'A supervisor releases: every line is allocated in M15 and on its bin (over-allocation is refused) and becomes a pick task. Each line is picked by scanning its bin and item (Pick Lines); picking without scans is a supervisor exception with a reason. Pack needs sealed cartons, ship a loaded stage with a scanned manifest.',
        fields: [
          { name: 'wave_date', required: true, label: 'Wave Date' },
          { name: 'strategy', required: true, label: 'Strategy' },
          { name: 'warehouse_id', label: 'Warehouse' },
          { name: 'pick_all_reason', label: 'Pick-All Exception Reason', readonly: true },
          { name: 'pick_all_by_id', label: 'Pick-All Exception By', readonly: true },
          { name: 'cancel_reason', label: 'Cancellation Reason', readonly: true },
          { name: 'cancelled_by_id', label: 'Cancelled By', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Wave Lines',
      note: 'Each line picks a quantity of a part from a bin; picked quantity can never exceed the wave quantity.',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part', domain: [['state', '=', 'active']] },
        { name: 'bin_id', label: 'Pick Bin', domain: [['zone_id.reservable', '=', true], ['blocked', '=', false]] },
        { name: 'qty', required: true, label: 'Quantity' }
      ]
    }
  },

  'M41-form-wave-line': {
    kind: 'model_form',
    model: 'fix.wms.wave.line',
    title: 'Pick Line',
    back: 'M41-pick-lines',
    status: { field: 'state', labels: {
      pending: 'Pending', picked: 'Picked', short: 'Short', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Pick Line', note: 'Read-only: a line is picked by the Scan Pick action, which checks the bin, the item and any serial. The wave holds the line.',
        fields: [
          { name: 'wave_id', label: 'Wave', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'bin_id', label: 'Pick Bin', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'reserved_qty', label: 'Allocated', readonly: true },
          { name: 'picked_qty', label: 'Picked', readonly: true },
          { name: 'lot_id', label: 'Picked Serial', readonly: true },
          { name: 'scanned_bin', label: 'Scanned Bin', readonly: true },
          { name: 'scanned_item', label: 'Scanned Item', readonly: true },
          { name: 'picked_by_id', label: 'Picked By', readonly: true }
        ] }
    ]
  },

  'M41-form-carton': {
    kind: 'model_form',
    model: 'fix.wms.carton',
    title: 'Carton',
    back: 'M41-packing',
    status: { field: 'state', labels: {
      open: 'Open', sealed: 'Sealed', dispatched: 'Dispatched' } },
    sections: [
      { title: 'Carton', note: 'A carton is sealed for a wave being packed, with its contents and weight; the sealed contents must reconcile to the picked lines.',
        fields: [
          { name: 'wave_id', required: true, label: 'Wave', domain: [['state', '=', 'picking']] },
          { name: 'carton_size', required: true, label: 'Carton Size' },
          { name: 'weight_kg', label: 'Weight (kg)' },
          { name: 'contents_qty', label: 'Contents (pcs)' }
        ] }
    ]
  },

  'M41-form-stage': {
    kind: 'model_form',
    model: 'fix.wms.stage',
    title: 'Staging Record',
    back: 'M41-staging',
    status: { field: 'state', labels: {
      staging: 'Staging', loaded: 'Loaded', dispatched: 'Dispatched' } },
    sections: [
      { title: 'Stage & Load', note: 'Load a staged wave with its load / vehicle reference by scanning every sealed carton, then dispatch: dispatching ships the wave.',
        fields: [
          { name: 'wave_id', required: true, label: 'Wave', domain: [['state', 'in', ['packed', 'staged']]] },
          { name: 'lane', required: true, label: 'Staging Lane' },
          { name: 'load_ref', label: 'Load / Vehicle Ref' },
          { name: 'manifest_verified', label: 'Manifest Verified', readonly: true },
          { name: 'manifest_scan', label: 'Scanned Manifest', readonly: true }
        ] }
    ]
  },

  'M41-form-task': {
    kind: 'model_form',
    model: 'fix.wms.task',
    title: 'Warehouse Task',
    back: 'M41-tasks',
    status: { field: 'state', labels: {
      open: 'Open', assigned: 'Assigned', done: 'Done', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Task', note: 'Only the assigned operative completes a task; a pick or put-away task completes the movement it represents, a count task its floor count. An operative may claim a free task; only a supervisor reassigns one.',
        fields: [
          { name: 'task_type', required: true, label: 'Task Type' },
          { name: 'ref', label: 'Reference' },
          { name: 'part_id', label: 'Spare Part' },
          { name: 'bin_id', label: 'Bin' },
          { name: 'qty', label: 'Quantity' },
          { name: 'wave_line_id', label: 'Wave Line', domain: [['state', '=', 'pending']] },
          { name: 'putaway_id', label: 'Put-Away', domain: [['state', '=', 'pending']] },
          { name: 'floor_count_id', label: 'Floor Count', domain: [['state', 'in', ['draft', 'recount', 'submitted']]] },
          { name: 'assignee_id', label: 'Assignee' }
        ] }
    ]
  },

  'M41-form-floor-count': {
    kind: 'model_form',
    model: 'fix.wms.floor.count',
    title: 'Floor Count',
    back: 'M41-counting',
    status: { field: 'state', labels: {
      draft: 'Draft', recount: 'Recount Required', submitted: 'Submitted to M15',
      posted: 'Posted', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Count', note: 'Blind bin count: the system takes the expected quantity. A variance is recounted, then submitted to M15 for Inventory Controller approval; the bin moves when that count posts.',
        fields: [
          { name: 'bin_id', required: true, label: 'Bin' },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'counted_qty', label: 'Counted' },
          { name: 'reason_code', label: 'Variance Reason (after recount)' },
          { name: 'counted_on', required: true, label: 'Counted On' },
          { name: 'stock_count_id', label: 'M15 Count', readonly: true }
        ] }
    ]
  },

  'M41-form-template': {
    kind: 'model_form',
    model: 'fix.wms.wave.template',
    title: 'Wave Template',
    back: 'M41-waves',
    sections: [
      { title: 'Template', note: 'A template fixes the picking strategy and cut-off for recurring waves.',
        fields: [
          { name: 'name', required: true, label: 'Template' },
          { name: 'strategy', required: true, label: 'Strategy' },
          { name: 'zone_id', label: 'Zone' },
          { name: 'cutoff', label: 'Cut-off (HH:MM)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M41-form-station': {
    kind: 'model_form',
    model: 'fix.wms.packing.station',
    title: 'Packing Station',
    back: 'M41-packing',
    sections: [
      { title: 'Station', fields: [
          { name: 'name', required: true, label: 'Station' },
          { name: 'lane', label: 'Lane' },
          { name: 'printer', label: 'Label Printer' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M41-stock-location': { kind: 'model_list', model: 'fix.stock.location', stateField: 'state',
    cols: ['name', 'code', 'location_type', 'technician_id', 'branch_id', 'state', 'active', 'company_id', 'operating_unit_id', 'name_bn'],
    actions: [
      { m: 'action_set_active', l: 'Activate (controller)' },
      { m: 'action_set_inactive', l: 'Deactivate (controller)' },
      { m: 'action_audit_van_stock', l: 'Audit Van Stock (controller)', asks: [
        { label: 'Lines audited', kwarg: 'audited_count', number: true },
        { label: 'Lines with a discrepancy', kwarg: 'discrepancy_count', number: true }
      ] }
    ] },
  'M41-inventory-valuation-suspense': { kind: 'model_list', model: 'fix.inventory.valuation.suspense',
    cols: ['name', 'company_id', 'product_id', 'operating_unit_id', 'name_bn', 'consumption_id', 'quantity'] },
  'M41-spare-part': { kind: 'model_list', model: 'fix.spare.part', stateField: 'state',
    cols: ['name', 'part_number', 'product_id', 'is_serialized', 'uom', 'state', 'active', 'company_id', 'operating_unit_id', 'name_bn'],
    actions: [
      { m: 'action_discontinue', l: 'Discontinue (controller)' },
      { m: 'action_mark_obsolete', l: 'Mark Obsolete (controller)' },
      { m: 'action_reactivate', l: 'Reactivate (controller)' },
      { m: 'action_set_standard_cost', l: 'Set Standard Cost (controller)', asks: [
        { label: 'New standard cost (BDT)', kwarg: 'cost', number: true }
      ] }
    ] },
  'M41-warehouse': { kind: 'model_list', model: 'fix.warehouse',
    cols: ['name', 'code', 'active', 'company_id', 'operating_unit_id', 'branch_id'] },

  'M41-form-stock-location': {
    kind: 'model_form',
    model: 'fix.stock.location',
    title: "Stock Location",
    back: 'M41-stock-location',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', inactive: 'Inactive' } },
    sections: [
      { title: "Stock Location", note: "A van names its custodian technician: only that technician (or an Inventory Controller) issues from it, and only an Inventory Controller changes the custodian or the location type. An inactive location moves no stock.",
        fields: [
          { name: 'name', required: true, label: "Location Name" },
          { name: 'code', required: true, label: "Location Code" },
          { name: 'location_type', required: true, label: "Location Type" },
          { name: 'technician_id', label: "Custodian Technician (vans)" },
          { name: 'van_plate', label: "Vehicle Plate (vans)" },
          { name: 'branch_id', label: "Branch Hub" },
          { name: 'parent_id', label: "Parent Location" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'active', label: "Active" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'name_bn', label: "লোকেশন নাম (বাংলা)" }
        ] }
    ]
  },
  'M41-form-inventory-valuation-suspense': {
    kind: 'model_form',
    model: 'fix.inventory.valuation.suspense',
    title: "Inventory Valuation Suspense",
    back: 'M41-inventory-valuation-suspense',
    sections: [
      { title: "Inventory Valuation Suspense", note: "Read-only: the stock movements write these entries and only the M19 GL cutover reconciles them.",
        fields: [
          { name: 'name', label: "Entry Reference", readonly: true },
          { name: 'company_id', label: "Company", readonly: true },
          { name: 'product_id', label: "Spare Part", readonly: true },
          { name: 'entry_type', label: "Entry Type", readonly: true },
          { name: 'quantity', label: "Movement Quantity", readonly: true },
          { name: 'total_valuation', label: "Total Valuation", readonly: true },
          { name: 'status', label: "GL Status", readonly: true },
          { name: 'operating_unit_id', label: "Operating Unit", readonly: true },
          { name: 'consumption_id', label: "Originating Consumption", readonly: true }
        ] }
    ]
  },
  'M41-form-spare-part': {
    kind: 'model_form',
    model: 'fix.spare.part',
    title: "Spare Part",
    back: 'M41-spare-part',
    status: { field: 'state', labels: { active: 'Active', discontinued: 'Discontinued', obsolete: 'Obsolete' } },
    sections: [
      { title: "Spare Part", note: "Map the part to the product M16 buys it as: a PO goods receipt of an unmapped product does not reach this ledger. A discontinued part is run down and no longer bought; an obsolete part is not issued. Status and standard cost change only by the controller's actions.",
        fields: [
          { name: 'name', required: true, label: "Part Description" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'part_number', required: true, label: "Part Number / SKU" },
          { name: 'product_id', label: "Purchased As (Product)" },
          { name: 'barcode', label: "Barcode" },
          { name: 'uom', label: "Unit of Measure" },
          { name: 'is_serialized', label: "Serialized (one serial per unit)" },
          { name: 'storage_class', label: "Storage Class" },
          { name: 'active', label: "Active" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'name_bn', label: "যন্ত্রাংশের নাম (বাংলা)" }
        ] }
    ]
  },
  'M41-form-warehouse': {
    kind: 'model_form',
    model: 'fix.warehouse',
    title: "Warehouse",
    back: 'M41-warehouse',
    sections: [
      { title: "Warehouse", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'code', required: true, label: "Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'active', label: "Active" },
          { name: 'branch_id', label: "Branch" },
          { name: 'stock_location_id', label: "M15 Stock Location" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M41:Throughput by Shift': 'M41-rpt-throughput',
  'M41:Pick Accuracy Trend': 'M41-rpt-accuracy',
  'M41:Wave Cycle Time': 'M41-rpt-cycle',
  'M41:Labour Productivity': 'M41-rpt-labour',
  'M41:Bin Utilisation Heatmap': 'M41-rpt-bins'
};

export const FORM_MODELS = {
  'M41:Bin': 'fix.warehouse.bin',
  'M41:Wave Template': 'fix.wms.wave.template',
  'M41:Dock Appointment': 'fix.wms.dock',
  'M41:Packing Station Config': 'fix.wms.packing.station'
};

export const FORM_CHIPS = {
  'M41:Bin': 'M41-form-bin',
  'M41:Wave Template': 'M41-form-template',
  'M41:Dock Appointment': 'M41-form-dock',
  'M41:Packing Station Config': 'M41-form-station',
  'M41:__by_model__': {
    'fix.stock.location': 'M41-form-stock-location',
    'fix.inventory.valuation.suspense': 'M41-form-inventory-valuation-suspense',
    'fix.spare.part': 'M41-form-spare-part',
    'fix.warehouse': 'M41-form-warehouse',
    'fix.warehouse.bin': 'M41-form-bin',
    'fix.warehouse.zone': 'M41-form-zone',
    'fix.wms.wave.line': 'M41-form-wave-line',
    'fix.stock.receipt': 'M15-form-receipt',
    'fix.wms.slot': 'M41-form-slot',
    'fix.wms.dock': 'M41-form-dock',
    'fix.wms.putaway': 'M41-form-putaway',
    'fix.wms.wave': 'M41-form-wave',
    'fix.wms.carton': 'M41-form-carton',
    'fix.wms.stage': 'M41-form-stage',
    'fix.wms.task': 'M41-form-task',
    'fix.wms.floor.count': 'M41-form-floor-count',
    'fix.wms.wave.template': 'M41-form-template',
    'fix.wms.packing.station': 'M41-form-station'
  },
  'M41:__by_screen__': {
    'M41-stock-location': 'M41-form-stock-location',
    'M41-inventory-valuation-suspense': 'M41-form-inventory-valuation-suspense',
    'M41-spare-part': 'M41-form-spare-part',
    'M41-warehouse': 'M41-form-warehouse',
    'M41-wh-zones': 'M41-form-zone',
    'M41-zones': 'M41-form-bin',
    'M41-slotting': 'M41-form-slot',
    'M41-docks': 'M41-form-dock',
    'M41-receiving': 'M15-form-receipt',
    'M41-putaway': 'M41-form-putaway',
    'M41-waves': 'M41-form-wave',
    'M41-pick-lines': 'M41-form-wave-line',
    'M41-packing': 'M41-form-carton',
    'M41-staging': 'M41-form-stage',
    'M41-tasks': 'M41-form-task',
    'M41-counting': 'M41-form-floor-count'
  }
};

export const CREATE = {
  M41: { screen: 'M41-form-dock', model: 'fix.wms.dock', label: 'Dock Appointment' }
};
