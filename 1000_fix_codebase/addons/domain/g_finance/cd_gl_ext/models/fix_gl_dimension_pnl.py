# cd_gl_ext — branch / operating-unit profit-and-loss derivation (M19-F4).
#
# A08 audit M19-F4 (FR-FIN-031 P0, BR-FIN-008, AC-15): every statement filtered
# by company + dates only, so the 73 branches and their operating units had no
# P&L even though every posting carries the seven dimensions on
# fix.journal.dimension. The slice lives HERE, in the engine, not in the portal
# controller, so the P03 screens, a report pack and a close check all read the
# same computation (and the same unallocated bucket).
#
# The figures are the POSTED account.move.line rows of the company — the same
# rows compute_pnl() reads — joined to their dimension rows. A line without a
# dimension row (the M19-F6 take-on lanes carry none) is NOT dropped: it lands
# in the "unallocated" bucket, and the bucket totals plus the allocated rows
# always tie exactly to compute_pnl() for the same window.
from __future__ import annotations

import logging
from decimal import Decimal

from odoo import fields, models
from odoo.exceptions import UserError

from .fix_fiscal_year_ext import compute_pnl

_logger = logging.getLogger(__name__)

# The dimension slices a report pack may ask for. "branch" and
# "operating_unit" are the BR-FIN-008 requirements; the rest are the other
# five dimensions of FR-FIN-003, free to slice because they ride the same row.
DIMENSION_GROUPS = {
    "branch": {
        "field": "branch_id",
        "label": "Branch",
        "model": "fix.branch",
        "code_field": "code",
        "name_field": "name",
    },
    "operating_unit": {
        "field": "operating_unit_id",
        "label": "Operating Unit",
        "model": "operating.unit",
        "code_field": "code",
        "name_field": "name",
    },
    "business_line": {
        "field": "business_line",
        "label": "Business Line",
        "model": None,
    },
    "cost_centre": {
        "field": "cost_centre",
        "label": "Cost Centre",
        "model": None,
    },
    "project": {
        "field": "project_ref",
        "label": "Project / Contract",
        "model": None,
    },
    "brand": {
        "field": "brand",
        "label": "Brand / OEM",
        "model": None,
    },
    "channel": {
        "field": "channel",
        "label": "Service Channel",
        "model": None,
    },
}

UNALLOCATED_KEY = "unallocated"
PL_GROUPS = ("income", "expense")
_TWO_PLACES = Decimal("0.01")


def _money(value) -> Decimal:
    """A journal-item amount as an exact 2-place Decimal (never float math)."""
    return Decimal(str(value or 0.0)).quantize(_TWO_PLACES)


def _plain(value: Decimal) -> float:
    """A JSON/report float, never -0.0 (an empty slice printed as '-0')."""
    return float(value) + 0.0


def _dimension_key(dimension, spec) -> int | str | None:
    """The slice key of one dimension row: an id for a many2one dimension, the
    trimmed tag for a free-form one, None when the dimension is empty."""
    value = dimension[spec["field"]]
    if isinstance(value, models.BaseModel):
        return value.id or None
    value = (value or "").strip()
    return value or None


def _label(env, spec, key) -> tuple[str, dict]:
    """(display label, identifying fields) for one slice key."""
    if key is None:
        return "Unallocated (no %s dimension)" % spec["label"].lower(), {}
    if not spec.get("model"):
        return str(key), {"dimension_value": key}
    record = env[spec["model"]].sudo().browse(key)
    if not record.exists():
        return "%s #%s" % (spec["label"], key), {"dimension_value": key}
    code = record[spec["code_field"]] if spec.get("code_field") else ""
    name = record[spec["name_field"]] if spec.get("name_field") else ""
    label = ("%s " % code if code else "") + (name or "#%s" % key)
    fields_ = {"dimension_value": key}
    if spec["field"] == "branch_id":
        fields_["branch_id"] = key
        fields_["branch_code"] = code or ""
        fields_["branch_name"] = name or ""
    elif spec["field"] == "operating_unit_id":
        fields_["operating_unit_id"] = key
        fields_["operating_unit_code"] = code or ""
        fields_["operating_unit_name"] = name or ""
    return label, fields_


def _empty_bucket() -> dict:
    return {"revenue": Decimal("0.00"), "expense": Decimal("0.00"), "line_count": 0, "accounts": {}}


def _bucket_totals(bucket: dict) -> dict:
    revenue = bucket["revenue"]
    expense = bucket["expense"]
    return {
        "revenue": _plain(revenue),
        "expense": _plain(expense),
        "net_profit": _plain(revenue - expense),
        "line_count": bucket["line_count"],
        "account_count": len(bucket["accounts"]),
    }


def _account_rows(bucket: dict) -> list[dict]:
    rows = []
    for account in bucket["accounts"].values():
        balance = account["balance"]
        if account["internal_group"] == "income":
            revenue, expense = -balance, Decimal("0.00")
        else:
            revenue, expense = Decimal("0.00"), balance
        rows.append(
            {
                "account_code": account["account_code"],
                "account_name": account["account_name"],
                "internal_group": account["internal_group"],
                "balance": _plain(balance),
                "revenue": _plain(revenue),
                "expense": _plain(expense),
            }
        )
    return sorted(rows, key=lambda row: row["account_code"])


