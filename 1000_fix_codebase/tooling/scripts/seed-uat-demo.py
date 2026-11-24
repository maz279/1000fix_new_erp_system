# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""Seed the single-host synthetic UAT demo estate (Gate 3, 2026-11-24).

Run inside `odoo-bin shell -d fix_uat` (see infra/README-uat.md). Idempotent:
every section guards on its own marker record and prints ALREADY_SEEDED.

CREDENTIAL RULE: no password literal appears here. The portal logins read
DEMO_PARTNER_PW / DEMO_VENDOR_PW (the partner/vendor sections, faithful to the
2026-11-24 rebuild seeds) and DEMO_UAT_PW (the other six accounts) from the
environment. Generate them into infra/uat/.env.uat and pass them through
`docker compose exec -e ...`.

Demo accounts (all synthetic, disposable):
  customer   phone 01711000001 (OTP; the local contract echoes dev_code)
  corporate  demo.corporate@1000fix.com   (client of Demo Corporate Ltd)
  analytics  demo.analytics@1000fix.com   (internal staff)
  seller     demo.seller@1000fix.com      (Demo Seller Shop)
  brand      demo.brand@1000fix.com       (acts for DemoBrand)
  agent      demo.agent@1000fix.com       (internal staff, contact centre)
  partner    demo.partner@1000fix.com     (Dhaka Digital Solutions)
  vendor     demo.vendor@1000fix.com      (Dhaka Spare Parts Ltd)
