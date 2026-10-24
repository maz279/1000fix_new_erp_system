# cd_gl_ext — Pure Bangladesh Chart of Accounts (CoA) Logic & Validation Rules (MD-035).
# Pure calculation & validation module: zero Odoo ORM imports, 100% testable (DoD-03).
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

ACCOUNT_CODE_REGEX = re.compile(r"^[1-5]-\d{2}-\d{2}-\d{3}$")
VALID_ACCOUNT_TYPES = {"asset", "liability", "equity", "income", "expense"}
VALID_SUBTYPES = {
    "current_asset",
    "fixed_asset",
    "receivable",
    "payable",
    "bank",
    "cash",
    "stock",
    "tax",
    "revenue",
    "cogs",
    "opex",
    "payroll",
    "liability",
    "equity",
}
VALID_CONTROL_SUBLEDGERS = {"receivable", "payable", "stock", "fixed_asset", "tax"}
VALID_DIMENSIONS = {"branch", "cost_centre", "business_line"}

# MD-035 §3: the T block of T-GG-SS-NNN is the account type.
TYPE_BY_DIGIT = {
    "1": "asset",
    "2": "liability",
    "3": "equity",
    "4": "income",
    "5": "expense",
}


class CoaValidationError(Exception):
    """Raised when a Chart of Accounts validation rule is violated."""

    def __init__(self, code: str, message: str, rule: str):
        super().__init__(f"[{rule}] {code}: {message}")
        self.code = code
        self.message = message
        self.rule = rule


@dataclass
class AccountRecord:
    account_code: str
    entity_code: str
    account_name: str
    account_type: str
    account_subtype: str
    is_postable: bool
    is_control_account: bool
    control_subledger: str | None
    requires_dimension: set[str]
    statutory_group: str
    active: bool = True
    balance: Decimal = Decimal("0.00")
    has_postings: bool = False
    last_posting_days_ago: int = 0
    # MD-035 §2 optional self-reference; when absent the parent is derived
    # from the code hierarchy (nearest existing ancestor).
    parent_account_code: str | None = None


def parse_coa_csv(csv_content: str) -> list[AccountRecord]:
    """Parse CSV text into a list of AccountRecord instances."""
    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    records: list[AccountRecord] = []
    for row in reader:
        dims = set()
        dim_str = row.get("requires_dimension", "").strip()
        if dim_str:
            dims = {d.strip() for d in dim_str.split(";") if d.strip()}

        is_postable = row.get("is_postable", "").strip().upper() in ("TRUE", "1", "YES")
        is_control = row.get("is_control_account", "").strip().upper() in ("TRUE", "1", "YES")
        active = row.get("active", "TRUE").strip().upper() in ("TRUE", "1", "YES")
        control_subledger = row.get("control_subledger", "").strip() or None

        rec = AccountRecord(
            account_code=row["account_code"].strip(),
            entity_code=row.get("entity_code", "EN-01").strip(),
            account_name=row["account_name"].strip(),
            account_type=row["account_type"].strip().lower(),
            account_subtype=row.get("account_subtype", "").strip().lower(),
            is_postable=is_postable,
            is_control_account=is_control,
            control_subledger=control_subledger,
            requires_dimension=dims,
            statutory_group=row.get("statutory_group", "").strip(),
            active=active,
            parent_account_code=(row.get("parent_account_code") or "").strip() or None,
        )
        records.append(rec)
    return records


def account_level(account_code: str) -> int:
    """Hierarchy level of a well-formed T-GG-SS-NNN code.

    Level 1: T-00-00-000 (group) · Level 2: T-GG-00-000 (category) ·
    Level 3: T-GG-SS-000 (subgroup) · Level 4: T-GG-SS-NNN, NNN > 000 (leaf).
    """
    _t, gg, ss, nnn = account_code.split("-")
    if nnn != "000":
        return 4
    if ss != "00":
        return 3
    if gg != "00":
        return 2
    return 1


def ancestor_codes(account_code: str) -> list[str]:
    """The summary codes above an account, nearest first (root last)."""
    t, gg, ss, _nnn = account_code.split("-")
    candidates = [f"{t}-{gg}-{ss}-000", f"{t}-{gg}-00-000", f"{t}-00-00-000"]
    return candidates[4 - account_level(account_code) :]


