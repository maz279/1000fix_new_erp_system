#!/usr/bin/env python3
"""One-shot: bn_BD.po for the six P07 modules (100% — FF-25).

RETIRED (2026-10-22, TR-07/DoD-08): this one-shot wrote the P07 bn_BD.po files in a form
Odoo 19 cannot load - no `#. module:` comment and no `#:` references, so
odoo.tools.translate.PoFileReader raises AttributeError and the whole bn_BD
load aborts. The files it produced have since been completed and rewritten
in Odoo form; re-running it would overwrite them. It now exits without
writing anything. Maintain i18n/bn_BD.po directly and refresh templates and
references with tooling/scripts/extract-translations.py
(docs/guides/bn-terminology-glossary.md). The tables below are kept as history.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"

T: dict[str, str] = {
    # shared
    "Company": "কোম্পানি",
    "Customer": "গ্রাহক",
    "Vendor": "ভেন্ডর",
    "Contract": "চুক্তি",
    "State": "অবস্থা",
    "Amount": "পরিমাণ",
    "Currency": "মুদ্রা",
    "Active": "সক্রিয়",
    "Name": "নাম",
    "Description": "বিবরণ",
    "Start Date": "শুরুর তারিখ",
    "Due Date": "মেয়াদ",
    "Draft": "খসড়া",
    "Total": "মোট",
    "Period": "পর্যায়",
    # cd_contract_core
    "Contract No.": "চুক্তি নং",
    "Title": "শিরোনাম",
    "Product Family": "পণ্য পরিবার",
    "AMC (Annual Maintenance)": "এএমসি (বার্ষিক রক্ষণাবেক্ষণ)",
    "RAMC (Repair & Maintenance)": "র‍্যামক (মেরামত ও রক্ষণাবেক্ষণ)",
    "Managed Services": "পরিচালিত সেবা",
    "Rental": "ভাড়া",
    "Marketplace Agreement": "মার্কেটপ্লেস চুক্তি",
    "Pending Signature": "স্বাক্ষরের অপেক্ষায়",
    "Active ": "সক্রিয়",
    "Expiring Soon": "শীঘ্রই মেয়াদোত্তীর্ণ",
    "Expired": "মেয়াদোত্তীর্ণ",
    "Terminated": "সমাপ্ত",
    "The term end must be after the start": "মেয়াদ শুরুর পরে হতে হবে",
    "Annual Value": "বার্ষিক মূল্য",
    "Annual Escalation (%)": "বার্ষিক বৃদ্ধি (%)",
    "Covered Assets": "আচ্ছাদিত সম্পদ",
    "Entitlements": "এনটাইটেলমেন্ট",
    "Contract Entitlement": "চুক্তি এনটাইটেলমেন্ট",
    "Contract SLAs": "চুক্তি SLA",
    "E-Signature": "ই-সিগনেচার",
    "Term End": "মেয়াদ শেষ",
    "Contracts": "চুক্তিসমূহ",
    "All Contracts": "সকল চুক্তি",
    "Preventive Visits": "প্রতিরোধমূলক ভিজিট",
    "Repair Incidents": "মেরামত ঘটনা",
    "Labour Hours": "শ্রম ঘণ্টা",
    "Loaner Devices": "লোনার ডিভাইস",
    "Quantity Consumed": "ব্যবহৃত পরিমাণ",
    "Quantity Remaining": "অবশিষ্ট পরিমাণ",
    "Specific Asset": "নির্দিষ্ট সম্পদ",
    "Quantity Included": "অন্তর্ভুক্ত পরিমাণ",
    "Preventive Maintenance Visit": "প্রতিরোধমূলক রক্ষণাবেক্ষণ ভিজিট",
    "PM Schedule": "পিএম সময়সূচি",
    "Scheduled": "নির্ধারিত",
    "Dispatched": "প্রেরিত",
    "Completed": "সম্পন্ন",
    "Skipped": "বাদ দেওয়া",
    "Service Order": "সার্ভিস অর্ডার",
    "Preventive maintenance visit": "প্রতিরোধমূলক রক্ষণাবেক্ষণ ভিজিট",
    "Terms": "শর্তাবলী",
    "Commercial": "বাণিজ্যিক",
    "Pending": "অপেক্ষমাণ",
    # cd_warranty_claims
    "Claim No.": "দাবি নং",
    "Warranty / Protection Product": "ওয়ারেন্টি / সুরক্ষা পণ্য",
    "Warranty Extension": "ওয়ারেন্টি সম্প্রসারণ",
    "Protection Plan": "সুরক্ষা পরিকল্পনা",
    "Catalogue Item": "ক্যাটালগ আইটেম",
    "Duration (months)": "মেয়াদ (মাস)",
    "Waiting Days": "অপেক্ষার দিন",
    "Aggregate Claim Limit": "সমষ্টিগত দাবি সীমা",
    "Customer Excess": "গ্রাহক অতিরিক্ত",
    "Warranty Claim": "ওয়ারেন্টি দাবি",
    "Claim Amount": "দাবির পরিমাণ",
    "Evidence Pack": "প্রমাণ প্যাক",
    "Pack OK": "প্যাক সম্পূর্ণ",
    "Submitted": "জমা দেওয়া",
    "In Review": "পর্যালোচনাধীন",
    "Approved": "অনুমোদিত",
    "Rejected": "প্রত্যাখ্যাত",
    "Remitted": "পরিশোধিত",
    "Claim Evidence Item": "দাবির প্রমাণ আইটেম",
    "Before Photograph": "পূর্বের ছবি",
    "After Photograph": "পরের ছবি",
    "Diagnostic Record": "ডায়াগনস্টিক রেকর্ড",
    "Parts Issued Evidence": "পার্টস প্রদানের প্রমাণ",
    "Device Serial Capture": "ডিভাইস সিরিয়াল সংগ্রহ",
    "Technician Certification": "টেকনিশিয়ান সার্টিফিকেট",
    "Purchase Proof": "ক্রয়ের প্রমাণ",
    "Document": "দলিল",
    "Warranty Claims": "ওয়ারেন্টি দাবিসমূহ",
    "Claims": "দাবিসমূহ",
    "Protection Products": "সুরক্ষা পণ্যসমূহ",
    "Warranty": "ওয়ারেন্টি",
    "Brand": "ব্র্যান্ড",
    "Claim": "দাবি",
    "Amounts": "পরিমাণসমূহ",
    "Protection Product": "সুরক্ষা পণ্য",
    # cd_subscription
    "Subscription": "সাবস্ক্রিপশন",
    "Basic": "বেসিক",
    "Standard": "স্ট্যান্ডার্ড",
    "Premium": "প্রিমিয়াম",
    "Monthly": "মাসিক",
    "Quarterly": "ত্রৈমাসিক",
    "Annual": "বার্ষিক",
    "Recurring Amount": "পুনরাবৃত্ত পরিমাণ",
    "Trial": "ট্রায়াল",
    "Past Due": "মেয়াদোত্তীর্ণ",
    "Paused": "স্থগিত",
    "Cancelled": "বাতিলকৃত",
    "Churned": "ছুটে যাওয়া",
    "Revenue Recognition Schedule": "রাজস্ব স্বীকৃতি সময়সূচি",
    "Deferred Amount": "স্থগিত পরিমাণ",
    "Recognized": "স্বীকৃত",
    "Revenue Schedules": "রাজস্ব সময়সূচি",
    "Subscriptions": "সাবস্ক্রিপশনসমূহ",
    "One recognition schedule per source document": "প্রতি উৎস দলিলে একটি স্বীকৃতি সময়সূচি",
    "Billing Cycle": "বিলিং চক্র",
    "Next Invoice Date": "পরবর্তী চালানের তারিখ",
    # cd_contact_centre
    "Voice (Hotline 16743)": "ভয়েস (হটলাইন ১৬৭৪৩)",
    "WhatsApp": "হোয়াটসঅ্যাপ",
    "Web Chat": "ওয়েব চ্যাট",
    "Email": "ইমেইল",
    "In-App": "ইন-অ্যাপ",
    "Conversation": "কথোপকথন",
    "Contact Identity": "যোগাযোগ পরিচয়",
    "New": "নতুন",
    "With AI Assistant": "এআই সহকারীর সাথে",
    "With Agent": "এজেন্টের সাথে",
    "Resolved by AI": "এআই দ্বারা সমাধান",
    "Resolved by Agent": "এজেন্ট দ্বারা সমাধান",
    "Abandoned": "পরিত্যক্ত",
    "Transcript": "ট্রান্সক্রিপ্ট",
    "Conversation Turn": "কথোপকথন পালা",
    "AI Assistant": "এআই সহকারী",
    "Agent": "এজেন্ট",
    "Assistant Intent (transactional)": "সহকারী অভিপ্রায় (লেনদেনমূলক)",
    "Name (Bengali)": "নাম (বাংলা)",
    "Bengali Utterances": "বাংলা উচ্চারণ",
    "English Utterances": "ইংরেজি উচ্চারণ",
    "Grounding (live ERP data)": "গ্রাউন্ডিং (লাইভ ইআরপি ডেটা)",
    "Handoff on Failure": "ব্যর্থতায় হ্যান্ডঅফ",
    "Conversations": "কথোপকথনসমূহ",
    "Assistant Intents": "সহকারী অভিপ্রায়সমূহ",
    "Contact Centre": "যোগাযোগ কেন্দ্র",
    "Intent": "অভিপ্রায়",
    "Resolution": "সমাধান",
    "Context": "প্রসঙ্গ",
    "বাংলা": "বাংলা",
    "English": "ইংরেজি",
    "Speaker": "বক্তা",
    # cd_cx_feedback
    "Service Survey": "সার্ভিস সমীক্ষা",
    "One survey per service order": "প্রতি সার্ভিস অর্ডারে একটি সমীক্ষা",
    "Responded": "উত্তর দেওয়া",
    "খুব খারাপ / Very Poor": "খুব খারাপ",
    "খারাপ / Poor": "খারাপ",
    "মোটামুটি / Fair": "মোটামুটি",
    "ভালো / Good": "ভালো",
    "খুব ভালো / Excellent": "খুব ভালো",
    "Comment": "মন্তব্য",
    "Complaint": "অভিযোগ",
    "Service Quality": "সার্ভিসের গুণমান",
    "Delay / SLA": "বিলম্ব / SLA",
    "Billing": "বিলিং",
    "Staff Conduct": "কর্মীদের আচরণ",
    "Device Damage": "ডিভাইস ক্ষতি",
    "Other": "অন্যান্য",
    "Minor": "গৌণ",
    "Major": "বড়",
    "Critical": "সংকটজনক",
    "Investigating": "তদন্তাধীন",
    "NCR Raised": "এনসিআর জারি",
    "Root Cause Identified": "মূল কারণ চিহ্নিত",
    "CAPA Open": "ক্যাপা চালু",
    "Verification": "যাচাই",
    "Closed": "বন্ধ",
    "Supplier Scorecard": "সরবরাহকারী স্কোরকার্ড",
    "One scorecard per vendor and period": "প্রতি ভেন্ডর ও পর্যায়ে একটি স্কোরকার্ড",
    "On-time (%)": "সময়মতো (%)",
    "Complaints": "অভিযোগসমূহ",
    "Surveys": "সমীক্ষাসমূহ",
    "Supplier Scorecards": "সরবরাহকারী স্কোরকার্ডসমূহ",
    "Score": "স্কোর",
    "Source ID": "উৎস আইডি",
    "Source Model": "উৎস মডেল",
    "AI": "এআই",
    "Triggered": "ট্রিগার্ড",
    "TDS Return": "টিডিএস রিটার্ন",
    "Vendor Invoice": "ভেন্ডর চালান",
    # cd_corporate_portal
    "My Contracts": "আমার চুক্তিসমূহ",
    "My Subscriptions": "আমার সাবস্ক্রিপশনসমূহ",
    "Corporate Portal": "কর্পোরেট পোর্টাল",
    # tax returns
    "VAT Return (Mushak 9.1)": "ভ্যাট রিটার্ন (মুশক ৯.১)",
    "One VAT return per company and period": "প্রতি কোম্পানি ও পর্যায়ে একটি ভ্যাট রিটার্ন",
    "Taxable Value": "করযোগ্য মূল্য",
    "Output VAT": "আউটপুট ভ্যাট",
    "Input VAT": "ইনপুট ভ্যাট",
    "Net Payable": "নিট প্রদেয়",
    "Nil": "শূন্য",
    "NBR Confirmation": "এনবিআর নিশ্চিতকরণ",
    "Prepared": "প্রস্তুত",
    "Filed": "দাখিলকৃত",
    "TDS Return (quarterly)": "টিডিএস রিটার্ন (ত্রৈমাসিক)",
    "One TDS return per company and quarter": "প্রতি কোম্পানি ও ত্রৈমাসিকে একটি টিডিএস রিটার্ন",
    "Total Withheld": "মোট কর্তন",
    "VAT Returns": "ভ্যাট রিটার্নসমূহ",
    "TDS Returns": "টিডিএস রিটার্নসমূহ",
    "Fiscal Year": "অর্থবছর",
    "Withholding Tax Certificate": "কর্তন কর শংসাপত্র",
}

HEADER = """# Bengali (Bangladesh) translation for {module}.
# 100% coverage - FF-24/FF-25 block below 100% (AS-12, DE-17, TR-07).
msgid ""
msgstr ""
"Project-Id-Version: 1000FiX ERP 19.0\\n"
"Language: bn_BD\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

