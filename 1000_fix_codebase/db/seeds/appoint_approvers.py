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

APPROVERS = [
    # DOFA tiers stack (tier 4 implies 3, 2, 1): one holder per tier.
    (
        "seed.dofa.t1@1000fix.local",
        "রাশেদ করিম (DOFA Tier 1)",
        ["cd_entity_config.group_dofa_tier_1", CLAIM_APPROVER],
    ),
    (
        "seed.dofa.t2@1000fix.local",
        "নাসরিন আক্তার (DOFA Tier 2)",
        ["cd_entity_config.group_dofa_tier_2", CLAIM_APPROVER],
    ),
    (
        "seed.dofa.t3@1000fix.local",
        "মাহবুব আলম (DOFA Tier 3)",
        ["cd_entity_config.group_dofa_tier_3", CLAIM_APPROVER],
    ),
    (
        "seed.dofa.t4@1000fix.local",
        "ফারহানা ইসলাম (DOFA Tier 4)",
        ["cd_entity_config.group_dofa_tier_4", CLAIM_APPROVER],
    ),
    (
        "seed.dofa.t5@1000fix.local",
        "আনোয়ার হোসেন (DOFA Tier 5)",
        ["cd_entity_config.group_dofa_tier_5", CLAIM_APPROVER],
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
]

Users = env["res.users"].with_context(no_reset_password=True)
base_user = env.ref("base.group_user")
# Every company, so a record in any of them finds its approver.
companies = env["res.company"].search([])
home = env.ref("base.main_company")
made, extended, missing = [], [], []
for login, name, xmlids in APPROVERS:
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
