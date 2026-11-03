/** @odoo-module **/
/* A12 · M66 Internal IT Service Management. 3 groups / 8 screens / 4 reports / 4 forms / freg 52. */

export const MODULE = {
  area: 'A12', code: 'M66', en: 'Internal IT Service Management', title: 'M66 · Internal IT Service Management',
  bn: 'আইটি সার্ভিস', icon: '🖥️',
  desc: 'Internal ITSM tickets (incidents and service requests), IT change management with approval and rollback, the internal IT asset register with lifecycle and warranty, and category/SLA analytics.',
  kpis: [
    { l: 'Tickets Open', m: 'tickets_open' },
    { l: 'Tickets Total', m: 'tickets_total' },
    { l: 'Changes Pending', m: 'changes_pending' },
    { l: 'Assets In Service', m: 'assets_in_service' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M66-catalogue', en: 'Service Catalogue', bn: 'Service Catalogue', t: 'g' },
      { id: 'M66-problems', en: 'Problems', bn: 'Problems', t: 'g' },
      { id: 'M66-licences', en: 'Licences & Subscriptions', bn: 'Licences & Subscriptions', t: 'g' },
      { id: 'M66-cmdb', en: 'CMDB', bn: 'CMDB', t: 'g' },
      { id: 'M66-onboard', en: 'Onboard/Offboard Workflows', bn: 'Onboard/Offboard Workflows', t: 'g' }
    ]},
    { en: 'Service Desk', screens: [
      { id: 'M66-incidents', en: 'Incidents', bn: 'ইনসিডেন্ট', t: 'g' },
      { id: 'M66-requests', en: 'Service Requests', bn: 'সার্ভিস রিকোয়েস্ট', t: 'g' },
      { id: 'M66-all', en: 'All Tickets', bn: 'সব টিকেট', t: 'g' }
    ]},
    { en: 'Change', screens: [
      { id: 'M66-changes', en: 'Changes', bn: 'চেঞ্জ', t: 'g' },
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
  cross: ['M29 identity/access', 'M28 connectors', 'M67 project changes'],
  freg: { src: 52, sub: [
    ['1', 'Service Desk', 12, { model: 'fix.itsm.ticket', cols: ['name', 'title', 'category', 'priority', 'state'], screens: ['M66-incidents', 'M66-requests', 'M66-catalogue'] }],
    ['2', 'Change Management', 10, { model: 'fix.itsm.change', cols: ['name', 'title', 'change_type', 'risk', 'state'], screens: ['M66-changes', 'M66-success'] }],
    ['3', 'Asset Register', 9, { model: 'fix.itsm.asset', cols: ['name', 'asset_tag', 'asset_kind', 'assigned_to_id', 'state'], screens: ['M66-assets', 'M66-lifecycle', 'M66-cmdb'] }],
    ['4', 'Knowledge', 6, { model: 'fix.itsm.problem', cols: ['name', 'title', 'severity', 'known_error', 'state'], screens: ['M66-problems'] }],
    ['5', 'Analytics', 8, { model: 'fix.itsm.ticket', cols: ['category', 'priority', 'state', 'assigned_to', 'create_date'], screens: ['M66-mix', 'M66-all'] }],
    ['6', 'Audit', 7, { model: 'fix.jml.event', cols: ['name', 'event_type', 'user_id', 'effective_on', 'state'], screens: ['M66-onboard', 'M66-licences'] }]
  ] }
};

export const SCREENS = {
  'M66-incidents': { kind: 'model_list', model: 'fix.itsm.ticket', stateField: 'state',
    cols: ['name', 'title', 'category', 'priority', 'requester_id', 'state'],
    actions: [{ m: 'action_resolve', l: 'Resolve' }] },
  'M66-requests': { kind: 'model_list', model: 'fix.itsm.ticket', stateField: 'state',
    cols: ['name', 'title', 'category', 'requester_id', 'state'] },
  'M66-all': { kind: 'model_list', model: 'fix.itsm.ticket', stateField: 'state',
    cols: ['name', 'title', 'category', 'priority', 'requester_id', 'state'],
    actions: [{ m: 'action_resolve', l: 'Resolve' }] },
  'M66-changes': { kind: 'model_list', model: 'fix.itsm.change', stateField: 'state',
    cols: ['name', 'title', 'change_type', 'risk', 'requested_by_id', 'planned_on', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }, { m: 'action_implement', l: 'Implement' },
              { m: 'action_rollback', l: 'Roll Back' }] },
  'M66-success': { kind: 'table_report', module: 'M66', report: 'change_success', title: 'Change Success Rate', period: false },
  'M66-assets': { kind: 'model_list', model: 'fix.itsm.asset', stateField: 'state',
    cols: ['name', 'asset_tag', 'asset_kind', 'assigned_to_id', 'warranty_end', 'state'] },
  'M66-lifecycle': { kind: 'table_report', module: 'M66', report: 'asset_lifecycle', title: 'Asset Lifecycle', period: false },
  'M66-mix': { kind: 'table_report', module: 'M66', report: 'category_mix', title: 'Ticket Category Mix', period: false },

  /* Report chips */
  'M66-rpt-sla': { kind: 'table_report', module: 'M66', report: 'sla_report', title: 'ITSM Ticket SLA', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M66-form-ticket': {
    kind: 'model_form',
    model: 'fix.itsm.ticket',
    title: 'Incident / Service Request',
    back: 'M66-all',
    status: { field: 'state', labels: { new: 'New', open: 'Open', resolved: 'Resolved', closed: 'Closed' } },
    sections: [
      { title: 'Ticket', note: 'The requester is an employee; resolution stamps the closure note. Category mix and SLA reports read these rows.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'priority', required: true, label: 'Priority' },
          { name: 'requester_id', required: true, label: 'Requester' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M66-form-change': {
    kind: 'model_form',
    model: 'fix.itsm.change',
    title: 'Change Request',
    back: 'M66-changes',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', implemented: 'Implemented',
      rolled_back: 'Rolled Back', rejected: 'Rejected' } },
    sections: [
      { title: 'Change', note: 'Draft → approved → implemented (→ rolled back). The rollback plan is required reading before implementation.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'change_type', required: true, label: 'Change Type' },
          { name: 'risk', required: true, label: 'Risk' },
          { name: 'requested_by_id', label: 'Requested By' },
          { name: 'planned_on', required: true, label: 'Planned On' },
          { name: 'change_window_hours', label: 'Change Window (hours)' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Rollback Plan', fields: [
          { name: 'rollback_plan', type: 'text', label: 'Rollback Plan' }
        ] }
    ]
  },

  'M66-form-asset': {
    kind: 'model_form',
    model: 'fix.itsm.asset',
    title: 'IT Asset',
    back: 'M66-assets',
    status: { field: 'state', labels: {
      in_service: 'In Service', in_stock: 'In Stock', repair: 'Under Repair', retired: 'Retired' } },
    sections: [
      { title: 'Asset', note: 'The asset tag is unique per company (database UNIQUE).',
        fields: [
          { name: 'name', required: true, label: 'Asset Name' },
          { name: 'asset_tag', required: true, label: 'Asset Tag' },
          { name: 'asset_kind', required: true, label: 'Kind' },
          { name: 'assigned_to_id', label: 'Assigned To' },
          { name: 'serial_no', label: 'Serial No' },
          { name: 'os_version', label: 'OS / Firmware' },
          { name: 'warranty_end', label: 'Warranty End' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  /* registry completion screens */
  'M66-catalogue': { kind: 'model_list', model: 'fix.itsm.catalogue', cols: ['code', 'name', 'category', 'fulfilment_team', 'target_hours', 'requires_approval', 'active'] },
  'M66-problems': { kind: 'model_list', model: 'fix.itsm.problem', stateField: 'state', cols: ['name', 'title', 'severity', 'owner_id', 'known_error', 'state'], actions: [{ m: 'action_known_error', l: 'Known Error' }, { m: 'action_resolve', l: 'Resolve' }, { m: 'action_close', l: 'Close' }] },
  'M66-licences': { kind: 'model_list', model: 'fix.itsm.licence', stateField: 'state', cols: ['name', 'vendor', 'licence_type', 'seats_owned', 'seats_assigned', 'utilisation_pct', 'renewal_on', 'state'] },
  'M66-cmdb': { kind: 'model_list', model: 'fix.itsm.ci', cols: ['ci_key', 'name', 'ci_class', 'environment_id', 'criticality', 'support_hours', 'life_status'] },
  'M66-onboard': { kind: 'model_list', model: 'fix.jml.event', create: false, stateField: 'state', cols: ['name', 'event_type', 'employee_id', 'user_id', 'role_id', 'effective_on', 'state'] },


  /* ===== registry completion forms ===== */
  'M66-form-catalogue': {
    kind: 'model_form',
    model: 'fix.itsm.catalogue',
    title: "Catalogue Item",
    back: 'M66-catalogue',
    sections: [
      { title: "Catalogue Item", note: "A service catalogue entry: what the service desk offers, who fulfils it and the target time. Approval requirement decides if a request needs a manager.",
        fields: [
          { name: 'code', required: true, label: "Catalogue Code" },
          { name: 'name', required: true, label: "Service Name" },
          { name: 'category', required: true, label: "Category" },
          { name: 'fulfilment_team', label: "Fulfilment Team" },
          { name: 'target_hours', label: "Target (hours)" },
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
    status: { field: 'state', labels: { open: "Open", investigating: "Investigating", known_error: "Known Error", resolved: "Resolved", closed: "Closed" } },
    sections: [
      { title: "IT Problem", note: "A problem links recurring incidents to one root cause. Declaring a known error requires the root cause to be written first.",
        fields: [
          { name: 'title', required: true, label: "Title" },
          { name: 'severity', required: true, label: "Severity" },
          { name: 'owner_id', label: "Problem Owner" },
          { name: 'opened_on', required: true, label: "Opened On" },
          { name: 'state', required: true, label: "State" }
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
      { title: "Software Licence", note: "Seats owned vs assigned gives the utilisation. Annual cost is computed from the licence type, seats and unit cost.",
        fields: [
          { name: 'name', required: true, label: "Licence Name" },
          { name: 'vendor', required: true, label: "Vendor" },
          { name: 'licence_type', required: true, label: "Licence Type" },
          { name: 'seats_owned', required: true, label: "Seats Owned" },
          { name: 'seats_assigned', label: "Seats Assigned" },
          { name: 'unit_cost', label: "Unit Cost" },
          { name: 'purchased_on', label: "Purchased On" },
          { name: 'renewal_on', label: "Renewal On" },
          { name: 'state', required: true, label: "State" }
        ] }
    ]
  },
  'M66-form-ci': {
    kind: 'model_form',
    model: 'fix.itsm.ci',
    title: "Configuration Item",
    back: 'M66-cmdb',
    sections: [
      { title: "Configuration Item", note: "A CMDB configuration item: its stable key, class, environment and what it depends on. Criticality and support hours drive incident priority.",
        fields: [
          { name: 'name', required: true, label: "CI Name" },
          { name: 'ci_key', required: true, label: "CI Key" },
          { name: 'ci_class', required: true, label: "CI Class" },
          { name: 'environment_id', label: "Environment" },
          { name: 'owner_id', label: "Owner" },
          { name: 'depends_on', label: "Depends On" },
          { name: 'criticality', required: true, label: "Criticality" },
          { name: 'support_hours', required: true, label: "Support Hours" },
          { name: 'life_status', required: true, label: "Life Status" },
          { name: 'asset_id', label: "Linked Asset" }
        ] }
    ]
  },

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
    'M66-assets': 'M66-form-asset'
  }
};

export const CREATE = {
  M66: { screen: 'M66-form-ticket', model: 'fix.itsm.ticket', label: 'Incident' }
};
