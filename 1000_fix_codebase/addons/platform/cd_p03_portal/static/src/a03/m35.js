/** @odoo-module **/
/* A03 · Customer Experience — M35 Marketing Campaigns (v2 rebuild).
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 4 forms / freg 58.
 * Campaigns and responses are real (fix.campaign); journeys, triggers,
 * offers, creatives, portal ads and experiments are new fix.campaign.* records.
 * Attributed revenue is a declared gap — never estimated. */

export const MODULE = {
  area: 'A03', code: 'M35', en: 'Marketing Campaigns', title: 'M35 · Marketing Campaigns',
  bn: 'মার্কেটিং ক্যাম্পেইন', icon: '📣',
  desc: 'Campaign planning and PDPA-safe approval, journeys and behaviour triggers, offers, creatives, portal ads, A/B experiments and attribution.',
  kpis: [
    { l: 'Active Campaigns', m: 'active_campaigns' },
    { l: 'Leads MTD', m: 'leads_mtd' },
    { l: 'CAC', m: 'cac', prefix: 'BDT ' },
    { l: 'Attributed Revenue', m: 'attributed_revenue', prefix: 'BDT ' },
    { l: 'Open Rate', m: 'open_rate', suffix: '%' },
    { l: 'Consent-Safe Reach', m: 'consent_safe_reach' }
  ],
  groups: [
    { en: 'Campaigns', screens: [
      { id: 'M35-campaigns', en: 'Campaign Manager', bn: 'ক্যাম্পেইন ম্যানেজার', t: 'g' },
      { id: 'M35-form-campaign', en: 'Campaign Form', bn: 'ক্যাম্পেইন ফর্ম', t: 'f' },
      { id: 'M35-approval', en: 'Planning & Approval', bn: 'পরিকল্পনা ও অনুমোদন', t: 'r' },
      { id: 'M35-audience', en: 'Campaign Audiences', bn: 'ক্যাম্পেইন অডিয়েন্স', t: 'g' },
      { id: 'M35-comarketing', en: 'Co-Marketing Campaigns', bn: 'কো-মার্কেটিং ক্যাম্পেইন', t: 'g' }
    ]},
    { en: 'Journeys', screens: [
      { id: 'M35-journeys', en: 'Journey Orchestration', bn: 'জার্নি অর্কেস্ট্রেশন', t: 'g' },
      { id: 'M35-triggers', en: 'Behaviour Triggers', bn: 'আচরণ ট্রিগার', t: 'g' }
    ]},
    { en: 'Offers & Content', screens: [
      { id: 'M35-offers', en: 'Offer Selection', bn: 'অফার নির্বাচন', t: 'g' },
      { id: 'M35-content', en: 'Creative Library', bn: 'ক্রিয়েটিভ লাইব্রেরি', t: 'g' },
      { id: 'M35-ads', en: 'Portal Ad Placement', bn: 'পোর্টাল বিজ্ঞাপন', t: 'g' }
    ]},
    { en: 'Measurement', screens: [
      { id: 'M35-ab', en: 'A/B & Holdout', bn: 'এ/বি পরীক্ষা', t: 'g' },
      { id: 'M35-spend', en: 'Campaign Spend', bn: 'ক্যাম্পেইন ব্যয়', t: 'g' },
      { id: 'M35-attribution-models', en: 'Attribution Models', bn: 'অ্যাট্রিবিউশন মডেল', t: 'g' },
      { id: 'M35-attribution', en: 'Attribution Model', bn: 'অ্যাট্রিবিউশন', t: 'r' },
      { id: 'M35-roi', en: 'Budget & ROI', bn: 'বাজেট ও ROI', t: 'r' }
    ]},
    { en: 'Journey Runtime (S10)', bn: 'জার্নি রানটাইম', screens: [
      { id: 'M35-journey-members', en: 'Journey Members', bn: 'জার্নি সদস্য', t: 'g' }
    ]},
    { en: 'Multi-Touch Attribution', bn: 'মাল্টি-টাচ অ্যাট্রিবিউশন', screens: [
      { id: 'M35-touches', en: 'Touchpoint Ledger', bn: 'টাচপয়েন্ট লেজার', t: 'g' }
    ]}
  ],
  reports: ['Campaign Funnel by Channel', 'Attribution & ROI', 'Seasonal Template Performance', 'Co-Marketing Partner Report', 'Lead-to-Order Conversion'],
  forms: ['Campaign', 'Journey (multi-step)', 'Offer', 'Creative Asset',
    'Define Campaign Audience', 'Behaviour Trigger', 'A/B Experiment', 'Conclude an Experiment',
    'Campaign Spend', 'Void a Spend', 'Attribution Model', 'Portal Ad Placement',
    'Co-Marketing Partners', 'MDF Co-Funding'],
  cross: ['M33 Customer Master', 'M10 Loyalty', 'M34 CX Feedback', 'M40 Partner & Channel'],
  /* Capture audit 2026-11-14: each page's "+ New" captures the record the
   * page names (spec section 5 FR-MKT-001..040, section 10.1). Pages 2 and 8
   * offered "+ New Campaign"; page 6 offered nothing. */
  freg: { src: 58, sub: [
    ['1', 'Campaign Planning & Approval', 8, { model: 'fix.campaign', cols: ['name', 'state', 'dofa_tier_required', 'dofa_approved', 'dofa_approved_by', 'dofa_approved_at'], screens: ['M35-campaigns', 'M35-approval'], reports: ['Campaign Funnel by Channel'], forms: ['Campaign'] }],
    /* 2 (FR-MKT-009..014, BRU-MKT-02/03/14): the audience is composed from
     * governed M33 segments with a holdout, and estimated after suppression. */
    ['2', 'Audience from Segments', 6, { model: 'fix.campaign', cols: ['name', 'target_audience_type', 'segment_names', 'holdout_pct', 'estimated_reach', 'estimated_at', 'state'], screens: ['M35-audience', 'M35-campaigns'], reports: [], forms: ['Define Campaign Audience'], create: 'M35-form-audience' }],
    ['3', 'Journey Orchestration', 10, { model: 'fix.campaign.journey', cols: ['name', 'state', 'active', 'campaign_id', 'trigger_event', 'steps_json'], screens: ['M35-journeys', 'M35-triggers', 'M35-journey-members'], reports: [], forms: ['Journey (multi-step)', 'Behaviour Trigger'] }],
    ['4', 'Content & Offers', 8, { model: 'fix.campaign.creative', cols: ['name', 'state', 'campaign_id', 'asset_type', 'channel', 'reference'], screens: ['M35-content', 'M35-offers'], reports: ['Seasonal Template Performance'], forms: ['Creative Asset', 'Offer'] }],
    /* 5 (FR-MKT-031): an experiment is designed, started and concluded with a winner. */
    ['5', 'Experimentation', 7, { model: 'fix.campaign.experiment', cols: ['name', 'state', 'campaign_id', 'variable', 'variant_a_pct', 'metric', 'winner'], screens: ['M35-ab'], reports: [], forms: ['A/B Experiment', 'Conclude an Experiment'] }],
    /* 6 (FR-MKT-032..037, BRU-MKT-11/12): spend booked outside the estate is
     * recorded against the budget; the attribution model is a versioned record. */
    ['6', 'Budget & Attribution', 8, { model: 'fix.campaign.spend', cols: ['spend_date', 'campaign_id', 'name', 'category', 'amount', 'reference', 'state'], screens: ['M35-spend', 'M35-attribution-models', 'M35-attribution', 'M35-roi', 'M35-rpt-roi', 'M35-touches'], reports: ['Attribution & ROI', 'Lead-to-Order Conversion'], forms: ['Campaign Spend', 'Void a Spend', 'Attribution Model'] }],
    ['7', 'Portal Advertising', 5, { model: 'fix.campaign.ad', cols: ['name', 'active', 'campaign_id', 'placement', 'advertiser_partner_id', 'active_from', 'active_to', 'impressions', 'clicks'], screens: ['M35-ads'], reports: [], forms: ['Portal Ad Placement'] }],
    /* 8 (scope item 14): a co-marketing campaign names its M40 partners;
     * their MDF accrual is how the partner co-funds it. */
    ['8', 'Co-Marketing', 6, { model: 'fix.campaign', cols: ['name', 'comarketing_partner_names', 'channel', 'budget', 'start_date', 'state'], screens: ['M35-comarketing', 'M35-mdf', 'M35-rpt-co'], reports: ['Co-Marketing Partner Report'], forms: ['Co-Marketing Partners', 'MDF Co-Funding'], create: 'M35-form-comarketing' }]
  ] }
};

