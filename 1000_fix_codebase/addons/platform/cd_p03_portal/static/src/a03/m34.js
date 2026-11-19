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
      { id: 'M34-design', en: 'Survey Designer', bn: 'সার্ভে ডিজাইনার', t: 'g' },
      { id: 'M34-responses', en: 'Responses & Ratings', bn: 'প্রতিক্রিয়া', t: 'g' },
      { id: 'M34-throttle', en: 'Distribution & Throttling', bn: 'বিতরণ ও থ্রটলিং', t: 'g' },
      { id: 'M34-survey-triggers', en: 'Survey Triggers & Sampling', bn: 'সার্ভে ট্রিগার ও নমুনা', t: 'g' },
      { id: 'M34-anomalies', en: 'Response Anomalies', bn: 'উত্তরের অসঙ্গতি', t: 'g' },
      { id: 'M34-conv-ratings', en: 'Conversation Ratings', bn: 'কথোপকথন রেটিং', t: 'g' }
    ]},
    { en: 'Complaints', screens: [
      { id: 'M34-complaints', en: 'Complaints', bn: 'অভিযোগ', t: 'g' },
      { id: 'M34-record', en: 'Complaint Record', bn: 'অভিযোগ রেকর্ড', t: 'f' },
      { id: 'M34-escalation', en: 'Severity & Escalation', bn: 'তীব্রতা ও এসক্যালেশন', t: 'r' },
      { id: 'M34-goodwill', en: 'Goodwill Authority', bn: 'সদিচ্ছা কর্তৃত্ব', t: 'r' },
      { id: 'M34-taxonomy', en: 'Complaint Categories', bn: 'অভিযোগের শ্রেণি', t: 'g' },
      { id: 'M34-sla-rules', en: 'Complaint SLA Bindings', bn: 'অভিযোগ এসএলএ', t: 'g' },
      { id: 'M34-complaint-updates', en: 'Customer Updates', bn: 'গ্রাহককে আপডেট', t: 'g' }
    ]},
    { en: 'Closed Loop', screens: [
      { id: 'M34-detractor', en: 'Detractor Recovery', bn: 'ডিট্রাক্টর রিকভারি', t: 'g' },
      { id: 'M34-journey', en: 'Journey Measurement', bn: 'যাত্রা পরিমাপ', t: 'r' }
    ]},
    { en: 'Voice of Customer', screens: [
      { id: 'M34-voc', en: 'VoC Analytics', bn: 'ভিওসি বিশ্লেষণ', t: 'r' },
      { id: 'M34-reviews', en: 'Reviews & Testimonials', bn: 'রিভিউ', t: 'g' },
      { id: 'M34-byybranch', en: 'Experience by Branch/Tech', bn: 'শাখাভিত্তিক অভিজ্ঞতা', t: 'r' },
      { id: 'M34-journeys', en: 'Customer Journeys', bn: 'গ্রাহক যাত্রা', t: 'g' },
      { id: 'M34-voc-themes', en: 'VoC Themes', bn: 'ভিওসি থিম', t: 'g' }
    ]},
    { en: 'Survey Designer', bn: 'সার্ভে ডিজাইনার', screens: [
      { id: 'M34-survey-templates', en: 'Survey Instruments', bn: 'সার্ভে ইনস্ট্রুমেন্ট', t: 'g' },
      { id: 'M34-form-survey-template', en: 'Survey Instrument', bn: 'ইনস্ট্রুমেন্ট ফর্ম', t: 'f' },
      { id: 'M34-survey-answers', en: 'Collected Answers', bn: 'সংগৃহীত উত্তর', t: 'g' }
    ]}
  ],
  reports: ['CSAT by Branch & Technician', 'NPS Trend & Drivers', 'Complaint Category Pareto', 'Closed-Loop Effectiveness', 'Review Sentiment Summary'],
  forms: ['Survey', 'Complaint', 'Goodwill Credit', 'Detractor Follow-up', 'Survey Instrument', 'Distribution Throttle', 'Complaint Category', 'Complaint SLA Binding', 'Customer Review',
    'Survey Trigger', 'Response Anomaly', 'Conversation Rating', 'Customer Update', 'Customer Journey', 'VoC Theme'],
  cross: ['M01 Service Orders', 'M20 Credit Notes', 'M23 QMS / NCR'],
  /* M34 capture audit (2026-11-13): each page captures what its functions
   * (FR-CXM-001..042) record. Before it, Survey Design offered "+ New Survey"
   * (a response row the order-closed event raises), Multi-Parameter Ratings
   * offered "+ New Customer Review" (an external Google/Facebook review),
   * Categorisation & SLA offered "+ New Complaint", and the instrument
   * designer, its answers, the throttle rules and the complaint SLA bindings
   * sat on no page. */
  freg: { src: 69, sub: [
    // FR-001..010: the instrument (questions, branching, bilingual text) and
    // the per-customer frequency cap. Surveys themselves are SENT by the
    // service_order.closed consumer, never typed.
    ['1', 'Survey Design & Distribution', 10, { model: 'fix.survey.template', cols: ['name', 'code', 'version', 'purpose', 'state', 'question_count', 'response_count'], screens: ['M34-survey-templates', 'M34-design', 'M34-survey-triggers', 'M34-throttle'], reports: [], forms: ['Survey Instrument', 'Survey Trigger', 'Distribution Throttle'] }],
    // FR-011..019: a response taken by phone or at the counter is recorded on
    // the survey the closed order raised (there is no customer response link
    // yet), which also raises the detractor follow-up.
    // Third pass (2026-11-19): a response records how it arrived (BRU-CXM-15)
    // and freezes who it is about (BRU-CXM-10); a suspected manipulation is
    // a Response Anomaly that holds the scores out of M57 (BRU-CXM-11).
    ['2', 'CSAT / NPS / CES', 7, { model: 'fix.survey', cols: ['state', 'customer_id', 'service_order_id', 'technician_id', 'rating', 'nps_score', 'ces_score', 'response_channel', 'incentive_excluded'], screens: ['M34-responses', 'M34-anomalies', 'M34-rpt-csat', 'M34-rpt-nps'], reports: ['CSAT by Branch & Technician', 'NPS Trend & Drivers'], forms: ['Survey', 'Response Anomaly'], create: 'M34-form-survey' }],
    // FR-014/015: overall, timeliness, professionalism and behaviour are the
    // instrument's questions; each answer is a row. Captured on the response.
    // Third pass (2026-11-19): FR-015, the rating at the close of a contact-
    // centre conversation (overall, timeliness, professionalism, behaviour),
    // had no record; this page's + now captures it. Service ratings stay on
    // the survey response (chip).
    ['3', 'Multi-Parameter Ratings', 6, { model: 'fix.survey.answer', cols: ['answered_at', 'survey_id', 'question_code', 'question_type', 'value_numeric', 'value_text'], screens: ['M34-survey-answers', 'M34-conv-ratings'], reports: [], forms: ['Conversation Rating', 'Survey', 'Survey Instrument'], create: 'M34-form-conv-rating' }],
    ['4', 'Closed Feedback Loop', 9, { model: 'fix.cx.followup', cols: ['name', 'state', 'customer_id', 'reason', 'owner_id', 'contact_due', 'escalation_level', 'due_date'], screens: ['M34-detractor', 'M34-rpt-loop'], reports: ['Closed-Loop Effectiveness'], forms: ['Detractor Follow-up'] }],
    // Third pass (2026-11-19): FR-033 / BRU-CXM-07, the customer is told of
    // progress without chasing: a Customer Update is queued on S1 (SMS,
    // e-mail, WhatsApp) or recorded as made (call, letter, visit).
    ['5', 'Complaint Management', 14, { model: 'fix.complaint', cols: ['name', 'state', 'customer_id', 'intake_channel', 'last_update_at', 'dofa_tier_required', 'dofa_approved'], screens: ['M34-complaints', 'M34-complaint-updates'], reports: ['Complaint Category Pareto'], forms: ['Complaint', 'Customer Update'] }],
    // FR-030/031: the maintained complaint taxonomy (type and sub-type, in
    // English and Bengali, with the severity a category starts at) and which
    // SLA a complaint of each severity buys, per branch or unit. Both are the
    // Customer Service Manager's registers (spec section 13): the Contact
    // Centre Supervisor group and the administrator save them. Second pass
    // (2026-11-14): this page had no + button at all; the category was a
    // fixed six-value list and the bindings were administrator-only.
    ['6', 'Categorisation & SLA', 8, { model: 'fix.complaint.taxonomy', cols: ['code', 'complete_name', 'name_bn', 'category', 'default_severity', 'complaint_count', 'active'], screens: ['M34-taxonomy', 'M34-sla-rules', 'M34-complaints', 'M34-escalation', 'M34-rpt-pareto'], reports: ['Complaint Category Pareto'], forms: ['Complaint Category', 'Complaint SLA Binding', 'Complaint'], create: 'M34-form-complaint-taxonomy' }],
    ['7', 'Compensation & Goodwill', 6, { model: 'fix.credit.note', cols: ['invoice_id', 'amount', 'state', 'approved_by', 'issued_at'], screens: ['M34-goodwill'], reports: [], forms: ['Goodwill Credit'], domain: [['reason_code', '=', 'goodwill']] }],
    // FR-039..042: the analytics are calculated; the one record a person
    // enters here is a review or testimonial (FR-040).
    // Third pass (2026-11-19): journeys (FR-039) and coded themes (FR-041)
    // are the two VoC records a person defines; the rest is calculated.
    ['8', 'VoC Analytics', 9, { model: 'fix.survey', cols: ['service_order_id', 'customer_id', 'rating', 'nps_score', 'ces_score'], screens: ['M34-voc', 'M34-journey', 'M34-journeys', 'M34-voc-themes', 'M34-byybranch', 'M34-reviews', 'M34-rpt-sentiment', 'M34-responses'], reports: ['Review Sentiment Summary', 'NPS Trend & Drivers'], forms: ['Customer Review', 'Customer Journey', 'VoC Theme'], create: 'M34-form-review', domain: [['state', '=', 'responded']] }]
  ] }
};

