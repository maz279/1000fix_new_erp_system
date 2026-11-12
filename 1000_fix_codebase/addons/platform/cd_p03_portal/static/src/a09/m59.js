/** @odoo-module **/
/* A09 · People & Workforce — M59 Health, Safety & Wellbeing.
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 60. */

export const MODULE = {
  area: 'A09', code: 'M59', en: 'Health, Safety & Wellbeing', title: 'M59 · Health, Safety & Wellbeing',
  bn: 'স্বাস্থ্য, নিরাপত্তা ও কল্যাণ', icon: '🦺',
  desc: 'Hazard register with risk scoring, JSA and safe procedures, PPE register, incident and near-miss reporting, investigation and RCA, the statutory DIFE notification clock, lone-worker check-ins, road and vehicle safety, battery/electrical/chemical risks, drills and training, the safety committee and occupational health with return-to-work.',
  kpis: [
    { l: 'Recordable Incidents YTD', m: 'recordable_incidents_ytd' },
    { l: 'Lost-Time Injuries', m: 'lost_time_injuries' },
    { l: 'Near-Miss MTD', m: 'near_miss_mtd' },
    { l: 'Statutory Clock', m: 'statutory_clock' },
    { l: 'PPE Stock Compliance', m: 'ppe_compliance', suffix: '%' },
    { l: 'Drills Completed', m: 'drills_completed' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M59-safety-inspection', en: "Safety Inspection", bn: "নিরাপত্তা পরিদর্শন", t: 'g' },
      { id: 'M59-statutory-accident-register', en: "Statutory Accident Register", bn: "সংবিধিবদ্ধ দুর্ঘটনা রেজিস্টার", t: 'g' }
    ]},
    { en: 'Risk', screens: [
      { id: 'M59-hazards', en: 'Hazard Register', bn: 'ঝুঁকি রেজিস্টার', t: 'g' },
      { id: 'M59-jsa', en: 'JSA & Safe Procedures', bn: 'কাজের নিরাপত্তা বিশ্লেষণ', t: 'g' },
      { id: 'M59-ppe', en: 'PPE Issue Register', bn: 'পিপিই বিতরণ', t: 'g' },
      { id: 'M59-ppe-stock', en: 'PPE Stock Register', bn: 'পিপিই', t: 'g' }
    ]},
    { en: 'Incidents', screens: [
      { id: 'M59-report', en: 'Incident & Near-Miss Reporting', bn: 'ঘটনা রিপোর্ট', t: 'g' },
      { id: 'M59-investigate', en: 'Investigation & RCA', bn: 'তদন্ত', t: 'g' },
      { id: 'M59-capa', en: 'CAPA Actions', bn: 'সংশোধনী পদক্ষেপ', t: 'g' },
      { id: 'M59-root-causes', en: 'Root Causes', bn: 'মূল কারণ', t: 'g' },
      { id: 'M59-investigation-team', en: 'Investigation Team', bn: 'তদন্ত দল', t: 'g' },
      { id: 'M59-statutory', en: 'Statutory Notification Clock', bn: 'আইনি ঘড়ি', t: 'r' }
    ]},
    { en: 'Field Safety', screens: [
      { id: 'M59-loneworker', en: 'Lone-Worker & Emergency', bn: 'একাকী কর্মী', t: 'g' },
      { id: 'M59-road', en: 'Road & Vehicle Safety', bn: 'সড়ক নিরাপত্তা', t: 'g' },
      { id: 'M59-battery', en: 'Battery / Electrical / Chemical', bn: 'ব্যাটারি ঝুঁকি', t: 'g' }
    ]},
    { en: 'Programme', screens: [
      { id: 'M59-drills', en: 'Drills & Training', bn: 'মহড়া', t: 'g' },
      { id: 'M59-committee', en: 'Safety Committee', bn: 'নিরাপত্তা কমিটি', t: 'g' },
      { id: 'M59-committee-members', en: 'Committee Members', bn: 'কমিটির সদস্য', t: 'g' },
      { id: 'M59-committee-meetings', en: 'Committee Meetings', bn: 'কমিটির সভা', t: 'g' },
      { id: 'M59-wellbeing', en: 'Occupational Health', bn: 'পেশাগত স্বাস্থ্য', t: 'g' },
      { id: 'M59-fitness', en: 'Fitness for Work', bn: 'কাজের উপযুক্ততা', t: 'g' },
      { id: 'M59-safety-followups', en: 'Lapsed Safety Certifications', bn: 'মেয়াদোত্তীর্ণ নিরাপত্তা সনদ', t: 'g' }
    ]}
  ],
  reports: ['Incident Statistics', 'Leading Indicators', 'Statutory Compliance', 'PPE Compliance', 'Drill Calendar Coverage'],
  forms: ['Incident Report', 'Anonymous Safety Report', 'JSA', 'PPE Issue', 'Return-to-Work'],
  cross: ['M47 Facility safety', 'M21 Workforce', 'M46 Fleet', 'M02 Field Safety'],
  freg: { src: 60, sub: [
    ['1', 'Hazard Register & Risk', 9, { model: 'fix.hse.hazard', cols: ['name', 'hazard_type', 'risk_score', 'residual_risk', 'state'], screens: ['M59-hazards', 'M59-safety-inspection'], reports: ['Leading Indicators'], forms: [] }],
    ['2', 'Procedures & Permits', 7, { model: 'fix.hse.jsa', cols: ['name', 'job_type', 'ppe_required', 'approved_on', 'state'], screens: ['M59-jsa'], reports: [], forms: ['JSA'] }],
    ['3', 'Incident Management', 13, { model: 'fix.hse.incident', cols: ['name', 'incident_type', 'severity', 'branch_id', 'state'], screens: ['M59-report', 'M59-investigate'], reports: ['Incident Statistics'], forms: ['Incident Report', 'Anonymous Safety Report'] }],
    ['4', 'Statutory Notification', 5, { model: 'fix.statutory.accident.register', cols: ['register_entry_no', 'employee_id', 'accident_date', 'notice_form_type', 'dife_notified'], screens: ['M59-statutory', 'M59-statutory-accident-register'], reports: ['Statutory Compliance'], forms: [] }],
    ['5', 'PPE', 5, { model: 'fix.ppe.register', cols: ['name', 'item_type', 'stock_quantity', 'min_required_quantity', 'state'], screens: ['M59-ppe-stock', 'M59-ppe'], reports: ['PPE Compliance'], forms: ['PPE Issue'] }],
    ['6', 'Field & Road Safety', 8, { model: 'fix.hse.roadcheck', cols: ['name', 'employee_id', 'vehicle_ref', 'checked_on', 'passed'], screens: ['M59-road', 'M59-loneworker', 'M59-battery'], reports: ['Leading Indicators'], forms: [] }],
    ['7', 'Training & Drills', 6, { model: 'fix.hse.drill', cols: ['name', 'drill_type', 'scheduled_on', 'completed_on', 'state'], screens: ['M59-drills', 'M59-committee'], reports: ['Drill Calendar Coverage'], forms: [] }],
    ['8', 'Health & Wellbeing', 7, { model: 'fix.hse.health', cols: ['name', 'employee_id', 'record_type', 'valid_until', 'fitness'], screens: ['M59-wellbeing'], reports: [], forms: ['Return-to-Work'] }]
  ] }
};

