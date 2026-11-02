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
      { id: 'M35-approval', en: 'Planning & Approval', bn: 'পরিকল্পনা ও অনুমোদন', t: 'c' }
    ]},
    { en: 'Journeys', screens: [
      { id: 'M35-journeys', en: 'Journey Orchestration', bn: 'জার্নি অর্কেস্ট্রেশন', t: 'f' },
      { id: 'M35-triggers', en: 'Behaviour Triggers', bn: 'আচরণ ট্রিগার', t: 'g' }
    ]},
    { en: 'Offers & Content', screens: [
      { id: 'M35-offers', en: 'Offer Selection', bn: 'অফার নির্বাচন', t: 'g' },
      { id: 'M35-content', en: 'Creative Library', bn: 'ক্রিয়েটিভ লাইব্রেরি', t: 'g' },
      { id: 'M35-ads', en: 'Portal Ad Placement', bn: 'পোর্টাল বিজ্ঞাপন', t: 'g' }
    ]},
    { en: 'Measurement', screens: [
      { id: 'M35-ab', en: 'A/B & Holdout', bn: 'এ/বি পরীক্ষা', t: 'g' },
      { id: 'M35-attribution', en: 'Attribution Model', bn: 'অ্যাট্রিবিউশন', t: 'r' },
      { id: 'M35-roi', en: 'Budget & ROI', bn: 'বাজেট ও ROI', t: 'r' }
    ]},
    { en: 'Journey Runtime (S10)', bn: 'জার্নি রানটাইম', screens: [
      { id: 'M35-journey-members', en: 'Journey Members', bn: 'জার্নি সদস্য', t: 'g' },
      { id: 'M35-form-journey-member', en: 'Journey Member', bn: 'সদস্য ফর্ম', t: 'f' }
    ]},
    { en: 'Multi-Touch Attribution', bn: 'মাল্টি-টাচ অ্যাট্রিবিউশন', screens: [
      { id: 'M35-touches', en: 'Touchpoint Ledger', bn: 'টাচপয়েন্ট লেজার', t: 'g' }
    ]}
  ],
  reports: ['Campaign Funnel by Channel', 'Attribution & ROI', 'Seasonal Template Performance', 'Co-Marketing Partner Report', 'Lead-to-Order Conversion'],
  forms: ['Campaign', 'Journey (multi-step)', 'Offer', 'Creative Asset', 'Journey Member'],
  cross: ['M33 Customer Master', 'M10 Loyalty', 'M34 CX Feedback'],
  freg: { src: 58, sub: [
    ['1', 'Campaign Planning & Approval', 8, { model: 'fix.campaign', cols: ['name', 'state', 'dofa_tier_required', 'dofa_approved', 'dofa_approved_by', 'dofa_approved_at'], screens: ['M35-campaigns', 'M35-approval'] }], ['2', 'Audience from Segments', 6, { screens: ['M35-campaigns'] }],
    ['3', 'Journey Orchestration', 10, { model: 'fix.campaign.journey', cols: ['name', 'state', 'active', 'campaign_id', 'trigger_event', 'steps_json'], screens: ['M35-journeys', 'M35-triggers'] }], ['4', 'Content & Offers', 8, { model: 'fix.campaign.creative', cols: ['name', 'state', 'campaign_id', 'asset_type', 'channel', 'reference'], screens: ['M35-content', 'M35-offers'] }],
    ['5', 'Experimentation', 7, { model: 'fix.campaign.experiment', cols: ['name', 'state', 'campaign_id', 'variant_a_pct', 'metric', 'result_note'], screens: ['M35-ab'] }], ['6', 'Budget & Attribution', 8, { screens: ['M35-attribution', 'M35-roi', 'M35-rpt-roi'] }],
    ['7', 'Portal Advertising', 5, { model: 'fix.campaign.ad', cols: ['name', 'active', 'campaign_id', 'placement', 'impressions', 'clicks'], screens: ['M35-ads'] }], ['8', 'Co-Marketing', 6, { screens: ['M35-rpt-co'] }]
  ] }
};

