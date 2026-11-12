/** @odoo-module **/
/* A04 · Commercial & Revenue — M12 Marketplace & Sellers (v2 rebuild).
 * Registry-faithful: 5 groups / 15 screens / 5 reports / 4 forms / freg 101.
 * Sellers (2061), orders (2150), quotes, scorecards, statements and disputes
 * are real; listings are the new fix.marketplace.listing. Seller stock
 * (fix.seller.stock) and standards/training (fix.seller.standard and
 * fix.seller.certification) were declared gaps until 12 Nov 2026; the two
 * screens now render the built reports and the records have their own lists. */

export const MODULE = {
  area: 'A04', code: 'M12', en: 'Marketplace & Sellers', title: 'M12 · Marketplace & Sellers',
  bn: 'মার্কেটপ্লেস ও সেলার', icon: '🏪',
  desc: 'Seller KYC and agreements, listings and moderation, job broadcast and bidding, execution oversight, commission and fees, wallets and payouts, ratings, disputes and trust ops.',
  kpis: [
    { l: 'Active Sellers', m: 'active_sellers' },
    { l: 'Job Fill Rate', m: 'job_fill_rate', suffix: '%' },
    { l: 'Marketplace Share', m: 'marketplace_share', src: false, suffix: '%' },
    { l: 'Disputes Open', m: 'disputes_open' },
    { l: 'Payouts MTD', m: 'payouts_mtd' },
    { l: 'Seller NPS', m: 'seller_nps', src: false }
  ],
  groups: [
    { en: 'Marketplace Records', screens: [
      { id: 'M12-marketplace-order', en: "Marketplace Order", bn: "Marketplace Order", t: 'g' },
      { id: 'M12-seller-score', en: "Seller Score", bn: "Seller Score", t: 'g' }
    ]},
    { en: 'Sellers', screens: [
      { id: 'M12-sellers', en: 'Seller Directory', bn: 'সেলার ডিরেক্টরি', t: 'g' },
      { id: 'M12-kyc', en: 'KYC & Approval', bn: 'কেওয়াইসি', t: 'r' },
      { id: 'M12-agreements', en: 'Agreements & Tiers', bn: 'চুক্তি ও টিয়ার', t: 'r' }
    ]},
    { en: 'Supply', screens: [
      { id: 'M12-listings', en: 'Listings & Moderation', bn: 'লিস্টিং', t: 'g' },
      { id: 'M12-stock', en: 'Seller Stock', bn: 'সেলার স্টক', t: 'r' },
      { id: 'M12-stock-positions', en: 'Stock Positions', bn: 'স্টক পজিশন', t: 'g' },
      { id: 'M12-training', en: 'Standards & Training', bn: 'প্রশিক্ষণ', t: 'r' },
      { id: 'M12-certifications', en: 'Seller Certifications', bn: 'সেলার সনদ', t: 'g' },
      { id: 'M12-standards', en: 'Standards Catalogue', bn: 'মানদণ্ড তালিকা', t: 'g' }
    ]},
    { en: 'Job Market', screens: [
      { id: 'M12-broadcast', en: 'Job Broadcast', bn: 'জব ব্রডকাস্ট', t: 'r' },
      { id: 'M12-bids', en: 'Bidding & Award', bn: 'বিডিং', t: 'g' },
      { id: 'M12-oversight', en: 'Execution Oversight', bn: 'তদারকি', t: 'r' }
    ]},
    { en: 'Money', screens: [
      { id: 'M12-commission', en: 'Commission Schemes', bn: 'কমিশন', t: 'r' },
      { id: 'M12-wallet', en: 'Seller Wallets & Payouts', bn: 'ওয়ালেট', t: 'r' },
      { id: 'M12-fees', en: 'Fees & Promotion', bn: 'ফি', t: 'r' }
    ]},
    { en: 'Trust', screens: [
      { id: 'M12-reviews', en: 'Ratings & Reviews', bn: 'রেটিং', t: 'r' },
      { id: 'M12-disputes', en: 'Disputes & Mediation', bn: 'বিরোধ', t: 'g' },
      { id: 'M12-trust', en: 'Fraud & Trust Ops', bn: 'ট্রাস্ট অপস', t: 'r' },
      { id: 'M12-chargebacks', en: 'Chargebacks', bn: 'চার্জব্যাক', t: 'g' }
    ]}
  ],
  reports: ['Supply-Demand Liquidity', 'Fill Rate & Time-to-Accept', 'Commission Revenue', 'Dispute Rate & Outcomes', 'Seller Scorecard Distribution', 'Listing Coverage', 'Seller Stock', 'Standards & Training'],
  forms: ['Seller Application', 'Listing', 'Payout Run', 'Dispute Case', 'Stock Position', 'Seller Certification', 'Seller Standard'],
  cross: ['M01 Service Orders', 'M20 AR', 'M33 Party Master', 'M40 Partners'],
  freg: { src: 101, sub: [
    ['1', 'Seller Registration & KYC', 12, { model: 'fix.marketplace.seller', cols: ['name', 'partner_id', 'trade_license_no', 'tin_number', 'kyc_verified_date'], screens: ['M12-sellers', 'M12-kyc'], reports: [], forms: ['Seller Application'] }],
    ['2', 'Agreements & Tiers', 7, { model: 'fix.marketplace.seller', cols: ['name', 'tier', 'kyc_status', 'cfo_approved', 'rating'], screens: ['M12-agreements', 'M12-sellers'], reports: [], forms: [], create: false }],
    ['3', 'Listings', 9, { model: 'fix.marketplace.listing', cols: ['name', 'state', 'seller_id', 'category_id', 'list_price'], screens: ['M12-listings', 'M12-rpt-listingcoverage'], reports: ['Listing Coverage', 'Seller Stock'], forms: ['Listing', 'Stock Position'] }],
    ['4', 'Job Broadcast & Bidding', 14, { model: 'fix.seller.quote', cols: ['seller_id', 'quoted_price', 'eta_days', 'state'], screens: ['M12-bids', 'M12-broadcast'], reports: ['Supply-Demand Liquidity', 'Fill Rate & Time-to-Accept'], forms: [] }],
    ['5', 'Execution Oversight', 10, { model: 'fix.marketplace.order', cols: ['state'], screens: ['M12-marketplace-order', 'M12-oversight'], reports: ['Fill Rate & Time-to-Accept'], forms: [] }],
    ['6', 'Ratings', 6, { model: 'fix.seller.score', cols: ['seller_id', 'period', 'acceptance_rate', 'on_time_rate', 'review_rating', 'dispute_rate'], screens: ['M12-seller-score', 'M12-reviews'], reports: ['Seller Scorecard Distribution'], forms: [] }],
    ['7', 'Performance Consequences', 6, { model: 'fix.seller.score', cols: ['seller_id', 'period', 'acceptance_rate', 'on_time_rate', 'review_rating', 'dispute_rate'], screens: ['M12-rpt-scorecard'], reports: ['Seller Scorecard Distribution'], forms: [] }],
    ['8', 'Disputes', 9, { model: 'fix.marketplace.dispute', cols: ['name', 'state', 'customer_id', 'seller_id', 'disputed_amount', 'dispute_reason', 'sla_deadline'], screens: ['M12-disputes', 'M12-rpt-dispute'], reports: ['Dispute Rate & Outcomes'], forms: ['Dispute Case'] }],
    ['9', 'Commission & Fees', 10, { model: 'fix.seller.statement', cols: ['seller_partner_id', 'period', 'gross_gmv', 'commission_amount', 'platform_fee'], screens: ['M12-commission', 'M12-fees', 'M12-rpt-commission'], reports: ['Commission Revenue'], forms: [] }],
    ['10', 'Wallet & Payouts', 10, { model: 'fix.seller.statement', cols: ['seller_partner_id', 'period', 'net_payable', 'payout_run_id', 'state'], screens: ['M12-wallet'], reports: ['Commission Revenue'], forms: ['Payout Run'] }],
    ['11', 'Trust & Safety', 8, { model: 'fix.marketplace.seller', cols: ['name', 'tier', 'kyc_status', 'payout_hold', 'rating'], screens: ['M12-trust', 'M12-disputes'], reports: ['Standards & Training', 'Dispute Rate & Outcomes'], forms: ['Seller Certification', 'Seller Standard'], create: false }]
  ] }
};