"""

MODULES = [
    "cd_contract_core",
    "cd_warranty_claims",
    "cd_subscription",
    "cd_contact_centre",
    "cd_cx_feedback",
    "cd_corporate_portal",
    "cd_tax_engine_bd",
]


def upsert_po(module: str) -> tuple[int, list[str]]:
    base = next(p for p in ADDONS.rglob(module) if p.is_dir() and (p / "__manifest__.py").is_file())
    pot_path = base / "i18n" / f"{module}.pot"
    if not pot_path.exists():
        return 0, []
    pot_text = pot_path.read_text(encoding="utf-8")
    msgids = [m for m in re.findall(r'^msgid "((?:[^"\\]|\\.)*)"', pot_text, re.M) if m]
    po_path = base / "i18n" / "bn_BD.po"
    existing = {}
    if po_path.exists():
        existing = dict(
            re.findall(
                r'msgid "((?:[^"\\]|\\.)*)"\nmsgstr "((?:[^"\\]|\\.)*)"',
                po_path.read_text(encoding="utf-8"),
            )
        )
    lines = [HEADER.format(module=module)]
    missing = []
    for msgid in msgids:
        raw = msgid.replace('\\"', '"')
        msgstr = T.get(raw) or existing.get(msgid, "")
        if not msgstr:
            missing.append(raw)
            msgstr = raw
        lines.append(f'msgid "{msgid}"')
        lines.append(f'msgstr "{msgstr}"')
        lines.append("")
    po_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return len(msgids), missing


def main() -> int:
    total_missing = 0
    for module in MODULES:
        count, missing = upsert_po(module)
        if count:
            print(f"{module}: {count} strings" + (f" MISSING {missing}" if missing else " OK"))
            total_missing += len(missing)
    print("done" if not total_missing else f"{total_missing} untranslated")
    return 1 if total_missing else 0


if __name__ == "__main__":
    print(
        "generate-p07-po.py: RETIRED - it would overwrite the Odoo-loadable i18n/bn_BD.po files; "
        "use tooling/scripts/extract-translations.py (see the module docstring)."
    )
    raise SystemExit(2)
