/** @odoo-module **/
/* A04 · Commercial & Revenue — M38 E-Commerce Storefront (v2 rebuild).
 * A04 audit (2026-11-04): workflow fields are read-only; the lifecycle runs
 * from the list actions.
 * Registry-faithful: 4 groups / 11 screens / 6 reports / 4 forms / freg 92.
 * Carts, storefront orders and graded stock are real; RMA and slots are new.
 * Payment mix comes from the order's payment rail; refurb GMV by grade is a
 * declared gap (no order↔grade link). */

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
      { id: 'M38-storefront', en: 'Storefront Preview', bn: 'স্টোরফ্রন্ট', t: 'r' },
      { id: 'M38-merch', en: 'Merchandising', bn: 'মার্চেন্ডাইজিং', t: 'r' },
      { id: 'M38-compat', en: 'Compatibility Filters', bn: 'কম্প্যাটিবিলিটি', t: 'r' }
    ]},
    { en: 'Cart & Checkout', screens: [
      { id: 'M38-carts', en: 'Carts & Abandonment', bn: 'কার্ট', t: 'g' },
      { id: 'M38-checkout', en: 'Checkout & Payment Orchestration', bn: 'চেকআউট', t: 'r' },
      { id: 'M38-delivery', en: 'Delivery Options', bn: 'ডেলিভারি', t: 'r' },
      { id: 'M38-slots', en: 'Delivery Slots', bn: 'ডেলিভারি স্লট', t: 'g' }
    ]},
    { en: 'Orders', screens: [
      { id: 'M38-orders', en: 'Online Orders', bn: 'অনলাইন অর্ডার', t: 'g' },
      { id: 'M38-returns', en: 'Returns & RMA', bn: 'রিটার্ন', t: 'g' },
      { id: 'M38-stock', en: 'Stock Exposure Policy', bn: 'স্টক এক্সপোজার', t: 'g' }
    ]},
    { en: 'Commerce Marketing', screens: [
      { id: 'M38-promos', en: 'Checkout Promotions (from M11)', bn: 'প্রমোশন (M11)', t: 'g' },
      { id: 'M38-recovery', en: 'Abandoned-Cart Recovery', bn: 'কার্ট রিকভারি', t: 'r' }
    ]}
  ],
  reports: ['Funnel & Conversion', 'Payment Method Mix', 'Refurb GMV by Grade', 'Delivery Performance', 'RMA & Returns Report', 'Abandonment Recovery Rate'],
  forms: ['Online Order', 'RMA Request', 'Storefront Slot', 'Delivery Slot'],
  cross: ['M20 AR', 'M37 Catalogue', 'M11 Pricing', 'M31 Refurb'],
  freg: { src: 92, sub: [
    ['1', 'Storefront & Browse', 12, { model: 'fix.storefront.cart', cols: ['name', 'customer_id', 'state', 'total', 'create_date'], screens: ['M38-storefront', 'M38-rpt-funnel', 'M38-carts'], reports: ['Funnel & Conversion'], forms: [] }],
    ['2', 'Merchandising', 7, { model: 'fix.graded.stock', cols: ['name', 'device_id', 'grade_id', 'resale_price', 'state'], screens: ['M38-merch', 'M38-compat', 'M38-stock'], reports: ['Refurb GMV by Grade'], forms: [] }],
    ['3', 'Cart', 9, { model: 'fix.storefront.cart', cols: ['name', 'state', 'customer_id', 'total', 'order_id'], screens: ['M38-carts'], reports: ['Abandonment Recovery Rate'], forms: [] }],
    ['4', 'Checkout & Payments', 14, { model: 'fix.storefront.order', cols: ['name', 'customer_id', 'payment_rail', 'total_amount', 'state'], screens: ['M38-checkout', 'M38-rpt-pay', 'M38-orders'], reports: ['Payment Method Mix', 'Funnel & Conversion'], forms: [], create: false }],
    ['5', 'Online Orders', 9, { model: 'fix.storefront.order', cols: ['state'], screens: ['M38-orders'], reports: ['Payment Method Mix'], forms: ['Online Order'] }],
    ['6', 'Stock Exposure', 6, { model: 'fix.graded.stock', cols: ['name', 'state', 'device_id', 'grade_id', 'location_id'], screens: ['M38-stock', 'M38-rpt-refurb'], reports: ['Refurb GMV by Grade'], forms: [] }],
    ['7', 'Returns & RMA', 9, { model: 'fix.storefront.rma', cols: ['name', 'state', 'customer_id', 'order_id', 'reason', 'requested_on', 'refund_amount'], screens: ['M38-returns', 'M38-rpt-rma'], reports: ['RMA & Returns Report'], forms: ['RMA Request'] }],
    ['8', 'B2B Commerce', 11, { model: 'fix.storefront.return', cols: ['name', 'state', 'customer_id', 'order_id', 'reason', 'refund_amount'], screens: ['M38-storefront-return'], reports: ['RMA & Returns Report'], forms: [] }],
    ['9', 'Recovery & Analytics', 9, { model: 'fix.storefront.cart', cols: ['name', 'customer_id', 'state', 'total', 'create_date'], screens: ['M38-recovery', 'M38-rpt-recovery', 'M38-carts'], reports: ['Abandonment Recovery Rate'], forms: [], domain: [['state', 'in', ['open', 'checkout']]] }],
    ['10', 'Service Booking Commerce', 6, { model: 'fix.storefront.slot', cols: ['name', 'slot_date', 'capacity', 'booked', 'state'], screens: ['M38-delivery', 'M38-rpt-delivery'], reports: ['Delivery Performance'], forms: ['Storefront Slot', 'Delivery Slot'] }]
  ] }
};

