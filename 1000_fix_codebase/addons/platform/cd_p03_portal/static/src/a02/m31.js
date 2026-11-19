/** @odoo-module **/
/* A02 · Service Operations — M31 Workshop & Depot Repair.
 * This fragment REPLACES the base-file M31 block, which described an
 * on-site appointments module — wrong content for a bench-repair module
 * (registry-drift measured 2026-10-26). The structure below is the
 * CANONICAL registry M31 (contracts/nav/registry.json): 4 groups, 12
 * screens, 6 KPIs, 6 reports, 76 freg functions in 9 subs.
 *
 * Backend: controllers/a02/m31.py (SURFACES, kpis, 6 REPORTS) over the
 * cd_workshop models — the 11-state job machine, L1/L2/L3 bench routing,
 * burn-in gates and the bench auto-allocation engine. */

export const MODULE = {
  area: 'A02', code: 'M31', en: 'Workshop & Depot Repair', title: 'M31 · Workshop & Depot Repair',
  bn: 'ওয়ার্কশপ মেরামত', icon: '🔧',
  desc: 'Bench repair L1/L2/L3, serial genealogy, burn-in testing, workshop costing and knowledge capture.',
  kpis: [
    { l: 'On Bench', m: 'on_bench' },
    { l: 'First-Pass Yield', m: 'first_pass_yield' },
    { l: 'L3 Queue > 48h', m: 'l3_queue_48h' },
    { l: 'Avg Bench Days', m: 'avg_bench_days' },
    { l: 'Parts Fitment', m: 'parts_fitment' },
    { l: 'Internal Rework', m: 'internal_rework' }
  ],
  groups: [
    { en: 'Repair Orders', screens: [
      { id: 'M31-orders', en: 'Repair Orders', bn: 'রিপেয়ার অর্ডার', t: 'g' },
      { id: 'M31-record', en: 'Repair Order Record', bn: 'রিপেয়ার অর্ডার নথি', t: 'g' },
      { id: 'M31-transfer', en: 'Bench Utilisation by Workshop', bn: 'ওয়ার্কশপভিত্তিক বেঞ্চ ব্যবহার', t: 'r' }
    ]},
    { en: 'Bench Board', screens: [
      { id: 'M31-benches', en: 'Bench & WIP Board', bn: 'বেঞ্চ ও ডাব্লিউআইপি বোর্ড', t: 'd' },
      { id: 'M31-benchmaster', en: 'Bench Master (Capacity)', bn: 'বেঞ্চ মাস্টার', t: 'g' },
      { id: 'M31-levels', en: 'L1/L2/L3 Classification', bn: 'এল১/এল২/এল৩ শ্রেণি', t: 'r' }
    ]},
    { en: 'Execution', screens: [
      { id: 'M31-diag', en: 'Component Diagnosis', bn: 'কম্পোনেন্ট ডায়াগনোসিস', t: 'g' },
      { id: 'M31-parts', en: 'Parts Consumption', bn: 'পার্টস ব্যবহার', t: 'g' },
      { id: 'M31-testing', en: 'Test Protocols & Burn-In', bn: 'টেস্ট ও বার্ন-ইন', t: 'g' }
    ]},
    { en: 'Costing & Knowledge', screens: [
      { id: 'M31-costing', en: 'Repair Costing', bn: 'মেরামত ব্যয়', t: 'r' },
      { id: 'M31-throughput', en: 'Throughput Analytics', bn: 'থ্রুপুট বিশ্লেষণ', t: 'r' },
      { id: 'M31-methods', en: 'Repair-Method Capture', bn: 'মেরামত পদ্ধতি', t: 'r' }
    ]}
  ],
  reports: ['Bench Utilisation by Workshop', 'Repair Cycle Time by Level', 'Internal Rework Loop Analysis', 'Workshop Cost per Repair', 'Parts Genealogy Trace', 'Burn-In Failure Report'],
  /* 'Workshop Transfer' was the workshop FACILITY master form under another
   * name; a transfer is captured on the Job Routing form (new workshop).
   * 2026-11-12: every sub-module page captures its own data (it was 1 of 9). */
  /* 2026-11-14 audit: "Bench Allocation" and "Test Protocol Result" are the
   * registry's own form names. They had become a bench-master form and a
   * file upload, so allocating a job to a bench and recording a measured
   * test result had no capture anywhere. Each now captures what its name
   * says; the bench master and the evidence upload keep forms of their own. */
  forms: ['Receive Device into Workshop', 'Repair Order', 'Workshop Facility', 'Bench Master', 'Bench Allocation',
    'Job Routing', 'Bench Diagnosis', 'Part Fitment', 'Test Protocol', 'Test Protocol Result', 'Test Evidence',
    'Labour & Cost',
    /* capture pass 2 (19 Nov 2026) */
    'Move Device to Location', 'Workshop Location', 'Burn-In Station', 'ESD Bench Check', 'Shift Close',
    'Escalation', 'Teardown Record', 'Instrument Use', 'Knowledge Capture', 'Consumable Usage', 'Burn-In Run',
    'Workshop Transfer', 'Work Clock'],
  cross: ['M01 device release', 'M15 parts consumption', 'M61 knowledge capture', 'M45 test equipment', 'M22 skill routing'],
  freg: {
    src: 76,
    sub: [
      /* A repair order is never typed from scratch (BRU-WSR-01): it is the
       * service order's hand-over, so the page's button picks the booked-in
       * order and runs that hand-over (FR-WSR-001/004). */
      ['1', 'Repair Order Creation', 8, { model: 'fix.workshop.job', cols: ['name', 'order_reference', 'workshop_id', 'priority', 'intake_date'], screens: ['M31-orders', 'M31-record', 'M31-custody'], reports: ['Repair Cycle Time by Level'], forms: ['Receive Device into Workshop', 'Repair Order', 'Move Device to Location'], create: 'M31-form-receive' }],
      /* the two masters (FR-WSR-009/010): the button adds a workshop, the
       * Bench Master chip a bench in it */
      ['2', 'Workshop & Bench Master', 9, { model: 'fix.workshop', cols: ['code', 'name', 'workshop_type', 'branch_id', 'bench_count'], screens: ['M31-benchmaster', 'M31-locations', 'M31-burnin-stations', 'M31-esd-checks'], reports: ['Bench Utilisation by Workshop'], forms: ['Workshop Facility', 'Bench Master', 'Workshop Location', 'Burn-In Station', 'ESD Bench Check'] }],
      /* FR-WSR-011/015: the button allocates a waiting job to a bench and a
       * technician, or hands it over; it used to add a new bench */
      ['3', 'Bench Allocation & Queue', 10, { model: 'fix.workshop.bench', cols: ['code', 'name', 'state', 'current_job_count', 'technician_id'], screens: ['M31-benches', 'M31-handovers', 'M31-shift-closes', 'M31-custody'], reports: ['Bench Utilisation by Workshop'], forms: ['Bench Allocation', 'Shift Close', 'Move Device to Location'], create: 'M31-form-allocate' }],
      /* 2026-11-19 pass 2: each page also captures the spec's own records
       * (locations, ESD, hand-over, shift close, escalation, teardown,
       * instruments, consumables, burn-in runs, transfers, clock, cost sheet).
       * Page 8's button is now the transfer itself (BRU-WSR-14). */
      /* routing, diagnosis, rework and costing act on a job already in the
       * workshop: each page picks the job, then captures its own part of it */
      ['4', 'Repair-Level Routing', 7, { model: 'fix.workshop.job', cols: ['name', 'repair_level', 'workshop_id', 'bench_id', 'state'], screens: ['M31-levels', 'M31-record', 'M31-escalations'], reports: ['Repair Cycle Time by Level'], forms: ['Job Routing', 'Escalation'], create: 'M31-form-routing' }],
      ['5', 'Diagnosis & Execution', 13, { model: 'fix.workshop.job', cols: ['name', 'device_serial', 'technician_id', 'bench_id', 'state'], screens: ['M31-diag', 'M31-methods', 'M31-teardowns', 'M31-instrument-uses'], reports: ['Internal Rework Loop Analysis'], forms: ['Bench Diagnosis', 'Teardown Record', 'Instrument Use', 'Knowledge Capture'], create: 'M31-form-diagnosis', domain: [['state', 'in', ['diagnostic', 'waiting_parts', 'in_repair']]] }],
      ['6', 'Parts Consumption & Genealogy', 8, { model: 'fix.workshop.part.line', cols: ['job_id', 'part_number', 'lot_serial_number', 'quantity', 'source_origin'], screens: ['M31-parts', 'M31-consumables'], reports: ['Parts Genealogy Trace'], forms: ['Part Fitment', 'Consumable Usage'] }],
      /* FR-WSR-031/032/039: the page lists the recorded test results; the
       * button records one against a protocol test, judged by its limits.
       * The protocol library and the evidence upload are its chips. */
      ['7', 'Testing & Burn-In', 8, { model: 'fix.workshop.test.result', cols: ['job_id', 'step_id', 'measured_value', 'unit', 'passed', 'tested_by_id', 'tested_at'], screens: ['M31-testing', 'M31-testresults', 'M31-protocols', 'M31-burnin-sessions'], reports: ['Burn-In Failure Report'], forms: ['Test Protocol Result', 'Test Protocol', 'Test Evidence', 'Burn-In Run'], create: 'M31-form-testresult' }],
      ['8', 'Rework & Transfers', 6, { model: 'fix.workshop.job', cols: ['name', 'rework_of_id', 'rework_count', 'workshop_id', 'state'], screens: ['M31-transfers', 'M31-reworks', 'M31-transfer', 'M31-record'], reports: ['Internal Rework Loop Analysis', 'Bench Utilisation by Workshop'], forms: ['Workshop Transfer', 'Job Routing'], create: 'M31-form-transfer', domain: [['is_rework', '=', true]] }],
      ['9', 'Repair Costing', 7, { model: 'fix.workshop.job', cols: ['name', 'parts_total', 'labour_cost', 'total_repair_cost', 'labor_efficiency_pct'], screens: ['M31-costing', 'M31-throughput', 'M31-timelogs', 'M31-cost-jobs', 'M31-costlines'], reports: ['Workshop Cost per Repair', 'Repair Cycle Time by Level'], forms: ['Labour & Cost', 'Work Clock'], create: 'M31-form-labour' }]
    ]
  }
};