export const SCREENS = {
  'M35-campaigns': { kind: 'model_list', model: 'fix.campaign', stateField: 'state',
    cols: ['name', 'channel', 'target_audience_type', 'budget', 'response_count', 'recipient_count', 'state'],
    actions: [
      { m: 'action_approve_budget', l: 'Approve Budget (DOFA)' },
      { m: 'action_launch', l: 'Launch Campaign' },
      { m: 'action_pause', l: 'Pause' },
      { m: 'action_resume', l: 'Resume' },
      { m: 'action_complete', l: 'Mark Completed' }
    ] },
  'M35-approval': { kind: 'table_report', module: 'M35', report: 'campaign_approval', title: 'Planning & Approval', period: false },
  'M35-journeys': { kind: 'model_list', model: 'fix.campaign.journey', stateField: 'state',
    cols: ['name', 'campaign_id', 'trigger_event', 'state', 'active'] },
  'M35-triggers': { kind: 'model_list', model: 'fix.campaign.trigger', stateField: 'active',
    cols: ['name', 'campaign_id', 'event', 'delay_hours', 'active'] },
  'M35-offers': { kind: 'model_list', model: 'fix.campaign.offer', stateField: 'active',
    cols: ['name', 'campaign_id', 'offer_type', 'value', 'valid_from', 'valid_until', 'active'] },
  'M35-content': { kind: 'model_list', model: 'fix.campaign.creative', stateField: 'state',
    cols: ['name', 'campaign_id', 'asset_type', 'channel', 'reference', 'state'] },
  'M35-ads': { kind: 'model_list', model: 'fix.campaign.ad', stateField: 'active',
    cols: ['name', 'campaign_id', 'placement', 'active', 'impressions', 'clicks'] },
  'M35-ab': { kind: 'model_list', model: 'fix.campaign.experiment', stateField: 'state',
    cols: ['name', 'campaign_id', 'variant_a_pct', 'metric', 'state', 'result_note'] },
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
      { id: 'budget', label: '2. Budget & DOFA Memo', bn: '২. বাজেট ও ডোফা', icon: '💰', badge: '6' },
      { id: 'audience', label: '3. Audience Segmentation', bn: '৩. অডিয়েন্স সেগমেন্ট', icon: '👥', badge: '3' },
      { id: 'compliance', label: '4. BTRC Curfew & PDPA', bn: '৪. কমপ্লায়েন্স ও কার্ফিউ', icon: '🛡️', badge: '4' },
      { id: 'docs', label: '5. Creative Assets & Approvals', bn: '৫. ক্রিয়েটিভ সম্পদ ও অনুমোদন', icon: '🎨', badge: '2' },
      { id: 'attribution', label: '6. Attribution & ROI', bn: '৬. অ্যাট্রিবিউশন ও আরওআই', icon: '📈', badge: '5' },
      { id: 'audit', label: '7. System Governance', bn: '৭. অডিট ট্রেইল', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Campaign Identification & Broadcast Channel', fields: [
        { name: 'name', required: true, label: 'Campaign Title (English)' },
        { name: 'name_bn', label: 'Campaign Title (Bengali Bangla)' },
        { name: 'channel', required: true, label: 'Primary Delivery Channel (SMS / Email / Push / Social)' },
        { name: 'state', label: 'Campaign Lifecycle State' },
        { name: 'operating_unit_id', label: 'Operating Business Unit' },
        { name: 'company_id', label: 'Operating Legal Entity' },
      ]},
      { tab: 'budget', title: 'Financial Budget & DOFA Governance Gating (FLAW-35.1)',
        note: 'Campaign budget releases mandate a documented Finance internal memo reference and DOFA executive sign-off before campaign activation.',
        fields: [
          { name: 'budget', required: true, label: 'Allocated Campaign Budget (BDT)' },
          { name: 'budget_memo_ref', required: true, label: 'Internal Finance Memo Reference' },
          { name: 'budget_approved', label: 'DOFA Executive Budget Approval Confirmed' },
          { name: 'budget_approver_id', label: 'Authorized DOFA Executive Signoff' },
          { name: 'budget_approval_date', label: 'DOFA Budget Approval Date', readonly: true },
          { name: 'currency_id', label: 'Budget Currency', readonly: true },
      ]},
      { tab: 'audience', title: 'Target Audience Profile & Criteria Filter', fields: [
        { name: 'target_audience_type', required: true, label: 'Target Audience Classification' },
        { name: 'audience_domain', label: 'Audience Criteria Domain (Odoo Domain Filter)' },
        { name: 'recipient_count', label: 'Total Targeted Customer Count', readonly: true },
      ]},
      { tab: 'compliance', title: 'BTRC Telecom Curfew & PDPA Consent Verification (FLAW-35.2)',
        note: 'BTRC Telecommunication Directive: Outbound SMS marketing broadcasts are restricted strictly to 08:00 to 22:00 BST. Do-Not-Disturb (DND) customers are scrubbed automatically.',
        fields: [
          { name: 'pdpa_consent_verified', label: 'Statutory PDPA Consent Verification Completed' },
          { name: 'excluded_no_consent_count', label: 'DND & Non-Consented Excluded Customers', readonly: true },
          { name: 'start_date', required: true, label: 'Campaign Scheduled Start Date' },
          { name: 'end_date', required: true, label: 'Campaign Scheduled End Date' },
      ]},
      { tab: 'docs', title: 'Creative Assets, NOC & Approval Evidence', 
        note: 'Creative banners, BTRC NOC letters and the CFO budget-approval memo are fix.campaign.creative records (see the Creative Assets grid) plus budget_memo_ref on the Budget tab. The checksummed repository (fix.document, M24 — SHA-256) is the estate-wide asset path; a direct campaign→document relation is a declared platform gap.',
        fields: [
          { name: 'recipient_ids', label: 'Associated Campaign Audience Records', readonly: true },
          { name: 'budget_memo_ref', label: 'DOFA Budget Approval Memo Reference', readonly: true },
          { name: 'btrc_sender_mask', label: 'BTRC Approved Sender ID Mask' },
          { name: 'sms_opt_out_text', label: 'Mandatory Opt-Out Instruction' },
          { name: 'dnd_scrubbed_at', label: 'DND Registry Scrubbed At', readonly: true },
          { name: 'dnd_excluded_count', label: 'Recipients Excluded by BTRC DND', readonly: true },
      ]},
      { tab: 'attribution', title: 'Marketing Attribution & Customer Acquisition Economics', fields: [
        { name: 'utm_source', label: 'UTM Tracking Source' },
        { name: 'utm_medium', label: 'UTM Tracking Medium' },
        { name: 'utm_campaign', label: 'UTM Tracking Campaign Name' },
        { name: 'response_count', label: 'Total Inbound Customer Responses', readonly: true },
        { name: 'cost_per_response', label: 'Effective Cost per Response (BDT)', readonly: true },
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
        { name: 'purpose', label: 'Purpose' },
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
        note: 'D365 ships two kinds with different membership semantics, and the estate conflated them. A SEGMENT-BASED journey enumerates its audience at launch; a TRIGGER-BASED one admits one member per event and must be idempotent. The constraint refuses a journey whose kind has no starter, because it would silently enrol nobody.',
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
          { name: 'step_count', label: 'Steps' },
          { name: 'steps_json', label: 'Legacy Steps Definition (JSON)', type: 'text' }
        ]
      },
      {
        tab: 'audit',
        title: 'Journey State & Membership',
        fields: [
          { name: 'state', required: true, label: 'Execution State' },
          { name: 'launched_at', label: 'Activated At' },
          { name: 'member_active_count', label: 'Active Members' },
          { name: 'member_completed_count', label: 'Completed' },
          { name: 'member_exited_count', label: 'Exited / Failed' },
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
        fields: [
          { name: 'state', required: true, label: 'Approval State' }
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
        note: 'Statistically controlled A/B split on messaging or creative variants.',
        fields: [
          { name: 'name', required: true, label: 'Experiment Name' },
          { name: 'campaign_id', required: true, label: 'Campaign' }
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
        fields: [
          { name: 'result_note', label: 'Experiment Finding & Winner' },
          { name: 'state', required: true, label: 'Lifecycle State' }
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
          { name: 'placement', required: true, label: 'Portal Placement Location' }
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
        { name: 'enrol_source', label: 'Joined Via', required: true },
        { name: 'source_event_id', label: 'Outbox Event' },
        { name: 'enrol_key', label: 'Idempotency Key' },
        { name: 'entered_at', label: 'Joined At', required: true }
        ]
      },
      {
        tab: 'progress',
        title: 'Where They Are',
        note: 'Membership and consent are re-evaluated before every step, not trusted from the launch-time snapshot.',
        fields: [
        { name: 'current_step_id', label: 'Current Step' },
        { name: 'next_action_at', label: 'Next Action' },
        { name: 'steps_executed', label: 'Steps Run' },
        { name: 'state', label: 'State', required: true },
        { name: 'exited_at', label: 'Left At' },
        { name: 'exit_reason', label: 'Why They Stopped' }
        ]
      },
      {
        tab: 'messages',
        title: 'Delivery Rows',
        fields: [
        { name: 'delivery_ids', label: 'Messages' },
        { name: 'last_send_state', label: 'Last Send Outcome' }
        ]
      }
    ]
  },
  'M35-touches': { kind: 'model_list', model: 'fix.campaign.touch', create: false,
    cols: ['occurred_at', 'campaign_id', 'partner_id', 'touch_type', 'channel', 'value_bdt', 'value_known'],
    note: 'Harvested from the S1 delivery log. Only sent and delivered messages earn attribution credit.' },
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
  'M35:Creative Asset': 'fix.campaign.creative'
};

export const FORM_CHIPS = {
  'M35:Journey Member': 'M35-form-journey-member',
  'M35:Campaign': 'M35-form-campaign',
  'M35:Journey (multi-step)': 'M35-form-journey',
  'M35:Offer': 'M35-form-offer',
  'M35:Creative Asset': 'M35-form-creative',
  'M35:__by_model__': {
    'fix.campaign.journey.member': 'M35-form-journey-member',
    'fix.campaign': 'M35-form-campaign',
    'fix.campaign.journey': 'M35-form-journey',
    'fix.campaign.trigger': 'M35-form-trigger',
    'fix.campaign.offer': 'M35-form-offer',
    'fix.campaign.creative': 'M35-form-creative',
    'fix.campaign.ad': 'M35-form-ad',
    'fix.campaign.experiment': 'M35-form-experiment'
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
    'M35-triggers': 'M35-form-trigger'
  }
};

export const CREATE = {
  M35: { screen: 'M35-form-campaign', model: 'fix.campaign', label: 'Campaign' }
};
