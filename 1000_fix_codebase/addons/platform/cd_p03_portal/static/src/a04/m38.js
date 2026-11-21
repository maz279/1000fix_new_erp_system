/** @odoo-module **/
/* A04 · Commercial & Revenue — M38 E-Commerce Storefront (v2 rebuild).
 * A04 audit (2026-11-04): workflow fields are read-only; the lifecycle runs
 * from the list actions.
 * Registry-faithful: 4 groups / 11 screens / 6 reports / 4 forms / freg 92.
 * Carts, storefront orders and graded stock are real; RMA and slots are new.
 * Payment mix comes from the order's payment rail; refurb GMV by grade is a
 * declared gap (no order↔grade link).
 * Capture audit (19 Nov 2026): every sub-module page now captures its own
 * record - content, collections, assisted/corporate carts, COD rules, order
 * changes, exposure and return policies, corporate accounts, recovery
 * contacts and service bookings (cd_storefront fix_storefront_capture.py). */

export const MODULE = {
  area: 'A04', code: 'M38', en: 'E-Commerce Storefront', title: 'M38 · E-Commerce Storefront',
  bn: 'ই-কমার্স স্টোরফ্রন্ট', icon: '🛒',
  desc: 'Storefront browse and merchandising, cart and checkout orchestration, delivery slots, online orders, returns/RMA, refurb stock exposure, checkout promotions and abandoned-cart recovery.',
  kpis: [
    { l: 'Orders MTD', m: 'orders_mtd' },
    { l: 'Conversion', m: 'conversion', suffix: '%' },
    { l: 'Cart Abandon', m: 'cart_abandon', suffix: '%' },
    { l: 'bKash Share', m: 'bkash_share', suffix: '%' },
    { l: 'Refurb GMV MTD', m: 'refurb_gmv_mtd', prefix: '৳ ' },
    { l: 'RMA Rate', m: 'rma_rate', suffix: '%' }
  ],
  groups: [
    { en: 'Storefront Records', screens: [
      { id: 'M38-storefront-return', en: "Storefront Return", bn: "Storefront Return", t: 'g' }
    ]},
    { en: 'Storefront', screens: [
      { id: 'M38-content', en: 'Banners & Pages', bn: 'ব্যানার ও পেজ', t: 'g' },
      { id: 'M38-collections', en: 'Collections & Cross-sell', bn: 'কালেকশন', t: 'g' },
      { id: 'M38-storefront', en: 'Storefront Preview', bn: 'স্টোরফ্রন্ট', t: 'r' },
      { id: 'M38-merch', en: 'Merchandising', bn: 'মার্চেন্ডাইজিং', t: 'r' },
      { id: 'M38-compat', en: 'Compatibility Filters', bn: 'কম্প্যাটিবিলিটি', t: 'r' }
    ]},
    { en: 'Cart & Checkout', screens: [
      { id: 'M38-carts', en: 'Carts & Abandonment', bn: 'কার্ট', t: 'g' },
      { id: 'M38-checkout', en: 'Checkout & Payment Orchestration', bn: 'চেকআউট', t: 'r' },
      { id: 'M38-delivery', en: 'Delivery Options', bn: 'ডেলিভারি', t: 'r' },
      { id: 'M38-slots', en: 'Delivery Slots', bn: 'ডেলিভারি স্লট', t: 'g' },
      { id: 'M38-cod-rules', en: 'COD Eligibility Rules', bn: 'ক্যাশ অন ডেলিভারি নিয়ম', t: 'g' },
      { id: 'M38-service-bookings', en: 'Service Bookings', bn: 'সার্ভিস বুকিং', t: 'g' }
    ]},
    { en: 'Orders', screens: [
      { id: 'M38-orders', en: 'Online Orders', bn: 'অনলাইন অর্ডার', t: 'g' },
      { id: 'M38-returns', en: 'Returns & RMA', bn: 'রিটার্ন', t: 'g' },
      { id: 'M38-order-changes', en: 'Order Changes', bn: 'অর্ডার পরিবর্তন', t: 'g' },
      { id: 'M38-exposure', en: 'Stock Exposure Policy', bn: 'স্টক এক্সপোজার', t: 'g' },
      { id: 'M38-stock', en: 'Refurbished Stock (from M15)', bn: 'রিফার্বিশড স্টক', t: 'g' },
      { id: 'M38-return-policies', en: 'Return Policies', bn: 'রিটার্ন নীতি', t: 'g' }
    ]},
    { en: 'B2B Commerce', screens: [
      { id: 'M38-corporate-accounts', en: 'Corporate Commerce Accounts', bn: 'কর্পোরেট অ্যাকাউন্ট', t: 'g' },
      { id: 'M38-corporate-orders', en: 'Corporate Orders', bn: 'কর্পোরেট অর্ডার', t: 'g' }
    ]},
    { en: 'Commerce Marketing', screens: [
      { id: 'M38-promos', en: 'Checkout Promotions (from M11)', bn: 'প্রমোশন (M11)', t: 'g' },
      { id: 'M38-recovery', en: 'Abandoned-Cart Recovery', bn: 'কার্ট রিকভারি', t: 'r' },
      { id: 'M38-recovery-attempts', en: 'Recovery Contacts', bn: 'রিকভারি যোগাযোগ', t: 'g' }
    ]}
  ],
  reports: ['Funnel & Conversion', 'Payment Method Mix', 'Refurb GMV by Grade', 'Delivery Performance', 'RMA & Returns Report', 'Abandonment Recovery Rate'],
  forms: ['Online Order', 'RMA Request', 'Storefront Slot', 'Delivery Slot', 'Storefront Content',
    'Storefront Collection', 'Assisted Cart', 'COD Rule', 'Order Change', 'Stock Exposure Policy',
    'Return Policy', 'Corporate Commerce Account', 'Corporate Order', 'Cart Recovery Contact', 'Service Booking'],
  cross: ['M20 AR', 'M37 Catalogue', 'M11 Pricing', 'M31 Refurb'],
  freg: { src: 92, sub: [
    ['1', 'Storefront & Browse', 12, { model: 'fix.storefront.content', cols: ['name', 'content_type', 'slot', 'audience', 'valid_from', 'valid_to', 'state'], screens: ['M38-content', 'M38-storefront', 'M38-rpt-funnel'], reports: ['Funnel & Conversion'], forms: ['Storefront Content'] }],
    ['2', 'Merchandising', 7, { model: 'fix.storefront.collection', cols: ['name', 'collection_type', 'anchor_product_id', 'valid_from', 'valid_to', 'state'], screens: ['M38-collections', 'M38-merch', 'M38-compat'], reports: ['Refurb GMV by Grade'], forms: ['Storefront Collection'] }],
    ['3', 'Cart', 9, { model: 'fix.storefront.cart', cols: ['name', 'channel', 'customer_id', 'state', 'total', 'order_id'], screens: ['M38-carts'], reports: ['Abandonment Recovery Rate'], forms: ['Assisted Cart'] }],
    ['4', 'Checkout & Payments', 14, { model: 'fix.storefront.cod.rule', cols: ['name', 'max_order_value', 'history_value', 'min_delivered_orders', 'max_open_cod_orders', 'state'], screens: ['M38-cod-rules', 'M38-checkout', 'M38-promos', 'M38-rpt-pay', 'M38-orders'], reports: ['Payment Method Mix', 'Funnel & Conversion'], forms: ['COD Rule'] }],
    ['5', 'Online Orders', 9, { model: 'fix.storefront.order', cols: ['name', 'customer_id', 'order_date', 'total_amount', 'shipping_method', 'state'], screens: ['M38-orders', 'M38-order-changes'], reports: ['Payment Method Mix'], forms: ['Online Order', 'Order Change'], create: 'M38-form-order-change', createLabel: 'Request Order Change' }],
    ['6', 'Stock Exposure', 6, { model: 'fix.stock.exposure.policy', cols: ['name', 'product_id', 'category_id', 'buffer_qty', 'buffer_pct', 'enabled', 'state'], screens: ['M38-exposure', 'M38-stock', 'M38-rpt-refurb'], reports: ['Refurb GMV by Grade'], forms: ['Stock Exposure Policy'] }],
    ['7', 'Returns & RMA', 9, { model: 'fix.storefront.rma', cols: ['name', 'state', 'customer_id', 'order_id', 'reason', 'requested_on', 'refund_amount'], screens: ['M38-returns', 'M38-storefront-return', 'M38-return-policies', 'M38-rpt-rma'], reports: ['RMA & Returns Report'], forms: ['RMA Request', 'Return Policy'] }],
    ['8', 'B2B Commerce', 11, { model: 'fix.storefront.corporate.account', cols: ['name', 'approval_threshold', 'po_required', 'state'], screens: ['M38-corporate-accounts', 'M38-corporate-orders'], reports: [], forms: ['Corporate Commerce Account', 'Corporate Order'] }],
    ['9', 'Recovery & Analytics', 9, { model: 'fix.storefront.cart', cols: ['name', 'customer_id', 'state', 'total', 'create_date'], screens: ['M38-recovery', 'M38-recovery-attempts', 'M38-rpt-recovery', 'M38-carts'], reports: ['Abandonment Recovery Rate'], forms: ['Cart Recovery Contact'], domain: [['state', 'in', ['open', 'checkout']]], create: 'M38-form-recovery', createLabel: 'Record Recovery Contact' }],
    ['10', 'Service Booking Commerce', 6, { model: 'fix.storefront.service.booking', cols: ['name', 'customer_id', 'device_id', 'branch_id', 'slot_id', 'state'], screens: ['M38-service-bookings', 'M38-slots', 'M38-delivery', 'M38-rpt-delivery'], reports: ['Delivery Performance'], forms: ['Service Booking', 'Storefront Slot', 'Delivery Slot'] }]
  ] }
};