const JOB_FLOW = [
  { m: 'action_intake', l: 'Intake' },
  { m: 'action_diagnostic', l: 'Start Diagnosis' },
  { m: 'action_auto_assign_bench', l: 'Auto-Assign Bench' },
  { m: 'action_wait_parts', l: 'Wait for Parts' },
  { m: 'action_start_repair', l: 'Start Repair (Order Approved)' },
  { m: 'action_submit_qc', l: 'Submit to QC (L1)' },
  { m: 'action_start_burn_in', l: 'Start Burn-In' },
  { m: 'action_log_thermal_crash', l: 'Log Thermal Crash', ask: 'What happened (crash, throttle, reboot)?', kwarg: 'note' },
  { m: 'action_pass_burn_in', l: 'Pass Burn-In' },
  { m: 'action_fail_burn_in', l: 'Fail Burn-In (Back to Bench)', ask: 'Why did the burn-in fail?', kwarg: 'reason' },
  { m: 'action_pass_qc', l: 'Pass QC (Inspector)', ask: 'QC inspection findings', kwarg: 'notes' },
  { m: 'action_fail_qc', l: 'Fail QC (NCR + Rework)', ask: 'Why did the job fail QC?', kwarg: 'reason' },
  { m: 'action_deliver', l: 'Release / Deliver' },
  { m: 'action_cancel', l: 'Cancel Job' }
];
/* A02 audit B1: the waiver and the BER write-off are routed M63 approvals,
 * decided from the approver's inbox (M63 workspace), never pressed here. */
const JOB_EXCEPTIONS = [
  { m: 'action_request_certification_waiver', l: 'Request Certification Waiver (to Supervisor)', ask: 'Waiver justification', kwarg: 'reason' },
  { m: 'action_propose_ber', l: 'Propose BER / Scrap (evidence attached)', ask: 'BER reason and the evidence seen', kwarg: 'reason' },
  { m: 'action_confirm_ber', l: 'Confirm BER & Route Write-Off (Second Technician)' },
  { m: 'action_recall_approval', l: 'Recall BER Approval Request' }
];

/* In-workspace data screens: model_list over the whitelisted cd_workshop
 * models; table_report over the module REPORTS. Workflow buttons call the
 * named job actions only (A02 audit M31-11): the job's state, QC, burn-in
 * and waiver fields change nowhere else. */
