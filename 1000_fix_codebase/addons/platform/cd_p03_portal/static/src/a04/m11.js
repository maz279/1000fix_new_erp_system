/** @odoo-module **/
/* A04 · Commercial & Revenue — M11 Pricing & Rate Cards (v2 rebuild).
 * Registry-faithful: freg 97 (11 sub-modules), each with its capture.
 * Rate cards, dynamic rules, explanations and discount approvals are real;
 * price books/versions/floors/promotions/simulations/policies are new. */

export const MODULE = {
  area: 'A04', code: 'M11', en: 'Pricing & Rate Cards', title: 'M11 · Pricing & Rate Cards',
  bn: 'মূল্য ও রেট কার্ড', icon: '💲',
  desc: 'Price books and versions, labour/parts/brand rate cards, dynamic adjustment rules, discount governance, cost-plus floors, promotions, simulation and realised-price analytics.',
  kpis: [
    { l: 'Realised Margin', m: 'realised_margin', suffix: '%' },
    { l: 'Discount Leaks MTD', m: 'discount_leaks_mtd' },
    { l: 'Rate Cards Live', m: 'rate_cards_live' },
    { l: 'Brand Reimb. Rates', m: 'brand_reimb_rates' },
    { l: 'Simulations MTD', m: 'simulations_mtd' },
    { l: 'Margin Floors Breached', m: 'margin_floors_breached' }
  ],
  groups: [
    { en: 'Pricing Records', screens: [
      { id: 'M11-price-explanation', en: "Price Explanation", bn: "Price Explanation", t: 'g' }
    ]},
    { en: 'Price Books', screens: [
      { id: 'M11-books', en: 'Price Books', bn: 'প্রাইস বুক', t: 'g' },
      { id: 'M11-engine', en: 'Price Resolution Engine', bn: 'প্রাইস ইঞ্জিন', t: 'r' },
      { id: 'M11-versions', en: 'Versioning & Mass Changes', bn: 'ভার্সনিং', t: 'g' }
    ]},
    { en: 'Rate Cards', screens: [
      { id: 'M11-labour', en: 'Labour & Service Rate Cards', bn: 'শ্রম ও সার্ভিস রেট কার্ড', t: 'g' },
      { id: 'M11-parts', en: 'Parts Pricing Rules', bn: 'পার্টস মূল্য', t: 'g' },
      { id: 'M11-parts-schemes', en: 'Parts Pricing Schemes', bn: 'পার্টস মূল্য পদ্ধতি', t: 'g' },
      { id: 'M11-contract', en: 'Contract Rates', bn: 'চুক্তিভিত্তিক রেট', t: 'g' },
      { id: 'M11-brand', en: 'Brand Reimbursement Rates', bn: 'ব্র্যান্ড রেট', t: 'g' },
      { id: 'M11-adjust', en: 'Adjustment Rules', bn: 'সমন্বয় নিয়ম', t: 'g' },
      { id: 'M11-premiums', en: 'Premiums & Surcharges', bn: 'প্রিমিয়াম ও সারচার্জ', t: 'g' }
    ]},
    { en: 'Pricing Governance', screens: [
      { id: 'M11-discounts', en: 'Discount Governance', bn: 'ডিসকাউন্ট গভর্নেন্স', t: 'g' },
      { id: 'M11-floors', en: 'Cost-Plus & Margin Floors', bn: 'মার্জিন ফ্লোর', t: 'g' },
      { id: 'M11-promos', en: 'Promotions', bn: 'প্রমোশন', t: 'g' },
      { id: 'M11-changes', en: 'Rate & Floor Changes', bn: 'রেট ও ফ্লোর পরিবর্তন', t: 'g' },
      { id: 'M11-policies', en: 'Discount Ladder', bn: 'ডিসকাউন্ট ধাপ', t: 'g' },
      { id: 'M11-reasons', en: 'Discount Reason Codes', bn: 'ডিসকাউন্ট কারণ কোড', t: 'g' },
      { id: 'M11-mass', en: 'Mass Price Changes', bn: 'একযোগে মূল্য পরিবর্তন', t: 'g' },
      { id: 'M11-mass-lines', en: 'Mass Change Preview', bn: 'একযোগে পরিবর্তনের পূর্বরূপ', t: 'g' },
      { id: 'M11-differentials', en: 'Channel Differentials', bn: 'চ্যানেল মূল্য পার্থক্য', t: 'g' },
      { id: 'M11-breaks', en: 'Volume Breaks', bn: 'পরিমাণভিত্তিক মূল্য', t: 'g' },
      { id: 'M11-reviews', en: 'Pricing Reviews', bn: 'মূল্য পর্যালোচনা', t: 'g' },
      { id: 'M11-override-log', en: 'Price Override Record', bn: 'মূল্য পরিবর্তনের রেকর্ড', t: 'g' },
      { id: 'M11-rpt-exceptions', en: 'Price Exceptions', bn: 'মূল্য ব্যতিক্রম', t: 'r' },
      { id: 'M11-rpt-consistency', en: 'Price Consistency Monitor', bn: 'মূল্য সামঞ্জস্য', t: 'r' }
    ]},
    { en: 'Analytics', screens: [
      { id: 'M11-simulate', en: 'Price Simulation', bn: 'মূল্য সিমুলেশন', t: 'g' },
      { id: 'M11-realised', en: 'Realised-Price Analytics', bn: 'বাস্তব মূল্য বিশ্লেষণ', t: 'r' }
    ]}
  ],
  reports: ['Price Exceptions', 'Price Consistency Monitor', 'Realised Price vs Card', 'Discount Register by Approver', 'Rate-Card Utilisation', 'Margin by Service Line', 'Promotion Effectiveness', 'Brand Reimbursement Recovery', 'Floor vs Realised Rate'],
  forms: ['Price Book', 'Rate Card', 'Discount Policy', 'Promotion', 'Price Simulation Request', 'Dynamic Price Rule', 'Discount Approval', 'Price Floor', 'Price Book Version', 'Price Change Request', 'Brand Reimbursement Rate', 'Parts Pricing Scheme', 'Price Premium', 'Mass Price Change', 'Discount Reason Code', 'Below-Floor Override', 'Channel Differential', 'Volume Break'],
  cross: ['M37 Catalogue', 'M36 Quotations', 'M20 AR', 'M09 Warranty Claims'],
  /* M11 capture audit (2026-11-13): pages 1 and 6 offered no button, 9 and 11
   * no form chip, and three pages captured the wrong record:
   *  - Customer/Contract Pricing listed price books. A contract rate is a rate
   *    card in the engine's contract lane (min_tier 99 + contract no., BRU-
   *    PRC-11), and the Rate Card form did not even show the contract no., so
   *    no contract rate could be recorded at all.
   *  - Rate Cards and Parts Pricing listed every card, labour and parts alike.
   *  - Brand Reimbursement listed warranty claims (M09's record) under the
   *    heading "rates": the brand rate card the spec gives M11 (FR-PRC-015)
   *    did not exist. It is now fix.brand.reimbursement.rate.
   * Cost-Plus & Margin Floors, Rate & Floor Changes and the Discount Ladder
   * sat on no page. A price explanation stays engine-written (BRU-PRC-02): the
   * Pricing Engine page offers the what-if simulation an agent runs instead.
   * Pass 2 (2026-11-18), read against the spec's FRs rather than counted:
   *  - Parts Pricing could record a fixed price only; FR-PRC-013 (P0) prices
   *    parts by markup on cost, banded markup or a provenance-grade
   *    differential. "+ New" is now a Parts Pricing Scheme with cost bands.
   *  - Adjustment Rules held only the W7 marketplace/storefront dynamic rule;
   *    the urgency, after-hours, weekend, holiday, zone and distance premiums
   *    of FR-PRC-018/019 had no record. "+ New" is now a Price Premium.
   *  - Versioning & Approval moved one rate at a time; FR-PRC-024 / BRU-PRC-16
   *    ask for a previewed, approved, scheduled mass change with rollback.
   *  - Discount Governance took free text only; BRU-PRC-13 needs a reason
   *    code from a governed list (Discount Reason Codes).
   *  - A contract rate typed its contract number; it now names the M08
   *    contract and lapses with it (FR-PRC-016, AC-08).
   *  - The simulation asked for its inputs as JSON; they are fields now.
   * `domain` stays the LAST key (the mapping guard parses it there). */
  freg: { src: 97, sub: [
    ['1', 'Pricing Engine', 12, { model: 'fix.price.explanation', cols: ['name', 'rule_id', 'base_price', 'final_price', 'model_driven'], screens: ['M11-engine', 'M11-price-explanation', 'M11-simulate'], reports: ['Realised Price vs Card', 'Margin by Service Line'], forms: ['Price Simulation Request'], create: false }],
    ['2', 'Price Books', 10, { model: 'fix.price.book', cols: ['name', 'code', 'state', 'currency_id', 'active'], screens: ['M11-books', 'M11-versions'], reports: ['Realised Price vs Card'], forms: ['Price Book', 'Price Book Version'] }],
    ['3', 'Rate Cards', 11, { model: 'fix.rate.card', cols: ['name', 'product_code', 'line_type', 'unit_price', 'catalogue_item_id', 'min_tier', 'state'], screens: ['M11-labour'], reports: ['Rate-Card Utilisation', 'Floor vs Realised Rate'], forms: ['Rate Card'], domain: [['line_type', '!=', 'part'], ['min_tier', '!=', 99]] }],
    ['4', 'Parts Pricing', 9, { model: 'fix.parts.price.scheme', cols: ['name', 'method', 'category_id', 'brand_id', 'provenance_grade', 'markup_pct', 'valid_from', 'state'], screens: ['M11-parts-schemes', 'M11-parts', 'M11-floors'], reports: ['Margin by Service Line', 'Floor vs Realised Rate'], forms: ['Parts Pricing Scheme', 'Rate Card', 'Price Floor'] }],
    ['5', 'Customer/Contract Pricing', 8, { model: 'fix.rate.card', cols: ['contract_id', 'product_code', 'line_type', 'unit_price', 'valid_from', 'valid_to', 'state'], screens: ['M11-contract'], reports: ['Rate-Card Utilisation'], forms: ['Rate Card'], create: 'M11-form-card', domain: [['min_tier', '=', 99]] }],
    ['6', 'Brand Reimbursement', 7, { model: 'fix.brand.reimbursement.rate', cols: ['brand_id', 'repair_level', 'labour_rate', 'parts_markup_pct', 'valid_from', 'valid_to', 'version', 'state'], screens: ['M11-brand', 'M11-rpt-brand'], reports: ['Brand Reimbursement Recovery'], forms: ['Brand Reimbursement Rate'] }],
    ['7', 'Discount Governance', 10, { model: 'fix.discount.approval', cols: ['quotation_id', 'discount_pct', 'state', 'justification', 'approved_by'], screens: ['M11-discounts', 'M11-policies', 'M11-reasons', 'M11-floors', 'M11-overrides', 'M11-rpt-discount'], reports: ['Discount Register by Approver', 'Floor vs Realised Rate'], forms: ['Discount Approval', 'Discount Reason Code', 'Discount Policy', 'Price Floor', 'Below-Floor Override'] }],
    ['8', 'Promotions', 7, { model: 'fix.promotion', cols: ['code', 'name', 'discount_type', 'value', 'channel', 'state'], screens: ['M11-promos', 'M11-rpt-promo'], reports: ['Promotion Effectiveness'], forms: ['Promotion'] }],
    ['9', 'Adjustment Rules', 8, { model: 'fix.price.adjustment', cols: ['code', 'name', 'adjustment_type', 'basis', 'value', 'applies_to', 'valid_from', 'state'], screens: ['M11-premiums', 'M11-adjust'], reports: [], forms: ['Price Premium', 'Dynamic Price Rule'] }],
    ['10', 'Simulation & Trace', 7, { model: 'fix.price.simulation', cols: ['name', 'catalogue_item_id', 'rate_card_id', 'state', 'computed_at'], screens: ['M11-simulate', 'M11-price-explanation'], reports: [], forms: ['Price Simulation Request'] }],
    ['11', 'Versioning & Approval', 8, { model: 'fix.price.version', cols: ['name', 'state', 'book_id', 'version', 'effective_from', 'approved_by'], screens: ['M11-versions', 'M11-changes', 'M11-mass', 'M11-mass-lines', 'M11-differentials', 'M11-breaks', 'M11-reviews', 'M11-override-log', 'M11-rpt-exceptions', 'M11-rpt-consistency'], reports: ['Price Exceptions', 'Price Consistency Monitor'], forms: ['Price Book Version', 'Price Change Request', 'Mass Price Change', 'Channel Differential', 'Volume Break'] }]
  ] }
};

