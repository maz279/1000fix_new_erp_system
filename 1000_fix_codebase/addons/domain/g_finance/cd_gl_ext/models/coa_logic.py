# cd_gl_ext — Pure Bangladesh Chart of Accounts (CoA) Logic & Validation Rules (MD-035).
# Pure calculation & validation module: zero Odoo ORM imports, 100% testable (DoD-03).
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

ACCOUNT_CODE_REGEX = re.compile(r"^[1-5]-\d{2}-\d{2}-\d{3}$")
VALID_ACCOUNT_TYPES = {"asset", "liability", "equity", "income", "expense"}
VALID_SUBTYPES = {
    "current_asset", "fixed_asset", "receivable", "payable", "bank", "cash",
    "stock", "tax", "revenue", "cogs", "opex", "payroll", "liability", "equity"
}
VALID_CONTROL_SUBLEDGERS = {"receivable", "payable", "stock", "fixed_asset", "tax"}
VALID_DIMENSIONS = {"branch", "cost_centre", "business_line"}


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
    control_subledger: Optional[str]
    requires_dimension: Set[str]
    statutory_group: str
    active: bool = True
    balance: Decimal = Decimal("0.00")
    has_postings: bool = False
    last_posting_days_ago: int = 0


def parse_coa_csv(csv_content: str) -> List[AccountRecord]:
    """Parse CSV text into a list of AccountRecord instances."""
    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    records: List[AccountRecord] = []
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
        )
        records.append(rec)
    return records


def validate_account_structure(record: AccountRecord) -> None:
    """Validate format and basic constraints for an individual account."""
    if not ACCOUNT_CODE_REGEX.match(record.account_code):
        raise CoaValidationError(
            record.account_code,
            f"Code '{record.account_code}' must follow format T-GG-SS-NNN",
            "CODE-FMT"
        )
    if record.account_type not in VALID_ACCOUNT_TYPES:
        raise CoaValidationError(
            record.account_code,
            f"Invalid account type '{record.account_type}'",
            "TYPE-FMT"
        )
    if not record.statutory_group:
        raise CoaValidationError(
            record.account_code,
            "statutory_group is mandatory (COA-05)",
            "ERR-COA-005"
        )
    if record.is_control_account and not record.control_subledger:
        raise CoaValidationError(
            record.account_code,
            "Control account must specify control_subledger",
            "CTRL-REQ"
        )
    if record.control_subledger and record.control_subledger not in VALID_CONTROL_SUBLEDGERS:
        raise CoaValidationError(
            record.account_code,
            f"Invalid control subledger '{record.control_subledger}'",
            "SUBLEDGER-FMT"
        )
    invalid_dims = record.requires_dimension - VALID_DIMENSIONS
    if invalid_dims:
        raise CoaValidationError(
            record.account_code,
            f"Invalid dimensions: {invalid_dims}",
            "DIM-FMT"
        )


def validate_coa_rules(accounts: List[AccountRecord]) -> Dict[str, Any]:
    """Validate the complete set of accounts against MD-035 rules COA-01 to COA-07."""
    code_map = {acc.account_code: acc for acc in accounts}
    warnings: List[str] = []

    # Identify parent codes by hierarchical prefix
    # Format: T-GG-SS-NNN.
    # Level 1: T-00-00-000 (Group)
    # Level 2: T-GG-00-000 (Category)
    # Level 3: T-GG-SS-000 (Subgroup)
    # Level 4: T-GG-SS-NNN (Leaf, NNN > 000)
    for acc in accounts:
        validate_account_structure(acc)
        parts = acc.account_code.split("-")
        t, gg, ss, nnn = parts[0], parts[1], parts[2], parts[3]
        is_leaf = (nnn != "000")

        # COA-01: Only leaf accounts may be postable
        if acc.is_postable and not is_leaf:
            raise CoaValidationError(
                acc.account_code,
                "Non-leaf summary account cannot be postable (COA-01)",
                "ERR-COA-001"
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
    dimensions: Dict[str, Any],
    is_direct_manual_post: bool = False,
) -> None:
    """Validate a posting against COA-01, COA-02, COA-03, COA-06."""
    if not account.is_postable:
        raise CoaValidationError(
            account.account_code,
            "Cannot post to non-postable summary account",
            "ERR-COA-001"
        )
    # COA-02: Control account cannot be posted to directly (only via subledger)
    if account.is_control_account and is_direct_manual_post:
        raise CoaValidationError(
            account.account_code,
            f"Control account {account.account_code} cannot receive direct manual journal entries (COA-02)",
            "ERR-COA-002"
        )
    # COA-03: Every posting must carry dimensions specified in requires_dimension
    for req_dim in account.requires_dimension:
        if req_dim not in dimensions or not dimensions[req_dim]:
            raise CoaValidationError(
                account.account_code,
                f"Posting requires dimension '{req_dim}' which is missing or empty (COA-03)",
                "ERR-COA-003"
            )


def validate_archive_attempt(account: AccountRecord) -> None:
    """Validate archiving an account under COA-04."""
    if account.balance != Decimal("0.00"):
        raise CoaValidationError(
            account.account_code,
            f"Cannot archive account {account.account_code} with non-zero balance {account.balance} BDT (COA-04)",
            "ERR-COA-004"
        )


def validate_type_change(account: AccountRecord, new_type: str) -> None:
    """Validate modifying account type under COA-06."""
    if account.has_postings and account.account_type != new_type:
        raise CoaValidationError(
            account.account_code,
            f"Cannot change account type from {account.account_type} to {new_type} on an account with existing postings (COA-06)",
            "ERR-COA-006"
        )


def reconcile_trial_balance(
    account_balances: Dict[str, Decimal],
    accounts: List[AccountRecord]
) -> Dict[str, Any]:
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

    is_reconciled = (discrepancy.copy_abs() < Decimal("0.001"))

    return {
        "reconciled": is_reconciled,
        "total_assets": float(totals["asset"]),
        "total_liabilities": float(totals["liability"]),
        "total_equity": float(totals["equity"]),
        "total_income": float(totals["income"]),
        "total_expense": float(totals["expense"]),
        "discrepancy": float(discrepancy),
    }
