"""bank_feed_parser — INT-006 Bank Statement Import Feed Parser (MT940 & CSV).

Parses electronic bank feeds for Bangladeshi commercial banks (City Bank,
Eastern Bank Limited, BRAC Bank, Standard Chartered Bangladesh):
1. SWIFT MT940 standard statement format.
2. Structured commercial bank CSV feeds.
3. Enforces statement line deduplication via content hashing (SHA256).
4. Detects sequence gaps in statement files (IN-004 §9).
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from decimal import Decimal

try:
    from .reconciliation import StatementLine
except ImportError:
    from reconciliation import StatementLine


@dataclass
class ParsedStatement:
    statement_id: str
    sequence_number: str
    opening_balance: Decimal | None
    closing_balance: Decimal | None
    lines: list[StatementLine] = field(default_factory=list)
    file_hash: str = ""
    line_hashes: list[str] = field(default_factory=list)
    duplicate_lines_skipped: int = 0
    warnings: list[str] = field(default_factory=list)


def _compute_line_hash(dt: date, amount: Decimal, ref: str, narration: str) -> str:
    raw = f"{dt.isoformat()}|{amount:.2f}|{ref.strip()}|{narration.strip()}".encode()
    return hashlib.sha256(raw).hexdigest()


def _parse_swift_date(yy_mm_dd: str) -> date:
    # 261015 -> 2026-10-15
    year = 2000 + int(yy_mm_dd[0:2])
    month = int(yy_mm_dd[2:4])
    day = int(yy_mm_dd[4:6])
    return date(year, month, day)


def _parse_swift_amount(amt_str: str) -> Decimal:
    return Decimal(amt_str.replace(",", "."))


_BOM = "\ufeff"  # UTF-8 byte-order mark (Excel / bank-portal exports)
# A SWIFT tag line: ":20:", ":28C:", ":60F:", ":61:", ":86:", ...
_TAG_RE = re.compile(r"^:(\d{2}[A-Z]?):")
_BALANCE_RE = re.compile(r":(?:60F|60M|62F|62M):([CD])(\d{6})([A-Z]{3})([0-9,.]+)")
# e.g., :61:2610151015CR1150,00NTRFNONREF//AR/101
# Fields: ValueDate(6) [EntryDate(4)] DebitCredit(1..2) [FundsCode(1)] Amount
#         TxType(4: N/F + 3 letters, or S + 3 digits e.g. S103)
#         Ref(16 - may itself contain "/", e.g. AR/555) [//ExtRef]
_ENTRY_RE = re.compile(
    r":61:(\d{6})(?:\d{4})?([CD]|RC|RD)([A-Z]?)([0-9,.]+)([A-Z][A-Z0-9]{3})?"
    r"((?:(?!//).)+)?(?://(.*))?"
)
# SWIFT field 61 subfield 3: C = credit, D = debit, RC = reversal of credit
# (a DEBIT entry), RD = reversal of debit (a CREDIT entry).
_DEBIT_MARKS = ("D", "RC")


def _parse_balance(line: str, warnings: list[str]) -> Decimal | None:
    match = _BALANCE_RE.match(line)
    try:
        if match is None:
            raise ValueError("no balance field match")
        sign, _dt_str, _curr, amt_str = match.groups()
        amt = _parse_swift_amount(amt_str)
    except (ValueError, ArithmeticError):
        warnings.append(f"Failed to parse MT940 balance line: {line}")
        return None
    return amt if sign == "C" else -amt


def _parse_entry(line: str, warnings: list[str]) -> StatementLine | None:
    match = _ENTRY_RE.match(line)
    try:
        if match is None:
            raise ValueError("no field-61 match")
        val_dt_str, cd_sign, _funds, amt_str, _tx_type, ref_part, ext_ref = match.groups()
        dt = _parse_swift_date(val_dt_str)
        amt = _parse_swift_amount(amt_str)
    except (ValueError, ArithmeticError):
        warnings.append(f"Failed to parse MT940 line: {line}")
        return None
    if cd_sign in _DEBIT_MARKS:
        amt = -amt
    ref = (ext_ref or ref_part or "").strip()
    return StatementLine(date=dt, amount=amt, reference=ref, narration="")


def _check_sequence(seq_no: str, expected: int | None, warnings: list[str]) -> None:
    """IN-004 §9 sequence audit: the statement number (the part before any
    "/page" suffix) must be the one the caller expects next."""
    if expected is None:
        return
    try:
        actual = int(seq_no.split("/")[0])
    except ValueError:
        warnings.append(f"Sequence check skipped: unparseable sequence {seq_no!r}")
        return
    if actual != expected:
        warnings.append(f"Sequence mismatch: expected {expected}, got {seq_no}")


def parse_mt940(
    content: str,
    seen_hashes: set[str] | None = None,
    expected_sequence: int | None = None,
) -> ParsedStatement:
    """Parse SWIFT MT940 text into StatementLine records with deduplication and sequence audit."""
    content = content.lstrip(_BOM)
    seen = set(seen_hashes) if seen_hashes else set()
    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    statement_id = "UNKNOWN"
    sequence_no = "1"
    opening_bal: Decimal | None = None
    closing_bal: Decimal | None = None
    lines: list[StatementLine] = []
    line_hashes: list[str] = []
    skipped = 0
    warnings: list[str] = []

    # A :61: entry stays PENDING until something ends it (the next :61:, a
    # :62F:/:62M: closing balance, a new :20: statement, or end of input), so
    # its :86: narration - including continuation lines - is complete before
    # the line is hashed and committed. :86: is optional in MT940.
    pending: StatementLine | None = None
    in_narration = False
    last_tag = ""

    def commit() -> None:
        nonlocal pending, skipped
        if pending is None:
            return
        l_hash = _compute_line_hash(
            pending.date, pending.amount, pending.reference, pending.narration
        )
        if l_hash in seen:
            skipped += 1
        else:
            seen.add(l_hash)
            line_hashes.append(l_hash)
            lines.append(pending)
        pending = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        tag_match = _TAG_RE.match(line)
        if tag_match is None:
            # Continuation of a multi-line :86: narration; anything else
            # (block wrappers such as "-}") belongs to no entry.
            if in_narration and pending is not None:
                pending = replace(pending, narration=f"{pending.narration} {line}".strip())
            continue

        tag = tag_match.group(1)
        in_narration = False
        if tag == "20":
            commit()
            statement_id = line[4:].strip()
        elif tag in ("28C", "28"):
            sequence_no = line[len(tag) + 2 :].strip()
        elif tag in ("60F", "60M"):
            balance = _parse_balance(line, warnings)
            if balance is not None:
                opening_bal = balance
        elif tag == "61":
            commit()
            pending = _parse_entry(line, warnings)
        elif tag == "86":
            if pending is not None and last_tag == "61":
                pending = replace(pending, narration=line[4:].strip())
                in_narration = True
        elif tag in ("62F", "62M"):
            commit()
            balance = _parse_balance(line, warnings)
            if balance is not None:
                closing_bal = balance
        # Other tags (:25:, :64:, :65:, ...) carry nothing this import needs.
        last_tag = tag

    commit()
    _check_sequence(sequence_no, expected_sequence, warnings)

    return ParsedStatement(
        statement_id=statement_id,
        sequence_number=sequence_no,
        opening_balance=opening_bal,
        closing_balance=closing_bal,
        lines=lines,
        file_hash=file_hash,
        line_hashes=line_hashes,
        duplicate_lines_skipped=skipped,
        warnings=warnings,
    )


def _detect_delimiter(content: str) -> str:
    """Pick the separator from the HEADER line only: amounts in a tab- or
    semicolon-separated feed may legitimately carry comma thousands
    separators, so data rows must not vote. Ties prefer the comma."""
    header = content.split("\n", 1)[0]
    return max((",", "\t", ";"), key=header.count)


def _cell(row: dict[str | None, str | None], field_map: dict[str, str], key: str) -> str:
    """A mapped cell's stripped text; "" when the column is unmapped or the
    row is short (csv.DictReader fills missing trailing cells with None)."""
    column = field_map.get(key)
    if column is None:
        return ""
    return (row.get(column) or "").strip()


def _parse_csv_amount(raw: str) -> Decimal:
    cleaned = raw.replace(",", "").replace("$", "").replace("৳", "").strip()
    return Decimal(cleaned) if cleaned else Decimal("0.00")


def parse_csv(
    content: str,
    seen_hashes: set[str] | None = None,
    expected_sequence: int | None = None,
) -> ParsedStatement:
    """Parse commercial bank CSV feed with auto-column mapping, deduplication, and sequence verification."""
    content = content.lstrip(_BOM)
    seen = set(seen_hashes) if seen_hashes else set()
    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    lines: list[StatementLine] = []
    line_hashes: list[str] = []
    skipped = 0
    warnings: list[str] = []

    reader = csv.DictReader(io.StringIO(content), delimiter=_detect_delimiter(content))

    if not reader.fieldnames:
        return ParsedStatement("EMPTY", "0", None, None, [], file_hash, [], 0, ["Empty CSV"])

    field_map: dict[str, str] = {}
    for col in reader.fieldnames:
        norm = col.strip().lower().replace(" ", "_").replace(".", "")
        if "date" in norm and "value" not in norm:
            field_map["date"] = col
        elif norm in ("reference", "ref", "ref_no", "cheque_no", "trn_id", "trx_id"):
            field_map["ref"] = col
        elif norm in ("description", "narration", "particulars", "remarks"):
            field_map["narration"] = col
        elif norm in ("credit", "deposit", "inflow", "cr"):
            field_map["credit"] = col
        elif norm in ("debit", "withdrawal", "outflow", "dr"):
            field_map["debit"] = col
        elif norm in ("amount", "net_amount"):
            field_map["amount"] = col
        elif norm in ("sequence", "seq", "seq_no", "statement_no"):
            field_map["seq"] = col
    if "date" not in field_map:
        warnings.append("No date column in CSV header - no statement lines imported")

    seq_no = "1"
    for row_idx, row in enumerate(reader, start=1):
        # 1. Parse Date
        dt_raw = _cell(row, field_map, "date")
        if not dt_raw:
            continue

        try:
            # Handle YYYY-MM-DD or DD/MM/YYYY or DD-MM-YYYY
            if "-" in dt_raw:
                parts = dt_raw.split("-")
                if len(parts[0]) == 4:
                    dt = date(int(parts[0]), int(parts[1]), int(parts[2]))
                else:
                    dt = date(int(parts[2]), int(parts[1]), int(parts[0]))
            elif "/" in dt_raw:
                parts = dt_raw.split("/")
                if len(parts[0]) == 4:
                    dt = date(int(parts[0]), int(parts[1]), int(parts[2]))
                else:
                    dt = date(int(parts[2]), int(parts[1]), int(parts[0]))
            else:
                dt = datetime.strptime(dt_raw, "%Y%m%d").date()
        except Exception:
            warnings.append(f"Row {row_idx}: invalid date {dt_raw!r}")
            continue

        # 2. Parse Amount (a signed "amount" cell wins over credit/debit)
        amount_raw = _cell(row, field_map, "amount")
        credit_raw = _cell(row, field_map, "credit")
        debit_raw = _cell(row, field_map, "debit")
        try:
            if amount_raw:
                amt = _parse_csv_amount(amount_raw)
            else:
                amt = _parse_csv_amount(credit_raw) - _parse_csv_amount(debit_raw)
        except ArithmeticError:
            warnings.append(
                f"Row {row_idx}: invalid amount (amount={amount_raw!r}, "
                f"credit={credit_raw!r}, debit={debit_raw!r})"
            )
            continue

        ref = _cell(row, field_map, "ref")
        narration = _cell(row, field_map, "narration")
        seq_cell = _cell(row, field_map, "seq")
        if seq_cell:
            seq_no = seq_cell

        l_hash = _compute_line_hash(dt, amt, ref, narration)
        if l_hash in seen:
            skipped += 1
        else:
            seen.add(l_hash)
            line_hashes.append(l_hash)
            lines.append(StatementLine(date=dt, amount=amt, reference=ref, narration=narration))

    _check_sequence(seq_no, expected_sequence, warnings)

    return ParsedStatement(
        statement_id="CSV-IMPORT",
        sequence_number=seq_no,
        opening_balance=None,
        closing_balance=None,
        lines=lines,
        file_hash=file_hash,
        line_hashes=line_hashes,
        duplicate_lines_skipped=skipped,
        warnings=warnings,
    )


def parse_bank_feed(
    content: str,
    format_type: str = "auto",
    seen_hashes: set[str] | None = None,
    expected_sequence: int | None = None,
) -> ParsedStatement:
    """Entry point for bank feed parsing with auto-detection."""
    content_stripped = content.lstrip(_BOM).strip()
    if format_type == "mt940" or (
        format_type == "auto"
        and (content_stripped.startswith(":20:") or ":61:" in content_stripped)
    ):
        return parse_mt940(
            content_stripped, seen_hashes=seen_hashes, expected_sequence=expected_sequence
        )
    return parse_csv(content_stripped, seen_hashes=seen_hashes, expected_sequence=expected_sequence)
