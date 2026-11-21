/** @odoo-module **/
/* A07 · Assets & Facilities — M17 Device & Asset Registry (v2 rebuild).
 * Registry-faithful: 5 groups / 14 screens / 5 reports / 4 forms / freg 96.
 * Capture pass 2 (2026-11-19): labels, identifiers, accessories, configuration,
 * population, estate nodes and placements, end-of-life and stewardship.
 * The device master, warranty, ownership and history existed; estates, PM,
 * condition, identity resolution, custody and installed components are new. */

export const MODULE = {
  area: 'A07', code: 'M17', en: 'Device & Asset Registry', title: 'M17 · Device & Asset Registry',
  bn: 'ডিভাইস ও অ্যাসেট রেজিস্ট্রি', icon: '📱',
  desc: 'Asset register and record with five identifiers, Asset 360, identity resolution and merge, service history, parts genealogy, repeat-fault detection, custody chain, ownership transfers with evidence, lost/stolen flags, identifier history with NEIR status, merge lineage, corporate estates with device placement, bulk estate registration from a file (committed as a set), warranty dates with their derivation basis and PM plans; asset labels, extra identifiers, the accessory register and actual configuration, population changes, estate sites/departments/users with dated placements, end-of-life decisions and the stewardship worklist.',
  kpis: [
    { l: 'Active Devices', m: 'devices_active' },
    { l: 'Estates', m: 'estates' },
    { l: 'PM Due (30d)', m: 'pm_due_30d' },
    { l: 'Lost (open)', m: 'custody_open_lost' },
    { l: 'No Condition', m: 'without_condition' },
    { l: 'Active Warranties', m: 'warranty_active' }
  ],
  groups: [
    { en: 'Alerts', screens: [
      { id: 'M17-alerts', en: 'Alerts', bn: 'সতর্কতা', t: 'g' }
    ]},
    { en: 'Record Coverage', screens: [
      { id: 'M17-device-part-compatibility', en: "Device Part Compatibility", bn: "Device Part Compatibility", t: 'g' }
    ]},
    { en: 'Registry', screens: [
      { id: 'M17-assets', en: 'Asset Register', bn: 'অ্যাসেট রেজিস্টার', t: 'g' },
      { id: 'M17-asset', en: 'Asset Record', bn: 'অ্যাসেট রেকর্ড', t: 'g' },
      { id: 'M17-360', en: 'Asset 360', bn: 'অ্যাসেট ৩৬০', t: 'r' },
      { id: 'M17-identifiers', en: 'Multi-Identifier Model', bn: 'মাল্টি-আইডেন্টিফায়ার', t: 'r' },
      { id: 'M17-merge', en: 'Identity Resolution & Merge', bn: 'আইডেন্টিটি রেজলিউশন', t: 'g' },
      { id: 'M17-merges', en: 'Merge Lineage & Reversal', bn: 'মার্জ লিনিয়েজ', t: 'g' },
      { id: 'M17-idhistory', en: 'Identifier History & NEIR', bn: 'আইডেন্টিফায়ার ইতিহাস ও NEIR', t: 'g' },
      { id: 'M17-labels', en: 'Asset Labels', bn: 'অ্যাসেট লেবেল', t: 'g' },
      { id: 'M17-quality-issues', en: 'Stewardship Worklist', bn: 'ডেটা স্টুয়ার্ডশিপ', t: 'g' }
    ]},
    { en: 'Intake & Configuration', screens: [
      { id: 'M17-accessories', en: 'Accessory Register', bn: 'আনুষঙ্গিক রেজিস্টার', t: 'g' },
      { id: 'M17-configs', en: 'Actual Configuration', bn: 'প্রকৃত কনফিগারেশন', t: 'g' }
    ]},
    { en: 'History', screens: [
      { id: 'M17-history', en: 'Service History', bn: 'সেবা ইতিহাস', t: 'g' },
      { id: 'M17-genealogy', en: 'Parts Genealogy', bn: 'পার্টস বংশতালিকা', t: 'r' },
      { id: 'M17-rework', en: 'Repeat-Fault Detection', bn: 'পুনরাবৃত্তি ত্রুটি', t: 'r' },
      { id: 'M17-components', en: 'Installed Components', bn: 'ইনস্টলড কম্পোনেন্ট', t: 'g' }
    ]},
    { en: 'Custody', screens: [
      { id: 'M17-custody', en: 'Custody State & Chain', bn: 'কাস্টডি চেইন', t: 'g' },
      { id: 'M17-ownership', en: 'Ownership & Transfers', bn: 'মালিকানা হস্তান্তর', t: 'g' },
      { id: 'M17-holds', en: 'Lost / Stolen Holds', bn: 'হারানো / চুরি হোল্ড', t: 'g' },
      { id: 'M17-populations', en: 'Population Changes', bn: 'পপুলেশন পরিবর্তন', t: 'g' }
    ]},
    { en: 'Corporate Estates', screens: [
      { id: 'M17-estates', en: 'Estates (Site/Dept/User)', bn: 'কর্পোরেট এস্টেট', t: 'g' },
      { id: 'M17-estate-nodes', en: 'Estate Sites, Departments & Users', bn: 'এস্টেট নোড', t: 'g' },
      { id: 'M17-placements', en: 'Estate Placements & Moves', bn: 'এস্টেট প্লেসমেন্ট', t: 'g' },
      { id: 'M17-bulk-loads', en: 'Bulk Registrations', bn: 'বাল্ক রেজিস্ট্রেশন', t: 'g' },
      { id: 'M17-bulk-lines', en: 'Bulk Registration Lines', bn: 'বাল্ক রেজিস্ট্রেশন লাইন', t: 'g' },
      { id: 'M17-bulk', en: 'Bulk Readiness', bn: 'বাল্ক প্রস্তুতি', t: 'r' }
    ]},
    { en: 'Coverage', screens: [
      { id: 'M17-wty', en: 'Warranty Dates & Priority', bn: 'ওয়ারেন্টি তারিখ', t: 'g' },
      { id: 'M17-conditions', en: 'Condition Grades', bn: 'কন্ডিশন গ্রেড', t: 'g' },
      { id: 'M17-pm', en: 'PM Plans', bn: 'পিএম প্ল্যান', t: 'g' },
      { id: 'M17-eol', en: 'End-of-Life Decisions', bn: 'জীবনশেষ সিদ্ধান্ত', t: 'g' }
    ]}
  ],
  reports: ['Installed Base by Brand/Model', 'Repeat-Fault Pareto', 'Estate Coverage by Client', 'Custody Exceptions', 'Data Quality Scorecard'],
  // M17 capture audit (2026-11-13): every sub-module page names the form that
  // captures its record. Before, Ownership & Custody, Bulk Registration and
  // Corporate Estates offered no way to record a custody event, a transfer, a
  // lost/stolen report, a device's estate placement or an estate file; the
  // compatibility and PM forms existed but no page offered them.
  forms: ['Asset (5 identifiers)', 'Corporate Estate', 'Estate Assignment', 'Ownership Transfer',
    'Custody Event', 'Report Lost / Stolen', 'Condition Grading', 'PM Plan', 'Installed Component',
    'Part Compatibility', 'Identity Resolution', 'Bulk Estate Upload',
    // M17 capture pass 2 (2026-11-19): the records pages 1, 2, 3, 8, 10 and
    // 11 still could not capture (FR-AST-002/008/012/015/022/038/048/051).
    'Asset Label', 'Add Identifier', 'Accessory Received', 'Configuration Record',
    'Population Change', 'Estate Node', 'End-of-Life Decision', 'Stewardship Issue'],
  cross: ['M01 every order links asset', 'M09 warranty evidence', 'M05 monitored assets', 'M48 telemetry streams', 'P01 customer devices'],
  freg: { src: 96, sub: [
    // M17 capture audit (2026-11-13). Each page offers the capture its record
    // has: a "+ New" or chip for what a person records; nothing, and a list
    // that says where its rows come from, for what the system writes (service
    // history is projected from orders, repeat faults are detected from it).
    ['1', 'Identity & Resolution', 14, { model: 'fix.device', cols: ['name', 'serial_number', 'imei_1', 'mac_address', 'legacy_reference'], screens: ['M17-asset', 'M17-identifiers', 'M17-assets', 'M17-idhistory', 'M17-labels'], reports: ['Installed Base by Brand/Model', 'Data Quality Scorecard'], forms: ['Asset (5 identifiers)', 'Asset Label', 'Add Identifier'] }],
    ['2', 'Configuration & Components', 8, { model: 'fix.device.component', cols: ['device_id', 'part_name', 'serial_no', 'installed_on', 'state'], screens: ['M17-components', 'M17-device-part-compatibility', 'M17-accessories', 'M17-configs'], reports: [], forms: ['Installed Component', 'Part Compatibility', 'Accessory Received', 'Configuration Record'] }],
    ['3', 'Ownership & Custody', 12, { model: 'fix.device.ownership', cols: ['device_id', 'from_partner_id', 'to_partner_id', 'transfer_type', 'transfer_date'], screens: ['M17-ownership', 'M17-custody', 'M17-holds', 'M17-populations'], reports: ['Custody Exceptions'], forms: ['Ownership Transfer', 'Custody Event', 'Report Lost / Stolen', 'Population Change'], create: 'M17-form-custody' }],
    ['4', 'Service History', 9, { model: 'fix.device.history', cols: ['date', 'device_id', 'event_type', 'description', 'technician_id'], screens: ['M17-history', 'M17-360'], reports: ['Repeat-Fault Pareto'], forms: [], create: false }],
    ['5', 'Parts Genealogy', 7, { model: 'fix.device.component', cols: ['device_id', 'part_name', 'serial_no', 'source_ref', 'removed_on'], screens: ['M17-genealogy', 'M17-components'], reports: [], forms: ['Installed Component'] }],
    ['6', 'Repeat-Fault Detection', 6, { model: 'fix.device.history', cols: ['device_id', 'date', 'event_type', 'service_order_id', 'description'], screens: ['M17-rework', 'M17-history'], reports: ['Repeat-Fault Pareto'], forms: [], create: false, domain: [['event_type', 'in', ['repair', 'service_order']]] }],
    ['7', 'Warranty Projection', 7, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'start_date', 'end_date', 'derivation_basis', 'status'], screens: ['M17-wty'], reports: [], forms: ['Device Warranty'] }],
    ['8', 'Corporate Estates', 12, { model: 'fix.device.estate', cols: ['name', 'client_id', 'site', 'department', 'cost_centre'], screens: ['M17-estates', 'M17-estate-nodes', 'M17-placements', 'M17-assets'], reports: ['Estate Coverage by Client'], forms: ['Corporate Estate', 'Estate Node', 'Estate Assignment'] }],
    ['9', 'Bulk Registration', 7, { model: 'fix.device.bulk.load', cols: ['name', 'estate_id', 'upload_filename', 'line_count', 'error_count', 'state'], screens: ['M17-bulk-loads', 'M17-bulk-lines', 'M17-bulk', 'M17-assets'], reports: ['Installed Base by Brand/Model'], forms: ['Bulk Estate Upload'], create: 'M17-form-bulk' }],
    ['10', 'Condition & EOL Routing', 8, { model: 'fix.device.condition', cols: ['device_id', 'grade', 'functional_ok', 'battery_health_pct', 'graded_on'], screens: ['M17-conditions', 'M17-pm', 'M17-eol', 'M17-assets'], reports: [], forms: ['Condition Grading', 'PM Plan', 'End-of-Life Decision'] }],
    ['11', 'Data Quality', 6, { model: 'fix.device.identity', cols: ['name', 'primary_device_id', 'duplicate_device_id', 'match_score', 'state'], screens: ['M17-merge', 'M17-quality-issues', 'M17-merges', 'M17-identifiers', 'M17-alerts'], reports: ['Data Quality Scorecard'], forms: ['Identity Resolution', 'Stewardship Issue'] }]
  ] }
};

