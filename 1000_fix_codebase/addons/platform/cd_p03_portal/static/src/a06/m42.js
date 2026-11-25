/** @odoo-module **/
/* A06 · Supply Chain — M42 Supplier Relationship & Performance (v2 rebuild).
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 71.
 * The supplier register did not exist (the vendor portal module had no
 * models); this pass adds it with qualification → activation, scorecards,
 * CARs, reviews, risk and compliance screening.
 *
 * Capture audit 2026-11-15: page 2 Segmentation captured nothing (the segment
 * was typed on the profile although it sets the review cadence and the
 * qualification authority); page 5 Contracts & Price Lists captured a contract
 * DOCUMENT - no agreement, agreed price, price change or consignment terms
 * existed (FR-SRM2-021..024); pages 3, 4, 6 and 9 had a "+ New" but no chip
 * for the other records they list (activation, re-qualification, documents,
 * bank changes, reviews, screening), and the bank-change list sat on no page.
 * Every page now captures its own record: segment reviews a second person
 * applies, agreements put in force by an approver, agreed prices and governed
 * price changes (a PO above the agreed price is refused, BRU-SRM2-14),
 * role-based contacts, questionnaire templates with mandatory evidence, and
 * the profile's classification and risk tier (FR-SRM2-002/004/008, §10.1). */

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
      { id: 'M42-contacts', en: 'Supplier Contacts', bn: 'সরবরাহকারী যোগাযোগ', t: 'g' },
      { id: 'M42-segments', en: 'Segmentation', bn: 'সেগমেন্টেশন', t: 'g' },
      { id: 'M42-segment-reviews', en: 'Segment Reviews', bn: 'সেগমেন্ট পর্যালোচনা', t: 'g' },
      { id: 'M42-docs', en: 'Document Register', bn: 'নথি নিবন্ধন', t: 'g' },
      { id: 'M42-bank', en: 'Bank-Detail Changes', bn: 'ব্যাংক তথ্য পরিবর্তন', t: 'g' }
    ]},
    { en: 'Agreements & Prices', screens: [
      { id: 'M42-agreements', en: 'Supplier Agreements', bn: 'সরবরাহকারী চুক্তি', t: 'g' },
      { id: 'M42-prices', en: 'Agreed Price List', bn: 'সম্মত মূল্য তালিকা', t: 'g' },
      { id: 'M42-price-changes', en: 'Price Changes', bn: 'মূল্য পরিবর্তন', t: 'g' }
    ]},
    { en: 'Qualification', screens: [
      { id: 'M42-qualification', en: 'Qualification Workflow', bn: 'যোগ্যতা যাচাই', t: 'g' },
      { id: 'M42-questionnaires', en: 'Questionnaire Templates', bn: 'প্রশ্নাবলী টেমপ্লেট', t: 'g' },
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
  forms: ['Supplier Profile', 'Qualification Questionnaire', 'CAR', 'Risk Assessment',
    'Supplier Contact', 'Segment Review', 'Questionnaire Template', 'Activation Gate',
    'Re-Qualification', 'Supplier Document', 'Bank-Detail Change', 'Supplier Agreement',
    'Agreed Price', 'Price Change', 'Scorecard', 'Supplier Review', 'Compliance Screening'],
  cross: ['M33 party extension', 'M16 activation gate', 'P05 vendor portal', 'M40 brand class'],
  freg: { src: 71, sub: [
    /* FR-SRM2-001/002/004/005: the profile, its classification and risk tier, and its role-based contacts */
    ['1', 'Supplier Profiles', 9, { model: 'fix.supplier', cols: ['name', 'supplier_code', 'classification', 'category', 'status'], screens: ['M42-suppliers', 'M42-contacts'], reports: ['Supplier Scorecard League'], forms: ['Supplier Profile', 'Supplier Contact'] }],
    /* FR-SRM2-003: after onboarding the segment changes only through a review a second person approves */
    ['2', 'Segmentation', 6, { model: 'fix.supplier', cols: ['name', 'segment', 'risk_tier', 'buyer_id', 'status'], screens: ['M42-segments', 'M42-segment-reviews'], reports: ['Supplier Scorecard League'], forms: ['Segment Review'], create: 'M42-form-segment-review' }],
    /* FR-SRM2-008..015: questionnaire template -> qualification -> activation gate -> re-qualification */
    ['3', 'Qualification', 10, { model: 'fix.supplier.qualification', cols: ['name', 'supplier_id', 'stage', 'score', 'state'], screens: ['M42-qualification', 'M42-questionnaires', 'M42-gate', 'M42-requal'], reports: [], forms: ['Qualification Questionnaire', 'Questionnaire Template', 'Activation Gate', 'Re-Qualification'] }],
    /* FR-SRM2-016..018: the document register and controlled bank-detail changes */
    ['4', 'Documents & Validity', 8, { model: 'fix.supplier.document', cols: ['name', 'supplier_id', 'doc_type', 'valid_to', 'state'], screens: ['M42-docs', 'M42-bank'], reports: ['Contract Coverage'], forms: ['Supplier Document', 'Bank-Detail Change'] }],
    /* FR-SRM2-021..024: agreements (consignment terms included), agreed prices, governed price changes */
    ['5', 'Contracts & Price Lists', 7, { model: 'fix.supplier.agreement', cols: ['name', 'supplier_id', 'agreement_type', 'term_to', 'state'], screens: ['M42-agreements', 'M42-prices', 'M42-price-changes'], reports: ['Contract Coverage'], forms: ['Supplier Agreement', 'Agreed Price', 'Price Change'] }],
    ['6', 'Scorecards', 9, { model: 'fix.supplier.performance', cols: ['name', 'supplier_id', 'period', 'total_score', 'grade'], screens: ['M42-scorecards', 'M42-reviews'], reports: ['Supplier Scorecard League'], forms: ['Scorecard', 'Supplier Review'] }],
    ['7', 'Corrective Actions', 7, { model: 'fix.supplier.car', cols: ['name', 'supplier_id', 'issue', 'severity', 'state'], screens: ['M42-cars'], reports: ['CAR Closure Performance'], forms: ['CAR'] }],
    ['8', 'Risk Assessment', 9, { model: 'fix.supplier.risk', cols: ['name', 'supplier_id', 'risk_type', 'risk_score', 'band'], screens: ['M42-risk'], reports: ['Risk Heat Map'], forms: ['Risk Assessment'] }],
    ['9', 'Compliance Screening', 6, { model: 'fix.supplier.screening', cols: ['name', 'supplier_id', 'screening_type', 'result', 'screened_on'], screens: ['M42-screening'], reports: ['Compliance Screening Log'], forms: ['Compliance Screening'] }]
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
    cols: ['name', 'supplier_code', 'partner_id', 'classification', 'segment', 'risk_tier', 'residency', 'payment_block', 'status'],
    actions: [
      { m: 'action_suspend', l: 'Suspend', ask: 'Reason for suspending the supplier', kwarg: 'reason' },
      { m: 'action_block', l: 'Block (CFO / CEO)', ask: 'Reason for blocking the supplier', kwarg: 'reason' },
      { m: 'action_request_reinstatement', l: 'Request Reinstatement', ask: 'Why the supplier should be reinstated', kwarg: 'reason' },
      { m: 'action_approve_reinstatement', l: 'Approve Reinstatement (approver)' }
    ] },
  'M42-segments': { kind: 'model_list', model: 'fix.supplier',
    cols: ['name', 'segment', 'classification', 'risk_tier', 'category', 'status'],
    note: 'The segment sets the review cadence and the authority a qualification needs. After onboarding it changes only through an approved segment review.',
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

  'M42-contacts': { kind: 'model_list', model: 'fix.supplier.contact',
    cols: ['supplier_id', 'name', 'role', 'phone', 'email', 'active'],
    note: 'Who to call at each supplier, by role: commercial, logistics, quality, finance and escalation.' },
  'M42-segment-reviews': { kind: 'model_list', model: 'fix.supplier.segment.review', stateField: 'state',
    cols: ['name', 'supplier_id', 'from_segment', 'to_segment', 'criticality', 'proposed_by_id', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_propose', l: 'Propose' },
      { m: 'action_approve', l: 'Approve (second person)' },
      { m: 'action_reject', l: 'Reject', ask: 'Why the segment change is rejected', kwarg: 'reason' }
    ],
    note: 'A steward proposes the new segment with its basis (spend, criticality, risk); a Supplier Approver who did not propose it applies it to the supplier.' },
  'M42-questionnaires': { kind: 'model_list', model: 'fix.qualification.questionnaire',
    cols: ['name', 'spend_category', 'category_id', 'risk_tier', 'required_doc_types', 'pass_threshold', 'version', 'active'],
    note: 'Qualification templates per category and risk tier: the questions, the evidence that must be verified before approval, and a pass mark that never lowers the estate-wide threshold.' },
  'M42-agreements': { kind: 'model_list', model: 'fix.supplier.agreement', stateField: 'state',
    cols: ['name', 'supplier_id', 'agreement_type', 'reference', 'term_from', 'term_to', 'days_to_expiry', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_activate', l: 'Put in Force (approver)' },
      { m: 'action_terminate', l: 'Terminate', ask: 'Why the agreement is terminated', kwarg: 'reason' }
    ],
    note: 'An agreement is drafted with its signed copy and put in force by a Supplier Approver who did not draft it; its terms are then fixed. Reminders go out 90, 60 and 30 days before it ends, and it expires on its end date.' },
  'M42-prices': { kind: 'model_list', model: 'fix.supplier.price.list', stateField: 'state',
    cols: ['name', 'supplier_id', 'agreement_id', 'product_id', 'price', 'moq', 'lead_time_days', 'valid_from', 'valid_to', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (second person)' },
      { m: 'action_withdraw', l: 'Withdraw' }
    ],
    note: 'Agreed prices under an agreement in force. A purchase order above the approved price for its supplier and part is refused; the price moves only through an approved price change.' },
  'M42-price-changes': { kind: 'model_list', model: 'fix.supplier.price.change', stateField: 'state',
    cols: ['name', 'supplier_id', 'product_id', 'old_price', 'proposed_price', 'variance_pct', 'effective_from', 'requested_by_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit' },
      { m: 'action_approve', l: 'Approve (second person)' },
      { m: 'action_reject', l: 'Reject', ask: 'Why the price change is rejected', kwarg: 'reason' }
    ],
    note: 'A supplier price movement with its justification. Approval by someone other than the requester closes the old price the day before the change takes effect and opens the new one.' },

  /* Report chips -> their own computed pack */
  'M42-rpt-league': { kind: 'table_report', module: 'M42', report: 'scorecard_league', title: 'Supplier Scorecard League', period: false },
  'M42-rpt-car': { kind: 'table_report', module: 'M42', report: 'car_closure', title: 'CAR Closure Performance', period: false },
  'M42-rpt-heat': { kind: 'table_report', module: 'M42', report: 'risk_heat', title: 'Risk Heat Map', period: false },
  'M42-rpt-coverage': { kind: 'table_report', module: 'M42', report: 'contract_coverage', title: 'Contract Coverage', period: true },
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
      { title: 'Profile', note: 'One supplier record per partner. The status moves only by its actions: prospect → qualified (qualification approved) → active (activation gate, decided by a Supplier Approver) → suspended / blocked (blocking is the CFO or CEO\'s); a suspended or blocked supplier returns only through an approved reinstatement. Bank details change only through a confirmed bank-change request. Approved categories are read by the PO gate when it is switched on. The segment sets the review cadence. Residency decides the documents activation requires: a Bangladesh-registered supplier its trade licence, TIN and VAT registration; a foreign one its certificate of incorporation, home-country tax residency and bank letter. It must agree with the contact\'s country and changes only before activation.',
        fields: [
          { name: 'name', required: true, label: 'Supplier Name' },
          { name: 'partner_id', required: true, label: 'Contact Partner' },
          { name: 'classification', required: true, label: 'Classification' },
          { name: 'segment', required: true, label: 'Segment (after onboarding: by segment review)' },
          { name: 'risk_tier', label: 'Risk Tier' },
          /* decides the mandatory documents: BD trade licence, TIN and VAT, or a foreign
           * supplier's incorporation, tax residency and bank letter (12 Nov 2026) */
          { name: 'residency', required: true, label: 'Residency (decides mandatory documents)' },
          { name: 'category', label: 'Spend Category' },
          /* A06 P08: written by an approved qualification, never typed */
          { name: 'approved_category_ids', readonly: true, label: 'Approved Product Categories (from qualification)' },
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
      { title: 'Qualification', note: 'Stage walks documents → site audit → samples → finance → activation. A Supplier Approver who did not score or audit it approves a score at or above the threshold (whoever changes the score becomes its scorer and cannot approve it); approval moves the supplier to qualified, and the score is then final. A questionnaire template adds its mandatory evidence and pass mark; an authorised distributor also needs a verified brand authorisation.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'questionnaire_id', label: 'Questionnaire Template' },
          { name: 'stage', required: true, label: 'Stage' },
          { name: 'submitted_on', required: true, label: 'Submitted On' },
          { name: 'auditor_id', label: 'Auditor' },
          { name: 'score', label: 'Score (0–100)' },
          { name: 'category_ids', label: 'Categories Qualified For' },
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
  },

  'M42-form-contact': {
    kind: 'model_form',
    model: 'fix.supplier.contact',
    title: 'Supplier Contact',
    back: 'M42-contacts',
    sections: [
      { title: 'Contact', note: 'A phone number or an e-mail is required.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'name', required: true, label: 'Contact Person' },
          { name: 'role', required: true, label: 'Role' },
          { name: 'phone', label: 'Phone' },
          { name: 'email', label: 'E-mail' },
          { name: 'partner_id', label: 'Contact Record (Party Master)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M42-form-segment-review': {
    kind: 'model_form',
    model: 'fix.supplier.segment.review',
    title: 'Segment Review',
    back: 'M42-segment-reviews',
    status: { field: 'state', labels: {
      draft: 'Draft', proposed: 'Proposed', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Re-Segmentation', note: 'Record the proposed segment and its basis, then Propose on Segment Reviews. A Supplier Approver who did not propose it approves, which changes the supplier\'s segment and with it the review cadence and the qualification authority. A proposal cannot be edited; reject it and propose again.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'from_segment', readonly: true, label: 'Current Segment (at proposal)' },
          { name: 'to_segment', required: true, label: 'Proposed Segment' },
          { name: 'annual_spend', label: 'Annual Spend (BDT)' },
          { name: 'criticality', required: true, label: 'Criticality' },
          { name: 'risk_tier', label: 'Risk Tier' },
          { name: 'reason', type: 'text', required: true, label: 'Basis / Reason' },
          { name: 'proposed_by_id', readonly: true, label: 'Proposed By' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'reject_reason', readonly: true, label: 'Rejection Reason' }
        ] }
    ]
  },

  'M42-form-questionnaire': {
    kind: 'model_form',
    model: 'fix.qualification.questionnaire',
    title: 'Questionnaire Template',
    back: 'M42-questionnaires',
    sections: [
      { title: 'Template', note: 'Mandatory evidence lists document types (for example iso, insurance, brand_authorisation) the supplier must hold verified before a qualification on this template is approved. The pass mark only raises the estate-wide threshold.',
        fields: [
          { name: 'name', required: true, label: 'Template Name' },
          { name: 'spend_category', label: 'Spend Category' },
          { name: 'category_id', label: 'Product Category' },
          { name: 'risk_tier', label: 'Risk Tier' },
          { name: 'questions', type: 'text', required: true, label: 'Questions (one per line, with weight)' },
          { name: 'required_doc_types', label: 'Mandatory Evidence (document types)' },
          { name: 'pass_threshold', label: 'Pass Mark (0–100)' },
          { name: 'version', required: true, label: 'Version' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M42-form-agreement': {
    kind: 'model_form',
    model: 'fix.supplier.agreement',
    title: 'Supplier Agreement',
    back: 'M42-agreements',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'In Force', expired: 'Expired', terminated: 'Terminated' } },
    tabs: [
      { id: 'agreement', label: '1. Agreement & Term', bn: '১. চুক্তি ও মেয়াদ', icon: '📄', badge: '13' },
      { id: 'commercial', label: '2. Service & Commercial', bn: '২. সেবা ও বাণিজ্যিক শর্ত', icon: '💼', badge: '3' },
      { id: 'consignment', label: '3. Consignment Terms', bn: '৩. কনসাইনমেন্ট শর্ত', icon: '📦', badge: '7' }
    ],
    sections: [
      { tab: 'agreement', title: 'Agreement and Term', note: 'Draft the agreement with the uploaded signed copy. A Supplier Approver who did not draft it puts it in force; its terms are then fixed and a change is a new agreement.',
        fields: [
          { name: 'supplier_id', required: true, label: 'Supplier' },
          { name: 'agreement_type', required: true, label: 'Type' },
          { name: 'reference', required: true, label: 'Agreement Reference' },
          { name: 'term_from', required: true, label: 'Term From' },
          { name: 'term_to', required: true, label: 'Term To' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'committed_value', label: 'Committed Value' },
          { name: 'committed_volume', label: 'Committed Volume' },
          { name: 'notice_days', label: 'Notice Period (days)' },
          { name: 'renewal_mode', required: true, label: 'Renewal' },
          { name: 'file', type: 'binary', filename: 'file_filename', accept: '.pdf,.jpg,.jpeg,.png', label: 'Signed Agreement' },
          { name: 'file_filename', label: 'File Name' },
          { name: 'approved_by_id', readonly: true, label: 'Put in Force By' }
        ] },
      { tab: 'commercial', title: 'Service Levels, Penalties and Rebates',
        fields: [
          { name: 'service_levels', type: 'text', label: 'Service Levels' },
          { name: 'penalties', type: 'text', label: 'Penalties' },
          { name: 'rebate_terms', type: 'text', label: 'Rebate Terms' }
        ] },
      { tab: 'consignment', title: 'Consignment Terms (consignment agreements)', note: 'Required before a consignment agreement is put in force: these are the terms stock control enforces for the brand\'s consigned parts.',
        fields: [
          { name: 'parts_scope', type: 'text', label: 'Parts in Scope' },
          { name: 'valuation_basis', label: 'Valuation Basis' },
          { name: 'settlement_trigger', label: 'Settlement Trigger' },
          { name: 'settlement_cadence', label: 'Settlement Cadence' },
          { name: 'return_rights', type: 'text', label: 'Return Rights' },
          { name: 'reconciliation_frequency', label: 'Reconciliation Frequency' },
          { name: 'loss_liability', label: 'Liability for Loss or Damage' }
        ] }
    ]
  },

  'M42-form-price': {
    kind: 'model_form',
    model: 'fix.supplier.price.list',
    title: 'Agreed Price',
    back: 'M42-prices',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', withdrawn: 'Withdrawn' } },
    sections: [
      { title: 'Agreed Price', note: 'A price under an agreement in force. A Supplier Approver other than its preparer approves it; it then changes only through a price change. A purchase order above it is refused.',
        fields: [
          { name: 'agreement_id', required: true, label: 'Agreement (in force)', domain: [['state', '=', 'active']] },
          { name: 'product_id', required: true, label: 'Part' },
          { name: 'price', required: true, label: 'Agreed Unit Price' },
          { name: 'moq', label: 'Minimum Order Qty' },
          { name: 'lead_time_days', label: 'Lead Time (days)' },
          { name: 'volume_breaks', label: 'Volume Breaks' },
          { name: 'valid_from', required: true, label: 'Valid From' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
        ] }
    ]
  },

  'M42-form-price-change': {
    kind: 'model_form',
    model: 'fix.supplier.price.change',
    title: 'Price Change',
    back: 'M42-price-changes',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Price Change', note: 'Pick the approved price, the proposed price, the date it takes effect and the justification, then Submit on Price Changes. Someone other than the requester approves or rejects it.',
        fields: [
          { name: 'price_list_id', required: true, label: 'Agreed Price', domain: [['state', '=', 'approved']] },
          { name: 'proposed_price', required: true, label: 'Proposed Unit Price' },
          { name: 'effective_from', required: true, label: 'Takes Effect From' },
          { name: 'justification', type: 'text', required: true, label: 'Justification' },
          { name: 'old_price', readonly: true, label: 'Price at Submission' },
          { name: 'variance_pct', readonly: true, label: 'Variance %' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'decision_note', readonly: true, label: 'Rejection Reason' }
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
  'M42:Risk Assessment': 'fix.supplier.risk',
  'M42:Supplier Contact': 'fix.supplier.contact',
  'M42:Segment Review': 'fix.supplier.segment.review',
  'M42:Questionnaire Template': 'fix.qualification.questionnaire',
  'M42:Activation Gate': 'fix.supplier.activation',
  'M42:Re-Qualification': 'fix.supplier.requalification',
  'M42:Supplier Document': 'fix.supplier.document',
  'M42:Bank-Detail Change': 'fix.supplier.bank.change',
  'M42:Supplier Agreement': 'fix.supplier.agreement',
  'M42:Agreed Price': 'fix.supplier.price.list',
  'M42:Price Change': 'fix.supplier.price.change',
  'M42:Scorecard': 'fix.supplier.performance',
  'M42:Supplier Review': 'fix.supplier.review',
  'M42:Compliance Screening': 'fix.supplier.screening'
};

export const FORM_CHIPS = {
  'M42:Supplier Profile': 'M42-form-supplier',
  'M42:Qualification Questionnaire': 'M42-form-qualification',
  'M42:CAR': 'M42-form-car',
  'M42:Risk Assessment': 'M42-form-risk',
  'M42:Supplier Contact': 'M42-form-contact',
  'M42:Segment Review': 'M42-form-segment-review',
  'M42:Questionnaire Template': 'M42-form-questionnaire',
  'M42:Activation Gate': 'M42-form-activation',
  'M42:Re-Qualification': 'M42-form-requalification',
  'M42:Supplier Document': 'M42-form-document',
  'M42:Bank-Detail Change': 'M42-form-bank-change',
  'M42:Supplier Agreement': 'M42-form-agreement',
  'M42:Agreed Price': 'M42-form-price',
  'M42:Price Change': 'M42-form-price-change',
  'M42:Scorecard': 'M42-form-scorecard',
  'M42:Supplier Review': 'M42-form-review',
  'M42:Compliance Screening': 'M42-form-screening',
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
    'fix.supplier.screening': 'M42-form-screening',
    'fix.supplier.contact': 'M42-form-contact',
    'fix.supplier.segment.review': 'M42-form-segment-review',
    'fix.qualification.questionnaire': 'M42-form-questionnaire',
    'fix.supplier.agreement': 'M42-form-agreement',
    'fix.supplier.price.list': 'M42-form-price',
    'fix.supplier.price.change': 'M42-form-price-change'
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
    'M42-screening': 'M42-form-screening',
    'M42-contacts': 'M42-form-contact',
    'M42-segment-reviews': 'M42-form-segment-review',
    'M42-questionnaires': 'M42-form-questionnaire',
    'M42-agreements': 'M42-form-agreement',
    'M42-prices': 'M42-form-price',
    'M42-price-changes': 'M42-form-price-change'
  }
};

export const CREATE = {
  M42: { screen: 'M42-form-supplier', model: 'fix.supplier', label: 'Supplier Profile' }
};
