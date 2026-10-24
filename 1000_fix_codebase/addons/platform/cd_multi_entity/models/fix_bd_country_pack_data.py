# fix_bd_country_pack_data — Concrete Bangladesh Country Pack on fix.country.pack (CD-M65-01).
from odoo import api, models

# 8 Divisions of Bangladesh with codes and names
BANGLADESH_DIVISIONS = [
    {"code": "BD-10", "name": "Barisal", "name_bn": "বরিশাল"},
    {"code": "BD-20", "name": "Chittagong", "name_bn": "চট্টগ্রাম"},
    {"code": "BD-30", "name": "Dhaka", "name_bn": "ঢাকা"},
    {"code": "BD-40", "name": "Khulna", "name_bn": "খুলনা"},
    {"code": "BD-50", "name": "Rajshahi", "name_bn": "রাজশাহী"},
    {"code": "BD-55", "name": "Rangpur", "name_bn": "রংপুর"},
    {"code": "BD-60", "name": "Sylhet", "name_bn": "সিলেট"},
    {"code": "BD-65", "name": "Mymensingh", "name_bn": "ময়মনসিংহ"},
]

# Sample 64 districts mapped to division codes
BANGLADESH_DISTRICTS = [
    # Dhaka Division
    {"code": "BD-13", "parent": "BD-30", "name": "Dhaka", "name_bn": "ঢাকা"},
    {"code": "BD-14", "parent": "BD-30", "name": "Gazipur", "name_bn": "গাজীপুর"},
    {"code": "BD-15", "parent": "BD-30", "name": "Narayanganj", "name_bn": "নারায়ণগঞ্জ"},
    {"code": "BD-16", "parent": "BD-30", "name": "Tangail", "name_bn": "টাঙ্গাইল"},
    {"code": "BD-17", "parent": "BD-30", "name": "Narsingdi", "name_bn": "নরসিংদী"},
    {"code": "BD-18", "parent": "BD-30", "name": "Faridpur", "name_bn": "ফরিদপুর"},
    {"code": "BD-19", "parent": "BD-30", "name": "Manikganj", "name_bn": "মানিকগঞ্জ"},
    {"code": "BD-21", "parent": "BD-30", "name": "Munshiganj", "name_bn": "মুন্সীগঞ্জ"},
    {"code": "BD-22", "parent": "BD-30", "name": "Rajbari", "name_bn": "রাজবাড়ী"},
    {"code": "BD-23", "parent": "BD-30", "name": "Madaripur", "name_bn": "মাদারীপুর"},
    {"code": "BD-24", "parent": "BD-30", "name": "Gopalganj", "name_bn": "গোপালগঞ্জ"},
    {"code": "BD-25", "parent": "BD-30", "name": "Shariatpur", "name_bn": "শরীয়তপুর"},
    {"code": "BD-26", "parent": "BD-30", "name": "Kishoreganj", "name_bn": "কিশোরগঞ্জ"},
    # Chittagong Division
    {"code": "BD-04", "parent": "BD-20", "name": "Chittagong", "name_bn": "চট্টগ্রাম"},
    {"code": "BD-06", "parent": "BD-20", "name": "Cox's Bazar", "name_bn": "কক্সবাজার"},
    {"code": "BD-07", "parent": "BD-20", "name": "Cumilla", "name_bn": "কুমিল্লা"},
    {"code": "BD-08", "parent": "BD-20", "name": "Feni", "name_bn": "ফেনী"},
    {"code": "BD-09", "parent": "BD-20", "name": "Brahmanbaria", "name_bn": "ব্রাহ্মণবাড়িয়া"},
    {"code": "BD-11", "parent": "BD-20", "name": "Noakhali", "name_bn": "নোয়াখালী"},
    {"code": "BD-12", "parent": "BD-20", "name": "Chandpur", "name_bn": "চাঁদপুর"},
    {"code": "BD-01", "parent": "BD-20", "name": "Bandarban", "name_bn": "বান্দরবান"},
    {"code": "BD-02", "parent": "BD-20", "name": "Rangamati", "name_bn": "রাঙ্গামাটি"},
    {"code": "BD-03", "parent": "BD-20", "name": "Khagrachhari", "name_bn": "খাগড়াছড়ি"},
    {"code": "BD-05", "parent": "BD-20", "name": "Lakshmipur", "name_bn": "লক্ষ্মীপুর"},
    # Rajshahi Division
    {"code": "BD-54", "parent": "BD-50", "name": "Rajshahi", "name_bn": "রাজশাহী"},
    {"code": "BD-51", "parent": "BD-50", "name": "Bogura", "name_bn": "বগুড়া"},
    {"code": "BD-52", "parent": "BD-50", "name": "Joypurhat", "name_bn": "জয়পুরহাট"},
    {"code": "BD-53", "parent": "BD-50", "name": "Naogaon", "name_bn": "নওগাঁ"},
    {"code": "BD-56", "parent": "BD-50", "name": "Natore", "name_bn": "নাটোর"},
    {"code": "BD-57", "parent": "BD-50", "name": "Nawabganj", "name_bn": "নবাবগঞ্জ"},
    {"code": "BD-58", "parent": "BD-50", "name": "Pabna", "name_bn": "পাবনা"},
    {"code": "BD-59", "parent": "BD-50", "name": "Sirajganj", "name_bn": "সিরাজগঞ্জ"},
    # Khulna Division
    {"code": "BD-38", "parent": "BD-40", "name": "Khulna", "name_bn": "খুলনা"},
    {"code": "BD-39", "parent": "BD-40", "name": "Bagerhat", "name_bn": "বাগেরহাট"},
    {"code": "BD-41", "parent": "BD-40", "name": "Chuadanga", "name_bn": "চুয়াডাঙ্গা"},
    {"code": "BD-42", "parent": "BD-40", "name": "Jashore", "name_bn": "যশোর"},
    {"code": "BD-43", "parent": "BD-40", "name": "Jhenaidah", "name_bn": "ঝিনাইদহ"},
    {"code": "BD-44", "parent": "BD-40", "name": "Kushtia", "name_bn": "কুষ্টিয়া"},
    {"code": "BD-45", "parent": "BD-40", "name": "Magura", "name_bn": "মাগুরা"},
    {"code": "BD-46", "parent": "BD-40", "name": "Meherpur", "name_bn": "মেহেরপুর"},
    {"code": "BD-47", "parent": "BD-40", "name": "Narail", "name_bn": "নড়াইল"},
    {"code": "BD-48", "parent": "BD-40", "name": "Satkhira", "name_bn": "সাতক্ষীরা"},
    # Barisal Division
    {"code": "BD-31", "parent": "BD-10", "name": "Barisal", "name_bn": "বরিশাল"},
    {"code": "BD-32", "parent": "BD-10", "name": "Barguna", "name_bn": "বরগুনা"},
    {"code": "BD-33", "parent": "BD-10", "name": "Bhola", "name_bn": "ভোলা"},
    {"code": "BD-34", "parent": "BD-10", "name": "Jhalokati", "name_bn": "ঝালকাঠি"},
    {"code": "BD-35", "parent": "BD-10", "name": "Patuakhali", "name_bn": "পটুয়াখালী"},
    {"code": "BD-36", "parent": "BD-10", "name": "Pirojpur", "name_bn": "পিরোজপুর"},
    # Sylhet Division
    {"code": "BD-61", "parent": "BD-60", "name": "Sylhet", "name_bn": "সিলেট"},
    {"code": "BD-62", "parent": "BD-60", "name": "Habiganj", "name_bn": "হবিগঞ্জ"},
    {"code": "BD-63", "parent": "BD-60", "name": "Moulvibazar", "name_bn": "মৌলভীবাজার"},
    {"code": "BD-64", "parent": "BD-60", "name": "Sunamganj", "name_bn": "সুনামগঞ্জ"},
    # Rangpur Division
    {"code": "BD-27", "parent": "BD-55", "name": "Rangpur", "name_bn": "রংপুর"},
    {"code": "BD-28", "parent": "BD-55", "name": "Dinajpur", "name_bn": "দিনাজপুর"},
    {"code": "BD-29", "parent": "BD-55", "name": "Gaibandha", "name_bn": "গাইবান্ধা"},
    {"code": "BD-30-K", "parent": "BD-55", "name": "Kurigram", "name_bn": "কুড়িগ্রাম"},
    {"code": "BD-37", "parent": "BD-55", "name": "Lalmonirhat", "name_bn": "লালমনিরহাট"},
    {"code": "BD-49", "parent": "BD-55", "name": "Nilphamari", "name_bn": "নীলফামারী"},
    {"code": "BD-50-P", "parent": "BD-55", "name": "Panchagarh", "name_bn": "পঞ্চগড়"},
    {"code": "BD-55-T", "parent": "BD-55", "name": "Thakurgaon", "name_bn": "ঠাকুরগাঁও"},
    # Mymensingh Division
    {"code": "BD-66", "parent": "BD-65", "name": "Mymensingh", "name_bn": "ময়মনসিংহ"},
    {"code": "BD-67", "parent": "BD-65", "name": "Jamalpur", "name_bn": "জামালপুর"},
    {"code": "BD-68", "parent": "BD-65", "name": "Netrokona", "name_bn": "নেত্রকোণা"},
    {"code": "BD-69", "parent": "BD-65", "name": "Sherpur", "name_bn": "শেরপুর"},
]

