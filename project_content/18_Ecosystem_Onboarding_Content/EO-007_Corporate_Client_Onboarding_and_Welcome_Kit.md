---
id: EO-007
title: Corporate Client Onboarding and Welcome Kit
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Account Management
author: Account Management with Content Design and Localisation
reviewers: [Chief Commercial Officer, Chief Financial Officer, Operations Director, Legal Counsel, Data Protection Officer, Master Data Owner, Localisation Lead, Content Design Lead]
approver: Content Design Lead with Account Management
content_class: D
purpose: >
  The kit issued to a newly contracted corporate or government client to get them from signature
  to self-service: how their account and site hierarchy is built, how their asset estate is
  uploaded, how their own users, roles and approval chains are configured, what they may order
  against their contract, how SLA and service credits work, and who they escalate to. Corporate
  portal adoption is targeted above 85% of contracted clients and Gate 4 requires ten clients
  transacting; adoption is set in the first six weeks after signature, when the client is still
  deciding whether the portal is easier than telephoning their account manager.
traces_to: [P04, M08, M05, M07, M09, M11, M17, M20, M25, M27, M06, M18, 04-00 P04, 05-04 §8 EA-01, EA-02, G4-05, G4-08, KPI-028, KPI-030, KPI-052, KPI-054, MD-006, MD-007, MD-013, MD-015, MD-019, MD-028, MD-032, MD-036, LG-003, LG-008, LG-013, LG-015, LG-016, LG-017, DT-020, DT-031, SP-015, UI-014, UI-040, HC-006, NT-010, TR-013, EO-008, EO-011, EO-014, CM-014, AP-008, RP-005]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: EO-007_Corporate_Client_Onboarding_and_Welcome_Kit_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P04 capability set across account, asset estate, service, contracts, managed services, SLA, billing, reporting, procurement, support and compliance; users "corporate and government client staff" 500–2,000; KPIs "corporate clients actively using the portal > 85% of contracted clients", "bulk requests submitted through the portal > 70%", "bulk service request creation time < 5 minutes", "invoice disputes < 3% of consolidated invoices", "corporate client satisfaction > 4.6/5"; Wave W4
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md §2 node structure group/company/division/site/department with maximum depth 5, is_billing_node, billing_cycle, client cost_centre_ref printed on DT-020, approval_chain_id, contract_id, sla_band_code inheriting from parent when null; §2.1 four-level approval chain defined per node and inheriting downward; §4 CAH-01…CAH-07
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 4 G4-05 "10+ corporate clients transacting on the B2B portal", G4-08 "consolidated B2B invoicing operating correctly"; §2.4 KPI-028 AMC/RAMC renewal rate, KPI-030 contract SLA attainment
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-013_Category_10_LG_Content_Audit.md finding LG-01 — gate F3 fails: DT-031 maps nine MD-028 fields that do not exist, so an SLA breach cannot be computed from the register it cites
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md §3 Wave 4 — Agreements, Billing & Contact, Months 14–18; delivers the contract engine, consolidated B2B invoicing and the corporate B2B portal with asset estates
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Corporate Client Onboarding and Welcome Kit

| Item | Value |
|---|---|
| Audience | Newly contracted corporate and government clients — their administrators, requesters, approvers and finance staff |
| Population | **500–2,000** client users (`04-00` P04) |
| Portal | `P04` Corporate B2B Portal |
| Language | **Bilingual.** Portal-facing guidance in Bengali and English; contractual documents remain English (`CG-010` §3.3) |
| Issued by | Account Management, at contract signature |
| Wave | W4 · Months 14–18 |
| Gate criteria evidenced | `G4-05` 10+ corporate clients transacting · `G4-08` consolidated B2B invoicing |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions appear as §4.1 (**journey** — signature to
> self-service), §4.3 (**checklist** — what the client must supply, and in what form) and §4.8
> (**first 90 days**). Template 15 `TPL_Onboarding_Kit.md` does not exist.

