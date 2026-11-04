{
    "name": "1000FiX Treasury & Cash",
    "summary": "M50 core: event-driven payment execution, bank statement matching, cash position over M04 drawers (CD-M50-01)",
    "description": """
CD-M50-01: the treasury core.

- fix.payment.execution — EXECUTES payment.requested events raised by M52/M20
  (AR-006 pairs 6/9: no synchronous finance -> treasury call); idempotent on
  the source key (DI-04 — a replayed request never double-pays); publishes
  payment.executed
- fix.bank.statement.line (+auto_match) — the reconciliation ladder's
  in-Odoo half: exact reference match, then amount+date-window
- fix.cash.position — cash position from the posted bank GL, M04 cash
  drawers, petty cash and cash-in-transit, less unconfirmed payments

A08 (2026-10-26): bank account master (BD routing number / account type on
account.journal + res.partner.bank), cash-in-transit, rider COD settlement
(finance side), petty cash imprest, cheque register, gateway/MFS settlement
with three-way match, facilities & covenants, recurring cash items, and the
computed reports (branch cash, 13-week forecast, FX holdings, bank charges).
""",
    "version": "19.0.1.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Finance/Treasury",
    "depends": [
        "base",
        "mail",
        "account",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_front_desk",
        "cd_gl_ext",
        "cd_storefront",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/fix_payroll_treasury_consumers.xml",
        "views/fix_cash_position_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M50-01",
    "x_module_id": "M50",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "G_Finance_and_Treasury",
    "x_tier": "T5",
}