export const SCREENS = {
  'M38-storefront': { kind: 'table_report', module: 'M38', report: 'funnel_conversion', title: 'Storefront Preview', period: false },
  'M38-merch': { kind: 'table_report', module: 'M38', report: 'merchandising', title: 'Merchandising', period: false },
  'M38-compat': { kind: 'table_report', module: 'M38', report: 'stock_availability', title: 'Compatibility Filters', period: false },
  /* Capture audit (19 Nov 2026): customers open carts on the storefront;
   * staff capture an ASSISTED cart for a customer on the phone or at a branch
   * (spec §13: R08/R34 assisted ordering) - priced by the server, placed
   * through the same checkout. */
  'M38-carts': { kind: 'model_list', model: 'fix.storefront.cart', stateField: 'state',
    cols: ['name', 'channel', 'customer_id', 'state', 'total', 'terms_accepted_at', 'order_id'],
    empty: 'No cart yet. Customers open carts on the storefront; "+ New" captures an assisted cart for a customer.',
    actions: [
      { m: 'action_record_terms', l: 'Record Terms Acceptance', states: ['open', 'checkout'] },
      { m: 'action_place_assisted_order', l: 'Place Order', states: ['open', 'checkout'] }
    ] },
  'M38-checkout': { kind: 'table_report', module: 'M38', report: 'checkout_conversion', title: 'Checkout & Payment Orchestration', period: false },
  'M38-delivery': { kind: 'table_report', module: 'M38', report: 'delivery_performance', title: 'Delivery Options', period: false },
  /* A04 audit (2026-11-04) C3: the order lifecycle runs from these buttons;
   * the status, the payment and the total are read-only on the form. The
   * server checks the role, the M20 receipt (or the signed gateway callback),
   * the consignment and its POD for each. */
  'M38-orders': { kind: 'model_list', create: false, model: 'fix.storefront.order', stateField: 'state',
    cols: ['name', 'customer_id', 'order_date', 'payment_rail', 'total_amount', 'shipping_method', 'delivery_sla_status', 'state'],
    actions: [
      { m: 'action_confirm_payment', l: 'Confirm Payment (M20 Receipt)', ask: 'M20 receipt number or reference', kwarg: 'payment_ref', states: ['draft', 'pending_payment'] },
      { m: 'action_dispatch', l: 'Dispatch on Consignment', ask: 'M03 consignment reference (blank for branch pickup)', kwarg: 'carrier_consignment_id', states: ['pending_payment', 'paid'] },
      { m: 'action_deliver', l: 'Mark Delivered (needs POD)', states: ['dispatched'] },
      { m: 'action_cancel', l: 'Cancel Order', ask: 'Reason for cancelling', kwarg: 'reason', states: ['draft', 'pending_payment', 'paid'] }
    ] },
  /* A04 audit M38-5/13: the refund is approved from the M63 inbox (Request
   * Refund Approval); the approver holds the DOFA tier and did not raise it. */
  'M38-returns': { kind: 'model_list', model: 'fix.storefront.rma', stateField: 'state',
    cols: ['name', 'customer_id', 'order_id', 'reason', 'refund_amount', 'approval_state', 'state'],
    actions: [
      { m: 'action_approve', l: 'Authorise Return', states: ['requested'] },
      { m: 'action_receive_and_inspect', l: 'Receive & Inspect', ask: 'Inspection result: grade_a, grade_b or scrap', kwarg: 'condition', states: ['approved'] },
      { m: 'action_request_approval', l: 'Request Refund Approval', ask: 'Justification for the refund', kwarg: 'justification', states: ['received'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['received'] },
      { m: 'action_reject', l: 'Reject Return', ask: 'Reason for rejecting', kwarg: 'reason', states: ['requested', 'approved', 'received'] },
      { m: 'action_record_credit_note', l: 'Record M20 Credit Note', ask: 'M20 credit note number (Mushak 6.7)', kwarg: 'credit_note', states: ['refund_approved'] }
    ] },
  /* Graded refurb units are graded and valued in M14/M15; the storefront
   * sells them (capture audit 19 Nov 2026: this list offered "+ New"). */
  'M38-stock': { kind: 'model_list', model: 'fix.graded.stock', stateField: 'state', create: false,
    cols: ['name', 'device_id', 'grade_id', 'resale_price', 'state'],
    empty: 'No refurbished unit yet. Units are graded in M14 and stocked in M15; the storefront sells them.' },
  // Promotions are MASTERED in M11 (Pricing & Rate Cards). This is the
  // storefront's scoped view of that master - online-facing promotions
  // only - not a second copy of it. It used to repeat M11-promos column
  // for column, which is the duplication this estate forbids.
  'M38-promos': { kind: 'model_list', model: 'fix.promotion', stateField: 'state',
    create: false,
    domain: [['channel', 'in', ['online', 'both']]],
    cols: ['code', 'name', 'discount_type', 'value', 'state'] },
  'M38-slots': { kind: 'model_list', model: 'fix.storefront.slot', stateField: 'state',
    cols: ['name', 'slot_type', 'slot_date', 'start_hour', 'end_hour', 'capacity', 'booked', 'state'],
    actions: [
      { m: 'action_close', l: 'Close Slot', states: ['open', 'full'] },
      { m: 'action_reopen', l: 'Reopen Slot', states: ['closed'] }
    ] },
  /* ============ capture audit (19 Nov 2026): the pages' own records ============ */
  'M38-content': { kind: 'model_list', model: 'fix.storefront.content', stateField: 'state',
    cols: ['code', 'name', 'name_bn', 'content_type', 'slot', 'audience', 'valid_from', 'valid_to', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'published'] }
    ] },
  'M38-collections': { kind: 'model_list', model: 'fix.storefront.collection', stateField: 'state',
    cols: ['code', 'name', 'name_bn', 'collection_type', 'anchor_product_id', 'category_id', 'valid_from', 'valid_to', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'published'] }
    ] },
  'M38-cod-rules': { kind: 'model_list', model: 'fix.storefront.cod.rule', stateField: 'state',
    cols: ['name', 'max_order_value', 'history_value', 'min_delivered_orders', 'max_open_cod_orders', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_activate', l: 'Approve & Activate', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'active'] }
    ] },
  'M38-order-changes': { kind: 'model_list', model: 'fix.storefront.order.change', stateField: 'state',
    cols: ['name', 'order_id', 'customer_id', 'change_type', 'reason', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply Change', states: ['requested'] },
      { m: 'action_refuse', l: 'Refuse', ask: 'Reason for refusing', kwarg: 'reason', states: ['requested'] }
    ] },
  'M38-exposure': { kind: 'model_list', model: 'fix.stock.exposure.policy', stateField: 'state',
    cols: ['name', 'product_id', 'category_id', 'buffer_qty', 'buffer_pct', 'max_promise_days', 'enabled', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_activate', l: 'Approve & Activate', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'active'] }
    ] },
  'M38-return-policies': { kind: 'model_list', model: 'fix.storefront.return.policy', stateField: 'state',
    cols: ['name', 'category_id', 'window_days', 'restocking_fee_pct', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_activate', l: 'Approve & Activate', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'active'] }
    ] },
  'M38-corporate-accounts': { kind: 'model_list', model: 'fix.storefront.corporate.account', stateField: 'state',
    cols: ['name', 'approval_threshold', 'po_required', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_activate', l: 'Approve & Activate', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'active'] }
    ] },
  'M38-corporate-orders': { kind: 'model_list', model: 'fix.storefront.cart', stateField: 'state',
    domain: [['corporate_account_id', '!=', false]],
    cols: ['name', 'corporate_account_id', 'customer_id', 'po_reference', 'total', 'client_approved_at', 'state', 'order_id'],
    empty: 'No corporate order yet. The Corporate Order chip captures one for an active corporate account.',
    actions: [
      { m: 'action_record_client_approval', l: 'Record Client Approval', states: ['open', 'checkout'] },
      { m: 'action_place_assisted_order', l: 'Place Order', states: ['open', 'checkout'] }
    ] },
  'M38-recovery-attempts': { kind: 'model_list', model: 'fix.storefront.recovery.attempt',
    cols: ['cart_id', 'customer_id', 'cart_total', 'channel', 'outcome', 'contacted_by_id', 'contacted_at', 'converted'] },
  'M38-service-bookings': { kind: 'model_list', model: 'fix.storefront.service.booking', stateField: 'state',
    cols: ['name', 'customer_id', 'device_id', 'branch_id', 'slot_id', 'channel', 'service_order_id', 'state'],
    actions: [
      { m: 'action_confirm', l: 'Confirm (raise M01 service order)', states: ['requested'] },
      { m: 'action_cancel', l: 'Cancel Booking', ask: 'Reason for cancelling', kwarg: 'reason', states: ['requested'] }
    ] },
  'M38-recovery': { kind: 'table_report', module: 'M38', report: 'abandonment_recovery', title: 'Abandoned-Cart Recovery', period: false },

  /* Report chips -> their own computed pack */
  'M38-rpt-funnel': { kind: 'table_report', module: 'M38', report: 'funnel_conversion', title: 'Funnel & Conversion', period: false },
  'M38-rpt-pay': { kind: 'table_report', module: 'M38', report: 'payment_method_mix', title: 'Payment Method Mix', period: false },
  'M38-rpt-refurb': { kind: 'table_report', module: 'M38', report: 'refurb_gmv', title: 'Refurb GMV by Grade', period: false },
  'M38-rpt-delivery': { kind: 'table_report', module: 'M38', report: 'delivery_performance', title: 'Delivery Performance', period: false },
  'M38-rpt-rma': { kind: 'table_report', module: 'M38', report: 'rma_report', title: 'RMA & Returns Report', period: false },
  'M38-rpt-recovery': { kind: 'table_report', module: 'M38', report: 'abandonment_recovery', title: 'Abandonment Recovery Rate', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M38-form-order': {
    lines: {
      field: 'line_ids',
      title: 'Order Lines',
      note: 'The lines are what the customer bought, at the price the server set at placement; they cannot be edited.',
      fields: [
        { name: 'product_id', label: 'Product', readonly: true },
        { name: 'graded_stock_id', label: 'Refurbished Item', readonly: true },
        { name: 'quantity', label: 'Qty', readonly: true },
        { name: 'unit_price', label: 'Unit Price', readonly: true },
        { name: 'subtotal', label: 'Subtotal', readonly: true }
      ]
    },
    kind: 'model_form',
    model: 'fix.storefront.order',
    title: 'E-Commerce Storefront Customer Order',
    back: 'M38-orders',
    /* An online order is placed by the customer at storefront checkout; no
     * back-office role may create one (fix.storefront.order grants staff read
     * and write only), so "+ New" here could only fail (fix_real, 12 Nov). */
    create: false,
    pick: 'An online order is placed by the customer at storefront checkout: open one from Online Orders.',
    status: { field: 'state' },
    tabs: [
      { id: 'order', label: '1. Order Identity', bn: '১. অর্ডার পরিচিতি', icon: '🛍️', badge: '5' },
      { id: 'items', label: '2. Line Items & Graded Stock', bn: '২. পণ্য ও স্টক', icon: '📦', badge: '2' },
      { id: 'payment_logistics', label: '3. Payment & Logistics SLA', bn: '৩. পেমেন্ট ও ডেলিভারি', icon: '🚚', badge: '6' },
      { id: 'tax_invoice', label: '4. Mushak 6.3 Tax Invoicing', bn: '৪. মূসক ৬.৩ চালান', icon: '🧾', badge: '2' },
      { id: 'reverse_rma', label: '5. Reverse RMA & Credit Notes', bn: '৫. রিটার্ন ও ক্রেডিট নোট', icon: '↩️', badge: '2' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'order', title: 'Customer Order Master Header',
        note: 'Customer order placed via public website or storefront portal with instant gateway confirmation.',
        fields: [
          { name: 'name', readonly: true, label: 'Order Reference (auto)' },
          { name: 'customer_id', readonly: true, label: 'Customer Record' },
          { name: 'order_date', readonly: true, label: 'Order Placed Date/Time' },
          { name: 'total_amount', readonly: true, label: 'Order Grand Total (BDT)' },
          { name: 'state', readonly: true, label: 'Fulfillment Status' }
        ] },
      { tab: 'items', title: 'Cart Line Items & Warranty Packages',
        fields: [
          { name: 'shipping_address', required: true, label: 'Delivery Shipping Address', type: 'text' }
        ] },
      { tab: 'payment_logistics', title: 'Payment Gateways & Delivery SLA Countdown',
        note: 'Compliance with Bangladesh Digital Commerce Operational Guidelines 2021 (maximum 48h/72h delivery SLA).',
        fields: [
          { name: 'payment_rail', readonly: true, label: 'Payment Method (bKash / Nagad / SSL)' },
          { name: 'payment_ref', readonly: true, label: 'Payment Gateway Transaction ID (TrxID)' },
          { name: 'payment_date', readonly: true, label: 'Payment Confirmation Date' },
          { name: 'payment_source', readonly: true, label: 'Payment Proof' },
          { name: 'amount_paid', readonly: true, label: 'Amount Paid (BDT)' },
          { name: 'shipping_method', required: true, label: 'Logistics SLA Tier' },
          { name: 'carrier_consignment_id', readonly: true, label: 'M03 Consignment' },
          { name: 'slot_id', readonly: true, label: 'Delivery Slot' },
          { name: 'delivered_at', readonly: true, label: 'Delivered At (POD)' },
          { name: 'return_deadline', readonly: true, label: 'Returnable Until' },
          { name: 'delivery_due_date', label: 'Statutory Delivery Due Date', readonly: true },
          { name: 'delivery_sla_status', label: 'SLA Status', readonly: true }
        ] },
      { tab: 'tax_invoice', title: 'NBR Mushak 6.3 Tax Invoice Generation',
        note: 'The payment is proved by its M20 receipt or the signed gateway callback; the Mushak 6.3 invoice is raised by M20 from storefront.payment_confirmed.',
        fields: [
          { name: 'payment_receipt_id', readonly: true, label: 'M20 Receipt' }
        ] },
      { tab: 'reverse_rma', title: 'Customer Returns & Mushak 6.7 Credit Notes',
        note: 'Returns run from the Returns screens; an approved refund completes on its M20 Mushak 6.7 credit note. A cancelled paid order shows the refund sent to finance.',
        fields: [
          { name: 'refund_due', readonly: true, label: 'Refund Due on Cancellation (BDT)' }
        ] },
      { tab: 'vault', title: 'Storefront Order Vault',
        note: 'Customer proof of payment, digital receipts, courier air waybills, and inspection logs.',
        fields: [] }
    ]
  },

  'M38-form-rma': {
    kind: 'model_form',
    model: 'fix.storefront.rma',
    title: 'E-Commerce Return Merchandise Authorisation (RMA)',
    back: 'M38-returns',
    status: { field: 'state' },
    tabs: [
      { id: 'rma_header', label: '1. Return Request', bn: '১. ফেরতের আবেদন', icon: '↩️', badge: '4' },
      { id: 'inspection_refund', label: '2. Inspection & Refund Value', bn: '২. পরিদর্শন ও ফেরত মূল্য', icon: '🔍', badge: '3' },
      { id: 'resolution', label: '3. Resolution & Note', bn: '৩. নিষ্পত্তি ও মন্তব্য', icon: '✅', badge: '2' }
    ],
    sections: [
      { tab: 'rma_header', title: 'Return Authorization Request', note: 'Consumer return under Digital Commerce Guidelines 2021.',
        fields: [
          { name: 'name', readonly: true, label: 'RMA Tracking Number (auto)' },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'order_id', required: true, label: 'Storefront Order Reference' },
          { name: 'reason', required: true, label: 'Return Grounds' }
        ] },
      { tab: 'inspection_refund', title: 'Technical Inspection & NBR Credit Note', fields: [
          { name: 'requested_on', required: true, label: 'Date Requested' },
          { name: 'refund_amount', label: 'Refund Requested (BDT, capped at the amount paid)' },
          { name: 'inspected_condition', readonly: true, label: 'Inspection Result' },
          { name: 'disposition', readonly: true, label: 'Disposition' },
          { name: 'dofa_tier_required', readonly: true, label: 'DOFA Tier Required' },
          { name: 'dofa_justification', label: 'Refund Justification', type: 'text' },
          { name: 'approval_state', readonly: true, label: 'Refund Approval' },
          { name: 'credit_note_ref', readonly: true, label: 'M20 Credit Note (Mushak 6.7)' }
          ] },
      { tab: 'resolution', title: 'Settlement Status', fields: [
          { name: 'state', readonly: true, label: 'RMA Lifecycle State' },
          { name: 'rejection_reason', readonly: true, label: 'Rejection Reason' },
          { name: 'note', label: 'Notes', type: 'text' }
        ] }
    ]
  },
  'M38-form-delivery-slot': { kind: 'model_form', model: 'fix.storefront.slot',
    title: 'Delivery Slot', back: 'M38-delivery',
    lines: {
      field: 'order_ids',
      title: 'Booked Orders',
      note: 'The slot bookings are its orders (A04 audit M38-8); they are booked at checkout, never typed here.',
      fields: [
        { name: 'name', label: 'Order', readonly: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ]
    },
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Slot Name', required: true },
        { name: 'slot_type', label: 'Slot Type', required: true },
        { name: 'start_hour', label: 'Start Hour', required: true },
        { name: 'end_hour', label: 'End Hour', required: true },
        { name: 'capacity', label: 'Capacity', required: true },
        { name: 'booked', label: 'Booked (its orders)', readonly: true },
        { name: 'state', label: 'State', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'slot_date', label: 'Date', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true }
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
  /* Graded refurb units are created and valued in M14/M15 (capture audit
   * 19 Nov 2026: the storefront offered "+ New Graded Stock Item"). */
  'M38-form-gstock': { kind: 'model_form', model: 'fix.graded.stock',
    title: 'Graded Stock Item', back: 'M38-stock', create: false,
    pick: 'A refurbished unit is graded in M14 and stocked in M15: open one from Refurbished Stock.',
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
        { name: 'name', label: 'Stock Tag / Serial', required: true },
        { name: 'tradein_id', label: 'Originating Trade-In ID', readonly: true },
        { name: 'tradein_ref', label: 'Originating Trade-In Ref' },
        { name: 'inventory_valuation', label: 'Inventory Valuation', readonly: true },
        { name: 'state', label: 'Inventory Status (reserved and sold by orders)', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        /* A05 ERP M14-04 / XC-09: cost and price are set by M14 (payout, refurbishment
         * absorption, approved listing price / markdown) and guarded on the model */
        { name: 'acquisition_cost', label: 'Acquisition Cost (Trade-In)', readonly: true },
        { name: 'refurbishment_cost', label: 'Refurbishment Cost', readonly: true },
        { name: 'resale_price', label: 'Approved Resale Price (M14)', readonly: true },
        { name: 'projected_margin', label: 'Projected Margin', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'device_id', label: 'Device Serial', required: true },
        { name: 'grade_id', label: 'Refurbishment Grade', required: true },
        { name: 'location_id', label: 'Warehouse Location' },
        { name: 'currency_id', label: 'Currency', required: true }
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
  'M38-storefront-return': { kind: 'model_list', model: 'fix.storefront.return', stateField: 'state',
    cols: ['name', 'state', 'company_id', 'operating_unit_id', 'cart_id', 'order_id', 'customer_id', 'refund_amount', 'approval_state'],
    actions: [
      { m: 'action_approve', l: 'Authorise Return', states: ['requested'] },
      { m: 'action_receive_and_inspect', l: 'Receive & Inspect', ask: 'Inspection result: grade_a, grade_b or scrap', kwarg: 'condition', states: ['approved'] },
      { m: 'action_request_approval', l: 'Request Refund Approval', ask: 'Justification for the refund', kwarg: 'justification', states: ['received'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['received'] },
      { m: 'action_reject', l: 'Reject Return', ask: 'Reason for rejecting', kwarg: 'reason', states: ['requested', 'approved', 'received'] },
      { m: 'action_record_credit_note', l: 'Record M20 Credit Note', ask: 'M20 credit note number (Mushak 6.7)', kwarg: 'credit_note', states: ['refund_approved'] }
    ] },

  'M38-form-storefront-return': { kind: 'model_form', model: 'fix.storefront.return',
    title: 'Storefront Return', back: 'M38-storefront-return',
    status: { field: 'state' },
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
        { name: 'name', label: 'RMA Number', readonly: true },
        { name: 'reason', label: 'Reason', required: true },
        { name: 'inspected_condition', label: 'Inspection Result', readonly: true },
        { name: 'disposition', label: 'Disposition', readonly: true },
        { name: 'credit_note_ref', label: 'NBR Mushak 6.7 Credit Note Ref', readonly: true },
        { name: 'state', label: 'State', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'refund_amount', label: 'Refund Requested (capped at the amount paid)' },
        { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
        { name: 'dofa_justification', label: 'Refund Justification', type: 'text' },
        { name: 'approval_state', label: 'Refund Approval', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'cart_id', label: 'Original Cart' },
        { name: 'order_id', label: 'Original Order' },
        { name: 'customer_id', label: 'Customer', required: true },
        { name: 'currency_id', label: 'Currency', required: true },
        { name: 'carrier_consignment_id', label: 'Reverse Logistics Consignment' }
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

  /* ===== capture audit (19 Nov 2026): one form per page record ===== */
  'M38-form-content': { kind: 'model_form', model: 'fix.storefront.content',
    title: 'Storefront Content', back: 'M38-content',
    status: { field: 'state' },
    tabs: [
      { id: 'content', label: '1. Content', bn: '১. বিষয়বস্তু' },
      { id: 'placement', label: '2. Placement & Validity', bn: '২. স্থান ও মেয়াদ' },
      { id: 'docs', label: '3. Image', bn: '৩. ছবি' },
      { id: 'audit', label: '4. Publication', bn: '৪. প্রকাশ' }
    ],
    sections: [
      { tab: 'content', title: 'Bilingual Content', note: 'Bengali is the storefront default: nothing is published in one language only. A banner needs its image; a page needs its text in both languages. Published content is fixed - retire it and record a new one.', fields: [
        { name: 'code', required: true, label: 'Code' },
        { name: 'content_type', required: true, label: 'Type' },
        { name: 'name', required: true, label: 'Title (English)' },
        { name: 'name_bn', label: 'Title (Bengali)' },
        { name: 'body_en', type: 'text', label: 'Content (English)' },
        { name: 'body_bn', type: 'text', label: 'Content (Bengali)' },
        { name: 'link_url', label: 'Link' }
      ] },
      { tab: 'placement', title: 'Where and When', fields: [
        { name: 'slot', label: 'Placement Slot' },
        { name: 'audience', required: true, label: 'Audience' },
        { name: 'valid_from', required: true, label: 'Valid From' },
        { name: 'valid_to', label: 'Valid To' }
      ] },
      { tab: 'docs', title: 'Banner Image', fields: [
        { name: 'image', type: 'binary', filename: 'image_filename', label: 'Upload Image' },
        { name: 'image_filename', label: 'File Name' }
      ] },
      { tab: 'audit', title: 'Publication', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'published_by_id', readonly: true, label: 'Published By' },
        { name: 'published_at', readonly: true, label: 'Published At' }
      ] }
    ] },

  'M38-form-collection': { kind: 'model_form', model: 'fix.storefront.collection',
    title: 'Storefront Collection', back: 'M38-collections',
    status: { field: 'state' },
    tabs: [
      { id: 'set', label: '1. Collection', bn: '১. কালেকশন' },
      { id: 'items', label: '2. Items', bn: '২. পণ্য' },
      { id: 'audit', label: '3. Publication', bn: '৩. প্রকাশ' }
    ],
    sections: [
      { tab: 'set', title: 'Merchandising Set', note: 'A cross- or up-sell offers its items on the page and cart line of the item it is shown with. Only items for sale online can be published.', fields: [
        { name: 'code', required: true, label: 'Code' },
        { name: 'collection_type', required: true, label: 'Type' },
        { name: 'name', required: true, label: 'Name (English)' },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'sequence', label: 'Display Order' },
        { name: 'audience', required: true, label: 'Audience' },
        { name: 'valid_from', required: true, label: 'Valid From' },
        { name: 'valid_to', label: 'Valid To' }
      ] },
      { tab: 'items', title: 'What It Holds', fields: [
        { name: 'anchor_product_id', label: 'Shown With (cross- / up-sell)' },
        { name: 'product_ids', label: 'Items' },
        { name: 'category_id', label: 'Rule: Every Item of Category' }
      ] },
      { tab: 'audit', title: 'Publication', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'published_by_id', readonly: true, label: 'Published By' },
        { name: 'published_at', readonly: true, label: 'Published At' }
      ] }
    ] },

  /* An assisted or corporate cart: the staff capture of a customer's order.
   * Prices are the server's; the order is placed through the storefront
   * checkout with every storefront rule (exposure, COD, terms, corporate
   * approval). */
  'M38-form-cart': { kind: 'model_form', model: 'fix.storefront.cart',
    title: 'Assisted Cart', back: 'M38-carts',
    status: { field: 'state' },
    lines: {
      field: 'line_ids',
      title: 'Cart Lines',
      note: 'Pick the item (or the refurbished unit) and the quantity; the price is the catalogue\'s, set by the server.',
      fields: [
        { name: 'product_id', label: 'Item' },
        { name: 'graded_stock_id', label: 'Refurbished Unit' },
        { name: 'quantity', label: 'Qty' },
        { name: 'unit_price', label: 'Unit Price', readonly: true },
        { name: 'subtotal', label: 'Subtotal', readonly: true }
      ]
    },
    tabs: [
      { id: 'customer', label: '1. Customer', bn: '১. গ্রাহক' },
      { id: 'checkout', label: '2. Delivery & Payment', bn: '২. ডেলিভারি ও পেমেন্ট' },
      { id: 'terms', label: '3. Terms Acceptance', bn: '৩. শর্ত গ্রহণ' },
      { id: 'corporate', label: '4. Corporate Order', bn: '৪. কর্পোরেট অর্ডার' },
      { id: 'audit', label: '5. Captured', bn: '৫. রেকর্ড' }
    ],
    sections: [
      { tab: 'customer', title: 'Customer and Cart', fields: [
        { name: 'name', readonly: true, label: 'Cart (auto)' },
        { name: 'customer_id', required: true, label: 'Customer' },
        { name: 'channel', readonly: true, label: 'Channel' },
        { name: 'total', readonly: true, label: 'Total (BDT)' }
      ] },
      { tab: 'checkout', title: 'Checkout', note: 'Placed with "Place Order" on the cart list. Cash on delivery is offered only within the active COD rule; stock only within its exposure policy.', fields: [
        { name: 'delivery_address', type: 'text', label: 'Delivery Address (blank: the customer\'s address)' },
        { name: 'delivery_method', label: 'Delivery Mode' },
        { name: 'slot_id', label: 'Delivery / Pickup Slot' },
        { name: 'payment_method', label: 'Payment Method' }
      ] },
      { tab: 'terms', title: 'Item Terms (refurbished condition, warranty)', note: 'A cart with a refurbished unit is placed only after the customer\'s acceptance is recorded ("Record Terms Acceptance"). An OTP, signed form or recorded call carries its reference.', fields: [
        { name: 'terms_method', label: 'How the Customer Accepted' },
        { name: 'terms_reference', label: 'Reference (OTP / form / call)' },
        { name: 'terms_accepted_at', readonly: true, label: 'Terms Recorded At' },
        { name: 'terms_accepted_by_id', readonly: true, label: 'Recorded By' }
      ] },
      { tab: 'corporate', title: 'Corporate Order (P04)', note: 'For a corporate client: its active account, its PO reference, and - above the account\'s threshold - the approval of one of its own approvers ("Record Client Approval"). Approved lines are fixed.', fields: [
        { name: 'corporate_account_id', label: 'Corporate Account' },
        { name: 'po_reference', label: 'Client PO Reference' },
        { name: 'client_approver_id', label: 'Client Approver' },
        { name: 'client_approval_ref', label: 'Client Approval Reference' },
        { name: 'client_approved_at', readonly: true, label: 'Client Approval Recorded At' }
      ] },
      { tab: 'audit', title: 'Captured', fields: [
        { name: 'assisted_by_id', readonly: true, label: 'Captured By' },
        { name: 'order_id', readonly: true, label: 'Order Placed' },
        { name: 'create_date', readonly: true, label: 'Opened On' }
      ] }
    ] },

  'M38-form-cod-rule': { kind: 'model_form', model: 'fix.storefront.cod.rule',
    title: 'COD Rule', back: 'M38-cod-rules',
    status: { field: 'state' },
    tabs: [
      { id: 'limits', label: '1. Limits', bn: '১. সীমা' },
      { id: 'approval', label: '2. Approval', bn: '২. অনুমোদন' }
    ],
    sections: [
      { tab: 'limits', title: 'Cash-on-Delivery Eligibility', note: 'Checked at every order placement while the rule is active. A new rule replaces the active one when it is approved by a Storefront Manager who did not write it.', fields: [
        { name: 'name', required: true, label: 'Rule Name' },
        { name: 'max_order_value', required: true, label: 'Largest COD Order (BDT)' },
        { name: 'history_value', label: 'Delivery History Needed Above (BDT)' },
        { name: 'min_delivered_orders', label: 'Delivered Orders Needed' },
        { name: 'max_open_cod_orders', label: 'Open COD Orders Allowed (0 = no limit)' }
      ] },
      { tab: 'approval', title: 'Approval', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'approved_by_id', readonly: true, label: 'Approved By' },
        { name: 'approved_at', readonly: true, label: 'Approved At' }
      ] }
    ] },

  'M38-form-order-change': { kind: 'model_form', model: 'fix.storefront.order.change',
    title: 'Order Change', newLabel: 'Request Order Change', back: 'M38-order-changes',
    status: { field: 'state' },
    tabs: [
      { id: 'change', label: '1. Change', bn: '১. পরিবর্তন' },
      { id: 'decision', label: '2. Decision', bn: '২. সিদ্ধান্ত' }
    ],
    sections: [
      { tab: 'change', title: 'What the Customer Asks to Change', note: 'Accepted until dispatch (the delivery mode only before payment). Another operator applies it.', fields: [
        { name: 'name', readonly: true, label: 'Reference (auto)' },
        { name: 'order_id', required: true, label: 'Online Order' },
        { name: 'change_type', required: true, label: 'Change' },
        { name: 'new_address', type: 'text', label: 'New Address' },
        { name: 'new_slot_id', label: 'New Slot' },
        { name: 'new_method', label: 'New Delivery Mode' },
        { name: 'reason', type: 'text', required: true, label: 'Customer\'s Reason' }
      ] },
      { tab: 'decision', title: 'Decision', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'decided_by_id', readonly: true, label: 'Decided By' },
        { name: 'decided_at', readonly: true, label: 'Decided At' },
        { name: 'refusal_reason', readonly: true, label: 'Refusal Reason' }
      ] }
    ] },

  'M38-form-exposure': { kind: 'model_form', model: 'fix.stock.exposure.policy',
    title: 'Stock Exposure Policy', back: 'M38-exposure',
    status: { field: 'state' },
    tabs: [
      { id: 'scope', label: '1. Scope', bn: '১. পরিধি' },
      { id: 'buffer', label: '2. Locations & Buffer', bn: '২. লোকেশন ও বাফার' },
      { id: 'approval', label: '3. Approval', bn: '৩. অনুমোদন' }
    ],
    sections: [
      { tab: 'scope', title: 'What It Covers', note: 'One item, or one category (and its sub-categories). An item\'s own policy wins over its category\'s. "Sold Online" off withdraws it from online sale.', fields: [
        { name: 'name', required: true, label: 'Policy Name' },
        { name: 'product_id', label: 'Item' },
        { name: 'category_id', label: 'Category' },
        { name: 'enabled', label: 'Sold Online' }
      ] },
      { tab: 'buffer', title: 'Where From, What Is Kept Back', note: 'Online sale is limited to the stock on hand in these locations less the buffer (the larger of the units and the share).', fields: [
        { name: 'location_ids', label: 'Locations Sold From (empty: all internal)' },
        { name: 'buffer_qty', label: 'Buffer (units)' },
        { name: 'buffer_pct', label: 'Buffer (%)' },
        { name: 'max_promise_days', label: 'Longest Promise (days)' }
      ] },
      { tab: 'approval', title: 'Approval', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'approved_by_id', readonly: true, label: 'Approved By' },
        { name: 'approved_at', readonly: true, label: 'Approved At' }
      ] }
    ] },

  'M38-form-return-policy': { kind: 'model_form', model: 'fix.storefront.return.policy',
    title: 'Return Policy', back: 'M38-return-policies',
    status: { field: 'state' },
    tabs: [
      { id: 'policy', label: '1. Policy', bn: '১. নীতি' },
      { id: 'approval', label: '2. Approval', bn: '২. অনুমোদন' }
    ],
    sections: [
      { tab: 'policy', title: 'Return Window and Restocking', note: 'A return is accepted within the longest window of the policies its order\'s items fall under; without an active policy the configured default applies.', fields: [
        { name: 'name', required: true, label: 'Policy Name' },
        { name: 'category_id', label: 'Category (empty: the default)' },
        { name: 'window_days', required: true, label: 'Return Window (days)' },
        { name: 'restocking_fee_pct', label: 'Change-of-mind Restocking Fee (%)' }
      ] },
      { tab: 'approval', title: 'Approval', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'approved_by_id', readonly: true, label: 'Approved By' },
        { name: 'approved_at', readonly: true, label: 'Approved At' }
      ] }
    ] },

  'M38-form-corporate-account': { kind: 'model_form', model: 'fix.storefront.corporate.account',
    title: 'Corporate Commerce Account', back: 'M38-corporate-accounts',
    status: { field: 'state' },
    tabs: [
      { id: 'client', label: '1. Client', bn: '১. ক্লায়েন্ট' },
      { id: 'approval_chain', label: '2. Approval Chain', bn: '২. অনুমোদন শৃঙ্খল' },
      { id: 'catalogue', label: '3. Agreed Catalogue', bn: '৩. সম্মত ক্যাটালগ' },
      { id: 'approval', label: '4. Activation', bn: '৪. সক্রিয়করণ' }
    ],
    sections: [
      { tab: 'client', title: 'Corporate Client', fields: [
        { name: 'partner_id', required: true, label: 'Corporate Client' },
        { name: 'po_required', label: 'PO Reference Required' }
      ] },
      { tab: 'approval_chain', title: 'The Client\'s Own Approvers', note: 'Orders above the threshold (0: every order) are placed only after one of these people - the client\'s own staff - approves them.', fields: [
        { name: 'approver_ids', label: 'Client Approvers' },
        { name: 'approval_threshold', label: 'Client Approval Above (BDT)' }
      ] },
      { tab: 'catalogue', title: 'What the Client May Order', fields: [
        { name: 'category_ids', label: 'Agreed Categories (empty: all)' }
      ] },
      { tab: 'approval', title: 'Activation', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'approved_by_id', readonly: true, label: 'Approved By' },
        { name: 'approved_at', readonly: true, label: 'Approved At' }
      ] }
    ] },

  'M38-form-recovery': { kind: 'model_form', model: 'fix.storefront.recovery.attempt',
    title: 'Cart Recovery Contact', newLabel: 'Record Recovery Contact', back: 'M38-recovery-attempts',
    tabs: [
      { id: 'contact', label: '1. Contact', bn: '১. যোগাযোগ' },
      { id: 'result', label: '2. Result', bn: '২. ফলাফল' }
    ],
    sections: [
      { tab: 'contact', title: 'Who Was Contacted, How', note: 'A log entry: only an open, unordered cart is followed up, and the contact stays as recorded.', fields: [
        { name: 'cart_id', required: true, label: 'Abandoned Cart' },
        { name: 'customer_id', readonly: true, label: 'Customer' },
        { name: 'cart_total', readonly: true, label: 'Cart Value' },
        { name: 'channel', required: true, label: 'Channel' },
        { name: 'outcome', required: true, label: 'Outcome' },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'result', title: 'Result', fields: [
        { name: 'contacted_by_id', readonly: true, label: 'Contacted By' },
        { name: 'contacted_at', readonly: true, label: 'Contacted At' },
        { name: 'converted', readonly: true, label: 'Ordered After Contact' }
      ] }
    ] },

  'M38-form-service-booking': { kind: 'model_form', model: 'fix.storefront.service.booking',
    title: 'Service Booking', back: 'M38-service-bookings',
    status: { field: 'state' },
    tabs: [
      { id: 'booking', label: '1. Booking', bn: '১. বুকিং' },
      { id: 'docs', label: '2. Fault Photo', bn: '২. ত্রুটির ছবি' },
      { id: 'outcome', label: '3. Service Order', bn: '৩. সার্ভিস অর্ডার' }
    ],
    sections: [
      { tab: 'booking', title: 'Repair Appointment', note: 'The device must be registered to the customer and the slot a service slot with room. Confirming raises the M01 service order, which then owns the repair.', fields: [
        { name: 'name', readonly: true, label: 'Reference (auto)' },
        { name: 'customer_id', required: true, label: 'Customer' },
        { name: 'device_id', required: true, label: 'Device' },
        { name: 'branch_id', required: true, label: 'Branch' },
        { name: 'slot_id', required: true, label: 'Appointment Slot' },
        { name: 'channel', required: true, label: 'Booked Through' },
        { name: 'fault_description', type: 'text', required: true, label: 'Fault Description' }
      ] },
      { tab: 'docs', title: 'Fault Photograph', fields: [
        { name: 'photo', type: 'binary', filename: 'photo_filename', label: 'Upload Photo' },
        { name: 'photo_filename', label: 'File Name' }
      ] },
      { tab: 'outcome', title: 'Service Order', fields: [
        { name: 'state', readonly: true, label: 'Status' },
        { name: 'service_order_id', readonly: true, label: 'M01 Service Order' },
        { name: 'confirmed_by_id', readonly: true, label: 'Confirmed By' },
        { name: 'confirmed_at', readonly: true, label: 'Confirmed At' },
        { name: 'cancel_reason', readonly: true, label: 'Cancel Reason' }
      ] }
    ] }
};