def validate_code_hierarchy(record: AccountRecord) -> None:
    """MD-035 §3 T/GG/SS rules for one (format-valid) account code.

    The T block must agree with account_type, and a zero block may only be
    followed by zero blocks: a subgroup cannot sit under group 00 and a
    sequence cannot sit under subgroup 00 (T-00-SS-*, T-GG-00-NNN are
    malformed — they have no place in the four-level tree)."""
    t, gg, ss, nnn = record.account_code.split("-")
    expected_type = TYPE_BY_DIGIT[t]
    if record.account_type != expected_type:
        raise CoaValidationError(
            record.account_code,
            f"Type block '{t}' denotes '{expected_type}' but the account type is "
            f"'{record.account_type}'",
            "HIER-TYPE",
        )
    if gg == "00" and (ss != "00" or nnn != "000"):
        raise CoaValidationError(
            record.account_code,
            "A subgroup or sequence cannot sit under group block 00",
            "HIER-LEVEL",
        )
    if ss == "00" and nnn != "000":
        raise CoaValidationError(
            record.account_code,
            "A sequence cannot sit under subgroup block 00",
            "HIER-LEVEL",
        )


def validate_leaf_postable(record: AccountRecord) -> None:
    """COA-01: only level-4 leaf accounts (NNN > 000) may be postable."""
    if record.is_postable and account_level(record.account_code) != 4:
        raise CoaValidationError(
            record.account_code,
            "Non-leaf summary account cannot be postable (COA-01)",
            "ERR-COA-001",
        )


def validate_account_structure(record: AccountRecord) -> None:
    """Validate format and basic constraints for an individual account."""
    if not ACCOUNT_CODE_REGEX.match(record.account_code):
        raise CoaValidationError(
            record.account_code,
            f"Code '{record.account_code}' must follow format T-GG-SS-NNN",
            "CODE-FMT",
        )
    if record.account_type not in VALID_ACCOUNT_TYPES:
        raise CoaValidationError(
            record.account_code, f"Invalid account type '{record.account_type}'", "TYPE-FMT"
        )
    if not record.statutory_group:
        raise CoaValidationError(
            record.account_code, "statutory_group is mandatory (COA-05)", "ERR-COA-005"
        )
    if record.is_control_account and not record.control_subledger:
        raise CoaValidationError(
            record.account_code, "Control account must specify control_subledger", "CTRL-REQ"
        )
    if record.control_subledger and record.control_subledger not in VALID_CONTROL_SUBLEDGERS:
        raise CoaValidationError(
            record.account_code,
            f"Invalid control subledger '{record.control_subledger}'",
            "SUBLEDGER-FMT",
        )
    invalid_dims = record.requires_dimension - VALID_DIMENSIONS
    if invalid_dims:
        raise CoaValidationError(
            record.account_code, f"Invalid dimensions: {invalid_dims}", "DIM-FMT"
        )
    validate_code_hierarchy(record)


def validate_coa_rules(accounts: list[AccountRecord]) -> dict[str, Any]:
    """Validate the complete set of accounts against MD-035 rules COA-01 to COA-07
    and the §3 four-level hierarchy.

    Format: T-GG-SS-NNN.
      Level 1: T-00-00-000 (Group)
      Level 2: T-GG-00-000 (Category)
      Level 3: T-GG-SS-000 (Subgroup)
      Level 4: T-GG-SS-NNN (Leaf, NNN > 000)

    Parent-account existence: every account below level 1 must roll up to
    an EXISTING summary account of the same entity. The parent is the
    nearest existing ancestor (intermediate levels may be omitted, as in the
    statutory MD-035 file), so a chart whose group root T-00-00-000 is
    missing has orphans. A declared parent_account_code must exist and must
    be exactly that nearest existing ancestor. The natural key
    entity_code + account_code is unique (§3: codes are never reused).
    """
    warnings: list[str] = []
    code_map: dict[tuple[str, str], AccountRecord] = {}

    for acc in accounts:
        validate_account_structure(acc)
        key = (acc.entity_code, acc.account_code)
        if key in code_map:
            raise CoaValidationError(
                acc.account_code,
                f"Duplicate account code within entity {acc.entity_code} (MD-035 §3)",
                "DUP-CODE",
            )
        code_map[key] = acc

    for acc in accounts:
        # COA-01: Only leaf accounts may be postable
        validate_leaf_postable(acc)

        parent_code = next(
            (
                code
                for code in ancestor_codes(acc.account_code)
                if (acc.entity_code, code) in code_map
            ),
            None,
        )
        if acc.parent_account_code:
            if (acc.entity_code, acc.parent_account_code) not in code_map:
                raise CoaValidationError(
                    acc.account_code,
                    f"Parent account {acc.parent_account_code} does not exist in the chart",
                    "PARENT-MISSING",
                )
            if acc.parent_account_code != parent_code:
                raise CoaValidationError(
                    acc.account_code,
                    f"Declared parent {acc.parent_account_code} contradicts the code "
                    f"hierarchy (expected {parent_code or 'none: level-1 group'})",
                    "PARENT-MISMATCH",
                )
        elif parent_code is None and account_level(acc.account_code) > 1:
            raise CoaValidationError(
                acc.account_code,
                "No parent summary account exists for this account; its group "
                f"{ancestor_codes(acc.account_code)[-1]} is missing from the chart",
                "PARENT-MISSING",
            )

        # COA-07: Unused account for 2 years (>= 730 days) issues warning
        if acc.is_postable and acc.has_postings and acc.last_posting_days_ago >= 730:
            warnings.append(
                f"[WRN-COA-007] Account {acc.account_code} has had no postings for {acc.last_posting_days_ago} days."
            )

    return {
        "valid": True,
        "account_count": len(accounts),
        "postable_count": sum(1 for a in accounts if a.is_postable),
        "control_count": sum(1 for a in accounts if a.is_control_account),
        "warnings": warnings,
    }


