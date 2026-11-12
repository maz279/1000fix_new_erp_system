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
  forms: ['Receive Device into Workshop', 'Repair Order', 'Workshop Facility', 'Bench Allocation', 'Job Routing',
    'Bench Diagnosis', 'Part Fitment', 'Test Protocol Result', 'Labour & Cost'],
  cross: ['M01 device release', 'M15 parts consumption', 'M61 knowledge capture', 'M45 test equipment', 'M22 skill routing'],
  freg: {
    src: 76,
    sub: [
      /* A repair order is never typed from scratch (BRU-WSR-01): it is the
       * service order's hand-over, so the page's button picks the booked-in
       * order and runs that hand-over (FR-WSR-001/004). */
      ['1', 'Repair Order Creation', 8, { model: 'fix.workshop.job', cols: ['name', 'order_reference', 'workshop_id', 'priority', 'intake_date'], screens: ['M31-orders', 'M31-record'], reports: ['Repair Cycle Time by Level'], forms: ['Receive Device into Workshop', 'Repair Order'], create: 'M31-form-receive' }],
      ['2', 'Workshop & Bench Master', 9, { model: 'fix.workshop', cols: ['code', 'name', 'workshop_type', 'branch_id', 'bench_count'], screens: ['M31-benchmaster'], reports: ['Bench Utilisation by Workshop'], forms: ['Workshop Facility'] }],
      ['3', 'Bench Allocation & Queue', 10, { model: 'fix.workshop.bench', cols: ['code', 'name', 'state', 'current_job_count', 'technician_id'], screens: ['M31-benches'], reports: ['Bench Utilisation by Workshop'], forms: ['Bench Allocation'] }],
      /* routing, diagnosis, rework and costing act on a job already in the
       * workshop: each page picks the job, then captures its own part of it */
      ['4', 'Repair-Level Routing', 7, { model: 'fix.workshop.job', cols: ['name', 'repair_level', 'workshop_id', 'bench_id', 'state'], screens: ['M31-levels', 'M31-record'], reports: ['Repair Cycle Time by Level'], forms: ['Job Routing'], create: 'M31-form-routing' }],
      ['5', 'Diagnosis & Execution', 13, { model: 'fix.workshop.job', cols: ['name', 'device_serial', 'technician_id', 'bench_id', 'state'], screens: ['M31-diag', 'M31-methods'], reports: ['Internal Rework Loop Analysis'], forms: ['Bench Diagnosis'], create: 'M31-form-diagnosis', domain: [['state', 'in', ['diagnostic', 'waiting_parts', 'in_repair']]] }],
      ['6', 'Parts Consumption & Genealogy', 8, { model: 'fix.workshop.part.line', cols: ['job_id', 'part_number', 'lot_serial_number', 'quantity', 'source_origin'], screens: ['M31-parts'], reports: ['Parts Genealogy Trace'], forms: ['Part Fitment'] }],
      ['7', 'Testing & Burn-In', 8, { model: 'fix.workshop.job', cols: ['name', 'burn_in_started_at', 'burn_in_passed', 'qc_passed', 'state'], screens: ['M31-testing'], reports: ['Burn-In Failure Report'], forms: ['Test Protocol Result'], create: 'M31-form-evidence', domain: [['state', 'in', ['burn_in', 'qc_pending', 'qc_failed']]] }],
      ['8', 'Rework & Transfers', 6, { model: 'fix.workshop.job', cols: ['name', 'rework_of_id', 'rework_count', 'workshop_id', 'state'], screens: ['M31-transfer', 'M31-record'], reports: ['Internal Rework Loop Analysis', 'Bench Utilisation by Workshop'], forms: ['Job Routing'], create: 'M31-form-routing', domain: [['is_rework', '=', true]] }],
      ['9', 'Repair Costing', 7, { model: 'fix.workshop.job', cols: ['name', 'parts_total', 'labour_total', 'total_repair_cost', 'labor_efficiency_pct'], screens: ['M31-costing', 'M31-throughput'], reports: ['Workshop Cost per Repair', 'Repair Cycle Time by Level'], forms: ['Labour & Cost'], create: 'M31-form-labour' }]
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
      'burn_in_passed', 'qc_passed', 'is_rework', 'rework_count', 'parts_total', 'labour_total', 'total_repair_cost',
      'intake_date', 'completed_at'],
    stateField: 'state',
    actions: [...JOB_FLOW, ...JOB_EXCEPTIONS] },
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
          { name: 'rework_of_id', label: "Comeback Of Job", readonly: true }
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
          { name: 'labour_total', label: "Labour Cost Allocation (BDT)" },
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
    title: "Bench Allocation",
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
    title: "Test Protocol Result",
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
      { id: 'iso', label: '2. ISO 9001 EPA Certification', bn: '২. আইএসও ৯০০১ ও ইপিএ সনদ', icon: '📜', badge: '5' }
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
    newLabel: 'Route, Re-route or Transfer a Job',
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
        note: 'Confirm or revise the repair level after inspection. A higher level that raises the cost above the approved estimate needs the estimate re-approved in M01 before QC (BRU-WSR-11). For a workshop transfer, choose the receiving workshop and raise the consignment for the move in M03 Service Logistics.',
        fields: [
          { name: 'name', label: 'Job Reference', readonly: true },
          { name: 'order_reference', label: 'Service Order', readonly: true },
          { name: 'device_serial', label: 'Device Serial / IMEI', readonly: true },
          { name: 'state', label: 'Job State', readonly: true },
          { name: 'is_rework', label: 'Internal Rework', readonly: true },
          { name: 'rework_count', label: 'Rework Loops', readonly: true },
          { name: 'rework_reason', label: 'Why QC Failed', readonly: true },
          { name: 'repair_level', required: true, label: 'Repair Level (L1/L2/L3)' },
          { name: 'workshop_id', required: true, label: 'Workshop (receiving workshop for a transfer)' },
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
      cols: ['name', 'order_reference', 'repair_level', 'technician_id', 'labour_total', 'total_repair_cost', 'state'],
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
          { name: 'labour_total', label: 'Labour Cost (BDT)' },
          { name: 'labor_efficiency_pct', label: 'Labour Efficiency (%)', readonly: true },
          { name: 'parts_total', label: 'Parts Cost (BDT)', readonly: true },
          { name: 'total_repair_cost', label: 'Total Repair Cost (BDT)', readonly: true },
          { name: 'estimate_ceiling', label: 'Approved Amount (BDT)', readonly: true },
          { name: 'cost_over_estimate', label: 'Cost Above Approval', readonly: true }
        ] }
    ]
  },

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
  'M31:Bench Allocation': 'M31-form-bench',
  'M31:Job Routing': 'M31-form-routing',
  'M31:Bench Diagnosis': 'M31-form-diagnosis',
  'M31:Part Fitment': 'M31-form-part',
  'M31:Test Protocol Result': 'M31-form-evidence',
  'M31:Labour & Cost': 'M31-form-labour',
  'M31:__by_model__': {
    'fix.workshop.job': 'M31-form-job',
    'fix.workshop.bench': 'M31-form-bench',
    'fix.workshop.evidence': 'M31-form-evidence',
    'fix.workshop': 'M31-form-workshop',
    'fix.workshop.part.line': 'M31-form-part',
  },
  'M31:__by_screen__': {
    'M31-orders': 'M31-form-job',
    'M31-record': 'M31-form-job',
    'M31-diag': 'M31-form-job',
    'M31-testing': 'M31-form-job',
    'M31-benches': 'M31-form-bench',
    'M31-benchmaster': 'M31-form-workshop',
    'M31-parts': 'M31-form-part',
  }
};