---

## 1. Purpose

A corporate contract is signed by a procurement or facilities director. The portal is then used —
or not used — by fifty people that director will never watch: a site administrator in Chittagong,
a department head approving a repair estimate, an accounts-payable clerk checking a consolidated
invoice against four hundred lines.

`04-00` sets P04's adoption target at **more than 85% of contracted clients actively using the
portal**, with **more than 70% of corporate requests submitted in bulk through it**. `G4-05`
requires ten clients transacting before Wave 4 closes. None of those is achieved by the signature;
all of them are decided in the six weeks after it.

| Absent | Consequence |
|---|---|
| A structured account build | The hierarchy is invented under time pressure by whoever loads the first site, and `MD-015`'s billing node, approval chain and SLA inheritance are wrong from the first invoice |
| A stated estate-upload format and validation rule set | The client sends a spreadsheet, it fails, they send it again, and by the third attempt the account manager is taking requests by email — permanently |
| Named escalation contacts and a stated SLA mechanism | The first breach becomes an argument about what was promised, and `KPI-030` contract SLA attainment has no shared meaning |

**What this kit is not.** It is not the contract or the SLA terms (`LG-015`, `LG-013`), not the
portal terms (`LG-003`), not the client-administrator configuration guide (**`EO-008`**), not the
screen copy (`UI-014`, `UI-040`), not the help set (`HC-006`), and not the internal contract
lifecycle procedure (`SP-015`).

---

## 2. Scope

**In scope.** The onboarding journey from signature to first invoice; the account and site
hierarchy as the client experiences it; the asset-estate upload — format, validation, and what
happens to rejected rows; user roles and what each can do; the approval-chain concept at the
level a requester needs (the *configuration* of it is `EO-008`); what the client may order and
against what coverage; SLA, breach visibility and service credits; consolidated billing and the
invoice-approval and dispute routes; managed-services onboarding where contracted; compliance
artefacts the client can self-serve; reporting scope; support and escalation contacts; and the
first-90-days adoption plan.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| **Multi-user, multi-site and multi-level approval configuration by the client's own administrator** | **`EO-008`** |
| The contract, AMC/SLA master terms and service-credit rules | `LG-015`; warranty and service terms `LG-013` |
| Portal terms of use | `LG-003` |
| Managed-services and remote-access consent terms | `LG-016` |
| Data-recovery and secure-destruction terms | `LG-017` |
| The account hierarchy **as a data standard** | `MD-015`; addresses `MD-007`; geography `MD-006` |
| SLA band definitions | `MD-028` — **and see `O-02`** |
| Contract and AMC template catalogue | `MD-032` |
| The internal contract lifecycle procedure | `SP-015` |
| Screen copy, help, notifications | `UI-014`, `UI-040`, `HC-006`, `NT-010` |
| The consolidated invoice document | `DT-020`; SLA/service-credit statement `DT-031` |
| Price and rate-card change communication | **`EO-011`** |
| Contract exit, data return and account closure | **`EO-014`** |
| **Moving an *existing* contracted client onto `P04`** | **`CM-014`** Corporate Client Transition Pack — a one-off change event per account |
| The client's own systems integrating to ours — estate exchange, ITSM ticket exchange, federated sign-on | **`AP-008`** Partner Integration Guide — Corporate |
| Scoped analytics the client sees on their own portal | `RP-005` |

> **The `CM-014` boundary.** `CM-014` owns the **transition** of an already-contracted client from
> the legacy way of working — including the consolidated-invoice format change and SLA reporting
> continuity, which a newly signed client never experiences. This kit owns **onboarding** — the
> build that every client passes through, transitioned or new. Where both apply, `CM-014` sequences
> the account and this kit supplies stages 2–10.

---

## 3. Audience

