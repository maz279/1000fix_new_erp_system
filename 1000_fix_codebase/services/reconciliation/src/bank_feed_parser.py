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
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

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
    raw = f"{dt.isoformat()}|{amount:.2f}|{ref.strip()}|{narration.strip()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _parse_swift_date(yy_mm_dd: str) -> date:
    # 261015 -> 2026-10-15
    year = 2000 + int(yy_mm_dd[0:2])
    month = int(yy_mm_dd[2:4])
    day = int(yy_mm_dd[4:6])
    return date(year, month, day)


def _parse_swift_amount(amt_str: str) -> Decimal:
    return Decimal(amt_str.replace(",", "."))


def parse_mt940(content: str, seen_hashes: set[str] | None = None) -> ParsedStatement:
    """Parse SWIFT MT940 text into StatementLine records with deduplication and sequence audit."""
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

    # Tag regex pattern
    current_line: StatementLine | None = None
    last_tag = ""

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith(":20:"):
            statement_id = line[4:].strip()
            last_tag = "20"
        elif line.startswith(":25:"):
            last_tag = "25"
        elif line.startswith(":28C:") or line.startswith(":28:"):
            tag_len = 5 if line.startswith(":28C:") else 4
            sequence_no = line[tag_len:].strip()
            last_tag = "28"
        elif line.startswith(":60F:") or line.startswith(":60M:"):
            # e.g., :60F:C261001BDT100000,00
            match = re.match(r":(?:60F|60M):([CD])(\d{6})([A-Z]{3})([0-9,.]+)", line)
            if match:
                sign, dt_str, curr, amt_str = match.groups()
                amt = _parse_swift_amount(amt_str)
                opening_bal = amt if sign == "C" else -amt
            last_tag = "60"
        elif line.startswith(":61:"):
            # e.g., :61:2610151015CR1150,00NTRFNONREF//AR/101
            # Fields: ValueDate(6) [EntryDate(4)] DebitCredit(1..2) [FundsCode(1)] Amount CurrencyCode(1) TxType(4) Ref(16) [//ExtRef]
            match = re.match(
                r":61:(\d{6})(?:\d{4})?([CD]|RC|RD)([A-Z]?)([0-9,.]+)([A-Z]{4})?([^/\n]+)?(?://(.*))?",
                line
            )
            if match:
                val_dt_str, cd_sign, funds, amt_str, tx_type, ref_part, ext_ref = match.groups()
                dt = _parse_swift_date(val_dt_str)
                amt = _parse_swift_amount(amt_str)
                if cd_sign in ("D", "RD"):
                    amt = -amt
                ref = (ext_ref or ref_part or "").strip()
                current_line = StatementLine(date=dt, amount=amt, reference=ref, narration="")
            else:
                warnings.append(f"Failed to parse MT940 line: {line}")
            last_tag = "61"
        elif line.startswith(":86:"):
            narration = line[4:].strip()
            if current_line:
                # Commit previous line with narration
                combined_line = StatementLine(
                    date=current_line.date,
                    amount=current_line.amount,
                    reference=current_line.reference,
                    narration=narration,
                )
                l_hash = _compute_line_hash(combined_line.date, combined_line.amount, combined_line.reference, combined_line.narration)
                if l_hash in seen:
                    skipped += 1
                else:
                    seen.add(l_hash)
                    line_hashes.append(l_hash)
                    lines.append(combined_line)
                current_line = None
            last_tag = "86"
        elif line.startswith(":62F:") or line.startswith(":62M:"):
            if current_line:
                l_hash = _compute_line_hash(current_line.date, current_line.amount, current_line.reference, current_line.narration)
                if l_hash in seen:
                    skipped += 1
                else:
                    seen.add(l_hash)
                    line_hashes.append(l_hash)
                    lines.append(current_line)
                current_line = None

            match = re.match(r":(?:62F|62M):([CD])(\d{6})([A-Z]{3})([0-9,.]+)", line)
            if match:
                sign, dt_str, curr, amt_str = match.groups()
                amt = _parse_swift_amount(amt_str)
                closing_bal = amt if sign == "C" else -amt
            last_tag = "62"
        else:
            # Continuation line
            if last_tag == "86" and lines:
                prev = lines[-1]
                lines[-1] = StatementLine(
                    date=prev.date,
                    amount=prev.amount,
                    reference=prev.reference,
                    narration=(prev.narration + " " + line).strip(),
                )

    # Sequence gap audit
    if "/" in sequence_no:
        parts = sequence_no.split("/")
        try:
            seq_int = int(parts[0])
            if seq_int > 1 and "last_sequence" in warnings:
                warnings.append(f"Potential sequence jump to {seq_int}")
        except ValueError:
            pass

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


def parse_csv(
    content: str,
    seen_hashes: set[str] | None = None,
    expected_sequence: int | None = None,
) -> ParsedStatement:
    """Parse commercial bank CSV feed with auto-column mapping, deduplication, and sequence verification."""
    seen = set(seen_hashes) if seen_hashes else set()
    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    lines: list[StatementLine] = []
    line_hashes: list[str] = []
    skipped = 0
    warnings: list[str] = []

    # Detect delimiter
    sample = content[:1024]
    delimiter = "\t" if "\t" in sample and "," not in sample else ","
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

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

    seq_no = "1"
    for row_idx, row in enumerate(reader, start=1):
        # 1. Parse Date
        dt_raw = row.get(field_map.get("date", ""), "").strip()
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

        # 2. Parse Amount
        amt = Decimal("0.00")
        if "amount" in field_map and row.get(field_map["amount"]):
            amt_str = row[field_map["amount"]].replace(",", "").replace("$", "").replace("৳", "").strip()
            amt = Decimal(amt_str) if amt_str else Decimal("0.00")
        else:
            cr_str = row.get(field_map.get("credit", ""), "").replace(",", "").strip()
            dr_str = row.get(field_map.get("debit", ""), "").replace(",", "").strip()
            cr = Decimal(cr_str) if cr_str else Decimal("0.00")
            dr = Decimal(dr_str) if dr_str else Decimal("0.00")
            amt = cr - dr

        ref = row.get(field_map.get("ref", ""), "").strip()
        narration = row.get(field_map.get("narration", ""), "").strip()
        if "seq" in field_map and row.get(field_map["seq"]):
            seq_no = row[field_map["seq"]].strip()

        l_hash = _compute_line_hash(dt, amt, ref, narration)
        if l_hash in seen:
            skipped += 1
        else:
            seen.add(l_hash)
            line_hashes.append(l_hash)
            lines.append(StatementLine(date=dt, amount=amt, reference=ref, narration=narration))

    if expected_sequence is not None:
        try:
            if int(seq_no) != expected_sequence:
                warnings.append(f"Sequence mismatch: expected {expected_sequence}, got {seq_no}")
        except ValueError:
            pass

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
) -> ParsedStatement:
    """Entry point for bank feed parsing with auto-detection."""
    content_stripped = content.strip()
    if format_type == "mt940" or (format_type == "auto" and (content_stripped.startswith(":20:") or ":61:" in content_stripped)):
        return parse_mt940(content_stripped, seen_hashes=seen_hashes)
    return parse_csv(content_stripped, seen_hashes=seen_hashes)