"""

import os
from datetime import timedelta

from odoo import fields

now = fields.Datetime.now()
today = fields.Date.context_today(env.user)
portal_group = env.ref("base.group_portal")


def _pw(var):
    value = os.environ.get(var, "").strip()
    if not value:
        raise SystemExit(f"seed-uat-demo: {var} must be set (credential rule)")
    return value


def _user(name, login, partner, groups, password):
    existing = env["res.users"].search([("login", "=", login)], limit=1)
    if existing:
        return existing
    return env["res.users"].create(
        {
            "name": name,
            "login": login,
            "email": login,
            "password": password,
            "partner_id": partner.id,
            "group_ids": [(6, 0, [g.id for g in groups])],
        }
    )


def _group(xmlid):
    try:
        return env.ref(xmlid)
    except ValueError:
        return None


# --- shared spine: entity / branch / operating unit -------------------------
ou = env["operating.unit"].search([], limit=1)
company = env.company
entity = env["fix.entity"].search([("company_id", "=", company.id)], limit=1)
if not entity:
    entity = env["fix.entity"].create(
        {"code": "UATENT", "legal_name": "UAT Synthetic Entity", "company_id": company.id}
    )
branch = env["fix.branch"].search([], limit=1)
if not branch:
    branch = env["fix.branch"].create(
        {
            "name": "UAT Dhanmondi",
            "code": "UATDH",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
brand = env["fix.brand"].search([("name", "=", "DemoBrand")], limit=1)
if not brand:
    brand = env["fix.brand"].create({"name": "DemoBrand", "code": "UATBR"})
phone_model = env["fix.device.model"].search([("name", "=", "Demo Phone X")], limit=1)
if not phone_model:
    phone_model = env["fix.device.model"].create(
        {"name": "Demo Phone X", "brand_id": brand.id, "device_type": "smartphone"}
    )
laptop_model = env["fix.device.model"].search([("name", "=", "Demo Laptop 14")], limit=1)
if not laptop_model:
    laptop_model = env["fix.device.model"].create(
        {"name": "Demo Laptop 14", "brand_id": brand.id, "device_type": "laptop"}
    )

# --- 1. customer (phone OTP) -------------------------------------------------
# Guard on the seed's own marker, not the phone: the party master normalizes
# phone on create, and a prior OTP may already have provisioned a bare partner
# with the raw number - the login binding below re-points that account here.
cust_partner = env["res.partner"].search([("name", "=", "Demo Customer")], limit=1)
if cust_partner:
    print("ALREADY_SEEDED customer", cust_partner.id)
else:
    cust_partner = env["res.partner"].create(
        {"name": "Demo Customer", "phone": "01711000001", "email": "demo.customer@example.com"}
    )
    device = env["fix.device"].create(
        {
            "device_model_id": phone_model.id,
            "owner_id": cust_partner.id,
            "serial_number": "SN-UAT-0001",
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": cust_partner.id,
            "branch_id": branch.id,
            "fault_description": "Screen flicker (UAT demo)",
        }
    )
    estimate = env["fix.estimate"].create({"order_id": order.id})
    env["fix.estimate.line"].create(
        {"estimate_id": estimate.id, "description": "Display assembly", "unit_price": 1000.0}
    )
    estimate.state = "sent"
    print("CUSTOMER", cust_partner.id, "ORDER", order.id, "ESTIMATE", estimate.id)

# The OTP identity is keyed by login = phone (_portal_user_for_phone): bind
# that account to the seeded estate, or a first OTP would provision a fresh
# empty partner instead of showing the demo device/order/estimate.
cust_user = (
    env["res.users"]
    .with_context(active_test=False)
    .search([("login", "=", "01711000001")], limit=1)
)
if not cust_user:
    cust_user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Demo Customer",
                "login": "01711000001",
                "phone": "01711000001",
                "partner_id": cust_partner.id,
                "group_ids": [(6, 0, [portal_group.id])],
            }
        )
    )
elif cust_user.partner_id.id != cust_partner.id:
    cust_user.partner_id = cust_partner.id
print("CUSTOMER_LOGIN", cust_user.id, "PARTNER", cust_user.partner_id.id)

# --- 2. corporate (commercial-partner fence) ---------------------------------
corp_company = env["res.partner"].search([("name", "=", "Demo Corporate Ltd")], limit=1)
if corp_company:
    print("ALREADY_SEEDED corporate", corp_company.id)
else:
    corp_company = env["res.partner"].create(
        {
            "name": "Demo Corporate Ltd",
            "is_company": True,
            "email": "it@democorporate.example",
            "phone": "+8801711000300",
            "city": "Dhaka",
        }
    )
    desk = env["res.partner"].create(
        {"name": "Demo Corporate IT Desk", "parent_id": corp_company.id, "type": "contact"}
    )
    groups = [portal_group]
    cg = _group("cd_corporate_portal.group_fix_corporate_portal")
    if cg:
        groups.append(cg)
    corp_user = _user(
        "Demo Corporate IT", "demo.corporate@1000fix.com", desk, groups, _pw("DEMO_UAT_PW")
    )
    laptop = env["fix.device"].create(
        {
            "device_model_id": laptop_model.id,
            "owner_id": corp_company.id,
            "serial_number": "SN-UAT-CORP-01",
        }
    )
    env["fix.warranty"].create(
        {
            "device_id": laptop.id,
            "start_date": today - timedelta(days=30),
            "end_date": today + timedelta(days=335),
            "status": "active",
        }
    )
    invoice = env["fix.ar.invoice"].create(
        {
            "operating_unit_id": ou.id,
            "customer_id": corp_company.id,
            "source_model": "fix.service.order",
            "source_id": 1,
            "invoice_date": today,
            "state": "issued",
        }
    )
    env["fix.ar.invoice.line"].create(
        {"invoice_id": invoice.id, "taxable_amount": 1000.0, "vat_amount": 150.0}
    )
    print("CORPORATE", corp_company.id, "USER", corp_user.id, "INVOICE", invoice.id)

# --- 3. analytics (internal staff) -------------------------------------------
analytics_user = _user(
    "Demo Analytics Staff",
    "demo.analytics@1000fix.com",
    env["res.partner"].create({"name": "Demo Analytics Staff"}),
    [env.ref("base.group_user")],
    _pw("DEMO_UAT_PW"),
)
print("ANALYTICS", analytics_user.id, analytics_user.login)

# --- 4. seller (marketplace) -------------------------------------------------
seller_partner = env["res.partner"].search([("name", "=", "Demo Seller Shop")], limit=1)
if seller_partner:
    print("ALREADY_SEEDED seller", seller_partner.id)
else:
    seller_partner = env["res.partner"].create(
        {"name": "Demo Seller Shop", "is_company": True, "email": "shop@demoseller.example"}
    )
    seller_user = _user(
        "Demo Seller", "demo.seller@1000fix.com", seller_partner, [portal_group], _pw("DEMO_UAT_PW")
    )
    seller = env["fix.marketplace.seller"].create(
        {
            "name": "Demo Seller Shop",
            "partner_id": seller_partner.id,
            "company_id": company.id,
            "operating_unit_id": ou.id,
        }
    )
    print("SELLER", seller.id, "USER", seller_user.id)

# --- 5. brand (acts for DemoBrand) -------------------------------------------
brand_user = env["res.users"].search([("login", "=", "demo.brand@1000fix.com")], limit=1)
if brand_user:
    print("ALREADY_SEEDED brand", brand_user.id)
else:
    brand_partner = env["res.partner"].create(
        {
            "name": "DemoBrand Warranty Desk",
            "is_company": True,
            "email": "warranty@demobrand.example",
        }
    )
    groups = [portal_group]
    bg = _group("cd_warranty_claims.group_fix_brand_portal")
    if bg:
        groups.append(bg)
    brand_user = _user(
        "DemoBrand Warranty", "demo.brand@1000fix.com", brand_partner, groups, _pw("DEMO_UAT_PW")
    )
    brand.write({"api_user_ids": [(4, brand_user.id)]})
    print("BRAND", brand.id, "USER", brand_user.id)

# --- 6. agent console (internal staff, contact centre) -----------------------
agent_groups = [env.ref("base.group_user")]
for xmlid in (
    "cd_contact_centre.group_fix_contact_centre_agent",
    "cd_contact_centre.group_fix_agent",
):
    g = _group(xmlid)
    if g:
        agent_groups.append(g)
        break
agent_user = _user(
    "Demo Agent",
    "demo.agent@1000fix.com",
    env["res.partner"].create({"name": "Demo Agent"}),
    agent_groups,
    _pw("DEMO_UAT_PW"),
)
print("AGENT", agent_user.id, agent_user.login)

# --- 7. partner & referral (faithful to the 2026-11-24 rebuild seed) ---------
existing = env["fix.partner"].search([("name", "=", "Dhaka Digital Solutions")], limit=1)
if existing:
    print("ALREADY_SEEDED partner", existing.id)
else:
    company_partner = env["res.partner"].create(
        {
            "name": "Dhaka Digital Solutions",
            "is_company": True,
            "email": "partners@dhakadigital.example",
            "phone": "+8801711000100",
            "city": "Dhaka",
        }
    )
    groups = [portal_group]
    pg = _group("cd_partner.group_fix_partner_portal")
    if pg:
        groups.append(pg)
    partner_user = _user(
        "Ayesha Rahman", "demo.partner@1000fix.com", company_partner, groups, _pw("DEMO_PARTNER_PW")
    )
    profile = env["fix.partner"].create(
        {
            "name": "Dhaka Digital Solutions",
            "partner_id": company_partner.id,
            "partner_type": "referral",
            "territory": "Dhaka",
            "commission_rate": 0.08,
            "state": "onboarded",
            "kyc_verified": True,
        }
    )
    Lead = env["fix.partner.lead"]
    for name, phone, interest, state in [
        ("Tanvir Ahmed", "+8801711000011", "Corporate AMC — 40 laptops", "converted"),
        ("Metro Traders", "+8801711000012", "Bulk laptop servicing", "converted"),
        ("Rahim Uddin", "+8801711000014", "Mobile screen replacement", "submitted"),
        ("Nusrat Jahan", "+8801711000015", "AC servicing — 2 units", "qualified"),
        ("Farhan Kabir", "+8801711000016", "Printer repair", "lost"),
    ]:
        lead = Lead.create(
            {
                "partner_id": profile.id,
                "company_id": profile.company_id.id,
                "customer_name": name,
                "customer_phone": phone,
                "customer_email": "%s@example.com" % name.split()[0].lower(),
                "service_interest": interest,
                "consent_given": True,
                "consent_method": "digital",
            }
        )
        if state != "submitted":
            lead.write({"state": state})
    print(
        "PARTNER",
        profile.id,
        "USER",
        partner_user.id,
        "LEADS",
        Lead.search_count([("partner_id", "=", profile.id)]),
    )

# --- 8. vendor (faithful to the 2026-11-24 rebuild seed) ---------------------
existing = env["fix.supplier"].search([("name", "=", "Dhaka Spare Parts Ltd")], limit=1)
if existing:
    print("ALREADY_SEEDED vendor", existing.id)
else:
    vendor_partner = env["res.partner"].create(
        {
            "name": "Dhaka Spare Parts Ltd",
            "is_company": True,
            "email": "vendors@dhakaspare.example",
            "phone": "+8801711000200",
            "city": "Dhaka",
        }
    )
    groups = [portal_group]
    vg = _group("cd_vendor_portal.group_fix_vendor_portal")
    if vg:
        groups.append(vg)
    vendor_user = _user(
        "Rafiq Hasan", "demo.vendor@1000fix.com", vendor_partner, groups, _pw("DEMO_VENDOR_PW")
    )
    supplier = env["fix.supplier"].create(
        {
            "name": "Dhaka Spare Parts Ltd",
            "partner_id": vendor_partner.id,
            "segment": "preferred",
            "residency": "resident",
            "category": "Spare parts — laptop & desktop",
            "status": "active",
            "classification": "authorised_distributor",
            "risk_tier": "low",
            "onboarded_on": today - timedelta(days=320),
        }
    )
    env["fix.supplier.contact"].create(
        {
            "supplier_id": supplier.id,
            "name": "Ayesha Karim",
            "role": "commercial",
            "phone": "+8801711000201",
            "email": "ayesha@dhakaspare.example",
        }
    )
    for doc_type, number, valid_to, state in [
        ("trade_licence", "TL-2026-88120", today + timedelta(days=300), "valid"),
        ("tin", "TIN-2099114455", today + timedelta(days=18), "valid"),
        ("vat", "VAT-8899001122", today - timedelta(days=12), "expired"),
    ]:
        env["fix.supplier.document"].create(
            {
                "supplier_id": supplier.id,
                "doc_type": doc_type,
                "number": number,
                "valid_from": today - timedelta(days=365),
                "valid_to": valid_to,
                "state": state,
                "file_ref": "VENDOR-DEMO-%s.pdf" % doc_type,
            }
        )
    print("VENDOR", supplier.id, "USER", vendor_user.id)

env.cr.commit()
print("UAT_DEMO_SEED_OK")