export const SCREENS = {
  'M38-storefront': { kind: 'table_report', module: 'M38', report: 'funnel_conversion', title: 'Storefront Preview', period: false },
  'M38-merch': { kind: 'table_report', module: 'M38', report: 'merchandising', title: 'Merchandising', period: false },
  'M38-compat': { kind: 'table_report', module: 'M38', report: 'stock_availability', title: 'Compatibility Filters', period: false },
  'M38-carts': { kind: 'model_list', create: false, model: 'fix.storefront.cart', stateField: 'state',
    cols: ['name', 'customer_id', 'state', 'total', 'order_id'],
    empty: 'No cart yet. Carts are opened by customers on the online storefront; they are not typed in here.' },
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
  'M38-stock': { kind: 'model_list', model: 'fix.graded.stock', stateField: 'state',
    cols: ['device_id', 'grade_id', 'acquisition_cost', 'state'] },
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
  'M38-form-gstock': { kind: 'model_form', model: 'fix.graded.stock',
    title: 'Graded Stock Item', back: 'M38-stock',
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
        { name: 'tradein_id', label: 'Originating Trade-In ID' },
        { name: 'tradein_ref', label: 'Originating Trade-In Ref' },
        { name: 'inventory_valuation', label: 'Inventory Valuation', readonly: true },
        { name: 'state', label: 'Inventory Status (reserved and sold by orders)', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'acquisition_cost', label: 'Acquisition Cost (Trade-In)', required: true },
        { name: 'refurbishment_cost', label: 'Refurbishment Cost' },
        { name: 'resale_price', label: 'Target Resale Price', required: true },
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
  'M38:__by_model__': {
    'fix.storefront.return': 'M38-form-storefront-return',
    'fix.graded.stock': 'M38-form-gstock',
    'fix.promotion': 'M11-form-promo',
    'fix.storefront.order': 'M38-form-order',
    'fix.storefront.rma': 'M38-form-rma',
    'fix.storefront.slot': 'M38-form-delivery-slot'
  },
  'M38:__by_screen__': {
    'M38-storefront-return': 'M38-form-storefront-return',
    'M38-stock': 'M38-form-gstock',
    'M38-promos': 'M11-form-promo',
    'M38-orders': 'M38-form-order',
    'M38-returns': 'M38-form-rma',
    'M38-delivery': 'M38-form-delivery-slot',
    'M38-slots': 'M38-form-delivery-slot'
  }
};

/* No "+ New Online Order": orders come from storefront checkout (see M38-form-order). */
export const CREATE = {};