export const SCREENS = {
  'M31-orders': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'workshop_id', 'bench_id', 'technician_id', 'repair_level', 'priority', 'state'],
    stateField: 'state',
    actions: [...JOB_FLOW, ...JOB_EXCEPTIONS] },
  'M31-record': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'workshop_id', 'bench_id', 'technician_id', 'repair_level', 'state',
      'burn_in_passed', 'qc_passed', 'is_rework', 'rework_count', 'parts_total', 'labour_cost', 'total_repair_cost',
      'intake_date', 'completed_at'],
    stateField: 'state',
    /* A02 ERP audit X-17: the job card / repair report */
    actions: [...JOB_FLOW, ...JOB_EXCEPTIONS, { m: 'p03_print_document', print: 'a4', l: 'Print Job Card' }] },
  'M31-transfer': { kind: 'table_report', module: 'M31', report: 'bench_utilisation', period: false },
  'M31-benches': { kind: 'model_list', model: 'fix.workshop.bench',
    cols: ['code', 'name', 'workshop_id', 'repair_level', 'state', 'current_job_count', 'max_concurrent_jobs', 'technician_id', 'is_esd_safe'],
    stateField: 'state',
    actions: [
      { m: 'action_set_maintenance', l: 'Take into Maintenance', ask: 'Reason (calibration, tool fault…)', kwarg: 'reason' },
      { m: 'action_return_to_service', l: 'Return to Service' },
      { m: 'action_set_offline', l: 'Close Bench (Supervisor)', ask: 'Why is the bench closing?', kwarg: 'reason' }
    ] },
  /* the two masters are created here (a workshop manager's right, by ACL):
   * with both lists closed to "+ New", a workshop or bench could only be
   * added outside the workspace, and the M01 hand-over's "create one first"
   * pointed at a page that offered no way to do it */
  'M31-benchmaster': { kind: 'model_list', model: 'fix.workshop',
    cols: ['code', 'name', 'workshop_type', 'branch_id', 'bench_count', 'available_bench_count', 'bench_utilization', 'active_job_count'],
    /* A02 audit M31 step 1: the M31 side of the M01 hand-off */
    actions: [
      { m: 'action_receive_service_order', l: 'Receive Device from M01', ask: 'Service order reference (e.g. SO/2026/00123)', kwarg: 'order_ref' }
    ] },
  'M31-levels': { kind: 'table_report', module: 'M31', report: 'cycle_time', period: false },
  'M31-diag': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'device_serial', 'repair_level', 'priority', 'state', 'technician_id', 'bench_id'],
    domain: [['state', 'in', ['intake', 'diagnostic']]],
    stateField: 'state',
    actions: [
      { m: 'action_diagnostic', l: 'Start Diagnosis' },
      { m: 'action_auto_assign_bench', l: 'Auto-Assign Bench' },
      { m: 'action_wait_parts', l: 'Wait for Parts' },
      { m: 'action_start_repair', l: 'Start Repair (Order Approved)' },
      { m: 'action_request_certification_waiver', l: 'Request Certification Waiver (to Supervisor)', ask: 'Waiver justification', kwarg: 'reason' },
      { m: 'action_propose_ber', l: 'Propose BER / Scrap (evidence attached)', ask: 'BER reason and the evidence seen', kwarg: 'reason' }
    ] },
  /* a part is added to a job here (Part Fitment); reserving and consuming it
   * stay the actions below */
  'M31-parts': { kind: 'model_list', model: 'fix.workshop.part.line',
    cols: ['job_id', 'part_number', 'quantity', 'unit_cost', 'subtotal', 'lot_serial_number', 'reservation_state', 'approval_state', 'consumption_ref'],
    stateField: 'reservation_state',
    actions: [
      { m: 'action_reserve', l: 'Reserve (Stock Move)' },
      { m: 'action_consume_part', l: 'Consume on Bench' },
      { m: 'action_release_reservation', l: 'Release Reservation' },
      { m: 'action_request_approval', l: 'Request Extra-Part Approval (beyond estimate)', ask: 'Why is this part needed beyond the approved estimate?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M31-testing': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'repair_level', 'state', 'burn_in_started_at', 'burn_in_completed_at', 'burn_in_passed', 'qc_passed', 'qc_inspector_id'],
    domain: [['state', 'in', ['burn_in', 'qc_pending', 'qc_failed']]],
    stateField: 'state',
    actions: [
      { m: 'action_log_thermal_crash', l: 'Log Thermal Crash', ask: 'What happened (crash, throttle, reboot)?', kwarg: 'note' },
      { m: 'action_pass_burn_in', l: 'Pass Burn-In' },
      { m: 'action_fail_burn_in', l: 'Fail Burn-In (Back to Bench)', ask: 'Why did the burn-in fail?', kwarg: 'reason' },
      { m: 'action_pass_qc', l: 'Pass QC (Inspector)', ask: 'QC inspection findings', kwarg: 'notes' },
      { m: 'action_fail_qc', l: 'Fail QC (NCR + Rework)', ask: 'Why did the job fail QC?', kwarg: 'reason' },
      { m: 'action_start_repair', l: 'Back on Bench (Rework)' }
    ] },
  'M31-costing': { kind: 'table_report', module: 'M31', report: 'cost_per_repair', period: false },
  /* 2026-11-14: the recorded test results and the protocol library */
  'M31-testresults': { kind: 'model_list', model: 'fix.workshop.test.result', title: 'Test Results',
    cols: ['job_id', 'protocol_id', 'step_id', 'measured_value', 'unit', 'lower_limit', 'upper_limit', 'passed', 'equipment_id', 'tested_by_id', 'tested_at'] },
  'M31-protocols': { kind: 'model_list', model: 'fix.workshop.test.protocol', title: 'Test Protocol Library',
    cols: ['code', 'name', 'device_type', 'repair_level', 'fault_type', 'burn_in_minutes', 'step_count', 'active'] },
  /* M31 sweep audit 2026-11-06 (D17): the genealogy and burn-in packs get
   * their own screens - their tiles previously opened the nearest grids. */
  'M31-rpt-genealogy': { kind: 'table_report', module: 'M31', report: 'parts_genealogy', title: 'Parts Genealogy Trace', period: false },
  'M31-rpt-burnin': { kind: 'table_report', module: 'M31', report: 'burn_in', title: 'Burn-In Failure Report', period: false },
  'M31-throughput': { kind: 'table_report', module: 'M31', report: 'cycle_time', period: false },
  'M31-methods': { kind: 'table_report', module: 'M31', report: 'rework_loops', period: false },

  /* ===== service data-entry forms (registry names) ===== */
  'M31-form-job': {
    kind: 'model_form',
    model: 'fix.workshop.job',
    title: "Repair Order",
    back: 'M31-orders',
    /* BRU-WSR-01: a repair order comes from its service order (the hand-over
     * copies device, customer, fault and book-in, and refuses a draft order
     * or a second live job). A blank form here saved nothing - it lacked the
     * required reported fault - so it opens existing jobs only. */
    create: false,
    pick: 'A repair order starts from its service order: use "Receive Device into Workshop", or open a job from this list.',
    status: { field: 'state', labels: { draft: "Draft", intake: "Intake", diagnostic: "Diagnosis", waiting_parts: "Waiting Parts", in_repair: "In Repair", burn_in: "Burn-In", qc_pending: "QC Pending", qc_failed: "QC Failed", ready: "Ready", delivered: "Delivered", unrepairable: "Unrepairable (BER)", cancelled: "Cancelled" } },
    tabs: [
      { id: 'job', label: '1. Depot Job & Bench', bn: '১. ওয়ার্কশপ জব ও বেঞ্চ', icon: '🔧', badge: '15' },
      { id: 'bookin', label: '1b. Book-In Receipt', bn: '১খ. বুক-ইন রসিদ', icon: '📥', badge: '8' },
      { id: 'soldering', label: '2. Diagnosis & IPC Rework', bn: '২. ডায়াগনোসিস ও মাইক্রো-সোল্ডারিং', icon: '🔍', badge: '9' },
      { id: 'burnin', label: '3. 240-Min Burn-In Gate', bn: '৩. ২৪০-মিনিট বার্ন-ইন যাচাই', icon: '🔥', badge: '6' },
      { id: 'labor', label: '4. SAM Labor Efficiency', bn: '৪. শ্রম দক্ষতা ও কস্টিং', icon: '⏱️', badge: '6' },
      { id: 'qc', label: '5. Quality & Evidence Pack', bn: '৫. কিউসি ও প্রমাণক', icon: '🛡️', badge: '9' },
      { id: 'waiver', label: '6. Waiver & BER Write-Off', bn: '৬. ছাড় ও বিইআর রাইট-অফ', icon: '⚖️', badge: '9' }
    ],
    sections: [
      { tab: 'job', title: "Workshop Repair Job & Bench Routing", note: "A bench repair job. Parts and labour totals roll up from the job lines.",
        fields: [
          { name: 'name', required: true, label: "Job Reference", readonly: true },
          { name: 'order_id', label: "Service Order Reference" },
          { name: 'customer_id', label: "Customer", readonly: true },
          { name: 'device_id', label: "Device", readonly: true },
          { name: 'fault_description', label: "Reported Fault (from the service order)", type: "text", readonly: true },
          { name: 'workshop_id', required: true, label: "Depot / Workshop Facility" },
          { name: 'repair_level', required: true, label: "Repair Capability Level (L1/L2/L3)" },
          { name: 'bench_id', label: "Assigned Workbench (ESD Compliant Today)" },
          { name: 'technician_id', label: "Assigned Depot Technician" },
          { name: 'priority', required: true, label: "Repair Priority Tier" },
          { name: 'device_serial', label: "Device Serial / IMEI" },
          { name: 'estimate_id', label: "Approved Estimate (governing version)", readonly: true },
          { name: 'estimate_ceiling', label: "Approved Amount (BDT)", readonly: true },
          { name: 'cost_over_estimate', label: "Cost Above Approval (re-approval needed)", readonly: true },
          { name: 'rework_of_id', label: "Comeback Of Job", readonly: true },
          { name: 'high_value_device', label: "High-Value Device (secure store overnight)" },
          { name: 'current_location_id', label: "Current Location in Workshop", readonly: true }
        ] },
      { tab: 'bookin', title: "Book-In: Condition & Accessories (A02 audit M31 step 2)",
        note: "Copied from the M01 intake where recorded. Intake needs the condition and the accessories (or 'received without accessories'); the book-in is frozen once the job is booked in.",
        fields: [
          { name: 'bookin_condition', label: "Condition at Book-In", type: "text" },
          { name: 'bookin_accessories', label: "Accessories Received", type: "text" },
          { name: 'bookin_no_accessories', label: "Received Without Accessories" },
          { name: 'bookin_accessory_bag', label: "Accessory Bag Barcode" },
          { name: 'bookin_lci_tripped', label: "Liquid Contact Indicator Tripped" },
          { name: 'bookin_photo_attachment_id', label: "Book-In Photo" },
          { name: 'bookin_by_id', label: "Booked In By", readonly: true },
          { name: 'bookin_at', label: "Booked In At", readonly: true }
        ] },
      { tab: 'soldering', title: "Bench Diagnosis & IPC-7711/7721 Micro-Soldering (FLAW-31.2 / HS-05)",
        note: "What the bench found and did (FR-WSR-018/027), DC power rail measurements, boardview schematics, and IPC visual inspection verification.",
        fields: [
          { name: 'diagnostic_findings', label: "Diagnosis & Defect Coding", type: "text" },
          { name: 'repair_action_summary', label: "Repair Actions Taken", type: "text" },
          { name: 'schematic_designators', label: "Schematic / Boardview IC Designators (e.g. U7000)" },
          { name: 'reflow_profile_name', label: "BGA Reflow Profile Curve" },
          { name: 'flux_solder_spec', label: "Solder Alloy & Flux Spec Lot" },
          { name: 'dc_power_rail_readings', label: "DC Power Rail Pre/Post Diode Readings", type: "text" },
          { name: 'ipc_class_target', label: "IPC-7711/7721 Class Standard" },
          { name: 'ipc_visual_inspection_passed', label: "Microscope 10x-40x Solder Joint Inspection Passed" },
          { name: 'pre_rework_photo_attachment_id', label: "Pre-Rework Microscope Photo" }
        ] },
      { tab: 'burnin', title: "Continuous 240-Minute Stress / Burn-In Gate (FLAW-31.3)",
        note: "L2/L3 repairs require >= 240 minutes (4 hours) continuous burn-in with 0 thermal crashes before QC.",
        fields: [
          { name: 'burn_in_duration_hours', label: "Target Burn-In Duration (Hours)" },
          { name: 'burn_in_actual_minutes', label: "Measured Burn-In Minutes (>= 240m)", readonly: true },
          { name: 'thermal_crash_count', label: "Thermal Crashes Logged (Must be 0)", readonly: true },
          { name: 'burn_in_temp_celsius', label: "Chamber Ambient Temp (°C)" },
          { name: 'burn_in_started_at', label: "Burn-In Started At", readonly: true },
          { name: 'burn_in_completed_at', label: "Burn-In Completed At", readonly: true },
          { name: 'burn_in_passed', label: "Burn-In Interlock Passed", readonly: true }
        ] },
      { tab: 'labor', title: "Standard Allowed Minutes (SAM) & Cost Accounting",
        fields: [
          { name: 'sam_standard_minutes', label: "Standard Allowed Minutes (SAM)" },
          { name: 'actual_logged_minutes', label: "Actual Logged Bench Minutes" },
          { name: 'labor_efficiency_pct', label: "Labor Productivity Efficiency (%)", readonly: true },
          { name: 'parts_total', label: "Spare Parts Total (BDT)", readonly: true },
          /* A02 ERP audit M31-F14: labour is the clock at the workshop rate;
           * the typed figure (no rate) is recorded by a supervisor */
          { name: 'labour_cost', label: "Labour Cost (clock x rate, BDT)", readonly: true },
          { name: 'labour_total', label: "Recorded Labour Figure (no rate, BDT)", readonly: true },
          { name: 'total_repair_cost', label: "Total Direct Repair Cost (BDT)", readonly: true },
          { name: 'dofa_writeoff_tier', label: "DOFA Scrap / BER Write-Off Tier (derived)", readonly: true }
        ] },
      { tab: 'qc', title: "Independent Quality Control & Post-Rework Photos",
        note: "Name the test instrument here and save before Pass QC. It must be fit on the day: calibrated, in service, and if issued, issued to you or to this job's technician. It is fixed once QC passes.",
        fields: [
          { name: 'equipment_id', label: "Test Instrument Used" },
          { name: 'qc_passed', label: "Independent QC Inspection Passed", readonly: true },
          { name: 'qc_inspector_id', label: "Independent QC Inspector (stamped)", readonly: true },
          { name: 'qc_inspector_user_id', label: "QC Inspected By (user)", readonly: true },
          { name: 'qc_inspected_at', label: "QC Inspected At", readonly: true },
          { name: 'qc_notes', label: "QC Inspection Findings", type: "text", readonly: true },
          { name: 'post_rework_photo_attachment_id', label: "Post-Rework Finished Board Photo" },
          { name: 'is_rework', label: "Internal Rework Loop Active", readonly: true },
          { name: 'calibration_review', label: "QC Marked for Review (instrument out of calibration)", readonly: true },
          { name: 'state', label: "Repair Job State", readonly: true }
        ] },
      { tab: 'waiver', title: "M22 Certification Waiver & BER / Scrap Write-Off (DOFA)",
        note: "A waiver is granted by a workshop supervisor; a BER write-off is DOFA-approved on its amount and confirmed by a second technician. Use the workflow buttons.",
        fields: [
          { name: 'certification_waiver', label: "Certification Waiver Granted", readonly: true },
          { name: 'certification_waiver_reason', label: "Waiver Justification", readonly: true },
          { name: 'certification_waiver_by_id', label: "Waiver Granted By", readonly: true },
          { name: 'ber_reason', label: "BER / Scrap Reason", type: "text", readonly: true },
          { name: 'ber_writeoff_amount', label: "Write-Off Amount (BDT)", readonly: true },
          { name: 'dofa_justification', label: "DOFA Justification (Tier 2+)", type: "text" },
          { name: 'dofa_approved', label: "Write-Off DOFA Approved", readonly: true },
          { name: 'dofa_approved_by', label: "Write-Off Approved By", readonly: true },
          { name: 'approval_state', label: "Write-Off Approval (M63)", readonly: true },
          { name: 'ber_confirmed_by_id', label: "BER Confirmed By (Second Technician)", readonly: true }
        ] }
    ]
  },
  'M31-form-bench': {
    kind: 'model_form',
    model: 'fix.workshop.bench',
    title: "Bench Master",
    back: 'M31-benches',
    status: { field: 'state', labels: { available: "Available", occupied: "Occupied", maintenance: "Maintenance", offline: "Offline / Closed" } },
    tabs: [
      { id: 'bench', label: '1. Bench Specification', bn: '১. বেঞ্চ পরিচিতি', icon: '🪑', badge: '7' },
      { id: 'esd', label: '2. Daily ESD Verification Interlock', bn: '২. দৈনিক ইএসডি ইন্টারলক', icon: '⚡', badge: '6' }
    ],
    sections: [
      { tab: 'bench', title: "Physical Repair Bench & Routing Capability", note: "A physical bench with its repair level, tools, and concurrent job capacity.",
        fields: [
          { name: 'workshop_id', required: true, label: "Workshop Facility" },
          { name: 'code', required: true, label: "Bench Identification Code" },
          { name: 'name', required: true, label: "Bench Name" },
          /* NOT NULL on the table: a bench saved without it was refused */
          { name: 'name_bn', required: true, label: "নাম (বাংলা)" },
          { name: 'repair_level', required: true, label: "Repair Level Capability (L1/L2/L3)" },
          { name: 'technician_id', label: "Assigned Primary Technician" },
          { name: 'max_concurrent_jobs', label: "Maximum Concurrent Job Capacity" },
          { name: 'state', label: "Current Bench State (bench actions)", readonly: true }
        ] },
      { tab: 'esd', title: "Daily ESD Mat & Wrist-Strap Telemetry Interlock (FLAW-31.2)",
        note: "ANSI/ESD S20.20 requires wrist strap < 35 MΩ and mat worksurface < 1000 MΩ logged daily. Readings are recorded by the daily ESD log action, not typed here.",
        fields: [
          { name: 'is_esd_safe', label: "ESD Protection Certified Station", readonly: true },
          { name: 'wrist_strap_mohm', label: "Wrist Strap Resistance (< 35.0 MΩ)", readonly: true },
          { name: 'worksurface_rtg_mohm', label: "Worksurface RTG Resistance (< 1000.0 MΩ)", readonly: true },
          { name: 'esd_last_verified_date', label: "Daily ESD Verification Date", readonly: true },
          { name: 'esd_compliant_today', label: "ESD Verification Compliant Today", readonly: true },
          { name: 'calibration_expiry_date', label: "Oscilloscope / DMM Calibration Expiry" },
          { name: 'calibration_cert_attachment_id', label: "Daily Calibration & ESD Log Sheet" }
        ] }
    ]
  },
  'M31-form-evidence': {
    kind: 'model_form',
    model: 'fix.workshop.evidence',
    title: "Test Evidence",
    back: 'M31-testing',
    tabs: [
      { id: 'evidence', label: '1. Test Evidence Spec', bn: '১. প্রমাণক তথ্য', icon: '📎', badge: '6' },
      { id: 'document', label: '2. Governed Document File', bn: '২. গভর্নড ফাইল ও টিয়ার', icon: '📄', badge: '4' }
    ],
    sections: [
      { tab: 'evidence', title: "Diagnostic / Rework Evidence Item", note: "Governed evidence captured against a workshop job.",
        fields: [
          { name: 'job_id', required: true, label: "Target Workshop Job" },
          { name: 'name', required: true, label: "Evidence Title" },
          { name: 'evidence_type', required: true, label: "Evidence Category" },
          { name: 'captured_at', label: "Captured Timestamp (stamped)", readonly: true },
          { name: 'captured_by_id', label: "Captured By Technician (stamped)", readonly: true },
          { name: 'description', label: "Evidence Observations / Engineering Notes", type: "text" }
        ] },
      { tab: 'document', title: "cd_document_core Unified Storage Link (AS-01)",
        fields: [
          { name: 'upload_file', type: 'file', label: "Evidence File" },
          { name: 'upload_filename', label: "File Name" },
          { name: 'document_id', label: "Or an Existing Document" },
          { name: 'attachment_id', label: "Underlying Binary File Attachment", readonly: true },
          { name: 'isolation_tier', label: "Data Residency Isolation Tier", readonly: true }
        ] }
    ]
  },
  'M31-form-workshop': {
    kind: 'model_form',
    model: 'fix.workshop',
    title: "Workshop Facility",
    back: 'M31-benchmaster',
    tabs: [
      { id: 'facility', label: '1. Facility Profile', bn: '১. ফ্যাসিলিটি পরিচিতি', icon: '🏢', badge: '7' },
      { id: 'iso', label: '2. ISO 9001 EPA Certification', bn: '২. আইএসও ৯০০১ ও ইপিএ সনদ', icon: '📜', badge: '5' },
      { id: 'cost', label: '3. Costing Rates', bn: '৩. ব্যয়ের হার', icon: '💰', badge: '3' }
    ],
    sections: [
      { tab: 'facility', title: "Depot Facility Master & Capacity", note: "Depot classification, branch association, and technician capacity.",
        fields: [
          { name: 'code', required: true, label: "Workshop Facility Code" },
          { name: 'name', required: true, label: "Workshop Name" },
          { name: 'name_bn', required: true, label: "নাম (বাংলা)" },
          { name: 'workshop_type', required: true, label: "Depot Classification (Central/Regional/Express)" },
          { name: 'branch_id', label: "Associated Physical Branch Hub" },
          { name: 'manager_id', label: "Workshop Depot Manager" },
          { name: 'active', label: "Active Facility" }
        ] },
      { tab: 'iso', title: "ISO 9001:2015 & EPA ESD Protected Area Standards",
        fields: [
          { name: 'is_esd_certified', label: "EPA (ESD Protected Area) Certified" },
          { name: 'iso_9001_cert_number', label: "ISO 9001:2015 Certificate Number" },
          { name: 'fume_extraction_active', label: "HEPA / Solder Fume Extraction Active" },
          { name: 'power_backup_kva', label: "Online UPS / Diesel Generator (kVA)" },
          { name: 'facility_cert_attachment_id', label: "ISO / EPA Audit Certificate PDF" }
        ] },
      { tab: 'cost', title: "Costing Rates (FR-WSR-043)",
        note: "The rates Build Cost Sheet applies: labour minutes from the work clock, instrument hours, and overhead on the direct cost.",
        fields: [
          { name: 'labour_rate_per_hour', label: "Labour Rate (BDT / hour)" },
          { name: 'equipment_rate_per_hour', label: "Equipment Rate (BDT / hour)" },
          { name: 'overhead_pct', label: "Overhead Absorption (%)" }
        ] }
    ]
  },

  /* ===== sub-module capture forms (2026-11-12) =====
   * Before these, 8 of the 9 Function Register pages offered no capture at
   * all. Each form below captures what its sub-module's requirements name,
   * through the job's own rules: nothing here writes a guarded field. */

  /* 1 Repair Order Creation (FR-WSR-001): the M31 side of the M01 hand-over.
   * The button runs action_create_workshop_job, which refuses a draft,
   * closed or already-received order and copies device, customer, fault and
   * the M01 book-in. The level starts at L1; Job Routing revises it. */
  'M31-form-receive': {
    kind: 'model_form',
    model: 'fix.service.order',
    title: 'Receive Device into Workshop',
    newLabel: 'Receive Device into Workshop',
    back: 'M31-orders',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the service order whose device arrives at the workshop',
      note: 'Booked-in service orders that have no workshop job yet. A draft order is booked in at M01 intake first.',
      search: 'Search order / customer / serial',
      choose: 'Receive this device',
      cols: ['name', 'customer_id', 'device_id', 'branch_id', 'priority', 'state'],
      domain: [['state', 'in', ['intake', 'diagnostic', 'approved', 'in_repair']], ['workshop_job_ids', '=', false]],
      empty: 'No booked-in service order is waiting for the workshop.'
    },
    saveAction: {
      method: 'action_create_workshop_job', label: 'Receive into Workshop',
      done: 'Device received: a draft repair order is in the workshop queue',
      kwargs: {}
    },
    sections: [
      { title: 'Step 2 of 2: Confirm the Device Being Received',
        note: 'The repair order takes the workshop of the order\'s branch (else the central workshop), the device, customer, priority, reported fault and the M01 book-in record. Complete the book-in and route the level on the repair order next.',
        fields: [
          { name: 'name', label: 'Service Order', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'branch_id', label: 'Branch', readonly: true },
          { name: 'priority', label: 'Priority', readonly: true },
          { name: 'state', label: 'Order State', readonly: true },
          { name: 'fault_description', label: 'Reported Fault', type: 'text', readonly: true }
        ] }
    ]
  },

  /* 4 Repair-Level Routing (FR-WSR-003/020) and 8 Rework & Transfers
   * (FR-WSR-016/038): the job's level, workshop, bench and technician. The
   * level and technician lock once the job is on the bench (the model refuses
   * the change with its reason); certification is checked at Start Repair. */
  'M31-form-routing': {
    kind: 'model_form',
    model: 'fix.workshop.job',
    title: 'Job Routing',
    newLabel: 'Route or Re-route a Job',
    back: 'M31-orders',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the repair job to route',
      note: 'Jobs not yet on the bench, and jobs back from a failed QC (internal rework). Once a job is in repair, burn-in or QC its level and technician are fixed.',
      search: 'Search job / order / serial',
      choose: 'Route this job',
      cols: ['name', 'order_reference', 'repair_level', 'workshop_id', 'bench_id', 'technician_id', 'is_rework', 'state'],
      domain: [['state', 'in', ['draft', 'intake', 'diagnostic', 'waiting_parts', 'qc_failed']]],
      empty: 'No repair job is waiting to be routed.'
    },
    sections: [
      { title: 'Step 2 of 2: Level, Workshop, Bench & Technician',
        note: 'Confirm or revise the repair level after inspection. A higher level that raises the cost above the approved estimate needs the estimate re-approved in M01 before QC (BRU-WSR-11). The workshop changes here only before book-in; a booked-in job moves by a Workshop Transfer (Rework & Transfers page, BRU-WSR-14).',
        fields: [
          { name: 'name', label: 'Job Reference', readonly: true },
          { name: 'order_reference', label: 'Service Order', readonly: true },
          { name: 'device_serial', label: 'Device Serial / IMEI', readonly: true },
          { name: 'state', label: 'Job State', readonly: true },
          { name: 'is_rework', label: 'Internal Rework', readonly: true },
          { name: 'rework_count', label: 'Rework Loops', readonly: true },
          { name: 'rework_reason', label: 'Why QC Failed', readonly: true },
          { name: 'repair_level', required: true, label: 'Repair Level (L1/L2/L3)' },
          { name: 'workshop_id', required: true, label: 'Workshop (before book-in only)' },
          { name: 'bench_id', label: 'Bench' },
          { name: 'technician_id', label: 'Technician' },
          { name: 'priority', required: true, label: 'Priority' }
        ] }
    ]
  },

  /* 5 Diagnosis & Execution (FR-WSR-018/025/027): what the bench found and
   * did. The findings and repair actions had no input anywhere. */
  'M31-form-diagnosis': {
    kind: 'model_form',
    model: 'fix.workshop.job',
    title: 'Bench Diagnosis',
    newLabel: 'Record Bench Diagnosis',
    back: 'M31-diag',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the job on the bench',
      note: 'Jobs booked in, in diagnosis, waiting for parts, in repair, or back from a failed QC.',
      search: 'Search job / order / serial',
      choose: 'Record diagnosis',
      cols: ['name', 'order_reference', 'device_serial', 'repair_level', 'technician_id', 'state'],
      domain: [['state', 'in', ['intake', 'diagnostic', 'waiting_parts', 'in_repair', 'qc_failed']]],
      empty: 'No job is on the bench.'
    },
    tabs: [
      { id: 'diag', label: '1. Findings & Repair Actions', bn: '১. ফলাফল ও মেরামত কাজ', icon: '🔍', badge: '9' },
      { id: 'ipc', label: '2. Measurements & Micro-Soldering', bn: '২. পরিমাপ ও মাইক্রো-সোল্ডারিং', icon: '🔬', badge: '7' }
    ],
    sections: [
      { tab: 'diag', title: 'Step 2 of 2: Bench Diagnosis',
        note: 'Record the findings in Bengali or English. The instrument named here is the one QC checks for calibration.',
        fields: [
          { name: 'name', label: 'Job Reference', readonly: true },
          { name: 'order_reference', label: 'Service Order', readonly: true },
          { name: 'device_serial', label: 'Device Serial / IMEI', readonly: true },
          { name: 'repair_level', label: 'Repair Level', readonly: true },
          { name: 'state', label: 'Job State', readonly: true },
          { name: 'fault_description', label: 'Reported Fault', type: 'text', readonly: true },
          { name: 'diagnostic_findings', label: 'Diagnosis & Defect Coding', type: 'text' },
          { name: 'repair_action_summary', label: 'Repair Actions Taken', type: 'text' },
          { name: 'equipment_id', label: 'Test / Repair Instrument Used' }
        ] },
      { tab: 'ipc', title: 'Component-Level Measurements (IPC-7711/7721)',
        fields: [
          { name: 'schematic_designators', label: 'Schematic / Boardview Designators (e.g. U7000)' },
          { name: 'dc_power_rail_readings', label: 'DC Power Rail Pre/Post Readings', type: 'text' },
          { name: 'reflow_profile_name', label: 'BGA Reflow Profile' },
          { name: 'flux_solder_spec', label: 'Solder Alloy & Flux Lot' },
          { name: 'ipc_class_target', label: 'IPC Class Standard' },
          { name: 'ipc_visual_inspection_passed', label: 'Microscope Solder Joint Inspection Passed' },
          { name: 'pre_rework_photo_attachment_id', label: 'Pre-Rework Microscope Photo' }
        ] }
    ]
  },

  /* 6 Parts Consumption & Genealogy (FR-WSR-022/023): a part line on a job.
   * The cost is the part's standard cost (set by the model, not typed);
   * reserving and consuming stay the list actions, inside the estimate. */
  'M31-form-part': {
    kind: 'model_form',
    model: 'fix.workshop.part.line',
    title: 'Part Fitment',
    back: 'M31-parts',
    status: { field: 'reservation_state' },
    sections: [
      { title: 'Part, Job & Genealogy',
        note: 'One line per part fitted. The serial and the board position make the genealogy trace; a part harvested from a donor board names that board. A closed job takes no new parts.',
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'product_id', required: true, label: 'Spare Part' },
          { name: 'quantity', required: true, label: 'Quantity' },
          { name: 'source_origin', required: true, label: 'Part Source' },
          { name: 'lot_serial_number', label: 'Part Serial / Lot Number' },
          { name: 'circuit_designator', label: 'Board Position (e.g. U3100)' },
          { name: 'donor_board_serial', label: 'Donor Board S/N (harvested part)' },
          { name: 'notes', label: 'Fitment Notes' },
          { name: 'part_photo_attachment_id', label: 'Old vs New Part Photo' }
        ] },
      { title: 'Cost & Stock Status',
        fields: [
          { name: 'part_number', label: 'Part Number', readonly: true },
          { name: 'unit_cost', label: 'Unit Cost (standard cost)', readonly: true },
          { name: 'subtotal', label: 'Line Cost', readonly: true },
          { name: 'reservation_state', label: 'Stock Status', readonly: true },
          { name: 'consumption_ref', label: 'Stock Consumption Ref', readonly: true }
        ] }
    ]
  },

  /* 9 Repair Costing (FR-WSR-026/043/044): the labour inputs. Parts, totals
   * and the estimate comparison are computed from the job's lines. */
  'M31-form-labour': {
    kind: 'model_form',
    model: 'fix.workshop.job',
    title: 'Labour & Cost',
    newLabel: 'Record Labour & Cost',
    back: 'M31-orders',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the repair job',
      note: 'Open jobs. A delivered, written-off or cancelled job is the record of the repair and is not changed.',
      search: 'Search job / order / serial',
      choose: 'Record labour',
      cols: ['name', 'order_reference', 'repair_level', 'technician_id', 'labour_cost', 'total_repair_cost', 'state'],
      domain: [['state', 'not in', ['delivered', 'unrepairable', 'cancelled']]],
      empty: 'No open repair job.'
    },
    sections: [
      { title: 'Step 2 of 2: Labour Time & Cost',
        note: 'Cost above the approved amount stops the job at QC until the estimate is re-approved in M01 or the extra parts are approved (BRU-WSR-11).',
        fields: [
          { name: 'name', label: 'Job Reference', readonly: true },
          { name: 'order_reference', label: 'Service Order', readonly: true },
          { name: 'repair_level', label: 'Repair Level', readonly: true },
          { name: 'state', label: 'Job State', readonly: true },
          { name: 'sam_standard_minutes', label: 'Standard Allowed Minutes (SAM)' },
          { name: 'actual_logged_minutes', label: 'Actual Bench Minutes' },
          { name: 'labour_cost', label: 'Labour Cost (clock x rate, BDT)', readonly: true },
          { name: 'labour_total', label: 'Recorded Labour Figure (no rate, BDT)', readonly: true },
          { name: 'labor_efficiency_pct', label: 'Labour Efficiency (%)', readonly: true },
          { name: 'parts_total', label: 'Parts Cost (BDT)', readonly: true },
          { name: 'total_repair_cost', label: 'Total Repair Cost (BDT)', readonly: true },
          { name: 'estimate_ceiling', label: 'Approved Amount (BDT)', readonly: true },
          { name: 'cost_over_estimate', label: 'Cost Above Approval', readonly: true }
        ] }
    ]
  },

  /* 3 Bench Allocation & Queue (FR-WSR-011/015, BRU-WSR-02/06): a waiting
   * job goes to a bench and a technician through action_allocate_bench. It
   * refuses a bench of another workshop, under maintenance, closed, full or
   * below the job's level, and a technician not certified for the job; a job
   * already on a bench is handed over and its old bench freed. */
  'M31-form-allocate': {
    kind: 'model_form',
    model: 'fix.workshop.job',
    title: 'Bench Allocation',
    newLabel: 'Allocate a Job to a Bench',
    back: 'M31-benches',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the job to allocate or hand over',
      note: 'Jobs waiting for a bench, and jobs on a bench that move to another bench or technician. A job in repair keeps its technician; only its bench can change.',
      search: 'Search job / order / serial',
      choose: 'Allocate this job',
      cols: ['name', 'order_reference', 'repair_level', 'workshop_id', 'bench_id', 'technician_id', 'priority', 'state'],
      domain: [['state', 'in', ['draft', 'intake', 'diagnostic', 'waiting_parts', 'in_repair', 'qc_failed']]],
      empty: 'No repair job is waiting for a bench.'
    },
    saveAction: {
      method: 'action_allocate_bench', label: 'Allocate to Bench',
      done: 'Job allocated: the bench and technician are set and the note is on the job',
      kwargs: { bench_id: 'bench_id', technician_id: 'technician_id', note: 'bench_handover_note' }
    },
    sections: [
      { title: 'Step 2 of 2: Bench, Technician & Hand-Over Note',
        note: "The bench must be in the job's workshop, in service, of the job's level or higher, and have room. Leave the technician empty to keep the job's own, or to take the one stationed at the bench. An L2/L3 job needs a technician certified for it.",
        fields: [
          { name: 'name', label: 'Job Reference', readonly: true },
          { name: 'order_reference', label: 'Service Order', readonly: true },
          { name: 'device_serial', label: 'Device Serial / IMEI', readonly: true },
          { name: 'workshop_id', label: 'Workshop', readonly: true },
          { name: 'repair_level', label: 'Repair Level', readonly: true },
          { name: 'priority', label: 'Priority', readonly: true },
          { name: 'state', label: 'Job State', readonly: true },
          /* readonly for the generic write; INPUTS here: saveAction carries
           * them to action_allocate_bench, which applies the bench rules */
          { name: 'bench_id', label: 'Bench', required: true, readonly: true },
          { name: 'technician_id', label: 'Technician', readonly: true },
          { name: 'bench_handover_note', label: 'Allocation / Hand-Over Note', type: 'text', readonly: true }
        ] }
    ]
  },

  /* 7 Testing & Burn-In (FR-WSR-032/035): one measured result against a
   * protocol test. The pass is judged by the test's limits, not typed. */
  'M31-form-testresult': {
    kind: 'model_form',
    model: 'fix.workshop.test.result',
    title: 'Test Protocol Result',
    newLabel: 'Record a Test Result',
    back: 'M31-testresults',
    sections: [
      { title: 'Job, Protocol Test & Measurement',
        note: "Choose the job and the protocol test, then enter what the instrument read. Inside the test's limits it passes, outside it fails. For a check with no limits (visual, functional), tick whether it passed. Results are fixed once the job passes QC.",
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'step_id', required: true, label: 'Protocol Test' },
          { name: 'measured_value', label: 'Measured Value' },
          { name: 'observed_pass', label: 'Check Passed (test with no limits)' },
          { name: 'equipment_id', label: 'Instrument Used' },
          { name: 'notes', label: 'Observations', type: 'text' }
        ] },
      { title: 'Limits & Outcome',
        fields: [
          { name: 'protocol_id', label: 'Protocol', readonly: true },
          { name: 'unit', label: 'Unit', readonly: true },
          { name: 'lower_limit', label: 'Lower Limit', readonly: true },
          { name: 'upper_limit', label: 'Upper Limit', readonly: true },
          { name: 'passed', label: 'Passed', readonly: true },
          { name: 'tested_by_id', label: 'Tested By', readonly: true },
          { name: 'tested_at', label: 'Tested At', readonly: true }
        ] }
    ]
  },

  /* 7 the protocol library (FR-WSR-031): a workshop manager defines the
   * tests, their limits and the burn-in duration for a device category */
  'M31-form-protocol': {
    kind: 'model_form',
    model: 'fix.workshop.test.protocol',
    title: 'Test Protocol',
    back: 'M31-protocols',
    lines: { field: 'step_ids', title: 'Tests in this Protocol',
      note: 'One line per test. Tick "Against Limits" for a measured test and give its limits and unit; leave it unticked for a visual or functional check.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'code', label: 'Test Code' },
        { name: 'name', label: 'Test', required: true },
        { name: 'unit', label: 'Unit' },
        { name: 'has_limits', label: 'Against Limits' },
        { name: 'lower_limit', label: 'Lower Limit' },
        { name: 'upper_limit', label: 'Upper Limit' }
      ] },
    sections: [
      { title: 'Protocol',
        note: 'Burn-in may be extended beyond the protocol duration, never shortened below it (BRU-WSR-07). Only a workshop manager maintains the library.',
        fields: [
          { name: 'code', required: true, label: 'Protocol Code' },
          { name: 'name', required: true, label: 'Protocol Name' },
          { name: 'device_type', label: 'Device Category' },
          { name: 'repair_level', label: 'Repair Level' },
          { name: 'fault_type', label: 'Fault Type' },
          { name: 'burn_in_minutes', label: 'Burn-In Duration (minutes)' },
          { name: 'pass_criteria', label: 'Pass Criteria', type: 'text' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },


  /* ===== capture pass 2 (19 Nov 2026) =====
   * Read against the spec (FR-WSR-001..053, BRU-WSR-01..14, §10.1), the
   * pages still had no capture for most of what a workshop records. Each
   * screen below is the spec's own record; the server applies its rules. */

  /* 1/3: where the device is (FR-WSR-005 buffer, 042 staging, 053 secure store) */
  'M31-custody': { kind: 'model_list', model: 'fix.workshop.custody.move', title: 'Device Location Moves',
    cols: ['job_id', 'from_location_id', 'location_id', 'location_kind', 'note', 'moved_by_id', 'moved_at'] },
  'M31-locations': { kind: 'model_list', model: 'fix.workshop.location', title: 'Workshop Locations',
    cols: ['workshop_id', 'code', 'name', 'kind', 'capacity', 'occupant_count', 'active'] },
  'M31-form-custody': {
    kind: 'model_form', model: 'fix.workshop.custody.move', title: 'Move Device to Location',
    newLabel: 'Move Device to Location', back: 'M31-custody',
    sections: [
      { title: 'Job & Location',
        note: "Place a booked-in device in the incoming buffer until a bench takes it, in outgoing staging once released, or in the secure store overnight if it is high value (BRU-WSR-13). The location must be in the job's workshop. The trail is never edited.",
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'location_id', required: true, label: 'To Location' },
          { name: 'note', label: 'Note' },
          { name: 'from_location_id', label: 'From Location', readonly: true },
          { name: 'moved_by_id', label: 'Moved By', readonly: true },
          { name: 'moved_at', label: 'Moved At', readonly: true }
        ] }
    ]
  },
  'M31-form-location': {
    kind: 'model_form', model: 'fix.workshop.location', title: 'Workshop Location', back: 'M31-locations',
    sections: [
      { title: 'Location', note: 'Incoming buffer, outgoing staging or the secure store for high-value devices. Capacity 0 means no limit.',
        fields: [
          { name: 'workshop_id', required: true, label: 'Workshop' },
          { name: 'code', required: true, label: 'Location Code' },
          { name: 'name', required: true, label: 'Location' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'capacity', label: 'Capacity (devices)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* 2: the daily ESD check (FR-WSR-050) and burn-in stations (FR-WSR-034) */
  'M31-esd-checks': { kind: 'model_list', model: 'fix.workshop.esd.check', title: 'Bench ESD Checks',
    cols: ['bench_id', 'workshop_id', 'wrist_strap_mohm', 'worksurface_mohm', 'passed', 'checked_by_id', 'checked_at'] },
  'M31-form-esd': {
    kind: 'model_form', model: 'fix.workshop.esd.check', title: 'ESD Bench Check', back: 'M31-esd-checks',
    sections: [
      { title: 'Pre-Shift ESD Reading',
        note: 'Wrist strap below 35 MΩ and worksurface below 1000 MΩ pass. A failed reading is kept and blocks L2/L3 repair on the bench until a passing check.',
        fields: [
          { name: 'bench_id', required: true, label: 'Bench' },
          { name: 'wrist_strap_mohm', required: true, label: 'Wrist Strap (MΩ)' },
          { name: 'worksurface_mohm', required: true, label: 'Worksurface (MΩ)' },
          { name: 'note', label: 'Note' },
          { name: 'passed', label: 'Passed', readonly: true },
          { name: 'checked_by_id', label: 'Checked By', readonly: true },
          { name: 'checked_at', label: 'Checked At', readonly: true }
        ] }
    ]
  },
  'M31-burnin-stations': { kind: 'model_list', model: 'fix.workshop.burnin.station', title: 'Burn-In Stations',
    cols: ['workshop_id', 'code', 'name', 'capacity', 'running_count', 'load_profile', 'active'] },
  'M31-form-station': {
    kind: 'model_form', model: 'fix.workshop.burnin.station', title: 'Burn-In Station', back: 'M31-burnin-stations',
    sections: [
      { title: 'Station', note: 'Once a workshop has a station, its burn-in runs start at a station, within its capacity.',
        fields: [
          { name: 'workshop_id', required: true, label: 'Workshop' },
          { name: 'code', required: true, label: 'Station Code' },
          { name: 'name', required: true, label: 'Station' },
          { name: 'capacity', required: true, label: 'Devices at Once' },
          { name: 'load_profile', label: 'Default Load Profile' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* 3: hand-overs (from Allocate to Bench) and the shift close (FR-WSR-017, BRU-WSR-13) */
  'M31-handovers': { kind: 'model_list', model: 'fix.workshop.bench.handover', title: 'Bench Hand-Overs', create: false,
    cols: ['job_id', 'from_bench_id', 'to_bench_id', 'from_technician_id', 'to_technician_id', 'job_state', 'note', 'occurred_at'] },
  'M31-shift-closes': { kind: 'model_list', model: 'fix.workshop.shift.close', title: 'Shift Closes', stateField: 'state',
    cols: ['workshop_id', 'shift_date', 'shift', 'counted_wip', 'system_wip', 'high_value_count', 'state', 'closed_by_id'],
    actions: [{ m: 'action_close', l: 'Close the Shift (Supervisor)' }] },
  'M31-form-shiftclose': {
    kind: 'model_form', model: 'fix.workshop.shift.close', title: 'Shift Close', back: 'M31-shift-closes',
    status: { field: 'state', labels: { draft: 'Open', closed: 'Closed' } },
    sections: [
      { title: 'Shift Count',
        note: 'Count the devices held. Close the shift from the list: the count must match the system or carry its exception, and every high-value device must be in the secure store (BRU-WSR-13).',
        fields: [
          { name: 'workshop_id', required: true, label: 'Workshop' },
          { name: 'shift_date', required: true, label: 'Shift Date' },
          { name: 'shift', required: true, label: 'Shift' },
          { name: 'counted_wip', required: true, label: 'Devices Counted' },
          { name: 'exception_note', label: 'Count Exception', type: 'text' },
          { name: 'system_wip', label: 'Devices per System', readonly: true },
          { name: 'high_value_count', label: 'High-Value Devices Held', readonly: true },
          { name: 'high_value_summary', label: 'High-Value Devices and Locations', type: 'text', readonly: true },
          { name: 'closed_by_id', label: 'Closed By', readonly: true },
          { name: 'closed_at', label: 'Closed At', readonly: true }
        ] }
    ]
  },

  /* 4: escalation (FR-WSR-029) */
  'M31-escalations': { kind: 'model_list', model: 'fix.workshop.escalation', title: 'Escalations', stateField: 'state',
    cols: ['job_id', 'escalation_type', 'to_level', 'to_technician_id', 'to_workshop_id', 'state', 'requested_by_id', 'decided_by_id'],
    actions: [
      { m: 'action_accept', l: 'Accept (Supervisor)', ask: 'Decision note (optional)', kwarg: 'note' },
      { m: 'action_decline', l: 'Decline (Supervisor)', ask: 'Why is it declined?', kwarg: 'note' }
    ] },
  'M31-form-escalation': {
    kind: 'model_form', model: 'fix.workshop.escalation', title: 'Escalation', newLabel: 'Escalate a Repair', back: 'M31-escalations',
    status: { field: 'state' },
    sections: [
      { title: 'Escalate To',
        note: 'Name a higher level, a specialist technician or another workshop, and why. The bench context is copied in. A supervisor other than you accepts it; another workshop becomes a Workshop Transfer.',
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'escalation_type', required: true, label: 'Escalate To' },
          { name: 'to_level', label: 'New Repair Level' },
          { name: 'to_technician_id', label: 'Specialist Technician' },
          { name: 'to_workshop_id', label: 'Other Workshop' },
          { name: 'reason', required: true, label: 'Why Escalate', type: 'text' },
          { name: 'context_snapshot', label: 'Bench Context', type: 'text', readonly: true },
          { name: 'decision_note', label: 'Decision Note', type: 'text', readonly: true }
        ] }
    ]
  },

  /* 5: teardown (FR-WSR-019) and instrument use (FR-WSR-025/040, BRU-WSR-09) */
  'M31-teardowns': { kind: 'model_list', model: 'fix.workshop.teardown', title: 'Teardown Records',
    cols: ['job_id', 'sequence', 'component', 'designator', 'condition', 'recorded_by_id', 'recorded_at'] },
  'M31-form-teardown': {
    kind: 'model_form', model: 'fix.workshop.teardown', title: 'Teardown Record', back: 'M31-teardowns',
    sections: [
      { title: 'Component Removed',
        note: 'One line per component taken off, in order, with its condition and a photo where the procedure asks for one. Fixed once the job passes QC.',
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'sequence', label: 'Step' },
          { name: 'component', required: true, label: 'Component Removed' },
          { name: 'designator', label: 'Board Position / Designator' },
          { name: 'condition', required: true, label: 'Condition' },
          { name: 'photo_attachment_id', label: 'Photo' },
          { name: 'note', label: 'Observation', type: 'text' }
        ] }
    ]
  },
  'M31-instrument-uses': { kind: 'model_list', model: 'fix.workshop.instrument.use', title: 'Instruments Used',
    cols: ['job_id', 'equipment_id', 'purpose', 'used_from', 'used_to', 'hours', 'calibration_valid', 'calibration_problem'] },
  'M31-form-instrument': {
    kind: 'model_form', model: 'fix.workshop.instrument.use', title: 'Instrument Use', back: 'M31-instrument-uses',
    sections: [
      { title: 'Instrument & Time',
        note: "Every test or repair instrument used on the job. An instrument out of calibration is recorded and flagged, and the job's QC is marked for review (BRU-WSR-09). M45 gets the usage row.",
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'equipment_id', required: true, label: 'Instrument' },
          { name: 'purpose', label: 'Used For' },
          { name: 'used_from', required: true, label: 'Used From' },
          { name: 'used_to', label: 'Used To' },
          { name: 'calibration_valid', label: 'Calibration Valid at Use', readonly: true },
          { name: 'calibration_problem', label: 'Calibration Problem', readonly: true }
        ] }
    ]
  },

  /* 6: consumables (FR-WSR-024) */
  'M31-consumables': { kind: 'model_list', model: 'fix.workshop.consumable.usage', title: 'Consumables Used',
    cols: ['job_id', 'product_id', 'quantity', 'uom_name', 'unit_cost', 'subtotal', 'recorded_by_id', 'recorded_at'] },
  'M31-form-consumable': {
    kind: 'model_form', model: 'fix.workshop.consumable.usage', title: 'Consumable Usage', back: 'M31-consumables',
    sections: [
      { title: 'Consumable',
        note: "Solder, flux, thermal paste, adhesive, cleaning agents. Costed at the item's standard cost; the cost sheet adds them up.",
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'product_id', required: true, label: 'Consumable' },
          { name: 'quantity', required: true, label: 'Quantity' },
          { name: 'notes', label: 'Notes' },
          { name: 'uom_name', label: 'Unit', readonly: true },
          { name: 'unit_cost', label: 'Unit Cost (BDT)', readonly: true },
          { name: 'subtotal', label: 'Cost (BDT)', readonly: true }
        ] }
    ]
  },

  /* 7: burn-in at a station (FR-WSR-033, BRU-WSR-07) */
  'M31-burnin-sessions': { kind: 'model_list', model: 'fix.workshop.burnin.session', title: 'Burn-In Runs',
    cols: ['job_id', 'station_id', 'required_minutes', 'minimum_minutes', 'started_at', 'due_at', 'completed_at', 'outcome'],
    actions: [{ m: 'action_extend', l: 'Extend the Run', ask: 'Extra minutes (a run is never shortened)', kwarg: 'minutes' }] },
  'M31-form-burnin': {
    kind: 'model_form', model: 'fix.workshop.burnin.session', title: 'Burn-In Run', newLabel: 'Start Burn-In at a Station', back: 'M31-burnin-sessions',
    sections: [
      { title: 'Job & Station',
        note: "Starts the job's burn-in at the station, within its capacity. The duration defaults to the protocol's (240 minutes for L2/L3): you may set more, never less (BRU-WSR-07). Pass or fail it on the Testing list.",
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'station_id', required: true, label: 'Station' },
          { name: 'required_minutes', label: 'Run Minutes (blank = protocol)' },
          { name: 'load_profile', label: 'Load Profile' },
          { name: 'minimum_minutes', label: 'Protocol Minimum', readonly: true },
          { name: 'started_at', label: 'Started At', readonly: true },
          { name: 'due_at', label: 'Due At', readonly: true },
          { name: 'outcome', label: 'Outcome', readonly: true }
        ] }
    ]
  },

  /* 8: internal rework (FR-WSR-038, BRU-WSR-10) and workshop transfer (FR-WSR-016, BRU-WSR-14) */
  'M31-reworks': { kind: 'model_list', model: 'fix.workshop.rework', title: 'Internal Rework Loops', create: false,
    cols: ['job_id', 'iteration', 'failed_at_state', 'reason', 'attributed_to_id', 'repair_level', 'raised_at'] },
  'M31-transfers': { kind: 'model_list', model: 'fix.workshop.transfer', title: 'Workshop Transfers', stateField: 'state',
    cols: ['job_id', 'from_workshop_id', 'to_workshop_id', 'stage', 'state', 'consignment_id', 'requested_by_id', 'confirmed_by_id'],
    actions: [
      { m: 'action_confirm', l: 'Confirm (Receiving Workshop)' },
      { m: 'action_receive', l: 'Record Arrival' },
      { m: 'action_decline', l: 'Decline (Receiving Workshop)', ask: 'Why is it declined?', kwarg: 'note' },
      { m: 'action_cancel', l: 'Cancel Request', ask: 'Why is it cancelled?', kwarg: 'note' }
    ] },
  'M31-form-transfer': {
    kind: 'model_form', model: 'fix.workshop.transfer', title: 'Workshop Transfer', newLabel: 'Request a Workshop Transfer', back: 'M31-transfers',
    status: { field: 'state' },
    sections: [
      { title: 'Job, Receiving Workshop & Reason',
        note: 'For a specialist stage in another workshop. The receiving workshop confirms it, which raises the M03 consignment and moves the job off its bench (BRU-WSR-14). A job on the bench is first put to Wait for Parts.',
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'to_workshop_id', required: true, label: 'Receiving Workshop' },
          { name: 'stage', label: 'Specialist Stage' },
          { name: 'reason', required: true, label: 'Why Transfer', type: 'text' },
          { name: 'from_workshop_id', label: 'From Workshop', readonly: true },
          { name: 'consignment_id', label: 'M03 Consignment', readonly: true },
          { name: 'confirmed_by_id', label: 'Confirmed By', readonly: true },
          { name: 'received_at', label: 'Received At', readonly: true }
        ] }
    ]
  },

  /* 9: the work clock (FR-WSR-026) and the cost build-up (FR-WSR-043/044) */
  'M31-timelogs': { kind: 'model_list', model: 'fix.workshop.time.log', title: 'Time Booked',
    cols: ['job_id', 'technician_id', 'activity', 'started_at', 'ended_at', 'minutes', 'running', 'note'],
    actions: [{ m: 'action_stop', l: 'Stop / Pause the Clock', ask: 'Note (optional)', kwarg: 'note' }] },
  'M31-form-clock': {
    kind: 'model_form', model: 'fix.workshop.time.log', title: 'Work Clock', newLabel: 'Start the Work Clock', back: 'M31-timelogs',
    sections: [
      { title: 'Start Booking Time',
        note: 'Time is booked as the work proceeds, never afterwards (SOP SP-010 step 10). Start the clock now; stop it from the list to pause, and start a new one to resume. Waiting time is booked apart from active work.',
        fields: [
          { name: 'job_id', required: true, label: 'Repair Job' },
          { name: 'activity', required: true, label: 'Activity' },
          { name: 'note', label: 'Note' },
          { name: 'technician_id', label: 'Technician', readonly: true },
          { name: 'started_at', label: 'Started', readonly: true }
        ] }
    ]
  },
  'M31-cost-jobs': { kind: 'model_list', model: 'fix.workshop.job', title: 'Cost Sheets', create: false,
    cols: ['name', 'repair_level', 'logged_active_minutes', 'labour_cost', 'parts_total', 'consumables_total', 'total_repair_cost', 'full_cost', 'estimate_ceiling', 'cost_variance', 'cost_variance_flag'],
    domain: [['state', '!=', 'draft']],
    actions: [
      { m: 'action_build_cost_sheet', l: 'Build Cost Sheet' },
      /* A02 ERP audit M31-F14: only where the workshop has no labour rate */
      { m: 'action_record_labour', l: 'Record Labour Figure (no rate, Supervisor)', ask: 'Labour cost in BDT', kwarg: 'amount' }
    ] },
  'M31-costlines': { kind: 'model_list', model: 'fix.workshop.cost.line', title: 'Cost Build-Up', create: false,
    cols: ['job_id', 'cost_type', 'description', 'quantity', 'rate', 'amount', 'built_at'] },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M31:Bench Utilisation by Workshop": "M31-transfer",
  "M31:Repair Cycle Time by Level": "M31-throughput",
  "M31:Internal Rework Loop Analysis": "M31-methods",
  "M31:Workshop Cost per Repair": "M31-costing",
  "M31:Parts Genealogy Trace": "M31-rpt-genealogy",
  "M31:Burn-In Failure Report": "M31-rpt-burnin"
};

