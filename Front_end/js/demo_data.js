/* =====================================================================
   1000 FiX ERP — deterministic demo data (FIX-UXD-2026-001 Part 10).
   Keyword-matched grid schemas so every one of the 823 grids shows
   plausible columns and rows; enriched Tell-ME records; console scripts;
   dashboard widget sets; sample report tables; 360 bands. Bangladesh
   service flavour: SO/JO numbers, BDT, bKash/Nagad, districts, brands,
   technicians, parts. Deterministic seed — same values every reload.
   ===================================================================== */
(function () {
'use strict';
var D = window.FX_DEMO = {};

/* ---------- deterministic PRNG --------------------------------------- */
var seed = 20260927;
function rnd() { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; }
function pick(a) { return a[Math.floor(rnd() * a.length)]; }
function int(a, b) { return a + Math.floor(rnd() * (b - a + 1)); }
function bdt(n) { return '৳ ' + n.toLocaleString('en-IN'); }

D.rnd = rnd; D.pick = pick; D.int = int; D.bdt = bdt;

/* ---------- shared pools -------------------------------------------- */
var BRANCHES = ['DHK-Elephant Rd','DHK-Mirpur 10','DHK-Dhanmondi','DHK-Uttara','DHK-Bashundhara','CTG-Agrabad','CTG-GEC','SYL-Zindabazar','RAJ-Shaheb Bazar','KHL-Khulna Sadar','BRB-Barishal','RNG-Rangpur','MYM-Mymensingh','COM-Comilla'];
var DISTRICTS = ['Dhaka','Chattogram','Sylhet','Rajshahi','Khulna','Barishal','Rangpur','Mymensingh','Gazipur','Narayanganj'];
var CUSTOMERS = ['Nasir Ahmed','Rashedul Islam','Tahmina Begum','Sabbir Rahman','Farhana Yasmin','Imran Hossain','Mahmuda Khanam','Arif Chowdhury','Shirin Akter','Kamrul Hasan','BRAC Bank Ltd.','Grameenphone Ltd.','Apex Footwear','Beximco Communications','Square Pharmaceuticals','Pran-RFL Group','City Bank Ltd.','LankaBangla','Buet CSE Dept.','Unilever BD'];
var BRANDS = ['Dell','HP','Samsung','Xiaomi','Lenovo','Asus','Acer','Huawei','Epson','Canon','Apple','Walton','Symphony','realme','Microsoft','Toshiba','Fujitsu','LG'];
var DEVICES = ['Laptop','Desktop PC','Smartphone','Tablet','Printer','Monitor','Router','AC (Split)','Refrigerator','Washing Machine','Microwave','Projector','Server','Camera','UPS'];
var MODELS = ['Latitude 5420','Pavilion 15','Galaxy A54','Redmi Note 12','IdeaPad Slim 3','Vivobook 15','Aspire 5','MateBook D15','L3210 Printer','MF3010','iPhone 12','WNH-23FU'];
var TECHS = ['Jamil Hossain','Rakib Mahmud','Sohel Rana','Mizanur Rahman','Ashraful Alam','Naeem Islam','Ruhul Amin','Shahin Alam','Titu Mia','Farid Miah','Sabbir Tech','Sumon Das'];
var PARTS = ['LCD Assembly','Battery Pack','Keyboard','SSD 512GB NVMe','RAM 8GB DDR4','Charging Port','Motherboard','Fan Assembly','Power Adapter','Touch Panel','Speaker Module','Hinge Set','Back Cover','ROM Chip','Toner Cartridge'];
var PAY = ['bKash','Nagad','Card (SSLCOMMERZ)','Cash','Bank Transfer','Cheque','Wallet Credit'];
var CHANNELS = ['Hotline 16743','Web Portal','Mobile App','WhatsApp','AI Assistant','Walk-in','Email','B2B Bulk','Partner'];
var ST_OK = ['<span class="st ok">Active</span>','<span class="st ok">Completed</span>','<span class="st ok">Paid</span>'];
var ST_WARN = ['<span class="st warn">Pending</span>','<span class="st warn">Awaiting Approval</span>','<span class="st warn">In Transit</span>'];
var ST_ERR = ['<span class="st err">Blocked</span>','<span class="st err">Overdue</span>'];
function st() { var r = rnd(); return r < .55 ? pick(ST_OK) : r < .88 ? pick(ST_WARN) : pick(ST_ERR); }
var TODAY = '27 Sep 2026';

/* ---------- grid schemas (keyword-matched) ---------------------------- */
/* each: match[] tested against "screenId groupEn moduleEn" lowercased */
var SCHEMAS = [
  { m:['order','intake','request','token'], cols:['Order No','Customer','Device','Brand','Channel','Branch','Status','SLA','Amount'],
    row: function (i) { return ['SO-2026-' + (14820 + i), pick(CUSTOMERS), pick(DEVICES), pick(BRANDS), pick(CHANNELS), pick(BRANCHES), st(), pick(['2h 14m left','6h 02m left','On track','Escalated']), bdt(int(450, 14500))]; } },
  { m:['work order','dispatch','field','technician','van'], cols:['WO No','Technician','Zone','Customer','Skill','Scheduled','Status','Travel','Action'],
    row: function (i) { return ['WO-' + (9210 + i), pick(TECHS), pick(['Zone-1 Uttara','Zone-2 Mirpur','Zone-3 Dhanmondi','Zone-4 Bashundhara','Zone-5 Old Dhaka']), pick(CUSTOMERS), pick(['L1','L2','L3']), 'Today ' + int(9,17) + ':' + pick(['00','15','30','45']), st(), int(8,42) + ' min', '➊ Call']; } },
  { m:['repair','bench','workshop','wip'], cols:['RO No','Device','Model','Level','Bench','Technician','Days on Bench','Parts Fit','Status'],
    row: function (i) { return ['RO-' + (5410 + i), pick(DEVICES), pick(MODELS), pick(['L1','L2','L3']), 'B-' + int(1,24), pick(TECHS), (rnd()*6).toFixed(1), int(88,100) + '%', st()]; } },
  { m:['consignment','logistics','rider','courier','custody','pod'], cols:['Consignment','Type','Origin','Destination','Rider/Courier','Leg','Seal No','COD','Status'],
    row: function (i) { return ['CS-' + (31200 + i), pick(['Pick & Drop','Transfer','Return','Rental','Fulfilment']), pick(BRANCHES), pick(DISTRICTS), pick(TECHS), int(1,3) + ' of ' + int(3,5), 'SL-' + int(10000,99999), pick([bdt(0), bdt(int(500,8000))]), st()]; } },
  { m:['customer','party','account','member','seller','supplier','vendor','partner'], cols:['ID','Name','Type','District','Phone','Segment','Balance','Since','Status'],
    row: function (i) { return ['CUS-' + (104280 + i), pick(CUSTOMERS), pick(['Individual','Corporate','Government','Seller','Partner']), pick(DISTRICTS), '+8801' + int(3,9) + int(10000000,99999999), pick(['Standard','Privilege Gold','Corporate','SME']), bdt(int(0,42000)), '20' + int(18,25), st()]; } },
  { m:['inventory','stock','part','bin','transfer','count','warehouse','valuation'], cols:['Part No','Description','Brand','Class','On-Hand','Reserved','Available','Location','Value'],
    row: function (i) { return ['PRT-' + (71200 + i), pick(PARTS), pick(BRANDS), pick(['Own','Brand Consign','Refurb','Rental Pool']), int(0,480), int(0,60), int(0,420), pick(BRANCHES) + ' / BIN-' + int(1,99), bdt(int(1200,480000))]; } },
  { m:['invoice','bill','payment','receipt','mushak','vat','dunning','ar ','aging','ageing'], cols:['Doc No','Customer','Date','Type','Taxable','VAT 15%','Total','Method','Status'],
    row: function (i) { return ['INV-2026-' + (28410 + i), pick(CUSTOMERS), int(1,27) + ' Sep', pick(['Service','Parts','AMC','Brand Claim','Consolidated']), bdt(int(800,68000)), bdt(int(120,10200)), bdt(int(920,78200)), pick(PAY), st()]; } },
  { m:['journal','ledger','trial','gl ','coa','account'], cols:['Entry No','Date','Account','Cost Centre','Branch','Debit','Credit','Narration','Status'],
    row: function (i) { return ['JE-2026-' + (61200 + i), int(1,27) + ' Sep', pick(['1101 Cash','1201 AR','1401 Inventory','2101 AP','3101 Service Revenue','4101 Salaries','5101 Rent']), 'CC-' + int(100,999), pick(BRANCHES), bdt(int(1000,900000)), bdt(int(0,900000)), pick(['Monthly accrual','Service settlement','Payroll posting','Reclass']), st()]; } },
  { m:['purchase','procurement','rfq','po ','grn','match','requisition'], cols:['Doc No','Supplier','Item Class','Value','Approval','Promised','Received','Match','Status'],
    row: function (i) { return [pick(['PR-','RFQ-','PO-','GRN-']) + '2026-' + (4100 + i), pick(['SmartTech BD','Global Parts Ltd.','Component House','DigiTrade','Everest Import']), pick(PARTS), bdt(int(12000,1400000)), pick(['GM ✓','Head ✓','Pending']), int(1,28) + ' Sep', pick(['—','Full','Partial']), pick(['3-way ✓','Exception','—']), st()]; } },
  { m:['warranty','claim','protection','recall'], cols:['Claim No','Brand','Order','Device','Evidence','Submitted','Decision','Reimb.','Status'],
    row: function (i) { return ['CLM-2026-' + (7410 + i), pick(BRANDS), 'SO-2026-' + int(14000,14800), pick(DEVICES), int(92,100) + '%', int(1,27) + ' Sep', pick(['Approved','Part-Approved','Pending','Info Requested']), bdt(int(800,24000)), st()]; } },
  { m:['contract','amc','entitlement','subscription','renewal','sla '], cols:['Contract','Client','Family','Start','Expiry','Value','Visits Used','SLA','Status'],
    row: function (i) { return ['AMC-' + (2100 + i), pick(CUSTOMERS), pick(['Residential Silver','Commercial Gold','IT Infra','Healthcare','Managed T2']), int(1,12) + '/' + int(20,25), int(1,12) + '/2' + int(6,8), bdt(int(24000,2400000)), int(2,48) + ' / ' + int(12,120), int(88,100) + '%', st()]; } },
  { m:['employee','staff','payroll','attendance','leave','roster','shift','hr ','directory','candidate','talent','performance'], cols:['ID','Name','Role','Branch','Grade','Join Date','Certified','Score','Status'],
    row: function (i) { return ['FX-EMP-' + (100 + i), pick(TECHS.concat(['Nusrat Jahan','Abdul Karim','Sumaiya Akter','Rahim Uddin'])), pick(['Technician L1','Technician L2','Technician L3','Branch Manager','Agent','Accountant']), pick(BRANCHES), pick(['T2','T3','T4','M2','M3']), int(1,12) + '/20' + int(19,25), pick(['✓ 4 brands','✓ 2 brands','✓ Expired ⚠','—']), int(62,98), st()]; } },
  { m:['quality','ncr','capa','audit','incident','risk','complaint','safety'], cols:['Ref','Type','Source','Branch','Severity','Owner','Raised','Due','Status'],
    row: function (i) { return ['NC-' + (620 + i), pick(['NCR','CAPA','Audit Finding','Complaint','Near-Miss','Risk']), pick(['QC Gate','Customer','Auditor','Technician','System']), pick(BRANCHES), pick(['Low','Medium','High','Critical']), pick(TECHS), int(1,27) + ' Sep', int(28,30) + ' Sep', st()]; } },
  { m:['asset','device','equipment','fleet','vehicle','calibration','estate'], cols:['Asset ID','Type','Brand','Model','Serial','Custodian/Site','Warranty/Cal','Condition','Status'],
    row: function (i) { return ['AST-' + (41200 + i), pick(DEVICES.concat(['Multimeter','Oscilloscope','Van','Motorcycle'])), pick(BRANDS), pick(MODELS), 'SN' + int(100000,999999), pick(BRANCHES.concat(TECHS)), int(1,12) + '/2' + int(6,9), pick(['A','B','C','D']), st()]; } },
  { m:['rental','trade','refurb','recycl','ewaste','e-waste','valuation'], cols:['Ref','Item','Grade','Model','Valuation/Rate','Ageing','Location','Buyer/Settler','Status'],
    row: function (i) { return [pick(['RT-','TI-','RB-']) + (1820 + i), pick(DEVICES), pick(['A','B','C','D','—']), pick(MODELS), bdt(int(4000,84000)), int(1,60) + ' d', pick(BRANCHES), pick(CUSTOMERS), st()]; } },
  { m:['document','knowledge','article','manual','template','bulletin'], cols:['Ref','Title','Type','Owner','Version','Effective','Reviews','Language','Status'],
    row: function (i) { return ['DOC-' + (8200 + i), pick(['No-power diagnosis','Battery replacement SOP','Board-level micro-solder','Water damage triage','Mushak guide']), pick(['Procedure','Fault→Fix','Manual','Policy','Bulletin']), pick(TECHS), 'v' + int(1,6), int(1,27) + ' Sep', int(1,40), pick(['EN + বাংলা','EN','বাংলা']), st()]; } },
  { m:['conversation','ticket','chat','queue','agent','notification','ivr'], cols:['Ref','Channel','Customer','Intent/Topic','Agent','Started','Wait/AHT','Disposition','Status'],
    row: function (i) { return ['CNV-' + (62800 + i), pick(['Voice','WhatsApp','Web Chat','Email','Social']), pick(CUSTOMERS), pick(['Booking','Status check','Reschedule','Complaint','Payment','Warranty']), pick(['Agent-07','Agent-12','AI Assistant']), int(8,17) + ':' + int(10,59), pick(['38s','2m 14s','4m 02s','—']), pick(['Resolved','Escalated','Follow-up','Converted']), st()]; } },
  { m:['alert','monitor','telemetry','iot','stream','prediction','health'], cols:['Stream/Alert','Asset','Metric','Value','Threshold','Since','Severity','Action','Status'],
    row: function (i) { return ['STR-' + (12400 + i), 'AST-' + int(41000,41999), pick(['temp_c','vibration','uptime','battery_soh','toner_pct']), (rnd()*90).toFixed(1), int(60,95) + '', int(1,48) + ' h', pick(['Info','Warn','High']), pick(['Auto-remediate','Create SO','Notify']), st()]; } },
  { m:['campaign','marketing','lead','opportun','pipeline','quote','quotation','tender'], cols:['Ref','Customer/Title','Stage','Owner','Value','Probability','Next Step','Close Date','Status'],
    row: function (i) { return [pick(['LEAD-','OPP-','QT-','TDR-']) + (2410 + i), pick(CUSTOMERS.concat(['AMC tender — 400 seats','Printer fleet refresh'])), pick(['Qualified','Quoted','Negotiation','Won','Lost']), pick(['AM East','AM West','AM Corporate']), bdt(int(12000,2400000)), int(20,90) + '%', pick(['Follow-up call','Send revision','Site visit','e-Sign']), int(1,30) + ' Oct', st()]; } },
  { m:['project','wbs','milestone','task','portfolio'], cols:['Project','Type','PM','Start','End','Progress','Budget Used','RAG','Status'],
    row: function (i) { return ['PRJ-' + (118 + i), pick(['Branch Opening','ERP Rollout','Bulk Decommission','Fleet Upgrade','Corporate Rollout']), pick(['Rahim Uddin','Nusrat Jahan','Project Cell']), int(1,8) + '/26', int(1,12) + '/27', int(12,96) + '%', int(8,104) + '%', pick(['🟢','🟡','🔴']), st()]; } },
  { m:['user','role','permission','access','security','sod','api','event','config','flag','job','environment','connector'], cols:['Ref','Name/Subject','Type','Scope','Owner','Last Change','Risk','Review','Status'],
    row: function (i) { return [pick(['USR-','ROL-','RUL-','CFG-','FLG-','JOB-','CON-']) + (i + 101), pick(['Dispatcher','Branch Manager','Technician App','Vendor Portal','bKash Connector','Auto-assign Model','VAT Calendar']), pick(['Role','Rule','Config','Integration','Job','Model']), pick(['T2 Branch','T3 Zone','T0 Global','T4 Own','T5 Restricted']), pick(TECHS), int(1,27) + ' Sep', pick(['Low','Medium','High']), pick(['Q3 ✓','Due','—']), st()]; } },
  { m:['backup','destruction','recovery','data case','media','purge'], cols:['Case','Customer','Media','Specialism','Attempt','Success %','Quotation','Certificate','Status'],
    row: function (i) { return ['DRC-' + (410 + i), pick(CUSTOMERS), pick(['HDD 1TB','SSD 512GB','RAID Array','USB Drive','Phone Storage']), pick(['Logical','Firmware','Electrical','Head Stack','Cleanroom']), int(1,3), pick(['—',int(40,98) + '%']), bdt(int(3000,84000)), pick(['DT-CERT-' + int(1000,9999),'—']), st()]; } }
];
var GENERIC = { cols:['Ref','Name','Category','Owner','Branch','Date','Priority','Value','Status'],
  row: function (i) { return ['FX-' + (24000 + i), ['Record ' + (i + 1), pick(DEVICES)].join(' — '), pick(['Standard','Urgent','Planned']), pick(TECHS), pick(BRANCHES), int(1,27) + ' Sep', pick(['Normal','High','Critical']), bdt(int(500,84000)), st()]; } };
D.schemaFor = function (key) {
  key = (key || '').toLowerCase();
  for (var i = 0; i < SCHEMAS.length; i++) {
    for (var k = 0; k < SCHEMAS[i].m.length; k++)
      if (key.indexOf(SCHEMAS[i].m[k]) >= 0) return SCHEMAS[i];
  }
  return GENERIC;
};
D.rowsFor = function (key, n) {
  var sc = D.schemaFor(key), out = [];
  n = n || int(6, 12);
  for (var i = 0; i < n; i++) out.push(sc.row(i));
  return { cols: sc.cols, rows: out };
};

/* ---------- Tell-ME records ------------------------------------------ */
D.tellme = [
  ['SO-2026-14838','Service Order','On-site · Laptop no-power · Dell Latitude 5420 · Mirpur · SLA 4h','#/record/M01-order/SO-2026-14838'],
  ['SO-2026-14821','Service Order','Workshop · Printer paper jam · Epson L3210 · Warranty','#/record/M01-order/SO-2026-14821'],
  ['WO-9218','Field Work Order','Jamil Hossain · Zone-2 Mirpur · EN ROUTE · ETA 14 min','#/record/M02-record/WO-9218'],
  ['RO-5412','Repair Order (Bench)','L3 board-level · MacBook A2338 · B-14 · 2.4 days','#/record/M31-record/RO-5412'],
  ['CS-31244','Consignment','Pick & Drop · Dhanmondi → Elephant Rd · leg 2 of 3 · seal SL-48291','#/record/M03-record/CS-31244'],
  ['CUS-104283','Customer','Nasir Ahmed · Privilege Gold · 14 devices · LTV ৳ 84,200','#/record/M33-party/CUS-104283'],
  ['CUS-100912','Corporate Account','Grameenphone Ltd. · AMC Gold · 412 assets · 6 sites','#/record/M33-party/CUS-100912'],
  ['TECH-0321','Technician','Jamil Hossain · L3 · Dell+Apple certified · score 94 · util 82%','#/record/M21-employee/FX-EMP-321'],
  ['INV-2026-28441','Invoice (Mushak 6.3)','৳ 4,830 · bKash · paid · SO-2026-14838','#/record/M20-invoice/INV-2026-28441'],
  ['CLM-2026-7428','Brand Claim','Samsung · evidence 100% · submitted 26 Sep · ৳ 4,120','#/record/M09-record/CLM-2026-7428'],
  ['AMC-2118','Contract','BRAC Bank · IT Infra AMC · expires 14 Mar 2028 · ৳ 8.4 L','#/record/M08-record/AMC-2118'],
  ['PRT-71208','Part','LCD Assembly · Galaxy A54 · on-hand 42 · 3 branches','#/record/M15-onhand/PRT-71208'],
  ['PO-2026-4182','Purchase Order','SmartTech BD · ৳ 6.2 L · 3-way matched ✓','#/record/M16-pos/PO-2026-4182'],
  ['AST-41280','Device Asset','MacBook Pro 14 · SN C02XK9... · 3 repairs · warranty to 2027','#/record/M17-asset/AST-41280'],
  ['DRC-418','Data Recovery Case','RAID array · cleanroom booked · firm quote ৳ 42,000','#/record/M06-record/DRC-418'],
  ['NC-628','NCR','QC fail — hinge torque · Dhanmondi branch · CAPA open','#/record/M23-ncr/NC-628'],
  ['QT-2418','Quotation','Corporate 60-seat AMC · v2 · awaiting e-sign · ৳ 14.2 L','#/record/M36-record/QT-2418'],
  ['PRJ-121','Project','Branch Opening — Chattogram-3 · 68% · on budget','#/record/M67-record/PRJ-121']
];

/* ---------- console scripts (steppers × checklists) ------------------- */
D.CONSOLES = {
  'M19-close': { title:'Month-End Close — September 2026', steps:[
    ['Day 1','Branch cash & drawer reconciliation','51 of 53 branches reported ✓','done'],
    ['Day 1','Inventory & van-stock period lock','Locked ✓','done'],
    ['Day 1','Subledger posting sweep','AR 100% · AP 98% · Inventory 100%','done'],
    ['Day 2','Accruals & prepayments','14 journals posted ✓','done'],
    ['Day 2','Brand claim provisions','৳ 4.2 L accrued ✓','done'],
    ['Day 2','Intercompany reconciliation','2 pairs pending','active'],
    ['Day 3','Statutory statements render','P&L · BS · CF queued','todo'],
    ['Day 3','Archiving & audit seal','Scheduled 30 Sep 23:00','todo']],
    gauge:[82,100,'Close progress'] },
  'M01-intake': { title:'Omni-Channel Intake Console', steps:[
    ['Live','Hotline 16743','12 calls waiting · SL 91%','active'],
    ['Live','WhatsApp bot','38 sessions · AI handling 26','active'],
    ['Live','Web & app bookings','142 today · conversion 74%','done'],
    ['Queue','Walk-in tokens (51 branches)','4,236 issued today','done'],
    ['Queue','B2B bulk uploads','2 files pending validation','todo'],
    ['Watch','SLA at-risk orders','37 orders — 6 critical','todo']],
    gauge:[64,100,'Channel load'] },
  'M02-dispatch': { title:'Dispatch Board — Live', steps:[
    ['Zones','5 zones · 214 technicians','168 on-site / en-route','active'],
    ['Queue','Unassigned work orders','6 open > 15 min','active'],
    ['AI','Auto-assignment engine','68% auto-assign · 6.2% override','done'],
    ['Routes','Route optimisation','12 routes re-optimised 12:40','done'],
    ['Safety','Lone-worker check-ins','All 24 field techs checked in ✓','done'],
    ['Cash','Daily reconciliation','184 of 214 submitted','todo']],
    gauge:[78,100,'Dispatch readiness'] },
  'M51-vat91': { title:'VAT Return 9.1 — September 2026', steps:[
    ['1','Mushak 6.1 sales register','38,412 invoices · ৳ 12.42 Cr + VAT ৳ 1.42 Cr','done'],
    ['2','Mushak 6.2 purchase register','8,214 bills · input credit ৳ 38.4 L','done'],
    ['3','Adjustments (Mushak 6.7/6.8)','6 entries validated','done'],
    ['4','Net payable computation','৳ 1.04 Cr payable','active'],
    ['5','Payment — A-Challan','Scheduled 14 Oct','todo'],
    ['6','Return submission (NBR)','Deadline 15 Oct','todo']],
    gauge:[67,100,'Filing readiness'] },
  'M56-runs': { title:'Payroll Run — September 2026', steps:[
    ['1','Attendance verification & lock','Locked 24 Sep ✓','done'],
    ['2','Overtime & incentive intake','From M55/M57 · ৳ 6.4 L OT','done'],
    ['3','Dry run','512 employees · 0 exceptions','done'],
    ['4','Gross-to-net + tax (AY 26-27)','Tax ৳ 42.6 L withheld','active'],
    ['5','PF / gratuity provisions','Posted ✓','todo'],
    ['6','BEFTN file generation','52 error-free','todo'],
    ['7','Bank release & payslips','Scheduled 28 Sep','todo']],
    gauge:[71,100,'Run progress'] },
  'M16-match': { title:'3-Way Match Workbench', steps:[
    ['1','PO ↔ GRN matching','184 clean · 11 quantity variance','done'],
    ['2','GRN ↔ invoice matching','169 clean · 3 price variance','active'],
    ['3','Tolerance routing','Within ±2% auto-pass','done'],
    ['4','Exception disposition','11 pending supplier clarification','todo'],
    ['5','Release to AP','169 released','done']],
    gauge:[74,100,'Match coverage'] },
  'M09-evidence': { title:'Brand Claim Evidence Assembly', steps:[
    ['1','Order & device linkage','SO ↔ AST ✓ 100%','done'],
    ['2','Technician certification proof','Expired found — 1 blocked','active'],
    ['3','Parts consumption genealogy','42 parts serialised ✓','done'],
    ['4','Photos with GPS + timestamps','18 of 18 ✓','done'],
    ['5','Purchase proof (where claimed)','3 of 3 ✓','done'],
    ['6','Brand rule validation','Samsung format v4 ✓','done']],
    gauge:[88,100,'Evidence completeness'] }
};
D.consoleFor = function (id) {
  if (D.CONSOLES[id]) return D.CONSOLES[id];
  return { title:'Operations Console', steps:[
    ['Prepare','Load inputs','System data ✓','done'],
    ['Validate','Pre-flight checks','8 of 9 passed','active'],
    ['Execute','Process batch','Ready to start','todo'],
    ['Review','Outcome verification','—','todo'],
    ['Close','Post & archive','—','todo']],
    gauge:[42,100,'Progress'] };
};

/* ---------- report tables -------------------------------------------- */
D.reportFor = function (name) {
  name = (name || '').toLowerCase();
  if (name.indexOf('trial') >= 0) return { cols:['Account','Name','Debit','Credit'], rows:[
    ['1101','Cash & Banks', bdt(184200000), bdt(0)], ['1201','Accounts Receivable', bdt(284600000), bdt(0)],
    ['1401','Inventory', bdt(86200000), bdt(0)], ['2101','Accounts Payable', bdt(0), bdt(68400000)],
    ['3101','Service Revenue', bdt(0), bdt(1242000000)], ['4101','Salaries & Wages', bdt(48200000), bdt(0)],
    ['5101','Rent & Facilities', bdt(8600000), bdt(0)], ['9101','Retained Earnings', bdt(0), bdt(212400000)] ],
    footer:['','Net', bdt(761400000), bdt(761400000)] };
  if (name.indexOf('aging') >= 0 || name.indexOf('ageing') >= 0) return { cols:['Bucket','Current','1–30 d','31–60 d','61–90 d','> 90 d','Total'], rows:[
    ['Individual', bdt(2420000), bdt(1240000), bdt(420000), bdt(180000), bdt(84000), bdt(4344000)],
    ['Corporate', bdt(6840000), bdt(2480000), bdt(860000), bdt(240000), bdt(62000), bdt(10482000)],
    ['Brand claims', bdt(1420000), bdt(860000), bdt(180000), bdt(0), bdt(0), bdt(2460000)],
    ['Marketplace', bdt(420000), bdt(86000), bdt(0), bdt(0), bdt(0), bdt(506000)] ],
    footer:['Total', bdt(11100000), bdt(4666000), bdt(1460000), bdt(420000), bdt(146000), bdt(17792000)] };
  if (name.indexOf('league') >= 0 || name.indexOf('branch') >= 0) return { cols:['#','Branch','Revenue MTD','Jobs','TAT','CSAT','FTF','Margin'], rows:[
    ['1','DHK-Dhanmondi', bdt(14200000), 2842, '18.2 h', '4.8', '89%', '46.2%'],
    ['2','DHK-Mirpur 10', bdt(12480000), 2618, '19.6 h', '4.7', '88%', '44.8%'],
    ['3','CTG-Agrabad', bdt(9860000), 2014, '21.4 h', '4.7', '86%', '43.6%'],
    ['4','DHK-Uttara', bdt(9420000), 1926, '20.8 h', '4.6', '87%', '43.1%'],
    ['5','SYL-Zindabazar', bdt(7840000), 1642, '22.6 h', '4.6', '85%', '41.8%'],
    ['6','DHK-Elephant Rd', bdt(7620000), 1586, '23.2 h', '4.5', '84%', '40.9%'],
    ['7','RAJ-Shaheb Bazar', bdt(6480000), 1382, '24.8 h', '4.5', '83%', '39.4%'],
    ['8','KHL-Khulna Sadar', bdt(5920000), 1204, '25.6 h', '4.4', '82%', '38.2%']] };
  if (name.indexOf('vat') >= 0 || name.indexOf('mushak') >= 0 || name.indexOf('return') >= 0 ||
      name.indexOf('tax') >= 0 || name.indexOf('tds') >= 0) return { cols:['Line','Description','Output SD','VAT 15%','Input TC','Net Payable'], rows:[
    ['1','Service revenue — repairs & AMC', bdt(84200000), bdt(12630000), bdt(0), bdt(12630000)],
    ['2','Parts & accessories sales', bdt(41600000), bdt(6240000), bdt(0), bdt(6240000)],
    ['3','Corporate AMC contracts', bdt(28400000), bdt(4260000), bdt(0), bdt(4260000)],
    ['4','Import — parts (A-Challan)', bdt(0), bdt(0), bdt(9840000), bdt(-9840000)],
    ['5','Local purchases — VAT deducted at source', bdt(0), bdt(0), bdt(2140000), bdt(-2140000)],
    ['6','Establishment expenses (taxable portion)', bdt(0), bdt(0), bdt(860000), bdt(-860000)],
    ['7','Telecom & IT services', bdt(0), bdt(0), bdt(420000), bdt(-420000)] ],
    footer:['','Total (Mushak 9.1)', bdt(154200000), bdt(23130000), bdt(13300000), bdt(9830000)] };
  return D.rowsFor(name, 9);
};

/* ---------- role-centre personas -------------------------------------- */
D.PERSONAS = [
  { id:'super', name:'Rahim Uddin', role:'CTO / Super Admin', initials:'RU',
    approvals:[['PR-2026-4188','Procurement','৳ 2.4 L — test equipment','#/record/M16-pos/PO-2026-4182'],
               ['QT-2418','Quotation','Corporate AMC ৳ 14.2 L','#/record/M36-record/QT-2418'],
               ['CFG-318','Config change','Auto-assign threshold','#/screen/M30-params']],
    worklist:[['37 orders','SLA at-risk','#/screen/M01-sla'],['6 WOs','Unassigned > 15 min','#/screen/M02-unassigned'],
              ['38 docs','Certifications expiring','#/screen/M22-expiry'],['14 claims','Awaiting brand decision','#/screen/M09-claims']] },
  { id:'ops', name:'Nusrat Jahan', role:'Operations Manager', initials:'NJ',
    approvals:[['RO-5412','L3 routing','Board-level specialist','#/record/M31-record/RO-5412'],
               ['EXC-208','Field exception','Customer absent ×2','#/screen/M02-exceptions']],
    worklist:[['148 consignments','In transit','#/screen/M03-cons'],['212 units','On bench','#/screen/M31-benches'],
              ['8 waves','Warehouse open','#/screen/M41-waves'],['24 near-miss','HSE reports','#/screen/M59-report']] },
  { id:'finance', name:'Abdul Karim', role:'Finance Manager', initials:'AK',
    approvals:[['JE-2026-61842','Journal','Accrual ৳ 8.4 L','#/screen/M19-je'],
               ['RUN-251','Payment run','৳ 42.6 L · 62 vendors','#/screen/M52-runs'],
               ['INV-C-881','Credit note','Goodwill ৳ 1,200','#/screen/M20-refunds']],
    worklist:[['Close day 2','Month-end console','#/screen/M19-close'],['32 exceptions','Bank recon','#/screen/M50-recon'],
              ['৳ 84 L','Overdue > 60d','#/screen/M20-aging'],['14 docs','TDS certificates due','#/screen/M51-certs']] },
  { id:'branch', name:'Sumaiya Akter', role:'Branch Manager — Dhanmondi', initials:'SA',
    approvals:[['TKN-4182','Priority token','VIP customer','#/screen/M04-queue'],
               ['HD-118','Hold release','Customer travelling','#/screen/M01-holds']],
    worklist:[['412 tokens','Today queue','#/screen/M04-queue'],['৳ 2.14 L','Drawer + banking','#/screen/M04-shift'],
              ['8 devices','Uncollected > 7d','#/screen/M04-uncollected'],['2 CARs','Store variance','#/screen/M15-recon']] }
];

/* ---------- journeys (user journeys × task flows) ---------------------- */
D.JOURNEYS = [
  { id:'J01', en:'Customer books an on-site repair (P01 → payment)', steps:[
    ['P01 · Customer','Customer opens app / portal, Bengali UI, picks device + symptom','#/portals'],
    ['M33 · Party','Identity via OTP — golden record matched or created','#/record/M33-party/CUS-104283'],
    ['M37 · Catalogue','Service resolved with upfront price + slot (≤3 steps)','#/screen/M37-services'],
    ['M01 · Order','Service Order created — entitlement evaluated (warranty/AMC/membership)','#/record/M01-order/SO-2026-14838'],
    ['M02 · Dispatch','AI scores candidates → assigned → ETA published to customer','#/screen/M02-dispatch'],
    ['P02 · Technician','Job accepted, navigation, photos w/ GPS, fix, e-sign','#/portals'],
    ['M01 · QC','Quality checkpoint gate → repair warranty issued','#/screen/M01-qc'],
    ['M20 · Invoice','Mushak 6.3 invoice + bKash link → paid','#/record/M20-invoice/INV-2026-28441'],
    ['M34 · Feedback','CSAT survey → detractor loop if ≤3','#/screen/M34-responses']] },
  { id:'J02', en:'Walk-in branch repair (counter → bench → collection)', steps:[
    ['M04 · Counter','Token issued, fast intake, device condition photos','#/screen/M04-counter'],
    ['M01 · Order','Workshop order — estimate if out-of-warranty','#/screen/M01-order'],
    ['M31 · Bench','L1/L2/L3 routing; parts from branch store','#/screen/M31-benches'],
    ['M15 · Parts','Serial-tracked consumption; consignment hard block respected','#/screen/M15-serials'],
    ['M31 · Test','Test protocol + burn-in → release','#/screen/M31-testing'],
    ['M04 · Collection','SMS + WhatsApp notify → ID-verified handover','#/screen/M04-handover'],
    ['M04 · Cash','Payment captured at counter, drawer reconciled at shift close','#/screen/M04-shift']] },
  { id:'J03', en:'Pick & drop logistics round trip', steps:[
    ['P01 · Booking','Customer books pick & drop with slot','#/portals'],
    ['M03 · Consignment','Multi-leg journey planned; seal number issued','#/record/M03-record/CS-31244'],
    ['P09 · Rider','Scan + OTP + photos at every custody handover','#/portals'],
    ['M31 · Workshop','Repair executed under custody state ON BENCH','#/screen/M31-orders'],
    ['M03 · Return','Delivery leg with OTP + signature + COD if due','#/screen/M03-pod'],
    ['M50 · Settlement','Rider COD reconciled at end of shift','#/screen/M50-ridercod']] },
  { id:'J04', en:'Brand warranty claim → reimbursement', steps:[
    ['M01 · Order','Warranty order — entitlement says brand pays','#/screen/M01-entitle'],
    ['M09 · Claim','Auto-created on delivery; evidence pack assembled <5 min','#/screen/M09-evidence'],
    ['M24 · Evidence','Photos, diagnostics, parts genealogy, certification proof','#/screen/M24-envelopes'],
    ['P08 · Brand','Partner reviews → approve / part-approve / info-request','#/portals'],
    ['M20 · AR','Receivable raised on approval','#/screen/M20-brand'],
    ['M09 · Recon','Remittance matched — reconciliation per brand','#/screen/M09-recon']] },
  { id:'J05', en:'Corporate AMC: contract → PM schedule → consolidated invoice', steps:[
    ['M07 · CRM','Opportunity won → contract template selected','#/screen/M07-opps'],
    ['M08 · Contract','14 families — entitlement & SLA defined','#/record/M08-record/AMC-2118'],
    ['M17 · Estate','Assets bulk-registered site/department/user','#/screen/M17-bulk'],
    ['M08 · PM','Preventive schedules auto-generate work','#/screen/M08-pm'],
    ['P04 · Client','Bulk requests validated against coverage','#/portals'],
    ['M20 · Billing','Consolidated monthly invoice + SLA credits','#/screen/M20-consolidated']] },
  { id:'J06', en:'Parts stockout → replenishment → payment', steps:[
    ['M15 · Alert','Stock breaches reorder point','#/screen/M15-onhand'],
    ['M43 · Planning','Forecast + safety stock → planned order','#/screen/M43-planned'],
    ['M16 · PR → RFQ','Requisition approved; RFQ to qualified suppliers','#/screen/M16-rfqs'],
    ['M42 · Gate','Supplier must be qualified & active','#/screen/M42-gate'],
    ['P05 · Vendor','Vendor acknowledges PO, sends ASN','#/portals'],
    ['M41 · Receive','Scan receiving + inspection gate','#/screen/M41-receiving'],
    ['M16 · Match','3-way match → release to AP','#/screen/M16-match'],
    ['M52 · Pay','Payment run with TDS at source','#/screen/M52-runs']] },
  { id:'J07', en:'Trade-in → refurbish → graded online resale', steps:[
    ['M14 · Intake','Portal valuation — firm 48h offer','#/screen/M14-valuation'],
    ['M14 · Provenance','IMEI / serial screening','#/screen/M14-provenance'],
    ['M06 · Gate','Data-bearing? destruction certificate mandatory','#/screen/M06-destroy'],
    ['M31 · Refurb','Work order, QA incl. battery health','#/screen/M14-qa'],
    ['M14 · Grade','A–D grading with supervisor override','#/screen/M14-grading'],
    ['M38 · Resale','Listing live on storefront with disclosure report','#/screen/M14-listings']] },
  { id:'J08', en:'Marketplace seller: onboarding → job → payout', steps:[
    ['M12 · KYC','NID + trade licence + references verified','#/screen/M12-kyc'],
    ['M12 · Agreement','Digital agreement + fee acceptance','#/screen/M12-agreements'],
    ['P07 · Seller','Profile, listings, own stock','#/portals'],
    ['M12 · Broadcast','Job broadcast to matching sellers → bidding','#/screen/M12-broadcast'],
    ['M02 · Oversight','Execution QC identical to in-house standards','#/screen/M12-oversight'],
    ['M53 · Payout','Commission deducted → wallet → payout run','#/screen/M53-payouts']] },
  { id:'J09', en:'Data recovery case (sealed custody → certificate)', steps:[
    ['M06 · Intake','Case with specialism routing; media sealed','#/screen/M06-cases'],
    ['M06 · Custody','Dual-control custody ledger','#/screen/M06-custody'],
    ['M06 · Evaluation','Free evaluation → firm quotation','#/screen/M06-eval'],
    ['M06 · Recovery','Attempts logged; cleanroom if needed','#/screen/M06-attempts'],
    ['M06 · Handover','Secure handover + verified purge certificate','#/screen/M06-handover']] },
  { id:'J10', en:'Month-end close → VAT 9.1 filing', steps:[
    ['M19 · Close','3-day close console across 53 branches','#/screen/M19-close'],
    ['M50 · Cash','Branch cash & rider COD consolidated','#/screen/M50-branchcash'],
    ['M19 · Statements','P&L · BS · CF rendered bilingually','#/screen/M19-pl'],
    ['M51 · VAT','Mushak registers → 9.1 return → A-Challan','#/screen/M51-vat91'],
    ['M19 · Seal','Period locked; audit trail sealed','#/screen/M19-periods']] }
];

/* ---------- portal catalogue (12 portals) ------------------------------ */
D.PORTALS = [
  ['P01','Customer Self-Service & App','Individual customers','250 K+/mo','Next.js 15 + RN',
   ['OTP register & devices','≤3-step booking & slots','live tracking + technician ETA','approvals & e-sign','bKash/Nagad/card pay','loyalty & shop','Bengali AI assistant']],
  ['P02','Technician Mobile App','Field & workshop technicians','200–400','Flutter',
   ['day queue + geofenced clock-in','offline 24h + 30s sync','diagnostic trees & fault coding','van stock scan-consume','field evidence + e-sign','panic alert','100% Bengali UI']],
  ['P03','Admin Operations Portal','Back-office & branch staff','150–250','Odoo OWL 2',
   ['15 role workspaces','dispatch console & live map','branch & workshop consoles','≤4 clicks to any record','bulk actions','keyboard-first']],
  ['P04','Corporate B2B Portal','Corporate & government','500–2,000','Next.js 15',
   ['multi-user approval chains','estate management','bulk CSV requests','SLA & credit visibility','consolidated billing','scoped analytics']],
  ['P05','Vendor & Supplier Portal','Vendors · couriers · recyclers','200–500','Odoo + Next.js',
   ['onboarding & documents','RFQ response','PO acknowledge + ASN','invoice match status','scorecard','logistics & recycling flows']],
  ['P06','Analytics & Executive','Management','25–60','Metabase + Grafana',
   ['executive cockpit','branch league table','real-time ops board','self-service on certified data','scheduled bursting','threshold alerts']],
  ['P07','Marketplace Seller App','Engineers & shops','500–2,000','Next.js + RN',
   ['KYC & agreement','listings & stock','job broadcast & bidding','earnings & payouts','performance scorecard','growth tools']],
  ['P08','Brand Partner Portal','17+ brand partners','50–150','Next.js 15',
   ['claim review & bulk decisions','evidence packs','reconciliation & remittance','consignment parts','rate cards','our performance on their brand']],
  ['P09','Logistics & Rider App','Riders & coordinators','50–200','Flutter',
   ['optimised manifest','scan + OTP collection','transit exceptions','identity-verified delivery','COD reconciliation','full offline']],
  ['P10','Contact Centre Console','Agents & supervisors','30–80','Next.js 15',
   ['unified queue (voice→social)','Customer-360 screen pop','act-in-conversation','AI suggested replies','wrap-up coding','live supervision']],
  ['P11','Field Auditor & Quality','Auditors & regional managers','20–60','Flutter',
   ['assigned audits & checklists','offline evidence capture','cash & stock spot checks','CAPA verification','auditee signature','on-device report']],
  ['P12','Partner & Referral Portal','Alliance partners & referrers','100–500','Next.js 15',
   ['application & approval','referral links & tracking','earnings & payouts','co-marketing assets','reseller allocation','performance ranking']]
];

/* ---------- misc -------------------------------------------------------- */
D.BRANCHES = BRANCHES; D.BRANDS = BRANDS; D.TECHS = TECHS; D.CUSTOMERS = CUSTOMERS;
D.DEVICES = DEVICES; D.MODELS = MODELS; D.PARTS = PARTS; D.PAY = PAY; D.CHANNELS = CHANNELS;
D.TODAY = TODAY;
})();
