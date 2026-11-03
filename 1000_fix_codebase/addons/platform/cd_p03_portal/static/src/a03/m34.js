/** @odoo-module **/
/* A03 · Customer Experience — M34 CX, Feedback & Complaints (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 69.
 * Surveys and complaints are real (fix.survey / fix.complaint); detractor
 * follow-ups, throttling and reviews are the new fix.cx.* records. */

export const MODULE = {
  area: 'A03', code: 'M34', en: 'CX, Feedback & Complaints', title: 'M34 · CX, Feedback & Complaints',
  bn: 'অভিজ্ঞতা ও অভিযোগ', icon: '💬',
  desc: 'CSAT / NPS / CES surveys, complaint management with escalation, closed-loop recovery, goodwill authority, VoC analytics and reviews.',
  kpis: [
    { l: 'CSAT', m: 'csat', suffix: '%' },
    { l: 'NPS', m: 'nps' },
    { l: 'Open Complaints', m: 'open_complaints' },
    { l: 'Complaint SLA Met', m: 'complaint_sla_met', suffix: '%' },
    { l: 'Detractor Follow-ups', m: 'detractor_followups' },
    { l: 'Survey Response', m: 'survey_response', suffix: '%' }
  ],
  groups: [
    { en: 'Surveys', screens: [
      { id: 'M34-design', en: 'Survey Designer', bn: 'সার্ভে ডিজাইনার', t: 'f' },
      { id: 'M34-responses', en: 'Responses & Ratings', bn: 'প্রতিক্রিয়া', t: 'g' },
      { id: 'M34-throttle', en: 'Distribution & Throttling', bn: 'বিতরণ ও থ্রটলিং', t: 'g' }
    ]},
    { en: 'Complaints', screens: [
      { id: 'M34-complaints', en: 'Complaints', bn: 'অভিযোগ', t: 'g' },
      { id: 'M34-form-complaint', en: 'Complaint Record', bn: 'অভিযোগ রেকর্ড', t: 'f' },
      { id: 'M34-escalation', en: 'Severity & Escalation', bn: 'তীব্রতা ও এসক্যালেশন', t: 'g' },
      { id: 'M34-goodwill', en: 'Goodwill Authority', bn: 'সদিচ্ছা কর্তৃত্ব', t: 'g' }
    ]},
    { en: 'Closed Loop', screens: [
      { id: 'M34-detractor', en: 'Detractor Recovery', bn: 'ডিট্রাক্টর রিকভারি', t: 'c' },
      { id: 'M34-journey', en: 'Journey Measurement', bn: 'যাত্রা পরিমাপ', t: 'r' }
    ]},
    { en: 'Voice of Customer', screens: [
      { id: 'M34-voc', en: 'VoC Analytics', bn: 'ভিওসি বিশ্লেষণ', t: 'd' },
      { id: 'M34-reviews', en: 'Reviews & Testimonials', bn: 'রিভিউ', t: 'g' },
      { id: 'M34-byybranch', en: 'Experience by Branch/Tech', bn: 'শাখাভিত্তিক অভিজ্ঞতা', t: 'r' }
    ]},
    { en: 'Survey Designer', bn: 'সার্ভে ডিজাইনার', screens: [
      { id: 'M34-survey-templates', en: 'Survey Instruments', bn: 'সার্ভে ইনস্ট্রুমেন্ট', t: 'g' },
      { id: 'M34-form-survey-template', en: 'Survey Instrument', bn: 'ইনস্ট্রুমেন্ট ফর্ম', t: 'f' },
      { id: 'M34-survey-answers', en: 'Collected Answers', bn: 'সংগৃহীত উত্তর', t: 'g' }
    ]}
  ],
  reports: ['CSAT by Branch & Technician', 'NPS Trend & Drivers', 'Complaint Category Pareto', 'Closed-Loop Effectiveness', 'Review Sentiment Summary'],
  forms: ['Survey', 'Complaint', 'Goodwill Credit', 'Detractor Follow-up', 'Survey Instrument'],
  cross: ['M01 Service Orders', 'M20 Credit Notes', 'M23 QMS / NCR'],
  freg: { src: 69, sub: [
    ['1', 'Survey Design & Distribution', 10, { model: 'fix.survey', cols: ['state', 'customer_id', 'service_order_id', 'rating', 'nps_score', 'comment'], screens: ['M34-design', 'M34-responses'] }],
    ['2', 'CSAT / NPS / CES', 7, { model: 'fix.survey', cols: ['state', 'customer_id', 'service_order_id', 'rating', 'nps_score', 'comment'], screens: ['M34-responses', 'M34-rpt-csat', 'M34-rpt-nps'] }],
    ['3', 'Multi-Parameter Ratings', 6, { model: 'fix.cx.review', cols: ['name', 'state', 'customer_id', 'source', 'service_order_id', 'rating'], screens: ['M34-reviews'] }],
    ['4', 'Closed Feedback Loop', 9, { model: 'fix.cx.followup', cols: ['name', 'state', 'customer_id', 'survey_id', 'reason', 'owner_id'], screens: ['M34-detractor', 'M34-rpt-loop'] }],
    ['5', 'Complaint Management', 14, { model: 'fix.complaint', cols: ['name', 'state', 'customer_id', 'dofa_tier_required', 'dofa_approved', 'dofa_approved_by'], screens: ['M34-complaints'] }],
    ['6', 'Categorisation & SLA', 8, { model: 'fix.complaint', cols: ['name', 'state', 'customer_id', 'dofa_tier_required', 'dofa_approved', 'dofa_approved_by'], screens: ['M34-escalation', 'M34-rpt-pareto'] }],
    ['7', 'Compensation & Goodwill', 6, { model: 'fix.credit.note', cols: ['invoice_id', 'amount', 'state', 'approved_by', 'issued_at'], screens: ['M34-goodwill'], domain: [['reason_code', '=', 'goodwill']] }],
    ['8', 'VoC Analytics', 9, { model: 'fix.survey', cols: ['service_order_id', 'customer_id', 'rating', 'nps_score', 'ces_score'], screens: ['M34-voc', 'M34-journey', 'M34-rpt-sentiment', 'M34-responses'], domain: [['state', '=', 'responded']] }]
  ] }
};

