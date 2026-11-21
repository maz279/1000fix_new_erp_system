/** @odoo-module **/
/* A05 — Circular Economy — M14 Trade-In, Refurbishment & Resale (v2.1 D365 multi-tab standard).
 * 100% Dynamics 365 6-tab forms with Document Vault (10 forms incl. the price grid).
 * All 8 report packs exposed as chips (including Resale Listings & Unit Economics).
 * Zero phantom fields: all fields verified against PostgreSQL fix_dev. */

export const MODULE = {
  area: 'A05', code: 'M14', en: 'Trade-In & Refurbishment', title: 'M14 · Trade-In & Refurbishment',
  bn: 'ট্রেড-ইন ও রিফার্বিশমেন্ট', icon: '🔄',
  desc: 'Trade-in intake across five channels, automated valuation with manual override, IMEI/blacklist provenance screening, settlement and four-eyes payout, refurb work orders, QA and battery health, A–E grading, harvest to parts, graded stock, resale channel and unit economics.',
  kpis: [
    { l: 'Open Trade-Ins', m: 'open_tradeins' },
    { l: 'Payouts Pending', m: 'pending_payouts' },
    { l: 'Refurb Open', m: 'refurb_open' },
    { l: 'Resale Ready', m: 'resale_ready' },
    { l: 'Graded Stock Value', m: 'graded_stock_value', prefix: '৳ ' },
    { l: 'Margin Pipeline', m: 'margin_pipeline', prefix: '৳ ' },
    { l: 'Gross Margin 12m', m: 'gross_margin_pct_12m', suffix: '%' },
    { l: 'Refurb Yield', m: 'refurb_yield_pct', suffix: '%' },
    { l: 'Stock > 90 Days', m: 'stock_over_90d_pct', suffix: '%' },
    { l: 'Zero-Target Breaches 90d', m: 'zero_target_breaches_90d' }
  ],
  groups: [
    { en: 'Trade-In', screens: [
      { id: 'M14-intake', en: 'Trade-In Intake', bn: 'ট্রেড-ইন গ্রহণ', t: 'g' },
      { id: 'M14-intake-check', en: 'Physical Intake Verification', bn: 'প্রাপ্তিকালীন যাচাই', t: 'g' },
      { id: 'M14-bulk', en: 'Corporate Bulk Buy-Back', bn: 'কর্পোরেট বাল্ক বাই-ব্যাক', t: 'g' },
      { id: 'M14-valuation', en: 'Automated Valuation', bn: 'স্বয়ংক্রিয় মূল্যায়ন', t: 'g' },
      { id: 'M14-grid', en: 'Governed Price Grid', bn: 'মূল্য গ্রিড', t: 'g' },
      { id: 'M14-provenance', en: 'Provenance & IMEI Screen', bn: 'আইএমইআই যাচাই', t: 'g' },
      { id: 'M14-gate', en: 'Destruction Gate', bn: 'ডেটা ধ্বংস গেট', t: 'g' },
      { id: 'M14-settlement', en: 'Settlement', bn: 'পরিশোধ ও নিষ্পত্তি', t: 'g' }
    ]},
    { en: 'Refurbishment', screens: [
      { id: 'M14-orders', en: 'Refurb Work Orders', bn: 'রিফার্বিশমেন্ট কার্যআদেশ', t: 'g' },
      { id: 'M14-qa', en: 'QA & Battery Health', bn: 'কিউএ ও ব্যাটারি স্বাস্থ্য', t: 'g' },
      { id: 'M14-grading', en: 'A–D Grading', bn: 'গ্রেডিং নির্ধারণ', t: 'g' },
      { id: 'M14-writeoff', en: 'Parts-Only Routing & Write-off', bn: 'যন্ত্রাংশ-কেবল রাউটিং ও অবলোপন', t: 'g' },
      { id: 'M14-harvest', en: 'Harvest to Parts', bn: 'যন্ত্রাংশ সংগ্রহ', t: 'g' }
    ]},
    { en: 'Resale', screens: [
      { id: 'M14-resale-prep', en: 'Resale Preparation', bn: 'পুনর্বিক্রয় প্রস্তুতি', t: 'g' },
      { id: 'M14-stock', en: 'Graded Stock', bn: 'গ্রেডেড স্টক', t: 'g' },
      { id: 'M14-listings', en: 'Resale Listings', bn: 'পুনর্বিক্রয় তালিকা', t: 'r' },
      { id: 'M14-wty', en: 'Refurb Warranty', bn: 'রিফার্বিশড ওয়ারেন্টি', t: 'g' },
      { id: 'M14-returns', en: 'Refurbished Returns', bn: 'রিফার্বিশড ফেরত', t: 'g' },
      { id: 'M14-economics', en: 'Unit Economics', bn: 'ইউনিট অর্থনীতি', t: 'r' }
    ]}
  ],
  reports: [
    'Trade-In Margin by Model',
    'Refurb Cost per Grade',
    'Ageing & Markdown',
    'Resale Channel Performance',
    'Harvest Yield',
    'Valuation Queue',
    'Resale Listings',
    'Unit Economics',
    'Trade-In Funnel',
    'Gate Compliance'
  ],
  forms: [
    'Trade-In Intake Dossier',
    'Automated Valuation File',
    'Governed Price Grid Row',
    'Provenance Screening & Anti-Theft',
    'Settlement & Four-Eyes Payout',
    'Refurbishment Work Order',
    'QA & Battery Health Dossier',
    'Grading Certificate',
    'Harvest to Parts Dossier',
    'Destruction Certificate Attachment',
    'Resale Listing Preparation',
    'Corporate Bulk Buy-Back Lot',
    'Physical Intake Verification',
    'Refurbished Unit Return',
    'Parts-Only Routing & Write-off'
  ],
  cross: ['M06 destruction gate', 'M31 refurb repairs', 'M15 graded stock', 'M38 online resale', 'M18 recycle routing'],
  freg: { src: 84, sub: [
    ['1', 'Intake (5 channels)', 9, { model: 'fix.tradein.request', cols: ['name', 'customer_id', 'device_model_id', 'offered_value', 'state'], screens: ['M14-intake', 'M14-intake-check'], reports: ['Valuation Queue', 'Trade-In Funnel', 'Gate Compliance'], forms: ['Trade-In Intake Dossier', 'Physical Intake Verification'] }],
    ['2', 'Valuation Engine', 9, { model: 'fix.tradein.valuation', cols: ['name', 'tradein_id', 'market_ref_price', 'computed_offer', 'final_offer'], screens: ['M14-valuation'], reports: ['Valuation Queue', 'Trade-In Margin by Model'], forms: ['Automated Valuation File', 'Governed Price Grid Row'] }],
    ['3', 'Provenance Screening', 7, { model: 'fix.tradein.provenance', cols: ['name', 'tradein_id', 'imei', 'btrc_neir_status', 'state'], screens: ['M14-provenance'], reports: [], forms: ['Provenance Screening & Anti-Theft'] }],
    ['4', 'Settlement', 8, { model: 'fix.tradein.request', cols: ['name', 'customer_id', 'payout_amount', 'payout_approval_state', 'net_payout'], screens: ['M14-settlement'], reports: ['Unit Economics'], forms: ['Settlement & Four-Eyes Payout'], create: 'M14-form-settlement' }],
    ['5', 'Bulk Buy-Back', 6, { model: 'fix.bulk.buyback', cols: ['name', 'partner_id', 'declared_asset_count', 'pending_count', 'state'], screens: ['M14-bulk', 'M14-intake'], reports: ['Trade-In Margin by Model'], forms: ['Corporate Bulk Buy-Back Lot'] }],
    /* M14 capture audit (2026-11-13): Destruction Gate and Resale named no
     * form, so neither page had a button. The gate's record is the M06
     * certificate ATTACHED to a collected unit (M14 never issues one: SoD,
     * spec §13), then Data Wipe; resale is the listing prepared on a graded
     * unit (FR-TRF-021), then Resale Ready, which stocks it. */
    ['6', 'Destruction Gate', 4, { model: 'fix.tradein.request', cols: ['name', 'device_id', 'wipe_certificate_id', 'state'], screens: ['M14-gate', 'M14-orders'], reports: [], forms: ['Destruction Certificate Attachment'], create: 'M14-form-wipe', domain: [['state', 'in', ['collected', 'wiped']]] }],
    ['7', 'Refurbishment Orders', 11, { model: 'fix.refurbishment', cols: ['name', 'tradein_id', 'step', 'technician_id', 'state'], screens: ['M14-orders'], reports: ['Refurb Cost per Grade'], forms: ['Refurbishment Work Order'] }],
    ['8', 'Grading & QA', 11, { model: 'fix.tradein.grade', cols: ['name', 'tradein_id', 'grade', 'battery_health_pct', 'graded_on'], screens: ['M14-grading', 'M14-qa'], reports: ['Refurb Cost per Grade'], forms: ['Grading Certificate', 'QA & Battery Health Dossier'] }],
    ['9', 'Resale', 10, { model: 'fix.graded.stock', cols: ['name', 'device_id', 'grade_id', 'resale_price', 'state'], screens: ['M14-resale-prep', 'M14-listed', 'M14-stock', 'M14-markdown', 'M14-listings', 'M14-wty', 'M14-returns', 'M14-economics'], reports: ['Resale Listings', 'Resale Channel Performance', 'Ageing & Markdown', 'Unit Economics'], forms: ['Resale Listing Preparation', 'Refurbished Unit Return', 'Refurbished Unit Markdown'], create: 'M14-form-resale' }],
    ['10', 'Harvesting', 9, { model: 'fix.tradein.harvest', cols: ['name', 'component', 'part_name', 'quantity', 'target'], screens: ['M14-writeoff', 'M14-parts-only', 'M14-harvest'], reports: ['Harvest Yield'], forms: ['Parts-Only Routing & Write-off', 'Harvest to Parts Dossier'], create: 'M14-form-harvest' }]
    /* M14 capture pass 2 (2026-11-19), read against FR-TRF-001..039:
     * p1 also verifies the unit as received (FR-TRF-005, BRU-TRF-09); p9
     * captures a return of a sold unit (FR-TRF-026); p10 routes an
     * unsellable unit to parts only with an approved write-off before any
     * harvest (FR-TRF-020, BRU-TRF-19). */
  ] }
};

