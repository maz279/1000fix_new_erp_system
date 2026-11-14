# cd_party_master — M33 Customer & Party Master (P03-M05).
# The party kernel: a SINGLE res.partner holds MULTIPLE roles simultaneously.
# Do NOT model seller, customer, vendor and partner as separate master records
# joined by reference — violating this produces exactly the duplicate-identity
# problem the programme exists to remove, and it is unrecoverable.
{
    "name": "1000FiX Party Master",
    "summary": "The party kernel: multi-role res.partner, identity documents via residency, consent registry, dedup engine",
    "description": """
CD-M33-01: the party kernel (M33).

THE design rule (TSS section 3.2): one res.partner holds multiple
fix.party.role records. A party that is a customer AND a vendor AND a
brand-partner is ONE record with three role records — not three masters.

Owns:
- fix.party.role (multi-role: customer, vendor, seller, brand-partner, employee...)
- fix.party.hierarchy (corporate structures)
- fix.identity.document (NID, passport, TIN — routed through residency to Z4)
- fix.party.classification (customer classification)
- fix.consent (PDPA consent capture, withdrawal, transparency)
- fix.dedup.rule (golden-record dedup, consuming M64-core governance)

M33 rebuild (2026-10-27) adds the registry-screen surfaces:
- fix.transparency.notice (BRU-CPM-08: consent is invalid without a notice version)
- fix.otp.log (contact verification events)
- fix.registration.approval (two-tier chain, BRU-CPM-02)
- fix.party.duplicate + fix.party.merge (supervised merge, reversible, SOD-15)
- fix.party.quality (deterministic scoring, KPI-120)
- fix.rights.request (PDPA data-subject rights, 30-day clock)
- fix.segment / fix.segment.membership (definitions + governed membership)
- res.partner party_status lifecycle (BRU-CPM-13 hard exits)

Credit profile: the model of record is cd_billing_engine's fix.credit.profile
(M20, FR-ARB-030/031) — M33 surfaces it (spec §3.3: M33 holds the value,
M20 enforces at order time); this module adds no competing model.
""",
    "version": "19.0.1.5.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/Party",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_rbac_ext",
        "cd_event_outbox",
        # A03 audit M33-1: registration approval is a routed M63 request.
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_party_master_groups.xml",
        "data/fix_dedup_cron.xml",
        "data/fix_dedup_rules.xml",
        "data/fix_party_master_a03_data.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/fix_party_views.xml",
        "views/fix_party_workspace_views.xml",
        "views/fix_party_surfaces_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M33-01",
    "x_module_id": "M33",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