| Reader | Uses it for | Language |
|---|---|---|
| **Client procurement / facilities director** | What happens now that they have signed, and what they must supply | Either |
| **Client portal administrator** | The build sequence; then hands over to `EO-008` | Either |
| **Client site administrator** | Their site, their estate, their requesters | **Bengali** |
| **Client requester / department head** | Raising and approving a request, and what coverage means | **Bengali** |
| **Client accounts-payable clerk** | The consolidated invoice, its breakdown, and the dispute route | **Bengali** |
| **1000FiX Account Manager (`R22`)** | The kit they present and the build they run | English |
| **1000FiX Finance Officer (`R27`)** | The billing structure agreed at onboarding | English |

---

## 4. Content

### 4.1 The onboarding journey

**Six weeks, ten stages.** The dates are commitments the account manager makes at signature.

| # | Stage | Client does | 1000FiX does | Target | Exit condition |
|---|---|---|---|---|---|
| **1** | **Kick-off** | Names the portal administrator, the billing owner and the escalation contact | Presents this kit; confirms contract scope, coverage and SLA band | Week 1 | Three names, with deputies |
| **2** | **Structure** | Confirms the hierarchy — group, company, division, site, department (`MD-015`) | Builds it; **maximum depth 5, no cycles** (`CAH-01`) | Week 1–2 | Structure signed off by the client |
| **3** | **Billing** | Nominates billing nodes, billing cycle and their **own** cost centres | Configures; **at least one billing node per client** (`CAH-02`), each with a cycle and address (`CAH-03`) | Week 2 | Billing structure agreed by the client's finance owner |
| **4** | **Estate** | Supplies the asset estate in the §4.3 format | Validates, loads, reports rejected rows with reasons | Week 2–3 | Estate loaded, exceptions resolved or accepted |
| **5** | **Users** | Supplies users with roles and site or department scope | Provisions through `M29` under `PS-01` | Week 3 | Every user can sign in and sees **only their scope** |
| **6** | **Approvals** | Defines approval chains per node | Configures; **a chain with no final approver is rejected** (`CAH-05`) | Week 3–4 | Chains terminate; **then hand over to `EO-008`** |
| **7** | **Catalogue** | Reviews what they may order and at what price | Publishes the contracted service catalogue and pricing | Week 4 | Catalogue confirmed |
| **8** | **Walkthrough** | Attends with requesters, approvers and finance | Demonstrates single and **bulk** request, approval, tracking, invoice | Week 4 | A real request raised by a client user |
| **9** | **First request** | Raises a real service request through the portal | Fulfils it, tracked end to end | Week 5 | The client has seen the loop close |
| **10** | **First invoice** | Reviews and approves the consolidated invoice | Issues it against the agreed structure (`DT-020`) | Week 6–8 | Invoice approved without dispute |

> **Stage 10 is the real adoption test.** A client whose first consolidated invoice is disputed
> has a structure problem from stage 3, not a billing problem — and `04-00` targets invoice
> disputes **below 3%**.

### 4.2 How the account is structured, and why it matters to the client

`MD-015` is a data standard; this is what it means to a client who is being asked to describe
their own organisation.

| Level | What it usually is | What it controls |
|---|---|---|
| **Group** | The parent, where one exists | Consolidated reporting |
| **Company** | The contracting legal entity | The contract, and who is invoiced |
| **Division** | Business unit or region | Reporting and approval scope |
| **Site** | A physical location — **an address is mandatory here** (`CAH-04`) | Where a technician is sent; where assets live |
| **Department** | A team or cost-bearing unit | The client's own cost centre on the invoice |

**Four decisions at stage 2–3 that are expensive to change later:**

| Decision | Why it is hard to change |
|---|---|
| **Where the billing node sits** | Changing it mid-cycle requires Finance approval (`CAH-07`) and splits a period across two structures |
| **The client's cost-centre codes** | They are printed on `DT-020` and reconciled by the client's own finance system |
| **The SLA band per node** | It inherits downward when null (`MD-015` `sla_band_code`); a band set at company level silently governs every site below it |
| **Hierarchy depth** | Maximum 5 (`CAH-01`). A client with six real levels must collapse one, and which one is a business decision, not a data one |

