/** @odoo-module **/
/* A12 · M66 Internal IT Service Management. 3 groups / 8 screens / 4 reports / 4 forms / freg 52.
 *
 * A12 workflow audit (2026-11-04) R4/X5: the forms posted `state` (and the
 * ticket's resolution) as ordinary inputs — the badge at the top of the form
 * is now the ONLY place state appears, and every lifecycle button is an
 * action with its server-side checks: Resolve prompts for the resolution
 * text (M66-8), Submit routes the change through M63 (P1-1), Retire prompts
 * for the wipe certificate (M66-9).
 *
 * A12 finish (2026-11-07): every employee raises a ticket; Incidents, Requests and
 * All Tickets are different lists (N-M66-10); Assign names the agent (N-M66-5);
 * Implement First is the emergency path and Recall reaches the requester
 * (M66-3, N-M66-9); retirement is two people (M66-10). */

export const MODULE = {
  area: 'A12', code: 'M66', en: 'Internal IT Service Management', title: 'M66 · Internal IT Service Management',
  bn: 'আইটি সার্ভিস', icon: '🖥️',
  desc: 'Internal ITSM tickets (incidents and service requests) with catalogue SLA targets and escalation, IT change management with routed M63 approval, CAB review and rollback, the internal IT asset register with lifecycle, wipe-certificated retirement and warranty, and category/SLA analytics.',
  kpis: [
    { l: 'Tickets Open', m: 'tickets_open' },
    { l: 'Escalated (SLA)', m: 'tickets_escalated' },
    { l: 'Changes Pending', m: 'changes_pending' },
    { l: 'Assets In Service', m: 'assets_in_service' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M66-catalogue', en: 'Service Catalogue', bn: 'সার্ভিস ক্যাটালগ', t: 'g' },
      { id: 'M66-problems', en: 'Problems', bn: 'সমস্যা', t: 'g' },
      { id: 'M66-licences', en: 'Licences & Subscriptions', bn: 'লাইসেন্স ও সাবস্ক্রিপশন', t: 'g' },
      { id: 'M66-seats', en: 'Licence Seats', bn: 'লাইসেন্স সিট', t: 'g' },
      { id: 'M66-exceptions', en: 'Licence Exceptions', bn: 'লাইসেন্স ব্যতিক্রম', t: 'g' },
      { id: 'M66-cmdb', en: 'CMDB', bn: 'CMDB', t: 'g' },
      { id: 'M66-onboard', en: 'Onboard/Offboard Workflows', bn: 'Onboard/Offboard Workflows', t: 'g' }
    ]},
    { en: 'Service Desk', screens: [
      { id: 'M66-incidents', en: 'Incidents', bn: 'ইনসিডেন্ট', t: 'g' },
      { id: 'M66-requests', en: 'Service Requests', bn: 'সার্ভিস রিকোয়েস্ট', t: 'g' },
      { id: 'M66-all', en: 'All Tickets', bn: 'সব টিকেট', t: 'g' },
      { id: 'M66-sla', en: 'Ticket SLA', bn: 'এসএলএ', t: 'r' }
    ]},
    { en: 'Change', screens: [
      { id: 'M66-changes', en: 'Changes', bn: 'চেঞ্জ', t: 'g' },
      { id: 'M66-templates', en: 'Standard Change Templates', bn: 'স্ট্যান্ডার্ড চেঞ্জ টেমপ্লেট', t: 'g' },
      { id: 'M66-success', en: 'Change Success', bn: 'সাফল্য', t: 'r' }
    ]},
    { en: 'Assets', screens: [
      { id: 'M66-assets', en: 'IT Asset Lifecycle', bn: 'আইটি সম্পদ', t: 'g' },
      { id: 'M66-lifecycle', en: 'Asset Lifecycle', bn: 'লাইফসাইকেল', t: 'r' },
      { id: 'M66-mix', en: 'Ticket Category Mix', bn: 'ক্যাটাগরি', t: 'r' }
    ]}
  ],
  reports: ['ITSM Ticket SLA', 'Change Success Rate', 'IT Asset Lifecycle', 'Ticket Category Mix'],
  forms: ['Incident', 'Change', 'Asset', 'Service Request'],
  cross: ['M29 identity/access', 'M28 dead letters raise incidents', 'M30 platform releases (itsm.change_implemented)', 'M06 destruction review (itsm.asset_retired)', 'M21 exit clearance (asset recovery)', 'M67 project changes'],
  freg: { src: 52, sub: [
    ['1', 'Service Desk', 12, { model: 'fix.itsm.ticket', cols: ['name', 'title', 'category', 'priority', 'state'], screens: ['M66-incidents', 'M66-requests', 'M66-catalogue'], reports: ['ITSM Ticket SLA'], forms: ['Incident', 'Service Request'] }],
    ['2', 'Change Management', 10, { model: 'fix.itsm.change', cols: ['name', 'title', 'change_type', 'risk', 'risk_score', 'state'], screens: ['M66-changes', 'M66-success'], reports: ['Change Success Rate'], forms: ['Change'] }],
    ['3', 'Asset Register', 9, { model: 'fix.itsm.asset', cols: ['name', 'asset_tag', 'asset_kind', 'assigned_to_id', 'state'], screens: ['M66-assets', 'M66-lifecycle', 'M66-cmdb'], reports: ['IT Asset Lifecycle'], forms: ['Asset'] }],
    ['4', 'Knowledge', 6, { model: 'fix.itsm.problem', cols: ['name', 'title', 'severity', 'known_error', 'state'], screens: ['M66-problems'], reports: [], forms: [] }],
    ['5', 'Analytics', 8, { model: 'fix.itsm.ticket', cols: ['category', 'priority', 'state', 'assigned_to', 'create_date'], screens: ['M66-mix', 'M66-all'], reports: ['Ticket Category Mix', 'ITSM Ticket SLA'], forms: [], create: false }],
    ['6', 'Audit', 7, { model: 'fix.jml.event', cols: ['name', 'event_type', 'user_id', 'effective_on', 'state'], screens: ['M66-onboard', 'M66-licences'], reports: [], forms: [] }]
  ] }
};