/* every M31 form is an in-workspace form (FORM_CHIPS below) */
export const FORM_MODELS = {};

/* the module's "+ New" surface: no generic create — a job starts from the
 * service-order hand-over (sub-module 1, "Receive Device into Workshop"). */
export const CREATE = {};


export const FORM_CHIPS = {
  'M31:Receive Device into Workshop': 'M31-form-receive',
  'M31:Repair Order': 'M31-form-job',
  'M31:Workshop Facility': 'M31-form-workshop',
  'M31:Bench Master': 'M31-form-bench',
  'M31:Bench Allocation': 'M31-form-allocate',
  'M31:Job Routing': 'M31-form-routing',
  'M31:Bench Diagnosis': 'M31-form-diagnosis',
  'M31:Part Fitment': 'M31-form-part',
  'M31:Test Protocol Result': 'M31-form-testresult',
  'M31:Test Protocol': 'M31-form-protocol',
  'M31:Test Evidence': 'M31-form-evidence',
  'M31:Labour & Cost': 'M31-form-labour',
  /* capture pass 2 (19 Nov 2026) */
  'M31:Move Device to Location': 'M31-form-custody',
  'M31:Workshop Location': 'M31-form-location',
  'M31:Burn-In Station': 'M31-form-station',
  'M31:ESD Bench Check': 'M31-form-esd',
  'M31:Shift Close': 'M31-form-shiftclose',
  'M31:Escalation': 'M31-form-escalation',
  'M31:Teardown Record': 'M31-form-teardown',
  'M31:Instrument Use': 'M31-form-instrument',
  // FR-WSR-028: a repair note proposed to the M61 library is M61's field capture
  'M31:Knowledge Capture': 'M61-form-capture',
  'M31:Consumable Usage': 'M31-form-consumable',
  'M31:Burn-In Run': 'M31-form-burnin',
  'M31:Workshop Transfer': 'M31-form-transfer',
  'M31:Work Clock': 'M31-form-clock',
  'M31:__by_model__': {
    'fix.workshop.job': 'M31-form-job',
    'fix.workshop.bench': 'M31-form-bench',
    'fix.workshop.evidence': 'M31-form-evidence',
    'fix.workshop': 'M31-form-workshop',
    'fix.workshop.part.line': 'M31-form-part',
    'fix.workshop.test.result': 'M31-form-testresult',
    'fix.workshop.test.protocol': 'M31-form-protocol',
    'fix.workshop.custody.move': 'M31-form-custody',
    'fix.workshop.location': 'M31-form-location',
    'fix.workshop.burnin.station': 'M31-form-station',
    'fix.workshop.esd.check': 'M31-form-esd',
    'fix.workshop.shift.close': 'M31-form-shiftclose',
    'fix.workshop.escalation': 'M31-form-escalation',
    'fix.workshop.teardown': 'M31-form-teardown',
    'fix.workshop.instrument.use': 'M31-form-instrument',
    'fix.workshop.consumable.usage': 'M31-form-consumable',
    'fix.workshop.burnin.session': 'M31-form-burnin',
    'fix.workshop.transfer': 'M31-form-transfer',
    'fix.workshop.time.log': 'M31-form-clock',
  },
  'M31:__by_screen__': {
    'M31-orders': 'M31-form-job',
    'M31-record': 'M31-form-job',
    'M31-diag': 'M31-form-job',
    'M31-testing': 'M31-form-job',
    'M31-benches': 'M31-form-bench',
    'M31-benchmaster': 'M31-form-workshop',
    'M31-parts': 'M31-form-part',
    'M31-testresults': 'M31-form-testresult',
    'M31-protocols': 'M31-form-protocol',
    'M31-custody': 'M31-form-custody',
    'M31-locations': 'M31-form-location',
    'M31-burnin-stations': 'M31-form-station',
    'M31-esd-checks': 'M31-form-esd',
    'M31-shift-closes': 'M31-form-shiftclose',
    'M31-escalations': 'M31-form-escalation',
    'M31-teardowns': 'M31-form-teardown',
    'M31-instrument-uses': 'M31-form-instrument',
    'M31-consumables': 'M31-form-consumable',
    'M31-burnin-sessions': 'M31-form-burnin',
    'M31-transfers': 'M31-form-transfer',
    'M31-timelogs': 'M31-form-clock',
  }
};
