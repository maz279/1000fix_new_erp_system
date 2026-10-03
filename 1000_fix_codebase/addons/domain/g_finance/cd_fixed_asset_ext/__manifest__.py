# cd_fixed_asset_ext — M49 Fixed Assets & Capital Investment (P08-M08).
{
    "name": "1000FiX Fixed Assets",
    "summary": "M49: fixed assets on M19's seam, straight-line depreciation (100% covered), CWIP capitalisation; M54 budget link advisory (CD-M49-nn)",
    "description": """
CD-M49-01 (P08-M08) — fixed assets on the seam M19 built (P06-M01-T07):

- fix.fixed.asset — gross (Monetary), life, salvage; straight-line
  monthly depreciation computed by a PURE function (100% coverage,
  DoD-03 — a financial path); capitalised FROM the M19 seam
  (fix.fixed.asset.seam): finance posts capitalisation events, M49
  consumes
- fix.cwip.entry — capital-work-in-progress: costs accumulate; the
  CAPITALISE action creates the fixed asset from the accumulated total
- THE M49 <-> M54 BREAK (AR-006 4.1 pair 14): M54 consumes
  depreciation EVENTS (depreciation.accrued published monthly); M49
  does NOT read budgets — budget_reference is an ADVISORY char (5.4
  NOT-A-PREREQ), never a foreign key into M54
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Accounting/Fixed Assets",
    "depends": ["base", "mail", "cd_entity_config", "cd_gl_ext",
                 "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/fix_fixed_asset_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M49-01",
    "x_module_id": "M49",
    "x_wave": "W5",
    "x_owner": "Finance",
    "x_category": "G_Finance_and_Statutory",
    "x_tier": "T9",
}