export const SCREENS = {
  'M11-books': { kind: 'model_list', model: 'fix.price.book', stateField: 'state',
    cols: ['code', 'name', 'currency_id', 'state', 'active_version_id', 'active'],
    // A04 audit 2026-11-04: a book goes Active when its first released
    // version activates; a Price-Book Releaser retires it.
    actions: [
      { m: 'action_retire', l: 'Retire Price Book (Releaser)', ask: 'Why is the book retired?', kwarg: 'reason' }
    ] },
  'M11-engine': { kind: 'table_report', module: 'M11', report: 'pricing_engine', title: 'Price Resolution Engine', period: false },
  'M11-versions': { kind: 'model_list', model: 'fix.price.version', stateField: 'state',
    cols: ['name', 'book_id', 'version', 'effective_from', 'state', 'approval_state', 'approved_by'],
    // Released from the Price-Book Releaser's M63 inbox (approver != author);
    // activates on its effective date.
    actions: [
      { m: 'action_submit', l: 'Submit for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' }
    ] },
  /* Labour and the fixed-price service lines (transport, consumables): they
   * were on no list at all, as labour-only filtering left them out. Contract
   * rates show here too (tier 99): the Rate Card form returns here on Save &
   * Close, and a saved contract rate must not seem to vanish. Contract Rates
   * lists them on their own. */
  'M11-labour': { kind: 'model_list', model: 'fix.rate.card', stateField: 'state',
    domain: [['line_type', '!=', 'part']],
    cols: ['product_code', 'name', 'line_type', 'unit_price', 'min_tier', 'valid_from', 'valid_to', 'state', 'active'],
    // A rate prices nothing until released; a released rate changes only
    // through a price change a releaser approves (A04 audit M11-5).
    actions: [
      { m: 'action_request_release', l: 'Request Release (Releaser approves)' },
      { m: 'action_request_change', l: 'Request Change to the Proposed Rate' },
      { m: 'action_request_retire', l: 'Request Retirement', ask: 'Why is the rate retired?', kwarg: 'reason' }
    ] },
  'M11-parts': { kind: 'model_list', model: 'fix.rate.card', stateField: 'state',
    domain: [['line_type', '=', 'part']],
    cols: ['product_code', 'name', 'unit_price', 'min_tier', 'valid_from', 'valid_to', 'state', 'active'],
    // A rate prices nothing until released; a released rate changes only
    // through a price change a releaser approves (A04 audit M11-5).
    actions: [
      { m: 'action_request_release', l: 'Request Release (Releaser approves)' },
      { m: 'action_request_change', l: 'Request Change to the Proposed Rate' },
      { m: 'action_request_retire', l: 'Request Retirement', ask: 'Why is the rate retired?', kwarg: 'reason' }
    ] },
  /* FR-PRC-016 / BRU-PRC-11: a negotiated contract rate is a rate card in
   * the engine's contract lane (tier 99 + the contract no.); it overrides
   * every tier rate for that contract. "+ New" starts one in that lane. */
  'M11-contract': { kind: 'model_list', model: 'fix.rate.card', stateField: 'state',
    domain: [['min_tier', '=', 99]],
    cols: ['contract_id', 'contract_no', 'product_code', 'line_type', 'unit_price', 'valid_from', 'valid_to', 'state', 'active'],
    actions: [
      { m: 'action_request_release', l: 'Request Release (Releaser approves)' },
      { m: 'action_request_change', l: 'Request Change to the Proposed Rate' },
      { m: 'action_request_retire', l: 'Request Retirement', ask: 'Why is the rate retired?', kwarg: 'reason' }
    ] },
  /* This heading listed the claim-recovery report: there was no rate to list.
   * The recovery report stays a chip (Brand Reimbursement Recovery). */
  'M11-brand': { kind: 'model_list', model: 'fix.brand.reimbursement.rate', stateField: 'state',
    cols: ['brand_id', 'repair_level', 'labour_rate', 'parts_markup_pct', 'valid_from', 'valid_to', 'version', 'state', 'approval_state', 'approved_by'],
    // FR-PRC-015 / BRU-PRC-12: released by a Price-Book Releaser who is not
    // the author (M63 inbox); a released rate is superseded, never edited.
    actions: [
      { m: 'action_submit', l: 'Submit for Release', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Submission', states: ['in_review'] },
      { m: 'action_retire', l: 'Retire Rate (Releaser)', ask: 'Why does the brand stop paying this rate?', kwarg: 'reason', states: ['active'] }
    ] },
  'M11-adjust': { kind: 'model_list', model: 'fix.dynamic.price.rule', stateField: 'active',
    cols: ['name', 'channel', 'rule_type', 'adjustment_pct', 'surge_multiplier', 'active'],
    actions: [
      { m: 'action_disable', l: 'Disable Rule (guardrail)', ask: 'Why is the rule disabled?', kwarg: 'reason' },
      { m: 'action_enable', l: 'Re-enable Rule (Releaser, not the author)' }
    ] },
  'M11-discounts': { kind: 'model_list', model: 'fix.discount.approval', stateField: 'state',
    cols: ['quotation_id', 'discount_pct', 'reason_code_id', 'state', 'approval_state', 'approved_by', 'justification'],
    // Approved or rejected from the approver's M63 inbox (A03 audit R7).
    actions: [
      { m: 'action_request_approval', l: 'Request Discount Approval', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M11-floors': { kind: 'model_list', model: 'fix.price.floor', stateField: 'active',
    cols: ['product_code', 'name', 'floor_price', 'proposed_override_price', 'dofa_tier_required', 'approval_state', 'dofa_approved', 'active'],
    // A below-floor override is a DOFA decision from the approver's M63 inbox;
    // the floor itself changes only through an approved price change.
    actions: [
      { m: 'action_request_approval', l: 'Request Below-Floor Override (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Override Request' },
      { m: 'action_request_floor_change', l: 'Request Floor Change (staged on the form)' },
      { m: 'action_request_retire', l: 'Request Floor Retirement', ask: 'Why is the floor retired?', kwarg: 'reason' }
    ] },
  /* A04 ERP audit (20 Nov 2026) M11-F7: a below-floor price is approved for
   * ONE document line, used once, and lapses at its use-by date. */
  'M11-overrides': { kind: 'model_list', model: 'fix.price.override', stateField: 'state',
    cols: ['name', 'product_id', 'res_model', 'res_id', 'requested_price', 'floor_price', 'valid_until', 'dofa_tier_required', 'approval_state', 'state'],
    actions: [
      { m: 'action_submit', l: 'Request Override Approval (DOFA)', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Request', states: ['pending'] }
    ] },
  'M11-promos': { kind: 'model_list', model: 'fix.promotion', stateField: 'state',
    cols: ['code', 'name', 'discount_type', 'value', 'channel', 'valid_from', 'valid_until', 'state', 'approval_state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' },
      { m: 'action_end', l: 'End Promotion Early', ask: 'Why does it end early?', kwarg: 'reason' }
    ] },
  'M11-simulate': { kind: 'model_list', model: 'fix.price.simulation', stateField: 'state',
    cols: ['name', 'catalogue_item_id', 'rate_card_id', 'state', 'requested_by', 'computed_at'],
    actions: [{ m: 'action_compute', l: 'Run Simulation (engine)' }] },
  'M11-changes': { kind: 'model_list', model: 'fix.price.change', stateField: 'state',
    cols: ['name', 'target_type', 'change_type', 'product_code', 'current_value', 'proposed_value', 'state', 'approval_state', 'applied_by'],
    // A04 audit M11-5: the only way a live rate or floor moves.
    actions: [
      { m: 'action_submit', l: 'Submit for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' },
      { m: 'action_cancel', l: 'Cancel Draft' }
    ] },
  'M11-policies': { kind: 'model_list', model: 'fix.discount.policy', stateField: 'state',
    cols: ['name', 'role', 'min_pct', 'max_pct', 'requires_approval', 'approval_tier', 'state', 'approval_state'],
    // The one discount ladder (BRU-PRC-06 until a band is released).
    actions: [
      { m: 'action_submit', l: 'Submit Band for Release' },
      { m: 'action_recall_approval', l: 'Recall Submission' },
      { m: 'action_retire', l: 'Retire Band (Releaser)' }
    ] },
  /* Pass 2 (2026-11-18): FR-PRC-013, how a part's price follows from its cost. */
  'M11-parts-schemes': { kind: 'model_list', model: 'fix.parts.price.scheme', stateField: 'state',
    cols: ['name', 'method', 'category_id', 'brand_id', 'provenance_grade', 'markup_pct', 'valid_from', 'valid_to', 'version', 'state', 'approval_state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Release', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Submission', states: ['in_review'] },
      { m: 'action_retire', l: 'Retire Scheme (Releaser)', ask: 'Why is the scheme retired?', kwarg: 'reason', states: ['active'] }
    ] },
  /* FR-PRC-018/019: declared premiums and surcharges, named on every price. */
  'M11-premiums': { kind: 'model_list', model: 'fix.price.adjustment', stateField: 'state',
    cols: ['code', 'name', 'adjustment_type', 'basis', 'value', 'applies_to', 'valid_from', 'valid_to', 'state', 'approval_state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Release', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Submission', states: ['in_review'] },
      { m: 'action_retire', l: 'Retire Premium (Releaser)', ask: 'Why is the premium retired?', kwarg: 'reason', states: ['active'] }
    ] },
  /* BRU-PRC-13: the governed list a discount request picks its reason from. */
  /* A04 ERP round 2 (21 Nov 2026), M11-F19. FR-PRC-020 / BRU-PRC-14: a
   * declared channel differential, released inside the governed spread. */
  'M11-differentials': { kind: 'model_list', model: 'fix.channel.differential', stateField: 'state',
    cols: ['name', 'channel', 'product_code', 'category_id', 'adjustment_pct', 'valid_from', 'valid_to', 'state', 'released_by'],
    actions: [
      { m: 'action_release', l: 'Release (Price-Book Releaser, within the max spread)', states: ['draft'] },
      { m: 'action_retire', l: 'Retire Differential', states: ['released'] }
    ] },
  /* FR-PRC-017: the breaks of a draft rate card. */
  'M11-breaks': { kind: 'model_list', model: 'fix.price.break', cols: ['card_id', 'threshold', 'unit_price'] },
  /* AUT-PRC-08..12: the pricing tasks events and scans raise. */
  'M11-reviews': { kind: 'model_list', model: 'fix.price.review', stateField: 'state', create: false,
    cols: ['name', 'kind', 'product_code', 'rate_card_id', 'catalogue_item_id', 'successor_item_id', 'current_price', 'proposed_price', 'deadline', 'card_retired', 'state'],
    actions: [
      { m: 'action_dispose', l: 'Dispose', ask: 'What was done about it?', kwarg: 'note', states: ['open'] },
      { m: 'action_accept', l: 'Accept New Labour Price (SRT)', states: ['open'] },
      { m: 'action_reject', l: 'Reject New Labour Price (SRT)', ask: 'Why is the new labour price not taken?', kwarg: 'note', states: ['open'] }
    ] },
  /* FR-PRC-032: permanent. */
  'M11-override-log': { kind: 'model_list', model: 'fix.price.override.log', create: false,
    cols: ['at', 'document', 'product_id', 'original_price', 'override_price', 'actor_id', 'reason', 'approval_ref'] },
  'M11-rpt-exceptions': { kind: 'table_report', module: 'M11', report: 'price_exceptions', title: 'Price Exceptions', period: true },
  'M11-rpt-consistency': { kind: 'table_report', module: 'M11', report: 'price_consistency', title: 'Price Consistency Monitor', period: true },
  'M11-form-differential': {
    kind: 'model_form',
    model: 'fix.channel.differential',
    title: 'Channel Differential',
    back: 'M11-differentials',
    status: { field: 'state', labels: { draft: 'Draft', released: 'Released', retired: 'Retired' } },
    tabs: [
      { id: 'scope', label: '1. Channel & Scope', bn: '১. চ্যানেল ও পরিসর', icon: '🛒', badge: '5' },
      { id: 'decision', label: '2. Release', bn: '২. অনুমোদন', icon: '🏛️', badge: '3' },
      { id: 'docs', label: '3. Documents', bn: '৩. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'scope', title: 'What Differs on Which Channel',
        note: 'A percentage above (+) or below (-) the released card on one channel, for one item code, a category, or every item. The channels may differ by no more than the governed maximum spread (BRU-PRC-14); a contract rate is never moved (BRU-PRC-11).',
        fields: [
          { name: 'channel', label: 'Channel', required: true },
          { name: 'product_code', label: 'Item Code (empty: category / all)' },
          { name: 'category_id', label: 'Category' },
          { name: 'adjustment_pct', label: 'Differential (%)', required: true },
          { name: 'reason', label: 'Why This Channel Differs', type: 'text', required: true }
        ] },
      { tab: 'decision', title: 'Validity and Release',
        fields: [
          { name: 'valid_from', label: 'Valid From', required: true },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'released_by', label: 'Released By', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The channel cost study and the release approval evidence attach here (fix.document, M24).', fields: [] }
    ]
  },
  'M11-form-break': {
    kind: 'model_form',
    model: 'fix.price.break',
    title: 'Volume Break',
    back: 'M11-breaks',
    tabs: [{ id: 'break', label: '1. Break', bn: '১. ধাপ', icon: '📶', badge: '3' }],
    sections: [
      { tab: 'break', title: 'From This Quantity / Value, This Price',
        note: 'A break belongs to a Draft rate card (its basis and treatment are on the card). It never raises the price, never goes under the floor, and a higher break never has a higher price.',
        fields: [
          { name: 'card_id', label: 'Rate Card (Draft)', required: true },
          { name: 'threshold', label: 'From (quantity / value / committed volume)', required: true },
          { name: 'unit_price', label: 'Unit Price From Here (VAT-exclusive BDT)', required: true }
        ] }
    ]
  },
  'M11-reasons': { kind: 'model_list', model: 'fix.discount.reason',
    cols: ['code', 'name', 'description', 'use_count', 'active'] },
  /* FR-PRC-024 / BRU-PRC-16: preview, approval, scheduled date, rollback. */
  'M11-mass': { kind: 'model_list', model: 'fix.price.mass.change', stateField: 'state',
    cols: ['name', 'line_type', 'product_code_prefix', 'change_kind', 'value', 'effective_date', 'line_count', 'below_floor_count', 'state', 'approval_state'],
    actions: [
      { m: 'action_preview', l: 'Preview Affected Rates', states: ['draft'] },
      { m: 'action_submit', l: 'Submit for Approval', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Submission', states: ['in_review'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft', 'approved'] },
      { m: 'action_rollback', l: 'Roll Back (Releaser)', ask: 'Why is the change rolled back?', kwarg: 'reason', states: ['applied'] }
    ] },
  'M11-mass-lines': { kind: 'model_list', model: 'fix.price.mass.change.line', create: false,
    cols: ['change_id', 'product_code', 'line_type', 'current_price', 'new_price', 'floor_price', 'below_floor', 'applied'],
    empty: 'No mass change has been previewed yet. Preview Affected Rates on a mass price change lists here every released rate it moves, with its new price and its floor.' },
  'M11-realised': { kind: 'table_report', module: 'M11', report: 'realised_vs_card', title: 'Realised-Price Analytics', period: false },

  /* Report chips -> their own computed pack */
  'M11-rpt-realised': { kind: 'table_report', module: 'M11', report: 'realised_vs_card', title: 'Realised Price vs Card', period: false },
  'M11-rpt-discount': { kind: 'table_report', module: 'M11', report: 'discount_register', title: 'Discount Register by Approver', period: false },
  'M11-rpt-util': { kind: 'table_report', module: 'M11', report: 'rate_card_utilisation', title: 'Rate-Card Utilisation', period: false },
  'M11-rpt-margin': { kind: 'table_report', module: 'M11', report: 'margin_by_line', title: 'Margin by Service Line', period: false },
  'M11-rpt-promo': { kind: 'table_report', module: 'M11', report: 'promotion_effectiveness', title: 'Promotion Effectiveness', period: false },
  'M11-rpt-brand': { kind: 'table_report', module: 'M11', report: 'brand_reimbursement', title: 'Brand Reimbursement Recovery', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M11-form-book': {
    kind: 'model_form',
    model: 'fix.price.book',
    title: 'Price Book',
    back: 'M11-books',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'general', label: '1. Book Identity', bn: '১. সাধারণ তথ্য', icon: '📘', badge: '3' },
      { id: 'governance', label: '2. Lifecycle & Status', bn: '২. অনুমোদন ও নিয়ন্ত্রণ', icon: '✅', badge: '2' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '⏱️', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Price Book Identity',
        note: 'A price book is the versioned container a rate card is published from. Codes are immutable once a version is live.',
        fields: [
          { name: 'name', label: "Book Name", required: true },
          { name: 'code', label: "Book Code", required: true },
          { name: 'currency_id', label: "Currency", required: true }
        ] },
      { tab: 'governance', title: 'Lifecycle & Status',
        fields: [
          { name: 'state', label: "Lifecycle State", readonly: true },
          { name: 'active_version_id', label: "Version in Force", readonly: true },
          { name: 'active', label: "Active" }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'company_id', label: "Legal Entity" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },


  'M11-form-card': {
    kind: 'model_form',
    model: 'fix.rate.card',
    title: 'Rate Card',
    back: 'M11-labour',
    status: { field: 'state', labels: { draft: 'Draft', released: 'Released', retired: 'Retired' } },
    /* M11 capture audit (2026-11-13): the form had no Contract No., so a
     * contract rate could not be recorded; two tabs (VAT, documents) had no
     * field at all and a "Surge Multipliers" tab held only the validity dates.
     * VAT is M51's, surges are Adjustment Rules. */
    tabs: [
      { id: 'identity', label: '1. Identity & Scope', bn: '১. রেট পরিচিতি', icon: '🏷️', badge: '5' },
      { id: 'pricing', label: '2. Rate & Who It Applies To', bn: '২. রেট ও প্রযোজ্যতা', icon: '💵', badge: '4' },
      { id: 'validity', label: '3. Validity Window', bn: '৩. মেয়াদ', icon: '📅', badge: '2' },
      { id: 'governance', label: '4. Release & Changes', bn: '৪. অনুমোদন ও পরিবর্তন', icon: '🏛️', badge: '4' }
    ],
    /* A04 ERP round 2 FR-PRC-017: the breaks of the card, edited while Draft. */
    grids: [
      { field: 'price_break_ids', tab: 'pricing', title: 'Volume Breaks',
        addLabel: '+ Add break',
        empty: 'No break: every quantity sells at the rate.',
        note: 'From each threshold (quantity, value or committed volume, per the card basis) the unit price below applies. Never above the rate, never under the floor; locked once released.',
        fields: [
          { name: 'threshold', label: 'From', required: true },
          { name: 'unit_price', label: 'Unit Price From Here (VAT-exclusive BDT)', required: true }
        ] }
    ],
    sections: [
      { tab: 'identity', title: 'Rate Scope & Catalogue Association',
        note: 'One rate per product code, customer tier and contract. Labour is charged against the catalogue standard repair time; parts, consumables and transport at the rate per unit.',
        fields: [
          { name: 'product_code', required: true, label: 'Product SKU / Service Code' },
          { name: 'line_type', required: true, label: 'Service Line Classification' },
          { name: 'catalogue_item_id', label: 'Associated Catalogue Item (M37)' },
          { name: 'rate_kind', label: 'Rate Kind (per unit / labour rate per hour x SRT)' },
          { name: 'state', label: 'Release State', readonly: true },
          { name: 'active', label: 'Active Rate Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Rate and Who It Applies To',
        note: 'A customer tier rate applies to that tier and above. A contract rate names its M08 contract: it overrides every tier rate for that contract (BRU-PRC-11), stays within the contract term and lapses with it (AC-08). Left empty, the validity follows the contract term.',
        fields: [
          { name: 'unit_price', required: true, label: 'Base Rate (VAT-exclusive BDT)' },
          { name: 'min_tier', label: 'Customer Tier (99 = contract rate)' },
          { name: 'contract_id', label: 'Contract (M08), contract rates only' },
          { name: 'contract_no', label: 'Contract No.', readonly: true },
          { name: 'partner_id', label: 'Customer (customer-specific rate)' },
          { name: 'version_id', label: 'Price-Book Version' }
        ] },
      { tab: 'pricing', title: 'Labour Rate Scope (labour rate per hour only)',
        note: 'FR-PRC-012: a labour rate per hour prices every operation of its repair level at rate x the M37 standard repair time. The most specific matching rate wins; empty = any.',
        fields: [
          { name: 'repair_level', label: 'Repair Level' },
          { name: 'skill_band', label: 'Skill Band' },
          { name: 'brand_id', label: 'Brand' },
          { name: 'delivery_mode', label: 'Delivery Mode' },
          { name: 'operating_unit_id', label: 'Branch' }
        ] },
      { tab: 'pricing', title: 'Volume Breaks (FR-PRC-017)',
        note: 'Bracket: every unit at the break reached. Cumulative: each unit at the price of its band. The breaks themselves are recorded under Volume Breaks while the card is Draft.',
        fields: [
          { name: 'break_basis', label: 'Break Basis' },
          { name: 'break_treatment', label: 'Break Treatment' }
        ] },
      { tab: 'validity', title: 'Effective Window',
        fields: [
          { name: 'valid_from', label: 'Tariff Effective From' },
          { name: 'valid_to', label: 'Tariff Valid Until' }
        ] },
      { tab: 'governance', title: 'Price Floor Governance & Delegation of Authority',
        note: 'A released rate changes only through a price change that a Price-Book Releaser other than its author approves (BRU-PRC-07). Stage the new rate and reason here, then use Request Change.',
        fields: [
          { name: 'proposed_unit_price', label: 'Proposed Rate (staged)' },
          { name: 'change_reason', label: 'Change Reason', type: 'text' },
          { name: 'released_by', label: 'Released By', readonly: true },
          { name: 'released_at', label: 'Released On', readonly: true }
        ] }
    ]
  },

  /* FR-PRC-015 / BRU-PRC-12: what a brand pays 1000FiX for warranty work. */
  'M11-form-brand-rate': {
    kind: 'model_form',
    model: 'fix.brand.reimbursement.rate',
    title: 'Brand Reimbursement Rate',
    back: 'M11-brand',
    status: { field: 'state', labels: { draft: 'Draft', in_review: 'In Review', active: 'In Force', superseded: 'Superseded', retired: 'Retired' } },
    tabs: [
      { id: 'scope', label: '1. Brand & Repair Level', bn: '১. ব্র্যান্ড ও মেরামতের স্তর', icon: '🏷️', badge: '3' },
      { id: 'rate', label: '2. What the Brand Pays', bn: '২. ব্র্যান্ড যা পরিশোধ করে', icon: '💵', badge: '3' },
      { id: 'validity', label: '3. Effective Date & Version', bn: '৩. কার্যকর তারিখ ও সংস্করণ', icon: '📅', badge: '3' },
      { id: 'release', label: '4. Release', bn: '৪. অনুমোদন', icon: '✅', badge: '5' }
    ],
    sections: [
      { tab: 'scope', title: 'Brand and Repair Level',
        note: 'One rate per brand and repair level at a time. Warranty claims against the brand are valued at the rate in force on the service date (BRU-PRC-12).',
        fields: [
          { name: 'brand_id', required: true, label: 'Brand' },
          { name: 'repair_level', required: true, label: 'Repair Level' },
          { name: 'circular_reference', label: 'Brand Circular / Agreement Ref.' }
        ] },
      { tab: 'rate', title: 'What the Brand Pays',
        note: 'Labour per warranty job at this level, plus the parts fitted at cost and the handling markup.',
        fields: [
          { name: 'labour_rate', required: true, label: 'Labour Rate per Job (BDT)' },
          { name: 'parts_markup_pct', label: 'Parts Handling Markup (%)' },
          { name: 'currency_id', required: true, label: 'Currency' }
        ] },
      { tab: 'validity', title: 'Effective Date and Version',
        note: 'A released rate is never edited. A new brand circular is a new version with its own effective date; the previous version stays valid up to the day before.',
        fields: [
          { name: 'valid_from', required: true, label: 'Effective From' },
          { name: 'valid_to', label: 'Effective Until', readonly: true },
          { name: 'version', label: 'Version', readonly: true }
        ] },
      { tab: 'release', title: 'Release',
        fields: [
          { name: 'state', label: 'Rate State', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'submitted_by', label: 'Submitted By', readonly: true },
          { name: 'approved_by', label: 'Released By', readonly: true },
          { name: 'approved_at', label: 'Released On', readonly: true },
          { name: 'note', label: 'Notes', type: 'text' },
          { name: 'company_id', label: 'Legal Entity' }
        ] }
    ]
  },
  'M11-form-policy': {
    kind: 'model_form',
    model: 'fix.discount.policy',
    title: 'Discount Policy',
    back: 'M11-discounts',
    tabs: [
      { id: 'general', label: '1. Policy Identity', bn: '১. সাধারণ তথ্য', icon: '📋', badge: '2' },
      { id: 'commercial', label: '2. Discount Band', bn: '২. বাণিজ্যিক শর্ত', icon: '💰', badge: '3' },
      { id: 'governance', label: '3. Approval Requirement', bn: '৩. অনুমোদন ও নিয়ন্ত্রণ', icon: '🔐', badge: '1' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Policy Identity',
        fields: [
          { name: 'name', label: "Policy Name", required: true },
          { name: 'role', label: "Applies to Role" }
        ] },
      { tab: 'commercial', title: 'Permitted Discount Band',
        note: 'The band a holder of this role may grant unaided. Anything beyond it raises a fix.discount.approval for a second signature.',
        fields: [
          { name: 'min_pct', label: "Minimum Discount %" },
          { name: 'max_pct', label: "Maximum Discount %" },
          { name: 'active', label: "Active" }
        ] },
      { tab: 'governance', title: 'Approval Requirement',
        note: 'A band is part of the discount ladder only once a Price-Book Releaser other than its author releases it (M63 inbox).',
        fields: [
          { name: 'requires_approval', label: "Requires a Second Signature" },
          { name: 'approval_tier', label: "Approving DOFA Tier" },
          { name: 'state', label: "Band State", readonly: true },
          { name: 'approval_state', label: "Approval", readonly: true },
          { name: 'approved_by', label: "Released By", readonly: true }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'company_id', label: "Legal Entity" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },

  'M11-form-discount-approval': {
    kind: 'model_form',
    model: 'fix.discount.approval',
    title: 'Discount Approval',
    back: 'M11-discounts',
    status: { field: 'state' },
    tabs: [
      { id: 'request', label: '1. Discount Requested', bn: '১. অনুরোধকৃত ডিসকাউন্ট', icon: '🏷️', badge: '4' },
      { id: 'authority', label: '2. Approval Authority', bn: '২. অনুমোদন কর্তৃপক্ষ', icon: '🔐', badge: '2' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'request', title: 'Requested Concession',
        note: 'A discount beyond the rate card is a concession: it carries a reason code from the governed list (BRU-PRC-13) and a stated justification, and the approver is not the requester.',
        fields: [
          { name: 'quotation_id', required: true, label: "Quotation" },
          { name: 'discount_pct', required: true, label: "Discount Requested (%)" },
          { name: 'reason_code_id', label: "Reason Code (governed list)" },
          { name: 'justification', label: "Commercial Justification", type: 'text' }
        ] },
      { tab: 'authority', title: 'Delegation of Financial Authority', fields: [
        { name: 'approved_by', label: "Approved By", readonly: true },
        { name: 'state', label: "Approval State" }
      ] },
      { tab: 'audit', title: 'System Audit Trail', fields: [
        { name: 'operating_unit_id', label: "Operating Unit" },
        { name: 'company_id', label: "Legal Entity" },
        { name: 'create_date', label: "Raised On", readonly: true }
      ] }
    ]
  },
  'M11-form-promo': {
    kind: 'model_form',
    model: 'fix.promotion',
    title: 'Promotion',
    back: 'M11-promos',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Promotion Identity', bn: '১. সাধারণ তথ্য', icon: '🏷️', badge: '4' },
      { id: 'commercial', label: '2. Discount Mechanics', bn: '২. বাণিজ্যিক শর্ত', icon: '💰', badge: '3' },
      { id: 'schedule', label: '3. Validity Window', bn: '৩. সময়সূচি', icon: '📅', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    /* M40 alliance schemes that make this promotion member-only (read-only). */
    grids: [
      { field: 'alliance_scheme_ids', tab: 'commercial', title: 'Alliance Schemes (member-only)', readonlyGrid: true,
        empty: 'No alliance scheme names this promotion: it is open to every eligible customer.',
        fields: [
          { name: 'code', label: 'Scheme Code', readonly: true },
          { name: 'name', label: 'Scheme', readonly: true },
          { name: 'partner_id', label: 'Alliance Partner', readonly: true }
        ] }
    ],
    sections: [
      { tab: 'general', title: 'Promotion Identity',
        fields: [
          { name: 'name', label: "Promotion Name", required: true },
          { name: 'code', label: "Promo Code", required: true },
          { name: 'channel', label: "Sales Channel" },
          { name: 'catalogue_item_ids', label: "Items It Applies To (empty = every item)" }
        ] },
      { tab: 'commercial', title: 'Discount Mechanics',
        fields: [
          { name: 'discount_type', label: "Discount Type" },
          { name: 'value', label: "Discount Value" },
          { name: 'storefront_voucher', label: "Storefront Checkout Voucher (applied only when the customer enters the code; fixed once out of draft)" },
          { name: 'stackable', label: "Stackable with Other Promotions" },
          { name: 'priority', label: "Priority" },
          { name: 'budget_amount', label: "Budget (BDT)" },
          { name: 'budget_used', label: "Budget Used", readonly: true },
          { name: 'max_uses', label: "Usage Cap" },
          { name: 'use_count', label: "Times Used", readonly: true },
          { name: 'state', label: "Promotion State", readonly: true },
          { name: 'approval_state', label: "Approval", readonly: true },
          { name: 'approved_by', label: "Released By", readonly: true }
        ] },
      { tab: 'schedule', title: 'Validity Window',
        note: 'A promotion outside its window must not price: the dates are the control, not a label.',
        fields: [
          { name: 'valid_from', label: "Valid From" },
          { name: 'valid_until', label: "Valid Until" }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'company_id', label: "Legal Entity" },
          { name: 'active', label: "Active" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },
  'M11-form-simulation': {
    kind: 'model_form',
    model: 'fix.price.simulation',
    title: 'Price Simulation',
    back: 'M11-simulate',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Simulation Request', bn: '১. সাধারণ তথ্য', icon: '🧪', badge: '3' },
      { id: 'commercial', label: '2. Inputs', bn: '২. বাণিজ্যিক শর্ত', icon: '📥', badge: '7' },
      { id: 'result', label: '3. Computed Result', bn: '৩. ফলাফল', icon: '📊', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Simulation Request',
        note: 'A what-if run against the live rate card. Simulations never write a price; they explain one.',
        fields: [
          { name: 'name', label: "Reference", required: true },
          { name: 'catalogue_item_id', label: "Catalogue Item" },
          { name: 'rate_card_id', label: "Rate Card" }
        ] },
      { tab: 'commercial', title: 'Inputs',
        note: 'The customer and the job the price is for. Premiums: any of express, emergency, after_hours, weekend, holiday (comma-separated).',
        fields: [
          { name: 'quantity', label: "Quantity" },
          { name: 'customer_tier', label: "Customer Tier" },
          { name: 'contract_id', label: "Contract (M08)" },
          { name: 'channel', label: "Sales Channel" },
          { name: 'proposed_price', label: "Price to Test Against the Floor" },
          { name: 'premium_kinds', label: "Premiums" },
          { name: 'state', label: "State", readonly: true }
        ] },
      { tab: 'result', title: 'Computed Result',
        fields: [
          { name: 'result_json', label: "Computed Result", type: 'text', readonly: true },
          { name: 'computed_at', label: "Computed At", readonly: true }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'requested_by', label: "Requested By", readonly: true },
          { name: 'company_id', label: "Legal Entity" },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },
  'M11-form-version': {
    kind: 'model_form',
    model: 'fix.price.version',
    title: 'Price Book Version',
    back: 'M11-versions',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Version Identity', bn: '১. সাধারণ তথ্য', icon: '🔖', badge: '3' },
      { id: 'schedule', label: '2. Effective Dating', bn: '২. সময়সূচি', icon: '📅', badge: '1' },
      { id: 'governance', label: '3. Approval', bn: '৩. অনুমোদন ও নিয়ন্ত্রণ', icon: '✅', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Version Identity',
        fields: [
          { name: 'name', label: "Version Name", required: true },
          { name: 'book_id', label: "Price Book", required: true },
          { name: 'version', label: "Version No." }
        ] },
      { tab: 'schedule', title: 'Effective Dating',
        note: 'A version prices from its effective date. Back-dating a live version restates history, so the date is governed.',
        fields: [
          { name: 'effective_from', label: "Effective From" }
        ] },
      { tab: 'governance', title: 'Approval',
        fields: [
          { name: 'state', label: "Lifecycle State", readonly: true },
          { name: 'approval_state', label: "Approval", readonly: true },
          { name: 'submitted_by', label: "Submitted By", readonly: true },
          { name: 'approved_by', label: "Approved By", readonly: true },
          { name: 'rejection_reason', label: "Returned Because", type: 'text', readonly: true }
        ] },
      { tab: 'audit', title: 'System Audit Trail',
        fields: [
          { name: 'note', label: "Notes", type: 'text' },
          { name: 'create_date', label: "Created", readonly: true }
        ] }
    ]
  },


  'M11-form-floor': {
    kind: 'model_form',
    model: 'fix.price.floor',
    title: 'Statutory Price Floor Rule',
    back: 'M11-floors',
    status: { field: 'active', labels: { true: 'Active Rule', false: 'Inactive' } },
    tabs: [
      { id: 'floor_scope', label: '1. Product Code & Scope', bn: '১. পণ্য কোড ও পরিধি', icon: '🏷️', badge: '4' },
      { id: 'pricing_limit', label: '2. Floor Price & Limits', bn: '২. ন্যূনতম মূল্য ও সীমা', icon: '💵', badge: '2' },
      { id: 'dofa_override', label: '3. DOFA Override Governance', bn: '৩. ডোফা ওভাররাইড', icon: '🔐', badge: '3' }
    ],
    sections: [
      { tab: 'floor_scope', title: 'Target Identification', note: 'The minimum sellable price per product code. Quotes below it trigger floor breach controls.',
        fields: [
          { name: 'name', required: true, label: 'Floor Rule Name' },
          { name: 'product_code', required: true, label: 'Product Code' },
          { name: 'catalogue_item_id', label: 'Catalogue Item' },
          { name: 'book_id', label: 'Price Book Link' }
        ] },
      { tab: 'pricing_limit', title: 'Statutory Pricing Limit',
        note: 'The floor is set when the rule is created and then changes only through a price change a Price-Book Releaser approves. Stage the new floor and reason, then use Request Floor Change.',
        fields: [
          { name: 'floor_price', required: true, label: 'Floor Price (BDT)' },
          { name: 'proposed_floor_price', label: 'Proposed New Floor (staged)' },
          { name: 'floor_change_reason', label: 'Floor Change Reason', type: 'text' }
        ] },
      { tab: 'dofa_override', title: 'Delegation of Financial Authority (DOFA)', note: 'A sale below the floor needs a Below-Floor Override approved for that one document line (Discount Governance > Below-Floor Overrides). An approval recorded here on the floor no longer clears any sale.',
        fields: [
          { name: 'proposed_override_price', label: 'Proposed Below-Floor Price' },
          { name: 'dofa_justification', label: 'Business Justification', type: 'text' },
          { name: 'dofa_tier', label: 'Required DOFA Tier', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'dofa_override_approved', label: 'DOFA Override Approved', readonly: true },
          { name: 'dofa_override_user_id', label: 'DOFA Approver', readonly: true },
          { name: 'active', label: 'Active Floor Enforcement', readonly: true }
        ] }
    ]
  },
  'M11-form-override': {
    kind: 'model_form',
    model: 'fix.price.override',
    title: 'Below-Floor Price Override',
    back: 'M11-overrides',
    status: { field: 'state', labels: { draft: 'Draft', pending: 'Awaiting Approval', approved: 'Approved', consumed: 'Used', expired: 'Expired', rejected: 'Rejected' } },
    tabs: [
      { id: 'line', label: '1. Line & Price', bn: '১. লাইন ও মূল্য', icon: '🏷️', badge: '6' },
      { id: 'decision', label: '2. DOFA Decision', bn: '২. ডোফা সিদ্ধান্ত', icon: '🔐', badge: '6' },
      { id: 'docs', label: '3. Documents', bn: '৩. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'line', title: 'The One Line This Price Is For',
        note: 'Name the estimate line (or the line type and id of another selling document). The override covers that line only, at or above the requested price, once, before its use-by date.',
        fields: [
          { name: 'estimate_line_id', label: 'Estimate Line (M01)' },
          { name: 'res_model', label: 'Other Document Line Type' },
          { name: 'res_id', label: 'Other Document Line ID' },
          { name: 'product_id', label: 'Item', required: true },
          { name: 'requested_price', label: 'Requested Unit Price (BDT, excl. VAT)', required: true },
          { name: 'valid_until', label: 'Use By', required: true }
        ] },
      { tab: 'decision', title: 'Floor and Approval',
        note: 'The tier follows how far below the floor the price sits; the requester never approves it (M63 inbox).',
        fields: [
          { name: 'floor_price', label: 'Floor When Requested', readonly: true },
          { name: 'floor_basis', label: 'Floor Basis', readonly: true },
          { name: 'cost', label: 'M15 Cost When Requested', readonly: true },
          { name: 'dofa_justification', label: 'Business Justification', type: 'text' },
          { name: 'dofa_tier_required', label: 'Required DOFA Tier', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The competitor quote, customer letter or other evidence behind the below-floor price attaches here; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ]
  },
  'M11-form-pricerule': {
    kind: 'model_form',
    model: 'fix.dynamic.price.rule',
    title: "Dynamic Price Rule",
    back: 'M11-adjust',
    tabs: [
      { id: 'general', label: '1. Rule Identity', bn: '১. নিয়ম পরিচয়', icon: '🏷️', badge: '5' },
      { id: 'commercial', label: '2. Adjustment & Bounds', bn: '২. সমন্বয় ও সীমা', icon: '💰', badge: '4' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ', icon: '🔗', badge: '2' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Rule Identity & Scope',
        note: 'A pricing rule adjusts the base rate by a stated condition. The rule must state its own basis — an unexplained adjustment is not defensible to a customer or an auditor.',
        fields: [
          { name: 'name', required: true, label: "Rule Name" },
          { name: 'rule_type', required: true, label: "Rule Type" },
          { name: 'channel', required: true, label: "Sales Channel" },
          { name: 'active', label: "Active", readonly: true },
          { name: 'disabled_reason', label: "Disabled Because", readonly: true },
          { name: 'company_id', required: true, label: "Legal Entity" }
        ] },
      { tab: 'commercial', title: 'Adjustment and its Guard Rails',
        note: 'Adjustments are computed in Decimal and quantised to the paisa (FLAW-11.1). Minimum and maximum bound what the rule may do, and are enforced by a model constraint.',
        fields: [
          { name: 'adjustment_pct', label: "Adjustment %" },
          { name: 'surge_multiplier', label: "Surge Multiplier" },
          { name: 'min_adjustment', label: "Minimum Adjustment %" },
          { name: 'max_adjustment', label: "Maximum Adjustment %" }
        ] },
      { tab: 'relations', title: 'Rate Card Basis', fields: [
        { name: 'rate_card_id', label: "Rate Card Base" },
        { name: 'currency_id', required: true, label: "Currency" }
      ] },
      { tab: 'audit', title: 'System Audit Trail', fields: [
        { name: 'operating_unit_id', label: "Operating Unit" },
        { name: 'create_date', label: "Created", readonly: true },
        { name: 'write_date', label: "Last Updated", readonly: true }
      ] }
    ]
  },
  'M11-rpt-floors': { kind: 'table_report', module: 'M11', report: 'floors_vs_rate', title: "Floor vs Realised Rate", period: false },

  'M11-form-change': {
    kind: 'model_form',
    model: 'fix.price.change',
    title: 'Price Change Request',
    back: 'M11-changes',
    status: { field: 'state' },
    tabs: [
      { id: 'request', label: '1. Change Requested', bn: '১. অনুরোধকৃত পরিবর্তন', icon: '💱', badge: '6' },
      { id: 'decision', label: '2. Release Decision', bn: '২. অনুমোদন সিদ্ধান্ত', icon: '✅', badge: '4' }
    ],
    sections: [
      { tab: 'request', title: 'What Changes and Why',
        note: 'A released rate or a floor moves only through this request; a Price-Book Releaser who did not raise it decides it from the M63 inbox (BRU-PRC-07).',
        fields: [
          { name: 'target_type', label: "Target", required: true },
          { name: 'change_type', label: "Change", required: true },
          { name: 'rate_card_id', label: "Rate Card" },
          { name: 'floor_id', label: "Price Floor" },
          { name: 'proposed_value', label: "New Price (BDT)" },
          { name: 'effective_from', label: "Effective From (new rate version)" },
          { name: 'reason', label: "Reason", type: 'text', required: true }
        ] },
      { tab: 'decision', title: 'Release Decision', fields: [
        { name: 'current_value', label: "Price When Raised", readonly: true },
        { name: 'approval_state', label: "Approval", readonly: true },
        { name: 'applied_by', label: "Released By", readonly: true },
        { name: 'applied_at', label: "Applied On", readonly: true }
      ] }
    ]
  },

  /* FR-PRC-013: markup on cost, banded markup, grade differential or fixed. */
  'M11-form-parts-scheme': {
    kind: 'model_form',
    model: 'fix.parts.price.scheme',
    title: 'Parts Pricing Scheme',
    back: 'M11-parts-schemes',
    status: { field: 'state', labels: { draft: 'Draft', in_review: 'In Review', active: 'In Force', superseded: 'Superseded', retired: 'Retired' } },
    tabs: [
      { id: 'scope', label: '1. Parts It Prices', bn: '১. প্রযোজ্য পার্টস', icon: '🔩', badge: '4' },
      { id: 'method', label: '2. Pricing Method', bn: '২. মূল্য পদ্ধতি', icon: '🧮', badge: '5' },
      { id: 'grades', label: '3. Grade Differential', bn: '৩. গ্রেড পার্থক্য', icon: '🏷️', badge: '4' },
      { id: 'bands', label: '4. Cost Bands', bn: '৪. খরচের ধাপ', icon: '📶', badge: '+' },
      { id: 'release', label: '5. Effective Date & Release', bn: '৫. কার্যকর তারিখ ও অনুমোদন', icon: '✅', badge: '8' }
    ],
    sections: [
      { tab: 'scope', title: 'Which Parts It Prices',
        note: 'Leave a field empty to cover every value of it. The most specific scheme in force wins: one for a grade beats one for every grade, a brand beats every brand, a category beats every category.',
        fields: [
          { name: 'name', required: true, label: 'Scheme Name' },
          { name: 'category_id', label: 'Part Category' },
          { name: 'brand_id', label: 'Brand' },
          { name: 'provenance_grade', label: 'Provenance Grade' }
        ] },
      { tab: 'method', title: 'How the Price Follows from Cost',
        note: 'Markup: price = standard cost x (1 + markup). Banded: the markup of the cost band the part falls in (tab 4). Grade: the markup plus the grade adjustment (tab 3). Fixed: one price whatever the cost.',
        fields: [
          { name: 'method', required: true, label: 'Pricing Method' },
          { name: 'markup_pct', label: 'Markup on Cost (%)' },
          { name: 'fixed_price', label: 'Fixed Price (BDT)' },
          { name: 'rounding_step', label: 'Round Selling Price To (BDT)' },
          { name: 'currency_id', required: true, label: 'Currency' }
        ] },
      { tab: 'grades', title: 'Provenance-Grade Differential',
        note: 'Grade method only: percentage points added to (or, negative, taken from) the markup for each grade. A grade can never sell below cost.',
        fields: [
          { name: 'genuine_adj_pct', label: 'Genuine (pts)' },
          { name: 'oem_adj_pct', label: 'OEM (pts)' },
          { name: 'aftermarket_adj_pct', label: 'Aftermarket (pts)' },
          { name: 'refurbished_adj_pct', label: 'Refurbished (pts)' }
        ] },
      { tab: 'release', title: 'Effective Date and Release',
        note: 'Released by a Price-Book Releaser who did not author it (BRU-PRC-07). A released scheme never changes: a new one with its own date supersedes it, and the old one keeps its window.',
        fields: [
          { name: 'valid_from', required: true, label: 'Effective From' },
          { name: 'valid_to', label: 'Effective Until', readonly: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'state', label: 'Scheme State', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by', label: 'Released By', readonly: true },
          { name: 'note', label: 'Notes', type: 'text' },
          { name: 'company_id', label: 'Legal Entity' }
        ] }
    ],
    lines: {
      field: 'band_ids',
      tab: 'bands',
      title: 'Cost Bands (banded method)',
      note: 'One line per cost band, from 0 upward; each band starts where the one before ends. Leave the last "Up To" empty for no upper limit.',
      fields: [
        { name: 'cost_from', label: 'Cost From (BDT)', required: true },
        { name: 'cost_to', label: 'Cost Up To (BDT)' },
        { name: 'markup_pct', label: 'Markup (%)', required: true }
      ]
    }
  },

  /* FR-PRC-018/019: a declared, auditable premium or surcharge. */
  'M11-form-premium': {
    kind: 'model_form',
    model: 'fix.price.adjustment',
    title: 'Price Premium / Surcharge',
    back: 'M11-premiums',
    status: { field: 'state', labels: { draft: 'Draft', in_review: 'In Review', active: 'In Force', superseded: 'Superseded', retired: 'Retired' } },
    tabs: [
      { id: 'identity', label: '1. Premium', bn: '১. প্রিমিয়াম', icon: '⚡', badge: '4' },
      { id: 'amount', label: '2. Amount', bn: '২. পরিমাণ', icon: '💵', badge: '3' },
      { id: 'conditions', label: '3. When It Applies', bn: '৩. কখন প্রযোজ্য', icon: '📍', badge: '5' },
      { id: 'release', label: '4. Effective Date & Release', bn: '৪. কার্যকর তারিখ ও অনুমোদন', icon: '✅', badge: '8' }
    ],
    sections: [
      { tab: 'identity', title: 'Which Premium',
        note: 'Express, emergency, after-hours, weekend and holiday premiums, and zone and distance surcharges for on-site and pick-and-drop work. Each appears as its own named line of the price explanation.',
        fields: [
          { name: 'name', required: true, label: 'Premium Name' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'adjustment_type', required: true, label: 'Premium Type' },
          { name: 'applies_to', required: true, label: 'Applies To' }
        ] },
      { tab: 'amount', title: 'Amount',
        fields: [
          { name: 'basis', required: true, label: 'Basis' },
          { name: 'value', required: true, label: 'Value (% or BDT)' },
          { name: 'currency_id', required: true, label: 'Currency' }
        ] },
      { tab: 'conditions', title: 'When It Applies',
        note: 'Zone: the branches in the zone. Distance: the band in km from the branch. After-hours: the hours (24-hour clock; a window may run past midnight). The other types apply whenever the job is booked as such.',
        fields: [
          { name: 'operating_unit_ids', label: 'Branches in the Zone' },
          { name: 'distance_from_km', label: 'Distance From (km)' },
          { name: 'distance_to_km', label: 'Distance Up To (km)' },
          { name: 'hour_from', label: 'From Hour' },
          { name: 'hour_to', label: 'To Hour' }
        ] },
      { tab: 'release', title: 'Effective Date and Release',
        note: 'Released by a Price-Book Releaser who did not author it (BRU-PRC-07). A released premium never changes: a new version with the same code supersedes it.',
        fields: [
          { name: 'valid_from', required: true, label: 'Effective From' },
          { name: 'valid_to', label: 'Effective Until', readonly: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by', label: 'Released By', readonly: true },
          { name: 'note', label: 'Notes', type: 'text' },
          { name: 'company_id', label: 'Legal Entity' }
        ] }
    ]
  },

  /* FR-PRC-024 / BRU-PRC-16: a previewed, approved, scheduled mass change. */
  'M11-form-mass': {
    kind: 'model_form',
    model: 'fix.price.mass.change',
    title: 'Mass Price Change',
    back: 'M11-mass',
    status: { field: 'state', labels: { draft: 'Draft', in_review: 'In Review', approved: 'Approved (scheduled)', applied: 'Applied', rolled_back: 'Rolled Back', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'scope', label: '1. Which Rates', bn: '১. কোন রেট', icon: '🎯', badge: '4' },
      { id: 'change', label: '2. Change & Date', bn: '২. পরিবর্তন ও তারিখ', icon: '📈', badge: '4' },
      { id: 'decision', label: '3. Preview & Approval', bn: '৩. পূর্বরূপ ও অনুমোদন', icon: '✅', badge: '8' }
    ],
    sections: [
      { tab: 'scope', title: 'Which Released Rates It Moves',
        note: 'Every released rate card matching all the filters. Contract rates are negotiated (BRU-PRC-11) and stay out unless ticked.',
        fields: [
          { name: 'line_type', required: true, label: 'Line Type' },
          { name: 'product_code_prefix', label: 'Product Code Starts With' },
          { name: 'category_id', label: 'Catalogue Category' },
          { name: 'include_contract', label: 'Include Contract Rates' }
        ] },
      { tab: 'change', title: 'The Change and When',
        note: 'A future date is approved by a Price-Book Releaser and applied on that date. A change dated today is immediate and needs the CCO (BRU-PRC-16). The author never approves it (BRU-PRC-07).',
        fields: [
          { name: 'change_kind', required: true, label: 'Change By' },
          { name: 'value', required: true, label: 'Change (+ raises, - lowers)' },
          { name: 'effective_date', required: true, label: 'Effective Date' },
          { name: 'reason', required: true, label: 'Reason', type: 'text' }
        ] },
      { tab: 'decision', title: 'Preview and Approval',
        note: 'Preview Affected Rates lists every rate with its new price and floor (Mass Change Preview). A rate that would fall below its floor blocks submission. An applied change rolls back in one step while no rate moved since.',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'line_count', label: 'Rates Affected', readonly: true },
          { name: 'below_floor_count', label: 'Below a Floor', readonly: true },
          { name: 'preview_at', label: 'Previewed On', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by', label: 'Approved By', readonly: true },
          { name: 'applied_at', label: 'Applied On', readonly: true }
        ] }
    ]
  },

  /* BRU-PRC-13: one entry of the governed reason list. */
  'M11-form-reason': {
    kind: 'model_form',
    model: 'fix.discount.reason',
    title: 'Discount Reason Code',
    back: 'M11-reasons',
    tabs: [
      { id: 'reason', label: '1. Reason', bn: '১. কারণ', icon: '🏷️', badge: '5' }
    ],
    sections: [
      { tab: 'reason', title: 'Reason Code',
        note: 'Kept by Pricing Officers. Once the first code is active, a discount above the threshold cannot be sent for approval without one. A code that was used is archived, never renamed or deleted.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Reason' },
          { name: 'description', label: 'When to Use It', type: 'text' },
          { name: 'sequence', label: 'Order in the List' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M11-price-explanation': { kind: 'model_list', model: 'fix.price.explanation', create: false,
    cols: ['name', 'company_id', 'operating_unit_id', 'rule_id', 'currency_id', 'base_price', 'final_price'],
    empty: 'No price has been explained yet. An explanation is written each time the pricing engine prices a line; it is the audit trail of that price and cannot be typed in.',
    // append-only trail (BRU-PRC-02): reconstruct, never edit
    actions: [{ m: 'action_reconstruct', l: 'Reconstruct from the Rule' }] },

  'M11-form-price-explanation': {
    kind: 'model_form',
    model: 'fix.price.explanation',
    title: "Price Explanation",
    back: 'M11-price-explanation',
    create: false, pick: 'A price explanation is written by the pricing engine: open one from Price Explanations.',
    tabs: [
      { id: 'general', label: '1. Explanation Header', bn: '১. ব্যাখ্যার শিরোনাম', icon: '📄', badge: '3' },
      { id: 'commercial', label: '2. Price Derivation', bn: '২. মূল্য নির্ধারণ', icon: '💵', badge: '4' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Explanation Header',
        note: 'Every dynamic price writes an explanation record. This is the trail a customer dispute or a commercial audit reads back; it is append-only (BRU-PRC-02).',
        fields: [
          { name: 'name', required: true, label: "Reference", readonly: true },
          { name: 'company_id', required: true, label: "Legal Entity", readonly: true },
          { name: 'currency_id', required: true, label: "Currency", readonly: true }
        ] },
      { tab: 'commercial', title: 'How the Price Was Derived', fields: [
        { name: 'rule_id', label: "Applied Rule", readonly: true },
        { name: 'base_price', label: "Base Price", readonly: true },
        { name: 'final_price', label: "Final Price", readonly: true },
        { name: 'rules_applied', label: "Rules Applied", type: 'text', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit Trail', fields: [
        { name: 'operating_unit_id', label: "Operating Unit", readonly: true },
        { name: 'model_driven', label: "Model Driven", readonly: true },
        { name: 'create_date', label: "Computed At", readonly: true }
      ] }
    ]
  }
};

/* Built-in report chips -> their computed pack. These seven routes used to
 * sit inside SCREENS (so the merge never saw them and every M11 report chip
 * answered "arrives with the workspace phase"). */
export const REPORT_ROUTES = {
  'M11:Price Exceptions': 'M11-rpt-exceptions',
  'M11:Price Consistency Monitor': 'M11-rpt-consistency',
  'M11:Floor vs Realised Rate': 'M11-rpt-floors',
  'M11:Realised Price vs Card': 'M11-rpt-realised',
  'M11:Discount Register by Approver': 'M11-rpt-discount',
  'M11:Rate-Card Utilisation': 'M11-rpt-util',
  'M11:Margin by Service Line': 'M11-rpt-margin',
  'M11:Promotion Effectiveness': 'M11-rpt-promo',
  'M11:Brand Reimbursement Recovery': 'M11-rpt-brand'
};

export const FORM_MODELS = {
  'M11:Price Book': 'fix.price.book',
  'M11:Rate Card': 'fix.rate.card',
  'M11:Discount Policy': 'fix.discount.policy',
  'M11:Promotion': 'fix.promotion',
  'M11:Price Simulation Request': 'fix.price.simulation',
  'M11:Dynamic Price Rule': 'fix.dynamic.price.rule',
  'M11:Discount Approval': 'fix.discount.approval',
  'M11:Price Floor': 'fix.price.floor',
  'M11:Price Book Version': 'fix.price.version',
  'M11:Price Change Request': 'fix.price.change',
  'M11:Brand Reimbursement Rate': 'fix.brand.reimbursement.rate',
  'M11:Parts Pricing Scheme': 'fix.parts.price.scheme',
  'M11:Price Premium': 'fix.price.adjustment',
  'M11:Mass Price Change': 'fix.price.mass.change',
  'M11:Discount Reason Code': 'fix.discount.reason',
  'M11:Below-Floor Override': 'fix.price.override',
  'M11:Channel Differential': 'fix.channel.differential',
  'M11:Volume Break': 'fix.price.break'
};

export const FORM_CHIPS = {
  'M11:Dynamic Price Rule': 'M11-form-pricerule',
  'M11:Price Book': 'M11-form-book',
  'M11:Rate Card': 'M11-form-card',
  'M11:Discount Policy': 'M11-form-policy',
  'M11:Promotion': 'M11-form-promo',
  'M11:Price Simulation Request': 'M11-form-simulation',
  'M11:Discount Approval': 'M11-form-discount-approval',
  'M11:Price Floor': 'M11-form-floor',
  'M11:Price Book Version': 'M11-form-version',
  'M11:Price Change Request': 'M11-form-change',
  'M11:Brand Reimbursement Rate': 'M11-form-brand-rate',
  'M11:Parts Pricing Scheme': 'M11-form-parts-scheme',
  'M11:Price Premium': 'M11-form-premium',
  'M11:Mass Price Change': 'M11-form-mass',
  'M11:Discount Reason Code': 'M11-form-reason',
  'M11:Below-Floor Override': 'M11-form-override',
  'M11:Channel Differential': 'M11-form-differential',
  'M11:Volume Break': 'M11-form-break',
  'M11:__by_model__': {
    'fix.parts.price.scheme': 'M11-form-parts-scheme',
    'fix.price.adjustment': 'M11-form-premium',
    'fix.price.mass.change': 'M11-form-mass',
    'fix.discount.reason': 'M11-form-reason',
    'fix.brand.reimbursement.rate': 'M11-form-brand-rate',
    'fix.price.explanation': 'M11-form-price-explanation',
    'fix.dynamic.price.rule': 'M11-form-pricerule',
    'fix.price.book': 'M11-form-book',
    'fix.rate.card': 'M11-form-card',
    'fix.discount.policy': 'M11-form-policy',
    'fix.discount.approval': 'M11-form-discount-approval',
    'fix.promotion': 'M11-form-promo',
    'fix.price.simulation': 'M11-form-simulation',
    'fix.price.version': 'M11-form-version',
    'fix.price.floor': 'M11-form-floor',
    'fix.price.change': 'M11-form-change',
    'fix.price.override': 'M11-form-override',
    'fix.channel.differential': 'M11-form-differential',
    'fix.price.break': 'M11-form-break'
  },
  'M11:__by_screen__': {
    'M11-price-explanation': 'M11-form-price-explanation',
    'M11-adjust': 'M11-form-pricerule',
    'M11-books': 'M11-form-book',
    'M11-labour': 'M11-form-card',
    'M11-parts': 'M11-form-card',
    'M11-contract': 'M11-form-card',
    'M11-brand': 'M11-form-brand-rate',
    'M11-versions': 'M11-form-version',
    'M11-floors': 'M11-form-floor',
    'M11-promos': 'M11-form-promo',
    'M11-simulate': 'M11-form-simulation',
    'M11-discounts': 'M11-form-discount-approval',
    'M11-changes': 'M11-form-change',
    'M11-policies': 'M11-form-policy',
    'M11-parts-schemes': 'M11-form-parts-scheme',
    'M11-premiums': 'M11-form-premium',
    'M11-mass': 'M11-form-mass',
    'M11-reasons': 'M11-form-reason',
    'M11-overrides': 'M11-form-override',
    'M11-differentials': 'M11-form-differential',
    'M11-breaks': 'M11-form-break'
  }
};

export const CREATE = {
  M11: { screen: 'M11-form-book', model: 'fix.price.book', label: 'Price Book' }
};