export const SCREENS = {
  'M17-form-compat': {
    kind: 'model_form',
    model: 'fix.device.part.compatibility',
    title: "Part Compatibility",
    back: 'M17-device-part-compatibility',
    sections: [
      { title: "Part Compatibility", note: "The compatibility map that tells a technician which part fits which device model. Category and type are required because the parts search filters on them.",
        fields: [
          { name: 'model_id', required: true, label: "Device Model" },
          { name: 'brand_id', label: "Brand" },
          { name: 'part_number', required: true, label: "Part Number" },
          { name: 'part_name', required: true, label: "Part Name" },
          { name: 'category', required: true, label: "Category" },
          { name: 'compatibility_type', required: true, label: "Compatibility Type" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },

  'M17-alerts': { kind: 'model_list', model: 'fix.asset.alert', stateField: 'state', create: false,
    empty: 'No alert. The scheduled registry checks raise alerts here.',
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M17']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  'M17-assets': { kind: 'model_list', model: 'fix.device', stateField: 'state',
    cols: ['name', 'serial_number', 'asset_tag', 'device_model_id', 'owner_id', 'population', 'state', 'custody_state', 'ownership_disputed', 'identifier_quarantined', 'lifecycle_stage', 'neir_status', 'approval_state'],
    // A07 audit M17-8: the state moves only through these. A Branch Manager
    // other than the flagger clears a lost flag; scrap is decided from the M63
    // approval inbox by a Device Quality Manager who did not request it.
    // A07 P1: Transfer Ownership reads the recipient, reason and evidence
    // staged on the asset form (Device Registry Agent role).
    actions: [
      { m: 'action_transfer_ownership', l: 'Transfer Ownership (staged on the form)' },
      { m: 'action_correct_identifier', l: 'Correct Identifier (Quality Manager, staged on the form)' },
      { m: 'action_confirm_identity', l: 'Confirm Provisional Identity' },
      { m: 'action_mark_lost', l: 'Flag Lost / Stolen', ask: 'How was the loss or theft reported?', kwarg: 'reason' },
      { m: 'action_clear_lost', l: 'Clear Lost Flag (Branch Manager)', ask: 'How was it recovered, or why is the report withdrawn?', kwarg: 'reason' },
      // A07 ERP audit (2026-11-20) D12(b): a disputed ownership holds the device
      // like a lost flag; a Branch Manager who did not raise it clears it.
      { m: 'action_flag_disputed', l: 'Flag Ownership Disputed', ask: 'Who disputes the ownership, and on what basis?', kwarg: 'reason' },
      { m: 'action_clear_dispute', l: 'Clear Ownership Dispute (Branch Manager)', ask: 'How was the dispute settled?', kwarg: 'reason' },
      // M17-11: the purchase date is corrected only by a Warranty Officer.
      { m: 'action_correct_purchase_date', l: 'Correct Purchase Date (Warranty Officer, staged on the form)' },
      { m: 'action_set_vintage', l: 'Lifecycle: Vintage', ask: 'Basis for the decision?', kwarg: 'reason' },
      { m: 'action_return_to_active', l: 'Lifecycle: Back to Active (from Vintage)', ask: 'Basis for the decision?', kwarg: 'reason' },
      { m: 'action_set_end_of_support', l: 'Lifecycle: End of OEM Support', ask: 'Basis for the decision?', kwarg: 'reason' },
      { m: 'action_set_obsolete', l: 'Lifecycle: Obsolete (customer instruction required)', ask: 'Basis for the end-of-life decision?', kwarg: 'reason' },
      { m: 'action_request_approval', l: 'Request Scrap Approval (Quality Manager)', ask: 'Why should this device be scrapped?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M17-asset': { kind: 'model_list', model: 'fix.device',
    cols: ['serial_number', 'imei_1', 'imei_2', 'mac_address', 'legacy_reference', 'estate_id'] },
  'M17-360': { kind: 'table_report', module: 'M17', report: 'asset_360', title: 'Asset 360', period: true },
  'M17-identifiers': { kind: 'table_report', module: 'M17', report: 'identifiers', title: 'Multi-Identifier Model', period: true },
  'M17-merge': { kind: 'model_list', model: 'fix.device.identity', stateField: 'state',
    cols: ['name', 'primary_device_id', 'duplicate_device_id', 'match_reason', 'match_score', 'state', 'approval_state'],
    // A07 audit M17-3: a Device Quality Manager who neither raised nor
    // requested the candidate merges it from the M63 approval inbox. Here it
    // is only routed.
    actions: [
      { m: 'action_request_approval', l: 'Request Merge Approval (Quality Manager)', ask: 'Why are these the same device? (required if owners or models differ)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_reject', l: 'Reject (not a duplicate)' }
    ] },
  // Projected from the service orders, repairs, transfers and registry events
  // that touch the device (AUT-AST-05); never typed, so a forged repair cannot
  // put a device on the repeat-fault list.
  'M17-history': { kind: 'model_list', create: false, model: 'fix.device.history', stateField: 'event_type',
    empty: 'Nothing has happened to these devices yet. A history row is written by each service order, repair, ownership transfer and registry event on the device; it is not entered by hand.',
    cols: ['date', 'device_id', 'event_type', 'description', 'technician_id'] },
  'M17-genealogy': { kind: 'table_report', module: 'M17', report: 'parts_genealogy', title: 'Parts Genealogy', period: true },
  'M17-rework': { kind: 'table_report', module: 'M17', report: 'repeat_fault', title: 'Repeat-Fault Detection', period: true },
  'M17-components': { kind: 'model_list', model: 'fix.device.component', stateField: 'state',
    cols: ['device_id', 'part_name', 'part_number', 'serial_no', 'installed_on', 'warranty_until', 'removed_on', 'disposition', 'state'],
    actions: [
      { m: 'action_remove', l: 'Remove Component' },
      { m: 'action_dispose_returned', l: 'Disposition: Returned to Customer' },
      { m: 'action_dispose_harvested', l: 'Disposition: Harvested' },
      { m: 'action_dispose_returned_to_brand', l: 'Disposition: Returned to Brand' },
      { m: 'action_dispose_scrapped', l: 'Disposition: Scrapped' }
    ] },
  'M17-custody': { kind: 'model_list', model: 'fix.device.custody', stateField: 'event',
    cols: ['name', 'device_id', 'event', 'from_party_id', 'to_party_id', 'event_date', 'condition_id', 'accessories_reconciled'] },
  // Ownership rows are written only by Transfer Ownership on the asset.
  'M17-ownership': { kind: 'model_list', create: false, model: 'fix.device.ownership',
    empty: 'No ownership transfer is recorded. A transfer is recorded with Ownership Transfer on the Ownership & Custody page (or Transfer Ownership on the Asset Register), with its reason and evidence.',
    cols: ['device_id', 'from_partner_id', 'to_partner_id', 'transfer_type', 'transfer_date', 'reason', 'recorded_by_id', 'channel'] },
  // Written by the M17 lost/stolen flag and its clearance; nobody types a hold.
  'M17-holds': { kind: 'model_list', create: false, model: 'fix.service.order.device.hold', stateField: 'state',
    empty: 'No hold. A hold is placed on each open service order of a device reported lost or stolen (Report Lost / Stolen).',
    note: 'One row for each open service order of a device reported lost or stolen. While a hold is open the order cannot be handed over. A Branch Manager ends it by clearing the lost flag on the Asset Register.',
    cols: ['name', 'order_id', 'device_id', 'branch_id', 'reason', 'flagged_by_id', 'flagged_at', 'cleared_by_id', 'cleared_at', 'state'] },
  'M17-merges': { kind: 'model_list', create: false, model: 'fix.device.merge', stateField: 'state',
    empty: 'No merge yet. A merge is written when a Quality Manager approves an identity resolution from the approval inbox.',
    cols: ['name', 'survivor_id', 'merged_id', 'approved_by_id', 'merged_at', 'reversible_until', 'rows_repointed', 'state'],
    actions: [{ m: 'action_reverse', l: 'Reverse Merge (Quality Manager, inside the window)', ask: 'Why is the merge reversed?', kwarg: 'reason' }] },
  'M17-idhistory': { kind: 'model_list', create: false, model: 'fix.device.identifier', stateField: 'neir_status',
    empty: 'No identifier recorded. Each serial and IMEI is written here when a device is registered, captured or corrected.',
    cols: ['device_id', 'identifier_type', 'value', 'source', 'captured_by_id', 'captured_at', 'is_current', 'neir_status', 'neir_reference'],
    // B4: NEIR results are recorded by a Branch Manager with the BTRC/operator reference.
    actions: [
      { m: 'action_neir_registered', l: 'NEIR: Registered', ask: 'NEIR / BTRC reference?', kwarg: 'reference' },
      { m: 'action_neir_deregistered', l: 'NEIR: De-registered', ask: 'NEIR / BTRC reference?', kwarg: 'reference' },
      { m: 'action_neir_blocked', l: 'NEIR: Blocked / Blacklisted', ask: 'NEIR / BTRC reference?', kwarg: 'reference' }
    ] },
  'M17-estates': { kind: 'model_list', model: 'fix.device.estate',
    cols: ['name', 'client_id', 'site', 'department', 'cost_centre', 'manager_id', 'active'] },
  'M17-bulk': { kind: 'table_report', module: 'M17', report: 'bulk_registration', title: 'Bulk Registration', period: true },
  'M17-conditions': { kind: 'model_list', model: 'fix.device.condition', stateField: 'state',
    cols: ['name', 'device_id', 'grade', 'functional_ok', 'battery_health_pct', 'graded_on', 'state'],
    actions: [{ m: 'action_confirm', l: 'Confirm Grade' }] },
  'M17-wty': { kind: 'model_list', model: 'fix.warranty', stateField: 'status',
    cols: ['device_id', 'warranty_type', 'start_date', 'end_date', 'derivation_basis', 'status', 'verification_state', 'verification_blocker', 'approval_state'],
    // Verification is requested here and decided from a Warranty Officer's inbox.
    actions: [
      { m: 'action_request_approval', l: 'Request Verification', ask: 'What proof is attached?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' }
    ] },
  'M17-pm': { kind: 'model_list', model: 'fix.device.pm', stateField: 'state',
    cols: ['name', 'device_id', 'plan_type', 'interval_months', 'last_done', 'next_due', 'due_notified_for', 'state'],
    actions: [
      { m: 'action_complete', l: 'Mark Done' },
      { m: 'action_reschedule', l: 'Reschedule (Branch Manager)', asks: [
        { label: 'New due date (YYYY-MM-DD)', kwarg: 'next_due' },
        { label: 'Why is the plan rescheduled?', kwarg: 'reason' }
      ] },
      { m: 'action_pause', l: 'Pause Plan' },
      { m: 'action_resume', l: 'Resume Plan' }
    ] },

  /* Report chips -> their own computed pack */
  'M17-rpt-base': { kind: 'table_report', module: 'M17', report: 'installed_base', title: 'Installed Base by Brand/Model', period: true },
  'M17-rpt-repeat': { kind: 'table_report', module: 'M17', report: 'repeat_fault', title: 'Repeat-Fault Pareto', period: true },
  'M17-rpt-estate': { kind: 'table_report', module: 'M17', report: 'estate_coverage', title: 'Estate Coverage by Client', period: true },
  'M17-rpt-custody': { kind: 'table_report', module: 'M17', report: 'custody_exceptions', title: 'Custody Exceptions', period: true },
  'M17-rpt-quality': { kind: 'table_report', module: 'M17', report: 'data_quality', title: 'Data Quality Scorecard', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M17-form-asset': {
    kind: 'model_form',
    model: 'fix.device',
    title: 'Asset (5 identifiers)',
    back: 'M17-assets',
    status: { field: 'state', labels: {
      provisional: 'Provisional', registered: 'Registered', transferred: 'Ownership Transferred',
      scrapped: 'Scrapped', lost: 'Lost/Stolen' } },
    tabs: [
      { id: 'identity', label: '1. Identifiers', bn: '১. শনাক্তকারী', icon: '🏷️' },
      { id: 'ownership', label: '2. Ownership & Estate', bn: '২. মালিকানা ও এস্টেট', icon: '👤' },
      { id: 'transfer', label: '3. Ownership Transfer', bn: '৩. মালিকানা হস্তান্তর', icon: '🔁' },
      { id: 'correction', label: '4. Identifier Correction', bn: '৪. শনাক্তকারী সংশোধন', icon: '✏️' },
      { id: 'lifecycle', label: '5. Lifecycle', bn: '৫. জীবনচক্র', icon: '📈' }
    ],
    sections: [
      { tab: 'identity', title: 'Identifiers', note: 'Give the serial or an IMEI; IMEI-2 and MAC are for devices that have them. Once captured, a serial or IMEI is changed only by a Quality Manager correction, which keeps the old value in the identifier history. Case and spacing variants of a registered serial, and an IMEI already on another device, are refused.',
        fields: [
          { name: 'serial_number', label: 'Serial Number' },
          { name: 'imei_1', label: 'IMEI 1' },
          { name: 'imei_2', label: 'IMEI 2' },
          { name: 'mac_address', label: 'MAC Address' },
          { name: 'legacy_reference', label: 'Legacy Reference' },
          { name: 'device_model_id', required: true, label: 'Device Model' },
          { name: 'identifier_warning', label: 'Identifier Warning', readonly: true },
          { name: 'asset_tag', label: '1000FiX Asset Tag', readonly: true },
          { name: 'neir_status', label: 'NEIR Status', readonly: true }
        ] },
      { tab: 'identity', title: 'Identity Not Confirmed', note: 'Only when registering a device whose serial and IMEI cannot be read: tick this and say why. It can be taken in and diagnosed, but gets no warranty claim, invoice or transfer until its identifier is captured and Confirm Provisional Identity is pressed.',
        fields: [
          { name: 'register_provisional', type: 'boolean', label: 'Register as Provisional' },
          { name: 'provisional_reason', label: 'Why the Identity Is Unconfirmed' }
        ] },
      { tab: 'ownership', title: 'Ownership & Estate', note: 'The owner changes only by Transfer Ownership. A device joins an estate only when its owner is the estate client or one of its contacts.',
        fields: [
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'estate_id', label: 'Corporate Estate' },
          { name: 'estate_node_id', label: 'Estate Site / Department / User', readonly: true },
          { name: 'population', label: 'Population', readonly: true },
          { name: 'branch_id', label: 'Registered At' },
          { name: 'purchase_date', label: 'Purchase Date' },
          { name: 'custody_state', label: 'Custody State', readonly: true },
          { name: 'custody_party_id', label: 'Held By', readonly: true },
          { name: 'custody_branch_id', label: 'Held At', readonly: true },
          { name: 'dormant', label: 'Dormant', readonly: true },
          { name: 'ownership_disputed', label: 'Ownership Disputed', readonly: true },
          { name: 'dispute_reason', label: 'Dispute', readonly: true },
          { name: 'identifier_quarantined', label: 'Quarantined (Identifier Conflict)', readonly: true }
        ] },
      { tab: 'correction', title: 'Purchase Date Correction', note: 'Once recorded, the purchase date decides warranty and plan eligibility and is changed only here: fill these, save, then press Correct Purchase Date on the asset list (Warranty Officer). The receipt or invoice showing the date is required.',
        fields: [
          { name: 'purchase_date_correction', label: 'Corrected Purchase Date' },
          { name: 'purchase_date_correction_reason', label: 'Correction Reason' },
          { name: 'purchase_date_proof_file', type: 'file', label: 'Upload Purchase Proof' },
          { name: 'purchase_date_proof_filename', label: 'Proof File Name' },
          { name: 'purchase_date_proof_document_id', label: 'Or Choose Filed Proof' }
        ] },
      { tab: 'transfer', title: 'Ownership Transfer', note: 'Fill these, save, then press Transfer Ownership on the asset list (Device Registry Agent). The type, the reason and the evidence are required: a sale receipt, deed or signed hand-over, uploaded here or chosen from those already filed, and used for one transfer only. The system records the evidence; it does not ask the new owner to accept. They are cleared once the transfer is recorded. A lost, scrapped, provisional or NEIR-blocked device is not transferred.',
        fields: [
          { name: 'transfer_to_partner_id', label: 'Transfer To' },
          { name: 'transfer_type_pending', label: 'Transfer Type' },
          { name: 'transfer_reason', label: 'Transfer Reason' },
          { name: 'transfer_effective_date', label: 'Effective On (default today)' },
          { name: 'transfer_evidence_file', type: 'file', label: 'Upload Transfer Evidence' },
          { name: 'transfer_evidence_filename', label: 'Evidence File Name' },
          { name: 'transfer_evidence_document_id', label: 'Transfer Evidence' }
        ] },
      { tab: 'correction', title: 'Identifier Correction', note: 'For a serial or IMEI that is wrong (a board swap, a mistyped intake). Fill these, save, then press Correct Identifier on the asset list (Quality Manager). The old value stays in the identifier history with the reason.',
        fields: [
          { name: 'correction_field', label: 'Identifier to Correct' },
          { name: 'correction_value', label: 'Corrected Value' },
          { name: 'correction_reason', label: 'Correction Reason' }
        ] },
      { tab: 'lifecycle', title: 'Lifecycle', note: 'State changes only by Flag Lost, Clear Lost Flag (Branch Manager), Confirm Provisional Identity, an ownership transfer or an approved scrap. The lifecycle stage changes only by the Lifecycle buttons (Branch Manager, with a basis). Making a customer-owned device obsolete, or scrapping it, needs the customer instruction below.',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'lifecycle_stage', label: 'Lifecycle Stage', readonly: true },
          { name: 'end_of_support_date', label: 'End of Support Date', readonly: true },
          { name: 'eol_customer_instruction', label: 'Customer End-of-Life Instruction' },
          { name: 'lifecycle_reason', label: 'Lifecycle Decision Basis', readonly: true },
          { name: 'lifecycle_decided_by_id', label: 'Lifecycle Decided By', readonly: true },
          { name: 'approval_state', label: 'Scrap Approval', readonly: true },
          { name: 'lost_reason', label: 'Lost / Stolen Report', readonly: true },
          { name: 'lost_flagged_by_id', label: 'Flagged Lost By', readonly: true },
          { name: 'lost_cleared_by_id', label: 'Lost Flag Cleared By', readonly: true }
        ] }
    ]
  },

  'M17-form-estate': {
    kind: 'model_form',
    model: 'fix.device.estate',
    title: 'Corporate Estate',
    back: 'M17-estates',
    sections: [
      { title: 'Estate', note: 'An estate groups a client\x27s devices by site and department; assignment is on the device record.',
        fields: [
          { name: 'name', required: true, label: 'Estate' },
          { name: 'client_id', required: true, label: 'Client' },
          { name: 'site', label: 'Site' },
          { name: 'department', label: 'Department' },
          { name: 'cost_centre', label: 'Cost Centre' },
          { name: 'manager_id', label: 'Estate Manager' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M17-form-transfer': {
    kind: 'model_form',
    model: 'fix.device.ownership',
    title: 'Ownership Transfer',
    back: 'M17-ownership',
    create: false, pick: 'A transfer is staged on the asset (Asset Register, open the asset, Ownership Transfer tab) and recorded by Transfer Ownership; past transfers are listed here.',
    sections: [
      { title: 'Transfer', note: 'A transfer is a permanent audit record written only by Transfer Ownership on the asset: the device, both parties, the type, the date, the reason, the evidence and who recorded it. It is never edited here.',
        fields: [
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'from_partner_id', label: 'From', readonly: true },
          { name: 'to_partner_id', label: 'To', readonly: true },
          { name: 'transfer_type', label: 'Type', readonly: true },
          { name: 'transfer_date', label: 'Transfer Date', readonly: true },
          { name: 'reason', label: 'Reason', readonly: true },
          { name: 'evidence_document_id', label: 'Evidence', readonly: true },
          { name: 'recorded_by_id', label: 'Recorded By', readonly: true },
          { name: 'channel', label: 'Channel', readonly: true },
          { name: 'notes', type: 'text', label: 'Notes', readonly: true }
        ] }
    ]
  },

  // The chip lands here: a transfer is made on the device, so this says how.
  'M17-form-condition': {
    kind: 'model_form',
    model: 'fix.device.condition',
    title: 'Condition Grading',
    back: 'M17-assets',
    status: { field: 'state', labels: { draft: 'Draft', confirmed: 'Confirmed' } },
    sections: [
      { title: 'Condition', note: 'The confirmed grade is what the data-quality scorecard and bulk readiness read. Someone other than the grader confirms it, and a confirmed grade is never edited.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'grade', required: true, label: 'Grade' },
          { name: 'functional_ok', label: 'Functional OK' },
          { name: 'battery_health_pct', label: 'Battery Health %' },
          { name: 'cosmetic_notes', label: 'Cosmetic Notes' },
          { name: 'inspector_id', label: 'Inspector' },
          { name: 'graded_on', required: true, label: 'Graded On' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'confirmed_by_id', label: 'Confirmed By', readonly: true }
        ] }
    ]
  },

  'M17-form-pm': {
    kind: 'model_form',
    model: 'fix.device.pm',
    title: 'PM Plan',
    back: 'M17-pm',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused' } },
    sections: [
      { title: 'Preventive Maintenance', note: 'The plan type sets the interval (quarterly 3, bi-annual 6, annual 12 months; choose Custom interval for another). Mark Done rolls the next due date on; a daily job announces each plan when it falls due.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'plan_type', required: true, label: 'Plan Type' },
          { name: 'interval_months', label: 'Interval (months)' },
          { name: 'last_done', label: 'Last Done', readonly: true },
          { name: 'next_due', required: true, label: 'Next Due' },
          { name: 'due_notified_for', label: 'Due Announced For', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M17-form-identity': {
    kind: 'model_form',
    model: 'fix.device.identity',
    title: 'Identity Resolution',
    back: 'M17-merge',
    status: { field: 'state', labels: {
      candidate: 'Candidate', merged: 'Merged', rejected: 'Rejected', reversed: 'Merge Reversed' } },
    sections: [
      { title: 'Resolution', note: 'An approved merge archives the duplicate device (never deleted) and re-points its history, warranties, orders and other records to the survivor; the lineage keeps the reference map, so a Quality Manager can reverse it inside the window. A Device Quality Manager who neither raised nor requested it decides it from the approval inbox.',
        fields: [
          { name: 'primary_device_id', required: true, label: 'Surviving Device' },
          { name: 'duplicate_device_id', required: true, label: 'Duplicate Device' },
          { name: 'match_reason', required: true, label: 'Match Reason' },
          { name: 'match_score', label: 'Match Score %' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'approval_state', label: 'Merge Approval', readonly: true },
          { name: 'resolved_by_id', label: 'Resolved By', readonly: true },
          { name: 'merge_id', label: 'Merge Lineage', readonly: true },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M17-form-custody': {
    kind: 'model_form',
    model: 'fix.device.custody',
    title: 'Custody Event',
    back: 'M17-custody',
    status: { field: 'event', labels: {
      issued: 'Issued', returned: 'Returned', transferred: 'Transferred',
      lost: 'Lost', found: 'Recovered' } },
    sections: [
      { title: 'Custody', note: 'Events are permanent: never edited or dated in the future; record the next event instead. A Reported Lost event puts the device in the lost register; a Recovered event does not end it, a Branch Manager clearing the flag does. A lost, scrapped or NEIR-blocked device is released to no one.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'event', required: true, label: 'Event' },
          { name: 'from_party_id', label: 'From' },
          { name: 'to_party_id', label: 'To' },
          { name: 'custodian_id', label: 'Custodian' },
          { name: 'event_date', required: true, label: 'Event Date' },
          { name: 'reference', label: 'Reference' },
          { name: 'notes', label: 'Notes' }
        ] },
      { title: 'Release Evidence', note: 'Issued to Customer goes only to the owner and needs a confirmed condition grade of this device, a photograph (uploaded here, or chosen from those filed; each hand-over has its own) and the accessory reconciliation.',
        fields: [
          { name: 'condition_id', label: 'Condition Grade at Release' },
          { name: 'evidence_file', type: 'file', label: 'Upload Photograph' },
          { name: 'evidence_filename', label: 'Photograph File Name' },
          { name: 'evidence_document_id', label: 'Photographic Evidence' },
          { name: 'accessories_reconciled', label: 'Accessories Reconciled' },
          { name: 'accessory_notes', label: 'Accessory Discrepancies' },
          { name: 'signature_ref', label: 'Signature Reference' }
        ] }
    ]
  },

  'M17-form-component': {
    kind: 'model_form',
    model: 'fix.device.component',
    title: 'Installed Component',
    back: 'M17-components',
    status: { field: 'state', labels: {
      installed: 'Installed', removed: 'Removed' } },
    tabs: [
      { id: 'part', label: '1. Component', bn: '১. কম্পোনেন্ট', icon: '🔩' },
      { id: 'origin', label: '2. Origin & Warranty', bn: '২. উৎস ও ওয়ারেন্টি', icon: '📦' },
      { id: 'removal', label: '3. Removal', bn: '৩. অপসারণ', icon: '♻️' }
    ],
    sections: [
      { tab: 'part', title: 'Component', note: 'One row per installation; removal is an explicit action with its own date. A serial is installed in one device at a time, and a part the compatibility matrix grades incompatible for the model is refused.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'part_name', required: true, label: 'Part / Component' },
          { name: 'part_number', label: 'Part Number' },
          { name: 'product_id', label: 'Part (Catalogue)' },
          { name: 'serial_no', label: 'Component Serial' },
          { name: 'installed_on', required: true, label: 'Installed On' },
          { name: 'notes', label: 'Notes' }
        ] },
      { tab: 'origin', title: 'Origin & Warranty', note: 'Which job fitted it, who fitted it, which stock lot it came from and how long its own warranty runs.',
        fields: [
          { name: 'causing_order_id', label: 'Causing Job' },
          { name: 'technician_id', label: 'Fitted By' },
          { name: 'stock_lot_ref_id', label: 'Stock Lot' },
          { name: 'source_ref', label: 'Source Order / PO' },
          { name: 'ownership_class', label: 'Ownership Class' },
          { name: 'warranty_until', label: 'Part Warranty Until' }
        ] },
      { tab: 'removal', title: 'Removal', note: 'Set by Remove Component and the Disposition buttons on the Installed Components list.',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'removed_on', label: 'Removed On', readonly: true },
          { name: 'disposition', label: 'Removed-Part Disposition', readonly: true }
        ] }
    ]
  },


  'M17-form-hold': {
    kind: 'model_form',
    model: 'fix.service.order.device.hold',
    title: 'Lost / Stolen Hold',
    back: 'M17-holds',
    create: false, pick: 'A hold is raised by flagging a device lost or stolen on the Asset Register: open one from Lost / Stolen Holds.',
    status: { field: 'state', labels: { open: 'Device Reported Lost / Stolen', cleared: 'Flag Cleared' } },
    sections: [
      { title: 'Hold', note: 'Raised by the lost or stolen flag on the device, and ended only by a Branch Manager clearing that flag. While it is open the service order cannot be handed over.',
        fields: [
          { name: 'name', label: 'Hold', readonly: true },
          { name: 'order_id', label: 'Service Order', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'branch_id', label: 'Branch', readonly: true },
          { name: 'reason', type: 'text', label: 'Reported', readonly: true },
          { name: 'flagged_by_id', label: 'Flagged By', readonly: true },
          { name: 'flagged_at', label: 'Flagged At', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'cleared_by_id', label: 'Cleared By', readonly: true },
          { name: 'cleared_at', label: 'Cleared At', readonly: true },
          { name: 'clear_reason', type: 'text', label: 'Clearance Reason', readonly: true }
        ] }
    ]
  },

  'M17-form-merge': {
    kind: 'model_form',
    model: 'fix.device.merge',
    title: 'Merge Lineage',
    back: 'M17-merges',
    create: false, pick: 'A merge is written by an approved identity resolution: open one from Merge Lineage & Reversal.',
    status: { field: 'state', labels: { merged: 'Merged', reversed: 'Reversed' } },
    sections: [
      { title: 'Lineage', note: 'Written by the approved merge: both devices, the approver and the rows re-pointed. Reverse Merge (Quality Manager) moves those rows back inside the window.',
        fields: [
          { name: 'identity_id', label: 'Resolution', readonly: true },
          { name: 'survivor_id', label: 'Surviving Device', readonly: true },
          { name: 'merged_id', label: 'Merged Device', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'merged_at', label: 'Merged At', readonly: true },
          { name: 'reversible_until', label: 'Reversible Until', readonly: true },
          { name: 'rows_repointed', label: 'Rows Re-pointed', readonly: true },
          { name: 'reversed_by_id', label: 'Reversed By', readonly: true },
          { name: 'reversal_reason', type: 'text', label: 'Reversal Reason', readonly: true }
        ] }
    ]
  },

  'M17-form-identifier': {
    kind: 'model_form',
    model: 'fix.device.identifier',
    title: 'Identifier History',
    back: 'M17-idhistory',
    create: false, pick: 'Identifier history is written by registration, capture and correction: open one from Identifier History & NEIR.',
    sections: [
      { title: 'Identifier', note: 'Written by registration, capture and correction; never edited. A Branch Manager records the NEIR result of an IMEI with its reference.',
        fields: [
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'identifier_type', label: 'Type', readonly: true },
          { name: 'value', label: 'Value', readonly: true },
          { name: 'source', label: 'Source', readonly: true },
          { name: 'captured_by_id', label: 'Captured By', readonly: true },
          { name: 'captured_at', label: 'Captured At', readonly: true },
          { name: 'is_current', label: 'Current', readonly: true },
          { name: 'supersede_reason', label: 'Correction Reason', readonly: true },
          { name: 'neir_status', label: 'NEIR Status', readonly: true },
          { name: 'neir_reference', label: 'NEIR Reference', readonly: true }
        ] }
    ]
  },

  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M17-form-warranty': {
    kind: 'model_form',
    model: 'fix.warranty',
    title: "Device Warranty",
    back: 'M17-wty',
    sections: [
      { title: "Device Warranty", note: "Born pending. Upload the receipt or warranty card below or choose one already filed, save, then press Request Verification on the warranty list; a Warranty Officer who did not register it verifies it from the approvals inbox. The end date cannot precede the start; a daily job marks ended cover expired and announces cover about to end.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'device_id', required: true, label: "Device" },
          { name: 'warranty_type', required: true, label: "Warranty Type" },
          { name: 'start_date', required: true, label: "Start Date" },
          { name: 'end_date', required: true, label: "End Date" },
          // BRU-AST-16: how the dates were established; a date defaulted from
          // manufacture is flagged and is not verified on its own
          { name: 'derivation_basis', required: true, label: "Dates Derived From" },
          { name: 'basis_flag', label: "Basis Flag", readonly: true },
          { name: 'status', label: "Status", readonly: true },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'coverage_details', type: 'text', label: "Coverage Details" }
        ] },
      { title: "Proof of Purchase", note: "A purchase receipt or warranty card. A request for verification with no proof is refused.",
        fields: [
          { name: 'proof_file', type: 'file', label: "Upload Proof" },
          { name: 'proof_filename', label: "Proof File Name" },
          { name: 'proof_document_id', label: "Proof Document" }
        ] }
    ]
  },


  /* ===== M17 capture audit (2026-11-13): the captures pages 3, 8 and 9 lacked ===== */

  // Ownership & Custody: a transfer is recorded in one step. The device is
  // picked, the transfer filled, and the governed Transfer Ownership runs with
  // what was entered (Device Registry Agent, reason and evidence required).
  'M17-form-transfer-record': {
    kind: 'model_form',
    model: 'fix.device',
    title: 'Ownership Transfer',
    newLabel: 'Record an Ownership Transfer',
    back: 'M17-ownership',
    pickRecord: {
      label: 'Step 1 of 2: choose the device changing owner',
      note: 'Registered devices. A lost, scrapped, provisional or NEIR-blocked device is not transferred.',
      search: 'Search serial, IMEI or owner',
      choose: 'Transfer this device',
      cols: ['name', 'serial_number', 'imei_1', 'device_model_id', 'owner_id', 'state'],
      domain: [['state', 'not in', ['lost', 'scrapped', 'provisional']]],
      empty: 'No device can change owner: none is registered, or every one is lost, scrapped or provisional.'
    },
    saveAction: {
      method: 'action_transfer_ownership', label: 'Record Transfer',
      done: 'Ownership transferred: the old owner stays in the ownership history',
      kwargs: {
        new_owner_id: 'transfer_to_partner_id', transfer_type: 'transfer_type_pending',
        reason: 'transfer_reason', evidence_document_id: 'transfer_evidence_document_id',
        effective_date: 'transfer_effective_date',
        evidence_file: 'transfer_evidence_file', evidence_filename: 'transfer_evidence_filename'
      }
    },
    sections: [
      { title: 'Step 2 of 2: New Owner, Reason & Evidence (FR-AST-017/018)',
        note: 'Needs the Device Registry Agent role. The evidence is a sale receipt, deed or signed hand-over: upload it here or choose one already filed on this device; each transfer needs its own. The system records the evidence; it does not ask the new owner to accept. A technician never re-owns a device in their own custody.',
        fields: [
          { name: 'name', label: 'Device', readonly: true },
          { name: 'owner_id', label: 'Current Owner', readonly: true },
          { name: 'transfer_to_partner_id', required: true, label: 'Transfer To', readonly: true },
          { name: 'transfer_type_pending', required: true, label: 'Transfer Type', readonly: true },
          { name: 'transfer_reason', required: true, label: 'Transfer Reason', readonly: true },
          { name: 'transfer_effective_date', label: 'Effective On (default today)', readonly: true },
          { name: 'transfer_evidence_file', type: 'file', label: 'Upload Transfer Evidence', readonly: true },
          { name: 'transfer_evidence_filename', label: 'Evidence File Name', readonly: true },
          { name: 'transfer_evidence_document_id', label: 'Or Choose Filed Evidence', readonly: true }
        ] }
    ]
  },

  // FR-AST-023 / BRU-AST-09: anyone may raise the flag; a Branch Manager who
  // did not raise it clears it on the Asset Register.
  'M17-form-lost': {
    kind: 'model_form',
    model: 'fix.device',
    title: 'Report Lost / Stolen',
    newLabel: 'Report a Device Lost / Stolen',
    back: 'M17-holds',
    pickRecord: {
      label: 'Step 1 of 2: choose the device reported lost or stolen',
      note: 'Devices not already flagged or scrapped.',
      search: 'Search serial, IMEI or owner',
      choose: 'Report this device',
      cols: ['name', 'serial_number', 'imei_1', 'owner_id', 'state'],
      domain: [['state', 'not in', ['lost', 'scrapped']]],
      empty: 'Every device is already flagged lost or scrapped.'
    },
    saveAction: {
      method: 'action_mark_lost', label: 'Flag Lost / Stolen',
      done: 'Flagged: its open service orders are on hold until a Branch Manager clears it',
      kwargs: { reason: 'lost_reason', flag_type: 'lost_flag_type_pending', police_ref: 'lost_police_ref_pending' }
    },
    sections: [
      { title: 'Step 2 of 2: How It Was Reported',
        note: 'The flag holds every open service order of the device and blocks any release or transfer. It is recorded in the custody chain with who raised it. Only a Branch Manager who did not raise it clears it (Asset Register, Clear Lost Flag).',
        fields: [
          { name: 'name', label: 'Device', readonly: true },
          { name: 'owner_id', label: 'Owner', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'lost_reason', required: true, label: 'How Was the Loss or Theft Reported?', readonly: true },
          { name: 'lost_flag_type_pending', label: 'Lost or Stolen (default Lost)', readonly: true },
          { name: 'lost_police_ref_pending', label: 'GD / Police Report No. (required for Stolen)', readonly: true }
        ] }
    ]
  },

  // FR-AST-039 / BRU-AST-18 / AUT-AST-11: the estate file. Saving validates it.
  'M17-bulk-loads': { kind: 'model_list', model: 'fix.device.bulk.load', stateField: 'state',
    note: 'An uploaded estate file is checked at once, row by row, against the device catalogue, the registry and the rules a single registration meets. Commit as a Set (Device Registry Agent) registers every row or none.',
    cols: ['name', 'estate_id', 'client_id', 'upload_filename', 'line_count', 'new_count', 'place_count', 'error_count', 'state', 'committed_by_id'],
    actions: [
      { m: 'action_validate', l: 'Validate Again' },
      { m: 'action_commit', l: 'Commit as a Set (Device Registry Agent)' }
    ] },
  'M17-bulk-lines': { kind: 'model_list', create: false, model: 'fix.device.bulk.line', stateField: 'status',
    empty: 'No lines. Lines are written when an estate file is uploaded and validated (Bulk Estate Upload).',
    cols: ['load_id', 'row_no', 'serial_number', 'imei_1', 'model_ref', 'device_model_id', 'status', 'message', 'device_id'] },
  'M17-form-bulk': {
    kind: 'model_form',
    model: 'fix.device.bulk.load',
    title: 'Bulk Estate Upload',
    back: 'M17-bulk-loads',
    status: { field: 'state', labels: {
      draft: 'Uploaded', validated: 'Validated: Ready to Commit', rejected: 'Rejected: See the Lines', committed: 'Committed' } },
    sections: [
      { title: 'Estate & File',
        note: 'A CSV or Excel file with a header row: Model (name or model code from the catalogue) and Serial Number and/or IMEI 1; optional IMEI 2, MAC Address, Legacy Reference, Purchase Date (YYYY-MM-DD). Every device is registered to the estate\x27s client. Saving checks the file; the rejected rows and why are on Bulk Registration Lines. Fix the file and upload it again until nothing is rejected, then Commit as a Set.',
        fields: [
          { name: 'estate_id', required: true, label: 'Corporate Estate' },
          { name: 'branch_id', label: 'Registered At' },
          // the engine's default picker offers only PDF/images/Word
          { name: 'upload_file', type: 'file', accept: '.csv,.xlsx', label: 'Estate File (CSV or Excel)' },
          { name: 'upload_filename', label: 'File Name' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] },
      { title: 'Result',
        note: 'Written by the validation and the commit.',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'client_id', label: 'Client', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'line_count', label: 'Rows', readonly: true },
          { name: 'new_count', label: 'New Devices', readonly: true },
          { name: 'place_count', label: 'Existing Devices Joining', readonly: true },
          { name: 'error_count', label: 'Rejected Rows', readonly: true },
          { name: 'validated_by_id', label: 'Validated By', readonly: true },
          { name: 'committed_by_id', label: 'Committed By', readonly: true },
          { name: 'committed_on', label: 'Committed On', readonly: true }
        ] }
    ]
  },
  'M17-form-bulk-line': {
    kind: 'model_form',
    model: 'fix.device.bulk.line',
    title: 'Bulk Registration Line',
    back: 'M17-bulk-lines',
    create: false, pick: 'Lines are written by validating an estate file: open one from Bulk Registration Lines.',
    status: { field: 'status' },
    sections: [
      { title: 'Row', note: 'One row of the uploaded file and what the commit does with it.',
        fields: [
          { name: 'load_id', label: 'Bulk Registration', readonly: true },
          { name: 'row_no', label: 'File Row', readonly: true },
          { name: 'serial_number', label: 'Serial Number', readonly: true },
          { name: 'imei_1', label: 'IMEI 1', readonly: true },
          { name: 'imei_2', label: 'IMEI 2', readonly: true },
          { name: 'mac_address', label: 'MAC Address', readonly: true },
          { name: 'legacy_reference', label: 'Legacy Reference', readonly: true },
          { name: 'model_ref', label: 'Model in File', readonly: true },
          { name: 'device_model_id', label: 'Catalogue Model', readonly: true },
          { name: 'status', label: 'Outcome', readonly: true },
          { name: 'message', label: 'Why', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true }
        ] }
    ]
  },

  /* ===== M17 capture pass 2 (2026-11-19) ===== */

  // p1 FR-AST-008: the QR asset tag. A new label on a labelled device replaces
  // the old one, which stays on record with the reason.
  'M17-labels': { kind: 'model_list', model: 'fix.device.label', stateField: 'state',
    note: 'One row per tag applied. A damaged or lost tag is replaced by applying a new label; the old one stays here as Replaced.',
    cols: ['name', 'device_id', 'label_type', 'applied_by_id', 'applied_on', 'replaces_label_id', 'replace_reason', 'state'] },
  'M17-form-label': {
    kind: 'model_form',
    model: 'fix.device.label',
    title: 'Asset Label',
    back: 'M17-labels',
    status: { field: 'state', labels: { active: 'Active', replaced: 'Replaced' } },
    sections: [
      { title: 'Label', note: 'The code is issued on save and printed on the tag; the tag code then finds the device anywhere a serial or IMEI does. If the device already carries a tag, say why it is replaced.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'label_type', required: true, label: 'Label Type' },
          { name: 'applied_by_id', required: true, label: 'Labelling Technician' },
          { name: 'applied_on', required: true, label: 'Applied On' },
          { name: 'replace_reason', label: 'Why the Old Tag Is Replaced' },
          { name: 'name', label: 'Label Code', readonly: true },
          { name: 'replaces_label_id', label: 'Replaces Label', readonly: true },
          { name: 'printed_at', label: 'Printed At', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] }
    ]
  },

  // p1 FR-AST-002/010: identifiers beyond serial and IMEI. A value already on
  // another device is still recorded; both go on the stewardship worklist.
  'M17-form-identifier-add': {
    kind: 'model_form',
    model: 'fix.device',
    title: 'Add Identifier',
    newLabel: 'Add an Identifier to a Device',
    back: 'M17-idhistory',
    pickRecord: {
      label: 'Step 1 of 2: choose the device',
      note: 'The brand service tag, the customer\x27s own asset number or a part number. Serials and IMEIs are captured on the asset; the asset tag comes from a label.',
      search: 'Search serial, IMEI, tag or owner',
      choose: 'Add to this device',
      cols: ['name', 'serial_number', 'imei_1', 'asset_tag', 'owner_id', 'state'],
      domain: [['state', '!=', 'scrapped']],
      empty: 'No device to add an identifier to.'
    },
    saveAction: {
      method: 'action_add_identifier', label: 'Record Identifier',
      done: 'Identifier recorded in the identifier history',
      kwargs: { identifier_type: 'extra_identifier_type', value: 'extra_identifier_value' }
    },
    sections: [
      { title: 'Step 2 of 2: Identifier',
        note: 'The value is kept with who captured it and when. If the same value of the same type is current on another device, both devices go on the Stewardship Worklist as an identifier conflict.',
        fields: [
          { name: 'name', label: 'Device', readonly: true },
          { name: 'extra_identifier_type', required: true, label: 'Identifier Type', readonly: true },
          { name: 'extra_identifier_value', required: true, label: 'Identifier Value', readonly: true }
        ] }
    ]
  },

  // p2 FR-AST-015 / BRU-AST-08: what came in with the device. A device is not
  // issued back to its customer while an accessory is still held.
  'M17-accessories': { kind: 'model_list', model: 'fix.device.accessory', stateField: 'state',
    note: 'Every accessory received with a device is held until it is handed back or recorded missing. Issued to Customer is refused while one is still held.',
    cols: ['name', 'device_id', 'intake_reference', 'accessory_type', 'description', 'quantity', 'received_on', 'state', 'returned_on', 'discrepancy_note'],
    actions: [
      { m: 'action_return', l: 'Handed Back' },
      { m: 'action_report_missing', l: 'Missing at Return', ask: 'What is missing or different, and what was the customer told?', kwarg: 'reason' }
    ] },
  'M17-form-accessory': {
    kind: 'model_form',
    model: 'fix.device.accessory',
    title: 'Accessory Received',
    back: 'M17-accessories',
    status: { field: 'state', labels: { held: 'Held', returned: 'Returned', missing: 'Missing at Return' } },
    sections: [
      { title: 'Accessory', note: 'One row per accessory (charger, battery, bag…) received with the device. What was received is not edited afterwards; it is handed back or recorded missing on the Accessory Register.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'intake_reference', label: 'Intake / Job Reference' },
          { name: 'accessory_type', required: true, label: 'Accessory' },
          { name: 'description', label: 'Description' },
          { name: 'quantity', required: true, label: 'Quantity' },
          { name: 'received_on', required: true, label: 'Received On' },
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'received_by_id', label: 'Received By', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'returned_on', label: 'Returned On', readonly: true },
          { name: 'discrepancy_note', label: 'Discrepancy', readonly: true }
        ] }
    ]
  },

  // p2 FR-AST-012: the unit's actual specification and its history.
  'M17-configs': { kind: 'model_list', model: 'fix.device.configuration',
    note: 'Where the unit differs from its model. A new value of an attribute closes the previous one, which stays here with its end date.',
    cols: ['device_id', 'attribute', 'value', 'unit', 'source', 'effective_from', 'effective_to', 'is_current', 'recorded_by_id'] },
  'M17-form-config': {
    kind: 'model_form',
    model: 'fix.device.configuration',
    title: 'Configuration Record',
    back: 'M17-configs',
    sections: [
      { title: 'Configuration', note: 'Record the value as found (16 GB, 512 GB SSD, Windows 11). It is not edited afterwards: a later change is a new record from its own date.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'attribute', required: true, label: 'Attribute' },
          { name: 'value', required: true, label: 'Value' },
          { name: 'unit', label: 'Unit' },
          { name: 'source', required: true, label: 'Source' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'effective_to', label: 'Effective To', readonly: true },
          { name: 'is_current', label: 'Current', readonly: true }
        ] }
    ]
  },

  // p3 FR-AST-022 / BRU-AST-10/11: one population per device, changed only by
  // a reason-coded transaction.
  'M17-populations': { kind: 'model_list', model: 'fix.device.population.change',
    note: 'Every change of a device\x27s population, with its reason. Rental-pool or refurbishment stock becomes customer-owned only with the ownership transfer that sold or gave it.',
    cols: ['name', 'device_id', 'from_population', 'to_population', 'reason_code', 'ownership_id', 'state', 'recorded_by_id', 'approved_by_id', 'recorded_at'],
    // A07 ERP audit M17-17: a requested change applies when an Operations
    // Director (R05) who did not request it approves it.
    stateField: 'state',
    actions: [
      { m: 'action_approve', l: 'Approve (Operations Director)' },
      { m: 'action_reject', l: 'Reject (Operations Director)', ask: 'Why is the change rejected?', kwarg: 'reason' }
    ] },
  'M17-form-population': {
    kind: 'model_form',
    model: 'fix.device.population.change',
    title: 'Population Change',
    back: 'M17-populations',
    sections: [
      { title: 'Population Change', note: 'Device Registry Agent. The population says which modules may act on the device (rental, refurbishment, marketplace, e-waste). A change is permanent; a wrong one is put right by another change with the reason Correction.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'to_population', required: true, label: 'New Population' },
          { name: 'reason_code', required: true, label: 'Reason' },
          { name: 'ownership_id', label: 'Ownership Transfer (stock sold to a customer)' },
          { name: 'notes', label: 'Notes' },
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'from_population', label: 'Previous Population', readonly: true },
          { name: 'recorded_by_id', label: 'Recorded By', readonly: true },
          { name: 'recorded_at', label: 'Recorded At', readonly: true }
        ] }
    ]
  },

  // p8 FR-AST-038: customer > site > department > assigned user.
  'M17-estate-nodes': { kind: 'model_list', model: 'fix.device.estate.node',
    cols: ['complete_name', 'estate_id', 'client_id', 'node_type', 'contact_id', 'cost_centre', 'device_count', 'active'] },
  'M17-form-estate-node': {
    kind: 'model_form',
    model: 'fix.device.estate.node',
    title: 'Estate Node',
    back: 'M17-estate-nodes',
    sections: [
      { title: 'Site, Department or User', note: 'A site is the top of the estate; a department sits within a site; an assigned user sits within a department or site and names the client\x27s employee who holds the devices.',
        fields: [
          { name: 'estate_id', required: true, label: 'Estate' },
          { name: 'node_type', required: true, label: 'Level' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'parent_id', label: 'Within' },
          { name: 'contact_id', label: 'Contact / Assigned User' },
          { name: 'address', label: 'Address' },
          { name: 'cost_centre', label: 'Cost Centre' },
          { name: 'active', label: 'Active' },
          { name: 'complete_name', label: 'Full Path', readonly: true },
          { name: 'device_count', label: 'Devices Placed', readonly: true }
        ] }
    ]
  },

  // p8 FR-AST-038: placing (or moving) a device, dated. The previous placement
  // closes on the same date and stays on record.
  'M17-placements': { kind: 'model_list', model: 'fix.device.estate.placement',
    note: 'Where each device has been in its client\x27s estate. A change of estate on the asset itself is recorded here too.',
    cols: ['name', 'device_id', 'estate_id', 'node_id', 'placed_from', 'placed_to', 'is_current', 'move_reason', 'moved_by_id'] },
  'M17-form-estate-placement': {
    kind: 'model_form',
    model: 'fix.device.estate.placement',
    title: 'Estate Assignment',
    newLabel: 'Place or Move a Device in an Estate',
    back: 'M17-placements',
    sections: [
      { title: 'Placement', note: 'Only a device the estate\x27s client (or one of its contacts) owns is placed. An estate organised into sites, departments and users takes the device at one of its nodes. For a whole estate at once, use Bulk Estate Upload.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'estate_id', required: true, label: 'Corporate Estate' },
          { name: 'node_id', label: 'Site / Department / User' },
          { name: 'placed_from', required: true, label: 'Placed From' },
          { name: 'move_reason', required: true, label: 'Reason for the Move' },
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'placed_to', label: 'Placed To', readonly: true },
          { name: 'is_current', label: 'Current', readonly: true }
        ] }
    ]
  },

  // p10 FR-AST-048 / BRU-AST-19: the route, its basis, the customer's
  // instruction and an approver who did not raise it.
  'M17-eol': { kind: 'model_list', model: 'fix.device.eol.decision', stateField: 'state',
    note: 'An approved decision makes the device obsolete and hands it on: refurbishment (M14) or e-waste (M18). A Branch Manager who neither raised nor requested it decides.',
    cols: ['name', 'device_id', 'route', 'customer_instruction', 'state', 'requested_by_id', 'decided_by_id', 'decided_at'],
    actions: [
      { m: 'action_request', l: 'Request Approval' },
      { m: 'action_approve', l: 'Approve Route (Branch Manager)' },
      { m: 'action_reject', l: 'Reject (Branch Manager)', ask: 'Why is the route rejected?', kwarg: 'reason' }
    ] },
  'M17-form-eol': {
    kind: 'model_form',
    model: 'fix.device.eol.decision',
    title: 'End-of-Life Decision',
    back: 'M17-eol',
    status: { field: 'state', labels: { draft: 'Draft', requested: 'Awaiting Approval', approved: 'Approved: Routed', rejected: 'Rejected' } },
    sections: [
      { title: 'Decision', note: 'For a customer-owned device the customer\x27s instruction is required and must match the route. Save, then Request Approval on the list.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'route', required: true, label: 'Route' },
          { name: 'basis', type: 'text', required: true, label: 'Basis for the Decision' },
          { name: 'customer_instruction', label: 'Customer Instruction' },
          { name: 'instruction_reference', label: 'Instruction Reference' },
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'population', label: 'Population', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decision_note', label: 'Decision Note', readonly: true }
        ] }
    ]
  },

  // p11 FR-AST-051 / BRU-AST-22: the stewardship worklist. The daily sweep
  // adds provisional identities left unresolved and escalates old issues.
  'M17-quality-issues': { kind: 'model_list', model: 'fix.device.quality.issue', stateField: 'state',
    note: 'Provisional identities, probable duplicates, identifier conflicts and incomplete records, by branch. A daily check adds provisional devices left unresolved and escalates issues left open too long.',
    cols: ['name', 'device_id', 'issue_type', 'severity', 'assigned_branch_id', 'assigned_to_id', 'age_days', 'escalated', 'state'],
    actions: [
      { m: 'action_assign', l: 'Assign (Branch Manager)', ask: 'Login of the user who works the issue?', kwarg: 'user_id' },
      { m: 'action_start', l: 'Start Work' },
      { m: 'action_resolve', l: 'Resolve (conflict / duplicate: Quality Manager)', ask: 'How was the record put right?', kwarg: 'resolution' }
    ] },
  'M17-form-quality-issue': {
    kind: 'model_form',
    model: 'fix.device.quality.issue',
    title: 'Stewardship Issue',
    back: 'M17-quality-issues',
    status: { field: 'state', labels: { open: 'Open', in_progress: 'In Progress', resolved: 'Resolved' } },
    sections: [
      { title: 'Issue', note: 'The assignee or a Branch Manager works it. A provisional-identity issue resolves only once the identity is confirmed.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'issue_type', required: true, label: 'Issue' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'description', type: 'text', required: true, label: 'What Is Wrong' },
          { name: 'assigned_branch_id', label: 'Assigned Branch' },
          { name: 'assigned_to_id', label: 'Assigned To (Assign on the list)', readonly: true },
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'escalated', label: 'Escalated', readonly: true },
          { name: 'resolution', type: 'text', label: 'Resolution', readonly: true },
          { name: 'resolved_by_id', label: 'Resolved By', readonly: true }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M17-device-part-compatibility': { kind: 'model_list', model: 'fix.device.part.compatibility',
    cols: ['active', 'company_id', 'operating_unit_id', 'model_id', 'part_number', 'part_name', 'category'] },


};

