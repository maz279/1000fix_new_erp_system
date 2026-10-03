/* =====================================================================
   1000 FiX ERP — NAV DATA part 1 of 3: areas + Categories A & B
   Authored from the ERP Module Catalogue Master Register (02-02) and
   the 67 module specifications (1000fix_ERP_Module/03_Modules).
   Screen types: w workspace · g grid · f form/record · r report ·
   c console · d dashboard · x 360 · s scaffold(generated).
   freg = function register (sub-modules × function counts) — the
   machine-checkable "every function accounted for" evidence.
   ===================================================================== */
window.FX_AREAS = [
  { id:'A01', key:'home',       en:'Home',                    bn:'হোম',                       mods:[] },
  { id:'A02', key:'service',    en:'Service Operations',      bn:'সার্ভিস অপারেশন',          mods:['M01','M02','M31','M03','M04','M05','M06'] },
  { id:'A03', key:'customer',   en:'Customer Experience',     bn:'গ্রাহক অভিজ্ঞতা',           mods:['M33','M07','M10','M34','M27','M32','M35'] },
  { id:'A04', key:'commercial', en:'Commercial & Revenue',    bn:'বাণিজ্যিক ও রাজস্ব',        mods:['M37','M11','M36','M08','M09','M39','M38','M12','M40'] },
  { id:'A05', key:'circular',   en:'Circular Economy',        bn:'সার্কুলার ইকোনমি',         mods:['M13','M14','M18'] },
  { id:'A06', key:'supply',     en:'Supply Chain',            bn:'সরবরাহ শৃঙ্খল',             mods:['M15','M41','M16','M42','M43','M44'] },
  { id:'A07', key:'assets',     en:'Assets & Facilities',     bn:'সম্পদ ও সুবিধা',            mods:['M17','M45','M46','M47','M48'] },
  { id:'A08', key:'finance',    en:'Finance & Treasury',      bn:'অর্থ ও কোষাগার',            mods:['M19','M20','M52','M50','M51','M53','M49','M54'] },
  { id:'A09', key:'people',     en:'People & Workforce',      bn:'জনবল',                      mods:['M21','M55','M56','M57','M22','M58','M59'] },
  { id:'A10', key:'quality',    en:'Quality & Governance',    bn:'গুণগতমান ও গভর্নেন্স',      mods:['M23','M60','M24','M61'] },
  { id:'A11', key:'insight',    en:'Insights & Intelligence', bn:'বিশ্লেষণ ও বুদ্ধিমত্তা',     mods:['M25','M26','M62','M63'] },
  { id:'A12', key:'platform',   en:'Platform & Technology',   bn:'প্ল্যাটফর্ম ও প্রযুক্তি',    mods:['M28','M29','M30','M64','M65','M66','M67'] }
];
window.FX_PORTALS = ['P01','P02','P03','P04','P05','P06','P07','P08','P09','P10','P11','P12'];

