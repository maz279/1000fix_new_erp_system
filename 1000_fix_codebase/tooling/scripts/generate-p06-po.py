#!/usr/bin/env python3
"""One-shot: generate the twelve P06 module bn_BD.po files (100%).

Same discipline as generate-platform-po.py: authored once here, idempotent,
FF-25 enforces 100% after this run.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"

T: dict[str, str] = {
    # shared
    "Company": "কোম্পানি", "Operating Unit": "পরিচালন ইউনিট",
    "Description": "বিবরণ", "Currency": "মুদ্রা", "Branch": "শাখা",
    "Vendor": "ভেন্ডর", "Employee": "কর্মী", "Product": "পণ্য",
    "Amount": "পরিমাণ", "Total": "মোট", "State": "অবস্থা",
    "Quantity": "পরিমাণ", "Unit Price": "একক মূল্য", "Line Total": "লাইন মোট",
    "Lines": "লাইনসমূহ", "Active": "সক্রিয়", "Date": "তারিখ",
    "Status": "অবস্থা", "Notes": "নোট", "Reference": "রেফারেন্স",
    "Priority": "প্রাধিকার", "Sequence": "ক্রম", "Name": "নাম",
    "Code": "কোড", "Rate (VAT-exclusive)": "হার (ভ্যাট-বাদে)",
    "Customer": "গ্রাহক", "Invoice Date": "চালানের তারিখ",
    "Taxable Value": "করযোগ্য মূল্য", "VAT": "ভ্যাট", "Total Payable": "মোট প্রদেয়",
    "Valid From": "হইতে বৈধ", "Valid To": "পর্যন্ত বৈধ",
    # cd_gl_ext
    "Branches": "শাখাসমূহ", "Journal Posting Dimension": "জার্নাল পোস্টিং মাত্রা",
    "Period": "পর্যায়",
    "Journal Item": "জার্নাল আইটেম", "Cost Centre": "খরচ কেন্দ্র",
    "Period Close Checklist": "পর্যায় সমাপ্তি চেকলিস্ট",
    "Period End": "পর্যায় সমাপ্তি", "Close Steps": "সমাপ্তি ধাপসমূহ",
    "Suspense Opening": "সাসপেন্স শুরু", "Suspense Closing": "সাসপেন্স শেষ",
    "Close Duration (days)": "সমাপ্তি সময় (দিন)",
    "Period Close Step": "সমাপ্তি ধাপ", "Step": "ধাপ",
    "Owning Role": "দায়িত্বপ্রাপ্ত ভূমিকা", "Target Day": "লক্ষ্য দিন",
    "Evidence Reference": "প্রমাণের রেফারেন্স",
    "Fixed Asset Seam (M49 interface)": "স্থায়ী সম্পদ সংযোগ (M49)",
    "Capitalisation Reference": "মূলধনীকরণ রেফারেন্স",
    "Capitalised Amount": "মূলধনীকৃত পরিমাণ", "Asset Category": "সম্পদের শ্রেণি",
    "Period Close": "পর্যায় সমাপ্তি", "Fixed Asset Seam": "স্থায়ী সম্পদ সংযোগ",
    "Finance": "ফাইন্যান্স", "Suspense (AR-006 section 5.4)": "সাসপেন্স (AR-006)",
    # cd_tax_engine_bd
    "VAT Treatment": "ভ্যাট শ্রেণি", "Tariff Code": "ট্যারিফ কোড",
    "Treatment": "শ্রেণি নির্ধারণ", "Rate (%)": "হার (%)",
    "Truncated Fixed Base": "ট্রাংকেটেড নির্দিষ্ট ভিত্তি",
    "Mushak 6.3 VAT Register": "মুশক ৬.৩ ভ্যাট রেজিস্টার",
    "Mushak 6.3 No.": "মুশক ৬.৩ নং", "Invoice Reference": "চালান রেফারেন্স",
    "Supplier": "সরবরাহকারী", "Supplier BIN": "সরবরাহকারী BIN",
    "Buyer": "ক্রেতা", "Customer BIN": "ক্রেতার BIN",
    "Source Event": "উৎস ইভেন্ট", "Determination": "নির্ধারণ",
    "Mushak 6.3 Register": "মুশক ৬.৩ রেজিস্টার", "VAT Treatments": "ভ্যাট শ্রেণিসমূহ",
    "Parties": "পক্ষসমূহ", "Amounts": "পরিমাণসমূহ", "Unposted": "অ-পোস্টকৃত",
    "Group By": "গ্রুপ অনুযায়ী",
    # cd_billing_engine
    "AR Invoice": "প্রাপ্য হিসাব চালান", "Source Model": "উৎস মডেল",
    "Source ID": "উৎস আইডি", "Mushak 6.3": "মুশক ৬.৩",
    "Gen (s)": "জেনারেশন (সে.)", "AR Invoice Line": "চালান লাইন",
    "Dunning Run": "ডানিং রান", "Invoice": "চালান", "Overdue": "অতিমেয়াদি",
    "Days Overdue": "অতিমেয়াদি দিন", "Ageing Bucket": "আয়ু বালতি",
    "Ageing": "আয়ু বিশ্লেষণ", "Credit Note": "ক্রেডিট নোট",
    "Original Invoice": "মূল চালান", "Credit Amount": "ক্রেডিট পরিমাণ",
    "Approved By": "অনুমোদনকারী", "AR Invoices": "প্রাপ্য চালানসমূহ",
    "Collections & Dunning": "আদায় ও ডানিং", "Collections": "আদায়",
    "Credit Notes": "ক্রেডিট নোটসমূহ", "Reminder (NT-006 L1)": "অনুস্মারক (NT-006 L1)",
    "Final Notice (L2)": "চূড়ান্ত নোটিশ (L2)",
    "Escalated to Collections (L3)": "আদায়ে এসকালেটেড (L3)",
    "Service Failure": "সার্ভিস ব্যর্থতা", "Pricing Error": "মূল্য ত্রুটি",
    "Warranty Re-work": "ওয়ারেন্টি পুনঃকাজ", "Goodwill": "সদিচ্ছা",
    "Return": "ফেরত", "Current": "বর্তমান",
    # cd_ap_ext
    "Vendor Invoice (three-way match)": "ভেন্ডর চালান (থ্রি-ওয়ে ম্যাচ)",
    "Vendor Invoice Ref": "ভেন্ডর চালান রেফারেন্স", "Subtotal": "উপমোট",
    "TDS Deducted": "TDS কর্তন", "Purchase Order": "ক্রয় আদেশ",
    "Three-Way Match": "থ্রি-ওয়ে ম্যাচ", "Matched Invoice": "মিলিত চালান",
    "Unmatched": "অমিলিত", "Auto-Matched": "স্বয়ংক্রিয় মিল",
    "Manually Matched": "ম্যানুয়াল মিল", "3-Way": "থ্রি-ওয়ে",
    "Vendor Invoice Line": "ভেন্ডর চালান লাইন", "TDS Category": "TDS শ্রেণি",
    "Expense Claim": "ব্যয় দাবি", "Claimed Amount": "দাবিকৃত পরিমাণ",
    "Expense Date": "ব্যয়ের তারিখ", "Vendor Invoices": "ভেন্ডর চালানসমূহ",
    "Expense Claims": "ব্যয় দাবিসমূহ",
    "service_general": "service_general", "rent_commercial": "rent_commercial",
    "service_contractor": "service_contractor", "professional_fees": "professional_fees",
    "commission": "commission", "supply_of_goods": "supply_of_goods",
    "transport": "transport",
    # cd_cash_position
    "Payment Execution": "পেমেন্ট নির্বাহন", "Payee": "প্রাপক",
    "Bank Transfer": "ব্যাংক ট্রান্সফার", "Cheque": "চেক", "Cash": "নগদ",
    "bKash/Nagad Merchant Pay": "বিকাশ/নগদ মার্চেন্ট পে",
    "Executed At": "নির্বাহনের সময়", "Bank Statement Line": "ব্যাংক স্টেটমেন্ট লাইন",
    "Bank Reference": "ব্যাংক রেফারেন্স", "Matched Payment": "মিলিত পেমেন্ট", "Cash Position Snapshot": "নগদ অবস্থান স্ন্যাপশট",
    "As Of": "যতদিন পর্যন্ত", "Bank": "ব্যাংক", "Branch Drawers": "শাখা ড্রয়ার",
    "Pending Payments": "অপেক্ষমাণ পেমেন্ট", "Total Position": "মোট অবস্থান",
    "Payment Executions": "পেমেন্ট নির্বাহনসমূহ", "Bank Statements": "ব্যাংক স্টেটমেন্ট",
    "Cash Position": "নগদ অবস্থান", "Position": "অবস্থান",
    # cd_rate_card
    "Rate Card": "রেট কার্ড", "Rate Line Name": "রেট লাইনের নাম",
    "Product Code": "পণ্য কোড", "Labour": "শ্রম", "Part": "পার্টস",
    "Consumable": "অব্যবহৃত্যযোগ্য", "Transport": "পরিবহন",
    "Minimum Tier": "সর্বনিম্ন স্তর", "Contract No.": "চুক্তি নং",
    "Rate Cards": "রেট কার্ডসমূহ",
    # cd_quotation
    "Quotation State": "কোটেশন অবস্থা", "Quoted to Customer": "গ্রাহককে কোট করা",
    "Internal Estimate": "অভ্যন্তরীণ অনুমান", "Negotiating": "দর কষাকষি",
    "Accepted": "গৃহীত", "Declined": "প্রত্যাখ্যাত", "Quotation (M36)": "কোটেশন (M36)",
    "Tender Reference": "টেন্ডার রেফারেন্স",
    "Discount Approval": "ছাড় অনুমোদন", "Discount (%)": "ছাড় (%)",
    "Pending": "অপেক্ষমাণ", "Rejected": "প্রত্যাখ্যাত", "Justification": "যৌক্তিকতা",
    "Quotation": "কোটেশন", "Discount Approvals": "ছাড় অনুমোদনসমূহ",
    # cd_requisition
    "Requisition": "ক্রয় অনুরোধ", "Requesting Branch": "অনুরোধকারী শাখা",
    "Requested By": "অনুরোধকারী", "Estimated Amount": "আনুমানিক পরিমাণ",
    "Urgent (stock-out)": "জরুরি (স্টক-আউট)", "Emergency (job-stopped)": "ইমার্জেন্সি (কাজ বন্ধ)",
    "Converted to PO": "PO-তে রূপান্তরিত", "Normal": "স্বাভাবিক",
    "Urgent": "জরুরি", "Emergency": "ইমার্জেন্সি",
    "Order Date": "অর্ডারের তারিখ", "Deliver-to Branch": "ডেলিভি শাখা",
    "Sent": "প্রেরিত", "Acknowledged": "স্বীকৃত", "Partially Received": "আংশিক গৃহীত",
    "Received": "গৃহীত", "Closed": "বন্ধ", "Cancelled": "বাতিল",
    "PO Reference": "PO রেফারেন্স", "Ordered": "অর্ডিত", "Purchase Order Line": "ক্রয় আদেশ লাইন",
    "PO / receipt / invoice reconciled": "PO / রিসিট / চালান মিলেছে",
    "Purchase Orders": "ক্রয় আদেশসমূহ", "Requisitions": "ক্রয় অনুরোধসমূহ",
    "Procurement": "প্রকিউরমেন্ট", "Draft": "খসড়া",
    # cd_consignment
    "Consignment": "কনসাইনমেন্ট", "Consignment No.": "কনসাইনমেন্ট নং",
    "Pickup (customer -> branch)": "পিকআপ (গ্রাহক -> শাখা)",
    "Delivery (branch -> customer)": "ডেলিভি (শাখা -> গ্রাহক)",
    "Branch Transfer": "শাখা স্থানান্তর", "Return to Vendor": "ভেন্ডরে ফেরত",
    "Confirmed": "নিশ্চিত", "In Transit": "পথিমধ্যে", "Delivered": "ডেলিভৃত",
    "Returned": "ফেরতকৃত", "Lost": "হারানো", "Origin": "উৎস",
    "Destination": "গন্তব্য", "Rider": "রাইডার", "Custody Chain": "কাস্টডি চেইন",
    "Chain Broken": "চেইন ভাঙা", "Custody Summary": "কাস্টডি সারসংক্ষেপ",
    "Custody Scan": "কাস্টডি স্ক্যান", "Picked Up": "পিক আপ করা",
    "Hub Scan": "হাব স্ক্যান", "Out for Delivery": "ডেলিভির পথে",
    "Scanned At": "স্ক্যানের সময়", "Scanned By": "স্ক্যানকারী",
    "Location": "অবস্থান", "Device Serial": "ডিভাইস সিরিয়াল",
    "Consignments": "কনসাইনমেন্টসমূহ", "Chain": "চেইন",
    "Service Order": "সার্ভিস অর্ডার",
    # cd_wms_structure
    "Bins": "বিনসমূহ", "Zones": "অঞ্চলসমূহ",
    # cd_wms_structure
    "Warehouse": "গুদাম", "Warehouse Zone": "গুদাম অঞ্চল",
    "Receiving": "গ্রহণ", "Quality Inspection": "গুণগত পরিদর্শন",
    "Quarantine / Blocked": "কোয়ারেন্টাইন / অবরুদ্ধ",
    "Main Storage": "প্রধান সংরক্ষণ", "Dispatch": "প্রেরণ", "Returns": "ফেরতসমূহ",
    "Reservable": "সংরক্ষণযোগ্য", "Warehouse Bin": "গুদাম বিন",
    "Barcode": "বারকোড", "Capacity Qty": "ধারণক্ষমতা",
    "Warehouses": "গুদামসমূহ",
    # cd_workflow_engine
    "Business Automation": "ব্যবসায়িক অটোমেশন", "AUT Code": "AUT কোড",
    "Trigger": "ট্রিগার", "Action": "কার্যক্রম",
    "Odoo Automated Action (event + server action)": "Odoo স্বয়ংক্রিয় কার্যক্রম",
    "Apache Airflow (scheduled / threshold workflow)": "Apache Airflow (নির্ধারিত কার্যক্রম)",
    "Domain Service (named L5 engine)": "ডোমেইন সার্ভিস (নির্দিষ্ট L5 ইঞ্জিন)",
    "Engine Reference": "ইঞ্জিন রেফারেন্স",
    "Manual Fallback (the catalogue's named fallback)": "ম্যানুয়াল ফলব্যাক (ক্যাটালগের নামকৃত ফলব্যাক)",
    "Retry then alert": "পুনঃপ্রচেষ্টা পরে সতর্কতা",
    "Approval Authority Matrix": "অনুমোদন কর্তৃত্ব ম্যাট্রিক্স",
    "Decision Domain": "সিদ্ধান্ত ডোমেইন", "Estimate Approval": "অনুমান অনুমোদন", "Discount": "ছাড়",
    "Stock Adjustment": "স্টক সমন্বয়", "Write-Off": "রাইট-অফ",
    "Threshold": "সীমা", "Approver Role (R-nn)": "অনুমোদক ভূমিকা (R-nn)",
    "Automation Register": "অটোমেশন রেজিস্টার",
    "Approval Matrix": "অনুমোদন ম্যাট্রিক্স",
    "Estimate": "অনুমান", "Adjustment": "সমন্বয়",
    # cd_vendor_portal
    "Vendor Portal": "ভেন্ডর পোর্টাল", "My Purchase Orders": "আমার ক্রয় আদেশসমূহ",
    "My Invoices": "আমার চালানসমূহ", "My Invoice Submissions": "আমার চালান জমা",
    "My Purchase Order": "আমার ক্রয় আদেশ",
    # cd_esignature
    "E-Signature Envelope": "ই-সিগনেচার খাম", "Subject": "বিষয়",
    "Document": "দলিল", "Documents": "দলিলসমূহ", "Templates": "টেমপ্লেটসমূহ",
    "Signs As": "যে পরিচয়ে স্বাক্ষর", "Partially Signed": "আংশিক স্বাক্ষরিত",
    "Completed": "সম্পন্ন", "Voided": "বাতিলকৃত", "Signer": "স্বাক্ষরকারী",
    "Signers": "স্বাক্ষরকারীগণ", "Signature Provider": "স্বাক্ষর সরবরাহকারী",
    "E-Signatures": "ই-সিগনেচার", "Signing Order": "স্বাক্ষর ক্রম",
}

HEADER = '''# Bengali (Bangladesh) translation for {module}.
# 100% coverage — FF-24/FF-25 block below 100% (AS-12, DE-17, TR-07).
msgid ""
msgstr ""
"Project-Id-Version: 1000FiX ERP 19.0\\n"
"Language: bn_BD\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

'''

MODULES = [
    "cd_gl_ext", "cd_tax_engine_bd", "cd_billing_engine", "cd_ap_ext",
    "cd_cash_position", "cd_rate_card", "cd_quotation", "cd_requisition",
    "cd_consignment", "cd_wms_structure", "cd_workflow_engine",
    "cd_vendor_portal", "cd_esignature",
]


def upsert_po(module: str) -> tuple[int, int]:
    base = next(p for p in ADDONS.rglob(module)
                if p.is_dir() and (p / "__manifest__.py").is_file())
    pot_path = base / "i18n" / f"{module}.pot"
    if not pot_path.exists():
        # no strings extracted (e.g. view-only modules with none) — skip
        return 0, 0
    msgids = [m for m in re.findall(r'^msgid "((?:[^"\\]|\\.)*)"',
                                    pot_path.read_text(encoding="utf-8"), re.M) if m]
    po_path = base / "i18n" / "bn_BD.po"
    lines = [HEADER.format(module=module)]
    missing = []
    for msgid in msgids:
        msgstr = T.get(msgid.replace('\\"', '"'), "")
        if not msgstr:
            missing.append(msgid)
            msgstr = msgid  # identity fallback keeps count honest for the fix pass
        lines.append(f'msgid "{msgid}"')
        lines.append(f'msgstr "{msgstr}"')
        lines.append("")
    po_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return len(msgids), len(missing)


def main() -> int:
    total_missing = 0
    for module in MODULES:
        count, missing = upsert_po(module)
        total_missing += missing
        if count:
            print(f"{module}: {count} strings" + (f" MISSING {missing}" if missing else " OK"))
    print("done" if not total_missing else f"{total_missing} untranslated — fill T dict")
    return 1 if total_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
