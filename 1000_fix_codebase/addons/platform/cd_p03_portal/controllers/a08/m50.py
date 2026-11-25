# A08 · M50 Treasury & Banking — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action),
# plus the module's KPI hook and computed reports (/p03/model/report).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting groups apply).
#
# A08 workflow audit (M50-4, X02): every workflow step is an ACTION here and
# runs the model's own checks (two-person release, DOFA routing, maker-checker,
# imported-statement evidence); no state, stamp or match field is writable
# from the workspace forms (the models guard them; writable.py is generated
# from the forms in static/src/a08/m50.js). KPIs and reports read in the
# caller's environment, filtered to the caller's company.
#
# The computations live in cd_cash_position (models/treasury_reports.py) and
# are imported lazily: cd_p03_portal does not depend on the treasury addon,
# so a database without it gets an honest "not installed" answer.
SURFACES = {
    "fix.payment.execution": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_prepare",
            "action_request_approval",
            "action_recall_approval",
            "action_release",
            "action_confirm_bank",
            "action_mark_failed",
            "action_retry",
            "action_cancel",
        },
    },
    "fix.bank.statement.import": {"order": "id desc", "limit": 100, "actions": {"action_import"}},
    "fix.bank.reconciliation": {
        "order": "period desc, journal_id, id desc",
        "limit": 100,
        "actions": {"action_prepare", "action_submit", "action_review", "action_return"},
    },
    "fix.bank.reconciliation.line": {
        "order": "reconciliation_id desc, date, id",
        "limit": 300,
        "actions": {"action_explain"},
    },
    "fix.bank.statement.line": {
        "order": "date desc, id desc",
        "limit": 200,
        "actions": {
            "auto_match",
            "action_confirm_manual_match",
            "action_post_bank_charge",
            "action_apply_rules",
        },
    },
    "fix.cash.position": {
        "order": "as_of desc, id desc",
        "limit": 50,
        "actions": {"action_take_snapshot"},
    },
    "account.journal": {"order": "sequence, id", "limit": 100, "actions": set()},
    "fix.cash.deposit": {
        "order": "business_date desc, id desc",
        "limit": 200,
        "actions": {"action_dispatch", "action_resolve_variance", "action_cancel"},
    },
    "fix.cod.settlement": {
        "order": "settlement_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_load_orders",
            "action_submit",
            "action_approve_shortage",
            "action_settle",
            "action_dispute",
            "action_mark_recovered",
        },
    },
    # G10 (owner decision 12 Nov 2026): a third-party courier's COD payout.
    "fix.courier.remittance": {
        "order": "remittance_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_load_orders",
            "action_remove_orders",
            "action_submit",
            "action_settle",
            "action_dispute",
        },
    },
    "fix.imprest.fund": {"order": "name", "limit": 100, "actions": {"action_request_topup"}},
    "fix.imprest.voucher": {
        "order": "voucher_date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_post", "action_reject"},
    },
    "fix.imprest.topup": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_approve", "action_pay", "action_reject"},
    },
    "fix.imprest.count": {
        "order": "count_date desc, id desc",
        "limit": 100,
        "actions": {"action_reconcile", "action_book_variance"},
    },
    "fix.cheque": {
        "order": "cheque_date desc, id desc",
        "limit": 200,
        "actions": {"action_deposit", "action_bounce", "action_cancel"},
    },
    "fix.cheque.book": {
        "order": "journal_id, first_number",
        "limit": 100,
        "actions": {"action_close"},
    },
    "fix.gateway.settlement": {
        "order": "settlement_date desc, id desc",
        "limit": 100,
        "actions": {"action_import_report", "action_match", "action_post"},
    },
    "fix.gateway.settlement.line": {
        "order": "batch_id desc, id",
        "limit": 300,
        "actions": {"action_open_case"},
    },
    "fix.bank.facility": {
        "order": "name",
        "limit": 100,
        "actions": {
            "action_activate",
            "action_generate_schedule",
            "action_close",
            "action_acknowledge_expiry",
        },
    },
    "fix.facility.amendment": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.facility.repayment": {
        "order": "due_date, id",
        "limit": 300,
        "actions": {"action_pay", "action_confirm_bank", "action_withdraw_payment"},
    },
    "fix.facility.covenant": {
        "order": "facility_id, id",
        "limit": 200,
        "actions": {"action_approve", "action_test"},
    },
    "fix.cash.forecast.item": {"order": "direction, name", "limit": 200, "actions": set()},
    # M50 capture audit (2026-11-17): the five records the pages could not
    # capture. Every decision is an action with its own maker-checker.
    "fix.bank.mandate": {
        "order": "journal_id, state, valid_from desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_approve", "action_reject", "action_revoke"},
        "pickers": {
            "journal_id": [("type", "=", "bank")],
            "supersedes_id": [("state", "=", "active")],
        },
    },
    "fix.bank.matching.rule": {
        "order": "sequence, id",
        "limit": 200,
        "actions": {
            "action_submit",
            "action_approve",
            "action_reject",
            "action_retire",
            "action_new_version",
            "action_test",
        },
        "pickers": {"journal_id": [("type", "=", "bank")]},
    },
    "fix.settlement.exception": {
        "order": "state, opened_on, id",
        "limit": 200,
        "actions": {
            "action_raise_with_provider",
            "action_propose",
            "action_approve",
            "action_return",
        },
        "pickers": {
            "line_id": [("match_state", "!=", "matched")],
            "owner_id": [("share", "=", False)],
        },
    },
    "fix.cash.forecast.version": {
        "order": "generated_at desc, id desc",
        "limit": 100,
        "actions": {"action_measure"},
    },
    "fix.cash.forecast.version.line": {
        "order": "version_id desc, horizon",
        "limit": 300,
        "actions": set(),
    },
    "fix.fx.conversion": {
        "order": "deal_date desc, id desc",
        "limit": 100,
        "actions": {"action_submit", "action_approve", "action_cancel"},
        "pickers": {
            "from_journal_id": [("type", "=", "bank")],
            "to_journal_id": [("type", "=", "bank")],
        },
    },
}


_NOT_INSTALLED = {
    "cols": [],
    "rows": [],
    "empty": "The treasury module (cd_cash_position) is not installed on this database.",
}


def _engine(env):
    if "fix.cash.position" not in env:
        return None
    from odoo.addons.cd_cash_position.models import treasury_reports

    return treasury_reports


def _report(name):
    def run(env, date_from=None, date_to=None, **params):
        engine = _engine(env)
        if engine is None:
            return dict(_NOT_INSTALLED)
        return engine.REPORTS[name](env, date_from=date_from, date_to=date_to, **params)

    run.__name__ = "m50_%s" % name
    return run


REPORTS = {
    name: _report(name)
    for name in (
        "daily_cash_position",
        "bank_recon_summary",
        "gateway_recon",
        "cod_report",
        "branch_cash",
        "cash_forecast",
        "bank_charges",
        "fx_holdings",
        # R8 (CIH capability report, 2026-11-09): the cheque pack —
        # register, PDC maturity, stale aging, clearing latency, GL tie-out.
        "cheque_register",
    )
}


def kpis(env):
    """M50 tiles: cash position (GL bank + drawers + petty + in transit - not
    yet bank-confirmed payments), branch cash not yet deposited (30 days),
    payments awaiting the bank's confirmation."""
    engine = _engine(env)
    if engine is None:
        return {}
    return engine.kpis(env)
