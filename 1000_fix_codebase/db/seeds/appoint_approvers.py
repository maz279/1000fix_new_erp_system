# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""appoint_approvers.py - synthetic approvers for the M63 approval groups (DE-12).

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser). Idempotent: an
existing login is reused and only gains the groups listed here.

A routed approval refuses to be decided directly and goes to the holders of
its group, never to the requester or the record's creator (M63). With these
groups empty every request is refused with "No one can approve". One person
per role keeps segregation of duties visible in the inbox. Logins and
passwords are local test values (password = login), like the seed users.
"""

# A damage-claim payout needs the claim-approver role on top of the DOFA tier.
CLAIM_APPROVER = "cd_consignment.group_fix_damage_claim_approver"
# A05: a trade-in payout goes to a DOFA tier holder who also holds the payout role.
TRADEIN_PAYOUT = "cd_tradein.group_tradein_payout_approver"

APPROVERS = [
    # DOFA tiers stack (tier 4 implies 3, 2, 1): one holder per tier.
    (
        "seed.dofa.t1@1000fix.local",
        "রাশেদ করিম (DOFA Tier 1)",
        ["cd_entity_config.group_dofa_tier_1", CLAIM_APPROVER, TRADEIN_PAYOUT],
    ),
    (
        "seed.dofa.t2@1000fix.local",
        "নাসরিন আক্তার (DOFA Tier 2)",
        ["cd_entity_config.group_dofa_tier_2", CLAIM_APPROVER, TRADEIN_PAYOUT],
    ),
    (
        "seed.dofa.t3@1000fix.local",
        "মাহবুব আলম (DOFA Tier 3)",
        ["cd_entity_config.group_dofa_tier_3", CLAIM_APPROVER, TRADEIN_PAYOUT],
    ),
    (
        "seed.dofa.t4@1000fix.local",
        "ফারহানা ইসলাম (DOFA Tier 4)",
        ["cd_entity_config.group_dofa_tier_4", CLAIM_APPROVER, TRADEIN_PAYOUT],
    ),
    (
        "seed.dofa.t5@1000fix.local",
        "আনোয়ার হোসেন (DOFA Tier 5)",
        ["cd_entity_config.group_dofa_tier_5", CLAIM_APPROVER, TRADEIN_PAYOUT],
    ),
    # A02 role groups
    (
        "seed.branch.manager@1000fix.local",
        "সাইফুল ইসলাম (Branch Manager)",
        ["cd_front_desk.group_fd_branch_manager"],
    ),
    (
        "seed.refund.approver@1000fix.local",
        "তাহমিনা রহমান (Refund Approver)",
        ["cd_front_desk.group_fd_refund_approver"],
    ),
    (
        "seed.cab.member@1000fix.local",
        "জাহিদ হাসান (MSP CAB Member)",
        ["cd_msp_contract.group_msp_cab_member"],
    ),
    (
        "seed.change.manager@1000fix.local",
        "শামীম আহমেদ (MSP Change Manager)",
        ["cd_msp_contract.group_msp_change_manager"],
    ),
    (
        "seed.credit.approver@1000fix.local",
        "লায়লা পারভীন (MSP SLA Credit Approver)",
        ["cd_msp_contract.group_msp_credit_approver"],
    ),
    (
        "seed.lab.manager@1000fix.local",
        "কামরুল হাসান (Data Lab Manager)",
        ["cd_data_case.group_data_lab_manager"],
    ),
    (
        "seed.warranty.officer@1000fix.local",
        "সুমাইয়া খাতুন (Warranty Officer)",
        ["cd_device_registry.group_warranty_officer"],
    ),
    (
        "seed.workshop.supervisor@1000fix.local",
        "মোস্তফা কামাল (Workshop Supervisor)",
        ["cd_workshop.group_fix_workshop_manager"],
    ),
    (
        "seed.commercial.approver@1000fix.local",
        "রেহানা পারভীন (Commercial Approver)",
        ["cd_service_order.group_so_commercial_approver"],
    ),
    (
        "seed.so.supervisor@1000fix.local",
        "আরিফুল হক (Service Order Supervisor)",
        ["cd_service_order.group_so_supervisor"],
    ),
    # A06 supply chain (DE-12). Approver roles ship empty; one synthetic holder
    # each, never the operational users who raise the documents. An LC and a
    # supplier reinstatement are decided under DOFA Tier 4 as well.
    (
        "seed.inventory.controller@1000fix.local",
        "সাইফুল ইসলাম (Inventory Controller)",
        ["cd_wms_structure.group_inventory_controller"],
    ),
    (
        "seed.procurement.approver@1000fix.local",
        "তানজিলা হক (Procurement Approver)",
        ["cd_requisition.group_fix_procurement_approver"],
    ),
    (
        "seed.procurement.manager@1000fix.local",
        "কামরুল হাসান (Procurement Manager)",
        ["cd_requisition.group_fix_procurement_manager"],
    ),
    (
        "seed.supplier.approver@1000fix.local",
        "শারমিন সুলতানা (Supplier Approver)",
        ["cd_vendor_portal.group_fix_supplier_approver", "cd_entity_config.group_dofa_tier_4"],
    ),
    (
        "seed.demand.approver@1000fix.local",
        "জাহিদ হাসান (Demand Plan Approver)",
        ["cd_demand_plan.group_fix_demand_approver"],
    ),
    (
        "seed.import.approver@1000fix.local",
        "নুসরাত জাহান (Import Approver)",
        ["cd_import_order.group_fix_import_approver", "cd_entity_config.group_dofa_tier_4"],
    ),
    (
        "seed.doa.admin@1000fix.local",
        "আবদুল্লাহ আল মামুন (DoA Administrator)",
        ["cd_workflow_engine.group_doa_administrator"],
    ),
    # A05 circular economy (DE-12): one synthetic holder per role, so segregation
    # of duties stays visible (an assessor is never the dispatcher or the CFO).
    (
        "seed.provenance.officer@1000fix.local",
        "নাজমুল হুদা (Provenance Officer)",
        ["cd_tradein.group_tradein_provenance_officer"],
    ),
    (
        "seed.refurb.qa@1000fix.local",
        "সাবরিনা ইয়াসমিন (Refurbishment QA)",
        ["cd_tradein.group_tradein_qa_inspector"],
    ),
    (
        "seed.valuation.manager@1000fix.local",
        "তৌহিদুল ইসলাম (Valuation Manager)",
        ["cd_tradein.group_tradein_valuation_manager"],
    ),
    (
        "seed.ewaste.assessor@1000fix.local",
        "মাসুদ রানা (E-Waste Triage Assessor)",
        ["cd_ewaste.group_ewaste_triage_assessor"],
    ),
    (
        "seed.hse.officer@1000fix.local",
        "রুমানা আফরোজ (HSE Officer)",
        ["cd_ewaste.group_ewaste_hse_officer"],
    ),
    (
        "seed.ewaste.dispatcher@1000fix.local",
        "কবির হোসেন (E-Waste Dispatcher)",
        ["cd_ewaste.group_ewaste_dispatcher"],
    ),
    (
        "seed.recycler.approver@1000fix.local",
        "শাহানা পারভীন (Recycler Approver)",
        ["cd_ewaste.group_ewaste_recycler_approver"],
    ),
    (
        "seed.ewaste.compliance@1000fix.local",
        "ফয়সাল আহমেদ (E-Waste Compliance Officer)",
        ["cd_ewaste.group_ewaste_compliance_officer"],
    ),
    (
        "seed.ewaste.cfo@1000fix.local",
        "জেসমিন আক্তার (E-Waste Finance Approver)",
        ["cd_ewaste.group_ewaste_finance_approver"],
    ),
    # A08 S5: enough finance staff that every maker has a checker. Billing
    # raises, two Accountants prepare and clear level 1, two Administrators
    # approve and release. None of them may confirm a supplier's bank change
    # (FSOD-01): that stays with seed.supplier.approver, outside payables.
    (
        "seed.fin.billing@1000fix.local",
        "তানজিনা রহমান (Billing)",
        ["account.group_account_invoice"],
    ),
    (
        "seed.fin.accountant1@1000fix.local",
        "মেহেদী হাসান (Accountant 1)",
        ["account.group_account_user"],
    ),
    (
        "seed.fin.accountant2@1000fix.local",
        "সুমাইয়া খাতুন (Accountant 2)",
        ["account.group_account_user"],
    ),
    # A07: the spec's roles for the five asset and facility modules. Maker and checker
    # must differ on calibration, off-road, work orders and consent, so some come in pairs.
    (
        "seed.a07.device.agent@1000fix.local",
        "শারমিন সুলতানা (Device Registry Agent)",
        ["cd_device_registry.group_device_registry_user"],
    ),
    (
        "seed.a07.device.branch@1000fix.local",
        "ইমরান হোসেন (Device Registry Branch Manager)",
        ["cd_device_registry.group_device_branch_manager"],
    ),
    (
        "seed.a07.device.quality@1000fix.local",
        "রুমানা পারভীন (Device Quality Manager)",
        ["cd_device_registry.group_device_quality_manager"],
    ),
    (
        "seed.a07.cal.technician@1000fix.local",
        "আরিফুল ইসলাম (Calibration Technician)",
        ["cd_equipment_register.group_calibration_technician"],
    ),
    (
        "seed.a07.custodian@1000fix.local",
        "মোস্তফা কামাল (Equipment Custodian)",
        ["cd_equipment_register.group_equipment_custodian"],
    ),
    (
        "seed.a07.quality1@1000fix.local",
        "সাবিনা ইয়াসমিন (Quality Manager, Test Equipment)",
        ["cd_equipment_register.group_quality_manager"],
    ),
    (
        "seed.a07.quality2@1000fix.local",
        "নাজমুল হক (Quality Manager, Test Equipment)",
        ["cd_equipment_register.group_quality_manager"],
    ),
    (
        "seed.a07.fleet1@1000fix.local",
        "রফিকুল ইসলাম (Fleet Officer)",
        ["fleet.fleet_group_user"],
    ),
    (
        "seed.a07.fleet2@1000fix.local",
        "শাহানা বেগম (Fleet Officer)",
        ["fleet.fleet_group_user"],
    ),
    (
        "seed.a07.logistics@1000fix.local",
        "জসিম উদ্দিন (Fleet Logistics Manager)",
        ["cd_vehicle_ext.group_logistics_manager"],
    ),
    (
        "seed.a07.facility1@1000fix.local",
        "মাহমুদা খাতুন (Facility Manager)",
        ["cd_facility.group_facility_manager"],
    ),
    (
        "seed.a07.facility2@1000fix.local",
        "কবির আহমেদ (Facility Manager)",
        ["cd_facility.group_facility_manager"],
    ),
    (
        "seed.a07.branch.lead@1000fix.local",
        "তানজিনা আক্তার (Branch Operations Lead)",
        ["cd_facility.group_branch_operations_lead"],
    ),
    (
        "seed.a07.ops.director@1000fix.local",
        "হাসান মাহমুদ (Operations Director)",
        ["cd_facility.group_operations_director"],
    ),
    (
        "seed.a07.iot.operator@1000fix.local",
        "সজীব আহমেদ (IoT Operator)",
        ["cd_stream_registry.group_iot_operator"],
    ),
    (
        "seed.a07.iot.admin@1000fix.local",
        "মেহেদী হাসান (IoT Administrator)",
        ["cd_stream_registry.group_iot_admin"],
    ),
    (
        "seed.a07.iot.manager@1000fix.local",
        "লুৎফর রহমান (IoT Manager)",
        ["cd_stream_registry.group_iot_manager"],
    ),
    (
        "seed.a07.consent1@1000fix.local",
        "ফারজানা হক (IoT Consent Officer)",
        ["cd_stream_registry.group_iot_consent_officer"],
    ),
    (
        "seed.a07.consent2@1000fix.local",
        "রেজাউল করিম (IoT Consent Officer)",
        ["cd_stream_registry.group_iot_consent_officer"],
    ),
    (
        "seed.fin.admin@1000fix.local",
        "কামরুল হাসান (Accounting Administrator)",
        [
            "account.group_account_manager",
            "cd_entity_config.group_dofa_tier_3",
            "cd_partner.group_fix_referral_manager",
        ],
    ),
    (
        # The run's approver, the instruction's authoriser and its releaser are three
        # different people (M52-6, M50-1), so a payment needs three Administrators.
        "seed.fin.treasury@1000fix.local",
        "তৌহিদুল ইসলাম (Treasury Releaser)",
        ["account.group_account_manager"],
    ),
    (
        # Treasury authorisers must hold the DOFA tier AND be an Accounting
        # Administrator (M50-1); without this only `admin` could clear the bands.
        "seed.fin.cfo@1000fix.local",
        "শারমিন সুলতানা (CFO)",
        [
            "account.group_account_manager",
            "cd_tax_engine_bd.group_tax_filing_approver",
            "cd_entity_config.group_dofa_tier_5",
        ],
    ),
]

Users = env["res.users"].with_context(no_reset_password=True)
base_user = env.ref("base.group_user")
# Every company, so a record in any of them finds its approver.
companies = env["res.company"].search([])
home = env.ref("base.main_company")
made, extended, missing = [], [], []
# FIX_APPOINT_ONLY=seed.fin. limits a run to one area's logins, so deploying one
# area's staffing does not also appoint every other area's synthetic approvers.
only = __import__("os").environ.get("FIX_APPOINT_ONLY", "")
for login, name, xmlids in APPROVERS:
    if not login.startswith(only):
        continue
    groups = [env.ref(x, raise_if_not_found=False) for x in xmlids]
    missing += [x for x, g in zip(xmlids, groups, strict=True) if not g]
    groups = [g for g in groups if g]
    if not groups:
        continue
    user = Users.search([("login", "=", login)], limit=1)
    if not user:
        user = Users.create(
            {
                "name": name,
                "login": login,
                "email": login,
                "password": login,
                "group_ids": [(6, 0, [base_user.id] + [g.id for g in groups])],
                "company_id": home.id,
                "company_ids": [(6, 0, companies.ids)],
            }
        )
        made.append(login)
    elif any(g not in user.group_ids for g in groups) or companies - user.company_ids:
        user.write(
            {
                "group_ids": [(4, g.id) for g in groups],
                "company_ids": [(4, c.id) for c in companies],
            }
        )
        extended.append(login)
env.cr.commit()
print("appoint-approvers:", {"created": len(made), "extended": len(extended), "missing": missing})