export const SCREENS = {
  'M34-design': { kind: 'table_report', module: 'M34', report: 'survey_blueprint', title: 'Survey Designer', period: false },
  'M34-responses': { kind: 'model_list', model: 'fix.survey', stateField: 'state',
    cols: ['service_order_id', 'customer_id', 'operating_unit_id', 'rating', 'nps_score', 'state', 'comment'] },
  'M34-throttle': { kind: 'model_list', model: 'fix.cx.throttle', stateField: 'suppressed',
    cols: ['partner_id', 'channel', 'max_per_month', 'sent_this_month', 'last_sent_at', 'suppressed', 'reason'] },
  'M34-complaints': { kind: 'model_list', model: 'fix.complaint', stateField: 'state',
    cols: ['name', 'customer_id', 'category', 'severity', 'state', 'operating_unit_id', 'service_order_id'],
    // The lifecycle moves only through these actions; the state field is
    // read-only on the form (A03 workflow audit, 2026-11-03).
    // ISO 10002 cl. 7, in lifecycle order (A03 P2, M34-3/M34-6).
    actions: [
      { m: 'action_take_ownership', l: 'Take Ownership' },
      { m: 'action_assign', l: 'Assign Owner', ask: 'Login of the person who will own this complaint', kwarg: 'assignee' },
      { m: 'action_assess', l: 'Assess', ask: 'Confirm the severity (minor, major or critical); leave blank to keep it', kwarg: 'severity' },
      { m: 'action_reassess', l: 'Reassess Severity', ask: 'New severity (minor, major or critical), then the reason', kwarg: 'severity' },
      { m: 'action_investigate', l: 'Start Investigation' },
      { m: 'action_raise_ncr', l: 'Raise NCR' },
      { m: 'action_record_root_cause', l: 'Record Root Cause' },
      { m: 'action_verify_root_cause', l: 'Verify 5-Why' },
      { m: 'action_open_capa', l: 'Open CAPA' },
      { m: 'action_request_verification', l: 'Send CAPA to Verification' },
      { m: 'action_request_approval', l: 'Request Concession Approval', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_respond', l: 'Send Response', ask: 'Decision and remedy given to the customer', kwarg: 'response' },
      { m: 'action_customer_accept', l: 'Customer Accepted', ask: 'What the customer said (optional)', kwarg: 'note' },
      { m: 'action_customer_reject', l: 'Customer Rejected', ask: 'Why the customer rejected the response', kwarg: 'reason' },
      { m: 'action_close', l: 'Close Complaint', ask: 'Resolution given to the customer', kwarg: 'resolution' },
      { m: 'action_decline', l: 'Decline (Not Upheld)', ask: 'Why the complaint is not upheld', kwarg: 'reason' },
      { m: 'action_reopen', l: 'Reopen', ask: 'Why the complaint is reopened', kwarg: 'reason' }
    ] },
  'M34-escalation': { kind: 'table_report', module: 'M34', report: 'complaint_escalation', title: 'Severity & Escalation', period: false },
  'M34-goodwill': { kind: 'table_report', module: 'M34', report: 'goodwill_authority', title: 'Goodwill Authority', period: false },
  'M34-detractor': { kind: 'model_list', model: 'fix.cx.followup', stateField: 'state',
    cols: ['survey_id', 'customer_id', 'reason', 'owner_id', 'due_date', 'state'],
    actions: [
      { m: 'action_close_recovered', l: 'Mark Recovered' },
      { m: 'action_raise_complaint', l: 'Raise / Link Complaint' }
    ] },
  'M34-journey': { kind: 'table_report', module: 'M34', report: 'journey_measurement', title: 'Journey Measurement', period: false },
  'M34-voc': { kind: 'table_report', module: 'M34', report: 'voc_analytics', title: 'VoC Analytics', period: false },
  'M34-reviews': { kind: 'model_list', model: 'fix.cx.review', stateField: 'state',
    cols: ['name', 'source', 'customer_id', 'rating', 'state', 'reviewed_at'] },
  'M34-byybranch': { kind: 'table_report', module: 'M34', report: 'experience_by_branch', title: 'Experience by Branch/Tech', period: false },

  /* Report chips -> their own computed pack */
  'M34-rpt-csat': { kind: 'table_report', module: 'M34', report: 'csat_by_branch', title: 'CSAT by Branch & Technician', period: false },
  'M34-rpt-nps': { kind: 'table_report', module: 'M34', report: 'nps_trend', title: 'NPS Trend & Drivers', period: false },
  'M34-rpt-pareto': { kind: 'table_report', module: 'M34', report: 'complaint_pareto', title: 'Complaint Category Pareto', period: false },
  'M34-rpt-loop': { kind: 'table_report', module: 'M34', report: 'closed_loop', title: 'Closed-Loop Effectiveness', period: false },
  'M34-rpt-sentiment': { kind: 'table_report', module: 'M34', report: 'review_sentiment', title: 'Review Sentiment Summary', period: false },

  /* ============ D365 IN-WORKSPACE MULTI-TAB FORMS ============ */
  'M34-form-survey': {
    lines: {
      field: 'answer_ids',
      title: 'Answers Given',
      note: 'One row per answer rather than a JSON blob, so that "average punctuality by branch this quarter" is a query and not a parsing job. A question whose branch condition was not met is absent rather than blank: "not asked" and "asked and declined" mean different things.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'question_code', label: 'Question', required: true },
        { name: 'question_type', label: 'Type' },
        { name: 'value_numeric', label: 'Score' },
        { name: 'value_text', label: 'Answer' },
        { name: 'answered_at', label: 'Answered At' }
      ]
    },
    kind: 'model_form',
    model: 'fix.survey',
    title: 'Survey',
    back: 'M34-responses',
    status: { field: 'state', labels: { pending: 'Pending', sent: 'Sent', responded: 'Responded', expired: 'Expired' } },
    tabs: [
      { id: 'general', label: 'Survey Details', bn: 'জরিপ বিবরণ', icon: '📝' },
      { id: 'response', label: 'VoC Rating & NPS', bn: 'রেটিং ও এনপিএস', icon: '⭐' },
      { id: 'audit', label: 'Metadata & Origin', bn: 'মেটাডাটা ও উৎস', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Survey Details',
        note: 'The fixed CX instrument on a service order. Send it, then record the response here.',
        fields: [
          { name: 'service_order_id', required: true, label: 'Service Order' },
          { name: 'customer_id', label: 'Customer' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'state', required: true, label: 'State' }
        ]
      },
      {
        tab: 'response',
        title: 'Customer Response & VoC',
        note: 'Ratings 1 to 5 are recorded; the NPS score is computed automatically by the model.',
        fields: [
          { name: 'rating', label: 'Overall Rating (1 to 5)' },
          { name: 'nps_score', readonly: true, label: 'NPS Score (computed)' },
          { name: 'comment', label: 'Customer Feedback', type: 'text' }
        ]
      },
      {
        tab: 'audit',
        title: 'Source & Metadata',
        fields: [
          { name: 'source_event_id', readonly: true, label: 'Source Event ID' }
        ]
      }
    ]
  },

  'M34-form-complaint': { kind: 'model_form', model: 'fix.complaint',
    title: 'ISO 10002 Customer Complaint & Escalation Master', back: 'M34-complaints',
    status: { field: 'state' },
    tabs: [
      { id: 'intake', label: '1. Intake & Classification', bn: '১. গ্রহণ ও তীব্রতা', icon: '⚠️', badge: '12' },
      { id: 'acknowledgment', label: '2. Acknowledgment & SLA', bn: '২. স্বীকৃতি', icon: '⏱️', badge: '6' },
      { id: 'rca_5why', label: '3. 5-Why Root Cause Analysis', bn: '৩. ফাইভ-হোয়াই মূল কারণ', icon: '🔍', badge: '5' },
      { id: 'capa', label: '4. CAPA & Quality NCR', bn: '৪. ক্যাপা ও এনসিআর', icon: '🛠️', badge: '4' },
      { id: 'concession', label: '5. Concession & DOFA Approval', bn: '৫. ছাড়', icon: '💳', badge: '10' },
      { id: 'docs', label: '6. Evidence & Documents', bn: '৬. প্রমাণ ও নথি', icon: '📑', badge: '2' },
      { id: 'resolution', label: '7. Response, Decision & Closure', bn: '৭. চূড়ান্ত নিষ্পত্তি', icon: '✅', badge: '13' }
    ],
    sections: [
      { tab: 'intake', title: 'Complaint Intake & Severity Tier', fields: [
        { name: 'name', required: true, label: 'Complaint Reference Code' },
        { name: 'customer_id', required: true, label: 'Aggrieved Customer Party' },
        { name: 'service_order_id', label: 'Linked Service Order Ref' },
        { name: 'operating_unit_id', label: 'Branch / Operating Unit' },
        { name: 'category', required: true, label: 'ISO 10002 Complaint Category' },
        { name: 'severity', required: true, label: 'Severity Level (Minor / Major / Critical)' },
        { name: 'state', readonly: true, label: 'Complaint Workflow State' },
        { name: 'owner_id', readonly: true, label: 'Complaint Owner (Assess / Take Ownership / Assign)' },
        { name: 'assessed_at', readonly: true, label: 'Assessed At' },
        { name: 'intake_channel', readonly: true, label: 'Received Through' },
        { name: 'conversation_id', readonly: true, label: 'Contact-Centre Conversation' },
        { name: 'escalation_owner_id', readonly: true, label: '72-Hour Escalation Owner' },
      ]},
      { tab: 'acknowledgment', title: 'Statutory 24-Hour Customer Acknowledgment (FLAW-34.3)',
        note: 'ISO 10002 and company SLA mandate formal customer acknowledgment via SMS/email within 24 hours of complaint intake.',
        fields: [
          { name: 'acknowledged_at', label: 'Formal Customer Acknowledgment Timestamp', readonly: true },
          { name: 'description', required: true, label: 'Customer Grievance Statement / Description', type: 'text' },
          { name: 'sla_policy_id', readonly: true, label: 'SLA Policy (from severity and branch)' },
          { name: 'sla_resolution_state', readonly: true, label: 'Resolution SLA' },
          { name: 'escalated_at', readonly: true, label: 'Escalated At' },
          { name: 'quality_warning', readonly: true, label: 'Branch Quality Warning' },
        ]},
      { tab: 'rca_5why', title: 'Mandatory 5-Why Root Cause Analysis (FLAW-34.1)',
        note: 'Major and Critical complaints are not answered or closed until the 5-Why is written and then verified by a second person (Verify 5-Why). Editing it afterwards withdraws the verification.',
        fields: [
          { name: 'root_cause_5why', label: '5-Why Root Cause Investigation Details', type: 'text' },
          { name: 'root_cause_author_id', readonly: true, label: '5-Why Written By' },
          { name: 'five_why_verified', readonly: true, label: '5-Why Verified' },
          { name: 'five_why_verified_by_id', readonly: true, label: '5-Why Verified By' },
          { name: 'five_why_verified_at', readonly: true, label: '5-Why Verified At' },
        ]},
      { tab: 'capa', title: 'Corrective & Preventive Action (CAPA) & Quality NCR', fields: [
        { name: 'capa_id', label: 'Linked CAPA Action Plan Ref' },
        { name: 'capa_stub_ref', label: 'CAPA Cross-Module Tracking Code' },
        { name: 'ncr_id', readonly: true, label: 'Non-Conformance Report (NCR) Ref' },
        { name: 'ncr_stub_ref', readonly: true, label: 'M23 Quality Management NCR Reference' },
      ]},
      { tab: 'concession', title: 'Financial Goodwill Concession & DOFA Gating (FLAW-34.2)',
        note: 'Financial concessions (refunds, goodwill credits, free accessories) mandate DOFA authorization before voucher issuance or accounts posting.',
        fields: [
          { name: 'concession_amount', label: 'Concession Commercial Amount (BDT)' },
          { name: 'concession_type', label: 'Concession Category (Credit Note / Waiver / Replacement)' },
          { name: 'dofa_justification', label: 'DOFA Approval Justification (mandatory at Tier 2+)', type: 'text' },
          { name: 'dofa_tier_required', readonly: true, label: 'DOFA Tier Required' },
          { name: 'concession_approved', readonly: true, label: 'DOFA Concession Authorization Granted' },
          { name: 'concession_approver_id', readonly: true, label: 'Authorized DOFA Executive Approver' },
          { name: 'approval_state', readonly: true, label: 'Approval Request (M63)' },
          { name: 'concession_settled_amount', readonly: true, label: 'Documented (Credit Note / Voucher)' },
          { name: 'concession_settlement_note', readonly: true, label: 'Settlement', type: 'text' },
          { name: 'currency_id', label: 'Transaction Currency', readonly: true },
        ]},
      { tab: 'docs', title: 'Complaint Evidence & Document Repository (ISO 10002 / CRPA 2009)',
        note: 'Damage photographs, written complaint letters, technician incident reports, CCTV references and signed settlement release forms attach to this record (Odoo attachments). The checksummed document repository (fix.document, M24 — SHA-256 + retention class) is the estate-wide evidence path; a dedicated complaint-evidence relation is a declared platform gap.',
        fields: [
          { name: 'ncr_id', label: 'Quality NCR Evidence Ref', readonly: true },
          { name: 'capa_id', label: 'CAPA Action Evidence Ref', readonly: true },
        ]},
      { tab: 'resolution', title: 'Response, Customer Decision & Closure (ISO 10002 cl. 7.7-7.9)',
        note: 'Send Response records what was offered; the customer then accepts or rejects it. Only an accepted response closes, and closing raises the concession credit note or voucher and the post-resolution survey.',
        fields: [
        { name: 'customer_response', readonly: true, label: 'Response Given to the Customer', type: 'text' },
        { name: 'responded_at', readonly: true, label: 'Responded At' },
        { name: 'customer_decision', readonly: true, label: 'Customer Decision' },
        { name: 'customer_decision_note', readonly: true, label: 'Customer Comment', type: 'text' },
        { name: 'customer_rejection_count', readonly: true, label: 'Responses Rejected' },
        { name: 'resolution', readonly: true, label: 'Formal Customer Resolution Statement (set on Close)', type: 'text' },
        { name: 'closed_at', readonly: true, label: 'Closed At' },
        { name: 'reopen_count', readonly: true, label: 'Times Reopened' },
        { name: 'reopen_reason', readonly: true, label: 'Last Reopen Reason', type: 'text' },
        { name: 'company_id', label: 'Operating Corporate Legal Entity' },
        { name: 'create_date', label: 'Complaint Intake Timestamp', readonly: true },
        { name: 'write_date', label: 'Final Resolution Timestamp', readonly: true },
      ]}
    ] },

  'M34-form-goodwill': {
    kind: 'model_form',
    model: 'fix.credit.note',
    title: 'Goodwill Credit',
    back: 'M34-goodwill',
    status: { field: 'state', labels: { draft: 'Draft', pending_approval: 'Pending Approval', approved: 'Approved', rejected: 'Rejected', issued: 'Issued' } },
    tabs: [
      { id: 'general', label: 'Goodwill Credit', bn: 'সদিচ্ছা ক্রেডিট', icon: '💳' },
      { id: 'approval', label: 'DOFA Approval', bn: 'অনুমোদন', icon: '✍️' },
      { id: 'posting', label: 'GL Posting', bn: 'জিএল পোস্টিং', icon: '🏛️' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Goodwill Credit Details',
        note: 'A goodwill credit is a real M20 credit note with reason Goodwill. Credits above 25,000 BDT require manager DOFA approval before issuance.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Original Invoice' },
          { name: 'amount', required: true, label: 'Credit Amount (BDT)' },
          { name: 'reason_code', required: true, value: 'goodwill', label: 'Reason Code' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
        ]
      },
      {
        tab: 'approval',
        title: 'Approval Governance',
        fields: [
          { name: 'state', readonly: true, label: 'Approval State' },
          { name: 'approved_by', readonly: true, label: 'Approved By' }
        ]
      },
      {
        tab: 'posting',
        title: 'GL Posting & Settlement',
        fields: [
          { name: 'issued_at', readonly: true, label: 'Issued Timestamp' },
          { name: 'gl_note', readonly: true, label: 'General Ledger Note' }
        ]
      }
    ]
  },

  'M34-form-followup': {
    kind: 'model_form',
    model: 'fix.cx.followup',
    title: 'Detractor Follow-up',
    back: 'M34-detractor',
    status: { field: 'state', labels: { open: 'Open', contacted: 'Customer Contacted', recovered: 'Recovered', closed: 'Closed — no recovery' } },
    tabs: [
      { id: 'general', label: 'Recovery Task', bn: 'পুনরুদ্ধার কাজ', icon: '🎯' },
      { id: 'outcome', label: 'Recovery Outcome', bn: 'ফলাফল ও নোট', icon: '📋' },
      { id: 'audit', label: 'Status & Timeline', bn: 'অবস্থা ও সময়সীমা', icon: '⏱️' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Recovery Assignment',
        note: 'A follow-up is opened from a detractor response; recovering the customer is a recorded outcome.',
        fields: [
          { name: 'survey_id', required: true, label: 'Survey Response' },
          { name: 'reason', required: true, label: 'Detractor Trigger' },
          { name: 'owner_id', label: 'Recovery Owner' },
          { name: 'due_date', required: true, label: 'Follow-up Due Date' },
          { name: 'complaint_id', readonly: true, label: 'Linked Complaint' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Outreach & Recovery Notes',
        fields: [
          { name: 'notes', label: 'Recovery Notes & Narrative', type: 'text' }
        ]
      },
      {
        tab: 'audit',
        title: 'Status & Completion',
        fields: [
          { name: 'state', required: true, label: 'Recovery Status' },
          { name: 'closed_at', readonly: true, label: 'Closed At' }
        ]
      }
    ]
  },

  'M34-form-throttle': {
    kind: 'model_form',
    model: 'fix.cx.throttle',
    title: 'Distribution Throttle',
    back: 'M34-throttle',
    status: { field: 'suppressed', labels: { true: 'Suppressed', false: 'Active' } },
    tabs: [
      { id: 'general', label: 'Throttle Policy', bn: 'থ্রটল নীতি', icon: '🛡️' },
      { id: 'audit', label: 'Status & Overrides', bn: 'অবস্থা ও ওভাররাইড', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Outreach Throttle Rule',
        note: 'One rule per customer and channel. Suppression prevents fatigue across customer touchpoints.',
        fields: [
          { name: 'partner_id', required: true, label: 'Customer' },
          { name: 'channel', required: true, label: 'Communication Channel' },
          { name: 'max_per_month', required: true, label: 'Max Surveys per Month' }
        ]
      },
      {
        tab: 'audit',
        title: 'Suppression Status',
        fields: [
          { name: 'suppressed', label: 'Suppression Active' },
          { name: 'reason', label: 'Suppression Reason' }
        ]
      }
    ]
  },

  'M34-form-review': {
    kind: 'model_form',
    model: 'fix.cx.review',
    title: 'Customer Review',
    back: 'M34-reviews',
    status: { field: 'state', labels: { new: 'New', published: 'Published', flagged: 'Flagged for review' } },
    tabs: [
      { id: 'general', label: 'Review Origin', bn: 'রিভিউ উৎস', icon: '🌐' },
      { id: 'content', label: 'Review Content', bn: 'রিভিউ বিবরণ', icon: '💬' },
      { id: 'audit', label: 'Moderation & Status', bn: 'মডারেশন ও অবস্থা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Review Source & Customer',
        note: 'External reviews captured for Voice of Customer intelligence.',
        fields: [
          { name: 'name', required: true, label: 'Headline' },
          { name: 'source', required: true, label: 'Review Source' },
          { name: 'customer_id', label: 'Customer' },
          { name: 'service_order_id', label: 'Service Order' },
          { name: 'reviewed_at', required: true, label: 'Reviewed On' }
        ]
      },
      {
        tab: 'content',
        title: 'Sentiment & Content',
        fields: [
          { name: 'rating', required: true, label: 'Rating (1 to 5 Stars)' },
          { name: 'text', label: 'Review Text', type: 'text' }
        ]
      },
      {
        tab: 'audit',
        title: 'Moderation State',
        fields: [
          { name: 'state', label: 'Publishing State' }
        ]
      }
    ]
  }

  /* NOTE (A03 audit 2026-10-31): the misplaced M42 'fix.supplier.scorecard'
   * surface was removed — supplier performance lives in M42 (A06), and this
   * grid's +New chip pointed at the Survey form (wrong model→form routing). */,
  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M34-survey-templates': { kind: 'model_list', model: 'fix.survey.template', create: true,
    cols: ['name', 'code', 'version', 'purpose', 'state', 'question_count', 'response_count', 'active'],
    stateField: 'state',
    actions: [
      { m: 'action_publish', l: 'Publish' },
      { m: 'action_new_version', l: 'New Version' },
      { m: 'action_retire', l: 'Retire' }
    ],
    note: 'Publishing freezes the instrument: answers are only comparable if the question did not change under them.' },
  'M34-form-survey-template': {
    lines: {
      field: 'question_ids',
      title: 'Questions',
      note: 'A branch may only read an answer already given, which the model enforces — a forward dependency cannot be evaluated.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'code', label: 'Code', required: true },
        { name: 'text', label: 'Question (English)', required: true },
        { name: 'text_bn', label: 'Question (Bengali)' },
        { name: 'question_type', label: 'Type', required: true },
        { name: 'required', label: 'Required' },
        { name: 'choice_values', label: 'Choices' },
        { name: 'ask_if_question_id', label: 'Only Ask If' },
        { name: 'ask_if_operator', label: 'Operator' },
        { name: 'ask_if_value', label: 'Value' }
      ]
    },
    kind: 'model_form', model: 'fix.survey.template',
    title: 'Survey Instrument', back: 'M34-survey-templates',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    tabs: [
      { id: 'identity', label: '1. Instrument', bn: '১. ইনস্ট্রুমেন্ট', icon: '📝' },
      { id: 'intro', label: '2. Introduction', bn: '২. ভূমিকা', icon: '💬' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Instrument Identity',
        note: 'Publishing freezes the instrument. Changing a question\'s wording after responses exist would silently merge two different questions into one trend line.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'code', label: 'Code', required: true },
        { name: 'version', label: 'Version', required: true },
        { name: 'purpose', label: 'Purpose', required: true },
        { name: 'state', label: 'State', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'intro',
        title: 'What The Customer Reads First',
        note: 'Publishing refuses an instrument whose questions have no Bengali text: a survey a Bengali-speaking customer cannot read is not a survey (DE-17).',
        fields: [
        { name: 'intro_text', label: 'Introduction (English)' },
        { name: 'intro_text_bn', label: 'Introduction (Bengali)' },
        { name: 'question_count', label: 'Questions' },
        { name: 'response_count', label: 'Responses' }
        ]
      }
    ]
  },
  'M34-survey-answers': { kind: 'model_list', model: 'fix.survey.answer', create: false,
    cols: ['answered_at', 'survey_id', 'question_code', 'question_type', 'value_numeric', 'value_text'],
    note: 'A row per answer, so \'average punctuality by branch\' is a query and not a parsing job.' },
};