export const REPORT_ROUTES = {
  'M38:Funnel & Conversion': 'M38-rpt-funnel',
  'M38:Payment Method Mix': 'M38-rpt-pay',
  'M38:Refurb GMV by Grade': 'M38-rpt-refurb',
  'M38:Delivery Performance': 'M38-rpt-delivery',
  'M38:RMA & Returns Report': 'M38-rpt-rma',
  'M38:Abandonment Recovery Rate': 'M38-rpt-recovery'
};

export const FORM_MODELS = {
  'M38:Storefront Content': 'fix.storefront.content',
  'M38:Storefront Collection': 'fix.storefront.collection',
  'M38:Assisted Cart': 'fix.storefront.cart',
  'M38:Corporate Order': 'fix.storefront.cart',
  'M38:COD Rule': 'fix.storefront.cod.rule',
  'M38:Order Change': 'fix.storefront.order.change',
  'M38:Stock Exposure Policy': 'fix.stock.exposure.policy',
  'M38:Return Policy': 'fix.storefront.return.policy',
  'M38:Corporate Commerce Account': 'fix.storefront.corporate.account',
  'M38:Cart Recovery Contact': 'fix.storefront.recovery.attempt',
  'M38:Service Booking': 'fix.storefront.service.booking',
  'M38:Online Order': 'fix.storefront.order',
  'M38:RMA Request': 'fix.storefront.rma',
  'M38:Storefront Slot': 'fix.storefront.slot',
  'M38:Delivery Slot': 'fix.storefront.slot'
};

