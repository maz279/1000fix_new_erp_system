# cd_gl_ext — subledger-to-control reconciliation as a close gate (M19).
#
# A08 audit M19-F10 (FR-FIN-022, BRU-FIN-20 H, AUT-FIN-08): the estate only
# reconciled AR, AP and VAT output on the /p03/gl/recon screen, and the close
# never ran any of it (the Mushak 9.1 VAT step was the only subledger gate).
# The reconciliation maths therefore lives HERE, in the engine: the P03 screen
# and the period close both call subledger_reconciliation_rows(), so there is
# one definition of "reconciled", and the close refuses on a variance.
#
# The four mandatory proofs are the ones AUT-FIN-08 names first:
#   customer AR control, vendor AP control, VAT output, VAT input.
# Each row compares the POSTED GL balance of the control account with the
# sub-ledger's own figure. A control account that cannot be resolved is NOT
# skipped: the row is "not_configured" and the close fails closed naming the
# system parameter to set (FR-FIN-022).

from __future__ import annotations

import logging

from odoo import fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

RULE_IDS = "FR-FIN-022 / BRU-FIN-20 (AUT-FIN-08)"


def _round(value) -> float:
    return round(float(value or 0.0), 2)


def _control(
    env,
    company,
    label,
    subledger=None,
    name_like=None,
    param_codes=(),
    configuration="",
):
    """The control account for one subledger, with the parameter that configures it.

    Resolution order matches the posting engines and /p03/gl/recon:
    the linked statutory chart first, then the Odoo account code named by the
    sub-ledger's system parameter. Returns a dict, or None (the caller then
    reports "not_configured" and the close fails closed)."""
    Chart = env["fix.chart.account"].sudo()
    domain = [("company_id", "=", company.id), ("odoo_account_id", "!=", False)]
    found = Chart
    if name_like:
        # A named control (VAT payable - output / Input VAT) is the most
        # specific match on the chart, exactly as the P03 screen resolves it.
        found = Chart.search([*domain, ("name", "ilike", name_like)], limit=1)
    if not found and subledger:
        found = Chart.search([*domain, ("control_subledger", "=", subledger)], limit=1)
    if found:
        return {
            "label": label,
            "account_code": found.account_code,
            "name": found.name,
            "account": found.odoo_account_id,
            "source": "fix.chart.account",
            "parameter": False,
            "configuration": configuration,
        }

    params = env["ir.config_parameter"].sudo()
    for param in param_codes:
        code = (params.get_param(param) or "").strip()
        if not code:
            continue
        account = (
            env["account.account"]
            .sudo()
            .with_company(company)
            .search(
                [("code", "=", code), ("company_ids", "in", company.id)],
                limit=1,
            )
        )
        if account:
            return {
                "label": label,
                "account_code": account.code,
                "name": account.name or "",
                "account": account,
                "source": param,
                "parameter": param,
                "configuration": configuration,
            }
    return None


def _gl_balance(env, company, account, period_end=None):
    """The POSTED GL balance of a control account through ``period_end``."""
    if not account:
        return None
    domain = [
        ("company_id", "=", company.id),
        ("parent_state", "=", "posted"),
        ("account_id", "=", account.id),
    ]
    if period_end:
        domain.append(("date", "<=", period_end))
    groups = env["account.move.line"].sudo()._read_group(domain, [], ["balance:sum"])
    return round(sum(group[0] or 0.0 for group in groups), 2)


def _takeon_open(env, company, control, period_end=None) -> float:
    """The take-on opening lines (legacy MIG journal) still open on the control
    account at the period end — the same opening balance /p03/gl/recon adds."""
    if not control:
        return 0.0
    domain = [
        ("company_id", "=", company.id),
        ("parent_state", "=", "posted"),
        ("account_id", "=", control["account"].id),
        ("journal_id.code", "=", "MIG"),
    ]
    if period_end:
        domain.append(("date", "<=", period_end))
    lines = env["account.move.line"].sudo().search(domain)
    return round(sum(lines.mapped("amount_residual")), 2)


class _RowBuilder(list):
    """The row list plus the environment/company/period a row is proved in."""

    def __init__(self, env, company, period_end):
        super().__init__()
        self.env = env
        self.company = company
        self.period_end = period_end
        self.configuration = {}