export const SCREENS = {
  'M35-campaigns': { kind: 'model_list', model: 'fix.campaign', stateField: 'state',
    cols: ['name', 'channel', 'target_audience_type', 'budget', 'approval_state', 'dnd_scrubbed_at', 'creative_unapproved_count', 'response_count', 'recipient_count', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Budget Approval', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_scrub_dnd', l: 'Run BTRC DND Scrub' },
      { m: 'action_launch', l: 'Launch Campaign' },
      { m: 'action_pause', l: 'Pause' },
      { m: 'action_resume', l: 'Resume' },
      { m: 'action_complete', l: 'Mark Completed' }
    ] },
  'M35-approval': { kind: 'table_report', module: 'M35', report: 'campaign_approval', title: 'Planning & Approval', period: false },
  'M35-journeys': { kind: 'model_list', model: 'fix.campaign.journey', stateField: 'state',
    cols: ['name', 'campaign_id', 'journey_kind', 'step_count', 'member_active_count', 'state', 'paused_by_campaign', 'active'],
    actions: [
      { m: 'action_activate', l: 'Activate Journey' },
      { m: 'action_pause_journey', l: 'Pause Journey' },
      { m: 'action_resume_journey', l: 'Resume Journey' }
    ],
    note: 'A journey runs only under a running campaign. Launching a campaign activates its journeys that have steps; pausing it pauses them.' },
  'M35-triggers': { kind: 'model_list', model: 'fix.campaign.trigger', stateField: 'active',
    cols: ['name', 'campaign_id', 'event', 'outbox_event_type', 'consumer_registered', 'producer_missing', 'delay_hours', 'active'] },
  'M35-offers': { kind: 'model_list', model: 'fix.campaign.offer', stateField: 'active',
    cols: ['name', 'campaign_id', 'offer_type', 'value', 'valid_from', 'valid_until', 'active'] },
  'M35-content': { kind: 'model_list', model: 'fix.campaign.creative', stateField: 'state',
    cols: ['name', 'campaign_id', 'asset_type', 'channel', 'reference', 'approval_state', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Content Approval', ask: 'What should the approver check?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_withdraw', l: 'Withdraw for Editing' },
      { m: 'action_retire', l: 'Retire' },
      { m: 'action_reset_to_draft', l: 'Back to Draft' }
    ],
    note: 'Content is approved from the approver\'s inbox (M63). An approved creative must be withdrawn before it is edited, and every live creative must be approved before the campaign launches.' },
  'M35-ads': { kind: 'model_list', model: 'fix.campaign.ad', stateField: 'active',
    cols: ['name', 'campaign_id', 'placement', 'advertiser_partner_id', 'active_from', 'active_to', 'active', 'impressions', 'clicks'] },
  'M35-ab': { kind: 'model_list', model: 'fix.campaign.experiment', stateField: 'state',
    cols: ['name', 'campaign_id', 'variable', 'variant_a_pct', 'metric', 'state', 'winner', 'result_note'],
    actions: [
      { m: 'action_start', l: 'Start Experiment' }
    ],
    note: 'An experiment is designed in draft, started here, and concluded with its winner and the figures it was judged on (Conclude an Experiment). A started experiment\'s design is fixed.' },

  /* ============ CAPTURE AUDIT 2026-11-14 ============ */
  'M35-audience': { kind: 'model_list', model: 'fix.campaign', stateField: 'state', create: false,
    cols: ['name', 'channel', 'target_audience_type', 'segment_names', 'exclude_segment_names', 'holdout_pct', 'estimated_reach', 'estimated_at', 'holdout_count', 'state'],
    actions: [
      { m: 'action_estimate_audience', l: 'Estimate Reach' }
    ],
    note: 'The audience comes from governed customer segments, never from an uploaded list. Estimate Reach shows the approver how many people the campaign would actually reach once consent, the Do-Not-Disturb registry and the holdout are applied. Requesting budget approval refreshes it.' },
  'M35-comarketing': { kind: 'model_list', model: 'fix.campaign', stateField: 'state', create: false,
    domain: [['partner_ids', '!=', false]],
    cols: ['name', 'comarketing_partner_names', 'channel', 'budget', 'start_date', 'state'],
    empty: 'No campaign names a co-marketing partner yet: use Co-Marketing Partners to name one.',
    note: 'Campaigns run with channel partners. A partner co-funds a campaign through a market development fund accrual that names the campaign.' },
  'M35-mdf': { kind: 'model_list', model: 'fix.partner.rebate', stateField: 'state', create: false,
    domain: [['kind', '=', 'mdf'], ['campaign_id', '!=', false]],
    cols: ['name', 'partner_id', 'campaign_id', 'period', 'amount', 'state'],
    empty: 'No partner co-funds a campaign yet.' },
  'M35-spend': { kind: 'model_list', model: 'fix.campaign.spend', stateField: 'state',
    cols: ['spend_date', 'campaign_id', 'name', 'category', 'amount', 'vendor_partner_id', 'reference', 'state'],
    note: 'Spend booked outside the estate: media, print, events, agency fees. Message cost and offer discounts are already counted from the estate\'s own records. A spend that would take a campaign past its approved budget is refused until the raised budget is approved again.' },
  'M35-attribution-models': { kind: 'model_list', model: 'fix.attribution.model', stateField: 'state',
    cols: ['code', 'version', 'name', 'method', 'lookback_days', 'state', 'effective_from', 'activated_by_id'],
    actions: [
      { m: 'action_activate', l: 'Put In Force' }
    ],
    note: 'One model is in force at a time. A model that was in force is never edited: a change is a new version. A campaign keeps the model that was in force when it completed, so a later model does not restate it.' },
  'M35-attribution': { kind: 'table_report', module: 'M35', report: 'attribution_roi', title: 'Attribution Model', period: false },
  'M35-roi': { kind: 'table_report', module: 'M35', report: 'budget_roi', title: 'Budget & ROI', period: false },

  /* Report chips -> their own computed pack */
  'M35-rpt-funnel': { kind: 'table_report', module: 'M35', report: 'campaign_funnel', title: 'Campaign Funnel by Channel', period: false },
  'M35-rpt-roi': { kind: 'table_report', module: 'M35', report: 'attribution_roi', title: 'Attribution & ROI', period: false },
  'M35-rpt-seasonal': { kind: 'table_report', module: 'M35', report: 'seasonal_performance', title: 'Seasonal Template Performance', period: false },
  'M35-rpt-co': { kind: 'table_report', module: 'M35', report: 'co_marketing_partner', title: 'Co-Marketing Partner Report', period: false },
  'M35-rpt-lead': { kind: 'table_report', module: 'M35', report: 'lead_to_order', title: 'Lead-to-Order Conversion', period: false },

  /* ============ D365 IN-WORKSPACE MULTI-TAB FORMS ============ */
  'M35-form-campaign': {
    lines: {
      field: 'response_ids',
      title: 'Campaign Responses',
      note: 'Who responded, how, and whether it converted.',
      fields: [
        { name: 'partner_id', label: 'Lead / Customer', required: true },
        { name: 'response_type', label: 'Response', required: true },
        { name: 'conversion_status', label: 'Converted' },
        { name: 'loyalty_points_awarded', label: 'Bonus Points' },
        { name: 'responded_at', label: 'At' }
      ]
    }, kind: 'model_form', model: 'fix.campaign',
    title: 'Marketing Campaign & Customer Engagement Master', back: 'M35-campaigns',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Campaign Definition', bn: '১. ক্যাম্পেইন শিরোনাম', icon: '📢', badge: '6' },
      { id: 'budget', label: '2. Budget & DOFA Memo', bn: '২. বাজেট ও ডোফা', icon: '💰', badge: '10' },
      { id: 'audience', label: '3. Audience Segmentation', bn: '৩. অডিয়েন্স সেগমেন্ট', icon: '👥', badge: '9' },
      { id: 'compliance', label: '4. BTRC Curfew & PDPA', bn: '৪. কমপ্লায়েন্স ও কার্ফিউ', icon: '🛡️', badge: '4' },
      { id: 'docs', label: '5. Creative Assets & Approvals', bn: '৫. ক্রিয়েটিভ সম্পদ ও অনুমোদন', icon: '🎨', badge: '8' },
      { id: 'attribution', label: '6. Attribution & ROI', bn: '৬. অ্যাট্রিবিউশন ও আরওআই', icon: '📈', badge: '6' },
      { id: 'audit', label: '7. System Governance', bn: '৭. অডিট ট্রেইল', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Campaign Identification & Broadcast Channel', fields: [
        { name: 'name', required: true, label: 'Campaign Title (English)' },
        { name: 'name_bn', label: 'Campaign Title (Bengali Bangla)' },
        { name: 'channel', required: true, label: 'Primary Delivery Channel (SMS / Email / Push / Social)' },
        { name: 'state', label: 'Campaign Lifecycle State', readonly: true },
        { name: 'operating_unit_id', label: 'Operating Business Unit' },
        { name: 'company_id', label: 'Operating Legal Entity' },
      ]},
      { tab: 'budget', title: 'Financial Budget & DOFA Governance Gating (FLAW-35.1)',
        note: 'Campaign budget releases mandate a documented Finance internal memo reference and DOFA executive sign-off before campaign activation.',
        fields: [
          { name: 'budget', required: true, label: 'Allocated Campaign Budget (BDT)' },
          { name: 'budget_memo_ref', required: true, label: 'Internal Finance Memo Reference' },
          { name: 'budget_approved', label: 'DOFA Executive Budget Approval Confirmed', readonly: true },
          { name: 'approval_state', label: 'Budget Approval Request (M63)', readonly: true },
          { name: 'budget_approver_id', label: 'Authorized DOFA Executive Signoff', readonly: true },
          { name: 'budget_approval_date', label: 'DOFA Budget Approval Date', readonly: true },
          { name: 'currency_id', label: 'Budget Currency', readonly: true },
          { name: 'actual_spend', label: 'Recorded Actual Spend (BDT)', readonly: true },
          { name: 'budget_variance', label: 'Budget Remaining (BDT)', readonly: true },
          { name: 'budget_utilisation_pct', label: 'Budget Used (%)', readonly: true },
      ]},
      { tab: 'audience', title: 'Audience From Governed Segments',
        note: 'Audiences come from governed customer segments (BRU-MKT-02): no list is uploaded and no filter is typed. The holdout receives nothing, so what the campaign caused can be measured.',
        fields: [
        { name: 'target_audience_type', required: true, label: 'Audience',
          choices: [['segments', 'Governed M33 Segments'], ['all_customers', 'All Registered Customers']] },
        { name: 'segment_ids', label: 'Include Segments' },
        { name: 'exclude_segment_ids', label: 'Exclude Segments' },
        { name: 'holdout_pct', label: 'Holdout (% kept back for measurement)' },
        { name: 'holdout_key', label: 'Holdout Key (shared across an experiment)' },
        { name: 'estimated_reach', label: 'Estimated Reach (after suppression)', readonly: true },
        { name: 'estimate_breakdown', label: 'How The Estimate Was Reached', readonly: true },
        { name: 'recipient_count', label: 'Recipients At Launch', readonly: true },
        { name: 'holdout_count', label: 'Held Out At Launch', readonly: true },
      ]},
      { tab: 'compliance', title: 'BTRC Telecom Curfew & PDPA Consent Verification (FLAW-35.2)',
        note: 'BTRC Telecommunication Directive: outbound marketing is restricted to 08:00 to 22:00 BST. Run the DND scrub (Campaign Manager) within 24 hours of launch; parties on the DND registry are removed from the recipients at launch and are never enrolled in a journey.',
        fields: [
          { name: 'pdpa_consent_verified', label: 'Statutory PDPA Consent Verification Completed', readonly: true },
          { name: 'excluded_no_consent_count', label: 'Excluded For No Consent', readonly: true },
          { name: 'start_date', required: true, label: 'Campaign Scheduled Start Date' },
          { name: 'end_date', required: true, label: 'Campaign Scheduled End Date' },
      ]},
      { tab: 'docs', title: 'Creative Assets, NOC & Approval Evidence', 
        note: 'Creative banners, BTRC NOC letters and the CFO budget-approval memo are fix.campaign.creative records (see the Creative Assets grid) plus budget_memo_ref on the Budget tab. The checksummed repository (fix.document, M24 — SHA-256) is the estate-wide asset path; a direct campaign→document relation is a declared platform gap.',
        fields: [
          { name: 'recipient_ids', label: 'Associated Campaign Audience Records', readonly: true },
          { name: 'btrc_sender_mask', label: 'BTRC Approved Sender ID Mask' },
          { name: 'sms_opt_out_text', label: 'Mandatory Opt-Out Instruction' },
          { name: 'dnd_scrubbed_at', label: 'DND Registry Scrubbed At', readonly: true },
          { name: 'dnd_excluded_count', label: 'Recipients Excluded by BTRC DND', readonly: true },
          { name: 'dnd_excluded_partner_ids', label: 'Parties Excluded by BTRC DND', readonly: true },
          { name: 'creative_unapproved_count', label: 'Creatives Not Yet Approved', readonly: true },
      ]},
      { tab: 'attribution', title: 'Marketing Attribution & Customer Acquisition Economics', fields: [
        { name: 'utm_source', label: 'UTM Tracking Source' },
        { name: 'utm_medium', label: 'UTM Tracking Medium' },
        { name: 'utm_campaign', label: 'UTM Tracking Campaign Name' },
        { name: 'response_count', label: 'Total Inbound Customer Responses', readonly: true },
        { name: 'cost_per_response', label: 'Effective Cost per Response (BDT)', readonly: true },
        { name: 'attribution_model_id', label: 'Attribution Model (pinned at completion)', readonly: true },
      ]},
      { tab: 'audit', title: 'System Governance & Response Trace', fields: [
        { name: 'response_ids', label: 'Converted Customer Response Trace', readonly: true },
        { name: 'create_date', label: 'Campaign Creation Timestamp', readonly: true },
        { name: 'write_date', label: 'Last Campaign Update Timestamp', readonly: true },
      ]}
    ] },

  'M35-form-journey': {
    lines: {
      field: 'step_ids',
      title: 'Journey Steps',
      note: 'Executed in sequence order by the S10 runtime. Membership and consent are re-evaluated before EVERY step, so a party who withdraws consent after step 1 does not receive step 3.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'name', label: 'Step', required: true },
        { name: 'step_type', label: 'Type', required: true },
        { name: 'wait_minutes', label: 'Wait Before (min)' },
        { name: 'channel', label: 'Channel' },
        { name: 'purpose', label: 'Purpose (from the template)', readonly: true },
        { name: 'template_id', label: 'Template' },
        { name: 'segment_id', label: 'Segment' },
        { name: 'event_type', label: 'Event Type' },
        { name: 'condition_kind', label: 'Branch Condition' },
        { name: 'true_step_id', label: 'If True' },
        { name: 'false_step_id', label: 'If False' },
        { name: 'active', label: 'Active' }
      ]
    },
    kind: 'model_form',
    model: 'fix.campaign.journey',
    title: 'Customer Journey',
    back: 'M35-journeys',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', paused: 'Paused' } },
    tabs: [
      { id: 'general', label: '1. Journey Definition', bn: '১. জার্নি বিবরণ', icon: '🗺️' },
      { id: 'kind', label: '2. Kind & Audience', bn: '২. ধরন ও অডিয়েন্স', icon: '🎯' },
      { id: 'steps', label: '3. Steps & Automation', bn: '৩. ধাপ ও অটোমেশন', icon: '⚙️' },
      { id: 'audit', label: '4. State & Members', bn: '৪. অবস্থা ও সদস্য', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Journey Identity',
        note: 'An automated multi-step customer lifecycle workflow. A journey only runs under a RUNNING campaign, so the campaign budget DOFA and BTRC launch gates apply to everything it sends.',
        fields: [
          { name: 'name', required: true, label: 'Journey Name' },
          { name: 'campaign_id', required: true, label: 'Associated Campaign' },
          { name: 'trigger_event', label: 'Legacy Trigger Event (free text)' }
        ]
      },
      {
        tab: 'kind',
        title: 'Which Kind Of Journey',
        note: 'A SEGMENT-BASED journey enumerates its audience at launch; a TRIGGER-BASED one admits one member per event and must be idempotent; a CAMPAIGN-AUDIENCE one enrols the recipients the campaign launch resolved (consented and DND-scrubbed). The constraint refuses a journey whose kind has no starter, because it would silently enrol nobody.',
        fields: [
          { name: 'journey_kind', required: true, label: 'Journey Kind' },
          { name: 'segment_id', label: 'Audience Segment (segment-based)' },
          { name: 'trigger_id', label: 'Starting Trigger (trigger-based)' },
          { name: 'live_segment_sync', label: 'Apply Segment Changes Live' },
          { name: 'exit_on_consent_withdrawal', label: 'Exit On Consent Withdrawal' }
        ]
      },
      {
        tab: 'steps',
        title: 'Orchestration Steps',
        note: 'The steps grid below is the definition the runtime executes. steps_json is the pre-runtime config field and is kept for records authored before the executor existed.',
        fields: [
          { name: 'step_count', label: 'Steps', readonly: true },
          { name: 'steps_json', label: 'Legacy Steps Definition (JSON)', type: 'text' }
        ]
      },
      {
        tab: 'audit',
        title: 'Journey State & Membership',
        fields: [
          { name: 'state', required: true, label: 'Execution State', readonly: true },
          { name: 'paused_by_campaign', label: 'Paused With Its Campaign', readonly: true },
          { name: 'launched_at', label: 'Activated At', readonly: true },
          { name: 'member_active_count', label: 'Active Members', readonly: true },
          { name: 'member_completed_count', label: 'Completed', readonly: true },
          { name: 'member_exited_count', label: 'Exited / Failed', readonly: true },
          { name: 'active', label: 'Active Status' }
        ]
      }
    ]
  },

  'M35-form-offer': {
    kind: 'model_form',
    model: 'fix.campaign.offer',
    title: 'Marketing Offer',
    back: 'M35-offers',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'general', label: 'Offer Definition', bn: 'অফার বিবরণ', icon: '🏷️' },
      { id: 'discount', label: 'Discount & Promo Code', bn: 'ছাড় ও প্রমো কোড', icon: '🎟️' },
      { id: 'budget', label: 'Budget Cap & Fraud Control', bn: 'বাজেট সীমা ও নিয়ন্ত্রণ', icon: '🛡️' },
      { id: 'validity', label: 'Validity & Status', bn: 'মেয়াদ ও অবস্থা', icon: '📅' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Offer Identity',
        note: 'Promotional discount structure bound to a marketing campaign.',
        fields: [
          { name: 'name', required: true, label: 'Offer Name' },
          { name: 'campaign_id', required: true, label: 'Parent Campaign' }
        ]
      },
      {
        tab: 'discount',
        title: 'Discount Terms & Promo Code',
        note: 'Customer-facing discount values and promo code for storefront/portal checkout.',
        fields: [
          { name: 'offer_type', required: true, label: 'Discount Type' },
          { name: 'value', label: 'Discount Value (% or BDT)' },
          { name: 'promo_code', label: 'Promotional Code (FLAW-35.3)' }
        ]
      },
      {
        tab: 'budget',
        title: 'Budget Caps & Multi-Account Fraud Prevention',
        note: 'Prevents promo code abuse and budget runaway spend across portals (HS-08).',
        fields: [
          { name: 'max_redemptions_per_customer', label: 'Max Redemptions Per Customer' },
          { name: 'total_budget_cap_bdt', label: 'Total Budget Cap (BDT)' },
          { name: 'total_redeemed_bdt', readonly: true, label: 'Total Redeemed Value (BDT)' },
          { name: 'redemption_count', readonly: true, label: 'Total Redemptions Completed' }
        ]
      },
      {
        tab: 'validity',
        title: 'Validity Window & Status',
        fields: [
          { name: 'valid_from', label: 'Valid From Date' },
          { name: 'valid_until', label: 'Valid Until Date' },
          { name: 'active', label: 'Active Status' }
        ]
      }
    ]
  },

  'M35-form-creative': {
    kind: 'model_form',
    model: 'fix.campaign.creative',
    title: 'Creative Asset',
    back: 'M35-content',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', retired: 'Retired' } },
    tabs: [
      { id: 'general', label: 'Asset Identification', bn: 'অ্যাসেট পরিচয়', icon: '🎨' },
      { id: 'storage', label: 'Asset Reference', bn: 'স্টোরেজ রেফারেন্স', icon: '🔗' },
      { id: 'governance', label: 'Approval & State', bn: 'অনুমোদন ও অবস্থা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Creative Asset Identity',
        note: 'Brand-compliant creative asset for campaign channels.',
        fields: [
          { name: 'name', required: true, label: 'Asset Name' },
          { name: 'campaign_id', required: true, label: 'Campaign' },
          { name: 'asset_type', required: true, label: 'Asset Type' },
          { name: 'channel', label: 'Target Channel' }
        ]
      },
      {
        tab: 'storage',
        title: 'Storage & Location',
        note: 'Exact reference key in digital asset management or Cloudflare R2 / S3 storage.',
        fields: [
          { name: 'reference', label: 'Asset Reference (S3 Key / URL)' }
        ]
      },
      {
        tab: 'governance',
        title: 'Approval & Lifecycle',
        note: 'Request approval from the Creative Library. The approver decides from the M63 inbox; an approved creative is frozen until it is withdrawn.',
        fields: [
          { name: 'state', required: true, label: 'Content State', readonly: true },
          { name: 'approval_state', label: 'Approval Request', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'approved_at', label: 'Approved At', readonly: true }
        ]
      }
    ]
  },

  'M35-form-experiment': {
    kind: 'model_form',
    model: 'fix.campaign.experiment',
    title: 'A/B Experiment',
    back: 'M35-ab',
    status: { field: 'state', labels: { draft: 'Draft', running: 'Running', concluded: 'Concluded' } },
    tabs: [
      { id: 'general', label: 'Experiment Setup', bn: 'পরীক্ষা সেটআপ', icon: '🧪' },
      { id: 'metrics', label: 'Split & Primary Metric', bn: 'বিভাজন ও মেট্রিক', icon: '📊' },
      { id: 'outcome', label: 'Results & Conclusion', bn: 'ফলাফল ও নোট', icon: '🏆' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Experiment Setup',
        note: 'Statistically controlled A/B split on content, offer, channel or timing variants. The design is fixed once the experiment starts.',
        fields: [
          { name: 'name', required: true, label: 'Experiment Name' },
          { name: 'campaign_id', required: true, label: 'Campaign' },
          { name: 'variable', required: true, label: 'What Is Tested' },
          { name: 'variant_a_label', label: 'Variant A' },
          { name: 'variant_b_label', label: 'Variant B' }
        ]
      },
      {
        tab: 'metrics',
        title: 'Audience Split & Metric',
        fields: [
          { name: 'variant_a_pct', required: true, label: 'Variant A Split %' },
          { name: 'metric', required: true, label: 'Primary Optimization Metric' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Results & Determination',
        note: 'Start the experiment from A/B & Holdout; conclude it with Conclude an Experiment. The state and the winner are never typed.',
        fields: [
          { name: 'state', label: 'Lifecycle State', readonly: true },
          { name: 'started_at', label: 'Started At', readonly: true },
          { name: 'winner', label: 'Winner', readonly: true },
          { name: 'result_note', label: 'Experiment Finding', readonly: true },
          { name: 'concluded_by_id', label: 'Concluded By', readonly: true },
          { name: 'concluded_at', label: 'Concluded At', readonly: true }
        ]
      }
    ]
  },

  'M35-form-trigger': {
    kind: 'model_form',
    model: 'fix.campaign.trigger',
    title: 'Behaviour Trigger',
    back: 'M35-triggers',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'general', label: 'Trigger Definition', bn: 'ট্রিগার বিবরণ', icon: '⚡' },
      { id: 'timing', label: 'Event & Delay', bn: 'ইভেন্ট ও সময়', icon: '⏱️' },
      { id: 'audit', label: 'Status & Governance', bn: 'অবস্থা ও পরিচালনা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Trigger Configuration',
        note: 'Automated behavioural event trigger initiating customer lifecycle outreach.',
        fields: [
          { name: 'name', required: true, label: 'Trigger Name' },
          { name: 'campaign_id', required: true, label: 'Campaign' }
        ]
      },
      {
        tab: 'timing',
        title: 'Event & Delay Schedule',
        fields: [
          { name: 'event', required: true, label: 'Triggering Event' },
          { name: 'delay_hours', required: true, label: 'Delay Window (Hours)' }
        ]
      },
      {
        tab: 'audit',
        title: 'Active Governance',
        fields: [
          { name: 'active', label: 'Active Status' }
        ]
      }
    ]
  },

  'M35-form-ad': {
    kind: 'model_form',
    model: 'fix.campaign.ad',
    title: 'Portal Ad Placement',
    back: 'M35-ads',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'general', label: 'Ad Placement', bn: 'বিজ্ঞাপন বিবরণ', icon: '🖼️' },
      { id: 'telemetry', label: 'Impressions & Clicks', bn: 'টেলিমেট্রি ও ফলাফল', icon: '📈' },
      { id: 'audit', label: 'Status & Governance', bn: 'অবস্থা ও পরিচালনা', icon: '📋' }
    ],
    sections: [
      {
        tab: 'general',
        title: 'Portal Ad Placement',
        note: 'In-portal contextual promotional banner displayed across customer and partner portals.',
        fields: [
          { name: 'name', required: true, label: 'Banner Name' },
          { name: 'campaign_id', required: true, label: 'Associated Campaign' },
          { name: 'placement', required: true, label: 'Portal Placement Location' },
          { name: 'advertiser_partner_id', label: 'Advertiser (empty for the Company\'s own promotion)' },
          { name: 'active_from', label: 'Runs From' },
          { name: 'active_to', label: 'Runs Until' }
        ]
      },
      {
        tab: 'telemetry',
        title: 'Telemetry & Engagement',
        note: 'Audited impression and click-through counts recorded from portal frontend activity.',
        fields: [
          { name: 'impressions', readonly: true, label: 'Total Impressions' },
          { name: 'clicks', readonly: true, label: 'Total Clicks' }
        ]
      },
      {
        tab: 'audit',
        title: 'Status & State',
        fields: [
          { name: 'active', label: 'Active Status' }
        ]
      }
    ]
  },
  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M35-journey-members': { kind: 'model_list', model: 'fix.campaign.journey.member', create: false,
    cols: ['next_action_at', 'journey_id', 'partner_id', 'current_step_id', 'state', 'enrol_source', 'steps_executed', 'last_send_state'],
    stateField: 'state',
    actions: [
      { m: 'action_pause_member', l: 'Pause' },
      { m: 'action_resume_member', l: 'Resume' }
    ],
    note: 'Membership and consent are re-evaluated before every step, not trusted from the launch snapshot.' },
  'M35-form-journey-member': {
    kind: 'model_form', model: 'fix.campaign.journey.member',
    title: 'Journey Member', back: 'M35-journey-members',
    create: false, pick: 'A journey member is enrolled by the journey\'s trigger or audience: open one from Journey Members.',
    status: { field: 'state', labels: { active: 'Active', completed: 'Completed', exited: 'Exited', suppressed: 'Suppressed', failed: 'Failed' } },
    tabs: [
      { id: 'member', label: '1. Member', bn: '১. সদস্য', icon: '👤' },
      { id: 'progress', label: '2. Progress', bn: '২. অগ্রগতি', icon: '➡️' },
      { id: 'messages', label: '3. Messages Sent', bn: '৩. পাঠানো বার্তা', icon: '✉️' }
    ],
    sections: [
      {
        tab: 'member',
        title: 'Who And How They Joined',
        note: 'The enrolment key makes a trigger journey idempotent per member per event, so a replayed outbox event re-enrols nobody.',
        fields: [
        { name: 'journey_id', label: 'Journey', required: true },
        { name: 'partner_id', label: 'Party', required: true },
        { name: 'enrol_source', label: 'Joined Via', required: true, readonly: true },
        { name: 'source_event_id', label: 'Outbox Event', readonly: true },
        { name: 'enrol_key', label: 'Idempotency Key', readonly: true },
        { name: 'entered_at', label: 'Joined At', required: true, readonly: true }
        ]
      },
      {
        tab: 'progress',
        title: 'Where They Are',
        note: 'Membership and consent are re-evaluated before every step, not trusted from the launch-time snapshot.',
        fields: [
        { name: 'current_step_id', label: 'Current Step', readonly: true },
        { name: 'next_action_at', label: 'Next Action', readonly: true },
        { name: 'steps_executed', label: 'Steps Run', readonly: true },
        { name: 'state', label: 'State', required: true, readonly: true },
        { name: 'exited_at', label: 'Left At', readonly: true },
        { name: 'exit_reason', label: 'Why They Stopped', readonly: true }
        ]
      },
      {
        tab: 'messages',
        title: 'Delivery Rows',
        fields: [
        { name: 'delivery_ids', label: 'Messages', readonly: true },
        { name: 'last_send_state', label: 'Last Send Outcome', readonly: true }
        ]
      }
    ]
  },
  'M35-touches': { kind: 'model_list', model: 'fix.campaign.touch', create: false,
    cols: ['occurred_at', 'campaign_id', 'partner_id', 'touch_type', 'channel', 'value_bdt', 'value_known'],
    note: 'Harvested from the S1 delivery log. Only sent and delivered messages earn attribution credit.' },

  /* ==================================================================
   * CAPTURE AUDIT 2026-11-14 - the forms each sub-module page captures
   * ================================================================== */
  /* 2 Audience from Segments: a draft campaign's audience, composed from
   * governed segments (BRU-MKT-02) with a holdout (FR-MKT-014). */
  'M35-form-audience': {
    kind: 'model_form', model: 'fix.campaign',
    title: 'Define Campaign Audience', newLabel: 'Define Campaign Audience', back: 'M35-audience',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the draft campaign',
      note: 'An audience is set before launch: a running campaign keeps the audience it launched with.',
      search: 'Search campaign',
      choose: 'Define this audience',
      cols: ['name', 'channel', 'target_audience_type', 'start_date', 'state'],
      domain: [['state', '=', 'draft']],
      empty: 'No draft campaign: create the campaign first (Campaign Manager).'
    },
    sections: [
      { title: 'Step 2 of 2: Segments And Holdout',
        note: 'Every audience member comes from a governed customer segment. Consent, the Do-Not-Disturb registry and the holdout are applied when the reach is estimated and again at launch.',
        fields: [
        { name: 'name', label: 'Campaign', readonly: true },
        { name: 'channel', label: 'Channel', readonly: true },
        { name: 'target_audience_type', label: 'Audience', required: true,
          choices: [['segments', 'Governed M33 Segments'], ['all_customers', 'All Registered Customers']] },
        { name: 'segment_ids', label: 'Include Segments' },
        { name: 'exclude_segment_ids', label: 'Exclude Segments' },
        { name: 'holdout_pct', label: 'Holdout (% kept back for measurement, up to 50)' },
        { name: 'holdout_key', label: 'Holdout Key (campaigns sharing it share one holdout group)' },
        { name: 'estimated_reach', label: 'Estimated Reach (after suppression)', readonly: true },
        { name: 'estimate_breakdown', label: 'How The Estimate Was Reached', readonly: true }
      ]}
    ]
  },

  /* 5 Experimentation: the conclusion, with its winner (FR-MKT-031). */
  'M35-form-experiment-conclude': {
    kind: 'model_form', model: 'fix.campaign.experiment',
    title: 'Conclude an Experiment', newLabel: 'Conclude an Experiment', back: 'M35-ab',
    status: { field: 'state', labels: { draft: 'Draft', running: 'Running', concluded: 'Concluded' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the running experiment',
      search: 'Search experiment',
      choose: 'Conclude this experiment',
      cols: ['name', 'campaign_id', 'variable', 'variant_a_pct', 'metric', 'started_at'],
      domain: [['state', '=', 'running']],
      empty: 'No experiment is running: start one from A/B & Holdout.'
    },
    saveAction: { method: 'action_conclude', label: 'Conclude', done: 'Concluded: the winner is recorded', kwargs: { winner: 'winner', note: 'result_note' } },
    sections: [
      { title: 'Step 2 of 2: The Winner And Why',
        note: 'Name the winner only where the difference is significant; otherwise record that there was none.',
        fields: [
        { name: 'name', label: 'Experiment', readonly: true },
        { name: 'campaign_id', label: 'Campaign', readonly: true },
        { name: 'variable', label: 'What Was Tested', readonly: true },
        { name: 'variant_a_label', label: 'Variant A', readonly: true },
        { name: 'variant_b_label', label: 'Variant B', readonly: true },
        { name: 'metric', label: 'Judged On', readonly: true },
        { name: 'winner', label: 'Winner', required: true, readonly: true },
        { name: 'result_note', label: 'Finding (the figures the winner was judged on)', required: true, readonly: true }
      ]}
    ]
  },

  /* 6 Budget & Attribution: spend booked outside the estate (FR-MKT-033,
   * BRU-MKT-11). */
  'M35-form-spend': {
    kind: 'model_form', model: 'fix.campaign.spend',
    title: 'Campaign Spend', back: 'M35-spend',
    status: { field: 'state', labels: { recorded: 'Recorded', void: 'Void' } },
    sections: [
      { title: 'What Was Spent',
        note: 'A recorded spend is not edited: a wrong one is voided with a reason and recorded again. A spend that would take the campaign past its approved budget is refused.',
        fields: [
        { name: 'campaign_id', label: 'Campaign', required: true },
        { name: 'name', label: 'What Was Bought', required: true },
        { name: 'category', label: 'Category', required: true },
        { name: 'spend_date', label: 'Spend Date', required: true },
        { name: 'amount', label: 'Amount (BDT)', required: true },
        { name: 'vendor_partner_id', label: 'Supplier' },
        { name: 'reference', label: 'Invoice / PO Reference' }
      ]},
      { title: 'Status',
        fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'void_reason', label: 'Why It Was Voided', readonly: true },
        { name: 'voided_by_id', label: 'Voided By', readonly: true },
        { name: 'voided_at', label: 'Voided At', readonly: true }
      ]}
    ]
  },
  'M35-form-spend-void': {
    kind: 'model_form', model: 'fix.campaign.spend',
    title: 'Void a Spend', newLabel: 'Void a Spend', back: 'M35-spend',
    status: { field: 'state', labels: { recorded: 'Recorded', void: 'Void' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the recorded spend',
      search: 'Search spend',
      choose: 'Void this spend',
      cols: ['spend_date', 'campaign_id', 'name', 'amount', 'reference'],
      domain: [['state', '=', 'recorded']],
      empty: 'No recorded spend.'
    },
    saveAction: { method: 'action_void', label: 'Void Spend', done: 'Voided: it no longer counts against the budget', kwargs: { reason: 'void_reason' } },
    sections: [
      { title: 'Step 2 of 2: Say Why',
        fields: [
        { name: 'campaign_id', label: 'Campaign', readonly: true },
        { name: 'name', label: 'What Was Bought', readonly: true },
        { name: 'amount', label: 'Amount (BDT)', readonly: true },
        { name: 'reference', label: 'Invoice / PO Reference', readonly: true },
        { name: 'void_reason', label: 'Why It Is Voided', required: true, readonly: true }
      ]}
    ]
  },

  /* 6 Budget & Attribution: the versioned attribution model (BRU-MKT-12). */
  'M35-form-attribution-model': {
    kind: 'model_form', model: 'fix.attribution.model',
    title: 'Attribution Model', back: 'M35-attribution-models',
    status: { field: 'state', labels: { draft: 'Draft', active: 'In Force', superseded: 'Superseded' } },
    sections: [
      { title: 'How Credit Is Shared',
        note: 'Saved as a draft and put in force from Attribution Models. A new version of an existing code is a new record: a model that was in force is never changed.',
        fields: [
        { name: 'code', label: 'Code', required: true },
        { name: 'name', label: 'Name', required: true },
        { name: 'method', label: 'Method', required: true },
        { name: 'lookback_days', label: 'Lookback (days)', required: true },
        { name: 'rationale', label: 'Why This Model', type: 'text' }
      ]},
      { title: 'Version',
        fields: [
        { name: 'version', label: 'Version', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'effective_from', label: 'In Force From', readonly: true },
        { name: 'activated_by_id', label: 'Put In Force By', readonly: true }
      ]}
    ]
  },

  /* 8 Co-Marketing: the M40 partners a campaign runs with. */
  'M35-form-comarketing': {
    kind: 'model_form', model: 'fix.campaign',
    title: 'Co-Marketing Partners', newLabel: 'Name Co-Marketing Partners', back: 'M35-comarketing',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the campaign',
      search: 'Search campaign',
      choose: 'Name its partners',
      cols: ['name', 'channel', 'budget', 'start_date', 'state'],
      domain: [['state', '!=', 'completed']],
      empty: 'No open campaign: create the campaign first (Campaign Manager).'
    },
    sections: [
      { title: 'Step 2 of 2: The Partners',
        note: 'A Channel Officer names the partners, and only an onboarded partner co-markets. A partner whose fund accrual names the campaign stays on it until that accrual is cancelled.',
        fields: [
        { name: 'name', label: 'Campaign', readonly: true },
        { name: 'channel', label: 'Channel', readonly: true },
        { name: 'budget', label: 'Budget (BDT)', readonly: true },
        { name: 'partner_ids', label: 'Co-Marketing Partners' }
      ]}
    ]
  },
};

