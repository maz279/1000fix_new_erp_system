/** @odoo-module **/
/* A06 · Supply Chain — M42 Supplier Relationship & Performance (v2 rebuild).
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 71.
 * The supplier register did not exist (the vendor portal module had no
 * models); this pass adds it with qualification → activation, scorecards,
 * CARs, reviews, risk and compliance screening. */

export const MODULE = {
  area: 'A06', code: 'M42', en: 'Supplier Relationship', title: 'M42 · Supplier Relationship',
  bn: 'সরবরাহকারী সম্পর্ক', icon: '🧑‍💼',
  desc: 'Supplier directory and segmentation, document validity, the qualification workflow and activation gate, re-qualification, weighted scorecards, corrective actions, review cycles, risk heat and sanctions/COI/ABAC screening.',
  kpis: [
    { l: 'Active Suppliers', m: 'active_suppliers' },
    { l: 'Qualifications Pending', m: 'qualified_pending' },
    { l: 'Docs Expiring (90d)', m: 'docs_expiring_90d' },
    { l: 'CARs Open', m: 'cars_open' },
    { l: 'High Risks', m: 'risk_high' },
    { l: 'Screening Flags', m: 'screening_flags' }
  ],
  groups: [
    { en: 'Register', screens: [
      { id: 'M42-suppliers', en: 'Supplier Directory', bn: 'সরবরাহকারী তালিকা', t: 'g' },
      { id: 'M42-segments', en: 'Segmentation', bn: 'সেগমেন্টেশন', t: 'g' },
      { id: 'M42-docs', en: 'Document Register', bn: 'নথি নিবন্ধন', t: 'g' },
      { id: 'M42-bank', en: 'Bank-Detail Changes', bn: 'ব্যাংক তথ্য পরিবর্তন', t: 'g' }
    ]},
    { en: 'Qualification', screens: [
      { id: 'M42-qualification', en: 'Qualification Workflow', bn: 'যোগ্যতা যাচাই', t: 'g' },
      { id: 'M42-gate', en: 'Activation Gate (M16)', bn: 'অ্যাক্টিভেশন গেট', t: 'g' },
      { id: 'M42-requal', en: 'Re-Qualification', bn: 'পুনঃযোগ্যতা', t: 'g' }
    ]},
    { en: 'Performance', screens: [
      { id: 'M42-scorecards', en: 'Scorecards', bn: 'স্কোরকার্ড', t: 'g' },
      { id: 'M42-cars', en: 'Corrective Actions', bn: 'সংশোধনমূলক ব্যবস্থা', t: 'g' },
      { id: 'M42-reviews', en: 'Review Cycles', bn: 'পর্যালোচনা', t: 'g' }
    ]},
    { en: 'Risk & Compliance', screens: [
      { id: 'M42-risk', en: 'Risk Assessment', bn: 'ঝুঁকি মূল্যায়ন', t: 'g' },
      { id: 'M42-screening', en: 'Sanctions / COI / ABAC', bn: 'কমপ্লায়েন্স স্ক্রিনিং', t: 'g' }
    ]}
  ],
  reports: ['Supplier Scorecard League', 'CAR Closure Performance', 'Risk Heat Map', 'Contract Coverage', 'Compliance Screening Log'],
  forms: ['Supplier Profile', 'Qualification Questionnaire', 'CAR', 'Risk Assessment'],
  cross: ['M33 party extension', 'M16 activation gate', 'P05 vendor portal', 'M40 brand class'],
  freg: { src: 71, sub: [
    ['1', 'Supplier Profiles', 9, { model: 'fix.supplier', cols: ['name', 'supplier_code', 'partner_id', 'category', 'status'], screens: ['M42-suppliers'], reports: ['Supplier Scorecard League'], forms: ['Supplier Profile'] }],
    ['2', 'Segmentation', 6, { model: 'fix.supplier', cols: ['name', 'segment', 'category', 'buyer_id', 'status'], screens: ['M42-segments'], reports: ['Supplier Scorecard League'], forms: [], create: false }],
    ['3', 'Qualification', 10, { model: 'fix.supplier.qualification', cols: ['name', 'supplier_id', 'stage', 'score', 'state'], screens: ['M42-qualification', 'M42-gate', 'M42-requal'], reports: [], forms: ['Qualification Questionnaire'] }],
    ['4', 'Documents & Validity', 8, { model: 'fix.supplier.document', cols: ['name', 'supplier_id', 'doc_type', 'valid_to', 'state'], screens: ['M42-docs'], reports: ['Contract Coverage'], forms: [] }],
    ['5', 'Contracts & Price Lists', 7, { model: 'fix.supplier.document', cols: ['name', 'supplier_id', 'number', 'valid_from', 'valid_to'], screens: ['M42-docs'], reports: ['Contract Coverage'], forms: [], domain: [['doc_type', '=', 'contract']] }],
    ['6', 'Scorecards', 9, { model: 'fix.supplier.performance', cols: ['name', 'supplier_id', 'period', 'total_score', 'grade'], screens: ['M42-scorecards', 'M42-reviews'], reports: ['Supplier Scorecard League'], forms: [] }],
    ['7', 'Corrective Actions', 7, { model: 'fix.supplier.car', cols: ['name', 'supplier_id', 'issue', 'severity', 'state'], screens: ['M42-cars'], reports: ['CAR Closure Performance'], forms: ['CAR'] }],
    ['8', 'Risk Assessment', 9, { model: 'fix.supplier.risk', cols: ['name', 'supplier_id', 'risk_type', 'risk_score', 'band'], screens: ['M42-risk'], reports: ['Risk Heat Map'], forms: ['Risk Assessment'] }],
    ['9', 'Compliance Screening', 6, { model: 'fix.supplier.screening', cols: ['name', 'supplier_id', 'screening_type', 'result', 'screened_on'], screens: ['M42-screening'], reports: ['Compliance Screening Log'], forms: [] }]
  ] }
};

