# cd_p03_portal — 1000 FiX official letterhead, single source of truth.
# Every export artefact (XLSX workbook header, PDF letterhead, email body)
# and the workspace shell read from HERE, so the logo, address and contact
# line can never drift between documents (ERPNext-style central Letter Head).
#
# Address/contact are read from res.company — fix that ONE record and every
# document follows. The hotline and ISO badge are brand constants from the
# company profile (they have no res.company field of their own).
from __future__ import annotations

from pathlib import Path

# brand tokens (tokens.json color.brand.60 / ink) — match _XLSX_BRAND
BRAND_TEAL = "0E7A6E"
BRAND_TEAL_RGB = (0x0E, 0x7A, 0x6E)
BRAND_INK = "242424"
BRAND_INK_RGB = (0x24, 0x24, 0x24)
GREY_RGB = (0x61, 0x61, 0x61)

ISO_BADGE = "ISO 9001:2015 Certified"
HOTLINE = "16743"

# fallback letterhead when res.company still carries installer/demo data —
# the official block from the company's own purchase-order stationery.
FALLBACK_COMPANY = "1000Fix Services Limited"
FALLBACK_ADDRESS_LINES = (
    "586/1 (4th Floor), Begum Rokeya Sarani",
    "Shewrapara, Mirpur, Dhaka 1216",
    "Bangladesh",
)
FALLBACK_PHONE = "09644-300600"
FALLBACK_EMAIL = "info@1000fix.com"

# a res.company with these values was never configured (Odoo demo defaults)
_DEMO_MARKERS = ("yourcompany", "example.com", "Marina Blvd", "54.0.0.")


def logo_path() -> Path:
    """Filesystem path of the official 1000 FiX logo (transparent PNG).
    Resolved from this file (controllers/brand.py → module root) so no Odoo
    module-path API can break the letterhead between versions."""
    return Path(__file__).resolve().parent.parent / "static" / "img" / "1000fix_logo.png"


def _looks_demo(company) -> bool:
    data = " ".join(
        str(x or "") for x in (company.name, company.street, company.email, company.website)
    )
    return any(marker.lower() in data.lower() for marker in _DEMO_MARKERS)


def letterhead(env) -> dict:
    """{name, address_lines, phone, email, website, contact_line} for the
    current company, falling back to the official stationery block."""
    company = env.company
    if _looks_demo(company):
        name = FALLBACK_COMPANY
        address_lines = list(FALLBACK_ADDRESS_LINES)
        phone, email = FALLBACK_PHONE, FALLBACK_EMAIL
    else:
        name = company.name or FALLBACK_COMPANY
        street = [s for s in (company.street, company.street2) if s]
        city = ", ".join(p for p in (company.city, company.zip) if p)
        address_lines = [*street, *([city] if city else [])]
        phone = company.phone or FALLBACK_PHONE
        email = company.email or FALLBACK_EMAIL
    contact = "Contact: %s · %s · Hot Line: %s" % (phone, email, HOTLINE)
    return {
        "name": name,
        "address_lines": address_lines,
        "phone": phone,
        "email": email,
        "contact_line": contact,
    }
