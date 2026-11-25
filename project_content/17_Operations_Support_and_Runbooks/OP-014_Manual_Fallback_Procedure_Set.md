---
id: OP-014
title: Manual Fallback Procedure Set
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with Platform Engineering
author: Operations with Platform Engineering, Finance and Content Design
reviewers: [Operations Director, Chief Technology Officer, Chief Financial Officer, Branch Operations Manager, Field Operations Manager, Tax Manager, Localisation Lead, Internal Audit, Support Lead]
approver: Operations Director
content_class: C
purpose: >
  The paper or degraded-mode procedure for every P0 integration and for total system
  unavailability, with the reconciliation that puts the records back afterwards. IP-09 and NFR-050
  require a documented, tested manual fallback for every P0 integration; without one, a
  third-party outage stops 51+ branches from trading, and an undocumented improvised fallback
  produces records that cannot be reconciled and money that cannot be traced.
traces_to: [05-03 IP-09, 05-06 NFR-050, NFR-047, M01, M19, M20, M27, OP-001, OP-004, OP-007, OP-008, OP-009, OP-011, OP-012, OP-013, DT-011, DT-016, SP-007, SP-008, SP-019, NT-025]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: OP-014_Manual_Fallback_Procedure_Set_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §1 IP-09; §2.1–§2.7 the integration catalogue with priorities; §7 the P0 fallback register
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-050 every P0 integration has a documented, tested manual fallback; NFR-047 technician app functional without connectivity for 24 hours
    verified: 2026-08-20
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md — manual money receipt format and numbering
    verified: 2026-08-20
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md — counter cash handling, reconciliation and banking controls
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-021 — Mushak 6.3 tax invoice format compliance under the VAT and SD Act 2012; sequence integrity requirement carried in DT-011
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# OP-014 — Manual Fallback Procedure Set

> **This is the file that keeps 51+ branches trading when the system does not.** It is written to
> be *printed*, held in a physical folder at every site, and used by someone who is not an engineer,
> under pressure, in Bengali.
>
> **The operational version of this file is the Bengali counterpart.** English is the source of
> truth for governance; Bengali is what is in the folder at the counter.

---

## 1. Purpose

`IP-09` states the principle — *"third-party outages must not stop the business"* — and `NFR-050`
makes it testable: every P0 integration has a **documented, tested** manual fallback. This file is
that documentation, plus the two things a fallback register alone never contains:

1. **What the person at the counter actually does**, step by step, with the form in front of them.
2. **How the records get back into the system afterwards without duplicating anything.**

**What stops without this file:** at the first payment-gateway outage, 51+ branches each invent a
different procedure. Money is taken against handwritten notes with no sequence, no customer
reference and no VAT position. Two weeks later Finance cannot reconcile it, the Mushak sequence has
gaps, and the audit finding is not the outage — it is the response.

---

## 2. Scope

**In scope:** the fallback procedure for every P0 integration; the total-unavailability procedures
for branch, field, dispatch, contact centre and finance; the fallback pack held at every site; the
rules that make manual records reconcilable; the catch-up and reconciliation procedure; and the
testing regime that keeps all of it real.

**Out of scope:**

| Situation | Owned by |
|---|---|
| Deciding to invoke a fallback | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) §4.8 (authority), [`OP-012`](OP-012_Disaster_Recovery_and_Continuity_Playbook.md) §4.1 (in a disaster) |
| Telling people a fallback is in force | [`OP-004`](OP-004_Incident_Communication_Template_Set.md), [`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) |
| The technical restoration | [`OP-007`](OP-007_Runbook_Core_ERP_Platform.md)…`OP-012` |
| The normal-mode process being replaced | The relevant `SP` SOP, named in each procedure |
| The manual money receipt and invoice **formats** | [`DT-016`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md), [`DT-011`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-011_Sales_Register_Mushak_6_2.md) |
| Cash handling and banking controls | [`SP-019`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md) |
| Post-incident review | [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md) |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| Branch coordinators and front desk | Keep serving customers |
| Cashiers | Take money safely and traceably |
| Dispatchers | Keep allocating work |
| Field technicians and riders | Know that offline is normal and what to do beyond 24 hours |
| Contact centre agents | Keep taking bookings |
| Finance | Reconcile afterwards |
| Platform Engineering | Know what the business is doing while they fix it |
| Internal Audit and Tax | Evidence that manual operation preserved the controls |

---

## 4. Content

### 4.1 How to use this set

| # | Rule |
|---|---|
| **FB-R1** | **A fallback is invoked by a named person, announced, and timed.** Start time, end time and the procedure code go on every form and into the incident record |
| **FB-R2** | **Never invent a fallback.** If the situation is not in §4.3–§4.5, call the service desk ([`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md)) and record what you did. An unlisted situation becomes a new procedure here within 5 working days |
| **FB-R3** | **Every manual record carries three things**: the customer's mobile number, the branch code, and the pre-printed serial of the form. Those three make reconciliation possible |
| **FB-R4** | **Never re-enter a form twice.** Catch-up entry is done by the named person in §4.6, working from the serial sequence — not by whoever has a free moment |
| **FB-R5** | **Do not promise digital artefacts you cannot produce** — no "the SMS will arrive shortly", no "you will get the e-receipt today" |
| **FB-R6** | **Serial-numbered stationery is controlled stock.** Issued against signature, returned against signature, and every serial accounted for — including the spoiled ones |
| **FB-R7** | The fallback ends when the service desk says it ends, **not** when the system looks like it is back |