def _row(builder, label, control, subledger_total, breakdown=None):
    rows = builder
    if not control:
        rows.append(
            {
                "label": label,
                "control": None,
                "subledger": None,
                "variance": None,
                "status": "not_configured",
                "breakdown": breakdown or {},
                "rule": RULE_IDS,
                "configuration": rows.configuration.get(label, ""),
            }
        )
        return
    gl = _gl_balance(rows.env, rows.company, control["account"], rows.period_end)
    subledger_total = _round(subledger_total)
    variance = None if gl is None else _round(gl - subledger_total)
    rows.append(
        {
            "label": label,
            "account": "%s %s" % (control["account_code"], control["name"]),
            "odoo_code": control["account"].with_company(rows.company).code,
            "control": gl,
            "subledger": subledger_total,
            "variance": variance,
            "status": ("matched" if variance is not None and abs(variance) < 0.01 else "variance"),
            "breakdown": breakdown or {},
            "rule": RULE_IDS,
        }
    )


def subledger_reconciliation_rows(env, company, period_end=None) -> list[dict]:
    """The four control-account proofs AUT-FIN-08 requires, as of ``period_end``.

    One row per subledger (AR, AP, VAT output, VAT input). ``control`` is the
    posted GL balance and ``subledger`` the owning ledger's figure in the same
    sign convention, so ``variance = control - subledger`` is meaningful:
      - AR: open issued invoices (residual) + take-on opening lines;
      - AP: open posted bills on the payable control + take-on opening lines;
      - VAT output: the Mushak 6.3 register, negated (credit-normal GL sign);
      - VAT input: the supplier Mushak 6.3 VAT on posted bills (debit sign).

    With no ``period_end`` the proof is cumulative, exactly as /p03/gl/recon
    shows it; the close passes its period end so later documents never leak
    into a closed period's proof. A missing control account yields a
    "not_configured" row — never a silent zero-total pass.
    """
    period_end = fields.Date.to_date(period_end) if period_end else None
    builder = _RowBuilder(env, company, period_end)
    builder.configuration = {
        "AR — Trade receivables": (
            "cd_billing_engine.account_code.ar / "
            "cd_gl_ext.ledger_takeon.receivable_account_code, or a fix.chart.account "
            "with control_subledger=receivable"
        ),
        "AP — Trade payables": (
            "cd_gl_ext.ledger_takeon.payable_account_code, or a fix.chart.account "
            "with control_subledger=payable"
        ),
        "VAT output — Mushak 6.3": (
            "cd_tax_engine_bd.vat_output_account_code (default 210100), or a "
            "fix.chart.account named 'VAT payable - output'"
        ),
        "VAT input — supplier Mushak 6.3": (
            "cd_tax_engine_bd.vat_input_account_code, or a fix.chart.account named "
            "'Input VAT' (no safe default exists for the input-VAT role)"
        ),
    }

    # ------------------------------------------------------------- AR control
    control = _control(
        env,
        company,
        "AR — Trade receivables",
        subledger="receivable",
        param_codes=(
            "cd_billing_engine.account_code.ar",
            "cd_gl_ext.ledger_takeon.receivable_account_code",
        ),
        configuration=builder.configuration["AR — Trade receivables"],
    )
    invoices = 0.0
    if "fix.ar.invoice" in env:
        domain = [
            ("state", "not in", ("draft", "cancelled")),
            ("company_id", "=", company.id),
        ]
        if period_end:
            domain.append(("invoice_date", "<=", period_end))
        invoices = round(
            sum(env["fix.ar.invoice"].sudo().search(domain).mapped("amount_residual")), 2
        )
    opening = _takeon_open(env, company, control, period_end)
    _row(
        builder,
        "AR — Trade receivables",
        control,
        invoices + opening,
        {"open_invoices": invoices, "takeon_open": opening},
    )

    # ------------------------------------------------------------- AP control
    control = _control(
        env,
        company,
        "AP — Trade payables",
        subledger="payable",
        param_codes=("cd_gl_ext.ledger_takeon.payable_account_code",),
        configuration=builder.configuration["AP — Trade payables"],
    )
    bills = 0.0
    if control and "fix.vendor.invoice" in env:
        domain = [
            ("company_id", "=", company.id),
            ("move_id.state", "=", "posted"),
        ]
        if period_end:
            domain.append(("move_id.date", "<=", period_end))
        lines = (
            env["fix.vendor.invoice"]
            .sudo()
            .search(domain)
            .mapped("move_id.line_ids")
            .filtered(lambda line: line.account_id == control["account"])
        )
        bills = round(sum(lines.mapped("amount_residual")), 2)
    opening = _takeon_open(env, company, control, period_end)
    _row(
        builder,
        "AP — Trade payables",
        control,
        bills + opening,
        {"open_bills": bills, "takeon_open": opening},
    )

    # ------------------------------------------------------- VAT output control
    control = _control(
        env,
        company,
        "VAT output — Mushak 6.3",
        subledger="tax",
        name_like="VAT payable - output",
        param_codes=("cd_tax_engine_bd.vat_output_account_code",),
        configuration=builder.configuration["VAT output — Mushak 6.3"],
    )
    register_vat = 0.0
    if "fix.mushak.register" in env:
        domain = [("company_id", "=", company.id)]
        if period_end:
            domain.append(("invoice_date", "<=", period_end))
        register_vat = round(
            sum(env["fix.mushak.register"].sudo().search(domain).mapped("vat_amount")), 2
        )
    # The register states output VAT as a positive liability; the GL control is
    # credit-normal (negative balance), so the sub-ledger figure is negated.
    _row(
        builder,
        "VAT output — Mushak 6.3",
        control,
        -register_vat,
        {"register_output_vat": register_vat, "sign": "credit-normal (negated)"},
    )

    # -------------------------------------------------------- VAT input control
    control = _control(
        env,
        company,
        "VAT input — supplier Mushak 6.3",
        subledger="tax",
        name_like="Input VAT",
        param_codes=("cd_tax_engine_bd.vat_input_account_code",),
        configuration=builder.configuration["VAT input — supplier Mushak 6.3"],
    )
    input_vat = 0.0
    if "fix.vendor.invoice" in env:
        domain = [
            ("company_id", "=", company.id),
            ("move_id.state", "=", "posted"),
        ]
        if period_end:
            domain += [("invoice_date", "<=", period_end), ("move_id.date", "<=", period_end)]
        vendor_bills = env["fix.vendor.invoice"].sudo().search(domain)
        field = "vat_amount_bdt" if "vat_amount_bdt" in vendor_bills._fields else "vat_amount"
        input_vat = round(sum(vendor_bills.mapped(field)), 2)
    _row(
        builder,
        "VAT input — supplier Mushak 6.3",
        control,
        input_vat,
        {"supplier_input_vat": input_vat},
    )
    return list(builder)


