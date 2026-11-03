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
      { id: 'M31-record', en: 'Repair Order Record', bn: 'রিপেয়ার অর্ডার নথি', t: 'f' },
      { id: 'M31-transfer', en: 'Workshop Transfers', bn: 'ওয়ার্কশপ ট্রান্সফার', t: 'g' }
    ]},
    { en: 'Bench Board', screens: [
      { id: 'M31-benches', en: 'Bench & WIP Board', bn: 'বেঞ্চ ও ডাব্লিউআইপি বোর্ড', t: 'd' },
      { id: 'M31-benchmaster', en: 'Bench Master (Capacity)', bn: 'বেঞ্চ মাস্টার', t: 'g' },
      { id: 'M31-levels', en: 'L1/L2/L3 Classification', bn: 'এল১/এল২/এল৩ শ্রেণি', t: 'g' }
    ]},
    { en: 'Execution', screens: [
      { id: 'M31-diag', en: 'Component Diagnosis', bn: 'কম্পোনেন্ট ডায়াগনোসিস', t: 'g' },
      { id: 'M31-parts', en: 'Parts Consumption', bn: 'পার্টস ব্যবহার', t: 'g' },
      { id: 'M31-testing', en: 'Test Protocols & Burn-In', bn: 'টেস্ট ও বার্ন-ইন', t: 'g' }
    ]},
    { en: 'Costing & Knowledge', screens: [
      { id: 'M31-costing', en: 'Repair Costing', bn: 'মেরামত ব্যয়', t: 'r' },
      { id: 'M31-throughput', en: 'Throughput Analytics', bn: 'থ্রুপুট বিশ্লেষণ', t: 'r' },
      { id: 'M31-methods', en: 'Repair-Method Capture', bn: 'মেরামত পদ্ধতি', t: 'g' }
    ]}
  ],
  reports: ['Bench Utilisation by Workshop', 'Repair Cycle Time by Level', 'Internal Rework Loop Analysis', 'Workshop Cost per Repair', 'Parts Genealogy Trace', 'Burn-In Failure Report'],
  forms: ['Repair Order', 'Bench Allocation', 'Test Protocol Result', 'Workshop Transfer'],
  cross: ['M01 device release', 'M15 parts consumption', 'M61 knowledge capture', 'M45 test equipment', 'M22 skill routing'],
  freg: {
    src: 76,
    sub: [
      ['1', 'Repair Order Creation', 8, { model: 'fix.workshop.job', cols: ['name', 'order_reference', 'workshop_id', 'priority', 'intake_date'], screens: ['M31-orders', 'M31-record'] }],
      ['2', 'Workshop & Bench Master', 9, { model: 'fix.workshop', cols: ['code', 'name', 'workshop_type', 'branch_id', 'bench_count'], screens: ['M31-benchmaster'] }],
      ['3', 'Bench Allocation & Queue', 10, { model: 'fix.workshop.bench', cols: ['code', 'name', 'state', 'current_job_count', 'technician_id'], screens: ['M31-benches'] }],
      ['4', 'Repair-Level Routing', 7, { model: 'fix.workshop.job', cols: ['name', 'repair_level', 'workshop_id', 'bench_id', 'state'], screens: ['M31-levels', 'M31-record'] }],
      ['5', 'Diagnosis & Execution', 13, { model: 'fix.workshop.job', cols: ['name', 'device_serial', 'technician_id', 'bench_id', 'state'], screens: ['M31-diag', 'M31-methods'], domain: [['state', 'in', ['diagnostic', 'waiting_parts', 'in_repair']]] }],
      ['6', 'Parts Consumption & Genealogy', 8, { model: 'fix.workshop.part.line', cols: ['job_id', 'part_number', 'lot_serial_number', 'quantity', 'source_origin'], screens: ['M31-parts'] }],
      ['7', 'Testing & Burn-In', 8, { model: 'fix.workshop.job', cols: ['name', 'burn_in_started_at', 'burn_in_passed', 'qc_passed', 'state'], screens: ['M31-testing'], domain: [['state', 'in', ['burn_in', 'qc_pending', 'qc_failed']]] }],
      ['8', 'Rework & Transfers', 6, { model: 'fix.workshop.job', cols: ['name', 'rework_of_id', 'rework_count', 'workshop_id', 'state'], screens: ['M31-transfer', 'M31-record'], domain: [['is_rework', '=', true]] }],
      ['9', 'Repair Costing', 7, { model: 'fix.workshop.job', cols: ['name', 'parts_total', 'labour_total', 'total_repair_cost', 'labor_efficiency_pct'], screens: ['M31-costing', 'M31-throughput'] }]
    ]
  }
};

/* In-workspace data screens: model_list over the whitelisted cd_workshop
 * models; table_report over the module REPORTS. */