window.FX_MODULES = {

/* ============ A02 · SERVICE OPERATIONS ============================== */

/* ---------------- M01 SERVICE REQUEST & ORDER MANAGEMENT ------------ */
M01: { area:'A02', en:'Service Requests & Orders', bn:'সার্ভিস অর্ডার', icon:'📋', rail:'service',
  desc:'Master record of every service need from 12 intake channels — lifecycle, entitlement, estimates, SLA.',
  kpis:[ {l:'Open Orders',v:'1,284',d:'+62 today',spark:[1180,1195,1220,1240,1252,1268,1284]},
          {l:'SLA At-Risk',v:'37',st:'warn',spark:[52,48,44,41,39,38,37]},
          {l:'TAT < 24h (IT)',v:'91.2%',d:'+1.4pt',up:1,st:'ok',spark:[85,86,88,89,90,91,91.2]},
          {l:'Estimate Conv.',v:'78.4%',d:'+2.1pt',up:1,st:'ok'},
          {l:'Intake < 3 min',v:'2m 41s',st:'ok'},
          {l:'Rework Rate',v:'2.6%',d:'−0.4pt',up:1,st:'ok'} ],
  groups:[
    {en:'Intake & Channels', screens:[
      {id:'M01-board', en:'Order Operations Board', bn:'অর্ডার বোর্ড', t:'d'},
      {id:'M01-all', en:'All Service Orders', bn:'সকল অর্ডার', t:'g'},
      {id:'M01-intake', en:'Omni-Channel Intake', bn:'চ্যানেল ইনটেক', t:'c'},
      {id:'M01-channels', en:'Channel Performance', bn:'চ্যানেল পারফরম্যান্স', t:'r'},
      {id:'M01-hotline', en:'Hotline 16743 Queue', bn:'হটলাইন ১৬৭৪৩', t:'g'} ]},
    {en:'Order Lifecycle', screens:[
      {id:'M01-order', en:'Service Order Record', bn:'অর্ডার নথি', t:'f'},
      {id:'M01-types', en:'Order Types (12)', bn:'অর্ডারের ধরন', t:'g'},
      {id:'M01-wip', en:'WIP & Ageing Analysis', bn:'চলমান কাজ', t:'r'},
      {id:'M01-holds', en:'Hold Management', bn:'হোল্ড ব্যবস্থাপনা', t:'g'},
      {id:'M01-rework', en:'Rework Detection', bn:'রিওয়ার্ক শনাক্তকরণ', t:'g'} ]},
    {en:'Diagnosis & Estimates', screens:[
      {id:'M01-templates', en:'Diagnostic Templates', bn:'ডায়াগনস্টিক টেমপ্লেট', t:'g'},
      {id:'M01-fault', en:'Fault & Symptom Coding', bn:'ত্রুটি কোডিং', t:'g'},
      {id:'M01-estimates', en:'Estimates & Approvals', bn:'অনুমান ও অনুমোদন', t:'g'},
      {id:'M01-thresholds', en:'Approval Thresholds', bn:'অনুমোদন সীমা', t:'g'} ]},
    {en:'Entitlement & SLA', screens:[
      {id:'M01-entitle', en:'Entitlement Evaluation', bn:'সুবিধা মূল্যায়ন', t:'g'},
      {id:'M01-sla', en:'SLA Policies & Clocks', bn:'এসএলএ নীতি', t:'g'},
      {id:'M01-esc', en:'Escalation Rules', bn:'এসকালেশন নিয়ম', t:'g'},
      {id:'M01-sla-rep', en:'SLA Compliance Report', bn:'এসএলএ রিপোর্ট', t:'r'} ]},
    {en:'Quality & Release', screens:[
      {id:'M01-qc', en:'QC Checkpoints', bn:'কিউসি চেকপয়েন্ট', t:'g'},
      {id:'M01-reports', en:'Service Reports', bn:'সার্ভিস রিপোর্ট', t:'g'},
      {id:'M01-rwty', en:'Repair Warranty Issuance', bn:'মেরামত ওয়ারেন্টি', t:'g'} ]} ],
  reports:['Daily Intake by Channel','WIP Ageing by Branch','SLA Compliance & Escalations','Estimate Conversion Funnel','Rework & Repeat-Fault Analysis','Order Cycle-Time (TAT) Distribution','Uncollected Device Register'],
  forms:['Service Order (12 channels, 34 fields)','Estimate Request','Hold / Release Reason','QC Checklist Result'],
  cross:['M02 dispatch handoff','M31 workshop routing','M09 entitlement check at intake','M20 invoice on closure','M17 device history'],
  freg:{ src:128, sub:[
    ['1','Omni-Channel Intake (12 channels)',14],['2','Lifecycle State Machine',9],
    ['3','Entitlement Evaluation',8],['4','Complaint & Fault Coding',10],
    ['5','Diagnostic Templates',7],['6','Estimate & Approval Loop',12],
    ['7','Assignment Handoff',6],['8','SLA Policy / Clock / Escalation',13],
    ['9','Hold Management',5],['10','QC Checkpoints & Rework',11],
    ['11','Service Reports & Repair Warranty',12],['12','Ops Boards & WIP Analysis',11],['13','API & Domain Events',10] ] } },

/* ---------------- M02 FIELD SERVICE & DISPATCH ---------------------- */
M02: { area:'A02', en:'Field Service & Dispatch', bn:'ফিল্ড সার্ভিস ও ডিসপ্যাচ', icon:'🚐', rail:'service',
  desc:'AI dispatch board, route optimisation, technician app (24h offline), GPS tracking, field evidence & payments.',
  kpis:[ {l:'Jobs / Tech / Day',v:'7.2',d:'+0.8',up:1,spark:[4.6,5.1,5.7,6.2,6.7,7.0,7.2]},
          {l:'Auto-Assignment',v:'68%',d:'+6pt',up:1,st:'ok',spark:[22,31,40,49,58,64,68]},
          {l:'On-Time Arrival',v:'93.4%',st:'ok',spark:[88,89,90,92,92,93,93.4]},
          {l:'Travel Time Share',v:'24%',d:'−3pt',up:1,st:'ok',spark:[35,33,31,29,27,25,24]},
          {l:'Unassigned > 15m',v:'6',st:'warn'},
          {l:'Offline Sync Health',v:'99.7%',st:'ok'} ],
  groups:[
    {en:'Dispatch Console', screens:[
      {id:'M02-dispatch', en:'Dispatch Board (Live)', bn:'ডিসপ্যাচ বোর্ড', t:'d'},
      {id:'M02-map', en:'Live Technician Map', bn:'লাইভ ম্যাপ', t:'d'},
      {id:'M02-unassigned', en:'Unassigned Queue', bn:'অনির্ধারিত সারি', t:'g'},
      {id:'M02-sla-risk', en:'SLA Risk Board', bn:'এসএলএ ঝুঁকি', t:'g'} ]},
    {en:'Work Orders', screens:[
      {id:'M02-wo', en:'Field Work Orders', bn:'ফিল্ড ওয়ার্ক অর্ডার', t:'g'},
      {id:'M02-record', en:'Work Order Record', bn:'ওয়ার্ক অর্ডার নথি', t:'f'},
      {id:'M02-exceptions', en:'Field Exceptions', bn:'ফিল্ড ব্যতিক্রম', t:'g'},
      {id:'M02-crews', en:'Crews & Multi-Tech Jobs', bn:'ক্রু নিয়োগ', t:'g'} ]},
    {en:'Routing & Territories', screens:[
      {id:'M02-zones', en:'Zones & Geofences', bn:'জোন ও জিওফেন্স', t:'g'},
      {id:'M02-routes', en:'Route Optimisation', bn:'রুট অপ্টিমাইজেশন', t:'c'},
      {id:'M02-territory', en:'Territory Balancing', bn:'টেরিটরি সমন্বয়', t:'r'} ]},
    {en:'Technician App (P02)', screens:[
      {id:'M02-day', en:'Day / Job Queue Preview', bn:'দিনের কাজ', t:'d'},
      {id:'M02-offline', en:'Offline Sync Monitor', bn:'অফলাইন সিঙ্ক', t:'g'},
      {id:'M02-evidence', en:'Field Evidence Hub', bn:'ফিল্ড প্রমাণ', t:'g'},
      {id:'M02-vanstock', en:'Van Stock Consumption', bn:'ভ্যান স্টক', t:'g'} ]},
    {en:'Safety & Payments', screens:[
      {id:'M02-loneworker', en:'Lone-Worker Check-In', bn:'একাকী কর্মী নিরাপত্তা', t:'g'},
      {id:'M02-panic', en:'Panic Alert Log', bn:'প্যানিক অ্যালার্ট', t:'g'},
      {id:'M02-fieldpay', en:'On-Site Payments', bn:'স্থানে পেমেন্ট', t:'g'},
      {id:'M02-cashrec', en:'Daily Cash Reconciliation', bn:'নগদ মিলকরণ', t:'c'} ]} ],
  reports:['Dispatch Performance by Zone','Travel-Time Analysis','Jobs per Technician','Field Exception Summary','Van Stock Variance','On-Site Payment Reconciliation'],
  forms:['Field Work Order','Field Exception Report','Crew Assignment','Route Plan'],
  cross:['M01 order → work order','M55 availability & roster','M22 certification gate','M03 logistics handover','M17 asset context'],
  freg:{ src:106, sub:[
    ['1','Candidate Scoring & Assignment',14],['2','Dispatch Board',10],
    ['3','Route Optimisation & Re-optimisation',9],['4','Territory / Zone / Geofence',8],
    ['5','Work-Order Lifecycle',9],['6','Technician Mobile App',18],
    ['7','Offline Sync & Conflict Resolution',7],['8','GPS Tracking & ETA',7],
    ['9','Field Evidence Capture',6],['10','Van Stock',5],['11','On-Site Payment',6],['12','Field Safety',7] ] } },

/* ---------------- M31 WORKSHOP & DEPOT REPAIR ------------------------ */
M31: { area:'A02', en:'Workshop & Depot Repair', bn:'ওয়ার্কশপ মেরামত', icon:'🔧', rail:'service',
  desc:'Bench repair L1/L2/L3, serial genealogy, burn-in testing, workshop costing and knowledge capture.',
  kpis:[ {l:'On Bench',v:'212',st:'info',spark:[190,196,201,205,208,210,212]},
          {l:'First-Pass Yield',v:'94.1%',st:'ok',spark:[90,91,92,93,93.6,94,94.1]},
          {l:'L3 Queue > 48h',v:'9',st:'warn'},
          {l:'Avg Bench Days',v:'2.1',d:'−0.3',up:1,st:'ok'},
          {l:'Parts Fitment',v:'98.8%',st:'ok'},
          {l:'Internal Rework',v:'1.9%',d:'−0.5pt',up:1,st:'ok'} ],
  groups:[
    {en:'Repair Orders', screens:[
      {id:'M31-orders', en:'Repair Orders', bn:'মেরামত অর্ডার', t:'g'},
      {id:'M31-record', en:'Repair Order Record', bn:'মেরামত নথি', t:'f'},
      {id:'M31-transfer', en:'Workshop Transfers', bn:'ওয়ার্কশপ স্থানান্তর', t:'g'} ]},
    {en:'Bench Board', screens:[
      {id:'M31-benches', en:'Bench & WIP Board', bn:'বেঞ্চ বোর্ড', t:'d'},
      {id:'M31-benchmaster', en:'Bench Master (Capacity)', bn:'বেঞ্চ মাস্টার', t:'g'},
      {id:'M31-levels', en:'L1/L2/L3 Classification', bn:'স্তর শ্রেণিবিভাগ', t:'g'} ]},
    {en:'Execution', screens:[
      {id:'M31-diag', en:'Component Diagnosis', bn:'কম্পোনেন্ট ডায়াগনোসিস', t:'g'},
      {id:'M31-parts', en:'Parts Consumption', bn:'পার্টস ব্যবহার', t:'g'},
      {id:'M31-testing', en:'Test Protocols & Burn-In', bn:'টেস্ট ও বার্ন-ইন', t:'g'} ]},
    {en:'Costing & Knowledge', screens:[
      {id:'M31-costing', en:'Repair Costing', bn:'মেরামত ব্যয়', t:'r'},
      {id:'M31-throughput', en:'Throughput Analytics', bn:'থ্রুপুট বিশ্লেষণ', t:'r'},
      {id:'M31-methods', en:'Repair-Method Capture', bn:'মেরামত পদ্ধতি', t:'g'} ]} ],
  reports:['Bench Utilisation by Workshop','Repair Cycle Time by Level','Internal Rework Loop Analysis','Workshop Cost per Repair','Parts Genealogy Trace','Burn-In Failure Report'],
  forms:['Repair Order','Bench Allocation','Test Protocol Result','Workshop Transfer'],
  cross:['M01 device release','M15 parts consumption','M61 knowledge capture','M45 test equipment','M22 skill routing'],
  freg:{ src:76, sub:[
    ['1','Repair Order Creation',8],['2','Workshop & Bench Master',9],
    ['3','Bench Allocation & Queue',10],['4','Repair-Level Routing',7],
    ['5','Diagnosis & Execution',13],['6','Parts Consumption & Genealogy',8],
    ['7','Testing & Burn-In',8],['8','Rework & Transfers',6],['9','Repair Costing',7] ] } },

/* ---------------- M03 SERVICE & REVERSE LOGISTICS -------------------- */
M03: { area:'A02', en:'Service Logistics (Pick & Drop)', bn:'সার্ভিস লজিস্টিক', icon:'📦', rail:'service',
  desc:'Multi-leg consignments, unbroken chain of custody, POD with OTP, rider app, courier partners, COD.',
  kpis:[ {l:'In Transit',v:'148',st:'info',spark:[130,136,140,144,146,147,148]},
          {l:'On-Time Delivery',v:'93.6%',st:'ok',spark:[89,90,91,92,93,93.4,93.6]},
          {l:'Custody Exceptions',v:'0',st:'ok'},
          {l:'COD Today',v:'৳ 2.14 L',st:'info'},
          {l:'Avg Round Trip',v:'1.8 d',d:'−0.2',up:1,st:'ok'},
          {l:'Rider Shifts Open',v:'23',st:'info'} ],
  groups:[
    {en:'Consignments', screens:[
      {id:'M03-cons', en:'Consignments', bn:'কনসাইনমেন্ট', t:'g'},
      {id:'M03-record', en:'Consignment Record', bn:'কনসাইনমেন্ট নথি', t:'f'},
      {id:'M03-journeys', en:'Multi-Leg Journeys', bn:'বহু-পর্যায় যাত্রা', t:'g'},
      {id:'M03-manifest', en:'Item Manifests', bn:'আইটেম ম্যানিফেস্ট', t:'g'} ]},
    {en:'Custody & POD', screens:[
      {id:'M03-custody', en:'Chain-of-Custody Ledger', bn:'কাস্টডি লেজার', t:'g'},
      {id:'M03-pod', en:'Proof of Delivery (OTP)', bn:'ডেলিভারি প্রমাণ', t:'g'},
      {id:'M03-seals', en:'Sealing & Tamper Log', bn:'সিল ও ট্যাম্পার', t:'g'} ]},
    {en:'Riders & Fleet', screens:[
      {id:'M03-riders', en:'Rider Assignment', bn:'রাইডার নিয়োগ', t:'g'},
      {id:'M03-routes', en:'Route Manifests', bn:'রুট ম্যানিফেস্ট', t:'g'},
      {id:'M03-app', en:'Rider App (P09) Preview', bn:'রাইডার অ্যাপ', t:'d'} ]},
    {en:'Courier Partners', screens:[
      {id:'M03-couriers', en:'Courier Partners', bn:'কুরিয়ার পার্টনার', t:'g'},
      {id:'M03-bookings', en:'Courier Bookings', bn:'কুরিয়ার বুকিং', t:'g'},
      {id:'M03-recon', en:'Courier Reconciliation', bn:'কুরিয়ার মিলকরণ', t:'c'} ]},
    {en:'Exceptions & Billing', screens:[
      {id:'M03-exc', en:'Loss / Damage Claims', bn:'ক্ষতির দাবি', t:'g'},
      {id:'M03-charges', en:'Distance & Zone Charging', bn:'দূরত্ব চার্জ', t:'g'},
      {id:'M03-cod', en:'COD Reconciliation', bn:'সিওডি মিলকরণ', t:'c'} ]} ],
  reports:['Consignment Cycle Time','Custody Exception Register','Courier Performance (Pathao/RedX/Steadfast)','COD Settlement Report','Reverse Logistics Volume','Damage & Insurance Claims'],
  forms:['Consignment (5 types)','Rider Shift Open/Close','Courier Booking','Damage Claim'],
  cross:['M01 pick&drop orders','M04 counter handover','M46 fleet & drivers','M50 COD settlement','M17 custody chain'],
  freg:{ src:93, sub:[
    ['1','Consignment Creation (5 types)',10],['2','Multi-Leg Journeys',8],
    ['3','Item Manifest',7],['4','Chain of Custody',12],['5','POD (OTP/Signature/Photo)',8],
    ['6','Packaging & Sealing',5],['7','Scheduling & Windows',6],['8','Rider Assignment & App',10],
    ['9','Courier Partners',9],['10','Charging & Waivers',6],['11','Reverse Flows',5],['12','COD & Claims',7] ] } },

/* ---------------- M04 BRANCH & FRONT-DESK ---------------------------- */
M04: { area:'A02', en:'Branch & Front-Desk', bn:'শাখা ও ফ্রন্ট ডেস্ক', icon:'🏢', rail:'service',
  desc:'Counter operations at 51+ centres — token queue, device custody, cash drawer, shift close, counter sales.',
  kpis:[ {l:'Tokens Today',v:'4,236',st:'info',spark:[3900,3980,4050,4110,4170,4200,4236]},
          {l:'Avg Wait',v:'11 min',d:'−2 min',up:1,st:'ok'},
          {l:'Uncollected > 7d',v:'38',st:'warn'},
          {l:'Cash Variance Today',v:'৳ 0',st:'ok'},
          {l:'Shifts Open',v:'51',st:'info'},
          {l:'Counter Sales MTD',v:'৳ 18.4 L',d:'+7%',up:1} ],
  groups:[
    {en:'Queue & Token', screens:[
      {id:'M04-queue', en:'Token & Waiting Display', bn:'টোকেন ও অপেক্ষা', t:'d'},
      {id:'M04-counter', en:'Counter Workstation', bn:'কাউন্টার ওয়ার্কস্টেশন', t:'c'},
      {id:'M04-priority', en:'Priority Queue Rules', bn:'অগ্রাধিকার নিয়ম', t:'g'} ]},
    {en:'Device Custody', screens:[
      {id:'M04-storage', en:'Storage Locations', bn:'সংরক্ষণ অবস্থান', t:'g'},
      {id:'M04-handover', en:'Collection & Handover', bn:'সংগ্রহ ও হস্তান্তর', t:'g'},
      {id:'M04-uncollected', en:'Uncollected Devices', bn:'অসংগৃহীত ডিভাইস', t:'g'} ]},
    {en:'Cash & Shift', screens:[
      {id:'M04-drawer', en:'Cash Drawer', bn:'নগদ ড্রয়ার', t:'g'},
      {id:'M04-payments', en:'Payment Capture (All Methods)', bn:'পেমেন্ট গ্রহণ', t:'g'},
      {id:'M04-shift', en:'Shift Open / Close', bn:'শিফট খোলা/বন্ধ', t:'c'},
      {id:'M04-banking', en:'Banking Deposits', bn:'ব্যাংক জমা', t:'g'} ]},
    {en:'Counter Sales', screens:[
      {id:'M04-sales', en:'Counter Sales (Parts/Plans)', bn:'কাউন্টার বিক্রয়', t:'g'},
      {id:'M04-kiosk', en:'Kiosk Mode', bn:'কিয়স্ক মোড', t:'d'} ]},
    {en:'Branch Ops', screens:[
      {id:'M04-checklists', en:'Open/Close Checklists', bn:'চেকলিস্ট', t:'g'},
      {id:'M04-dashboard', en:'Branch Ops Dashboard', bn:'শাখা ড্যাশবোর্ড', t:'d'},
      {id:'M04-receipts', en:'Receipt & Label Printing', bn:'রিসিট প্রিন্ট', t:'g'} ]} ],
  reports:['Branch Daily Cash Summary','Token Wait-Time Distribution','Uncollected Device Ageing','Counter Sales by Category','Shift Variance Register','Branch Comparison League'],
  forms:['Token Issue','Device Storage Assignment','Shift Open/Close','Counter Sale','Handover (ID verified)'],
  cross:['M01 walk-in intake','M03 collection/delivery','M20 receipts','M47 branch infrastructure','M17 device custody'],
  freg:{ src:95, sub:[
    ['1','Token & Queue',12],['2','Counter Workstation',14],
    ['3','Device Storage & Retrieval',10],['4','Collection & Handover',9],
    ['5','Counter Sales',8],['6','Cash Drawer',12],['7','Payment Capture',9],
    ['8','Shift Operations',10],['9','Banking & Deposits',5],['10','Branch Admin',6] ] } },

/* ---------------- M05 REMOTE SUPPORT & MANAGED SERVICES -------------- */
M05: { area:'A02', en:'Remote Support & MSP', bn:'রিমোট সাপোর্ট ও এমএসপি', icon:'🖥️', rail:'service',
  desc:'Managed IT services — remote sessions, monitored estate, alert-to-ticket, runbooks, patching, SLA credits.',
  kpis:[ {l:'Monitored Assets',v:'4,872',d:'+118',up:1,spark:[4200,4360,4480,4610,4720,4800,4872]},
          {l:'Remote Resolution',v:'64.2%',st:'ok',spark:[55,57,59,61,63,64,64.2]},
          {l:'Open MSP Tickets',v:'64',st:'info'},
          {l:'SLA Credits MTD',v:'৳ 12.4 K',st:'warn'},
          {l:'Patch Compliance',v:'97.1%',st:'ok'},
          {l:'On-Call Escalations',v:'3',st:'warn'} ],
  groups:[
    {en:'Remote Sessions', screens:[
      {id:'M05-sessions', en:'Remote Sessions', bn:'রিমোট সেশন', t:'g'},
      {id:'M05-console', en:'Session Console', bn:'সেশন কনসোল', t:'c'} ]},
    {en:'Monitored Estate', screens:[
      {id:'M05-estate', en:'Estate & Agents', bn:'এস্টেট ও এজেন্ট', t:'g'},
      {id:'M05-health', en:'Health Scoring', bn:'স্বাস্থ্য স্কোর', t:'d'},
      {id:'M05-alerts', en:'Alert Rules & Inbox', bn:'অ্যালার্ট', t:'g'} ]},
    {en:'Service Desk', screens:[
      {id:'M05-tickets', en:'MSP Tickets', bn:'এমএসপি টিকেট', t:'g'},
      {id:'M05-oncall', en:'On-Call Rota', bn:'অন-কল রোটা', t:'g'},
      {id:'M05-runbooks', en:'Runbooks & Auto-Remediation', bn:'রানবুক', t:'g'} ]},
    {en:'Compliance', screens:[
      {id:'M05-patching', en:'Patch Management', bn:'প্যাচ ব্যবস্থাপনা', t:'g'},
      {id:'M05-windows', en:'Maintenance Windows', bn:'মেইনটেনেন্স উইন্ডো', t:'g'},
      {id:'M05-problem', en:'Problem & Change', bn:'সমস্যা ও পরিবর্তন', t:'g'} ]},
    {en:'Client Reporting', screens:[
      {id:'M05-sla', en:'SLA Attainment', bn:'এসএলএ অর্জন', t:'r'},
      {id:'M05-reviews', en:'Client Service Reviews', bn:'ক্লায়েন্ট রিভিউ', t:'g'} ]} ],
  reports:['MSP SLA Attainment by Client','Remote Resolution Rate','Patch Compliance Report','Alert-to-Ticket Conversion','Backup & Restore Test Log','SLA Credit Register'],
  forms:['Remote Session (consent recorded)','MSP Ticket','Change Record','Maintenance Window'],
  cross:['M08 contract entitlement','M17 monitored assets','M48 telemetry streams','M20 SLA credit billing','P04 client portal'],
  freg:{ src:93, sub:[
    ['1','Remote Sessions',10],['2','Monitored Estate',12],['3','Metrics & Health Scoring',9],
    ['4','Alerting Engine',11],['5','On-Call & Escalation',7],['6','Runbooks & Remediation',8],
    ['7','Patch Management',9],['8','MSP Service Desk',13],['9','Client Reporting',9],['10','Onboarding Projects',5] ] } },

/* ---------------- M06 DATA SERVICES ---------------------------------- */
M06: { area:'A02', en:'Data Services & Recovery', bn:'ডেটা সেবা ও রিকভারি', icon:'💾', rail:'service',
  desc:'Data recovery case management, sealed media custody, secure destruction with certificates, backup plans.',
  kpis:[ {l:'Active Cases',v:'26',st:'info',spark:[22,23,24,25,25,26,26]},
          {l:'Recovery Success',v:'82.4%',st:'ok',spark:[74,76,78,80,81,82,82.4]},
          {l:'Cleanroom Slots',v:'4 free',st:'ok'},
          {l:'Destruction Certs MTD',v:'61',st:'info'},
          {l:'Eval Turnaround',v:'1.2 d',st:'ok'},
          {l:'Purge Verifications',v:'100%',st:'ok'} ],
  groups:[
    {en:'Recovery Cases', screens:[
      {id:'M06-cases', en:'Recovery Cases', bn:'রিকভারি কেস', t:'g'},
      {id:'M06-record', en:'Case Record (7 specialisms)', bn:'কেস নথি', t:'f'},
      {id:'M06-attempts', en:'Attempt Tracking', bn:'প্রচেষ্টা ট্র্যাকিং', t:'g'} ]},
    {en:'Media Custody', screens:[
      {id:'M06-custody', en:'Sealed Media Custody', bn:'সিলড মিডিয়া', t:'g'},
      {id:'M06-cleanroom', en:'Cleanroom Schedule', bn:'ক্লিনরুম', t:'g'},
      {id:'M06-inventory', en:'Recovered-Data Inventory', bn:'উদ্ধার তালিকা', t:'g'} ]},
    {en:'Quotation & Handover', screens:[
      {id:'M06-eval', en:'Free Evaluations', bn:'ফ্রি মূল্যায়ন', t:'g'},
      {id:'M06-quotes', en:'Firm Quotations', bn:'চূড়ান্ত কোট', t:'g'},
      {id:'M06-handover', en:'Secure Handover & Purge', bn:'নিরাপদ হস্তান্তর', t:'c'} ]},
    {en:'Backup & Destruction', screens:[
      {id:'M06-backup', en:'Backup Plans & Tests', bn:'ব্যাকআপ পরিকল্পনা', t:'g'},
      {id:'M06-destroy', en:'Secure Destruction', bn:'নিরাপদ ধ্বংস', t:'c'},
      {id:'M06-certs', en:'Destruction Certificates', bn:'ধ্বংস সনদ', t:'g'} ]} ],
  reports:['Recovery Success by Specialism','Case Cycle Time','Data Service Revenue','Destruction & Purge Audit','Backup Restore-Test Compliance'],
  forms:['Recovery Case','Media Intake (sealed)','Firm Quotation','Destruction Request (dual control)'],
  cross:['M36 recovery quotations','M24 evidence certificates','M18 e-waste routing','M01 data-service orders'],
  freg:{ src:75, sub:[
    ['1','Case Management (7 specialisms)',12],['2','Media Chain of Custody',11],
    ['3','Evaluation & Quotation',8],['4','Methodology Logging',6],['5','Attempt Tracking',5],
    ['6','Recovered-Data Inventory',5],['7','Secure Handover & Purge',7],['8','Backup Plans',6],
    ['9','Secure Destruction',9],['10','Access Control & Audit',6] ] } },

/* ============ A03 · CUSTOMER EXPERIENCE ============================== */

/* ---------------- M33 CUSTOMER & PARTY MASTER ------------------------- */
M33: { area:'A03', en:'Customer & Party Master', bn:'গ্রাহক মাস্টার', icon:'🪪', rail:'customer',
  desc:'Single golden record for every party — roles, hierarchies, OTP verification, consent, segments, credit.',
  kpis:[ {l:'Active Customers',v:'1.42 M',spark:[1.18,1.22,1.27,1.31,1.36,1.39,1.42]},
          {l:'Duplicate Rate',v:'0.9%',d:'−1.6pt',up:1,st:'ok'},
          {l:'Golden Coverage',v:'97.8%',st:'ok'},
          {l:'Consent Current',v:'95.2%',st:'ok'},
          {l:'Credit Holds',v:'214',st:'warn'},
          {l:'New Today',v:'1,864',st:'info'} ],
  groups:[
    {en:'Party Records', screens:[
      {id:'M33-directory', en:'Party Directory', bn:'পার্টি তালিকা', t:'g'},
      {id:'M33-party', en:'Party Record (roles)', bn:'পার্টি নথি', t:'f'},
      {id:'M33-360', en:'Customer 360', bn:'গ্রাহক ৩৬০', t:'x'},
      {id:'M33-hierarchy', en:'Account Hierarchies', bn:'অ্যাকাউন্ট স্তর', t:'g'} ]},
    {en:'Identity & Verification', screens:[
      {id:'M33-identity', en:'Identity Documents (NID/BIN)', bn:'পরিচয়পত্র', t:'g'},
      {id:'M33-otp', en:'OTP Verification Log', bn:'ওটিপি যাচাই', t:'g'},
      {id:'M33-approval', en:'Registration Approvals', bn:'নিবন্ধন অনুমোদন', t:'c'} ]},
    {en:'Data Quality', screens:[
      {id:'M33-dedupe', en:'Duplicate Detection', bn:'সদৃশ শনাক্তকরণ', t:'g'},
      {id:'M33-merge', en:'Supervised Merge', bn:'মার্জ তত্ত্বাবধান', t:'c'},
      {id:'M33-quality', en:'Quality Scoring', bn:'গুণগত স্কোর', t:'r'} ]},
    {en:'Consent & Rights', screens:[
      {id:'M33-consent', en:'Consent Register', bn:'সম্মতি রেজিস্টার', t:'g'},
      {id:'M33-dsr', en:'Data-Subject Requests', bn:'ডেটা অনুরোধ', t:'c'} ]},
    {en:'Segments & Credit', screens:[
      {id:'M33-segments', en:'Segments', bn:'সেগমেন্ট', t:'g'},
      {id:'M33-credit', en:'Credit Profiles & Holds', bn:'ক্রেডিট প্রোফাইল', t:'g'},
      {id:'M33-status', en:'Party Status Lifecycle', bn:'স্ট্যাটাস জীবনচক্র', t:'g'} ]} ],
  reports:['Customer Growth by District','Data Quality Scorecard','Duplicate Merge Audit','Consent Coverage Report','Credit Exposure by Segment','Corporate Hierarchy Map'],
  forms:['Party (multi-role)','Address with GPS','Identity Document','Credit Profile','Merge Request'],
  cross:['Every module reads party','M07 CRM accounts','M20 credit control','P01 self-service profile','M29 record isolation'],
  freg:{ src:100, sub:[
    ['1','Party Record & Roles',12],['2','Classification',7],['3','Account Hierarchy',8],
    ['4','Addresses (BD structure + GPS)',7],['5','Identity & OTP',9],['6','Registration Approval',6],
    ['7','Deduplication & Merge',11],['8','Golden Record & Quality',9],['9','Consent & DSR',13],
    ['10','Segments',5],['11','Credit Profile',8],['12','Status Lifecycle',5] ] } },

/* ---------------- M07 CRM & SALES PIPELINE ---------------------------- */
M07: { area:'A03', en:'CRM & Sales Pipeline', bn:'সিআরএম ও বিক্রয়', icon:'🎯', rail:'customer',
  desc:'Leads, opportunities, corporate account plans, QBRs, renewals T-90, cross-sell and win/loss.',
  kpis:[ {l:'Weighted Pipeline',v:'৳ 6.84 Cr',d:'+9%',up:1,spark:[5.2,5.6,5.9,6.2,6.5,6.7,6.84]},
          {l:'Win Rate',v:'31%',d:'+3pt',up:1,st:'ok'},
          {l:'AMC Renewals T-90',v:'23',st:'warn'},
          {l:'New Corp Logos YTD',v:'31',d:'+7',up:1},
          {l:'QBRs This Month',v:'12',st:'info'},
          {l:'Referral Leads',v:'418',d:'+18%',up:1} ],
  groups:[
    {en:'Leads', screens:[
      {id:'M07-leads', en:'Leads', bn:'লিড', t:'g'},
      {id:'M07-scoring', en:'Scoring & Routing', bn:'স্কোরিং ও রাউটিং', t:'g'},
      {id:'M07-sources', en:'Sources & Campaigns', bn:'উৎস', t:'r'} ]},
    {en:'Pipeline', screens:[
      {id:'M07-opps', en:'Opportunities', bn:'সুযোগ', t:'g'},
      {id:'M07-kanban', en:'Pipeline Kanban', bn:'পাইপলাইন কানবান', t:'d'},
      {id:'M07-forecast', en:'Forecast', bn:'পূর্বাভাস', t:'r'} ]},
    {en:'Accounts', screens:[
      {id:'M07-accounts', en:'Corporate Accounts', bn:'কর্পোরেট অ্যাকাউন্ট', t:'g'},
      {id:'M07-plans', en:'Account Plans', bn:'অ্যাকাউন্ট প্ল্যান', t:'g'},
      {id:'M07-qbr', en:'QBR Scheduler', bn:'কিউবিআর', t:'c'},
      {id:'M07-activities', en:'Activities & Visits', bn:'কার্যক্রম', t:'g'} ]},
    {en:'Renewals & Growth', screens:[
      {id:'M07-t90', en:'T-90 Renewal Register', bn:'নবায়ন রেজিস্টার', t:'g'},
      {id:'M07-crosssell', en:'Cross-Sell / Upsell', bn:'ক্রস-সেল', t:'g'},
      {id:'M07-winloss', en:'Win/Loss Analysis', bn:'জয়-পরাজয়', t:'r'} ]} ],
  reports:['Pipeline by Stream','Funnel Conversion','Win Rate by Source','Account Manager Scorecard','Renewal Risk Report','Cross-Sell Attach Rate'],
  forms:['Lead','Opportunity','Activity (call/visit/meeting)','Account Plan'],
  cross:['M33 party master','M08 contract renewals','M35 marketing campaigns','M54 profitability by customer'],
  freg:{ src:79, sub:[
    ['1','Lead Capture & Qualification',12],['2','Opportunity Stages',10],
    ['3','Pipeline & Forecasting',9],['4','Account Plans & Stakeholders',9],
    ['5','Account-Manager Assignment',6],['6','QBR Programme',7],['7','Activities',8],
    ['8','Renewal Pipeline',6],['9','Cross-Sell / Upsell',7],['10','Competitor Intelligence',5] ] } },

/* ---------------- M10 LOYALTY & REWARDS -------------------------------- */
M10: { area:'A03', en:'Loyalty & Rewards', bn:'লয়্যালটি ও পুরস্কার', icon:'🎁', rail:'customer',
  desc:'Privilege tiers, points ledger, wallet, vouchers, referral programme, alliance benefits, liability.',
  kpis:[ {l:'Members',v:'384 K',spark:[290,306,322,338,352,368,384]},
          {l:'Points Liability',v:'৳ 1.24 Cr',st:'info'},
          {l:'Redemption MTD',v:'৳ 8.4 L',d:'+12%',up:1},
          {l:'Referral Conversions',v:'1,142',d:'+18%',up:1,st:'ok'},
          {l:'Breakage',v:'18.2%',st:'info'},
          {l:'Tier Upgrades MTD',v:'2,340',st:'ok'} ],
  groups:[
    {en:'Programme', screens:[
      {id:'M10-tiers', en:'Tiers & Benefits', bn:'স্তর ও সুবিধা', t:'g'},
      {id:'M10-enrol', en:'Enrolment & Upgrade', bn:'নথিভুক্তি', t:'g'},
      {id:'M10-alliance', en:'Alliance Benefits', bn:'জোট সুবিধা', t:'g'} ]},
    {en:'Points & Wallet', screens:[
      {id:'M10-ledger', en:'Points Ledger', bn:'পয়েন্ট লেজার', t:'g'},
      {id:'M10-wallet', en:'Wallet & Credits', bn:'ওয়ালেট', t:'g'},
      {id:'M10-redemption', en:'Redemption Rules', bn:'খরচ নিয়ম', t:'g'} ]},
    {en:'Vouchers & Referrals', screens:[
      {id:'M10-vouchers', en:'Vouchers & Coupons', bn:'ভাউচার', t:'g'},
      {id:'M10-referral', en:'Referral Programme', bn:'রেফারেল', t:'g'},
      {id:'M10-fraud', en:'Fraud Controls', bn:'প্রতারণা নিয়ন্ত্রণ', t:'g'} ]},
    {en:'Finance', screens:[
      {id:'M10-liability', en:'Liability & Breakage (IFRS 15)', bn:'দায় ও ব্রেকেজ', t:'r'},
      {id:'M10-profit', en:'Programme Profitability', bn:'কর্মসূচি লাভ', t:'r'} ]} ],
  reports:['Member Growth & Tier Mix','Points Earn/Burn Analysis','Referral Funnel','Voucher Usage & Fraud','Programme P&L'],
  forms:['Tier Configuration','Voucher Campaign','Points Adjustment','Referral Code'],
  cross:['M33 member records','M20 wallet refunds','M35 referral campaigns','P01 member dashboard'],
  freg:{ src:63, sub:[
    ['1','Tiers & Enrolment',10],['2','Benefit Engine',9],['3','Points Ledger',9],
    ['4','Wallet',7],['5','Vouchers & Coupons',9],['6','Referrals',7],
    ['7','Alliance Benefits',5],['8','Liability & Breakage',7] ] } },

/* ---------------- M34 CX, FEEDBACK & COMPLAINTS ------------------------ */
M34: { area:'A03', en:'CX, Feedback & Complaints', bn:'অভিজ্ঞতা ও অভিযোগ', icon:'💬', rail:'customer',
  desc:'CSAT/NPS/CES surveys, closed feedback loop, complaint SLA & escalation, goodwill authority, VoC analytics.',
  kpis:[ {l:'CSAT',v:'4.6 / 5',d:'+0.3',up:1,st:'ok',spark:[3.9,4.0,4.2,4.3,4.4,4.5,4.6]},
          {l:'NPS',v:'58',d:'+6',up:1,st:'ok',spark:[38,42,46,50,54,56,58]},
          {l:'Open Complaints',v:'87',st:'warn'},
          {l:'Complaint SLA Met',v:'96.1%',st:'ok'},
          {l:'Detractor Follow-ups',v:'31',st:'warn'},
          {l:'Survey Response',v:'38.4%',d:'+4pt',up:1} ],
  groups:[
    {en:'Surveys', screens:[
      {id:'M34-design', en:'Survey Designer', bn:'সার্ভে ডিজাইনার', t:'f'},
      {id:'M34-responses', en:'Responses & Ratings', bn:'প্রতিক্রিয়া', t:'g'},
      {id:'M34-throttle', en:'Distribution & Throttling', bn:'বিতরণ নিয়ন্ত্রণ', t:'g'} ]},
    {en:'Complaints', screens:[
      {id:'M34-complaints', en:'Complaints', bn:'অভিযোগ', t:'g'},
      {id:'M34-record', en:'Complaint Record', bn:'অভিযোগ নথি', t:'f'},
      {id:'M34-escalation', en:'Severity & Escalation', bn:'তীব্রতা ও এসকালেশন', t:'g'},
      {id:'M34-goodwill', en:'Goodwill Authority', bn:'সদিচ্ছা ক্ষমতা', t:'g'} ]},
    {en:'Closed Loop', screens:[
      {id:'M34-detractor', en:'Detractor Recovery', bn:'সমালোচক পুনরুদ্ধার', t:'c'},
      {id:'M34-journey', en:'Journey Measurement', bn:'যাত্রা পরিমাপ', t:'r'} ]},
    {en:'Voice of Customer', screens:[
      {id:'M34-voc', en:'VoC Analytics', bn:'ভিওসি বিশ্লেষণ', t:'d'},
      {id:'M34-reviews', en:'Reviews & Testimonials', bn:'রিভিউ', t:'g'},
      {id:'M34-byybranch', en:'Experience by Branch/Tech', bn:'শাখাভিত্তিক অভিজ্ঞতা', t:'r'} ]} ],
  reports:['CSAT by Branch & Technician','NPS Trend & Drivers','Complaint Category Pareto','Closed-Loop Effectiveness','Review Sentiment Summary'],
  forms:['Survey','Complaint','Goodwill Credit','Detractor Follow-up'],
  cross:['M27 conversation ratings','M21 technician signals','M23 quality signals','P01 in-app feedback'],
  freg:{ src:69, sub:[
    ['1','Survey Design & Distribution',10],['2','CSAT / NPS / CES',7],
    ['3','Multi-Parameter Ratings',6],['4','Closed Feedback Loop',9],['5','Complaint Management',14],
    ['6','Categorisation & SLA',8],['7','Compensation & Goodwill',6],['8','VoC Analytics',9] ] } },

/* ---------------- M27 CONTACT CENTRE ------------------------------------ */
M27: { area:'A03', en:'Contact Centre (16743)', bn:'কল সেন্টার ১৬৭৪৩', icon:'🎧', rail:'customer',
  desc:'Unified voice + digital conversations, skills routing, agent desktop with Customer-360 pop, notifications for the ERP.',
  kpis:[ {l:'Conversations Today',v:'3,842',st:'info',spark:[3400,3520,3610,3700,3760,3800,3842]},
          {l:'Service Level 80/20',v:'91.7%',st:'ok',spark:[84,86,88,89,90,91,91.7]},
          {l:'AHT',v:'4m 12s',d:'−18s',up:1,st:'ok'},
          {l:'Abandon Rate',v:'2.4%',d:'−0.5pt',up:1,st:'ok'},
          {l:'WhatsApp Share',v:'38%',d:'+5pt',up:1},
          {l:'Notification Delivery',v:'98.6%',st:'ok'} ],
  groups:[
    {en:'Unified Queue', screens:[
      {id:'M27-queue', en:'Unified Queue Board', bn:'একত্র সারি', t:'d'},
      {id:'M27-conversations', en:'Conversations', bn:'কথোপকথন', t:'g'},
      {id:'M27-routing', en:'Skills Routing', bn:'স্কিল রাউটিং', t:'g'} ]},
    {en:'Agent Desktop (P10)', screens:[
      {id:'M27-desktop', en:'Agent Desktop Preview', bn:'এজেন্ট ডেস্কটপ', t:'d'},
      {id:'M27-states', en:'Agent States & Wrap-Up', bn:'এজেন্ট অবস্থা', t:'g'},
      {id:'M27-dispositions', en:'Disposition Codes', bn:'নিষ্পত্তি কোড', t:'g'} ]},
    {en:'Channels', screens:[
      {id:'M27-voice', en:'Voice & IVR Flows', bn:'ভয়েস ও আইভিআর', t:'g'},
      {id:'M27-digital', en:'WhatsApp / Chat / Email / Social', bn:'ডিজিটাল চ্যানেল', t:'g'},
      {id:'M27-outbound', en:'Outbound Campaigns', bn:'আউটবাউন্ড', t:'g'} ]},
    {en:'Notification Hub', screens:[
      {id:'M27-templates', en:'Notification Templates', bn:'বিজ্ঞপ্তি টেমপ্লেট', t:'g'},
      {id:'M27-delivery', en:'Delivery Tracking & Retry', bn:'ডেলিভারি ট্র্যাকিং', t:'g'},
      {id:'M27-preferences', en:'Consent & DND', bn:'সম্মতি ও ডিএনডি', t:'g'} ]},
    {en:'Quality & WFM', screens:[
      {id:'M27-qa', en:'QA Evaluations', bn:'কিউএ মূল্যায়ন', t:'g'},
      {id:'M27-wfm', en:'Forecast & Roster', bn:'পূর্বাভাস ও রোস্টার', t:'r'} ]} ],
  reports:['Channel Mix & Volumes','Service Level by Interval','AHT & FCR by Disposition','Notification Delivery by Channel','QA Score Distribution'],
  forms:['IVR Flow','Notification Template','Disposition Code','Outbound List'],
  cross:['M32 AI handoff','M33 Customer-360 pop','M01 create SO in-conversation','M55 agent roster'],
  freg:{ src:87, sub:[
    ['1','Voice & IVR',12],['2','Digital Channels',12],['3','Unified Conversation Object',8],
    ['4','Queue & Routing',9],['5','Agent Desktop',10],['6','Workforce Management',7],
    ['7','Quality Monitoring',9],['8','ERP Notification Service',14],['9','Consent Enforcement',6] ] } },

/* ---------------- M32 CONVERSATIONAL AI ---------------------------------- */
M32: { area:'A03', en:'Conversational AI (Bengali)', bn:'কথোপকথন এআই', icon:'🤖', rail:'customer',
  desc:'Bengali-first assistant — intent recognition, RAG on live ERP data, authenticated actions, human handoff.',
  kpis:[ {l:'FAQ Automation',v:'71%',d:'+9pt',up:1,st:'ok',spark:[52,56,60,63,66,69,71]},
          {l:'AI FCR',v:'57.8%',st:'ok'},
          {l:'Handoff Precision',v:'94.2%',st:'ok'},
          {l:'Bengali Sessions',v:'68%',st:'info'},
          {l:'Guard-Rail Blocks',v:'126',st:'warn'},
          {l:'Avg Turns',v:'4.2',st:'info'} ],
  groups:[
    {en:'Assistant', screens:[
      {id:'M32-chat', en:'Assistant Playground', bn:'অ্যাসিস্ট্যান্ট', t:'c'},
      {id:'M32-sessions', en:'Conversations', bn:'সেশন', t:'g'} ]},
    {en:'Understanding', screens:[
      {id:'M32-intents', en:'Intent Library', bn:'ইনটেন্ট লাইব্রেরি', t:'g'},
      {id:'M32-entities', en:'Entity Extraction', bn:'এনটিটি নিষ্কাশন', t:'g'},
      {id:'M32-dialogue', en:'Dialogue Flows', bn:'সংলাপ প্রবাহ', t:'g'} ]},
    {en:'Grounding & Safety', screens:[
      {id:'M32-rag', en:'RAG Knowledge Sources', bn:'র্যাগ উৎস', t:'g'},
      {id:'M32-guardrails', en:'Guard Rails', bn:'গার্ডরেল', t:'g'},
      {id:'M32-handoff', en:'Handoff Packages', bn:'হ্যান্ডঅফ', t:'g'} ]},
    {en:'Agent Assist', screens:[
      {id:'M32-assist', en:'Suggested Replies / NBA', bn:'এজেন্ট সহায়তা', t:'d'},
      {id:'M32-analytics', en:'Conversation Analytics', bn:'বিশ্লেষণ', t:'r'} ]} ],
  reports:['Intent Coverage & FCR','Handoff Reasons','Guard-Rail Intervention Log','Bengali vs English Performance','Assistant CSAT'],
  forms:['Intent','Dialogue Flow','Guard-Rail Rule'],
  cross:['M27 agent desktop','M61 knowledge grounding','M26 NLP models','P01 customer chat'],
  freg:{ src:62, sub:[
    ['1','Intent Recognition (bn/en/mixed)',9],['2','Entity Extraction',7],
    ['3','Dialogue Management',8],['4','RAG Grounding',7],['5','Authenticated Actions',6],
    ['6','Guard Rails',7],['7','Handoff Decision',5],['8','Agent Assistance',6],['9','Analytics',7] ] } },

/* ---------------- M35 MARKETING ------------------------------------------- */
M35: { area:'A03', en:'Marketing Campaigns', bn:'মার্কেটিং ক্যাম্পেইন', icon:'📣', rail:'customer',
  desc:'Segment-driven journeys, offer selection, A/B & attribution, seasonal templates, co-marketing with partners.',
  kpis:[ {l:'Active Campaigns',v:'14',st:'info'},
          {l:'Leads MTD',v:'3,142',d:'+22%',up:1,spark:[2100,2280,2440,2610,2780,2960,3142]},
          {l:'CAC',v:'৳ 164',d:'−৳ 18',up:1,st:'ok'},
          {l:'Attributed Revenue',v:'৳ 92 L',st:'info'},
          {l:'Open Rate',v:'41.2%',st:'ok'},
          {l:'Consent-Safe Reach',v:'1.21 M',st:'ok'} ],
  groups:[
    {en:'Campaigns', screens:[
      {id:'M35-campaigns', en:'Campaign Manager', bn:'ক্যাম্পেইন ম্যানেজার', t:'g'},
      {id:'M35-approval', en:'Planning & Approval', bn:'পরিকল্পনা ও অনুমোদন', t:'c'} ]},
    {en:'Journeys', screens:[
      {id:'M35-journeys', en:'Journey Orchestration', bn:'জার্নি অর্কেস্ট্রেশন', t:'f'},
      {id:'M35-triggers', en:'Behaviour Triggers', bn:'আচরণ ট্রিগার', t:'g'} ]},
    {en:'Offers & Content', screens:[
      {id:'M35-offers', en:'Offer Selection', bn:'অফার নির্বাচন', t:'g'},
      {id:'M35-content', en:'Creative Library', bn:'ক্রিয়েটিভ লাইব্রেরি', t:'g'},
      {id:'M35-ads', en:'Portal Ad Placement', bn:'পোর্টাল বিজ্ঞান', t:'g'} ]},
    {en:'Measurement', screens:[
      {id:'M35-ab', en:'A/B & Holdout', bn:'এ/বি পরীক্ষা', t:'g'},
      {id:'M35-attribution', en:'Attribution Model', bn:'অ্যাট্রিবিউশন', t:'r'},
      {id:'M35-roi', en:'Budget & ROI', bn:'বাজেট ও আরওআই', t:'r'} ]} ],
  reports:['Campaign Funnel by Channel','Attribution & ROI','Seasonal Template Performance','Co-Marketing Partner Report','Lead-to-Order Conversion'],
  forms:['Campaign','Journey (multi-step)','Offer','Creative Asset'],
  cross:['M33 governed segments','M07 lead routing','M27 notification channels','M38 storefront promos'],
  freg:{ src:58, sub:[
    ['1','Campaign Planning & Approval',8],['2','Audience from Segments',6],
    ['3','Journey Orchestration',10],['4','Content & Offers',8],['5','Experimentation',7],
    ['6','Budget & Attribution',8],['7','Portal Advertising',5],['8','Co-Marketing',6] ] } }
};