> **A node cannot be archived while it has open service orders or unbilled charges** (`CAH-06`).
> Stated at onboarding because clients reorganise, and the first attempted site closure is when
> they discover it.

### 4.3 The estate-upload checklist

The largest single cause of stalled corporate onboarding, and the most preventable.

| # | Column | Required | Rule | Common failure |
|---|---|---|---|---|
| 1 | Asset identifier — serial or IMEI | **Yes** | Must be unique within the client | Blank rows; the same serial on two sites |
| 2 | Make and model | **Yes** | Must resolve in `MD-021`; unmatched models are reported, not silently created | Free-text model names |
| 3 | Category | **Yes** | `MD-021` device family | — |
| 4 | Site | **Yes** | Must resolve to a `site` node with an address (`CAH-04`) | A site named in the file that does not exist in the hierarchy |
| 5 | Department | Where the client bills by department | Must resolve to a `department` node | — |
| 6 | Assigned user | Optional | Free text or a named client user | — |
| 7 | Purchase date | Where warranty is claimed | Drives warranty status | Missing — the asset then shows out of warranty |
| 8 | Warranty expiry or reference | Optional | `M09` coverage lookup | — |
| 9 | Contract coverage flag | **Yes** | Whether the asset is in the contracted estate | **Assets loaded but not covered, then requested against and refused** |
| 10 | Client asset tag / cost centre | Where the client reconciles by tag | Printed on `DT-020` | — |
| 11 | Condition or status | Optional | Active, spare, retired | Retired assets loaded as active, inflating the estate |

**What happens to a rejected row.** Each is reported with its row number and reason. **The load is
not partial-silent**: a file with 40 rejected rows out of 4,000 loads 3,960 and returns 40 with
reasons. The client corrects and re-submits only the 40.

**Bulk update and retirement use the same file shape**, so a client learns one format
(`04-00` P04: "bulk upload and update … retire and decommission").

### 4.4 Users and what each role can do

| Role | Can | Cannot |
|---|---|---|
| **Portal administrator** | Manage users, sites, departments, approval chains; see everything in their scope | Change the contract, prices or SLA band |
| **Site administrator** | Manage their site's estate, users and requests | See other sites |
| **Requester** | Raise single and bulk requests; track them; see coverage before submitting | Approve; see cost outside their scope |
| **Approver** | Approve estimates and requests **within delegated authority** | Exceed their limit — it routes upward |
| **Finance user** | Consolidated invoices, breakdown by site, department and asset; approve or dispute | Raise service requests |
| **Read-only / reporting** | Scoped analytics on their own estate, with export | Transact |

**Every role sees only their own organisation's data, and only their scope within it**
(`EA-01`, `EA-02`; `LG-003` states it). A client with competitors in the same building asks this
question at stage 5, and the answer is in the kit before they do.

### 4.5 Raising work — coverage before submission

`04-00` P04 states the mechanism that saves the most client time: **requests are validated against
contract coverage before submission**, not rejected after it.

| Route | Use it for | Target |
|---|---|---|
| Single request | One asset, one fault | — |
| **Bulk request (CSV upload)** | A site move, a fleet fault, a scheduled sweep | **Creation in under 5 minutes**; > 70% of corporate requests |
| Scheduled maintenance | Preventive visits generated from the contract | `G4-04` |
| Procurement | Parts, rentals, trade-in and decommission projects against agreed pricing | — |

**Three answers a requester can get at submission, and what each means:**

| Answer | Meaning | What the requester does |
|---|---|---|
| **Covered** | The contract covers this asset and this work | Submit |
| **Covered with an excess or limit** | Partly covered; the balance is chargeable | Submit; an estimate follows for approval |
| **Not covered** | Out of contract — chargeable, or out of scope entirely | Submit as chargeable, or route to procurement |

