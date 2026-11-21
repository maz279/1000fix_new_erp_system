/** @odoo-module **/
/* A04 · Commercial & Revenue — M40 Partner & Channel (v2 rebuild).
 * A04 audit (2026-11-04): workflow fields are read-only; the lifecycles run
 * from the list actions.
 * Registry-faithful at birth (4 groups / 13 screens / 5 reports / 4 forms /
 * freg 80); the 19 Nov 2026 capture audit added the spec's registers.
 * Partners (8) and referrals (7) are real; authorisations, deals, rebates,
 * franchises and conflicts are new. Partner revenue = recorded referral
 * commission + won deal value. Co-marketing (a declared gap until 12 Nov
 * 2026) is built from the campaign's co-marketing partners, the MDF's
 * campaign key and the M35 touch attribution. */

export const MODULE = {
  area: 'A04', code: 'M40', en: 'Partner & Channel', title: 'M40 · Partner & Channel',
  bn: 'পার্টনার ও চ্যানেল', icon: '🤝',
  desc: 'Partner master and onboarding, brand authorisations, alliances, referral programme, deal registration, resellers, franchises, rebates and MDF, channel conflict and partner health/ranking.',
  kpis: [
    { l: 'Brand Partners', m: 'brand_partners' },
    { l: 'Referral Partners', m: 'referral_partners' },
    { l: 'Deal Registrations', m: 'deal_registrations' },
    { l: 'Partner Revenue MTD', m: 'partner_revenue_mtd', prefix: '৳ ' },
    { l: 'Audits Due (90d)', m: 'audits_due_90d' },
    { l: 'Rebates Accrued', m: 'rebates_accrued', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Partner Master', screens: [
      { id: 'M40-partners', en: 'Partner Directory', bn: 'পার্টনার ডিরেক্টরি', t: 'g' },
      { id: 'M40-brand', en: 'Brand Partner Relations', bn: 'ব্র্যান্ড পার্টনার', t: 'r' },
      { id: 'M40-authorisation', en: 'Authorisation & Certification', bn: 'অনুমোদন', t: 'g' },
      { id: 'M40-audits', en: 'Technical Audits', bn: 'টেকনিক্যাল অডিট', t: 'g' },
      { id: 'M40-programmes', en: 'Programmes & Tiers', bn: 'কার্যক্রম ও স্তর', t: 'g' },
      { id: 'M40-contacts', en: 'Partner Contacts', bn: 'পার্টনার যোগাযোগ', t: 'g' },
      { id: 'M40-rate-changes', en: 'Commission Rate Changes', bn: 'কমিশন হার পরিবর্তন', t: 'g' }
    ]},
    { en: 'Onboarding & Brand Governance', screens: [
      { id: 'M40-onboarding', en: 'Onboarding Checklist', bn: 'অনবোর্ডিং চেকলিস্ট', t: 'g' },
      { id: 'M40-enablement', en: 'Enablement & Certification', bn: 'প্রশিক্ষণ ও সনদ', t: 'g' },
      { id: 'M40-obligations', en: 'Brand Obligations', bn: 'ব্র্যান্ড দায়বদ্ধতা', t: 'g' },
      { id: 'M40-brand-audits', en: 'Brand Audit Calendar', bn: 'ব্র্যান্ড অডিট', t: 'g' },
      { id: 'M40-engagement', en: 'Engagement Log', bn: 'যোগাযোগ লগ', t: 'g' }
    ]},
    { en: 'Programmes', screens: [
      { id: 'M40-alliance', en: 'Alliance Benefits', bn: 'অ্যালায়েন্স সুবিধা', t: 'r' },
      { id: 'M40-referral', en: 'Referral Programme', bn: 'রেফারেল কার্যক্রম', t: 'g' },
      { id: 'M40-dealreg', en: 'Deal Registration', bn: 'ডিল নিবন্ধন', t: 'g' },
      { id: 'M40-reseller', en: 'Resellers', bn: 'রিসেলার', t: 'r' },
      { id: 'M40-franchise', en: 'Franchise Management', bn: 'ফ্র্যাঞ্চাইজি', t: 'g' },
      { id: 'M40-schemes', en: 'Alliance Schemes', bn: 'অ্যালায়েন্স স্কিম', t: 'g' },
      { id: 'M40-eligibility', en: 'Eligibility Checks', bn: 'যোগ্যতা যাচাই', t: 'g' },
      { id: 'M40-leads', en: 'Partner Leads', bn: 'পার্টনার লিড', t: 'g' },
      { id: 'M40-referral-links', en: 'Referral Links & Codes', bn: 'রেফারেল লিংক', t: 'g' },
      { id: 'M40-allocations', en: 'Reseller Allocations', bn: 'রিসেলার বরাদ্দ', t: 'g' },
      { id: 'M40-draws', en: 'Reseller Draws', bn: 'রিসেলার উত্তোলন', t: 'g' },
      { id: 'M40-territories', en: 'Franchise Territories', bn: 'ফ্র্যাঞ্চাইজি অঞ্চল', t: 'g' },
      { id: 'M40-royalties', en: 'Franchise Royalties', bn: 'রয়্যালটি', t: 'g' }
    ]},
    { en: 'Commercial', screens: [
      { id: 'M40-rebates', en: 'Rebates & MDF', bn: 'রিবেট ও MDF', t: 'g' },
      { id: 'M40-comarketing', en: 'Co-Marketing', bn: 'কো-মার্কেটিং', t: 'r' },
      { id: 'M40-conflict', en: 'Channel Conflict', bn: 'চ্যানেল দ্বন্দ্ব', t: 'g' },
      { id: 'M40-conflict-rules', en: 'Channel Precedence Rules', bn: 'চ্যানেল অগ্রাধিকার', t: 'g' },
      { id: 'M40-mdf-funds', en: 'MDF Funds', bn: 'MDF তহবিল', t: 'g' },
      { id: 'M40-mdf-claims', en: 'MDF Claims', bn: 'MDF দাবি', t: 'g' }
    ]},
    { en: 'Performance', screens: [
      { id: 'M40-health', en: 'Health & Risk', bn: 'স্বাস্থ্য ও ঝুঁকি', t: 'r' },
      { id: 'M40-ranking', en: 'Ranking & Scorecards', bn: 'র্যাঙ্কিং', t: 'r' }
    ]}
  ],
  reports: ['Partner Revenue Contribution', 'Referral Conversion', 'Brand Audit Calendar', 'Rebate Accruals', 'Channel Conflict Log', 'Deal Register'],
  forms: ['Partner', 'Deal Registration', 'Rebate Scheme', 'Franchise Agreement'],
  cross: ['M07 CRM', 'M12 Marketplace', 'M35 Marketing', 'M20 AR'],
  /* M40 capture audit (19 Nov 2026): each page lists and captures the
   * records the spec puts on it; "+ New" is the page's own record. */
  freg: { src: 80, sub: [
    ['1', 'Partner Master', 10, { model: 'fix.partner', cols: ['name', 'state', 'partner_type', 'programme_id', 'tier_id', 'territory'], screens: ['M40-partners', 'M40-programmes', 'M40-contacts', 'M40-rate-changes'], reports: ['Partner Revenue Contribution'], forms: ['Partner', 'Partner Programme', 'Partner Contact', 'Commission Rate Change'] }],
    ['2', 'Recruitment & Onboarding', 8, { model: 'fix.partner.onboarding', cols: ['partner_id', 'step', 'name', 'required', 'state'], screens: ['M40-onboarding', 'M40-enablement', 'M40-partners'], reports: [], forms: ['Onboarding Step', 'Partner Enablement', 'Partner'] }],
    ['3', 'Brand Relations', 9, { model: 'fix.partner.authorisation', cols: ['name', 'partner_id', 'brand_id', 'valid_to', 'state'], screens: ['M40-brand', 'M40-authorisation', 'M40-obligations', 'M40-brand-audits', 'M40-engagement'], reports: ['Brand Audit Calendar'], forms: ['Partner Authorisation', 'Brand Obligation', 'Brand Audit', 'Partner Engagement'] }],
    ['4', 'Alliances', 6, { model: 'fix.alliance.scheme', cols: ['code', 'name', 'partner_id', 'valid_from', 'valid_to', 'eligible_count', 'state'], screens: ['M40-schemes', 'M40-eligibility', 'M40-alliance'], reports: [], forms: ['Alliance Scheme', 'Eligibility Check'] }],
    ['5', 'Referrals', 8, { model: 'fix.partner.lead', cols: ['name', 'partner_id', 'customer_name', 'attribution_expires_on', 'referral_id', 'state'], screens: ['M40-leads', 'M40-referral-links', 'M40-referral', 'M40-rpt-referral'], reports: ['Referral Conversion'], forms: ['Partner Lead', 'Referral Link', 'Referral'] }],
    ['6', 'Deal Registration', 7, { model: 'fix.partner.deal', cols: ['name', 'state', 'partner_id', 'customer_id', 'value', 'registered_on'], screens: ['M40-dealreg', 'M40-conflict', 'M40-conflict-rules', 'M40-rpt-deals'], reports: ['Deal Register', 'Channel Conflict Log'], forms: ['Deal Registration', 'Channel Conflict', 'Channel Precedence Rule'] }],
    ['7', 'Resellers', 6, { model: 'fix.reseller.allocation', cols: ['name', 'partner_id', 'item_description', 'qty', 'consumed_qty', 'state'], screens: ['M40-allocations', 'M40-draws', 'M40-reseller'], reports: [], forms: ['Reseller Allocation', 'Reseller Draw'] }],
    ['8', 'Franchise', 9, { model: 'fix.partner.franchise', cols: ['name', 'state', 'partner_id', 'territory', 'fee', 'start_date', 'end_date'], screens: ['M40-franchise', 'M40-territories', 'M40-royalties'], reports: [], forms: ['Franchise Agreement', 'Franchise Territory', 'Franchise Royalty'] }],
    ['9', 'Commercial Terms', 8, { model: 'fix.partner.rebate', cols: ['name', 'state', 'partner_id', 'amount', 'period', 'basis', 'rate'], screens: ['M40-rebates', 'M40-mdf-funds', 'M40-mdf-claims', 'M40-comarketing', 'M40-rpt-rebates'], reports: ['Rebate Accruals'], forms: ['Rebate Scheme', 'MDF Fund', 'MDF Claim'] }],
    ['10', 'Performance', 9, { model: 'fix.partner.audit', cols: ['name', 'partner_id', 'audit_date', 'score', 'valid_until', 'state'], screens: ['M40-audits', 'M40-health', 'M40-ranking', 'M40-rpt-revenue'], reports: ['Partner Revenue Contribution'], forms: ['Technical Audit'] }]
  ] }
};

