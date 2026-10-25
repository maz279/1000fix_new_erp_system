#!/usr/bin/env python3
"""generate-landing-artefact — PP5 landing/marketing shell data.

Extracts and enriches the 12 portal cards + 10 journey strips into a production-grade
bilingual landing artefact (libs/ts/i18n/src/landing.generated.json) consumed by the shared
LandingShell. Includes complete Bengali and English titles, personas, volumes,
capabilities, live production ports, navigation URLs, and deep-link shortcuts.

Regenerate:
    python tooling/generators/generate-landing-artefact.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "contracts" / "nav" / "registry.json"
OUT = REPO / "libs" / "ts" / "i18n" / "src" / "landing.generated.json"

# Production portals metadata, ports, deep links and full Bengali dictionary
PORTAL_META = {
    "P01": {
        "bn": "কাস্টমার সেলফ-সার্ভিস ও ওয়েব পোর্টাল",
        "users_bn": "সাধারণ গ্রাহক এবং সরাসরি সেবা প্রার্থী",
        "volume_bn": "প্রতি মাসে ২,৫০,০০০+ সেবা",
        "url": "/",
        "port": 3000,
        "is_live": True,
        "tech": "Next.js 16.3 + PWA",
        "capabilities_bn": [
            "ওটিপি লগইন ও ডিভাইস তালিকা",
            "৩-ধাপে সার্ভিস বুকিং ও স্লট নির্বাচন",
            "লাইভ ট্র্যাকিং ও টেকনিশিয়ান ইটিএ",
            "অনুমোদন, ডিজিটাল পেমেন্ট ও ই-স্বাক্ষর",
        ],
        "shortcuts": [
            {"label_en": "Booking", "label_bn": "সার্ভিস বুকিং", "url": "/booking"},
            {"label_en": "Live Tracking", "label_bn": "লাইভ ট্র্যাকিং", "url": "/tracking"},
            {"label_en": "My Devices", "label_bn": "ডিভাইস তালিকা", "url": "/devices"},
            {"label_en": "Estimates", "label_bn": "এস্টিমেট", "url": "/estimates"},
            {"label_en": "Privacy & Consent", "label_bn": "সম্মতি ও গোপনীয়তা", "url": "/consent"},
        ],
    },
    "P02": {
        "bn": "টেকনিশিয়ান মোবাইল অ্যাপ",
        "users_bn": "ফিল্ড ও ওয়ার্কশপ টেকনিশিয়ান",
        "volume_bn": "২০০–৪০০ জন সক্রিয় টেকনিশিয়ান",
        # The technician PWA is served by the P01 customer app (:3000).
        # Absolute on purpose: P02 shortcuts must survive being rendered
        # from OTHER portals' /welcome pages (relative /technician 404s there).
        "url": "http://127.0.0.1:3000/technician",
        "port": 3000,
        "is_live": True,
        "is_mobile": True,
        "tech": "Flutter Mobile + Next.js PWA",
        "capabilities_bn": [
            "দৈনিক কাজের সারি ও জিওফেন্স হাজিরা",
            "২৪ ঘণ্টা অফলাইন মোড ও ৩০ সেকেন্ডে সিঙ্ক",
            "সমস্যা নির্ণয় নির্দেশিকা ও ফল্ট কোডিং",
            "গাড়ির যন্ত্রাংশ স্ক্যান ও ব্যবহার",
        ],
        "shortcuts": [
            # Absolute :3000 — these must work from any portal's landing.
            {
                "label_en": "Technician PWA",
                "label_bn": "টেকনিশিয়ান PWA",
                "url": "http://127.0.0.1:3000/technician",
            },
            {
                "label_en": "Day Queue",
                "label_bn": "দৈনিক কিউ",
                "url": "http://127.0.0.1:3000/technician",
            },
            {
                "label_en": "Geofenced Clock-In",
                "label_bn": "জিওফেন্স হাজিরা",
                "url": "http://127.0.0.1:3000/technician",
            },
            {
                "label_en": "Van Stock Scan",
                "label_bn": "ভ্যান স্টক স্ক্যান",
                "url": "http://127.0.0.1:3000/technician",
            },
            {
                "label_en": "Field Dispatch Board",
                "label_bn": "ফিল্ড ডেসপ্যাচ বোর্ড",
                "url": "http://127.0.0.1:8069/odoo",
            },
        ],
    },
    "P03": {
        "bn": "অ্যাডমিন ও সেন্ট্রাল অপারেশনস পোর্টাল",
        "users_bn": "শাখা ও প্রধান কার্যালয় পরিচালনা কর্মী",
        "volume_bn": "১৫০–২৫০ জন অভ্যন্তরীণ কর্মী",
        "url": "http://127.0.0.1:8069/odoo",
        "port": 8069,
        "is_live": True,
        "tech": "Odoo 19 OWL 2",
        "capabilities_bn": [
            "১৫টি বিশেষায়িত ভূমিকা ওয়ার্কস্পেস",
            "ডেসপ্যাচ কনসোল ও রিয়েল-টাইম লাইভ ম্যাপ",
            "শাখা ও ল্যাব ওয়ার্কশপ কন্ট্রোল",
            "৪ বা তার কম ক্লিকে যেকোনো তথ্যে প্রবেশ",
        ],
        "shortcuts": [
            {
                "label_en": "Operations Console",
                "label_bn": "অপারেশনস কনসোল",
                "url": "http://127.0.0.1:8069/odoo",
            },
        ],
    },
    "P04": {
        "bn": "কর্পোরেট ও প্রাতিষ্ঠানিক B2B পোর্টাল",
        "users_bn": "কর্পোরেট প্রতিষ্ঠান ও সরকারি ক্লায়েন্ট",
        "volume_bn": "৫০০–২,০০০ এন্টারপ্রাইজ অ্যাকাউন্ট",
        "url": "http://127.0.0.1:3001/",
        "port": 3001,
        "is_live": True,
        "tech": "Next.js 16.3",
        "capabilities_bn": [
            "বহুস্তরীয় অনুমোদন ব্যবস্থা",
            "প্রাতিষ্ঠানিক ডিভাইস এসেট ব্যবস্থাপনা",
            "বাল্ক সিএসভি সার্ভিস রিকোয়েস্ট",
            "এসএলএ ও ক্রেডিট লিমিট ট্র্যাকিং",
        ],
        "shortcuts": [
            {
                "label_en": "B2B Dashboard",
                "label_bn": "কর্পোরেট ড্যাশবোর্ড",
                "url": "http://127.0.0.1:3001/",
            },
        ],
    },
    "P05": {
        "bn": "ভেন্ডর ও সাপ্লায়ার পোর্টাল",
        "users_bn": "সরবরাহকারী, কুরিয়ার ও রিসাইক্লার",
        "volume_bn": "২০০–৫০০ সক্রিয় সরবরাহকারী",
        "url": "http://127.0.0.1:3007/",
        "port": 3007,
        "is_live": False,
        "tech": "Next.js 16.3",
        "capabilities_bn": [
            "সাপ্লায়ার অনবোর্ডিং ও সনদ যাচাই",
            "আরএফকিউ দরপত্র সাড়া প্রদান",
            "পিও গ্রহণ ও অ্যাডভান্সড শিপিং নোটিশ",
            "চালান ম্যাচিং ও পেমেন্ট স্ট্যাটাস",
        ],
        "shortcuts": [
            {
                "label_en": "Vendor Portal",
                "label_bn": "ভেন্ডর ড্যাশবোর্ড",
                "url": "http://127.0.0.1:3007/",
            },
        ],
    },
    "P06": {
        "bn": "অ্যানালিটিক্স ও এক্সিকিউটিভ ককপিট",
        "users_bn": "ব্যবস্থাপনা ও শীর্ষ নেতৃত্ব",
        "volume_bn": "২৫–৬০ জন পরিচালনা পর্ষদ",
        "url": "http://127.0.0.1:3002/",
        "port": 3002,
        "is_live": False,
        "tech": "Next.js + Superset",
        "capabilities_bn": [
            "এক্সিকিউটিভ পারফরম্যান্স ড্যাশবোর্ড",
            "শাখাভিত্তিক তুলনামূলক পারফরম্যান্স র্যাঙ্কিং",
            "রিয়েল-টাইম অপারেশনাল মেট্রিক্স বোর্ড",
            "স্বয়ংক্রিয় সার্টিফাইড ডেটা বিশ্লেষণ",
        ],
        "shortcuts": [
            {
                "label_en": "Analytics Cockpit",
                "label_bn": "অ্যানালিটিক্স ড্যাশবোর্ড",
                "url": "http://127.0.0.1:3002/",
            },
        ],
    },
    "P07": {
        "bn": "মার্কেটপ্লেস সেলার প্ল্যাটফর্ম",
        "users_bn": "স্বতন্ত্র টেকনিশিয়ান ও লোকাল রিপেয়ার শপ",
        "volume_bn": "৫০০–২,০০০ নিবন্ধিত বিক্রেতা ও কারিগর",
        "url": "http://127.0.0.1:3003/",
        "port": 3003,
        "is_live": False,
        "tech": "Next.js + React Native",
        "capabilities_bn": [
            "কেওয়াইসি ভেরিফিকেশন ও চুক্তি সম্পাদন",
            "যন্ত্রাংশ তালিকা ও স্টক ইনভেন্টরি",
            "কাজের বিজ্ঞপ্তি ও বিডিং প্রক্রিয়া",
            "উপার্জন হিসাব ও ব্যাংক পে-আউট",
        ],
        "shortcuts": [
            {"label_en": "Seller App", "label_bn": "সেলার প্ল্যাটফর্ম", "url": "http://127.0.0.1:3003/"},
        ],
    },
    "P08": {
        "bn": "ব্র্যান্ড পার্টনার পোর্টাল",
        "users_bn": "১৭+ অনুমোদিত বৈশ্বিক ব্র্যান্ড অংশীদার",
        "volume_bn": "৫০–১৫০ ব্র্যান্ড সমন্বয়কারী",
        "url": "http://127.0.0.1:3004/",
        "port": 3004,
        "is_live": False,
        "tech": "Next.js 16.3",
        "capabilities_bn": [
            "ওয়ারেন্টি ক্লেইম পর্যালোচনা ও বাল্ক অনুমোদন",
            "প্রমাণক ছবি ও ল্যাব টেস্ট রিপোর্ট",
            "আর্থিক সমন্বয় ও রেম্যিট্যান্স স্টেটমেন্ট",
            "কনসাইনমেন্ট পার্টস ইনভেন্টরি ও ট্র্যাকিং",
        ],
        "shortcuts": [
            {
                "label_en": "Brand Portal",
                "label_bn": "ব্র্যান্ড ড্যাশবোর্ড",
                "url": "http://127.0.0.1:3004/",
            },
        ],
    },
    "P09": {
        "bn": "লজিস্টিকস ও রাইডার মোবাইল অ্যাপ",
        "users_bn": "পিকআপ-ড্রপ রাইডার ও ট্রিপ সমন্বয়কারী",
        "volume_bn": "৫০–২০০ ডেলিভারি রাইডার",
        "url": "http://127.0.0.1:8069/odoo",
        "port": 8069,
        "is_live": True,
        "is_mobile": True,
        "tech": "Flutter Mobile App",
        "capabilities_bn": [
            "স্মার্ট রুট ও অপ্টিমাইজড ডেলিভারি শিডিউল",
            "বারকোড স্ক্যান ও ওটিপি ভেরিফাইড গ্রহণ",
            "ট্রানজিট সমস্যা ও রিটার্ন রসিদ",
            "জাতীয় পরিচয়পত্র যাচাইকৃত নিরাপদ হস্তান্তর",
        ],
        "shortcuts": [
            {
                "label_en": "Logistics Hub",
                "label_bn": "লজিস্টিকস কন্ট্রোল",
                "url": "http://127.0.0.1:8069/odoo",
            },
        ],
    },
    "P10": {
        "bn": "কন্টাক্ট সেন্টার কনসোল (১৬৭৪৩)",
        "users_bn": "কল সেন্টার প্রতিনিধি ও সুপারভাইজার",
        "volume_bn": "৩০–৮০ জন প্রতিনিধি",
        "url": "http://127.0.0.1:3005/",
        "port": 3005,
        "is_live": False,
        "tech": "Next.js 16.3",
        "capabilities_bn": [
            "ভয়েস, সোশ্যাল মিডিয়া ও চ্যাট একক কিউ",
            "কল আসার সাথে সাথে কাস্টমার-৩৬০ হিস্ট্রি",
            "কথা বলার সময়ই সার্ভিস অর্ডার তৈরি",
            "বাংলা এআই প্রস্তাবিত তাৎক্ষণিক উত্তর",
        ],
        "shortcuts": [
            {
                "label_en": "Agent Queue",
                "label_bn": "কল এজেন্ট কিউ",
                "url": "http://127.0.0.1:3005/",
            },
        ],
    },
    "P11": {
        "bn": "ফিল্ড অডিটর ও আইএসও কোয়ালিটি অ্যাপ",
        "users_bn": "মান নিয়ন্ত্রণ কর্মকর্তা ও আঞ্চলিক নিরীক্ষক",
        "volume_bn": "২০–৬০ জন পরিদর্শক",
        "url": "http://127.0.0.1:8069/odoo",
        "port": 8069,
        "is_live": True,
        "is_mobile": True,
        "tech": "Flutter Mobile App",
        "capabilities_bn": [
            "অডিট চেকলিস্ট ও আইএসও মানদণ্ড পরীক্ষা",
            "অফলাইনে ছবি ও নথিপত্র সংগ্রহ",
            "নগদ টাকা ও শাখা স্টক স্পট চেক",
            "সংশোধনমূলক ব্যবস্থা (CAPA) যাচাই",
        ],
        "shortcuts": [
            {
                "label_en": "QMS Process",
                "label_bn": "আইএসও নিরীক্ষা ব্যবস্থা",
                "url": "http://127.0.0.1:8069/odoo",
            },
        ],
    },
    "P12": {
        "bn": "পার্টনার ও রেফারেল পোর্টাল",
        "users_bn": "অ্যালায়েন্স পার্টনার ও রেফারেল অংশীদার",
        "volume_bn": "১০০–৫০০ অংশীদার",
        "url": "http://127.0.0.1:3006/",
        "port": 3006,
        "is_live": False,
        "tech": "Next.js 16.3",
        "capabilities_bn": [
            "অনলাইন আবেদন ও অনুমোদন",
            "রেফারেল লিংক তৈরি ও ক্লিক ট্র্যাকিং",
            "কমিশন হিসাব ও স্বয়ংক্রিয় পেমেন্ট",
            "মার্কেটিং ব্যানার ও ব্র্যান্ড রিসোর্স",
        ],
        "shortcuts": [
            {
                "label_en": "Partner Console",
                "label_bn": "অংশীদার কনসোল",
                "url": "http://127.0.0.1:3006/",
            },
        ],
    },
}

JOURNEY_META = {
    "J01": {
        "bn": "গ্রাহক অনসাইট মেরামতের বুকিং দেন (P01 → পেমেন্ট)",
        "steps_bn": [
            {
                "actor": "P01 · গ্রাহক",
                "desc": "গ্রাহক বাংলা ইন্টারফেসে পোর্টাল খোলেন, ডিভাইস ও সমস্যা নির্বাচন করেন",
            },
            {
                "actor": "M33 · গ্রাহক মাস্টার",
                "desc": "ওটিপির মাধ্যমে পরিচয় নিশ্চিত — গোল্ডেন রেকর্ড তৈরি বা শনাক্ত",
            },
            {"actor": "M37 · ক্যাটালগ", "desc": "৩ বা তার কম ধাপে অগ্রিম মূল্য ও সময় স্লট নির্ধারিত"},
            {"actor": "M01 · সার্ভিস অর্ডার", "desc": "সার্ভিস অর্ডার তৈরি — ওয়ারেন্টি/এএমসি বা সদস্যপদ মূল্যায়ন"},
            {
                "actor": "M02 · ডেসপ্যাচ",
                "desc": "এআই দ্বারা টেকনিশিয়ান নির্বাচন → অ্যাসাইন → গ্রাহককে ইটিএ প্রদান",
            },
            {
                "actor": "P02 · টেকনিশিয়ান",
                "desc": "কাজ গ্রহণ, জিপিএস নেভিগেশন, ছবি ও মেরামত শেষে ই-স্বাক্ষর",
            },
        ],
    },
    "J02": {
        "bn": "শাখায় সরাসরি এসে মেরামত (কাউন্টার → ল্যাব বেঞ্চ → ডেলিভারি)",
        "steps_bn": [
            {
                "actor": "M04 · ফ্রন্ট ডেস্ক",
                "desc": "টোকেন প্রদান, দ্রুত গ্রহণ ও ডিভাইসের বর্তমান অবস্থার ছবি ধারণ",
            },
            {
                "actor": "M01 · ওয়ার্কশপ অর্ডার",
                "desc": "ওয়ার্কশপ অর্ডার তৈরি — ওয়ারেন্টির বাইরে হলে খরচের প্রাক্কলন",
            },
            {"actor": "M31 · ল্যাব বেঞ্চ", "desc": "এল১/এল২/এল৩ ল্যাব রাউটিং ও শাখা স্টোর থেকে যন্ত্রাংশ গ্রহণ"},
            {
                "actor": "M15 · যন্ত্রাংশ নিয়ন্ত্রণ",
                "desc": "সিরিয়াল নম্বর ট্র্যাকিং ও কনসাইনমেন্ট নীতিমালায় যন্ত্রাংশ ব্যবহার",
            },
            {"actor": "M31 · মান যাচাই", "desc": "মান নিয়ন্ত্রণ প্রোটোকল ও পরীক্ষা শেষে ডেলিভারির জন্য প্রস্তুত"},
            {
                "actor": "M04 · হস্তান্তর",
                "desc": "এসএমএস ও হোয়াটসঅ্যাপে নোটিফিকেশন → পরিচয় যাচাই করে ডিভাইস হস্তান্তর",
            },
        ],
    },
    "J03": {
        "bn": "পিক অ্যান্ড ড্রপ লজিস্টিকস চক্র (বাসা → ল্যাব → গ্রাহক)",
        "steps_bn": [
            {"actor": "P01 · গ্রাহক বুকিং", "desc": "গ্রাহক নির্ধারিত স্লটে পিক অ্যান্ড ড্রপ বুকিং করেন"},
            {"actor": "M03 · কনসাইনমেন্ট", "desc": "মাল্টি-লেগ রুট পরিকল্পনা ও নিরাপত্তা সিল নম্বর বরাদ্দ"},
            {
                "actor": "P09 · লজিস্টিকস রাইডার",
                "desc": "প্রতিটি হস্তান্তরে বারকোড স্ক্যান, ওটিপি ও ছবি সংগ্রহ",
            },
            {"actor": "M31 · কেন্দ্রীয় ল্যাব", "desc": "সুরক্ষিত হেফাজতে ল্যাব বেঞ্চে ডিভাইসের মেরামত সম্পন্ন"},
            {
                "actor": "M03 · নিরাপদ ফেরত",
                "desc": "ওটিপি যাচাই, গ্রাহকের ডিজিটাল স্বাক্ষর ও প্রযোজ্য ক্ষেত্রে সিওডি গ্রহণ",
            },
        ],
    },
    "J04": {
        "bn": "ব্র্যান্ড ওয়ারেন্টি ক্লেইম ও বৈশ্বিক প্রতিপূরণ",
        "steps_bn": [
            {"actor": "M01 · সার্ভিস অর্ডার", "desc": "ওয়ারেন্টি অর্ডার — মূল ব্র্যান্ড কোম্পানি খরচ বহন করবে"},
            {
                "actor": "M09 · স্বয়ংক্রিয় ক্লেইম",
                "desc": "ডেলিভারির পর ৫ মিনিটের মধ্যে স্বয়ংক্রিয় এভিডেন্স প্যাক তৈরি",
            },
            {
                "actor": "M24 · প্রমাণক নথিপত্র",
                "desc": "ছবি, ডায়াগনস্টিক লগ, যন্ত্রাংশের উৎস ও টেকনিশিয়ান সার্টিফিকেশন",
            },
            {"actor": "P08 · ব্র্যান্ড পার্টনার", "desc": "ব্র্যান্ড অংশীদার কর্তৃক পর্যালোচনা ও ক্লেইম অনুমোদন"},
            {"actor": "M20 · প্রাপ্য হিসাব", "desc": "অনুমোদনের সাথে সাথে প্রাপ্য হিসাব ও ইনভয়েস ইস্যু"},
        ],
    },
    "J05": {
        "bn": "কর্পোরেট এএমসি: চুক্তি → প্রতিরোধমূলক শিডিউল → সমন্বিত বিল",
        "steps_bn": [
            {"actor": "M07 · কর্পোরেট সিআরএম", "desc": "চুক্তি চূড়ান্ত → এন্টারপ্রাইজ সার্ভিস টেমপ্লেট নির্বাচন"},
            {"actor": "M08 · চুক্তি ব্যবস্থাপনা", "desc": "১৪টি সার্ভিস ক্যাটাগরি — এসএলএ ও কভারেজ নির্ধারণ"},
            {
                "actor": "M17 · প্রাতিষ্ঠানিক এসেট",
                "desc": "শাখা, বিভাগ ও ব্যবহারকারী ভিত্তিক ডিভাইস এসেট বাল্ক রেজিস্ট্রেশন",
            },
            {
                "actor": "M08 · রুটিন মেইনটেন্যান্স",
                "desc": "প্রতিরোধমূলক রক্ষণাবেক্ষণ শিডিউল থেকে স্বয়ংক্রিয় কাজের আদেশ",
            },
            {
                "actor": "P04 · কর্পোরেট ক্লায়েন্ট",
                "desc": "চুক্তির কভারেজ অনুযায়ী বাল্ক রিকোয়েস্ট যাচাই ও অনুমোদন",
            },
        ],
    },
    "J06": {
        "bn": "যন্ত্রাংশের ঘাটতি → সরবরাহ পূরণ → ভেন্ডর পেমেন্ট",
        "steps_bn": [
            {"actor": "M15 · ইনভেন্টরি অ্যালার্ট", "desc": "যন্ত্রাংশের মজুদ রি-অর্ডার সীমার নিচে নামার সতর্কবার্তা"},
            {"actor": "M43 · চাহিদা পরিকল্পনা", "desc": "ভবিষ্যৎ চাহিদা ও নিরাপত্তা স্টক বিশ্লেষণ করে পরিকল্পনা"},
            {
                "actor": "M16 · রিকুইজিশন ও দরপত্র",
                "desc": "রিকুইজিশন অনুমোদন ও যোগ্য সরবরাহকারীদের নিকট আরএফকিউ প্রেরণ",
            },
            {"actor": "M42 · ভেন্ডর গেট", "desc": "সরবরাহকারীর সক্রিয় স্থিতি ও সনদ নিশ্চিতকরণ"},
            {"actor": "P05 · ভেন্ডর পোর্টাল", "desc": "ভেন্ডর কর্তৃক ক্রয়াদেশ গ্রহণ ও শিপিং নোটিশ প্রেরণ"},
            {"actor": "M41 · ওয়্যারহাউস রিসিভিং", "desc": "বারকোড স্ক্যান গ্রহণ ও ল্যাব কোয়ালিটি গেট পরীক্ষা"},
        ],
    },
    "J07": {
        "bn": "পুরনো ডিভাইস এক্সচেঞ্জ → রিফার্বিশ → অনলাইন পুনঃবিক্রয়",
        "steps_bn": [
            {"actor": "M14 · এক্সচেঞ্জ মূল্যায়ন", "desc": "পোর্টালে স্বয়ংক্রিয় ডিভাইস মূল্যায়ন — ৪৮ ঘণ্টার অফার"},
            {"actor": "M14 · বৈধতা ও নিরাপত্তা", "desc": "আইএমইআই ও সিরিয়াল নম্বর নিরাপত্তা যাচাই"},
            {"actor": "M06 · ডেটা ডিস্ট্রাকশন", "desc": "গ্রাহকের গোপনীয় ডেটা সুরক্ষিতভাবে ডিলিট করার সনদ"},
            {"actor": "M31 · রিফার্বিশমেন্ট ল্যাব", "desc": "ল্যাব ওয়ার্ক অর্ডার, ব্যাটারি ও পারফরম্যান্স ওভারহলিং"},
            {
                "actor": "M14 · গ্রেডিং সার্টিফিকেশন",
                "desc": "এ থেকে ডি গ্রেডিং ও কোয়ালিটি সুপারভাইজার অনুমোদন",
            },
        ],
    },
    "J08": {
        "bn": "মার্কেটপ্লেস কারিগর: অনবোর্ডিং → কাজ সম্পন্ন → উপার্জনের অর্থ পরিশোধ",
        "steps_bn": [
            {"actor": "M12 · কারিগর কেওয়াইসি", "desc": "জাতীয় পরিচয়পত্র, ট্রেড লাইসেন্স ও সনদ যাচাই"},
            {"actor": "M12 · ডিজিটাল চুক্তি", "desc": "ডিজিটাল চুক্তি স্বাক্ষর ও কমিশন হার অনুমোদন"},
            {"actor": "P07 · সেলার পোর্টাল", "desc": "প্রোফাইল তৈরি, সেবার তালিকা ও যন্ত্রাংশ স্টক যুক্তকরণ"},
            {"actor": "M12 · কাজ ব্রডকাস্ট", "desc": "উপযুক্ত সেলারদের কাছে কাজ সম্প্রচার ও বিডিং"},
            {
                "actor": "M02 · কাজের মান তদারকি",
                "desc": "১০০০ফিক্স মানদণ্ড অনুযায়ী কাজ যাচাই ও দ্রুত ব্যাংক পে-আউট",
            },
        ],
    },
    "J09": {
        "bn": "সংবেদনশীল ডেটা রিকভারি (সুরক্ষিত হেফাজত → সফল উদ্ধার সনদ)",
        "steps_bn": [
            {
                "actor": "M06 · কেস ইনটেক",
                "desc": "কেস গ্রহণ, বিশেষজ্ঞ ল্যাবে রাউটিং ও স্টোরেজ ড্রাইভ সিলকরণ",
            },
            {"actor": "M06 · দ্বৈত হেফাজত লেজার", "desc": "দ্বৈত নিয়ন্ত্রণ বিশিষ্ট সুরক্ষিত হেফাজত লেজার"},
            {"actor": "M06 · ল্যাব পরীক্ষা", "desc": "বিনামূল্যে প্রাথমিক ল্যাব টেস্ট ও চূড়ান্ত কোটেশন প্রদান"},
            {
                "actor": "M06 · ক্লিনরুম রিকভারি",
                "desc": "ক্লাস-১০০ ক্লিনরুমে রিকভারি সম্পন্ন ও সুরক্ষা সনদ প্রদান",
            },
        ],
    },
    "J10": {
        "bn": "মাসিক হিসাব সমাপনী → মূসক ৯.১ ভ্যাট রিটার্ন দাখিল",
        "steps_bn": [
            {"actor": "M19 · হিসাব সমাপনী", "desc": "৫৩টি শাখা জুড়ে ৩ দিনের ফাইন্যান্সিয়াল ক্লোজিং কনসোল"},
            {"actor": "M50 · ক্যাশ রিকনসিলিয়েশন", "desc": "শাখা কাউন্টার ক্যাশ ও রাইডার সিওডি ফান্ড একত্রীকরণ"},
            {
                "actor": "M19 · আর্থিক বিবরণী",
                "desc": "লাভ-ক্ষতি, ব্যালেন্স শিট ও ক্যাশ ফ্লো দ্বিভাষিক প্রতিবেদন",
            },
            {
                "actor": "M51 · মূসক ও ভ্যাট রিটার্ন",
                "desc": "মূসক রেজিস্টার, ৯.১ রিটার্ন তৈরি ও এ-চালান স্বয়ংক্রিয় জেনারেশন",
            },
        ],
    },
}


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    portals_out = []
    for p in registry.get("portals", []):
        pid = p["id"]
        meta = PORTAL_META.get(pid, {})
        portals_out.append(
            {
                "id": pid,
                "en": p["name"],
                "bn": meta.get("bn", p["name"]),
                "users": p.get("users", ""),
                "users_bn": meta.get("users_bn", p.get("users", "")),
                "volume": p.get("volume", ""),
                "volume_bn": meta.get("volume_bn", p.get("volume", "")),
                "url": meta.get("url", "/"),
                "port": meta.get("port", 3010),
                "is_live": meta.get("is_live", False),
                "is_mobile": meta.get("is_mobile", False),
                "tech": meta.get("tech", p.get("tech", "")),
                "capabilities": p.get("capabilities", [])[:4],
                "capabilities_bn": meta.get("capabilities_bn", p.get("capabilities", [])[:4]),
                "shortcuts": meta.get("shortcuts", []),
            }
        )

    journeys_out = []
    for j in registry.get("journeys", []):
        jid = j["id"]
        jmeta = JOURNEY_META.get(jid, {})
        steps_out = []
        raw_steps = j.get("steps", [])[:6]
        meta_steps = jmeta.get("steps_bn", [])
        for idx, s in enumerate(raw_steps):
            ms = meta_steps[idx] if idx < len(meta_steps) else {}
            steps_out.append(
                {
                    "actor": s.get("actor", ""),
                    "actor_bn": ms.get("actor", s.get("actor", "")),
                    "desc": s.get("desc", ""),
                    "desc_bn": ms.get("desc", s.get("desc", "")),
                }
            )
        journeys_out.append(
            {
                "id": jid,
                "en": j["en"],
                "bn": jmeta.get("bn", j.get("bn", "")),
                "steps": steps_out,
            }
        )

    landing = {
        "$description": "Landing/marketing shell data — PP5. Generated from "
        "contracts/nav/registry.json (portals + journeys only; "
        "navigation, not data). Production bilingual with deep links.",
        "portals": portals_out,
        "journeys": journeys_out,
        "counts": {
            "portals": len(portals_out),
            "journeys": len(journeys_out),
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(landing, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(
        f"landing artefact: {landing['counts']['portals']} portals, "
        f"{landing['counts']['journeys']} journeys -> {OUT.relative_to(REPO)} "
        f"({size_kb:.1f} KB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