export const SCREENS = {
  /* M34 capture audit (2026-11-13): this was a fixed three-row report that
   * said "a question designer is not built (no model for custom questions)"
   * while fix.survey.template / fix.survey.question existed. The designer is
   * the question bank of every instrument; questions are edited on their
   * instrument (Survey Instrument form), which freezes once published. */
  'M34-design': { kind: 'model_list', model: 'fix.survey.question', create: false,
    cols: ['template_id', 'sequence', 'code', 'text', 'text_bn', 'question_type', 'required', 'ask_if_question_id'],
    note: 'Every question of every instrument. A question is added or changed on its instrument (+ New Survey Instrument, or New Version of a published one).',
    empty: 'No questions yet: create a Survey Instrument and add its questions.' },
  'M34-responses': { kind: 'model_list', model: 'fix.survey', stateField: 'state',
    cols: ['service_order_id', 'customer_id', 'branch_id', 'technician_id', 'template_id', 'rating', 'nps_score', 'ces_score', 'state', 'response_channel', 'responded_at', 'incentive_excluded'],
    note: 'A survey is raised when a service order closes (by its trigger: instrument, delay, sample) and is sent within the customer\'s monthly cap. A response taken by phone or at the counter is recorded with Record a Survey Response, saying how it arrived.',
    empty: 'No surveys yet: one is raised for each service order when it closes.' },
  'M34-throttle': { kind: 'model_list', model: 'fix.cx.throttle', stateField: 'suppressed',
    cols: ['partner_id', 'channel', 'max_per_month', 'sent_this_month', 'last_sent_at', 'suppressed', 'reason'],
    note: 'A counter row appears when the first survey goes to a customer on a channel (default cap 1 a month). Add a rule to raise or lower one customer\'s cap, or to suppress all CX outreach to them.' },
  'M34-complaints': { kind: 'model_list', model: 'fix.complaint', stateField: 'state',
    cols: ['name', 'customer_id', 'category', 'severity', 'state', 'intake_channel', 'last_update_at', 'operating_unit_id', 'service_order_id'],
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
      { m: 'action_link_capa', l: 'Link CAPA (QM)', ask: 'ID of the CAPA raised from this complaint\'s NCR (leave blank to take the NCR\'s only CAPA)', kwarg: 'capa_id' },
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
    cols: ['name', 'customer_id', 'reason', 'owner_id', 'contact_due', 'escalation_level', 'escalated_to_id', 'due_date', 'state'],
    note: 'A detractor survey or a low conversation rating raises its follow-up automatically, with a 24-hour contact deadline. An uncontacted one escalates to the branch manager, then the operations director. Add one by hand only for a customer who asked for a call back.',
    // M34 capture audit: 'contacted' and 'closed' had no action, so the only
    // way to reach them was typing the state on the form (FR-CXM-022/024).
    actions: [
      { m: 'action_mark_contacted', l: 'Record Contact', ask: 'What was discussed with the customer', kwarg: 'note' },
      // Second pass (2026-11-14): both closes need a recorded contact, and a
      // recovery closes only on what the customer said (BRU-CXM-03/04).
      { m: 'action_close_recovered', l: 'Mark Recovered', ask: 'What the customer said to confirm they are satisfied', kwarg: 'confirmation' },
      { m: 'action_close_unrecovered', l: 'Close (Not Recovered)', ask: 'Why the customer could not be recovered', kwarg: 'reason' },
      { m: 'action_raise_complaint', l: 'Raise / Link Complaint' }
    ] },
  'M34-journey': { kind: 'table_report', module: 'M34', report: 'journey_measurement', title: 'Journey Measurement', period: false },
  'M34-voc': { kind: 'table_report', module: 'M34', report: 'voc_analytics', title: 'VoC Analytics', period: false },
  'M34-reviews': { kind: 'model_list', model: 'fix.cx.review', stateField: 'state',
    cols: ['name', 'source', 'customer_id', 'rating', 'state', 'publication_consent', 'reviewed_at'],
    note: 'A review is published to the website only after the customer\'s consent is recorded (Record Consent, then Publish).',
    // Second pass (2026-11-14): the state was typed on the form, so a review
    // could be "Published" with no consent (BRU-CXM-13). FR-CXM-040 also
    // asks for moderation and a reply.
    actions: [
      { m: 'action_record_consent', l: 'Record Consent', ask: 'How the customer agreed to publication (call, SMS reply, signed form)', kwarg: 'evidence' },
      { m: 'action_publish', l: 'Publish' },
      { m: 'action_flag', l: 'Hold Back', ask: 'Why the review is held back', kwarg: 'reason' },
      { m: 'action_reply', l: 'Reply', ask: 'Our reply to the customer', kwarg: 'reply' },
      { m: 'action_withdraw_consent', l: 'Withdraw Consent', ask: 'What the customer asked for', kwarg: 'reason' }
    ] },

  /* FR-CXM-030/031: the complaint SLA binding (severity x branch / unit ->
   * SLA policy). Saved by the Contact Centre Supervisor group or the
   * administrator (second pass, 2026-11-14: it was administrator-only). */
  'M34-sla-rules': { kind: 'model_list', model: 'fix.complaint.sla.rule', create: true,
    cols: ['sequence', 'severity', 'loyalty_tier_id', 'branch_id', 'operating_unit_id', 'policy_id', 'active'],
    note: 'The most specific binding wins: branch, then operating unit, then the estate default for the severity; within each, a binding for the customer\'s membership tier wins over one for every tier. A complaint with no binding uses the M01 default SLA.',
    empty: 'No bindings: every complaint uses the default SLA. A contact-centre supervisor adds one with Complaint SLA Binding.' },
  'M34-form-sla-rule': {
    kind: 'model_form',
    model: 'fix.complaint.sla.rule',
    title: 'Complaint SLA Binding',
    back: 'M34-sla-rules',
    sections: [
      {
        title: 'Which SLA a Complaint Buys',
        note: 'Leave branch and unit empty for the estate default of that severity. Saving needs the Contact Centre Supervisor or administrator role.',
        fields: [
          { name: 'severity', required: true, label: 'Complaint Severity' },
          { name: 'policy_id', required: true, label: 'SLA Policy' },
          { name: 'branch_id', label: 'Branch (optional)' },
          { name: 'operating_unit_id', label: 'Operating Unit (optional)' },
          { name: 'loyalty_tier_id', label: 'Customer Tier (optional, FR-CXM-031)' },
          { name: 'sequence', label: 'Priority Order' },
          { name: 'active', label: 'Active' }
        ]
      }
    ]
  },
  /* FR-CXM-030: the maintained complaint taxonomy (spec 10.1). */
  'M34-taxonomy': { kind: 'model_list', model: 'fix.complaint.taxonomy', create: true,
    cols: ['code', 'complete_name', 'name_bn', 'category', 'default_severity', 'complaint_count', 'active'],
    note: 'The categories a complaint is filed under, in English and Bengali. A sub-category carries its parent\'s ISO category; a complaint filed under a category starts at no less than its default severity.',
    empty: 'No complaint categories yet: complaints use the six fixed ISO categories until a supervisor adds them.' },
  'M34-form-complaint-taxonomy': {
    lines: { field: 'child_ids', title: 'Sub-categories', readonlyGrid: true,
      note: 'A sub-category is added with its own Complaint Category form, naming this one as its parent.',
      fields: [
        { name: 'code', label: 'Code', readonly: true },
        { name: 'name', label: 'Category (English)', readonly: true },
        { name: 'name_bn', label: 'Category (Bengali)', readonly: true },
        { name: 'default_severity', label: 'Starts At', readonly: true }
      ] },
    kind: 'model_form',
    model: 'fix.complaint.taxonomy',
    title: 'Complaint Category',
    back: 'M34-taxonomy',
    sections: [
      {
        title: 'Complaint Category',
        note: 'Saved by a contact-centre supervisor or administrator. A sub-category takes its parent\'s ISO category.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Category (English)' },
          { name: 'name_bn', required: true, label: 'Category (Bengali)' },
          { name: 'parent_id', label: 'Parent Category (blank for a top-level one)' },
          { name: 'category', label: 'ISO Category (a sub-category uses its parent\'s)' },
          { name: 'default_severity', label: 'Starts At Severity (optional)' },
          { name: 'description', label: 'When to Use It', type: 'text' },
          { name: 'active', label: 'Active' },
          { name: 'complaint_count', readonly: true, label: 'Complaints Filed' }
        ]
      }
    ]
  },
  'M34-byybranch': { kind: 'table_report', module: 'M34', report: 'experience_by_branch', title: 'Experience by Branch/Tech', period: false },

  /* Report chips -> their own computed pack */
  'M34-rpt-csat': { kind: 'table_report', module: 'M34', report: 'csat_by_branch', title: 'CSAT by Branch & Technician', period: false },
  'M34-rpt-nps': { kind: 'table_report', module: 'M34', report: 'nps_trend', title: 'NPS Trend & Drivers', period: false },
  'M34-rpt-pareto': { kind: 'table_report', module: 'M34', report: 'complaint_pareto', title: 'Complaint Category Pareto', period: false },
  'M34-rpt-loop': { kind: 'table_report', module: 'M34', report: 'closed_loop', title: 'Closed-Loop Effectiveness', period: false },
  'M34-rpt-sentiment': { kind: 'table_report', module: 'M34', report: 'review_sentiment', title: 'Review Sentiment Summary', period: false },

  /* ============ D365 IN-WORKSPACE MULTI-TAB FORMS ============ */
  /* M34 capture audit (2026-11-13): this was a blank "+ New Survey" with an
   * editable state, so a survey could be typed for an order that already had
   * one (one per order) or marked "Sent" with nothing sent; and its answer
   * grid keyed a related code instead of the question, so no answer could be
   * saved. A survey is raised by the closed order; what a person records is
   * the customer's response to it. Recording a rating or an answer moves the
   * survey to Responded and raises the detractor follow-up (server side). */
  'M34-form-survey': {
    lines: {
      field: 'answer_ids',
      title: 'Answers by Parameter',
      note: 'One row per question of the instrument (timeliness, professionalism, behaviour, NPS, effort...). Each answer is range-checked against its question, which must belong to this survey\'s instrument. Leave out a question the customer was not asked.',
      fields: [
        { name: 'question_id', label: 'Question', required: true },
        { name: 'value_numeric', label: 'Score' },
        { name: 'value_text', label: 'Answer (text / yes-no / choice)' },
        { name: 'question_type', label: 'Type', readonly: true },
        { name: 'answered_at', label: 'Answered At', readonly: true }
      ]
    },
    kind: 'model_form',
    model: 'fix.survey',
    title: 'Survey Response',
    newLabel: 'Record a Survey Response',
    back: 'M34-responses',
    pickRecord: {
      label: 'Step 1 of 2: choose the survey the customer answered',
      note: 'Surveys raised by closed service orders and not yet answered.',
      search: 'Search service order or customer',
      choose: 'Record this response',
      cols: ['service_order_id', 'customer_id', 'operating_unit_id', 'state', 'dispatch_channel'],
      domain: [['state', 'in', ['pending', 'sent']]],
      empty: 'No survey is waiting for an answer: a survey is raised when a service order closes.'
    },
    status: { field: 'state', labels: { pending: 'Pending', sent: 'Sent', responded: 'Responded', expired: 'Expired' } },
    tabs: [
      { id: 'response', label: 'Customer Response', bn: 'গ্রাহকের উত্তর', icon: '⭐' },
      { id: 'general', label: 'Survey Details', bn: 'জরিপ বিবরণ', icon: '📝' }
    ],
    sections: [
      {
        tab: 'response',
        title: 'Step 2 of 2: What the Customer Said',
        note: 'A rating of 3 or below, or an NPS answer of 6 or below, raises a detractor follow-up at once. The response is logged on the survey with who recorded it.',
        fields: [
          { name: 'template_id', label: 'Instrument (needed for the answers below)' },
          { name: 'response_channel', required: true, label: 'Received Through (BRU-CXM-15)' },
          { name: 'response_device', label: 'From Number / Device' },
          { name: 'rating', label: 'Overall Rating (1 to 5)' },
          { name: 'comment', label: 'Customer\'s Words', type: 'text' },
          { name: 'nps_score', readonly: true, label: 'NPS Contribution (computed)' },
          { name: 'ces_score', readonly: true, label: 'Effort Score (from the CES answer)' }
        ]
      },
      {
        tab: 'general',
        title: 'Survey Details',
        note: 'Raised from the closed service order; one survey per order. Branch, technician and service type are frozen when the survey is raised, so a later reassignment never moves the score.',
        fields: [
          { name: 'service_order_id', readonly: true, label: 'Service Order' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'operating_unit_id', readonly: true, label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'dispatch_channel', readonly: true, label: 'Sent By' },
          { name: 'dispatch_suppressed_reason', readonly: true, label: 'Not Sent Because', type: 'text' },
          { name: 'followup_id', readonly: true, label: 'Detractor Follow-up' },
          { name: 'trigger_id', readonly: true, label: 'Trigger' },
          { name: 'branch_id', readonly: true, label: 'Branch (frozen at capture)' },
          { name: 'technician_id', readonly: true, label: 'Technician (frozen at capture)' },
          { name: 'service_type', readonly: true, label: 'Service Type' },
          { name: 'responded_at', readonly: true, label: 'Responded At' },
          { name: 'response_recorded_by_id', readonly: true, label: 'Response Recorded By' },
          { name: 'incentive_excluded', readonly: true, label: 'Kept Out of Incentives' },
          { name: 'anomaly_id', readonly: true, label: 'Under Anomaly Review' },
          { name: 'source_event_id', readonly: true, label: 'Source Event ID' }
        ]
      }
    ]
  },

  /* M34 sweep audit 2026-11-06: the registry id for the complaint record
     * form is M34-record - restored (was renamed in the fragment). */
  'M34-record': { kind: 'model_form', model: 'fix.complaint',
    title: 'ISO 10002 Customer Complaint & Escalation Master', back: 'M34-complaints',
    status: { field: 'state' },
    tabs: [
      { id: 'intake', label: '1. Intake & Classification', bn: '১. গ্রহণ ও তীব্রতা', icon: '⚠️', badge: '12' },
      { id: 'acknowledgment', label: '2. Acknowledgment & SLA', bn: '২. স্বীকৃতি', icon: '⏱️', badge: '6' },
      { id: 'rca_5why', label: '3. 5-Why Root Cause Analysis', bn: '৩. ফাইভ-হোয়াই মূল কারণ', icon: '🔍', badge: '5' },
      { id: 'capa', label: '4. CAPA & Quality NCR', bn: '৪. ক্যাপা ও এনসিআর', icon: '🛠️', badge: '4' },
      { id: 'concession', label: '5. Concession & DOFA Approval', bn: '৫. ছাড়', icon: '💳', badge: '10' },
      { id: 'docs', label: '6. Evidence & Documents', bn: '৬. প্রমাণ ও নথি', icon: '📑', badge: '2' },
      { id: 'resolution', label: '7. Response, Decision & Closure', bn: '৭. চূড়ান্ত নিষ্পত্তি', icon: '✅', badge: '13' },
      { id: 'referral', label: '8. External Referral', bn: '৮. বাহ্যিক রেফারেল', icon: '🏛️', badge: '3' },
      { id: 'updates', label: '9. Customer Updates', bn: '৯. গ্রাহককে আপডেট', icon: '📣' }
    ],
    grids: [
      { field: 'update_ids', tab: 'updates', title: 'What the customer has been told', readonlyGrid: true,
        note: 'Sent with Customer Update (FR-CXM-033): SMS, e-mail and WhatsApp through the delivery service, a call or letter recorded as made.',
        fields: [
          { name: 'sent_at', label: 'Sent At', readonly: true },
          { name: 'update_type', label: 'Type', readonly: true },
          { name: 'channel', label: 'Channel', readonly: true },
          { name: 'content', label: 'Content', readonly: true },
          { name: 'state', label: 'Outcome', readonly: true }
        ] }
    ],
    sections: [
      { tab: 'intake', title: 'Complaint Intake & Severity Tier', fields: [
        { name: 'name', required: true, label: 'Complaint Reference Code' },
        { name: 'customer_id', required: true, label: 'Aggrieved Customer Party' },
        { name: 'service_order_id', label: 'Linked Service Order Ref' },
        { name: 'operating_unit_id', label: 'Branch / Operating Unit' },
        { name: 'taxonomy_id', label: 'Complaint Category (maintained list; sets the ISO category)' },
        { name: 'category', required: true, label: 'ISO 10002 Complaint Category' },
        { name: 'severity', required: true, label: 'Severity Level (a category may raise it at intake)' },
        { name: 'state', readonly: true, label: 'Complaint Workflow State' },
        { name: 'owner_id', readonly: true, label: 'Complaint Owner (Assess / Take Ownership / Assign)' },
        { name: 'assessed_at', readonly: true, label: 'Assessed At' },
        { name: 'received_via', label: 'Received Via (staff-keyed complaint: counter, phone, e-mail, regulator...)' },
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
      { tab: 'capa', title: 'Corrective & Preventive Action (CAPA) & Quality NCR',
        note: 'The CAPA link is the Quality Manager\'s act over the real chain (complaint → NCR → the CAPA raised from that NCR) — never a typed field (A10 S6).',
        fields: [
        { name: 'capa_id', readonly: true, label: 'Linked CAPA Action Plan Ref' },
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
        fields: []},
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
      ]},
      { tab: 'referral', title: 'Regulator, Consumer Body or Brand Partner (FR-CXM-038)',
        note: 'Required when the complaint was received via a regulator or brand partner.',
        fields: [
        { name: 'external_body', label: 'Referring Body' },
        { name: 'external_reference', label: 'Their Reference' },
        { name: 'external_response_due', label: 'Their Response Deadline' },
      ]},
      { tab: 'updates', title: 'Customer Updates (ISO 10002 cl. 7.3)',
        note: 'Send one with + Send a Customer Update on the Customer Updates list.',
        fields: [
        { name: 'update_count', readonly: true, label: 'Updates Sent' },
        { name: 'last_update_at', readonly: true, label: 'Customer Last Updated' },
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
        note: 'The status moves only by the list actions: Record Contact, then Mark Recovered (with what the customer said) or Close (Not Recovered).',
        fields: [
          { name: 'state', readonly: true, label: 'Recovery Status' },
          { name: 'contact_due', readonly: true, label: 'Contact By (24-hour target)' },
          { name: 'contacted_at', readonly: true, label: 'First Contact At' },
          { name: 'escalation_level', readonly: true, label: 'Escalated To Level' },
          { name: 'escalated_to_id', readonly: true, label: 'Escalated To' },
          { name: 'escalated_at', readonly: true, label: 'Escalated At' },
          { name: 'rating_id', readonly: true, label: 'Conversation Rating (if raised from one)' },
          { name: 'customer_confirmation', readonly: true, label: 'Customer\'s Confirmation', type: 'text' },
          { name: 'customer_confirmed_at', readonly: true, label: 'Customer Confirmed At' },
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
    status: { field: 'state', labels: { new: 'New', published: 'Published', flagged: 'Held back' } },
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
        title: 'Consent, Moderation & Reply',
        note: 'These move by the list actions: Record Consent, Publish, Hold Back, Reply, Withdraw Consent. A review is never published without the customer\'s consent.',
        fields: [
          { name: 'state', readonly: true, label: 'Publishing State' },
          { name: 'publication_consent', readonly: true, label: 'Customer Consented' },
          { name: 'consent_evidence', readonly: true, label: 'How They Consented', type: 'text' },
          { name: 'moderated_by_id', readonly: true, label: 'Moderated By' },
          { name: 'moderation_note', readonly: true, label: 'Why Held Back', type: 'text' },
          { name: 'reply_text', readonly: true, label: 'Our Reply', type: 'text' }
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
        // Publish / Retire on the list: a typed "Published" skipped the
        // Bengali-text check and the freeze (M34 capture audit).
        { name: 'state', label: 'State', readonly: true },
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
        { name: 'question_count', label: 'Questions', readonly: true },
        { name: 'response_count', label: 'Responses', readonly: true }
        ]
      }
    ]
  },
  'M34-survey-answers': { kind: 'model_list', model: 'fix.survey.answer', create: false,
    cols: ['answered_at', 'survey_id', 'question_code', 'question_type', 'value_numeric', 'value_text'],
    note: 'A row per answer, so \'average punctuality by branch\' is a query and not a parsing job. Answers are recorded on the survey response.',
    empty: 'No answers yet: they are recorded with Record a Survey Response, against the survey\'s instrument.' },
  /* ============ M34 THIRD PASS (2026-11-19) ============
   * The spec records that no page could capture: survey triggers and
   * sampling (FR-002..004), response anomalies (FR-019, BRU-CXM-11),
   * conversation ratings (FR-015), customer updates on a complaint (FR-033,
   * BRU-CXM-07), journeys (FR-039) and coded VoC themes (FR-041). */
  'M34-survey-triggers': { kind: 'model_list', model: 'fix.survey.trigger', create: true,
    cols: ['sequence', 'code', 'name', 'trigger_event', 'template_id', 'delay_minutes', 'sampling_rate', 'branch_id', 'service_type', 'survey_count', 'not_sampled_count', 'active'],
    note: 'Which instrument a closed order is surveyed on, after what delay and for what share of orders. The most specific trigger wins (branch and service type, then branch, then service type, then the default). With no trigger every closed order is surveyed at once.',
    empty: 'No triggers: every closed order is surveyed at once, with no instrument. A contact-centre supervisor adds one with Survey Trigger.' },
  'M34-form-survey-trigger': {
    kind: 'model_form', model: 'fix.survey.trigger', title: 'Survey Trigger', back: 'M34-survey-triggers',
    tabs: [
      { id: 'when', label: 'When & What', bn: 'কখন ও কী', icon: '⏰' },
      { id: 'who', label: 'Eligibility & Sample', bn: 'যোগ্যতা ও নমুনা', icon: '🎯' }
    ],
    sections: [
      { tab: 'when', title: 'Trigger', note: 'Saved by a contact-centre supervisor or administrator. The instrument must be published.', fields: [
        { name: 'code', required: true, label: 'Code' },
        { name: 'name', required: true, label: 'Name' },
        { name: 'trigger_event', required: true, label: 'Event' },
        { name: 'template_id', required: true, label: 'Instrument (published)' },
        { name: 'delay_minutes', label: 'Delay Before Sending (minutes)' },
        { name: 'sequence', label: 'Priority Order' },
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'who', title: 'Who Is Asked', note: 'The sample is a fixed hash of the order, so the same order is always in or out and nobody can steer which customers are asked.', fields: [
        { name: 'sampling_rate', required: true, label: 'Sample (% of eligible orders)' },
        { name: 'branch_id', label: 'Only for Branch (optional)' },
        { name: 'service_type', label: 'Only for Service Type key (optional: walk_in, onsite, collection...)' },
        { name: 'eligibility_note', label: 'Eligibility Criteria', type: 'text' },
        { name: 'survey_count', readonly: true, label: 'Surveys Raised' },
        { name: 'not_sampled_count', readonly: true, label: 'Orders Not Sampled' }
      ] }
    ]
  },
  'M34-anomalies': { kind: 'model_list', model: 'fix.cx.response.anomaly', stateField: 'state', create: true,
    cols: ['name', 'detection_type', 'scope_type', 'period_from', 'period_to', 'held_count', 'state', 'investigator_id'],
    note: 'Raising an anomaly keeps every response in its scope and period out of the technician incentive (M57) until it is cleared. The person whose scores are in question cannot investigate or decide it (SOD-21).',
    empty: 'No anomalies raised.',
    actions: [
      { m: 'action_start_investigation', l: 'Start Investigation' },
      { m: 'action_clear', l: 'Clear (Not Manipulation)', ask: 'What the investigation found', kwarg: 'outcome' },
      { m: 'action_uphold', l: 'Uphold (Manipulation Found)', ask: 'What the investigation found', kwarg: 'outcome' }
    ] },
  'M34-form-anomaly': {
    kind: 'model_form', model: 'fix.cx.response.anomaly', title: 'Response Anomaly', back: 'M34-anomalies',
    status: { field: 'state', labels: { open: 'Open', investigating: 'Investigating', cleared: 'Cleared', upheld: 'Upheld' } },
    tabs: [
      { id: 'what', label: 'What Was Seen', bn: 'কী দেখা গেছে', icon: '🔎' },
      { id: 'decision', label: 'Investigation', bn: 'তদন্ত', icon: '⚖️' },
      { id: 'held', label: 'Responses Held', bn: 'আটকে রাখা উত্তর', icon: '⏸️' }
    ],
    grids: [
      { field: 'survey_ids', tab: 'held', title: 'Responses kept out of incentives', readonlyGrid: true,
        note: 'Every response in the scope and period, including ones that arrive after the anomaly was raised.',
        fields: [
          { name: 'service_order_id', label: 'Service Order', readonly: true },
          { name: 'technician_id', label: 'Technician', readonly: true },
          { name: 'rating', label: 'Rating', readonly: true },
          { name: 'response_channel', label: 'Received Through', readonly: true },
          { name: 'responded_at', label: 'Responded At', readonly: true }
        ] }
    ],
    sections: [
      { tab: 'what', title: 'Suspected Manipulation', note: 'Name one subject: the technician, the branch or the person keying responses. Saved by a contact-centre supervisor or administrator.', fields: [
        { name: 'detection_type', required: true, label: 'What Looks Wrong' },
        { name: 'scope_type', required: true, label: 'About' },
        { name: 'technician_id', label: 'Technician' },
        { name: 'branch_id', label: 'Branch' },
        { name: 'recorder_id', label: 'Person Keying Responses' },
        { name: 'period_from', required: true, label: 'From' },
        { name: 'period_to', required: true, label: 'To' },
        { name: 'evidence', required: true, label: 'Evidence (counts, times, numbers)', type: 'text' }
      ] },
      { tab: 'decision', title: 'Investigation & Decision', note: 'Moves only by the list actions: Start Investigation, then Clear or Uphold.', fields: [
        { name: 'state', readonly: true, label: 'State' },
        { name: 'raised_by_id', readonly: true, label: 'Raised By' },
        { name: 'investigator_id', readonly: true, label: 'Investigator' },
        { name: 'investigation_started_at', readonly: true, label: 'Started At' },
        { name: 'outcome', readonly: true, label: 'Finding', type: 'text' },
        { name: 'decided_by_id', readonly: true, label: 'Decided By' },
        { name: 'decided_at', readonly: true, label: 'Decided At' },
        { name: 'held_count', readonly: true, label: 'Responses Held' }
      ] }
    ]
  },
  'M34-conv-ratings': { kind: 'model_list', model: 'fix.cx.rating', create: true,
    cols: ['captured_at', 'conversation_id', 'customer_id', 'agent_id', 'channel', 'overall', 'timeliness', 'professionalism', 'behaviour', 'response_channel', 'followup_id'],
    note: 'The rating a customer gives when a contact-centre conversation ends. An overall rating of 3 or below opens a detractor follow-up at once.',
    empty: 'No conversation ratings yet: record one with Conversation Rating when a closed conversation is rated.' },
  'M34-form-conv-rating': {
    kind: 'model_form', model: 'fix.cx.rating', title: 'Conversation Rating', newLabel: 'Record a Conversation Rating', back: 'M34-conv-ratings',
    tabs: [
      { id: 'rating', label: 'Customer Rating', bn: 'গ্রাহকের রেটিং', icon: '⭐' },
      { id: 'about', label: 'Attribution', bn: 'কার সম্পর্কে', icon: '👤' }
    ],
    sections: [
      { tab: 'rating', title: 'What the Customer Rated', note: 'A conversation is rated once, after it has ended. The rating is the customer\'s words: it is not edited afterwards.', fields: [
        { name: 'conversation_id', required: true, label: 'Conversation (ended)' },
        { name: 'overall', required: true, label: 'Overall (1 to 5)' },
        { name: 'timeliness', label: 'Timeliness' },
        { name: 'professionalism', label: 'Professionalism' },
        { name: 'behaviour', label: 'Behaviour' },
        { name: 'comment', label: 'Customer\'s Words', type: 'text' },
        { name: 'response_channel', required: true, label: 'Received Through' }
      ] },
      { tab: 'about', title: 'Who and What It Is About', note: 'Taken from the conversation when the rating is saved.', fields: [
        { name: 'customer_id', readonly: true, label: 'Customer' },
        { name: 'agent_id', readonly: true, label: 'Agent' },
        { name: 'channel', readonly: true, label: 'Conversation Channel' },
        { name: 'operating_unit_id', readonly: true, label: 'Operating Unit' },
        { name: 'captured_at', readonly: true, label: 'Captured At' },
        { name: 'recorded_by_id', readonly: true, label: 'Recorded By' },
        { name: 'followup_id', readonly: true, label: 'Detractor Follow-up' }
      ] }
    ]
  },
  'M34-complaint-updates': { kind: 'model_list', model: 'fix.complaint.update', create: true,
    cols: ['sent_at', 'complaint_id', 'customer_id', 'update_type', 'channel', 'state', 'not_sent_reason', 'sent_by_id'],
    note: 'Every status communication to a complaining customer (ISO 10002). SMS, e-mail and WhatsApp go through the delivery service, which applies consent; a call, letter or visit is recorded as made.',
    empty: 'No customer updates yet: send one with Customer Update.' },
  'M34-form-complaint-update': {
    kind: 'model_form', model: 'fix.complaint.update', title: 'Customer Update', newLabel: 'Send a Customer Update', back: 'M34-complaint-updates',
    status: { field: 'state', labels: { sent: 'Sent / Made', suppressed: 'Not Sent' } },
    sections: [
      { title: 'Update to the Customer', note: 'Saved once: an update is a record of what the customer was told. A closed complaint takes only a closure notice.', fields: [
        { name: 'complaint_id', required: true, label: 'Complaint' },
        { name: 'update_type', required: true, label: 'Type of Update' },
        { name: 'channel', required: true, label: 'Channel' },
        { name: 'content', required: true, label: 'What the Customer Is Told', type: 'text' },
        { name: 'to_address', label: 'Send To (blank: the customer\'s number or e-mail on file)' },
        { name: 'state', readonly: true, label: 'Outcome' },
        { name: 'not_sent_reason', readonly: true, label: 'Not Sent Because' },
        { name: 'sent_at', readonly: true, label: 'Sent At' },
        { name: 'sent_by_id', readonly: true, label: 'Sent By' },
        { name: 'delivery_id', readonly: true, label: 'Delivery Row' }
      ] }
    ]
  },
  'M34-journeys': { kind: 'model_list', model: 'fix.journey.definition', create: true,
    cols: ['code', 'name', 'name_bn', 'stage_count', 'active'],
    note: 'A journey is its stages, each measured by an instrument; Journey Measurement scores every stage from that instrument\'s responses.',
    empty: 'No journeys defined yet.' },
  'M34-form-journey': {
    kind: 'model_form', model: 'fix.journey.definition', title: 'Customer Journey', back: 'M34-journeys',
    lines: { field: 'stage_ids', title: 'Stages', note: 'In order. A stage with no instrument is defined but not yet measured.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'name', label: 'Stage', required: true },
        { name: 'name_bn', label: 'Stage (Bengali)' },
        { name: 'touchpoint', label: 'Touchpoint' },
        { name: 'template_id', label: 'Measured By Instrument' },
        { name: 'effort_question_code', label: 'Effort Question Code' }
      ]
    },
    sections: [
      { title: 'Journey', note: 'Saved by a contact-centre supervisor or administrator.', fields: [
        { name: 'code', required: true, label: 'Code' },
        { name: 'name', required: true, label: 'Journey (English)' },
        { name: 'name_bn', required: true, label: 'Journey (Bengali)' },
        { name: 'description', label: 'Description', type: 'text' },
        { name: 'active', label: 'Active' }
      ] }
    ]
  },
  'M34-voc-themes': { kind: 'model_list', model: 'fix.voc.theme', create: true,
    cols: ['period', 'theme', 'theme_bn', 'sentiment', 'driver', 'frequency', 'coded_by_id'],
    note: 'Themes coded from what customers wrote, by month. The frequency is the number of responses and complaints coded to the theme, never typed.',
    empty: 'No themes coded yet.' },
  'M34-form-voc-theme': {
    kind: 'model_form', model: 'fix.voc.theme', title: 'VoC Theme', back: 'M34-voc-themes',
    tabs: [
      { id: 'theme', label: 'Theme', bn: 'থিম', icon: '🏷️' },
      { id: 'verbatims', label: 'Coded Verbatims', bn: 'মন্তব্য', icon: '💬' }
    ],
    sections: [
      { tab: 'theme', title: 'Theme', note: 'Saved by a contact-centre supervisor or administrator.', fields: [
        { name: 'period', required: true, label: 'Month (YYYY-MM)' },
        { name: 'theme', required: true, label: 'Theme (English)' },
        { name: 'theme_bn', required: true, label: 'Theme (Bengali)' },
        { name: 'sentiment', required: true, label: 'Sentiment' },
        { name: 'driver', label: 'Operational Driver' },
        { name: 'notes', label: 'Coding Notes', type: 'text' },
        { name: 'frequency', readonly: true, label: 'Frequency' },
        { name: 'coded_by_id', readonly: true, label: 'Coded By' }
      ] },
      { tab: 'verbatims', title: 'What Customers Said', note: 'Only survey responses with a written comment can be coded.', fields: [
        { name: 'survey_ids', label: 'Survey Responses' },
        { name: 'complaint_ids', label: 'Complaints' }
      ] }
    ]
  }
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
  'M34:Detractor Follow-up': 'fix.cx.followup',
  'M34:Distribution Throttle': 'fix.cx.throttle',
  'M34:Complaint Category': 'fix.complaint.taxonomy',
  'M34:Complaint SLA Binding': 'fix.complaint.sla.rule',
  'M34:Customer Review': 'fix.cx.review',
  'M34:Survey Trigger': 'fix.survey.trigger',
  'M34:Response Anomaly': 'fix.cx.response.anomaly',
  'M34:Conversation Rating': 'fix.cx.rating',
  'M34:Customer Update': 'fix.complaint.update',
  'M34:Customer Journey': 'fix.journey.definition',
  'M34:VoC Theme': 'fix.voc.theme'
};

export const FORM_CHIPS = {
  'M34:Survey Instrument': 'M34-form-survey-template',
  'M34:Survey': 'M34-form-survey',
  'M34:Complaint': 'M34-record',
  'M34:Goodwill Credit': 'M34-form-goodwill',
  'M34:Detractor Follow-up': 'M34-form-followup',
  'M34:Distribution Throttle': 'M34-form-throttle',
  'M34:Complaint Category': 'M34-form-complaint-taxonomy',
  'M34:Complaint SLA Binding': 'M34-form-sla-rule',
  'M34:Customer Review': 'M34-form-review',
  'M34:Survey Trigger': 'M34-form-survey-trigger',
  'M34:Response Anomaly': 'M34-form-anomaly',
  'M34:Conversation Rating': 'M34-form-conv-rating',
  'M34:Customer Update': 'M34-form-complaint-update',
  'M34:Customer Journey': 'M34-form-journey',
  'M34:VoC Theme': 'M34-form-voc-theme',
  'M34:__by_model__': {
    'fix.survey.template': 'M34-form-survey-template',
    'fix.survey': 'M34-form-survey',
    'fix.complaint': 'M34-record',
    'fix.credit.note': 'M34-form-goodwill',
    'fix.cx.followup': 'M34-form-followup',
    'fix.cx.throttle': 'M34-form-throttle',
    'fix.cx.review': 'M34-form-review',
    'fix.complaint.sla.rule': 'M34-form-sla-rule',
    'fix.complaint.taxonomy': 'M34-form-complaint-taxonomy',
    'fix.survey.trigger': 'M34-form-survey-trigger',
    'fix.cx.response.anomaly': 'M34-form-anomaly',
    'fix.cx.rating': 'M34-form-conv-rating',
    'fix.complaint.update': 'M34-form-complaint-update',
    'fix.journey.definition': 'M34-form-journey',
    'fix.voc.theme': 'M34-form-voc-theme'
  },
  'M34:__by_screen__': {
    'M34-survey-templates': 'M34-form-survey-template',
    'M34-responses': 'M34-form-survey',
    'M34-complaints': 'M34-record',
    'M34-record': 'M34-record',
    'M34-detractor': 'M34-form-followup',
    'M34-throttle': 'M34-form-throttle',
    'M34-reviews': 'M34-form-review',
    'M34-sla-rules': 'M34-form-sla-rule',
    'M34-taxonomy': 'M34-form-complaint-taxonomy',
    'M34-survey-triggers': 'M34-form-survey-trigger',
    'M34-anomalies': 'M34-form-anomaly',
    'M34-conv-ratings': 'M34-form-conv-rating',
    'M34-complaint-updates': 'M34-form-complaint-update',
    'M34-journeys': 'M34-form-journey',
    'M34-voc-themes': 'M34-form-voc-theme'
  }
};

export const CREATE = {
  M34: { screen: 'M34-record', model: 'fix.complaint', label: 'Complaint' }
};
