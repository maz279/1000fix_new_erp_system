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
      { id: 'M46-assign', en: 'Assignment & Pool', bn: 'অ্যাসাইনমেন্ট', t: 'g' },
      { id: 'M46-models', en: 'Vehicle Models', bn: 'যানবাহনের মডেল', t: 'g' },
      { id: 'M46-brands', en: 'Vehicle Makes', bn: 'যানবাহনের নির্মাতা', t: 'g' }
    ]},
    { en: 'Statutory', screens: [
      { id: 'M46-docs', en: 'Documents & Expiry', bn: 'নথি ও মেয়াদ', t: 'g' },
      { id: 'M46-renewal', en: 'Off-Road Records', bn: 'অফ-রোড রেকর্ড', t: 'g' }
    ]},
    { en: 'Operations', screens: [
      { id: 'M46-preuse', en: 'Daily Pre-Use Checks', bn: 'দৈনিক চেক', t: 'g' },
      { id: 'M46-pm', en: 'PM by Odometer', bn: 'ওডোমিটার পিএম', t: 'g' },
      { id: 'M46-fuel', en: 'Fuel & Efficiency', bn: 'জ্বালানি ও দক্ষতা', t: 'g' },
      { id: 'M46-telematics', en: 'Telematics Health', bn: 'টেলিমেট্রিক্স', t: 'g' }
    ]},
    { en: 'Alerts', screens: [
      { id: 'M46-alerts', en: 'Alerts', bn: 'সতর্কতা', t: 'g' }
    ]},
    { en: 'Safety & Cost', screens: [
      { id: 'M46-accidents', en: 'Accidents & Insurance', bn: 'দুর্ঘটনা ও বীমা', t: 'g' },
      { id: 'M46-insurers', en: 'Insurers', bn: 'বিমাকারী', t: 'g' },
      { id: 'M46-behaviour', en: 'Driver Behaviour', bn: 'চালকের আচরণ', t: 'g' },
      { id: 'M46-cost', en: 'Cost per Kilometre', bn: 'প্রতি কিমি খরচ', t: 'g' }
    ]}
  ],
  reports: ['Fleet Availability', 'Fuel Efficiency Trend', 'Maintenance Cost per Vehicle', 'Statutory Compliance Register', 'Incident Summary'],
  forms: ['Vehicle', 'Driver', 'Fuel Transaction', 'Accident Report', 'PM Service'],
  cross: ['M03 rider fleet', 'M02 field vans', 'M52 fuel expenses', 'M47 site vehicles'],
  freg: { src: 62, sub: [
    ['1', 'Vehicle Register', 8, { model: 'fleet.vehicle', cols: ['name', 'license_plate', 'fix_driver_id', 'branch_id', 'fitness_expiry'], screens: ['M46-vehicles'] }],
    ['2', 'Statutory Documents', 9, { model: 'fix.vehicle.document', cols: ['name', 'vehicle_id', 'doc_type', 'number', 'valid_to', 'state'], screens: ['M46-docs', 'M46-renewal'] }],
    ['3', 'Drivers', 8, { model: 'fix.driver', cols: ['name', 'employee_id', 'license_no', 'license_expiry', 'state'], screens: ['M46-drivers', 'M46-behaviour'] }],
    ['4', 'Assignment & Pool', 6, { model: 'fix.vehicle.assignment', cols: ['name', 'vehicle_id', 'date', 'driver_id', 'technician_id', 'order_id', 'state'], screens: ['M46-assign'] }],
    ['5', 'Pre-Use & PM', 9, { model: 'fix.vehicle.check', cols: ['name', 'vehicle_id', 'driver_id', 'checked_on', 'passed'], screens: ['M46-preuse', 'M46-pm'] }],
    ['6', 'Fuel & Odometer', 8, { model: 'fix.vehicle.fuel', cols: ['vehicle_id', 'filled_on', 'litres', 'odometer', 'amount'], screens: ['M46-fuel', 'M46-cost'] }],
    ['7', 'Telematics', 5, { model: 'fix.vehicle.telemetry', cols: ['name', 'vehicle_id', 'device_ref', 'last_ping', 'state'], screens: ['M46-telematics'] }],
    ['8', 'Accidents & Insurance', 9, { model: 'fix.vehicle.accident', cols: ['name', 'vehicle_id', 'driver_id', 'occurred_on', 'damage_cost', 'state'], screens: ['M46-accidents'] }]
  ] }
};

