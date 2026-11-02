/** @odoo-module **/
/* A07 · Assets & Facilities — M46 Fleet & Vehicles (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 5 forms / freg 62.
 * The fleet.vehicle extension and dispatch assignments existed; drivers,
 * documents, off-road, checks, PM, fuel, telemetry and accidents are new. */

export const MODULE = {
  area: 'A07', code: 'M46', en: 'Fleet & Vehicles', title: 'M46 · Fleet & Vehicles',
  bn: 'ফ্লিট ও যানবাহন', icon: '🚚',
  desc: 'Vehicle register and driver register, assignment and pool, statutory documents and expiry, renewal and off-road records, daily pre-use checks, PM by odometer, fuel and efficiency, telematics health, accidents and insurance, driver behaviour and cost per kilometre.',
  kpis: [
    { l: 'Vehicles', m: 'vehicles' },
    { l: 'Available', m: 'fleet_available' },
    { l: 'Docs Expiring (90d)', m: 'docs_expiring_90d' },
    { l: 'Off Road', m: 'offroad' },
    { l: 'Fuel MTD', m: 'fuel_mtd', prefix: '৳ ' },
    { l: 'Incidents Open', m: 'accidents_open' }
  ],
  groups: [
    { en: 'Register', screens: [
      { id: 'M46-vehicles', en: 'Vehicle Register', bn: 'যানবাহন রেজিস্টার', t: 'g' },
      { id: 'M46-drivers', en: 'Driver Register', bn: 'চালক রেজিস্টার', t: 'g' },
      { id: 'M46-assign', en: 'Assignment & Pool', bn: 'অ্যাসাইনমেন্ট', t: 'g' }
    ]},
    { en: 'Statutory', screens: [
      { id: 'M46-docs', en: 'Documents & Expiry', bn: 'নথি ও মেয়াদ', t: 'g' },
      { id: 'M46-renewal', en: 'Renewal & Off-Road', bn: 'নবায়ন ও অফ-রোড', t: 'g' }
    ]},
    { en: 'Operations', screens: [
      { id: 'M46-preuse', en: 'Daily Pre-Use Checks', bn: 'দৈনিক চেক', t: 'g' },
      { id: 'M46-pm', en: 'PM by Odometer', bn: 'ওডোমিটার পিএম', t: 'g' },
      { id: 'M46-fuel', en: 'Fuel & Efficiency', bn: 'জ্বালানি ও দক্ষতা', t: 'g' },
      { id: 'M46-telematics', en: 'Telematics Health', bn: 'টেলিমেট্রিক্স', t: 'g' }
    ]},
    { en: 'Safety & Cost', screens: [
      { id: 'M46-accidents', en: 'Accidents & Insurance', bn: 'দুর্ঘটনা ও বীমা', t: 'g' },
      { id: 'M46-behaviour', en: 'Driver Behaviour', bn: 'চালকের আচরণ', t: 'g' },
      { id: 'M46-cost', en: 'Cost per Kilometre', bn: 'প্রতি কিমি খরচ', t: 'g' }
    ]}
  ],
  reports: ['Fleet Availability', 'Fuel Efficiency Trend', 'Maintenance Cost per Vehicle', 'Statutory Compliance Register', 'Incident Summary'],
  forms: ['Vehicle', 'Driver', 'Fuel Transaction', 'Accident Report', 'PM Service'],
  cross: ['M03 rider fleet', 'M02 field vans', 'M52 fuel expenses', 'M47 site vehicles'],
  freg: { src: 62, sub: [
    ['1', 'Vehicle Register', 8], ['2', 'Statutory Documents', 9],
    ['3', 'Drivers', 8], ['4', 'Assignment & Pool', 6],
    ['5', 'Pre-Use & PM', 9], ['6', 'Fuel & Odometer', 8],
    ['7', 'Telematics', 5], ['8', 'Accidents & Insurance', 9]
  ] }
};