def pnl_by_branch(env, date_from, date_to, group_by: str = "branch", company=None) -> dict:
    """Revenue / expense / net profit for a date window, sliced by a dimension.

    ``group_by`` is one of DIMENSION_GROUPS — "branch" (the BR-FIN-008 slice),
    "operating_unit", or any other posting dimension. ``company`` defaults to
    ``env.company`` and may be a record or an id.

    Every posted income/expense line of the window is bucketed by the
    dimension row attached to it; a line with no dimension row, or with the
    dimension empty, is reported in the ``unallocated`` bucket (never
    dropped). The returned ``totals`` reconcile exactly to
    ``compute_pnl(env, company, date_from, date_to)["net_profit"]`` — the
    test suite asserts that equality.

    Returns a report-pack-shaped dict: rows (with per-account detail) + totals
    + the unallocated bucket + the tie flag.
    """
    if group_by not in DIMENSION_GROUPS:
        raise UserError(
            "Unknown P&L slice %r (FR-FIN-031). Choose one of: %s."
            % (group_by, ", ".join(sorted(DIMENSION_GROUPS)))
        )
    spec = DIMENSION_GROUPS[group_by]
    date_from = fields.Date.to_date(date_from)
    date_to = fields.Date.to_date(date_to)
    if not date_from or not date_to or date_from > date_to:
        raise UserError(
            "A branch / operating-unit P&L needs a valid date window: the start must not be "
            "after the end (FR-FIN-031)."
        )
    if isinstance(company, int):
        company = env["res.company"].browse(company)
    company = company or env.company
    if not company:
        raise UserError("A P&L slice belongs to a company (FR-FIN-031).")

    # The SAME posted rows compute_pnl() reads: company + window + income/expense.
    lines = (
        env["account.move.line"]
        .sudo()
        .search(
            [
                ("company_id", "=", company.id),
                ("parent_state", "=", "posted"),
                ("account_id.internal_group", "in", PL_GROUPS),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ],
            order="id",
        )
    )
    dimension_of = {}
    if lines:
        dimensions = (
            env["fix.journal.dimension"]
            .sudo()
            .search([("move_line_id", "in", lines.ids)], order="id")
        )
        for dimension in dimensions:
            # One dimension row per line is the posting API's contract; if a
            # duplicate ever appears, the first (lowest id) is the annotation
            # the ledger entry was posted with.
            dimension_of.setdefault(dimension.move_line_id.id, _dimension_key(dimension, spec))

    buckets: dict[int | str | None, dict] = {}
    for line in lines:
        key = dimension_of.get(line.id)
        bucket = buckets.setdefault(key, _empty_bucket())
        amount = _money(line.balance)
        if line.account_id.internal_group == "income":
            bucket["revenue"] += -amount
        else:
            bucket["expense"] += amount
        bucket["line_count"] += 1
        account = bucket["accounts"].setdefault(
            line.account_id.id,
            {
                "account_code": line.account_id.with_company(company).code or "",
                "account_name": line.account_id.name or "",
                "internal_group": line.account_id.internal_group or "",
                "balance": Decimal("0.00"),
            },
        )
        account["balance"] += amount

    rows = []
    totals = _empty_bucket()
    unallocated_bucket = buckets.pop(None, _empty_bucket())
    for key, bucket in buckets.items():
        label, identification = _label(env, spec, key)
        row_totals = _bucket_totals(bucket)
        rows.append(
            {
                "key": str(key),
                "label": label,
                "unallocated": False,
                **identification,
                **row_totals,
                "accounts": _account_rows(bucket),
            }
        )
        totals["revenue"] += bucket["revenue"]
        totals["expense"] += bucket["expense"]
        totals["line_count"] += bucket["line_count"]
        totals["accounts"].update(bucket["accounts"])
    rows.sort(key=lambda row: (row["label"], row["key"]))

    unallocated = {
        "key": UNALLOCATED_KEY,
        "label": "Unallocated (no %s dimension)" % spec["label"].lower(),
        "unallocated": True,
        **_bucket_totals(unallocated_bucket),
        "accounts": _account_rows(unallocated_bucket),
    }
    # The bucket is always present in the pack, even at zero: a reader must be
    # able to see that nothing fell outside the dimension (BR-FIN-008).
    rows.append(unallocated)
    totals["revenue"] += unallocated_bucket["revenue"]
    totals["expense"] += unallocated_bucket["expense"]
    totals["line_count"] += unallocated_bucket["line_count"]
    totals["accounts"].update(unallocated_bucket["accounts"])

    company_pnl = compute_pnl(env, company, date_from, date_to)
    revenue = _plain(totals["revenue"])
    expense = _plain(totals["expense"])
    net_profit = _plain(totals["revenue"] - totals["expense"])
    ties = net_profit == company_pnl["net_profit"]

    return {
        "report": "pnl_by_dimension",
        "group_by": group_by,
        "group_label": spec["label"],
        "company": company.name,
        "company_id": company.id,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "currency": company.currency_id.name,
        "basis": "posted account.move.line, income/expense by account type, sliced by "
        "%s; lines lacking the dimension are reported in the unallocated bucket "
        "(FR-FIN-031 / BR-FIN-008)" % spec["label"].lower(),
        "rows": rows,
        "totals": {
            "revenue": revenue,
            "expense": expense,
            "net_profit": net_profit,
            "line_count": totals["line_count"],
            "account_count": len(totals["accounts"]),
            "company_pnl_net_profit": company_pnl["net_profit"],
            "ties_to_company_pnl": ties,
        },
        "unallocated": unallocated,
        "ties_to_company_pnl": ties,
    }
