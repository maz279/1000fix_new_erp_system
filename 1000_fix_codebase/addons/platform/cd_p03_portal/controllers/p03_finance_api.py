# P03 finance KPI endpoint — real aggregates from the g_finance subledgers.
#
# Serves /p03/finance/kpis for the workspace module view: per-module metric
# values keyed exactly as the A08 kpi `m` keys in p03_modules_meta.js. Every
# figure is a live read of the real Odoo models (fix.ar.invoice, Mushak
# register, vendor bills, bank statement lines, fixed assets, payout runs,
# budgets, account.move) — nothing is fabricated. Metrics whose model is
# absent or unreadable come back as None and the workspace keeps the honest
# placeholder. Read-only, internal-user only (NVR-22, same as /p03/registry).
import datetime
import logging

from odoo import http
from odoo.http import request

from . import a08
from .p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)


def _month_start():
    today = datetime.date.today()
    return datetime.date(today.year, today.month, 1)


class P03FinanceApiController(http.Controller):
    """Real finance KPIs for the A08 module tiles."""

    @http.route("/p03/finance/kpis", type="jsonrpc", auth="user", readonly=True)
    def finance_kpis(self, module=None, **kw):
        _require_internal(request.env)
        env = request.env
        ms = _month_start()
        out = {}

        def count(model, domain):
            try:
                return env[model].search_count(domain)
            except Exception:
                return None

        def total(model, domain, field):
            try:
                recs = env[model].search(domain)
                return sum(recs.mapped(field)) or 0.0
            except Exception:
                return None

        if module in (None, "M19"):
            m19 = {
                "posted_moves_mtd": count(
                    "account.move", [("state", "=", "posted"), ("date", ">=", ms)]
                ),
                "open_period_closes": count(
                    "fix.period.close", [("state", "in", ("open", "in_progress", "ready_to_close"))]
                ),
                # the maker-checker review queue (drafts awaiting a checker)
                "draft_journals": count("account.move", [("state", "=", "draft")]),
            }
            try:
                # Revenue MTD = net posted movement of income accounts
                # (credit - debit); TB imbalance = debit vs credit of the
                # fiscal year's posted lines. None when the ledger is empty.
                income = env["account.move.line"]._read_group(
                    [
                        ("parent_state", "=", "posted"),
                        ("date", ">=", ms),
                        ("company_id", "=", env.company.id),
                        ("account_id.internal_group", "=", "income"),
                    ],
                    [],
                    ["debit:sum", "credit:sum"],
                )
                revenue = sum(g[1] or 0.0 for g in income) - sum(g[0] or 0.0 for g in income)
                m19["revenue_mtd"] = round(revenue, 2) if revenue else None

                fy_start = datetime.date(ms.year if ms.month >= 7 else ms.year - 1, 7, 1)
                fy = env["account.move.line"]._read_group(
                    [
                        ("parent_state", "=", "posted"),
                        ("date", ">=", fy_start),
                        ("company_id", "=", env.company.id),
                    ],
                    [],
                    ["debit:sum", "credit:sum"],
                )
                debit = sum(g[0] or 0.0 for g in fy)
                credit = sum(g[1] or 0.0 for g in fy)
                m19["tb_imbalance"] = round(debit - credit, 2) if (debit or credit) else None
            except Exception:
                m19["revenue_mtd"] = None
                m19["tb_imbalance"] = None
            out["M19"] = m19

        if module in (None, "M20"):
            m20 = {
                "ar_invoices_mtd": count("fix.ar.invoice", [("invoice_date", ">=", ms)]),
                "credit_notes_total": count("fix.credit.note", []),
            }
            try:
                Invoice = env["fix.ar.invoice"]
                today = datetime.date.today()
                # Overdue > 60d past the customer's OWN terms (registry KPI 3)
                overdue_sum = 0.0
                for inv in Invoice.search([("state", "=", "issued")]):
                    if inv.amount_residual <= 0.005:
                        continue
                    days_past = (today - inv.invoice_date).days - inv._payment_terms_days()
                    if days_past > 60:
                        overdue_sum += inv.amount_residual
                m20["overdue_gt_60d"] = round(overdue_sum, 2)
                # DSO: average invoice→paid days over the trailing 90 days
                paid = Invoice.search(
                    [
                        ("state", "in", ("paid", "credited")),
                        ("paid_date", ">=", today - datetime.timedelta(days=90)),
                    ]
                ).filtered(lambda i: i.paid_date and i.invoice_date)
                m20["dso"] = (
                    round(sum((i.paid_date - i.invoice_date).days for i in paid) / len(paid), 1)
                    if paid
                    else None
                )
                # Auto-generation % and within-1h % (NFR-040; manual rows
                # carry no generation timing and are excluded from it)
                issued_all = Invoice.search([("state", "!=", "draft")])
                if issued_all:
                    auto = issued_all.filtered(lambda i: i.source_model != "manual")
                    m20["auto_generated_pct"] = round(len(auto) / len(issued_all) * 100.0, 1)
                else:
                    m20["auto_generated_pct"] = None
                timed = issued_all.filtered(lambda i: i.generation_seconds)
                m20["within_1h_pct"] = (
                    round(
                        len(timed.filtered(lambda i: i.generation_seconds <= 3600.0))
                        / len(timed)
                        * 100.0,
                        1,
                    )
                    if timed
                    else None
                )
            except Exception:
                m20["overdue_gt_60d"] = None
                m20["dso"] = None
                m20["auto_generated_pct"] = None
                m20["within_1h_pct"] = None
            out["M20"] = m20

        if module in (None, "M50"):
            bank_total = count("fix.bank.statement.line", [])
            bank_auto = count("fix.bank.statement.line", [("match_state", "=", "auto")])
            out["M50"] = {
                "unreconciled_bank_lines": count(
                    "fix.bank.statement.line", [("match_state", "=", "unmatched")]
                ),
                "auto_match_rate": (round(bank_auto / bank_total * 100.0, 1) if bank_total else 0.0)
                if bank_total is not None and bank_auto is not None
                else None,
            }

        if module in (None, "M51"):
            out["M51"] = {
                "vat_collected_mtd": total(
                    "fix.mushak.register", [("invoice_date", ">=", ms)], "vat_amount"
                ),
                "mushak_records": count("fix.mushak.register", []),
                "vat_returns_count": count("fix.vat.return", []),
            }

        if module in (None, "M52"):
            out["M52"] = {
                "vendor_bills_open": count("fix.vendor.invoice", []),
                "match_exceptions": count(
                    "fix.vendor.invoice", [("match_state", "in", ("unmatched", "blocked"))]
                ),
                "expense_claims_pending": count(
                    "fix.expense.claim", [("state", "in", ("draft", "submitted"))]
                ),
            }

        if module in (None, "M53"):
            out["M53"] = {
                "commission_accrued_count": count(
                    "fix.commission.ledger", [("state", "=", "accrued")]
                ),
                "payout_runs_open": count(
                    "fix.payout.run", [("state", "in", ("draft", "approved", "executing"))]
                ),
                "revenue_schedules_count": count("fix.revenue.schedule", []),
            }

        if module in (None, "M49"):
            out["M49"] = {
                "assets_gross_block": total("fix.fixed.asset", [], "gross"),
                "cwip_open_count": count("fix.cwip.entry", [("state", "=", "open")]),
            }

        if module in (None, "M54"):
            out["M54"] = {
                "budget_total_variance": total("fix.budget", [], "variance"),
                "budgets_count": count("fix.budget", []),
            }

        # Per-module metrics declared in controllers/a08/<module>.py as an
        # optional kpis(env) -> {metric_key: value or None}.
        for code, mod in a08.MODULES.items():
            hook = getattr(mod, "kpis", None)
            if hook and module in (None, code):
                try:
                    out.setdefault(code, {}).update(hook(env) or {})
                except Exception:
                    _logger.exception("p03 finance kpis hook failed for %s", code)
        return out