export const SCREENS = {
  'M46-vehicles': { kind: 'model_list', model: 'fleet.vehicle',
    cols: ['name', 'license_plate', 'fix_driver_id', 'branch_id', 'fitness_expiry', 'insurance_expiry', 'compliance_ok'],
    actions: [{ m: 'action_assert_dispatchable', l: 'Assert Dispatchable' }] },
  'M46-drivers': { kind: 'model_list', model: 'fix.driver', stateField: 'state',
    cols: ['name', 'employee_id', 'license_no', 'license_class', 'license_expiry', 'state'],
    actions: [{ m: 'action_suspend', l: 'Suspend' }] },
  'M46-assign': { kind: 'model_list', create: false, model: 'fix.vehicle.assignment',
    cols: ['vehicle_id', 'date', 'technician_id', 'order_id'] },
  'M46-docs': { kind: 'model_list', model: 'fix.vehicle.document', stateField: 'state',
    cols: ['name', 'vehicle_id', 'doc_type', 'number', 'valid_to', 'is_valid', 'state'] },
  'M46-renewal': { kind: 'model_list', model: 'fix.vehicle.offroad', stateField: 'state',
    cols: ['name', 'vehicle_id', 'reason', 'started_on', 'ended_on', 'state'],
    actions: [{ m: 'action_return', l: 'Return to Service' }] },
  'M46-preuse': { kind: 'model_list', model: 'fix.vehicle.check',
    cols: ['name', 'vehicle_id', 'driver_id', 'checked_on', 'odometer', 'passed', 'defects'] },
  'M46-pm': { kind: 'model_list', model: 'fix.vehicle.pm', stateField: 'state',
    cols: ['name', 'vehicle_id', 'pm_type', 'odometer', 'due_odometer', 'scheduled_on', 'done_on', 'cost', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M46-fuel': { kind: 'model_list', model: 'fix.vehicle.fuel',
    cols: ['name', 'vehicle_id', 'driver_id', 'filled_on', 'litres', 'odometer', 'amount', 'station'] },
  'M46-telematics': { kind: 'model_list', model: 'fix.vehicle.telemetry', stateField: 'state',
    cols: ['name', 'vehicle_id', 'device_ref', 'last_ping', 'odometer', 'fuel_level_pct', 'state'] },
  'M46-accidents': { kind: 'model_list', model: 'fix.vehicle.accident', stateField: 'state',
    cols: ['name', 'vehicle_id', 'driver_id', 'occurred_on', 'damage_cost', 'claim_ref', 'state'],
    actions: [
      { m: 'action_claim', l: 'File Claim' },
      { m: 'action_close', l: 'Close Incident' }
    ] },
  'M46-behaviour': { kind: 'table_report', module: 'M46', report: 'driver_behaviour', title: 'Driver Behaviour', period: false },
  'M46-cost': { kind: 'table_report', module: 'M46', report: 'cost_per_km', title: 'Cost per Kilometre', period: false },

  /* Report chips -> their own computed pack */
  'M46-rpt-availability': { kind: 'table_report', module: 'M46', report: 'fleet_availability', title: 'Fleet Availability', period: false },
  'M46-rpt-fuel': { kind: 'table_report', module: 'M46', report: 'fuel_efficiency', title: 'Fuel Efficiency Trend', period: false },
  'M46-rpt-maintenance': { kind: 'table_report', module: 'M46', report: 'maintenance_cost', title: 'Maintenance Cost per Vehicle', period: false },
  'M46-rpt-statutory': { kind: 'table_report', module: 'M46', report: 'statutory_compliance', title: 'Statutory Compliance Register', period: false },
  'M46-rpt-incident': { kind: 'table_report', module: 'M46', report: 'incident_summary', title: 'Incident Summary', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M46-form-vehicle': {
    kind: 'model_form',
    model: 'fleet.vehicle',
    title: 'Vehicle',
    back: 'M46-vehicles',
    sections: [
      { title: 'Vehicle', note: 'The display name is generated from the model and plate (Odoo fleet); fitness and insurance dates drive the compliance flag that blocks dispatch.',
        fields: [
          { name: 'model_id', required: true, label: 'Vehicle Model' },
          { name: 'license_plate', required: true, label: 'Licence Plate' },
          { name: 'fix_driver_id', label: 'Assigned Driver' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'fitness_expiry', label: 'Fitness Expiry' },
          { name: 'insurance_expiry', label: 'Insurance Expiry' }
        ] }
    ]
  },

  'M46-form-driver': {
    kind: 'model_form',
    model: 'fix.driver',
    title: 'Driver',
    back: 'M46-drivers',
    status: { field: 'state', labels: { active: 'Active', suspended: 'Suspended' } },
    sections: [
      { title: 'Driver', note: 'One driver record per employee; the licence expiry is recorded, not enforced by a gate yet.',
        fields: [
          { name: 'name', required: true, label: 'Driver Name' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'license_no', required: true, label: 'Licence No' },
          { name: 'license_class', label: 'Licence Class' },
          { name: 'license_expiry', label: 'Licence Expiry' },
          { name: 'phone', label: 'Phone' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M46-form-fuel': {
    kind: 'model_form',
    model: 'fix.vehicle.fuel',
    title: 'Fuel Transaction',
    back: 'M46-fuel',
    sections: [
      { title: 'Fuel', note: 'Litres, amount and odometer are the basis of the efficiency and cost-per-km packs.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'driver_id', label: 'Driver' },
          { name: 'filled_on', required: true, label: 'Filled On' },
          { name: 'litres', required: true, label: 'Litres' },
          { name: 'odometer', required: true, label: 'Odometer (km)' },
          { name: 'amount', label: 'Amount' },
          { name: 'station', label: 'Station' }
        ] }
    ]
  },

  'M46-form-accident': {
    kind: 'model_form',
    model: 'fix.vehicle.accident',
    title: 'Accident Report',
    back: 'M46-accidents',
    status: { field: 'state', labels: {
      reported: 'Reported', claimed: 'Claim Filed', closed: 'Closed' } },
    sections: [
      { title: 'Incident', note: 'Reported → claimed → closed; the claim reference is recorded when filed.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'driver_id', label: 'Driver' },
          { name: 'occurred_on', required: true, label: 'Occurred On' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'damage_cost', label: 'Damage Cost' },
          { name: 'claim_ref', label: 'Insurance Claim Ref' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M46-form-pm': {
    kind: 'model_form',
    model: 'fix.vehicle.pm',
    title: 'PM Service',
    back: 'M46-pm',
    status: { field: 'state', labels: { open: 'Open', done: 'Done' } },
    sections: [
      { title: 'Service', note: 'The odometer at service and the due odometer record the PM interval actually used.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'pm_type', required: true, label: 'Type' },
          { name: 'odometer', label: 'Odometer at Service' },
          { name: 'due_odometer', label: 'Due Odometer' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'cost', label: 'Cost' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M46-form-document': {
    kind: 'model_form',
    model: 'fix.vehicle.document',
    title: 'Vehicle Document',
    back: 'M46-docs',
    status: { field: 'state', labels: { valid: 'Valid', expired: 'Expired' } },
    sections: [
      { title: 'Document', note: 'Validity is the state AND the end date.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'doc_type', required: true, label: 'Document Type' },
          { name: 'number', label: 'Document Number' },
          { name: 'valid_from', label: 'Valid From' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M46-form-offroad': {
    kind: 'model_form',
    model: 'fix.vehicle.offroad',
    title: 'Off-Road Record',
    back: 'M46-renewal',
    status: { field: 'state', labels: {
      offroad: 'Off Road', returned: 'Returned to Service' } },
    sections: [
      { title: 'Off-Road', note: 'An open record removes the vehicle from availability until returned.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'started_on', required: true, label: 'Started On' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M46-form-check': {
    kind: 'model_form',
    model: 'fix.vehicle.check',
    title: 'Pre-Use Check',
    back: 'M46-preuse',
    sections: [
      { title: 'Daily Check', note: 'Passed is computed: all four checks must be true; defects are recorded either way.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'driver_id', label: 'Driver' },
          { name: 'checked_on', required: true, label: 'Checked On' },
          { name: 'odometer', label: 'Odometer (km)' },
          { name: 'tyres_ok', label: 'Tyres OK' },
          { name: 'lights_ok', label: 'Lights OK' },
          { name: 'fluids_ok', label: 'Fluids OK' },
          { name: 'brakes_ok', label: 'Brakes OK' },
          { name: 'defects', type: 'text', label: 'Defects' }
        ] }
    ]
  },

  'M46-form-telemetry': {
    kind: 'model_form',
    model: 'fix.vehicle.telemetry',
    title: 'Telemetry Snapshot',
    back: 'M46-telematics',
    status: { field: 'state', labels: {
      online: 'Online', stale: 'Stale', offline: 'Offline' } },
    sections: [
      { title: 'Telemetry', note: 'A snapshot of what the device reported; no live feed is claimed.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'device_ref', label: 'Telematics Device' },
          { name: 'last_ping', label: 'Last Ping' },
          { name: 'odometer', label: 'Odometer (km)' },
          { name: 'fuel_level_pct', label: 'Fuel Level %' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M46:Fleet Availability': 'M46-rpt-availability',
  'M46:Fuel Efficiency Trend': 'M46-rpt-fuel',
  'M46:Maintenance Cost per Vehicle': 'M46-rpt-maintenance',
  'M46:Statutory Compliance Register': 'M46-rpt-statutory',
  'M46:Incident Summary': 'M46-rpt-incident'
};

export const FORM_MODELS = {
  'M46:Vehicle': 'fleet.vehicle',
  'M46:Driver': 'fix.driver',
  'M46:Fuel Transaction': 'fix.vehicle.fuel',
  'M46:Accident Report': 'fix.vehicle.accident',
  'M46:PM Service': 'fix.vehicle.pm'
};

export const FORM_CHIPS = {
  'M46:Vehicle': 'M46-form-vehicle',
  'M46:Driver': 'M46-form-driver',
  'M46:Fuel Transaction': 'M46-form-fuel',
  'M46:Accident Report': 'M46-form-accident',
  'M46:PM Service': 'M46-form-pm',
  'M46:__by_model__': {
    'fleet.vehicle': 'M46-form-vehicle',
    'fix.driver': 'M46-form-driver',
    'fix.vehicle.fuel': 'M46-form-fuel',
    'fix.vehicle.accident': 'M46-form-accident',
    'fix.vehicle.pm': 'M46-form-pm',
    'fix.vehicle.document': 'M46-form-document',
    'fix.vehicle.offroad': 'M46-form-offroad',
    'fix.vehicle.check': 'M46-form-check',
    'fix.vehicle.telemetry': 'M46-form-telemetry'
  },
  'M46:__by_screen__': {
    'M46-vehicles': 'M46-form-vehicle',
    'M46-drivers': 'M46-form-driver',
    'M46-docs': 'M46-form-document',
    'M46-renewal': 'M46-form-offroad',
    'M46-preuse': 'M46-form-check',
    'M46-pm': 'M46-form-pm',
    'M46-fuel': 'M46-form-fuel',
    'M46-telematics': 'M46-form-telemetry',
    'M46-accidents': 'M46-form-accident'
  }
};

export const CREATE = {
  M46: { screen: 'M46-form-vehicle', model: 'fleet.vehicle', label: 'Vehicle' }
};