export const SCREENS = {
  /* A05 audit (2026-11-03) E3-E12: every workflow, approval, money and
   * evidence field is read-only below and changes only through its action;
   * the payout is requested here and decided from the approver's M63 inbox. */
  'M14-intake': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'state',
    cols: ['name', 'customer_id', 'device_model_id', 'offered_value', 'graded_value', 'revision_state', 'grade', 'state'],
    actions: [
      { m: 'action_send_offer', l: 'Send Offer' },
      { m: 'action_accept', l: 'Accept' },
      { m: 'action_accept_revision', l: 'Accept Revised Value' },
      { m: 'action_reject', l: 'Customer Declines', ask: 'Why the trade-in is rejected', kwarg: 'reason' },
      { m: 'action_collect', l: 'Collect' },
      { m: 'action_wipe', l: 'Data Wipe' },
      { m: 'action_refurbish', l: 'Refurbish' },
      { m: 'action_grade', l: 'Grade' },
      { m: 'action_resale_ready', l: 'Resale Ready' },
      /* A05 ERP XC-10: seller purchase voucher + declaration (from acceptance) */
      { m: 'p03_print_document', print: 'a4', l: 'Print Purchase Voucher', states: ['accepted', 'collected', 'wiped', 'refurbished', 'graded', 'resale_ready', 'parts_only', 'closed'] }
    ] },
  /* The destruction gate (FR-TRF-011, BRU-TRF-01): a collected unit waits
   * here for its M06 certificate; Data Wipe checks it is VERIFIED and bound
   * to this device's media serial, Refurbish re-checks it. */
  'M14-gate': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'state', create: false,
    cols: ['name', 'customer_id', 'device_id', 'wipe_certificate_id', 'hold_until', 'state'],
    domain: [['state', 'in', ['collected', 'wiped']]],
    actions: [
      { m: 'action_wipe', l: 'Data Wipe (passes the gate)', states: ['collected'] },
      { m: 'action_refurbish', l: 'Refurbish', states: ['wiped'] }
    ],
    empty: 'No collected unit is waiting at the destruction gate. A trade-in arrives here when it is collected; attach its verified M06 certificate with + Attach Destruction Certificate, then press Data Wipe.' },
  /* FR-TRF-009 / BRU-TRF-23: a corporate fleet is bought back as a LOT. The
   * client's declared assets are listed on the lot; Receive Lot opens one
   * trade-in per declared asset (valued, screened and wiped per unit); the
   * lot closes only when every declared asset has an intake or a documented
   * exception. */
  'M14-bulk': { kind: 'model_list', model: 'fix.bulk.buyback', stateField: 'state',
    cols: ['name', 'partner_id', 'contract_ref', 'lot_price_basis', 'declared_asset_count', 'matched_count', 'exception_count', 'pending_count', 'state'],
    actions: [
      { m: 'action_open_intakes', l: 'Receive Lot & Open Intakes', states: ['draft', 'received'] },
      { m: 'action_close', l: 'Close Lot (all reconciled)', states: ['received'] }
    ] },
  /* FR-TRF-005 / BRU-TRF-09: the unit as received, against the declaration.
   * A value below the accepted offer needs a worse condition, its description
   * and photographs; Confirm makes it the graded value the customer accepts. */
  'M14-intake-check': { kind: 'model_list', model: 'fix.tradein.intake.check', stateField: 'state',
    cols: ['name', 'tradein_id', 'declared_condition', 'verified_condition', 'condition_differs', 'accepted_value', 'verified_value', 'checked_by_id', 'state'],
    actions: [{ m: 'action_confirm', l: 'Confirm Verification', states: ['draft'] }],
    empty: 'No unit has been verified at intake. Verify each accepted unit as received with + Physical Intake Verification.' },
  'M14-valuation': { kind: 'model_list', model: 'fix.tradein.valuation', stateField: 'state',
    cols: ['name', 'tradein_id', 'market_ref_price', 'computed_offer', 'final_offer', 'resale_estimate', 'modelled_margin_pct', 'override_state', 'state'],
    actions: [
      { m: 'action_request_override_approval', l: 'Request Override Approval' },
      { m: 'action_approve_override', l: 'Approve Override' },
      { m: 'action_reject_override', l: 'Reject Override' },
      { m: 'action_apply_to_tradein', l: 'Apply to Trade-In' }
    ] },
  'M14-grid': { kind: 'model_list', model: 'fix.tradein.price.grid', stateField: 'state',
    cols: ['name', 'device_model_id', 'market_ref_price', 'valid_from', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve Price' },
      { m: 'action_retire', l: 'Retire' }
    ] },
  'M14-provenance': { kind: 'model_list', model: 'fix.tradein.provenance', stateField: 'state',
    cols: ['name', 'tradein_id', 'imei', 'checked_on', 'blacklist_hit', 'stolen_hit', 'lock_status', 'btrc_neir_status', 'customer_nid_verified', 'state'],
    actions: [
      { m: 'action_clear', l: 'Clear (Provenance Officer)' },
      { m: 'action_flag', l: 'Flag', ask: 'Why the device is flagged', kwarg: 'reason' },
      { m: 'action_run_neir_check', l: 'BTRC NEIR Check' },
      /* A05 ERP D4: the provenance officer (not the trade-in's creator)
       * records the manual NEIR result with its evidence; only clear passes. */
      { m: 'action_record_neir_result', l: 'NEIR Result: Clear', kw: { result: 'clear' },
        asks: [{ kwarg: 'evidence_ref', label: 'NEIR lookup reference (evidence)' }] },
      { m: 'action_record_neir_result', l: 'NEIR Result: Blocked', kw: { result: 'blocked' },
        asks: [{ kwarg: 'evidence_ref', label: 'NEIR lookup reference (evidence)' }] },
      { m: 'action_record_neir_result', l: 'NEIR Result: Not Found', kw: { result: 'not_found' },
        asks: [{ kwarg: 'evidence_ref', label: 'NEIR lookup reference (evidence)' }] }
    ] },
  'M14-settlement': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'payout_approval_state',
    cols: ['name', 'customer_id', 'graded_value', 'net_payout', 'tds_amount', 'payout_approval_state', 'approval_state', 'payout_approved_by_id', 'payout_execution_id', 'paid_at', 'state'],
    actions: [
      { m: 'action_verify_psr', l: 'Verify PSR' },
      { m: 'action_request_payout_approval', l: 'Request Approval', ask: 'Business justification (mandatory from Tier 2)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_pay', l: 'Pay via Treasury' }
    ] },
  'M14-orders': { kind: 'model_list', model: 'fix.refurbishment', stateField: 'state',
    cols: ['name', 'tradein_id', 'step', 'technician_id', 'parts_cost', 'labor_cost', 'total_cost', 'cost_approved_by_id', 'state'],
    actions: [
      { m: 'action_start', l: 'Start Step' },
      { m: 'action_request_parts', l: 'Request Parts' },
      { m: 'action_complete_repair', l: 'Complete Step' },
      /* A05 ERP M14-12: parts come from M15 and labour from the M31 clock; a
       * typed step cost counts only once a supervisor approves it. */
      { m: 'action_approve_cost', l: 'Approve Typed Cost (Supervisor)', states: ['done'] },
      { m: 'p03_print_document', print: 'a4', l: 'Print Job Card' }
    ] },
  'M14-qa': { kind: 'model_list', model: 'fix.refurb.qa', stateField: 'qa_state',
    cols: ['name', 'tradein_id', 'battery_health_pct', 'tests_passed', 'tests_total', 'pass_pct', 'qa_state', 'checked_on', 'inspected_by_id'],
    actions: [{ m: 'action_submit_result', l: 'Submit Result (QA Inspector)' }] },
  'M14-grading': { kind: 'model_list', model: 'fix.tradein.grade',
    cols: ['name', 'tradein_id', 'grade', 'battery_health_pct', 'screen_grade', 'cosmetic_grade', 'functional_grade', 'graded_on'] },
  /* FR-TRF-020 / BRU-TRF-19: a supervisor routes the unit to parts only and a
   * write-off approver (another person) approves its accumulated cost. */
  'M14-writeoff': { kind: 'model_list', model: 'fix.refurb.writeoff', stateField: 'state',
    cols: ['name', 'tradein_id', 'cause', 'destination', 'accumulated_cost', 'requested_by_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_request', l: 'Route to Parts Only (Supervisor)', states: ['draft', 'rejected'] },
      { m: 'action_approve', l: 'Approve Write-off', states: ['pending'] },
      { m: 'action_reject', l: 'Reject', ask: 'Why the write-off is rejected', kwarg: 'reason', states: ['pending'] }
    ],
    empty: 'No unit has been routed to parts only. A unit that failed QA or cannot be sold profitably is routed here before it is harvested or recycled.' },
  /* A05 ERP M14-09/20/21: an approved write-off puts the unit in Parts Only:
   * harvest its parts (each valued from the unit's cost), then close it (the
   * residue is written off), or hand it whole to M18 for recycling. */
  'M14-parts-only': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'state', create: false,
    cols: ['name', 'device_model_id', 'grade', 'written_off', 'paid_at', 'state'],
    domain: [['state', '=', 'parts_only']],
    actions: [
      { m: 'action_close_parts_only', l: 'Close (harvest done, write off residue)' },
      { m: 'action_route_to_recycle', l: 'Hand to M18 for Recycling' }
    ],
    empty: 'No unit is parts only. A unit arrives here when its parts-only write-off is approved.' },
  'M14-harvest': { kind: 'model_list', model: 'fix.tradein.harvest', stateField: 'state',
    cols: ['name', 'tradein_id', 'component', 'part_id', 'quantity', 'total_value', 'target', 'receipt_id', 'state'],
    actions: [
      { m: 'action_harvest', l: 'Harvest' },
      { m: 'action_scrap', l: 'Scrap', ask: 'Why the component is scrapped', kwarg: 'reason' }
    ] },
  /* FR-TRF-021: a graded unit's listing is prepared (channel, price,
   * merchant) and Resale Ready then stocks it in M15 and lists it; the
   * channel, price and merchant freeze from that point. */
  'M14-resale-prep': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'state', create: false,
    cols: ['name', 'device_model_id', 'grade', 'refurb_grade_id', 'resale_channel', 'resale_value', 'listing_price', 'listing_price_state', 'state'],
    domain: [['state', '=', 'graded']],
    actions: [
      /* A05 ERP D6: the suggested price is proposed, a pricing manager who
       * did not propose or enter it approves it; below cost is a markdown. */
      { m: 'action_request_listing_price', l: 'Propose Listing Price' },
      { m: 'action_approve_listing_price', l: 'Approve Listing Price (Pricing Manager)' },
      { m: 'action_resale_ready', l: 'Resale Ready (stock and list)' }
    ],
    empty: 'No graded unit is waiting for resale. A trade-in arrives here once it is graded; prepare its listing with + Prepare a Resale Listing, then press Resale Ready.' },
  'M14-stock': { kind: 'model_list', model: 'fix.graded.stock', stateField: 'state', create: false,
    cols: ['name', 'device_id', 'grade_id', 'tradein_ref', 'inventory_valuation', 'resale_price', 'projected_margin', 'state'],
    empty: 'No graded unit in stock. A unit is stocked by Resale Ready on Resale Preparation, at what the seller was paid plus its refurbishment cost; it is sold from its store or marketplace order.' },
  /* A05 ERP M14-15: a listed unit sold at the counter is invoiced through
   * M20 (the VAT is M51's); a marketplace unit is sold from its M12 order. */
  'M14-listed': { kind: 'model_list', model: 'fix.tradein.request', stateField: 'state', create: false,
    cols: ['name', 'device_model_id', 'grade', 'resale_channel', 'listing_price', 'graded_stock_id', 'sale_count', 'state'],
    domain: [['state', '=', 'resale_ready']],
    actions: [
      { m: 'action_counter_sell', l: 'Counter Sale (Inventory Controller)', ask: 'Buyer (customer id)', kwarg: 'buyer_id' }
    ],
    empty: 'No unit is listed. A unit is listed by Resale Ready at its approved price.' },
  /* A05 ERP M14-25 / D6: a price cut, or a listing below landed cost, is a
   * markdown a different pricing manager approves; it writes the stock down
   * to its net realisable value. */
  'M14-markdown': { kind: 'model_list', model: 'fix.refurb.markdown', stateField: 'state',
    cols: ['name', 'tradein_id', 'current_price', 'new_price', 'requested_by_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_request', l: 'Request Approval', states: ['draft', 'rejected'] },
      { m: 'action_approve', l: 'Approve (Pricing Manager)', states: ['pending'] },
      { m: 'action_reject', l: 'Reject', states: ['pending'] }
    ],
    empty: 'No markdown. Raise one with + Markdown when a listed unit must sell for less.' },
  'M14-listings': { kind: 'table_report', module: 'M14', report: 'resale_pipeline', title: 'Resale Listings', period: true },
  'M14-wty': { kind: 'model_list', model: 'fix.tradein.warranty', stateField: 'state', create: false,
    cols: ['name', 'tradein_id', 'graded_stock_ref', 'months', 'start_date', 'end_date', 'claims_count', 'state'],
    empty: 'No refurbished warranty issued yet. A warranty is issued automatically when a refurbished unit is resold; it cannot be typed in.',
    actions: [{ m: 'action_void', l: 'Void (Warranty Officer)', ask: 'Reason for voiding', kwarg: 'reason' },
      { m: 'p03_print_document', print: 'a4', l: 'Print Warranty Card & Disclosure' }] },
  'M14-economics': { kind: 'table_report', module: 'M14', report: 'unit_economics', title: 'Unit Economics', period: true },
  /* FR-TRF-026 / AUT-TRF-18: a sold refurbished unit comes back. */
  'M14-returns': { kind: 'model_list', model: 'fix.refurb.return', stateField: 'state',
    cols: ['name', 'tradein_id', 'grade_at_sale', 'return_date', 'reason', 'failure_code', 'within_terms', 'outcome', 'state'],
    actions: [
      { m: 'action_receive', l: 'Receive Return', states: ['draft'] },
      { m: 'action_decide', l: 'Decide (Supervisor)', states: ['received'] }
    ],
    empty: 'No refurbished unit has been returned. Record a return of a sold unit with + Refurbished Unit Return.' },

  /* Report chips -> their own computed packs (All 8 active) */
  'M14-rpt-margin': { kind: 'table_report', module: 'M14', report: 'tradein_margin', title: 'Trade-In Margin by Model', period: true },
  'M14-rpt-grade': { kind: 'table_report', module: 'M14', report: 'refurb_cost_grade', title: 'Refurb Cost per Grade', period: true },
  'M14-rpt-ageing': { kind: 'table_report', module: 'M14', report: 'ageing_markdown', title: 'Ageing & Markdown', period: true },
  'M14-rpt-channel': { kind: 'table_report', module: 'M14', report: 'resale_channel', title: 'Resale Channel Performance', period: true },
  'M14-rpt-harvest': { kind: 'table_report', module: 'M14', report: 'harvest_yield', title: 'Harvest Yield', period: true },
  'M14-rpt-valqueue': { kind: 'table_report', module: 'M14', report: 'valuation_queue', title: 'Valuation Queue', period: true },
  'M14-rpt-resale': { kind: 'table_report', module: 'M14', report: 'resale_pipeline', title: 'Resale Listings', period: true },
  'M14-rpt-economics': { kind: 'table_report', module: 'M14', report: 'unit_economics', title: 'Unit Economics', period: true },
  'M14-rpt-funnel': { kind: 'table_report', module: 'M14', report: 'tradein_funnel', title: 'Trade-In Funnel', period: true },
  'M14-rpt-gate': { kind: 'table_report', module: 'M14', report: 'gate_compliance', title: 'Gate Compliance', period: true },

  /* ============ D365 IN-WORKSPACE FORMS (6-TAB STANDARD) ============ */
  'M14-form-request': {
    kind: 'model_form',
    model: 'fix.tradein.request',
    title: 'Trade-In Intake Dossier',
    back: 'M14-intake',
    status: { field: 'state', labels: {
      draft: 'Draft', offered: 'Offer Sent', accepted: 'Accepted', collected: 'Collected',
      wiped: 'Data Wiped', refurbished: 'Refurbished', graded: 'Graded',
      resale_ready: 'Resale Ready', closed: 'Closed', rejected: 'Rejected' } },
    tabs: [
      { id: 'general', label: '1. General & Customer', bn: '১. সাধারণ ও গ্রাহক', icon: '👤', badge: '8' },
      { id: 'pricing', label: '2. Valuation & Tax', bn: '২. মূল্যায়ন ও কর', icon: '৳', badge: '15' },
      { id: 'technical', label: '3. Device & Grading', bn: '৩. ডিভাইস ও গ্রেডিং', icon: '📱', badge: '4' },
      { id: 'lifecycle', label: '4. Workshop & Costs', bn: '৪. ওয়ার্কশপ ও খরচ', icon: '🔧', badge: '7' },
      { id: 'governance', label: '5. Payout & Channel', bn: '৫. পরিশোধ ও চ্যানেল', icon: '⚖️', badge: '17' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ডকুমেন্ট ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Customer & Intake Master',
        fields: [
          { name: 'name', label: 'Trade-In Reference', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'customer_nid', label: 'National ID (10-digit Smart / 17-digit NID)' },
          { name: 'intake_channel', required: true, label: 'Intake Channel (portal / app / counter / field / corporate)' },
          { name: 'acceptance_channel', label: 'Acceptance Channel' },
          { name: 'state', label: 'Intake State', readonly: true }
        ] },
      { tab: 'general', title: "Customer's Declaration (FR-TRF-001 / FR-TRF-035)",
        note: 'What the customer declares is what the offer is built on: it freezes once the offer is sent. The unit is then verified against it at intake.',
        fields: [
          { name: 'declared_condition', required: true, label: 'Declared Condition' },
          { name: 'declared_faults', label: 'Declared Faults' },
          { name: 'declared_age_months', label: 'Declared Age (months)' },
          { name: 'oem_warranty_status', label: 'OEM Warranty Status' },
          { name: 'condition_photo_id', label: 'Condition Photographs' },
          { name: 'acc_charger', label: 'Charger' },
          { name: 'acc_cable', label: 'Cable' },
          { name: 'acc_box', label: 'Original Box' },
          { name: 'acc_earphones', label: 'Earphones' },
          { name: 'acc_documents', label: 'Purchase Documents' },
          { name: 'accessories_notes', label: 'Other Accessories' }
        ] },
      { tab: 'general', title: 'Intake Device Reference',
        fields: [
          { name: 'device_id', label: 'Device Serial Master' },
          { name: 'device_model_id', label: 'Device Model', readonly: true },
          { name: 'hold_until', label: 'Hold Period Ends', readonly: true }
        ] },
      { tab: 'pricing', title: 'Commercial Valuation & Payout Offer',
        fields: [
          { name: 'offered_value', label: 'Offer Value (draft only, from the applied valuation)' },
          { name: 'accepted_offer_value', label: 'Offer Accepted by Customer', readonly: true },
          { name: 'graded_value', label: 'Payout Value (set by the confirmed Physical Intake Verification, capped at the accepted offer)', readonly: true },
          { name: 'revision_state', label: 'Revised Offer', readonly: true },
          { name: 'revision_accepted_value', label: 'Revised Value Accepted', readonly: true },
          { name: 'payout_amount', label: 'Payout Queued', readonly: true },
          { name: 'net_payout', label: 'Net Payout After Tax', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'pricing', title: 'Statutory Withholding Tax (ITA 2023 s.89/90)',
        fields: [
          { name: 'tds_applicable', label: 'TDS Withholding Applicable' },
          { name: 'tds_section', label: 'TDS Section' },
          { name: 'tds_rate_pct', label: 'TDS Rate (%)' },
          { name: 'taxpayer_tin', label: 'Seller e-TIN (12 digits)' },
          { name: 'psr_attachment_id', label: 'PSR Document' },
          { name: 'psr_verified', label: 'PSR Verified', readonly: true },
          { name: 'tds_amount', label: 'TDS Withheld Amount', readonly: true }
        ] },
      { tab: 'technical', title: 'Technical Grading & Diagnostic',
        fields: [
          { name: 'grade', label: 'Grade (from the grading certificate)', readonly: true },
          { name: 'refurb_grade_id', label: 'Final Graded Class' },
          { name: 'battery_health_pct', label: 'Battery Health (%) - from the QA', readonly: true },
          { name: 'wipe_certificate_id', label: 'Data Sanitization Certificate' }
        ] },
      { tab: 'lifecycle', title: 'Refurbishment Workshop Integration',
        fields: [
          { name: 'workshop_job_id', label: 'Origin Workshop Job', readonly: true },
          { name: 'consignment_id', label: 'Collection Consignment', readonly: true },
          { name: 'labour_cost', label: 'Direct Labour Cost', readonly: true },
          { name: 'parts_cost', label: 'Direct Parts Cost', readonly: true },
          { name: 'steps_cost', label: 'Costed Refurbishment Steps', readonly: true },
          { name: 'first_pass_cost', label: 'First-Pass Work', readonly: true },
          { name: 'rework_cost', label: 'Rework After a Failed QA', readonly: true },
          { name: 'refurbishment_cost', label: 'Total Refurbishment Cost', readonly: true },
          { name: 'inventory_valuation', label: 'Inventory Valuation', readonly: true }
        ] },
      { tab: 'governance', title: 'Four-Eyes Settlement Approval (M63)',
        fields: [
          { name: 'settlement_method', required: true, label: 'Settlement Method' },
          { name: 'settlement_bank_account_id', label: "Seller's Bank Account / bKash-Nagad Wallet" },
          { name: 'payout_approval_state', label: 'Payout Approval State', readonly: true },
          { name: 'approval_state', label: 'Routed Approval', readonly: true },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'payout_requested_by_id', label: 'Requested By', readonly: true },
          { name: 'payout_approved_by_id', label: 'Approver', readonly: true },
          { name: 'payout_approved_at', label: 'Approval Timestamp', readonly: true },
          { name: 'payout_approved_partner_id', label: 'Approved Payee', readonly: true },
          { name: 'payout_approved_net', label: 'Approved Net', readonly: true },
          { name: 'payout_execution_id', label: 'Treasury Execution Reference', readonly: true },
          { name: 'withholding_line_id', label: 'TDS Register Line (M51)', readonly: true }
        ] },
      { tab: 'governance', title: 'Resale Marketplace Channel Allocation',
        fields: [
          { name: 'resale_channel', label: 'Target Resale Channel' },
          { name: 'resale_listed_on', label: 'Marketplace Listing Date (stamped by Resale Ready)', readonly: true },
          { name: 'resale_value', label: 'Suggested Resale Price (a starting point; the listing price is approved)' },
          { name: 'listing_price', label: 'Approved Listing Price', readonly: true },
          { name: 'marketplace_seller_id', label: 'Merchant / Seller Account' },
          { name: 'graded_stock_id', label: 'Graded Stock Unit', readonly: true },
          { name: 'company_id', label: 'Operating Entity' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit Hub (fixed once the offer is sent)' },
          { name: 'branch_id', label: 'Intake Branch' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-valuation': {
    kind: 'model_form',
    model: 'fix.tradein.valuation',
    title: 'Automated Valuation File',
    back: 'M14-valuation',
    status: { field: 'state', labels: { draft: 'Draft', applied: 'Applied', superseded: 'Superseded' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '📄', badge: '4' },
      { id: 'pricing', label: '2. Reference Pricing', bn: '২. বেঞ্চমার্ক মূল্য', icon: '৳', badge: '7' },
      { id: 'technical', label: '3. Condition Factor', bn: '৩. শর্ত গুণাঙ্ক', icon: '⚙️', badge: '3' },
      { id: 'lifecycle', label: '4. Valuer & Override', bn: '৪. মূল্যায়নকারী ও ব্যত্যয়', icon: '✍️', badge: '6' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Valuation Run Master',
        fields: [
          { name: 'name', label: 'Valuation Run ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request (before the offer is accepted)', domain: [['state', 'in', ['draft', 'offered']]] },
          { name: 'method', label: 'Algorithm Method' },
          { name: 'state', label: 'Valuation State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Market Benchmark & Calculations',
        fields: [
          { name: 'device_model_id', label: 'Device Model', readonly: true },
          { name: 'grid_id', label: 'Governed Grid Price', readonly: true },
          { name: 'market_ref_price', label: 'Market Benchmark Price' },
          { name: 'computed_offer', label: 'Algorithm Computed Offer', readonly: true },
          { name: 'final_offer', label: 'Final Commercial Offer' },
          { name: 'applied_offer', label: 'Offer Applied', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'pricing', title: 'Offer Economics (FR-TRF-033, BRU-TRF-10)',
        note: 'Every offer is the resale estimate minus the expected refurbishment, logistics, data destruction and channel cost. A modelled margin below the floor is an override a valuation manager approves.',
        fields: [
          { name: 'resale_estimate', required: true, label: 'Resale Estimate' },
          { name: 'expected_refurb_cost', label: 'Expected Refurbishment Cost' },
          { name: 'expected_logistics_cost', label: 'Expected Logistics Cost' },
          { name: 'expected_destruction_cost', label: 'Expected Data Destruction Cost' },
          { name: 'expected_channel_cost', label: 'Expected Channel Cost' },
          { name: 'expected_cost_total', label: 'Expected Cost', readonly: true },
          { name: 'modelled_margin', label: 'Modelled Margin', readonly: true },
          { name: 'modelled_margin_pct', label: 'Modelled Margin (%)', readonly: true },
          { name: 'margin_floor_pct', label: 'Margin Floor (%)', readonly: true },
          { name: 'below_margin_floor', label: 'Below the Floor (needs approval)', readonly: true }
        ] },
      { tab: 'technical', title: 'Depreciation & Age Factors',
        fields: [
          { name: 'condition_factor_pct', label: 'Physical Condition Factor (%)' },
          { name: 'age_factor_pct', label: 'Depreciation Factor (%)' },
          { name: 'age_months', label: 'Device Age (Months)' }
        ] },
      { tab: 'lifecycle', title: 'Manual Review & Override Audit',
        fields: [
          { name: 'valuated_by_id', label: 'Valuation Specialist', readonly: true },
          { name: 'valuated_on', label: 'Valuation Date' },
          { name: 'is_override', label: 'Overrides the Grid', readonly: true },
          { name: 'override_reason', label: 'Override Justification' },
          { name: 'override_state', label: 'Override Approval', readonly: true },
          { name: 'override_approved_by_id', label: 'Override Approved By', readonly: true }
        ] },
      { tab: 'governance', title: 'Corporate Entity Scope',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-grid': {
    kind: 'model_form',
    model: 'fix.tradein.price.grid',
    title: 'Governed Price Grid Row',
    back: 'M14-grid',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', retired: 'Retired' } },
    tabs: [
      { id: 'general', label: '1. Price', bn: '১. মূল্য', icon: '৳', badge: '5' },
      { id: 'governance', label: '2. Approval', bn: '২. অনুমোদন', icon: '🏛️', badge: '4' }
    ],
    sections: [
      { tab: 'general', title: 'Market Reference Price',
        fields: [
          { name: 'device_model_id', required: true, label: 'Device Model' },
          { name: 'market_ref_price', required: true, label: 'Market Reference Price' },
          { name: 'valid_from', required: true, label: 'Valid From' },
          { name: 'notes', label: 'Source of the Price' },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'governance', title: 'Valuation Manager Approval',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'approved_at', label: 'Approved On', readonly: true },
          { name: 'company_id', label: 'Company' }
        ] }
    ]
  },

  'M14-form-provenance': {
    kind: 'model_form',
    model: 'fix.tradein.provenance',
    title: 'Provenance Screening & Anti-Theft',
    back: 'M14-provenance',
    status: { field: 'state', labels: { pending: 'Pending', cleared: 'Cleared', flagged: 'Flagged' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔍', badge: '4' },
      { id: 'pricing', label: '2. Evidence', bn: '২. প্রমাণ', icon: '⏱️', badge: '5' },
      { id: 'technical', label: '3. Blacklist & Stolen', bn: '৩. ব্ল্যাকলিস্ট ও চুরি', icon: '🛡️', badge: '7' },
      { id: 'lifecycle', label: '4. BTRC NEIR & NID', bn: '৪. বিটিআরসি এনইআইআর', icon: '🇧🇩', badge: '4' },
      { id: 'governance', label: '5. Governance & Notes', bn: '৫. নিয়ন্ত্রণ ও নোট', icon: '📝', badge: '4' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Screening Subject',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request', domain: [['state', 'not in', ['closed', 'rejected']]] },
          { name: 'imei', required: true, label: 'Primary IMEI' },
          { name: 'state', label: 'Clearance Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Screening Evidence',
        fields: [
          { name: 'evidence_attachment_id', label: 'Lookup Evidence / NID Card Scan' },
          { name: 'evidence_ref', label: 'Lookup Reference' },
          { name: 'checked_on', label: 'Cleared On', readonly: true },
          { name: 'cleared_by_id', label: 'Cleared By (Provenance Officer)', readonly: true },
          { name: 'cleared_at', label: 'Cleared At', readonly: true }
        ] },
      { tab: 'technical', title: 'Anti-Theft & Stolen Database Checks',
        fields: [
          { name: 'stolen_checked', label: 'Police Stolen DB Verified', readonly: true },
          { name: 'stolen_hit', label: 'Stolen Record Hit (raise only)' },
          { name: 'blacklist_checked', label: 'GSMA Blacklist Verified', readonly: true },
          { name: 'blacklist_hit', label: 'Blacklist Hit Flag (raise only)' },
          { name: 'lock_status', label: 'Activation Lock (Find My / FRP)' },
          { name: 'warranty_checked', label: 'OEM Warranty Verified', readonly: true },
          { name: 'warranty_active', label: 'Active OEM Coverage', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Bangladesh Telecommunication Regulatory Commission (BTRC) NEIR',
        fields: [
          { name: 'btrc_neir_checked', label: 'BTRC NEIR Queried', readonly: true },
          { name: 'btrc_neir_status', label: 'NEIR Status (unchecked until the NEIR relaunch)', readonly: true },
          { name: 'customer_nid_no', label: 'Seller NID Sighted' },
          { name: 'customer_nid_verified', label: 'NID Verified by the Officer', readonly: true }
        ] },
      { tab: 'governance', title: 'Security Notes & Company',
        fields: [
          { name: 'notes', label: 'Investigator Notes' },
          { name: 'flag_reason', label: 'Flag Reason', readonly: true },
          { name: 'flagged_by_id', label: 'Flagged By', readonly: true },
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-settlement': {
    kind: 'model_form',
    model: 'fix.tradein.request',
    title: 'Settlement & Four-Eyes Payout',
    back: 'M14-settlement',
    /* settlement is captured on an EXISTING trade-in: opened blank it created a
     * request with no device or intake (2026-11-12). It asks which first. */
    newLabel: 'Settle a Trade-In',
    pickRecord: {
      label: 'Step 1 of 2: choose the trade-in to settle',
      note: 'Accepted trade-ins that are not closed or rejected.',
      search: 'Search trade-in / customer',
      choose: 'Settle this trade-in',
      cols: ['name', 'customer_id', 'graded_value', 'payout_approval_state', 'state'],
      domain: [['state', 'not in', ['draft', 'offered', 'closed', 'rejected']]],
      empty: 'No accepted trade-in is waiting for settlement. A trade-in reaches settlement once the customer accepts the offer.'
    },
    status: { field: 'payout_approval_state', labels: {
      none: 'Not Requested', pending: 'Approval Pending', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '👤', badge: '4' },
      { id: 'pricing', label: '2. Payout & Tax', bn: '২. মূল্য ও উৎসে কর', icon: '৳', badge: '10' },
      { id: 'technical', label: '3. Valuation Target', bn: '৩. মূল্যায়ন রেফারেন্স', icon: '📱', badge: '3' },
      { id: 'lifecycle', label: '4. Four-Eyes Authorization', bn: '৪. চার-চক্ষু অনুমোদন', icon: '👔', badge: '9' },
      { id: 'governance', label: '5. Treasury & Ops', bn: '৫. ট্রেজারি ও পরিচালনা', icon: '🏦', badge: '5' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Settlement Beneficiary',
        fields: [
          { name: 'name', label: 'Trade-In Reference', readonly: true },
          { name: 'customer_id', label: 'Customer Account' },
          { name: 'customer_nid', label: 'National ID / Tax Identity' },
          { name: 'state', label: 'Trade-In State', readonly: true }
        ] },
      { tab: 'pricing', title: 'How the Seller Is Paid (FR-TRF-007)',
        note: 'Mobile money, bank transfer or cash. The payout approval covers the method and the account: changing either after it voids the approval.',
        fields: [
          { name: 'settlement_method', required: true, label: 'Settlement Method' },
          { name: 'settlement_bank_account_id', label: "Seller's Bank Account / bKash-Nagad Wallet" }
        ] },
      { tab: 'pricing', title: 'Settlement & Statutory Withholding (ITA 2023)',
        fields: [
          { name: 'graded_value', label: 'Graded Payout Value (below the offer only through a Physical Intake Verification)', readonly: true },
          { name: 'revision_state', label: 'Revised Offer', readonly: true },
          { name: 'tds_applicable', label: 'TDS Applicable' },
          { name: 'tds_section', label: 'TDS Section' },
          { name: 'tds_rate_pct', label: 'TDS Rate (%)' },
          { name: 'taxpayer_tin', label: 'Seller e-TIN' },
          { name: 'psr_attachment_id', label: 'PSR Document' },
          { name: 'psr_verified', label: 'PSR Verified', readonly: true },
          { name: 'tds_amount', label: 'Withheld TDS (BDT)', readonly: true },
          { name: 'net_payout', label: 'Net Payable via MFS/Bank', readonly: true }
        ] },
      { tab: 'technical', title: 'Device & Graded Unit Reference',
        fields: [
          { name: 'device_model_id', label: 'Device Model', readonly: true },
          { name: 'grade', label: 'Inspection Grade' },
          { name: 'graded_stock_id', label: 'Graded Stock Inventory Master', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'DOFA Four-Eyes Verification (M63 inbox)',
        fields: [
          { name: 'payout_approval_state', label: 'Payout Stage', readonly: true },
          { name: 'approval_state', label: 'Routed Approval', readonly: true },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'dofa_justification', label: 'Business Justification' },
          { name: 'payout_requested_by_id', label: 'Submitted By (Agent)', readonly: true },
          { name: 'payout_approved_by_id', label: 'Authorized Approver', readonly: true },
          { name: 'payout_approved_at', label: 'Authorization Timestamp', readonly: true },
          { name: 'payout_approved_partner_id', label: 'Approved Payee', readonly: true },
          { name: 'payout_approved_net', label: 'Approved Net', readonly: true }
        ] },
      { tab: 'governance', title: 'Treasury Execution & Operating Hub',
        fields: [
          { name: 'payout_execution_id', label: 'Payment Gateway / Journal Reference', readonly: true },
          { name: 'withholding_line_id', label: 'TDS Register Line (M51)', readonly: true },
          { name: 'withholding_certificate_no', label: 'TDS Certificate No', readonly: true },
          { name: 'company_id', label: 'Company' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ] },
      { tab: 'vault', title: 'Settlement Voucher Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-refurb': {
    kind: 'model_form',
    model: 'fix.refurbishment',
    title: 'Refurbishment Work Order',
    back: 'M14-orders',
    status: { field: 'state', labels: { pending: 'Pending', in_progress: 'In Progress', done: 'Done' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔧', badge: '4' },
      { id: 'pricing', label: '2. Job Costing', bn: '২. কার্য ব্যয়', icon: '৳', badge: '4' },
      { id: 'technical', label: '3. Technical Routing', bn: '৩. কারিগরি বরাদ্দ', icon: '👨‍🔧', badge: '5' },
      { id: 'lifecycle', label: '4. Observations', bn: '৪. পর্যবেক্ষণ', icon: '📋', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Refurbishment Step Identification',
        fields: [
          { name: 'name', label: 'Work Order ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request (in refurbishment)', domain: [['state', '=', 'refurbished']] },
          { name: 'step', label: 'Refurbishment Stage' },
          { name: 'state', label: 'Progress Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Job Costing & Absorption',
        fields: [
          { name: 'labor_cost', label: 'Allocated Labor Cost' },
          { name: 'parts_cost', label: 'BOM Replacement Parts Cost' },
          { name: 'total_cost', label: 'Total Step Cost', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'technical', title: 'Technician Assignment',
        fields: [
          { name: 'technician_id', label: 'Assigned Technician' },
          { name: 'operating_unit_id', label: 'Refurbishment Center' },
          { name: 'started_at', label: 'Started', readonly: true },
          { name: 'completed_at', label: 'Completed', readonly: true },
          { name: 'completed_by_id', label: 'Completed By', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Technician Log & Repair Observations',
        fields: [
          { name: 'notes', label: 'Step Procedure & Diagnostic Notes' }
        ] },
      { tab: 'lifecycle', title: 'Rework After a Failed QA (FR-TRF-036)',
        note: 'A step added while the latest QA of the unit failed is rework: it states its cause, and its cost is kept apart from first-pass work.',
        fields: [
          { name: 'is_rework', label: 'Rework', readonly: true },
          { name: 'rework_qa_id', label: 'Failed QA', readonly: true },
          { name: 'rework_cause', label: 'Rework Cause' },
          { name: 'rework_notes', label: 'Rework Detail' }
        ] },
      { tab: 'governance', title: 'Corporate Entity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Work Evidence (FR-TRF-013, FR-TRF-014)',
        note: 'Cosmetic work is recorded with before and after photographs. An activation lock is removed only on the documented proof of ownership given by the seller (BRU-TRF-22).',
        fields: [
          { name: 'before_photo_id', label: 'Before Photo' },
          { name: 'after_photo_id', label: 'After Photo' },
          { name: 'activation_lock_removed', label: 'Activation Lock Removed' },
          { name: 'ownership_proof_id', label: "Seller's Proof of Ownership" }
          ] }
    ]
  },

  'M14-form-qa': {
    kind: 'model_form',
    model: 'fix.refurb.qa',
    title: 'QA & Battery Health Dossier',
    back: 'M14-qa',
    status: { field: 'qa_state', labels: { pending: 'Pending', pass: 'Passed', fail: 'Failed' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔍', badge: '4' },
      { id: 'pricing', label: '2. Pass Metrics', bn: '২. পাসের অনুপাত', icon: '📊', badge: '1' },
      { id: 'technical', label: '3. Diagnostics & Battery', bn: '৩. ব্যাটারি ও ডায়াগনস্টিকস', icon: '🔋', badge: '3' },
      { id: 'lifecycle', label: '4. Inspector Log', bn: '৪. পরিদর্শক লগ', icon: '✍️', badge: '4' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Quality Assurance Docket',
        fields: [
          { name: 'name', label: 'QA Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request (in refurbishment)', domain: [['state', '=', 'refurbished']] },
          { name: 'refurbishment_id', label: 'Refurbishment Step' },
          { name: 'qa_state', label: 'Quality Assessment (from the results)', readonly: true }
        ] },
      { tab: 'pricing', title: 'Test Metrics',
        fields: [
          { name: 'pass_pct', label: 'Diagnostic Pass Rate (%)', readonly: true }
        ] },
      { tab: 'technical', title: 'Battery Health & Automated Suite',
        note: 'With test results recorded in the protocol grid, the totals are counted from them when the result is submitted.',
        fields: [
          { name: 'battery_health_pct', label: 'Battery Health (%)' },
          { name: 'tests_passed', label: 'Automated Tests Passed' },
          { name: 'tests_total', label: 'Total Test Cases' }
        ] },
      { tab: 'lifecycle', title: 'Inspector Evaluation & Sign-off',
        fields: [
          { name: 'inspector_id', label: 'Lead QA Inspector' },
          { name: 'inspected_by_id', label: 'Submitted By', readonly: true },
          { name: 'checked_on', label: 'Submitted On', readonly: true },
          { name: 'notes', label: 'Defect Analysis' }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ],
    lines: {
      field: 'test_ids',
      title: 'QA Protocol - one row per test (FR-TRF-017)',
      note: 'Hardware, ports, display, camera, connectivity, thermal, battery and software: each measured result with its outcome. Frozen once the result is submitted.',
      fields: [
        { name: 'test_code', required: true, label: 'Test' },
        { name: 'expected', label: 'Expected' },
        { name: 'measured', label: 'Measured' },
        { name: 'outcome', required: true, label: 'Outcome' },
        { name: 'equipment_ref', label: 'Equipment / Tool' }
      ]
    }
  },

  'M14-form-grade': {
    kind: 'model_form',
    model: 'fix.tradein.grade',
    title: 'Grading Certificate',
    back: 'M14-grading',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🏷️', badge: '3' },
      { id: 'pricing', label: '2. Grade Output', bn: '২. গ্রেড স্তর', icon: '🎖️', badge: '1' },
      { id: 'technical', label: '3. Physical Dimensions', bn: '৩. বহিরাঙ্গ ও স্ক্রিন', icon: '📐', badge: '4' },
      { id: 'lifecycle', label: '4. Grading Sign-off', bn: '৪. গ্রেডার নিরীক্ষা', icon: '👨‍🔬', badge: '3' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Grading Docket',
        fields: [
          { name: 'name', label: 'Grade Certificate ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request (in refurbishment)', domain: [['state', '=', 'refurbished']] }
        ] },
      { tab: 'pricing', title: 'Grade Classification (BRU-TRF-12/13/14)',
        note: 'The grade is computed from the axes and the battery health: the worst axis sets it, and a battery below the minimum of a grade drops it. Leave the grade blank to take the computed one. A different grade is an override by a Refurbishment Supervisor with a justification, never by the person who ran the QA.',
        fields: [
          { name: 'computed_grade', label: 'Computed Grade', readonly: true },
          { name: 'grade', label: 'Grade Recorded (blank = computed)' },
          { name: 'battery_minimum_pct', label: 'Battery Minimum of the Grade (%)', readonly: true },
          { name: 'is_override', label: 'Supervisor Override', readonly: true },
          { name: 'override_reason', label: 'Override Justification' },
          { name: 'override_by_id', label: 'Overridden By', readonly: true },
          { name: 'override_at', label: 'Overridden At', readonly: true },
          { name: 'qa_id', label: 'QA Result Used', readonly: true }
        ] },
      { tab: 'technical', title: 'Multi-Axis Assessment',
        fields: [
          { name: 'cosmetic_grade', label: 'Cosmetic / Housing Condition' },
          { name: 'functional_grade', label: 'Hardware Functionality' },
          { name: 'screen_grade', label: 'Display Panel Clarity' },
          { name: 'battery_health_pct', label: 'Battery Capacity (%)' }
        ] },
      { tab: 'lifecycle', title: 'Inspector Authentication',
        fields: [
          { name: 'inspector_id', label: 'Certified Grader' },
          { name: 'graded_on', label: 'Graded Timestamp' },
          { name: 'notes', label: 'Defect Explanations' }
        ] },
      { tab: 'governance', title: 'Corporate Entity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-harvest': {
    kind: 'model_form',
    model: 'fix.tradein.harvest',
    title: 'Harvest to Parts Dossier',
    back: 'M14-harvest',
    status: { field: 'state', labels: { pending: 'Pending', harvested: 'Harvested', scrapped: 'Scrapped' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '📦', badge: '4' },
      { id: 'pricing', label: '2. Recovered Value', bn: '২. উদ্ধারকৃত মূল্য', icon: '৳', badge: '3' },
      { id: 'technical', label: '3. Part Specifications', bn: '৩. যন্ত্রাংশের বিবরণ', icon: '🔩', badge: '5' },
      { id: 'lifecycle', label: '4. Harvest Timeline', bn: '৪. সংগ্রহের সময়কাল', icon: '📅', badge: '3' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Harvest Case',
        fields: [
          { name: 'name', label: 'Harvest Record ID', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In Request (parts only, written off)', domain: [['state', '=', 'parts_only']] },
          { name: 'state', label: 'Harvesting State', readonly: true },
          { name: 'receipt_id', label: 'M15 Goods Receipt', readonly: true }
        ] },
      { tab: 'pricing', title: 'Inventory Valuation of Harvested Spares',
        fields: [
          { name: 'unit_value', label: 'Standard Unit Value (BDT)' },
          { name: 'total_value', label: 'Total Valuation Absorbed', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'technical', title: 'Harvested Component Definition',
        fields: [
          { name: 'component', label: 'Component Category' },
          { name: 'part_id', label: 'M15 Spare Part' },
          { name: 'part_name', required: true, label: 'Spare Part SKU / Name' },
          { name: 'quantity', required: true, label: 'Quantity Salvaged' },
          { name: 'target', label: 'Destination Stock / Refurb Buffer' }
        ] },
      { tab: 'lifecycle', title: 'Dismantling Execution',
        fields: [
          { name: 'harvested_on', label: 'Harvest Date' },
          { name: 'harvested_by_id', label: 'Harvested By', readonly: true },
          { name: 'notes', label: 'Extraction Conditions' }
        ] },
      { tab: 'governance', title: 'Corporate Entity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M14-form-warranty': {
    kind: 'model_form',
    model: 'fix.tradein.warranty',
    title: 'Refurbished Warranty Master',
    back: 'M14-wty',
    /* issued by the resale itself, every field read-only: a record, not data entry */
    create: false, pick: 'A refurbished warranty is issued when the unit is resold: open one from Refurb Warranty.',
    status: { field: 'state', labels: { active: 'Active', expired: 'Expired', void: 'Void' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🛡️', badge: '4' },
      { id: 'pricing', label: '2. Claims Liability', bn: '২. দাবির দায়', icon: '⚠️', badge: '1' },
      { id: 'technical', label: '3. Coverage Term', bn: '৩. কভারেজের মেয়াদ', icon: '📅', badge: '3' },
      { id: 'lifecycle', label: '4. Terms & Exclusions', bn: '৪. শর্ত ও ব্যতিক্রম', icon: '📜', badge: '2' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Policy Header (issued by the resale)',
        fields: [
          { name: 'name', label: 'Warranty Policy ID', readonly: true },
          { name: 'tradein_id', label: 'Origin Trade-In', readonly: true },
          { name: 'graded_stock_ref', label: 'Resold Stock Unit', readonly: true },
          { name: 'state', label: 'Coverage Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Claims Experience',
        fields: [
          { name: 'claims_count', label: 'Service Claims Registered', readonly: true }
        ] },
      { tab: 'technical', title: 'Validity Window',
        fields: [
          { name: 'months', label: 'Warranty Duration (Months)', readonly: true },
          { name: 'start_date', label: 'Coverage Start Date', readonly: true },
          { name: 'end_date', label: 'Coverage Expiration Date', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Policy Terms',
        fields: [
          { name: 'terms', label: 'Refurbished Warranty Terms & Conditions', readonly: true },
          { name: 'void_reason', label: 'Void Reason', readonly: true }
        ] },
      { tab: 'governance', title: 'Issuing Legal Entity',
        fields: [
          { name: 'company_id', label: 'Company', readonly: true }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  /* ============ M14 SUB-MODULE CAPTURE (2026-11-13) ==================
   * Two steps a person performs on an EXISTING trade-in. Each picks the unit
   * first; the value it captures is a plain field the model still accepts at
   * that stage, and the gate itself is the list action that follows. */
  'M14-form-bulk': {
    kind: 'model_form',
    model: 'fix.bulk.buyback',
    title: 'Corporate Bulk Buy-Back Lot',
    back: 'M14-bulk',
    status: { field: 'state', labels: { draft: 'Draft', received: 'Received', closed: 'Closed' } },
    tabs: [
      { id: 'general', label: '1. Client & Contract', bn: '১. গ্রাহক ও চুক্তি', icon: '🏢', badge: '6' },
      { id: 'pricing', label: '2. Lot Pricing', bn: '২. লট মূল্য', icon: '৳', badge: '4' },
      { id: 'lifecycle', label: '3. Reconciliation', bn: '৩. মিলকরণ', icon: '✅', badge: '10' }
    ],
    sections: [
      { tab: 'general', title: 'Corporate Client & Buy-Back Contract',
        fields: [
          { name: 'name', label: 'Lot Reference', readonly: true },
          { name: 'partner_id', required: true, label: 'Corporate Client' },
          { name: 'contract_ref', label: 'Buy-Back Contract / PO Reference' },
          { name: 'account_manager_id', label: 'Account Manager' },
          { name: 'operating_unit_id', label: 'Receiving Operating Unit' },
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'pricing', title: 'Lot Pricing Basis',
        note: 'Per-unit: every unit is valued on the governed price grid like any trade-in. Agreed lot price: the contract fixes a total, and the offers made on the units are shown beside it so a gap is visible.',
        fields: [
          { name: 'lot_price_basis', required: true, label: 'Lot Pricing' },
          { name: 'lot_price', label: 'Agreed Lot Price (lot pricing only)' },
          { name: 'offered_total', label: 'Offers Made on the Units of the Lot', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'lifecycle', title: 'Reconciliation Against the Declared Asset List (BRU-TRF-23)',
        note: 'Receive Lot & Open Intakes on Corporate Bulk Buy-Back opens one trade-in per declared asset, linked to the registered device when its serial or IMEI matches. The lot closes only when every declared asset has an intake or a documented exception.',
        fields: [
          { name: 'state', label: 'Lot State', readonly: true },
          { name: 'declared_asset_count', label: 'Declared Assets', readonly: true },
          { name: 'matched_count', label: 'Reconciled to an Intake', readonly: true },
          { name: 'exception_count', label: 'Documented Exceptions', readonly: true },
          { name: 'pending_count', label: 'Not Yet Reconciled', readonly: true },
          { name: 'received_by_id', label: 'Received By', readonly: true },
          { name: 'received_at', label: 'Received At', readonly: true },
          { name: 'closed_by_id', label: 'Closed By', readonly: true },
          { name: 'closed_at', label: 'Closed At', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ],
    lines: {
      field: 'asset_ids',
      title: 'Declared Assets - the asset list of the client',
      note: 'One row per asset the client declares (serial or IMEI as on their list). The intake is opened by Receive Lot, never typed; an asset that does not arrive, is retained or is declined is reconciled with a documented exception.',
      fields: [
        { name: 'asset_tag', label: 'Client Asset Tag' },
        { name: 'serial_number', required: true, label: 'Serial / IMEI' },
        { name: 'description', label: 'Make / Model' },
        { name: 'tradein_id', label: 'Trade-In Intake', readonly: true },
        { name: 'tradein_state', label: 'Intake State', readonly: true },
        { name: 'status', label: 'Reconciliation', readonly: true },
        { name: 'exception_reason', label: 'Documented Exception' }
      ]
    }
  },

  'M14-form-wipe': {
    kind: 'model_form',
    model: 'fix.tradein.request',
    title: 'Destruction Certificate Attachment',
    newLabel: 'Attach Destruction Certificate',
    back: 'M14-gate',
    pickRecord: {
      label: 'Step 1 of 2: choose the collected unit',
      note: 'Collected trade-ins that have not passed the destruction gate.',
      search: 'Search trade-in / customer',
      choose: 'Attach its certificate',
      cols: ['name', 'customer_id', 'device_id', 'wipe_certificate_id', 'state'],
      domain: [['state', '=', 'collected']],
      empty: 'No collected unit is waiting at the destruction gate. A trade-in reaches the gate when Collect is pressed on Trade-In Intake.'
    },
    status: { field: 'state', labels: { collected: 'Collected', wiped: 'Data Wiped' } },
    sections: [
      { title: 'Step 2 of 2: The M06 Destruction Certificate (FR-TRF-011)',
        note: 'Data destruction is performed, certified and verified in M06 Data Services: M14 never issues a certificate (segregation of duties). Attach the verified certificate for THIS unit, save, then press Data Wipe on Destruction Gate: it refuses a certificate that is not verified, whose log changed after verification, or that certifies another media serial.',
        fields: [
          { name: 'name', label: 'Trade-In Reference', readonly: true },
          { name: 'customer_id', label: 'Seller', readonly: true },
          { name: 'device_id', label: 'Device (media serial checked against the certificate)', readonly: true },
          { name: 'state', label: 'Trade-In State', readonly: true },
          { name: 'wipe_certificate_id', required: true, label: 'Verified M06 Destruction Certificate',
            domain: [['sanitization_status', '=', 'verified']] }
        ] }
    ]
  },

  'M14-form-resale': {
    kind: 'model_form',
    model: 'fix.tradein.request',
    title: 'Resale Listing Preparation',
    newLabel: 'Prepare a Resale Listing',
    back: 'M14-resale-prep',
    pickRecord: {
      label: 'Step 1 of 2: choose the graded unit to list',
      note: 'Graded units that are not parts-only (grade E is harvested, never resold).',
      search: 'Search trade-in / model',
      choose: 'Prepare its listing',
      cols: ['name', 'device_model_id', 'grade', 'refurb_grade_id', 'resale_value', 'state'],
      domain: [['state', '=', 'graded'], ['grade', '!=', 'e']],
      empty: 'No graded unit is waiting for resale. A trade-in is graded by Grade on Trade-In Intake once its QA and grading certificate are recorded.'
    },
    status: { field: 'state', labels: { graded: 'Graded', resale_ready: 'Resale Ready' } },
    sections: [
      { title: 'Graded Unit',
        fields: [
          { name: 'name', label: 'Trade-In Reference', readonly: true },
          { name: 'device_model_id', label: 'Device Model', readonly: true },
          { name: 'grade', label: 'Grade', readonly: true },
          { name: 'refurb_grade_id', label: 'M37 Grade (sets the stock class)', readonly: true },
          { name: 'battery_health_pct', label: 'Battery Health (%) - disclosed to the buyer', readonly: true },
          { name: 'state', label: 'Trade-In State', readonly: true }
        ] },
      { title: 'Step 2 of 2: Channel & Price (FR-TRF-021, FR-TRF-022)',
        note: 'Save, then press Propose Listing Price on Resale Preparation: a pricing manager who did not propose or enter the price approves it (never below landed cost without an approved markdown). Resale Ready then stocks the unit at its cost on the refurbished-stock ledger and lists it at the approved price.',
        fields: [
          { name: 'resale_channel', required: true, label: 'Resale Channel' },
          { name: 'resale_value', required: true, label: 'Suggested Listing Price (BDT, VAT inclusive)' },
          { name: 'listing_price', label: 'Approved Listing Price', readonly: true },
          { name: 'listing_price_state', label: 'Price Approval', readonly: true },
          { name: 'marketplace_seller_id', label: 'Marketplace Merchant Account (marketplace channel)' },
          { name: 'resale_listed_on', label: 'Listing Date', readonly: true }
        ] }
    ]
  },

  /* ============ M14 CAPTURE PASS 2 (2026-11-19) ======================= */
  'M14-form-intake-check': {
    kind: 'model_form',
    model: 'fix.tradein.intake.check',
    title: 'Physical Intake Verification',
    back: 'M14-intake-check',
    status: { field: 'state', labels: { draft: 'Draft', confirmed: 'Confirmed' } },
    tabs: [
      { id: 'general', label: '1. Unit & Declaration', bn: '১. ইউনিট ও ঘোষণা', icon: '📱', badge: '5' },
      { id: 'technical', label: '2. As Received', bn: '২. প্রাপ্ত অবস্থা', icon: '🔍', badge: '6' },
      { id: 'governance', label: '3. Value & Sign-off', bn: '৩. মূল্য ও স্বাক্ষর', icon: '✍️', badge: '5' }
    ],
    sections: [
      { tab: 'general', title: 'The Unit and What the Customer Declared',
        fields: [
          { name: 'name', label: 'Verification Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Trade-In (accepted, payout not yet requested)',
            domain: [['state', 'in', ['accepted', 'collected', 'wiped', 'refurbished', 'graded', 'resale_ready']], ['payout_approval_state', 'not in', ['pending', 'approved']]] },
          { name: 'declared_condition', label: 'Declared Condition', readonly: true },
          { name: 'accepted_value', label: 'Accepted Offer', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { tab: 'technical', title: 'Verified on Receipt (FR-TRF-005)',
        note: 'Check the unit received against the declaration. Where it is worse, describe the difference and attach the photographs: only then may the value go below the accepted offer (BRU-TRF-09).',
        fields: [
          { name: 'identity_matches', label: 'Serial / IMEI Matches the Request' },
          { name: 'verified_condition', required: true, label: 'Verified Condition' },
          { name: 'condition_differs', label: 'Worse Than Declared', readonly: true },
          { name: 'accessories_as_declared', label: 'Accessories as Declared' },
          { name: 'accessories_notes', label: 'Accessories Missing or Extra' },
          { name: 'difference_notes', label: 'What Differs From the Declaration' },
          { name: 'evidence_attachment_id', label: 'Photographic Evidence' }
        ] },
      { tab: 'governance', title: 'Verified Value',
        note: 'Confirm Verification on Physical Intake Verification makes this the graded value of the trade-in. A lower value is a revised offer the customer must accept. The person who valued the unit does not confirm it.',
        fields: [
          { name: 'verified_value', required: true, label: 'Verified Value (BDT)' },
          { name: 'checked_by_id', label: 'Verified By', readonly: true },
          { name: 'checked_at', label: 'Verified At', readonly: true },
          { name: 'company_id', label: 'Company' }
        ] }
    ]
  },

  'M14-form-return': {
    kind: 'model_form',
    model: 'fix.refurb.return',
    title: 'Refurbished Unit Return',
    back: 'M14-returns',
    status: { field: 'state', labels: { draft: 'Draft', received: 'Received', decided: 'Decided' } },
    tabs: [
      { id: 'general', label: '1. Sold Unit', bn: '১. বিক্রীত ইউনিট', icon: '📦', badge: '6' },
      { id: 'technical', label: '2. Failure', bn: '২. ত্রুটি', icon: '⚠️', badge: '5' },
      { id: 'governance', label: '3. Decision', bn: '৩. সিদ্ধান্ত', icon: '⚖️', badge: '6' }
    ],
    sections: [
      { tab: 'general', title: 'The Sold Refurbished Unit',
        fields: [
          { name: 'name', label: 'Return Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Sold Unit (trade-in)', domain: [['graded_stock_id.state', '=', 'sold']] },
          { name: 'graded_stock_id', label: 'Graded Stock Unit', readonly: true },
          { name: 'warranty_id', label: 'Refurbished Warranty', readonly: true },
          { name: 'grade_at_sale', label: 'Grade at Sale', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { tab: 'technical', title: 'What Came Back (FR-TRF-026)',
        note: 'The failure code is what the grading analysis reads each period (BRU-TRF-24). The unit is taken back within the return window or its refurbished warranty.',
        fields: [
          { name: 'return_date', required: true, label: 'Return Date' },
          { name: 'reason', required: true, label: 'Return Reason' },
          { name: 'failure_code', label: 'Failure Code' },
          { name: 'description', label: 'What the Buyer Reports' },
          { name: 'evidence_attachment_id', label: 'Evidence' }
        ] },
      { tab: 'governance', title: 'Supervisor Decision',
        note: 'Receive Return on Refurbished Returns, then a Refurbishment Supervisor who did not receive it decides.',
        fields: [
          { name: 'within_terms', label: 'Within Return Window or Warranty', readonly: true },
          { name: 'outcome', label: 'Decision' },
          { name: 'decision_notes', label: 'Decision Notes' },
          { name: 'received_by_id', label: 'Received By', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'company_id', label: 'Company' }
        ] }
    ]
  },

  'M14-form-writeoff': {
    kind: 'model_form',
    model: 'fix.refurb.writeoff',
    title: 'Parts-Only Routing & Write-off',
    back: 'M14-writeoff',
    status: { field: 'state', labels: { draft: 'Draft', pending: 'Approval Pending', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'general', label: '1. Unit & Cause', bn: '১. ইউনিট ও কারণ', icon: '🔧', badge: '5' },
      { id: 'pricing', label: '2. Cost', bn: '২. খরচ', icon: '৳', badge: '4' },
      { id: 'governance', label: '3. Approval', bn: '৩. অনুমোদন', icon: '🏛️', badge: '5' }
    ],
    sections: [
      { tab: 'general', title: 'Why the Unit Cannot Be Sold (FR-TRF-020)',
        fields: [
          { name: 'name', label: 'Routing Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Unit (trade-in at intake, in refurbishment or graded)', domain: [['state', 'in', ['collected', 'wiped', 'refurbished', 'graded']]] },
          { name: 'cause', required: true, label: 'Cause' },
          { name: 'cause_notes', required: true, label: 'Why the Unit Cannot Be Sold' },
          { name: 'destination', required: true, label: 'Route To' }
        ] },
      { tab: 'pricing', title: 'Cost Written Off',
        note: 'For a cost-to-complete routing the cost to complete must exceed the resale estimate. The accumulated cost is taken from the unit when the routing is requested.',
        fields: [
          { name: 'resale_estimate', label: 'Resale Estimate' },
          { name: 'cost_to_complete', label: 'Cost to Complete' },
          { name: 'accumulated_cost', label: 'Accumulated Cost Written Off', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ] },
      { tab: 'governance', title: 'Two Signatures (BRU-TRF-19, section 13)',
        note: 'A Refurbishment Supervisor routes the unit; a Write-off Approver who did not route it approves. A harvest is refused until the routing to harvest is approved.',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'requested_by_id', label: 'Routed By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'rejection_reason', label: 'Rejection Reason', readonly: true },
          { name: 'company_id', label: 'Company' }
        ] }
    ]
  },

  /* A05 ERP M14-25 / D6: a markdown of a graded or listed unit. */
  'M14-form-markdown': {
    kind: 'model_form',
    model: 'fix.refurb.markdown',
    title: 'Refurbished Unit Markdown',
    newLabel: 'Markdown',
    back: 'M14-markdown',
    status: { field: 'state', labels: { draft: 'Draft', pending: 'Approval Pending', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'The Unit and Its New Price',
        note: 'Request Approval records the price before and the landed cost; a pricing manager who did not ask approves it. The unit is repriced and, where the price before VAT is below its carrying cost, written down to that value (NRV).',
        fields: [
          { name: 'name', label: 'Markdown Reference', readonly: true },
          { name: 'tradein_id', required: true, label: 'Unit (graded or listed trade-in)', domain: [['state', 'in', ['graded', 'resale_ready']]] },
          { name: 'new_price', required: true, label: 'New Price (BDT, VAT inclusive)' },
          { name: 'reason', required: true, label: 'Why the Price Comes Down' },
          { name: 'current_price', label: 'Price Before', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M14:Trade-In Funnel': 'M14-rpt-funnel',
  'M14:Gate Compliance': 'M14-rpt-gate',
  'M14:Trade-In Margin by Model': 'M14-rpt-margin',
  'M14:Refurb Cost per Grade': 'M14-rpt-grade',
  'M14:Ageing & Markdown': 'M14-rpt-ageing',
  'M14:Resale Channel Performance': 'M14-rpt-channel',
  'M14:Harvest Yield': 'M14-rpt-harvest',
  'M14:Valuation Queue': 'M14-rpt-valqueue',
  'M14:Resale Listings': 'M14-rpt-resale',
  'M14:Unit Economics': 'M14-rpt-economics'
};

export const FORM_MODELS = {
  'M14:Trade-In Intake Dossier': 'fix.tradein.request',
  'M14:Automated Valuation File': 'fix.tradein.valuation',
  'M14:Governed Price Grid Row': 'fix.tradein.price.grid',
  'M14:Provenance Screening & Anti-Theft': 'fix.tradein.provenance',
  'M14:Settlement & Four-Eyes Payout': 'fix.tradein.request',
  'M14:Refurbishment Work Order': 'fix.refurbishment',
  'M14:QA & Battery Health Dossier': 'fix.refurb.qa',
  'M14:Grading Certificate': 'fix.tradein.grade',
  'M14:Harvest to Parts Dossier': 'fix.tradein.harvest',
  'M14:Destruction Certificate Attachment': 'fix.tradein.request',
  'M14:Resale Listing Preparation': 'fix.tradein.request',
  'M14:Corporate Bulk Buy-Back Lot': 'fix.bulk.buyback',
  'M14:Physical Intake Verification': 'fix.tradein.intake.check',
  'M14:Refurbished Unit Return': 'fix.refurb.return',
  'M14:Parts-Only Routing & Write-off': 'fix.refurb.writeoff',
  'M14:Refurbished Unit Markdown': 'fix.refurb.markdown'
};

export const FORM_CHIPS = {
  'M14:Trade-In Intake Dossier': 'M14-form-request',
  'M14:Automated Valuation File': 'M14-form-valuation',
  'M14:Governed Price Grid Row': 'M14-form-grid',
  'M14:Provenance Screening & Anti-Theft': 'M14-form-provenance',
  'M14:Settlement & Four-Eyes Payout': 'M14-form-settlement',
  'M14:Refurbishment Work Order': 'M14-form-refurb',
  'M14:QA & Battery Health Dossier': 'M14-form-qa',
  'M14:Grading Certificate': 'M14-form-grade',
  'M14:Harvest to Parts Dossier': 'M14-form-harvest',
  'M14:Destruction Certificate Attachment': 'M14-form-wipe',
  'M14:Resale Listing Preparation': 'M14-form-resale',
  'M14:Corporate Bulk Buy-Back Lot': 'M14-form-bulk',
  'M14:Physical Intake Verification': 'M14-form-intake-check',
  'M14:Refurbished Unit Return': 'M14-form-return',
  'M14:Parts-Only Routing & Write-off': 'M14-form-writeoff',
  'M14:Refurbished Unit Markdown': 'M14-form-markdown',
  'M14:__by_model__': {
    'fix.tradein.request': 'M14-form-request',
    'fix.tradein.valuation': 'M14-form-valuation',
    'fix.tradein.price.grid': 'M14-form-grid',
    'fix.tradein.provenance': 'M14-form-provenance',
    'fix.refurbishment': 'M14-form-refurb',
    'fix.refurb.qa': 'M14-form-qa',
    'fix.tradein.grade': 'M14-form-grade',
    'fix.tradein.harvest': 'M14-form-harvest',
    'fix.tradein.warranty': 'M14-form-warranty',
    'fix.bulk.buyback': 'M14-form-bulk',
    'fix.tradein.intake.check': 'M14-form-intake-check',
    'fix.refurb.return': 'M14-form-return',
    'fix.refurb.writeoff': 'M14-form-writeoff',
    'fix.refurb.markdown': 'M14-form-markdown'
  },
  'M14:__by_screen__': {
    'M14-intake': 'M14-form-request',
    'M14-bulk': 'M14-form-bulk',
    'M14-valuation': 'M14-form-valuation',
    'M14-grid': 'M14-form-grid',
    'M14-provenance': 'M14-form-provenance',
    'M14-gate': 'M14-form-wipe',
    'M14-settlement': 'M14-form-settlement',
    'M14-resale-prep': 'M14-form-resale',
    'M14-orders': 'M14-form-refurb',
    'M14-qa': 'M14-form-qa',
    'M14-grading': 'M14-form-grade',
    'M14-harvest': 'M14-form-harvest',
    'M14-wty': 'M14-form-warranty',
    'M14-intake-check': 'M14-form-intake-check',
    'M14-returns': 'M14-form-return',
    'M14-writeoff': 'M14-form-writeoff',
    'M14-markdown': 'M14-form-markdown'
  }
};

export const CREATE = {
  M14: { screen: 'M14-form-request', model: 'fix.tradein.request', label: 'Trade-In Request' }
};
