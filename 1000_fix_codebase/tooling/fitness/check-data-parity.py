#!/usr/bin/env python3
"""check-data-parity — PP6 §4: the data-shape parity suite + §7 masks.

Parity (03-DATA-STRATEGY §4): for every ported grid the test asserts
    set(expected_columns) ⊆ set(api_response_fields)
where expected_columns are the prototype's grid schemas (the §9 matrix,
audit-corrected 2026-10-05) mapped onto the REAL API surface (the W4 +
PP5 JSON-RPC endpoints — the /api/v1/* paths in the matrix are the
PROPOSED surface and are tracked as pending, not silently dropped).
Each row targets the controller METHOD that builds the payload and
collects every literal response key in its body — nesting-safe.

§7 masks: libs/ts/ui/src/masks.ts must implement the four statutory
identifiers exactly as the table prescribes (13-digit BIN, 10/17-digit
NID, 12-digit hyphenated e-TIN) — digit-only, length-exact, no invented
checksums.

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

CTRL = {
    "customer": REPO
    / "addons/domain/b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "corporate": REPO
    / "addons/domain/b_customer_engagement/cd_corporate_portal/controllers/corporate_api.py",
    "vendor": REPO / "addons/domain/e_supply_chain/cd_vendor_portal/controllers/vendor_api.py",
    "brand": REPO / "addons/domain/a_service_delivery/cd_warranty_claims/controllers/brand_api.py",
    "contact": REPO
    / "addons/domain/b_customer_engagement/cd_contact_centre/controllers/contact_api.py",
    "seller": REPO / "addons/domain/d_circular/cd_marketplace/controllers/seller_api.py",
    "settlement": REPO / "addons/domain/g_finance/cd_settlement_ext/controllers/settlement_api.py",
    "partner": REPO / "addons/domain/b_customer_engagement/cd_partner/controllers/partner_api.py",
}

# (controller key, method name, prototype grid columns that must ship)
PARITY = [
    # M01 Service Orders — §9 row 1 (order grid) via the two real surfaces
    ("customer", "_list_bookings", {"ref", "state", "device", "technician"}),
    ("customer", "tracking", {"ref", "state", "technician", "eta_resolution"}),
    # M17 Device Registry — §9 row 3 via both estate surfaces
    ("customer", "devices", {"identifier", "warranty_status", "state", "brand", "model"}),
    ("corporate", "estate", {"identifier", "warranty_status", "warranty_end"}),
    # M20 AR & Invoicing — §9 row 5 (corporate consolidated grid)
    ("corporate", "consolidated_invoices", {"invoice_no", "gross_bdt", "vat_bdt", "net_bdt"}),
    # M16 Procurement — vendor PO + invoice grids
    ("vendor", "purchase_orders", {"ref", "state", "total_bdt", "acknowledged_at"}),
    (
        "vendor",
        "invoices",
        {"invoice_ref", "subtotal_bdt", "tds_bdt", "payable_bdt", "match_state", "match_detail"},
    ),
    # M09 Warranty claims — the brand queue grid
    (
        "brand",
        "_list_claims",
        {"claim_no", "state", "amount_bdt", "evidence_complete", "missing_evidence"},
    ),
    # M27 Contact centre — the unified queue grid
    ("contact", "conversations", {"channel", "state", "intent", "customer", "turns"}),
    # M12 Marketplace — jobs board + scorecard grid
    ("seller", "orders", {"name", "description", "budget_bdt", "state", "my_quote"}),
    (
        "seller",
        "scorecard",
        {"period", "acceptance_rate", "on_time_rate", "review_rating", "dispute_rate", "composite"},
    ),
    # M53 Settlement — statement lines grid
    (
        "settlement",
        "seller_settlements",
        {"ref", "gross_bdt", "commission_bdt", "tds_bdt", "net_bdt", "state"},
    ),
    # M53 Partner programme — referrals + commissions
    ("partner", "referrals", {"name", "referred", "state", "commission_bdt"}),
    ("partner", "commissions", {"earned_total_bdt"}),
]

MASKS = REPO / "libs/ts/ui/src/masks.ts"

# §7 rules as they must appear in masks.ts — plain substrings of the
# statutory pattern (no regex-escaping games: we assert the pattern text)
MASK_CONTRACT = [
    ("BIN_13", "\\d{13}"),
    ("NID_10", "\\d{10}"),
    ("NID_17", "\\d{15}"),  # (19|20) year prefix + 15 more digits = 17
    ("ETIN_12", "\\d{4}-\\d{4}-\\d{4}"),
]

LINE_COMMENT = re.compile(r"//[^\n]*")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def method_keys(src: str, method: str) -> set | None:
    """Every literal `"key":` inside the def `method` block (nesting-safe)."""
    m = re.search(rf"def {re.escape(method)}\(", src)
    if not m:
        return None
    nxt = re.search(r"\n    def |\n    @|\nclass |\Z", src[m.start() :])
    body = src[m.start() : m.start() + (nxt.start() if nxt else len(src))]
    return set(re.findall(r'"([a-z_0-9]+)":', body))


def main() -> int:
    v: list[str] = []

    # --- §4 parity -------------------------------------------------------
    for file_key, method, expected in PARITY:
        keys = method_keys(CTRL[file_key].read_text(encoding="utf-8"), method)
        if keys is None:
            v.append(f"parity: method {file_key}.{method} not found " "(renamed controller?)")
            continue
        missing = expected - keys
        if missing:
            v.append(
                f"parity {file_key}.{method}: prototype columns missing "
                f"from the API payload: {sorted(missing)}"
            )

    # --- §7 statutory masks ----------------------------------------------
    if not MASKS.is_file():
        v.append("§7 masks: libs/ts/ui/src/masks.ts is missing")
    else:
        msrc = MASKS.read_text(encoding="utf-8")
        code = BLOCK_COMMENT.sub("", LINE_COMMENT.sub("", msrc))
        for name, pattern in MASK_CONTRACT:
            if name not in code:
                v.append(f"§7 masks: {name} validator missing from masks.ts")
            elif pattern not in code:
                v.append(
                    f"§7 masks: {name} pattern does not match the "
                    f"statutory rule (expected {pattern!r})"
                )
        # no invented checksums (audit correction): CODE must not claim
        # checksum validation (the word may appear in comments)
        if re.search(r"checksum", code, re.I):
            v.append(
                "§7 masks: checksum logic present — the 2026-10-05 "
                "audit removed invented checksums (length/format only)"
            )
        # BN-007 display formatter (§8: formatting, never arithmetic)
        if "bn007" not in code:
            v.append("§8: bn007 display formatter missing from masks.ts")

    if v:
        print(f"data-parity: FAIL - {len(v)} violation(s):")
        for line in v:
            print(f"  {line}")
        return 1

    print(
        f"data-parity: OK — {len(PARITY)} ported grids carry every "
        "prototype column in their API payloads (§4), and the four "
        "statutory masks + bn007 formatter conform (§7/§8)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
