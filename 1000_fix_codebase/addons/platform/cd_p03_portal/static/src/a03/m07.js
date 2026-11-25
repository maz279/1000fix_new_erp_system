/** @odoo-module **/
/* A03 · Customer Experience — M07 CRM, Pipeline & Key Account Management.
 * Rebuilt 2026-10-31: Full Microsoft Dynamics 365 multi-tab form architecture
 * across all 8 in-workspace forms with zero Bengali/English mixing, comprehensive
 * data capture, stage-gating enforcement, and B2B corporate governance.
 *
 * M07 audit 2026-11-13 ("not all the sub-modules have a relevant data capture
 * button"): 3 of 10 sub-module pages had none (Activities, Cross-Sell,
 * Competitor Intelligence) and three buttons that did show saved the wrong
 * thing: "+ New Lead" made an opportunity, "+ New Forecast Snapshot" froze a
 * snapshot of zeros, the Activity form edited a lead. Every page now captures
 * what its function records; see tests/test_m07_submodule_capture.py.
 */

export const MODULE = {
  area: 'A03', code: 'M07', en: 'CRM & Sales Pipeline', title: 'M07 · CRM & Sales Pipeline',
  bn: 'সিআরএম ও বিক্রয়', icon: '🎯',
  desc: 'Enterprise sales pipeline, multi-stream forecast categories, stage gating, win/loss intelligence, corporate account plans, QBRs and renewals.',
  kpis: [
    { l: 'Weighted Pipeline', m: 'weighted_pipeline', prefix: 'BDT ' },
    { l: 'Win Rate', m: 'win_rate', suffix: '%' },
    { l: 'AMC Renewals T-90', m: 'renewals_t90' },
    { l: 'New Corp Logos YTD', m: 'new_corp_logos_ytd' },
    { l: 'QBRs This Month', m: 'qbrs_this_month' },
    { l: 'Referral Leads', m: 'referral_leads' }
  ],
  groups: [
    { en: 'Leads', bn: 'লিড', screens: [
      { id: 'M07-leads', en: 'Leads', bn: 'লিড', t: 'g' },
      { id: 'M07-qualifications', en: 'Qualification Assessments', bn: 'যোগ্যতা যাচাই', t: 'g' },
      { id: 'M07-scoring', en: 'Scoring & Routing', bn: 'স্কোরিং ও রাউটিং', t: 'g' },
      { id: 'M07-sources', en: 'Sources & Campaigns', bn: 'উৎস ও ক্যাম্পেইন', t: 'r' }
    ]},
    { en: 'Pipeline', bn: 'পাইপলাইন', screens: [
      { id: 'M07-opps', en: 'Opportunities', bn: 'সুযোগ', t: 'g' },
      { id: 'M07-kanban', en: 'Pipeline Kanban', bn: 'পাইপলাইন কানবান', t: 'd' },
      { id: 'M07-opp-team', en: 'Opportunity Teams', bn: 'সুযোগ টিম', t: 'g' },
      { id: 'M07-forecast', en: 'Forecast', bn: 'পূর্বাভাস', t: 'g' },
      { id: 'M07-quotas', en: 'Sales Quotas', bn: 'বিক্রয় কোটা', t: 'g' },
      { id: 'M07-quotes', en: 'Opportunity Estimates', bn: 'সুযোগের প্রাক্কলন', t: 'g' },
      { id: 'M07-form-quote', en: 'Opportunity Estimate', bn: 'প্রাক্কলন ফর্ম', t: 'f' }
    ]},
    { en: 'Accounts', bn: 'অ্যাকাউন্ট', screens: [
      { id: 'M07-key-accounts', en: 'Key Accounts & Stakeholders', bn: 'কী অ্যাকাউন্ট ও স্টেকহোল্ডার', t: 'g' },
      { id: 'M07-accounts', en: 'Corporate Accounts', bn: 'কর্পোরেট অ্যাকাউন্ট', t: 'g' },
      { id: 'M07-eligibility', en: 'Dedicated-Manager Criteria', bn: 'ডেডিকেটেড ম্যানেজার মানদণ্ড', t: 'g' },
      { id: 'M07-plans', en: 'Account Plans', bn: 'অ্যাকাউন্ট পরিকল্পনা', t: 'g' },
      { id: 'M07-qbr', en: 'QBR Scheduler', bn: 'কিউবিআর সময়সূচি', t: 'g' },
      { id: 'M07-qbr-actions', en: 'QBR Agreed Actions', bn: 'কিউবিআর সিদ্ধান্ত', t: 'g' },
      { id: 'M07-activities', en: 'Activities & Visits', bn: 'কার্যক্রম ও সাক্ষাৎ', t: 'g' }
    ]},
    { en: 'Renewals & Growth', bn: 'নবায়ন ও প্রবৃদ্ধি', screens: [
      { id: 'M07-t90', en: 'T-90 Renewal Register', bn: 'টি-৯০ নবায়ন রেজিস্টার', t: 'r' },
      { id: 'M07-crosssell', en: 'Cross-Sell / Upsell', bn: 'ক্রস-সেল / আপসেল', t: 'r' },
      { id: 'M07-winloss', en: 'Win/Loss Analysis', bn: 'জয়/পরাজয় বিশ্লেষণ', t: 'r' }
    ]},
    { en: 'CRM Configuration & Forms', bn: 'কনফিগারেশন ও ফর্ম', screens: [
      { id: 'M07-renewals', en: 'Contract Renewals', bn: 'চুক্তি নবায়ন', t: 'g' },
      { id: 'M07-form-lead', en: 'Lead', bn: 'লিড ফর্ম', t: 'f' },
      { id: 'M07-form-opp', en: 'Opportunity', bn: 'সুযোগ ফর্ম', t: 'f' },
      { id: 'M07-form-activity', en: 'Activity (call/visit/meeting)', bn: 'কার্যক্রম ফর্ম', t: 'f' },
      { id: 'M07-form-competitor', en: 'Competitor Intelligence', bn: 'প্রতিযোগী তথ্য ফর্ম', t: 'f' },
      { id: 'M07-form-account', en: 'Key Account & Stakeholders', bn: 'কী অ্যাকাউন্ট ফর্ম', t: 'f' },
      { id: 'M07-form-plan', en: 'Account Plan', bn: 'পরিকল্পনা ফর্ম', t: 'f' },
      { id: 'M07-form-pipeline', en: 'Pipeline Configuration', bn: 'পাইপলাইন কনফিগ', t: 'f' },
      { id: 'M07-form-assignment', en: 'Account Assignment', bn: 'অ্যাসাইনমেন্ট ফর্ম', t: 'f' },
      { id: 'M07-form-qbr', en: 'Quarterly Business Review', bn: 'কিউবিআর ফর্ম', t: 'f' },
      { id: 'M07-form-renewal', en: 'Renewal Pursuit', bn: 'নবায়ন ফর্ম', t: 'f' },
      { id: 'M07-form-forecast', en: 'Forecast Snapshot', bn: 'ফোরকাস্ট ফর্ম', t: 'f' },
      { id: 'M07-form-qualification', en: 'Lead Qualification', bn: 'লিড যোগ্যতা ফর্ম', t: 'f' },
      { id: 'M07-form-opp-team', en: 'Opportunity Team', bn: 'সুযোগ টিম ফর্ম', t: 'f' },
      { id: 'M07-form-quota', en: 'Sales Quota', bn: 'কোটা ফর্ম', t: 'f' },
      { id: 'M07-form-eligibility', en: 'Dedicated-Manager Eligibility Criteria', bn: 'যোগ্যতার মানদণ্ড ফর্ম', t: 'f' }
    ]},
    { en: 'Pipeline Reports', bn: 'রিপোর্ট', screens: [
      { id: 'M07-rpt-pipeline', en: 'Pipeline by Stream', bn: 'স্ট্রিমভিত্তিক পাইপলাইন', t: 'r' },
      { id: 'M07-rpt-funnel', en: 'Funnel Conversion', bn: 'ফানেল রূপান্তর', t: 'r' },
      { id: 'M07-rpt-winsrc', en: 'Win Rate by Source', bn: 'উৎসভিত্তিক জয়ের হার', t: 'r' },
      { id: 'M07-rpt-amscore', en: 'Account Manager Scorecard', bn: 'এএম স্কোরকার্ড', t: 'r' },
      { id: 'M07-rpt-renewalrisk', en: 'Renewal Risk Report', bn: 'নবায়ন ঝুঁকি রিপোর্ট', t: 'r' },
      { id: 'M07-rpt-crosssell', en: 'Cross-Sell Attach Rate', bn: 'ক্রস-সেল সংযুক্তি হার', t: 'r' }
    ]},
    { en: 'Sequences & Playbooks', bn: 'সিকোয়েন্স ও প্লেবুক', screens: [
      { id: 'M07-sequences', en: 'Sequences & Playbooks', bn: 'সিকোয়েন্স', t: 'g' },
      { id: 'M07-form-sequence', en: 'Sequence', bn: 'সিকোয়েন্স ফর্ম', t: 'f' },
      { id: 'M07-sequence-enrolments', en: 'Cadence Enrolments', bn: 'ক্যাডেন্স তালিকাভুক্তি', t: 'g' }
    ]},
    { en: 'Lead Scoring', bn: 'লিড স্কোরিং', screens: [
      { id: 'M07-score-models', en: 'Scoring Models', bn: 'স্কোরিং মডেল', t: 'g' },
      { id: 'M07-form-score-model', en: 'Scoring Model', bn: 'স্কোরিং ফর্ম', t: 'f' }
    ]}
  ],
  reports: ['Pipeline by Stream', 'Funnel Conversion', 'Win Rate by Source', 'Account Manager Scorecard', 'Renewal Risk Report', 'Cross-Sell Attach Rate'],
  forms: ['Lead', 'Opportunity', 'Activity (call/visit/meeting)', 'Account Plan', 'Pipeline Configuration', 'Account Assignment', 'Quarterly Business Review', 'Renewal Pursuit', 'Forecast Snapshot', 'Sequence / Playbook', 'Lead Scoring Model', 'Opportunity Estimate', 'Key Account & Stakeholders', 'Competitor Intelligence', 'Lead Qualification', 'Opportunity Team', 'Sales Quota', 'Dedicated-Manager Eligibility Criteria'],
  cross: ['M33 Party Master', 'M08 Service Contracts', 'M01 Service Orders', 'M20 Credit Control', 'M53 Commissions'],
  freg: {
    src: 79,
    sub: [
      ['1', 'Lead Capture & Qualification', 12, { model: 'crm.lead', cols: ['name', 'partner_id', 'stage_id', 'user_id', 'type'], screens: ['M07-leads', 'M07-qualifications'], reports: ['Win Rate by Source'], forms: ['Lead', 'Lead Qualification', 'Lead Scoring Model'], create: 'M07-form-lead' }],
      ['2', 'Opportunity Stages', 10, { model: 'crm.lead', cols: ['name', 'partner_id', 'stage_id', 'expected_revenue', 'probability'], screens: ['M07-opps', 'M07-kanban', 'M07-opp-team'], reports: ['Funnel Conversion'], forms: ['Opportunity', 'Opportunity Team', 'Pipeline Configuration'] }],
      ['3', 'Pipeline & Forecasting', 9, { model: 'fix.forecast.snapshot', cols: ['period', 'owner_id', 'pipeline_id', 'commit_value', 'best_case_value', 'pipeline_value'], screens: ['M07-forecast', 'M07-quotas', 'M07-rpt-pipeline', 'M07-rpt-funnel'], reports: ['Pipeline by Stream', 'Funnel Conversion'], forms: ['Forecast Snapshot', 'Sales Quota'] }],
      /* 4 FR-CRM-028/029: the plan, and the decision makers it is written
       * for - mapped on the key-account record (fix.account.stakeholder). */
      ['4', 'Account Plans & Stakeholders', 9, { model: 'fix.account.plan', cols: ['partner_id', 'period', 'objectives', 'whitespace_json', 'risks', 'actions'], screens: ['M07-plans', 'M07-key-accounts'], reports: [], forms: ['Account Plan', 'Key Account & Stakeholders'] }],
      ['5', 'Account-Manager Assignment', 6, { model: 'fix.account.assignment', cols: ['partner_id', 'owner_id', 'assignment_type', 'dedicated', 'effective_from', 'effective_to'], screens: ['M07-accounts', 'M07-eligibility', 'M07-rpt-amscore'], reports: ['Account Manager Scorecard'], forms: ['Account Assignment', 'Dedicated-Manager Eligibility Criteria'] }],
      ['6', 'QBR Programme', 7, { model: 'fix.qbr', cols: ['state', 'partner_id', 'period', 'scheduled_for', 'held_on', 'attendees'], screens: ['M07-qbr', 'M07-qbr-actions'], reports: [], forms: ['Quarterly Business Review'] }],
      /* 7 FR-CRM-045: the calls, meetings, site visits, e-mails and tasks
       * themselves (fix.sales.activity), each with its outcome and next step. */
      ['7', 'Activities', 8, { model: 'fix.sales.activity', cols: ['occurred_at', 'activity_type', 'name', 'lead_id', 'partner_id', 'owner_id', 'outcome', 'next_action_date'], screens: ['M07-activities'], reports: [], forms: ['Activity (call/visit/meeting)', 'Sequence / Playbook'] }],
      ['8', 'Renewal Pipeline', 6, { model: 'fix.renewal', cols: ['state', 'partner_id', 'source_type', 'source_ref', 'value', 'expiry_date'], screens: ['M07-renewals', 'M07-rpt-renewalrisk'], reports: ['Renewal Risk Report'], forms: ['Renewal Pursuit'] }],
      /* 9 FR-CRM-044: an expansion opportunity on the installed base - the
       * page used to list every opportunity and capture none; "+ New" opens
       * the opportunity form with the cross-sell flag already ticked. */
      ['9', 'Cross-Sell / Upsell', 7, { model: 'crm.lead', cols: ['name', 'partner_id', 'is_cross_sell', 'expected_revenue', 'stage_id'], screens: ['M07-crosssell', 'M07-rpt-crosssell', 'M07-opps'], reports: ['Cross-Sell Attach Rate'], forms: ['Opportunity', 'Opportunity Estimate'], create: 'M07-form-opp', domain: [['type', '=', 'opportunity'], ['is_cross_sell', '=', true]] }],
      /* 10 FR-CRM-015: who we compete with, their bid and our price
       * position, recorded on the opportunity while it is pursued (a Lost
       * outcome refuses to close without it). Lost deals are archived, so
       * the page lists the live and won ones; the report covers all. */
      ['10', 'Competitor Intelligence', 5, { model: 'crm.lead', cols: ['name', 'partner_id', 'competitor', 'competitor_price_bdt', 'price_position', 'won_status'], screens: ['M07-winloss', 'M07-sources', 'M07-rpt-winsrc'], reports: ['Win Rate by Source'], forms: ['Competitor Intelligence'], create: 'M07-form-competitor', domain: [['type', '=', 'opportunity'], ['competitor', '!=', false]] }]
    ]
  }
};