export const SCREENS = {
  'M42-bank': { kind: 'model_list', model: 'fix.supplier.bank.change', stateField: 'state',
    cols: ['name', 'supplier_id', 'acc_number_masked', 'bank_id', 'proposed_by_id', 'confirmed_by_id', 'supplier_payment_block', 'state'],
    actions: [
      { m: 'action_propose', l: 'Propose (blocks payment)' },
      { m: 'action_confirm', l: 'Confirm (second person)' },
      { m: 'action_reject', l: 'Reject', ask: 'Why the bank-detail change is rejected', kwarg: 'reason' }
    ],
    note: 'Readable only by Supplier Stewards and Approvers. A proposal blocks payment to the supplier until a second person confirms or rejects it.' },
  'M42-suppliers': { kind: 'model_list', model: 'fix.supplier', stateField: 'status',
    cols: ['name', 'supplier_code', 'partner_id', 'segment', 'category', 'payment_block', 'status'],
    actions: [
      { m: 'action_suspend', l: 'Suspend', ask: 'Reason for suspending the supplier', kwarg: 'reason' },
      { m: 'action_block', l: 'Block (CFO / CEO)', ask: 'Reason for blocking the supplier', kwarg: 'reason' },
      { m: 'action_request_reinstatement', l: 'Request Reinstatement', ask: 'Why the supplier should be reinstated', kwarg: 'reason' },
      { m: 'action_approve_reinstatement', l: 'Approve Reinstatement (approver)' }
    ] },
  'M42-segments': { kind: 'model_list', model: 'fix.supplier',
    cols: ['name', 'segment', 'category', 'status'],
    actions: [
      { m: 'action_suspend', l: 'Suspend', ask: 'Reason for suspending the supplier', kwarg: 'reason' },
      { m: 'action_block', l: 'Block (CFO / CEO)', ask: 'Reason for blocking the supplier', kwarg: 'reason' },
      { m: 'action_request_reinstatement', l: 'Request Reinstatement', ask: 'Why the supplier should be reinstated', kwarg: 'reason' },
      { m: 'action_approve_reinstatement', l: 'Approve Reinstatement (approver)' }
    ] },
  'M42-docs': { kind: 'model_list', model: 'fix.supplier.document', stateField: 'state',
    cols: ['name', 'supplier_id', 'doc_type', 'number', 'valid_to', 'is_valid', 'verified_by_id', 'state'],
    actions: [{ m: 'action_verify', l: 'Verify (second person)' }] },
  'M42-qualification': { kind: 'model_list', model: 'fix.supplier.qualification', stateField: 'state',
    cols: ['name', 'supplier_id', 'stage', 'submitted_on', 'score', 'scored_by_id', 'state'],
    actions: [
      { m: 'action_start', l: 'Start Review' },
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject' }
    ] },
  'M42-gate': { kind: 'model_list', model: 'fix.supplier.activation', stateField: 'state',
    cols: ['name', 'supplier_id', 'qualification_id', 'activated_on', 'state', 'blocker'],
    actions: [{ m: 'action_activate', l: 'Activate Supplier' }] },
  'M42-requal': { kind: 'model_list', model: 'fix.supplier.requalification', stateField: 'state',
    cols: ['name', 'supplier_id', 'due_on', 'completed_on', 'outcome', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete' }] },
  'M42-scorecards': { kind: 'model_list', model: 'fix.supplier.performance', stateField: 'state',
    cols: ['name', 'supplier_id', 'period', 'total_score', 'grade', 'state'],
    actions: [
      { m: 'action_compute', l: 'Compute from PO / Receipts' },
      { m: 'action_publish', l: 'Publish' }
    ] },
  'M42-cars': { kind: 'model_list', model: 'fix.supplier.car', stateField: 'state',
    cols: ['name', 'supplier_id', 'issue', 'severity', 'due_date', 'is_overdue', 'actioned_by_id', 'state'],
    actions: [
      { m: 'action_action', l: 'Mark Actioned' },
      { m: 'action_close', l: 'Close CAR' }
    ] },
  'M42-reviews': { kind: 'model_list', model: 'fix.supplier.review', stateField: 'state',
    cols: ['name', 'supplier_id', 'review_type', 'review_date', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete Review' }] },
  'M42-risk': { kind: 'model_list', model: 'fix.supplier.risk', stateField: 'state',
    cols: ['name', 'supplier_id', 'risk_type', 'likelihood', 'impact', 'risk_score', 'band', 'state'],
    actions: [{ m: 'action_mitigate', l: 'Mitigate' }] },
  'M42-screening': { kind: 'model_list', model: 'fix.supplier.screening', stateField: 'state',
    cols: ['name', 'supplier_id', 'screening_type', 'result', 'screened_on', 'state'],
    actions: [
      { m: 'action_clear', l: 'Clear' },
      { m: 'action_flag', l: 'Flag' },
      { m: 'action_clear_hit', l: 'Clear Hit (approver; sanctions: CFO)', ask: 'Why the hit is a false positive (evidence reference)', kwarg: 'reason' }
    ] },

  /* Report chips -> their own computed pack */
  'M42-rpt-league': { kind: 'table_report', module: 'M42', report: 'scorecard_league', title: 'Supplier Scorecard League', period: false },
  'M42-rpt-car': { kind: 'table_report', module: 'M42', report: 'car_closure', title: 'CAR Closure Performance', period: false },
  'M42-rpt-heat': { kind: 'table_report', module: 'M42', report: 'risk_heat', title: 'Risk Heat Map', period: false },
  'M42-rpt-coverage': { kind: 'table_report', module: 'M42', report: 'contract_coverage', title: 'Contract Coverage', period: false },
  'M42-rpt-compliance': { kind: 'table_report', module: 'M42', report: 'compliance_log', title: 'Compliance Screening Log', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M42-form-bank-change': {
    kind: 'model_form',
    model: 'fix.supplier.bank.change',
    title: 'Bank-Detail Change',
    back: 'M42-bank',
    status: { field: 'state', labels: {
      draft: 'Draft', proposed: 'Proposed', confirmed: 'Confirmed', rejected: 'Rejected' } },
    sections: [
      { title: 'Proposed Account', note: 'A steward records the new account with the call-back verification and the evidence, then proposes it: payments to the supplier stop. A second steward or an approver confirms it, which makes it the approved payee account, or rejects it. A proposal cannot be edited; reject it and propose again.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'acc_number', required: true, label: 'New Account Number' },
          { name: 'bank_id', label: 'Bank' },
          { name: 'routing_number', label: 'BEFTN Routing Number (9 digits)' },
          { name: 'acc_holder_name', label: 'Account Holder' },
          { name: 'verification_ref', required: true, label: 'Call-Back Verification' },
          { name: 'evidence_ref', required: true, label: 'Evidence File Reference' },
          { name: 'proposed_by_id', readonly: true, label: 'Proposed By' },
          { name: 'confirmed_by_id', readonly: true, label: 'Confirmed By' },
          { name: 'supplier_payment_block', readonly: true, label: 'Payment Block' },
          { name: 'reject_reason', readonly: true, label: 'Rejection Reason' }
        ] }
    ]
  },

  'M42-form-supplier': {
    kind: 'model_form',
    model: 'fix.supplier',
    title: 'Supplier Profile',
    back: 'M42-suppliers',
    status: { field: 'status', labels: {
      prospect: 'Prospect', qualified: 'Qualified', active: 'Active',
      suspended: 'Suspended', deactivated: 'Deactivated (Blocked)' } },
    sections: [
      { title: 'Profile', note: 'One supplier record per partner. The status moves only by its actions: prospect → qualified (qualification approved) → active (activation gate, decided by a Supplier Approver) → suspended / blocked (blocking is the CFO or CEO\'s); a suspended or blocked supplier returns only through an approved reinstatement. Bank details change only through a confirmed bank-change request. Approved categories are read by the PO gate when it is switched on. The segment sets the review cadence.',
        fields: [
          { name: 'name', required: true, label: 'Supplier Name' },
          { name: 'partner_id', required: true, label: 'Contact Partner' },
          { name: 'segment', required: true, label: 'Segment' },
          { name: 'category', label: 'Spend Category' },
          { name: 'approved_category_ids', label: 'Approved Product Categories' },
          { name: 'buyer_id', label: 'Buyer' },
          { name: 'onboarded_on', label: 'Onboarded On' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M42-form-document': {
    kind: 'model_form',
    model: 'fix.supplier.document',
    title: 'Supplier Document',
    back: 'M42-docs',
    status: { field: 'state', labels: {
      valid: 'Valid', pending: 'Pending', expired: 'Expired' } },
    sections: [
      { title: 'Document', note: 'A document becomes valid only when a second user verifies it against its number and the uploaded file (Verify). Changing it or its file afterwards returns it to pending; an expired end date makes it invalid and suspends an active supplier.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'doc_type', required: true, label: 'Document Type' },
          { name: 'number', label: 'Document Number' },
          { name: 'valid_from', label: 'Valid From' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'file', type: 'binary', filename: 'file_filename', accept: '.pdf,.jpg,.jpeg,.png', label: 'Document File' },
          { name: 'file_filename', label: 'File Name' },
          { name: 'file_ref', label: 'Paper File Reference (optional)' }
        ] }
    ]
  },

  'M42-form-qualification': {
    kind: 'model_form',
    model: 'fix.supplier.qualification',
    title: 'Qualification Questionnaire',
    back: 'M42-qualification',
    status: { field: 'state', labels: {
      draft: 'Draft', in_review: 'In Review', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Qualification', note: 'Stage walks documents → site audit → samples → finance → activation. A Supplier Approver who did not score or audit it approves a score at or above the threshold (whoever changes the score becomes its scorer and cannot approve it); approval moves the supplier to qualified, and the score is then final.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'stage', required: true, label: 'Stage' },
          { name: 'submitted_on', required: true, label: 'Submitted On' },
          { name: 'auditor_id', label: 'Auditor' },
          { name: 'score', label: 'Score (0–100)' },
          { name: 'scored_by_id', readonly: true, label: 'Scored By' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M42-form-activation': {
    kind: 'model_form',
    model: 'fix.supplier.activation',
    title: 'Activation Gate',
    back: 'M42-gate',
    status: { field: 'state', labels: {
      draft: 'Draft', activated: 'Activated', blocked: 'Blocked' } },
    sections: [
      { title: 'Gate', note: 'Activation requires an approved qualification of this supplier, verified unexpired trade licence, TIN and VAT documents, a cleared screening of every required type (sanctions, conflict of interest and anti-bribery by default), no unresolved screening hit and no critical open risk; a Supplier Approver other than the preparer activates.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'qualification_id', label: 'Qualification', domain: [['state', '=', 'approved']] }
        ] }
    ]
  },

  'M42-form-requalification': {
    kind: 'model_form',
    model: 'fix.supplier.requalification',
    title: 'Re-Qualification',
    back: 'M42-requal',
    status: { field: 'state', labels: {
      due: 'Due', scheduled: 'Scheduled', done: 'Done' } },
    sections: [
      { title: 'Re-Qualification', note: 'Completing needs a recorded outcome (pass / conditional / fail).',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'due_on', required: true, label: 'Due On' },
          { name: 'outcome', label: 'Outcome' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M42-form-scorecard': {
    kind: 'model_form',
    model: 'fix.supplier.performance',
    title: 'Scorecard',
    back: 'M42-scorecards',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published' } },
    sections: [
      { title: 'Scorecard', note: 'Compute fills quality (accepted / received at inspection), delivery (receipts on or before the confirmed date), cost (lines at or below the previous price) and responsiveness (POs acknowledged within the SLA) from the month\'s POs and receipts; components with no data are excluded. Total = quality 35% + delivery 30% + cost 20% + responsiveness 15%; grade A ≥85 / B ≥70 / C ≥55 / D. Published cards are final; two D grades in a row raise a CAR.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'quality_score', readonly: true, label: 'Quality' },
          { name: 'delivery_score', readonly: true, label: 'Delivery' },
          { name: 'cost_score', readonly: true, label: 'Cost' },
          { name: 'responsiveness_score', readonly: true, label: 'Responsiveness' },
          { name: 'reviewed_on', required: true, label: 'Reviewed On' }
        ] }
    ]
  },

  'M42-form-car': {
    kind: 'model_form',
    model: 'fix.supplier.car',
    title: 'CAR',
    back: 'M42-cars',
    status: { field: 'state', labels: {
      open: 'Open', actioned: 'Actioned', closed: 'Closed' } },
    sections: [
      { title: 'Corrective Action', note: 'Marking actioned needs the action plan; closing (verification) is done by someone other than the raiser and the person who actioned it. Overdue is computed against today.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'issue', required: true, label: 'Issue' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'raised_on', required: true, label: 'Raised On' },
          { name: 'due_date', required: true, label: 'Due Date' },
          { name: 'root_cause', type: 'text', label: 'Root Cause' },
          { name: 'action_plan', type: 'text', label: 'Action Plan' }
        ] }
    ]
  },

  'M42-form-review': {
    kind: 'model_form',
    model: 'fix.supplier.review',
    title: 'Supplier Review',
    back: 'M42-reviews',
    status: { field: 'state', labels: { scheduled: 'Scheduled', done: 'Done' } },
    sections: [
      { title: 'Review', fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'review_type', required: true, label: 'Type' },
          { name: 'review_date', required: true, label: 'Review Date' },
          { name: 'attendees', label: 'Attendees' },
          { name: 'outcomes', type: 'text', label: 'Outcomes' }
        ] }
    ]
  },

  'M42-form-risk': {
    kind: 'model_form',
    model: 'fix.supplier.risk',
    title: 'Risk Assessment',
    back: 'M42-risk',
    status: { field: 'state', labels: { open: 'Open', mitigated: 'Mitigated' } },
    sections: [
      { title: 'Risk', note: 'Score = likelihood × impact (1–5 each); band critical ≥20, high ≥12, medium ≥6.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'risk_type', required: true, label: 'Risk Type' },
          { name: 'likelihood', label: 'Likelihood (1–5)' },
          { name: 'impact', label: 'Impact (1–5)' },
          { name: 'assessed_on', required: true, label: 'Assessed On' },
          { name: 'mitigation', type: 'text', label: 'Mitigation' }
        ] }
    ]
  },

  'M42-form-screening': {
    kind: 'model_form',
    model: 'fix.supplier.screening',
    title: 'Compliance Screening',
    back: 'M42-screening',
    status: { field: 'state', labels: {
      pending: 'Pending', cleared: 'Cleared', flagged: 'Flagged' } },
    sections: [
      { title: 'Screening', note: 'A recorded hit is never rewritten: flagging a sanctions hit blocks the supplier, any other hit suspends an active one. A Supplier Approver other than the recorder clears a hit with the reason; a sanctions hit takes the CFO or CEO, and a blocked supplier then still needs an approved reinstatement.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'screening_type', required: true, label: 'Screening Type' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'screened_on', required: true, label: 'Screened On' },
          { name: 'reference', label: 'Reference' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M42:Supplier Scorecard League': 'M42-rpt-league',
  'M42:CAR Closure Performance': 'M42-rpt-car',
  'M42:Risk Heat Map': 'M42-rpt-heat',
  'M42:Contract Coverage': 'M42-rpt-coverage',
  'M42:Compliance Screening Log': 'M42-rpt-compliance'
};

export const FORM_MODELS = {
  'M42:Supplier Profile': 'fix.supplier',
  'M42:Qualification Questionnaire': 'fix.supplier.qualification',
  'M42:CAR': 'fix.supplier.car',
  'M42:Risk Assessment': 'fix.supplier.risk'
};

export const FORM_CHIPS = {
  'M42:Supplier Profile': 'M42-form-supplier',
  'M42:Qualification Questionnaire': 'M42-form-qualification',
  'M42:CAR': 'M42-form-car',
  'M42:Risk Assessment': 'M42-form-risk',
  'M42:__by_model__': {
    'fix.supplier.bank.change': 'M42-form-bank-change',
    'fix.supplier': 'M42-form-supplier',
    'fix.supplier.document': 'M42-form-document',
    'fix.supplier.qualification': 'M42-form-qualification',
    'fix.supplier.activation': 'M42-form-activation',
    'fix.supplier.requalification': 'M42-form-requalification',
    'fix.supplier.performance': 'M42-form-scorecard',
    'fix.supplier.car': 'M42-form-car',
    'fix.supplier.review': 'M42-form-review',
    'fix.supplier.risk': 'M42-form-risk',
    'fix.supplier.screening': 'M42-form-screening'
  },
  'M42:__by_screen__': {
    'M42-suppliers': 'M42-form-supplier',
    'M42-segments': 'M42-form-supplier',
    'M42-docs': 'M42-form-document',
    'M42-bank': 'M42-form-bank-change',
    'M42-qualification': 'M42-form-qualification',
    'M42-gate': 'M42-form-activation',
    'M42-requal': 'M42-form-requalification',
    'M42-scorecards': 'M42-form-scorecard',
    'M42-cars': 'M42-form-car',
    'M42-reviews': 'M42-form-review',
    'M42-risk': 'M42-form-risk',
    'M42-screening': 'M42-form-screening'
  }
};

export const CREATE = {
  M42: { screen: 'M42-form-supplier', model: 'fix.supplier', label: 'Supplier Profile' }
};
