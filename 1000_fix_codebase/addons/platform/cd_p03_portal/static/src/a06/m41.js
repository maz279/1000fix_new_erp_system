/** @odoo-module **/
/* A06 · Supply Chain — M41 Warehouse Management (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 78,
 * plus the floor-record screens of the capture audit (2026-11-14).
 * Warehouse/zone/bin existed; slotting, dock appointments, put-away, waves,
 * cartons, staging, tasks, bin floor counts, templates and packing stations
 * are new. Bin slots are a breakdown of the M15 ledger: put-away, pick, ship
 * and approved counts move it; no form types a stock quantity (A06 R1).
 *
 * Capture audit 2026-11-14: pages 5 Picking, 7 Replenishment, 8 RF Execution
 * and 9 Labour & Analytics captured nothing, and 1, 2, 4 and 6 offered only part
 * of what they list (zones, slots, staging, picks had no form chip; the zone,
 * pick-line, template and station lists sat on no page). Every page now
 * captures the spec's own record: internal moves and pick-face replenishment
 * (FR-WMS-028/029), scan and short picks (FR-WMS-023/024), task claim and scan
 * completion (FR-WMS-036/038), RF device enrolment (T-15), operative profiles
 * and handling equipment (FR-WMS-039, BRU-WMS-18). */

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
      { id: 'M41-receiving', en: 'Scan Receiving', bn: 'স্ক্যান রিসিভিং', t: 'g' },
      { id: 'M41-putaway', en: 'Directed Put-Away', bn: 'ডিরেক্টেড পুট-অ্যাওয়ে', t: 'g' }
    ]},
    { en: 'Outbound', screens: [
      { id: 'M41-waves', en: 'Wave Planning', bn: 'ওয়েভ প্ল্যানিং', t: 'g' },
      { id: 'M41-pick-lines', en: 'Pick Lines', bn: 'পিক লাইন', t: 'g' },
      { id: 'M41-picking', en: 'Pick Strategies', bn: 'পিক কৌশল', t: 'r' },
      { id: 'M41-packing', en: 'Packing & Cartons', bn: 'প্যাকিং', t: 'g' },
      { id: 'M41-staging', en: 'Staging & Load', bn: 'স্টেজিং ও লোড', t: 'g' },
      { id: 'M41-wave-templates', en: 'Wave Templates', bn: 'ওয়েভ টেমপ্লেট', t: 'g' },
      { id: 'M41-packing-stations', en: 'Packing Stations', bn: 'প্যাকিং স্টেশন', t: 'g' }
    ]},
    { en: 'Floor Ops', screens: [
      { id: 'M41-rf', en: 'RF Mobile App', bn: 'আরএফ কিউ', t: 'r' },
      { id: 'M41-tasks', en: 'Task Management', bn: 'টাস্ক ম্যানেজমেন্ট', t: 'g' },
      { id: 'M41-counting', en: 'Floor Counts', bn: 'ফ্লোর কাউন্ট', t: 'g' },
      { id: 'M41-moves', en: 'Internal Moves & Replenishment', bn: 'অভ্যন্তরীণ স্থানান্তর ও রিপ্লেনিশমেন্ট', t: 'g' },
      { id: 'M41-devices', en: 'RF Devices', bn: 'আরএফ ডিভাইস', t: 'g' },
      { id: 'M41-operatives', en: 'Operative Profiles', bn: 'অপারেটিভ প্রোফাইল', t: 'g' },
      { id: 'M41-equipment', en: 'Handling Equipment', bn: 'হ্যান্ডলিং সরঞ্জাম', t: 'g' }
    ]}
  ],
  reports: ['Throughput by Shift', 'Pick Accuracy Trend', 'Wave Cycle Time', 'Labour Productivity', 'Bin Utilisation Heatmap'],
  forms: ['Bin', 'Wave Template', 'Dock Appointment', 'Packing Station Config',
    'Warehouse', 'Warehouse Zone', 'Slot Assignment', 'Directed Put-Away', 'Goods Receipt (scan receiving)',
    'Pick Wave', 'Scan a Pick', 'Report a Short Pick', 'Carton', 'Staging Record',
    'Internal Move / Replenishment', 'Confirm a Move by Scan',
    'Complete a Task by Scan', 'Claim a Task', 'Warehouse Task', 'RF Device',
    'Operative Profile', 'Handling Equipment', 'Floor Count'],
  cross: ['M15 stock ledger', 'M16 goods receipt', 'M03 outbound staging', 'M44 import receiving'],
  freg: { src: 78, sub: [
    /* FR-WMS-001..004: warehouse -> zones -> bins */
    ['1', 'Physical Structure', 8, { model: 'fix.warehouse.bin', cols: ['name', 'zone_id', 'barcode', 'capacity_qty'], screens: ['M41-zones', 'M41-wh-zones', 'M41-warehouse', 'M41-stock-location'], reports: ['Bin Utilisation Heatmap'], forms: ['Bin', 'Warehouse Zone', 'Warehouse'] }],
    /* FR-WMS-005/028: a part's home bin, velocity and pick-face minimum */
    ['2', 'Slotting', 7, { model: 'fix.wms.slot', cols: ['part_id', 'bin_id', 'velocity', 'slot_type', 'state'], screens: ['M41-slotting'], reports: ['Bin Utilisation Heatmap'], forms: ['Slot Assignment'] }],
    /* FR-WMS-008/009/011/013: dock, scan receipt with its inspection gate, directed put-away */
    ['3', 'Inbound & Put-Away', 12, { model: 'fix.wms.putaway', cols: ['name', 'part_id', 'qty', 'to_bin_id', 'state'], screens: ['M41-putaway', 'M41-docks', 'M41-receiving'], reports: ['Throughput by Shift'], forms: ['Directed Put-Away', 'Dock Appointment', 'Goods Receipt (scan receiving)'] }],
    ['4', 'Wave Planning', 9, { model: 'fix.wms.wave', cols: ['name', 'wave_date', 'strategy', 'released_at', 'state'], screens: ['M41-waves', 'M41-wave-templates'], reports: ['Wave Cycle Time'], forms: ['Pick Wave', 'Wave Template'] }],
    /* FR-WMS-023/024, BRU-WMS-05/07: a pick is a scan of bin and item; a short pick says what was found and raises the count-back */
    ['5', 'Picking', 11, { model: 'fix.wms.wave.line', cols: ['wave_id', 'part_id', 'bin_id', 'qty', 'picked_qty', 'state'], screens: ['M41-pick-lines', 'M41-picking', 'M41-tasks'], reports: ['Pick Accuracy Trend'], forms: ['Scan a Pick', 'Report a Short Pick'], create: 'M41-form-scan-pick' }],
    ['6', 'Packing & Staging', 8, { model: 'fix.wms.carton', cols: ['name', 'wave_id', 'carton_size', 'weight_kg', 'state'], screens: ['M41-packing', 'M41-staging', 'M41-packing-stations'], reports: ['Throughput by Shift'], forms: ['Carton', 'Staging Record', 'Packing Station Config'] }],
    /* FR-WMS-028/029/030: bulk -> pick-face replenishment and ad-hoc bin moves, confirmed by scan */
    ['7', 'Replenishment', 6, { model: 'fix.wms.move', cols: ['name', 'move_type', 'part_id', 'from_bin_id', 'to_bin_id', 'qty', 'state'], screens: ['M41-moves', 'M41-slotting', 'M41-spare-part', 'M41-tasks'], reports: [], forms: ['Internal Move / Replenishment', 'Confirm a Move by Scan'], create: 'M41-form-move' }],
    /* FR-WMS-036/038, T-04/T-15: claim the next task, complete it by scan, enrol the handheld */
    ['8', 'RF Execution', 8, { model: 'fix.wms.task', cols: ['name', 'task_type', 'bin_id', 'assignee_id', 'state'], screens: ['M41-rf', 'M41-tasks', 'M41-devices'], reports: ['Pick Accuracy Trend'], forms: ['Complete a Task by Scan', 'Claim a Task', 'Warehouse Task', 'RF Device'], create: 'M41-form-task-scan' }],
    /* FR-WMS-031/039/040, BRU-WMS-18: who works where with what equipment; floor counts */
    ['9', 'Labour & Analytics', 9, { model: 'fix.wms.operative', cols: ['employee_id', 'warehouse_id', 'shift', 'active'], screens: ['M41-operatives', 'M41-equipment', 'M41-counting', 'M41-tasks', 'M41-inventory-valuation-suspense'], reports: ['Labour Productivity', 'Throughput by Shift'], forms: ['Operative Profile', 'Handling Equipment', 'Floor Count'], create: 'M41-form-operative' }]
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
    cols: ['part_id', 'bin_id', 'zone_id', 'qty', 'reserved_qty', 'min_qty', 'velocity', 'slot_type', 'last_slotted_on', 'state'],
    actions: [
      { m: 'action_raise_replenishment', l: 'Raise Replenishment (pick face below minimum)' },
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
  'M41-receiving': { kind: 'model_list', model: 'fix.stock.receipt', stateField: 'state',
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
    empty: 'No pick line yet. Lines are generated from the reserved stock when a wave is released.',
    cols: ['wave_id', 'part_id', 'bin_id', 'qty', 'reserved_qty', 'picked_qty', 'lot_id', 'scanned_bin', 'scanned_item', 'state'],
    actions: [
      { m: 'action_scan_pick', l: 'Scan Pick', asks: [
        { label: 'Scan the bin', kwarg: 'bin_code' },
        { label: 'Scan the item', kwarg: 'item_code' },
        { label: 'Scan the serial (serialized parts; otherwise leave empty)', kwarg: 'serial' }
      ] },
      { m: 'action_scan_short_pick', l: 'Short Pick', asks: [
        { label: 'Scan the bin', kwarg: 'bin_code' },
        { label: 'Quantity actually in the bin', kwarg: 'found_qty', number: true },
        { label: 'Scan the item (leave empty when the bin is empty)', kwarg: 'item_code' }
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
    cols: ['name', 'task_type', 'ref', 'part_id', 'bin_id', 'qty', 'equipment_required', 'assignee_id', 'state'],
    actions: [
      { m: 'action_claim', l: 'Claim (take this task)' },
      { m: 'action_assign', l: 'Assign' },
      { m: 'action_done', l: 'Complete Task', ask: 'Scan the bin, then the item, then any serial (a move: from bin, to bin, item), e.g. A-01-01 FX-1001', kwarg: 'scan' },
      { m: 'action_cancel', l: 'Cancel Task' }
    ] },
  'M41-counting': { kind: 'model_list', model: 'fix.wms.floor.count', stateField: 'state',
    cols: ['name', 'bin_id', 'part_id', 'counted_qty', 'counted_on', 'stock_count_id', 'state'],
    actions: [{ m: 'action_post', l: 'Post Count' }] },
  'M41-wave-templates': { kind: 'model_list', model: 'fix.wms.wave.template',
    cols: ['name', 'strategy', 'zone_id', 'cutoff', 'active'] },
  'M41-packing-stations': { kind: 'model_list', model: 'fix.wms.packing.station',
    cols: ['name', 'lane', 'printer', 'active'] },
  'M41-moves': { kind: 'model_list', model: 'fix.wms.move', stateField: 'state',
    cols: ['name', 'move_type', 'part_id', 'from_bin_id', 'to_bin_id', 'qty', 'reason_code', 'assignee_id', 'done_by_id', 'state'],
    actions: [
      { m: 'action_confirm', l: 'Confirm Move', asks: [
        { label: 'Scan the bin it leaves', kwarg: 'from_code' },
        { label: 'Scan the bin it goes to', kwarg: 'to_code' },
        { label: 'Scan the item', kwarg: 'item_code' }
      ] },
      { m: 'action_cancel', l: 'Cancel Move' }
    ] },
  'M41-devices': { kind: 'model_list', model: 'fix.wms.device', stateField: 'state',
    cols: ['device_code', 'warehouse_id', 'model_name', 'operative_id', 'app_version', 'enrolled_at', 'last_seen_at', 'state'],
    actions: [
      { m: 'action_deactivate', l: 'Deactivate (lost / retired)', ask: 'Why the device is deactivated', kwarg: 'reason' },
      { m: 'action_reactivate', l: 'Reactivate (another administrator)' }
    ] },
  'M41-operatives': { kind: 'model_list', model: 'fix.wms.operative',
    cols: ['employee_id', 'warehouse_id', 'shift', 'active'] },
  'M41-equipment': { kind: 'model_list', model: 'fix.wms.equipment',
    cols: ['code', 'name', 'equipment_type', 'warehouse_id', 'capacity_kg', 'active'] },

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
          { name: 'min_qty', label: 'Replenish When Below (pick face)' },
          { name: 'max_qty', label: 'Replenish Up To' },
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
    create: false, pick: 'Pick lines are generated when a wave is released: open one from Pick Lines.',
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
          { name: 'equipment_required', label: 'Equipment Needed' },
          { name: 'assignee_id', label: 'Assignee' },
          { name: 'move_id', label: 'Internal Move', readonly: true }
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
  /* written by stock movements, reconciled only by the GL cutover: a ledger */
  'M41-inventory-valuation-suspense': { kind: 'model_list', model: 'fix.inventory.valuation.suspense', create: false,
    cols: ['name', 'company_id', 'product_id', 'operating_unit_id', 'name_bn', 'consumption_id', 'quantity'],
    empty: 'No valuation suspense entry. Entries are written by stock movements awaiting the general-ledger cutover; they cannot be typed in.' },
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
    create: false, pick: 'A suspense entry is written by a stock movement: open one from Inventory Valuation Suspense.',
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

  /* ===== capture audit 2026-11-14: the floor steps, one form each ===== */
  'M41-form-scan-pick': {
    kind: 'model_form', model: 'fix.wms.wave.line',
    title: 'Scan a Pick', newLabel: 'Scan a Pick', back: 'M41-pick-lines',
    status: { field: 'state', labels: { pending: 'Pending', picked: 'Picked', short: 'Short', cancelled: 'Cancelled' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the pick line of a released wave',
      search: 'Search pick line', choose: 'Pick this line',
      cols: ['wave_id', 'part_id', 'bin_id', 'qty', 'reserved_qty'],
      domain: [['state', '=', 'pending'], ['wave_id.state', 'in', ['released', 'picking']]],
      empty: 'No pick line waits. Lines appear when a supervisor releases a wave.'
    },
    saveAction: { method: 'action_scan_pick', label: 'Confirm Pick', done: 'Picked: the stock moved from the bin to staged', kwargs: { bin_code: 'scan_bin_entry', item_code: 'scan_item_entry', serial: 'scan_serial_entry' } },
    sections: [
      { title: 'Step 2 of 2: Scan',
        note: 'BRU-WMS-05/10: scan the bin, then the item; a serialized part also scans its serial. A pick another operative holds is his (BRU-WMS-14). A bin that empties raises a zero-crossing count.',
        fields: [
          { name: 'wave_id', label: 'Wave', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'bin_id', label: 'Pick Bin', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'scan_bin_entry', label: 'Scan the Bin', required: true, readonly: true },
          { name: 'scan_item_entry', label: 'Scan the Item', required: true, readonly: true },
          { name: 'scan_serial_entry', label: 'Scan the Serial (serialized parts)', readonly: true }
        ] }
    ]
  },
  'M41-form-short-pick': {
    kind: 'model_form', model: 'fix.wms.wave.line',
    title: 'Report a Short Pick', newLabel: 'Report a Short Pick', back: 'M41-pick-lines',
    status: { field: 'state', labels: { pending: 'Pending', picked: 'Picked', short: 'Short', cancelled: 'Cancelled' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the pick line the bin cannot fill',
      search: 'Search pick line', choose: 'Report this line short',
      cols: ['wave_id', 'part_id', 'bin_id', 'qty', 'reserved_qty'],
      domain: [['state', '=', 'pending'], ['wave_id.state', 'in', ['released', 'picking']]],
      empty: 'No pick line waits.'
    },
    saveAction: { method: 'action_scan_short_pick', label: 'Record Short Pick', done: 'Short pick recorded: what was found is picked and the bin has a count-back task', kwargs: { bin_code: 'scan_bin_entry', found_qty: 'found_qty_entry', item_code: 'scan_item_entry' } },
    sections: [
      { title: 'Step 2 of 2: What Is Really in the Bin',
        note: 'FR-WMS-024 / BRU-WMS-07: scan the bin and give what it really holds (fewer than the line asks for); scan the item if there is any. That many are picked, the line is short, and the bin is counted back at once. The stock record is corrected only by the approved count in M15.',
        fields: [
          { name: 'wave_id', label: 'Wave', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'bin_id', label: 'Pick Bin', readonly: true },
          { name: 'qty', label: 'Quantity Asked For', readonly: true },
          { name: 'scan_bin_entry', label: 'Scan the Bin', required: true, readonly: true },
          { name: 'found_qty_entry', label: 'Quantity Actually in the Bin', required: true, readonly: true },
          { name: 'scan_item_entry', label: 'Scan the Item (empty bin: leave empty)', readonly: true }
        ] }
    ]
  },
  'M41-form-move': {
    kind: 'model_form', model: 'fix.wms.move',
    title: 'Internal Move / Replenishment', newLabel: 'New Internal Move / Replenishment', back: 'M41-moves',
    status: { field: 'state', labels: { open: 'Open', done: 'Done', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Move', note: 'FR-WMS-028/029: a bin-to-bin move inside one warehouse, so the M15 total never changes. It becomes a task in the queue and is confirmed by scanning both bins and the item. Only free stock moves (not what waves hold); a blocked, quarantine or inspection bin, a non-hazardous bin for a hazardous part, a bin of another ownership class or an over-full bin is refused.',
        fields: [
          { name: 'move_type', required: true, label: 'Move Type' },
          { name: 'part_id', required: true, label: 'Spare Part', domain: [['state', '=', 'active']] },
          { name: 'from_bin_id', required: true, label: 'From Bin', domain: [['blocked', '=', false]] },
          { name: 'to_bin_id', required: true, label: 'To Bin', domain: [['zone_id.reservable', '=', true], ['blocked', '=', false]] },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'reason_code', required: true, label: 'Reason' },
          { name: 'note', label: 'Note' },
          { name: 'assignee_id', label: 'Assigned To' },
          { name: 'trigger_qty', label: 'Pick Face Held (when raised)', readonly: true },
          { name: 'task_id', label: 'Task', readonly: true },
          { name: 'done_by_id', label: 'Moved By', readonly: true },
          { name: 'done_at', label: 'Moved On', readonly: true }
        ] }
    ]
  },
  'M41-form-move-confirm': {
    kind: 'model_form', model: 'fix.wms.move',
    title: 'Confirm a Move by Scan', newLabel: 'Confirm a Move by Scan', back: 'M41-moves',
    status: { field: 'state', labels: { open: 'Open', done: 'Done', cancelled: 'Cancelled' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the open move',
      search: 'Search move', choose: 'Confirm this move',
      cols: ['name', 'move_type', 'part_id', 'from_bin_id', 'to_bin_id', 'qty'],
      domain: [['state', '=', 'open']],
      empty: 'No open move. Raise one from Slotting (pick face below minimum) or New Internal Move.'
    },
    saveAction: { method: 'action_confirm', label: 'Confirm Move', done: 'Moved: both bins updated and the task closed', kwargs: { from_code: 'scan_from_entry', to_code: 'scan_to_entry', item_code: 'scan_item_entry' } },
    sections: [
      { title: 'Step 2 of 2: Scan Both Bins and the Item',
        note: 'BRU-WMS-05: the bin it leaves, the bin it goes to, then the item.',
        fields: [
          { name: 'name', label: 'Move', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'from_bin_id', label: 'From Bin', readonly: true },
          { name: 'to_bin_id', label: 'To Bin', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'scan_from_entry', label: 'Scan the From Bin', required: true, readonly: true },
          { name: 'scan_to_entry', label: 'Scan the To Bin', required: true, readonly: true },
          { name: 'scan_item_entry', label: 'Scan the Item', required: true, readonly: true }
        ] }
    ]
  },
  'M41-form-task-scan': {
    kind: 'model_form', model: 'fix.wms.task',
    title: 'Complete a Task by Scan', newLabel: 'Complete a Task by Scan', back: 'M41-tasks',
    status: { field: 'state', labels: { open: 'Open', assigned: 'Assigned', done: 'Done', cancelled: 'Cancelled' } },
    pickRecord: {
      label: 'Step 1 of 2: choose your assigned task',
      search: 'Search task', choose: 'Do this task',
      cols: ['name', 'task_type', 'ref', 'part_id', 'bin_id', 'qty', 'assignee_id'],
      domain: [['state', '=', 'assigned']],
      empty: 'No assigned task. Claim one first (Claim a Task).'
    },
    saveAction: { method: 'action_done', label: 'Complete Task', done: 'Task complete: the movement it represents is done', kwargs: { scan: 'scan_entry' } },
    sections: [
      { title: 'Step 2 of 2: Scan',
        note: 'Only the assigned operative completes a task (BRU-WMS-14). A pick scans bin, item (and serial); a put-away scans bin and item; a move scans from bin, to bin and item; a count task completes once its floor count is submitted.',
        fields: [
          { name: 'name', label: 'Task', readonly: true },
          { name: 'task_type', label: 'Task Type', readonly: true },
          { name: 'ref', label: 'Reference', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'bin_id', label: 'Bin', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'scan_entry', label: 'Scans, separated by spaces', readonly: true }
        ] }
    ]
  },
  'M41-form-claim': {
    kind: 'model_form', model: 'fix.wms.task',
    title: 'Claim a Task', newLabel: 'Claim a Task', back: 'M41-tasks',
    status: { field: 'state', labels: { open: 'Open', assigned: 'Assigned', done: 'Done', cancelled: 'Cancelled' } },
    pickRecord: {
      label: 'Step 1 of 2: choose a free task',
      search: 'Search task', choose: 'Claim this task',
      cols: ['name', 'task_type', 'ref', 'part_id', 'bin_id', 'qty', 'equipment_required'],
      domain: [['state', '=', 'open']],
      empty: 'No open task in the queue.'
    },
    saveAction: { method: 'action_claim', label: 'Claim', done: 'Claimed: the task is yours' },
    sections: [
      { title: 'Step 2 of 2: Take It',
        note: 'T-04 / BRU-WMS-14: a task has one operative; two devices can never claim the same task. A task that needs equipment goes only to an operative whose profile holds it (BRU-WMS-18).',
        fields: [
          { name: 'name', label: 'Task', readonly: true },
          { name: 'task_type', label: 'Task Type', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'bin_id', label: 'Bin', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'equipment_required', label: 'Equipment Needed', readonly: true }
        ] }
    ]
  },
  'M41-form-device': {
    kind: 'model_form', model: 'fix.wms.device',
    title: 'RF Device', newLabel: 'Enrol an RF Device', back: 'M41-devices',
    status: { field: 'state', labels: { active: 'Active', deactivated: 'Deactivated' } },
    sections: [
      { title: 'Device', note: 'T-15: a handheld is enrolled to one warehouse by a Warehouse Supervisor or the IT administrator. A lost device is deactivated at once (Devices list); another administrator reactivates it.',
        fields: [
          { name: 'device_code', required: true, label: 'Device Code' },
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'model_name', label: 'Make / Model' },
          { name: 'operative_id', label: 'Issued To' },
          { name: 'app_version', label: 'App Version' },
          { name: 'enrolled_at', label: 'Enrolled On', readonly: true },
          { name: 'enrolled_by_id', label: 'Enrolled By', readonly: true },
          { name: 'last_seen_at', label: 'Last Seen', readonly: true },
          { name: 'deactivation_reason', label: 'Deactivation Reason', readonly: true }
        ] }
    ]
  },
  'M41-form-operative': {
    kind: 'model_form', model: 'fix.wms.operative',
    title: 'Operative Profile', newLabel: 'New Operative Profile', back: 'M41-operatives',
    sections: [
      { title: 'Operative', note: 'FR-WMS-036/039: the zones an operative works and the equipment held or certified on. A task that needs equipment is assigned only to an operative holding it (BRU-WMS-18). Set by a Warehouse Supervisor.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'shift', required: true, label: 'Shift' },
          { name: 'zone_ids', label: 'Zones Worked' },
          { name: 'equipment_ids', label: 'Equipment Held / Certified On' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M41-form-equipment': {
    kind: 'model_form', model: 'fix.wms.equipment',
    title: 'Handling Equipment', newLabel: 'Register Handling Equipment', back: 'M41-equipment',
    sections: [
      { title: 'Equipment', note: 'FR-WMS-039: trolleys, ladders, pallet trucks and keys, by warehouse. Registered by a Warehouse Supervisor.',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'code', required: true, label: 'Equipment Code' },
          { name: 'name', required: true, label: 'Description' },
          { name: 'equipment_type', required: true, label: 'Type' },
          { name: 'capacity_kg', label: 'Safe Working Load (kg)' },
          { name: 'active', label: 'Active' }
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
  'M41:Packing Station Config': 'fix.wms.packing.station',
  'M41:Internal Move / Replenishment': 'fix.wms.move',
  'M41:RF Device': 'fix.wms.device',
  'M41:Operative Profile': 'fix.wms.operative',
  'M41:Handling Equipment': 'fix.wms.equipment'
};

export const FORM_CHIPS = {
  'M41:Bin': 'M41-form-bin',
  'M41:Wave Template': 'M41-form-template',
  'M41:Dock Appointment': 'M41-form-dock',
  'M41:Packing Station Config': 'M41-form-station',
  'M41:Warehouse': 'M41-form-warehouse',
  'M41:Warehouse Zone': 'M41-form-zone',
  'M41:Slot Assignment': 'M41-form-slot',
  'M41:Directed Put-Away': 'M41-form-putaway',
  /* the receipt (with its inspection gate) is M15's form: one form, two pages */
  'M41:Goods Receipt (scan receiving)': 'M15-form-receipt',
  'M41:Pick Wave': 'M41-form-wave',
  'M41:Scan a Pick': 'M41-form-scan-pick',
  'M41:Report a Short Pick': 'M41-form-short-pick',
  'M41:Carton': 'M41-form-carton',
  'M41:Staging Record': 'M41-form-stage',
  'M41:Internal Move / Replenishment': 'M41-form-move',
  'M41:Confirm a Move by Scan': 'M41-form-move-confirm',
  'M41:Complete a Task by Scan': 'M41-form-task-scan',
  'M41:Claim a Task': 'M41-form-claim',
  'M41:Warehouse Task': 'M41-form-task',
  'M41:RF Device': 'M41-form-device',
  'M41:Operative Profile': 'M41-form-operative',
  'M41:Handling Equipment': 'M41-form-equipment',
  'M41:Floor Count': 'M41-form-floor-count',
  'M41:__by_model__': {
    'fix.stock.location': 'M41-form-stock-location',
    'fix.inventory.valuation.suspense': 'M41-form-inventory-valuation-suspense',
    /* Real-inventory upgrade 2026-11-07: the spare-part master now opens the
     * 7-tab M15 form (single surface owner per model) instead of the 6-field
     * stub below, which stays only as the fallback screen definition. */
    'fix.spare.part': 'M15-form-part',
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
    'fix.wms.packing.station': 'M41-form-station',
    'fix.wms.move': 'M41-form-move',
    'fix.wms.device': 'M41-form-device',
    'fix.wms.operative': 'M41-form-operative',
    'fix.wms.equipment': 'M41-form-equipment'
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
    'M41-counting': 'M41-form-floor-count',
    'M41-wave-templates': 'M41-form-template',
    'M41-packing-stations': 'M41-form-station',
    'M41-moves': 'M41-form-move',
    'M41-devices': 'M41-form-device',
    'M41-operatives': 'M41-form-operative',
    'M41-equipment': 'M41-form-equipment'
  }
};

export const CREATE = {
  M41: { screen: 'M41-form-dock', model: 'fix.wms.dock', label: 'Dock Appointment' }
};
