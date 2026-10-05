#!/usr/bin/env python3
"""apply-bn-counterparts — PP0-M02-T01.

Closes the 110 counterpart-pending UI-copy keys by inserting the reviewed
Bengali string into the source pack row immediately AFTER the English cell
(non-destructive: hazard markers, guidance sentences and CTA columns that
currently occupy that position shift right and survive).

The extractor (tooling/scripts/extract-ui-copy.py) marks a row inline
bilingual exactly when the cell after English carries Bengali script, so an
insert-after-English is the minimal correct transform.

Safety: every application verifies the English cell matches the expected
string; any mismatch or missing row is reported and fails the run. Idempotent:
rows already carrying Bengali script are skipped.

Exit: 0 all applied / 1 anything missing or mismatched.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONTENT = REPO.parent / "project_content" / "03_UI_Copy_and_Microcopy"

BENGALI = re.compile(r"[\u0980-\u09FF]")

# (pack, key, expected English, Bengali counterpart) — 110 entries, reviewed.
MAP: list[tuple[str, str, str, str]] = [
    # UI-001
    ("UI-001", "common.error.system.string_missing",
     "This text could not be loaded. Refresh the page. If it happens again, quote reference {ref}.",
     "এই লেখাটি লোড করা যায়নি। পেজটি রিফ্রেশ করুন। বারবার ঘটলে রেফারেন্স {ref} উল্লেখ করে জানান।"),
    # UI-002 — module keys carry the module's Bengali nav label
    ("UI-002", "fix.service.order", "`M01`", "সার্ভিস অর্ডার"),
    ("UI-002", "fix.dispatch.job", "`M02`", "ফিল্ড সার্ভিস ও ডিসপ্যাচ"),
    ("UI-002", "fix.work.order", "`M31`", "ওয়ার্কশপ মেরামত"),
    ("UI-002", "fix.asset", "`M17`", "ডিভাইস রেজিস্ট্রি"),
    ("UI-002", "fix.part", "`M15`", "স্পেয়ার পার্টস ও ইনভেন্টরি"),
    ("UI-002", "fix.contract", "`M08`", "চুক্তি ব্যবস্থাপনা"),
    ("UI-002", "fix.warranty.register", "`M09`", "ওয়ারেন্টি ও ক্লেইম"),
    ("UI-002", "common.nav.chrome.product", "1000FiX", "1000FiX সার্ভিসেস"),
    ("UI-002", "common.nav.error.no_access",
     "This workspace is not part of your role. Ask your manager if you need access to {workspace}.",
     "এই ওয়ার্কস্পেসটি আপনার ভূমিকার অন্তর্ভুক্ত নয়। {workspace} দরকার হলে আপনার ম্যানেজারের সঙ্গে যোগাযোগ করুন।"),
    ("UI-002", "common.nav.error.surface_down",
     "{surface} is unavailable. Other workspaces are working normally. We are restoring it.",
     "{surface} এখন ব্যবহারযোগ্য নয়। অন্য সব ওয়ার্কস্পেস স্বাভাবিক চলছে। আমরা দ্রুত পুনরুদ্ধার করছি।"),
    # UI-003
    ("UI-003", "common.error.field.required", "Enter {field}.", "{field} লিখুন।"),
    ("UI-003", "common.error.field.mobile_format",
     "Enter the mobile number as 11 digits starting 01.",
     "মোবাইল নম্বরটি 01 দিয়ে শুরু 11 সংখ্যায় লিখুন।"),
    ("UI-003", "common.error.field.imei_format",
     "Enter the IMEI as 15 digits with no spaces.",
     "IMEI হবে 15 সংখ্যা, কোনো ফাঁকা স্থান ছাড়া।"),
    ("UI-003", "common.error.field.bin_format", "Enter the BIN as 13 digits.",
     "BIN হবে 13 সংখ্যা।"),
    ("UI-003", "common.error.field.date_format", "Enter the date as DD/MM/YYYY.",
     "তারিখ লিখুন DD/MM/YYYY আকারে।"),
    ("UI-003", "common.error.field.date_future", "The purchase date cannot be in the future.",
     "কেনার তারিখ ভবিষ্যতে হতে পারে না।"),
    ("UI-003", "common.error.field.amount_precision",
     "Enter the amount with up to two decimal places.",
     "পরিমাণ দশমিকের পরে সর্বোচ্চ দুই ঘরে লিখুন।"),
    ("UI-003", "common.error.field.max_length",
     "Shorten this to {max} characters. You have {current}.",
     "এটি সংক্ষিপ্ত করে {max} অক্ষরের মধ্যে আনুন। বর্তমানে {current} অক্ষর আছে।"),
    # UI-004 — validation library (24)
    ("UI-004", "common.error.srm.device_required",
     "A service order needs an identified device. Search for the device, or register it now.",
     "সার্ভিস অর্ডারের জন্য শনাক্ত করা একটি ডিভাইস দরকার। ডিভাইসটি খুঁজুন, অথবা এখনই নিবন্ধন করুন।"),
    ("UI-004", "common.error.srm.warranty_inactive",
     "This device is not under warranty on {date}. Its warranty ended {expiry}. Create a paid repair instead.",
     "এই ডিভাইসের {date} তারিখে ওয়ারেন্টি নেই। ওয়ারেন্টি শেষ হয়েছে {expiry}। পেইড মেরামত তৈরি করুন।"),
    ("UI-004", "common.error.srm.not_on_contract",
     "This device is not on {contract}. Add it to the contract, or create a paid repair.",
     "এই ডিভাইসটি {contract}-এর অন্তর্ভুক্ত নয়। চুক্তিতে যোগ করুন, অথবা পেইড মেরামত নিন।"),
    ("UI-004", "common.error.srm.qc_not_passed",
     "This order cannot be completed. The quality checklist is not recorded as passed. Complete the checklist first.",
     "এই অর্ডার সম্পন্ন করা যাবে না। কোয়ালিটি চেকলিস্ট এখনো পাস হিসেবে নথিভুক্ত হয়নি। আগে চেকলিস্ট সম্পন্ন করুন।"),
    ("UI-004", "common.error.srm.invoice_before_complete",
     "An invoice cannot be raised for an order that is not completed. Complete the order first.",
     "সম্পন্ন না হওয়া অর্ডারের চালান ইস্যু করা যায় না। আগে অর্ডারটি সম্পন্ন করুন।"),
    ("UI-004", "common.error.srm.estimate_approval_5k",
     "Work above BDT 5,000 needs the customer's approval first. Send the estimate, then start work when it is approved.",
     "৫,০০০ টাকার বেশি কাজের জন্য আগে গ্রাহকের অনুমোদন দরকার। এস্টিমেট পাঠান; অনুমোদন পেলে কাজ শুরু করুন।"),
    ("UI-004", "common.error.srm.estimate_approval_25k",
     "Work above BDT 25,000 needs the customer's approval and the branch manager's approval. Send it to {branch_manager}.",
     "২৫,০০০ টাকার বেশি কাজের জন্য গ্রাহক ও ব্রাঞ্চ ম্যানেজার উভয়ের অনুমোদন দরকার। {branch_manager}-কে পাঠান।"),
    ("UI-004", "common.error.srm.tech_not_certified",
     "{technician} is not certified for {brand} warranty work. Their certification expired on {expiry}. Assign a certified technician, or ask the Quality Manager to renew it.",
     "{technician} এই {brand} ওয়ারেন্টি কাজের জন্য সার্টিফাইড নন; সার্টিফিকেটের মেয়াদ শেষ {expiry}। সার্টিফাইড কারিগর নির্ধারণ করুন, বা কোয়ালিটি ম্যানেজারকে নবায়নের অনুরোধ করুন।"),
    ("UI-004", "common.error.srm.parts_unapproved",
     "Parts cannot be issued against an unapproved paid repair. Approve the estimate first, then issue the parts.",
     "অনুমোদনহীন পেইড মেরামতে পার্টস ইস্যু করা যায় না। আগে এস্টিমেট অনুমোদন করুন, তারপর পার্টস দিন।"),
    ("UI-004", "common.error.srm.rework_flagged",
     "This is the second order for {device} with the same fault within 30 days. It has been linked to {original} as rework.",
     "{device} ডিভাইসের একই ত্রুটিতে 30 দিনের মধ্যে এটি দ্বিতীয় অর্ডার। এটি {original}-এর রিওয়ার্ক হিসেবে যুক্ত হয়েছে।"),
    ("UI-004", "common.error.srm.priority_upgraded",
     "{customer} is a {tier} member, so this order has been set to priority 1.",
     "{customer} একজন {tier} সদস্য, তাই এই অর্ডারটি অগ্রাধিকার ১-এ সেট করা হয়েছে।"),
    ("UI-004", "common.error.approval.over_limit",
     "You can approve up to {limit}. This is {amount}. Send it to {approver} for approval.",
     "আপনি সর্বোচ্চ {limit} পর্যন্ত অনুমোদন করতে পারেন; এটি {amount}। অনুমোদনের জন্য {approver}-কে পাঠান।"),
    ("UI-004", "common.error.approval.self",
     "You cannot approve your own {object}. Send it to {approver}.",
     "নিজের {object} নিজে অনুমোদন করতে পারবেন না। {approver}-কে পাঠান।"),
    ("UI-004", "common.error.approval.override_available",
     "This is blocked by {rule}. {role} can authorise an exception. Record a reason to request it.",
     "এটি {rule} কর্তৃক আটকানো হয়েছে। {role} ব্যতিক্রম অনুমোদন করতে পারেন। অনুরোধ করতে কারণ লিখুন।"),
    ("UI-004", "common.error.approval.reason_required",
     "Enter a reason for this override. It is recorded against the transaction.",
     "এই ব্যতিক্রমের কারণ লিখুন। এটি লেনদেনের সঙ্গে নথিভুক্ত থাকবে।"),
    ("UI-004", "common.error.stock.unavailable",
     "{part} is not in stock at {location}. It is available at {alt_location}. Request a transfer, or order it.",
     "{location}-এ {part} স্টকে নেই; {alt_location}-এ আছে। ট্রান্সফারের অনুরোধ করুন, অথবা অর্ডার করুন।"),
    ("UI-004", "common.error.stock.incompatible",
     "{part} does not fit {model}. Compatible parts: {alternatives}.",
     "{part} এই {model}-এর সঙ্গে খাপ খায় না। সামঞ্জস্যপূর্ণ পার্টস: {alternatives}।"),
    ("UI-004", "common.error.stock.negative",
     "Issuing {qty} would take {location} below zero. Count the location, or record a receipt first.",
     "{qty} ইস্যু করলে {location} ঋণাত্মক হয়ে যাবে। লোকেশন গুনে নিন, বা আগে রিসিট নথিভুক্ত করুন।"),
    ("UI-004", "common.error.stock.hazard_ack",
     "{part} is a {hazard_class} item. Confirm you have read the handling instructions before issuing it.",
     "{part} একটি {hazard_class} আইটেম। ইস্যু করার আগে হ্যান্ডলিং নির্দেশনা পড়েছেন বলে নিশ্চিত করুন।"),
    ("UI-004", "common.error.fin.period_closed",
     "{period} is closed. Post this to the current period, or ask Finance to reopen {period}.",
     "{period} বন্ধ। বর্তমান পিরিয়ডে পোস্ট করুন, বা ফাইন্যান্সকে {period} পুনরায় খুলতে বলুন।"),
    ("UI-004", "common.error.fin.no_tax_class",
     "{item} has no tax class, so a compliant invoice cannot be issued. Ask Finance to set the tax class.",
     "{item}-এর কোনো ট্যাক্স ক্লাস নেই, তাই সামঞ্জস্যপূর্ণ চালান ইস্যু করা যাবে না। ফাইন্যান্সকে ট্যাক্স ক্লাস সেট করতে বলুন।"),
    ("UI-004", "common.error.fin.bin_required",
     "A VAT invoice to a business needs the buyer's BIN. Add the BIN to {customer}, or issue to an individual.",
     "ব্যবসায়িক প্রতিষ্ঠানের ভ্যাট চালানে ক্রেতার BIN দরকার। {customer}-এ BIN যোগ করুন, বা ব্যক্তি হিসেবে ইস্যু করুন।"),
    ("UI-004", "common.error.fin.tax_unverified",
     "This tax code is not yet verified for {fiscal_year}, so it cannot be used. Finance is completing verification.",
     "এই ট্যাক্স কোডটি {fiscal_year}-এর জন্য এখনো যাচাই হয়নি, তাই ব্যবহার করা যাবে না। ফাইন্যান্স যাচাই সম্পন্ন করছে।"),
    ("UI-004", "common.error.fin.dimension_required",
     "{account} needs a {dimension}. Select one.",
     "{account}-এর জন্য একটি {dimension} দরকার। একটি নির্বাচন করুন।"),
    # UI-005 — system/session messages (4)
    ("UI-005", "common.system.maintenance",
     "1000FiX is unavailable until {time} for planned maintenance. Call 16743 for urgent service.",
     "পরিকল্পিত রক্ষণাবেক্ষণের জন্য {time} পর্যন্ত 1000FiX ব্যবহারযোগ্য নয়। জরুরি সেবার জন্য 16743 নম্বরে কল করুন।"),
    ("UI-005", "common.system.degraded",
     "{feature} is not working right now. {fallback} Everything else is working normally.",
     "{feature} এখন কাজ করছে না। {fallback} বাকি সবকিছু স্বাভাবিক চলছে।"),
    ("UI-005", "common.system.rate_limited",
     "Too many requests. Wait {seconds} seconds and try again.",
     "অনেক বেশি অনুরোধ হয়েছে। {seconds} সেকেন্ড অপেক্ষা করে আবার চেষ্টা করুন।"),
    ("UI-005", "common.system.version_old",
     "Update the app to continue. This version is no longer supported.",
     "চালিয়ে যেতে অ্যাপটি আপডেট করুন। এই সংস্করণটি আর সমর্থিত নয়।"),
    # UI-006 — empty/first-run states (16)
    ("UI-006", "p01.empty.orders", "No services yet", "এখনো কোনো সার্ভিস নেই"),
    ("UI-006", "p01.empty.devices", "No devices registered", "কোনো ডিভাইস নিবন্ধিত নেই"),
    ("UI-006", "p02.empty.jobs", "No jobs assigned", "কোনো কাজ নির্ধারিত নেই"),
    ("UI-006", "ws.empty.dispatch_queue", "No unassigned jobs", "কোনো অনির্ধারিত কাজ নেই"),
    ("UI-006", "ws.empty.workshop", "No jobs on the bench", "বেঞ্চে কোনো কাজ নেই"),
    ("UI-006", "ws.empty.invoices", "No invoices in this period", "এই সময়ে কোনো চালান নেই"),
    ("UI-006", "common.empty.no_results.search", "No matches for \"{query}\"",
     "“{query}”-এর জন্য কোনো মিল নেই"),
    ("UI-006", "common.empty.no_results.filter", "No records match these filters",
     "এই ফিল্টারে কোনো রেকর্ড মেলে না"),
    ("UI-006", "common.empty.no_results.date", "Nothing in {period}", "{period}-এ কিছু নেই"),
    ("UI-006", "common.empty.not_configured.master_data", "{dataset} is not set up yet",
     "{dataset} এখনো সেটআপ করা হয়নি"),
    ("UI-006", "common.empty.not_configured.price_list", "No price list for {segment}",
     "{segment}-এর জন্য কোনো প্রাইস লিস্ট নেই"),
    ("UI-006", "common.empty.not_configured.zone", "This area is not covered yet",
     "এই এলাকা এখনো কভার করা হয়নি"),
    ("UI-006", "p01.firstrun.welcome", "Welcome to 1000FiX", "1000FiX-এ স্বাগতম"),
    ("UI-006", "p02.firstrun.welcome", "Your jobs, offline", "আপনার কাজ, অফলাইনেও"),
    ("UI-006", "ws.firstrun.welcome", "Choose your workspace", "আপনার ওয়ার্কস্পেস বেছে নিন"),
    ("UI-006", "p09.firstrun.welcome", "Today's manifest", "আজকের ম্যানিফেস্ট"),
    # UI-007 — confirmations (14)
    ("UI-007", "common.confirm.order.cancel", "Cancel this service order",
     "এই সার্ভিস অর্ডারটি বাতিল করুন"),
    ("UI-007", "common.confirm.job.reassign", "Reassign this job to {technician}",
     "এই কাজটি {technician}-এর কাছে পুনর্নির্ধারণ করুন"),
    ("UI-007", "common.confirm.order.close_no_qc", "This order has no recorded quality check",
     "এই অর্ডারে কোনো কোয়ালিটি চেক নথিভুক্ত হয়নি"),
    ("UI-007", "common.confirm.order.ber", "Mark this device beyond economic repair",
     "এই ডিভাইসটি মেরামতের অযোগ্য (BER) হিসেবে চিহ্নিত করুন"),
    ("UI-007", "common.confirm.fin.post", "Post invoice {reference}",
     "চালান {reference} পোস্ট করুন"),
    ("UI-007", "common.confirm.fin.void", "Void invoice {reference}",
     "চালান {reference} বাতিল করুন"),
    ("UI-007", "common.confirm.fin.refund", "Refund {amount} to {customer}",
     "{customer}-কে {amount} ফেরত দিন"),
    ("UI-007", "common.confirm.fin.writeoff", "Write off {amount}",
     "{amount} রাইট-অফ করুন"),
    ("UI-007", "common.confirm.override.request", "Request an exception to {rule}",
     "{rule}-এর ব্যতিক্রমের অনুরোধ করুন"),
    ("UI-007", "common.confirm.override.authorise", "Authorise this exception",
     "এই ব্যতিক্রমটি অনুমোদন করুন"),
    ("UI-007", "common.confirm.data.archive", "Archive {object}",
     "{object} আর্কাইভ করুন"),
    ("UI-007", "common.confirm.data.bulk", "{action} {count} records",
     "{count}টি রেকর্ডে {action} প্রয়োগ করুন"),
    ("UI-007", "common.confirm.data.merge", "Merge {source} into {target}",
     "{source}-কে {target}-এর সঙ্গে একত্র করুন"),
    ("UI-007", "common.confirm.data.revoke", "Remove {user} from {role}",
     "{user}-কে {role} থেকে সরিয়ে দিন"),
    # UI-010 — accessibility live regions (7)
    ("UI-010", "common.a11y.live.saved", "{object} saved", "{object} সংরক্ষিত হয়েছে"),
    ("UI-010", "common.a11y.live.invalid", "{count} fields need attention",
     "{count}টি ফিল্ডে মনোযোগ দরকার"),
    ("UI-010", "common.a11y.live.status", "{object} is now {status}",
     "{object} এখন {status}"),
    ("UI-010", "common.a11y.live.results", "{count} results", "{count}টি ফলাফল"),
    ("UI-010", "common.a11y.live.sync", "{sync_state}",
     "সিঙ্ক অবস্থা: {sync_state}"),
    ("UI-010", "common.a11y.live.session", "Session ends in {minutes} minutes",
     "সেশন শেষ হবে {minutes} মিনিটে"),
    ("UI-010", "common.a11y.sr.file", "{format}, {size}",
     "{format} ফরম্যাট, আকার {size}"),
    # UI-013 — list patterns (4)
    ("UI-013", "p03.list.bulk", "{action} {n}", "{action} — {n}টি"),
    ("UI-013", "p03.error.bulk_limit",
     "Bulk actions apply to at most {max} records. Narrow your filter.",
     "বাল্ক অ্যাকশন সর্বোচ্চ {max}টি রেকর্ডে প্রযোজ্য। ফিল্টার সংকুচিত করুন।"),
    ("UI-013", "p03.error.export_size",
     "This export has {rows} rows. Schedule it instead — we will email it when ready.",
     "এই এক্সপোর্টে {rows}টি সারি আছে। এটি শিডিউল করুন — প্রস্তুত হলে ইমেইলে পাঠানো হবে।"),
    ("UI-013", "p03.error.stale",
     "{user} changed this while you were editing. Review their change before saving.",
     "আপনি সম্পাদনার সময় {user} এটি পরিবর্তন করেছেন। সংরক্ষণের আগে সেই পরিবর্তনটি দেখে নিন।"),
    # UI-023 — intake workspace (3)
    ("UI-023", "ws.intake.error.device_required",
     "An intake needs an identified device. Search, or register a new one.",
     "ইনটেকের জন্য শনাক্ত করা একটি ডিভাইস দরকার। খুঁজুন, অথবা নতুন একটি নিবন্ধন করুন।"),
    ("UI-023", "ws.intake.error.accessories",
     "Record the accessories, or confirm there are none. This is the custody record.",
     "সঙ্গে থাকা জিনিসপত্র নথিভুক্ত করুন, বা কিছু নেই বলে নিশ্চিত করুন। এটিই কাস্টডি রেকর্ড।"),
    ("UI-023", "ws.intake.error.duplicate",
     "{device} already has an open order {ref}. Continue anyway, or open the existing one.",
     "{device}-এর ইতিমধ্যে একটি খোলা অর্ডার {ref} আছে। তবুও চালিয়ে যাবেন, নাকি আগেরটি খুলবেন?"),
    # UI-024 — dispatch workspace (3)
    ("UI-024", "ws.dispatch.error.uncertified",
     "{technician} is not certified for {brand}. Assign someone certified, or ask Quality to renew.",
     "{technician} {brand}-এর জন্য সার্টিফাইড নন। সার্টিফাইড কাউকে দিন, বা কোয়ালিটিকে নবায়নের অনুরোধ করুন।"),
    ("UI-024", "ws.dispatch.error.zone",
     "{technician} does not cover {zone}. Assign anyway with a reason, or choose another.",
     "{technician} {zone} এলাকা কভার করেন না। কারণসহ তবুও নির্ধারণ করুন, বা অন্য কাউকে বেছে নিন।"),
    ("UI-024", "ws.dispatch.error.overload",
     "{technician} already has {count} jobs today. Assign anyway?",
     "{technician}-এর আজ ইতিমধ্যে {count}টি কাজ আছে। তবুও নির্ধারণ করবেন?"),
    # UI-025 — branch workspace (2)
    ("UI-025", "ws.branch.error.cash_variance",
     "Counted {counted}, expected {expected}. Record a reason before closing.",
     "গোনা হয়েছে {counted}, প্রত্যাশিত {expected}। বন্ধ করার আগে কারণ লিখুন।"),
    ("UI-025", "ws.branch.error.uncollected",
     "{count} devices are past {days} days. Contact the customers before any disposal step.",
     "{count}টি ডিভাইস {days} দিন পার হয়ে গেছে। যেকোনো নিষ্পত্তির ধাপের আগে গ্রাহকদের যোগাযোগ করুন।"),
    # UI-026 — workshop workspace (2)
    ("UI-026", "ws.workshop.error.qc",
     "This cannot be completed. The quality checklist is not recorded as passed.",
     "এটি সম্পন্ন করা যাবে না। কোয়ালিটি চেকলিস্ট এখনো পাস হিসেবে নথিভুক্ত হয়নি।"),
    ("UI-026", "ws.workshop.error.over_time",
     "This job is {pct}% over the standard time of {standard} minutes. Record why.",
     "এই কাজটি স্ট্যান্ডার্ড {standard} মিনিটের চেয়ে {pct}% বেশি সময় নিচ্ছে। কারণ লিখুন।"),
    # UI-027 — inventory workspace (2)
    ("UI-027", "ws.inventory.error.negative",
     "Issuing {qty} would take {location} below zero. Count it, or record a receipt first.",
     "{qty} ইস্যু করলে {location} ঋণাত্মক হয়ে যাবে। গুনে নিন, বা আগে রিসিট নথিভুক্ত করুন।"),
    ("UI-027", "ws.inventory.error.location",
     "{part} is not held at {location}. It is at {alt_location}.",
     "{part} এই {location}-এ নেই; আছে {alt_location}-এ।"),
    # UI-029 — finance workspace (4)
    ("UI-029", "ws.finance.error.period",
     "{period} is closed. Post to the current period, or ask Finance to reopen it.",
     "{period} বন্ধ। বর্তমান পিরিয়ডে পোস্ট করুন, বা ফাইন্যান্সকে পুনরায় খুলতে বলুন।"),
    ("UI-029", "ws.finance.error.tax_class",
     "{item} has no tax class, so a compliant invoice cannot be issued.",
     "{item}-এর কোনো ট্যাক্স ক্লাস নেই, তাই সামঞ্জস্যপূর্ণ চালান ইস্যু করা যাবে না।"),
    ("UI-029", "ws.finance.error.bin",
     "A VAT invoice to a business needs the buyer BIN. Add it to {customer}.",
     "ব্যবসার ভ্যাট চালানে ক্রেতার BIN দরকার। {customer}-এ যোগ করুন।"),
    ("UI-029", "ws.finance.error.not_complete",
     "An invoice cannot be raised for an order that is not completed.",
     "সম্পন্ন না হওয়া অর্ডারের চালান ইস্যু করা যায় না।"),
    # UI-036 — RBAC/system admin (3)
    ("UI-036", "ws.system.error.sod",
     "{role_a} and {role_b} cannot be held together. CFO or CTO can authorise a time-boxed exception.",
     "{role_a} ও {role_b} একসঙ্গে রাখা যায় না। CFO বা CTO সময়সীমাযুক্ত ব্যতিক্রম অনুমোদন করতে পারেন।"),
    ("UI-036", "ws.system.error.role_unregistered",
     "{role} is not registered in the role matrix and cannot be granted.",
     "{role} রোল ম্যাট্রিক্সে নিবন্ধিত নয়, তাই প্রদান করা যাবে না।"),
    ("UI-036", "ws.system.error.leaver",
     "{user} left on {date} but still has access. Revoke it.",
     "{user} {date} তারিখে চলে গেছেন কিন্তু এখনো অ্যাক্সেস আছে। তা বাতিল করুন।"),
    # UI-041 — bulk flows (3)
    ("UI-041", "flow.bulk.error.limit",
     "Bulk actions apply to at most {max}. Narrow your filter.",
     "বাল্ক অ্যাকশন সর্বোচ্চ {max}-এ প্রযোজ্য। ফিল্টার সংকুচিত করুন।"),
    ("UI-041", "flow.bulk.error.mixed",
     "{n} of the selected records cannot have {action} applied. Continue with the other {ok}?",
     "নির্বাচিত {n}টি রেকর্ডে {action} প্রয়োগ করা যাবে না। বাকি {ok}টির সঙ্গে চালিয়ে যাবেন?"),
    ("UI-041", "flow.bulk.error.none",
     "Select at least one record.",
     "অন্তত একটি রেকর্ড নির্বাচন করুন।"),
]


def pack_files() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^id:\s*(UI-\d+)", text, re.M)
        if m:
            out.setdefault(m.group(1), path)
    return out


def main() -> int:
    if len(MAP) != 110:
        print(f"apply-bn-counterparts: MAP has {len(MAP)} entries, expected 110")
        return 1
    for _, key, _, bn in MAP:
        if not BENGALI.search(bn):
            print(f"apply-bn-counterparts: {key} counterpart carries no Bengali script "
                  "- the extractor would leave it pending")
            return 1
    files = pack_files()
    applied, skipped, failures = 0, 0, []
    for pack, key, en, bn in MAP:
        path = files.get(pack)
        if path is None:
            failures.append(f"{pack}: pack file not found")
            continue
        lines = path.read_text(encoding="utf-8").splitlines(keepends=False)
        hit = False
        for i, line in enumerate(lines):
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            key_idx = next((j for j, c in enumerate(cells)
                            if c == f"`{key}`" or c == key), None)
            if key_idx is None:
                continue
            rest = cells[key_idx + 1:]
            if not rest:
                continue
            if rest[0] != en:
                failures.append(f"{pack}/{key}: en mismatch {rest[0]!r} != {en!r}")
                hit = True
                break
            if len(rest) > 1 and BENGALI.search(rest[1]):
                skipped += 1  # already bilingual — idempotent rerun
                hit = True
                break
            new_cells = cells[:key_idx + 1] + [en, bn] + rest[1:]
            lines[i] = "| " + " | ".join(new_cells) + " |"
            hit = True
            applied += 1
            break
        if hit:
            path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        else:
            failures.append(f"{pack}/{key}: row not found")
    print(f"apply-bn-counterparts: applied={applied} skipped(already)={skipped} "
          f"failures={len(failures)}")
    for f in failures:
        print("  FAIL", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