def validate_posting_attempt(
    account: AccountRecord,
    dimensions: dict[str, Any],
    is_direct_manual_post: bool = False,
) -> None:
    """Validate a posting against COA-01, COA-02, COA-03, COA-06."""
    if not account.is_postable:
        raise CoaValidationError(
            account.account_code, "Cannot post to non-postable summary account", "ERR-COA-001"
        )
    # COA-02: Control account cannot be posted to directly (only via subledger)
    if account.is_control_account and is_direct_manual_post:
        raise CoaValidationError(
            account.account_code,
            f"Control account {account.account_code} cannot receive direct manual journal entries (COA-02)",
            "ERR-COA-002",
        )
    # COA-03: Every posting must carry dimensions specified in requires_dimension
    for req_dim in account.requires_dimension:
        if req_dim not in dimensions or not dimensions[req_dim]:
            raise CoaValidationError(
                account.account_code,
                f"Posting requires dimension '{req_dim}' which is missing or empty (COA-03)",
                "ERR-COA-003",
            )


def validate_archive_attempt(account: AccountRecord) -> None:
    """Validate archiving an account under COA-04."""
    if account.balance != Decimal("0.00"):
        raise CoaValidationError(
            account.account_code,
            f"Cannot archive account {account.account_code} with non-zero balance {account.balance} BDT (COA-04)",
            "ERR-COA-004",
        )


def validate_type_change(account: AccountRecord, new_type: str) -> None:
    """Validate modifying account type under COA-06."""
    if account.has_postings and account.account_type != new_type:
        raise CoaValidationError(
            account.account_code,
            f"Cannot change account type from {account.account_type} to {new_type} on an account with existing postings (COA-06)",
            "ERR-COA-006",
        )


def reconcile_trial_balance(
    account_balances: dict[str, Decimal], accounts: list[AccountRecord]
) -> dict[str, Any]:
    """Verify accounting equation: Total Assets = Total Liabilities + Total Equity.
    Or sum of all signed balances (Assets positive, Liabilities/Equity negative) == 0.
    """
    code_map = {a.account_code: a for a in accounts}
    totals = {
        "asset": Decimal("0.00"),
        "liability": Decimal("0.00"),
        "equity": Decimal("0.00"),
        "income": Decimal("0.00"),
        "expense": Decimal("0.00"),
    }

    for code, balance in account_balances.items():
        acc = code_map.get(code)
        if acc:
            totals[acc.account_type] += balance

    # Net income = income - expense
    net_income = totals["income"] - totals["expense"]
    # Total equity including period profit = equity + net_income
    effective_equity = totals["equity"] + net_income
    discrepancy = totals["asset"] - (totals["liability"] + effective_equity)

    is_reconciled = discrepancy.copy_abs() < Decimal("0.001")

    return {
        "reconciled": is_reconciled,
        "total_assets": float(totals["asset"]),
        "total_liabilities": float(totals["liability"]),
        "total_equity": float(totals["equity"]),
        "total_income": float(totals["income"]),
        "total_expense": float(totals["expense"]),
        "discrepancy": float(discrepancy),
    }