export const REPORT_ROUTES = {
  'M17:Installed Base by Brand/Model': 'M17-rpt-base',
  'M17:Repeat-Fault Pareto': 'M17-rpt-repeat',
  'M17:Estate Coverage by Client': 'M17-rpt-estate',
  'M17:Custody Exceptions': 'M17-rpt-custody',
  'M17:Data Quality Scorecard': 'M17-rpt-quality'
};

export const FORM_MODELS = {
  'M17:Asset (5 identifiers)': 'fix.device',
  'M17:Corporate Estate': 'fix.device.estate',
  'M17:Estate Assignment': 'fix.device.estate.placement',
  'M17:Ownership Transfer': 'fix.device',
  'M17:Custody Event': 'fix.device.custody',
  'M17:Report Lost / Stolen': 'fix.device',
  'M17:Condition Grading': 'fix.device.condition',
  'M17:PM Plan': 'fix.device.pm',
  'M17:Installed Component': 'fix.device.component',
  'M17:Part Compatibility': 'fix.device.part.compatibility',
  'M17:Identity Resolution': 'fix.device.identity',
  'M17:Bulk Estate Upload': 'fix.device.bulk.load',
  'M17:Asset Label': 'fix.device.label',
  'M17:Add Identifier': 'fix.device',
  'M17:Accessory Received': 'fix.device.accessory',
  'M17:Configuration Record': 'fix.device.configuration',
  'M17:Population Change': 'fix.device.population.change',
  'M17:Estate Node': 'fix.device.estate.node',
  'M17:End-of-Life Decision': 'fix.device.eol.decision',
  'M17:Stewardship Issue': 'fix.device.quality.issue'
};