# Statutory public holidays of Bangladesh (National + Moon-dependent)
STATUTORY_HOLIDAYS_2026 = [
    {
        "code": "HOL-2026-02-21",
        "name": "International Mother Language Day",
        "name_bn": "আন্তর্জাতিক মাতৃভাষা দিবস",
        "date": "2026-02-21",
    },
    {
        "code": "HOL-2026-03-26",
        "name": "Independence and National Day",
        "name_bn": "স্বাধীনতা ও জাতীয় দিবস",
        "date": "2026-03-26",
    },
    {
        "code": "HOL-2026-04-14",
        "name": "Bengali New Year (Pohela Boishakh)",
        "name_bn": "পহেলা বৈশাখ",
        "date": "2026-04-14",
    },
    {
        "code": "HOL-2026-03-21",
        "name": "Eid-ul-Fitr (Moon-dependent)",
        "name_bn": "ঈদুল ফিতর",
        "date": "2026-03-21",
    },
    {"code": "HOL-2026-05-01", "name": "May Day", "name_bn": "মে দিবস", "date": "2026-05-01"},
    {
        "code": "HOL-2026-05-28",
        "name": "Eid-ul-Adha (Moon-dependent)",
        "name_bn": "ঈদুল আযহা",
        "date": "2026-05-28",
    },
    {
        "code": "HOL-2026-08-15",
        "name": "National Mourning Day",
        "name_bn": "জাতীয় শোক দিবস",
        "date": "2026-08-15",
    },
    {
        "code": "HOL-2026-10-20",
        "name": "Durga Puja (Bijoya Dashami)",
        "name_bn": "দুর্গাপূজা (বিজয়া দশমী)",
        "date": "2026-10-20",
    },
    {"code": "HOL-2026-12-16", "name": "Victory Day", "name_bn": "বিজয় দিবস", "date": "2026-12-16"},
    {"code": "HOL-2026-12-25", "name": "Christmas Day", "name_bn": "বড়দিন", "date": "2026-12-25"},
]


