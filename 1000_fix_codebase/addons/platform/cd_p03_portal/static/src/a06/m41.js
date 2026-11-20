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
 * and handling equipment (FR-WMS-039, BRU-WMS-18).
 *
 * Capture pass 2 2026-11-19: the buttons existed but the forms could not hold
 * the spec's records. Added: warehouse enablement, cut-offs and shift pattern
 * (FR-WMS-003), zone types/class/walk order and bin coordinates, pick face,
 * weight and volume (FR-WMS-001/002, T-09), the bin block history (FR-WMS-034),
 * the directed put-away with strategy, rejected bins, override and approval
 * (FR-WMS-013/014, BRU-WMS-06), put-away exceptions (FR-WMS-015), dock doors
 * and the unload clock (FR-WMS-008), handling units (FR-WMS-010, T-11),
 * cross-dock (FR-WMS-016), return receiving (FR-WMS-017), the outbound demand
 * queue and building a wave from it (FR-WMS-018/020), template purpose and
 * release rule (FR-WMS-019), cluster / pick-and-pass (FR-WMS-021), the pick
 * walk order (FR-WMS-022), short-pick re-sourcing (FR-WMS-024), count plans by
 * zone, bin or ABC class (FR-WMS-031), time standards and productivity runs
 * (FR-WMS-040, AUT-WMS-15).
 *
 * Part 2 (2026-11-20, owner's choice): the demand feed from M15 transfers, van
 * replenishment and RTVs with the wave shipment dispatching them, auto-release
 * at the cut-off (FR-WMS-018/027, AUT-WMS-07), the scan log and Attempted
 * Violations report (§10.1, §14), substitute pick (FR-WMS-023), slotting
 * proposals (FR-WMS-006/030) and the RF journal behind /api/v1/wh (T-06/07). */

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
      { id: 'M41-spare-part', en: "Spare Part", bn: "Spare Part", t: 'g' },
      { id: 'M41-warehouse', en: "Warehouse", bn: "Warehouse", t: 'g' }
    ]},
    { en: 'Structure', screens: [
      { id: 'M41-wh-zones', en: 'Warehouse Zones', bn: 'ওয়্যারহাউস জোন', t: 'g' },
      { id: 'M41-zones', en: 'Zones, Aisles & Bins', bn: 'জোন ও বিন', t: 'g' },
      { id: 'M41-slotting', en: 'Slotting & Re-Slotting', bn: 'স্লটিং', t: 'g' },
      { id: 'M41-block-log', en: 'Bin Block History', bn: 'বিন ব্লক ইতিহাস', t: 'g' },
      { id: 'M41-proposals', en: 'Slotting Proposals', bn: 'স্লটিং প্রস্তাব', t: 'g' },
      { id: 'M41-slot-loads', en: 'Opening Slot Loads', bn: 'প্রারম্ভিক স্লট', t: 'g' }
    ]},
    { en: 'Inbound', screens: [
      { id: 'M41-docks', en: 'Dock Appointments', bn: 'ডক অ্যাপয়েন্টমেন্ট', t: 'g' },
      { id: 'M41-receiving', en: 'Scan Receiving', bn: 'স্ক্যান রিসিভিং', t: 'g' },
      { id: 'M41-inspection', en: 'Inspection Outcomes', bn: 'পরিদর্শন ফলাফল', t: 'g' },
      { id: 'M41-putaway', en: 'Directed Put-Away', bn: 'ডিরেক্টেড পুট-অ্যাওয়ে', t: 'g' },
      { id: 'M41-putaway-exceptions', en: 'Put-Away Exceptions', bn: 'পুট-অ্যাওয়ে ব্যতিক্রম', t: 'g' },
      { id: 'M41-dock-doors', en: 'Dock Doors', bn: 'ডক দরজা', t: 'g' },
      { id: 'M41-handling-units', en: 'Handling Units', bn: 'হ্যান্ডলিং ইউনিট', t: 'g' },
      { id: 'M41-crossdocks', en: 'Cross-Dock', bn: 'ক্রস-ডক', t: 'g' },
      { id: 'M41-returns', en: 'Return Receiving', bn: 'রিটার্ন গ্রহণ', t: 'g' }
    ]},
    { en: 'Outbound', screens: [
      { id: 'M41-demand', en: 'Outbound Demand Queue', bn: 'আউটবাউন্ড চাহিদা', t: 'g' },
      { id: 'M41-waves', en: 'Wave Planning', bn: 'ওয়েভ প্ল্যানিং', t: 'g' },
      { id: 'M41-pick-lines', en: 'Pick Lines', bn: 'পিক লাইন', t: 'g' },
      { id: 'M41-substitutions', en: 'Substitutions', bn: 'বিকল্প যন্ত্রাংশ', t: 'g' },
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
      { id: 'M41-scan-log', en: 'Scan Log', bn: 'স্ক্যান লগ', t: 'g' },
      { id: 'M41-rf-journal', en: 'RF Confirmations', bn: 'আরএফ নিশ্চিতকরণ', t: 'g' },
      { id: 'M41-operatives', en: 'Operative Profiles', bn: 'অপারেটিভ প্রোফাইল', t: 'g' },
      { id: 'M41-equipment', en: 'Handling Equipment', bn: 'হ্যান্ডলিং সরঞ্জাম', t: 'g' },
      { id: 'M41-count-plans', en: 'Count Plans', bn: 'গণনা পরিকল্পনা', t: 'g' },
      { id: 'M41-time-standards', en: 'Time Standards', bn: 'সময় মান', t: 'g' },
      { id: 'M41-productivity-runs', en: 'Productivity Runs', bn: 'উৎপাদনশীলতা পরিমাপ', t: 'g' },
      { id: 'M41-productivity', en: 'Labour Productivity', bn: 'শ্রম উৎপাদনশীলতা', t: 'g' }
    ]}
  ],
  reports: ['Throughput by Shift', 'Pick Accuracy Trend', 'Wave Cycle Time', 'Labour Productivity', 'Bin Utilisation Heatmap', 'Attempted Violations',
    'Daily Override Report', 'Short-Pick Rate', 'Cycle Times', 'Put-Away Compliance', 'Cross-Dock Utilisation', 'Device Health', 'Slot vs Ledger Reconciliation'],
  forms: ['Bin', 'Wave Template', 'Dock Appointment', 'Packing Station Config',
    'Warehouse', 'Warehouse Zone', 'Slot Assignment', 'Directed Put-Away', 'Goods Receipt (scan receiving)',
    'Pick Wave', 'Scan a Pick', 'Report a Short Pick', 'Carton', 'Staging Record',
    'Internal Move / Replenishment', 'Confirm a Move by Scan',
    'Complete a Task by Scan', 'Claim a Task', 'Warehouse Task', 'RF Device',
    'Operative Profile', 'Handling Equipment', 'Floor Count',
    'Report a Put-Away Exception', 'Dock Door', 'Handling Unit', 'Cross-Dock', 'Return Receiving',
    'Inspection Outcome (M16)', 'Outbound Demand', 'Count Plan', 'Time Standard', 'Labour Productivity Run',
    'Request a Substitute Part', 'Opening Slot Load'],
  cross: ['M15 stock ledger', 'M16 goods receipt', 'M03 outbound staging', 'M44 import receiving'],
  freg: { src: 78, sub: [
    /* FR-WMS-001..004: warehouse -> zones -> bins */
    ['1', 'Physical Structure', 8, { model: 'fix.warehouse.bin', cols: ['name', 'zone_id', 'barcode', 'capacity_qty'], screens: ['M41-zones', 'M41-wh-zones', 'M41-warehouse', 'M41-block-log', 'M41-stock-location'], reports: ['Bin Utilisation Heatmap'], forms: ['Bin', 'Warehouse Zone', 'Warehouse'] }],
    /* FR-WMS-005/028: a part's home bin, velocity and pick-face minimum */
    ['2', 'Slotting', 7, { model: 'fix.wms.slot', cols: ['part_id', 'bin_id', 'velocity', 'slot_type', 'state'], screens: ['M41-slotting', 'M41-proposals', 'M41-slot-loads'], reports: ['Bin Utilisation Heatmap', 'Slot vs Ledger Reconciliation'], forms: ['Slot Assignment', 'Opening Slot Load'] }],
    /* FR-WMS-008/009/011/013: dock, scan receipt with its inspection gate, directed put-away */
    ['3', 'Inbound & Put-Away', 12, { model: 'fix.wms.putaway', cols: ['name', 'part_id', 'qty', 'to_bin_id', 'state'], screens: ['M41-putaway', 'M41-putaway-exceptions', 'M41-docks', 'M41-dock-doors', 'M41-receiving', 'M41-inspection', 'M41-handling-units', 'M41-crossdocks', 'M41-returns'], reports: ['Throughput by Shift', 'Daily Override Report', 'Put-Away Compliance', 'Cross-Dock Utilisation'], forms: ['Directed Put-Away', 'Report a Put-Away Exception', 'Dock Appointment', 'Dock Door', 'Goods Receipt (scan receiving)', 'Inspection Outcome (M16)', 'Handling Unit', 'Cross-Dock', 'Return Receiving'] }],
    ['4', 'Wave Planning', 9, { model: 'fix.wms.wave', cols: ['name', 'wave_date', 'strategy', 'released_at', 'state'], screens: ['M41-waves', 'M41-demand', 'M41-wave-templates'], reports: ['Wave Cycle Time'], forms: ['Pick Wave', 'Outbound Demand', 'Wave Template'] }],
    /* FR-WMS-023/024, BRU-WMS-05/07: a pick is a scan of bin and item; a short pick says what was found and raises the count-back */
    ['5', 'Picking', 11, { model: 'fix.wms.wave.line', cols: ['wave_id', 'part_id', 'bin_id', 'qty', 'picked_qty', 'state'], screens: ['M41-pick-lines', 'M41-substitutions', 'M41-picking', 'M41-tasks'], reports: ['Pick Accuracy Trend', 'Short-Pick Rate'], forms: ['Scan a Pick', 'Report a Short Pick', 'Request a Substitute Part'], create: 'M41-form-scan-pick' }],
    ['6', 'Packing & Staging', 8, { model: 'fix.wms.carton', cols: ['name', 'wave_id', 'carton_size', 'weight_kg', 'state'], screens: ['M41-packing', 'M41-staging', 'M41-handling-units', 'M41-packing-stations'], reports: ['Throughput by Shift'], forms: ['Carton', 'Staging Record', 'Handling Unit', 'Packing Station Config'] }],
    /* FR-WMS-028/029/030: bulk -> pick-face replenishment and ad-hoc bin moves, confirmed by scan */
    ['7', 'Replenishment', 6, { model: 'fix.wms.move', cols: ['name', 'move_type', 'part_id', 'from_bin_id', 'to_bin_id', 'qty', 'state'], screens: ['M41-moves', 'M41-slotting', 'M41-spare-part', 'M41-tasks'], reports: [], forms: ['Internal Move / Replenishment', 'Confirm a Move by Scan'], create: 'M41-form-move' }],
    /* FR-WMS-036/038, T-04/T-15: claim the next task, complete it by scan, enrol the handheld */
    ['8', 'RF Execution', 8, { model: 'fix.wms.task', cols: ['name', 'task_type', 'bin_id', 'assignee_id', 'state'], screens: ['M41-rf', 'M41-tasks', 'M41-devices', 'M41-scan-log', 'M41-rf-journal'], reports: ['Pick Accuracy Trend', 'Attempted Violations', 'Device Health'], forms: ['Complete a Task by Scan', 'Claim a Task', 'Warehouse Task', 'RF Device'], create: 'M41-form-task-scan' }],
    /* FR-WMS-031/039/040, BRU-WMS-18: who works where with what equipment; floor counts */
    ['9', 'Labour & Analytics', 9, { model: 'fix.wms.operative', cols: ['employee_id', 'warehouse_id', 'shift', 'active'], screens: ['M41-operatives', 'M41-equipment', 'M41-count-plans', 'M41-counting', 'M41-time-standards', 'M41-productivity-runs', 'M41-productivity', 'M41-tasks'], reports: ['Labour Productivity', 'Throughput by Shift', 'Cycle Times'], forms: ['Operative Profile', 'Handling Equipment', 'Count Plan', 'Floor Count', 'Time Standard', 'Labour Productivity Run'], create: 'M41-form-operative' }]
  ] }
};