def _period_vat_return(env, company, period_end):
    if "fix.vat.return" not in env:
        return None
    period = period_end.strftime("%Y-%m")
    return (
        env["fix.vat.return"]
        .sudo()
        .search([("company_id", "=", company.id), ("period", "=", period)], limit=1)
    )


def assert_subledgers_reconciled(env, company, period_end) -> list[dict]:
    """Raise unless every subledger control proof is reconciled at ``period_end``.

    Two failure modes, both hard blocks (FR-FIN-022 / BRU-FIN-20):
      - a control account cannot be resolved ("missing config"): the close
        fails closed and names the system parameter to set;
      - a proof shows a variance: the close names the account and the amount.
    The period's Mushak 9.1 return is reused when present: a pending
    reconciliation is run through its own action_subledger_reconciliation()
    (never re-implemented here), and a recorded variance blocks.
    """
    period_end = fields.Date.to_date(period_end)
    if not period_end:
        raise UserError("The subledger close gate needs the period end it proves (FR-FIN-022).")
    rows = subledger_reconciliation_rows(env, company, period_end)

    # Reuse the VAT return's own reconciliation when it has not run yet: its
    # action reads the same control accounts, and its refusal names the missing
    # VAT account parameter (fail closed, never a silent pass).
    vat_return = _period_vat_return(env, company, period_end)
    if vat_return and vat_return.state != "draft" and vat_return.subledger_status == "pending":
        vat_return.action_subledger_reconciliation()
        vat_return = _period_vat_return(env, company, period_end)
    vat_parts = []
    if vat_return and vat_return.subledger_status == "variance_detected":
        vat_parts.append(
            "Mushak 9.1 return %s: output variance %.2f, input variance %.2f"
            % (
                vat_return.period,
                vat_return.subledger_output_variance or 0.0,
                vat_return.subledger_input_variance or 0.0,
            )
        )

    missing = [row for row in rows if row["status"] == "not_configured"]
    if missing:
        raise UserError(
            "Period %s cannot close: the %s reconciliation cannot be computed — no control "
            "account is configured. Set %s (%s)."
            % (
                period_end,
                ", ".join(row["label"] for row in missing),
                "; ".join(row["configuration"] for row in missing),
                RULE_IDS,
            )
        )

    variances = [row for row in rows if row["status"] == "variance"]
    parts = [
        "%s: control account %s [%s] is out by %.2f (GL %.2f vs sub-ledger %.2f)"
        % (
            row["label"],
            row["account"],
            row["odoo_code"],
            row["variance"],
            row["control"],
            row["subledger"],
        )
        for row in variances
    ] + vat_parts
    if parts:
        raise UserError(
            "Period %s cannot close: sub-ledger reconciliation variance(s): %s. An "
            "unexplained difference blocks the hard close (%s)."
            % (period_end, "; ".join(parts), RULE_IDS)
        )
    return rows