export const SCREENS = {
  /* A04 audit (2026-11-04) C3: the partner lifecycle runs from these
   * buttons; the status, KYC stamps, audit score and commission rate are
   * read-only on the form. The server checks the role and the segregation of
   * duties (creator, submitter, uploader, suspender) for each. */
  'M40-partners': { kind: 'model_list', model: 'fix.partner', stateField: 'state',
    cols: ['name', 'partner_id', 'partner_type', 'territory', 'commission_rate', 'kyc_verified', 'technical_audit_score', 'state'],
    actions: [
      { m: 'action_submit_onboarding', l: 'Submit for Onboarding', states: ['prospective'] },
      { m: 'action_verify_kyc', l: 'Verify KYC Documents', states: ['prospective', 'qualifying'] },
      { m: 'action_onboard', l: 'Approve Onboarding', states: ['prospective', 'qualifying'] },
      { m: 'action_return_to_prospect', l: 'Return Application', ask: 'What is missing', kwarg: 'reason', states: ['qualifying'] },
      { m: 'action_suspend', l: 'Suspend Partner', ask: 'Reason for suspension', kwarg: 'reason', states: ['onboarded', 'probation'] },
      { m: 'action_reinstate', l: 'Reinstate Partner', ask: 'Reason for reinstatement', kwarg: 'reason', states: ['suspended'] },
      /* A04 ERP audit M40-F24: the spec's standings (FR-PCM-010) */
      { m: 'action_probation', l: 'Put on Probation', ask: 'Remediation plan', kwarg: 'reason', states: ['onboarded'] },
      { m: 'action_end_probation', l: 'End Probation', ask: 'Outcome of the remediation', kwarg: 'reason', states: ['probation'] },
      { m: 'action_reactivate', l: 'Reactivate Dormant Partner', ask: 'Reason for reactivation', kwarg: 'reason', states: ['dormant'] },
      { m: 'action_start_exit', l: 'Start Exit (CCO)', ask: 'Reason for the exit', kwarg: 'reason', states: ['onboarded', 'probation', 'dormant', 'suspended'] },
      { m: 'action_complete_exit', l: 'Complete Exit (CCO)', states: ['exiting'] },
      /* A04 ERP audit M40-F5: proposes the rate; a DOFA Tier 3 approver
       * applies it from the M63 inbox */
      { m: 'action_set_commission_rate', l: 'Propose Commission Rate', ask: 'New rate as a fraction (0.05 = 5%)', kwarg: 'rate' },
      { m: 'action_generate_onboarding', l: 'Generate Onboarding Checklist', states: ['prospective', 'qualifying'] },
      { m: 'action_change_tier', l: 'Move to Tier', ask: 'Tier code within the partner programme', kwarg: 'tier_code', states: ['onboarded'] },
      { m: 'action_request_erasure', l: 'Register PDPA Erasure Request' },
      { m: 'action_execute_erasure', l: 'Execute PDPA Erasure (Tier 3)' }
    ] },
  'M40-audits': { kind: 'model_list', model: 'fix.partner.audit', stateField: 'state',
    cols: ['name', 'partner_id', 'audit_date', 'score', 'auditor_id', 'approved_by_id', 'valid_until', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit Audit', states: ['draft'] },
      { m: 'action_approve', l: 'Approve Audit', states: ['submitted'] },
      { m: 'action_reject', l: 'Reject Audit', ask: 'Reason for rejecting', kwarg: 'reason', states: ['submitted'] }
    ] },
  'M40-brand': { kind: 'table_report', module: 'M40', report: 'brand_partners', title: 'Brand Partner Relations', period: false },
  'M40-authorisation': { kind: 'model_list', model: 'fix.partner.authorisation', stateField: 'state',
    cols: ['name', 'partner_id', 'brand_id', 'valid_from', 'valid_to', 'certificate_ref', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Authorisation', states: ['draft'] },
      { m: 'action_revoke', l: 'Revoke Authorisation', ask: 'Reason for revoking', kwarg: 'reason', states: ['active'] }
    ] },
  'M40-alliance': { kind: 'table_report', module: 'M40', report: 'alliance_report', title: 'Alliance Benefits', period: false },
  'M40-referral': { kind: 'model_list', model: 'fix.referral', stateField: 'state',
    cols: ['name', 'partner_id', 'referred_partner_id', 'base_amount', 'commission_amount', 'state'] },
  'M40-dealreg': { kind: 'model_list', model: 'fix.partner.deal', stateField: 'state',
    cols: ['name', 'partner_id', 'customer_id', 'value', 'registered_on', 'protected_until', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve & Protect (conflict check)', states: ['registered', 'conflict'] },
      { m: 'action_decline', l: 'Decline Registration', ask: 'Reason for declining', kwarg: 'reason', states: ['registered', 'conflict'] },
      { m: 'action_mark_won', l: 'Mark Won', states: ['approved'] },
      { m: 'action_mark_lost', l: 'Mark Lost', states: ['registered', 'approved'] }
    ] },
  'M40-reseller': { kind: 'table_report', module: 'M40', report: 'reseller_report', title: 'Resellers', period: false },
  'M40-franchise': { kind: 'model_list', model: 'fix.partner.franchise', stateField: 'state',
    cols: ['name', 'partner_id', 'territory', 'fee', 'start_date', 'end_date', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Agreement', states: ['draft'] },
      { m: 'action_terminate', l: 'Terminate Agreement', ask: 'Reason for termination', kwarg: 'reason', states: ['active'] }
    ] },
  /* A04 audit M40-1/2/3: the payout is approved from the M63 inbox; the
   * approver holds the DOFA tier of the amount, did not raise the rebate,
   * and the partner's approved technical audit is at least 85%. */
  'M40-rebates': { kind: 'model_list', model: 'fix.partner.rebate', stateField: 'state',
    cols: ['name', 'partner_id', 'period', 'kind', 'campaign_id', 'basis', 'rate', 'amount', 'approval_state', 'state'],
    actions: [
      { m: 'action_accrue', l: 'Accrue Rebate', states: ['draft'] },
      { m: 'action_request_approval', l: 'Request Payout Approval', ask: 'Justification for the payout', kwarg: 'justification', states: ['accrued'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['accrued'] },
      /* A04 ERP audit M40-F13: paid when its M50 payout is executed */
      { m: 'action_record_payout', l: 'Record Payout (Finance)', states: ['approved'] },
      { m: 'action_cancel', l: 'Cancel Rebate', states: ['draft', 'accrued'] }
    ] },
  /* M40-comarketing (12 Nov 2026): partners named on a campaign
   * (fix.campaign.partner_ids, kept from the partner form's Co-Marketing
   * Campaigns), their MDF on it (the rebate's campaign) and the revenue the
   * M35 touch attribution credits where the conversion value is on file. */
  'M40-comarketing': { kind: 'table_report', module: 'M40', report: 'comarketing', title: 'Co-Marketing', period: false },
  /* DISC-40.2 / A04 audit M40-6: a ruling is given once, by a Tier 3
   * arbitrator who did not raise the conflict, with a rationale. */
  'M40-conflict': { kind: 'model_list', model: 'fix.partner.conflict', stateField: 'state',
    cols: ['name', 'partner_a_id', 'partner_b_id', 'customer_id', 'dofa_decision', 'dofa_arbitrator_id', 'state'],
    actions: [
      { m: 'action_rule_partner_a', l: 'Rule: Award Partner A', ask: 'Arbitration rationale', kwarg: 'notes', states: ['open'] },
      { m: 'action_rule_partner_b', l: 'Rule: Award Partner B', ask: 'Arbitration rationale', kwarg: 'notes', states: ['open'] },
      { m: 'action_rule_split', l: 'Rule: Split', ask: 'Arbitration rationale', kwarg: 'notes', states: ['open'] },
      { m: 'action_rule_direct', l: 'Rule: Retain as Direct Account', ask: 'Arbitration rationale', kwarg: 'notes', states: ['open'] },
      { m: 'action_close', l: 'Close Conflict', states: ['mediated'] }
    ] },
  'M40-health': { kind: 'table_report', module: 'M40', report: 'health', title: 'Health & Risk', period: false },
  'M40-ranking': { kind: 'table_report', module: 'M40', report: 'ranking', title: 'Ranking & Scorecards', period: false },

  /* Report chips -> their own computed pack */
  'M40-rpt-revenue': { kind: 'table_report', module: 'M40', report: 'partner_revenue', title: 'Partner Revenue Contribution', period: false },
  'M40-rpt-referral': { kind: 'table_report', module: 'M40', report: 'referral_conversion', title: 'Referral Conversion', period: false },
  'M40-rpt-audits': { kind: 'table_report', module: 'M40', report: 'brand_audit_calendar', title: 'Brand Audit Calendar', period: false },
  'M40-rpt-rebates': { kind: 'table_report', module: 'M40', report: 'rebate_accruals', title: 'Rebate Accruals', period: false },
  'M40-rpt-conflict': { kind: 'table_report', module: 'M40', report: 'conflict_log', title: 'Channel Conflict Log', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M40-form-partner': {
    kind: 'model_form',
    model: 'fix.partner',
    lines: {
      field: 'audit_ids',
      title: 'Technical Audits',
      note: 'The audit score that gates rebates is the latest audit approved by a channel manager other than the auditor (A04 audit M40-2); audits are recorded on the Technical Audits screen.',
      fields: [
        { name: 'name', label: 'Audit', readonly: true },
        { name: 'audit_date', label: 'Date', readonly: true },
        { name: 'score', label: 'Score (%)', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ]
    },
    title: 'Channel Partner & Franchise Master',
    back: 'M40-partners',
    status: { field: 'state' },
    tabs: [
      { id: 'partner', label: '1. Partner Master', bn: '১. পার্টনার পরিচিতি', icon: '🏢', badge: '6' },
      { id: 'brand_auth', label: '2. Brand Authorisations', bn: '২. ব্র্যান্ড অনুমোদন', icon: '🛡️', badge: '2' },
      { id: 'financials', label: '3. Financials & Rebates', bn: '৩. কমিশন ও রিবেট', icon: '২', badge: '3' },
      { id: 'statutory', label: '4. Statutory Tax & KYC', bn: '৪. কেওয়াইসি ও কর', icon: '⚖️', badge: '5' },
      { id: 'technical', label: '5. Technical Audits & ESD', bn: '৫. টেকনিক্যাল অডিট', icon: '🔬', badge: '2' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'partner', title: 'Channel Partner Identity',
        note: 'Authorized franchise, reseller, or referral partner under 1000FiX partner governance.',
        fields: [
          { name: 'name', required: true, label: 'Partner Entity Name' },
          { name: 'partner_id', required: true, label: 'Party Master Record (M33)' },
          { name: 'partner_type', required: true, label: 'Partnership Classification' },
          { name: 'brand_id', label: 'Brand (M37) - brand partners only' },
          { name: 'territory', label: 'Assigned Geographic Territory' },
          { name: 'contract_id', label: 'Master Franchise Agreement (M08)' },
          { name: 'programme_id', label: 'Partner Programme (version bound, BRU-PCM-12)' },
          { name: 'programme_version', readonly: true, label: 'Programme Version' },
          { name: 'tier_id', readonly: true, label: 'Tier (moved by a channel manager)' },
          { name: 'state', readonly: true, label: 'Partnership Status' },
          { name: 'onboarded_by_id', readonly: true, label: 'Onboarded By' },
          { name: 'pdpa_erasure_state', readonly: true, label: 'PDPA Erasure Status' }
        ] },
      { tab: 'brand_auth', title: 'Brand Certifications & Scopes',
        note: 'Brand certifications authorizing partner workshop technicians to perform warranty repairs.',
        fields: [] },
      { tab: 'financials', title: 'Commercial Commission & Volume Rebates',
        fields: [
          { name: 'commission_rate', readonly: true, label: 'Standard Referral Commission Rate (set by a channel manager)' },
          { name: 'comarketing_campaign_ids', label: 'Co-Marketing Campaigns (M35; a channel officer names them, onboarded partners only)' }
        ] },
      { tab: 'statutory', title: 'Bangladesh Statutory Compliance & Tax Registrations',
        note: 'Mandatory trade license, e-TIN, and National ID verification under Bangladesh law.',
        fields: [
          { name: 'nid_number', label: 'National ID (NID)' },
          { name: 'tin_number', label: '12-Digit e-TIN' },
          { name: 'trade_license_no', label: 'Trade License Number' },
          { name: 'trade_license_expiry', label: 'Trade License Expiry Date' },
          { name: 'bank_solvency_ref', label: 'Bank Solvency Reference' },
          { name: 'trade_license_attachment_id', label: 'Trade Licence Document' },
          { name: 'bank_solvency_attachment_id', label: 'Bank Solvency Certificate' },
          { name: 'kyc_verified', readonly: true, label: 'KYC Verified' },
          { name: 'kyc_verified_by_id', readonly: true, label: 'KYC Verified By' }
        ] },
      { tab: 'technical', title: 'Technical Compliance, Workshop Tooling & ESD Audit',
        note: 'Annual technical audit score (minimum 85.0% required for volume rebate payouts / FLAW-40.1).',
        fields: [
          { name: 'technical_audit_score', readonly: true, label: 'Technical Audit Score (%) — from the approved audit' },
          { name: 'technical_audit_id', readonly: true, label: 'Current Technical Audit' }
        ] },
      { tab: 'vault', title: 'Partner Agreement & Certificate Vault',
        note: 'Verified trade licenses, bank solvency certificates, ESD audit reports, and franchise agreements.',
        fields: [] }
    ]
  },

  'M40-form-deal': { kind: 'model_form', model: 'fix.partner.deal',
    title: 'Deal Registration', back: 'M40-dealreg',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'audit', label: '5. System Audit', bn: '৫. সিস্টেম অডিট' },
      { id: 'docs', label: '6. Documents', bn: '৬. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Deal Name', required: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'protected_until', label: 'Protected Until', readonly: true },
        { name: 'approved_by_id', label: 'Approved By', readonly: true },
        { name: 'conflict_id', label: 'Channel Conflict', readonly: true },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'value', label: 'Deal Value' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'registered_on', label: 'Registered On', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'customer_id', label: 'End Customer' },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M40-form-rebate': {
    kind: 'model_form',
    model: 'fix.partner.rebate',
    title: 'Channel Partner Rebate & MDF Scheme',
    back: 'M40-rebates',
    status: { field: 'state' },
    tabs: [
      { id: 'rebate_header', label: '1. Scheme Identification', bn: '১. স্কিম শনাক্তকরণ', icon: '🏷️', badge: '4' },
      { id: 'computation', label: '2. Basis & Rate', bn: '২. ভিত্তি ও হার', icon: '🧮', badge: '3' },
      { id: 'audit_payout', label: '3. Audit Gate & State', bn: '৩. অডিট গেট ও অবস্থা', icon: '🔒', badge: '1' }
    ],
    sections: [
      { tab: 'rebate_header', title: 'Rebate Scheme Target', note: 'Performance-driven channel partner rebate under statutory withholding rules.',
        fields: [
          { name: 'name', required: true, label: 'Scheme Name' },
          { name: 'partner_id', required: true, label: 'Authorized Partner' },
          { name: 'period', required: true, label: 'Evaluation Period' },
          { name: 'period_from', required: true, label: 'Period From (paid invoices)' },
          { name: 'period_to', required: true, label: 'Period To (paid invoices)' },
          { name: 'kind', required: true, label: 'Rebate Classification' },
          { name: 'campaign_id', label: 'Co-Marketing Campaign (MDF only; the partner must co-fund it)' }
        ] },
      { tab: 'computation', title: 'Stored Computation Formula', fields: [
          { name: 'basis', readonly: true, label: 'Basis: paid M20 invoices of the period, ex-VAT (computed at accrual)' },
          { name: 'basis_invoice_count', readonly: true, label: 'Paid Invoices Counted' },
          { name: 'rate', required: true, label: 'Incentive Rate (decimal)' },
          { name: 'amount', readonly: true, label: 'Gross Rebate Amount (computed BDT)' }
        ] },
      { tab: 'audit_payout', title: 'Technical Audit Gate & Settlement', fields: [
          { name: 'state', readonly: true, label: 'Settlement State' },
          { name: 'technical_audit_score', readonly: true, label: 'Partner Audit Score (%)' },
          { name: 'audit_id', readonly: true, label: 'Audit Relied On' },
          { name: 'dofa_tier_required', readonly: true, label: 'DOFA Tier Required' },
          { name: 'dofa_justification', label: 'Payout Justification', type: 'text' },
          { name: 'approval_state', readonly: true, label: 'Payout Approval' },
          { name: 'paid_ref', readonly: true, label: 'Payout Reference' }
        ] }
    ]
  },
  'M40-form-conflict': {
    kind: 'model_form',
    model: 'fix.partner.conflict',
    title: 'Channel Territory Conflict & Arbitration',
    back: 'M40-conflict',
    status: { field: 'state' },
    tabs: [
      { id: 'parties', label: '1. Contesting Partners', bn: '১. বিবদমান অংশীদার', icon: '👥', badge: '4' },
      { id: 'dispute_narrative', label: '2. Territory Conflict Narrative', bn: '২. অঞ্চল বিরোধের বিবরণ', icon: '📝', badge: '1' },
      { id: 'dofa_arbitration', label: '3. DOFA Arbitration & Outcome', bn: '৩. ডোফা সালিশ ও ফলাফল', icon: '⚖️', badge: '4' }
    ],
    sections: [
      { tab: 'parties', title: 'Contesting Parties', note: 'A territorial or account dispute between registered commercial partners.',
        fields: [
          { name: 'name', required: true, label: 'Conflict Docket Number' },
          { name: 'partner_a_id', required: true, label: 'Partner A (Complainant)' },
          { name: 'partner_b_id', label: 'Partner B (Respondent)' },
          { name: 'customer_id', label: 'Contested Account / Enterprise Customer' }
        ] },
      { tab: 'dispute_narrative', title: 'Factual Conflict Narrative', fields: [
          { name: 'description', required: true, label: 'Incident Statement & Overlap Details', type: 'text' }
        ] },
      { tab: 'dofa_arbitration', title: 'DOFA Arbitration Governance', fields: [
          { name: 'dofa_arbitrator_id', readonly: true, label: 'DOFA Arbitrator (who ruled)' },
          { name: 'dofa_decision', readonly: true, label: 'Arbitration Ruling Code' },
          { name: 'arbitration_notes', readonly: true, label: 'Arbitration Rationale', type: 'text' },
          { name: 'arbitrated_at', readonly: true, label: 'Ruling Issued' },
          { name: 'resolution', readonly: true, label: 'Final Resolution', type: 'text' },
          { name: 'state', readonly: true, label: 'Docket Status' }
        ] }
    ]
  },
  'M40-form-franchise': { kind: 'model_form', model: 'fix.partner.franchise',
    title: 'Franchise Agreement', back: 'M40-franchise',
    lines: {
      field: 'territory_ids', readonlyGrid: true,
      title: 'Territories',
      note: 'Territories are drafted and activated on the Franchise Territories screen, where exclusivity is checked (BRU-PCM-16).',
      fields: [
        { name: 'code', label: 'Code', readonly: true },
        { name: 'name', label: 'Territory', readonly: true },
        { name: 'districts', label: 'Districts', readonly: true },
        { name: 'exclusivity', label: 'Exclusivity', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ]
    },
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'audit', label: '5. System Audit', bn: '৫. সিস্টেম অডিট' },
      { id: 'docs', label: '6. Documents', bn: '৬. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Agreement Name', required: true },
        { name: 'territory', label: 'Territory', required: true },
        { name: 'state', label: 'State', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', note: 'Royalties are computed from the verified service-order settlements of the branch operating unit named here (BRU-PCM-17); the rates freeze when the agreement is activated.', fields: [
        { name: 'fee', label: 'Franchise Fee' },
        { name: 'operating_unit_id', label: 'Franchise Branch (Operating Unit)' },
        { name: 'royalty_rate', label: 'Royalty Rate (fraction of revenue)' },
        { name: 'marketing_levy_rate', label: 'Marketing Levy Rate (fraction)' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'start_date', label: 'Start Date', required: true },
        { name: 'end_date', label: 'End Date' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M40-form-auth': { kind: 'model_form', model: 'fix.partner.authorisation',
    title: 'Partner Authorisation', back: 'M40-authorisation',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'scope', label: 'Scope' },
        { name: 'state', label: 'State', readonly: true },
        { name: 'certificate_ref', label: 'Certificate Ref' },
        { name: 'certificate_attachment_id', label: 'Certificate Document' },
        { name: 'activated_by_id', label: 'Activated By', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'valid_from', label: 'Valid From', required: true },
        { name: 'valid_to', label: 'Valid To', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'brand_id', label: 'Brand' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },
  'M40-form-referral': { kind: 'model_form', model: 'fix.referral',
    title: 'Partner Referral', back: 'M40-referral',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'audit', label: '6. System Audit', bn: '৬. সিস্টেম অডিট' },
      { id: 'docs', label: '7. Documents', bn: '৭. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', required: true },
        // A04 audit 2026-11-04: the referral state moves only through its
        // lifecycle (fix.referral is A08's model); the form never writes it.
        { name: 'state', label: 'State', readonly: true },
        { name: 'payout_state', label: 'Payout State', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'base_amount', readonly: true, label: 'Referred Revenue (Gross)' },
        { name: 'commission_amount', label: 'Commission Earned', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'partner_id', label: 'Referring Partner', required: true },
        { name: 'referred_partner_id', label: 'Referred Customer' },
        { name: 'consent_given', label: 'Customer Consent Recorded (BRU-PCM-06)' },
        { name: 'consent_method', label: 'How Consent Was Given' },
        { name: 'referred_on', label: 'Referred On (attribution window start)', readonly: true },
        { name: 'commission_rate', label: 'Commission Rate Earned', readonly: true },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'commission_ledger_id', label: 'Commission Ledger Entry', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  /* A04 audit M40-2: the technical audit behind the 85% rebate gate. */
  'M40-form-audit': { kind: 'model_form', model: 'fix.partner.audit',
    title: 'Partner Technical Audit', back: 'M40-audits',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Audit', bn: '১. অডিট' },
      { id: 'decision', label: '2. Approval', bn: '২. অনুমোদন' }
    ],
    sections: [
      { tab: 'general', title: '1. Audit', note: 'The score counts for the rebate gate once a channel manager other than the auditor approves it, for 365 days.', fields: [
        { name: 'name', label: 'Audit Number', readonly: true },
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'audit_date', label: 'Audit Date', required: true },
        { name: 'score', label: 'Audit Score (%)', required: true },
        { name: 'findings', label: 'Findings', type: 'text' },
        { name: 'evidence_attachment_id', label: 'Audit Report' }
      ] },
      { tab: 'decision', title: '2. Approval', fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'auditor_id', label: 'Auditor', readonly: true },
        { name: 'approved_by_id', label: 'Approved By', readonly: true },
        { name: 'valid_until', label: 'Valid Until', readonly: true },
        { name: 'rejection_reason', label: 'Rejection Reason', readonly: true }
      ] }
    ] },

  /* ============ M40 capture audit (19 Nov 2026) ============
   * Each sub-module page captures the record the spec puts on it (M40 §5,
   * §10.1). States, stamps and computed figures are read-only: they move
   * through the list actions, which the server checks for role, evidence
   * and segregation of duties. */
  'M40-programmes': { kind: 'model_list', model: 'fix.partner.programme', stateField: 'state',
    cols: ['code', 'name', 'partner_type', 'version', 'valid_from', 'partner_count', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish Programme', states: ['draft'] },
      { m: 'action_new_version', l: 'Draft New Version', states: ['published', 'superseded'] },
      { m: 'action_retire', l: 'Retire Programme', ask: 'Reason for retiring', kwarg: 'reason', states: ['published', 'superseded'] }
    ] },
  /* A04 ERP audit M40-F5: a proposed commission rate. It is decided by a
   * DOFA Tier 3 approver from the M63 inbox (routed), never here. */
  'M40-rate-changes': { kind: 'model_list', model: 'fix.partner.rate.change', stateField: 'state',
    cols: ['partner_id', 'current_rate', 'proposed_rate', 'approval_state', 'applied_by_id', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval (Tier 3)', ask: 'Justification for the new rate', kwarg: 'justification', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['draft'] },
      { m: 'action_cancel', l: 'Cancel Proposal', states: ['draft'] }
    ] },
  /* A04 ERP audit M40-F16: each draw's stock move and M20 invoice (raised by
   * Record Draw on the allocation; read only, so the list has no + New). */
  'M40-draws': { kind: 'model_list', model: 'fix.reseller.draw', create: false,
    cols: ['allocation_id', 'partner_id', 'sequence', 'qty', 'unit_price', 'move_id', 'invoice_id'] },
  'M40-contacts': { kind: 'model_list', model: 'fix.partner.contact.role',
    cols: ['partner_id', 'contact_id', 'role', 'portal_scope', 'primary', 'email', 'phone'] },
  'M40-onboarding': { kind: 'model_list', model: 'fix.partner.onboarding', stateField: 'state',
    cols: ['partner_id', 'step', 'name', 'required', 'evidence_attachment_id', 'completed_by_id', 'state'],
    actions: [
      { m: 'action_complete', l: 'Complete Step (on evidence)', states: ['pending'] },
      { m: 'action_waive', l: 'Waive Optional Step', ask: 'Reason for waiving', kwarg: 'reason', states: ['pending'] }
    ] },
  'M40-enablement': { kind: 'model_list', model: 'fix.partner.enablement', stateField: 'state',
    cols: ['partner_id', 'course', 'required', 'completed_on', 'certification_ref', 'expires_on', 'state'],
    actions: [
      { m: 'action_certify', l: 'Record Certification', states: ['assigned'] }
    ] },
  'M40-obligations': { kind: 'model_list', model: 'fix.brand.obligation', stateField: 'state',
    cols: ['authorisation_id', 'brand_id', 'obligation_type', 'due_date', 'recurrence', 'owner_id', 'state'],
    actions: [
      { m: 'action_mark_met', l: 'Mark Met (on evidence)', states: ['open', 'overdue'] }
    ] },
  'M40-brand-audits': { kind: 'model_list', model: 'fix.brand.audit', stateField: 'state',
    cols: ['name', 'brand_id', 'scheduled_on', 'conducted_on', 'm23_ref', 'closed_by_id', 'state'],
    actions: [
      { m: 'action_record_findings', l: 'Record Findings', states: ['scheduled'] },
      { m: 'action_respond', l: 'Submit Response', states: ['conducted'] },
      { m: 'action_close', l: 'Close Audit', states: ['responded'] }
    ] },
  'M40-engagement': { kind: 'model_list', model: 'fix.partner.engagement',
    cols: ['date', 'partner_id', 'engagement_type', 'direction', 'participants', 'commitment_due', 'logged_by_id'] },
  'M40-schemes': { kind: 'model_list', model: 'fix.alliance.scheme', stateField: 'state',
    cols: ['code', 'name', 'partner_id', 'eligibility_method', 'valid_from', 'valid_to', 'volume_commitment', 'eligible_count', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Scheme', states: ['draft'] },
      { m: 'action_close', l: 'Close Scheme', ask: 'Reason for closing', kwarg: 'reason', states: ['active'] }
    ] },
  'M40-eligibility': { kind: 'model_list', model: 'fix.alliance.eligibility.check',
    cols: ['checked_at', 'scheme_id', 'member_ref', 'customer_id', 'result', 'evidence_ref', 'checked_by_id'] },
  'M40-referral-links': { kind: 'model_list', model: 'fix.referral.link', stateField: 'state',
    cols: ['code', 'partner_id', 'campaign_ref', 'valid_from', 'valid_to', 'lead_count', 'state'],
    actions: [
      { m: 'action_revoke', l: 'Revoke Link', ask: 'Reason for revoking', kwarg: 'reason', states: ['active'] }
    ] },
  'M40-leads': { kind: 'model_list', model: 'fix.partner.lead', stateField: 'state',
    cols: ['name', 'partner_id', 'customer_name', 'customer_phone', 'attribution_expires_on', 'attribution_lapsed', 'referral_id', 'state'],
    actions: [
      { m: 'action_qualify', l: 'Qualify Lead', states: ['submitted'] },
      { m: 'action_convert', l: 'Convert (attribution check)', states: ['qualified'] },
      { m: 'action_mark_lost', l: 'Mark Lost', ask: 'Reason the lead was lost (the partner sees it)', kwarg: 'reason', states: ['submitted', 'qualified'] }
    ] },
  'M40-conflict-rules': { kind: 'model_list', model: 'fix.channel.conflict.rule', stateField: 'state',
    cols: ['name', 'territory', 'precedence', 'valid_from', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Rule (CCO)', states: ['draft'] },
      { m: 'action_retire', l: 'Retire Rule', ask: 'Reason for retiring', kwarg: 'reason', states: ['active'] }
    ] },
  'M40-allocations': { kind: 'model_list', model: 'fix.reseller.allocation', stateField: 'state',
    cols: ['name', 'partner_id', 'allocation_type', 'item_description', 'period', 'qty', 'consumed_qty', 'remaining_qty', 'state'],
    actions: [
      { m: 'action_allocate', l: 'Confirm Allocation', states: ['draft'] },
      { m: 'action_record_draw', l: 'Record Draw', ask: 'Quantity the reseller drew', kwarg: 'qty', states: ['allocated'] },
      { m: 'action_close', l: 'Close Allocation', states: ['allocated'] }
    ] },
  'M40-territories': { kind: 'model_list', model: 'fix.franchise.territory', stateField: 'state',
    cols: ['code', 'name', 'partner_id', 'districts', 'exclusivity', 'valid_from', 'valid_to', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate (overlap check)', states: ['draft'] },
      { m: 'action_retire', l: 'Retire Territory', ask: 'Reason for retiring', kwarg: 'reason', states: ['active'] }
    ] },
  'M40-royalties': { kind: 'model_list', model: 'fix.franchise.royalty', stateField: 'state',
    cols: ['franchise_id', 'partner_id', 'period_from', 'period_to', 'order_count', 'revenue_basis', 'royalty_amount', 'levy_amount', 'state'],
    actions: [
      { m: 'action_compute', l: 'Compute from ERP Revenue', states: ['draft'] },
      /* A04 ERP audit M40-F1: raises the draft M20 invoice (royalty + levy, VAT by M51) */
      { m: 'action_raise_invoice', l: 'Raise M20 Invoice (Finance)', states: ['computed'] }
    ] },
  'M40-mdf-funds': { kind: 'model_list', model: 'fix.mdf.fund', stateField: 'state',
    cols: ['name', 'partner_id', 'period', 'allocated', 'claimed', 'approved', 'paid', 'balance', 'state'],
    actions: [
      { m: 'action_open', l: 'Allocate Fund', states: ['draft'] },
      { m: 'action_close', l: 'Close Fund', states: ['open'] }
    ] },
  'M40-mdf-claims': { kind: 'model_list', model: 'fix.mdf.claim', stateField: 'state',
    cols: ['name', 'fund_id', 'partner_id', 'campaign_id', 'amount', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit Claim', states: ['draft'] },
      { m: 'action_approve', l: 'Approve & Instruct Payment', states: ['submitted'] },
      { m: 'action_refuse', l: 'Refuse Claim', ask: 'Reason for refusing', kwarg: 'reason', states: ['submitted'] },
      /* A04 ERP audit M40-F3: paid when its M50 payout is executed */
      { m: 'action_record_payment', l: 'Record Payment (Finance)', states: ['approved'] }
    ] },

  'M40-form-programme': { kind: 'model_form', model: 'fix.partner.programme',
    title: 'Partner Programme', back: 'M40-programmes', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Programme', bn: '১. কার্যক্রম', icon: '📘' },
      { id: 'terms', label: '2. Criteria & Benefits', bn: '২. মানদণ্ড ও সুবিধা', icon: '📋' },
      { id: 'approval', label: '3. Version & Approval', bn: '৪. সংস্করণ ও অনুমোদন', icon: '⏱️' }
    ],
    sections: [
      { tab: 'general', title: 'Programme', note: 'Published terms never change: a change is a new version, and each partner stays bound to the version it joined on (BRU-PCM-12).', fields: [
        { name: 'code', label: 'Programme Code', required: true },
        { name: 'name', label: 'Programme Name', required: true },
        { name: 'partner_type', label: 'Partner Type', required: true },
        { name: 'valid_from', label: 'Effective From', required: true },
        { name: 'company_id', label: 'Company', required: true }
      ] },
      { tab: 'terms', title: 'Entry, Benefits, Obligations & Exit', fields: [
        { name: 'entry_criteria', label: 'Entry Criteria', type: 'text', required: true },
        { name: 'benefits', label: 'Benefits', type: 'text' },
        { name: 'obligations', label: 'Obligations', type: 'text' },
        { name: 'commercial_terms_ref', label: 'Commercial Terms (M11 rate reference; M53 pays)' },
        { name: 'exit_conditions', label: 'Exit Conditions', type: 'text' }
      ] },
      { tab: 'approval', title: 'Version & Approval', fields: [
        { name: 'version', label: 'Version', readonly: true },
        { name: 'previous_id', label: 'Previous Version', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'published_by_id', label: 'Published By', readonly: true },
        { name: 'published_at', label: 'Published On', readonly: true }
      ] }
    ],
    lines: {
      field: 'tier_ids',
      title: 'Programme Tiers',
      note: 'A programme is published with at least one tier; tiers change only while it is a draft (BRU-PCM-12).',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'code', label: 'Tier Code' },
        { name: 'name', label: 'Tier' },
        { name: 'criteria', label: 'Criteria' },
        { name: 'benefits', label: 'Benefits' },
        { name: 'commission_ref', label: 'Commission (M11)' },
        { name: 'notice_days', label: 'Notice (days)' }
      ]
    } },
  'M40-form-rate-change': { kind: 'model_form', model: 'fix.partner.rate.change',
    title: 'Commission Rate Change', back: 'M40-rate-changes', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Proposed Rate', bn: '১. প্রস্তাবিত হার', icon: '📈' },
      { id: 'decision', label: '2. Decision', bn: '২. সিদ্ধান্ত', icon: '✅' }
    ],
    sections: [
      { tab: 'general', title: 'Proposal (A04 ERP M40-F5)', note: 'Takes effect only when a DOFA Tier 3 approver other than the proposer approves it from the M63 inbox.', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'current_rate', label: 'Rate Before', readonly: true },
        { name: 'proposed_rate', label: 'Proposed Rate (fraction, 0.05 = 5%)', required: true },
        { name: 'dofa_justification', label: 'Justification', type: 'text' }
      ] },
      { tab: 'decision', title: 'Routed Decision', fields: [
        { name: 'approval_state', label: 'Approval', readonly: true },
        { name: 'dofa_approved_by', label: 'Approved By', readonly: true },
        { name: 'applied_by_id', label: 'Applied By', readonly: true },
        { name: 'applied_at', label: 'Applied On', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ] }
    ] },
  'M40-form-draw': { kind: 'model_form', model: 'fix.reseller.draw',
    title: 'Reseller Draw', back: 'M40-draws', create: false, pick: true,
    tabs: [
      { id: 'general', label: '1. Draw', bn: '১. উত্তোলন', icon: '📦' }
    ],
    sections: [
      { tab: 'general', title: 'Draw (A04 ERP M40-F16)', note: 'Raised by Record Draw on the allocation: the stock move and the draft M20 invoice at the M11 reseller price.', fields: [
        { name: 'allocation_id', label: 'Allocation', readonly: true },
        { name: 'partner_id', label: 'Reseller', readonly: true },
        { name: 'sequence', label: 'Draw No', readonly: true },
        { name: 'qty', label: 'Quantity', readonly: true },
        { name: 'unit_price', label: 'Unit Price (M11)', readonly: true },
        { name: 'move_id', label: 'Stock Move (M15)', readonly: true },
        { name: 'invoice_id', label: 'Invoice (M20)', readonly: true }
      ] }
    ] },
  'M40-form-contact': { kind: 'model_form', model: 'fix.partner.contact.role',
    title: 'Partner Contact', back: 'M40-contacts',
    tabs: [
      { id: 'general', label: '1. Contact & Role', bn: '১. যোগাযোগ ও ভূমিকা', icon: '👤' }
    ],
    sections: [
      { tab: 'general', title: 'Named Contact (FR-PCM-009)', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'contact_id', label: 'Contact Person (M33)', required: true },
        { name: 'role', label: 'Role', required: true },
        { name: 'primary', label: 'Primary for this Role' },
        { name: 'portal_scope', label: 'P12 Portal Scope', required: true },
        { name: 'active', label: 'Active' },
        { name: 'email', label: 'E-mail', readonly: true },
        { name: 'phone', label: 'Phone', readonly: true }
      ] }
    ] },
  'M40-form-onboarding': { kind: 'model_form', model: 'fix.partner.onboarding',
    title: 'Onboarding Step', back: 'M40-onboarding', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Step', bn: '১. ধাপ', icon: '✅' },
      { id: 'decision', label: '2. Completion', bn: '২. সম্পন্ন', icon: '🔒' }
    ],
    sections: [
      { tab: 'general', title: 'Checklist Step', note: 'A required step is completed on its evidence (upload it on this record, then pick it) and is never waived; the partner is onboarded only once every required step is done (BRU-PCM-01).', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'step', label: 'Step', required: true },
        { name: 'name', label: 'Description', required: true },
        { name: 'required', label: 'Required' },
        { name: 'sequence', label: 'Order' },
        { name: 'evidence_attachment_id', label: 'Evidence' },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'decision', title: 'Completion', fields: [
        { name: 'state', label: 'Status', readonly: true },
        { name: 'completed_by_id', label: 'Completed By', readonly: true },
        { name: 'completed_at', label: 'Completed On', readonly: true },
        { name: 'waived_by_id', label: 'Waived By', readonly: true },
        { name: 'waive_reason', label: 'Waiver Reason', readonly: true }
      ] }
    ] },
  'M40-form-enablement': { kind: 'model_form', model: 'fix.partner.enablement',
    title: 'Partner Enablement & Certification', back: 'M40-enablement', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Course', bn: '১. কোর্স', icon: '🎓' },
      { id: 'cert', label: '2. Certification', bn: '২. সনদ', icon: '📜' }
    ],
    sections: [
      { tab: 'general', title: 'Assigned Course', note: 'A required certification gates the partner\'s rebates and MDF (FR-PCM-041).', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'course', label: 'Course / Certification', required: true },
        { name: 'required', label: 'Required for Benefits' },
        { name: 'assigned_on', label: 'Assigned On', required: true }
      ] },
      { tab: 'cert', title: 'Certification', fields: [
        { name: 'completed_on', label: 'Completed On' },
        { name: 'certification_ref', label: 'Certificate Number' },
        { name: 'certificate_attachment_id', label: 'Certificate' },
        { name: 'expires_on', label: 'Expires On' },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'certified_by_id', label: 'Recorded By', readonly: true }
      ] }
    ] },
  'M40-form-obligation': { kind: 'model_form', model: 'fix.brand.obligation',
    title: 'Brand Obligation', back: 'M40-obligations', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Obligation', bn: '১. দায়বদ্ধতা', icon: '📌' },
      { id: 'evidence', label: '2. Evidence', bn: '২. প্রমাণ', icon: '📎' }
    ],
    sections: [
      { tab: 'general', title: 'Obligation under the Authorisation (FR-PCM-017)', fields: [
        { name: 'authorisation_id', label: 'Brand Authorisation', required: true },
        { name: 'obligation_type', label: 'Type', required: true },
        { name: 'description', label: 'What Is Owed', type: 'text', required: true },
        { name: 'due_date', label: 'Due Date', required: true },
        { name: 'recurrence', label: 'Recurrence', required: true },
        { name: 'owner_id', label: 'Owner' },
        { name: 'brand_id', label: 'Brand', readonly: true }
      ] },
      { tab: 'evidence', title: 'Evidence', fields: [
        { name: 'evidence_attachment_id', label: 'Evidence' },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'met_by_id', label: 'Met By', readonly: true },
        { name: 'met_at', label: 'Met On', readonly: true }
      ] }
    ] },
  'M40-form-brand-audit': { kind: 'model_form', model: 'fix.brand.audit',
    title: 'Brand Partner Audit', back: 'M40-brand-audits', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Schedule', bn: '১. সময়সূচি', icon: '🗓️' },
      { id: 'findings', label: '2. Findings & Response', bn: '২. ফলাফল ও জবাব', icon: '📝' },
      { id: 'closure', label: '3. Closure', bn: '৩. সমাপ্তি', icon: '🔒' }
    ],
    sections: [
      { tab: 'general', title: 'Audit Calendar (FR-PCM-016)', fields: [
        { name: 'name', label: 'Audit', required: true },
        { name: 'brand_id', label: 'Brand', required: true },
        { name: 'authorisation_id', label: 'Authorisation Audited' },
        { name: 'scheduled_on', label: 'Scheduled On', required: true },
        { name: 'scope', label: 'Scope', type: 'text', required: true },
        { name: 'auditor_name', label: 'Brand Auditor' }
      ] },
      { tab: 'findings', title: 'Findings & Response', fields: [
        { name: 'conducted_on', label: 'Conducted On' },
        { name: 'findings', label: 'Brand\'s Findings', type: 'text' },
        { name: 'response', label: '1000FiX Response', type: 'text' },
        { name: 'm23_ref', label: 'Quality Finding (M23)' }
      ] },
      { tab: 'closure', title: 'Closure', fields: [
        { name: 'state', label: 'Status', readonly: true },
        { name: 'closed_by_id', label: 'Closed By', readonly: true },
        { name: 'closed_on', label: 'Closed On', readonly: true }
      ] }
    ] },
  'M40-form-engagement': { kind: 'model_form', model: 'fix.partner.engagement',
    title: 'Partner Engagement', back: 'M40-engagement',
    tabs: [
      { id: 'general', label: '1. Engagement', bn: '১. যোগাযোগ', icon: '🤝' },
      { id: 'commit', label: '2. Commitments', bn: '২. প্রতিশ্রুতি', icon: '📌' }
    ],
    sections: [
      { tab: 'general', title: 'Engagement Log (append-only)', note: 'An entry is never edited once logged, so a brand\'s own assessment of 1000FiX stays verbatim (BRU-PCM-20).', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'engagement_type', label: 'Type', required: true },
        { name: 'direction', label: 'Direction', required: true },
        { name: 'date', label: 'Date', required: true },
        { name: 'participants', label: 'Participants' },
        { name: 'summary', label: 'Summary / Verbatim Assessment', type: 'text', required: true },
        { name: 'logged_by_id', label: 'Logged By', readonly: true }
      ] },
      { tab: 'commit', title: 'Commitments', fields: [
        { name: 'commitments', label: 'Commitments Made', type: 'text' },
        { name: 'commitment_due', label: 'Due By' },
        { name: 'attachment_id', label: 'Document' }
      ] }
    ] },
  'M40-form-scheme': { kind: 'model_form', model: 'fix.alliance.scheme',
    title: 'Alliance Scheme', back: 'M40-schemes', status: { field: 'state' },
    lines: {
      field: 'check_ids', readonlyGrid: true,
      title: 'Eligibility Checks',
      note: 'Recorded at intake on the Eligibility Checks screen; a check is a log entry and never edited.',
      fields: [
        { name: 'checked_at', label: 'Checked On', readonly: true },
        { name: 'member_ref', label: 'Member', readonly: true },
        { name: 'result', label: 'Result', readonly: true },
        { name: 'checked_by_id', label: 'Checked By', readonly: true }
      ]
    },
    tabs: [
      { id: 'general', label: '1. Scheme', bn: '১. স্কিম', icon: '🤝' },
      { id: 'benefit', label: '2. Members & Benefit', bn: '২. সদস্য ও সুবিধা', icon: '🎁' },
      { id: 'volume', label: '3. Commitment', bn: '৩. প্রতিশ্রুতি', icon: '📈' }
    ],
    sections: [
      { tab: 'general', title: 'Alliance Scheme (FR-PCM-030)', fields: [
        { name: 'code', label: 'Scheme Code', required: true },
        { name: 'name', label: 'Scheme Name', required: true },
        { name: 'partner_id', label: 'Alliance Partner', required: true },
        { name: 'valid_from', label: 'Valid From', required: true },
        { name: 'valid_to', label: 'Valid To' },
        { name: 'company_id', label: 'Company', required: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'activated_by_id', label: 'Activated By', readonly: true }
      ] },
      { tab: 'benefit', title: 'Members & Benefit', note: 'The benefit is applied by the M11 rule named here, never as an ad-hoc discount (BRU-PCM-19).', fields: [
        { name: 'member_definition', label: 'Member Base', type: 'text', required: true },
        { name: 'eligibility_method', label: 'Validation Method', required: true },
        { name: 'benefit_description', label: 'Benefit', type: 'text', required: true },
        { name: 'benefit_ref', label: 'M11 Benefit Rule' }
      ] },
      { tab: 'volume', title: 'Volume Commitment (FR-PCM-032)', fields: [
        { name: 'volume_commitment', label: 'Committed Volume (jobs)' },
        { name: 'eligible_count', label: 'Eligible Members Served', readonly: true },
        { name: 'commitment_pct', label: 'Commitment Achieved (%)', readonly: true }
      ] }
    ] },
  'M40-form-eligibility': { kind: 'model_form', model: 'fix.alliance.eligibility.check',
    title: 'Alliance Eligibility Check', back: 'M40-eligibility',
    tabs: [
      { id: 'general', label: '1. Validation', bn: '১. যাচাই', icon: '🪪' }
    ],
    sections: [
      { tab: 'general', title: 'Member Validation at Intake (FR-PCM-031)', note: 'Only an active scheme inside its validity validates; the check is a log entry and is never edited.', fields: [
        { name: 'scheme_id', label: 'Alliance Scheme', required: true },
        { name: 'member_ref', label: 'Member ID / Proof', required: true },
        { name: 'customer_id', label: 'Customer (M33)' },
        { name: 'result', label: 'Result', required: true },
        { name: 'evidence_ref', label: 'How It Was Validated', required: true },
        { name: 'evidence_attachment_id', label: 'Evidence' },
        { name: 'checked_at', label: 'Checked On', readonly: true },
        { name: 'checked_by_id', label: 'Checked By', readonly: true }
      ] }
    ] },
  'M40-form-link': { kind: 'model_form', model: 'fix.referral.link',
    title: 'Referral Link / Code', back: 'M40-referral-links', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Link', bn: '১. লিংক', icon: '🔗' }
    ],
    sections: [
      { tab: 'general', title: 'Referral Code (FR-PCM-022)', note: 'The code is generated on save: unique, non-guessable and revocable (T-07).', fields: [
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'campaign_ref', label: 'Campaign' },
        { name: 'valid_from', label: 'Valid From', required: true },
        { name: 'valid_to', label: 'Valid To' },
        { name: 'company_id', label: 'Company', required: true },
        { name: 'code', label: 'Code', readonly: true },
        { name: 'url_path', label: 'Link Path', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'revoke_reason', label: 'Revocation Reason', readonly: true }
      ] }
    ] },
  'M40-form-lead': { kind: 'model_form', model: 'fix.partner.lead',
    title: 'Partner Lead', back: 'M40-leads', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Lead', bn: '১. লিড', icon: '📨' },
      { id: 'consent', label: '2. Customer Consent', bn: '২. গ্রাহকের সম্মতি', icon: '✍️' },
      { id: 'attribution', label: '3. Attribution & Outcome', bn: '৩. অ্যাট্রিবিউশন', icon: '🎯' }
    ],
    sections: [
      { tab: 'general', title: 'Submitted Lead (FR-PCM-023)', fields: [
        { name: 'name', label: 'Lead Number', readonly: true },
        { name: 'partner_id', label: 'Referring Partner', required: true },
        { name: 'link_id', label: 'Referral Link' },
        { name: 'customer_name', label: 'Customer Name', required: true },
        { name: 'customer_phone', label: 'Customer Phone', required: true },
        { name: 'customer_email', label: 'Customer E-mail' },
        { name: 'service_interest', label: 'Service Interest' },
        { name: 'customer_id', label: 'Customer Party (M33, at conversion)' },
        { name: 'company_id', label: 'Company', required: true }
      ] },
      { tab: 'consent', title: 'Customer Consent (BRU-PCM-06)', note: 'No consent, no lead: the record is refused before it is created (PDPA).', fields: [
        { name: 'consent_given', label: 'Customer Consent Recorded', required: true },
        { name: 'consent_method', label: 'How Consent Was Given', required: true },
        { name: 'consent_at', label: 'Consent Given At' },
        { name: 'consent_attachment_id', label: 'Consent Evidence' }
      ] },
      { tab: 'attribution', title: 'Attribution (written once, BRU-PCM-04/05)', fields: [
        { name: 'attributed_at', label: 'Attributed On', readonly: true },
        { name: 'attribution_window_days', label: 'Window (days)', readonly: true },
        { name: 'attribution_expires_on', label: 'Window Closes', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'converted_at', label: 'Converted On', readonly: true },
        { name: 'attribution_lapsed', label: 'Converted Outside Window', readonly: true },
        { name: 'referral_id', label: 'Commission Referral', readonly: true },
        { name: 'loss_reason', label: 'Loss Reason', readonly: true }
      ] }
    ] },
  'M40-form-conflict-rule': { kind: 'model_form', model: 'fix.channel.conflict.rule',
    title: 'Channel Precedence Rule', back: 'M40-conflict-rules', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Rule', bn: '১. নিয়ম', icon: '⚖️' },
      { id: 'order', label: '2. Precedence', bn: '২. অগ্রাধিকার', icon: '🔢' }
    ],
    sections: [
      { tab: 'general', title: 'Declared Rule (BRU-PCM-10)', note: 'Activated by a Tier 3 officer (CCO) who did not draft it; one active rule per territory.', fields: [
        { name: 'name', label: 'Rule', required: true },
        { name: 'scope', label: 'Scope', type: 'text', required: true },
        { name: 'territory', label: 'Territory (blank = national)' },
        { name: 'valid_from', label: 'Effective From', required: true },
        { name: 'company_id', label: 'Company', required: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'approved_by_id', label: 'Activated By', readonly: true }
      ] },
      { tab: 'order', title: 'Channel Precedence (FR-PCM-029)', fields: [
        { name: 'first_channel', label: '1st', required: true },
        { name: 'second_channel', label: '2nd', required: true },
        { name: 'third_channel', label: '3rd' },
        { name: 'fourth_channel', label: '4th' },
        { name: 'fifth_channel', label: '5th' },
        { name: 'precedence', label: 'Resulting Order', readonly: true }
      ] }
    ] },
  'M40-form-allocation': { kind: 'model_form', model: 'fix.reseller.allocation',
    title: 'Reseller Allocation', back: 'M40-allocations', status: { field: 'state' },
    lines: {
      field: 'draw_ids', readonlyGrid: true,
      title: 'Draws',
      note: 'Each draw is recorded by Record Draw: it moves the stock and raises the draft M20 invoice at the M11 price (A04 ERP M40-F16).',
      fields: [
        { name: 'sequence', label: 'Draw No', readonly: true },
        { name: 'qty', label: 'Quantity', readonly: true },
        { name: 'unit_price', label: 'Unit Price', readonly: true },
        { name: 'move_id', label: 'Stock Move', readonly: true },
        { name: 'invoice_id', label: 'Invoice', readonly: true }
      ]
    },
    tabs: [
      { id: 'general', label: '1. Allocation', bn: '১. বরাদ্দ', icon: '📦' },
      { id: 'usage', label: '2. Drawn & Status', bn: '২. ব্যবহার', icon: '📊' }
    ],
    sections: [
      { tab: 'general', title: 'Allocation (FR-PCM-033)', fields: [
        { name: 'name', label: 'Allocation', readonly: true },
        { name: 'partner_id', label: 'Reseller', required: true },
        { name: 'allocation_type', label: 'Type', required: true },
        { name: 'item_description', label: 'Item / Capacity', required: true },
        { name: 'item_ref', label: 'Lot Reference (M14/M15)' },
        { name: 'product_id', label: 'Item (priced by M11)', required: true },
        { name: 'location_id', label: 'Draw From (M15 location, stock only)' },
        { name: 'qty', label: 'Allocated Quantity', required: true },
        { name: 'period', label: 'Period', required: true },
        { name: 'unit_price', label: 'Agreed Unit Price (M11 reseller price)', readonly: true },
        { name: 'price_source', label: 'Price Source (M11)', readonly: true },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'company_id', label: 'Company', required: true }
      ] },
      { tab: 'usage', title: 'Drawn & Status', fields: [
        { name: 'consumed_qty', label: 'Drawn', readonly: true },
        { name: 'remaining_qty', label: 'Remaining', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'allocated_by_id', label: 'Allocated By', readonly: true }
      ] }
    ] },
  'M40-form-territory': { kind: 'model_form', model: 'fix.franchise.territory',
    title: 'Franchise Territory', back: 'M40-territories', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Territory', bn: '১. অঞ্চল', icon: '🗺️' }
    ],
    sections: [
      { tab: 'general', title: 'Territory (FR-PCM-035)', note: 'An exclusive territory may not share a district with another active territory in the same period (BRU-PCM-16).', fields: [
        { name: 'code', label: 'Territory Code', required: true },
        { name: 'name', label: 'Territory', required: true },
        { name: 'districts', label: 'Districts (comma-separated)', required: true },
        { name: 'exclusivity', label: 'Exclusivity', required: true },
        { name: 'partner_id', label: 'Franchisee', required: true },
        { name: 'franchise_id', label: 'Franchise Agreement' },
        { name: 'valid_from', label: 'Valid From', required: true },
        { name: 'valid_to', label: 'Valid To' },
        { name: 'company_id', label: 'Company', required: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'approved_by_id', label: 'Activated By', readonly: true }
      ] }
    ] },
  'M40-form-royalty': { kind: 'model_form', model: 'fix.franchise.royalty',
    title: 'Franchise Royalty', back: 'M40-royalties', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Period', bn: '১. সময়কাল', icon: '🗓️' },
      { id: 'computed', label: '2. Computed from ERP', bn: '২. হিসাব', icon: '🧮' }
    ],
    sections: [
      { tab: 'general', title: 'Royalty Period (FR-PCM-036)', note: 'The basis is the verified settlements of the franchise branch\'s service orders, never the franchisee\'s declaration (BRU-PCM-17).', fields: [
        { name: 'franchise_id', label: 'Franchise Agreement', required: true },
        { name: 'period_from', label: 'Period From', required: true },
        { name: 'period_to', label: 'Period To', required: true },
        { name: 'partner_id', label: 'Franchisee', readonly: true }
      ] },
      { tab: 'computed', title: 'Computed from ERP Revenue', fields: [
        { name: 'order_count', label: 'M20 Invoices Counted', readonly: true },
        { name: 'revenue_basis', label: 'Revenue Basis (ex-VAT, net of credit notes)', readonly: true },
        { name: 'credited_basis', label: 'Credit Notes Netted (ex-VAT)', readonly: true },
        { name: 'royalty_rate', label: 'Royalty Rate', readonly: true },
        { name: 'royalty_amount', label: 'Royalty', readonly: true },
        { name: 'levy_rate', label: 'Marketing Levy Rate', readonly: true },
        { name: 'levy_amount', label: 'Marketing Levy', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'computed_by_id', label: 'Computed By', readonly: true },
        { name: 'invoice_ref', label: 'Royalty Invoice No (M20)', readonly: true },
        { name: 'invoice_id', label: 'Royalty Invoice (M20)', readonly: true }
      ] }
    ] },
  'M40-form-mdf-fund': { kind: 'model_form', model: 'fix.mdf.fund',
    title: 'MDF Fund Allocation', back: 'M40-mdf-funds', status: { field: 'state' },
    lines: {
      field: 'claim_ids', readonlyGrid: true,
      title: 'Claims on this Fund',
      note: 'Claims are raised and decided on the MDF Claims screen; the balance is derived from them (T-09).',
      fields: [
        { name: 'name', label: 'Claim', readonly: true },
        { name: 'amount', label: 'Amount', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'decided_by_id', label: 'Decided By', readonly: true }
      ]
    },
    tabs: [
      { id: 'general', label: '1. Allocation', bn: '১. বরাদ্দ', icon: '💰' },
      { id: 'ledger', label: '2. Fund Ledger', bn: '২. তহবিল খতিয়ান', icon: '📒' }
    ],
    sections: [
      { tab: 'general', title: 'Fund (FR-PCM-039)', fields: [
        { name: 'name', label: 'Fund', required: true },
        { name: 'partner_id', label: 'Partner', required: true },
        { name: 'period', label: 'Period', required: true },
        { name: 'allocated', label: 'Allocated', required: true },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'company_id', label: 'Company', required: true }
      ] },
      { tab: 'ledger', title: 'Derived Ledger (T-09)', fields: [
        { name: 'claimed', label: 'Under Review', readonly: true },
        { name: 'approved', label: 'Approved', readonly: true },
        { name: 'paid', label: 'Paid', readonly: true },
        { name: 'balance', label: 'Balance', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'allocated_by_id', label: 'Allocated By', readonly: true }
      ] }
    ] },
  'M40-form-mdf-claim': { kind: 'model_form', model: 'fix.mdf.claim',
    title: 'MDF Claim', back: 'M40-mdf-claims', status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Claim', bn: '১. দাবি', icon: '🧾' },
      { id: 'decision', label: '2. Decision & Payment', bn: '২. সিদ্ধান্ত ও পরিশোধ', icon: '⚖️' }
    ],
    sections: [
      { tab: 'general', title: 'Claim on Evidence (BRU-PCM-11)', note: 'Decided by a manager who neither allocated the fund nor raised the claim.', fields: [
        { name: 'name', label: 'Claim', readonly: true },
        { name: 'fund_id', label: 'MDF Fund', required: true },
        { name: 'campaign_id', label: 'Campaign (M35)' },
        { name: 'amount', label: 'Amount', required: true },
        { name: 'description', label: 'Activity Delivered', type: 'text', required: true },
        { name: 'evidence_attachment_id', label: 'Proof of Execution' },
        { name: 'partner_id', label: 'Partner', readonly: true }
      ] },
      { tab: 'decision', title: 'Decision & Payment', fields: [
        { name: 'state', label: 'Status', readonly: true },
        { name: 'submitted_by_id', label: 'Submitted By', readonly: true },
        { name: 'decided_by_id', label: 'Decided By', readonly: true },
        { name: 'decided_at', label: 'Decided On', readonly: true },
        { name: 'refusal_reason', label: 'Refusal Reason', readonly: true },
        { name: 'payment_ref', label: 'Payment Reference', readonly: true }
      ] }
    ] },

  /* computed pack that had no screen (closure 2026-10-28) */
  'M40-rpt-deals': { kind: 'table_report', module: 'M40', report: 'deal_register', title: "Deal Register", period: false },
};

