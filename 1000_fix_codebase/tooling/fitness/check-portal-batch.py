#!/usr/bin/env python3
"""check-portal-batch — PP5 structural validation for the Next.js batch.

Validates the 7 PP5 portals (P01/P05/P06/P07/P08/P10/P12) without a
browser:
- App skeleton: package.json + lib/imports.ts + lib/api.ts +
  components/theme.tsx (the PP3 template; one barrel per app)
- API discipline: lib/api.ts wraps ApiClient.callOdoo (P-11); no raw
  fetch anywhere (FF-39 carries the repo-wide scan — this asserts the
  wrapper exists per app)
- Screen inventory: each app carries its plan-mandated routes
- P01 is Bengali-first (DE-17: lang="bn" + bn copy + Bengali font)
- P06 embed seam: iframe only from backend embed_url (no host literals)
- P08 brand isolation: every /brand call carries brand_id
- P10 softphone seam: config rendered, nulls accepted
- Backend parity: every route the apps call has an @http.route
  controller (the app↔controller matrix; FL-03 settlement exception
  lives in cd_settlement_ext)

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WEB = REPO / "apps" / "web"
ADDONS = REPO / "addons"

APPS = {
    "customer": {
        "title": "P01 Customer",
        "routes": [
            "app/page.tsx",
            "app/booking/page.tsx",
            "app/tracking/page.tsx",
            "app/estimates/page.tsx",
            "app/devices/page.tsx",
            "app/consent/page.tsx",
            "app/technician/page.tsx",
        ],
        "bn": True,
    },
    "vendor": {
        "title": "P05 Vendor",
        "routes": ["app/page.tsx", "app/invoices/page.tsx"],
        "bn": False,
    },
    "analytics": {
        "title": "P06 Analytics",
        "routes": ["app/page.tsx"],
        "bn": False,
    },
    "seller": {
        "title": "P07 Seller",
        "routes": [
            "app/page.tsx",
            "app/jobs/page.tsx",
            "app/scorecard/page.tsx",
            "app/settlements/page.tsx",
        ],
        "bn": False,
    },
    "brand": {
        "title": "P08 Brand",
        "routes": ["app/page.tsx", "app/reconciliation/page.tsx"],
        "bn": False,
    },
    "agent-console": {
        "title": "P10 Agent Console",
        "routes": ["app/page.tsx", "app/conversation/page.tsx"],
        "bn": False,
    },
    "partner": {
        "title": "P12 Partner",
        "routes": ["app/page.tsx", "app/referrals/page.tsx", "app/commissions/page.tsx"],
        "bn": False,
    },
}

# The app↔controller matrix: every API path any PP5 app calls must have
# an @http.route in the owning module's controller (server parity).
CONTROLLER_MATRIX = {
    "/customer/devices": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/customer/bookings": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/customer/tracking": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/customer/estimates": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/customer/consent": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/customer/ownership/transfer": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/customer/models": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/customer/branches": "b_customer_engagement/cd_customer_portal/controllers/customer_api.py",
    "/technician/auth/me": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/queue": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/attendance/clock_in": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/attendance/clock_out": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/job/status": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/diagnostics/tree": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/diagnostics/submit": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/van-stock": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/van-stock/consume": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/technician/sync": "a_service_delivery/cd_service_order/controllers/technician_api.py",
    "/vendor/purchase-orders": "e_supply_chain/cd_vendor_portal/controllers/vendor_api.py",
    "/vendor/invoices": "e_supply_chain/cd_vendor_portal/controllers/vendor_api.py",
    "/analytics/dashboards": "j_data_analytics/cd_metric_registry/controllers/analytics_api.py",
    "/analytics/kpis": "j_data_analytics/cd_metric_registry/controllers/analytics_api.py",
    "/seller/dashboard": "d_circular/cd_marketplace/controllers/seller_api.py",
    "/seller/orders": "d_circular/cd_marketplace/controllers/seller_api.py",
    "/seller/quotes": "d_circular/cd_marketplace/controllers/seller_api.py",
    "/seller/scorecard": "d_circular/cd_marketplace/controllers/seller_api.py",
    "/seller/settlements": "g_finance/cd_settlement_ext/controllers/settlement_api.py",
    "/brand/claims": "a_service_delivery/cd_warranty_claims/controllers/brand_api.py",
    "/brand/claims/status": "a_service_delivery/cd_warranty_claims/controllers/brand_api.py",
    "/brand/reconciliation": "a_service_delivery/cd_warranty_claims/controllers/brand_api.py",
    "/contact/conversations": "b_customer_engagement/cd_contact_centre/controllers/contact_api.py",
    "/contact/conversations/detail": "b_customer_engagement/cd_contact_centre/controllers/contact_api.py",
    "/contact/handoff": "b_customer_engagement/cd_contact_centre/controllers/contact_api.py",
    "/contact/softphone": "b_customer_engagement/cd_contact_centre/controllers/contact_api.py",
    "/partner/profile": "b_customer_engagement/cd_partner/controllers/partner_api.py",
    "/partner/referrals": "b_customer_engagement/cd_partner/controllers/partner_api.py",
    "/partner/commissions": "b_customer_engagement/cd_partner/controllers/partner_api.py",
}

LINE_COMMENT = re.compile(r"//[^\n]*")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def strip_comments(text: str) -> str:
    return LINE_COMMENT.sub("", BLOCK_COMMENT.sub("", text))


def main() -> int:
    v: list[str] = []
    api_calls: set[str] = set()

    for dirname, spec in APPS.items():
        base = WEB / dirname
        if not base.is_dir():
            v.append(f"{spec['title']}: app directory missing: apps/web/{dirname}")
            continue

        # skeleton: package.json + barrel + api wrapper + theme
        for rel in ("package.json", "lib/imports.ts", "lib/api.ts", "components/theme.tsx"):
            if not (base / rel).is_file():
                v.append(f"{spec['title']}: missing {rel}")

        if (base / "lib" / "api.ts").is_file():
            api_src = (base / "lib" / "api.ts").read_text(encoding="utf-8")
            if "ApiClient" not in api_src or "callOdoo" not in api_src:
                v.append(f"{spec['title']}: lib/api.ts must wrap ApiClient.callOdoo (P-11)")

        # routes exist and stay token-driven (CFM-01: no hand hex)
        for rel in spec["routes"]:
            page = base / rel
            if not page.is_file():
                v.append(f"{spec['title']}: missing route {rel}")
                continue
            src = strip_comments(page.read_text(encoding="utf-8"))
            if re.search(r"#[0-9a-fA-F]{3,8}\b", src):
                v.append(f"{spec['title']}: hand-authored hex in {rel} (CFM-01)")
            # collect backend paths this app calls
            for m in re.finditer(r'callOdoo[^(]*\(\s*"(/[^"]+)"', src):
                api_calls.add(m.group(1))
            if "fetch(" in src:
                v.append(f"{spec['title']}: raw fetch in {rel} (P-11)")

        layout = base / "app" / "layout.tsx"
        if layout.is_file():
            src = layout.read_text(encoding="utf-8")
            if spec["bn"]:
                if 'lang="bn"' not in src:
                    v.append(f"{spec['title']}: DE-17 requires lang=\"bn\" in the shell")
                if '"bn"' not in src or "typography.font.bengali" not in src:
                    v.append(f"{spec['title']}: DE-17 requires Bengali copy + font")

    # app-specific conformance -----------------------------------------
    analytics_page = WEB / "analytics" / "app" / "page.tsx"
    if analytics_page.is_file():
        src = analytics_page.read_text(encoding="utf-8")
        if re.search(r'src="(http|https|wss)://', src):
            v.append(
                "P06: embed iframe src must come from the backend embed_url — no host literals"
            )
        if "embed_available" not in src or "embed_url" not in src:
            v.append("P06: the embed seam must render backend embed availability")

    brand_pages = [
        WEB / "brand" / "app" / "page.tsx",
        WEB / "brand" / "app" / "reconciliation" / "page.tsx",
    ]
    for p in brand_pages:
        if p.is_file():
            src = strip_comments(p.read_text(encoding="utf-8"))
            for m in re.finditer(r'callOdoo[^(]*\(\s*"(/brand/[^"]+)"', src):
                # every /brand call site must carry brand_id in its params
                window = src[m.end() : m.end() + 400]
                if "brand_id" not in window:
                    v.append(
                        f"P08: {p.name} call to {m.group(1)} lacks brand_id (per-brand isolation)"
                    )

    agent_queue = WEB / "agent-console" / "app" / "page.tsx"
    if agent_queue.is_file():
        src = agent_queue.read_text(encoding="utf-8")
        if "/contact/softphone" not in src:
            v.append("P10: the queue must render the softphone seam (/contact/softphone)")
        if re.search(r"wss?://|sip:\w+@", src):
            v.append("P10: softphone hosts must come from config — no literals")

    # the shared marketing shell (landing/login experience) --------------
    landing = REPO / "libs" / "ts" / "i18n" / "src" / "landing.generated.json"
    shell = REPO / "libs" / "ts" / "ui" / "src" / "landing.tsx"
    generator = REPO / "tooling" / "generators" / "generate-landing-artefact.py"
    for p, what in (
        (landing, "landing artefact"),
        (shell, "LandingShell"),
        (generator, "landing generator"),
    ):
        if not p.is_file():
            v.append(f"landing: missing {what}: {p.relative_to(REPO)}")
    if landing.is_file():
        import json

        art = json.loads(landing.read_text(encoding="utf-8"))
        if len(art.get("portals", [])) != 12:
            v.append(f"landing: expected 12 portal cards, found {len(art.get('portals', []))}")
        if len(art.get("journeys", [])) != 10:
            v.append(f"landing: expected 10 journey strips, found {len(art.get('journeys', []))}")
    if shell.is_file():
        src = shell.read_text(encoding="utf-8")
        if '"bn"' not in src:
            v.append("landing: the shell must be bilingual (DE-17 — Bengali default)")
        if re.search(r"#[0-9a-fA-F]{3,8}\b", strip_comments(src)):
            v.append("landing: hand-authored hex in the shell (CFM-01)")

    # server parity: every called path has a controller route -----------
    for path, rel in CONTROLLER_MATRIX.items():
        controller = ADDONS / "domain" / rel
        if not controller.is_file():
            v.append(f"controller missing for {path}: {rel}")
            continue
        src = controller.read_text(encoding="utf-8")
        if f'"{path}"' not in src:
            v.append(f"route {path} not registered in {rel}")

    # every path an app calls must be in the matrix (no orphan calls)
    for path in sorted(api_calls):
        if path not in CONTROLLER_MATRIX:
            v.append(f"app calls {path} but no PP5 controller matrix entry covers it")

    if v:
        print(f"portal-batch: FAIL - {len(v)} violation(s):")
        for line in v:
            print(f"  {line}")
        return 1

    print(
        f"portal-batch: OK — {len(APPS)} portals, "
        f"{sum(len(s['routes']) for s in APPS.values())} routes, "
        f"{len(CONTROLLER_MATRIX)} controller routes verified, "
        "P-11 wrappers + CFM-01 tokens clean, P01 Bengali-first (DE-17), "
        "P06 embed seam config-only, P08 brand isolation, P10 softphone seam"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
