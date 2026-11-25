/** @odoo-module **/
/* A03 · Customer Experience — M33 Customer & Party Master.
 * This fragment mirrors the CANONICAL registry M33 exactly: 7 groups,
 * 20 screens, 6 KPIs, 6 reports, 7 forms, freg src 100 in 12 subs.
 * (Was 5 groups / 15 screens / 5 forms before the A03 gap-closure build of
 * 2026-11-02 added the S8 'Duplicate Detection Jobs' group and its form.)
 *
 * Upgraded 2026-10-31: Full Microsoft Dynamics 365 multi-tab layout across
 * all 14 in-workspace forms with zero Bengali/English mixing, comprehensive
 * data capture, and strict compliance with Bangladesh PDPA & statutory rules.
 */

export const MODULE = {
  area: 'A03', code: 'M33', en: 'Customer & Party Master', title: 'M33 · Customer & Party Master',
  bn: 'গ্রাহক মাস্টার', icon: '🪪',
  desc: 'Single golden record for every party — roles, hierarchies, OTP verification, consent, segments, credit.',
  kpis: [
    { l: 'Active Customers', m: 'active_customers' },
    { l: 'Duplicate Rate', m: 'duplicate_rate', suffix: '%' },
    { l: 'Golden Coverage', m: 'golden_coverage', suffix: '%' },
    { l: 'Consent Current', m: 'consent_current', suffix: '%' },
    { l: 'Credit Holds', m: 'credit_holds' },
    { l: 'New Today', m: 'new_today' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M33-dedup-rule', en: "Dedup Rule", bn: "ডুপ্লিকেট রুল", t: 'g' },
      { id: 'M33-transparency-notice', en: "Transparency Notice", bn: "স্বচ্ছতা নোটিশ", t: 'g' }
    ]},
    { en: 'Party Records', screens: [
      { id: 'M33-directory', en: 'Party Directory', bn: 'পার্টি ডিরেক্টরি', t: 'g' },
      { id: 'M33-form-party', en: 'Party Master Record', bn: 'পার্টি রেকর্ড ফর্ম', t: 'f' },
      { id: 'M33-party', en: 'Party Record (roles)', bn: 'পার্টি রোল', t: 'g' },
      { id: 'M33-360', en: 'Customer 360', bn: 'কাস্টমার ৩৬০', t: 'r' },
      { id: 'M33-hierarchy', en: 'Account Hierarchies', bn: 'অ্যাকাউন্ট স্তর', t: 'g' },
      { id: 'M33-addresses', en: 'Party Addresses (BD + GPS)', bn: 'পার্টির ঠিকানা', t: 'g' },
      { id: 'M33-form-classify', en: 'Classify a Party', bn: 'পার্টি শ্রেণিবিন্যাস', t: 'f' },
      { id: 'M33-contact-points', en: 'Contact Points', bn: 'যোগাযোগ পয়েন্ট', t: 'g' },
      { id: 'M33-relationships', en: 'Party Relationships', bn: 'পার্টি সম্পর্ক', t: 'g' },
      { id: 'M33-contact-roles', en: 'Corporate Contact Roles', bn: 'কর্পোরেট যোগাযোগ ভূমিকা', t: 'g' },
      { id: 'M33-form-contact-limit', en: 'Corporate Contact Limit', bn: 'কর্পোরেট যোগাযোগ সীমা', t: 'f' }
    ]},
    { en: 'Identity & Verification', screens: [
      { id: 'M33-identity', en: 'Identity Documents (NID/BIN)', bn: 'পরিচয়পত্র', t: 'g' },
      { id: 'M33-otp', en: 'OTP Verification Log', bn: 'ওটিপি যাচাই', t: 'g' },
      { id: 'M33-approval', en: 'Registration Approvals', bn: 'নিবন্ধন অনুমোদন', t: 'g' }
    ]},
    { en: 'Data Quality', screens: [
      { id: 'M33-dedupe', en: 'Duplicate Detection', bn: 'সদৃশ শনাক্তকরণ', t: 'g' },
      { id: 'M33-merge', en: 'Supervised Merge', bn: 'মার্জ তত্ত্বাবধান', t: 'g' },
      { id: 'M33-quality', en: 'Quality Scoring', bn: 'গুণগত স্কোর', t: 'g' },
      { id: 'M33-form-score', en: 'Score a Party', bn: 'পার্টির গুণগত স্কোর', t: 'f' }
    ]},
    { en: 'Consent & Rights', screens: [
      { id: 'M33-consent', en: 'Consent Register', bn: 'সম্মতি রেজিস্টার', t: 'g' },
      { id: 'M33-dsr', en: 'Data-Subject Requests', bn: 'ডেটা অনুরোধ', t: 'g' },
      { id: 'M33-processing', en: 'Record of Processing', bn: 'প্রক্রিয়াকরণ রেকর্ড', t: 'g' },
      { id: 'M33-form-withdraw', en: 'Withdraw a Consent', bn: 'সম্মতি প্রত্যাহার', t: 'f' },
      { id: 'M33-form-consent-handling', en: 'Consent Handling (minor / assisted)', bn: 'সম্মতি পরিচালনা', t: 'f' }
    ]},
    { en: 'Segments & Credit', screens: [
      { id: 'M33-segments', en: 'Segments', bn: 'সেগমেন্ট', t: 'g' },
      { id: 'M33-credit', en: 'Credit Profiles & Holds', bn: 'ক্রেডিট প্রোফাইল', t: 'g' },
      { id: 'M33-credit-changes', en: 'Credit Limit Changes', bn: 'ক্রেডিট সীমা পরিবর্তন', t: 'g' },
      { id: 'M33-status', en: 'Party Status Lifecycle', bn: 'পার্টি স্ট্যাটাস', t: 'g' },
      { id: 'M33-form-party-status', en: 'Change Party Status', bn: 'পার্টি স্ট্যাটাস পরিবর্তন', t: 'f' },
      { id: 'M33-form-reactivate', en: 'Reactivate a Party', bn: 'পার্টি পুনরায় সক্রিয়', t: 'f' }
    ]},
    { en: 'Duplicate Detection Jobs (S8)', bn: 'ডুপ্লিকেট সনাক্তকরণ জব', screens: [
      { id: 'M33-dedup-jobs', en: 'Detection Jobs', bn: 'সনাক্তকরণ জব', t: 'g' },
      { id: 'M33-form-dedup-job', en: 'Detection Job', bn: 'জব ফর্ম', t: 'f' }
    ]},
    { en: 'Real-Customer Cut-over', bn: 'রিয়েল কাস্টমার কাট-ওভার', screens: [
      { id: 'M33-import-batches', en: 'Import Batches', bn: 'ইমপোর্ট ব্যাচ', t: 'g' },
      { id: 'M33-import-lines', en: 'Import Lines (audit)', bn: 'ইমপোর্ট লাইন (অডিট)', t: 'g' }
    ]}
  ],
  reports: ['Customer Growth by District', 'Data Quality Scorecard', 'Duplicate Merge Audit', 'Consent Coverage Report', 'Credit Exposure by Segment', 'Corporate Hierarchy Map'],
  forms: ['Party Master', 'Party (multi-role)', 'Address with GPS', 'Identity Document', 'Credit Profile', 'Merge Request', 'Duplicate Detection Job',
    'Classify a Party', 'Account Hierarchy Link', 'Dedup Rule', 'Score a Party', 'Survivorship Rule',
    'Consent Record', 'Withdraw a Consent', 'Data-Subject Request', 'Transparency Notice', 'Processing Record',
    'Change Party Status', 'Reactivate a Party',
    'Contact Point', 'Party Relationship', 'Corporate Contact Role', 'Corporate Contact Limit', 'Consent Handling', 'Credit Limit Change'],
  cross: ['Every module reads party', 'M07 CRM accounts', 'M20 credit control', 'P01 self-service profile', 'M29 record isolation'],
  freg: {
    src: 100,
    sub: [
      /* M33 capture audit 2026-11-14. Before: page 1 offered only a role,
       * 2 Classification captured a role (the class is the party's own
       * field), 4 Addresses listed and captured PARTIES (0 addresses on
       * fix_real), 8 Quality and 12 Status had no capture, and 9 had no way
       * to raise a data-subject request, publish a notice or record
       * processing (FR-CPM-044 had no register). */
      /* 1 FR-CPM-001/002: the ONE party record first, its roles beside it */
      /* Pass 2 (2026-11-19): a party's phones and emails are contact points
       * with their own verification (FR-CPM-022, BRU-CPM-01), and its links
       * to other parties are relationships (FR-CPM-006). Neither existed. */
      ['1', 'Party Record & Roles', 12, { model: 'fix.party.role', cols: ['partner_id', 'role_type', 'role_status', 'since'], screens: ['M33-party', 'M33-directory', 'M33-contact-points', 'M33-relationships'], reports: [], forms: ['Party Master', 'Party (multi-role)', 'Contact Point', 'Party Relationship'], create: 'M33-form-party' }],
      /* 2 FR-CPM-003: Individual / Dealer / Corporate / Government is the party's
       * class; seller, brand partner, vendor are roles */
      ['2', 'Classification', 7, { model: 'fix.party.role', cols: ['partner_id', 'role_type', 'role_status', 'since'], screens: ['M33-party', 'M33-directory'], reports: [], forms: ['Classify a Party', 'Party (multi-role)'], create: 'M33-form-classify' }],
      /* Pass 2: who at a corporate account requests, approves, pays or
       * administers (FR-CPM-009), inside the contact limit 1000FiX sets
       * (FR-CPM-011). */
      ['3', 'Account Hierarchy', 8, { model: 'fix.party.hierarchy', cols: ['parent_id', 'child_id', 'relation_type', 'date_from', 'date_to'], screens: ['M33-hierarchy', 'M33-contact-roles', 'M33-relationships', 'M33-rpt-hiermap'], reports: ['Corporate Hierarchy Map'], forms: ['Account Hierarchy Link', 'Corporate Contact Role', 'Corporate Contact Limit', 'Party Relationship'] }],
      /* 4 FR-CPM-014..016: the party's tagged Bangladesh addresses with GPS */
      ['4', 'Addresses (BD structure + GPS)', 7, { model: 'fix.bd.address', cols: ['party_id', 'address_tag', 'is_default', 'district', 'upazila', 'postcode', 'latitude', 'longitude'], domain: [['party_id', '!=', false]], screens: ['M33-addresses', 'M33-directory'], reports: ['Customer Growth by District'], forms: ['Address with GPS', 'Party Master'], create: 'M33-form-address' }],
      /* Pass 2: the OTP log verified nothing in particular; the contact
       * point is what a code now verifies. */
      ['5', 'Identity & OTP', 9, { model: 'fix.identity.document', cols: ['partner_id', 'active', 'residency_ref', 'document_type', 'document_number', 'issuing_country'], screens: ['M33-identity', 'M33-contact-points', 'M33-otp'], reports: [], forms: ['Identity Document', 'Contact Point'] }],
      ['6', 'Registration Approval', 6, { model: 'fix.registration.approval', cols: ['partner_id', 'party_class', 'lm_state', 'admin_state', 'requested_at', 'lm_decided_by'], screens: ['M33-approval'], reports: [], forms: [] }],
      ['7', 'Deduplication & Merge', 11, { model: 'fix.party.duplicate', cols: ['state', 'party_a', 'party_b', 'score', 'factors', 'reviewed_by'], screens: ['M33-dedupe', 'M33-merge', 'M33-dedup-rule', 'M33-rpt-mergeaudit'], reports: ['Duplicate Merge Audit'], forms: ['Merge Request', 'Duplicate Detection Job', 'Dedup Rule'] }],
      /* 8 FR-CPM-031/032: score the party in front of you; the per-attribute
       * survivorship rules are M64's golden rules (spec 12.1) */
      ['8', 'Golden Record & Quality', 9, { model: 'fix.party.quality', cols: ['partner_id', 'completeness', 'validity', 'recency', 'composite', 'deficiencies'], screens: ['M33-quality', 'M33-rpt-scorecard'], reports: ['Data Quality Scorecard'], forms: ['Score a Party', 'Survivorship Rule'], create: 'M33-form-score' }],
      /* 9 FR-CPM-035..044 */
      ['9', 'Consent & DSR', 13, { model: 'fix.consent', cols: ['state', 'partner_id', 'purpose', 'channel', 'date_granted', 'date_withdrawn'], screens: ['M33-consent', 'M33-dsr', 'M33-transparency-notice', 'M33-processing', 'M33-rpt-consentcov'], reports: ['Consent Coverage Report'], forms: ['Consent Record', 'Withdraw a Consent', 'Consent Handling', 'Data-Subject Request', 'Transparency Notice', 'Processing Record'] }],
      ['10', 'Segments', 5, { model: 'fix.segment', cols: ['name', 'code', 'active', 'name_bn', 'criteria_json', 'evaluation_mode'], screens: ['M33-segments'], reports: ['Credit Exposure by Segment'], forms: [] }],
      /* Pass 2: a limit changed by any profile edit, with no approval
       * (FR-CPM-047, BRU-CPM-12, SOD-04). It changes by an approved request. */
      ['11', 'Credit Profile', 8, { model: 'fix.credit.profile', cols: ['customer_id', 'credit_limit', 'payment_terms_days', 'credit_hold', 'hold_reason', 'hold_by'], screens: ['M33-credit', 'M33-credit-changes', 'M33-rpt-creditexp'], reports: ['Credit Exposure by Segment'], forms: ['Credit Profile', 'Credit Limit Change'] }],
      /* 12 FR-CPM-005: restricting a party is a reasoned decision, reactivation a Tier 2 one */
      ['12', 'Status Lifecycle', 5, { model: 'res.partner', cols: ['name', 'party_status', 'status_reason', 'status_since'], screens: ['M33-status', 'M33-rpt-growth'], reports: ['Customer Growth by District'], forms: ['Change Party Status', 'Reactivate a Party'], create: 'M33-form-party-status' }],
      ['13', 'Real-Customer Cut-over', 5, { model: 'fix.party.import.batch', cols: ['name', 'sheet_kind', 'state', 'line_count', 'created_count', 'matched_count', 'quarantined_count'], screens: ['M33-import-batches', 'M33-import-lines'], reports: [], forms: [] }]
    ]
  }
};