export const SCREENS = {
  'M07-kanban': { kind: 'model_list', model: 'crm.lead', create: true,
    cols: ['name', 'partner_id', 'expected_revenue', 'stage_id', 'user_id', 'forecast_category'],
    stateField: 'stage_id' },
  'M07-leads': { kind: 'model_list', model: 'crm.lead', create: true,
    cols: ['name', 'partner_id', 'lead_source', 'qualification_state', 'expected_revenue', 'user_id', 'create_date'],
    domain: [['type', '=', 'lead']],
    actions: [
      { m: 'action_score', l: 'Score Lead' },
      { m: 'action_convert_to_opportunity', l: 'Convert to Opportunity' }
    ] },
  'M07-opps': { kind: 'model_list', model: 'crm.lead', create: true,
    cols: ['name', 'partner_id', 'pipeline_id', 'expected_revenue', 'probability', 'forecast_category', 'stage_id'],
    domain: [['type', '=', 'opportunity']],
    stateField: 'stage_id',
    actions: [
      { m: 'action_raise_estimate', l: 'Raise Estimate' },
      { m: 'action_link_estimate', l: 'Link Estimate', ask: 'Estimate number', kwarg: 'estimate' },
      { m: 'action_request_contract_verification', l: 'Request Contract Verification', ask: 'Note for the verifier', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Verification Request' },
      { m: 'action_score', l: 'Score Lead' },
      { m: 'action_set_won', l: 'Mark Won' },
      { m: 'action_convert_to_service_order', l: 'Convert to Service Order' },
      { m: 'action_set_lost', l: 'Mark Lost', ask: 'Loss reason code (name the competitor on the form first)', kwarg: 'reason' }
    ] },
  'M07-forecast': { kind: 'model_list', model: 'fix.forecast.snapshot', create: true,
    cols: ['period', 'owner_id', 'pipeline_id', 'pipeline_value', 'best_case_value', 'commit_value', 'taken_at'],
    note: 'Forecast snapshots by commit category (pipeline / best case / commit).' },
  'M07-accounts': { kind: 'model_list', model: 'fix.account.assignment', create: true,
    cols: ['partner_id', 'owner_id', 'assignment_type', 'effective_from', 'effective_to', 'eligibility_basis', 'exception_approved_by'],
    actions: [{ m: 'action_assign_unowned', l: 'Assign Unowned Accounts' }] },
  'M07-plans': { kind: 'model_list', model: 'fix.account.plan', create: true,
    cols: ['partner_id', 'period', 'reviewed_at', 'company_id'],
    actions: [{ m: 'action_mark_reviewed', l: 'Mark Reviewed' }] },
  'M07-qbr': { kind: 'model_list', model: 'fix.qbr', create: true,
    cols: ['partner_id', 'period', 'scheduled_for', 'state', 'held_on', 'open_action_count'],
    stateField: 'state',
    actions: [
      { m: 'action_mark_data_ready', l: 'Data Pack Ready' },
      { m: 'action_mark_held', l: 'Mark Held' }
    ] },
  'M07-renewals': { kind: 'model_list', model: 'fix.renewal', create: true,
    cols: ['partner_id', 'source_ref', 'expiry_date', 'value', 'state', 'risk_band'],
    stateField: 'state',
    actions: [
      { m: 'action_engage', l: 'Start Engagement' },
      { m: 'action_renew', l: 'Mark Renewed' },
      { m: 'action_lapse', l: 'Mark Lapsed' },
      { m: 'action_close', l: 'Close (No Renewal Possible)', ask: 'Why no renewal is possible', kwarg: 'reason' }
    ] },
  'M07-winloss': { kind: 'table_report', module: 'M07', report: 'winloss_summary', title: 'Win/Loss Analysis', period: true },
  'M07-activities': { kind: 'model_list', model: 'fix.sales.activity', create: true,
    cols: ['occurred_at', 'activity_type', 'name', 'lead_id', 'partner_id', 'owner_id', 'outcome', 'next_action', 'next_action_date'],
    note: 'Every call, meeting, site visit, e-mail and task, against a lead, an opportunity or an account. A next step with a due date becomes a To-Do for whoever did the activity.' },
  'M07-key-accounts': { kind: 'model_list', model: 'fix.account', create: true,
    cols: ['name', 'account_code', 'tier', 'industry_vertical', 'health_rating', 'acv_bdt', 'user_id', 'last_qbr_date', 'qbr_overdue'],
    note: 'One record per corporate customer: tier, health, contract value and the people who decide inside it. The account manager is the current Corporate Accounts assignment.' },
  'M07-scoring': { kind: 'model_list', model: 'fix.pipeline', create: true,
    cols: ['code', 'name', 'revenue_stream', 'default_probability', 'active'],
    note: 'Pipeline scoring & routing streams that gate opportunity stages by revenue stream.' },
  'M07-sources': { kind: 'table_report', module: 'M07', report: 'win_rate_by_source', title: 'Sources & Campaigns', period: true },
  'M07-t90': { kind: 'table_report', module: 'M07', report: 'renewal_risk', title: 'T-90 Renewal Register', period: true },
  'M07-crosssell': { kind: 'table_report', module: 'M07', report: 'crosssell_attach', title: 'Cross-Sell / Upsell', period: true },

  /* Built-in reports */
  'M07-rpt-pipeline': { kind: 'table_report', module: 'M07', report: 'pipeline_by_stream', title: 'Pipeline by Stream', period: false },
  'M07-rpt-funnel': { kind: 'table_report', module: 'M07', report: 'funnel_conversion', title: 'Funnel Conversion', period: false },
  'M07-rpt-winsrc': { kind: 'table_report', module: 'M07', report: 'win_rate_by_source', title: 'Win Rate by Source', period: false },
  'M07-rpt-amscore': { kind: 'table_report', module: 'M07', report: 'am_scorecard', title: 'Account Manager Scorecard', period: false },
  'M07-rpt-renewalrisk': { kind: 'table_report', module: 'M07', report: 'renewal_risk', title: 'Renewal Risk Report', period: false },
  'M07-rpt-crosssell': { kind: 'table_report', module: 'M07', report: 'crosssell_attach', title: 'Cross-Sell Attach Rate', period: false },

  /* ==================================================================
   * D365 IN-WORKSPACE RECORD FORMS (Dynamics 365 Multi-Tab Forms)
   * ================================================================== */
  'M07-form-lead': {
    lines: {
      field: 'calendar_event_ids',
      title: 'Meetings on this Lead',
      note: 'Calls, visits and meetings scheduled against the lead.',
      fields: [
        { name: 'name', label: 'Subject', required: true },
        { name: 'start', label: 'Start' },
        { name: 'stop', label: 'End' },
        { name: 'user_id', label: 'Organiser' },
        { name: 'location', label: 'Location' }
      ]
    }, kind: 'model_form', model: 'crm.lead',
    title: 'Lead', back: 'M07-leads',
    tabs: [
      { id: 'general', label: '1. Lead Profile', bn: '১. লিড প্রোফাইল', icon: '🎯', badge: '5' },
      { id: 'firmographics', label: '2. B2B Account & Firmographics', bn: '২. অ্যাকাউন্ট বিবরণ', icon: '🏢', badge: '3' },
      { id: 'commercials', label: '3. Pursuit & Expected Commercials', bn: '৩. বাণিজ্যিক সম্ভাবনা', icon: '💰', badge: '4' },
      { id: 'qualification', label: '4. Kernel Match & Conversion', bn: '৪. কার্নেল ম্যাচ ও রূপান্তর', icon: '✅', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Lead Identification', fields: [
        { name: 'name', required: true, label: 'Lead Title / Subject' },
        // posted on create (no user holds Odoo's "use leads" right, so the
        // default made every new lead an opportunity); locked once saved
        { name: 'type', value: 'lead', label: 'Lead Classification' },
        { name: 'partner_id', label: 'Linked Customer / Party' },
        { name: 'lead_source', label: 'Inbound Acquisition Source' },
        { name: 'user_id', label: 'Assigned Sales Representative' },
      ]},
      { tab: 'firmographics', title: 'Contact Person & Firmographics', fields: [
        { name: 'contact_name', label: 'Primary Contact Person' },
        { name: 'email_from', label: 'Contact Email' },
        { name: 'phone', label: 'Telephone Number' },
      ]},
      { tab: 'commercials', title: 'Expected Commercials & Expansion', fields: [
        { name: 'expected_revenue', label: 'Expected Revenue (BDT)' },
        { name: 'probability', label: 'Closing Probability %' },
        { name: 'date_deadline', label: 'Target Closing Date' },
        { name: 'is_cross_sell', label: 'Cross-Sell / Installed Base Expansion' },
      ]},
      { tab: 'qualification', title: 'Qualification & Party Match',
        note: 'A lead converts to an opportunity once it is qualified (need, authority, budget and timing: + Qualify a Lead on the Leads page) and matched to its party in the M33 master (BRU-CRM-02). Conversion never creates a duplicate party.',
        fields: [
          { name: 'qualification_state', readonly: true, label: 'Qualification' },
          { name: 'lead_score', readonly: true, label: 'Lead Score' }
        ] }
    ] },

  'M07-form-opp': {
    lines: {
      field: 'calendar_event_ids',
      title: 'Meetings on this Opportunity',
      note: 'Calls, visits and meetings scheduled against the opportunity.',
      fields: [
        { name: 'name', label: 'Subject', required: true },
        { name: 'start', label: 'Start' },
        { name: 'stop', label: 'End' },
        { name: 'user_id', label: 'Organiser' },
        { name: 'location', label: 'Location' }
      ]
    },
    // M07 capture pass 2, FR-CRM-013: the people working the pursuit
    grids: [
      {
        field: 'team_member_ids', tab: 'team', title: 'Opportunity Team',
        addLabel: '+ Add contributor',
        empty: 'Nobody besides the owner yet. Add the technical, commercial and executive contributors.',
        note: 'The owner is the Assigned Key Account Manager. Only the owner or a sales manager changes the team.',
        fields: [
          { name: 'user_id', label: 'Contributor' },
          { name: 'role', label: 'Role' },
          { name: 'notes', label: 'Responsibility' }
        ]
      }
    ],
    kind: 'model_form', model: 'crm.lead',
    title: 'Commercial Opportunity & B2B KAM', back: 'M07-opps',
    tabs: [
      { id: 'general', label: '1. Opportunity Header', bn: '১. সুযোগের শিরোনাম', icon: '💼', badge: '6' },
      { id: 'b2b_profile', label: '2. B2B Client Profile', bn: '২. ক্লায়েন্ট প্রোফাইল', icon: '🏢', badge: '5' },
      { id: 'scope', label: '3. Technical Scope & SLA', bn: '৩. পরিসর ও এসএলএ', icon: '🛠️', badge: '3' },
      { id: 'commercial', label: '4. Commercials & Forecasting', bn: '৪. বাণিজ্যিক শর্ত', icon: '💰', badge: '6' },
      { id: 'competition', label: '5. Competitor Intelligence', bn: '৫. প্রতিযোগী তথ্য', icon: '⚔️', badge: '5' },
      { id: 'stage', label: '6. Stage Gating & Duration', bn: '৬. পর্যায় গেটিং', icon: '📊', badge: '3' },
      { id: 'team', label: '6a. Opportunity Team', bn: '৬ক. সুযোগ টিম', icon: '👥' },
      { id: 'docs', label: '7. Contracts, PO & Evidence', bn: '৭. চুক্তি ও নথি', icon: '📎', badge: '9' },
      { id: 'audit', label: '8. System Audit Trail', bn: '৮. সিস্টেম অডিট', icon: '⏱️', badge: '4' }
    ],
    sections: [
      { tab: 'general', title: 'Opportunity Overview & Corporate Account', fields: [
        { name: 'name', required: true, label: 'Deal Title / Opportunity Name' },
        { name: 'type', value: 'opportunity', label: 'Record Type' },
        { name: 'partner_id', required: true, label: 'Key Account / Corporate Customer' },
        { name: 'user_id', required: true, label: 'Assigned Key Account Manager' },
        { name: 'team_id', label: 'Commercial Sales Team' },
        { name: 'stage_id', label: 'Current Sales Stage' },
        { name: 'company_id', label: 'Operating Legal Entity' },
      ]},
      { tab: 'b2b_profile', title: 'Key Decision Maker & Corporate Contact', fields: [
        { name: 'contact_name', label: 'Primary Contact / Decision Maker' },
        { name: 'email_from', label: 'Official Business Email' },
        { name: 'phone', label: 'Telephone Number' },
        { name: 'phone_sanitized', label: 'Sanitized Mobile Number', readonly: true },
        { name: 'city', label: 'Corporate Office Location / City' },
      ]},
      { tab: 'scope', title: 'Scope of Service & Order Conversion', fields: [
        { name: 'description', label: 'Service Scope / Requirements', type: 'text' },
        { name: 'is_cross_sell', label: 'Cross-Sell / Expansion Engagement' },
        { name: 'converted_service_order_id', label: 'Converted Service Order Link', readonly: true },
      ]},
      { tab: 'commercial', title: 'Commercial Value & Forecast Classification', fields: [
        { name: 'expected_revenue', required: true, label: 'Expected Deal Value (BDT)' },
        { name: 'probability', label: 'Closing Probability %' },
        { name: 'date_deadline', label: 'Target Closing Date' },
        { name: 'forecast_category', required: true, label: 'Forecast Category (Commit/Best Case/Pipeline)' },
        { name: 'lead_source', label: 'Lead Source Acquisition Channel' },
        { name: 'automated_probability', label: 'Automated ML Probability %', readonly: true },
      ]},
      { tab: 'competition', title: 'Competitor Intelligence & Structured Loss Analysis', fields: [
        { name: 'competitor', label: 'Primary Winning Competitor' },
        { name: 'competitor_price_bdt', label: 'Competitor Bid Value (BDT)' },
        { name: 'price_position', label: 'Our Price Position' },
        { name: 'loss_reason_category', label: 'Primary Loss Reason Category' },
        { name: 'lost_reason_code', label: 'Detailed Loss Reason Code' },
        { name: 'lost_reason_id', label: 'Formal Loss Reason Reference' },
      ]},
      { tab: 'stage', title: 'Stage Gating & Advancement Criteria',
        note: 'Stage transitions to Proposal and Won require confirmed entry criteria and credit clearance under DOFA governance.',
        fields: [
          { name: 'criteria_confirmed', label: 'Stage Entry Criteria Formally Confirmed' },
          { name: 'date_last_stage_update', label: 'Last Stage Advancement Date', readonly: true },
          { name: 'duration_tracking', label: 'Stage Dwell Time Tracking (JSON)', readonly: true },
        ]},
      { tab: 'docs', title: 'Corporate Contracts, Purchase Orders & Evidence',
        note: 'REQ-07.1: marking Won requires a verified signed contract or PO captured here, and no receivable more than 60 days overdue. Signed MSAs, SLA schedules and tender documents attach to this record; the checksummed repository (fix.document, M24) is the estate-wide contract archive — a direct opportunity→document relation is a declared platform gap.',
        fields: [
        { name: 'contract_ref', label: 'Contract / Purchase Order Reference' },
        { name: 'contract_verified', label: 'Contract / PO Verified (set by the verifier)', readonly: true },
        { name: 'rate_card_approved', label: 'Rate Card Confirmed (set by the verifier)', readonly: true },
        { name: 'approval_state', label: 'Contract Verification Request', readonly: true },
        { name: 'contract_verified_by', label: 'Verified By', readonly: true },
        { name: 'contract_verified_at', label: 'Verified On', readonly: true },
        { name: 'company_currency', label: 'Transaction Currency', readonly: true },
      ]},
      { tab: 'docs', title: 'Estimate & Quote Approval',
        note: 'An approved estimate is required before the deal is won or converted (approved quote before order). Raise or link it from the Opportunities screen; add its lines and approve it in M36 Quotations. An edit after approval, or a discount whose approval is pending or was rejected, blocks the win until a revision is approved.',
        fields: [
        { name: 'quote_estimate_id', label: 'Current Estimate', readonly: true },
        { name: 'quote_status', label: 'Quote Status', readonly: true },
      ]},
      { tab: 'audit', title: 'System Governance & Lifecycle Timestamps', fields: [
        { name: 'create_date', label: 'Opportunity Created Timestamp', readonly: true },
        { name: 'date_closed', label: 'Opportunity Final Closed Date', readonly: true },
        { name: 'active', label: 'Active Pipeline Status' },
        { name: 'write_date', label: 'Last System Modification Timestamp', readonly: true },
      ]}
    ] },

  'M07-form-plan': { kind: 'model_form', model: 'fix.account.plan',
    title: 'Account Plan', back: 'M07-plans',
    tabs: [
      { id: 'overview', label: '1. Account Plan Scope', bn: '১. অ্যাকাউন্ট প্ল্যান পরিধি', icon: '📋', badge: '3' },
      { id: 'strategy', label: '2. Objectives & Whitespace', bn: '২. উদ্দেশ্য ও সুযোগ', icon: '🎯', badge: '2' },
      { id: 'risks', label: '3. Risk Controls & Planned Actions', bn: '৩. ঝুঁকি ও কর্মপরিকল্পনা', icon: '🛡️', badge: '2' },
      { id: 'governance', label: '4. Institutional Governance', bn: '৪. প্রাতিষ্ঠানিক মেমোরি', icon: '🏛️', badge: '1' }
    ],
    sections: [
      { tab: 'overview', title: 'Account & Planning Period', fields: [
        { name: 'partner_id', required: true, label: 'Key Account' },
        { name: 'period', required: true, placeholder: '2026 or 2026-Q4', label: 'Planning Period' },
        { name: 'reviewed_at', readonly: true, label: 'Last Executive Review Timestamp' },
      ]},
      { tab: 'strategy', title: 'Strategic Objectives & Revenue Whitespace', fields: [
        { name: 'objectives', label: 'Strategic Objectives', type: 'text' },
        { name: 'whitespace_json', label: 'Service Whitespace Opportunities (JSON)', type: 'text' },
      ]},
      { tab: 'risks', title: 'Account Risks & Planned Mitigations', fields: [
        { name: 'risks', label: 'Identified Account Risks', type: 'text' },
        { name: 'actions', label: 'Planned Strategic Actions', type: 'text' },
      ]},
      { tab: 'governance', title: 'Institutional Memory & Continuity Policy',
        note: 'An account plan survives the account manager departure — it is the institutional memory of the corporate relationship (FR-CRM-028). Mark Reviewed from the Account Plans screen.',
        fields: [] }
    ] },

  'M07-form-pipeline': { kind: 'model_form', model: 'fix.pipeline',
    title: 'Pipeline Configuration', back: 'M07-kanban',
    tabs: [
      { id: 'definition', label: '1. Pipeline Configuration', bn: '১. পাইপলাইন কনফিগারেশন', icon: '⚙️', badge: '5' },
      { id: 'stages', label: '2. Stage Progression & Probability', bn: '২. পর্যায় ও সম্ভাবনা', icon: '📊', badge: '1' },
      { id: 'rules', label: '3. Stage Entry Gating Rules', bn: '৩. স্টেজ গেটিং রুলস', icon: '🔒', badge: '1' }
    ],
    sections: [
      { tab: 'definition', title: 'Pipeline Definition', fields: [
        { name: 'code', required: true, label: 'Pipeline Code' },
        { name: 'name', required: true, label: 'Pipeline Name' },
        { name: 'revenue_stream', required: true, label: 'Revenue Stream Category' },
        { name: 'default_probability', label: 'Default Stage Probability %' },
        { name: 'active', label: 'Active Status' },
      ]},
      { tab: 'stages', title: 'Configured Stages Model (JSON T-02)', fields: [
        { name: 'stages_json', label: 'Stages & Entry Criteria (JSON)' },
      ]},
      { tab: 'rules', title: 'Dynamic Revenue Stream Gating Rules',
        note: 'Adding a pipeline for a new revenue stream requires no code release — stages_json carries entry criteria and probabilities; gated stages refuse advancement without confirmed criteria (BRU-CRM-03).',
        fields: [] }
    ] },

  'M07-form-assignment': { kind: 'model_form', model: 'fix.account.assignment',
    title: 'Account Assignment', back: 'M07-accounts',
    tabs: [
      { id: 'ownership', label: '1. Key Account Ownership', bn: '১. অ্যাকাউন্ট মালিকানা', icon: '👤', badge: '3' },
      { id: 'validity', label: '2. Effective Validity Period', bn: '২. কার্যকর সময়কাল', icon: '📅', badge: '2' },
      { id: 'coverage', label: '3. Enterprise Coverage Rules', bn: '৩. কভারেজ নিয়মাবলী', icon: '🛡️', badge: '1' }
    ],
    sections: [
      { tab: 'ownership', title: 'Key Account Ownership (BRU-CRM-08)', fields: [
        { name: 'partner_id', required: true, label: 'Key Account' },
        { name: 'owner_id', required: true, label: 'Assigned Account Manager' },
        { name: 'assignment_type', required: true, label: 'Assignment Type (Primary / Specialist / Overlay)' },
      ]},
      { tab: 'validity', title: 'Effective Assignment Window', fields: [
        { name: 'effective_from', required: true, label: 'Assignment Effective Date' },
        { name: 'effective_to', label: 'Valid Until (Empty = Indefinite)' },
      ]},
      { tab: 'coverage', title: 'Dedicated Manager Eligibility (BRU-CRM-09)',
        note: 'A Dedicated Manager assignment is checked against the published criteria (Dedicated-Manager Criteria). An account outside them needs an exception reason, and only a sales manager (the CCO) may record it. Every corporate, dealer and government account must have a named owner at all times: Assign Unowned Accounts back-fills the gaps.',
        fields: [
          { name: 'exception_reason', label: 'Exception Reason (outside the criteria)' },
          { name: 'eligibility_basis', readonly: true, label: 'Eligibility Basis' },
          { name: 'exception_approved_by', readonly: true, label: 'Exception Approved By' }
        ] }
    ] },

  'M07-form-qbr': {
    lines: {
      field: 'action_ids',
      title: 'Agreed Actions',
      note: 'What the QBR committed to, who owns it and when it is due.',
      fields: [
        { name: 'description', label: 'Action', required: true },
        { name: 'owner_internal', label: 'Owner (internal)' },
        { name: 'owner_party', label: 'Owner (client side)' },
        { name: 'due_date', label: 'Due' },
        { name: 'state', label: 'State' },
        { name: 'overdue', label: 'Overdue' }
      ]
    }, kind: 'model_form', model: 'fix.qbr',
    title: 'Quarterly Business Review (QBR)', back: 'M07-qbr',
    status: { field: 'state' },
    tabs: [
      { id: 'schedule', label: '1. Review Schedule & Account', bn: '১. কিউবিআর সময়সূচি', icon: '📅', badge: '4' },
      { id: 'meeting', label: '2. Attendees & Decisions', bn: '২. উপস্থিতি ও সিদ্ধান্ত', icon: '📝', badge: '3' },
      { id: 'docs', label: '3. Presentation Pack Reference', bn: '৩. উপস্থাপনা ও নথি', icon: '📎', badge: '2' },
      { id: 'governance', label: '4. SLA Integration & W4 Seam', bn: '৪. এসএলএ ও গভর্নেন্স', icon: '⚖️', badge: '1' }
    ],
    sections: [
      { tab: 'schedule', title: 'Quarterly Review Schedule', fields: [
        { name: 'partner_id', required: true, label: 'Corporate Key Account' },
        { name: 'period', required: true, placeholder: '2026-Q4', label: 'Review Quarter' },
        { name: 'scheduled_for', required: true, label: 'Scheduled Meeting Date' },
        { name: 'state', readonly: true, label: 'QBR Execution State' },
      ]},
      { tab: 'meeting', title: 'Executive Attendees & Meeting Minutes', fields: [
        { name: 'attendees', label: 'Executive Attendees (Client & 1000FiX)', type: 'text' },
        { name: 'decisions', label: 'Discussion, Decisions & Agreed Actions', type: 'text' },
        { name: 'held_on', readonly: true, label: 'Actual Meeting Date' },
      ]},
      { tab: 'docs', title: 'QBR Presentation Pack Reference', fields: [
        { name: 'document_ref', label: 'Presentation Pack / Document Reference' },
      ]},
      { tab: 'governance', title: 'Executive SLA Governance Mandate',
        note: 'Key Accounts classified as Strategic or Enterprise must have a formal QBR held at least once every 90 days. Marking a QBR as Held mandates attendees list, decision minutes, and presentation pack link (FLAW-07.3 / REQ-07.4).',
        fields: [] }
    ] },

  'M07-form-renewal': { kind: 'model_form', model: 'fix.renewal',
    title: 'Contract Renewal Pursuit', back: 'M07-renewals',
    status: { field: 'state' },
    tabs: [
      { id: 'contract', label: '1. Renewal Target & Contract', bn: '১. চুক্তি ও নবায়ন লক্ষ্য', icon: '📄', badge: '4' },
      { id: 'commercials', label: '2. Commercials & Churn Risk', bn: '২. বাণিজ্যিক ও চূর্ণ ঝুঁকি', icon: '💰', badge: '3' },
      { id: 'history', label: '3. Renewal History & Escalations', bn: '৩. ইতিহাস ও এসকেলেশন', icon: '⏳', badge: '2' },
      { id: 'governance', label: '4. Retention Governance & SLA', bn: '৪. রিটেনশন গভর্নেন্স', icon: '🛡️', badge: '1' }
    ],
    sections: [
      { tab: 'contract', title: 'Contract & Account Information', fields: [
        { name: 'partner_id', required: true, label: 'Corporate Account' },
        // M07 capture pass 2: required by the model and missing here, so
        // "+ New Contract Renewal Pursuit" could never save
        { name: 'source_type', required: true, label: 'Renewing (Contract / Membership / Warranty Product)' },
        { name: 'source_ref', label: 'Source Contract / AMC Reference' },
        { name: 'expiry_date', required: true, label: 'Contract Expiration Date' },
        { name: 'state', readonly: true, label: 'Renewal Pursuit State' },
      ]},
      { tab: 'commercials', title: 'Renewal Value & Churn Risk Level', fields: [
        { name: 'value', label: 'Projected Renewal Contract Value (BDT)' },
        { name: 'risk_band', label: 'Account Churn Risk Band' },
        { name: 'play', label: 'Renewal Play (FR-CRM-042)' },
        { name: 'lead_time_days', readonly: true, label: 'Created Lead Time (Days Before Expiry)' },
      ]},
      { tab: 'history', title: 'Engagement Timeline', fields: [
        { name: 'auto_created', readonly: true, label: 'Auto-Created From Contract Expiry Engine' },
        { name: 'owner_id', label: 'Renewal Owner (KAM)' },
      ]},
      { tab: 'governance', title: 'Automated Renewal Alerts Policy',
        note: 'The system triggers automated renewal reminders at T-90, T-60, and T-30 calendar days prior to contract expiration. High-risk accounts require immediate KAM escalation (REQ-07.5).',
        fields: [] }
    ] },

  'M07-form-forecast': { kind: 'model_form', model: 'fix.forecast.snapshot',
    title: 'Forecast Snapshot', back: 'M07-forecast',
    newLabel: 'Take a Forecast Snapshot',
    tabs: [
      { id: 'scope', label: '1. Period & Pipeline Scope', bn: '১. পূর্বাভাসের সময়কাল', icon: '📆', badge: '4' },
      { id: 'categories', label: '2. Forecast Categories Breakdown', bn: '২. ক্যাটাগরি বিশ্লেষণ', icon: '📊', badge: '3' },
      { id: 'adjustments', label: '3. Attainment & Manager Adjustments', bn: '৩. ম্যানেজার সমন্বয়', icon: '📈', badge: '3' },
      { id: 'audit', label: '4. Snapshot Lock & Audit', bn: '৪. স্ন্যাপশট অডিট ট্রেইল', icon: '⚙️', badge: '1' }
    ],
    sections: [
      { tab: 'scope', title: 'Snapshot Scope & Revenue Stream', fields: [
        { name: 'period', required: true, placeholder: '2026-Q4 or 2026-10', label: 'Forecast Period' },
        { name: 'owner_id', required: true, label: 'Forecast Owner' },
        { name: 'pipeline_id', required: true, label: 'Revenue Stream Pipeline' },
        { name: 'taken_at', readonly: true, label: 'Snapshot Timestamp' },
      ]},
      { tab: 'categories', title: 'Forecast Category Value Totals',
        note: 'Rolled up on save from the owner\'s open opportunities in the pipeline, by forecast category. Nothing is typed here, and a snapshot is refused when the owner has no open opportunity to forecast.',
        fields: [
        { name: 'commit_value', readonly: true, label: 'Commit Category Value (BDT)' },
        { name: 'best_case_value', readonly: true, label: 'Best Case Value (BDT)' },
        { name: 'pipeline_value', readonly: true, label: 'Pipeline Category Value (BDT)' },
      ]},
      { tab: 'adjustments', title: 'Executive Management Adjustments', fields: [
        { name: 'manager_adjustment', label: 'Manager Judgement Adjustment (BDT)' },
        { name: 'adjustment_reason', label: 'Adjustment Rationale / Justification', type: 'text' },
        { name: 'adjusted_by', readonly: true, label: 'Adjusted By' },
      ]},
      { tab: 'audit', title: 'Immutable Forecast Governance Law',
        note: 'Forecast snapshots freeze the pipeline state at a moment in time (FR-CRM-022) — they are never retroactively recalculated. Manager adjustments preserve the original rep rollup alongside.',
        fields: [] }
    ] },

  /* M07 audit 2026-11-13: the activity itself (FR-CRM-045). The form this
   * replaces edited a LEAD's next-activity snapshot: its due date is computed
   * by Odoo, so every save that set one was refused, and opened blank it
   * created a new lead named after the "activity". */
  'M07-form-activity': { kind: 'model_form', model: 'fix.sales.activity',
    title: 'Activity (call/visit/meeting)', back: 'M07-activities',
    newLabel: 'Log a Call, Visit or Meeting',
    status: { field: 'activity_type', labels: { call: 'Phone Call', meeting: 'Meeting', site_visit: 'Site Visit', email: 'E-mail', task: 'Task' } },
    tabs: [
      { id: 'what', label: '1. What Happened', bn: '১. কী হয়েছে', icon: '📞', badge: '6' },
      { id: 'against', label: '2. Lead, Opportunity or Account', bn: '২. লিড, সুযোগ বা অ্যাকাউন্ট', icon: '🎯', badge: '3' },
      { id: 'outcome', label: '3. Outcome & Next Step', bn: '৩. ফলাফল ও পরবর্তী পদক্ষেপ', icon: '✅', badge: '5' }
    ],
    sections: [
      { tab: 'what', title: 'The Interaction', fields: [
        { name: 'activity_type', required: true, label: 'Activity Type' },
        { name: 'name', required: true, label: 'Subject' },
        { name: 'occurred_at', required: true, label: 'When' },
        { name: 'duration_minutes', label: 'Duration (minutes)' },
        { name: 'location', label: 'Location / Site Address' },
        { name: 'owner_id', required: true, label: 'Done By' }
      ]},
      { tab: 'against', title: 'Who It Was With',
        note: 'Pick the lead or opportunity; the account fills in from it. A visit to a customer with no open pursuit is logged against the account alone.',
        fields: [
        { name: 'lead_id', label: 'Lead / Opportunity' },
        { name: 'partner_id', label: 'Account' },
        { name: 'subject_type', readonly: true, label: 'Logged Against' }
      ]},
      { tab: 'outcome', title: 'Outcome & Reminder',
        note: 'A next step with a due date schedules a To-Do for the person who did the activity, on the lead or the account: that is the reminder.',
        fields: [
        { name: 'outcome', label: 'Outcome' },
        { name: 'notes', type: 'text', label: 'Notes / Minutes' },
        { name: 'next_action', label: 'Next Step' },
        { name: 'next_action_date', label: 'Next Step Due' },
        { name: 'reminder_activity_id', readonly: true, label: 'Reminder Scheduled' }
      ]}
    ] },

  /* FR-CRM-028/029: the key-account master and its decision makers. The
   * model was built on 31 Oct but no screen served it. */
  'M07-form-account': {
    lines: {
      field: 'stakeholder_ids',
      title: 'Decision Makers & Influencers',
      note: 'Who decides inside the account, their buying role and how they lean towards us.',
      fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'designation', label: 'Designation' },
        { name: 'buying_role', label: 'Buying Role', required: true },
        { name: 'sentiment', label: 'Sentiment' },
        { name: 'phone', label: 'Phone' },
        { name: 'email', label: 'E-mail' },
        { name: 'partner_id', label: 'Contact Record' }
      ]
    },
    kind: 'model_form', model: 'fix.account',
    title: 'Key Account & Stakeholders', back: 'M07-key-accounts',
    status: { field: 'health_rating', labels: { healthy: 'Healthy', neutral: 'Neutral', at_risk: 'At Risk', critical: 'Critical' } },
    tabs: [
      { id: 'profile', label: '1. Account Profile', bn: '১. অ্যাকাউন্ট প্রোফাইল', icon: '🏢', badge: '6' },
      { id: 'value', label: '2. Value & Health', bn: '২. মূল্য ও স্বাস্থ্য', icon: '💰', badge: '8' }
    ],
    sections: [
      { tab: 'profile', title: 'Corporate Customer', fields: [
        { name: 'partner_id', required: true, label: 'Corporate Party' },
        { name: 'account_code', label: 'Account Code' },
        { name: 'tier', required: true, label: 'Account Tier' },
        { name: 'industry_vertical', required: true, label: 'Industry Vertical' },
        { name: 'operating_unit_id', label: 'Operating Unit' },
        { name: 'office_address', label: 'Head Office Address' }
      ]},
      { tab: 'value', title: 'Contract Value, Margin & Review Cadence',
        note: 'The account manager is the current Corporate Accounts assignment (BRU-CRM-08); change it there. Strategic and Enterprise accounts need a held QBR every 90 days.',
        fields: [
        { name: 'acv_bdt', label: 'Annual Contract Value (BDT)' },
        { name: 'gross_margin_pct', label: 'Gross Margin (%)' },
        { name: 'account_grade', readonly: true, label: 'Profitability Grade' },
        { name: 'health_rating', label: 'Account Health' },
        { name: 'user_id', readonly: true, label: 'Key Account Manager' },
        { name: 'last_qbr_date', readonly: true, label: 'Last QBR Held' },
        { name: 'days_since_qbr', readonly: true, label: 'Days Since QBR' },
        { name: 'qbr_overdue', readonly: true, label: 'QBR Overdue' }
      ]}
    ] },

  /* FR-CRM-015: competitor and price position on a pursued opportunity -
   * step 1 picks it, step 2 records the intelligence on it. */
  'M07-form-competitor': { kind: 'model_form', model: 'crm.lead',
    title: 'Competitor Intelligence', back: 'M07-opps',
    newLabel: 'Record Competitor Intelligence',
    pickRecord: {
      label: 'Step 1 of 2: choose the opportunity you are competing for',
      note: 'Opportunities, open and won.',
      search: 'Search opportunity',
      choose: 'Record intelligence for this opportunity',
      cols: ['name', 'partner_id', 'stage_id', 'expected_revenue', 'competitor'],
      domain: [['type', '=', 'opportunity']],
      empty: 'No opportunity yet: raise one with + New Opportunity first.'
    },
    sections: [
      { title: 'Step 2 of 2: Who We Compete With (FR-CRM-015)',
        note: 'Record it while the deal is pursued. Marking the deal Lost later also asks for the loss reason.',
        fields: [
        { name: 'name', readonly: true, label: 'Opportunity' },
        { name: 'competitor', required: true, label: 'Competitor' },
        { name: 'competitor_price_bdt', label: 'Competitor Bid (BDT)' },
        { name: 'price_position', label: 'Our Price Position' }
      ]}
    ] },
  /* ==================================================================
   * M07 capture audit, second pass (2026-11-18): the records five pages
   * had nowhere to capture. See tests/test_m07_capture_pass2.py.
   * ================================================================== */

  /* page 1, FR-CRM-002: the need / authority / budget / timing assessment
   * and its outcome. A lead converts only once qualified (lifecycle 8.1). */
  'M07-qualifications': { kind: 'model_list', model: 'fix.lead.qualification', create: true,
    title: 'Qualification Assessments',
    cols: ['assessed_at', 'lead_id', 'partner_id', 'need', 'authority', 'budget', 'timing', 'outcome', 'disqualify_reason', 'assessed_by'],
    note: 'Each assessment is a record of the judgement made and is never edited. Qualified leads convert to opportunities; a disqualified lead closes with its reason; a lead not ready to buy goes back to marketing nurture.' },
  'M07-form-qualification': { kind: 'model_form', model: 'fix.lead.qualification',
    title: 'Lead Qualification', back: 'M07-qualifications',
    newLabel: 'Qualify a Lead',
    status: { field: 'outcome', labels: { qualified: 'Qualified', disqualified: 'Disqualified', nurture: 'Returned to Nurture' } },
    tabs: [
      { id: 'bant', label: '1. Need, Authority, Budget, Timing', bn: '১. প্রয়োজন, কর্তৃত্ব, বাজেট, সময়', icon: '🧭', badge: '7' },
      { id: 'outcome', label: '2. Outcome', bn: '২. ফলাফল', icon: '✅', badge: '5' }
    ],
    sections: [
      { tab: 'bant', title: 'The Assessment (FR-CRM-002)',
        note: 'Qualified needs a confirmed need and at least a partly established authority, budget and timing.',
        fields: [
        { name: 'lead_id', required: true, label: 'Lead' },
        { name: 'need', required: true, label: 'Need' },
        { name: 'authority', required: true, label: 'Authority (decision maker reached)' },
        { name: 'budget', required: true, label: 'Budget' },
        { name: 'budget_bdt', label: 'Indicated Budget (BDT)' },
        { name: 'timing', required: true, label: 'Timing' },
        { name: 'decision_by', label: 'Decision Expected By' }
      ]},
      { tab: 'outcome', title: 'Outcome',
        note: 'Disqualified closes the lead with its reason. Not Ready returns it to marketing nurture (FR-CRM-008) instead of discarding it. Neither can be undone from here.',
        fields: [
        { name: 'outcome', required: true, label: 'Outcome' },
        { name: 'disqualify_reason', label: 'Disqualification Reason' },
        { name: 'notes', type: 'text', label: 'Assessment Notes' },
        { name: 'assessed_by', readonly: true, label: 'Assessed By' },
        { name: 'assessed_at', readonly: true, label: 'Assessed On' }
      ]}
    ] },

  /* page 2, FR-CRM-013: who works the pursuit besides its owner. */
  'M07-opp-team': { kind: 'model_list', model: 'fix.opportunity.team', create: true,
    title: 'Opportunity Teams',
    cols: ['lead_id', 'user_id', 'role', 'notes'],
    note: 'Contributors on each pursued opportunity and their role. Only the opportunity owner or a sales manager changes a team; a closed deal keeps its team as recorded.' },
  'M07-form-opp-team': { kind: 'model_form', model: 'fix.opportunity.team',
    title: 'Opportunity Team Member', back: 'M07-opp-team',
    newLabel: 'Add to an Opportunity Team',
    sections: [
      { title: 'Pursuit Contributor (FR-CRM-013)',
        note: 'The opportunity owner is its salesperson and is not listed. One executive sponsor per opportunity.',
        fields: [
        { name: 'lead_id', required: true, label: 'Opportunity' },
        { name: 'user_id', required: true, label: 'Contributor' },
        { name: 'role', required: true, label: 'Role' },
        { name: 'notes', label: 'Responsibility' }
      ]}
    ] },

  /* page 3, FR-CRM-023: the target the forecast is read against. */
  'M07-quotas': { kind: 'model_list', model: 'fix.sales.quota', create: true,
    title: 'Sales Quotas',
    cols: ['period', 'owner_id', 'pipeline_id', 'target_value', 'achieved_value', 'won_count', 'attainment_pct', 'set_by'],
    note: 'Targets by seller, period and (optionally) pipeline. Attainment counts won deals closed in the period. A sales manager sets quotas, never their own.' },
  'M07-form-quota': { kind: 'model_form', model: 'fix.sales.quota',
    title: 'Sales Quota', back: 'M07-quotas',
    newLabel: 'Set a Sales Quota',
    sections: [
      { title: 'Target (FR-CRM-023)',
        note: 'Period as a year (2026), a quarter (2026-Q4) or a month (2026-11). Leave the pipeline empty for a target across every revenue stream.',
        fields: [
        { name: 'owner_id', required: true, label: 'Seller' },
        { name: 'period', required: true, placeholder: '2026-Q4', label: 'Period' },
        { name: 'pipeline_id', label: 'Pipeline (empty = every stream)' },
        { name: 'target_value', required: true, label: 'Target (BDT)' }
      ]},
      { title: 'Attainment',
        fields: [
        { name: 'achieved_value', readonly: true, label: 'Won (BDT)' },
        { name: 'won_count', readonly: true, label: 'Deals Won' },
        { name: 'attainment_pct', readonly: true, label: 'Attainment %' },
        { name: 'set_by', readonly: true, label: 'Set By' }
      ]}
    ] },

  /* page 5, FR-CRM-027 / BRU-CRM-09: the published criteria a dedicated
   * account manager follows (open question Q-01 is answered here). */
  'M07-eligibility': { kind: 'model_list', model: 'fix.account.eligibility', create: true,
    title: 'Dedicated-Manager Criteria',
    cols: ['name', 'effective_from', 'min_annual_spend_bdt', 'min_acv_bdt', 'strategic_qualifies', 'published_by'],
    note: 'The criteria in force. Publishing new criteria archives the previous set. An account meeting any criterion qualifies for a dedicated manager; any other dedicated assignment is an exception a sales manager approves.' },
  'M07-form-eligibility': { kind: 'model_form', model: 'fix.account.eligibility',
    title: 'Dedicated-Manager Eligibility Criteria', back: 'M07-eligibility',
    newLabel: 'Publish Dedicated-Manager Criteria',
    sections: [
      { title: 'Criteria (FR-CRM-027)',
        note: 'Published by the CCO (a sales manager). Leave a threshold at 0 to not use it. An account qualifies when it meets ANY criterion set.',
        fields: [
        { name: 'name', required: true, placeholder: 'FY2027 criteria', label: 'Criteria Name' },
        { name: 'min_annual_spend_bdt', label: 'Annual Spend At Least (BDT, last 12 months invoiced)' },
        { name: 'min_acv_bdt', label: 'Annual Contract Value At Least (BDT)' },
        { name: 'strategic_qualifies', label: 'Strategic-Tier Accounts Qualify' },
        { name: 'effective_from', required: true, label: 'Effective From' },
        { name: 'published_by', readonly: true, label: 'Published By' }
      ]}
    ] },

  /* page 6, FR-CRM-037/038: agreed actions tracked across reviews; an
   * accepted recommendation becomes an opportunity. Actions are agreed on
   * the QBR form itself, so this list adds none. */
  'M07-qbr-actions': { kind: 'model_list', model: 'fix.qbr.action', create: false,
    title: 'QBR Agreed Actions',
    cols: ['due_date', 'partner_id', 'qbr_period', 'description', 'owner_internal', 'owner_party', 'state', 'overdue', 'opportunity_id'],
    stateField: 'state',
    actions: [
      { m: 'action_close', l: 'Mark Done' },
      { m: 'action_cancel', l: 'Cancel Action' },
      { m: 'action_raise_opportunity', l: 'Raise Opportunity' }
    ],
    note: 'What each review committed to, until it is done. A recommendation the client accepted at a held review becomes an opportunity with Raise Opportunity, once.' },

  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M07-sequences': { kind: 'model_list', model: 'fix.crm.sequence', create: true,
    cols: ['name', 'code', 'sequence_kind', 'applies_to', 'state', 'first_touch_sla_hours', 'step_count', 'active_enrolments', 'sla_breaches'],
    stateField: 'state',
    actions: [
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_pause', l: 'Pause' }
    ],
    note: 'Cadences and playbooks run on the same engine as M35 journeys.' },
  'M07-form-sequence': {
    lines: {
      field: 'step_ids',
      title: 'Cadence Steps',
      note: 'A manual step raises an activity and the member waits on this step until the seller closes it.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'name', label: 'Step', required: true },
        { name: 'step_type', label: 'Type', required: true },
        { name: 'wait_minutes', label: 'Wait Before (min)' },
        { name: 'due_in_days', label: 'Activity Due In (days)' },
        { name: 'instructions', label: 'Instruction' },
        { name: 'email_subject', label: 'E-mail Subject' },
        { name: 'active', label: 'Active' }
      ]
    },
    kind: 'model_form', model: 'fix.crm.sequence',
    title: 'Sequence / Playbook', back: 'M07-sequences',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', paused: 'Paused' } },
    tabs: [
      { id: 'identity', label: '1. Cadence', bn: '১. ক্যাডেন্স', icon: '📅' },
      { id: 'sla', label: '2. First-Touch Promise', bn: '২. প্রথম যোগাযোগ', icon: '⏱️' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Cadence Identity',
        note: 'D365 ships sequences and playbooks as two features on one mechanism. So do we: the engine treats them identically.',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'sequence_kind', label: 'Kind', required: true },
        { name: 'applies_to', label: 'Applies To', required: true },
        { name: 'state', label: 'State', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'sla',
        title: 'First-Touch SLA',
        note: 'A first-touch promise nobody is told about breaking is not a promise, so breaches are published to the outbox.',
        fields: [
        { name: 'first_touch_sla_hours', label: 'First Touch Within (hours)' },
        { name: 'active_enrolments', label: 'Active Enrolments' },
        { name: 'sla_breaches', label: 'Breaches' }
        ]
      }
    ]
  },
  'M07-sequence-enrolments': { kind: 'model_list', model: 'fix.crm.sequence.enrolment', create: false,
    cols: ['next_action_at', 'sequence_id', 'lead_id', 'owner_id', 'current_step_id', 'state', 'first_touch_due_at', 'first_touch_at', 'first_touch_breached'],
    stateField: 'state',
    actions: [
      { m: 'action_pause_member', l: 'Pause' },
      { m: 'action_resume_member', l: 'Resume' }
    ],
    note: 'The first-touch promise, measured. A breach is published, not just coloured in.' },
  'M07-score-models': { kind: 'model_list', model: 'fix.crm.score.model', create: true,
    cols: ['sequence', 'name', 'code', 'basis', 'applies_to', 'state', 'm26_model_ref', 'active'],
    stateField: 'state',
    actions: [
      { m: 'action_activate', l: 'Activate' }
    ],
    note: 'A heuristic is not a prediction, and the basis column never hides which one produced a score.' },
  'M07-form-score-model': {
    lines: {
      field: 'factor_ids',
      title: 'Scoring Factors',
      note: 'Every contribution is inspectable, and a negative weight is how a risk factor is expressed.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'name', label: 'Factor', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'factor', label: 'Measures', required: true },
        { name: 'weight', label: 'Points', required: true },
        { name: 'threshold_value', label: 'Threshold / Values' },
        { name: 'active', label: 'Active' }
      ]
    },
    kind: 'model_form', model: 'fix.crm.score.model',
    title: 'Lead Scoring Model', back: 'M07-score-models',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'identity', label: '1. Model', bn: '১. মডেল', icon: '🎯' },
      { id: 'basis', label: '2. Basis', bn: '২. ভিত্তি', icon: '🔬' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Model Identity',
        fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'code', label: 'Code', required: true },
        { name: 'applies_to', label: 'Applies To', required: true },
        { name: 'sequence', label: 'Priority' },
        { name: 'state', label: 'State', required: true },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'basis',
        title: 'Heuristic Or Prediction',
        note: 'A heuristic is NOT a prediction, and the score records which it was. A seller who believes a number came from a trained model will drop a lead it scored low and nobody will measure whether they should have.',
        fields: [
        { name: 'basis', label: 'Basis', required: true },
        { name: 'm26_model_ref', label: 'M26 Model Reference' }
        ]
      }
    ]
  },

  /* A03 P2: the opportunity's pre-sales estimate (approved quote before
   * order). Raised from M07-opps; priced, sent and approved here. The
   * workflow fields are read-only: only the estimate's own actions and the
   * M63 approval engine set them. */
  'M07-quotes': { kind: 'model_list', model: 'fix.estimate', create: false,
    cols: ['lead_id', 'version', 'state', 'grand_total', 'discount_pct', 'approval_state', 'approved_total'],
    domain: [['lead_id', '!=', false]],
    stateField: 'state',
    actions: [
      { m: 'action_send', l: 'Send to Customer' },
      { m: 'action_approve', l: 'Approve Estimate' },
      { m: 'action_revise', l: 'Revise (New Version)' }
    ],
    note: 'Raise an estimate from the Opportunities screen. A deal is won and converted only on its latest estimate, approved and unchanged since.' },
  'M07-form-quote': {
    lines: {
      field: 'line_ids',
      title: 'Estimate Lines',
      note: 'Parts from inventory (by part number) and service, labour, support, transport or other charges (by charge code) quoted to the customer.',
      fields: [
        { name: 'line_type', label: 'Type', required: true },
        { name: 'product_id', label: 'Item / Part No. (search)' },
        { name: 'item_code', label: 'Item Code', readonly: true },
        { name: 'description', label: 'Description', required: true },
        { name: 'serial_ref', label: 'Serial / IMEI' },
        { name: 'quantity', label: 'Qty', required: true },
        { name: 'uom_id', label: 'Unit' },
        { name: 'unit_price', label: 'Unit Price', required: true },
        { name: 'line_total', label: 'Total', readonly: true }
      ]
    },
    kind: 'model_form', model: 'fix.estimate',
    title: 'Opportunity Estimate', back: 'M07-quotes',
    status: { field: 'state' },
    tabs: [
      { id: 'quote', label: '1. Quote', bn: '১. প্রাক্কলন', icon: '🧾' },
      { id: 'commercial', label: '2. Price & Discount', bn: '২. মূল্য ও ছাড়', icon: '💰' },
      { id: 'approval', label: '3. Approval Evidence', bn: '৩. অনুমোদনের প্রমাণ', icon: '✅' }
    ],
    sections: [
      { tab: 'quote', title: 'Opportunity & Version', fields: [
        { name: 'lead_id', label: 'Opportunity', readonly: true },
        { name: 'version', label: 'Version', readonly: true },
        { name: 'state', label: 'Estimate State', readonly: true },
        { name: 'expiry_date', label: 'Valid Until' },
        { name: 'diagnostic_notes', label: 'Scope & Exclusions', type: 'text' }
      ]},
      { tab: 'commercial', title: 'Totals & Discount Authority',
        note: 'A discount above 5% needs DOFA sign-off from someone other than the seller. Changing the discount while its approval is pending withdraws the request.',
        fields: [
        { name: 'discount', label: 'Discount (BDT)' },
        { name: 'discount_pct', label: 'Discount %', readonly: true },
        { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
        { name: 'dofa_justification', label: 'Discount Justification', type: 'text' },
        { name: 'grand_total', label: 'Grand Total (BDT)', readonly: true }
      ]},
      { tab: 'approval', title: 'Who Approved What', fields: [
        { name: 'customer_approval_ref', label: 'Customer Approval Reference', readonly: true },
        { name: 'approval_state', label: 'Discount Approval Request', readonly: true },
        { name: 'dofa_approved', label: 'Discount Approved', readonly: true },
        { name: 'dofa_approved_by', label: 'Discount Approved By', readonly: true },
        { name: 'manager_approval_uid', label: 'Branch Manager Approval', readonly: true },
        { name: 'approved_total', label: 'Total When Approved', readonly: true },
        { name: 'approval_stamped_at', label: 'Approval Recorded On', readonly: true }
      ]}
    ]
  },
};