export const SCREENS = {
  'M59-safety-inspection': { kind: 'model_list', model: 'fix.safety.inspection', stateField: 'state',
    cols: ['name', 'branch_id', 'inspector_id', 'inspected_on', 'findings_count', 'critical_findings', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete Inspection' }] },
  'M59-statutory-accident-register': { kind: 'model_list', model: 'fix.statutory.accident.register',
    cols: ['name', 'register_entry_no', 'employee_id', 'accident_date', 'notice_due', 'notice_form_type', 'dife_notified', 'notified_late', 'dife_ack_ref', 'approval_state', 'state'],
    /* A09 audit M59-F5/F8: the notice is recorded by the notification
     * authority with the Form 27 on file; compensation is approved from the
     * M63 inbox, not here. */
    actions: [
      { m: 'action_notify_dife', l: 'Record DIFE Notice', ask: 'DIFE dispatch / acknowledgement reference', kwarg: 'notice_ref' },
      { m: 'action_request_approval', l: 'Request Compensation Approval' },
      { m: 'action_recall_approval', l: 'Recall Approval' },
      { m: 'action_record_return_to_work', l: 'Record Return to Work', ask: 'Return date (YYYY-MM-DD)', kwarg: 'return_date' },
      { m: 'action_close', l: 'Close Entry' }
    ] },
  'M59-hazards': { kind: 'model_list', model: 'fix.hse.hazard', stateField: 'state',
    cols: ['name', 'hazard_type', 'likelihood', 'severity', 'risk_score', 'residual_score', 'residual_risk', 'next_review_date', 'state'],
    actions: [{ m: 'action_control', l: 'Record Controls' }, { m: 'action_review', l: 'Record Review' }, { m: 'action_close', l: 'Close (another HSE Officer)' }] },
  'M59-jsa': { kind: 'model_list', model: 'fix.hse.jsa', stateField: 'state',
    cols: ['name', 'job_type', 'revision', 'ppe_required', 'approved_by_id', 'approved_on', 'approval_state', 'state'],
    /* A09 audit M59-F9: approved from another HSE Officer's inbox. */
    actions: [
      { m: 'action_request_approval', l: 'Request Approval' },
      { m: 'action_recall_approval', l: 'Recall Approval' },
      { m: 'action_revise', l: 'New Revision' },
      { m: 'action_retire', l: 'Retire' }
    ] },
  /* A09 M59-F13: an issue to one worker, acknowledged by that worker only. */
  'M59-ppe': { kind: 'model_list', model: 'fix.ppe.issue',
    cols: ['employee_id', 'ppe_id', 'quantity', 'issued_on', 'replace_by', 'replacement_alert_level', 'replaced', 'issued_by_id', 'acknowledged', 'acknowledged_on'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge Receipt' }] },
  'M59-committee-members': { kind: 'model_list', model: 'fix.safety.committee.member',
    cols: ['committee_id', 'employee_id', 'side', 'term_start'] },
  /* A meeting is append-only (the model refuses any edit) and is recorded
   * with Record Meeting on Safety Committee, which checks the committee is
   * constituted first; a direct create here would skip that check. */
  'M59-committee-meetings': { kind: 'model_list', model: 'fix.safety.committee.meeting', create: false,
    note: 'Recorded with Record Meeting on the Safety Committee screen. Minutes are a record: they are never edited, a new meeting is added instead.',
    cols: ['committee_id', 'meeting_date', 'minutes', 'actions'] },
  'M59-ppe-stock': { kind: 'model_list', model: 'fix.ppe.register', stateField: 'state',
    cols: ['name', 'item_type', 'regulatory_standard', 'stock_quantity', 'min_required_quantity', 'state'] },
  'M59-report': { kind: 'model_list', model: 'fix.hse.incident', stateField: 'state',
    cols: ['name', 'incident_type', 'severity', 'branch_id', 'anonymous', 'accident_datetime', 'notice_due', 'notice_form', 'dife_notice_ref', 'state'],
    actions: [
      { m: 'action_triage', l: 'Triage', ask: 'Triage note', kwarg: 'note' },
      { m: 'action_dispatch_dife_notice', l: 'Record DIFE Notice (s.80)', ask: 'DIFE dispatch / acknowledgement reference', kwarg: 'notice_ref' },
      { m: 'action_investigate', l: 'Investigate' },
      { m: 'action_escalate', l: 'Escalate Severity', ask: 'Why is the severity raised?', kwarg: 'reason' },
      { m: 'action_record_action_taken', l: 'Record Action Taken' },
      { m: 'action_close', l: 'Close Incident' }
    ] },
  /* Round 2 (M59-F8): investigation team, root causes and CAPA actions are
   * child records; every CAPA is verified by an HSE Officer who neither owns
   * nor completed it. */
  'M59-investigate': { kind: 'model_list', model: 'fix.hse.incident', stateField: 'state',
    cols: ['name', 'incident_type', 'severity', 'branch_id', 'reported_at', 'triaged_by_id', 'capa_open_count', 'capa_verified', 'state'],
    actions: [
      { m: 'action_investigate', l: 'Investigate' },
      { m: 'action_record_action_taken', l: 'Record Action Taken' },
      { m: 'action_close', l: 'Close Incident' }
    ] },
  'M59-capa': { kind: 'model_list', model: 'fix.hse.capa', stateField: 'state',
    cols: ['incident_id', 'name', 'action_type', 'owner_id', 'due_date', 'overdue', 'completed_by_id', 'verified_by_id', 'state'],
    actions: [
      { m: 'action_mark_done', l: 'Mark Done (owner)', ask: 'What was done?', kwarg: 'note' },
      { m: 'action_verify', l: 'Verify Effective (another HSE Officer)', ask: 'How was it verified effective?', kwarg: 'note' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Why is it cancelled?', kwarg: 'reason' }
    ] },
  'M59-root-causes': { kind: 'model_list', model: 'fix.hse.root.cause',
    cols: ['incident_id', 'category', 'description'] },
  'M59-investigation-team': { kind: 'model_list', model: 'fix.hse.investigation.member',
    cols: ['incident_id', 'employee_id', 'role'] },
  /* Round 2 (FR-HSE-037, BRU-HSE-15): the status and the functional
   * restriction only; the medical record stays with Occupational Health. */
  'M59-safety-followups': { kind: 'model_list', model: 'fix.hse.safety.followup', create: false, stateField: 'state',
    cols: ['name', 'employee_id', 'competency', 'expired_on', 'assigned_to_id', 'closed_by_id', 'state'],
    actions: [{ m: 'action_close', l: 'Close Follow-up', ask: 'What was done?', kwarg: 'outcome' }] },
  'M59-fitness': { kind: 'model_list', model: 'fix.hse.fitness.status', create: false, stateField: 'state',
    cols: ['employee_id', 'status', 'work_restriction', 'valid_from', 'valid_until', 'decided_by_id', 'state'] },
  'M59-statutory': { kind: 'table_report', module: 'M59', report: 'statutory_compliance', title: 'Statutory Notification Clock', period: true },
  'M59-loneworker': { kind: 'model_list', model: 'fix.hse.loneworker', stateField: 'state',
    cols: ['name', 'employee_id', 'field_order_id', 'opened_by_id', 'checkin_time', 'expected_end', 'buddy_id', 'state'],
    actions: [{ m: 'action_checkout', l: 'Check Out' }, { m: 'action_escalate', l: 'Escalate' }] },
  'M59-road': { kind: 'model_list', model: 'fix.hse.roadcheck',
    cols: ['name', 'employee_id', 'vehicle_ref', 'checked_on', 'licence_class', 'licence_expiry', 'tyres_ok', 'brakes_ok', 'documents_ok', 'passed'] },
  'M59-battery': { kind: 'model_list', model: 'fix.hazardous.substance.register', stateField: 'state',
    cols: ['name', 'un_number', 'storage_location', 'current_stock_litres', 'max_allowable_litres', 'msds_on_file', 'fire_suppression_type', 'state'],
    actions: [
      { m: 'action_quarantine', l: 'Quarantine', ask: 'Why is it quarantined?', kwarg: 'reason' },
      { m: 'action_release', l: 'Release from Quarantine' }
    ] },
  'M59-drills': { kind: 'model_list', model: 'fix.hse.drill', stateField: 'state',
    cols: ['name', 'drill_type', 'scheduled_on', 'completed_on', 'participants', 'duration_min', 'state'],
    actions: [{ m: 'action_complete', l: 'Mark Completed' }, { m: 'action_cancel', l: 'Cancel' }] },
  'M59-committee': { kind: 'model_list', model: 'fix.safety.committee',
    cols: ['name', 'branch_id', 'formation_date', 'chairperson_id', 'secretary_id', 'member_count', 'meeting_frequency', 'last_meeting_date', 'next_meeting_date', 'dife_registered', 'state'],
    /* A09 audit M59-F12: constituted only with a valid composition; a
     * meeting is a record with its minutes; DIFE registration needs the
     * acknowledgement on file. */
    actions: [
      { m: 'action_activate', l: 'Constitute' },
      { m: 'action_record_meeting', l: 'Record Meeting', ask: 'Minutes of the meeting', kwarg: 'minutes_text' },
      { m: 'action_record_dife_registration', l: 'Record DIFE Registration', ask: 'DIFE registration reference', kwarg: 'registration_ref' },
      { m: 'action_dissolve', l: 'Dissolve' }
    ] },
  'M59-wellbeing': { kind: 'model_list', model: 'fix.hse.health', stateField: 'state',
    cols: ['name', 'employee_id', 'record_type', 'record_date', 'valid_until', 'fitness', 'restrictions', 'work_restriction', 'clinician', 'fitness_status_id', 'state'],
    actions: [
      { m: 'action_publish_fitness', l: 'Publish Fitness Status' },
      { m: 'action_close', l: 'Close Record' }
    ] },

  /* Report chips -> their own computed pack */
  'M59-rpt-incidents': { kind: 'table_report', module: 'M59', report: 'incident_statistics', title: 'Incident Statistics', period: true },
  'M59-rpt-leading': { kind: 'table_report', module: 'M59', report: 'leading_indicators', title: 'Leading Indicators', period: true },
  'M59-rpt-statutory': { kind: 'table_report', module: 'M59', report: 'statutory_compliance', title: 'Statutory Compliance', period: true },
  'M59-rpt-ppe': { kind: 'table_report', module: 'M59', report: 'ppe_compliance', title: 'PPE Compliance', period: true },
  'M59-rpt-drills': { kind: 'table_report', module: 'M59', report: 'drill_coverage', title: 'Drill Calendar Coverage', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M59-form-incident': {
    kind: 'model_form',
    model: 'fix.hse.incident',
    title: 'Incident Report',
    back: 'M59-investigate',
    status: { field: 'state', labels: {
      reported: 'Reported', investigating: 'Investigating', action_taken: 'Action Taken',
      closed: 'Closed' } },
    tabs: [
      { id: 'severity', label: 'Incident Severity', bn: 'দুর্ঘটনার মাত্রা', icon: '🚨', badge: '7' },
      { id: 'statutory', label: 'Statutory Investigation', bn: 'তদন্ত ও নোটিশ', icon: '📑', badge: '10' },
      { id: 'corrective', label: 'Corrective Action', bn: 'সংশোধনী ব্যবস্থা', icon: '🔧', badge: '6' }
    ],
    sections: [
      {
        tab: 'severity',
        title: 'Workplace Incident Particulars',
        note: 'Incident severity classification under Department of Inspection for Factories and Establishments (DIFE) regulations.',
        fields: [
          { name: 'name', label: 'Incident Reference', readonly: true },
          { name: 'incident_type', required: true, label: 'Incident Type' },
          { name: 'severity', required: true, label: 'Severity Classification' },
          { name: 'branch_id', label: 'Incident Location / Branch' },
          { name: 'employee_id', label: 'Reporting Employee' },
          { name: 'injured_employee_id', label: 'Injured Employee / Technician' },
          { name: 'anonymous', label: 'Report Anonymously (no reporter is recorded)' }
        ]
      },
      {
        tab: 'statutory',
        title: 'Statutory DIFE Notification Clock (BLA s.80 + BLR r.70) & Form 28 Register',
        note: 'Two-working-day statutory notice deadline (Forms 27/27a/27b) and Form 28 accident register link.',
        fields: [
          { name: 'reported_at', label: 'Reported Timestamp', readonly: true },
          { name: 'accident_datetime', label: 'Actual Accident Timestamp' },
          { name: 'notice_due', label: '2-Working-Day DIFE Notice Deadline', readonly: true },
          { name: 'notice_form', label: 'Statutory Notice Form (27 / 27a / 27b)', readonly: true },
          { name: 'immediate_notification_required', label: 'Immediate Phone/Fax Notice Required', readonly: true },
          { name: 'dife_notice_ref', label: 'DIFE Notice Dispatch Ref', readonly: true },
          { name: 'statutory_record_id', label: 'Form 28 Accident Register Record', readonly: true },
          { name: 'site_incident_id', label: 'Raised From Site Incident', readonly: true },
          { name: 'source_notice_due_on', label: 'Site Incident Notice Reminder', readonly: true },
          { name: 'description', type: 'text', label: 'Factual Event Description' }
        ]
      },
      {
        tab: 'corrective',
        title: 'Investigation & CAPA (child records)',
        note: 'Team, root causes and CAPA actions are kept on their own screens; each CAPA has an owner, a due date and an independent verifier.',
        fields: [
          { name: 'investigation_findings', type: 'text', label: 'Investigation Findings' },
          { name: 'triaged_by_id', label: 'Triaged By', readonly: true },
          { name: 'triage_note', type: 'text', label: 'Triage Note', readonly: true },
          { name: 'capa_open_count', label: 'CAPA Not Yet Verified', readonly: true },
          { name: 'capa_verified', label: 'Every CAPA Verified', readonly: true },
          { name: 'state', label: 'Incident Lifecycle State', readonly: true }
        ]
      }
    ]
  },

  /* BRU-HSE-01 / T-10: the dedicated anonymous entry. It carries only what
   * an anonymous report may hold (what happened, where, when, who was hurt);
   * the server files it as the system user, so no reporter, author or
   * follower is recorded and the reporter keeps no access to it. */
  'M59-form-anonymous': {
    kind: 'model_form',
    model: 'fix.hse.incident',
    title: 'Anonymous Safety Report',
    back: 'M59-report',
    sections: [
      {
        title: 'What happened (no reporter is recorded)',
        note: 'Your name is not stored with this report. An HSE Officer triages it.',
        fields: [
          { name: 'anonymous', label: 'Report Anonymously', value: true },
          { name: 'incident_type', required: true, label: 'Incident Type' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'branch_id', label: 'Where (Branch)' },
          { name: 'accident_datetime', label: 'When' },
          { name: 'injured_employee_id', label: 'Who Was Hurt (if anyone)' },
          { name: 'description', type: 'text', label: 'What Happened' }
        ]
      }
    ]
  },
  'M59-form-hazard': {
    kind: 'model_form',
    model: 'fix.hse.hazard',
    title: 'Hazard Register',
    back: 'M59-hazards',
    status: { field: 'state', labels: {
      open: 'Open', controlled: 'Controlled', closed: 'Closed' } },
    tabs: [
      { id: 'identification', label: 'Hazard Particulars', bn: 'ঝুঁকি সনাক্তকরণ', icon: '⚠️', badge: '4' },
      { id: 'matrix', label: '5x5 Risk Assessment', bn: 'ঝুঁকি মূল্যায়ন ও নিয়ন্ত্রণ', icon: '🛡️', badge: '6' }
    ],
    sections: [
      {
        tab: 'identification',
        title: 'Hazard Identification',
        note: 'Physical, electrical, chemical, ergonomic or environmental workplace hazards.',
        fields: [
          { name: 'name', required: true, label: 'Hazard Description' },
          { name: 'hazard_type', required: true, label: 'Hazard Category' },
          { name: 'branch_id', label: 'Facility / Workshop Branch' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'matrix',
        title: '5x5 Risk Matrix & Hierarchy of Controls',
        note: 'Risk score is Likelihood (1-5) x Severity (1-5). Residual risk judged after implementing hierarchy of controls.',
        fields: [
          { name: 'likelihood', required: true, label: 'Likelihood Score (1-5)' },
          { name: 'severity', required: true, label: 'Severity Score (1-5)' },
          { name: 'risk_score', label: 'Initial Risk Score (L x S)', readonly: true },
          { name: 'controls', type: 'text', label: 'Control Measures Implemented' },
          { name: 'residual_likelihood', label: 'Residual Likelihood (1-5)' },
          { name: 'residual_severity', label: 'Residual Severity (1-5)' },
          { name: 'residual_score', label: 'Residual Score (L x S)', readonly: true },
          { name: 'next_review_date', label: 'Next Review Due', readonly: true },
          { name: 'residual_risk', label: 'Residual Risk Level', readonly: true },
          { name: 'state', label: 'Hazard State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-jsa': {
    kind: 'model_form',
    model: 'fix.hse.jsa',
    title: 'Job Safety Analysis',
    back: 'M59-jsa',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', retired: 'Retired' } },
    tabs: [
      { id: 'task', label: 'Task Specification', bn: 'কাজের বিবরণ ও পিপিই', icon: '🦺', badge: '4' },
      { id: 'steps', label: 'Safety Steps & Hazards', bn: 'ধাপ ও নিয়ন্ত্রণ ব্যবস্থা', icon: '🛡️', badge: '3' }
    ],
    sections: [
      {
        tab: 'task',
        title: 'Task & Required PPE',
        note: 'Safety analysis for high-risk field activities (working at heights, high-voltage HVAC repair).',
        fields: [
          { name: 'name', required: true, label: 'JSA Title' },
          { name: 'job_type', required: true, label: 'Job / Task Category' },
          { name: 'ppe_required', label: 'Mandatory PPE Required' },
          { name: 'approved_by_id', label: 'Safety Officer Approval', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true },
          { name: 'revision', label: 'Revision', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true }
        ]
      },
      {
        tab: 'steps',
        title: 'Step-by-Step Risk Mitigation',
        note: 'Sequential job steps, potential hazards, and preventive controls.',
        fields: [
          { name: 'steps', type: 'text', label: 'Job Steps' },
          { name: 'hazards', type: 'text', label: 'Potential Hazards per Step' },
          { name: 'controls', type: 'text', label: 'Mandatory Controls per Step' }
        ]
      }
    ]
  },

  'M59-form-ppe': {
    kind: 'model_form',
    model: 'fix.ppe.register',
    title: 'PPE Inventory Item',
    back: 'M59-ppe-stock',
    status: { field: 'state', labels: { adequate: 'Adequate Stock', low_stock: 'Low Stock Alert' } },
    tabs: [
      { id: 'item', label: 'Equipment Details', bn: 'সরঞ্জামের বিবরণ', icon: '🦺', badge: '3' },
      { id: 'stock', label: 'Stock & Replenishment', bn: 'মজুদ ও পুনঃপূরণ', icon: '📦', badge: '4' }
    ],
    sections: [
      {
        tab: 'item',
        title: 'Personal Protective Equipment Specification',
        note: 'Certified safety equipment (insulated gloves, safety boots, goggles, harness).',
        fields: [
          { name: 'name', required: true, label: 'PPE Item Name' },
          { name: 'item_type', required: true, label: 'Equipment Category' },
          { name: 'regulatory_standard', label: 'Regulatory Standard (EN/ANSI/BDS)' }
        ]
      },
      {
        tab: 'stock',
        title: 'Stock Thresholds & Replenishment Status',
        note: 'Triggers replenishment alert when stock drops below minimum required quantity.',
        fields: [
          { name: 'stock_quantity', label: 'Current In-Stock Quantity' },
          { name: 'min_required_quantity', label: 'Minimum Required Threshold' },
          { name: 'company_id', label: 'Company' },
          { name: 'state', label: 'Stock Adequacy State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-health': {
    kind: 'model_form',
    model: 'fix.hse.health',
    title: 'Occupational Health',
    back: 'M59-wellbeing',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed' } },
    tabs: [
      { id: 'checkup', label: 'Medical Assessment', bn: 'চিকিৎসা মূল্যায়ন', icon: '🩺', badge: '4' },
      { id: 'fitness', label: 'Fitness & Restrictions', bn: 'শারীরিক সক্ষমতা', icon: '📋', badge: '4' }
    ],
    sections: [
      {
        tab: 'checkup',
        title: 'Occupational Health Check',
        note: 'Periodic medical examinations and post-incident fitness evaluations.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'record_type', required: true, label: 'Record Type' },
          { name: 'record_date', required: true, label: 'Examination Date' },
          { name: 'valid_until', label: 'Fitness Valid Until' }
        ]
      },
      {
        tab: 'fitness',
        title: 'Clinical Assessment & Work Restrictions',
        note: 'Fitness outcome drives field dispatch capability.',
        fields: [
          { name: 'clinician', label: 'Examining Medical Officer' },
          { name: 'fitness', required: true, label: 'Clinical Fitness Status' },
          { name: 'restrictions', label: 'Medical Restrictions (clinical, Occupational Health only)' },
          { name: 'work_restriction', label: 'Work Restriction to Publish (functional, no diagnosis)' },
          { name: 'fitness_status_id', label: 'Published Fitness Status', readonly: true },
          { name: 'state', label: 'Record State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-capa': {
    kind: 'model_form',
    model: 'fix.hse.capa',
    title: 'CAPA Action',
    back: 'M59-capa',
    status: { field: 'state', labels: {
      open: 'Open', done: 'Done', verified: 'Verified Effective', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'plan', label: 'Action & Owner', bn: 'পদক্ষেপ ও দায়িত্ব', icon: '🔧', badge: '5' },
      { id: 'verify', label: 'Completion & Verification', bn: 'সম্পাদন ও যাচাই', icon: '✅', badge: '5' }
    ],
    sections: [
      {
        tab: 'plan',
        title: 'Corrective / Preventive Action (BRU-HSE-06)',
        note: 'Planned by HSE; owned by one person with a due date.',
        fields: [
          { name: 'incident_id', required: true, label: 'Incident' },
          { name: 'name', required: true, label: 'Action' },
          { name: 'action_type', label: 'Type' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'due_date', required: true, label: 'Due Date' }
        ]
      },
      {
        tab: 'verify',
        title: 'Done by the Owner, Verified by Another HSE Officer',
        note: 'Use the Mark Done and Verify Effective actions; nothing here is typed.',
        fields: [
          { name: 'completion_note', type: 'text', label: 'What Was Done', readonly: true },
          { name: 'completed_by_id', label: 'Completed By', readonly: true },
          { name: 'verification_note', type: 'text', label: 'Verification', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-root-cause': {
    kind: 'model_form',
    model: 'fix.hse.root.cause',
    title: 'Root Cause',
    back: 'M59-root-causes',
    tabs: [{ id: 'cause', label: 'Root Cause', bn: 'মূল কারণ', icon: '🔍', badge: '3' }],
    sections: [
      {
        tab: 'cause',
        title: 'Root Cause (BRU-HSE-05)',
        note: 'One row per cause; added by HSE, frozen once the incident closes.',
        fields: [
          { name: 'incident_id', required: true, label: 'Incident' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'description', type: 'text', required: true, label: 'Cause' }
        ]
      }
    ]
  },

  'M59-form-investigation-member': {
    kind: 'model_form',
    model: 'fix.hse.investigation.member',
    title: 'Investigation Team Member',
    back: 'M59-investigation-team',
    tabs: [{ id: 'member', label: 'Team Member', bn: 'দলের সদস্য', icon: '👥', badge: '3' }],
    sections: [
      {
        tab: 'member',
        title: 'Investigation Team',
        note: 'Lost-time and reportable incidents need a team before the action is recorded.',
        fields: [
          { name: 'incident_id', required: true, label: 'Incident' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'role', required: true, label: 'Role' }
        ]
      }
    ]
  },

  'M59-form-committee-member': {
    kind: 'model_form',
    model: 'fix.safety.committee.member',
    title: 'Safety Committee Member',
    back: 'M59-committee-members',
    tabs: [{ id: 'member', label: 'Committee Seat', bn: 'কমিটির আসন', icon: '👥', badge: '4' }],
    sections: [
      {
        tab: 'member',
        title: 'Committee Seat (BLR r.81)',
        note: 'An employee sits on a committee once. Constitute needs at least six members with both worker and employer representatives, and the chairperson and secretary among them.',
        fields: [
          { name: 'committee_id', required: true, label: 'Committee' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'side', required: true, label: 'Represents' },
          { name: 'term_start', label: 'Term Start' },
          { name: 'company_id', readonly: true, label: 'Company' }
        ]
      }
    ]
  },

  'M59-form-ppe-issue': {
    kind: 'model_form',
    model: 'fix.ppe.issue',
    title: 'PPE Issue',
    back: 'M59-ppe',
    tabs: [
      { id: 'issue', label: 'Issue', bn: 'বিতরণ', icon: '🦺', badge: '6' },
      { id: 'status', label: 'Acknowledgement & Replacement', bn: 'স্বীকৃতি ও প্রতিস্থাপন', icon: '🔁', badge: '4' }
    ],
    sections: [
      {
        tab: 'issue',
        title: 'PPE Issued to a Named Employee (FR-HSE-031)',
        note: 'A replacement names the issue it replaces; that issue then stops alerting.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'ppe_id', required: true, label: 'PPE Item' },
          { name: 'quantity', required: true, label: 'Quantity' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'replace_by', label: 'Replace By' },
          { name: 'replaces_id', label: 'Replaces Issue' }
        ]
      },
      {
        tab: 'status',
        title: 'Acknowledgement & Replacement Alerts (FR-HSE-032)',
        note: 'The daily cron alerts on the replace-by date and escalates once overdue.',
        fields: [
          { name: 'acknowledged', label: 'Acknowledged by the Employee', readonly: true },
          { name: 'replacement_alert_level', label: 'Replacement Alert Level', readonly: true },
          { name: 'replaced', label: 'Replaced', readonly: true },
          { name: 'issued_by_id', label: 'Issued By', readonly: true }
        ]
      }
    ]
  },

  'M59-form-inspection': {
    kind: 'model_form',
    model: 'fix.safety.inspection',
    title: 'Workplace Safety Inspection',
    back: 'M59-safety-inspection',
    status: { field: 'state', labels: {
      scheduled: 'Scheduled', in_progress: 'In Progress', completed: 'Completed' } },
    tabs: [
      { id: 'inspection', label: 'Inspection Scope', bn: 'পরিদর্শনের বিবরণ', icon: '🔍', badge: '4' },
      { id: 'findings', label: 'Findings & CAPA', bn: 'ফলাফল ও সংশোধনী', icon: '📋', badge: '4' }
    ],
    sections: [
      {
        tab: 'inspection',
        title: 'Facility & Workshop Safety Walkthrough',
        note: 'Periodic branch workshop, ESD bench, and fire safety inspection.',
        fields: [
          { name: 'name', label: 'Inspection Reference', readonly: true },
          { name: 'branch_id', required: true, label: 'Inspected Branch / Hub' },
          { name: 'inspector_id', required: true, label: 'Lead Safety Inspector' },
          { name: 'inspected_on', required: true, label: 'Inspection Date' }
        ]
      },
      {
        tab: 'findings',
        title: 'Non-Conformities & Corrective Actions',
        note: 'Critical findings and remediation notes.',
        fields: [
          { name: 'fire_extinguisher_ok', label: 'Fire Extinguisher Inspected & Valid' },
          { name: 'emergency_exit_ok', label: 'Emergency Exits Unobstructed' },
          { name: 'first_aid_ok', label: 'First Aid Box Stocked (BLR r.67)' },
          { name: 'electrical_ok', label: 'Electrical Wiring & Grounding Safe' },
          { name: 'esd_grounding_ok', label: 'ESD Benches & Mats Grounded' },
          { name: 'fume_extraction_ok', label: 'Soldering Fume Extractor Operational' },
          { name: 'chemical_storage_ok', label: 'IPA & Solvents in Flammable Cabinet' },
          { name: 'findings_count', label: 'Total Findings Count', readonly: true },
          { name: 'critical_findings', label: 'Critical Safety Violations', readonly: true },
          { name: 'findings', type: 'text', label: 'Inspection Observations & CAPA' },
          { name: 'state', label: 'Inspection State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-statutory-register': {
    kind: 'model_form',
    model: 'fix.statutory.accident.register',
    title: 'Statutory Accident Register (Form 28 — BLA s.90)',
    back: 'M59-statutory-accident-register',
    tabs: [
      { id: 'accident', label: 'Register Entry & Worker', bn: 'রেজিস্টার এন্ট্রি ও কর্মী', icon: '📒', badge: '5' },
      { id: 'injury', label: 'Injury & Lost Work Days', bn: 'আঘাত ও কর্মদিবস ক্ষতি', icon: '🩹', badge: '4' },
      { id: 'dife', label: 'DIFE Notice & Half-Year Return', bn: 'ডিআইএফই নোটিশ ও রিটার্ন', icon: '🏛️', badge: '5' }
    ],
    sections: [
      {
        tab: 'accident',
        title: 'Form 28 Statutory Accident Register Entry (BLA s.90 + BLR r.73)',
        note: 'Immutable statutory register entry once notified to DIFE.',
        fields: [
          { name: 'name', label: 'Register Record Reference', readonly: true },
          { name: 'register_entry_no', label: 'Form 28 Serial Entry No', readonly: true },
          { name: 'incident_id', label: 'Source HSE Incident', readonly: true },
          { name: 'employee_id', required: true, label: 'Injured Worker / Technician' },
          { name: 'accident_date', required: true, label: 'Accident Date' }
        ]
      },
      {
        tab: 'injury',
        title: 'Anatomical Injury & Incapacity Duration',
        note: 'Lost work days (>48h incapacity triggers mandatory DIFE notice).',
        fields: [
          { name: 'affected_body_part', label: 'Affected Body Part' },
          { name: 'nature_of_injury', label: 'Nature of Injury / Exposure' },
          { name: 'lost_work_days', label: 'Lost Work Days' },
          { name: 'return_to_work_date', label: 'Return-to-Work Date (from the fitness status)', readonly: true },
          { name: 'return_fitness_status', label: 'Returned As', readonly: true }
        ]
      },
      {
        tab: 'dife',
        title: 'DIFE Inspector Notification & Half-Yearly Return',
        note: 'Tracks Form 27/27a/27b notice acknowledgement and Form 28 half-yearly return.',
        fields: [
          { name: 'notice_form_type', label: 'Submitted Notice Form Type' },
          { name: 'dife_notified', label: 'Notified to DIFE Inspector', readonly: true },
          { name: 'dife_notification_date', label: 'DIFE Notification Date', readonly: true },
          { name: 'dife_ack_ref', label: 'DIFE Acknowledgement Receipt No', readonly: true },
          { name: 'notice_due', label: 'DIFE Notice Deadline', readonly: true },
          { name: 'notified_late', label: 'Notified After the Deadline', readonly: true },
          { name: 'dife_notice_file', type: 'binary', label: 'Form 27 / 27(a) as Dispatched' },
          { name: 'compensation_basis', label: 'Compensation Basis (BLA Ch. XII)' },
          { name: 'compensation_proposed', label: 'Assessed Compensation (BDT)' },
          { name: 'compensation_reason', type: 'text', label: 'Assessment Workings' },
          { name: 'statutory_compensation_bdt', label: 'Approved Compensation (BDT)', readonly: true },
          { name: 'approval_state', label: 'Compensation Approval', readonly: true },
          { name: 'half_year_return_due', label: 'Half-Yearly Return Due Date', readonly: true }
        ]
      }
    ]
  },

  'M59-form-loneworker': {
    kind: 'model_form',
    model: 'fix.hse.loneworker',
    title: 'Lone-Worker Check-In & Emergency SOS',
    back: 'M59-loneworker',
    // the model's states are checked_in / checked_out / escalated / missed
    // (there is no 'active': the open session showed its raw key)
    status: { field: 'state', labels: {
      checked_in: 'Checked In', checked_out: 'Checked Out Safe', escalated: 'Emergency Escalated',
      missed: 'Missed Check-Out' } },
    tabs: [
      { id: 'checkin', label: 'Session & Window', bn: 'চেক-ইন ও সময়সীমা', icon: '📍', badge: '6' },
      { id: 'buddy', label: 'Buddy & Escalation', bn: 'সহযোগী ও জরুরি পদক্ষেপ', icon: '🆘', badge: '5' }
    ],
    sections: [
      {
        tab: 'checkin',
        title: 'Field Technician Lone-Worker Session',
        note: 'Monitors late-night or remote premises field service visits.',
        fields: [
          { name: 'name', label: 'Session Reference', readonly: true },
          { name: 'employee_id', required: true, label: 'Field Technician' },
          { name: 'checkin_time', required: true, label: 'Check-In Timestamp' },
          { name: 'expected_end', required: true, label: 'Expected Check-Out Timestamp' },
          { name: 'location', label: 'Site / Location' },
          { name: 'notes', label: 'Notes' }
        ]
      },
      {
        tab: 'buddy',
        title: 'Assigned Safety Buddy & M02 Dispatch Escalation',
        note: 'Escalating emits hse.loneworker.escalated to M02 Dispatch.',
        fields: [
          { name: 'buddy_id', label: 'Assigned Safety Buddy' },
          { name: 'field_order_id', label: 'Field Order (a dispatcher opening it for the technician)' },
          { name: 'opened_by_id', label: 'Opened By', readonly: true },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', label: 'Session State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-roadcheck': {
    kind: 'model_form',
    model: 'fix.hse.roadcheck',
    title: 'Road & Vehicle Pre-Trip Safety Check',
    back: 'M59-road',
    tabs: [
      { id: 'vehicle', label: 'Rider & Vehicle', bn: 'রাইডার ও যানবাহন', icon: '🛵', badge: '4' },
      { id: 'checklist', label: 'Safety Checklist', bn: 'নিরাপত্তা যাচাই তালিকা', icon: '✅', badge: '5' }
    ],
    sections: [
      {
        tab: 'vehicle',
        title: 'Field Service Motorcycle / Van Identification',
        note: 'Daily pre-dispatch road safety inspection.',
        fields: [
          { name: 'name', label: 'Check Reference', readonly: true },
          { name: 'employee_id', required: true, label: 'Rider / Technician' },
          { name: 'vehicle_ref', required: true, label: 'Vehicle Registration / Fleet No' },
          { name: 'checked_on', required: true, label: 'Inspection Date' }
        ]
      },
      {
        tab: 'checklist',
        title: 'Pre-Trip Mechanical & Document Verification',
        note: 'All checks must pass for safe field dispatch.',
        fields: [
          { name: 'tyres_ok', label: 'Tyre Pressure & Tread OK' },
          { name: 'brakes_ok', label: 'Front & Rear Brakes OK' },
          { name: 'lights_ok', label: 'Headlights, Indicators & Horn OK' },
          { name: 'documents_ok', label: 'BRTA License, Fitness & Insurance Valid' },
          { name: 'licence_number', label: 'Driving Licence No. (from the licence record)', readonly: true },
          { name: 'licence_class', label: 'Licence Class', readonly: true },
          { name: 'licence_expiry', label: 'Licence Valid Until', readonly: true },
          { name: 'passed', label: 'Overall Road Safety Check Passed', readonly: true }
        ]
      }
    ]
  },

  'M59-form-substance': {
    kind: 'model_form',
    model: 'fix.hazardous.substance.register',
    title: 'Battery, Chemical & Hazardous Substance Register',
    back: 'M59-battery',
    status: { field: 'state', labels: {
      compliant: 'Compliant', over_limit: 'Over Storage Limit', review_due: 'MSDS Review Due' } },
    tabs: [
      { id: 'substance', label: 'Substance & UN Class', bn: 'রাসায়নিক ও ইউএন শ্রেণী', icon: '🧪', badge: '4' },
      { id: 'containment', label: 'Storage Limits & Fire Suppression', bn: 'মজুদ সীমা ও অগ্নিনির্বাপণ', icon: '🧯', badge: '5' }
    ],
    sections: [
      {
        tab: 'substance',
        title: 'Hazardous Material / Lithium Battery Classification',
        note: 'IPA flux solvents, refrigerant gases, and swollen Li-ion battery quarantine.',
        fields: [
          { name: 'name', required: true, label: 'Substance / Material Name' },
          { name: 'un_number', label: 'UN Hazard Classification Number' },
          { name: 'storage_location', required: true, label: 'Designated Storage Location' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'containment',
        title: 'Volume Limits, MSDS & Fire Suppression',
        note: 'Enforces maximum storage capacity and Class D / CO2 fire suppression readiness.',
        fields: [
          { name: 'current_stock_litres', label: 'Current Stock Volume (L / kg)' },
          { name: 'max_allowable_litres', label: 'Maximum Allowable Volume (L / kg)' },
          { name: 'msds_on_file', label: 'Safety Data Sheet (MSDS) Displayed' },
          { name: 'fire_suppression_type', label: 'Required Fire Suppression Agent' },
          { name: 'state', label: 'Compliance State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-drill': {
    kind: 'model_form',
    model: 'fix.hse.drill',
    title: 'Emergency Drill & Safety Training',
    back: 'M59-drills',
    status: { field: 'state', labels: {
      planned: 'Planned', completed: 'Completed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'schedule', label: 'Drill Type & Schedule', bn: 'মহড়ার ধরন ও সূচি', icon: '🚒', badge: '4' },
      { id: 'execution', label: 'Participation & Outcome', bn: 'অংশগ্রহণ ও ফলাফল', icon: '📋', badge: '3' }
    ],
    sections: [
      {
        tab: 'schedule',
        title: 'Statutory Fire & Emergency Evacuation Drill (BLA s.62)',
        note: 'Mandatory fire fighting and evacuation drills across branches and central depot.',
        fields: [
          { name: 'name', required: true, label: 'Drill Title' },
          { name: 'drill_type', required: true, label: 'Emergency Drill Type' },
          { name: 'scheduled_on', required: true, label: 'Scheduled Date' },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' }
        ]
      },
      {
        tab: 'execution',
        title: 'Completion & Headcount Participation',
        note: 'Feeds the M59 Drill Calendar Coverage report.',
        fields: [
          { name: 'completed_on', label: 'Actual Completion Date', readonly: true },
          { name: 'participants', label: 'Participating Staff Count' },
          { name: 'duration_min', label: 'Duration (minutes)' },
          { name: 'findings', label: 'Findings' },
          { name: 'state', label: 'Drill State', readonly: true }
        ]
      }
    ]
  },

  'M59-form-committee': {
    kind: 'model_form',
    model: 'fix.safety.committee',
    title: 'Safety Committee (BLA s.90a)',
    back: 'M59-committee',
    tabs: [
      { id: 'constitution', label: 'Committee Constitution', bn: 'কমিটি গঠন', icon: '👥', badge: '6' },
      { id: 'meetings', label: 'Meeting Cadence', bn: 'সভার সময়সূচি', icon: '📅', badge: '3' }
    ],
    sections: [
      {
        tab: 'constitution',
        title: 'Statutory Safety Committee Constitution (BLA s.90a)',
        note: 'Mandatory joint management-worker safety committee for establishments with >= 50 workers.',
        fields: [
          { name: 'name', required: true, label: 'Committee Name' },
          { name: 'branch_id', label: 'Branch / Establishment' },
          { name: 'formation_date', required: true, label: 'Constitution Date' },
          { name: 'chairperson_id', label: 'Committee Chairperson' },
          { name: 'secretary_id', label: 'Committee Secretary' },
          { name: 'member_count', label: 'Total Members Count (Min 6)', readonly: true }
        ]
      },
      {
        tab: 'meetings',
        title: 'Quarterly Meeting Schedule & Minutes',
        note: 'Tracks statutory quarterly safety committee meetings.',
        fields: [
          { name: 'meeting_frequency', label: 'Meeting Frequency' },
          { name: 'last_meeting_date', label: 'Last Meeting Date', readonly: true },
          { name: 'next_meeting_date', label: 'Next Meeting Due', readonly: true },
          { name: 'dife_registration_file', type: 'binary', label: 'DIFE Registration Acknowledgement' },
          { name: 'dife_registered', label: 'DIFE Registered', readonly: true },
          { name: 'state', label: 'Committee State', readonly: true }
        ]
      }
    ]
  }
};

export const REPORT_ROUTES = {
  'M59:Incident Statistics': 'M59-rpt-incidents',
  'M59:Leading Indicators': 'M59-rpt-leading',
  'M59:Statutory Compliance': 'M59-rpt-statutory',
  'M59:PPE Compliance': 'M59-rpt-ppe',
  'M59:Drill Calendar Coverage': 'M59-rpt-drills'
};

export const FORM_MODELS = {
  'M59:Incident Report': 'fix.hse.incident',
  'M59:Anonymous Safety Report': 'fix.hse.incident',
  'M59:JSA': 'fix.hse.jsa',
  'M59:PPE Issue': 'fix.ppe.issue',
  'M59:Return-to-Work': 'fix.hse.health'
};

export const FORM_CHIPS = {
  'M59:Incident Report': 'M59-form-incident',
  'M59:Anonymous Safety Report': 'M59-form-anonymous',
  'M59:JSA': 'M59-form-jsa',
  'M59:PPE Issue': 'M59-form-ppe-issue',
  'M59:Return-to-Work': 'M59-form-health',
  'M59:__by_model__': {
    'fix.safety.inspection': 'M59-form-inspection',
    'fix.statutory.accident.register': 'M59-form-statutory-register',
    'fix.hse.hazard': 'M59-form-hazard',
    'fix.hse.jsa': 'M59-form-jsa',
    'fix.ppe.register': 'M59-form-ppe',
    'fix.hse.incident': 'M59-form-incident',
    'fix.hse.loneworker': 'M59-form-loneworker',
    'fix.hse.roadcheck': 'M59-form-roadcheck',
    'fix.hazardous.substance.register': 'M59-form-substance',
    'fix.hse.drill': 'M59-form-drill',
    'fix.safety.committee': 'M59-form-committee',
    'fix.hse.health': 'M59-form-health',
    'fix.hse.capa': 'M59-form-capa',
    'fix.hse.root.cause': 'M59-form-root-cause',
    'fix.hse.investigation.member': 'M59-form-investigation-member',
    'fix.ppe.issue': 'M59-form-ppe-issue',
    'fix.safety.committee.member': 'M59-form-committee-member'
  },
  'M59:__by_screen__': {
    'M59-safety-inspection': 'M59-form-inspection',
    'M59-statutory-accident-register': 'M59-form-statutory-register',
    'M59-hazards': 'M59-form-hazard',
    'M59-jsa': 'M59-form-jsa',
    'M59-ppe-stock': 'M59-form-ppe',
    'M59-report': 'M59-form-incident',
    'M59-investigate': 'M59-form-incident',
    'M59-loneworker': 'M59-form-loneworker',
    'M59-road': 'M59-form-roadcheck',
    'M59-battery': 'M59-form-substance',
    'M59-drills': 'M59-form-drill',
    'M59-committee': 'M59-form-committee',
    'M59-wellbeing': 'M59-form-health',
    'M59-capa': 'M59-form-capa',
    'M59-root-causes': 'M59-form-root-cause',
    'M59-investigation-team': 'M59-form-investigation-member',
    'M59-ppe': 'M59-form-ppe-issue',
    'M59-committee-members': 'M59-form-committee-member'
  }
};

export const CREATE = {
  M59: { screen: 'M59-form-incident', model: 'fix.hse.incident', label: 'Incident Report' }
};