export const SCREENS = {
  'M41-wh-zones': { kind: 'model_list', model: 'fix.warehouse.zone',
    cols: ['name', 'code', 'warehouse_id', 'zone_type', 'ownership_class', 'sequence', 'reservable'] },
  'M41-zones': { kind: 'model_list', model: 'fix.warehouse.bin',
    cols: ['name', 'zone_id', 'aisle', 'bay', 'level', 'position', 'is_pick_face', 'capacity_qty', 'max_weight_kg', 'ownership_class', 'blocked', 'block_reason', 'block_report_reason'],
    actions: [
      { m: 'action_report_block', l: 'Report a Bin Problem', ask: 'What is wrong with the bin', kwarg: 'reason' },
      { m: 'action_block', l: 'Block Bin (supervisor / QM)', ask: 'Reason the bin is blocked', kwarg: 'reason' },
      { m: 'action_unblock', l: 'Unblock Bin (controller)', ask: 'Why the block is lifted', kwarg: 'note' }
    ] },
  'M41-slotting': { kind: 'model_list', model: 'fix.wms.slot', stateField: 'state',
    cols: ['part_id', 'bin_id', 'zone_id', 'ownership_class', 'min_qty', 'velocity', 'slot_type', 'last_slotted_on', 'state'],
    actions: [
      { m: 'action_raise_replenishment', l: 'Raise Replenishment (pick face below minimum)' },
      { m: 'action_report_block', l: 'Report a Bin Problem', ask: 'What is wrong with the bin', kwarg: 'reason' },
      { m: 'action_block', l: 'Block Whole Bin (supervisor / QM)', ask: 'Reason the bin is blocked', kwarg: 'reason' },
      { m: 'action_unblock', l: 'Unblock Bin (controller)', ask: 'Why the block is lifted', kwarg: 'note' }
    ] },
  'M41-docks': { kind: 'model_list', model: 'fix.wms.dock', stateField: 'state',
    cols: ['name', 'door_id', 'dock_no', 'partner_id', 'dock_type', 'slot_start', 'slot_end', 'arrived_at', 'unload_started_at', 'completed_at', 'state'],
    actions: [
      { m: 'action_check_in', l: 'Check In (arrived)' },
      { m: 'action_start_unload', l: 'Start Unloading' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M41-receiving': { kind: 'model_list', model: 'fix.stock.receipt', stateField: 'state',
    cols: ['name', 'partner_id', 'location_id', 'received_on', 'state'] },
  'M41-putaway': { kind: 'model_list', model: 'fix.wms.putaway', stateField: 'state',
    cols: ['name', 'part_id', 'qty', 'directed_bin_id', 'strategy_used', 'to_bin_id', 'override_state', 'receipt_line_id', 'transfer_line_id', 'assignee_id', 'state'],
    actions: [
      { m: 'action_complete', l: 'Complete Put-Away', asks: [
        { label: 'Scan the target bin', kwarg: 'bin_code' },
        { label: 'Scan the item', kwarg: 'item_code' }
      ] },
      { m: 'action_direct', l: 'Direct Again (run the strategy)' },
      { m: 'action_approve_override', l: 'Approve Override (another supervisor)' },
      { m: 'action_reject_override', l: 'Reject Override (back to the directed bin)' },
      { m: 'action_cancel', l: 'Cancel Put-Away (supervisor)', ask: 'Why the put-away is cancelled', kwarg: 'reason' }
    ] },
  'M41-waves': { kind: 'model_list', model: 'fix.wms.wave', stateField: 'state',
    cols: ['name', 'wave_date', 'template_id', 'strategy', 'priority', 'cutoff_at', 'released_at', 'shipped_at', 'pick_all_reason', 'cancel_reason', 'state'],
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
    cols: ['wave_id', 'pick_sequence', 'part_id', 'bin_id', 'qty', 'reserved_qty', 'picked_qty', 'dest_location_id', 'priority', 'resourced_from_id', 'substitute_of_id', 'scanned_bin', 'state'],
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
    cols: ['name', 'task_type', 'pick_sequence', 'ref', 'part_id', 'bin_id', 'qty', 'equipment_required', 'time_standard_sec', 'assignee_id', 'claimed_at', 'state'],
    actions: [
      { m: 'action_claim', l: 'Claim (take this task)' },
      { m: 'action_assign', l: 'Assign' },
      { m: 'action_done', l: 'Complete Task', ask: 'Scan the bin, then the item, then any serial (a move: from bin, to bin, item), e.g. A-01-01 FX-1001', kwarg: 'scan' },
      { m: 'action_cancel', l: 'Cancel Task' }
    ] },
  'M41-counting': { kind: 'model_list', model: 'fix.wms.floor.count', stateField: 'state',
    cols: ['name', 'plan_id', 'count_type', 'bin_id', 'part_id', 'counted_qty', 'counted_on', 'stock_count_id', 'state'],
    actions: [{ m: 'action_post', l: 'Post Count' }] },
  'M41-wave-templates': { kind: 'model_list', model: 'fix.wms.wave.template',
    cols: ['name', 'purpose', 'warehouse_id', 'strategy', 'release_rule', 'priority', 'cutoff', 'armed_by_id', 'last_released_at', 'last_release_error', 'active'] },
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

  /* ===== capture pass 2 (2026-11-19) lists ===== */
  'M41-block-log': { kind: 'model_list', model: 'fix.wms.bin.block.log', create: false,
    cols: ['bin_id', 'event', 'reason', 'user_id', 'at', 'blocked_hours'],
    empty: 'No bin was blocked yet. Block / Unblock on the bin list write this history.' },
  'M41-putaway-exceptions': { kind: 'model_list', model: 'fix.wms.putaway.exception', create: false,
    cols: ['putaway_id', 'part_id', 'cause', 'bin_id', 'redirected_bin_id', 'note', 'reported_by_id', 'reported_at'],
    empty: 'No put-away exception. Report one with "Report a Put-Away Exception".' },
  /* FR-WMS-011: the inspection is executed on M16's record (BRU-WMS-04 holds the stock until it is confirmed there) */
  'M41-inspection': { kind: 'model_list', model: 'fix.procurement.inspection', stateField: 'state',
    cols: ['name', 'receipt_ref', 'purchase_order_id', 'product_id', 'qty_received', 'qty_accepted', 'outcome', 'state'],
    empty: 'No inspection yet. A purchase-order receipt raises one; record the sample, checks and outcome with "Inspection Outcome (M16)".' },
  'M41-dock-doors': { kind: 'model_list', model: 'fix.wms.dock.door',
    cols: ['warehouse_id', 'code', 'name', 'direction', 'max_vehicle', 'active'] },
  'M41-handling-units': { kind: 'model_list', model: 'fix.wms.handling.unit', stateField: 'state',
    cols: ['name', 'warehouse_id', 'hu_type', 'parent_id', 'receipt_id', 'wave_id', 'current_bin_id', 'contents_qty', 'state'],
    actions: [
      { m: 'action_close', l: 'Close & Label' },
      { m: 'action_store', l: 'Store (scan the bin)', ask: 'Scan the bin', kwarg: 'bin_code' },
      { m: 'action_dissolve', l: 'Dissolve' }
    ] },
  'M41-crossdocks': { kind: 'model_list', model: 'fix.wms.crossdock', stateField: 'state',
    cols: ['name', 'receipt_line_id', 'demand_id', 'wave_id', 'part_id', 'qty', 'stage_lane', 'load_ref', 'state'],
    actions: [
      { m: 'action_confirm', l: 'Confirm (scan the item)', ask: 'Scan the item', kwarg: 'item_code' },
      { m: 'action_dispatch', l: 'Dispatch', ask: 'Load / vehicle reference', kwarg: 'load_ref' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M41-returns': { kind: 'model_list', model: 'fix.wms.return.receipt', stateField: 'state',
    cols: ['name', 'warehouse_id', 'source_type', 'source_ref', 'part_id', 'qty', 'condition', 'returns_bin_id', 'disposition', 'state'],
    actions: [{ m: 'action_dispose', l: 'Decide Disposition (supervisor / controller)' }] },
  'M41-demand': { kind: 'model_list', model: 'fix.wms.outbound.demand', stateField: 'state',
    cols: ['name', 'warehouse_id', 'source_type', 'source_ref', 'part_id', 'qty', 'dest_location_id', 'priority', 'cutoff_at', 'template_id', 'wave_id', 'short_note', 'state'],
    actions: [
      { m: 'action_build_wave', l: 'Build Wave from Selected Demand' },
      { m: 'action_cancel', l: 'Cancel Demand' }
    ] },
  'M41-count-plans': { kind: 'model_list', model: 'fix.wms.count.plan', stateField: 'state',
    cols: ['name', 'warehouse_id', 'scope', 'zone_id', 'velocity', 'count_type', 'planned_on', 'assignee_id', 'counts_total', 'counts_open', 'state'],
    actions: [
      { m: 'action_generate', l: 'Generate Counts' },
      { m: 'action_close', l: 'Close Plan' },
      { m: 'action_cancel', l: 'Cancel Plan' }
    ] },
  'M41-time-standards': { kind: 'model_list', model: 'fix.wms.time.standard',
    cols: ['warehouse_id', 'task_type', 'zone_id', 'seconds_per_task', 'seconds_per_unit', 'active'] },
  'M41-productivity-runs': { kind: 'model_list', model: 'fix.wms.productivity.run', stateField: 'state',
    cols: ['name', 'warehouse_id', 'date_from', 'date_to', 'computed_by_id', 'computed_at', 'state'],
    actions: [{ m: 'action_compute', l: 'Measure (supervisor)' }] },
  'M41-productivity': { kind: 'model_list', model: 'fix.wms.productivity', create: false,
    cols: ['date', 'operative_id', 'warehouse_id', 'task_type', 'tasks_completed', 'units', 'actual_seconds', 'standard_seconds', 'efficiency_pct', 'accuracy_pct'],
    empty: 'Nothing measured yet. A productivity run (nightly, or Measure) writes these rows.' },

  /* ===== part 2 (2026-11-20) ===== */
  'M41-substitutions': { kind: 'model_list', model: 'fix.wms.substitution', stateField: 'state',
    cols: ['name', 'wave_id', 'part_id', 'substitute_part_id', 'bin_id', 'qty', 'crossref_id', 'requested_by_id', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (another supervisor)' },
      { m: 'action_reject', l: 'Reject (supervisor)' }
    ] },
  'M41-slot-loads': { kind: 'model_list', model: 'fix.wms.slot.load', stateField: 'state',
    cols: ['name', 'warehouse_id', 'bin_id', 'part_id', 'qty', 'reason', 'loaded_by_id', 'loaded_at', 'state'],
    empty: 'No opening slot load. A supervisor slots stock M15 already holds (the take-on) into the bins here, with no ledger effect.',
    actions: [
      { m: 'action_load', l: 'Slot Into the Bin (supervisor)' },
      { m: 'action_cancel', l: 'Cancel (supervisor)' }
    ] },
  'M41-form-slot-load': {
    kind: 'model_form', model: 'fix.wms.slot.load',
    title: 'Opening Slot Load', newLabel: 'New Opening Slot Load', back: 'M41-slot-loads',
    status: { field: 'state', labels: { draft: 'Draft', loaded: 'Slotted', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Opening Position', note: 'O2 / spec 16.4: a Warehouse Supervisor slots stock that M15 already holds at this warehouse (counted in the bin) with the reason or count reference. Nothing moves in the M15 ledger; the quantity is capped at what M15 holds of the bin class outside every bin (BRU-WMS-01).',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse', domain: [['wms_enabled', '=', true]] },
          { name: 'bin_id', required: true, label: 'Bin' },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'qty', required: true, label: 'Quantity Found in the Bin' },
          { name: 'reason', required: true, label: 'Reason / Count Reference' },
          { name: 'loaded_by_id', label: 'Slotted By', readonly: true },
          { name: 'loaded_at', label: 'Slotted On', readonly: true }
        ] }
    ]
  },
  'M41-proposals': { kind: 'model_list', model: 'fix.wms.slot.proposal', stateField: 'state', create: false,
    cols: ['name', 'warehouse_id', 'kind', 'part_id', 'from_bin_id', 'to_bin_id', 'qty', 'picks_90d', 'reason', 'decided_by_id', 'move_id', 'state'],
    empty: 'No proposal. The nightly slotting run (or Propose Re-slotting Now on the warehouse) proposes moves here.',
    actions: [
      { m: 'action_accept', l: 'Accept (raises the move)' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M41-scan-log': { kind: 'model_list', model: 'fix.wms.scan.event', create: false,
    cols: ['occurred_at', 'user_name', 'device_code', 'action', 'record_name', 'scans', 'accepted', 'rule', 'message', 'offline'],
    empty: 'No scan yet. Every put-away, pick, move, cross-dock and task scan is logged here, refused ones included.' },
  'M41-rf-journal': { kind: 'model_list', model: 'fix.wms.rf.journal', create: false,
    cols: ['processed_at', 'device_id', 'user_id', 'op', 'task_id', 'key', 'ok', 'offline', 'result'],
    empty: 'No RF confirmation yet. The handheld API (/api/v1/wh) records each one once per idempotency key.' },
  'M41-rpt-violations': { kind: 'table_report', module: 'M41', report: 'scan_violations', title: 'Attempted Violations', period: true },

  'M41-form-substitution': {
    kind: 'model_form', model: 'fix.wms.substitution',
    title: 'Request a Substitute Part', newLabel: 'Request a Substitute Part', back: 'M41-substitutions',
    status: { field: 'state', labels: { requested: 'Requested', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Substitute', note: 'FR-WMS-023: a short line may be filled with a part M37 lists as an approved alternate (one way from the asked part, or two way), from a bin of this warehouse that holds it free. A supervisor other than you approves it; it then becomes a new pick line with its task. A transfer or return to vendor moves one named part and is never substituted.',
        fields: [
          { name: 'wave_line_id', required: true, label: 'Short Pick Line', domain: [['state', '=', 'short'], ['wave_id.state', '=', 'picking']] },
          { name: 'substitute_part_id', required: true, label: 'Substitute Part' },
          { name: 'bin_id', required: true, label: 'Pick the Substitute From', domain: [['blocked', '=', false]] },
          { name: 'reason', label: 'Why' },
          { name: 'qty', label: 'Quantity (the shortfall)', readonly: true },
          { name: 'crossref_id', label: 'M37 Approval', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'new_line_id', label: 'Substitute Pick Line', readonly: true }
        ] }
    ]
  },

  /* Report chips -> their own computed pack */
  'M41-rpt-throughput': { kind: 'table_report', module: 'M41', report: 'throughput_by_shift', title: 'Throughput by Shift', period: true },
  'M41-rpt-accuracy': { kind: 'table_report', module: 'M41', report: 'pick_accuracy', title: 'Pick Accuracy Trend', period: true },
  'M41-rpt-cycle': { kind: 'table_report', module: 'M41', report: 'wave_cycle_time', title: 'Wave Cycle Time', period: true },
  'M41-rpt-labour': { kind: 'table_report', module: 'M41', report: 'labour_productivity', title: 'Labour Productivity', period: true },
  'M41-rpt-bins': { kind: 'table_report', module: 'M41', report: 'bin_utilisation', title: 'Bin Utilisation Heatmap', period: false },
  /* A06 ERP audit F15: the spec section 14 reports the data already supports */
  'M41-rpt-overrides': { kind: 'table_report', module: 'M41', report: 'override_report', title: 'Daily Override Report', period: true },
  'M41-rpt-short': { kind: 'table_report', module: 'M41', report: 'short_pick_rate', title: 'Short-Pick Rate', period: true },
  'M41-rpt-cycletimes': { kind: 'table_report', module: 'M41', report: 'cycle_times', title: 'Cycle Times', period: true },
  'M41-rpt-compliance': { kind: 'table_report', module: 'M41', report: 'putaway_compliance', title: 'Put-Away Compliance', period: true },
  'M41-rpt-crossdock': { kind: 'table_report', module: 'M41', report: 'crossdock_utilisation', title: 'Cross-Dock Utilisation', period: true },
  'M41-rpt-devices': { kind: 'table_report', module: 'M41', report: 'device_health', title: 'Device Health', period: true },
  'M41-rpt-recon': { kind: 'table_report', module: 'M41', report: 'slot_ledger_recon', title: 'Slot vs Ledger Reconciliation', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M41-form-bin': {
    kind: 'model_form',
    model: 'fix.warehouse.bin',
    title: 'Bin',
    back: 'M41-zones',
    tabs: [
      { id: 'bin', label: '1. Bin & Rules', bn: '১. বিন ও নিয়ম', icon: '📦', badge: '6' },
      { id: 'place', label: '2. Location (T-09)', bn: '২. অবস্থান', icon: '📍', badge: '6' },
      { id: 'size', label: '3. Size & Limits', bn: '৩. আকার ও সীমা', icon: '📐', badge: '6' },
      { id: 'block', label: '4. Block', bn: '৪. ব্লক', icon: '⛔' }
    ],
    sections: [
      { tab: 'bin', title: 'Bin', note: 'FR-WMS-002: hazardous parts go only into hazardous-class bins (BRU-WMS-11); a bin of one ownership class takes no other class (BRU-WMS-03), and in a zone reserved for a class every bin is of that class (T-02).',
        fields: [
          { name: 'name', required: true, label: 'Bin' },
          { name: 'zone_id', required: true, label: 'Zone' },
          { name: 'barcode', label: 'Barcode (Code-128 / QR)' },
          { name: 'storage_class', required: true, label: 'Storage Class' },
          { name: 'ownership_class', required: true, label: 'Ownership Class' },
          { name: 'is_pick_face', label: 'Pick Face' }
        ] },
      { tab: 'place', title: 'Coordinate', note: 'T-09 / FR-WMS-022: aisle, bay, level and position give the walk order: zones in their walk sequence, odd aisles walked up and even aisles back down.',
        fields: [
          { name: 'aisle', label: 'Aisle' },
          { name: 'bay', label: 'Bay / Rack' },
          { name: 'level', label: 'Level' },
          { name: 'position', label: 'Position' },
          { name: 'pick_sequence', label: 'Pick Sequence', readonly: true }
        ] },
      { tab: 'size', title: 'Size & Capacity', note: 'BRU-WMS-09: a put-away or move that would exceed the count, the weight or the volume limit is refused and re-directed; 0 means no limit. With no volume limit the inner dimensions give it. Part weight and volume come from the product (M37).',
        fields: [
          { name: 'capacity_qty', label: 'Capacity (units)' },
          { name: 'max_weight_kg', label: 'Weight Limit (kg)' },
          { name: 'max_volume_m3', label: 'Volume Limit (m³)' },
          { name: 'length_cm', label: 'Length (cm)' },
          { name: 'width_cm', label: 'Width (cm)' },
          { name: 'height_cm', label: 'Height (cm)' }
        ] },
      { tab: 'block', title: 'Block', note: 'FR-WMS-034: Block / Unblock on the bin list; every block and unblock is kept in the Bin Block History.',
        fields: [
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
          { name: 'ownership_class', required: true, label: 'Reserved for Ownership Class' },
          { name: 'sequence', label: 'Walk Sequence' },
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
          { name: 'ownership_class', label: 'Ownership Class (from the bin)', readonly: true },
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
          { name: 'door_id', label: 'Dock Door' },
          { name: 'dock_no', label: 'Dock (filled from the door)' },
          { name: 'partner_id', label: 'Partner / Carrier' },
          { name: 'carrier', label: 'Carrier Name' },
          { name: 'dock_type', required: true, label: 'Type' },
          { name: 'slot_start', required: true, label: 'Window Start' },
          { name: 'slot_end', required: true, label: 'Window End' },
          { name: 'receipt_id', label: 'Goods Receipt' },
          { name: 'wave_id', label: 'Outbound Wave' },
          { name: 'notes', label: 'Notes' },
          { name: 'arrived_at', label: 'Arrived', readonly: true },
          { name: 'unload_started_at', label: 'Unloading Started', readonly: true },
          { name: 'completed_at', label: 'Completed', readonly: true }
        ] }
    ]
  },

  'M41-form-putaway': {
    kind: 'model_form',
    model: 'fix.wms.putaway',
    title: 'Directed Put-Away',
    back: 'M41-putaway',
    status: { field: 'state', labels: { pending: 'Pending', done: 'Done', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'what', label: '1. What Is Put Away', bn: '১. কী রাখা হবে', icon: '📥', badge: '6' },
      { id: 'directive', label: '2. Directive (T-01)', bn: '২. নির্দেশনা', icon: '🧭', badge: '5' },
      { id: 'override', label: '3. Override', bn: '৩. ওভাররাইড', icon: '✋', badge: '5' }
    ],
    sections: [
      { tab: 'what', title: 'Put-Away', note: 'Stock a POSTED goods-receipt line accepted (out of inspection), or a received M15 transfer line brought, up to what is not yet put away or cross-docked, and never more than M15 holds outside the bins. Leave the bin empty: saving runs the directive and fills it. Stock already on hand is slotted by an Opening Slot Load.',
        fields: [
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'receipt_line_id', label: 'Received Line (goods receipt)', domain: [['is_posted', '=', true]] },
          { name: 'transfer_line_id', label: 'Received Line (M15 transfer)', domain: [['transfer_id.state', 'in', ['received', 'discrepancy']]] },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'lot_id', label: 'Serial / Lot', domain: [['status', '=', 'in_stock']] },
          { name: 'from_ref', label: 'Source Reference' },
          { name: 'assignee_id', label: 'Assigned To' }
        ] },
      { tab: 'directive', title: 'Where the System Directs It', note: 'FR-WMS-013: fixed bin, then addition to existing stock, near the pick face, nearest empty bin, bulk; under capacity, weight, volume, storage and ownership class. Every bin it rejected is listed with the reason.',
        fields: [
          { name: 'directed_bin_id', label: 'Directed Bin', readonly: true },
          { name: 'strategy_used', label: 'Strategy', readonly: true },
          { name: 'rejected_bins', label: 'Bins Rejected (why)', readonly: true },
          { name: 'directed_at', label: 'Directed On', readonly: true },
          { name: 'to_bin_id', label: 'Target Bin (another bin than the directed one is an override)', domain: [['zone_id.reservable', '=', true], ['blocked', '=', false]] }
        ] },
      { tab: 'override', title: 'Override (BRU-WMS-06)', note: 'Another bin than the directed one needs a reason and waits for a Warehouse Supervisor other than you to approve it (list action) before the put-away can be completed.',
        fields: [
          { name: 'override_reason', label: 'Override Reason' },
          { name: 'override_note', label: 'Override Note' },
          { name: 'override_state', label: 'Override', readonly: true },
          { name: 'override_by_id', label: 'Overridden By', readonly: true },
          { name: 'override_approved_by_id', label: 'Approved By', readonly: true }
        ] }
    ]
  },

  'M41-form-putaway-exception': {
    kind: 'model_form', model: 'fix.wms.putaway',
    title: 'Report a Put-Away Exception', newLabel: 'Report a Put-Away Exception', back: 'M41-putaway-exceptions',
    status: { field: 'state', labels: { pending: 'Pending', done: 'Done' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the pending put-away',
      search: 'Search put-away', choose: 'Report on this put-away',
      cols: ['name', 'part_id', 'qty', 'to_bin_id', 'strategy_used'],
      domain: [['state', '=', 'pending']],
      empty: 'No pending put-away.'
    },
    saveAction: { method: 'action_report_exception', label: 'Report Exception', done: 'Recorded: a full or blocked bin is re-directed to the next eligible bin', kwargs: { cause: 'exception_cause_entry', note: 'exception_note_entry' } },
    sections: [
      { title: 'Step 2 of 2: What Went Wrong',
        note: 'FR-WMS-015: a full or blocked bin re-directs the put-away to the next eligible bin (and a full bin is counted back, FR-WMS-033); a damaged item is recorded and stays for an M15 quarantine.',
        fields: [
          { name: 'name', label: 'Put-Away', readonly: true },
          { name: 'part_id', label: 'Spare Part', readonly: true },
          { name: 'qty', label: 'Quantity', readonly: true },
          { name: 'to_bin_id', label: 'Bin', readonly: true },
          { name: 'exception_cause_entry', label: 'What Went Wrong', required: true, readonly: true },
          { name: 'exception_note_entry', label: 'Note', readonly: true }
        ] }
    ]
  },

  'M41-form-dock-door': {
    kind: 'model_form', model: 'fix.wms.dock.door',
    title: 'Dock Door', newLabel: 'New Dock Door', back: 'M41-dock-doors',
    sections: [
      { title: 'Door', note: 'FR-WMS-008: appointments are booked against these doors; an inbound appointment cannot use an outbound-only door. Defined by a Warehouse Supervisor or the IT administrator.',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'code', required: true, label: 'Door' },
          { name: 'name', label: 'Description' },
          { name: 'direction', required: true, label: 'Direction' },
          { name: 'max_vehicle', label: 'Largest Vehicle' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M41-form-hu': {
    kind: 'model_form', model: 'fix.wms.handling.unit',
    title: 'Handling Unit', newLabel: 'New Handling Unit', back: 'M41-handling-units',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed / Labelled', stored: 'Stored', dispatched: 'Dispatched', dissolved: 'Dissolved' } },
    sections: [
      { title: 'Licence Plate', note: 'FR-WMS-010 / T-11: a pallet, carton, tote or cage moved and traced as one object; it nests one level deep. A received unit cannot hold more of a part than its receipt accepted. Close it (label), then Store it by scanning a bin.',
        fields: [
          { name: 'name', label: 'Licence Plate', readonly: true },
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'hu_type', required: true, label: 'Type' },
          { name: 'parent_id', label: 'Inside Handling Unit', domain: [['state', '=', 'open'], ['parent_id', '=', false]] },
          { name: 'receipt_id', label: 'Received On (goods receipt)' },
          { name: 'wave_id', label: 'Outbound Wave' },
          { name: 'gross_weight_kg', label: 'Gross Weight (kg)' },
          { name: 'current_bin_id', label: 'Stored In Bin', readonly: true },
          { name: 'contents_qty', label: 'Units (incl. nested)', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Contents',
      note: 'Each line is a part and quantity (a serialized part: one line per serial).',
      fields: [
        { name: 'part_id', required: true, label: 'Spare Part' },
        { name: 'qty', required: true, label: 'Quantity' },
        { name: 'lot_id', label: 'Serial / Lot' }
      ]
    }
  },

  'M41-form-crossdock': {
    kind: 'model_form', model: 'fix.wms.crossdock',
    title: 'Cross-Dock', newLabel: 'New Cross-Dock', back: 'M41-crossdocks',
    status: { field: 'state', labels: { proposed: 'Proposed', staged: 'Staged', dispatched: 'Dispatched', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Cross-Dock', note: 'FR-WMS-016 / BRU-WMS-15: stock a POSTED receipt accepted (out of inspection) and nobody put away goes straight to an outbound lane for a waiting demand, whole, before its wave is released. Confirm (scan the item) moves it to staged and takes the demand off its wave; Dispatch with the load reference ships it through the M15 document of the demand (transfer, RTV or job issue).',
        fields: [
          { name: 'receipt_line_id', required: true, label: 'Received Line', domain: [['is_posted', '=', true]] },
          { name: 'demand_id', label: 'Waiting Demand', domain: [['state', 'in', ['queued', 'waved']]] },
          { name: 'wave_line_id', label: 'or its Wave Line', domain: [['state', '=', 'pending'], ['wave_id.state', '=', 'draft']] },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'stage_lane', required: true, label: 'Outbound Staging Lane' },
          { name: 'wave_id', label: 'Wave', readonly: true },
          { name: 'demand_qty_before', label: 'Demand Before', readonly: true },
          { name: 'load_ref', label: 'Load / Vehicle Ref', readonly: true },
          { name: 'staged_by_id', label: 'Staged By', readonly: true },
          { name: 'dispatched_by_id', label: 'Dispatched By', readonly: true }
        ] }
    ]
  },

  'M41-form-return': {
    kind: 'model_form', model: 'fix.wms.return.receipt',
    title: 'Return Receiving', newLabel: 'Receive a Return', back: 'M41-returns',
    status: { field: 'state', labels: { received: 'Awaiting Disposition', disposed: 'Disposed' } },
    tabs: [
      { id: 'received', label: '1. What Came Back', bn: '১. কী ফেরত এল', icon: '↩️', badge: '9' },
      { id: 'decision', label: '2. Disposition', bn: '২. নিষ্পত্তি', icon: '⚖️', badge: '2' }
    ],
    sections: [
      { tab: 'received', title: 'Return', note: 'FR-WMS-017: the return is held in a returns-zone bin until a second person decides it.',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'source_type', required: true, label: 'Return Type' },
          { name: 'source_ref', required: true, label: 'Source Document' },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'lot_id', label: 'Serial / Lot' },
          { name: 'condition', required: true, label: 'Condition' },
          { name: 'returns_bin_id', required: true, label: 'Returns Bin', domain: [['zone_id.zone_type', '=', 'returns']] },
          { name: 'receipt_line_id', label: 'M15 Receipt Line (restock)', domain: [['is_posted', '=', true]] }
        ] },
      { tab: 'decision', title: 'Disposition', note: 'Decided (list action) by a Warehouse Supervisor or Inventory Controller who did not receive it. Restock raises a directed put-away of the receipt line; quarantine, RTV, refurbishment and scrap name the M15 record that carries them.',
        fields: [
          { name: 'disposition', label: 'Disposition' },
          { name: 'disposition_note', label: 'Disposition Note / M15 Reference' },
          { name: 'received_by_id', label: 'Received By', readonly: true },
          { name: 'disposed_by_id', label: 'Decided By', readonly: true },
          { name: 'putaway_id', label: 'Restock Put-Away', readonly: true }
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
          { name: 'template_id', label: 'Template (fills strategy and cut-off)' },
          { name: 'strategy', required: true, label: 'Strategy' },
          { name: 'warehouse_id', label: 'Warehouse' },
          { name: 'cutoff_at', label: 'Cut-off' },
          { name: 'priority', label: 'Priority (highest line)', readonly: true },
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
        { name: 'qty', required: true, label: 'Quantity' },
        { name: 'source_type', label: 'Demand Source' },
        { name: 'source_ref', label: 'Source Document' },
        { name: 'dest_location_id', label: 'Destination' },
        { name: 'priority', label: 'Priority' }
      ]
    }
  },

  'M41-form-demand': {
    kind: 'model_form', model: 'fix.wms.outbound.demand',
    title: 'Outbound Demand', newLabel: 'Queue Outbound Demand', back: 'M41-demand',
    status: { field: 'state', labels: { queued: 'Queued', waved: 'Waved', crossdocked: 'Cross-Docked', shipped: 'Shipped', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Demand', note: 'FR-WMS-018: an approved M15 transfer, van replenishment or RTV out of this warehouse queues here by itself, and the wave that picks it dispatches it when it ships; refurbishment, job and manual demand is typed here. It queues with its priority and cut-off. "Build Wave" (Outbound Demand Queue) groups the chosen demand into a draft wave per warehouse and template, picking from free bin stock (pick faces first); a supervisor releases it.',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse', domain: [['wms_enabled', '=', true]] },
          { name: 'source_type', required: true, label: 'Source' },
          { name: 'source_ref', required: true, label: 'Source Document' },
          { name: 'part_id', required: true, label: 'Spare Part' },
          { name: 'qty', required: true, label: 'Quantity' },
          { name: 'dest_location_id', label: 'Destination (not for an RTV)' },
          { name: 'ownership_class', required: true, label: 'Ownership Class (only a job issue draws other than owned)' },
          { name: 'technician_id', label: 'Technician (job demand: the M15 job issue)' },
          { name: 'priority', required: true, label: 'Priority' },
          { name: 'cutoff_at', label: 'Needed By (cut-off)' },
          { name: 'template_id', label: 'Wave Template (filled from the warehouse template)' },
          { name: 'wave_id', label: 'Wave', readonly: true },
          { name: 'transfer_id', label: 'From Transfer (M15)', readonly: true },
          { name: 'rtv_id', label: 'From Return to Vendor (M15)', readonly: true },
          { name: 'consumption_id', label: 'M15 Job Issue', readonly: true },
          { name: 'short_note', label: 'Waiting Because', readonly: true }
        ] }
    ]
  },

  'M41-form-wave-line': {
    kind: 'model_form',
    model: 'fix.wms.wave.line',
    title: 'Pick Line',
    back: 'M41-pick-lines',
    create: false, pick: 'Pick lines are generated when a wave is released: open one from Pick Lines.',
    status: { field: 'state', labels: {
      pending: 'Pending', picked: 'Picked', short: 'Short', cancelled: 'Cancelled', handed: 'Shipped by its Document' } },
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
          { name: 'count_type', label: 'Count Type' },
          { name: 'plan_id', label: 'Count Plan', readonly: true },
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
      { title: 'Template', note: 'FR-WMS-019: a template by purpose (branch run, urgent, van, RTV, refurbishment) with its release rule, cut-off, priority, pick strategy (incl. cluster and pick-and-pass, FR-WMS-021) and the destinations it serves.',
        fields: [
          { name: 'name', required: true, label: 'Template' },
          { name: 'purpose', required: true, label: 'Purpose' },
          { name: 'warehouse_id', label: 'Warehouse' },
          { name: 'strategy', required: true, label: 'Pick Strategy' },
          { name: 'release_rule', required: true, label: 'Release Rule' },
          { name: 'priority', required: true, label: 'Priority' },
          { name: 'zone_id', label: 'Zone' },
          { name: 'cutoff', label: 'Cut-off (HH:MM)' },
          { name: 'dest_location_ids', label: 'Destinations (empty: any)' },
          { name: 'active', label: 'Active' },
          { name: 'armed_by_id', label: 'Automatic Release Set By (supervisor)', readonly: true },
          { name: 'last_released_at', label: 'Last Auto-Release', readonly: true },
          { name: 'last_release_error', label: 'Last Auto-Release Problem', readonly: true }
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
  'M41-spare-part': { kind: 'model_list', model: 'fix.spare.part', stateField: 'state',
    cols: ['name', 'part_number', 'product_id', 'is_serialized', 'uom', 'state', 'active', 'company_id', 'operating_unit_id', 'name_bn'],
    actions: [
      { m: 'action_discontinue', l: 'Discontinue (controller)' },
      { m: 'action_mark_obsolete', l: 'Mark Obsolete (controller)' },
      { m: 'action_reactivate', l: 'Reactivate (controller)' }
    ] },
  'M41-warehouse': { kind: 'model_list', model: 'fix.warehouse',
    cols: ['name', 'code', 'wms_enabled', 'wave_cutoffs', 'shift_pattern', 'active', 'company_id', 'operating_unit_id', 'branch_id'],
    actions: [{ m: 'action_propose_slotting', l: 'Propose Re-slotting Now (supervisor)' }] },

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
      { title: "Warehouse", note: "The M15 location this warehouse's bins break down: put-away, waves, picks and ship move that location's stock.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'code', required: true, label: "Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'active', label: "Active" },
          { name: 'branch_id', label: "Branch" },
          { name: 'stock_location_id', label: "M15 Stock Location" }
        ] },
      { title: "Warehouse Execution (FR-WMS-003)", note: "BRU-WMS-02: only an enabled warehouse is laid out in zones and bins and runs put-away, waves and RF tasks; a branch stockroom stays on M15 alone. A Warehouse Supervisor or the IT administrator enables it; it is turned off only when its bins are empty and no task is open.",
        fields: [
          { name: 'wms_enabled', label: "Warehouse Execution Enabled" },
          { name: 'wave_cutoffs', label: "Wave Cut-offs (HH:MM, comma separated)" },
          { name: 'shift_pattern', label: "Shift Pattern" }
        ] }
    ]
  },

  /* ===== capture audit 2026-11-14: the floor steps, one form each ===== */
  'M41-form-scan-pick': {
    kind: 'model_form', model: 'fix.wms.wave.line',
    title: 'Scan a Pick', newLabel: 'Scan a Pick', back: 'M41-pick-lines',
    status: { field: 'state', labels: { pending: 'Pending', picked: 'Picked', short: 'Short', cancelled: 'Cancelled', handed: 'Shipped by its Document' } },
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
    status: { field: 'state', labels: { pending: 'Pending', picked: 'Picked', short: 'Short', cancelled: 'Cancelled', handed: 'Shipped by its Document' } },
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
  'M41-form-count-plan': {
    kind: 'model_form', model: 'fix.wms.count.plan',
    title: 'Count Plan', newLabel: 'New Count Plan', back: 'M41-count-plans',
    status: { field: 'state', labels: { draft: 'Draft', generated: 'Counting', closed: 'Closed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Plan', note: 'FR-WMS-031: counts by bins, a zone, a velocity (ABC) class or the whole warehouse. Generate raises one BLIND floor count and one count task per slot in scope (a slot already under count is skipped); each result goes to M15 for approval (BRU-WMS-16).',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse', domain: [['wms_enabled', '=', true]] },
          { name: 'scope', required: true, label: 'Scope' },
          { name: 'zone_id', label: 'Zone (scope: zone)' },
          { name: 'bin_ids', label: 'Bins (scope: bins)' },
          { name: 'velocity', label: 'Velocity Class (scope: ABC)' },
          { name: 'count_type', required: true, label: 'Count Type' },
          { name: 'planned_on', required: true, label: 'Planned On' },
          { name: 'assignee_id', label: 'Counter' },
          { name: 'counts_total', label: 'Counts', readonly: true },
          { name: 'counts_open', label: 'Still Open', readonly: true }
        ] }
    ]
  },
  'M41-form-time-standard': {
    kind: 'model_form', model: 'fix.wms.time.standard',
    title: 'Time Standard', newLabel: 'New Time Standard', back: 'M41-time-standards',
    sections: [
      { title: 'Standard', note: 'FR-WMS-035/040: how long a task should take, per task plus per unit, by warehouse and task type (a zone standard wins over the warehouse one). Set by a Warehouse Supervisor.',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'task_type', required: true, label: 'Task Type' },
          { name: 'zone_id', label: 'Zone (empty: all)' },
          { name: 'seconds_per_task', required: true, label: 'Seconds per Task' },
          { name: 'seconds_per_unit', label: 'Seconds per Unit' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M41-form-productivity-run': {
    kind: 'model_form', model: 'fix.wms.productivity.run',
    title: 'Labour Productivity Run', newLabel: 'Measure Labour Productivity', back: 'M41-productivity-runs',
    status: { field: 'state', labels: { draft: 'Draft', done: 'Measured' } },
    sections: [
      { title: 'Period', note: 'FR-WMS-040 / AUT-WMS-15 (also nightly): tasks and units per operative, actual (claimed -> done) against standard time, and pick accuracy, from the tasks the system recorded as done. A supervisor runs Measure from the list.',
        fields: [
          { name: 'warehouse_id', required: true, label: 'Warehouse' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'computed_by_id', label: 'Measured By', readonly: true },
          { name: 'computed_at', label: 'Measured On', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids', title: 'Productivity', readonlyGrid: true,
      fields: [
        { name: 'operative_id', label: 'Operative' },
        { name: 'date', label: 'Date' },
        { name: 'task_type', label: 'Task Type' },
        { name: 'tasks_completed', label: 'Tasks' },
        { name: 'units', label: 'Units' },
        { name: 'actual_seconds', label: 'Actual (s)' },
        { name: 'standard_seconds', label: 'Standard (s)' },
        { name: 'efficiency_pct', label: 'Efficiency %' },
        { name: 'accuracy_pct', label: 'Pick Accuracy %' }
      ]
    }
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
  'M41:Bin Utilisation Heatmap': 'M41-rpt-bins',
  'M41:Attempted Violations': 'M41-rpt-violations',
  'M41:Daily Override Report': 'M41-rpt-overrides',
  'M41:Short-Pick Rate': 'M41-rpt-short',
  'M41:Cycle Times': 'M41-rpt-cycletimes',
  'M41:Put-Away Compliance': 'M41-rpt-compliance',
  'M41:Cross-Dock Utilisation': 'M41-rpt-crossdock',
  'M41:Device Health': 'M41-rpt-devices',
  'M41:Slot vs Ledger Reconciliation': 'M41-rpt-recon'
};

export const FORM_MODELS = {
  'M41:Bin': 'fix.warehouse.bin',
  'M41:Wave Template': 'fix.wms.wave.template',
  'M41:Dock Appointment': 'fix.wms.dock',
  'M41:Packing Station Config': 'fix.wms.packing.station',
  'M41:Internal Move / Replenishment': 'fix.wms.move',
  'M41:RF Device': 'fix.wms.device',
  'M41:Operative Profile': 'fix.wms.operative',
  'M41:Handling Equipment': 'fix.wms.equipment',
  'M41:Dock Door': 'fix.wms.dock.door',
  'M41:Handling Unit': 'fix.wms.handling.unit',
  'M41:Cross-Dock': 'fix.wms.crossdock',
  'M41:Return Receiving': 'fix.wms.return.receipt',
  'M41:Outbound Demand': 'fix.wms.outbound.demand',
  'M41:Count Plan': 'fix.wms.count.plan',
  'M41:Time Standard': 'fix.wms.time.standard',
  'M41:Labour Productivity Run': 'fix.wms.productivity.run',
  'M41:Request a Substitute Part': 'fix.wms.substitution',
  'M41:Opening Slot Load': 'fix.wms.slot.load'
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
  'M41:Report a Put-Away Exception': 'M41-form-putaway-exception',
  'M41:Dock Door': 'M41-form-dock-door',
  /* the inspection is M16's record and form: one form, two pages */
  'M41:Inspection Outcome (M16)': 'M16-form-inspection',
  'M41:Handling Unit': 'M41-form-hu',
  'M41:Cross-Dock': 'M41-form-crossdock',
  'M41:Return Receiving': 'M41-form-return',
  'M41:Outbound Demand': 'M41-form-demand',
  'M41:Count Plan': 'M41-form-count-plan',
  'M41:Time Standard': 'M41-form-time-standard',
  'M41:Labour Productivity Run': 'M41-form-productivity-run',
  'M41:Request a Substitute Part': 'M41-form-substitution',
  'M41:Opening Slot Load': 'M41-form-slot-load',
  'M41:__by_model__': {
    'fix.stock.location': 'M41-form-stock-location',
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
    'fix.wms.equipment': 'M41-form-equipment',
    'fix.wms.dock.door': 'M41-form-dock-door',
    'fix.wms.handling.unit': 'M41-form-hu',
    'fix.wms.crossdock': 'M41-form-crossdock',
    'fix.wms.return.receipt': 'M41-form-return',
    'fix.wms.outbound.demand': 'M41-form-demand',
    'fix.wms.count.plan': 'M41-form-count-plan',
    'fix.wms.time.standard': 'M41-form-time-standard',
    'fix.wms.productivity.run': 'M41-form-productivity-run',
    'fix.wms.substitution': 'M41-form-substitution',
    'fix.wms.slot.load': 'M41-form-slot-load'
  },
  'M41:__by_screen__': {
    'M41-stock-location': 'M41-form-stock-location',
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
    'M41-equipment': 'M41-form-equipment',
    'M41-inspection': 'M16-form-inspection',
    'M41-dock-doors': 'M41-form-dock-door',
    'M41-handling-units': 'M41-form-hu',
    'M41-crossdocks': 'M41-form-crossdock',
    'M41-returns': 'M41-form-return',
    'M41-demand': 'M41-form-demand',
    'M41-count-plans': 'M41-form-count-plan',
    'M41-time-standards': 'M41-form-time-standard',
    'M41-productivity-runs': 'M41-form-productivity-run',
    'M41-substitutions': 'M41-form-substitution',
    'M41-slot-loads': 'M41-form-slot-load'
  }
};

export const CREATE = {
  M41: { screen: 'M41-form-dock', model: 'fix.wms.dock', label: 'Dock Appointment' }
};