export const REPORT_ROUTES = {
  'M35:Campaign Funnel by Channel': 'M35-rpt-funnel',
  'M35:Attribution & ROI': 'M35-rpt-roi',
  'M35:Seasonal Template Performance': 'M35-rpt-seasonal',
  'M35:Co-Marketing Partner Report': 'M35-rpt-co',
  'M35:Lead-to-Order Conversion': 'M35-rpt-lead'
};

export const FORM_MODELS = {
  'M35:Journey Member': 'fix.campaign.journey.member',
  'M35:Campaign': 'fix.campaign',
  'M35:Journey (multi-step)': 'fix.campaign.journey',
  'M35:Offer': 'fix.campaign.offer',
  'M35:Creative Asset': 'fix.campaign.creative',
  'M35:Define Campaign Audience': 'fix.campaign',
  'M35:Behaviour Trigger': 'fix.campaign.trigger',
  'M35:A/B Experiment': 'fix.campaign.experiment',
  'M35:Conclude an Experiment': 'fix.campaign.experiment',
  'M35:Campaign Spend': 'fix.campaign.spend',
  'M35:Void a Spend': 'fix.campaign.spend',
  'M35:Attribution Model': 'fix.attribution.model',
  'M35:Portal Ad Placement': 'fix.campaign.ad',
  'M35:Co-Marketing Partners': 'fix.campaign',
  'M35:MDF Co-Funding': 'fix.partner.rebate'
};

