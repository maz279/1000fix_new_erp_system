/* =====================================================================
   1000 FiX ERP — NAV DATA part 3 of 3: Categories F–K
   (Assets & Facilities · Finance · People · Quality · Insights · Platform)
   ===================================================================== */
window.FX_MODULES && (function () {

/* ============ A07 · ASSET, EQUIPMENT & FACILITIES =================== */

/* ---------------- M17 DEVICE & CUSTOMER ASSET REGISTRY -------------- */
window.FX_MODULES.M17 = { area:'A07', en:'Device & Asset Registry', bn:'ডিভাইস রেজিস্ট্রি', icon:'📱', rail:'assets',
  desc:'Permanent identity per device — multi-identifier model, custody chain, service history, parts genealogy, estates.',
  kpis:[ {l:'Registered Devices',v:'2.84 M',spark:[2.1,2.24,2.38,2.52,2.66,2.76,2.84]},
          {l:'Corporate Estates',v:'284',st:'info'},
          {l:'Duplicate Rate',v:'1.2%',d:'−0.8pt',up:1,st:'ok'},
          {l:'Repeat-Fault Flags',v:'318',st:'warn'},
          {l:'Data Quality Score',v:'94.6%',st:'ok'},
          {l:'QR Labelled',v:'88.2%',st:'ok'} ],
  groups:[
    {en:'Registry', screens:[
      {id:'M17-assets', en:'Asset Register', bn:'অ্যাসেট রেজিস্টার', t:'g'},
      {id:'M17-asset', en:'Asset Record', bn:'অ্যাসেট নথি', t:'f'},
      {id:'M17-360', en:'Asset 360', bn:'অ্যাসেট ৩৬০', t:'x'},
      {id:'M17-identifiers', en:'Multi-Identifier Model', bn:'বহু-আইডেন্টিফায়ার', t:'g'},
      {id:'M17-merge', en:'Identity Resolution & Merge', bn:'আইডেন্টিটি মার্জ', t:'c'} ]},
    {en:'History', screens:[
      {id:'M17-history', en:'Service History', bn:'সেবা ইতিহাস', t:'r'},
      {id:'M17-genealogy', en:'Parts Genealogy', bn:'পার্টস বংশতালিকা', t:'g'},
      {id:'M17-rework', en:'Repeat-Fault Detection', bn:'পুনরাবৃত্ত ত্রুটি', t:'g'} ]},
    {en:'Custody', screens:[
      {id:'M17-custody', en:'Custody State & Chain', bn:'কাস্টডি শৃঙ্খল', t:'g'},
      {id:'M17-ownership', en:'Ownership & Transfers', bn:'মালিকানা', t:'g'} ]},
    {en:'Corporate Estates', screens:[
      {id:'M17-estates', en:'Estates (Site/Dept/User)', bn:'কর্পোরেট এস্টেট', t:'g'},
      {id:'M17-bulk', en:'Bulk Registration', bn:'বাল্ক নিবন্ধন', t:'c'} ]},
    {en:'Coverage', screens:[
      {id:'M17-wty', en:'Warranty Dates & Priority', bn:'ওয়রেন্টি তারিখ', t:'g'},
      {id:'M17-pm', en:'PM Plans', bn:'পিএম পরিকল্পনা', t:'g'} ]} ],
  reports:['Installed Base by Brand/Model','Repeat-Fault Pareto','Estate Coverage by Client','Custody Exceptions','Data Quality Scorecard'],
  forms:['Asset (6 identifiers)','Estate Assignment','Ownership Transfer','Condition Grading'],
  cross:['M01 every order links asset','M09 warranty evidence','M05 monitored assets','M48 telemetry streams','P01 customer devices'],
  freg:{ src:96, sub:[
    ['1','Identity & Resolution',14],['2','Configuration & Components',8],['3','Ownership & Custody',12],
    ['4','Service History',9],['5','Parts Genealogy',7],['6','Repeat-Fault Detection',6],
    ['7','Warranty Projection',7],['8','Corporate Estates',12],['9','Bulk Registration',7],
    ['10','Condition & EOL Routing',8],['11','Data Quality',6] ] } };

/* ---------------- M45 ENTERPRISE ASSET & TEST EQUIPMENT ---------------- */
window.FX_MODULES.M45 = { area:'A07', en:'Enterprise Assets & Test Equipment', bn:'এন্টারপ্রাইজ সম্পদ', icon:'🔬', rail:'assets',
  desc:'Test instruments & tools — calibration management, tool crib issue/return, fitness states, usage per job.',
  kpis:[ {l:'Equipment Items',v:'3,412',st:'info'},
          {l:'Calibration Due (30d)',v:'38',st:'warn'},
          {l:'Out-of-Service',v:'6',st:'err'},
          {l:'Calibration Compliance',v:'99.2%',st:'ok'},
          {l:'Tool Loss Rate',v:'0.4%',st:'ok'},
          {l:'Personal Issues',v:'418',st:'info'} ],
  groups:[
    {en:'Register', screens:[
      {id:'M45-register', en:'Equipment Register', bn:'সরঞ্জাম রেজিস্টার', t:'g'},
      {id:'M45-classes', en:'Classification', bn:'শ্রেণিবিভাগ', t:'g'},
      {id:'M45-kits', en:'Kit Management', bn:'কিট', t:'g'} ]},
    {en:'Custody', screens:[
      {id:'M45-issue', en:'Tool Crib Issue / Return', bn:'ইস্যু ও ফেরত', t:'g'},
      {id:'M45-transfer', en:'Transfers', bn:'স্থানান্তর', t:'g'},
      {id:'M45-audits', en:'Physical Verification', bn:'শারীরিক যাচাই', t:'c'} ]},
    {en:'Calibration', screens:[
      {id:'M45-calibration', en:'Calibration Schedule', bn:'ক্যালিব্রেশন সূচি', t:'g'},
      {id:'M45-certificates', en:'Certificates & Trace', bn:'সনদ', t:'g'},
      {id:'M45-oos', en:'Out-of-Service Enforcement', bn:'সেবাবহির', t:'g'},
      {id:'M45-retro', en:'Retrospective Impact', bn:'পূর্ববর্তী প্রভাব', t:'g'} ]},
    {en:'Maintenance', screens:[
      {id:'M45-pm', en:'PM & Corrective', bn:'পিএম', t:'g'},
      {id:'M45-usage', en:'Usage per Job/QC', bn:'ব্যবহার', t:'g'} ]} ],
  reports:['Calibration Compliance Report','Equipment Utilisation','Tool Loss & Write-Off','Cost of Ownership'],
  forms:['Equipment','Calibration Record','Issue/Return','Write-Off'],
  cross:['M31 bench equipment','M23 ISO 7.1.5 evidence','M21 custodians','M47 branch assets'],
  freg:{ src:64, sub:[
    ['1','Register & Classification',10],['2','Issue / Custody / Transfer',11],
    ['3','Kit Management',6],['4','Calibration Management',16],
    ['5','PM & Repair',8],['6','Usage Capture',6],['7','Verification & Loss',7] ] } },

/* ---------------- M46 FLEET & VEHICLE ------------------------------------- */
window.FX_MODULES.M46 = { area:'A07', en:'Fleet & Vehicles', bn:'ফ্লিট ও যানবাহন', icon:'🚚', rail:'assets',
  desc:'Vans & bikes — statutory documents with expiry control, fuel efficiency, telematics, cost per km.',
  kpis:[ {l:'Vehicles',v:'214',st:'info'},
          {l:'Fitness Expiring (30d)',v:'7',st:'warn'},
          {l:'Off-Road',v:'3',st:'warn'},
          {l:'Fuel Efficiency Var.',v:'+2.4%',st:'ok'},
          {l:'Cost / km',v:'৳ 18.6',d:'−৳ 0.8',up:1,st:'ok'},
          {l:'Accidents YTD',v:'4',st:'info'} ],
  groups:[
    {en:'Register', screens:[
      {id:'M46-vehicles', en:'Vehicle Register', bn:'যানবাহন রেজিস্টার', t:'g'},
      {id:'M46-drivers', en:'Driver Register', bn:'চালক রেজিস্টার', t:'g'},
      {id:'M46-assign', en:'Assignment & Pool', bn:'নিয়োগ', t:'g'} ]},
    {en:'Statutory', screens:[
      {id:'M46-docs', en:'Documents & Expiry', bn:'দলিল ও মেয়াদ', t:'g'},
      {id:'M46-renewal', en:'Renewal & Off-Road', bn:'নবায়ন', t:'c'} ]},
    {en:'Operations', screens:[
      {id:'M46-preuse', en:'Daily Pre-Use Checks', bn:'প্রাক-ব্যবহার যাচাই', t:'g'},
      {id:'M46-pm', en:'PM by Odometer', bn:'পিএম', t:'g'},
      {id:'M46-fuel', en:'Fuel & Efficiency', bn:'জ্বালানি', t:'g'},
      {id:'M46-telematics', en:'Telematics Health', bn:'টেলিমেটিক্স', t:'g'} ]},
    {en:'Safety & Cost', screens:[
      {id:'M46-accidents', en:'Accidents & Insurance', bn:'দুর্ঘটনা', t:'g'},
      {id:'M46-behaviour', en:'Driver Behaviour', bn:'চালক আচরণ', t:'r'},
      {id:'M46-cost', en:'Cost per Kilometre', bn:'প্রতি কিমি ব্যয়', t:'r'} ]} ],
  reports:['Fleet Availability','Fuel Efficiency Trend','Maintenance Cost per Vehicle','Statutory Compliance Register','Incident Summary'],
  forms:['Vehicle','Driver','Fuel Transaction','Accident Report','PM Service'],
  cross:['M03 rider fleet','M02 field vans','M52 fuel expenses','M47 site vehicles'],
  freg:{ src:62, sub:[
    ['1','Vehicle Register',8],['2','Statutory Documents',9],['3','Drivers',8],
    ['4','Assignment & Pool',6],['5','Pre-Use & PM',9],['6','Fuel & Odometer',8],
    ['7','Telematics',5],['8','Accidents & Insurance',9] ] } },

/* ---------------- M47 FACILITY & BRANCH INFRASTRUCTURE --------------------- */
window.FX_MODULES.M47 = { area:'A07', en:'Facility & Branch Infrastructure', bn:'সুবিধা ও শাখা', icon:'🏬', rail:'assets',
  desc:'51+ sites — lease administration, statutory licences, utilities, branch infrastructure, safety equipment.',
  kpis:[ {l:'Sites',v:'53',st:'info'},
          {l:'Lease Renewals (90d)',v:'4',st:'warn'},
          {l:'Licence Gaps',v:'0',st:'ok'},
          {l:'Utilities Cost /sqft',v:'৳ 96',d:'−৳ 4',up:1,st:'ok'},
          {l:'Open Facility Work Orders',v:'27',st:'info'},
          {l:'Safety Inspections',v:'100%',st:'ok'} ],
  groups:[
    {en:'Sites', screens:[
      {id:'M47-sites', en:'Site Register', bn:'সাইট রেজিস্টার', t:'g'},
      {id:'M47-occupancy', en:'Occupancy & Condition', bn:'দখল ও অবস্থা', t:'r'} ]},
    {en:'Leases', screens:[
      {id:'M47-leases', en:'Lease Administration', bn:'লিজ প্রশাসন', t:'g'},
      {id:'M47-dates', en:'Critical-Date Control', bn:'গুরুত্বপূর্ণ তারিখ', t:'g'} ]},
    {en:'Compliance', screens:[
      {id:'M47-licences', en:'Statutory Licences', bn:'আইনি লাইসেন্স', t:'g'},
      {id:'M47-utilities', en:'Utilities & Anomalies', bn:'ইউটিলিটি', t:'g'} ]},
    {en:'Infrastructure', screens:[
      {id:'M47-infra', en:'Branch Asset Register', bn:'শাখা সম্পদ', t:'g'},
      {id:'M47-pm', en:'Building Services PM', bn:'ভবন সেবা', t:'g'},
      {id:'M47-wo', en:'Facility Work Orders', bn:'সুবিধা কাজ', t:'g'} ]},
    {en:'Safety', screens:[
      {id:'M47-safety', en:'Safety Equipment', bn:'নিরাপত্তা সরঞ্জাম', t:'g'},
      {id:'M47-security', en:'Security & Incidents', bn:'নিরাপত্তা ঘটনা', t:'g'},
      {id:'M47-opening', en:'Site Open / Close Projects', bn:'সাইট খোলা/বন্ধ', t:'c'} ]} ],
  reports:['Cost per Site / per Job','Lease Expiry Register','Licence Compliance','Utilities Variance','Facility Work Order Performance'],
  forms:['Site','Lease','Licence','Facility Work Order','Safety Inspection'],
  cross:['M04 branch operations','M30 branch provisioning','M49 ROU assets','M59 safety committee'],
  freg:{ src:71, sub:[
    ['1','Site Register',7],['2','Lease Administration',11],['3','Statutory Compliance',9],
    ['4','Utilities',6],['5','Infrastructure Assets',9],['6','Building PM',7],
    ['7','Work Orders',6],['8','Safety & Security',10],['9','Open / Close Projects',6] ] } },

/* ---------------- M48 IOT TELEMETRY ------------------------------------------ */
window.FX_MODULES.M48 = { area:'A07', en:'IoT Telemetry & Predictive', bn:'আইওটি ও পূর্বাভাস', icon:'📡', rail:'assets',
  desc:'TimescaleDB hypertables, threshold alerting, asset health scoring, failure prediction, prescriptive routing.',
  kpis:[ {l:'Streams Ingesting',v:'12,418',spark:[9200,9860,10420,11040,11560,12000,12418]},
          {l:'Ingest Rate',v:'2.1 K/s',st:'ok'},
          {l:'Open Alerts',v:'42',st:'warn'},
          {l:'Prediction Precision',v:'84.2%',st:'ok'},
          {l:'Prescriptive Actions',v:'18',st:'info'},
          {l:'Retention Compression',v:'91.4%',st:'ok'} ],
  groups:[
    {en:'Ingestion', screens:[
      {id:'M48-streams', en:'Stream Registry', bn:'স্ট্রিম রেজিস্টার', t:'g'},
      {id:'M48-adapters', en:'Protocol Adapters', bn:'প্রোটোকল অ্যাডাপ্টার', t:'g'},
      {id:'M48-health', en:'Pipeline Observability', bn:'পাইপলাইন', t:'d'} ]},
    {en:'Alerting', screens:[
      {id:'M48-alerts', en:'Threshold Alerts', bn:'থ্রেশহোল্ড অ্যালার্ট', t:'g'},
      {id:'M48-lifecycle', en:'Alert Lifecycle', bn:'অ্যালার্ট জীবনচক্র', t:'g'} ]},
    {en:'Intelligence', screens:[
      {id:'M48-scores', en:'Asset Health Scoring', bn:'অ্যাসেট স্বাস্থ্য', t:'d'},
      {id:'M48-failure', en:'Failure Prediction', bn:'ব্যর্থতা পূর্বাভাস', t:'g'},
      {id:'M48-rul', en:'RUL Estimation', bn:'অবশিষ্ট আয়ু', t:'r'},
      {id:'M48-routing', en:'Prescriptive Routing', bn:'নির্দেশনামূলক রুটিং', t:'g'} ]},
    {en:'Governance', screens:[
      {id:'M48-consent', en:'Consent & Access Control', bn:'সম্মতি', t:'g'} ]} ],
  reports:['Telemetry Coverage','Alert Storm Analysis','Prediction Outcome Tracking','Stream Quality Report'],
  forms:['Stream Binding','Alert Rule','Downsampling Policy'],
  cross:['M17 asset binding','M26 prediction models','M05 MSP monitoring','M01 prescriptive work orders'],
  freg:{ src:51, sub:[
    ['1','Stream Registry & Onboarding',8],['2','Protocol Adapters',7],['3','Ingestion & Storage',9],
    ['4','Threshold Alerting',8],['5','Health Scoring',6],['6','Failure Prediction',7],
    ['7','Prescriptive Routing',6] ] } },

/* ============ A08 · FINANCE & TREASURY =============================== */

/* ---------------- M19 FINANCIAL ACCOUNTING & GL -------------------------- */
window.FX_MODULES.M19 = { area:'A08', en:'Financial Accounting & GL', bn:'আর্থিক হিসাব', icon:'💰', rail:'finance',
  desc:'Chart of accounts, 7-dimension model, subledger posting engine, July–June close, statutory statements.',
  kpis:[ {l:'Revenue MTD',v:'৳ 12.42 Cr',d:'+8.4%',up:1,spark:[9.2,9.8,10.4,10.9,11.5,12.0,12.42]},
          {l:'Gross Margin',v:'44.6%',d:'+1.2pt',up:1,st:'ok',spark:[40,41,42,43,43.6,44.2,44.6]},
          {l:'Close Progress',v:'Day 2 of 3',st:'ok'},
          {l:'Unposted Subledgers',v:'0',st:'ok'},
          {l:'TB Imbalance',v:'৳ 0',st:'ok'},
          {l:'Journals MTD',v:'48,214',st:'info'} ],
  groups:[
    {en:'Ledger', screens:[
      {id:'M19-coa', en:'Chart of Accounts', bn:'হিসাবের ছক', t:'g'},
      {id:'M19-journals', en:'Journals', bn:'জার্নাল', t:'g'},
      {id:'M19-je', en:'Journal Entry', bn:'জার্নাল এন্ট্রি', t:'f'},
      {id:'M19-tb', en:'Trial Balance', bn:'ট্রায়াল ব্যালান্স', t:'r'},
      {id:'M19-dimensions', en:'7-Dimension Model', bn:'মাত্রা মডেল', t:'g'} ]},
    {en:'Close', screens:[
      {id:'M19-close', en:'Month-End Close Console', bn:'মাসিক ক্লোজ', t:'c'},
      {id:'M19-periods', en:'Periods & Locks', bn:'পিরিয়ড', t:'g'} ]},
    {en:'Statements', screens:[
      {id:'M19-bs', en:'Balance Sheet', bn:'উত্তরপত্র', t:'r'},
      {id:'M19-pl', en:'Profit & Loss', bn:'লাভ-ক্ষতি', t:'r'},
      {id:'M19-cf', en:'Cash Flow', bn:'নগদ প্রবাহ', t:'r'},
      {id:'M19-consol', en:'Consolidation', bn:'সমন্বয়', t:'r'} ]},
    {en:'Controls', screens:[
      {id:'M19-suspense', en:'Suspense & Control Accounts', bn:'সাসপেন্স', t:'g'},
      {id:'M19-recon', en:'Subledger vs Control', bn:'উপ-খতিয়ান মিলকরণ', t:'c'},
      {id:'M19-audit', en:'Immutable Audit Trail', bn:'নিরবচ্ছিন্ন অডিট', t:'g'} ]} ],
  reports:['Trial Balance','P&L (BFRS)','Balance Sheet','Cash Flow','Dimensional P&L by Branch','Close Checklist Report'],
  forms:['Journal Entry (manual/recurring)','Allocation Rule','Intercompany Charge'],
  cross:['Every subledger posts here','M20/M52 AR/AP','M51 tax postings','M56 payroll cost'],
  freg:{ src:91, sub:[
    ['1','CoA & Dimensions',12],['2','Journals',11],['3','Subledger Posting Engine',12],
    ['4','Fiscal Calendar & Close',10],['5','Multi-Entity & Consolidation',9],
    ['6','Multi-Currency',7],['7','Statutory Statements',9],['8','Audit & Retention',7],
    ['9','Accrual Framework',8],['10','Controls & SoD',6] ] } },

/* ---------------- M20 AR, INVOICING & COLLECTIONS ------------------------- */
window.FX_MODULES.M20 = { area:'A08', en:'AR, Invoicing & Collections', bn:'প্রাপ্য ও ইনভয়েসিং', icon:'🧾', rail:'finance',
  desc:'Billable events from every module, Mushak 6.3 invoices, bKash/Nagad/card receipts, dunning, ageing.',
  kpis:[ {l:'Invoices MTD',v:'38,412',st:'info',spark:[31200,32400,33800,35200,36600,37600,38412]},
          {l:'DSO',v:'29 d',d:'−3 d',up:1,st:'ok',spark:[42,39,36,34,32,30,29]},
          {l:'Auto-Generated',v:'100%',st:'ok'},
          {l:'Within 1h of Closure',v:'97.6%',st:'ok'},
          {l:'Overdue > 60d',v:'৳ 84 L',st:'warn'},
          {l:'Credit Notes',v:'1.2%',st:'ok'} ],
  groups:[
    {en:'Invoicing', screens:[
      {id:'M20-invoices', en:'Customer Invoices', bn:'গ্রাহক ইনভয়েস', t:'g'},
      {id:'M20-invoice', en:'Invoice (Mushak 6.3)', bn:'মুশক ৬.৩', t:'f'},
      {id:'M20-events', en:'Billable Events', bn:'বিলযোগ্য ঘটনা', t:'g'},
      {id:'M20-consolidated', en:'Consolidated Corporate Invoices', bn:'সমন্বিত ইনভয়েস', t:'g'},
      {id:'M20-brand', en:'Brand Claim Invoices', bn:'ব্র্যান্ড ইনভয়েস', t:'g'} ]},
    {en:'Receipts', screens:[
      {id:'M20-receipts', en:'Receipts (All Methods)', bn:'রিসিট', t:'g'},
      {id:'M20-links', en:'Payment Links', bn:'পেমেন্ট লিংক', t:'g'},
      {id:'M20-allocation', en:'Matching & Allocation', bn:'মিলকরণ', t:'c'} ]},
    {en:'Credit Control', screens:[
      {id:'M20-credit', en:'Limits, Terms & Holds', bn:'ক্রেডিট নিয়ন্ত্রণ', t:'g'},
      {id:'M20-dunning', en:'Dunning Worklist', bn:'দেনা আদায়', t:'c'},
      {id:'M20-disputes', en:'Disputes', bn:'বিরোধ', t:'g'},
      {id:'M20-refunds', en:'Credit Notes & Refunds', bn:'ক্রেডিট নোট', t:'g'} ]},
    {en:'Analysis', screens:[
      {id:'M20-aging', en:'AR Ageing', bn:'বয়স্ক প্রাপ্য', t:'r'},
      {id:'M20-leakage', en:'Revenue-Leakage Detection', bn:'রাজস্ব ক্ষয়', t:'r'},
      {id:'M20-statements', en:'Customer Statements', bn:'গ্রাহক স্টেটমেন্ট', t:'r'} ]} ],
  reports:['AR Ageing by Segment','Dunning Effectiveness','Payment Method Mix','Invoice Accuracy','Brand Receivable Ageing','Collections Productivity'],
  forms:['Invoice Request','Receipt','Credit Note','Refund','Payment Link'],
  cross:['M19 GL postings','M39 subscription billing','M51 Mushak compliance','M50 gateway settlement'],
  freg:{ src:99, sub:[
    ['1','Billable-Event Intake',12],['2','Invoice Assembly',12],['3','Mushak 6.3 Rendering',8],
    ['4','Delivery Channels',6],['5','Receipt Capture (8 methods)',14],['6','Matching & Allocation',11],
    ['7','Credit Control',9],['8','Dunning & Collections',12],['9','Credit Notes & Refunds',8],
    ['10','Leakage Detection',7] ] } },

/* ---------------- M52 AP & EMPLOYEE EXPENSE ------------------------------ */
window.FX_MODULES.M52 = { area:'A08', en:'AP & Employee Expense', bn:'প্রদেয় ও ব্যয়', icon:'💸', rail:'finance',
  desc:'Vendor invoices with 3-way match, TDS/VDS at source, employee expenses & advances, payment runs.',
  kpis:[ {l:'Payables Open',v:'৳ 6.84 Cr',st:'info'},
          {l:'Match Exceptions',v:'14',st:'warn'},
          {l:'TDS MTD',v:'৳ 12.4 L',st:'info'},
          {l:'Expense Claims Pending',v:'62',st:'warn'},
          {l:'Duplicate Catches YTD',v:'38',st:'ok'},
          {l:'Discounts Captured',v:'৳ 4.2 L',st:'ok'} ],
  groups:[
    {en:'Vendor Payables', screens:[
      {id:'M52-bills', en:'Vendor Bills', bn:'বিক্রেতার বিল', t:'g'},
      {id:'M52-match', en:'Match Exceptions', bn:'মিল ব্যতিক্রম', t:'g'},
      {id:'M52-approval', en:'Approval Workflow', bn:'অনুমোদন', t:'c'} ]},
    {en:'Payments', screens:[
      {id:'M52-runs', en:'Payment Runs', bn:'পেমেন্ট রান', t:'c'},
      {id:'M52-tds', en:'TDS / VDS at Source', bn:'উৎসে কর', t:'g'},
      {id:'M52-notes', en:'Debit / Credit Notes', bn:'ডেবিট নোট', t:'g'} ]},
    {en:'Employee Expense', screens:[
      {id:'M52-claims', en:'Expense Claims', bn:'খরচের দাবি', t:'g'},
      {id:'M52-advances', en:'Advances & Floats', bn:'অগ্রিম', t:'g'},
      {id:'M52-perdiem', en:'Per-Diem & Mileage', bn:'ভাতা ও মাইলেজ', t:'g'},
      {id:'M52-policy', en:'Expense Policy', bn:'নীতি', t:'g'} ]},
    {en:'Analysis', screens:[
      {id:'M52-aging', en:'AP Ageing', bn:'প্রদেয় বয়স', t:'r'},
      {id:'M52-grni', en:'GRNI Accruals', bn:'জিআরএনআই', t:'r'} ]} ],
  reports:['AP Ageing','TDS Deduction Register','Payment Run Summary','Expense by Category','GRNI Reconciliation','Duplicate Prevention Log'],
  forms:['Vendor Bill','Expense Claim','Employee Advance','Debit Note'],
  cross:['M16 3-way match','M50 payment execution','M51 TDS/VDS','M21 employee masters'],
  freg:{ src:82, sub:[
    ['1','Invoice Capture',10],['2','Matching',11],['3','Approval',8],
    ['4','Payable Ledger',8],['5','Payment Runs',9],['6','TDS/VDS',9],
    ['7','Employee Expenses',14],['8','Advances & Cards',8],['9','GRNI',5] ] } },

/* ---------------- M50 TREASURY, CASH & BANKING ---------------------------- */
window.FX_MODULES.M50 = { area:'A08', en:'Treasury & Banking', bn:'কোষাগার ও ব্যাংক', icon:'🏦', rail:'finance',
  desc:'Bank reconciliation, branch cash consolidation, rider COD, gateway/MFS settlement, BEFTN/RTGS execution.',
  kpis:[ {l:'Cash Position',v:'৳ 18.4 Cr',d:'+৳ 1.2 Cr',up:1,spark:[12.4,13.6,14.8,15.9,16.8,17.6,18.4]},
          {l:'Auto-Match Rate',v:'94.2%',st:'ok',spark:[82,85,87,89,91,93,94.2]},
          {l:'Branch Cash Uncollected',v:'৳ 84 L',st:'warn'},
          {l:'Recon Exceptions',v:'32',st:'warn'},
          {l:'Gateway Settle Lag',v:'T+1',st:'ok'},
          {l:'13-Week Forecast',v:'positive',st:'ok'} ],
  groups:[
    {en:'Cash', screens:[
      {id:'M50-position', en:'Consolidated Cash Position', bn:'নগদ অবস্থান', t:'d'},
      {id:'M50-branchcash', en:'Branch Cash Consolidation', bn:'শাখা নগদ', t:'c'},
      {id:'M50-ridercod', en:'Rider COD Settlement', bn:'রাইডার সিওডি', t:'c'},
      {id:'M50-petty', en:'Petty Cash (Imprest)', bn:'খরচি নগদ', t:'g'} ]},
    {en:'Banking', screens:[
      {id:'M50-accounts', en:'Bank Account Master', bn:'ব্যাংক হিসাব', t:'g'},
      {id:'M50-statements', en:'Statements Import', bn:'স্টেটমেন্ট', t:'g'},
      {id:'M50-recon', en:'Auto Reconciliation', bn:'স্বয়ংক্রিয় মিলকরণ', t:'c'} ]},
    {en:'Execution', screens:[
      {id:'M50-beftn', en:'BEFTN / RTGS Instructions', bn:'বিইএফটিএন', t:'g'},
      {id:'M50-cheques', en:'Cheque Management', bn:'চেক', t:'g'},
      {id:'M50-mfs', en:'MFS Disbursement', bn:'এমএফএস বিতরণ', t:'g'} ]},
    {en:'Settlement', screens:[
      {id:'M50-gateway', en:'Gateway / MFS Settlement', bn:'গেটওয়ে সেটেলমেন্ট', t:'c'},
      {id:'M50-cit', en:'Cash-in-Transit', bn:'নগদ পরিবহন', t:'g'} ]},
    {en:'Planning', screens:[
      {id:'M50-forecast', en:'Cash-Flow Forecast', bn:'নগদ প্রবাহ পূর্বাভাস', t:'r'},
      {id:'M50-facilities', en:'Facilities & Covenants', bn:'সুবিধা ও চুক্তি', t:'g'},
      {id:'M50-fx', en:'FX Holdings', bn:'বৈদেশিক মুদ্রা', t:'g'} ]} ],
  reports:['Daily Cash Position','Bank Reconciliation Summary','Gateway Settlement Reconciliation','COD Settlement Report','13-Week Cash Forecast','Bank Charges Analysis'],
  forms:['Bank Statement Import','Payment Instruction','Cash Deposit','Imprest Top-Up'],
  cross:['M04 branch drawers','M03 rider COD','M20 receipts','M52 payment runs','M44 trade finance'],
  freg:{ src:88, sub:[
    ['1','Bank Masters',7],['2','Statement & Recon',13],['3','Cash Position & Consolidation',12],
    ['4','Payment Execution',13],['5','Gateway/MFS Settlement',11],['6','Forecasting',8],
    ['7','Facilities & Trade Finance',12],['8','FX',5],['9','Controls',7] ] } },

/* ---------------- M51 TAX & REGULATORY (BANGLADESH) ------------------------ */
window.FX_MODULES.M51 = { area:'A08', en:'Tax & Regulatory (BD)', bn:'কর ও ভ্যাট', icon:'🏛️', rail:'finance',
  desc:'VAT 15%, Mushak 6.1–9.1 registers & returns, TDS/VDS, challans, NID capture, statutory calendar.',
  kpis:[ {l:'VAT Payable MTD',v:'৳ 1.42 Cr',st:'info'},
          {l:'Mushak 9.1 Status',v:'on track',st:'ok'},
          {l:'Input Credit Tracked',v:'৳ 38.4 L',st:'ok'},
          {l:'TDS Certificates Due',v:'124',st:'warn'},
          {l:'High-Value NID Gaps',v:'0',st:'ok'},
          {l:'Filing On-Time YTD',v:'100%',st:'ok'} ],
  groups:[
    {en:'VAT', screens:[
      {id:'M51-mushak61', en:'Mushak 6.1 (Purchases)', bn:'মুশক ৬.১', t:'g'},
      {id:'M51-mushak62', en:'Mushak 6.2 (Sales)', bn:'মুশক ৬.২', t:'g'},
      {id:'M51-mushak63', en:'Mushak 6.3 Records', bn:'মুশক ৬.৩', t:'g'},
      {id:'M51-vat91', en:'VAT Return 9.1 Filing', bn:'ভ্যাট রিটার্ন ৯.১', t:'c'},
      {id:'M51-challans', en:'Challans (A-Challan)', bn:'চালান', t:'g'},
      {id:'M51-input', en:'Input Credit Tracking', bn:'ইনপুট ক্রেডিট', t:'g'} ]},
    {en:'Withholding', screens:[
      {id:'M51-tds', en:'TDS Register', bn:'টিডিএস রেজিস্টার', t:'g'},
      {id:'M51-vds', en:'VDS (45 Services)', bn:'ভিডিএস', t:'g'},
      {id:'M51-certs', en:'Certificates', bn:'সনদ', t:'g'} ]},
    {en:'Compliance', screens:[
      {id:'M51-determination', en:'Tax Determination Service', bn:'কর নির্ধারণ', t:'c'},
      {id:'M51-nid', en:'High-Value NID Capture', bn:'এনআইডি সংগ্রহ', t:'g'},
      {id:'M51-calendar', en:'Statutory Calendar', bn:'বিধিবদ্ধ ক্যালেন্ডার', t:'c'},
      {id:'M51-audit', en:'Audit Support Pack', bn:'অডিট সহায়তা', t:'r'} ]} ],
  reports:['Mushak 9.1 Return Draft','VAT Reconciliation','TDS Annual Summary','SD & AT Liability','Marketplace VAT Model','Statutory Compliance Calendar'],
  forms:['Mushak 6.3 Entry','TDS Entry','Challan','Tax Adjustment'],
  cross:['M20 invoice taxation','M52 TDS at source','M12 marketplace model','M19 GL postings'],
  freg:{ src:78, sub:[
    ['1','Determination Service',9],['2','VAT Output/Input',12],['3','Mushak Registers',11],
    ['4','VAT Return 9.1',8],['5','VDS',7],['6','TDS',12],['7','Challans & Certificates',7],
    ['8','NID & Cash Controls',4],['9','Calendar & Audit',8] ] } },

/* ---------------- M53 REVENUE RECOGNITION & SETTLEMENT --------------------- */
window.FX_MODULES.M53 = { area:'A08', en:'Revenue Recognition & Settlement', bn:'রাজস্ব ও নিষ্পত্তি', icon:'📊', rail:'finance',
  desc:'Performance obligations, contract balances, commission ledger, seller/partner payouts, clawbacks, escrow.',
  kpis:[ {l:'Deferred Revenue',v:'৳ 14.2 Cr',st:'info'},
          {l:'Recognised MTD',v:'৳ 11.8 Cr',st:'info'},
          {l:'Commission Accrued',v:'৳ 32.4 L',st:'info'},
          {l:'Payout Runs MTD',v:'2',st:'ok'},
          {l:'Clawbacks',v:'৳ 1.8 L',st:'warn'},
          {l:'Settlement Accuracy',v:'100%',st:'ok'} ],
  groups:[
    {en:'Revenue', screens:[
      {id:'M53-obligations', en:'Performance Obligations', bn:'পারফরম্যান্স বাধ্যবাধকতা', t:'g'},
      {id:'M53-schedules', en:'Revenue Schedules', bn:'রাজস্ব সূচি', t:'g'},
      {id:'M53-contract', en:'Contract Assets & Liabilities', bn:'চুক্তি সম্পদ', t:'r'} ]},
    {en:'Commission', screens:[
      {id:'M53-ledger', en:'Commission Ledger', bn:'কমিশন লেজার', t:'g'},
      {id:'M53-schemes', en:'Commission Schemes', bn:'কমিশন কর্মসূচি', t:'g'} ]},
    {en:'Settlements', screens:[
      {id:'M53-payouts', en:'Payout Runs', bn:'পেআউট রান', t:'c'},
      {id:'M53-sellers', en:'Seller Statements', bn:'বিক্রেতা বিবৃতি', t:'r'},
      {id:'M53-partners', en:'Partner / Referral Payouts', bn:'পার্টনার পেআউট', t:'g'},
      {id:'M53-escrow', en:'Escrow & Clawbacks', bn:'এসক্রো', t:'g'} ]} ],
  reports:['Deferred Revenue Bridge','Rev-Rec by Stream','Commission Accrual','Payout Reconciliation','Clawback Register'],
  forms:['Revenue Schedule','Payout Run','Clawback','Commission Scheme'],
  cross:['M39 subscriptions','M08 contract schedules','M12 seller payouts','M40 partner rebates'],
  freg:{ src:74, sub:[
    ['1','Performance Obligations',10],['2','Allocation & SSP',8],['3','Schedules & Triggers',12],
    ['4','Modifications & Reversals',8],['5','Principal vs Agent',5],['6','Commission Ledger',8],
    ['7','Seller Settlement',10],['8','Partner Payouts',7],['9','Escrow & Clawbacks',6] ] } },

/* ---------------- M49 FIXED ASSETS ------------------------------------------ */
window.FX_MODULES.M49 = { area:'A08', en:'Fixed Assets & Capex', bn:'স্থায়ী সম্পদ ও ক্যাপেক্স', icon:'🏗️', rail:'finance',
  desc:'Capex requests to retirement — CWIP, dual-book depreciation (accounting + tax Third Schedule), verification.',
  kpis:[ {l:'Gross Block',v:'৳ 42.6 Cr',st:'info'},
          {l:'CWIP',v:'৳ 3.2 Cr',st:'warn'},
          {l:'NBV',v:'৳ 28.4 Cr',st:'info'},
          {l:'Capex Requests Open',v:'11',st:'warn'},
          {l:'Depreciation Run',v:'done (Sep)',st:'ok'},
          {l:'Verification Coverage',v:'96.4%',st:'ok'} ],
  groups:[
    {en:'Capex', screens:[
      {id:'M49-requests', en:'Capex Requests', bn:'ক্যাপেক্স অনুরোধ', t:'g'},
      {id:'M49-budget', en:'Capital Budget', bn:'মূলধনী বাজেট', t:'g'} ]},
    {en:'Register', screens:[
      {id:'M49-register', en:'Asset Register', bn:'সম্পদ রেজিস্টার', t:'g'},
      {id:'M49-cwip', en:'CWIP Tracking', bn:'সিডব্লিউআইপি', t:'g'},
      {id:'M49-transfer', en:'Transfers & Custodians', bn:'স্থানান্তর', t:'g'} ]},
    {en:'Depreciation', screens:[
      {id:'M49-dep', en:'Dual-Book Depreciation', bn:'দ্বৈত অবচয়', t:'c'},
      {id:'M49-schedules', en:'Schedules & Movements', bn:'সূচি', t:'r'} ]},
    {en:'Lifecycle', screens:[
      {id:'M49-impairment', en:'Revaluation & Impairment', bn:'পুনর্মূল্যায়ন', t:'g'},
      {id:'M49-disposal', en:'Disposal & Write-Off', bn:'নিষ্পত্তি', t:'g'},
      {id:'M49-verify', en:'Physical Verification', bn:'শারীরিক যাচাই', t:'c'} ]} ],
  reports:['Fixed Asset Movement Schedule','Depreciation (Dual Book)','NBV by Category','Capex vs Budget','Disposal Gains/Losses'],
  forms:['Capex Request','Asset Capitalisation','Transfer','Disposal'],
  cross:['M19 capitalisation postings','M47 branch capex','M45 equipment class','M66 IT assets'],
  freg:{ src:66, sub:[
    ['1','Capex & Approval',9],['2','Register & Capitalisation',11],['3','Componentisation',5],
    ['4','Dual-Book Depreciation',12],['5','Revaluation & Impairment',7],
    ['6','Transfers & Custody',6],['7','Verification & Tagging',7],['8','Disposal',9] ] } },

/* ---------------- M54 COSTING, BUDGETING & FP&A ------------------------------ */
window.FX_MODULES.M54 = { area:'A08', en:'Costing, Budget & FP&A', bn:'ব্যয়, বাজেট ও এফপিএ', icon:'🧮', rail:'finance',
  desc:'Allocation cycles, job & contract costing, 14-stream business-line profitability, branch league, budgets.',
  kpis:[ {l:'Branch League #1',v:'Dhanmondi',st:'ok'},
          {l:'Negative-Margin Branches',v:'1',st:'warn'},
          {l:'Budget Variance',v:'+2.4%',st:'ok'},
          {l:'Job Costing Coverage',v:'100%',st:'ok'},
          {l:'Technician Cost/hr',v:'৳ 412',st:'info'},
          {l:'Forecast Cycle',v:'Rolling 12M',st:'ok'} ],
  groups:[
    {en:'Costing', screens:[
      {id:'M54-pools', en:'Cost Pools & Elements', bn:'ব্যয় পুল', t:'g'},
      {id:'M54-allocation', en:'Allocation Cycles', bn:'বণ্টন চক্র', t:'c'},
      {id:'M54-jobs', en:'Job / Work-Order Costing', bn:'কাজের ব্যয়', t:'r'},
      {id:'M54-loaded', en:'Technician Loaded Cost', bn:'কর্মী ব্যয়', t:'r'} ]},
    {en:'Profitability', screens:[
      {id:'M54-streams', en:'14 Business-Line P&L', bn:'১৪ ব্যবসার লাভ', t:'r'},
      {id:'M54-branches', en:'Branch Profitability', bn:'শাখা লাভজনকতা', t:'r'},
      {id:'M54-customers', en:'Customer Profitability', bn:'গ্রাহক লাভজনকতা', t:'r'},
      {id:'M54-unitecon', en:'Unit Economics', bn:'একক অর্থনীতি', t:'r'} ]},
    {en:'Budgeting', screens:[
      {id:'M54-budgets', en:'Operating & Capital Budgets', bn:'বাজেট', t:'g'},
      {id:'M54-workflow', en:'Budget Workflow', bn:'বাজেট প্রবাহ', t:'c'},
      {id:'M54-bva', en:'Variance Analysis', bn:'বিচ্যুতি বিশ্লেষণ', t:'r'} ]},
    {en:'Planning', screens:[
      {id:'M54-rolling', en:'Rolling Forecast', bn:'রোলিং পূর্বাভাস', t:'r'},
      {id:'M54-scenario', en:'Scenario Modelling', bn:'পরিস্থিতি মডেল', t:'c'},
      {id:'M54-board', en:'Board Pack', bn:'বোর্ড প্যাক', t:'r'} ]} ],
  reports:['Business-Line P&L (14)','Branch League Table','Budget vs Actual','Job Margin Distribution','Customer Profitability Deciles','Unit Economics per Repair'],
  forms:['Budget Version','Allocation Rule','Scenario'],
  cross:['M19 GL dimensions','M31 repair costs','M02 field costs','M25 dashboards'],
  freg:{ src:70, sub:[
    ['1','Cost Model',9],['2','Allocation Cycles',10],['3','Job & Contract Costing',11],
    ['4','Business-Line Profitability',9],['5','Branch & Channel Profitability',8],
    ['6','Budgeting',11],['7','Variance & Forecast',8],['8','Board Pack',4] ] } },

/* ============ A09 · PEOPLE & WORKFORCE =============================== */

/* ---------------- M21 CORE HR ---------------------------------------------- */
window.FX_MODULES.M21 = { area:'A09', en:'Core HR & Lifecycle', bn:'মানবসম্পদ', icon:'👥', rail:'people',
  desc:'Hire-to-retire, Labour Act documents (appointment letter, ID card, service book), org structure, ESS/MSS.',
  kpis:[ {l:'Headcount',v:'512',d:'+14 QoQ',up:1,spark:[446,462,474,484,494,504,512]},
          {l:'Attrition YTD',v:'8.4%',d:'−1.2pt',up:1,st:'ok',spark:[12,11.4,10.6,9.8,9.1,8.7,8.4]},
          {l:'Technicians',v:'284',st:'info'},
          {l:'Open Positions',v:'22',st:'warn'},
          {l:'Probation Ending (30d)',v:'9',st:'info'},
          {l:'Service Books Complete',v:'100%',st:'ok'} ],
  groups:[
    {en:'Employee Master', screens:[
      {id:'M21-directory', en:'Directory', bn:'কর্মী তালিকা', t:'g'},
      {id:'M21-employee', en:'Employee Record', bn:'কর্মী নথি', t:'f'},
      {id:'M21-orgchart', en:'Org Chart', bn:'সংগঠন চার্ট', t:'x'},
      {id:'M21-positions', en:'Positions & Jobs', bn:'পদ', t:'g'} ]},
    {en:'Lifecycle', screens:[
      {id:'M21-hire', en:'Hire / Onboard', bn:'নিয়োগ', t:'c'},
      {id:'M21-transfer', en:'Transfer / Promote', bn:'স্থানান্তর ও পদোন্নতি', t:'g'},
      {id:'M21-exit', en:'Exit & Settlement', bn:'প্রস্থান', t:'c'},
      {id:'M21-movement', en:'Movement History', bn:'চলাচলের ইতিহাস', t:'r'} ]},
    {en:'Documents', screens:[
      {id:'M21-appointment', en:'Appointment Letters', bn:'নিয়োগপত্র', t:'g'},
      {id:'M21-servicebook', en:'Service Books', bn:'সার্ভিস বুক', t:'g'},
      {id:'M21-nominees', en:'Dependants & Nominees', bn:'মনোনীত ব্যক্তি', t:'g'} ]},
    {en:'Self-Service', screens:[
      {id:'M21-ess', en:'ESS / MSS', bn:'স্ব-সেবা', t:'d'} ]} ],
  reports:['Headcount & Movement','Attrition Analysis','Probation Conversion','Establishment Register','Org Distribution'],
  forms:['Employee','Transfer','Promotion','Exit Clearance'],
  cross:['M29 JML provisioning','M56 payroll feed','M22 certification register','M55 shifts'],
  freg:{ src:70, sub:[
    ['1','Employee Master',12],['2','Employment Contracts',7],['3','Org Structure',9],
    ['4','Lifecycle Events',12],['5','Statutory Documents',7],['6','Dependants & Nominees',5],
    ['7','ESS / MSS',9],['8','Exit Process',9] ] } },

/* ---------------- M55 TIME, ATTENDANCE & SCHEDULING -------------------------- */
window.FX_MODULES.M55 = { area:'A09', en:'Time, Attendance & Scheduling', bn:'সময় ও শিফট', icon:'⏰', rail:'people',
  desc:'Biometric + geofenced mobile capture, moon-dependent holidays, rosters, availability published to dispatch.',
  kpis:[ {l:'Attendance Today',v:'96.2%',st:'ok',spark:[92,93,94,94.8,95.4,95.8,96.2]},
          {l:'Exceptions Pending',v:'48',st:'warn'},
          {l:'Overtime Pre-Approved',v:'100%',st:'ok'},
          {l:'Roster Coverage',v:'98.6%',st:'ok'},
          {l:'Leave Pending',v:'36',st:'warn'},
          {l:'Geofence Clock-Ins',v:'284',st:'info'} ],
  groups:[
    {en:'Capture', screens:[
      {id:'M55-daily', en:'Daily Attendance', bn:'দৈনিক উপস্থিতি', t:'g'},
      {id:'M55-devices', en:'Biometric Devices', bn:'বায়োমেট্রিক', t:'g'},
      {id:'M55-geofence', en:'Geofenced Clock-In', bn:'জিওফেন্স', t:'g'},
      {id:'M55-exc', en:'Exception Regularisation', bn:'ব্যতিক্রম নিয়মিতকরণ', t:'c'} ]},
    {en:'Working Time', screens:[
      {id:'M55-rules', en:'Rules & Overtime', bn:'নিয়ম ও অতিরিক্ত সময়', t:'g'},
      {id:'M55-holidays', en:'Holidays (moon-dependent)', bn:'ছুটির দিনপঞ্জি', t:'g'} ]},
    {en:'Leave', screens:[
      {id:'M55-leave', en:'Leave Requests', bn:'ছুটির আবেদন', t:'g'},
      {id:'M55-balances', en:'Balances', bn:'ব্যালান্স', t:'r'},
      {id:'M55-calendar', en:'Calendar', bn:'ক্যালেন্ডার', t:'g'} ]},
    {en:'Scheduling', screens:[
      {id:'M55-shifts', en:'Shift Patterns', bn:'শিফট', t:'g'},
      {id:'M55-rosters', en:'Rosters & Publication', bn:'রোস্টার', t:'c'},
      {id:'M55-oncall', en:'On-Call / Standby', bn:'অন-কল', t:'g'},
      {id:'M55-availability', en:'Availability → Dispatch', bn:'প্রাপ্যতা', t:'g'} ]} ],
  reports:['Attendance Summary','Overtime Analysis','Leave Utilisation','Roster vs Actual','Coverage Gaps'],
  forms:['Leave Request','Roster','Shift Pattern','Exception Regularisation'],
  cross:['M02 dispatch availability','M56 payroll hours','M27 contact-centre WFM','M21 employees'],
  freg:{ src:74, sub:[
    ['1','Capture (4 modes)',12],['2','Working Time & OT',9],['3','Leave',10],
    ['4','Holidays',5],['5','Shifts & Rosters',13],['6','On-Call',6],
    ['7','Availability Publication',7],['8','Verification & Lock',6],['9','Timesheets',6] ] } },

/* ---------------- M56 PAYROLL & STATUTORY ------------------------------------ */
window.FX_MODULES.M56 = { area:'A09', en:'Payroll & Statutory', bn:'বেতন ও সুবিধা', icon:'💵', rail:'people',
  desc:'BD gross-to-net engine, tax slabs AY26-27, PF, gratuity ≥30 days/yr, festival bonus, BEFTN bank files.',
  kpis:[ {l:'Payroll Cycle',v:'Day 19',st:'ok'},
          {l:'Gross Payroll',v:'৳ 4.82 Cr',st:'info'},
          {l:'Run Duration',v:'2.6 h',d:'−48 min',up:1,st:'ok'},
          {l:'Corrections',v:'0.2%',st:'ok'},
          {l:'Tax Withheld MTD',v:'৳ 42.6 L',st:'info'},
          {l:'Festival Bonus Accrued',v:'৳ 96 L',st:'info'} ],
  groups:[
    {en:'Payroll Engine', screens:[
      {id:'M56-runs', en:'Payroll Runs', bn:'বেতন রান', t:'c'},
      {id:'M56-structures', en:'Salary Structures', bn:'বেতন কাঠামো', t:'g'},
      {id:'M56-payslips', en:'Payslips', bn:'বেতন পত্র', t:'g'},
      {id:'M56-offcycle', en:'Off-Cycle Payments', bn:'অফ-সাইকেল', t:'g'} ]},
    {en:'Statutory', screens:[
      {id:'M56-tax', en:'Income Tax (AY 2026-27)', bn:'আয়কর', t:'g'},
      {id:'M56-pf', en:'Provident Fund', bn:'প্রভিডেন্ট ফান্ড', t:'g'},
      {id:'M56-gratuity', en:'Gratuity & Encashment', bn:'গ্র্যাচুইটি', t:'g'},
      {id:'M56-bonus', en:'Festival Bonus', bn:'উৎসব বোনাস', t:'g'} ]},
    {en:'Disbursement', screens:[
      {id:'M56-beftn', en:'BEFTN Bank Files', bn:'বিইএফটিএন', t:'g'},
      {id:'M56-certificates', en:'Certificates & Tax Statements', bn:'সনদ', t:'g'} ]},
    {en:'Compliance', screens:[
      {id:'M56-returns', en:'Withholding Returns (Quarterly)', bn:'উৎসে কর রিটার্ন', t:'c'},
      {id:'M56-settlement', en:'Final Settlements', bn:'চূড়ান্ত নিষ্পত্তি', t:'g'} ]} ],
  reports:['Salary Register','Payroll Cost Allocation','Tax Deduction Summary','PF & Gratuity Provisions','Payroll Variance'],
  forms:['Salary Structure','Payroll Run','Bonus Run','Final Settlement'],
  cross:['M55 attendance input','M19 GL posting','M50 BEFTN execution','M57 incentive feed'],
  freg:{ src:82, sub:[
    ['1','Gross-to-Net Engine',14],['2','BD Income Tax',12],['3','Provident Fund',7],
    ['4','Gratuity',7],['5','Bonus & Encashment',7],['6','Loans & Advances',6],
    ['7','Runs & Off-Cycle',9],['8','BEFTN & Payslips',8],['9','Returns & Certificates',7],
    ['10','Final Settlement',5] ] } },

/* ---------------- M57 PERFORMANCE & INCENTIVES ------------------------------- */
window.FX_MODULES.M57 = { area:'A09', en:'Performance & Incentives', bn:'পারফরম্যান্স ও প্রণোদনা', icon:'🏆', rail:'people',
  desc:'Goal cascades, KPI attribution to payroll, technician incentive schemes, calibration, recognition.',
  kpis:[ {l:'Reviews On Track',v:'94.2%',st:'ok'},
          {l:'Incentive Pool MTD',v:'৳ 12.4 L',st:'info'},
          {l:'Goal Coverage',v:'98.4%',st:'ok'},
          {l:'Calibration Sessions',v:'6 done',st:'ok'},
          {l:'PIPs Active',v:'4',st:'warn'},
          {l:'Incentive Accuracy',v:'99.8%',st:'ok'} ],
  groups:[
    {en:'Performance', screens:[
      {id:'M57-goals', en:'Goal Cascades', bn:'লক্ষ্য স্তর', t:'g'},
      {id:'M57-kpis', en:'KPI Definitions', bn:'কেপিআই', t:'g'},
      {id:'M57-reviews', en:'Review Cycles', bn:'পর্যালোচনা চক্র', t:'c'},
      {id:'M57-calibration', en:'Calibration', bn:'ক্যালিব্রেশন', t:'g'},
      {id:'M57-pips', en:'PIPs', bn:'কর্ম উন্নয়ন পরিকল্পনা', t:'g'} ]},
    {en:'Incentives', screens:[
      {id:'M57-schemes', en:'Incentive Schemes', bn:'প্রণোদনা কর্মসূচি', t:'g'},
      {id:'M57-calc', en:'Calculation Runs', bn:'হিসাব রান', t:'c'},
      {id:'M57-recognition', en:'Recognition', bn:'স্বীকৃতি', t:'g'} ]},
    {en:'Compensation', screens:[
      {id:'M57-comp', en:'Compensation Review', bn:'বেতন পর্যালোচনা', t:'c'},
      {id:'M57-succession', en:'Succession', bn:'উত্তরসূরি', t:'g'} ]} ],
  reports:['Rating Distribution','Incentive Payout by Scheme','Technician Scorecards','Calibration Summary','PIP Outcomes'],
  forms:['Goal','Review','Incentive Scheme','Recognition'],
  cross:['M25 KPI dashboards','M56 payroll publication','M34 customer ratings','M22 technician skills'],
  freg:{ src:58, sub:[
    ['1','Goals & KPIs',11],['2','Review Cycles',10],['3','Multi-Source Feedback',6],
    ['4','Rating & Calibration',8],['5','Incentive Design & Calculation',12],['6','Recognition',4],
    ['7','Compensation Review',7] ] } },

/* ---------------- M22 LEARNING & CERTIFICATION -------------------------------- */
window.FX_MODULES.M22 = { area:'A09', en:'Learning & Certification', bn:'প্রশিক্ষণ ও সার্টিফিকেশন', icon:'🎓', rail:'people',
  desc:'Competency framework, brand certification register with expiry, hard block on expired certification at dispatch.',
  kpis:[ {l:'Certified Technicians',v:'276 of 284',st:'ok'},
          {l:'Expiring (30d)',v:'8',st:'warn'},
          {l:'Expired Working',v:'0',st:'ok'},
          {l:'Training Hours /tech',v:'42',d:'+6',up:1},
          {l:'Brand Certifications',v:'312',st:'info'},
          {l:'Assessment Pass Rate',v:'88.4%',st:'ok'} ],
  groups:[
    {en:'Competency', screens:[
      {id:'M22-framework', en:'Competency Framework', bn:'দক্ষতা কাঠামো', t:'g'},
      {id:'M22-matrix', en:'Skill Matrix', bn:'দক্ষতা ম্যাট্রিক্স', t:'d'},
      {id:'M22-assessments', en:'Assessments', bn:'মূল্যায়ন', t:'g'} ]},
    {en:'Certifications', screens:[
      {id:'M22-register', en:'Certification Register', bn:'সার্টিফিকেশন রেজিস্টার', t:'g'},
      {id:'M22-expiry', en:'Validity & Renewal', bn:'মেয়াদ ও নবায়ন', t:'c'},
      {id:'M22-eligibility', en:'Dispatch Eligibility (hard block)', bn:'ডিসপ্যাচ যোগ্যতা', t:'g'} ]},
    {en:'Training', screens:[
      {id:'M22-catalogue', en:'Course Catalogue', bn:'কোর্স তালিকা', t:'g'},
      {id:'M22-paths', en:'Learning Paths', bn:'শেখার পথ', t:'g'},
      {id:'M22-schedule', en:'Schedule & Attendance', bn:'সূচি ও উপস্থিতি', t:'g'},
      {id:'M22-ojt', en:'OJT & Mentoring', bn:'কর্মস্থল প্রশিক্ষণ', t:'g'} ]},
    {en:'Evidence', screens:[
      {id:'M22-iso', en:'ISO / Brand Audit Evidence', bn:'আইএসও প্রমাণ', t:'g'} ]} ],
  reports:['Certification Coverage by Brand','Expiry Forecast','Training Effectiveness','Skill-Gap Heatmap','Audit Evidence Pack'],
  forms:['Certification','Course','Learning Path','Assessment'],
  cross:['M02 assignment gate','M31 L3 routing','M23 ISO 7.2','M21 employees'],
  freg:{ src:52, sub:[
    ['1','Competency Framework',8],['2','Skill Matrix & Assessment',10],
    ['3','Certification Register',12],['4','Training Delivery',12],
    ['5','OJT & Mentoring',5],['6','Evidence & Analytics',5] ] } },

/* ---------------- M58 TALENT ACQUISITION --------------------------------------- */
window.FX_MODULES.M58 = { area:'A09', en:'Talent Acquisition', bn:'নিয়োগ', icon:'🧲', rail:'people',
  desc:'Requisitions vs budget, structured interviews, practical technician assessments, pre-boarding, PDPA erasure.',
  kpis:[ {l:'Open Requisitions',v:'22',st:'warn'},
          {l:'Time-to-Fill',v:'28 d',d:'−4 d',up:1,st:'ok'},
          {l:'Pipeline',v:'184',st:'info'},
          {l:'Offer Accept Rate',v:'82%',st:'ok'},
          {l:'Referral Share',v:'31%',st:'info'},
          {l:'First-90 Retention',v:'91.4%',st:'ok'} ],
  groups:[
    {en:'Requisitions', screens:[
      {id:'M58-reqs', en:'Requisitions', bn:'নিয়োগ অনুরোধ', t:'g'},
      {id:'M58-approval', en:'Approval vs Budget', bn:'বাজেট অনুমোদন', t:'c'} ]},
    {en:'Sourcing', screens:[
      {id:'M58-postings', en:'Job Postings', bn:'চাকরির বিজ্ঞপ্তি', t:'g'},
      {id:'M58-candidates', en:'Candidate Pipeline', bn:'প্রার্থী', t:'g'} ]},
    {en:'Selection', screens:[
      {id:'M58-interviews', en:'Structured Interviews', bn:'সাক্ষাৎকার', t:'g'},
      {id:'M58-practical', en:'Practical Assessments', bn:'ব্যবহারিক মূল্যায়ন', t:'c'},
      {id:'M58-checks', en:'Reference & Background', bn:'রেফারেন্স', t:'g'},
      {id:'M58-offers', en:'Offers', bn:'প্রস্তাব', t:'g'} ]},
    {en:'Onboarding', screens:[
      {id:'M58-preboard', en:'Pre-Boarding', bn:'প্রি-বোর্ডিং', t:'c'},
      {id:'M58-first90', en:'First-90-Days', bn:'প্রথম ৯০ দিন', t:'g'} ]} ],
  reports:['Funnel & Conversion','Time-to-Fill by Role','Source Effectiveness','First-90 Retention','Practical Assessment Results'],
  forms:['Requisition','Candidate','Interview Evaluation','Offer'],
  cross:['M21 handover','M29 account provisioning','M22 onboarding training','M57 workforce planning'],
  freg:{ src:50, sub:[
    ['1','Workforce Planning & Requisition',9],['2','Sourcing',7],['3','Screening',6],
    ['4','Interviews & Assessments',11],['5','Checks & Offers',7],['6','Pre-Boarding',4],
    ['7','Onboarding Orchestration',6] ] } },

/* ---------------- M59 HEALTH, SAFETY & WELLBEING -------------------------------- */
window.FX_MODULES.M59 = { area:'A09', en:'Health, Safety & Wellbeing', bn:'স্বাস্থ্য ও নিরাপত্তা', icon:'🦺', rail:'people',
  desc:'Hazard register, lone-worker safety, battery/electrical hazards, statutory accident clock, safety committee.',
  kpis:[ {l:'Recordable Incidents YTD',v:'6',st:'info'},
          {l:'Lost-Time Injuries',v:'1',st:'warn'},
          {l:'Near-Miss Reports MTD',v:'24',d:'+8',up:1,st:'ok'},
          {l:'Statutory Clock (FIFO)',v:'compliant',st:'ok'},
          {l:'PPE Compliance',v:'97.8%',st:'ok'},
          {l:'Drills Completed',v:'12 of 13',st:'warn'} ],
  groups:[
    {en:'Risk', screens:[
      {id:'M59-hazards', en:'Hazard Register', bn:'ঝুঁকি রেজিস্টার', t:'g'},
      {id:'M59-jsa', en:'JSA & Safe Procedures', bn:'কাজের নিরাপত্তা বিশ্লেষণ', t:'g'},
      {id:'M59-ppe', en:'PPE Issue Register', bn:'পিপিই', t:'g'} ]},
    {en:'Incidents', screens:[
      {id:'M59-report', en:'Incident & Near-Miss Reporting', bn:'ঘটনা রিপোর্ট', t:'f'},
      {id:'M59-investigate', en:'Investigation & RCA', bn:'তদন্ত', t:'c'},
      {id:'M59-statutory', en:'Statutory Notification Clock', bn:'আইনি ঘড়ি', t:'g'} ]},
    {en:'Field Safety', screens:[
      {id:'M59-loneworker', en:'Lone-Worker & Emergency', bn:'একাকী কর্মী', t:'g'},
      {id:'M59-road', en:'Road & Vehicle Safety', bn:'সড়ক নিরাপত্তা', t:'g'},
      {id:'M59-battery', en:'Battery / Electrical / Chemical', bn:'ব্যাটারি ঝুঁকি', t:'g'} ]},
    {en:'Programme', screens:[
      {id:'M59-drills', en:'Drills & Training', bn:'মহড়া', t:'g'},
      {id:'M59-committee', en:'Safety Committee', bn:'নিরাপত্তা কমিটি', t:'g'},
      {id:'M59-wellbeing', en:'Occupational Health', bn:'পেশাগত স্বাস্থ্য', t:'g'} ]} ],
  reports:['Incident Statistics','Leading Indicators','Statutory Compliance','PPE Compliance','Drill Calendar Coverage'],
  forms:['Incident Report','JSA','PPE Issue','Return-to-Work'],
  cross:['M02 lone-worker check-ins','M46 vehicle safety','M47 site safety','M22 safety training'],
  freg:{ src:60, sub:[
    ['1','Hazard Register & Risk',9],['2','Procedures & Permits',7],['3','Incident Management',13],
    ['4','Statutory Notification',5],['5','PPE',5],['6','Field & Road Safety',8],
    ['7','Training & Drills',6],['8','Health & Wellbeing',7] ] } },

/* ============ A10 · QUALITY, RISK & KNOWLEDGE ======================== */

/* ---------------- M23 QUALITY MANAGEMENT SYSTEM ---------------------------- */
window.FX_MODULES.M23 = { area:'A10', en:'Quality Management (ISO)', bn:'কোয়ালিটি ম্যানেজমেন্ট', icon:'✅', rail:'quality',
  desc:'ISO 9001:2015 operating system — process register, NCRs, CAPA with verification, audits, management review.',
  kpis:[ {l:'Major NCs',v:'0',st:'ok'},
          {l:'CAPA On-Time',v:'95.8%',st:'ok',spark:[88,90,91.5,93,94.2,95,95.8]},
          {l:'Open NCRs',v:'18',st:'warn'},
          {l:'Audit Findings (open)',v:'7',st:'warn'},
          {l:'First-Pass QC',v:'95.2%',st:'ok'},
          {l:'CoPQ',v:'1.9% of revenue',d:'−0.3pt',up:1,st:'ok'} ],
  groups:[
    {en:'Framework', screens:[
      {id:'M23-policy', en:'Policy & Objectives', bn:'নীতি ও উদ্দেশ্য', t:'g'},
      {id:'M23-processes', en:'Process Register (ISO map)', bn:'প্রক্রিয়া রেজিস্টার', t:'g'},
      {id:'M23-checklists', en:'Checklist Authoring', bn:'চেকলিস্ট রচনা', t:'g'},
      {id:'M23-gates', en:'Quality Gates', bn:'গুণগত গেট', t:'g'} ]},
    {en:'Nonconformance', screens:[
      {id:'M23-ncr', en:'NCR Management', bn:'অসঙ্গতি', t:'g'},
      {id:'M23-rca', en:'RCA (5-Why / 8D)', bn:'মূল কারণ', t:'c'},
      {id:'M23-capa', en:'CAPA & Verification', bn:'ক্যাপা', t:'c'} ]},
    {en:'Audits', screens:[
      {id:'M23-internal', en:'Internal Audit Programme', bn:'অভ্যন্তরীণ অডিট', t:'c'},
      {id:'M23-external', en:'Certification & Surveillance', bn:'সার্টিফিকেশন', t:'g'},
      {id:'M23-review', en:'Management Review', bn:'ব্যবস্থাপনা পর্যালোচনা', t:'c'} ]},
    {en:'Analytics', screens:[
      {id:'M23-stat', en:'Pareto & Control Charts', bn:'প্যারেটো', t:'r'},
      {id:'M23-copq', en:'Cost of Poor Quality', bn:'নিম্ন গুণগত ব্যয়', t:'r'} ]} ],
  reports:['NCR & CAPA Register','Audit Programme Status','Repeat-Failure Escalation','CoPQ Analysis','Management Review Pack'],
  forms:['NCR','CAPA','Audit Finding','Checklist Template'],
  cross:['M01 QC gates','M31 workshop QC','M34 complaint signals','P11 auditor app'],
  freg:{ src:78, sub:[
    ['1','Policy & Objectives',6],['2','Process Register',7],['3','Checklists & Gates',10],
    ['4','NCR Management',12],['5','RCA & CAPA',14],['6','Audit Programme',13],
    ['7','Management Review',7],['8','Statistics & CoPQ',9] ] } },

/* ---------------- M60 GOVERNANCE, RISK & COMPLIANCE ------------------------- */
window.FX_MODULES.M60 = { area:'A10', en:'Governance, Risk & Compliance', bn:'গভর্নেন্স ও ঝুঁকি', icon:'⚖️', rail:'quality',
  desc:'Enterprise risk register, internal control testing, SoD rules, licence register, PDPA governance, whistleblowing.',
  kpis:[ {l:'Risks Above Appetite',v:'7',st:'warn'},
          {l:'Control Tests Due',v:'14',st:'warn'},
          {l:'Licence Gaps',v:'0',st:'ok'},
          {l:'Policy Attestations',v:'96.4%',st:'ok'},
          {l:'Legal Matters Open',v:'3',st:'info'},
          {l:'DSRs (SLA 30d)',v:'4 in progress',st:'ok'} ],
  groups:[
    {en:'Risk', screens:[
      {id:'M60-register', en:'Enterprise Risk Register', bn:'ঝুঁকি রেজিস্টার', t:'g'},
      {id:'M60-appetite', en:'Appetite & Aggregation', bn:'ঝুঁকি ক্ষমতা', t:'r'} ]},
    {en:'Controls', screens:[
      {id:'M60-framework', en:'Internal Control Framework', bn:'অভ্যন্তরীণ নিয়ন্ত্রণ', t:'g'},
      {id:'M60-testing', en:'Control Testing', bn:'নিয়ন্ত্রণ পরীক্ষা', t:'c'},
      {id:'M60-sod', en:'SoD Rules', bn:'দায়িত্ব বিভাজন', t:'g'},
      {id:'M60-authority', en:'Delegated Authority', bn:'প্রতিনিধি ক্ষমতা', t:'g'} ]},
    {en:'Compliance', screens:[
      {id:'M60-obligations', en:'Obligation Register', bn:'বাধ্যবাধকতা', t:'g'},
      {id:'M60-licences', en:'Licence Register', bn:'লাইসেন্স রেজিস্টার', t:'g'},
      {id:'M60-policies', en:'Policy Governance', bn:'নীতি শাসন', t:'g'} ]},
    {en:'Legal & Data', screens:[
      {id:'M60-legal', en:'Legal Matters', bn:'আইনি বিষয়', t:'g'},
      {id:'M60-pdpa', en:'PDPA Governance', bn:'পিডিপিএ শাসন', t:'c'},
      {id:'M60-whistle', en:'Whistleblowing', bn:'হুইসেলব্লোয়িং', t:'g'} ]} ],
  reports:['Risk Heat Map','Control Deficiency Log','Licence Expiry Register','Attestation Status','Board Risk Pack'],
  forms:['Risk','Control Test','Licence','Policy','Whistleblow Report'],
  cross:['M29 SoD enforcement','M23 ISO interface','M51 statutory','M33 DSR handling'],
  freg:{ src:70, sub:[
    ['1','Risk Register',12],['2','Control Framework & Testing',14],['3','SoD & Authority',8],
    ['4','Compliance Obligations',9],['5','Policy Governance',6],['6','Legal & IP',7],
    ['7','PDPA Governance',9],['8','Whistleblowing',5] ] } },

/* ---------------- M24 DOCUMENTS & E-SIGNATURE -------------------------------- */
window.FX_MODULES.M24 = { area:'A10', en:'Documents & E-Signature', bn:'দলিল ও ই-স্বাক্ষর', icon:'🗂️', rail:'quality',
  desc:'Auto-filing from transactions, bilingual OCR search, e-signature envelopes, retention 5–10y, evidence packs.',
  kpis:[ {l:'Documents',v:'4.2 M',st:'info'},
          {l:'Auto-Filed',v:'100%',st:'ok'},
          {l:'Search p95',v:'1.2 s',st:'ok'},
          {l:'Pending e-Signatures',v:'26',st:'warn'},
          {l:'Legal Holds',v:'2',st:'warn'},
          {l:'Evidence Packs < 5 min',v:'100%',st:'ok'} ],
  groups:[
    {en:'Repository', screens:[
      {id:'M24-browser', en:'Document Browser', bn:'দলিল ব্রাউজার', t:'g'},
      {id:'M24-search', en:'Bilingual Full-Text + OCR', bn:'পূর্ণ-পাঠ অনুসন্ধান', t:'c'} ]},
    {en:'Workflows', screens:[
      {id:'M24-controlled', en:'Controlled Documents', bn:'নিয়ন্ত্রিত দলিল', t:'c'},
      {id:'M24-generation', en:'Templates & Generation', bn:'টেমপ্লেট', t:'g'} ]},
    {en:'E-Signature', screens:[
      {id:'M24-envelopes', en:'Signature Envelopes', bn:'স্বাক্ষর খাম', t:'g'},
      {id:'M24-audit', en:'Tamper Evidence & Audit', bn:'ট্যাম্পার প্রমাণ', t:'g'} ]},
    {en:'Retention', screens:[
      {id:'M24-retention', en:'Retention Enforcement', bn:'সংরক্ষণ নীতি', t:'g'},
      {id:'M24-holds', en:'Legal Holds', bn:'আইনি আটক', t:'g'},
      {id:'M24-disposal', en:'Defensible Disposal', bn:'নিষ্পত্তি', t:'g'} ]} ],
  reports:['Retention Compliance','Signature Status','Repository Growth','Access Audit Export'],
  forms:['Upload','Signature Envelope','Share Token','Retention Policy'],
  cross:['Every transaction auto-files','M36 quote e-sign','M09 evidence packs','M23 controlled docs'],
  freg:{ src:56, sub:[
    ['1','Repository & Integrity',7],['2','Auto-Filing',6],['3','Classification & Search',9],
    ['4','Versioning & Control',7],['5','E-Signature',10],['6','Retention & Holds',10],
    ['7','Evidence Packs',7] ] } },

/* ---------------- M61 KNOWLEDGE MANAGEMENT ------------------------------------ */
window.FX_MODULES.M61 = { area:'A10', en:'Knowledge & Technical Library', bn:'জ্ঞান ও কারিগরি লাইব্রেরি', icon:'📚', rail:'quality',
  desc:'Repair procedures & fault→fix, troubleshooting trees, offline distribution to technician app, brand bulletins.',
  kpis:[ {l:'Articles',v:'8,412',st:'info',spark:[6200,6700,7100,7500,7840,8140,8412]},
          {l:'Coverage (top faults)',v:'92.4%',st:'ok'},
          {l:'Offline Synced Techs',v:'284',st:'ok'},
          {l:'Usefulness Score',v:'4.4 / 5',st:'ok'},
          {l:'Reviews Due',v:'38',st:'warn'},
          {l:'Brand Bulletins MTD',v:'12',st:'info'} ],
  groups:[
    {en:'Authoring', screens:[
      {id:'M61-articles', en:'Article Library (7 types)', bn:'নিবন্ধ লাইব্রেরি', t:'g'},
      {id:'M61-trees', en:'Troubleshooting Trees', bn:'সমস্যা নিরসন ট্রি', t:'f'},
      {id:'M61-review', en:'Review Workflow', bn:'পর্যালোচনা প্রবাহ', t:'c'} ]},
    {en:'Technical Library', screens:[
      {id:'M61-manuals', en:'Manuals & Schematics', bn:'ম্যানুয়াল', t:'g'},
      {id:'M61-media', en:'Video & Image Content', bn:'ভিডিও', t:'g'} ]},
    {en:'Distribution', screens:[
      {id:'M61-context', en:'Context-Aware Surfacing', bn:'প্রসঙ্গ-সচেতন', t:'g'},
      {id:'M61-offline', en:'Offline Distribution', bn:'অফলাইন বিতরণ', t:'g'} ]},
    {en:'Feedback', screens:[
      {id:'M61-health', en:'Article Health & Gaps', bn:'নিবন্ধ স্বাস্থ্য', t:'r'},
      {id:'M61-bulletins', en:'Brand Bulletins & Recalls', bn:'ব্র্যান্ড বুলেটিন', t:'g'} ]} ],
  reports:['Coverage Analysis','Article Usage & Usefulness','Gap Report by Brand/Model','Contribution Leaderboard'],
  forms:['Article','Troubleshooting Tree','Bulletin'],
  cross:['M32 RAG grounding','M31 repair methods','P02 offline library','M01 diagnostic trees'],
  freg:{ src:48, sub:[
    ['1','Authoring & Versioning',8],['2','Troubleshooting Trees',7],['3','Technical Library',7],
    ['4','Search & Surfacing',7],['5','Offline Distribution',5],['6','Feedback & Health',6],
    ['7','Brand Bulletins',4],['8','Expertise Mapping',4] ] } },

/* ============ A11 · DATA, ANALYTICS & INTELLIGENCE =================== */

/* ---------------- M25 BUSINESS INTELLIGENCE ---------------------------------- */
window.FX_MODULES.M25 = { area:'A11', en:'Business Intelligence', bn:'বিজনেস ইন্টেলিজেন্স', icon:'📊', rail:'insight',
  desc:'Role dashboards, standard report library, embedded analytics, scheduled bursting, spreadsheet retirement.',
  kpis:[ {l:'Dashboards Live',v:'31',st:'ok'},
          {l:'Standard Reports',v:'214',st:'ok'},
          {l:'Weekly Manager Usage',v:'93.6%',st:'ok'},
          {l:'Load Time p95',v:'3.2 s',st:'ok'},
          {l:'Scheduled Distributions',v:'84',st:'info'},
          {l:'Spreadsheets Retired',v:'126',st:'ok'} ],
  groups:[
    {en:'Executive', screens:[
      {id:'M25-ceo', en:'CEO Cockpit', bn:'সিইও ককপিট', t:'d'},
      {id:'M25-coo', en:'COO / Ops Board (Live)', bn:'অপারেশন বোর্ড', t:'d'},
      {id:'M25-cfo', en:'CFO Dashboard', bn:'সিএফও', t:'d'},
      {id:'M25-ccO', en:'CCO Commercial', bn:'সিসিও', t:'d'} ]},
    {en:'Functional', screens:[
      {id:'M25-service', en:'Service Analytics', bn:'সার্ভিস বিশ্লেষণ', t:'d'},
      {id:'M25-branch', en:'Branch League Table', bn:'শাখা লিগ টেবিল', t:'r'},
      {id:'M25-finance', en:'Finance Analytics', bn:'আর্থিক বিশ্লেষণ', t:'d'},
      {id:'M25-people', en:'People Analytics', bn:'জনবল বিশ্লেষণ', t:'d'},
      {id:'M25-quality', en:'Quality Analytics', bn:'গুণগত বিশ্লেষণ', t:'d'} ]},
    {en:'Self-Service', screens:[
      {id:'M25-datasets', en:'Certified Datasets', bn:'প্রত্যয়িত ডেটাসেট', t:'g'},
      {id:'M25-builder', en:'Dashboard Builder', bn:'ড্যাশবোর্ড নির্মাতা', t:'c'} ]},
    {en:'Operations', screens:[
      {id:'M25-schedules', en:'Scheduled Distribution', bn:'নির্ধারিত বিতরণ', t:'g'},
      {id:'M25-alerts', en:'Threshold Alerts', bn:'সতর্কতা', t:'g'} ]} ],
  reports:['Executive Pack','Branch League','Service KPI Pack','Finance Pack','People Pack','Any dashboard → export'],
  forms:['Dashboard','Distribution Schedule','Alert Subscription'],
  cross:['M62 semantic layer','M26 model outputs','P06 analytics portal','M54 FP&A'],
  freg:{ src:58, sub:[
    ['1','Role Dashboards',12],['2','Standard Report Library',10],['3','Self-Service',8],
    ['4','Distribution & Alerting',9],['5','Embedded Analytics',7],['6','Mobile',5],
    ['7','Lifecycle & Usage',7] ] } },

/* ---------------- M26 AI/ML SERVICES ------------------------------------------- */
window.FX_MODULES.M26 = { area:'A11', en:'AI/ML Services (14 models)', bn:'এআই/এমএল সেবা', icon:'🧠', rail:'insight',
  desc:'Dispatch scoring 70% auto-assign, fault classification from Bengali text, demand MAPE<22%, trade-in valuation.',
  kpis:[ {l:'Auto-Assign Rate',v:'68%',d:'+6pt',up:1,st:'ok',spark:[22,31,40,49,58,64,68]},
          {l:'Demand MAPE',v:'18.4%',st:'ok',spark:[26,24.6,23.2,21.8,20.4,19.2,18.4]},
          {l:'Fault Classification F1',v:'0.91',st:'ok'},
          {l:'Churn Model AUC',v:'0.84',st:'ok'},
          {l:'Override Rate',v:'6.2%',st:'ok'},
          {l:'Drift Alerts',v:'2',st:'warn'} ],
  groups:[
    {en:'Portfolio', screens:[
      {id:'M26-models', en:'Model Portfolio (14)', bn:'মডেল পোর্টফোলিও', t:'g'},
      {id:'M26-registry', en:'Model Registry', bn:'মডেল রেজিস্ট্রি', t:'g'} ]},
    {en:'Operations', screens:[
      {id:'M26-deploy', en:'Deployment Patterns', bn:'স্থাপন পদ্ধতি', t:'g'},
      {id:'M26-monitor', en:'Production Monitoring', bn:'উৎপাদন পর্যবেক্ষণ', t:'d'},
      {id:'M26-fallback', en:'Inference Fallback', bn:'ফলব্যাক', t:'g'} ]},
    {en:'Governance', screens:[
      {id:'M26-governance', en:'Guard Rails & HITL', bn:'গার্ডরেল', t:'g'},
      {id:'M26-bias', en:'Bias Testing', bn:'পক্ষপাত পরীক্ষা', t:'g'},
      {id:'M26-cards', en:'Model Cards', bn:'মডেল কার্ড', t:'g'} ]},
    {en:'Generative', screens:[
      {id:'M26-genai', en:'Self-Hosted GenAI + RAG', bn:'জেনএআই', t:'c'},
      {id:'M26-ocr', en:'OCR & Bengali NLP', bn:'ওসিআর', t:'g'} ]} ],
  reports:['Model Performance Pack','Override Analysis','Drift Report','Fairness Summary'],
  forms:['Model Version','Evaluation Gate','Guard-Rail Config'],
  cross:['M02 dispatch scoring','M43 demand forecasts','M48 predictive failure','M32 conversational AI'],
  freg:{ src:58, sub:[
    ['1','Portfolio & Governance',10],['2','Training Pipelines',8],['3','Evaluation Gates',7],
    ['4','Deployment & Monitoring',11],['5','Explainability',5],['6','GenAI & RAG',9],
    ['7','Bengali NLP & OCR',8] ] } },

/* ---------------- M62 DATA PLATFORM -------------------------------------------- */
window.FX_MODULES.M62 = { area:'A11', en:'Data Platform & Governance', bn:'ডেটা প্ল্যাটফর্ম', icon:'🗃️', rail:'insight',
  desc:'Medallion lakehouse, dimensional model, semantic metric registry (one certified number), lineage, masking.',
  kpis:[ {l:'Certified Metrics',v:'312',st:'ok'},
          {l:'Quality Tests Passing',v:'99.2%',st:'ok'},
          {l:'Freshness Lag',v:'12 min',st:'ok'},
          {l:'Lineage Coverage',v:'100%',st:'ok'},
          {l:'PII Columns Masked',v:'100%',st:'ok'},
          {l:'Warehouse Cost MTD',v:'৳ 4.2 L',st:'warn'} ],
  groups:[
    {en:'Pipelines', screens:[
      {id:'M62-ingestion', en:'Ingestion & CDC', bn:'ইনজেশন', t:'g'},
      {id:'M62-medallion', en:'Medallion Progression', bn:'মেডালিয়ন', t:'g'},
      {id:'M62-backfill', en:'Replay & Backfill', bn:'রিপ্লে', t:'c'} ]},
    {en:'Modelling', screens:[
      {id:'M62-dimensional', en:'Dimensional Model', bn:'মাত্রিক মডেল', t:'g'},
      {id:'M62-contracts', en:'Data Contracts', bn:'ডেটা চুক্তি', t:'g'} ]},
    {en:'Governance', screens:[
      {id:'M62-metrics', en:'Metric Registry', bn:'মেট্রিক রেজিস্ট্রি', t:'g'},
      {id:'M62-catalog', en:'Catalogue & Glossary', bn:'ক্যাটালগ', t:'g'},
      {id:'M62-quality', en:'Quality Tests & Incidents', bn:'গুণগত পরীক্ষা', t:'g'},
      {id:'M62-observability', en:'Observability', bn:'পর্যবেক্ষণযোগ্যতা', t:'d'} ]},
    {en:'Security', screens:[
      {id:'M62-masking', en:'Masking & Access', bn:'মাস্কিং', t:'g'},
      {id:'M62-retention', en:'Retention & Cost', bn:'সংরক্ষণ ও ব্যয়', t:'g'} ]} ],
  reports:['Data Quality Scorecard','Freshness SLA','Lineage Coverage','Cost per Domain'],
  forms:['Data Contract','Metric Definition','Quality Test'],
  cross:['M25 dashboards','M29 row/column security','M63 automation triggers'],
  freg:{ src:62, sub:[
    ['1','Ingestion',10],['2','Medallion & Transformation',9],['3','Dimensional Model',10],
    ['4','Semantic Layer',9],['5','Quality & Observability',10],['6','Catalogue & Lineage',8],
    ['7','Security & Cost',6] ] } },

/* ---------------- M63 PROCESS AUTOMATION ---------------------------------------- */
window.FX_MODULES.M63 = { area:'A11', en:'Process Automation', bn:'প্রসেস অটোমেশন', icon:'⚙️', rail:'insight',
  desc:'Workflow engine with approval chains, DoA matrix, business-rule repository, unified task inbox, escalation.',
  kpis:[ {l:'Automation Rate',v:'71.4%',d:'+9pt',up:1,st:'ok',spark:[20,32,42,52,60,66,71.4]},
          {l:'Open Workflows',v:'1,842',st:'info'},
          {l:'Avg Approval Time',v:'3.2 h',d:'−1.1 h',up:1,st:'ok'},
          {l:'Rule Repository',v:'214 rules',st:'ok'},
          {l:'Escalations MTD',v:'31',st:'warn'},
          {l:'STP Share',v:'64%',st:'ok'} ],
  groups:[
    {en:'Engine', screens:[
      {id:'M63-definitions', en:'Workflow Definitions', bn:'ওয়ার্কফ্লো সংজ্ঞা', t:'g'},
      {id:'M63-monitor', en:'Instance Monitor', bn:'ইনস্ট্যান্স মনিটর', t:'g'},
      {id:'M63-jobs', en:'Scheduled Jobs', bn:'নির্ধারিত কাজ', t:'g'} ]},
    {en:'Approvals', screens:[
      {id:'M63-doa', en:'Delegation of Authority', bn:'ক্ষমতার প্রতিনিধিত্ব', t:'g'},
      {id:'M63-substitution', en:'Substitution / OOO', bn:'প্রতিনিধি', t:'g'} ]},
    {en:'Rules', screens:[
      {id:'M63-rules', en:'Business-Rule Repository', bn:'ব্যবসায়িক নিয়ম', t:'g'},
      {id:'M63-simulation', en:'Rule Simulation', bn:'নিয়ম সিমুলেশন', t:'c'} ]},
    {en:'Task Inbox', screens:[
      {id:'M63-inbox', en:'Unified Task Inbox', bn:'একত্র কাজের ইনবক্স', t:'c'} ]} ],
  reports:['Automation Rate by Process','Approval Cycle Time','Escalation Analysis','Rule Change Log'],
  forms:['Workflow Definition','Approval Chain','Business Rule'],
  cross:['Every module with approvals','M60 SoD in approvals','M29 identity context'],
  freg:{ src:54, sub:[
    ['1','Workflow Engine',11],['2','Approval Chains',10],['3','DoA Matrix',6],
    ['4','Business Rules',9],['5','Scheduled & Event Jobs',7],['6','Task Inbox',5],
    ['7','Audit & Performance',6] ] } },

/* ============ A12 · PLATFORM & TECHNOLOGY ============================= */

/* ---------------- M28 INTEGRATION, API & EVENTS ---------------------------------- */
window.FX_MODULES.M28 = { area:'A12', en:'Integration, API & Events', bn:'ইন্টিগ্রেশন ও এপিআই', icon:'🔌', rail:'platform',
  desc:'API gateway, 47 external connectors (bKash/Nagad/SSLCOMMERZ/Google Maps/Traccar), event bus, offline sync.',
  kpis:[ {l:'API p95',v:'312 ms',st:'ok',spark:[420,396,372,352,336,322,312]},
          {l:'Uptime',v:'99.96%',st:'ok'},
          {l:'Event Delivery',v:'99.97%',st:'ok'},
          {l:'DLQ Depth',v:'3',st:'warn'},
          {l:'Connectors Live',v:'47',st:'ok'},
          {l:'Sync Conflicts Today',v:'2',st:'warn'} ],
  groups:[
    {en:'Gateway', screens:[
      {id:'M28-apis', en:'API Catalogue', bn:'এপিআই ক্যাটালগ', t:'g'},
      {id:'M28-consumers', en:'Consumers & Credentials', bn:'ভোক্তা', t:'g'},
      {id:'M28-quotas', en:'Rate Limits & Quotas', bn:'সীমা', t:'g'} ]},
    {en:'Events', screens:[
      {id:'M28-topics', en:'Event Topics', bn:'ইভেন্ট টপিক', t:'g'},
      {id:'M28-schemas', en:'Schema Registry', bn:'স্কিমা রেজিস্ট্রি', t:'g'},
      {id:'M28-dlq', en:'Dead-Letter Queue', bn:'ডেড-লেটার', t:'c'},
      {id:'M28-replay', en:'Replay', bn:'রিপ্লে', t:'c'} ]},
    {en:'Connectors', screens:[
      {id:'M28-external', en:'47 External Connectors', bn:'বাহ্যিক সংযোগ', t:'g'},
      {id:'M28-health', en:'Connector Health', bn:'সংযোগ স্বাস্থ্য', t:'d'} ]},
    {en:'Sync', screens:[
      {id:'M28-offline', en:'Offline Sync Protocol', bn:'অফলাইন সিঙ্ক', t:'g'},
      {id:'M28-conflicts', en:'Conflict Resolution', bn:'দ্বন্দ্ব নিষ্পত্তি', t:'g'} ]} ],
  reports:['API Usage by Consumer','Event Delivery SLO','Connector Latency','DLQ Analysis','Webhook Success Rate'],
  forms:['API Consumer','Event Subscription','Connector Credential'],
  cross:['M29 token validation','M63 event automation','P02/P09/P11 offline','bKash/Nagad/SSLCOMMERZ'],
  freg:{ src:70, sub:[
    ['1','Gateway',10],['2','Versioning & Portals',6],['3','Outbox & Event Bus',12],
    ['4','Subscriptions & DLQ',9],['5','Webhooks',5],['6','Connector Framework (47)',12],
    ['7','Offline Sync',10],['8','Reconciliation',6] ] } },

/* ---------------- M29 IDENTITY, ACCESS & SECURITY -------------------------------- */
window.FX_MODULES.M29 = { area:'A12', en:'Identity, Access & Security', bn:'পরিচয় ও নিরাপত্তা', icon:'🔐', rail:'platform',
  desc:'MFA everywhere, 6 data-isolation tiers T0–T5, field-level permissions, SoD enforcement, immutable audit.',
  kpis:[ {l:'MFA Coverage',v:'100%',st:'ok'},
          {l:'Orphaned Accounts',v:'0',st:'ok'},
          {l:'Privileged Sessions',v:'6 active',st:'info'},
          {l:'SoD Conflicts',v:'0',st:'ok'},
          {l:'Access Certifications',v:'Q3 done',st:'ok'},
          {l:'Security Incidents MTD',v:'0',st:'ok'} ],
  groups:[
    {en:'Identity', screens:[
      {id:'M29-users', en:'Users', bn:'ব্যবহারকারী', t:'g'},
      {id:'M29-sessions', en:'Sessions & Device Trust', bn:'সেশন', t:'g'},
      {id:'M29-jml', en:'JML Automation', bn:'জেএমএল', t:'g'} ]},
    {en:'Access', screens:[
      {id:'M29-roles', en:'Roles & Permission Sets', bn:'ভূমিকা', t:'g'},
      {id:'M29-record', en:'Record Rules (T0–T5)', bn:'রেকর্ড নিয়ম', t:'g'},
      {id:'M29-fields', en:'Field-Level Permissions', bn:'ক্ষেত্র-স্তরের অনুমতি', t:'g'},
      {id:'M29-cert', en:'Access Certification', bn:'অ্যাক্সেস সার্টিফিকেশন', t:'c'} ]},
    {en:'Data Protection', screens:[
      {id:'M29-classification', en:'Classification (S0–S3)', bn:'শ্রেণিবিন্যাস', t:'g'},
      {id:'M29-residency', en:'Residency Enforcement', bn:'আবাসিক প্রয়োগ', t:'g'},
      {id:'M29-keys', en:'Encryption & Keys', bn:'এনক্রিপশন', t:'g'} ]},
    {en:'Monitoring', screens:[
      {id:'M29-audit', en:'Immutable Audit Trail', bn:'অডিট ট্রেইল', t:'g'},
      {id:'M29-privileged', en:'Privileged Access', bn:'বিশেষ সুবিধাভোগী', t:'g'},
      {id:'M29-incidents', en:'Security Incidents', bn:'নিরাপত্তা ঘটনা', t:'g'} ]} ],
  reports:['Access Review Pack','Privileged Session Log','Sensitive-Data Access','SoD Test Results','Authentication Trends'],
  forms:['User','Role','Record Rule','Access Request'],
  cross:['M21 JML events','M60 SoD definitions','M62 column security','All 12 portals SSO'],
  freg:{ src:78, sub:[
    ['1','Identity Lifecycle',10],['2','Authentication & MFA',11],['3','Roles & Record Rules',14],
    ['4','Field Permissions & SoD',11],['5','Certification',5],['6','Privileged Access',8],
    ['7','Data Protection',10],['8','Monitoring & Response',9] ] } },

/* ---------------- M30 PLATFORM ADMINISTRATION ------------------------------------ */
window.FX_MODULES.M30 = { area:'A12', en:'Platform Administration', bn:'প্ল্যাটফর্ম প্রশাসন', icon:'🛠️', rail:'platform',
  desc:'Legal entities, 51+ branch register with <1-day provisioning, config registry, feature flags, health console.',
  kpis:[ {l:'Branches',v:'53',st:'info'},
          {l:'Config Changes MTD',v:'184',st:'info'},
          {l:'Feature Flags',v:'42',st:'info'},
          {l:'Rollbacks MTD',v:'1',st:'warn'},
          {l:'Scheduled Jobs Healthy',v:'100%',st:'ok'},
          {l:'Announcements Active',v:'2',st:'info'} ],
  groups:[
    {en:'Organisation', screens:[
      {id:'M30-entities', en:'Legal Entities', bn:'আইনি সত্তা', t:'g'},
      {id:'M30-branches', en:'Branch Register (53)', bn:'শাখা রেজিস্টার', t:'g'},
      {id:'M30-provisioning', en:'Branch Provisioning (<1d)', bn:'শাখা প্রভিশনিং', t:'c'},
      {id:'M30-zones', en:'Dispatch Zones', bn:'ডিসপ্যাচ জোন', t:'g'} ]},
    {en:'Configuration', screens:[
      {id:'M30-params', en:'Parameter Registry', bn:'প্যারামিটার', t:'g'},
      {id:'M30-flags', en:'Feature Flags & Kill Switches', bn:'ফিচার ফ্ল্যাগ', t:'g'},
      {id:'M30-calendars', en:'Calendars & Shifts', bn:'ক্যালেন্ডার', t:'g'} ]},
    {en:'Operations', screens:[
      {id:'M30-jobs', en:'Scheduled Job Registry', bn:'নির্ধারিত কাজ', t:'g'},
      {id:'M30-health', en:'Platform Health Console', bn:'স্বাস্থ্য কনসোল', t:'d'},
      {id:'M30-env', en:'Environments', bn:'পরিবেশ', t:'g'},
      {id:'M30-backup', en:'Backup & DR', bn:'ব্যাকআপ', t:'g'} ]},
    {en:'Comms', screens:[
      {id:'M30-announcements', en:'System Announcements', bn:'সিস্টেম ঘোষণা', t:'g'},
      {id:'M30-release', en:'Release Coordination', bn:'রিলিজ সমন্বয়', t:'c'} ]} ],
  reports:['Config Change Log','Job Success Rate','Environment Inventory','Branch Provisioning Time'],
  forms:['Branch','Config Parameter','Feature Flag','Announcement'],
  cross:['M64 master data','M29 users','M47 sites','M65 country packs'],
  freg:{ src:64, sub:[
    ['1','Entity & Branch Register',12],['2','Provisioning',8],['3','Configuration Registry',10],
    ['4','Feature Flags',6],['5','Jobs & Queues',7],['6','Health & Observability',7],
    ['7','Backup / DR / Archival',7],['8','Announcements & Release',7] ] } },

/* ---------------- M64 MASTER DATA MANAGEMENT -------------------------------------- */
window.FX_MODULES.M64 = { area:'A12', en:'Master Data Management', bn:'মাস্টার ডেটা', icon:'🧬', rail:'platform',
  desc:'Domain ownership, stewardship workflow as only change path, DQ rule engine, golden-record survivorship.',
  kpis:[ {l:'Domains Governed',v:'18',st:'ok'},
          {l:'Steward Requests',v:'42 open',st:'warn'},
          {l:'DQ Score',v:'94.6%',st:'ok',spark:[82,85,87.4,89.8,91.8,93.4,94.6]},
          {l:'Golden Records',v:'2.86 M',st:'info'},
          {l:'Bulk Changes MTD',v:'6',st:'info'},
          {l:'Code Lists',v:'214',st:'info'} ],
  groups:[
    {en:'Governance', screens:[
      {id:'M64-domains', en:'Domain Register', bn:'ডোমেইন রেজিস্টার', t:'g'},
      {id:'M64-stewardship', en:'Stewardship Workflow', bn:'স্টুয়ার্ডশিপ', t:'c'} ]},
    {en:'Quality', screens:[
      {id:'M64-rules', en:'DQ Rule Engine', bn:'নিয়ম ইঞ্জিন', t:'g'},
      {id:'M64-scoring', en:'Quality Scoring & Gating', bn:'স্কোরিং', t:'r'},
      {id:'M64-dedupe', en:'Duplicate Detection', bn:'সদৃশ শনাক্তকরণ', t:'g'} ]},
    {en:'Reference Data', screens:[
      {id:'M64-codelists', en:'Code Lists', bn:'কোড তালিকা', t:'g'},
      {id:'M64-xref', en:'Cross-Reference Mapping', bn:'ক্রস-রেফারেন্স', t:'g'} ]},
    {en:'Change', screens:[
      {id:'M64-impact', en:'Impact Analysis', bn:'প্রভাব বিশ্লেষণ', t:'c'},
      {id:'M64-lineage', en:'Lineage', bn:'লিনেজ', t:'g'} ]} ],
  reports:['Data Quality by Domain','Stewardship SLA','Merge/Unmerge Audit','Code List Versions'],
  forms:['Steward Request','DQ Rule','Code List Entry'],
  cross:['M33 party golden records','M37 catalogue stewardship','M62 warehouse gating'],
  freg:{ src:52, sub:[
    ['1','Domain Register',6],['2','Stewardship',9],['3','DQ Rules & Scoring',11],
    ['4','Deduplication & Survivorship',10],['5','Reference Data',8],['6','Hierarchy & Lineage',8] ] } },

/* ---------------- M65 MULTI-ENTITY & LOCALISATION ---------------------------------- */
window.FX_MODULES.M65 = { area:'A12', en:'Multi-Entity & Localisation', bn:'বহু-সত্তা ও স্থানীয়করণ', icon:'🌍', rail:'platform',
  desc:'Country packs, bn-BD ICU collation & phonetic input, lakh/crore grouping, residency rules, expansion gateways.',
  kpis:[ {l:'Bengali Coverage',v:'100%',st:'ok'},
          {l:'Translation Gaps',v:'0',st:'ok'},
          {l:'Country Packs',v:'1 (BD)',st:'info'},
          {l:'Expansion Gateways',v:'3 planned',st:'info'},
          {l:'Onboarding Time',v:'≤ 12 weeks',st:'ok'},
          {l:'Locale Packs',v:'2',st:'ok'} ],
  groups:[
    {en:'Localisation', screens:[
      {id:'M65-bengali', en:'Bengali Support (bn-BD)', bn:'বাংলা সমর্থন', t:'g'},
      {id:'M65-translations', en:'Translation Infrastructure', bn:'অনুবাদ', t:'c'},
      {id:'M65-locales', en:'Locale Packs', bn:'লোকেল', t:'g'} ]},
    {en:'Country Packs', screens:[
      {id:'M65-packs', en:'Country Pack Authoring', bn:'দেশ প্যাক', t:'c'},
      {id:'M65-jurisdictions', en:'Jurisdiction Rules', bn:'এখতিয়ার নিয়ম', t:'g'} ]},
    {en:'Multi-Entity', screens:[
      {id:'M65-entities', en:'Entities per Country', bn:'সত্তা', t:'g'},
      {id:'M65-intercompany', en:'Intercompany', bn:'আন্তঃকোম্পানি', t:'g'} ]},
    {en:'Expansion', screens:[
      {id:'M65-gateways', en:'Payment Gateways (Razorpay/KBZPay/eSewa)', bn:'পেমেন্ট গেটওয়ে', t:'g'},
      {id:'M65-assessment', en:'Expansion Assessment', bn:'সম্প্রসারণ মূল্যায়ন', t:'r'} ]} ],
  reports:['Translation Completeness','Country Pack Inventory','Cross-Border Transfer Log'],
  forms:['Country Pack','Locale Pack','Jurisdiction Rule'],
  cross:['M51 tax config','M56 payroll rules','M29 residency','M50 payment methods'],
  freg:{ src:48, sub:[
    ['1','Country Packs',12],['2','Locale & Translation',9],['3','Bengali-Specific',8],
    ['4','Currency & Address',7],['5','Jurisdiction & Residency',7],['6','Expansion',5] ] } },

/* ---------------- M66 INTERNAL IT SERVICE MANAGEMENT ------------------------------- */
window.FX_MODULES.M66 = { area:'A12', en:'Internal IT Service', bn:'অভ্যন্তরীণ আইটি সেবা', icon:'🖥', rail:'platform',
  desc:'Employee service catalogue, incidents & changes, IT asset lifecycle, licence optimisation, CMDB.',
  kpis:[ {l:'Open Tickets',v:'34',st:'info'},
          {l:'First-Contact Resolution',v:'68%',st:'ok'},
          {l:'Licence Optimisation Saved',v:'৳ 3.4 L',st:'ok'},
          {l:'CMDB Coverage',v:'92.6%',st:'ok'},
          {l:'Changes in Freeze',v:'2',st:'warn'},
          {l:'Shadow-IT Detected',v:'5',st:'warn'} ],
  groups:[
    {en:'Service Desk', screens:[
      {id:'M66-catalogue', en:'Service Catalogue', bn:'সেবা ক্যাটালগ', t:'g'},
      {id:'M66-incidents', en:'Incidents', bn:'ঘটনা', t:'g'},
      {id:'M66-problems', en:'Problems', bn:'সমস্যা', t:'g'},
      {id:'M66-changes', en:'Changes', bn:'পরিবর্তন', t:'c'} ]},
    {en:'Assets', screens:[
      {id:'M66-assets', en:'IT Asset Lifecycle', bn:'আইটি সম্পদ', t:'g'},
      {id:'M66-licences', en:'Licences & Subscriptions', bn:'লাইসেন্স', t:'g'},
      {id:'M66-cmdb', en:'CMDB', bn:'সিএমডিবি', t:'g'} ]},
    {en:'Employee IT', screens:[
      {id:'M66-onboard', en:'Onboard/Offboard Workflows', bn:'অনবোর্ড/অফবোর্ড', t:'c'} ]} ],
  reports:['Ticket SLA Performance','Licence Utilisation','Asset Lifecycle Status','Change Success Rate'],
  forms:['Incident','Change','Asset','Service Request'],
  cross:['M21 JML triggers','M29 access requests','M19 cost centres'],
  freg:{ src:52, sub:[
    ['1','Service Catalogue',7],['2','Incident & Problem',12],['3','Change & Release',9],
    ['4','IT Asset Management',10],['5','Licence Optimisation',7],['6','CMDB',7] ] } },

/* ---------------- M67 PROJECT & PORTFOLIO ------------------------------------------- */
window.FX_MODULES.M67 = { area:'A12', en:'Projects & Portfolio', bn:'প্রকল্প ও পোর্টফোলিও', icon:'📁', rail:'platform',
  desc:'Branch openings, rollouts, bulk decommissions — WBS, earned value, milestone billing, portfolio stage gates.',
  kpis:[ {l:'Active Projects',v:'18',st:'info'},
          {l:'On-Time Milestones',v:'88.4%',st:'ok'},
          {l:'Budget Variance',v:'+1.8%',st:'ok'},
          {l:'At-Risk (RAG)',v:'2',st:'warn'},
          {l:'Milestone Billings MTD',v:'৳ 84 L',st:'info'},
          {l:'Benefits Tracked',v:'11 initiatives',st:'info'} ],
  groups:[
    {en:'Portfolio', screens:[
      {id:'M67-portfolio', en:'Portfolio Board', bn:'পোর্টফোলিও বোর্ড', t:'d'},
      {id:'M67-templates', en:'Templates (6 types)', bn:'টেমপ্লেট', t:'g'} ]},
    {en:'Delivery', screens:[
      {id:'M67-projects', en:'Projects', bn:'প্রকল্প', t:'g'},
      {id:'M67-record', en:'Project Record', bn:'প্রকল্প নথি', t:'f'},
      {id:'M67-wbs', en:'WBS & Tasks', bn:'কাজের বিভাজন', t:'g'},
      {id:'M67-resources', en:'Resource Planning', bn:'সম্পদ পরিকল্পনা', t:'g'} ]},
    {en:'Financials', screens:[
      {id:'M67-evm', en:'Earned Value', bn:'অর্জিত মূল্য', t:'r'},
      {id:'M67-billing', en:'Milestone Billing', bn:'মাইলস্টোন বিলিং', t:'g'},
      {id:'M67-profit', en:'Project P&L', bn:'প্রকল্প লাভ-ক্ষতি', t:'r'} ]},
    {en:'Risk', screens:[
      {id:'M67-risks', en:'Risk & Issue Registers', bn:'ঝুঁকি রেজিস্টার', t:'g'},
      {id:'M67-gates', en:'Stage Gates', bn:'স্টেজ গেট', t:'c'} ]} ],
  reports:['Portfolio Health','Earned Value Analysis','Milestone Billing Register','Resource Utilisation','Benefits Realisation'],
  forms:['Project (6 types)','Milestone','Task','Stage Gate Review'],
  cross:['M30 branch openings','M20 milestone invoices','M21 resources','P04 client status'],
  freg:{ src:54, sub:[
    ['1','Project Object & WBS',12],['2','Scheduling & Baselines',9],['3','Resources',8],
    ['4','Cost & Earned Value',10],['5','Milestone Billing',6],['6','Risk & Gates',9] ] } }
;
})();