/* Ticket lifecycle actions. Assign and Reassign name the agent (an employee code,
 * name or id; blank on Assign means the clicking agent). The server decides who may
 * press what: the assignee works the ticket, the requester closes, reopens or
 * answers it (M66-8). */
const TICKET_ACTIONS = [
  { m: 'action_classify', l: 'Classify', states: ['new', 'assigned', 'in_progress', 'awaiting_user'] },
  { m: 'action_request_fulfilment', l: 'Request Approval', states: ['new'] },
  { m: 'action_assign', l: 'Assign', states: ['new'], ask: 'Agent: employee code or name (blank = me)', kwarg: 'assigned_to' },
  { m: 'action_reassign', l: 'Reassign', states: ['assigned', 'in_progress', 'awaiting_user'], ask: 'Hand to which agent: employee code or name', kwarg: 'assigned_to' },
  { m: 'action_start', l: 'Start', states: ['assigned'] },
  { m: 'action_await_user', l: 'Await User', states: ['assigned', 'in_progress'], ask: 'What do you need from the user? (SLA pauses)', kwarg: 'reason' },
  { m: 'action_resume', l: 'Resume', states: ['awaiting_user'] },
  { m: 'action_resolve', l: 'Resolve', states: ['assigned', 'in_progress'], ask: 'Resolution (required)', kwarg: 'resolution' },
  { m: 'action_close', l: 'Close', states: ['resolved'] },
  { m: 'action_reopen', l: 'Reopen', states: ['resolved', 'closed'], ask: 'Why is it not fixed? (required)', kwarg: 'reason' },
  { m: 'action_declare_major', l: 'Declare Major', states: ['new', 'assigned', 'in_progress', 'awaiting_user'], ask: 'Named incident manager: login or employee code', kwarg: 'manager' },
  { m: 'action_major_update', l: 'Major Update', states: ['new', 'assigned', 'in_progress', 'awaiting_user'], ask: 'Update for the affected users', kwarg: 'note' },
  { m: 'action_raise_problem', l: 'Raise Problem', states: ['new', 'assigned', 'in_progress', 'awaiting_user', 'resolved', 'closed'] }
];

/* Change actions (P1-1): Submit routes through M63 (a change that follows an
 * authorised standard template is pre-approved; normal -> Change Manager;
 * emergency/high-risk -> CAB); approval itself happens in the approver's inbox,
 * never here. Implement First is the emergency path: implemented now, retro approval
 * and review to follow. */