export const FORM_CHIPS = {
  'M35:Journey Member': 'M35-form-journey-member',
  'M35:Campaign': 'M35-form-campaign',
  'M35:Journey (multi-step)': 'M35-form-journey',
  'M35:Offer': 'M35-form-offer',
  'M35:Creative Asset': 'M35-form-creative',
  'M35:Define Campaign Audience': 'M35-form-audience',
  'M35:Behaviour Trigger': 'M35-form-trigger',
  'M35:A/B Experiment': 'M35-form-experiment',
  'M35:Conclude an Experiment': 'M35-form-experiment-conclude',
  'M35:Campaign Spend': 'M35-form-spend',
  'M35:Void a Spend': 'M35-form-spend-void',
  'M35:Attribution Model': 'M35-form-attribution-model',
  'M35:Portal Ad Placement': 'M35-form-ad',
  'M35:Co-Marketing Partners': 'M35-form-comarketing',
  'M35:MDF Co-Funding': 'M40-form-rebate',
  'M35:__by_model__': {
    'fix.campaign.journey.member': 'M35-form-journey-member',
    'fix.campaign': 'M35-form-campaign',
    'fix.campaign.journey': 'M35-form-journey',
    'fix.campaign.trigger': 'M35-form-trigger',
    'fix.campaign.offer': 'M35-form-offer',
    'fix.campaign.creative': 'M35-form-creative',
    'fix.campaign.ad': 'M35-form-ad',
    'fix.campaign.experiment': 'M35-form-experiment',
    'fix.campaign.spend': 'M35-form-spend',
    'fix.attribution.model': 'M35-form-attribution-model',
    'fix.partner.rebate': 'M40-form-rebate'
  },
  'M35:__by_screen__': {
    'M35-journey-members': 'M35-form-journey-member',
    'M35-campaigns': 'M35-form-campaign',
    'M35-form-campaign': 'M35-form-campaign',
    'M35-journeys': 'M35-form-journey',
    'M35-offers': 'M35-form-offer',
    'M35-content': 'M35-form-creative',
    'M35-ads': 'M35-form-ad',
    'M35-ab': 'M35-form-experiment',
    'M35-triggers': 'M35-form-trigger',
    'M35-audience': 'M35-form-campaign',
    'M35-comarketing': 'M35-form-campaign',
    'M35-mdf': 'M40-form-rebate',
    'M35-spend': 'M35-form-spend',
    'M35-attribution-models': 'M35-form-attribution-model'
  }
};

export const CREATE = {
  M35: { screen: 'M35-form-campaign', model: 'fix.campaign', label: 'Campaign' }
};