export const FORM_CHIPS = {
  'M38:Graded Stock': 'M38-form-gstock',
  // M11 owns fix.promotion; the storefront lists it but edits it there,
  // so the two surfaces cannot drift apart (A04 audit, 2026-10-31).
  'M38:Promotion': 'M11-form-promo',
  'M38:Online Order': 'M38-form-order',
  'M38:RMA Request': 'M38-form-rma',
  'M38:Storefront Slot': 'M38-form-delivery-slot',
  'M38:Delivery Slot': 'M38-form-delivery-slot',
  'M38:Storefront Content': 'M38-form-content',
  'M38:Storefront Collection': 'M38-form-collection',
  'M38:Assisted Cart': 'M38-form-cart',
  'M38:Corporate Order': 'M38-form-cart',
  'M38:COD Rule': 'M38-form-cod-rule',
  'M38:Order Change': 'M38-form-order-change',
  'M38:Stock Exposure Policy': 'M38-form-exposure',
  'M38:Return Policy': 'M38-form-return-policy',
  'M38:Corporate Commerce Account': 'M38-form-corporate-account',
  'M38:Cart Recovery Contact': 'M38-form-recovery',
  'M38:Service Booking': 'M38-form-service-booking',
  'M38:__by_model__': {
    'fix.storefront.content': 'M38-form-content',
    'fix.storefront.collection': 'M38-form-collection',
    'fix.storefront.cart': 'M38-form-cart',
    'fix.storefront.cod.rule': 'M38-form-cod-rule',
    'fix.storefront.order.change': 'M38-form-order-change',
    'fix.stock.exposure.policy': 'M38-form-exposure',
    'fix.storefront.return.policy': 'M38-form-return-policy',
    'fix.storefront.corporate.account': 'M38-form-corporate-account',
    'fix.storefront.recovery.attempt': 'M38-form-recovery',
    'fix.storefront.service.booking': 'M38-form-service-booking',
    'fix.storefront.return': 'M38-form-storefront-return',
    'fix.graded.stock': 'M38-form-gstock',
    'fix.promotion': 'M11-form-promo',
    'fix.storefront.order': 'M38-form-order',
    'fix.storefront.rma': 'M38-form-rma',
    'fix.storefront.slot': 'M38-form-delivery-slot'
  },
  'M38:__by_screen__': {
    'M38-content': 'M38-form-content',
    'M38-collections': 'M38-form-collection',
    'M38-carts': 'M38-form-cart',
    'M38-corporate-orders': 'M38-form-cart',
    'M38-cod-rules': 'M38-form-cod-rule',
    'M38-order-changes': 'M38-form-order-change',
    'M38-exposure': 'M38-form-exposure',
    'M38-return-policies': 'M38-form-return-policy',
    'M38-corporate-accounts': 'M38-form-corporate-account',
    'M38-recovery-attempts': 'M38-form-recovery',
    'M38-service-bookings': 'M38-form-service-booking',
    'M38-storefront-return': 'M38-form-storefront-return',
    'M38-stock': 'M38-form-gstock',
    'M38-promos': 'M11-form-promo',
    'M38-orders': 'M38-form-order',
    'M38-returns': 'M38-form-rma',
    'M38-delivery': 'M38-form-delivery-slot',
    'M38-slots': 'M38-form-delivery-slot'
  }
};

/* No "+ New Online Order": orders come from storefront checkout (see M38-form-order);
 * staff place them through an assisted cart (M38-form-cart). */
export const CREATE = {};