const CHANGE_ACTIONS = [
  { m: 'action_submit', l: 'Submit', states: ['draft'] },
  { m: 'action_recall_approval', l: 'Recall', states: ['draft'] },
  { m: 'action_implement', l: 'Implement', states: ['approved'] },
  { m: 'action_emergency_implement', l: 'Implement First (Emergency)', states: ['draft'], ask: 'Why can this not wait for the CAB? (required)', kwarg: 'reason' },
  { m: 'action_record_pir', l: 'Record PIR', states: ['implemented', 'rolled_back'], ask: 'Post-implementation review notes (required)', kwarg: 'pir_notes' },
  { m: 'action_rollback', l: 'Roll Back', states: ['implemented', 'reviewed'], ask: 'Why is it coming out? (required)', kwarg: 'reason' }
];

const TICKET_COLS = ['name', 'title', 'category', 'priority', 'requester_id', 'assigned_to', 'problem_id', 'sla_deadline', 'escalated', 'approval_state', 'state'];

export const SCREENS = {
  'M66-incidents': { kind: 'model_list', model: 'fix.itsm.ticket', stateField: 'state',
    domain: [['ticket_type', '=', 'incident']],
    cols: ['name', 'title', 'category', 'priority', 'requester_id', 'assigned_to', 'major_incident', 'sla_deadline', 'escalated', 'state'],
    actions: TICKET_ACTIONS },
  'M66-requests': { kind: 'model_list', model: 'fix.itsm.ticket', stateField: 'state',
    domain: [['ticket_type', '=', 'request']],
    cols: ['name', 'title', 'catalogue_id', 'requester_id', 'assigned_to', 'sla_deadline', 'approval_state', 'state'],
    actions: TICKET_ACTIONS },
  'M66-all': { kind: 'model_list', model: 'fix.itsm.ticket', stateField: 'state',
    cols: TICKET_COLS,
    actions: TICKET_ACTIONS },
  'M66-changes': { kind: 'model_list', model: 'fix.itsm.change', stateField: 'state',
    cols: ['name', 'title', 'change_type', 'risk', 'risk_score', 'high_risk', 'requested_by_id', 'planned_on', 'approval_state', 'retro_approval_state', 'approved_by_id', 'pir_required', 'state'],
    actions: CHANGE_ACTIONS },
  'M66-templates': { kind: 'model_list', model: 'fix.itsm.change.template', stateField: 'state',
    cols: ['code', 'name', 'risk_score', 'max_window_hours', 'authorised_by_id', 'authorised_on', 'state'],
    actions: [
      { m: 'action_authorise', l: 'Authorise', states: ['draft'] },
      { m: 'action_retire_template', l: 'Retire', states: ['draft', 'authorised'] }
    ] },
  'M66-success': { kind: 'table_report', module: 'M66', report: 'change_success', title: 'Change Success Rate', period: false },
  'M66-assets': { kind: 'model_list', model: 'fix.itsm.asset', stateField: 'state',
    cols: ['name', 'asset_tag', 'asset_kind', 'assigned_to_id', 'acceptance_state', 'recovery_from_id', 'warranty_end', 'writeoff_state', 'state'],
    actions: [
      { m: 'action_allocate', l: 'Allocate', states: ['in_stock'] },
      { m: 'action_accept', l: 'Accept', states: ['in_service'] },
      { m: 'action_record_acceptance', l: 'Record Paper Acceptance', states: ['in_service'], ask: 'Signed acceptance form reference (required)', kwarg: 'reference' },
      { m: 'action_return', l: 'Return to Stock', states: ['in_service'] },
      { m: 'action_send_repair', l: 'Send to Repair', states: ['in_stock', 'in_service'] },
      { m: 'action_recover', l: 'Recover', states: ['repair', 'recovery_due'] },
      { m: 'action_retire', l: 'Record Write-off', states: ['in_stock', 'repair', 'recovery_due'], ask: 'Data-wipe certificate reference (required)', kwarg: 'wipe_certificate' },
      { m: 'action_approve_writeoff', l: 'Approve Write-off', states: ['in_stock', 'repair', 'recovery_due'] },
      { m: 'action_reject_writeoff', l: 'Refuse Write-off', states: ['in_stock', 'repair', 'recovery_due'], ask: 'Why is the write-off refused? (required)', kwarg: 'reason' }
    ] },
  'M66-lifecycle': { kind: 'table_report', module: 'M66', report: 'asset_lifecycle', title: 'Asset Lifecycle', period: false },
  'M66-mix': { kind: 'table_report', module: 'M66', report: 'category_mix', title: 'Ticket Category Mix', period: false },
  'M66-sla': { kind: 'table_report', module: 'M66', report: 'sla_report', title: 'ITSM Ticket SLA', period: false },

  /* Report chips */
  'M66-rpt-sla': { kind: 'table_report', module: 'M66', report: 'sla_report', title: 'ITSM Ticket SLA', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M66-form-ticket': {
    kind: 'model_form',
    model: 'fix.itsm.ticket',
    title: 'Incident / Service Request',
    back: 'M66-all',
    status: { field: 'state', labels: { new: 'New', assigned: 'Assigned', in_progress: 'In Progress', awaiting_user: 'Awaiting User', resolved: 'Resolved', closed: 'Closed', rejected: 'Rejected' } },
    tabs: [
      { id: 'ticket', label: '1. Ticket', bn: '১. টিকেট', icon: '🎫', badge: '9' },
      { id: 'links', label: '2. Links', bn: '২. সংযোগ', icon: '🔗', badge: '4' },
      { id: 'sla', label: '3. SLA & Outcome', bn: '৩. এসএলএ ও ফলাফল', icon: '⏱️', badge: '8' }
    ],
    sections: [
      { tab: 'ticket', title: 'Ticket', note: 'You raise it for yourself; the desk fills in the rest. Impact and urgency set the priority. A ticket on a catalogue item that requires approval waits for the approver before anyone works it.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'ticket_type', label: 'Ticket Type' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'impact', label: 'Impact' },
          { name: 'urgency', label: 'Urgency' },
          { name: 'priority', label: 'Priority' },
          { name: 'requester_id', label: 'Requester' },
          { name: 'catalogue_id', label: 'Catalogue Item' },
          { name: 'description', type: 'text', required: true, label: 'Description' }
        ] },
      { tab: 'links', title: 'Links', note: 'The problem behind this incident, the configuration item it touches and the change that caused it.',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'problem_id', label: 'Problem' },
          { name: 'ci_id', label: 'Configuration Item' },
          { name: 'caused_by_change_id', label: 'Caused By Change' }
        ] },
      { tab: 'sla', title: 'SLA & Outcome', note: 'Assign, Start, Await User, Resolve, Close and Reopen move the ticket from the list. Awaiting the user pauses the clock.',
        fields: [
          { name: 'assigned_to', label: 'Assigned To' },
          { name: 'sla_deadline', label: 'SLA Deadline' },
          { name: 'sla_paused_hours', label: 'SLA Paused (hours)' },
          { name: 'escalation_level', label: 'Escalation Tier' },
          { name: 'major_incident', label: 'Major Incident' },
          { name: 'major_incident_manager_id', label: 'Major Incident Manager' },
          { name: 'resolution', type: 'text', label: 'Resolution' },
          { name: 'resolved_on', label: 'Resolved On' }
        ] }
    ]
  },

  'M66-form-change': {
    kind: 'model_form',
    model: 'fix.itsm.change',
    title: 'Change Request',
    back: 'M66-changes',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', implemented: 'Implemented', reviewed: 'Reviewed',
      rolled_back: 'Rolled Back', rejected: 'Rejected' } },
    tabs: [
      { id: 'change', label: '1. Change', bn: '১. পরিবর্তন', icon: '🔁', badge: '10' },
      { id: 'plans', label: '2. Plans', bn: '২. পরিকল্পনা', icon: '📋', badge: '3' },
      { id: 'scope', label: '3. Scope', bn: '৩. পরিধি', icon: '🧩', badge: '5' },
      { id: 'record', label: '4. Approval & Review', bn: '৪. অনুমোদন ও পর্যালোচনা', icon: '🧾', badge: '8' }
    ],
    sections: [
      { tab: 'change', title: 'Change', note: 'Draft → submit (routed by risk: a change that follows an authorised standard template is pre-approved, normal → Change Manager, emergency/high-risk → CAB) → approved → implemented → reviewed. Editing the approved terms voids the approval.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'change_type', required: true, label: 'Change Type' },
          { name: 'template_id', label: 'Standard Change Template' },
          { name: 'risk', required: true, label: 'Risk' },
          { name: 'risk_probability', required: true, label: 'Risk Probability' },
          { name: 'risk_impact', required: true, label: 'Risk Impact' },
          { name: 'requested_by_id', label: 'Requested By' },
          { name: 'implementer_id', label: 'Implementer' },
          { name: 'planned_on', required: true, label: 'Planned On' },
          { name: 'change_window_hours', label: 'Change Window (hours)' }
        ] },
      { tab: 'plans', title: 'Plans', note: 'A change carries its implementation, test and back-out plan before it can be approved (BRU-ITS-06).',
        fields: [
          { name: 'implementation_plan', type: 'text', label: 'Implementation Plan' },
          { name: 'test_plan', type: 'text', label: 'Test Plan' },
          { name: 'rollback_plan', type: 'text', label: 'Rollback Plan' }
        ] },
      { tab: 'scope', title: 'Scope', note: 'Linked configuration items set a risk floor and drive the collision check; a freeze window stops all but the emergency path.',
        fields: [
          { name: 'ci_ids', label: 'Configuration Items' },
          { name: 'asset_ids', label: 'Affected Assets' },
          { name: 'release_note', label: 'Release Note' },
          { name: 'risk_basis', label: 'Risk Basis' },
          { name: 'freeze_conflict', label: 'In Freeze Window' }
        ] },
      { tab: 'record', title: 'Approval & Review', note: 'Who decided and what the review found. The implementer does not write his own review.',
        fields: [
          { name: 'approved_by_id', label: 'Approved By' },
          { name: 'retro_approval_state', label: 'Retro Approval' },
          { name: 'emergency_reason', type: 'text', label: 'Emergency Reason' },
          { name: 'implemented_on', label: 'Implemented On' },
          { name: 'pir_due_on', label: 'PIR Due' },
          { name: 'pir_notes', type: 'text', label: 'Post-Implementation Review' },
          { name: 'pir_by_id', label: 'PIR By' },
          { name: 'rollback_reason', type: 'text', label: 'Rollback Reason' }
        ] }
    ]
  },

  'M66-form-template': {
    kind: 'model_form',
    model: 'fix.itsm.change.template',
    title: 'Standard Change Template',
    back: 'M66-templates',
    status: { field: 'state', labels: { draft: 'Draft', authorised: 'Authorised', retired: 'Retired' } },
    sections: [
      { title: 'Pre-Authorised Standard Change', note: 'A Change Manager or CAB member other than the author authorises it. A change that follows it to the letter needs no further approval; its risk is the floor under the change. Editing it after authorisation returns it to draft.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'risk_probability', required: true, label: 'Risk Probability (floor)' },
          { name: 'risk_impact', required: true, label: 'Risk Impact (floor)' },
          { name: 'max_window_hours', label: 'Maximum Window (hours)' },
          { name: 'implementation_plan', type: 'text', required: true, label: 'Implementation Plan' },
          { name: 'test_plan', type: 'text', required: true, label: 'Test Plan' },
          { name: 'rollback_plan', type: 'text', required: true, label: 'Rollback Plan' },
          { name: 'description', type: 'text', label: 'Description' }
        ] }
    ]
  },

  'M66-form-asset': {
    kind: 'model_form',
    model: 'fix.itsm.asset',
    title: 'IT Asset',
    back: 'M66-assets',
    status: { field: 'state', labels: {
      in_service: 'In Service', in_stock: 'In Stock', repair: 'Under Repair', recovery_due: 'Recovery Due', retired: 'Retired' } },
    tabs: [
      { id: 'asset', label: '1. Asset', bn: '১. সম্পদ', icon: '💻', badge: '7' },
      { id: 'life', label: '2. Custody & Write-off', bn: '২. হেফাজত ও অবলোপন', icon: '🧾', badge: '8' }
    ],
    sections: [
      { tab: 'asset', title: 'Asset', note: 'The asset tag is unique per company. The holder is typed only while the asset is in stock; after that Allocate, Return and Recover move it.',
        fields: [
          { name: 'name', required: true, label: 'Asset Name' },
          { name: 'asset_tag', required: true, label: 'Asset Tag' },
          { name: 'asset_kind', required: true, label: 'Kind' },
          { name: 'assigned_to_id', label: 'Assigned To' },
          { name: 'serial_no', label: 'Serial No' },
          { name: 'os_version', label: 'OS / Firmware' },
          { name: 'warranty_end', label: 'Warranty End' }
        ] },
      { tab: 'life', title: 'Custody & Write-off', note: 'The holder accepts the asset. A leaver blocks exit clearance until it is recovered or its write-off is approved. Retirement needs the certificate and a second person.',
        fields: [
          { name: 'acceptance_state', label: 'Acceptance' },
          { name: 'accepted_on', label: 'Accepted On' },
          { name: 'acceptance_ref', label: 'Acceptance Reference' },
          { name: 'recovery_from_id', label: 'Recover From' },
          { name: 'wipe_certificate', label: 'Wipe Certificate' },
          { name: 'wipe_document_id', label: 'M06 Certificate Document' },
          { name: 'writeoff_state', label: 'Write-off' },
          { name: 'writeoff_approved_by_id', label: 'Write-off Approved By' }
        ] }
    ]
  },

  'M66-form-seat': {
    kind: 'model_form',
    model: 'fix.itsm.licence.seat',
    title: 'Licence Seat',
    back: 'M66-seats',
    status: { field: 'state', labels: { active: 'Active', revoked: 'Revoked' } },
    sections: [
      { title: 'Licence Seat', note: 'One seat held by one person; the licence counts these. Seats are assigned from the licence list and revoked from this list.',
        fields: [
          { name: 'licence_id', label: 'Licence' },
          { name: 'employee_id', label: 'Employee' },
          { name: 'assigned_by_id', label: 'Assigned By' },
          { name: 'assigned_on', label: 'Assigned On' },
          { name: 'over_entitlement', label: 'Over Entitlement' },
          { name: 'revoked_on', label: 'Revoked On' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },

  'M66-form-exception': {
    kind: 'model_form',
    model: 'fix.itsm.licence.exception',
    title: 'Licence Compliance Exception',
    back: 'M66-exceptions',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed' } },
    sections: [
      { title: 'Licence Compliance Exception', note: 'Opened when use goes past the entitlement. It closes once the count is back inside it, and never by the person who created the installation (BRU-ITS-17).',
        fields: [
          { name: 'name', label: 'Exception' },
          { name: 'licence_id', label: 'Licence' },
          { name: 'seats_over', label: 'Seats Over' },
          { name: 'installer_id', label: 'Installed By' },
          { name: 'raised_on', label: 'Raised On' },
          { name: 'remediation_due', label: 'Remediate By' },
          { name: 'closure_note', type: 'text', label: 'Closure Note' },
          { name: 'closed_by_id', label: 'Closed By' }
        ] }
    ]
  },

  /* registry completion screens */
  'M66-catalogue': { kind: 'model_list', model: 'fix.itsm.catalogue', cols: ['code', 'name', 'category', 'fulfilment_team', 'target_hours', 'calendar_id', 'requires_approval', 'active'] },
  'M66-problems': { kind: 'model_list', model: 'fix.itsm.problem', stateField: 'state', cols: ['name', 'title', 'severity', 'owner_id', 'incident_count', 'fix_change_id', 'known_error', 'verify_until', 'state'], actions: [{ m: 'action_investigate', l: 'Investigate', states: ['open'] }, { m: 'action_known_error', l: 'Known Error', states: ['investigating'] }, { m: 'action_resolve', l: 'Resolve', states: ['investigating', 'known_error'] }, { m: 'action_verify', l: 'Start Verifying', states: ['resolved'] }, { m: 'action_close', l: 'Close', states: ['verifying'] }] },
  'M66-licences': { kind: 'model_list', model: 'fix.itsm.licence', stateField: 'state', cols: ['name', 'vendor', 'licence_type', 'seats_owned', 'seats_assigned', 'seats_declared', 'utilisation_pct', 'compliance_state', 'renewal_on', 'state'],
    actions: [
      { m: 'action_assign_seat', l: 'Assign Seat', ask: 'Employee: code or name', kwarg: 'employee' },
      { m: 'action_record_overuse', l: 'Record Over-use', ask: 'Employee on whose device it was found: code or name', kwarg: 'employee' }
    ] },
  'M66-seats': { kind: 'model_list', model: 'fix.itsm.licence.seat', create: false, stateField: 'state',
    cols: ['licence_id', 'employee_id', 'assigned_by_id', 'assigned_on', 'over_entitlement', 'revoked_on', 'state'],
    actions: [{ m: 'action_revoke', l: 'Revoke', states: ['active'] }] },
  'M66-exceptions': { kind: 'model_list', model: 'fix.itsm.licence.exception', create: false, stateField: 'state',
    cols: ['name', 'licence_id', 'seats_over', 'installer_id', 'raised_on', 'remediation_due', 'closed_by_id', 'state'],
    actions: [{ m: 'action_close_exception', l: 'Close', states: ['open'], ask: 'How was it remediated? (required)', kwarg: 'closure_note' }] },
  'M66-cmdb': { kind: 'model_list', model: 'fix.itsm.ci', cols: ['ci_key', 'name', 'ci_class', 'environment_id', 'criticality', 'support_hours', 'asset_id', 'life_status'] },
  'M66-onboard': { kind: 'model_list', model: 'fix.jml.event', create: false, stateField: 'state', cols: ['name', 'event_type', 'employee_id', 'user_id', 'role_id', 'effective_on', 'state'] },


  /* ===== registry completion forms ===== */
  'M66-form-catalogue': {
    kind: 'model_form',
    model: 'fix.itsm.catalogue',
    title: "Catalogue Item",
    back: 'M66-catalogue',
    sections: [
      { title: "Catalogue Item", note: "A service catalogue entry: what the service desk offers, who fulfils it and the target time. The target hours set each ticket's SLA deadline.",
        fields: [
          { name: 'code', required: true, label: "Catalogue Code" },
          { name: 'name', required: true, label: "Service Name" },
          { name: 'category', required: true, label: "Category" },
          { name: 'fulfilment_team', label: "Fulfilment Team" },
          { name: 'target_hours', label: "Target (hours)" },
          { name: 'calendar_id', label: "SLA Calendar" },
          { name: 'description', type: 'text', label: "Description" },
          { name: 'cost_per_request', label: "Cost per Request" },
          { name: 'requires_approval', label: "Requires Approval" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M66-form-problem': {
    kind: 'model_form',
    model: 'fix.itsm.problem',
    title: "IT Problem",
    back: 'M66-problems',
    status: { field: 'state', labels: { open: "Open", investigating: "Investigating", known_error: "Known Error", resolved: "Resolved", verifying: "Verifying", closed: "Closed" } },
    sections: [
      { title: "IT Problem", note: "A problem links recurring incidents to one root cause. A known error needs BOTH the root cause and the workaround, after investigating. It closes only on verified absence of recurrence (BRU-ITS-05).",
        fields: [
          { name: 'title', required: true, label: "Title" },
          { name: 'severity', required: true, label: "Severity" },
          { name: 'owner_id', label: "Problem Owner" },
          { name: 'opened_on', required: true, label: "Opened On" },
          { name: 'fix_change_id', label: "Fix Change" },
          { name: 'verify_until', label: "Verify Until" },
          { name: 'incident_count', label: "Incidents" },
          { name: 'description', type: 'text', label: "Description" },
          { name: 'root_cause', type: 'text', label: "Root Cause" },
          { name: 'workaround', type: 'text', label: "Workaround" }
        ] }
    ]
  },
  'M66-form-licence': {
    kind: 'model_form',
    model: 'fix.itsm.licence',
    title: "Software Licence",
    back: 'M66-licences',
    status: { field: 'state', labels: { active: "Active", expiring: "Expiring", expired: "Expired" } },
    sections: [
      { title: "Software Licence", note: "Seats assigned is counted from the seat records. A figure declared before they existed shows as unverified and still counts towards utilisation. Over-use opens a compliance exception (BRU-ITS-17). The status is computed from the renewal date.",
        fields: [
          { name: 'name', required: true, label: "Licence Name" },
          { name: 'vendor', required: true, label: "Vendor" },
          { name: 'licence_type', required: true, label: "Licence Type" },
          { name: 'seats_owned', required: true, label: "Seats Owned" },
          { name: 'seats_assigned', label: "Seats Assigned" },
          { name: 'seats_declared', label: "Seats Declared (unverified)" },
          { name: 'compliance_state', label: "Compliance" },
          { name: 'unit_cost', label: "Unit Cost" },
          { name: 'purchased_on', label: "Purchased On" },
          { name: 'renewal_on', label: "Renewal On" }
        ] }
    ]
  },
  'M66-form-ci': {
    kind: 'model_form',
    model: 'fix.itsm.ci',
    title: "Configuration Item",
    back: 'M66-cmdb',
    tabs: [
      { id: 'identity', label: '1. Identity & Class', bn: '১. পরিচয় ও শ্রেণি', icon: '🪪', badge: '5' },
      { id: 'context', label: '2. Environment & Dependencies', bn: '২. পরিবেশ ও নির্ভরতা', icon: '🧩', badge: '5' }
    ],
    sections: [
      { tab: 'identity', title: "Configuration Item", note: "A CMDB configuration item: its stable key, class and criticality. Nothing runs in service on a retired asset (M66-13).",
        fields: [
          { name: 'name', required: true, label: "CI Name" },
          { name: 'ci_key', required: true, label: "CI Key" },
          { name: 'ci_class', required: true, label: "CI Class" },
          { name: 'criticality', required: true, label: "Criticality" },
          { name: 'life_status', required: true, label: "Life Status" }
        ] },
      { tab: 'context', title: "Environment & Dependencies", note: "Where the CI runs, who owns it, what it depends on and the support window it carries.",
        fields: [
          { name: 'environment_id', label: "Environment" },
          { name: 'owner_id', label: "Owner" },
          { name: 'depends_on', label: "Depends On" },
          { name: 'support_hours', required: true, label: "Support Hours" },
          { name: 'asset_id', label: "Linked Asset" }
        ] }
    ]
  }

};

export const REPORT_ROUTES = {
  'M66:Ticket SLA Performance': 'M66-rpt-sla',
  'M66:Licence Utilisation': 'M66-licences',
  'M66:Asset Lifecycle Status': 'M66-lifecycle',
  'M66:ITSM Ticket SLA': 'M66-rpt-sla',
  'M66:Change Success Rate': 'M66-success',
  'M66:IT Asset Lifecycle': 'M66-lifecycle',
  'M66:Ticket Category Mix': 'M66-mix'
};

export const FORM_MODELS = {
  'M66:Incident': 'fix.itsm.ticket',
  'M66:Change': 'fix.itsm.change',
  'M66:Asset': 'fix.itsm.asset',
  'M66:Service Request': 'fix.itsm.ticket'
};

export const FORM_CHIPS = {
  'M66:Incident': 'M66-form-ticket',
  'M66:Change': 'M66-form-change',
  'M66:Asset': 'M66-form-asset',
  'M66:Service Request': 'M66-form-ticket',
  'M66:__by_model__': {
    'fix.itsm.change.template': 'M66-form-template',
    'fix.itsm.licence.seat': 'M66-form-seat',
    'fix.itsm.licence.exception': 'M66-form-exception',
    'fix.itsm.catalogue': 'M66-form-catalogue',
    'fix.itsm.problem': 'M66-form-problem',
    'fix.itsm.licence': 'M66-form-licence',
    'fix.itsm.ci': 'M66-form-ci',
    'fix.itsm.ticket': 'M66-form-ticket',
    'fix.itsm.change': 'M66-form-change',
    'fix.itsm.asset': 'M66-form-asset'
  },
  'M66:__by_screen__': {
    'M66-catalogue': 'M66-form-catalogue',
    'M66-problems': 'M66-form-problem',
    'M66-licences': 'M66-form-licence',
    'M66-cmdb': 'M66-form-ci',
    'M66-incidents': 'M66-form-ticket',
    'M66-requests': 'M66-form-ticket',
    'M66-all': 'M66-form-ticket',
    'M66-changes': 'M66-form-change',
    'M66-templates': 'M66-form-template',
    'M66-seats': 'M66-form-seat',
    'M66-exceptions': 'M66-form-exception',
    'M66-assets': 'M66-form-asset'
  }
};

export const CREATE = {
  M66: { screen: 'M66-form-ticket', model: 'fix.itsm.ticket', label: 'Incident' }
};
