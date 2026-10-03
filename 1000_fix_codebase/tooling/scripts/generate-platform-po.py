#!/usr/bin/env python3
"""One-shot: generate the eight platform bn_BD.po files (P04-M06 W1 screens).

Every string below is authored once, here; the file it writes is the
deliverable. Re-run is idempotent (same input -> same output). After this
run, FF-25 enforces 100% on every module shipping a template.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"

T: dict[str, str] = {
    # shared
    "Operating Unit": "পরিচালন ইউনিট",
    "Company": "কোম্পানি",
    "Currency": "মুদ্রা",
    "Description": "বিবরণ",
    "Name (Bengali)": "নাম (বাংলা)",
    "From": "হইতে",
    "To": "প্রতি",
    "Lines": "লাইনসমূহ",
    "Model": "মডেল",
    "Field": "ফিল্ড",
    "Version": "সংস্করণ",
    "Code": "কোড",
    "Scope": "পরিসর",
    "Active": "সক্রিয়",
    "Branch": "শাখা",
    "Branches": "শাখাসমূহ",
    "Party": "পার্টি",
    "phone,name_normalized": "phone,name_normalized",
    "নাম (বাংলা)": "নাম (বাংলা)",
    # cd_catalogue
    "1000FiX Authorised": "1000FiX অনুমোদিত",
    "Authorisation Expiry": "অনুমোদনের মেয়াদ",
    "Brand": "ব্র্যান্ড",
    "Brand Code": "ব্র্যান্ড কোড",
    "Brands": "ব্র্যান্ডসমূহ",
    "Catalogue": "ক্যাটালগ",
    "Catalogue Item": "ক্যাটালগ আইটেম",
    "Catalogue Items": "ক্যাটালগ আইটেমসমূহ",
    "Compatible Device Models": "সামঞ্জস্যপূর্ণ ডিভাইস মডেল",
    "Components": "উপাদানসমূহ",
    "Daily Rate": "দৈনিক ভাড়া",
    "Description (Bengali)": "বিবরণ (বাংলা)",
    "Device Models": "ডিভাইস মডেলসমূহ",
    "Estimated Cost": "আনুমানিক ব্যয়",
    "Estimated Time (hours)": "আনুমানিক সময় (ঘণ্টা)",
    "Items": "আইটেমসমূহ",
    "Maximum Rental Duration (days)": "সর্বোচ্চ ভাড়ার মেয়াদ (দিন)",
    "Model Code": "মডেল কোড",
    "Monthly Rate": "মাসিক ভাড়া",
    "Name": "নাম",
    "New Warranty (months)": "নতুন ওয়ারেন্টি (মাস)",
    "Price Multiplier (e.g. 0.8 = 80% of new price)": "মূল্য গুণক (যেমন 0.8 = নতুন মূল্যের ৮০%)",
    "Product": "পণ্য",
    "Product Category": "পণ্য শ্রেণি",
    "Product Name (Bengali)": "পণ্যের নাম (বাংলা)",
    "Product Template": "পণ্য টেমপ্লেট",
    "Refurb Warranty (days)": "রিফার্ব ওয়ারেন্টি (দিন)",
    "Security Deposit": "নিরাপত্তা জামানত",
    "Service Kits": "সার্ভিস কিট",
    "Standard Cost": "প্রচলিত ব্যয়",
    "Standard Labour Time (hours)": "প্রচলিত শ্রম সময় (ঘণ্টা)",
    "Support Portal URL": "সাপোর্ট পোর্টাল URL",
    "Time Allocation (hours)": "সময় বণ্টন (ঘণ্টা)",
    "Weekly Rate": "সাপ্তাহিক ভাড়া",
    # cd_document_core
    "All Documents": "সকল দলিল",
    "Applicable Document Types": "প্রযোজ্য দলিলের ধরন",
    "Attachment": "সংযুক্তি",
    "Document": "দলিল",
    "Documents": "দলিলসমূহ",
    "Linked Model": "সংযুক্ত মডেল",
    "Linked Record ID": "সংযুক্ত রেকর্ড আইডি",
    "Regulatory Basis": "নিয়ন্ত্রক ভিত্তি",
    "Retention Class": "সংরক্ষণ শ্রেণি",
    "Retention Expires": "সংরক্ষণ মেয়াদোত্তীর্ণ",
    "Retention Period (years)": "সংরক্ষণ মেয়াদ (বছর)",
    # cd_employee_core
    "Additional Roles": "অতিরিক্ত ভূমিকা",
    "Assigned Branch": "নিযুক্ত শাখা",
    "Employee Code": "কর্মী কোড",
    "Joined Date": "যোগদানের তারিখ",
    "Keycloak User ID": "Keycloak ব্যবহারকারী আইডি",
    "Left Date": "ত্যাগের তারিখ",
    "Linked Party": "সংযুক্ত পার্টি",
    "Party Role (Employee)": "পার্টি ভূমিকা (কর্মী)",
    "Primary Business Role (M29)": "প্রধান ব্যবসায়িক ভূমিকা (M29)",
    # cd_entity_config
    "1000FiX Operations": "1000FiX অপারেশন্স",
    "Address": "ঠিকানা",
    "Archived": "সংরক্ষণাগারভুক্ত",
    "Branch Code": "শাখা কোড",
    "Branch Manager": "শাখা ব্যবস্থাপক",
    "Branch Name": "শাখার নাম",
    "Branch Name (Bengali)": "শাখার নাম (বাংলা)",
    "Calendar Name": "ক্যালেন্ডারের নাম",
    "Combined Cap (non-transactional)": "সম্মিলিত সীমা (অ-লেনদেন)",
    "Configuration": "কনফিগারেশন",
    "Country": "দেশ",
    "Country Data Packs": "দেশ ডেটা প্যাক",
    "Date (holiday packs)": "তারিখ (ছুটির প্যাক)",
    "Dispatch Zone": "ডিসপ্যাচ জোন",
    "Dispatch Zones": "ডিসপ্যাচ জোনসমূহ",
    "District": "জেলা",
    "District (Bengali)": "জেলা (বাংলা)",
    "Division": "বিভাগ",
    "Division (Bengali)": "বিভাগ (বাংলা)",
    "Email": "ইমেইল",
    "Enabled Branches": "সক্রিয় শাখাসমূহ",
    "Enabled Roles": "সক্রিয় ভূমিকাসমূহ",
    "Entity": "প্রতিষ্ঠান",
    "Entity Code": "প্রতিষ্ঠান কোড",
    "Feature Flag": "ফিচার ফ্ল্যাগ",
    "Feature Flags": "ফিচার ফ্ল্যাগসমূহ",
    "Frequency Cap (7-day rolling)": "ফ্রিকোয়েন্সি সীমা (৭ দিন রোলিং)",
    "From (hour)": "শুরু (ঘণ্টা)",
    "Geofence Name": "জিওফেন্সের নাম",
    "Geofences": "জিওফেন্সসমূহ",
    "Geometry (JSON)": "জ্যামিতি (JSON)",
    "Holiday": "ছুটি",
    "Holiday (Bengali)": "ছুটি (বাংলা)",
    "Holidays": "ছুটিসমূহ",
    "House/Building": "বাড়ি/ভবন",
    "Key": "কী",
    "Landmark": "ল্যান্ডমার্ক",
    "Legal Entities": "আইনি প্রতিষ্ঠানসমূহ",
    "Legal Entity": "আইনি প্রতিষ্ঠান",
    "Legal Name": "আইনি নাম",
    "Legal Name (Bengali)": "আইনি নাম (বাংলা)",
    "Loaded At": "লোডের সময়",
    "Name (English)": "নাম (ইংরেজি)",
    "Notification Configuration": "নোটিফিকেশন কনফিগারেশন",
    "Pack Code": "প্যাক কোড",
    "Pack Name": "প্যাকের নাম",
    "Parent Code": "ঊর্ধ্বতন কোড",
    "Phone": "ফোন",
    "Platform Administration": "প্ল্যাটফর্ম প্রশাসন",
    "Policy (NT-003)": "নীতি (NT-003)",
    "Postcode": "পোস্টকোড",
    "Primary Operating Unit": "প্রধান পরিচালন ইউনিট",
    "Send Window": "প্রেরণ সময়সীমা",
    "Stale Discard (hours)": "পুরানো বাতিল (ঘণ্টা)",
    "Street/Road": "রাস্তা/সড়ক",
    "Template": "টেমপ্লেট",
    "To (hour)": "শেষ (ঘণ্টা)",
    "Union/Ward": "ইউনিয়ন/ওয়ার্ড",
    "Upazila/Thana": "উপজেলা/থানা",
    "Upazila/Thana (Bengali)": "উপজেলা/থানা (বাংলা)",
    "Weekday": "সপ্তাহের দিন",
    "Working Calendar": "ওয়ার্কিং ক্যালেন্ডার",
    "Working Calendars": "ওয়ার্কিং ক্যালেন্ডারসমূহ",
    "Working Hours": "কর্মঘণ্টা",
    "Zone": "জোন",
    "Zone Code": "জোন কোড",
    "Zone Name": "জোনের নাম",
    "Zone Name (Bengali)": "জোনের নাম (বাংলা)",
    # cd_event_outbox
    "Aggregate": "অ্যাগ্রিগেট",
    "Aggregate ID": "অ্যাগ্রিগেট আইডি",
    "Event ID": "ইভেন্ট আইডি",
    "Event Outbox": "ইভেন্ট আউটবক্স",
    "Event Outbox Entry": "ইভেন্ট আউটবক্স এন্ট্রি",
    "Event Type": "ইভেন্টের ধরন",
    "Integration Platform": "ইন্টিগ্রেশন প্ল্যাটফর্ম",
    "Metadata": "মেটাডেটা",
    "Metadata (JSON)": "মেটাডেটা (JSON)",
    "Payload": "পেলোড",
    "Payload (JSON)": "পেলোড (JSON)",
    # cd_mdm_core
    "Approve": "অনুমোদন",
    "Change Requests": "পরিবর্তনের অনুরোধ",
    "Current Values": "বর্তমান মানসমূহ",
    "Current Values (JSON)": "বর্তমান মানসমূহ (JSON)",
    "MDM Change Request": "MDM পরিবর্তনের অনুরোধ",
    "MDM Change Requests": "MDM পরিবর্তনের অনুরোধসমূহ",
    "Master Data Governance": "মাস্টার ডেটা গভর্নেন্স",
    "Proposed Changes": "প্রস্তাবিত পরিবর্তন",
    "Proposed Changes (JSON)": "প্রস্তাবিত পরিবর্তন (JSON)",
    "Reference": "রেফারেন্স",
    "Reject": "প্রত্যাখ্যান",
    "Source Priority Order": "উৎসের অগ্রাধিকার ক্রম",
    "Submit": "জমা দিন",
    "Target Model": "লক্ষ্য মডেল",
    "Target Record ID": "লক্ষ্য রেকর্ড আইডি",
    # cd_party_master
    "Active Branches": "সক্রিয় শাখাসমূহ",
    "Checksum Valid": "চেকসাম বৈধ",
    "Child Party": "অধীন পার্টি",
    "Consent": "সম্মতি",
    "Consent Records": "সম্মতির রেকর্ড",
    "Dedup Rules": "ডিডুপ নিয়ম",
    "Document Number": "দলিল নম্বর",
    "Expiry Date": "মেয়াদোত্তীর্ণের তারিখ",
    "Fuzzy Threshold": "ফাজি থ্রেশহোল্ড",
    "Granted At": "প্রদানের সময়",
    "Identity Documents": "পরিচয়পত্রসমূহ",
    "Issuing Country": "ইস্যুকারী দেশ",
    "Match Fields": "মিলের ফিল্ড",
    "Parent Party": "ঊর্ধ্বতন পার্টি",
    "Parties": "পার্টিসমূহ",
    "Party Kernel (M33)": "পার্টি কার্নেল (M33)",
    "Party Master": "পার্টি মাস্টার",
    "Party Role": "পার্টি ভূমিকা",
    "Party Roles": "পার্টি ভূমিকাসমূহ",
    "Primary Document": "প্রধান দলিল",
    "Proof Reference": "প্রমাণের রেফারেন্স",
    "Related Parties (as child)": "সম্পর্কিত পার্টি (অধীন হিসেবে)",
    "Related Parties (as parent)": "সম্পর্কিত পার্টি (ঊর্ধ্বতন হিসেবে)",
    "Role Since": "ভূমিকা থেকে",
    "Roles": "ভূমিকাসমূহ",
    "Rule Name": "নিয়মের নাম",
    "Signed form ID / OTP session / legacy batch": "স্বাক্ষরিত ফর্ম আইডি / OTP সেশন / লিগ্যাসি ব্যাচ",
    "Since": "হইতে",
    "Until": "পর্যন্ত",
    "Verified By": "যাচাইকারী",
    "Withdrawn At": "প্রত্যাহারের সময়",
    # cd_rbac_ext
    "Administration": "প্রশাসন",
    "Business Role": "ব্যবসায়িক ভূমিকা",
    "Business Roles": "ব্যবসায়িক ভূমিকাসমূহ",
    "Data Isolation Tiers": "ডেটা আইসোলেশন স্তর",
    "Entity Configuration": "প্রতিষ্ঠান কনফিগারেশন",
    "Isolation Tiers": "আইসোলেশন স্তরসমূহ",
    "Keycloak Realm Role": "Keycloak রিয়েল্ম ভূমিকা",
    "NID Number": "NID নম্বর",
    "Odoo Group": "Odoo গ্রুপ",
    "Operating Units": "পরিচালন ইউনিটসমূহ",
    "Record Rule Domain": "রেকর্ড রুল ডোমেইন",
    "Residency Reference": "রেসিডেন্সি রেফারেন্স",
    "Role A": "ভূমিকা ক",
    "Role B": "ভূমিকা খ",
    "Role Code (R-nn)": "ভূমিকা কোড (R-nn)",
    "Role Name": "ভূমিকার নাম",
    "Role Name (Bengali)": "ভূমিকার নাম (বাংলা)",
    "Roles with Access": "অ্যাক্সেসপ্রাপ্ত ভূমিকাসমূহ",
    "Scope (OUs)": "পরিসর (OU)",
    "Security & Access": "নিরাপত্তা ও অ্যাক্সেস",
    "SoD Code": "SoD কোড",
    "SoD Controls": "SoD নিয়ন্ত্রণসমূহ",
    "Why these roles conflict": "কেন এই ভূমিকাগুলো দ্বন্দ্ব করে",
    # domain top-ups
    "Devices": "ডিভাইসসমূহ",
    "Service Intake": "সার্ভিস ইনটেক",
    "Token Queue": "টোকেন কিউ",
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


def po_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def module_dir(module: str) -> Path:
    return next(
        p for p in ADDONS.rglob(module)
        if p.is_dir() and (p / "__manifest__.py").is_file()
    )


def upsert_po(module: str) -> tuple[int, int]:
    base = module_dir(module)
    pot = (base / "i18n" / f"{module}.pot").read_text(encoding="utf-8")
    msgids = [m for m in re.findall(r'^msgid "((?:[^"\\]|\\.)*)"', pot, re.M) if m]
    po_path = base / "i18n" / "bn_BD.po"
    existing = dict(
        re.findall(r'msgid "((?:[^"\\]|\\.)*)"\s*\nmsgstr "((?:[^"\\]|\\.)*)"',
                   po_path.read_text(encoding="utf-8")) if po_path.exists() else []
    )
    lines = [HEADER.format(module=module)]
    untranslated = []
    for msgid in msgids:
        unescaped = msgid.replace('\\"', '"').replace("\\\\", "\\")
        msgstr = T.get(unescaped) or existing.get(msgid, "")
        if not msgstr:
            untranslated.append(unescaped)
        lines.append(f'msgid "{msgid}"')
        lines.append(f'msgstr "{po_escape(msgstr)}"')
        lines.append("")
    po_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return len(msgids), len(untranslated)


def main() -> int:
    modules = [
        "cd_catalogue", "cd_document_core", "cd_employee_core",
        "cd_entity_config", "cd_event_outbox", "cd_mdm_core",
        "cd_party_master", "cd_rbac_ext",
        "cd_device_registry", "cd_front_desk",  # top-ups
    ]
    total_missing = 0
    for module in modules:
        count, missing = upsert_po(module)
        total_missing += missing
        flag = " OK" if not missing else f" MISSING {missing}"
        print(f"{module}: {count} strings{flag}")
        for m in ([m for m in missing] if False else []):
            pass
    print("all translated" if not total_missing else f"{total_missing} strings still untranslated")
    return 1 if total_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