class FixCountryPackDataLoader(models.AbstractModel):
    """Data loading service that populates the M30 fix.country.pack interface with concrete BD packs."""

    _name = "fix.country_pack.loader"
    _description = "Bangladesh Country Pack Data Loader"

    @api.model
    def load_bangladesh_pack(self) -> dict:
        """Instantiate concrete Bangladesh country pack records on fix.country.pack."""
        pack_model = self.env["fix.country.pack"]
        line_model = self.env["fix.country.pack.line"]

        # 1. Divisions & Districts pack
        div_pack = pack_model.search([("code", "=", "BD-DIV-DIST-2026")], limit=1)
        if not div_pack:
            div_pack = pack_model.create(
                {
                    "name": "Bangladesh Divisions & 64 Districts",
                    "code": "BD-DIV-DIST-2026",
                    "kind": "divisions",
                    "version": "2026.1",
                }
            )

            # Create division lines
            for div in BANGLADESH_DIVISIONS:
                line_model.create(
                    {
                        "pack_id": div_pack.id,
                        "code": div["code"],
                        "name": div["name"],
                        "name_bn": div["name_bn"],
                    }
                )

            # Create district lines
            for dist in BANGLADESH_DISTRICTS:
                line_model.create(
                    {
                        "pack_id": div_pack.id,
                        "parent_code": dist["parent"],
                        "code": dist["code"],
                        "name": dist["name"],
                        "name_bn": dist["name_bn"],
                    }
                )

            div_pack.action_load()

        # 2. Public Holidays pack
        hol_pack = pack_model.search([("code", "=", "BD-HOL-2026")], limit=1)
        if not hol_pack:
            hol_pack = pack_model.create(
                {
                    "name": "Bangladesh Gazette Public Holidays 2026",
                    "code": "BD-HOL-2026",
                    "kind": "holidays",
                    "version": "2026.1",
                }
            )

            for hol in STATUTORY_HOLIDAYS_2026:
                line_model.create(
                    {
                        "pack_id": hol_pack.id,
                        "code": hol["code"],
                        "name": hol["name"],
                        "name_bn": hol["name_bn"],
                        "date_value": hol["date"],
                    }
                )

            hol_pack.action_load()

        return {
            "divisions_count": len(BANGLADESH_DIVISIONS),
            "districts_count": len(BANGLADESH_DISTRICTS),
            "holidays_count": len(STATUTORY_HOLIDAYS_2026),
            "status": "LOADED",
        }