export const REPORT_ROUTES = {
  'M34:CSAT by Branch & Technician': 'M34-rpt-csat',
  'M34:NPS Trend & Drivers': 'M34-rpt-nps',
  'M34:Complaint Category Pareto': 'M34-rpt-pareto',
  'M34:Closed-Loop Effectiveness': 'M34-rpt-loop',
  'M34:Review Sentiment Summary': 'M34-rpt-sentiment'
};

export const FORM_MODELS = {
  'M34:Survey Instrument': 'fix.survey.template',
  'M34:Survey': 'fix.survey',
  'M34:Complaint': 'fix.complaint',
  'M34:Goodwill Credit': 'fix.credit.note',
  'M34:Detractor Follow-up': 'fix.cx.followup'
};

export const FORM_CHIPS = {
  'M34:Survey Instrument': 'M34-form-survey-template',
  'M34:Survey': 'M34-form-survey',
  'M34:Complaint': 'M34-form-complaint',
  'M34:Goodwill Credit': 'M34-form-goodwill',
  'M34:Detractor Follow-up': 'M34-form-followup',
  'M34:__by_model__': {
    'fix.survey.template': 'M34-form-survey-template',
    'fix.survey': 'M34-form-survey',
    'fix.complaint': 'M34-form-complaint',
    'fix.credit.note': 'M34-form-goodwill',
    'fix.cx.followup': 'M34-form-followup',
    'fix.cx.throttle': 'M34-form-throttle',
    'fix.cx.review': 'M34-form-review'
  },
  'M34:__by_screen__': {
    'M34-survey-templates': 'M34-form-survey-template',
    'M34-responses': 'M34-form-survey',
    'M34-complaints': 'M34-form-complaint',
    'M34-form-complaint': 'M34-form-complaint',
    'M34-detractor': 'M34-form-followup',
    'M34-throttle': 'M34-form-throttle',
    'M34-reviews': 'M34-form-review'
  }
};

export const CREATE = {
  M34: { screen: 'M34-form-complaint', model: 'fix.complaint', label: 'Complaint' }
};
