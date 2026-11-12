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

A08 workflow audit (2026-11-04): two-person payment release with DOFA
routing above the single-releaser ceiling (M63), pinned instructions, bank
confirmation only from an imported statement debit, guarded state / stamp /
match fields on every treasury model, cheque books and bounce unwinding,
imprest count against pending vouchers, frozen facility schedules with
amendments, approved covenants, the payment.requested consumer and the
auto-match / covenant crons.

Bank master take-on (2026-11-09): the res.bank.branch directory — the
Bank -> Branch -> Account middle layer that sources the 9-digit BEFTN
routing number per branch (R4 of the bank-list capability report); bank
accounts gain a bank_branch_id that defaults institution, branch name and
routing from the directory.

Courier COD remittance (G10, owner decision 2026-11-12): the payout of a
third-party courier (Pathao, RedX, Steadfast) for the delivered COD orders it
carried, net of its charges: Dr bank (net) + Dr courier charges / Cr COD
clearing (gross), prepared by an accountant and settled by a different
Accounting Administrator.
""",
    "version": "19.0.1.4.0",
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
        # cd_storefront: the COD settlement model carries a One2many to
        # fix.storefront.order (a load-time field), and through it this
        # module also sees fix.ar.receipt for the cheque-bounce re-open.
        "cd_storefront",
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        # A04 report C7: consumers of the storefront refund and bond
        # encashment hand-offs.
        "data/fix_a04_consumers.xml",
        # A05 report cross-area follow-up: the e-waste settlement money leg.
        "data/fix_a05_consumers.xml",
        # A09 Update 3/4: payroll payments reach treasury (M50).
        "data/fix_payroll_treasury_consumers.xml",
        # A08 B1 (F1/E12): deposit matching, LC expiry and the payment
        # consumer crons.
        "data/fix_treasury_automation.xml",
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
