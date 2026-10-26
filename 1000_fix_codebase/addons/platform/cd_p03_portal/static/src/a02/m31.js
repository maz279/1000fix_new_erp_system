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
      ['1', 'Repair Order Creation', 8],
      ['2', 'Workshop & Bench Master', 9],
      ['3', 'Bench Allocation & Queue', 10],
      ['4', 'Repair-Level Routing', 7],
      ['5', 'Diagnosis & Execution', 13],
      ['6', 'Parts Consumption & Genealogy', 8],
      ['7', 'Testing & Burn-In', 8],
      ['8', 'Rework & Transfers', 6],
      ['9', 'Repair Costing', 7]
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
  'M31-methods': { kind: 'table_report', module: 'M31', report: 'rework_loops', period: false }
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