export const REPORT_ROUTES = {
  'M07:Pipeline by Stream': 'M07-rpt-pipeline',
  'M07:Funnel Conversion': 'M07-rpt-funnel',
  'M07:Win Rate by Source': 'M07-rpt-winsrc',
  'M07:Account Manager Scorecard': 'M07-rpt-amscore',
  'M07:Renewal Risk Report': 'M07-rpt-renewalrisk',
  'M07:Cross-Sell Attach Rate': 'M07-rpt-crosssell'
};

export const FORM_CHIPS = {
  'M07:Sequence / Playbook': 'M07-form-sequence',
  'M07:Lead Scoring Model': 'M07-form-score-model',
  'M07:Lead': 'M07-form-lead',
  'M07:Opportunity': 'M07-form-opp',
  'M07:Activity (call/visit/meeting)': 'M07-form-activity',
  'M07:Account Plan': 'M07-form-plan',
  'M07:Pipeline Configuration': 'M07-form-pipeline',
  'M07:Account Assignment': 'M07-form-assignment',
  'M07:Quarterly Business Review': 'M07-form-qbr',
  'M07:Renewal Pursuit': 'M07-form-renewal',
  'M07:Forecast Snapshot': 'M07-form-forecast',
  'M07:Opportunity Estimate': 'M07-form-quote',
  'M07:Key Account & Stakeholders': 'M07-form-account',
  'M07:Competitor Intelligence': 'M07-form-competitor',
  'M07:Lead Qualification': 'M07-form-qualification',
  'M07:Opportunity Team': 'M07-form-opp-team',
  'M07:Sales Quota': 'M07-form-quota',
  'M07:Dedicated-Manager Eligibility Criteria': 'M07-form-eligibility',
  'M07:__by_model__': {
    'fix.crm.sequence': 'M07-form-sequence',
    'fix.crm.score.model': 'M07-form-score-model',
    'crm.lead': 'M07-form-opp',
    'fix.account.plan': 'M07-form-plan',
    'fix.pipeline': 'M07-form-pipeline',
    'fix.account.assignment': 'M07-form-assignment',
    'fix.qbr': 'M07-form-qbr',
    'fix.renewal': 'M07-form-renewal',
    'fix.forecast.snapshot': 'M07-form-forecast',
    'fix.estimate': 'M07-form-quote',
    'fix.sales.activity': 'M07-form-activity',
    'fix.account': 'M07-form-account',
    'fix.lead.qualification': 'M07-form-qualification',
    'fix.opportunity.team': 'M07-form-opp-team',
    'fix.sales.quota': 'M07-form-quota',
    'fix.account.eligibility': 'M07-form-eligibility'
  },
  'M07:__by_screen__': {
    'M07-sequences': 'M07-form-sequence',
    'M07-score-models': 'M07-form-score-model',
    'M07-kanban': 'M07-form-opp',
    'M07-leads': 'M07-form-lead',
    'M07-opps': 'M07-form-opp',
    'M07-form-opp': 'M07-form-opp',
    'M07-form-lead': 'M07-form-lead',
    'M07-activities': 'M07-form-activity',
    'M07-accounts': 'M07-form-assignment',
    'M07-key-accounts': 'M07-form-account',
    'M07-plans': 'M07-form-plan',
    'M07-qbr': 'M07-form-qbr',
    'M07-renewals': 'M07-form-renewal',
    'M07-scoring': 'M07-form-pipeline',
    'M07-forecast': 'M07-form-forecast',
    'M07-quotes': 'M07-form-quote',
    'M07-qualifications': 'M07-form-qualification',
    'M07-opp-team': 'M07-form-opp-team',
    'M07-quotas': 'M07-form-quota',
    'M07-eligibility': 'M07-form-eligibility'
  }
};

