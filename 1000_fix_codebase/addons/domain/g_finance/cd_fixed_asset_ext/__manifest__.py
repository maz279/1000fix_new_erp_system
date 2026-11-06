# cd_fixed_asset_ext — M49 Fixed Assets & Capital Investment (P08-M08, A08 rebuild).
{
    "name": "1000FiX Fixed Assets",
    "summary": "M49: capex requests and capital budget, asset register, CWIP, dual-book depreciation with GL posting, revaluation/impairment, disposal, verification, IFRS 16 leases",
    "description": """
CD-M49-01 (P08-M08, rebuilt for A08) — fixed assets on the seam M19 built:

- fix.capex.budget / fix.capex.request — request -> approve (SoD, within the
  budget's available amount) -> CWIP project -> capitalised asset
- fix.fixed.asset — the register (tag, category, branch, custodian);
  straight-line monthly charge from a PURE function (DoD-03)
- fix.cwip.entry — capital work in progress; CAPITALISE posts Dr asset /
  Cr CWIP and registers the asset
- fix.asset.depreciation.run — monthly dual-book run: accounting book
  (IAS 16 straight-line, GL posted per category) and tax book (ITA 2023
  Third Schedule reducing balance, effective-dated master data, memo book);
  one line per asset, book and month (idempotent)
- fix.asset.transfer — branch / custodian moves with history
- fix.asset.revaluation — IAS 16 revaluation, IAS 36 impairment and reversal
- fix.asset.disposal — sale / scrap / write-off with gain or loss posting
- fix.asset.verification.campaign — physical verification by tag scan
- fix.lease — IFRS 16 branch leases: liability at the IBR, ROU asset,
  effective-interest schedule, monthly postings
- THE M49 <-> M54 BREAK (AR-006 4.1 pair 14): M54 consumes depreciation
  EVENTS (depreciation.accrued, now published only for POSTED charges)
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Accounting/Fixed Assets",
    "depends": [
        "base",
        "mail",
        "account",
        "hr",
        "cd_entity_config",
        "cd_gl_ext",
        "cd_event_outbox",
        # A08: routed DOFA approvals (M63) and the M51 Third Schedule rates
        "cd_workflow_engine",
        "cd_tax_engine_bd",
        # A08 M49-10: a capital purchase order carries its capex reference
        "cd_requisition",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/fix_asset_sequence_data.xml",
        "data/fix_asset_master_data.xml",
        "data/fix_asset_consumers.xml",
        "data/fix_asset_cron.xml",
        "views/fix_fixed_asset_views.xml",
        "views/fix_asset_lifecycle_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M49-01",
    "x_module_id": "M49",
    "x_wave": "W5",
    "x_owner": "Finance",
    "x_category": "G_Finance_and_Statutory",
    "x_tier": "T9",
}
