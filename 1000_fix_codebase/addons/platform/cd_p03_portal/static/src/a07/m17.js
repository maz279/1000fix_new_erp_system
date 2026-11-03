/** @odoo-module **/
/* A07 · Assets & Facilities — M17 Device & Asset Registry (v2 rebuild).
 * Registry-faithful: 5 groups / 14 screens / 5 reports / 4 forms / freg 96.
 * The device master, warranty, ownership and history existed; estates, PM,
 * condition, identity resolution, custody and installed components are new. */

export const MODULE = {
  area: 'A07', code: 'M17', en: 'Device & Asset Registry', title: 'M17 · Device & Asset Registry',
  bn: 'ডিভাইস ও অ্যাসেট রেজিস্ট্রি', icon: '📱',
  desc: 'Asset register and record with six identifiers, Asset 360, identity resolution and merge, service history, parts genealogy, repeat-fault detection, custody chain, ownership transfers, corporate estates, bulk registration, warranty dates and PM plans.',
  kpis: [
    { l: 'Active Devices', m: 'devices_active' },
    { l: 'Estates', m: 'estates' },
    { l: 'PM Due (30d)', m: 'pm_due_30d' },
    { l: 'Lost (open)', m: 'custody_open_lost' },
    { l: 'No Condition', m: 'without_condition' },
    { l: 'Active Warranties', m: 'warranty_active' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M17-device-part-compatibility', en: "Device Part Compatibility", bn: "Device Part Compatibility", t: 'g' }
    ]},
    { en: 'Registry', screens: [
      { id: 'M17-assets', en: 'Asset Register', bn: 'অ্যাসেট রেজিস্টার', t: 'g' },
      { id: 'M17-asset', en: 'Asset Record', bn: 'অ্যাসেট রেকর্ড', t: 'g' },
      { id: 'M17-360', en: 'Asset 360', bn: 'অ্যাসেট ৩৬০', t: 'g' },
      { id: 'M17-identifiers', en: 'Multi-Identifier Model', bn: 'মাল্টি-আইডেন্টিফায়ার', t: 'g' },
      { id: 'M17-merge', en: 'Identity Resolution & Merge', bn: 'আইডেন্টিটি রেজলিউশন', t: 'g' }
    ]},
    { en: 'History', screens: [
      { id: 'M17-history', en: 'Service History', bn: 'সেবা ইতিহাস', t: 'g' },
      { id: 'M17-genealogy', en: 'Parts Genealogy', bn: 'পার্টস বংশতালিকা', t: 'g' },
      { id: 'M17-rework', en: 'Repeat-Fault Detection', bn: 'পুনরাবৃত্তি ত্রুটি', t: 'g' },
      { id: 'M17-components', en: 'Installed Components', bn: 'ইনস্টলড কম্পোনেন্ট', t: 'g' }
    ]},
    { en: 'Custody', screens: [
      { id: 'M17-custody', en: 'Custody State & Chain', bn: 'কাস্টডি চেইন', t: 'g' },
      { id: 'M17-ownership', en: 'Ownership & Transfers', bn: 'মালিকানা হস্তান্তর', t: 'g' }
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

  'M17-assets': { kind: 'model_list', model: 'fix.device', stateField: 'state',
    cols: ['name', 'serial_number', 'device_model_id', 'owner_id', 'state', 'lifecycle_stage', 'approval_state'],
    // A07 audit M17-8: the state moves only through these. Someone other than
    // the flagger clears a lost flag; scrap is decided from the M63 approval
    // inbox by a Tier 2 holder who did not request it.
    actions: [
      { m: 'action_mark_lost', l: 'Flag Lost / Stolen', ask: 'How was the loss or theft reported?', kwarg: 'reason' },
      { m: 'action_clear_lost', l: 'Clear Lost Flag', ask: 'How was it recovered, or why is the report withdrawn?', kwarg: 'reason' },
      { m: 'action_request_approval', l: 'Request Scrap Approval (Tier 2)', ask: 'Why should this device be scrapped?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M17-asset': { kind: 'model_list', model: 'fix.device',
    cols: ['serial_number', 'imei_1', 'imei_2', 'mac_address', 'legacy_reference', 'estate_id'] },
  'M17-360': { kind: 'table_report', module: 'M17', report: 'asset_360', title: 'Asset 360', period: false },
  'M17-identifiers': { kind: 'table_report', module: 'M17', report: 'identifiers', title: 'Multi-Identifier Model', period: false },
  'M17-merge': { kind: 'model_list', model: 'fix.device.identity', stateField: 'state',
    cols: ['name', 'primary_device_id', 'duplicate_device_id', 'match_reason', 'match_score', 'state', 'approval_state'],
    // A07 audit M17-3: a Tier 2 holder who neither raised nor requested the
    // candidate merges it from the M63 approval inbox. Here it is only routed.
    actions: [
      { m: 'action_request_approval', l: 'Request Merge Approval (Tier 2)', ask: 'Why are these the same device? (required if owners or models differ)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_reject', l: 'Reject (not a duplicate)' }
    ] },
  'M17-history': { kind: 'model_list', create: false, model: 'fix.device.history', stateField: 'event_type',
    cols: ['date', 'device_id', 'event_type', 'description', 'technician_id'] },
  'M17-genealogy': { kind: 'table_report', module: 'M17', report: 'parts_genealogy', title: 'Parts Genealogy', period: false },
  'M17-rework': { kind: 'table_report', module: 'M17', report: 'repeat_fault', title: 'Repeat-Fault Detection', period: false },
  'M17-components': { kind: 'model_list', model: 'fix.device.component', stateField: 'state',
    cols: ['device_id', 'part_name', 'serial_no', 'installed_on', 'removed_on', 'state'],
    actions: [{ m: 'action_remove', l: 'Remove Component' }] },
  'M17-custody': { kind: 'model_list', model: 'fix.device.custody', stateField: 'event',
    cols: ['name', 'device_id', 'event', 'from_party_id', 'to_party_id', 'event_date'] },
  'M17-ownership': { kind: 'model_list', model: 'fix.device.ownership',
    cols: ['device_id', 'from_partner_id', 'to_partner_id', 'transfer_type', 'transfer_date'] },
  'M17-estates': { kind: 'model_list', model: 'fix.device.estate',
    cols: ['name', 'client_id', 'site', 'department', 'cost_centre', 'manager_id', 'active'] },
  'M17-bulk': { kind: 'table_report', module: 'M17', report: 'bulk_registration', title: 'Bulk Registration', period: false },
  'M17-conditions': { kind: 'model_list', model: 'fix.device.condition', stateField: 'state',
    cols: ['name', 'device_id', 'grade', 'functional_ok', 'battery_health_pct', 'graded_on', 'state'],
    actions: [{ m: 'action_confirm', l: 'Confirm Grade' }] },
  'M17-wty': { kind: 'model_list', model: 'fix.warranty', stateField: 'status',
    cols: ['device_id', 'warranty_type', 'start_date', 'end_date', 'status'] },
  'M17-pm': { kind: 'model_list', model: 'fix.device.pm', stateField: 'state',
    cols: ['name', 'device_id', 'plan_type', 'interval_months', 'last_done', 'next_due', 'state'],
    actions: [
      { m: 'action_complete', l: 'Mark Done' },
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
    title: 'Asset (6 identifiers)',
    back: 'M17-assets',
    status: { field: 'state', labels: {
      registered: 'Registered', in_service: 'In Service', repaired: 'Repaired',
      returned: 'Returned to Owner', transferred: 'Ownership Transferred',
      scrapped: 'Scrapped', lost: 'Lost/Stolen' } },
    sections: [
      { title: 'Identifiers', note: 'At least the serial is mandatory; IMEI-2 and MAC are optional for devices that have them.',
        fields: [
          { name: 'serial_number', required: true, label: 'Serial Number' },
          { name: 'imei_1', label: 'IMEI 1' },
          { name: 'imei_2', label: 'IMEI 2' },
          { name: 'mac_address', label: 'MAC Address' },
          { name: 'legacy_reference', label: 'Legacy Reference' },
          { name: 'device_model_id', required: true, label: 'Device Model' }
        ] },
      { title: 'Ownership & Estate', fields: [
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'estate_id', label: 'Corporate Estate' },
          { name: 'branch_id', label: 'Registered At' },
          { name: 'purchase_date', label: 'Purchase Date' },
          { name: 'lifecycle_stage', label: 'Lifecycle Stage' }
        ] },
      { title: 'Lifecycle', note: 'Changed only by Flag Lost, Clear Lost Flag, an ownership transfer or an approved scrap.',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'approval_state', label: 'Scrap Approval', readonly: true },
          { name: 'lost_reason', label: 'Lost / Stolen Report', readonly: true },
          { name: 'lost_flagged_by_id', label: 'Flagged Lost By', readonly: true }
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
      { title: 'Transfer', note: 'A transfer is a permanent audit record: the device, both parties, the type and the date.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'from_partner_id', label: 'From' },
          { name: 'to_partner_id', required: true, label: 'To' },
          { name: 'transfer_type', required: true, label: 'Type' },
          { name: 'transfer_date', required: true, label: 'Transfer Date' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

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
      { title: 'Preventive Maintenance', fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'plan_type', required: true, label: 'Plan Type' },
          { name: 'interval_months', label: 'Interval (months)' },
          { name: 'last_done', label: 'Last Done', readonly: true },
          { name: 'next_due', required: true, label: 'Next Due' },
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
      candidate: 'Candidate', merged: 'Merged', rejected: 'Rejected' } },
    sections: [
      { title: 'Resolution', note: 'An approved merge deactivates the duplicate device; it is never deleted, so its history stays auditable. A Tier 2 approver decides it from the approval inbox.',
        fields: [
          { name: 'primary_device_id', required: true, label: 'Surviving Device' },
          { name: 'duplicate_device_id', required: true, label: 'Duplicate Device' },
          { name: 'match_reason', required: true, label: 'Match Reason' },
          { name: 'match_score', label: 'Match Score %' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'approval_state', label: 'Merge Approval', readonly: true },
          { name: 'resolved_by_id', label: 'Resolved By', readonly: true },
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
      { title: 'Custody', note: 'A lost event with no later found event is a custody exception. Events are permanent: never edited or dated in the future; record the next event instead.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'event', required: true, label: 'Event' },
          { name: 'from_party_id', label: 'From' },
          { name: 'to_party_id', label: 'To' },
          { name: 'custodian_id', label: 'Custodian' },
          { name: 'event_date', required: true, label: 'Event Date' },
          { name: 'reference', label: 'Reference' },
          { name: 'notes', label: 'Notes' }
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
    sections: [
      { title: 'Component', note: 'One row per installation; removal is an explicit action with its own date.',
        fields: [
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'part_name', required: true, label: 'Part / Component' },
          { name: 'serial_no', label: 'Component Serial' },
          { name: 'installed_on', required: true, label: 'Installed On' },
          { name: 'source_ref', label: 'Source Order / PO' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'removed_on', label: 'Removed On', readonly: true },
          { name: 'notes', label: 'Notes' }
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
      { title: "Device Warranty", note: "The warranty attached to a registered device; expiry drives claim eligibility.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'device_id', required: true, label: "Device" },
          { name: 'warranty_type', required: true, label: "Warranty Type" },
          { name: 'start_date', required: true, label: "Start Date" },
          { name: 'end_date', required: true, label: "End Date" },
          { name: 'status', label: "Status", readonly: true },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'coverage_details', type: 'text', label: "Coverage Details" }
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
  'M17:Ownership Transfer': 'M17-form-transfer',
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
    'fix.device.component': 'M17-form-component'
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
    'M17-conditions': 'M17-form-condition'
  }
};

export const CREATE = {
  M17: { screen: 'M17-form-asset', model: 'fix.device', label: 'Asset' }
};