export const SCREENS = {
  'M31-orders': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'workshop_id', 'bench_id', 'technician_id', 'repair_level', 'priority', 'state'],
    stateField: 'state' },
  'M31-record': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'workshop_id', 'bench_id', 'technician_id', 'repair_level', 'state',
      'burn_in_passed', 'qc_passed', 'is_rework', 'rework_count', 'parts_total', 'labour_total', 'total_repair_cost',
      'intake_date', 'completed_at'],
    stateField: 'state' },
  'M31-transfer': { kind: 'table_report', module: 'M31', report: 'bench_utilisation', period: false },
  'M31-benches': { kind: 'model_list', model: 'fix.workshop.bench', create: false,
    cols: ['code', 'name', 'workshop_id', 'repair_level', 'state', 'current_job_count', 'max_concurrent_jobs', 'technician_id', 'is_esd_safe'],
    stateField: 'state' },
  'M31-benchmaster': { kind: 'model_list', model: 'fix.workshop', create: false,
    cols: ['code', 'name', 'workshop_type', 'branch_id', 'bench_count', 'available_bench_count', 'bench_utilization', 'active_job_count'] },
  'M31-levels': { kind: 'table_report', module: 'M31', report: 'cycle_time', period: false },
  'M31-diag': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'device_serial', 'repair_level', 'priority', 'state', 'technician_id', 'bench_id'],
    domain: [['state', 'in', ['intake', 'diagnostic']]],
    stateField: 'state' },
  'M31-parts': { kind: 'model_list', model: 'fix.workshop.part.line', create: false,
    cols: ['job_id', 'part_number', 'quantity', 'unit_cost', 'subtotal', 'lot_serial_number'] },
  'M31-testing': { kind: 'model_list', model: 'fix.workshop.job', create: false,
    cols: ['name', 'order_reference', 'repair_level', 'state', 'burn_in_started_at', 'burn_in_completed_at', 'burn_in_passed', 'qc_passed', 'qc_inspector_id'],
    domain: [['state', 'in', ['burn_in', 'qc_pending', 'qc_failed']]],
    stateField: 'state' },
  'M31-costing': { kind: 'table_report', module: 'M31', report: 'cost_per_repair', period: false },
  'M31-throughput': { kind: 'table_report', module: 'M31', report: 'cycle_time', period: false },
  'M31-methods': { kind: 'table_report', module: 'M31', report: 'rework_loops', period: false },

  /* ===== service data-entry forms (registry names) ===== */
  'M31-form-job': {
    kind: 'model_form',
    model: 'fix.workshop.job',
    title: "Repair Order",
    back: 'M31-jobs',
    status: { field: 'state', labels: { draft: "Draft", in_repair: "In Repair", burn_in: "Burn-In", qc: "QC", completed: "Completed", cancelled: "Cancelled" } },
    tabs: [
      { id: 'job', label: '1. Depot Job & Bench', bn: '১. ওয়ার্কশপ জব ও বেঞ্চ', icon: '🔧', badge: '7' },
      { id: 'soldering', label: '2. Schematic & IPC Rework', bn: '২. স্কিম্যাটিক ও মাইক্রো-সোল্ডারিং', icon: '🔍', badge: '7' },
      { id: 'burnin', label: '3. 240-Min Burn-In Gate', bn: '৩. ২৪০-মিনিট বার্ন-ইন যাচাই', icon: '🔥', badge: '6' },
      { id: 'labor', label: '4. SAM Labor Efficiency', bn: '৪. শ্রম দক্ষতা ও কস্টিং', icon: '⏱️', badge: '6' },
      { id: 'qc', label: '5. Quality & Evidence Pack', bn: '৫. কিউসি ও প্রমাণক', icon: '🛡️', badge: '6' }
    ],
    sections: [
      { tab: 'job', title: "Workshop Repair Job & Bench Routing", note: "A bench repair job. Parts and labour totals roll up from the job lines.",
        fields: [
          { name: 'name', required: true, label: "Job Reference", readonly: true },
          { name: 'order_id', label: "Service Order Reference" },
          { name: 'workshop_id', required: true, label: "Depot / Workshop Facility" },
          { name: 'repair_level', required: true, label: "Repair Capability Level (L1/L2/L3)" },
          { name: 'bench_id', label: "Assigned Workbench (ESD Compliant Today)" },
          { name: 'technician_id', label: "Assigned Depot Technician" },
          { name: 'priority', required: true, label: "Repair Priority Tier" },
          { name: 'device_serial', label: "Device Serial / IMEI" }
        ] },
      { tab: 'soldering', title: "IPC-7711/7721 Micro-Soldering & Component Diagnostics (FLAW-31.2 / HS-05)",
        note: "DC power rail measurements, boardview schematics, and IPC visual inspection verification.",
        fields: [
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
          { name: 'burn_in_actual_minutes', label: "Actual Logged Burn-In Minutes (>= 240m)" },
          { name: 'thermal_crash_count', label: "Thermal Crashes Observed (Must be 0)" },
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
          { name: 'dofa_writeoff_tier', label: "DOFA Scrap / BER Write-Off Tier" }
        ] },
      { tab: 'qc', title: "Independent Quality Control & Post-Rework Photos",
        fields: [
          { name: 'qc_passed', label: "Independent QC Inspection Passed", readonly: true },
          { name: 'qc_inspector_id', label: "Independent QC Inspector" },
          { name: 'qc_notes', label: "QC Inspection Findings", type: "text" },
          { name: 'post_rework_photo_attachment_id', label: "Post-Rework Finished Board Photo" },
          { name: 'is_rework', label: "Internal Rework Loop Active", readonly: true },
          { name: 'state', required: true, label: "Repair Job State" }
        ] }
    ]
  },
  'M31-form-bench': {
    kind: 'model_form',
    model: 'fix.workshop.bench',
    title: "Bench Allocation",
    back: 'M31-benches',
    status: { field: 'state', labels: { available: "Available", occupied: "Occupied", maintenance: "Maintenance", retired: "Retired" } },
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
          { name: 'name_bn', label: "নাম (বাংলা)" },
          { name: 'repair_level', required: true, label: "Repair Level Capability (L1/L2/L3)" },
          { name: 'technician_id', label: "Assigned Primary Technician" },
          { name: 'max_concurrent_jobs', label: "Maximum Concurrent Job Capacity" },
          { name: 'state', required: true, label: "Current Bench State" }
        ] },
      { tab: 'esd', title: "Daily ESD Mat & Wrist-Strap Telemetry Interlock (FLAW-31.2)",
        note: "ANSI/ESD S20.20 requires wrist strap < 35 MΩ and mat worksurface < 1000 MΩ logged daily.",
        fields: [
          { name: 'is_esd_safe', label: "ESD Protection Certified Station" },
          { name: 'wrist_strap_mohm', required: true, label: "Wrist Strap Resistance (< 35.0 MΩ)" },
          { name: 'worksurface_rtg_mohm', required: true, label: "Worksurface RTG Resistance (< 1000.0 MΩ)" },
          { name: 'esd_last_verified_date', required: true, label: "Daily ESD Verification Date" },
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
    back: 'M31-evidence',
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
          { name: 'captured_at', required: true, label: "Captured Timestamp" },
          { name: 'captured_by_id', label: "Captured By Technician" },
          { name: 'description', label: "Evidence Observations / Engineering Notes", type: "text" }
        ] },
      { tab: 'document', title: "cd_document_core Unified Storage Link (AS-01)",
        fields: [
          { name: 'document_id', required: true, label: "Governed Document Record" },
          { name: 'attachment_id', label: "Underlying Binary File Attachment", readonly: true },
          { name: 'isolation_tier', label: "Data Residency Isolation Tier", readonly: true }
        ] }
    ]
  },
  'M31-form-workshop': {
    kind: 'model_form',
    model: 'fix.workshop',
    title: "Workshop Transfer",
    back: 'M31-workshops',
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

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M31:Bench Utilisation by Workshop": "M31-benchmaster",
  "M31:Repair Cycle Time by Level": "M31-throughput",
  "M31:Internal Rework Loop Analysis": "M31-methods",
  "M31:Workshop Cost per Repair": "M31-costing",
  "M31:Parts Genealogy Trace": "M31-parts",
  "M31:Burn-In Failure Report": "M31-testing"
};

/* data-entry form chips: repair orders are created from the M01 service
 * order (bridge action); the rest arrive with their engines in later
 * phases and keep the honest toast. */
export const FORM_MODELS = {};

/* the module's "+ New" surface: no generic create — jobs start from the
 * service-order hand-over or the bench queue. */
export const CREATE = {};


export const FORM_CHIPS = {
  'M31:Repair Order': 'M31-form-job',
  'M31:Bench Allocation': 'M31-form-bench',
  'M31:Test Protocol Result': 'M31-form-evidence',
  'M31:Workshop Transfer': 'M31-form-workshop',
  'M31:__by_model__': {
    'fix.workshop.job': 'M31-form-job',
    'fix.workshop.bench': 'M31-form-bench',
    'fix.workshop.evidence': 'M31-form-evidence',
    'fix.workshop': 'M31-form-workshop',
  },
  'M31:__by_screen__': {
    'M31-jobs': 'M31-form-job',
    'M31-benches': 'M31-form-bench',
    'M31-evidence': 'M31-form-evidence',
    'M31-workshops': 'M31-form-workshop',
  }
};