export const FORM_CHIPS = {
  'M17:Device Warranty': 'M17-form-warranty',
  'M17:Asset (5 identifiers)': 'M17-form-asset',
  'M17:Corporate Estate': 'M17-form-estate',
  // M17 pass 2: a placement is a dated record at an estate node (FR-AST-038)
  'M17:Estate Assignment': 'M17-form-estate-placement',
  // the chip records a transfer; past transfers open M17-form-transfer
  'M17:Ownership Transfer': 'M17-form-transfer-record',
  'M17:Custody Event': 'M17-form-custody',
  'M17:Report Lost / Stolen': 'M17-form-lost',
  'M17:Condition Grading': 'M17-form-condition',
  'M17:PM Plan': 'M17-form-pm',
  'M17:Installed Component': 'M17-form-component',
  'M17:Part Compatibility': 'M17-form-compat',
  'M17:Identity Resolution': 'M17-form-identity',
  'M17:Bulk Estate Upload': 'M17-form-bulk',
  'M17:Asset Label': 'M17-form-label',
  'M17:Add Identifier': 'M17-form-identifier-add',
  'M17:Accessory Received': 'M17-form-accessory',
  'M17:Configuration Record': 'M17-form-config',
  'M17:Population Change': 'M17-form-population',
  'M17:Estate Node': 'M17-form-estate-node',
  'M17:End-of-Life Decision': 'M17-form-eol',
  'M17:Stewardship Issue': 'M17-form-quality-issue',
  'M17:__by_model__': {
    'fix.device.part.compatibility': 'M17-form-compat',

    'fix.warranty': 'M17-form-warranty',
    'fix.device': 'M17-form-asset',
    'fix.device.estate': 'M17-form-estate',
    'fix.device.ownership': 'M17-form-transfer',
    'fix.device.condition': 'M17-form-condition',
    'fix.device.pm': 'M17-form-pm',
    'fix.device.identity': 'M17-form-identity',
    'fix.device.custody': 'M17-form-custody',
    'fix.device.component': 'M17-form-component',
    'fix.device.merge': 'M17-form-merge',
    'fix.device.identifier': 'M17-form-identifier',
    'fix.service.order.device.hold': 'M17-form-hold',
    'fix.device.bulk.load': 'M17-form-bulk',
    'fix.device.bulk.line': 'M17-form-bulk-line',
    'fix.device.label': 'M17-form-label',
    'fix.device.accessory': 'M17-form-accessory',
    'fix.device.configuration': 'M17-form-config',
    'fix.device.population.change': 'M17-form-population',
    'fix.device.estate.node': 'M17-form-estate-node',
    'fix.device.estate.placement': 'M17-form-estate-placement',
    'fix.device.eol.decision': 'M17-form-eol',
    'fix.device.quality.issue': 'M17-form-quality-issue'
  },
  'M17:__by_screen__': {
    'M17-device-part-compatibility': 'M17-form-compat',

    'M17-wty': 'M17-form-warranty',
    'M17-assets': 'M17-form-asset',
    'M17-asset': 'M17-form-asset',
    'M17-merge': 'M17-form-identity',
    'M17-custody': 'M17-form-custody',
    'M17-ownership': 'M17-form-transfer',
    'M17-estates': 'M17-form-estate',
    'M17-pm': 'M17-form-pm',
    'M17-genealogy': 'M17-form-component',
    'M17-components': 'M17-form-component',
    'M17-conditions': 'M17-form-condition',
    'M17-merges': 'M17-form-merge',
    'M17-idhistory': 'M17-form-identifier',
    'M17-holds': 'M17-form-hold',
    'M17-bulk-loads': 'M17-form-bulk',
    'M17-bulk-lines': 'M17-form-bulk-line',
    'M17-labels': 'M17-form-label',
    'M17-accessories': 'M17-form-accessory',
    'M17-configs': 'M17-form-config',
    'M17-populations': 'M17-form-population',
    'M17-estate-nodes': 'M17-form-estate-node',
    'M17-placements': 'M17-form-estate-placement',
    'M17-eol': 'M17-form-eol',
    'M17-quality-issues': 'M17-form-quality-issue'
  }
};

export const CREATE = {
  M17: { screen: 'M17-form-asset', model: 'fix.device', label: 'Asset' }
};