export const SCREENS = {
  'M12-sellers': { kind: 'model_list', model: 'fix.marketplace.seller', stateField: 'kyc_status',
    cols: ['name', 'partner_id', 'tier', 'kyc_status', 'cfo_approved', 'approval_state', 'rating', 'total_jobs', 'payout_hold'],
    // A04 audit M12-1: KYC is a compliance decision; CFO approval is
    // requested here and granted by a DOFA Tier 4 holder from the M63 inbox
    // (never the KYC reviewer).
    actions: [
      { m: 'action_submit_kyc', l: 'Submit KYC for Review' },
      { m: 'action_verify_kyc', l: 'Verify KYC' },
      { m: 'action_reject_kyc', l: 'Reject KYC', ask: 'Why the KYC is rejected', kwarg: 'reason' },
      { m: 'action_request_approval', l: 'Request CFO Approval', ask: 'Business case for the seller', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall CFO Request' }
    ] },
  'M12-kyc': { kind: 'table_report', module: 'M12', report: 'kyc_queue', title: 'KYC & Approval', period: false },
  'M12-agreements': { kind: 'table_report', module: 'M12', report: 'agreements', title: 'Agreements & Tiers', period: false },
  'M12-listings': { kind: 'model_list', model: 'fix.marketplace.listing', stateField: 'state',
    cols: ['name', 'seller_id', 'category_id', 'list_price', 'state', 'approved_by_id'],
    // A04 audit M12-10: a listing goes live only on a compliance reviewer's
    // approval (M63 inbox), for a verified, CFO-approved seller.
    actions: [
      { m: 'action_submit', l: 'Submit for Approval', states: ['draft', 'rejected'] },
      { m: 'action_recall_approval', l: 'Recall Request', states: ['submitted'] },
      { m: 'action_pause', l: 'Pause', states: ['active'] },
      { m: 'action_resume', l: 'Resume', states: ['paused'] },
      { m: 'action_withdraw', l: 'Withdraw to Draft', states: ['active', 'paused', 'rejected'] },
      { m: 'action_remove', l: 'Remove Listing', states: ['draft', 'submitted', 'active', 'paused', 'rejected'] }
    ] },
  /* M12-stock / M12-training (12 Nov 2026): built from the seller's reported
   * stock positions and the seller certifications held against the
   * standards their approved categories require. */
  'M12-stock': { kind: 'table_report', module: 'M12', report: 'seller_stock', title: 'Seller Stock', period: false },
  'M12-training': { kind: 'table_report', module: 'M12', report: 'seller_standards', title: 'Standards & Training', period: false },
  /* A position is what the seller (portal), an operator or an import reports;
   * who reported it, when and how are stamped by the server. */
  'M12-stock-positions': { kind: 'model_list', model: 'fix.seller.stock',
    cols: ['seller_id', 'listing_id', 'sku', 'part_id', 'qty_on_hand', 'qty_reserved', 'qty_available', 'last_updated', 'source'] },
  /* A certification is submitted with its evidence and verified by a
   * compliance reviewer who did not submit it and does not act for the
   * seller; a verified one expires on its date (daily run). */
  'M12-certifications': { kind: 'model_list', model: 'fix.seller.certification', stateField: 'state',
    cols: ['seller_id', 'standard_id', 'certificate_no', 'issued_on', 'expires_on', 'expiry_status', 'verified_by_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Verification', states: ['draft', 'rejected'] },
      { m: 'action_verify', l: 'Verify Certificate', states: ['submitted'] },
      { m: 'action_reject', l: 'Reject', ask: 'Why the certificate is rejected', kwarg: 'reason', states: ['submitted'] },
      { m: 'action_revoke', l: 'Revoke', ask: 'Why the certificate is revoked', kwarg: 'reason', states: ['verified'] }
    ] },
  'M12-standards': { kind: 'model_list', model: 'fix.seller.standard',
    cols: ['code', 'name', 'kind', 'issuing_body', 'validity_months', 'category_ids', 'active'] },
  'M12-broadcast': { kind: 'table_report', module: 'M12', report: 'broadcast_backlog', title: 'Job Broadcast', period: false },
  'M12-bids': { kind: 'model_list', model: 'fix.seller.quote', stateField: 'state',
    cols: ['marketplace_order_id', 'seller_id', 'quoted_price', 'eta_days', 'state'],
    // A04 audit M12-7: the operator awards; price and rate are pinned then.
    actions: [
      { m: 'action_select', l: 'Award to this Quote', states: ['submitted'] }
    ] },
  'M12-oversight': { kind: 'table_report', module: 'M12', report: 'oversight', title: 'Execution Oversight', period: false },
  'M12-commission': { kind: 'table_report', module: 'M12', report: 'commission_revenue', title: 'Commission Schemes', period: false },
  'M12-wallet': { kind: 'table_report', module: 'M12', report: 'seller_wallet', title: 'Seller Wallets & Payouts', period: false },
  'M12-fees': { kind: 'table_report', module: 'M12', report: 'fees_register', title: 'Fees & Promotion', period: false },
  'M12-reviews': { kind: 'table_report', module: 'M12', report: 'reviews_summary', title: 'Ratings & Reviews', period: false },
  'M12-disputes': { kind: 'model_list', model: 'fix.marketplace.dispute', stateField: 'state',
    cols: ['name', 'order_id', 'seller_id', 'customer_id', 'dispute_reason', 'disputed_amount', 'proposed_resolution', 'approval_state', 'state'],
    // A04 audit M12-3: raised -> investigating -> arbitration -> resolved.
    // The ruling proposed on the form is decided by a Marketplace Dispute
    // Arbitrator from the M63 inbox; the 48h SLA escalates by cron.
    actions: [
      { m: 'action_investigate', l: 'Start Investigation', states: ['raised'] },
      { m: 'action_arbitrate', l: 'Send Ruling to Arbitrator', states: ['investigating', 'escalated'] },
      { m: 'action_recall_approval', l: 'Recall Ruling', states: ['arbitration', 'escalated'] },
      { m: 'action_escalate', l: 'Escalate to Executive', states: ['raised', 'investigating', 'arbitration'] }
    ] },
  'M12-chargebacks': { kind: 'model_list', model: 'fix.marketplace.chargeback', stateField: 'state',
    cols: ['name', 'order_id', 'seller_id', 'amount', 'reason', 'gateway_ref', 'received_on', 'respond_by', 'state'],
    // A04 P2 (M12): a chargeback holds the seller's payout while open; a
    // lost one is recovered from the seller (M53, via the event).
    actions: [
      { m: 'action_submit_evidence', l: 'Contest (evidence sent)', ask: 'What evidence went to the gateway', kwarg: 'note', states: ['received'] },
      { m: 'action_mark_won', l: 'Gateway Ruled: Won', ask: 'Gateway outcome reference', kwarg: 'note', states: ['contested'] },
      { m: 'action_mark_lost', l: 'Gateway Ruled: Lost', ask: 'Gateway outcome reference', kwarg: 'note', states: ['contested'] },
      { m: 'action_accept', l: 'Accept Liability', ask: 'Why the chargeback is accepted', kwarg: 'note', states: ['received', 'contested'] }
    ] },
  'M12-form-chargeback': { kind: 'model_form', model: 'fix.marketplace.chargeback',
    title: 'Chargeback', back: 'M12-chargebacks',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Case', bn: '১. কেস' },
      { id: 'outcome', label: '2. Outcome', bn: '২. ফলাফল' }
    ],
    sections: [
      { tab: 'general', title: 'Gateway Case', fields: [
        { name: 'name', label: 'Reference (auto)', readonly: true },
        { name: 'order_id', label: 'Marketplace Order', required: true },
        { name: 'seller_id', label: 'Seller (the awarded seller)', readonly: true },
        { name: 'amount', label: 'Amount Charged Back (BDT)', required: true },
        { name: 'currency_id', label: 'Currency' },
        { name: 'reason', label: 'Reason', required: true },
        { name: 'gateway_ref', label: 'Gateway Case Reference', required: true },
        { name: 'received_on', label: 'Received On', required: true },
        { name: 'respond_by', label: 'Respond By', readonly: true }
      ] },
      { tab: 'outcome', title: 'Contest & Outcome', fields: [
        { name: 'state', label: 'State (set by its actions)', readonly: true },
        { name: 'evidence_note', label: 'Evidence Sent', readonly: true, type: 'text' },
        { name: 'outcome_note', label: 'Gateway Outcome', readonly: true, type: 'text' },
        { name: 'decided_by_id', label: 'Outcome Recorded By', readonly: true }
      ] }
    ] },
  'M12-trust': { kind: 'table_report', module: 'M12', report: 'trust_bands', title: 'Fraud & Trust Ops', period: false },

  /* Report chips -> their own computed pack */
  'M12-rpt-liquidity': { kind: 'table_report', module: 'M12', report: 'seller_liquidity', title: 'Supply-Demand Liquidity', period: false },
  'M12-rpt-fill': { kind: 'table_report', module: 'M12', report: 'fill_rate', title: 'Fill Rate & Time-to-Accept', period: false },
  'M12-rpt-commission': { kind: 'table_report', module: 'M12', report: 'commission_revenue', title: 'Commission Revenue', period: false },
  'M12-rpt-dispute': { kind: 'table_report', module: 'M12', report: 'dispute_rate', title: 'Dispute Rate & Outcomes', period: false },
  'M12-rpt-scorecard': { kind: 'table_report', module: 'M12', report: 'scorecard_distribution', title: 'Seller Scorecard Distribution', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M12-form-seller': {
    lines: {
      field: 'certification_ids',
      title: 'Standards & Certifications',
      readonlyGrid: true,
      note: 'Recorded, submitted and verified on the Seller Certifications screen; a verified certificate expires on its date.',
      fields: [
        { name: 'standard_id', label: 'Standard / Course', readonly: true },
        { name: 'certificate_no', label: 'Certificate No.', readonly: true },
        { name: 'expires_on', label: 'Expires', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ]
    },
    kind: 'model_form',
    model: 'fix.marketplace.seller',
    title: 'Marketplace Seller Master',
    back: 'M12-sellers',
    status: { field: 'kyc_status' },
    tabs: [
      { id: 'merchant', label: '1. Merchant Profile', bn: '১. মার্চেন্ট পরিচিতি', icon: '🏪', badge: '5' },
      { id: 'commercial', label: '2. Commercial Terms', bn: '২. বাণিজ্যিক শর্তাবলী', icon: '🤝', badge: '3' },
      { id: 'kyc', label: '3. Bangladesh Statutory & KYC', bn: '৩. কেওয়াইসি ও কর', icon: '⚖️', badge: '4' },
      { id: 'quality', label: '4. Quality & Ratings', bn: '৪. গুণমান স্কোর', icon: '⭐', badge: '2' },
      { id: 'workflow', label: '5. CFO Approval & State', bn: '৫. অনুমোদন প্রবাহ', icon: '✅', badge: '3' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'merchant', title: 'Merchant Master Identity',
        note: 'Registered third-party seller or repair partner on the 1000FiX Circular Platform.',
        fields: [
          { name: 'name', required: true, label: 'Merchant Business Name' },
          { name: 'partner_id', required: true, label: 'Party Master Record (M33)' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'operating_unit_id', label: 'Assigned Operating Unit' },
          { name: 'active', label: 'Active Merchant Status' }
        ] },
      { tab: 'commercial', title: 'Platform Commission & Settlement Terms',
        fields: [
          { name: 'tier', readonly: true, label: 'Seller Rating Tier (measured)' },
          ] },
      { tab: 'kyc', title: 'Bangladesh Statutory Compliance & Tax Registrations',
        note: 'Statutory compliance under Digital Commerce Operational Guidelines 2021 and Income Tax Act 2023 s.140.',
        fields: [
          { name: 'nid_number', label: 'National ID (Smart NID)' },
          { name: 'tin_number', label: '12-Digit e-TIN Number' },
          { name: 'trade_license_no', label: 'City Corporation / Union Trade License No' },
          { name: 'kyc_status', readonly: true, label: 'Statutory KYC Status (Submit / Verify / Reject)' },
          { name: 'compliance_reviewer_id', readonly: true, label: 'KYC Reviewed By' }
        ] },
      { tab: 'quality', title: 'Performance Telemetry & Quality Standards',
        fields: [
          { name: 'kyc_review_mode', required: true, label: 'Verification Methodology' }
        ] },
      { tab: 'workflow', title: 'CFO Governance & Payout Authorization',
        note: 'CFO approval required before first payout disbursement or high-value refurbished device listing.',
        fields: [
          { name: 'cfo_approved', readonly: true, label: 'CFO Approval Granted (DOFA Tier 4, inbox)' },
          { name: 'cfo_approved_by', readonly: true, label: 'CFO Approved By' },
          { name: 'payout_hold', readonly: true, label: 'Payout Hold (open dispute / chargeback)' }
        ] },
      { tab: 'vault', title: 'Merchant Statutory Document Vault',
        note: 'Verified trade licenses, e-TIN certificates, bank solvency letters, and signed platform agreements.',
        fields: [] }
    ]
  },

  'M12-form-listing': {
    lines: {
      field: 'stock_ids',
      title: 'Seller Stock',
      readonlyGrid: true,
      note: 'Reported by the seller, an operator or an import on the Stock Positions screen.',
      fields: [
        { name: 'sku', label: 'SKU', readonly: true },
        { name: 'qty_on_hand', label: 'On Hand', readonly: true },
        { name: 'qty_reserved', label: 'Reserved', readonly: true },
        { name: 'qty_available', label: 'Available', readonly: true },
        { name: 'last_updated', label: 'Last Reported', readonly: true }
      ]
    },
    kind: 'model_form', model: 'fix.marketplace.listing',
    title: 'Listing', back: 'M12-listings',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'text', label: '4. Notes & Terms', bn: '৪. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '5. System Audit', bn: '৫. সিস্টেম অডিট' },
      { id: 'docs', label: '6. Documents', bn: '৬. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Listing Title', required: true },
        { name: 'state', label: 'State (set by its actions)', readonly: true },
        { name: 'approved_by_id', label: 'Approved By', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'list_price', label: 'List Price' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'seller_id', label: 'Seller', required: true },
        { name: 'category_id', label: 'Category' },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'description', label: 'Description', type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M12-form-payout': {

    lines: {

      field: 'statement_ids',

      title: 'Seller Statements in this Run',

      note: 'One statement per payee; gross GMV less commission is what is paid.',

      fields: [

        { name: 'seller_partner_id', label: 'Seller', required: true },

        { name: 'period', label: 'Period' },

        { name: 'gross_gmv', label: 'Gross GMV' },

        { name: 'commission_amount', label: 'Commission' },

        { name: 'date_issued', label: 'Issued' }

      ]

    }, kind: 'model_form', model: 'fix.payout.run',
    title: 'Payout Run', back: 'M12-wallet',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'flags', label: '6. Status Flags', bn: '৬. অবস্থা নির্দেশক' },
      { id: 'audit', label: '7. System Audit', bn: '৭. সিস্টেম অডিট' },
      { id: 'docs', label: '8. Documents', bn: '৮. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Run Name', required: true },
        { name: 'period', label: 'Period', required: true },
        { name: 'seller_count', label: 'Seller Count', readonly: true },
        // A04 integration (2026-11-04): A08 guards the payout-run state; it moves
        // only through the run's transitions, never from this form.
        { name: 'state', label: 'State', readonly: true },
        { name: 'rail_type', label: 'Rail Type', required: true },
        { name: 'rail_status', label: 'Rail Status', readonly: true },
        { name: 'rail_batch_id', label: 'Rail Batch Reference', readonly: true },
        { name: 'bank_confirmation_ref', readonly: true, label: 'Bank Confirmation Ref' },
        { name: 'beftn_file', label: 'BEFTN Batch File Content', readonly: true },
        { name: 'beftn_filename', label: 'BEFTN Filename', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'total_payable', label: 'Total Net Payable', readonly: true },
        { name: 'total_tds', label: 'Total Statutory TDS Withheld', readonly: true },
        { name: 'total_gross', label: 'Total Gross GMV', readonly: true },
        { name: 'total_clawback', label: 'Clawback Deducted', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'approved_date', label: 'Approved Date', readonly: true },
        { name: 'bank_confirmed_at', label: 'Bank Confirmation Recorded At', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'prepared_by_id', label: 'Prepared By', readonly: true },
        { name: 'approved_by_id', label: 'Approved By', readonly: true },
        { name: 'bank_confirmed_by_id', label: 'Bank Confirmation Recorded By', readonly: true },
        { name: 'gl_move_id', label: 'GL Disbursement Entry', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'sod_verified', label: 'SoD Verified', readonly: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (commission_ids, clawback_ids, recovery_ids, statement_ids, reconciliation_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M12-form-dispute': {
    kind: 'model_form',
    model: 'fix.marketplace.dispute',
    title: 'Marketplace Merchant Dispute Case',
    back: 'M12-disputes',
    status: { field: 'state' },
    tabs: [
      { id: 'case_header', label: '1. Dispute Details', bn: '১. বিরোধের বিবরণ', icon: '⚖️', badge: '5' },
      { id: 'financial_escrow', label: '2. Disputed Amount & Claim', bn: '২. বিরোধপূর্ণ অর্থ ও দাবি', icon: '💰', badge: '2' },
      { id: 'resolution', label: '3. Settlement & State', bn: '৩. নিষ্পত্তি ও অবস্থা', icon: '🤝', badge: '1' }
    ],
    sections: [
      { tab: 'case_header', title: 'Dispute Identification', note: 'A disputed marketplace order with its reason and transaction details.',
        fields: [
          { name: 'name', readonly: true, label: 'Dispute Reference (auto)' },
          { name: 'order_id', required: true, label: 'Marketplace Order' },
          { name: 'seller_id', required: true, label: 'Merchant / Seller' },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'dispute_reason', required: true, label: 'Dispute Reason' }
        ] },
      { tab: 'financial_escrow', title: 'Escrow Claim & Evidence', fields: [
          { name: 'disputed_amount', label: 'Disputed Amount (BDT)' },
          { name: 'description', required: true, label: 'Factual Statement / Claim Narrative', type: 'text' }
        ] },
      { tab: 'resolution', title: 'Adjudication Outcome', fields: [
          { name: 'state', readonly: true, label: 'Dispute Status (set by its actions)' },
          { name: 'proposed_resolution', label: 'Proposed Ruling (for the arbitrator)' },
          { name: 'proposed_refund_amount', label: 'Proposed Refund to Customer (BDT)' },
          { name: 'resolution_notes', label: 'Ruling Rationale', type: 'text' },
          { name: 'resolution_type', readonly: true, label: 'Ruling (arbitrator)' },
          { name: 'refund_amount', readonly: true, label: 'Refund Ruled (BDT)' },
          { name: 'resolved_by', readonly: true, label: 'Arbitrated By' }
        ] }
    ]
  },
  'M12-form-bid': { kind: 'model_form', model: 'fix.seller.quote',
    title: 'Seller Quote / Bid', back: 'M12-bids',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'text', label: '6. Notes & Terms', bn: '৬. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '7. System Audit', bn: '৭. সিস্টেম অডিট' },
      { id: 'docs', label: '8. Documents', bn: '৮. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'eta_days', label: 'ETA (days)', required: true },
        { name: 'state', label: 'State (Award selects it)', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'quoted_price', label: 'Quoted Price', required: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'marketplace_order_id', label: 'Marketplace Order', required: true },
        { name: 'seller_id', label: 'Seller', required: true },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'notes', label: 'Quote Description / Proposal', type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  /* ===== M12-stock / M12-training records (12 Nov 2026) ===== */
  'M12-form-stock': { kind: 'model_form', model: 'fix.seller.stock',
    title: 'Seller Stock Position', back: 'M12-stock-positions',
    tabs: [
      { id: 'position', label: '1. Position', bn: '১. পজিশন' },
      { id: 'reported', label: '2. Reported', bn: '২. রিপোর্ট' }
    ],
    sections: [
      { tab: 'position', title: 'Listing, SKU and Quantities', fields: [
        { name: 'listing_id', label: 'Listing', required: true },
        { name: 'seller_id', label: 'Seller (the listing\'s)', readonly: true },
        { name: 'sku', label: 'Seller SKU', required: true },
        { name: 'part_id', label: 'Catalogue Part' },
        { name: 'qty_on_hand', label: 'On Hand' },
        { name: 'qty_reserved', label: 'Reserved' },
        { name: 'qty_available', label: 'Available', readonly: true },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'reported', title: 'Stamped by the Server', fields: [
        { name: 'last_updated', label: 'Quantity Last Reported', readonly: true },
        { name: 'updated_by_id', label: 'Reported By', readonly: true },
        { name: 'source', label: 'Reported Via', readonly: true }
      ] }
    ] },

  'M12-form-certification': { kind: 'model_form', model: 'fix.seller.certification',
    title: 'Seller Certification', back: 'M12-certifications',
    status: { field: 'state' },
    tabs: [
      { id: 'certificate', label: '1. Certificate', bn: '১. সনদ' },
      { id: 'evidence', label: '2. Evidence', bn: '২. প্রমাণক' },
      { id: 'review', label: '3. Verification', bn: '৩. যাচাই' }
    ],
    sections: [
      { tab: 'certificate', title: 'Seller and Standard', fields: [
        { name: 'seller_id', label: 'Seller', required: true },
        { name: 'standard_id', label: 'Standard / Course', required: true },
        { name: 'certificate_no', label: 'Certificate No.' },
        { name: 'issued_on', label: 'Issued On', required: true },
        { name: 'expires_on', label: 'Expires On (blank = from the standard\'s validity)' },
        { name: 'expiry_status', label: 'Expiry', readonly: true },
        { name: 'days_to_expiry', label: 'Days to Expiry', readonly: true }
      ] },
      { tab: 'evidence', title: 'Certificate Evidence', note: 'Attach the certificate scan before submitting; it is pinned once submitted.', fields: [
        { name: 'evidence_attachment_id', label: 'Evidence (certificate scan)' }
      ] },
      { tab: 'review', title: 'Compliance Verification', fields: [
        { name: 'state', label: 'State (set by its actions)', readonly: true },
        { name: 'submitted_by_id', label: 'Submitted By', readonly: true },
        { name: 'verified_by_id', label: 'Verified By', readonly: true },
        { name: 'verified_at', label: 'Verified At', readonly: true },
        { name: 'decision_note', label: 'Reviewer Note', readonly: true, type: 'text' }
      ] }
    ] },

  'M12-form-standard': { kind: 'model_form', model: 'fix.seller.standard',
    title: 'Seller Standard / Course', back: 'M12-standards',
    tabs: [
      { id: 'standard', label: '1. Standard', bn: '১. মানদণ্ড' },
      { id: 'categories', label: '2. Required For', bn: '২. প্রযোজ্য ক্যাটাগরি' }
    ],
    sections: [
      { tab: 'standard', title: 'Standard, Course or Certificate', fields: [
        { name: 'code', label: 'Code', required: true },
        { name: 'name', label: 'Name', required: true },
        { name: 'kind', label: 'Kind', required: true },
        { name: 'issuing_body', label: 'Issued By' },
        { name: 'validity_months', label: 'Validity (months, 0 = no expiry)' },
        { name: 'active', label: 'Active' },
        { name: 'description', label: 'Description', type: 'text' }
      ] },
      { tab: 'categories', title: 'Service Categories that Require It', note: 'A seller approved for one of these categories must hold this standard; the Standards & Training report lists who is missing it.', fields: [
        { name: 'category_ids', label: 'Required for Categories' }
      ] }
    ] },

  /* computed pack that had no screen (closure 2026-10-28) */
  'M12-rpt-listingcoverage': { kind: 'table_report', module: 'M12', report: 'listing_coverage', title: "Listing Coverage", period: false },

  /* ===== triage coverage screens ===== */
  'M12-marketplace-order': { kind: 'model_list', model: 'fix.marketplace.order', stateField: 'state',
    cols: ['name', 'state', 'company_id', 'operating_unit_id', 'order_type', 'customer_id', 'awarded_price', 'payout_available_date'],
    // A04 audit M12-5/-6: the order moves only through these actions; the
    // payout waits for the 7-day escrow from the customer's sign-off, no
    // open dispute and no seller payout hold.
    actions: [
      { m: 'action_start_job', l: 'Start Job', states: ['selected'] },
      { m: 'action_complete', l: 'Job Completed', states: ['in_progress'] },
      { m: 'action_review', l: 'Customer Sign-off', ask: 'Customer rating 1-5 (blank for none)', kwarg: 'rating', states: ['completed'] },
      { m: 'action_earn_commission', l: 'Earn Commission', states: ['reviewed'] },
      { m: 'action_paid', l: 'Release Payout', states: ['commissioned'] },
      { m: 'action_cancel', l: 'Cancel Order', states: ['open', 'quoted', 'selected'] }
    ] },
  'M12-seller-score': { kind: 'model_list', model: 'fix.seller.score', create: false,
    cols: ['company_id', 'operating_unit_id', 'seller_id', 'period', 'acceptance_rate', 'on_time_rate', 'review_rating', 'metrics_measured'],
    empty: 'No seller score yet. Scores are measured each period from the seller\'s accepted jobs, on-time completion and customer reviews; they are not typed in.',
    // A04 C5: the KPIs are measured from the seller's records, never typed.
    actions: [
      { m: 'action_publish', l: 'Measure & Rank' }
    ] },

  'M12-form-marketplace-order': {

    lines: {

      field: 'quote_ids',

      title: 'Seller Quotes',

      note: 'Competing seller quotes against this marketplace order.',

      fields: [

        { name: 'seller_id', label: 'Seller', required: true },

        { name: 'quoted_price', label: 'Quoted Price', required: true },

        { name: 'eta_days', label: 'ETA (days)' },

        { name: 'state', label: 'State' },

        { name: 'notes', label: 'Notes' }

      ]

    }, kind: 'model_form', model: 'fix.marketplace.order',
    title: 'Marketplace Order', back: 'M12-marketplace-order',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'flags', label: '6. Status Flags', bn: '৬. অবস্থা নির্দেশক' },
      { id: 'text', label: '7. Notes & Terms', bn: '৭. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '8. System Audit', bn: '৮. সিস্টেম অডিট' },
      { id: 'docs', label: '9. Documents', bn: '৯. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', required: true, readonly: true },
        { name: 'order_type', label: 'Order Type', required: true },
        { name: 'state', label: 'State (set by its actions)', readonly: true },
        { name: 'battery_health_percent', label: 'Battery Health (%)' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'budget', label: 'Customer Budget / Listing Price' },
        { name: 'commission_amount', label: 'Commission Earned', readonly: true },
        { name: 'awarded_price', label: 'Awarded Price (pinned at award)', readonly: true },
        { name: 'commission_rate', label: 'Commission Rate (seller tier, pinned at award)', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'started_at', label: 'Job Started', readonly: true },
        { name: 'completed_at', label: 'Job Completed', readonly: true },
        { name: 'delivery_confirmed_at', label: 'Customer Confirmed Delivery', readonly: true },
        { name: 'payout_available_date', label: 'Escrow Release Date (7-Day Hold)', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'customer_id', label: 'Customer', required: true },
        { name: 'service_order_id', label: 'Linked Service Order (M01)' },
        { name: 'category_id', label: 'Service Category' },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'tradein_request_id', label: 'Source Trade-In Request' },
        { name: 'graded_stock_id', label: 'Graded Refurb Inventory Unit' },
        { name: 'revealed_seller_id', label: 'Awarded Seller for Contact Disclosure', readonly: true },
        { name: 'selected_quote_id', label: 'Selected Quote', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' },
        { name: 'review_rating', label: 'Customer Rating (1-5, at sign-off)', readonly: true }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'customer_contact_revealed', label: 'Contact Info Revealed to Selected Seller', readonly: true },
        { name: 'has_open_dispute', label: 'Has Active Open Disputes', readonly: true }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'description', label: 'Description', required: true, type: 'text' },
        { name: 'disclosed_defects', label: 'Disclosed Cosmetic / Functional Defects', type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (quote_ids, dispute_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

};

export const REPORT_ROUTES = {
  'M12:Listing Coverage': 'M12-rpt-listingcoverage',
  'M12:Seller Stock': 'M12-stock',
  'M12:Standards & Training': 'M12-training',
  'M12:Supply-Demand Liquidity': 'M12-rpt-liquidity',
  'M12:Fill Rate & Time-to-Accept': 'M12-rpt-fill',
  'M12:Commission Revenue': 'M12-rpt-commission',
  'M12:Dispute Rate & Outcomes': 'M12-rpt-dispute',
  'M12:Seller Scorecard Distribution': 'M12-rpt-scorecard'
};

export const FORM_MODELS = {
  'M12:Seller Application': 'fix.marketplace.seller',
  'M12:Listing': 'fix.marketplace.listing',
  'M12:Payout Run': 'fix.payout.run',
  'M12:Dispute Case': 'fix.marketplace.dispute',
  'M12:Chargeback': 'fix.marketplace.chargeback',
  'M12:Stock Position': 'fix.seller.stock',
  'M12:Seller Certification': 'fix.seller.certification',
  'M12:Seller Standard': 'fix.seller.standard'
};

export const FORM_CHIPS = {
  'M12:Seller Bid': 'M12-form-bid',
  'M12:Seller Application': 'M12-form-seller',
  'M12:Listing': 'M12-form-listing',
  'M12:Payout Run': 'M12-form-payout',
  'M12:Dispute Case': 'M12-form-dispute',
  'M12:Stock Position': 'M12-form-stock',
  'M12:Seller Certification': 'M12-form-certification',
  'M12:Seller Standard': 'M12-form-standard',
  'M12:__by_model__': {
    'fix.marketplace.order': 'M12-form-marketplace-order',
    'fix.seller.quote': 'M12-form-bid',
    'fix.marketplace.seller': 'M12-form-seller',
    'fix.marketplace.listing': 'M12-form-listing',
    'fix.payout.run': 'M12-form-payout',
    'fix.marketplace.dispute': 'M12-form-dispute',
    'fix.marketplace.chargeback': 'M12-form-chargeback',
    'fix.seller.stock': 'M12-form-stock',
    'fix.seller.certification': 'M12-form-certification',
    'fix.seller.standard': 'M12-form-standard'
  },
  'M12:__by_screen__': {
    'M12-marketplace-order': 'M12-form-marketplace-order',
    'M12-bids': 'M12-form-bid',
    'M12-sellers': 'M12-form-seller',
    'M12-listings': 'M12-form-listing',
    'M12-wallet': 'M12-form-payout',
    'M12-disputes': 'M12-form-dispute',
    'M12-chargebacks': 'M12-form-chargeback',
    'M12-stock-positions': 'M12-form-stock',
    'M12-certifications': 'M12-form-certification',
    'M12-standards': 'M12-form-standard'
  }
};

export const CREATE = {
  M12: { screen: 'M12-form-seller', model: 'fix.marketplace.seller', label: 'Seller Application' }
};