**The four sentences every counter needs, in both languages:**

| English | Bengali |
|---|---|
| The system is temporarily unavailable. We are still serving you — we will do it on paper and enter it afterwards. | সিস্টেম সাময়িকভাবে বন্ধ আছে। আমরা আপনার সেবা চালিয়ে যাচ্ছি — কাগজে লিখে পরে সিস্টেমে তুলব। |
| Please give me your mobile number — that is how we will find your job when the system returns. | অনুগ্রহ করে আপনার মোবাইল নম্বরটি দিন — সিস্টেম ফিরে এলে এটি দিয়েই আমরা আপনার কাজটি খুঁজে পাব। |
| Here is your receipt. Please keep it — this is your proof until the system confirms it. | এই যে আপনার রসিদ। এটি রেখে দিন — সিস্টেম নিশ্চিত না করা পর্যন্ত এটিই আপনার প্রমাণ। |
| You will receive an SMS confirming everything once the system is back. | সিস্টেম ফিরে এলে সবকিছু নিশ্চিত করে আপনি একটি এসএমএস পাবেন। |

### 4.2 The fallback pack

Held **physically** at every branch, workshop, the central warehouse and the contact centre.
Checked monthly by the branch coordinator; replenished by Operations.

| # | Item | Quantity per site | Serial-controlled |
|---:|---|---|:--:|
| 1 | Paper job card (`FB-01` form) | 100 | ✔ |
| 2 | Manual money receipt book (`DT-016` format) | 2 books | ✔ |
| 3 | **Manual tax invoice book** from the reserved Mushak range (`DT-011`) | 1 book | ✔ **statutory** |
| 4 | Device intake and condition sheet | 50 | ✔ |
| 5 | Customer signature/acknowledgement sheet | 50 | ✔ |
| 6 | Stock issue and return sheet | 50 | ✔ |
| 7 | Gate pass / stock transfer note pad | 25 | ✔ |
| 8 | Dispatch allocation board sheet (`FB-10`) | 20 | ✘ |
| 9 | This procedure set, printed, in Bengali | 1 | ✘ |
| 10 | The severity and contact card (`OP-013` §4.1, §4.10) | 1 | ✘ |
| 11 | Branch telephone tree, printed (`OP-013` `OB-01`) | 1 | ✘ |
| 12 | Twelve essential support macros, printed ([`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) §4) | 1 | ✘ |
| 13 | Carbon paper / duplicate books where forms are not self-carbonating | as needed | ✘ |

> **`FP-01`.** The pack is checked **monthly** and its check is recorded. A fallback pack that is
> out of stock, out of date, or locked in the manager's drawer is the most common reason a
> documented fallback fails in practice — not the procedure.

### 4.3 Total-unavailability procedures

#### `FB-01` — Branch paper mode *(শাখা কাগজ পদ্ধতি)*

| Item | Value |
|---|---|
| **Trigger** | ERP core unreachable (`OP-007`), identity down ([`OP-009`](OP-009_Runbook_Identity_and_Access.md)), or a declared disaster (`OP-012`) |
| **Who** | Branch coordinator, front desk, cashier |
| **Replaces** | [`SP-007`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) walk-in intake, normal job creation |
| **Tolerable** | 8 hours; beyond that the day's queue becomes unrecoverable |

| Step | Action | Bengali instruction |
|---:|---|---|
| 1 | Announce at the counter: the system is down, we are serving on paper | কাউন্টারে জানান: সিস্টেম বন্ধ, আমরা কাগজে সেবা দিচ্ছি |
| 2 | Take the paper job card. Write the **serial**, date, time, branch code | কাগজের জব কার্ড নিন। **সিরিয়াল**, তারিখ, সময়, শাখা কোড লিখুন |
| 3 | Record customer name and **mobile number** — mandatory, no exceptions | গ্রাহকের নাম ও **মোবাইল নম্বর** লিখুন — বাধ্যতামূলক |
| 4 | Record device: type, brand, model, serial/IMEI, visible condition | ডিভাইস লিখুন: ধরন, ব্র্যান্ড, মডেল, সিরিয়াল/আইএমইআই, বাহ্যিক অবস্থা |
| 5 | Record the reported fault in the customer's own words | গ্রাহকের নিজের ভাষায় সমস্যাটি লিখুন |
| 6 | Take a photograph of the device with the job card serial visible in frame | জব কার্ডের সিরিয়াল ফ্রেমে রেখে ডিভাইসের ছবি তুলুন |
| 7 | Customer signs the intake sheet; give them the **customer copy** | গ্রাহক ইনটেক শিটে স্বাক্ষর করবেন; তাঁকে **গ্রাহক কপি** দিন |
| 8 | Tell the customer: you will receive an SMS with your reference when the system returns | গ্রাহককে বলুন: সিস্টেম ফিরলে রেফারেন্সসহ এসএমএস পাবেন |
| 9 | File the branch copy in the **fallback tray**, in serial order | শাখার কপি সিরিয়াল অনুসারে **ফলব্যাক ট্রে**-তে রাখুন |
| 10 | Every hour, note the last serial used on the fallback log | প্রতি ঘণ্টায় ব্যবহৃত শেষ সিরিয়ালটি ফলব্যাক লগে লিখুন |

**Reconciliation:** §4.6 catch-up. Serial gaps are investigated before the fallback is closed.

#### `FB-02` — Field mode *(ফিল্ড পদ্ধতি)*

| Item | Value |
|---|---|
| **Trigger** | Technician or rider app unusable ([`OP-011`](OP-011_Runbook_Portal_and_Mobile_App_Operations.md)), or offline beyond 24 hours (`NFR-047`) |
| **Who** | Technician, rider, field supervisor |
| **Replaces** | [`SP-008`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md) on-site visit recording |
| **Tolerable** | One shift |

| Step | Action | Bengali instruction |
|---:|---|---|
| 1 | **Do not reinstall the app. Do not sign out. Do not clear app data.** | **অ্যাপ আবার ইনস্টল করবেন না। সাইন আউট করবেন না। অ্যাপের ডেটা মুছবেন না।** |
| 2 | If the app opens, keep working in it — it stores everything offline | অ্যাপ খুললে তাতেই কাজ চালিয়ে যান — এটি সব অফলাইনে জমা রাখে |
| 3 | If the app will not open: use the paper job sheet from the van pack | অ্যাপ না খুললে: ভ্যান প্যাকের কাগজের জব শিট ব্যবহার করুন |
| 4 | Write the job reference given by the dispatcher by telephone | ডিসপ্যাচারের ফোনে দেওয়া জব রেফারেন্স লিখুন |
| 5 | Photograph before and after work **on the device camera**, and write the job reference on a slip in the first frame | কাজের আগে ও পরে **ফোনের ক্যামেরায়** ছবি তুলুন, প্রথম ছবিতে জব রেফারেন্স লেখা কাগজ রাখুন |
| 6 | Record parts used, by part number, on the stock sheet | ব্যবহৃত পার্টস পার্ট নম্বরসহ স্টক শিটে লিখুন |
| 7 | Customer signs the paper sheet; leave the customer copy | গ্রাহক কাগজে স্বাক্ষর দেবেন; গ্রাহক কপি রেখে আসুন |
| 8 | If money is collected, use the manual receipt book (`FB-07`) | টাকা নিলে ম্যানুয়াল রসিদ বই ব্যবহার করুন (`FB-07`) |
| 9 | Hand all sheets to the branch **at end of shift, same day** | শিফট শেষে **একই দিনে** সব শিট শাখায় জমা দিন |

#### `FB-10` — Manual dispatch *(হাতে ডিসপ্যাচ)*

| Trigger | Dispatch board unavailable, or routing/GPS down (`FB-08`, `FB-09`) |
|---|---|
| **Who** | Dispatcher, branch coordinator |
| **Steps** | Use the allocation board sheet: list open jobs by branch and priority from the last known board state or from the paper job cards · allocate by telephone to technicians by zone · record technician name, time allocated, and expected arrival · call the customer with the window · record actual completion by telephone at end of visit |
| **Tolerable** | 8 hours |
| **Reconciliation** | Jobs entered with **actual** times, not entry times — the SLA record must reflect what happened |

#### `FB-11` — Manual document production

| Trigger | Document generation or printing unavailable |
|---|---|
| **Who** | Branch coordinator, cashier |
| **Steps** | Use the pre-printed forms from the pack · for a tax invoice use the **reserved Mushak range only** (`DT-011`) · never hand-write a document that has a statutory format without using the reserved stationery |
| **Tolerable** | 8 hours |
| **Reconciliation** | Every reserved serial accounted for; **statutory sequence integrity verified by Finance before the next VAT filing** |

#### `FB-16` — Sign-in unavailable

| Trigger | Identity provider down (`OP-009`) |
|---|---|
| **Who** | All staff |
| **Steps** | Sessions already open continue — **do not sign out** · new work goes to `FB-01`/`FB-02` · **no shared or borrowed credentials, ever** (`OP-003` `mac.int.no_share_account`) · the branch manager authorises exceptions on their own signature on the paper form |
| **Tolerable** | 4 hours |
| **Reconciliation** | Work attributed to the staff member named on the form, not to whoever enters it |

#### `FB-19` — Contact centre fallback

| Trigger | Telephony (`INT-015`) or the agent console (`P10`) unavailable |
|---|---|
| **Who** | Contact centre supervisor and agents |
| **Steps** | Divert hotline 16743 to the nominated mobile numbers · agents log every call on the paper call sheet: time, number, customer name, reason, action promised · **promise nothing that requires the system** · escalate anything urgent to the branch by telephone |
| **Tolerable** | 8 hours |
| **Reconciliation** | Call sheets entered as contact records; any promise made is honoured or the customer is called back |

### 4.4 P0 integration fallbacks

**Thirteen P0 integrations** are enumerated in `05-03` §2.1–§2.7 (counted 2026-08-20). Each has a
procedure below. `05-03` §7's own register lists twelve and **omits `INT-013` email**; `FB-05`
closes that gap and the upstream correction is raised in the Category 17 audit.

| Code | Integration(s) | Trigger | Fallback in one line | Tolerable | Reconciliation |
|---|---|---|---|---|---|
| **FB-03** | `INT-010` SMS gateway (P0) | SMS not delivering | Automatic failover to `INT-011`; then WhatsApp; then push; **OTP-dependent sign-in escalates to `Sev1`** | 1 h for OTP, 4 h otherwise | Queued messages send on recovery; **duplicates suppressed by message key** |
| **FB-04** | `INT-012` WhatsApp (P0) | WhatsApp API failing | SMS, then email, then in-app inbox ([`NT-025`](../04_Notification_and_Messaging/NT-025_Notification_Failure_and_Fallback_Copy.md)) | 4 h | None — channel substitution only |
| **FB-05** | **`INT-013` Email (P0)** | Email send or inbound parsing failing | **Outbound:** invoices and notices held in a queue and re-sent on recovery; urgent corporate notices sent by SMS with a call from the account manager. **Inbound:** the `it@` and support mailboxes are monitored manually from a second client; tickets created by hand with the sender's address recorded | 4 h | Held queue drained with duplicate suppression; manually created tickets matched against the mailbox on recovery |
| **FB-06** | `INT-014` Push (P0) | Push not delivering | SMS for critical messages only (cost control); in-app inbox retains everything | 4 h | None |
| **FB-07** | `INT-001` bKash · `INT-002` Nagad · `INT-003` SSLCOMMERZ (P0) | One gateway failing → route to another. **All failing** → counter cash only | See the detailed procedure below | 4 h | Manual receipts matched to gateway settlement; **duplicate payment check mandatory** |
| **FB-08** | `INT-019` Google Maps (P0) | Geocoding or mapping unavailable | Cached geocodes; OSRM-only routing; **manual address entry with the area/thana recorded from the customer** | 8 h | Addresses re-geocoded on recovery; any that fail are queued for correction |
| **FB-09** | `INT-023` Traccar GPS (P0) | Position streaming down | Last known position on the board; technicians report status by telephone at each transition | 8 h | **Gaps are declared, never interpolated** ([`OP-010`](OP-010_Runbook_Data_Platform_and_Warehouse.md) `FB-03`) |
| **FB-12** | `INT-005` BEFTN (P0) | Disbursement file cannot be transmitted | Manual bank file submission through the bank's own portal, by the authorised signatories | 1 working day | Payment confirmations matched line by line before the next run |
| **FB-13** | `INT-006` Bank statement import (P0) | Statement not arriving | Manual statement download and upload | 2 working days | Auto-matching re-run; unmatched items worked manually |
| **FB-14** | `INT-034` Identity verification / KYC (P0) | Verification service down | **Manual document review by Compliance** against the seller/customer document standard; the record is flagged `manually verified` with the reviewer named | 2 working days | Re-verified automatically on recovery where the service permits; the manual flag is retained either way |
| **FB-15** | `INT-038` NBR e-VAT filing (P0) | Filing channel unavailable | Manual portal filing from the generated return, by the Tax Manager | **To the statutory deadline — this one does not slip** | Filing acknowledgement retained; system marked filed with the manual reference |

#### `FB-07` in detail — payments *(পেমেন্ট)*

| Step | Action | Bengali instruction |
|---:|---|---|
| 1 | Try the next available gateway before falling back to cash | নগদে যাওয়ার আগে পরবর্তী গেটওয়ে চেষ্টা করুন |
| 2 | If all gateways are down: **counter cash only** | সব গেটওয়ে বন্ধ থাকলে: **কেবল কাউন্টারে নগদ** |
| 3 | Write the manual money receipt (`DT-016` format) — serial, date, amount in figures **and words**, customer mobile, job reference or paper job card serial | ম্যানুয়াল মানি রসিদ লিখুন — সিরিয়াল, তারিখ, অঙ্কে **ও কথায়** টাকার পরিমাণ, গ্রাহকের মোবাইল, জব রেফারেন্স |
| 4 | Customer signs; give the customer the top copy | গ্রাহক স্বাক্ষর দেবেন; উপরের কপিটি গ্রাহককে দিন |
| 5 | Where a tax invoice is required, use the **reserved Mushak book** (`FB-11`) | কর চালান প্রয়োজন হলে **সংরক্ষিত মুশক বই** ব্যবহার করুন |
| 6 | Log every receipt in the fallback cash log, running total maintained | প্রতিটি রসিদ ফলব্যাক ক্যাশ লগে লিখুন, চলমান মোট রাখুন |
| 7 | Cash is counted, sealed and banked per `SP-019` **on the same day**, regardless of the outage | `SP-019` অনুযায়ী **একই দিনে** নগদ গুনে, সিল করে ব্যাংকে জমা দিন |
| 8 | **Do not** tell the customer a digital receipt will follow today | আজই ডিজিটাল রসিদ যাবে — এমন **বলবেন না** |
| 9 | On recovery, **check the gateway for a payment that also succeeded** before entering the cash receipt | সিস্টেম ফিরলে নগদ রসিদ তোলার আগে **গেটওয়েতে ওই পেমেন্ট সফল হয়েছিল কি না দেখুন** |

> **`PY-01`.** Step 9 is the one that prevents the classic double-charge: a gateway payment that
> succeeded at the provider but never reached the ERP, followed by a cash payment for the same job.
> Every fallback cash receipt is checked against settlement before it is posted, and any duplicate
> is refunded the same day with the customer told, unprompted.

### 4.5 Non-P0 fallbacks worth having

`IP-09` requires fallbacks for P0 integrations only. These four are P1/P2 but stop work often
enough to be worth writing down.

| Code | Integration | Fallback |
|---|---|---|
| `FB-20` | `INT-015` Telephony (P1) | See `FB-19` |
| `FB-21` | `INT-024`…`INT-026` Couriers (P2) | Book by the courier's own app or telephone; record the consignment number on the paper form; chain of custody signed manually ([`SP-009`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md)) |
| `FB-22` | `INT-041` Biometric attendance (P1) | Paper attendance register countersigned by the supervisor; entered within 2 working days for payroll |
| `FB-23` | `INT-043` LLM inference (P2) | Rule-based responses and direct human routing (`05-03` §7) |

> Listing these here does **not** make them P0. The audit distinction matters: `IP-09` coverage is
> measured against the thirteen P0 integrations in §4.4, not against the twenty-three procedures in
> this file.

### 4.6 Catch-up and reconciliation

The half of a fallback that gets forgotten, and the half auditors look at.

| Step | Action | Owner | Timing |
|---:|---|---|---|
| 1 | Service desk announces the fallback has **ended** (`FB-R7`) and catch-up has begun (`OP-003` `mac.int.catchup`) | Support Lead | On restoration |
| 2 | Collect every form, in serial order, per site | Branch coordinator | Same day |
| 3 | **Account for every serial**, including spoiled and unused — gaps are investigated before entry begins | Branch coordinator | Same day |
| 4 | Enter records in serial order, by the **named catch-up person only** (`FB-R4`) | Named per site | Within 24 h |
| 5 | Enter **actual** times and dates, not entry times | Catch-up person | — |
| 6 | For each payment: check the gateway settlement **before** posting (`PY-01`) | Cashier + Finance | Before posting |
| 7 | Send the deferred customer confirmations (`FB-R5` promised an SMS — it must now arrive) | System, once records exist | Within 24 h |
| 8 | Reconcile: forms issued = records created + spoiled + unused | Branch coordinator | On completion |
| 9 | Finance reconciles fallback cash to banking (`SP-019`) and to the manual receipt range | Finance | Within 2 working days |
| 10 | **Tax Manager verifies statutory sequence integrity** for any reserved Mushak serials used | Tax Manager | Before the next filing |
| 11 | Branch signs the fallback closure record; it goes to the incident record | Branch manager | Within 2 working days |
| 12 | Findings feed the post-incident review (`OP-016`) — including how the fallback itself performed | Support Lead | With the PIR |

**Closure record**

```
FALLBACK CLOSURE — Site: ________   Procedure(s): ______   Incident: ________
Started: ____  Ended: ____  Duration: ____      Announced by: ____________

FORMS         Issued from serial ____ to ____ = ____ forms
              Records created: ____   Spoiled: ____   Unused: ____   Gaps: ____
              Gaps explained: __________________________________________

MONEY         Manual receipts: ____ totalling BDT ________
              Banked same day (SP-019): ☐   Duplicate-payment check done (PY-01): ☐
              Duplicates found: ____   Refunded: ____

STATUTORY     Reserved Mushak serials used: ____ to ____
              Sequence integrity verified by Tax Manager: ☐   Date: ______

CUSTOMERS     Deferred confirmations sent: ☐    Complaints arising: ____

WHAT FAILED   (procedure gaps, stock-outs, wording that did not work)
              ____________________________________________________

Branch manager ______________  Finance ______________  Support Lead ______________
```

### 4.7 Testing the fallbacks

`NFR-050` requires the fallback to be **tested**, not merely documented. A fallback nobody has
practised is discovered to be wrong at the worst moment.

| Test | Frequency | Scope | Pass criteria |
|---|---|---|---|
| **Fallback pack check** | Monthly | Every site | All 13 items present, in date, accessible without a manager's key |
| **Counter drill** | Quarterly | 5 branches, rotated | A full walk-in served on paper in ≤ 6 minutes, and entered correctly the next day |
| **Payment drill** | Quarterly | 3 branches | Manual receipt written, banked, and the `PY-01` duplicate check performed |
| **Field drill** | Quarterly | One technician cohort | A full job recorded on paper and reconciled |
| **Full fallback exercise** | **Twice yearly**, inside the DR exercise (`OP-012` §11) | All sites, 2 hours | ≥ 90% of sites trading on paper within 15 minutes of the announcement |
| **Statutory drill** | Annually | Finance | A manual Mushak invoice issued from the reserved range and reconciled without a sequence break |

**`TF-01`.** Drills are run **during trading hours with real customers**, not after closing. A
fallback that only works in an empty branch has not been tested.

### 4.8 Open decisions

| # | Decision required | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|
| **OP-014-OI-01** | **Reserved Mushak serial ranges must be obtained and allocated per site** before W1 go-live | Tax Manager + CFO | W1 | `FB-11` and `FB-07` cannot lawfully produce a tax invoice during an outage |
| **OP-014-OI-02** | Fund and distribute the fallback pack to 51+ sites (printing, serial-controlled stationery, monthly replenishment) | Operations Director | W1 | The procedures exist and the forms do not |
| **OP-014-OI-03** | `05-03` §7 must be corrected: `INT-013` email has no fallback, and the P0 count is 13, not 12 | Enterprise Architecture | W1 | `IP-09` compliance is claimed against the wrong denominator |
| **OP-014-OI-04** | Confirm who is the "named catch-up person" per site and how they are covered on leave | Branch Operations Manager | W1 | `FB-R4` is unassigned and entry duplicates appear |
| **OP-014-OI-05** | Bengali counterpart must be **authored and G4-reviewed before W1**, not after — it is the operational version | Localisation Lead | W1 | The file cannot be used by the people it is written for |
| **OP-014-OI-06** | Confirm whether cash-only trading during an outage requires any additional insurance or security measure at branches | CFO + Operations | W2 | Sites hold materially more cash than usual with no assessment |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-03` §7 and §2 | The P0 integration set this file must cover |
| `DT-011`, `DT-016` | Statutory invoice and money-receipt formats used in fallback |
| `SP-007`, `SP-008`, `SP-009`, `SP-019` | The normal processes each fallback replaces |
| `OP-013` §4.8 | Who may invoke a fallback |
| `OP-004`, `OP-005` | How the invocation is announced |
| `OP-003` | The macros that tell users what to do (`mac.int.fallback`, `mac.int.catchup`) |
| `OP-012` | The disaster case, where every fallback runs at once |
| `OP-016` | Where fallback performance is reviewed |
| `NT-025` | Notification channel fallbacks referenced by `FB-03`…`FB-06` |
| [`BN-003`](../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md), [`BN-018`](../11_Localisation_Bengali/BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | Bengali terminology and in-context review of the operational version |

**Depended on by:** every `NT` template library (26 files cite `OP-014`) · every branch and field
SOP · `OP-007`…`OP-012` §7 · [`TS-013`](../13_Test_and_Acceptance_Content/TS-013_Regression_Pack_and_Smoke_Test_Checklist.md) · [`TS-014`](../13_Test_and_Acceptance_Content/TS-014_Performance_and_Load_Test_Scenario_Pack.md) · [`LG-021`](../10_Legal_Policy_and_Compliance/LG-021_ISMS_Policy_Set.md) · [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md) · [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md).

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly, and after every invocation |
| Trigger for out-of-cycle review | A new P0 integration · a failed drill · any invocation where the procedure proved wrong · a change to `DT-011`/`DT-016` · a change to the P0 set in `05-03` |
| Owner | Operations, with Platform Engineering for the integration procedures |
| Distribution | **Printed and physically held** at every site in Bengali; the English version is the governance copy |
| Version control | Each printed copy carries the version and date; superseded copies are **removed from site**, not left in the folder |
| Evidence retained | Closure records, drill results and reconciliations — 7 years (`NFR-088`) |

---

## Open Items

1. **OP-014-OI-01** — reserved Mushak ranges not obtained (statutory blocker).
2. **OP-014-OI-02** — fallback pack unfunded and undistributed.
3. **OP-014-OI-03** — `05-03` §7 register incomplete and miscounted.
4. **OP-014-OI-04** — catch-up person unassigned per site.
5. **OP-014-OI-05** — Bengali counterpart outstanding; it is the operational version.
6. **OP-014-OI-06** — cash-handling risk during payment outages unassessed.
7. Procedure codes `FB-17` and `FB-18` are **deliberately unallocated**, reserved for invoicing and
   warehouse fallbacks that [`SP-018`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md)/[`SP-020`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) may require; recorded so the numbering is not read as
   a gap.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in `CG-008`.

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md); Bengali terms follow `BN-003`
- [x] All internal links resolve
- [x] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) applied — printed forms legible, instructions in short sentences, no reliance on colour
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **open, OI-05; this file is not usable until it is**
- [ ] Named approver recorded — Operations Director; **Tax Manager sign-off additionally required for `FB-11`/`FB-15`**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open decisions pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ●, G4 ● (bilingual). **`FB-11` and `FB-15` additionally
require G6 statutory verification** of the reserved-range procedure against the VAT and SD Act 2012
— a Class A intrusion into a Class C file, declared here and logged in `RF-006`.

---

*`OP-014` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