### 4.6 SLA, breach and service credits

| Element | Where it lives | What the client sees |
|---|---|---|
| SLA band per node | `MD-015` `sla_band_code` → `MD-028`, **inherits downward when null** | Their band, per site |
| Real-time SLA status per request | `P04` | A countdown, not a retrospective report |
| Breach history | `P04` | Every breach, with cause |
| **Service credits earned** | **`LG-015`** master terms and credit rules | Credits accrued and applied |
| The statement | `DT-031` | Per period |

> **This section carries a known, open defect and says so.** `AUDIT-013` finding `LG-01` records
> that **`DT-031` maps nine `MD-028` fields that do not exist**, so an SLA breach cannot currently
> be computed from the register the statement cites. `KPI-030` targets 95% contract SLA attainment
> at W4. **Until `LG-01` closes, this kit describes a service-credit mechanism that cannot be
> calculated** — recorded as `O-02`, and it is not a Category 18 defect to fix.

### 4.7 Billing, disputes and the compliance shelf

| Item | How it works |
|---|---|
| **Consolidated invoice** | One invoice per billing node per cycle, itemised by site, department and asset (`DT-020`, `G4-08`) |
| **Client cost centres** | The client's own codes, carried through to the invoice line (`MD-015` `cost_centre_ref`) |
| **Invoice approval workflow** | The client's own approval, in the portal, before payment |
| **Dispute** | Raised per line, not per invoice. **A disputed line does not hold the undisputed remainder** |
| **Statements** | Per billing node, per period |
| **Compliance artefacts** | Destruction certificates, disposal certificates and service evidence packs, self-served (`M06`, `M18`, `LG-017`) |

**The compliance shelf is an under-sold part of the proposition.** A corporate client with a data
-protection obligation needs destruction certificates on demand, and today obtains them by email
request. Self-service here removes a support load and is a genuine reason to sign in.

### 4.8 The first 90 days

| Days | Client milestone | 1000FiX milestone | Adoption test |
|---|---|---|---|
| **0–30** | Structure, billing, estate and users live; walkthrough held | Account built; catalogue published | **Has one client user signed in without the account manager present?** |
| **31–60** | First requests raised **by requesters, not by the administrator**; first estimate approved in the portal | First fulfilment tracked end to end; first bulk request | **Portal request share for this client** |
| **61–90** | First consolidated invoice reviewed and approved; first report exported | First period reconciled; first SLA report issued | **Invoice approved without dispute** (`04-00`: disputes < 3%) |
| **91+** | Steady state; scheduled maintenance calendar in use | First quarterly service review | This client counts toward `G4-05` and the 85% adoption target |

**The 30-day test is deliberately harsh.** A client whose only portal user is the administrator
the account manager trained is not an adopted client; it is a single point of failure with a
login. `04-00`'s 85% target counts *clients actively using*, and the count that matters is
requesters, not administrators.

### 4.9 Rules