export const FORM_MODELS = {
  'M07:Lead Scoring Model': 'fix.crm.score.model',
  'M07:Sequence / Playbook': 'fix.crm.sequence',
  'M07:Lead': 'crm.lead',
  'M07:Opportunity': 'crm.lead',
  'M07:Activity (call/visit/meeting)': 'fix.sales.activity',
  'M07:Account Plan': 'fix.account.plan',
  'M07:Pipeline Configuration': 'fix.pipeline',
  'M07:Account Assignment': 'fix.account.assignment',
  'M07:Quarterly Business Review': 'fix.qbr',
  'M07:Renewal Pursuit': 'fix.renewal',
  'M07:Forecast Snapshot': 'fix.forecast.snapshot',
  'M07:Opportunity Estimate': 'fix.estimate',
  'M07:Key Account & Stakeholders': 'fix.account',
  'M07:Competitor Intelligence': 'crm.lead',
  'M07:Lead Qualification': 'fix.lead.qualification',
  'M07:Opportunity Team': 'fix.opportunity.team',
  'M07:Sales Quota': 'fix.sales.quota',
  'M07:Dedicated-Manager Eligibility Criteria': 'fix.account.eligibility'
};

export const CREATE = {
  M07: { screen: 'M07-form-opp', model: 'crm.lead', label: 'Opportunity' }
};
