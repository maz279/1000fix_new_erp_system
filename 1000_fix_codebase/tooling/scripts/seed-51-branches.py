#!/usr/bin/env python3
"""
seed-51-branches.py — Milestone R08-M05-T01:
Extend branch master data from the 6 seeded to all 51+ (53 service centres)
spanning all 8 administrative divisions of Bangladesh.

Adheres to:
- MD-003 (Branch and Service Centre Master)
- RL-004 (Rollout and Branch Wave Deployment Plan)
- AS-03 (Operating Unit multi-branch isolation)
- BRN-01 (Mandatory bilingual name: name_bn)
- BRN-02 (Latitude 20.5-26.7, Longitude 88.0-92.7)

Updates:
1. PostgreSQL 17 DEV database (`fix_branch` and `operating_unit` tables) - and
   links the six pilot-era alias branches (HQ, PC-01..PC-05) to their real
   register branches.
2. Optionally (`--out PATH`) a JSON export of the seeded register.

It NEVER writes under migrations/: migrations/extracts/ is the Wave-1 pilot
rehearsal's checksummed extract set (6 pilot branches, MIG-02); overwriting
branches_extract.json with the 53-centre register corrupts that rehearsal.
`--out` refuses any path inside migrations/.

Usage:
  py tooling/scripts/seed-51-branches.py --dry-run     # plan only: no DB, no files
  py tooling/scripts/seed-51-branches.py [--out PATH]  # seed the DEV database
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5433"))
DB_NAME = os.environ.get("PGDATABASE", "fix_dev")
DB_USER = os.environ.get("PGUSER", "fix")
DB_PASS = os.environ.get("PGPASSWORD", "change-me-dev-only")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# Off-limits: the Wave-1 rehearsal's checksummed extracts live here
MIGRATIONS_DIR = ROOT_DIR / "migrations"

# Authoritative 53 Service Centres Register
BRANCH_REGISTER = [
    # Dhaka Division (Wave 1 Pilot & Wave 2)
    {
        "sc": "SC-001",
        "code": "BR-0001",
        "alias": "HQ",
        "name": "1000FiX Shewrapara HQ & Flagship",
        "name_bn": "শেওড়াপাড়া প্রধান কার্যালয় ও ফ্ল্যাগশিপ",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Mirpur, Dhaka",
        "lat": 23.7900,
        "lon": 90.3700,
        "phone": "09644-300600",
        "wave": 1,
        "pilot": True,
    },
    {
        "sc": "SC-002",
        "code": "BR-0002",
        "alias": "PC-01A",
        "name": "Motijheel Service Center",
        "name_bn": "মতিঝিল সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Motijheel, Dhaka",
        "lat": 23.7330,
        "lon": 90.4170,
        "phone": "09644-300601",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-003",
        "code": "BR-0003",
        "alias": "PC-01B",
        "name": "Elephant Road Service Center",
        "name_bn": "এলিফ্যান্ট রোড সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Elephant Road, Dhaka",
        "lat": 23.7390,
        "lon": 90.3850,
        "phone": "09644-300602",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-004",
        "code": "BR-0004",
        "alias": "PC-02",
        "name": "Uttara Service Center",
        "name_bn": "উত্তরা সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Uttara, Dhaka",
        "lat": 23.8720,
        "lon": 90.3980,
        "phone": "09644-300603",
        "wave": 1,
        "pilot": True,
    },
    {
        "sc": "SC-005",
        "code": "BR-0005",
        "alias": "PC-01C",
        "name": "IDB Bhaban Service Center",
        "name_bn": "আইডিবি ভবন সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Agargaon, Dhaka",
        "lat": 23.7770,
        "lon": 90.3800,
        "phone": "09644-300604",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-006",
        "code": "BR-0006",
        "alias": "PC-01D",
        "name": "Bashundhara City Service Center",
        "name_bn": "বসুন্ধরা সিটি সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Panthapath, Dhaka",
        "lat": 23.7510,
        "lon": 90.3910,
        "phone": "09644-300605",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-007",
        "code": "BR-0007",
        "alias": "PC-01E",
        "name": "Farmgate Service Station",
        "name_bn": "ফার্মগেট সার্ভিস স্টেশন",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Farmgate, Dhaka",
        "lat": 23.7560,
        "lon": 90.3870,
        "phone": "09644-300606",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-008",
        "code": "BR-0008",
        "alias": "PC-01F",
        "name": "Agargaon Service Station",
        "name_bn": "আগারগাঁও সার্ভিস স্টেশন",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Agargaon, Dhaka",
        "lat": 23.7760,
        "lon": 90.3780,
        "phone": "09644-300607",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-009",
        "code": "BR-0009",
        "alias": "PC-01G",
        "name": "Multiplan Centre Service Center",
        "name_bn": "মাল্টিপ্ল্যান সেন্টার সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Elephant Road, Dhaka",
        "lat": 23.7400,
        "lon": 90.3860,
        "phone": "09644-300608",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-010",
        "code": "BR-0010",
        "alias": "PC-01H",
        "name": "Gazipur Service Center",
        "name_bn": "গাজীপুর সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Gazipur",
        "city": "Gazipur",
        "lat": 23.9980,
        "lon": 90.4200,
        "phone": "09644-300609",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-011",
        "code": "BR-0011",
        "alias": "PC-01I",
        "name": "Narayanganj Service Center",
        "name_bn": "নারায়ণগঞ্জ সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Narayanganj",
        "city": "Narayanganj",
        "lat": 23.6230,
        "lon": 90.5000,
        "phone": "09644-300610",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-012",
        "code": "BR-0012",
        "alias": "PC-01J",
        "name": "Savar Service Center",
        "name_bn": "সাভার সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Dhaka",
        "city": "Savar",
        "lat": 23.8440,
        "lon": 90.2580,
        "phone": "09644-300611",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-013",
        "code": "BR-0013",
        "alias": "PC-01K",
        "name": "Narsingdi Service Center",
        "name_bn": "নরসিংদী সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Narsingdi",
        "city": "Narsingdi",
        "lat": 23.9200,
        "lon": 90.7200,
        "phone": "09644-300612",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-014",
        "code": "BR-0014",
        "alias": "PC-01L",
        "name": "Tangail Service Center",
        "name_bn": "টাঙ্গাইল সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Tangail",
        "city": "Tangail",
        "lat": 24.2500,
        "lon": 89.9200,
        "phone": "09644-300613",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-015",
        "code": "BR-0015",
        "alias": "PC-01M",
        "name": "Manikganj Service Center",
        "name_bn": "মানিকগঞ্জ সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Manikganj",
        "city": "Manikganj",
        "lat": 23.8600,
        "lon": 90.0000,
        "phone": "09644-300614",
        "wave": 2,
        "pilot": False,
    },
    # Mymensingh Division (Wave 4)
    {
        "sc": "SC-016",
        "code": "BR-0016",
        "alias": "PC-06A",
        "name": "Mymensingh City Service Center",
        "name_bn": "ময়মনসিংহ সিটি সার্ভিস সেন্টার",
        "div": "MYM",
        "district": "Mymensingh",
        "city": "Mymensingh",
        "lat": 24.7500,
        "lon": 90.4000,
        "phone": "09644-300615",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-017",
        "code": "BR-0017",
        "alias": "PC-06B",
        "name": "Jamalpur Service Center",
        "name_bn": "জামালপুর সার্ভিস সেন্টার",
        "div": "MYM",
        "district": "Jamalpur",
        "city": "Jamalpur",
        "lat": 24.9200,
        "lon": 89.9400,
        "phone": "09644-300616",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-018",
        "code": "BR-0018",
        "alias": "PC-06C",
        "name": "Kishoreganj Service Center",
        "name_bn": "কিশোরগঞ্জ সার্ভিস সেন্টার",
        "div": "MYM",
        "district": "Kishoreganj",
        "city": "Kishoreganj",
        "lat": 24.4400,
        "lon": 90.7800,
        "phone": "09644-300617",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-019",
        "code": "BR-0019",
        "alias": "PC-06D",
        "name": "Netrokona Service Center",
        "name_bn": "নেত্রকোণা সার্ভিস সেন্টার",
        "div": "MYM",
        "district": "Netrokona",
        "city": "Netrokona",
        "lat": 24.8800,
        "lon": 90.7300,
        "phone": "09644-300618",
        "wave": 4,
        "pilot": False,
    },
    # Rajshahi Division (Wave 3)
    {
        "sc": "SC-020",
        "code": "BR-0020",
        "alias": "PC-05A",
        "name": "Rajshahi City Service Center",
        "name_bn": "রাজশাহী সিটি সার্ভিস সেন্টার",
        "div": "RAJ",
        "district": "Rajshahi",
        "city": "Rajshahi",
        "lat": 24.3700,
        "lon": 88.6000,
        "phone": "09644-300619",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-021",
        "code": "BR-0021",
        "alias": "PC-05B",
        "name": "Bogura Service Center",
        "name_bn": "বগুড়া সার্ভিস সেন্টার",
        "div": "RAJ",
        "district": "Bogura",
        "city": "Bogura",
        "lat": 24.8500,
        "lon": 89.3700,
        "phone": "09644-300620",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-022",
        "code": "BR-0022",
        "alias": "PC-05C",
        "name": "Pabna Service Center",
        "name_bn": "পাবনা সার্ভিস সেন্টার",
        "div": "RAJ",
        "district": "Pabna",
        "city": "Pabna",
        "lat": 24.0100,
        "lon": 89.2400,
        "phone": "09644-300621",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-023",
        "code": "BR-0023",
        "alias": "PC-05D",
        "name": "Sirajganj Service Center",
        "name_bn": "সিরাজগঞ্জ সার্ভিস সেন্টার",
        "div": "RAJ",
        "district": "Sirajganj",
        "city": "Sirajganj",
        "lat": 24.4500,
        "lon": 89.7100,
        "phone": "09644-300622",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-024",
        "code": "BR-0024",
        "alias": "PC-05E",
        "name": "Natore Service Center",
        "name_bn": "নাটোর সার্ভিস সেন্টার",
        "div": "RAJ",
        "district": "Natore",
        "city": "Natore",
        "lat": 24.4100,
        "lon": 89.0000,
        "phone": "09644-300623",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-025",
        "code": "BR-0025",
        "alias": "PC-05F",
        "name": "Chapai Nawabganj Service Center",
        "name_bn": "চাঁপাইনবাবগঞ্জ সার্ভিস সেন্টার",
        "div": "RAJ",
        "district": "Chapai Nawabganj",
        "city": "Chapai Nawabganj",
        "lat": 24.5900,
        "lon": 88.2700,
        "phone": "09644-300624",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-026",
        "code": "BR-0026",
        "alias": "PC-05G",
        "name": "Naogaon Service Center",
        "name_bn": "নওগাঁ সার্ভিস সেন্টার",
        "div": "RAJ",
        "district": "Naogaon",
        "city": "Naogaon",
        "lat": 24.8100,
        "lon": 88.9500,
        "phone": "09644-300625",
        "wave": 3,
        "pilot": False,
    },
    # Rangpur Division (Wave 4)
    {
        "sc": "SC-027",
        "code": "BR-0027",
        "alias": "PC-07A",
        "name": "Rangpur City Service Center",
        "name_bn": "রংপুর সিটি সার্ভিস সেন্টার",
        "div": "RAN",
        "district": "Rangpur",
        "city": "Rangpur",
        "lat": 25.7500,
        "lon": 89.2500,
        "phone": "09644-300626",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-028",
        "code": "BR-0028",
        "alias": "PC-07B",
        "name": "Dinajpur Service Center",
        "name_bn": "দিনাজপুর সার্ভিস সেন্টার",
        "div": "RAN",
        "district": "Dinajpur",
        "city": "Dinajpur",
        "lat": 25.6300,
        "lon": 88.6400,
        "phone": "09644-300627",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-029",
        "code": "BR-0029",
        "alias": "PC-07C",
        "name": "Gaibandha Service Center",
        "name_bn": "গাইবান্ধা সার্ভিস সেন্টার",
        "div": "RAN",
        "district": "Gaibandha",
        "city": "Gaibandha",
        "lat": 25.3300,
        "lon": 89.5400,
        "phone": "09644-300628",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-030",
        "code": "BR-0030",
        "alias": "PC-07D",
        "name": "Nilphamari Service Center",
        "name_bn": "নীলফামারী সার্ভিস সেন্টার",
        "div": "RAN",
        "district": "Nilphamari",
        "city": "Nilphamari",
        "lat": 25.9300,
        "lon": 88.8500,
        "phone": "09644-300629",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-031",
        "code": "BR-0031",
        "alias": "PC-07E",
        "name": "Thakurgaon Service Center",
        "name_bn": "ঠাকুরগাঁও সার্ভিস সেন্টার",
        "div": "RAN",
        "district": "Thakurgaon",
        "city": "Thakurgaon",
        "lat": 26.0300,
        "lon": 88.4700,
        "phone": "09644-300630",
        "wave": 4,
        "pilot": False,
    },
    # Khulna Division (Wave 3)
    {
        "sc": "SC-032",
        "code": "BR-0032",
        "alias": "PC-04A",
        "name": "Khulna City Service Center",
        "name_bn": "খুলনা সিটি সার্ভিস সেন্টার",
        "div": "KHU",
        "district": "Khulna",
        "city": "Khulna",
        "lat": 22.8200,
        "lon": 89.5500,
        "phone": "09644-300631",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-033",
        "code": "BR-0033",
        "alias": "PC-04B",
        "name": "Jashore Service Center",
        "name_bn": "যশোর সার্ভিস সেন্টার",
        "div": "KHU",
        "district": "Jashore",
        "city": "Jashore",
        "lat": 23.1700,
        "lon": 89.2100,
        "phone": "09644-300632",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-034",
        "code": "BR-0034",
        "alias": "PC-04C",
        "name": "Satkhira Service Center",
        "name_bn": "সাতক্ষীরা সার্ভিস সেন্টার",
        "div": "KHU",
        "district": "Satkhira",
        "city": "Satkhira",
        "lat": 22.7200,
        "lon": 89.0800,
        "phone": "09644-300633",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-035",
        "code": "BR-0035",
        "alias": "PC-04D",
        "name": "Narail Service Center",
        "name_bn": "নড়াইল সার্ভিস সেন্টার",
        "div": "KHU",
        "district": "Narail",
        "city": "Narail",
        "lat": 23.1700,
        "lon": 89.5000,
        "phone": "09644-300634",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-036",
        "code": "BR-0036",
        "alias": "PC-04E",
        "name": "Kushtia Service Center",
        "name_bn": "কুষ্টিয়া সার্ভিস সেন্টার",
        "div": "KHU",
        "district": "Kushtia",
        "city": "Kushtia",
        "lat": 23.9000,
        "lon": 89.1200,
        "phone": "09644-300635",
        "wave": 3,
        "pilot": False,
    },
    # Barishal Division (Wave 4)
    {
        "sc": "SC-037",
        "code": "BR-0037",
        "alias": "PC-08A",
        "name": "Barishal City Service Center",
        "name_bn": "বরিশাল সিটি সার্ভিস সেন্টার",
        "div": "BAR",
        "district": "Barishal",
        "city": "Barishal",
        "lat": 22.7000,
        "lon": 90.3700,
        "phone": "09644-300636",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-038",
        "code": "BR-0038",
        "alias": "PC-08B",
        "name": "Patuakhali Service Center",
        "name_bn": "পটুয়াখালী সার্ভিস সেন্টার",
        "div": "BAR",
        "district": "Patuakhali",
        "city": "Patuakhali",
        "lat": 22.3500,
        "lon": 90.3300,
        "phone": "09644-300637",
        "wave": 4,
        "pilot": False,
    },
    {
        "sc": "SC-039",
        "code": "BR-0039",
        "alias": "PC-08C",
        "name": "Bhola Service Center",
        "name_bn": "ভোলা সার্ভিস সেন্টার",
        "div": "BAR",
        "district": "Bhola",
        "city": "Bhola",
        "lat": 22.6800,
        "lon": 90.6500,
        "phone": "09644-300638",
        "wave": 4,
        "pilot": False,
    },
    # Sylhet Division (Wave 1 Pilot & Wave 3)
    {
        "sc": "SC-040",
        "code": "BR-0040",
        "alias": "PC-05",
        "name": "Sylhet Zindabazar Service Center",
        "name_bn": "সিলেট জিন্দাবাজার সার্ভিস সেন্টার",
        "div": "SYL",
        "district": "Sylhet",
        "city": "Zindabazar, Sylhet",
        "lat": 24.8900,
        "lon": 91.8700,
        "phone": "09644-300639",
        "wave": 1,
        "pilot": True,
    },
    {
        "sc": "SC-041",
        "code": "BR-0041",
        "alias": "PC-03B",
        "name": "Moulvibazar Service Center",
        "name_bn": "মৌলভীবাজার সার্ভিস সেন্টার",
        "div": "SYL",
        "district": "Moulvibazar",
        "city": "Moulvibazar",
        "lat": 24.4800,
        "lon": 91.7700,
        "phone": "09644-300640",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-042",
        "code": "BR-0042",
        "alias": "PC-03C",
        "name": "Sunamganj Service Center",
        "name_bn": "সুনামগঞ্জ সার্ভিস সেন্টার",
        "div": "SYL",
        "district": "Sunamganj",
        "city": "Sunamganj",
        "lat": 25.0700,
        "lon": 91.4000,
        "phone": "09644-300641",
        "wave": 3,
        "pilot": False,
    },
    # Chattogram Division (Wave 1 Pilot & Wave 3)
    {
        "sc": "SC-043",
        "code": "BR-0043",
        "alias": "PC-04",
        "name": "Chattogram Agrabad Service Center",
        "name_bn": "চট্টগ্রাম আগ্রাবাদ সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Chattogram",
        "city": "Agrabad, Chattogram",
        "lat": 22.3300,
        "lon": 91.8100,
        "phone": "09644-300642",
        "wave": 1,
        "pilot": True,
    },
    {
        "sc": "SC-044",
        "code": "BR-0044",
        "alias": "PC-02B",
        "name": "Chattogram Nasirabad Service Center",
        "name_bn": "চট্টগ্রাম নাসিরাবাদ সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Chattogram",
        "city": "Nasirabad, Chattogram",
        "lat": 22.3600,
        "lon": 91.8200,
        "phone": "09644-300643",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-045",
        "code": "BR-0045",
        "alias": "PC-02C",
        "name": "Cox's Bazar Service Center",
        "name_bn": "কক্সবাজার সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Cox's Bazar",
        "city": "Cox's Bazar",
        "lat": 21.4300,
        "lon": 91.9800,
        "phone": "09644-300644",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-046",
        "code": "BR-0046",
        "alias": "PC-02D",
        "name": "Cumilla Service Center",
        "name_bn": "কুমিল্লা সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Cumilla",
        "city": "Cumilla",
        "lat": 23.4600,
        "lon": 91.1800,
        "phone": "09644-300645",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-047",
        "code": "BR-0047",
        "alias": "PC-02E",
        "name": "Feni Service Center",
        "name_bn": "ফেনী সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Feni",
        "city": "Feni",
        "lat": 23.0100,
        "lon": 91.4000,
        "phone": "09644-300646",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-048",
        "code": "BR-0048",
        "alias": "PC-02F",
        "name": "Noakhali Service Center",
        "name_bn": "নোয়াখালী সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Noakhali",
        "city": "Maijdee, Noakhali",
        "lat": 22.8700,
        "lon": 91.1000,
        "phone": "09644-300647",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-049",
        "code": "BR-0049",
        "alias": "PC-02G",
        "name": "Chandpur Service Center",
        "name_bn": "চাঁদপুর সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Chandpur",
        "city": "Chandpur",
        "lat": 23.2300,
        "lon": 90.6600,
        "phone": "09644-300648",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-050",
        "code": "BR-0050",
        "alias": "PC-02H",
        "name": "Lakshmipur Service Center",
        "name_bn": "লক্ষ্মীপুর সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Lakshmipur",
        "city": "Lakshmipur",
        "lat": 22.9400,
        "lon": 90.8400,
        "phone": "09644-300649",
        "wave": 3,
        "pilot": False,
    },
    {
        "sc": "SC-051",
        "code": "BR-0051",
        "alias": "PC-02I",
        "name": "Brahmanbaria Service Center",
        "name_bn": "ব্রাহ্মণবাড়িয়া সার্ভিস সেন্টার",
        "div": "CTG",
        "district": "Brahmanbaria",
        "city": "Brahmanbaria",
        "lat": 23.9600,
        "lon": 91.1100,
        "phone": "09644-300650",
        "wave": 3,
        "pilot": False,
    },
    # Greater Dhaka Division Outlying (Wave 2)
    {
        "sc": "SC-052",
        "code": "BR-0052",
        "alias": "PC-01N",
        "name": "Faridpur Service Center",
        "name_bn": "ফরিদপুর সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Faridpur",
        "city": "Faridpur",
        "lat": 23.6000,
        "lon": 89.8400,
        "phone": "09644-300651",
        "wave": 2,
        "pilot": False,
    },
    {
        "sc": "SC-053",
        "code": "BR-0053",
        "alias": "PC-01O",
        "name": "Madaripur Service Center",
        "name_bn": "মাদারীপুর সার্ভিস সেন্টার",
        "div": "DHA",
        "district": "Madaripur",
        "city": "Madaripur",
        "lat": 23.1700,
        "lon": 90.1800,
        "phone": "09644-300652",
        "wave": 2,
        "pilot": False,
    },
]

# Additional pilot aliases mapping
PILOT_ALIAS_MAPPING = {
    "HQ": "BR-0001",
    "PC-01": "BR-0002",
    "PC-02": "BR-0004",
    "PC-03": "BR-0001",
    "PC-04": "BR-0043",
    "PC-05": "BR-0040",
}


def alias_legacy_reference(alias_code: str, real_code: str) -> str:
    """MIG-03 reference recording which real branch a pilot alias resolves to."""
    return f"BR:PILOT_ALIAS:{alias_code}->{real_code}"


def link_pilot_aliases(cur, mapping: dict[str, str]) -> list[dict]:
    """Point every pilot alias branch (the six pilot-era codes) at its real
    register branch: the alias takes the real branch's operating unit (the
    AS-03 isolation unit - records keyed to the alias land in the real
    branch's OU) and zone, and its legacy_reference names the real code.

    A real branch missing from fix_branch is an error, not a silent skip: the
    register upsert above must have created it. Returns one row per alias
    linked; an alias code absent from fix_branch is reported, not invented."""
    linked: list[dict] = []
    for alias_code, real_code in mapping.items():
        cur.execute(
            "SELECT id, operating_unit_id, zone_id FROM fix_branch WHERE code = %s;",
            (real_code,),
        )
        real_row = cur.fetchone()
        if not real_row:
            raise RuntimeError(
                f"pilot alias {alias_code!r} maps to {real_code!r}, which is not in fix_branch"
            )
        real_id, real_ou_id, real_zone_id = real_row
        cur.execute("SELECT id FROM fix_branch WHERE code = %s;", (alias_code,))
        alias_row = cur.fetchone()
        if not alias_row:
            logger.info(f"Pilot alias {alias_code} not present in fix_branch; nothing to link")
            continue
        if alias_row[0] == real_id:
            continue  # the alias code IS the real branch row
        cur.execute(
            """UPDATE fix_branch
               SET active = true,
                   operating_unit_id = %s,
                   zone_id = %s,
                   legacy_reference = %s
               WHERE id = %s;""",
            (
                real_ou_id,
                real_zone_id,
                alias_legacy_reference(alias_code, real_code),
                alias_row[0],
            ),
        )
        linked.append(
            {
                "alias_code": alias_code,
                "alias_id": alias_row[0],
                "real_code": real_code,
                "real_id": real_id,
                "operating_unit_id": real_ou_id,
            }
        )
        logger.info(f"Linked pilot alias {alias_code} -> {real_code} (OU {real_ou_id})")
    return linked


def get_db():
    import psycopg2  # only a real (non-dry) run needs the driver

    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )


def seed_operating_units_and_branches(conn):
    with conn.cursor() as cur:
        # 1. Resolve company_id and entity_id
        cur.execute("SELECT id, company_id FROM fix_entity WHERE id = 1 LIMIT 1;")
        entity_row = cur.fetchone()
        if not entity_row:
            cur.execute("SELECT id, company_id FROM fix_entity LIMIT 1;")
            entity_row = cur.fetchone()

        entity_id = entity_row[0] if entity_row else 1
        company_id = entity_row[1] if entity_row and entity_row[1] else 2

        cur.execute("SELECT partner_id FROM res_company WHERE id = %s;", (company_id,))
        p_row = cur.fetchone()
        company_partner_id = p_row[0] if p_row and p_row[0] else 1

        logger.info(
            f"Target Entity ID: {entity_id}, Company ID: {company_id}, Partner ID: {company_partner_id}"
        )

        # 2. Ensure zones exist for all 8 divisions
        zone_codes = {
            "DHA": ("ZN-001", "Dhaka Metro & Greater Zone"),
            "CTG": ("ZN-002", "Chattogram Division Zone"),
            "SYL": ("ZN-003", "Sylhet Division Zone"),
            "KHU": ("ZN-004", "Khulna Division Zone"),
            "RAJ": ("ZN-005", "Rajshahi Division Zone"),
            "RAN": ("ZN-006", "Rangpur Division Zone"),
            "BAR": ("ZN-007", "Barishal Division Zone"),
            "MYM": ("ZN-008", "Mymensingh Division Zone"),
        }
        zone_id_map = {}
        for div, (zcode, zname) in zone_codes.items():
            cur.execute("SELECT id FROM fix_zone WHERE code = %s;", (zcode,))
            zrow = cur.fetchone()
            if zrow:
                zone_id_map[div] = zrow[0]
            else:
                cur.execute(
                    "INSERT INTO fix_zone (code, name, active) VALUES (%s, %s, true) RETURNING id;",
                    (zcode, zname),
                )
                zone_id_map[div] = cur.fetchone()[0]

        # 3. Seed operating units and branches for all 53 service centres
        seeded_branches = []
        for b in BRANCH_REGISTER:
            ou_code, ou_name, email, legacy_ref = branch_identity(b)

            # Create / resolve Operating Unit (AS-03)
            cur.execute("SELECT id FROM operating_unit WHERE code = %s;", (ou_code,))
            ou_row = cur.fetchone()
            if ou_row:
                ou_id = ou_row[0]
            else:
                cur.execute(
                    """INSERT INTO operating_unit (code, name, company_id, partner_id, active)
                       VALUES (%s, %s, %s, %s, true) RETURNING id;""",
                    (ou_code, ou_name, company_id, company_partner_id),
                )
                ou_id = cur.fetchone()[0]

            zone_id = zone_id_map.get(b["div"], 1)

            # Check if branch already exists by code or sc
            cur.execute(
                "SELECT id FROM fix_branch WHERE code = %s OR legacy_reference = %s;",
                (b["code"], legacy_ref),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    """UPDATE fix_branch
                       SET name = %s, name_bn = %s, operating_unit_id = %s,
                           zone_id = %s, phone = %s, email = %s, legacy_reference = %s,
                           active = true
                       WHERE id = %s;""",
                    (
                        b["name"],
                        b["name_bn"],
                        ou_id,
                        zone_id,
                        b["phone"],
                        email,
                        legacy_ref,
                        existing[0],
                    ),
                )
                branch_id = existing[0]
            else:
                cur.execute(
                    """INSERT INTO fix_branch (
                           code, name, name_bn, entity_id, operating_unit_id,
                           zone_id, phone, email, legacy_reference, active
                       ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, true) RETURNING id;""",
                    (
                        b["code"],
                        b["name"],
                        b["name_bn"],
                        entity_id,
                        ou_id,
                        zone_id,
                        b["phone"],
                        email,
                        legacy_ref,
                    ),
                )
                branch_id = cur.fetchone()[0]

            seeded_branches.append(
                {
                    "id": branch_id,
                    "sc": b["sc"],
                    "code": b["code"],
                    "name": b["name"],
                    "name_bn": b["name_bn"],
                    "division": b["div"],
                    "district": b["district"],
                    "city": b["city"],
                    "latitude": b["lat"],
                    "longitude": b["lon"],
                    "phone": b["phone"],
                    "email": email,
                    "operating_unit_code": ou_code,
                    "operating_unit_id": ou_id,
                    "legacy_reference": legacy_ref,
                    "wave": b["wave"],
                    "pilot": b["pilot"],
                }
            )

        # Ensure pilot aliases point to their real branches
        link_pilot_aliases(cur, PILOT_ALIAS_MAPPING)

        conn.commit()
        logger.info(
            f"Successfully seeded/updated {len(seeded_branches)} branches in PostgreSQL 17."
        )
        return seeded_branches


def branch_identity(b: dict) -> tuple[str, str, str, str]:
    """(operating-unit code, operating-unit name, email, legacy reference)."""
    return (
        f"OU-{b['code'].replace('-', '')}",
        f"OU {b['name']}",
        f"service.{b['sc'].lower()}@1000fix.com",
        f"BR:SC:{b['sc']}",
    )


def resolve_output_path(path: Path) -> Path:
    """The export path, refusing anything inside migrations/."""
    resolved = path.resolve()
    if resolved == MIGRATIONS_DIR.resolve() or MIGRATIONS_DIR.resolve() in resolved.parents:
        raise ValueError(
            f"refusing to write {resolved}: migrations/ holds the Wave-1 rehearsal's "
            "checksummed extracts (6 pilot branches); export the register elsewhere"
        )
    return resolved


def export_branch_register(branches: list[dict], out_path: Path) -> Path:
    target = resolve_output_path(out_path)
    export_data = [
        {
            "code": b["code"],
            "sc_id": b["sc"],
            "name": b["name"],
            "name_bn": b["name_bn"],
            "division": b["division"],
            "district": b["district"],
            "latitude": b["latitude"],
            "longitude": b["longitude"],
            "phone": b["phone"],
            "email": b["email"],
            "operating_unit_code": b["operating_unit_code"],
            "legacy_reference": b["legacy_reference"],
            "wave": b["wave"],
            "pilot": b["pilot"],
        }
        for b in branches
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(export_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    logger.info(f"Exported {len(export_data)} branches to {target}")
    return target


def plan(out_path: Path | None) -> int:
    """Dry run: validate the register and alias mapping; no DB, no files."""
    codes = [b["code"] for b in BRANCH_REGISTER]
    problems = []
    if len(set(codes)) != len(codes):
        problems.append("duplicate branch codes in BRANCH_REGISTER")
    for alias_code, real_code in PILOT_ALIAS_MAPPING.items():
        if real_code not in codes:
            problems.append(f"pilot alias {alias_code} maps to {real_code}, not in the register")
    for b in BRANCH_REGISTER:
        if not (20.5 <= b["lat"] <= 26.7 and 88.0 <= b["lon"] <= 92.7):
            problems.append(f"{b['code']}: coordinates outside Bangladesh (BRN-02)")
        if not b.get("name_bn"):
            problems.append(f"{b['code']}: missing name_bn (BRN-01)")
    if out_path is not None:
        try:
            print(f"DRY RUN: would export the register to {resolve_output_path(out_path)}")
        except ValueError as exc:
            problems.append(str(exc))
    divisions = sorted({b["div"] for b in BRANCH_REGISTER})
    print(
        f"DRY RUN: would upsert {len(BRANCH_REGISTER)} branches / operating units across "
        f"{len(divisions)} divisions and link {len(PILOT_ALIAS_MAPPING)} pilot aliases "
        f"({', '.join(f'{a}->{r}' for a, r in PILOT_ALIAS_MAPPING.items())}). "
        "No database connection made; no file written."
    )
    for problem in problems:
        print(f"  PROBLEM: {problem}")
    for question in alias_data_questions():
        print(f"  DATA QUESTION: {question}")
    return 1 if problems else 0


def alias_data_questions() -> list[str]:
    """Pilot aliases whose target is not a Wave-1 pilot centre of the register.

    Every pilot alias names a Wave-1 pilot centre; a target that is a Wave-2,
    non-pilot centre (e.g. PC-01 Dhanmondi -> BR-0002 Motijheel; the register
    has no Dhanmondi centre) is surfaced for the data owner - not silently
    re-pointed, because the register itself cannot say which centre is right."""
    by_code = {b["code"]: b for b in BRANCH_REGISTER}
    questions = []
    for alias_code, real_code in PILOT_ALIAS_MAPPING.items():
        b = by_code.get(real_code)
        if b and not (b["pilot"] and b["wave"] == 1):
            questions.append(
                f"pilot alias {alias_code} maps to {real_code} {b['name']!r} ({b['city']}), "
                f"a wave-{b['wave']} non-pilot centre whose own alias is {b['alias']}"
            )
    return questions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--dry-run", action="store_true", help="plan only: no database connection, no file written"
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="optional JSON export of the seeded register (never inside migrations/)",
    )
    args = parser.parse_args(argv)
    if args.dry_run:
        return plan(args.out)
    if args.out is not None:
        resolve_output_path(args.out)  # fail before touching the database
    conn = get_db()
    try:
        branches = seed_operating_units_and_branches(conn)
        if args.out is not None:
            export_branch_register(branches, args.out)
        print(
            f"SUCCESS: Seeded all {len(branches)} branches across all 8 administrative divisions."
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
