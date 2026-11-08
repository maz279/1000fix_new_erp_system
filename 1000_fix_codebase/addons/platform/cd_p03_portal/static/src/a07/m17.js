/** @odoo-module **/
/* A07 · Assets & Facilities — M17 Device & Asset Registry (v2 rebuild).
 * Registry-faithful: 5 groups / 14 screens / 5 reports / 4 forms / freg 96.
 * The device master, warranty, ownership and history existed; estates, PM,
 * condition, identity resolution, custody and installed components are new. */

export const MODULE = {
  area: 'A07', code: 'M17', en: 'Device & Asset Registry', title: 'M17 · Device & Asset Registry',
  bn: 'ডিভাইস ও অ্যাসেট রেজিস্ট্রি', icon: '📱',
  desc: 'Asset register and record with five identifiers, Asset 360, identity resolution and merge, service history, parts genealogy, repeat-fault detection, custody chain, ownership transfers with evidence, identifier history with NEIR status, merge lineage, corporate estates, a bulk-registration readiness report (no bulk load yet), warranty dates and PM plans.',
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
      { id: 'M17-360', en: 'Asset 360', bn: 'অ্যাসেট ৩৬০', t: 'g' },
      { id: 'M17-identifiers', en: 'Multi-Identifier Model', bn: 'মাল্টি-আইডেন্টিফায়ার', t: 'g' },
      { id: 'M17-merge', en: 'Identity Resolution & Merge', bn: 'আইডেন্টিটি রেজলিউশন', t: 'g' },
      { id: 'M17-merges', en: 'Merge Lineage & Reversal', bn: 'মার্জ লিনিয়েজ', t: 'g' },
      { id: 'M17-idhistory', en: 'Identifier History & NEIR', bn: 'আইডেন্টিফায়ার ইতিহাস ও NEIR', t: 'g' }
    ]},
    { en: 'History', screens: [
      { id: 'M17-history', en: 'Service History', bn: 'সেবা ইতিহাস', t: 'g' },
      { id: 'M17-genealogy', en: 'Parts Genealogy', bn: 'পার্টস বংশতালিকা', t: 'g' },
      { id: 'M17-rework', en: 'Repeat-Fault Detection', bn: 'পুনরাবৃত্তি ত্রুটি', t: 'g' },
      { id: 'M17-components', en: 'Installed Components', bn: 'ইনস্টলড কম্পোনেন্ট', t: 'g' }
    ]},
    { en: 'Custody', screens: [
      { id: 'M17-custody', en: 'Custody State & Chain', bn: 'কাস্টডি চেইন', t: 'g' },
      { id: 'M17-ownership', en: 'Ownership & Transfers', bn: 'মালিকানা হস্তান্তর', t: 'g' },
      { id: 'M17-holds', en: 'Lost / Stolen Holds', bn: 'হারানো / চুরি হোল্ড', t: 'g' }
    ]},
    { en: 'Corporate Estates', screens: [
      { id: 'M17-estates', en: 'Estates (Site/Dept/User)', bn: 'কর্পোরেট এস্টেট', t: 'g' },
      { id: 'M17-bulk', en: 'Bulk Registration', bn: 'বাল্ক রেজিস্ট্রেশন', t: 'g' }
    ]},
    { en: 'Coverage', screens: [
      { id: 'M17-wty', en: 'Warranty Dates & Priority', bn: 'ওয়ারেন্টি তারিখ', t: 'g' },
      { id: 'M17-conditions', en: 'Condition Grades', bn: 'কন্ডিশন গ্রেড', t: 'g' },
      { id: 'M17-pm', en: 'PM Plans', bn: 'পিএম প্ল্যান', t: 'g' }
    ]}
  ],
  reports: ['Installed Base by Brand/Model', 'Repeat-Fault Pareto', 'Estate Coverage by Client', 'Custody Exceptions', 'Data Quality Scorecard'],
  forms: ['Asset (6 identifiers)', 'Estate Assignment', 'Ownership Transfer', 'Condition Grading'],
  cross: ['M01 every order links asset', 'M09 warranty evidence', 'M05 monitored assets', 'M48 telemetry streams', 'P01 customer devices'],
  freg: { src: 96, sub: [
    ['1', 'Identity & Resolution', 14, { model: 'fix.device', cols: ['name', 'serial_number', 'imei_1', 'mac_address', 'legacy_reference'], screens: ['M17-asset', 'M17-identifiers', 'M17-assets'] }],
    ['2', 'Configuration & Components', 8, { model: 'fix.device.component', cols: ['device_id', 'part_name', 'serial_no', 'installed_on', 'state'], screens: ['M17-components', 'M17-device-part-compatibility'] }],
    ['3', 'Ownership & Custody', 12, { model: 'fix.device.ownership', cols: ['device_id', 'from_partner_id', 'to_partner_id', 'transfer_type', 'transfer_date'], screens: ['M17-ownership', 'M17-custody'] }],
    ['4', 'Service History', 9, { model: 'fix.device.history', cols: ['date', 'device_id', 'event_type', 'description', 'technician_id'], screens: ['M17-history', 'M17-360'] }],
    ['5', 'Parts Genealogy', 7, { model: 'fix.device.component', cols: ['device_id', 'part_name', 'serial_no', 'source_ref', 'removed_on'], screens: ['M17-genealogy', 'M17-components'] }],
    ['6', 'Repeat-Fault Detection', 6, { model: 'fix.device.history', cols: ['device_id', 'date', 'event_type', 'service_order_id', 'description'], screens: ['M17-rework', 'M17-history'], domain: [['event_type', 'in', ['repair', 'service_order']]] }],
    ['7', 'Warranty Projection', 7, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'start_date', 'end_date', 'status'], screens: ['M17-wty'] }],
    ['8', 'Corporate Estates', 12, { model: 'fix.device.estate', cols: ['name', 'client_id', 'site', 'department', 'cost_centre'], screens: ['M17-estates'] }],
    ['9', 'Bulk Registration', 7, { model: 'fix.device', cols: ['name', 'serial_number', 'device_model_id', 'owner_id', 'estate_id'], screens: ['M17-bulk', 'M17-assets'] }],
    ['10', 'Condition & EOL Routing', 8, { model: 'fix.device.condition', cols: ['device_id', 'grade', 'functional_ok', 'battery_health_pct', 'graded_on'], screens: ['M17-conditions', 'M17-pm'] }],
    ['11', 'Data Quality', 6, { model: 'fix.device.identity', cols: ['name', 'primary_device_id', 'duplicate_device_id', 'match_score', 'state'], screens: ['M17-merge', 'M17-identifiers'] }]
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
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M17']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  'M17-assets': { kind: 'model_list', model: 'fix.device', stateField: 'state',
    cols: ['name', 'serial_number', 'device_model_id', 'owner_id', 'state', 'lifecycle_stage', 'neir_status', 'approval_state'],
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
      { m: 'action_set_vintage', l: 'Lifecycle: Vintage', ask: 'Basis for the decision?', kwarg: 'reason' },
      { m: 'action_return_to_active', l: 'Lifecycle: Back to Active (from Vintage)', ask: 'Basis for the decision?', kwarg: 'reason' },
      { m: 'action_set_end_of_support', l: 'Lifecycle: End of OEM Support', ask: 'Basis for the decision?', kwarg: 'reason' },
      { m: 'action_set_obsolete', l: 'Lifecycle: Obsolete (customer instruction required)', ask: 'Basis for the end-of-life decision?', kwarg: 'reason' },
      { m: 'action_request_approval', l: 'Request Scrap Approval (Quality Manager)', ask: 'Why should this device be scrapped?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M17-asset': { kind: 'model_list', model: 'fix.device',
    cols: ['serial_number', 'imei_1', 'imei_2', 'mac_address', 'legacy_reference', 'estate_id'] },
  'M17-360': { kind: 'table_report', module: 'M17', report: 'asset_360', title: 'Asset 360', period: false },
  'M17-identifiers': { kind: 'table_report', module: 'M17', report: 'identifiers', title: 'Multi-Identifier Model', period: false },
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
  'M17-history': { kind: 'model_list', create: false, model: 'fix.device.history', stateField: 'event_type',
    cols: ['date', 'device_id', 'event_type', 'description', 'technician_id'] },
  'M17-genealogy': { kind: 'table_report', module: 'M17', report: 'parts_genealogy', title: 'Parts Genealogy', period: false },
  'M17-rework': { kind: 'table_report', module: 'M17', report: 'repeat_fault', title: 'Repeat-Fault Detection', period: false },
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
    cols: ['device_id', 'from_partner_id', 'to_partner_id', 'transfer_type', 'transfer_date', 'reason', 'recorded_by_id', 'channel'] },
  // Written by the M17 lost/stolen flag and its clearance; nobody types a hold.
  'M17-holds': { kind: 'model_list', create: false, model: 'fix.service.order.device.hold', stateField: 'state',
    note: 'One row for each open service order of a device reported lost or stolen. While a hold is open the order cannot be handed over. A Branch Manager ends it by clearing the lost flag on the Asset Register.',
    cols: ['name', 'order_id', 'device_id', 'branch_id', 'reason', 'flagged_by_id', 'flagged_at', 'cleared_by_id', 'cleared_at', 'state'] },
  'M17-merges': { kind: 'model_list', create: false, model: 'fix.device.merge', stateField: 'state',
    cols: ['name', 'survivor_id', 'merged_id', 'approved_by_id', 'merged_at', 'reversible_until', 'rows_repointed', 'state'],
    actions: [{ m: 'action_reverse', l: 'Reverse Merge (Quality Manager, inside the window)', ask: 'Why is the merge reversed?', kwarg: 'reason' }] },
  'M17-idhistory': { kind: 'model_list', create: false, model: 'fix.device.identifier', stateField: 'neir_status',
    cols: ['device_id', 'identifier_type', 'value', 'source', 'captured_by_id', 'captured_at', 'is_current', 'neir_status', 'neir_reference'],
    // B4: NEIR results are recorded by a Branch Manager with the BTRC/operator reference.
    actions: [
      { m: 'action_neir_registered', l: 'NEIR: Registered', ask: 'NEIR / BTRC reference?', kwarg: 'reference' },
      { m: 'action_neir_deregistered', l: 'NEIR: De-registered', ask: 'NEIR / BTRC reference?', kwarg: 'reference' },
      { m: 'action_neir_blocked', l: 'NEIR: Blocked / Blacklisted', ask: 'NEIR / BTRC reference?', kwarg: 'reference' }
    ] },
  'M17-estates': { kind: 'model_list', model: 'fix.device.estate',
    cols: ['name', 'client_id', 'site', 'department', 'cost_centre', 'manager_id', 'active'] },
  'M17-bulk': { kind: 'table_report', module: 'M17', report: 'bulk_registration', title: 'Bulk Registration', period: false },
  'M17-conditions': { kind: 'model_list', model: 'fix.device.condition', stateField: 'state',
    cols: ['name', 'device_id', 'grade', 'functional_ok', 'battery_health_pct', 'graded_on', 'state'],
    actions: [{ m: 'action_confirm', l: 'Confirm Grade' }] },
  'M17-wty': { kind: 'model_list', model: 'fix.warranty', stateField: 'status',
    cols: ['device_id', 'warranty_type', 'start_date', 'end_date', 'status', 'verification_state', 'verification_blocker', 'approval_state'],
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
  'M17-rpt-base': { kind: 'table_report', module: 'M17', report: 'installed_base', title: 'Installed Base by Brand/Model', period: false },
  'M17-rpt-repeat': { kind: 'table_report', module: 'M17', report: 'repeat_fault', title: 'Repeat-Fault Pareto', period: false },
  'M17-rpt-estate': { kind: 'table_report', module: 'M17', report: 'estate_coverage', title: 'Estate Coverage by Client', period: false },
  'M17-rpt-custody': { kind: 'table_report', module: 'M17', report: 'custody_exceptions', title: 'Custody Exceptions', period: false },
  'M17-rpt-quality': { kind: 'table_report', module: 'M17', report: 'data_quality', title: 'Data Quality Scorecard', period: false },

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
          { name: 'branch_id', label: 'Registered At' },
          { name: 'purchase_date', label: 'Purchase Date' }
        ] },
      { tab: 'transfer', title: 'Ownership Transfer', note: 'Fill these, save, then press Transfer Ownership on the asset list (Device Registry Agent). The type, the reason and the evidence are required: a sale receipt, deed or signed hand-over, uploaded here or chosen from those already filed, and used for one transfer only. The system records the evidence; it does not ask the new owner to accept. They are cleared once the transfer is recorded. A lost, scrapped, provisional or NEIR-blocked device is not transferred.',
        fields: [
          { name: 'transfer_to_partner_id', label: 'Transfer To' },
          { name: 'transfer_type_pending', label: 'Transfer Type' },
          { name: 'transfer_reason', label: 'Transfer Reason' },
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
    title: 'Estate Assignment',
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
    back: 'M17-genealogy',
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
  'M17:Asset (6 identifiers)': 'fix.device',
  'M17:Estate Assignment': 'fix.device.estate',
  'M17:Ownership Transfer': 'fix.device.ownership',
  'M17:Condition Grading': 'fix.device.condition'
};

export const FORM_CHIPS = {
  'M17:Device Warranty': 'M17-form-warranty',
  'M17:Asset (6 identifiers)': 'M17-form-asset',
  'M17:Estate Assignment': 'M17-form-estate',
  'M17:Ownership Transfer': 'M17-assets',
  'M17:Condition Grading': 'M17-form-condition',
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
    'fix.service.order.device.hold': 'M17-form-hold'
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
    'M17-holds': 'M17-form-hold'
  }
};

export const CREATE = {
  M17: { screen: 'M17-form-asset', model: 'fix.device', label: 'Asset' }
};
