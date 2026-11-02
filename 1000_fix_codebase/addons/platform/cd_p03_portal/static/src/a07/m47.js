/** @odoo-module **/
/* A07 · Assets & Facilities — M47 Facility & Branch Infrastructure (v2 rebuild).
 * Registry-faithful: 5 groups / 12 screens / 5 reports / 5 forms / freg 71.
 * fix.site and fix.facility.work.order existed; leases, licences, utilities,
 * occupancy, building PM, safety equipment, incidents and site projects are new. */

export const MODULE = {
  area: 'A07', code: 'M47', en: 'Facility & Branch Infrastructure', title: 'M47 · Facility & Branch Infrastructure',
  bn: 'সুবিধা ও শাখা অবকাঠামো', icon: '🏬',
  desc: 'Site register and occupancy, lease administration and critical dates, statutory licences, utilities and anomalies, branch asset register, building services PM, facility work orders, safety equipment, security incidents and site open/close projects.',
  kpis: [
    { l: 'Sites', m: 'sites_active' },
    { l: 'Lease Renewals (90d)', m: 'leases_expiring_90d' },
    { l: 'Licence Gaps', m: 'licences_expired' },
    { l: 'Utilities Cost /sqft', m: 'utilities_cost_per_sqft', prefix: '৳ ' },
    { l: 'Open Facility Work Orders', m: 'open_work_orders' },
    { l: 'Safety Inspections Due', m: 'safety_due' }
  ],
  groups: [
    { en: 'Sites', screens: [
      { id: 'M47-sites', en: 'Site Register', bn: 'সাইট রেজিস্টার', t: 'g' },
      { id: 'M47-occupancy', en: 'Occupancy & Condition', bn: 'দখল ও অবস্থা', t: 'g' }
    ]},
    { en: 'Leases', screens: [
      { id: 'M47-leases', en: 'Lease Administration', bn: 'লিজ প্রশাসন', t: 'g' },
      { id: 'M47-dates', en: 'Critical-Date Control', bn: 'গুরুত্বপূর্ণ তারিখ', t: 'r' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M47-licences', en: 'Statutory Licences', bn: 'আইনি লাইসেন্স', t: 'g' },
      { id: 'M47-utilities', en: 'Utilities & Anomalies', bn: 'ইউটিলিটি', t: 'g' }
    ]},
    { en: 'Infrastructure', screens: [
      { id: 'M47-infra', en: 'Branch Asset Register', bn: 'শাখা সম্পদ', t: 'r' },
      { id: 'M47-pm', en: 'Building Services PM', bn: 'ভবন সেবা', t: 'g' },
      { id: 'M47-wo', en: 'Facility Work Orders', bn: 'সুবিধা কাজ', t: 'g' }
    ]},
    { en: 'Safety', screens: [
      { id: 'M47-safety', en: 'Safety Equipment', bn: 'নিরাপত্তা সরঞ্জাম', t: 'g' },
      { id: 'M47-security', en: 'Security & Incidents', bn: 'নিরাপত্তা ঘটনা', t: 'g' },
      { id: 'M47-opening', en: 'Site Open / Close Projects', bn: 'সাইট খোলা/বন্ধ', t: 'g' }
    ]}
  ],
  reports: ['Cost per Site / per Job', 'Lease Expiry Register', 'Licence Compliance', 'Utilities Variance', 'Facility Work Order Performance', 'Branch Asset Register'],
  forms: ['Site', 'Lease', 'Licence', 'Facility Work Order', 'Safety Inspection'],
  cross: ['M04 branch operations', 'M30 branch provisioning', 'M49 ROU assets', 'M59 safety committee'],
  freg: { src: 71, sub: [
    ['1', 'Site Register', 7], ['2', 'Lease Administration', 11],
    ['3', 'Statutory Compliance', 9], ['4', 'Utilities', 6],
    ['5', 'Infrastructure Assets', 9], ['6', 'Building PM', 7],
    ['7', 'Work Orders', 6], ['8', 'Safety & Security', 10],
    ['9', 'Open / Close Projects', 6]
  ] }
};

export const SCREENS = {
  'M47-sites': { kind: 'model_list', model: 'fix.site', stateField: 'state',
    cols: ['name', 'site_type', 'branch_id', 'floor_area_sqm', 'lease_start', 'lease_end', 'monthly_rent', 'state'],
    actions: [
      { m: 'action_close', l: 'Close Site' },
      { m: 'action_reopen', l: 'Reopen Site' }
    ] },
  'M47-occupancy': { kind: 'model_list', model: 'fix.site.condition',
    cols: ['name', 'site_id', 'inspected_on', 'occupancy_pct', 'condition_grade', 'inspector_id', 'notes'] },
  'M47-leases': { kind: 'model_list', model: 'fix.site.lease', stateField: 'state',
    cols: ['name', 'site_id', 'lessor_id', 'start_date', 'end_date', 'monthly_rent', 'escalation_pct', 'state'] },
  'M47-dates': { kind: 'table_report', module: 'M47', report: 'critical_dates', title: 'Critical-Date Control', period: false },
  'M47-licences': { kind: 'model_list', model: 'fix.site.licence', stateField: 'state',
    cols: ['name', 'site_id', 'licence_type', 'number', 'issued_on', 'valid_to', 'is_valid', 'state'] },
  'M47-utilities': { kind: 'model_list', model: 'fix.site.utility',
    cols: ['name', 'site_id', 'period', 'utility_type', 'amount', 'usage', 'unit', 'flagged'],
    actions: [{ m: 'action_flag', l: 'Flag Anomaly' }] },
  'M47-infra': { kind: 'model_list', model: 'fix.site.asset', stateField: 'state',
    cols: ['name', 'site_id', 'asset_type', 'tag', 'installed_on', 'warranty_end', 'value', 'state'],
    actions: [
      { m: 'action_maintenance', l: 'Take to Maintenance' },
      { m: 'action_restore', l: 'Restore to Service' },
      { m: 'action_retire', l: 'Retire Asset' }
    ] },
  'M47-pm': { kind: 'model_list', model: 'fix.site.pm', stateField: 'state',
    cols: ['name', 'site_id', 'service_type', 'provider_id', 'scheduled_on', 'done_on', 'cost', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M47-wo': { kind: 'model_list', model: 'fix.facility.work.order', stateField: 'state',
    cols: ['name', 'site_id', 'work_type', 'scheduled_date', 'assigned_to', 'estimated_cost', 'actual_cost', 'state'],
    actions: [
      { m: 'action_schedule', l: 'Schedule' },
      { m: 'action_start', l: 'Start' },
      { m: 'action_complete', l: 'Complete' }
    ] },
  'M47-safety': { kind: 'model_list', model: 'fix.site.safety', stateField: 'state',
    cols: ['name', 'site_id', 'equipment_type', 'ref', 'last_check', 'next_check', 'state'],
    actions: [{ m: 'action_check', l: 'Record Check' }] },
  'M47-security': { kind: 'model_list', model: 'fix.site.incident', stateField: 'state',
    cols: ['name', 'site_id', 'incident_type', 'occurred_on', 'severity', 'description', 'state'],
    actions: [{ m: 'action_close', l: 'Close Incident' }] },
  'M47-opening': { kind: 'model_list', model: 'fix.site.project', stateField: 'state',
    cols: ['name', 'site_id', 'project_type', 'planned_on', 'done_on', 'budget', 'state'],
    actions: [
      { m: 'action_start', l: 'Start Project' },
      { m: 'action_done', l: 'Complete Project' }
    ] },

  /* Report chips -> their own computed pack */
  'M47-rpt-cost': { kind: 'table_report', module: 'M47', report: 'cost_per_site', title: 'Cost per Site / per Job', period: false },
  'M47-rpt-lease': { kind: 'table_report', module: 'M47', report: 'lease_expiry', title: 'Lease Expiry Register', period: false },
  'M47-rpt-licence': { kind: 'table_report', module: 'M47', report: 'licence_compliance', title: 'Licence Compliance', period: false },
  'M47-rpt-utilities': { kind: 'table_report', module: 'M47', report: 'utilities_variance', title: 'Utilities Variance', period: false },
  'M47-rpt-wo': { kind: 'table_report', module: 'M47', report: 'work_order_performance', title: 'Facility Work Order Performance', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M47-form-site': {
    kind: 'model_form',
    model: 'fix.site',
    title: 'Site',
    back: 'M47-sites',
    status: { field: 'state', labels: { active: 'Active', closed: 'Closed' } },
    sections: [
      { title: 'Site', note: 'The site register is the anchor for leases, licences, utilities, occupancy, safety equipment and work orders. Closing a site keeps every historical record readable.',
        fields: [
          { name: 'name', required: true, label: 'Site Name' },
          { name: 'site_type', required: true, label: 'Site Type' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'floor_area_sqm', label: 'Floor Area (sqm)' },
          { name: 'lease_start', label: 'Lease Start' },
          { name: 'lease_end', label: 'Lease End' },
          { name: 'monthly_rent', label: 'Monthly Rent' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Address', note: 'Plant assets (HVAC, lift, generator, fire pump, UPS, CCTV) are recorded on the Branch Asset Register screen against this site.',
        fields: [
          { name: 'address', type: 'text', label: 'Address' }
        ] }
    ]
  },

  'M47-form-lease': {
    kind: 'model_form',
    model: 'fix.site.lease',
    title: 'Lease',
    back: 'M47-leases',
    status: { field: 'state', labels: { active: 'Active', expired: 'Expired', terminated: 'Terminated' } },
    sections: [
      { title: 'Lease', note: 'The end date cannot precede the start (database CHECK). The end date feeds Critical-Date Control and Lease Expiry.',
        fields: [
          { name: 'name', required: true, label: 'Lease Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'lessor_id', required: true, label: 'Lessor' },
          { name: 'start_date', required: true, label: 'Start Date' },
          { name: 'end_date', required: true, label: 'End Date' },
          { name: 'monthly_rent', label: 'Monthly Rent' },
          { name: 'escalation_pct', label: 'Escalation %' },
          { name: 'deposit', label: 'Deposit' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-licence': {
    kind: 'model_form',
    model: 'fix.site.licence',
    title: 'Licence',
    back: 'M47-licences',
    status: { field: 'state', labels: { valid: 'Valid', expired: 'Expired', suspended: 'Suspended' } },
    sections: [
      { title: 'Statutory Licence', note: 'Valid today is computed: the state must be Valid and the end date must not have passed. The flag is read-only and drives the Licence Gaps KPI.',
        fields: [
          { name: 'name', required: true, label: 'Licence Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'licence_type', required: true, label: 'Licence Type' },
          { name: 'number', label: 'Licence Number' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'is_valid', label: 'Valid Today' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M47-form-wo': {
    kind: 'model_form',
    model: 'fix.facility.work.order',
    title: 'Facility Work Order',
    back: 'M47-wo',
    status: { field: 'state', labels: {
      draft: 'Draft', scheduled: 'Scheduled', in_progress: 'In Progress',
      completed: 'Completed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Work Order', note: 'Draft → scheduled → in progress → completed; completion publishes the outbox event used downstream.',
        fields: [
          { name: 'name', required: true, label: 'Work Order' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'equipment_id', label: 'Target Equipment' },
          { name: 'work_type', required: true, label: 'Work Type' },
          { name: 'assigned_to', label: 'Assigned Engineer' },
          { name: 'scheduled_date', label: 'Scheduled Date' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Scope & Cost', note: 'The description is required; actual cost replaces the estimate in the performance report once recorded.',
        fields: [
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'estimated_cost', label: 'Estimated Cost' },
          { name: 'actual_cost', label: 'Actual Cost' }
        ] }
    ]
  },

  'M47-form-safety': {
    kind: 'model_form',
    model: 'fix.site.safety',
    title: 'Safety Inspection',
    back: 'M47-safety',
    status: { field: 'state', labels: { ok: 'OK', due: 'Due', overdue: 'Overdue' } },
    sections: [
      { title: 'Safety Equipment', note: 'Recording a check sets the last-check date and returns the item to OK.',
        fields: [
          { name: 'name', required: true, label: 'Check Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'equipment_type', required: true, label: 'Equipment Type' },
          { name: 'ref', label: 'Tag / Reference' },
          { name: 'last_check', label: 'Last Check' },
          { name: 'next_check', required: true, label: 'Next Check' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-condition': {
    kind: 'model_form',
    model: 'fix.site.condition',
    title: 'Occupancy & Condition',
    back: 'M47-occupancy',
    sections: [
      { title: 'Inspection', note: 'Occupancy is a 0–100 percentage (database CHECK); the grade is the recorded judgement of the inspector.',
        fields: [
          { name: 'name', required: true, label: 'Inspection Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'inspected_on', required: true, label: 'Inspected On' },
          { name: 'occupancy_pct', label: 'Occupancy %' },
          { name: 'condition_grade', required: true, label: 'Condition Grade' },
          { name: 'inspector_id', label: 'Inspector' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-asset': {
    kind: 'model_form',
    model: 'fix.site.asset',
    title: 'Infrastructure Asset',
    back: 'M47-infra',
    status: { field: 'state', labels: {
      operational: 'Operational', maintenance: 'Under Maintenance', retired: 'Retired' } },
    sections: [
      { title: 'Plant Asset', note: 'Operational → under maintenance → operational; retirement is final. The register drives the Branch Asset Register count and value.',
        fields: [
          { name: 'name', required: true, label: 'Asset Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'asset_type', required: true, label: 'Asset Type' },
          { name: 'tag', label: 'Asset Tag' },
          { name: 'serial_no', label: 'Serial No' },
          { name: 'installed_on', label: 'Installed On' },
          { name: 'warranty_end', label: 'Warranty End' },
          { name: 'value', label: 'Asset Value' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-utility': {
    kind: 'model_form',
    model: 'fix.site.utility',
    title: 'Utility Account',
    back: 'M47-utilities',
    sections: [
      { title: 'Utility', note: 'One line per site, period and utility type. The anomaly flag is a recorded judgement, not a statistical detector.',
        fields: [
          { name: 'name', required: true, label: 'Account Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'utility_type', required: true, label: 'Utility Type' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'usage', label: 'Usage' },
          { name: 'unit', label: 'Unit' },
          { name: 'flagged', label: 'Anomaly Flagged' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-pm': {
    kind: 'model_form',
    model: 'fix.site.pm',
    title: 'Building Services PM',
    back: 'M47-pm',
    status: { field: 'state', labels: { open: 'Open', done: 'Done' } },
    sections: [
      { title: 'PM Job', note: 'Only an open job can be marked done; the done date is set at completion.',
        fields: [
          { name: 'name', required: true, label: 'PM Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'service_type', required: true, label: 'Service Type' },
          { name: 'provider_id', label: 'Service Provider' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'done_on', label: 'Done On' },
          { name: 'cost', label: 'Cost' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-incident': {
    kind: 'model_form',
    model: 'fix.site.incident',
    title: 'Security Incident',
    back: 'M47-security',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed' } },
    sections: [
      { title: 'Incident', note: 'Only an open incident can be closed; the description is required.',
        fields: [
          { name: 'name', required: true, label: 'Incident Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'incident_type', required: true, label: 'Incident Type' },
          { name: 'occurred_on', required: true, label: 'Occurred On' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M47-form-project': {
    kind: 'model_form',
    model: 'fix.site.project',
    title: 'Site Open / Close Project',
    back: 'M47-opening',
    status: { field: 'state', labels: {
      planned: 'Planned', in_progress: 'In Progress', done: 'Done' } },
    sections: [
      { title: 'Project', note: 'Planned → in progress → done; the done date is set at completion.',
        fields: [
          { name: 'name', required: true, label: 'Project Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'project_type', required: true, label: 'Project Type' },
          { name: 'planned_on', required: true, label: 'Planned On' },
          { name: 'done_on', label: 'Done On' },
          { name: 'budget', label: 'Budget' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  /* computed pack that had no screen (closure 2026-10-28) */
  'M47-rpt-branchassets': { kind: 'table_report', module: 'M47', report: 'branch_assets', title: "Branch Asset Register", period: false },
};

export const REPORT_ROUTES = {
  'M47:Branch Asset Register': 'M47-rpt-branchassets',
  'M47:Cost per Site / per Job': 'M47-rpt-cost',
  'M47:Lease Expiry Register': 'M47-rpt-lease',
  'M47:Licence Compliance': 'M47-rpt-licence',
  'M47:Utilities Variance': 'M47-rpt-utilities',
  'M47:Facility Work Order Performance': 'M47-rpt-wo'
};

export const FORM_MODELS = {
  'M47:Site': 'fix.site',
  'M47:Lease': 'fix.site.lease',
  'M47:Licence': 'fix.site.licence',
  'M47:Facility Work Order': 'fix.facility.work.order',
  'M47:Safety Inspection': 'fix.site.safety'
};

export const FORM_CHIPS = {
  'M47:Site': 'M47-form-site',
  'M47:Lease': 'M47-form-lease',
  'M47:Licence': 'M47-form-licence',
  'M47:Facility Work Order': 'M47-form-wo',
  'M47:Safety Inspection': 'M47-form-safety',
  'M47:__by_model__': {
    'fix.site': 'M47-form-site',
    'fix.site.lease': 'M47-form-lease',
    'fix.site.licence': 'M47-form-licence',
    'fix.facility.work.order': 'M47-form-wo',
    'fix.site.safety': 'M47-form-safety',
    'fix.site.condition': 'M47-form-condition',
    'fix.site.asset': 'M47-form-asset',
    'fix.site.utility': 'M47-form-utility',
    'fix.site.pm': 'M47-form-pm',
    'fix.site.incident': 'M47-form-incident',
    'fix.site.project': 'M47-form-project'
  },
  'M47:__by_screen__': {
    'M47-sites': 'M47-form-site',
    'M47-occupancy': 'M47-form-condition',
    'M47-leases': 'M47-form-lease',
    'M47-licences': 'M47-form-licence',
    'M47-utilities': 'M47-form-utility',
    'M47-infra': 'M47-form-asset',
    'M47-pm': 'M47-form-pm',
    'M47-wo': 'M47-form-wo',
    'M47-safety': 'M47-form-safety',
    'M47-security': 'M47-form-incident',
    'M47-opening': 'M47-form-project'
  }
};

export const CREATE = {
  M47: { screen: 'M47-form-site', model: 'fix.site', label: 'Site' }
};