export const SCREENS = {
  'M46-alerts': { kind: 'model_list', model: 'fix.asset.alert', stateField: 'state', create: false,
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M46']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  /* A retired vehicle stays on the register: its history is still read. */
  'M46-vehicles': { kind: 'model_list', model: 'fleet.vehicle',
    domain: [['active', 'in', [true, false]]],
    cols: ['name', 'license_plate', 'fix_driver_id', 'branch_id', 'compliance_ok', 'dispatch_blockers', 'fix_position_unknown', 'fitness_expiry', 'insurance_expiry', 'active', 'fix_retire_reason'],
    actions: [
      { m: 'action_assert_dispatchable', l: 'Assert Dispatchable' },
      /* A Fleet Logistics Manager's decision; it raises the disposal request to finance. */
      { m: 'action_retire', l: 'Retire', ask: 'Why is this vehicle leaving the fleet?', kwarg: 'reason' }
    ] },
  'M46-models': { kind: 'model_list', model: 'fleet.vehicle.model',
    note: 'A Fleet Officer adds a model here before registering the first vehicle of that model. A bike needs a motorcycle licence; a car or van a light one.',
    cols: ['name', 'brand_id', 'vehicle_type', 'model_year', 'seats'] },
  'M46-brands': { kind: 'model_list', model: 'fleet.vehicle.model.brand',
    note: 'The makes a vehicle model can name.',
    cols: ['name'] },
  'M46-drivers': { kind: 'model_list', model: 'fix.driver', stateField: 'state',
    cols: ['name', 'employee_id', 'license_no', 'license_class', 'license_class_codes', 'license_expiry', 'state', 'suspended_by_id'],
    /* A07 P0 recipe M46-6: both take a reason (kept in the chatter); the
     * suspender cannot reinstate, nor can anyone while the licence is expired.
     * A07 P1: Fleet Officer only; the licence-expiry job suspends on its own. */
    actions: [
      { m: 'action_suspend', l: 'Suspend', ask: 'Reason for the suspension', kwarg: 'reason' },
      { m: 'action_reinstate', l: 'Reinstate', ask: 'Reason for the reinstatement', kwarg: 'reason' }
    ] },
  /* M02 dispatch books a van for a field order that names one. A Fleet Officer
   * also books, changes and releases here; a booking a live field order holds
   * is changed on that order. Every save runs the dispatch gate. */
  'M46-assign': { kind: 'model_list', model: 'fix.vehicle.assignment', stateField: 'state',
    note: 'A booking holds a vehicle for one day. Making or changing one runs the dispatch gate and refuses a van already booked that day. Release frees the day and keeps the booking as history. A booking a live field order travels in is changed on that order.',
    domain: [['active', 'in', [true, false]]],
    cols: ['name', 'vehicle_id', 'date', 'driver_id', 'technician_id', 'order_id', 'field_order_ids', 'offroad_conflict_note', 'state', 'release_reason'],
    actions: [
      { m: 'action_reassign', l: 'Reassign', asks: [
        { label: 'New vehicle plate (blank = keep)', kwarg: 'vehicle' },
        { label: 'New driver name or licence number (blank = keep)', kwarg: 'driver' },
        { label: 'New technician name (blank = keep)', kwarg: 'technician' },
        { label: 'Reason for the change', kwarg: 'reason' }
      ] },
      { m: 'action_release', l: 'Release', ask: 'Reason for releasing the booking', kwarg: 'reason' }
    ] },
  'M46-docs': { kind: 'model_list', model: 'fix.vehicle.document', stateField: 'state',
    cols: ['name', 'vehicle_id', 'doc_type', 'number', 'valid_to', 'evidence_status', 'is_current', 'is_valid', 'state'],
    /* A07 P1: Fleet Officer only (record, attach the scan, mark expired). */
    actions: [{ m: 'action_expire', l: 'Mark Expired' }] },
  'M46-renewal': { kind: 'model_list', model: 'fix.vehicle.offroad', stateField: 'state',
    cols: ['name', 'vehicle_id', 'cause', 'reason', 'started_on', 'ended_on', 'state', 'raised_by_id', 'returned_by_id', 'return_check_id'],
    /* M46-8: a Fleet Officer other than the one who raised it; a defect,
     * accident or service record needs a passed pre-use check recorded after
     * the off-road start, a document record needs the renewal with its scan. */
    actions: [{ m: 'action_return', l: 'Return to Service' }] },
  'M46-preuse': { kind: 'model_list', model: 'fix.vehicle.check',
    cols: ['name', 'vehicle_id', 'driver_id', 'checked_on', 'odometer', 'passed', 'defects'] },
  'M46-pm': { kind: 'model_list', model: 'fix.vehicle.pm', stateField: 'state',
    cols: ['name', 'vehicle_id', 'pm_type', 'odometer', 'due_odometer', 'due_date', 'is_overdue', 'scheduled_on', 'done_on', 'cost', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M46-fuel': { kind: 'model_list', model: 'fix.vehicle.fuel', stateField: 'review_state',
    cols: ['name', 'vehicle_id', 'driver_id', 'filled_on', 'litres', 'odometer', 'amount', 'station', 'receipt_no', 'exception_summary', 'review_state'],
    /* M46-9: a held fill is reviewed by a Fleet Logistics Manager who did not
     * record it. A wrong reading that was accepted is corrected by the same
     * person, so one typo does not refuse every later fill. */
    actions: [
      { m: 'action_clear_exception', l: 'Clear Exception', ask: 'What was checked (receipt, odometer, route)?', kwarg: 'note' },
      { m: 'action_reject_fill', l: 'Reject Fill', ask: 'Reason for rejecting the fill', kwarg: 'reason' },
      { m: 'action_correct_odometer', l: 'Correct Odometer', asks: [
        { label: 'The right odometer reading (km)', kwarg: 'odometer', number: true },
        { label: 'What shows it (receipt, service record)?', kwarg: 'reason' }
      ] }
    ] },
  'M46-telematics': { kind: 'model_list', model: 'fix.vehicle.telemetry', stateField: 'state',
    cols: ['name', 'vehicle_id', 'device_ref', 'last_ping', 'odometer', 'fuel_level_pct', 'state'] },
  'M46-accidents': { kind: 'model_list', model: 'fix.vehicle.accident', stateField: 'state',
    cols: ['name', 'vehicle_id', 'driver_id', 'occurred_on', 'damage_cost', 'claim_ref', 'insurer_id', 'settlement_amount', 'approval_state', 'state'],
    /* M46-10: the claim carries the insurer's reference; a settlement above
     * Tier 0 is approved from the approver's inbox (M63); a Fleet Logistics
     * Manager who did not report it closes it, with the insurer and the
     * evidence, or closes it with no claim, with the reason. */
    actions: [
      { m: 'action_add_insurer', l: 'Add Insurer', ask: "The insurer's full name (an existing partner is marked, otherwise a new company is made)", kwarg: 'insurer' },
      { m: 'action_claim', l: 'File Claim', ask: "Insurer's claim reference (blank = the one on the record)", kwarg: 'claim_ref' },
      { m: 'action_request_approval', l: 'Request Settlement Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_close', l: 'Close Claim', ask: 'Settled amount in BDT (0 if declined)', kwarg: 'settlement' },
      { m: 'action_close_no_claim', l: 'Close With No Claim', ask: 'Why is no claim being made?', kwarg: 'reason' }
    ] },
  'M46-insurers': { kind: 'table_report', module: 'M46', report: 'insurers', title: 'Insurers', period: false },
  'M46-behaviour': { kind: 'table_report', module: 'M46', report: 'driver_behaviour', title: 'Driver Behaviour', period: false },
  /* M46-11: cost/km and km/l honour the chosen period (fill to fill) */
  'M46-cost': { kind: 'table_report', module: 'M46', report: 'cost_per_km', title: 'Cost per Kilometre' },

  /* Report chips -> their own computed pack */
  'M46-rpt-availability': { kind: 'table_report', module: 'M46', report: 'fleet_availability', title: 'Fleet Availability', period: false },
  'M46-rpt-fuel': { kind: 'table_report', module: 'M46', report: 'fuel_efficiency', title: 'Fuel Efficiency Trend' },
  'M46-rpt-maintenance': { kind: 'table_report', module: 'M46', report: 'maintenance_cost', title: 'Maintenance Cost per Vehicle', period: false },
  'M46-rpt-statutory': { kind: 'table_report', module: 'M46', report: 'statutory_compliance', title: 'Statutory Compliance Register', period: false },
  'M46-rpt-incident': { kind: 'table_report', module: 'M46', report: 'incident_summary', title: 'Incident Summary', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M46-form-vehicle': {
    kind: 'model_form',
    model: 'fleet.vehicle',
    title: 'Vehicle',
    back: 'M46-vehicles',
    tabs: [
      { id: 'register', label: '1. Register', bn: '১. রেজিস্টার', icon: '🚐', badge: '10' },
      { id: 'value', label: '2. Value & Retirement', bn: '২. মূল্য ও অবসর', icon: '💰', badge: '8' }
    ],
    sections: [
      { tab: 'register', title: 'Vehicle', note: 'The display name is generated from the model and plate (Odoo fleet); a plate is registered to one active vehicle. The fitness and insurance dates are read from the statutory document register (record a renewal as a document with its scan); dispatch is decided from the register. The licence class required follows the model (bike = motorcycle, car/van = light); raise it for a medium or heavy vehicle.',
        fields: [
          { name: 'model_id', required: true, label: 'Vehicle Model' },
          { name: 'license_plate', required: true, label: 'Licence Plate' },
          { name: 'fix_driver_id', label: 'Assigned Driver' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'fix_licence_class_required', label: 'Licence Class Required' },
          { name: 'fix_tank_capacity_l', label: 'Fuel Tank Capacity (L)' },
          { name: 'fitness_expiry', label: 'Fitness Expiry (register)', readonly: true },
          { name: 'insurance_expiry', label: 'Insurance Expiry (register)', readonly: true },
          { name: 'fix_position_unknown', label: 'Position Unknown', readonly: true }
        ] },
      { tab: 'value', title: 'Purchase, Cancellation & Retirement', note: 'The purchase value and the cancellation date are kept by a Fleet Logistics Manager. A value above the capitalisation floor raises a capitalisation request to finance; a cancellation date, or Retire on the Vehicle Register, raises a disposal request, and the dispatch gate refuses the vehicle. Retire takes the reason, and refuses while the vehicle is still booked.',
        fields: [
          { name: 'net_car_value', label: 'Purchase Value' },
          { name: 'acquisition_date', label: 'Registration Date' },
          { name: 'write_off_date', label: 'Plate Cancellation Date' },
          { name: 'fixed_asset_id', label: 'Fixed Asset', readonly: true },
          { name: 'active', label: 'In the Fleet', readonly: true },
          { name: 'fix_retire_reason', label: 'Retirement Reason', readonly: true },
          { name: 'fix_retired_on', label: 'Retired On', readonly: true },
          { name: 'fix_retired_by_id', label: 'Retired By', readonly: true }
        ] }
    ]
  },

  'M46-form-model': {
    kind: 'model_form',
    model: 'fleet.vehicle.model',
    title: 'Vehicle Model',
    back: 'M46-models',
    sections: [
      { title: 'Model', note: 'Kept by a Fleet Officer. A vehicle is registered against a model. If the make is not offered, add it on Vehicle Makes first.',
        fields: [
          { name: 'brand_id', required: true, label: 'Make' },
          { name: 'name', required: true, label: 'Model Name' },
          { name: 'vehicle_type', required: true, label: 'Vehicle Type' },
          { name: 'model_year', label: 'Model Year' },
          { name: 'seats', label: 'Seats' }
        ] }
    ]
  },

  'M46-form-brand': {
    kind: 'model_form',
    model: 'fleet.vehicle.model.brand',
    title: 'Vehicle Make',
    back: 'M46-brands',
    sections: [
      { title: 'Make', fields: [{ name: 'name', required: true, label: 'Make' }] }
    ]
  },

  'M46-form-assignment': {
    kind: 'model_form',
    model: 'fix.vehicle.assignment',
    title: 'Vehicle Booking',
    back: 'M46-assign',
    status: { field: 'state', labels: { booked: 'Booked', released: 'Released' } },
    sections: [
      { title: 'Booking', note: 'Kept by a Fleet Officer: one vehicle, one day. The dispatch gate reads the vehicle and the driver when you save: an uninsured vehicle, an expired licence or a van already booked that day is refused. With no driver chosen, the vehicle\'s assigned driver is used. A booking a live field order travels in is changed on that order.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'date', required: true, label: 'Day' },
          { name: 'driver_id', label: 'Driver' },
          { name: 'technician_id', label: 'Technician' },
          { name: 'order_id', label: 'Service Order' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ] },
      { title: 'Status',
        fields: [
          { name: 'dispatch_created', label: 'Made by Dispatch', readonly: true },
          { name: 'offroad_conflict_note', label: 'Off-Road Conflict', readonly: true },
          { name: 'released_on', label: 'Released On', readonly: true },
          { name: 'released_by_id', label: 'Released By', readonly: true },
          { name: 'release_reason', label: 'Release Reason', readonly: true }
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
      { title: 'Driver', note: 'One driver record per employee, kept by a Fleet Officer. The dispatch gate refuses a driver who is not active, whose licence expiry is past or not recorded, or whose BRTA licence class does not cover the vehicle. A driver whose licence has expired is suspended by the daily licence job (or on registration) and is reinstated only with the renewed licence.',
        fields: [
          { name: 'name', required: true, label: 'Driver Name' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'license_no', required: true, label: 'Licence No' },
          { name: 'license_class', label: 'Licence Class (e.g. Light, Motorcycle)' },
          { name: 'license_class_codes', label: 'BRTA Classes Read', readonly: true },
          { name: 'license_expiry', label: 'Licence Expiry' },
          { name: 'phone', label: 'Phone' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'suspended_by_id', label: 'Suspended By', readonly: true }
        ] }
    ]
  },

  'M46-form-fuel': {
    kind: 'model_form',
    model: 'fix.vehicle.fuel',
    title: 'Fuel Transaction',
    back: 'M46-fuel',
    tabs: [
      { id: 'fill', label: '1. Fill', bn: '১. জ্বালানি', icon: '⛽', badge: '11' },
      { id: 'review', label: '2. Exception Review', bn: '২. ব্যতিক্রম পর্যালোচনা', icon: '🔍', badge: '5' }
    ],
    sections: [
      { tab: 'fill', title: 'Fuel', note: 'Litres, amount and odometer are the basis of the efficiency and cost-per-km packs. Every fill names the driver and the amount. A fill is refused when the odometer is below the previous fill, the litres exceed the tank capacity, it repeats a recorded fill (same odometer and litres, or the same receipt at the same station) or the vehicle is off-road. If such a fill is genuine, give the reason: it is then held for review by a Fleet Logistics Manager who did not record it. A distance since the previous fill beyond what a full tank covers is held the same way. A held fill is left out of the cost figures until reviewed. Only the recorder corrects a fill, and a reviewed fill is locked.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'driver_id', required: true, label: 'Driver' },
          { name: 'filled_on', required: true, label: 'Filled On' },
          { name: 'litres', required: true, label: 'Litres' },
          { name: 'odometer', required: true, label: 'Odometer (km)' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'station', label: 'Station' },
          { name: 'receipt_no', label: 'Receipt No' },
          { name: 'receipt_file', label: 'Receipt (scan)', type: 'file' },
          { name: 'receipt_filename', label: 'Receipt File Name' },
          { name: 'exception_reason', label: 'Reason (if the fill is genuine)' }
        ] },
      { tab: 'review', title: 'Exception Review',
        fields: [
          { name: 'exception_summary', label: 'Exceptions', readonly: true },
          { name: 'review_state', label: 'Review', readonly: true },
          { name: 'reviewed_by_id', label: 'Reviewed By', readonly: true },
          { name: 'reviewed_on', label: 'Reviewed On', readonly: true },
          { name: 'review_note', label: 'Review Note', readonly: true }
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
    tabs: [
      { id: 'incident', label: '1. Incident', bn: '১. ঘটনা', icon: '🚨', badge: '14' },
      { id: 'settlement', label: '2. Settlement & Close', bn: '২. নিষ্পত্তি ও বন্ধ', icon: '🔐', badge: '7' }
    ],
    sections: [
      { tab: 'incident', title: 'Incident', note: 'Reporting an accident takes the vehicle off-road until a passed re-check by someone else. Reported → claim filed (with the insurer claim reference, by the reporter or a Fleet Officer) → closed by a Fleet Logistics Manager who did not report it, once the insurer and the evidence are recorded. With no claim to make, the same person closes it from Reported with Close With No Claim and the reason. If the insurer is not offered, a Fleet Officer adds it with Add Insurer on the list. A settlement above Tier 0 needs a DOFA approval from the approver inbox, and changing the figure afterwards withdraws it. A closed accident is locked.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'driver_id', label: 'Driver' },
          { name: 'occurred_on', required: true, label: 'Occurred On' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'damage_cost', label: 'Damage Cost' },
          { name: 'claim_ref', label: 'Insurance Claim Ref' },
          { name: 'insurer_id', label: 'Insurer' },
          { name: 'police_ref', label: 'Police Reference (GD/case no.)' },
          { name: 'injury', label: 'Injury Involved' },
          { name: 'evidence_file', label: 'Evidence (photos / assessor report)', type: 'file' },
          { name: 'evidence_filename', label: 'Evidence File Name' },
          { name: 'settlement_amount', label: 'Settlement Amount' },
          { name: 'hse_case_ref', label: 'HSE Case', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { tab: 'settlement', title: 'Settlement Approval',
        fields: [
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'dofa_approved_by', label: 'Approved By', readonly: true },
          { name: 'dofa_approved_amount', label: 'Amount Approved', readonly: true },
          { name: 'closed_by_id', label: 'Closed By', readonly: true },
          { name: 'closed_on', label: 'Closed On', readonly: true },
          { name: 'no_claim_reason', label: 'Closed Without a Claim', readonly: true }
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
      { title: 'Service', note: 'A service is due on its due date or its due odometer, whichever comes first; the daily job flags it overdue. Mark Done (Fleet Officer) needs the odometer at service and a cost of zero or more; a completed PM is locked.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'pm_type', required: true, label: 'Type' },
          { name: 'odometer', label: 'Odometer at Service' },
          { name: 'due_odometer', label: 'Due Odometer' },
          { name: 'due_date', label: 'Due Date' },
          { name: 'is_overdue', label: 'Overdue', readonly: true },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'cost', label: 'Cost' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'done_on', label: 'Done On', readonly: true },
          { name: 'done_by_id', label: 'Completed By', readonly: true },
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
      { title: 'Document', note: 'Recorded by a Fleet Officer. Valid = state Valid, today between Valid From and Valid To, and the evidence scan attached. The gate reads the current document of each type: the latest recorded one in force, so a renewal supersedes the old certificate once it starts. A new document is valid only with an end date that is not past. An expired document cannot be made valid again, and a scanned one cannot be edited: record the renewal or the correction as a new document. The daily job expires lapsed documents, alerts 60/30/15/7/1 days ahead and takes a vehicle off-road when a mandatory document lapses.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'doc_type', required: true, label: 'Document Type' },
          { name: 'number', label: 'Document Number' },
          { name: 'valid_from', label: 'Valid From' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'evidence_file', label: 'Evidence (scan)', type: 'file' },
          { name: 'evidence_filename', label: 'Evidence File Name' },
          { name: 'evidence_status', label: 'Evidence', readonly: true },
          { name: 'is_current', label: 'Current', readonly: true },
          { name: 'is_valid', label: 'Valid Today', readonly: true },
          { name: 'state', label: 'State', readonly: true }
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
      { title: 'Off-Road', note: 'An open record removes the vehicle from availability until returned. Anyone may report a defect; a failed pre-use check, a reported accident and a lapsed mandatory document open one automatically. Return to Service is a Fleet Officer action by someone other than the person who raised the record: a defect, accident or service record needs a passed pre-use check recorded after the vehicle went off-road, and a service record also needs the service marked done; a document record needs the renewal recorded with its scan.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'started_on', required: true, label: 'Started On' },
          { name: 'cause', label: 'Cause', readonly: true },
          { name: 'raised_by_id', label: 'Raised By', readonly: true },
          { name: 'check_id', label: 'Failed Check', readonly: true },
          { name: 'accident_id', label: 'Accident', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'ended_on', label: 'Returned On', readonly: true },
          { name: 'returned_by_id', label: 'Returned By', readonly: true },
          { name: 'return_check_id', label: 'Re-Check', readonly: true }
        ] }
    ]
  },

  'M46-form-check': {
    kind: 'model_form',
    model: 'fix.vehicle.check',
    title: 'Pre-Use Check',
    back: 'M46-preuse',
    sections: [
      { title: 'Daily Check', note: 'Passed is computed: each of the four items must be ticked OK (an unanswered item fails the check); defects are recorded either way. A failed check takes the vehicle off-road at once, until a passed re-check is recorded and someone else returns it to service. A saved check cannot be changed: record a new one. A reading below the last recorded one, or further on than a full tank covers, is refused; if it is right, leave Odometer empty and tell the Fleet Logistics Manager.',
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
      { title: 'Telemetry', note: 'A snapshot of what the device reported, recorded by a Fleet Officer; no live feed is claimed. The state is derived from the last ping: online within the silence interval (cd_vehicle_ext.telematics_silence_minutes), stale after it (the vehicle is position-unknown, and an inspection of the device is raised), offline with no ping. Enter the last ping in your own local time. A saved snapshot is not edited.',
        fields: [
          { name: 'vehicle_id', required: true, label: 'Vehicle' },
          { name: 'device_ref', label: 'Telematics Device' },
          { name: 'last_ping', label: 'Last Ping' },
          { name: 'odometer', label: 'Odometer (km)' },
          { name: 'fuel_level_pct', label: 'Fuel Level %' },
          { name: 'state', label: 'State', readonly: true }
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
    'fix.vehicle.telemetry': 'M46-form-telemetry',
    'fix.vehicle.assignment': 'M46-form-assignment',
    'fleet.vehicle.model': 'M46-form-model',
    'fleet.vehicle.model.brand': 'M46-form-brand'
  },
  'M46:__by_screen__': {
    'M46-vehicles': 'M46-form-vehicle',
    'M46-drivers': 'M46-form-driver',
    'M46-assign': 'M46-form-assignment',
    'M46-models': 'M46-form-model',
    'M46-brands': 'M46-form-brand',
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