/* In-workspace data screens over the whitelisted party models — every one
 * of the 15 registry screens is a live surface. */
export const SCREENS = {
  'M33-form-transparency': {
    kind: 'model_form',
    model: 'fix.transparency.notice',
    title: "Transparency Notice",
    back: 'M33-transparency-notice',
    tabs: [
      { id: 'general', label: '1. Notice Profile', bn: '১. বিজ্ঞপ্তির পরিধি', icon: '📜', badge: '2' },
      { id: 'content', label: '2. Bilingual Disclosure Text', bn: '২. নোটিশ বিবরণ', icon: '📝', badge: '2' },
      { id: 'compliance', label: '3. PDPA & Regulatory Audit', bn: '৩. পিডিপিএ অডিট', icon: '⚖️', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: "Notice Version & Status",
        note: "A PDPA transparency notice version. Consent records point at the notice version they were granted under, so once a consent is captured against it the wording is fixed: publish a new version instead (the server refuses the edit).",
        fields: [
          { name: 'version', required: true, label: "Version Code" },
          { name: 'purpose_set', required: true, label: "Purposes Covered (e.g. marketing, research)" },
          { name: 'published_at', readonly: true, label: "Published At" },
          { name: 'retired_at', readonly: true, label: "Retired At" },
          { name: 'active', readonly: true, label: "Current (published, not retired)" }
        ] },
      { tab: 'content', title: "Bilingual Statutory Disclosures",
        note: "State the data categories, purposes, risks, retention periods, third-party transfers and how to withdraw (FR-CPM-037).",
        fields: [
          { name: 'text_en', required: true, label: "Disclosure Text (English)", type: 'text' },
          { name: 'text_bn', required: true, label: "Disclosure Text (Bengali)", type: 'text' }
        ] },
      { tab: 'compliance', title: "PDPA Governance & Revision Policy",
        note: "Under the Personal Data Protection Act (PDPA), any material change to personal data collection requires issuing a new notice version. Existing consent records remain anchored to their capture version.",
        fields: [] }
    ]
  },

  /* --- Party Records --- */
  'M33-directory': { kind: 'model_list', model: 'res.partner', create: true,
    cols: ['name', 'name_bn', 'preferred_language', 'party_status', 'phone', 'email', 'write_date'],
    stateField: 'party_status' },
  /* THE design rule made visible: one partner, many roles (never masters) */
  'M33-party': { kind: 'model_list', model: 'fix.party.role', create: true,
    cols: ['partner_id', 'role_type', 'role_status', 'since', 'company_id'],
    stateField: 'role_status' },
  'M33-360': { kind: 'table_report', module: 'M33', report: 'party_360', period: false },
  'M33-hierarchy': { kind: 'model_list', model: 'fix.party.hierarchy', create: true,
    cols: ['parent_id', 'child_id', 'relation_type', 'date_from', 'date_to'] },

  /* --- Identity & Verification --- */
  'M33-identity': { kind: 'model_list', model: 'fix.identity.document',
    cols: ['partner_id', 'document_type', 'checksum_valid', 'verification_status', 'verified_by', 'expiry_date'],
    stateField: 'verification_status',
    // A03 audit M33-9 / W4: KYC is a data-steward decision that stamps the
    // verifier; whoever captured the document cannot verify it. Submitting
    // routes it; the steward verifies or fails it from the M63 inbox.
    actions: [
      { m: 'action_kyc_submit', l: 'Submit for Verification' },
      { m: 'action_request_approval', l: 'Request Approval', ask: 'Note for the steward (optional)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M33-otp': { kind: 'model_list', model: 'fix.otp.log', create: false,
    cols: ['requested_at', 'partner_id', 'channel', 'destination_masked', 'state', 'verified_at'],
    stateField: 'state',
    actions: [
      { m: 'action_mark_verified', l: 'Mark Verified', ask: 'Channel reference (optional)', kwarg: 'channel_ref' },
      { m: 'action_expire', l: 'Expire' }
    ] },
  'M33-approval': { kind: 'model_list', model: 'fix.registration.approval', create: true,
    cols: ['requested_at', 'partner_id', 'party_class', 'current_step', 'lm_state', 'admin_state', 'approval_state'],
    // A03 audit M33-1: each step is decided (approve / reject) from the M63
    // approval inbox, by a different person per step. Here it is only routed.
    actions: [
      { m: 'action_request_approval', l: 'Request Approval', ask: 'Note for the approver (optional)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },

  /* --- Data Quality --- */
  'M33-dedupe': { kind: 'model_list', model: 'fix.party.duplicate', create: true,
    cols: ['score', 'party_a', 'party_b', 'state', 'reviewed_by', 'decision'],
    stateField: 'state',
    actions: [
      { m: 'action_review', l: 'Start Review' },
      { m: 'action_confirm', l: 'Confirm Duplicate (opens merge)' },
      { m: 'action_dismiss', l: 'Dismiss', ask: 'Why is this NOT a duplicate?', kwarg: 'reason' }
    ] },
  'M33-merge': { kind: 'model_list', model: 'fix.party.merge', create: true,
    cols: ['requested_at', 'survivor_id', 'victim_id', 'state', 'executed_by', 'reversible_until'],
    stateField: 'state',
    // A03 audit W4: a steward who created neither party executes the merge
    // from the M63 approval inbox (SOD-15). Here it is only routed.
    actions: [
      { m: 'action_request_approval', l: 'Request Merge Approval', ask: 'Note for the steward (optional)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_reverse', l: 'Reverse (inside window)' }
    ] },
  'M33-quality': { kind: 'model_list', model: 'fix.party.quality', create: false,
    cols: ['partner_id', 'completeness', 'validity', 'recency', 'composite', 'evaluated_at'],
    actions: [{ m: 'action_recompute', l: 'Recompute Score' }] },

  /* --- Consent & Rights --- */
  'M33-consent': { kind: 'model_list', model: 'fix.consent', create: true,
    cols: ['partner_id', 'purpose', 'channel', 'state', 'date_granted', 'notice_version_id', 'proof'],
    stateField: 'state',
    actions: [{ m: 'action_withdraw', l: 'Withdraw (append-only)' }] },
  'M33-dsr': { kind: 'model_list', model: 'fix.rights.request', create: true,
    cols: ['received_at', 'partner_id', 'request_type', 'statutory_due', 'state', 'evidence_ref'],
    stateField: 'state',
    actions: [
      { m: 'action_verify', l: 'Verify Identity' },
      { m: 'action_start', l: 'Start Work' },
      { m: 'action_fulfil', l: 'Fulfil', ask: 'Evidence reference (export/notice ID)', kwarg: 'evidence' },
      { m: 'action_reject', l: 'Reject', ask: 'Stated basis (statutory override)', kwarg: 'reason' }
    ] },

  /* --- Segments & Credit --- */
  'M33-segments': { kind: 'model_list', model: 'fix.segment', create: true,
    cols: ['code', 'name', 'name_bn', 'member_count', 'evaluation_mode', 'active'],
    actions: [
      { m: 'action_add_members', l: 'Add Members', ask: 'Partner ids (comma-separated)', kwarg: 'partner_ids' },
      { m: 'action_remove_member', l: 'Remove Member', ask: 'Partner id', kwarg: 'partner_id' }
    ] },
  /* The credit model of record is cd_billing_engine's (M20, FR-ARB-030/031);
   * M33 surfaces it (spec §3.3) — fields are the billing engine's own. */
  'M33-credit': { kind: 'model_list', model: 'fix.credit.profile', create: true,
    cols: ['customer_id', 'credit_limit', 'payment_terms_days', 'credit_hold', 'hold_reason', 'exposure', 'over_limit'],
    actions: [
      { m: 'action_toggle_hold', l: 'Toggle Credit Hold', ask: 'Hold reason (placing)', kwarg: 'reason' }
    ] },
  'M33-status': { kind: 'model_list', model: 'res.partner', create: false,
    cols: ['name', 'party_status', 'status_reason', 'status_since', 'write_date'],
    stateField: 'party_status',
    domain: [['party_status', '!=', false]],
    // Activation is a decision with an owner, not a field edit.
    actions: [
      { m: 'action_reactivate_party', l: 'Reactivate Party (Tier 2)', ask: 'Reason for reactivation', kwarg: 'reason' }
    ] },
/* the registry's six built-in reports as in-workspace table reports */
  'M33-rpt-growth': { kind: 'table_report', module: 'M33', report: 'customer_growth_by_district', title: 'Customer Growth by District', period: true },
  'M33-rpt-scorecard': { kind: 'table_report', module: 'M33', report: 'data_quality_scorecard', title: 'Data Quality Scorecard', period: false },
  'M33-rpt-mergeaudit': { kind: 'table_report', module: 'M33', report: 'duplicate_merge_audit', title: 'Duplicate Merge Audit', period: false },
  'M33-rpt-consentcov': { kind: 'table_report', module: 'M33', report: 'consent_coverage', title: 'Consent Coverage Report', period: false },
  'M33-rpt-creditexp': { kind: 'table_report', module: 'M33', report: 'credit_exposure_by_segment', title: 'Credit Exposure by Segment', period: false },
  'M33-rpt-hiermap': { kind: 'table_report', module: 'M33', report: 'corporate_hierarchy_map', title: 'Corporate Hierarchy Map', period: false },

  /* ==================================================================
   * D365 IN-WORKSPACE RECORD FORMS (Dynamics 365 7-Tab Master Forms)
   * Rendered inside the workspace shell: command bar, record header with
   * status pill, tab bar, section cards, labelled field grid.
   * ================================================================== */
  'M33-form-party': {
    lines: {
      field: 'child_ids',
      title: 'Contacts at this Party',
      note: 'The individuals and sites that belong to this party.',
      fields: [
        { name: 'name', label: 'Contact', required: true },
        { name: 'function', label: 'Job Position' },
        { name: 'email', label: 'Email' },
        { name: 'phone', label: 'Phone' },
        { name: 'type', label: 'Address Type' }
      ]
    }, kind: 'model_form', model: 'res.partner',
    title: 'Customer & Party Master', back: 'M33-directory',
    status: { field: 'party_status' },
    tabs: [
      { id: 'general', label: '1. General Profile', bn: '১. সাধারণ প্রোফাইল', icon: '👤', badge: '7' },
      { id: 'identity', label: '2. Statutory Identity & Tax', bn: '২. স্ট্যাটুটরি পরিচয়', icon: '🏛️', badge: '5' },
      { id: 'address', label: '3. BD Geo-Address & Location', bn: '৩. ভূগোল-ঠিকানা', icon: '📍', badge: '7' },
      { id: 'contact', label: '4. Communications & Contacts', bn: '৪. যোগাযোগ', icon: '📞', badge: '5' },
      { id: 'roles', label: '5. Multi-Role & Classification', bn: '৫. বহু-রোল', icon: '🏷️', badge: '4' },
      { id: 'credit', label: '6. Credit & Financial Terms', bn: '৬. ক্রেডিট ও আর্থিক', icon: '💳', badge: '4' },
      { id: 'consent', label: '7. Consent & PDPA Privacy', bn: '৭. সম্মতি ও গোপনীয়তা', icon: '🛡️', badge: '2' },
      { id: 'hierarchy', label: '8. Corporate Account Hierarchy', bn: '৮. অ্যাকাউন্ট শ্রেণিবিন্যাস', icon: '🏢', badge: '3' },
      { id: 'docs', label: '9. KYC Verification Repository', bn: '৯. ভেরিফিকেশন নথি', icon: '📑', badge: '2' },
      { id: 'audit', label: '10. Lifecycle & Audit Trail', bn: '১০. জীবনচক্র ও অডিট', icon: '⏱️', badge: '5' }
    ],
    sections: [
      { tab: 'general', title: 'Party Identity & Legal Entity', fields: [
        { name: 'name', required: true, label: 'Legal / Trade Name' },
        { name: 'name_bn', label: 'Bengali Legal Name (Bangla)' },
        { name: 'ref', label: 'Party Reference Code' },
        { name: 'is_company', label: 'Corporate Entity Flag' },
        { name: 'company_type', label: 'Company Structure Type' },
        { name: 'party_class', label: 'Party Class (Dealer / Corporate / Government open a registration approval)' },
        { name: 'preferred_language', label: 'Preferred Communication Language' },
        { name: 'company_id', label: 'Primary Operating Unit / Company' },
      ]},
      { tab: 'identity', title: 'Statutory Registration & National Identifiers', fields: [
        { name: 'vat', label: 'Tax Identification Number (e-TIN / BIN / VAT)' },
        { name: 'company_registry', label: 'Registrar / Trade License Number' },
        { name: 'barcode', label: 'Smart Identification Barcode' },
        { name: 'commercial_partner_id', label: 'Commercial Entity Master Ref', readonly: true },
        { name: 'application_statistics', label: 'Application Verification Code', readonly: true },
      ]},
      { tab: 'address', title: 'Bangladesh Statutory Geographic Address', fields: [
        { name: 'street', label: 'Holding / Building / Street Address' },
        { name: 'street2', label: 'Road / Area / Sector (Line 2)' },
        { name: 'city', label: 'Thana / Upazila / City' },
        { name: 'state_id', label: 'District / Administrative Division' },
        { name: 'zip', label: 'Postal Code' },
        { name: 'country_id', label: 'Country' },
        { name: 'contact_address_inline', label: 'Full Normalized Geographic Address', readonly: true },
      ]},
      { tab: 'contact', title: 'Primary Communications & Digital Endpoints', fields: [
        { name: 'phone_sanitized', label: 'Normalized Mobile Number (E.164)', readonly: true },
        { name: 'phone', label: 'Hotline / Office Phone' },
        { name: 'email', label: 'Official Business Email' },
        { name: 'email_normalized', label: 'Standardized Normalized Email', readonly: true },
        { name: 'website', label: 'Corporate Portal / Website' },
      ]},
      { tab: 'roles', title: 'Commercial Classification & Assigned Relationship',
        note: 'Unified Party Architecture: A single party record projects multiple functional roles across sales, vendor, counter and corporate tiers.',
        fields: [
          { name: 'customer_rank', label: 'Customer Hierarchy Rank' },
          { name: 'user_id', label: 'Dedicated Account Manager / Salesperson' },
          { name: 'category_id', label: 'Customer Segment & Category Tags' },
          { name: 'bank_ids', label: 'Associated Bank Accounts' },
        ]},
      { tab: 'credit', title: 'Commercial Credit Exposure & Payment Terms',
        note: 'The approved credit limit and holds are kept on the party\'s Credit Profile (Credit Profiles & Holds), where M20 enforces them. They are shown here, not edited.',
        fields: [
        { name: 'credit_limit', label: 'Credit Limit on the Contact (BDT)', readonly: true },
        { name: 'property_payment_term_id', label: 'Default Commercial Payment Terms' },
        { name: 'credit', label: 'Total Current Receivables (BDT)', readonly: true },
        { name: 'days_sales_outstanding', label: 'Days Sales Outstanding (DSO)', readonly: true },
      ]},
      { tab: 'consent', title: 'Data Privacy & Consent Register Compliance',
        note: 'Customer privacy preferences governing SMS, push notifications, and telephone outreach under Bangladesh Telecom & PDPA regulations.',
        fields: [
          { name: 'consent_ids', label: 'Statutory Consent Records', readonly: true },
          { name: 'active', label: 'Active Operational Status' },
        ]},
      { tab: 'hierarchy', title: 'Parent Corporate Account & Branch Consolidation', fields: [
        { name: 'parent_id', label: 'Parent Corporate Account (Holding Company)' },
        { name: 'child_ids', label: 'Subsidiaries & Branch Office Locations', readonly: true },
        { name: 'commercial_company_name', label: 'Consolidated Commercial Name', readonly: true },
      ]},
      { tab: 'docs', title: 'Cryptographic Document Repository & KYC Verification',
        note: 'Scanned copies of National ID (Smart NID), Municipal Trade License, e-TIN certificate, and Bank Solvency verification records.',
        fields: [
          { name: 'identity_document_ids', label: 'Verified KYC Identity Documents', readonly: true },
          { name: 'approval_ids', label: 'Registration Approval History', readonly: true },
        ]},
      { tab: 'audit', title: 'Party Lifecycle Governance & System Timestamps',
        note: 'The status changes through Change Party Status (with a reason) or Reactivate a Party (DOFA Tier 2), on the Party Status Lifecycle page.',
        fields: [
        { name: 'party_status', label: 'Party Lifecycle Governance Status', readonly: true },
        { name: 'status_reason', label: 'Status Reason / Audit Justification', readonly: true },
        { name: 'status_since', label: 'Status Effective Date', readonly: true },
        { name: 'create_date', label: 'Initial Registration Timestamp', readonly: true },
        { name: 'write_date', label: 'Last System Modification Timestamp', readonly: true },
      ]}
    ] },

  'M33-form-role': { kind: 'model_form', model: 'fix.party.role',
    title: 'Party Role', back: 'M33-party',
    status: { field: 'role_status' },
    tabs: [
      { id: 'general', label: '1. Role Definition', bn: '১. ভূমিকার বিবরণ', icon: '🏷️', badge: '4' },
      { id: 'scope', label: '2. Company & Scope', bn: '২. কোম্পানি ও পরিধি', icon: '🏢', badge: '2' },
      { id: 'lifecycle', label: '3. Lifecycle & Validity', bn: '৩. মেয়াদ ও অবস্থা', icon: '⏳', badge: '2' },
      { id: 'audit', label: '4. Kernel Design Rule', bn: '৪. কার্নেল নকশা নিয়ম', icon: '⚙️', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Role Assignment', fields: [
        { name: 'partner_id', required: true, label: 'The ONE Party' },
        { name: 'role_type', required: true, label: 'Role Type' },
        { name: 'since', readonly: true, label: 'Active Since' },
      ]},
      { tab: 'scope', title: 'Operating Scope', fields: [
        { name: 'company_id', label: 'Company' },
        { name: 'operating_unit_id', label: 'Operating Unit' },
      ]},
      { tab: 'lifecycle', title: 'Validity & Authority', fields: [
        { name: 'role_status', required: true, label: 'Role Status' },
      ]},
      { tab: 'audit', title: 'The Architectural Design Rule',
        note: 'A party with three roles has THREE role records pointing at the SAME party — never three separate master records. Duplicate masters are the failure this kernel exists to prevent.',
        fields: [] }
    ] },

  'M33-form-address': { kind: 'model_form', model: 'fix.bd.address',
    title: 'Address with GPS', back: 'M33-addresses',
    tabs: [
      { id: 'owner', label: '1. Owner & Purpose', bn: '১. স্বত্বাধিকারী ও উদ্দেশ্য', icon: '👤', badge: '3' },
      { id: 'geo', label: '2. Administrative Hierarchy', bn: '২. প্রশাসনিক স্তর (বিভাগ/জেলা)', icon: '🗺️', badge: '8' },
      { id: 'street', label: '3. Street & House Details', bn: '৩. রাস্তা ও বাড়ির বিবরণ', icon: '🏠', badge: '2' },
      { id: 'gps', label: '4. GPS & Geolocation', bn: '৪. জিপিএস ও অবস্থান', icon: '📍', badge: '3' }
    ],
    sections: [
      { tab: 'owner', title: 'Owner & Purpose',
        note: 'One party may hold any number of tagged addresses; one per tag is its default (FR-CPM-014).',
        fields: [
        { name: 'party_id', label: 'Party', required: true },
        { name: 'address_tag', label: 'Address Tag / Label', required: true },
        { name: 'is_default', label: 'Default Address for this Tag' },
        { name: 'landmark', label: 'Prominent Landmark' },
      ]},
      { tab: 'geo', title: 'Bangladesh Administrative Structure (BN-007 §4)', fields: [
        { name: 'division', required: true, label: 'Division' },
        { name: 'division_bn', label: 'Division (Bengali)' },
        { name: 'district', required: true, label: 'District' },
        { name: 'district_bn', label: 'District (Bengali)' },
        { name: 'upazila', label: 'Upazila / Thana' },
        { name: 'upazila_bn', label: 'Upazila / Thana (Bengali)' },
        { name: 'union_or_ward', label: 'Union / Ward' },
        { name: 'postcode', label: 'Postcode (4 digits)' },
      ]},
      { tab: 'street', title: 'Street & House Numbering', fields: [
        { name: 'street', label: 'Street / Road' },
        { name: 'house', label: 'House / Building / Flat' },
      ]},
      { tab: 'gps', title: 'GPS Geolocation & Dispatch Coordinates (FR-CPM-016)',
        note: 'BN-007 §4: the address renders house → road → upazila → district → postcode — the inverse of the Western order. Field dispatch relies on precision GPS coordinates and the landmark.',
        fields: [
          { name: 'latitude', label: 'GPS Latitude' },
          { name: 'longitude', label: 'GPS Longitude' },
        ]}
    ] },

  'M33-form-identity': { kind: 'model_form', model: 'fix.identity.document',
    title: 'Identity Document', back: 'M33-identity',
    status: { field: 'verification_status' },
    tabs: [
      { id: 'document', label: '1. Document Details', bn: '১. পরিচয়পত্র হেডার', icon: '🪪', badge: '4' },
      { id: 'verification', label: '2. Verification Status', bn: '২. যাচাইকরণ ও অবস্থা', icon: '✅', badge: '6' },
      { id: 'residency', label: '3. Z4 Residency Classification', bn: '৩. ডেটা রেসিডেন্সি (Z4)', icon: '🔒', badge: '1' },
      { id: 'docs', label: '4. Scans & Evidence', bn: '৪. নথির স্ক্যান কপি', icon: '📎', badge: '2' }
    ],
    sections: [
      { tab: 'document', title: 'Document Header', fields: [
        { name: 'partner_id', required: true, label: 'Party' },
        { name: 'document_type', required: true, label: 'Document Type' },
        { name: 'document_number', label: 'Document Number' },
        { name: 'is_primary', label: 'Primary Document' },
      ]},
      { tab: 'verification', title: 'Verification Audit', fields: [
        { name: 'verification_status', readonly: true, label: 'Verification Status' },
        { name: 'checksum_valid', readonly: true, label: 'Checksum Valid' },
        { name: 'expiry_date', label: 'Document Expiry Date' },
        { name: 'issuing_country', label: 'Issuing Country' },
        { name: 'verified_by', readonly: true, label: 'Verified By' },
        { name: 'verified_at', readonly: true, label: 'Verified Timestamp' },
        { name: 'verification_note', readonly: true, label: 'Verification Note' },
      ]},
      { tab: 'residency', title: 'Residency Classification (PDPA Z4)',
        note: 'RESIDENCY-CLASSIFIED: The document number routes through the residency service to the Bangladesh-resident store (Z4); the regional database holds only the pointer — the value never appears in caches, logs, or exports (FR-CPM-021, NFR-086/099).',
        fields: [] },
      { tab: 'docs', title: 'Scanned Document Attachment',
        note: 'Scans are NOT kept on this record (FR-CPM-024: images go to the Bangladesh-resident document store, never the party record). That store is not live yet (DEP-31), so no scan is captured here; the steward verifies against the original document.',
        fields: [] }
    ] },

  'M33-form-credit': {
    lines: { field: 'limit_change_ids', title: 'Credit Limit Changes', readonlyGrid: true,
      note: 'Every limit change asked for on this profile, and who decided it (BRU-CPM-12). Raise one with "Credit Limit Change".',
      fields: [
        { name: 'current_limit', label: 'Limit Then', readonly: true },
        { name: 'proposed_limit', label: 'Proposed', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'requested_by', label: 'Requested By', readonly: true },
        { name: 'decided_by', label: 'Decided By', readonly: true },
        { name: 'decided_at', label: 'Decided At', readonly: true }
      ]
    },
    kind: 'model_form', model: 'fix.credit.profile',
    title: 'Credit Profile', back: 'M33-credit',
    status: { field: 'credit_hold', labels: { true: 'On Hold', false: 'Active' } },
    tabs: [
      { id: 'terms', label: '1. Credit Limit & Terms', bn: '১. ক্রেডিট সীমা ও শর্ত', icon: '💳', badge: '3' },
      { id: 'hold', label: '2. Credit Hold & Exposure', bn: '২. ক্রেডিট হোল্ড ও এক্সপোজার', icon: '🛑', badge: '4' },
      { id: 'enforcement', label: '3. Enforcement Governance', bn: '৩. কার্যকরীকরণ নিয়ম', icon: '⚖️', badge: '1' },
      { id: 'audit', label: '4. Review & Audit Trail', bn: '৪. রিভিউ ট্রেইল', icon: '⚙️', badge: '2' }
    ],
    sections: [
      { tab: 'terms', title: 'Customer Credit Terms', fields: [
        { name: 'customer_id', required: true, label: 'Customer' },
        { name: 'credit_limit', readonly: true, label: 'Credit Limit (BDT): changed by an approved Credit Limit Change' },
        { name: 'payment_terms_days', required: true, label: 'Payment Terms (Days)' },
      ]},
      { tab: 'hold', title: 'Hold & Real-Time Exposure', fields: [
        { name: 'credit_hold', readonly: true, label: 'Credit Hold Placed' },
        { name: 'hold_reason', label: 'Credit Hold Reason' },
        { name: 'exposure', readonly: true, label: 'Total Current Exposure (BDT)' },
        { name: 'over_limit', readonly: true, label: 'Over Credit Limit' },
      ]},
      { tab: 'enforcement', title: 'Enforcement Governance',
        note: 'M33 holds the limit and the hold status; M20 enforces it at order intake and invoice generation time (spec §3.3). Placing or releasing a hold is executed via the Toggle Hold action on the Credit Profiles screen with mandatory reason.',
        fields: [] },
      { tab: 'audit', title: 'DOFA Approval & Credit Review',
        note: 'A new profile starts with no limit. The limit changes only through a Credit Limit Change that a Finance Manager (Accounting Administrator) other than the requester approves (BRU-CPM-12, SOD-04). Each change is kept on the Credit Limit Changes register and in the profile chatter.',
        fields: [] }
    ] },

  'M33-form-merge': { kind: 'model_form', model: 'fix.party.merge',
    title: 'Merge Request', back: 'M33-merge',
    status: { field: 'state' },
    tabs: [
      { id: 'records', label: '1. Merge Pair Records', bn: '১. মার্জ রেকর্ডস', icon: '🔀', badge: '2' },
      { id: 'execution', label: '2. Execution & Timing', bn: '২. সম্পাদন ও রিভার্সাল', icon: '⏳', badge: '5' },
      { id: 'decisions', label: '3. Field Decisions Audit', bn: '৩. ক্ষেত্রভিত্তিক সিদ্ধান্ত', icon: '📋', badge: '1' },
      { id: 'governance', label: '4. Data Steward Governance', bn: '৪. সুশাসন নিয়মাবলী', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'records', title: 'Merge Candidate Pair', fields: [
        { name: 'survivor_id', required: true, label: 'Survivor (Golden Record)' },
        { name: 'victim_id', required: true, label: 'Victim (Tombstoned)' },
      ]},
      { tab: 'execution', title: 'Merge Execution Status', fields: [
        { name: 'state', readonly: true, label: 'Merge State' },
        { name: 'requested_at', readonly: true, label: 'Requested Timestamp' },
        { name: 'executed_by', readonly: true, label: 'Executed By' },
        { name: 'executed_at', readonly: true, label: 'Executed Timestamp' },
        { name: 'reversible_until', readonly: true, label: 'Reversible Until' },
      ]},
      { tab: 'decisions', title: 'Move Audit & Attribute Reconciliation', fields: [
        { name: 'attribute_decisions', label: 'What Moved / What Was Skipped', readonly: true },
      ]},
      { tab: 'governance', title: 'Data Steward Governance Law',
        note: 'Automated merge is strictly prohibited (BRU-CPM-04). Execution is a human data-steward action, refused when the steward created either record (SOD-15); the victim is tombstoned, never deleted, and every downstream module re-points on party.merged.',
        fields: [] }
    ] },

  'M33-form-consent': { kind: 'model_form', model: 'fix.consent',
    title: 'Consent Record', back: 'M33-consent',
    status: { field: 'state' },
    tabs: [
      { id: 'consent', label: '1. Consent Scope', bn: '১. সম্মতির পরিধি', icon: '📜', badge: '4' },
      { id: 'evidence', label: '2. Proof Reference & Notice', bn: '২. প্রমাণক রেফারেন্স', icon: '🔐', badge: '5' },
      { id: 'lifecycle', label: '3. Lifecycle & Withdrawal', bn: '৩. প্রত্যাহার ও মেয়াদ', icon: '⏳', badge: '2' },
      { id: 'pdpa', label: '4. PDPA Legal Mandate', bn: '৪. পিডিপিএ বিধান', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'consent', title: 'Consent Definition', fields: [
        { name: 'partner_id', required: true, label: 'Party' },
        { name: 'purpose', required: true, label: 'Processing Purpose' },
        { name: 'channel', required: true, label: 'Communication Channel' },
        // Guarded (append-only consent): a grant is born 'granted'; withdrawal is an action.
        { name: 'state', readonly: true, label: 'Consent State' },
      ]},
      { tab: 'evidence', title: 'Evidence & Transparency Notice Link', fields: [
        { name: 'notice_version_id', required: true, label: 'Transparency Notice Version Presented' },
        { name: 'proof', required: true, label: 'Proof Reference (signed form ID / OTP session)' },
        { name: 'assisted_by_id', label: 'Given By (verified guardian / representative, for a minor or assisted party)' },
        { name: 'source', label: 'Capture Channel / Portal' },
        { name: 'date_granted', readonly: true, label: 'Date Granted' },
        { name: 'date_withdrawn', readonly: true, label: 'Date Withdrawn' },
      ]},
      { tab: 'lifecycle', title: 'Withdrawal & Append-Only Log',
        note: 'Under the Bangladesh PDPA, a customer can withdraw consent at any time. Withdrawal does not erase historical audit trails; it appends a withdrawal event superseding the grant.',
        fields: [] },
      { tab: 'pdpa', title: 'Statutory PDPA Consent Requirements',
        note: 'A granted consent requires BOTH its cryptographic proof reference and the transparency notice version presented at the time of capture (BRU-CPM-08).',
        fields: [] }
    ] },

  'M33-form-dsr': { kind: 'model_form', model: 'fix.rights.request',
    title: 'Data-Subject Request', back: 'M33-dsr',
    status: { field: 'state' },
    tabs: [
      { id: 'request', label: '1. Request Scope', bn: '১. অনুরোধের বিবরণ', icon: '📝', badge: '4' },
      { id: 'decision', label: '2. Decision & Evidence Ref', bn: '২. সিদ্ধান্ত ও প্রমাণক', icon: '✅', badge: '6' },
      { id: 'sla', label: '3. Statutory Clock & SLA', bn: '৩. সংবিধিবদ্ধ সময়সীমা', icon: '⏱️', badge: '1' },
      { id: 'audit', label: '4. Governance Action', bn: '৪. সুশাসন পদক্ষেপ', icon: '⚙️', badge: '1' }
    ],
    sections: [
      { tab: 'request', title: 'Data Subject Request Definition', fields: [
        { name: 'partner_id', required: true, label: 'Party' },
        { name: 'request_type', required: true, label: 'Request Type (Access/Rectification/Erasure)' },
        { name: 'received_at', readonly: true, label: 'Received Timestamp' },
        { name: 'statutory_due', readonly: true, label: 'Statutory Due Date (30 Days)' },
        { name: 'handler_id', label: 'Handler (receives the 30-day reminder)' },
      ]},
      { tab: 'decision', title: 'Decision & Fulfillment Evidence', fields: [
        { name: 'identity_verified', readonly: true, label: 'Identity Verified' },
        { name: 'evidence_ref', readonly: true, label: 'Evidence Reference / Export Link' },
        { name: 'fulfilled_at', readonly: true, label: 'Fulfilled Timestamp' },
        { name: 'notified_at', label: 'Party Notified At (a rectification is not closed without it, BRU-CPM-10)' },
        { name: 'decision', label: 'Decision Summary' },
        { name: 'rejected_reason', readonly: true, label: 'Rejection Legal Basis' },
      ]},
      { tab: 'sla', title: 'PDPA 30-Day Statutory Clock',
        note: 'Bangladesh PDPA mandates that data subject requests must be fulfilled or legally refused within 30 calendar days of verified identity receipt. A daily job reminds the handler inside the reminder window and escalates to every Data Protection Officer once the date has passed.',
        fields: [
          { name: 'reminded_at', readonly: true, label: 'Reminder Sent' },
          { name: 'escalated_at', readonly: true, label: 'Escalated to DPO' },
        ] },
      { tab: 'audit', title: 'Data Protection Officer (DPO) Action',
        note: 'Verification and fulfillment actions must be authenticated by the designated Data Protection Officer. Rectification requests must issue notifications to all integrated services.',
        fields: [] }
    ] },

  'M33-form-segment': {
    lines: {
      field: 'membership_ids',
      title: 'Segment Members',
      note: 'Who is in this segment, and when they entered or left it.',
      fields: [
        { name: 'partner_id', label: 'Party', required: true },
        { name: 'entered_at', label: 'Entered' },
        { name: 'exited_at', label: 'Exited' }
      ]
    }, kind: 'model_form', model: 'fix.segment',
    title: 'Customer Segment', back: 'M33-segments',
    tabs: [
      { id: 'definition', label: '1. Segment Definition', bn: '১. সেগমেন্ট সংজ্ঞা', icon: '🎯', badge: '5' },
      { id: 'criteria', label: '2. Dynamic Domain Query', bn: '২. ডোমেন মানদণ্ড', icon: '🔍', badge: '1' },
      { id: 'membership', label: '3. Membership & Publishing', bn: '৩. সদস্যপদ ও ইভেন্ট', icon: '👥', badge: '1' }
    ],
    sections: [
      { tab: 'definition', title: 'Segment Profile & Evaluation Mode', fields: [
        { name: 'code', required: true, label: 'Segment Code' },
        { name: 'name', required: true, label: 'Segment Name' },
        { name: 'name_bn', label: 'Segment Name (Bengali)' },
        { name: 'evaluation_mode', label: 'Evaluation Mode (Manual / Dynamic)' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'criteria', title: 'Query Filtering Criteria (JSON)', fields: [
        { name: 'criteria_json', label: 'Criteria (JSON Domain Rule)' },
      ]},
      { tab: 'membership', title: 'Audience Publishing & Sync',
        note: 'Membership changes publish event segment.membership_changed. Downstream campaigns (M35) and notification dispatchers subscribe to audience rosters.',
        fields: [] }
    ] },

  'M33-form-hierarchy': { kind: 'model_form', model: 'fix.party.hierarchy',
    title: 'Account Hierarchy Link', back: 'M33-hierarchy',
    tabs: [
      { id: 'edge', label: '1. Relationship Link', bn: '১. সম্পর্ক লিংক', icon: '🏢', badge: '3' },
      { id: 'validity', label: '2. Validity Window', bn: '২. সময়কাল', icon: '📅', badge: '2' },
      { id: 'governance', label: '3. Corporate Group Governance', bn: '৩. কর্পোরেট গ্রুপ নিয়ম', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'edge', title: 'Corporate / Household Edge Link', fields: [
        { name: 'parent_id', required: true, label: 'Parent Corporate Entity' },
        { name: 'child_id', required: true, label: 'Child Entity / Branch' },
        { name: 'relation_type', required: true, label: 'Relationship Type' },
      ]},
      { tab: 'validity', title: 'Validity Window', fields: [
        { name: 'date_from', required: true, label: 'Effective Date From' },
        { name: 'date_to', label: 'Valid Until (Empty = Indefinite)' },
      ]},
      { tab: 'governance', title: 'Hierarchy Governance & Dedup Isolation',
        note: 'One party relates to another for an explicit corporate or household reason. Inactive relations retain historical date_to stamps and are never deleted, ensuring dedup merges never orphan relationships.',
        fields: [] }
    ] },

  'M33-form-approval': { kind: 'model_form', model: 'fix.registration.approval',
    title: 'Registration Approval', back: 'M33-approval',
    status: { field: 'admin_state', labels: { approved: 'Fully Approved', pending: 'In Chain', rejected: 'Rejected' } },
    tabs: [
      { id: 'applicant', label: '1. Application Header', bn: '১. আবেদন হেডার', icon: '📝', badge: '3' },
      { id: 'tier1', label: '2. Tier 1 Client Manager', bn: '২. স্তর ১ ক্লায়েন্ট ম্যানেজার', icon: '👤', badge: '3' },
      { id: 'tier2', label: '3. Tier 2 1000FiX Admin', bn: '৩. স্তর ২ ১০০০ফিক্স অ্যাডমিন', icon: '🛡️', badge: '4' },
      { id: 'rules', label: '4. Two-Tier Governance Rules', bn: '৪. দ্বি-স্তরীয় সুশাসন', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'applicant', title: 'Registration Application Header', fields: [
        { name: 'partner_id', required: true, label: 'Party' },
        { name: 'party_class', required: true, label: 'Party Classification' },
        { name: 'requested_at', readonly: true, label: 'Requested Timestamp' },
        { name: 'current_step', readonly: true, label: 'Awaiting' },
        { name: 'approval_state', readonly: true, label: 'Approval Inbox State (M63)' },
      ]},
      { tab: 'tier1', title: 'Tier 1 — Client Line Manager Sign-off', fields: [
        { name: 'lm_state', readonly: true, label: 'Line Manager Decision' },
        { name: 'lm_decided_by', readonly: true, label: 'Line Manager Approver' },
        { name: 'lm_on_behalf_of_id', readonly: true, label: 'Decided On Behalf Of' },
        { name: 'lm_decided_at', readonly: true, label: 'Decision Timestamp' },
      ]},
      { tab: 'tier2', title: 'Tier 2 — 1000FiX Corporate Administrator', fields: [
        { name: 'admin_state', readonly: true, label: 'Admin Decision' },
        { name: 'admin_decided_by', readonly: true, label: 'Admin Approver' },
        { name: 'admin_decided_at', readonly: true, label: 'Admin Decision Timestamp' },
        { name: 'reason', label: 'Approval / Rejection Justification' },
      ]},
      { tab: 'rules', title: 'Mandatory Two-Tier Dual Sign-off Rule',
        note: 'Dealer, corporate, and government accounts can only transact after BOTH the client organization line manager and 1000FiX corporate administrator formally approve (BRU-CRM-02 / BRU-CPM-02).',
        fields: [] }
    ] },

  'M33-form-duplicate': { kind: 'model_form', model: 'fix.party.duplicate',
    title: 'Duplicate Candidate', back: 'M33-dedupe',
    status: { field: 'state' },
    tabs: [
      { id: 'candidate', label: '1. Candidate Pair', bn: '১. প্রার্থী যুগল', icon: '👥', badge: '3' },
      { id: 'factors', label: '2. Match Scoring Factors', bn: '২. ম্যাচ ফ্যাক্টর ও স্কোর', icon: '📊', badge: '1' },
      { id: 'stewardship', label: '3. Steward Review & Action', bn: '৩. স্টুয়ার্ড পর্যালোচনা', icon: '⚖️', badge: '3' },
      { id: 'governance', label: '4. Supervised Merge Rules', bn: '৪. তত্ত্বাবধানে মার্জ নিয়ম', icon: '🛡️', badge: '1' }
    ],
    sections: [
      { tab: 'candidate', title: 'Candidate Pair',
        note: 'Name the two parties you believe are the same person. On save the active dedup rules score the pair; the score and its factors are measured, never typed (T-03).',
        fields: [
        { name: 'party_a', required: true, label: 'Party A' },
        { name: 'party_b', required: true, label: 'Party B' },
        { name: 'score', readonly: true, label: 'Composite Match Score (0–100)' },
      ]},
      { tab: 'factors', title: 'Why The Rules Scored It So', fields: [
        { name: 'factors', readonly: true, label: 'Rule Verdicts' },
      ]},
      { tab: 'stewardship', title: 'Data Steward Triage & Resolution', fields: [
        { name: 'state', readonly: true, label: 'Triage State' },
        { name: 'reviewed_by', readonly: true, label: 'Reviewed By' },
        { name: 'decision', label: 'Steward Decision Note' },
      ]},
      { tab: 'governance', title: 'Zero Automated Merge Policy',
        note: 'Confirming a duplicate candidate merely opens a supervised merge request. Automated algorithmic merges are prohibited to eliminate accidental entity corruption.',
        fields: [] }
    ] },

  /* ==================================================================
   * M33 CAPTURE AUDIT 2026-11-14 — each sub-module page captures the
   * record it names (spec section 5, FR-CPM-003/005/014/032/038/044).
   * ================================================================== */
  'M33-addresses': { kind: 'model_list', model: 'fix.bd.address', create: true,
    cols: ['party_id', 'address_tag', 'is_default', 'district', 'upazila', 'postcode', 'latitude', 'longitude'],
    domain: [['party_id', '!=', false]],
    empty: 'No party address is recorded yet. Use "+ New" to add one with its GPS point.' },

  /* 2 Classification (FR-CPM-003). Dealer, corporate and government
   * parties open their two-step registration approval on save. */
  'M33-form-classify': {
    kind: 'model_form', model: 'res.partner',
    title: 'Classify a Party', back: 'M33-directory',
    newLabel: 'Classify a Party',
    status: { field: 'party_status' },
    pickRecord: {
      label: 'Step 1 of 2: choose the party to classify',
      note: 'Any party that is not merged or blacklisted.',
      search: 'Search name / phone',
      choose: 'Classify this party',
      cols: ['name', 'party_class', 'party_status', 'phone', 'email'],
      domain: [['party_status', 'not in', ['merged', 'blacklisted']]],
      empty: 'No party can be classified.'
    },
    sections: [
      { title: 'Step 2 of 2: Set The Party Class',
        note: 'Dealer, Corporate and Government parties transact only after the client line manager and a 1000FiX administrator approve: saving opens that registration approval. A class cannot change while an approval is still open. Seller, brand partner and vendor are roles: add them with "Party (multi-role)".',
        fields: [
        { name: 'name', label: 'Party', readonly: true },
        { name: 'party_class', label: 'Party Class', required: true },
        { name: 'is_company', label: 'Is a Company (legal entity)' },
        { name: 'party_status', label: 'Current Status', readonly: true }
      ]}
    ]
  },

  /* 8 Golden Record & Quality (FR-CPM-032): score the party in front of
   * the steward now, rather than wait for the batch scorer. */
  'M33-form-score': {
    kind: 'model_form', model: 'res.partner',
    title: 'Score a Party', back: 'M33-quality',
    newLabel: 'Score a Party',
    status: { field: 'party_status' },
    pickRecord: {
      label: 'Step 1 of 2: choose the party to score',
      note: 'Completeness, validity and recency are measured from the record itself.',
      search: 'Search name / phone',
      choose: 'Score this party',
      cols: ['name', 'party_class', 'party_status', 'phone', 'email'],
      domain: [['party_status', '!=', 'merged']],
      empty: 'No party to score.'
    },
    saveAction: { method: 'action_score_quality', label: 'Score Now', done: 'Scored: the result is on Quality Scoring', kwargs: {} },
    sections: [
      { title: 'Step 2 of 2: What The Score Reads',
        note: 'Completeness counts name, Bengali name, phone, email, language and at least one role (50%); validity checks the email, an 11-digit mobile and an identity document (30%); recency falls after a year without an update (20%).',
        fields: [
        { name: 'name', label: 'Party', readonly: true },
        { name: 'name_bn', label: 'Bengali Name', readonly: true },
        { name: 'phone', label: 'Phone', readonly: true },
        { name: 'email', label: 'Email', readonly: true },
        { name: 'preferred_language', label: 'Preferred Language', readonly: true },
        { name: 'write_date', label: 'Last Updated', readonly: true }
      ]}
    ]
  },

  /* 9 Consent & DSR (FR-CPM-038): withdrawal at the counter or the contact
   * centre appends a withdrawal record; the grant is never rewritten. */
  'M33-form-withdraw': {
    kind: 'model_form', model: 'fix.consent',
    title: 'Withdraw a Consent', back: 'M33-consent',
    newLabel: 'Withdraw a Consent',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the consent the party withdraws',
      note: 'Granted consents only. The withdrawal takes effect at once on every channel.',
      search: 'Search party',
      choose: 'Withdraw this consent',
      cols: ['partner_id', 'purpose', 'channel', 'date_granted', 'notice_version_id', 'source'],
      domain: [['state', '=', 'granted']],
      empty: 'No granted consent to withdraw.'
    },
    saveAction: { method: 'action_withdraw', label: 'Withdraw Consent', done: 'Withdrawn: suppression is effective on every channel', kwargs: {} },
    sections: [
      { title: 'Step 2 of 2: Confirm The Withdrawal',
        note: 'A new withdrawal record supersedes the grant and both are kept (append-only, T-09). The withdrawal is entered in the record of processing.',
        fields: [
        { name: 'partner_id', label: 'Party', readonly: true },
        { name: 'purpose', label: 'Purpose', readonly: true },
        { name: 'channel', label: 'Channel', readonly: true },
        { name: 'date_granted', label: 'Granted At', readonly: true },
        { name: 'notice_version_id', label: 'Notice Version', readonly: true },
        { name: 'proof', label: 'Proof Reference', readonly: true },
        { name: 'assisted_by_id', label: 'Given By (guardian / representative)', readonly: true }
      ]}
    ]
  },

  /* 9 Consent & DSR (FR-CPM-044, BRU-CPM-15): the record of processing. */
  'M33-processing': { kind: 'model_list', model: 'fix.processing.record', create: true,
    cols: ['occurred_at', 'party_id', 'purpose', 'lawful_basis', 'categories', 'recipients', 'retention_months', 'source'],
    empty: 'No processing is recorded yet. Consent captures and withdrawals record themselves; the Data Protection Officer records any other activity.' },
  'M33-form-processing': {
    kind: 'model_form', model: 'fix.processing.record',
    title: 'Processing Record', back: 'M33-processing',
    tabs: [
      { id: 'what', label: '1. Processing Activity', bn: '১. প্রক্রিয়াকরণ', icon: '🗂️', badge: '5' },
      { id: 'basis', label: '2. Lawful Basis & Retention', bn: '২. আইনি ভিত্তি ও সংরক্ষণ', icon: '⚖️', badge: '4' }
    ],
    sections: [
      { tab: 'what', title: 'What Was Processed',
        note: 'Recorded by the Data Protection Officer. The record is evidence: it cannot be edited, and it is kept at least five years even if the party is erased (BRU-CPM-15).',
        fields: [
        { name: 'party_id', label: 'Party', required: true },
        { name: 'purpose', label: 'Purpose', required: true },
        { name: 'categories', label: 'Data Categories (e.g. name, mobile, service address)', required: true },
        { name: 'recipients', label: 'Recipients / Transfers (empty = stays inside 1000FiX)' },
        { name: 'occurred_at', label: 'Occurred At', required: true }
      ]},
      { tab: 'basis', title: 'Why It Was Lawful',
        note: 'Processing on consent must name the consent relied on (BRU-CPM-07). Legitimate interest is not an enumerated basis under the PDPA 2026.',
        fields: [
        { name: 'lawful_basis', label: 'Lawful Basis', required: true },
        { name: 'consent_id', label: 'Consent Relied On (for the consent basis)' },
        { name: 'retention_months', label: 'Retention (months)', required: true },
        { name: 'note', label: 'Note', type: 'text' }
      ]}
    ]
  },

  /* 12 Status Lifecycle (FR-CPM-005, BRU-CPM-13). */
  'M33-form-party-status': {
    kind: 'model_form', model: 'res.partner',
    title: 'Change Party Status', back: 'M33-status',
    newLabel: 'Change Party Status',
    status: { field: 'party_status' },
    pickRecord: {
      label: 'Step 1 of 2: choose the party',
      note: 'Merged and blacklisted parties are final and are not listed.',
      search: 'Search name / phone',
      choose: 'Change this party\'s status',
      cols: ['name', 'party_class', 'party_status', 'status_reason', 'status_since'],
      domain: [['party_status', 'not in', ['merged', 'blacklisted']]],
      empty: 'No party whose status can change.'
    },
    saveAction: { method: 'action_set_party_status', label: 'Change Status', done: 'Status changed and logged on the party', kwargs: { status: 'party_status', reason: 'status_reason' } },
    sections: [
      { title: 'Step 2 of 2: New Status And Why',
        note: 'Dormant, Blocked, Credit Hold or Blacklisted, always with a reason. Blacklisting is terminal (only the CEO reinstates, BRU-CPM-13) and needs DOFA Tier 2. Making a party active is "Reactivate a Party" or its registration approval.',
        fields: [
        { name: 'name', label: 'Party', readonly: true },
        { name: 'party_status', label: 'New Status', required: true,
          choices: [['dormant', 'Dormant'], ['blocked', 'Blocked'], ['credit_hold', 'Credit Hold'], ['blacklisted', 'Blacklisted (terminal)']] },
        { name: 'status_reason', label: 'Reason', required: true },
        { name: 'status_since', label: 'Current Status Since', readonly: true }
      ]}
    ]
  },
  'M33-form-reactivate': {
    kind: 'model_form', model: 'res.partner',
    title: 'Reactivate a Party', back: 'M33-status',
    newLabel: 'Reactivate a Party',
    status: { field: 'party_status' },
    pickRecord: {
      label: 'Step 1 of 2: choose the party to reactivate',
      note: 'Draft, dormant, blocked and credit-held parties. A dealer, corporate or government party awaiting registration is activated by its approval instead.',
      search: 'Search name / phone',
      choose: 'Reactivate this party',
      cols: ['name', 'party_class', 'party_status', 'status_reason', 'status_since'],
      domain: [['party_status', 'in', ['draft', 'dormant', 'blocked', 'credit_hold']]],
      empty: 'No party is waiting to be reactivated.'
    },
    saveAction: { method: 'action_reactivate_party', label: 'Reactivate', done: 'Reactivated and logged on the party', kwargs: { reason: 'status_reason' } },
    sections: [
      { title: 'Step 2 of 2: Why It Is Reactivated',
        note: 'DOFA Tier 2 (Branch / Operations Manager) only, with a written reason.',
        fields: [
        { name: 'name', label: 'Party', readonly: true },
        { name: 'party_status', label: 'Current Status', readonly: true },
        { name: 'status_reason', label: 'Reason for Reactivation', required: true }
      ]}
    ]
  },

  /* ==================================================================
   * M33 CAPTURE AUDIT PASS 2 (2026-11-19): the spec records (section 10.1)
   * no page could capture, read FR by FR rather than counted.
   * ================================================================== */
  /* 1 / 5 Contact points (FR-CPM-022, BRU-CPM-01, KPI-125) */
  'M33-contact-points': { kind: 'model_list', model: 'fix.contact.point', create: true,
    cols: ['partner_id', 'contact_type', 'value', 'is_primary', 'state', 'verified_at'],
    stateField: 'state',
    actions: [{ m: 'action_request_verification', l: 'Send Verification Code' }],
    empty: 'No contact point is recorded yet. Add the party\'s mobile or email, then send it a code.' },
  'M33-form-contact-point': {
    kind: 'model_form', model: 'fix.contact.point',
    title: 'Contact Point', back: 'M33-contact-points',
    status: { field: 'state', labels: { unverified: 'Unverified', pending: 'Code Sent', verified: 'Verified' } },
    sections: [
      { title: 'The Contact',
        note: 'A mobile (11 digits, 013-019) or an email, WhatsApp or landline. One primary per type. Changing a verified contact makes it unverified again (FR-CPM-022).',
        fields: [
          { name: 'partner_id', label: 'Party', required: true },
          { name: 'contact_type', label: 'Type', required: true },
          { name: 'value', label: 'Number / Address', required: true },
          { name: 'is_primary', label: 'Primary for this Type' }
        ] },
      { title: 'Verification',
        note: 'Verified only by a one-time code: "Send Verification Code" on the list opens the OTP log line; the channel that sends the code marks it verified, and that stamps this contact (BRU-CPM-01).',
        fields: [
          { name: 'state', label: 'Verification', readonly: true },
          { name: 'verified_at', label: 'Verified At', readonly: true },
          { name: 'verification_method', label: 'Verified By', readonly: true }
        ] }
    ]
  },

  /* 1 / 3 Party relationships (FR-CPM-006) */
  'M33-relationships': { kind: 'model_list', model: 'fix.party.relationship', create: true,
    cols: ['party_a_id', 'relation_type', 'party_b_id', 'date_from', 'date_to', 'verified'],
    actions: [
      { m: 'action_verify', l: 'Verify (data steward)' },
      { m: 'action_end', l: 'End Relationship', ask: 'Why does it end?', kwarg: 'reason' }
    ],
    empty: 'No relationship between parties is recorded yet.' },
  'M33-form-relationship': {
    kind: 'model_form', model: 'fix.party.relationship',
    title: 'Party Relationship', back: 'M33-relationships',
    sections: [
      { title: 'Who Is What To Whom',
        note: 'Read as "Party A <relation> Party B": the employer, guardian, referrer, group or representative is Party A. Households and corporate groups are Account Hierarchy links.',
        fields: [
          { name: 'party_a_id', label: 'Party A', required: true },
          { name: 'relation_type', label: 'Relation', required: true },
          { name: 'party_b_id', label: 'Party B', required: true },
          { name: 'date_from', label: 'Since', required: true },
          { name: 'evidence', label: 'Evidence (guardianship document, power of attorney, letter)' }
        ] },
      { title: 'Verification',
        note: 'A data steward who did not record it verifies it against the evidence. A minor\'s or an assisted party\'s consent is taken only through a VERIFIED guardian or authorised representative (BRU-CPM-16).',
        fields: [
          { name: 'verified', label: 'Verified', readonly: true },
          { name: 'verified_by', label: 'Verified By', readonly: true },
          { name: 'verified_at', label: 'Verified At', readonly: true },
          { name: 'date_to', label: 'Ended', readonly: true }
        ] }
    ]
  },

  /* 3 Corporate contact roles (FR-CPM-009/011) */
  'M33-contact-roles': { kind: 'model_list', model: 'fix.party.contact.role', create: true,
    cols: ['corporate_id', 'contact_id', 'role', 'state', 'approval_limit', 'date_from'],
    stateField: 'state',
    actions: [
      { m: 'action_suspend', l: 'Suspend', ask: 'Why is this person suspended?', kwarg: 'reason' },
      { m: 'action_reinstate', l: 'Reinstate', ask: 'Why is this person reinstated?', kwarg: 'reason' },
      { m: 'action_remove', l: 'Remove', ask: 'Why is this person removed?', kwarg: 'reason' }
    ],
    empty: 'No contact role is recorded at a corporate, dealer or government account yet.' },
  'M33-form-contact-role': {
    kind: 'model_form', model: 'fix.party.contact.role',
    title: 'Corporate Contact Role', back: 'M33-contact-roles',
    status: { field: 'state', labels: { active: 'Active', suspended: 'Suspended', removed: 'Removed' } },
    sections: [
      { title: 'The Role',
        note: 'One person, one role, at one corporate, dealer or government account. The account may have no more active people than the contact limit 1000FiX set for it (FR-CPM-011).',
        fields: [
          { name: 'corporate_id', label: 'Corporate Account', required: true },
          { name: 'contact_id', label: 'Contact Person', required: true },
          { name: 'role', label: 'Role', required: true },
          { name: 'approval_limit', label: 'Approval Limit (BDT, approvers only)' },
          { name: 'date_from', label: 'From', required: true }
        ] },
      { title: 'Status',
        note: 'Suspend, reinstate and remove from the list, always with a reason. A removed role is kept.',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'status_note', label: 'Last Status Reason', readonly: true },
          { name: 'date_to', label: 'Removed On', readonly: true }
        ] }
    ]
  },
  'M33-form-contact-limit': {
    kind: 'model_form', model: 'res.partner',
    title: 'Corporate Contact Limit', back: 'M33-contact-roles',
    newLabel: 'Set a Corporate Contact Limit',
    pickRecord: {
      label: 'Step 1 of 2: choose the corporate, dealer or government account',
      search: 'Search name / phone',
      choose: 'Set this account\'s limit',
      cols: ['name', 'party_class', 'party_status', 'delegated_contact_limit'],
      domain: ['|', ['is_company', '=', true], ['party_class', 'in', ['dealer', 'corporate', 'government']]],
      empty: 'No corporate, dealer or government account.'
    },
    sections: [
      { title: 'Step 2 of 2: How Many People May Act For It',
        note: 'Set by a 1000FiX registration administrator (FR-CPM-011); 0 means no limit. A limit below the people already active is refused.',
        fields: [
          { name: 'name', label: 'Account', readonly: true },
          { name: 'delegated_contact_limit', label: 'Most Active Contacts (0 = no limit)', required: true }
        ] }
    ]
  },

  /* 9 Minor / assisted consent (FR-CPM-052, BRU-CPM-16) */
  'M33-form-consent-handling': {
    kind: 'model_form', model: 'res.partner',
    title: 'Consent Handling', back: 'M33-consent',
    newLabel: 'Set Consent Handling (minor / assisted)',
    pickRecord: {
      label: 'Step 1 of 2: choose the party',
      search: 'Search name / phone',
      choose: 'Set this party\'s consent handling',
      cols: ['name', 'party_class', 'consent_handling', 'consent_handling_reason'],
      domain: [['party_status', '!=', 'merged']],
      empty: 'No party.'
    },
    saveAction: { method: 'action_set_consent_handling', label: 'Set Handling', done: 'Consent handling set and logged on the party', kwargs: { handling: 'consent_handling', reason: 'consent_handling_reason' } },
    sections: [
      { title: 'Step 2 of 2: Who May Consent For This Party',
        note: 'A minor or a party needing assistance consents only through a verified guardian or authorised representative, named on the consent (BRU-CPM-16). Anyone serving the party may raise the flag; only the Data Protection Officer clears it back to Standard.',
        fields: [
          { name: 'name', label: 'Party', readonly: true },
          // guarded: the save action takes them (the engine opens its inputs)
          { name: 'consent_handling', label: 'Consent Handling', required: true, readonly: true },
          { name: 'consent_handling_reason', label: 'Reason', required: true, readonly: true }
        ] }
    ]
  },

  /* 11 Credit limit change (FR-CPM-047, BRU-CPM-12, SOD-04) */
  'M33-credit-changes': { kind: 'model_list', model: 'fix.credit.limit.change', create: true,
    cols: ['customer_id', 'current_limit', 'proposed_limit', 'state', 'requested_by', 'decided_by', 'decided_at'],
    stateField: 'state',
    actions: [
      { m: 'action_approve', l: 'Approve and Apply (Finance Manager)', ask: 'Note (optional)', kwarg: 'note' },
      { m: 'action_reject', l: 'Reject', ask: 'Why is it rejected?', kwarg: 'note' },
      { m: 'action_cancel', l: 'Withdraw (requester)' }
    ],
    empty: 'No credit limit change has been requested.' },
  'M33-form-credit-change': {
    kind: 'model_form', model: 'fix.credit.limit.change',
    title: 'Credit Limit Change', back: 'M33-credit-changes',
    status: { field: 'state', labels: { submitted: 'Awaiting Finance Manager', approved: 'Approved and Applied', rejected: 'Rejected', cancelled: 'Withdrawn' } },
    sections: [
      { title: 'The Change Asked For',
        note: 'A Finance Manager (Accounting Administrator) who did not raise it approves it, and the new limit applies at once (BRU-CPM-12, SOD-04). The limit in force when you ask is recorded beside it.',
        fields: [
          { name: 'profile_id', label: 'Credit Profile (customer)', required: true },
          { name: 'current_limit', label: 'Limit Now (BDT)', readonly: true },
          { name: 'proposed_limit', label: 'Proposed Limit (BDT)', required: true },
          { name: 'reason', label: 'Why', required: true, type: 'text' }
        ] },
      { title: 'Decision',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'requested_by', label: 'Requested By', readonly: true },
          { name: 'decided_by', label: 'Decided By', readonly: true },
          { name: 'decided_at', label: 'Decided At', readonly: true },
          { name: 'decision_note', label: 'Decision Note', readonly: true },
          { name: 'applied_at', label: 'Applied At', readonly: true }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M33-dedup-rule': { kind: 'model_list', model: 'fix.dedup.rule',
    cols: ['name', 'active', 'company_id', 'model_id', 'match_fields', 'scope', 'threshold'] },
  'M33-transparency-notice': { kind: 'model_list', model: 'fix.transparency.notice',
    cols: ['active', 'company_id', 'version', 'purpose_set', 'published_at', 'retired_at'] },

  'M33-form-dedup-rule': {
    kind: 'model_form',
    model: 'fix.dedup.rule',
    title: "Dedup Rule",
    back: 'M33-dedup-rule',
    tabs: [
      { id: 'rule', label: '1. Rule Definition', bn: '১. নিয়মের বিবরণ', icon: '📐', badge: '3' },
      { id: 'scope', label: '2. Model & Target Fields', bn: '২. মডেল ও লক্ষ্য ক্ষেত্র', icon: '🎯', badge: '2' },
      { id: 'threshold', label: '3. Scoring & Thresholds', bn: '৩. থ্রেশহোল্ড ও স্কোর', icon: '⚙️', badge: '2' }
    ],
    sections: [
      { tab: 'rule', title: "Rule Definition & Identification", fields: [
        { name: 'name', required: true, label: "Rule Name" },
        { name: 'company_id', required: true, label: "Company" },
        { name: 'active', label: "Active Status" }
      ] },
      { tab: 'scope', title: "Target Scope & Model Selection", fields: [
        { name: 'model_id', required: true, label: "Target Model" },
        { name: 'scope', required: true, label: "Evaluation Scope" }
      ] },
      { tab: 'threshold', title: "Field Match Normalization & Thresholds",
        note: "Defines normalized field weights (phone, NID, legal name) and minimum similarity threshold before raising duplicate candidate alerts.",
        fields: [
          { name: 'match_fields', required: true, label: "Match Fields (comma-separated, e.g. phone,name)" },
          { name: 'threshold', label: "Fuzzy Threshold (maximum edit distance)" },
          { name: 'action', required: true, label: "On a Match (block the save, or flag for the steward)" }
        ] }
    ]
  },

  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M33-dedup-jobs': { kind: 'model_list', model: 'fix.dedup.job', create: true,
    cols: ['started_at', 'name', 'state', 'scheduled', 'records_scanned', 'candidates_found', 'candidates_new', 'finished_at'],
    stateField: 'state',
    actions: [
      { m: 'action_run', l: 'Run Sweep' }
    ],
    note: 'Layer (c) of the three-layer duplicate model, and a prerequisite for adding any new uniqueness key to live data.' },
  'M33-form-dedup-job': {
    kind: 'model_form', model: 'fix.dedup.job',
    title: 'Duplicate Detection Job', back: 'M33-dedup-jobs',
    status: { field: 'state', labels: { draft: 'Draft', running: 'Running', done: 'Completed', failed: 'Failed' } },
    tabs: [
      { id: 'job', label: '1. Job', bn: '১. জব', icon: '🔍' },
      { id: 'result', label: '2. Result', bn: '২. ফলাফল', icon: '📊' }
    ],
    sections: [
      {
        tab: 'job',
        title: 'What To Sweep',
        note: 'These are the SAME rules that warn at data entry — one definition of \'duplicate\', two moments it is applied.',
        fields: [
        { name: 'name', label: 'Job Name', required: true },
        { name: 'rule_ids', label: 'Rules To Run' },
        { name: 'scheduled', label: 'Created By The Nightly Cron' },
        { name: 'state', label: 'State', required: true }
        ]
      },
      {
        tab: 'result',
        title: 'What It Found',
        note: 'A uniqueness key cannot be added while stored data violates it, so this layer must run and its merges be worked before any new constraint reaches live data.',
        fields: [
        { name: 'started_at', label: 'Started' },
        { name: 'finished_at', label: 'Finished' },
        { name: 'records_scanned', label: 'Records Scanned' },
        { name: 'blocks_compared', label: 'Blocks Compared' },
        { name: 'candidates_found', label: 'Pairs Matched' },
        { name: 'candidates_new', label: 'New Candidates' },
        { name: 'summary', label: 'Per-Rule Summary' },
        { name: 'error_text', label: 'Error' }
        ]
      }
    ]
  },

  /* --- Real-Customer Cut-over (readiness report §7 step 5, 2026-11-08) --- */
  'M33-import-batches': { kind: 'model_list', model: 'fix.party.import.batch', create: true,
    cols: ['name', 'sheet_kind', 'state', 'line_count', 'created_count', 'matched_count', 'quarantined_count', 'error_count'],
    stateField: 'state',
    actions: [
      { m: 'action_stage', l: '1. Stage spreadsheet' },
      { m: 'action_validate', l: '2. Validate & match' },
      { m: 'action_import', l: '3. Import as draft parties' },
      { m: 'action_decide_registrations', l: '4. Decide registrations (two-tier)' },
      { m: 'action_assign_roles', l: 'Assign classification roles' },
      { m: 'action_register_suppliers', l: 'Register suppliers (vendor ledger)' },
      { m: 'action_score_quality', l: 'Score golden-record quality' },
      { m: 'action_reconcile', l: '5. Reconcile counts' },
      { m: 'action_rollback', l: 'Rollback this batch' },
    ],
    links: [
      { s: 'M33-import-lines', l: 'Import Lines (per-row audit)' },
      { s: 'M33-approval', l: 'Registration Approvals' },
    ],
    note: 'The governed party loader: stage the source spreadsheet, validate (every cleansing rule recorded per line), import as draft parties with legacy keys, decide registrations, reconcile counts. Every action appends to the batch decision log.' },
  'M33-import-lines': { kind: 'model_list', model: 'fix.party.import.line', create: false,
    cols: ['row_no', 'raw_name', 'legacy_reference', 'clean_name', 'line_state', 'division_id', 'phone_norm', 'email_norm', 'matched_partner_id', 'created_partner_id'],
    stateField: 'line_state' },
  'M33-form-party-import': {
    kind: 'model_form', model: 'fix.party.import.batch',
    title: 'Party Import Batch', back: 'M33-import-batches',
    status: { field: 'state', labels: {
      draft: 'Draft', staged: 'Staged', validated: 'Validated',
      imported: 'Imported', approved: 'Registrations decided', reconciled: 'Reconciled' } },
    tabs: [
      { id: 'src', label: '1. Source & Rules', bn: '১. সোর্স ও নিয়ম', icon: '📄', badge: '5' },
      { id: 'out', label: '2. Outcome', bn: '২. ফলাফল', icon: '📊', badge: '6' },
      { id: 'log', label: '3. Decision Log', bn: '৩. সিদ্ধান্ত লগ', icon: '🗂️', badge: '1' }
    ],
    sections: [
      { tab: 'src', title: 'Source Spreadsheet & Lawful Basis',
        note: "Attach the customer list export, choose the sheet layout and the PDPA lawful basis (legitimate interest is NOT an enumerated basis under Act 63 of 2026). Save, then run Stage → Validate → Import → Decide Registrations → Reconcile from the list's command bar.",
        fields: [
          { name: 'name', label: 'Batch', readonly: true },
          { name: 'source_file', label: 'Source Spreadsheet (.xlsx)', type: 'file' },
          { name: 'source_filename', label: 'File Name' },
          { name: 'sheet_kind', label: 'Sheet Layout', required: true },
          { name: 'import_ref', label: 'Import Reference (legacy grouping)', required: true },
          { name: 'lawful_basis', label: 'PDPA Lawful Basis', required: true }
        ] },
      { tab: 'out', title: 'Counts',
        fields: [
          { name: 'line_count', label: 'Source Rows', readonly: true },
          { name: 'created_count', label: 'Created Parties', readonly: true },
          { name: 'matched_count', label: 'Matched Existing', readonly: true },
          { name: 'quarantined_count', label: 'Quarantined', readonly: true },
          { name: 'error_count', label: 'Errors', readonly: true },
          { name: 'hierarchy_count', label: 'Branch Links (hierarchy)', readonly: true }
        ] },
      { tab: 'log', title: 'Audit Trail',
        fields: [
          { name: 'decision_log', label: 'Decision Log (who, when, what)', readonly: true, type: 'text' }
        ] }
    ]
  },
};

/* built-in report chips -> the computed report screen that shows them */
export const REPORT_ROUTES = {
  'M33:Customer Growth by District': 'M33-rpt-growth',
  'M33:Data Quality Scorecard': 'M33-rpt-scorecard',
  'M33:Duplicate Merge Audit': 'M33-rpt-mergeaudit',
  'M33:Consent Coverage Report': 'M33-rpt-consentcov',
  'M33:Credit Exposure by Segment': 'M33-rpt-creditexp',
  'M33:Corporate Hierarchy Map': 'M33-rpt-hiermap'
};

/* data-entry form chips -> the module's IN-WORKSPACE D365 form screens. */
export const FORM_CHIPS = {
  'M33:Duplicate Detection Job': 'M33-form-dedup-job',
  'M33:Party Master': 'M33-form-party',
  'M33:Party (multi-role)': 'M33-form-role',
  'M33:Address with GPS': 'M33-form-address',
  'M33:Identity Document': 'M33-form-identity',
  'M33:Credit Profile': 'M33-form-credit',
  'M33:Merge Request': 'M33-form-merge',
  'M33:Classify a Party': 'M33-form-classify',
  'M33:Account Hierarchy Link': 'M33-form-hierarchy',
  'M33:Dedup Rule': 'M33-form-dedup-rule',
  'M33:Score a Party': 'M33-form-score',
  // per-attribute survivorship (FR-CPM-031) is M64's golden-rule register (spec 12.1)
  'M33:Survivorship Rule': 'M64-form-goldenrule',
  'M33:Consent Record': 'M33-form-consent',
  'M33:Withdraw a Consent': 'M33-form-withdraw',
  'M33:Data-Subject Request': 'M33-form-dsr',
  'M33:Transparency Notice': 'M33-form-transparency',
  'M33:Processing Record': 'M33-form-processing',
  'M33:Change Party Status': 'M33-form-party-status',
  'M33:Reactivate a Party': 'M33-form-reactivate',
  // capture pass 2 (2026-11-19)
  'M33:Contact Point': 'M33-form-contact-point',
  'M33:Party Relationship': 'M33-form-relationship',
  'M33:Corporate Contact Role': 'M33-form-contact-role',
  'M33:Corporate Contact Limit': 'M33-form-contact-limit',
  'M33:Consent Handling': 'M33-form-consent-handling',
  'M33:Credit Limit Change': 'M33-form-credit-change',
  'M33:__by_model__': {
    'fix.dedup.job': 'M33-form-dedup-job',
    'fix.transparency.notice': 'M33-form-transparency',
    'fix.dedup.rule': 'M33-form-dedup-rule',
    'fix.party.import.batch': 'M33-form-party-import',
    'res.partner': 'M33-form-party',
    'fix.party.role': 'M33-form-role',
    'fix.bd.address': 'M33-form-address',
    'fix.identity.document': 'M33-form-identity',
    'fix.credit.profile': 'M33-form-credit',
    'fix.party.merge': 'M33-form-merge',
    'fix.consent': 'M33-form-consent',
    'fix.rights.request': 'M33-form-dsr',
    'fix.segment': 'M33-form-segment',
    'fix.party.hierarchy': 'M33-form-hierarchy',
    'fix.registration.approval': 'M33-form-approval',
    'fix.party.duplicate': 'M33-form-duplicate',
    'fix.processing.record': 'M33-form-processing',
    'fix.contact.point': 'M33-form-contact-point',
    'fix.party.relationship': 'M33-form-relationship',
    'fix.party.contact.role': 'M33-form-contact-role',
    'fix.credit.limit.change': 'M33-form-credit-change'
  },
  'M33:__by_screen__': {
    'M33-dedup-jobs': 'M33-form-dedup-job',
    'M33-import-batches': 'M33-form-party-import',
    'M33-directory': 'M33-form-party',
    'M33-party': 'M33-form-role',
    'M33-form-party': 'M33-form-party',
    'M33-hierarchy': 'M33-form-hierarchy',
    'M33-identity': 'M33-form-identity',
    'M33-approval': 'M33-form-approval',
    'M33-dedupe': 'M33-form-duplicate',
    'M33-merge': 'M33-form-merge',
    'M33-consent': 'M33-form-consent',
    'M33-dsr': 'M33-form-dsr',
    'M33-segments': 'M33-form-segment',
    'M33-credit': 'M33-form-credit',
    'M33-dedup-rule': 'M33-form-dedup-rule',
    'M33-transparency-notice': 'M33-form-transparency',
    'M33-addresses': 'M33-form-address',
    'M33-processing': 'M33-form-processing',
    'M33-contact-points': 'M33-form-contact-point',
    'M33-relationships': 'M33-form-relationship',
    'M33-contact-roles': 'M33-form-contact-role',
    'M33-credit-changes': 'M33-form-credit-change'
  }
};

/* the models behind each chip (kept for the last-resort dialog fallback) */
export const FORM_MODELS = {
  'M33:Duplicate Detection Job': 'fix.dedup.job',
  'M33:Party Master': 'res.partner',
  'M33:Party (multi-role)': 'fix.party.role',
  'M33:Address with GPS': 'fix.bd.address',
  'M33:Identity Document': 'fix.identity.document',
  'M33:Credit Profile': 'fix.credit.profile',
  'M33:Merge Request': 'fix.party.merge',
  'M33:Processing Record': 'fix.processing.record',
  'M33:Contact Point': 'fix.contact.point',
  'M33:Party Relationship': 'fix.party.relationship',
  'M33:Corporate Contact Role': 'fix.party.contact.role',
  'M33:Credit Limit Change': 'fix.credit.limit.change'
};

/* the module's "+ New" surface: the party itself is the anchor record. */
export const CREATE = {
  M33: { screen: 'M33-form-party', model: 'res.partner', label: 'Party' }
};