| # | Rule |
|---|---|
| **CO-01** | The kit is issued **at signature**, not at portal launch. A client onboarded to a contract and later to a portal onboards twice |
| **CO-02** | The four hard-to-change decisions (§4.2) are stated **before** the structure is built, with their consequences |
| **CO-03** | The estate template is issued **once**, with validation rules stated, and rejected rows are returned with reasons and row numbers |
| **CO-04** | Coverage is validated **before** submission, and the three possible answers are stated to requesters (§4.5) |
| **CO-05** | No price, rate, SLA target or credit value is stated in the kit. The contract, `MD-029` and `LG-015` hold them; `EO-011` governs change communication |
| **CO-06** | The data-boundary statement (§4.4) appears in every edition |
| **CO-07** | Every contact named in the kit is a **person with a deputy**. A corporate escalation ladder ending in a mailbox has no top |
| **CO-08** | Approval-chain **configuration** is `EO-008`. This kit explains the concept and hands over at stage 6 — it never duplicates the configuration guidance (`CP-01`) |
| **CO-09** | Bengali is required for the requester, approver, site-administrator and finance-clerk sections. Contractual references remain English (`CG-010` §3.3, §4.1) |
| **CO-10** | Where a described capability has an open defect, the kit **says so** rather than describing an intended state — §4.6 is the current instance |
| **CO-11** | Managed-services onboarding is included **only where contracted**, and carries the `LG-016` remote-access consent position |
| **CO-12** | Nothing in the kit varies the contract or `LG-003`. Variation requests route to Legal through the account manager |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`MD-015`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md) | The hierarchy, billing nodes, approval chains and SLA inheritance the whole build rests on |
| [`MD-013`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md), [`MD-006`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md), [`MD-007`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md) | Party master, geography and address format for sites |
| [`MD-021`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Model resolution for the estate upload |
| [`MD-028`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | SLA band definitions — **carrying `AUDIT-013` `LG-01`** |
| [`MD-032`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032_Contract_and_AMC_Template_Catalogue.md) | Contract and AMC templates |
| [`MD-036`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md) | Cost centre and dimension register, against which client cost centres are held |
| `M08`, [`SP-015`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md) | The contract lifecycle this kit sits inside |
| [`LG-003`](../10_Legal_Policy_and_Compliance/LG-003_Portal_Terms_of_Use_Corporate.md), [`LG-013`](../10_Legal_Policy_and_Compliance/LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md), [`LG-015`](../10_Legal_Policy_and_Compliance/LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md), `LG-016`, `LG-017` | Portal terms, service and warranty terms, SLA and credits, remote access, destruction |
| [`EO-008`](EO-008_Corporate_Admin_Setup_and_Delegation_Guide.md) | Takes over at stage 6 for administrator configuration |
| [`DT-020`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md), [`DT-031`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md) | Consolidated invoice and SLA/service-credit statement |
| [`UI-014`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-014_P04_Corporate_B2B_Portal_UI_Copy_Pack.md), [`UI-040`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-040_Registration_and_Onboarding_Flow_Copy.md), [`HC-006`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-006_Help_Set_P04_Corporate_B2B_Portal.md), `NT-010` | Screens, flow copy, help and notifications |
| [`TR-013`](../08_Training_and_Enablement/08B_Course_Packs/TR-013_Course_Pack_Procurement_Officer.md) | Internal training for the account and vendor-facing roles |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md), [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Price change communication; contract exit and data return |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly during W4–W5 while adoption is being established; annually thereafter |
| Trigger for out-of-cycle review | A change to `MD-015` structure rules; a `P04` release changing the estate upload or request flow; closure of `AUDIT-013` `LG-01`; a change to `LG-003` or `LG-015`; adoption falling below the 85% target; invoice disputes exceeding 3% |
| Owner | Account Management, with Finance for §4.7 and the Master Data Owner for §4.2–§4.3 |
| Change control | Any change to the estate template or to the billing structure guidance requires Finance and Master Data Owner sign-off — both are reconciled by the client's own systems |
| Effectiveness measure | Days from signature to first client-raised request; portal request share per client; first-invoice dispute rate |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The corporate adoption target has no registered KPI identifier.** `04-00`'s five P04 targets — 85% adoption, 70% bulk share, 5-minute bulk creation, sub-3% invoice disputes, 4.6 CSAT — exist only in the portal specification. `06-02` §4 `G4-05` requires *"10+ corporate clients transacting"*, which is a **count**, not an adoption rate, and the two are not the same test: ten clients transacting is satisfiable while adoption sits far below 85%. **The number in this file's `purpose:` is not gate-measurable as written**. **This is an instance of `AUDIT-015` RP-01, not a new finding**: that audit counted **250 KPI identifiers in use against 95 registered in `06-02`**, with 196 unregistered, and recommended widening the register per `RP-001` §4.3 (R-01). The portal targets below are part of the 196. | BI Lead with Enterprise Architecture | **W4 — before the Gate 4 pack** |
| **O-02** | **§4.6 describes a service-credit mechanism that cannot currently be computed.** `AUDIT-013` `LG-01` is a **critical, open** finding: `DT-031` maps nine `MD-028` fields that do not exist. `LG-015` holds the credit rules, `KPI-030` targets 95% SLA attainment at W4, and `TS-007` `UAT-R22-010` already fails on the same ground from the test side. **This kit must either describe the mechanism with the defect stated (as it does) or omit the section** — it cannot describe a working one | Enterprise Architecture with Service Operations and Legal Counsel | **W4 — before the first SLA statement** |
| **O-03** | **No estate-upload template artefact exists.** §4.3 specifies eleven columns and their validation; **no `DT` or `MD` file holds the file itself**, and `DM-012` migration load templates cover migration, not client self-service. A client cannot be issued a specification in place of a template | Master Data Owner with Account Management | **W4 — before the first client build** |
| **O-04** | **The six-week build has no capacity model.** §4.1 commits an account manager to ten stages per client. At `G4-05`'s ten clients this is manageable; at the 500–2,000 user population implied by `04-00` it is not, and `06-01` §3 Wave 4 allocates no onboarding line. **Corporate onboarding is the only ecosystem onboarding in Category 18 that is a delivered service rather than a document** | Programme Manager with CCO | **W4 — before the first cohort** |
| **O-05** | **Government clients are named in the audience and given no distinct treatment.** `04-00` P04 says *"corporate and government client staff"*. Public-sector procurement in Bangladesh carries tender, approval and disclosure requirements that a commercial onboarding does not, and **no `LG`, `SP` or `EO` file distinguishes them**. §4.1 stage 3's billing and §4.7's invoice-approval workflow are the likeliest points of divergence | Legal Counsel with CCO | **W4** |
| **O-06** | **Bengali is required and unresourced.** §3 marks four of seven reader roles as Bengali readers, and `CG-010` §3.3 classes corporate client users as *"Partly — portal UI yes; contractual and technical documents English"*. **The split inside a single kit has not been drawn**: §4.2 and §4.3 are technical, §4.5 and §4.7 are operational, and the boundary between them is a judgement nobody has made | Localisation Lead *(unappointed)* with Account Management | **W4 minus 6 weeks** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions placed and the template gap noted
- [x] Ten-stage, six-week journey with a target and an exit condition at each stage
- [x] **The four hard-to-change structural decisions named, with why each is expensive to reverse**
- [x] `MD-015` rendered from the client's point of view, with `CAH-01`…`CAH-07` consequences stated
- [x] Eleven-column estate-upload checklist with the common failure for each and the partial-load behaviour
- [x] Six client roles with what each can and cannot do, and the data boundary stated
- [x] Coverage-before-submission mechanism stated with its three possible answers
- [x] **The `AUDIT-013` `LG-01` service-credit defect stated in the file rather than described as working**
- [x] Billing, per-line dispute and the compliance self-service shelf covered
- [x] First-90-days adoption plan whose 30-day test is a client user signing in unaccompanied
- [x] Twelve rules, including the `CP-01` handover to `EO-008` at stage 6
- [x] All internal links resolve
- [x] Six open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` the 85% adoption target is not gate-measurable — outstanding**
- [ ] **`O-02` service credits cannot be computed (`AUDIT-013` `LG-01`, critical, open) — outstanding**
- [ ] **`O-03` no estate-upload template artefact — outstanding**
- [ ] **`O-04` no onboarding capacity model — outstanding**
- [ ] **`O-05` government clients undifferentiated — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending Content Design Lead with Account Management**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