export const REPORT_ROUTES = {
  'M40:Deal Register': 'M40-rpt-deals',
  'M40:Partner Revenue Contribution': 'M40-rpt-revenue',
  'M40:Referral Conversion': 'M40-rpt-referral',
  'M40:Brand Audit Calendar': 'M40-rpt-audits',
  'M40:Rebate Accruals': 'M40-rpt-rebates',
  'M40:Channel Conflict Log': 'M40-rpt-conflict'
};

export const FORM_MODELS = {
  'M40:Partner': 'fix.partner',
  'M40:Deal Registration': 'fix.partner.deal',
  'M40:Rebate Scheme': 'fix.partner.rebate',
  'M40:Franchise Agreement': 'fix.partner.franchise'
};

export const FORM_CHIPS = {
  'M40:Partner Authorisation': 'M40-form-auth',
  'M40:Referral': 'M40-form-referral',
  'M40:Partner': 'M40-form-partner',
  'M40:Deal Registration': 'M40-form-deal',
  'M40:Rebate Scheme': 'M40-form-rebate',
  'M40:Franchise Agreement': 'M40-form-franchise',
  'M40:Channel Conflict': 'M40-form-conflict',
  'M40:Technical Audit': 'M40-form-audit',
  'M40:Partner Programme': 'M40-form-programme',
  'M40:Partner Contact': 'M40-form-contact',
  'M40:Commission Rate Change': 'M40-form-rate-change',
  'M40:Reseller Draw': 'M40-form-draw',
  'M40:Onboarding Step': 'M40-form-onboarding',
  'M40:Partner Enablement': 'M40-form-enablement',
  'M40:Brand Obligation': 'M40-form-obligation',
  'M40:Brand Audit': 'M40-form-brand-audit',
  'M40:Partner Engagement': 'M40-form-engagement',
  'M40:Alliance Scheme': 'M40-form-scheme',
  'M40:Eligibility Check': 'M40-form-eligibility',
  'M40:Partner Lead': 'M40-form-lead',
  'M40:Referral Link': 'M40-form-link',
  'M40:Channel Precedence Rule': 'M40-form-conflict-rule',
  'M40:Reseller Allocation': 'M40-form-allocation',
  'M40:Franchise Territory': 'M40-form-territory',
  'M40:Franchise Royalty': 'M40-form-royalty',
  'M40:MDF Fund': 'M40-form-mdf-fund',
  'M40:MDF Claim': 'M40-form-mdf-claim',
  'M40:__by_model__': {
    'fix.partner.authorisation': 'M40-form-auth',
    'fix.referral': 'M40-form-referral',
    'fix.partner': 'M40-form-partner',
    'fix.partner.deal': 'M40-form-deal',
    'fix.partner.rebate': 'M40-form-rebate',
    'fix.partner.franchise': 'M40-form-franchise',
    'fix.partner.conflict': 'M40-form-conflict',
    'fix.partner.audit': 'M40-form-audit',
    'fix.partner.programme': 'M40-form-programme',
    'fix.partner.contact.role': 'M40-form-contact',
    'fix.partner.rate.change': 'M40-form-rate-change',
    'fix.reseller.draw': 'M40-form-draw',
    'fix.partner.onboarding': 'M40-form-onboarding',
    'fix.partner.enablement': 'M40-form-enablement',
    'fix.brand.obligation': 'M40-form-obligation',
    'fix.brand.audit': 'M40-form-brand-audit',
    'fix.partner.engagement': 'M40-form-engagement',
    'fix.alliance.scheme': 'M40-form-scheme',
    'fix.alliance.eligibility.check': 'M40-form-eligibility',
    'fix.partner.lead': 'M40-form-lead',
    'fix.referral.link': 'M40-form-link',
    'fix.channel.conflict.rule': 'M40-form-conflict-rule',
    'fix.reseller.allocation': 'M40-form-allocation',
    'fix.franchise.territory': 'M40-form-territory',
    'fix.franchise.royalty': 'M40-form-royalty',
    'fix.mdf.fund': 'M40-form-mdf-fund',
    'fix.mdf.claim': 'M40-form-mdf-claim'
  },
  'M40:__by_screen__': {
    'M40-authorisation': 'M40-form-auth',
    'M40-referral': 'M40-form-referral',
    'M40-partners': 'M40-form-partner',
    'M40-dealreg': 'M40-form-deal',
    'M40-rebates': 'M40-form-rebate',
    'M40-franchise': 'M40-form-franchise',
    'M40-conflict': 'M40-form-conflict',
    'M40-audits': 'M40-form-audit',
    'M40-programmes': 'M40-form-programme',
    'M40-contacts': 'M40-form-contact',
    'M40-rate-changes': 'M40-form-rate-change',
    'M40-draws': 'M40-form-draw',
    'M40-onboarding': 'M40-form-onboarding',
    'M40-enablement': 'M40-form-enablement',
    'M40-obligations': 'M40-form-obligation',
    'M40-brand-audits': 'M40-form-brand-audit',
    'M40-engagement': 'M40-form-engagement',
    'M40-schemes': 'M40-form-scheme',
    'M40-eligibility': 'M40-form-eligibility',
    'M40-leads': 'M40-form-lead',
    'M40-referral-links': 'M40-form-link',
    'M40-conflict-rules': 'M40-form-conflict-rule',
    'M40-allocations': 'M40-form-allocation',
    'M40-territories': 'M40-form-territory',
    'M40-royalties': 'M40-form-royalty',
    'M40-mdf-funds': 'M40-form-mdf-fund',
    'M40-mdf-claims': 'M40-form-mdf-claim'
  }
};

export const CREATE = {
  M40: { screen: 'M40-form-partner', model: 'fix.partner', label: 'Partner' }
};
